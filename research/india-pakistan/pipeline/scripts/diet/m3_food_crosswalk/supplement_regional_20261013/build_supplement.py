"""Bind reviewed regional FCT cells and proposals without estimating intake."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CORE = HERE.parent
SOURCES = {
    "bd": {
        "source_id": "bangladesh_fct_2013",
        "source_tier": "B",
        "country": "Bangladesh",
        "raw_file": "data/raw/diet/m3-infoods-2026-10-13/bangladesh-fct-2013.pdf",
        "raw_sha256": "9728be753c4675e0673d02624297d81d1da41fea8a78fa36dee586aa9224cb93",
        "n_basis": "number of compositional data points; not persons or households",
        "method_locator": "PDF12/printedxi basis and EDIBLE; PDF23/printedxxii n/SD; PDF15/printedxiv protein",
    },
    "in": {
        "source_id": "india_ifct_2017",
        "source_tier": "A",
        "country": "India",
        "raw_file": "data/raw/diet/m3-infoods-2026-10-13/india-ifct-2017.pdf",
        "raw_sha256": "7fc5a5112a57240d25bf695dca82cccd8d93ed54e8c39530e42b5ad1820d0e8c",
        "n_basis": "number of sampled regions; not persons or households",
        "method_locator": "PDF26/printedxix regional means; PDF27/printedxx raw-state and protein methods",
    },
}


def digest(path: Path) -> str:
    """Return a source artifact's SHA256."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Read a small source-controlled table without type coercion."""
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter=delimiter))
    assert all(None not in row and None not in row.values() for row in rows), path
    return rows


