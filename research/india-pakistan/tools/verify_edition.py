"""Fail-closed, source-bound checks for the supervisor edition and full report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import posixpath
import re
import struct
import subprocess
import tempfile
import unicodedata
import zipfile
import zlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree

CHECK_IDS = tuple(f"C{i}" for i in range(1, 13))
TIERS = {"A", "B", "C", "D", "derived"}
REVIEW_IDS = (
    {f"H{i}" for i in range(1, 8)}
    | {f"M{i}" for i in range(8, 18)}
    | {f"L{i}" for i in range(1, 6)}
    | {f"Y{i}" for i in range(1, 5)}
    | {f"E{i}" for i in range(1, 4)}
)
DETECTOR = (
    Path.home() / ".claude" / "skills" / "avoid-ai-writing" / "detector" / "patterns.js"
)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
NATIVE_SPAN = re.compile(r"\[([^\]\n]*)\]\{([^}\n]*)\}")
ATTR = re.compile(r'([\w-]+)="([^"]*)"')
# Existing public discovery lineage, inspected on 14 October 2026. These exact
# immutable references never authorize new publication payloads in that directory.
CURATED_PUBLIC_REFERENCES = {
    "/".join(("research", "halal-cultivated", "arch" + "ive", name)): digest
    for name, digest in {
        "AGENTIC-PLAN.md": "e985190635e5411e657811f9df0a0b6f5f943bd61751a89f293fe281c8843d36",
        "PAPER-PLAN.md": "e75994f63da22b488d66c89a866d0d13713afaa3eb8baefeb20061bf9be8ee5c",
        "README.md": "8784b9193cf0cc7f1064442a30eaa6e141fd86e15140aa278520bd5b418ccc65",
        "discovery-pass/certification.csv": "8c0f4bb7adb315d6f69e35a2d230aa2c4e95f4b6c07689c781edc69358fe2648",
        "discovery-pass/claims.csv": "1f33d576fb8bd6415c0c2828304623178159ac2902a033f12e21185dddd8b152",
        "discovery-pass/consensus-matrix.csv": "2fbadbd71181c072cacd24f8e5bd3a56ab7f2740d0e3c0fbc1127256a4430382",
        "discovery-pass/elasticities.csv": "150c45c768b7c83867d472ab911aaabc74754a6b94452e9be11949c5c79b5298",
        "discovery-pass/feed-inputs.csv": "dab78dd99c3759430f842e07b8f2377824f979e18fa8cb41fce7697613e756bb",
        "discovery-pass/historical-parallels.csv": "0ef6987eb4ba50f177e82bbc38e0fac9873463796659ef527dedee3385322a4e",
        "discovery-pass/madhhab-geography.csv": "b0541aef11c3b6f061080912beeacbaa707e68d50b41ded992d3769f7bdf316f",
        "discovery-pass/market-records.csv": "f09769a781b88f83f7f43075ab987533ab45af56be183243350c1513405bf834",
        "discovery-pass/rulings.csv": "93c9bca93d15ff3b49d8d222fbcff55ab443fa18e3fadd2c76502ae467312de6",
        "discovery-pass/scenarios.csv": "2c841763d3c20c82aa8d848542fa11c90b60b5f2580ba6df05721c4bd334cad4",
        "discovery-pass/scripture-sources.csv": "374f77e3d4ff978e59a8d66a50580a12e741e97184aa0e800642d82e861fd1b4",
        "discovery-pass/source-register.json": "32175dc5ceb9436bbd5c35a5a16fa1ec3eba8fe892c220ab15db14cbbbb396bb",
    }.items()
}


class InvalidEvidence(ValueError):
    """A check found missing, inconsistent or inadmissible evidence."""


def require(condition: object, message: str) -> None:
    """Reject a false condition with an actionable validation message."""
    if not condition:
        raise InvalidEvidence(message)


def sha(path: Path) -> str:
    """Hash the exact bytes of a regular local evidence file."""
    require(path.is_file(), f"Missing evidence file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text: str) -> str:
    """Hash UTF-8 text without newline or whitespace normalization."""
    return hashlib.sha256(text.encode()).hexdigest()


def read_json(path: Path) -> Any:
    """Read strict JSON from an existing evidence file."""
    require(path.is_file(), f"Missing JSON evidence: {path}")
    return json.loads(path.read_text())


def write_json(path: Path, data: object) -> None:
    """Write a deterministic, human-readable evidence receipt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV with unique headers and no malformed row widths."""
    require(path.is_file(), f"Missing CSV: {path}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames, f"No CSV columns: {path}")
        require(
            len(set(reader.fieldnames)) == len(reader.fieldnames), "Duplicate columns"
        )
        result = list(reader)
    require(
        all(None not in row and None not in row.values() for row in result),
        "Malformed CSV",
    )
    return result


def parse_time(value: str) -> datetime:
    """Parse an explicit timezone-aware timestamp and convert it to UTC."""
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None, f"Timestamp has no timezone: {value}")
    return result.astimezone(UTC)


def run(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Execute a fixed verifier command without a shell, with a bounded timeout."""
    return subprocess.run(
        argv, cwd=cwd, text=True, capture_output=True, timeout=240, check=False
    )


def checked_run(argv: list[str], cwd: Path | None = None) -> str:
    """Execute a command and reject any nonzero exit status."""
    result = run(argv, cwd)
    require(result.returncode == 0, f"Command failed {argv}: {result.stderr[-1000:]}")
    return result.stdout


@dataclass
class Node:
    """Minimal DOM node retaining visible text and declared source bindings."""

    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)

    def find(self, predicate: Any) -> list[Node]:
        """Return this subtree's nodes matching a predicate in document order."""
        found = [self] if predicate(self) else []
        for child in self.children:
            if isinstance(child, Node):
                found.extend(child.find(predicate))
        return found

    def text(self, exclude: set[str] | None = None) -> str:
        """Read node text, optionally excluding named tags and their contents."""
        if self.tag in (exclude or set()):
            return ""
        return " ".join(
            c.text(exclude) if isinstance(c, Node) else c for c in self.children
        ).strip()


