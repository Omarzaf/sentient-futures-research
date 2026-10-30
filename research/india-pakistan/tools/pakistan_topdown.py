"""Reproduce a conditional Pakistan value-scale check without altering the proxy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import statistics
import zipfile
from pathlib import Path

__all__ = ["extract", "generate", "main", "normalize_package", "value_check"]
HERE = Path(__file__).resolve().parents[1]
YEARS = (2026, 2030, 2035)
SHARES = (0.0005, 0.001, 0.005)


def digest(path: Path) -> str:
    """Hash a file without changing it or retaining its full content in memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def one(rows: list[dict], label: str) -> dict:
    """Require exact source-selector cardinality instead of silently picking a row."""
    if len(rows) != 1:
        raise ValueError(f"Expected one {label}; found {len(rows)}")
    return rows[0]


def checked_sources(workspace: Path) -> dict[str, Path]:
    """Resolve and verify every original input named in the companion manifest."""
    manifest = json.loads(
        (HERE / "data/pakistan-topdown/input-manifest.json").read_text()
    )
    paths = {}
    for key, record in manifest.items():
        path = workspace / record["path"]
        if digest(path) != record["sha256"]:
            raise ValueError(f"Input hash mismatch: {key}")
        paths[key] = path
    return paths


def csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a source CSV with its original named columns."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def normalize_package(text: str, category: str) -> float:
    """Convert stated package mass or volume, rejecting incompatible dimensions."""
    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*(kg|g|ml|l|liter|litre)\s*", text, re.IGNORECASE
    )
    if match is None:
        raise ValueError(f"Unrecognised package: {text}")
    quantity, unit = float(match[1]), match[2].lower()
    if quantity <= 0:
        raise ValueError("Package quantity must be positive")
    if category == "chicken" and unit in {"g", "kg"}:
        return quantity / 1000 if unit == "g" else quantity
    if category in {"milk", "alternative_milk"} and unit in {
        "ml",
        "l",
        "liter",
        "litre",
    }:
        return quantity / 1000 if unit == "ml" else quantity
    raise ValueError(f"Package dimension does not match {category}: {text}")


def retail_inputs(path: Path) -> list[dict]:
    """Bind every retained Naheed observation to its original captured HTML bytes."""
    retained = []
    for record in (json.loads(line) for line in path.read_text().splitlines()):
        if record.get("country") != "Pakistan" or record.get("category") not in {
            "chicken",
            "milk",
            "alternative_milk",
        }:
            continue
        if (
            record["retailer"] != "Naheed.pk"
            or record["currency"] != "PKR"
            or record["http_status"] != 200
        ):
            raise ValueError("Unexpected retailer/currency/retrieval status")
        raw = path.parent / record["raw_file"]
        if digest(raw) != record["raw_sha256"]:
            raise ValueError(f"Naheed source hash mismatch: {raw}")
        if not record["capture_finished_utc"].startswith("2026-10-16"):
            raise ValueError("Unexpected retail observation date")
        size = normalize_package(record["package_text_in_title"], record["category"])
        retained.append(
            {
                "category": record["category"],
                "title": record["title"],
                "listed_price_pkr_2026": float(record["listed_price"]),
                "package": record["package_text_in_title"],
                "price_per_kg_or_litre_pkr_2026": float(record["listed_price"]) / size,
                "availability": record["availability_as_reported"],
                "url": record["url"],
                "capture_date": record["capture_finished_utc"],
                "raw_file": record["raw_file"],
                "raw_sha256": record["raw_sha256"],
            }
        )
    counts = {
        category: sum(row["category"] == category for row in retained)
        for category in ("chicken", "milk", "alternative_milk")
    }
    if counts != {"chicken": 6, "milk": 9, "alternative_milk": 11}:
        raise ValueError(f"Retained retail counts changed: {counts}")
    return retained


