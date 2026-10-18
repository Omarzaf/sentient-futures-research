"""Unit-value price, income and cross-price elasticities from the household tables.

Method (Deaton unit-value approach, simplified; plan Task 4):

1. Keep households with ``mpce_status == "OK"``, positive MPCE, household size
   and survey weight. One table holds one country (one ``currency``).
2. Price of group g in a cell is the weighted mean of household market unit
   values ``unit_value_{g}`` (survey weight ``multiplier``). A cell is state by
   price area by sector. The price area is ``district`` in India and the PR-code
   geography (``psu // 100_000``: rural district or urban division) in Pakistan,
   whose table leaves urban ``district`` missing. A cell with fewer than
   ``min_cell_obs`` (default 5) unweighted unit-value households has a missing
   price, and its households leave every equation that uses that price.
3. For each group g, regress ln w_g on the log cell prices of all requested
   groups, ln MPCE and ln household size, with state fixed effects, by weighted
   least squares (numpy). w_g = value_month_g / (mpce_local * hh_size). Only
   households with w_g > 0 enter: an item a household did not report stays
   missing and is never imputed as zero (global constraint), so the estimates
   are conditional on purchase. State fixed effects are absorbed by weighted
   within-state demeaning (Frisch-Waugh-Lovell), which gives the same slopes
   as state dummies.
4. Elasticities. With q_g = w_g * X / p_g and X = mpce * hh_size, the log-share
   form gives own-price b_gg - 1, cross-price b_gk and income 1 + c_g. These
   hold at any share, including the weighted mean share; the weighted mean
   share among purchasers is recorded in ``mean_share`` for Task 8, which needs
   it to convert to level-share or aggregate responses.
5. Variance. Bootstrap PSUs (``cluster``) with the Rao-Wu rescaled bootstrap:
   n_h - 1 PSUs drawn with replacement in each resampling stratum h, weight
   factor count * n_h / (n_h - 1). Resampling strata are the official strata
   (state x sector x ``stratum``) where ``stratum_status == "RESOLVED"`` and
   the province (``state``) elsewhere (decision 18, ruling R2). An official
   stratum with one PSU joins a pooled stratum for its state and sector. Each
   draw recomputes cell prices and all regressions with the draw's weights.
   Seed 20261018.

District variation feeds estimation only. Results are national (one pooled
regression with state fixed effects) or state level (``level="state"`` adds a
separate regression per state in ``by_state``); anything else raises.

Run from the library root (writes national aggregates only, status DIAGNOSTIC):

    python research/household-demand/elasticities.py \
        --india "../OUTPUTS/Household Demand 2026-10/work/india_households.parquet" \
        --pakistan "../OUTPUTS/Household Demand 2026-10/work/pakistan_households.parquet" \
        --out outputs/elasticities_national.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import synthetic

__all__ = [
    "COUNTRY",
    "DEFAULT_DRAWS",
    "INDIA_GROUPS",
    "LEVELS",
    "MIN_CELL_OBS",
    "MIN_STATE_HOUSEHOLDS",
    "PAKISTAN_GROUPS",
    "PLACEHOLDER_STATUS",
    "RESOLVED_STATUS",
    "SEED",
    "Elasticities",
    "cell_prices",
    "estimate_elasticities",
    "main",
    "price_area",
    "psu_factors",
    "resampling_strata",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]

SEED = 20261018
DEFAULT_DRAWS = 500
LEVELS = ("national", "state")
MIN_CELL_OBS = 5
MIN_STATE_HOUSEHOLDS = 30
RESOLVED_STATUS = "RESOLVED"
PLACEHOLDER_STATUS = synthetic.SYNTHETIC
COUNTRY = {"INR": "India", "PKR": "Pakistan"}
CELL_KEYS = ("state", "area", "sector")

# Decision 16: plant-based meat substitutes for chicken and competes with
# paneer, soya chunks and pulses; dairy alternatives substitute for milk.
# Pakistan's table has no paneer or soya unit values.
INDIA_GROUPS = ("chicken", "pulses", "milk", "paneer", "soya")
PAKISTAN_GROUPS = ("chicken", "pulses", "milk")


@dataclass
class Elasticities:
    """Point elasticities, bootstrap draws and the design behind them."""

    own_price: dict[str, float]
    income: dict[str, float]
    cross_price: dict[tuple[str, str], float]
    draws: pd.DataFrame
    level: str
    country: str = ""
    state: str | None = None
    variance_method: dict[str, str] = field(default_factory=dict)
    variance_strata_placeholder: bool = False
    n_households: dict[str, int] = field(default_factory=dict)
    n_cells: dict[str, int] = field(default_factory=dict)
    mean_share: dict[str, float] = field(default_factory=dict)
    min_cell_obs: int = MIN_CELL_OBS
    failed_draws: int = 0
    design: dict[str, int] = field(default_factory=dict)
    by_state: dict[str, Elasticities] = field(default_factory=dict)
    skipped_states: dict[str, str] = field(default_factory=dict)

    @property
    def estimates(self) -> dict[str, float]:
        """Point estimates keyed like the ``draws`` columns."""
        return _flatten(self.own_price, self.income, self.cross_price)

    def intervals(self, coverage: float = 0.95) -> pd.DataFrame:
        """Percentile bootstrap interval and draw median for each parameter."""
        tail = (1 - coverage) / 2
        estimates = self.estimates
        rows = {
            name: {
                "estimate": estimates[name],
                "lower": float(self.draws[name].quantile(tail)),
                "upper": float(self.draws[name].quantile(1 - tail)),
                "draw_median": float(self.draws[name].median()),
            }
            for name in estimates
        }
        return pd.DataFrame.from_dict(rows, orient="index")

    def to_dict(self, coverage: float = 0.95) -> dict:
        """JSON-ready summary: estimates, intervals and design counts (no draws)."""
        table = self.intervals(coverage)
        params = {
            name: {
                "estimate": _round(row["estimate"]),
                "lower": _round(row["lower"]),
                "upper": _round(row["upper"]),
                "draw_median": _round(row["draw_median"]),
            }
            for name, row in table.iterrows()
        }
        out = {
            "country": self.country,
            "level": self.level,
            "elasticities": params,
            "interval": f"bootstrap percentile {coverage:.0%}",
            "draws": len(self.draws),
            "failed_draws": self.failed_draws,
            "n_households": self.n_households,
            "n_cells_with_price": self.n_cells,
            "mean_budget_share_purchasers": {
                g: _round(v, 6) for g, v in self.mean_share.items()
            },
            "min_cell_obs": self.min_cell_obs,
            "variance_method": self.variance_method,
            "variance_strata_placeholder": self.variance_strata_placeholder,
            "design": self.design,
        }
        if self.state is not None:
            out["state"] = self.state
        return out


def _round(value: float, digits: int = 4) -> float | None:
    return None if not np.isfinite(value) else round(float(value), digits)


def _flatten(own: dict, income: dict, cross: dict) -> dict[str, float]:
    out = {f"own_price:{g}": v for g, v in own.items()}
    out.update({f"income:{g}": v for g, v in income.items()})
    out.update({f"cross_price:{g}:{k}": v for (g, k), v in cross.items()})
    return out


def price_area(frame: pd.DataFrame) -> pd.Series:
    """Return the sub-state price area: district, or the PR-code area in Pakistan."""
    if "currency" in frame and frame["currency"].eq("PKR").all():
        return (frame["psu"].astype("int64") // 100_000).rename("area")
    district = frame["district"]
    if district.isna().any():
        raise ValueError("district is missing for some households outside Pakistan")
    return district.astype("int64").rename("area")


def _cell_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {"state": frame["state"], "area": price_area(frame), "sector": frame["sector"]},
        index=frame.index,
    )


def cell_prices(
    frame: pd.DataFrame, groups: list[str], min_obs: int = MIN_CELL_OBS
) -> pd.DataFrame:
    """Weighted mean unit value per state by area by sector cell; small cells are NaN."""
    cells = _cell_frame(frame)
    out = {}
    for g in groups:
        uv = frame[f"unit_value_{g}"]
        has = uv.notna()
        weight = frame["multiplier"].astype(float)
        grouped = pd.DataFrame({"num": (weight * uv)[has], "den": weight[has]}).groupby(
            [cells.loc[has, k] for k in CELL_KEYS]
        )
        sums = grouped.sum()
        price = sums["num"] / sums["den"]
        price[grouped.size() < min_obs] = np.nan
        out[g] = price
    index = pd.MultiIndex.from_frame(cells.drop_duplicates())
    return pd.DataFrame(out).reindex(index).sort_index()


def resampling_strata(frame: pd.DataFrame) -> pd.Series:
    """Label each row with its bootstrap stratum.

    RESOLVED rows: official stratum, state x sector x stratum; a stratum with one
    PSU in ``frame`` joins a pooled stratum for its state and sector. Other rows
    (placeholder strata): the province, ``state``.
    """
    resolved = frame["stratum_status"].eq(RESOLVED_STATUS)
    unknown = ~frame["stratum_status"].isin([RESOLVED_STATUS, PLACEHOLDER_STATUS])
    if unknown.any():
        raise ValueError("stratum_status must be RESOLVED or the placeholder flag")
    state = frame["state"].astype(str)
    sector = frame["sector"].astype(str)
    official = "R:" + state + ":" + sector + ":" + frame["stratum"].astype(str)
    psus = frame["psu"].groupby(official).transform("nunique")
    official = official.where(psus > 1, "R:" + state + ":" + sector + ":pooled")
    return official.where(resolved, "P:" + state).rename("resampling_stratum")


def psu_factors(
    strata: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Rao-Wu rescaled bootstrap for one draw, one entry per PSU.

    Returns (weight factors, selection counts). In a stratum of n_h >= 2 PSUs,
    n_h - 1 PSUs are drawn with replacement and factor = count * n_h / (n_h - 1),
    so factors sum to n_h. A single-PSU stratum keeps factor 1 and count 1.
    """
    codes, _ = pd.factorize(strata)
    n_h = np.bincount(codes)
    order = np.argsort(codes, kind="stable")
    start = np.concatenate([[0], np.cumsum(n_h)[:-1]])
    m_h = np.where(n_h >= 2, n_h - 1, 0)
    draw_stratum = np.repeat(np.arange(n_h.size), m_h)
    pick = start[draw_stratum] + np.floor(
        rng.random(draw_stratum.size) * n_h[draw_stratum]
    )
    counts = np.bincount(order[pick.astype(np.int64)], minlength=codes.size).astype(
        float
    )
    single = n_h[codes] == 1
    counts[single] = 1.0
    scale = np.where(n_h >= 2, n_h / np.maximum(n_h - 1, 1), 1.0)[codes]
    factors = np.where(single, 1.0, counts * scale)
    return factors, counts


