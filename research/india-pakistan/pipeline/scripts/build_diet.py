"""Prepare M3 observed diet evidence without inventing protein factors or requirements."""

from __future__ import annotations

import re
from decimal import Decimal

from provenance import ROOT, read_csv, write_csv

__all__ = ["build", "india_rows"]
SOURCE = "mospi_nutrition_report_594_2025"
PDF = "data/raw/diet/india-nutritional-intake-report-594.pdf"
FOOD_GROUPS = [
    "cereals",
    "pulses",
    "milk_and_milk_products",
    "egg_fish_and_meat",
    "other_food",
]


def table_rows(page: str, expected: int, width: int) -> list[tuple[str, list[str]]]:
    """Read validated MPCE rows while guarding against a shifted source table."""
    matches = re.findall(r"^\s*(\d+-\d+%|All-India)\s+([\d.\s]+)$", page, re.MULTILINE)
    rows = [(group, text.split()) for group, text in matches]
    if len(rows) != expected or any(len(values) != width for _, values in rows):
        raise ValueError("Unexpected MoSPI table dimensions; inspect the PDF")
    return rows


def india_rows(
    intake_basis: str = "unadjusted_per_capita",
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Extract published food shares and protein under an explicit denominator."""
    if intake_basis not in {
        "unadjusted_per_capita",
        "unadjusted_per_consumer_unit",
    }:
        raise ValueError("Unknown intake basis")
    consumer_unit = intake_basis == "unadjusted_per_consumer_unit"
    pages = (
        (ROOT / "data/raw/diet/india-nutritional-intake-report-594.txt")
        .read_text()
        .split("\f")
    )
    samples = re.search(
        r"All – India\*\s+[\d,]+\s+[\d,]+\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)", pages[26]
    )
    if samples is None:
        raise ValueError("Household sample table not found")
    sector_samples = dict(
        zip(
            ["rural", "urban"],
            [v.replace(",", "") for v in samples.groups()[:2]],
            strict=True,
        )
    )

    def metadata(sector: str, fractile: str, locator: str) -> dict[str, str]:
        """Keep survey and subgroup denominators separate on every extracted figure."""
        return {
            "country": "India",
            "region": "India",
            "group": sector + "_MPCE_" + fractile,
            "year": "2024",
            "source_id": SOURCE,
            "residence": sector,
            "fractile": fractile,
            "period": "2023-24",
            "sample_size": "",
            "sample_basis": "Exact MPCE-cell analytical sample not stated in selected summary table.",
            "survey_sample_size": sector_samples[sector],
            "survey_sample_basis": "Surveyed sector households in Report594 Table1.2 PDF27/printed8; context only, not a cell-specific respondent count.",
            "sample_source_id": SOURCE,
            "denominator": "Per-person household-derived intake; MPCE population fractiles formed separately within rural and urban sectors.",
            "fieldwork_start": "2023-08",
            "fieldwork_end": "2024-07",
            "raw_file": PDF,
            "raw_locator": locator,
            "method": "Direct published value, unadjusted intake; no analyst imputation or conversion.",
            "notes": "All-India row is an overlapping sector total, not an additional fractile. Group averages are not individual deficiency prevalence.",
        }

    protein = []
    for fractile, values in table_rows(pages[56], 13, 8):
        columns = (
            (("rural", 6), ("urban", 7))
            if consumer_unit
            else (("rural", 2), ("urban", 3))
        )
        for sector, column in columns:
            row = metadata(
                sector,
                fractile,
                "Table3.9; PDFpage57/printed38; 2023-24 "
                + (
                    "per-consumer-unit columns8-9"
                    if consumer_unit
                    else "per-capita columns4-5"
                ),
            )
            row.update(
                intake_g=values[column],
                unit="g/consumer_unit/day" if consumer_unit else "g/person/day",
                intake_basis=intake_basis,
            )
            if consumer_unit:
                row.update(
                    tier="A",
                    denominator="Published household protein per energy-based consumer unit; MPCE population fractiles formed separately within rural and urban sectors.",
                    denominator_locator="Report594 Section2.9.5 PDFpage35/printed16 and Table2.1 PDFpage36/printed17",
                )
                row["notes"] += (
                    " A consumer unit is an energy-requirement scale referenced to a sedentary adult man aged 20-39 and weighing 60 kg, not a protein-requirement equivalence scale."
                    " Adult EAR/RDA comparisons therefore remain descriptive scenarios, not individual adequacy or deficiency prevalence."
                )
            protein.append(row)
    diet = []
    for index, (fractile, values) in enumerate(table_rows(pages[60], 26, 12)):
        sector = "rural" if index < 13 else "urban"
        shares = values[6:11]
        if Decimal(values[11]) != 100 or abs(
            sum(Decimal(value) for value in shares) - 100
        ) > Decimal("0.2"):
            raise ValueError(
                "Protein-source shares inconsistent with published rounding"
            )
        for food_group, value in zip(FOOD_GROUPS, shares, strict=True):
            row = metadata(
                sector, fractile, "Table3.11; PDFpage61/printed42; 2023-24 columns8-12"
            )
            row.update(
                food_group=food_group,
                metric="share_of_protein_intake",
                value=value,
                unit="percent_of_protein_intake",
            )
            row[
                "notes"
            ] += " These are protein shares, not mass, calorie or expenditure shares. Source rounding retained; not renormalized."
            diet.append(row)
    return diet, protein


def build() -> None:
    """Combine observed diet data; deliberately leave protein-gap estimation unfinished."""
    diet, protein = india_rows()
    _, consumer_unit_protein = india_rows("unadjusted_per_consumer_unit")
    pakistan = read_csv(ROOT / "scripts/diet/pakistan_diet_rows.csv")
    if not pakistan:
        raise ValueError("Pakistan diet staging is not ready")
    diet.extend(pakistan)
    mandatory = [
        "country",
        "region",
        "group",
        "year",
        "food_group",
        "metric",
        "value",
        "unit",
        "source_id",
    ]
    fields = mandatory + sorted(
        set().union(*(row.keys() for row in diet)) - set(mandatory)
    )
    source_ids = {
        row["source_id"] for row in read_csv(ROOT / "data/processed/sources.csv")
    }
    for row in diet + protein + consumer_unit_protein:
        if row["source_id"] not in source_ids:
            raise ValueError("Unregistered diet source")
    keys = [
        tuple(
            row[field]
            for field in (
                "country",
                "region",
                "group",
                "year",
                "food_group",
                "metric",
                "source_id",
            )
        )
        for row in diet
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate diet observation")
    write_csv(
        ROOT / "data/processed/diet_composition.csv",
        fields,
        [{field: row.get(field, "") for field in fields} for row in diet],
    )
    write_csv(
        ROOT / "data/processed/protein_intake_observed.csv", list(protein[0]), protein
    )
    write_csv(
        ROOT / "data/processed/protein_intake_consumer_unit.csv",
        list(consumer_unit_protein[0]),
        consumer_unit_protein,
    )
    print(
        f"Diet observations: {len(diet)}; India observed protein groups: {len(protein)}. Protein gaps not computed."
    )


if __name__ == "__main__":
    build()
