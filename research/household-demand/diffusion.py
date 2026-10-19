"""Bass diffusion for plant-based adoption: fit, path, analogs and the US stress series.

The Bass model gives cumulative adopters at ``t`` years after launch:

    N(t) = m * (1 - exp(-(p + q) t)) / (1 + (q / p) exp(-(p + q) t)),  t >= 0

and ``N(t) = 0`` before launch. ``fit_bass`` searches a grid of ``(p, q)``,
solves ``m`` in closed form for each pair (least squares, ``m = F.y / F.F``),
then refines the grid three times around the best pair.

Analogs (rulings R8, R9). The protocol registers three analog candidates.
Task 7 checked each for a public national annual series of at least 5 points.
None passed (``ANALOGS`` records each reason), so the main diffusion uses the
registered prior ``p = 0.03``, ``q = 0.38`` (Sultan, Farley and Lehmann 1990)
with launch years India 2019 and Pakistan 2023 (both assumptions in the
protocol). ``m`` is the adoption ceiling that Task 8 sets from conversion and
the addressable segment.

US stress test (decision 14). ``US_STRESS_SERIES`` holds GFI US plant-based
retail dollar sales (SPINS), 2018 to 2025. Each value is the first figure GFI
published for that calendar year, with its document and locator; later GFI
restatements are kept in ``US_RESTATEMENTS``. GFI revised its SPINS categories
between editions, so the series mixes vintages. ``fit_bass_with_launch`` fits
the Bass curve to the sales path (sales stand in for adopters) over candidate
launch years and keeps the best fit. The result is a sensitivity row only.

Run from the library root:

    python research/household-demand/diffusion.py --out research/household-demand/outputs/diffusion.json
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

import numpy as np

__all__ = [
    "ANALOGS",
    "US_RESTATEMENTS",
    "US_STRESS_SERIES",
    "bass_path",
    "fit_bass",
    "fit_bass_with_launch",
    "main_parameters",
]

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "protocol.json"

_P_GRID = np.geomspace(1e-4, 0.5, 120)
_Q_GRID = np.linspace(0.0, 1.5, 151)
_REFINEMENTS = 3


def _bass_share(p: np.ndarray, q: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Cumulative adoption share F(t); broadcasts over p, q and t."""
    t = np.clip(t, 0.0, None)
    decay = np.exp(-(p + q) * t)
    return (1.0 - decay) / (1.0 + (q / p) * decay)


def bass_path(p: float, q: float, m: float, years: np.ndarray) -> np.ndarray:
    """Return cumulative adopters ``m * F(t)``; ``years`` are years since launch."""
    if p <= 0 or q < 0 or m < 0:
        raise ValueError("Bass parameters need p > 0, q >= 0 and m >= 0")
    t = np.asarray(years, dtype=float)
    return m * _bass_share(np.float64(p), np.float64(q), t)


def _best_on_grid(
    p_grid: np.ndarray, q_grid: np.ndarray, t: np.ndarray, y: np.ndarray
) -> tuple[float, float, float, float]:
    """Return ``(p, q, m, sse)`` minimising squared error over the grid."""
    share = _bass_share(p_grid[:, None, None], q_grid[None, :, None], t[None, None, :])
    denom = np.einsum("ijk,ijk->ij", share, share)
    numer = np.einsum("ijk,k->ij", share, y)
    with np.errstate(divide="ignore", invalid="ignore"):
        m = np.where(denom > 0, numer / denom, 0.0)
    m = np.clip(m, 0.0, None)
    resid = y[None, None, :] - m[:, :, None] * share
    sse = np.einsum("ijk,ijk->ij", resid, resid)
    i, j = np.unravel_index(np.nanargmin(sse), sse.shape)
    return float(p_grid[i]), float(q_grid[j]), float(m[i, j]), float(sse[i, j])


