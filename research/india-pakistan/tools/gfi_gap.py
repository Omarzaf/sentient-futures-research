"""Explain the conditional GFI difference without changing the retained model.

This standard-library companion independently implements the documented equations,
checks agreement with retained summaries, and writes separate diagnostic outputs.
It neither acquires evidence nor estimates new empirical model parameters.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "Draw",
    "Model",
    "Sensitivity",
    "annual_growth",
    "build_diagnostics",
    "category_diagnostics",
    "factor_product",
    "load_categories",
    "main",
    "quantile",
    "required_growth",
    "write_outputs",
]

SEED = 20261015
DRAWS = 10000
OUTPUT_SIGNIFICANT_DIGITS = 12
YEARS = (2026, 2030, 2035)
COUNTRIES = ("India", "Pakistan")
ROOT = Path(__file__).resolve().parents[1]
Scalar = str | int | float | bool | None
Row = dict[str, Scalar]
PRICE_QUALIFICATION = (
    "Conditional retained conversion: the GFI source price and retail valuation "
    "bases are unstated; treat both its anchor and targets as 2022 rupees, "
    "inflate to 2025 and convert at the retained 2025 market exchange rate."
)


def sha256(file: Path) -> str:
    """Return a file checksum without changing its contents."""
    return hashlib.sha256(file.read_bytes()).hexdigest()


def read_rows(file: Path) -> list[dict[str, str]]:
    """Read source values as strings, preserving blank cells."""
    with file.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def quantile(values: list[float], fraction: float) -> float:
    """Interpolate order statistics using the retained quantile convention."""
    if not values or not 0 <= fraction <= 1:
        raise ValueError("Quantile needs values and a fraction in [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low, high = math.floor(position), math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def annual_growth(base: float | None, target: float, years: int) -> float | None:
    """Return fractional CAGR, leaving missing or zero baselines undefined."""
    if years <= 0 or not math.isfinite(target) or target < 0:
        raise ValueError("CAGR requires positive years and a finite nonnegative target")
    if base is None or base == 0:
        return None
    if not math.isfinite(base) or base < 0:
        raise ValueError("CAGR baseline must be finite and nonnegative")
    return (target / base) ** (1 / years) - 1


def required_growth(target: float, no_drift_value: float, years: int) -> float:
    """Solve for the constant extra growth needed to hit a conditional target."""
    if years <= 0 or any(
        not math.isfinite(value) or value <= 0 for value in (target, no_drift_value)
    ):
        raise ValueError("Growth inversion requires positive finite values and years")
    return (target / no_drift_value) ** (1 / years) - 1


def factor_product(
    population: float, income: float, urban: float, extra: float
) -> float:
    """Multiply the four mechanical factors without claiming causal attribution."""
    return population * income * urban * extra


@dataclass(frozen=True)
class Sensitivity:
    """Specify one declared diagnostic while retaining the baseline random stream."""

    name: str
    drift_floor: float | None = None
    drift_ceiling: float | None = None
    elasticity: float | None = None
    drift: float | None = None
    animal_weight: float | None = None
    industry: float | None = None
    omit_pakistan_overlap: bool = False


@dataclass(frozen=True)
class Draw:
    """Retain the four sampled parameters and their stable paired draw ID."""

    draw_id: int
    elasticity: float
    drift: float
    animal_weight: float
    industry: float


class Model:
    """Evaluate the documented equations independently of the frozen engine."""

    def __init__(self, file: Path):
        """Validate retained inputs and precompute deterministic country paths."""
        rows = read_rows(file)
        self.input_rows = len(rows)
        self.values = {row["input_id"]: float(row["value"]) for row in rows}
        if len(self.values) != len(rows) or any(
            not math.isfinite(value) for value in self.values.values()
        ):
            raise ValueError("Proxy inputs contain duplicate IDs or nonfinite values")
        self.populations = {
            (iso, year): self._population(iso, year)
            for iso in ("ind", "pak")
            for year in range(2022, 2036)
        }
        self.incomes = {
            (iso, year): self._income(iso, year)
            for iso in ("ind", "pak")
            for year in range(2022, 2036)
        }
        self.urban_shares = {
            (iso, year): self._urban(iso, year)
            for iso in ("ind", "pak")
            for year in range(2022, 2036)
        }
        self.cpi = math.prod(
            1 + self.get(f"imf_pcpipch_ind_{year}") / 100 for year in range(2023, 2026)
        )
        self.fx = self.get("wdi_exchange_rate_ind_2025")
        self.anchor = self.convert_crore(self.get("gfi_india_domestic_2022_central"))
        self.india_per_person = self.anchor / self.populations[("ind", 2022)]
        self.us_per_person = (
            self.get("gfi_us_retail_sales_2025") * 1000 / self.get("imf_lp_usa_2025")
        )
        income_ratio = self.get("wdi_gdp_per_capita_usd_usa_2025") / (
            self.get("wdi_gdp_per_capita_lcu_ind_2022") * self.cpi / self.fx
        )
        self.elasticity_max = math.log(
            self.us_per_person / self.india_per_person
        ) / math.log(income_ratio)
        self.drift_min = self.get("gfi_us_retail_dollar_change_2025") / 100
        self.drift_max = (
            self.get("jobs_vacancies_india_2025")
            / self.get("jobs_vacancies_india_2023")
        ) ** 0.5 - 1
        income_growth = (
            self.incomes[("ind", 2025)] / self.incomes[("ind", 2023)]
        ) ** 0.5 - 1
        self.overlap_drift_max = self.drift_max - income_growth * self.elasticity_max
        animal = {
            country: sum(
                float(row["value"])
                for row in rows
                if row["country"] == country
                and row["quantity"] == "animal_protein_supply_item"
            )
            for country in COUNTRIES
        }
        self.animal_ratio = animal["Pakistan"] / animal["India"]
        self.industry_min = (
            self.get("jobs_directory_rows_pakistan") / self.populations[("pak", 2025)]
        ) / (self.get("jobs_directory_rows_india") / self.populations[("ind", 2025)])
        self.industry_max = (
            self.get("jobs_vacancies_pakistan_2025") / self.populations[("pak", 2025)]
        ) / (self.get("jobs_vacancies_india_2025") / self.populations[("ind", 2025)])
        self.pakistan_income_ratio = self.get(
            "wdi_gdp_per_capita_usd_pak_2025"
        ) / self.get("wdi_gdp_per_capita_usd_ind_2025")

    def get(self, key: str) -> float:
        """Read an exact retained numeric input by ID."""
        return self.values[key]

    def _population(self, iso: str, year: int) -> float:
        """Retain the documented post-2031 constant population-growth extension."""
        if year <= 2031:
            return self.get(f"imf_lp_{iso}_{year}")
        last = self.get(f"imf_lp_{iso}_2031")
        return last * (last / self.get(f"imf_lp_{iso}_2030")) ** (year - 2031)

    def _income(self, iso: str, year: int) -> float:
        """Build real GDP per person relative to 2022, in original operation order."""
        result = 1.0
        for current in range(2023, year + 1):
            growth = self.get(f"imf_ngdp_rpch_{iso}_{min(current, 2031)}") / 100
            ratio = (
                self.populations[(iso, current)] / self.populations[(iso, current - 1)]
            )
            result *= (1 + growth) / ratio
        return result

    def _urban(self, iso: str, year: int) -> float:
        """Use observed shares through 2025 and the retained OLS trend thereafter."""
        points = [
            (y, self.get(f"wdi_urban_share_{iso}_{y}")) for y in range(2015, 2026)
        ]
        if year <= 2025:
            return dict(points)[year]
        mean_x = sum(x for x, _ in points) / len(points)
        mean_y = sum(y for _, y in points) / len(points)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sum(
            (x - mean_x) ** 2 for x, _ in points
        )
        return dict(points)[2025] + slope * (year - 2025)

    def convert_crore(self, value: float) -> float:
        """Apply the retained, explicitly conditional source-price conversion."""
        return value * 1e7 * self.cpi / self.fx / 1e6

    def draws(self, case: Sensitivity, count: int = DRAWS) -> list[Draw]:
        """Draw e, d, animal weight and industry in frozen order before overrides."""
        rng = random.Random(SEED)
        lower = self.drift_min if case.drift_floor is None else case.drift_floor
        upper = self.drift_max if case.drift_ceiling is None else case.drift_ceiling
        if not -1 < lower <= upper or count <= 0:
            raise ValueError("Invalid drift support or draw count")
        result = []
        for draw_id in range(1, count + 1):
            elasticity = rng.uniform(1, self.elasticity_max)
            drift = rng.uniform(lower, upper)
            animal = rng.uniform(0, 1)
            industry = rng.uniform(self.industry_min, self.industry_max)
            result.append(
                Draw(
                    draw_id,
                    elasticity if case.elasticity is None else case.elasticity,
                    drift if case.drift is None else case.drift,
                    animal if case.animal_weight is None else case.animal_weight,
                    industry if case.industry is None else case.industry,
                )
            )
        return result

    def per_person(
        self, country: str, year: int, draw: Draw, omit_overlap: bool = False
    ) -> float:
        """Evaluate a draw with original operation order and shared parameters."""
        india = (
            self.india_per_person
            * self.incomes[("ind", year)] ** draw.elasticity
            * self.urban_shares[("ind", year)]
            / self.urban_shares[("ind", 2022)]
            * (1 + draw.drift) ** (year - 2022)
        )
        if country == "India":
            return india
        if country != "Pakistan":
            raise ValueError(
                "Only the retained India and Pakistan outcomes are supported"
            )
        relative_income = (
            self.pakistan_income_ratio
            * (self.incomes[("pak", year)] / self.incomes[("pak", 2025)])
            / (self.incomes[("ind", year)] / self.incomes[("ind", 2025)])
        )
        return (
            india
            * relative_income**draw.elasticity
            * (1 if omit_overlap else self.urban_shares[("pak", year)])
            / (1 if omit_overlap else self.urban_shares[("ind", year)])
            * (1 if omit_overlap else self.animal_ratio**draw.animal_weight)
            * draw.industry
        )

    def total(
        self, country: str, year: int, draw: Draw, omit_overlap: bool = False
    ) -> float:
        """Convert per-person values to million dollars using million-person inputs."""
        iso = "ind" if country == "India" else "pak"
        return (
            self.per_person(country, year, draw, omit_overlap)
            * self.populations[(iso, year)]
        )

    def factor_row(self, draw: Draw) -> Row:
        """Expose exact 2022-to-2030 mechanical factors for a single paired draw."""
        factors = (
            self.populations[("ind", 2030)] / self.populations[("ind", 2022)],
            self.incomes[("ind", 2030)] ** draw.elasticity,
            self.urban_shares[("ind", 2030)] / self.urban_shares[("ind", 2022)],
            (1 + draw.drift) ** 8,
        )
        return {
            "draw_id": draw.draw_id,
            "elasticity": draw.elasticity,
            "extra_growth_fraction": draw.drift,
            "animal_weight": draw.animal_weight,
            "industry_factor": draw.industry,
            "population_factor": factors[0],
            "income_factor": factors[1],
            "urban_factor": factors[2],
            "extra_growth_factor": factors[3],
            "total_multiple": factor_product(*factors),
            "india_2030_million_usd_2025_prices": self.total("India", 2030, draw),
            "log_population": math.log(factors[0]),
            "log_income": math.log(factors[1]),
            "log_urban": math.log(factors[2]),
            "log_extra_growth": math.log(factors[3]),
        }


def load_categories(file: Path) -> list[dict[str, str]]:
    """Validate the complete source grid without converting source dashes to zero."""
    rows = read_rows(file)
    expected = {
        (category, year, scenario)
        for category in ("meat", "dairy", "eggs", "fermentation", "overall")
        for year, scenario in (
            ("2022", "baseline"),
            ("2030", "low"),
            ("2030", "medium"),
            ("2030", "high"),
        )
    }
    keys = [(r["category_id"], r["year"], r["scenario"]) for r in rows]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("GFI category extraction is incomplete or has duplicate cells")
    for row in rows:
        missing = row["category_id"] == "fermentation" and row["year"] == "2022"
        if missing:
            if row["source_display"] != "-" or row["value_crore"] != "":
                raise ValueError(
                    "The fermentation source dash must retain a missing numeric value"
                )
        elif (
            not row["value_crore"]
            or not math.isfinite(float(row["value_crore"]))
            or float(row["value_crore"]) < 0
        ):
            raise ValueError("GFI numeric source cells must be finite and nonnegative")
        elif float(row["source_display"].replace(",", "")) != float(row["value_crore"]):
            raise ValueError(
                "Numeric extraction disagrees with the preserved source display"
            )
        if row["unit"] != "INR crore" or row["physical_pdf_page"] != "4":
            raise ValueError("GFI category unit/page does not match the source table")
    return rows


def category_diagnostics(rows: list[dict[str, str]]) -> tuple[list[Row], list[Row]]:
    """Calculate source-value growth and report, rather than repair, sum differences."""
    cells = {(r["category_id"], r["scenario"]): r for r in rows}
    growth, sums = [], []
    for category in ("meat", "dairy", "eggs", "fermentation", "overall"):
        baseline = cells[(category, "baseline")]
        base = float(baseline["value_crore"]) if baseline["value_crore"] else None
        for scenario in ("low", "medium", "high"):
            target_row = cells[(category, scenario)]
            target = float(target_row["value_crore"])
            rate = annual_growth(base, target, 8)
            growth.append(
                {
                    "category_id": category,
                    "category": baseline["category"],
                    "scenario": scenario,
                    "base_year": 2022,
                    "target_year": 2030,
                    "base_source_display": baseline["source_display"],
                    "base_crore": base,
                    "target_crore": target,
                    "absolute_increase_crore": None if base is None else target - base,
                    "source_value_cagr_percent": None if rate is None else rate * 100,
                    "cagr_status": (
                        "undefined_source_baseline_missing"
                        if rate is None
                        else "defined_price_interpretation_unresolved"
                    ),
                    "physical_pdf_page": 4,
                }
            )
    for scenario in ("baseline", "low", "medium", "high"):
        category_cells = [
            cells[(c, scenario)] for c in ("meat", "dairy", "eggs", "fermentation")
        ]
        known_sum = sum(
            float(r["value_crore"]) for r in category_cells if r["value_crore"]
        )
        missing = sum(not r["value_crore"] for r in category_cells)
        overall = float(cells[("overall", scenario)]["value_crore"])
        sums.append(
            {
                "scenario": scenario,
                "known_category_sum_crore": known_sum,
                "reported_total_crore": overall,
                "unresolved_cells": missing,
                "reported_minus_known_sum_crore": overall - known_sum,
                "status": (
                    "unresolved_source_dash"
                    if missing
                    else (
                        "exact_agreement"
                        if known_sum == overall
                        else "source_discrepancy_preserved"
                    )
                ),
            }
        )
    return growth, sums


def sensitivity_cases(model: Model) -> list[Sensitivity]:
    """Declare bounded diagnostics, including retained controls and a five-point grid."""
    cases = [Sensitivity("baseline"), Sensitivity("drift_floor_zero", drift_floor=0)]
    cases.extend(
        Sensitivity(
            f"elasticity_grid_{index:02d}",
            elasticity=1 + index / 4 * (model.elasticity_max - 1),
        )
        for index in range(5)
    )
    cases.extend(
        [
            Sensitivity(
                "combined_zero_floor_elasticity_1", drift_floor=0, elasticity=1
            ),
            Sensitivity("income_drift_overlap", drift_ceiling=model.overlap_drift_max),
            Sensitivity("pakistan_no_urban_animal", omit_pakistan_overlap=True),
            Sensitivity("pakistan_industry_low", industry=model.industry_min),
            Sensitivity("pakistan_industry_high", industry=model.industry_max),
            Sensitivity("drift_fixed_low", drift=model.drift_min),
            Sensitivity("drift_fixed_high", drift=model.drift_max),
            Sensitivity("animal_weight_low", animal_weight=0),
            Sensitivity("animal_weight_high", animal_weight=1),
        ]
    )
    return cases


def reference_check(
    actual: float, row_id: str, reference: dict[str, dict[str, str]]
) -> Row:
    """Require equality at the reference's six-decimal output precision."""
    expected = reference[row_id]["value"]
    if f"{actual:.6f}" != expected:
        raise ValueError(f"Companion/reference parity failed: {row_id}")
    return {
        "row_id": row_id,
        "reference_value": expected,
        "actual_value": actual,
        "absolute_error": abs(actual - float(expected)),
    }