def extract(workspace: Path) -> dict:
    """Extract quantities and prices from original captures and bound transcriptions."""
    paths = checked_sources(workspace)
    with (
        zipfile.ZipFile(paths["faostat_raw"]) as archive,
        archive.open("FoodBalanceSheets_E_All_Data_(Normalized).csv") as stream,
    ):
        fao = [
            row
            for row in csv.DictReader(io.TextIOWrapper(stream, "utf-8-sig"))
            if row["Area Code"] == "165"
            and row["Item Code"] in {"2734", "2948"}
            and row["Element Code"] in {"5142", "645"}
            and row["Year"] == "2023"
        ]
    quantities = {}
    for name, code in (("poultry", "2734"), ("milk", "2948")):
        food = one(
            [
                row
                for row in fao
                if row["Item Code"] == code and row["Element Code"] == "5142"
            ],
            name,
        )
        per_person = one(
            [
                row
                for row in fao
                if row["Item Code"] == code and row["Element Code"] == "645"
            ],
            name,
        )
        if (
            food["Unit"] != "1000 t"
            or per_person["Unit"] != "kg/cap"
            or per_person["Element"] != "Food supply quantity (kg/capita/yr)"
        ):
            raise ValueError("FAO quantity units differ from the approved selectors")
        quantities[name] = {
            "thousand_tonnes": float(food["Value"]),
            "kg_person_year": float(per_person["Value"]),
            "flag": food["Flag"],
        }
    oecd_all = csv_rows(paths["oecd_raw"])
    oecd = {}
    for year in (2023, 2026, 2030, 2034):
        row = one(
            [
                r
                for r in oecd_all
                if r["REF_AREA"] == "PAK"
                and r["COMMODITY"] == "CPC_EX_PT"
                and r["MEASURE"] == "QC"
                and r["TIME_PERIOD"] == str(year)
            ],
            f"OECD poultry {year}",
        )
        if (
            row["UNIT_MEASURE"],
            row["UNIT_MULT"],
            row["CONVENTION"],
            row["VERSION_ID"],
        ) != ("T", "3", "RTOC", "AO_2025_2034"):
            raise ValueError("OECD unit, convention or vintage changed")
        oecd[year] = float(row["OBS_VALUE"])
    fx = one(
        [
            r
            for r in json.loads(paths["wdi_fx_raw"].read_text())[1]
            if r["countryiso3code"] == "PAK" and r["date"] == "2025"
        ],
        "Pakistan FX",
    )
    cpi = json.loads(paths["imf_cpi_raw"].read_text())["values"]["PCPIPCH"]["PAK"][
        "2026"
    ]
    price_page = paths["pbs_text"].read_text().split("\f")[2]
    if "PRICES ON 24-12-2025" not in price_page or "National Average" not in price_page:
        raise ValueError("PBS issue or table header changed")
    prices = {}
    for name, label, unit in (
        ("poultry", "Chicken Farm Broiler (Live)", "1 Kg"),
        ("milk", "Milk fresh (Un-boiled)", "1 Ltr"),
    ):
        lines = [line for line in price_page.splitlines() if label in line]
        if len(lines) != 1 or unit not in lines[0]:
            raise ValueError("PBS price item/unit changed")
        prices[name] = float(re.findall(r"\d+\.\d+", lines[0].split(unit, 1)[1])[10])
    economic_text = paths["economic_text"].read_text()
    table = economic_text.split("Table 2.6: Estimated Milk and Meat Production", 1)[
        1
    ].split("Table 2.7:", 1)[0]
    economic = {}
    for name, label in (
        ("poultry", "Poultry meat"),
        ("milk", "Milk (Human Consumption)3"),
    ):
        lines = [line for line in table.splitlines() if label in line]
        if len(lines) != 1:
            raise ValueError("Economic Survey quantity selector is not unique")
        economic[name] = [
            float(x.replace(",", ""))
            for x in re.findall(r"[\d,]+", lines[0].split(label, 1)[1])
        ]
        if len(economic[name]) != 3:
            raise ValueError("Economic Survey fiscal-year column count changed")
    densities = csv_rows(paths["density_catalog"])
    density_values = {
        name: float(
            one([r for r in densities if r["factor_id"] == factor], factor)["value"]
        )
        for name, factor in (
            ("whole_DK", "density:milk_whole_DK"),
            ("cow_KEN", "density:milk_cow_KEN"),
        )
    }
    references = csv_rows(paths["transfer_reference"])
    if len(references) != 127:
        raise ValueError("Reference-row count changed")
    transfer = {
        year: {
            q: float(
                one(
                    [
                        r
                        for r in references
                        if r["row_id"] == f"pakistan_{year}_market_value_{q}"
                    ],
                    f"reference {year}/{q}",
                )["value"]
            )
            for q in ("p10", "p50", "p90")
        }
        for year in YEARS
    }
    retail = retail_inputs(paths["retail_manifest"])
    return {
        "fao": quantities,
        "oecd_poultry_thousand_tonnes": oecd,
        "economic": economic,
        "fx_pkr_per_usd_2025": fx["value"],
        "cpi_percent_2026": cpi,
        "pbs_price": prices,
        "densities": density_values,
        "transfer": transfer,
        "retail": retail,
        "reference_sha256": digest(paths["transfer_reference"]),
    }


