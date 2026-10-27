"""Verify source-preserving attachment decoding and bounded grain checks."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from inspect_hces_attachments import read_workbook, reconcile_grains


def workbook_fixture(path: Path, target: str = "worksheets/sheet1.xml") -> None:
    """Write a minimal synthetic workbook with distinct source cell types."""
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{namespace}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="FDQ_Impu_rate_sec" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="'
            + target
            + '"/></Relationships>',
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            f'<sst xmlns="{namespace}"><si><t>061</t></si><si><t>Questionnaire Item</t></si></sst>',
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="{namespace}"><dimension ref="A1:D3"/><sheetData><row r="2"><c r="A2" t="s"><v>1</v></c></row><row r="3"><c r="A3" t="s"><v>0</v></c><c r="B3"><v>39.950000000000003</v></c><c r="C3"><f>1+1</f><v>2</v></c><c r="D3" t="e"><v>#N/A</v></c></row></sheetData></worksheet>',
        )


def test_leading_zero_and_numeric_lexemes_preserved(tmp_path: Path) -> None:
    """Codes retain leading zeros and numeric XML precision is not rounded."""
    path = tmp_path / "source.xlsx"
    workbook_fixture(path)
    sheet = read_workbook(path)["sheets"][0]
    assert sheet["cells"]["A3"]["value"] == "061"
    assert sheet["cells"]["B3"]["value"] == "39.950000000000003"
    assert sheet["headers_row_2"] == {"A2": "Questionnaire Item"}


def test_formula_and_cache_and_errors_remain_distinct(tmp_path: Path) -> None:
    """Reading never replaces formulas with cached values or hides errors."""
    path = tmp_path / "source.xlsx"
    workbook_fixture(path)
    before = path.read_bytes()
    sheet = read_workbook(path)["sheets"][0]
    assert sheet["cells"]["C3"]["formula"] == "1+1"
    assert sheet["cells"]["C3"]["value"] == "2"
    assert sheet["formula_count"] == 1
    assert sheet["error_cells"] == ["D3"]
    assert path.read_bytes() == before


def test_unexpected_sheet_target_rejected(tmp_path: Path) -> None:
    """Workbook relationships cannot redirect decoding outside worksheet members."""
    path = tmp_path / "source.xlsx"
    workbook_fixture(path, target="../../other.xml")
    with pytest.raises(ValueError, match="Unexpected worksheet"):
        read_workbook(path)


def test_grain_checks_retain_mismatches_and_missing_values(tmp_path: Path) -> None:
    """Matching quantities cannot certify missing monetary values or nutrition."""
    clean = tmp_path / "04_clean"
    clean.mkdir()
    pq.write_table(
        pa.table({"hhid": ["a", "b", "c"], "state": [8, 9, 6]}),
        clean / "level_01.parquet",
    )
    pq.write_table(
        pa.table(
            {
                "hhid": ["a", "a", "a", "b", "b", "c", "c"],
                "item_code": [1, 55, 56, 2, 115, 70, 63],
                "cons_total_qty": [5.0, 2.0, 3.0, 4.0, 4.0, 3.0, 4.0],
                "cons_total_value": [50.0, 20.0, 29.0, 40.0, 40.0, None, None],
            }
        ),
        clean / "level_05.parquet",
    )
    result = reconcile_grains(tmp_path)
    pds, other, free = result["families"]
    assert pds["comparisons"]["cons_total_qty"]["mismatches_tolerance_1e_minus_8"] == 0
    assert (
        pds["comparisons"]["cons_total_value"]["mismatches_tolerance_1e_minus_8"] == 1
    )
    assert other["child_only_households"] == 0
    assert free["comparisons"]["cons_total_qty"]["mismatches_tolerance_1e_minus_8"] == 1
    assert free["comparisons"]["cons_total_value"]["parent_missing"] == 1
    assert free["comparisons"]["cons_total_value"]["child_sum_missing"] == 1
    assert (
        free["comparisons"]["cons_total_value"]["maximum_absolute_difference"] is None
    )
    assert result["nutrient_estimation_performed"] is False
    assert result["household_rows_exported"] == 0