class Document(HTMLParser):
    """Parse generated HTML without executing JavaScript or fetching resources."""

    def __init__(self, text: str) -> None:
        """Construct a bounded tree from the supplied complete HTML string."""
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(text)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Append a node and track non-void element nesting."""
        require(len(dict(attrs)) == len(attrs), f"Duplicate HTML attributes: {tag}")
        node = Node(tag, {k: v or "" for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        """Close the corresponding open element without swallowing siblings."""
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data: str) -> None:
        """Preserve visible and embedded JSON character data."""
        self.stack[-1].children.append(data)


class Context:
    """Resolve current files and configuration within the local workspace."""

    def __init__(self, root: Path, skip_library: bool = False) -> None:
        """Load configuration; missing real inputs remain validation failures."""
        self.root = root.resolve()
        self.workspace = self.root.parent.parent
        self.skip_library = skip_library
        self.config = read_json(self.root / "verification-config.json")
        require(
            self.config.get("schema_version") == 1,
            "Configuration schema_version must be 1",
        )
        parse_time(self.config["as_of"])
        self.datasets = {d["id"]: d for d in self.config["datasets"]}
        require(
            self.datasets and len(self.datasets) == len(self.config["datasets"]),
            "Empty or duplicate dataset IDs",
        )

    def path(self, value: str) -> Path:
        """Resolve a local evidence path and reject workspace escapes."""
        path = (self.root / value).resolve()
        require(
            path.is_relative_to(self.workspace), f"Evidence escapes workspace: {value}"
        )
        return path

    def dataset(self, dataset_id: str) -> list[dict[str, str]]:
        """Load a configured CSV dataset by its stable public identifier."""
        require(dataset_id in self.datasets, f"Unknown dataset: {dataset_id}")
        data = rows(self.path(self.datasets[dataset_id]["path"]))
        require(data, f"Empty dataset: {dataset_id}")
        return data

    def claims(self) -> dict[str, dict[str, str]]:
        """Read unique nonempty claim IDs and the complete claim schema."""
        data = rows(self.root / "claims.csv")
        needed = {
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
        }
        require(
            data and needed.issubset(data[0]),
            "Missing claims or required claim columns",
        )
        result = {r["claim_id"]: r for r in data}
        require(
            len(result) == len(data) and "" not in result,
            "Duplicate or empty claim IDs",
        )
        return result

    def document(self) -> Node:
        """Read the actual current edition DOM."""
        path = self.root / "edition/index.html"
        require(path.is_file(), "Missing edition/index.html")
        return Document(path.read_text()).root

    def report(self) -> str:
        """Read the actual current report Markdown."""
        path = self.root / "report/REPORT.md"
        require(path.is_file(), "Missing report/REPORT.md")
        return path.read_text()

    def sources(self) -> dict[str, dict[str, str]]:
        """Read a nonempty source registry with unique identifiers and valid tiers."""
        data = rows(self.path(self.config["sources"]))
        require(data, "Empty source registry")
        result = {r["source_id"]: r for r in data}
        require(
            len(result) == len(data) and "" not in result,
            "Duplicate or blank source ID",
        )
        require(all(r["tier"] in TIERS for r in data), "Invalid or blank source tier")
        return result


def select(data: list[dict[str, str]], filters: object) -> list[dict[str, str]]:
    """Select rows using explicit string equality or membership only."""
    require(isinstance(filters, dict), "Filters must be a JSON object")
    for key, value in filters.items():
        require(all(key in r for r in data), f"Unknown filter column: {key}")
        require(
            isinstance(value, str)
            or (
                isinstance(value, dict)
                and set(value) == {"in"}
                and isinstance(value["in"], list)
                and value["in"]
                and all(isinstance(v, str) for v in value["in"])
            ),
            f"Invalid filter: {key}",
        )
    chosen = [
        r
        for r in data
        if all(
            r[k] == v if isinstance(v, str) else r[k] in v["in"]
            for k, v in filters.items()
        )
    ]
    require(chosen, "Filter selected no source rows")
    return chosen


def ids(value: str) -> list[str]:
    """Decode source IDs from a single ID, pipe list or JSON string array."""
    if not value:
        return []
    result = json.loads(value) if value.startswith("[") else re.split(r"[|;]", value)
    require(
        isinstance(result, list)
        and all(isinstance(v, str) and v.strip() == v and v for v in result),
        "Malformed source IDs",
    )
    require(len(set(result)) == len(result), "Duplicate source IDs")
    return result


def decimal(value: str) -> Decimal:
    """Parse a finite numeric source cell without inventing missing values."""
    require(value.strip() == value and value, "Blank or padded numeric value")
    result = Decimal(value)
    require(result.is_finite(), "Nonfinite numeric value")
    return result


def compute(ctx: Context, claim: dict[str, str]) -> str:
    """Recompute a claim deterministically from selected CSV cells."""
    selected = select(ctx.dataset(claim["dataset"]), json.loads(claim["filter_json"]))
    op = claim["operation"]
    require(
        op in {"value", "sum", "mean", "min", "max", "count", "distinct_count"},
        f"Unknown operation: {op}",
    )
    require(
        re.fullmatch(r"[0-8]", claim["rounding"]),
        "Rounding must be integer decimal places 0..8",
    )
    places = int(claim["rounding"])
    column = claim["value_column"]
    if op == "count":
        result = Decimal(len(selected))
    else:
        require(
            column and all(column in r for r in selected),
            f"Unknown value column: {column}",
        )
        if op == "distinct_count":
            require(all(r[column] for r in selected), "Missing distinct-count cell")
            result = Decimal(len({r[column] for r in selected}))
        else:
            values = [decimal(r[column]) for r in selected]
            if op == "value":
                require(len(values) == 1, "Value operation requires exactly one row")
                result = values[0]
            elif op == "sum":
                result = sum(values, Decimal(0))
            elif op == "mean":
                result = sum(values, Decimal(0)) / len(values)
            elif op == "min":
                result = min(values)
            else:
                result = max(values)
    require(
        bool(claim["locator"].strip()) and bool(claim["unit"].strip()),
        "Claim lacks locator or unit",
    )
    return format(
        result.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP),
        f".{places}f",
    )


def c1(ctx: Context) -> dict[str, object]:
    """C1: recompute every displayed claim without expression evaluation."""
    claims = ctx.claims()
    for key, claim in claims.items():
        actual = compute(ctx, claim)
        require(
            actual == claim["display"],
            f"{key}: displayed {claim['display']} != recomputed {actual}",
        )
    return {"claims_recomputed": len(claims)}


def allowed_number(kind: str, text: str) -> bool:
    """Validate a narrowly scoped structural number, date or year."""
    if kind == "year":
        return bool(
            re.fullmatch(
                r"(?:18|19|20|21)\d{2}(?:[–-](?:(?:18|19|20|21)\d{2}|\d{2}))?", text
            )
        )
    if kind == "date":
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%B %d, %Y"):
            try:
                datetime.strptime(text, fmt)
                return True
            except ValueError:
                continue
        return False
    if kind in {"chapter", "page"}:
        return text.isdigit() and 1 <= int(text) <= (15 if kind == "chapter" else 999)
    return False


def remove_urls(text: str) -> str:
    """Remove link destinations while preserving visible link labels."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return re.sub(r"https?://[^\s<>\]\)]+", "", text)


def verify_source_row(node: Node, sources: dict[str, dict[str, str]]) -> None:
    """Verify every visible source-ledger cell against its named source field."""
    source_id = node.attrs["data-source-id"]
    require(source_id in sources, f"Unknown visible ledger source: {source_id}")
    cells = node.find(lambda n: n.tag in {"td", "th"})
    require(cells, "Source ledger row has no cells")
    for cell in cells:
        col = cell.attrs.get("data-source-column", "")
        require(
            col in sources[source_id] and cell.text() == sources[source_id][col],
            f"Source ledger cell mismatch: {source_id}/{col}",
        )


def c2(ctx: Context) -> dict[str, object]:
    """C2: reject every unbound numeric token in reader-visible prose."""
    claims = ctx.claims()
    sources = ctx.sources()
    used: list[str] = []

    def binding(text: str, attrs: dict[str, str]) -> bool:
        if "data-claim-meta" in attrs:
            key = attrs["data-claim-meta"]
            field = attrs.get("data-claim-field", "")
            require(key in claims, f"Unknown claim metadata ID: {key}")
            if field in {"claim_id", "value_column"}:
                expected = claims[key][field]
            elif field.startswith("filter.") and field[7:]:
                filters = json.loads(claims[key]["filter_json"])
                column = field[7:]
                require(
                    isinstance(filters, dict) and column in filters,
                    f"Unknown claim metadata filter: {field}",
                )
                value = filters[column]
                require(
                    not isinstance(value, (list, dict)),
                    "Claim metadata filter must be scalar",
                )
                expected = (
                    value
                    if isinstance(value, str)
                    else json.dumps(value, allow_nan=False, separators=(",", ":"))
                )
            else:
                raise InvalidEvidence(f"Unsupported claim metadata field: {field}")
            require(
                text == expected, f"Claim metadata differs from ledger: {key}/{field}"
            )
            return True
        if "data-claim" in attrs:
            key = attrs["data-claim"]
            require(key in claims, f"Unknown prose claim: {key}")
            require(
                text == claims[key]["display"], f"Prose value differs from claim: {key}"
            )
            used.append(key)
            return True
        if "data-source-id" in attrs and "data-source-column" in attrs:
            source_id = attrs["data-source-id"]
            column = attrs["data-source-column"]
            require(
                source_id in sources and column in sources[source_id],
                "Unknown source-cell prose binding",
            )
            require(
                text == sources[source_id][column],
                "Source-cell prose differs from exact registry text",
            )
            return True
        if "data-number-kind" in attrs:
            require(
                allowed_number(attrs["data-number-kind"], text),
                f"Invalid number allowance: {text}",
            )
            return True
        return False

    def visible(node: Node) -> str:
        if node.tag in {"script", "style", "code", "pre"}:
            return ""
        if binding(node.text(), node.attrs):
            return ""
        if "data-chart-table" in node.attrs:
            verify_chart_table(ctx, node.attrs["data-chart-table"], node)
            return ""
        if "data-source-id" in node.attrs:
            verify_source_row(node, sources)
            return ""
        return " ".join(visible(c) if isinstance(c, Node) else c for c in node.children)

    edition = visible(ctx.document())
    report = re.sub(r"```.*?```", "", ctx.report(), flags=re.DOTALL)

    def span(match: re.Match[str]) -> str:
        attrs = dict(ATTR.findall(match[2]))
        return "" if binding(html.unescape(match[1]), attrs) else match[1]

    report = NATIVE_SPAN.sub(span, report)
    report = re.sub(
        r"\{[^}\n]*\}|^[ \t]*:::[ \t]*[^\n]*$|<[^>]+>", "", report, flags=re.MULTILINE
    )
    report = html.unescape(report)
    for name, text in (("edition", edition), ("report", report)):
        text = remove_urls(text)
        text = re.sub(r"\b(?:NFHS-5|BioE3|D3)\b", "", text)
        match = NUMBER.search(text)
        require(
            match is None,
            f"Untraced number in {name}: {text[max(0, match.start()-40):match.end()+40] if match else ''}",
        )
    require(used, "No reader-visible claim bindings")
    return {"claim_occurrences": len(used), "distinct_claims": len(set(used))}


