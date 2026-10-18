"""Build the Pakistan household protein table from the HIES 2024-25 Stata archive.

One row per household with the India table's columns (``households_india``),
``mpce_pkr`` in place of ``mpce_inr``, and ``province``, ``region`` and
``prcode`` kept from the release. ``state`` is the province code, ``sector``
the region (1 rural, 2 urban), ``psu`` the PR code and ``multiplier`` the PSU
weight from ``weight.dta`` (rulings R2, R3). HIES holds no religion, caste or
sub-stratum variable, so those columns are missing for every household.

Section 6 rows carry four channels (``codes.PK_CHANNELS``): paid, wages in
kind, own produced and gifts. ``qty_month_`` and ``value_month_`` sum all four
channels; a channel with a value and no quantity makes the row quantity
missing. The unit value uses the paid channel only (q1, v1; ruling R15
analogue) and is missing unless the paid quantity is positive. Monthly values
follow PBS's annualisation (manual printed p. 142): part A (14 days) times
26 / 12, parts B and C (last month) as reported, parts D and E (last year)
divided by 12. An item a household did not report stays missing.

MPCE (ruling R4): no file holds a PBS household total, so the monthly
household total sums the item rows of parts A to D, all channels, scaled by
part, and divides by the number of household members (roster s1aq10 = 1).
Recorded part totals (1000 to 6000) and part E durables are left out; see
``codes.PK_MPCE_PARTS``. A household with no part A to D rows gets missing
MPCE and ``mpce_status`` "MISSING_EXPENDITURE"; all others are "OK".

Strata: the release has no stratum variable and the official mapping is
unresolved (``research/protein-markets-2026/DATA-ACCESS.md``). A household
whose (PR code digits 1 to 3, region) sits in ``codes.PK_OFFICIAL_STRATA`` is
RESOLVED; every other household takes the placeholder stratum of its rural
district or urban division from ``synthetic/pakistan_strata.csv`` and is
flagged with the placeholder status.

Household rows are written outside the repository. The repository receives
weighted province-level means only, with cells under 30 unweighted households
set to null (R16) and placeholder strata counted, never flagged (R1).

Run from the library root:

    python research/household-demand/households_pakistan.py \\
        --zip "../OUTPUTS/Deep Research 2026-10/raw/pbs-stata-2024-25.zip" \\
        --out "../OUTPUTS/Household Demand 2026-10/work/pakistan_households.parquet" \\
        --summary outputs/pakistan_summary.json

Rebuild the placeholder strata table from the PBS coding scheme:

    python research/household-demand/households_pakistan.py \\
        --write-strata "../OUTPUTS/Deep Research 2026-10/raw/pbs-coding-scheme.xlsx"
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree

import codes
import households_india as hi
import numpy as np
import pandas as pd

__all__ = [
    "BASE_COLUMNS",
    "LIBRARY_ROOT",
    "PLACEHOLDER_STATUS",
    "STRATA_PATH",
    "build_pakistan_households",
    "main",
    "province_summary",
    "read_tables",
    "run_log",
    "strata_table",
]

HERE = Path(__file__).resolve().parent
LIBRARY_ROOT = HERE.parents[1]
STRATA_PATH = HERE / "synthetic" / "pakistan_strata.csv"
REPRODUCE_PATH = (
    LIBRARY_ROOT / "research" / "protein-markets-2026" / "reproduce_pakistan.py"
)

PLACEHOLDER_STATUS = "SYNTHETIC"
RESOLVED_STATUS = "RESOLVED"

BASE_COLUMNS: tuple[str, ...] = (
    "hhid",
    "state",
    "district",
    "sector",
    "multiplier",
    "hh_size",
    "religion",
    "caste",
    "mpce_pkr",
    "mpce_local",
    "mpce_status",
    "currency",
    "psu",
    "stratum",
    "sub_stratum",
    "stratum_status",
    "province",
    "region",
    "prcode",
)
GROUP_KINDS = hi.GROUP_KINDS

# Published HIES 2024-25 averages, report Tables 3.6.A and 3.6.B (printed
# p. 18 and 19), rupees per month. Run-log comparison only.
PUBLISHED_HOUSEHOLD_PKR = {"total": 79150, "urban": 95533, "rural": 67894}
PUBLISHED_PER_CAPITA_PKR = {"total": 13240, "urban": 16795, "rural": 10991}


def _load_reproduce():
    """Import reproduce_pakistan.py by path (its folder name has a hyphen)."""
    spec = importlib.util.spec_from_file_location("reproduce_pakistan", REPRODUCE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {REPRODUCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RP = _load_reproduce()
QUANTITY: list[str] = list(RP.QUANTITY)
VALUE: list[str] = list(RP.VALUE)

# Same members, columns and reader settings as reproduce_pakistan.reproduce_pakistan.
MEMBERS: dict[str, list[str]] = {
    "section_info": ["hhcode", "prcode", "province", "region"],
    "plist_roster": ["hhcode", "idc", "s1aq10"],
    "weight": ["prcode", "weight"],
    "sec_6a_consum_exp": ["hhcode", "itc", *QUANTITY, *VALUE],
}


def read_tables(zip_path: Path) -> dict[str, pd.DataFrame]:
    """Read the four Stata members in memory; nothing is extracted to disk."""
    tables = {}
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupted PBS ZIP member")
        for name, selected in MEMBERS.items():
            with pd.read_stata(
                io.BytesIO(archive.read(f"Stata data/{name}.dta")),
                iterator=True,
                convert_categoricals=False,
                columns=selected,
            ) as reader:
                tables[name] = reader.read()
    return tables


def _integer_ids(values: pd.Series, name: str) -> pd.Series:
    """Return integral identifiers as int64; raise on missing or fractional values."""
    as_float = values.astype(float)
    if as_float.isna().any() or not np.equal(np.mod(as_float, 1), 0).all():
        raise ValueError(f"missing or non-integral {name}")
    return as_float.astype("int64")


def _strata_lookup(path: Path) -> pd.DataFrame:
    """Read the placeholder strata table and check its keys and status."""
    strata = pd.read_csv(path)
    needed = {"geo_code", "region", "stratum", "status"}
    if not needed <= set(strata.columns):
        raise ValueError(
            f"strata table lacks columns {sorted(needed - set(strata.columns))}"
        )
    if strata.duplicated(["geo_code", "region"]).any():
        raise ValueError("duplicate (geo_code, region) rows in the strata table")
    if set(strata["status"]) != {PLACEHOLDER_STATUS}:
        raise ValueError("every strata table row must carry the placeholder status")
    return strata


def _households(tables: dict[str, pd.DataFrame], strata_path: Path) -> pd.DataFrame:
    """Join section info, roster members, PSU weights and strata; one row per household."""
    info = tables["section_info"].copy()
    roster = tables["plist_roster"]
    weights = tables["weight"]
    RP._unique(info, ["hhcode"], "section_info")
    RP._unique(roster, ["hhcode", "idc"], "plist_roster")
    RP._unique(weights, ["prcode"], "weight")
    if set(info["hhcode"]) != set(roster["hhcode"]):
        raise ValueError("Household information and roster key sets differ")
    if roster["s1aq10"].isna().any() or not roster["s1aq10"].isin([1, 2]).all():
        raise ValueError("Unresolved household-membership code")
    if not info["region"].isin([1, 2]).all():
        raise ValueError("Unresolved rural/urban code")
    if info["province"].isna().any():
        raise ValueError("missing province code")
    members = roster.loc[roster["s1aq10"].eq(1)].groupby("hhcode").size()
    info["hh_size"] = info["hhcode"].map(members).fillna(0).astype(int)
    if not info["hh_size"].gt(0).all():
        raise ValueError("household with no confirmed members")
    info = info.merge(weights, on="prcode", how="left", validate="many_to_one")
    if info["weight"].isna().any() or not info["weight"].gt(0).all():
        raise ValueError("missing or non-positive PSU weight")
    info["hhid"] = _integer_ids(info["hhcode"], "hhcode")
    info["prcode"] = _integer_ids(info["prcode"], "prcode")
    text = info["prcode"].astype(str)
    if not text.str.len().eq(8).all():
        raise ValueError("PR code is not 8 digits")
    if not text.str[3].astype(int).eq(info["region"]).all():
        raise ValueError("PR code digit 4 differs from the region code")
    info["geo_code"] = info["prcode"] // 100_000

    strata = _strata_lookup(strata_path)
    info = info.merge(
        strata[["geo_code", "region", "stratum"]],
        on=["geo_code", "region"],
        how="left",
        validate="many_to_one",
    )
    if info["stratum"].isna().any():
        raise ValueError("PR code geography absent from the placeholder strata table")
    info["stratum_status"] = PLACEHOLDER_STATUS
    official = pd.Series(
        [
            codes.PK_OFFICIAL_STRATA.get((g, r))
            for g, r in zip(info["geo_code"], info["region"])
        ],
        index=info.index,
        dtype=object,
    )
    resolved = official.notna()
    info.loc[resolved, "stratum"] = official[resolved]
    info.loc[resolved, "stratum_status"] = RESOLVED_STATUS
    return info


def _channel_sum(
    rows: pd.DataFrame, columns: list[str], present: pd.DataFrame
) -> pd.Series:
    """Sum used channels; missing when a used channel lacks this field."""
    values = rows[columns].astype(float).to_numpy()
    used = present.to_numpy()
    incomplete = (used & np.isnan(values)).any(axis=1)
    total = np.where(used, np.nan_to_num(values), 0.0).sum(axis=1)
    total = np.where(incomplete | ~used.any(axis=1), np.nan, total)
    return pd.Series(total, index=rows.index)


def _items(food: pd.DataFrame, hhids: pd.Index) -> pd.DataFrame:
    """Check item rows and return per-row monthly quantity, value and paid channel."""
    totals = set(codes.PK_PART_TOTAL_CODES.values())
    rows = food.loc[~food["itc"].isin(totals)].copy()
    rows["hhid"] = _integer_ids(rows["hhcode"], "hhcode")
    if rows.duplicated(["hhid", "itc"]).any():
        raise ValueError("duplicate household item rows in sec_6a would double count")
    if not set(rows["hhid"]) <= set(hhids):
        raise ValueError("sec_6a holds households absent from section_info")
    for column in (*QUANTITY, *VALUE):
        rows[column] = rows[column].astype(float)
        if rows[column].lt(0).any():
            raise ValueError(f"negative {column} in sec_6a")
        if np.isinf(rows[column]).any():
            raise ValueError(f"non-finite {column} in sec_6a")
    item_codes = pd.Series(rows["itc"].unique())
    parts = dict(zip(item_codes, item_codes.map(codes.pk_part)))
    rows["part"] = rows["itc"].map(parts)
    rows["periods"] = rows["part"].map(codes.PK_PERIODS_PER_YEAR)

    present = pd.DataFrame(
        {q: rows[q].notna() | rows[v].notna() for q, v in zip(QUANTITY, VALUE)}
    )
    no_value = pd.DataFrame(
        {q: rows[q].gt(0) & rows[v].isna() for q, v in zip(QUANTITY, VALUE)}
    )
    if no_value.to_numpy().any():
        raise ValueError("quantity without value in a sec_6a channel")
    rows["qty"] = _channel_sum(rows, QUANTITY, present)
    value_present = present.rename(columns=dict(zip(QUANTITY, VALUE)))
    rows["value"] = _channel_sum(rows, VALUE, value_present)
    if rows["value"].isna().any():
        raise ValueError("sec_6a row without a complete value would bias MPCE")
    rows["qty_m"] = rows["qty"] * rows["periods"] / codes.PK_MONTHS_PER_YEAR
    rows["value_m"] = rows["value"] * rows["periods"] / codes.PK_MONTHS_PER_YEAR

    paid_q, paid_v = codes.PK_MARKET_CHANNEL
    paid_used = present[paid_q]
    rows["paid_qty"] = rows[paid_q].where(paid_used, 0.0)
    rows["paid_value"] = rows[paid_v].where(paid_used, 0.0)
    return rows


def _group_columns(rows: pd.DataFrame, group: str, hhids: pd.Index) -> pd.DataFrame:
    """Return monthly quantity, monthly value and paid unit value for one group."""
    mine = rows.loc[rows["itc"].isin(codes.PK_GROUPS[group])]
    value = hi._sum_or_missing(mine, "value_m").reindex(hhids).astype(float)
    counted = mine.loc[mine["itc"].isin(codes.PK_QUANTITY_CODES[group])]
    if counted["part"].nunique() > 1:
        raise ValueError(f"quantity codes of group {group} span several recall periods")
    qty = hi._sum_or_missing(counted, "qty_m").reindex(hhids).astype(float)
    paid_qty = hi._sum_or_missing(counted, "paid_qty").reindex(hhids).astype(float)
    paid_value = hi._sum_or_missing(counted, "paid_value").reindex(hhids).astype(float)
    unit_value = (paid_value / paid_qty).where(paid_qty.gt(0) & paid_value.notna())
    return pd.DataFrame(
        {
            f"qty_month_{group}": qty,
            f"value_month_{group}": value,
            f"unit_value_{group}": unit_value,
        },
        index=hhids,
    )


def _mpce(rows: pd.DataFrame, households: pd.DataFrame) -> pd.DataFrame:
    """Return monthly household totals by part, MPCE and its status, indexed by hhid."""
    hhids = pd.Index(households["hhid"], name="hhid")
    by_part = (
        rows.groupby(["hhid", "part"])["value_m"]
        .sum(min_count=1)
        .unstack("part")
        .reindex(index=hhids, columns=list(codes.PK_PERIODS_PER_YEAR))
    )
    counted = by_part[list(codes.PK_MPCE_PARTS)]
    absent = counted.isna().all(axis=1)
    total = counted.sum(axis=1, min_count=1)
    size = households.set_index("hhid")["hh_size"].reindex(hhids)
    return pd.DataFrame(
        {
            "total_month": total.mask(absent),
            "total_month_with_durables": (total + by_part["E"].fillna(0.0)).mask(
                absent
            ),
            "mpce_pkr": (total / size).mask(absent),
            "mpce_status": np.where(absent, "MISSING_EXPENDITURE", "OK"),
            **{f"part_{part}": by_part[part] for part in codes.PK_PERIODS_PER_YEAR},
        },
        index=hhids,
    )


def _build(
    zip_path: Path, strata_path: Path = STRATA_PATH
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    """Return the household table, the MPCE frame and the raw tables."""
    tables = read_tables(zip_path)
    households = _households(tables, strata_path)
    hhids = pd.Index(households["hhid"], name="hhid")
    rows = _items(tables["sec_6a_consum_exp"], hhids)
    mpce = _mpce(rows, households)
    groups = pd.concat(
        [_group_columns(rows, group, hhids) for group in codes.PK_GROUPS], axis=1
    )
    base = households.set_index("hhid")
    missing_code = pd.Series(pd.NA, index=hhids, dtype="Int64")
    table = pd.DataFrame(
        {
            "state": base["province"].astype("int64"),
            "district": base["geo_code"].where(base["region"].eq(1)).astype("Int64"),
            "sector": base["region"].astype("int64"),
            "multiplier": base["weight"].astype(float),
            "hh_size": base["hh_size"].astype("int64"),
            "religion": missing_code,
            "caste": missing_code,
            "mpce_pkr": mpce["mpce_pkr"],
            "mpce_local": mpce["mpce_pkr"],
            "mpce_status": mpce["mpce_status"],
            "currency": "PKR",
            "psu": base["prcode"],
            "stratum": base["stratum"].astype(str),
            "sub_stratum": missing_code,
            "stratum_status": base["stratum_status"],
            "province": base["province"].astype("int64"),
            "region": base["region"].astype("int64"),
            "prcode": base["prcode"],
        },
        index=hhids,
    )
    table = pd.concat([table, groups], axis=1).reset_index()
    ordered = list(BASE_COLUMNS) + [
        f"{kind}_{group}" for group in codes.PK_GROUPS for kind in GROUP_KINDS
    ]
    tables["_rows"] = rows
    tables["_households"] = households
    return table[ordered], mpce, tables


def build_pakistan_households(
    zip_path: Path, strata_path: Path = STRATA_PATH
) -> pd.DataFrame:
    """Return one row per household with MPCE and monthly protein-group columns."""
    return _build(Path(zip_path), Path(strata_path))[0]


def province_summary(
    table: pd.DataFrame, min_households: int = hi.MIN_CELL_HOUSEHOLDS
) -> dict:
    """Return weighted province-level means; no household row or sub-province cell.

    Every cell carries its unweighted household count. A cell with fewer than
    ``min_households`` households has a null value and keeps its count (R16).
    Households on placeholder strata are counted, not flagged (R1).
    """
    provinces = {}
    for province, frame in table.groupby("province", sort=True):
        weight = frame["multiplier"].astype(float)
        groups = {}
        for group in codes.PK_GROUPS:
            reported = frame[f"value_month_{group}"].notna()
            n_reporting = int(reported.sum())
            share = round(float(weight[reported].sum() / weight.sum()), 6)
            value, n_value = hi._cell(
                frame[f"value_month_{group}"], weight, min_households
            )
            qty, n_qty = hi._cell(frame[f"qty_month_{group}"], weight, min_households)
            unit, n_unit = hi._cell(
                frame[f"unit_value_{group}"], weight, min_households
            )
            groups[group] = {
                "n_reporting": n_reporting,
                "reporting_share": share if n_reporting >= min_households else None,
                "n_value": n_value,
                "mean_value_month_pkr_reporting": value,
                "n_qty": n_qty,
                "mean_qty_month_reporting": qty,
                "n_unit_value": n_unit,
                "mean_unit_value_pkr": unit,
            }
        persons = weight * frame["hh_size"]
        mpce, n_mpce = hi._cell(frame["mpce_pkr"], persons, min_households)
        provinces[str(int(province))] = {
            "n_households": len(frame),
            "n_psus": int(frame["psu"].nunique()),
            "n_mpce": n_mpce,
            "mean_mpce_pkr": mpce,
            "groups": groups,
        }
    placeholder = table["stratum_status"].ne(RESOLVED_STATUS)
    return {
        "status": "DIAGNOSTIC",
        "source": (
            "PBS HIES 2024-25 Stata archive: section_info, plist_roster, weight, "
            "sec_6a_consum_exp"
        ),
        "weight": "PSU weight from weight.dta",
        "province_codes": {
            "1": "Khyber Pakhtunkhwa",
            "2": "Punjab",
            "3": "Sindh",
            "4": "Balochistan",
        },
        "province_note": (
            "province 2 includes Islamabad Capital Territory PSUs (PR code 61x); "
            "AJK and Gilgit-Baltistan are absent from the archive"
        ),
        "min_cell_households": min_households,
        "suppression": (
            "a cell with fewer than min_cell_households unweighted households is null; "
            "its unweighted count n_* is kept (ruling R16)"
        ),
        "mean_mpce_definition": (
            "person-weighted over households with mpce_status OK: "
            "sum(w * MPCE * hh_size) / sum(w * hh_size); MPCE sums section 6 parts A to D "
            "(all channels) per member, part E durables left out"
        ),
        "group_mean_definition": (
            "household-weighted means among households reporting the group; "
            "reporting_share is the weighted share reporting it; unreported items are not zero-filled"
        ),
        "unit_value_definition": "paid and consumed channel only (q1, v1; ruling R15 analogue)",
        "monthly_scaling": "part A (14 days) x 26 / 12; parts B and C as reported; parts D and E / 12",
        "units": {group: codes.PK_GROUP_UNITS[group] for group in codes.PK_GROUPS},
        "not_collected_groups": list(codes.PK_NOT_COLLECTED),
        "households": len(table),
        "psus": int(table["psu"].nunique()),
        "placeholder_stratum_households": int(placeholder.sum()),
        "resolved_stratum_households": int((~placeholder).sum()),
        "provinces": provinces,
    }


def _weighted(values: pd.Series, weights: pd.Series, denominator: pd.Series) -> float:
    """Return sum(w * value) / sum(w * denominator) over rows with a value."""
    keep = values.notna()
    return float(
        (values[keep] * weights[keep]).sum() / (denominator[keep] * weights[keep]).sum()
    )


def run_log(
    table: pd.DataFrame, mpce: pd.DataFrame, tables: dict[str, pd.DataFrame]
) -> dict:
    """Return national diagnostics: counts, MPCE against published means, totals check."""
    base = table.set_index("hhid")
    weight = base["multiplier"]
    size = base["hh_size"].astype(float)
    ones = pd.Series(1.0, index=base.index)
    comparison = {}
    for name, region in (("total", None), ("urban", 2), ("rural", 1)):
        mask = (
            base["region"].eq(region) if region else pd.Series(True, index=base.index)
        )
        entry = {}
        for label, column in (
            ("parts_a_to_d", "total_month"),
            ("with_part_e_durables", "total_month_with_durables"),
        ):
            values = mpce[column][mask]
            entry[label] = {
                "household_pkr": round(_weighted(values, weight[mask], ones[mask]), 1),
                "per_capita_pkr": round(_weighted(values, weight[mask], size[mask]), 1),
            }
        entry["published_household_pkr"] = PUBLISHED_HOUSEHOLD_PKR[name]
        entry["published_per_capita_pkr"] = PUBLISHED_PER_CAPITA_PKR[name]
        comparison[name] = entry

    food = tables["sec_6a_consum_exp"]
    rows = tables["_rows"]
    quantity_codes = {c for items in codes.PK_QUANTITY_CODES.values() for c in items}
    agreement = {}
    for part, code in codes.PK_PART_TOTAL_CODES.items():
        recorded = (
            food.loc[food["itc"].eq(code)]
            .assign(hhid=lambda f: _integer_ids(f["hhcode"], "hhcode"))
            .set_index("hhid")[VALUE]
            .sum(axis=1)
        )
        summed = rows.loc[rows["part"].eq(part)].groupby("hhid")["value"].sum()
        joined = pd.concat(
            [recorded.rename("recorded"), summed.rename("items")], axis=1
        ).fillna(0.0)
        agreement[part] = {
            "households_with_recorded_total": len(recorded),
            "share_within_1_rupee": round(
                float((joined["recorded"] - joined["items"]).abs().lt(1).mean()), 4
            ),
        }

    households = tables["_households"]
    placeholder = households["stratum_status"].ne(RESOLVED_STATUS)
    psus_per_stratum = (
        households.loc[placeholder].groupby("stratum")["prcode"].nunique()
    )
    return {
        "households": len(table),
        "psus": int(table["psu"].nunique()),
        "households_by_province": {
            str(k): int(v)
            for k, v in table["province"].value_counts().sort_index().items()
        },
        "islamabad_psus_in_province_2": int(
            households.loc[households["geo_code"].between(610, 619), "prcode"].nunique()
        ),
        "placeholder_stratum_households": int(placeholder.sum()),
        "placeholder_strata": int(psus_per_stratum.size),
        "placeholder_strata_with_one_psu": int(psus_per_stratum.eq(1).sum()),
        "mpce_comparison_with_report_tables_3_6": comparison,
        "recorded_part_total_agreement": agreement,
        "households_mpce_status": {
            status: int(count)
            for status, count in table["mpce_status"]
            .value_counts()
            .sort_index()
            .items()
        },
        "group_quantity_rows_with_value_but_no_quantity": int(
            (
                rows["itc"].isin(quantity_codes)
                & rows["qty"].isna()
                & rows["value"].notna()
            ).sum()
        ),
        "households_reporting_group": {
            group: int(table[f"value_month_{group}"].notna().sum())
            for group in codes.PK_GROUPS
        },
        "households_with_unit_value": {
            group: int(table[f"unit_value_{group}"].notna().sum())
            for group in codes.PK_GROUPS
        },
    }


def _shared_strings(archive: zipfile.ZipFile, ns: dict[str, str]) -> list[str]:
    """Return the workbook's shared strings."""
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    tag = f"{{{ns['m']}}}t"
    return [
        "".join(t.text or "" for t in item.iter(tag))
        for item in root.findall("m:si", ns)
    ]


