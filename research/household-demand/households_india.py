"""Build the India household protein table from HCES 2023-24 clean parquet.

One row per household with geography, design identifiers, the third-visit
multiplier, FDQ household size, head-of-household religion and social group,
MPCE in rupees, and for each protein group in ``codes.GROUPS`` the monthly
quantity, monthly value and unit value.

MPCE follows "Survey methodology and Estimation Procedure" section 3.5:
TE = E1 + (E2/P2) * P1 + (E3/P3) * P1 and MPCE = TE / P1, where E1, E2 and E3
are the FDQ, CSQ and DGQ summary-block totals (level_14) converted to 30 days
by each block's printed recall period, and P1, P2 and P3 are the household
sizes recorded with each questionnaire (level_15). Imputed rent (item 539) is
left out. A CSQ or DGQ summary row absent from a canvassed questionnaire
counts as no expenditure in that block. A household with no FDQ summary rows
gets missing MPCE and ``mpce_status`` "MISSING_FDQ"; all others are "OK" (R18).

Item quantities and values use ``cons_total_qty`` and ``cons_total_value``,
which already include home produce, scaled to 30 days by the item's recall
period. Free PMGKAY pulses (071) and gram (072) carry no value in the
questionnaire and add 0 rupees. An item a household did not report stays
missing. The unit value uses market purchases only, cons_total minus cons_home;
pulses leave out PDS 158 and free 071 and 072 (R15, R17). It is missing
unless the purchased quantity is positive.

Household rows are written outside the repository. The repository receives
weighted state-level means only (NSO rider: no estimates below state level),
with cells under 30 unweighted households set to null (R16).

Run from the library root:

    python research/household-demand/households_india.py \
        --clean-dir "../data/external/hces_2023_24/04_clean" \
        --out "../OUTPUTS/Household Demand 2026-10/work/india_households.parquet" \
        --summary outputs/india_summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import codes
import numpy as np
import pandas as pd

__all__ = [
    "BASE_COLUMNS",
    "GROUP_KINDS",
    "LIBRARY_ROOT",
    "MIN_CELL_HOUSEHOLDS",
    "build_india_households",
    "main",
    "mpce_frame",
    "run_log",
    "state_summary",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]

BASE_COLUMNS: tuple[str, ...] = (
    "hhid",
    "state",
    "district",
    "sector",
    "multiplier",
    "hh_size",
    "religion",
    "caste",
    "mpce_inr",
    "mpce_local",
    "mpce_status",
    "currency",
    "psu",
    "stratum",
    "sub_stratum",
    "stratum_status",
)
GROUP_KINDS: tuple[str, ...] = ("qty_month", "value_month", "unit_value")
QUESTIONNAIRES: tuple[str, ...] = ("F", "C", "D")

# Published all-India average MPCE, HCES 2023-24 fact sheet (NSO, December
# 2024), rupees, without imputed values of free items. Recorded for the run
# log comparison only; no local copy of the fact sheet is held.
PUBLISHED_MPCE_INR = {"rural": 4122, "urban": 6996}


def _read(
    clean_dir: Path, level: str, columns: list[str], filters=None
) -> pd.DataFrame:
    """Read selected columns of one clean level; fail on a missing file or column."""
    path = Path(clean_dir) / f"level_{level}.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"HCES level file not found: {path}")
    frame = pd.read_parquet(path, columns=columns, filters=filters)
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"level_{level} lacks columns {sorted(missing)}")
    frame["hhid"] = frame["hhid"].astype(str)
    return frame


def _not_reported_to_missing(values: pd.Series) -> pd.Series:
    """Map HCQ code 0 ("not reported") to missing and keep other codes."""
    return values.astype("Int64").mask(values.eq(codes.NOT_REPORTED_CODE))


def _households(clean_dir: Path) -> pd.DataFrame:
    """Join geography and design (level_01) with household traits (level_03)."""
    info = _read(
        clean_dir,
        "01",
        [
            "hhid",
            "fsu_serial_no",
            "sector",
            "state",
            "district",
            "stratum",
            "sub_stratum",
            "multiplier",
        ],
    )
    traits = _read(clean_dir, "03", ["hhid", "hh_size", "hoh_religion", "caste"])
    for name, frame in (("level_01", info), ("level_03", traits)):
        if frame["hhid"].duplicated().any():
            raise ValueError(f"duplicate household key in {name}")
    if set(info["hhid"]) != set(traits["hhid"]):
        raise ValueError("level_01 and level_03 hold different households")
    traits = traits.assign(
        religion=_not_reported_to_missing(traits["hoh_religion"]),
        caste=_not_reported_to_missing(traits["caste"]),
    ).drop(columns=["hoh_religion"])
    return info.merge(traits, on="hhid", validate="one_to_one")


def mpce_frame(clean_dir: Path, hhids: pd.Index) -> pd.DataFrame:
    """Return MPCE inputs and result per household, indexed by hhid."""
    visits = _read(
        clean_dir,
        "15",
        [
            "hhid",
            "questionnaire_num",
            "visit",
            "hh_size",
            "hh_usual_cons_exp_mnth",
            "multiplier",
        ],
    )
    visits = visits.loc[visits["questionnaire_num"].isin(QUESTIONNAIRES)]
    if visits.duplicated(["hhid", "questionnaire_num"]).any():
        raise ValueError("duplicate household questionnaire rows in level_15")
    counts = visits.groupby("hhid")["questionnaire_num"].nunique().reindex(hhids)
    if counts.isna().any() or not counts.eq(len(QUESTIONNAIRES)).all():
        raise ValueError(
            "FDQ, CSQ and DGQ questionnaires are not complete for every household"
        )
    sizes = visits.pivot(
        index="hhid", columns="questionnaire_num", values="hh_size"
    ).reindex(hhids)
    if sizes.isna().any().any() or not sizes.gt(0).all().all():
        raise ValueError("missing or non-positive questionnaire household size")
    third = visits.loc[visits["visit"].eq(3)]
    if third["hhid"].duplicated().any() or set(third["hhid"]) != set(hhids):
        raise ValueError("each household needs exactly one third-visit questionnaire")
    multiplier = third.set_index("hhid")["multiplier"].reindex(hhids)

    summary = _read(
        clean_dir, "14", ["hhid", "questionnaire_num", "section", "item_code", "value"]
    )
    if not set(summary["hhid"]) <= set(hhids):
        raise ValueError("level_14 holds households absent from level_01")
    if summary["value"].isna().any() or summary["value"].lt(0).any():
        raise ValueError("missing or negative expenditure summary value in level_14")
    summary = summary.loc[~summary["item_code"].isin(codes.EXCLUDED_EXPENDITURE_CODES)]
    pairs = summary[["section", "item_code"]].drop_duplicates()
    pairs["recall"] = [
        codes.expenditure_recall_days(section, item)
        for section, item in zip(pairs["section"], pairs["item_code"])
    ]
    summary = summary.merge(pairs, on=["section", "item_code"], validate="many_to_one")
    summary["monthly"] = summary["value"] * codes.DAYS_PER_MONTH / summary["recall"]
    totals = (
        summary.groupby(["hhid", "questionnaire_num"])["monthly"]
        .sum()
        .unstack("questionnaire_num")
        .reindex(index=hhids, columns=list(QUESTIONNAIRES))
    )
    absent_food_block = totals["F"].isna()
    totals = totals.fillna(0.0)
    total = (
        totals["F"]
        + totals["C"] / sizes["C"] * sizes["F"]
        + totals["D"] / sizes["D"] * sizes["F"]
    )
    usual = (
        visits.loc[visits["questionnaire_num"].eq("F")]
        .set_index("hhid")["hh_usual_cons_exp_mnth"]
        .reindex(hhids)
    )
    return pd.DataFrame(
        {
            "multiplier": multiplier,
            "p1": sizes["F"],
            "e1": totals["F"],
            "e2": totals["C"],
            "e3": totals["D"],
            "te": total.mask(absent_food_block),
            "mpce_inr": (total / sizes["F"]).mask(absent_food_block),
            "mpce_status": np.where(absent_food_block, "MISSING_FDQ", "OK"),
            "usual_monthly_inr": usual,
            "absent_food_block": absent_food_block,
        },
        index=hhids,
    )


def _items(clean_dir: Path, level: str) -> pd.DataFrame:
    """Read the protein item rows of one level and check keys and values."""
    item_codes = sorted(
        {
            code
            for group, values in codes.GROUPS.items()
            if codes.GROUP_LEVEL[group] == level
            for code in values
        }
    )
    home = ["cons_home_qty", "cons_home_value"] if level == "05" else []
    rows = _read(
        clean_dir,
        level,
        ["hhid", "item_code", "cons_total_qty", "cons_total_value", *home],
        filters=[("item_code", "in", item_codes)],
    )
    if rows.duplicated(["hhid", "item_code"]).any():
        raise ValueError(
            f"duplicate household item rows in level_{level} would double count"
        )
    for column in ("cons_total_qty", "cons_total_value", *home):
        rows[column] = rows[column].astype(float)
        if rows[column].lt(0).any():
            raise ValueError(f"negative {column} in level_{level}")
        if np.isinf(rows[column]).any():
            raise ValueError(f"non-finite {column} in level_{level}")
    if home:
        home_qty = _home_part(rows["cons_home_qty"], rows["cons_home_value"])
        home_value = _home_part(rows["cons_home_value"], rows["cons_home_qty"])
        if (
            rows["cons_home_qty"].gt(rows["cons_total_qty"]).any()
            or rows["cons_home_value"].gt(rows["cons_total_value"]).any()
        ):
            raise ValueError(f"home produce exceeds total consumption in level_{level}")
    else:
        home_qty = home_value = pd.Series(0.0, index=rows.index)
    rows["purchase_qty"] = rows["cons_total_qty"] - home_qty
    rows["purchase_value"] = rows["cons_total_value"] - home_value
    free = rows["item_code"].isin(codes.FREE_ITEM_CODES)
    rows["value_used"] = rows["cons_total_value"].mask(
        free & rows["cons_total_value"].isna(), 0.0
    )
    return rows


def _home_part(part: pd.Series, other: pd.Series) -> pd.Series:
    """Home-produce part: blank counts as 0 only when the paired field is blank or 0."""
    blank_pair = other.isna() | other.eq(0)
    return part.mask(part.isna() & blank_pair, 0.0)


def _sum_or_missing(frame: pd.DataFrame, column: str) -> pd.Series:
    """Sum a column per household; missing if any contributing row is missing."""
    total = frame.groupby("hhid")[column].sum(min_count=1)
    missing = frame[column].isna().groupby(frame["hhid"]).any()
    return total.mask(missing)


def _group_columns(rows: pd.DataFrame, group: str, hhids: pd.Index) -> pd.DataFrame:
    """Return monthly quantity, monthly value and unit value for one group."""
    days = codes.RECALL_DAYS[group]
    mine = rows.loc[rows["item_code"].isin(codes.GROUPS[group])]
    value_raw = _sum_or_missing(mine, "value_used").reindex(hhids)
    counted = mine.loc[mine["item_code"].isin(codes.QUANTITY_CODES[group])]
    qty_raw = _sum_or_missing(counted, "cons_total_qty").reindex(hhids).astype(float)
    market = mine.loc[mine["item_code"].isin(codes.UNIT_VALUE_CODES[group])]
    bought_qty = _sum_or_missing(market, "purchase_qty").reindex(hhids).astype(float)
    bought_value = (
        _sum_or_missing(market, "purchase_value").reindex(hhids).astype(float)
    )
    unit_value = (bought_value / bought_qty).where(
        bought_qty.gt(0) & bought_value.notna()
    )
    return pd.DataFrame(
        {
            f"qty_month_{group}": qty_raw * codes.DAYS_PER_MONTH / days,
            f"value_month_{group}": value_raw.astype(float)
            * codes.DAYS_PER_MONTH
            / days,
            f"unit_value_{group}": unit_value,
        },
        index=hhids,
    )


def _build(clean_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return the household table, the MPCE frame and the household frame."""
    households = _households(clean_dir)
    hhids = pd.Index(households["hhid"], name="hhid")
    mpce = mpce_frame(clean_dir, hhids)
    if not households.set_index("hhid")["hh_size"].eq(mpce["p1"]).all():
        raise ValueError("level_03 household size differs from the FDQ household size")
    item_rows = {
        level: _items(clean_dir, level)
        for level in sorted(set(codes.GROUP_LEVEL.values()))
    }
    for level, rows in item_rows.items():
        if not set(rows["hhid"]) <= set(hhids):
            raise ValueError(f"level_{level} holds households absent from level_01")
    groups = pd.concat(
        [
            _group_columns(item_rows[codes.GROUP_LEVEL[g]], g, hhids)
            for g in codes.GROUPS
        ],
        axis=1,
    )
    base = households.set_index("hhid")
    table = pd.DataFrame(
        {
            "state": base["state"],
            "district": base["district"],
            "sector": base["sector"],
            "multiplier": mpce["multiplier"],
            "hh_size": base["hh_size"],
            "religion": base["religion"],
            "caste": base["caste"],
            "mpce_inr": mpce["mpce_inr"],
            "mpce_local": mpce["mpce_inr"],
            "mpce_status": mpce["mpce_status"],
            "currency": "INR",
            "psu": base["fsu_serial_no"],
            "stratum": base["stratum"],
            "sub_stratum": base["sub_stratum"],
            "stratum_status": "RESOLVED",
        },
        index=hhids,
    )
    table = pd.concat([table, groups], axis=1).reset_index()
    ordered = list(BASE_COLUMNS) + [
        f"{k}_{g}" for g in codes.GROUPS for k in GROUP_KINDS
    ]
    return table[ordered], mpce, households


