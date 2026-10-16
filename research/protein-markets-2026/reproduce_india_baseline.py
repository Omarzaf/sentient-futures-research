"""Reconstruct unadjusted HCES protein using physical and monetary source factors."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from inspect_hces import (
    DESIGN,
    REPORT_SHA256,
    THIRTY_DAY_CODES,
    parse_factors,
    parse_target_definition,
    verify_candidate,
)

__all__ = [
    "cpi_recipe",
    "mapped_component",
    "ratio_estimate",
    "reconstruct",
    "roster_meal_diagnostic",
    "verify_cpi_capture",
]

# Questionnaire FDQ pp24–37: grain children roll into source-factor parents;
# 092–095 are drop-down parents; the remaining codes here are printed subtotals.
# CSQ pp47–48: tobacco has no nutrient factor, and320/325 are expressly excluded
# by Report594 section2.9.8.1. These are exclusions, never additional zero foods.
EXCLUDED_CODES = {
    "05": set(range(55, 61))
    | set(range(63, 69))
    | {
        92,
        93,
        94,
        95,
        115,
        116,
        117,
        118,
        120,
        121,
        129,
        159,
        169,
        179,
        189,
        199,
        219,
        239,
        249,
        269,
        279,
    },
    "06": {289, 299},
    "10": {309, 310, 311, 312, 313, 314, 315, 316, 317, 319, 320, 325, 329},
}


def _identity(path: Path) -> dict:
    """Bind an input or producer to exact local bytes."""
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def cpi_recipe(payload: dict, group: str = "General") -> tuple[dict, pd.DataFrame]:
    """Calculate a predeclared December2024/survey-average sector CPI ratio."""
    data = pd.DataFrame.from_records(payload["data"])
    if len(data) != payload["api_record_count"]:
        raise ValueError("CPI record count differs from its capture receipt")
    data = data.assign(
        month_num=data["month"].map(
            {name: i for i, name in enumerate(calendar.month_name) if name}
        ),
        index=pd.to_numeric(data["index"], errors="coerce"),
    )
    selected = data.loc[
        data["group"].eq(group) & data["subgroup"].eq(group + "-Overall")
    ].copy()
    if selected.empty and group == "General":
        selected = data.loc[data["group"].eq(group)].copy()
    if (
        not selected["baseyear"].eq("2012").all()
        or not selected["state"].eq("All India").all()
        or not selected["status"].eq("F").all()
    ):
        raise ValueError("CPI series must be final, all-India, and2012-base")
    if selected.duplicated(["sector", "year", "month_num"]).any():
        raise ValueError("Ambiguous CPI monthly series")
    selected["period"] = pd.to_datetime(
        {"year": selected["year"], "month": selected["month_num"], "day": 1}
    ).dt.strftime("%Y-%m")
    required = {f"2023-{month:02}" for month in range(8, 13)} | {
        f"2024-{month:02}" for month in range(1, 8)
    }
    result = {}
    for sector in ["Rural", "Urban"]:
        sample = selected.loc[
            selected["sector"].eq(sector) & selected["period"].isin(required)
        ]
        base = selected.loc[
            selected["sector"].eq(sector) & selected["period"].eq("2024-12"), "index"
        ]
        if (
            set(sample["period"]) != required
            or len(sample) != 12
            or len(base) != 1
            or sample["index"].isna().any()
            or not np.isfinite(sample["index"]).all()
            or not sample["index"].gt(0).all()
            or not math.isfinite(float(base.iloc[0]))
            or not float(base.iloc[0]) > 0
        ):
            raise ValueError("Missing, duplicate or invalid CPI survey/reference month")
        average = float(sample["index"].mean())
        result[sector.lower()] = {
            "survey_months": 12,
            "average_cpi": average,
            "december_2024_cpi": float(base.iloc[0]),
            "coefficient_multiplier": float(base.iloc[0]) / average,
        }
    return {
        "group": group,
        "base_year": "2012=100",
        "period": "2023-08 through2024-07",
        "rule": "December2024 CPI / arithmetic survey-period average CPI; converts nominal survey rupees into December2024 price-equivalent purchasing power",
        "sectors": result,
    }, selected.loc[selected["period"].isin(required | {"2024-12"})].sort_values(
        ["sector", "period"]
    ).reset_index(
        drop=True
    )


def verify_cpi_capture(payload: dict, path: Path) -> None:
    """Verify that the computational CPI input exactly combines its captured pages."""
    records, names = [], set()
    for record in payload["source_pages"]:
        name = record["file"]
        if not re.fullmatch(r"cpi-page-\d{2}\.json", name) or name in names:
            raise ValueError("Invalid or duplicate captured CPI page")
        names.add(name)
        page_path = path.parent / "raw" / name
        if _identity(page_path)["sha256"] != record["sha256"]:
            raise ValueError("Captured CPI page identity mismatch")
        page = json.loads(page_path.read_text())
        if page.get("statusCode") is not True:
            raise ValueError("Captured CPI page is not a successful response")
        records.extend(page["data"])
    if (
        not names
        or records != payload["data"]
        or len(records) != payload["api_record_count"]
        or len(records) != int(page["meta_data"]["totalRecords"])
        or len(names) != int(page["meta_data"]["totalPages"])
    ):
        raise ValueError("Computational CPI input differs from complete captured pages")


def _count_true(values: pa.Array | pa.ChunkedArray) -> int:
    """Count a Boolean Arrow mask without exporting source records."""
    return int(pc.sum(pc.cast(values, pa.int64())).as_py() or 0)


def mapped_component(
    path: Path, factors: pd.DataFrame, level: str, monetary: bool
) -> tuple[pd.DataFrame, dict]:
    """Map every applicable source row and aggregate in Arrow before pandas."""
    selected = factors.loc[
        factors["unit"].eq("Re.") if monetary else factors["unit"].ne("Re.")
    ]
    codes = sorted(int(code) for code in selected["item_code"].unique())
    value_col = "cons_total_value" if monetary else "cons_total_qty"
    table = pq.read_table(
        path,
        columns=["hhid", "item_code", value_col],
        filters=[("item_code", "in", codes)],
    )
    valid = table[value_col]
    if table["hhid"].null_count or table["item_code"].null_count:
        raise ValueError("Missing household/item key")
    if _count_true(
        pc.or_(pc.less(table["item_code"], 0), pc.greater(table["item_code"], 999))
    ):
        raise ValueError("Food item key exceeds the source three-digit code width")
    encoded_keys = pc.add_checked(
        pc.multiply_checked(table["hhid"], 1000), table["item_code"]
    )
    duplicate_keys = table.num_rows - int(pc.count_distinct(encoded_keys).as_py())
    quality = {
        "level": level,
        "kind": "monetary" if monetary else "physical",
        "rows": table.num_rows,
        "missing_observed_values": valid.null_count,
        "negative_observed_values": _count_true(pc.less(valid, 0)),
        "nonfinite_observed_values": _count_true(pc.invert(pc.is_finite(valid))),
        "duplicate_household_item_keys": duplicate_keys,
        "source_field": value_col,
    }
    if duplicate_keys:
        raise ValueError("Duplicate household/item key would double count consumption")
    if (
        quality["missing_observed_values"]
        or quality["negative_observed_values"]
        or quality["nonfinite_observed_values"]
    ):
        raise ValueError(
            "Invalid observed food values; no imputation permitted: "
            + json.dumps(quality)
        )
    if table.num_rows == 0:
        return pd.DataFrame(columns=["hhid"]), quality
    days = (
        pc.if_else(
            pc.is_in(table["item_code"], value_set=pa.array(sorted(THIRTY_DAY_CODES))),
            30.0,
            7.0,
        )
        if level == "05"
        else pa.scalar(7.0)
    )
    lookup = pc.index_in(table["item_code"], value_set=pa.array(codes))
    columns = []
    for sector in (["rural", "urban"] if monetary else ["all"]):
        subset = selected.loc[selected["sector"].eq(sector)].set_index("item_code")
        coefficient = pa.array(subset.loc[codes, "protein_g_per_unit"].tolist())
        contribution = pc.divide(pc.multiply(valid, pc.take(coefficient, lookup)), days)
        name = "monetary_" + sector if monetary else "physical"
        table = table.append_column(name, contribution)
        columns.append(name)
    grouped = table.group_by("hhid", use_threads=False).aggregate(
        [(name, "sum") for name in columns] + [("item_code", "count")]
    )
    return (
        grouped.to_pandas().rename(
            columns={name + "_sum": name for name in columns}, errors="raise"
        ),
        quality,
    )


def ratio_estimate(households: pd.DataFrame, outcome: str) -> dict:
    """Estimate a person-denominator ratio and explicit with-replacement PSU SE."""
    if (
        households[[outcome, "hh_size", "final_weight", *DESIGN]].isna().any().any()
        or not households[["hh_size", "final_weight"]].gt(0).all().all()
    ):
        raise ValueError(
            "Incomplete outcome, positive denominator/weight or design: "
            + json.dumps(
                households[[outcome, "hh_size", "final_weight", *DESIGN]]
                .isna()
                .sum()
                .to_dict()
            )
        )
    denominator = float((households["hh_size"] * households["final_weight"]).sum())
    value = (
        float((households[outcome] * households["final_weight"]).sum()) / denominator
    )
    frame = households.assign(
        residual=households["final_weight"]
        * (households[outcome] - value * households["hh_size"])
    )
    strata = ["sector", "state", "stratum", "sub_stratum"]
    clusters = frame.groupby([*strata, "fsu_serial_no"], as_index=False)[
        "residual"
    ].sum()
    grouped = (
        clusters.assign(square=clusters["residual"] ** 2)
        .groupby(strata, as_index=False)
        .agg(
            n=("residual", "size"), total=("residual", "sum"), squares=("square", "sum")
        )
    )
    lonely = int(grouped["n"].eq(1).sum())
    variance = (
        None
        if lonely
        else float(
            (
                grouped["n"]
                / (grouped["n"] - 1)
                * (grouped["squares"] - grouped["total"] ** 2 / grouped["n"])
            ).sum()
        )
        / denominator**2
    )
    return {
        "estimate_g_person_day": value,
        "households": len(households),
        "PSUs": len(clusters),
        "strata": len(grouped),
        "singleton_strata": lonely,
        "approximate_WR_cluster_SE": (
            math.sqrt(max(0.0, variance)) if variance is not None else None
        ),
        "variance_method": "Taylor ratio linearization with replacement across SRS first-stage FSUs, stratified by sector/state/stratum/sub_stratum; panels/subsamples pooled; no FPC. Approximation, not the published NSS variance. SE unavailable if any singleton stratum.",
    }


def roster_meal_diagnostic(
    household: pd.DataFrame,
    roster: pd.DataFrame,
    meal_items: pd.DataFrame,
    targets: dict,
) -> dict:
    """Test the report's X+G algebra without claiming unadjusted or blank-field equivalence."""
    columns = ["meals_school", "meals_employer", "meals_others", "meals_payment"]
    if roster[columns].lt(0).any().any():
        raise ValueError("Negative observed away-meal count")
    if roster.duplicated(["hhid", "person_id"]).any():
        raise ValueError("Duplicate roster person key")
    observed = (
        roster.assign(observed_X=roster[columns].sum(axis=1, min_count=1) * 25 / 30)
        .groupby("hhid", as_index=False)["observed_X"]
        .sum(min_count=1)
    )
    work = household.merge(
        observed, on="hhid", how="left", validate="one_to_one"
    ).merge(
        meal_items[["hhid", "physical"]].rename(columns={"physical": "meal_item_g"}),
        on="hhid",
        how="left",
        validate="one_to_one",
        indicator="meal_item_presence",
    )
    work.loc[work["meal_item_presence"].eq("left_only"), "meal_item_g"] = 0.0
    results = {}
    for sector in ["rural", "urban"]:
        domain = work.loc[work["sector_name"].eq(sector)]
        denominator = float((domain["hh_size"] * domain["final_weight"]).sum())
        x = (
            float((domain["observed_X"] * domain["final_weight"]).sum(min_count=1))
            / denominator
        )
        meal = (
            float((domain["meal_item_g"] * domain["final_weight"]).sum()) / denominator
        )
        variants = {}
        for name in ["general", "food_and_beverages"]:
            g = (
                float(
                    (
                        (domain[name] - domain["meal_item_g"]) * domain["final_weight"]
                    ).sum()
                )
                / denominator
            )
            point = x + g
            variants[name] = {
                "estimate_g_person_day": point,
                "difference_from_target": point - targets[sector],
                "within_numerical_tolerance": abs(point - targets[sector]) <= 0.5,
            }
        results[sector] = {
            "observed_X_g_person_day": x,
            "food_item_meal_g_person_day": meal,
            "variants": variants,
        }
    return {
        "name": "observed_roster_X_plus_G_localization_only",
        "source_defined_method": False,
        "complete_unadjusted_estimator": False,
        "target_fitting_used": False,
        "selection_rule": "All level02 H-roster persons, observed nonnegative school/employer/other/payment30-day meal counts; source meal factor25g/count. No membership or CPI variant selected by agreement.",
        "interpretation": "Report5942.9.8.1 defines adjusted Y=X+G*; X+G is its algebra before the G adjustment, but the source does not explicitly state that this is its published unadjusted algorithm. Existing7-day meal source primary remains unchanged.",
        "missing_cell_rule": "Observed-only sum with min_count=1; missing meal cells and all-missing households remain missing. Weighted sum of observed X is divided by the full FDQ person denominator as a localization contribution, not as a validated national intake. No missing cell is filled or claimed zero.",
        "person_rows": len(roster),
        "missing_away_meal_person_cells": int(roster[columns].isna().sum().sum()),
        "all_away_meal_fields_missing_person_rows": int(
            roster[columns].isna().all(axis=1).sum()
        ),
        "households_without_any_observed_away_meal_cell": int(
            work["observed_X"].isna().sum()
        ),
        "strict_complete_away_meal_households": int(
            roster.assign(incomplete=roster[columns].isna().any(axis=1))
            .groupby("hhid")["incomplete"]
            .any()
            .eq(False)
            .sum()
        ),
        "remaining_questions": [
            "Exact FDQ-time member inclusion for merged H-roster",
            "Whether blank away-meal counts are routed zeros or unresolved responses",
            "Whether published unadjusted intake uses X+G rather than7-day food-item meal quantities",
        ],
        "sector_results": results,
    }


