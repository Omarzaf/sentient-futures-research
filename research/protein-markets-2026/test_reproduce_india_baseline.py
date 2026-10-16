"""Check source units, CPI alignment, missingness and person-weighted estimation."""

from __future__ import annotations

import calendar
import hashlib
import json
import math
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from fetch_india_cpi import fetch_cpi
from reproduce_india_baseline import (
    cpi_recipe,
    mapped_component,
    ratio_estimate,
    roster_meal_diagnostic,
    verify_cpi_capture,
)


def cpi_fixture() -> dict:
    """Make twelve survey months and one later reference month per sector."""
    rows = []
    for sector, index, reference in [("Rural", 100, 110), ("Urban", 200, 240)]:
        months = (
            [(2023, month) for month in range(8, 13)]
            + [(2024, month) for month in range(1, 8)]
            + [(2024, 12)]
        )
        rows.extend(
            {
                "baseyear": "2012",
                "year": year,
                "month": calendar.month_name[month],
                "state": "All India",
                "sector": sector,
                "group": "General",
                "subgroup": "General-Overall",
                "index": reference if (year, month) == (2024, 12) else index,
                "status": "F",
            }
            for year, month in months
        )
    return {"api_record_count": len(rows), "data": rows}


def test_cpi_reference_direction_and_sector_are_fixed() -> None:
    """Higher later prices raise nutrients per survey rupee, independently by sector."""
    recipe, selected = cpi_recipe(cpi_fixture())
    assert recipe["sectors"]["rural"]["coefficient_multiplier"] == pytest.approx(1.1)
    assert recipe["sectors"]["urban"]["coefficient_multiplier"] == pytest.approx(1.2)
    assert recipe["sectors"]["rural"]["survey_months"] == 12
    assert len(selected) == 26


def test_cpi_cannot_drop_a_month_or_use_provisional_data() -> None:
    """Incomplete periods and provisional observations cannot silently pass."""
    data = cpi_fixture()
    data["data"].pop()
    data["api_record_count"] -= 1
    with pytest.raises(ValueError, match="Missing"):
        cpi_recipe(data)
    data = cpi_fixture()
    data["data"][0]["status"] = "P"
    with pytest.raises(ValueError, match="final"):
        cpi_recipe(data)


def test_cpi_duplicate_series_and_wrong_base_fail() -> None:
    """Duplicate observations and a rebased series are not compatible inputs."""
    data = cpi_fixture()
    data["data"].append(data["data"][0])
    data["api_record_count"] += 1
    with pytest.raises(ValueError, match="Ambiguous"):
        cpi_recipe(data)
    data = cpi_fixture()
    data["data"][0]["baseyear"] = "2024"
    with pytest.raises(ValueError, match="2012"):
        cpi_recipe(data)


def test_decimal_quantities_and_distinct_recalls(tmp_path: Path) -> None:
    """Use literal decimal kg and source30/7-day recalls, not another /1000."""
    path = tmp_path / "level05.parquet"
    pq.write_table(
        pa.table(
            {
                "hhid": [1, 1, 1],
                "item_code": [61, 3, 129],
                "cons_total_qty": [0.125, 0.2, 100.0],
            }
        ),
        path,
    )
    factors = pd.DataFrame(
        [
            {
                "item_code": 61,
                "unit": "kg.",
                "sector": "all",
                "protein_g_per_unit": 79.4,
            },
            {
                "item_code": 3,
                "unit": "kg.",
                "sector": "all",
                "protein_g_per_unit": 130.0,
            },
        ]
    )
    result, quality = mapped_component(path, factors, "05", False)
    assert result["physical"].iloc[0] == pytest.approx(
        0.125 * 79.4 / 30 + 0.2 * 130 / 7
    )
    assert quality["rows"] == 2