def build_diagnostics(
    inputs: Path, reference_file: Path, categories: Path
) -> dict[str, object]:
    """Compute independent supplementary results and preserve immutable source bytes."""
    protected = {
        "proxy_inputs": inputs,
        "proxy_reference": reference_file,
        "gfi_categories": categories,
    }
    before = {name: sha256(file) for name, file in protected.items()}
    model = Model(inputs)
    references = read_rows(reference_file)
    reference = {r["row_id"]: r for r in references}
    if model.input_rows != 106 or len(references) != 127 or len(reference) != 127:
        raise ValueError(
            "The retained contract requires 106 inputs and 127 unique reference rows"
        )
    category_rows = load_categories(categories)
    growth, sums = category_diagnostics(category_rows)
    cells = {(r["category_id"], r["scenario"]): r for r in category_rows}
    if float(cells[("overall", "baseline")]["value_crore"]) != model.get(
        "gfi_india_domestic_2022_central"
    ):
        raise ValueError("GFI category extraction disagrees with the retained anchor")
    baseline_draws = model.draws(Sensitivity("baseline"))
    factor_rows = [model.factor_row(draw) for draw in baseline_draws]
    midpoint = Draw(
        0,
        (1 + model.elasticity_max) / 2,
        (model.drift_min + model.drift_max) / 2,
        0.5,
        (model.industry_min + model.industry_max) / 2,
    )
    summaries, checks = [], []
    lookup: dict[tuple[str, str, int], Row] = {}
    fixed_refs = {
        "elasticity_grid_00": "elasticity_fixed_low",
        "elasticity_grid_04": "elasticity_fixed_high",
        "pakistan_industry_low": "ecosystem_fixed_low",
        "pakistan_industry_high": "ecosystem_fixed_high",
        "drift_fixed_low": "drift_fixed_low",
        "drift_fixed_high": "drift_fixed_high",
        "animal_weight_low": "weight_fixed_low",
        "animal_weight_high": "weight_fixed_high",
    }
    for case in sensitivity_cases(model):
        draws = model.draws(case)
        for country in COUNTRIES:
            iso = "ind" if country == "India" else "pak"
            for year in YEARS:
                per_person = [
                    model.per_person(country, year, draw, case.omit_pakistan_overlap)
                    for draw in draws
                ]
                values = {
                    label: quantile(per_person, fraction)
                    * model.populations[(iso, year)]
                    for label, fraction in (("p10", 0.1), ("p50", 0.5), ("p90", 0.9))
                }
                row: Row = {
                    "case": case.name,
                    "country": country,
                    "year": year,
                    "fixed_elasticity": case.elasticity,
                    "drift_lower_fraction": (
                        model.drift_min
                        if case.drift_floor is None
                        else case.drift_floor
                    ),
                    "drift_upper_fraction": (
                        model.drift_max
                        if case.drift_ceiling is None
                        else case.drift_ceiling
                    ),
                    "fixed_drift_fraction": case.drift,
                    "fixed_animal_weight": case.animal_weight,
                    "fixed_industry_factor": case.industry,
                    "omit_pakistan_urban_animal": case.omit_pakistan_overlap,
                    **{
                        f"{label}_million_usd_2025_prices": value
                        for label, value in values.items()
                    },
                }
                lookup[(case.name, country, year)] = row
                baseline = lookup[("baseline", country, year)]
                base_median = float(baseline["p50_million_usd_2025_prices"])
                row["median_change_percent_from_baseline"] = 100 * (
                    values["p50"] / base_median - 1
                )
                summaries.append(row)
                prefix = f"{country.lower()}_{year}_market_value"
                for label, value in values.items():
                    reference_id = ""
                    if case.name == "baseline":
                        reference_id = f"{prefix}_{label}"
                    elif case.name == "income_drift_overlap":
                        reference_id = f"{prefix}_drift_overlap_adjusted_{label}"
                    elif (
                        case.name == "pakistan_no_urban_animal"
                        and country == "Pakistan"
                        and year == 2035
                    ):
                        reference_id = f"{prefix}_without_urban_animal_{label}"
                    elif case.name in fixed_refs and year == 2035 and label == "p50":
                        candidate = f"{prefix}_{fixed_refs[case.name]}"
                        reference_id = candidate if candidate in reference else ""
                    if reference_id:
                        checks.append(reference_check(value, reference_id, reference))
    india_median = float(
        lookup[("baseline", "India", 2030)]["p50_million_usd_2025_prices"]
    )
    targets, required = [], []
    for scenario, reference_label in (
        ("low", "low"),
        ("medium", "central"),
        ("high", "high"),
    ):
        target_crore = float(cells[("overall", scenario)]["value_crore"])
        if target_crore != model.get(f"gfi_india_domestic_2030_{reference_label}"):
            raise ValueError(
                "GFI target transcription disagrees with the frozen inputs"
            )
        target = model.convert_crore(target_crore)
        fermentation_crore = float(cells[("fermentation", scenario)]["value_crore"])
        checks.append(
            reference_check(
                target,
                f"india_2030_gfi_india_domestic_scenario_{reference_label}",
                reference,
            )
        )
        range_values = []
        for index in range(21):
            elasticity = 1 + index / 20 * (model.elasticity_max - 1)
            no_drift = model.total("India", 2030, Draw(0, elasticity, 0, 0, 1))
            rate = required_growth(target, no_drift, 8)
            range_values.append(rate)
            required.append(
                {
                    "scenario": scenario,
                    "elasticity": elasticity,
                    "source_target_crore": target_crore,
                    "conditional_target_million_usd": target,
                    "required_extra_growth_percent": rate * 100,
                    "current_extra_growth_ceiling_percent": model.drift_max * 100,
                    "percentage_points_above_current_ceiling": 100
                    * (rate - model.drift_max),
                    "years": 8,
                    "interpretation": "inverse_model_diagnostic_conditional_price_basis",
                }
            )
        targets.append(
            {
                "scenario": scenario,
                "source_target_crore": target_crore,
                "source_value_multiple": target_crore
                / model.get("gfi_india_domestic_2022_central"),
                "source_value_cagr_percent": annual_growth(
                    model.get("gfi_india_domestic_2022_central"), target_crore, 8
                )
                * 100,
                "conditional_target_million_usd": target,
                "gap_above_baseline_median_million_usd": target - india_median,
                "fermentation_source_crore": fermentation_crore,
                "fermentation_share_of_target_percent": 100
                * fermentation_crore
                / target_crore,
                "gap_reduction_if_fermentation_subtracted_percent": 100
                * model.convert_crore(fermentation_crore)
                / (target - india_median),
                "required_growth_at_midpoint_elasticity_percent": range_values[10]
                * 100,
                "required_growth_min_percent": min(range_values) * 100,
                "required_growth_max_percent": max(range_values) * 100,
            }
        )
    sampled_max = max(model.total("India", 2030, draw) for draw in baseline_draws)
    analytic_max = model.total(
        "India", 2030, Draw(0, model.elasticity_max, model.drift_max, 0, 1)
    )
    sampled_cagr = annual_growth(model.anchor, sampled_max, 8) * 100
    checks.append(
        reference_check(sampled_cagr, "india_2030_fastest_draw_growth_max", reference)
    )
    after = {name: sha256(file) for name, file in protected.items()}
    if before != after:
        raise ValueError("An immutable source changed during the diagnostic run")
    return {
        "schema_version": 1,
        "seed": SEED,
        "draw_count": DRAWS,
        "price_qualification": PRICE_QUALIFICATION,
        "interpretation": "Supplementary arithmetic and assumption sensitivity; not a validated forecast, causal gap attribution, or replacement for the retained 127 rows.",
        "source_hashes": before,
        "source_hashes_after": after,
        "source_row_counts": {
            "proxy_inputs": model.input_rows,
            "proxy_reference": len(references),
            "gfi_category_cells": len(category_rows),
        },
        "baseline_parity": {
            "checked_rows": len(checks),
            "six_decimal_agreement": True,
            "max_absolute_rounding_difference": max(
                float(r["absolute_error"]) for r in checks
            ),
        },
        "model": {
            "anchor_million_usd_2025_prices": model.anchor,
            "elasticity_min": 1,
            "elasticity_max": model.elasticity_max,
            "drift_min": model.drift_min,
            "drift_max": model.drift_max,
            "income_overlap_drift_max": model.overlap_drift_max,
        },
        "maxima": {
            "sampled_max_million_usd": sampled_max,
            "sampled_max_cagr_percent": sampled_cagr,
            "analytic_max_million_usd": analytic_max,
            "analytic_max_cagr_percent": annual_growth(model.anchor, analytic_max, 8)
            * 100,
            "analytic_max_below_gfi_low": analytic_max
            < float(targets[0]["conditional_target_million_usd"]),
        },
        "midpoint_parameter_illustration": model.factor_row(midpoint),
        "category_growth": growth,
        "category_reconciliation": sums,
        "target_comparison": targets,
        "required_growth_grid": required,
        "sensitivities": summaries,
        "baseline_reference_checks": checks,
        "factor_draws": factor_rows,
    }


