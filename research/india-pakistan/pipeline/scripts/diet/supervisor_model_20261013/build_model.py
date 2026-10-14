"""Recalculate conditional Table23 protein components without basket imputation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import NamedTuple

import xlrd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ANIMAL = {"beef", "mutton", "chicken_meat", "fish", "eggs"}
NATIVE_UNITS = {
    "kg/person/month": "Kg",
    "g/person/month": "Gm",
    "litre/person/month": "Ltr",
    "count/person/month": "No",
}
__all__ = [
    "ANIMAL",
    "build",
    "complete_sum",
    "daily_content",
    "equal_factor",
    "impute_within_group",
    "mass_factor",
]


class Factor(NamedTuple):
    """Carry the exact factor and the evidence needed to interpret it."""

    value: Fraction | None
    native_unit: str
    refs: str
    source_ids: str
    assumptions: str


def sha(path: Path) -> str:
    """Hash a local file without changing its contents."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read source precision as text rather than binary floating point."""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write a nonempty deterministic table with an explicit union schema."""
    fields = list(rows[0]) + sorted(
        set().union(*(r.keys() for r in rows)) - set(rows[0])
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decimal_text(value: Fraction | None) -> str:
    """Expose 12 decimals while preserving authoritative rational fields separately."""
    if value is None:
        return ""
    with localcontext() as context:
        context.prec = 50
        result = Decimal(value.numerator) / Decimal(value.denominator)
        return format(result.quantize(Decimal("0.000000000001")), "f")


def equal_factor(values: list[Fraction]) -> Fraction:
    """Average complete component products under an explicit equal-share scenario."""
    if not values:
        raise ValueError("A named nonempty component set is required")
    return sum(values, Fraction()) / len(values)


def mass_factor(
    protein_per_100g: Fraction,
    grams: Fraction,
    edible: Fraction,
    *,
    already_edible: bool = False,
) -> Fraction:
    """Convert native mass to protein, rejecting repeated edible adjustments."""
    if protein_per_100g < 0 or grams <= 0 or not 0 < edible <= 1:
        raise ValueError("Invalid physical composition or edible fraction")
    if already_edible and edible != 1:
        raise ValueError(
            "Already edible mass cannot receive another shell/refuse factor"
        )
    return protein_per_100g * grams * edible / 100


def daily_content(
    quantity: Fraction | None,
    quantity_unit: str,
    factor: Fraction | None,
    factor_native_unit: str,
    *,
    days: int = 30,
) -> Fraction | None:
    """Apply a matched physical factor once to a published monthly quantity."""
    if days != 30:
        raise ValueError(
            "Table23 is monthly; raw14day recalls must not be applied again"
        )
    if NATIVE_UNITS.get(quantity_unit) != factor_native_unit:
        raise ValueError("Quantity/factor native units differ")
    if quantity is None or factor is None:
        return None
    if quantity < 0 or factor < 0:
        raise ValueError("Negative physical quantity or protein factor")
    return quantity * factor / days


def complete_sum(values: list[Fraction | None]) -> Fraction | None:
    """Return missing whenever any required component is unresolved."""
    if not values or any(value is None for value in values):
        return None
    return sum((value for value in values if value is not None), Fraction())


def impute_within_group(
    expenditure: Fraction | None,
    target_group: str,
    donor_group: str,
    rupees_per_gram: Fraction | None,
    comparable_scope: bool,
) -> Fraction | None:
    """Reject cross-group transfer and preserve missing unsupported within-group data."""
    if not target_group or target_group != donor_group or donor_group == "whole_basket":
        raise ValueError("Protein costs require the same demonstrable food group")
    if expenditure is None or rupees_per_gram is None or not comparable_scope:
        return None
    if expenditure < 0 or rupees_per_gram <= 0:
        raise ValueError("Invalid expenditure or nutrient cost")
    return expenditure / rupees_per_gram


def verify_inputs() -> dict[str, dict[str, str | int]]:
    """Reject any change to source bytes or the frozen old model chain."""
    bindings = json.loads((HERE / "input-hashes.json").read_text())["files"]
    for relative, expected in bindings.items():
        path = ROOT / relative
        if sha(path) != expected["sha256"] or path.stat().st_size != expected["bytes"]:
            raise ValueError(f"Frozen input changed: {relative}")
    return bindings


def verify_factor_algebra(
    compiled: list[dict[str, str]],
    components: list[dict[str, str]],
    catalog: dict[str, dict[str, str]],
) -> None:
    """Recompute prior physical recipes independently before reusing their factors."""
    recipes: dict[str, Fraction] = defaultdict(Fraction)
    for row in components:
        protein = Fraction(row["protein_g_per_100g_edible"])
        if protein != Fraction(catalog["protein:" + row["protein_ref"]]["value"]):
            raise ValueError("Composition concentration differs from source catalog")
        if row["edible_ref"] == "zero_shortcut":
            if protein != 0:
                raise ValueError("Only a source-known zero can omit mass conversion")
            product = Fraction(0)
        else:
            product = (
                protein
                / 100
                * Fraction(row["grams_per_native_unit_before_edible"])
                * Fraction(row["edible_fraction"])
                * Fraction(row["transfer_fraction"])
            )
        if product != Fraction(
            int(row["component_factor_numerator"]),
            int(row["component_factor_denominator"]),
        ):
            raise ValueError("Physical component product does not reconcile")
        weighted = product * Fraction(
            int(row["weight_numerator"]), int(row["weight_denominator"])
        )
        if weighted != Fraction(
            int(row["weighted_factor_numerator"]),
            int(row["weighted_factor_denominator"]),
        ):
            raise ValueError("Weighted physical component does not reconcile")
        recipes[row["recipe_id"]] += weighted
    for row in compiled:
        if not row["protein_factor_numerator"]:
            continue
        exact = Fraction(
            int(row["protein_factor_numerator"]), int(row["protein_factor_denominator"])
        )
        if recipes[row["recipe_id"]] != exact:
            raise ValueError("Compiled factor differs from physical component sum")


def reconcile_quantities(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Compare all cached Table23 quantity cells and household sizes to the XLS."""
    book = xlrd.open_workbook(str(ROOT / "data/raw/regional/pakistan-hies-table23.xls"))
    sheet = book.sheet_by_name("Sheet1")
    if "2024-25" not in str(sheet.cell_value(1, 0)):
        raise ValueError("Table23 survey vintage changed")
    if len(rows) != 684 or len({(r["group"], r["food_group"]) for r in rows}) != 684:
        raise ValueError("Expected all38 foods in all18 published groups")
    for row in rows:
        if (
            row["source_id"] != "pakistan_hies_2024_25_table23"
            or row["period"] != "2024-25"
        ):
            raise ValueError("Source identity or survey period changed")
        match = re.match(r"Sheet1!([A-H])(\d+);", row["raw_locator"])
        if not match:
            raise ValueError("Missing Table23 source-cell address")
        column, line = ord(match[1]) - 65, int(match[2]) - 1
        if Fraction(str(sheet.cell_value(line, column))) != Fraction(row["value"]):
            raise ValueError(f"Quantity differs from source: {row['raw_locator']}")
        if str(sheet.cell_value(line, 1)).strip() != row["native_unit"]:
            raise ValueError("Table23 native unit changed")
    sizes = []
    for line in range(sheet.nrows):
        if str(sheet.cell_value(line, 0)).strip() == "PAKISTAN":
            header = line + 2
            if (
                str(sheet.cell_value(header, 0)).strip()
                != "Average No. of Members Per HH"
            ):
                raise ValueError("Household-size header moved")
            for column, group in enumerate(["all", "Q1", "Q2", "Q3", "Q4", "Q5"], 2):
                sizes.append(
                    {
                        "country": "Pakistan",
                        "residence": "all",
                        "quintile": group,
                        "mean_household_size": str(sheet.cell_value(header, column)),
                        "unit": "persons/household",
                        "source_id": "pakistan_hies_2024_25_table23",
                        "raw_locator": f"Sheet1!{chr(65 + column)}{header + 1}",
                        "interpretation": "Household-size context only; not an adult-equivalent conversion factor",
                    }
                )
            break
    if len(sizes) != 6:
        raise ValueError("National household sizes not found")
    return sizes