def reconstruct(
    candidate: Path, receipt: Path, report: Path, cpi_path: Path, output_dir: Path
) -> dict:
    """Compute all unadjusted components with fixed primary and sensitivity recipes."""
    source = verify_candidate(candidate, receipt)
    if _identity(report)["sha256"] != REPORT_SHA256:
        raise ValueError("Nutrition report identity mismatch")
    text = subprocess.run(
        ["pdftotext", "-layout", str(report), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    factors, definition = parse_factors(text), parse_target_definition(text)
    payload = json.loads(cpi_path.read_text())
    verify_cpi_capture(payload, cpi_path)
    primary, cpi_table = cpi_recipe(payload, "General")
    sensitivity, food_cpi_table = cpi_recipe(payload, "Food and Beverages")
    root = candidate / "04_clean"
    info = pd.read_parquet(root / "level_01.parquet", columns=["hhid", *DESIGN])
    visit = pd.read_parquet(
        root / "level_15.parquet",
        columns=["hhid", "questionnaire_num", "visit", "hh_size", "multiplier"],
    )
    if (
        info["hhid"].duplicated().any()
        or visit.duplicated(["hhid", "questionnaire_num"]).any()
    ):
        raise ValueError("Duplicate household/questionnaire keys")
    complete = (
        visit.loc[visit["questionnaire_num"].isin(["F", "C", "D"])]
        .groupby("hhid")["questionnaire_num"]
        .nunique()
    )
    if not complete.eq(3).all() or set(complete.index) != set(info["hhid"]):
        raise ValueError("Three questionnaires are not complete for every household")
    third = visit.loc[
        visit["visit"].eq(3) & visit["questionnaire_num"].isin(["F", "C", "D"]),
        ["hhid", "multiplier"],
    ]
    fdq = visit.loc[visit["questionnaire_num"].eq("F"), ["hhid", "hh_size"]]
    household = (
        info.merge(third, on="hhid", validate="one_to_one")
        .merge(fdq, on="hhid", validate="one_to_one")
        .assign(final_weight=lambda d: d["multiplier"] / 100)
    )
    quality, physical, monetary = [], [], []
    exclusions = []
    for level in ["05", "06", "10"]:
        path = root / f"level_{level}.parquet"
        observed = set(
            pq.read_table(path, columns=["item_code"])
            .group_by("item_code")
            .aggregate([])["item_code"]
            .to_pylist()
        )
        extra = observed - set(factors["item_code"]) - EXCLUDED_CODES[level]
        if extra:
            raise ValueError(
                f"Unclassified food/item codes in level{level}: {sorted(extra)}"
            )
        exclusions.append(
            {
                "level": level,
                "excluded_observed_codes": sorted(observed & EXCLUDED_CODES[level]),
                "unclassified_codes": [],
            }
        )
        for money, collection in [(False, physical), (True, monetary)]:
            totals, diagnostic = mapped_component(path, factors, level, money)
            quality.append(diagnostic)
            if not totals.empty:
                collection.append(totals)
    physical_sum = (
        pd.concat(physical).groupby("hhid", as_index=False)["physical"].sum(min_count=1)
    )
    money_sum = (
        pd.concat(monetary)
        .groupby("hhid", as_index=False)[
            ["monetary_rural", "monetary_urban", "item_code_count"]
        ]
        .sum(min_count=1)
    )
    if not set(physical_sum["hhid"]).issubset(set(household["hhid"])) or not set(
        money_sum["hhid"]
    ).issubset(set(household["hhid"])):
        raise ValueError("Food source record lacks a completed survey household")
    household = household.merge(
        physical_sum,
        on="hhid",
        how="left",
        validate="one_to_one",
        indicator="physical_presence",
    ).merge(
        money_sum,
        on="hhid",
        how="left",
        validate="one_to_one",
        indicator="monetary_presence",
    )
    absent = household["monetary_presence"].eq("left_only")
    absent_physical = household["physical_presence"].eq("left_only")
    household.loc[absent_physical, "physical"] = 0.0
    household.loc[absent, ["monetary_rural", "monetary_urban"]] = 0.0
    household["monetary_nominal"] = np.where(
        household["sector"].eq(1),
        household["monetary_rural"],
        household["monetary_urban"],
    )
    household["sector_name"] = household["sector"].map({1: "rural", 2: "urban"})
    for name, recipe in [("general", primary), ("food_and_beverages", sensitivity)]:
        multiplier = household["sector_name"].map(
            {
                sector: values["coefficient_multiplier"]
                for sector, values in recipe["sectors"].items()
            }
        )
        household[name] = (
            household["physical"] + household["monetary_nominal"] * multiplier
        )
    estimates = {}
    for sector in ["rural", "urban"]:
        domain = household.loc[household["sector_name"].eq(sector)]
        estimates[sector] = {
            name: ratio_estimate(domain, name)
            for name in [
                "physical",
                "monetary_nominal",
                "general",
                "food_and_beverages",
            ]
        }
    point = {
        sector: values["general"]["estimate_g_person_day"]
        for sector, values in estimates.items()
    }
    comparisons = {
        sector: {
            "target": target,
            "estimate": point[sector],
            "difference": point[sector] - target,
            "tolerance": 0.5,
            "passes": abs(point[sector] - target) <= 0.5,
        }
        for sector, target in definition["unadjusted_target"].items()
    }
    numerical_pass = all(value["passes"] for value in comparisons.values())
    roster = pd.read_parquet(
        root / "level_02.parquet",
        columns=[
            "hhid",
            "person_id",
            "meals_school",
            "meals_employer",
            "meals_others",
            "meals_payment",
        ],
    )
    meal_items, _ = mapped_component(
        root / "level_06.parquet",
        factors.loc[factors["item_code"].isin([76, 280, 281, 282])],
        "06",
        False,
    )
    meal_diagnostic = roster_meal_diagnostic(
        household, roster, meal_items, definition["unadjusted_target"]
    )
    result = {
        "status": "HOLD_METHOD_CONFIRMATION" if numerical_pass else "TARGET_FAILED",
        "estimate_g_person_day": point,
        "complete_unadjusted_estimator": True,
        "source_defined_method": False,
        "target_fitting_used": False,
        "method_status": "Complete source-factor reconstruction with predeclared General-CPI interpretation; report specifies sector CPI and averaging period but not the exact index family/normalization. Food-and-Beverages is retained as an unselected sensitivity.",
        "target_comparison": comparisons,
        "numerical_target_criterion_passed": numerical_pass,
        "target_definition": definition,
        "primary_cpi_recipe": primary,
        "sensitivity_cpi_recipe": sensitivity,
        "sector_results": estimates,
        "meal_source_diagnostic": meal_diagnostic,
        "input_quality": quality,
        "excluded_source_codes": exclusions,
        "absent_monetary_item_households": int(absent.sum()),
        "absent_physical_item_households": int(absent_physical.sum()),
        "no_mapped_food_record_households": int((absent & absent_physical).sum()),
        "sparse_record_rule": "An absent mapped item record contributes no observed quantity/expenditure; only wholly absent component sums initialize to0. Every present quantity/value is nonmissing, nonnegative and finite; no observed missing value is imputed. Households with no level05/06 source records are source-record absences, not independently verified zero actual intake.",
        "weight_rule": "All F/C/D questionnaires completed; third-visit multiplier/100; FDQ household size; ratio of weighted HHprotein to weighted FDQ persons",
        "design_fields": DESIGN,
        "official_raw_identity_verified": False,
        "source_type": "third_party_cleaned_survey_candidate",
        "candidate_commit": source["checkout_commit"],
        "candidate_hashes_verified": len(source["files"]),
        "raw_lineage_note": "Target agreement does not authenticate absent official original text files or rights to redistribute cleaned respondent records",
        "source_support": [
            "Report594Table2.2 supplies all176factor rows, including36 sector-specific monetary rows",
            "Report594printedp21 specifies December2024 prices, averageAug2023–Jul2024 CPI and separate rural/urban indices",
            "Official CPI API provides final2012-base monthly General andFood-and-Beverages series; metadata names both andsectorcodes",
            "Methodology3.5 andReport5942.1 establish third-visit multiplier andFDQ household size",
            "Survey methodology2.2.6 describesSRSWOR first-stageFSUs; reported WRSE is an explicit no-FPC approximation",
        ],
        "sources": [_identity(report), _identity(cpi_path), _identity(receipt)],
        "producer": _identity(Path(__file__)),
        "code_dependencies": [_identity(Path(__file__).with_name("inspect_hces.py"))],
        "household_rows_exported": 0,
        "new_market_estimates_performed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline-receipt.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    pd.concat([cpi_table, food_cpi_table], ignore_index=True).to_csv(
        output_dir / "cpi-selected-series.csv", index=False
    )
    (output_dir / "factor-table.json").write_text(
        json.dumps(factors.to_dict(orient="records"), indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--cpi-data", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = reconstruct(
        args.candidate_dir, args.receipt, args.report, args.cpi_data, args.output_dir
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in [
                    "status",
                    "estimate_g_person_day",
                    "numerical_target_criterion_passed",
                    "source_defined_method",
                ]
            }
        )
    )
    raise SystemExit(
        0
        if result["source_defined_method"]
        and result["numerical_target_criterion_passed"]
        else 2
    )
