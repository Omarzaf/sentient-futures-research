"""Extract cited NFHS regional frequencies and HIES regional quantities."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/regional"
OUT = Path(__file__).resolve().parent
FIELDS = [
    "country",
    "region",
    "region_type",
    "year",
    "indicator",
    "value",
    "unit",
    "source_id",
    "sex",
    "age_group",
    "residence",
    "quintile",
    "period",
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
    "sample_source_id",
    "sample_locator",
    "daily_component",
    "weekly_component",
    "display_value",
    "notes",
]
UTS = {
    "Chandigarh",
    "Delhi",
    "Jammu & Kashmir",
    "Ladakh",
    "Dadra & Nagar Haveli and Daman & Diu",
    "Andaman & Nicobar Islands",
    "Lakshadweep",
    "Puducherry",
}


def normalize(text: str) -> str:
    """Normalize only whitespace for source region labels."""
    return re.sub(r"\s+", " ", text).strip()


def tabular_rows(text: str, count: int) -> list[tuple[str, list[str]]]:
    """Read region-name rows with the expected count of numeric tokens."""
    text = re.sub(
        r"Dadra & Nagar Haveli and\s*\n\s*Daman & Diu",
        "Dadra & Nagar Haveli and Daman & Diu",
        text,
    )
    found = []
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z&][A-Za-z &'/-]*?)\s{2,}([\d.,\s]+)$", line)
        if match:
            values = match.group(2).split()
            if len(values) == count:
                found.append((normalize(match.group(1)), values))
    return found


def sid_for_state(path: Path) -> str:
    """Return a stable source ID for an NFHS state PDF."""
    return "nfhs5_state_" + re.sub(
        r"[^a-z0-9]", "", path.stem.removeprefix("FR374_").lower()
    )


def extract_india() -> list[dict[str, str]]:
    """Read all 36 states and attach explicitly scoped sample evidence."""
    text = (RAW / "india-nfhs5-national.txt").read_text()
    pages = text.split("\f")
    metadata = dict(tabular_rows(pages[50] + "\n" + pages[51], 10))
    assert len(metadata) == 37, len(metadata)
    state_reports = {}
    for file in RAW.glob("FR374*.txt"):
        state = re.sub(r"[^a-z]", "", file.stem.removeprefix("FR374_").lower())
        content = file.read_text()
        matches = list(
            re.finditer(r"^Fish or chicken/meat\s+([\d.,\s]+)$", content, re.MULTILINE)
        )
        assert len(matches) == 2, file
        state_reports[state] = [
            (match.group(1).split(), content[: match.start()].count("\f") + 1, file)
            for match in matches
        ]
    rows = []
    for sex, page, table in [("women", 476, "10.27.1"), ("men", 477, "10.27.2")]:
        assert f"Table {table}" in pages[page - 1]
        data = tabular_rows(pages[page - 1], 10)
        assert len(data) == 37, (sex, len(data))
        for region, values in data:
            if region == "India":
                continue
            meta = metadata[region]
            report = state_reports.get(re.sub(r"[^a-z]", "", region.lower()))
            sample_size, sample_id, sample_locator, daily, weekly = (
                "",
                "nfhs5_india_2019_21",
                "Table 1.2; printed pages 15-16 / PDF pages 51-52",
                "",
                "",
            )
            sample_basis = "Food-specific age 15-49 respondent count not published in national state food table; unavailable here."
            if report:
                source_values, sample_page, file = report[0 if sex == "women" else 1]
                assert len(source_values) == 6, (region, source_values)
                daily, weekly = source_values[:2]
                sample_size = source_values[-1].replace(",", "")
                sample_id = sid_for_state(file)
                sample_locator = f"Table 77; PDF page {sample_page}"
                sample_basis = "State report Table 77 reported respondents age 15-49; weighted tabulations (state-normalized), not a raw unweighted count."
                assert abs(float(daily) + float(weekly) - float(values[7])) <= 0.11, (
                    region,
                    sex,
                )
            elif sex == "women":
                sample_size = meta[6].replace(",", "")
                sample_basis = "Actual interviewed women age 15-49 in Table 1.2; food table does not restate its analytical respondent count."
            rows.append(
                {
                    "country": "India",
                    "region": region,
                    "region_type": "union_territory" if region in UTS else "state",
                    "year": "2021",
                    "indicator": f"{sex}_15_49_fish_chicken_or_meat_at_least_weekly",
                    "value": values[7],
                    "unit": "percent",
                    "source_id": "nfhs5_india_2019_21",
                    "sex": sex,
                    "age_group": "15-49",
                    "residence": "all",
                    "quintile": "all",
                    "period": "2019-21",
                    "sample_size": sample_size,
                    "sample_basis": sample_basis,
                    "survey_sample_size": meta[6 if sex == "women" else 8].replace(
                        ",", ""
                    ),
                    "survey_sample_basis": f"Table 1.2 actual unweighted interviewed {sex} age {'15-49' if sex == 'women' else '15-54'}; male total must not be used as food denominator.",
                    "denominator": f"Survey-weighted {sex} age 15-49 in the region; at least once weekly includes daily and weekly responses.",
                    "fieldwork_start": f"{meta[1]}-{int(meta[0]):02d}",
                    "fieldwork_end": f"{meta[3]}-{int(meta[2]):02d}",
                    "fieldwork_note": "Region-specific month and year from national Table 1.2; dates have month precision.",
                    "method": "Read the published at-least-weekly percentage directly; do not sum rounded daily/weekly components to replace it.",
                    "raw_file": "data/raw/regional/india-nfhs5-national.pdf",
                    "raw_locator": f"Table {table}; printed page {page-36}; PDF page {page}",
                    "sample_source_id": sample_id,
                    "sample_locator": sample_locator,
                    "daily_component": daily,
                    "weekly_component": weekly,
                    "display_value": values[7],
                    "notes": "Food frequency, not consumption mass, expenditure, or protein adequacy. Rounding can make state daily+weekly differ by 0.1 percentage point from national table.",
                }
            )
    assert len(rows) == 72
    return rows


def pakistan_sample_context() -> dict[tuple[str, str], list[str]]:
    """Read the report's household counts as separate workbook context."""
    text = (
        (RAW / "pakistan-hies-2024-25.txt")
        .read_text()
        .split("TABLE 2:-DISTRIBUTION", 1)[1]
        .split("TABLE 3:-", 1)[0]
    )
    context = {}
    current = "urban"
    for line in text.splitlines():
        if line.strip() == "RURAL":
            current = "rural"
        elif line.strip().startswith("TOTAL "):
            current = "all"
        match = re.match(r"\s*(Punjab|Sindh|KP|Balochistan)\s+([\d\s]+)$", line)
        if match:
            values = match.group(2).split()
            assert len(values) in (5, 6)
            # Wrapped totals are recovered by summing the explicitly published
            # five quintile counts and are marked as such in sample notes.
            total = str(sum(int(value) for value in values[:5]))
            if len(values) == 6:
                assert total == values[5]
            region = "Khyber Pakhtunkhwa" if match.group(1) == "KP" else match.group(1)
            context[(region, current)] = [total, *values[:5]]
    assert len(context) == 12
    for residence in ("all", "urban", "rural"):
        context[("Pakistan", residence)] = [
            str(
                sum(
                    int(context[(region, residence)][index])
                    for region in (
                        "Punjab",
                        "Sindh",
                        "Khyber Pakhtunkhwa",
                        "Balochistan",
                    )
                )
            )
            for index in range(6)
        ]
    return context


