"""Keep full Pakistan intake missing and release separate physical subtotals."""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from provenance import ROOT, read_csv

STAGE = ROOT / "scripts/diet/m3_calibration_estimates_20261013"
RELEASE = ROOT / "scripts/diet/m3_modelled_release_20261013"
REVIEW = ROOT / "scripts/diet/m3_interpretation_review_20261013"
AGGREGATE_SHA = "5209ac00acfa81997d4c0f79fb90b27c41db73f1a82aa66487ad61ff97bf9cc0"
RECEIPT_SHA = "7c0216d97e4b8a0369c2330f592b5bf2c8e5edaa71be11ce49cbab54fbbd6df6"
FACTOR_SHA = "da7dbb4fae9a1b4027e28b7e96d1763983d3b85de9388c26f2e0d220d99e0c44"
REVIEW_SHA = "ae506c28fe6e7e920767aea786d1b1cd53b7bd6d7bcf3a07d4d3605e65614c8c"
CONTRACT_SHA = "1fdf4721d866ae4660f07bd5a2984a871ae4889ffc082f1396cd005ff7129c51"
RAW = "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip"
RAW_SHA = "cf1286dc00cfc325df7a51fab64b8baecc4f6b62e015742e229bf299760898cc"
SOURCE = "pbs_hies_2024_25_stata_candidate"
PROVINCES = {"1": "Khyber Pakhtunkhwa", "2": "Punjab", "3": "Sindh", "4": "Balochistan"}
GEOGRAPHY = (
    "Released four-province HIES frame: Khyber Pakhtunkhwa, Punjab, Sindh and Balochistan. "
    "Whether ICT is folded into Punjab or absent is not established; AJK/GB inclusion is not established."
)
GROUPING = (
    "Independent national-within-frame population-weighted quintiles of observed Section6 expenditure "
    "per member, retaining exact-value ties; not official PBS welfare, income or within-residence quintiles."
)
YOGURT_HOLD = (
    "HELD: code11408 yogurt kg quantities disagree materially between the released archive, "
    "standalone Table23 and main-report series; period conversion does not reconcile them. "
    "Diagnostic evidence only; not eligible for baseline or adult-reference comparisons."
)
METHOD = (
    "Experimental analyst calculation from public HIES records, not a PBS published protein figure. "
    "Same-channel food quantities and values use A/14 or B/30 daily periods. "
    "Source-matched protein uses the frozen named composition, edible, density and transfer factors; "
    "published equal-food defaults are declared assumptions, not observed mixture shares. "
    "Daily G expenditure includes source-known-zero foods. Population-weighted median G rupees/protein gram "
    "within province/residence/independent expenditure quintile estimates protein for unresolved K expenditure. "
    "At-home food and prepared restaurant/hotel CPI are normalized separately within residence over nine months. "
    "Mean=sum(household weight*household daily protein)/sum(household weight*members). "
    "No household trimming, official-table fitting or AI-generated numerical parameters."
)
LIMITS = (
    "Experimental apparent household protein associated with observed reported food quantities/values, "
    "not measured individual intake, complete measured consumption or a strict lower bound. "
    + GEOGRAPHY
    + " "
    "Independent observed-expenditure quintiles differ from official Table23 groups. "
    "Source release/table disagreements remain unresolved; yogurt stays unresolved in baseline. "
    "Reference-food costs may not transfer to unresolved foods or prepared meals. "
    "Narrow reference-pool stress tests differ substantially and are not confidence bounds. "
    "Broad CPI baskets, missing expenditure parts, reporting, waste and intrahousehold allocation limit interpretation. "
    "Blank channels/absent food records are not proven true nonconsumption; wholly unreported food is not recovered. "
    "Imputation reverses the baseline rural/urban ordering; group rankings are model dependent. "
    "Input source grades do not certify this analyst model. No headline, adequacy or deficiency-prevalence use."
)