def chart_specs(ctx: Context) -> dict[str, dict[str, Any]]:
    """Parse unique embedded chart JSON records from the current edition."""
    scripts = ctx.document().find(lambda n: "data-chart" in n.attrs)
    require(scripts, "No source-bound embedded chart data")
    specs: dict[str, dict[str, Any]] = {}
    for node in scripts:
        key = node.attrs["data-chart"]
        require(
            node.tag == "script" and node.attrs.get("type") == "application/json",
            "Chart data must be JSON script",
        )
        require(key and key not in specs, "Duplicate or blank chart ID")
        specs[key] = json.loads(node.text())
    return specs


def chart_rows(ctx: Context, spec: dict[str, Any]) -> list[dict[str, str]]:
    """Project a chart's exact source selection without lossy coercion."""
    columns = spec["columns"]
    require(
        isinstance(columns, list) and columns and len(set(columns)) == len(columns),
        "Invalid chart columns",
    )
    selected = select(ctx.dataset(spec["dataset"]), spec["filter"])
    require(
        all(all(c in row for c in columns) for row in selected), "Unknown chart column"
    )
    return [{c: row[c] for c in columns} for row in selected]


def verify_chart_table(ctx: Context, key: str, table: Node) -> None:
    """Require accessible table headings and cells to equal the chart's CSV rows."""
    specs = chart_specs(ctx)
    require(key in specs and table.tag == "table", "Unknown or non-table chart table")
    spec = specs[key]
    table_rows = table.find(lambda n: n.tag == "tr")
    actual = [
        [
            c.text()
            for c in row.children
            if isinstance(c, Node) and c.tag in {"td", "th"}
        ]
        for row in table_rows
    ]
    expected = [spec["columns"]] + [
        [r[c] for c in spec["columns"]] for r in chart_rows(ctx, spec)
    ]
    require(actual == expected, f"Accessible chart table differs: {key}")


def c3(ctx: Context) -> dict[str, object]:
    """C3: compare all embedded chart data and accessible tables with source rows."""
    specs = chart_specs(ctx)
    document = ctx.document()
    for key, spec in specs.items():
        require(
            spec["rows"] == chart_rows(ctx, spec),
            f"Chart JSON differs from source rows: {key}",
        )
        require(
            all(
                isinstance(spec.get(k), str) and spec[k].strip()
                for k in ("title", "unit", "caveat")
            ),
            f"Missing chart semantics: {key}",
        )
        require(
            isinstance(spec.get("source_ids"), list) and spec["source_ids"],
            "Chart lacks source IDs",
        )
        containers = document.find(
            lambda n, key=key: n.attrs.get("data-chart-container") == key
        )
        require(len(containers) == 1, f"Missing/duplicate chart container: {key}")
        container = containers[0]
        require(
            container.find(lambda n: n.tag in {"h2", "h3", "h4"} and bool(n.text())),
            f"Chart has no heading: {key}",
        )
        require(
            container.find(
                lambda n, key=key, spec=spec: n.attrs.get("data-chart-unit") == key
                and n.text() == spec["unit"]
            ),
            "Missing/mismatched unit line",
        )
        require(
            container.find(
                lambda n, key=key: n.attrs.get("data-chart-source") == key
                and bool(n.text())
            ),
            "Missing chart source line",
        )
        details = container.find(lambda n: n.tag == "details")
        tables = [
            t
            for d in details
            for t in d.find(lambda n, key=key: n.attrs.get("data-chart-table") == key)
        ]
        require(len(tables) == 1, f"Missing exact chart data toggle/table: {key}")
        verify_chart_table(ctx, key, tables[0])
    all_tables = document.find(lambda n: "data-chart-table" in n.attrs)
    require(len(all_tables) == len(specs), "Orphan/duplicate chart table")
    return {"charts_and_tables_checked": len(specs)}


def c4(ctx: Context) -> dict[str, object]:
    """C4: resolve every source and enforce derived/headline tier boundaries."""
    sources = ctx.sources()

    def resolve(values: list[str]) -> None:
        require(values, "Missing source identity")
        require(
            all(v in sources for v in values),
            f"Unresolved sources: {set(values) - set(sources)}",
        )

    total = 0
    for key, spec in ctx.datasets.items():
        columns = spec["source_columns"]
        require(isinstance(columns, list) and columns, f"No source columns: {key}")
        require(
            isinstance(spec.get("derived"), bool),
            "Dataset derived flag must be explicit boolean",
        )
        for row in ctx.dataset(key):
            require(row.get("tier") in TIERS, f"Blank/invalid row tier: {key}")
            require(all(c in row for c in columns), "Missing configured source column")
            joined = [v for c in columns for v in ids(row[c])]
            resolve(joined)
            extra = [
                v
                for c, val in row.items()
                if (c == "source_ids" or c.endswith("_source_id")) and c not in columns
                for v in ids(val)
            ]
            if extra:
                resolve(extra)
            if (
                spec["derived"]
                or row.get("flag", "").startswith("derived")
                or row.get("estimate_type", "").lower()
                in {
                    "derived",
                    "modelled",
                    "modeled",
                    "experimental",
                    "analyst_estimate",
                }
            ):
                require(
                    row["tier"] == "derived",
                    f"Derived dataset inherits source tier: {key}",
                )
            elif row["tier"] != "derived":
                require(
                    all(row["tier"] == sources[v]["tier"] for v in joined),
                    "Observation/source tier mismatch",
                )
            total += 1
    for key, claim in ctx.claims().items():
        joined = ids(claim["source_ids"])
        resolve(joined)
        require(
            claim["tier"] in TIERS and claim["headline"] in {"true", "false"},
            f"Invalid claim tier/headline: {key}",
        )
        selected = select(
            ctx.dataset(claim["dataset"]), json.loads(claim["filter_json"])
        )
        source_columns = ctx.datasets[claim["dataset"]]["source_columns"]
        actual_sources = {
            v for row in selected for col in source_columns for v in ids(row[col])
        }
        require(
            actual_sources.issubset(joined), f"Claim omits selected-row sources: {key}"
        )
        derived = (
            claim["operation"] != "value"
            or ctx.datasets[claim["dataset"]]["derived"]
            or any(r["tier"] == "derived" for r in selected)
        )
        require(
            not derived or claim["tier"] == "derived",
            f"Derived claim inherits input tier: {key}",
        )
        if not derived:
            require(
                all(claim["tier"] == r["tier"] for r in selected),
                "Claim/row tier mismatch",
            )
        if claim["headline"] == "true":
            require(
                claim["tier"] in {"A", "B"}
                and all(sources[v]["tier"] in {"A", "B"} for v in joined),
                f"Non-A/B headline: {key}",
            )
    for key, spec in chart_specs(ctx).items():
        resolve(spec["source_ids"])
        selected = select(ctx.dataset(spec["dataset"]), spec["filter"])
        require(
            {
                v
                for row in selected
                for col in ctx.datasets[spec["dataset"]]["source_columns"]
                for v in ids(row[col])
            }.issubset(spec["source_ids"]),
            f"Chart omits source identity: {key}",
        )
    return {"source_records": len(sources), "dataset_rows_joined": total}


