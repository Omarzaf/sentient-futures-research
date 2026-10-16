"""Protect official reproduction diagnostics against false passing results."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location(
    "pbs_diagnostic", Path(__file__).with_name("reproduce_pakistan.py")
)
assert SPEC is not None and SPEC.loader is not None
PBS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PBS)


def _tables() -> tuple[pd.DataFrame, ...]:
    """Build synthetic households with unequal sizes and survey weights."""
    info = pd.DataFrame(
        {"hhcode": [1, 2], "prcode": [10, 20], "province": [1, 2], "region": [1, 2]}
    )
    roster = pd.DataFrame(
        {"hhcode": [1, 2, 2, 2], "idc": [1, 1, 2, 3], "s1aq10": [1, 1, 1, 2]}
    )
    weights = pd.DataFrame({"prcode": [10, 20], "weight": [1.0, 3.0]})
    food = pd.DataFrame(
        {
            "hhcode": [1, 2],
            "itc": [11203, 11203],
            "unit": [None, None],
            "q1": [1.0, 2.0],
            "q2": [None, 1.0],
            "q3": [None, None],
            "q4": [None, None],
            "v1": [100, 200],
            "v2": [None, 100],
            "v3": [None, None],
            "v4": [None, None],
        }
    )
    return info, roster, weights, food


def test_ratio_of_weighted_totals_keeps_nonmembers_separate() -> None:
    """Unequal household size must not become a mean of household ratios."""
    result = PBS.aggregate_diagnostic(*_tables())
    rows = {
        (r["residence"], r["denominator"], r["period_convention"]): r
        for r in result["diagnostics"]
    }
    assert rows[("all", "member_yes", "days30_div14")][
        "diagnostic_kg_person_month"
    ] == pytest.approx(10 * 30 / 14 / 7)
    assert rows[("all", "all_roster", "days30_div14")][
        "diagnostic_kg_person_month"
    ] == pytest.approx(10 * 30 / 14 / 10)
    assert result["status"] == "HOLD" and result["baseline_reproduced"] is False
    assert result["survey_design_verified"] is False


def test_paid_only_numerical_match_cannot_pass_gate() -> None:
    """Matching the target by discarding in-kind consumption is not reproduction."""
    info, roster, weights, food = _tables()
    food["q1"] = 0.34 * 7 / (4 * 30 / 14)
    result = PBS.aggregate_diagnostic(info, roster, weights, food)
    assert result["excluded_paid_only_match"]["within_national_report_rounding"] is True
    assert result["excluded_paid_only_match"]["accepted"] is False
    assert result["new_estimation_allowed"] is False


def test_duplicate_join_key_is_rejected_without_ids_in_error() -> None:
    """A duplicated household must fail before it inflates weighted totals."""
    info, roster, weights, food = _tables()
    info = pd.concat([info, info.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate join keys in section_info"):
        PBS.aggregate_diagnostic(info, roster, weights, food)


def test_unmatched_weight_is_not_silently_dropped() -> None:
    """A missing PSU weight must not shrink the population denominator."""
    info, roster, weights, food = _tables()
    with pytest.raises(ValueError, match="weight"):
        PBS.aggregate_diagnostic(info, roster, weights.iloc[:1], food)


def test_unknown_membership_and_negative_quantity_stop() -> None:
    """Unknown membership and impossible quantity cannot enter a diagnostic."""
    info, roster, weights, food = _tables()
    roster.loc[0, "s1aq10"] = 9
    with pytest.raises(ValueError, match="membership"):
        PBS.aggregate_diagnostic(info, roster, weights, food)
    info, roster, weights, food = _tables()
    food.loc[0, "q1"] = -1
    with pytest.raises(ValueError, match="Negative"):
        PBS.aggregate_diagnostic(info, roster, weights, food)


def test_all_missing_quantities_remain_explicit() -> None:
    """A priced record without quantities must be disclosed, not certified zero."""
    info, roster, weights, food = _tables()
    food.loc[0, PBS.QUANTITY] = None
    result = PBS.aggregate_diagnostic(info, roster, weights, food)
    assert result["quality"]["positive_value_but_no_quantity_records"] == 1
    assert result["quality"]["all_quantity_channels_missing_records"] == 1
    assert result["baseline_reproduced"] is False


def test_raw_source_identity_is_required_before_parse(tmp_path: Path) -> None:
    """Published-source paths and a changed archive cannot fake raw reproduction."""
    with pytest.raises(FileNotFoundError, match="Missing required PBS source"):
        PBS.verify_raw(tmp_path)
    (tmp_path / "pbs-stata-2024-25.zip").write_bytes(b"changed source")
    with pytest.raises(ValueError, match="identity mismatch"):
        PBS.verify_raw(tmp_path)
