"""Stage published HCES 2023-24 regional protein tables without modifying shared data."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/regional/india-supplement-2026-10-13"
PDF = ROOT / "data/raw/diet/india-nutritional-intake-report-594.pdf"
TEXT = PDF.with_suffix(".txt")
SOURCE = "mospi_nutrition_report_594_2025"
PDF_HASH = "f08155b2b9811d236b1a75ccdb48fc60f96efe32bdbabad1413cf7b65017b50b"
TEXT_HASH = "471bfcf200c82e04faca132a2db892b6a348e4ba1dc79da9dabb4fe932df6d81"
MERGED_UT = "Dadra & Nagar Haveli and Daman & Diu"
UTS = {
    "Andaman & Nicobar Islands",
    "Chandigarh",
    MERGED_UT,
    "Delhi",
    "Jammu & Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
}
GROUPS = (
    ("cereals", "cereals"),
    ("pulses", "pulses"),
    ("milk_products", "milk & milk products"),
    ("eggs_fish_meat", "egg, fish & meat"),
    ("other_food", "other food"),
)


def sha(path: Path) -> str:
    """Return the exact file SHA-256."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(label: str) -> str:
    """Resolve two source-label abbreviations without altering geography."""
    label = " ".join(label.split())
    return {
        "Andaman & N. Island": "Andaman & Nicobar Islands",
        "All – India*": "All-India",
    }.get(label, label)


