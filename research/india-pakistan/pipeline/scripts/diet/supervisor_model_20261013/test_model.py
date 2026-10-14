"""Test physical unit arithmetic and reject unsupported total-diet inference."""

from __future__ import annotations

import copy
import csv
import importlib.util
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "supervisor_model", HERE / "build_model.py"
)
assert SPEC and SPEC.loader
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


class PhysicalModelTests(unittest.TestCase):
    """Exercise calculations independently of empirical output expectations."""

    def test_monthly_kg_conversion(self) -> None:
        """One kg monthly at 18.8g/100g yields 188/30g daily."""
        self.assertEqual(
            model.daily_content(F(1), "kg/person/month", F(188), "Kg"), F(94, 15)
        )

    def test_monthly_gram_conversion(self) -> None:
        """A gram quantity must not receive the kg multiplier again."""
        self.assertEqual(
            model.daily_content(F(30), "g/person/month", F(122, 1000), "Gm"),
            F(122, 1000),
        )

    def test_monthly_quantity_is_not_fourteen_day_recall(self) -> None:
        """Table23 monthly values reject a second raw-recall conversion."""
        with self.assertRaises(ValueError):
            model.daily_content(F(1), "kg/person/month", F(188), "Kg", days=14)

    def test_native_unit_mismatch_rejected(self) -> None:
        """Count, litre and mass factors cannot be silently interchanged."""
        for unit, native in [
            ("count/person/month", "Kg"),
            ("litre/person/month", "Gm"),
            ("kg/person/month", "Gm"),
        ]:
            with self.subTest(unit=unit, native=native), self.assertRaises(ValueError):
                model.daily_content(F(1), unit, F(1), native)

    def test_already_edible_egg_portion(self) -> None:
        """A USDA edible 50g egg uses Pakistan12.2 without another shell factor."""
        factor = model.mass_factor(F("12.2"), F(50), F(1), already_edible=True)
        self.assertEqual(factor, F("6.1"))
        with self.assertRaises(ValueError):
            model.mass_factor(F("12.2"), F(50), F("0.87"), already_edible=True)

    def test_component_products_precede_average(self) -> None:
        """Goat/sheep factors retain species-specific edible coefficients."""
        factors = [
            model.mass_factor(F("19.6"), F(1000), F("0.69")),
            model.mass_factor(F("17.5"), F(1000), F("0.75")),
        ]
        self.assertEqual(model.equal_factor(factors), F("133.245"))
        self.assertNotEqual(model.equal_factor(factors), F("18.55") * 10 * F("0.72"))

    def test_missing_factor_and_quantity_remain_missing(self) -> None:
        """Missing cannot become observed zero through unit arithmetic."""
        self.assertIsNone(model.daily_content(None, "kg/person/month", F(1), "Kg"))
        self.assertIsNone(model.daily_content(F(1), "kg/person/month", None, "Kg"))

    def test_zero_factor_is_preserved(self) -> None:
        """A named zero-protein food stays zero without imputation."""
        self.assertEqual(model.daily_content(F(3), "kg/person/month", F(0), "Kg"), 0)

    def test_partial_sum_is_never_a_complete_total(self) -> None:
        """One unresolved component prevents the complete sum."""
        self.assertIsNone(model.complete_sum([F(1), None, F(3)]))
        self.assertEqual(model.complete_sum([F(1), F(0), F(3)]), F(4))

    def test_whole_basket_calibration_rejected(self) -> None:
        """Meat cannot receive milk/cereal or mixed-basket protein costs."""
        for donor in ["whole_basket", "dairy", "cereals", "", "meat;dairy"]:
            with self.subTest(donor=donor), self.assertRaises(ValueError):
                model.impute_within_group(F(100), "meat", donor, F(2), True)

    def test_missing_same_group_support_stays_missing(self) -> None:
        """Even within a group, expenditure and comparable cost support are needed."""
        self.assertIsNone(model.impute_within_group(F(100), "meat", "meat", None, True))
        self.assertIsNone(model.impute_within_group(None, "meat", "meat", F(2), True))
        self.assertIsNone(
            model.impute_within_group(F(100), "meat", "meat", F(2), False)
        )
        self.assertEqual(
            model.impute_within_group(F(100), "meat", "meat", F(2), True), F(50)
        )

    def test_invalid_mass_or_edible_coefficient_rejected(self) -> None:
        """Negative quantities and impossible refuse factors stop calculation."""
        for protein, mass, edible in [
            (F(-1), F(1000), F(1)),
            (F(20), F(0), F(1)),
            (F(20), F(1000), F("1.2")),
        ]:
            with self.subTest(values=(protein, mass, edible)), self.assertRaises(
                ValueError
            ):
                model.mass_factor(protein, mass, edible)


