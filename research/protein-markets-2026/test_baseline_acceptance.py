"""Falsify false baseline acceptance using complete and invalid measurements."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "baseline_acceptance", Path(__file__).with_name("baseline_acceptance.py")
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def inputs() -> tuple[dict, dict]:
    """Return synthetic complete inputs used only to exercise the gate."""
    return (
        {
            "estimate_g_person_day": {"rural": 61.8, "urban": 63.4},
            "complete_unadjusted_estimator": True,
            "source_defined_method": True,
            "target_fitting_used": False,
        },
        {
            "estimate_kg_person_month": 0.34,
            "complete_source_defined_comparator": True,
            "all_channels_included": True,
            "source_defined_method": True,
            "target_fitting_used": False,
        },
    )


def test_complete_reproductions_open_only_baseline_gate() -> None:
    """A real passing path must exist without declaring full research complete."""
    result = MODULE.evaluate_baselines(*inputs())
    assert result["status"] == "PASS"
    assert result["new_estimation_allowed"] is True
    assert "research_complete" not in result


@pytest.mark.parametrize(
    "value,expected", [(0.335, True), (0.344999, True), (0.345, False)]
)
def test_pakistan_rounding_interval(value: float, expected: bool) -> None:
    """The displayed hundredth has a half-open rounding interval."""
    india, pakistan = inputs()
    pakistan["estimate_kg_person_month"] = value
    result = MODULE.evaluate_baselines(india, pakistan)
    assert result["Pakistan"]["numerical_reproduction_pass"] is expected


@pytest.mark.parametrize("value", [None, True, float("nan"), float("inf"), -0.34])
def test_invalid_or_missing_measurement_cannot_pass(value: object) -> None:
    """A missing or invalid measurement is never zero or a successful baseline."""
    india, pakistan = inputs()
    pakistan["estimate_kg_person_month"] = value
    result = MODULE.evaluate_baselines(india, pakistan)
    assert result["status"] == "FAIL"
    assert result["new_estimation_allowed"] is False


def test_paid_only_or_fitted_result_cannot_open_gate() -> None:
    """Numerical agreement cannot rescue the wrong consumption definition."""
    india, pakistan = inputs()
    pakistan["all_channels_included"] = False
    pakistan["target_fitting_used"] = True
    result = MODULE.evaluate_baselines(india, pakistan)
    assert result["Pakistan"]["numerical_reproduction_pass"] is True
    assert result["Pakistan"]["accepted"] is False


def test_plausible_cpi_variant_is_not_source_method_acceptance() -> None:
    """A candidate recipe is explicit even when its numbers happen to match."""
    india, pakistan = inputs()
    india["source_defined_method"] = False
    result = MODULE.evaluate_baselines(india, pakistan)
    assert result["India"]["numerical_reproduction_pass"] is True
    assert result["status"] == "FAIL"


def test_one_sector_or_partial_intake_cannot_pass() -> None:
    """Both sectors and all components are prerequisites for the India gate."""
    india, pakistan = inputs()
    india["estimate_g_person_day"].pop("urban")
    india["complete_unadjusted_estimator"] = False
    result = MODULE.evaluate_baselines(india, pakistan)
    assert result["India"]["accepted"] is False
