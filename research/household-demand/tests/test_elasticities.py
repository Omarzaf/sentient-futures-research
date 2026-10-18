"""Tests for unit-value price, income and cross-price elasticities (Task 4)."""

from __future__ import annotations

import json

import elasticities as el
import numpy as np
import pandas as pd
import pytest

SEED = 20261018

# Known parameters of the simulated households. Elasticities are Marshallian and
# conditional on purchase: own = b_gg - 1, cross = b_gk, income = 1 + c_g in
# ln w_g = a + sum_k b_gk ln p_k + c_g ln mpce + d_g ln hh_size + state + e.
TRUE_OWN = {"chicken": -0.8, "pulses": -0.5}
TRUE_INCOME = {"chicken": 0.9, "pulses": 0.4}
TRUE_CROSS = {("chicken", "pulses"): 0.10, ("pulses", "chicken"): 0.05}
BASE_PRICE = {"chicken": 150.0, "pulses": 120.0}
BASE_SHARE = {"chicken": 0.03, "pulses": 0.04}
PURCHASE_RATE = {"chicken": 0.6, "pulses": 0.95}


def make_households(seed: int = SEED) -> pd.DataFrame:
    """Simulate 10,000 households in 200 district-by-sector cells, 4 states.

    Each cell has 2 PSUs of 25 households. Cell prices vary log-normally;
    household unit values add 10% quality noise around the cell price.
    Purchase is random and independent of prices, so the conditional
    regression is unbiased. 40 extra households carry MISSING_FDQ.
    """
    rng = np.random.default_rng(seed)
    rows = []
    psu_id = 0
    for state in range(1, 5):
        state_fe = rng.normal(0, 0.2)
        for district in range(1, 26):
            for sector in (1, 2):
                log_p = {
                    "chicken": np.log(BASE_PRICE["chicken"]) + rng.normal(0, 0.3),
                    "pulses": np.log(BASE_PRICE["pulses"]) + rng.normal(0, 0.25),
                }
                for _ in range(2):
                    psu_id += 1
                    multiplier = int(rng.integers(50, 500))
                    for h in range(25):
                        rows.append(
                            {
                                "hhid": f"{psu_id:05d}{h:02d}",
                                "state": state,
                                "district": district,
                                "sector": sector,
                                "psu": psu_id,
                                "stratum": state * 10 + sector,
                                "stratum_status": "RESOLVED",
                                "multiplier": multiplier,
                                "state_fe": state_fe,
                                "log_p_chicken": log_p["chicken"],
                                "log_p_pulses": log_p["pulses"],
                            }
                        )
    frame = pd.DataFrame(rows)
    n = len(frame)
    frame["hh_size"] = rng.integers(1, 9, n)
    frame["mpce_local"] = np.exp(np.log(4000) + rng.normal(0, 0.5, n))
    frame["mpce_status"] = "OK"
    frame["currency"] = "INR"
    log_x = np.log(frame["mpce_local"] / 4000)
    log_n = np.log(frame["hh_size"])
    for g in ("chicken", "pulses"):
        other = "pulses" if g == "chicken" else "chicken"
        log_w = (
            np.log(BASE_SHARE[g])
            + (TRUE_OWN[g] + 1) * (frame[f"log_p_{g}"] - np.log(BASE_PRICE[g]))
            + TRUE_CROSS[(g, other)]
            * (frame[f"log_p_{other}"] - np.log(BASE_PRICE[other]))
            + (TRUE_INCOME[g] - 1) * log_x
            - 0.05 * log_n
            + frame["state_fe"]
            + rng.normal(0, 0.3, n)
        )
        buys = rng.random(n) < PURCHASE_RATE[g]
        value = np.exp(log_w) * frame["mpce_local"] * frame["hh_size"]
        unit_value = np.exp(frame[f"log_p_{g}"] + rng.normal(0, 0.1, n))
        frame[f"value_month_{g}"] = value.where(buys)
        frame[f"unit_value_{g}"] = unit_value.where(buys)
        frame[f"qty_month_{g}"] = (value / unit_value).where(buys)
    frame["value_month_meals_out"] = 100.0
    frame["qty_month_meals_out"] = np.nan
    frame["unit_value_meals_out"] = np.nan
    frame["hhid"] = frame["hhid"].astype(str)
    missing = frame.sample(40, random_state=1).copy()
    missing["hhid"] = "M" + missing["hhid"]
    missing["mpce_local"] = np.nan
    missing["mpce_status"] = "MISSING_FDQ"
    frame = pd.concat([frame, missing], ignore_index=True)
    return frame.drop(columns=["state_fe", "log_p_chicken", "log_p_pulses"])


