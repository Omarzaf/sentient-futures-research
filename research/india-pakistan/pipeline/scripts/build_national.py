"""Build M1 from preserved FAOSTAT files and reviewed supplemental source extracts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = ["build"]
COUNTRIES = {"India", "Pakistan"}
USDA_BATCH = "scripts/national/usda-poultry-2026-10-13"
FIELDS = [
    "country",
    "year",
    "item",
    "metric",
    "value",
    "unit",
    "source_id",
    "flag",
    "method",
    "period",
    "raw_file",
    "raw_locator",
    "notes",
    "item_code",
    "source_vintage",
    "sample_size",
    "sample_basis",
]
ITEM_CODES = {
    "2731": "Bovine Meat",
    "2732": "Mutton & Goat Meat",
    "2734": "Poultry Meat",
    "2733": "Pigmeat",
    "2960": "Fish, Seafood",
    "2949": "Eggs",
    "2948": "Milk - Excluding Butter",
    "2911": "Pulses",
}
METRICS = {
    "645": ("food_supply_quantity", "kg/capita/year"),
    "674": ("protein_supply_quantity", "g/capita/day"),
    "5511": ("production_fbs", "1000 t"),
    "5611": ("imports_fbs", "1000 t"),
    "5911": ("exports_fbs", "1000 t"),
    "5142": ("food_available_fbs", "1000 t"),
}


def bulk_rows(path: Path) -> Iterator[dict[str, str]]:
    """Stream the normalized CSV member without extracting the large global table."""
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if "Normalized" in name)
        with archive.open(name) as binary:
            yield from csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig"))


def fbs_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    """Identify one source observation, including its original measurement unit."""
    return tuple(row[key] for key in ("Area", "Item", "Element Code", "Year", "Unit"))


def reconcile_fbs(
    rows: list[dict[str, str]], restored: list[dict[str, str]]
) -> dict[str, object]:
    """Compare supplied observation multisets with code-bearing official source rows."""
    supplied_counts = Counter(
        (fbs_key(row), Decimal(row["Value"]), row["Flag"]) for row in rows
    )
    official_counts = Counter(
        (fbs_key(row), Decimal(row["Value"]), row["Flag"]) for row in restored
    )
    if supplied_counts != official_counts:
        raise ValueError(
            "Restored official FBS observation multiset differs from supplied extract"
        )
    coded_keys = [
        (r["Area Code"], r["Item Code"], r["Element Code"], r["Year"], r["Unit"])
        for r in restored
    ]
    if len(coded_keys) != len(set(coded_keys)):
        raise ValueError("Duplicate coded observations in restored FBS")
    return {
        "source_id": "fao_fbs_2025_10_28",
        "supplied_rows": len(rows),
        "matched_rows": len(restored),
        "matched_label_keys": len({fbs_key(row) for row in rows}),
        "mismatches": 0,
        "code_selection": ITEM_CODES,
        "restoration_method": "scripts/fbs/restore_item_codes.py; see notes/M1-FBS-DUPLICATES.md",
    }


def fbs_observations(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Keep source measurements and derive apparent consumption only from complete triples."""
    output = []
    components = defaultdict(dict)
    seen = set()
    for row in rows:
        if row["Item Code"] not in ITEM_CODES or row["Element Code"] not in METRICS:
            continue
        if ITEM_CODES[row["Item Code"]] != row["Item"]:
            raise ValueError("FBS source item label changed for selected code")
        key = (
            row["Area"],
            row["Item Code"],
            row["Element Code"],
            row["Year"],
            row["Unit"],
        )
        if key in seen:
            raise ValueError("Duplicate coded FBS observation")
        seen.add(key)
        metric, unit = METRICS[row["Element Code"]]
        output.append(
            {
                "country": row["Area"],
                "year": row["Year"],
                "item": row["Item"],
                "metric": metric,
                "value": row["Value"],
                "unit": unit,
                "source_id": "fao_fbs_2025_10_28",
                "flag": row["Flag"],
                "method": "Official code-bearing row matched to supplied extract; source value preserved. Explicit display-code selection: 2949 Eggs and 2948 Milk; companion same-label codes 2744 and 2848 excluded to avoid overlap.",
                "period": row["Year"],
                "raw_file": "data/raw/faostat_fbs_2025-10-28.zip",
                "raw_locator": f"FoodBalanceSheets_E_All_Data_(Normalized).csv; Area Code={row['Area Code']}; Item Code={row['Item Code']}; Element Code={row['Element Code']}; Year={row['Year']}",
                "notes": "Food balance availability, not measured individual intake or retail sales. The original supplied file and all alternative coded records are preserved.",
                "item_code": row["Item Code"],
            }
        )
        if row["Element Code"] in {"5511", "5611", "5911"}:
            components[(row["Area"], row["Item"], row["Year"], row["Unit"])][
                row["Element Code"]
            ] = row
    omitted = []
    for (country, item, year, unit), group in sorted(components.items()):
        required = {"5511", "5611", "5911"}
        if set(group) != required or any(not row["Value"] for row in group.values()):
            omitted.append(
                {
                    "country": country,
                    "item": item,
                    "year": year,
                    "missing_elements": ",".join(
                        sorted(
                            (required - set(group))
                            | {code for code, row in group.items() if not row["Value"]}
                        )
                    ),
                    "source_id": "fao_fbs_2025_10_28",
                }
            )
            continue
        value = (
            Decimal(group["5511"]["Value"])
            + Decimal(group["5611"]["Value"])
            - Decimal(group["5911"]["Value"])
        )
        output.append(
            {
                "country": country,
                "year": year,
                "item": item,
                "metric": "apparent_consumption_production_plus_imports_minus_exports",
                "value": str(value),
                "unit": unit,
                "source_id": "fao_fbs_2025_10_28",
                "flag": "derived;"
                + ";".join(
                    f"{code}={group[code]['Flag']}" for code in sorted(required)
                ),
                "method": "Production (5511) + import quantity (5611) - export quantity (5911); no imputation; same year, country, item and unit.",
                "period": year,
                "raw_file": "data/raw/faostat_fbs_2025-10-28.zip",
                "raw_locator": f"Area={country}; Item Code={group['5511']['Item Code']}; Year={year}; Element Codes=5511,5611,5911",
                "notes": "Volume proxy only; excludes stock changes, non-food uses and losses. Not retail sales value or the FBS Food element.",
                "item_code": group["5511"]["Item Code"],
            }
        )
    return output, omitted