def build_india_households(clean_dir: Path) -> pd.DataFrame:
    """Return one row per household with MPCE and monthly protein-group columns."""
    return _build(Path(clean_dir))[0]


MIN_CELL_HOUSEHOLDS = 30


def _cell(
    values: pd.Series, weights: pd.Series, minimum: int
) -> tuple[float | None, int]:
    """Weighted mean over non-missing values and its unweighted household count.

    The mean is None when fewer than ``minimum`` households contribute (R16).
    """
    present = values.notna()
    count = int(present.sum())
    if count == 0 or count < minimum:
        return None, count
    mean = (values[present] * weights[present]).sum() / weights[present].sum()
    return round(float(mean), 4), count


def state_summary(
    table: pd.DataFrame, min_households: int = MIN_CELL_HOUSEHOLDS
) -> dict:
    """Return weighted state-level means; no household row or sub-state cell.

    Every cell carries its unweighted household count. A cell with fewer than
    ``min_households`` households has a null value and keeps its count (R16).
    """
    states = {}
    for state, frame in table.groupby("state", sort=True):
        weight = frame["multiplier"].astype(float)
        groups = {}
        for group in codes.GROUPS:
            reported = frame[f"value_month_{group}"].notna()
            n_reporting = int(reported.sum())
            share = round(float(weight[reported].sum() / weight.sum()), 6)
            value, n_value = _cell(
                frame[f"value_month_{group}"], weight, min_households
            )
            qty, n_qty = _cell(frame[f"qty_month_{group}"], weight, min_households)
            unit, n_unit = _cell(frame[f"unit_value_{group}"], weight, min_households)
            groups[group] = {
                "n_reporting": n_reporting,
                "reporting_share": share if n_reporting >= min_households else None,
                "n_value": n_value,
                "mean_value_month_inr_reporting": value,
                "n_qty": n_qty,
                "mean_qty_month_reporting": qty,
                "n_unit_value": n_unit,
                "mean_unit_value_inr": unit,
            }
        persons = weight * frame["hh_size"]
        mpce, n_mpce = _cell(frame["mpce_inr"], persons, min_households)
        states[str(int(state))] = {
            "n_households": len(frame),
            "n_mpce": n_mpce,
            "mean_mpce_inr": mpce,
            "groups": groups,
        }
    return {
        "status": "DIAGNOSTIC",
        "source": "HCES 2023-24 unit-level clean parquet, levels 01, 03, 05, 06, 14 and 15",
        "weight": "third-visit multiplier",
        "min_cell_households": min_households,
        "suppression": (
            "a cell with fewer than min_cell_households unweighted households is null; "
            "its unweighted count n_* is kept (ruling R16)"
        ),
        "mean_mpce_definition": (
            "person-weighted over households with mpce_status OK: "
            "sum(w * MPCE * hh_size) / sum(w * hh_size)"
        ),
        "group_mean_definition": (
            "household-weighted means among households reporting the group; "
            "reporting_share is the weighted share reporting it; unreported items are not zero-filled"
        ),
        "unit_value_definition": (
            "market purchases only: cons_total minus cons_home; pulses leave out PDS 158 "
            "and free 071 and 072 (rulings R15, R17)"
        ),
        "units": {group: codes.GROUP_UNITS[group] for group in codes.GROUPS},
        "recall_days": dict(codes.RECALL_DAYS),
        "households": len(table),
        "states": states,
    }


