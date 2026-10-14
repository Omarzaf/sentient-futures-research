"""Capture public Pakistan evidence bytes and acquisition metadata via curl."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/altprotein/pakistan"
CAT = Path(__file__).with_name("acquisitions.json")


def fetch(name: str, url: str, source_id: str) -> dict[str, str]:
    """Download a public page without submissions and record exact bytes."""
    path = RAW / name
    proc = subprocess.run(
        [
            "curl",
            "-L",
            "--fail",
            "--max-time",
            "60",
            "--retry",
            "1",
            "-A",
            "Mozilla/5.0",
            url,
            "-o",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    entry = {
        "file": str(path.relative_to(ROOT)),
        "url": url,
        "accessed_utc": datetime.now(UTC).isoformat(),
        "source_id": source_id,
        "returncode": str(proc.returncode),
    }
    if proc.returncode == 0:
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    else:
        entry["error"] = proc.stderr[-1500:]
    return entry


def main() -> None:
    """Fetch the named public source batch and append its acquisition ledger."""
    import sys

    items = json.loads(Path(sys.argv[1]).read_text())
    catalog = Path(sys.argv[2]) if len(sys.argv) > 2 else CAT
    records = json.loads(catalog.read_text()) if catalog.exists() else []
    for item in items:
        if any(
            r["file"].endswith("/" + item[0]) and r["returncode"] == "0"
            for r in records
        ):
            print(item[0], "saved earlier")
            continue
        entry = fetch(*item)
        records.append(entry)
        catalog.write_text(json.dumps(records, indent=2) + "\n")
        print(item[0], entry["returncode"], flush=True)


if __name__ == "__main__":
    main()