def c5(ctx: Context) -> dict[str, object]:
    """C5: require all inventory packages and all approved chapters."""
    inventory = (ctx.root / "INVENTORY.md").read_text()
    package_lines = re.findall(r"^\| (P\d{2}) \| (.+)$", inventory, re.MULTILINE)
    packages = {key for key, _ in package_lines}
    edition_packages = {key for key, line in package_lines if "| E:" in line}
    require(
        len(package_lines) == 12 and packages == {f"P{i:02}" for i in range(1, 13)},
        "Inventory is incomplete/duplicated",
    )
    sections = ctx.document().find(lambda n: "data-chapter" in n.attrs)
    require(len(sections) == 15, "Edition must have exactly fifteen chapters")
    require(
        {n.attrs["data-chapter"] for n in sections} == {str(i) for i in range(1, 16)},
        "Missing/duplicate chapter numbers",
    )
    covered: set[str] = set()
    for node in sections:
        number = int(node.attrs["data-chapter"])
        require(
            node.tag == "section" and node.attrs.get("id") == f"chapter-{number:02}",
            "Invalid chapter anchor",
        )
        require(
            node.find(lambda n: n.tag in {"h1", "h2"} and bool(n.text())),
            "Chapter lacks heading",
        )
        require(
            len(node.text({"script", "style"}).split()) >= 20,
            "Chapter lacks substantive prose",
        )
        declared = set(node.attrs.get("data-packages", "").split())
        require(declared.issubset(packages), "Chapter names unknown inventory package")
        covered |= declared
    require(
        edition_packages.issubset(covered),
        f"Missing E packages: {edition_packages - covered}",
    )
    report_blocks = re.findall(
        r'::: \{data-package="(P\d{2})"\}\s*\n(.*?)\n:::', ctx.report(), re.DOTALL
    )
    report_packages = {key for key, text in report_blocks if len(text.split()) >= 20}
    require(
        packages.issubset(report_packages),
        f"Report omits/thins inventory packages: {packages-report_packages}",
    )
    spec = (ctx.root / "DESIGN-SPEC.md").read_text()
    require(
        {int(i) for i in re.findall(r"^\| (\d+)\s*\|", spec, re.MULTILINE)}
        == set(range(1, 16)),
        "Design specification chapter contract changed",
    )
    return {
        "inventory_packages": len(packages),
        "edition_packages": len(edition_packages),
        "chapters": len(sections),
    }


def c6(ctx: Context) -> dict[str, object]:
    """C6: require closed review findings backed by current existing evidence."""
    ledger = (ctx.root / "REVIEW-FIXES.md").read_text()
    entries = re.findall(
        r"^\| ([HMLYE]\d+) \| [^\n]*? \| (open|fixed|disclosed|declined) \| ([^\n]+)\|\s*$",
        ledger,
        re.MULTILINE,
    )
    require(
        {e[0] for e in entries} == REVIEW_IDS and len(entries) == len(REVIEW_IDS),
        "Missing/duplicate review finding",
    )
    evidence = read_json(ctx.root / "logs/checks-review-evidence.json")
    require(
        set(evidence) == REVIEW_IDS, "Evidence register does not cover exact review IDs"
    )
    for key, status, action in entries:
        require(status in {"fixed", "disclosed", "declined"}, f"Open finding: {key}")
        record = evidence[key]
        require(
            record["status"] == status
            and len(record["reason"].strip()) >= 10
            and len(action.strip()) >= 10,
            f"Missing/inconsistent closure rationale: {key}",
        )
        require(record["evidence"], f"No evidence for {key}")
        for item in record["evidence"]:
            require(
                sha(ctx.path(item["path"])) == item["sha256"],
                f"Stale review evidence: {key}",
            )
    return {"closed_findings": len(entries)}


def png_size(path: Path) -> tuple[int, int]:
    """Validate actual PNG chunk integrity, compressed pixels and dimensions."""
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path}")
    offset = 8
    pixels = bytearray()
    dimensions = None
    ended = False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        require(
            len(payload) == length and offset + 12 + length <= len(data),
            "Truncated PNG chunk",
        )
        crc = struct.unpack(">I", data[offset + 8 + length : offset + 12 + length])[0]
        require(zlib.crc32(chunk + payload) == crc, "Invalid PNG chunk CRC")
        if chunk == b"IHDR":
            require(dimensions is None and length == 13, "Invalid PNG IHDR")
            width, height, depth, color, compression, filtering, interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
            require(
                width > 0
                and height > 0
                and depth == 8
                and color in {2, 6}
                and compression == filtering == interlace == 0,
                "Unsupported screenshot PNG encoding",
            )
            dimensions = (width, height, 3 if color == 2 else 4)
        elif chunk == b"IDAT":
            pixels.extend(payload)
        elif chunk == b"IEND":
            ended = True
            require(offset + 12 == len(data), "Extra bytes after PNG end")
            break
        offset += length + 12
    require(dimensions and pixels and ended, "Incomplete PNG image")
    decoded = zlib.decompress(pixels)
    width, height, channels = dimensions
    require(
        len(decoded) == height * (width * channels + 1),
        "PNG decoded pixel length mismatch",
    )
    return width, height


def c7(ctx: Context) -> dict[str, object]:
    """C7: require hash-bound browser, accessibility, keyboard and print evidence."""
    receipt = read_json(ctx.root / "logs/checks-browser.json")
    require(
        receipt["html_sha256"] == sha(ctx.root / "edition/index.html"),
        "Stale browser HTML hash",
    )
    when = parse_time(receipt["executed_at"])
    require(when <= datetime.now(UTC) + timedelta(minutes=5), "Future browser QA")
    require(
        receipt["runner"] == "playwright"
        and re.search(r"\d+\.\d+", receipt["browser_version"])
        and receipt["command"],
        "Missing actual browser runner identity",
    )
    require(
        urlparse(receipt["url"]).hostname in {"127.0.0.1", "localhost", "::1"},
        "Browser evidence did not use localhost",
    )
    for node in ctx.document().find(
        lambda item: item.tag
        in {"script", "link", "img", "iframe", "video", "audio", "source"}
    ):
        resource = node.attrs.get("src", "") or (
            node.attrs.get("href", "") if node.tag == "link" else ""
        )
        if resource.startswith(("http://", "https://")):
            require(
                node.tag == "link"
                and urlparse(resource).hostname
                in {"fonts.googleapis.com", "fonts.gstatic.com"},
                "Edition requests an external resource other than permitted Google Fonts",
            )
    controls = ctx.document().find(
        lambda n: n.tag in {"button", "input", "select", "textarea", "summary"}
        or (n.tag == "a" and "href" in n.attrs)
    )
    control_ids = [n.attrs.get("id", "") for n in controls]
    require(
        control_ids
        and "" not in control_ids
        and len(set(control_ids)) == len(control_ids),
        "Every interactive control needs a unique ID",
    )
    runs = receipt["runs"]
    require(
        len(runs) == 4
        and {(r["width"], r["theme"]) for r in runs}
        == {(1440, "light"), (1440, "dark"), (390, "light"), (390, "dark")},
        "Missing browser viewport/theme coverage",
    )
    screenshots = 0
    for result in runs:
        require(
            result["height"] > 0 and result["document_width"] <= result["width"],
            "Horizontal overflow or invalid viewport",
        )
        require(result["console_errors"] == [], "Browser console errors")
        axe = result["axe"]
        require(
            axe["testEngine"]["name"] == "axe-core"
            and re.search(r"\d+\.\d+", axe["testEngine"]["version"])
            and isinstance(axe["violations"], list),
            "Missing real axe result metadata",
        )
        require(
            not any(
                v.get("impact") in {"critical", "serious"} for v in axe["violations"]
            ),
            "Serious/critical accessibility violation",
        )
        events = result["keyboard"]
        require(
            {
                e["control_id"]
                for e in events
                if e.get("focused") is True and e.get("key") in {"Tab", "Shift+Tab"}
            }
            == set(control_ids),
            "Keyboard coverage incomplete",
        )
        require(
            result["reduced_motion"] == {"requested": True, "active_animations": 0},
            "Reduced-motion evidence missing/failing",
        )
        shots = result["screenshots"]
        require(
            len(shots) == 15 and {s["chapter"] for s in shots} == set(range(1, 16)),
            "Missing/duplicate chapter screenshots",
        )
        for shot in shots:
            path = ctx.path(shot["path"])
            require(sha(path) == shot["sha256"], "Stale screenshot hash")
            width, height = png_size(path)
            require(
                width == result["width"] and height > 0, "Screenshot viewport mismatch"
            )
            screenshots += 1
    printed = receipt["print"]
    path = ctx.path(printed["path"])
    require(
        sha(path) == printed["sha256"] and path.read_bytes().startswith(b"%PDF-"),
        "Missing/stale printed PDF",
    )
    require(
        printed["pages"] >= 15 and printed["clipped_charts"] == [],
        "Print clipping or incomplete chapters",
    )
    info = checked_run(["pdfinfo", str(path)])
    count = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    require(
        count and int(count[1]) == printed["pages"],
        "Print receipt page count differs from actual PDF",
    )
    pages = printed["page_reviews"]
    require(
        {p["page"] for p in pages} == set(range(1, printed["pages"] + 1))
        and len(pages) == printed["pages"],
        "Missing print page review",
    )
    require(
        all(p["defects"] == [] and p.get("reviewed") is True for p in pages),
        "Print defects/unreviewed page",
    )
    return {
        "viewport_theme_runs": len(runs),
        "screenshots": screenshots,
        "controls": len(control_ids),
    }


