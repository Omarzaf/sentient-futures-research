"""Write a deterministic SVG of speculative spending shares using only stdlib.

Read the recorded shares directly; do not divide rounded report values.
Only D1-figure-us-share.svg is written. Run with python3 from any directory.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

SOURCE = Path(__file__).resolve().parents[1] / "data/altprotein_proxy_scenarios.csv"
OUTPUT = Path(__file__).with_name("D1-figure-us-share.svg")
COUNTRIES = ("India", "Pakistan")
YEARS = ("2026", "2030", "2035")
STATISTICS = ("p10", "p50", "p90")
QUANTITY = "per_capita_share_of_us_2025"


def read_values() -> tuple[dict[tuple[str, str, str], dict[str, str]], dict[str, str]]:
    """Require a complete, unique set of finite, ordered scenario shares."""
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    selected = [
        row for row in records
        if row["record_type"] == "scenario" and row["quantity"] == QUANTITY
        and row["country"] in COUNTRIES and row["year"] in YEARS
        and row["statistic"] in STATISTICS
    ]
    values = {(row["country"], row["year"], row["statistic"]): row for row in selected}
    expected = {(country, year, stat) for country in COUNTRIES
                for year in YEARS for stat in STATISTICS}
    if set(values) != expected or len(selected) != len(expected):
        raise ValueError("Missing or duplicate scenario share rows")
    for country in COUNTRIES:
        for year in YEARS:
            numbers = [Decimal(values[country, year, stat]["value"]) for stat in STATISTICS]
            if any(not value.is_finite() or value < 0 for value in numbers):
                raise ValueError("Non-finite or negative spending share")
            if numbers != sorted(numbers):
                raise ValueError("Scenario quantiles are out of order")
    benchmarks = [row for row in records
                  if row["row_id"] == "united_states_2025_retail_per_capita_value"]
    if len(benchmarks) != 1:
        raise ValueError("Expected exactly one US spending benchmark")
    benchmark = Decimal(benchmarks[0]["value"])
    if not benchmark.is_finite() or benchmark <= 0:
        raise ValueError("Invalid US spending benchmark")
    return values, benchmarks[0]


def render_svg() -> str:
    """Render shared-scale ranges and exact CSV values without timestamps."""
    values, benchmark = read_values()
    maximum = max(Decimal(row["value"]) for row in values.values())
    if maximum <= 0:
        raise ValueError("A positive share is required for the chart scale")
    left, width = 170, 380

    def x(value: str) -> str:
        """Map a share onto the common linear plot scale."""
        return f"{Decimal(left) + Decimal(value) / maximum * width:.3f}"

    def text(x_pos: int, y_pos: int, value: str, css: str = "") -> str:
        """Escape a text label for XML."""
        return f'<text x="{x_pos}" y="{y_pos}" class="{css}">{escape(value)}</text>'

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="650" '
        'viewBox="0 0 1080 650" role="img" aria-labelledby="title description">',
        '<title id="title">India and Pakistan: spending per person as a share of US spending</title>',
        '<desc id="description">Speculative scenarios for India and Pakistan in '
        + ", ".join(YEARS)
        + '. Points show middle values; whiskers show p10 to p90 ranges on one linear scale. '
        'All values are percentages of observed US spending per person in '
        + benchmark["year"] + '. These ranges are not calibrated confidence intervals.</desc>',
        '<metadata>Source: research/india-pakistan/data/altprotein_proxy_scenarios.csv; '
        'quantity: ' + QUANTITY + '; values copied directly from scenario rows. '
        'AI-assisted working figure; human verification pending.</metadata>',
        '<style>text{font-family:Arial,sans-serif;fill:#172b35;font-size:16px}'
        '.title{font-size:25px;font-weight:bold}.note{font-size:14px;fill:#4a5c65}'
        '.heading{font-size:14px;font-weight:bold}.number{font-variant-numeric:tabular-nums}'
        '.country{font-weight:bold}</style>',
        '<rect width="1080" height="650" fill="#fbfaf6"/>',
        text(32, 45, "Spending per person remains far below the US benchmark", "title"),
        text(32, 76, "Percent of US spending per person; middle values with p10 to p90 ranges"),
        '<g data-row-id="' + benchmark["row_id"] + '">',
        text(32, 103, "US " + benchmark["year"] + " benchmark: $" + benchmark["value"]
             + " per person at constant prices", "note"),
        '</g>',
        text(32, 147, "Country / year", "heading"),
        text(600, 147, "Lower (p10)", "heading"),
        text(750, 147, "Middle (p50)", "heading"),
        text(900, 147, "Upper (p90)", "heading"),
        '<path d="M170 163 V522" stroke="#85959d" stroke-width="1"/>',
    ]
    for country_index, country in enumerate(COUNTRIES):
        colour = ("#165d83", "#9a4d20")[country_index]
        for year_index, year in enumerate(YEARS):
            y_pos = 190 + country_index * 180 + year_index * 50
            rows = [values[country, year, stat] for stat in STATISTICS]
            lo, middle, hi = [x(row["value"]) for row in rows]
            parts.extend([
                '<g>',
                '<title>' + country + ' ' + year + ': '
                + '; '.join(row["statistic"] + ' ' + row["value"] + '%' for row in rows)
                + '</title>',
                text(32, y_pos + 6, country + ' ' + year, "country"),
                f'<path d="M{left} {y_pos} H{left + width}" stroke="#dce2e4"/>',
                f'<path d="M{lo} {y_pos} H{hi} M{lo} {y_pos - 7} V{y_pos + 7} '
                f'M{hi} {y_pos - 7} V{y_pos + 7}" stroke="{colour}" stroke-width="3"/>',
                f'<circle cx="{middle}" cy="{y_pos}" r="6" fill="{colour}"/>',
            ])
            for column, row in enumerate(rows):
                parts.extend([
                    '<g data-row-id="' + row["row_id"]
                    + '" data-value="' + row["value"] + '">',
                    text(600 + column * 150, y_pos + 6, row["value"] + '%', "number"),
                    '</g>',
                ])
            parts.append('</g>')
    parts.extend([
        text(170, 547, "Shares increase to the right; the left boundary is zero.", "note"),
        text(32, 584, "Source: altprotein_proxy_scenarios.csv. Values are speculative spending scenarios.", "note"),
        text(32, 610, "AI-assisted working figure. Human verification pending.", "note"),
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    """Write only the owned SVG artifact as deterministic UTF-8 bytes."""
    OUTPUT.write_bytes(render_svg().encode("utf-8"))
    print(f"Wrote {OUTPUT.name} from {SOURCE.name}")


if __name__ == "__main__":
    main()
