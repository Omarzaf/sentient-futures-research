"""Assign vegetarian and addressable household segments.

Input: a household table with the shared schema of ``households_india`` and
``households_pakistan``. Output: the same rows with these columns added.

- ``segment``: ``meat_eater`` or ``vegetarian`` (NaN for ``NO_FOOD_DATA`` rows). Only India has a vegetarian
  segment; every Pakistan household is ``meat_eater``.
- ``segment_method``: ``NFHS5_CALIBRATED``, ``ZERO_RECALL_DIAGNOSTIC`` or ``NO_FOOD_DATA``.
- ``addressable``: urban meat eater with packaged-food spending above 0.
- ``addressable_vegetarian``: urban vegetarian with packaged-food spending above 0
  (India only, False for Pakistan; ruling R30).
- ``addressable_rule``: ``FULL``, or ``PACKAGED_CONDITION_DROPPED`` for a country
  whose ``value_month_packaged`` is missing for every household (ruling R6).

No-food-data rule (ruling R33). A household whose ``value_month_`` columns are all
missing gets ``segment`` NaN, ``segment_method`` ``NO_FOOD_DATA`` and False for both
addressable flags. It joins no NFHS cell and no share denominator, because all-missing
meat columns would otherwise read as zero recall.

Zero-recall rule. A household is zero-recall when every meat group (chicken,
mutton, beef and buffalo, fish, pork, eggs) is missing or 0 in both quantity and
value. A missing group counts as no purchase because the survey tables leave an
item missing when a household did not report it. A group with a positive value
but a missing quantity counts as purchased. Zero-recall households are labelled
``vegetarian`` in India when no NFHS-5 table is given.

NFHS-5 calibration. Within each state by religion by caste cell that has an NFHS-5
never-eat share, zero-recall households are ranked by meat-free spending score and
the top households are labelled ``vegetarian`` until their weighted share of the
cell is closest to ``never_eat_share``. The score is
``veg / (veg + meat + meals_out)`` with veg = milk + paneer + pulses + soya value,
meat = meat groups value and meals_out = cooked meals bought. Meals bought outside
the home are the main place unseen meat can enter, so households with the least
of it rank first. A missing value counts as 0 in the score only; no consumption
is imputed. Ties break on ``hhid``. Households with meat recall are never labelled
vegetarian, so a cell whose zero-recall share is below its target falls short;
``calibration_report`` lists the shortfall. A cell without an NFHS-5 row keeps the
zero-recall rule and the ``ZERO_RECALL_DIAGNOSTIC`` label.

Run from the library root:

    python research/household-demand/segments.py \
        --india "../OUTPUTS/Household Demand 2026-10/work/india_households.parquet" \
        --pakistan "../OUTPUTS/Household Demand 2026-10/work/pakistan_households.parquet" \
        --summary outputs/segments_summary.json

``--nfhs`` takes ``inputs/nfhs5_never_eat.csv`` (columns state, religion, caste,
never_eat_share) once the DHS Program data are available. Its state, religion and
caste codes must match the HCES codes in the household table.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import households_india as hi
import numpy as np
import pandas as pd

__all__ = [
    "ADDRESSABLE_RULES",
    "MEAT_GROUPS",
    "SEGMENT_METHODS",
    "assign_segments",
    "calibration_report",
    "main",
    "segment_summary",
]

LIBRARY_ROOT = hi.LIBRARY_ROOT
HERE = hi.HERE

MEAT_GROUPS: tuple[str, ...] = (
    "chicken",
    "mutton",
    "beef_buffalo",
    "fish",
    "pork",
    "eggs",
)
SCORE_VEG_GROUPS: tuple[str, ...] = ("milk", "paneer", "pulses", "soya")
SEGMENT_METHODS: tuple[str, ...] = (
    "NFHS5_CALIBRATED",
    "ZERO_RECALL_DIAGNOSTIC",
    "NO_FOOD_DATA",
)
ADDRESSABLE_RULES: tuple[str, ...] = ("FULL", "PACKAGED_CONDITION_DROPPED")
NFHS_COLUMNS: tuple[str, ...] = ("state", "religion", "caste", "never_eat_share")
CELL_KEYS: tuple[str, ...] = ("state", "religion", "caste")
SEGMENT_FLAGS: tuple[str, ...] = (
    "meat_eater",
    "vegetarian",
    "addressable",
    "addressable_vegetarian",
)
URBAN = 2
INDIA_CURRENCY = "INR"
PAKISTAN_CURRENCY = "PKR"


def _require(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    """Raise ValueError naming every column missing from ``frame``."""
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} is missing columns: {', '.join(missing)}")


def _positive(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return a boolean frame, True where a value is above 0 (missing is False)."""
    return frame[columns].astype(float).gt(0)