def verify_frozen_inputs() -> None:
    """Reject drift in reviewed calculations, contract and preserved unknown rows."""
    required = {
        STAGE / "experimental_group_estimates.csv": AGGREGATE_SHA,
        STAGE / "integrity_receipt.json": RECEIPT_SHA,
        ROOT / "scripts/diet/m3_calibration_spec/compiled_factors.csv": FACTOR_SHA,
        REVIEW / "review_receipt.json": REVIEW_SHA,
        REVIEW / "acceptance_contract.json": CONTRACT_SHA,
        ROOT / RAW: RAW_SHA,
    }
    preservation = json.loads((RELEASE / "preservation.json").read_text())
    required.update({ROOT / r["preserved"]: r["sha256"] for r in preservation["files"]})
    for path, expected in required.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen release input changed: {path.relative_to(ROOT)}")


def additional_sources() -> str:
    """Resolve the named calculation inputs without grading the analyst result."""
    ids = {
        r["source_id"]
        for r in read_csv(ROOT / "scripts/diet/m3_calibration_spec/factor_catalog.csv")
        if r["source_id"] != "dimensional_identity"
    }
    ids.update(
        {
            "fao_hces_nutrient_method_current",
            "fao_adept_nutrient_analysis_2018",
            "worldbank_adept_food_security_2014",
            "pbs_hies_2024_25_female_questionnaire",
            "pbs_hies_2024_25_male_questionnaire",
        }
    )
    for path in (
        "scripts/diet/m3_price_inputs/price_indices_staging.csv",
        "scripts/diet/m3_price_inputs/overall_cpi/overall_cpi.csv",
    ):
        ids.update(r["source_id"] for r in read_csv(ROOT / path))
    sources = {r["source_id"]: r for r in read_csv(ROOT / "data/processed/sources.csv")}
    assert all(
        i in sources and sources[i]["tier"] in {"A", "B"} for i in ids | {SOURCE}
    )
    return ";".join(sorted(ids))


