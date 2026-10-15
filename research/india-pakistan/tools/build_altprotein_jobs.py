"""Build data/altprotein_jobs.csv from the two AltProtein.Jobs workbooks.

The workbooks were shared with the project by AltProtein.Jobs and are not
redistributed. This script keeps only company-level directory fields and
country-level vacancy counts. Contact columns (first name, last name, position)
are never read into the output.

Usage (openpyxl required):
    python3 tools/build_altprotein_jobs.py DIRECTORY.xlsx VACANCY.xlsx
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/altprotein_jobs.csv"
DIRECTORY_SOURCE = "altprotein_jobs_company_directory_2024"
VACANCY_SOURCE = "altprotein_jobs_vacancy_2023_2025"
DIRECTORY_RAW = "data/raw/altprotein/jobs/companies-with-jobs-on-altprotein-jobs.xlsx"
VACANCY_RAW = "data/raw/altprotein/jobs/global-vacancy-data-2023-2025.xlsx"
# Exact Country_province spellings found in the directory for the three countries.
COUNTRY_CODES = {
    "India": {"India", "IN"},
    "Brazil": {"Brazil", "Brasil", "BR"},
    "Pakistan": {"Pakistan", "PK"},
}
FIELDS = [
    "record_type",
    "country",
    "country_source_value",
    "region",
    "year",
    "period",
    "entity",
    "normalized_name",
    "directory_id",
    "value",
    "has_value",
    "posting_status",
    "protein_category",
    "company_focus",
    "business_model",
    "unit",
    "source_id",
    "tier",
    "raw_file",
    "raw_sha256",
    "raw_locator",
    "notes",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value: object) -> str:
    """Return an integer string; blank when the source cell is empty or NULL."""
    if value in (None, "", "NULL"):
        return ""
    result = float(value)
    if result != int(result):
        raise ValueError(f"Non-integer count: {value}")
    return str(int(result))


def text(value: object) -> str:
    return "" if value is None else str(value).strip()


def directory_rows(path: Path) -> list[dict[str, str]]:
    sheet = openpyxl.load_workbook(path, read_only=True, data_only=True)[
        "Companies with jobs since Octob"
    ]
    rows = list(sheet.iter_rows(values_only=True))
    header = {name: index for index, name in enumerate(rows[0])}
    digest = sha256(path)
    out = []
    for offset, row in enumerate(rows[1:], start=2):
        raw_country = text(row[header["Country_province"]])
        country = next((k for k, v in COUNTRY_CODES.items() if raw_country in v), "")
        if not country:
            continue
        name = text(row[header["Business Name"]])
        value = number(row[header["number_of_jobs_since_oct_24"]])
        status = "missing" if not value else "positive" if int(value) > 0 else "zero"
        out.append(
            {
                "record_type": "directory_row",
                "country": country,
                "country_source_value": raw_country,
                "period": "postings since October 2024; end date not recorded",
                "entity": name,
                "normalized_name": name.lower(),
                "directory_id": number(row[header["id"]]),
                "value": value,
                "has_value": "true" if value else "false",
                "posting_status": status,
                "protein_category": text(row[header["protein_categories"]]),
                "company_focus": text(row[header["company_focuses"]]),
                "business_model": text(row[header["business_model"]]),
                "unit": "job postings",
                "source_id": DIRECTORY_SOURCE,
                "tier": "C",
                "raw_file": DIRECTORY_RAW,
                "raw_sha256": digest,
                "raw_locator": f"Sheet 'Companies with jobs since Octob', row {offset}; "
                "columns B id, C Business Name, D Country_province, E-G categories, "
                "K number_of_jobs_since_oct_24",
                "notes": "Directory membership is not proof of current operation. "
                "Contact columns L-N are excluded."
                + (
                    " Posting cell is NULL and the row's category fields are"
                    " misaligned in the source; values are kept as recorded."
                    if status == "missing"
                    else ""
                ),
            }
        )
    return out


def vacancy_rows(path: Path) -> list[dict[str, str]]:
    sheet = openpyxl.load_workbook(path, read_only=True, data_only=True)["4ai.2"]
    rows = list(sheet.iter_rows(values_only=True))
    years = {2: "2023", 3: "2024", 4: "2025"}
    digest = sha256(path)
    out = []
    for offset, row in enumerate(rows[1:], start=2):
        if not text(row[0]):
            continue
        for column, year in years.items():
            out.append(
                {
                    "record_type": "annual_vacancies",
                    "country": text(row[0]),
                    "country_source_value": text(row[0]),
                    "region": text(row[1]),
                    "year": year,
                    "period": f"January-December {year}",
                    "value": number(row[column]),
                    "has_value": "true",
                    "unit": "job vacancies",
                    "source_id": VACANCY_SOURCE,
                    "tier": "C",
                    "raw_file": VACANCY_RAW,
                    "raw_sha256": digest,
                    "raw_locator": f"Sheet 4ai.2, cell {'CDE'[column - 2]}{offset}",
                    "notes": "Platform vacancy count; not a national employment census. "
                    "Country basis (company headquarters or job location) is not documented.",
                }
            )
    return out


def main() -> None:
    directory, vacancy = map(Path, sys.argv[1:3])
    data = directory_rows(directory) + vacancy_rows(vacancy)
    with OUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in FIELDS} for row in data)
    print(f"{OUT.relative_to(ROOT)}: {len(data)} rows")


if __name__ == "__main__":
    main()