def extract_pakistan() -> list[dict[str, str]]:
    """Read the workbook's own survey year, sheet cells and native values."""
    book = xlrd.open_workbook(
        str(RAW / "pakistan-hies-table23.xls"), formatting_info=True
    )
    sheet = book.sheet_by_index(0)
    assert "2024-25" in str(sheet.cell_value(1, 0))
    assert [str(sheet.cell_value(3, col)).strip() for col in range(2, 8)] == [
        "Total",
        "1st",
        "2nd",
        "3rd",
        "4th",
        "5th",
    ]
    samples = pakistan_sample_context()
    rows = []
    region, residence = "", ""
    for row in range(sheet.nrows):
        name = str(sheet.cell_value(row, 0)).strip()
        heading = re.fullmatch(
            r"(PAKISTAN|PUNJAB|SINDH|KHYBER PAKHTUNKHWA|KP|BALOCHISTAN)(?: (URBAN|RURAL))?",
            name,
        )
        if heading:
            region = {
                "KP": "Khyber Pakhtunkhwa",
                "KHYBER PAKHTUNKHWA": "Khyber Pakhtunkhwa",
            }.get(heading.group(1), heading.group(1).title())
            residence = (heading.group(2) or "all").lower()
            continue
        if name.lower() not in {"mutton", "beef", "fish", "chicken meat", "eggs"}:
            continue
        assert region
        native_unit = sheet.cell_value(row, 1)
        assert native_unit in ("Kg", "No"), (name, native_unit)
        for index, column in enumerate(range(2, 8)):
            value = sheet.cell_value(row, column)
            assert isinstance(value, float) and value >= 0
            sample = samples[(region, residence)][index]
            rows.append(
                {
                    "country": "Pakistan",
                    "region": region,
                    "region_type": "national" if region == "Pakistan" else "province",
                    "year": "2025",
                    "indicator": f"monthly_per_capita_{name.lower().replace(' ', '_')}_consumption",
                    "value": repr(value),
                    "unit": (
                        "kg/person/month"
                        if native_unit == "Kg"
                        else "eggs/person/month"
                    ),
                    "source_id": "pakistan_hies_2024_25_table23",
                    "sex": "all",
                    "age_group": "all",
                    "residence": residence,
                    "quintile": ["all", "Q1", "Q2", "Q3", "Q4", "Q5"][index],
                    "period": "2024-25",
                    "sample_size": "",
                    "sample_basis": "Exact revised-workbook analytical sample not stated; see separately labelled report household-count context.",
                    "survey_sample_size": sample,
                    "survey_sample_basis": "Household count context from report Table 2, same province/residence/quintile; total is sum of five reported quintile counts. Workbook-vintage equivalence has not been established.",
                    "denominator": "Per household member per month in specified province/residence and national consumption-expenditure quintile; not a share of consumers.",
                    "fieldwork_start": "2024-09",
                    "fieldwork_end": "",
                    "fieldwork_note": "PBS catalog/preface say September 2024-June 2025; report foreword says September 2024-August 2025. End month unresolved.",
                    "method": "Read original XLS cached numeric cell via xlrd 2.0.2. Preserve full stored precision; display_value follows native 0.00 cell format. No imputation.",
                    "raw_file": "data/raw/regional/pakistan-hies-table23.xls",
                    "raw_locator": f"Sheet1!{chr(65+column)}{row+1}; Table 23; {name}",
                    "sample_source_id": "pakistan_hies_2024_25_report",
                    "sample_locator": "Table 2; printed page 29; PDF page 46",
                    "display_value": f"{value:.2f}",
                    "notes": "Workbook title confirms 2024-25 despite catalog linking same URL under 2018-19. Workbook national totals differ from report Table 3.7.C; retained as separate source vintage. Exact sample and fieldwork-end uncertainty remain.",
                }
            )
    assert len(rows) == 450, len(rows)
    return rows


def main() -> None:
    """Write the regional rows and check coverage and source-shaped values."""
    rows = extract_india() + extract_pakistan()
    with (OUT / "extracted_rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    assert len(rows) == 522
    assert len({row["region"] for row in rows if row["country"] == "India"}) == 36
    assert len({row["region"] for row in rows if row["region_type"] == "province"}) == 4
    assert all(
        0 <= float(row["value"]) <= 100 for row in rows if row["unit"] == "percent"
    )
    assert len(
        {
            tuple(
                row.get(key, "")
                for key in ("country", "region", "indicator", "residence", "quintile")
            )
            for row in rows
        }
    ) == len(rows)
    print(
        "PASS: 522 regional rows; India 36 states/UTs, Pakistan 4 provinces plus national comparator; native measures kept separate."
    )


if __name__ == "__main__":
    main()
