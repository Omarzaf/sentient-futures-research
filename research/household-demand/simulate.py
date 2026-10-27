"""Joint household-demand simulation, with national aggregates and missingness intact.

All monetary inputs at this boundary must be USD_2025. ``rows`` contains one
national segment-product row per country and year: meat, vegetarian (India only),
and dairy. ``map_unit_parameters`` maps independent unit-cube factors to the
same deterministic ``evaluate`` used by Monte Carlo and panel-input reruns.
A single bootstrap index per country preserves coefficient dependence. R24
recentres each coefficient; R25 caps positive own-price responses at zero.

R47 fixes unsourced Bass uncertainty at its registered point prior. R48 (the
controller's vegetarian mapping ruling) transfers the chicken equation's
paneer, soya and pulses cross-price coefficients, expenditure weighted and
negated for the inverse relative premium. This is a diagnostic assumption,
not an identified plant-based price elasticity. ``literal_signed`` exposes
the opposite-sign sensitivity. Missing weights, prices or coefficients are
never silently omitted. Totals require every specified component.

Private household data and bootstrap caches stay outside this repository.
This module does not open any acceptance gate or download any data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from codes import GROUPS, PK_GROUPS
from elasticities import (
    INDIA_GROUPS,
    PAKISTAN_GROUPS,
    Elasticities,
    estimate_elasticities,
)
from segments import assign_segments

__all__ = [
    "SimInputs",
    "SimResult",
    "evaluate",
    "load_inputs",
    "map_unit_parameters",
    "parameter_columns",
    "sample_parameters",
    "simulate",
    "write_result",
]
HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]
WORKSPACE = LIBRARY_ROOT.parent
SEED = 20261018
PAIRS = ("meat", "vegetarian", "dairy")
VEG_GROUPS = ("paneer", "soya", "pulses")
METRICS = ("value_usd_2025", "volume_t", "share")


@dataclass
class SimInputs:
    """National segment-year model inputs, point estimates and joint bootstrap draws."""

    rows: pd.DataFrame
    elasticities: dict[str, Elasticities]
    metadata: dict[str, Any] = field(default_factory=dict)
    price_basis: str = "USD_2025"
    status: str = "DIAGNOSTIC"
    source_statuses: dict[str, str] = field(default_factory=dict)
    diffusion: str = "analog"
    vegetarian_mapping: str = "inverse_premium"
    ai_decline: float = 0.0
    parity_year: int | None = None


@dataclass
class SimResult:
    """National simulation draws, quantiles, component diagnostics and provenance."""

    draws: pd.DataFrame
    quantiles: pd.DataFrame
    ceiling_binding_share: float
    status: str
    diffusion: str
    pair_draws: pd.DataFrame = field(default_factory=pd.DataFrame)
    metadata: dict[str, Any] = field(default_factory=dict)


def _validate(inputs: SimInputs) -> None:
    """Reject incompatible units, malformed rows and invalid scenario controls."""
    if (
        inputs.price_basis != "USD_2025"
        or "price_basis" not in inputs.rows
        or not inputs.rows.price_basis.eq("USD_2025").all()
    ):
        raise ValueError("every monetary input must use price_basis USD_2025")
    if inputs.diffusion not in ("analog", "us_stress"):
        raise ValueError("diffusion must be analog or us_stress")
    if inputs.vegetarian_mapping not in ("inverse_premium", "literal_signed"):
        raise ValueError("unknown vegetarian mapping")
    if not 0 <= inputs.ai_decline < 1:
        raise ValueError("ai_decline must be in [0,1)")
    if inputs.parity_year is not None and inputs.parity_year <= 2026:
        raise ValueError("parity_year must be after 2026")
    if (
        inputs.rows.empty
        or inputs.rows[["country", "year", "pair"]].isna().any().any()
        or inputs.rows.duplicated(["country", "year", "pair"]).any()
    ):
        raise ValueError("require distinct non-empty country, year, pair rows")
    if np.isinf(
        inputs.rows.select_dtypes(include="number").to_numpy(dtype=float)
    ).any():
        raise ValueError("numeric inputs must be finite or missing")
    for name in ("bass_q", "spend_us", "conversion", "poultry_kg_per_capita"):
        if (inputs.rows[name].dropna() < 0).any():
            raise ValueError(f"{name} must be nonnegative or missing")
    if not inputs.rows.pair.isin(PAIRS).all():
        raise ValueError("unknown segment-product pair")
    for (country, year), part in inputs.rows.groupby(["country", "year"]):
        expected = set(PAIRS) if country == "India" else {"meat", "dairy"}
        if country not in ("India", "Pakistan") or set(part.pair) != expected:
            raise ValueError(
                f"incomplete or invalid segment-product pairs: {country} {year}"
            )
        if country not in inputs.elasticities:
            raise ValueError(f"missing country elasticities: {country}")
    _status(inputs)
    if inputs.status not in ("DIAGNOSTIC", "SYNTHETIC", "ACCEPTED"):
        raise ValueError("unknown simulation status")
    positive = (
        "hh_size",
        "urban_survey",
        "income_us",
        "ratio",
        "ratio_us",
        "price_usd_2025_kg",
        "bass_p",
    )
    for name in positive:
        if (inputs.rows[name].dropna() <= 0).any():
            raise ValueError(f"{name} must be positive or missing")
    for name in ("addressable_share", "intent", "urban_survey"):
        if not inputs.rows[name].dropna().between(0, 1).all():
            raise ValueError(f"{name} must be in [0,1] or missing")
    for prefix in ("population", "income", "urban"):
        low, mid, high = (inputs.rows[f"{prefix}_{b}"] for b in ("low", "mid", "high"))
        if ((low > mid) | (mid > high) | (low <= 0)).any():
            raise ValueError(f"invalid {prefix} bands")


def parameter_columns(inputs: SimInputs) -> list[str]:
    """Names of independent unit-cube factors, with one joint elasticity factor."""
    names = ["us_intent"]
    for country in sorted(inputs.rows.country.unique()):
        names.extend(
            f"{country}:{factor}"
            for factor in (
                "elasticities",
                "intent",
                "income",
                "population",
                "urban",
                "bass_p",
                "bass_q",
            )
        )
    return names


def map_unit_parameters(inputs: SimInputs, unit_cube: np.ndarray) -> pd.DataFrame:
    """Wrap independent U[0,1] factors; evaluate performs their fixed mapping."""
    cube = np.asarray(unit_cube, dtype=float)
    names = parameter_columns(inputs)
    if cube.ndim != 2 or cube.shape[1] != len(names) or not len(cube):
        raise ValueError(f"unit_cube must have shape (n, {len(names)})")
    if not np.isfinite(cube).all() or ((cube < 0) | (cube > 1)).any():
        raise ValueError("unit-cube coordinates must be finite and in [0,1]")
    return pd.DataFrame(cube, columns=names)


def sample_parameters(
    inputs: SimInputs, n: int = 10_000, seed: int = SEED
) -> pd.DataFrame:
    """Sample the reproducible joint factor distribution used by evaluate."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    rng = np.random.default_rng(seed)
    return map_unit_parameters(inputs, rng.random((n, len(parameter_columns(inputs)))))


