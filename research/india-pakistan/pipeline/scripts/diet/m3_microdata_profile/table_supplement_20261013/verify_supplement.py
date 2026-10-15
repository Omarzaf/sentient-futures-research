"""Verify the frozen parent profile and isolated public-table supplement."""

import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROFILE = OUT.parent
ROOT = OUT.parents[3]


def sha(path: Path) -> str:
    """Hash a file without retaining or exposing its content."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    """Assert exact source/profile bindings and aggregate-only export structure."""
    previous = json.loads((PROFILE / "integrity_receipt.json").read_text())
    for name, expected in previous["outputs"].items():
        assert sha(PROFILE / name) == expected, f"Frozen profile drift: {name}"
    metadata = json.loads((OUT / "workbook_layout_and_vintage.json").read_text())
    for item in metadata.values():
        assert sha(ROOT / item["path"]) == item["sha256"]
        assert "2024-25" in item["title_cells"]["A2"]
    assert not metadata["15"]["national_categories_merged_ranges"]
    assert not metadata["16"]["national_categories_merged_ranges"]
    boundary = json.loads((OUT / "table22_boundary_evidence.json").read_text())
    assert boundary["formula_cells"] == 0
    assert boundary["next_block"] == {"cell": "A382", "value": "PUNJAB"}
    assert [b["block_first_row"] for b in boundary["blocks"]] == [7, 132, 257]
    checks = json.loads((OUT / "balance_integrity_checks.json").read_text())
    assert checks["unique_household_keys"] == checks["balance_households"] == 30123
    assert checks["key_sets_equal_main_info"] and checks["geography_equal_main_info"]
    assert checks["sum_exp_matches_stored_four_field_sum"] == 30123
    assert checks["sum_exp_matches_annualizing_four_fields"] == 0
    assert checks["supplied_quintile_named_variables"] == []
    assert not checks["health_module_read"]
    for path in OUT.glob("*.csv"):
        with path.open() as stream:
            reader = csv.DictReader(stream)
            assert not {"hhcode", "prcode", "hhno", "idc"} & set(
                reader.fieldnames or []
            )
    verifier_hash = sha(ROOT / "verify_plan.py")
    assert (
        verifier_hash
        == "a0dce0308eb9965e29da0157b6557e285ab54fba351380719ffc13306d39126d"
    )
    sources = {v["path"]: v["sha256"] for v in metadata.values()}
    for relative in (
        "data/raw/diet/m3-survey-inputs-2026-10-13/health-balance.rar",
        "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip",
        "data/raw/diet/m3-method-followup-2026-10-13/worldbank-adept-2014.pdf",
        "data/raw/regional/pbs-hies-catalog.html",
    ):
        sources[relative] = sha(ROOT / relative)
    receipt = {
        "date": "2026-10-13",
        "status": "VERIFIED_SOURCE_INCONSISTENCIES_PRESERVED_NO_GROUPS_ACCEPTED",
        "source_hashes": sources,
        "frozen_parent_receipt_sha256": sha(PROFILE / "integrity_receipt.json"),
        "frozen_parent_artifacts_verified_unchanged": len(previous["outputs"]),
        "verifier_original_sha256": verifier_hash,
        "verifier_executed": False,
        "household_or_person_records_or_identifiers_exported": 0,
        "health_module_read": False,
        "income_or_granular_health_values_exported": 0,
        "new_welfare_groups_or_nutrient_estimates_accepted": 0,
        "shared_registry_processed_state_dashboard_writes": 0,
        "outputs": {
            p.name: sha(p)
            for p in sorted(OUT.iterdir())
            if p.is_file() and p.name != "integrity_receipt.json"
        },
    }
    (OUT / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        f"PASS: {len(previous['outputs'])} frozen artifacts unchanged; source layouts, balance keys/formula and output scope verified."
    )


if __name__ == "__main__":
    main()
