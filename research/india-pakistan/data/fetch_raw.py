"""Retrieve explicitly selected original inputs into a private, hash-checked cache."""

from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import re
import socket
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import BinaryIO
from urllib.parse import urlsplit

__all__ = ["classify", "fetch", "load_manifest", "main", "select"]
Transport = Callable[[str, BinaryIO, float, int], dict[str, object]]


def safe_relative(value: str) -> Path:
    """Accept only normalized manifest identities beneath the original input root."""
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or "\\" in value
        or "\x00" in value
        or ".." in path.parts
        or str(path) != value
        or path.parts[:2] != ("data", "raw")
        or len(path.parts) < 3
    ):
        raise ValueError("Unsafe manifest file identity")
    return Path(*path.parts)


def public_url(url: str) -> str:
    """Reject credentials, fragments and local or literal nonpublic endpoints."""
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    if (
        parsed.scheme not in {"https", "http"}
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or any(ord(char) <= 32 for char in url)
        or "." not in host
        or host.endswith((".localhost", ".local", ".internal"))
        or parsed.port not in {None, 80, 443}
    ):
        raise ValueError("Only public HTTP(S) URLs without credentials are supported")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return host
    if not address.is_global:
        raise ValueError("Nonpublic IP address")
    return host


def load_manifest(path: Path) -> list[dict[str, str]]:
    """Read and validate all identities before any retrieval can occur."""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    seen = set()
    for row in rows:
        safe_relative(row["file"])
        if row["file"] in seen or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
            raise ValueError("Duplicate file identity or invalid SHA-256")
        if not row.get("source_id"):
            raise ValueError("Missing source identity")
        seen.add(row["file"])
    return rows


def classify(row: dict[str, str]) -> tuple[str, str]:
    """Conservatively distinguish retrievable originals from generated artifacts."""
    name, notes, url = row["file"].lower(), row.get("notes", "").lower(), row["url"]
    if not url.startswith(("https://", "http://")):
        return "local_artifact", "No original HTTP byte URL is recorded."
    if name.endswith((".headers", ".request.json", ".meta.json")):
        return (
            "acquisition_metadata",
            "Headers and local request receipts are not URL response bodies.",
        )
    if re.search(r"failed acquisition|http[ :]*(?:4\d\d|5\d\d)|dns failure", notes):
        return (
            "failure_diagnostic",
            "Historical failure evidence is not a source download.",
        )
    if re.search(r"\bpost\b", notes):
        return (
            "unsupported_method",
            "Recorded acquisition may require POST; this utility only sends GET.",
        )
    if name.endswith((".png", ".txt", ".py", ".body")) or re.search(
        r"derived|pdftotext|pdftoppm|user-supplied|search tool|search queries|web-tool|rill|native capture",
        notes,
    ):
        return (
            "derived_or_captured",
            "Regenerate from separately obtained parents; URL is provenance context, not these bytes.",
        )
    try:
        public_url(url)
    except ValueError as error:
        return "unsupported_url", str(error)
    suffix = Path(urlsplit(url).path).suffix.lower()
    original = re.search(
        r"original.*(?:download|response)|exact.*(?:response|html)|official.*(?:download|structural metadata)|\bdownload;",
        notes,
    )
    if original or (
        suffix in {".pdf", ".zip", ".xlsx", ".xls", ".geojson", ".gz", ".xml", ".rar"}
        and name.endswith(suffix)
    ):
        return (
            "original_candidate",
            "Original-byte candidate only; acceptance still requires exact historical SHA-256.",
        )
    return (
        "manual_review",
        "Metadata does not unambiguously identify an original GET response.",
    )