def scenarios() -> list[dict[str, str]]:
    """Declare interpretable one-factor changes and named joint form diagnostics."""
    base = {
        "scenario_id": "edible_flesh_us_large",
        "compiled": "baseline",
        "egg": "large",
        "cut": "identity",
        "fish": "six_edible",
        "beef": "equal",
        "mutton": "equal",
        "role": "comparable_conditional_components",
    }
    rows = [base]
    for size in ("small", "medium", "extra large", "jumbo"):
        rows.append(
            {
                **base,
                "scenario_id": "edible_flesh_us_" + size.replace(" ", "_"),
                "egg": size,
            }
        )
    for code in ("141", "145"):
        rows.append({**base, "scenario_id": "edible_beef_pk_" + code, "beef": code})
    for code in ("148", "152"):
        rows.append({**base, "scenario_id": "edible_mutton_pk_" + code, "mutton": code})
    for code in ("155", "156", "157", "158", "159", "160"):
        rows.append({**base, "scenario_id": "edible_fish_pk_" + code, "fish": code})
    for form in ("bd_rohu_boneless", "bd_rohu_river"):
        rows.append({**base, "scenario_id": form + "_us_large", "fish": form})
    for cut in ("bd_leg", "bd_breast"):
        rows.append({**base, "scenario_id": cut + "_us_large", "cut": cut})
    for size in ("small", "large", "jumbo"):
        rows.append(
            {
                **base,
                "scenario_id": "bd_cuts_rohu_us_" + size,
                "cut": "bd_leg",
                "fish": "bd_rohu_boneless",
                "egg": size,
            }
        )
    rows.append(
        {
            **base,
            "scenario_id": "species_milk_density_us_large",
            "compiled": "milk_species_density",
        }
    )
    for name in ("exact_food_forms", "domestic_single_positive"):
        rows.append(
            {
                **base,
                "scenario_id": name + "_coverage_only",
                "compiled": name,
                "role": "changed_coverage_diagnostic",
            }
        )
    rows.append(
        {
            **base,
            "scenario_id": "yogurt_included_held",
            "compiled": "yogurt_included_held",
            "role": "held_quantity_discrepancy",
        }
    )
    return rows


