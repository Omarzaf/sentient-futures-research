"""Diagnose the PBS chicken baseline from fixed public microdata, failing closed."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

__all__ = ["aggregate_diagnostic", "main", "reproduce_pakistan", "verify_raw"]

RAW_FILES = {
    "pbs-stata-2024-25.zip": "cf1286dc00cfc325df7a51fab64b8baecc4f6b62e015742e229bf299760898cc",
    "pbs-hies-report.pdf": "02d2f4f3feeecd25e2aee15bf6f90fde5997904548764fc12679a78729409885",
    "pbs-table23.xls": "c11710ba93b596dca5fa2ff2d6a74da227ee57051700c1120a719421e71a7287",
    "pbs-female-questionnaire.pdf": "084e602cb645d43aae5ebbf18a896ee46eb8e2c4df2ff71550fc3cceb7b0e9f3",
    "pbs-manual.pdf": "188081a3fccf744e5f496b525b6a094916a61bb1ef7ebabc230ecc2f5cada91c",
    "pbs-coding-scheme.xlsx": "36e2793a0020c31a841df574c99d656a1f1aeed51a1f9f6a3b206c1f43bd2beb",
}
QUANTITY = ["q1", "q2", "q3", "q4"]
VALUE = ["v1", "v2", "v3", "v4"]
TARGETS = {"all": 0.34, "rural": 0.29, "urban": 0.41}


def verify_raw(raw_dir: Path) -> dict[str, str]:
    """Require exact source versions before parsing any respondent data."""
    verified = {}
    for name, expected in RAW_FILES.items():
        path = raw_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing required PBS source: {name}")
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"PBS source identity mismatch: {name}")
        verified[name] = actual
    return verified


def _unique(frame: pd.DataFrame, columns: list[str], source: str) -> None:
    """Reject missing or duplicate join keys without disclosing their values."""
    if frame[columns].isna().any().any() or frame.duplicated(columns).any():
        raise ValueError(f"Missing or duplicate join keys in {source}")


def aggregate_diagnostic(
    info: pd.DataFrame,
    roster: pd.DataFrame,
    weights: pd.DataFrame,
    food: pd.DataFrame,
) -> dict:
    """Compute aggregate known-quantity diagnostics without selecting a fitted match."""
    _unique(info, ["hhcode"], "section_info")
    _unique(roster, ["hhcode", "idc"], "plist_roster")
    _unique(weights, ["prcode"], "weight")
    chicken = food.loc[food["itc"].eq(11203)].copy()
    _unique(chicken, ["hhcode"], "chicken item11203")
    if set(info["hhcode"]) != set(roster["hhcode"]):
        raise ValueError("Household information and roster key sets differ")
    if not set(chicken["hhcode"]).issubset(set(info["hhcode"])):
        raise ValueError("A chicken record lacks household information")
    if roster["s1aq10"].isna().any() or not roster["s1aq10"].isin([1, 2]).all():
        raise ValueError("Unresolved household-membership code")
    if not info["region"].isin([1, 2]).all():
        raise ValueError("Unresolved rural/urban code")
    if chicken[QUANTITY].lt(0).any().any():
        raise ValueError("Negative reported chicken quantity")
    members = (
        roster.assign(member_yes=roster["s1aq10"].eq(1).astype(int))
        .groupby("hhcode", as_index=False)
        .agg(member_yes=("member_yes", "sum"), all_roster=("idc", "size"))
    )
    households = info.merge(members, on="hhcode", validate="one_to_one").merge(
        weights, on="prcode", how="left", validate="many_to_one"
    )
    if (
        households["weight"].isna().any()
        or not households["weight"].gt(0).all()
        or not households["member_yes"].gt(0).all()
    ):
        raise ValueError("Missing/nonpositive weight or no confirmed household members")
    chicken["known_quantity"] = chicken[QUANTITY].sum(axis=1, min_count=1)
    quality = {
        "chicken_records": len(chicken),
        "all_quantity_channels_missing_records": int(
            chicken[QUANTITY].isna().all(axis=1).sum()
        ),
        "positive_value_but_no_quantity_records": int(
            (
                chicken[QUANTITY].isna().all(axis=1)
                & chicken[VALUE].sum(axis=1, min_count=1).gt(0)
            ).sum()
        ),
        "raw_unit_field_missing_records": int(chicken["unit"].isna().sum()),
        "absent_chicken_item_households": len(households) - len(chicken),
    }
    joined = households.merge(
        chicken[["hhcode", "known_quantity", *QUANTITY]],
        on="hhcode",
        how="left",
        validate="one_to_one",
    )
    results = []
    for residence, region in (("all", None), ("rural", 1), ("urban", 2)):
        subset = joined if region is None else joined.loc[joined["region"].eq(region)]
        for denominator in ("member_yes", "all_roster"):
            people = float((subset["weight"] * subset[denominator]).sum())
            known = float((subset["weight"] * subset["known_quantity"]).sum())
            for convention, multiplier in (
                ("annual26_div12", 26 / 12),
                ("days30_div14", 30 / 14),
            ):
                amount = known * multiplier / people
                results.append(
                    {
                        "residence": residence,
                        "denominator": denominator,
                        "period_convention": convention,
                        "diagnostic_kg_person_month": amount,
                        "published_report_target": TARGETS[residence],
                        "within_report_rounding": abs(amount - TARGETS[residence])
                        < 0.005,
                        "households": len(subset),
                        "psus": int(subset["prcode"].nunique()),
                    }
                )
    paid_only = (
        float((joined["weight"] * joined["q1"]).sum())
        * 30
        / 14
        / float((joined["weight"] * joined["member_yes"]).sum())
    )
    return {
        "status": "HOLD",
        "new_estimation_allowed": False,
        "baseline_reproduced": False,
        "diagnostic_only": True,
        "survey_design_verified": False,
        "standard_errors": None,
        "cause": [
            "All-channel observed-quantity diagnostics do not establish reproduction of the report target.",
            "Released fields contain PSU key prcode and weight, but no verified sampling-stratum construction.",
            "Absent item records and missing channels are not certified nonconsumption; no quantity is imputed.",
            "Territorial alignment of the four-province release with the report's stated sampling universe remains unverified.",
        ],
        "quality": quality,
        "province_codes_present": sorted(
            int(value) for value in info["province"].unique()
        ),
        "diagnostics": results,
        "excluded_paid_only_match": {
            "diagnostic_kg_person_month": paid_only,
            "within_national_report_rounding": abs(paid_only - TARGETS["all"]) < 0.005,
            "accepted": False,
            "reason": "Dropping unpaid/in-kind channels changes the report Section2.4.2 consumption definition; numerical agreement alone cannot select it.",
        },
    }


def reproduce_pakistan(raw_dir: Path, output_path: Path) -> dict:
    """Save an aggregate, source-bound reproduction diagnostic with a held gate."""
    hashes = verify_raw(raw_dir)
    if output_path.resolve() in {(raw_dir / name).resolve() for name in RAW_FILES}:
        raise ValueError("Diagnostic cannot overwrite a raw source")
    tables = {}
    schema = {}
    columns = {
        "section_info": ["hhcode", "prcode", "province", "region"],
        "plist_roster": ["hhcode", "idc", "s1aq10"],
        "weight": ["prcode", "weight"],
        "sec_6a_consum_exp": ["hhcode", "itc", "unit", *QUANTITY, *VALUE],
    }
    with ZipFile(raw_dir / "pbs-stata-2024-25.zip") as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupted PBS ZIP member")
        for name, selected in columns.items():
            with pd.read_stata(
                io.BytesIO(archive.read(f"Stata data/{name}.dta")),
                iterator=True,
                convert_categoricals=False,
                columns=selected,
            ) as reader:
                schema[name] = reader.variable_labels()
                tables[name] = reader.read()
    result = aggregate_diagnostic(*(tables[name] for name in columns))
    workbook = pd.read_excel(raw_dir / "pbs-table23.xls", header=None, engine="xlrd")
    result.update(
        producer={
            "code_path": "research/protein-markets-2026/reproduce_pakistan.py",
            "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        source_sha256=hashes,
        source_schema=schema,
        source_locators={
            "chicken": "Female questionnaire printedp19, item11203,kg,last14days,quantity columns1/3/5/7",
            "period": "Manual printedp91:14day recall and30day month; printedp143:annualize PartA by26",
            "membership": "Roster s1aq10=yes; report Section2.1 usual household membership",
            "target": "Report Table3.7.C printedp25/PDF42",
            "design": "Report Section1.5 printedp3/PDF20; exact released stratum mapping unresolved",
            "unit": "Questionnaire establisheskg; release unit field is entirely missing for chicken",
        },
        official_workbook_chicken={
            "national": float(workbook.iloc[31, 2]),
            "urban": float(workbook.iloc[74, 2]),
            "rural": float(workbook.iloc[116, 2]),
            "locators": "Sheet1!C32,C75,C117; source values retained, not averaged with report",
            "agrees_with_report_at_2dp": False,
        },
        licence="Publicly accessible; redistribution licence not established. Local research only.",
        household_or_person_rows_exported=0,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    """Run only the official-baseline diagnostic, never a market forecast."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = reproduce_pakistan(args.raw_dir, args.output)
    print(json.dumps({"status": result["status"], "baseline_reproduced": False}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