def value_check(
    quantity_thousand_tonnes: float,
    price: float,
    quantity_basis: str,
    price_basis: str,
    fx: float,
    conversion: float | None = None,
) -> float:
    """Convert only explicitly matched or declared sensitivity units into million USD."""
    if min(quantity_thousand_tonnes, price, fx) <= 0:
        raise ValueError("Quantity, price and FX must be positive")
    if quantity_basis == "milk_equivalent_kg" and price_basis == "PKR_per_litre":
        if conversion is None or conversion <= 0:
            raise ValueError("An explicit milk density sensitivity is required")
        price = price / conversion
    elif quantity_basis == "poultry_meat_kg" and price_basis == "PKR_per_kg_live":
        if conversion is None or not 0 < conversion <= 1:
            raise ValueError("An explicit dressed/live yield sensitivity is required")
        price = price / conversion
    elif quantity_basis != "poultry_meat_kg" or price_basis != "PKR_per_kg_cut":
        raise ValueError("Unsupported quantity/price mapping")
    # One thousand tonnes equals one million kg, cancelling million-USD scaling.
    return quantity_thousand_tonnes * price / fx


def flag(value: float, reference: dict) -> str:
    """Report every prescribed order-of-magnitude comparison without tuning values."""
    if value > 10 * reference["p90"]:
        return "above_10x_p90_disclosed_after_user_approval"
    if value < reference["p10"] / 10:
        return "below_0.1x_p10_disclosed_after_user_approval"
    if value > reference["p90"]:
        return "above_p90"
    if value < reference["p10"]:
        return "below_p10"
    return "within_transfer_range_not_validation"