class _Design:
    """Arrays for one country (or one state) prepared once for all draws."""

    def __init__(
        self, frame: pd.DataFrame, groups: list[str], cluster: str, min_obs: int
    ):
        self.groups = groups
        self.min_obs = min_obs
        self.weight = frame["multiplier"].to_numpy(float)
        cells = _cell_frame(frame)
        self.cell, _ = pd.factorize(pd.MultiIndex.from_frame(cells))
        self.n_cell = int(self.cell.max()) + 1
        self.state, state_labels = pd.factorize(frame["state"])
        self.n_state = len(state_labels)
        self.psu, psu_labels = pd.factorize(frame[cluster])
        strata = resampling_strata(frame)
        first = pd.Series(np.arange(len(frame))).groupby(self.psu).first().to_numpy()
        self.psu_strata = strata.to_numpy()[first]
        self.n_psu = len(psu_labels)
        self.uv = {g: frame[f"unit_value_{g}"].to_numpy(float) for g in groups}
        self.has_uv = {g: np.isfinite(self.uv[g]) & (self.uv[g] > 0) for g in groups}
        log_x = np.log(frame["mpce_local"].to_numpy(float))
        log_n = np.log(frame["hh_size"].to_numpy(float))
        budget = frame["mpce_local"].to_numpy(float) * frame["hh_size"].to_numpy(float)
        self.rows, self.y, self.share, self.extra = {}, {}, {}, {}
        for g in groups:
            share = frame[f"value_month_{g}"].to_numpy(float) / budget
            rows = np.flatnonzero(np.isfinite(share) & (share > 0))
            self.rows[g] = rows
            self.share[g] = share[rows]
            self.y[g] = np.log(share[rows])
            self.extra[g] = np.column_stack([log_x[rows], log_n[rows]])

    def log_prices(
        self, weight: np.ndarray, count: np.ndarray
    ) -> dict[str, np.ndarray]:
        out = {}
        for g in self.groups:
            has = self.has_uv[g]
            cell = self.cell[has]
            num = np.bincount(
                cell, weights=(weight * self.uv[g])[has], minlength=self.n_cell
            )
            den = np.bincount(cell, weights=weight[has], minlength=self.n_cell)
            obs = np.bincount(cell, weights=count[has], minlength=self.n_cell)
            with np.errstate(divide="ignore", invalid="ignore"):
                price = np.log(num / den)
            price[(obs < self.min_obs) | ~(den > 0)] = np.nan
            out[g] = price
        return out

    def fit(
        self, weight: np.ndarray, count: np.ndarray
    ) -> tuple[dict[str, float], dict]:
        """One weighted fit of every equation; NaN where an equation is singular."""
        log_p = self.log_prices(weight, count)
        k = len(self.groups)
        own, income, cross, n_hh, share = {}, {}, {}, {}, {}
        for i, g in enumerate(self.groups):
            rows = self.rows[g]
            cells = self.cell[rows]
            prices = np.column_stack([log_p[h][cells] for h in self.groups])
            w = weight[rows]
            keep = np.isfinite(prices).all(axis=1) & (w > 0)
            design = np.column_stack([prices, self.extra[g]])[keep]
            y, w, state = self.y[g][keep], w[keep], self.state[rows][keep]
            n_hh[g] = int(keep.sum())
            share[g] = (
                float(np.average(self.share[g][keep], weights=w))
                if keep.any()
                else np.nan
            )
            beta = _within_wls(design, y, w, state, self.n_state)
            own[g] = beta[i] - 1.0
            income[g] = 1.0 + beta[k]
            for j, h in enumerate(self.groups):
                if j != i:
                    cross[(g, h)] = beta[j]
        n_cells = {g: int(np.isfinite(log_p[g]).sum()) for g in self.groups}
        params = _flatten(own, income, cross)
        return params, {"n_households": n_hh, "mean_share": share, "n_cells": n_cells}


