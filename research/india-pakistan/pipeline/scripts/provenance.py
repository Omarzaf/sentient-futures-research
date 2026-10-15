"""Manage local source and raw-file provenance without altering existing raw bytes."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FIELDS = [
    "source_id",
    "title",
    "publisher",
    "url",
    "year",
    "accessed",
    "tier",
    "access_method",
    "license",
    "notes",
]
MANIFEST_FIELDS = [
    "file",
    "url",
    "accessed_utc",
    "sha256",
    "license",
    "source_id",
    "notes",
]
__all__ = ["ROOT", "read_csv", "register_raw", "upsert_source", "write_csv"]


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV, returning no records when it does not exist."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    """Write a deterministic CSV with an explicit schema."""
    if path.parent == ROOT / "data/processed" and path.name != "sources.csv":
        sources = {
            row["source_id"]: row["tier"]
            for row in read_csv(ROOT / "data/processed/sources.csv")
        }
        fields = list(dict.fromkeys([*fields, "tier", "source_tier"]))
        tagged = []
        for incoming in rows:
            row = dict(incoming)
            source = row.get("source_id", "")
            if source not in sources:
                raise ValueError(f"Unregistered processed source: {source}")
            row["source_tier"] = sources[source]
            derived = (
                path.stem.startswith("protein_model_")
                or path.stem
                in {
                    "protein_intake_modelled",
                    "protein_gap",
                    "protein_gap_group_summary",
                    "region_boundary_crosswalk",
                }
                or row.get("metric")
                == "apparent_consumption_production_plus_imports_minus_exports"
                or row.get("affected_count_method", "").startswith(
                    "published_rate_times"
                )
            )
            row["tier"] = "derived" if derived else row.get("tier") or sources[source]
            if row["tier"] not in {"A", "B", "C", "D", "derived"}:
                raise ValueError(f"Invalid processed tier: {row['tier']}")
            tagged.append(row)
        rows = tagged
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def upsert_source(row: dict[str, str]) -> None:
    """Register an explicitly identified source, preserving unrelated rows."""
    path = ROOT / "data/processed/sources.csv"
    rows = read_csv(path)
    rows = [old for old in rows if old["source_id"] != row["source_id"]]
    rows.append(row)
    write_csv(path, SOURCE_FIELDS, sorted(rows, key=lambda record: record["source_id"]))


def register_raw(
    relative: str,
    url: str,
    source_id: str,
    license_text: str,
    notes: str = "",
    accessed_utc: str | None = None,
) -> None:
    """Register new evidence with an explicit date; preserve existing raw identity."""
    path = ROOT / relative
    if not path.is_file() or not path.resolve().is_relative_to(
        (ROOT / "data/raw").resolve()
    ):
        raise ValueError(f"Not a raw file inside this project: {relative}")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    target = ROOT / "data/raw/MANIFEST.csv"
    existing = read_csv(target)
    matches = [old for old in existing if old["file"] == relative]
    if len(matches) > 1:
        raise ValueError(f"Duplicate raw identity in manifest: {relative}")
    if matches:
        previous = matches[0]
        identity = {"sha256": digest, "url": url, "source_id": source_id}
        if any(previous.get(field) != value for field, value in identity.items()):
            raise ValueError(
                f"A registered raw identity changed; use a new evidence path: {relative}"
            )
        if accessed_utc is None:
            # Existing dates retain their historical provenance. A routine rebuild
            # cannot make an mtime-derived old timestamp independently verified.
            return
    if not accessed_utc:
        raise ValueError(
            f"New evidence needs an explicit retrieval timestamp: {relative}"
        )
    try:
        observed = datetime.fromisoformat(accessed_utc)
    except ValueError as exc:
        raise ValueError("Retrieval timestamp must be timezone-aware ISO 8601") from exc
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError("Retrieval timestamp must be timezone-aware ISO 8601")
    row = {
        "file": relative,
        "url": url,
        "accessed_utc": accessed_utc,
        "sha256": digest,
        "license": license_text,
        "source_id": source_id,
        "notes": notes,
    }
    rows = [old for old in existing if old["file"] != relative]
    rows.append(row)
    write_csv(target, MANIFEST_FIELDS, sorted(rows, key=lambda record: record["file"]))