def fish_coefficients() -> dict[str, str]:
    """Read two visually reviewed Bangladesh source coefficients from saved text."""
    text = (
        ROOT
        / "scripts/diet/m3_food_crosswalk/supplement_regional_20261013/evidence/bangladesh-fct-2013.txt"
    ).read_text()
    page = text.split("\f")[121]
    values = {}
    for code, label in (
        ("09_0059", "Rohu, river, raw"),
        ("09_0060", "Rohu, without bones, raw"),
    ):
        line = next(
            line
            for line in page.splitlines()
            if line.startswith(code) and label in line
        )
        match = re.search(r"\s(0\.\d+)\s+\(\d+\)", line)
        if match is None:
            raise ValueError("Rohu edible coefficient not located in source table")
        values[code] = match[1]
    return values


def source_factor_catalog(
    catalog: dict[str, dict[str, str]],
    pk: dict[str, dict[str, str]],
    regional: dict[str, dict[str, str]],
    portions: dict[str, dict[str, str]],
    fish_edible: dict[str, str],
) -> dict[str, dict[str, str]]:
    """Expose every new or inherited factor through an exact primary-source locator."""
    result = {key: dict(value) for key, value in catalog.items()}
    for row in pk.values():
        if row["food_number"] not in {
            "141",
            "145",
            "146",
            "148",
            "152",
            "155",
            "156",
            "157",
            "158",
            "159",
            "160",
            "166",
        }:
            continue
        result[row["factor_id"]] = {
            "factor_id": row["factor_id"],
            "kind": "protein",
            "value": row["protein_g_per_100g_edible"],
            "unit": "g/100g edible",
            "description": row["food_name"],
            "source_id": row["source_id"],
            "source_tier": row["tier"],
            "raw_file": row["raw_file"],
            "raw_sha256": sha(ROOT / row["raw_file"]),
            "source_locator": row["raw_locator"],
            "evidence_kind": "PUBLISHED_VALUE_VISUALLY_RECHECKED",
            "underlying_reference": "Pakistan FCT2001; selected meat/fish/whole-chicken-egg rows",
        }
    for code in ("10_0002", "10_0006", "10_0007", "10_0011", "10_0012"):
        row = regional[code]
        factor_id = "edible:bd:" + code
        result[factor_id] = {
            "factor_id": factor_id,
            "kind": "edible",
            "value": row["edible_coefficient"],
            "unit": "edible g/as-purchased g",
            "description": row["food_name"],
            "source_id": row["source_id"],
            "source_tier": row["source_tier"],
            "raw_file": row["raw_file"],
            "raw_sha256": row["raw_sha256"],
            "source_locator": f"PDF{row['pdf_page']}/printed{row['printed_page']}; food{code}; edible portion coefficient",
            "evidence_kind": "PUBLISHED_VALUE_CONDITIONAL_CROSS_COUNTRY_TRANSFER",
            "underlying_reference": row["form_note"],
        }
    for row in portions.values():
        factor_id = "usda_portion:" + row["id"]
        result[factor_id] = {
            "factor_id": factor_id,
            "kind": "portion",
            "value": row["gram_weight"],
            "unit": "edible g/egg",
            "description": "US chicken egg " + row["modifier"],
            "source_id": row["source_id"],
            "source_tier": "A",
            "raw_file": "data/raw/diet/m3-usda-sr-legacy-2026-10-13/sr-legacy.zip",
            "raw_sha256": row["raw_sha256"],
            "source_locator": f"food_portion.csv record{row['csv_record']}; id{row['id']}; FDC{row['fdc_id']}; SR documentation PDF13/printed12 defines edible gram weights",
            "evidence_kind": "PUBLISHED_US_SIZE_NOT_PAKISTAN_MEAN",
            "underlying_reference": row["status"],
        }
    raw = "data/raw/diet/m3-infoods-2026-10-13/bangladesh-fct-2013.pdf"
    for code, value in fish_edible.items():
        factor_id = "edible:bd:" + code
        result[factor_id] = {
            "factor_id": factor_id,
            "kind": "edible",
            "value": value,
            "unit": "edible g/as-purchased g",
            "description": (
                "Rohu, without bones, raw" if code == "09_0060" else "Rohu, river, raw"
            ),
            "source_id": "bangladesh_fct_2013",
            "source_tier": "B",
            "raw_file": raw,
            "raw_sha256": sha(ROOT / raw),
            "source_locator": f"PDF122/printed97; Table1; food{code}; edible portion coefficient",
            "evidence_kind": "PUBLISHED_VALUE_VISUALLY_RECHECKED",
            "underlying_reference": "Named Bangladesh food-form coefficient, not a measured yield for the Pakistan fish basket",
        }
    return result


