"""Plant-based price snapshot: normalisation, state reference prices and price ratios.

Snapshot (decisions 7, 20, 21). One pass over public product pages, 19
October 2026 UTC, plant-based meat (``plant_meat``) and dairy alternatives
(``dairy_alt``) only. Raw captures and the observation table stay local in
``OUTPUTS/Household Demand 2026-10/prices-raw/``; the repository gets the
summary only (``outputs/prices_summary.json``). Each observation records
country, city, ``city_basis`` (``city_store`` for a price tied to one city,
``national_online`` for one online price list), retailer, product, brand,
category, pack size, price in local currency, protein per 100 g where the page
shows it, capture time and URL.

Normalisation: ``price_per_kg_local = price_local / pack_size_g * 1000`` and
``price_per_kg_protein_local = price_per_kg_local * 100 / protein_g_per_100g``.
Liquid packs in millilitres count 1 ml as 1 g. Missing protein stays missing.

Reference prices (decision 29, rulings R15, R16): chicken and milk unit
values come from the household tables (market purchases only), as weighted
state or province means with ``multiplier`` weights. A cell with fewer than
30 households is missing; its count is kept.

Price ratio: the country median plant price per kg (all cities and retailers
of a category pooled) divided by each state's reference unit value. Optional
deflators bring both to 2025 prices: plant prices captured in 2026 are divided
by the 2026 CPI index; HCES 2023-24 unit values (August 2023 to July 2024)
are multiplied by 1 / (5/12 CPI 2023 + 7/12 CPI 2024); HIES 2024-25 unit values
(fiscal year label, July 2024 to June 2025 assumed) by 1 / (CPI 2024 / 2 + CPI 2025 / 2).
Rows of different status never mix in one ratio.

Placeholders (decision 19, ruling R1). ``synthetic/plant_prices.csv`` holds one
placeholder row per country, city and category. Each placeholder price is the
US plant-to-conventional price ratio (GFI 2025, ``outputs/us_calibration.json``)
times the city's state reference unit value; protein is left missing. Results
built from placeholders go to ``synthetic/outputs/``, never ``outputs/``.

Run from the library root:

    python research/household-demand/prices.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "CATEGORIES",
    "CITIES",
    "example_rows",
    "load_synthetic",
    "normalise_prices",
    "price_ratio",
    "state_unit_values",
    "summarise",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]
WORKSPACE_ROOT = LIBRARY_ROOT.parent
LOCAL = WORKSPACE_ROOT / "OUTPUTS" / "Household Demand 2026-10"
OBSERVATIONS = LOCAL / "prices-raw" / "observations.csv"
SYNTHETIC_CSV = HERE / "synthetic" / "plant_prices.csv"
US_CALIBRATION = HERE / "outputs" / "us_calibration.json"
MIN_CELL_HOUSEHOLDS = 30

CATEGORIES = ("plant_meat", "dairy_alt")
REFERENCE_GROUP = {"plant_meat": "chicken", "dairy_alt": "milk"}
CURRENCY = {"India": "INR", "Pakistan": "PKR"}

# Decision 7 cities with the household-table state or province code.
# India: NSS state codes (Delhi 7, West Bengal 19, Maharashtra 27, Karnataka 29,
# Tamil Nadu 33, Telangana 36). Pakistan: HIES province codes (Punjab 2,
# Sindh 3). Islamabad Capital Territory has no province cell in the HIES table
# and the tier-2 city was never selected, so both carry no state.
CITIES: tuple[tuple[str, str, int | None], ...] = (
    ("India", "Delhi NCR", 7),
    ("India", "Mumbai", 27),
    ("India", "Bengaluru", 29),
    ("India", "Hyderabad", 36),
    ("India", "Chennai", 33),
    ("India", "Kolkata", 19),
    ("India", "Pune", 27),
    ("India", "Tier-2 city (not selected)", None),
    ("Pakistan", "Karachi", 3),
    ("Pakistan", "Lahore", 2),
    ("Pakistan", "Islamabad", None),
)

REQUIRED = (
    "country",
    "city",
    "retailer",
    "product",
    "category",
    "pack_size_g",
    "price_local",
)
OUTPUT_COLUMNS = [
    "country",
    "city",
    "city_basis",
    "retailer",
    "product",
    "brand",
    "category",
    "pack_size_g",
    "price_local",
    "currency",
    "protein_g_per_100g",
    "price_per_kg_local",
    "price_per_kg_protein_local",
    "status",
]


def example_rows() -> pd.DataFrame:
    """Test helper: one 200 g pack at INR 150 with 20 g protein per 100 g."""
    return pd.DataFrame(
        {
            "country": ["India"],
            "city": ["Mumbai"],
            "city_basis": ["city_store"],
            "retailer": ["Example retailer"],
            "product": ["Example plant-based nuggets 200 g"],
            "brand": ["Example"],
            "category": ["plant_meat"],
            "pack_size_g": [200.0],
            "price_local": [150.0],
            "currency": ["INR"],
            "protein_g_per_100g": [20.0],
            "status": ["DIAGNOSTIC"],
        }
    )


def load_synthetic(path: Path = SYNTHETIC_CSV) -> pd.DataFrame:
    """Read the placeholder price rows (every row flagged)."""
    return pd.read_csv(path)


def normalise_prices(observations: pd.DataFrame) -> pd.DataFrame:
    """Return price per kg and per kg protein for each observation."""
    obs = observations.copy()
    missing = [c for c in REQUIRED if c not in obs.columns]
    if missing:
        raise ValueError(f"observations lack columns {missing}")
    bad = sorted(set(obs["category"]) - set(CATEGORIES))
    if bad:
        raise ValueError(f"unknown category {bad}; expected {CATEGORIES}")
    pack = pd.to_numeric(obs["pack_size_g"], errors="coerce")
    price = pd.to_numeric(obs["price_local"], errors="coerce")
    if not ((pack > 0) & (price > 0)).all():
        raise ValueError("pack_size_g and price_local must be positive numbers")
    if "protein_g_per_100g" in obs.columns:
        protein = pd.to_numeric(obs["protein_g_per_100g"], errors="coerce")
    else:
        protein = pd.Series(np.nan, index=obs.index)
    if (protein <= 0).any():
        raise ValueError("protein_g_per_100g must be positive or missing")
    for column, default in (
        ("status", "DIAGNOSTIC"),
        ("city_basis", "city_store"),
        ("brand", None),
    ):
        if column not in obs.columns:
            obs[column] = default
    if "currency" not in obs.columns:
        obs["currency"] = obs["country"].map(CURRENCY)
    obs["pack_size_g"] = pack.astype(float)
    obs["price_local"] = price.astype(float)
    obs["protein_g_per_100g"] = protein.astype(float)
    obs["price_per_kg_local"] = price / pack * 1000.0
    obs["price_per_kg_protein_local"] = obs["price_per_kg_local"] * 100.0 / protein
    return obs[OUTPUT_COLUMNS].reset_index(drop=True)


def state_unit_values(
    table: pd.DataFrame,
    country: str,
    group: str,
    min_households: int = MIN_CELL_HOUSEHOLDS,
) -> pd.DataFrame:
    """Weighted state means of ``unit_value_{group}``; cells under the minimum are missing."""
    column = f"unit_value_{group}"
    rows = []
    for state, frame in table.groupby("state", sort=True):
        present = frame[column].notna()
        n = int(present.sum())
        value = np.nan
        if n >= min_households:
            w = frame.loc[present, "multiplier"].astype(float)
            value = float((frame.loc[present, column] * w).sum() / w.sum())
        rows.append(
            {
                "country": country,
                "state": int(state),
                "group": group,
                "unit_value_local": value,
                "n_households": n,
            }
        )
    return pd.DataFrame(rows)


def price_ratio(
    plant: pd.DataFrame,
    chicken_unit_values: pd.DataFrame,
    category: str = "plant_meat",
    plant_deflator: dict[str, float] | None = None,
    reference_deflator: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Country median plant price per kg over each state's reference unit value."""
    if category not in CATEGORIES:
        raise ValueError(f"unknown category {category}")
    rows = plant[plant["category"] == category]
    out = []
    for rec in chicken_unit_values.itertuples(index=False):
        mine = rows[rows["country"] == rec.country]
        statuses = set(mine["status"])
        if len(statuses) > 1:
            raise ValueError(
                f"{rec.country}: rows of different status {sorted(statuses)}"
            )
        median = float(mine["price_per_kg_local"].median()) if len(mine) else np.nan
        pd_factor = (plant_deflator or {}).get(rec.country, 1.0)
        rd_factor = (reference_deflator or {}).get(rec.country, 1.0)
        reference = float(rec.unit_value_local)
        ratio = (median * pd_factor) / (reference * rd_factor)
        out.append(
            {
                "country": rec.country,
                "state": int(rec.state),
                "category": category,
                "plant_price_per_kg_local": median,
                "n_plant_observations": len(mine),
                "reference_unit_value_local": reference,
                "n_reference_households": _count(getattr(rec, "n_households", None)),
                "price_ratio": ratio,
                "status": statuses.pop() if statuses else None,
            }
        )
    return pd.DataFrame(out)


