"""Compare unchanged official aggregate tables with the frozen microdata profile."""

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import xlrd

OUT = Path(__file__).resolve().parent
PROFILE = OUT.parent
ROOT = OUT.parents[3]
RAW = ROOT / "data/raw/diet/m3-survey-inputs-2026-10-13"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def digest(path: Path) -> str:
    """Bind the original source bytes without changing a workbook."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_csv(name: str, rows: list[dict]) -> None:
    """Write public source cells or aggregate comparisons only."""
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read an existing aggregate artifact."""
    with path.open() as stream:
        return list(csv.DictReader(stream))


def load_xls(path: Path) -> tuple[dict, list, dict]:
    """Read cached source cell values and original merged-cell layout."""
    book = xlrd.open_workbook(path, formatting_info=True)
    assert book.sheet_names() == ["Sheet1"]
    sheet = book.sheet_by_index(0)
    cells = {}
    rows = []
    for row in range(sheet.nrows):
        for col in range(sheet.ncols):
            value = sheet.cell_value(row, col)
            if value == "":
                continue
            address = f"{xlrd.formula.colname(col)}{row + 1}"
            cells[address] = value
            rows.append(
                {
                    "source": path.name,
                    "sheet": sheet.name,
                    "cell": address,
                    "type": sheet.cell_type(row, col),
                    "value": value,
                }
            )
    metadata = {
        "sheet": sheet.name,
        "rows": sheet.nrows,
        "columns": sheet.ncols,
        "title_cells": {k: cells.get(k) for k in ("A1", "A2")},
        "merged_cells_zero_based_half_open": sheet.merged_cells,
        "national_categories_merged_ranges": [
            m for m in sheet.merged_cells if m[0] < 26 and m[1] > 14
        ],
    }
    return cells, rows, metadata


def load_xlsx(path: Path) -> tuple[dict, list, dict]:
    """Read source strings, cached numeric values and formulas with ZIP/XML."""
    with zipfile.ZipFile(path) as archive:
        strings = [
            "".join(node.itertext())
            for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))
        ]
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        cells, rows, formulas = {}, [], {}
        for node in root.findall(".//m:sheetData/m:row/m:c", NS):
            value = node.find("m:v", NS)
            if value is None:
                continue
            address = node.attrib["r"]
            text = (
                strings[int(value.text)]
                if node.attrib.get("t") == "s"
                else float(value.text)
            )
            cells[address] = text
            rows.append(
                {
                    "source": path.name,
                    "sheet": "Sheet1",
                    "cell": address,
                    "type": node.attrib.get("t", "n"),
                    "value": text,
                }
            )
            formula = node.find("m:f", NS)
            if formula is not None:
                formulas[address] = formula.text
        metadata = {
            "sheet": "Sheet1",
            "title_cells": {k: cells.get(k) for k in ("A1", "A2")},
            "formulas": formulas,
            "merged_cells": [
                n.attrib["ref"] for n in root.findall(".//m:mergeCell", NS)
            ],
        }
    return cells, rows, metadata


