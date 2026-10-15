"""Build an isolated, source-bound food matching draft without intake arithmetic."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
FCT = ROOT / "data/raw/composition/pakistan-food-composition-2001.pdf"
QUESTION = ROOT / "data/raw/diet/pakistan-hies-2024-25-female-questionnaire.pdf"
INVENTORY = ROOT / "scripts/diet/m3_microdata_profile/item_unit_totals_raw.csv"
SOURCE_ID = "pakistan_food_composition_2001"
METHOD_ID = "worldbank_adept_food_security_2014"
METHOD_LOCATOR = "PDF217-219; printed201-203; food matching and matching index"


def sha(path: Path) -> str:
    """Return the SHA256 of exact artifact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Read a staged table preserving numerical strings."""
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write(name: str, rows: list[dict[str, object]]) -> None:
    """Write only a file owned by this isolated draft."""
    with (BASE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def food_state(row: dict[str, str]) -> str:
    """Preserve explicitly printed states and flag unqualified food names."""
    if row["serial"].startswith("T"):
        return "prepared recipe; traditional-food appendix"
    name = row["food_name"]
    descriptors = re.findall(
        r"raw|cooked|boiled|fried|dried|dry|fresh|ripe|roasted|fluid|liquid|"
        r"skimmed|whole|refined|granular|flour|powder|hydrogenated",
        name,
        re.IGNORECASE,
    )
    return "; ".join(descriptors) or "not explicitly stated in food name"


def main() -> None:
    """Validate source joins and emit candidate rows without assigning intake."""
    factors = read(BASE / "fct_transcription.psv", "|")
    codes = read(BASE / "code_review.psv", "|")
    assert len(factors) == 215
    assert {r["serial"] for r in factors if not r["serial"].startswith("T")} == {
        str(n) for n in range(1, 199)
    }
    assert len(codes) == len({r["itc"] for r in codes}) == 120
    assert not any(None in r for r in factors + codes)
    factor_by_serial = {r["serial"]: r for r in factors}
    source_rows = read(ROOT / "data/processed/sources.csv")
    source_ids = {r["source_id"] for r in source_rows}
    assert {SOURCE_ID, METHOD_ID, "pbs_hies_2024_25_female_questionnaire"} <= source_ids
    aggregate_codes: set[str] = set()
    unit_groups: dict[str, int] = defaultdict(int)
    # The aggregate artifact is opened only to project code keys, never q/v values.
    for row in read(INVENTORY):
        code = str(int(Decimal(row["itc"])))
        aggregate_codes.add(code)
        unit_groups[code] += 1
    expected_food_range = {
        c
        for c in aggregate_codes
        if 11101 <= int(c) <= 11999
        or 12101 <= int(c) <= 12299
        or 110001 <= int(c) <= 110021
    }
    assert {r["itc"] for r in codes} == expected_food_range
    questionnaire_text = (
        ROOT / "data/raw/diet/pakistan-hies-2024-25-female-questionnaire.txt"
    )
    question_lines = questionnaire_text.read_text().splitlines()
    factor_rows = []
    for row in factors:
        assert Decimal(row["protein_g_per_100g_edible"]) >= 0
        page = int(row["pdf_page"])
        if row["serial"].startswith("T"):
            render = BASE / f"evidence/fct-traditional-{page}.png"
            entry = f"traditional dish{row['serial'][1:]}"
        else:
            render = ROOT / f"data/raw/composition/pakistan-fct-{page:02}.png"
            if page == 33:
                render = BASE / "evidence/fct-33.png"
            entry = f"Composition of Food serial{row['serial']}; Protein g column6"
        assert render.exists(), str(render)
        factor_rows.append(
            {
                "factor_id": f"pak_fct_2001_{row['serial']}",
                **row,
                "food_state_as_printed": food_state(row),
                "basis": "g protein per100g edible portion",
                "source_id": SOURCE_ID,
                "source_tier": "A",
                "raw_file": str(FCT.relative_to(ROOT)),
                "raw_sha256": sha(FCT),
                "source_locator": f"PDF{page}; printed{row['printed_page']}; {entry}",
                "visual_evidence_file": str(render.relative_to(ROOT)),
                "visual_evidence_sha256": sha(render),
                "review_status": "visual_cell_transcription; crosswalk approval pending",
            }
        )
    write("factor_catalog.csv", factor_rows)
    output_codes = []
    candidate_rows = []
    for row in codes:
        code = row["itc"]
        page = int(row["questionnaire_page"])
        food_scope = code != "11108"
        candidates = (
            row["candidate_serials"].split(";") if row["candidate_serials"] else []
        )
        assert len(candidates) == len(set(candidates))
        assert set(candidates) <= set(factor_by_serial)
        lines = [
            str(n)
            for n, text in enumerate(question_lines, 1)
            if re.search(rf"\b{code}\b", text)
        ]
        assert lines, code
        output_codes.append(
            {
                **row,
                "food_scope": str(food_scope).lower(),
                "period_days": 14 if page <= 21 else 30,
                "period_label": "14 days" if page <= 21 else "one month",
                "native_unit_source": "questionnaire; raw unit codes not interpreted",
                "mass_unit_grams": {"Kg": "1000", "Gm": "1"}.get(
                    row["native_unit"], ""
                ),
                "edible_fraction": "",
                "density_g_per_ml": "",
                "edible_grams_per_count": "",
                "selected_protein_factor": "",
                "approved_for_calibration": "false",
                "quantity_value_channels": "q1/v1 paid;q2/v2 wages in kind;q3/v3 own produce;q4/v4 gifts",
                "aggregate_code_present": "true",
                "aggregate_unit_groups": unit_groups[code],
                "questionnaire_source_id": "pbs_hies_2024_25_female_questionnaire",
                "questionnaire_raw_file": str(QUESTION.relative_to(ROOT)),
                "questionnaire_raw_sha256": sha(QUESTION),
                "questionnaire_locator": f"PDF/printed{page}; section6F; code{code}; text lines{','.join(lines)}",
                "matching_method_source_id": METHOD_ID,
                "matching_method_locator": METHOD_LOCATOR,
                "matching_grade_is_not_source_tier": "true",
                "status": "DRAFT_REVIEW_ONLY" if food_scope else "SERVICE_EXCLUDED",
            }
        )
        for serial in candidates:
            factor = factor_by_serial[serial]
            candidate_rows.append(
                {
                    "itc": code,
                    "factor_id": f"pak_fct_2001_{serial}",
                    "food_name": factor["food_name"],
                    "protein_g_per_100g_edible": factor["protein_g_per_100g_edible"],
                    "food_state_as_printed": food_state(factor),
                    "candidate_set_status": row["candidate_set_status"],
                    "proposed_match_grade": row["proposed_match_grade"],
                    "candidate_role": "screened_candidate_or_explicit_proxy; consult code review_note",
                    "assigned_mixture_weight": "",
                    "source_id": SOURCE_ID,
                    "source_locator": f"PDF{factor['pdf_page']}; printed{factor['printed_page']}; serial{serial}",
                    "selection_status": "NOT_APPROVED",
                }
            )
    write("questionnaire_inventory.csv", output_codes)
    write("candidate_matches.csv", candidate_rows)
    density_rows = read(BASE / "density_candidates.psv", "|")
    density_pdf = ROOT / "data/raw/diet/m3-infoods-2026-10-13/density-v2.pdf"
    assert len(density_rows) == 17
    for row in density_rows:
        assert bool(row["density_g_per_ml"]) != bool(row["specific_gravity"])
        row.update(
            source_id="fao_infoods_density_v2_2012",
            source_locator="PDF13; printed10; Milk table; row by food description and BiblioID",
            raw_file=str(density_pdf.relative_to(ROOT)),
            raw_sha256=sha(density_pdf),
            status="CANDIDATE_NOT_SELECTED",
        )
    write("density_candidates.csv", density_rows)
    write("method_rules.csv", read(BASE / "method_rules.psv", "|"))
    existing = read(ROOT / "scripts/diet/pakistan_conversion_factors.csv")
    differences = []
    for old in existing:
        new = factor_by_serial[old["food_number"]]
        if Decimal(old["protein_g_per_100g_edible"]) != Decimal(
            new["protein_g_per_100g_edible"]
        ):
            differences.append(
                {
                    "factor_id": old["factor_id"],
                    "existing_protein": old["protein_g_per_100g_edible"],
                    "visually_checked_protein": new["protein_g_per_100g_edible"],
                    "source_locator": f"PDF{new['pdf_page']}; printed{new['printed_page']}; Protein column6",
                    "finding": "Prior25.1 is lipid column7; protein column6 is25.2",
                    "action": "Corrected isolated catalog only; central factor unchanged by this task",
                }
            )
    assert len(differences) == 1 and differences[0]["factor_id"] == "pak_fct_2001_138"
    write("factor_discrepancies.csv", differences)
    source_files = [
        FCT,
        QUESTION,
        questionnaire_text,
        INVENTORY,
        ROOT / "scripts/diet/pakistan_conversion_factors.csv",
        ROOT / "data/raw/diet/pakistan-hies-2024-25-manual.pdf",
        ROOT / "data/raw/diet/pakistan-hies-2024-25-manual.txt",
        ROOT / "data/raw/diet/m3-method-followup-2026-10-13/worldbank-adept-2014.pdf",
    ]
    for name in [
        "density-v2.pdf",
        "food-matching-v1-2.pdf",
        "hces-technical-notes.pdf",
    ]:
        source_files.append(ROOT / f"data/raw/diet/m3-infoods-2026-10-13/{name}")
    for row in factor_rows:
        source_files.append(ROOT / str(row["visual_evidence_file"]))
    write(
        "source_artifact_bindings.csv",
        [
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha(p),
                "bytes": p.stat().st_size,
            }
            for p in sorted(set(source_files))
        ],
    )
    receipt = {
        "date": "2026-10-13",
        "status": "PASS_STRUCTURAL_INTEGRITY; semantic mapping remains draft",
        "questionnaire_codes": len(codes),
        "food_codes": sum(r["food_scope"] == "true" for r in output_codes),
        "service_codes": ["11108"],
        "prepared_food_codes": sum(int(r["itc"]) >= 110001 for r in codes),
        "main_fct_cells": 198,
        "traditional_dish_cells": 17,
        "candidate_matches": len(candidate_rows),
        "density_candidates": len(density_rows),
        "density_values_selected": 0,
        "food_native_units": dict(
            Counter(r["native_unit"] for r in output_codes if r["food_scope"] == "true")
        ),
        "food_matching_set_status": dict(
            Counter(
                r["candidate_set_status"]
                for r in output_codes
                if r["food_scope"] == "true"
            )
        ),
        "old_factor_cells_compared": len(existing),
        "old_factor_discrepancies": len(differences),
        "missing_aggregate_food_codes": [],
        "approved_calibration_rows": 0,
        "intake_values_calculated": 0,
        "household_records_read": 0,
        "unit_costs_calculated": 0,
        "weights_assigned_to_food_candidates": 0,
        "source_hashes": {
            str(p.relative_to(ROOT)): sha(p) for p in sorted(set(source_files))
        },
        "output_hashes": {p.name: sha(p) for p in sorted(BASE.glob("*.csv"))},
        "input_hashes": {p.name: sha(p) for p in sorted(BASE.glob("*.psv"))},
    }
    (BASE / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {k: v for k, v in receipt.items() if not k.endswith("hashes")}, indent=2
        )
    )


if __name__ == "__main__":
    main()