def write_csv(name: str, rows: list[dict[str, str]]) -> None:
    """Write a deterministic derived table."""
    with (HERE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Validate local source cells and freeze a review-only supplement."""
    inventory = {
        row["itc"]: row
        for row in read_rows(CORE / "questionnaire_inventory.csv")
        if row["food_scope"] == "true"
    }
    source_register = {
        row["source_id"]: row for row in read_rows(ROOT / "data/processed/sources.csv")
    }
    frozen = json.loads((CORE / "handoff_hashes.json").read_text())
    for relative, binding in frozen["files"].items():
        assert digest(ROOT / relative) == binding["sha256"], relative
    for source in SOURCES.values():
        assert digest(ROOT / source["raw_file"]) == source["raw_sha256"]
        assert source_register[source["source_id"]]["tier"] == source["source_tier"]

    transcribed = read_rows(HERE / "source_cells.psv", "|")
    cells, matches, keys = [], [], set()
    for row in transcribed:
        key = (row["source_key"], row["food_code"])
        assert key not in keys, key
        keys.add(key)
        source = SOURCES[row["source_key"]]
        protein, edible = row["protein_g_per_100g_edible"], row["edible_coefficient"]
        if protein:
            assert 0 <= float(protein) <= 100
            assert 0 < int(row["protein_n_or_regions"])
            assert 0 <= float(row["water_g_per_100g_edible"]) <= 100
        else:
            assert row["role"] == "edible_coefficient_only"
            assert not any(
                row[x]
                for x in [
                    "protein_n_or_regions",
                    "protein_dispersion_type",
                    "protein_dispersion",
                    "water_g_per_100g_edible",
                ]
            )
        if edible:
            assert 0 < float(edible) <= 1
        if row["source_key"] == "in":
            assert not edible, "IFCT selected table has no edible coefficient column"
        page = HERE / "evidence" / f"{row['source_key']}-{row['pdf_page']}.png"
        assert page.is_file()
        text_path = (
            HERE / "evidence" / Path(source["raw_file"]).with_suffix(".txt").name
        )
        source_page = text_path.read_text().split("\f")[int(row["pdf_page"]) - 1]
        assert row["food_code"] in source_page, (key, row["pdf_page"])
        cell = {
            **row,
            **source,
            "source_url": source_register[source["source_id"]]["url"],
            "rights_status": source_register[source["source_id"]]["license"],
            "protein_basis": "g per 100g edible food; blank means not transcribed for this row",
            "edible_coefficient_basis": "edible mass / total food as purchased; ratio; source BD Table1",
            "evidence_image": str(page.relative_to(ROOT)),
            "evidence_image_sha256": digest(page),
            "selected_for_calibration": "false",
            "status": "SOURCE_TRANSCRIPTION_REVIEW_ONLY",
        }
        cells.append(cell)
        for code in row["hies_codes"].split(";"):
            assert code in inventory, code
            matches.append(
                {
                    "itc": code,
                    "questionnaire_label": inventory[code]["questionnaire_label"],
                    "native_unit": inventory[code]["native_unit"],
                    "source_id": source["source_id"],
                    "food_code": row["food_code"],
                    "role": row["role"],
                    "form_note": row["form_note"],
                    "selected_for_calibration": "false",
                }
            )
    assert len(matches) == len(
        {(r["itc"], r["source_id"], r["food_code"]) for r in matches}
    )
    write_csv("regional_source_cells.csv", cells)
    write_csv("regional_candidate_matches.csv", matches)

    searches = []
    for source_key, name in [("bd", "bangladesh-fct-2013"), ("in", "india-ifct-2017")]:
        path = HERE / "evidence" / f"{name}.txt"
        content = path.read_text()
        for item, pattern in [
            ("rice flour", r"rice[^\n]{0,30}flour|flour[^\n]{0,30}rice"),
            (
                "Besan/chickpea flour",
                r"besan|(?:gram|chick\w*)[^\n]{0,30}flour|flour[^\n]{0,30}(?:gram|chick\w*)",
            ),
        ]:
            hits = list(re.finditer(pattern, content, re.IGNORECASE))
            searches.append(
                {
                    "source_id": SOURCES[source_key]["source_id"],
                    "target": item,
                    "regex": pattern,
                    "hits": str(len(hits)),
                    "matched_text": "; ".join(hit.group() for hit in hits),
                    "text_file": str(path.relative_to(ROOT)),
                    "text_sha256": digest(path),
                    "disposition": "No exact food entry located by these searches and inspected cereal/pulse pages. India rice-and-flour hit is only a nitrogen-to-protein conversion-factor row in Table3, PDF28/printedxxi. This is not proof of absence from all possible references. Dal-to-Besan or polished-rice-to-rice-flour remain explicit milling proxies.",
                }
            )
    assert [row["hits"] for row in searches] == ["0", "0", "1", "0"]
    write_csv("search_dispositions.csv", searches)

    proposals = read_rows(HERE / "calibration_proposals.psv", "|")
    usda_dir = ROOT / "scripts/diet/m3_usda_supplement"
    usda_receipt = json.loads((usda_dir / "receipt.json").read_text())
    for name, expected in usda_receipt["output_sha256"].items():
        assert digest(usda_dir / name) == expected, name
    reference_keys = {
        "pk": {row["serial"] for row in read_rows(CORE / "factor_catalog.csv")},
        "bd": {r["food_code"] for r in cells if r["source_key"] == "bd"},
        "in": {r["food_code"] for r in cells if r["source_key"] == "in"},
        "usda": {r["fdc_id"] for r in read_rows(usda_dir / "protein_candidates.csv")},
    }
    assert len(proposals) == len({row["itc"] for row in proposals})
    for row in proposals:
        assert row["itc"] in inventory
        assert row["status"] in {
            "PROPOSE_CALIBRATION",
            "PROPOSE_SENSITIVITY_ONLY",
            "PROPOSE_MONETARY_ROUTE",
            "HOLD_SURVEY_RECONCILIATION",
            "PROPOSE_ZERO_CONTRIBUTION",
        }
        for alias, entry in re.findall(
            r"\b(pk|bd|in|usda):([A-Z0-9_]+)", " ".join(row.values())
        ):
            assert entry in reference_keys[alias], (alias, entry)
    write_csv("calibration_proposals.csv", proposals)
    quantity_gaps = []
    for code, row in inventory.items():
        if row["native_unit"] not in {"No", "unspecified"}:
            continue
        if code == "110018":
            route = "DIRECT_ZERO_PREPARED_WATER; outside at-home G and unresolved K"
        elif row["native_unit"] == "unspecified":
            route = (
                "MONETARY_ROUTE_WITH_CURRENT_INSTRUMENT; no standard physical quantity"
            )
        elif code == "11409":
            route = "FOREIGN_SOURCE_EGG_SIZE_SENSITIVITY_OR_MONETARY_ROUTE"
        else:
            route = "PORTION_INPUT_NOT_REVIEWED; monetary route unless sourced count default accepted"
        quantity_gaps.append(
            {
                "itc": code,
                "questionnaire_label": row["questionnaire_label"],
                "native_unit": row["native_unit"],
                "questionnaire_locator": row["questionnaire_locator"],
                "proposed_route": route,
            }
        )
    write_csv("quantity_route_inventory.csv", quantity_gaps)
    receipt = {
        "date": "2026-10-13",
        "status": "FROZEN_REVIEW_HANDOFF",
        "source_cell_rows": len(cells),
        "protein_cell_rows": sum(bool(r["protein_g_per_100g_edible"]) for r in cells),
        "edible_coefficient_rows": sum(bool(r["edible_coefficient"]) for r in cells),
        "candidate_links": len(matches),
        "distinct_food_codes": len({r["itc"] for r in matches}),
        "calibration_proposals": len(proposals),
        "proposal_status_counts": dict(
            sorted(Counter(r["status"] for r in proposals).items())
        ),
        "quantity_route_inventory": len(quantity_gaps),
        "frozen_core_files_unchanged": len(frozen["files"]),
        "selected_cells": 0,
        "intake_or_unit_cost_estimates_computed": False,
        "source_hashes": {v["source_id"]: v["raw_sha256"] for v in SOURCES.values()},
        "coordinator_usda_candidate_bindings": {
            name: digest(usda_dir / name)
            for name in [
                "protein_candidates.csv",
                "portion_candidates.csv",
                "receipt.json",
            ]
        },
        "outputs": {
            name: digest(HERE / name)
            for name in [
                "regional_source_cells.csv",
                "regional_candidate_matches.csv",
                "search_dispositions.csv",
                "calibration_proposals.csv",
                "quantity_route_inventory.csv",
            ]
        },
    }
    (HERE / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
