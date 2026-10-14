"""Bind final source inputs and run aggregate-only coverage checks."""

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PROFILE = ROOT / "scripts/diet/m3_microdata_profile"
FACTOR_DIR = ROOT / "scripts/diet/m3_calibration_spec"


def sha(path: Path) -> str:
    """Return a streaming file hash without showing source records."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    """Read a local evidence receipt."""
    return json.loads(path.read_text())


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read source-factor or exported aggregate rows only."""
    with path.open() as stream:
        return list(csv.DictReader(stream))


def bind(expected: str) -> None:
    """Freeze source bindings only after the specialist supplies a final hash."""
    assert sha(FACTOR_DIR / "compiled_factors.csv") == expected
    paths = {}
    for folder in (
        PROFILE,
        PROFILE / "table_supplement_20261013",
        PROFILE / "grouping_exploration_20261013",
    ):
        receipt = folder / "integrity_receipt.json"
        data = read_json(receipt)
        paths[str(receipt.relative_to(ROOT))] = sha(receipt)
        for name, digest in data["outputs"].items():
            target = folder / name
            assert sha(target) == digest, f"Frozen artifact drift: {name}"
            paths[str(target.relative_to(ROOT))] = digest
        for name, digest in data["source_hashes"].items():
            assert sha(ROOT / name) == digest, f"Frozen source drift: {name}"
            paths[name] = digest
    factor_receipt = read_json(FACTOR_DIR / "receipt.json")
    for name, digest in factor_receipt["input_sha256"].items():
        assert sha(ROOT / name) == digest, f"Factor input drift: {name}"
        paths[name] = digest
    for name, digest in factor_receipt["outputs"].items():
        target = FACTOR_DIR / name
        assert sha(target) == digest, f"Factor output drift: {name}"
        paths[str(target.relative_to(ROOT))] = digest
    for target in FACTOR_DIR.rglob("*"):
        if target.is_file() and "__pycache__" not in target.parts:
            paths[str(target.relative_to(ROOT))] = sha(target)
    for name in (
        "scripts/diet/m3_food_crosswalk/questionnaire_inventory.csv",
        "scripts/diet/m3_price_inputs/price_indices_staging.csv",
        "scripts/diet/m3_price_inputs/receipt.json",
        "scripts/diet/m3_price_inputs/visual_review.json",
        "scripts/diet/m3_price_inputs/overall_cpi/overall_cpi.csv",
        "scripts/diet/m3_price_inputs/overall_cpi/receipt.json",
        "scripts/diet/m3_price_inputs/overall_cpi/visual_review.json",
        "scripts/diet/m3_calibration_coverage_20261013/SPEC.json",
        "verify_plan.py",
    ):
        paths[name] = sha(ROOT / name)
    assert (
        paths["verify_plan.py"]
        == "a0dce0308eb9965e29da0157b6557e285ab54fba351380719ffc13306d39126d"
    )
    prices = read_json(ROOT / "scripts/diet/m3_price_inputs/visual_review.json")
    assert prices["pass"] and prices["reviewed_cells"] == 60
    assert (
        prices["staged_csv_sha256"]
        == paths["scripts/diet/m3_price_inputs/price_indices_staging.csv"]
    )
    binding = {
        "date": "2026-10-13",
        "stage": "PRECOMPUTE_SOURCE_BINDING",
        "compiled_factor_sha256": expected,
        "paths": paths,
        "intake_acceptance": False,
    }
    (OUT / "input_bindings.json").write_text(json.dumps(binding, indent=2) + "\n")
    print(f"PASS: {len(paths)} source and frozen-artifact bindings.")


def check_bindings() -> dict:
    """Fail on any source or frozen-output drift before or after computation."""
    binding = read_json(OUT / "input_bindings.json")
    for name, digest in binding["paths"].items():
        assert sha(ROOT / name) == digest, f"Input drift: {name}"
    return binding


