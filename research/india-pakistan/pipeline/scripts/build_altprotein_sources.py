"""Extract crop production as potential feedstock context, never product sales."""

from __future__ import annotations

from decimal import Decimal
from html.parser import HTMLParser

from build_national import bulk_rows
from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = ["build"]

RAW = "data/raw/faostat_qcl_2025-12-31.zip"
ITEMS = {
    "1726": ("pulses_total", "Pulses, Total"),
    "236": ("soybeans", "Soya beans"),
    "242": ("groundnuts_in_shell", "Groundnuts, excluding shelled"),
}


class SourceTable(HTMLParser):
    """Read the public server-rendered SOPA export table without running scripts."""

    def __init__(self) -> None:
        """Initialize a single-table capture."""
        super().__init__()
        self.active = False
        self.cell_active = False
        self.rows: list[list[str]] = []
        self.row: list[str] = []
        self.cell: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Capture only text in the explicit export table."""
        if tag == "table":
            self.active = "export-table" in (dict(attrs).get("class") or "").split()
        if self.active and tag == "tr":
            self.row = []
        if self.active and tag in ("td", "th"):
            self.cell_active = True
            self.cell = []

    def handle_data(self, data: str) -> None:
        """Collect table cell text, including nested formatting."""
        if self.active and self.cell_active:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        """Finish cells and rows while ignoring commented markup."""
        if self.active and tag in ("td", "th"):
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell_active = False
        if self.active and tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = []
        if tag == "table":
            self.active = False


def sopa_rows() -> list[dict[str, str]]:
    """Register SOPA originals and retain dated soymeal production context."""
    source_id = "sopa_soymeal_tables_snapshot_2026_10_13"
    base = "https://sopa.org/"
    license_text = (
        "SOPA copyright; public access does not establish a redistribution license"
    )
    upsert_source(
        {
            "source_id": source_id,
            "title": "SOPA soymeal production and yearly soybean processing public tables, snapshot 13 October 2026",
            "publisher": "Soybean Processors Association of India; world table attributes USDA",
            "url": base + "world-soymeal-production/",
            "year": "2026",
            "accessed": "2026-10-13",
            "tier": "B",
            "access_method": "curl public server-rendered HTML; standard-library table parser",
            "license": license_text,
            "notes": "Industry-association tracker. Year2026 denotes access snapshot, not known statistical release date. World table attributes USDA Oilseeds World Markets and Trade without issue date or estimate/projection flags. Domestic extraction series is stale, ending2017-18. Production is not food-grade protein output or sales.",
        }
    )
    pages = {
        "home.html": "",
        "statistics.html": "statistics/",
        "world-soymeal-production.html": "world-soymeal-production/",
        "yearly-processing.html": "yearly-processing-of-soybean-production-of-meal-oil-october-september/",
    }
    for filename, endpoint in pages.items():
        register_raw(
            "data/raw/altprotein/sopa/" + filename,
            base + endpoint,
            source_id,
            license_text,
            "Original public HTML; no login or form action",
        )
    output = []
    for filename, metric, column in (
        (
            "world-soymeal-production.html",
            "soymeal_production_sopa_usda_table",
            "India",
        ),
        (
            "yearly-processing.html",
            "soymeal_extraction_produced_sopa_oil_year",
            "Extraction Produced (In Million Metric Ton)",
        ),
    ):
        path = ROOT / "data/raw/altprotein/sopa" / filename
        parser = SourceTable()
        parser.feed(path.read_text())
        if not parser.rows or column not in parser.rows[0]:
            raise ValueError("SOPA table header changed")
        index = parser.rows[0].index(column)
        for values in parser.rows[1:]:
            period = values[0]
            if period == "Total" or int(period.split("-")[0]) < 2010:
                continue
            if len(values) != len(parser.rows[0]):
                raise ValueError("SOPA table width changed")
            value = str(Decimal(values[index]) * 1000000)
            year = period.split("-")[0]
            output.append(
                {
                    "country": "India",
                    "source_type": "soybean_meal",
                    "year": year,
                    "metric": metric,
                    "value": value,
                    "unit": "tonnes",
                    "source_id": source_id,
                    "tier": "B",
                    "category": "plant_processing_output",
                    "source_item": column,
                    "source_value": values[index],
                    "source_unit": "million metric tonnes",
                    "period": period,
                    "flag": "source_actual_estimate_projection_status_unspecified",
                    "freshness": (
                        "stale" if int(year) < 2025 else "release_date_unspecified"
                    ),
                    "raw_file": str(path.relative_to(ROOT)),
                    "raw_locator": f"Public export-table; row={period}; column={column}",
                    "method": "Source million tonnes multiplied by exactly1000000; year is period start, not calendar-year output.",
                    "notes": "Soymeal can be used for feed and many industrial/food uses; no food-grade share, alternative-protein allocation, product capacity or retail sales inferred. Table release date and status flags are absent. Domestic oil-year series is October-September; world table period calendar is not specified. Overlapping source series must not be summed.",
                }
            )
    return output


def build() -> None:
    """Preserve published units, item identities, values and FAO observation flags."""
    output = []
    for row in bulk_rows(ROOT / RAW):
        if (
            row["Area"] not in ("India", "Pakistan")
            or row["Element Code"] != "5510"
            or row["Item Code"] not in ITEMS
            or int(row["Year"]) < 2010
        ):
            continue
        source_type, expected_label = ITEMS[row["Item Code"]]
        if row["Item"] != expected_label or row["Unit"] != "t":
            raise ValueError(
                "QCL item identity/unit changed; inspect before rebuilding"
            )
        if row["Value"] and Decimal(row["Value"]) < 0:
            raise ValueError("Negative source crop production")
        output.append(
            {
                "country": row["Area"],
                "source_type": source_type,
                "year": row["Year"],
                "metric": "crop_production_potential_feedstock_context",
                "value": row["Value"],
                "unit": "tonnes",
                "source_id": "fao_qcl_2025_12_31",
                "tier": "A",
                "category": "plant_crop",
                "item_code": row["Item Code"],
                "source_item": row["Item"],
                "source_unit": row["Unit"],
                "flag": row["Flag"],
                "raw_file": RAW,
                "raw_locator": f"AreaCode={row['Area Code']};ItemCode={row['Item Code']};ElementCode=5510;Year={row['Year']}",
                "method": "Exact FAOSTAT QCL source-code selection; original tonne values; no nutrient yield, allocation or conversion inferred.",
                "notes": "Total crop production includes many food/feed uses. It is not protein isolate capacity, alternative-meat output, consumption or sales. Pulses aggregate overlaps individual pulses; do not add them. Groundnuts are in-shell rather than edible kernel mass. "
                + row.get("Note", ""),
            }
        )
    keys = [(r["country"], r["item_code"], r["year"]) for r in output]
    if not output or len(keys) != len(set(keys)):
        raise ValueError("Missing or duplicate crop observations")
    output.sort(key=lambda r: (r["country"], r["source_type"], int(r["year"])))
    for country in ("India", "Pakistan"):
        selected = [r for r in output if r["country"] == country]
        if {r["source_type"] for r in selected} != {
            value[0] for value in ITEMS.values()
        }:
            raise ValueError("Country does not cover all three crop sources")
        print(
            f"{country}: {len(selected)} crop rows; {min(r['year'] for r in selected)}-{max(r['year'] for r in selected)}"
        )
    output.extend(sopa_rows())
    for group in ("india_policy", "pakistan"):
        output.extend(
            read_csv(ROOT / "scripts/altprotein" / group / "capacity_rows.csv")
        )
    fields = list(output[0]) + sorted(
        set().union(*(row.keys() for row in output)) - set(output[0])
    )
    write_csv(
        ROOT / "data/processed/altprotein_sources.csv",
        fields,
        [{f: row.get(f, "") for f in fields} for row in output],
    )
    print(
        f"Saved {len(output)} source/capacity context rows; unknown capacity remains blank."
    )


if __name__ == "__main__":
    build()
