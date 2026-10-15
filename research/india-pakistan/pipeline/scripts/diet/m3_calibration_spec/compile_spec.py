"""Compile source-bound protein factors without reading survey household data."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = ROOT / "scripts/diet/m3_food_crosswalk"
REGIONAL = CORE / "supplement_regional_20261013"
USDA = ROOT / "scripts/diet/m3_usda_supplement"
CHANNELS = "q1/v1 paid;q2/v2 wages in kind;q3/v3 own produce;q4/v4 gifts"
FROZEN = [CORE / "handoff_hashes.json", REGIONAL / "handoff_hashes.json"]
METHODS = {
    "usda_sr_legacy_documentation_2018": (
        "data/raw/diet/m3-usda-sr-legacy-2026-10-13/sr-legacy-documentation.pdf",
        "fdc33442adb5707d448676e92b54f9adeaad63b6df267b683b5fe728307391cf",
    ),
    "worldbank_adept_food_security_2014": (
        "data/raw/diet/m3-method-followup-2026-10-13/worldbank-adept-2014.pdf",
        "90f79aa073b94abcf5b23fcbd72954b7463aaa625359912c2e2ae475cc246c27",
    ),
    "fao_hces_technical_notes": (
        "data/raw/diet/m3-infoods-2026-10-13/hces-technical-notes.pdf",
        "c5b138f6cfc8a6bb717838fb262e703f9742272c223190bf6f0082c88124ca8e",
    ),
    "fao_infoods_food_matching_v1_2_2012": (
        "data/raw/diet/m3-infoods-2026-10-13/food-matching-v1-2.pdf",
        "7f51ddf38e3201cc3365ebf98744b41bb53b99215b72d10e746911c91b6286ce",
    ),
}


def sha(path: Path) -> str:
    """Hash a named local source or output."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Read a small source table without coercing identifiers or missing cells."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter=delimiter))
    assert rows and all(None not in r and None not in r.values() for r in rows), path
    return rows


