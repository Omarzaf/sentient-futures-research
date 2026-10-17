"""Localize baseline differences using aggregate item and source-record diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from inspect_hces import THIRTY_DAY_CODES
from reproduce_india_baseline import EXCLUDED_CODES, _identity, cpi_recipe

__all__ = ["diagnose"]


def diagnose(candidate: Path, output: Path) -> dict:
    """Save only aggregate item contributions and sparse-household source checks."""
    root = candidate / "04_clean"
    factors = pd.DataFrame.from_records(
        json.loads((output / "factor-table.json").read_text())
    )
    cpi, _ = cpi_recipe(json.loads((output / "cpi-data.json").read_text()))
    info = pd.read_parquet(root / "level_01.parquet", columns=["hhid", "sector"])
    visits = pd.read_parquet(root / "level_15.parquet")
    households = (
        info.merge(
            visits.loc[
                visits["visit"].eq(3)
                & visits["questionnaire_num"].isin(["F", "C", "D"]),
                ["hhid", "multiplier"],
            ],
            on="hhid",
            validate="one_to_one",
        )
        .merge(
            visits.loc[visits["questionnaire_num"].eq("F"), ["hhid", "hh_size"]],
            on="hhid",
            validate="one_to_one",
        )
        .assign(weight=lambda d: d["multiplier"] / 100)
    )
    denominator = (
        households.assign(person_weight=lambda d: d["weight"] * d["hh_size"])
        .groupby("sector")["person_weight"]
        .sum()
    )
    ids, weights, sectors = (
        pa.array(households["hhid"]),
        pa.array(households["weight"]),
        pa.array(households["sector"]),
    )
    sparse_sets, pieces, source_checks = [], [], []
    for level in ["05", "06", "10"]:
        table = pq.read_table(
            root / f"level_{level}.parquet",
            columns=["hhid", "item_code", "cons_total_qty", "cons_total_value"],
        )
        applicable = pc.is_in(
            table["item_code"], value_set=pa.array(sorted(set(factors["item_code"])))
        )
        mapped = table.filter(applicable)
        sparse_sets.append(set(mapped["hhid"].unique().to_pylist()))
        index = pc.index_in(mapped["hhid"], value_set=ids)
        if index.null_count:
            raise ValueError("Food record lacks a household design/weight key")
        sector = pc.take(sectors, index)
        row_weights = pc.take(weights, index)
        codes = sorted(set(factors["item_code"]))
        lookup = pc.index_in(mapped["item_code"], value_set=pa.array(codes))
        coefficients = {}
        for name in ["rural", "urban"]:
            selected = factors.loc[factors["sector"].isin(["all", name])].set_index(
                "item_code"
            )
            coefficients[name] = pa.array(selected.loc[codes, "protein_g_per_unit"])
        monetary_codes = pa.array(
            sorted(set(factors.loc[factors["unit"].eq("Re."), "item_code"]))
        )
        is_money = pc.is_in(mapped["item_code"], value_set=monetary_codes)
        values = pc.if_else(
            is_money, mapped["cons_total_value"], mapped["cons_total_qty"]
        )
        coefficient = pc.if_else(
            pc.equal(sector, 1),
            pc.take(coefficients["rural"], lookup),
            pc.take(coefficients["urban"], lookup),
        )
        inflation = pc.if_else(
            pc.equal(sector, 1),
            cpi["sectors"]["rural"]["coefficient_multiplier"],
            cpi["sectors"]["urban"]["coefficient_multiplier"],
        )
        coefficient = pc.if_else(
            is_money, pc.multiply(coefficient, inflation), coefficient
        )
        recall = (
            pc.if_else(
                pc.is_in(
                    mapped["item_code"], value_set=pa.array(sorted(THIRTY_DAY_CODES))
                ),
                30.0,
                7.0,
            )
            if level == "05"
            else pa.scalar(7.0)
        )
        protein = pc.divide(pc.multiply(values, coefficient), recall)
        grouped = (
            pa.table(
                {
                    "sector": sector,
                    "item_code": mapped["item_code"],
                    "weighted_protein": pc.multiply(protein, row_weights),
                }
            )
            .group_by(["sector", "item_code"], use_threads=False)
            .aggregate([("weighted_protein", "sum")])
            .to_pandas()
        )
        grouped["g_person_day"] = grouped["weighted_protein_sum"] / grouped[
            "sector"
        ].map(denominator)
        grouped["level"] = level
        pieces.append(grouped)
        source_checks.append(
            {
                "level": level,
                "all_rows": table.num_rows,
                "mapped_rows": mapped.num_rows,
                "excluded_rows": table.num_rows - mapped.num_rows,
                "excluded_codes": sorted(
                    EXCLUDED_CODES[level] & set(table["item_code"].unique().to_pylist())
                ),
            }
        )
    item = pd.concat(pieces, ignore_index=True).sort_values(
        ["sector", "level", "item_code"]
    )
    # Questionnaire section-based groups; bread113 and baby food161 stay processed.
    item["food_group"] = np.select(
        [
            item["level"].eq("05")
            & (
                item["item_code"].isin([1, 2, 61, 62, 70, 139])
                | item["item_code"].between(101, 122)
            ),
            item["level"].eq("05")
            & (item["item_code"].isin([71, 72]) | item["item_code"].between(140, 158)),
            item["level"].eq("05")
            & (item["item_code"].between(3, 7) | item["item_code"].between(160, 167)),
            item["level"].eq("05") & item["item_code"].between(190, 196),
        ],
        ["cereals", "pulses", "milk", "egg_fish_meat"],
        default="other",
    )
    groups = item.groupby(["sector", "food_group"], as_index=False)[
        "g_person_day"
    ].sum()
    groups["share_percent"] = (
        groups["g_person_day"]
        / groups["sector"].map(item.groupby("sector")["g_person_day"].sum())
        * 100
    )
    no_food = set(households["hhid"]) - set.union(*sparse_sets)
    sparse = {"no_mapped_food_households": len(no_food), "source_levels": []}
    for level in ["05", "06", "10"]:
        records = pq.read_table(
            root / f"level_{level}.parquet",
            filters=[("hhid", "in", sorted(no_food))],
            columns=["hhid", "item_code", "cons_total_qty", "cons_total_value"],
        )
        sparse["source_levels"].append(
            {
                "level": level,
                "source_rows": records.num_rows,
                "distinct_households": len(records["hhid"].unique()),
                "source_item_codes": sorted(records["item_code"].unique().to_pylist()),
                "positive_quantity_rows": int(
                    pc.sum(
                        pc.cast(
                            pc.fill_null(
                                pc.greater(records["cons_total_qty"], 0), False
                            ),
                            pa.int64(),
                        )
                    ).as_py()
                    or 0
                ),
                "positive_value_rows": int(
                    pc.sum(
                        pc.cast(
                            pc.fill_null(
                                pc.greater(records["cons_total_value"], 0), False
                            ),
                            pa.int64(),
                        )
                    ).as_py()
                    or 0
                ),
            }
        )
    sizes = visits.loc[visits["questionnaire_num"].isin(["F", "C", "D"])].pivot(
        index="hhid", columns="questionnaire_num", values="hh_size"
    )
    ddm = []
    for parent, children in [
        (92, [6, 7, 167]),
        (93, [235, 233, 227, 221, 234, 223, 238]),
        (94, [8, 10, 247]),
        (95, [180, 185]),
    ]:
        rows = pq.read_table(
            root / "level_05.parquet",
            columns=["hhid", "item_code", "cons_total_value"],
            filters=[("item_code", "in", [parent, *children])],
        ).to_pandas()
        rows["kind"] = np.where(rows["item_code"].eq(parent), "parent", "children")
        wide = (
            rows.groupby(["hhid", "kind"])["cons_total_value"]
            .sum(min_count=1)
            .unstack("kind")
        )
        both = wide.dropna(subset=["parent", "children"])
        discrepancy = both["parent"] - both["children"]
        ddm.append(
            {
                "parent_code": parent,
                "child_codes": children,
                "households_with_parent_and_child_values": len(both),
                "discrepancy_over_one_rupee_households": int(
                    discrepancy.abs().gt(1).sum()
                ),
                "parent_without_child_households": int(
                    (wide["parent"].notna() & wide["children"].isna()).sum()
                ),
                "child_without_parent_households": int(
                    (wide["children"].notna() & wide["parent"].isna()).sum()
                ),
                "missing_observed_values": int(rows["cons_total_value"].isna().sum()),
                "net_parent_minus_children_rupees_unweighted": float(discrepancy.sum()),
            }
        )
    meal_columns = ["meals_school", "meals_employer", "meals_others", "meals_payment"]
    roster = pd.read_parquet(root / "level_02.parquet", columns=["hhid", *meal_columns])
    meal_quality = {
        "scope": "All H roster as a source localization diagnostic, not validated FDQ-time member selection",
        "negative_observed_away_meal_counts": int(
            roster[meal_columns].lt(0).sum().sum()
        ),
        "missing_person_cells": int(roster[meal_columns].isna().sum().sum()),
        "observed_only_away_meals_g_person_day": {},
    }
    observed = (
        roster.assign(observed_away_meals=roster[meal_columns].sum(axis=1, min_count=1))
        .groupby("hhid", as_index=False)["observed_away_meals"]
        .sum(min_count=1)
    )
    meal_hh = households.merge(observed, on="hhid", validate="one_to_one", how="left")
    meal_quality["households_without_any_observed_away_meal_cell"] = int(
        meal_hh["observed_away_meals"].isna().sum()
    )
    meal_totals = (
        meal_hh.assign(
            observed_weighted_meals=lambda d: d["weight"]
            * d["observed_away_meals"]
            * 25
            / 30
        )
        .groupby("sector")["observed_weighted_meals"]
        .sum(min_count=1)
    )
    meal_quality["observed_only_away_meals_g_person_day"] = {
        str(sector): float(meal_totals.loc[sector] / denominator.loc[sector])
        for sector in denominator.index
    }
    meal_quality["food_questionnaire_meal_g_person_day"] = (
        item.loc[item["level"].eq("06") & item["item_code"].isin([76, 280, 281, 282])]
        .groupby("sector")["g_person_day"]
        .sum()
        .to_dict()
    )
    result = {
        "source_checks": source_checks,
        "food_group_contributions": groups.to_dict(orient="records"),
        "sparse_records": sparse,
        "drop_down_menu_value_reconciliation": ddm,
        "meal_source_localization": meal_quality,
        "household_size_consistency": {
            "F_vs_C_different_households": int(sizes["F"].ne(sizes["C"]).sum()),
            "F_vs_D_different_households": int(sizes["F"].ne(sizes["D"]).sum()),
        },
        "producer": _identity(Path(__file__)),
        "sources": [
            _identity(root / f"level_{level}.parquet")
            for level in ["01", "02", "05", "06", "10", "15"]
        ]
        + [
            _identity(output / "factor-table.json"),
            _identity(output / "cpi-data.json"),
        ],
        "household_rows_exported": 0,
    }
    item.drop(columns="weighted_protein_sum").to_csv(
        output / "item-contributions.csv", index=False
    )
    (output / "reconstruction-diagnostic.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(diagnose(args.candidate_dir, args.output_dir), indent=2))
