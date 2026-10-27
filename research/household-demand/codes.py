"""Survey item codes, recall periods and protein factors for the household tables.

India: HCES 2023-24. Pakistan: HIES 2024-25, constants prefixed ``PK_`` (see the
Pakistan section below for its sources).

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
    "FREE_ITEM_CODES",
    "GROUPS",
    "GROUP_LEVEL",
    "GROUP_UNITS",
    "NOT_REPORTED_CODE",
    "PK_CHANNELS",
    "PK_GROUPS",
    "PK_GROUP_UNITS",
    "PK_MARKET_CHANNEL",
    "PK_MONTHS_PER_YEAR",
    "PK_MPCE_PARTS",
    "PK_NOT_COLLECTED",
    "PK_OFFICIAL_STRATA",
    "PK_PART_ITEMS",
    "PK_PART_TOTAL_CODES",
    "PK_PERIODS_PER_YEAR",
    "PK_QUANTITY_CODES",
    "PROTEIN_G_PER_KG",
    "PROTEIN_SOURCE",
    "QUANTITY_CODES",
    "RECALL_DAYS",
    "SECTION_RECALL_DAYS",
    "UNIT_VALUE_CODES",
    "expenditure_recall_days",
    "pk_monthly_factor",
    "pk_part",
]

DAYS_PER_MONTH = 30

# Group name -> HCES item codes. Pulses: 140 to 148, 150, PDS pulses 158 and
# free PMGKAY pulses (071) and gram (072) (ruling R17). Item 147 is not printed
# in the questionnaire and never occurs in the data. Soya chunks (152) stay
# outside the pulses group.
GROUPS: dict[str, tuple[int, ...]] = {
    "chicken": (195,),
    "mutton": (192,),
    "beef_buffalo": (193,),
    "fish": (191,),
    "pork": (194,),
    "eggs": (190,),
    "milk": (160,),
    "paneer": (3,),
    "pulses": (71, 72, 140, 141, 142, 143, 144, 145, 146, 147, 148, 150, 158),
    "soya": (152,),
    "packaged": (299,),
    "meals_out": (280, 283),
}

# Clean parquet level holding each group: level_05 is FDQ sections 5 and 6,
# level_06 is FDQ section 7 (served and packaged processed food).
GROUP_LEVEL: dict[str, str] = {
    group: ("06" if group in {"packaged", "meals_out"} else "05") for group in GROUPS
}

# Codes whose quantity enters qty_month. Snacks (283) and the
# packaged sub-total (299) carry value only in the questionnaire and the data.
QUANTITY_CODES: dict[str, tuple[int, ...]] = {
    **GROUPS,
    "packaged": (),
    "meals_out": (280,),
}

# Codes whose market purchases enter the unit value (ruling R15): purchase is
# cons_total minus cons_home. Pulses leave out PDS 158 and free 071 and 072.
UNIT_VALUE_CODES: dict[str, tuple[int, ...]] = {
    **QUANTITY_CODES,
    "pulses": tuple(c for c in GROUPS["pulses"] if c not in {71, 72, 158}),
}

# Items received free under PMGKAY or state schemes. The questionnaire collects
# no value for them (value is blank on 3,055 of 3,056 rows of 071 and 072), so
# they add 0 rupees to value_month, as in the published MPCE without imputation.
FREE_ITEM_CODES: frozenset[int] = frozenset({71, 72})

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
    "pulses": 214.31,
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
        f"{_REPORT_594}, unweighted mean of items 071 (224.6), 072 (201.6), "
        "140 (204.7), 141 (215.5), 142 (187.7), 143 (225.3), 144 (228.7), "
        "145 (219.7), 146 (188.0), 148 (227.3), 150 (224.0) and 158 (224.6) "
        "g per kg, 214.31; item factors span 187.7 to 228.7"
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


# ---------------------------------------------------------------------------
# Pakistan: HIES 2024-25 (PBS), section 6 household consumption expenditure.
#
# Sources, local copies in ``OUTPUTS/Deep Research 2026-10/raw/`` (hashes in
# ``research/protein-markets-2026/reproduce_pakistan.py`` RAW_FILES):
# - Manual of Instructions HIES 2024-25 (pbs-manual.pdf), section 6, printed
#   pp. 90 to 93: five parts and their reference periods; channel definitions.
# - Female questionnaire (pbs-female-questionnaire.pdf), PDF pp. 19 to 24,
#   section 6-F parts A and B: item codes, units and column headings.
# - Manual printed p. 142, balance sheet step 2: part A totals are multiplied
#   by 26 and part B and C totals by 12 to annualise; parts D and E are annual.
# The coding scheme workbook (pbs-coding-scheme.xlsx) lists geography (PR code
# positions I to IV), not item codes; item labels come from the questionnaire
# and the Stata value labels of ``itc``.
# ---------------------------------------------------------------------------

# Channels (columns) of every section 6 row, questionnaire PDF p. 19 notes 1
# and 2 and manual printed pp. 91 to 93: q1/v1 "paid and consumed" (cash,
# credit or barter; cols 1 and 2), q2/v2 wages and salaries in kind (cols 3
# and 4), q3/v3 own produced and consumed (cols 5 and 6), q4/v4 received from
# assistance, gifts, dowry or inheritance (cols 7 and 8). Values are market
# values in whole rupees. Quantities are consumed (not purchased) amounts.
PK_CHANNELS: tuple[tuple[str, str, str], ...] = (
    ("q1", "v1", "paid and consumed"),
    ("q2", "v2", "wages and salaries in kind"),
    ("q3", "v3", "own produced and consumed"),
    ("q4", "v4", "assistance, gifts, dowry, inheritance"),
)
PK_MARKET_CHANNEL: tuple[str, str] = ("q1", "v1")

PK_MONTHS_PER_YEAR = 12

# Part -> reference periods per year (manual printed p. 142): part A covers
# the last 14 days (26 periods), parts B and C the last month (12), parts D
# and E the last year (1). Monthly value = reported value * periods / 12.
PK_PERIODS_PER_YEAR: dict[str, int] = {"A": 26, "B": 12, "C": 12, "D": 1, "E": 1}

# Recorded part totals (sec_6a rows): 1000 part A, 2000 part B, 4000 part C,
# 5000 part D, 6000 part E. They are enumerator sums of the item rows and are
# left out of every item or MPCE sum.
PK_PART_TOTAL_CODES: dict[str, int] = {
    "A": 1000,
    "B": 2000,
    "C": 4000,
    "D": 5000,
    "E": 6000,
}


def _codes(*spans: tuple[int, int] | int) -> tuple[int, ...]:
    """Expand inclusive (first, last) spans and single codes into a code tuple."""
    out: list[int] = []
    for span in spans:
        if isinstance(span, tuple):
            out.extend(range(span[0], span[1] + 1))
        else:
            out.append(span)
    return tuple(out)


# Item codes of each part. Parts A and B are printed in the female
# questionnaire (PDF pp. 19 to 24). Parts C, D and E come from the male
# questionnaire, which is not held locally; their membership was read from the
# recorded part totals: each item's per-household value regresses on the 4000,
# 5000 or 6000 total with coefficient 1.00 for its own part (Task 3 report).
# The manual headings agree: part C (printed p. 101) holds tobacco, water,
# refuse, electricity, gas and fuels; part D runs pp. 102 to 115; part E
# (from p. 116) holds durables.
PK_PART_ITEMS: dict[str, tuple[int, ...]] = {
    "A": _codes(
        (11201, 11204),
        (11301, 11302),
        (11401, 11410),
        (11601, 11613),
        (11701, 11713),
        (11801, 11810),
        (11901, 11908),
        (12201, 12206),
    ),
    "B": _codes(
        (11101, 11120),
        (11501, 11506),
        (12101, 12103),
        (11909, 11912),
        (56101, 56113),
        121101,
        121102,
        121201,
        121202,
        (121301, 121309),
        (110001, 110021),
    ),
    "C": _codes(
        (22001, 22008),
        44101,
        44201,
        45101,
        45102,
        45201,
        45202,
        45301,
        (45401, 45406),
    ),
    "D": _codes(
        (31101, 31103),
        (31201, 31205),
        31401,
        31402,
        32101,
        32102,
        32201,
        41101,
        (42101, 42104),
        (43101, 43103),
        (43201, 43203),
        53101,
        53102,
        (54101, 54103),
        (56201, 56204),
        61101,
        61102,
        (62101, 62104),
        72201,
        72202,
        (72301, 72303),
        72401,
        72402,
        73101,
        73201,
        73202,
        73301,
        73501,
        73502,
        81001,
        (83001, 83003),
        (93101, 93103),
        (94101, 94103),
        (95101, 95104),
        (95201, 95203),
        (101001, 101006),
        (112001, 112003),
        123101,
        (123201, 123203),
        (127001, 127009),
    ),
    "E": _codes(
        (51101, 51106),
        (52201, 52203),
        (53103, 53107),
        (54104, 54107),
        55101,
        55201,
        71101,
        82101,
        (91101, 91103),
        123102,
        123103,
    ),
}

_PK_PART_OF: dict[int, str] = {
    code: part for part, items in PK_PART_ITEMS.items() for code in items
}

# MPCE (ruling R4): no HIES file holds a household total, so monthly household
# consumption expenditure sums the item rows of parts A to D, all four
# channels, each scaled by its part's periods per year / 12, divided by the
# number of household members (roster s1aq10 = 1). Part E (yearly purchases of
# durables) is left out: with it the weighted mean household total is 81,299
# rupees against the published 79,150 (report Table 3.6.A, printed p. 18);
# without it 78,610, and the COICOP shares match report Figure 3 (Task 3 report).
PK_MPCE_PARTS: tuple[str, ...] = ("A", "B", "C", "D")

# Group name -> HIES item codes. Group order follows the India GROUPS, then
# other_poultry (HIES item 11204, no India counterpart). Brief codes: chicken
# 11203, mutton 11202, beef 11201, other poultry 11204, fish 11301, eggs 11409,
# milk 11401 (fresh), pulses 11109 to 11113 and 11115. Milk also holds tetra
# pack milk 11403 (ruling R22; questionnaire PDF p. 19, litres, part A like
# 11401), so its unit value mixes loose and packaged milk. Beans 11114 and
# prawns 11302 are outside the groups. HIES has no pork,
# paneer or soya chunks item, so those groups hold no codes and stay missing.
# Packaged (ruling R6): the HIES items matching the lines of the HCES
# "packaged processed food" block (FDQ 7.2, sub-total 299): breakfast cereals
# and noodles (11107), baby food (11405 formula milk), biscuits (11116), bread
# (11117), cake and pastry (11118, 11119), chips and fried snacks (11120),
# chocolate (11804), jam and jelly (11809), ketchup and mayonnaise (11909),
# pickles (11910) and health drinks (12103). Meals out (110001 to 110021, part
# B) and packaged food carry value only.
PK_GROUPS: dict[str, tuple[int, ...]] = {
    "chicken": (11203,),
    "mutton": (11202,),
    "beef_buffalo": (11201,),
    "fish": (11301,),
    "pork": (),
    "eggs": (11409,),
    "milk": (11401, 11403),
    "paneer": (),
    "pulses": (11109, 11110, 11111, 11112, 11113, 11115),
    "soya": (),
    "packaged": (
        11107,
        11116,
        11117,
        11118,
        11119,
        11120,
        11405,
        11804,
        11809,
        11909,
        11910,
        12103,
    ),
    "meals_out": _codes((110001, 110021)),
    "other_poultry": (11204,),
}

PK_NOT_COLLECTED: tuple[str, ...] = tuple(
    group for group, items in PK_GROUPS.items() if not items
)

# Codes whose quantity enters qty_month and the unit value. Packaged and meals
# out are value only (no quantity column is filled for 110001 to 110021).
PK_QUANTITY_CODES: dict[str, tuple[int, ...]] = {
    **PK_GROUPS,
    "packaged": (),
    "meals_out": (),
}

# Unit of qty_month (questionnaire PDF pp. 19 and 22): kg unless stated.
PK_GROUP_UNITS: dict[str, str] = {
    **{group: "kg" for group in PK_GROUPS},
    "eggs": "number",
    "milk": "litre",
    "packaged": "none (value only)",
    "meals_out": "none (value only)",
    **{group: "not collected in HIES" for group in PK_NOT_COLLECTED},
}

# Official sampling-stratum mapping, (prcode digits 1 to 3, region) ->
# stratum. Empty: the released archive carries no stratum variable and the
# mapping is unresolved (research/protein-markets-2026/DATA-ACCESS.md).
# Households outside this table take a placeholder stratum from
# synthetic/pakistan_strata.csv.
PK_OFFICIAL_STRATA: dict[tuple[int, int], str] = {}


def pk_part(item_code: int) -> str:
    """Return the section 6 part (A to E) of one HIES item; raise if unknown."""
    code = int(item_code)
    if code not in _PK_PART_OF:
        raise ValueError(f"no recall period registered for HIES item {code}")
    return _PK_PART_OF[code]


def pk_monthly_factor(item_code: int) -> tuple[int, int]:
    """Return (periods per year, 12): monthly value = value * periods / 12."""
    return PK_PERIODS_PER_YEAR[pk_part(item_code)], PK_MONTHS_PER_YEAR
