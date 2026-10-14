"""Extract exact overall CPI indices separately from frozen food-price inputs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
PARENT = OUT.parent
sys.path.insert(0, str(PARENT))
from extract_price_inputs import RAW, REPORTS, ROOT


def digest(path: Path) -> str:
    """Bind each source or generated artifact to its exact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> None:
    """Retain current and previous overall indices without price adjustment."""
    rows = []
    for stem, current, prior, current_header, prior_header in REPORTS:
        source = RAW / (stem + ".pdf")
        text = PARENT / (stem + ".txt")
        pages = text.read_text().split("\f")
        for number, residence, pdf_page in (
            (1, "all", 8),
            (2, "urban", 9),
            (3, "rural", 10),
        ):
            page = pages[pdf_page - 1]
            assert f"Table {number}:" in page and "Base 2015-16" in page
            assert current_header in page and prior_header in page
            lines = [
                s for s in page.splitlines() if re.match(r"^\s*General\s+100\.00", s)
            ]
            assert len(lines) == 1
            line = lines[0]
            values = re.findall(r"-?\d+\.\d+", line)
            assert len(values) == 8 and values[0] == "100.00"
            for column, period in enumerate((current, prior), start=1):
                rows.append(
                    {
                        "country": "Pakistan",
                        "residence": residence,
                        "period": period,
                        "series": "overall_cpi",
                        "value": values[column],
                        "unit": "index_2015_16_100",
                        "tier": "A",
                        "source_id": "pbs_"
                        + stem.replace("-current", "").replace("-", "_"),
                        "pdf_page": str(pdf_page),
                        "table": str(number),
                        "column": "current_month" if column == 1 else "previous_month",
                        "source_line": line.strip(),
                        "raw_file": str(source.relative_to(ROOT)),
                        "raw_sha256": digest(source),
                        "text_sha256": digest(text),
                        "status": "EXTRACTED_NOT_APPLIED_SEE_VISUAL_REVIEW",
                    }
                )
    assert len({(r["residence"], r["period"]) for r in rows}) == len(rows) == 30
    assert sum(r["period"] >= "2024-10" for r in rows) == 27
    target = OUT / "overall_cpi.csv"
    with target.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    receipt = {
        "rows": 30,
        "fieldwork_rows": 27,
        "source_reports": 5,
        "output_sha256": digest(target),
        "applied_to_survey": False,
        "notes": "Overall CPI, not food CPI. September retained as adjacent context. No chained rounded inflation rates or provincial prices inferred.",
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    build()
