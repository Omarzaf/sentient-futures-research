"""Rebuild a scoped retail observation inventory offline from hashed captures."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from capture import parse_product

__all__ = ["build_inventory", "validate_capture"]


def _contained_file(data_dir: Path, relative: str) -> Path:
    """Reject manifest paths outside the explicitly named capture directory."""
    path = (data_dir / relative).resolve()
    if not path.is_relative_to(data_dir.resolve()):
        raise ValueError("Capture path escapes data directory")
    return path


def validate_capture(record: dict, data_dir: Path) -> dict:
    """Recheck original bytes and parse a source-bound observation without network."""
    raw_path = _contained_file(data_dir, record["raw_file"])
    body = raw_path.read_bytes()
    if hashlib.sha256(body).hexdigest() != record["raw_sha256"]:
        raise ValueError(f"Raw SHA mismatch: {record['capture_id']}")
    if len(body) != record["raw_bytes"]:
        raise ValueError(f"Raw size mismatch: {record['capture_id']}")
    header_path = _contained_file(data_dir, record["headers_file"])
    if hashlib.sha256(header_path.read_bytes()).hexdigest() != record["headers_sha256"]:
        raise ValueError(f"Header SHA mismatch: {record['capture_id']}")
    excluded = {
        "nutrition_text_candidates",
        "error",
        "price_evidence",
        "listed_price",
        "currency",
        "title",
        "availability_as_reported",
        "evidence_status",
    }
    result = {key: value for key, value in record.items() if key not in excluded}
    if record.get("retrieval_failed") or record["http_status"] != 200:
        result.update(evidence_status="HOLD_retrieval_failure", stock_status="unknown")
        return result
    parsed = parse_product(body.decode("utf-8", errors="replace"))
    result.update(
        {
            key: value
            for key, value in parsed.items()
            if key != "nutrition_text_candidates"
        }
    )
    expected_currency = {"India": "INR", "Pakistan": "PKR"}.get(record["country"])
    if parsed["currency"] != expected_currency:
        result["evidence_status"] = "HOLD_currency_mismatch"
    age = record.get("http_age")
    if age and (not str(age).isdigit() or int(age) > 0):
        result["evidence_status"] = "HOLD_cache_age"
    reported = str(parsed.get("availability_as_reported") or "").rsplit("/", 1)[-1]
    result["stock_status"] = {
        "InStock": "source_listed_in_stock",
        "OutOfStock": "source_listed_out_of_stock",
    }.get(reported, "unknown")
    result["delivery_availability_verified"] = False
    result["alternative_scope_status"] = (
        "traditional soy comparator; pillar eligibility pending product-positioning review"
        if record["category"] == "traditional_soy_comparator"
        else (
            "plant beverage; study pillar inclusion requires review"
            if record["category"] == "alternative_milk"
            else "category assigned in scoped capture plan; not market classification proof"
        )
    )
    return result


def build_inventory(data_dir: Path, output_dir: Path | None = None) -> dict:
    """Validate every capture, deduplicate source URLs, and write auditable counts."""
    output_dir = output_dir or data_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = data_dir / "capture-manifest.jsonl"
    records = [json.loads(line) for line in manifest.read_text().splitlines() if line]
    validated = [validate_capture(record, data_dir) for record in records]
    latest: dict[str, dict] = {}
    for record in sorted(validated, key=lambda value: value["capture_finished_utc"]):
        latest[record["url"]] = record
    observations = sorted(
        latest.values(),
        key=lambda value: (value["country"], value["category"], value["url"]),
    )
    coverage = {
        "scope": "Dated public outlet observations; not an exhaustive national product census",
        "capture_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "capture_count": len(records),
        "all_raw_and_header_hashes_verified": True,
        "deduplication": "Latest captured original URL; genuine package/cut/flavour variants retained",
        "country": {},
        "protein_price_calculation_status": "HOLD: official baseline gate and product protein bases unresolved; no calculation performed",
        "nutrition": "Protein values/bases remain null; navigation and marketing references do not establish nutrient content",
        "licence": "Publicly readable retail pages; redistribution rights unestablished; raw captures private",
        "limitations": [
            "Schema InStock means the source reported stock at capture; no postcode or fulfilment check was performed",
            "One functioning outlet per country is a convenience sample with correlated prices and package variants",
            "OutOfStock records remain evidence and are excluded from source-listed-in-stock counts",
            "Plant beverages include flavoured drinks; traditional tofu/chaap pillar eligibility remains pending product-positioning review",
            "No verification of production country, manufacturer identity, national sales, or all-country product availability",
            "Unverified search snippets and inaccessible listings are not price observations",
        ],
    }
    for country in sorted({record["country"] for record in observations}):
        rows = [record for record in observations if record["country"] == country]
        verified = [
            record
            for record in rows
            if record["evidence_status"] == "raw_listed_price_observation"
        ]
        in_stock = [
            record
            for record in verified
            if record["stock_status"] == "source_listed_in_stock"
        ]
        coverage["country"][country] = {
            "attempted_distinct_urls": len(rows),
            "verified_original_page_price_observations": len(verified),
            "source_listed_in_stock": len(in_stock),
            "source_listed_out_of_stock": sum(
                record["stock_status"] == "source_listed_out_of_stock"
                for record in verified
            ),
            "held_urls": len(rows) - len(verified),
            "in_stock_with_explicit_package_text": sum(
                bool(record.get("package_text_in_title")) for record in in_stock
            ),
            "verified_price_categories": dict(
                sorted(Counter(record["category"] for record in verified).items())
            ),
            "in_stock_categories": dict(
                sorted(Counter(record["category"] for record in in_stock).items())
            ),
            "outlets": sorted({record["retailer"] for record in verified}),
            "capture_started_utc": min(
                record["capture_started_utc"] for record in rows
            ),
            "capture_finished_utc": max(
                record["capture_finished_utc"] for record in rows
            ),
            "minimum_30_original_prices_met": len(verified) >= 30,
            "minimum_30_source_listed_in_stock_met": len(in_stock) >= 30,
            "protein_values_verified": sum(
                record.get("protein_value") is not None for record in verified
            ),
        }
    (output_dir / "observations.json").write_text(
        json.dumps(observations, indent=2, ensure_ascii=False) + "\n"
    )
    (output_dir / "coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False) + "\n"
    )
    columns = [
        "country",
        "retailer",
        "category",
        "title",
        "variant",
        "package_quantity_as_shown",
        "package_unit_as_shown",
        "listed_price",
        "currency",
        "availability_as_reported",
        "stock_status",
        "location_as_shown",
        "protein_value",
        "protein_basis",
        "url",
        "capture_finished_utc",
        "raw_sha256",
        "evidence_status",
    ]
    with (output_dir / "observations.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(observations)
    lines = [
        "# Scoped retail observations",
        "",
        coverage["scope"],
        "",
        "| Country | Original price observations | Source-listed InStock | OutOfStock | Held |",
        "|---|---:|---:|---:|---:|",
    ]
    for country, counts in coverage["country"].items():
        lines.append(
            f"| {country} | {counts['verified_original_page_price_observations']} | {counts['source_listed_in_stock']} | {counts['source_listed_out_of_stock']} | {counts['held_urls']} |"
        )
    lines += [
        "",
        coverage["protein_price_calculation_status"],
        "",
        *["- " + limitation for limitation in coverage["limitations"]],
        "",
        "Rebuild: activate the named task venv, then run `python research/protein-markets-2026/retail/build_inventory.py --data-dir <named retail folder>`. This command reads saved bytes only.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n")
    return coverage


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_inventory(args.data_dir, args.output_dir), indent=2))
