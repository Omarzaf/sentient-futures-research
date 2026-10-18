"""HCES 2023-24 item codes, recall periods and protein factors for the India table.

Item codes and recall periods come from the FDQ questionnaire printed in
``data/external/hces_2023_24/01_docs/HCES2023-24_Vol_II.pdf`` (sections 5, 6, 7
and summary blocks A1, B1, C1). Protein factors come from NSS Report 594,
"Nutritional Intake in India 2022-23 and 2023-24", Table 2.2 (protein grams per
unit), local copy ``OUTPUTS/Deep Research 2026-10/raw/mospi-report594.pdf``,
SHA-256 f08155b2b9811d236b1a75ccdb48fc60f96efe32bdbabad1413cf7b65017b50b.
"""

from __future__ import annotations

import math

__all__ = [
    "DAYS_PER_MONTH",
    "EXCLUDED_EXPENDITURE_CODES",
    "GROUPS",
    "GROUP_LEVEL",
    "GROUP_UNITS",
    "NOT_REPORTED_CODE",
    "PROTEIN_G_PER_KG",
    "PROTEIN_SOURCE",
    "QUANTITY_CODES",
    "RECALL_DAYS",
    "SECTION_RECALL_DAYS",
    "expenditure_recall_days",
]

DAYS_PER_MONTH = 30

# Group name -> HCES item codes. Pulses follow the brief: 140 to 148, 150, 158.
# Item 147 is not printed in the questionnaire and never occurs in the data.
# Free PMGKAY pulses (071) and gram (072) and soya chunks (152) stay outside
# the pulses group.
GROUPS: dict[str, tuple[int, ...]] = {
    "chicken": (195,),
    "mutton": (192,),
    "beef_buffalo": (193,),
    "fish": (191,),
    "pork": (194,),
    "eggs": (190,),
    "milk": (160,),
    "paneer": (3,),
    "pulses": (140, 141, 142, 143, 144, 145, 146, 147, 148, 150, 158),
    "soya": (152,),
    "packaged": (299,),
    "meals_out": (280, 283),
}

# Clean parquet level holding each group: level_05 is FDQ sections 5 and 6,
# level_06 is FDQ section 7 (served and packaged processed food).
GROUP_LEVEL: dict[str, str] = {
    group: ("06" if group in {"packaged", "meals_out"} else "05") for group in GROUPS
}

# Codes whose quantity enters qty_month and the unit value. Snacks (283) and the
# packaged sub-total (299) carry value only in the questionnaire and the data.
QUANTITY_CODES: dict[str, tuple[int, ...]] = {
    **GROUPS,
    "packaged": (),
    "meals_out": (280,),
}

# Unit of qty_month for each group (FDQ "*Unit is Kg unless otherwise specified").
GROUP_UNITS: dict[str, str] = {
    **{group: "kg" for group in GROUPS},
    "eggs": "number",
    "milk": "litre",
    "packaged": "none (value only)",
    "meals_out": "cooked meals purchased (number, item 280)",
}

# Recall period in days. FDQ section 5 (cereals, pulses, sugar and salt) uses
# 30 days; sections 6 and 7 use 7 days. Soya chunks (152) sit in section 5.2.
RECALL_DAYS: dict[str, int] = {
    group: (30 if group in {"pulses", "soya"} else 7) for group in GROUPS
}

# Recall period of each summary-block section in level_14 (Vol II blocks A1,
# B1, C1). Item 899 (other consumer taxes and cesses) in section 11.4 uses
# 365 days while the rest of 11.4 uses 30 days; see expenditure_recall_days.
SECTION_RECALL_DAYS: dict[float, int] = {
    **{section: 30 for section in (5.1, 5.2, 5.3)},
    **{section: 7 for section in (6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 7.1, 7.2)},
    8.1: 30,
    9.1: 30,
    9.2: 30,
    10.1: 365,
    10.2: 365,
    10.3: 30,
    11.1: 30,
    11.2: 30,
    11.3: 30,
    11.4: 30,
    **{section: 7 for section in (12.1, 12.2, 12.3)},
    # The clean data stores section as a float, so DGQ 14.10 (jewellery, item
    # 649) reads as 14.1 (personal goods, item 629). Both use 365 days.
    **{
        section: 365
        for section in (13.1, 13.2, 13.3, 14.1, 14.2, 14.3, 14.4, 14.5)
        + (14.6, 14.7, 14.8, 14.9)
    },
}
_ITEM_RECALL_OVERRIDE: dict[int, int] = {899: 365}

# Imputed house and garage rent (CSQ 11.4, item 539). Leaving it out reproduces
# the published all-India MPCE (rural 4,122, urban 6,996 rupees) to the rupee.
EXCLUDED_EXPENDITURE_CODES: frozenset[int] = frozenset({539})

# HCQ Q4.11 and Q4.12 code 0 means "not reported".
NOT_REPORTED_CODE = 0

_REPORT_594 = "NSS Report 594 Table 2.2"

# Protein grams per unit of qty_month: per kg, except per litre for milk, per
# egg for eggs and per cooked meal for meals_out. Packaged food has no factor.
PROTEIN_G_PER_KG: dict[str, float] = {
    "chicken": 259.0,
    "mutton": 203.9,
    "beef_buffalo": 198.2,
    "fish": 232.4,
    "pork": 194.1,
    "eggs": 13.28,
    "milk": 35.7,
    "paneer": 134.0,
    "pulses": 214.55,
    "soya": 258.4,
    "packaged": math.nan,
    "meals_out": 25.0,
}

PROTEIN_SOURCE: dict[str, str] = {
    "chicken": f"{_REPORT_594}, item 195 chicken, 259.0 g per kg",
    "mutton": f"{_REPORT_594}, item 192 goat meat/mutton, 203.9 g per kg",
    "beef_buffalo": f"{_REPORT_594}, item 193 beef/buffalo meat, 198.2 g per kg",
    "fish": f"{_REPORT_594}, item 191 fish, prawn, 232.4 g per kg",
    "pork": f"{_REPORT_594}, item 194 pork, 194.1 g per kg",
    "eggs": f"{_REPORT_594}, item 190 eggs, 13.28 g per egg",
    "milk": f"{_REPORT_594}, item 160 milk: liquid, 35.7 g per litre",
    "paneer": f"{_REPORT_594}, item 003 paneer, 134.0 g per kg",
    "pulses": (
        f"{_REPORT_594}, unweighted mean of items 140 (204.7), 141 (215.5), "
        "142 (187.7), 143 (225.3), 144 (228.7), 145 (219.7), 146 (188.0), "
        "148 (227.3), 150 (224.0) and 158 (224.6) g per kg; item factors span "
        "187.7 to 228.7"
    ),
    "soya": f"{_REPORT_594}, item 152 other pulse products (soya chunks), 258.4 g per kg",
    "packaged": f"none: {_REPORT_594} gives no factor for sub-total item 299",
    "meals_out": (
        f"{_REPORT_594}, item 280 cooked meals purchased, 25 g per meal; "
        "snacks (283) have a per-rupee factor and are not in this per-meal value"
    ),
}


def expenditure_recall_days(section: float, item_code: int) -> int:
    """Return the recall period of one level_14 summary row; raise if unknown."""
    if item_code in _ITEM_RECALL_OVERRIDE:
        return _ITEM_RECALL_OVERRIDE[item_code]
    key = round(float(section), 2)
    if key not in SECTION_RECALL_DAYS:
        raise ValueError(f"no recall period registered for level_14 section {section}")
    return SECTION_RECALL_DAYS[key]