def generate(inputs: dict) -> list[dict]:
    """Generate all requested shares, years, quantity families and price sensitivities."""
    fx = inputs["fx_pkr_per_usd_2025"]
    deflator = 1 + inputs["cpi_percent_2026"] / 100
    retail = {
        category: [
            r["price_per_kg_or_litre_pkr_2026"]
            for r in inputs["retail"]
            if r["category"] == category
        ]
        for category in ("chicken", "milk", "alternative_milk")
    }
    profiles = []
    for label, yield_value, density in (
        ("lower_value", 0.8, inputs["densities"]["cow_KEN"]),
        ("central_sensitivity", 0.7, inputs["densities"]["whole_DK"]),
        ("upper_value", 0.6, inputs["densities"]["whole_DK"]),
    ):
        profiles.append(
            (
                f"official_{label}",
                inputs["pbs_price"]["poultry"],
                inputs["pbs_price"]["milk"],
                "PKR_per_kg_live",
                yield_value,
                density,
                "2025-12-24",
                "none; dated weekly2025 price",
            )
        )
    for label, aggregation in (
        ("minimum", min),
        ("median", statistics.median),
        ("maximum", max),
    ):
        profiles.append(
            (
                f"naheed_{label}",
                aggregation(retail["chicken"]) / deflator,
                aggregation(retail["milk"]) / deflator,
                "PKR_per_kg_cut",
                None,
                inputs["densities"]["whole_DK"],
                "2026-10-16",
                "divide2026 price by1.071; nationalannualCPI sensitivity, not product/date-matched",
            )
        )
    output = []
    for family in (
        "FAO2023_fixed",
        "EconomicSurvey2024_25_fixed",
        "OECD_poultry_FAO_milk",
    ):
        for year in YEARS:
            poultry = inputs["fao"]["poultry"]["thousand_tonnes"]
            milk = inputs["fao"]["milk"]["thousand_tonnes"]
            quantity_note = "FAOSTAT2023 food quantities held fixed; comparison year is not a quantity forecast"
            poultry_year, milk_year = "2023", "2023"
            if family == "EconomicSurvey2024_25_fixed":
                poultry, milk = (
                    inputs["economic"]["poultry"][-1],
                    inputs["economic"]["milk"][-1],
                )
                quantity_note = "2024-25 production poultry/human-consumption-supply milk held fixed; alternative source definitions, not reconciled withFAO"
                poultry_year = milk_year = "2024-25"
            elif family == "OECD_poultry_FAO_milk":
                poultry_year = str(min(year, 2034))
                poultry = inputs["oecd_poultry_thousand_tonnes"][min(year, 2034)]
                quantity_note = "OECDready-to-cookQC; 2035 carries2034 unchanged byassumption; milkFAO2023 heldfixed; mixed-source scalecheck"
            reference = inputs["transfer"][year]
            for (
                profile,
                chicken_price,
                milk_price,
                chicken_basis,
                yield_value,
                density,
                price_date,
                deflation,
            ) in profiles:
                chicken_value = value_check(
                    poultry,
                    chicken_price,
                    "poultry_meat_kg",
                    chicken_basis,
                    fx,
                    yield_value,
                )
                milk_value = value_check(
                    milk, milk_price, "milk_equivalent_kg", "PKR_per_litre", fx, density
                )
                for share in SHARES:
                    chicken_capture, milk_capture = (
                        chicken_value * share,
                        milk_value * share,
                    )
                    total = chicken_capture + milk_capture
                    output.append(
                        {
                            "quantity_family": family,
                            "comparison_year": year,
                            "price_profile": profile,
                            "capture_share": share,
                            "poultry_quantity_thousand_tonnes": poultry,
                            "poultry_quantity_year": poultry_year,
                            "milk_quantity_thousand_tonnes": milk,
                            "milk_quantity_year": milk_year,
                            "quantity_note": quantity_note,
                            "price_observation_date": price_date,
                            "price_year": 2025,
                            "currency": "USD",
                            "fx_pkr_per_usd_2025": fx,
                            "price_adjustment": deflation,
                            "poultry_price_pkr_2025": chicken_price,
                            "poultry_price_basis": chicken_basis,
                            "dressed_live_yield_assumption": (
                                "not_applied_to_cuts"
                                if yield_value is None
                                else yield_value
                            ),
                            "milk_price_pkr_per_litre_2025": milk_price,
                            "milk_density_kg_per_litre_sensitivity": density,
                            "poultry_conventional_value_million_usd": chicken_value,
                            "milk_equivalent_conventional_value_million_usd": milk_value,
                            "poultry_capture_million_usd": chicken_capture,
                            "milk_capture_million_usd": milk_capture,
                            "combined_capture_million_usd": total,
                            "transfer_p10_million_usd": reference["p10"],
                            "transfer_p90_million_usd": reference["p90"],
                            "poultry_comparison": flag(chicken_capture, reference),
                            "milk_comparison": flag(milk_capture, reference),
                            "combined_comparison": flag(total, reference),
                            "combined_to_p90_ratio": total / reference["p90"],
                            "mapping_status": "conditional_unvalidated; neither observedretailvalue noralternativeproteinforecast",
                        }
                    )
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    """Write deterministic data with explicit headers and six-decimal float displays."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.6f}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def main() -> None:
    """Build an offline companion while preserving all original source/reference bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=HERE / "build/pakistan-topdown"
    )
    args = parser.parse_args()
    inputs = extract(args.workspace.resolve())
    rows = generate(inputs)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "pakistan_topdown.csv", rows)
    write_csv(args.output_dir / "naheed_normalized.csv", inputs["retail"])
    (args.output_dir / "extracted-inputs.json").write_text(
        json.dumps(inputs, indent=2, sort_keys=True) + "\n"
    )
    # Recheck all input hashes after execution, including the 127 reference rows.
    checked_sources(args.workspace.resolve())
    receipt = {
        "rows": len(rows),
        "reference_rows": 127,
        "reference_sha256": inputs["reference_sha256"],
        "combined_above_10x_p90_rows": sum(
            "above_10x" in row["combined_comparison"] for row in rows
        ),
        "poultry_above_10x_p90_rows": sum(
            "above_10x" in row["poultry_comparison"] for row in rows
        ),
        "milk_above_10x_p90_rows": sum(
            "above_10x" in row["milk_comparison"] for row in rows
        ),
        "approval": "User30Oct2026: Continue the conditional check with explicit caveats.",
        "scientific_acceptance": "unvalidated mapping; humanreviewpending",
        "network_calls": 0,
        "output_sha256": digest(args.output_dir / "pakistan_topdown.csv"),
    }
    (args.output_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
