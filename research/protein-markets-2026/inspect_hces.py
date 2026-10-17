"""Inspect a third-party HCES candidate and reconstruct only known physical foods."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

__all__ = [
    "inspect_hces",
    "main",
    "parse_factors",
    "parse_target_definition",
    "physical_components",
    "verify_candidate",
]

REPORT_SHA256 = "f08155b2b9811d236b1a75ccdb48fc60f96efe32bdbabad1413cf7b65017b50b"
THIRTY_DAY_CODES = {
    1,
    2,
    61,
    62,
    70,
    71,
    72,
    73,
    74,
    101,
    102,
    103,
    105,
    106,
    107,
    108,
    110,
    111,
    112,
    114,
    122,
    139,
    140,
    141,
    142,
    143,
    144,
    145,
    146,
    148,
    150,
    152,
    158,
    170,
    171,
    172,
    173,
    174,
    175,
    178,
}
DESIGN = [
    "sector",
    "state",
    "stratum",
    "sub_stratum",
    "fsu_serial_no",
    "panel",
    "subsample",
]


def _sha(path: Path) -> str:
    """Hash one source without exporting its contents."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_candidate(candidate_dir: Path, receipt_path: Path) -> dict:
    """Verify candidate bytes while preserving the unverified official-raw boundary."""
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("source_type") != "third_party_cleaned_survey_candidate":
        raise ValueError("An explicit third-party candidate receipt is required")
    if len(receipt.get("files", [])) != 15:
        raise ValueError("Candidate receipt must contain all fifteen levels")
    seen = set()
    for record in receipt["files"]:
        relative = record["path"]
        if not re.fullmatch(r"04_clean/level_(?:0[1-9]|1[0-5])\.parquet", relative):
            raise ValueError("Unexpected candidate path")
        path = (candidate_dir / relative).resolve()
        if relative in seen or not path.is_relative_to(candidate_dir.resolve()):
            raise ValueError("Duplicate or escaping candidate path")
        seen.add(relative)
        if _sha(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError(f"Candidate identity mismatch: {relative}")
    return receipt


def parse_factors(report_text: str) -> pd.DataFrame:
    """Extract all 176 source-table rows without filling or tuning coefficients."""
    start = report_text.index("Table 2.2: Nutrient contents of food items")
    end = report_text.index("2.11 EFFICACY OF THE ESTIMATES", start)
    table = report_text[start:end]
    positions = list(re.finditer(r"^\s*(\d+)\.\s+(\d{3})\s+", table, re.MULTILINE))
    records = []
    for index, position in enumerate(positions):
        block = table[
            position.end() : (
                positions[index + 1].start()
                if index + 1 < len(positions)
                else len(table)
            )
        ]
        values = re.search(
            r"(kg\.|gm\.|litre|no\.|Re\.)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",
            block,
        )
        if values is None:
            raise ValueError("Unparsed nutrient-table row; inspect original PDF")
        records.append(
            {
                "serial": int(position.group(1)),
                "item_code": int(position.group(2)),
                "unit": values.group(1),
                "protein_g_per_unit": float(values.group(3)),
                "sector": (
                    "rural"
                    if "(rural)" in block
                    else "urban" if "(urban)" in block else "all"
                ),
            }
        )
    if [row["serial"] for row in records] != list(range(1, 177)):
        raise ValueError("Nutrient-table source rows are incomplete or shifted")
    frame = pd.DataFrame.from_records(records)
    if frame.duplicated(["item_code", "sector"]).any():
        raise ValueError("Ambiguous coefficient key")
    return frame


def parse_target_definition(report_text: str) -> dict:
    """Keep the published unadjusted target separate from meal-adjusted intake."""
    rural_start = report_text.index("Table 3.18R:")
    urban_start = report_text.index("Table 3.18U:", rural_start)
    end = report_text.index("3.4.5", urban_start)
    unadjusted = {}
    adjusted = {}
    for sector, block in (
        ("rural", report_text[rural_start:urban_start]),
        ("urban", report_text[urban_start:end]),
    ):
        row = re.search(
            r"^\s*All classes\s+([\d.]+(?:\s+[\d.]+){11})", block, re.MULTILINE
        )
        if row is None:
            raise ValueError("Missing adjusted/unadjusted source comparison row")
        values = [float(value) for value in row.group(1).split()]
        unadjusted[sector] = values[1]
        adjusted[sector] = values[4]
    if unadjusted != {"rural": 61.8, "urban": 63.4}:
        raise ValueError("Published unadjusted columns do not match the brief targets")
    return {
        "baseline_estimand": "unadjusted household-consumption-derived protein",
        "unit": "g/person/day",
        "year": "2023-24",
        "unadjusted_target": unadjusted,
        "published_meal_adjusted_reference_not_target": adjusted,
        "meal_adjustment_required_for_this_target": False,
        "locator": "Report594 Table3.18R/U printed51/PDF70, All classes; corroborates Table3.8",
    }


def physical_components(
    food: pd.DataFrame,
    factors: pd.DataFrame,
    level: str,
) -> tuple[pd.DataFrame, dict]:
    """Calculate documented physical components while retaining all unresolved rows."""
    if (
        food[["hhid", "item_code"]].isna().any().any()
        or food.duplicated(["hhid", "item_code"]).any()
    ):
        raise ValueError("Missing or duplicate HCES item key")
    if food["cons_total_qty"].lt(0).any():
        raise ValueError("Negative reported food quantity")
    physical = factors.loc[factors["unit"].ne("Re.")]
    if physical["item_code"].duplicated().any():
        raise ValueError("A physical coefficient has unresolved sector variants")
    selected = food.merge(
        physical[["item_code", "unit", "protein_g_per_unit"]],
        on="item_code",
        how="left",
        validate="many_to_one",
    )
    known = selected.loc[selected["protein_g_per_unit"].notna()].copy()
    days = pd.Series(7.0, index=known.index)
    if level == "05":
        days.loc[known["item_code"].isin(THIRTY_DAY_CODES)] = 30.0
    elif level not in {"06", "10"}:
        raise ValueError("No source-established recall rule for this level")
    # Quantity(0.000) denotes decimal places, not an implied integer scale.
    # Candidate Stata destring preserves those decimals: questionnaire kg/litre/
    # gram/count stay distinct through their source coefficients, without /1000.
    known["physical_protein_g_day"] = (
        known["cons_total_qty"] * known["protein_g_per_unit"] / days
    )
    totals = known.groupby("hhid", as_index=False)["physical_protein_g_day"].sum(
        min_count=1
    )
    rupees = set(factors.loc[factors["unit"].eq("Re."), "item_code"])
    physical_codes = set(physical["item_code"])
    actual_codes = set(food["item_code"])
    diagnostic = {
        "level": level,
        "physical_component_records": len(known),
        "physical_records_missing_quantity": int(known["cons_total_qty"].isna().sum()),
        "unresolved_rupee_item_codes": sorted(
            int(code) for code in actual_codes & rupees
        ),
        "codes_without_table_coefficient": sorted(
            int(code) for code in actual_codes - rupees - physical_codes
        ),
        "note": "Unmapped rows include questionnaire totals/drop-down parent or child rows; they are not set to zero or counted as resolved foods.",
    }
    return totals, diagnostic


def inspect_hces(
    candidate_dir: Path, receipt_path: Path, report_pdf: Path, output_path: Path
) -> dict:
    """Write a source-bound inspection with no complete intake or passing baseline."""
    receipt = verify_candidate(candidate_dir, receipt_path)
    if _sha(report_pdf) != REPORT_SHA256:
        raise ValueError("Official nutrition-report identity mismatch")
    extraction = subprocess.run(
        ["pdftotext", "-layout", str(report_pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    factors = parse_factors(extraction.stdout)
    target_definition = parse_target_definition(extraction.stdout)
    root = candidate_dir / "04_clean"
    info = pd.read_parquet(
        root / "level_01.parquet", columns=["hhid", "year", "multiplier", *DESIGN]
    )
    visits = pd.read_parquet(
        root / "level_15.parquet",
        columns=["hhid", "questionnaire_num", "visit", "hh_size", "multiplier"],
    )
    if info["hhid"].duplicated().any() or info[["hhid", *DESIGN]].isna().any().any():
        raise ValueError("Incomplete/duplicate household or design identifiers")
    if visits.duplicated(["hhid", "questionnaire_num"]).any():
        raise ValueError("Duplicate questionnaire per household")
    complete = (
        visits.loc[visits["questionnaire_num"].isin(["F", "C", "D"])]
        .groupby("hhid")["questionnaire_num"]
        .nunique()
    )
    if not complete.eq(3).all() or set(complete.index) != set(info["hhid"]):
        raise ValueError("Three-questionnaire completion not established")
    third = visits.loc[
        visits["visit"].eq(3) & visits["questionnaire_num"].isin(["F", "C", "D"]),
        ["hhid", "multiplier"],
    ]
    fdq = visits.loc[visits["questionnaire_num"].eq("F"), ["hhid", "hh_size"]]
    households = (
        info.drop(columns="multiplier")
        .merge(third, on="hhid", validate="one_to_one")
        .merge(fdq, on="hhid", validate="one_to_one")
    )
    if (
        len(households) != len(info)
        or households[["hh_size", "multiplier"]].isna().any().any()
        or not households[["hh_size", "multiplier"]].gt(0).all().all()
    ):
        raise ValueError("Incomplete FDQ size or third-visit weight")
    households["final_weight"] = households["multiplier"] / 100
    components = []
    coverage = []
    for level in ("05", "06", "10"):
        food = pd.read_parquet(
            root / f"level_{level}.parquet",
            columns=["hhid", "item_code", "cons_total_qty"],
        )
        totals, diagnostic = physical_components(food, factors, level)
        if not set(totals["hhid"]).issubset(set(households["hhid"])):
            raise ValueError("A food household is absent from the design data")
        components.append(totals)
        coverage.append(diagnostic)
    daily = (
        pd.concat(components, ignore_index=True)
        .groupby("hhid", as_index=False)["physical_protein_g_day"]
        .sum(min_count=1)
    )
    work = households.merge(daily, on="hhid", how="left", validate="one_to_one")
    work["weighted_physical_g_day"] = (
        work["physical_protein_g_day"] * work["final_weight"]
    )
    work["weighted_members"] = work["hh_size"] * work["final_weight"]
    # Preserve strata and PSUs in aggregate construction; a point component does
    # not implement the design-based variance required for eventual inference.
    grouped = work.groupby(DESIGN, as_index=False)[
        ["weighted_physical_g_day", "weighted_members"]
    ].sum(min_count=1)
    summary = grouped.groupby("sector", as_index=False)[
        ["weighted_physical_g_day", "weighted_members"]
    ].sum(min_count=1)
    summary["physical_component_g_person_day"] = (
        summary["weighted_physical_g_day"] / summary["weighted_members"]
    )
    result = {
        "status": "HOLD",
        "baseline_reproduced": False,
        "new_estimation_allowed": False,
        "status_origin": "incomplete_component_diagnostic_not_dynamic_acceptance_test",
        "source_type": "third_party_cleaned_survey_candidate",
        "official_raw_identity_verified": False,
        "candidate_commit": receipt["checkout_commit"],
        "candidate_hashes_verified": len(receipt["files"]),
        "candidate_raw_directory_present": (candidate_dir / "03_raw").exists(),
        "candidate_licence": "Not located; do not redistribute respondent records",
        "official_report_sha256": REPORT_SHA256,
        "official_report_url": "https://www.mospi.gov.in/sites/default/files/publication_reports/Nutritional_Intake_in_India_L.pdf",
        "official_targets_g_person_day": {"rural": 61.8, "urban": 63.4},
        "target_definition": target_definition,
        "complete_intake_g_person_day": {"rural": None, "urban": None},
        "partial_components_are_not_target_comparable": True,
        "physical_component_diagnostics": summary[
            ["sector", "physical_component_g_person_day"]
        ].to_dict(orient="records"),
        "rupee_components_g_person_day": {"rural": None, "urban": None},
        "coefficient_rows": len(factors),
        "rupee_coefficient_rows": int(factors["unit"].eq("Re.").sum()),
        "rupee_item_codes": sorted(
            int(code)
            for code in factors.loc[factors["unit"].eq("Re."), "item_code"].unique()
        ),
        "source_factors": factors.to_dict(orient="records"),
        "component_coverage": coverage,
        "household_counts_by_sector": {
            str(key): int(value) for key, value in info.groupby("sector").size().items()
        },
        "three_visits_complete": True,
        "weight_rule": "Readme MLT/100; Methodology3.5/Report5942.1 third-visit multiplier and FDQ household size",
        "quantity_unit_rule": "Candidate quantities are decimal-valued questionnaire units. Layout quantity(0.000) specifies decimal places; Stata destring preserves decimals. No /1000 scaling is applied to Parquet values.",
        "design_fields_used": DESIGN,
        "standard_errors": None,
        "survey_variance_implemented": False,
        "causes": [
            "Fifteen cleaned unit-level files are available and hash-verified; the omitted original official text-file lineage is not authenticated by those hashes.",
            "Report594printedp21 specifies December2024-price rupee factors, the Aug2023-Jul2024 period and separate rural/urban CPI; exact index series/base/normalization remains unresolved. The text does not expressly require an item-by-item CPI crosswalk.",
            "The 36 rural/urban monetary-factor rows exist, but monetary contributions are not implemented by this physical-only diagnostic; whole intake stays null.",
            "Design-based variance and complete MPCE reconstruction are not implemented; preserved design fields are not proof of implemented inference.",
        ],
        "grain_composite_method": "Official Table2.2 supplies coefficients for parents001/002/070; the physical join already uses those parents once and excludes unmapped child rows. Quantity identities were separately audited. Reproducing this published composite does not require inventing variety-specific child factors.",
        "meal_adjustment_scope": "Report2.9.8.1 is a separate adjusted estimand. Candidate level02 contains H-roster meal fields and level04 contains meals_nonhh; input usability requires separate missingness/membership checks. No meal adjustment is required to reproduce the unadjusted brief targets.",
        "primary_lookup": [
            "Official Report594Table2.2 and surrounding methodology inspected; printedp21/PDF40 and target printedp38/PDF57 visually checked.",
            "An official-search-index excerpt for MoSPI https://mospi.gov.in/faq describes CFPI exclusions; the fetched page is an application shell, so the excerpt is not a verified full-page capture. No replacement for the unresolved sector CPI recipe is assumed.",
        ],
        "producer": {
            "code_path": "research/protein-markets-2026/inspect_hces.py",
            "code_sha256": _sha(Path(__file__)),
        },
        "household_or_person_rows_exported": 0,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    """Run candidate inspection and a clearly incomplete baseline diagnostic."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect_hces(args.candidate_dir, args.receipt, args.report, args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "baseline_reproduced": False,
                "complete_intake": None,
            }
        )
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
