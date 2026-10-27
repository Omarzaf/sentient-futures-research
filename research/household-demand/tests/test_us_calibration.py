"""Tests for the US intent-to-purchase calibration."""

from __future__ import annotations

import json

import pandas as pd
import pytest
import us_calibration as us


def test_conversion_and_spend():
    c = us.calibrate(
        us_households=130_000_000, penetration=0.15, intent_share=0.40, sales_usd=7.9e9
    )
    assert c.conversion == 0.15 / 0.40
    assert round(c.spend_per_adopter_usd, 2) == round(7.9e9 / (130e6 * 0.15), 2)


def test_rejects_penetration_above_intent():
    with pytest.raises(ValueError):
        us.calibrate(130_000_000, penetration=0.5, intent_share=0.4, sales_usd=7.9e9)


def test_addressable_share_scales_penetration_within_segment():
    c = us.calibrate(
        130_000_000,
        penetration=0.11,
        intent_share=0.329,
        sales_usd=1.0e9,
        addressable_share=0.5,
    )
    assert c.conversion == pytest.approx((0.11 / 0.5) / 0.329)
    assert c.spend_per_adopter_usd == pytest.approx(1.0e9 / (130e6 * 0.11))
    assert c.addressable_share == 0.5


def test_addressable_penetration_capped_at_one():
    c = us.calibrate(
        130_000_000,
        penetration=0.6,
        intent_share=1.0,
        sales_usd=1.0e9,
        addressable_share=0.5,
    )
    assert c.conversion == 1.0


def test_rejects_conversion_above_one_after_segment_scaling():
    with pytest.raises(ValueError):
        us.calibrate(
            130_000_000,
            penetration=0.2,
            intent_share=0.3,
            sales_usd=1.0e9,
            addressable_share=0.5,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("us_households", 0),
        ("penetration", 0.0),
        ("penetration", 1.2),
        ("intent_share", 0.0),
        ("sales_usd", -1.0),
        ("addressable_share", 0.0),
        ("addressable_share", 1.5),
        ("penetration", float("nan")),
    ],
)
def test_rejects_out_of_range_inputs(field, value):
    args = {
        "us_households": 130_000_000,
        "penetration": 0.1,
        "intent_share": 0.4,
        "sales_usd": 1.0e9,
        "addressable_share": 1.0,
    }
    args[field] = value
    with pytest.raises(ValueError):
        us.calibrate(**args)


def _diary(rows, foodtot=None):
    """Build an FMLD-shaped frame from (weight, urban code, meat, miscfood) tuples.

    ``foodtot`` defaults to 10 dollars per diary week.
    """
    frame = pd.DataFrame(rows, columns=["FINLWT21", "BLS_URBN", "meat", "MISCFOOD"])
    for column in us.CE_MEAT_VARIABLES:
        frame[column] = 0.0
    frame["POULTRY"] = frame.pop("meat")
    frame["FOODTOT"] = foodtot if foodtot is not None else [10.0] * len(frame)
    frame["quarter_file"] = ["fmld231.csv"] * 2 + ["fmld232.csv"] * (len(frame) - 2)
    return frame


def test_ce_summary_counts_weighted_households_and_addressable_share():
    frame = _diary(
        [
            (100.0, 1, 5.0, 2.0),  # urban, meat, packaged: addressable
            (100.0, 2, 5.0, 2.0),  # rural
            (50.0, 1, 0.0, 2.0),  # no meat
            (150.0, 1, 5.0, 0.0),  # no packaged food
        ]
    )
    summary = us.ce_summary(frame)
    # quarter 231 sums to 200, quarter 232 sums to 200: mean 200 households
    assert summary["us_households"] == 200
    assert summary["addressable_share"] == pytest.approx(100 / 400)
    assert summary["urban_share"] == pytest.approx(300 / 400)
    assert summary["meat_share"] == pytest.approx(350 / 400)
    assert summary["packaged_share"] == pytest.approx(250 / 400)
    assert summary["us_urban_packaged_share"] == pytest.approx(150 / 400)
    assert summary["n_records"] == 4


def test_ce_summary_excludes_zero_food_weeks_from_share_denominators():
    frame = _diary(
        [
            (100.0, 1, 5.0, 2.0),  # addressable
            (100.0, 1, 0.0, 0.0),  # no food at all this week
            (100.0, 1, 0.0, 2.0),  # urban, packaged, no meat
            (200.0, 2, 5.0, 2.0),  # rural
        ],
        foodtot=[10.0, 0.0, 10.0, 10.0],
    )
    summary = us.ce_summary(frame)
    # the zero-food week still counts in the CU total: (100 + 100 + 100 + 200) / 2
    assert summary["us_households"] == 250
    assert summary["addressable_share"] == pytest.approx(100 / 400)
    assert summary["us_urban_packaged_share"] == pytest.approx(200 / 400)
    assert summary["addressable_share_including_zero_food_weeks"] == pytest.approx(
        100 / 500
    )
    assert summary[
        "us_urban_packaged_share_including_zero_food_weeks"
    ] == pytest.approx(200 / 500)
    assert summary["n_zero_food_records"] == 1
    assert summary["zero_food_share"] == pytest.approx(100 / 500)


