"""Driver bands (GDP per capita, population, urban share), CPI deflators and price scenarios.

Sources (recorded in ``inputs/manifest.csv``; files stay outside the repository):

- IMF World Economic Outlook, October 2026, DataMapper API JSON: ``NGDPDPC``
  (GDP per capita, current US dollars), ``NGDP_RPCH`` (real GDP growth),
  ``LP`` (population, IMF basis) and ``PCPIPCH`` (average CPI inflation).
- UN World Population Prospects 2024, demographic indicators CSV, Medium
  variant and other variants (``TPopulation1July``, thousands).
- UN World Urbanization Prospects 2018, file F21 (annual percentage urban,
  national definitions), read from the official Excel zip.

Bands (``low``, ``mid``, ``high`` approximate the 10th, 50th and 90th percentiles):

- ``gdp_per_capita_usd_2025``: mid starts at IMF NGDPDPC for 2025 (current
  dollars of 2025 equal 2025 dollars) and grows at IMF real per capita growth,
  ``(1 + NGDP_RPCH / 100) / (LP_t / LP_t-1) - 1``. IMF projections end in
  2031; 2032 to 2035 hold the 2031 rate (``extended`` years). The real
  exchange rate is held at its 2025 level. Low and high are
  ``mid * exp(-/+ 1.2816 * sigma * sqrt(h))``, with ``h`` years after 2025 and
  ``sigma`` the standard deviation of realised annual log real per capita
  growth over 2000 to 2019 in the same IMF series (a random walk around the
  IMF path; 2020 and 2021 are left out as pandemic years).
- ``population``: WPP 2024 Lower 80 PI, Medium and Upper 80 PI.
- ``urban_share``: WUP 2018 has one projection, so low, mid and high are equal.
  The WUP 2025 revision uses the Degree of Urbanisation (India about 80
  percent "cities and towns"), which does not match the census urban
  definition behind the HCES and HIES sector codes; it was downloaded and is
  not used.

CPI index: ``index_2025`` chains IMF PCPIPCH to 1.0 in 2025. IMF reports India
on a fiscal-year basis (April to March); the year label is used as published.

Scenarios (decision 11), ``scenario_paths``: the 2026 plant-to-conventional
price ratio ``r0`` declines by ``ai_decline`` a year (AI cost-decline path);
the parity path falls geometrically from ``r0`` to 1.0 at ``parity_year`` and
stays at 1.0; with both, the lower ratio applies each year.

Run from the library root:

    python research/household-demand/drivers.py --out research/household-demand/outputs/drivers.json
"""

from __future__ import annotations

import argparse
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "BAND_Z",
    "cpi_index",
    "example_base",
    "load_drivers",
    "scenario_paths",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]
WORKSPACE_ROOT = LIBRARY_ROOT.parent
MANIFEST = HERE / "inputs" / "manifest.csv"

COUNTRIES = {"IND": "India", "PAK": "Pakistan"}
YEARS = list(range(2026, 2036))
BASE_YEAR = 2025
IMF_LAST_YEAR = 2031
SIGMA_YEARS = (2000, 2019)
BAND_Z = 1.2815515655446004  # standard normal 90th percentile
WPP_BANDS = {"low": "Lower 80 PI", "mid": "Medium", "high": "Upper 80 PI"}
WUP_MEMBER = "WUP2018-F21-Proportion_Urban_Annual.xls"

INPUT_IDS = {
    "ngdp_rpch": "imf_weo_2026_10_ngdp_rpch",
    "lp": "imf_weo_2026_10_lp",
    "ngdpdpc": "imf_weo_2026_10_ngdpdpc",
    "pcpipch": "imf_weo_2026_10_pcpipch",
    "wpp_medium": "un_wpp_2024_medium",
    "wpp_other": "un_wpp_2024_other_variants",
    "wup": "un_wup_2018_excel_zip",
}


def _paths(manifest: Path, root: Path | None) -> dict[str, Path]:
    """Map each needed input to its file, resolved against the workspace root."""
    table = pd.read_csv(manifest, dtype=str)
    stored = dict(zip(table["input_id"], table["stored_at"]))
    base = Path(root) if root is not None else WORKSPACE_ROOT
    out = {}
    for key, input_id in INPUT_IDS.items():
        if input_id not in stored:
            raise KeyError(f"manifest has no row {input_id}")
        out[key] = base / stored[input_id].split(" (")[0]
    return out


def _imf(path: Path, code: str) -> dict[str, dict[int, float]]:
    data = json.loads(Path(path).read_text())["values"][code]
    return {
        iso: {int(y): float(v) for y, v in data[iso].items() if v is not None}
        for iso in COUNTRIES
        if iso in data
    }