def test_monetary_values_use_sector_coefficients_not_quantity(tmp_path: Path) -> None:
    """An expenditure-only source record yields both separate sector conversions."""
    path = tmp_path / "money.parquet"
    pq.write_table(
        pa.table({"hhid": [1], "item_code": [166], "cons_total_value": [70.0]}), path
    )
    factors = pd.DataFrame(
        [
            {
                "item_code": 166,
                "unit": "Re.",
                "sector": "rural",
                "protein_g_per_unit": 0.13,
            },
            {
                "item_code": 166,
                "unit": "Re.",
                "sector": "urban",
                "protein_g_per_unit": 0.11,
            },
        ]
    )
    result, quality = mapped_component(path, factors, "05", True)
    assert result["monetary_rural"].iloc[0] == pytest.approx(1.3)
    assert result["monetary_urban"].iloc[0] == pytest.approx(1.1)
    assert quality["source_field"] == "cons_total_value"


def test_duplicate_food_keys_cannot_double_count(tmp_path: Path) -> None:
    """Repeated household-item rows are an input failure even when values are valid."""
    path = tmp_path / "duplicates.parquet"
    pq.write_table(
        pa.table({"hhid": [1, 1], "item_code": [61, 61], "cons_total_qty": [0.5, 0.5]}),
        path,
    )
    factors = pd.DataFrame(
        [{"item_code": 61, "unit": "kg.", "sector": "all", "protein_g_per_unit": 79.4}]
    )
    with pytest.raises(ValueError, match="double count"):
        mapped_component(path, factors, "05", False)


@pytest.mark.parametrize("value", [None, -1.0, float("nan"), float("inf")])
def test_present_missing_or_negative_values_are_not_imputed(
    tmp_path: Path, value: float | None
) -> None:
    """A present invalid source value fails rather than becoming zero."""
    path = tmp_path / "missing.parquet"
    pq.write_table(
        pa.table(
            {
                "hhid": [1],
                "item_code": [166],
                "cons_total_value": pa.array([value], type=pa.float64()),
            }
        ),
        path,
    )
    factors = pd.DataFrame(
        [
            {
                "item_code": 166,
                "unit": "Re.",
                "sector": "rural",
                "protein_g_per_unit": 0.13,
            },
            {
                "item_code": 166,
                "unit": "Re.",
                "sector": "urban",
                "protein_g_per_unit": 0.11,
            },
        ]
    )
    with pytest.raises(ValueError, match="no imputation"):
        mapped_component(path, factors, "05", True)


def survey_fixture() -> pd.DataFrame:
    """Make a two-PSU stratified household sample with unequal household sizes."""
    return pd.DataFrame(
        {
            "protein": [10.0, 80.0],
            "hh_size": [1.0, 4.0],
            "final_weight": [1.0, 1.0],
            "sector": [1, 1],
            "state": [1, 1],
            "stratum": [1, 1],
            "sub_stratum": [1, 1],
            "fsu_serial_no": [10, 20],
            "panel": [1, 2],
            "subsample": [1, 2],
        }
    )


def test_ratio_uses_person_denominator_and_psu_linearization() -> None:
    """Person ratio18 differs from the unweighted household mean15."""
    result = ratio_estimate(survey_fixture(), "protein")
    assert result["estimate_g_person_day"] == pytest.approx(18)
    assert result["approximate_WR_cluster_SE"] == pytest.approx(3.2)
    assert result["PSUs"] == 2


def test_weight_rescaling_leaves_estimate_and_se_unchanged() -> None:
    """Multiplier normalization cannot alter a ratio or its linearized SE."""
    data = survey_fixture()
    first = ratio_estimate(data, "protein")
    second = ratio_estimate(
        data.assign(final_weight=data["final_weight"] * 100), "protein"
    )
    assert first["estimate_g_person_day"] == second["estimate_g_person_day"]
    assert first["approximate_WR_cluster_SE"] == pytest.approx(
        second["approximate_WR_cluster_SE"]
    )