def strip_prose(text: str, is_html: bool) -> str:
    """Strip code, tables and URLs as required by the local writing-style policy."""
    if is_html:
        root = Document(text).root
        text = root.text({"script", "style", "table", "pre", "code"})
    else:
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"^\s*\|.*\|\s*$", "", text, flags=re.MULTILINE)
        text = NATIVE_SPAN.sub(lambda m: m[1], text)
        text = re.sub(
            r"\{[^}\n]*\}|^[ \t]*:::[ \t]*[^\n]*$|<[^>]+>", "", text, flags=re.MULTILINE
        )
    return remove_urls(text)


def detector(text: str) -> dict[str, Any]:
    """Invoke the local MIT detector without copying it into public artifacts."""
    require(DETECTOR.is_file(), f"Local style detector unavailable: {DETECTOR}")
    command = [
        "node",
        "-e",
        "const fs=require('fs'); const d=require(process.argv[1]); process.stdout.write(JSON.stringify(d.analyzeText(fs.readFileSync(0,'utf8'))));",
        str(DETECTOR),
    ]
    result = subprocess.run(
        command, input=text, text=True, capture_output=True, timeout=60, check=False
    )
    require(result.returncode == 0, f"Style detector failed: {result.stderr}")
    return json.loads(result.stdout)


def issue_key(issue: dict[str, Any]) -> str:
    """Identify an exact detector finding including its current text position."""
    return text_sha(json.dumps(issue, sort_keys=True, separators=(",", ":")))


def c8(ctx: Context) -> dict[str, object]:
    """C8: enforce local detector and punctuation rules with scoped medium decisions."""
    files = ctx.config["prose_files"]
    authored = {
        str(p.relative_to(ctx.root))
        for folder in ("edition", "report")
        for p in (ctx.root / folder).rglob("*")
        if p.suffix.lower() in {".md", ".html"}
    }
    require(
        authored.issubset(files),
        f"Authored prose omitted from style lint: {authored - set(files)}",
    )
    require(
        isinstance(files, list)
        and {"edition/index.html", "report/REPORT.md"}.issubset(files)
        and len(set(files)) == len(files),
        "Prose list omits deliverables or has duplicates",
    )
    decisions_path = ctx.root / "logs/style-decisions.md"
    decisions: list[dict[str, str]] = []
    if decisions_path.is_file():
        blocks = re.findall(
            r"```json\s*(.*?)```", decisions_path.read_text(), re.DOTALL
        )
        require(len(blocks) == 1, "Style decisions require one JSON array block")
        decisions = json.loads(blocks[0])
    indexed = {(d["file"], d["issue_key"]): d for d in decisions}
    require(len(indexed) == len(decisions), "Duplicate style decision")
    used: set[tuple[str, str]] = set()
    details: list[dict[str, object]] = []
    for value in files:
        path = ctx.path(value)
        text = strip_prose(path.read_text(), path.suffix == ".html")
        require("—" not in text, f"Em dash in prose: {value}")
        dash_check = text
        for name in ("Pakistan–India", "India–Pakistan", "OECD–FAO"):
            dash_check = dash_check.replace(name, "")
        require(
            not re.search(r"(?<!\d)–|–(?!\d)", dash_check),
            f"Unpermitted en dash: {value}",
        )
        analysis = detector(text)
        require(isinstance(analysis.get("issues"), list), "Malformed detector response")
        for issue in analysis["issues"]:
            severity = issue.get("severity")
            require(
                severity not in {"high", "critical"},
                f"High style issue in {value}: {issue}",
            )
            if severity == "medium":
                key = (value, issue_key(issue))
                require(
                    key in indexed, f"Unreviewed medium issue {value}: {key[1]} {issue}"
                )
                choice = indexed[key]
                require(
                    choice["text_sha256"] == text_sha(text)
                    and choice["decision"] == "keep"
                    and len(choice["reason"].strip()) >= 12,
                    f"Stale/unreasoned medium decision: {key}",
                )
                used.add(key)
        details.append(
            {
                "file": value,
                "text_sha256": text_sha(text),
                "issues": [
                    {"issue_key": issue_key(i), **i} for i in analysis["issues"]
                ],
            }
        )
    require(used == set(indexed), "Orphan style decisions; remove or re-review")
    return {"files": details, "reviewed_medium_issues": len(used)}


def external_links(ctx: Context) -> set[str]:
    """Extract exact current public links and resource URLs without source-code noise."""
    result: set[str] = set()
    for node in ctx.document().find(lambda n: True):
        for attr in ("href", "src"):
            value = node.attrs.get(attr, "")
            if value.startswith(("https://", "http://")):
                result.add(value.split("#", 1)[0])
    report = ctx.report()
    for value in re.findall(r"https?://[^\s<>\]\)\"}]+", report):
        result.add(html.unescape(value).rstrip(".,;").split("#", 1)[0])
    return result


def c9(ctx: Context) -> dict[str, object]:
    """C9: bind successful recent HTTP checks to the exact current link set."""
    receipt = read_json(ctx.root / "logs/checks-links.json")
    require(
        receipt["html_sha256"] == sha(ctx.root / "edition/index.html")
        and receipt["report_sha256"] == sha(ctx.root / "report/REPORT.md"),
        "Stale link-check content hashes",
    )
    now = datetime.now(UTC)
    checked = parse_time(receipt["checked_at"])
    require(
        now - timedelta(days=7) <= checked <= now + timedelta(minutes=5),
        "Stale/future link check",
    )
    expected = external_links(ctx)
    require(expected, "No external source links")
    results = receipt["results"]
    require(
        len(results) == len(expected) and {r["url"] for r in results} == expected,
        "Missing/extra/duplicate checked links",
    )
    for result in results:
        require(
            type(result["status"]) is int and 200 <= result["status"] <= 399,
            f"Failed live link: {result['url']}",
        )
        require(
            result["method"] in {"GET", "HEAD"}
            and urlparse(result["final_url"]).scheme in {"http", "https"},
            "Invalid link-check method/final URL",
        )
        date = parse_time(result["checked_at"])
        require(
            now - timedelta(days=7) <= date <= now + timedelta(minutes=5)
            and abs((checked - date).total_seconds()) <= 86400,
            "Stale/inconsistent per-link date",
        )
    return {"live_links_checked": len(results), "checked_at": receipt["checked_at"]}


