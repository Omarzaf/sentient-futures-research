"""Shared fixtures for the household-demand tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixture_dir() -> Path:
    """Return the six-household HCES fixture written by ``make_hces_mini.py``."""
    return FIXTURES / "hces_mini"


@pytest.fixture(scope="session")
def pk_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Write the six-household HIES fixture ZIP with ``make_hies_mini.py``.

    The repository ignores ``*.zip``, so the fixture is rebuilt for each test
    session from the generator instead of being committed.
    """
    spec = importlib.util.spec_from_file_location(
        "make_hies_mini", FIXTURES / "make_hies_mini.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_fixture(tmp_path_factory.mktemp("hies") / "hies_mini.zip")
