"""Check a local writing-kit handoff without publishing its private materials."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

__all__ = ["check_coverage", "check_document", "numeric_tokens", "verify"]
NUMBER = re.compile(
    r"(?<![A-Za-z0-9])[−-]?\d+(?:,\d{3})*(?:\.\d+)?(?:th)?%?(?![A-Za-z0-9])"
)
LINK = re.compile(r"!?\[([^\]]+)\]\(([^\n]+?)\)")
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def numeric_tokens(line: str) -> list[str]:
    """Extract quantitative tokens while excluding URLs and code/source locators."""
    text = re.sub(r"`[^`]*`", "", line)
    text = LINK.sub(lambda match: match.group(1), text)
    text = re.sub(r"\b[A-Z]\d+(?:\.\d+)+\b", "", text)
    return NUMBER.findall(text)


def check_coverage(mapping: list[dict], claims: list[dict]) -> list[dict]:
    """Require one accepted source-bound CSV occurrence per visible numeric token."""
    available = Counter(
        (row["occurrence_file"], int(row["occurrence_line"]), row["display_token"])
        for row in claims
        if row.get("occurrence_line", "").isdigit()
        and row.get("status") in {"verified", "corrected"}
    )
    missing = []
    for row in mapping:
        for token in numeric_tokens(row["text"]):
            key = (row["source"], row["source_line"], token)
            if available[key]:
                available[key] -= 1
            else:
                missing.append(
                    {"line": row["line"], "source": key, "text": row["text"]}
                )
    return missing


def plain_markdown(markdown: str) -> str:
    """Normalize authored visible prose and table cells for OOXML parity."""
    result = []
    for line in markdown.splitlines():
        if re.fullmatch(r"\s*\|[\s|:−-]+\|\s*", line):
            continue
        line = re.sub(r"^#{1,6}\s+|^-\s+", "", line)
        line = LINK.sub(lambda match: match.group(1), line)
        line = line.replace("**", "").replace("`", "")
        line = line.strip().strip("|").replace("|", " ")
        result.append(line)
    return " ".join(" ".join(result).split())


def check_document(docx: Path, markdown: str) -> dict:
    """Compare DOCX body text, hyperlink counts and hidden-claim boundaries."""
    with ZipFile(docx) as archive:
        body = archive.read("word/document.xml")
        root = ET.fromstring(body)
        text = " ".join(
            "".join(paragraph.itertext()) for paragraph in root.findall(".//w:p", NS)
        )
        actual = " ".join(text.split())
        expected = plain_markdown(markdown)
        links = len(root.findall(".//w:hyperlink", NS))
        expected_links = len(re.findall(r"(?<!!)\[[^\]]+\]\([^\n]+?\)", markdown))
        return {
            "text_parity": actual == expected,
            "expected_characters": len(expected),
            "actual_characters": len(actual),
            "hyperlinks": links,
            "expected_hyperlinks": expected_links,
            "hyperlink_count_parity": links == expected_links,
            "tables": len(root.findall(".//w:tbl", NS)),
            "images": len(
                [name for name in archive.namelist() if name.startswith("word/media/")]
            ),
            "hidden_claim_ids_absent": not re.search(
                rb"WK-[CWPF]-|data-claim=|fbs_2023_", body
            ),
            "footnotes_absent": "word/footnotes.xml" not in archive.namelist(),
        }


def verify(handoff: Path) -> dict:
    """Validate assembled structure, source coverage, links and document parity."""
    failures = []
    kit = handoff / "kit"
    markdown = (kit / "WRITING-KIT.md").read_text()
    mapping = json.loads((handoff / "support/assembly-map.json").read_text())
    claims = list(csv.DictReader((kit / "claims-by-section.csv").open()))
    coverage = check_coverage(mapping["lines"], claims)
    if coverage:
        failures.append(f"{len(coverage)} unregistered numeric occurrences")
    numbers = re.findall(r"^## (\d+)\.", markdown, re.MULTILINE)
    if numbers != [str(number) for number in range(1, 12)]:
        failures.append("Numbered sections are not exactly one through eleven")
    if mapping["missing"]:
        failures.append("Missing assembly modules: " + ", ".join(mapping["missing"]))
    fields = [
        "Claim:",
        "Evidence:",
        "Caveat:",
        "Cross-reference:",
        "Figures or tables:",
        "AI draft, replace:",
    ]
    for block in re.split(r"(?m)^## ", markdown)[1:]:
        for field in fields:
            if field not in block:
                failures.append(f"Missing {field} in {block.splitlines()[0]}")
    link_checks = 0
    for _, url in LINK.findall(markdown):
        if url.startswith(("https://", "http://", "#")):
            continue
        target = kit / unquote(urlsplit(url.strip("<>")).path)
        link_checks += 1
        if not target.exists():
            failures.append("Missing local link " + url)
    messages = {}
    for file in sorted((handoff / "messages").glob("*.md")):
        count = len(file.read_text().split())
        messages[file.name] = count
        if count >= 200:
            failures.append("Message reaches word limit: " + file.name)
    for row in claims:
        if row["status"] not in {"verified", "corrected", "conflict", "unresolved"}:
            failures.append("Invalid claim status: " + row["claim_id"])
        if row["status"] in {"verified", "corrected"} and not row.get("local_source"):
            failures.append("Missing source binding: " + row["claim_id"])
    document = check_document(kit / "WRITING-KIT.docx", markdown)
    if not all(
        document[key]
        for key in [
            "text_parity",
            "hyperlink_count_parity",
            "hidden_claim_ids_absent",
            "footnotes_absent",
        ]
    ):
        failures.append("DOCX parity/boundary failure")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "sections": len(numbers),
        "claim_rows": len(claims),
        "numeric_occurrences": sum(
            len(numeric_tokens(row["text"])) for row in mapping["lines"]
        ),
        "unregistered_occurrences": coverage,
        "local_links": link_checks,
        "message_word_counts": messages,
        "document": document,
        "markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
        "docx_sha256": hashlib.sha256(
            (kit / "WRITING-KIT.docx").read_bytes()
        ).hexdigest(),
        "limits": "Source-bound agent checks; no human verification, current remote state, rights or joint acceptance inferred.",
    }


def main() -> None:
    """Run the explicit local handoff check and save its receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.handoff.resolve())
    (args.handoff / "verification/kit-check.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
