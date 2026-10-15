"""Stage authenticated BAHS 2025 meat production tables and source receipts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from extract_hces import MERGED_UT, UTS, write_csv

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/regional/india-supplement-2026-10-13"
PDF = RAW / "bahs-2025-current.pdf"
SOURCE = "india_bahs_2025_full_book"
CATALOG_SOURCE = "dahd_migrated_public_search_20261013"
ODISHA_SOURCE = "india_loksabha_1718_20260210"
URL = "https://www.dahd.gov.in/static/uploads/2026/02/71836f721eb692711897d31f382eb926.pdf"
SEARCH_URL = "https://dahd.gov.in/cms/wp-json/custom/api/search?s=Basic%20Animal%20Husbandry%20Statistics"
ODISHA_URL = "https://sansad.in/getFile/loksabhaquestions/annex/187/AU1718_noXgsI.pdf?source=pqals"
PDF_HASH = "08c3b3fa8244b14b222ba25719e4742120dce631ac3fd0b9d3e8fe3c67bef6af"
LICENSE = "Not stated in retrieved document; public access does not establish redistribution license."
SPECIES = ("cattle", "buffalo", "sheep", "goat", "pig", "poultry")
VALUE = re.compile(r"(?<![\w.])(?:\d+\.\d{2}|-)(?![\w.])")
SOURCE_UT = "Daman & Diu and D.& N. Haveli"


def sha(path: Path) -> str:
    """Return a file checksum without changing it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(page: str, count: int) -> dict[str, tuple[str, list[str]]]:
    """Align table cells by their text-column positions, preserving blanks and dashes."""
    lines = page.splitlines()
    national = next(line for line in lines if "All India" in line)
    anchors = [match.end() for match in VALUE.finditer(national)]
    assert len(anchors) == count
    result = {}
    for index, line in enumerate(lines):
        serial = re.match(r"^\s*(\d{1,2})\s+", line)
        if not serial and "All India" not in line:
            continue
        if serial and not 1 <= int(serial[1]) <= 36:
            continue
        if serial and int(serial[1]) == 33:
            assert "Daman & Diu" in lines[index - 1]
            label = SOURCE_UT
            cells_text = [lines[index - 1], line]
        else:
            first = next(VALUE.finditer(line), None)
            assert first is not None, line
            start = serial.end() if serial else 0
            label = line[start : first.start()].strip()
            cells_text = [line]
        region = {
            "A&N Islands": "Andaman & Nicobar Islands",
            SOURCE_UT: MERGED_UT,
        }.get(label, label)
        assert region and region not in result, region
        cells = [""] * count
        for segment in cells_text:
            for match in VALUE.finditer(segment):
                position = min(
                    range(count), key=lambda column: abs(anchors[column] - match.end())
                )
                assert abs(anchors[position] - match.end()) <= 5, (
                    region,
                    match.group(),
                )
                assert cells[position] == "", (region, position)
                cells[position] = match.group()
        result[region] = (label, cells)
    assert len(result) == 37, len(result)
    return result


def make_row(
    region: str, label: str, year: int, species: str, value: str, locator: str
) -> dict[str, object]:
    """Build one regional production observation with explicit scope and precision."""
    return {
        "country": "India",
        "region": region,
        "region_type": "union_territory" if region in UTS else "state",
        "year": year + 1,
        "year_semantics": "ISS survey-period end year",
        "indicator": f"bahs_meat_production_{species}",
        "value": value,
        "unit": "1000 tonnes",
        "source_id": SOURCE,
        "sex": "all",
        "age_group": "all",
        "residence": "all",
        "quintile": "all",
        "period": f"{year}-{str(year + 1)[2:]}",
        "sample_size": "",
        "sample_basis": "Region/species-specific achieved sample count not provided with the production table.",
        "survey_sample_size": "",
        "survey_sample_basis": "ISS design is described in sections 1.3-1.5, printed pages 4-6 / PDF24-26. General sampling targets and cumulative e-LISS counts are not table-specific sample sizes.",
        "denominator": "Total production in the region; not a per-person measure.",
        "fieldwork_start": f"{year}-03",
        "fieldwork_end": f"{year + 1}-02",
        "fieldwork_note": "ISS year is March-February, not calendar year or April-March fiscal year. Section1.1 explicitly dates the latest survey1Mar2024-28Feb2025; section1.3 defines annual periods.",
        "method": "Direct transcription of DAHD official ISS estimates compiled from State/UT Animal Husbandry Departments. No analyst-generated estimate.",
        "raw_file": str(PDF.relative_to(ROOT)),
        "raw_locator": locator,
        "sample_source_id": SOURCE,
        "sample_locator": "Sections1.3-1.5, printed4-6 / PDF24-26; no achieved state/species table sample supplied.",
        "display_value": value,
        "notes": "Production, not food intake, retail sales, exports or FAOSTAT availability. Published 0.00 is retained as reported at two-decimal precision; it is not an imputed zero or proof of exact absence. Six species remain distinct; cattle and buffalo are not silently combined.",
        "species": species,
        "source_region_label": label,
        "source_year": "2025",
        "source_vintage": "BAHS2025 full book; migrated official PDF uploaded2026-02-24",
        "raw_sha256": PDF_HASH,
        "missingness": "value present; achieved analytical sample unavailable",
        "staging_status": "SOURCE_TRANSCRIPTION_FOR_INTEGRATION_REVIEW",
    }


