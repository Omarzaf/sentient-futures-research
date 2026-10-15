"""Integrate M2 tables while preserving non-comparable survey definitions and sample bases."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from decimal import Decimal

from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = ["build", "region_key"]

# Explicit reviewed batches only: candidate files are never imported by glob.
BATCHES = [
    ("scripts/regional", "extracted_rows.csv", "source_rows.csv", "manifest_rows.csv"),
    (
        "scripts/regional/india-supplement-2026-10-13",
        "hces_extracted_rows.csv",
        "source_rows.csv",
        "hces_manifest_rows.csv",
    ),
    (
        "scripts/regional/pakistan_supplement_20261013",
        "extracted_rows.csv",
        "source_rows.csv",
        "manifest_rows.csv",
    ),
    (
        "scripts/regional/india-supplement-2026-10-13",
        "bahs_regional_rows.csv",
        "bahs_source_rows.csv",
        "bahs_manifest_rows.csv",
    ),
]
PROVENANCE_ONLY = [
    (
        "scripts/regional/india-supplement-2026-10-13",
        "failed_acquisition_source_rows.csv",
        "failed_acquisition_manifest_rows.csv",
    )
]


def region_key(name: str) -> str:
    """Normalize spelling accents and ampersands without fuzzy geographic matching."""
    ascii_name = "".join(
        character
        for character in unicodedata.normalize("NFKD", name)
        if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", ascii_name.lower().replace("&", " and ")).strip()


def build() -> None:
    """Merge reviewed survey records and require an exact normalized boundary join."""
    for folder, *files in BATCHES + PROVENANCE_ONLY:
        for filename in files:
            if not (ROOT / folder / filename).is_file():
                raise ValueError(
                    f"Required reviewed batch artifact missing: {folder}/{filename}"
                )
    provenance_batches = [
        (folder, source, manifest) for folder, _, source, manifest in BATCHES
    ] + PROVENANCE_ONLY
    source_rows = [
        row
        for folder, source, _ in provenance_batches
        for row in read_csv(ROOT / folder / source)
    ]
    if not source_rows:
        raise ValueError("Regional source registry not ready")
    for row in source_rows:
        upsert_source(row)
    for row in [
        row
        for folder, _, manifest in provenance_batches
        for row in read_csv(ROOT / folder / manifest)
    ]:
        with (ROOT / row["file"]).open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"Raw regional file changed after handoff: {row['file']}")
        notes = row.get("notes", "") or (
            row.get("kind", "") + "; derived_from=" + row.get("derived_from", "")
        )
        register_raw(
            row["file"],
            row["url"],
            row["source_id"],
            row["license"],
            notes,
            row["accessed_utc"],
        )
    sources = {
        row["source_id"] for row in read_csv(ROOT / "data/processed/sources.csv")
    }
    rows = [
        row
        for folder, extracted, _, _ in BATCHES
        for row in read_csv(ROOT / folder / extracted)
    ]
    if not rows:
        raise ValueError("No regional rows")
    seen = set()
    for row in rows:
        for field in ("source_id", "sample_source_id"):
            if row[field] not in sources:
                raise ValueError(f"Unregistered source {row[field]}")
        value = Decimal(row["value"])
        if (
            not value.is_finite()
            or value < 0
            or (row["unit"].startswith("percent") and value > 100)
        ):
            raise ValueError("Invalid survey observation")
        key = tuple(
            row[field]
            for field in (
                "country",
                "region",
                "region_type",
                "year",
                "indicator",
                "sex",
                "residence",
                "quintile",
                "source_id",
            )
        )
        if key in seen:
            raise ValueError("Duplicate regional observation")
        seen.add(key)
        if not all(
            row[field] for field in ("denominator", "method", "raw_locator", "period")
        ):
            raise ValueError("Missing survey interpretation metadata")
        status = row.get("boundary_match_status", "")
        if status.startswith("unmapped_") and not row.get("boundary_match_note"):
            raise ValueError("Unmapped geography needs an explicit source-scope reason")
    crosswalk = []
    for country, iso in (("India", "IND"), ("Pakistan", "PAK")):
        geometry = json.loads(
            (ROOT / f"dashboard/geo/geoBoundaries-{iso}-ADM1.geojson").read_text()
        )
        by_name = {
            region_key(feature["properties"]["shapeName"]): feature["properties"]
            for feature in geometry["features"]
        }
        if len(by_name) != len(geometry["features"]):
            raise ValueError("Boundary names collide after normalization")
        regions = sorted(
            {
                row["region"]
                for row in rows
                if row["country"] == country
                and row["region_type"] != "national"
                and not row.get("boundary_match_status", "").startswith("unmapped_")
            }
        )
        for region in regions:
            properties = by_name.get(region_key(region))
            if properties is None:
                raise ValueError(
                    f"No exact normalized boundary for {country}: {region}"
                )
            crosswalk.append(
                {
                    "country": country,
                    "region": region,
                    "shapeName": properties["shapeName"],
                    "shapeID": properties["shapeID"],
                    "source_id": f"geoboundaries_{iso.lower()}_adm1_9469f09",
                    "method": "Exact match after Unicode accent normalization, ampersand expansion and whitespace normalization; no fuzzy matching.",
                    "notes": "Survey period differs from geometry metadata; boundary depiction does not assert sovereignty.",
                }
            )
    lookup = {(row["country"], row["region"]): row for row in crosswalk}
    for row in rows:
        boundary = lookup.get((row["country"], row["region"]))
        if row.get("boundary_match_status", "").startswith("unmapped_"):
            boundary = None
        row["boundary_shape_id"] = boundary["shapeID"] if boundary else ""
        row["boundary_source_id"] = boundary["source_id"] if boundary else ""
        if not row.get("boundary_match_status"):
            row["boundary_match_status"] = (
                "mapped_exact" if boundary else "national_no_adm1"
            )
    rows.sort(
        key=lambda row: tuple(
            row[field]
            for field in (
                "country",
                "region",
                "source_id",
                "year",
                "indicator",
                "residence",
                "quintile",
            )
        )
    )
    fields = list(dict.fromkeys(field for row in rows for field in row))
    write_csv(ROOT / "data/processed/meat_regional.csv", fields, rows)
    write_csv(
        ROOT / "data/processed/region_boundary_crosswalk.csv",
        list(crosswalk[0]),
        crosswalk,
    )
    audit = {
        "rows_by_source": dict(Counter(row["source_id"] for row in rows)),
        "subnational_regions": {
            country: sorted(
                {row["region"] for row in crosswalk if row["country"] == country}
            )
            for country in ("India", "Pakistan")
        },
        "matched_boundaries": len(crosswalk),
        "unmatched_subnational_regions": [
            {
                "country": country,
                "region": region,
                "source_id": source,
                "reason": reason,
            }
            for country, region, source, reason in sorted(
                {
                    (
                        row["country"],
                        row["region"],
                        row["source_id"],
                        row.get("boundary_match_note", ""),
                    )
                    for row in rows
                    if row["region_type"] != "national" and not row["boundary_shape_id"]
                }
            )
        ],
        "intentionally_unmapped_rows": sum(
            row["boundary_match_status"].startswith("unmapped_") for row in rows
        ),
        "national_rows_without_adm1_shape": sum(
            row["region_type"] == "national" for row in rows
        ),
        "missing_sample_size_rows": sum(not row["sample_size"] for row in rows),
        "sample_basis_row_counts": dict(Counter(row["sample_basis"] for row in rows)),
        "missing_fieldwork_end_rows": sum(not row["fieldwork_end"] for row in rows),
    }
    (ROOT / "logs/m2-data-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(
        json.dumps(
            {
                "rows": len(rows),
                "boundary_matches": len(crosswalk),
                "sources": audit["rows_by_source"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    build()