@lru_cache(maxsize=16)
def _beta_grid(mean: float, sample_size: float) -> tuple[np.ndarray, np.ndarray]:
    """Tabulate the R46 Beta(mean*n,(1-mean)*n) CDF without new dependencies."""
    if not 0 < mean < 1 or sample_size <= 0:
        raise ValueError("Beta intent requires 0 < mean < 1 and sample size > 0")
    a, b = mean * sample_size, (1 - mean) * sample_size
    # Numerical inverse CDF on a fixed grid, not an additional simulated sample.
    x = np.linspace(1e-12, 1 - 1e-12, 65537)
    log_density = (a - 1) * np.log(x) + (b - 1) * np.log1p(-x)
    density = np.exp(log_density - log_density.max())
    cdf = np.r_[0.0, np.cumsum((density[:-1] + density[1:]) * np.diff(x) / 2)]
    return x, cdf / cdf[-1]


def _intent(mean: float, sample_size: float, coordinate: np.ndarray) -> np.ndarray:
    """Return Beta quantiles when the registered sample size exists, else fixed."""
    mean, sample_size = _finite(mean), _finite(sample_size)
    if not np.isfinite(mean):
        return np.full(len(coordinate), np.nan)
    if not np.isfinite(sample_size):
        return np.full(len(coordinate), mean)
    x, cdf = _beta_grid(float(mean), float(sample_size))
    return np.interp(coordinate, cdf, x)


def _band(row: dict, prefix: str, coordinate: np.ndarray) -> np.ndarray:
    """Interpolate low, mid and high as bounded scenario bands, not calibrated tails."""
    low, mid, high = (row[f"{prefix}_{b}"] for b in ("low", "mid", "high"))
    # The driver artifacts define bands, not full probability distributions.
    # A bounded piecewise-linear quantile curve is an explicit scenario assumption.
    return np.where(
        coordinate <= 0.5,
        low + 2 * coordinate * (mid - low),
        mid + 2 * (coordinate - 0.5) * (high - mid),
    )


def _coefficient(
    inputs: SimInputs, parameters: pd.DataFrame, country: str, key: str
) -> np.ndarray:
    """Sample a joint bootstrap row and recenter on its point estimate (R24)."""
    result = inputs.elasticities[country]
    point = result.estimates.get(key, np.nan)
    if key not in result.draws or result.draws.empty or not np.isfinite(point):
        return np.full(len(parameters), np.nan)
    observed = result.draws[key].to_numpy(float)
    finite = observed[np.isfinite(observed)]
    if not len(finite):
        return np.full(len(parameters), np.nan)
    index = np.minimum(
        (parameters[f"{country}:elasticities"].to_numpy() * len(observed)).astype(int),
        len(observed) - 1,
    )
    return observed[index] - np.median(finite) + point


