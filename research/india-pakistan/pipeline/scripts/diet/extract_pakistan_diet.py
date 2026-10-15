"""Extract HIES major-food quantities without inventing nutrient conversions."""

from __future__ import annotations

import csv
import hashlib
import math
import re
from collections import Counter
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = Path("data/raw/regional/pakistan-hies-table23.xls")
OUT = Path(__file__).resolve().parent
SOURCE_ID = "pakistan_hies_2024_25_table23"
QUINTILES = ("all", "Q1", "Q2", "Q3", "Q4", "Q5")
UNITS = {
    "Kg": "kg/person/month",
    "Gm": "g/person/month",
    "Ltr": "litre/person/month",
    "No": "count/person/month",
}
FIELDS = [
    "country",
    "region",
    "group",
    "year",
    "food_group",
    "metric",
    "value",
    "unit",
    "source_id",
    "residence",
    "quintile",
    "period",
    "source_food_item",
    "native_unit",
    "display_value",
    "source_cell_format",
    "food_group_basis",
    "sample_size",
    "sample_basis",
    "survey_sample_size",
    "survey_sample_basis",
    "denominator",
    "fieldwork_start",
    "fieldwork_end",
    "fieldwork_note",
    "method",
    "raw_file",
    "raw_locator",
    "raw_sha256",
    "sample_source_id",
    "sample_locator",
    "nutrient_conversion_status",
    "mapping_gap",
    "source_footnote",
    "notes",
]
CONTEXT_FIELDS = [
    "sample_size",
    "sample_basis",
    "survey_sample_size",
    "survey_sample_basis",
    "fieldwork_start",
    "fieldwork_end",
    "fieldwork_note",
    "sample_source_id",
    "sample_locator",
]


def normalize(text: str) -> str:
    """Normalize whitespace without silently changing a published food label."""
    return re.sub(r"\s+", " ", text).strip()