def _cell_keys(frame: pd.DataFrame) -> pd.Series:
    """Return one string key per row for state, religion and caste; missing becomes -1."""
    parts = [frame[name].astype("Int64").fillna(-1).astype(str) for name in CELL_KEYS]
    return parts[0] + "|" + parts[1] + "|" + parts[2]


def _nfhs_targets(nfhs: pd.DataFrame) -> dict[str, float]:
    """Validate the NFHS-5 table and return never-eat share by cell key."""
    _require(nfhs, list(NFHS_COLUMNS), "nfhs")
    share = nfhs["never_eat_share"].astype(float)
    if share.isna().any() or (share < 0).any() or (share > 1).any():
        raise ValueError("nfhs never_eat_share must lie in [0, 1] and not be missing")
    keys = _cell_keys(nfhs)
    if keys.duplicated().any():
        raise ValueError(
            f"nfhs has duplicate state, religion, caste cells: {sorted(keys[keys.duplicated()].unique())}"
        )
    return dict(zip(keys, share, strict=True))


def _meat_free_score(frame: pd.DataFrame) -> np.ndarray:
    """Return veg / (veg + meat + meals_out) per row, 0 where the sum is 0."""

    def value(group: str) -> pd.Series:
        return frame[f"value_month_{group}"].astype(float).fillna(0.0)

    veg = sum(value(group) for group in SCORE_VEG_GROUPS)
    other = sum(value(group) for group in MEAT_GROUPS) + value("meals_out")
    total = veg + other
    return np.where(total > 0, veg / total.where(total > 0, 1.0), 0.0)


def _closest_prefix(weights: np.ndarray, total: float, target: float) -> int:
    """Return how many ranked households to label so their weight share is closest to target."""
    shares = np.concatenate([[0.0], np.cumsum(weights) / total])
    return int(np.argmin(np.abs(shares - target)))


def _calibrate_cell(
    weights: np.ndarray,
    eligible: np.ndarray,
    score: np.ndarray,
    hhid: np.ndarray,
    target: float,
) -> np.ndarray:
    """Return a boolean mask of the zero-recall households labelled vegetarian."""
    chosen = np.zeros(len(weights), dtype=bool)
    candidates = np.flatnonzero(eligible)
    if len(candidates) == 0:
        return chosen
    order = candidates[np.lexsort((hhid[candidates], -score[candidates]))]
    count = _closest_prefix(weights[order], float(weights.sum()), target)
    chosen[order[:count]] = True
    return chosen


def _addressable(
    frame: pd.DataFrame, packaged_present: bool, segment: str
) -> pd.Series:
    """Return urban, ``segment`` and (when present) packaged-above-0 as a boolean."""
    flag = (frame["sector"] == URBAN) & (frame["segment"] == segment)
    if packaged_present:
        flag &= frame["value_month_packaged"].astype(float).gt(0)
    return flag