@pytest.fixture(scope="module")
def simulated_households() -> pd.DataFrame:
    return make_households()


# Brief, Step 1.


def test_recovers_known_elasticities(simulated_households):
    # generated with own-price -0.8 and income 0.9 for chicken
    est = el.estimate_elasticities(
        simulated_households, ["chicken", "pulses"], cluster="psu"
    )
    assert abs(est.own_price["chicken"] + 0.8) < 0.05
    assert abs(est.income["chicken"] - 0.9) < 0.05


def test_bootstrap_is_seeded(simulated_households):
    a = el.estimate_elasticities(simulated_households, ["chicken"], cluster="psu")
    b = el.estimate_elasticities(simulated_households, ["chicken"], cluster="psu")
    assert a.draws.equals(b.draws)


def test_rejects_sub_state_reporting(simulated_households):
    with np.testing.assert_raises(ValueError):
        el.estimate_elasticities(
            simulated_households, ["chicken"], cluster="psu", level="district"
        )


# Added: cross-price, intervals, draws shape, filters and variance design.


def test_recovers_pulses_and_cross_price(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken", "pulses"], cluster="psu", draws=50
    )
    assert abs(est.own_price["pulses"] - TRUE_OWN["pulses"]) < 0.05
    assert abs(est.income["pulses"] - TRUE_INCOME["pulses"]) < 0.05
    for pair, value in TRUE_CROSS.items():
        assert abs(est.cross_price[pair] - value) < 0.05
    assert set(est.cross_price) == set(TRUE_CROSS)


def test_draws_have_one_column_per_parameter(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken", "pulses"], cluster="psu", draws=40
    )
    assert est.draws.shape == (40, 2 + 2 + 2)
    assert "own_price:chicken" in est.draws.columns
    assert "cross_price:chicken:pulses" in est.draws.columns
    assert est.draws.notna().all().all()
    assert est.draws["own_price:chicken"].std() > 0


def test_intervals_cover_truth(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken"], cluster="psu", draws=200
    )
    table = est.intervals(0.95)
    row = table.loc["own_price:chicken"]
    assert row["lower"] < row["estimate"] < row["upper"]
    assert row["lower"] < TRUE_OWN["chicken"] < row["upper"]


def test_default_draws_is_500(simulated_households):
    est = el.estimate_elasticities(simulated_households, ["chicken"], cluster="psu")
    assert len(est.draws) == 500
    assert est.level == "national"


def test_uses_only_mpce_ok_households(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken"], cluster="psu", draws=2
    )
    ok = simulated_households["mpce_status"].eq("OK")
    buyers = simulated_households["value_month_chicken"].gt(0)
    assert est.n_households["chicken"] == int((ok & buyers).sum())


def test_group_without_unit_values_raises(simulated_households):
    with pytest.raises(ValueError, match="meals_out"):
        el.estimate_elasticities(
            simulated_households, ["chicken", "meals_out"], cluster="psu", draws=2
        )


def test_unknown_group_raises(simulated_households):
    with pytest.raises(ValueError, match="paneer"):
        el.estimate_elasticities(
            simulated_households, ["paneer"], cluster="psu", draws=2
        )


def test_mixed_currency_raises(simulated_households):
    mixed = simulated_households.copy()
    mixed.loc[mixed.index[:10], "currency"] = "PKR"
    with pytest.raises(ValueError, match="currency"):
        el.estimate_elasticities(mixed, ["chicken"], cluster="psu", draws=2)


def test_small_cells_are_missing(simulated_households):
    frame = simulated_households.copy()
    cell = frame["state"].eq(1) & frame["district"].eq(1) & frame["sector"].eq(1)
    with_uv = frame.index[cell & frame["unit_value_chicken"].notna()]
    frame.loc[with_uv[4:], "unit_value_chicken"] = np.nan
    prices = el.cell_prices(frame, ["chicken"], min_obs=5)
    assert np.isnan(prices.loc[(1, 1, 1), "chicken"])
    assert prices["chicken"].notna().sum() == 199
    prices_3 = el.cell_prices(frame, ["chicken"], min_obs=4)
    assert np.isfinite(prices_3.loc[(1, 1, 1), "chicken"])
    est = el.estimate_elasticities(frame, ["chicken"], cluster="psu", draws=2)
    dropped = int(
        (
            cell & frame["value_month_chicken"].gt(0) & frame["mpce_status"].eq("OK")
        ).sum()
    )
    full = el.estimate_elasticities(
        simulated_households, ["chicken"], cluster="psu", draws=2
    )
    assert est.n_households["chicken"] == full.n_households["chicken"] - dropped
    assert est.min_cell_obs == 5


