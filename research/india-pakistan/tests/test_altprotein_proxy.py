"""Dollar-basis, overlap sensitivity and US comparison checks for the proxy.

Spending is in market-exchange-rate dollars at 2025 prices, so every income
ratio the model applies to it must use the same basis and price year.
"""

import csv
import importlib.util
import math
from pathlib import Path

# Values are written with six decimals, hence the 1e-6 tolerances.
ROOT = Path(__file__).resolve().parents[1]
MODEL_SPEC = importlib.util.spec_from_file_location("altprotein_proxy", ROOT / "tools/build_altprotein_proxy.py")
MODEL = importlib.util.module_from_spec(MODEL_SPEC)
MODEL_SPEC.loader.exec_module(MODEL)


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


def test_drift_overlap_subtracts_income_growth_for_the_same_period():
    """Check the adjusted bound against aggregate growth and population inputs."""
    i, p = inputs(), params()
    income_growth = (
        (1 + i["imf_ngdp_rpch_ind_2024"] / 100)
        * (1 + i["imf_ngdp_rpch_ind_2025"] / 100)
        * i["imf_lp_ind_2023"] / i["imf_lp_ind_2025"]
    ) ** 0.5 - 1
    cpi_fx = india_2022_income_at_2025_prices(i) / i["wdi_gdp_per_capita_lcu_ind_2022"]
    india_anchor = i["gfi_india_domestic_2022_central"] * 10 * cpi_fx / i["imf_lp_ind_2022"]
    us_per_person = i["gfi_us_retail_sales_2025"] * 1000 / i["imf_lp_usa_2025"]
    elasticity_high = math.log(us_per_person / india_anchor) / math.log(
        i["wdi_gdp_per_capita_usd_usa_2025"] / india_2022_income_at_2025_prices(i)
    )
    vacancy_growth = (i["jobs_vacancies_india_2025"] / i["jobs_vacancies_india_2023"]) ** 0.5 - 1
    expected = 100 * (vacancy_growth - income_growth * elasticity_high)
    assert math.isclose(p["india_2022_adoption_drift_overlap_adjusted_high"], expected, rel_tol=0, abs_tol=1e-6)
    assert MODEL.SEED == 20261015 and MODEL.DRAWS == 10000


def test_drift_overlap_rows_cover_both_countries_and_all_years():
    """Require all requested quantiles and a lower India middle scenario."""
    scenarios = {r["row_id"]: r for r in rows("altprotein_proxy_scenarios.csv")}
    for country in ("india", "pakistan"):
        for year in (2026, 2030, 2035):
            values = []
            for statistic in ("p10", "p50", "p90"):
                row = scenarios[f"{country}_{year}_market_value_drift_overlap_adjusted_{statistic}"]
                assert row["record_type"] == "sensitivity"
                assert row["unit"] == "million US dollars at constant prices"
                values.append(float(row["value"]))
            assert 0 < values[0] <= values[1] <= values[2]
    assert float(scenarios["india_2035_market_value_drift_overlap_adjusted_p50"]["value"]) <= float(
        scenarios["india_2035_market_value_p50"]["value"]
    )


def test_pakistan_overlap_variant_rows_are_present():
    """Removing the two positive multipliers lowers each Pakistan quantile."""
    scenarios = {r["row_id"]: r for r in rows("altprotein_proxy_scenarios.csv")}
    values = []
    for statistic in ("p10", "p50", "p90"):
        row = scenarios[f"pakistan_2035_market_value_without_urban_animal_{statistic}"]
        assert row["record_type"] == "sensitivity"
        value = float(row["value"])
        assert 0 < value <= float(scenarios[f"pakistan_2035_market_value_{statistic}"]["value"])
        values.append(value)
    assert values == sorted(values)


def test_us_comparison_reproduces_existing_2025_shares():
    """Reconstruct per-person values from totals to avoid small-value rounding."""
    i = inputs()
    scenarios = {r["row_id"]: r for r in rows("altprotein_proxy_scenarios.csv")}
    us_per_person = i["gfi_us_retail_sales_2025"] * 1000 / i["imf_lp_usa_2025"]
    for country in ("India", "Pakistan"):
        for year in (2026, 2030, 2035):
            prefix = f"{country.lower()}_{year}"
            for statistic in ("p10", "p50", "p90"):
                existing = scenarios[f"{prefix}_per_capita_share_of_us_2025_{statistic}"]
                per_person = float(scenarios[f"{prefix}_market_value_{statistic}"]["value"]) / float(
                    scenarios[f"{prefix}_population_value"]["value"]
                )
                actual = MODEL.us_comparison_row(
                    country, year, statistic, per_person, 2025, us_per_person,
                    [], "Test against the observed US comparison",
                )
                assert actual["row_id"] == existing["row_id"]
                assert math.isclose(float(actual["value"]), float(existing["value"]), rel_tol=0, abs_tol=1e-6)


def test_us_comparison_accepts_supplied_year_and_value():
    """Use synthetic values in memory, without creating any US forecast rows."""
    for us_year in (2026, 2030, 2035):
        row = MODEL.us_comparison_row("India", 2035, "p50", 1.0, us_year, 4.0, [], "Synthetic test")
        assert list(row) == MODEL.OUTPUT_FIELDS
        assert row["year"] == "2035"
        assert row["quantity"] == f"per_capita_share_of_us_{us_year}"
        assert row["value"] == "25.000000"
    for invalid in (0, -1, math.nan, math.inf):
        try:
            MODEL.us_comparison_row("India", 2035, "p50", 1.0, 2035, invalid, [], "Synthetic test")
        except ValueError:
            continue
        raise AssertionError(f"Invalid US comparison denominator accepted: {invalid}")
    assert not any(
        r["country"] == "United States" and r["year"] in {"2026", "2030", "2035"}
        for r in rows("altprotein_proxy_scenarios.csv")
    )
