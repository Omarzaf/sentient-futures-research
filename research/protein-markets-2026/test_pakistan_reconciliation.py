"""Independent arithmetic and rejection cases for the PBS quantity estimator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location(
    "pakistan_reconciliation", Path(__file__).with_name("pakistan_reconciliation.py")
)
assert SPEC and SPEC.loader
PBS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PBS)


def tables() -> tuple[pd.DataFrame, ...]:
    """Use two unequal households with independently specified channel totals."""
    info = pd.DataFrame(
        {"hhcode": [1, 2], "prcode": [10, 20], "province": [1, 2], "region": [1, 2]}
    )
    roster = pd.DataFrame(
        {
            "hhcode": [1, 2, 2, 2],
            "idc": [1, 1, 2, 3],
            "s1aq10": [1, 1, 1, 2],
            "weight": [1.0, 3.0, 3.0, 3.0],
        }
    )
    weights = pd.DataFrame({"prcode": [10, 20], "weight": [1.0, 3.0]})
    food = pd.DataFrame(
        {
            "hhcode": [1, 2],
            "itc": [11203, 11203],
            "q1": [1.0, 2.0],
            "q2": [None, 1.0],
            "q3": [None, None],
            "q4": [None, None],
            "v1": [100.0, 200.0],
            "v2": [None, 100.0],
            "v3": [None, None],
            "v4": [None, None],
        }
    )
    return info, roster, weights, food


def test_person_weighted_ratio_is_not_household_mean() -> None:
    """Ten weighted kg over seven people differs from averaging household ratios."""
    hh, quality = PBS.build_households(*tables())
    result = PBS.estimate_variant(hh)
    assert result["estimate_kg_person_month"] == pytest.approx(150 / 49)
    assert result["weighted_person_denominator"] == 7
    assert quality["roster_psu_weight_disagreements"] == 0
    other = PBS.estimate_variant(hh, formula="household_mean")
    assert other["estimate_kg_person_month"] == pytest.approx(165 / 56)
    assert other["estimate_kg_person_month"] != result["estimate_kg_person_month"]


@pytest.mark.parametrize(
    ("estimate", "expected"),
    [
        (0.334999999, False),
        (0.335, True),
        (0.34, True),
        (0.344999999, True),
        (0.345, False),
    ],
)
def test_rounding_interval_is_half_open(estimate: float, expected: bool) -> None:
    """The printed0.34 interval includes its lower but excludes its upper boundary."""
    assert PBS.rounding_pass(estimate, 0.34) is expected


def test_complete_synthetic_primary_can_pass() -> None:
    """A real positive path is possible without changing the target or dropping channels."""
    info, roster, weights, food = tables()
    food[["q1", "q2", "q3", "q4"]] = 0.0
    food.loc[0, "q2"] = 0.34 * 7 * 14 / 30
    hh, quality = PBS.build_households(info, roster, weights, food)
    result = PBS.primary_assessment(PBS.estimate_variant(hh), quality)
    assert result["point_target_reproduced"] is True
    assert result["source_defined_method"] is True
    assert result["all_channels_included"] is True
    assert result["target_fitting_used"] is False


def test_paid_only_match_is_not_accepted() -> None:
    """An exact paid-only match cannot override an all-source failure."""
    info, roster, weights, food = tables()
    food[["q1", "q2", "q3", "q4"]] = 0.0
    food.loc[0, "q1"] = 0.34 * 7 * 14 / 30
    food.loc[1, "q4"] = 1.0
    hh, quality = PBS.build_households(info, roster, weights, food)
    paid = PBS.estimate_variant(hh, channels="paid_only")
    assert PBS.rounding_pass(paid["estimate_kg_person_month"], 0.34)
    result = PBS.primary_assessment(PBS.estimate_variant(hh), quality)
    assert result["point_target_reproduced"] is False
    assert PBS.primary_assessment(paid, quality)["point_target_reproduced"] is False


def test_nonmembers_are_not_eligible_people() -> None:
    """A source-coded nonmember changes only the explicitly labelled falsification."""
    hh, _ = PBS.build_households(*tables())
    result = PBS.estimate_variant(hh, denominator="all_roster")
    assert result["weighted_person_denominator"] == 10
    assert result["source_defined_method"] is False


def test_missing_priced_quantity_prevents_complete_comparator() -> None:
    """A priced record with no quantities is not silently certified a zero."""
    info, roster, weights, food = tables()
    food.loc[0, ["q1", "q2", "q3", "q4"]] = None
    hh, quality = PBS.build_households(info, roster, weights, food)
    assert quality["positive_value_no_quantity_records"] == 1
    assert not PBS.primary_assessment(PBS.estimate_variant(hh), quality)[
        "complete_source_defined_comparator"
    ]


def test_duplicate_and_unmatched_keys_fail_without_identifiers() -> None:
    """Bad joins fail before totals are formed and do not disclose respondent keys."""
    info, roster, weights, food = tables()
    with pytest.raises(ValueError, match="duplicate"):
        PBS.build_households(pd.concat([info, info.iloc[:1]]), roster, weights, food)
    with pytest.raises(ValueError, match="weight"):
        PBS.build_households(info, roster, weights.iloc[:1], food)


def test_roster_and_weight_disagreement_is_rejected() -> None:
    """A second weight source cannot be silently ignored."""
    info, roster, weights, food = tables()
    roster.loc[0, "weight"] = 99
    with pytest.raises(ValueError, match="weight"):
        PBS.build_households(info, roster, weights, food)


def test_negative_or_unknown_membership_fails() -> None:
    """Impossible quantities and undecoded membership do not reach the estimator."""
    info, roster, weights, food = tables()
    food.loc[0, "q4"] = -1
    with pytest.raises(ValueError, match="Negative"):
        PBS.build_households(info, roster, weights, food)
    food.loc[0, "q4"] = None
    roster.loc[0, "s1aq10"] = 9
    with pytest.raises(ValueError, match="membership"):
        PBS.build_households(info, roster, weights, food)


def test_ict_is_preserved_in_national_sample() -> None:
    """A geography sensitivity cannot silently become the national estimate."""
    hh, quality = PBS.build_households(*tables())
    hh["source_geography"] = ["PUNJAB", "ISLAMABAD CAPITAL TERRITORY"]
    domain = PBS.estimate_variant(hh, geography="four_provinces")
    assert domain["households"] == 1
    assert PBS.estimate_variant(hh)["households"] == 2
    assert not PBS.primary_assessment(domain, quality)["point_target_reproduced"]


def test_published_report_is_parsed_as_reference_not_input_estimate() -> None:
    """The2024columns follow2018columns and remain separately named source targets."""
    text = "TABLE 3.7.C\nChicken Meat Kg 0.42 0.32 0.36 0.41 0.29 0.34\n"
    assert PBS.parse_chicken_targets(text) == {
        "urban": 0.41,
        "rural": 0.29,
        "all": 0.34,
    }
    with pytest.raises(ValueError, match="Chicken"):
        PBS.parse_chicken_targets("TABLE 3.7.C\n")


def test_wrapped_wheat_label_retains2024_columns() -> None:
    """A label split around numeric rows must not silently shift the year columns."""
    source = "TABLE 3.7.C\nWheat and Wheat\n6.12 7.50 7.00 5.76 7.12 6.59\nFlour Kg\n"
    assert PBS.parse_food_targets(source, "Wheat and Wheat Flour") == {
        "urban": 5.76,
        "rural": 7.12,
        "all": 6.59,
    }


def test_nonfinite_inputs_fail() -> None:
    """Infinite quantities or weights cannot yield a purported numerical comparator."""
    info, roster, weights, food = tables()
    food.loc[0, "q1"] = float("inf")
    with pytest.raises(ValueError, match="Nonfinite"):
        PBS.build_households(info, roster, weights, food)
    food.loc[0, "q1"] = 1.0
    weights.loc[0, "weight"] = float("inf")
    with pytest.raises(ValueError, match="weight"):
        PBS.build_households(info, roster, weights, food)
