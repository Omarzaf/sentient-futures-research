"""Reconcile local vacancy sources and write the D3 tables using only stdlib.

Run with python3 from any directory. Only D3-vacancy-tables.csv is written.
The shared workbook must match the SHA-256 recorded in altprotein_jobs.csv.
"""

from __future__ import annotations

import csv
import hashlib
import posixpath
import re
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zipfile import ZipFile

STUDY = Path(__file__).resolve().parents[1]
REPO = STUDY.parents[1]
OUTPUT = Path(__file__).with_name("D3-vacancy-tables.csv")
COUNTRIES = ("India", "Pakistan", "Brazil")
YEARS = ("2023", "2024", "2025")
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
FIELDS = (
    "metric", "country", "year", "value", "unit", "claim_id", "claim_status",
    "source_claim_ids", "population_millions", "population_input_id",
    "source_ids", "raw_file", "raw_sha256", "raw_locator", "workbook_read_path",
    "population_raw_file", "population_raw_sha256", "population_raw_locator", "notes",
)
DEMAND_NOTE = (
    "Demand signal on one job board; not employment or measured skill shortages. "
    "Country attribution and posting deduplication are undocumented."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 source table without modifying it."""
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def workbook_path(record: dict[str, str]) -> Path:
    """Find the cited workbook or its shared workspace original by exact hash."""
    candidates = (
        STUDY / record["raw_file"],
        REPO / record["raw_file"],
        REPO.parent / "AltProtein.Jobs resources" / "Global vacancy data 2023-2025.xlsx",
    )
    for path in candidates:
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest == record["raw_sha256"]:
                return path
    raise ValueError("Cited vacancy workbook missing or SHA-256 does not match")


def workbook_cells(path: Path) -> dict[str, dict[str, str]]:
    """Read cached XLSX values, including shared and inline strings, by cell."""
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [
                "".join(node.text or "" for node in item.findall(".//s:t", NS))
                for item in root.findall("s:si", NS)
            ]
        relations = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = {}
        for sheet in workbook.findall("s:sheets/s:sheet", NS):
            target = relations[sheet.attrib[REL_ID]]
            target = (target.lstrip("/") if target.startswith("/")
                      else posixpath.normpath("xl/" + target))
            cells = {}
            for cell in ET.fromstring(archive.read(target)).findall(
                "s:sheetData/s:row/s:c", NS
            ):
                value = cell.find("s:v", NS)
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s":
                    text = strings[int(text)]
                elif cell.attrib.get("t") == "inlineStr":
                    text = "".join(n.text or "" for n in cell.findall("s:is//s:t", NS))
                cells[cell.attrib["r"]] = text.strip()
            sheets[sheet.attrib["name"]] = cells
        return sheets


def integer_count(value: str) -> str:
    """Reject missing, negative or fractional counts instead of treating as zero."""
    number = Decimal(value)
    if not number.is_finite() or number < 0 or number != number.to_integral_value():
        raise ValueError(f"Invalid count: {value!r}")
    return str(int(number))


def tabulate() -> list[dict[str, str]]:
    """Reconcile every country-year and retain source and missing-data notes."""
    jobs = read_csv(STUDY / "data/altprotein_jobs.csv")
    populations = read_csv(STUDY / "data/altprotein_proxy_inputs.csv")
    vacancies = [r for r in jobs if r["record_type"] == "annual_vacancies"
                 and r["country"] in COUNTRIES and r["year"] in YEARS]
    keys = [(r["country"], r["year"]) for r in vacancies]
    if len(keys) != len(set(keys)) or set(keys) != {
        (country, year) for country in COUNTRIES for year in YEARS
    }:
        raise ValueError("Expected exactly one vacancy record per country-year")
    source = vacancies[0]
    if any((r["raw_file"], r["raw_sha256"]) !=
           (source["raw_file"], source["raw_sha256"]) for r in vacancies):
        raise ValueError("Vacancy rows do not cite a single workbook revision")
    path = workbook_path(source)
    sheets = workbook_cells(path)
    headers = [value for cells in sheets.values() for key, value in cells.items()
               if re.fullmatch(r"[A-Z]+1", key) and value]
    if any(re.search(r"function|category|categories|occupation|role|job.?type", h, re.I)
           for h in headers):
        raise ValueError("Workbook schema changed: inspect role/category columns before tabulation")
    role_note = (
        "No role, function or vacancy category column in any worksheet header; "
        "vacancies by role function are unavailable. Company directory categories "
        "describe businesses, not job functions."
    )
    cells = sheets["4ai.2"]
    for year, column in zip(YEARS, "CDE"):
        if cells.get(column + "1") != f"Jobs ({year})":
            raise ValueError("Annual vacancy column header changed")
    population_index = {}
    for row in populations:
        if (row["quantity"] == "population" and row["country"] in COUNTRIES
                and row["year"] in YEARS):
            key = (row["country"], row["year"])
            if key in population_index:
                raise ValueError(f"Duplicate population record: {key}")
            if (row["unit"] != "million people" or row["source_id"] != "imf_weo_2026_10"
                    or not Decimal(row["value"]).is_finite() or Decimal(row["value"]) <= 0):
                raise ValueError(f"Invalid IMF population denominator: {key}")
            population_index[key] = row
    directory_counts = Counter(r["country"] for r in jobs if r["record_type"] == "directory_row")
    output = []
    for country in COUNTRIES:
        for year in YEARS:
            record = next(r for r in vacancies if (r["country"], r["year"]) == (country, year))
            match = re.fullmatch(r"Sheet 4ai\.2, cell ([A-Z]+)(\d+)", record["raw_locator"])
            if not match or match[1] != dict(zip(YEARS, "CDE"))[year]:
                raise ValueError("Unexpected vacancy cell locator")
            if cells.get("A" + match[2]) != country:
                raise ValueError("Workbook country does not match the source record")
            count = integer_count(cells[match[1] + match[2]])
            if count != integer_count(record["value"]):
                raise ValueError(f"Workbook/CSV count mismatch: {country} {year}")
            claim = f"jobs_vacancies_{country.lower()}_{year}"
            base = {
                "country": country, "year": year, "source_claim_ids": claim,
                **{key: record[key] for key in ("raw_file", "raw_sha256", "raw_locator")},
                "workbook_read_path": posixpath.relpath(path.as_posix(), REPO.as_posix()),
                "source_ids": record["source_id"],
            }
            output.append({**base, "metric": "annual_vacancies", "value": count,
                           "unit": "job vacancies", "claim_id": claim,
                           "claim_status": "existing", "notes": DEMAND_NOTE + " " + role_note})
            population = population_index.get((country, year))
            rate = {**base, "metric": "vacancies_per_million", "value": "",
                    "unit": "job vacancies per million people", "claim_status": "unavailable",
                    "notes": DEMAND_NOTE + " No population row for this country-year in "
                    "altprotein_proxy_inputs.csv; denominator and rate left blank, not zero."}
            if population:
                value = Decimal(count) / Decimal(population["value"])
                rate.update({
                    "value": str(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
                    "claim_id": f"d3_vacancies_per_million_{country.lower()}_{year}",
                    "claim_status": "new_claim_needed",
                    "population_millions": population["value"],
                    "population_input_id": population["input_id"],
                    "source_ids": record["source_id"] + ";" + population["source_id"],
                    **{"population_" + key: population[key] for key in
                       ("raw_file", "raw_sha256", "raw_locator")},
                    "notes": DEMAND_NOTE + " Derived count / population in million people; "
                    "same-year IMF WEO October 2026 denominator; rounded to six decimals. "
                    "New derived claim needs registration; source count claim already exists.",
                })
            output.append(rate)
        directory = [r for r in jobs if r["record_type"] == "directory_row" and r["country"] == country]
        if not directory:
            raise ValueError(f"No directory rows recorded for {country}")
        output.append({
            "metric": "directory_rows", "country": country, "value": str(directory_counts[country]),
            "unit": "directory rows", "claim_id": f"jobs_directory_{country.lower()}_rows",
            "claim_status": "existing", "source_ids": directory[0]["source_id"],
            "raw_file": directory[0]["raw_file"], "raw_sha256": directory[0]["raw_sha256"],
            "raw_locator": "; ".join(r["raw_locator"].split(";", 1)[0] for r in directory),
            "notes": "Directory described as of 2024; accessed 2026-10-14. Count includes "
            "duplicate names; not distinct firms, current operations or annual vacancies. "
            "Postings-since-October-2024 end date is unrecorded. " + role_note,
        })
    return output


def main() -> None:
    """Write one deterministic UTF-8 CSV with LF line endings."""
    rows = tabulate()
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, restval="", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT.name}: {len(rows)} rows; workbook counts and hash reconciled")


if __name__ == "__main__":
    main()