class EmpiricalContractTests(unittest.TestCase):
    """Require full source coverage and prevent promotion of partial estimates."""

    def test_thousandfold_source_corruption_rejected(self) -> None:
        """Changing a supplied value must fail raw XLS reconciliation."""
        rows = model.read_csv(model.ROOT / "scripts/diet/pakistan_diet_rows.csv")
        rows[0]["value"] = str(float(rows[0]["value"]) * 1000)
        with self.assertRaisesRegex(ValueError, "Quantity differs"):
            model.reconcile_quantities(rows)

    def test_source_identity_and_vintage_corruptions_rejected(self) -> None:
        """A source row cannot silently become another survey or vintage."""
        rows = model.read_csv(model.ROOT / "scripts/diet/pakistan_diet_rows.csv")
        for field, value in [("source_id", "not_table23"), ("period", "2018-19")]:
            changed = copy.deepcopy(rows)
            changed[0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "identity or survey"
            ):
                model.reconcile_quantities(changed)

    def test_physical_factor_corruptions_rejected(self) -> None:
        """Bad catalog, component and compiled values each fail algebra checks."""
        root = model.ROOT / "scripts/diet/m3_calibration_spec"
        compiled = model.read_csv(root / "compiled_factors.csv")
        components = model.read_csv(root / "component_factors.csv")
        catalog = {
            r["factor_id"]: r for r in model.read_csv(root / "factor_catalog.csv")
        }
        bad_compiled = copy.deepcopy(compiled)
        bad_compiled[0]["protein_factor_numerator"] = str(
            int(bad_compiled[0]["protein_factor_numerator"]) * 1000
        )
        with self.assertRaisesRegex(ValueError, "Compiled factor differs"):
            model.verify_factor_algebra(bad_compiled, components, catalog)
        bad_component = copy.deepcopy(components)
        bad_component[0]["edible_fraction"] = "0.5"
        with self.assertRaisesRegex(ValueError, "component product"):
            model.verify_factor_algebra(compiled, bad_component, catalog)
        bad_catalog = copy.deepcopy(catalog)
        bad_catalog["protein:" + components[0]["protein_ref"]]["value"] = "999"
        with self.assertRaisesRegex(ValueError, "source catalog"):
            model.verify_factor_algebra(compiled, components, bad_catalog)

    def test_complete_basket_coverage_and_missing_total(self) -> None:
        """Every Table23 item is explained, and omitted foods block total intake."""
        with tempfile.TemporaryDirectory() as directory:
            receipt = model.build(Path(directory))
            with (Path(directory) / "food_coverage.csv").open() as handle:
                coverage = list(csv.DictReader(handle))
            self.assertEqual(len(coverage), 38)
            self.assertEqual(len({r["food_group"] for r in coverage}), 38)
            self.assertTrue(all(r["evidence_paths"] and r["reason"] for r in coverage))
            with (Path(directory) / "scenario_summary.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(rows)
            self.assertTrue(all(not r["whole_diet_protein_g_person_day"] for r in rows))
            self.assertTrue(all(r["imputed_food_count"] == "0" for r in rows))
            self.assertTrue(
                all(
                    r["tier"] == "derived" and r["headline_eligible"] == "false"
                    for r in rows
                )
            )
            self.assertTrue(
                all(r["residence_ranking_eligible"] == "false" for r in rows)
            )
            self.assertEqual(receipt["quantity_rows_reconciled_to_xls"], 684)
            self.assertEqual(receipt["old_sensitivity_cases_disposed"], 26)

    def test_animal_scenarios_have_all_five_physical_components(self) -> None:
        """Eligible animal subtotals cannot omit an inconvenient food."""
        with tempfile.TemporaryDirectory() as directory:
            model.build(Path(directory))
            with (Path(directory) / "component_estimates.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            selected = [
                r
                for r in rows
                if r["scenario_id"] == "edible_flesh_us_large"
                and r["group"] == "all_all"
                and r["food_group"] in model.ANIMAL
            ]
            self.assertEqual({r["food_group"] for r in selected}, model.ANIMAL)
            self.assertTrue(
                all(
                    r["protein_g_person_day"]
                    and r["quantity_locator"]
                    and r["factor_ids"]
                    for r in selected
                )
            )
            self.assertTrue(all(r["imputation_method"] == "none" for r in selected))

    def test_two_builds_identical(self) -> None:
        """Source-linked CSV and receipt outputs reproduce exactly."""
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            model.build(Path(left))
            model.build(Path(right))
            a = {p.name: p.read_bytes() for p in Path(left).iterdir() if p.is_file()}
            b = {p.name: p.read_bytes() for p in Path(right).iterdir() if p.is_file()}
            self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