def write_rows(name: str, rows: list[dict[str, str]]) -> None:
    """Write a deterministic local CSV."""
    with (HERE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def decimal_text(value: Fraction) -> str:
    """Display up to twelve decimals while retaining exact rational fields separately."""
    with localcontext() as context:
        context.prec = 40
        number = Decimal(value.numerator) / Decimal(value.denominator)
        result = format(number.quantize(Decimal("0.000000000001")), "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def expand_refs(text: str, size: int) -> list[str]:
    """Expand an explicitly uniform conversion or validate a component-specific list."""
    values = text.split(";")
    if len(values) == 1:
        return values * size
    assert len(values) == size, (text, size)
    return values


def section_group(row: dict[str, str]) -> str:
    """Preserve questionnaire period and prepared/service boundaries."""
    code, days = row["itc"], row["period_days"]
    if code == "11108":
        assert days == "30"
        return "MILLING_SERVICE_30_DAY"
    if code.startswith("1100"):
        assert days == "30"
        return "PREPARED_30_DAY"
    assert days in {"14", "30"}, (code, days)
    return f"AT_HOME_{days}_DAY"


def verify_inputs() -> dict[str, str]:
    """Check frozen evidence and named method inputs without opening microdata."""
    bound = {}
    for receipt_path in FROZEN:
        receipt = json.loads(receipt_path.read_text())
        for relative, binding in receipt["files"].items():
            assert sha(ROOT / relative) == binding["sha256"], relative
        bound[str(receipt_path.relative_to(ROOT))] = sha(receipt_path)
    usda_receipt = json.loads((USDA / "receipt.json").read_text())
    for name, expected in usda_receipt["output_sha256"].items():
        assert sha(USDA / name) == expected, name
        bound[str((USDA / name).relative_to(ROOT))] = expected
    bound[str((USDA / "receipt.json").relative_to(ROOT))] = sha(USDA / "receipt.json")
    for relative, expected in METHODS.values():
        assert sha(ROOT / relative) == expected, relative
        bound[relative] = expected
    for name in ["recipes.psv", "extra_conversions.psv", "scenarios.json"]:
        bound[str((HERE / name).relative_to(ROOT))] = sha(HERE / name)
    return bound


def load_catalog() -> dict[str, dict[str, str]]:
    """Resolve protein, conversion and method factors from the reviewed artifacts."""
    catalog: dict[str, dict[str, str]] = {}

    def add(
        kind: str,
        reference: str,
        value: str,
        unit: str,
        description: str,
        source_id: str,
        tier: str,
        raw_file: str,
        raw_hash: str,
        locator: str,
        evidence_kind: str = "PUBLISHED_VALUE",
        underlying_reference: str = "",
    ) -> None:
        """Register one typed factor and its independent source binding."""
        key = f"{kind}:{reference}"
        assert key not in catalog, key
        assert Fraction(value) >= 0, key
        catalog[key] = {
            "factor_id": key,
            "kind": kind,
            "value": value,
            "unit": unit,
            "description": description,
            "source_id": source_id,
            "source_tier": tier,
            "raw_file": raw_file,
            "raw_sha256": raw_hash,
            "source_locator": locator,
            "evidence_kind": evidence_kind,
            "underlying_reference": underlying_reference,
        }

    for row in read_rows(CORE / "factor_catalog.csv"):
        add(
            "protein",
            f"pk:{row['serial']}",
            row["protein_g_per_100g_edible"],
            "g/100g edible",
            row["food_name"],
            row["source_id"],
            row["source_tier"],
            row["raw_file"],
            row["raw_sha256"],
            row["source_locator"],
        )
    for row in read_rows(REGIONAL / "regional_source_cells.csv"):
        reference = f"{row['source_key']}:{row['food_code']}"
        locator = (
            f"PDF{row['pdf_page']}/printed{row['printed_page']}; food{row['food_code']}"
        )
        if row["protein_g_per_100g_edible"]:
            add(
                "protein",
                reference,
                row["protein_g_per_100g_edible"],
                "g/100g edible",
                row["food_name"],
                row["source_id"],
                row["source_tier"],
                row["raw_file"],
                row["raw_sha256"],
                locator + "; Protein column",
            )
        if row["edible_coefficient"]:
            add(
                "edible",
                reference,
                row["edible_coefficient"],
                "edible g/as-purchased g",
                row["food_name"],
                row["source_id"],
                row["source_tier"],
                row["raw_file"],
                row["raw_sha256"],
                locator + "; Edible portion coefficient",
            )
    for row in read_rows(USDA / "protein_candidates.csv"):
        add(
            "protein",
            f"usda:{row['fdc_id']}",
            row["protein_g_per_100g_edible"],
            "g/100g edible",
            row["food_description"],
            row["source_id"],
            row["source_tier"],
            row["raw_file"],
            row["raw_sha256"],
            f"FDC{row['fdc_id']}; food_nutrient_id{row['food_nutrient_id']}; food.csv record{row['food_csv_record']}; food_nutrient.csv record{row['nutrient_csv_record']}; {row['unit_locator']}",
            underlying_reference=f"derivation={row['derivation_code'] or 'NOT_SUPPLIED'}; {row['derivation_description']}",
        )
    for row in read_rows(USDA / "portion_candidates.csv"):
        if row["id"] not in {"88374", "88379", "88376"}:
            continue
        assert row["fdc_id"] == "171287" and row["amount"] == "1"
        add(
            "portion",
            f"usda_portion:{row['id']}",
            row["gram_weight"],
            "edible g/egg",
            f"US chicken egg {row['modifier']}; not Pakistan mean",
            row["source_id"],
            "A",
            "data/raw/diet/m3-usda-sr-legacy-2026-10-13/sr-legacy.zip",
            row["raw_sha256"],
            f"food_portion.csv record{row['csv_record']}; id{row['id']}; FDC171287; SR2018 documentation PDF13/printed12 defines edible gram weights",
        )
    density_selection = {
        ("Milk liquid whole", "DK", "1.031"): "milk_whole_DK",
        ("Milk cow whole", "KEN", "1.04"): "milk_cow_KEN",
        ("Milk goat whole", "FNDDS4.1", "1.08"): "milk_goat_FNDDS",
    }
    for row in read_rows(CORE / "density_candidates.csv"):
        key = (row["food_description"], row["biblio_id"], row["density_g_per_ml"])
        if key in density_selection:
            add(
                "density",
                density_selection[key],
                row["density_g_per_ml"],
                "g/ml",
                row["food_description"],
                row["source_id"],
                "A",
                row["raw_file"],
                row["raw_sha256"],
                row["source_locator"],
                underlying_reference=row["biblio_id"],
            )
    for row in read_rows(HERE / "extra_conversions.psv", "|"):
        add(
            row["kind"],
            row["conversion_id"],
            row["value"],
            row["unit"],
            row["description"],
            row["source_id"],
            "A",
            row["raw_file"],
            row["raw_sha256"],
            row["source_locator"],
            underlying_reference=row["underlying_reference"],
        )
    method_path, method_hash = METHODS["fao_hces_technical_notes"]
    add(
        "transfer",
        "tea_transfer_005",
        "0.05",
        "nutrient retained fraction",
        "FAO tea-leaf infusion assumption; source calls this edible portion; applied once",
        "fao_hces_technical_notes",
        "A",
        method_path,
        method_hash,
        "PDF2 nutrient conversion tables; 0.05 tea/mate/coffee-bean assumption",
        "PUBLISHED_METHOD_ASSUMPTION",
    )
    match_path, match_hash = METHODS["fao_infoods_food_matching_v1_2_2012"]
    add(
        "edible",
        "retail_edible",
        "1",
        "edible g/as-purchased g",
        "Explicit model assumption: selected retail flour/pulse/honey/ghee/spice product quantity is already edible; no refuse modeled",
        "fao_infoods_food_matching_v1_2_2012",
        "METHOD_NOT_MEASURED",
        match_path,
        match_hash,
        "printed8-11 Table2 food-form matching; actual identity choice declared per recipe",
        "DECLARED_MATCHING_ASSUMPTION",
    )
    add(
        "edible",
        "portion_already_edible",
        "1",
        "edible g/edible g",
        "Identity: USDA gram portion already excludes inedible refuse; no second shell factor",
        "usda_sr_legacy_documentation_2018",
        "DIMENSIONAL_IDENTITY",
        METHODS["usda_sr_legacy_documentation_2018"][0],
        METHODS["usda_sr_legacy_documentation_2018"][1],
        "PDF13/printed12 Table6; coordinator USDA README; actual mass source bound separately",
        "DIMENSIONAL_IDENTITY",
    )
    add(
        "transfer",
        "identity",
        "1",
        "unit fraction",
        "No additional nutrient-transfer adjustment; raw-food/retail-state matching declared per recipe",
        "dimensional_identity",
        "NOT_A_SOURCE_GRADE",
        "",
        "",
        "Identity multiplier; no estimated coefficient",
        "DIMENSIONAL_IDENTITY",
    )
    seen = {}
    for row in catalog.values():
        if row["raw_file"]:
            previous = seen.setdefault(row["raw_file"], row["raw_sha256"])
            assert previous == row["raw_sha256"]
    for relative, expected in seen.items():
        assert sha(ROOT / relative) == expected, relative
    assert all(f"density:{name}" in catalog for name in density_selection.values())
    return catalog


def compile_recipe(
    recipe: dict[str, str],
    item: dict[str, str],
    catalog: dict[str, dict[str, str]],
) -> tuple[Fraction, list[dict[str, str]]]:
    """Multiply each source-food conversion before its explicit equal-weight average."""
    protein_refs = recipe["protein_refs"].split(";")
    assert len(protein_refs) == len(set(protein_refs)), recipe["recipe_id"]
    count = len(protein_refs)
    assert (
        recipe["weight_rule"] == "equal"
    ), "Only the reviewed WB equal-weight rule is implemented"
    weight = Fraction(1, count)
    assert weight * count == 1
    refs = {
        kind: expand_refs(recipe[f"{kind}_refs"], count)
        for kind in ["edible", "density", "portion", "transfer"]
    }
    total = Fraction(0)
    components = []
    for index, protein_ref in enumerate(protein_refs):
        protein_id = f"protein:{protein_ref}"
        protein = Fraction(catalog[protein_id]["value"])
        assert catalog[protein_id]["unit"] == "g/100g edible"
        conversion = {kind: refs[kind][index] for kind in refs}
        binding_ids = [protein_id]
        edible, density, portion, transfer, mass = None, None, None, None, None
        if conversion["edible"] == "zero_shortcut":
            assert protein == 0, "Unknown/nonzero nutrient cannot use zero shortcut"
            assert conversion["density"] == conversion["portion"] == "none"
            assert conversion["transfer"] == "identity"
            component = Fraction(0)
            formula = (
                "source-matched protein=0; conversion unnecessary for zero protein only"
            )
        else:
            edible_id = f"edible:{conversion['edible']}"
            transfer_id = f"transfer:{conversion['transfer']}"
            edible = Fraction(catalog[edible_id]["value"])
            transfer = Fraction(catalog[transfer_id]["value"])
            assert 0 < edible <= 1 and 0 < transfer <= 1
            binding_ids.extend([edible_id, transfer_id])
            unit = item["native_unit"]
            if unit in {"Kg", "Gm"}:
                assert conversion["density"] == conversion["portion"] == "none"
                mass = Fraction(1000 if unit == "Kg" else 1)
            elif unit == "Ltr":
                assert conversion["portion"] == "none"
                density_id = f"density:{conversion['density']}"
                assert (
                    density_id in catalog
                ), "A true source density is required; specific gravity is not density"
                assert (
                    catalog[density_id]["kind"] == "density"
                    and catalog[density_id]["unit"] == "g/ml"
                )
                density = Fraction(catalog[density_id]["value"])
                assert density > 0
                binding_ids.append(density_id)
                mass = 1000 * density
            elif unit == "No":
                assert conversion["density"] == "none"
                assert (
                    conversion["edible"] == "portion_already_edible"
                ), "Edible US egg portion must not receive shell correction"
                portion_id = f"portion:{conversion['portion']}"
                portion = Fraction(catalog[portion_id]["value"])
                assert portion > 0 and catalog[portion_id]["unit"] == "edible g/egg"
                binding_ids.append(portion_id)
                mass = portion
            else:
                raise AssertionError(
                    "No physical quantity unit; only explicit known-zero recipe can compile"
                )
            component = protein * mass * edible * transfer / 100
            formula = f"({protein})/100 * ({mass}) * ({edible}) * ({transfer})"
        weighted = weight * component
        total += weighted
        components.append(
            {
                "component_id": f"{recipe['recipe_id']}:{index + 1:02d}",
                "recipe_id": recipe["recipe_id"],
                "itc": recipe["itc"],
                "native_unit": item["native_unit"],
                "protein_ref": protein_ref,
                "edible_ref": conversion["edible"],
                "density_ref": conversion["density"],
                "portion_ref": conversion["portion"],
                "transfer_ref": conversion["transfer"],
                "protein_g_per_100g_edible": str(catalog[protein_id]["value"]),
                "edible_fraction": "" if edible is None else decimal_text(edible),
                "density_g_per_ml": "" if density is None else decimal_text(density),
                "portion_edible_grams": (
                    "" if portion is None else decimal_text(portion)
                ),
                "transfer_fraction": "" if transfer is None else decimal_text(transfer),
                "grams_per_native_unit_before_edible": (
                    "" if mass is None else decimal_text(mass)
                ),
                "weight_numerator": str(weight.numerator),
                "weight_denominator": str(weight.denominator),
                "weight_source_id": "worldbank_adept_food_security_2014",
                "weight_locator": "PDF217-218/printed201-202; default equal shares if shares unknown",
                "protein_component_g_per_native_unit": decimal_text(component),
                "component_factor_numerator": str(component.numerator),
                "component_factor_denominator": str(component.denominator),
                "weighted_component_g_per_native_unit": decimal_text(weighted),
                "weighted_factor_numerator": str(weighted.numerator),
                "weighted_factor_denominator": str(weighted.denominator),
                "source_factor_refs": ";".join(binding_ids),
                "formula": formula,
                "assumptions": recipe["assumptions"],
                "scope_note": recipe["scope_note"],
            }
        )
    return total, components


def build() -> dict[str, object]:
    """Compile complete source-code roles and all declared experimental scenarios."""
    bindings = verify_inputs()
    inventory_rows = read_rows(CORE / "questionnaire_inventory.csv")
    inventory = {r["itc"]: r for r in inventory_rows}
    assert (
        len(inventory) == 120
        and sum(r["food_scope"] == "true" for r in inventory_rows) == 119
    )
    recipes = read_rows(HERE / "recipes.psv", "|")
    recipe_map = {r["recipe_id"]: r for r in recipes}
    assert len(recipe_map) == len(recipes)
    catalog = load_catalog()
    results, components = {}, []
    for recipe in recipes:
        assert recipe["itc"] in inventory
        assert recipe["WB_grade"] in {"A", "A2", "B", "B2"}
        result, pieces = compile_recipe(recipe, inventory[recipe["itc"]], catalog)
        results[recipe["recipe_id"]] = result
        components.extend(pieces)
    assert len({r["component_id"] for r in components}) == len(components)
    base = {
        r["itc"]: r["recipe_id"] for r in recipes if r["baseline_role"] != "SENSITIVITY"
    }
    assert len(base) == sum(r["baseline_role"] != "SENSITIVITY" for r in recipes)
    scenarios = json.loads((HERE / "scenarios.json").read_text())
    compiled, counts = [], {}
    for scenario, config in scenarios.items():
        active = dict(base)
        retain = config["retain_positive_codes"]
        if retain is not None:
            assert set(retain) <= set(base)
            active = {
                code: rid
                for code, rid in active.items()
                if code in retain or results[rid] == 0
            }
        for code, rid in config["recipe_overrides"].items():
            assert recipe_map[rid]["itc"] == code
            active[code] = rid
        scenario_rows = []
        for code, item in inventory.items():
            rid = active.get(code, "")
            recipe = recipe_map[rid] if rid else None
            value = results[rid] if rid else None
            group = section_group(item)
            role = "SERVICE" if code == "11108" else "K"
            if recipe:
                role = "DIRECT_ZERO_OUTSIDE_G" if code == "110018" else "G"
            if role == "G":
                assert group.startswith("AT_HOME_")
            if role == "DIRECT_ZERO_OUTSIDE_G":
                assert group == "PREPARED_30_DAY" and value == 0
            pieces = [r for r in components if r["recipe_id"] == rid]
            refs = sorted(
                {ref for r in pieces for ref in r["source_factor_refs"].split(";")}
            )
            known_zero = value is not None and value == 0
            compiled_row = {
                "scenario": scenario,
                "itc": code,
                "questionnaire_label": item["questionnaire_label"],
                "native_unit": item["native_unit"],
                "period_days": item["period_days"],
                "food_scope": item["food_scope"],
                "section_group": group,
                "role": role,
                "recipe_id": rid,
                "protein_g_per_native_unit": (
                    "" if value is None else decimal_text(value)
                ),
                "protein_factor_numerator": (
                    "" if value is None else str(value.numerator)
                ),
                "protein_factor_denominator": (
                    "" if value is None else str(value.denominator)
                ),
                "known_zero": str(known_zero).lower(),
                "calibration_value_eligible": str(role == "G").lower(),
                "quantity_required_for_G": str(role == "G" and not known_zero).lower(),
                "match_grade": recipe["WB_grade"] if recipe else "",
                "assumptions": recipe["assumptions"] if recipe else "",
                "component_ids": ";".join(r["component_id"] for r in pieces),
                "source_factor_refs": ";".join(refs),
                "formula": (
                    "weighted sum of component products; no daily/household normalization"
                    if recipe
                    else ""
                ),
                "data_gate": config["data_gate"],
                "role_reason": (
                    recipe["scope_note"]
                    if recipe
                    else (
                        "Service: retain expenditure separately; no food nutrient"
                        if role == "SERVICE"
                        else "Unresolved or excluded from this positive calibration pool; retain K scope and observed value; do not zero-fill"
                    )
                ),
                "quantity_value_channels": CHANNELS,
                "record_eligibility_policy": "G positive: positive same-channel q/v. G zero: positive same-channel v, q unnecessary for independently known zero. Observation validation remains downstream.",
                "native_unit_source": item["native_unit_source"],
                "questionnaire_source_id": item["questionnaire_source_id"],
                "questionnaire_raw_sha256": item["questionnaire_raw_sha256"],
                "questionnaire_locator": item["questionnaire_locator"],
                "status": "EXPERIMENTAL_FACTOR_NOT_ACCEPTED_INTAKE",
            }
            scenario_rows.append(compiled_row)
        assert {r["itc"] for r in scenario_rows} == set(inventory)
        counts[scenario] = dict(
            sorted(Counter(r["role"] for r in scenario_rows).items())
        )
        compiled.extend(scenario_rows)
    assert len(compiled) == len(inventory) * len(scenarios)
    for row in compiled:
        if row["role"] in {"K", "SERVICE"}:
            assert (
                row["protein_g_per_native_unit"] == "" and row["known_zero"] == "false"
            )
    used = sorted(
        {ref for r in components for ref in r["source_factor_refs"].split(";")}
    )
    write_rows("factor_catalog.csv", [catalog[key] for key in used])
    write_rows("component_factors.csv", components)
    write_rows("compiled_factors.csv", compiled)
    write_rows(
        "food_roles_baseline.csv", [r for r in compiled if r["scenario"] == "baseline"]
    )
    for row in catalog.values():
        if row["raw_file"]:
            bindings[row["raw_file"]] = row["raw_sha256"]
    receipt = {
        "date": "2026-10-13",
        "status": "EXPERIMENTAL_CALIBRATION_SPEC_VERIFIED_NOT_ACCEPTED_INTAKE",
        "household_data_read": False,
        "intake_or_unit_cost_computed": False,
        "food_codes": 119,
        "service_codes": ["11108"],
        "scenarios": list(scenarios),
        "compiled_rows": len(compiled),
        "recipes": len(recipes),
        "component_rows": len(components),
        "used_factor_rows": len(used),
        "roles_by_scenario": counts,
        "calculation": "exact rational products then weights; displayed decimals rounded to12places; exact numerator/denominator authoritative",
        "scenario_interpretation": "Method diagnostics, not statistical confidence limits or equal-plausibility uncertainty bounds. G/K changes affect calibration cost composition.",
        "input_sha256": dict(sorted(bindings.items())),
        "outputs": {
            name: sha(HERE / name)
            for name in [
                "factor_catalog.csv",
                "component_factors.csv",
                "compiled_factors.csv",
                "food_roles_baseline.csv",
            ]
        },
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