def release_row(
    row: dict[str, str], source_ids: str, *, historical: bool = False
) -> dict[str, str]:
    """Reproduce a withdrawn historical aggregate only after explicit opt-in."""
    if not historical:
        raise ValueError("Withdrawn pooled-basket model requires historical=True")
    residence = {"": "all", "1": "rural", "2": "urban"}[row["region"]]
    province = PROVINCES.get(row["province"], "Pakistan")
    quintile = "Q" + row["quintile"] if row["quintile"] else "all"
    group = f"independent_observed_expenditure__{province.replace(' ', '_')}__{residence}__{quintile}"
    total = Decimal(row["total_g_per_member_day"])
    parts = sum(
        Decimal(row[k])
        for k in (
            "source_g_per_member_day",
            "imputed_at_home_g_per_member_day",
            "imputed_prepared_g_per_member_day",
        )
    )
    assert abs(total - parts) < Decimal("0.000000001")
    source_grade_basis = "A/B grades describe source inputs, not a credibility grade or official endorsement of this analyst model"
    source_all = ";".join(sorted({SOURCE, *source_ids.split(";")}))
    is_held = row["factor_scenario"] == "yogurt_included_held"
    return {
        "country": "Pakistan",
        "region": province,
        "province_code": row["province"],
        "residence_code": row["region"],
        "group": group,
        "group_id": row["reporting_level"] + "__" + group,
        "year": "2025",
        "year_basis": "survey_round_end_not_calendar_year_intake",
        "period": "2024-25",
        "residence": residence,
        "quintile": quintile,
        "reporting_level": row["reporting_level"],
        "total_display_label": "Survey total — covered four provinces",
        "geography_display_label": (
            "Survey total — covered four provinces" if not row["province"] else province
        ),
        "metric": "modelled_apparent_household_protein",
        "intake_g": row["total_g_per_member_day"],
        "total_g_per_member_day": row["total_g_per_member_day"],
        "source_converted_g": row["source_g_per_member_day"],
        "source_g_per_member_day": row["source_g_per_member_day"],
        "imputed_at_home_g": row["imputed_at_home_g_per_member_day"],
        "imputed_at_home_g_per_member_day": row["imputed_at_home_g_per_member_day"],
        "imputed_prepared_g": row["imputed_prepared_g_per_member_day"],
        "imputed_prepared_g_per_member_day": row["imputed_prepared_g_per_member_day"],
        "imputed_share": row["imputed_share"],
        "imputed_share_unit": "fraction_of_modelled_protein_not_people_or_food_expenditure",
        "component_definition": "Source-converted reported quantities plus at-home K and prepared K expenditure/cell-median protein cost; no component is measured individual intake",
        "unit": "g/household_member/day",
        "estimate_type": "experimental_analyst_modelled_apparent_household_protein",
        "estimate_status": (
            "held_diagnostic_only" if is_held else "experimental_reviewed_with_warnings"
        ),
        "estimate_author": "Project analyst calculation; not PBS",
        "intake_basis": "observed_expenditure_apparent_household_protein",
        "evidence_status": (
            "HELD_YOGURT_RELEASE_DISCREPANCY"
            if is_held
            else "EXPERIMENTAL_SOURCE_DERIVED"
        ),
        "evidence_hold_reason": YOGURT_HOLD if is_held else "",
        "headline_eligible": "false",
        "official_pbs_estimate": "false",
        "official_estimate": "false",
        "measured_individual_intake": "false",
        "denominator_compatible": "false",
        "denominator_compatibility_basis": "All-age household-member means are not reference-adult requirements",
        "population_deficiency_prevalence": "",
        "population_affected": "",
        "source_id": SOURCE,
        "source_ids": source_all,
        "additional_source_ids": source_ids,
        "input_tier_scope": source_grade_basis,
        "source_grade_basis": source_grade_basis,
        "food_match_grade": "Mixed source-form matching grades; food-level values and assumptions in frozen compiled_factors.csv; distinct from A/B source tiers",
        "method": METHOD,
        "notes": LIMITS,
        "limitations": LIMITS,
        "geographic_scope": GEOGRAPHY,
        "geography_scope": GEOGRAPHY,
        "grouping_basis": GROUPING,
        "group_definition": GROUPING,
        "sample_size": row["households"],
        "sample_size_unit": "households",
        "sample_households": row["households"],
        "sample_basis": "Exact contributing released households in this aggregate; all retained",
        "sample_members": row["members"],
        "sample_members_unit": "persons_with_roster_member_yes_all_ages",
        "reference_households": row["reference_households"],
        "reference_households_unit": "households_with_positive_G_protein_and_matched_G_value",
        "no_matched_source_households": row["no_matched_source_households"],
        "households_with_imputed_at_home": row["households_with_imputed_at_home"],
        "households_with_imputed_prepared": row["households_with_imputed_prepared"],
        "survey_sample_size": "30123",
        "survey_sample_size_unit": "households",
        "survey_sample_members": "184008",
        "survey_sample_members_unit": "persons_with_roster_member_yes_all_ages",
        "survey_sample_basis": "Verified released household sample;184008 member=yes roster records",
        "denominator": "Sum of positive household survey weight times member=yes count, all ages",
        "mean_formula": "sum(household_weight * household_daily_protein) / sum(household_weight * member_yes_count); all households retained",
        "population_weight": row["population_weight"],
        "population_weight_unit": "survey_expanded_member_weight_not_independent_population_estimate",
        "household_weight_sum": row["household_weight"],
        "household_weight_sum_unit": "survey_expanded_household_weight",
        "fieldwork_start": "2024-10",
        "fieldwork_end": "2025-06",
        "fieldwork_note": "Observed enumeration dates in public archive; source publication date statements differ",
        "fieldwork_basis": "Actual archive enumeration dates; distinct from conflicting publication-wide descriptions",
        "factor_scenario": row["factor_scenario"],
        "grouping_scenario": row["grouping_scenario"],
        "price_scenario": row["price_scenario"],
        "raw_file": RAW,
        "raw_sha256": RAW_SHA,
        "raw_locator": "Stata data:section_info,plist_roster,weight,sec_6a_consum_exp; frozen factor/cost/grouping recipes",
        "calculation_file": "scripts/diet/m3_calibration_estimates_20261013/experimental_group_estimates.csv",
        "calculation_sha256": AGGREGATE_SHA,
        "calculation_receipt_file": "scripts/diet/m3_calibration_estimates_20261013/integrity_receipt.json",
        "calculation_receipt_sha256": RECEIPT_SHA,
        "factor_file": "scripts/diet/m3_calibration_spec/compiled_factors.csv",
        "factor_sha256": FACTOR_SHA,
        "interpretation_review_file": "scripts/diet/m3_interpretation_review_20261013/REVIEW.md",
        "interpretation_receipt_sha256": REVIEW_SHA,
        "acceptance_contract_file": "scripts/diet/m3_interpretation_review_20261013/acceptance_contract.json",
        "acceptance_contract_sha256": CONTRACT_SHA,
        "method_record": "notes/M3-MODELLED-RELEASE-2026-10-13.md",
        "statistical_confidence_interval": "",
        "scenario_extrema_are_confidence_interval": "false",
        "uncertainty_interval_low": "",
        "uncertainty_interval_high": "",
    }


