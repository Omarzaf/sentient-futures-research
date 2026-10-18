"""Tests for the Pakistan household protein table built from HIES 2024-25."""

from __future__ import annotations

import io
import json
import math
import zipfile
from datetime import datetime
from pathlib import Path

import codes
import households_india as hi
import households_pakistan as hp
import pandas as pd
import pytest

# Tests from the Task 3 brief. The brief expected 3.0 for chicken; chicken sits
# in 14-day part A, so the monthly value is (2 + 1) * 26 / 12. The 3.0 case is
# kept for a monthly item in test_channels_summed_monthly_item.


def test_channels_summed(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[2, "qty_month_chicken"] == (2 + 1) * 26 / 12  # q1=2, q2=1


def test_meals_out_value_only(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert math.isnan(df.loc[1, "qty_month_meals_out"])
    assert df.loc[1, "value_month_meals_out"] > 0


def test_unresolved_stratum_flagged(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    assert set(df.stratum_status) <= {"RESOLVED", "SYNTHETIC"}
    assert (df.stratum_status == "SYNTHETIC").any()


def test_no_religion_invented(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    assert df.religion.isna().all()


# Additional tests: channel semantics, recall scaling, MPCE, schema, fail-closed checks.


def _rewrite(source: Path, target: Path, name: str, change) -> Path:
    """Copy the fixture ZIP, applying ``change`` to one Stata member."""
    with zipfile.ZipFile(source) as archive:
        members = {item: archive.read(item) for item in archive.namelist()}
    member = f"Stata data/{name}.dta"
    frame = pd.read_stata(io.BytesIO(members[member]), convert_categoricals=False)
    buffer = io.BytesIO()
    change(frame).to_stata(
        buffer, write_index=False, version=118, time_stamp=datetime(2026, 10, 18)
    )
    members[member] = buffer.getvalue()
    with zipfile.ZipFile(target, "w") as archive:
        for item, data in members.items():
            archive.writestr(item, data)
    return target


def test_channels_summed_monthly_item(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    # moong: paid 2 kg for 500 plus 1 kg gift for 250, monthly part B
    assert df.loc[2, "qty_month_pulses"] == 3.0
    assert df.loc[2, "value_month_pulses"] == 750.0


def test_unit_value_uses_paid_channel_only(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[2, "unit_value_chicken"] == 700.0
    assert df.loc[2, "unit_value_pulses"] == 250.0
    assert df.loc[2, "value_month_chicken"] == 2100 * 26 / 12
    # beef: paid 0.5 kg for 500 and own produced 1 kg for 1000
    assert df.loc[5, "unit_value_beef_buffalo"] == 1000.0
    assert df.loc[5, "qty_month_beef_buffalo"] == 1.5 * 26 / 12


def test_unpaid_only_gives_missing_unit_value(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[3, "qty_month_eggs"] == 10 * 26 / 12
    assert math.isnan(df.loc[3, "unit_value_eggs"])
    assert df.loc[5, "qty_month_pulses"] == 1.0
    assert math.isnan(df.loc[5, "unit_value_pulses"])


def test_value_without_quantity_gives_missing_quantity(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert math.isnan(df.loc[4, "qty_month_other_poultry"])
    assert math.isnan(df.loc[4, "unit_value_other_poultry"])
    assert df.loc[4, "value_month_other_poultry"] == 300 * 26 / 12


def test_absent_item_stays_missing(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert math.isnan(df.loc[4, "qty_month_mutton"])
    assert math.isnan(df.loc[4, "value_month_mutton"])
    assert df.loc[6, ["value_month_chicken", "value_month_pulses"]].isna().all()


def test_part_a_scaled_and_part_b_not(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[3, "qty_month_milk"] == 7 * 26 / 12
    assert df.loc[3, "unit_value_milk"] == 200.0
    assert df.loc[1, "qty_month_pulses"] == 2.0
    assert df.loc[1, "value_month_meals_out"] == 500.0


def test_packaged_value_only_with_item_recall(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    # biscuits 300 (part B, monthly) and chocolate 140 (part A, 14 days)
    assert df.loc[3, "value_month_packaged"] == 300 + 140 * 26 / 12
    assert math.isnan(df.loc[3, "qty_month_packaged"])
    assert math.isnan(df.loc[3, "unit_value_packaged"])
    assert {11116, 11804} <= set(codes.PK_GROUPS["packaged"])


def test_groups_not_collected_stay_missing(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    for group in codes.PK_NOT_COLLECTED:
        assert codes.PK_GROUPS[group] == ()
        for kind in hi.GROUP_KINDS:
            assert df[f"{kind}_{group}"].isna().all()
    assert set(codes.PK_NOT_COLLECTED) == {"pork", "paneer", "soya"}


def test_mpce_sums_parts_a_to_d_without_totals_or_durables(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    # hh 1: chicken 700 (A) + dal 600 + meals 500 (B); part totals 1000, 2000 left out
    assert df.loc[1, "mpce_pkr"] == pytest.approx((700 * 26 / 12 + 600 + 500) / 2)
    # hh 4: A 650 + 300, C 3000 monthly, D 12000 yearly; E 24000 durable left out
    expected = (950 * 26 / 12 + 3000 + 12000 / 12) / 5
    assert df.loc[4, "mpce_pkr"] == pytest.approx(expected)
    assert df["mpce_local"].equals(df["mpce_pkr"])
    assert set(df["currency"]) == {"PKR"}


def test_household_without_consumption_rows_gets_missing_mpce(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert math.isnan(df.loc[6, "mpce_pkr"])
    assert df.loc[6, "mpce_status"] == "MISSING_EXPENDITURE"
    assert set(df.drop(index=6)["mpce_status"]) == {"OK"}


def test_household_size_counts_members_only(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[1, "hh_size"] == 2
    assert df.loc[5, "hh_size"] == 6


def test_schema_matches_india_groups(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    assert sorted(df["hhid"]) == [1, 2, 3, 4, 5, 6]
    expected = list(hp.BASE_COLUMNS) + [
        f"{kind}_{group}" for group in codes.PK_GROUPS for kind in hi.GROUP_KINDS
    ]
    assert list(df.columns) == expected
    assert list(codes.PK_GROUPS)[: len(codes.GROUPS)] == list(codes.GROUPS)
    shared = set(hi.BASE_COLUMNS) - {"mpce_inr"}
    assert shared <= set(hp.BASE_COLUMNS)
    assert {"mpce_pkr", "province", "region", "prcode"} <= set(hp.BASE_COLUMNS)


def test_geography_and_design_columns(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[4, "state"] == 3 and df.loc[4, "province"] == 3
    assert df.loc[4, "sector"] == 2 and df.loc[4, "region"] == 2
    assert df.loc[1, "psu"] == 25111001 and df.loc[1, "prcode"] == 25111001
    assert df.loc[1, "district"] == 251
    assert pd.isna(df.loc[3, "district"])
    assert df.loc[3, "multiplier"] == 500.0
    assert df["caste"].isna().all()


def test_placeholder_strata_from_csv(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    strata = pd.read_csv(hp.STRATA_PATH)
    assert set(strata["status"]) == {"S" + "YNTHETIC"}
    assert not strata.duplicated(["geo_code", "region"]).any()
    row = strata.loc[strata["geo_code"].eq(251) & strata["region"].eq(1)].iloc[0]
    assert df.loc[1, "stratum"] == row["stratum"]
    assert df.loc[1, "stratum"] == df.loc[2, "stratum"]
    assert df.loc[1, "stratum"] != df.loc[3, "stratum"]


def test_official_stratum_mapping_marks_resolved(pk_fixture, monkeypatch):
    monkeypatch.setattr(codes, "PK_OFFICIAL_STRATA", {(251, 1): "official-251-1"})
    df = hp.build_pakistan_households(pk_fixture).set_index("hhid")
    assert df.loc[1, "stratum_status"] == "RESOLVED"
    assert df.loc[1, "stratum"] == "official-251-1"
    assert df.loc[3, "stratum_status"] == "SYNTHETIC"


def test_psu_outside_strata_csv_raises(pk_fixture, tmp_path: Path):
    def move(frame):
        frame.loc[frame["hhcode"].eq(6), "prcode"] = 99911001
        return frame

    copy = _rewrite(pk_fixture, tmp_path / "a.zip", "section_info", move)
    copy = _rewrite(
        copy,
        tmp_path / "b.zip",
        "weight",
        lambda w: w.assign(prcode=w["prcode"].replace({41111001: 99911001})),
    )
    with pytest.raises(ValueError, match="strata"):
        hp.build_pakistan_households(copy)


def test_duplicate_household_item_rows_raise(pk_fixture, tmp_path: Path):
    copy = _rewrite(
        pk_fixture,
        tmp_path / "dup.zip",
        "sec_6a_consum_exp",
        lambda f: pd.concat([f, f.iloc[[0]]]),
    )
    with pytest.raises(ValueError, match="double count"):
        hp.build_pakistan_households(copy)


def test_missing_weight_raises(pk_fixture, tmp_path: Path):
    copy = _rewrite(
        pk_fixture,
        tmp_path / "w.zip",
        "weight",
        lambda w: w.loc[w["prcode"].ne(41111001)],
    )
    with pytest.raises(ValueError, match="weight"):
        hp.build_pakistan_households(copy)


def test_unknown_item_code_raises(pk_fixture, tmp_path: Path):
    def add(frame):
        extra = frame.iloc[[0]].assign(itc=99999)
        return pd.concat([frame, extra])

    copy = _rewrite(pk_fixture, tmp_path / "u.zip", "sec_6a_consum_exp", add)
    with pytest.raises(ValueError, match="recall"):
        hp.build_pakistan_households(copy)


def test_negative_value_raises(pk_fixture, tmp_path: Path):
    def negate(frame):
        frame.loc[frame.index[0], "v1"] = -1.0
        return frame

    copy = _rewrite(pk_fixture, tmp_path / "n.zip", "sec_6a_consum_exp", negate)
    with pytest.raises(ValueError, match="negative"):
        hp.build_pakistan_households(copy)


def test_row_without_value_raises(pk_fixture, tmp_path: Path):
    def blank(frame):
        frame.loc[frame.index[0], ["q1", "v1"]] = float("nan")
        return frame

    copy = _rewrite(pk_fixture, tmp_path / "b.zip", "sec_6a_consum_exp", blank)
    with pytest.raises(ValueError, match="complete value"):
        hp.build_pakistan_households(copy)


def test_every_item_code_has_one_part():
    parts = [set(codes.PK_PART_ITEMS[part]) for part in codes.PK_PART_ITEMS]
    union = set().union(*parts)
    assert sum(len(p) for p in parts) == len(union)
    for group, items in codes.PK_GROUPS.items():
        assert set(items) <= union, group
    assert codes.pk_monthly_factor(11203) == (26, 12)
    assert codes.pk_monthly_factor(11110) == (12, 12)
    assert codes.pk_monthly_factor(31201) == (1, 12)
    with pytest.raises(ValueError, match="recall"):
        codes.pk_monthly_factor(1000)


def test_province_summary_counts_placeholders_without_flag(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    summary = hp.province_summary(df, min_households=1)
    assert summary["status"] == "DIAGNOSTIC"
    assert summary["households"] == 6
    assert summary["psus"] == 5
    assert summary["placeholder_stratum_households"] == 6
    assert set(summary["provinces"]) == {"1", "2", "3", "4"}
    punjab = summary["provinces"]["2"]
    # Punjab: hh 1 (w 1000, 2 persons), 2 (1000, 4), 3 (500, 3)
    mpce = df.set_index("hhid")["mpce_pkr"]
    expected = (mpce[1] * 1000 * 2 + mpce[2] * 1000 * 4 + mpce[3] * 500 * 3) / (
        1000 * 2 + 1000 * 4 + 500 * 3
    )
    assert punjab["mean_mpce_pkr"] == pytest.approx(expected)
    chicken = punjab["groups"]["chicken"]
    assert chicken["n_reporting"] == 2
    assert chicken["reporting_share"] == pytest.approx(2000 / 2500)
    text = json.dumps(summary)
    assert "S" + "YNTHETIC" not in text


def test_province_summary_suppresses_cells_under_thirty(pk_fixture):
    df = hp.build_pakistan_households(pk_fixture)
    summary = hp.province_summary(df)
    punjab = summary["provinces"]["2"]
    assert summary["min_cell_households"] == 30
    assert punjab["mean_mpce_pkr"] is None
    assert punjab["n_mpce"] == 3
    chicken = punjab["groups"]["chicken"]
    assert chicken["n_value"] == 2
    assert chicken["mean_value_month_pkr_reporting"] is None
    assert chicken["reporting_share"] is None


def test_main_refuses_household_rows_inside_repository(pk_fixture, tmp_path: Path):
    inside = hp.LIBRARY_ROOT / "research" / "household-demand" / "x.parquet"
    with pytest.raises(SystemExit):
        hp.main(
            [
                "--zip",
                str(pk_fixture),
                "--out",
                str(inside),
                "--summary",
                str(tmp_path / "summary.json"),
            ]
        )
    assert not inside.exists()
