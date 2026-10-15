"""Check released aggregates and arithmetic without claiming a raw-input rerun."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

PIPELINE = Path(__file__).resolve().parents[1]
DATA = PIPELINE.parent / "data"
FIXTURES = PIPELINE / "fixtures/supervisor_model"
sys.path.insert(0, str(PIPELINE / "scripts"))
import build_pakistan_modelled as projection
from build_protein_gap import comparison, summarize, validate_pakistan

SPEC = importlib.util.spec_from_file_location(
    "physical_calculation",
    PIPELINE / "scripts/diet/supervisor_model_20261013/build_model.py",
)
assert SPEC and SPEC.loader
physical = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(physical)


def rows(path: Path) -> list[dict[str, str]]:
    """Read released values as strings so numeric source precision survives."""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_physical_units_and_missingness() -> None:
    """A monthly kilogram conversion differs from recall and gram conversions."""
    assert physical.daily_content(
        Fraction(1), "kg/person/month", Fraction(188), "Kg"
    ) == Fraction(94, 15)
    assert physical.daily_content(
        Fraction(30), "g/person/month", Fraction(122, 1000), "Gm"
    ) == Fraction(122, 1000)
    assert physical.daily_content(None, "kg/person/month", Fraction(188), "Kg") is None
    assert (
        physical.daily_content(Fraction(1), "kg/person/month", Fraction(0), "Kg") == 0
    )
    with pytest.raises(ValueError):
        physical.daily_content(
            Fraction(1), "kg/person/month", Fraction(188), "Kg", days=14
        )
    with pytest.raises(ValueError):
        physical.daily_content(Fraction(1), "count/person/month", Fraction(188), "Kg")
    assert physical.complete_sum([Fraction(1), None, Fraction(3)]) is None


def test_species_specific_factors_precede_average() -> None:
    """Averaging different edible fractions before multiplication changes the result."""
    factors = [
        physical.mass_factor(Fraction("19.6"), Fraction(1000), Fraction("0.69")),
        physical.mass_factor(Fraction("17.5"), Fraction(1000), Fraction("0.75")),
    ]
    assert physical.equal_factor(factors) == Fraction("133.245")
    assert physical.equal_factor(factors) != Fraction("18.55") * 10 * Fraction("0.72")
    with pytest.raises(ValueError):
        physical.impute_within_group(
            Fraction(100), "meat", "whole_basket", Fraction(2), True
        )


def test_aggregate_fixtures_match_historical_receipt() -> None:
    """Bind only shipped aggregate outputs; do not pretend withheld inputs exist."""
    receipt = json.loads((FIXTURES / "integrity_receipt.json").read_text())
    assert not receipt["whole_diet_total_available"] and not receipt["old_total_reused"]
    for name in (
        "scenario_summary.csv",
        "method_ranges.csv",
        "food_coverage.csv",
        "scenario_definitions.csv",
    ):
        assert (
            hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
            == receipt["outputs"][name]["sha256"]
        )


def test_range_endpoints_bind_eligible_equal_coverage_cases() -> None:
    """Every released endpoint names a matching eligible scenario with 27 foods."""
    scenarios = {
        (r["group"], r["scenario_id"]): r
        for r in rows(FIXTURES / "scenario_summary.csv")
    }
    for row in rows(DATA / "protein_model_method_ranges.csv"):
        for side in ("low", "high"):
            source = scenarios[row["group"], row[side + "_method"]]
            assert source["scenario_role"] == "comparable_conditional_components"
            assert source["n_converted_foods"] == "27"
            assert source[row["scope"] + "_g_person_day"] == row[side]
        assert row["statistical_confidence_interval"] == "false"
    coverage = rows(FIXTURES / "food_coverage.csv")
    assert len(coverage) == len({r["food_group"] for r in coverage}) == 38
    assert sum(r["physical_route"] == "unresolved" for r in coverage) == 11


def test_numeric_complete_total_and_partial_alias_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A subtotal cannot quietly enter an intake or adequacy field."""
    released = rows(DATA / "protein_intake_modelled.csv")
    projection.validate_active_totals(released)
    validate_pakistan(released)
    released[0]["intake_g"] = "40.45"
    with pytest.raises(ValueError, match="complete-total"):
        projection.validate_active_totals(released)
    source = rows(FIXTURES / "scenario_summary.csv")[0]
    source["intake_g"] = source["matched_basket_subtotal_g_person_day"]
    with pytest.raises(ValueError, match="complete-total"):
        projection.partial_projection(source, {}, "scenario_summary.csv")
    with pytest.raises(ValueError, match="historical=True"):
        projection.historical_release_rows()


def test_benchmark_arithmetic_and_denominators() -> None:
    """EAR/RDA weights are adult scenarios, separate from consumer-unit observations."""
    benchmarks = rows(DATA / "reference_requirements.csv")
    assert len(benchmarks) == len({r["benchmark_id"] for r in benchmarks}) == 12
    for row in benchmarks:
        coefficient = Decimal("0.66" if row["reference_type"] == "EAR" else "0.83")
        assert Decimal(row["protein_g_per_kg_day"]) == coefficient
        assert Decimal(row["requirement_g_day"]) == coefficient * Decimal(
            row["reference_body_weight_kg"]
        )
        assert row["tier"] == "derived" and row["source_tier"] == "A"
        assert "not population" in row["notes"] and "energy" in row["notes"]
    assert comparison("", "39.60") == ("", "unknown")
    gaps = rows(DATA / "protein_gap.csv")
    assert len(gaps) == 192
    for row in gaps:
        assert row["denominator_compatible"] == row["headline_eligible"] == "false"
        assert not row["population_deficiency_prevalence"]
        if row["country"] == "Pakistan":
            assert not row["intake_g"] and not row["gap_g"]
        else:
            assert row["intake_basis"] == "unadjusted_per_consumer_unit"
            assert Decimal(row["gap_g"]) == Decimal(row["requirement_g"]) - Decimal(
                row["intake_g"]
            )
    assert all("share_groups_below" not in row for row in summarize(gaps))
