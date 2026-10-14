"""Audit source resolution and immutable raw hashes for the local research handoff."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from provenance import ROOT, read_csv

__all__ = ["audit"]


def audit() -> None:
    """Reject unregistered raw files, changed bytes and unresolved source references."""
    sources = read_csv(ROOT / "data/processed/sources.csv")
    source_ids = {row["source_id"] for row in sources}
    errors = []
    if len(source_ids) != len(sources):
        errors.append("Duplicate source IDs")
    for row in sources:
        if row["tier"] not in ("A", "B", "C", "D"):
            errors.append(f"Invalid tier: {row['source_id']}")
    manifest = read_csv(ROOT / "data/raw/MANIFEST.csv")
    paths = {row["file"] for row in manifest}
    if len(paths) != len(manifest):
        errors.append("Duplicate raw manifest paths")
    for row in manifest:
        path = ROOT / row["file"]
        if not path.is_file():
            errors.append(f"Missing raw file: {row['file']}")
            continue
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        if actual != row["sha256"]:
            errors.append(f"Changed raw bytes: {row['file']}")
        if row["source_id"] and row["source_id"] not in source_ids:
            errors.append(f"Unresolved raw source: {row['file']}")
    actual_files = {
        str(p.relative_to(ROOT))
        for p in (ROOT / "data/raw").rglob("*")
        if p.is_file() and p.name != "MANIFEST.csv"
    }
    errors.extend(f"Unregistered raw file: {p}" for p in sorted(actual_files - paths))
    datasets = {}
    for path in sorted((ROOT / "data/processed").glob("*.csv")):
        rows = read_csv(path)
        datasets[path.name] = len(rows)
        for index, row in enumerate(rows, start=2):
            for field, value in row.items():
                if field.endswith("_source_ids") and value:
                    for source_id in value.split(";"):
                        if source_id.strip() not in source_ids:
                            errors.append(
                                f"{path.name}:{index}: unresolved {field}={source_id}"
                            )
                if (
                    (field == "source_id" or field.endswith("_source_id"))
                    and value
                    and value not in source_ids
                ):
                    errors.append(f"{path.name}:{index}: unresolved {field}={value}")
    verifier = ROOT / "verify_plan.py"
    verifier_hash = hashlib.sha256(verifier.read_bytes()).hexdigest()
    if (
        verifier_hash
        != "a0dce0308eb9965e29da0157b6557e285ab54fba351380719ffc13306d39126d"
    ):
        errors.append("Immutable verifier hash changed")
    result = {
        "checked_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "pass": not errors,
        "source_records": len(sources),
        "raw_manifest_records": len(manifest),
        "raw_files_present": len(actual_files),
        "datasets": datasets,
        "verifier_sha256": verifier_hash,
        "errors": errors,
    }
    (ROOT / "logs/iteration-provenance-audit.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    audit()