def _within_wls(
    design: np.ndarray, y: np.ndarray, w: np.ndarray, state: np.ndarray, n_state: int
) -> np.ndarray:
    """Weighted least squares slopes with state fixed effects absorbed."""
    cols = design.shape[1]
    if y.size <= cols + 1:
        return np.full(cols, np.nan)
    den = np.bincount(state, weights=w, minlength=n_state)
    safe = np.where(den > 0, den, 1.0)

    def demean(v: np.ndarray) -> np.ndarray:
        return v - (np.bincount(state, weights=w * v, minlength=n_state) / safe)[state]

    z = np.column_stack([demean(design[:, c]) for c in range(cols)])
    root = np.sqrt(w)
    zw, yw = z * root[:, None], demean(y) * root
    beta, _, rank, _ = np.linalg.lstsq(zw, yw, rcond=None)
    return beta if rank == cols else np.full(cols, np.nan)


def _prepare(households: pd.DataFrame, groups: list[str], cluster: str, min_obs: int):
    if not groups or len(set(groups)) != len(groups):
        raise ValueError("groups must be a non-empty list of distinct group names")
    for g in groups:
        for col in (f"unit_value_{g}", f"value_month_{g}"):
            if col not in households:
                raise ValueError(f"group {g}: column {col} is absent")
    currencies = households["currency"].dropna().unique()
    if len(currencies) != 1 or currencies[0] not in COUNTRY:
        raise ValueError(
            f"one currency per table (INR or PKR); found {sorted(currencies)}"
        )
    ok = (
        households["mpce_status"].eq("OK")
        & households["mpce_local"].gt(0)
        & households["hh_size"].gt(0)
        & households["multiplier"].gt(0)
        & households[cluster].notna()
    )
    frame = households.loc[ok].reset_index(drop=True)
    prices = cell_prices(frame, groups, min_obs)
    for g in groups:
        if not prices[g].notna().any():
            raise ValueError(
                f"group {g} has no cell with {min_obs} or more market unit values; "
                "it cannot enter as a priced good"
            )
    return frame, COUNTRY[currencies[0]]