def _count(value) -> float | int:
    """Household count as int; a missing count stays missing (NaN, null in JSON)."""
    if value is None or pd.isna(value):
        return np.nan
    return int(value)


def _round(value: float, digits: int = 4) -> float | None:
    return (
        None if value is None or not np.isfinite(value) else round(float(value), digits)
    )


def summarise(observed: pd.DataFrame, placeholders: pd.DataFrame) -> dict:
    """Country and city coverage plus price statistics; placeholders are counted only."""
    by_country = {}
    for (country, category), part in observed.groupby(["country", "category"]):
        protein = part["price_per_kg_protein_local"].dropna()
        by_country.setdefault(country, {})[category] = {
            "currency": CURRENCY.get(country),
            "n_observations": len(part),
            "n_brands": int(part["brand"].nunique()),
            "retailers": sorted(part["retailer"].unique()),
            "n_by_city_basis": part["city_basis"].value_counts().sort_index().to_dict(),
            "median_price_per_kg_local": _round(part["price_per_kg_local"].median(), 2),
            "min_price_per_kg_local": _round(part["price_per_kg_local"].min(), 2),
            "max_price_per_kg_local": _round(part["price_per_kg_local"].max(), 2),
            "n_with_protein": len(protein),
            "median_price_per_kg_protein_local": (
                _round(protein.median(), 2) if len(protein) else None
            ),
        }
    cells = []
    counts = {"city_store": 0, "national_online_only": 0, "placeholder": 0}
    for country, city, state in CITIES:
        for category in CATEGORIES:
            mine = observed[
                (observed.country == country) & (observed.category == category)
            ]
            n_city = int(
                ((mine.city == city) & (mine.city_basis == "city_store")).sum()
            )
            n_national = int((mine.city_basis == "national_online").sum())
            if n_city:
                basis = "city_store"
            elif n_national:
                basis = "national_online_only"
            else:
                basis = "placeholder"
            counts[basis] += 1
            n_placeholder = int(
                (
                    (placeholders.country == country)
                    & (placeholders.city == city)
                    & (placeholders.category == category)
                ).sum()
            )
            cells.append(
                {
                    "country": country,
                    "city": city,
                    "state": state,
                    "category": category,
                    "n_city_store_observations": n_city,
                    "n_national_online_observations": n_national,
                    "price_basis": basis,
                    "placeholder_rows_available": n_placeholder,
                }
            )
    return {
        "by_country": by_country,
        "coverage": {
            "cells": cells,
            "city_store_cells": counts["city_store"],
            "national_online_only_cells": counts["national_online_only"],
            "placeholder_cells": counts["placeholder"],
            "rule": (
                "city_store: a price tied to that city; national_online_only: only one "
                "online price list for the country; placeholder: no observation, the "
                "placeholder row stands in and its results stay under synthetic/outputs/"
            ),
        },
    }