def main() -> None:
    """Extract latest regional series, full historical transcription and national totals."""
    assert sha(PDF) == PDF_HASH
    assert PDF.stat().st_size == 30617144
    pages = PDF.with_suffix(".txt").read_text().split("\f")
    total = table(pages[184], 7)
    part_a = table(pages[187], 6)
    part_b = table(pages[188], 6)
    assert set(total) == set(part_a) == set(part_b)
    assert total["Delhi"][1] == ["0.00", "-", "", "0.00", "0.00", "0.00", "0.00"]
    assert total["Ladakh"][1][:3] == ["-", "-", "0.02"]
    assert part_a[MERGED_UT][1] == ["0.00"] * 6
    assert part_b[MERGED_UT][1] == ["0.05", "0.05", "0.00", "0.00", "0.00", "0.00"]

    # Independent visual readings from the three rendered pages, including wrapped cells.
    assert total["All India"][1] == [
        "8114.45",
        "8599.97",
        "8797.91",
        "9292.13",
        "9768.64",
        "10252.65",
        "10504.54",
    ]
    assert total["West Bengal"][1][-2:] == ["1293.85", "1307.83"]
    assert total["Andhra Pradesh"][1][-2:] == ["1067.88", "1137.63"]
    assert part_a["Andhra Pradesh"][1] == [
        "24.35",
        "0.00",
        "163.78",
        "197.10",
        "393.54",
        "418.43",
    ]
    assert part_b["Andhra Pradesh"][1] == [
        "102.78",
        "100.58",
        "1.53",
        "1.51",
        "381.91",
        "420.00",
    ]
    assert part_a["All India"][1] == [
        "266.40",
        "242.03",
        "1854.64",
        "1935.16",
        "1141.45",
        "1186.42",
    ]
    assert part_b["All India"][1] == [
        "1588.94",
        "1582.14",
        "381.79",
        "383.50",
        "5019.51",
        "5175.29",
    ]
    odisha_text = (RAW / "loksabha-odisha1718.txt").read_text().split("\f")[3]
    odisha_line = next(
        line for line in odisha_text.splitlines() if "II. Meat Production" in line
    )
    odisha_values = re.findall(r"\d+\.\d{2}", odisha_line)
    assert (
        total["Odisha"][1][-5:]
        == odisha_values
        == ["213.10", "216.20", "226.87", "242.30", "246.30"]
    )

    regional = []
    national = []
    historical = []
    reconciliation = []
    for region, (label, values) in total.items():
        for index, token in enumerate(values):
            year = 2018 + index
            historical.append(
                {
                    "country": "India",
                    "region": region,
                    "period": f"{year}-{str(year + 1)[2:]}",
                    "year": year,
                    "species": "total",
                    "value": "" if token == "-" else token,
                    "source_token": token,
                    "unit": "1000 tonnes",
                    "source_id": SOURCE,
                    "raw_locator": f"Table62; printed166 / PDF185; {label}; {year}-{str(year + 1)[2:]}",
                    "missingness": (
                        "dash: not reported by State/UT"
                        if token == "-"
                        else (
                            "blank in source; not zero"
                            if token == ""
                            else "published value"
                        )
                    ),
                    "notes": "Ladakh is included in J&K through2019-20; Ladakh2020-21 covers winter only. D&N Haveli and Daman&Diu were separate UTs through2019-20 and merged2020; historical combined label is the publisher's representation. Historical transcription preserves all missing cells and is separate from latest-two-year integration batch.",
                }
            )
        for period_index, year in enumerate((2023, 2024)):
            species_values = {
                species: values[period_index + 2 * (i % 3)]
                for i, species in enumerate(SPECIES)
                for values in [(part_a if i < 3 else part_b)[region][1]]
            }
            total_value = total[region][1][5 + period_index]
            difference = sum(
                Decimal(value) for value in species_values.values()
            ) - Decimal(total_value)
            reconciliation.append(
                {
                    "region": region,
                    "period": f"{year}-{str(year + 1)[2:]}",
                    "species_sum_minus_reported_total_1000_tonnes": str(difference),
                }
            )
            for species, value in {"total": total_value, **species_values}.items():
                assert value not in {"", "-"}
                assert Decimal(value) >= 0
                page, printed, table_id = (
                    (185, 166, "62")
                    if species == "total"
                    else (
                        (188, 169, "64(A)")
                        if species in SPECIES[:3]
                        else (189, 170, "64(B)")
                    )
                )
                locator = f"Table{table_id}; printed{printed} / PDF{page}; {label}; {species}; {year}-{str(year + 1)[2:]}"
                row = make_row(region, label, year, species, value, locator)
                if region == "All India":
                    national.append(
                        {
                            "country": "India",
                            "year": year,
                            "item": (
                                "total meat"
                                if species == "total"
                                else f"{species} meat"
                            ),
                            "metric": "production",
                            "value": value,
                            "unit": "1000 tonnes",
                            "source_id": SOURCE,
                            "flag": "official_estimate;ISS_survey_year_start;BAHS2025_full_book_vintage",
                            "method": row["method"],
                            "period": row["period"],
                            "raw_file": row["raw_file"],
                            "raw_locator": locator,
                            "notes": str(row["notes"])
                            + " Survey-year March-February; retain distinction from rounded PIB summary, other vintages and calendar-year FAOSTAT/USDA estimates.",
                            "source_vintage": row["source_vintage"],
                            "sample_size": "",
                            "sample_basis": row["sample_basis"],
                        }
                    )
                else:
                    regional.append(row)
    # Add the other five national historical totals directly from the same table.
    prototype = next(row for row in national if row["item"] == "total meat")
    for index, year in enumerate(range(2018, 2023)):
        national.append(
            {
                **prototype,
                "year": year,
                "period": f"{year}-{str(year + 1)[2:]}",
                "value": total["All India"][1][index],
                "raw_locator": f"Table62; printed166 / PDF185; All India; total meat; {year}-{str(year + 1)[2:]}",
            }
        )
    assert len(regional) == 504 and len(national) == 19 and len(historical) == 259
    assert len({(r["region"], r["period"], r["species"]) for r in regional}) == 504
    assert len({r["region"] for r in regional}) == 36
    assert sum(row["value"] == "" for row in historical) == 4
    write_csv(OUT / "bahs_regional_rows.csv", regional)
    write_csv(OUT / "bahs_national_rows.csv", national)
    write_csv(OUT / "bahs_table62_historical_transcription.csv", historical)
    write_csv(OUT / "bahs_reconciliation.csv", reconciliation)

    sources = [
        {
            "source_id": SOURCE,
            "title": "Basic Animal Husbandry Statistics 2025 (full220-page book; migrated official PDF)",
            "publisher": "Government of India, Department of Animal Husbandry and Dairying",
            "url": URL,
            "year": "2025",
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl HTTPS200; migrated PDF discovered from the anonymous official DAHD public-search endpoint; no TLS bypass or credentials",
            "license": LICENSE,
            "notes": "ISS survey1Mar2024-28Feb2025. Tables62/64A/64B national/state species production; general survey design sections1.3-1.5. Official CMS record23101 uploaded2026-02-24. Source estimates, not sales/intake. Some rounded component sums differ; retained published values with reconciliation receipt.",
        },
        {
            "source_id": CATALOG_SOURCE,
            "title": "DAHD migrated official public search and BAHS2025 asset locator",
            "publisher": "Government of India, Department of Animal Husbandry and Dairying",
            "url": SEARCH_URL,
            "year": "2026",
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl anonymous public GET; endpoint observed in linked homepage scripts; no API key sent",
            "license": LICENSE,
            "notes": "Acquisition provenance only; no numerical research observations. Old/sites/default/files URLs404 after website migration. Search result record23101 points to authenticated official static PDF.",
        },
        {
            "source_id": ODISHA_SOURCE,
            "title": "Lok Sabha unstarred question1718: Indigenous breeds and animal husbandry performance,10February2026",
            "publisher": "Government of India, Ministry of Fisheries, Animal Husbandry and Dairying / Lok Sabha",
            "url": ODISHA_URL,
            "year": "2026",
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl official Parliament PDF HTTPS200",
            "license": LICENSE,
            "notes": "AnnexureII,PDF4 cites BAHS and independently matches all five Odisha2020-21 through2024-25 meat production cells. Corroboration only; no competing duplicate numeric rows staged.",
        },
    ]
    write_csv(OUT / "bahs_source_rows.csv", sources)
    file_urls = {
        "bahs-2025-current.pdf": (
            URL,
            SOURCE,
            "Original full official PDF, HTTP200;30,617,144bytes.",
        ),
        "bahs-2025-current.headers": (URL, SOURCE, "Download response headers."),
        "bahs-2025-current.txt": (
            URL,
            SOURCE,
            "DERIVED pdftotext -layout from full official PDF.",
        ),
        "bahs-table62-p185.png": (
            URL,
            SOURCE,
            "DERIVED Poppler PDF185 render, Table62, printed166; visually reviewed.",
        ),
        "bahs-table64a-p188.png": (
            URL,
            SOURCE,
            "DERIVED Poppler PDF188 render, Table64A, printed169; visually reviewed.",
        ),
        "bahs-table64b-p189.png": (
            URL,
            SOURCE,
            "DERIVED Poppler PDF189 render, Table64B, printed170; visually reviewed.",
        ),
        "dahd-current-home.html": (
            "https://dahd.gov.in/",
            CATALOG_SOURCE,
            "Official homepage used only to discover its linked search-client script.",
        ),
        "dahd-current-home.headers": (
            "https://dahd.gov.in/",
            CATALOG_SOURCE,
            "Homepage response headers.",
        ),
        "dahd-current-index.js": (
            "https://dahd.gov.in/_next/static/chunks/pages/index-537aec7ee35fef4a.js",
            CATALOG_SOURCE,
            "Public homepage script; acquisition evidence, never executed locally.",
        ),
        "dahd-current-app.js": (
            "https://dahd.gov.in/_next/static/chunks/pages/_app-6b2289dfd3783fed.js",
            CATALOG_SOURCE,
            "Public application script exposes anonymous public search URL; no credentials used.",
        ),
        "dahd-current-search.json": (
            SEARCH_URL,
            CATALOG_SOURCE,
            "Original public search result; no credentials sent.",
        ),
        "dahd-current-search.headers": (
            SEARCH_URL,
            CATALOG_SOURCE,
            "Public search response headers HTTP200.",
        ),
        "bahs-2025-current-catalog-record.json": (
            SEARCH_URL,
            CATALOG_SOURCE,
            "DERIVED exact record id23101 from preserved full public search JSON.",
        ),
        "loksabha-odisha1718.pdf": (
            ODISHA_URL,
            ODISHA_SOURCE,
            "Original official Parliament PDF, HTTP200.",
        ),
        "loksabha-odisha1718.headers": (
            ODISHA_URL,
            ODISHA_SOURCE,
            "Download response headers.",
        ),
        "loksabha-odisha1718.txt": (
            ODISHA_URL,
            ODISHA_SOURCE,
            "DERIVED pdftotext -layout.",
        ),
        "loksabha-odisha1718-p4.png": (
            ODISHA_URL,
            ODISHA_SOURCE,
            "DERIVED Poppler PDF4 render; independently visually reviewed meat row.",
        ),
    }
    manifest = []
    for filename, (url, source_id, note) in file_urls.items():
        path = RAW / filename
        manifest.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": url,
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, UTC
                ).isoformat(),
                "sha256": sha(path),
                "license": LICENSE,
                "source_id": source_id,
                "notes": note
                + " Timestamp is local file completion time; derivatives retain original URL and parent in this receipt.",
            }
        )
    write_csv(OUT / "bahs_manifest_rows.csv", manifest)
    warnings = [
        r
        for r in reconciliation
        if abs(Decimal(r["species_sum_minus_reported_total_1000_tonnes"]))
        > Decimal("0.035")
    ]
    report = {
        "status": "PASS_FOR_STAGING_REVIEW_WITH_SOURCE_ARITHMETIC_WARNINGS",
        "source_id": SOURCE,
        "pdf_sha256": PDF_HASH,
        "pdf_bytes": PDF.stat().st_size,
        "pdf_pages": 220,
        "regional_rows": 504,
        "regions": 36,
        "periods": ["2023-24", "2024-25"],
        "species": ["total", *SPECIES],
        "national_rows": 19,
        "historical_table62_cells": 259,
        "historical_missing_cells": 4,
        "latest_batch_missing_values": 0,
        "independent_odisha_cells_matched": 5,
        "component_reconciliation_checks": len(reconciliation),
        "source_component_discrepancies_above_rounding_bound": warnings,
        "regional_csv_sha256": sha(OUT / "bahs_regional_rows.csv"),
        "national_csv_sha256": sha(OUT / "bahs_national_rows.csv"),
        "source_rows": len(sources),
        "manifest_rows": len(manifest),
    }
    (OUT / "bahs_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
