"""Extract paired prevalence and published affected counts from SOFI 2025."""

from __future__ import annotations

import csv
import hashlib
import re
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/deficiency/sofi"
SOURCE = "fao_sofi_2025"
URL = "https://www.fao.org/fileadmin/templates/cfs/CFS53/Plenary_documents/Inf.15_SOFI_Report/EN_compiled.pdf"
LICENSE = "Source labels CC BY 4.0; see PDF page 3 accompanying reuse terms and third-party exclusions"
COUNTRIES = ("India", "Pakistan")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write ordered CSV records without dropping empty metadata."""
    assert rows
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def country_tokens(page: str, country: str) -> list[str]:
    """Resolve one country row on a specified table page."""
    found = re.findall(rf"^\s*{country}\s+(.+)$", page, flags=re.MULTILINE)
    assert len(found) == 1, (country, len(found))
    return found[0].split()


def base_row(country: str, year: str, rate: str, count: str) -> dict[str, str]:
    """Create a paired rate/count record while retaining reported precision."""
    assert 0 <= Decimal(rate) <= 100 and Decimal(count) > 0
    persons = Decimal(count) * Decimal(1_000_000)
    assert persons == persons.to_integral_value()
    return {
        "country": country,
        "region": country,
        "year": year,
        "indicator": "",
        "value": rate,
        "unit": "percent",
        "population_affected_published": str(persons.to_integral_value()),
        "population_affected_published_unit": "persons",
        "population_affected_source_value": count,
        "population_affected_source_unit": "million persons",
        "population_affected_source_id": SOURCE,
        "population_affected_method": "Direct published affected count multiplied by exactly 1000000 to convert millions to persons. No population denominator is reconstructed from the rounded rate/count.",
        "source_id": SOURCE,
        "tier": "A",
        "source_vintage": "SOFI 2025; annex data accessed by publisher on 28 July 2025",
        "period": "",
        "period_type": "",
        "year_semantics": "",
        "denominator": "Total national population, all ages and sexes",
        "population_base": "",
        "population_base_source_id": "",
        "population_base_note": "Separate numeric base not extracted; published affected count retained. Do not backsolve a base from rounded count/rate.",
        "sample_size": "",
        "sample_basis": "Modelled national estimate drawing on multiple statistical inputs, not a single survey sample",
        "fieldwork_start": "",
        "fieldwork_end": "",
        "fieldwork_note": "Not a single fieldwork period; reference period and source-vintage fields apply",
        "raw_file": "data/raw/deficiency/sofi/sofi-2025.pdf",
        "raw_sha256": hashlib.sha256((RAW / "sofi-2025.pdf").read_bytes()).hexdigest(),
        "rate_locator": "",
        "count_locator": "",
        "method": "",
        "rounding_note": "Source rates and counts are displayed to one decimal; person units retain source count resolution of 0.1 million (100000 persons), not individual-level precision. No unrounded inputs are inferred.",
        "protein_deficiency_prevalence": "",
        "interpretation_limit": "",
    }


def extract() -> list[dict[str, str]]:
    """Read the exact source pages for all requested available reference years."""
    pages = (RAW / "sofi-2025.txt").read_text().split("\f")
    assert "July 2025" in pages[0]
    assert "2025" in pages[1] and "FOOD SECURITY" in pages[1]
    count_page = pages[154]
    affordability_page = pages[175]
    assert "TABLE A1.2" in count_page and "(millions)" in count_page
    assert "TABLE A1.6" in affordability_page and "2017" in affordability_page
    rows = []
    for country in COUNTRIES:
        rate_pdf_page = 140 if country == "India" else 141
        rate_page = pages[rate_pdf_page - 1]
        assert "TABLE A1.1" in rate_page and "2004–06" in rate_page
        rates = country_tokens(rate_page, country)[:2]
        counts = country_tokens(count_page, country)[:2]
        assert len(rates) == len(counts) == 2
        for index, period in enumerate(("2004-2006", "2022-2024")):
            year = period[-4:]
            row = base_row(country, year, rates[index], counts[index])
            row.update(
                indicator="prevalence_of_undernourishment",
                period=period,
                period_type="three_year_average",
                year_semantics="Period end used for indexing; not an annual point estimate",
                rate_locator=f"Table A1.1; {country}; {period}; PDF page {rate_pdf_page}; printed page {rate_pdf_page - 27}",
                count_locator=f"Table A1.2; {country}; {period}; PDF page 155; printed page 128; million persons",
                method="Extract paired published national percentage and affected count for the same three-year period and report vintage. Annex 1B PDF page 181/printed 154 defines the model using habitual dietary energy consumption below minimum dietary energy requirements. Annex table notes PDF149/printed122 specify three-year averages; 2022-2024 uses its three annual point estimates.",
                interpretation_limit="Modelled chronic dietary-energy insufficiency, not protein-specific deficiency, observed individual intake or a count to add to overlapping nutrition proxies.",
            )
            rows.append(row)
        tokens = country_tokens(affordability_page, country)
        assert len(tokens) == 10
        for index, year in enumerate(("2017", "2019", "2021", "2023", "2024")):
            row = base_row(country, year, tokens[index], tokens[index + 5])
            row.update(
                indicator="unable_to_afford_healthy_diet",
                period=year,
                period_type="annual_estimate",
                year_semantics="Annual reference year",
                rate_locator=f"Table A1.6; {country}; {year}; percentage column; PDF page 176; printed page 149",
                count_locator=f"Table A1.6; {country}; {year}; million persons column; PDF page 176; printed page 149",
                method="Extract paired published percentage and affected count for the same country/year and SOFI2025 vintage. Annex1B PDF189-191/printed162-164 compares income remaining after basic non-food needs with minimum healthy-diet cost; source calculates count using population from WPP2024. Retain source count rather than re-estimate using rounded rates.",
                interpretation_limit="Economic access to a healthy diet, not measured diet quality, nutrient intake, protein-specific deficiency or a count to add to overlapping nutrition proxies.",
            )
            rows.append(row)
    assert len(rows) == 14
    assert len({(r["country"], r["indicator"], r["period"]) for r in rows}) == len(rows)
    return rows


def write_provenance() -> None:
    """Stage source and raw-file registrations for coordinator integration."""
    original = RAW / "sofi-2025.pdf"
    access_day = (
        datetime.fromtimestamp(original.stat().st_mtime, UTC).date().isoformat()
    )
    write_csv(
        OUT / "source_rows.csv",
        [
            {
                "source_id": SOURCE,
                "title": "The State of Food Security and Nutrition in the World 2025 - Addressing high food price inflation for food security and nutrition",
                "publisher": "FAO, IFAD, UNICEF, WFP and WHO",
                "url": URL,
                "year": "2025",
                "accessed": access_day,
                "tier": "A",
                "access_method": "curl official FAO PDF; pdftotext layout extraction; Poppler table renders visually inspected",
                "license": LICENSE,
                "notes": "DOI10.4060/cd6008en. AnnexA1.1/A1.2/A1.6 India/Pakistan data retained in report2025 vintage, not mixed with later revisions. Underlying FAOSTAT FS/CAHD access date28July2025. Counts directly published in millions. Copyright page labels CC BY4.0 but includes additional restrictive prose; preserve printed terms rather than infer reuse scope.",
            }
        ],
    )
    manifest = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        if path.suffix == ".pdf":
            note = "Original official FAO-hosted CFS compiled report download; PDF includes cover material, so printed page differs from PDF page."
        elif path.suffix == ".txt":
            note = "DERIVED pdftotext -layout extraction; parent sofi-2025.pdf."
        else:
            note = "DERIVED Poppler page render; parent sofi-2025.pdf; PDF page encoded in filename."
        manifest.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": URL,
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, UTC
                ).isoformat(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "license": LICENSE,
                "source_id": SOURCE,
                "notes": note,
            }
        )
    write_csv(OUT / "manifest_rows.csv", manifest)


def main() -> None:
    """Write the bounded SOFI evidence handoff and check paired unit conversions."""
    rows = extract()
    write_csv(OUT / "extracted_rows.csv", rows)
    write_provenance()
    print(
        "PASS: 14 SOFI2025 proxy rows; four period-average PoU pairs and ten annual healthy-diet affordability pairs; direct counts scaled from millions; no denominator backsolving."
    )


if __name__ == "__main__":
    main()
