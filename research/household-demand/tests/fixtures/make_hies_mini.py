"""Write the six-household HIES fixture used by ``test_households_pakistan.py``.

Every value is invented for the tests and shaped like the PBS HIES 2024-25
Stata archive: a ZIP holding ``Stata data/section_info.dta``,
``plist_roster.dta``, ``weight.dta`` and ``sec_6a_consum_exp.dta``. Run from
the library root:

    python research/household-demand/tests/fixtures/make_hies_mini.py

The script overwrites ``hies_mini.zip`` (ignored by Git; ``tests/conftest.py``
writes a fresh copy for each test session). Geography codes are real coding-scheme
codes so every PSU maps to a row of ``synthetic/pakistan_strata.csv``.
Household roles (hhcode):

- 1: rural Lahore district (251); chicken paid 1 kg for 700 (14-day part A),
  dal chana 2 kg for 600 (monthly part B), cooked meat bought out for 500
  (value only); recorded part totals 1000 and 2000; one roster person is not
  a household member.
- 2: same PSU; chicken paid 2 kg for 1,400 plus 1 kg as wages in kind for 700;
  moong 2 kg paid for 500 plus 1 kg received as a gift for 250.
- 3: urban Lahore division (250); eggs from own production only; fresh milk
  paid; biscuits (part B) and chocolate (part A) as packaged food.
- 4: urban Karachi division (350); other poultry received as a gift with value
  and no quantity; chicken paid; electricity (part C, monthly), garments
  (part D, yearly) and a refrigerator (part E, yearly durable).
- 5: rural Peshawar district (142); fish paid; beef paid and own produced;
  masoor from own production only.
- 6: rural Quetta district (411); no consumption rows.
"""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["write_fixture"]

HERE = Path(__file__).resolve().parent / "hies_mini.zip"
NAN = np.nan
STAMP = datetime(2026, 10, 18)

HOUSEHOLDS = {
    # hhcode: (prcode, province, region, members, non-members)
    1: (25111001, 2, 1, 2, 1),
    2: (25111001, 2, 1, 4, 0),
    3: (25022001, 2, 2, 3, 0),
    4: (35023001, 3, 2, 5, 0),
    5: (14211001, 1, 1, 6, 0),
    6: (41111001, 4, 1, 1, 0),
}
WEIGHTS = {25111001: 1000.0, 25022001: 500.0, 35023001: 2000.0}
WEIGHTS |= {14211001: 800.0, 41111001: 600.0}

# (hhcode, itc, q1, v1, q2, v2, q3, v3, q4, v4)
ITEMS = [
    (1, 11203, 1.0, 700, NAN, NAN, NAN, NAN, NAN, NAN),
    (1, 11110, 2.0, 600, NAN, NAN, NAN, NAN, NAN, NAN),
    (1, 110001, NAN, 500, NAN, NAN, NAN, NAN, NAN, NAN),
    (1, 1000, NAN, 700, NAN, NAN, NAN, NAN, NAN, NAN),
    (1, 2000, NAN, 1100, NAN, NAN, NAN, NAN, NAN, NAN),
    (2, 11203, 2.0, 1400, 1.0, 700, NAN, NAN, NAN, NAN),
    (2, 11112, 2.0, 500, NAN, NAN, NAN, NAN, 1.0, 250),
    (3, 11409, NAN, NAN, NAN, NAN, 10.0, 200, NAN, NAN),
    (3, 11401, 7.0, 1400, NAN, NAN, NAN, NAN, NAN, NAN),
    (3, 11116, 1.0, 300, NAN, NAN, NAN, NAN, NAN, NAN),
    (3, 11804, 0.2, 140, NAN, NAN, NAN, NAN, NAN, NAN),
    (4, 11204, NAN, NAN, NAN, NAN, NAN, NAN, NAN, 300),
    (4, 11203, 1.0, 650, NAN, NAN, NAN, NAN, NAN, NAN),
    (4, 45101, NAN, 3000, NAN, NAN, NAN, NAN, NAN, NAN),
    (4, 31201, NAN, 12000, NAN, NAN, NAN, NAN, NAN, NAN),
    (4, 53103, NAN, 24000, NAN, NAN, NAN, NAN, NAN, NAN),
    (5, 11301, 1.0, 800, NAN, NAN, NAN, NAN, NAN, NAN),
    (5, 11201, 0.5, 500, NAN, NAN, 1.0, 1000, NAN, NAN),
    (5, 11113, NAN, NAN, NAN, NAN, 1.0, 300, NAN, NAN),
]


