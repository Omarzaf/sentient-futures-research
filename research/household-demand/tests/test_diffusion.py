"""Tests for the Bass diffusion fit and path."""

from __future__ import annotations

import diffusion
import numpy as np
import pytest


def test_bass_recovers_parameters():
    years = np.arange(0, 20)
    y = diffusion.bass_path(0.01, 0.4, 1000.0, years)
    p, q, m = diffusion.fit_bass(years, y)
    assert abs(p - 0.01) < 0.002 and abs(q - 0.4) < 0.02 and abs(m - 1000) < 20


def test_bass_path_starts_at_zero_and_rises_to_m():
    path = diffusion.bass_path(0.03, 0.38, 50.0, np.array([0, 1, 10, 200]))
    assert path[0] == 0.0
    assert np.all(np.diff(path) > 0)
    assert path[-1] == pytest.approx(50.0)


def test_bass_path_is_zero_before_launch():
    path = diffusion.bass_path(0.03, 0.38, 50.0, np.array([-3, -1, 0]))
    assert np.all(path == 0.0)


def test_fit_bass_ignores_missing_points():
    years = np.arange(0, 15).astype(float)
    y = diffusion.bass_path(0.02, 0.5, 200.0, years)
    y[[3, 7]] = np.nan
    p, q, m = diffusion.fit_bass(years, y)
    assert abs(p - 0.02) < 0.003 and abs(q - 0.5) < 0.03 and abs(m - 200) < 5


def test_fit_bass_rejects_too_few_points():
    with pytest.raises(ValueError):
        diffusion.fit_bass(np.array([0.0, 1.0]), np.array([1.0, 2.0]))


def test_fit_with_launch_recovers_launch_year():
    calendar = np.arange(2018, 2026)
    y = diffusion.bass_path(0.02, 0.45, 9.0, calendar - 2010)
    fit = diffusion.fit_bass_with_launch(calendar, y, range(2000, 2018))
    assert fit["launch_year"] == 2010
    assert fit["m"] == pytest.approx(9.0, rel=0.05)


def test_us_stress_series_has_a_source_for_each_value():
    for year, row in diffusion.US_STRESS_SERIES.items():
        assert 2018 <= year <= 2025
        if row["value_usd"] is not None:
            assert row["source"] and row["locator"]


def test_main_diffusion_uses_prior_when_no_analog_survives():
    main = diffusion.main_parameters(diffusion.ANALOGS)
    assert all(a["status"] == "DROPPED" for a in diffusion.ANALOGS)
    assert (main["p"], main["q"]) == (0.03, 0.38)
    assert main["basis"] == "registered_prior"
