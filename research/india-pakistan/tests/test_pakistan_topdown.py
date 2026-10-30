"""Source, dimension, temporal-basis and integrity checks for the P4 companion."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pakistan_topdown", ROOT / "tools/pakistan_topdown.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)
WORKSPACE = Path(__file__).resolve().parents[5]


@pytest.fixture(scope="module")
def inputs() -> dict:
    """Read and hash-check original sources once for the integration checks."""
    return MODEL.extract(WORKSPACE)


@pytest.fixture(scope="module")
def rows(inputs: dict) -> list[dict]:
    """Calculate the full authorized grid once without writing model artifacts."""
    return MODEL.generate(inputs)


def test_exact_original_source_cells(inputs: dict) -> None:
    """Match publication cells and source-native dimensions, not just snapshots."""
    assert inputs["fao"]["poultry"]["kg_person_year"] == 8.72
    assert inputs["fao"]["milk"]["kg_person_year"] == 129.71
    assert inputs["fao"]["milk"]["thousand_tonnes"] == 32104
    assert inputs["economic"]["poultry"] == [2160, 2362, 2583]
    assert inputs["economic"]["milk"] == [54707, 56474, 58300]
    assert inputs["pbs_price"] == {"poultry": 424.89, "milk": 203.51}
    assert inputs["fx_pkr_per_usd_2025"] == 281.143001173202


def test_all_years_shares_families_and_profiles_are_retained(rows: list[dict]) -> None:
    """Detect missing inconvenient scenarios, duplicate cells or changed shares."""
    keys = {
        (
            r["quantity_family"],
            r["comparison_year"],
            r["price_profile"],
            r["capture_share"],
        )
        for r in rows
    }
    assert len(rows) == len(keys) == 162
    assert {r["comparison_year"] for r in rows} == {2026, 2030, 2035}
    assert {r["capture_share"] for r in rows} == {0.0005, 0.001, 0.005}
    assert len({r["quantity_family"] for r in rows}) == 3
    assert len({r["price_profile"] for r in rows}) == 6


def test_original_gate_disagreement_is_retained(rows: list[dict]) -> None:
    """Preserve the disclosed discrepancy rather than tuning a parameter to fit."""
    row = next(
        r
        for r in rows
        if r["quantity_family"] == "FAO2023_fixed"
        and r["comparison_year"] == 2026
        and r["price_profile"] == "official_central_sensitivity"
        and r["capture_share"] == 0.005
    )
    assert math.isclose(
        row["milk_capture_million_usd"], 112.70130982761414, abs_tol=1e-10
    )
    assert "above_10x_p90" in row["milk_comparison"]
    assert "above_10x_p90" in row["combined_comparison"]


def test_dressed_live_conversion_requires_explicit_assumption() -> None:
    """Reject silent use of a live-broiler price on meat quantities."""
    with pytest.raises(ValueError, match="yield"):
        MODEL.value_check(100, 200, "poultry_meat_kg", "PKR_per_kg_live", 2)
    assert (
        MODEL.value_check(100, 200, "poultry_meat_kg", "PKR_per_kg_live", 2, 0.5)
        == 20000
    )


def test_milk_conversion_requires_explicit_density() -> None:
    """Reject automatic kg-to-litre equality and wrong quantity dimensions."""
    with pytest.raises(ValueError, match="density"):
        MODEL.value_check(100, 200, "milk_equivalent_kg", "PKR_per_litre", 2)
    with pytest.raises(ValueError, match="Unsupported"):
        MODEL.value_check(100, 200, "milk_equivalent_kg", "PKR_per_kg_live", 2, 1)


def test_package_normalization_checks_dimensions() -> None:
    """Verify mass and volume conversions while forbidding a cross-dimension join."""
    assert MODEL.normalize_package("250ml", "milk") == 0.25
    assert MODEL.normalize_package("1.5 Litre", "milk") == 1.5
    assert MODEL.normalize_package("1000g", "chicken") == 1
    with pytest.raises(ValueError, match="dimension"):
        MODEL.normalize_package("1000g", "milk")
    with pytest.raises(ValueError):
        MODEL.normalize_package("pack of six", "milk")


def test_oecd_2035_is_2034_carry_forward(inputs: dict, rows: list[dict]) -> None:
    """Do not manufacture an OECD 2035 forecast beyond the retained vintage."""
    selected = [
        r
        for r in rows
        if r["quantity_family"] == "OECD_poultry_FAO_milk"
        and r["comparison_year"] == 2035
    ]
    assert {r["poultry_quantity_year"] for r in selected} == {"2034"}
    assert {r["poultry_quantity_thousand_tonnes"] for r in selected} == {
        inputs["oecd_poultry_thousand_tonnes"][2034]
    }
    assert all("assumption" in r["quantity_note"] for r in selected)


def test_retail_deflation_and_out_of_stock_are_disclosed(
    inputs: dict, rows: list[dict]
) -> None:
    """Keep all retained prices and apply only the declared national-CPI sensitivity."""
    assert len(inputs["retail"]) == 26
    assert any("OutOfStock" in r["availability"] for r in inputs["retail"])
    assert inputs["cpi_percent_2026"] == 7.1
    row = next(r for r in rows if r["price_profile"] == "naheed_minimum")
    assert math.isclose(row["poultry_price_pkr_2025"], 1080 / 1.071)
    assert math.isclose(row["milk_price_pkr_per_litre_2025"], 360 / 1.071)
    assert row["price_observation_date"] == "2026-10-16"
    assert row["price_year"] == 2025


def test_capture_share_monotonicity_and_component_sum(rows: list[dict]) -> None:
    """Check linear fractional-share arithmetic and no double counting of components."""
    for row in rows:
        expected = row["poultry_capture_million_usd"] + row["milk_capture_million_usd"]
        assert math.isclose(row["combined_capture_million_usd"], expected)
        assert row["combined_capture_million_usd"] > row["milk_capture_million_usd"]
    selected = sorted(
        [
            r
            for r in rows
            if r["quantity_family"] == "FAO2023_fixed"
            and r["comparison_year"] == 2026
            and r["price_profile"] == "official_central_sensitivity"
        ],
        key=lambda r: r["capture_share"],
    )
    assert math.isclose(
        selected[-1]["combined_capture_million_usd"]
        / selected[0]["combined_capture_million_usd"],
        10,
    )


def test_synthetic_independent_unit_expansion() -> None:
    """Test tonne/kg, density and currency factors using independently expanded units."""
    kg = 10 * 1000 * 1000
    expected_usd_million = (kg / 1.04) * 200 / 250 / 1000000
    assert math.isclose(
        MODEL.value_check(10, 200, "milk_equivalent_kg", "PKR_per_litre", 250, 1.04),
        expected_usd_million,
    )


def test_generation_is_deterministic(inputs: dict, rows: list[dict]) -> None:
    """A repeated build must not change the grid or sampled assumptions."""
    assert MODEL.generate(inputs) == rows


def test_all_protected_input_hashes_still_match() -> None:
    """Retain exact reference rows and original raw-source bytes after calculations."""
    assert len(MODEL.checked_sources(WORKSPACE)) == 14
