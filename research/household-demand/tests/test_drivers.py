"""Tests for driver bands, CPI deflators and the price scenarios."""

from __future__ import annotations

import gzip
import json
import math

import drivers
import numpy as np
import pandas as pd
import pytest


def test_parity_scenario_reaches_one():
    base = drivers.example_base()  # price_ratio 2.0 in 2026
    path = drivers.scenario_paths(base, ai_decline=0.0, parity_year=2030)
    assert path.loc[path.year == 2030, "price_ratio"].iloc[0] == 1.0


def test_parity_scenario_holds_after_parity_year():
    path = drivers.scenario_paths(drivers.example_base(), 0.0, 2030)
    assert (path.loc[path.year >= 2030, "price_ratio"] == 1.0).all()
    before = path.loc[path.year < 2030].sort_values("year").price_ratio
    assert before.iloc[0] == 2.0
    assert np.all(np.diff(before.to_numpy()) < 0)


def test_ai_decline_compounds_without_parity():
    path = drivers.scenario_paths(
        drivers.example_base(), ai_decline=0.1, parity_year=None
    )
    ratio = path.set_index("year").price_ratio
    assert ratio[2026] == 2.0
    assert ratio[2028] == pytest.approx(2.0 * 0.9**2)


def test_no_decline_no_parity_keeps_ratio():
    path = drivers.scenario_paths(drivers.example_base(), 0.0, None)
    assert (path.price_ratio == 2.0).all()


def test_scenario_rejects_bad_decline():
    with pytest.raises(ValueError):
        drivers.scenario_paths(drivers.example_base(), ai_decline=1.0, parity_year=None)


def _write_fixture(root):
    inputs = root / "inputs"
    inputs.mkdir()
    years = range(1998, 2032)
    ngdp = {"IND": {str(y): 6.0 for y in years}, "PAK": {str(y): 4.0 for y in years}}
    ngdp["IND"]["2005"] = 8.0
    lp = {"IND": {str(y): 1000.0 * 1.01 ** (y - 1998) for y in years}}
    lp["PAK"] = {str(y): 200.0 * 1.02 ** (y - 1998) for y in years}
    pc = {"IND": {"2025": 2000.0}, "PAK": {"2025": 1500.0}}
    cpi = {"IND": {str(y): 5.0 for y in years}, "PAK": {str(y): 10.0 for y in years}}
    for code, data in {
        "NGDP_RPCH": ngdp,
        "LP": lp,
        "NGDPDPC": pc,
        "PCPIPCH": cpi,
    }.items():
        (inputs / f"{code}.json").write_text(json.dumps({"values": {code: data}}))
    rows = []
    for iso in ("IND", "PAK"):
        for year in range(2024, 2036):
            for variant, scale in (
                ("Medium", 1.0),
                ("Lower 80 PI", 0.98),
                ("Upper 80 PI", 1.02),
            ):
                rows.append(
                    {
                        "ISO3_code": iso,
                        "Time": year,
                        "Variant": variant,
                        "TPopulation1July": 1000.0 * scale * (1 + 0.01 * (year - 2024)),
                    }
                )
    frame = pd.DataFrame(rows)
    with gzip.open(inputs / "wpp_medium.csv.gz", "wt") as handle:
        frame[frame.Variant == "Medium"].to_csv(handle, index=False)
    with gzip.open(inputs / "wpp_other.csv.gz", "wt") as handle:
        frame[frame.Variant != "Medium"].to_csv(handle, index=False)
    (inputs / "wup.zip").write_bytes(b"placeholder")
    manifest = root / "manifest.csv"
    entries = [
        ("imf_weo_2026_10_ngdp_rpch", "inputs/NGDP_RPCH.json"),
        ("imf_weo_2026_10_lp", "inputs/LP.json"),
        ("imf_weo_2026_10_ngdpdpc", "inputs/NGDPDPC.json"),
        ("imf_weo_2026_10_pcpipch", "inputs/PCPIPCH.json"),
        ("un_wpp_2024_medium", "inputs/wpp_medium.csv.gz"),
        ("un_wpp_2024_other_variants", "inputs/wpp_other.csv.gz"),
        ("un_wup_2018_excel_zip", "inputs/wup.zip"),
    ]
    pd.DataFrame(
        {"input_id": [e[0] for e in entries], "stored_at": [e[1] for e in entries]}
    ).to_csv(manifest, index=False)
    return manifest


