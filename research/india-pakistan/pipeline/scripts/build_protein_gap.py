"""Compare published energy-CU protein with labelled adult reference scenarios."""

from __future__ import annotations

from decimal import Decimal

from provenance import ROOT, read_csv, write_csv

__all__ = ["build", "comparison", "summarize", "validate_pakistan"]
MODEL_METADATA = ("estimate_status", "intake_basis", "official_estimate", "limitations")


def validate_pakistan(rows: list[dict[str, str]]) -> None:
    """Prevent incomplete physical subtotals from entering complete-intake arithmetic."""
    if len(rows) != 6 or {r.get("quintile") for r in rows} != {
        "all",
        "Q1",
        "Q2",
        "Q3",
        "Q4",
        "Q5",
    }:
        raise ValueError(
            "Exactly six unresolved Pakistan national/quintile groups required"
        )
    for row in rows:
        if (
            row.get("intake_g")
            or row.get("gap_g")
            or row.get("whole_diet_protein_g_person_day")
            or row.get("residence") != "all"
            or row.get("headline_eligible") != "false"
            or row.get("tier") != "derived"
            or row.get("estimate_status") != "missing_complete_diet_total"
            or row.get("intake_basis") != "unavailable_complete_diet_total"
        ):
            raise ValueError(
                "Pakistan complete-diet totals remain missing; partial subtotals are ineligible"
            )