def assign_segments(
    households: pd.DataFrame, nfhs: pd.DataFrame | None
) -> pd.DataFrame:
    """Return a copy of ``households`` with segment, method and addressable columns.

    ``currency`` decides the country: INR rows are India, PKR rows are Pakistan.
    See the module docstring for the zero-recall rule, the NFHS-5 calibration and
    the addressable rule. The input frame is not modified.
    """
    meat_columns = [
        f"{kind}_month_{group}" for kind in ("qty", "value") for group in MEAT_GROUPS
    ]
    required = [
        "hhid",
        "state",
        "sector",
        "multiplier",
        "currency",
        "value_month_packaged",
        *meat_columns,
    ]
    if nfhs is not None:
        required += [
            "religion",
            "caste",
            *(f"value_month_{group}" for group in (*SCORE_VEG_GROUPS, "meals_out")),
        ]
    _require(households, required, "households")
    unknown = set(households["currency"].dropna().unique()) - {
        INDIA_CURRENCY,
        PAKISTAN_CURRENCY,
    }
    if unknown or households["currency"].isna().any():
        raise ValueError(
            f"currency must be INR or PKR on every row, found: {sorted(map(str, unknown)) or 'missing'}"
        )
    if households["multiplier"].isna().any():
        raise ValueError("multiplier is missing for some households")

    out = households.copy()
    qty = _positive(out, [f"qty_month_{group}" for group in MEAT_GROUPS])
    value = _positive(out, [f"value_month_{group}" for group in MEAT_GROUPS])
    zero_recall = ~(qty.any(axis=1) | value.any(axis=1)).to_numpy()
    is_india = (out["currency"] == INDIA_CURRENCY).to_numpy()
    value_columns = [c for c in out.columns if c.startswith("value_month_")]
    no_food = out[value_columns].isna().all(axis=1).to_numpy()

    segment = np.where(is_india & zero_recall, "vegetarian", "meat_eater").astype(
        object
    )
    segment[no_food] = np.nan
    method = np.full(len(out), "ZERO_RECALL_DIAGNOSTIC", dtype=object)
    method[no_food] = "NO_FOOD_DATA"

    if nfhs is not None:
        targets = _nfhs_targets(nfhs)
        keys = _cell_keys(out).to_numpy()
        weights = out["multiplier"].to_numpy(dtype=float)
        score = _meat_free_score(out)
        hhid = out["hhid"].astype(str).to_numpy()
        positions = np.flatnonzero(is_india & ~no_food)
        cells = pd.Series(positions).groupby(keys[positions]).indices
        for key, inside in cells.items():
            if key not in targets:
                continue
            rows = positions[inside]
            chosen = _calibrate_cell(
                weights[rows], zero_recall[rows], score[rows], hhid[rows], targets[key]
            )
            segment[rows] = np.where(chosen, "vegetarian", "meat_eater")
            method[rows] = "NFHS5_CALIBRATED"

    out["segment"] = segment
    out["segment_method"] = method
    out["addressable"] = False
    out["addressable_vegetarian"] = False
    out["addressable_rule"] = "FULL"
    for currency in (INDIA_CURRENCY, PAKISTAN_CURRENCY):
        rows = out["currency"] == currency
        if not rows.any():
            continue
        has_food = rows.to_numpy() & ~no_food
        packaged_present = bool(out.loc[has_food, "value_month_packaged"].notna().any())
        country = out.loc[rows]
        out.loc[rows, "addressable"] = _addressable(
            country, packaged_present, "meat_eater"
        )
        if currency == INDIA_CURRENCY:
            out.loc[rows, "addressable_vegetarian"] = _addressable(
                country, packaged_present, "vegetarian"
            )
        if not packaged_present:
            out.loc[rows, "addressable_rule"] = "PACKAGED_CONDITION_DROPPED"
    return out


def calibration_report(segmented: pd.DataFrame, nfhs: pd.DataFrame) -> pd.DataFrame:
    """Return target and achieved vegetarian share for each NFHS-5 calibrated cell.

    ``shortfall`` is ``target_share - achieved_share``: positive when the cell holds
    too few zero-recall households to reach the target, near 0 when matched.
    ``zero_recall_share`` is the weighted share of the cell with no meat recall.
    """
    targets = _nfhs_targets(nfhs)
    frame = segmented[segmented["segment_method"] == "NFHS5_CALIBRATED"]
    keys = _cell_keys(frame)
    rows = []
    for key, cell in frame.groupby(keys.to_numpy(), sort=True):
        weight = cell["multiplier"].astype(float)
        achieved = float(weight[cell["segment"] == "vegetarian"].sum() / weight.sum())
        first = cell.iloc[0]
        rows.append(
            {
                **{name: first[name] for name in CELL_KEYS},
                "n_households": len(cell),
                "target_share": targets[key],
                "achieved_share": achieved,
                "shortfall": targets[key] - achieved,
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            *CELL_KEYS,
            "n_households",
            "target_share",
            "achieved_share",
            "shortfall",
        ],
    )