def _wup_frame(_path):
    return pd.DataFrame(
        {
            "country": ["India", "Pakistan"] * 10,
            "year": [y for y in range(2026, 2036) for _ in range(2)],
            "urban_share": [0.38, 0.39] * 10,
        }
    )


@pytest.fixture
def fixture_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(drivers, "_read_wup", _wup_frame)
    return _write_fixture(tmp_path)


def test_load_drivers_schema(fixture_manifest):
    out = drivers.load_drivers(fixture_manifest, root=fixture_manifest.parent)
    assert list(out.columns) == ["country", "year", "variable", "band", "value"]
    assert set(out.variable) == {"gdp_per_capita_usd_2025", "population", "urban_share"}
    assert set(out.band) == {"low", "mid", "high"}
    assert {2026, 2030, 2035} <= set(out.year)


def test_gdp_mid_grows_at_real_per_capita_rate(fixture_manifest):
    out = drivers.load_drivers(fixture_manifest, root=fixture_manifest.parent)
    gdp = out[(out.variable == "gdp_per_capita_usd_2025") & (out.country == "India")]
    mid = gdp[gdp.band == "mid"].set_index("year").value
    assert mid[2026] == pytest.approx(2000.0 * 1.06 / 1.01)
    assert mid[2035] == pytest.approx(2000.0 * (1.06 / 1.01) ** 10)


def test_gdp_band_widens_with_horizon(fixture_manifest):
    out = drivers.load_drivers(fixture_manifest, root=fixture_manifest.parent)
    gdp = out[(out.variable == "gdp_per_capita_usd_2025") & (out.country == "India")]
    wide = gdp.pivot(index="year", columns="band", values="value")
    spread = np.log(wide["high"] / wide["low"])
    assert spread[2030] > spread[2026] > 0
    assert math.isclose(spread[2035] / spread[2026], math.sqrt(10), rel_tol=1e-9)


def test_population_bands_from_wpp_variants(fixture_manifest):
    out = drivers.load_drivers(fixture_manifest, root=fixture_manifest.parent)
    pop = out[
        (out.variable == "population")
        & (out.country == "Pakistan")
        & (out.year == 2026)
    ]
    values = pop.set_index("band").value
    assert values["mid"] == pytest.approx(1000.0 * 1.02 * 1000)
    assert values["low"] < values["mid"] < values["high"]


def test_cpi_index_is_one_in_2025(fixture_manifest):
    idx = drivers.cpi_index(fixture_manifest, root=fixture_manifest.parent)
    india = idx[idx.country == "India"].set_index("year").index_2025
    assert india[2025] == 1.0
    assert india[2026] == pytest.approx(1.05)
    assert india[2024] == pytest.approx(1 / 1.05)


def test_missing_manifest_input_raises(tmp_path):
    manifest = tmp_path / "manifest.csv"
    pd.DataFrame({"input_id": ["x"], "stored_at": ["y"]}).to_csv(manifest, index=False)
    with pytest.raises(KeyError):
        drivers.load_drivers(manifest, root=tmp_path)


def test_ai_decline_values_follow_r41():
    defs = drivers.scenario_definitions()
    assert defs["main_ai_decline"] == 0.0
    assert defs["illustrative_ai_decline"] == [0.02, 0.05]
    assert "illustrative assumptions" in defs["illustrative_label"]
    assert "model_from_panel_inputs" in defs["panel_input_use"]
    assert "ruling" not in repr(defs).replace("(ruling R41)", "")


def test_illustrative_ai_paths_compound():
    for rate in drivers.AI_DECLINE_ILLUSTRATIVE:
        path = drivers.scenario_paths(drivers.example_base(), rate, None)
        ratio = path.set_index("year").price_ratio
        assert ratio[2030] == pytest.approx(2.0 * (1 - rate) ** 4)