def _variance_method(frame: pd.DataFrame, country: str) -> tuple[str, bool]:
    placeholder = bool(frame["stratum_status"].ne(RESOLVED_STATUS).any())
    if placeholder:
        text = (
            "Rao-Wu rescaled PSU bootstrap within province; official sampling strata "
            "unresolved, so placeholder strata are not used for resampling"
        )
        if frame["stratum_status"].eq(RESOLVED_STATUS).any():
            text += "; rows with resolved strata resample within official strata"
    else:
        text = (
            "Rao-Wu rescaled PSU bootstrap within official strata "
            "(state x sector x stratum); single-PSU strata pooled by state and sector"
        )
    return text, placeholder


def _estimate_one(
    frame: pd.DataFrame,
    groups: list[str],
    cluster: str,
    seed: int,
    draws: int,
    min_obs: int,
    level: str,
    country: str,
    state: str | None = None,
) -> Elasticities:
    design = _Design(frame, groups, cluster, min_obs)
    ones = np.ones(len(frame))
    point, info = design.fit(design.weight, ones)
    rng = np.random.default_rng(seed)
    records = []
    for _ in range(draws):
        factors, counts = psu_factors(design.psu_strata, rng)
        params, _ = design.fit(design.weight * factors[design.psu], counts[design.psu])
        records.append(params)
    table = pd.DataFrame.from_records(records, columns=list(point))
    method, placeholder = _variance_method(frame, country)
    strata = pd.Series(design.psu_strata)
    sizes = strata.value_counts()
    own = {g: point[f"own_price:{g}"] for g in groups}
    income = {g: point[f"income:{g}"] for g in groups}
    cross = {
        (g, h): point[f"cross_price:{g}:{h}"] for g in groups for h in groups if g != h
    }
    return Elasticities(
        own_price=own,
        income=income,
        cross_price=cross,
        draws=table,
        level=level,
        country=country,
        state=state,
        variance_method={country: method},
        variance_strata_placeholder=placeholder,
        n_households=info["n_households"],
        n_cells=info["n_cells"],
        mean_share=info["mean_share"],
        min_cell_obs=min_obs,
        failed_draws=int(table.isna().any(axis=1).sum()),
        design={
            "households": len(frame),
            "psus": design.n_psu,
            "cells": design.n_cell,
            "resampling_strata": int(sizes.size),
            "single_psu_resampling_strata": int((sizes == 1).sum()),
            "placeholder_stratum_households": int(
                frame["stratum_status"].ne(RESOLVED_STATUS).sum()
            ),
        },
    )


