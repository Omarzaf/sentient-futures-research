"""Keep conditional food subtotals separate from unavailable complete intake."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_pakistan_modelled as model


def rows(path: Path) -> list[dict[str, str]]:
    """Read the exact serialized projection for schema and source checks."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture()
def output(tmp_path: Path) -> Path:
    """Build the active model projection without changing shared processed data."""
    model.build(output_dir=tmp_path)
    return tmp_path


def test_active_complete_totals_stay_missing(output: Path) -> None:
    """Six official groups carry missing full totals rather than partial aliases."""
    result = rows(output / "protein_intake_modelled.csv")
    assert len(result) == len({r["group"] for r in result}) == 6
    assert {r["quintile"] for r in result} == {"all", "Q1", "Q2", "Q3", "Q4", "Q5"}
    assert {r["reporting_level"] for r in result} == {"national", "national_quintile"}
    for row in result:
        assert row["country"] == "Pakistan" and row["year"] == "2025"
        assert row["residence"] == "all"
        assert row["estimate_status"] == "missing_complete_diet_total"
        assert row["intake_basis"] == "unavailable_complete_diet_total"
        assert row["tier"] == "derived" and row["source_tier"] == "A"
        assert row["source_id"] == "pakistan_hies_2024_25_table23"
        assert row["raw_locator"] and row["calculation_receipt_sha256"]
        assert row["headline_eligible"] == row["whole_diet_total_eligible"] == "false"
        for field in model.FULL_TOTAL_FIELDS:
            assert row[field] == "", field
        assert row["below_requirement"] == "unknown"
        assert "subtotal_g_person_day" not in ";".join(row)


def test_source_metadata_is_copied_without_microdata_defaults(output: Path) -> None:
    """Unknown sample and conflicting fieldwork dates cannot become old hardcodes."""
    original = {
        r["group"]: r
        for r in rows(ROOT / "scripts/diet/pakistan_diet_rows.csv")
        if r["residence"] == "all"
    }
    for name in ("protein_intake_modelled.csv", "protein_model_physical_subtotals.csv"):
        for row in rows(output / name):
            for field in model.TABLE_METADATA:
                assert row[field] == original[row["group"]][field], (name, field)
            assert row["sample_size"] == row["fieldwork_end"] == ""
            assert "30123" != row["sample_size"]
            assert row["fieldwork_start"] == "2024-09"


def test_partial_tables_have_no_intake_or_gap_aliases(output: Path) -> None:
    """Numeric conditional subtotals cannot be consumed as complete intake."""
    for name, count in (
        ("protein_model_physical_subtotals.csv", 156),
        ("protein_model_sensitivity.csv", 26),
        ("protein_model_method_ranges.csv", 12),
    ):
        result = rows(output / name)
        assert len(result) == count
        for row in result:
            assert row["residence"] == "all"
            assert row["tier"] == "derived" and row["source_tier"] == "A"
            assert (
                row["adequacy_eligible"] == row["whole_diet_total_eligible"] == "false"
            )
            assert row["residence_ranking_eligible"] == "false"
            assert row["interpretation_scope"] == "conditional_incomplete_food_subtotal"
            assert not set(model.FULL_TOTAL_FIELDS) & row.keys()
            assert "intake_g" not in row and "value" not in row


def test_ranges_bind_named_endpoints_and_consistent_coverage(output: Path) -> None:
    """A method minimum/maximum is traceable and excludes held or sparse pools."""
    subtotals = {
        (r["group"], r["scenario_id"]): r
        for r in rows(output / "protein_model_physical_subtotals.csv")
    }
    for row in rows(output / "protein_model_method_ranges.csv"):
        for endpoint in ("low", "high"):
            source = subtotals[(row["group"], row[endpoint + "_method"])]
            assert source["scenario_role"] == "comparable_conditional_components"
            assert source["n_converted_foods"] == "27"
            assert row[endpoint] == source[row["scope"] + "_g_person_day"]
        assert row["statistical_confidence_interval"] == "false"
        assert row["n_enumerated_cases"] == "23"


def test_every_food_is_retained_with_missingness_reason(output: Path) -> None:
    """An unconverted group remains visible rather than disappearing from coverage."""
    result = rows(output / "protein_model_food_coverage.csv")
    assert len(result) == len({r["food_group"] for r in result}) == 38
    assert sum(r["physical_route"] == "unresolved" for r in result) == 11
    assert all(r["reason"] and r["quantity_locator"] for r in result)
    assert all(r["within_group_imputation_eligible"] == "false" for r in result)


@pytest.mark.parametrize("field", ["intake_g", "gap_g", "total_g_per_member_day"])
def test_numeric_complete_total_is_rejected(output: Path, field: str) -> None:
    """Accidentally substituting a physical subtotal fails the active guard."""
    result = rows(output / "protein_intake_modelled.csv")
    result[0][field] = "40.450970216927"
    with pytest.raises(ValueError, match="complete-total"):
        model.validate_active_totals(result)


def test_historical_release_requires_explicit_opt_in() -> None:
    """Old values remain reproducible only through an explicit historical route."""
    with pytest.raises(ValueError, match="historical=True"):
        model.historical_release_rows()
    historical = model.historical_release_rows(historical=True)
    assert len(historical["baseline"]) == 70
    assert len(historical["sensitivity"]) == 26
    national = next(
        r for r in historical["baseline"] if r["reporting_level"] == "national"
    )
    assert national["intake_g"] == "54.7170506752314"
    assert national["sample_households"] == "30123"
    assert national["sample_members"] == "184008"


def test_partial_input_cannot_smuggle_an_intake_alias() -> None:
    """Reject a numeric full-intake alias before projecting any partial row."""
    source = rows(model.SUPERVISOR / "scenario_summary.csv")[0]
    source["intake_g"] = source["matched_basket_subtotal_g_person_day"]
    with pytest.raises(ValueError, match="complete-total"):
        model.partial_projection(source, {}, "scenario_summary.csv")


def test_frozen_receipt_tampering_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Active projections require the reviewed revision receipt bytes."""
    fake = tmp_path / "revision"
    fake.mkdir()
    (fake / "integrity_receipt.json").write_text(json.dumps({"outputs": {}}))
    monkeypatch.setattr(model, "SUPERVISOR", fake)
    with pytest.raises(ValueError, match="Supervisor receipt changed"):
        model.build(output_dir=tmp_path / "out")


def test_two_builds_and_frozen_artifacts_are_identical(tmp_path: Path) -> None:
    """Repeated active projections preserve all historical/source evidence bytes."""
    before = hashlib.sha256(
        (model.STAGE / "experimental_group_estimates.csv").read_bytes()
    ).hexdigest()
    model.build(output_dir=tmp_path / "one")
    model.build(output_dir=tmp_path / "two")
    left = {p.name: p.read_bytes() for p in (tmp_path / "one").iterdir()}
    right = {p.name: p.read_bytes() for p in (tmp_path / "two").iterdir()}
    assert left == right and len(left) == 5
    assert (
        hashlib.sha256(
            (model.STAGE / "experimental_group_estimates.csv").read_bytes()
        ).hexdigest()
        == before
    )
    model.verify_frozen_inputs()