def run_log(table: pd.DataFrame, mpce: pd.DataFrame, households: pd.DataFrame) -> dict:
    """Return national diagnostics: counts, MPCE validation and published comparison."""
    usual = mpce["usual_monthly_inr"].astype(float)
    ok = usual.notna() & usual.gt(0) & mpce["te"].gt(0) & mpce["mpce_inr"].notna()
    sector = households.set_index("hhid")["sector"].reindex(mpce.index)
    published = {}
    for code, name in ((1, "rural"), (2, "urban")):
        part = mpce.loc[sector.eq(code) & mpce["mpce_inr"].notna()]
        persons = part["multiplier"] * part["p1"]
        estimate = float((part["mpce_inr"] * persons).sum() / persons.sum())
        published[name] = {
            "estimate_inr": round(estimate, 1),
            "published_inr": PUBLISHED_MPCE_INR[name],
            "difference_inr": round(estimate - PUBLISHED_MPCE_INR[name], 1),
        }
    return {
        "households": len(table),
        "mpce_validation": {
            "field": "level_15 FDQ hh_usual_cons_exp_mnth (informant's usual monthly household expenditure)",
            "households_compared": int(ok.sum()),
            "pearson_household_total": round(
                float(np.corrcoef(mpce["te"][ok], usual[ok])[0, 1]), 4
            ),
            "pearson_log_household_total": round(
                float(np.corrcoef(np.log(mpce["te"][ok]), np.log(usual[ok]))[0, 1]), 4
            ),
            "pearson_per_capita": round(
                float(
                    np.corrcoef(mpce["mpce_inr"][ok], (usual / mpce["p1"])[ok])[0, 1]
                ),
                4,
            ),
        },
        "published_mpce_comparison": published,
        "households_mpce_status": {
            status: int(count)
            for status, count in table["mpce_status"]
            .value_counts()
            .sort_index()
            .items()
        },
        "households_without_fdq_summary_rows": int(mpce["absent_food_block"].sum()),
        "households_with_zero_csq_total": int(mpce["e2"].eq(0).sum()),
        "households_with_zero_dgq_total": int(mpce["e3"].eq(0).sum()),
        "multiplier_differs_from_level_01": int(
            (
                households.set_index("hhid")["multiplier"].reindex(mpce.index)
                != mpce["multiplier"]
            ).sum()
        ),
        "religion_not_reported": int(table["religion"].isna().sum()),
        "caste_not_reported": int(table["caste"].isna().sum()),
        "households_reporting_group": {
            group: int(table[f"value_month_{group}"].notna().sum())
            for group in codes.GROUPS
        },
        "households_with_unit_value": {
            group: int(table[f"unit_value_{group}"].notna().sum())
            for group in codes.GROUPS
        },
    }


