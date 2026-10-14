"""Keep HCES consumer-unit protein columns and their energy-scale boundary intact."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_diet import india_rows


def test_consumer_unit_uses_published_columns_not_per_capita() -> None:
    """Check Table 3.9 source anchors that distinguish year and denominator."""
    _, rows = india_rows(intake_basis="unadjusted_per_consumer_unit")
    values = {(r["residence"], r["fractile"]): r["intake_g"] for r in rows}
    assert len(rows) == len(values) == 26
    assert values[("rural", "0-5%")] == "49.7"
    assert values[("urban", "0-5%")] == "52.4"
    assert values[("rural", "All-India")] == "66.6"
    assert values[("urban", "All-India")] == "69.9"


def test_consumer_unit_does_not_become_protein_equivalence() -> None:
    """Energy-based demographic scaling is not a protein-adequacy denominator."""
    _, rows = india_rows(intake_basis="unadjusted_per_consumer_unit")
    for row in rows:
        assert row["unit"] == "g/consumer_unit/day"
        assert row["intake_basis"] == "unadjusted_per_consumer_unit"
        assert "energy" in row["denominator"]
        assert "not a protein-requirement equivalence scale" in row["notes"]
        assert "columns8-9" in row["raw_locator"]
        assert "Section2.9.5" in row["denominator_locator"]


def test_per_capita_originals_remain_separate() -> None:
    """Preserve source-published per-capita observations for other report uses."""
    _, rows = india_rows()
    national = {r["residence"]: r for r in rows if r["fractile"] == "All-India"}
    assert national["rural"]["intake_g"] == "61.8"
    assert national["urban"]["intake_g"] == "63.4"
    assert all(r["unit"] == "g/person/day" for r in rows)


def test_unknown_denominator_is_rejected() -> None:
    """A misspelled basis must fail rather than silently select per-capita data."""
    with pytest.raises(ValueError, match="intake basis"):
        india_rows(intake_basis="adult_equivalent_protein")
