"""Extract national meat series from the downloaded 2025-2034 Outlook vintage."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/oecd/outlook_2025_2034_ind_pak.csv"
SOURCE_ID = "oecd_fao_outlook_2025_2034"
FIELDS = [
    "country",
    "year",
    "item",
    "metric",
    "value",
    "unit",
    "source_id",
    "flag",
    "method",
    "period",
    "raw_file",
    "raw_locator",
    "notes",
]
ITEMS = {
    "CPC_EX_BV": "Beef and veal",
    "CPC_EX_PK": "Pigmeat",
    "CPC_EX_PT": "Poultry meat",
    "CPC_EX_SH": "Sheepmeat",
}
MEASURES = {
    "FO_PC": "human_consumption",
    "FO_DFS_PROT": "food_protein_availability",
    "QC": "consumption",
    "QP": "production",
    "IM": "imports",
    "EX": "exports",
}
CONVENTIONS = {
    "RW": "retail weight",
    "CWE": "carcass weight equivalent",
    "RTOC": "ready to cook",
    "_Z": "not applicable",
}
COUNTRIES = {"IND": "India", "PAK": "Pakistan"}


def extract_rows() -> Iterator[dict[str, str]]:
    """Yield sourced rows without changing original numeric strings or weight bases."""
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = [
            dict(row, raw_csv_line=str(line))
            for line, row in enumerate(csv.DictReader(handle), start=2)
        ]
    assert len(rows) == 34050, "Unexpected raw row count; review retrieval."
    assert {r["VERSION_ID"] for r in rows} == {"AO_2025_2034"}
    assert {r["REF_AREA"] for r in rows} == set(COUNTRIES)
    assert {r["FREQ"] for r in rows} == {"A"}
    selected = [r for r in rows if r["COMMODITY"] in ITEMS and r["MEASURE"] in MEASURES]
    counts = Counter((r["REF_AREA"], r["COMMODITY"], r["MEASURE"]) for r in selected)
    assert len(selected) == 1200 and len(counts) == 48
    assert set(counts.values()) == {25}, "Every series must contain 2010-2034."
    keys = [
        (r["REF_AREA"], r["COMMODITY"], r["MEASURE"], r["TIME_PERIOD"])
        for r in selected
    ]
    assert len(keys) == len(set(keys)), "Duplicate source observations."
    for row in sorted(
        selected,
        key=lambda r: (r["REF_AREA"], r["COMMODITY"], r["MEASURE"], r["TIME_PERIOD"]),
    ):
        assert row["OBS_VALUE"], "Missing source value must be recorded as a gap."
        measure = row["MEASURE"]
        convention = CONVENTIONS[row["CONVENTION"]]
        if measure == "FO_PC":
            assert (row["UNIT_MEASURE"], row["UNIT_MULT"], row["CONVENTION"]) == (
                "KG_PS",
                "0",
                "RW",
            )
            unit = "kg/person/year (retail weight)"
        elif measure == "FO_DFS_PROT":
            assert (row["UNIT_MEASURE"], row["UNIT_MULT"]) == ("G_PS_D", "0")
            unit = "g/person/day"
        else:
            assert (row["UNIT_MEASURE"], row["UNIT_MULT"]) == ("T", "3")
            unit = f"1000 tonnes ({convention})"
        year = int(row["TIME_PERIOD"])
        period = "projection" if year >= 2025 else "historical_or_base_estimate"
        yield {
            "country": COUNTRIES[row["REF_AREA"]],
            "year": row["TIME_PERIOD"],
            "item": ITEMS[row["COMMODITY"]],
            "metric": f"oecd_{MEASURES[measure]}_{period}",
            "value": row["OBS_VALUE"],
            "unit": unit,
            "source_id": SOURCE_ID,
            "flag": f"{period};vintage=AO_2025_2034;obs_status={row['OBS_STATUS']};commodity={row['COMMODITY']};measure={measure};unit_mult={row['UNIT_MULT']};convention={row['CONVENTION']}",
            "method": "Direct extraction; original OBS_VALUE decimal string retained without multiplication, rounding, aggregation or imputation. Annual frequency and source UNIT_MULT/CONVENTION are represented in unit.",
            "period": period,
            "raw_file": str(RAW.relative_to(ROOT)),
            "raw_locator": f"CSV line {row['raw_csv_line']};REF_AREA={row['REF_AREA']};FREQ=A;COMMODITY={row['COMMODITY']};MEASURE={measure};UNIT_MEASURE={row['UNIT_MEASURE']};VERSION_ID={row['VERSION_ID']};TIME_PERIOD={row['TIME_PERIOD']}",
            "notes": "2025-2034 Outlook vintage. OBS_STATUS=A means normal value and does not establish an actual observation. Historical/base series are kept separate from FAOSTAT. Weight conventions differ across measures; monetary retail sales are not measured.",
        }


def main() -> None:
    """Write a canonical-schema CSV to standard output for coordinator integration."""
    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(extract_rows())


if __name__ == "__main__":
    main()