def _sheet_rows(path: Path) -> dict[str, list[list[str]]]:
    """Read every sheet of an .xlsx file as rows of cell text (standard library only)."""
    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    with zipfile.ZipFile(path) as archive:
        strings = _shared_strings(archive, ns)
        book = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        links = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {link.attrib["Id"]: link.attrib["Target"] for link in links}
        sheets = {}
        for sheet in book.find("m:sheets", ns):
            target = targets[sheet.attrib[f"{{{ns['r']}}}id"]].lstrip("/")
            target = target if target.startswith("xl/") else f"xl/{target}"
            root = ElementTree.fromstring(archive.read(target))
            rows = []
            for row in root.find("m:sheetData", ns):
                cells = []
                for cell in row:
                    value = cell.find("m:v", ns)
                    if value is None:
                        continue
                    text = value.text or ""
                    cells.append(
                        strings[int(text)] if cell.attrib.get("t") == "s" else text
                    )
                if cells:
                    rows.append(cells)
            sheets[sheet.attrib["name"]] = rows
    return sheets


def strata_table(coding_scheme: Path) -> pd.DataFrame:
    """Return one placeholder stratum per rural district and urban division.

    Rows come from the PBS coding scheme (PR code positions I to III with the
    region in position IV). The geography is documented; treating it as the
    sampling stratum is the invented part, so every row carries the
    placeholder status.
    """
    sheets = _sheet_rows(coding_scheme)
    records = []
    for name, rows in sheets.items():
        urban = name.lower().startswith("urban")
        for cells in rows:
            if not cells[-1].strip().isdigit() or not cells[-2].strip().isdigit():
                continue
            region = int(cells[-1])
            if region != (2 if urban else 1):
                raise ValueError(f"region {region} on coding sheet {name!r}")
            geo_code = int(cells[-2])
            records.append(
                {
                    "geo_code": geo_code,
                    "region": region,
                    "geo_level": "division" if urban else "district",
                    "province_name": cells[0].strip(),
                    "division_name": cells[1].strip(),
                    "district_name": "" if urban else cells[2].strip(),
                    "stratum": f"PK-{geo_code:03d}-{region}",
                    "status": PLACEHOLDER_STATUS,
                    "basis": (
                        "placeholder: rural district or urban division from PR code "
                        "positions I to IV (pbs-coding-scheme.xlsx); official sampling "
                        "strata unresolved (protein-markets-2026/DATA-ACCESS.md)"
                    ),
                }
            )
    table = (
        pd.DataFrame(records).sort_values(["region", "geo_code"]).reset_index(drop=True)
    )
    if table.duplicated(["geo_code", "region"]).any():
        raise ValueError("duplicate PR code geography in the coding scheme")
    return table


