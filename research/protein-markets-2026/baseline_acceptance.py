"""Evaluate actual baseline results without treating a fixed HOLD as a test."""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Any

__all__ = ["evaluate_baselines"]


def _finite(value: Any) -> bool:
    """Accept finite measurements while rejecting missing values and booleans."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def evaluate_baselines(india: dict, pakistan: dict) -> dict:
    """Separate numerical reproduction from source-defined method acceptance."""
    india_estimates = india.get("estimate_g_person_day", {})
    sectors = {}
    for sector, target in (("rural", 61.8), ("urban", 63.4)):
        value = india_estimates.get(sector)
        valid = _finite(value)
        sectors[sector] = {
            "estimate": value if valid else None,
            "published_target": target,
            "absolute_error": abs(value - target) if valid else None,
            "within_tolerance": valid and abs(value - target) <= 0.5,
        }
    india_numeric = all(row["within_tolerance"] for row in sectors.values())
    india_method = all(
        (
            india.get("complete_unadjusted_estimator") is True,
            india.get("source_defined_method") is True,
            india.get("target_fitting_used") is False,
        )
    )
    value = pakistan.get("estimate_kg_person_month")
    valid = _finite(value)
    pakistan_numeric = valid and Decimal("0.335") <= Decimal(str(value)) < Decimal(
        "0.345"
    )
    pakistan_method = all(
        (
            pakistan.get("complete_source_defined_comparator") is True,
            pakistan.get("all_channels_included") is True,
            pakistan.get("source_defined_method") is True,
            pakistan.get("target_fitting_used") is False,
        )
    )
    accepted = india_numeric and india_method and pakistan_numeric and pakistan_method
    return {
        "status": "PASS" if accepted else "FAIL",
        "gate_evaluation": "dynamic_complete_baseline_results",
        "India": {
            "unit": "g/person/day",
            "sectors": sectors,
            "numerical_reproduction_pass": india_numeric,
            "method_acceptance_pass": india_method,
            "accepted": india_numeric and india_method,
        },
        "Pakistan": {
            "unit": "kg/person/month",
            "estimate": value if valid else None,
            "published_target": 0.34,
            "rounding_interval": "[0.335, 0.345)",
            "numerical_reproduction_pass": bool(pakistan_numeric),
            "method_acceptance_pass": pakistan_method,
            "accepted": bool(pakistan_numeric and pakistan_method),
        },
        "new_estimation_allowed": accepted,
        "projection_allowed": accepted,
        "limits": (
            "This gate evaluates only the two baseline prerequisites. A passing "
            "comparison does not authenticate raw lineage or establish design "
            "variance, market inputs, respondent microdata, human coding or forecasts."
        ),
    }
