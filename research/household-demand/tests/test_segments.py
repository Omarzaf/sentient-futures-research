"""Tests for the vegetarian and addressable segments."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import segments as sg

MEAT = ("chicken", "mutton", "beef_buffalo", "fish", "pork", "eggs")
NAN = np.nan


def _row(hhid, state, sector, weight, religion, caste, packaged, meat=None, **extra):
    """Build one household row; ``meat`` maps group to a positive quantity."""
    row = {
        "hhid": hhid,
        "state": state,
        "sector": sector,
        "multiplier": float(weight),
        "religion": religion,
        "caste": caste,
        "currency": "INR",
        "value_month_packaged": packaged,
        "value_month_milk": 100.0,
        "value_month_paneer": 20.0,
        "value_month_pulses": 80.0,
        "value_month_soya": 5.0,
        "value_month_meals_out": 0.0,
    }
    for group in MEAT:
        qty = (meat or {}).get(group, NAN)
        row[f"qty_month_{group}"] = qty
        row[f"value_month_{group}"] = NAN if pd.isna(qty) else 100.0 * qty
    row.update(extra)
    return row


@pytest.fixture
def india_fixture() -> pd.DataFrame:
    """Cell (7, 1, 9): 10 households of weight 10, 6 zero-recall, urban and rural mix.

    Zero-recall households differ in meals-out spending so the ranking is
    unambiguous. Cell (8, 2, 3) has 4 households and no NFHS row.
    """
    rows = []
    for i in range(10):
        zero = i < 6
        rows.append(
            _row(
                f"a{i}",
                7,
                2 if i % 2 == 0 else 1,
                10,
                1,
                9,
                packaged=50.0 if i % 3 else NAN,
                meat=None if zero else {"chicken": 2.0},
                value_month_meals_out=10.0 * i,
            )
        )
    rows += [
        _row("b0", 8, 2, 5, 2, 3, packaged=40.0, meat={"fish": 1.0}),
        _row("b1", 8, 2, 5, 2, 3, packaged=40.0),
        _row("b2", 8, 1, 5, 2, 3, packaged=NAN),
        _row("b3", 8, 2, 5, 2, 3, packaged=0.0),
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def nfhs_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {"state": [7], "religion": [1], "caste": [9], "never_eat_share": [0.30]}
    )


def test_zero_recall_fallback_labelled(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    assert set(out.segment_method) == {"ZERO_RECALL_DIAGNOSTIC"}


def test_nfhs_calibration_matches_weighted_share(india_fixture, nfhs_fixture):
    out = sg.assign_segments(india_fixture, nfhs=nfhs_fixture)
    cell = out[(out.state == 7) & (out.religion == 1) & (out.caste == 9)]
    share = (
        cell.multiplier * (cell.segment == "vegetarian")
    ).sum() / cell.multiplier.sum()
    assert abs(share - 0.30) < 0.01
    assert set(cell.segment_method) == {"NFHS5_CALIBRATED"}


def test_addressable_requires_urban_meat_and_packaged(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    a = out[out.addressable]
    assert (a.sector == 2).all() and (a.segment == "meat_eater").all()
    assert (a.value_month_packaged > 0).all()
    assert len(a) > 0


def test_addressable_vegetarian_requires_urban_vegetarian_and_packaged(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    v = out[out.addressable_vegetarian]
    assert len(v) > 0
    assert (v.sector == 2).all() and (v.segment == "vegetarian").all()
    assert (v.value_month_packaged > 0).all()
    assert not (out.addressable & out.addressable_vegetarian).any()


def test_zero_recall_rule_treats_nan_and_zero_alike(india_fixture):
    frame = india_fixture.iloc[:3].copy()
    frame.loc[frame.index[0], [f"qty_month_{g}" for g in MEAT]] = 0.0
    frame.loc[frame.index[1], [f"qty_month_{g}" for g in MEAT]] = NAN
    frame.loc[frame.index[2], "qty_month_fish"] = 0.5
    frame.loc[frame.index[2], "value_month_fish"] = 50.0
    out = sg.assign_segments(frame, nfhs=None)
    assert list(out.segment) == ["vegetarian", "vegetarian", "meat_eater"]


def test_partly_missing_meat_is_zero_recall_when_the_rest_is_zero(india_fixture):
    frame = india_fixture.iloc[:1].copy()
    frame["qty_month_chicken"] = 0.0
    frame["qty_month_fish"] = NAN
    assert sg.assign_segments(frame, nfhs=None).segment.iloc[0] == "vegetarian"


def test_value_without_quantity_counts_as_meat(india_fixture):
    frame = india_fixture.iloc[:1].copy()
    frame["value_month_chicken"] = 80.0
    frame["qty_month_chicken"] = NAN
    assert sg.assign_segments(frame, nfhs=None).segment.iloc[0] == "meat_eater"


def test_pakistan_is_all_meat_eater(india_fixture):
    frame = india_fixture.copy()
    frame["currency"] = "PKR"
    out = sg.assign_segments(frame, nfhs=None)
    assert set(out.segment) == {"meat_eater"}
    assert not out.addressable_vegetarian.any()
    assert set(out.segment_method) == {"ZERO_RECALL_DIAGNOSTIC"}


def test_pakistan_ignores_nfhs(india_fixture, nfhs_fixture):
    frame = india_fixture.copy()
    frame["currency"] = "PKR"
    out = sg.assign_segments(frame, nfhs=nfhs_fixture)
    assert set(out.segment) == {"meat_eater"}
    assert set(out.segment_method) == {"ZERO_RECALL_DIAGNOSTIC"}


def test_addressable_rule_full_when_packaged_present(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    assert set(out.addressable_rule) == {"FULL"}


def test_addressable_rule_drops_packaged_when_entirely_missing(india_fixture):
    frame = india_fixture.copy()
    frame["value_month_packaged"] = NAN
    out = sg.assign_segments(frame, nfhs=None)
    assert set(out.addressable_rule) == {"PACKAGED_CONDITION_DROPPED"}
    urban_meat = (out.sector == 2) & (out.segment == "meat_eater")
    assert (out.addressable == urban_meat).all()
    urban_veg = (out.sector == 2) & (out.segment == "vegetarian")
    assert (out.addressable_vegetarian == urban_veg).all()


def test_addressable_rule_is_decided_per_country(india_fixture):
    india = india_fixture.copy()
    pakistan = india_fixture.copy()
    pakistan["currency"] = "PKR"
    pakistan["hhid"] = "p" + pakistan["hhid"]
    pakistan["value_month_packaged"] = NAN
    out = sg.assign_segments(pd.concat([india, pakistan], ignore_index=True), nfhs=None)
    assert set(out[out.currency == "INR"].addressable_rule) == {"FULL"}
    assert set(out[out.currency == "PKR"].addressable_rule) == {
        "PACKAGED_CONDITION_DROPPED"
    }


def test_zero_packaged_is_not_addressable(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    b3 = out[out.hhid == "b3"].iloc[0]
    assert not b3.addressable and not b3.addressable_vegetarian


def test_input_is_not_modified(india_fixture):
    before = india_fixture.copy()
    sg.assign_segments(india_fixture, nfhs=None)
    pd.testing.assert_frame_equal(india_fixture, before)


def test_calibration_picks_households_with_highest_meat_free_score(
    india_fixture, nfhs_fixture
):
    out = sg.assign_segments(india_fixture, nfhs=nfhs_fixture)
    cell = out[(out.state == 7) & (out.religion == 1) & (out.caste == 9)]
    chosen = set(cell[cell.segment == "vegetarian"].hhid)
    zero_recall = cell[cell.hhid.isin([f"a{i}" for i in range(6)])]
    # Zero-recall households with the least meals-out spending rank highest.
    assert chosen == {"a0", "a1", "a2"}
    assert zero_recall.segment_method.eq("NFHS5_CALIBRATED").all()


def test_calibration_never_labels_a_meat_recall_household_vegetarian(india_fixture):
    nfhs = pd.DataFrame(
        {"state": [7], "religion": [1], "caste": [9], "never_eat_share": [0.95]}
    )
    out = sg.assign_segments(india_fixture, nfhs=nfhs)
    cell = out[(out.state == 7) & (out.religion == 1) & (out.caste == 9)]
    assert (
        cell[cell.hhid.isin([f"a{i}" for i in range(6, 10)])].segment == "meat_eater"
    ).all()
    report = sg.calibration_report(out, nfhs)
    row = report.iloc[0]
    assert row.target_share == pytest.approx(0.95)
    assert row.achieved_share == pytest.approx(0.60)
    assert row.shortfall == pytest.approx(0.35)


def test_cell_without_nfhs_row_keeps_zero_recall_label(india_fixture, nfhs_fixture):
    out = sg.assign_segments(india_fixture, nfhs=nfhs_fixture)
    other = out[out.state == 8]
    assert set(other.segment_method) == {"ZERO_RECALL_DIAGNOSTIC"}
    assert other.set_index("hhid").segment.to_dict() == {
        "b0": "meat_eater",
        "b1": "vegetarian",
        "b2": "vegetarian",
        "b3": "vegetarian",
    }


def test_missing_caste_cell_is_matched_by_missing_caste(india_fixture):
    frame = india_fixture.copy()
    frame["caste"] = pd.array([pd.NA] * len(frame), dtype="Int64")
    nfhs = pd.DataFrame(
        {
            "state": [7],
            "religion": [1],
            "caste": pd.array([pd.NA], dtype="Int64"),
            "never_eat_share": [0.30],
        }
    )
    out = sg.assign_segments(frame, nfhs=nfhs)
    cell = out[out.state == 7]
    assert set(cell.segment_method) == {"NFHS5_CALIBRATED"}
    share = (
        cell.multiplier * (cell.segment == "vegetarian")
    ).sum() / cell.multiplier.sum()
    assert abs(share - 0.30) < 0.01


def test_nfhs_with_missing_columns_raises(india_fixture):
    with pytest.raises(ValueError, match="never_eat_share"):
        sg.assign_segments(india_fixture, nfhs=pd.DataFrame({"state": [7]}))


def test_nfhs_share_outside_unit_interval_raises(india_fixture):
    nfhs = pd.DataFrame(
        {"state": [7], "religion": [1], "caste": [9], "never_eat_share": [1.4]}
    )
    with pytest.raises(ValueError, match="never_eat_share"):
        sg.assign_segments(india_fixture, nfhs=nfhs)


def test_nfhs_duplicate_cells_raise(india_fixture):
    nfhs = pd.DataFrame(
        {
            "state": [7, 7],
            "religion": [1, 1],
            "caste": [9, 9],
            "never_eat_share": [0.3, 0.4],
        }
    )
    with pytest.raises(ValueError, match="duplicate"):
        sg.assign_segments(india_fixture, nfhs=nfhs)


def test_missing_input_column_raises(india_fixture):
    with pytest.raises(ValueError, match="value_month_packaged"):
        sg.assign_segments(
            india_fixture.drop(columns="value_month_packaged"), nfhs=None
        )


def test_unknown_currency_raises(india_fixture):
    frame = india_fixture.copy()
    frame["currency"] = "USD"
    with pytest.raises(ValueError, match="currency"):
        sg.assign_segments(frame, nfhs=None)


def test_segment_summary_shares_and_suppression(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    summary = sg.segment_summary({"india": out}, min_households=5)
    national = summary["countries"]["india"]["national"]
    assert national["n_households"] == 14
    total = sum(out.multiplier)
    veg = out.multiplier[out.segment == "vegetarian"].sum() / total
    assert national["shares"]["vegetarian"] == pytest.approx(veg, abs=1e-4)
    assert national["shares"]["meat_eater"] == pytest.approx(1 - veg, abs=1e-4)
    states = summary["countries"]["india"]["states"]
    assert states["7"]["n_households"] == 10
    assert states["8"]["n_households"] == 4
    assert states["8"]["shares"] == {
        "meat_eater": None,
        "vegetarian": None,
        "addressable": None,
        "addressable_vegetarian": None,
    }
    assert states["8"]["n_vegetarian"] == 3
    assert states["7"]["shares"]["vegetarian"] is not None


def test_segment_summary_is_diagnostic_and_labelled(india_fixture):
    out = sg.assign_segments(india_fixture, nfhs=None)
    summary = sg.segment_summary({"india": out})
    assert summary["status"] == "DIAGNOSTIC"
    assert summary["min_cell_households"] == 30
    country = summary["countries"]["india"]
    assert country["segment_method"] == {"ZERO_RECALL_DIAGNOSTIC": 14}
    assert country["addressable_rule"] == "FULL"
    text = json.dumps(summary)
    assert "SYNTHETIC" not in text


def test_segment_summary_counts_placeholder_strata_without_the_token(india_fixture):
    frame = india_fixture.copy()
    frame["currency"] = "PKR"
    frame["stratum_status"] = ["SYNTH" + "ETIC"] * 3 + ["RESOLVED"] * (len(frame) - 3)
    out = sg.assign_segments(frame, nfhs=None)
    summary = sg.segment_summary({"pakistan": out})
    assert summary["countries"]["pakistan"]["placeholder_stratum_households"] == 3
    assert "SYNTHETIC" not in json.dumps(summary)


def test_main_writes_summary_without_household_rows(india_fixture, tmp_path: Path):
    india_path = tmp_path / "india.parquet"
    india_fixture.to_parquet(india_path, index=False)
    summary = tmp_path / "summary.json"
    assert sg.main(["--india", str(india_path), "--summary", str(summary)]) == 0
    payload = json.loads(summary.read_text())
    assert payload["status"] == "DIAGNOSTIC"
    assert set(payload["countries"]) == {"india"}
    assert "hhid" not in summary.read_text()


def test_main_refuses_household_rows_inside_repository(india_fixture, tmp_path: Path):
    india_path = tmp_path / "india.parquet"
    india_fixture.to_parquet(india_path, index=False)
    inside = sg.LIBRARY_ROOT / "research" / "household-demand" / "x.parquet"
    with pytest.raises(SystemExit):
        sg.main(
            [
                "--india",
                str(india_path),
                "--india-out",
                str(inside),
                "--summary",
                str(tmp_path / "summary.json"),
            ]
        )
    assert not inside.exists()


def _with_no_food_household(frame: pd.DataFrame, **overrides) -> pd.DataFrame:
    """Append household n0: same geography as the first row, every food column missing."""
    row = frame.iloc[0].copy()
    for column in frame.columns:
        if column.startswith(("value_month_", "qty_month_")):
            row[column] = NAN
    row["hhid"] = "n0"
    for key, value in overrides.items():
        row[key] = value
    return pd.concat([frame, row.to_frame().T], ignore_index=True).astype(
        frame.dtypes.to_dict()
    )


def test_household_without_food_data_has_null_segment(india_fixture):
    frame = _with_no_food_household(india_fixture)
    out = sg.assign_segments(frame, nfhs=None).set_index("hhid")
    row = out.loc["n0"]
    assert pd.isna(row.segment)
    assert row.segment_method == "NO_FOOD_DATA"
    assert not row.addressable and not row.addressable_vegetarian
    assert out.drop(index="n0").segment.notna().all()


def test_household_without_food_data_is_excluded_from_nfhs_cells(
    india_fixture, nfhs_fixture
):
    frame = _with_no_food_household(india_fixture, multiplier=50.0)
    out = sg.assign_segments(frame, nfhs=nfhs_fixture)
    cell = out[(out.state == 7) & out.segment.notna()]
    share = (
        cell.multiplier * (cell.segment == "vegetarian")
    ).sum() / cell.multiplier.sum()
    assert abs(share - 0.30) < 0.01
    assert out[out.hhid == "n0"].segment_method.iloc[0] == "NO_FOOD_DATA"


def test_household_without_food_data_is_pakistan_null_too(india_fixture):
    frame = _with_no_food_household(india_fixture, currency="PKR")
    frame["currency"] = "PKR"
    out = sg.assign_segments(frame, nfhs=None)
    assert out.segment.isna().sum() == 1
    assert set(out.segment.dropna()) == {"meat_eater"}


def test_summary_excludes_households_without_food_data(india_fixture):
    base = sg.segment_summary(
        {"india": sg.assign_segments(india_fixture, nfhs=None)}, min_households=5
    )
    frame = _with_no_food_household(india_fixture, multiplier=500.0)
    summary = sg.segment_summary(
        {"india": sg.assign_segments(frame, nfhs=None)}, min_households=5
    )
    country = summary["countries"]["india"]
    assert country["households"] == 15
    assert country["no_food_data_households"] == 1
    assert country["segment_method"] == {
        "NO_FOOD_DATA": 1,
        "ZERO_RECALL_DIAGNOSTIC": 14,
    }
    national = country["national"]
    assert national["n_households"] == 15
    assert national["no_food_data_households"] == 1
    base_shares = base["countries"]["india"]["national"]["shares"]
    assert national["shares"] == base_shares
    assert national["shares"]["meat_eater"] + national["shares"]["vegetarian"] == (
        pytest.approx(1.0, abs=1e-4)
    )
    assert country["states"]["7"]["no_food_data_households"] == 1
    assert country["states"]["8"]["no_food_data_households"] == 0
