"""Check aggregate outputs and preserve all earlier evidence snapshots."""

import csv
import hashlib
import json
import math
import re
from itertools import pairwise
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROFILE = OUT.parent
ROOT = OUT.parents[3]
SCENARIOS = {"nominal", "scope_excluded", "cpi_temporal"}


def sha(path: Path) -> str:
    """Hash bytes without printing their contents."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_csv(name: str) -> list[dict[str, str]]:
    """Read one exported aggregate CSV."""
    with (OUT / name).open() as stream:
        return list(csv.DictReader(stream))


def total(rows: list[dict[str, str]], field: str) -> float:
    """Sum an unsuppressed aggregate field."""
    assert all(row[field] != "" for row in rows)
    return math.fsum(float(row[field]) for row in rows)


def close(left: float, right: float) -> bool:
    """Compare serialization-level aggregate rounding only."""
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-8)


def main() -> None:
    """Validate coverage, grouping, sensitivity, source hashes and export scope."""
    snapshots = {}
    sources = {}
    for folder in (PROFILE, PROFILE / "table_supplement_20261013"):
        receipt = folder / "integrity_receipt.json"
        frozen = json.loads(receipt.read_text())
        for name, expected in frozen["outputs"].items():
            assert sha(folder / name) == expected, f"Frozen artifact drift: {name}"
        for name, expected in frozen["source_hashes"].items():
            assert sha(ROOT / name) == expected, f"Frozen source drift: {name}"
            sources[name] = expected
        snapshots[str(folder.relative_to(ROOT))] = {
            "receipt_sha256": sha(receipt),
            "artifacts_unchanged": len(frozen["outputs"]),
        }
    price_dir = ROOT / "scripts/diet/m3_price_inputs/overall_cpi"
    price_receipt = json.loads((price_dir / "receipt.json").read_text())
    price_review = json.loads((price_dir / "visual_review.json").read_text())
    price_sha = sha(price_dir / "overall_cpi.csv")
    assert price_sha == price_receipt["output_sha256"]
    assert price_sha == price_review["staged_csv_sha256"]
    assert price_review["all_cells_match"] and price_review["reviewed_cells"] == 30
    for name in ("overall_cpi.csv", "receipt.json", "visual_review.json"):
        path = price_dir / name
        sources[str(path.relative_to(ROOT))] = sha(path)
    for name in ("form_item_part_mapping.csv",):
        path = PROFILE / name
        sources[str(path.relative_to(ROOT))] = sha(path)
    checks = json.loads((OUT / "grouping_checks.json").read_text())
    assert checks["households"] == 30123
    assert checks["source_detail_codes"] == 285
    assert checks["numeric_rounding_bytes"] == 0
    for key in (
        "records_with_all_value_channels_missing",
        "records_with_any_negative_value",
        "households_with_any_negative_value",
        "households_with_unknown_member_flag",
        "cpi_unmatched_households",
        "source_records_or_identifiers_exported",
        "nutrition_values_computed",
        "missing_amounts_imputed",
        "source_values_winsorized",
    ):
        assert checks[key] == 0, key
    exported_rows = {}
    for path in sorted(OUT.glob("*.csv")):
        rows = read_csv(path.name)
        fields = set(rows[0])
        assert not fields & {"hhcode", "prcode", "hhno", "idc", "name", "address"}
        assert len(rows) <= 200, "Unexpected record-level export size"
        exported_rows[path.name] = len(rows)
        for row in rows:
            if row.get("measures_suppressed_small_cell") == "TRUE":
                assert 0 < int(row["households"]) < 5
                for key, value in row.items():
                    if re.search("weight|share|rupees|factor|mean|median", key):
                        assert value == "", (path.name, key)
    quality = read_csv("record_quality_by_part.csv")
    assert total(quality, "records") == checks["detail_records"] == 2252450
    presence = read_csv("part_presence_coverage.csv")
    for part in "ABCDE":
        part_rows = [r for r in presence if r["part"] == part]
        assert total(part_rows, "households") == 30123
    bounds = read_csv("group_boundaries_and_population_shares.csv")
    population_totals = []
    for scenario in SCENARIOS:
        rows = sorted(
            [r for r in bounds if r["scenario"] == scenario],
            key=lambda r: int(r["quintile"]),
        )
        summary = checks["scenarios"][scenario]
        assert summary["eligible_households"] == 30123
        assert summary["ineligible_households"] == 0
        assert summary["same_values_share_group"]
        assert not summary["groups_are_official"]
        assert [int(r["quintile"]) for r in rows] == list(range(1, 6))
        assert total(rows, "households") == 30123
        assert close(total(rows, "population_share"), 1)
        population_totals.append(total(rows, "population_weight"))
        for earlier, later in pairwise(rows):
            assert float(earlier["upper_observed_rupees_per_member"]) < float(
                later["lower_observed_rupees_per_member"]
            )
        assert (
            max(abs(float(r["population_share"]) - 0.2) for r in rows)
            <= summary["maximum_tie_population_share"]
        )
    assert all(close(value, population_totals[0]) for value in population_totals)
    transitions = read_csv("sensitivity_transition_counts.csv")
    for change in read_csv("sensitivity_membership_changes.csv"):
        rows = [r for r in transitions if r["scenario"] == change["scenario"]]
        changed = [r for r in rows if r["baseline_group"] != r["alternate_group"]]
        assert total(rows, "households") == 30123
        assert total(changed, "households") == int(change["changed_households"])
        visible_changed = [r for r in changed if r["sum_population_weight"] != ""]
        visible_all = [r for r in rows if r["sum_population_weight"] != ""]
        known_changed_weight = total(visible_changed, "sum_population_weight")
        if len(visible_all) == len(rows):
            assert close(
                known_changed_weight / population_totals[0],
                float(change["population_changed_share"]),
            )
        else:
            # Small transition-cell weights stay suppressed. Check the feasible
            # interval using published national totals rather than exposing them.
            suppressed_weight = population_totals[0] - total(
                visible_all, "sum_population_weight"
            )
            reported = float(change["population_changed_share"]) * population_totals[0]
            assert known_changed_weight - 1e-6 <= reported
            assert reported <= known_changed_weight + suppressed_weight + 1e-6
    geographies = read_csv("group_coverage_by_geography.csv")
    for bound in bounds:
        rows = [
            r
            for r in geographies
            if (r["scenario"], r["quintile"]) == (bound["scenario"], bound["quintile"])
        ]
        assert len(rows) == 8
        assert total(rows, "households") == int(bound["households"])
        assert close(
            total(rows, "sum_population_weight"), float(bound["population_weight"])
        )
    missing = read_csv("baseline_missingness_coverage.csv")
    assert total(missing, "households") == 30123
    absent = [r for r in missing if int(r["absent_detail_parts"]) > 0]
    assert (
        total(absent, "households") == checks["households_with_any_absent_detail_part"]
    )
    factors = read_csv("temporal_cpi_factors.csv")
    for residence in ("rural", "urban"):
        rows = [r for r in factors if r["residence"] == residence]
        assert len(rows) == 9
        mean = total(rows, "overall_cpi") / 9
        assert close(total(rows, "temporal_factor") / 9, 1)
        for row in rows:
            assert close(float(row["residence_mean_cpi"]), mean)
            assert close(
                float(row["temporal_factor"]), float(row["overall_cpi"]) / mean
            )
    with (PROFILE / "detail_to_parent_subtotal_diagnostic.csv").open() as stream:
        prior = [r for r in csv.DictReader(stream) if r["residence"] == "all"]
    amounts = read_csv("scenario_observed_amount_diagnostic.csv")
    nominal = next(r for r in amounts if r["scenario"] == "nominal")
    assert close(
        total(prior, "detail_monthly_weighted_mean"),
        float(nominal["weighted_observed_monthly_mean_rupees"]),
    )
    verifier = sha(ROOT / "verify_plan.py")
    assert (
        verifier == "a0dce0308eb9965e29da0157b6557e285ab54fba351380719ffc13306d39126d"
    )
    receipt = {
        "date": "2026-10-13",
        "status": "PASS_EXPLORATORY_GROUPING_ONLY_NO_ANALYTICAL_ACCEPTANCE",
        "source_hashes": sources,
        "frozen_snapshots": snapshots,
        "verifier_original_sha256": verifier,
        "verifier_executed": False,
        "csv_row_counts": exported_rows,
        "source_record_or_identifier_exports": 0,
        "shared_registry_processed_state_dashboard_writes": 0,
        "outputs": {
            p.name: sha(p)
            for p in sorted(OUT.iterdir())
            if p.is_file() and p.name != "integrity_receipt.json"
        },
    }
    (OUT / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        "PASS: aggregate consistency, source bindings, prior snapshots and export scope."
    )


if __name__ == "__main__":
    main()