def comparison(intake: str, requirement: str) -> tuple[str, str]:
    """Return a descriptive signed distance, preserving missing observations."""
    if not intake:
        return "", "unknown"
    gap = Decimal(requirement) - Decimal(intake)
    return str(gap), "true" if gap > 0 else "false"


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Count tabulated cells without emitting population or unweighted group shares."""
    result = []
    keys = sorted({(r["country"], r["residence"], r["benchmark_id"]) for r in rows})
    for country, residence, benchmark in keys:
        selected = [
            r
            for r in rows
            if (r["country"], r["residence"], r["benchmark_id"])
            == (country, residence, benchmark)
            and r["is_total"] == "false"
        ]
        if not selected:
            raise ValueError("No disjoint groups for descriptive count")
        known = [r for r in selected if r["below_requirement"] != "unknown"]
        first = selected[0]
        result.append(
            {
                "country": country,
                "residence": residence,
                "benchmark_id": benchmark,
                "reference_type": first["reference_type"],
                "primary_scenario": first["primary_scenario"],
                "n_groups": str(len(selected)),
                "n_groups_with_numeric_reference_comparison": str(len(known)),
                "n_groups_below": (
                    str(sum(r["below_requirement"] == "true" for r in known))
                    if len(known) == len(selected)
                    else ""
                ),
                "unit": "tabulated_groups",
                "tier": "derived",
                "source_tier": first["source_tier"],
                "source_id": first["source_id"],
                "requirement_source_id": first["requirement_source_id"],
                "reference_weight_kg": first["reference_weight_kg"],
                "requirement_g": first["requirement_g"],
                "comparison_status": first["comparison_status"],
                "denominator_compatible": "false",
                "headline_eligible": "false",
                "population_deficiency_prevalence": "",
                "population_affected": "",
                "summary_denominator": "Disjoint published groups, not people; no percentage calculated.",
                "method": "Descriptive count excludes overlapping totals. Unequal India fractile widths are not population weights; Pakistan full totals remain missing.",
                "raw_locator": first.get("raw_locator", ""),
            }
        )
    return result


def build() -> None:
    """Build EAR-first CU comparisons without adequacy or prevalence inference."""
    india = read_csv(ROOT / "data/processed/protein_intake_consumer_unit.csv")
    pakistan = read_csv(ROOT / "data/processed/protein_intake_modelled.csv")
    if len(india) != 26 or any(
        r["intake_basis"] != "unadjusted_per_consumer_unit" for r in india
    ):
        raise ValueError(
            "Exactly 26 published India consumer-unit observations required"
        )
    validate_pakistan(pakistan)
    sources = {r["source_id"]: r for r in read_csv(ROOT / "data/processed/sources.csv")}
    benchmarks = read_csv(ROOT / "scripts/diet/requirements/benchmarks-supervisor.csv")
    if len(benchmarks) != 12 or len({r["benchmark_id"] for r in benchmarks}) != 12:
        raise ValueError("Expected twelve uniquely identified EAR/RDA scenarios")
    rows = []
    for observed in india + pakistan:
        is_india = observed["country"] == "India"
        for b in [b for b in benchmarks if b["country"] == observed["country"]]:
            for field in ("requirement_source_id", "weight_source_id"):
                if b[field] not in sources:
                    raise ValueError(f"Unregistered benchmark source: {b[field]}")
            weight = b["reference_body_weight_kg"]
            requirement = str(Decimal(b["protein_g_per_kg_day"]) * Decimal(weight))
            if Decimal(requirement) != Decimal(b["requirement_g_day"]):
                raise ValueError("Benchmark multiplication does not reconcile")
            intake = observed.get("intake_g", "")
            gap, below = comparison(intake, requirement)
            row = dict(observed)
            row.update(
                group=observed["group"] + "__" + b["benchmark_id"],
                survey_group=observed["group"],
                is_total=str(
                    observed.get("fractile") == "All-India"
                    if is_india
                    else observed["quintile"] == "all"
                ).lower(),
                intake_g=intake,
                requirement_g=requirement,
                gap_g=gap,
                below_requirement=below,
                reference_type=b["reference_type"],
                primary_scenario=b["primary_scenario"],
                reference_weight_kg=weight,
                requirement_g_per_kg_day=b["protein_g_per_kg_day"],
                reference_weight_source_id=b["weight_source_id"],
                requirement_source_id=b["requirement_source_id"],
                requirement_locator=b["table_or_page"],
                benchmark_id=b["benchmark_id"],
                tier="derived",
                source_tier=sources[observed["source_id"]]["tier"],
                denominator_compatible="false",
                actual_group_requirement_g="",
                headline_eligible="false",
                population_deficiency_prevalence="",
                population_affected="",
                comparison_status=(
                    "consumer_unit_reference_scenario_not_adequacy"
                    if is_india
                    else "unavailable_complete_diet_total"
                ),
                denominator_limitation=(
                    "HCES consumer units scale energy needs for a sedentary adult reference, not protein needs. This comparison is descriptive, not individual adequacy or population prevalence."
                    if is_india
                    else "A complete Pakistan total and protein-equivalent adult denominator are unavailable. Physical food subtotals cannot replace either."
                ),
                unit=(
                    "g/consumer_unit/day beside g/reference_adult/day"
                    if is_india
                    else "complete dietary intake unavailable"
                ),
                gap_g_semantics="Signed adult scenario minus published CU mean; not a physiological protein gap.",
                below_requirement_semantics="Tabulated CU mean below adult scenario only; not persons deficient.",
                protein_quality_assumption="No protein-quality adjustment; usual individual-intake distribution unavailable.",
                method="Published India energy-CU intake beside labelled adult EAR/RDA sensitivity. Pakistan unknowns propagate. No prevalence or adequacy classification.",
            )
            rows.append(row)
    fields = sorted(set().union(*(r.keys() for r in rows)))
    write_csv(
        ROOT / "data/processed/protein_gap.csv",
        fields,
        [{f: r.get(f, "") for f in fields} for r in rows],
    )
    summary = summarize(rows)
    write_csv(
        ROOT / "data/processed/protein_gap_group_summary.csv", list(summary[0]), summary
    )
    print(
        f"Reference rows: {len(rows)}; descriptive count rows: {len(summary)}; no population shares or Pakistan numeric gaps."
    )


if __name__ == "__main__":
    build()
