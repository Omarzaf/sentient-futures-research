"""Check source transcription, inverse diagnostics and frozen-output boundaries."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
import tempfile
import unittest
from itertools import pairwise
from pathlib import Path

ROOT = next(
    directory
    for directory in Path(__file__).resolve().parents
    if (directory / "tools/gfi_gap.py").exists()
    or (directory / "scripts/gfi_gap.py").exists()
)
SCRIPT = ROOT / "scripts/gfi_gap.py"
if not SCRIPT.exists():
    SCRIPT = ROOT / "tools/gfi_gap.py"
SPEC = importlib.util.spec_from_file_location("tested_gfi_gap", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
gfi_gap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gfi_gap
SPEC.loader.exec_module(gfi_gap)

INPUTS = ROOT / "data/altprotein_proxy_inputs.csv"
REFERENCE = ROOT / "data/reference_proxy_scenarios.csv"
if not REFERENCE.exists():
    REFERENCE = ROOT / "data/altprotein_proxy_scenarios.csv"
CATEGORIES = ROOT / "data/gfi_categories.csv"


class GfiGapTests(unittest.TestCase):
    """Verify numerical meaning and input preservation, not merely output formatting."""

    @classmethod
    def setUpClass(cls) -> None:
        """Read the immutable contract and calculate the supplement once."""
        cls.before = {
            file: file.read_bytes() for file in (INPUTS, REFERENCE, CATEGORIES)
        }
        cls.model = gfi_gap.Model(INPUTS)
        cls.result = gfi_gap.build_diagnostics(INPUTS, REFERENCE, CATEGORIES)
        cls.baseline = cls.model.draws(gfi_gap.Sensitivity("baseline"))
        cls.zero_floor = cls.model.draws(gfi_gap.Sensitivity("zero", drift_floor=0))

    def test_frozen_inputs_and_127_reference_rows_unchanged(self) -> None:
        """Require the approved baseline checksums as well as pre/post byte identity."""
        expected = {
            INPUTS: "93ae9dddbfa59c1930b1deaba3a31a3cc273fa8a43077f9dcf735c0d9e64aa37",
            REFERENCE: "98c5a19c94ecd891be7d1a44d24a9004268f160c96f6212c00386a3976c0e7b4",
        }
        for file, prior in self.before.items():
            with self.subTest(file=file.name):
                self.assertEqual(file.read_bytes(), prior)
        for file, digest in expected.items():
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(), digest)
        self.assertEqual(
            self.result["source_row_counts"],
            {"proxy_inputs": 106, "proxy_reference": 127, "gfi_category_cells": 20},
        )

    def test_category_totals_and_missing_fermentation_baseline(self) -> None:
        """Check the original domestic totals and preserve the source's dash."""
        summaries = self.result["category_reconciliation"]
        self.assertEqual(
            [row["reported_total_crore"] for row in summaries],
            [351, 7475, 12779, 18963],
        )
        self.assertTrue(
            all(row["reported_minus_known_sum_crore"] == 0 for row in summaries)
        )
        self.assertEqual(summaries[0]["unresolved_cells"], 1)
        self.assertEqual(summaries[0]["status"], "unresolved_source_dash")
        for row in self.result["category_growth"]:
            if row["category_id"] == "fermentation":
                self.assertEqual(row["base_source_display"], "-")
                self.assertIsNone(row["base_crore"])
                self.assertIsNone(row["absolute_increase_crore"])
                self.assertIsNone(row["source_value_cagr_percent"])

    def test_category_sum_discrepancy_is_retained(self) -> None:
        """Never alter source category values to force agreement with a total."""
        rows = gfi_gap.load_categories(CATEGORIES)
        row = next(
            item
            for item in rows
            if item["category_id"] == "eggs" and item["scenario"] == "low"
        )
        row["value_crore"] = "528"
        row["source_display"] = "528"
        growth, sums = gfi_gap.category_diagnostics(rows)
        self.assertEqual(sums[1]["reported_minus_known_sum_crore"], -1)
        self.assertEqual(sums[1]["status"], "source_discrepancy_preserved")
        self.assertEqual(
            next(
                item
                for item in growth
                if item["category_id"] == "eggs" and item["scenario"] == "low"
            )["target_crore"],
            528,
        )

    def test_extraction_rejects_dash_as_zero_and_duplicate_cells(self) -> None:
        """Catch silent null-to-zero substitution and repeated source cells."""
        source = gfi_gap.read_rows(CATEGORIES)
        for variant in ("zero", "duplicate", "display_mismatch"):
            rows = [dict(row) for row in source]
            if variant == "duplicate":
                rows.append(dict(rows[0]))
            elif variant == "display_mismatch":
                rows[0]["value_crore"] = "101"
            else:
                next(
                    row
                    for row in rows
                    if row["category_id"] == "fermentation" and row["year"] == "2022"
                )["value_crore"] = "0"
            with self.subTest(
                variant=variant
            ), tempfile.TemporaryDirectory() as temporary:
                file = Path(temporary) / "categories.csv"
                with file.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaises(ValueError):
                    gfi_gap.load_categories(file)

    def test_hand_calculable_growth_and_missing_cases(self) -> None:
        """Use eight doublings to detect a mistaken five-year observation horizon."""
        self.assertEqual(gfi_gap.annual_growth(100, 25600, 8), 1)
        self.assertEqual(gfi_gap.annual_growth(100, 100, 8), 0)
        self.assertIsNone(gfi_gap.annual_growth(None, 100, 8))
        self.assertIsNone(gfi_gap.annual_growth(0, 100, 8))
        with self.assertRaises(ValueError):
            gfi_gap.annual_growth(-1, 100, 8)
        with self.assertRaises(ValueError):
            gfi_gap.annual_growth(1, 100, 0)

    def test_required_growth_hand_calculation_and_forward_recovery(self) -> None:
        """Invert eight triplings and recover every GFI target via the forward model."""
        self.assertAlmostEqual(gfi_gap.required_growth(6561, 1, 8), 2, places=12)
        with self.assertRaises(ValueError):
            gfi_gap.required_growth(1, 0, 8)
        for row in self.result["required_growth_grid"]:
            draw = gfi_gap.Draw(
                0, row["elasticity"], row["required_extra_growth_percent"] / 100, 0, 1
            )
            recovered = self.model.total("India", 2030, draw)
            self.assertTrue(
                math.isclose(
                    recovered, row["conditional_target_million_usd"], rel_tol=1e-12
                )
            )

    def test_required_growth_ranges_are_assumption_bounds(self) -> None:
        """Check independently reviewed numbers and decreasing requirements with elasticity."""
        expected = [
            (29.186118, 32.378932, 35.650656),
            (38.142261, 41.556424, 45.054968),
            (45.128541, 48.715370, 52.390846),
        ]
        for row, values in zip(self.result["target_comparison"], expected, strict=True):
            actual = [
                row["required_growth_min_percent"],
                row["required_growth_at_midpoint_elasticity_percent"],
                row["required_growth_max_percent"],
            ]
            for observed, target in zip(actual, values, strict=True):
                self.assertAlmostEqual(observed, target, places=5)
            grid = [
                item["required_extra_growth_percent"]
                for item in self.result["required_growth_grid"]
                if item["scenario"] == row["scenario"]
            ]
            self.assertEqual(len(grid), 21)
            self.assertTrue(all(a > b for a, b in pairwise(grid)))
            self.assertGreater(min(grid), self.model.drift_max * 100)

    def test_fermentation_denominators_are_distinct(self) -> None:
        """Distinguish share of GFI total from arithmetic reduction of the gap."""
        low = self.result["target_comparison"][0]
        self.assertAlmostEqual(
            low["fermentation_share_of_target_percent"], 4.254180602006689, places=10
        )
        self.assertAlmostEqual(
            low["gap_reduction_if_fermentation_subtracted_percent"],
            5.2829713660495266,
            places=10,
        )
        self.assertGreater(
            low["gap_reduction_if_fermentation_subtracted_percent"],
            low["fermentation_share_of_target_percent"],
        )

    def test_factor_products_recover_each_draw(self) -> None:
        """Verify the direct equation against its multiplicative and logarithmic forms."""
        self.assertEqual(gfi_gap.factor_product(2, 3, 5, 7), 210)
        for row in self.result["factor_draws"]:
            direct = row["india_2030_million_usd_2025_prices"]
            product = self.model.anchor * row["total_multiple"]
            log_value = self.model.anchor * math.exp(
                sum(
                    row[key]
                    for key in (
                        "log_population",
                        "log_income",
                        "log_urban",
                        "log_extra_growth",
                    )
                )
            )
            self.assertTrue(math.isclose(direct, product, rel_tol=1e-12))
            self.assertTrue(math.isclose(direct, log_value, rel_tol=1e-12))

    def test_midpoint_scenario_is_not_labelled_as_sample_median(self) -> None:
        """Guard against replacing the median of products with midpoint-factor products."""
        midpoint = self.result["midpoint_parameter_illustration"]
        median = next(
            row["p50_million_usd_2025_prices"]
            for row in self.result["sensitivities"]
            if row["case"] == "baseline"
            and row["country"] == "India"
            and row["year"] == 2030
        )
        self.assertAlmostEqual(
            midpoint["india_2030_million_usd_2025_prices"], 188.1131102757077, places=9
        )
        self.assertAlmostEqual(median, 187.81184357758852, places=9)
        self.assertGreater(
            abs(midpoint["india_2030_million_usd_2025_prices"] - median), 0.3
        )

    def test_rng_draw_order_matches_retained_engine(self) -> None:
        """Independently draw the frozen e,d,w,k sequence and check retained IDs."""
        rng = random.Random(20261015)
        for index, draw in enumerate(self.baseline[:12], 1):
            expected = (
                rng.uniform(1, self.model.elasticity_max),
                rng.uniform(self.model.drift_min, self.model.drift_max),
                rng.uniform(0, 1),
                rng.uniform(self.model.industry_min, self.model.industry_max),
            )
            self.assertEqual(
                (draw.elasticity, draw.drift, draw.animal_weight, draw.industry),
                expected,
            )
            self.assertEqual(draw.draw_id, index)
        fixed = self.model.draws(
            gfi_gap.Sensitivity("fixed", elasticity=1, animal_weight=0), 12
        )
        for original, changed in zip(self.baseline[:12], fixed, strict=True):
            self.assertEqual(original.drift, changed.drift)
            self.assertEqual(original.industry, changed.industry)

    def test_zero_floor_is_rescaled_paired_not_clamped(self) -> None:
        """Retain paired parameters and rescale every drift variate, not only negatives."""
        for original, changed in zip(self.baseline, self.zero_floor, strict=True):
            self.assertEqual(
                (
                    original.draw_id,
                    original.elasticity,
                    original.animal_weight,
                    original.industry,
                ),
                (
                    changed.draw_id,
                    changed.elasticity,
                    changed.animal_weight,
                    changed.industry,
                ),
            )
            uniform = (original.drift - self.model.drift_min) / (
                self.model.drift_max - self.model.drift_min
            )
            self.assertAlmostEqual(
                changed.drift, uniform * self.model.drift_max, places=14
            )
            self.assertGreater(changed.drift, max(0, original.drift))

    def test_zero_floor_never_lowers_any_paired_country_result(self) -> None:
        """Check monotonicity across every paired draw, country and reporting year."""
        for country in gfi_gap.COUNTRIES:
            for year in gfi_gap.YEARS:
                for original, changed in zip(
                    self.baseline, self.zero_floor, strict=True
                ):
                    self.assertGreater(
                        self.model.total(country, year, changed),
                        self.model.total(country, year, original),
                    )

    def test_zero_floor_effect_and_separate_elasticity_cases(self) -> None:
        """Confirm the floor effect and expose US elasticity dependence separately."""
        selected = {
            row["case"]: row
            for row in self.result["sensitivities"]
            if row["country"] == "India" and row["year"] == 2030
        }
        zero = selected["drift_floor_zero"]
        self.assertAlmostEqual(
            zero["p50_million_usd_2025_prices"], 202.21380943224312, places=9
        )
        self.assertAlmostEqual(
            zero["median_change_percent_from_baseline"], 7.668294810547915, places=9
        )
        self.assertEqual(selected["elasticity_grid_00"]["fixed_elasticity"], 1)
        self.assertIsNone(zero["fixed_elasticity"])
        combined = selected["combined_zero_floor_elasticity_1"]
        self.assertEqual(combined["fixed_elasticity"], 1)
        self.assertEqual(combined["drift_lower_fraction"], 0)
        self.assertLess(
            selected["income_drift_overlap"]["p50_million_usd_2025_prices"],
            selected["baseline"]["p50_million_usd_2025_prices"],
        )

    def test_maximum_is_a_boundary_not_a_sample_record(self) -> None:
        """Check sampled support against the analytical endpoint and conditional target."""
        maxima = self.result["maxima"]
        self.assertAlmostEqual(
            maxima["sampled_max_cagr_percent"], 33.55650864512969, places=9
        )
        self.assertAlmostEqual(
            maxima["analytic_max_cagr_percent"], 33.68648622291266, places=9
        )
        self.assertAlmostEqual(
            maxima["analytic_max_million_usd"], 462.0299875337362, places=9
        )
        self.assertLess(
            maxima["sampled_max_million_usd"], maxima["analytic_max_million_usd"]
        )
        self.assertLess(
            maxima["analytic_max_million_usd"],
            self.result["target_comparison"][0]["conditional_target_million_usd"],
        )

    def test_frozen_summary_parity_includes_retained_controls(self) -> None:
        """Require the baseline and existing sensitivities to match all checked rows."""
        checks = self.result["baseline_reference_checks"]
        self.assertEqual(len(checks), 55)
        self.assertEqual(sum("_market_value_p" in row["row_id"] for row in checks), 18)
        self.assertTrue(any("without_urban_animal" in row["row_id"] for row in checks))
        self.assertTrue(any("ecosystem_fixed_high" in row["row_id"] for row in checks))
        for row in checks:
            self.assertEqual(f"{row['actual_value']:.6f}", row["reference_value"])

    def test_independent_rerun_and_exports_are_deterministic(self) -> None:
        """Rerun calculation and compare complete artifact bytes and declared hashes."""
        rerun = gfi_gap.build_diagnostics(INPUTS, REFERENCE, CATEGORIES)
        self.assertEqual(rerun, self.result)
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / "first", Path(temporary) / "second"
            gfi_gap.write_outputs(self.result, first)
            gfi_gap.write_outputs(rerun, second)
            self.assertEqual(
                {file.name for file in first.iterdir()},
                {file.name for file in second.iterdir()},
            )
            for file in first.iterdir():
                self.assertEqual(file.read_bytes(), (second / file.name).read_bytes())
            receipt = json.loads((first / "artifact-hashes.json").read_text())
            for row in receipt["files"]:
                self.assertEqual(gfi_gap.sha256(first / row["path"]), row["sha256"])
            self.assertEqual(len(gfi_gap.read_rows(first / "factor-draws.csv")), 10000)
            summary = json.loads((first / "diagnostics.json").read_text())
            self.assertNotIn("factor_draws", summary)
            self.assertEqual(summary["factor_draws_artifact"]["rows"], 10000)

    def test_output_cannot_contain_immutable_sources(self) -> None:
        """Fail before writing if the requested output directory includes the inputs."""
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--inputs",
                str(INPUTS),
                "--reference",
                str(REFERENCE),
                "--categories",
                str(CATEGORIES),
                "--output",
                str(INPUTS.parent),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not contain immutable source files", result.stderr)


if __name__ == "__main__":
    unittest.main()