def docx_text(path: Path) -> str:
    """Extract Word document body and notes in XML reading order."""
    with zipfile.ZipFile(path) as archive:
        require("word/document.xml" in archive.namelist(), "Invalid DOCX")
        parts = ["word/document.xml"] + [
            p
            for p in ("word/footnotes.xml", "word/endnotes.xml")
            if p in archive.namelist()
        ]
        return " ".join(
            " ".join(
                node.text or ""
                for node in ElementTree.fromstring(archive.read(part)).iter()
                if node.tag.endswith("}t")
            )
            for part in parts
        )


def artifact_text(path: Path) -> str:
    """Read publication text, opening compressed documents rather than skipping them."""
    if path.suffix.lower() == ".docx":
        return docx_text(path)
    if path.suffix.lower() == ".pdf":
        require(path.read_bytes().startswith(b"%PDF-"), "Invalid PDF signature")
        return checked_run(["pdftotext", "-layout", str(path), "-"])
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".woff", ".woff2", ".ico"}:
        return ""
    return path.read_text(encoding="utf-8")


def report_pdf_text(ctx: Context, path: Path) -> str:
    """Validate and remove only the exact final page-number footer on every PDF page."""
    text = artifact_text(path)
    numbered = ctx.config["exports"].get("page_numbers", False)
    require(isinstance(numbered, bool), "exports.page_numbers must be a boolean")
    if not numbered:
        return text
    info = checked_run(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    require(match and int(match[1]) > 0, "No actual numbered PDF page count")
    total = int(match[1])
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    require(
        len(pages) == total, "Numbered PDF extraction page count differs from pdfinfo"
    )
    body = []
    for number, page in enumerate(pages, 1):
        lines = page.splitlines()
        nonempty = [index for index, line in enumerate(lines) if line.strip()]
        require(nonempty, f"Numbered PDF page {number} has no footer")
        last = nonempty[-1]
        require(
            lines[last].strip() == f"Page {number} of {total}",
            f"Numbered PDF page {number} lacks its exact final footer",
        )
        body.append("\n".join(lines[:last] + lines[last + 1 :]))
    return "\f".join(body)


def mask_curated_public_references(content: str, root: Path, document: Path) -> str:
    """Classify only exact hash-pinned public lineage references, preserving all else."""
    require(
        not document.is_absolute() and ".." not in document.parts,
        "Unsafe document path for curated references",
    )
    for reference, expected_sha in CURATED_PUBLIC_REFERENCES.items():
        relative_link = posixpath.relpath(reference, document.parent.as_posix())
        alternatives = sorted({reference, relative_link}, key=len, reverse=True)
        pattern = re.compile(
            r"(?<![\w./:\\-])(?:"
            + "|".join(re.escape(value) for value in alternatives)
            + r")(?=$|[\s\"'`<>),;\]}#])"
        )
        if not pattern.search(content):
            continue
        target = root / reference
        require(
            not target.is_symlink()
            and (root / document.parent / relative_link).resolve() == target.resolve()
            and target.resolve().is_relative_to(root.resolve())
            and sha(target) == expected_sha,
            f"Changed or unsafe curated public reference: {reference}",
        )
        content = pattern.sub(
            lambda match: match[0].replace("/" + "arch" + "ive/", "/public-history/"),
            content,
        )
    return content


def c10(ctx: Context) -> dict[str, object]:
    """C10: inspect exact publication bytes and Git-staged paths against a rights allowlist."""
    root = ctx.path(ctx.config["publication_root"])
    manifest = read_json(ctx.path(ctx.config["publication_allowlist"]))
    files = manifest["files"]
    require(
        files and len({f["path"] for f in files}) == len(files),
        "Empty/duplicate publication allowlist",
    )
    forbidden_path = re.compile(
        r"(?:^|/)(?:RECOVERY|ARCHIVE|staging|raw|\.env(?:\.[^/]*)?)(?:/|$)|status-review-2026-10-13|Updated Report|Meeting"
        + r" Prep|Project Incubator"
        + r" Application|SF incubator|Sentient Futures Mentees",
        re.IGNORECASE,
    )
    private_text = re.compile(
        "|".join(
            [
                r"/" + r"Users/[^\s\"<>]+",
                r"/" + r"home/[^\s\"<>]+",
                r"(?<![\w.-])" + "RECOVERY" + "/",
                r"(?<![\w.-])" + "ARCHIVE" + "/",
                r"status-review-2026-10-13\.md",
                r"Updated Report\.md",
                "Meeting" + " Prep",
                "Project Incubator" + " Application",
                "SF incubator" + "/",
                "Sentient Futures Mentees" + " 2026/",
                r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                r"(?:app\.slack\.com|slack\.com/archives|mail\.google\.com)",
                r"(?:API_KEY|API_SECRET|GMAIL_TOKEN|DRIVE_API_KEY|PASSWORD)\s*[:=]",
                r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,})\b",
                r"\b(?:"
                + "|".join(
                    "_".join(parts)
                    for parts in (
                        ("full", "text"),
                        ("article", "text"),
                        ("body", "text"),
                        ("raw", "article", "body"),
                    )
                )
                + r")\b",
            ]
        ),
        re.IGNORECASE,
    )
    for item in files:
        value = item["path"]
        relative = Path(value)
        require(
            not relative.is_absolute()
            and ".." not in relative.parts
            and not forbidden_path.search(value),
            f"Private/unsafe publication path: {value}",
        )
        path = (root / relative).resolve()
        require(
            path.is_relative_to(root.resolve()),
            f"Publication symlink escapes root: {value}",
        )
        require(
            sha(path) == item["sha256"],
            f"Publication bytes differ from allowlist: {value}",
        )
        require(
            isinstance(item["license"], str)
            and item["license"].strip()
            and not re.search(
                r"unknown|unclear|pending|unreviewed", item["license"], re.IGNORECASE
            ),
            f"Unreviewed rights: {value}",
        )
        content = artifact_text(path)

        # Public journal/government URL components are not local archive paths.
        # Keep every other rule active, including emails and private filenames
        # inside the same URL. Neither local hosts nor file URLs qualify.
        def public_url(match: re.Match[str]) -> str:
            """Mask only the generic archive component of a public HTTP URL."""
            value = match[0]
            parsed = urlparse(value)
            host = parsed.hostname or ""
            if (
                parsed.username is None
                and re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}", host)
                and not host.endswith((".local", ".internal", ".localhost"))
            ):
                return re.sub(
                    "(?<=/)" + "arch" + "ive/",
                    "public-history/",
                    value,
                    flags=re.IGNORECASE,
                )
            return value

        scanned = mask_curated_public_references(content, root, relative)
        scanned = re.sub(r'https?://[^\s<>"\[\]]+', public_url, scanned)
        match = private_text.search(scanned)
        require(
            match is None,
            f"Private/copyright-risk content in {value}: {match[0] if match else ''}",
        )
    git = run(["git", "-C", str(root), "rev-parse", "--show-toplevel"])
    require(
        git.returncode == 0 and Path(git.stdout.strip()).resolve() == root.resolve(),
        "Publication root is not its own Git checkout",
    )
    staged = checked_run(
        ["git", "-C", str(root), "diff", "--cached", "--name-only", "-z"]
    ).split("\0")
    staged_paths = {p for p in staged if p}
    require(
        staged_paths.issubset({f["path"] for f in files}),
        f"Unallowlisted staged paths: {staged_paths - {f['path'] for f in files}}",
    )
    return {
        "allowlisted_files_scanned": len(files),
        "staged_files_scanned": len(staged_paths),
    }


def tree_hashes(root: Path) -> dict[str, str]:
    """Hash the real Git source tree including untracked, nonignored files."""
    names = checked_run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ]
    ).split("\0")
    return {
        name: sha(root / name)
        for name in sorted(set(names))
        if name and (root / name).is_file()
    }


