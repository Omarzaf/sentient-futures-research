"""Stage USDA coverage evidence and September GAIN rows without shared writes."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import UTC, datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RAW = ROOT / "data/raw/national/usda-poultry-2026-10-13"
LICENSE = "Not stated in retrieved artifact; public access does not establish redistribution license."
BASE = "https://apps.fas.usda.gov/"
SOURCES = [
    (
        "usda_psd_bulk_livestock_20261009",
        "PSD livestock bulk CSV archive; HTTP Last-Modified 9 October 2026",
        BASE + "psdonline/downloads/psd_livestock_csv.zip",
        "2026",
        "Historical poultry coverage only for India; no Pakistan poultry rows. No 2025/2026 poultry observations in either target country.",
    ),
    (
        "usda_psd_bulk_all_20261009",
        "PSD all-commodities bulk CSV archive; HTTP Last-Modified 9 October 2026",
        BASE + "psdonline/downloads/psd_alldata_csv.zip",
        "2026",
        "Independent complete-archive coverage check agrees with livestock subset for both countries. No country values inferred from Others.",
    ),
    (
        "usda_psd_coverage_notice_202110",
        "Livestock and Poultry: World Markets and Trade, October 2021; discontinued-series notice",
        BASE + "PSDOnline/Circulars/2021/10/Livestock_poultry.pdf",
        "2021",
        "PDF/printed page 17 explicitly lists India Chicken Meat and Pakistan Beef and Veal as discontinued after 2015. Context, not current values.",
    ),
    (
        "usda_gain_india_in2026_0049",
        "India Livestock and Products Annual, IN2026-0049, 23 September 2026",
        BASE
        + "newgainapi/api/Report/DownloadReportByFileName?fileName=Livestock+and+Products+Annual_New+Delhi_India_IN2026-0049.pdf",
        "2026",
        "Table 2, PDF/printed page 6; New Post estimates and forecast, distinct from USDA Official columns. Older than October 2026 PSD vintage; preserve report-specific series. Includes carabeef. No poultry data extracted.",
    ),
    (
        "usda_gain_required_schedule_2026",
        "2026 GAIN required reporting schedule, as of 13 January 2026",
        "https://gain.fas.usda.gov/assets/GAIN%20Report%20Schedule.pdf",
        "2026",
        "Planning context only; actual release dates differ. No required India poultry or Pakistan poultry/livestock entry; cannot exclude unscheduled reports.",
    ),
    (
        "usda_psd_public_catalog_20261013",
        "PSD public application and anonymous country availability catalog, accessed 13 October 2026",
        BASE + "psdonline/app/index.html",
        "2026",
        "Public catalog corroborates historical poultry end years. API lists India beef through 2026 while bulk includes 2027; coverage catalog may lag bulk. No authentication or API key used.",
    ),
    (
        "usda_gain_public_catalog_20261013",
        "GAIN public application and unsuccessful anonymous catalog reads, 13 October 2026",
        "https://gain.fas.usda.gov/",
        "2026",
        "HTML/scripts retrieved; anonymous country lookup and read-only poultry search returned HTTP 401. No authentication attempted. Unexecuted livestock request draft retained. Diagnostic context only; no numerical evidence.",
    ),
]


def write_csv(name: str, rows: list[dict], fields: list[str] | None = None) -> None:
    """Write a local staged CSV with explicit fields for an empty output."""
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    """Hash exact artifact bytes without modifying the input."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_archives() -> tuple[list[dict], list[dict], list[dict]]:
    """Stream both bulk archives and preserve matching country poultry rows."""
    coverage, subsets, totals = [], {}, []
    commodities = {
        "0115000": "Meat, Chicken",
        "0114200": "Poultry, Meat, Broiler",
    }
    for basename, member, source in [
        ("psd-livestock.zip", "psd_livestock.csv", SOURCES[0][0]),
        ("psd-all.zip", "psd_alldata.csv", SOURCES[1][0]),
    ]:
        selected = []
        total = 0
        with zipfile.ZipFile(RAW / basename) as archive:
            assert archive.namelist() == [member], archive.namelist()
            with archive.open(member) as binary:
                reader = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig"))
                for csv_row, row in enumerate(reader, 2):
                    total += 1
                    if row["Country_Name"].strip() in ("India", "Pakistan") and any(
                        term in row["Commodity_Description"].lower()
                        for term in (
                            "chicken",
                            "poultry",
                            "broiler",
                            "turkey",
                            "duck",
                            "goose",
                        )
                    ):
                        assert row["Commodity_Code"] in commodities, row
                    if (
                        row["Country_Name"].strip() in ("India", "Pakistan")
                        and row["Commodity_Code"] in commodities
                    ):
                        selected.append(
                            {
                                **row,
                                "source_id": source,
                                "raw_file": str((RAW / basename).relative_to(ROOT)),
                                "raw_locator": f"{member}; CSV row {csv_row} (header is row 1)",
                                "evidence_status": "HISTORICAL_ONLY_NOT_2025_2026",
                            }
                        )
        totals.append({"file": basename, "csv_member": member, "total_rows": total})
        subsets[basename] = selected
        for country in ("India", "Pakistan"):
            for code, name in commodities.items():
                matches = [
                    r
                    for r in selected
                    if r["Country_Name"].strip() == country
                    and r["Commodity_Code"] == code
                ]
                years = [int(r["Market_Year"]) for r in matches]
                contemporary = sum(y in (2025, 2026) for y in years)
                assert contemporary == 0
                coverage.append(
                    {
                        "country": country,
                        "commodity_code": code,
                        "commodity": name,
                        "matching_rows": len(matches),
                        "first_market_year": min(years) if years else "",
                        "last_market_year": max(years) if years else "",
                        "rows_market_year_2025_or_2026": contemporary,
                        "source_id": source,
                        "raw_file": str((RAW / basename).relative_to(ROOT)),
                        "raw_locator": f"Complete scan of {member}",
                        "status": (
                            "HISTORICAL_ONLY" if years else "NO_SERIES_IN_ARCHIVE"
                        ),
                        "notes": "Row count is an acquisition coverage diagnostic, not a national market estimate. Empty year bounds mean no series, not zero output.",
                    }
                )
    left, right = subsets.values()
    keys = [k for k in left[0] if k not in ("source_id", "raw_file", "raw_locator")]
    assert [tuple(r[k] for k in keys) for r in left] == [
        tuple(r[k] for k in keys) for r in right
    ], "Bulk archives disagree for the target poultry series"
    assert len(left) == 413
    assert [r["matching_rows"] for r in coverage[:4]] == [153, 260, 0, 0]
    return coverage, left, totals