def main() -> None:
    """Generate source-bound edition, denominator and category diagnostics."""
    paths = {
        "15": RAW / "table15.xls",
        "16": RAW / "table16.xls",
        "22": RAW / "table22.xlsx",
        "23": ROOT / "data/raw/regional/pakistan-hies-table23.xls",
    }
    books, metadata, inventory = {}, {}, []
    for number, path in paths.items():
        cells, cell_rows, meta = (
            load_xlsx(path) if path.suffix == ".xlsx" else load_xls(path)
        )
        assert "2024-25" in cells["A2"]
        books[number] = cells
        metadata[number] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
            **meta,
        }
        inventory.extend(cell_rows)
    save_csv("published_cell_inventory.csv", inventory)
    (OUT / "workbook_layout_and_vintage.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    categories = []
    for residence, offset in (("all", 0), ("urban", 21), ("rural", 42)):
        for index in range(15, 27):
            row = index + offset
            label = books["15"][f"A{row}"].strip()
            assert label == books["16"][f"A{row}"].strip()
            amount = books["16"][f"B{row}"]
            percentage = books["15"][f"B{row}"]
            total = books["16"][f"B{9 + offset}"]
            implied = amount / total * 100
            categories.append(
                {
                    "residence": residence,
                    "category": label,
                    "table15_share_percent": percentage,
                    "table16_amount_rupees": amount,
                    "table16_implied_share_percent": implied,
                    "difference_percentage_points": implied - percentage,
                    "table15_cell": f"Sheet1!B{row}",
                    "table16_cell": f"Sheet1!B{row}",
                    "adjacent_label_cell": f"Sheet1!A{row}",
                    "equal_within_0_00011_percentage_points": abs(implied - percentage)
                    <= 0.00011,
                }
            )
    save_csv("coicop_share_amount_comparison.csv", categories)
    populations = read_csv(PROFILE / "population_weight_aggregates.csv")
    budgets = {
        r["residence"]: r
        for r in read_csv(PROFILE / "observed_budget_reconciliation_diagnostic.csv")
    }
    food = read_csv(PROFILE / "food_expenditure_coverage_diagnostic.csv")
    denominator_rows = []
    for (
        residence,
        expenditure_row,
        member22_row,
        total22_row,
        food22_row,
        member23_row,
    ) in (
        ("all", 9, 9, 11, 14, 9),
        ("urban", 30, 134, 136, 139, 52),
        ("rural", 51, 259, 261, 264, 94),
    ):
        subset = [
            p
            for p in populations
            if residence == "all"
            or p["region"] == ("2" if residence == "urban" else "1")
        ]
        weight_sum = sum(float(p["sum_household_weight"]) for p in subset)
        raw_member_yes = sum(float(p["weighted_yes_member_population"]) for p in subset)
        raw_all = sum(float(p["weighted_roster_population"]) for p in subset)
        household = books["16"][f"B{expenditure_row}"]
        percap = books["22"][f"B{total22_row}"]
        published_size = books["22"][f"B{member22_row}"]
        assert published_size == books["23"][f"C{member23_row}"]
        observed_food = sum(
            float(r["weighted_monthly_observed_value"])
            for r in food
            if r["residence"] == residence
        )
        denominator_rows.append(
            {
                "residence": residence,
                "table15_household_rupees": books["15"][f"B{expenditure_row}"],
                "table16_household_rupees": household,
                "table22_person_rupees": percap,
                "table22_and23_mean_members": published_size,
                "table16_to22_implied_mean_members": household / percap,
                "raw_member_yes_mean": raw_member_yes / weight_sum,
                "raw_all_roster_mean": raw_all / weight_sum,
                "table22_product_minus_table16": percap * published_size - household,
                "raw_observed_budget_household_rupees": budgets[residence][
                    "mean_observed_subtotal_monthly_value"
                ],
                "raw_budget_minus_table16": float(
                    budgets[residence]["mean_observed_subtotal_monthly_value"]
                )
                - household,
                "table22_all_food_per_person_rupees": books["22"][f"B{food22_row}"],
                "raw_all_food_including_milling_per_yes_member_rupees": observed_food
                / raw_member_yes,
                "table16_total_cell": f"Sheet1!B{expenditure_row}",
                "table22_total_cell": f"Sheet1!B{total22_row}",
                "table22_members_cell": f"Sheet1!B{member22_row}",
                "table23_members_cell": f"Sheet1!C{member23_row}",
            }
        )
    save_csv("denominator_and_total_comparison.csv", denominator_rows)
    boundaries = []
    for residence, start, end, food_row in (
        ("all", 7, 131, 14),
        ("urban", 132, 256, 139),
        ("rural", 257, 381, 264),
    ):
        expected = "PAKISTAN" + ("" if residence == "all" else f" {residence.upper()}")
        assert books["22"][f"A{start}"].strip() == expected
        assert books["22"][f"A{food_row}"].strip() == "All Food Items"
        boundaries.append(
            {
                "residence": residence,
                "block_first_row": start,
                "block_last_row": end,
                "block_header_cell": f"A{start}",
                "block_header_text": expected,
                "food_label_cell": f"A{food_row}",
                "food_value_cell": f"B{food_row}",
                "food_percap_value": books["22"][f"B{food_row}"],
                "column_header_cell": "B4",
                "column_header_text": books["22"]["B4"],
            }
        )
    assert books["22"]["A382"].strip() == "PUNJAB"
    (OUT / "table22_boundary_evidence.json").write_text(
        json.dumps(
            {
                "blocks": boundaries,
                "next_block": {"cell": "A382", "value": "PUNJAB"},
                "formula_cells": len(metadata["22"]["formulas"]),
                "merged_cells": metadata["22"]["merged_cells"],
                "same_scope_positive_weighted_mean_check": "FAIL: national All Food Items exceeds both urban and rural values; preserved source inconsistency, not an adjusted value.",
            },
            indent=2,
        )
        + "\n"
    )
    balance = read_csv(OUT / "balance_expense_aggregate.csv")
    components = read_csv(PROFILE / "welfare_component_channel_diagnostic.csv")
    part_variables = {
        "A": "sum_v1_1000_a",
        "B": "sum_v1_2000_b",
        "C": "sum_v1_4000_c",
        "D": "sum_v1_5000_d",
    }
    balance_comparisons = []
    for residence in ("all", "rural", "urban"):
        for part, variable in part_variables.items():
            balance_row = next(
                r
                for r in balance
                if r["residence"] == residence and r["variable"] == variable
            )
            main_row = next(
                r
                for r in components
                if r["residence"] == residence and r["part"] == part
            )
            monthly = (
                float(balance_row["weighted_observed_sum_per_all_households"]) / 12
            )
            paid = float(main_row["paid_monthly_mean"])
            balance_comparisons.append(
                {
                    "residence": residence,
                    "part": part,
                    "balance_variable": variable,
                    "balance_observed_monthly_equivalent": monthly,
                    "main_paid_observed_monthly_equivalent": paid,
                    "balance_minus_main": monthly - paid,
                    "balance_nonmissing_households": balance_row["nonmissing"],
                    "interpretation": "Already annualized stored balance fields; paid cash check, not official welfare.",
                }
            )
    save_csv("balance_to_main_paid_comparison.csv", balance_comparisons)
    raw_catalogue = (ROOT / "data/raw/regional/pbs-hies-catalog.html").read_text()
    links = re.findall(
        r'<a\b[^>]*href=["\']([^"\']*Table23[^"\']*)["\'][^>]*>',
        raw_catalogue,
        flags=re.IGNORECASE,
    )
    (OUT / "catalogue_table23_link_observations.json").write_text(
        json.dumps(
            {
                "catalogue_sha256": digest(
                    ROOT / "data/raw/regional/pbs-hies-catalog.html"
                ),
                "links": links,
                "workbook_vintage_basis": "Internal Sheet1!A2 explicitly says 2024-25; repeated URL is not an edition identifier.",
            },
            indent=2,
        )
        + "\n"
    )
    print(
        f"PASS: {len(inventory)} public cells; 36 category and 3 national/residence comparisons; source bytes unchanged."
    )


if __name__ == "__main__":
    main()
