"""Tests for the plant-based price snapshot normalisation and price ratios."""

from __future__ import annotations

import numpy as np
import pandas as pd
import prices
import pytest


def test_price_per_kg_protein():
    obs = prices.example_rows()  # 200 g pack, INR 150, 20 g protein per 100 g
    out = prices.normalise_prices(obs)
    assert out.price_per_kg_local.iloc[0] == 750.0
    assert out.price_per_kg_protein_local.iloc[0] == 3750.0


def test_synthetic_prices_keep_flag():
    out = prices.normalise_prices(prices.load_synthetic())
    assert (out.status == "SYNTHETIC").all()


def test_normalise_has_interface_columns():
    out = prices.normalise_prices(prices.example_rows())
    for column in (
        "country",
        "city",
        "retailer",
        "product",
        "category",
        "price_per_kg_local",
        "price_per_kg_protein_local",
        "status",
    ):
        assert column in out.columns


def test_missing_protein_stays_missing():
    obs = prices.example_rows()
    obs.loc[0, "protein_g_per_100g"] = np.nan
    out = prices.normalise_prices(obs)
    assert np.isnan(out.price_per_kg_protein_local.iloc[0])


def test_unknown_category_raises():
    obs = prices.example_rows()
    obs.loc[0, "category"] = "chicken"
    with pytest.raises(ValueError):
        prices.normalise_prices(obs)


def test_non_positive_pack_raises():
    obs = prices.example_rows()
    obs.loc[0, "pack_size_g"] = 0
    with pytest.raises(ValueError):
        prices.normalise_prices(obs)


def test_synthetic_rows_cover_every_city_and_category():
    syn = prices.load_synthetic()
    cells = set(zip(syn.country, syn.city, syn.category))
    for country, city, _state in prices.CITIES:
        for category in prices.CATEGORIES:
            assert (country, city, category) in cells


def _uv_table():
    return pd.DataFrame(
        {
            "country": ["India", "India"],
            "state": [27, 7],
            "unit_value_local": [200.0, 250.0],
            "n_households": [500, 400],
        }
    )


def test_price_ratio_by_state():
    out = prices.price_ratio(
        prices.normalise_prices(prices.example_rows()), _uv_table()
    )
    ratio = out.set_index("state").price_ratio
    assert ratio[27] == pytest.approx(750.0 / 200.0)
    assert ratio[7] == pytest.approx(750.0 / 250.0)


def test_price_ratio_applies_deflators():
    out = prices.price_ratio(
        prices.normalise_prices(prices.example_rows()),
        _uv_table(),
        plant_deflator={"India": 0.5},
        reference_deflator={"India": 2.0},
    )
    assert out.set_index("state").price_ratio[27] == pytest.approx(
        (750.0 * 0.5) / (200.0 * 2.0)
    )


def test_price_ratio_rejects_mixed_status():
    plant = prices.normalise_prices(prices.example_rows())
    syn = plant.assign(status="SYNTHETIC")
    with pytest.raises(ValueError):
        prices.price_ratio(pd.concat([plant, syn], ignore_index=True), _uv_table())


def test_price_ratio_missing_reference_stays_missing():
    uv = _uv_table()
    uv.loc[0, "unit_value_local"] = np.nan
    out = prices.price_ratio(prices.normalise_prices(prices.example_rows()), uv)
    assert np.isnan(out.set_index("state").price_ratio[27])


def test_state_unit_values_suppress_small_cells():
    table = pd.DataFrame(
        {
            "state": [1] * 30 + [2] * 29,
            "multiplier": [1.0] * 59,
            "unit_value_chicken": [200.0] * 15 + [100.0] * 15 + [300.0] * 29,
        }
    )
    out = prices.state_unit_values(table, "India", "chicken").set_index("state")
    assert out.unit_value_local[1] == pytest.approx(150.0)
    assert out.n_households[2] == 29
    assert np.isnan(out.unit_value_local[2])


def test_summary_counts_placeholder_cells_without_flag_word():
    obs = prices.normalise_prices(prices.example_rows())
    summary = prices.summarise(obs, prices.load_synthetic())
    text = repr(summary)
    assert "SYNTHETIC" not in text
    assert summary["coverage"]["placeholder_cells"] > 0


def test_missing_household_count_stays_missing():
    uv = _uv_table().astype({"n_households": float})
    uv.loc[0, "n_households"] = np.nan
    out = prices.price_ratio(prices.normalise_prices(prices.example_rows()), uv)
    counts = out.set_index("state").n_reference_households
    assert np.isnan(counts[27])
    assert counts[7] == 400
    records = {r["state"]: r for r in prices._ratio_records(out)}
    assert records[27]["n_reference_households"] is None
    assert records[7]["n_reference_households"] == 400


def test_price_ratio_without_count_column_gives_missing_count():
    uv = _uv_table().drop(columns="n_households")
    out = prices.price_ratio(prices.normalise_prices(prices.example_rows()), uv)
    assert out.n_reference_households.isna().all()