def _deflators(cpi: dict[str, dict[str, float]]) -> tuple[dict, dict]:
    """Plant (2026 capture) and reference (survey period) factors to 2025 prices."""
    plant = {c: 1.0 / cpi[c]["2026"] for c in CURRENCY}
    reference = {
        "India": 1.0 / (5 / 12 * cpi["India"]["2023"] + 7 / 12 * cpi["India"]["2024"]),
        "Pakistan": 1.0
        / (0.5 * cpi["Pakistan"]["2024"] + 0.5 * cpi["Pakistan"]["2025"]),
    }
    return plant, reference


def reference_values(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Chicken and milk state unit values for both countries."""
    frames = []
    for country, table in tables.items():
        for category, group in REFERENCE_GROUP.items():
            frame = state_unit_values(table, country, group)
            frame["category"] = category
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def build_placeholders(refs: pd.DataFrame, us_ratio: dict[str, float]) -> pd.DataFrame:
    """One placeholder row per city and category from the US price ratio rule."""
    rows = []
    for country, city, state in CITIES:
        for category in CATEGORIES:
            part = refs[(refs.country == country) & (refs.category == category)]
            if state is not None:
                uv = float(part.set_index("state").loc[state, "unit_value_local"])
                where = f"state {state} weighted mean"
            elif country == "Pakistan":
                uv = float(part.set_index("state").loc[2, "unit_value_local"])
                where = (
                    "Punjab (province 2) weighted mean; Islamabad has no province cell"
                )
            else:
                w = part["n_households"]
                uv = float(
                    (part["unit_value_local"] * w).sum()
                    / w[part.unit_value_local.notna()].sum()
                )
                where = "household-count weighted mean of state cells; tier-2 city not selected"
            group = REFERENCE_GROUP[category]
            rows.append(
                {
                    "country": country,
                    "city": city,
                    "city_basis": "city_store",
                    "retailer": "placeholder",
                    "product": f"placeholder {category}",
                    "brand": "placeholder",
                    "category": category,
                    "pack_size_g": 1000.0,
                    "price_local": round(us_ratio[category] * uv, 2),
                    "currency": CURRENCY[country],
                    "protein_g_per_100g": np.nan,
                    "status": "SYNTHETIC",
                    "basis": (
                        f"US GFI 2025 plant-to-{group} price ratio {us_ratio[category]:.4f} "
                        f"times {group} unit value ({where}, household table, market "
                        "purchases); survey-year prices, not deflated"
                    ),
                }
            )
    return pd.DataFrame(rows)


def _us_ratio(path: Path = US_CALIBRATION) -> dict[str, float]:
    gfi = json.loads(Path(path).read_text())["gfi"]["values"]
    return {
        "plant_meat": gfi["plant_based_meat"]["price_ratio_us"]["value"],
        "dairy_alt": gfi["dairy_alternatives"]["price_ratio_us"]["value"],
    }


def _ratio_records(frame: pd.DataFrame) -> list[dict]:
    out = []
    for rec in frame.to_dict("records"):
        row = {}
        for key, value in rec.items():
            if isinstance(value, float):
                value = _round(value)
                if key.startswith("n_") and value is not None:
                    value = int(value)
            row[key] = value
        out.append(row)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--observations", type=Path, default=OBSERVATIONS)
    parser.add_argument("--work", type=Path, default=LOCAL / "work")
    parser.add_argument(
        "--drivers", type=Path, default=HERE / "outputs" / "drivers.json"
    )
    parser.add_argument(
        "--out", type=Path, default=HERE / "outputs" / "prices_summary.json"
    )
    parser.add_argument(
        "--synthetic-out",
        type=Path,
        default=HERE / "synthetic" / "outputs" / "price_ratios_placeholder.json",
    )
    parser.add_argument(
        "--write-placeholders",
        action="store_true",
        help="rebuild synthetic/plant_prices.csv from the household tables",
    )
    args = parser.parse_args(argv)

    tables = {
        "India": pd.read_parquet(args.work / "india_households.parquet"),
        "Pakistan": pd.read_parquet(args.work / "pakistan_households.parquet"),
    }
    refs = reference_values(tables)
    if args.write_placeholders:
        build_placeholders(refs, _us_ratio()).to_csv(SYNTHETIC_CSV, index=False)
        print(f"wrote {SYNTHETIC_CSV}")

    raw = pd.read_csv(args.observations)
    observed = normalise_prices(raw)
    placeholders = normalise_prices(load_synthetic())
    cpi = json.loads(args.drivers.read_text())["cpi_index_2025"]
    plant_defl, ref_defl = _deflators(cpi)

    ratios, ratios_nominal, placeholder_ratios = [], [], []
    for category in CATEGORIES:
        ref = refs[refs.category == category]
        ratios.append(price_ratio(observed, ref, category, plant_defl, ref_defl))
        ratios_nominal.append(price_ratio(observed, ref, category))
        placeholder_ratios.append(price_ratio(placeholders, ref, category))
    ratio = pd.concat(ratios, ignore_index=True)
    ratio = ratio[ratio.n_plant_observations > 0]
    nominal = pd.concat(ratios_nominal, ignore_index=True)
    nominal = nominal[nominal.n_plant_observations > 0]

    summary = summarise(observed, placeholders)
    summary = {
        "status": "DIAGNOSTIC",
        "snapshot": {
            "captured_utc": [
                str(raw.captured_at_utc.min()),
                str(raw.captured_at_utc.max()),
            ],
            "n_observations": len(observed),
            "categories": list(CATEGORIES),
            "unit_rule": "price per kg = price / pack grams * 1000; 1 ml counts as 1 g",
            "raw_captures": "local only: OUTPUTS/Household Demand 2026-10/prices-raw/ (ruling R21)",
        },
        **summary,
        "price_ratio_2025_prices": {
            "definition": (
                "country median plant price per kg (all observations of the category) "
                "over the state reference unit value (plant_meat: chicken per kg; "
                "dairy_alt: milk per litre), both deflated to 2025 with IMF WEO CPI"
            ),
            "deflators": {
                "plant": {c: _round(v, 6) for c, v in plant_defl.items()},
                "reference": {c: _round(v, 6) for c, v in ref_defl.items()},
                "reference_periods": {
                    "India": "HCES 2023-24, August 2023 to July 2024: 5/12 CPI 2023 + 7/12 CPI 2024",
                    "Pakistan": "HIES 2024-25, fiscal-year label (July 2024 to June 2025 assumed): CPI 2024 / 2 + CPI 2025 / 2",
                },
            },
            "rows": _ratio_records(ratio),
            "missing": [
                f"{c} {k}: no observation; any result rests on the placeholder ratio "
                "under synthetic/outputs/ and stays out of claims (ruling R43)"
                for c in CURRENCY
                for k in CATEGORIES
                if not ((observed.country == c) & (observed.category == k)).any()
            ],
        },
        "price_ratio_nominal_sensitivity": _ratio_records(nominal),
        "reference_unit_values": {
            "source": "household tables (HCES 2023-24, HIES 2024-25), market purchases only, multiplier-weighted",
            "min_cell_households": MIN_CELL_HOUSEHOLDS,
            "rows": _ratio_records(refs),
        },
        "us_comparison_ratio": _us_ratio(),
    }
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {args.out}")

    args.synthetic_out.parent.mkdir(parents=True, exist_ok=True)
    args.synthetic_out.write_text(
        json.dumps(
            {
                "status": "SYNTHETIC",
                "note": "price ratios from placeholder plant prices; not survey-deflated",
                "rows": _ratio_records(
                    pd.concat(placeholder_ratios, ignore_index=True)
                ),
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {args.synthetic_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
