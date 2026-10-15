"""Synthetic edge-case fixtures; these numbers are never research observations."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_national import fbs_observations


def source_row(code: str, value: str, year: str = "2010") -> dict[str, str]:
    """Create a synthetic observation to test missing-versus-zero arithmetic."""
    return {
        "Area": "India",
        "Area Code": "100",
        "Item": "Bovine Meat",
        "Item Code": "2731",
        "Element Code": code,
        "Year": year,
        "Unit": "1000 t",
        "Value": value,
        "Flag": "E",
    }


def test_missing_import_does_not_become_zero() -> None:
    """Omit apparent consumption when a trade component is absent."""
    rows, omissions = fbs_observations(
        [source_row("5511", "100"), source_row("5911", "25")]
    )
    assert len(rows) == 2
    assert len(omissions) == 1
    assert omissions[0]["missing_elements"] == "5611"


def test_explicit_zero_remains_a_source_value() -> None:
    """Use a reported zero while preserving source flags and the exact formula."""
    rows, omissions = fbs_observations(
        [
            source_row("5511", "100.10"),
            source_row("5611", "0"),
            source_row("5911", "25.05"),
        ]
    )
    derived = [row for row in rows if row["metric"].startswith("apparent_consumption")]
    assert not omissions
    assert len(derived) == 1
    assert Decimal(derived[0]["value"]) == Decimal("75.05")
    assert "5611=E" in derived[0]["flag"]
    assert "retail sales" in derived[0]["notes"]


def test_periods_are_never_joined_across_years() -> None:
    """Prevent a present trade value from filling a different reporting year."""
    rows, omissions = fbs_observations(
        [
            source_row("5511", "100", "2010"),
            source_row("5611", "5", "2011"),
            source_row("5911", "25", "2010"),
        ]
    )
    assert len(omissions) == 2
    assert not any(row["metric"].startswith("apparent_consumption") for row in rows)


def test_blank_component_remains_missing() -> None:
    """A blank reported component must not produce a numeric derived value."""
    rows, omissions = fbs_observations(
        [source_row("5511", "100"), source_row("5611", ""), source_row("5911", "25")]
    )
    assert len(omissions) == 1
    assert not any(row["metric"].startswith("apparent_consumption") for row in rows)


def test_same_label_companion_code_is_not_double_counted() -> None:
    """Keep only the declared display code when two item codes share a label."""
    selected = source_row("5511", "10")
    selected.update({"Item": "Eggs", "Item Code": "2949"})
    companion = dict(selected, **{"Item Code": "2744", "Flag": "I"})
    rows, _ = fbs_observations([selected, companion])
    assert len(rows) == 1
    assert rows[0]["item_code"] == "2949"
    assert rows[0]["flag"] == "E"


def test_duplicate_complete_code_is_rejected() -> None:
    """Fail instead of overwriting when the full source identity is duplicated."""
    row = source_row("5511", "10")
    try:
        fbs_observations([row, row])
    except ValueError as error:
        assert "Duplicate coded" in str(error)
    else:
        raise AssertionError("Duplicate code was silently accepted")