def _gdp_bands(paths: dict[str, Path]) -> pd.DataFrame:
    growth = _imf(paths["ngdp_rpch"], "NGDP_RPCH")
    pop = _imf(paths["lp"], "LP")
    level = _imf(paths["ngdpdpc"], "NGDPDPC")
    rows = []
    for iso, country in COUNTRIES.items():
        g, lp = growth[iso], pop[iso]
        pc_growth = {
            year: (1 + g[year] / 100) / (lp[year] / lp[year - 1]) - 1
            for year in g
            if year in lp and year - 1 in lp
        }
        hist = [
            math.log1p(pc_growth[y]) for y in range(SIGMA_YEARS[0], SIGMA_YEARS[1] + 1)
        ]
        sigma = float(np.std(hist, ddof=1))
        value = level[iso][BASE_YEAR]
        for year in YEARS:
            rate = pc_growth[min(year, IMF_LAST_YEAR)]
            value *= 1 + rate
            h = year - BASE_YEAR
            spread = BAND_Z * sigma * math.sqrt(h)
            for band, factor in (("low", -spread), ("mid", 0.0), ("high", spread)):
                rows.append(
                    {
                        "country": country,
                        "year": year,
                        "variable": "gdp_per_capita_usd_2025",
                        "band": band,
                        "value": value * math.exp(factor),
                        "sigma": sigma,
                        "extended": year > IMF_LAST_YEAR,
                    }
                )
    return pd.DataFrame(rows)


def _population_bands(paths: dict[str, Path]) -> pd.DataFrame:
    cols = ["ISO3_code", "Time", "Variant", "TPopulation1July"]
    frames = [
        pd.read_csv(paths[key], usecols=cols, low_memory=False)
        for key in ("wpp_medium", "wpp_other")
    ]
    wpp = pd.concat(frames, ignore_index=True)
    wpp = wpp[wpp.ISO3_code.isin(COUNTRIES) & wpp.Time.isin(YEARS)]
    rows = []
    for band, variant in WPP_BANDS.items():
        part = wpp[wpp.Variant == variant]
        for rec in part.itertuples(index=False):
            rows.append(
                {
                    "country": COUNTRIES[rec.ISO3_code],
                    "year": int(rec.Time),
                    "variable": "population",
                    "band": band,
                    "value": float(rec.TPopulation1July) * 1000.0,
                }
            )
    return pd.DataFrame(rows)


def _read_wup(path: Path) -> pd.DataFrame:
    """Return ``country, year, urban_share`` (fraction) from the WUP 2018 zip, file F21."""
    with zipfile.ZipFile(path) as archive:
        raw = archive.read(WUP_MEMBER)
    sheet = pd.read_excel(io.BytesIO(raw), sheet_name="Data", header=None)
    header_row = sheet.index[sheet.iloc[:, 0].astype(str).str.strip() == "Index"][0]
    header = sheet.iloc[header_row].tolist()
    body = sheet.iloc[header_row + 1 :]
    names = body.iloc[:, 1].astype(str).str.strip()
    rows = []
    for country in COUNTRIES.values():
        record = body[names == country]
        if len(record) != 1:
            raise ValueError(f"WUP F21 has {len(record)} rows for {country}")
        for col, label in enumerate(header):
            try:
                year = int(float(label))
            except (TypeError, ValueError):
                continue
            rows.append(
                {
                    "country": country,
                    "year": year,
                    "urban_share": float(record.iloc[0, col]) / 100.0,
                }
            )
    return pd.DataFrame(rows)


def _urban_bands(paths: dict[str, Path]) -> pd.DataFrame:
    wup = _read_wup(paths["wup"])
    wup = wup[wup.year.isin(YEARS)]
    rows = []
    for rec in wup.itertuples(index=False):
        for band in ("low", "mid", "high"):
            rows.append(
                {
                    "country": rec.country,
                    "year": int(rec.year),
                    "variable": "urban_share",
                    "band": band,
                    "value": float(rec.urban_share),
                }
            )
    return pd.DataFrame(rows)


def load_drivers(manifest: Path, root: Path | None = None) -> pd.DataFrame:
    """Return ``country, year, variable, band, value`` for the three drivers."""
    paths = _paths(Path(manifest), root)
    frames = [_gdp_bands(paths), _population_bands(paths), _urban_bands(paths)]
    cols = ["country", "year", "variable", "band", "value"]
    out = pd.concat([f[cols] for f in frames], ignore_index=True)
    return out.sort_values(["variable", "country", "year", "band"]).reset_index(
        drop=True
    )


def cpi_index(manifest: Path, root: Path | None = None) -> pd.DataFrame:
    """Return ``country, year, index_2025`` chained from IMF PCPIPCH (2025 = 1)."""
    paths = _paths(Path(manifest), root)
    infl = _imf(paths["pcpipch"], "PCPIPCH")
    rows = []
    for iso, country in COUNTRIES.items():
        years = sorted(infl[iso])
        index = {BASE_YEAR: 1.0}
        for year in (y for y in years if y > BASE_YEAR):
            index[year] = index[year - 1] * (1 + infl[iso][year] / 100)
        for year in sorted((y for y in years if y < BASE_YEAR), reverse=True):
            index[year] = index[year + 1] / (1 + infl[iso][year + 1] / 100)
        for year in range(2020, IMF_LAST_YEAR + 1):
            rows.append({"country": country, "year": year, "index_2025": index[year]})
    return pd.DataFrame(rows)


