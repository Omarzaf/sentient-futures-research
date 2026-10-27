"""Bind revised prose, evidence links and figures to the preserved research contract."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import unittest
from pathlib import Path

CONTENT = next(
    folder
    for folder in Path(__file__).resolve().parents
    if (folder / "report/chapter.md").exists()
    and (folder / "methods/proxy.md").exists()
)
NUMERICAL = next(
    folder
    for folder in Path(__file__).resolve().parents
    if (folder / "data/altprotein_proxy_inputs.csv").exists()
    and (folder / "build/gfi-gap/diagnostics.json").exists()
)
REFERENCE = NUMERICAL / "data/reference_proxy_scenarios.csv"
if not REFERENCE.exists():
    REFERENCE = NUMERICAL / "data/altprotein_proxy_scenarios.csv"
EQUATIONS_3_4_SHA256 = (
    "36faa47af4e547747414f912e3d9083c26801203eb74d04b7d631aabfc267df3"
)


def csv_rows(file: Path) -> list[dict[str, str]]:
    """Read exported evidence without changing numeric or missing-value strings."""
    with file.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def markdown_table(text: str, first_header: str) -> list[list[str]]:
    """Find an authored table by its first header, preserving displayed cell precision."""
    blocks = re.findall(r"(?:^\|[^\n]*\n?)+", text, flags=re.MULTILINE)
    tables = [
        [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in block.splitlines()
        ]
        for block in blocks
    ]
    found = [table for table in tables if table[0][0] == first_header]
    if len(found) != 1:
        raise AssertionError(
            f"Expected exactly one table starting with {first_header!r}"
        )
    return [found[0][0], *found[0][2:]]


def section(text: str, start: str, end: str) -> str:
    """Select one authored section so unrelated numbers cannot satisfy a claim check."""
    return text.split(start, 1)[1].split(end, 1)[0]


class RevisionContractTests(unittest.TestCase):
    """Check integration semantics rather than repeating the numerical implementation."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load authored content and independently produced data artifacts."""
        cls.chapter = (CONTENT / "report/chapter.md").read_text()
        cls.methods = (CONTENT / "methods/gfi-gap.md").read_text()
        cls.driver_methods = (CONTENT / "methods/drivers.md").read_text()
        cls.evidence = json.loads((CONTENT / "data/driver-evidence.json").read_text())
        cls.recommendations = csv_rows(CONTENT / "data/recommendations.csv")
        cls.diagnostics = json.loads(
            (NUMERICAL / "build/gfi-gap/diagnostics.json").read_text()
        )
        cls.reference = {row["row_id"]: row for row in csv_rows(REFERENCE)}
        cls.targets = {
            row["scenario"]: row for row in cls.diagnostics["target_comparison"]
        }
        cls.sensitivities = {
            (row["case"], row["country"], row["year"]): row
            for row in cls.diagnostics["sensitivities"]
        }

    def test_original_equation_and_aggregation_sections_are_byte_identical(
        self,
    ) -> None:
        """Lock sections 3 and 4 to the independently preserved 22 October bytes."""
        current = (CONTENT / "methods/proxy.md").read_bytes()
        start = current.index(b"## 3. Exact implemented transformations\n")
        end = current.index(b"## 5. Retained sensitivities and external benchmark\n")
        retained = current[start:end]
        self.assertEqual(len(retained), 5800)
        self.assertEqual(hashlib.sha256(retained).hexdigest(), EQUATIONS_3_4_SHA256)

    def test_driver_recommendation_and_source_ids_resolve(self) -> None:
        """Reject orphaned recommendations, duplicate IDs and unsupported source pointers."""
        sources = {row["source_id"]: row for row in self.evidence["sources"]}
        drivers = {row["driver_id"]: row for row in self.evidence["drivers"]}
        recommendations = {
            row["recommendation_id"]: row for row in self.recommendations
        }
        self.assertEqual(len(sources), len(self.evidence["sources"]))
        self.assertEqual(len(drivers), len(self.evidence["drivers"]))
        self.assertEqual(len(recommendations), len(self.recommendations))
        self.assertEqual(set(drivers), {f"D{number:02d}" for number in range(1, 9)})
        self.assertEqual(
            set(recommendations), {f"R{number:02d}" for number in range(1, 8)}
        )
        for source in sources.values():
            self.assertTrue(source["title"].strip())
            self.assertTrue(source["locator"].strip())
            self.assertTrue(source["limit"].strip())
        for driver_id, driver in drivers.items():
            with self.subTest(driver=driver_id):
                self.assertTrue(driver["obstacle_disposition"].strip())
                self.assertTrue(driver["signpost"].strip())
                for country in ("india", "pakistan"):
                    self.assertTrue(driver[country]["source_ids"])
                    self.assertLessEqual(
                        set(driver[country]["source_ids"]), set(sources)
                    )
                for recommendation_id in driver["recommendation_ids"]:
                    self.assertIn(recommendation_id, recommendations)
                    self.assertIn(
                        driver_id,
                        recommendations[recommendation_id]["driver_ids"].split(";"),
                    )
        for recommendation_id, recommendation in recommendations.items():
            with self.subTest(recommendation=recommendation_id):
                driver_ids = set(recommendation["driver_ids"].split(";"))
                evidence_ids = set(recommendation["evidence_ids"].split(";"))
                self.assertTrue(driver_ids)
                self.assertLessEqual(driver_ids, set(drivers))
                self.assertTrue(evidence_ids)
                self.assertLessEqual(evidence_ids, set(sources))
                for driver_id in driver_ids:
                    self.assertIn(
                        recommendation_id, drivers[driver_id]["recommendation_ids"]
                    )
                for field in (
                    "target",
                    "actor",
                    "proposal",
                    "baseline_comparator",
                    "outcome",
                    "horizon",
                    "feasibility_cost_limit",
                    "decision_rule",
                ):
                    self.assertTrue(recommendation[field].strip(), field)

    def test_chapter_driver_and_recommendation_links_match_the_register(self) -> None:
        """Catch prose labels that silently point to a different driver or proposal."""
        drivers = {row["driver_id"] for row in self.evidence["drivers"]}
        proposals = {
            row["recommendation_id"]: set(row["driver_ids"].split(";"))
            for row in self.recommendations
        }
        table = markdown_table(self.chapter, "ID and factor")
        self.assertEqual({row[0].split()[0] for row in table[1:]}, drivers)
        self.assertEqual(set(re.findall(r"\bD\d{2}\b", self.chapter)), drivers)
        self.assertEqual(set(re.findall(r"\bD\d{2}\b", self.driver_methods)), drivers)
        linked = set()
        for label in re.findall(r"^- \*\*(.*?)\*\*", self.chapter, flags=re.MULTILINE):
            recommendation_ids = set(re.findall(r"\bR\d{2}\b", label))
            driver_ids = set(re.findall(r"\bD\d{2}\b", label))
            for recommendation_id in recommendation_ids:
                self.assertIn(recommendation_id, proposals)
                self.assertEqual(driver_ids, proposals[recommendation_id])
                linked.add(recommendation_id)
        self.assertEqual(linked, set(proposals))

    def test_figure_receipt_and_rendered_labels_match_the_source_table(self) -> None:
        """Bind the plotted labels, range and ceiling to the exact CSV revision."""
        file = NUMERICAL / "build/gfi-gap/required-growth.csv"
        rows = csv_rows(file)
        figure = json.loads((CONTENT / "report/figures/figure-data.json").read_text())
        self.assertEqual(
            figure["source_sha256"], hashlib.sha256(file.read_bytes()).hexdigest()
        )
        ceiling = float(self.reference["india_2022_adoption_drift_high"]["value"])
        self.assertEqual(f"{figure['ceiling_percent']:.6f}", f"{ceiling:.6f}")
        self.assertEqual(
            figure["ceiling_percent"], self.diagnostics["model"]["drift_max"] * 100
        )
        self.assertTrue(
            all(
                float(row["current_extra_growth_ceiling_percent"])
                == figure["ceiling_percent"]
                for row in rows
            )
        )
        svg = (CONTENT / "report/figures/gfi-required-growth.svg").read_text()
        rendered_labels = {
            html.unescape(value.strip())
            for value in re.findall(r"<!--(.*?)-->", svg, flags=re.DOTALL)
        }
        self.assertIn(f"{ceiling:.1f}%", rendered_labels)
        self.assertIn("Current ceiling", rendered_labels)
        figure_labels = {row["scenario"]: row for row in figure["labels"]}
        self.assertEqual(set(figure_labels), {"low", "medium", "high"})
        alt_labels = re.findall(
            r"!\[([^\]]*)\]\([^)]*gfi-required-growth\.png\)", self.methods
        )
        self.assertEqual(len(alt_labels), 1)
        self.assertIn(f"{ceiling:.1f}% ceiling", alt_labels[0])
        for scenario, values in figure_labels.items():
            ordered = sorted(
                (row for row in rows if row["scenario"] == scenario),
                key=lambda row: float(row["elasticity"]),
            )
            required = [float(row["required_extra_growth_percent"]) for row in ordered]
            self.assertEqual(values["low"], min(required))
            self.assertEqual(values["high"], max(required))
            self.assertEqual(values["midpoint"], required[len(required) // 2])
            label = f"{min(required):.1f}-{max(required):.1f}%"
            self.assertIn(label, rendered_labels)
            self.assertIn(f"GFI {scenario}", rendered_labels)
            self.assertIn(label, alt_labels[0])

    def test_chapter_gfi_table_matches_diagnostic_values_at_display_precision(
        self,
    ) -> None:
        """Check year, original rupee totals, multiples and required-growth ranges together."""
        table = markdown_table(self.chapter, "GFI domestic scenario")
        self.assertIn("2030", table[0][1])
        self.assertIn("INR crore", table[0][1])
        self.assertEqual(len(table[1:]), 3)
        for row in table[1:]:
            target = self.targets[row[0].lower()]
            self.assertEqual(row[1], f"{target['source_target_crore']:,.0f}")
            self.assertEqual(row[2], f"{target['source_value_multiple']:.2f}x")
            self.assertEqual(
                row[3].replace("–", "-"),
                f"{target['required_growth_min_percent']:.1f}-{target['required_growth_max_percent']:.1f}%",
            )

    def test_chapter_gfi_prose_numbers_match_their_declared_cases(self) -> None:
        """Prevent baseline, zero-floor, maximum and target amounts from being swapped."""
        text = section(
            self.chapter,
            "## Why the scenarios sit below GFI India",
            "## US benchmark and the separate elicitation",
        )
        first_paragraph = text.strip().split("\n\n", 1)[0]
        amounts = re.findall(r"\$([\d,.]+) million", first_paragraph)
        baseline = self.sensitivities[("baseline", "India", 2030)][
            "p50_million_usd_2025_prices"
        ]
        zero = self.sensitivities[("drift_floor_zero", "India", 2030)][
            "p50_million_usd_2025_prices"
        ]
        expected = [
            baseline,
            zero,
            self.diagnostics["maxima"]["analytic_max_million_usd"],
            self.targets["low"]["conditional_target_million_usd"],
        ]
        self.assertEqual(amounts, [f"{value:.1f}" for value in expected])
        ceiling_match = re.search(
            r"upper additional-growth assumption is ([\d.]+)%", text
        )
        self.assertIsNotNone(ceiling_match)
        self.assertEqual(
            ceiling_match.group(1),
            f"{self.diagnostics['model']['drift_max'] * 100:.1f}",
        )

    def test_methods_category_table_matches_extraction_and_growth_artifact(
        self,
    ) -> None:
        """Check displayed category figures without recalculating their growth formula."""
        table = markdown_table(self.methods, "Category")
        growth = {
            (row["category"], row["scenario"]): row
            for row in self.diagnostics["category_growth"]
        }
        self.assertEqual(len(table[1:]), 5)
        for row in table[1:]:
            first = growth[(row[0], "low")]
            if first["base_crore"] is None:
                self.assertEqual(row[1], "Source dash; undefined")
            else:
                self.assertEqual(row[1], f"{first['base_crore']:.0f}")
            for cell, scenario in zip(row[2:], ("low", "medium", "high"), strict=True):
                record = growth[(row[0], scenario)]
                rate = record["source_value_cagr_percent"]
                display = "N/A" if rate is None else f"{rate:.2f}%"
                self.assertEqual(cell, f"{record['target_crore']:,.0f} ({display})")
        low = self.targets["low"]
        share = re.search(r"\*\*([\d.]+)% of GFI's low-case total\*\*", self.methods)
        gap = re.search(r"our median by \*\*([\d.]+)%\*\*", self.methods)
        self.assertIsNotNone(share)
        self.assertIsNotNone(gap)
        self.assertEqual(
            share.group(1), f"{low['fermentation_share_of_target_percent']:.3f}"
        )
        self.assertEqual(
            gap.group(1),
            f"{low['gap_reduction_if_fermentation_subtracted_percent']:.3f}",
        )

    def test_methods_factor_table_keeps_midpoint_and_median_distinct(self) -> None:
        """Bind the illustrative factors and their product to the declared midpoint case."""
        rows = markdown_table(self.methods, "Factor, 2022 to 2030")[1:]
        factors = self.diagnostics["midpoint_parameter_illustration"]
        mapping = {
            "Population": "population_factor",
            "Real income raised to elasticity": "income_factor",
            "Urban share": "urban_factor",
            "Additional growth": "extra_growth_factor",
            "Product": "total_multiple",
        }
        for row in rows:
            if row[0] in mapping:
                self.assertEqual(row[1], f"{factors[mapping[row[0]]]:.6f}")
        product = next(row for row in rows if row[0] == "Product")
        amounts = re.findall(r"\$([\d.]+)m", product[2])
        self.assertEqual(
            amounts,
            [
                f"{self.diagnostics['model']['anchor_million_usd_2025_prices']:.6f}",
                f"{factors['india_2030_million_usd_2025_prices']:.6f}",
            ],
        )
        median = self.sensitivities[("baseline", "India", 2030)][
            "p50_million_usd_2025_prices"
        ]
        self.assertIn(
            f"retained simulated median is ${median:.6f} million", self.methods
        )
        gfi_multiples = next(
            row[1] for row in rows if row[0] == "GFI reported low/medium/high multiples"
        )
        self.assertEqual(
            gfi_multiples,
            " / ".join(
                f"{self.targets[scenario]['source_value_multiple']:.3f}"
                for scenario in ("low", "medium", "high")
            ),
        )
        bounds = re.search(
            r"fastest sampled draw grows by ([\d.]+)% annually\..*?analytical maximum of ([\d.]+)%, or \$([\d.]+) million",
            self.methods,
        )
        self.assertIsNotNone(bounds)
        maximum = self.diagnostics["maxima"]
        self.assertEqual(
            bounds.groups(),
            tuple(
                f"{maximum[key]:.6f}"
                for key in (
                    "sampled_max_cagr_percent",
                    "analytic_max_cagr_percent",
                    "analytic_max_million_usd",
                )
            ),
        )

    def test_methods_required_growth_and_us_cases_match_their_tables(self) -> None:
        """Verify displayed inverse diagnostics and separate US sensitivities by named case."""
        table = markdown_table(self.methods, "Target")
        for row in table[1:]:
            target = self.targets[row[0].lower()]
            self.assertEqual(
                row[1],
                f"{target['required_growth_at_midpoint_elasticity_percent']:.2f}% per year",
            )
            self.assertEqual(
                row[2].replace("–", "-"),
                f"{target['required_growth_min_percent']:.2f}-{target['required_growth_max_percent']:.2f}%",
            )
        labels = {
            "Retained baseline": "baseline",
            "Extra-growth floor 0% instead of -2%": "drift_floor_zero",
            "Elasticity fixed at 1": "elasticity_grid_00",
            "Both changes": "combined_zero_floor_elasticity_1",
        }
        cases = markdown_table(self.methods, "Case")
        self.assertEqual({row[0] for row in cases[1:]}, set(labels))
        for row in cases[1:]:
            for country, cell in zip(("India", "Pakistan"), row[1:], strict=True):
                expected = self.sensitivities[(labels[row[0]], country, 2030)][
                    "p50_million_usd_2025_prices"
                ]
                self.assertEqual(cell, f"{expected:.3f}")
        change = self.sensitivities[("drift_floor_zero", "India", 2030)][
            "median_change_percent_from_baseline"
        ]
        self.assertIn(f"raises India's median by {change:.3f}%", self.methods)

    def test_headline_country_table_remains_the_retained_reference(self) -> None:
        """Check every displayed headline amount rather than only file identity."""
        table = markdown_table(self.chapter, "Country")
        self.assertEqual(len(table[1:]), 6)
        for country, year, *cells in table[1:]:
            for quantile, cell in zip(("p10", "p50", "p90"), cells, strict=True):
                value = float(
                    self.reference[f"{country.lower()}_{year}_market_value_{quantile}"][
                        "value"
                    ]
                )
                display = f"{value:,.0f}" if country == "India" else f"{value:.1f}"
                self.assertEqual(cell, display)

    def test_us_benchmark_prose_uses_fixed_year_and_per_person_denominator(
        self,
    ) -> None:
        """Reject changed denominator, comparator year or rounding in US-facing claims."""
        text = section(
            self.chapter,
            "## US benchmark and the separate elicitation",
            "## What follows from the evidence",
        )
        per_person = re.search(
            r"about \$([\d.]+) per person in India and \$([\d.]+) in Pakistan", text
        )
        shares = re.search(
            r"roughly ([\d.]+)% and ([\d.]+)% of the fixed US (\d{4})", text
        )
        self.assertIsNotNone(per_person)
        self.assertIsNotNone(shares)
        self.assertEqual(shares.group(3), "2025")
        india = float(self.reference["india_2035_per_capita_value_p50"]["value"])
        pakistan = float(self.reference["pakistan_2035_per_capita_value_p50"]["value"])
        self.assertEqual(per_person.groups(), (f"{india:.2f}", f"{pakistan:.3f}"))
        expected_shares = tuple(
            f"{float(self.reference[f'{country}_2035_per_capita_share_of_us_2025_p50']['value']):.2f}"
            for country in ("india", "pakistan")
        )
        self.assertEqual(shares.groups()[:2], expected_shares)
        self.assertIn("per-person comparisons", text)


if __name__ == "__main__":
    unittest.main()
