"""Independently check unit algebra, source zeros, scenario scope and failure gates."""

from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import compile_spec as spec


class CalibrationSpecTests(unittest.TestCase):
    """Exercise scientific dimensional failures rather than household estimates."""

    @classmethod
    def setUpClass(cls) -> None:
        """Build from frozen sources and retain only small factor/code tables."""
        cls.original = spec.HERE
        cls.before = {
            p.name: p.read_bytes() for p in cls.original.iterdir() if p.is_file()
        }
        temporary = tempfile.TemporaryDirectory(prefix="calibration-spec-test-")
        cls.addClassCleanup(temporary.cleanup)
        root = Path(temporary.name)
        here = root / "scripts/diet/m3_calibration_spec"
        here.parent.mkdir(parents=True)
        shutil.copytree(cls.original, here)
        (root / "data").symlink_to(spec.ROOT / "data", target_is_directory=True)
        core = root / "scripts/diet/m3_food_crosswalk"
        core.symlink_to(spec.CORE, target_is_directory=True)
        usda = root / "scripts/diet/m3_usda_supplement"
        usda.symlink_to(spec.USDA, target_is_directory=True)
        regional = core / "supplement_regional_20261013"
        isolated = patch.multiple(
            spec,
            ROOT=root,
            HERE=here,
            CORE=core,
            REGIONAL=regional,
            USDA=usda,
            FROZEN=[core / "handoff_hashes.json", regional / "handoff_hashes.json"],
        )
        isolated.start()
        cls.addClassCleanup(isolated.stop)
        cls.receipt = spec.build()
        cls.catalog = spec.load_catalog()
        cls.items = {
            r["itc"]: r
            for r in spec.read_rows(spec.CORE / "questionnaire_inventory.csv")
        }
        cls.recipes = {
            r["recipe_id"]: r for r in spec.read_rows(spec.HERE / "recipes.psv", "|")
        }
        cls.rows = {
            (r["scenario"], r["itc"]): r
            for r in spec.read_rows(spec.HERE / "compiled_factors.csv")
        }

    def exact(self, code: str, scenario: str = "baseline") -> Fraction:
        """Read the authoritative exact compiled rational, not rounded display text."""
        row = self.rows[(scenario, code)]
        return Fraction(
            int(row["protein_factor_numerator"]), int(row["protein_factor_denominator"])
        )

    def test_native_mass_units_without_time_conversion(self) -> None:
        """A kilogram of Atta yields100g protein while a gram of honey yields0.003g."""
        self.assertEqual(self.exact("11102"), Fraction(100))
        self.assertEqual(self.exact("11803"), Fraction(3, 1000))
        self.assertEqual(self.rows[("baseline", "11102")]["period_days"], "30")

    def test_component_product_precedes_average(self) -> None:
        """Cabbage/cauliflower must use paired source factors, not separate means."""
        self.assertEqual(self.exact("11704"), Fraction(213, 20))
        self.assertNotEqual(self.exact("11704"), Fraction(4389, 400))
        self.assertEqual(self.exact("11608"), Fraction(471, 100))

    def test_liquid_milk_density_and_species_variant(self) -> None:
        """Milk uses1031g/L baseline; species conversion changes only paired densities."""
        self.assertEqual(self.exact("11401"), Fraction(14434, 375))
        self.assertEqual(
            self.exact("11401", "milk_species_density"), Fraction(7829, 200)
        )
        self.assertEqual(self.exact("11401"), self.exact("11403"))

    def test_oil_sesame_is_not_erased(self) -> None:
        """Seven source-zero oils plus sesame0.2 at equal weights and920g/L yield0.23."""
        self.assertEqual(self.exact("11504"), Fraction(23, 100))
        self.assertEqual(self.rows[("baseline", "11504")]["known_zero"], "false")
        self.assertIn(
            "protein:pk:184", self.rows[("baseline", "11504")]["source_factor_refs"]
        )

    def test_tea_transfer_applies_once(self) -> None:
        """Source22.4/26.3 mean receives the published0.05 infusion transfer once."""
        self.assertEqual(self.exact("12101"), Fraction(487, 40000))
        self.assertNotEqual(self.exact("12101"), Fraction(487, 2000))

    def test_corrected_milk_powder_column(self) -> None:
        """The whole-powder protein25.2 is distinct from adjacent lipid25.1."""
        self.assertEqual(self.exact("11406"), Fraction(77, 250))
        self.assertEqual(self.catalog["protein:pk:138"]["value"], "25.2")

    def test_known_zero_cost_scope_and_prepared_boundary(self) -> None:
        """Known-zero at-home food remains eligible for calibration spending."""
        for code in ["11503", "11505", "11801", "11901", "11902", "12205"]:
            row = self.rows[("baseline", code)]
            self.assertEqual(self.exact(code), 0)
            self.assertEqual(row["role"], "G")
            self.assertEqual(row["calibration_value_eligible"], "true")
            self.assertEqual(row["quantity_required_for_G"], "false")
        prepared = self.rows[("baseline", "110018")]
        self.assertEqual(prepared["role"], "DIRECT_ZERO_OUTSIDE_G")
        self.assertEqual(prepared["calibration_value_eligible"], "false")
        self.assertEqual(prepared["section_group"], "PREPARED_30_DAY")

    def test_egg_portion_is_edible_and_sensitivity_only(self) -> None:
        """US50g already edible portion gives6.1g without a second shell correction."""
        self.assertEqual(self.rows[("baseline", "11409")]["role"], "K")
        self.assertEqual(self.exact("11409", "egg_US_large_50g"), Fraction(61, 10))
        self.assertEqual(self.exact("11409", "egg_US_small_38g"), Fraction(1159, 250))
        self.assertEqual(self.exact("11409", "egg_US_jumbo_63g"), Fraction(3843, 500))
        self.assertNotEqual(
            self.exact("11409", "egg_US_large_50g"),
            Fraction(61, 10) * Fraction(87, 100),
        )

    def test_full_code_scope_unknowns_and_yogurt_hold(self) -> None:
        """Each scenario preserves every food/service code and explicit unresolved factors."""
        for scenario in self.receipt["scenarios"]:
            rows = [r for (name, _), r in self.rows.items() if name == scenario]
            self.assertEqual(len(rows), 120)
            self.assertEqual({r["itc"] for r in rows}, set(self.items))
            for row in rows:
                if row["role"] in {"K", "SERVICE"}:
                    self.assertEqual(row["protein_g_per_native_unit"], "")
                    self.assertEqual(row["known_zero"], "false")
        self.assertEqual(self.rows[("baseline", "11408")]["role"], "K")
        self.assertEqual(self.exact("11408", "yogurt_included_held"), 32)
        self.assertIn(
            "MISMATCH_UNRESOLVED",
            self.rows[("yogurt_included_held", "11408")]["data_gate"],
        )
        self.assertEqual(self.rows[("baseline", "11108")]["role"], "SERVICE")

    def test_narrow_pool_retains_source_zero_accounting(self) -> None:
        """Pool changes are method diagnostics and cannot turn accepted zeros into K."""
        for scenario in ["exact_food_forms", "domestic_single_positive"]:
            self.assertEqual(self.rows[(scenario, "11504")]["role"], "K")
            self.assertEqual(self.rows[(scenario, "11505")]["role"], "G")
            self.assertEqual(self.rows[(scenario, "11901")]["role"], "G")
        domestic_positive = [
            r
            for (scenario, _), r in self.rows.items()
            if scenario == "domestic_single_positive"
            and r["role"] == "G"
            and r["known_zero"] == "false"
        ]
        self.assertEqual({r["itc"] for r in domestic_positive}, {"11102", "11803"})
        for row in domestic_positive:
            self.assertNotIn("edible:bd:", row["source_factor_refs"])

    def test_reject_unsupported_conversions_and_weights(self) -> None:
        """Neither specific gravity nor invented local shares can enter compilation."""
        bad = dict(self.recipes["cooking_oils"], density_refs="sesame_specific_gravity")
        with self.assertRaises(AssertionError):
            spec.compile_recipe(bad, self.items["11504"], self.catalog)
        bad = dict(self.recipes["atta"], weight_rule="inferred_Pakistan_share")
        with self.assertRaises(AssertionError):
            spec.compile_recipe(bad, self.items["11102"], self.catalog)
        bad = dict(self.recipes["atta"], edible_refs="zero_shortcut")
        with self.assertRaises(AssertionError):
            spec.compile_recipe(bad, self.items["11102"], self.catalog)
        bad_item = dict(self.items["11102"], native_unit="unspecified")
        with self.assertRaises(AssertionError):
            spec.compile_recipe(self.recipes["atta"], bad_item, self.catalog)

    def test_reject_wrong_nutrient_unit_and_duplicate_component(self) -> None:
        """Catch1000-fold nutrient-unit drift and duplicated source-food weights."""
        bad_catalog = copy.deepcopy(self.catalog)
        bad_catalog["protein:pk:15"]["unit"] = "mg/100g edible"
        with self.assertRaises(AssertionError):
            spec.compile_recipe(self.recipes["atta"], self.items["11102"], bad_catalog)
        bad = dict(self.recipes["atta"], protein_refs="pk:15;pk:15")
        with self.assertRaises(AssertionError):
            spec.compile_recipe(bad, self.items["11102"], self.catalog)

    def test_frozen_folder_never_written(self) -> None:
        """The compiler may regenerate only the isolated scratch output folder."""
        self.assertEqual(
            self.before,
            {p.name: p.read_bytes() for p in self.original.iterdir() if p.is_file()},
        )
        self.assertNotEqual(spec.HERE, self.original)

    def test_deterministic_rebuild(self) -> None:
        """Repeating the compiler preserves all output bytes and input bindings."""
        before = (spec.HERE / "receipt.json").read_bytes()
        repeated = spec.build()
        self.assertEqual(self.receipt, repeated)
        self.assertEqual(before, (spec.HERE / "receipt.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
