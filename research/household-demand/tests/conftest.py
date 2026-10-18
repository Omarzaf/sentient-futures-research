"""Shared fixtures for the household-demand tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixture_dir() -> Path:
    """Return the six-household HCES fixture written by ``make_hces_mini.py``."""
    return FIXTURES / "hces_mini"
