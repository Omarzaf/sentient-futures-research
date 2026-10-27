"""Estimate the frozen PBS chicken comparator and evaluate its actual discrepancy."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import subprocess
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

__all__ = [
    "build_households",
    "estimate_variant",
    "main",
    "parse_chicken_targets",
    "parse_food_targets",
    "primary_assessment",
    "rounding_pass",
    "run",
]

QUANTITIES = ["q1", "q2", "q3", "q4"]
VALUES = ["v1", "v2", "v3", "v4"]
RAW_SHA = "cf1286dc00cfc325df7a51fab64b8baecc4f6b62e015742e229bf299760898cc"
SPSS_SHA = "90d25be614280f841e3d5d03cdff3b169ceb1c54cbac906ce3bc83b34a617545"
INPUT_SHA = {
    "pbs-stata-2024-25.zip": RAW_SHA,
    "pbs-hies-report.pdf": "02d2f4f3feeecd25e2aee15bf6f90fde5997904548764fc12679a78729409885",
    "pbs-table23.xls": "c11710ba93b596dca5fa2ff2d6a74da227ee57051700c1120a719421e71a7287",
    "pbs-female-questionnaire.pdf": "084e602cb645d43aae5ebbf18a896ee46eb8e2c4df2ff71550fc3cceb7b0e9f3",
    "pbs-manual.pdf": "188081a3fccf744e5f496b525b6a094916a61bb1ef7ebabc230ecc2f5cada91c",
    "pbs-coding-scheme.xlsx": "36e2793a0020c31a841df574c99d656a1f1aeed51a1f9f6a3b206c1f43bd2beb",
}
FOOD_CHECKS = {
    "Wheat and Wheat Flour": ([11101, 11102], 30),
    "Rice and Rice Flour": ([11103], 30),
    "Pulses": (list(range(11109, 11116)), 30),
    "Milk fresh & boiled": ([11401], 14),
    "Cooking Oil": ([11504], 30),
    "Mutton": ([11202], 14),
    "Beef": ([11201], 14),
    "Chicken Meat": ([11203], 14),
    "Eggs": ([11409], 14),
    "Potato": ([11701], 14),
    "Tomato": ([11703], 14),
    "Onion": ([11702], 14),
}


def sha(path: Path) -> str:
    """Hash a local source without changing its bytes."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unique(frame: pd.DataFrame, columns: list[str], source: str) -> None:
    """Reject ambiguous joins without printing respondent identifiers."""
    if frame[columns].isna().any().any() or frame.duplicated(columns).any():
        raise ValueError(f"Missing or duplicate keys in {source}")


def rounding_pass(estimate: float, target: float) -> bool:
    """Evaluate the half-open two-decimal rounding interval without target fitting."""
    if not math.isfinite(estimate):
        return False
    value, centre = Decimal(str(estimate)), Decimal(str(target))
    return centre - Decimal("0.005") <= value < centre + Decimal("0.005")


def parse_chicken_targets(report_text: str) -> dict[str, float]:
    """Extract2024-25 references after the three2018-19 columns in Table3.7.C."""
    table = report_text[report_text.index("TABLE 3.7.C") :]
    row = re.search(r"Chicken Meat\s+Kg\s+((?:[\d.]+\s+){5}[\d.]+)", table)
    if row is None:
        raise ValueError("Chicken quantity reference row missing")
    values = [float(value) for value in row.group(1).split()]
    return dict(zip(("urban", "rural", "all"), values[3:], strict=True))


def parse_food_targets(report_text: str, label: str) -> dict[str, float]:
    """Handle the report's wrapped wheat label without shifting any numeric column."""
    flat = " ".join(report_text[report_text.index("TABLE 3.7.C") :].split())
    number_row = r"((?:[\d.]+\s+){5}[\d.]+)"
    pattern = r"\s+".join(re.escape(word) for word in label.split())
    row = re.search(pattern + r"\s+(?:Kg|Ltr|No|Gm)\s+" + number_row, flat)
    if row is None and label == "Wheat and Wheat Flour":
        row = re.search(r"Wheat and Wheat\s+" + number_row + r"\s+Flour\s+Kg", flat)
    if row is None:
        raise ValueError(f"Published cross-check row absent: {label}")
    return dict(
        zip(
            ("urban", "rural", "all"), map(float, row.group(1).split()[3:]), strict=True
        )
    )


