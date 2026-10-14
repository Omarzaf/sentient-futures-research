"""Demonstrate eight independent corruptions per check using synthetic scratch files."""

from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib
from collections import Counter
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import patch
from xml.sax.saxutils import escape

MODULE = Path(__file__).with_name("verify_edition.py")
spec = importlib.util.spec_from_file_location("supervisor_verifier", MODULE)
assert spec is not None and spec.loader is not None
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)

PROSE = "Measured food supply describes the available national basket. Household survey means answer a different question. Neither measure identifies individual diets or predicts future adoption."
CLAIM_FIELDS = [
    "claim_id",
    "dataset",
    "filter_json",
    "operation",
    "value_column",
    "display",
    "rounding",
    "tier",
    "headline",
    "source_ids",
    "locator",
    "unit",
]


def save_csv(
    path: Path, data: list[dict[str, str]], fields: list[str] | None = None
) -> None:
    """Write a synthetic CSV with explicit field order and ordinary string cells."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def change_csv(
    root: Path, path: str, change: Callable[[list[dict[str, str]]], None]
) -> None:
    """Mutate a scratch CSV without touching any actual research dataset."""
    target = root / path
    data = v.rows(target)
    fields = list(data[0])
    change(data)
    save_csv(target, data, fields)


def change_json(root: Path, path: str, change: Callable[[Any], None]) -> None:
    """Mutate a scratch JSON receipt or configuration."""
    target = root / path
    data = v.read_json(target)
    change(data)
    v.write_json(target, data)


def replace(root: Path, path: str, old: str, new: str) -> None:
    """Require and replace one known synthetic string in a scratch file."""
    target = root / path
    text = target.read_text()
    assert old in text, (path, old)
    target.write_text(text.replace(old, new, 1))


def make_docx(path: Path, text: str) -> None:
    """Create a labelled minimal synthetic Word XML container for parser tests."""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "word/document.xml",
            f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p></w:body></w:document>',
        )


def make_png(path: Path, width: int) -> None:
    """Create a valid blank synthetic PNG, never a purported browser screenshot."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body))
        )

    header = struct.pack(">IIBBBBB", width, 300, 8, 2, 0, 0, 0)
    pixels = zlib.compress((b"\0" + b"\xff" * width * 3) * 300)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", pixels)
        + chunk(b"IEND", b"")
    )


