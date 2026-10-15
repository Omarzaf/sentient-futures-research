"""Extract bounded USDA composition candidates with exact row and archive lineage."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/diet/m3-usda-sr-legacy-2026-10-13/sr-legacy.zip"
PREFIX = "FoodData_Central_sr_legacy_food_csv_2018-04/"
SOURCE = "usda_fdc_sr_legacy_2018"
SELECTED = {
    "168898": ("11103", "Rice flour, brown"),
    "169714": ("11103", "Rice flour, white, unenriched"),
    "174288": ("11105", "Chickpea flour (besan)"),
    "173468": ("11901;11902", "Salt, table"),
    "174158": ("12205;110018", "Water, bottled, generic"),
    "173647": ("", "Beverages, water, tap, drinking"),
    "172337": ("11505", "Oil, mustard"),
    "171287": ("11409", "Egg, whole, raw, fresh"),
    "172217": (
        "11401;11403",
        "Milk, whole, 3.25% milkfat, without added vitamin A and vitamin D",
    ),
    "172225": ("11402", "Milk, buttermilk, fluid, whole"),
    "173744": ("11114", "Beans, kidney, red, mature seeds, raw"),
    "173758": (
        "11114",
        "Cowpeas, common (blackeyes, crowder, southern), mature seeds, raw",
    ),
    "175193": ("11114", "Beans, kidney, all types, mature seeds, raw"),
}


def write_csv(name: str, rows: list[dict[str, str]]) -> None:
    """Write source candidates in deterministic order with explicit columns."""
    with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def extract() -> None:
    """Read only selected archive tables without extracting files or estimating intake."""
    archive_hash = hashlib.sha256(RAW.read_bytes()).hexdigest()
    table_hashes = {}
    with zipfile.ZipFile(RAW) as archive:

        def read_table(name: str) -> list[dict[str, str]]:
            """Bind CSV rows to their member hash and physical CSV record number."""
            data = archive.read(PREFIX + name + ".csv")
            table_hashes[name] = hashlib.sha256(data).hexdigest()
            records = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
            return [dict(row, csv_record=str(i)) for i, row in enumerate(records, 2)]

        foods = {row["fdc_id"]: row for row in read_table("food")}
        nutrients = {row["id"]: row for row in read_table("nutrient")}
        derivations = {row["id"]: row for row in read_table("food_nutrient_derivation")}
        values = read_table("food_nutrient")
        portions = read_table("food_portion")
        assert nutrients["1003"]["name"] == "Protein"
        assert nutrients["1003"]["unit_name"] == "G"
        candidates = []
        for fdc_id, (codes, expected) in SELECTED.items():
            food = foods[fdc_id]
            assert food["description"] == expected
            assert food["data_type"] == "sr_legacy_food"
            matches = [
                r
                for r in values
                if r["fdc_id"] == fdc_id and r["nutrient_id"] == "1003"
            ]
            assert len(matches) == 1
            row = matches[0]
            assert 0 <= float(row["amount"]) <= 100
            derivation = derivations.get(row["derivation_id"], {})
            candidates.append(
                {
                    "hies_candidate_codes": codes,
                    "fdc_id": fdc_id,
                    "food_description": expected,
                    "protein_g_per_100g_edible": row["amount"],
                    "nutrient_id": row["nutrient_id"],
                    "food_nutrient_id": row["id"],
                    "data_points": row["data_points"],
                    "derivation_id": row["derivation_id"],
                    "derivation_code": derivation.get("code", ""),
                    "derivation_description": derivation.get("description", ""),
                    "min": row["min"],
                    "max": row["max"],
                    "footnote": row["footnote"],
                    "source_id": SOURCE,
                    "source_tier": "A",
                    "raw_file": str(RAW.relative_to(ROOT)),
                    "raw_sha256": archive_hash,
                    "food_csv_record": food["csv_record"],
                    "nutrient_csv_record": row["csv_record"],
                    "unit_source_id": "usda_sr_legacy_documentation_2018",
                    "unit_locator": "PDF13/printed12 Table6: edible portion; FDC field descriptions PDF5: nutrient amount per100g",
                    "status": "SOURCE_CELL_VERIFIED_MATCH_REVIEW_REQUIRED",
                }
            )
        selected_portions = []
        for row in portions:
            if row["fdc_id"] in {"171287", "172217", "172225"}:
                selected_portions.append(
                    dict(
                        row,
                        source_id=SOURCE,
                        raw_sha256=archive_hash,
                        status="US_SOURCE_PORTION_NOT_PAKISTAN_MEAN_OR_SELECTED_DENSITY",
                    )
                )
    assert len(candidates) == len(SELECTED) == 13
    assert len({r["food_nutrient_id"] for r in candidates}) == len(candidates)
    write_csv("protein_candidates.csv", candidates)
    write_csv("portion_candidates.csv", selected_portions)
    output_hashes = {
        name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        for name in ("protein_candidates.csv", "portion_candidates.csv")
    }
    receipt = {
        "source_id": SOURCE,
        "archive_sha256": archive_hash,
        "archive_member_sha256": table_hashes,
        "protein_candidates": len(candidates),
        "portion_candidates": len(selected_portions),
        "output_sha256": output_hashes,
        "intake_or_imputation_computed": False,
        "missing_derivation_filled": False,
        "matching_status": "proposal_only",
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    extract()