def build_households(
    info: pd.DataFrame,
    roster: pd.DataFrame,
    weights: pd.DataFrame,
    food: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """Build one checked household row, retaining all released denominator members."""
    unique(info, ["hhcode"], "section_info")
    unique(roster, ["hhcode", "idc"], "roster")
    unique(weights, ["prcode"], "weight")
    if set(info["hhcode"]) != set(roster["hhcode"]):
        raise ValueError("Household/roster universe mismatch")
    if not roster["s1aq10"].isin([1, 2]).all():
        raise ValueError("Unknown household membership")
    if not info["region"].isin([1, 2]).all():
        raise ValueError("Unknown residence")
    people = (
        roster.assign(is_member=roster["s1aq10"].eq(1).astype(int))
        .groupby("hhcode", as_index=False)
        .agg(
            members=("is_member", "sum"),
            all_roster=("idc", "size"),
            roster_weight=("weight", "first"),
            roster_weight_count=("weight", "nunique"),
        )
    )
    hh = info.merge(people, on="hhcode", validate="one_to_one").merge(
        weights, on="prcode", how="left", validate="many_to_one"
    )
    if (
        not hh["weight"].gt(0).all()
        or hh["weight"].isna().any()
        or hh["weight"].isin([math.inf, -math.inf]).any()
        or not hh["members"].gt(0).all()
        or not hh["roster_weight_count"].eq(1).all()
        or hh["roster_weight"].isna().any()
        or (hh["roster_weight"] - hh["weight"]).abs().gt(1e-8).any()
    ):
        raise ValueError("Missing, conflicting or invalid weight/member denominator")
    chicken = food.loc[food["itc"].eq(11203)].copy()
    unique(chicken, ["hhcode"], "chicken")
    if not set(chicken["hhcode"]).issubset(set(hh["hhcode"])):
        raise ValueError("Unmatched chicken household")
    if chicken[QUANTITIES].lt(0).any().any():
        raise ValueError("Negative chicken quantity")
    if chicken[QUANTITIES].isin([math.inf, -math.inf]).any().any():
        raise ValueError("Nonfinite chicken quantity")
    chicken["quantity"] = chicken[QUANTITIES].sum(axis=1, min_count=1)
    missing = chicken[QUANTITIES].isna().all(axis=1)
    quality = {
        "households": len(hh),
        "psus": int(hh["prcode"].nunique()),
        "roster_person_rows": len(roster),
        "member_yes_person_rows": int(roster["s1aq10"].eq(1).sum()),
        "nonmember_person_rows": int(roster["s1aq10"].eq(2).sum()),
        "roster_psu_weight_disagreements": 0,
        "chicken_records": len(chicken),
        "absent_chicken_item_households": len(hh) - len(chicken),
        "all_quantity_channels_missing_records": int(missing.sum()),
        "positive_value_no_quantity_records": int(
            (missing & chicken[VALUES].sum(axis=1, min_count=1).gt(0)).sum()
        ),
        "quantity_channel_observed_counts": {
            key: int(chicken[key].notna().sum()) for key in QUANTITIES
        },
        "missingness_scope": "Observed reported quantities only. All sample denominators retained. An absent sparse item record is not independently certified true nonconsumption; no unknown amount is imputed.",
    }
    hh = hh.merge(
        chicken[["hhcode", "quantity", *QUANTITIES]],
        on="hhcode",
        how="left",
        validate="one_to_one",
    )
    return hh, quality


def estimate_variant(
    households: pd.DataFrame,
    *,
    residence: str = "all",
    denominator: str = "members",
    factor: float = 30 / 14,
    channels: str = "all",
    geography: str = "all",
    formula: str = "person_ratio",
) -> dict:
    """Compute an explicitly named point estimand rather than select a best fit."""
    if denominator not in {"members", "all_roster"}:
        raise ValueError("Unknown denominator")
    if channels not in {"all", "paid_only"} or formula not in {
        "person_ratio",
        "household_mean",
    }:
        raise ValueError("Unknown channels or formula")
    if residence not in {"all", "rural", "urban"}:
        raise ValueError("Unknown residence")
    hh = households.copy()
    if residence != "all":
        hh = hh.loc[hh["region"].eq({"rural": 1, "urban": 2}[residence])]
    if geography == "four_provinces":
        hh = hh.loc[hh["source_geography"].ne("ISLAMABAD CAPITAL TERRITORY")]
    elif geography != "all":
        raise ValueError("Unknown geography")
    if hh.empty:
        raise ValueError("Empty domain")
    quantity = hh["quantity"] if channels == "all" else hh["q1"]
    weighted_kg = float((hh["weight"] * quantity).sum())
    weighted_people = float((hh["weight"] * hh[denominator]).sum())
    if weighted_people <= 0 or not math.isfinite(weighted_kg):
        raise ValueError("Invalid weighted numerator/denominator")
    estimate = weighted_kg * factor / weighted_people
    if formula == "household_mean":
        estimate = float((hh["weight"] * quantity.fillna(0) / hh[denominator]).sum())
        estimate *= factor / float(hh["weight"].sum())
    eligible = (
        denominator == "members"
        and factor == 30 / 14
        and channels == "all"
        and geography == "all"
        and formula == "person_ratio"
    )
    return {
        "residence": residence,
        "estimate_kg_person_month": estimate,
        "weighted_recall_kg_numerator": weighted_kg,
        "weighted_person_denominator": weighted_people,
        "monthly_factor": factor,
        "denominator": denominator,
        "channels": channels,
        "geography": geography,
        "formula": formula,
        "households": len(hh),
        "psus": int(hh["prcode"].nunique()),
        "all_channels_included": channels == "all",
        "source_defined_method": eligible,
        "target_fitting_used": False,
    }


def primary_assessment(cell: dict, quality: dict, target: float = 0.34) -> dict:
    """Separate numerical rounding from source method and complete observed reporting."""
    comparable = (
        cell["source_defined_method"]
        and cell["all_channels_included"]
        and quality["all_quantity_channels_missing_records"] == 0
    )
    numerical = rounding_pass(cell["estimate_kg_person_month"], target)
    passed = comparable and numerical and not cell["target_fitting_used"]
    return {
        **cell,
        "published_target_kg_person_month": target,
        "rounding_interval": {
            "lower_inclusive": float(Decimal(str(target)) - Decimal("0.005")),
            "upper_exclusive": float(Decimal(str(target)) + Decimal("0.005")),
        },
        "numerical_criterion_met": numerical,
        "complete_source_defined_comparator": comparable,
        "comparator_scope": "Complete declared observed-quantity point formula for all released households; does not certify sparse-record nonresponse, wider territorial equivalence or variance design.",
        "point_target_reproduced": passed,
        "method_status": (
            "source_defined_point_comparator_variance_separate"
            if cell["source_defined_method"]
            else "excluded_falsification_or_scope_variant"
        ),
        "status": (
            "POINT_TARGET_REPRODUCED"
            if passed
            else "TARGET_MISMATCH" if comparable else "COMPARATOR_NOT_ELIGIBLE"
        ),
        "cause": (
            "This predeclared sensitivity/falsification is not the source-defined primary, or quantities are incomplete; numerical agreement cannot promote it."
            if not comparable
            else (
                "The fixed all-source comparator falls outside the printed target's rounding interval. No diagnostic variant is selected to force agreement."
                if not numerical
                else "Numerical agreement is separated from source/method qualifications."
            )
        ),
        "design_variance_status": "not_certified: administrative keys exist; final ultimate strata/substrata, ICT plan applicability and two singleton administrative groups remain unresolved",
        "standard_error": None,
    }


def extract_text(pdf: Path) -> str:
    """Read cached official PDF text with the installed layout-preserving extractor."""
    return subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def load_stata(archive_path: Path) -> tuple[dict[str, pd.DataFrame], dict]:
    """Read selected columns and retain respondent records in memory only."""
    columns = {
        "section_info": [
            "hhcode",
            "prcode",
            "province",
            "region",
            "enum_year",
            "enum_month",
        ],
        "plist_roster": ["hhcode", "idc", "s1aq10", "weight"],
        "weight": ["prcode", "weight"],
        "sec_6a_consum_exp": ["hhcode", "itc", *QUANTITIES, *VALUES],
    }
    frames, metadata = {}, {}
    with ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid source archive CRC")
        for name, selected in columns.items():
            member = f"Stata data/{name}.dta"
            data = archive.read(member)
            with pd.read_stata(
                io.BytesIO(data),
                iterator=True,
                convert_categoricals=False,
                columns=selected,
            ) as reader:
                metadata[name] = {
                    "member": member,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "variable_labels": reader.variable_labels(),
                }
                frames[name] = reader.read()
    return frames, metadata


def ancillary_cells(
    households: pd.DataFrame, food: pd.DataFrame, report_text: str
) -> list[dict]:
    """Falsify broad processing mistakes using twelve explicit published food groups."""
    results = []
    for label, (codes, days) in FOOD_CHECKS.items():
        targets = parse_food_targets(report_text, label)
        selected = food.loc[food["itc"].isin(codes)].copy()
        unique(selected, ["hhcode", "itc"], "cross-check food")
        if selected[QUANTITIES].lt(0).any().any():
            raise ValueError("Negative ancillary quantity")
        totals = (
            selected.assign(quantity=selected[QUANTITIES].sum(axis=1, min_count=1))
            .groupby("hhcode", as_index=False)["quantity"]
            .sum(min_count=1)
        )
        base = households.drop(columns=["quantity", *QUANTITIES]).merge(
            totals, on="hhcode", how="left", validate="one_to_one"
        )
        for residence in ("all", "rural", "urban"):
            cell = estimate_variant(base, residence=residence, factor=30 / days)
            results.append(
                {
                    "food": label,
                    "codes": codes,
                    "recall_days": days,
                    "residence": residence,
                    "estimate": cell["estimate_kg_person_month"],
                    "target": targets[residence],
                    "rounding_match": rounding_pass(
                        cell["estimate_kg_person_month"], targets[residence]
                    ),
                    "mapping_scope": "Explicit named questionnaire group; Pulses combines11109–11115 as an analyst grouping and does not govern chicken acceptance",
                }
            )
    return results


def run(
    raw_dir: Path,
    crosswalk: Path,
    spec_path: Path,
    output_dir: Path,
    spss_archive: Path | None = None,
    second_report: Path | None = None,
) -> dict:
    """Run the declared estimator, genuine comparator and optional independent-format check."""
    source_hashes = {}
    for name, expected in INPUT_SHA.items():
        actual = sha(raw_dir / name)
        if actual != expected:
            raise ValueError(f"Source identity mismatch: {name}")
        source_hashes[name] = actual
    spec = json.loads(spec_path.read_text())
    if spec["primary"]["id"] != "P0_all_source_member_yes_30d":
        raise ValueError("A different primary requires a new reviewed estimator")
    output_dir.mkdir(parents=True, exist_ok=True)
    frames, metadata = load_stata(raw_dir / "pbs-stata-2024-25.zip")
    hh, quality = build_households(*(frames[key] for key in frames))
    geography = pd.read_csv(crosswalk)
    unique(geography, ["prcode"], "source geography")
    hh = hh.merge(
        geography[["prcode", "province"]].rename(
            columns={"province": "source_geography"}
        ),
        on="prcode",
        how="left",
        validate="many_to_one",
    )
    if hh["source_geography"].isna().any():
        raise ValueError("Unmapped source geography")
    report_text = extract_text(raw_dir / "pbs-hies-report.pdf")
    targets = parse_chicken_targets(report_text)
    if targets != {"all": 0.34, "rural": 0.29, "urban": 0.41}:
        raise ValueError("Unexpected published target revision")
    variants = []
    changes = (
        ("P0_all_source_member_yes_30d", {}),
        ("S1_annual26_12", {"factor": 26 / 12}),
        ("S2_all_roster", {"denominator": "all_roster"}),
        ("S3_four_geographic_provinces", {"geography": "four_provinces"}),
        ("F1_paid_only", {"channels": "paid_only"}),
        ("F2_household_mean_percapita", {"formula": "household_mean"}),
    )
    for name, options in changes:
        for residence in ("all", "rural", "urban"):
            cell = estimate_variant(hh, residence=residence, **options)
            variants.append(
                {
                    "variant": name,
                    **primary_assessment(cell, quality, targets[residence]),
                }
            )
    primary = next(
        cell
        for cell in variants
        if cell["variant"] == "P0_all_source_member_yes_30d"
        and cell["residence"] == "all"
    )
    workbook = pd.read_excel(raw_dir / "pbs-table23.xls", header=None, engine="xlrd")
    published = {
        "all": float(workbook.iloc[31, 2]),
        "urban": float(workbook.iloc[74, 2]),
        "rural": float(workbook.iloc[116, 2]),
    }
    second = None
    if second_report is not None:
        duplicate = sha(second_report) == source_hashes["pbs-hies-report.pdf"]
        second = {
            "sha256": sha(second_report),
            "chicken_targets": parse_chicken_targets(extract_text(second_report)),
            "identical_to_primary_report": duplicate,
            "scope": (
                "Byte-identical duplicate report capture; adds no independent corroboration"
                if duplicate
                else "Distinct official report bytes from the same publisher; a publication cross-check, not independent respondent analysis"
            ),
        }
    spss = {"status": "not_requested"}
    if spss_archive is not None:
        if sha(spss_archive) != SPSS_SHA:
            raise ValueError("SPSS source identity mismatch")
        destination = output_dir / "spss-crosscheck.csv"
        helper = Path(__file__).with_name("pakistan_spss_crosscheck.R")
        process = subprocess.run(
            ["Rscript", "--vanilla", str(helper), str(spss_archive), str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )
        (output_dir / "spss-reader.log").write_text(process.stdout + process.stderr)
        comparison = pd.read_csv(destination)
        checks = []
        for residence in ("all", "rural", "urban"):
            saved = next(
                cell
                for cell in variants
                if cell["variant"] == "P0_all_source_member_yes_30d"
                and cell["residence"] == residence
            )
            actual = comparison.loc[comparison["residence"].eq(residence)].iloc[0]
            checks.append(
                {
                    "residence": residence,
                    "spss_estimate": float(actual["estimate_kg_person_month"]),
                    "stata_estimate": saved["estimate_kg_person_month"],
                    "difference": float(actual["estimate_kg_person_month"])
                    - saved["estimate_kg_person_month"],
                    "households_equal": int(actual["households"])
                    == saved["households"],
                    "psus_equal": int(actual["psus"]) == saved["psus"],
                }
            )
        spss = {
            "status": "computed_independent_R_foreign_reader",
            "archive_sha256": SPSS_SHA,
            "helper_sha256": sha(helper),
            "checks": checks,
            "all_agree_within_1e_12": all(
                abs(row["difference"]) < 1e-12
                and row["households_equal"]
                and row["psus_equal"]
                for row in checks
            ),
            "all_same_two_decimal_display": all(
                round(row["spss_estimate"], 2) == round(row["stata_estimate"], 2)
                for row in checks
            ),
            "max_absolute_format_difference": max(
                abs(row["difference"]) for row in checks
            ),
            "precision_note": "SPSS and Stata store numeric fields with different binary precision. Raw differences are retained; same published display is not exact binary equality or target reproduction.",
        }
    result = {
        **primary,
        "schema_version": 1,
        "estimator_implemented": True,
        "scope": "Official chicken point comparator; no full dietary protein or downstream market estimate",
        "quality": quality,
        "fieldwork_months": (
            frames["section_info"]
            .groupby(["enum_year", "enum_month"], as_index=False)
            .size()
            .rename(columns={"size": "households"})
            .to_dict(orient="records")
        ),
        "territory_check": {
            "released_households": len(hh),
            "released_psus": int(hh["prcode"].nunique()),
            "source_geographic_ICT_households": int(
                hh["source_geography"].eq("ISLAMABAD CAPITAL TERRITORY").sum()
            ),
            "source_geographic_ICT_psus": int(
                hh.loc[
                    hh["source_geography"].eq("ISLAMABAD CAPITAL TERRITORY"), "prcode"
                ].nunique()
            ),
            "scope": "National comparator keeps ICT and every released household; the four-province exclusion remains a separately named domain sensitivity",
        },
        "variants": variants,
        "published_workbook_chicken": published,
        "second_published_report": second,
        "independent_spss_reader": spss,
        "other_food_crosschecks": ancillary_cells(
            hh, frames["sec_6a_consum_exp"], report_text
        ),
        "source_sha256": source_hashes,
        "source_members": metadata,
        "spec_sha256": sha(spec_path),
        "crosswalk_sha256": sha(crosswalk),
        "producer_sha256": sha(Path(__file__)),
        "runtime": {"pandas": pd.__version__},
        "source_boundary": "Released sample kept intact, no trimming, rescaling, channel deletion, quantity imputation or target-selected variant. Mainreport30123HH matches release; its alternative planned PSU/HH totals are documented source inconsistencies, not assumed missing data.",
        "household_or_person_rows_exported": 0,
    }
    (output_dir / "reconciliation.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    pd.DataFrame(variants).drop(columns=["rounding_interval"]).to_csv(
        output_dir / "variants.csv", index=False
    )
    return result


def main() -> int:
    """Return success only when the declared point comparator actually reproduces its target."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--spss-archive", type=Path)
    parser.add_argument("--second-report", type=Path)
    args = parser.parse_args()
    result = run(
        args.raw_dir,
        args.crosswalk,
        args.spec,
        args.output_dir,
        args.spss_archive,
        args.second_report,
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "estimate_kg_person_month",
                    "point_target_reproduced",
                    "complete_source_defined_comparator",
                    "independent_spss_reader",
                )
            },
            allow_nan=False,
        )
    )
    return 0 if result["point_target_reproduced"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
