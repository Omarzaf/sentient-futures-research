"""Extract source-reported and harmonized anthropometry without inferring protein deficiency."""

from __future__ import annotations

import csv
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/deficiency/anthropometry"
OUT = Path(__file__).resolve().parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NFHS = "nfhs5_india_2019_21"
NNS = "pakistan_nns2018_volume1"
SURVEY = "jme_survey_database_march2026"
MODEL = "jme_country_model_march2026"
REPORT = "jme_key_findings_2025"
URLS = {
    NFHS: "https://dhsprogram.com/pubs/pdf/FR375/FR375.pdf",
    NNS: "https://www.unicef.org/pakistan/media/2826/file/National%20Nutrition%20Survey%202018%20Volume%201.pdf",
    SURVEY: "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/jme-database-march2026-edition.xlsx?sfvrsn=19e265c4_3",
    MODEL: "https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/jme-country-estimates-march2026.xlsx?sfvrsn=65301f6b_3",
    REPORT: "https://iris.who.int/server/api/core/bitstreams/a0aad785-4ff8-43d7-bdf9-be6c9a221e8e/content",
}
CATALOG = "https://www.who.int/teams/nutrition-and-food-safety/monitoring-nutritional-status-and-food-safety-and-events/joint-child-malnutrition-estimates/latest-estimates"


def sheet_rows(path: Path, sheet: str) -> list[tuple[int, dict[str, str]]]:
    """Read source XLSX cell values and coordinates using only Python's standard library."""
    with ZipFile(path) as archive:
        strings = [
            "".join(item.itertext())
            for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))
        ]
        relationships = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        sheets = ET.fromstring(archive.read("xl/workbook.xml")).find("m:sheets", NS)
        assert sheets is not None
        target = next(item for item in sheets if item.attrib["name"] == sheet)
        sheet_path = "xl/" + relationships[target.attrib[f"{{{REL}}}id"]]
        data = ET.fromstring(archive.read(sheet_path)).find("m:sheetData", NS)
        assert data is not None
        rows = []
        for row in data:
            values = {}
            for cell in row:
                value_element = cell.find("m:v", NS)
                value = "" if value_element is None else value_element.text or ""
                if cell.attrib.get("t") == "s":
                    value = strings[int(value)]
                column = re.sub(r"\d", "", cell.attrib["r"])
                values[column] = value
            rows.append((int(row.attrib["r"]), values))
        return rows


def write_rows(name: str, rows: list[dict[str, object]]) -> None:
    """Write a provenance-preserving CSV fragment without modifying shared outputs."""
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def base_row(
    country: str, year: int, indicator: str, source_id: str
) -> dict[str, object]:
    """Supply descriptive fields shared by every anthropometric proxy row."""
    return {
        "country": country,
        "region": "National",
        "year": year,
        "indicator": f"under5_{indicator}",
        "value": "",
        "unit": "percent",
        "population_base": "",
        "population_source_id": "",
        "population_affected_published": "",
        "population_affected_low_published": "",
        "population_affected_high_published": "",
        "population_vintage": "",
        "population_table_or_page": "",
        "population_alignment": "",
        "source_id": source_id,
        "estimate_type": "",
        "sample_size": "",
        "sample_size_type": "",
        "survey_period": "",
        "fieldwork_start": "",
        "fieldwork_end": "",
        "denominator": "children aged 0-59 months with valid indicator measurements",
        "definition": {
            "stunting": "height-for-age z-score below -2 SD",
            "wasting": "weight-for-height z-score below -2 SD",
            "underweight": "weight-for-age z-score below -2 SD",
        }[indicator],
        "table_or_page": "",
        "ci_lower": "",
        "ci_upper": "",
        "notes": "",
    }