def stable_floats(value: object) -> object:
    """Round floats to 12 significant digits so platform libm last-bit differences do not change output bytes."""
    if isinstance(value, float):
        return float(f"{value:.{OUTPUT_SIGNIFICANT_DIGITS}g}")
    if isinstance(value, dict):
        return {key: stable_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable_floats(item) for item in value]
    return value


def write_csv(file: Path, rows: list[Row]) -> None:
    """Export deterministic 12-significant-digit cells with blanks for unresolved values."""
    with file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_report(result: dict[str, object]) -> str:
    """Render a concise human-readable report from the exact diagnostic values."""
    targets = result["target_comparison"]
    sensitivities = result["sensitivities"]
    maxima = result["maxima"]
    lines = [
        "# Why these scenarios sit below GFI India: numerical diagnostics",
        "",
        str(result["price_qualification"]),
        "",
        str(result["interpretation"]),
        "",
        "The source fermentation baseline is a dash, preserved as missing. Its CAGR and absolute increase are undefined. Source-value growth rates cannot yet be classified as nominal or real.",
        "",
        "## GFI source categories",
        "",
        "| Category | Scenario | 2022 crore | 2030 crore | Absolute increase | Implied annual growth |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in result["category_growth"]:
        delta = (
            "N/A"
            if row["absolute_increase_crore"] is None
            else f"{row['absolute_increase_crore']:,.0f}"
        )
        rate = (
            "N/A"
            if row["source_value_cagr_percent"] is None
            else f"{row['source_value_cagr_percent']:.2f}%"
        )
        lines.append(
            f"| {row['category']} | {row['scenario']} | {row['base_source_display']} | {row['target_crore']:,.0f} | {delta} | {rate} |"
        )
    target_sums_agree = all(
        row["status"] == "exact_agreement"
        for row in result["category_reconciliation"]
        if row["scenario"] != "baseline"
    )
    sum_note = (
        "All three 2030 category sums reconcile to the reported totals."
        if target_sums_agree
        else "At least one 2030 category sum differs from the reported total; the source discrepancy is preserved in category-reconciliation.csv."
    )
    lines += [
        "",
        sum_note
        + " The known 2022 cells sum to 351 crore, but this does not resolve the fermentation dash as zero.",
        "",
        "## Targets and required extra annual growth",
        "",
        "| Scenario | GFI multiple | Conditional USD million | Required growth at midpoint elasticity | Range across elasticity bounds | Fermentation / GFI total | Arithmetic reduction in gap if fermentation subtracted |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in targets:
        lines.append(
            f"| {row['scenario']} | {row['source_value_multiple']:.3f}x | {row['conditional_target_million_usd']:.3f} | {row['required_growth_at_midpoint_elasticity_percent']:.2f}% | {row['required_growth_min_percent']:.2f}–{row['required_growth_max_percent']:.2f}% | {row['fermentation_share_of_target_percent']:.3f}% | {row['gap_reduction_if_fermentation_subtracted_percent']:.3f}% |"
        )
    lines += [
        "",
        "Required growth solves the existing equation for an eight-year extra-growth rate. The elasticity range is assumption sensitivity, not a predictive interval. The current extra-growth ceiling is 17.832570% annually.",
        "",
        "Subtracting fermentation from the target is a scope diagnostic, not causal attribution. The proxy's intended aggregate already includes fermentation, but has no separately estimated category-entry term.",
        "",
        "## Exact factorization",
        "",
    ]
    midpoint = result["midpoint_parameter_illustration"]
    lines.append(
        f"At midpoint parameter values, the 2022–2030 factors are population {midpoint['population_factor']:.6f} × income {midpoint['income_factor']:.6f} × urban share {midpoint['urban_factor']:.6f} × extra growth {midpoint['extra_growth_factor']:.6f}. This gives USD {midpoint['india_2030_million_usd_2025_prices']:.6f} million. It is an illustrative parameter scenario, not the simulated median. Per-draw factors and additive log factors are in factor-draws.csv; neither identifies causal contributions."
    )
    lines += [
        "",
        f"The fastest sampled draw grows {maxima['sampled_max_cagr_percent']:.6f}% annually; the analytical upper-bound case grows {maxima['analytic_max_cagr_percent']:.6f}% and reaches USD {maxima['analytic_max_million_usd']:.6f} million. Its failure to reach the conditional GFI low target is a property of the chosen bounds, not validation of either forecast.",
        "",
        "## Paired diagnostic cases",
        "",
        "Million USD at 2025 prices. P10/P50/P90 describe chosen assumption draws, not calibrated predictive intervals. All cases consume the same four random draws before overrides.",
        "",
        "| Case | Country | Year | P10 | P50 | P90 | Median change |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in sensitivities:
        lines.append(
            f"| {row['case']} | {row['country']} | {row['year']} | {row['p10_million_usd_2025_prices']:.3f} | {row['p50_million_usd_2025_prices']:.3f} | {row['p90_million_usd_2025_prices']:.3f} | {row['median_change_percent_from_baseline']:+.3f}% |"
        )
    lines += [
        "",
        "The zero-floor case rescales the same uniform variate into [0, d_max]; it does not clamp negative baseline draws. It tests only the US-derived drift floor. The separate elasticity grid exposes dependence on the US-derived elasticity ceiling without claiming an empirically estimated local correction. The combined case fixes e=1 and uses the zero floor. The historical US comparison remains descriptive.",
        "",
        "The income/drift overlap case narrows the extra-growth ceiling and lowers the India result, widening the GFI difference. Pakistan's omitted urban/animal and fixed industry-factor cases remain transfer diagnostics without a Pakistan sales baseline. Job-board indicators are not measured demand or independently identified effects.",
        "",
        "## Reproduction receipt",
        "",
        f"{result['baseline_parity']['checked_rows']} retained reference values agree at their six-decimal output precision. Inputs, category extraction and the 127-row reference file have identical pre/post SHA-256 checksums. No baseline engine or panel file is written.",
        "",
        "CSV and JSON values keep 12 significant digits, so outputs match across operating systems; display rounding is only for readability. diagnostics.json contains source checksums, the comparison contract and complete summary values. The full factor table is separate to keep the JSON compact.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(result: dict[str, object], output: Path) -> None:
    """Write deterministic companion artifacts in a separate output directory."""
    result = stable_floats(result)
    output.mkdir(parents=True, exist_ok=True)
    tables = {
        "category-growth.csv": "category_growth",
        "category-reconciliation.csv": "category_reconciliation",
        "target-comparison.csv": "target_comparison",
        "required-growth.csv": "required_growth_grid",
        "sensitivity-summary.csv": "sensitivities",
        "reference-checks.csv": "baseline_reference_checks",
        "factor-draws.csv": "factor_draws",
    }
    for filename, key in tables.items():
        write_csv(output / filename, result[key])
    write_csv(
        output / "midpoint-factors.csv", [result["midpoint_parameter_illustration"]]
    )
    summary = {key: value for key, value in result.items() if key != "factor_draws"}
    summary["factor_draws_artifact"] = {
        "file": "factor-draws.csv",
        "rows": DRAWS,
        "sha256": sha256(output / "factor-draws.csv"),
    }
    (output / "diagnostics.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (output / "REPORT.md").write_text(markdown_report(result), encoding="utf-8")
    files = sorted([*tables, "midpoint-factors.csv", "diagnostics.json", "REPORT.md"])
    receipt = {
        "schema_version": 1,
        "files": [{"path": name, "sha256": sha256(output / name)} for name in files],
    }
    (output / "artifact-hashes.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Run the offline diagnostics with explicit source and output paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inputs", type=Path, default=ROOT / "data/altprotein_proxy_inputs.csv"
    )
    default_reference = ROOT / "data/reference_proxy_scenarios.csv"
    if not default_reference.exists():
        default_reference = ROOT / "data/altprotein_proxy_scenarios.csv"
    parser.add_argument("--reference", type=Path, default=default_reference)
    parser.add_argument(
        "--categories", type=Path, default=ROOT / "data/gfi_categories.csv"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "build/gfi-gap")
    args = parser.parse_args()
    if any(
        file.resolve().is_relative_to(args.output.resolve())
        for file in (args.inputs, args.reference, args.categories)
    ):
        parser.error("The output directory must not contain immutable source files")
    result = build_diagnostics(args.inputs, args.reference, args.categories)
    write_outputs(result, args.output)
    print(
        json.dumps(
            {
                "status": "PASS",
                "draws": DRAWS,
                "category_cells": 20,
                "sensitivity_rows": len(result["sensitivities"]),
                "reference_checks": result["baseline_parity"]["checked_rows"],
                "immutable_hashes_preserved": result["source_hashes"]
                == result["source_hashes_after"],
            }
        )
    )


if __name__ == "__main__":
    main()