def _segment_cell(cell: pd.DataFrame, minimum: int) -> dict:
    """Return counts and weighted shares for one cell; shares are null under ``minimum``.

    Households with ``NO_FOOD_DATA`` are counted in ``no_food_data_households`` and
    left out of every share denominator and of the minimum-count test (ruling R33).
    ``n_households`` counts all rows of the cell.
    """
    frame = cell[cell["segment_method"] != "NO_FOOD_DATA"]
    weight = frame["multiplier"].astype(float)
    flags = {
        "meat_eater": frame["segment"] == "meat_eater",
        "vegetarian": frame["segment"] == "vegetarian",
        "addressable": frame["addressable"],
        "addressable_vegetarian": frame["addressable_vegetarian"],
    }
    shares = {
        name: hi._cell(flag.astype(float), weight, minimum)[0]
        for name, flag in flags.items()
    }
    return {
        "n_households": len(cell),
        "no_food_data_households": len(cell) - len(frame),
        **{f"n_{name}": int(flag.sum()) for name, flag in flags.items()},
        "shares": shares,
    }


def _single_value(column: pd.Series, name: str):
    """Return the one distinct value of ``column`` or raise."""
    distinct = column.unique()
    if len(distinct) != 1:
        raise ValueError(
            f"{name} must hold one value per country, found {list(distinct)}"
        )
    return distinct[0]


def segment_summary(
    tables: dict[str, pd.DataFrame], min_households: int = hi.MIN_CELL_HOUSEHOLDS
) -> dict:
    """Return weighted segment shares per country, national and by state.

    ``tables`` maps a country name to its output of ``assign_segments``. Each cell
    carries unweighted counts. A cell with fewer than ``min_households`` households
    has null shares and keeps its counts (ruling R16). Households without food data
    leave the share denominators and are counted separately (ruling R33). No
    household row is included.
    """
    countries = {}
    for name, table in tables.items():
        methods = table["segment_method"].value_counts().sort_index()
        country = {
            "households": len(table),
            "no_food_data_households": int(
                (table["segment_method"] == "NO_FOOD_DATA").sum()
            ),
            "segment_method": {key: int(count) for key, count in methods.items()},
            "addressable_rule": _single_value(
                table["addressable_rule"], "addressable_rule"
            ),
            "national": _segment_cell(table, min_households),
            "states": {
                str(int(state)): _segment_cell(frame, min_households)
                for state, frame in table.groupby("state", sort=True)
            },
        }
        if "stratum_status" in table:
            country["placeholder_stratum_households"] = int(
                (table["stratum_status"] != "RESOLVED").sum()
            )
        countries[name] = country
    return {
        "status": "DIAGNOSTIC",
        "source": "household tables from households_india.py and households_pakistan.py",
        "weight": "household multiplier from each table",
        "min_cell_households": min_households,
        "suppression": (
            "a cell with fewer than min_cell_households unweighted households has null shares; "
            "its unweighted counts n_* are kept (ruling R16)"
        ),
        "share_definition": (
            "weighted share of the households in the cell that have food data; households "
            "whose value_month_ columns are all missing (NO_FOOD_DATA) are counted in "
            "no_food_data_households and excluded from numerators and denominators (ruling R33)"
        ),
        "segment_rules": {
            "zero_recall": (
                "no chicken, mutton, beef, fish, pork or eggs with positive quantity or value "
                "in the recall window; a missing group counts as no purchase, unless every "
                "value_month_ column is missing (NO_FOOD_DATA)"
            ),
            "vegetarian": (
                "India only: NFHS5_CALIBRATED within calibrated state, religion and caste cells, "
                "otherwise zero-recall households; Pakistan has no vegetarian segment"
            ),
            "meat_eater": "every household that is not vegetarian",
            "addressable": (
                "urban meat eater with value_month_packaged above 0; the packaged condition is "
                "dropped for a country whose packaged value is missing for every household"
            ),
            "addressable_vegetarian": (
                "India only: urban vegetarian with value_month_packaged above 0, same rule R6"
            ),
        },
        "zero_recall_caveat": (
            "the recall window is 7 days, so a household that eats meat less often than weekly "
            "counts as zero-recall; ZERO_RECALL_DIAGNOSTIC vegetarian shares therefore sit above "
            "the share that never eats meat"
        ),
        "countries": countries,
    }