def main() -> None:
    """Extract 14 national proxy rows and two explicit JME population cells."""
    rows = []
    india_pages = (
        (ROOT / "data/raw/regional/india-nfhs5-national.txt").read_text().split("\f")
    )
    total = next(
        line for line in india_pages[425].splitlines() if re.match(r"\s*Total\s", line)
    )
    values = re.findall(r"-?\d[\d,]*(?:\.\d+)?", total)
    for indicator, value_idx, size_idx in (
        ("stunting", 1, 3),
        ("wasting", 5, 8),
        ("underweight", 10, 13),
    ):
        row = base_row("India", 2020, indicator, NFHS)
        row.update(
            {
                "value": values[value_idx],
                "sample_size": values[size_idx].replace(",", ""),
                "sample_size_type": "weighted table denominator; not unweighted respondent count",
                "estimate_type": "survey_as_published",
                "survey_period": "2019-2021",
                "fieldwork_start": "2019-06-17",
                "fieldwork_end": "2021-04-30",
                "table_or_page": "Table10.1 printed p390/PDF426; fieldwork printed p7/PDF43; weighting Table1.2 printed p16/PDF52",
                "notes": "Under5 growth proxy, not protein deficiency. Children present the preceding night; valid birth dates and anthropometry. Survey assigned2020 for population matching only. Do not add overlapping indicators. Published NFHS results differ from JME reanalysis.",
            }
        )
        rows.append(row)

    pakistan_pages = (RAW / "pakistan-nns2018-volume1.txt").read_text().split("\f")
    for indicator, page, table in (
        ("stunting", 101, "4-3"),
        ("wasting", 103, "4-4"),
        ("underweight", 106, "4-6"),
    ):
        line = next(
            line
            for line in pakistan_pages[page - 1].splitlines()
            if re.match(r"\s*Total\s", line)
        )
        values = re.findall(r"-?\d[\d,]*(?:\.\d+)?", line)
        row = base_row("Pakistan", 2018, indicator, NNS)
        row.update(
            {
                "value": values[0],
                "sample_size": values[-1],
                "sample_size_type": "published indicator-specific analytical count; table does not explicitly label count weighting",
                "estimate_type": "survey_as_published",
                "survey_period": "2018-2019",
                "fieldwork_start": "2018-04",
                "fieldwork_end": "2019-01",
                "table_or_page": f"Table{table} printed/PDF p{page}; fieldwork p67; sampling/weighting p69; exclusion rules p70",
                "notes": "Source-reported NNS national rate includes AJK and GB. JME March2026 Other Sources row183 excludes this survey; exclusion reason not stated. Population multiplier withheld pending geographically matched under5 base. Under5 growth proxy, not protein deficiency; indicators overlap.",
            }
        )
        rows.append(row)

    survey_file = RAW / "jme-database-march2026-edition.xlsx"
    survey = sheet_rows(survey_file, "Primary Data")
    pop_rows = []
    for iso, country, survey_year, year in (
        ("IND", "India", "2019-2021", 2020),
        ("PAK", "Pakistan", "2017-2018", 2018),
    ):
        matches = [
            (number, data)
            for number, data in survey
            if data.get("A") == iso
            and data.get("C") == survey_year
            and data.get("R") == "Total"
        ]
        assert len(matches) == 1
        number, data = matches[0]
        assert data["D"] == str(year)
        population = str(Decimal(data["AK"]) * 1000)
        pop_rows.append(
            {
                "country": country,
                "year": year,
                "population_group": "children_under5_both_sexes",
                "population_base": population,
                "source_value": data["AK"],
                "source_unit": "thousand persons",
                "source_id": SURVEY,
                "table_or_page": f"Primary Data!AK{number}",
                "vintage": "JME March2026; underlying WPP revision not specified in workbook",
                "notes": (
                    "JME-listed population; not survey sample size. Pakistan source survey footnote36 excludes AJK/GB; the population cell does not explicitly state territorial exclusions. Do not transfer to NNS2018 national coverage without reconciliation."
                    if iso == "PAK"
                    else "JME-listed population for NFHS assigned year2020; not survey sample size."
                ),
            }
        )
        if iso == "IND":
            for original in rows[:3]:
                original.update(
                    {
                        "population_base": population,
                        "population_source_id": SURVEY,
                        "population_table_or_page": f"Primary Data!AK{number}",
                        "population_alignment": "documented_approximation",
                        "population_vintage": "JME March2026; underlying WPP revision not specified in workbook",
                        "notes": str(original["notes"])
                        + " Population uses JME-listed under5 base for the same NFHS survey assigned2020; applying the survey-period rate to a single-year population is an explicitly approximate cross-sectional burden, not survey enumeration or annual incidence.",
                    }
                )
        for indicator, value_col, n_col in (
            ("stunting", "AB", "AA"),
            ("wasting", "W", "T"),
            ("underweight", "AE", "AD"),
        ):
            row = base_row(country, year, indicator, SURVEY)
            row.update(
                {
                    "value": data[value_col],
                    "sample_size": data[n_col],
                    "sample_size_type": "JME reanalysis sample N as published; weighted decimal count; not an unweighted number of interviews",
                    "estimate_type": "JME_reanalyzed_survey",
                    "survey_period": survey_year,
                    "survey_name": "PDHS 2017–18" if iso == "PAK" else "NFHS-5 2019–21",
                    "fieldwork_start": "2019-06" if iso == "IND" else "2017-11",
                    "fieldwork_end": "2021-05" if iso == "IND" else "2018-04",
                    "table_or_page": f"Primary Data!{value_col}{number}; sample {n_col}{number}; fieldwork AG{number}",
                    "population_base": population,
                    "population_source_id": SURVEY,
                    "population_alignment": (
                        "documented_approximation" if iso == "PAK" else "source_matched"
                    ),
                    "population_table_or_page": f"Primary Data!AK{number}",
                    "population_vintage": "JME March2026; underlying WPP revision not specified in workbook",
                    "notes": "Under5 growth proxy, not protein deficiency. JME harmonized reanalysis; keep distinct from original national report. Wasting prevalence times population is a cross-sectional estimate, not annual cases."
                    + (
                        " Footnote36 excludes AJK and GB; JME-listed population territorial coverage not explicit. Latest included Pakistan source is DHS2017-18, not excluded NNS2018."
                        if iso == "PAK"
                        else " JME fieldwork metadata ends May2021, whereas primary NFHS text ends30April2021; retain both as reported."
                    ),
                }
            )
            rows.append(row)

    model_file = RAW / "jme-country-estimates-march2026.xlsx"
    prevalence = sheet_rows(model_file, "Stunting Prevalence")
    counts = sheet_rows(model_file, "Stunting Numbers Affected")
    for iso, country in (("IND", "India"), ("PAK", "Pakistan")):
        selected = [
            (n, d) for n, d in prevalence if d.get("C") == iso and d.get("E") == "2024"
        ]
        selected_counts = [
            (n, d) for n, d in counts if d.get("C") == iso and d.get("E") == "2024"
        ]
        assert len(selected) == len(selected_counts) == 1
        number, data = selected[0]
        count_number, count = selected_counts[0]
        row = base_row(country, 2024, "stunting", MODEL)
        row.update(
            {
                "value": data["F"],
                "ci_lower": data["G"],
                "ci_upper": data["H"],
                "estimate_type": "JME_country_model",
                "sample_size_type": "not applicable: modeled estimate from multiple source surveys",
                "denominator": "country model population aged0-59months, both sexes",
                "population_affected_published": str(Decimal(count["F"]) * 1000),
                "population_affected_low_published": str(Decimal(count["G"]) * 1000),
                "population_affected_high_published": str(Decimal(count["H"]) * 1000),
                "population_source_id": MODEL,
                "population_table_or_page": f"Stunting Numbers Affected!F{count_number}:H{count_number}; original unit thousands",
                "population_vintage": "JME March2026",
                "table_or_page": f"Stunting Prevalence!F{number}:H{number}",
                "notes": "Published model estimates for2024 from March2026 revision; not a2024 field survey. Published numbers converted from thousands to persons; no denominator back-calculated from rounded prevalence. Not protein deficiency and cannot be added to wasting/underweight counts.",
            }
        )
        rows.append(row)

    evidence_cells = []
    selections = [
        (survey_file, SURVEY, "Primary Data", {1128, 2143}),
        (survey_file, SURVEY, "Other Sources", {183}),
        (survey_file, SURVEY, "Notes", {49}),
        (survey_file, SURVEY, "Cover Page", {20, 22}),
        (model_file, MODEL, "Stunting Prevalence", {2051, 3401}),
        (model_file, MODEL, "Stunting Numbers Affected", {2051, 3401}),
        (model_file, MODEL, "Cover Page", {20, 22}),
    ]
    for path, sid, sheet, row_numbers in selections:
        for number, values in sheet_rows(path, sheet):
            if number in row_numbers:
                for column, value in values.items():
                    if value:
                        evidence_cells.append(
                            {
                                "source_id": sid,
                                "sheet": sheet,
                                "cell": f"{column}{number}",
                                "value": value,
                            }
                        )
    exclusions = dict(sheet_rows(survey_file, "Other Sources"))[183]
    assert (
        exclusions["A"] == "PAK"
        and exclusions["F"] == "Pakistan 2018 National Nutrition Survey"
    )
    assert all(exclusions[column] == "x" for column in ("I", "J", "K", "L", "M"))
    assert (
        "Excludes Azad Jammu and Kashmir and Gilgit Baltistan"
        in dict(sheet_rows(survey_file, "Notes"))[49]["B"]
    )
    write_rows("evidence_cells.csv", evidence_cells)

    assert len(rows) == 14
    assert [row["value"] for row in rows[:6]] == [
        "35.5",
        "19.3",
        "32.1",
        "40.2",
        "17.7",
        "28.9",
    ]
    assert [row["sample_size"] for row in rows[:6]] == [
        "201276",
        "197314",
        "205641",
        "59449",
        "57433",
        "60977",
    ]
    assert all(0 <= Decimal(str(row["value"])) <= 100 for row in rows)
    write_rows("extracted_rows.csv", rows)
    write_rows("population_rows.csv", pop_rows)

    titles = {
        NNS: "Pakistan National Nutrition Survey 2018, Volume1 (published2020)",
        SURVEY: "UNICEF/WHO/World Bank Joint Child Malnutrition Estimates Database, March2026",
        MODEL: "UNICEF/WHO/World Bank Joint Child Malnutrition Estimates Country Estimates, March2026",
        REPORT: "Levels and trends in child malnutrition: key findings of the2025 edition",
    }
    source_rows = [
        {
            "source_id": sid,
            "title": title,
            "publisher": (
                "Government of Pakistan / UNICEF / Aga Khan University"
                if sid == NNS
                else "UNICEF / WHO / World Bank"
            ),
            "url": URLS[sid],
            "year": 2020 if sid == NNS else 2025 if sid == REPORT else 2026,
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl official PDF/XLSX; PDF visual review; XLSX zip/XML coordinate extraction",
            "license": (
                "Public access; redistribution terms not established here"
                if sid != REPORT
                else "CC BY-NC-SA3.0 IGO as stated on copyright page; third-party exclusions apply"
            ),
            "notes": (
                "Original national survey retained even though JME March2026 excludes NNS2018 in Other Sources row183; no reason stated."
                if sid == NNS
                else (
                    "Current March2026 workbook; UNICEF catalog still describes2025 edition, WHO catalog labels2026; exact downloaded vintage retained."
                    if sid in (SURVEY, MODEL)
                    else "2025 edition methodology context; do not mix its2025 estimates with March2026 workbook without vintage labels."
                )
            ),
        }
        for sid, title in titles.items()
    ]
    write_rows("source_rows.csv", source_rows)

    manifests = []
    for path in sorted(RAW.iterdir()):
        if path.name.startswith("nfhs5-"):
            sid = NFHS
        elif path.name.startswith(("pakistan-", "nns2018-")):
            sid = NNS
        elif path.name.startswith("jme-country"):
            sid = MODEL
        elif path.name.startswith("jme-key"):
            sid = REPORT
        else:
            sid = SURVEY
        note = "Original official download."
        if path.suffix == ".png":
            note = "DERIVED Poppler page render; manually visually checked; original PDF unchanged."
        elif path.suffix == ".txt":
            note = "DERIVED pdftotext -layout extraction from same-named PDF."
        manifests.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": CATALOG if path.suffix == ".html" else URLS[sid],
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, tz=UTC
                ).isoformat(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "license": "Publicly accessible; consult source license before redistribution",
                "source_id": sid,
                "notes": note,
            }
        )
    write_rows("manifest_rows.csv", manifests)
    print(
        f"Validated {len(rows)} proxy rows; {len(pop_rows)} population cells; {len(source_rows)} new sources; {len(manifests)} raw artifacts."
    )


if __name__ == "__main__":
    main()
