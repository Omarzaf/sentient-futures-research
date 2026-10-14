"""Integrate the frozen supervisor batch without refreshing historical receipts."""

from __future__ import annotations

import hashlib
from datetime import datetime

from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = ["register"]

REVISION = "scripts/altprotein/supervisor_revision_20261013"
CUTOFF = 2025
TABLES = {
    "policy_rows.csv": ("altprotein_policy.csv", "policy_id", "policy_date"),
    "company_rows.csv": ("altprotein_companies.csv", "company", "status_evidence_date"),
    "company_exclusions.csv": (
        "altprotein_company_exclusions.csv",
        "company",
        "status_evidence_date",
    ),
    "retail_listing_rows.csv": ("altprotein_retail_offers.csv", "listing_id", ""),
}


def indexed(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    """Reject duplicate identities before registering or writing any evidence."""
    result = {row[key]: row for row in rows}
    if len(result) != len(rows) or "" in result:
        raise ValueError(f"Duplicate or empty {key} in evidence table")
    return result


def dated_row(
    row: dict[str, str], source: dict[str, str], date_field: str
) -> dict[str, str]:
    """Keep source year distinct from event freshness and unknown publication dates."""
    result = dict(row)
    result["source_year"] = source["year"]
    evidence_year = row.get(date_field, "")[:4] if date_field else ""
    if evidence_year and not evidence_year.isdigit():
        raise ValueError(f"Invalid evidence date in {date_field}")
    result["policy_year" if date_field == "policy_date" else "evidence_year"] = (
        evidence_year
    )
    result["freshness_cutoff_year"] = str(CUTOFF)
    result["freshness_basis"] = (
        date_field or "Source publication date unknown; observed_date is access only"
    )
    result["stale"] = (
        str(int(evidence_year) < CUTOFF).lower() if evidence_year else "unknown"
    )
    result["freshness"] = (
        "undated_source_access_only"
        if not evidence_year
        else (
            "historical_evidence_pre2025"
            if int(evidence_year) < CUTOFF
            else "dated_evidence_2025_or_later"
        )
    )
    if row["tier"] != source["tier"]:
        raise ValueError(f"Staged source tier differs for {row['source_id']}")
    return result


def register() -> None:
    """Publish frozen rows and only new source/receipt identities after preflight."""
    base = ROOT / REVISION
    new_sources = indexed(read_csv(base / "source_rows.csv"), "source_id")
    old_sources = indexed(read_csv(ROOT / "data/processed/sources.csv"), "source_id")
    frozen_sources = indexed(
        read_csv(base / "reused_source_rows.csv") + list(new_sources.values()),
        "source_id",
    )
    for source_id, row in new_sources.items():
        if source_id in old_sources and old_sources[source_id] != row:
            raise ValueError(
                f"New source identity conflicts with registry: {source_id}"
            )
    registry = old_sources | new_sources
    receipts = indexed(read_csv(base / "manifest_rows.csv"), "file")
    previous = indexed(read_csv(ROOT / "data/raw/MANIFEST.csv"), "file")
    for relative, row in receipts.items():
        path = ROOT / relative
        if not path.is_file() or not path.resolve().is_relative_to(
            (ROOT / "data/raw").resolve()
        ):
            raise ValueError(f"Missing or invalid staged raw file: {relative}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError(f"Staged raw hash differs: {relative}")
        stamp = datetime.fromisoformat(row["accessed_utc"])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError(f"Staged receipt lacks timezone: {relative}")
        if row["source_id"] not in registry:
            raise ValueError(f"Raw source is unresolved: {relative}")
        if relative in previous and any(
            previous[relative][key] != row[key]
            for key in ("sha256", "url", "source_id")
        ):
            raise ValueError(f"Registered raw identity conflicts: {relative}")
    outputs = {}
    for filename, (target, key, date_field) in TABLES.items():
        staged = indexed(read_csv(base / filename), key)
        if not staged:
            raise ValueError(f"Missing frozen table: {filename}")
        output = []
        for row in staged.values():
            for column, value in row.items():
                if column.endswith(("source_id", "source_ids")):
                    missing = set(filter(None, value.split(";"))) - registry.keys()
                    if missing:
                        raise ValueError(f"Unresolved staged source: {sorted(missing)}")
            if row.get("raw_file"):
                raw = ROOT / row["raw_file"]
                if (
                    not raw.is_file()
                    or hashlib.sha256(raw.read_bytes()).hexdigest() != row["raw_sha256"]
                ):
                    raise ValueError(f"Broken table/raw binding: {row['raw_file']}")
            frozen_source = frozen_sources[row["source_id"]]
            if registry[row["source_id"]]["tier"] != frozen_source["tier"]:
                raise ValueError(
                    f"Frozen source tier differs from registry: {row['source_id']}"
                )
            output.append(dated_row(row, frozen_source, date_field))
        outputs[target] = output
    # Retain the existing market extraction, but preflight it before any write.
    market = read_csv(ROOT / "scripts/altprotein/market/extracted_rows.csv")
    market.extend(read_csv(ROOT / "scripts/altprotein/pakistan/market_rows.csv"))
    mandatory = {
        "country",
        "year",
        "segment",
        "metric",
        "low",
        "central",
        "high",
        "unit",
        "source_id",
        "tier",
    }
    for row in market:
        if not mandatory <= row.keys() or row["source_id"] not in registry:
            raise ValueError("Market staging does not meet required schema/source join")
    # All validation precedes mutation. Old records are never upserted from older
    # stage files; an identical repeat uses register_raw's preservation branch.
    for source_id, row in new_sources.items():
        if source_id not in old_sources:
            upsert_source(row)
    for relative, row in receipts.items():
        register_raw(
            relative,
            row["url"],
            row["source_id"],
            row["license"],
            row["notes"],
            None if relative in previous else row["accessed_utc"],
        )
    for target, output in outputs.items():
        fields = list(dict.fromkeys(field for row in output for field in row))
        write_csv(
            ROOT / "data/processed" / target,
            fields,
            [{field: row.get(field, "") for field in fields} for row in output],
        )
        print(f"Saved {len(output)} source-bounded records to {target}")
    # Keep the separate market extractor's existing behavior and schema; this
    # supervisor batch does not replace or reinterpret its observations.
    if market:
        fields = list(market[0]) + sorted(
            set().union(*(row.keys() for row in market)) - set(market[0])
        )
        write_csv(
            ROOT / "data/processed/altprotein_market.csv",
            fields,
            [{field: row.get(field, "") for field in fields} for row in market],
        )


if __name__ == "__main__":
    register()