def fixture(root: Path) -> None:
    """Build synthetic examples satisfying each production schema before corruption."""
    root.mkdir(parents=True)
    for name in ("edition", "report", "data", "logs", "publication", "library/tools"):
        (root / name).mkdir(parents=True)
    now = datetime.now(UTC).isoformat()
    config = {
        "schema_version": 1,
        "as_of": now,
        "sources": "data/sources.csv",
        "datasets": [
            {
                "id": "supply",
                "path": "data/supply.csv",
                "derived": False,
                "source_columns": ["source_id"],
            }
        ],
        "prose_files": ["edition/index.html", "report/REPORT.md"],
        "publication_root": "publication",
        "publication_allowlist": "logs/publication-allowlist.json",
        "library_root": "library",
        "exports": {"pdf_engine": "xelatex"},
    }
    v.write_json(root / "verification-config.json", config)
    save_csv(
        root / "data/sources.csv",
        [
            {
                "source_id": "official",
                "title": "Synthetic official source",
                "tier": "A",
                "url": "https://example.org/source",
                "year": "2023",
            }
        ],
    )
    save_csv(
        root / "data/supply.csv",
        [
            {
                "country": "Pakistan",
                "value": "8.72",
                "tier": "A",
                "source_id": "official",
            },
            {"country": "India", "value": "3.52", "tier": "A", "source_id": "official"},
        ],
    )
    claims = [
        {
            "claim_id": "poultry-pakistan",
            "dataset": "supply",
            "filter_json": '{"country":"Pakistan"}',
            "operation": "value",
            "value_column": "value",
            "display": "8.72",
            "rounding": "2",
            "tier": "A",
            "headline": "true",
            "source_ids": '["official"]',
            "locator": "Synthetic table, Pakistan row, supply column",
            "unit": "kg per person per year",
        }
    ]
    save_csv(root / "claims.csv", claims, CLAIM_FIELDS)
    chart = {
        "dataset": "supply",
        "filter": {},
        "columns": ["country", "value"],
        "rows": [
            {"country": "Pakistan", "value": "8.72"},
            {"country": "India", "value": "3.52"},
        ],
        "title": "Supply differs",
        "unit": "kg per person per year",
        "source_ids": ["official"],
        "caveat": "Available supply is not individual intake.",
    }
    sections = "".join(
        f'<section id="chapter-{i:02}" data-chapter="{i}" data-packages="P{min(i,12):02}"><h2>Measured supply and its limits</h2><p>{PROSE}</p></section>'
        for i in range(1, 16)
    )
    chart_html = '<figure data-chart-container="poultry"><h3>Supply differs</h3><p data-chart-unit="poultry">kg per person per year</p><p data-chart-source="poultry">Synthetic official source, tier A.</p><details><summary id="data-toggle">Show data</summary><table data-chart-table="poultry"><tr><th>country</th><th>value</th></tr><tr><td>Pakistan</td><td>8.72</td></tr><tr><td>India</td><td>3.52</td></tr></table></details></figure>'
    page = f'<!doctype html><html><head><title>Supply research</title></head><body><button id="theme">Theme</button><p>Pakistan supply is <span data-claim="poultry-pakistan">8.72</span> kg per person per year.</p><a id="source-link" href="https://example.org/source">Source</a>{sections}{chart_html}<script type="application/json" data-chart="poultry">{json.dumps(chart)}</script></body></html>'
    (root / "edition/index.html").write_text(page)
    report = (
        '# Supply research\n\nPakistan supply is [8.72]{.claim data-claim="poultry-pakistan"} kg per person per year.\n\n[Source](https://example.org/source)\n\n'
        + "\n\n".join(
            f'::: {{data-package="P{i:02}"}}\n{PROSE}\n:::' for i in range(1, 13)
        )
    )
    (root / "report/REPORT.md").write_text(report)
    (root / "INVENTORY.md").write_text(
        "\n".join(
            f"| P{i:02} | Package | Real synthetic path | {'E: chapter' if i <= 8 else 'No E requirement'} |"
            for i in range(1, 13)
        )
    )
    (root / "DESIGN-SPEC.md").write_text(
        "\n".join(f"| {i} | Title | Content |" for i in range(1, 16))
    )
    (root / "evidence.txt").write_text(
        "SYNTHETIC FIXTURE EVIDENCE. Not evidence of real research validity."
    )
    evidence_hash = v.sha(root / "evidence.txt")
    (root / "REVIEW-FIXES.md").write_text(
        "\n".join(
            f"| {key} | Synthetic finding | fixed | Synthetic local evidence in evidence.txt. |"
            for key in sorted(v.REVIEW_IDS)
        )
    )
    v.write_json(
        root / "logs/checks-review-evidence.json",
        {
            key: {
                "status": "fixed",
                "reason": "Synthetic review closed for checker testing only.",
                "evidence": [{"path": "evidence.txt", "sha256": evidence_hash}],
            }
            for key in v.REVIEW_IDS
        },
    )
    runs = []
    for width, theme in (
        (1440, "light"),
        (1440, "dark"),
        (390, "light"),
        (390, "dark"),
    ):
        shots = []
        for chapter in range(1, 16):
            path = root / f"logs/synthetic-{width}-{theme}-{chapter}.png"
            make_png(path, width)
            shots.append(
                {
                    "chapter": chapter,
                    "path": str(path.relative_to(root)),
                    "sha256": v.sha(path),
                }
            )
        runs.append(
            {
                "width": width,
                "height": 900,
                "theme": theme,
                "document_width": width,
                "console_errors": [],
                "axe": {
                    "testEngine": {"name": "axe-core", "version": "4.10.3-synthetic"},
                    "violations": [],
                },
                "keyboard": [
                    {"control_id": key, "focused": True, "key": "Tab"}
                    for key in ("theme", "source-link", "data-toggle")
                ],
                "reduced_motion": {"requested": True, "active_animations": 0},
                "screenshots": shots,
            }
        )
    printed = root / "logs/synthetic-print.pdf"
    printed.write_bytes(b"%PDF-1.7\nSYNTHETIC PRINT FIXTURE")
    v.write_json(
        root / "logs/checks-browser.json",
        {
            "synthetic": True,
            "html_sha256": v.sha(root / "edition/index.html"),
            "executed_at": now,
            "runner": "playwright",
            "browser_version": "143.0-synthetic",
            "command": ["synthetic-browser-evidence"],
            "url": "http://127.0.0.1:8798",
            "runs": runs,
            "print": {
                "path": str(printed.relative_to(root)),
                "sha256": v.sha(printed),
                "pages": 15,
                "clipped_charts": [],
                "page_reviews": [
                    {"page": page, "defects": [], "reviewed": True}
                    for page in range(1, 16)
                ],
            },
        },
    )
    v.write_json(
        root / "logs/checks-links.json",
        {
            "synthetic": True,
            "html_sha256": v.sha(root / "edition/index.html"),
            "report_sha256": v.sha(root / "report/REPORT.md"),
            "checked_at": now,
            "results": [
                {
                    "url": "https://example.org/source",
                    "status": 200,
                    "checked_at": now,
                    "method": "GET",
                    "final_url": "https://example.org/source",
                }
            ],
        },
    )
    public = root / "publication/README.md"
    public.write_text(
        "Synthetic published research summary. No real publication is implied."
    )
    v.write_json(
        root / "logs/publication-allowlist.json",
        {
            "files": [
                {
                    "path": "README.md",
                    "sha256": v.sha(public),
                    "license": "Author-owned synthetic fixture",
                }
            ]
        },
    )
    for name in (
        "build-library.mjs",
        "verify.mjs",
        "test-halal-checks.mjs",
        "test-phase1-checks.mjs",
        "test-paper-checks.mjs",
        "test-survey-checks.mjs",
        "test-fetch-citations.mjs",
    ):
        (root / "library/tools" / name).write_text(
            "// SYNTHETIC command body, external runner mocked by tests.\n"
        )
    make_docx(root / "report/report.docx", "Synthetic report text 8.72 kg.")
    (root / "report/report.pdf").write_text("%PDF-1.7\nSynthetic report text 8.72 kg.")
    make_png(root / "logs/synthetic-report-page.png", 595)
    v.write_json(
        root / "logs/checks-report-pages.json",
        {
            "synthetic": True,
            "pdf_sha256": v.sha(root / "report/report.pdf"),
            "md_sha256": v.sha(root / "report/REPORT.md"),
            "reviewed_at": now,
            "pages": [
                {
                    "page": 1,
                    "defects": [],
                    "reviewed": True,
                    "path": "logs/synthetic-report-page.png",
                    "sha256": v.sha(root / "logs/synthetic-report-page.png"),
                }
            ],
        },
    )
    v.write_json(
        root / "SYNTHETIC-ONLY.json",
        {
            "purpose": "Check semantics and corruption detection only",
            "not_real_evidence": ["browser", "links", "library", "exports"],
            "mocked_commands": True,
        },
    )


