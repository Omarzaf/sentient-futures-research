"""Exercise explicit selection, derivative classification and safe cache promotion."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import BinaryIO

import pytest

EDITION = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "public_input_fetcher", EDITION / "data/fetch_raw.py"
)
assert SPEC and SPEC.loader
fetcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetcher)


def source(payload: bytes = b"synthetic bytes") -> dict[str, str]:
    """Create a synthetic original-byte manifest entry, never a research observation."""
    return {
        "file": "data/raw/example.pdf",
        "url": "https://example.org/example.pdf",
        "source_id": "synthetic",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "notes": "Original downloaded bytes.",
    }


def transport(payload: bytes):
    """Return an offline byte writer with the same narrow transport contract."""

    def write(
        url: str, stream: BinaryIO, timeout: float, max_bytes: int
    ) -> dict[str, object]:
        """Write fixture bytes without constructing a network connection."""
        stream.write(payload)
        return {"http_status": 200, "final_url": url}

    return write


def test_exact_bytes_are_promoted_and_repeat_does_not_fetch(tmp_path: Path) -> None:
    """Matching bytes enter the cache once, with unchanged timestamps on repeats."""
    row = source()
    result = fetcher.fetch(row, tmp_path, transport=transport(b"synthetic bytes"))
    target = tmp_path / row["file"]
    assert result["outcome"] == "verified" and target.read_bytes() == b"synthetic bytes"
    before = target.stat().st_mtime_ns

    def reject(*args: object) -> dict[str, object]:
        """Prove an accepted cached file causes no repeated request."""
        raise AssertionError("Unexpected retrieval")

    assert (
        fetcher.fetch(row, tmp_path, transport=reject)["outcome"] == "already_verified"
    )
    assert target.stat().st_mtime_ns == before


def test_mismatch_is_logged_but_never_promoted(tmp_path: Path) -> None:
    """Changed live bytes cannot silently replace the historical identity."""
    row = source()
    result = fetcher.fetch(row, tmp_path, transport=transport(b"changed"))
    assert result["outcome"] == "hash_mismatch"
    assert not (tmp_path / row["file"]).exists()
    assert not list(tmp_path.rglob(".pending-*"))
    receipt = json.loads((tmp_path / "fetch-receipts.jsonl").read_text())
    assert receipt["actual_sha256"] != receipt["expected_sha256"]


def test_existing_conflict_is_preserved(tmp_path: Path) -> None:
    """Neither accepted nor conflicting existing bytes may be overwritten."""
    row = source()
    target = tmp_path / row["file"]
    target.parent.mkdir(parents=True)
    target.write_bytes(b"keep these bytes")
    result = fetcher.fetch(row, tmp_path, transport=transport(b"synthetic bytes"))
    assert result["outcome"] == "existing_conflict_preserved"
    assert target.read_bytes() == b"keep these bytes"


@pytest.mark.parametrize(
    "name",
    [
        "../escape.pdf",
        "/tmp/escape.pdf",
        "data/raw/../../escape.pdf",
        "data/raw/./file.pdf",
        "data/raw/a\\b.pdf",
    ],
)
def test_path_traversal_rejected_before_fetch(tmp_path: Path, name: str) -> None:
    """Manifest identities cannot escape or normalize into a different path."""
    row = dict(source(), file=name)
    with pytest.raises(ValueError, match="Unsafe"):
        fetcher.fetch(row, tmp_path, transport=transport(b"synthetic bytes"))
    assert not list(tmp_path.iterdir())


def test_cache_symlink_cannot_escape(tmp_path: Path) -> None:
    """An apparently nested destination cannot redirect writes through a symlink."""
    cache, outside = tmp_path / "cache", tmp_path / "outside"
    cache.mkdir()
    outside.mkdir()
    (cache / "data").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="Symlink"):
        fetcher.fetch(source(), cache, transport=transport(b"synthetic bytes"))
    assert not list(outside.iterdir())


def test_size_limit_rejects_mocked_oversized_response(tmp_path: Path) -> None:
    """The promotion layer checks size even when the transport is replaced."""
    row = source(b"large fixture")
    result = fetcher.fetch(
        row, tmp_path, transport=transport(b"large fixture"), max_bytes=2
    )
    assert result["outcome"] == "retrieval_failed"
    assert not (tmp_path / row["file"]).exists()


def test_cache_inside_public_checkout_is_rejected() -> None:
    """Downloading inputs cannot populate the publication checkout."""
    with pytest.raises(ValueError, match="outside the public checkout"):
        fetcher.fetch(
            source(), EDITION / "input-cache", transport=transport(b"synthetic bytes")
        )


def test_transport_failure_is_logged_without_partial_file(tmp_path: Path) -> None:
    """A failed response does not leave a seemingly accepted input."""

    def fail(
        url: str, stream: BinaryIO, timeout: float, max_bytes: int
    ) -> dict[str, object]:
        """Simulate an interrupted transfer after some bytes arrive."""
        stream.write(b"partial")
        raise OSError("synthetic connection interruption")

    result = fetcher.fetch(source(), tmp_path, transport=fail)
    assert result["outcome"] == "retrieval_failed"
    assert not (tmp_path / source()["file"]).exists()
    assert not list(tmp_path.rglob(".pending-*"))


def test_private_dns_resolution_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A public-looking hostname cannot resolve into a local service."""
    monkeypatch.setattr(
        fetcher.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(2, 1, 6, "", ("127.0.0.1", 443))],
    )
    result = fetcher.fetch(source(), tmp_path)
    assert result["outcome"] == "retrieval_failed"
    assert "nonpublic" in result["error"]