def test_cell_price_is_weighted_mean_unit_value():
    frame = pd.DataFrame(
        {
            "state": [1] * 5,
            "district": [1] * 5,
            "sector": [1] * 5,
            "multiplier": [1, 1, 1, 1, 4],
            "unit_value_chicken": [100.0, 100.0, 100.0, 100.0, 200.0],
        }
    )
    prices = el.cell_prices(frame, ["chicken"], min_obs=5)
    assert prices.loc[(1, 1, 1), "chicken"] == pytest.approx(150.0)


def test_resolved_rows_resample_within_strata(simulated_households):
    frame = simulated_households[simulated_households["mpce_status"].eq("OK")]
    labels = el.resampling_strata(frame)
    assert labels.groupby(frame["psu"]).nunique().max() == 1
    assert labels.nunique() == frame.groupby(["state", "sector", "stratum"]).ngroups


def test_placeholder_rows_resample_within_province(simulated_households):
    frame = simulated_households[simulated_households["mpce_status"].eq("OK")].copy()
    frame["stratum_status"] = "S" + "YNTHETIC"
    frame["currency"] = "PKR"
    labels = el.resampling_strata(frame)
    assert labels.nunique() == frame["state"].nunique()
    est = el.estimate_elasticities(frame, ["chicken"], cluster="psu", draws=5)
    assert est.variance_strata_placeholder is True
    assert "province" in est.variance_method["Pakistan"]
    assert "YNTHETIC" not in est.variance_method["Pakistan"]


def test_india_variance_method_is_recorded(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken"], cluster="psu", draws=5
    )
    assert est.variance_strata_placeholder is False
    assert "official strata" in est.variance_method["India"]


def test_psu_factors_keep_stratum_totals(simulated_households):
    frame = simulated_households[simulated_households["mpce_status"].eq("OK")]
    psus = frame.drop_duplicates("psu")
    strata = el.resampling_strata(psus).to_numpy()
    rng = np.random.default_rng(SEED)
    factors, counts = el.psu_factors(strata, rng)
    for label in np.unique(strata):
        mask = strata == label
        assert factors[mask].sum() == pytest.approx(mask.sum())
        assert counts[mask].sum() == mask.sum() - 1


def test_state_level_returns_per_state_estimates(simulated_households):
    est = el.estimate_elasticities(
        simulated_households, ["chicken"], cluster="psu", draws=20, level="state"
    )
    assert est.level == "state"
    assert set(est.by_state) == {"1", "2", "3", "4"}
    for sub in est.by_state.values():
        assert sub.level == "state"
        assert abs(sub.own_price["chicken"] + 0.8) < 0.2
        assert len(sub.draws) == 20
    assert abs(est.own_price["chicken"] + 0.8) < 0.05


def test_pakistan_area_comes_from_psu_code():
    frame = pd.DataFrame(
        {
            "state": [1, 1, 1],
            "district": pd.array([111, pd.NA, pd.NA], dtype="Int64"),
            "sector": [1, 2, 2],
            "psu": [11110001, 11520001, 11530001],
            "currency": ["PKR"] * 3,
        }
    )
    assert el.price_area(frame).tolist() == [111, 115, 115]


def test_missing_district_outside_pakistan_raises():
    frame = pd.DataFrame(
        {
            "state": [1],
            "district": pd.array([pd.NA], dtype="Int64"),
            "sector": [1],
            "psu": [1],
            "currency": ["INR"],
        }
    )
    with pytest.raises(ValueError, match="district"):
        el.price_area(frame)


def test_summary_is_json_and_free_of_placeholder_token(simulated_households):
    frame = simulated_households.copy()
    frame["stratum_status"] = "S" + "YNTHETIC"
    frame["currency"] = "PKR"
    frame["psu"] = frame["district"] * 100_000 + frame["psu"]
    est = el.estimate_elasticities(
        frame, ["chicken", "pulses"], cluster="psu", draws=20
    )
    text = json.dumps(est.to_dict(), allow_nan=False)
    assert "S" + "YNTHETIC" not in text
    summary = json.loads(text)
    assert summary["variance_strata_placeholder"] is True
    assert (
        summary["design"]["placeholder_stratum_households"]
        == summary["design"]["households"]
    )
    chicken = summary["elasticities"]["own_price:chicken"]
    assert chicken["lower"] <= chicken["draw_median"] <= chicken["upper"]