def extract_gain() -> list[dict]:
    """Select New Post columns and assert every source balance equation."""
    pages = (RAW / "gain-india-in2026-0049.txt").read_text().split("\f")
    assert "September 23, 2026" in pages[0]
    table = pages[5].split("Production\n", 1)[0]
    assert "Table 2: India:" in table and "Jan 2025" in table and "Jan 2027" in table
    rows = []
    for label, metric in [
        (r"Production \(1000 MT CWE\)", "production"),
        (r"Total Imports \(1000 MT CWE\)", "imports"),
        (r"Total Exports \(1000 MT CWE\)", "exports"),
        (r"Human Dom\. Consumption \(1000", "human_domestic_consumption"),
    ]:
        match = re.search(r"^" + label + r"\s+([\d\s]+)$", table, re.MULTILINE)
        assert match, label
        values = match.group(1).split()
        assert len(values) == 6, (label, values)
        for year, index in zip((2025, 2026, 2027), (1, 3, 5), strict=True):
            rows.append(
                {
                    "country": "India",
                    "year": year,
                    "item": "bovine meat",
                    "metric": metric,
                    "value": values[index],
                    "unit": "1000 tonnes carcass weight equivalent",
                    "source_id": SOURCES[3][0],
                    "source_vintage": "2026-09-23",
                    "sample_size": "",
                    "sample_basis": "FAS New Delhi post supply-and-demand estimates; no survey sample denominator supplied in Table 2.",
                    "flag": ("post_forecast" if year == 2027 else "post_estimate")
                    + ";vintage_2026-09-23;superseded_vintage;new_post_column",
                    "method": "Direct table transcription of New Post columns; no conversion, extrapolation or imputation.",
                    "period": str(year),
                    "raw_file": str(
                        (RAW / "gain-india-in2026-0049.pdf").relative_to(ROOT)
                    ),
                    "raw_locator": "Table 2; printed/PDF page 6; New Post column",
                    "notes": "Calendar market year begins January. Includes carabeef. September GAIN vintage precedes October 9 official PSD; retain separate series. 2026 is an incomplete-year estimate and 2027 a forecast. 2027 USDA Official zeros are not selected. Consumption is a balance-sheet quantity, not measured intake or retail sales.",
                }
            )
    for year in (2025, 2026, 2027):
        values = {r["metric"]: int(r["value"]) for r in rows if r["year"] == year}
        assert values["production"] + values["imports"] == (
            values["exports"] + values["human_domestic_consumption"]
        ), year
    assert len(rows) == 12
    return rows


