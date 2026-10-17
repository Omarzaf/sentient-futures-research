"""Audit HCES questionnaire/imputation attachments without estimating intake."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pyarrow.parquet as pq

__all__ = ["audit_attachments", "read_workbook", "reconcile_grains"]

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
GRAINS = {
    1: [55, 56, 57, 58, 59, 60],
    2: [115, 116, 117, 118, 121, 120],
    70: [63, 64, 65, 66, 67, 68],
}
DDM_STATES = {8, 3, 6, 24, 28, 33, 32, 29, 36, 9}


def _identity(path: Path) -> dict:
    """Identify source bytes without modifying their original container."""
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def read_workbook(path: Path) -> dict:
    """Decode every stored cell, preserving numeric lexemes and string codes."""
    sheets = []
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Workbook ZIP integrity failure")
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [
                "".join(item.itertext())
                for item in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall(
                    "s:si", NS
                )
            ]
        relations = {
            item.get("Id"): item.get("Target")
            for item in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            if item.get("TargetMode") != "External"
        }
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in book.findall("s:sheets/s:sheet", NS):
            target = relations[sheet.attrib[REL_ID]]
            member = (
                target.lstrip("/")
                if target.startswith("/")
                else posixpath.normpath("xl/" + target)
            )
            if not member.startswith("xl/worksheets/"):
                raise ValueError("Unexpected worksheet target")
            root = ET.fromstring(archive.read(member))
            cells = {}
            for cell in root.findall("s:sheetData/s:row/s:c", NS):
                kind = cell.get("t", "n")
                raw = cell.findtext("s:v", default="", namespaces=NS)
                value = (
                    strings[int(raw)]
                    if kind == "s"
                    else (
                        "".join(cell.find("s:is", NS).itertext())
                        if kind == "inlineStr"
                        else raw
                    )
                )
                formula = cell.findtext("s:f", default=None, namespaces=NS)
                if value or formula is not None:
                    cells[cell.attrib["r"]] = {
                        "type": kind,
                        "value": value,
                        "raw_value": raw,
                        "formula": formula,
                    }
            headers = {
                ref: cell["value"]
                for ref, cell in cells.items()
                if re.fullmatch(r"[A-Z]+2", ref)
            }
            rows = sorted({int(re.sub(r"^[A-Z]+", "", ref)) for ref in cells})
            dimension = root.find("s:dimension", NS)
            sheets.append(
                {
                    "name": sheet.attrib["name"],
                    "xml_member": member,
                    "dimension": (
                        dimension.get("ref") if dimension is not None else None
                    ),
                    "title": cells.get("A1", {}).get("value"),
                    "headers_row_2": headers,
                    "nonempty_cells": len(cells),
                    "populated_rows": len(rows),
                    "data_rows": (
                        len([row for row in rows if row >= 3])
                        if "Impu_rate" in sheet.attrib["name"]
                        else None
                    ),
                    "formula_count": sum(
                        cell["formula"] is not None for cell in cells.values()
                    ),
                    "error_cells": [
                        ref for ref, cell in cells.items() if cell["type"] == "e"
                    ],
                    "merges": [
                        item.attrib["ref"]
                        for item in root.findall("s:mergeCells/s:mergeCell", NS)
                    ],
                    "cells": cells,
                }
            )
        return {
            **_identity(path),
            "zip_crc_check": "PASS",
            "zip_members": len(archive.namelist()),
            "sheets": sheets,
        }


def reconcile_grains(candidate: Path) -> dict:
    """Test documented grain parent/child identities using aggregate diagnostics."""
    food_path = candidate / "04_clean/level_05.parquet"
    info_path = candidate / "04_clean/level_01.parquet"
    info = pq.read_table(info_path, columns=["hhid", "state"]).to_pandas()
    results = []
    for parent, children in GRAINS.items():
        fields = ["hhid", "item_code", "cons_total_qty", "cons_total_value"]
        parents = pq.read_table(
            food_path, columns=fields, filters=[("item_code", "=", parent)]
        ).to_pandas()
        child_table = pq.read_table(
            food_path, columns=fields, filters=[("item_code", "in", children)]
        )
        summed = (
            child_table.group_by("hhid")
            .aggregate([("cons_total_qty", "sum"), ("cons_total_value", "sum")])
            .to_pandas()
        )
        joined = parents.merge(
            summed, on="hhid", how="outer", validate="one_to_one", indicator=True
        ).merge(info, on="hhid", how="left", validate="one_to_one")
        both = joined.loc[joined["_merge"].eq("both")]
        matches = {}
        for field in ["cons_total_qty", "cons_total_value"]:
            difference = (both[field] - both[field + "_sum"]).abs()
            matches[field] = {
                "compared_households": len(both),
                "parent_missing": int(both[field].isna().sum()),
                "child_sum_missing": int(both[field + "_sum"].isna().sum()),
                "mismatches_tolerance_1e_minus_8": int(difference.gt(1e-8).sum()),
                "maximum_absolute_difference": (
                    float(difference.max()) if difference.notna().any() else None
                ),
                "sum_absolute_difference": (
                    float(difference.sum(min_count=1))
                    if difference.notna().any()
                    else None
                ),
                "mismatch_states": sorted(
                    int(state)
                    for state in both.loc[difference.gt(1e-8), "state"].unique()
                ),
            }
        results.append(
            {
                "parent_code": f"{parent:03}",
                "child_codes": [f"{code:03}" for code in children],
                "parent_records": len(parents),
                "child_records": child_table.num_rows,
                "households_with_child_rows": len(summed),
                "parent_only_households": int(joined["_merge"].eq("left_only").sum()),
                "child_only_households": int(joined["_merge"].eq("right_only").sum()),
                "parent_only_inside_documented_DDM_states": int(
                    (
                        joined["_merge"].eq("left_only")
                        & joined["state"].isin(DDM_STATES)
                    ).sum()
                ),
                "states_with_child_rows": sorted(
                    int(state)
                    for state in joined.loc[joined["_merge"].ne("left_only"), "state"]
                    .dropna()
                    .unique()
                ),
                "comparisons": matches,
            }
        )
    return {
        "source": _identity(food_path),
        "source_questionnaire_pdf_pages": [24, 25],
        "families": results,
        "household_rows_exported": 0,
        "nutrient_estimation_performed": False,
        "scope_limit": "Quantity hierarchy check only; matching sums do not verify nutrient composition, validity of an average parent coefficient for every child variety, or monetary imputation",
    }


def audit_attachments(pdf: Path, workbook: Path, candidate: Path, output: Path) -> dict:
    """Audit attachment identity, all workbook cells and questionnaire page coverage."""
    output.mkdir(parents=True, exist_ok=True)
    extraction = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    pages = [page for page in extraction.stdout.split("\f") if page.strip()]
    inventory = []
    for number, page in enumerate(pages, 1):
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        inventory.append(
            {
                "pdf_page": number,
                "opening_lines": lines[:4],
                "text_characters": len(page),
            }
        )
    decoded = read_workbook(workbook)
    (output / "workbook-decoded.json").write_text(
        json.dumps(decoded, indent=2, ensure_ascii=False) + "\n"
    )
    source_matches = {}
    for current, relative in [
        (pdf, "01_docs/HCES2023-24_Vol_II.pdf"),
        (workbook, "01_docs/HCES_2023_24_Imputation_Rate.xlsx"),
    ]:
        previous = candidate / relative
        source_matches[current.name] = {
            "supplied": _identity(current),
            "candidate_document": _identity(previous),
            "byte_identical": current.read_bytes() == previous.read_bytes(),
        }
    by_name = {sheet["name"]: sheet for sheet in decoded["sheets"]}
    examples = []
    for name, coordinates in [
        ("FDQ_Impu_rate_sec", ["A5", "B5", "C5", "D5", "E5", "F5"]),
        ("FDQ_Impu_rate_stsec", ["A3", "B3", "C3", "D3", "E3", "F3", "G3"]),
        ("DGQ_Impu_rate_sec", ["A3", "B3", "D3", "E3", "F3", "G3"]),
    ]:
        if name in by_name:
            examples.append(
                {
                    "sheet": name,
                    "cells": {
                        ref: by_name[name]["cells"].get(ref) for ref in coordinates
                    },
                }
            )
    result = {
        "status": "HOLD",
        "official_india_baseline_reproduced": False,
        "new_estimation_allowed": False,
        "source_matches": source_matches,
        "pdf_page_count": len(pages),
        "pdf_page_inventory": inventory,
        "workbook_summary": [
            {key: value for key, value in sheet.items() if key != "cells"}
            for sheet in decoded["sheets"]
        ],
        "decoded_exemplars": examples,
        "document_roles": {
            "pdf": "62-page blank questionnaire collection, not a nutrient conversion table or estimation-methodology report",
            "pdf_questionnaires": {
                "LCES": [1, 9],
                "HCQ": [10, 21],
                "FDQ": [22, 38],
                "CSQ": [39, 50],
                "DGQ": [51, 62],
            },
            "workbook": "Monetary unit rates for valuation of free food and durable goods; distinct Mode and 25th Percentile columns are retained, not silently selected",
            "currency_caption": "Workbook does not explicitly label INR/Rs in its headers. Monetary role is supported by free-item valuation titles and questionnaire value columns labelled Rs.; it is not grams protein per unit",
            "nutrient_or_cpi_mapping_supplied": False,
        },
        "unit_and_recall_evidence": [
            {
                "pdf_pages": [24, 25, 26, 27],
                "finding": "Cereals/pulses/sugar/salt:30 days; default quantity unit kg; separate total including home produce; subtotals are not extra foods",
            },
            {
                "pdf_pages": [28, 32, 34, 35, 36, 37],
                "finding": "Milk/vegetables/fruits/eggs/meat/oil/spices/beverages/processed foods:7 days; unit exceptions include liquid milk litre, eggs count, spices gram and cooked meals count; monetary-only rows remain monetary",
            },
            {
                "pdf_pages": [24, 25],
                "finding": "001/002/070 are coarse-grain parents;18 variety/source children apply to10 named states. Quantity sums do not establish nutrient equivalence of varieties",
            },
            {
                "pdf_pages": [28],
                "finding": "Other milk products parent092 has value-only drop-down children006/007/167; no nutrient or CPI coefficient is supplied here",
            },
        ],
        "baseline_limits": [
            "These exact documents were already in the candidate repository; they do not establish identity of its absent original raw data",
            "No exact nutrient-rupee CPI series/item-period mapping is supplied; imputation prices cannot substitute for nutrition conversion factors",
            "Quantity hierarchy verification does not certify nutrient composition or MPCE reconstruction; three PDS monetary differences and free child values remain separately diagnosed",
            "Neither official reproduction gate is promoted and no downstream estimate is computed",
        ],
        "grain_reconciliation": reconcile_grains(candidate),
        "producer": _identity(Path(__file__)),
        "raw_originals_modified": False,
        "scope": "Source identity, document structure and candidate grain arithmetic diagnostics; no intake mean or downstream estimate",
    }
    (output / "audit.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_attachments(args.pdf, args.workbook, args.candidate, args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "pdf_pages": result["pdf_page_count"],
                "sheets": len(result["workbook_summary"]),
                "both_match_existing": all(
                    record["byte_identical"]
                    for record in result["source_matches"].values()
                ),
            }
        )
    )
