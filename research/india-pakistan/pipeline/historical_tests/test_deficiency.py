"""Keep survey coverage, reported counts and non-population comparisons distinct."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_deficiency
from build_deficiency import affected_count


def test_reported_count_not_backsolved_from_rounded_rate() -> None:
    """Source-published counts retain their precision instead of recomputation."""
    assert affected_count({"population_affected_published": "123456"}) == (
        "123456",
        "direct_source_reported_count",
    )


def test_missing_population_stays_missing() -> None:
    """Absent or mismatched geographic bases cannot be replaced with a zero."""
    assert affected_count({"value": "40.2", "population_base": ""})[0] == ""
    with pytest.raises(ValueError, match="coverage alignment"):
        affected_count({"value": "40.2", "population_base": "1000"})


def test_groups_cannot_be_scaled_to_people() -> None:
    """Reject multiplying an adult-reference group share by a population."""
    with pytest.raises(ValueError, match="population prevalence"):
        affected_count(
            {
                "value": "25",
                "population_base": "1000",
                "population_alignment": "source_matched",
                "unit": "percent_of_tabulated_groups_not_people",
            }
        )


def test_matched_percentage_arithmetic() -> None:
    """Check source-derived percentage arithmetic with a synthetic small base."""
    count, method = affected_count(
        {
            "value": "10.05",
            "population_base": "1000",
            "population_alignment": "source_matched",
            "unit": "percent",
        }
    )
    assert count == "101"
    assert method.endswith("rounded_to_person")


def test_tabulated_group_shares_are_not_nutrition_indicators() -> None:
    """No unweighted group percentage may appear among population risk proxies."""
    root = Path(__file__).resolve().parents[1]
    with (root / "data/processed/deficiency_population.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 28
    assert not any(
        "group_means" in r["indicator"] or "tabulated_groups" in r["unit"] for r in rows
    )
    assert all(r["tier"] and r["source_tier"] for r in rows)


def test_routine_build_does_not_mutate_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rebuilding proxies must only read registries and emit the processed dataset."""
    captured = []

    def reject_mutation(*args: object, **kwargs: object) -> None:
        """Fail if the routine build tries to register evidence again."""
        raise AssertionError("Provenance mutation in routine build")

    def capture_output(
        path: Path, fields: list[str], rows: list[dict[str, str]]
    ) -> None:
        """Collect processed output in memory without rewriting any files."""
        captured.append((path, fields, rows))

    monkeypatch.setattr(build_deficiency, "register_evidence", reject_mutation)
    monkeypatch.setattr(build_deficiency, "upsert_source", reject_mutation)
    monkeypatch.setattr(build_deficiency, "register_raw", reject_mutation)
    monkeypatch.setattr(build_deficiency, "write_csv", capture_output)
    build_deficiency.build()
    assert len(captured) == 1
    assert captured[0][0].name == "deficiency_population.csv"
    assert captured[0][2]
