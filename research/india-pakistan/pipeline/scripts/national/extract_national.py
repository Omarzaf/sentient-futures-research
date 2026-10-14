"""Extract bounded national series from downloaded official documents."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/national"
OUT = Path(__file__).resolve().parent
FIELDS = [
    "country",
    "year",
    "item",
    "metric",
    "value",
    "unit",
    "source_id",
    "flag",
    "method",
    "period",
    "raw_file",
    "raw_locator",
    "notes",
]


def numeric_tokens(text: str) -> list[str]:
    """Read table numeric tokens without changing source precision."""
    return [token.replace(",", "") for token in text.split()]


def extract() -> list[dict[str, str]]:
    """Return source-linked rows with fiscal periods and forecast vintages."""
    rows: list[dict[str, str]] = []

    def add(**values: str) -> None:
        """Append one fully shaped evidence row."""
        rows.append({field: values.get(field, "") for field in FIELDS})

    pak = (RAW / "pakistan-economic-survey-2024-25-agriculture.txt").read_text()
    table = pak.split("TABLE 2.15", 1)[1]
    matches = re.findall(r"^(20\d{2}-\d{2})\s+([\d,.\s]+)$", table, re.MULTILINE)
    assert len(matches) == 15, f"Expected 15 fiscal-year rows, got {len(matches)}"
    for period, text in matches:
        values = numeric_tokens(text)
        assert len(values) == 12, (period, values)
        for item, index, unit in [
            ("bovine meat", 1, "1000 tonnes"),
            ("mutton (source category)", 2, "1000 tonnes"),
            ("poultry meat", 3, "1000 tonnes"),
            ("eggs", 9, "million eggs"),
        ]:
            add(
                country="Pakistan",
                year=period[:4],
                item=item,
                metric="production",
                value=values[index],
                unit=unit,
                source_id="pakistan_economic_survey_2024_25",
                flag="official_estimate;fiscal_year_start",
                method="Transcribed from table; source estimates based on inter-census growth rates of Livestock Censuses 1996 and 2006; no analyst imputation.",
                period=period,
                raw_file="data/raw/national/pakistan-economic-survey-2024-25-agriculture.pdf",
                raw_locator="Table 2.15; printed page 43; PDF page 39",
                notes="Year is the start of the fiscal-year label, not a calendar-year estimate. Source beef mapped to bovine; source mutton category retained without assigning an unsupported sheep/goat split. Not retail sales.",
            )
    # Do not take the inconsistent 2024-25 milk observation in Table 2.15.
    table26 = pak.split("Table 2.6:", 1)[1].split("Table 2.7:", 1)[0]
    for label, metric in [
        (r"Milk \(Gross Production\)", "production"),
        (r"Milk \(Human Consumption\)3", "human_consumption_supply"),
    ]:
        match = re.search(
            r"^" + label + r"\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$",
            table26,
            re.MULTILINE,
        )
        assert match, label
        for year, value in zip([2022, 2023, 2024], match.groups(), strict=True):
            add(
                country="Pakistan",
                year=str(year),
                item="milk",
                metric=metric,
                value=value.replace(",", ""),
                unit="1000 tonnes",
                source_id="pakistan_economic_survey_2024_25",
                flag="official_estimate;fiscal_year_start",
                period=f"{year}-{str(year + 1)[-2:]}",
                raw_file="data/raw/national/pakistan-economic-survey-2024-25-agriculture.pdf",
                raw_locator="Table 2.6; printed page 28; PDF page 9",
                method="Source estimates; milk human consumption deducts 20% from gross cow and buffalo milk, as explained in source footnote 3.",
                notes="Human-consumption supply is a source model, not measured dietary intake. Table 2.15 milk 2024-25 is inconsistent and not used.",
            )

    pages = (RAW / "usda-livestock-poultry-circular.txt").read_text().split("\f")
    production_page = pages[9]
    series = [
        ("production", production_page.split("Total Dom. Consumption", 1)[0], 10),
        (
            "total_domestic_consumption",
            production_page.split("Total Dom. Consumption", 1)[1],
            10,
        ),
        ("exports", pages[10].split("Total Exports", 1)[1], 11),
    ]
    for metric, text, page in series:
        match = re.search(r"^\s*India\s+([\d,\s]+)$", text, re.MULTILINE)
        assert match, metric
        values = numeric_tokens(match.group(1))
        assert len(values) == 6, (metric, values)
        for year, value in zip(range(2022, 2028), values, strict=True):
            add(
                country="India",
                year=str(year),
                item="bovine meat",
                metric=metric,
                value=value,
                unit="1000 tonnes carcass weight equivalent",
                source_id="usda_psd_livestock_2026_10",
                flag=("forecast" if year >= 2026 else "USDA_estimate")
                + ";vintage_2026-10-09",
                period=str(year),
                method="USDA PSD table value; no conversion or imputation.",
                raw_file="data/raw/national/usda-livestock-poultry-circular.pdf",
                raw_locator=f"Beef and Veal {'Trade' if metric == 'exports' else 'Production'} - Top Countries Summary; printed/PDF page {page}",
                notes="Includes carabeef (water buffalo). Consumption is a balance-sheet quantity, not retail value. Preserve vintage when comparing to GAIN February 2026.",
            )

    gain = (
        (RAW / "usda-india-livestock-2026.txt")
        .read_text()
        .split("Table 2. India: Commodity", 1)[1]
        .split("PRODUCTION", 1)[0]
    )
    for label, metric in [
        ("Production", "production"),
        ("Total Imports", "imports"),
        ("Total Exports", "exports"),
        ("Human Dom. Consumption", "human_domestic_consumption"),
    ]:
        match = re.search(
            r"^" + re.escape(label) + r"[^\n]*?\)\s+([\d\s]+)$", gain, re.MULTILINE
        )
        if label == "Human Dom. Consumption":
            match = re.search(
                r"^Human Dom\. Consumption \(1000 MT\s+([\d\s]+)\nCWE\)",
                gain,
                re.MULTILINE,
            )
        assert match, label
        values = numeric_tokens(match.group(1))
        assert len(values) == 6, (label, values)
        for year, value in zip(range(2024, 2027), values[1::2], strict=True):
            add(
                country="India",
                year=str(year),
                item="bovine meat",
                metric=metric,
                value=value,
                unit="1000 tonnes carcass weight equivalent",
                source_id="usda_gain_india_in2026_0009",
                flag=("post_forecast" if year == 2026 else "post_estimate")
                + ";vintage_2026-02-23;superseded_vintage",
                method="Selected New Post columns, not USDA Official columns. Report explicitly states Not Official USDA Data.",
                period=str(year),
                raw_file="data/raw/national/usda-india-livestock-2026.pdf",
                raw_locator="Table 2; PDF page 4; New Post columns",
                notes="GAIN Post assessments; mostly carabeef. More recent USDA PSD circular is preferred for latest-vintage comparison. Do not sum across vintages.",
            )

    text = html.unescape(
        re.sub(r"<[^>]+>", " ", (RAW / "india-bahs-2025-release.html").read_text())
    )
    text = re.sub(r"\s+", " ", text)
    for pattern, item, unit in [
        (
            r"total Meat production in the country is estimated as ([\d.]+) million tonnes",
            "meat total",
            "million tonnes",
        ),
        (
            r"meat production from poultry is ([\d.]+) million tonnes",
            "poultry meat",
            "million tonnes",
        ),
        (
            r"total Milk production in the country is estimated as ([\d.]+) million tonnes",
            "milk",
            "million tonnes",
        ),
        (
            r"total Egg production in the country is estimated as ([\d.]+) billion nos",
            "eggs",
            "billion eggs",
        ),
    ]:
        match = re.search(pattern, text)
        assert match, item
        add(
            country="India",
            year="2024",
            item=item,
            metric="production",
            value=match.group(1),
            unit=unit,
            source_id="india_bahs_2025_pib",
            flag="official_estimate;survey_year_start",
            method="Official BAHS 2025 release reproducing ISS estimates; sample count is not stated on release page.",
            period="2024-25",
            raw_file="data/raw/national/india-bahs-2025-release.html",
            raw_locator=f"Milk, Egg, Meat and Wool Production 2024-25; {item} production paragraph",
            notes="Release dates ISS March 2024-February 2025 but prints nonexistent 29 February 2025. Month bounds retained; exact end date unresolved. DAHD full book returned HTTP 404.",
        )
    return rows


def main() -> None:
    """Write extracted rows and run structural/source-table validation."""
    rows = extract()
    with (OUT / "extracted_rows.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    assert len(rows) == 100, len(rows)
    assert all(float(row["value"]) >= 0 for row in rows)
    assert len(
        {
            tuple(
                row[field]
                for field in ["country", "year", "item", "metric", "source_id"]
            )
            for row in rows
        }
    ) == len(rows)
    print(
        f"PASS: {len(rows)} source-linked rows; fiscal labels, native units and vintages retained."
    )


if __name__ == "__main__":
    main()
