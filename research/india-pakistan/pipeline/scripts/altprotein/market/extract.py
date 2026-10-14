"""Extract GFI India's historical market estimates and source-published scenarios."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/altprotein/market"
SOURCE = "gfi_india_smart_protein_economic_analysis_2022"
URL = "https://gfi-india.org/wp-content/uploads/2024/06/GFI-India-economic-analysis.pdf"
LICENSE = "No explicit reuse license identified in the four-page PDF"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write CSV records while preserving explicit missing values."""
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def numeric_lines(section: str) -> list[list[str]]:
    """Read standalone numeric table lines, retaining a printed missing dash."""
    result = []
    for line in section.splitlines():
        line = re.sub(r"^\s*(LOW|MEDIUM|HIGH)\s+", "", line)
        if re.fullmatch(r"\s*[\d,-]+(?:\s+[\d,-]+)*\s*", line):
            result.append([word.replace(",", "") for word in line.split()])
    return result


def extract() -> list[dict[str, str]]:
    """Parse the page-four tables without synthesizing any scenario or baseline."""
    pages = (RAW / "gfi-india-economic-analysis.txt").read_text().split("\f")
    assert len(pages) == 5 and not pages[-1].strip()
    assert "Smart Protein" in pages[0] and "Deloitte" in pages[0]
    page = pages[3]
    domestic_section, export_rest = page.split("EXPORT POTENTIAL BY 2030", 1)
    export_section = export_rest.split("ECONOMIC", 1)[0]
    domestic = numeric_lines(domestic_section)
    export_lines = numeric_lines(export_section)
    assert [len(row) for row in domestic] == [5, 5, 5, 5]
    assert [len(row) for row in export_lines] == [6, 6, 1, 5]
    # Poppler places cultivated high 4,158 on a separate line above its peers.
    export = export_lines[:2] + [
        export_lines[3][:4] + export_lines[2] + export_lines[3][4:]
    ]
    assert domestic[0] == ["100", "250", "1", "-", "351"]
    assert export[2] == ["6824", "1889", "631", "819", "4158", "14321"]
    for scenarios in (domestic[1:], export):
        for scenario in scenarios:
            assert sum(int(value) for value in scenario[:-1]) == int(scenario[-1])
    assert sum(int(value) for value in domestic[0][:-1] if value != "-") == 351
    segments = [
        "plant_based_meat",
        "plant_based_dairy",
        "plant_based_eggs",
        "fermentation_derived_meat",
        "all_smart_protein",
    ]
    export_segments = segments[:-1] + ["cultivated_meat", segments[-1]]
    rows = []
    for scope, names, scenarios in (
        ("domestic", segments, domestic[1:]),
        ("export", export_segments, export),
    ):
        for index, segment in enumerate(names):
            row = base_row(segment, "2030", scope)
            row.update(
                low=scenarios[0][index],
                central=scenarios[1][index],
                high=scenarios[2][index],
                estimate_type="source_published_forward_scenarios",
                range_semantics="Source low-growth, medium-growth, high-growth scenarios; not confidence bounds or an analyst estimate. Central is the published medium-growth scenario, not an expected value.",
                source_locator=f"PDF page 4, {'DOMESTIC MARKET SIZE' if scope == 'domestic' else 'EXPORT POTENTIAL'} BY 2030 (IN INR CR), {segment}, low/medium/high growth rows",
                method="Direct source table extraction. Domestic models use penetration, adoption, replacement, prices, localization and R&D assumptions; export models use overseas categories and adjacent-product export trends. See PDF pages 1-2; detailed numerical model inputs are not disclosed in this summary.",
                missing_reason="",
            )
            if segment == "cultivated_meat":
                row["segment_scope_note"] = (
                    "Source footnote includes growth factors and recombinant protein production; not solely finished cultivated meat food sales. No domestic cultivated-meat scenario is published."
                )
                row["source_conflict"] = (
                    "Page 4 table high is 4158 INR crore; page 3 narrative says 4152. Preserve table value, which reconciles to the published export total."
                )
            rows.append(row)
    for index, segment in enumerate(segments):
        row = base_row(segment, "2022", "domestic")
        value = domestic[0][index]
        row.update(
            central="" if value == "-" else value,
            estimate_type="historical_source_market_estimate",
            range_semantics="Source publishes one point estimate, not a range; low/high remain missing. The source does not identify this as audited sales or disclose baseline-specific data and uncertainty.",
            source_locator=f"PDF page 4, DOMESTIC MARKET SIZE BY 2030 table, CURRENT MARKET SIZE (2022) row, {segment}",
            method="Direct source current-market-size baseline transcription. Treat as a GFI/Deloitte historical market estimate, not observed official or audited sales.",
            missing_reason=(
                "Printed dash; not zero and no estimate inferred"
                if value == "-"
                else ""
            ),
        )
        rows.append(row)
    assert len(rows) == 16
    assert (
        len({(row["year"], row["segment"], row["market_scope"]) for row in rows}) == 16
    )
    for row in rows:
        if all(row[key] for key in ("low", "central", "high")):
            assert (
                Decimal(row["low"]) <= Decimal(row["central"]) <= Decimal(row["high"])
            )
    return rows


