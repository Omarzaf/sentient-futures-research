"""Rebuild legacy component diagnostics and collected-source tables offline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

__all__ = ["audit_inputs", "build_readiness", "main"]

PACKAGE = Path(__file__).resolve().parent


def _read_json(path: Path) -> Any:
    """Read an explicit JSON input without network access."""
    return json.loads(path.read_text(encoding="utf-8"))


def _contained_file(root: Path, relative: str) -> Path:
    """Reject absolute, escaping and symlink-escaping input paths."""
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Input paths must stay within the private data directory")
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Input path resolves outside the private data directory")
    return resolved


def audit_inputs(data_dir: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    """Verify source identity without promoting it to factual verification."""
    records = manifest.get("files", [])
    if not isinstance(records, list):
        raise TypeError("Manifest files must be a list")
    if not all(isinstance(record, dict) for record in records):
        raise TypeError("Every manifest record must be an object")
    ids = [record.get("id") for record in records]
    paths = [record.get("path") for record in records]
    if any(not isinstance(value, str) or not value for value in ids + paths):
        raise ValueError("Every manifest record needs a nonempty ID and path")
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        raise ValueError("Duplicate manifest identity or path")
    rows = []
    for record in records:
        path = _contained_file(data_dir, record["path"])
        expected = record.get("sha256", "")
        if len(expected) != 64 or any(
            char not in "0123456789abcdef" for char in expected
        ):
            raise ValueError("Expected SHA-256 must be lowercase hexadecimal")
        status = "missing"
        actual = ""
        if path.is_file():
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            status = (
                "hash_verified"
                if actual == expected and path.stat().st_size == record.get("bytes")
                else "mismatch"
            )
        rows.append(
            {
                "source_id": record["id"],
                "path": record["path"],
                "integrity_status": status,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "source_type": record.get("source_type", "unknown"),
                "licence": record.get("licence", "unresolved"),
                "claim_verification": "not_established_by_hash",
            }
        )
    return rows


def _preregistration() -> dict[str, Any]:
    """Bind the current question file to an ancestor commit without forecasting."""
    relative = "research/protein-markets-2026/forecast-questions.json"
    questions_path = PACKAGE / "forecast-questions.json"
    if not questions_path.is_file():
        return {"status": "missing", "commit": None, "question_count": 0}
    register = _read_json(questions_path)
    questions = register.get("questions", [])
    source_ids = {source["id"] for source in register.get("sources", [])}
    valid = (
        len(questions) >= 10
        and len({question["id"] for question in questions}) == len(questions)
        and all(
            question.get("question")
            and question.get("event_deadline")
            and question.get("resolution_date")
            and question.get("official_source_ids")
            and set(question["official_source_ids"]).issubset(source_ids)
            and question.get("forecast_probability") is None
            for question in questions
        )
    )
    result = {
        "status": "invalid" if not valid else "uncommitted",
        "commit": None,
        "question_count": len(questions),
        "chronology_proves": "registration_only_not_future_execution",
    }
    if not valid:
        return result
    root = PACKAGE.parents[1]
    process = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", relative],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode or not process.stdout.strip():
        return result
    commit = process.stdout.splitlines()[-1]
    content = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if content.returncode == 0 and content.stdout == questions_path.read_bytes():
        result.update(status="committed", commit=commit)
    else:
        result["status"] = "changed_since_registration"
    return result


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    """Write a deterministic table with explicit columns and missing values."""
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _diagnostics(
    data_dir: Path, output_dir: Path, hces_dir: Path | None
) -> dict[str, Any]:
    """Rebuild available official-baseline diagnostics without running forecasts."""
    results: dict[str, Any] = {}
    commands = []
    if (data_dir / "raw/pbs-stata-2024-25.zip").is_file():
        commands.append(
            (
                "Pakistan",
                "reproduce_pakistan.py",
                [
                    "--raw-dir",
                    str(data_dir / "raw"),
                    "--output",
                    str(output_dir / "pakistan-reproduction.json"),
                ],
            )
        )
    if hces_dir is not None:
        commands.append(
            (
                "India",
                "inspect_hces.py",
                [
                    "--candidate-dir",
                    str(hces_dir),
                    "--receipt",
                    str(data_dir / "hces-candidate-receipt.json"),
                    "--report",
                    str(data_dir / "raw/mospi-report594.pdf"),
                    "--output",
                    str(output_dir / "india-reproduction.json"),
                ],
            )
        )
    for country, script, arguments in commands:
        completed = subprocess.run(
            [sys.executable, str(PACKAGE / script), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        results[country] = {
            "script": script,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        (output_dir / "diagnostic-execution.json").write_text(
            json.dumps(results, indent=2) + "\n", encoding="utf-8"
        )
        if completed.returncode not in {0, 2}:
            raise ValueError(
                f"{country} baseline diagnostic failed; inspect diagnostic-execution.json"
            )
    return results


def build_readiness(
    data_dir: Path, output_dir: Path, hces_dir: Path | None = None
) -> dict[str, Any]:
    """Build integrity and requirement tables while holding all new estimation."""
    source_manifest = data_dir / "input-manifest.json"
    manifest = (
        _read_json(source_manifest) if source_manifest.is_file() else {"files": []}
    )
    rows = audit_inputs(data_dir, manifest)
    requirements = _read_json(PACKAGE / "requirements.json")["requirements"]
    preregistration = _preregistration()
    for requirement in requirements:
        if requirement["id"] == "S12" and preregistration["status"] == "committed":
            requirement["status"] = "registration_committed_no_projection_run"
            requirement["cause"] = (
                "Question identity is committed; enforce this ancestor before future projection execution."
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = _diagnostics(data_dir, output_dir, hces_dir)
    evidence_audits = {}
    attachment_dir = data_dir / "attachment-audit/raw"
    if hces_dir is not None and all(
        (attachment_dir / name).is_file()
        for name in [
            "HCES2023-24_Vol_II-2.pdf",
            "HCES_2023_24_Imputation_Rate.xlsx",
        ]
    ):
        completed = subprocess.run(
            [
                sys.executable,
                str(PACKAGE / "inspect_hces_attachments.py"),
                "--pdf",
                str(attachment_dir / "HCES2023-24_Vol_II-2.pdf"),
                "--workbook",
                str(attachment_dir / "HCES_2023_24_Imputation_Rate.xlsx"),
                "--candidate",
                str(hces_dir),
                "--output",
                str(output_dir / "hces-documentation"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            raise ValueError(f"HCES attachment audit failed: {completed.stderr}")
        evidence_audits["hces_documentation"] = json.loads(completed.stdout)
    if (data_dir / "market/capture-receipt-batch3.json").is_file():
        script = PACKAGE / "market/build-evidence.mjs"
        completed = subprocess.run(
            [
                "node",
                str(script),
                str(data_dir / "market"),
                str(output_dir / "market"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            raise ValueError(f"Market-source audit failed: {completed.stderr}")
        evidence_audits["market_sources"] = json.loads(completed.stdout)
    if (data_dir / "retail/capture-manifest.jsonl").is_file():
        completed = subprocess.run(
            [
                sys.executable,
                str(PACKAGE / "retail/build_inventory.py"),
                "--data-dir",
                str(data_dir / "retail"),
                "--output-dir",
                str(output_dir / "retail"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode:
            raise ValueError(f"Retail-source audit failed: {completed.stderr}")
        evidence_audits["retail_sources"] = json.loads(completed.stdout)
    _write_csv(
        output_dir / "source_integrity.csv",
        rows,
        [
            "source_id",
            "path",
            "integrity_status",
            "expected_sha256",
            "actual_sha256",
            "source_type",
            "licence",
            "claim_verification",
        ],
    )
    _write_csv(
        output_dir / "requirement_status.csv",
        requirements,
        ["id", "requirement", "evidence", "status", "cause"],
    )
    status = {
        "build_scope": "readiness_baseline_diagnostics_and_available_source_tables",
        "research_complete": False,
        "new_estimation_allowed": False,
        "projection_allowed": False,
        "reproduction_gate": "HOLD",
        "gate_evaluation": "diagnostic_checkpoint_hardcoded_hold_not_dynamic_reproduction_test",
        "cause": "This command rebuilds legacy component diagnostics. Complete baseline attempts and dynamic acceptance are provided by complete_research.py; these component outputs alone cannot accept an official reproduction.",
        "input_manifest_present": source_manifest.is_file(),
        "integrity_failures": [
            row["source_id"]
            for row in rows
            if row["integrity_status"] != "hash_verified"
        ],
        "input_identity_is_not_scientific_verification": True,
        "empirical_report_tables_rebuilt": False,
        "completion_criterion_met_by_this_command": False,
        "preregistration": preregistration,
        "baseline_diagnostics": diagnostics,
        "evidence_audits": evidence_audits,
    }
    (output_dir / "readiness.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    return status


def main() -> int:
    """Run the readiness rebuild and return a distinct exit code for a held gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--hces-dir", type=Path)
    arguments = parser.parse_args()
    try:
        status = build_readiness(
            arguments.data_dir, arguments.output_dir, arguments.hces_dir
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Readiness build failed: {error}\n")
    print(json.dumps(status, indent=2))
    return 1 if status["integrity_failures"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
