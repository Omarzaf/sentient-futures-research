"""Dollar-basis checks for tools/build_altprotein_proxy.py.

Spending is in market-exchange-rate dollars at 2025 prices, so every income
ratio the model applies to it must use the same basis and price year.
"""

import csv
import math
from pathlib import Path

# Values are written with six decimals, hence the 1e-6 tolerances.
ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    with (ROOT / "data" / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def inputs():
    return {r["input_id"]: float(r["value"]) for r in rows("altprotein_proxy_inputs.csv")}


def params():
    return {r["row_id"]: float(r["value"]) for r in rows("altprotein_proxy_scenarios.csv") if r["record_type"] == "parameter"}


def india_2022_income_at_2025_prices(i):
    cpi = 1.0
    for year in (2023, 2024, 2025):
        cpi *= 1 + i[f"imf_pcpipch_ind_{year}"] / 100
    return i["wdi_gdp_per_capita_lcu_ind_2022"] * cpi / i["wdi_exchange_rate_ind_2025"]


def test_market_rate_income_inputs_are_transcribed():
    i = inputs()
    for key in ("wdi_gdp_per_capita_lcu_ind_2022", "wdi_gdp_per_capita_usd_usa_2025", "wdi_gdp_per_capita_usd_ind_2025", "wdi_gdp_per_capita_usd_pak_2025"):
        assert key in i and i[key] > 0


def test_us_india_income_ratio_uses_market_dollars_at_2025_prices():
    i, p = inputs(), params()
    expected = i["wdi_gdp_per_capita_usd_usa_2025"] / india_2022_income_at_2025_prices(i)
    assert math.isclose(p["united_states_2025_market_income_ratio_to_india_anchor_value"], expected, rel_tol=1e-6, abs_tol=1e-6)
    assert "united_states_2025_ppp_income_ratio_to_india_anchor_value" not in p


def test_high_elasticity_divides_like_with_like():
    p = params()
    expected = math.log(p["united_states_2025_per_capita_ratio_to_india_anchor_value"]) / math.log(
        p["united_states_2025_market_income_ratio_to_india_anchor_value"]
    )
    assert math.isclose(p["india_2022_income_elasticity_high"], expected, rel_tol=1e-6, abs_tol=1e-6)


def test_pakistan_income_ratio_uses_market_dollars():
    i, p = inputs(), params()
    expected = i["wdi_gdp_per_capita_usd_pak_2025"] / i["wdi_gdp_per_capita_usd_ind_2025"]
    assert math.isclose(p["pakistan_2025_market_income_ratio_to_india_value"], expected, rel_tol=1e-6, abs_tol=1e-6)
    assert "pakistan_2025_ppp_income_ratio_to_india_value" not in p


def test_ppp_series_no_longer_feeds_the_model():
    assert not any(r["quantity"] == "gdp_per_capita_ppp" for r in rows("altprotein_proxy_inputs.csv"))
