"""Capture public retail pages using GET only; never calculate protein prices."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

__all__ = ["capture", "parse_product"]


class PublicHTML(HTMLParser):
    """Read product metadata without executing scripts or submitting forms."""

    def __init__(self) -> None:
        super().__init__()
        self.jsonld: list[str] = []
        self.ld: str | None = None
        self.h1: list[str] = []
        self.in_h1 = False
        self.meta: dict[str, str] = {}
        self.final_prices: list[str] = []
        self.text: list[str] = []
        self.skip = 0
        self.in_variant = False
        self.variant_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect only public structured product and visible text fields."""
        data = dict(attrs)
        if tag == "script" and data.get("type") == "application/ld+json":
            self.ld = ""
        if tag in {"script", "style", "svg"}:
            self.skip += 1
        if tag == "h1":
            self.in_h1 = True
        if "product-detail-title-variant" in (data.get("class") or ""):
            self.in_variant = True
        if tag == "meta":
            key = data.get("property") or data.get("itemprop") or ""
            self.meta[key] = data.get("content") or ""
        if data.get("data-price-type") == "finalPrice":
            self.final_prices.append(data.get("data-price-amount") or "")

    def handle_endtag(self, tag: str) -> None:
        """Close parsed contexts without executing any website behavior."""
        if tag == "script" and self.ld is not None:
            self.jsonld.append(self.ld)
            self.ld = None
        if tag in {"script", "style", "svg"}:
            self.skip = max(0, self.skip - 1)
        if tag == "h1":
            self.in_h1 = False
        if tag == "span":
            self.in_variant = False

    def handle_data(self, data: str) -> None:
        """Preserve text and JSON-LD in their separate source representations."""
        if self.ld is not None:
            self.ld += data
        if self.in_h1:
            self.h1.append(data)
        if self.in_variant:
            self.variant_text.append(data)
        if not self.skip and data.strip():
            self.text.append(data.strip())


def _nodes(value: object) -> list[dict]:
    """Walk only JSON containers to locate schema product records."""
    if isinstance(value, list):
        return [node for child in value for node in _nodes(child)]
    if isinstance(value, dict):
        return [value, *[node for child in value.values() for node in _nodes(child)]]
    return []


def parse_product(body: str) -> dict:
    """Extract an unambiguous listed price with explicit evidence and missingness."""
    parsed = PublicHTML()
    parsed.feed(body)
    products = []
    for block in parsed.jsonld:
        try:
            nodes = _nodes(json.loads(block))
        except json.JSONDecodeError:
            continue
        products.extend(node for node in nodes if node.get("@type") == "Product")
    product = products[0] if products else {}
    title = product.get("name") or (parsed.h1[0].strip() if parsed.h1 else None)
    offers = product.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if len(offers) == 1 else {}
    if not isinstance(offers, dict):
        offers = {}
    price = offers.get("price") or parsed.meta.get("product:price:amount")
    currency = offers.get("priceCurrency") or parsed.meta.get("product:price:currency")
    price_text = str(price) if price is not None else None
    evidence = []
    if price_text:
        try:
            amount = Decimal(price_text)
            if not amount.is_finite() or amount <= 0:
                raise InvalidOperation
            if any(Decimal(value) == amount for value in parsed.final_prices if value):
                evidence.append(
                    "JSON-LD/meta price matches rendered finalPrice attribute"
                )
            meta = parsed.meta.get("product:price:amount")
            if meta and Decimal(meta) == amount:
                evidence.append("product:price:amount meta corroborates offer")
            visible = " ".join(parsed.text)
            forms = {f"{amount:,.2f}", f"{amount:.2f}", f"{amount:f}"}
            money = r"(?:₹|INR|PKR|Rs\.?)"
            if any(
                re.search(
                    money + r"\s*" + re.escape(form) + r"(?![\d.])",
                    visible,
                    re.IGNORECASE,
                )
                for form in forms
            ):
                evidence.append(
                    "currency and price occur together in non-script page text"
                )
        except InvalidOperation:
            price_text = None
    visible = " ".join(parsed.text)
    variant_text = " ".join(parsed.variant_text).strip()
    pack = re.search(
        r"(\d+(?:\.\d+)?)\s*(kg|gm|grams?|g|ml|liters?|litres?|litre|liter|ltr|l|pcs?|pieces?|count|pack)\b",
        variant_text or title or "",
        re.IGNORECASE,
    )
    if pack is None:
        pack = re.search(r"(\d+)\s*[- ](Pack)\b", title or "", re.IGNORECASE)
    package = pack.group(0) if pack else None
    visible_evidence = any(
        "rendered finalPrice" in item or "non-script page text" in item
        for item in evidence
    )
    result = {
        "title": title,
        "listed_price": price_text,
        "currency": currency,
        "price_evidence": evidence,
        "package_text_in_title": package,
        "package_quantity_as_shown": pack.group(1) if pack else None,
        "package_unit_as_shown": pack.group(2) if pack else None,
        "package_status": "Source text only; no multipack conversion or net-mass inference",
        "variant": variant_text or title,
        "variant_source": (
            "selected product-detail-title-variant span"
            if variant_text
            else "product title"
        ),
        "availability_as_reported": offers.get("availability"),
        "location_as_shown": None,
        "location_status": "No postcode or delivery location selected; fulfilment not checked",
        "protein_value": None,
        "protein_basis": None,
        "protein_basis_status": "Not extracted or independently verified; no protein-price calculation",
        "nutrition_text_candidates": re.findall(
            r".{0,35}\bprotein\b.{0,100}", visible, re.IGNORECASE
        )[:5],
        "evidence_status": (
            "raw_listed_price_observation"
            if title and price_text and currency and visible_evidence
            else "HOLD_ambiguous_or_missing_price"
        ),
        "transaction_observed": False,
        "national_market_inference": False,
    }
    return result


