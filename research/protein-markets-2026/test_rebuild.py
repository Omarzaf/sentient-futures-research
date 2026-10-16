"""Check that source integrity cannot silently authorize research estimates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "readiness", Path(__file__).with_name("rebuild.py")
)
assert SPEC is not None and SPEC.loader is not None
READINESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(READINESS)


def _manifest(path: str, payload: bytes) -> dict:
    """Create an integrity fixture without inventing empirical evidence."""
    return {
        "files": [
            {
                "id": "source",
                "path": path,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "source_type": "published_table_transcription",
            }
        ]
    }


def test_verified_table_is_not_microdata_reproduction(tmp_path: Path) -> None:
    """A hash-valid published value must leave the estimation gate held."""
    payload = b"published official value, not respondent records"
    (tmp_path / "table.txt").write_bytes(payload)
    (tmp_path / "input-manifest.json").write_text(
        json.dumps(_manifest("table.txt", payload)), encoding="utf-8"
    )
    result = READINESS.build_readiness(tmp_path, tmp_path / "tables")
    assert result["integrity_failures"] == []
    assert result["reproduction_gate"] == "HOLD"
    assert result["new_estimation_allowed"] is False
    assert result["projection_allowed"] is False
    assert result["research_complete"] is False


def test_tampered_source_is_detected(tmp_path: Path) -> None:
    """Changing the raw bytes after receipt must fail the identity check."""
    (tmp_path / "input.txt").write_bytes(b"changed")
    rows = READINESS.audit_inputs(tmp_path, _manifest("input.txt", b"original"))
    assert rows[0]["integrity_status"] == "mismatch"


def test_missing_input_stays_missing(tmp_path: Path) -> None:
    """An absent source must not be accepted as a zero or a valid observation."""
    rows = READINESS.audit_inputs(tmp_path, _manifest("missing.txt", b"original"))
    assert rows[0]["integrity_status"] == "missing"
    assert rows[0]["actual_sha256"] == ""


@pytest.mark.parametrize("path", ["../outside.txt", "/outside.txt"])
def test_escaping_source_paths_are_rejected(tmp_path: Path, path: str) -> None:
    """Private source resolution must not escape its explicitly selected root."""
    with pytest.raises(ValueError, match="within"):
        READINESS.audit_inputs(tmp_path, _manifest(path, b"original"))


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    """A symlink cannot bypass source-path containment."""
    data = tmp_path / "data"
    data.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"original")
    (data / "linked.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="outside"):
        READINESS.audit_inputs(data, _manifest("linked.txt", b"original"))


def test_duplicate_source_identity_is_rejected(tmp_path: Path) -> None:
    """Ambiguous manifest identities must not be silently collapsed."""
    manifest = _manifest("input.txt", b"original")
    manifest["files"].append(dict(manifest["files"][0]))
    with pytest.raises(ValueError, match="Duplicate"):
        READINESS.audit_inputs(tmp_path, manifest)


def test_missing_manifest_does_not_authorize_estimation(tmp_path: Path) -> None:
    """Readiness output remains explicitly held when all input evidence is absent."""
    result = READINESS.build_readiness(tmp_path, tmp_path / "tables")
    assert result["input_manifest_present"] is False
    assert result["completion_criterion_met_by_this_command"] is False
    assert result["new_estimation_allowed"] is False


def test_second_rebuild_has_identical_bytes(tmp_path: Path) -> None:
    """Unchanged inputs must produce unchanged readiness tables."""
    output = tmp_path / "tables"
    READINESS.build_readiness(tmp_path, output)
    first = {path.name: path.read_bytes() for path in output.iterdir()}
    READINESS.build_readiness(tmp_path, output)
    assert first == {path.name: path.read_bytes() for path in output.iterdir()}