def animal_factor(
    food: str,
    scenario: dict[str, str],
    pk: dict[str, dict[str, str]],
    regional: dict[str, dict[str, str]],
    portions: dict[str, dict[str, str]],
    fish_edible: dict[str, str],
) -> Factor:
    """Calculate animal-food protein from named physical form and portion scenarios."""
    if scenario["role"] == "changed_coverage_diagnostic":
        return Factor(
            None,
            "No" if food == "eggs" else "Kg",
            "",
            "",
            "Old restricted pools do not resolve animal foods; preserve coverage gap",
        )
    codes = {
        "beef": ["141", "145"],
        "mutton": ["148", "152"],
        "chicken_meat": ["146"],
        "fish": ["155", "156", "157", "158", "159", "160"],
        "eggs": ["166"],
    }[food]
    if food in {"beef", "mutton"} and scenario[food] != "equal":
        codes = [scenario[food]]
    if food == "fish" and scenario["fish"].isdigit():
        codes = [scenario["fish"]]
    if food == "fish" and scenario["fish"].startswith("bd_rohu"):
        codes = ["155"]
    refs, sources, values = [], {"pakistan_food_composition_2001"}, []
    notes = [
        "Conditional food-form scenario; not observed edible mass, local species shares, total dietary intake or measured individual intake"
    ]
    for code in codes:
        concentration = Fraction(pk[code]["protein_g_per_100g_edible"])
        refs.append(pk[code]["factor_id"])
        edible = Fraction(1)
        grams = Fraction(1000)
        if food == "eggs":
            portion = portions[scenario["egg"]]
            grams = Fraction(portion["gram_weight"])
            refs.append("usda_portion:" + portion["id"])
            sources.update({portion["source_id"], "usda_sr_legacy_documentation_2018"})
            notes.append(
                f"US {scenario['egg']} chicken-egg edible portion; no second shell factor; not a Pakistan size distribution or duck-egg conversion"
            )
        elif scenario["cut"] != "identity" and food in {
            "chicken_meat",
            "mutton",
            "beef",
        }:
            bd_code = {
                "146": "10_0007" if scenario["cut"] == "bd_leg" else "10_0006",
                "148": "10_0011",
                "152": "10_0012",
                "141": "10_0002",
                "145": "10_0002",
            }[code]
            edible = Fraction(regional[bd_code]["edible_coefficient"])
            refs.append("edible:bd:" + bd_code)
            sources.add("bangladesh_fct_2013")
            notes.append(
                "Bangladesh edible coefficient for "
                + regional[bd_code]["food_name"]
                + "; proxy for the named Pakistan food, not live-animal yield; cattle coefficient applied to buffalo only as explicit boneless-flesh identity"
            )
        elif food == "fish" and scenario["fish"].startswith("bd_rohu"):
            bd_code = "09_0060" if scenario["fish"] == "bd_rohu_boneless" else "09_0059"
            edible = Fraction(fish_edible[bd_code])
            refs.append("edible:bd:" + bd_code)
            sources.add("bangladesh_fct_2013")
            notes.append(
                "Pakistan Roa/Labeo rohita concentration with Bangladesh named Rohu form coefficient; transfer diagnostic, not a generic whole-fish coefficient"
            )
        else:
            notes.append(
                "Reported kg treated as already edible flesh; explicitly excludes live-animal, bone/offal and dried/processed mixtures"
            )
        values.append(
            mass_factor(concentration, grams, edible, already_edible=food == "eggs")
        )
    if len(values) > 1:
        notes.append(
            "Equal shares across named components are a disclosed matching default, not observed local proportions"
        )
        sources.add("worldbank_adept_food_security_2014")
    return Factor(
        equal_factor(values),
        "No" if food == "eggs" else "Kg",
        ";".join(refs),
        ";".join(sorted(sources)),
        "; ".join(dict.fromkeys(notes)),
    )


