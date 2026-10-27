"""Tests for the India household protein table built from HCES 2023-24."""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import codes
import households_india as hi
import pandas as pd
import pytest

# Tests from the Task 2 brief, kept verbatim.


def test_mpce_follows_methodology(fixture_dir):
    df = hi.build_india_households(fixture_dir)
    row = df.set_index("hhid").loc["H1"]
    # fixture: E1=3000, E2=900 over P2=1, E3=600 over P3=1, P1=3 persons
    assert row.mpce_inr == (3000 + 900 * 3 + 600 * 3) / 3


def test_seven_day_recall_scaled_to_month(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H1", "qty_month_chicken"] == 0.5 * 30 / 7


def test_thirty_day_recall_not_rescaled(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H1", "qty_month_pulses"] == 2.0


def test_value_without_quantity_gives_missing_unit_value(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert math.isnan(df.loc["H2", "unit_value_mutton"])


def test_source_rows_not_double_counted(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    # H3 has home and purchased rows for eggs; cons_total already includes both
    assert df.loc["H3", "qty_month_eggs"] == 12 * 30 / 7


def test_absent_item_stays_missing(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert math.isnan(df.loc["H4", "qty_month_fish"])


# Additional tests: data facts that differ from the brief, schema and fail-closed checks.


def test_one_row_per_household_with_schema(fixture_dir):
    df = hi.build_india_households(fixture_dir)
    assert sorted(df["hhid"]) == ["H1", "H2", "H3", "H4", "H5", "H6"]
    expected = list(hi.BASE_COLUMNS) + [
        f"{kind}_{group}" for group in codes.GROUPS for kind in hi.GROUP_KINDS
    ]
    assert list(df.columns) == expected


def test_design_and_currency_columns(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H1", "psu"] == 10001
    assert df.loc["H3", "stratum"] == 2
    assert set(df["stratum_status"]) == {"RESOLVED"}
    assert set(df["currency"]) == {"INR"}
    assert df["mpce_local"].equals(df["mpce_inr"])
    assert "mpce_status" in hi.BASE_COLUMNS


def test_mpce_scales_recall_and_excludes_imputed_rent(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    # H2: E1 = 1400 (30-day) + 700 * 30 / 7 (7-day); E2 = 600, imputed rent 539 left out.
    assert df.loc["H2", "mpce_inr"] == (1400 + 700 * 30 / 7 + 600) / 2


def test_soya_uses_thirty_day_recall(fixture_dir):
    # Questionnaire FDQ section 5.2 lists item 152 under the 30-day pulses block.
    assert codes.RECALL_DAYS["soya"] == 30
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H6", "qty_month_soya"] == 0.5


def test_missing_quantity_gives_missing_quantity_and_unit_value(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert math.isnan(df.loc["H5", "qty_month_beef_buffalo"])
    assert math.isnan(df.loc["H5", "unit_value_beef_buffalo"])
    assert df.loc["H5", "value_month_beef_buffalo"] == 200 * 30 / 7


def test_meal_unit_value_uses_counted_meals_only(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H5", "qty_month_meals_out"] == 2 * 30 / 7
    assert df.loc["H5", "value_month_meals_out"] == 250 * 30 / 7
    assert df.loc["H5", "unit_value_meals_out"] == 100.0


def test_packaged_food_has_value_only(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H5", "value_month_packaged"] == 80 * 30 / 7
    assert math.isnan(df.loc["H5", "qty_month_packaged"])
    assert math.isnan(df.loc["H5", "unit_value_packaged"])


def test_unit_value_is_value_per_quantity(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H6", "unit_value_paneer"] == 400.0
    assert df.loc["H1", "unit_value_pulses"] == 105.0


def test_not_reported_codes_become_missing(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert pd.isna(df.loc["H6", "religion"])
    assert pd.isna(df.loc["H6", "caste"])
    assert df.loc["H5", "religion"] == 3


def test_duplicate_household_item_rows_raise(fixture_dir, tmp_path: Path):
    copy = tmp_path / "hces"
    shutil.copytree(fixture_dir, copy)
    items = pd.read_parquet(copy / "level_05.parquet")
    pd.concat([items, items.iloc[[4]]]).to_parquet(
        copy / "level_05.parquet", index=False
    )
    with pytest.raises(ValueError, match="double count"):
        hi.build_india_households(copy)


def test_incomplete_questionnaires_raise(fixture_dir, tmp_path: Path):
    copy = tmp_path / "hces"
    shutil.copytree(fixture_dir, copy)
    visits = pd.read_parquet(copy / "level_15.parquet")
    keep = ~((visits["hhid"] == "H4") & (visits["questionnaire_num"] == "D"))
    visits.loc[keep].to_parquet(copy / "level_15.parquet", index=False)
    with pytest.raises(ValueError, match="questionnaire"):
        hi.build_india_households(copy)


def test_negative_value_raises(fixture_dir, tmp_path: Path):
    copy = tmp_path / "hces"
    shutil.copytree(fixture_dir, copy)
    items = pd.read_parquet(copy / "level_05.parquet")
    items.loc[0, "cons_total_value"] = -1.0
    items.to_parquet(copy / "level_05.parquet", index=False)
    with pytest.raises(ValueError, match="negative"):
        hi.build_india_households(copy)


def test_protein_factors_carry_sources():
    assert set(codes.PROTEIN_G_PER_KG) == set(codes.GROUPS)
    assert set(codes.PROTEIN_SOURCE) == set(codes.GROUPS)
    assert codes.PROTEIN_G_PER_KG["chicken"] == 259.0
    assert math.isnan(codes.PROTEIN_G_PER_KG["packaged"])
    assert all(codes.PROTEIN_SOURCE[group] for group in codes.GROUPS)


def test_state_summary_is_diagnostic_state_means(fixture_dir):
    df = hi.build_india_households(fixture_dir)
    summary = hi.state_summary(df, min_households=1)
    assert summary["status"] == "DIAGNOSTIC"
    assert set(summary["states"]) == {"9", "27"}
    state_9 = summary["states"]["9"]
    # Person-weighted MPCE: H1 (w 1000, 3 persons), H2 (2000, 2), H3 (1500, 4).
    mpce = df.set_index("hhid")["mpce_inr"]
    expected = (
        mpce["H1"] * 1000 * 3 + mpce["H2"] * 2000 * 2 + mpce["H3"] * 1500 * 4
    ) / (1000 * 3 + 2000 * 2 + 1500 * 4)
    assert state_9["mean_mpce_inr"] == pytest.approx(expected)
    assert state_9["n_mpce"] == 3
    # State 27: H4 has missing MPCE, so only H5 (3000, 1) and H6 (1000, 2) enter.
    expected_27 = (mpce["H5"] * 3000 * 1 + mpce["H6"] * 1000 * 2) / (3000 + 2000)
    assert summary["states"]["27"]["mean_mpce_inr"] == pytest.approx(expected_27)
    assert summary["states"]["27"]["n_mpce"] == 2
    # Chicken reported by H1 only in state 9: share 1000 / 4500.
    chicken = state_9["groups"]["chicken"]
    assert chicken["reporting_share"] == pytest.approx(1000 / 4500)
    assert chicken["n_reporting"] == 1
    text = json.dumps(summary)
    assert "S" + "YNTHETIC" not in text
    assert "H1" not in text


def test_state_summary_suppresses_cells_under_thirty_households(fixture_dir):
    df = hi.build_india_households(fixture_dir)
    summary = hi.state_summary(df)
    assert summary["min_cell_households"] == 30
    state_9 = summary["states"]["9"]
    assert state_9["mean_mpce_inr"] is None
    assert state_9["n_mpce"] == 3
    chicken = state_9["groups"]["chicken"]
    assert chicken["n_reporting"] == 1
    assert chicken["n_value"] == 1
    assert chicken["n_qty"] == 1
    assert chicken["n_unit_value"] == 1
    for key in (
        "reporting_share",
        "mean_value_month_inr_reporting",
        "mean_qty_month_reporting",
        "mean_unit_value_inr",
    ):
        assert chicken[key] is None


def test_unit_value_uses_purchased_quantity_and_value(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    # H3 eggs: total 12 for 72, home 5 for 40, purchase 7 for 32.
    assert df.loc["H3", "unit_value_eggs"] == 32 / 7
    assert df.loc["H3", "value_month_eggs"] == 72 * 30 / 7


def test_home_produce_only_gives_missing_unit_value(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert df.loc["H6", "qty_month_milk"] == 3.5 * 30 / 7
    assert math.isnan(df.loc["H6", "unit_value_milk"])


def test_pulses_unit_value_excludes_pds_and_free_items(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    # H6: 140 (1.0 kg, 120), PDS 158 (1.0 kg, 30), free 071 (0.5 kg, no value).
    assert df.loc["H6", "qty_month_pulses"] == 2.5
    assert df.loc["H6", "value_month_pulses"] == 150.0
    assert df.loc["H6", "unit_value_pulses"] == 120.0
    assert {71, 72} <= set(codes.GROUPS["pulses"])
    assert not {71, 72, 158} & set(codes.UNIT_VALUE_CODES["pulses"])


def test_home_above_total_raises(fixture_dir, tmp_path: Path):
    copy = tmp_path / "hces"
    shutil.copytree(fixture_dir, copy)
    items = pd.read_parquet(copy / "level_05.parquet")
    items.loc[items["item_code"].eq(190), "cons_home_qty"] = 13.0
    items.to_parquet(copy / "level_05.parquet", index=False)
    with pytest.raises(ValueError, match="home"):
        hi.build_india_households(copy)


def test_missing_fdq_summary_gives_missing_mpce(fixture_dir):
    df = hi.build_india_households(fixture_dir).set_index("hhid")
    assert math.isnan(df.loc["H4", "mpce_inr"])
    assert math.isnan(df.loc["H4", "mpce_local"])
    assert df.loc["H4", "mpce_status"] == "MISSING_FDQ"
    assert set(df.drop(index="H4")["mpce_status"]) == {"OK"}


def test_main_refuses_household_rows_inside_repository(fixture_dir, tmp_path: Path):
    inside = hi.LIBRARY_ROOT / "research" / "household-demand" / "x.parquet"
    with pytest.raises(SystemExit):
        hi.main(
            [
                "--clean-dir",
                str(fixture_dir),
                "--out",
                str(inside),
                "--summary",
                str(tmp_path / "summary.json"),
            ]
        )
    assert not inside.exists()
