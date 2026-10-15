"""Check staged joins, raw integrity and decision-critical evidence boundaries."""

from __future__ import annotations

import json
from datetime import datetime

from build_staged import HERE, RAW, ROOT, digest, rows


def require(condition: bool, message: str) -> None:
    """Raise a useful error when an evidence-integrity condition fails."""
    if not condition:
        raise ValueError(message)


def main() -> None:
    """Validate the local batch without writing shared dashboard files."""
    source_rows = rows(HERE / "source_rows.csv")
    sources = rows(ROOT / "data/processed/sources.csv") + source_rows
    source_ids = {row["source_id"] for row in sources}
    require(
        len({row["source_id"] for row in source_rows}) == len(source_rows),
        "Duplicate new source IDs",
    )
    tables = {
        name: rows(HERE / f"{name}.csv")
        for name in (
            "policy_rows",
            "company_rows",
            "company_exclusions",
            "retail_listing_rows",
        )
    }
    bindings = 0
    for name, records in tables.items():
        for record in records:
            for column, value in record.items():
                if column.endswith(("source_id", "source_ids")):
                    for source_id in filter(None, value.split(";")):
                        require(
                            source_id in source_ids,
                            f"Unresolved {name}.{column}: {source_id}",
                        )
            if record.get("raw_file"):
                path = ROOT / record["raw_file"]
                require(
                    path.is_file() and digest(path) == record["raw_sha256"],
                    f"Broken binding: {path}",
                )
                bindings += 1
    manifest = rows(HERE / "manifest_rows.csv")
    manifest_paths = {row["file"] for row in manifest}
    require(
        manifest_paths
        == {str(path.relative_to(ROOT)) for path in RAW.iterdir() if path.is_file()},
        "Raw manifest coverage mismatch",
    )
    for record in manifest:
        path = ROOT / record["file"]
        require(digest(path) == record["sha256"], f"Raw digest mismatch: {path}")
        require(record["source_id"] in source_ids, f"Unregistered raw source: {path}")
        stamp = datetime.fromisoformat(record["accessed_utc"])
        require(
            stamp.tzinfo is not None and stamp.utcoffset() is not None,
            f"Missing retrieval timezone: {path}",
        )
    fetches = [
        json.loads(line) for line in (HERE / "fetch-log.jsonl").read_text().splitlines()
    ]
    for receipt in fetches:
        require(
            digest(RAW / receipt["file"]) == receipt["sha256"],
            f"Fetch receipt drift: {receipt['file']}",
        )
        require(
            receipt["http_status"] == "200" and receipt["curl_exit"] == 0,
            f"Unsuccessful request retained: {receipt['file']}",
        )
    companies = {row["company"]: row for row in tables["company_rows"]}
    require(companies["Phyx44"]["country"] == "India", "Phyx44 country drift")
    require(
        companies["UnCrave (Licious)"]["closure_effective_date"] == "",
        "Unknown closure date filled",
    )
    require(
        companies["UnCrave (Licious)"]["closure_reported_date"] == "2025-09-09",
        "Closure report date drift",
    )
    require(
        companies["Biokraft Foods"]["application_date"] == "2025-08-20",
        "Filing date drift",
    )
    require(
        {row["company"] for row in tables["company_exclusions"]}
        == {"String Bio", "Ful Foods"},
        "Inconsistent feed exclusions",
    )
    for row in tables["policy_rows"]:
        require(
            bool(row["status"] and row["freshness"] and row["date_basis"]),
            "Incomplete policy metadata",
        )
        require(
            row["stale"] == str(int(row["policy_date"][:4]) < 2025).lower(),
            "Freshness cutoff drift",
        )
        if row["status"] == "notified_future_commencement":
            require(
                row["effective_date"] > "2026-10-13", "Future amendment misclassified"
            )
    for row in tables["company_rows"] + tables["company_exclusions"]:
        if row["country"] == "Pakistan":
            require(
                bool(row["evidence_date_precision"] and row["geographic_basis"]),
                "Missing Pakistan company metadata",
            )
    listing = tables["retail_listing_rows"][0]
    require(
        not listing["unit_price"]
        and not listing["pack_net_weight"]
        and listing["transaction_observed"] == "false",
        "Unsupported price conversion or transaction",
    )
    for filename in (
        "fssai-vegan-original-2022-faolex.pdf",
        "fssai-vegan-amendment-20260521-official.pdf",
        "fssai-vegan-amendment-20260928-egazette.pdf",
        "fssai-dairy-consultation-20250416.pdf",
        "ayfoods-products.html",
    ):
        require(
            (RAW / filename).read_bytes().startswith(b"%PDF"),
            f"Claim source is not PDF: {filename}",
        )
    result = {
        "status": "PASS",
        "scope": "Staged evidence integrity and bounded-field consistency; not independent scholarly or legal approval",
        "counts": {name: len(records) for name, records in tables.items()},
        "new_sources": len(source_rows),
        "manifest_files": len(manifest),
        "logged_requests": len(fetches),
        "table_raw_bindings": bindings,
        "staged_csv_sha256": {
            path.name: digest(path) for path in sorted(HERE.glob("*.csv"))
        },
    }
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