def _sha256(path: Path) -> str:
    """Hash one file in chunks."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _outside_repository(
    parser: argparse.ArgumentParser, value: str | None
) -> Path | None:
    """Return ``value`` resolved, or stop with a parser error when it is inside the repository."""
    if value is None:
        return None
    path = Path(value).resolve()
    if path.is_relative_to(LIBRARY_ROOT):
        parser.error(f"household rows must be written outside the repository: {path}")
    return path


def _load(
    parser: argparse.ArgumentParser, path: str | None, currency: str, label: str
) -> pd.DataFrame | None:
    """Read one household parquet and check that it holds only ``currency`` rows."""
    if path is None:
        return None
    table = pd.read_parquet(path)
    if set(table["currency"].unique()) != {currency}:
        parser.error(f"--{label} must hold {currency} rows only: {path}")
    return table


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point: segment household tables and write the summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--india", help="India household parquet (relative to the working directory)"
    )
    parser.add_argument(
        "--pakistan",
        help="Pakistan household parquet (relative to the working directory)",
    )
    parser.add_argument(
        "--nfhs",
        help="NFHS-5 never-eat CSV (state, religion, caste, never_eat_share); omit for the zero-recall diagnostic",
    )
    parser.add_argument(
        "--india-out",
        help="optional segmented India parquet outside the repository",
    )
    parser.add_argument(
        "--pakistan-out",
        help="optional segmented Pakistan parquet outside the repository",
    )
    parser.add_argument(
        "--summary",
        default="outputs/segments_summary.json",
        help="segment summary JSON (relative paths resolve against research/household-demand/)",
    )
    args = parser.parse_args(argv)
    if not (args.india or args.pakistan):
        parser.error("give --india, --pakistan or both")
    outs = {
        "india": _outside_repository(parser, args.india_out),
        "pakistan": _outside_repository(parser, args.pakistan_out),
    }
    summary_path = hi._resolve_here(args.summary)

    sources = {"india": args.india, "pakistan": args.pakistan}
    raw = {
        "india": _load(parser, args.india, INDIA_CURRENCY, "india"),
        "pakistan": _load(parser, args.pakistan, PAKISTAN_CURRENCY, "pakistan"),
    }
    nfhs = pd.read_csv(args.nfhs) if args.nfhs else None
    tables = {
        name: assign_segments(table, nfhs)
        for name, table in raw.items()
        if table is not None
    }
    for name, table in tables.items():
        if outs[name] is not None:
            outs[name].parent.mkdir(parents=True, exist_ok=True)
            table.to_parquet(outs[name], index=False)

    summary = segment_summary(tables)
    summary["inputs"] = {
        name: {"file": Path(sources[name]).name, "sha256": _sha256(Path(sources[name]))}
        for name in tables
    }
    summary["nfhs5"] = (
        {"file": Path(args.nfhs).name, "sha256": _sha256(Path(args.nfhs))}
        if args.nfhs
        else None
    )
    hi._write_json(summary_path, summary)
    for name, country in summary["countries"].items():
        shares = country["national"]["shares"]
        print(
            f"{name} households={country['households']} "
            f"meat_eater={shares['meat_eater']} vegetarian={shares['vegetarian']} "
            f"addressable={shares['addressable']} "
            f"addressable_vegetarian={shares['addressable_vegetarian']} "
            f"rule={country['addressable_rule']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
