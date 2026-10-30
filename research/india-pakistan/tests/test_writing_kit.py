"""Test that numeric writing-kit coverage fails closed under text changes."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "verify_writing_kit", Path(__file__).parents[1] / "tools/verify_writing_kit.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_new_or_changed_number_fails_coverage() -> None:
    """A changed displayed amount cannot reuse a verified occurrence."""
    mapping = [
        {
            "line": 1,
            "source": "kit/example.md",
            "source_line": 5,
            "text": "$112.7 million",
        }
    ]
    claims = [
        {
            "occurrence_file": "kit/example.md",
            "occurrence_line": "5",
            "display_token": "112.7",
            "status": "verified",
        }
    ]
    assert MODULE.check_coverage(mapping, claims) == []
    mapping[0]["text"] = "$113.7 million"
    assert len(MODULE.check_coverage(mapping, claims)) == 1


def test_unresolved_or_duplicate_occurrence_cannot_clear_gate() -> None:
    """An unresolved row or single row for repeated numbers is insufficient."""
    mapping = [
        {
            "line": 1,
            "source": "kit/example.md",
            "source_line": 5,
            "text": "2026 and 2026",
        }
    ]
    claims = [
        {
            "occurrence_file": "kit/example.md",
            "occurrence_line": "5",
            "display_token": "2026",
            "status": "unresolved",
        }
    ]
    assert len(MODULE.check_coverage(mapping, claims)) == 2
    claims[0]["status"] = "verified"
    assert len(MODULE.check_coverage(mapping, claims)) == 1


def test_link_dates_and_identifiers_are_not_measurements() -> None:
    """Dates in a URL do not substitute for numbers in visible evidence."""
    line = "[Source](https://example.org/2025/351.pdf) D01 R06 `file-2026.csv` Table A1.6: 40.4%"
    assert MODULE.numeric_tokens(line) == ["40.4%"]