def historical_release_rows(
    *, historical: bool = False
) -> dict[str, list[dict[str, str]]]:
    """Reproduce historical rows without writing them to active processed files."""
    if not historical:
        raise ValueError("Withdrawn pooled-basket model requires historical=True")
    path = STAGE / "experimental_group_estimates.csv"
    verify_frozen_inputs()
    inputs = read_csv(path)
    source_ids = additional_sources()
    baseline = [
        release_row(r, source_ids, historical=True)
        for r in inputs
        if (r["factor_scenario"], r["grouping_scenario"], r["price_scenario"])
        == ("baseline", "nominal", "food_restaurant_cpi")
    ]
    assert len(baseline) == 70 and len({r["group"] for r in baseline}) == 70
    scenarios = []
    for source in inputs:
        if source["reporting_level"] != "national":
            continue
        row = release_row(source, source_ids, historical=True)
        factor = source["factor_scenario"]
        row["scenario_role"] = (
            "reference_pool_stress_not_confidence_interval"
            if factor in {"exact_food_forms", "domestic_single_positive"}
            else (
                "held_release_discrepancy"
                if factor == "yogurt_included_held"
                else "declared_parameter_or_method_scenario_not_confidence_interval"
            )
        )
        row["baseline_eligible"] = str(
            (factor, source["grouping_scenario"], source["price_scenario"])
            == ("baseline", "nominal", "food_restaurant_cpi")
        ).lower()
        row["scenario_interpretation"] = (
            "Declared reference-pool/method diagnostic; do not average cases, treat equally as plausible observations, or take extrema as a confidence interval"
        )
        scenarios.append(row)
    assert len(scenarios) == 26
    return {"baseline": baseline, "sensitivity": scenarios}


SUPERVISOR = ROOT / "scripts/diet/supervisor_model_20261013"
SUPERVISOR_RECEIPT_SHA = (
    "8d998b4f529601e1a31931c9f68a0d3e99db7e1c1126f6507226ba55d156cdd9"
)
TABLE_SOURCE = "pakistan_hies_2024_25_table23"
TABLE_METADATA = (
    "sample_size",
    "sample_basis",
    "survey_sample_size",
    "survey_sample_basis",
    "sample_source_id",
    "sample_locator",
    "denominator",
    "fieldwork_start",
    "fieldwork_end",
    "fieldwork_note",
)
FULL_TOTAL_FIELDS = (
    "intake_g",
    "total_g_per_member_day",
    "whole_diet_protein_g_person_day",
    "whole_diet_total",
    "source_converted_g",
    "source_g_per_member_day",
    "imputed_at_home_g",
    "imputed_prepared_g",
    "imputed_share",
    "gap_g",
    "adequacy_ratio",
    "population_deficiency_prevalence",
    "population_affected",
)
ACTIVE_LIMITS = (
    "Complete dietary-protein total unavailable. Table23 lists major foods only; "
    "11 baseline foods lack defensible complete physical conversion, prepared-food "
    "quantity coverage is incomplete, and purchased food forms remain uncertain. "
    "Conditional subtotals are separate diagnostics, not total intake, true-intake "
    "bounds, adequacy or deficiency prevalence. Old pooled-basket calibration is withdrawn."
)


