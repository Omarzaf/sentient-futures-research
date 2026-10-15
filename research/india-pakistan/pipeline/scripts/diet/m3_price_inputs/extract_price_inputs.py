"""Stage exact PBS price-index cells for review without applying a deflator."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RAW = ROOT / "data/raw/diet/m3-survey-inputs-2026-10-13"
REPORTS = (
    ("cpi-october-2024", "2024-10", "2024-09", "Oct 24", "Sep 24"),
    ("cpi-december-2024", "2024-12", "2024-11", "Dec 24", "Nov 24"),
    ("cpi-february-2025", "2025-02", "2025-01", "Feb 25", "Jan 25"),
    ("cpi-april-2025", "2025-04", "2025-03", "Apr 25", "Mar 25"),
    ("cpi-june-2025-current", "2025-06", "2025-05", "June 25", "May 25"),
)


def digest(path: Path) -> str:
    """Hash exact source bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> None:
    """Extract current/prior index columns from fixed source tables, retaining lines."""
    rows = []
    for stem, current, prior, current_header, prior_header in REPORTS:
        source = RAW / (stem + ".pdf")
        meta = json.loads((RAW / (stem + ".pdf.meta.json")).read_text())
        assert meta["http_code"] == 200 and source.read_bytes().startswith(b"%PDF")
        text = OUT / (stem + ".txt")
        pages = text.read_text().split("\f")
        for number, residence, pdf_page in (
            (1, "all", 8),
            (2, "urban", 9),
            (3, "rural", 10),
        ):
            page = pages[pdf_page - 1]
            assert f"Table {number}:" in page and "Base 2015-16" in page
            assert current_header in page and prior_header in page
            for marker, series in (
                ("Food & Non-alcoholic Bev.", "food_and_non_alcoholic_beverages"),
                ("Restaurants & Hotels", "restaurants_and_hotels"),
            ):
                lines = [line for line in page.splitlines() if marker in line]
                assert len(lines) == 1
                line = lines[0]
                values = re.findall(r"-?\d+\.\d+", line.split(marker)[1])
                assert len(values) == 8, (stem, number, line)
                for column, period in enumerate((current, prior), start=1):
                    rows.append(
                        {
                            "country": "Pakistan",
                            "residence": residence,
                            "period": period,
                            "series": series,
                            "value": values[column],
                            "unit": "index_2015_16_100",
                            "source_id": "pbs_"
                            + stem.replace("-current", "").replace("-", "_"),
                            "tier": "A",
                            "pdf_page": str(pdf_page),
                            "table": str(number),
                            "column": (
                                "current_month" if column == 1 else "previous_month"
                            ),
                            "source_line": line.strip(),
                            "raw_file": str(source.relative_to(ROOT)),
                            "raw_sha256": digest(source),
                            "text_file": str(text.relative_to(ROOT)),
                            "text_sha256": digest(text),
                            "status": "source_cell_extracted_not_applied_see_review_receipt",
                        }
                    )
    keys = [(r["residence"], r["period"], r["series"]) for r in rows]
    assert len(keys) == len(set(keys)) == 60
    assert sum(r["period"] >= "2024-10" for r in rows) == 54
    with (OUT / "price_indices_staging.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    review_path = OUT / "visual_review.json"
    visual_review = json.loads(review_path.read_text()) if review_path.exists() else {}
    review_valid = visual_review.get("staged_csv_sha256") == digest(
        OUT / "price_indices_staging.csv"
    )
    receipt = {
        "staged_rows": len(rows),
        "fieldwork_period_rows": 54,
        "source_reports": 5,
        "pdf_pages": [8, 9, 10],
        "uniqueness_and_source_header_checks": "pass",
        "visual_review_complete": review_valid,
        "visual_reviewer": visual_review.get("reviewer") if review_valid else None,
        "applied_to_survey": False,
        "notes": "Current/prior columns only; September2024 retained as adjacent context. Food group differs from restaurant/hotel group. No CPI MoM chaining, cross-group substitution or nutrient imputation performed. Deflator suitability remains a separate methodological review.",
        "output_sha256": digest(OUT / "price_indices_staging.csv"),
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    build()
