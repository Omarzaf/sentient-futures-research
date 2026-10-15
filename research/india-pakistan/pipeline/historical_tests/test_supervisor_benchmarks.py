"""Verify adult benchmark provenance, denominator labels and distinct scenario IDs."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from diet.requirements.build_supervisor_benchmarks import benchmark_rows


def test_both_requirement_scenarios_recompute_without_id_collision() -> None:
    """EAR and safe-intake scenarios have separate identifiers at every weight."""
    rows = benchmark_rows()
    assert len(rows) == len({r["benchmark_id"] for r in rows}) == 12
    for row in rows:
        coefficient = Decimal(row["protein_g_per_kg_day"])
        assert coefficient == (
            Decimal("0.66") if row["reference_type"] == "EAR" else Decimal("0.83")
        )
        assert Decimal(row["requirement_g_day"]) == coefficient * Decimal(
            row["reference_body_weight_kg"]
        )
        assert row["tier"] == "derived"
        assert row["source_tier"] == "A"


def test_consumer_unit_reference_is_explicit_not_population_average() -> None:
    """The displayed 60 kg reference is sourced but not an observed group weight."""
    rows = benchmark_rows()
    row = next(r for r in rows if r["benchmark_id"] == "india_EAR_60kg")
    assert row["requirement_g_day"] == "39.60"
    assert row["weight_source_id"] == "mospi_nutrition_report_594_2025"
    assert row["primary_scenario"] == "true"
    assert "energy" in row["notes"]
    assert "not population" in row["notes"]