def verify_supervisor_inputs() -> dict[str, object]:
    """Verify the frozen new revision and every bound input/output before projection."""
    path = SUPERVISOR / "integrity_receipt.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != SUPERVISOR_RECEIPT_SHA:
        raise ValueError("Supervisor receipt changed; declare a new reviewed revision")
    receipt = json.loads(path.read_text())
    for relative, record in receipt["input_bindings"].items():
        source = ROOT / relative
        if (
            hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]
            or source.stat().st_size != record["bytes"]
        ):
            raise ValueError(f"Supervisor source binding changed: {relative}")
    for name, record in receipt["outputs"].items():
        if (
            hashlib.sha256((SUPERVISOR / name).read_bytes()).hexdigest()
            != record["sha256"]
        ):
            raise ValueError(f"Supervisor output changed: {name}")
    if receipt["whole_diet_total_available"] or receipt["old_total_reused"]:
        raise ValueError("Supervisor receipt cannot admit a complete-total claim")
    return receipt


def table_metadata() -> dict[str, dict[str, str]]:
    """Preserve original Table23 metadata without historical microdata defaults."""
    source_rows = read_csv(ROOT / "scripts/diet/pakistan_diet_rows.csv")
    source = next(
        r
        for r in read_csv(SUPERVISOR / "source_snapshot.csv")
        if r["source_id"] == TABLE_SOURCE
    )
    metadata = {}
    for group in sorted({r["group"] for r in source_rows if r["residence"] == "all"}):
        selected = [r for r in source_rows if r["group"] == group]
        first = selected[0]
        if len(selected) != 38 or any(
            any(r[field] != first[field] for field in TABLE_METADATA) for r in selected
        ):
            raise ValueError("Table23 group metadata or coverage is inconsistent")
        metadata[group] = {
            "country": first["country"],
            "region": first["region"],
            "group": group,
            "group_id": "table23__" + group,
            "year": first["year"],
            "year_basis": "survey_round_end_not_calendar_year_intake",
            "period": first["period"],
            "residence": first["residence"],
            "quintile": first["quintile"],
            "reporting_level": (
                "national" if first["quintile"] == "all" else "national_quintile"
            ),
            **{field: first[field] for field in TABLE_METADATA},
            "sample_size_unit": "households_if_known",
            "source_id": TABLE_SOURCE,
            "source_tier": source["tier"],
            "source_grade_basis": "Source tier grades the published input, not the conditional analyst conversion",
            "tier": "derived",
            "raw_file": first["raw_file"],
            "raw_sha256": first["raw_sha256"],
            "raw_locator": ";".join(r["raw_locator"].split(";")[0] for r in selected),
            "group_definition": first["denominator"],
            "grouping_basis": "Official Table23 consumption-expenditure quintiles; not the old independent microdata groups",
            "headline_eligible": "false",
            "official_estimate": "false",
            "official_pbs_estimate": "false",
            "measured_individual_intake": "false",
            "whole_diet_total_eligible": "false",
            "adequacy_eligible": "false",
            "residence_ranking_eligible": "false",
            "denominator_compatible": "false",
            "calculation_receipt_file": str(
                (SUPERVISOR / "integrity_receipt.json").relative_to(ROOT)
            ),
            "calculation_receipt_sha256": SUPERVISOR_RECEIPT_SHA,
            "method_record": str((SUPERVISOR / "README.md").relative_to(ROOT)),
            "limitations": ACTIVE_LIMITS,
        }
    return metadata


def validate_active_totals(rows: list[dict[str, str]]) -> None:
    """Reject any promotion of conditional components into complete-total inference."""
    if len(rows) != 6 or len({r["group"] for r in rows}) != 6:
        raise ValueError(
            "Exactly six national/quintile missing complete-total rows required"
        )
    for row in rows:
        if (
            any(row.get(field) for field in FULL_TOTAL_FIELDS)
            or row.get("estimate_status") != "missing_complete_diet_total"
            or row.get("intake_basis") != "unavailable_complete_diet_total"
            or row.get("whole_diet_total_eligible") != "false"
            or row.get("adequacy_eligible") != "false"
            or row.get("headline_eligible") != "false"
            or row.get("residence") != "all"
            or row.get("below_requirement") != "unknown"
            or row.get("tier") != "derived"
        ):
            raise ValueError("Active complete-total inference must remain missing")


