"""Reject silent filling, incorrect recall and altered HCES candidate identities."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

SPEC = importlib.util.spec_from_file_location(
    "hces_inspection", Path(__file__).with_name("inspect_hces.py")
)
assert SPEC and SPEC.loader
HCES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HCES)


def test_seven_and_thirty_day_items_keep_units_and_recall() -> None:
    """A kilogram, counted egg and gram retain distinct source coefficients."""
    food = pd.DataFrame(
        {
            "hhid": [1, 1, 1],
            "item_code": [101, 190, 251],
            "cons_total_qty": [1.0, 1.0, 1.0],
        }
    )
    factors = pd.DataFrame(
        {
            "item_code": [101, 190, 251],
            "unit": ["kg.", "no.", "gm."],
            "protein_g_per_unit": [79.4, 13.28, 0.07],
        }
    )
    result, _ = HCES.physical_components(food, factors, "05")
    assert result.iloc[0]["physical_protein_g_day"] == pytest.approx(
        79.4 / 30 + 13.28 / 7 + 0.07 / 7
    )


def test_unresolved_rupee_items_are_never_zero_filled() -> None:
    """A rupee-valued food remains outside the physical component calculation."""
    food = pd.DataFrame(
        {"hhid": [1, 2], "item_code": [101, 166], "cons_total_qty": [1000, None]}
    )
    factors = pd.DataFrame(
        {
            "item_code": [101, 166, 166],
            "unit": ["kg.", "Re.", "Re."],
            "protein_g_per_unit": [79.4, 0.05, 0.04],
        }
    )
    result, diagnostic = HCES.physical_components(food, factors, "05")
    assert len(result) == 1
    assert diagnostic["unresolved_rupee_item_codes"] == [166]


def test_decimal_parquet_quantity_is_already_in_documented_units(
    tmp_path: Path,
) -> None:
    """A decimal-valued Parquet amount must not receive an implied-scale divisor."""
    path = tmp_path / "decimal_quantity.parquet"
    pd.DataFrame(
        {"hhid": [1], "item_code": [101], "cons_total_qty": [0.125]}
    ).to_parquet(path, index=False)
    food = pd.read_parquet(path)
    factors = pd.DataFrame(
        {"item_code": [101], "unit": ["kg."], "protein_g_per_unit": [79.4]}
    )
    result, _ = HCES.physical_components(food, factors, "05")
    assert result.iloc[0]["physical_protein_g_day"] == pytest.approx(0.125 * 79.4 / 30)


def test_unmapped_child_and_parent_codes_stay_visible() -> None:
    """An unsupported grain mapping cannot silently disappear from coverage."""
    food = pd.DataFrame({"hhid": [1], "item_code": [55], "cons_total_qty": [1000]})
    factors = pd.DataFrame(
        {"item_code": [1], "unit": ["kg."], "protein_g_per_unit": [94.4]}
    )
    result, diagnostic = HCES.physical_components(food, factors, "05")
    assert result.empty
    assert diagnostic["codes_without_table_coefficient"] == [55]


def test_duplicate_item_and_negative_quantity_are_rejected() -> None:
    """Duplicate keys and impossible quantities must fail before summation."""
    food = pd.DataFrame(
        {"hhid": [1, 1], "item_code": [101, 101], "cons_total_qty": [1000, 2000]}
    )
    factors = pd.DataFrame(
        {"item_code": [101], "unit": ["kg."], "protein_g_per_unit": [79.4]}
    )
    with pytest.raises(ValueError, match="duplicate"):
        HCES.physical_components(food, factors, "05")
    food = food.iloc[:1].copy()
    food["cons_total_qty"] = -1
    with pytest.raises(ValueError, match="Negative"):
        HCES.physical_components(food, factors, "05")


def test_incomplete_coefficient_table_is_rejected() -> None:
    """One attractive coefficient is insufficient to certify the official table."""
    text = "Table 2.2: Nutrient contents of food items\n1. 061 rice kg. 3567 79.4 5.2\n2.11 EFFICACY OF THE ESTIMATES"
    with pytest.raises(ValueError, match="incomplete"):
        HCES.parse_factors(text)


def test_published_values_cannot_substitute_for_candidate_receipt(
    tmp_path: Path,
) -> None:
    """A claim of official identity cannot bypass the explicitly bounded input type."""
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"source_type": "official_raw", "files": []}))
    with pytest.raises(ValueError, match="third-party"):
        HCES.verify_candidate(tmp_path, receipt)