def food_key(name: str) -> str:
    """Create a stable item key while retaining the original label separately."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower().replace("&", "and")).strip("_")


def sample_context() -> dict[tuple[str, str], dict[str, str]]:
    """Reuse the already verified M2 context without treating it as workbook N."""
    context = {}
    path = ROOT / "scripts/regional/extracted_rows.csv"
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["source_id"] != SOURCE_ID or row["region"] != "Pakistan":
                continue
            key = (row["residence"], row["quintile"])
            values = {field: row[field] for field in CONTEXT_FIELDS}
            if key in context:
                assert values == context[key], key
            context[key] = values
    assert set(context) == {
        (residence, quintile)
        for residence in ("all", "urban", "rural")
        for quintile in QUINTILES
    }
    assert all(row["sample_size"] == "" for row in context.values())
    return context


def mapping_gap(name: str, unit: str) -> str:
    """Describe unresolved mapping needs without supplying unsupported factors."""
    gaps = [
        "Named food-composition item, edible-portion basis and raw/cooked basis have not been matched."
    ]
    if unit == "No":
        gaps.append("Item-specific edible grams per counted egg or fruit are missing.")
    elif unit == "Ltr":
        gaps.append("Source-specific density or nutrient content per litre is missing.")
    lower = name.lower()
    if any(
        word in lower
        for word in ("other", " and ", " & ", "/", "fruit", "tea", "biscuit")
    ):
        gaps.append(
            "Combined category or food variety requires a sourced composition mixture or bounded scenario."
        )
    if "milk" in lower or "yogurt" in lower:
        gaps.append(
            "Milk species, fat level or powder/formula product composition is not resolved by this label."
        )
    if "butter" in lower:
        gaps.append("Source includes butter and margarine; the mixture is unknown.")
    if lower in {"mutton", "beef", "fish", "chicken meat"}:
        gaps.append(
            "Species/cut mix, bone or other refuse and edible mass are unresolved."
        )
    return " ".join(gaps)


def extract_rows() -> list[dict[str, str]]:
    """Extract every unit-bearing food row in the three national blocks."""
    raw = ROOT / RAW_FILE
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    book = xlrd.open_workbook(str(raw), formatting_info=True)
    sheet = book.sheet_by_index(0)
    assert sheet.name == "Sheet1"
    assert "2024-25" in str(sheet.cell_value(1, 0))
    assert [normalize(str(sheet.cell_value(3, col))) for col in range(2, 8)] == [
        "Total",
        "1st",
        "2nd",
        "3rd",
        "4th",
        "5th",
    ]
    footnote = normalize(str(sheet.cell_value(48, 0)))
    assert footnote.startswith("* Butter contains Butter /Margarine")
    context = sample_context()
    rows = []
    residence = ""
    food_rows: dict[str, list[str]] = {}
    for index in range(6, sheet.nrows):
        name = normalize(str(sheet.cell_value(index, 0)))
        if name == "PUNJAB":
            break
        heading = re.fullmatch(r"PAKISTAN(?: (URBAN|RURAL))?", name)
        if heading:
            residence = (heading.group(1) or "all").lower()
            assert residence not in food_rows
            food_rows[residence] = []
            continue
        native = normalize(str(sheet.cell_value(index, 1)))
        if not native:
            # Excludes headings, the butter footnote and household size, not foods.
            continue
        assert residence and native in UNITS, (index, name, native)
        key = food_key(name)
        food_rows[residence].append(key)
        for column, quintile in enumerate(QUINTILES, 2):
            value = sheet.cell_value(index, column)
            assert isinstance(value, float) and math.isfinite(value) and value >= 0
            cell_format = book.format_map[
                book.xf_list[sheet.cell_xf_index(index, column)].format_key
            ].format_str
            assert cell_format in {"0.00", "#,##0.00"}, (index, column, cell_format)
            rows.append(
                {
                    "country": "Pakistan",
                    "region": "Pakistan",
                    "group": f"{residence}_{quintile}",
                    "year": "2025",
                    "food_group": key,
                    "metric": "monthly_per_capita_consumption_quantity",
                    "value": repr(value),
                    "unit": UNITS[native],
                    "source_id": SOURCE_ID,
                    "residence": residence,
                    "quintile": quintile,
                    "period": "2024-25",
                    "source_food_item": name,
                    "native_unit": native,
                    "display_value": f"{value:.2f}",
                    "source_cell_format": cell_format,
                    "food_group_basis": "Published item/category; no broad food-group aggregation.",
                    **context[(residence, quintile)],
                    "denominator": "Per household member per month in the national residence/quintile group; quintiles are national consumption-expenditure groups, not within-residence quintiles.",
                    "method": "Read original XLS cached numeric cells with xlrd 2.0.2; preserve full stored precision and native units. Source display uses two decimal places. No summation across incompatible units, nutrient conversion, density or portion imputation.",
                    "raw_file": str(RAW_FILE),
                    "raw_locator": f"Sheet1!{chr(65 + column)}{index + 1}; Table 23; {name}",
                    "raw_sha256": digest,
                    "nutrient_conversion_status": "not_performed",
                    "mapping_gap": mapping_gap(name, native),
                    "source_footnote": footnote if key == "butter" else "",
                    "notes": "Major published food items only; completeness of total dietary intake is not established. Do not infer protein adequacy. Workbook title confirms 2024-25 despite reused 2018-19 catalog link; workbook and report Table 3.7.C are conflicting source vintages. Year is survey-round end, not a calendar-year estimate.",
                }
            )
    assert set(food_rows) == {"all", "urban", "rural"}
    assert len(food_rows["all"]) == len(set(food_rows["all"])) == 38
    assert food_rows["all"] == food_rows["urban"] == food_rows["rural"]
    assert len(rows) == 684
    assert Counter(row["group"] for row in rows) == {
        f"{residence}_{quintile}": 38
        for residence in ("all", "urban", "rural")
        for quintile in QUINTILES
    }
    assert len({(row["group"], row["food_group"]) for row in rows}) == len(rows)
    return rows


def main() -> None:
    """Write source-shaped diet rows for coordinator integration."""
    rows = extract_rows()
    with (OUT / "pakistan_diet_rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(
        "PASS: 684 quantities; 38 published food items; 18 residence/quintile groups; native units and missing analytical sample preserved."
    )


if __name__ == "__main__":
    main()
