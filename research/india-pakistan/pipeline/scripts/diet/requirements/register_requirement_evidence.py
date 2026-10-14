"""Register downloaded requirement evidence and explicit reference-person scenarios."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/requirements"
OUT = Path(__file__).resolve().parent
ICMR = "icmr_nin_dietary_guidelines_2024"
WHO = "who_fao_unu_protein_2007"
ICMR_URL = "https://nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf"
WHO_URL = "https://iris.who.int/server/api/core/bitstreams/b7c5ec43-bc59-4b38-b702-3f0e96a06fa1/content"
ICMR_LICENSE = (
    "Copyright ICMR-NIN 2024; personal reproduction with acknowledgment allowed; "
    "electronic reproduction for creating a product requires prior written permission"
)
WHO_LICENSE = (
    "Copyright WHO 2007; all rights reserved; reproduction permission required"
)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    """Write deterministic columns without changing the shared project registries."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Validate raw artifacts, then write provenance fragments and benchmark inputs."""
    metadata = json.loads((RAW / "who-bitstreams.json").read_text())
    entry = next(
        row
        for row in metadata["_embedded"]["bitstreams"]
        if row["name"] == "WHO_TRS_935_eng.pdf"
    )
    who_bytes = (RAW / "who-fao-unu-protein-2007.pdf").read_bytes()
    assert len(who_bytes) == entry["sizeBytes"]
    assert hashlib.md5(who_bytes).hexdigest() == entry["checkSum"]["value"]
    for name in ("who-fao-unu-protein-2007", "icmr-nin-dietary-guidelines-2024"):
        assert (RAW / f"{name}.pdf").read_bytes().startswith(b"%PDF-")

    sources = [
        {
            "source_id": ICMR,
            "title": "Dietary Guidelines for Indians, revised edition 2024",
            "publisher": "ICMR-National Institute of Nutrition",
            "url": ICMR_URL,
            "year": 2024,
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl official PDF; pdftotext -layout; visual page review",
            "license": ICMR_LICENSE,
            "notes": (
                "Guideline 8/Table 8.1 printed p58/PDF75: EAR0.66 and RDA0.83 g/kg/day; "
                "protein quality and lysine. Fig9.1 printed p63/PDF80: reference man65kg. "
                "Fig9.2 printed p65/PDF82: reference woman55kg; non-pregnant/non-lactating. "
                "Reference weights are not observed population averages. Primary paper includes "
                "menu protein72/57g; those are illustrative menu totals, not the RDA."
            ),
        },
        {
            "source_id": WHO,
            "title": "Protein and amino acid requirements in human nutrition; WHO Technical Report Series 935",
            "publisher": "WHO/FAO/UNU",
            "url": WHO_URL,
            "year": 2007,
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl official WHO IRIS REST API and PDF; checksum verification; visual page review",
            "license": WHO_LICENSE,
            "notes": (
                "Canonical record https://iris.who.int/handle/10665/43411. "
                "Section14.2 printed p242/PDF256: safe adult0.83g/kg/day assuming PDCAAS1.0. "
                "Table46 printed p243/PDF257: illustrative weights including55/65kg. "
                "Table header g/kg/day is inconsistent with rounded daily totals; use coefficient times kg. "
                "Section3.3.2 printed p41/PDF55 warns individual safe intake is not a population adequacy threshold."
            ),
        },
    ]
    write_csv(OUT / "source_rows.csv", list(sources[0]), sources)

    auxiliary_urls = {
        "who-record.json": "https://iris.who.int/server/api/pid/find?id=10665/43411",
        "who-bundles.json": "https://iris.who.int/server/api/core/items/78c03092-bcc2-40f5-90d1-60641ecdf6ea/bundles",
        "who-bitstreams.json": "https://iris.who.int/server/api/core/bundles/6619b9bf-de8d-4fc3-99aa-aa27e73bd365/bitstreams",
        "who-legacy-url-response.html": "https://iris.who.int/bitstream/handle/10665/43411/WHO_TRS_935_eng.pdf?sequence=1&isAllowed=y",
        "who-whqlibdoc-response.html": "https://whqlibdoc.who.int/trs/WHO_TRS_935_eng.pdf",
    }
    manifests = []
    for path in sorted(RAW.iterdir()):
        is_icmr = path.name.startswith("icmr-")
        sid, url, license_text = (
            (ICMR, ICMR_URL, ICMR_LICENSE) if is_icmr else (WHO, WHO_URL, WHO_LICENSE)
        )
        note = "Original official PDF download."
        if path.suffix == ".png":
            note = "DERIVED Poppler PDF page render; visually checked against cited page; local evidence only."
        elif path.suffix == ".txt":
            note = "DERIVED pdftotext -layout extraction from same-named PDF."
        elif path.suffix == ".json":
            note = "Original official WHO IRIS discovery metadata; checksum establishes English PDF identity."
        elif path.suffix == ".html":
            note = "Failed PDF route: HTML response preserved as retrieval evidence; not used for numerical facts."
        manifests.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": auxiliary_urls.get(path.name, url),
                "accessed_utc": datetime.fromtimestamp(
                    path.stat().st_mtime, tz=UTC
                ).isoformat(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "license": license_text,
                "source_id": sid,
                "notes": note,
            }
        )
    write_csv(OUT / "manifest_rows.csv", list(manifests[0]), manifests)

    benchmarks = []
    for country, sid in (("India", ICMR), ("Pakistan", WHO)):
        for weight in (55, 65):
            coefficient = Decimal("0.83")
            requirement = coefficient * weight
            locator = (
                f"Guideline8 p58/PDF75; Fig9.{2 if weight == 55 else 1} p{65 if weight == 55 else 63}/PDF{82 if weight == 55 else 80}"
                if country == "India"
                else "Section14.2 p242/PDF256 and Table46 p243/PDF257"
            )
            benchmarks.append(
                {
                    "benchmark_id": f"{country.lower()}_adult_reference_{weight}kg",
                    "country": country,
                    "source_id": sid,
                    "requirement_source_id": sid,
                    "weight_source_id": sid,
                    "reference_body_weight_kg": weight,
                    "protein_g_per_kg_day": str(coefficient),
                    "requirement_g_day": str(requirement),
                    "benchmark_type": (
                        "ICMR-NIN adult RDA scenario"
                        if country == "India"
                        else "WHO adult safe-level scenario"
                    ),
                    "requirement_population": "healthy adult reference person; excludes pregnancy/lactation increments",
                    "table_or_page": locator,
                    "method": "0.83 g/kg/day multiplied by source-listed reference weight; no intermediate rounding",
                    "notes": (
                        "Scenario comparator only. Weight is not an observed country/group average. "
                        "Comparing all-age household per-capita mean with adult benchmark is descriptive, not adequacy/deficiency. "
                        "Protein quality is unadjusted; WHO safe level assumes PDCAAS1.0."
                    ),
                }
            )
    write_csv(OUT / "benchmarks.csv", list(benchmarks[0]), benchmarks)
    assert len(benchmarks) == 4
    assert {row["requirement_g_day"] for row in benchmarks} == {"45.65", "53.95"}
    assert {row["source_id"] for row in manifests} <= {ICMR, WHO}
    print(
        f"Validated {len(manifests)} manifest entries, {len(sources)} sources, {len(benchmarks)} reference scenarios; WHO API MD5 matches."
    )


if __name__ == "__main__":
    main()