def c11(ctx: Context) -> dict[str, object]:
    """C11: run actual library checks and prove a repeat build introduces no byte drift."""
    require(
        not ctx.skip_library,
        "C11 skipped: diagnostic execution cannot pass final verification",
    )
    root = ctx.path(ctx.config["library_root"])
    require(root.is_dir(), "Library checkout absent")
    head = checked_run(["git", "-C", str(root), "rev-parse", "HEAD"]).strip()
    require(
        re.fullmatch(r"[a-f0-9]{40}", head),
        "Library HEAD is not an actual Git revision",
    )
    required = {
        "test-halal-checks.mjs",
        "test-phase1-checks.mjs",
        "test-paper-checks.mjs",
        "test-survey-checks.mjs",
    }
    suites = sorted((root / "tools").glob("test-*-checks.mjs"))
    require(
        required.issubset({p.name for p in suites}),
        "Required library test suite absent",
    )
    commands = (
        [["node", "tools/build-library.mjs"], ["node", "tools/verify.mjs"]]
        + [["node", str(p.relative_to(root))] for p in suites]
        + [["node", "tools/test-fetch-citations.mjs"]]
    )
    for command in commands:
        require(
            (root / command[1]).is_file(),
            f"Required library command absent: {command[1]}",
        )
    before = tree_hashes(root)
    log_dir = ctx.root / "logs/checks-library"
    log_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for index, command in enumerate(commands):
        result = run(command, root)
        log = log_dir / f"{index:02}-{Path(command[1]).stem}.txt"
        log.write_text(result.stdout + "\n" + result.stderr)
        records.append(
            {
                "command": command,
                "exit_code": result.returncode,
                "log": str(log.relative_to(ctx.root)),
                "sha256": sha(log),
            }
        )
        require(
            result.returncode == 0,
            f"Library command failed: {' '.join(command)}; see {log}",
        )
    after_first = tree_hashes(root)
    rebuild = run(["node", "tools/build-library.mjs"], root)
    log = log_dir / "rebuild.txt"
    log.write_text(rebuild.stdout + "\n" + rebuild.stderr)
    require(rebuild.returncode == 0, "Library repeat build failed")
    after_second = tree_hashes(root)
    require(
        after_first == after_second,
        "Library repeat build changed source/generated bytes",
    )
    require(
        checked_run(["git", "-C", str(root), "rev-parse", "HEAD"]).strip() == head,
        "Library HEAD changed during verification",
    )
    receipt = {
        "executed_at": datetime.now(UTC).isoformat(),
        "head": head,
        "source_before": before,
        "source_after": after_second,
        "commands": records,
        "rebuild": {
            "command": ["node", "tools/build-library.mjs"],
            "exit_code": rebuild.returncode,
            "log": str(log.relative_to(ctx.root)),
            "sha256": sha(log),
        },
        "no_drift": True,
    }
    write_json(ctx.root / "logs/checks-library.json", receipt)
    return {
        "head": head,
        "commands_executed": len(commands) + 1,
        "receipt": "logs/checks-library.json",
    }


def normalized_text(text: str) -> str:
    """Normalize whitespace, soft hyphens and typography ligatures only."""
    text = text.replace("\u00ad", "")
    for original, replacement in {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
    }.items():
        text = text.replace(original, replacement)
    text = " ".join(unicodedata.normalize("NFC", text).split())
    text = re.sub(r"\s+([,.;:!?\)\]])", r"\1", text)
    return re.sub(r"([\(\[])\s+", r"\1", text)


def ast_text(value: object) -> str:
    """Read authored Pandoc AST words while excluding layout metadata and attributes."""
    if isinstance(value, list):
        return " ".join(ast_text(item) for item in value)
    if not isinstance(value, dict):
        return ""
    kind = value.get("t")
    content = value.get("c")
    if kind == "Str":
        return str(content)
    if kind in {"Space", "SoftBreak", "LineBreak"}:
        return " "
    if kind in {"Code", "Math"}:
        return str(content[-1])
    if kind in {"RawInline", "RawBlock"}:
        return ""
    if kind in {"Link", "Image", "Span"}:
        return ast_text(content[1])
    if kind == "Header":
        return ast_text(content[2])
    if kind in {"Div", "CodeBlock"}:
        return ast_text(content[1]) if kind == "Div" else str(content[1])
    if kind is not None:
        return ast_text(content)
    if "blocks" in value:
        meta = value.get("meta", {})
        return (
            " ".join(
                ast_text(meta.get(key, {}))
                for key in ("title", "subtitle", "author", "date")
            )
            + " "
            + ast_text(value["blocks"])
        )
    return " ".join(ast_text(item) for item in value.values())


def ast_has_note(value: object) -> bool:
    """Detect footnotes before claiming exact body-order export text parity."""
    if isinstance(value, list):
        return any(ast_has_note(item) for item in value)
    if isinstance(value, dict):
        return value.get("t") == "Note" or any(
            ast_has_note(item) for item in value.values()
        )
    return False


def export_files(ctx: Context, scratch: Path) -> tuple[Path, Path, str]:
    """Regenerate exports and authored-text AST from the same current Markdown."""
    config = ctx.config["exports"]
    engine = config["pdf_engine"]
    numbered = config.get("page_numbers", False)
    require(isinstance(numbered, bool), "exports.page_numbers must be a boolean")
    require(
        not numbered or engine == "chromium",
        "Numbered report export requires the fixed Chromium footer",
    )
    require(
        engine in {"chromium", "xelatex", "lualatex", "pdflatex", "tectonic"},
        "Unapproved PDF engine",
    )
    source = ctx.root / "report/REPORT.md"
    base = [
        "pandoc",
        str(source),
        "--from=markdown+bracketed_spans+fenced_divs",
        "--standalone",
        "--wrap=none",
    ]
    if config.get("resource_path"):
        base += ["--resource-path", str(ctx.path(config["resource_path"]))]
    docx = scratch / "report.docx"
    pdf = scratch / "report.pdf"
    word = base + ["--output", str(docx)]
    if config.get("reference_doc"):
        reference = config["reference_doc"]
        require(
            sha(ctx.path(reference["path"])) == reference["sha256"],
            "Reference DOCX hash differs",
        )
        word += ["--reference-doc", str(ctx.path(reference["path"]))]
    checked_run(word)
    if engine == "chromium":
        module = Path(config["playwright_module"]).resolve()
        require(
            (module / "package.json").is_file(), "Installed Playwright module missing"
        )
        require(
            read_json(module / "package.json")["name"]
            in {"playwright", "playwright-core"},
            "Not a Playwright module",
        )
        browser = Path(config["chromium_executable"]).resolve()
        require(browser.is_file(), "Installed Chromium executable missing")
        html_path = scratch / "report.html"
        html_command = base + ["--to=html5", "--output", str(html_path)]
        if config.get("css"):
            css = config["css"]
            require(
                sha(ctx.path(css["path"])) == css["sha256"], "Export CSS hash differs"
            )
            html_command += ["--css", ctx.path(css["path"]).as_uri()]
        checked_run(html_command)
        script = """const {chromium}=require(process.argv[1]); const {pathToFileURL}=require('url');
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.argv[2]});
try {const page=await browser.newPage(); await page.route(/^https?:/,r=>r.abort());
await page.goto(pathToFileURL(process.argv[3]).href,{waitUntil:'load'});
await page.emulateMedia({media:'print',reducedMotion:'reduce'});
await page.addStyleTag({content:'ol,ul{list-style:none}'});
await page.evaluate(()=>document.fonts.ready);
const numbered=process.argv[5]==='true';
const footer='<div style="font-size:9px;width:100%;text-align:center;color:#555">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>';
await page.pdf({path:process.argv[4],format:'A4',printBackground:true,displayHeaderFooter:numbered,headerTemplate:'<span></span>',footerTemplate:numbered?footer:'',preferCSSPageSize:true,...(numbered?{margin:{bottom:'18mm'}}:{})});
} finally {await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});"""
        checked_run(
            [
                "node",
                "-e",
                script,
                str(module),
                str(browser),
                str(html_path),
                str(pdf),
                json.dumps(numbered),
            ]
        )
    else:
        checked_run(base + ["--pdf-engine", engine, "--output", str(pdf)])
    ast = json.loads(checked_run(base + ["--to=json"]))
    require(
        not ast_has_note(ast),
        "Automatic footnote layout is unsupported by exact-order export parity; use inline source hyperlinks and the source-ledger appendix",
    )
    authored = ast_text(ast)
    return pdf, docx, authored


