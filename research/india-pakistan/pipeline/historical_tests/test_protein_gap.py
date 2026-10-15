"""Preserve energy-unit caveats and prevent incomplete diet subtotals becoming gaps."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_protein_gap import comparison, summarize, validate_pakistan


def csv_rows(relative: str) -> list[dict[str, str]]:
    """Read released evidence without altering frozen historical files."""
    with (ROOT / relative).open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_missing_intake_never_becomes_zero() -> None:
    """Missing total intake must keep numeric difference and below flag unknown."""
    assert comparison("", "39.60") == ("", "unknown")
    assert comparison("40", "39.60") == ("-0.40", "false")
    assert comparison("39.60", "39.60") == ("0.00", "false")


def test_pakistan_has_no_eligible_total_or_residence_comparison() -> None:
    """Six unresolved official-table groups may not acquire totals or rankings."""
    rows = csv_rows("data/processed/protein_intake_modelled.csv")
    validate_pakistan(rows)
    assert len(rows) == 6
    assert all(r["residence"] == "all" for r in rows)
    for field, value in (
        ("intake_g", "40.45"),
        ("headline_eligible", "true"),
        ("tier", "A"),
    ):
        corrupted = [dict(row) for row in rows]
        corrupted[0][field] = value
        with pytest.raises(ValueError):
            validate_pakistan(corrupted)


def test_consumer_unit_and_benchmark_semantics() -> None:
    """India uses published CU values; both benchmarks remain adult scenarios."""
    rows = csv_rows("data/processed/protein_gap.csv")
    cu = {
        r["group"]: r
        for r in csv_rows("data/processed/protein_intake_consumer_unit.csv")
    }
    assert len(rows) == 192
    assert {r["reference_type"] for r in rows} == {"EAR", "RDA"}
    assert len([r for r in rows if r["primary_scenario"] == "true"]) == 32
    for row in rows:
        assert row["tier"] == "derived"
        assert row["source_tier"] == "A"
        assert row["headline_eligible"] == row["denominator_compatible"] == "false"
        assert (
            not row["population_deficiency_prevalence"]
            and not row["population_affected"]
        )
        coefficient = Decimal("0.66" if row["reference_type"] == "EAR" else "0.83")
        assert Decimal(row["requirement_g"]) == coefficient * Decimal(
            row["reference_weight_kg"]
        )
        if row["country"] == "India":
            assert row["intake_g"] == cu[row["survey_group"]]["intake_g"]
            assert row["intake_basis"] == "unadjusted_per_consumer_unit"
            assert "energy" in row["denominator_limitation"].lower()
            assert Decimal(row["gap_g"]) == Decimal(row["requirement_g"]) - Decimal(
                row["intake_g"]
            )
        else:
            assert not row["intake_g"] and not row["gap_g"]
            assert row["below_requirement"] == "unknown"
            assert row["comparison_status"] == "unavailable_complete_diet_total"


def test_counts_never_become_population_shares() -> None:
    """Unequal published groups may be counted, but no group percentage is emitted."""
    rows = csv_rows("data/processed/protein_gap.csv")
    summaries = summarize(rows)
    assert len(summaries) == 18
    for row in summaries:
        assert "share_groups_below" not in row
        assert row["unit"] == "tabulated_groups"
        assert row["tier"] == "derived"
        if row["country"] == "Pakistan":
            assert row["n_groups"] == "5"
            assert row["n_groups_with_numeric_reference_comparison"] == "0"
            assert row["n_groups_below"] == ""
        else:
            assert row["n_groups"] == "12"


def test_historical_unknowns_are_preserved() -> None:
    """Repair does not rewrite frozen receipts or unresolved historical tables."""
    folder = ROOT / "scripts/diet/m3_modelled_release_20261013"
    for record in json.loads((folder / "preservation.json").read_text())["files"]:
        assert (
            hashlib.sha256((ROOT / record["preserved"]).read_bytes()).hexdigest()
            == record["sha256"]
        )
