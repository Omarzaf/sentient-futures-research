"""Fetch the assigned public evidence without modifying shared registries."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/altprotein/supervisor_revision_20261013"


def main() -> None:
    """Save original public responses and append one receipt per request."""
    targets = json.loads((HERE / "fetch_targets.json").read_text())
    for target in targets:
        destination = RAW / target["file"]
        if destination.exists():
            print(f"preserved existing {target['file']}", flush=True)
            continue
        started = datetime.now(UTC).isoformat()
        result = subprocess.run(
            [
                "curl",
                "--location",
                "--silent",
                "--show-error",
                "--max-time",
                "40",
                "--output",
                str(destination),
                "--write-out",
                "%{http_code}\t%{url_effective}\t%{content_type}",
                target["url"],
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        fields = result.stdout.split("\t")
        body = destination.read_bytes() if destination.exists() else b""
        record = {
            **target,
            "started_utc": started,
            "completed_utc": datetime.now(UTC).isoformat(),
            "curl_exit": result.returncode,
            "http_status": fields[0] if fields else "",
            "effective_url": fields[1] if len(fields) > 1 else "",
            "content_type": fields[2] if len(fields) > 2 else "",
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest() if body else "",
            "error": result.stderr.strip(),
        }
        with (HERE / "fetch-log.jsonl").open("a") as handle:
            handle.write(json.dumps(record) + "\n")
        print(
            f"{target['file']}: {record['http_status']} {len(body)} bytes", flush=True
        )
    records = [
        json.loads(line) for line in (HERE / "fetch-log.jsonl").read_text().splitlines()
    ]
    with (HERE / "fetch-log.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    main()
