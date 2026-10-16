"""Check numerical checkpoint claims against saved outputs and source identities."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

__all__ = ["verify_report"]
PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]


def _json(path: Path) -> Any:
    """Read an explicit local JSON evidence file."""
    return json.loads(path.read_text())


def _private_file(base: Path, relative: str) -> Path:
    """Keep ledger source and output reads inside the private packet."""
    file = (base / relative).resolve()
    if not file.is_relative_to(base.resolve()):
        raise ValueError("Ledger path escapes private packet")
    return file


def verify_report(data_dir: Path) -> dict:
    """Verify available numeric findings without accepting incomplete research."""
    ledger = _json(data_dir / "claims-ledger.json")
    report = (data_dir / "REPORT.md").read_text()
    text = subprocess.check_output(
        ["pdftotext", str(data_dir / "REPORT.pdf"), "-"], text=True
    )
    pakistan = _json(data_dir / "tables/pakistan-reproduction.json")
    india = _json(data_dir / "tables/india-reproduction.json")
    retail = _json(data_dir / "tables/retail/coverage.json")
    with (data_dir / "tables/market/published-context.csv").open() as stream:
        context = {row["id"]: row for row in csv.DictReader(stream)}
    ids = [row["id"] for row in ledger["claims"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate claim IDs")
    for row in ledger["claims"]:
        claim_id = row["id"]
        source = _private_file(data_dir, row["source_file"])
        if hashlib.sha256(source.read_bytes()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"Changed claim source: {claim_id}")
        code = (REPOSITORY / row["code_path"]).resolve()
        if not code.is_relative_to(REPOSITORY.resolve()):
            raise ValueError("Code path escapes research repository")
        if hashlib.sha256(code.read_bytes()).hexdigest() != row["code_sha256"]:
            raise ValueError(f"Changed producing code: {claim_id}")
        if row.get("new_market_estimate") is not False:
            raise ValueError("Checkpoint contains an unaccepted market estimate")
        if claim_id == "B-PK-REPORT":
            actual = pakistan["diagnostics"][0]["published_report_target"]
        elif claim_id == "B-PK-XLS":
            actual = pakistan["official_workbook_chicken"]["national"]
        elif claim_id.startswith("B-PK-MICRO-"):
            selector = row["output_row"]
            matches = [
                item
                for item in pakistan["diagnostics"]
                if all(
                    item[key] == selector[key]
                    for key in ("residence", "denominator", "period_convention")
                )
            ]
            if len(matches) != 1:
                raise ValueError("Ambiguous baseline diagnostic")
            actual = matches[0]["diagnostic_kg_person_month"]
        elif claim_id.startswith("B-IN-"):
            actual = india["official_targets_g_person_day"][claim_id[5:].lower()]
        elif claim_id.startswith("CTX-"):
            actual = float(context[claim_id]["source_value"])
        elif claim_id.startswith("R-"):
            field = row["output_row"].split(".")[-1]
            actual = retail["country"][row["country"]][field]
            if (
                row["parser_code_sha256"]
                != hashlib.sha256(
                    (PACKAGE / "retail/capture.py").read_bytes()
                ).hexdigest()
            ):
                raise ValueError("Retail parser changed")
        else:
            raise ValueError(f"Unrecognised claim selector: {claim_id}")
        if actual != row["value"]:
            raise ValueError(f"Claim/output value mismatch: {claim_id}")
        token = rf"(?<![\w.]){re.escape(str(row['value']))}(?![\d.])"
        if claim_id not in report or not all(
            re.search(token, document) for document in (report, text)
        ):
            raise ValueError(f"Claim missing from Markdown or PDF: {claim_id}")
    status = _json(data_dir / "tables/readiness.json")
    if status["new_estimation_allowed"] or status["projection_allowed"]:
        raise ValueError("Unexpected estimation permission")
    return {
        "status": "PASS",
        "numeric_audit_and_context_claims": len(ids),
        "source_and_producer_hashes_checked": True,
        "markdown_and_pdf_numeric_tokens_checked": True,
        "research_complete": False,
        "reproduction_gate": "HOLD",
        "limits": "Checks the listed numerical findings and saved output lineage; dates/locators are metadata. Manual source passages and religious/linguistic interpretations still require human scholarly review. No full empirical table rebuild or new estimate is certified.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify_report(args.data_dir), indent=2))