def _section_info() -> pd.DataFrame:
    rows = [
        {
            "prcode": prcode,
            "hhno": hhcode,
            "province": province,
            "region": region,
            "fstatus": 1,
            "hhcode": float(hhcode),
        }
        for hhcode, (prcode, province, region, _, _) in HOUSEHOLDS.items()
    ]
    return pd.DataFrame(rows).astype(
        {
            "prcode": "int32",
            "hhno": "int16",
            "province": "int8",
            "region": "int8",
            "fstatus": "int8",
        }
    )


def _roster() -> pd.DataFrame:
    rows = []
    for hhcode, (prcode, province, region, members, others) in HOUSEHOLDS.items():
        for idc in range(1, members + others + 1):
            rows.append(
                {
                    "prcode": prcode,
                    "hhno": hhcode,
                    "idc": idc,
                    "province": province,
                    "region": region,
                    "s1aq10": 1 if idc <= members else 2,
                    "hhcode": float(hhcode),
                }
            )
    return pd.DataFrame(rows).astype(
        {
            "prcode": "int32",
            "hhno": "int16",
            "idc": "int16",
            "province": "int8",
            "region": "int8",
            "s1aq10": "int8",
        }
    )


def _weight() -> pd.DataFrame:
    return pd.DataFrame(
        {"prcode": list(WEIGHTS), "weight": list(WEIGHTS.values())}
    ).astype({"prcode": "int32", "weight": "float32"})


def _consumption() -> pd.DataFrame:
    columns = ["hhcode", "itc", "q1", "v1", "q2", "v2", "q3", "v3", "q4", "v4"]
    items = pd.DataFrame(ITEMS, columns=columns)
    geo = pd.DataFrame(
        [
            {"hhcode": h, "prcode": p, "province": pr, "region": r}
            for h, (p, pr, r, _, _) in HOUSEHOLDS.items()
        ]
    )
    frame = items.merge(geo, on="hhcode", validate="many_to_one")
    frame = frame.assign(
        hhno=frame["hhcode"],
        quater=1,
        pp=1.0,
        unit=NAN,
        hhcode=frame["hhcode"].astype(float),
    )
    ordered = ["prcode", "hhno", "province", "region", "quater", "itc", "pp", "unit"]
    ordered += ["q1", "v1", "q2", "v2", "q3", "v3", "q4", "v4", "hhcode"]
    return frame[ordered].astype(
        {
            "prcode": "int32",
            "hhno": "int16",
            "province": "int8",
            "region": "int8",
            "quater": "int8",
            "itc": "int32",
            "q2": "float32",
            "q3": "float32",
            "q4": "float32",
        }
    )


def _dta_bytes(frame: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    frame.to_stata(buffer, write_index=False, version=118, time_stamp=STAMP)
    return buffer.getvalue()


def write_fixture(path: Path = HERE) -> Path:
    """Write the fixture ZIP and return its path."""
    tables = {
        "section_info": _section_info(),
        "plist_roster": _roster(),
        "weight": _weight(),
        "sec_6a_consum_exp": _consumption(),
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, frame in tables.items():
            info = zipfile.ZipInfo(f"Stata data/{name}.dta", (2026, 10, 18, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, _dta_bytes(frame))
    return path


if __name__ == "__main__":
    print(write_fixture())