def test_singleton_strata_do_not_get_zero_variance() -> None:
    """Without a defensible singleton rule, preserve an unavailable SE."""
    data = survey_fixture().assign(stratum=[1, 2])
    result = ratio_estimate(data, "protein")
    assert math.isfinite(result["estimate_g_person_day"])
    assert result["singleton_strata"] == 2
    assert result["approximate_WR_cluster_SE"] is None


def test_roster_diagnostic_replaces_meals_once_and_preserves_null_limits() -> None:
    """Observed X replaces food-item meals once while all-missing persons stay unknown."""
    household = survey_fixture().assign(
        sector_name="rural", general=[100.0, 200.0], food_and_beverages=[105.0, 205.0]
    )
    household["hhid"] = [1, 2]
    # A third urban domain is needed because the production contract reports both.
    urban = household.iloc[[0]].assign(hhid=3, sector=2, sector_name="urban")
    household = pd.concat([household, urban], ignore_index=True)
    roster = pd.DataFrame(
        {
            "hhid": [1, 2, 3],
            "person_id": [1, 1, 1],
            "meals_school": [30.0, None, 0.0],
            "meals_employer": [None, None, 0.0],
            "meals_others": [None, None, 0.0],
            "meals_payment": [None, None, 0.0],
        }
    )
    meals = pd.DataFrame({"hhid": [1, 2, 3], "physical": [10.0, 20.0, 10.0]})
    result = roster_meal_diagnostic(
        household, roster, meals, {"rural": 61.8, "urban": 63.4}
    )
    assert result["sector_results"]["rural"]["variants"]["general"][
        "estimate_g_person_day"
    ] == pytest.approx((100 + 200 - 10 - 20 + 25) / 5)
    assert (
        result["sector_results"]["urban"]["variants"]["general"][
            "estimate_g_person_day"
        ]
        == 90.0
    )
    assert result["households_without_any_observed_away_meal_cell"] == 1
    assert result["strict_complete_away_meal_households"] == 1
    assert result["missing_away_meal_person_cells"] == 7
    assert result["source_defined_method"] is False
    assert result["complete_unadjusted_estimator"] is False


def test_cpi_page_binding_rejects_tampering_and_incomplete_pagination(
    tmp_path: Path,
) -> None:
    """A computed input cannot silently differ from the captured API response pages."""
    raw = tmp_path / "raw"
    raw.mkdir()
    path = raw / "cpi-page-01.json"
    page = {
        "statusCode": True,
        "meta_data": {"totalRecords": 1, "totalPages": 1},
        "data": [{"index": 100}],
    }
    path.write_text(json.dumps(page))
    payload = {
        "data": page["data"],
        "api_record_count": 1,
        "source_pages": [
            {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        ],
    }
    verify_cpi_capture(payload, tmp_path / "cpi-data.json")
    payload["data"] = [{"index": 999}]
    with pytest.raises(ValueError, match="differs"):
        verify_cpi_capture(payload, tmp_path / "cpi-data.json")
    payload["data"] = page["data"]
    path.write_text(
        json.dumps({**page, "meta_data": {"totalRecords": 2, "totalPages": 2}})
    )
    with pytest.raises(ValueError, match="identity"):
        verify_cpi_capture(payload, tmp_path / "cpi-data.json")


def test_cpi_cannot_accept_infinite_indices() -> None:
    """An infinite index must fail before coefficient calculation."""
    data = cpi_fixture()
    data["data"][0]["index"] = float("inf")
    with pytest.raises(ValueError, match="invalid"):
        cpi_recipe(data)


def test_cpi_fetch_refuses_to_overwrite_captured_sources(tmp_path: Path) -> None:
    """Reacquisition requires a new directory and never overwrites raw evidence."""
    path = tmp_path / "cpi-data.json"
    path.write_text("existing capture")
    with pytest.raises(FileExistsError, match="Preserve"):
        fetch_cpi(tmp_path)
    assert path.read_text() == "existing capture"