def extract_schedule() -> list[dict]:
    """Save target-country required-report entries without asserting publication."""
    rows = []
    pages = (RAW / "gain-2026-schedule.txt").read_text().split("\f")
    for page, text in enumerate(pages, 1):
        for line in text.splitlines():
            match = re.match(
                r"^\s*(.*?)\s{2,}(India|Pakistan)\s{2,}(New Delhi|Islamabad)\s+(\d+/\d+/\d+)\s*$",
                line,
            )
            if match:
                report, country, post, planned = match.groups()
                rows.append(
                    {
                        "report": report,
                        "country": country,
                        "post": post,
                        "planned_date": planned,
                        "source_id": SOURCES[4][0],
                        "raw_locator": f"PDF/printed page {page}",
                        "status": "SCHEDULE_ONLY_NOT_RELEASE_EVIDENCE",
                    }
                )
    relevant = [
        r for r in rows if any(k in r["report"] for k in ("Livestock", "Poultry"))
    ]
    assert len(relevant) == 2 and all(r["country"] == "India" for r in relevant)
    return rows


def provenance() -> tuple[list[dict], list[dict]]:
    """Cover every raw artifact, including failures and unexecuted request drafts."""
    sources = [
        {
            "source_id": source,
            "title": title,
            "publisher": "USDA Foreign Agricultural Service",
            "url": url,
            "year": year,
            "accessed": "2026-10-13",
            "tier": "B",
            "access_method": "curl public HTTPS; original download headers preserved; derivatives local only",
            "license": LICENSE,
            "notes": note,
        }
        for source, title, url, year, note in SOURCES
    ]
    groups = {
        "psd-livestock.zip": (0, SOURCES[0][2]),
        "psd-all.zip": (1, SOURCES[1][2]),
        "psd-discontinued-2021-10": (2, SOURCES[2][2]),
        "gain-india-in2026-0049": (3, SOURCES[3][2]),
        "gain-2026-schedule": (4, SOURCES[4][2]),
        "psd-index.html": (5, SOURCES[5][2]),
        "psd-services.js": (5, BASE + "psdonline/app/applicationServicesJs?v=05132016"),
        "psd-app.js": (5, BASE + "psdonline/app/applicationJs?v=05132016"),
        "psd-availability-IN.json": (
            5,
            BASE
            + "PSDOnlineApi/api/downloadableData/GetAvailabilitybyCountry?countryCode=IN",
        ),
        "psd-availability-PK.json": (
            5,
            BASE
            + "PSDOnlineApi/api/downloadableData/GetAvailabilitybyCountry?countryCode=PK",
        ),
        "gain-index.html": (6, SOURCES[6][2]),
        "gain-main.js": (6, "https://gain.fas.usda.gov/main-es2018.js"),
        "gain-countries.json": (6, BASE + "newgainapi/api/Lookup/GetAllCountries"),
        "gain-search-poultry": (6, BASE + "newgainapi/api/Search/GetSearchResults"),
        "gain-search-livestock": (6, BASE + "newgainapi/api/Search/GetSearchResults"),
    }
    manifest = []
    for path in sorted(RAW.iterdir()):
        matches = [
            (key, val) for key, val in groups.items() if path.name.startswith(key)
        ]
        assert len(matches) == 1, (path, matches)
        _, (index, url) = matches[0]
        if "livestock.request" in path.name:
            note = "LOCAL UNEXECUTED read-only search draft; URL is intended endpoint, not a completed request. No request sent after poultry search returned 401."
        elif path.name.endswith("request.json"):
            note = "LOCAL request body for executed anonymous read-only search; corresponding response HTTP 401. No credentials supplied."
        elif path.suffix == ".txt":
            note = "DERIVED pdftotext -layout from same-stem PDF; original source URL retained."
        elif path.suffix == ".png":
            note = "DERIVED pdftoppm -r 110 visual inspection of page identified in filename; original PDF URL retained."
        elif path.name.endswith("headers"):
            note = "curl HTTP response headers; status retained as received."
        else:
            note = "Original public response bytes."
        if "gain-countries" in path.name or (
            "gain-search-poultry" in path.name
            and not path.name.endswith("request.json")
        ):
            note += " HTTP 401 diagnostic; ineligible for numerical use."
        manifest.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": url,
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, UTC
                ).isoformat(),
                "sha256": digest(path),
                "license": LICENSE,
                "source_id": SOURCES[index][0],
                "notes": note
                + " Timestamp is local file completion time; derivatives are not a new retrieval.",
            }
        )
    assert {r["source_id"] for r in manifest} <= {r["source_id"] for r in sources}
    return sources, manifest


