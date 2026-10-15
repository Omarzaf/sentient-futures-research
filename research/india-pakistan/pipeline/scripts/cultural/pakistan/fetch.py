"""Retain public cultural-source downloads and explicit acquisition outcomes."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/cultural/pakistan"


def fetch(job: dict[str, str]) -> dict[str, object]:
    """Download one declared source without retries or overwriting evidence."""
    path = RAW / job["file"]
    outcome = path.with_suffix(path.suffix + ".request.json")
    assert not path.exists() and not outcome.exists()
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-L",
            "--max-time",
            "55",
            "-D",
            str(path) + ".headers",
            "-o",
            str(path),
            "-w",
            "%{http_code}",
            job["url"],
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    record = dict(job)
    record.update(
        accessed_utc=datetime.now(UTC).isoformat(),
        http_status=result.stdout,
        curl_exit=result.returncode,
        stderr=result.stderr,
    )
    outcome.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print(job["file"], result.stdout, result.returncode, flush=True)
    return record


if __name__ == "__main__":
    jobs = json.loads(Path(sys.argv[1]).read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(fetch, jobs))
