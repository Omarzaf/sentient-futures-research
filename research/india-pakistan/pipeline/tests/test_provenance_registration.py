"""Prevent filesystem dates and changed bytes from rewriting retrieval evidence."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import provenance


def raw_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated raw file and point registration at the temporary root."""
    monkeypatch.setattr(provenance, "ROOT", tmp_path)
    folder = tmp_path / "data/raw"
    folder.mkdir(parents=True)
    (folder / "source.txt").write_text("source evidence")
    return folder


def test_new_registration_requires_observed_timestamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An mtime cannot stand in for a source retrieval event."""
    folder = raw_project(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="explicit retrieval timestamp"):
        provenance.register_raw(
            "data/raw/source.txt", "https://example.org/source", "s1", "unknown"
        )
    assert not (folder / "MANIFEST.csv").exists()


def test_repeated_registration_preserves_historical_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A no-timestamp repeat may reuse identical evidence without rewriting its date."""
    folder = raw_project(tmp_path, monkeypatch)
    provenance.register_raw(
        "data/raw/source.txt",
        "https://example.org/source",
        "s1",
        "unknown",
        accessed_utc="2026-10-13T20:00:00+00:00",
    )
    before = (folder / "MANIFEST.csv").read_bytes()
    provenance.register_raw(
        "data/raw/source.txt", "https://example.org/source", "s1", "unknown"
    )
    assert (folder / "MANIFEST.csv").read_bytes() == before


def test_changed_raw_bytes_need_a_new_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Do not silently replace a registered raw checksum with mutated bytes."""
    folder = raw_project(tmp_path, monkeypatch)
    provenance.register_raw(
        "data/raw/source.txt",
        "https://example.org/source",
        "s1",
        "unknown",
        accessed_utc="2026-10-13T20:00:00+00:00",
    )
    before = (folder / "MANIFEST.csv").read_bytes()
    (folder / "source.txt").write_text("changed source evidence")
    with pytest.raises(ValueError, match="registered raw identity changed"):
        provenance.register_raw(
            "data/raw/source.txt",
            "https://example.org/source",
            "s1",
            "unknown",
            accessed_utc="2026-10-13T21:00:00+00:00",
        )
    assert (folder / "MANIFEST.csv").read_bytes() == before


@pytest.mark.parametrize(
    "timestamp", ["2026-10-13", "not a date", "2026-10-13T20:00:00"]
)
def test_new_timestamp_must_have_timezone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, timestamp: str
) -> None:
    """A retrieval event needs a parseable timezone-aware timestamp."""
    raw_project(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="timezone-aware"):
        provenance.register_raw(
            "data/raw/source.txt",
            "https://example.org/source",
            "s1",
            "unknown",
            accessed_utc=timestamp,
        )
