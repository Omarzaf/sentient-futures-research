"""Restore FBS item codes by matching the supplied extract to the official archive."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SUPPLIED = ROOT / "data/raw/fao_fbs_india_pakistan_2010_2023.csv"
ARCHIVE = ROOT / "data/raw/faostat_fbs_2025-10-28.zip"
MEMBER = "FoodBalanceSheets_E_All_Data_(Normalized).csv"
OUTPUT = ROOT / "data/raw/fao_fbs_restored_codes.csv"
SOURCE_ID = "fao_fbs_2025_10_28"
SELECTED_CODES = {
    "2731": "Bovine Meat",
    "2732": "Mutton & Goat Meat",
    "2733": "Pigmeat",
    "2734": "Poultry Meat",
    "2960": "Fish, Seafood",
    "2949": "Eggs",
    "2948": "Milk - Excluding Butter",
    "2911": "Pulses",
}


def sha256(path: Path) -> str:
    """Hash input or output bytes without loading a large archive into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def label_key(row: dict[str, str]) -> tuple[str, ...]:
    """Return the label-based key used by the supplied extract."""
    return tuple(row[name] for name in ("Area", "Item", "Element Code", "Year", "Unit"))


def value_flag(row: dict[str, str]) -> tuple[Decimal | None, str]:
    """Compare values numerically without rounding while retaining their source flags."""
    return (Decimal(row["Value"]) if row["Value"] else None, row["Flag"])


def main() -> None:
    """Write an official coded subset only after exact supplied-extract reconciliation."""
    supplied_hash = sha256(SUPPLIED)
    archive_hash = sha256(ARCHIVE)
    assert (
        supplied_hash
        == "3f19fc240a97b22993c78982acee4ac78519d91f235936ac71f6099a0f6f6724"
    )
    assert (
        archive_hash
        == "26200855ed5da3d0805e34219124e241d0e0bc6959d0995ebc77a10dd84cbaf1"
    )
    with SUPPLIED.open(newline="", encoding="utf-8") as handle:
        supplied = list(csv.DictReader(handle))
    by_key: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in supplied:
        by_key[label_key(row)].append(row)
    matched: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    restored: list[dict[str, str]] = []
    with ZipFile(ARCHIVE) as archive, archive.open(MEMBER) as stream:
        reader = csv.DictReader(
            io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")
        )
        original_fields = list(reader.fieldnames or [])
        for line_number, row in enumerate(reader, start=2):
            if row["Area Code"] not in {"100", "165"}:
                continue
            key = label_key(row)
            if key not in by_key:
                continue
            row.update(
                {
                    "source_id": SOURCE_ID,
                    "raw_file": str(ARCHIVE.relative_to(ROOT)),
                    "raw_locator": f"{MEMBER};CSV line {line_number}",
                    "method": "Official archive subset matched by supplied label-based keys; per-key Decimal(Value)/Flag multiset verified. Official item codes and original value strings retained. No code assigned from supplied row order.",
                }
            )
            restored.append(row)
            matched[key].append(row)
    mismatches = [
        key
        for key, rows in by_key.items()
        if Counter(map(value_flag, rows)) != Counter(map(value_flag, matched[key]))
    ]
    assert (
        not mismatches
    ), f"Supplied/official key-value-flag mismatch: {mismatches[:5]}"
    assert len(restored) == len(supplied) == 21018
    assert len(matched) == len(by_key) == 20458
    coded_keys = [
        tuple(
            row[name]
            for name in ("Area Code", "Item Code", "Element Code", "Year", "Unit")
        )
        for row in restored
    ]
    assert len(coded_keys) == len(
        set(coded_keys)
    ), "Duplicate coded source observations."
    duplicate_keys = [key for key, rows in matched.items() if len(rows) > 1]
    assert len(duplicate_keys) == 560
    assert all(
        len({row["Item Code"] for row in matched[key]}) == 2 for key in duplicate_keys
    )
    fields = original_fields + ["source_id", "raw_file", "raw_locator", "method"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(restored)
    selected = [row for row in restored if row["Item Code"] in SELECTED_CODES]
    assert {row["Item Code"] for row in selected} == set(SELECTED_CODES)
    assert all(row["Item"] == SELECTED_CODES[row["Item Code"]] for row in selected)
    verification = {
        "source_id": SOURCE_ID,
        "status": "PASS",
        "supplied_rows": len(supplied),
        "restored_rows": len(restored),
        "label_based_keys": len(by_key),
        "duplicate_label_keys": len(duplicate_keys),
        "coded_key_duplicates": len(coded_keys) - len(set(coded_keys)),
        "value_flag_multiset_mismatches": len(mismatches),
        "numerically_different_duplicate_pairs": sum(
            len({value_flag(row)[0] for row in matched[key]}) > 1
            for key in duplicate_keys
        ),
        "selected_item_codes": SELECTED_CODES,
        "selected_rows": len(selected),
        "selected_rows_by_country": dict(Counter(row["Area"] for row in selected)),
        "selected_rows_by_code": dict(Counter(row["Item Code"] for row in selected)),
        "explicitly_excluded_same_label_codes": {
            "2744": "Eggs",
            "2848": "Milk - Excluding Butter",
        },
        "input_sha256": {
            str(SUPPLIED.relative_to(ROOT)): supplied_hash,
            str(ARCHIVE.relative_to(ROOT)): archive_hash,
        },
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": sha256(OUTPUT),
        "output_note": "Derived official archive subset; not a new original download. All original coded records matching supplied keys retained, including same-label companions.",
    }
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