def _fit(t: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    p, q, m, sse = _best_on_grid(_P_GRID, _Q_GRID, t, y)
    p_step = np.log(_P_GRID[1] / _P_GRID[0])
    q_step = _Q_GRID[1] - _Q_GRID[0]
    for _ in range(_REFINEMENTS):
        p_grid = np.exp(np.linspace(np.log(p) - 2 * p_step, np.log(p) + 2 * p_step, 41))
        q_grid = np.clip(np.linspace(q - 2 * q_step, q + 2 * q_step, 41), 0.0, None)
        p, q, m, sse = _best_on_grid(p_grid, q_grid, t, y)
        p_step /= 10.0
        q_step /= 10.0
    return p, q, m, sse


def _clean(years: np.ndarray, adopters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(years, dtype=float)
    y = np.asarray(adopters, dtype=float)
    if t.shape != y.shape:
        raise ValueError("years and adopters must have the same shape")
    keep = np.isfinite(t) & np.isfinite(y)
    t, y = t[keep], y[keep]
    if len(t) < 3:
        raise ValueError("Bass fit needs at least 3 non-missing points")
    return t, y


def fit_bass(years: np.ndarray, adopters: np.ndarray) -> tuple[float, float, float]:
    """Fit ``(p, q, m)`` by grid least squares; missing points are dropped."""
    t, y = _clean(years, adopters)
    p, q, m, _ = _fit(t, y)
    return p, q, m


def fit_bass_with_launch(
    calendar_years: np.ndarray, values: np.ndarray, launch_years: Iterable[int]
) -> dict:
    """Fit Bass for each candidate launch year and keep the lowest squared error.

    Every observed year must fall after the launch year, so a candidate at or
    after the first observed year is skipped.
    """
    cal, y = _clean(calendar_years, values)
    best: dict | None = None
    for launch in launch_years:
        t = cal - float(launch)
        if t.min() <= 0:
            continue
        p, q, m, sse = _fit(t, y)
        if best is None or sse < best["sse"]:
            best = {"launch_year": int(launch), "p": p, "q": q, "m": m, "sse": sse}
    if best is None:
        raise ValueError("no candidate launch year precedes the first observation")
    total = float(np.sum((y - y.mean()) ** 2))
    best["r_squared"] = 1.0 - best["sse"] / total if total > 0 else None
    best["n_points"] = len(y)
    return best


# GFI US plant-based retail dollar sales, all categories (SPINS). First figure
# GFI published for each calendar year.
US_STRESS_SERIES: dict[int, dict] = {
    2018: {
        "value_usd": 4.5e9,
        "source": "GFI, Plant-Based Food Retail Market Overview (webinar slides, April 2020)",
        "url": "https://gfi.org/images/uploads/2020/04/GFI-Webinar-Plant-Based-Food-Retail-Market-Overview.pdf",
        "locator": "page 10, chart Total U.S. plant-based food market, bar 2018 ($4.5b)",
        "data_note": "SPINSscan Natural and Specialty Gourmet and Conventional Multi Outlet, 104 weeks ending 29 December 2019",
    },
    2019: {
        "value_usd": 5.0e9,
        "source": "GFI, Plant-Based Food Retail Market Overview (webinar slides, April 2020)",
        "url": "https://gfi.org/images/uploads/2020/04/GFI-Webinar-Plant-Based-Food-Retail-Market-Overview.pdf",
        "locator": "page 10, chart Total U.S. plant-based food market, bar 2019 ($5.0b); page 67 key takeaway 1",
        "data_note": "same SPINS base as 2018",
    },
    2020: {
        "value_usd": 7.0e9,
        "source": "GFI and PBFA press release, 6 April 2021, Plant-based food retail sales grow 27 percent to reach $7 billion in 2020",
        "url": "https://gfi.org/press/plant-based-food-retail-sales-grow-27-percent-to-reach-7-billion-in-2020/",
        "locator": "body: total plant-based market value of $7 billion; 52 weeks ending 27 December 2020",
        "data_note": "SPINS custom plant-based categories",
    },
    2021: {
        "value_usd": 7.4e9,
        "source": "GFI and PBFA press release, 24 March 2022, U.S. plant-based food retail sales hit $7.4 billion",
        "url": "https://gfi.org/press/u-s-plant-based-food-retail-sales-hit-7-4-billion/",
        "locator": "body: total plant-based market value of an all-time high of $7.4 billion; also GFI 2021 U.S. retail market insights, page 2",
        "data_note": "SPINS Natural Enhanced and Conventional Multi Outlet",
    },
    2022: {
        "value_usd": 8.0e9,
        "source": "GFI, 2022 State of the Industry Report: Plant-based meat, seafood, eggs, and dairy",
        "url": "https://gfi.org/wp-content/uploads/2023/01/2022-Plant-Based-State-of-the-Industry-Report-1-1.pdf",
        "locator": "Sales summary: Total U.S. retail plant-based food dollar sales reached $8 billion in 2022",
        "data_note": "SPINS data released by GFI and PBFA",
    },
    2023: {
        "value_usd": 8.1e9,
        "source": "GFI, 2023 State of the Industry Report: Plant-based meat, seafood, eggs, and dairy",
        "url": "https://gfi.org/wp-content/uploads/2024/04/State-of-the-Industry-report_Plant-based_2023.pdf",
        "locator": "Sales, U.S. retail sales overview: the 2023 U.S. retail plant-based food market was worth $8.1 billion",
        "data_note": "SPINS data released by GFI and PBFA",
    },
    2024: {
        "value_usd": 8.1e9,
        "source": "GFI, 2024 State of the Industry: Plant-based meat, seafood, eggs, dairy, and ingredients",
        "url": "https://gfi.org/wp-content/uploads/2025/04/2024-State-of-the-Industry_Plant-based_GFI24005.pdf",
        "locator": "Sales, Overview: U.S. sales: plant-based food sales declined slightly to $8.1 billion",
        "data_note": "SPINS data",
    },
    2025: {
        "value_usd": 7.9e9,
        "source": "GFI, Plant-based retail market overview (web page)",
        "url": "https://gfi.org/marketresearch/",
        "locator": "section Overall plant-based foods: the 2025 U.S. retail plant-based food market was worth $7.9 billion",
        "data_note": "SPINS point-of-sale data, 52 weeks ending 30 November 2025",
    },
}

US_RESTATEMENTS: list[dict] = [
    {
        "year": 2020,
        "value_usd": 6.9e9,
        "source": "GFI, 2021 U.S. retail market insights: Plant-based foods",
        "locator": "page 2: worth $7.4 billion, up from $6.9 billion in 2020",
    },
    {
        "year": 2022,
        "value_usd": 8.2e9,
        "source": "GFI, 2023 State of the Industry Report",
        "locator": "Sales: $8.1 billion in 2023, a slight decline from $8.2 billion in 2022",
    },
    {
        "year": 2022,
        "value_usd": 8.5e9,
        "source": "GFI, 2024 State of the Industry",
        "locator": "Sales, Overview: By 2022, the market had more than doubled to $8.5 billion",
    },
]

ANALOGS: list[dict] = [
    {
        "id": "packaged_liquid_milk",
        "countries": ["India", "Pakistan"],
        "status": "DROPPED",
        "reason": (
            "No public national packaged-milk series. India: NDDB annual reports give "
            "liquid milk sales by dairy cooperatives (lakh litres per day), which excludes "
            "private dairies, so it is not national packaged volume; the reports were seen "
            "as search excerpts only, not opened. Packaged milk in India dates from the "
            "1970s, so a 2017 to 2025 segment cannot identify a launch-anchored p. "
            "Pakistan: no Economic Survey or official series splits packaged from loose "
            "milk; only single-year industry estimates (3 to 5 percent formal share) and "
            "paid Euromonitor tables were found."
        ),
        "evidence": [
            "https://nddb.coop/sites/default/files/pdfs/NDDB_AR_2023_090124_Eng.pdf (search excerpt)",
            "https://www.fao.org/4/i0588e/i0588e07.htm (formal channel share estimate)",
            "https://www.euromonitor.com/drinking-milk-products-in-pakistan/report (paid)",
        ],
    },
    {
        "id": "soya_chunks",
        "countries": ["India"],
        "status": "DROPPED",
        "reason": (
            "NSS and HCES rounds give item 152 at most three points (2011-12, 2022-23, "
            "2023-24), and two need the author's microdata.gov.in registration. The "
            "protocol requires at least 5 annual points."
        ),
        "evidence": ["protocol.json analogs.candidates soya_chunks"],
    },
    {
        "id": "branded_rtc_chicken",
        "countries": ["India", "Pakistan"],
        "status": "DROPPED",
        "reason": (
            "No public national series. Searches found only paid market reports "
            "(GlobalData, IMARC, Ken Research) and firm-level figures; no listed "
            "processor reports a national branded ready-to-cook chicken series. "
            "Pakistan: no public filing or trade series for branded frozen chicken."
        ),
        "evidence": [
            "https://www.globaldata.com/store/?p=4625599 (paid)",
            "https://www.imarcgroup.com/india-ready-to-cook-food-market (all ready-to-cook food, paid)",
        ],
    },
]


def main_parameters(analogs: list[dict], protocol_path: Path = PROTOCOL) -> dict:
    """Return the main diffusion parameters: a kept analog fit, else the prior."""
    kept = [a for a in analogs if a["status"] == "KEPT"]
    if kept:
        raise NotImplementedError("analog fits are not used: no analog survived Task 7")
    priors = json.loads(Path(protocol_path).read_text())["priors"]
    prior = priors["bass_fallback"]
    return {
        "basis": "registered_prior",
        "p": prior["p"],
        "q": prior["q"],
        "source": prior["source"],
        "launch_year": {c: v["year"] for c, v in priors["bass_launch_year"].items()},
        "launch_year_basis": {
            c: v["basis"] for c, v in priors["bass_launch_year"].items()
        },
        "m": "set in Task 8 from conversion and the addressable segment",
    }


def us_stress_fit(launch_years: Iterable[int] = range(1990, 2018)) -> dict:
    """Fit the Bass curve to the GFI US sales path over candidate launch years."""
    years = np.array(sorted(US_STRESS_SERIES), dtype=float)
    values = np.array(
        [
            (
                np.nan
                if US_STRESS_SERIES[int(y)]["value_usd"] is None
                else US_STRESS_SERIES[int(y)]["value_usd"]
            )
            for y in years
        ]
    )
    fit = fit_bass_with_launch(years, values, launch_years)
    fit["candidate_launch_years"] = [min(launch_years), max(launch_years)]
    return fit


def build_output() -> dict:
    stress = us_stress_fit()
    return {
        "status": "DIAGNOSTIC",
        "model": "N(t) = m (1 - exp(-(p+q) t)) / (1 + (q/p) exp(-(p+q) t)), t = years since launch",
        "fit_method": (
            "grid least squares over p (120 log-spaced values, 1e-4 to 0.5) and q "
            "(151 values, 0 to 1.5), m solved in closed form, three refinements"
        ),
        "main": main_parameters(ANALOGS),
        "analogs": ANALOGS,
        "analog_rule": "protocol analogs.rule: a public national annual series of at least 5 points",
        "us_stress": {
            "role": "sensitivity only (decision 14); sales in USD stand in for adopters",
            "series_rule": "first figure GFI published for each calendar year; later restatements listed separately",
            "series": {str(k): v for k, v in US_STRESS_SERIES.items()},
            "restatements": US_RESTATEMENTS,
            "vintage_note": (
                "GFI changed SPINS category definitions between editions; values from "
                "different editions are not on one consistent base"
            ),
            "fit": stress,
            "fit_note": (
                "the launch year is fitted, not observed; p and the launch year trade off, "
                "so the shape (q, m) carries the stress information"
            ),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "outputs" / "diffusion.json")
    args = parser.parse_args(argv)
    out = build_output()
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