def estimate_elasticities(
    households: pd.DataFrame,
    groups: list[str],
    cluster: str,
    seed: int = SEED,
    draws: int = DEFAULT_DRAWS,
    level: str = "national",
    min_cell_obs: int = MIN_CELL_OBS,
) -> Elasticities:
    """Estimate own-price, cross-price and income elasticities with PSU bootstrap draws.

    ``level`` is "national" (pooled regression, state fixed effects) or "state"
    (adds one regression per state in ``by_state``); anything else raises
    ValueError, because district variation feeds estimation only (NSO rider).
    """
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}; got {level!r}")
    groups = list(groups)
    frame, country = _prepare(households, groups, cluster, min_cell_obs)
    result = _estimate_one(
        frame, groups, cluster, seed, draws, min_cell_obs, level, country
    )
    if level == "state":
        for value, sub in frame.groupby("state", sort=True):
            key = str(value)
            sub = sub.reset_index(drop=True)
            reason = _state_problem(sub, groups, min_cell_obs)
            if reason:
                result.skipped_states[key] = reason
                continue
            est = _estimate_one(
                sub, groups, cluster, seed, draws, min_cell_obs, level, country, key
            )
            if not np.isfinite(list(est.estimates.values())).all():
                result.skipped_states[key] = "singular regression"
                continue
            result.by_state[key] = est
    return result


