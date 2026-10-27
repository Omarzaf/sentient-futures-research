"""Write the six-household HCES fixture used by ``test_households_india.py``.

Every value is invented for the tests and shaped like the HCES 2023-24 clean
parquet levels 01, 03, 05, 06, 14 and 15. Run from the library root:

    python research/household-demand/tests/fixtures/make_hces_mini.py

The script overwrites ``hces_mini/``. Household roles:

- H1: MPCE example (E1 3000, E2 900 over P2 1, E3 600 a month over P3 1, P1 3),
  chicken on 7-day recall, pulses split over two 30-day items.
- H2: mutton with value and zero quantity; 7-day food section and imputed rent
  in the expenditure summary.
- H3: eggs with home produce 5 inside a total of 12 (purchase 7 for 32 rupees).
- H4: chicken only, so fish is absent; no FDQ summary rows, so MPCE is missing.
- H5: beef with missing quantity; cooked meals with a count and snacks with
  value only; packaged food with value only.
- H6: milk from home produce only, paneer and soya chunks; pulses from the
  market (140), PDS (158) and free PMGKAY (071, no value); religion and caste
  not reported (code 0).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

__all__ = ["write_fixture"]

HERE = Path(__file__).resolve().parent / "hces_mini"
NAN = np.nan
HOUSEHOLDS = ["H1", "H2", "H3", "H4", "H5", "H6"]
MULTIPLIER = {"H1": 1000, "H2": 2000, "H3": 1500, "H4": 1500, "H5": 3000, "H6": 1000}
STATE = {"H1": 9, "H2": 9, "H3": 9, "H4": 27, "H5": 27, "H6": 27}
SIZE = {"H1": 3, "H2": 2, "H3": 4, "H4": 5, "H5": 1, "H6": 2}


def _level_01() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "hhid": HOUSEHOLDS,
            "fsu_serial_no": [10001, 10001, 10002, 20001, 20001, 20002],
            "sector": [1, 1, 2, 1, 2, 2],
            "state": [STATE[h] for h in HOUSEHOLDS],
            "nss_region": [91, 91, 92, 271, 272, 272],
            "district": [1, 1, 2, 3, 4, 4],
            "stratum": [1, 1, 2, 1, 2, 2],
            "sub_stratum": [1, 1, 1, 1, 1, 1],
            "multiplier": [MULTIPLIER[h] for h in HOUSEHOLDS],
        }
    )


def _level_03() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "hhid": HOUSEHOLDS,
            "hh_size": [SIZE[h] for h in HOUSEHOLDS],
            "hoh_religion": [1, 2, 1, 1, 3, 0],
            "caste": [3, 9, 2, 1, 3, 0],
            "multiplier": [MULTIPLIER[h] for h in HOUSEHOLDS],
        }
    )


def _level_15() -> pd.DataFrame:
    rows = []
    for h in HOUSEHOLDS:
        rows.append((h, "H", 3, NAN, NAN))
        for visit, questionnaire in enumerate(["F", "C", "D"], start=1):
            size = 1 if h == "H1" and questionnaire != "F" else SIZE[h]
            rows.append((h, questionnaire, visit, size, 10000.0 * SIZE[h]))
    frame = pd.DataFrame(
        rows,
        columns=[
            "hhid",
            "questionnaire_num",
            "visit",
            "hh_size",
            "hh_usual_cons_exp_mnth",
        ],
    )
    frame["multiplier"] = frame["hhid"].map(MULTIPLIER)
    return frame


def _level_14() -> pd.DataFrame:
    rows = [
        ("H1", "F", 5.1, 129, 3000),
        ("H1", "C", 8.1, 349, 900),
        ("H1", "D", 13.1, 379, 7300),
        ("H2", "F", 5.1, 129, 1400),
        ("H2", "F", 6.5, 199, 700),
        ("H2", "C", 8.1, 349, 600),
        ("H2", "C", 11.4, 539, 5000),
    ]
    for h in ["H3", "H4", "H5", "H6"]:
        if h != "H4":
            rows.append((h, "F", 5.1, 129, 2000))
        rows.append((h, "C", 8.1, 349, 1000))
    frame = pd.DataFrame(
        rows, columns=["hhid", "questionnaire_num", "section", "item_code", "value"]
    )
    frame["multiplier"] = frame["hhid"].map(MULTIPLIER)
    return frame


def _level_05() -> pd.DataFrame:
    rows = [
        ("H1", 195, NAN, NAN, 0.5, 100.0, 1),
        ("H1", 140, NAN, NAN, 1.5, 150.0, 1),
        ("H1", 143, NAN, NAN, 0.5, 60.0, 1),
        ("H2", 192, NAN, NAN, 0.0, 300.0, 1),
        ("H3", 190, 5.0, 40.0, 12.0, 72.0, 3),
        ("H4", 195, NAN, NAN, 1.0, 200.0, 1),
        ("H5", 193, NAN, NAN, NAN, 200.0, 1),
        ("H6", 160, 3.5, 210.0, 3.5, 210.0, 2),
        ("H6", 3, NAN, NAN, 0.25, 100.0, 1),
        ("H6", 152, NAN, NAN, 0.5, 60.0, 1),
        ("H6", 140, NAN, NAN, 1.0, 120.0, 1),
        ("H6", 158, NAN, NAN, 1.0, 30.0, 1),
        ("H6", 71, NAN, NAN, 0.5, NAN, 1),
    ]
    frame = pd.DataFrame(
        rows,
        columns=[
            "hhid",
            "item_code",
            "cons_home_qty",
            "cons_home_value",
            "cons_total_qty",
            "cons_total_value",
            "source",
        ],
    )
    frame.insert(1, "questionnaire_num", "F")
    frame["multiplier"] = frame["hhid"].map(MULTIPLIER)
    return frame


def _level_06() -> pd.DataFrame:
    rows = [
        ("H5", 280, 2.0, 200, 1),
        ("H5", 283, NAN, 50, 1),
        ("H5", 299, NAN, 80, 1),
    ]
    frame = pd.DataFrame(
        rows,
        columns=["hhid", "item_code", "cons_total_qty", "cons_total_value", "source"],
    )
    frame.insert(1, "questionnaire_num", "F")
    frame["multiplier"] = frame["hhid"].map(MULTIPLIER)
    return frame


def write_fixture(directory: Path = HERE) -> None:
    """Write the six fixture levels as parquet files into ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    levels = {
        "01": _level_01(),
        "03": _level_03(),
        "05": _level_05(),
        "06": _level_06(),
        "14": _level_14(),
        "15": _level_15(),
    }
    for level, frame in levels.items():
        frame.to_parquet(directory / f"level_{level}.parquet", index=False)


if __name__ == "__main__":
    write_fixture()