def partial_projection(
    row: dict[str, str], metadata: dict[str, str], filename: str
) -> dict[str, str]:
    """Project a labelled partial diagnostic with no intake or adequacy aliases."""
    if any(row.get(field) for field in FULL_TOTAL_FIELDS):
        raise ValueError("A partial input contains a complete-total value")
    partial = {k: v for k, v in row.items() if k not in FULL_TOTAL_FIELDS}
    held = row.get("scenario_role") == "held_quantity_discrepancy"
    return {
        **partial,
        **metadata,
        "interpretation_scope": "conditional_incomplete_food_subtotal",
        "estimate_status": (
            "held_diagnostic_only" if held else "conditional_physical_subtotal"
        ),
        "evidence_status": (
            "HELD_QUANTITY_DISCREPANCY" if held else "CONDITIONAL_PHYSICAL_SUBTOTAL"
        ),
        "statistical_confidence_interval": "false",
        "calculation_file": str((SUPERVISOR / filename).relative_to(ROOT)),
        "calculation_sha256": hashlib.sha256(
            (SUPERVISOR / filename).read_bytes()
        ).hexdigest(),
    }


def build(output_dir: Path | None = None) -> None:
    """Release only missing complete totals and separate national partial diagnostics."""
    verify_supervisor_inputs()
    metadata = table_metadata()
    summaries = read_csv(SUPERVISOR / "scenario_summary.csv")
    baseline = [
        r
        for r in summaries
        if r["group"] in metadata and r["scenario_id"] == "edible_flesh_us_large"
    ]
    totals = []
    for row in baseline:
        totals.append(
            {
                **metadata[row["group"]],
                **{field: "" for field in FULL_TOTAL_FIELDS},
                "unit": "g/person/day",
                "metric": "complete_dietary_protein_unavailable",
                "estimate_status": "missing_complete_diet_total",
                "estimate_type": "unavailable_complete_dietary_protein",
                "estimate_author": "AI-assisted analyst calculation; human scholarly review pending",
                "intake_basis": "unavailable_complete_diet_total",
                "evidence_status": "INCOMPLETE_DIET_TOTAL_MISSING",
                "below_requirement": "unknown",
                "source_ids": row["source_ids"],
                "method": "Full intake remains missing after all38 food dispositions; physical subtotals are separate tables and cannot enter adequacy calculations",
                "calculation_file": str(
                    (SUPERVISOR / "scenario_summary.csv").relative_to(ROOT)
                ),
                "calculation_sha256": hashlib.sha256(
                    (SUPERVISOR / "scenario_summary.csv").read_bytes()
                ).hexdigest(),
            }
        )
    validate_active_totals(totals)
    partials = [
        partial_projection(r, metadata[r["group"]], "scenario_summary.csv")
        for r in summaries
        if r["group"] in metadata
    ]
    ranges = [
        partial_projection(r, metadata[r["group"]], "method_ranges.csv")
        for r in read_csv(SUPERVISOR / "method_ranges.csv")
        if r["group"] in metadata
    ]
    for row in ranges:
        if not row["low_method"] or not row["high_method"]:
            raise ValueError("Every method range needs named endpoints")
    coverage = [
        {
            **r,
            "country": "Pakistan",
            "source_id": TABLE_SOURCE,
            "source_tier": metadata["all_all"]["source_tier"],
            "tier": "derived",
            "headline_eligible": "false",
            "whole_diet_total_eligible": "false",
            "method_record": metadata["all_all"]["method_record"],
        }
        for r in read_csv(SUPERVISOR / "food_coverage.csv")
    ]
    tables = {
        "protein_intake_modelled.csv": totals,
        "protein_model_physical_subtotals.csv": partials,
        "protein_model_method_ranges.csv": ranges,
        "protein_model_food_coverage.csv": coverage,
        "protein_model_sensitivity.csv": [
            r for r in partials if r["group"] == "all_all"
        ],
    }
    for name, rows in tables.items():
        target = (output_dir or ROOT / "data/processed") / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=list(rows[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
    verify_supervisor_inputs()
    print(
        "Released six missing complete totals, 156 partial method rows, 12 named ranges and 38 food dispositions; no residence rankings."
    )


if __name__ == "__main__":
    build()
