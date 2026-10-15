"""Audit HIES-to-composition candidates and compute explicitly conditional components."""

from __future__ import annotations

import csv
import hashlib
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FACTOR_SOURCE = "pakistan_food_composition_2001"
QUANTITY_SOURCE = "pakistan_hies_2024_25_table23"
RAW = ROOT / "data/raw/composition/pakistan-food-composition-2001.pdf"

# Candidate IDs are evidence locators, not accepted mappings or mixture weights.
MAPPING: dict[str, tuple[str, str, str]] = {
    "wheat_and_wheat_flour": (
        "15;16;17",
        "mixture_unresolved",
        "Wheat grain versus whole/refined/granular flour proportions and milling basis are unknown.",
    ),
    "rice_and_rice_flour": (
        "8;9",
        "mixture_unresolved",
        "Rice variety, flour share and raw/cooked reporting state are unknown; cooked factor is diagnostic only.",
    ),
    "biscuit": (
        "23",
        "product_unresolved",
        "Generic biscuits are not necessarily the sampled wheat-flour biscuit; product mixture is unknown.",
    ),
    "gram_whole": (
        "26;27",
        "conditional_component_only",
        "Whole gram is matched to chickpea; raw versus cooked edible mass is not established by Table 23.",
    ),
    "gram_split": (
        "26;27",
        "product_unresolved",
        "Whole chickpea entries do not establish dehulled split-gram composition or milling yield.",
    ),
    "mash": (
        "36;37",
        "conditional_component_only",
        "Raw versus cooked edible mass and whole/dehulled state are not established by Table 23.",
    ),
    "moong": (
        "34;35",
        "conditional_component_only",
        "Raw versus cooked edible mass and whole/dehulled state are not established by Table 23.",
    ),
    "masoor": (
        "32;33",
        "conditional_component_only",
        "Raw versus cooked edible mass and whole/dehulled state are not established by Table 23.",
    ),
    "other_pulses": (
        "",
        "mixture_unresolved",
        "Residual pulse species, processing states and weights are unknown; no arbitrary mean is valid.",
    ),
    "milk_fresh_and_boiled": (
        "133;134;135",
        "density_and_mixture_unresolved",
        "Litres require density; cow/buffalo/goat shares, boiling concentration and nondairy inclusion are unknown.",
    ),
    "milk_packed_excluding_tea_whitener": (
        "133;134;135",
        "density_and_product_unresolved",
        "Litres require density; milk species, fat level, processing and product identity are unknown.",
    ),
    "milk_dry": (
        "137;138",
        "mixture_unresolved",
        "Skimmed versus whole powder proportions are unknown.",
    ),
    "milk_dry_children": (
        "",
        "product_unresolved",
        "Infant/child formula products cannot be mapped to generic dried cow milk without composition evidence.",
    ),
    "butter": (
        "172",
        "mixture_unresolved",
        "Workbook footnote includes margarine; the pure-butter factor is not valid for the unidentified mixture.",
    ),
    "ghee_desi": (
        "173;174",
        "mixture_unresolved",
        "Ghee and buffalo-ghee factors differ; species and processing mixture are unknown.",
    ),
    "yogurt_loose_packed": (
        "130;139",
        "mixture_unresolved",
        "Curd/dahi versus yogurt and sweetened/flavoured/other product shares are unknown.",
    ),
    "vegetable_ghee": (
        "176",
        "product_unresolved",
        "The named Dalda hydrogenated-oil entry does not prove every reported vegetable-ghee product has that composition.",
    ),
    "cooking_oil": (
        "177;178;179;180;181;182;183;184",
        "density_and_mixture_unresolved",
        "Oil type/density and mixture are unknown; sesame-oil factor is nonzero, so zero protein for all oils is not imposed.",
    ),
    "mutton": (
        "148;152",
        "edible_fraction_and_mixture_unresolved",
        "Goat/sheep mixture, cut/offal/preparation mix, bone/refuse and edible weight are unknown.",
    ),
    "beef": (
        "141;145",
        "edible_fraction_and_mixture_unresolved",
        "Cattle/buffalo mixture, cut/offal/preparation mix, bone/refuse and edible weight are unknown.",
    ),
    "fish": (
        "155;156;157;158;159;160",
        "edible_fraction_and_mixture_unresolved",
        "Species/seafood/processed shares, bone/refuse and edible weight are unknown; candidates are not exhaustive.",
    ),
    "chicken_meat": (
        "146",
        "edible_fraction_unresolved",
        "Chicken species name alone does not resolve cut/offal/preparation mix or bone/refuse and edible weight.",
    ),
    "eggs": (
        "166;167;170",
        "portion_and_mixture_unresolved",
        "Count requires edible grams per egg; species, size and preparation are unknown.",
    ),
    "banana": (
        "85",
        "portion_unresolved",
        "Count requires a measured or sourced edible portion per banana; size distribution is unknown.",
    ),
    "citrus_fruit_mossaumi_etc": (
        "97;103;104;105",
        "portion_and_mixture_unresolved",
        "Count requires edible mass; citrus variety and size distribution are unknown.",
    ),
    "apple": (
        "83",
        "edible_fraction_unresolved",
        "Table 23 does not establish edible mass after core/refuse or preparation state.",
    ),
    "other_fruit": (
        "",
        "mixture_unresolved",
        "Residual species, preparation, refuse and mixture weights are unknown.",
    ),
    "dry_fruits": (
        "",
        "mixture_unresolved",
        "Nuts/dried-fruit species, shell/refuse and mixture weights are unknown.",
    ),
    "potato": (
        "71",
        "edible_fraction_unresolved",
        "Peel/refuse and fresh versus processed/prepared mass are not established.",
    ),
    "tomato": (
        "63",
        "edible_fraction_unresolved",
        "Fresh versus processed/prepared mass and edible/refuse basis are not established.",
    ),
    "onion": (
        "70",
        "edible_fraction_unresolved",
        "Peel/refuse and fresh versus processed/prepared mass are not established.",
    ),
    "other_vegetables": (
        "",
        "mixture_unresolved",
        "Residual species, preparation, refuse and mixture weights are unknown.",
    ),
    "salt": (
        "",
        "factor_missing",
        "No salt factor was located in the inspected FCT pages; missing is not zero.",
    ),
    "chillies": (
        "59;60",
        "product_unresolved",
        "Fresh-pepper factors are not valid for dried chillies/powder; water content and product state are unknown.",
    ),
    "sugar_desi_and_milled": (
        "185;186",
        "product_unresolved",
        "White/brown sugars have reported zero protein, but equivalence to all desi/milled products has not been established.",
    ),
    "honey": (
        "188",
        "candidate_not_applied",
        "Named honey factor is available; Table 23 product identity/edible reporting basis still requires confirmation.",
    ),
    "gur_and_shakkar": (
        "187",
        "mixture_unresolved",
        "A gur factor does not establish the gur/shakkar mixture composition.",
    ),
    "tea_black_and_green": (
        "197;198",
        "infusion_and_mixture_unresolved",
        "Dry-leaf protein is not consumed infusion protein; steeping extraction and black/green proportions are unknown.",
    ),
}
SCENARIO_FACTORS = {"gram_whole": "26", "mash": "36", "moong": "34", "masoor": "32"}


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read CSV rows without changing source precision."""
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write nonempty records using their explicit column order."""
    assert rows
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Create full mapping audit and isolated raw-edible-legume scenarios."""
    factors = read_csv(OUT / "pakistan_conversion_factors.csv")
    by_number = {row["food_number"]: row for row in factors}
    assert len(by_number) == len(factors) == 64
    assert all(
        row["source_id"] == FACTOR_SOURCE and row["tier"] == "A" for row in factors
    )
    assert all(Decimal(row["protein_g_per_100g_edible"]) >= 0 for row in factors)
    quantities = read_csv(OUT / "pakistan_diet_rows.csv")
    first_group = [row for row in quantities if row["group"] == "all_all"]
    assert set(MAPPING) == {row["food_group"] for row in first_group}
    raw_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    mappings = []
    for row in first_group:
        candidates, status, gap = MAPPING[row["food_group"]]
        numbers = candidates.split(";") if candidates else []
        assert all(number in by_number for number in numbers)
        mappings.append(
            {
                "food_group": row["food_group"],
                "source_food_item": row["source_food_item"],
                "quantity_unit": row["unit"],
                "source_id": QUANTITY_SOURCE,
                "composition_source_id": FACTOR_SOURCE,
                "composition_tier": "A",
                "candidate_factor_ids": ";".join(
                    by_number[number]["factor_id"] for number in numbers
                ),
                "mapping_status": status,
                "mapping_gap": gap,
                "accepted_for_total_intake": "false",
                "quantity_locator": row["raw_locator"],
                "composition_raw_sha256": raw_hash,
            }
        )
    components = []
    for row in quantities:
        number = SCENARIO_FACTORS.get(row["food_group"])
        if number is None:
            continue
        assert row["unit"] == "kg/person/month" and row["source_id"] == QUANTITY_SOURCE
        factor = by_number[number]
        value = (
            Decimal(row["value"])
            * Decimal(1000)
            * Decimal(factor["protein_g_per_100g_edible"])
            / Decimal(100)
        )
        components.append(
            {
                "country": row["country"],
                "region": row["region"],
                "group": row["group"],
                "year": row["year"],
                "residence": row["residence"],
                "quintile": row["quintile"],
                "food_group": row["food_group"],
                "metric": "conditional_raw_edible_legume_protein_content",
                "value": str(value),
                "unit": "g/person/month",
                "source_id": QUANTITY_SOURCE,
                "composition_source_id": FACTOR_SOURCE,
                "composition_factor_id": factor["factor_id"],
                "quantity_value": row["value"],
                "quantity_unit": row["unit"],
                "protein_g_per_100g_edible": factor["protein_g_per_100g_edible"],
                "quantity_locator": row["raw_locator"],
                "composition_locator": factor["raw_locator"],
                "quantity_raw_sha256": row["raw_sha256"],
                "composition_raw_sha256": raw_hash,
                "sample_size": row["sample_size"],
                "sample_basis": row["sample_basis"],
                "survey_sample_size": row["survey_sample_size"],
                "survey_sample_basis": row["survey_sample_basis"],
                "sample_source_id": row["sample_source_id"],
                "sample_locator": row["sample_locator"],
                "denominator": row["denominator"],
                "fieldwork_start": row["fieldwork_start"],
                "fieldwork_end": row["fieldwork_end"],
                "fieldwork_note": row["fieldwork_note"],
                "method": "Conditional scenario only: quantity_kg_per_person_month * 1000 g/kg * FCT_crude_protein_g_per_100g / 100. Assumes the reported quantity is raw edible legume mass matching the named FCT item. No mixture weights, portion weights, edible fractions or daily denominator are imputed.",
                "interpretation": "Protein content of one reported component under an unverified raw-edible assumption. Not observed protein intake, total dietary protein, a lower bound, an adequacy gap or deficiency prevalence. Do not sum into protein_gap.csv.",
                "status": "conditional_scenario_not_accepted_for_total_intake",
                "unresolved_assumption": MAPPING[row["food_group"]][2],
            }
        )
    assert len(mappings) == 38 and len(components) == 72
    assert len({(row["group"], row["food_group"]) for row in components}) == len(
        components
    )
    assert {row["group"] for row in components} == {row["group"] for row in quantities}
    return mappings, components


def main() -> None:
    """Persist auditable intermediate evidence without writing processed totals."""
    mappings, components = build()
    write_csv(OUT / "pakistan_conversion_mapping.csv", mappings)
    write_csv(OUT / "pakistan_conversion_components.csv", components)
    print(
        "PASS: 64 source factors; 38 HIES items audited; 72 conditional monthly component calculations; zero total-intake or gap estimates."
    )


if __name__ == "__main__":
    main()
