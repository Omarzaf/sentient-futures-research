"""Protect country substitution from silently changing forecast units or scope."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "elicitation", Path(__file__).with_name("prepare_elicitation.py")
)
assert SPEC is not None and SPEC.loader is not None
ELICITATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ELICITATION)

TEXT = """market in the U.S.
terms of US sales
total US retail dollar sales
for U.S. plant-based food retail sales
what will be the US
US consumer sales
2025 US dollars
CPI-U, Food at Home, U.S. city average
cultivated includes pet food; hybrids overlap; resources permit existing forecasts"""


@pytest.mark.parametrize("country", ["India", "Pakistan"])
def test_geography_changes_preserve_units_and_study_scope(country: str) -> None:
    """The geography edit must not mutate the price basis or definition exceptions."""
    result, changes = ELICITATION.adapt_text(TEXT, country)
    assert f"market in {country}." in result
    assert "2025 US dollars" in result
    assert "CPI-U, Food at Home, U.S. city average" in result
    assert (
        "cultivated includes pet food; hybrids overlap; resources permit existing forecasts"
        in result
    )
    assert len(changes) == 6


def test_unreviewed_extraction_requires_new_review() -> None:
    """An unmatched source phrase must fail instead of producing a partial adaptation."""
    with pytest.raises(ValueError, match="differs"):
        ELICITATION.adapt_text(
            TEXT.replace("US consumer sales", "other wording"), "India"
        )


def test_changed_original_instrument_stops_before_adaptation(tmp_path: Path) -> None:
    """A different original document cannot inherit the reviewed instrument identity."""
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs/elicitation-original.docx").write_bytes(b"different document")
    with pytest.raises(ValueError, match="identity differs"):
        ELICITATION.prepare(tmp_path)