def parse_table(page: str, count: int) -> dict[str, tuple[str, list[str]]]:
    """Extract complete labelled rows, including the one wrapped merged-UT row."""
    result = {}
    pending = ""
    for line in page.splitlines():
        stripped = line.strip()
        if stripped == "Dadra & Nagar Haveli and":
            pending = MERGED_UT
            continue
        numbers = re.findall(r"(?<!\S)\d[\d,]*(?:\.\d+)?(?!\S)", line)
        if len(numbers) != count:
            continue
        first_number = re.search(r"(?<!\S)\d[\d,]*(?:\.\d+)?(?!\S)", line)
        assert first_number is not None
        label = line[: first_number.start()].strip() or pending
        if not label or label.startswith("("):
            continue
        pending = ""
        key = normalize(label)
        assert key not in result, key
        result[key] = (label, [n.replace(",", "") for n in numbers])
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a complete staging CSV with stable field order."""
    assert rows
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Validate source tables, stage observations, and emit a bounded review receipt."""
    assert sha(PDF) == PDF_HASH, "Source PDF changed: review the new vintage first"
    assert sha(TEXT) == TEXT_HASH, "Source text changed: review extraction first"
    pages = TEXT.read_text().split("\f")
    samples = parse_table(pages[26], 5)
    proteins = parse_table(pages[81], 8)
    shares = parse_table(pages[83], 12)
    corroboration = parse_table(pages[55], 8)
    assert len(samples) == len(proteins) == len(shares) == 37
    assert set(samples) == set(proteins) == set(shares)
    assert len(corroboration) == 19
    for region, (_, values) in corroboration.items():
        assert proteins[region][1] == values, region

    # These cells were independently read from rendered source pages 27, 82 and 84.
    checks = {
        "Andhra Pradesh": ("66.4", "65.2", "6306", "4159"),
        "Goa": ("83.7", "86.6", "360", "360"),
        "Sikkim": ("83.2", "94.0", "1439", "719"),
        MERGED_UT: ("61.2", "68.9", "354", "344"),
        "Ladakh": ("73.9", "82.7", "360", "360"),
        "Lakshadweep": ("78.6", "93.1", "249", "356"),
        "Puducherry": ("65.3", "65.2", "359", "718"),
    }
    for region, expected in checks.items():
        assert tuple(proteins[region][1][2:4] + samples[region][1][2:4]) == expected
    for region, expected in {
        "Kerala": ("38.2", "37.8"),
        "Lakshadweep": ("37.5", "51.9"),
        "Haryana": ("2.9", "5.5"),
        "Gujarat": ("3.6", "3.6"),
        "All-India": ("12.4", "14.1"),
    }.items():
        values = shares[region][1]
        assert (values[3], values[9]) == expected
    assert proteins["All-India"][1][2:4] == ["61.8", "63.4"]
    assert samples["All-India"][1][2:4] == ["154357", "107596"]

    rows = []
    sums = []
    for region in sorted(set(proteins) - {"All-India"}):
        source_label, values = proteins[region]
        share_values = shares[region][1]
        for sector_index, residence in enumerate(("rural", "urban")):
            base = {
                "country": "India",
                "region": region,
                "region_type": "union_territory" if region in UTS else "state",
                "year": "2024",
                "indicator": "",
                "value": "",
                "unit": "",
                "source_id": SOURCE,
                "sex": "all",
                "age_group": "all",
                "residence": residence,
                "quintile": "all",
                "period": "2023-24",
                "sample_size": "",
                "sample_basis": "Exact nutrient-table analytical person/household sample is not restated; unavailable here.",
                "survey_sample_size": samples[region][1][2 + sector_index],
                "survey_sample_basis": "Table 1.2 actual HCES 2023-24 surveyed households; context only, not a per-person denominator.",
                "denominator": "",
                "fieldwork_start": "2023-08",
                "fieldwork_end": "2024-07",
                "fieldwork_note": "Survey period in Introduction section 1.0; months, not inferred daily dates.",
                "method": "Direct transcription of a published survey-weighted household-quantity-derived nutrient statistic; no new estimate or gap arithmetic.",
                "raw_file": str(PDF.relative_to(ROOT)),
                "raw_locator": "",
                "sample_source_id": SOURCE,
                "sample_locator": f"Table 1.2; printed page 8 / PDF page 27; {region}; {residence} sample households",
                "display_value": "",
                "notes": "",
                "source_region_label": source_label,
                "food_group": "",
                "source_year": "2025",
                "raw_sha256": PDF_HASH,
                "missingness": "value present; exact analytical sample unavailable",
                "staging_status": "SOURCE_TRANSCRIPTION_FOR_INTEGRATION_REVIEW",
            }
            value = values[2 + sector_index]
            rows.append(
                {
                    **base,
                    "indicator": "hces_average_daily_protein_intake",
                    "value": value,
                    "unit": "g/person/day",
                    "denominator": "Survey-weighted persons in the specified region and residence; household-derived per-capita average.",
                    "raw_locator": f"Statement 5; printed S5 / PDF page 82; {source_label}; 2023-24 per capita {residence}; column ({4 + sector_index})",
                    "display_value": value,
                    "notes": "Household-derived average, not direct individual intake, protein adequacy or deficiency prevalence. Per-consumer-unit columns excluded. Year is survey-period end; period retained.",
                }
            )
            offset = sector_index * 6
            subtotal = sum(Decimal(v) for v in share_values[offset : offset + 5])
            assert share_values[offset + 5] == "100.0"
            assert abs(subtotal - Decimal(100)) <= Decimal("0.3")
            sums.append(str(subtotal))
            for group_index, (key, label) in enumerate(GROUPS):
                value = share_values[offset + group_index]
                rows.append(
                    {
                        **base,
                        "indicator": f"hces_protein_share_{key}",
                        "value": value,
                        "unit": "percent_of_total_protein_intake",
                        "denominator": "Total protein represented by the five published food groups in the specified region and residence.",
                        "raw_locator": f"Statement 7; printed S7 / PDF page 84; {source_label}; {residence} {label}; column ({2 + offset + group_index})",
                        "display_value": value,
                        "food_group": label,
                        "notes": "Share of protein, not share of food mass, calories, expenditure or people. Egg/fish/meat remain one published category; dairy is separate. Rounded source shares retained without renormalization; year is survey-period end.",
                    }
                )
    assert len(rows) == 432
    keys = [(r["region"], r["residence"], r["indicator"], r["period"]) for r in rows]
    assert len(set(keys)) == len(rows)
    assert len({r["region"] for r in rows}) == 36
    assert all(Decimal(str(r["value"])) >= 0 for r in rows)
    with (ROOT / "data/processed/sources.csv").open() as handle:
        source = next(r for r in csv.DictReader(handle) if r["source_id"] == SOURCE)
    write_csv(OUT / "source_rows.csv", [source])
    write_csv(OUT / "hces_extracted_rows.csv", rows)
    with (ROOT / "data/raw/manifest.csv").open() as handle:
        manifest = [
            r
            for r in csv.DictReader(handle)
            if r["file"] in {str(PDF.relative_to(ROOT)), str(TEXT.relative_to(ROOT))}
        ]
    assert len(manifest) == 2
    now = datetime.now(UTC).isoformat()
    for filename, page in (
        ("hces-sample-p27.png", "27"),
        ("hces-protein-p82.png", "82"),
        ("hces-protein-shares-p84.png", "84"),
    ):
        path = RAW / filename
        entry = {key: "" for key in manifest[0]}
        entry.update(
            file=str(path.relative_to(ROOT)),
            url=source["url"],
            accessed_utc=now,
            sha256=sha(path),
            license=source["license"],
            source_id=SOURCE,
            notes=f"DERIVED Poppler render PDF page {page}; parent {PDF.relative_to(ROOT)}; original download timestamp retained in parent record; visually reviewed 2026-10-13.",
        )
        manifest.append(entry)
    write_csv(OUT / "hces_manifest_rows.csv", manifest)
    report = {
        "status": "PASS_FOR_STAGING_REVIEW",
        "source_id": SOURCE,
        "source_pdf_sha256": PDF_HASH,
        "regional_rows": len(rows),
        "regions": 36,
        "protein_average_rows": 72,
        "protein_share_rows": 360,
        "sample_context_rows": 72,
        "analytical_sample_missing_rows": len(rows),
        "statement5_vs_table3_8_matched_cells": len(corroboration) * 8,
        "manually_checked_protein_cells": 14,
        "manually_checked_sample_cells": 14,
        "manually_checked_protein_share_cells": 10,
        "share_sum_min": str(min(map(Decimal, sums))),
        "share_sum_max": str(max(map(Decimal, sums))),
        "national_rows_staged": 0,
        "retained_2022_23_rows": 0,
        "source_manifest_rows": len(manifest),
        "staged_csv_sha256": sha(OUT / "hces_extracted_rows.csv"),
        "sample_footnote": "All-India includes rural households from uninhabited villages considered as a special stratum; state counts are not forced to add to national total.",
        "boundaries": "Existing regional names reused by explicit source-label normalization only; no boundary geometry is modified.",
    }
    (OUT / "hces_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
