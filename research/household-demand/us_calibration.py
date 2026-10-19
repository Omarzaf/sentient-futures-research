"""Calibrate intent-to-purchase conversion on the United States.

Formulas (protocol ``us_calibration``, ruling R7):

    conversion = min(1, penetration / addressable_share) / intent_share
    spend_per_adopter_usd = sales_usd / (us_households * penetration)

The addressable share defaults to 1.0. Passing the CE addressable share assumes
every US buyer sits in the addressable segment, which overstates conversion if
some buyers sit outside it (R7). A conversion above 1 raises ValueError.

Categories (ruling R34). Plant-based meat uses GFI's US plant-based meat and
seafood retail sales and household penetration with the Bryant et al. (2019)
USA top-two-box intent 0.329 (R12) and the plant-based to chicken price ratio
(R35; the all-meat ratio is a sensitivity value). Dairy alternatives have no
Bryant intent measure, so conversion is 1 and intent is
min(1, penetration / us_urban_packaged_share), the observed US plant-based milk
household penetration within urban CUs that buy packaged food (R36); this is a
deviation from the protocol formula. The
$7.9 billion all-category total is a benchmark only. A GFI value that cannot be
verified stays None and its category is marked UNAVAILABLE.

CE loader. The BLS Consumer Expenditure Survey 2023 Diary family files
(``fmld231.csv`` to ``fmld234.csv``) give one record per consumer unit (CU)
diary week with weight ``FINLWT21``. The weighted CU count is the mean over the
four quarterly files of the sum of ``FINLWT21`` (each quarterly file's weights
sum to the CU population). The addressable rule of Task 5 maps to:

- urban: ``BLS_URBN == 1`` (2 is rural; any other code raises);
- buys meat: ``BEEF + PORK + OTHMEAT + POULTRY + SEAFOOD + EGGS`` above 0 in
  the diary week, mirroring Task 5's 7-day meat, fish and egg recall;
- buys prepared or packaged food: ``MISCFOOD`` above 0 in the diary week
  (BLS "miscellaneous foods": frozen prepared meals and other foods, canned
  and packaged soups, other canned and packaged prepared foods). Ruling R38
  asks for the HCES 299 content (bakery, chocolate and candy, jam) instead; the
  CE zips carry no UCC labels, so those codes cannot be identified with
  confidence and MISCFOOD stays primary (``R38_STATUS``).

Each summary variable is the sum of ``COST`` over expenditure codes (UCC) with
a fixed two-digit prefix in the Diary expenditure files ``expd*.csv``: 03 beef,
04 pork, 05 other meats, 06 poultry, 07 fish and seafood, 08 eggs, 18
miscellaneous foods. ``ucc_check`` recomputes each sum and reports the largest
difference. The addressable share is the weighted share of diary weeks that
meet all three conditions; ``us_urban_packaged_share`` drops the meat
condition (R36). Diary weeks with ``FOODTOT`` at or below 0 leave the share
denominators (R39, matching R33); shares that keep them are reported as
sensitivity values. The CU count uses every diary week.

Only aggregates are written; no CE record enters the repository. Run from the
library root:

    python research/household-demand/us_calibration.py \
        --diary-dir "../OUTPUTS/Household Demand 2026-10/inputs/bls_ce_2023_extracted/diary23" \
        --out outputs/us_calibration.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "BRYANT_USA_INTENT",
    "CE_MEAT_VARIABLES",
    "CE_SUMMARY_UCC_PREFIX",
    "GFI",
    "R38_STATUS",
    "Calibration",
    "build_payload",
    "calibrate",
    "calibrate_category",
    "calibrate_dairy",
    "ce_summary",
    "load_ce_diary",
    "main",
    "ucc_check",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]

CE_URBAN = 1
CE_RURAL = 2
CE_MEAT_VARIABLES: tuple[str, ...] = (
    "BEEF",
    "PORK",
    "OTHMEAT",
    "POULTRY",
    "SEAFOOD",
    "EGGS",
)
CE_PACKAGED_VARIABLE = "MISCFOOD"
R38_STATUS = {
    "status": "NOT_DONE",
    "primary_packaged_condition": "MISCFOOD above 0",
    "requested": (
        "ruling R38: packaged condition from bakery (bread, biscuits or cookies, cakes), "
        "chocolate and candy, and jam and preserves UCCs, matching HCES item 299"
    ),
    "reason": (
        "the approved CE 2023 interview and diary zips hold CSV data only, with no UCC "
        "labels; bakery codes (prefix 02, 9 codes) and sweets codes (prefix 15, 3 codes) "
        "cannot be split into bread, cookies, cakes, candy and jam with confidence, and no "
        "further BLS file was approved for download"
    ),
}
CE_SUMMARY_UCC_PREFIX: dict[str, str] = {
    "BEEF": "03",
    "PORK": "04",
    "OTHMEAT": "05",
    "POULTRY": "06",
    "SEAFOOD": "07",
    "EGGS": "08",
    "MISCFOOD": "18",
}
CE_COLUMNS: tuple[str, ...] = (
    "NEWID",
    "FINLWT21",
    "BLS_URBN",
    "FOODTOT",
    *CE_SUMMARY_UCC_PREFIX,
)

GFI_PAGE = {
    "title": "Plant-based retail market overview",
    "publisher": "The Good Food Institute (GFI), data from SPINS",
    "url": "https://gfi.org/marketresearch/",
    "captured_at_utc": "2026-10-19T01:00:18Z",
    "sha256": "d06e4649b1dc7ca30767f50d93428e314d5bca930bde0eae4859a4d0a18895dc",
    "data_period": (
        "SPINS point-of-sale data, 52 weeks ending 30 November 2025; SPINS consumer "
        "panel (Circana), all US outlets, 52 weeks ending 30 November 2025 "
        "(section About the data)"
    ),
}
GFI_PRICE_GRAPHIC = {
    "title": "Plant-based versus animal-based price per weight comparison, 2025",
    "url": "https://gfi.org/wp-content/uploads/2026/04/GFI25009-MICE-MR05-v4-260330.png",
    "captured_at_utc": "2026-10-19T01:00:28Z",
    "sha256": "ccd9d6108f5506fb2add7eedbe491ca7e93a87d2658530bc34353e53da724c22",
    "locator": "gfi.org/marketresearch/, section Overall plant-based foods, tab Price gap, graphic",
    "source_note": (
        "graphic footnote: plant-based prices from GFI and PBFA custom SPINS categories, "
        "year ending 30 November 2025; animal-based meat prices from Circana fresh meat "
        "subcategories, 52 weeks ending November 2025; animal-based milk and egg prices "
        "from the US Bureau of Labor Statistics, monthly December 2024 to November 2025"
    ),
}


def _value(value, year, locator, quote):
    """Return one sourced value record."""
    return {"value": value, "year": year, "locator": locator, "quote": quote}


GFI: dict[str, dict] = {
    "all_categories": {
        "scope": "all plant-based foods, US retail",
        "sales_usd": _value(
            7.9e9,
            2025,
            "section Overall plant-based foods, heading Plant-based foods are a $7.9 billion market in U.S. retail",
            "the 2025 U.S. retail plant-based food market was worth $7.9 billion",
        ),
        "penetration": _value(
            0.60,
            2025,
            "section Overall plant-based foods, tab Purchase dynamics, first bullet",
            "A total of 60% of U.S. households purchased plant-based foods",
        ),
        "use": "benchmark only (ruling R34); not used in any conversion",
    },
    "plant_based_meat": {
        "scope": "plant-based meat and seafood, US retail (GFI reports meat and seafood together)",
        "sales_usd": _value(
            1.0e9,
            2025,
            "section Overall plant-based foods, tab Categories, second bullet",
            "Plant-based meat and seafood are estimated at $1.0 billion.",
        ),
        "penetration": _value(
            0.11,
            2025,
            "section Meat and seafood, tab Category sales, fourth bullet; also tab Purchase dynamics, second bullet",
            "In 2025, 11 percent of households purchased in the category",
        ),
        "price_ratio_us_all_meat": {
            "value": 8.23 / 4.67,
            "year": 2025,
            "plant_based_usd": 8.23,
            "conventional_usd": 4.67,
            "unit": "US dollars per pound, all meat",
            "locator": "price graphic, column Meat (per lb)",
            "quote": "$8.23 plant-based, $4.67 animal-based, 76% price premium",
            "use": "sensitivity value (ruling R35)",
        },
        "price_ratio_us": {
            "value": 7.88 / 3.17,
            "year": 2025,
            "plant_based_usd": 7.88,
            "conventional_usd": 3.17,
            "unit": "US dollars per pound, chicken",
            "locator": "price graphic, column Chicken",
            "quote": "$7.88 plant-based, $3.17 animal-based, 149% price premium",
            "use": "primary: plant-based meat substitutes chicken (decision 16, ruling R35)",
        },
    },
    "dairy_alternatives": {
        "scope": "plant-based milk, US retail (other plant-based dairy categories excluded)",
        "sales_usd": _value(
            2.7e9,
            2025,
            "section Milk, tab Category sales, first paragraph",
            "Plant-based milk remains a sizable category at $2.7 billion",
        ),
        "penetration": _value(
            0.38,
            2025,
            "section Milk, tab Category sales, first bullet; also Overall plant-based foods, tab Purchase dynamics, second bullet",
            "Household penetration at 38% and repeat rate at 75% remain steady.",
        ),
        "price_ratio_us": {
            "value": 8.70 / 4.07,
            "year": 2025,
            "plant_based_usd": 8.70,
            "conventional_usd": 4.07,
            "unit": "US dollars per gallon, milk",
            "locator": "price graphic, column Milk (per gal)",
            "quote": "$8.70 plant-based, $4.07 animal-based, 114% price premium",
        },
    },
}

BRYANT_USA_INTENT = {
    "value": 0.329,
    "definition": "USA share answering 4 or 5 (very or extremely likely) to plant-based meat purchase likelihood (R12)",
    "source": "protocol.json intent_sources.primary (Bryant, Szejda, Parekh, Deshpande and Tse 2019)",
    "locator": "Results, Descriptive Statistics, Acceptance, second paragraph",
}


@dataclass(frozen=True)
class Calibration:
    """US calibration of one product category."""

    us_households: int
    penetration: float
    intent_share: float
    sales_usd: float
    addressable_share: float
    conversion: float
    spend_per_adopter_usd: float


def _check_share(name: str, value: float) -> None:
    """Raise ValueError unless ``value`` lies in (0, 1]."""
    if not (isinstance(value, int | float) and math.isfinite(value) and 0 < value <= 1):
        raise ValueError(f"{name} must lie in (0, 1], got {value!r}")


def calibrate(
    us_households: int,
    penetration: float,
    intent_share: float,
    sales_usd: float,
    addressable_share: float = 1.0,
) -> Calibration:
    """Return conversion and spend per adopter for one category (ruling R7).

    Raises ValueError for a non-positive household count or sales, a share
    outside (0, 1], or a conversion above 1 (penetration within the addressable
    segment above stated intent).
    """
    if not (isinstance(us_households, int) and us_households > 0):
        raise ValueError(
            f"us_households must be a positive integer, got {us_households!r}"
        )
    if not (math.isfinite(sales_usd) and sales_usd > 0):
        raise ValueError(f"sales_usd must be positive, got {sales_usd!r}")
    _check_share("penetration", penetration)
    _check_share("intent_share", intent_share)
    _check_share("addressable_share", addressable_share)
    conversion = min(1.0, penetration / addressable_share) / intent_share
    if conversion > 1.0:
        raise ValueError(
            f"conversion {conversion:.4f} exceeds 1: penetration within the addressable "
            f"segment is above intent_share {intent_share}"
        )
    return Calibration(
        us_households=us_households,
        penetration=penetration,
        intent_share=intent_share,
        sales_usd=sales_usd,
        addressable_share=addressable_share,
        conversion=conversion,
        spend_per_adopter_usd=sales_usd / (us_households * penetration),
    )


def calibrate_category(
    category: str,
    us_households: int,
    penetration: float | None,
    intent_share: float | None,
    sales_usd: float | None,
    addressable_share: float = 1.0,
) -> dict:
    """Return a calibration record, UNAVAILABLE when any input is missing."""
    inputs = {
        "penetration": penetration,
        "intent_share": intent_share,
        "sales_usd": sales_usd,
    }
    missing = sorted(name for name, value in inputs.items() if value is None)
    if missing:
        return {
            "category": category,
            "status": "UNAVAILABLE",
            "missing": missing,
            "us_households": us_households,
            "addressable_share": addressable_share,
            **inputs,
            "conversion": None,
            "spend_per_adopter_usd": None,
        }
    result = calibrate(
        us_households, penetration, intent_share, sales_usd, addressable_share
    )
    return {
        "category": category,
        "status": "AVAILABLE",
        "missing": [],
        **asdict(result),
    }


def calibrate_dairy(
    us_households: int,
    penetration: float | None,
    sales_usd: float | None,
    urban_packaged_share: float = 1.0,
) -> dict:
    """Return the dairy record (rulings R34, R36).

    Intent is min(1, penetration / urban_packaged_share) and conversion is 1:
    penetration within urban CUs that buy packaged food stands in for intent.
    """
    intent = None
    if penetration is not None:
        _check_share("urban_packaged_share", urban_packaged_share)
        intent = min(1.0, penetration / urban_packaged_share)
    return calibrate_category(
        "dairy_alternatives",
        us_households,
        penetration,
        intent,
        sales_usd,
        addressable_share=urban_packaged_share,
    )


def load_ce_diary(diary_dir: Path) -> pd.DataFrame:
    """Read the four quarterly CE Diary family files with the columns this module uses."""
    paths = sorted(Path(diary_dir).glob("fmld*.csv"))
    if not paths:
        raise FileNotFoundError(f"no fmld*.csv files in {diary_dir}")
    frames = []
    for path in paths:
        frame = pd.read_csv(path, usecols=list(CE_COLUMNS), dtype={"NEWID": str})
        frame["quarter_file"] = path.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def load_ce_expenditures(diary_dir: Path) -> pd.DataFrame:
    """Read NEWID, UCC and COST from the CE Diary expenditure files."""
    paths = sorted(Path(diary_dir).glob("expd*.csv"))
    if not paths:
        raise FileNotFoundError(f"no expd*.csv files in {diary_dir}")
    return pd.concat(
        [
            pd.read_csv(
                path, usecols=["NEWID", "UCC", "COST"], dtype={"NEWID": str, "UCC": str}
            )
            for path in paths
        ],
        ignore_index=True,
    )


def ce_summary(diary: pd.DataFrame) -> dict:
    """Return the weighted CU count and the segment shares of CE diary weeks.

    ``us_households`` is the mean over ``quarter_file`` of the summed weights of
    all diary weeks. Shares are weighted by ``FINLWT21``. Primary shares leave
    out diary weeks with ``FOODTOT`` at or below 0 (ruling R39); the
    ``*_including_zero_food_weeks`` values keep them (sensitivity).
    """
    weight = diary["FINLWT21"].astype(float)
    if weight.isna().any() or (weight <= 0).any():
        raise ValueError("FINLWT21 must be positive on every record")
    codes = set(diary["BLS_URBN"].unique())
    if not codes <= {CE_URBAN, CE_RURAL}:
        raise ValueError(f"BLS_URBN must be 1 or 2, found {sorted(map(str, codes))}")
    food = diary["FOODTOT"].astype(float)
    if food.isna().any():
        raise ValueError("FOODTOT is missing for some diary weeks")
    has_food = food.gt(0)
    urban = diary["BLS_URBN"] == CE_URBAN
    meat = diary[list(CE_MEAT_VARIABLES)].astype(float).sum(axis=1).gt(0)
    packaged = diary[CE_PACKAGED_VARIABLE].astype(float).gt(0)
    urban_packaged = urban & packaged
    addressable = urban_packaged & meat
    if not has_food.any():
        raise ValueError("no diary week has food expenditure")

    def share(flag: pd.Series, base: pd.Series) -> float:
        return float(weight[flag & base].sum() / weight[base].sum())

    every = pd.Series(True, index=diary.index)
    quarters = weight.groupby(diary["quarter_file"]).sum()
    return {
        "us_households": round(float(quarters.mean())),
        "weight_sum_by_quarter_file": {
            name: float(value) for name, value in quarters.items()
        },
        "share_denominator": (
            "weighted diary weeks with FOODTOT above 0 (ruling R39); "
            "*_including_zero_food_weeks values use every diary week"
        ),
        "addressable_share": share(addressable, has_food),
        "us_urban_packaged_share": share(urban_packaged, has_food),
        "urban_share": share(urban, has_food),
        "meat_share": share(meat, has_food),
        "packaged_share": share(packaged, has_food),
        "addressable_share_including_zero_food_weeks": share(addressable, every),
        "us_urban_packaged_share_including_zero_food_weeks": share(
            urban_packaged, every
        ),
        "n_records": len(diary),
        "n_zero_food_records": int((~has_food).sum()),
        "zero_food_share": share(~has_food, every),
        "n_addressable_records": int(addressable.sum()),
        "n_urban_packaged_records": int(urban_packaged.sum()),
    }


def ucc_check(fmld: pd.DataFrame, expd: pd.DataFrame) -> dict:
    """Recompute each summary variable from UCC costs; report codes and largest difference."""
    out = {}
    newid = fmld["NEWID"].astype(str)
    for variable, prefix in CE_SUMMARY_UCC_PREFIX.items():
        rows = expd[expd["UCC"].astype(str).str.startswith(prefix)]
        totals = rows.groupby(rows["NEWID"].astype(str))["COST"].sum()
        recomputed = newid.map(totals).fillna(0.0).to_numpy()
        diff = np.abs(fmld[variable].astype(float).to_numpy() - recomputed)
        out[variable] = {
            "ucc_prefix": prefix,
            "uccs": sorted(rows["UCC"].astype(str).unique().tolist()),
            "max_abs_diff": float(diff.max()) if len(diff) else 0.0,
        }
    return out


def build_payload(ce: dict, ucc: dict, inputs: dict) -> dict:
    """Return the us_calibration.json payload from CE aggregates and the GFI values."""
    households = ce["us_households"]
    meat = GFI["plant_based_meat"]
    dairy = GFI["dairy_alternatives"]

    def value(record: dict) -> float | None:
        return record["value"]

    meat_result = calibrate_category(
        "plant_based_meat",
        households,
        value(meat["penetration"]),
        BRYANT_USA_INTENT["value"],
        value(meat["sales_usd"]),
        addressable_share=ce["addressable_share"],
    )
    meat_default = calibrate_category(
        "plant_based_meat",
        households,
        value(meat["penetration"]),
        BRYANT_USA_INTENT["value"],
        value(meat["sales_usd"]),
    )
    meat_result["conversion_with_addressable_share_1"] = meat_default["conversion"]
    meat_result["price_ratio_us"] = meat["price_ratio_us"]["value"]
    meat_result["price_ratio_us_all_meat"] = meat["price_ratio_us_all_meat"]["value"]
    meat_sensitivity = calibrate_category(
        "plant_based_meat",
        households,
        value(meat["penetration"]),
        BRYANT_USA_INTENT["value"],
        value(meat["sales_usd"]),
        addressable_share=ce["addressable_share_including_zero_food_weeks"],
    )
    meat_result["conversion_including_zero_food_weeks"] = meat_sensitivity["conversion"]
    meat_result["intent_source"] = BRYANT_USA_INTENT

    dairy_result = calibrate_dairy(
        households,
        value(dairy["penetration"]),
        value(dairy["sales_usd"]),
        urban_packaged_share=ce["us_urban_packaged_share"],
    )
    dairy_result["price_ratio_us"] = dairy["price_ratio_us"]["value"]
    dairy_sensitivity = calibrate_dairy(
        households,
        value(dairy["penetration"]),
        value(dairy["sales_usd"]),
        urban_packaged_share=ce["us_urban_packaged_share_including_zero_food_weeks"],
    )
    dairy_result["intent_share_including_zero_food_weeks"] = dairy_sensitivity[
        "intent_share"
    ]
    dairy_result["deviation"] = (
        "Rulings R34 and R36: no Bryant intent measure exists for dairy alternatives, so "
        "conversion is 1 and intent_share is min(1, penetration / us_urban_packaged_share), "
        "the observed US plant-based milk household penetration within urban CUs that buy "
        "packaged food (CE, without the meat condition), assuming every buyer sits in that "
        "base; observed behaviour replaces the protocol formula's intent term."
    )

    return {
        "status": "DIAGNOSTIC",
        "formulas": {
            "conversion": "min(1, penetration / addressable_share) / intent_share",
            "spend_per_adopter_usd": "sales_usd / (us_households * penetration)",
            "assumption": (
                "all US buyers sit in the addressable segment (ruling R7); overstates "
                "conversion if buyers sit outside it"
            ),
        },
        "ce": {
            "survey": "BLS Consumer Expenditure Survey 2023 public-use microdata, Diary survey",
            "files": "diary23/fmld231.csv to fmld234.csv (family), expd231.csv to expd234.csv (expenditure)",
            "unit": "consumer unit (CU); BLS notes CUs do not match households exactly",
            "us_households": households,
            "us_households_method": (
                "mean over the four quarterly fmld files of the summed FINLWT21 weights"
            ),
            "us_households_crosscheck": {
                "value": 134_556_000,
                "source": (
                    "BLS, Consumer expenditures in 2023, BLS Reports, Table A, row Number of "
                    "consumer units (in thousands), 2023 column: 134,556"
                ),
                "url": "https://www.bls.gov/opub/reports/consumer-expenditures/2023/",
            },
            "addressable_rule": {
                "urban": "BLS_URBN == 1 (1 urban, 2 rural)",
                "buys_meat": (
                    "BEEF + PORK + OTHMEAT + POULTRY + SEAFOOD + EGGS above 0 in the diary "
                    "week; UCC prefixes 03, 04, 05, 06, 07, 08"
                ),
                "buys_packaged_food": (
                    "MISCFOOD above 0 in the diary week; UCC prefix 18 (BLS miscellaneous "
                    "foods: frozen prepared meals and other foods, canned and packaged soups, "
                    "other canned and packaged prepared foods)"
                ),
                "buys_packaged_food_r38": R38_STATUS,
                "urban_packaged_base": (
                    "urban and buys packaged food, without the meat condition; dairy base "
                    "(ruling R36)"
                ),
                "window": "one diary week, mirroring the 7-day recall of Task 5",
                "definitions_source": "https://www.bls.gov/cex/csxgloss.htm",
            },
            **{key: value for key, value in ce.items() if key != "us_households"},
            "ucc_check": ucc,
        },
        "gfi": {"page": GFI_PAGE, "price_graphic": GFI_PRICE_GRAPHIC, "values": GFI},
        "categories": {
            "plant_based_meat": meat_result,
            "dairy_alternatives": dairy_result,
        },
        "benchmark_all_categories": {
            "sales_usd": GFI["all_categories"]["sales_usd"],
            "penetration": GFI["all_categories"]["penetration"],
            "use": GFI["all_categories"]["use"],
        },
        "inputs": inputs,
    }


def _sha256(path: Path) -> str:
    """Hash one file in chunks."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point: read CE Diary files and write us_calibration.json."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--diary-dir", required=True, help="extracted CE diary23 folder"
    )
    parser.add_argument(
        "--out",
        default="outputs/us_calibration.json",
        help="output JSON (relative paths resolve against research/household-demand/)",
    )
    args = parser.parse_args(argv)
    diary_dir = Path(args.diary_dir).resolve()
    if diary_dir.is_relative_to(LIBRARY_ROOT):
        parser.error(f"CE microdata must stay outside the repository: {diary_dir}")
    out = Path(args.out)
    out = out if out.is_absolute() else HERE / out

    diary = load_ce_diary(diary_dir)
    expd = load_ce_expenditures(diary_dir)
    ce = ce_summary(diary)
    ucc = ucc_check(diary, expd)
    inputs = {
        path.name: _sha256(path)
        for path in sorted([*diary_dir.glob("fmld*.csv"), *diary_dir.glob("expd*.csv")])
    }
    payload = build_payload(ce, ucc, inputs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    for name, record in payload["categories"].items():
        print(
            f"{name} status={record['status']} conversion={record['conversion']} "
            f"spend_per_adopter_usd={record['spend_per_adopter_usd']}"
        )
    print(
        f"us_households={ce['us_households']} addressable_share={ce['addressable_share']:.4f} "
        f"us_urban_packaged_share={ce['us_urban_packaged_share']:.4f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