def test_redirects_are_not_followed() -> None:
    """Redirect targets need separate manifest review rather than implicit access."""
    assert (
        fetcher.NoRedirect().redirect_request(
            None, None, 302, "redirect", None, "https://example.net/new"
        )
        is None
    )


@pytest.mark.parametrize(
    "change,expected",
    [
        (
            {"file": "data/raw/example.txt", "notes": "Derived PDF text"},
            "derived_or_captured",
        ),
        ({"file": "data/raw/example.pdf.headers"}, "acquisition_metadata"),
        ({"file": "data/raw/example.request.json"}, "acquisition_metadata"),
        ({"url": "local://calculation"}, "local_artifact"),
        ({"notes": "FAILED ACQUISITION; HTTP404"}, "failure_diagnostic"),
        ({"notes": "Original downloaded bytes; read-only POST."}, "unsupported_method"),
        ({"url": "https://127.0.0.1/private.pdf"}, "unsupported_url"),
        ({"url": "https://example.org/file.pdf#page2"}, "unsupported_url"),
    ],
)
def test_non_original_artifacts_never_fetch(
    tmp_path: Path, change: dict[str, str], expected: str
) -> None:
    """Context URLs cannot pretend to reproduce locally generated artifacts."""
    row = dict(source(), **change)
    assert fetcher.classify(row)[0] == expected
    result = fetcher.fetch(row, tmp_path, transport=transport(b"synthetic bytes"))
    assert result["outcome"] == "not_retrievable"
    assert not (tmp_path / row["file"]).exists()


def test_selectors_are_required_and_exact() -> None:
    """No-selector invocation and misspelled IDs cannot become bulk downloads."""
    rows = [source()]
    for files, sources in [([], []), (["typo"], []), ([], ["typo"])]:
        with pytest.raises(ValueError):
            fetcher.select(rows, files, sources)
    assert fetcher.select(rows, [], ["synthetic"]) == rows


def test_manifest_duplicate_rejected(tmp_path: Path) -> None:
    """Duplicate filename identities are rejected before requesting bytes."""
    path = tmp_path / "manifest.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(source()))
        writer.writeheader()
        writer.writerows([source(), source()])
    with pytest.raises(ValueError, match="Duplicate"):
        fetcher.load_manifest(path)


def test_full_manifest_and_offline_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Validate all 1,987 metadata rows without downloading any of them."""
    rows = fetcher.load_manifest(EDITION / "data/MANIFEST.csv")
    assert len(rows) == 1987
    assert all(fetcher.classify(row)[0] for row in rows)
    cache = tmp_path / "unused-cache"
    assert (
        fetcher.main(
            ["--source", rows[0]["source_id"], "--cache-dir", str(cache), "--list"]
        )
        == 0
    )
    assert capsys.readouterr().out and not cache.exists()


def test_later_manifest_additions_preserve_retrieval_boundaries() -> None:
    """Bind the 13 reviewed additions to their public or restricted byte classes."""
    # Commits 3b69531, 29d0928 and a5e2954 added 3, 8 and 2 records respectively;
    # all 1,974 records from the 13 October edition remain unchanged.
    additions = {
        "jobs/companies-with-jobs-on-altprotein-jobs.xlsx": "local_artifact",
        "jobs/global-vacancy-data-2023-2025.xlsx": "local_artifact",
        "market/indexbox-asia-plant-based-portfolio.txt": "derived_or_captured",
        "proxy/gfi-us-retail-market-research.html": "original_candidate",
        "proxy/imf-weo-2026-10-LP.json": "original_candidate",
        "proxy/imf-weo-2026-10-NGDP_RPCH.json": "original_candidate",
        "proxy/imf-weo-2026-10-PCPIPCH.json": "original_candidate",
        "proxy/imf-weo-2026-10-PPPPC.json": "original_candidate",
        "proxy/imf-weo-indicator-metadata.json": "original_candidate",
        "proxy/worldbank-NY.GDP.PCAP.CD.json": "original_candidate",
        "proxy/worldbank-NY.GDP.PCAP.CN.json": "original_candidate",
        "proxy/worldbank-PA.NUS.FCRF.json": "original_candidate",
        "proxy/worldbank-SP.URB.TOTL.IN.ZS.json": "original_candidate",
    }
    rows = {
        row["file"]: row for row in fetcher.load_manifest(EDITION / "data/MANIFEST.csv")
    }
    for relative, expected in additions.items():
        path = "data/raw/altprotein/" + relative
        assert path in rows, path
        assert fetcher.classify(rows[path])[0] == expected, path