def base_row(segment: str, year: str, scope: str) -> dict[str, str]:
    """Define source-bound metadata shared by each market record."""
    return {
        "country": "India",
        "year": year,
        "segment": segment,
        "metric": "domestic_market_size" if scope == "domestic" else "export_potential",
        "low": "",
        "central": "",
        "high": "",
        "unit": "INR crore",
        "source_id": SOURCE,
        "tier": "B",
        "market_scope": scope,
        "estimate_type": "",
        "range_semantics": "",
        "source_locator": "",
        "method": "",
        "source_date": "",
        "source_date_note": "No printed publication date on cover or other pages. PDF metadata creation and modification dates are 2022-10-12; baseline explicitly 2022. URL /2024/06/ denotes upload path, not proven publication date.",
        "source_vintage": "2022-context analysis; precise publication date unconfirmed",
        "stale": "true",
        "stale_note": "Historical model and baseline; accessed in 2026 but not an updated current-market estimate. Do not use 2030 scenarios as current sales or imply a 2024 model refresh from upload path.",
        "currency_basis": "Source INR crore; no exchange-rate or inflation conversion performed. Price base (nominal/constant and base year) is not explicitly stated in the summary.",
        "segment_scope_note": "Source categories and totals retained; no combined domestic-plus-export figure is constructed. Total overlaps component rows and must not be added to them.",
        "source_conflict": "Page 2 combined headline 12075-33194 INR crore does not equal page 4 domestic-plus-export totals 12057-33284; combined headline excluded from extracted rows. Page 3 USD export summary also conflicts with its INR endpoints; only table INR retained.",
        "missing_reason": "",
        "raw_file": "data/raw/altprotein/market/gfi-india-economic-analysis.pdf",
        "raw_sha256": hashlib.sha256(
            (RAW / "gfi-india-economic-analysis.pdf").read_bytes()
        ).hexdigest(),
    }


def write_provenance() -> None:
    """Stage source and raw-file registry rows without editing shared ledgers."""
    pdf = RAW / "gfi-india-economic-analysis.pdf"
    metadata = subprocess.run(
        ["pdfinfo", str(pdf)], check=True, capture_output=True, text=True
    ).stdout
    assert re.search(r"CreationDate:.*2022", metadata)
    (RAW / "pdfinfo.txt").write_text(metadata)
    write_csv(
        OUT / "source_rows.csv",
        [
            {
                "source_id": SOURCE,
                "title": "Smart Protein Economic Analysis",
                "publisher": "The Good Food Institute India, in collaboration with Deloitte India",
                "url": URL,
                "year": "2022",
                "accessed": datetime.fromtimestamp(pdf.stat().st_mtime, UTC)
                .date()
                .isoformat(),
                "tier": "B",
                "access_method": "curl official GFI India PDF; Poppler layout extraction and page-four visual review",
                "license": LICENSE,
                "notes": "Year denotes 2022 analysis context supported by PDF metadata dated 12 October 2022 and explicit 2022 baseline; precise publication date absent from printed report. The 2024/06 URL is not publication-date evidence. Four-page summary with proprietary GFI/Deloitte modeling; stale historical estimates and forward scenarios. Source arithmetic/narrative conflicts logged in notes/M5-MARKET-HANDOFF.md. Not audited sales. No Pakistan coverage.",
            }
        ],
    )
    manifest = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        if path.suffix == ".pdf":
            note = "Original official GFI India PDF download; four-page summary."
        elif path.name == "pdfinfo.txt":
            note = "DERIVED Poppler pdfinfo metadata for parent gfi-india-economic-analysis.pdf; timezone shown by local process."
        elif path.suffix == ".txt":
            note = "DERIVED pdftotext -layout extraction from parent gfi-india-economic-analysis.pdf."
        else:
            note = "DERIVED Poppler page render from parent gfi-india-economic-analysis.pdf; PDF page encoded in filename."
        manifest.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": URL,
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, UTC
                ).isoformat(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "license": LICENSE,
                "source_id": SOURCE,
                "notes": note,
            }
        )
    write_csv(OUT / "manifest_rows.csv", manifest)


def main() -> None:
    """Write all bounded market records and their provenance staging files."""
    write_csv(OUT / "extracted_rows.csv", extract())
    write_provenance()
    print(
        "PASS: 16 India records; 11 published 2030 scenario triplets, 4 historical 2022 point estimates, 1 explicit missing baseline; source conflicts preserved."
    )


if __name__ == "__main__":
    main()