def example_base() -> pd.DataFrame:
    """Test helper: India 2026 to 2035 with price_ratio 2.0 in 2026."""
    ratio = [2.0] + [np.nan] * (len(YEARS) - 1)
    return pd.DataFrame({"country": "India", "year": YEARS, "price_ratio": ratio})


def scenario_paths(
    base: pd.DataFrame, ai_decline: float, parity_year: int | None
) -> pd.DataFrame:
    """Add ``price_ratio`` by year from the first-year ratio, AI decline and parity."""
    if not 0.0 <= ai_decline < 1.0:
        raise ValueError("ai_decline must be in [0, 1)")
    out = []
    for country, frame in base.groupby("country", sort=False):
        frame = frame.sort_values("year").copy()
        start = int(frame["year"].iloc[0])
        r0 = float(frame["price_ratio"].iloc[0])
        if not np.isfinite(r0) or r0 <= 0:
            raise ValueError(f"{country}: first-year price_ratio must be positive")
        h = frame["year"].to_numpy() - start
        path = r0 * (1.0 - ai_decline) ** h
        if parity_year is not None:
            if parity_year <= start:
                raise ValueError("parity_year must follow the first year")
            if r0 > 1.0:
                frac = np.clip(h / (parity_year - start), 0.0, 1.0)
                parity = np.where(
                    frame["year"].to_numpy() >= parity_year, 1.0, r0 ** (1.0 - frac)
                )
                path = np.minimum(path, parity)
        frame["price_ratio"] = path
        out.append(frame)
    return pd.concat(out, ignore_index=True)


def _band_table(drivers: pd.DataFrame) -> dict:
    out: dict = {}
    for (variable, country), part in drivers.groupby(["variable", "country"]):
        wide = part.pivot(index="year", columns="band", values="value")
        out.setdefault(variable, {})[country] = {
            str(int(y)): {b: float(wide.loc[y, b]) for b in ("low", "mid", "high")}
            for y in wide.index
        }
    return out


def build_output(manifest: Path = MANIFEST) -> dict:
    drv = load_drivers(manifest)
    paths = _paths(manifest, None)
    gdp = _gdp_bands(paths)
    sigma = gdp.groupby("country")["sigma"].first().to_dict()
    cpi = cpi_index(manifest)
    return {
        "status": "DIAGNOSTIC",
        "years": YEARS,
        "bands": _band_table(drv),
        "band_methods": {
            "gdp_per_capita_usd_2025": {
                "source": "IMF World Economic Outlook, October 2026 (DataMapper API): NGDPDPC, NGDP_RPCH, LP",
                "mid": (
                    "NGDPDPC 2025 grown at IMF real per capita growth (1 + NGDP_RPCH/100) / "
                    "(LP_t / LP_t-1) - 1; 2032 to 2035 hold the 2031 rate; real exchange "
                    "rate fixed at 2025"
                ),
                "low_high": (
                    "mid * exp(-/+ 1.2816 * sigma * sqrt(years after 2025)); sigma = standard "
                    "deviation of realised annual log real per capita growth 2000 to 2019"
                ),
                "sigma": sigma,
                "extended_years": [y for y in YEARS if y > IMF_LAST_YEAR],
                "note": "IMF reports India on a fiscal-year basis",
            },
            "population": {
                "source": "UN World Population Prospects 2024, TPopulation1July",
                "bands": WPP_BANDS,
                "note": (
                    "IMF LP (used only for per capita growth) differs from WPP; Pakistan "
                    "2025: IMF 240.49 million, WPP 255.22 million"
                ),
            },
            "urban_share": {
                "source": "UN World Urbanization Prospects 2018, F21 annual percentage urban (national definitions)",
                "bands": "low = mid = high: WUP 2018 publishes one projection; no band",
                "not_used": (
                    "WUP 2025 F02 (Degree of Urbanisation, cities and towns) uses a "
                    "different urban definition from the HCES and HIES sector codes"
                ),
            },
        },
        "cpi_index_2025": {
            c: {str(int(r.year)): float(r.index_2025) for r in part.itertuples()}
            for c, part in cpi.groupby("country")
        },
        "cpi_source": "IMF WEO October 2026 PCPIPCH, chained to 1.0 in 2025",
        "scenarios": {
            "ai_cost_decline": {
                "rule": "price_ratio_t = r0 * (1 - ai_decline) ** (t - 2026)",
                "baseline_ai_decline": 0.0,
                "sourced_rate": None,
                "note": (
                    "no published rate for AI-driven plant-based cost decline was found; "
                    "a non-zero rate needs an author ruling before Task 8 uses it"
                ),
            },
            "price_parity": {
                "rule": "geometric fall from r0 in 2026 to 1.0 at parity_year, then 1.0",
                "parity_years": [2030, 2035],
                "parity_years_basis": "the protocol forecast years",
            },
            "combination": "with both, the lower ratio applies each year",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=HERE / "outputs" / "drivers.json")
    args = parser.parse_args(argv)
    out = build_output(args.manifest)
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