def qcl_observations() -> list[dict[str, str]]:
    """Extract animal-specific and explicitly labelled aggregate meat production."""
    output = []
    for row in bulk_rows(ROOT / "data/raw/faostat_qcl_2025-12-31.zip"):
        if row["Area"] not in COUNTRIES or int(row["Year"]) < 2010:
            continue
        if row["Element"] != "Production" or "meat" not in row["Item"].lower():
            continue
        output.append(
            {
                "country": row["Area"],
                "year": row["Year"],
                "item": row["Item"],
                "metric": "production_qcl",
                "value": row["Value"],
                "unit": row["Unit"],
                "source_id": "fao_qcl_2025_12_31",
                "item_code": row["Item Code"],
                "flag": row["Flag"],
                "method": "Direct extraction from QCL normalized bulk table; no conversion or imputation.",
                "period": row["Year"],
                "raw_file": "data/raw/faostat_qcl_2025-12-31.zip",
                "raw_locator": f"Area Code={row['Area Code']}; Item Code={row['Item Code']}; Element Code={row['Element Code']}; Year={row['Year']}",
                "notes": "Keep QCL separate from FBS production. "
                + row.get("Note", "")
                + (
                    " Aggregate overlaps animal-specific series; do not sum both."
                    if row["Item Code"] in {"1806", "1807", "1808", "1765"}
                    else ""
                ),
            }
        )
    return output


