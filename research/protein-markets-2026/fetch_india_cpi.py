"""Capture the public MoSPI CPI API with documented pagination and no login."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

__all__ = ["fetch_cpi"]


def fetch_cpi(output_dir: Path) -> dict:
    """Download every public 2012-base all-India rural/urban 2023–24 CPI row."""
    raw_dir = output_dir / "raw"
    if (
        (output_dir / "cpi-data.json").exists()
        or (output_dir / "cpi-download-receipts.json").exists()
        or (raw_dir.exists() and any(raw_dir.glob("cpi-page-*")))
    ):
        raise FileExistsError(
            "Preserve existing CPI captures; choose a fresh output directory"
        )
    raw_dir.mkdir(parents=True, exist_ok=True)
    records, receipts = [], []
    page, total_pages = 1, 1
    while page <= total_pages:
        params = {
            "base_year": "2012",
            "series": "Current",
            "year": "2023,2024",
            "state_code": "99",
            "sector_code": "1,2",
            "Format": "JSON",
            "limit": 200,
            "page": page,
        }
        url = "https://api.mospi.gov.in/api/cpi/getCPIIndex?" + urlencode(params)
        target, headers = (
            raw_dir / f"cpi-page-{page:02}.json",
            raw_dir / f"cpi-page-{page:02}.headers",
        )
        started = datetime.now(UTC).isoformat()
        result = subprocess.run(
            [
                "curl",
                "--max-time",
                "40",
                "--location",
                "--silent",
                "--show-error",
                "--dump-header",
                str(headers),
                "--output",
                str(target),
                "--write-out",
                "%{http_code}",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        receipt = {
            "url": url,
            "started_utc": started,
            "finished_utc": datetime.now(UTC).isoformat(),
            "http_status": result.stdout,
            "curl_exit_code": result.returncode,
            "file": str(target),
            "sha256": (
                hashlib.sha256(target.read_bytes()).hexdigest()
                if target.exists()
                else None
            ),
            "headers_file": str(headers),
            "headers_sha256": (
                hashlib.sha256(headers.read_bytes()).hexdigest()
                if headers.exists()
                else None
            ),
            "error": result.stderr or None,
        }
        receipts.append(receipt)
        (output_dir / "cpi-download-receipts.json").write_text(
            json.dumps(receipts, indent=2) + "\n"
        )
        if result.returncode or result.stdout != "200":
            raise RuntimeError(
                "CPI retrieval failed; receipt retained; no automatic retry"
            )
        data = json.loads(target.read_text())
        if data.get("statusCode") is not True:
            raise ValueError("CPI API did not report success")
        meta = data["meta_data"]
        total_pages = int(meta["totalPages"])
        records.extend(data["data"])
        print(
            json.dumps(
                {"page": page, "total_pages": total_pages, "records": len(data["data"])}
            ),
            flush=True,
        )
        page += 1
        time.sleep(0.3)
    if len(records) != int(meta["totalRecords"]):
        raise ValueError("Incomplete CPI pagination")
    combined = {
        "source": "MoSPI public API /api/cpi/getCPIIndex",
        "base_year": "2012",
        "api_record_count": len(records),
        "data": records,
        "source_pages": [
            {"file": Path(r["file"]).name, "sha256": r["sha256"]} for r in receipts
        ],
    }
    (output_dir / "cpi-data.json").write_text(json.dumps(combined, indent=2) + "\n")
    return combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    fetch_cpi(args.output_dir)
