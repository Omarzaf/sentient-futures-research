"""Extract official Pakistan regional supplements with source-native definitions."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from provenance import (
    MANIFEST_FIELDS,
    ROOT,
    SOURCE_FIELDS,
    read_csv,
    write_csv,
)

STAGE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/regional/pakistan-supplement-2026-10-13"
NNS = ROOT / "data/raw/deficiency/anthropometry/pakistan-nns2018-volume1.txt"
HIES_ID = "pakistan_hies_2018_19_report"
ASP_ID = "pakistan_agricultural_statistics_2024_25"
NNS_ID = "pakistan_nns2018_volume1"
HIES_URL = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Hies18.pdf"
ASP_URL = "https://mnfsr.gov.pk/SiteImage/Publication/ASP%202024-25%20FINAL.pdf"
LICENSE = "Publicly accessible official report; redistribution rights not established."
BASE_FIELDS = list(read_csv(ROOT / "scripts/regional/extracted_rows.csv")[0])
EXTRA_FIELDS = [
    "source_region_label",
    "boundary_match_status",
    "boundary_match_note",
    "estimate_type",
    "source_year",
]


def row_base(source_id: str, region: str, residence: str, raw: Path) -> dict[str, str]:
    """Create a fully labelled row without inventing analytical sample counts."""
    row = dict.fromkeys(BASE_FIELDS + EXTRA_FIELDS, "")
    row.update(
        country="Pakistan",
        region=region,
        region_type="national" if region == "Pakistan" else "province",
        sex="all",
        age_group="all",
        residence=residence,
        quintile="all",
        source_id=source_id,
        sample_source_id=source_id,
        raw_file=str(raw.relative_to(ROOT)),
    )
    row["region_type"] = {
        "Islamabad Capital Territory": "federal_territory",
        "Azad Kashmir": "administrative_region",
        "Gilgit-Baltistan": "administrative_region",
        "KP-NMD": "survey_domain",
        "Northern Areas": "historical_region",
    }.get(region, row["region_type"])
    return row


def extract_hies() -> list[dict[str, str]]:
    """Read five foods across Table 23's 15 geography/residence blocks and six quintiles."""
    pages = (RAW / "hies-2018-19.txt").read_text().split("\f")
    regions = ["Pakistan", "Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan"]
    foods = {
        "Mutton": "mutton",
        "Beef": "beef",
        "Fish": "fish",
        "Chicken Meat": "chicken_meat",
        "Eggs": "eggs",
    }
    rows = []
    for offset in range(15):
        region, residence = regions[offset // 3], ["all", "urban", "rural"][offset % 3]
        page, sample_page = 352 + offset, 45 + offset
        text, sample_text = pages[page - 1], pages[sample_page - 1]
        geography = (
            "KP"
            if region == "Khyber Pakhtunkhwa" and residence != "all"
            else region.upper()
        ) + (" " + residence.upper() if residence != "all" else "")
        assert geography in text and geography in sample_text
        sample_line = next(
            line
            for line in sample_text.splitlines()
            if line.startswith("No. of Sample Households")
        )
        samples = re.findall(r"\d+", sample_line)
        assert len(samples) == 6 and int(samples[0]) == sum(map(int, samples[1:]))
        for food, identifier in foods.items():
            line = next(
                line
                for line in text.splitlines()
                if re.match(rf"^{food}\s+(?:Kg|No)\s", line, re.IGNORECASE)
            )
            values = re.findall(r"\d+\.\d+", line)
            assert len(values) == 6
            for column, value in enumerate(values):
                row = row_base(HIES_ID, region, residence, RAW / "hies-2018-19.pdf")
                row.update(
                    year="2019",
                    period="2018-19",
                    source_year="2020",
                    indicator=f"monthly_per_capita_{identifier}_consumption",
                    value=value,
                    display_value=value,
                    unit="count/person/month" if food == "Eggs" else "kg/person/month",
                    quintile=["all", "Q1", "Q2", "Q3", "Q4", "Q5"][column],
                    sample_basis="Table 23 does not restate an analytical sample; Table 1 households are context only.",
                    survey_sample_size=samples[column],
                    survey_sample_basis="Published surveyed-household count in Table 1 for the same region/residence/quintile; not a person denominator.",
                    denominator="Per household member per month in the stated geography, residence and consumption-expenditure quintile.",
                    fieldwork_start="2018-08",
                    fieldwork_end="2019-06",
                    fieldwork_note="Report introduction: August 2018 through June 2019; month precision.",
                    method="Direct extraction of Table 23 published two-decimal quantities; no interpolation, protein conversion or re-estimation.",
                    raw_locator=f"Table 23; PDF page {page}; {geography}; {food}; column {column+2}",
                    sample_locator=f"Table 1; PDF page {sample_page}; No. of Sample Households; column {column+2}",
                    notes="Survey quantities are not retail sales or individual protein intake. Published rounded zero is retained, not interpreted as no consumption. Survey universe includes ICT and erstwhile FATA, excludes military restricted areas; see section 1.5. Do not merge with revised 2024-25 XLS vintage.",
                    source_region_label=geography,
                    estimate_type="published_household_survey_quantity",
                )
                rows.append(row)
    assert len(rows) == 450
    assert (
        next(
            r["value"]
            for r in rows
            if r["region"] == "Pakistan"
            and r["residence"] == "all"
            and r["quintile"] == "all"
            and r["indicator"].endswith("chicken_meat_consumption")
        )
        == "0.36"
    )
    return rows


def extract_nns() -> list[dict[str, str]]:
    """Read Table 6-28 by individual column labels, preserving KP/KP-NMD separation."""
    pages = NNS.read_text().split("\f")
    blocks = [(224, pages[223]), (225, pages[224].split("\n          Education")[0])]
    cells = []
    for page, text in blocks:
        for line in text.splitlines():
            if re.search(r"(?:Total|Urban|Rural)\s+\d", line):
                values = re.findall(r"(?<![\w-])\d+(?:\.\d+)?", line)
                if len(values) == 13:
                    cells.append((page, values))
    geography = [
        ("Pakistan", r, "Total" if r == "all" else r.title())
        for r in ["all", "urban", "rural"]
    ]
    for region, label in [
        ("Punjab", "Punjab"),
        ("Sindh", "Sindh"),
        ("Khyber Pakhtunkhwa", "KP"),
        ("Balochistan", "Balochistan"),
        ("Islamabad Capital Territory", "ICT"),
    ]:
        geography.extend((region, r, label) for r in ["urban", "rural", "all"])
    geography.append(("KP-NMD", "all", "KP-NMD"))
    for region, label in [("Azad Kashmir", "AJK"), ("Gilgit-Baltistan", "GB")]:
        geography.extend((region, r, label) for r in ["urban", "rural", "all"])
    assert len(cells) == len(geography) == 25
    indicators = [
        (0, "minimum_dietary_diversity"),
        (2, "grains_previous_day"),
        (3, "pulses_previous_day"),
        (4, "nuts_seeds_previous_day"),
        (5, "dairy_previous_day"),
        (6, "meat_fish_poultry_previous_day"),
        (7, "eggs_previous_day"),
        (8, "dark_green_leafy_vegetables_previous_day"),
        (9, "vitamin_a_fruit_vegetables_previous_day"),
        (10, "other_vegetables_previous_day"),
        (11, "other_fruits_previous_day"),
    ]
    rows = []
    for (page, values), (region, residence, label) in zip(
        cells, geography, strict=True
    ):
        for column, indicator in indicators:
            row = row_base(NNS_ID, region, residence, NNS.with_suffix(".pdf"))
            row.update(
                year="2018",
                period="2018-19 fieldwork; NNS 2018",
                source_year="2020",
                indicator="women_15_49_" + indicator,
                value=values[column],
                display_value=values[column],
                unit="percent",
                sex="women",
                age_group="15-49",
                sample_size=values[-1],
                sample_basis="Published Number of women in Table 6-28 for the stated geography/residence; table does not label this column weighted or unweighted.",
                denominator="Women aged 15-49; previous day/night food-group consumption. MDD is at least five of ten groups; group-specific percentages are not nutrient adequacy.",
                fieldwork_start="2018-04",
                fieldwork_end="2019-01",
                fieldwork_note="Overall survey fieldwork per section 2.4.7; no region-specific months inferred.",
                method="Direct published percentages by individual food-group labels. Ignore the source table's inverted overarching group headers; mean/SD column is not extracted.",
                raw_locator=f"Table 6-28; printed/PDF page {page}; {label}; {residence}; {indicator}",
                sample_locator=f"Table 6-28; printed/PDF page {page}; {label}; {residence}; Number of women",
                notes="Food-group prevalence is not grams, protein intake or protein-deficiency prevalence. The source's overarching Animal-source foods and Grain/pulses/nuts headers appear reversed; individual Grains/Pulses/Nuts/Dairy/Meat/Eggs labels are used. KP and KP-NMD are separate survey domains.",
                source_region_label=label,
                estimate_type="published_dietary_diversity_survey",
            )
            if region in ["KP-NMD", "Khyber Pakhtunkhwa"]:
                row.update(
                    boundary_match_status="unmapped_scope_mismatch",
                    boundary_match_note="NNS separately reports KP and KP-NMD; available ADM1 Khyber Pakhtunkhwa combines these domains. No aggregation or map assignment is justified.",
                )
            rows.append(row)
    assert len(rows) == 275
    assert (
        sum(
            int(values[-1])
            for (_, values), (region, residence, _) in zip(
                cells, geography, strict=True
            )
            if region != "Pakistan" and residence == "all"
        )
        == 86629
    )
    return rows


def extract_asp() -> list[dict[str, str]]:
    """Read livestock stocks as official intercensal estimates, never meat production."""
    pages = (RAW / "asp-2024-25.txt").read_text().split("\f")
    geography = {
        "Pakistan": "Pakistan",
        "Punjab": "Punjab",
        "Sindh": "Sindh",
        "KPK": "Khyber Pakhtunkhwa",
        "Balochistan": "Balochistan",
        "Nothern Areas": "Northern Areas",
        "AJK": "Azad Kashmir",
    }
    rows = []
    region = label = ""
    for page in [201, 202]:
        for line in pages[page - 1].splitlines():
            stripped = line.strip()
            if stripped in geography:
                label, region = stripped, geography[stripped]
            match = re.match(
                r"^\s*(Cattle|Buffaloes|Sheep|Goats|Camels|(?:Domestic )?Poultry)\s+(.+)$",
                line,
            )
            if not match:
                continue
            assert region
            animal = match[1]
            values = match[2].split()
            assert len(values) == 7
            for index, value in enumerate(values[-5:]):
                year = 2021 + index
                row = row_base(ASP_ID, region, "all", RAW / "asp-2024-25.pdf")
                row.update(
                    year=str(year),
                    period=f"{year-1}-{str(year)[2:]}",
                    source_year="2026",
                    indicator="livestock_population_"
                    + animal.lower().replace(" ", "_"),
                    value=value,
                    display_value=value,
                    unit="thousand_head",
                    sample_basis="Not a sampled-person statistic; published official intercensal estimate.",
                    denominator="Number of animals in the source geography; not food quantity, sales, slaughter or meat production.",
                    fieldwork_note="No current fieldwork inferred. Table footnote bases estimates on 1996/2006 intercensus growth rates.",
                    method="Direct Table 120 official estimate. Preserve thousand-head units and published precision; no AI estimate or own projection.",
                    raw_locator=f"Table 120; printed/PDF page {page}; {label}; {animal}; {year-1}-{str(year)[2:]}",
                    sample_locator="Table 120 notes; printed/PDF page 202",
                    notes="Stock context only. Source national totals exclude Northern Areas and AJK. Poultry scope is not established as all commercial birds; AJK explicitly says Domestic Poultry and remains a separate indicator. Source notes use 1996/2006 growth, not a current livestock census. No livestock-to-meat conversion.",
                    source_region_label=label,
                    estimate_type="official_intercensal_livestock_estimate",
                )
                if region in ["Khyber Pakhtunkhwa", "Northern Areas"]:
                    row.update(
                        boundary_match_status="unmapped_scope_unverified",
                        boundary_match_note="Source uses historical census domains (KPK/Northern Areas); alignment with current combined ADM1 geography is not established.",
                    )
                if animal == "Poultry" and year in [2021, 2022]:
                    row[
                        "notes"
                    ] += " Source nonreconciliation: published Pakistan poultry is 96195 versus four-province sum 91220 in 2020-21, and 97615 versus 92616 in 2021-22 (thousand head). Both source levels retained; no corrected national total inferred."
                rows.append(row)
    assert len(rows) == 210
    return rows


def build() -> None:
    """Write a reviewable staging batch and provenance, leaving shared files unchanged."""
    rows = extract_hies() + extract_nns() + extract_asp()
    write_csv(STAGE / "extracted_rows.csv", BASE_FIELDS + EXTRA_FIELDS, rows)
    known = {r["source_id"]: r for r in read_csv(ROOT / "data/processed/sources.csv")}
    sources = [known[NNS_ID]]
    for identifier, title, publisher, url, year, note in [
        (
            HIES_ID,
            "Household Integrated Economic Survey 2018-19",
            "Pakistan Bureau of Statistics",
            HIES_URL,
            "2020",
            "Table 23 exact survey-vintage food quantities; Table 1 household counts are contextual, not analytical person denominators. Includes erstwhile FATA per section 1.5.",
        ),
        (
            ASP_ID,
            "Agricultural Statistics of Pakistan 2024-25",
            "Ministry of National Food Security and Research, Government of Pakistan",
            ASP_URL,
            "2026",
            "Official catalog labels 2024-25; foreword on PDF page 4 is dated June 2026. Table 120 stocks estimated from 1996/2006 intercensus growth; excludes Northern Areas/AJK from national totals. PDF table index page numbers differ from printed pages. National meat production differs between tables 123 and 169; not harmonized or imported here.",
        ),
    ]:
        sources.append(
            dict(
                zip(
                    SOURCE_FIELDS,
                    [
                        identifier,
                        title,
                        publisher,
                        url,
                        year,
                        "2026-10-13",
                        "A",
                        "Official public PDF retrieved with curl; pdftotext layout and visually reviewed table renders",
                        LICENSE,
                        note,
                    ],
                    strict=True,
                )
            )
        )
    write_csv(STAGE / "source_rows.csv", SOURCE_FIELDS, sources)
    manifest = []
    for path in sorted(RAW.iterdir()):
        if path.name.startswith("nns-"):
            identifier, url = NNS_ID, known[NNS_ID]["url"]
        elif path.name.startswith("hies-"):
            identifier, url = HIES_ID, HIES_URL
        else:
            identifier, url = ASP_ID, (
                "https://mnfsr.gov.pk/" if path.name.startswith("mnfsr-") else ASP_URL
            )
        manifest.append(
            dict(
                zip(
                    MANIFEST_FIELDS,
                    [
                        str(path.relative_to(ROOT)),
                        url,
                        datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(
                            timespec="seconds"
                        ),
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        LICENSE,
                        identifier,
                        "Source PDF/HTTP receipt or locally derived text/table render; byte-preserving raw artifact. NNS page 226 is adjacent context only; no observations extracted.",
                    ],
                    strict=True,
                )
            )
        )
    write_csv(STAGE / "manifest_rows.csv", MANIFEST_FIELDS, manifest)
    (STAGE / "validation.json").write_text(
        json.dumps(
            {
                "rows": len(rows),
                "hies": 450,
                "nns": 275,
                "livestock_stock_context": 210,
                "source_cells_not_estimates_by_ai": True,
                "hies_national_chicken_kg_person_month": "0.36",
                "nns_region_total_women_reconcile": 86629,
                "unmapped_rows": sum(bool(r["boundary_match_status"]) for r in rows),
                "limits": [
                    "Sample counts remain distinct from person denominators",
                    "NNS inconsistent overarching headers ignored in favor of individual labels",
                    "Historical geography withheld from current map where alignment unresolved",
                    "Livestock stock is not regional meat production",
                    "ASP national poultry differs from the sum of four published provinces in 2020-21 and 2021-22; neither level adjusted",
                    "ASP foreword PDF page 4 verifies June 2026 publication; observations preserve 2020-21 through 2024-25 periods",
                ],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Staged {len(rows)} Pakistan rows and {len(manifest)} raw receipts.")


if __name__ == "__main__":
    build()
