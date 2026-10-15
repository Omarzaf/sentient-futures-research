"""Run and verify isolated, explicitly experimental nutrient-cost estimates."""

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
COVERAGE = ROOT / "scripts/diet/m3_calibration_coverage_20261013"
KEY = ("factor_scenario", "grouping_scenario", "price_scenario")


def sha(path: Path) -> str:
    """Hash file bytes without displaying their contents."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    """Read an evidence receipt."""
    return json.loads(path.read_text())


def csv_rows(path: Path) -> list[dict[str, str]]:
    """Read source-factor or aggregate rows, never public microdata records."""
    with path.open() as stream:
        return list(csv.DictReader(stream))


def near(a: float, b: float) -> bool:
    """Permit only numerical aggregation and text-serialization tolerance."""
    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-8)


def case(row: dict[str, str]) -> tuple[str, ...]:
    """Return the declared experimental scenario key."""
    return tuple(row[k] for k in KEY)


def bind() -> None:
    """Preserve the whole completed coverage chain before any new estimate run."""
    prior = read_json(COVERAGE / "input_bindings.json")
    paths = dict(prior["paths"])
    receipt = read_json(COVERAGE / "integrity_receipt.json")
    for name, digest in receipt["outputs"].items():
        paths[str((COVERAGE / name).relative_to(ROOT))] = digest
    paths[str((COVERAGE / "integrity_receipt.json").relative_to(ROOT))] = sha(
        COVERAGE / "integrity_receipt.json"
    )
    paths[str((OUT / "SPEC.json").relative_to(ROOT))] = sha(OUT / "SPEC.json")
    for name, digest in paths.items():
        assert sha(ROOT / name) == digest, f"Prior evidence drift: {name}"
    binding = {
        "date": "2026-10-13",
        "stage": "PRECOMPUTE_EXPERIMENTAL_SOURCE_BINDING",
        "paths": paths,
    }
    (OUT / "input_bindings.json").write_text(json.dumps(binding, indent=2) + "\n")
    print(f"PASS: {len(paths)} prior-source and frozen-artifact bindings.")


def check_bindings() -> dict:
    """Reject drift in all prior evidence and the predeclared specification."""
    binding = read_json(OUT / "input_bindings.json")
    for name, digest in binding["paths"].items():
        assert sha(ROOT / name) == digest, f"Input drift: {name}"
    return binding


def verify() -> None:
    """Independently check aggregate components, denominators and recombination."""
    binding = check_bindings()
    checks = read_json(OUT / "experimental_checks.json")
    assert checks["households"] == 30123 and checks["experimental_cases"] == 26
    assert checks["experimental_reporting_rows"] == 1820
    assert checks["reconstructed_group_cells_match"] == 120
    assert not checks["numeric_estimates_accepted"]
    for name in (
        "source_values_removed_or_winsorized",
        "gap_or_prevalence_values_computed",
        "source_household_or_person_records_or_identifiers_exported",
    ):
        assert checks[name] == 0
    assert checks["channel_negative_controls"]["channel"]["status"] == "PASS"
    assert checks["channel_negative_controls"]["calibration"]["method_controls"] == 17
    row_counts = {}
    for path in sorted(OUT.glob("*.csv")):
        rows = csv_rows(path)
        row_counts[path.name] = len(rows)
        assert rows
        assert not {
            "hhcode",
            "prcode",
            "hhno",
            "idc",
            "unit_cost",
            "protein_G",
            "value_G",
        } & set(rows[0])
        for row in rows:
            if row.get("measures_suppressed_small_cell") == "TRUE":
                for field, value in row.items():
                    if field != "factor_scenario" and any(
                        s in field
                        for s in ("weight", "share", "rupees", "_g_", "g_per_", "cost")
                    ):
                        assert value == "", (path.name, field)
    means = csv_rows(OUT / "experimental_group_estimates.csv")
    assert len(means) == 1820
    cases = defaultdict(list)
    for row in means:
        cases[case(row)].append(row)
    factors = set(checks["factor_scenarios"])
    groups = {"nominal", "scope_excluded", "cpi_temporal"}
    expected_cases = {(f, g, "food_restaurant_cpi") for f in factors for g in groups}
    expected_cases |= {
        ("baseline", "nominal", p) for p in ("no_cpi", "food_cpi_for_prepared")
    }
    assert set(cases) == expected_cases
    levels = {
        "national": 1,
        "residence": 2,
        "province": 4,
        "province_residence": 8,
        "national_quintile": 5,
        "residence_quintile": 10,
        "stratum": 40,
    }
    additive = (
        "households",
        "members",
        "household_weight",
        "population_weight",
        "source_weighted_g_per_day",
        "imputed_at_home_weighted_g_per_day",
        "imputed_prepared_weighted_g_per_day",
        "total_weighted_g_per_day",
    )
    for rows in cases.values():
        assert len(rows) == 70
        national = next(r for r in rows if r["reporting_level"] == "national")
        assert int(national["households"]) == 30123
        for level, count in levels.items():
            subset = [r for r in rows if r["reporting_level"] == level]
            assert len(subset) == count
            for field in additive:
                assert near(
                    math.fsum(float(r[field]) for r in subset), float(national[field])
                )
        for row in rows:
            population = float(row["population_weight"])
            assert population > 0
            for prefix in ("source", "imputed_at_home", "imputed_prepared", "total"):
                weighted = float(row[f"{prefix}_weighted_g_per_day"])
                per_member = float(row[f"{prefix}_g_per_member_day"])
                assert math.isfinite(weighted) and weighted >= 0
                assert math.isfinite(per_member) and per_member >= 0
                assert near(weighted / population, per_member)
            assert near(
                math.fsum(
                    float(row[f"{p}_g_per_member_day"])
                    for p in ("source", "imputed_at_home", "imputed_prepared")
                ),
                float(row["total_g_per_member_day"]),
            )
            assert near(
                float(row["imputed_share"]),
                (
                    float(row["imputed_at_home_g_per_member_day"])
                    + float(row["imputed_prepared_g_per_member_day"])
                )
                / float(row["total_g_per_member_day"]),
            )
    medians = csv_rows(OUT / "stratum_median_costs.csv")
    assert len(medians) == 1040
    assert (
        len({case(r) + (r["province"], r["region"], r["quintile"]) for r in medians})
        == 1040
    )
    support = {case(r): r for r in csv_rows(OUT / "median_cost_support.csv")}
    assert set(support) == expected_cases
    for key in expected_cases:
        rows = [r for r in medians if case(r) == key]
        assert len(rows) == 40
        values = [float(r["median_cost_rupees_per_g"]) for r in rows]
        assert all(math.isfinite(v) and v > 0 for v in values)
        assert all(int(r["reference_households"]) > 0 for r in rows)
        assert near(
            min(values), float(support[key]["minimum_stratum_median_cost_rupees_per_g"])
        )
        assert near(
            max(values), float(support[key]["maximum_stratum_median_cost_rupees_per_g"])
        )
        national = next(r for r in cases[key] if r["reporting_level"] == "national")
        assert sum(int(r["reference_households"]) for r in rows) == int(
            national["reference_households"]
        )
    # The inherited coverage must agree with its frozen prior aggregate, not only this run's own helpers.
    old_coverage = csv_rows(COVERAGE / "calibration_cell_coverage.csv")
    new_coverage = csv_rows(OUT / "calibration_cell_coverage.csv")
    key_fields = (
        "factor_scenario",
        "grouping_scenario",
        "province",
        "region",
        "quintile",
    )
    old_map = {tuple(r[f] for f in key_fields): r for r in old_coverage}
    assert len(new_coverage) == len(old_map) == 960
    for row in new_coverage:
        old = old_map[tuple(row[f] for f in key_fields)]
        for field in ("households", "eligible_households", "ineligible_households"):
            assert row[field] == old[field]
    tails = csv_rows(OUT / "source_outlier_influence.csv")
    assert len(tails) == 16
    for factor in factors:
        subset = sorted(
            [r for r in tails if r["factor_scenario"] == factor],
            key=lambda r: float(r["requested_unweighted_household_fraction"]),
        )
        assert len(subset) == 2
        for row in subset:
            assert (
                int(row["households"]) >= int(row["rank_cutoff_household_count"]) >= 31
            )
            assert 0 <= float(row["weighted_source_protein_share"]) <= 1
            assert 0 <= float(row["population_weight_share"]) <= 1
            assert row["source_values_removed_or_winsorized"] == "0"
        assert float(subset[0]["weighted_source_protein_share"]) <= float(
            subset[1]["weighted_source_protein_share"]
        )
    recombination = csv_rows(OUT / "national_recombination_checks.csv")
    assert len(recombination) == 156
    assert all(
        float(r["maximum_relative_recombination_error"]) < 1e-11 for r in recombination
    )
    receipt = {
        "date": "2026-10-13",
        "status": "PASS_NUMERICAL_CHECKS_EXPERIMENTAL_PENDING_REVIEW",
        "input_bindings_sha256": sha(OUT / "input_bindings.json"),
        "prior_source_and_frozen_artifact_bindings": len(binding["paths"]),
        "csv_row_counts": row_counts,
        "accepted_intake_or_gap": False,
        "central_files_changed": False,
        "strict_verifier_executed": False,
        "outputs": {
            p.name: sha(p)
            for p in sorted(OUT.iterdir())
            if p.is_file() and p.name != "integrity_receipt.json"
        },
    }
    (OUT / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        "PASS: 26 experimental cases, 1040 cost cells, 1820 aggregate estimates and preserved prior evidence."
    )


def main() -> None:
    """Expose explicit bind, compute and aggregate verification stages."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.bind:
        bind()
    if args.run:
        check_bindings()
        previous = (
            {p.name: sha(p) for p in OUT.glob("*.csv")}
            if (OUT / "experimental_checks.json").exists()
            else {}
        )
        with (OUT / "run.log").open("w") as log:
            result = subprocess.run(
                ["Rscript", "--vanilla", str(OUT / "estimates.R")],
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
        assert (
            result.returncode == 0
        ), "Experimental run failed; inspect aggregate-only run.log"
        check_bindings()
        if previous:
            after = {p.name: sha(p) for p in OUT.glob("*.csv")}
            assert (
                previous == after
            ), "Experimental aggregate outputs failed byte-identical reproduction"
            (OUT / "reproducibility_check.json").write_text(
                json.dumps(
                    {
                        "status": "PASS",
                        "csv_outputs_byte_identical": len(after),
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