def _state_problem(sub: pd.DataFrame, groups: list[str], min_obs: int) -> str:
    """Return why a state cannot carry its own regression, or an empty string."""
    prices = cell_prices(sub, groups, min_obs)
    priced = int(prices.notna().all(axis=1).sum())
    if priced < len(groups) + 2:
        return f"{priced} cells price every group; need {len(groups) + 2}"
    for g in groups:
        buyers = int(sub[f"value_month_{g}"].gt(0).sum())
        if buyers < MIN_STATE_HOUSEHOLDS:
            return f"{g}: {buyers} purchasing households; need {MIN_STATE_HOUSEHOLDS}"
    return ""


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def _resolve_here(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else HERE / path


def main(argv: list[str] | None = None) -> int:
    """Estimate national elasticities for India and Pakistan and write the summary JSON."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--india", required=True, help="India household parquet")
    parser.add_argument("--pakistan", required=True, help="Pakistan household parquet")
    parser.add_argument(
        "--out",
        default="outputs/elasticities_national.json",
        help="summary JSON (relative paths resolve against research/household-demand/)",
    )
    parser.add_argument("--draws", type=int, default=DEFAULT_DRAWS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    out = _resolve_here(args.out)
    countries = {}
    for name, path, groups in (
        ("India", args.india, INDIA_GROUPS),
        ("Pakistan", args.pakistan, PAKISTAN_GROUPS),
    ):
        started = time.perf_counter()
        table = pd.read_parquet(path)
        est = estimate_elasticities(
            table, list(groups), cluster="psu", seed=args.seed, draws=args.draws
        )
        summary = est.to_dict()
        summary["runtime_seconds"] = round(time.perf_counter() - started, 1)
        countries[name] = summary
        print(
            f"{name}: {summary['n_households']} households, {summary['runtime_seconds']} s"
        )
    payload = {
        "status": "DIAGNOSTIC",
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "level": "national",
        "seed": args.seed,
        "method": (
            "Deaton unit-value method, simplified: cell price is the weighted mean market "
            "unit value per state x district (India) or PR-code area (Pakistan) x sector; "
            "WLS of log budget share on log cell prices of all groups, log MPCE, log "
            "household size and state fixed effects, purchasers only; own-price b_gg - 1, "
            "cross-price b_gk, income 1 + c_g"
        ),
        "nso_rule": "district cells feed estimation only; results are national aggregates",
        "elasticity_type": "Marshallian, conditional on purchase",
        "countries": countries,
    }
    _write_json(out, payload)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