def _sha256(path: Path) -> str:
    """Hash one file in chunks."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point: household rows, province summary and run log."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--zip", help="pbs-stata-2024-25.zip (its folder must hold all six PBS sources)"
    )
    parser.add_argument("--out", help="household parquet path outside the repository")
    parser.add_argument(
        "--summary",
        help="province summary JSON (relative paths resolve against research/household-demand/)",
    )
    parser.add_argument(
        "--log",
        default="logs/pakistan-households-run.json",
        help="run log JSON (relative paths resolve against research/household-demand/)",
    )
    parser.add_argument(
        "--write-strata",
        metavar="CODING_SCHEME",
        help="rebuild synthetic/pakistan_strata.csv from pbs-coding-scheme.xlsx and exit",
    )
    args = parser.parse_args(argv)

    if args.write_strata:
        scheme = Path(args.write_strata)
        RP.verify_raw(scheme.parent)
        table = strata_table(scheme)
        table.to_csv(STRATA_PATH, index=False, lineterminator="\n")
        print(f"strata rows={len(table)} path={STRATA_PATH.relative_to(LIBRARY_ROOT)}")
        return 0

    if not (args.zip and args.out and args.summary):
        parser.error(
            "--zip, --out and --summary are required unless --write-strata is given"
        )
    out = Path(args.out).resolve()
    if out.is_relative_to(LIBRARY_ROOT):
        parser.error(f"household rows must be written outside the repository: {out}")
    summary_path = hi._resolve_here(args.summary)
    log_path = hi._resolve_here(args.log)
    zip_path = Path(args.zip)
    hashes = RP.verify_raw(zip_path.parent)

    table, mpce, tables = _build(zip_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(out, index=False)
    summary = province_summary(table)
    hi._write_json(summary_path, summary)
    log = {
        "status": "DIAGNOSTIC",
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "zip": args.zip,
        "source_sha256": hashes,
        "strata_table": {
            "path": str(STRATA_PATH.relative_to(LIBRARY_ROOT)),
            "sha256": _sha256(STRATA_PATH),
        },
        "household_table": {
            "path": args.out,
            "rows": len(table),
            "sha256": _sha256(out),
        },
        "summary": {
            "path": str(summary_path.relative_to(LIBRARY_ROOT)),
            "sha256": _sha256(summary_path),
        },
        **run_log(table, mpce, tables),
    }
    hi._write_json(log_path, log)
    total = log["mpce_comparison_with_report_tables_3_6"]["total"]
    print(
        f"households={log['households']} psus={log['psus']} "
        f"placeholder_stratum_households={log['placeholder_stratum_households']} "
        f"household_pkr={total['parts_a_to_d']['household_pkr']} "
        f"per_capita_pkr={total['parts_a_to_d']['per_capita_pkr']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
