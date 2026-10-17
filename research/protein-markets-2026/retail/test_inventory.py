"""Verify evidence boundaries of the offline retail inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from build_inventory import build_inventory, validate_capture
from capture import parse_product


def product_page(
    price: str = "95", stock: str = "InStock", text: str = "₹ 95.00"
) -> str:
    """Return a synthetic source page with independent rendered price text."""
    data = {
        "@type": "Product",
        "name": "Example lentils",
        "offers": {
            "@type": "Offer",
            "price": price,
            "priceCurrency": "INR",
            "availability": "https://schema.org/" + stock,
        },
    }
    return (
        '<script type="application/ld+json">'
        + json.dumps(data)
        + '</script><span class="product-detail-title-variant">500gm</span><p>'
        + text
        + "</p>"
    )


def saved_capture(tmp_path: Path, body: str, identifier: str = "example") -> dict:
    """Create a synthetic capture with verifiable body/header hashes."""
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    data = body.encode()
    headers = b"HTTP/2 200\r\ncontent-type: text/html\r\n\r\n"
    (raw / f"{identifier}.html").write_bytes(data)
    (raw / f"{identifier}.headers").write_bytes(headers)
    return {
        "capture_id": identifier,
        "url": "https://example.test/product",
        "source_host": "example.test",
        "country": "India",
        "category": "dal",
        "retailer": "Synthetic test outlet",
        "capture_started_utc": "2026-10-15T00:00:00+00:00",
        "capture_finished_utc": "2026-10-15T00:00:01+00:00",
        "http_status": 200,
        "retrieval_failed": False,
        "raw_file": f"raw/{identifier}.html",
        "raw_sha256": hashlib.sha256(data).hexdigest(),
        "raw_bytes": len(data),
        "headers_file": f"raw/{identifier}.headers",
        "headers_sha256": hashlib.sha256(headers).hexdigest(),
    }


def test_requires_currency_corroboration_not_an_unrelated_number() -> None:
    """An uncorroborated JSON-LD offer cannot become a displayed price."""
    assert parse_product(product_page(text="95 customer reviews"))[
        "evidence_status"
    ].startswith("HOLD")
    assert (
        parse_product(product_page())["evidence_status"]
        == "raw_listed_price_observation"
    )


def test_selected_variant_and_count_units_preserved() -> None:
    """Use the selected source variant and preserve pc as a count unit."""
    result = parse_product(product_page().replace("500gm", "25Pc"))
    assert result["package_quantity_as_shown"] == "25"
    assert result["package_unit_as_shown"] == "Pc"
    assert result["variant"] == "25Pc"


def test_no_protein_inference_from_marketing() -> None:
    """Marketing phrases cannot fill a missing nutrition basis."""
    result = parse_product(product_page(text="₹ 95.00 rich in protein"))
    assert result["protein_value"] is None
    assert result["protein_basis"] is None
    assert result["transaction_observed"] is False


def test_rejects_nonpositive_and_nonfinite_prices() -> None:
    """Invalid prices remain held even when a matching figure occurs."""
    for price in ("0", "-1", "NaN", "Infinity"):
        assert parse_product(product_page(price=price, text="₹ " + price))[
            "evidence_status"
        ].startswith("HOLD")


def test_tampered_body_fails_before_observation(tmp_path: Path) -> None:
    """Changed source bytes cannot silently preserve verification status."""
    record = saved_capture(tmp_path, product_page())
    (tmp_path / record["raw_file"]).write_text("changed")
    with pytest.raises(ValueError, match="Raw SHA mismatch"):
        validate_capture(record, tmp_path)


def test_currency_and_cache_held(tmp_path: Path) -> None:
    """Wrong-country currency and explicit positive cache age cannot pass."""
    record = saved_capture(tmp_path, product_page())
    assert (
        validate_capture({**record, "country": "Pakistan"}, tmp_path)["evidence_status"]
        == "HOLD_currency_mismatch"
    )
    assert (
        validate_capture({**record, "http_age": "100"}, tmp_path)["evidence_status"]
        == "HOLD_cache_age"
    )


def test_latest_url_dedup_and_out_of_stock_separation(tmp_path: Path) -> None:
    """Retain the latest capture per URL and separate stock status from price."""
    first = saved_capture(tmp_path, product_page(), "first")
    last = saved_capture(tmp_path, product_page(stock="OutOfStock"), "last")
    last["capture_finished_utc"] = "2026-10-15T00:00:02+00:00"
    (tmp_path / "capture-manifest.jsonl").write_text(
        json.dumps(first) + "\n" + json.dumps(last) + "\n"
    )
    coverage = build_inventory(tmp_path)
    india = coverage["country"]["India"]
    assert coverage["capture_count"] == 2
    assert india["attempted_distinct_urls"] == 1
    assert india["verified_original_page_price_observations"] == 1
    assert india["source_listed_in_stock"] == 0
    assert india["source_listed_out_of_stock"] == 1


def test_capture_path_cannot_escape_scope(tmp_path: Path) -> None:
    """A manifest cannot direct offline reading outside its named folder."""
    record = saved_capture(tmp_path, product_page())
    with pytest.raises(ValueError, match="escapes"):
        validate_capture({**record, "raw_file": "../private.html"}, tmp_path)


def test_separate_output_preserves_source_packet(tmp_path: Path) -> None:
    """Umbrella rebuilds can write elsewhere without mutating capture inputs."""
    data_dir = tmp_path / "input"
    data_dir.mkdir()
    record = saved_capture(data_dir, product_page())
    manifest = data_dir / "capture-manifest.jsonl"
    manifest.write_text(json.dumps(record) + "\n")
    before = manifest.read_bytes()
    output_dir = tmp_path / "rebuilt"
    build_inventory(data_dir, output_dir)
    assert manifest.read_bytes() == before
    assert not (data_dir / "coverage.json").exists()
    assert (output_dir / "coverage.json").exists()