def capture(plan: list[dict], output_dir: Path) -> list[dict]:
    """Capture one source-bound plan with capped failures and bounded rate."""
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "capture-manifest.jsonl"
    failures: dict[str, int] = {}
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            old = json.loads(line)
            if old.get("retrieval_failed"):
                host = old["source_host"]
                failures[host] = failures.get(host, 0) + 1
    results = []
    for target in plan:
        url = target["url"]
        parts = urlsplit(url)
        if (
            parts.scheme != "https"
            or parts.username
            or parts.password
            or not parts.hostname
        ):
            raise ValueError(
                "Only unauthenticated public HTTPS source URLs are allowed"
            )
        host = parts.hostname
        if failures.get(host, 0) >= 3:
            continue
        started = datetime.now(UTC).isoformat()
        identifier = hashlib.sha256((url + started).encode()).hexdigest()[:20]
        body_path, header_path = (
            raw_dir / f"{identifier}.html",
            raw_dir / f"{identifier}.headers",
        )
        process = subprocess.run(
            [
                "curl",
                "--max-time",
                "40",
                "--max-redirs",
                "3",
                "--location",
                "--silent",
                "--show-error",
                "--dump-header",
                str(header_path),
                "--output",
                str(body_path),
                "--write-out",
                "%{http_code}\t%{url_effective}\t%{size_download}",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        finished = datetime.now(UTC).isoformat()
        metadata = process.stdout.split("\t")
        http_status = int(metadata[0]) if metadata and metadata[0].isdigit() else 0
        failed = process.returncode != 0 or http_status != 200
        if failed:
            failures[host] = failures.get(host, 0) + 1
        body_bytes = body_path.read_bytes() if body_path.exists() else b""
        headers = (
            header_path.read_text(errors="replace") if header_path.exists() else ""
        )
        header_fields = {
            name.lower(): value.strip()
            for name, value in re.findall(
                r"^([^:\r\n]+):\s*([^\r\n]*)", headers, re.MULTILINE
            )
        }
        record = {
            "capture_id": identifier,
            "url": url,
            "effective_url": metadata[1] if len(metadata) > 1 else None,
            "source_host": host,
            "country": target["country"],
            "category": target["category"],
            "retailer": target["retailer"],
            "capture_started_utc": started,
            "capture_finished_utc": finished,
            "http_status": http_status,
            "curl_exit_code": process.returncode,
            "retrieval_failed": failed,
            "source_failure_count": failures.get(host, 0),
            "raw_file": str(body_path.relative_to(output_dir)),
            "raw_sha256": hashlib.sha256(body_bytes).hexdigest(),
            "raw_bytes": len(body_bytes),
            "headers_file": str(header_path.relative_to(output_dir)),
            "headers_sha256": (
                hashlib.sha256(header_path.read_bytes()).hexdigest()
                if header_path.exists()
                else None
            ),
            "http_date": header_fields.get("date"),
            "http_age": header_fields.get("age"),
            "cache_control": header_fields.get("cache-control"),
            "licence": "Public retail page; redistribution rights unestablished; raw capture retained privately",
            "source_constraints": "Public listed offer, not a transaction, stock audit, delivery quote or national product census",
            "error": process.stderr.strip()[:300] if process.returncode else None,
        }
        if not failed:
            record.update(parse_product(body_bytes.decode("utf-8", errors="replace")))
        else:
            record["evidence_status"] = "HOLD_retrieval_failure"
        with manifest.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        results.append(record)
        print(
            json.dumps(
                {
                    "capture_id": identifier,
                    "country": target["country"],
                    "category": target["category"],
                    "http_status": http_status,
                    "evidence_status": record["evidence_status"],
                }
            ),
            flush=True,
        )
        time.sleep(0.5)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    capture(json.loads(args.plan.read_text()), args.output_dir)