def compiled_factor(
    food: str,
    scenario: dict[str, str],
    spec: dict[str, object],
    compiled: dict[tuple[str, str], dict[str, str]],
    catalog: dict[str, dict[str, str]],
) -> Factor:
    """Reuse only physical conversion recipes, never old pooled cost estimates."""
    mapping = spec["compiled_item_mapping"]
    if food == "yogurt_loose_packed" and scenario["compiled"] == "yogurt_included_held":
        codes = ["11408"]
    else:
        codes = mapping.get(food, [])
    if not codes:
        return Factor(None, "", "", "", spec["unresolved_items"][food])
    rows = [compiled[(scenario["compiled"], code)] for code in codes]
    refs = sorted(
        {ref for row in rows for ref in row["source_factor_refs"].split(";") if ref}
    )
    sources = {
        catalog[ref]["source_id"]
        for ref in refs
        if catalog[ref]["source_id"] != "dimensional_identity"
    }
    notes = [r["role_reason"] + " Assumptions: " + r["assumptions"] for r in rows]
    notes.append("Frozen physical factor only; all pooled cost calibration discarded")
    if any(not r["protein_factor_numerator"] or r["role"] != "G" for r in rows):
        return Factor(
            None,
            rows[0]["native_unit"],
            ";".join(refs),
            ";".join(sorted(sources)),
            "Unresolved/restricted factor in this coverage case. " + " ".join(notes),
        )
    native = {r["native_unit"] for r in rows}
    if len(native) != 1:
        raise ValueError("Composite Table23 item has incompatible native factors")
    values = [
        Fraction(
            int(r["protein_factor_numerator"]), int(r["protein_factor_denominator"])
        )
        for r in rows
    ]
    if len(values) > 1:
        sources.add("worldbank_adept_food_security_2014")
        notes.append(
            "Equal shares across the named questionnaire components; unknown survey shares remain an assumption"
        )
    return Factor(
        equal_factor(values),
        rows[0]["native_unit"],
        ";".join(refs),
        ";".join(sorted(sources)),
        " ".join(notes),
    )


def old_case_dispositions() -> list[dict[str, str]]:
    """Assess each old case rather than carrying old totals into the revision."""
    path = (
        ROOT
        / "scripts/diet/m3_calibration_estimates_20261013/experimental_group_estimates.csv"
    )
    rows = [r for r in read_csv(path) if r["reporting_level"] == "national"]
    output = []
    for row in rows:
        factor = row["factor_scenario"]
        if factor == "yogurt_included_held":
            action = "held_diagnostic_only"
            reason = "Physical recipe retained in separate held case; quantity discrepancy persists."
        elif factor in {"exact_food_forms", "domestic_single_positive"}:
            action = "rerun_as_coverage_diagnostic_only"
            reason = "Rerun restricted physical subset; the narrowed pool cannot impute other groups or yield total intake."
        else:
            action = "rerun_physical_factor_variant_only"
            reason = "Physical factor/portion/density route recomputed; old pooled-cost output withdrawn from current inference."
        output.append(
            {
                "old_factor_scenario": factor,
                "old_grouping_scenario": row["grouping_scenario"],
                "old_price_scenario": row["price_scenario"],
                "disposition": action,
                "reason": reason
                + " Official Table23 cells already define group means: microdata regrouping and CPI cost adjustments do not apply to these quantity cells. No old numeric total is reused.",
                "old_source_path": str(path.relative_to(ROOT)),
                "evidence_paths": "SPEC.json;scenario_summary.csv;food_coverage.csv",
                "old_total_used_in_revision": "false",
            }
        )
    if len(output) != 26:
        raise ValueError("Expected all26 historical national sensitivity cases")
    return output


