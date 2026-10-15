"""Assemble source-bound cultural findings while retaining scope and survey metadata."""

from __future__ import annotations

import hashlib
import json
from collections import Counter

from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = ["build"]

FIELDS = [
    "country",
    "region",
    "dimension",
    "finding",
    "value",
    "unit",
    "date",
    "source_id",
    "evidence_source_ids",
    "table_page",
    "sample_size",
    "denominator",
    "fieldwork_dates",
    "evidence_scope",
    "notes",
]


def build() -> None:
    """Validate staged evidence, register originals and assemble both countries."""
    directories = [ROOT / "scripts/cultural" / c for c in ("india", "pakistan")]
    source_rows = [r for d in directories for r in read_csv(d / "source_rows.csv")]
    manifest_rows = [r for d in directories for r in read_csv(d / "manifest_rows.csv")]
    rows = [r for d in directories for r in read_csv(d / "cultural_rows.csv")]
    sources = {r["source_id"]: r for r in read_csv(ROOT / "data/processed/sources.csv")}
    staged_sources: dict[str, dict[str, str]] = {}
    for row in source_rows:
        source_id = row["source_id"]
        if source_id in staged_sources and staged_sources[source_id] != row:
            raise ValueError(f"Conflicting staged source: {source_id}")
        if row["tier"] not in ("A", "B", "C", "D"):
            raise ValueError(f"Invalid source tier: {source_id}")
        staged_sources[source_id] = row
    sources.update(staged_sources)
    for row in manifest_rows:
        path = ROOT / row["file"]
        if not path.resolve().is_relative_to((ROOT / "data/raw").resolve()):
            raise ValueError(f"Raw path outside evidence directory: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"Staged raw hash mismatch: {row['file']}")
        if row["source_id"] not in sources:
            raise ValueError(f"Unresolved raw source: {row['source_id']}")
    for row in rows:
        for field in ("country", "region", "dimension", "finding", "source_id"):
            if not row.get(field, "").strip():
                raise ValueError(f"Missing {field} in cultural finding: {row}")
        references = {row["source_id"]}
        references.update(filter(None, row.get("evidence_source_ids", "").split(";")))
        if references - sources.keys():
            raise ValueError(
                f"Unresolved finding sources: {references - sources.keys()}"
            )
        if row["country"] not in ("India", "Pakistan"):
            raise ValueError(f"Unexpected country: {row['country']}")
        if not row.get("table_page") or not row.get("evidence_scope"):
            raise ValueError(f"Missing evidence locator or scope: {row}")
        if row.get("value") and not row.get("unit"):
            raise ValueError(f"Numeric finding without unit: {row}")
    for row in staged_sources.values():
        upsert_source(row)
    for row in manifest_rows:
        register_raw(
            row["file"],
            row["url"],
            row["source_id"],
            row["license"],
            row.get("notes", ""),
            row["accessed_utc"],
        )
    extra = sorted({key for row in rows for key in row} - set(FIELDS))
    fields = FIELDS + extra
    normalized = [{f: row.get(f, "") for f in fields} for row in rows]
    normalized.sort(
        key=lambda r: (r["country"], r["dimension"], r["region"], r["finding"])
    )
    write_csv(ROOT / "data/processed/cultural_context.csv", fields, normalized)
    summary = {
        "output_sha256": hashlib.sha256(
            (ROOT / "data/processed/cultural_context.csv").read_bytes()
        ).hexdigest(),
        "rows": len(rows),
        "country_rows": dict(Counter(row["country"] for row in rows)),
        "dimensions": {
            country: sorted({r["dimension"] for r in rows if r["country"] == country})
            for country in ("India", "Pakistan")
        },
        "registered_source_rows": len(staged_sources),
        "registered_raw_rows": len(manifest_rows),
        "note": "Counts describe this evidence table, not cultural prevalence or acceptance.",
    }
    (ROOT / "logs/m7-build.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    build()
