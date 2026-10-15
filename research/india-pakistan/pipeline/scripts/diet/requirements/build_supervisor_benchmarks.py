"""Build separate EAR and safe-intake scenarios from pinned primary documents."""

from __future__ import annotations

import hashlib
import re
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from provenance import read_csv, write_csv

__all__ = ["benchmark_rows", "build"]
OUT = Path(__file__).resolve().parent


def verified_text(relative: str) -> str:
    """Read a saved primary-source extraction only when its manifest hash matches."""
    rows = [
        r for r in read_csv(ROOT / "data/raw/MANIFEST.csv") if r["file"] == relative
    ]
    if len(rows) != 1:
        raise ValueError(f"Expected one raw manifest binding: {relative}")
    payload = (ROOT / relative).read_bytes()
    if hashlib.sha256(payload).hexdigest() != rows[0]["sha256"]:
        raise ValueError(f"Changed raw requirement source: {relative}")
    return payload.decode("utf-8")


def captured(pattern: str, text: str) -> str:
    """Require one unambiguous number in a named primary-source passage."""
    matches = re.findall(pattern, text, flags=re.DOTALL)
    if len(matches) != 1:
        raise ValueError(f"Ambiguous or missing primary-source passage: {pattern}")
    return matches[0]


def benchmark_rows() -> list[dict[str, str]]:
    """Extract coefficients and calculate explicitly selected adult-weight scenarios."""
    icmr = verified_text(
        "data/raw/requirements/icmr-nin-dietary-guidelines-2024.txt"
    ).split("\f")[74]
    who = verified_text("data/raw/requirements/who-fao-unu-protein-2007.txt").split(
        "\f"
    )
    hces = verified_text("data/raw/diet/india-nutritional-intake-report-594.txt").split(
        "\f"
    )[34]
    coefficients = {
        "India": {
            "EAR": captured(r"intake is (\d+\.\d+)g of protein per kg/day", icmr),
            "RDA": captured(r"intake is (\d+\.\d+)g protein/kg/day", icmr),
        },
        "Pakistan": {
            "EAR": captured(r"(\d+\.\d+) g protein/kg per day \(i\.e\. exp", who[54]),
            "RDA": captured(r"is (\d+\.\d+) g/kg per day, for proteins", who[255]),
        },
    }
    consumer_weight = captured(r"weighting (\d+) Kg", hces)
    old_weights = read_csv(OUT / "benchmarks.csv")
    result = []
    for country in ("India", "Pakistan"):
        sid = (
            "icmr_nin_dietary_guidelines_2024"
            if country == "India"
            else "who_fao_unu_protein_2007"
        )
        previous = [r for r in old_weights if r["country"] == country]
        weights = sorted(
            {r["reference_body_weight_kg"] for r in previous} | {consumer_weight},
            key=Decimal,
        )
        for reference_type, coefficient in coefficients[country].items():
            for weight in weights:
                source_weight = next(
                    (r for r in previous if r["reference_body_weight_kg"] == weight),
                    None,
                )
                weight_source = (
                    source_weight["weight_source_id"]
                    if source_weight
                    else "mospi_nutrition_report_594_2025"
                )
                locator = (
                    "ICMR-NIN2024 Guideline8 PDF75/printed58"
                    if country == "India"
                    else "WHO2007 Section3.3.2 PDF55/printed41; Section14.2 PDF256/printed242"
                )
                result.append(
                    {
                        "benchmark_id": f"{country.lower()}_{reference_type}_{weight}kg",
                        "country": country,
                        "reference_type": reference_type,
                        "primary_scenario": str(
                            reference_type == "EAR" and weight == consumer_weight
                        ).lower(),
                        "reference_body_weight_kg": weight,
                        "protein_g_per_kg_day": coefficient,
                        "requirement_g_day": str(
                            Decimal(coefficient) * Decimal(weight)
                        ),
                        "source_id": sid,
                        "requirement_source_id": sid,
                        "weight_source_id": weight_source,
                        "tier": "derived",
                        "source_tier": "A",
                        "benchmark_type": (
                            "Adult estimated average requirement scenario"
                            if reference_type == "EAR"
                            else "Adult RDA / WHO safe-intake secondary scenario"
                        ),
                        "requirement_population": "healthy reference adult; not a surveyed group requirement",
                        "table_or_page": locator,
                        "weight_locator": (
                            source_weight["table_or_page"]
                            if source_weight
                            else "HCES Report594 Section2.9.5 PDF35/printed16; selected cross-country adult sensitivity weight, not a Pakistan demographic estimate"
                        ),
                        "method": "Primary-source coefficient multiplied by explicitly selected reference weight without intermediate rounding.",
                        "notes": "Adult scenarios, not population-average weights or prevalence thresholds. HCES consumer units scale energy needs, not protein requirements. Pakistan adult-equivalent intake remains unestablished. Protein quality is unadjusted; no distribution of usual individual intake is inferred.",
                    }
                )
    return result


def build() -> None:
    """Write the revised scenario ledger without mutating historical registrations."""
    rows = benchmark_rows()
    write_csv(OUT / "benchmarks-supervisor.csv", list(rows[0]), rows)
    print(f"Supervisor adult-reference scenarios: {len(rows)}; no prevalence estimate")


if __name__ == "__main__":
    build()