def near(left: float, right: float) -> bool:
    """Allow only floating-point and CSV serialization tolerance."""
    return math.isclose(left, right, rel_tol=1e-11, abs_tol=1e-6)


def verify() -> None:
    """Validate output grain, accounting, sample support and preservation."""
    binding = check_bindings()
    checks = read_json(OUT / "coverage_checks.json")
    assert (
        checks["households"] == 30123
        and checks["reconstructed_group_cells_match"] == 120
    )
    for key in (
        "source_household_or_person_records_or_identifiers_exported",
        "nutrient_unit_costs_computed",
        "imputed_nutrients_computed",
        "total_intake_or_gap_computed",
    ):
        assert checks[key] == 0
    scenarios = set(checks["factor_scenarios"])
    assert len(scenarios) == 8
    rows_by_file = {}
    for path in sorted(OUT.glob("*.csv")):
        rows = read_csv(path)
        rows_by_file[path.name] = len(rows)
        assert rows and not {"hhcode", "prcode", "hhno", "idc"} & set(rows[0])
        # Protein amounts and individual costs must never enter these exports.
        assert not {
            "protein_G",
            "value_G",
            "adjusted_value_G",
            "nutrient_unit_cost",
        } & set(rows[0])
        for row in rows:
            if row.get("measures_suppressed_small_cell") == "TRUE":
                for field, value in row.items():
                    if any(
                        token in field
                        for token in ("weight", "share", "rupees", "ratio")
                    ):
                        assert value == "", (path.name, field)
    cells = read_csv(OUT / "calibration_cell_coverage.csv")
    assert len(cells) == 960
    key_fields = (
        "factor_scenario",
        "grouping_scenario",
        "province",
        "region",
        "quintile",
    )
    assert len({tuple(r[f] for f in key_fields) for r in cells}) == len(cells)
    strata = defaultdict(list)
    for row in cells:
        assert int(row["eligible_households"]) + int(
            row["ineligible_households"]
        ) == int(row["households"])
        strata[(row["factor_scenario"], row["grouping_scenario"])].append(row)
    assert len(strata) == 24
    for (factor, _), rows in strata.items():
        assert len(rows) == 40
        assert sum(int(r["households"]) for r in rows) == 30123
        assert (
            sum(int(r["eligible_households"]) for r in rows)
            == checks["scenario_checks"][factor]["eligible_households"]
        )
    hh = read_csv(OUT / "household_eligibility_summary.csv")
    for factor in scenarios:
        rows = [r for r in hh if r["factor_scenario"] == factor]
        assert sum(int(r["households"]) for r in rows) == 30123
        assert (
            sum(int(r["households"]) for r in rows if r["eligible"] == "TRUE")
            == checks["scenario_checks"][factor]["eligible_households"]
        )
    controls = read_csv(OUT / "source_expenditure_controls.csv")
    national = read_csv(OUT / "national_expenditure_coverage.csv")
    for factor in scenarios:
        rows = [r for r in national if r["factor_scenario"] == factor]
        for scope in ("AT_HOME", "PREPARED", "SERVICE"):
            observed = [r for r in rows if r["source_scope"] == scope]
            target = [r for r in controls if r["source_scope"] == scope]
            assert near(
                math.fsum(float(r["weighted_nominal_daily_rupees"]) for r in observed),
                math.fsum(float(r["weighted_nominal_daily_rupees"]) for r in target),
            )
        for measure in (
            "nominal_share_of_food_expenditure",
            "adjusted_share_of_food_expenditure",
        ):
            assert near(math.fsum(float(r[measure]) for r in rows if r[measure]), 1)
    ledger = read_csv(OUT / "expenditure_ledger.csv")
    for factor in scenarios:
        for control in controls:
            rows = [
                r
                for r in ledger
                if r["factor_scenario"] == factor
                and r["region"] == control["region"]
                and r["source_scope"] == control["source_scope"]
            ]
            assert rows
            for measure in (
                "weighted_nominal_daily_rupees",
                "weighted_adjusted_daily_rupees",
            ):
                if control[measure] == "":
                    assert control["source_scope"] == "SERVICE"
                    continue
                if all(r[measure] != "" for r in rows):
                    assert near(
                        math.fsum(float(r[measure]) for r in rows),
                        float(control[measure]),
                    )
                else:
                    # R verified exact conservation before small-cell suppression.
                    assert checks["scenario_checks"][factor][
                        "conservation_nominal_and_adjusted"
                    ]
    missing = read_csv(OUT / "item_channel_missingness.csv")
    assert (
        len(missing) == 480 and len({(r["itc"], r["channel"]) for r in missing}) == 480
    )
    assert sum(int(r["positive_quantity_without_positive_value"]) for r in missing) == 0
    routes = read_csv(OUT / "factor_route_inventory.csv")
    assert len(routes) == 960
    for row in routes:
        if row["role"] in ("K", "SERVICE"):
            assert row["protein_g_per_native_unit"] == ""
        if row["role"] == "DIRECT_ZERO_OUTSIDE_G":
            assert (
                row["itc"] == "110018" and float(row["protein_g_per_native_unit"]) == 0
            )
    price_rows = read_csv(OUT / "temporal_food_price_factors.csv")
    assert len(price_rows) == 36
    for residence in ("rural", "urban"):
        for series in ("food_and_non_alcoholic_beverages", "restaurants_and_hotels"):
            rows = [
                r
                for r in price_rows
                if r["residence"] == residence and r["series"] == series
            ]
            assert len(rows) == 9
            average = math.fsum(float(r["value"]) for r in rows) / 9
            assert near(math.fsum(float(r["temporal_factor"]) for r in rows) / 9, 1)
            assert all(
                near(float(r["temporal_factor"]), float(r["value"]) / average)
                for r in rows
            )
    receipt = {
        "date": "2026-10-13",
        "status": "PASS_EXPLORATORY_COVERAGE_NOT_INTAKE_ACCEPTANCE",
        "input_bindings_sha256": sha(OUT / "input_bindings.json"),
        "source_and_frozen_bindings_verified": len(binding["paths"]),
        "csv_row_counts": rows_by_file,
        "verifier_executed": False,
        "source_household_or_person_exports": 0,
        "outputs": {
            p.name: sha(p)
            for p in sorted(OUT.iterdir())
            if p.is_file() and p.name != "integrity_receipt.json"
        },
    }
    (OUT / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        "PASS: output accounting, 960 calibration cells, source bindings and privacy checks."
    )


def main() -> None:
    """Expose explicit bind, run and verify operations for isolated evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", metavar="FINAL_COMPILED_SHA256")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.bind:
        bind(args.bind)
    if args.run:
        check_bindings()
        previous = (
            {p.name: sha(p) for p in OUT.glob("*.csv")}
            if (OUT / "coverage_checks.json").exists()
            else {}
        )
        with (OUT / "run.log").open("w") as log:
            result = subprocess.run(
                ["Rscript", "--vanilla", str(OUT / "coverage.R")],
                cwd=ROOT,
                check=False,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        assert result.returncode == 0, "Coverage failed; inspect aggregate-only run.log"
        check_bindings()
        if previous:
            after = {p.name: sha(p) for p in OUT.glob("*.csv")}
            assert previous == {
                name: after[name] for name in previous
            }, "Existing aggregate CSV output changed on repeat run"
            (OUT / "reproducibility_check.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "csv_outputs_byte_identical": len(previous),
                        "new_unreplicated_csvs": sorted(set(after) - set(previous)),
                        "sha256": after,
                    },
                    indent=2,
                )
                + "\n"
            )
        verify()
    elif args.verify:
        verify()


if __name__ == "__main__":
    main()