def select(
    rows: list[dict[str, str]], files: list[str], sources: list[str]
) -> list[dict[str, str]]:
    """Require explicit exact file/source selectors, rejecting typos before network."""
    if not files and not sources:
        raise ValueError(
            "Select at least one --file or --source; bulk default is disabled"
        )
    if set(files) - {r["file"] for r in rows} or set(sources) - {
        r["source_id"] for r in rows
    }:
        raise ValueError("Unknown exact file or source selector")
    return [r for r in rows if r["file"] in files or r["source_id"] in sources]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Require a separately reviewed URL when a server redirects a request."""

    def redirect_request(
        self, req: object, fp: object, code: int, msg: str, headers: object, newurl: str
    ) -> None:
        """Do not silently retrieve an unvalidated redirect destination."""
        return


def download(
    url: str, stream: BinaryIO, timeout: float, max_bytes: int
) -> dict[str, object]:
    """Stream one bounded public GET, without proxies, cookies or redirects."""
    started = time.monotonic()
    host = public_url(url)
    addresses = socket.getaddrinfo(
        host,
        urlsplit(url).port or (443 if url.startswith("https:") else 80),
        type=socket.SOCK_STREAM,
    )
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("DNS resolves to a nonpublic address")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(
        url, headers={"User-Agent": "ResearchInputVerifier/1.0"}, method="GET"
    )
    with opener.open(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Unexpected HTTP status {response.status}")
        count = 0
        while chunk := response.read(min(65536, max_bytes + 1 - count)):
            if time.monotonic() - started > timeout:
                raise ValueError("Response exceeds elapsed-time limit")
            count += len(chunk)
            if count > max_bytes:
                raise ValueError("Response exceeds byte limit")
            stream.write(chunk)
        return {"http_status": response.status, "final_url": response.geturl()}


def safe_target(cache: Path, relative: Path) -> Path:
    """Resolve the explicit cache root, then reject symlinks beneath that root."""
    if cache.resolve().is_relative_to(Path(__file__).resolve().parents[3]):
        raise ValueError("Cache must be outside the public checkout")
    target = cache.resolve() / relative
    for candidate in (target, *target.parents):
        if candidate.is_symlink():
            raise ValueError("Symlink cache paths are not allowed")
    if not target.resolve().is_relative_to(cache.resolve()):
        raise ValueError("Cache destination escapes root")
    return target


def record(cache: Path, result: dict[str, object]) -> dict[str, object]:
    """Append metadata only; source content is never included in the receipt."""
    cache.mkdir(parents=True, exist_ok=True)
    target = safe_target(cache, Path("fetch-receipts.jsonl"))
    descriptor = os.open(
        target, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(result, sort_keys=True) + "\n")
    return result


def fetch(
    row: dict[str, str],
    cache: Path,
    *,
    transport: Transport = download,
    timeout: float = 20,
    max_bytes: int = 25 * 1024 * 1024,
) -> dict[str, object]:
    """Promote exact matching bytes without overwriting any existing accepted file."""
    relative = safe_relative(row["file"])
    target = safe_target(cache, relative)
    kind, reason = classify(row)
    result: dict[str, object] = {
        "file": row["file"],
        "source_id": row["source_id"],
        "url": row["url"],
        "expected_sha256": row["sha256"],
        "checked_at": datetime.now(UTC).isoformat(),
        "classification": kind,
        "method": "GET",
        "reason": reason,
    }
    if kind != "original_candidate":
        return record(cache, dict(result, outcome="not_retrievable"))
    if timeout <= 0 or max_bytes <= 0:
        raise ValueError("Timeout and byte limit must be positive")
    if target.exists():
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return record(
            cache,
            dict(
                result,
                actual_sha256=digest,
                outcome=(
                    "already_verified"
                    if digest == row["sha256"]
                    else "existing_conflict_preserved"
                ),
            ),
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent, prefix=".pending-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            result.update(transport(row["url"], stream, timeout, max_bytes))
        if temporary.stat().st_size > max_bytes:
            raise ValueError("Response exceeds byte limit")
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        result.update(actual_sha256=digest, bytes=temporary.stat().st_size)
        if result.get("http_status") != 200:
            result["outcome"] = "http_failure"
        elif digest != row["sha256"]:
            result["outcome"] = "hash_mismatch"
        else:
            safe_target(cache, relative)
            os.link(
                temporary, target
            )  # Atomic no-overwrite promotion; a race fails closed.
            result["outcome"] = "verified"
    except (OSError, ValueError) as error:
        result.update(outcome="retrieval_failed", error=str(error))
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return record(cache, result)


def main(argv: list[str] | None = None) -> int:
    """List selections offline or explicitly fetch selected original candidates."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=Path(__file__).with_name("MANIFEST.csv")
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="Exact manifest file identity; repeatable",
    )
    parser.add_argument(
        "--source", action="append", default=[], help="Exact source ID; repeatable"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="Explicit local cache outside the public checkout",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print classifications without any network or cache writes",
    )
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=25 * 1024 * 1024)
    args = parser.parse_args(argv)
    try:
        selected = select(load_manifest(args.manifest), args.file, args.source)
    except (ValueError, KeyError) as error:
        parser.error(str(error))
    failed = False
    for row in selected:
        if args.list:
            kind, reason = classify(row)
            result = {
                "file": row["file"],
                "source_id": row["source_id"],
                "classification": kind,
                "reason": reason,
            }
        else:
            result = fetch(
                row, args.cache_dir, timeout=args.timeout, max_bytes=args.max_bytes
            )
            failed |= result["outcome"] not in {"verified", "already_verified"}
        print(json.dumps(result, sort_keys=True))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