def build(output: Path = HERE) -> dict[str, object]:
    """Create source-bound physical component tables and preserve unresolved totals."""
    bindings = verify_inputs()
    spec = json.loads((HERE / "SPEC.json").read_text())
    quantities = read_csv(ROOT / spec["quantity_dataset"])
    household_sizes = reconcile_quantities(quantities)
    pk = {
        r["food_number"]: r
        for r in read_csv(ROOT / "scripts/diet/pakistan_conversion_factors.csv")
    }
    regional = {
        r["food_code"]: r
        for r in read_csv(
            ROOT
            / "scripts/diet/m3_food_crosswalk/supplement_regional_20261013/regional_source_cells.csv"
        )
        if r["source_key"] == "bd"
    }
    portions = {
        r["modifier"]: r
        for r in read_csv(
            ROOT / "scripts/diet/m3_usda_supplement/portion_candidates.csv"
        )
        if r["fdc_id"] == "171287"
        and r["modifier"] in {"small", "medium", "large", "extra large", "jumbo"}
    }
    compiled = {
        (r["scenario"], r["itc"]): r
        for r in read_csv(
            ROOT / "scripts/diet/m3_calibration_spec/compiled_factors.csv"
        )
    }
    catalog = {
        r["factor_id"]: r
        for r in read_csv(ROOT / "scripts/diet/m3_calibration_spec/factor_catalog.csv")
    }
    verify_factor_algebra(
        list(compiled.values()),
        read_csv(ROOT / "scripts/diet/m3_calibration_spec/component_factors.csv"),
        catalog,
    )
    fish_edible = fish_coefficients()
    factor_catalog = source_factor_catalog(catalog, pk, regional, portions, fish_edible)
    source_ids = {r["source_id"] for r in read_csv(HERE / "source_snapshot.csv")}
    all_foods = {r["food_group"] for r in quantities}
    if (
        all_foods
        != set(spec["compiled_item_mapping"]) | set(spec["unresolved_items"]) | ANIMAL
    ):
        raise ValueError("Every Table23 food needs an explicit disposition")
    components, factors, summaries = [], [], []
    baseline_factors = {}
    range_values = defaultdict(list)
    for case in scenarios():
        food_factors = {}
        for food in sorted(all_foods):
            factor = (
                animal_factor(food, case, pk, regional, portions, fish_edible)
                if food in ANIMAL
                else compiled_factor(food, case, spec, compiled, catalog)
            )
            food_factors[food] = factor
            if any(
                sid not in source_ids for sid in factor.source_ids.split(";") if sid
            ):
                raise ValueError("Unregistered physical-factor source")
            if any(ref not in factor_catalog for ref in factor.refs.split(";") if ref):
                raise ValueError("Unresolved physical-factor locator")
            factors.append(
                {
                    "scenario_id": case["scenario_id"],
                    "food_group": food,
                    "factor_id": case["scenario_id"] + "__" + food,
                    "protein_g_per_native_unit": decimal_text(factor.value),
                    "factor_numerator": (
                        str(factor.value.numerator) if factor.value is not None else ""
                    ),
                    "factor_denominator": (
                        str(factor.value.denominator)
                        if factor.value is not None
                        else ""
                    ),
                    "native_unit": factor.native_unit,
                    "source_factor_refs": factor.refs,
                    "source_ids": factor.source_ids,
                    "tier": "derived",
                    "assumptions": factor.assumptions,
                    "prior_compiled_scenario": case["compiled"],
                    "old_cost_calibration_used": "false",
                }
            )
        if case["scenario_id"] == "edible_flesh_us_large":
            baseline_factors = food_factors
        grouped = defaultdict(list)
        for row in quantities:
            food = row["food_group"]
            factor = food_factors[food]
            value = daily_content(
                Fraction(row["value"]),
                row["unit"],
                factor.value,
                factor.native_unit or row["native_unit"],
            )
            record = {
                "country": "Pakistan",
                "group": row["group"],
                "residence": row["residence"],
                "quintile": row["quintile"],
                "period": row["period"],
                "food_group": food,
                "scenario_id": case["scenario_id"],
                "scenario_role": case["role"],
                "protein_g_person_day": decimal_text(value),
                "value_numerator": str(value.numerator) if value is not None else "",
                "value_denominator": (
                    str(value.denominator) if value is not None else ""
                ),
                "unit": "g/person/day",
                "quantity_value": row["value"],
                "quantity_unit": row["unit"],
                "quantity_locator": row["raw_locator"],
                "quantity_raw_file": row["raw_file"],
                "quantity_raw_sha256": row["raw_sha256"],
                "source_id": row["source_id"],
                "source_ids": ";".join(
                    sorted(
                        {
                            row["source_id"],
                            "pbs_hies_2024_25_manual",
                            *filter(None, factor.source_ids.split(";")),
                        }
                    )
                ),
                "factor_ids": case["scenario_id"] + "__" + food,
                "factor_evidence_file": "factor_evidence.csv",
                "tier": "derived",
                "conversion_status": (
                    "conditional_physical_conversion"
                    if value is not None
                    else "unresolved_missing"
                ),
                "imputation_method": "none",
                "method": "Monthly per-capita quantity times named physical factor divided by source-defined30days; exact rational arithmetic",
                "assumptions": factor.assumptions,
                "headline_eligible": "false",
                "residence_ranking_eligible": "false",
                "whole_diet_total_eligible": "false",
                "sample_size": row["sample_size"],
                "sample_basis": row["sample_basis"],
                "fieldwork_start": row["fieldwork_start"],
                "fieldwork_end": row["fieldwork_end"],
                "fieldwork_note": row["fieldwork_note"],
                "denominator": row["denominator"],
            }
            components.append(record)
            grouped[row["group"]].append((record, value))
        for group, items in sorted(grouped.items()):
            known = [value for _, value in items if value is not None]
            animal_values = [
                value for record, value in items if record["food_group"] in ANIMAL
            ]
            animal_total = complete_sum(animal_values)
            all_reported = complete_sum([value for _, value in items])
            if all_reported is not None:
                raise ValueError(
                    "Unexpected complete Table23 basket requires a new scope review"
                )
            subtotal = sum(known, Fraction())
            first = items[0][0]
            sources = sorted(
                {sid for record, _ in items for sid in record["source_ids"].split(";")}
            )
            summaries.append(
                {
                    "country": "Pakistan",
                    "group": group,
                    "residence": first["residence"],
                    "quintile": first["quintile"],
                    "scenario_id": case["scenario_id"],
                    "scenario_role": case["role"],
                    "matched_basket_subtotal_g_person_day": decimal_text(subtotal),
                    "subtotal_numerator": str(subtotal.numerator),
                    "subtotal_denominator": str(subtotal.denominator),
                    "five_animal_foods_subtotal_g_person_day": decimal_text(
                        animal_total
                    ),
                    "animal_numerator": (
                        str(animal_total.numerator) if animal_total is not None else ""
                    ),
                    "animal_denominator": (
                        str(animal_total.denominator)
                        if animal_total is not None
                        else ""
                    ),
                    "whole_diet_protein_g_person_day": "",
                    "unit": "g/person/day",
                    "n_table23_foods": str(len(items)),
                    "n_converted_foods": str(len(known)),
                    "unresolved_foods": ";".join(
                        sorted(
                            record["food_group"]
                            for record, value in items
                            if value is None
                        )
                    ),
                    "imputed_food_count": "0",
                    "source_id": spec["quantity_source_id"],
                    "source_ids": ";".join(sources),
                    "tier": "derived",
                    "headline_eligible": "false",
                    "residence_ranking_eligible": "false",
                    "whole_diet_total_eligible": "false",
                    "statistical_confidence_interval": "false",
                    "method": "Sum only converted physical components; named subset and assumptions retained. Unresolved contributions and complete total stay blank.",
                    "limitation": spec["whole_diet_total_reason"],
                }
            )
            if case["role"] == "comparable_conditional_components":
                range_values[(group, "matched_basket_subtotal")].append(
                    (subtotal, case["scenario_id"])
                )
                if animal_total is not None:
                    range_values[(group, "five_animal_foods_subtotal")].append(
                        (animal_total, case["scenario_id"])
                    )
    coverage = []
    quantity_by_food = {
        r["food_group"]: r for r in quantities if r["group"] == "all_all"
    }
    for food in sorted(all_foods):
        factor = baseline_factors[food]
        coverage.append(
            {
                "food_group": food,
                "source_label": quantity_by_food[food]["source_food_item"],
                "quantity_unit": quantity_by_food[food]["unit"],
                "quantity_locator": quantity_by_food[food]["raw_locator"],
                "physical_route": (
                    "conditional_named_factor"
                    if factor.value is not None
                    else "unresolved"
                ),
                "factor_refs": factor.refs,
                "source_ids": factor.source_ids,
                "within_group_imputation_eligible": "false",
                "imputation_reason": "Table23 has no compatible item/group expenditure and nutrient-cost donor, and known quantity alone cannot supply either; no cross-group fallback",
                "reason": factor.assumptions,
                "whole_diet_blocker": "Major-food list does not establish complete diet; unknown food forms and missing prepared-food quantities prevent complete total",
                "evidence_paths": "SPEC.json;scripts/diet/pakistan_conversion_mapping.csv;scripts/diet/m3_food_crosswalk/questionnaire_inventory.csv;data/raw/diet/pakistan-hies-2024-25-manual.pdf",
            }
        )
    ranges = []
    for (group, scope), values in sorted(range_values.items()):
        low, high = min(values), max(values)
        ranges.append(
            {
                "country": "Pakistan",
                "group": group,
                "scope": scope,
                "low": decimal_text(low[0]),
                "high": decimal_text(high[0]),
                "low_method": low[1],
                "high_method": high[1],
                "unit": "g/person/day",
                "low_numerator": str(low[0].numerator),
                "low_denominator": str(low[0].denominator),
                "high_numerator": str(high[0].numerator),
                "high_denominator": str(high[0].denominator),
                "n_enumerated_cases": str(len(values)),
                "whole_diet_total": "",
                "tier": "derived",
                "range_type": "enumerated_physical_method_diagnostic_not_confidence_or_identification_interval",
                "excluded_cases": "changed_coverage_diagnostic;held_quantity_discrepancy",
                "source_id": spec["quantity_source_id"],
                "source_ids": ";".join(
                    sorted(
                        {
                            sid
                            for row in summaries
                            if row["group"] == group
                            and row["scenario_role"]
                            == "comparable_conditional_components"
                            for sid in row["source_ids"].split(";")
                        }
                    )
                ),
                "headline_eligible": "false",
                "residence_ranking_eligible": "false",
                "limitation": "Not a whole-diet range or lower/upper bound on true intake. Enumerated assumptions do not exhaust species, processing, waste, allocation or measurement uncertainty.",
            }
        )
    dispositions = old_case_dispositions()
    output.mkdir(parents=True, exist_ok=True)
    tables = {
        "component_estimates.csv": components,
        "factor_evidence.csv": factors,
        "scenario_summary.csv": summaries,
        "method_ranges.csv": ranges,
        "food_coverage.csv": coverage,
        "household_size_context.csv": household_sizes,
        "old_sensitivity_disposition.csv": dispositions,
        "scenario_definitions.csv": scenarios(),
        "source_factor_catalog.csv": [
            factor_catalog[key] for key in sorted(factor_catalog)
        ],
    }
    for name, rows in tables.items():
        write_csv(output / name, rows)
    receipt = {
        "revision": spec["revision"],
        "quantity_rows_reconciled_to_xls": len(quantities),
        "table23_foods_covered": len(coverage),
        "physical_scenarios": len(scenarios()),
        "old_sensitivity_cases_disposed": len(dispositions),
        "imputation_performed": False,
        "whole_diet_total_available": False,
        "old_total_reused": False,
        "raw_and_prior_files_unchanged": True,
        "input_bindings": bindings,
        "outputs": {
            name: {"rows": len(rows), "sha256": sha(output / name)}
            for name, rows in tables.items()
        },
        "notes": "Implementation/source-byte checks passed; food-form choices remain conditional and human scholarly approval is pending.",
    }
    verify_inputs()
    (output / "integrity_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    return receipt


def main() -> None:
    """Run the isolated build and print only concise aggregate coverage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE)
    args = parser.parse_args()
    result = build(args.out)
    print(
        json.dumps(
            {
                key: result[key]
                for key in [
                    "quantity_rows_reconciled_to_xls",
                    "table23_foods_covered",
                    "physical_scenarios",
                    "old_sensitivity_cases_disposed",
                    "whole_diet_total_available",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