def c12(ctx: Context) -> dict[str, object]:
    """C12: actually regenerate exports, compare text, and require current page review."""
    existing_pdf = ctx.root / "report/report.pdf"
    existing_docx = ctx.root / "report/report.docx"
    require(
        existing_pdf.is_file() and existing_pdf.read_bytes().startswith(b"%PDF-"),
        "Missing/invalid report PDF",
    )
    require(
        existing_docx.is_file() and zipfile.is_zipfile(existing_docx),
        "Missing/invalid report DOCX",
    )
    with tempfile.TemporaryDirectory(prefix="supervisor-export-check-") as temporary:
        generated_pdf, generated_docx, plain = export_files(ctx, Path(temporary))
        require(
            generated_pdf.is_file() and generated_docx.is_file(),
            "Exporter produced no artifacts",
        )
        expected = normalized_text(plain)
        require(
            expected and any(c.isalpha() for c in expected), "Markdown render is empty"
        )
        values = {
            "existing_pdf": report_pdf_text(ctx, existing_pdf),
            "existing_docx": docx_text(existing_docx),
            "regenerated_pdf": report_pdf_text(ctx, generated_pdf),
            "regenerated_docx": docx_text(generated_docx),
        }
        for name, text in values.items():
            require(
                normalized_text(text) == expected,
                f"Report text differs from Markdown rendering: {name}",
            )
    info = checked_run(["pdfinfo", str(existing_pdf)])
    match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    require(match and int(match[1]) > 0, "No actual PDF page count")
    pages = int(match[1])
    review = read_json(ctx.root / "logs/checks-report-pages.json")
    require(
        review["pdf_sha256"] == sha(existing_pdf)
        and review["md_sha256"] == sha(ctx.root / "report/REPORT.md"),
        "Stale report visual review",
    )
    parse_time(review["reviewed_at"])
    records = review["pages"]
    require(
        len(records) == pages
        and {p["page"] for p in records} == set(range(1, pages + 1)),
        "Incomplete PDF page review",
    )
    for record in records:
        require(
            record["defects"] == [] and record["reviewed"] is True,
            "Unfixed/unreviewed report page",
        )
        screenshot = ctx.path(record["path"])
        require(sha(screenshot) == record["sha256"], "Stale PDF page image")
        png_size(screenshot)
    return {
        "text_parity": "exact_after_documented_whitespace_normalization",
        "pages_reviewed": pages,
        "markdown_sha256": sha(ctx.root / "report/REPORT.md"),
        "pdf_sha256": sha(existing_pdf),
        "docx_sha256": sha(existing_docx),
    }


CHECKS = {
    f"C{i}": fn
    for i, fn in enumerate((c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12), 1)
}


def verify(
    root: Path, selected: tuple[str, ...] = CHECK_IDS, skip_library: bool = False
) -> dict[str, object]:
    """Run independent checks, retaining all failures rather than stopping at the first."""
    results: dict[str, object] = {}
    try:
        ctx = Context(root, skip_library)
    except (InvalidEvidence, OSError, ValueError, KeyError, TypeError) as error:
        return {
            "all_pass": False,
            "checks": {
                key: {"pass": False, "error": f"Configuration: {error}"}
                for key in selected
            },
        }
    for key in selected:
        try:
            results[key] = {"pass": True, "evidence": CHECKS[key](ctx)}
        except (
            InvalidEvidence,
            OSError,
            ValueError,
            KeyError,
            TypeError,
            InvalidOperation,
            subprocess.SubprocessError,
            zipfile.BadZipFile,
            ElementTree.ParseError,
            zlib.error,
            struct.error,
        ) as error:
            results[key] = {"pass": False, "error": str(error)}
    return {
        "all_pass": all(value["pass"] for value in results.values()),
        "checks": results,
    }


def final_gates(root: Path) -> list[str]:
    """Require frozen checks, clean fresh review and a fully evidenced handover."""
    failures: list[str] = []
    try:
        frozen = read_json(root / "logs/checks-frozen.json")
        require(
            frozen["synthetic_probes_caught"] >= 96,
            "Fewer than 96 corruption probes caught",
        )
        require(
            frozen["per_check"] == {key: 8 for key in CHECK_IDS},
            "Frozen proof does not cover eight corruptions per check",
        )
        probe_path = (root / frozen["probe_receipt"]).resolve()
        require(
            probe_path.is_relative_to(root.resolve())
            and sha(probe_path) == frozen["probe_receipt_sha256"],
            "Frozen probe receipt hash drift",
        )
        proof = read_json(probe_path)
        require(
            proof["synthetic_only"] is True
            and proof["caught"] == proof["expected"] == 96
            and proof["per_check"] == frozen["per_check"],
            "Invalid frozen corruption proof",
        )
        for name in ("tools/verify_edition.py", "tools/probes.py"):
            require(
                frozen["files"][name] == sha(root / name),
                f"Frozen checker hash drift: {name}; log rationale and rerun all probes",
            )
        review = read_json(root / "reviews/final-review.json")
        require(
            review["fresh_context"] is True
            and 1 <= review["round"] <= 3
            and review["high"] == 0
            and review["medium"] == 0,
            "No clean fresh-context review",
        )
        require(
            len(review["traces"]) == 25
            and len({t["claim_id"] for t in review["traces"]}) == 25
            and all(
                t["match"] is True and t["source_locator"] for t in review["traces"]
            ),
            "Fresh review lacks 25 distinct successful number traces",
        )
        require(
            review["html_sha256"] == sha(root / "edition/index.html")
            and review["report_sha256"] == sha(root / "report/REPORT.md"),
            "Fresh review does not match current deliverables",
        )
        require(
            sha(root / f"reviews/round-{review['round']}.md")
            == review["review_sha256"],
            "Missing/stale fresh-review narrative",
        )
        handover = (root / "READY-TO-SEND.md").read_text()
        require(
            re.search(r"\[[xX]\]", handover) and not re.search(r"\[ \]", handover),
            "Handover checklist is incomplete",
        )
        rows_checked = [
            line for line in handover.splitlines() if re.search(r"\[[xX]\]", line)
        ]
        for line in rows_checked:
            links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", line)
            require(
                links
                and any(
                    (root / link.split("#")[0]).is_file()
                    for link in links
                    if not link.startswith("http")
                ),
                "Handover row lacks local evidence link",
            )
    except (InvalidEvidence, OSError, ValueError, KeyError, TypeError) as error:
        failures.append(str(error))
    return failures


def main() -> int:
    """Expose diagnostic and final verification without a bypass-success mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parent.parent
    )
    parser.add_argument("--only", help="Diagnostic comma-separated check IDs")
    parser.add_argument(
        "--skip-library",
        action="store_true",
        help="Report C11 as failed without executing its commands",
    )
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(
        not (args.final and (args.only or args.skip_library)),
        "Final mode cannot omit checks",
    )
    selected = tuple(args.only.split(",")) if args.only else CHECK_IDS
    require(
        set(selected).issubset(CHECK_IDS) and selected,
        "Unknown or empty check selection",
    )
    report = verify(args.root.resolve(), selected, args.skip_library)
    report["scope"] = "diagnostic" if args.only or args.skip_library else "all_checks"
    report["verified_at"] = datetime.now(UTC).isoformat()
    if args.final:
        report["final_gate_failures"] = final_gates(args.root.resolve())
        report["all_pass"] = report["all_pass"] and not report["final_gate_failures"]
    if args.output:
        write_json(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
