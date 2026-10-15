"""Register sentiment acquisition evidence without promoting unlabelled hits."""

from __future__ import annotations

import hashlib

from provenance import ROOT, read_csv, register_raw, upsert_source

__all__ = ["register"]


def register() -> None:
    """Merge staged sources and verified raw metadata into the shared ledgers."""
    base = ROOT / "scripts/sentiment"
    sources = read_csv(base / "source_rows.csv")
    manifest = read_csv(base / "manifest_rows.csv")
    if not sources or not manifest:
        raise ValueError("Sentiment acquisition staging is not ready")
    sources.extend(read_csv(base / "review/source_rows.csv"))
    manifest.extend(read_csv(base / "review/manifest_rows.csv"))
    for row in manifest:
        if (
            hashlib.sha256((ROOT / row["file"]).read_bytes()).hexdigest()
            != row["sha256"]
        ):
            raise ValueError(f"Staged sentiment raw hash mismatch: {row['file']}")
    for row in sources:
        upsert_source(row)
    for row in manifest:
        register_raw(
            row["file"],
            row["url"],
            row["source_id"],
            row["license"],
            row.get("notes", ""),
            row.get("accessed_utc") or None,
        )
    print(f"Registered {len(sources)} sources and {len(manifest)} raw artifacts")
    print("Unlabelled query hits remain in staging; no sentiment estimate published")


if __name__ == "__main__":
    register()
