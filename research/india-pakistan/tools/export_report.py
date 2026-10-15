"""Regenerate the report exports and record exact text parity without claiming visual QA."""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from verify_edition import (
    Context,
    checked_run,
    docx_text,
    export_files,
    normalized_text,
    report_pdf_text,
    sha,
    write_json,
)

ROOT = Path(__file__).resolve().parent.parent


def keep_word_rows_together(path: Path) -> int:
    """Prevent Word table rows from splitting, preserving every text node unchanged."""
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ET.register_namespace("w", namespace)
    before = docx_text(path)
    with zipfile.ZipFile(path) as source:
        parts = [(item, source.read(item.filename)) for item in source.infolist()]
    document = ET.fromstring(
        {item.filename: data for item, data in parts}["word/document.xml"]
    )
    table_rows = document.findall(f".//{{{namespace}}}tr")
    for row in table_rows:
        properties = row.find(f"{{{namespace}}}trPr")
        if properties is None:
            properties = ET.Element(f"{{{namespace}}}trPr")
            row.insert(0, properties)
        if properties.find(f"{{{namespace}}}cantSplit") is None:
            ET.SubElement(properties, f"{{{namespace}}}cantSplit")
    with zipfile.ZipFile(path, "w") as output:
        for item, data in parts:
            if item.filename == "word/document.xml":
                data = ET.tostring(document, encoding="utf-8", xml_declaration=True)
            output.writestr(item, data)
    if docx_text(path) != before:
        raise ValueError("Word row-pagination repair changed document text")
    return len(table_rows)


def comparison(expected: str, actual: str) -> dict[str, object]:
    """Report exact normalized equality and the first differing character only."""
    first = next(
        (
            index
            for index, pair in enumerate(zip(expected, actual))
            if pair[0] != pair[1]
        ),
        min(len(expected), len(actual)),
    )
    return {
        "pass": expected == actual,
        "expected_characters": len(expected),
        "actual_characters": len(actual),
        "first_difference": None if expected == actual else first,
        "expected_context": (
            "" if expected == actual else expected[max(0, first - 120) : first + 200]
        ),
        "actual_context": (
            "" if expected == actual else actual[max(0, first - 120) : first + 200]
        ),
    }


def main() -> None:
    """Build both formats from the current Markdown through the frozen exporter."""
    context = Context(ROOT)
    with tempfile.TemporaryDirectory(prefix="supervisor-report-export-") as temporary:
        pdf, docx, authored = export_files(context, Path(temporary))
        word_rows = keep_word_rows_together(docx)
        for source in (pdf, docx):
            shutil.copyfile(source, ROOT / "report" / source.name)
        expected = normalized_text(authored)
        results = {
            "pdf": comparison(expected, normalized_text(report_pdf_text(context, pdf))),
            "docx": comparison(expected, normalized_text(docx_text(docx))),
        }
    receipt = {
        "created_at": datetime.now(UTC).isoformat(),
        "markdown_sha256": sha(ROOT / "report/REPORT.md"),
        "pdf_sha256": sha(ROOT / "report/report.pdf"),
        "docx_sha256": sha(ROOT / "report/report.docx"),
        "comparisons": results,
        "word_rows_kept_together": word_rows,
        "pdfinfo": checked_run(["pdfinfo", str(ROOT / "report/report.pdf")]),
        "visual_review": "pending",
        "all_text_matches": all(result["pass"] for result in results.values()),
    }
    write_json(ROOT / "logs/report-export-parity.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