def test_ce_summary_rejects_missing_foodtot():
    frame = _diary([(100.0, 1, 5.0, 2.0), (100.0, 1, 5.0, 2.0)], foodtot=[1.0, None])
    with pytest.raises(ValueError):
        us.ce_summary(frame)


def test_ce_summary_rejects_unknown_urban_code():
    frame = _diary([(100.0, 3, 5.0, 2.0), (100.0, 1, 5.0, 2.0), (1.0, 1, 0.0, 0.0)])
    with pytest.raises(ValueError):
        us.ce_summary(frame)


def test_ucc_check_matches_summary_variables():
    fmld = pd.DataFrame(
        {
            "NEWID": ["a", "b"],
            **{column: [0.0, 0.0] for column in us.CE_SUMMARY_UCC_PREFIX},
        }
    )
    fmld.loc[0, "BEEF"] = 3.0
    fmld.loc[1, "MISCFOOD"] = 4.5
    expd = pd.DataFrame(
        {
            "NEWID": ["a", "a", "b", "b"],
            "UCC": ["030110", "030219", "180110", "900000"],
            "COST": [1.0, 2.0, 4.5, 9.0],
        }
    )
    check = us.ucc_check(fmld, expd)
    assert check["BEEF"]["max_abs_diff"] == 0.0
    assert check["BEEF"]["uccs"] == ["030110", "030219"]
    assert check["MISCFOOD"]["max_abs_diff"] == 0.0
    fmld.loc[0, "BEEF"] = 5.0
    assert us.ucc_check(fmld, expd)["BEEF"]["max_abs_diff"] == pytest.approx(2.0)


def test_category_unavailable_when_penetration_missing():
    result = us.calibrate_category(
        "plant_based_meat",
        us_households=130_000_000,
        penetration=None,
        intent_share=0.329,
        sales_usd=1.0e9,
        addressable_share=0.55,
    )
    assert result["status"] == "UNAVAILABLE"
    assert result["conversion"] is None
    assert "penetration" in result["missing"]


def test_dairy_category_sets_conversion_one_and_intent_to_penetration():
    result = us.calibrate_dairy(
        us_households=130_000_000, penetration=0.38, sales_usd=2.7e9
    )
    assert result["status"] == "AVAILABLE"
    assert result["conversion"] == 1.0
    assert result["intent_share"] == 0.38
    assert result["spend_per_adopter_usd"] == pytest.approx(2.7e9 / (130e6 * 0.38))


def test_dairy_intent_scales_penetration_by_urban_packaged_share():
    result = us.calibrate_dairy(
        130_000_000, penetration=0.38, sales_usd=2.7e9, urban_packaged_share=0.70
    )
    assert result["intent_share"] == pytest.approx(0.38 / 0.70)
    assert result["conversion"] == pytest.approx(1.0)
    assert result["addressable_share"] == 0.70
    assert result["spend_per_adopter_usd"] == pytest.approx(2.7e9 / (130e6 * 0.38))


def test_dairy_intent_capped_at_one():
    result = us.calibrate_dairy(
        130_000_000, penetration=0.38, sales_usd=2.7e9, urban_packaged_share=0.30
    )
    assert result["intent_share"] == 1.0
    assert result["conversion"] == 1.0


def test_build_payload_is_diagnostic_and_free_of_placeholder_token():
    ce = {
        "us_households": 134_000_000,
        "addressable_share": 0.55,
        "us_urban_packaged_share": 0.70,
        "addressable_share_including_zero_food_weeks": 0.50,
        "us_urban_packaged_share_including_zero_food_weeks": 0.64,
        "urban_share": 0.95,
        "meat_share": 0.64,
        "packaged_share": 0.71,
        "n_records": 100,
    }
    payload = us.build_payload(ce, ucc={}, inputs={})
    assert payload["status"] == "DIAGNOSTIC"
    meat = payload["categories"]["plant_based_meat"]
    assert meat["status"] == "AVAILABLE"
    assert meat["conversion"] == pytest.approx(
        min(1.0, us.GFI["plant_based_meat"]["penetration"]["value"] / 0.55)
        / us.BRYANT_USA_INTENT["value"]
    )
    assert meat["price_ratio_us"] == pytest.approx(7.88 / 3.17)
    assert meat["price_ratio_us_all_meat"] == pytest.approx(8.23 / 4.67)
    assert meat["conversion_including_zero_food_weeks"] == pytest.approx(
        (0.11 / 0.50) / 0.329
    )
    dairy = payload["categories"]["dairy_alternatives"]
    assert dairy["conversion"] == pytest.approx(1.0)
    assert dairy["intent_share"] == pytest.approx(0.38 / 0.70)
    assert dairy["intent_share_including_zero_food_weeks"] == pytest.approx(0.38 / 0.64)
    assert "us_urban_packaged_share" in dairy["deviation"]
    assert payload["ce"]["addressable_rule"]["buys_packaged_food_r38"]["status"] == (
        "NOT_DONE"
    )
    text = json.dumps(payload)
    assert "SYNTHETIC" not in text
    assert chr(0x2013) not in text and chr(0x2014) not in text