def main() -> None:
    """Rebuild isolated staged data, diagnostics and integrity receipts only."""
    coverage, historic, totals = extract_archives()
    national = extract_gain()
    schedule = extract_schedule()
    sources, manifest = provenance()
    write_csv("psd_target_coverage.csv", coverage)
    write_csv("psd_historical_poultry_rows.csv", historic)
    write_csv("gain_national_rows.csv", national)
    write_csv("gain_schedule_rows.csv", schedule)
    write_csv("source_rows.csv", sources)
    write_csv("manifest_rows.csv", manifest)
    api_summary = {}
    for country in ("IN", "PK"):
        records = json.loads((RAW / f"psd-availability-{country}.json").read_text())
        poultry = [
            r
            for r in records
            if any(k in r["commodity"] for k in ("Chicken", "Broiler"))
        ]
        assert all(r["maxYear"] < 2025 for r in poultry)
        assert len(poultry) == (2 if country == "IN" else 0)
        api_summary[country] = poultry
    validation = {
        "status": "PASS",
        "scope": "Isolated staging only; no shared register, processed dataset, dashboard, STATE or verifier output writes.",
        "bulk_archives": totals,
        "matching_historical_poultry_rows": len(historic),
        "coverage_rows": len(coverage),
        "archive_poultry_subsets_identical": True,
        "target_country_poultry_rows_2025_2026": 0,
        "gain_national_rows": len(national),
        "gain_balance_checks": "2025/2026/2027 production + imports = exports + human domestic consumption; all pass",
        "gain_2027_official_zero_columns_selected": False,
        "required_schedule_target_country_rows": len(schedule),
        "public_api_poultry_coverage": api_summary,
        "source_rows": len(sources),
        "manifest_rows": len(manifest),
        "all_raw_files_covered": len(manifest) == len(list(RAW.iterdir())),
        "visually_checked_pdf_pages": [
            "gain-india-in2026-0049.pdf:6",
            "psd-discontinued-2021-10.pdf:17",
        ],
        "numeric_country_gap": "No current USDA poultry series established. This is missing evidence, not zero national output.",
    }
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
