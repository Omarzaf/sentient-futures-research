"""Validate and summarize aggregate diagnostics without reading survey records."""

import csv
import hashlib
import json
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    """Read an aggregate CSV from the isolated output folder."""
    with (OUT / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def save_csv(name: str, data: list[dict]) -> None:
    """Write only source classifications or aggregate diagnostic rows."""
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def sha(path: Path) -> str:
    """Hash the exact bytes without exporting their contents."""
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def build_form_mapping() -> None:
    """Reproduce item-to-part source locators using only public codes and forms."""
    actual = {int(row["itc"]) for row in rows("item_unit_totals_raw.csv")}
    seen: dict[int, dict] = {}
    sources = {
        "data/raw/diet/pakistan-hies-2024-25-female-questionnaire.txt": {
            19: "A",
            20: "A",
            21: "A",
            22: "B",
            23: "B",
            24: "B",
        },
        "scripts/diet/m3_microdata_profile/male-questionnaire-source.txt": {
            17: "C",
            18: "D",
            19: "D",
            20: "D",
            21: "D",
            22: "E",
        },
    }
    for source, parts in sources.items():
        pages = (ROOT / source).read_text().split("\f")
        for page, part in parts.items():
            for line_number, line in enumerate(pages[page - 1].splitlines(), 1):
                for match in re.finditer(r"\b\d{5,6}\b", line):
                    code = int(match.group())
                    if code not in actual or code % 100 == 0:
                        continue
                    if code in seen:
                        assert seen[code]["part"] == part
                        continue
                    seen[code] = {
                        "itc": code,
                        "part": part,
                        "source_text": source,
                        "printed_page": page,
                        "line_within_page": line_number,
                        "code_as_printed": match.group(),
                    }
    assert set(seen) | {1000, 2000, 4000, 5000, 6000} == actual
    assert len(seen) == 285
    save_csv("form_item_part_mapping.csv", [seen[key] for key in sorted(seen)])


def main() -> None:
    """Check artifact integrity and preserve unresolved source differences."""
    assert (OUT / "run.log").read_text().strip() == (
        "Aggregate profile saved; zero household/person rows or identifiers exported."
    )
    build_form_mapping()
    # Exact source cells from report printed p25, not standalone Table23.
    report = {
        "wheat_and_wheat_flour": [6.59, 7.12, 5.76],
        "rice_and_rice_flour": [0.86, 0.84, 0.89],
        "milk_fresh_and_boiled": [6.15, 6.17, 6.12],
        "mutton": [0.05, 0.04, 0.06],
        "beef": [0.11, 0.10, 0.12],
        "chicken_meat": [0.34, 0.29, 0.41],
        "eggs": [2.83, 2.44, 3.44],
        "potato": [1.17, 1.17, 1.17],
        "tomato": [0.59, 0.60, 0.57],
        "onion": [0.85, 0.85, 0.85],
        "sugar_desi_and_milled": [1.22, 1.31, 1.07],
        "tea_black_and_green": [81.47, 82.70, 79.52],
    }
    comparison = rows("table23_reconciliation_diagnostic.csv")
    report_rows = []
    ratio_rows = []
    for residence in ("all", "rural", "urban"):
        selected = [r for r in comparison if r["residence"] == residence]
        for period in (14, 30):
            ratios = [
                float(r["published_value"])
                / float(r["monthly_quantity_per_roster_person"])
                for r in selected
                if int(r["recall_days"]) == period
            ]
            ratio_rows.append(
                {
                    "residence": residence,
                    "recall_days": period,
                    "items": len(ratios),
                    "median_published_table23_to_raw_30day_ratio": statistics.median(
                        ratios
                    ),
                    "timing_factor_source": "30/14 diagnostic; source annual26/12 retained separately",
                }
            )
        for r in selected:
            if r["food_group"] not in report:
                continue
            published = report[r["food_group"]][
                ("all", "rural", "urban").index(residence)
            ]
            report_rows.append(
                {
                    "food_group": r["food_group"],
                    "residence": residence,
                    "report_3_7c_value": published,
                    "standalone_table23_value": r["published_value"],
                    "raw_30day_value": r["monthly_quantity_per_roster_person"],
                    "raw_annual26_value": r["monthly_quantity_annual26_per_roster"],
                    "source_locator": "HIES2024-25 report printed p25 Table3.7.C",
                    "report_vs_standalone_2dp_equal": round(published, 2)
                    == round(float(r["published_value"]), 2),
                }
            )
    save_csv("report_vs_standalone_diagnostic.csv", report_rows)
    save_csv("table23_systematic_ratio_diagnostic.csv", ratio_rows)

    # Read classification cells only from the official codebook, omitting file metadata.
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    codebook = ROOT / "data/raw/diet/m3-survey-inputs-2026-10-13/coding-scheme.xlsx"
    public_codes = []
    with zipfile.ZipFile(codebook) as archive:
        strings = [
            "".join(node.itertext())
            for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))
        ]
        for sheet, code_col, region_col in ((1, "C", "D"), (2, "D", "E")):
            xml = ET.fromstring(archive.read(f"xl/worksheets/sheet{sheet}.xml"))
            for row in xml.findall(".//m:row", ns):
                cells = {}
                for cell in row.findall("m:c", ns):
                    value = cell.find("m:v", ns)
                    if value is not None:
                        cells[cell.attrib["r"].rstrip("0123456789")] = (
                            strings[int(value.text)]
                            if cell.attrib.get("t") == "s"
                            else value.text
                        )
                if cells.get(region_col) not in {"1", "2"}:
                    continue
                public_codes.append(
                    {
                        "province": cells["A"],
                        "province_first_digit": cells[code_col][0],
                        "region_code": cells[region_col],
                        "residence": "rural" if sheet == 2 else "urban",
                        "source_sheet": f"sheet{sheet}",
                        "source_row": row.attrib["r"],
                    }
                )
    save_csv("source_geography_code_evidence.csv", public_codes)
    suppressed = 0
    for path in OUT.rglob("*.csv"):
        with path.open() as stream:
            reader = csv.DictReader(stream)
            assert not {"hhcode", "prcode", "hhno", "idc"} & set(
                reader.fieldnames or []
            )
            for row in reader:
                if row.get("amounts_suppressed_small_cell") == "TRUE":
                    suppressed += 1
                    assert all(
                        value == ""
                        for key, value in row.items()
                        if key in {"q1", "q2", "q3", "q4", "v1", "v2", "v3", "v4"}
                        or key.startswith("sum_")
                    )
    archive = ROOT / "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip"
    assert (
        sha(archive)
        == "cf1286dc00cfc325df7a51fab64b8baecc4f6b62e015742e229bf299760898cc"
    )
    assert (
        sha(ROOT / "verify_plan.py")
        == "a0dce0308eb9965e29da0157b6557e285ab54fba351380719ffc13306d39126d"
    )
    source_paths = [
        archive,
        codebook,
        ROOT / "data/raw/diet/m3-survey-inputs-2026-10-13/male-questionnaire.pdf",
        ROOT / "data/raw/diet/pakistan-hies-2024-25-female-questionnaire.pdf",
        ROOT / "data/raw/diet/pakistan-hies-2024-25-manual.pdf",
        ROOT / "data/raw/regional/pakistan-hies-2024-25.pdf",
        ROOT / "data/raw/regional/pakistan-hies-table23.xls",
        ROOT / "data/raw/regional/pbs-hies-catalog.html",
    ]
    receipt = {
        "date": "2026-10-13",
        "status": "PROFILE_VERIFIED_ANALYTICAL_RECONCILIATION_HELD",
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in source_paths},
        "outputs": {
            str(p.relative_to(OUT)): sha(p)
            for p in sorted(OUT.rglob("*"))
            if p.is_file()
            and p.name != "integrity_receipt.json"
            and "__pycache__" not in p.parts
        },
        "small_cell_amount_groups_suppressed_including_historical": suppressed,
        "household_or_person_identifier_columns_exported": 0,
        "household_or_person_rows_exported": 0,
        "source_requested_outlier_stats": "Only aggregate min/max/quantiles/shares; no record IDs",
        "nutrient_or_imputation_values_computed": 0,
        "quintiles_reconstructed": False,
        "shared_registry_or_processed_or_state_writes": 0,
        "verifier_executed": False,
        "verifier_original_sha256_preserved": True,
    }
    (OUT / "integrity_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS: aggregate outputs, source hashes, suppression and unchanged verifier.")


if __name__ == "__main__":
    main()