def _status(
    inputs: SimInputs, country: str | None = None, pair: str | None = None
) -> str:
    """Propagate the least accepted applicable source and explicit synthetic taint."""
    rows = (
        inputs.rows if country is None else inputs.rows[inputs.rows.country.eq(country)]
    )
    if pair is not None:
        rows = rows[rows.pair.eq(pair)]
    source_flags = [
        value
        for key, value in inputs.source_statuses.items()
        if country is None or ":" not in key or key.startswith(country + ":")
    ]
    flags = [inputs.status, *rows.status.tolist(), *source_flags]
    if any(flag not in ("DIAGNOSTIC", "SYNTHETIC", "ACCEPTED") for flag in flags):
        raise ValueError("every relevant input status must be known")
    if "SYNTHETIC" in flags:
        return "SYNTHETIC"
    if "DIAGNOSTIC" in flags:
        return "DIAGNOSTIC"
    applicable = (
        inputs.elasticities.values()
        if country is None
        else [inputs.elasticities[country]]
    )
    if any(estimate.variance_strata_placeholder for estimate in applicable):
        return "DIAGNOSTIC"
    return "ACCEPTED"


def evaluate(inputs: SimInputs, parameters: pd.DataFrame) -> SimResult:
    """Evaluate all country-years deterministically with supplied joint factors."""
    _validate(inputs)
    if list(parameters.columns) != parameter_columns(inputs):
        raise ValueError("parameter columns must match parameter_columns(inputs)")
    map_unit_parameters(inputs, parameters.to_numpy())
    n = len(parameters)
    us_intent = _intent(
        _finite(inputs.metadata.get("us_intent", np.nan)),
        _finite(inputs.metadata.get("us_intent_n", np.nan)),
        parameters.us_intent.to_numpy(),
    )
    pieces = []
    capped = 0
    for row in inputs.rows.to_dict("records"):
        country, pair, year = row["country"], row["pair"], row["year"]

        def coordinate(name: str, country: str = country) -> np.ndarray:
            """Read the same country factor for each year and category."""
            return parameters[f"{country}:{name}"].to_numpy()

        population = _band(row, "population", coordinate("population"))
        income = _band(row, "income", coordinate("income"))
        urban = _band(row, "urban", coordinate("urban"))
        group = "milk" if pair == "dairy" else "chicken"
        income_e = _coefficient(inputs, parameters, country, f"income:{group}")
        if pair == "vegetarian":
            weights = np.array([row.get(f"weight_{g}", np.nan) for g in VEG_GROUPS])
            if (
                not np.isfinite(weights).all()
                or not np.isclose(weights.sum(), 1)
                or (weights < 0).any()
            ):
                price_e = np.full(n, np.nan)
            else:
                coefficients = np.column_stack(
                    [
                        _coefficient(
                            inputs, parameters, country, f"cross_price:chicken:{g}"
                        )
                        for g in VEG_GROUPS
                    ]
                )
                price_e = np.sum(coefficients * weights, axis=1)
                if inputs.vegetarian_mapping == "inverse_premium":
                    price_e = -price_e
        else:
            price_e = _coefficient(inputs, parameters, country, f"own_price:{group}")
            capped += int(np.sum(price_e > 0))
            price_e = np.minimum(price_e, 0)
        if pair == "dairy":
            intent = np.full(n, row["intent"])
            conversion = np.full(n, row["conversion"])
        else:
            intent = (
                0.329 + (0.628 - 0.329) * coordinate("intent")
                if country == "Pakistan"
                else _intent(
                    row["intent"], row.get("intent_n", np.nan), coordinate("intent")
                )
            )
            # The same US intent draw determines every country's conversion.
            conversion = (
                row["conversion"] * inputs.metadata.get("us_intent", np.nan) / us_intent
            )
        elapsed = max(0, year - 2026)
        ratio = np.full(n, row["ratio"] * (1 - inputs.ai_decline) ** elapsed)
        if inputs.parity_year is not None:
            parity_ratio = row["ratio"] ** (
                1 - min(1, elapsed / (inputs.parity_year - 2026))
            )
            ratio = np.minimum(ratio, parity_ratio)
        price = row["price_usd_2025_kg"] * ratio / row["ratio"]
        p, q, launch = row["bass_p"], row["bass_q"], row["launch_year"]
        if inputs.diffusion == "us_stress":
            fit = inputs.metadata.get("us_stress", {})
            p, q = fit.get("p", np.nan), fit.get("q", np.nan)
            # Transfer the US fitted shape to each country's own launch clock.
        decay = math.exp(-(p + q) * np.maximum(0, year - launch))
        bass = (1 - decay) / (1 + q / p * decay)
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            adoption = np.clip(
                conversion * intent * (ratio / row["ratio_us"]) ** price_e * bass, 0, 1
            )
            households = (
                np.minimum(row["addressable_share"] * urban / row["urban_survey"], 1)
                * population
                / row["hh_size"]
            )
            value = (
                households
                * adoption
                * row["spend_us"]
                * (income / row["income_us"]) ** income_e
            )
            # numpy treats NaN**0 as 1; a zero response must not erase missing inputs.
            price_known = (
                np.isfinite(ratio) & np.isfinite(row["ratio_us"]) & np.isfinite(price_e)
            )
            income_known = (
                np.isfinite(income)
                & np.isfinite(row["income_us"])
                & np.isfinite(income_e)
            )
            adoption = np.where(price_known, adoption, np.nan)
            value = np.where(price_known & income_known, value, np.nan)
            volume = value / price / 1000
        binding = np.zeros(n, dtype=bool)
        if pair == "meat":
            ceiling = population * row["poultry_kg_per_capita"] / 1000
            binding = volume > ceiling
            volume = np.minimum(volume, ceiling)
            # Missing plant price or supply means no defensible capped value.
            value = volume * price * 1000
        pieces.append(
            pd.DataFrame(
                {
                    "draw": np.arange(n),
                    "country": country,
                    "year": year,
                    "pair": pair,
                    "value_usd_2025": value,
                    "volume_t": volume,
                    "adopt_share": adoption,
                    "addressable_households": households,
                    "population": population,
                    "price_elasticity": price_e,
                    "income_elasticity": income_e,
                    "ceiling_binding": binding,
                    "status": _status(inputs, country, pair),
                }
            )
        )
    pairs = pd.concat(pieces, ignore_index=True)
    totals = []
    for (country, year), rows in inputs.rows.groupby(["country", "year"], sort=True):
        part = pairs[pairs.country.eq(country) & pairs.year.eq(year)]
        count = len(rows)
        grouped = part.groupby("draw", sort=True)
        sums = grouped[["value_usd_2025", "volume_t"]].sum(min_count=count)
        available = grouped.value_usd_2025.sum(min_count=1)
        first = rows.iloc[0]
        population = grouped.population.first()
        spend = (
            first["protein_spending_per_household_usd_2025"]
            * population
            / first["hh_size"]
        )
        share = sums.value_usd_2025 / spend
        share = share.where(spend > 0)
        residual = _finite(first.get("residual_usd_2025", np.nan))
        totals.append(
            pd.DataFrame(
                {
                    "draw": sums.index,
                    "country": country,
                    "year": year,
                    "value_usd_2025": sums.value_usd_2025.to_numpy(),
                    "volume_t": sums.volume_t.to_numpy(),
                    "share": share.to_numpy(),
                    "available_value_usd_2025": available.to_numpy(),
                    "residual_usd_2025": residual,
                    "total_with_residual_usd_2025": sums.value_usd_2025.to_numpy()
                    + residual,
                    "status": _status(inputs, country),
                    "scenario": (
                        "CONDITIONAL_TRANSFER"
                        if country == "Pakistan"
                        else "HOUSEHOLD_DIAGNOSTIC"
                    ),
                }
            )
        )
    draws = pd.concat(totals, ignore_index=True)
    quantiles = []
    for (country, year), part in draws.groupby(["country", "year"], sort=True):
        for metric in METRICS:
            values = part[metric].to_numpy(float)
            # Do not drop failed coefficient draws to make a narrower interval.
            qs = np.quantile(values, [0.1, 0.5, 0.9])
            quantiles.append(
                {
                    "country": country,
                    "year": year,
                    "metric": metric,
                    "p10": qs[0],
                    "p50": qs[1],
                    "p90": qs[2],
                    "valid_draws": int(np.isfinite(values).sum()),
                    "total_draws": n,
                    "status": _status(inputs, country),
                }
            )
    eligible = pairs[pairs.pair.eq("meat") & pairs.volume_t.notna()]
    binding_share = float(eligible.ceiling_binding.mean()) if len(eligible) else np.nan
    metadata = {
        **inputs.metadata,
        "positive_own_price_capped": capped,
        "own_price_evaluations": n * int(inputs.rows.pair.ne("vegetarian").sum()),
        "ceiling_displacement_assumption": "One kg of plant-based meat product displaces one kg of chicken product; no protein-equivalence conversion is claimed.",
        "own_price_cap_note": "R25 deviation: own-price draws above zero capped at zero, no replacement literature value",
        "bootstrap_recentering": "R24 draw minus bootstrap median plus point estimate",
        "vegetarian_mapping": inputs.vegetarian_mapping,
        "driver_distribution": "bounded piecewise-linear quantile interpolation at u=0,0.5,1; band endpoints are not interpreted as calibrated tail quantiles",
        "beta_numerics": "Beta(mean*n,(1-mean)*n) inverse CDF; 65537 point trapezoid grid",
        "fixed_factors": ["bass_p", "bass_q"],
        "ceiling_binding_denominator": len(eligible),
        "adoption_clipped_to_probability": True,
        "ai_decline": inputs.ai_decline,
        "parity_year": inputs.parity_year,
    }
    return SimResult(
        draws,
        pd.DataFrame(quantiles),
        binding_share,
        _status(inputs),
        inputs.diffusion,
        pairs,
        metadata,
    )