def _sha256(path: Path) -> str:
    """Hash one file in chunks."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    """Write indented JSON with a trailing newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def _resolve_here(value: str) -> Path:
    """Resolve a relative summary or log path against the household-demand folder."""
    path = Path(value)
    return path if path.is_absolute() else HERE / path


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point: write household rows, state summary and run log."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--clean-dir",
        required=True,
        help="HCES 04_clean folder (relative to the working directory)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="household parquet path outside the repository (relative to the working directory)",
    )
    parser.add_argument(
        "--summary",
        required=True,
        help="state summary JSON (relative paths resolve against research/household-demand/)",
    )
    parser.add_argument(
        "--log",
        default="logs/india-households-run.json",
        help="run log JSON (relative paths resolve against research/household-demand/)",
    )
    args = parser.parse_args(argv)
    out = Path(args.out).resolve()
    if out.is_relative_to(LIBRARY_ROOT):
        parser.error(f"household rows must be written outside the repository: {out}")
    summary_path = _resolve_here(args.summary)
    log_path = _resolve_here(args.log)

    table, mpce, households = _build(Path(args.clean_dir))
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(out, index=False)
    summary = state_summary(table)
    _write_json(summary_path, summary)
    log = {
        "status": "DIAGNOSTIC",
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "clean_dir": args.clean_dir,
        "household_table": {
            "path": args.out,
            "rows": len(table),
            "sha256": _sha256(out),
        },
        "summary": {
            "path": str(summary_path.relative_to(LIBRARY_ROOT)),
            "sha256": _sha256(summary_path),
        },
        **run_log(table, mpce, households),
    }
    _write_json(log_path, log)
    validation = log["mpce_validation"]
    print(
        f"households={len(table)} "
        f"mpce_vs_usual_pearson={validation['pearson_household_total']} "
        f"log_pearson={validation['pearson_log_household_total']} "
        f"rural={log['published_mpce_comparison']['rural']['estimate_inr']} "
        f"urban={log['published_mpce_comparison']['urban']['estimate_inr']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
