"""Build the speculative proxy estimate of alternative-protein market size.

Two stages share this file.

1. ``--inputs RAW_DIR`` transcribes public proxy observations from the private
   raw captures (IMF World Economic Outlook October 2026, World Bank WDI and the
   GFI US retail page) and from CSVs already in this package (FAOSTAT protein
   supply, GFI India market rows, AltProtein.Jobs counts) into
   data/altprotein_proxy_inputs.csv.
2. Without arguments, the scenario model reads only that inputs CSV and writes
   data/altprotein_proxy_scenarios.csv. It needs the standard library only and
   uses a fixed seed, so the published outputs can be regenerated from the
   public package.

The outputs are speculative scenarios built from assumptions about how proxies
carry one observed market estimate forward. They are not observed market values.

Usage:
    python3 tools/build_altprotein_proxy.py --inputs "<workspace>/OUTPUTS/Pakistan-India Data Dashboard/data/raw/altprotein/proxy"
    python3 tools/build_altprotein_proxy.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data/altprotein_proxy_inputs.csv"
OUTPUTS = ROOT / "data/altprotein_proxy_scenarios.csv"
RAW_PREFIX = "data/raw/altprotein/proxy/"

IMF = "imf_weo_2026_10"
URBAN = "worldbank_wdi_urban_population_share_2026"
FX = "worldbank_wdi_official_exchange_rate_2026"
GDP_PC = "worldbank_wdi_gdp_per_capita_2026"
GFI_US = "gfi_us_plant_based_retail_2025"
GFI_INDIA = "gfi_india_smart_protein_economic_analysis_2022"
FAO = "fao_fbs_2025_10_28"
JOBS_DIRECTORY = "altprotein_jobs_company_directory_2024"
JOBS_VACANCY = "altprotein_jobs_vacancy_2023_2025"

SEED = 20261015
DRAWS = 10000
YEARS = (2026, 2030, 2035)
ANCHOR_YEAR = 2022
PRICE_YEAR = 2025
LAST_IMF_YEAR = 2031
ANIMAL_ITEMS = (
    "Bovine Meat",
    "Eggs",
    "Fish, Seafood",
    "Milk - Excluding Butter",
    "Mutton & Goat Meat",
    "Pigmeat",
    "Poultry Meat",
)
INPUT_FIELDS = [
    "input_id",
    "country",
    "year",
    "quantity",
    "value",
    "unit",
    "source_id",
    "tier",
    "raw_file",
    "raw_sha256",
    "raw_locator",
    "notes",
]
OUTPUT_FIELDS = [
    "row_id",
    "record_type",
    "country",
    "year",
    "quantity",
    "statistic",
    "value",
    "unit",
    "tier",
    "source_ids",
    "method",
    "notes",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def build_inputs(raw_dir: Path) -> None:
    """Transcribe each proxy observation with its source, tier and locator."""
    rows: list[dict[str, str]] = []

    def add(input_id, country, year, quantity, value, unit, source, tier, raw, digest, locator, notes):
        rows.append(
            dict(
                input_id=input_id,
                country=country,
                year=str(year),
                quantity=quantity,
                value=str(value),
                unit=unit,
                source_id=source,
                tier=tier,
                raw_file=raw,
                raw_sha256=digest,
                raw_locator=locator,
                notes=notes,
            )
        )

    imf_series = {
        "NGDP_RPCH": ("real_gdp_growth", "percent per year", range(2023, LAST_IMF_YEAR + 1), ("IND", "PAK")),
        "LP": ("population", "million people", range(2022, LAST_IMF_YEAR + 1), ("IND", "PAK", "USA")),
        "PCPIPCH": ("consumer_price_inflation", "percent per year", range(2023, 2026), ("IND",)),
    }
    names = {"IND": "India", "PAK": "Pakistan", "USA": "United States"}
    for code, (quantity, unit, years, countries) in imf_series.items():
        path = raw_dir / f"imf-weo-2026-10-{code}.json"
        values = json.loads(path.read_text())["values"][code]
        for iso in countries:
            for year in years:
                value = values[iso][str(year)]
                projected = year >= 2026 or (code == "PCPIPCH" and year >= 2026)
                add(
                    f"imf_{code.lower()}_{iso.lower()}_{year}",
                    names[iso],
                    year,
                    quantity,
                    value,
                    unit,
                    IMF,
                    "A",
                    RAW_PREFIX + path.name,
                    sha256(path),
                    f"DataMapper API v1 {code}; values.{code}.{iso}.{year}",
                    "IMF projection, World Economic Outlook October 2026" if projected else "IMF estimate or outturn, World Economic Outlook October 2026",
                )

    urban_path = raw_dir / "worldbank-SP.URB.TOTL.IN.ZS.json"
    for entry in json.loads(urban_path.read_text())[1]:
        if entry["countryiso3code"] in ("IND", "PAK") and 2015 <= int(entry["date"]) <= 2025:
            add(
                f"wdi_urban_share_{entry['countryiso3code'].lower()}_{entry['date']}",
                names[entry["countryiso3code"]],
                entry["date"],
                "urban_population_share",
                round(entry["value"], 6),
                "percent of total population",
                URBAN,
                "A",
                RAW_PREFIX + urban_path.name,
                sha256(urban_path),
                f"WDI API v2 SP.URB.TOTL.IN.ZS; {entry['countryiso3code']}; date={entry['date']}",
                "Rounded to six decimals from the API value. National urban definitions differ.",
            )

    fx_path = raw_dir / "worldbank-PA.NUS.FCRF.json"
    for entry in json.loads(fx_path.read_text())[1]:
        if entry["countryiso3code"] == "IND" and entry["date"] == str(PRICE_YEAR):
            add(
                f"wdi_exchange_rate_ind_{PRICE_YEAR}",
                "India",
                PRICE_YEAR,
                "official_exchange_rate",
                round(entry["value"], 6),
                "INR per US dollar, period average",
                FX,
                "A",
                RAW_PREFIX + fx_path.name,
                sha256(fx_path),
                f"WDI API v2 PA.NUS.FCRF; IND; date={PRICE_YEAR}",
                "Rounded to six decimals from the API value.",
            )

    # GDP per person in market terms. The spending side is in market-exchange-rate
    # dollars, so income ratios must be too; PPP ratios would mix bases.
    gdp_series = (
        ("NY.GDP.PCAP.CN", "lcu", "current local currency units per person", (("IND", 2022),)),
        ("NY.GDP.PCAP.CD", "usd", "current US dollars per person", (("USA", PRICE_YEAR), ("IND", PRICE_YEAR), ("PAK", PRICE_YEAR))),
    )
    for code, tag, unit, wanted in gdp_series:
        gdp_path = raw_dir / f"worldbank-{code}.json"
        entries = {(e["countryiso3code"], int(e["date"])): e["value"] for e in json.loads(gdp_path.read_text())[1]}
        for iso, year in wanted:
            add(
                f"wdi_gdp_per_capita_{tag}_{iso.lower()}_{year}",
                names[iso],
                year,
                f"gdp_per_capita_{tag}",
                round(entries[(iso, year)], 6),
                unit,
                GDP_PC,
                "A",
                RAW_PREFIX + gdp_path.name,
                sha256(gdp_path),
                f"WDI API v2 {code}; {iso}; date={year}",
                "Rounded to six decimals from the API value.",
            )

    gfi_path = raw_dir / "gfi-us-retail-market-research.html"
    gfi_text = gfi_path.read_text(errors="ignore")
    if "worth $7.9 billion" not in gfi_text or "dollars were down 2 percent" not in gfi_text:
        raise ValueError("GFI US page no longer contains the transcribed sentences")
    add(
        "gfi_us_retail_sales_2025",
        "United States",
        2025,
        "plant_based_retail_sales",
        "7.9",
        "billion US dollars, nominal",
        GFI_US,
        "B",
        RAW_PREFIX + gfi_path.name,
        sha256(gfi_path),
        "Section 'Plant-based foods are a $7.9 billion market in U.S. retail', first sentence",
        "SPINS retail scan data commissioned by GFI. All plant-based food categories, including milk, meat and seafood, prepared meals and others.",
    )
    add(
        "gfi_us_retail_dollar_change_2025",
        "United States",
        2025,
        "plant_based_retail_dollar_change",
        "-2",
        "percent change from previous year",
        GFI_US,
        "B",
        RAW_PREFIX + gfi_path.name,
        sha256(gfi_path),
        "Same section, second sentence: 'dollars were down 2 percent'",
        "Change in US plant-based retail dollar sales from 2024 to 2025.",
    )

    market = read_csv(ROOT / "data/altprotein_market.csv")
    for row in market:
        if row["country"] == "India" and row["segment"] == "all_smart_protein" and row["metric"] == "domestic_market_size":
            for column in ("low", "central", "high"):
                if row[column]:
                    add(
                        f"gfi_india_domestic_{row['year']}_{column}",
                        "India",
                        row["year"],
                        "smart_protein_domestic_market" if row["year"] == "2022" else "smart_protein_domestic_market_scenario",
                        row[column],
                        "INR crore, price base not stated",
                        GFI_INDIA,
                        "B",
                        row["raw_file"],
                        row["raw_sha256"],
                        row["source_locator"],
                        "Copied from data/altprotein_market.csv. GFI India and Deloitte model estimate, not audited sales.",
                    )

    fao = read_csv(ROOT / "data/meat_supply_national.csv")
    for row in fao:
        if row["year"] == "2023" and row["metric"] == "protein_supply_quantity" and row["item"] in ANIMAL_ITEMS:
            add(
                "fao_protein_" + row["country"].lower() + "_" + row["item_code"],
                row["country"],
                2023,
                "animal_protein_supply_item",
                row["value"],
                row["unit"],
                FAO,
                "A",
                row["raw_file"],
                "",
                row["raw_locator"] + "; item=" + row["item"],
                "Copied from data/meat_supply_national.csv.",
            )

    jobs = read_csv(ROOT / "data/altprotein_jobs.csv")
    for country in ("India", "Pakistan"):
        directory = [r for r in jobs if r["record_type"] == "directory_row" and r["country"] == country]
        add(
            f"jobs_directory_rows_{country.lower()}",
            country,
            2024,
            "job_board_directory_rows",
            len(directory),
            "directory rows",
            JOBS_DIRECTORY,
            "C",
            directory[0]["raw_file"],
            directory[0]["raw_sha256"],
            "Count of directory rows in data/altprotein_jobs.csv for the country",
            "Directory membership is not proof of current operation.",
        )
        for row in jobs:
            if row["record_type"] == "annual_vacancies" and row["country"] == country:
                add(
                    f"jobs_vacancies_{country.lower()}_{row['year']}",
                    country,
                    row["year"],
                    "job_board_annual_vacancies",
                    row["value"],
                    "vacancies",
                    JOBS_VACANCY,
                    "C",
                    row["raw_file"],
                    row["raw_sha256"],
                    row["raw_locator"],
                    "Country basis (headquarters or job location) not documented by the table.",
                )

    with INPUTS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=INPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"inputs": str(INPUTS.relative_to(ROOT)), "rows": len(rows)}))


def quantile(values: list[float], q: float) -> float:
    """Linear interpolation between order statistics (numpy's default method)."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


class Inputs:
    def __init__(self, rows: list[dict[str, str]]):
        self.rows = {r["input_id"]: r for r in rows}
        self.used: set[str] = set()

    def get(self, key: str) -> float:
        row = self.rows[key]
        self.used.add(row["source_id"])
        return float(row["value"])


def run_model() -> None:
    """Carry the one observed Indian market estimate forward with proxy scenarios."""
    data = Inputs(read_csv(INPUTS))
    rows: list[dict[str, str]] = []
    all_sources = sorted({r["source_id"] for r in data.rows.values()})

    def emit(record_type, country, year, quantity, statistic, value, unit, sources, method, notes=""):
        rows.append(
            dict(
                row_id=f"{country.lower().replace(' ', '_')}_{year}_{quantity}_{statistic}",
                record_type=record_type,
                country=country,
                year=str(year),
                quantity=quantity,
                statistic=statistic,
                value=f"{value:.6f}",
                unit=unit,
                tier="derived",
                source_ids=json.dumps(sorted(sources)),
                method=method,
                notes=notes,
            )
        )

    # Population, million people. WEO stops in 2031; later years keep the 2031 growth rate.
    def population(iso: str, year: int) -> float:
        if year <= LAST_IMF_YEAR:
            return data.get(f"imf_lp_{iso}_{year}")
        last = data.get(f"imf_lp_{iso}_{LAST_IMF_YEAR}")
        growth = last / data.get(f"imf_lp_{iso}_{LAST_IMF_YEAR - 1}")
        return last * growth ** (year - LAST_IMF_YEAR)

    # Real GDP per person index, 2022 = 1, from real GDP growth and population growth.
    def income_index(iso: str, year: int) -> float:
        index = 1.0
        for y in range(ANCHOR_YEAR + 1, year + 1):
            g = data.get(f"imf_ngdp_rpch_{iso}_{min(y, LAST_IMF_YEAR)}") / 100
            pop_ratio = population(iso, y) / population(iso, y - 1)
            index *= (1 + g) / pop_ratio
        return index

    # Urban share: 2025 observation plus the 2015-2025 least-squares slope.
    def urban(iso: str, year: int) -> float:
        points = [(y, data.get(f"wdi_urban_share_{iso}_{y}")) for y in range(2015, 2026)]
        if year <= 2025:
            return dict(points)[year]
        mean_x = sum(x for x, _ in points) / len(points)
        mean_y = sum(y for _, y in points) / len(points)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / sum((x - mean_x) ** 2 for x, _ in points)
        return dict(points)[2025] + slope * (year - 2025)

    cpi_factor = 1.0
    for year in range(ANCHOR_YEAR + 1, PRICE_YEAR + 1):
        cpi_factor *= 1 + data.get(f"imf_pcpipch_ind_{year}") / 100
    fx = data.get(f"wdi_exchange_rate_ind_{PRICE_YEAR}")

    def crore_to_usd_million(crore: float) -> float:
        return crore * 1e7 * cpi_factor / fx / 1e6

    india_2022_usd_million = crore_to_usd_million(data.get("gfi_india_domestic_2022_central"))
    india_2022_per_capita = india_2022_usd_million / data.get("imf_lp_ind_2022")
    us_per_capita = data.get("gfi_us_retail_sales_2025") * 1000 / data.get("imf_lp_usa_2025")
    # India 2022 income gets the anchor's own conversion: 2022 rupees inflated to 2025
    # with IMF consumer prices, then the 2025 exchange rate. US 2025 dollars are
    # already 2025 prices. Both sides are then market dollars at 2025 prices.
    india_2022_income = data.get("wdi_gdp_per_capita_lcu_ind_2022") * cpi_factor / fx
    income_ratio_us_india = data.get(f"wdi_gdp_per_capita_usd_usa_{PRICE_YEAR}") / india_2022_income
    elasticity_low = 1.0
    elasticity_high = math.log(us_per_capita / india_2022_per_capita) / math.log(income_ratio_us_india)
    drift_low = data.get("gfi_us_retail_dollar_change_2025") / 100
    drift_high = (data.get("jobs_vacancies_india_2025") / data.get("jobs_vacancies_india_2023")) ** 0.5 - 1
    animal = {
        c: sum(float(r["value"]) for r in data.rows.values() if r["quantity"] == "animal_protein_supply_item" and r["country"] == c)
        for c in ("India", "Pakistan")
    }
    data.used.add(FAO)
    animal_ratio = animal["Pakistan"] / animal["India"]
    per_million = {
        c: (
            data.get(f"jobs_directory_rows_{c.lower()}") / population(iso, 2025),
            data.get(f"jobs_vacancies_{c.lower()}_2025") / population(iso, 2025),
        )
        for c, iso in (("India", "ind"), ("Pakistan", "pak"))
    }
    ecosystem_low = per_million["Pakistan"][0] / per_million["India"][0]
    ecosystem_high = per_million["Pakistan"][1] / per_million["India"][1]
    income_ratio_pak_india_2025 = data.get(f"wdi_gdp_per_capita_usd_pak_{PRICE_YEAR}") / data.get(f"wdi_gdp_per_capita_usd_ind_{PRICE_YEAR}")

    def india_per_capita(year: int, elasticity: float, drift: float) -> float:
        return (
            india_2022_per_capita
            * income_index("ind", year) ** elasticity
            * urban("ind", year) / urban("ind", ANCHOR_YEAR)
            * (1 + drift) ** (year - ANCHOR_YEAR)
        )

    def pakistan_per_capita(year: int, india_value: float, elasticity: float, weight: float, ecosystem: float) -> float:
        relative_income = income_ratio_pak_india_2025 * (income_index("pak", year) / income_index("pak", 2025)) / (
            income_index("ind", year) / income_index("ind", 2025)
        )
        return (
            india_value
            * relative_income**elasticity
            * urban("pak", year) / urban("ind", year)
            * animal_ratio**weight
            * ecosystem
        )

    def simulate(fixed: dict[str, float] | None = None) -> dict[tuple[str, int], list[float]]:
        fixed = fixed or {}
        rng = random.Random(SEED)
        result: dict[tuple[str, int], list[float]] = {(c, y): [] for c in ("India", "Pakistan") for y in YEARS}
        for _ in range(DRAWS):
            elasticity = rng.uniform(elasticity_low, elasticity_high)
            drift = rng.uniform(drift_low, drift_high)
            weight = rng.uniform(0.0, 1.0)
            ecosystem = rng.uniform(ecosystem_low, ecosystem_high)
            elasticity = fixed.get("elasticity", elasticity)
            drift = fixed.get("drift", drift)
            weight = fixed.get("weight", weight)
            ecosystem = fixed.get("ecosystem", ecosystem)
            for year in YEARS:
                india = india_per_capita(year, elasticity, drift)
                result[("India", year)].append(india)
                result[("Pakistan", year)].append(pakistan_per_capita(year, india, elasticity, weight, ecosystem))
        return result

    model_sources = all_sources
    parameter_method = "Calculated from altprotein_proxy_inputs.csv by tools/build_altprotein_proxy.py"
    emit("parameter", "India", ANCHOR_YEAR, "anchor_market_value", "value", india_2022_usd_million, "million US dollars at constant prices", [GFI_INDIA, IMF, FX], parameter_method, "GFI India 2022 domestic smart-protein estimate inflated with IMF consumer prices and converted at the 2025 WDI rate. Treats the source value as nominal 2022 rupees, which the source does not state.")
    emit("parameter", "India", ANCHOR_YEAR, "anchor_per_capita", "value", india_2022_per_capita, "US dollars per person at constant prices", [GFI_INDIA, IMF, FX], parameter_method)
    emit("parameter", "United States", PRICE_YEAR, "retail_per_capita", "value", us_per_capita, "US dollars per person at constant prices", [GFI_US, IMF], parameter_method, "GFI/SPINS retail sales divided by IMF population.")
    emit("parameter", "United States", PRICE_YEAR, "per_capita_ratio_to_india_anchor", "value", us_per_capita / india_2022_per_capita, "ratio", [GFI_US, GFI_INDIA, IMF, FX], parameter_method)
    emit("parameter", "United States", PRICE_YEAR, "market_income_ratio_to_india_anchor", "value", income_ratio_us_india, "ratio", [GDP_PC, IMF, FX], parameter_method, "US 2025 GDP per person over India 2022 GDP per person, both in market-exchange-rate US dollars at 2025 prices. India uses the anchor's CPI and exchange-rate conversion.")
    emit("parameter", "United States", PRICE_YEAR, "retail_dollar_decline", "value", -drift_low * 100, "percent", [GFI_US], parameter_method, "Size of the 2025 fall in US plant-based retail dollar sales.")
    emit("parameter", "India", ANCHOR_YEAR, "monte_carlo_draws", "value", DRAWS, "draws", [IMF], parameter_method, f"Fixed seed {SEED}.")
    emit("parameter", "India", ANCHOR_YEAR, "income_elasticity", "low", elasticity_low, "elasticity", [IMF], parameter_method, "Assumption: spending rises in proportion to income.")
    emit("parameter", "India", ANCHOR_YEAR, "income_elasticity", "high", elasticity_high, "elasticity", [GFI_US, GFI_INDIA, GDP_PC, IMF, FX], parameter_method, "Elasticity that would explain the whole US-India per-person gap by income alone, with spending and income both in market dollars at 2025 prices.")
    emit("parameter", "India", ANCHOR_YEAR, "adoption_drift", "low", drift_low * 100, "percent per year", [GFI_US], parameter_method, "US 2025 plant-based retail dollar change, used as the low non-income drift.")
    emit("parameter", "India", ANCHOR_YEAR, "adoption_drift", "high", drift_high * 100, "percent per year", [JOBS_VACANCY], parameter_method, "India job-board vacancy growth 2023-2025, used as the high non-income drift.")
    emit("parameter", "India", 2023, "animal_protein_supply", "value", animal["India"], "g/capita/day", [FAO], parameter_method, "Sum of seven FAOSTAT animal-source items.")
    emit("parameter", "Pakistan", 2023, "animal_protein_supply", "value", animal["Pakistan"], "g/capita/day", [FAO], parameter_method, "Sum of seven FAOSTAT animal-source items.")
    emit("parameter", "Pakistan", 2023, "animal_protein_ratio_to_india", "value", animal_ratio, "ratio", [FAO], parameter_method)
    emit("parameter", "Pakistan", 2025, "ecosystem_factor", "low", ecosystem_low, "ratio", [JOBS_DIRECTORY, IMF], parameter_method, "Pakistan over India job-board directory rows per million people.")
    emit("parameter", "Pakistan", 2025, "ecosystem_factor", "high", ecosystem_high, "ratio", [JOBS_VACANCY, IMF], parameter_method, "Pakistan over India 2025 job-board vacancies per million people.")
    emit("parameter", "Pakistan", 2025, "market_income_ratio_to_india", "value", income_ratio_pak_india_2025, "ratio", [GDP_PC], parameter_method, "Pakistan over India 2025 GDP per person, current US dollars.")
    for iso, country in (("ind", "India"), ("pak", "Pakistan")):
        for year in (2025, 2035):
            emit("parameter", country, year, "urban_share", "value", urban(iso, year), "percent of total population", [URBAN], parameter_method, "Observed" if year <= 2025 else "Linear 2015-2025 trend continued")
        emit("parameter", country, 2035, "income_index_from_2022", "value", income_index(iso, 2035), "ratio", [IMF], parameter_method, "Real GDP per person in 2035 relative to 2022; WEO projections to 2031, 2031 growth held to 2035.")
        for year in YEARS:
            emit("parameter", country, year, "population", "value", population(iso, year), "million people", [IMF], parameter_method)

    draws = simulate()
    scenario_method = f"Monte Carlo, {DRAWS} draws, seed {SEED}, linear-interpolation quantiles; tools/build_altprotein_proxy.py"
    for (country, year), values in draws.items():
        iso = "ind" if country == "India" else "pak"
        pop = population(iso, year)
        for label, q in (("p10", 0.1), ("p50", 0.5), ("p90", 0.9)):
            per_capita = quantile(values, q)
            emit("scenario", country, year, "market_value", label, per_capita * pop, "million US dollars at constant prices", model_sources, scenario_method, "Speculative scenario quantile, not an observed value.")
            emit("scenario", country, year, "per_capita_value", label, per_capita, "US dollars per person at constant prices", model_sources, scenario_method, "Speculative scenario quantile, not an observed value.")
            emit("scenario", country, year, "per_capita_share_of_us_2025", label, per_capita / us_per_capita * 100, "percent of US retail value per person in the US observation year", model_sources, scenario_method, "Speculative scenario quantile, not an observed value.")

    gfi_sources = [GFI_INDIA, IMF, FX]
    india_2030 = [v * population("ind", 2030) for v in draws[("India", 2030)]]
    for column in ("low", "central", "high"):
        converted = crore_to_usd_million(data.get(f"gfi_india_domestic_2030_{column}"))
        emit("benchmark", "India", 2030, "gfi_india_domestic_scenario", column, converted, "million US dollars at constant prices", gfi_sources, parameter_method, "GFI India 2030 domestic scenario converted on the same nominal-rupee assumption as the anchor.")
        emit("benchmark", "India", 2030, "draws_below_gfi_scenario", column, 100 * sum(v < converted for v in india_2030) / DRAWS, "percent of draws", model_sources, scenario_method)

    years_to_2030 = 2030 - ANCHOR_YEAR
    anchor_crore = data.get("gfi_india_domestic_2022_central")
    for column in ("low", "central"):
        implied = (data.get(f"gfi_india_domestic_2030_{column}") / anchor_crore) ** (1 / years_to_2030) - 1
        emit("benchmark", "India", 2030, "gfi_india_implied_growth", column, implied * 100, "percent per year", [GFI_INDIA], parameter_method, "Yearly growth from the GFI 2022 estimate to the GFI 2030 scenario, both in the source's rupees.")
    fastest = max(v * population("ind", 2030) for v in draws[("India", 2030)]) / india_2022_usd_million
    emit("benchmark", "India", 2030, "fastest_draw_growth", "max", (fastest ** (1 / years_to_2030) - 1) * 100, "percent per year", model_sources, scenario_method, "Yearly growth of the market total from 2022 to 2030 in the fastest of the draws.")

    swings = {
        "elasticity": (elasticity_low, elasticity_high),
        "drift": (drift_low, drift_high),
        "weight": (0.0, 1.0),
        "ecosystem": (ecosystem_low, ecosystem_high),
    }
    for name, (low, high) in swings.items():
        for label, value in (("low", low), ("high", high)):
            fixed = simulate({name: value})
            for country in ("India", "Pakistan"):
                if country == "India" and name in ("weight", "ecosystem"):
                    continue
                iso = "ind" if country == "India" else "pak"
                median = quantile(fixed[(country, 2035)], 0.5) * population(iso, 2035)
                emit("sensitivity", country, 2035, f"market_value_{name}_fixed", label, median, "million US dollars at constant prices", model_sources, scenario_method, f"Median with {name} fixed at its {label} bound and other parameters drawn.")

    with OUTPUTS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"scenarios": str(OUTPUTS.relative_to(ROOT)), "rows": len(rows)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--inputs", type=Path, help="Raw proxy capture directory; rebuilds the inputs CSV first")
    args = parser.parse_args()
    if args.inputs:
        build_inputs(args.inputs)
    run_model()


if __name__ == "__main__":
    main()