def simulate(inputs: SimInputs, n: int = 10_000, seed: int = SEED) -> SimResult:
    """Run one seeded joint Monte Carlo over every modelled country and year."""
    result = evaluate(inputs, sample_parameters(inputs, n, seed))
    result.metadata.update({"seed": seed, "draws": n})
    return result


def _sha256(path: Path) -> str:
    """Hash a local input without logging its household contents."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _finite(value: Any) -> float:
    """Represent JSON null or absent numeric data as a missing float."""
    return np.nan if value is None else float(value)


def _read(path: Path) -> dict:
    """Load one local aggregate JSON artifact."""
    return json.loads(path.read_text())


def _weighted(values: pd.Series, weights: pd.Series) -> float:
    """Weighted mean among observed positive-weight rows, with explicit exclusion."""
    good = values.notna() & weights.gt(0)
    return (
        float(np.average(values[good], weights=weights[good])) if good.any() else np.nan
    )


def _cached_elasticities(
    country: str,
    household_path: Path,
    households: pd.DataFrame,
    cache: Path,
    draws: int,
) -> Elasticities:
    """Re-estimate actual bootstrap draws, caching only outside the repository."""
    cache = cache.resolve()
    if cache.is_relative_to(LIBRARY_ROOT):
        raise ValueError("bootstrap cache must be outside the repository")
    identity = {
        "household_sha256": _sha256(household_path),
        "estimator_sha256": _sha256(HERE / "elasticities.py"),
        "draws": draws,
        "seed": SEED,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    stem = cache / f"{country.lower()}-elasticities-{key}"
    meta_path, draws_path = stem.with_suffix(".json"), stem.with_suffix(".parquet")
    if meta_path.exists() and draws_path.exists():
        meta = _read(meta_path)
        if meta.get("identity") != identity or meta.get("draws_sha256") != _sha256(
            draws_path
        ):
            raise ValueError("bootstrap cache identity/hash mismatch")
        return Elasticities(
            own_price={k: _finite(v) for k, v in meta["own_price"].items()},
            income={k: _finite(v) for k, v in meta["income"].items()},
            cross_price={
                tuple(k.split(":")): _finite(v) for k, v in meta["cross_price"].items()
            },
            draws=pd.read_parquet(draws_path),
            level="national",
            country=country,
            variance_strata_placeholder=meta["variance_strata_placeholder"],
        )
    groups = INDIA_GROUPS if country == "India" else PAKISTAN_GROUPS
    result = estimate_elasticities(
        households, list(groups), cluster="psu", draws=draws, seed=SEED
    )
    cache.mkdir(parents=True, exist_ok=True)
    result.draws.to_parquet(draws_path, index=False)
    meta = {
        "identity": identity,
        "own_price": result.own_price,
        "income": result.income,
        "cross_price": {":".join(k): v for k, v in result.cross_price.items()},
        "variance_strata_placeholder": result.variance_strata_placeholder,
        "draws_sha256": _sha256(draws_path),
    }
    meta_path.write_text(json.dumps(_json_safe(meta), indent=2, allow_nan=False) + "\n")
    return result


def _source_scalar(
    table: pd.DataFrame, country: str, year: int, quantity: str
) -> float:
    """Require an unambiguous local aggregate source row, otherwise keep missing."""
    found = table[
        table.country.eq(country) & table.year.eq(year) & table.quantity.eq(quantity)
    ]
    if len(found) > 1:
        raise ValueError(f"ambiguous source: {country} {year} {quantity}")
    return _finite(found.value.iloc[0]) if len(found) else np.nan


def load_inputs(
    work_dir: Path | None = None,
    cache_dir: Path | None = None,
    *,
    bootstrap_draws: int = 500,
    countries: tuple[str, ...] = ("India", "Pakistan"),
    years: tuple[int, ...] = (2026, 2030, 2035),
    diffusion: str = "analog",
    exchange_rates: dict[str, float] | None = None,
    residuals: dict[str, dict[int, float]] | None = None,
) -> SimInputs:
    """Load real local surveys and Tasks 4 to 7 artifacts, with no downloads."""
    from drivers import _read_wup

    work = Path(work_dir or WORKSPACE / "OUTPUTS/Household Demand 2026-10/work")
    cache = Path(cache_dir or work / "simulation")
    if work.resolve().is_relative_to(LIBRARY_ROOT):
        raise ValueError("household work directory must be outside the repository")
    output = HERE / "outputs"
    paths = {
        name: output / f"{name}.json"
        for name in (
            "us_calibration",
            "drivers",
            "prices_summary",
            "diffusion",
            "elasticities_national",
            "segments_summary",
        )
    }
    artifacts = {name: _read(path) for name, path in paths.items()}
    protocol = _read(HERE / "protocol.json")
    source = pd.read_csv(
        LIBRARY_ROOT / "research/india-pakistan/data/altprotein_proxy_inputs.csv"
    )
    supply = pd.read_csv(
        LIBRARY_ROOT / "research/india-pakistan/data/meat_supply_national.csv"
    )
    benchmark_path = WORKSPACE / "future-research/data/annual.csv"
    benchmark = pd.read_csv(benchmark_path)
    wup_path = work.parent / "inputs/un_wup/WUP2018-Excel-files.zip"
    urban = _read_wup(wup_path)
    driver = artifacts["drivers"]
    prices = artifacts["prices_summary"]
    observed = pd.DataFrame(prices["price_ratio_2025_prices"]["rows"])
    placeholder = pd.DataFrame(
        _read(HERE / "synthetic/outputs/price_ratios_placeholder.json")["rows"]
    )
    calibration = artifacts["us_calibration"]["categories"]
    intent_source = protocol["intent_sources"]["primary"]
    us_mean = intent_source["values"]["USA"]["plant_based_very_or_extremely_likely"]
    us_n = intent_source.get("sample", {}).get("USA", np.nan)
    income_us = _source_scalar(source, "United States", 2025, "gdp_per_capita_usd")
    fx_path = (
        WORKSPACE
        / "OUTPUTS/Pakistan-India Data Dashboard/data/raw/altprotein/proxy/worldbank-PA.NUS.FCRF.json"
    )
    fx_hash = _sha256(fx_path)
    expected_fx_hash = (
        "afc4d7b4d7f23090887403e1aabf4108679919c15bb45023b054563613b23439"
    )
    if fx_hash != expected_fx_hash:
        raise ValueError(
            "official 2025 FX capture hash differs from verified provenance"
        )
    fx_source = json.loads(fx_path.read_text())
    fx_observed = {}
    for code, country in (("IND", "India"), ("PAK", "Pakistan")):
        entries = [
            row
            for row in fx_source[1]
            if row["countryiso3code"] == code and row["date"] == "2025"
        ]
        if len(entries) != 1:
            raise ValueError(f"expected one official 2025 FX source row: {country}")
        fx_observed[country] = _finite(entries[0]["value"])
    rows, estimates, coverage, identities = [], {}, {}, {}
    for country in countries:
        household_path = work / f"{country.lower()}_households.parquet"
        table = pd.read_parquet(household_path)
        estimates[country] = _cached_elasticities(
            country, household_path, table, cache, bootstrap_draws
        )
        # Assert that the rebuilt point estimates reproduce the rounded saved artifact.
        registered = artifacts["elasticities_national"]["countries"][country][
            "elasticities"
        ]
        for key, point in estimates[country].estimates.items():
            saved = _finite(registered[key]["estimate"])
            if np.isfinite(saved) and not np.isclose(
                point, saved, atol=0.000051, rtol=0
            ):
                raise ValueError(
                    f"rebuilt point estimate differs from Task 4: {country} {key}"
                )
        segmented = assign_segments(table, nfhs=None)
        known = segmented.segment.notna()
        weight = segmented.multiplier.astype(float)
        hh_size = _weighted(segmented.hh_size, weight)
        masks = {
            "meat": segmented.addressable,
            "vegetarian": segmented.addressable_vegetarian,
            "dairy": segmented.addressable | segmented.addressable_vegetarian,
        }
        shares = {
            pair: float(weight[mask & known].sum() / weight[known].sum())
            for pair, mask in masks.items()
        }
        survey_years = (
            ((2023, 5 / 12), (2024, 7 / 12))
            if country == "India"
            else ((2024, 0.5), (2025, 0.5))
        )
        survey_urban = sum(
            float(
                urban.loc[
                    urban.country.eq(country) & urban.year.eq(year), "urban_share"
                ].iloc[0]
            )
            * share
            for year, share in survey_years
        )
        plant_deflator = 1 / driver["cpi_index_2025"][country]["2026"]
        survey_deflator = 1 / sum(
            driver["cpi_index_2025"][country][str(year)] * share
            for year, share in survey_years
        )
        fx = (exchange_rates or {}).get(country, fx_observed[country])
        if np.isfinite(fx) and fx <= 0:
            raise ValueError("exchange rate must be positive local currency per USD")
        group_codes = GROUPS if country == "India" else PK_GROUPS
        protein_columns = [
            f"value_month_{group}"
            for group, codes in group_codes.items()
            if codes and group not in ("packaged", "meals_out")
        ]
        protein = segmented.reindex(columns=protein_columns).sum(
            axis=1, min_count=len(protein_columns)
        )
        # Complete case is required: missing survey groups cannot become zero spending.
        complete = protein.notna()
        protein_spend = (
            _weighted(protein, weight) * 12 * survey_deflator / fx
            if complete.all()
            else np.nan
        )
        chicken = supply[
            supply.country.eq(country)
            & supply.item.eq("Poultry Meat")
            & supply.metric.eq("food_supply_quantity")
            & supply.unit.eq("kg/capita/year")
        ].sort_values("year")
        if chicken.empty:
            poultry, poultry_year = np.nan, None
        else:
            poultry, poultry_year = float(chicken.iloc[-1].value), int(
                chicken.iloc[-1].year
            )
        context = benchmark[
            benchmark.country.eq(country) & benchmark.component.eq("total")
        ].sort_values("year")
        coverage[country] = {
            "households": len(table),
            "protein_complete_households": int(complete.sum()),
            "protein_required_groups": protein_columns,
            "protein_denominator_scope": "Country-mapped animal and legume food groups only; no unmapped item or absent item is recoded as zero.",
            "protein_spending_note": "Share is missing unless every household has all specified observed protein-food groups; no missing item is zero-filled.",
            "survey_mean_household_size": hh_size,
            "survey_urban_share": survey_urban,
            "addressable_shares": shares,
            "poultry_supply_base_year": poultry_year,
            "poultry_supply_kg_per_capita": poultry,
            "poultry_projection": "latest observed per-capita supply held fixed; population changes",
            "protein_supply_context_g_per_capita_day": (
                float(context.iloc[-1].y) if len(context) else None
            ),
            "protein_supply_context_year": (
                int(context.iloc[-1].year) if len(context) else None
            ),
            "exchange_rate_local_per_usd_2025": fx,
            "nfhs_calibration": "NOT_DONE",
        }
        identities[country] = {
            "households_sha256": _sha256(household_path),
            "bootstrap_draws": len(estimates[country].draws),
            "bootstrap_source": "actual re-estimated PSU-bootstrap draws with source/code-hashed external cache",
        }
        for pair in PAIRS:
            if pair == "vegetarian" and country != "India":
                continue
            category = "dairy_alt" if pair == "dairy" else "plant_meat"
            cal = calibration[
                "dairy_alternatives" if pair == "dairy" else "plant_based_meat"
            ]
            ratio_rows = observed[
                observed.country.eq(country) & observed.category.eq(category)
            ].copy()
            is_placeholder = ratio_rows.empty
            if is_placeholder:
                ratio_rows = placeholder[
                    placeholder.country.eq(country) & placeholder.category.eq(category)
                ].copy()
                ratio_rows["price_ratio"] = (
                    ratio_rows.price_ratio * plant_deflator / survey_deflator
                )
            state_weights = (
                weight[masks[pair]].groupby(segmented.loc[masks[pair], "state"]).sum()
            )
            aligned = ratio_rows.set_index("state").reindex(state_weights.index)
            ratio = (
                _weighted(aligned.price_ratio, state_weights)
                if not aligned.price_ratio.isna().any()
                else np.nan
            )
            plant = (
                _weighted(aligned.plant_price_per_kg_local, state_weights)
                if not aligned.plant_price_per_kg_local.isna().any()
                else np.nan
            )
            extra = {}
            if pair == "vegetarian":
                veg = segmented.loc[masks[pair]]
                vw = weight[masks[pair]]
                # Observed expenditure totals determine composition, never household totals.
                spend = np.array(
                    [
                        float((veg[f"value_month_{g}"] * vw).sum(min_count=1))
                        for g in VEG_GROUPS
                    ]
                )
                weights = spend / spend.sum()
                refs = np.array(
                    [_weighted(veg[f"unit_value_{g}"], vw) for g in VEG_GROUPS]
                )
                ratio = (
                    plant * plant_deflator / (np.sum(weights * refs) * survey_deflator)
                    if np.isfinite(weights).all() and np.isfinite(refs).all()
                    else np.nan
                )
                extra = {f"weight_{g}": w for g, w in zip(VEG_GROUPS, weights)}
            for year in years:
                record = {
                    "country": country,
                    "year": year,
                    "pair": pair,
                    "addressable_share": shares[pair],
                    "hh_size": hh_size,
                    "urban_survey": survey_urban,
                    "income_us": income_us,
                    "ratio": ratio,
                    "ratio_us": cal["price_ratio_us"],
                    "price_usd_2025_kg": plant * plant_deflator / fx,
                    "conversion": cal["conversion"],
                    "intent": (
                        cal["intent_share"]
                        if pair == "dairy"
                        else intent_source["values"]["India"][
                            "plant_based_very_or_extremely_likely"
                        ]
                    ),
                    "intent_n": (
                        np.nan
                        if pair == "dairy"
                        else intent_source.get("sample", {}).get("India", np.nan)
                    ),
                    "spend_us": cal["spend_per_adopter_usd"],
                    "bass_p": artifacts["diffusion"]["main"]["p"],
                    "bass_q": artifacts["diffusion"]["main"]["q"],
                    "launch_year": artifacts["diffusion"]["main"]["launch_year"][
                        country
                    ],
                    "poultry_kg_per_capita": poultry,
                    "protein_spending_per_household_usd_2025": protein_spend,
                    "residual_usd_2025": (residuals or {})
                    .get(country, {})
                    .get(year, np.nan),
                    "price_basis": "USD_2025",
                    "status": (
                        "SYNTHETIC"
                        if is_placeholder
                        or aligned.status.eq("SYNTHETIC").any()
                        or cal.get("status") == "SYNTHETIC"
                        else "DIAGNOSTIC"
                    ),
                    **extra,
                }
                for prefix, variable in (
                    ("income", "gdp_per_capita_usd_2025"),
                    ("population", "population"),
                    ("urban", "urban_share"),
                ):
                    for band in ("low", "mid", "high"):
                        record[f"{prefix}_{band}"] = _finite(
                            driver["bands"][variable][country]
                            .get(str(year), {})
                            .get(band)
                        )
                rows.append(record)
    metadata = {
        "us_intent": us_mean,
        "us_intent_n": us_n,
        "us_stress": artifacts["diffusion"]["us_stress"]["fit"],
        "source_hashes": {
            **{name: _sha256(path) for name, path in paths.items()},
            "protocol": _sha256(HERE / "protocol.json"),
            "benchmark_annual": _sha256(benchmark_path),
            "wup": _sha256(wup_path),
            "official_fx_2025": fx_hash,
            "proxy_inputs": _sha256(
                LIBRARY_ROOT
                / "research/india-pakistan/data/altprotein_proxy_inputs.csv"
            ),
            "poultry_supply": _sha256(
                LIBRARY_ROOT / "research/india-pakistan/data/meat_supply_national.csv"
            ),
            **(
                {
                    "placeholder_prices": _sha256(
                        HERE / "synthetic/outputs/price_ratios_placeholder.json"
                    )
                }
                if any(row["status"] == "SYNTHETIC" for row in rows)
                else {}
            ),
            "simulator": _sha256(Path(__file__)),
            "elasticity_estimator": _sha256(HERE / "elasticities.py"),
            "segmentation": _sha256(HERE / "segments.py"),
        },
        "household_provenance": identities,
        "fx_provenance": {
            "source": "World Bank WDI PA.NUS.FCRF",
            "capture_last_updated": fx_source[0].get("lastupdated"),
            "year": 2025,
            "unit": "local currency per US dollar, period average",
            "values": fx_observed,
            "locator": "JSON [1], countryiso3code IND or PAK, date 2025",
            "override_countries": sorted((exchange_rates or {}).keys()),
        },
        "environment": {"numpy": np.__version__, "pandas": pd.__version__},
        "coverage": coverage,
        "review_status": "human scholarly review pending; diagnostic only",
        "vegetarian_transfer_assumption": "R48: negative observed-expenditure-weighted chicken-equation cross-price response to paneer, soya and pulses; US chicken premium retained as calibration reference",
        "residual_note": "Egg and fermentation residual must be supplied from disaggregated proxy evidence; absent stays null",
        "scope": "Plant-based meat and plant-based liquid milk only; other dairy alternatives are not calibrated by the available US milk category.",
        "volume_unit_convention": "Product tonnes; Task 7 treats liquid packs as 1 ml = 1 g, hence 1 litre = 1 kg for plant milk. This is an assumed density, not measured product mass or protein tonnes. Local conventional milk references are per litre, so the dimensionless dairy ratio uses the same convention.",
        "stress_clock": "US fitted p and q shape transferred to each country launch clock; fitted US calendar launch date is not used as a South Asian launch.",
        "timing_caveat": "Bryant 2019 intent and GFI 2025 penetration are from different periods; the GFI meat category includes seafood.",
        "income_note": "GDP per capita at market USD2025 used as income proxy; US2025 comparison held fixed",
        "stratum_note": "Pakistan official strata unresolved; estimator clusters by province without using invented stratum values",
    }
    return SimInputs(
        pd.DataFrame(rows),
        estimates,
        metadata,
        source_statuses={
            name: artifact.get("status", "DIAGNOSTIC")
            for name, artifact in artifacts.items()
        },
        diffusion=diffusion,
    )


def _json_safe(value: Any) -> Any:
    """Convert nonfinite values to JSON null and numpy scalars to primitives."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def write_result(result: SimResult, path: Path) -> None:
    """Write only aggregate quantiles, enforcing synthetic publication boundaries."""
    path = Path(path).resolve()
    if (
        result.status == "SYNTHETIC"
        and path.is_relative_to(LIBRARY_ROOT)
        and not path.is_relative_to(HERE / "synthetic")
    ):
        raise ValueError(
            "synthetic-derived results must be outside the repository or under synthetic/"
        )
    components = []
    for (country, year, pair), part in result.pair_draws.groupby(
        ["country", "year", "pair"], sort=True
    ):
        for metric in ("value_usd_2025", "volume_t"):
            qs = np.quantile(part[metric].to_numpy(float), [0.1, 0.5, 0.9])
            components.append(
                {
                    "country": country,
                    "year": year,
                    "pair": pair,
                    "metric": metric,
                    "p10": qs[0],
                    "p50": qs[1],
                    "p90": qs[2],
                    "status": part.status.iloc[0],
                }
            )
    payload = {
        "status": result.status,
        "diffusion": result.diffusion,
        "price_basis": "USD_2025",
        "ceiling_binding_share": result.ceiling_binding_share,
        "quantiles": result.quantiles.to_dict("records"),
        "component_quantiles": components,
        "metadata": result.metadata,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(payload), indent=2, allow_nan=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    """CLI for reproducible aggregate outputs with external cache and no downloads."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument(
        "--countries",
        nargs="+",
        choices=("India", "Pakistan"),
        default=["India", "Pakistan"],
    )
    parser.add_argument("--n", type=int, default=10_000)
    parser.add_argument("--bootstrap-draws", type=int, default=500)
    parser.add_argument(
        "--diffusion", choices=("analog", "us_stress"), default="analog"
    )
    parser.add_argument(
        "--vegetarian-mapping",
        choices=("inverse_premium", "literal_signed"),
        default="inverse_premium",
    )
    parser.add_argument("--ai-decline", type=float, default=0.0)
    parser.add_argument("--parity-year", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    inputs = load_inputs(
        args.work_dir,
        args.cache_dir,
        bootstrap_draws=args.bootstrap_draws,
        countries=tuple(args.countries),
        diffusion=args.diffusion,
    )
    inputs.vegetarian_mapping, inputs.ai_decline, inputs.parity_year = (
        args.vegetarian_mapping,
        args.ai_decline,
        args.parity_year,
    )
    result = simulate(inputs, args.n)
    write_result(result, args.out)
    print(
        f"wrote {args.out}; status={result.status}; n={args.n}; diffusion={result.diffusion}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