def register_usda_batch() -> None:
    """Register the reviewed USDA archive and report receipts after byte verification."""
    folder = ROOT / USDA_BATCH
    manifests = read_csv(folder / "manifest_rows.csv")
    sources = read_csv(folder / "source_rows.csv")
    if not manifests or not sources:
        raise ValueError("Reviewed USDA provenance batch is missing")
    for row in manifests:
        path = (ROOT / row["file"]).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("USDA receipt path outside project")
        with path.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"USDA receipt changed after handoff: {row['file']}")
    for row in sources:
        upsert_source(row)
    for row in manifests:
        register_raw(
            row["file"],
            row["url"],
            row["source_id"],
            row["license"],
            row.get("notes", ""),
            row["accessed_utc"],
        )


def build(supplement_paths: list[str]) -> None:
    """Build the combined national table and machine-readable provenance audit."""
    register_usda_batch()
    fbs = read_csv(ROOT / "data/raw/fao_fbs_india_pakistan_2010_2023.csv")
    restored = read_csv(ROOT / "data/raw/fao_fbs_restored_codes.csv")
    reconciliation = reconcile_fbs(fbs, restored)
    rows, omissions = fbs_observations(restored)
    rows.extend(qcl_observations())
    for name in supplement_paths:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Supplement path outside project")
        for row in read_csv(path):
            missing = set(FIELDS[:8]) - set(row)
            if missing:
                raise ValueError(f"Supplement lacks fields: {missing}")
            rows.append({field: row.get(field, "") for field in FIELDS})
    source_ids = {
        row["source_id"] for row in read_csv(ROOT / "data/processed/sources.csv")
    }
    unresolved = {row["source_id"] for row in rows} - source_ids
    if unresolved:
        raise ValueError(f"Unregistered sources: {unresolved}")
    keys = [
        (
            r["country"],
            r["year"],
            r["period"],
            r["item"],
            r["metric"],
            r["unit"],
            r["source_id"],
        )
        for r in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate national-series observations")
    for row in rows:
        if row["country"] not in COUNTRIES:
            raise ValueError("Unexpected country")
        if row["value"] and not Decimal(row["value"]).is_finite():
            raise ValueError("Non-finite observation")
    rows.sort(
        key=lambda r: (
            r["country"],
            r["source_id"],
            r["item"],
            r["metric"],
            r["year"],
            r["period"],
        )
    )
    write_csv(ROOT / "data/processed/meat_supply_national.csv", FIELDS, rows)
    audit = {
        "fbs_reconciliation": reconciliation,
        "row_counts_by_source": dict(Counter(r["source_id"] for r in rows)),
        "country_year_coverage_by_source": {
            source: {
                country: sorted(
                    {
                        int(r["year"])
                        for r in rows
                        if r["country"] == country and r["source_id"] == source
                    }
                )
                for country in sorted(COUNTRIES)
            }
            for source in sorted({r["source_id"] for r in rows})
        },
        "missing_apparent_consumption_components": omissions,
        "blank_values": [
            {
                k: r[k]
                for k in ("country", "year", "item", "metric", "source_id", "flag")
            }
            for r in rows
            if not r["value"]
        ],
        "supplement_files": supplement_paths,
    }
    (ROOT / "logs/m1-data-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(
        json.dumps(
            {
                "rows": len(rows),
                "sources": audit["row_counts_by_source"],
                "fbs_rows_reconciled": reconciliation["matched_rows"],
                "apparent_consumption_omissions": len(omissions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    build(
        sys.argv[1:]
        or [
            "data/raw/oecd/meat_rows_staging.csv",
            "scripts/national/extracted_rows.csv",
            "scripts/regional/india-supplement-2026-10-13/bahs_national_rows.csv",
            f"{USDA_BATCH}/gain_national_rows.csv",
        ]
    )