@contextmanager
def external_mocks(
    root: Path, faults: dict[str, object] | None = None
) -> Iterator[list[list[str]]]:
    """Mock only external processing in scratch tests, never in production verification."""
    faults = faults or {}
    calls: list[list[str]] = []
    builds = 0

    def process(
        argv: list[str], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        nonlocal builds
        calls.append(argv)
        stdout = ""
        code = 0
        if argv[0] == "git":
            if "rev-parse" in argv:
                stdout = (
                    str(root / "publication") if "--show-toplevel" in argv else "a" * 40
                )
            elif "ls-files" in argv:
                stdout = (
                    "\0".join(
                        str(p.relative_to(root / "library"))
                        for p in (root / "library").rglob("*")
                        if p.is_file()
                    )
                    + "\0"
                )
            elif "diff" in argv:
                stdout = (
                    "EXTRA.md\0"
                    if faults.get("unallowlisted_staged")
                    else "README.md\0"
                )
        elif argv[0] == "node":
            name = Path(argv[1]).name
            if name == "build-library.mjs":
                builds += 1
                if faults.get("build_fail") == builds:
                    code = 1
                if faults.get("drift") and builds == 2:
                    (root / "library/generated.txt").write_text(
                        "Changed only during repeat build"
                    )
            elif faults.get("fail_command") == name:
                code = 1
        elif argv[0] == "pdftotext":
            stdout = Path(argv[-2]).read_text().split("\n", 1)[1]
        elif argv[0] == "pdfinfo":
            stdout = "Pages: 15\n" if "synthetic-print" in argv[-1] else "Pages: 1\n"
        elif argv[0] == "pandoc":
            content = "Synthetic report text 8.72 kg."
            if faults.get("regenerated_text"):
                content = str(faults["regenerated_text"])
            if "--output" in argv:
                target = Path(argv[argv.index("--output") + 1])
                if target.suffix == ".docx":
                    make_docx(target, content)
                else:
                    target.write_text("%PDF-1.7\n" + content)
            else:
                stdout = json.dumps(
                    {
                        "meta": {},
                        "blocks": [{"t": "Para", "c": [{"t": "Str", "c": content}]}],
                    }
                )
        else:
            raise AssertionError(f"Unmocked external command: {argv}")
        return subprocess.CompletedProcess(
            argv, code, stdout, "Synthetic injected command failure" if code else ""
        )

    def style(text: str) -> dict[str, object]:
        issues = []
        if "SYNTHETIC_HIGH" in text:
            issues.append(
                {"severity": "high", "type": "synthetic", "text": "SYNTHETIC_HIGH"}
            )
        if "SYNTHETIC_MEDIUM" in text:
            issues.append(
                {"severity": "medium", "type": "synthetic", "text": "SYNTHETIC_MEDIUM"}
            )
        return {"issues": issues, "score": 0, "label": "synthetic test"}

    with patch.object(v, "run", process), patch.object(v, "detector", style):
        yield calls


def chart_mutation(root: Path, update: Callable[[dict[str, Any]], None]) -> None:
    """Change embedded JSON without altering the linked source CSV."""
    path = root / "edition/index.html"
    text = path.read_text()
    marker = '<script type="application/json" data-chart="poultry">'
    before, after = text.split(marker)
    payload, end = after.split("</script>", 1)
    data = json.loads(payload)
    update(data)
    path.write_text(before + marker + json.dumps(data) + "</script>" + end)


def public_mutation(root: Path, text: str, name: str = "README.md") -> None:
    """Keep a synthetic allowlist fresh so privacy failures cannot hide behind hash drift."""
    path = root / "publication" / name
    path.write_text(text)
    v.write_json(
        root / "logs/publication-allowlist.json",
        {
            "files": [
                {
                    "path": name,
                    "sha256": v.sha(path),
                    "license": "Author-owned synthetic fixture",
                }
            ]
        },
    )


def style_decision(root: Path, wrong: str) -> None:
    """Add a specifically defective medium-issue decision to the synthetic record."""
    path = root / "report/REPORT.md"
    path.write_text(path.read_text() + "\nSYNTHETIC_MEDIUM\n")
    issue = {"severity": "medium", "type": "synthetic", "text": "SYNTHETIC_MEDIUM"}
    item = {
        "file": "report/REPORT.md",
        "text_sha256": v.text_sha(v.strip_prose(path.read_text(), False)),
        "issue_key": v.issue_key(issue),
        "decision": "keep",
        "reason": "Required synthetic field term for this test.",
    }
    if wrong == "stale":
        item["text_sha256"] = "0" * 64
    elif wrong == "reason":
        item["reason"] = ""
    elif wrong == "key":
        item["issue_key"] = "0" * 64
    data = [item, item] if wrong == "duplicate" else [item]
    (root / "logs/style-decisions.md").write_text(
        "```json\n" + json.dumps(data) + "\n```\n"
    )


def corruptions() -> list[tuple[str, str, Callable[[Path], None], dict[str, object]]]:
    """Return eight distinct mutations for each stable verification check."""
    cases: list[tuple[str, str, Callable[[Path], None], dict[str, object]]] = []

    def add(
        check: str,
        name: str,
        mutation: Callable[[Path], None],
        faults: dict[str, object] | None = None,
    ) -> None:
        cases.append((check, name, mutation, faults or {}))

    for name, key, value in (
        ("multiply-value-by-thousand", "display", "8720.00"),
        ("empty-source-selection", "filter_json", '{"country":"Absent"}'),
        ("ambiguous-value-selection", "filter_json", "{}"),
        ("unknown-operation", "operation", "eval"),
        ("invalid-rounding", "rounding", "9"),
        ("missing-value-column", "value_column", "absent"),
        ("false-dataset", "dataset", "absent"),
    ):
        add(
            "C1",
            name,
            lambda r, k=key, val=value: change_csv(
                r, "claims.csv", lambda d: d[0].update({k: val})
            ),
        )
    add(
        "C1",
        "missing-numeric-cell",
        lambda r: change_csv(r, "data/supply.csv", lambda d: d[0].update(value="")),
    )
    add(
        "C2", "delete-claim-row", lambda r: save_csv(r / "claims.csv", [], CLAIM_FIELDS)
    )
    add(
        "C2",
        "untraced-prose-sentence",
        lambda r: replace(
            r,
            "report/REPORT.md",
            "# Supply research",
            "# Supply research\n\nThere are 999 households.",
        ),
    )
    add(
        "C2",
        "wrong-prose-display",
        lambda r: replace(
            r,
            "edition/index.html",
            'data-claim="poultry-pakistan">8.72',
            'data-claim="poultry-pakistan">8.73',
        ),
    )
    add(
        "C2",
        "unknown-claim-binding",
        lambda r: replace(
            r,
            "report/REPORT.md",
            'data-claim="poultry-pakistan"',
            'data-claim="unknown"',
        ),
    )
    add(
        "C2",
        "forged-date-allowance",
        lambda r: replace(
            r,
            "report/REPORT.md",
            "# Supply research",
            '# Supply [999]{.allow-number data-number-kind="date"}',
        ),
    )
    add(
        "C2",
        "naked-heading-number",
        lambda r: replace(
            r, "report/REPORT.md", "# Supply research", "# Supply research 500"
        ),
    )
    add(
        "C2",
        "excess-chapter-allowance",
        lambda r: replace(
            r,
            "report/REPORT.md",
            "# Supply research",
            '# Supply [16]{.allow-number data-number-kind="chapter"}',
        ),
    )
    add(
        "C2",
        "forged-source-ledger-cell",
        lambda r: replace(
            r,
            "edition/index.html",
            "</body>",
            '<table><tr data-source-id="official"><td data-source-column="year">9999</td></tr></table></body>',
        ),
    )
    add(
        "C3",
        "change-chart-json",
        lambda r: chart_mutation(r, lambda d: d["rows"][0].update(value="8720")),
    )
    add(
        "C3",
        "reorder-source-rows",
        lambda r: chart_mutation(r, lambda d: d["rows"].reverse()),
    )
    add(
        "C3",
        "coerce-number-cell",
        lambda r: chart_mutation(r, lambda d: d["rows"][0].update(value=8.72)),
    )
    add(
        "C3",
        "drop-chart-source-row",
        lambda r: chart_mutation(r, lambda d: d["rows"].pop()),
    )
    add(
        "C3",
        "unknown-chart-column",
        lambda r: chart_mutation(r, lambda d: d["columns"].append("missing")),
    )
    add(
        "C3",
        "empty-chart-title",
        lambda r: chart_mutation(r, lambda d: d.update(title="")),
    )
    add(
        "C3",
        "mismatched-accessible-table",
        lambda r: replace(r, "edition/index.html", "<td>8.72</td>", "<td>8.73</td>"),
    )
    add(
        "C3",
        "remove-table-toggle",
        lambda r: replace(r, "edition/index.html", "<details>", "<div>"),
    )
    add(
        "C4",
        "headline-tier-D",
        lambda r: change_csv(r, "claims.csv", lambda d: d[0].update(tier="D")),
    )
    add(
        "C4",
        "blank-source-tier",
        lambda r: change_csv(r, "data/sources.csv", lambda d: d[0].update(tier="")),
    )
    add(
        "C4",
        "unresolved-row-source",
        lambda r: change_csv(
            r, "data/supply.csv", lambda d: d[0].update(source_id="missing")
        ),
    )
    add(
        "C4",
        "blank-row-tier",
        lambda r: change_csv(r, "data/supply.csv", lambda d: d[0].update(tier="")),
    )
    add(
        "C4",
        "derived-dataset-inherits-A",
        lambda r: change_json(
            r,
            "verification-config.json",
            lambda d: d["datasets"][0].update(derived=True),
        ),
    )
    add(
        "C4",
        "aggregate-inherits-A",
        lambda r: change_csv(r, "claims.csv", lambda d: d[0].update(operation="sum")),
    )
    add(
        "C4",
        "unresolved-claim-source",
        lambda r: change_csv(
            r, "claims.csv", lambda d: d[0].update(source_ids='["missing"]')
        ),
    )
    add(
        "C4",
        "unresolved-chart-source",
        lambda r: chart_mutation(r, lambda d: d.update(source_ids=["missing"])),
    )
    add(
        "C5",
        "drop-chapter",
        lambda r: replace(
            r, "edition/index.html", 'data-chapter="15"', 'data-missing="15"'
        ),
    )
    add(
        "C5",
        "duplicate-chapter",
        lambda r: replace(
            r, "edition/index.html", 'data-chapter="15"', 'data-chapter="14"'
        ),
    )
    add(
        "C5",
        "wrong-chapter-anchor",
        lambda r: replace(
            r, "edition/index.html", 'id="chapter-15"', 'id="wrong-anchor"'
        ),
    )
    add(
        "C5",
        "remove-report-package",
        lambda r: replace(
            r, "report/REPORT.md", 'data-package="P12"', 'data-package="P11"'
        ),
    )
    add(
        "C5",
        "remove-E-package",
        lambda r: replace(
            r, "edition/index.html", 'data-packages="P01"', 'data-packages="P12"'
        ),
    )
    add(
        "C5",
        "incomplete-inventory",
        lambda r: replace(r, "INVENTORY.md", "| P12 |", "| Q12 |"),
    )
    add(
        "C5",
        "unknown-package",
        lambda r: replace(
            r, "edition/index.html", 'data-packages="P01"', 'data-packages="P99"'
        ),
    )
    add(
        "C5",
        "design-chapter-missing",
        lambda r: replace(r, "DESIGN-SPEC.md", "| 15 |", "| absent |"),
    )
    add(
        "C6",
        "open-finding",
        lambda r: replace(
            r,
            "REVIEW-FIXES.md",
            "| H1 | Synthetic finding | fixed |",
            "| H1 | Synthetic finding | open |",
        ),
    )
    add(
        "C6",
        "missing-required-finding",
        lambda r: replace(r, "REVIEW-FIXES.md", "| H1 |", "| X1 |"),
    )
    add(
        "C6",
        "missing-closure-record",
        lambda r: change_json(
            r, "logs/checks-review-evidence.json", lambda d: d.pop("H1")
        ),
    )
    add(
        "C6",
        "status-mismatch",
        lambda r: change_json(
            r,
            "logs/checks-review-evidence.json",
            lambda d: d["H1"].update(status="declined"),
        ),
    )
    add(
        "C6",
        "missing-evidence-file",
        lambda r: change_json(
            r,
            "logs/checks-review-evidence.json",
            lambda d: d["H1"]["evidence"][0].update(path="absent.txt"),
        ),
    )
    add(
        "C6",
        "stale-evidence-hash",
        lambda r: change_json(
            r,
            "logs/checks-review-evidence.json",
            lambda d: d["H1"]["evidence"][0].update(sha256="0" * 64),
        ),
    )
    add(
        "C6",
        "empty-closure-rationale",
        lambda r: change_json(
            r, "logs/checks-review-evidence.json", lambda d: d["H1"].update(reason="")
        ),
    )
    add(
        "C6",
        "empty-evidence-list",
        lambda r: change_json(
            r, "logs/checks-review-evidence.json", lambda d: d["H1"].update(evidence=[])
        ),
    )
    add(
        "C7",
        "serve-old-QA-receipt",
        lambda r: change_json(
            r, "logs/checks-browser.json", lambda d: d.update(html_sha256="0" * 64)
        ),
    )
    add(
        "C7",
        "missing-dark-mobile-run",
        lambda r: change_json(r, "logs/checks-browser.json", lambda d: d["runs"].pop()),
    )
    add(
        "C7",
        "browser-console-error",
        lambda r: change_json(
            r,
            "logs/checks-browser.json",
            lambda d: d["runs"][0].update(console_errors=["Synthetic error"]),
        ),
    )
    add(
        "C7",
        "serious-axe-violation",
        lambda r: change_json(
            r,
            "logs/checks-browser.json",
            lambda d: d["runs"][0]["axe"]["violations"].append({"impact": "serious"}),
        ),
    )
    add(
        "C7",
        "unreachable-control",
        lambda r: change_json(
            r, "logs/checks-browser.json", lambda d: d["runs"][0]["keyboard"].pop()
        ),
    )
    add(
        "C7",
        "missing-chapter-screenshot",
        lambda r: change_json(
            r, "logs/checks-browser.json", lambda d: d["runs"][0]["screenshots"].pop()
        ),
    )
    add(
        "C7",
        "stale-screenshot-hash",
        lambda r: change_json(
            r,
            "logs/checks-browser.json",
            lambda d: d["runs"][0]["screenshots"][0].update(sha256="0" * 64),
        ),
    )
    add(
        "C7",
        "clipped-print-chart",
        lambda r: change_json(
            r,
            "logs/checks-browser.json",
            lambda d: d["print"].update(clipped_charts=["poultry"]),
        ),
    )
    add(
        "C8",
        "em-dash-prose",
        lambda r: replace(r, "report/REPORT.md", "Supply research", "Supply—research"),
    )
    add(
        "C8",
        "en-dash-outside-range",
        lambda r: replace(r, "report/REPORT.md", "Supply research", "Supply–research"),
    )
    add(
        "C8",
        "high-detector-finding",
        lambda r: replace(
            r, "report/REPORT.md", "Supply research", "Supply SYNTHETIC_HIGH research"
        ),
    )
    add(
        "C8",
        "unreviewed-medium-finding",
        lambda r: replace(
            r, "report/REPORT.md", "Supply research", "Supply SYNTHETIC_MEDIUM research"
        ),
    )
    for kind in ("stale", "reason", "key", "duplicate"):
        add("C8", "medium-decision-" + kind, lambda r, k=kind: style_decision(r, k))
    add(
        "C9",
        "HTTP-404",
        lambda r: change_json(
            r, "logs/checks-links.json", lambda d: d["results"][0].update(status=404)
        ),
    )
    add(
        "C9",
        "missing-current-link",
        lambda r: change_json(
            r, "logs/checks-links.json", lambda d: d.update(results=[])
        ),
    )
    add(
        "C9",
        "stale-content-hash",
        lambda r: change_json(
            r, "logs/checks-links.json", lambda d: d.update(report_sha256="0" * 64)
        ),
    )
    add(
        "C9",
        "old-check-date",
        lambda r: change_json(
            r,
            "logs/checks-links.json",
            lambda d: d.update(
                checked_at=(datetime.now(UTC) - timedelta(days=9)).isoformat()
            ),
        ),
    )
    add(
        "C9",
        "future-check-date",
        lambda r: change_json(
            r,
            "logs/checks-links.json",
            lambda d: d.update(
                checked_at=(datetime.now(UTC) + timedelta(days=9)).isoformat()
            ),
        ),
    )
    add(
        "C9",
        "invalid-final-URL",
        lambda r: change_json(
            r,
            "logs/checks-links.json",
            lambda d: d["results"][0].update(final_url="file:///tmp/result"),
        ),
    )
    add(
        "C9",
        "invalid-HTTP-method",
        lambda r: change_json(
            r, "logs/checks-links.json", lambda d: d["results"][0].update(method="MOCK")
        ),
    )
    add(
        "C9",
        "duplicated-link-receipt",
        lambda r: change_json(
            r,
            "logs/checks-links.json",
            lambda d: d["results"].append(copy.deepcopy(d["results"][0])),
        ),
    )
    add(
        "C10",
        "insert-private-path",
        lambda r: public_mutation(
            r, "Private path /" + "Users/synthetic/" + "RECOVERY" + "/input.md"
        ),
    )
    add(
        "C10",
        "personal-email",
        lambda r: public_mutation(r, "Contact private.person" + "@" + "example.org"),
    )
    add(
        "C10",
        "Slack-private-message",
        lambda r: public_mutation(
            r, "https://app." + "slack.com/" + "archives/private"
        ),
    )
    add(
        "C10",
        "environment-file",
        lambda r: public_mutation(r, "SETTING=private", ".env"),
    )
    add(
        "C10",
        "credential-value",
        lambda r: public_mutation(r, "API" + "_KEY=synthetic_secret"),
    )
    add(
        "C10",
        "article-body-field",
        lambda r: public_mutation(r, "full" + '_text,"Copyrighted article body"'),
    )

    def escape_link(root: Path) -> None:
        target = root / "outside-publication.txt"
        target.write_text("Synthetic outside export target")
        (root / "publication/escape.txt").symlink_to(target)
        v.write_json(
            root / "logs/publication-allowlist.json",
            {
                "files": [
                    {
                        "path": "escape.txt",
                        "sha256": v.sha(target),
                        "license": "Synthetic owned",
                    }
                ]
            },
        )

    add("C10", "realpath-symlink-escape", escape_link)
    add(
        "C10",
        "unallowlisted-staged-file",
        lambda r: None,
        {"unallowlisted_staged": True},
    )
    for filename in ("build-library.mjs", "verify.mjs", "test-halal-checks.mjs"):
        add(
            "C11",
            "missing-" + filename,
            lambda r, f=filename: (r / "library/tools" / f).rename(
                r / "library/tools" / (f + ".held")
            ),
        )
    add("C11", "initial-build-fails", lambda r: None, {"build_fail": 1})
    add("C11", "library-verifier-fails", lambda r: None, {"fail_command": "verify.mjs"})
    add(
        "C11",
        "library-test-fails",
        lambda r: None,
        {"fail_command": "test-paper-checks.mjs"},
    )
    add("C11", "repeat-build-fails", lambda r: None, {"build_fail": 2})
    add("C11", "repeat-build-byte-drift", lambda r: None, {"drift": True})
    add(
        "C12",
        "PDF-text-corruption",
        lambda r: (r / "report/report.pdf").write_text(
            "%PDF-1.7\nSynthetic report text 8720 kg."
        ),
    )
    add(
        "C12",
        "DOCX-text-corruption",
        lambda r: make_docx(r / "report/report.docx", "Synthetic report text 8720 kg."),
    )
    add(
        "C12",
        "regenerated-text-differs",
        lambda r: None,
        {"regenerated_text": "Regenerated but different report text 8.72 kg."},
    )
    add(
        "C12",
        "invalid-PDF-signature",
        lambda r: (r / "report/report.pdf").write_text("Not a PDF"),
    )
    add(
        "C12",
        "invalid-DOCX-container",
        lambda r: (r / "report/report.docx").write_text("Not a DOCX"),
    )
    add(
        "C12",
        "stale-PDF-review",
        lambda r: change_json(
            r, "logs/checks-report-pages.json", lambda d: d.update(pdf_sha256="0" * 64)
        ),
    )
    add(
        "C12",
        "missing-page-review",
        lambda r: change_json(
            r, "logs/checks-report-pages.json", lambda d: d.update(pages=[])
        ),
    )
    add(
        "C12",
        "unfixed-page-defect",
        lambda r: change_json(
            r,
            "logs/checks-report-pages.json",
            lambda d: d["pages"][0].update(defects=["Clipped table"]),
        ),
    )
    return cases


def run_probes() -> dict[str, object]:
    """Check every baseline and corrupted copy, reporting exact expected failure IDs."""
    mutations = corruptions()
    counts = Counter(case[0] for case in mutations)
    assert counts == {key: 8 for key in v.CHECK_IDS}, counts
    records = []
    with tempfile.TemporaryDirectory(
        prefix="supervisor-SYNTHETIC-probes-"
    ) as temporary:
        scratch = Path(temporary)
        baseline = scratch / "baseline"
        fixture(baseline)
        with external_mocks(baseline) as calls:
            result = v.verify(baseline)
        assert result["all_pass"], json.dumps(result, indent=2)
        assert any(c[0] == "pandoc" for c in calls)
        assert sum(c[:2] == ["node", "tools/build-library.mjs"] for c in calls) == 2
        for index, (check, name, mutation, faults) in enumerate(mutations):
            target = scratch / f"copy-{index:03}-{check}"
            shutil.copytree(baseline, target)
            mutation(target)
            with external_mocks(target, faults):
                report = v.verify(target, (check,))
            caught = report["checks"][check]["pass"] is False
            records.append(
                {
                    "check": check,
                    "mutation": name,
                    "caught": caught,
                    "error": report["checks"][check].get("error", ""),
                }
            )
    return {
        "synthetic_only": True,
        "not_current_research_QA": True,
        "external_operations_mocked": [
            "HTTP receipts",
            "browser screenshots",
            "style detector response",
            "library commands",
            "Pandoc/PDF regeneration",
        ],
        "baseline_checks_passed": 12,
        "expected": len(mutations),
        "caught": sum(r["caught"] for r in records),
        "per_check": {
            key: sum(r["caught"] for r in records if r["check"] == key)
            for key in v.CHECK_IDS
        },
        "mutations": records,
        "executed_at": datetime.now(UTC).isoformat(),
    }


def main() -> int:
    """Run all synthetic probes and optionally freeze proven checker file hashes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_probes()
    root = MODULE.parent.parent
    output = args.output or root / "logs/checks-probes.json"
    v.write_json(output, report)
    passed = report["caught"] == report["expected"] == 96
    if args.freeze and passed:
        frozen = {
            "frozen_at": datetime.now(UTC).isoformat(),
            "synthetic_probes_caught": report["caught"],
            "per_check": report["per_check"],
            "files": {
                str(p.relative_to(root)): v.sha(p)
                for p in (MODULE, Path(__file__).resolve())
            },
            "probe_receipt": str(output.relative_to(root)),
            "probe_receipt_sha256": v.sha(output),
            "does_not_certify_current_deliverables": True,
        }
        previous = root / "logs/checks-frozen.json"
        if previous.exists():
            old = v.read_json(previous)
            if old.get("files") != frozen["files"]:
                changes = root / "logs/CHECK-CHANGES.md"
                v.require(
                    changes.is_file()
                    and all(
                        digest in changes.read_text()
                        for digest in list(old["files"].values())
                        + list(frozen["files"].values())
                    ),
                    "Checker changed after freeze: log old/new hashes and rationale before refreezing",
                )
        v.write_json(previous, frozen)
    print(
        json.dumps(
            {
                "synthetic_only": True,
                "caught": report["caught"],
                "expected": report["expected"],
                "per_check": report["per_check"],
                "receipt": str(output),
                "frozen": bool(args.freeze and passed),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
