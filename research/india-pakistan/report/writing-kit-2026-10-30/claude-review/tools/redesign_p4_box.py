"""Move the Pakistan box to Appendix A and recast it around implied capture shares.

Every displayed number is computed from retained files and registered in the
claim register. Requested by Umar on 30 October 2026 after the Claude review.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from pathlib import Path

HANDOFF = Path(__file__).resolve().parents[2]
ROOT = HANDOFF.parents[1]
W = ".worktrees/writing-kit-20261030"
B = W + "/research/india-pakistan"
GRID = B + "/build/pakistan-topdown/pakistan_topdown.csv"
REF = B + "/data/altprotein_proxy_scenarios.csv"
INPUTS = B + "/build/pakistan-topdown/extracted-inputs.json"
FAO = "OUTPUTS/Pakistan-India Data Dashboard/data/raw/faostat_fbs_2025-10-28.zip"
ECON = (
    "OUTPUTS/Pakistan-India Data Dashboard/data/raw/national/"
    "pakistan-economic-survey-2024-25-agriculture.txt"
)
SCRIPT = "OUTPUTS/Codex Handoff 2026-10-30/claude-review/tools/redesign_p4_box.py"
BOX = "kit/pakistan-topdown-box.md"
RESULTS = "kit/06-results.md"
NUMBER = re.compile(
    r"(?<![A-Za-z0-9])[−-]?\d+(?:,\d{3})*(?:\.\d+)?(?:th)?%?(?![A-Za-z0-9])"
)


def rows(path: str) -> list[dict]:
    """Read a CSV relative to the workspace root."""
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def visible(line: str) -> str:
    """Match the kit verifier: drop code spans and keep link labels."""
    line = re.sub(r"`[^`]*`", "", line)
    return re.sub(r"!?\[([^\]]+)\]\(([^\n]+?)\)", r"\1", line)


def fmt(value: float, places: int) -> str:
    """Round for display with thousands separators."""
    return f"{value:,.{places}f}"


grid = rows(GRID)
reference = {r["row_id"]: float(r["value"]) for r in rows(REF)}
inputs = json.loads((ROOT / INPUTS).read_text())
YEARS = ("2026", "2030", "2035")


def conventional(row: dict) -> float:
    """Combined conventional poultry and milk value, million USD."""
    return float(row["poultry_conventional_value_million_usd"]) + float(
        row["milk_equivalent_conventional_value_million_usd"]
    )


def transfer(year: str, stat: str) -> float:
    return reference[f"pakistan_{year}_market_value_{stat}"]


profiles: dict[tuple[str, str, str], float] = {}
for r in grid:
    key = (r["quantity_family"], r["price_profile"], r["comparison_year"])
    profiles.setdefault(key, conventional(r))
assert len({(f, p) for f, p, _ in profiles}) == 18
central = {
    y: profiles[("OECD_poultry_FAO_milk", "official_central_sensitivity", y)]
    for y in YEARS
}
share = {
    (y, s): transfer(y, s) / central[y] * 100 for y in YEARS for s in ("p10", "p90")
}
spread = {
    y: (
        min(transfer(y, "p10") / v * 100 for (_, _, yy), v in profiles.items() if yy == y),
        max(transfer(y, "p90") / v * 100 for (_, _, yy), v in profiles.items() if yy == y),
    )
    for y in YEARS
}
above = sum(
    float(r["combined_capture_million_usd"]) > float(r["transfer_p90_million_usd"])
    for r in grid
)
below = sum(
    float(r["combined_capture_million_usd"]) < float(r["transfer_p10_million_usd"])
    for r in grid
)
assert (len(grid), above, below) == (162, 139, 0)
assert all(0.05 > transfer("2026", "p90") / v * 100 for (_, _, y), v in profiles.items() if y == "2026")
milk_2026 = next(
    float(r["milk_capture_million_usd"])
    for r in grid
    if r["quantity_family"] == "OECD_poultry_FAO_milk"
    and r["price_profile"] == "official_central_sensitivity"
    and r["comparison_year"] == "2026"
    and r["capture_share"] == "0.005000"
)
assert milk_2026 / transfer("2026", "p90") > 17
with zipfile.ZipFile(ROOT / FAO) as archive, archive.open(
    "FoodBalanceSheets_E_All_Data_(Normalized).csv"
) as stream:
    fao = {
        (r["Item Code"], r["Element Code"]): float(r["Value"])
        for r in csv.DictReader(io.TextIOWrapper(stream, "utf-8-sig"))
        if r["Area Code"] == "165" and r["Year"] == "2023" and r["Element Code"] == "5142"
        and r["Item Code"] in {"2740", "2948"}
    }
ghee, fao_milk = fao[("2740", "5142")], fao[("2948", "5142")]
econ_milk = inputs["economic"]["milk"][-1]
assert (ghee, fao_milk, econ_milk) == (1268.0, 32104.0, 58300.0)

S = {k: fmt(v, 3) + "%" for k, v in share.items()}
SP = {y: (fmt(a, 3) + "%", fmt(b, 3) + "%") for y, (a, b) in spread.items()}
CV = {y: fmt(v / 1000, 1) for y, v in central.items()}
T = {(y, s): fmt(transfer(y, s), 2) for y in YEARS for s in ("p10", "p90")}

OECD_URL = (
    "https://sdmx.oecd.org/public/rest/data/OECD.TAD.ATM,DSD_AGR@DF_OUTLOOK_2025_2034,"
    "1.1/IND+PAK.A....?startPeriod=2010&endPeriod=2034&dimensionAtObservation=AllDimensions"
)
GRID_LINK = "../../../" + GRID
README_LINK = "../../../" + B + "/data/pakistan-topdown/README.md"
box = [
    "# Pakistan: conventional-value scale check",
    "",
    "**Conditional scale comparison. It shows how large the transferred Pakistan scenarios are relative to conventional poultry and milk value. It does not estimate alternative-protein sales or an observed market share.**",
    "",
    f"Conventional value multiplies quantity by price and converts at PKR 281.143001173202/USD, the retained 2025 annual-average rate. Poultry uses [OECD-FAO consumption quantities]({OECD_URL}), ready-to-cook weight, from the outlook published in 2025; the 2034 quantity is carried unchanged into 2035. Milk uses [FAOSTAT](https://www.fao.org/faostat/en/#data/FBS) 2023 food availability for milk excluding butter, held fixed.",
    "",
    "Prices come from the [PBS issue of 24 December 2025](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Annex_24.12.2025.pdf), page 3, whose national averages cover an urban-market sample: PKR 424.89/kg of live broiler and PKR 203.51/litre of fresh milk. The live-bird price is divided by an assumed dressed/live yield of 0.70. The milk price is converted with the [FAO INFOODS](https://www.fao.org/fileadmin/templates/food_composition/documents/density_DB_v2_0_01.pdf) whole-liquid-milk density of 1.031 kg/litre. Neither conversion is validated for this national basket.",
    "",
    "**Central conversion assumptions; values in US dollars at conditional 2025 reference prices.**",
    "",
    "| Comparison year | Conventional poultry and milk value, USD billion | Transfer 10th to 90th percentile, USD million | Transfer range as a share of conventional value |",
    "|---|---:|---:|---:|",
    *[
        f"| {y} | {CV[y]} | {T[(y, 'p10')]} to {T[(y, 'p90')]} | {S[(y, 'p10')]} to {S[(y, 'p90')]} |"
        for y in YEARS
    ],
    "",
    f"Across all 18 combinations of quantity source and price profile, the 2035 share spans {SP['2035'][0]} to {SP['2035'][1]}. The alternatives include fiscal-year 2024 to 2025 Economic Survey quantities and Naheed premium-outlet prices deflated by the 7.1% CPI projection. Higher conventional values give lower shares.",
    "",
    f"The requested capture shares of 0.05%, 0.1% and 0.5% each exceed the 2026 share under all 18 profiles. Across the full 162-row grid, 139 rows exceed the transfer's 90th percentile and none falls below its 10th percentile. At 0.5%, the milk component alone is USD {fmt(milk_2026, 2)} million in 2026, over 17 times the transfer's 90th percentile.",
    "",
    f"This is a scale check because the baskets differ. Conventional value includes nonmarketed and loose milk at an urban fresh-milk price, while the retained alternative-protein price evidence comes from formal retail. FAOSTAT's milk item excludes the milk equivalent of butter and ghee, listed separately at {fmt(ghee, 0)} thousand tonnes of food; the Economic Survey's milk for human consumption is {fmt(econ_milk, 0)} thousand tonnes against FAOSTAT's {fmt(fao_milk, 0)}. The live-bird price values poultry below retail. The transfer's basket includes plant-based meat, dairy and eggs; the conventional basket covers poultry and milk only. No retained source gives an observed alternative-protein share of conventional value in either country, so the requested shares remain unanchored.",
    "",
    f"**AI draft, replace:** We compare Pakistan's transferred scenarios with the value of conventional poultry and milk. Under central conversion assumptions, the scenarios equal about {S[('2026', 'p10')]} to {S[('2026', 'p90')]} of that value in 2026 and {S[('2035', 'p10')]} to {S[('2035', 'p90')]} in 2035. These shares describe scale only. The conventional value includes milk that never passes through formal retail, and its price conversions are assumptions. With no observed share to compare against, the result supports measuring a Pakistan sales baseline before any market share is assumed.",
    "",
    f"[Full grid]({GRID_LINK}); [assumptions and reproduction]({README_LINK}).",
]

# Claim rows: reuse accepted P4 rows for repeated inputs, add computed rows.
CLAIMS = HANDOFF / "kit/claims-by-section.csv"
with CLAIMS.open(newline="") as stream:
    reader = csv.DictReader(stream)
    headers = reader.fieldnames
    claims = list(reader)
by_id = {r["claim_id"]: r for r in claims}
results_row = {
    t: next(
        r for r in claims if r["occurrence_file"] == RESULTS and r["display_token"] == t
    )
    for t in ("10th", "90th")
}


def tpl(claim_id: str) -> dict:
    return dict(by_id[claim_id])


def tpl_results(token: str) -> dict:
    return dict(results_row[token])


def derived(value: str, unit: str, locator: str, local: str = GRID, family: str = "derived_scale_ratio", url: str | None = None, date: str = "2026-10-30") -> dict:
    return {
        "value": value,
        "unit": unit,
        "source_url": url or "../../../" + local,
        "source_date": date,
        "status": "verified",
        "evidence_family": family,
        "local_source": local,
        "locator": locator,
        "notes": f"Computed and display-checked by {SCRIPT}; scale comparison, not an observed share or market estimate.",
    }


def share_def(y: str, s: str) -> dict:
    return derived(f"{share[(y, s)]:.6f}", "percent of central conventional poultry and milk value", f"{REF} pakistan_{y}_market_value_{s} / OECD_poultry_FAO_milk official_central_sensitivity year={y} poultry+milk conventional value")


def year_def(y: str) -> dict:
    return tpl({"2026": "WK-P-018", "2030": "WK-P-024", "2035": "WK-P-030"}[y])


transfer_ids = {("2026", "p10"): "WK-P-022", ("2026", "p90"): "WK-P-023", ("2030", "p10"): "WK-P-028", ("2030", "p90"): "WK-P-029", ("2035", "p10"): "WK-P-034", ("2035", "p90"): "WK-P-035"}
seventeen = tpl("WK-P-046")
seventeen.update(value="17")
econ_year = derived("2024-2025", "Economic Survey fiscal-year column", "Table 2.6 column 2024-25; Milk (Human Consumption)", local=ECON, family="official_source_metadata", url="https://www.finance.gov.pk/survey/chapter_25/2_Agriculture.pdf")
bindings: dict[int, list[dict]] = {
    5: [tpl("WK-P-012"), tpl("WK-P-013"), tpl("WK-P-001"), tpl("WK-P-002"), tpl("WK-P-003"), tpl("WK-P-004")],
    7: [tpl("WK-P-005"), tpl("WK-P-006"), tpl("WK-P-007"), tpl("WK-P-008"), tpl("WK-P-009"), tpl("WK-P-010"), tpl("WK-P-011")],
    9: [tpl("WK-P-014")],
    11: [tpl_results("10th"), tpl_results("90th")],
    17: [
        derived(str(len({(f, p) for f, p, _ in profiles})), "quantity and price profile combinations", "unique quantity_family x price_profile in grid"),
        year_def("2035"),
        derived(f"{spread['2035'][0]:.6f}", "percent; lowest 10th-percentile share across profiles", "min over 18 profiles of pakistan_2035 p10 / conventional value"),
        derived(f"{spread['2035'][1]:.6f}", "percent; highest 90th-percentile share across profiles", "max over 18 profiles of pakistan_2035 p90 / conventional value"),
        econ_year,
        econ_year,
        tpl("WK-P-042"),
    ],
    19: [
        tpl("WK-P-015"), tpl("WK-P-016"), tpl("WK-P-017"), year_def("2026"),
        derived("18", "quantity and price profile combinations", "unique quantity_family x price_profile in grid"),
        tpl("P4_grid_rows"),
        derived(str(above), "grid rows above transfer 90th percentile", "combined_capture_million_usd > transfer_p90_million_usd"),
        tpl_results("90th"), tpl_results("10th"), tpl("WK-P-017"), tpl("WK-P-043"), year_def("2026"), seventeen, tpl_results("90th"),
    ],
    21: [
        derived(fmt(ghee, 0).replace(",", ""), "thousand tonnes, butter and ghee food, Pakistan 2023", "Area 165; Item 2740 Butter, Ghee; Element 5142 Food; Year 2023", local=FAO, family="national_food_supply", url="https://www.fao.org/faostat/en/#data/FBS", date="release_vintage=2025-10-28"),
        derived(str(int(econ_milk)), "thousand tonnes, milk for human consumption, 2024-25", "Table 2.6; Milk (Human Consumption); 2024-25 column", local=ECON, family="official_production_estimate", url="https://www.finance.gov.pk/survey/chapter_25/2_Agriculture.pdf", date="publication_year=2025; survey_edition=2024-25"),
        derived(str(int(fao_milk)), "thousand tonnes, milk excluding butter food, Pakistan 2023", "Area 165; Item 2948; Element 5142 Food; Year 2023", local=FAO, family="national_food_supply", url="https://www.fao.org/faostat/en/#data/FBS", date="release_vintage=2025-10-28"),
    ],
    23: [share_def("2026", "p10"), share_def("2026", "p90"), year_def("2026"), share_def("2035", "p10"), share_def("2035", "p90"), year_def("2035")],
}
for i, y in enumerate(YEARS):
    bindings[13 + i] = [
        year_def(y),
        derived(f"{central[y] / 1000:.6f}", "USD billion conventional poultry and milk value at conditional 2025 reference prices", f"OECD_poultry_FAO_milk; official_central_sensitivity; year={y}; poultry + milk conventional value", family="conditional_conventional_value"),
        tpl(transfer_ids[(y, "p10")]),
        tpl(transfer_ids[(y, "p90")]),
        share_def(y, "p10"),
        share_def(y, "p90"),
    ]


def check(token: str, definition: dict) -> None:
    """Require the displayed token to equal the bound value at display precision."""
    shown = token.replace(",", "").replace("−", "-").replace("th", "").replace("%", "")
    value = definition["value"]
    if definition.get("display_token") in {"10th", "90th"}:
        assert token == definition["display_token"], (token, definition["display_token"])
        return
    try:
        number = float(value)
    except ValueError:
        assert shown in re.split(r"[-/ ]", value), (token, value)
        return
    places = len(shown.split(".")[1]) if "." in shown else 0
    assert f"{number:.{places}f}" == shown, (token, value)


new_rows: list[dict] = []


def bind(file: str, section: str, line_no: int, line: str, defs: list[dict]) -> None:
    tokens = NUMBER.findall(visible(line))
    assert len(tokens) == len(defs), (file, line_no, tokens)
    for token, definition in zip(tokens, defs):
        check(token, definition)
        row = {k: definition.get(k, "") for k in headers}
        source_id = definition.get("claim_id", "")
        if source_id:
            row["notes"] = (definition.get("notes") or "") + f" Rebound from accepted row {source_id} by {SCRIPT}."
        row.update(section=section, claim_id=f"WK-B-{len(new_rows) + 1:03d}", status="verified", occurrence_file=file, occurrence_line=str(line_no), display_token=token, human_review="pending")
        new_rows.append(row)


for number, line in enumerate(box, start=1):
    defs = bindings.get(number, [])
    if NUMBER.findall(visible(line)) or defs:
        bind(BOX, "appendices", number, line, defs)

# One body sentence in section 6; other lines keep their numbers and positions.
results_path = HANDOFF / RESULTS
results = results_path.read_text().split("\n")
assert len(results) == 28 and results[12].startswith("Pakistan's body presentation")
sentence = f" Appendix A's scale check finds that, under central conversion assumptions, the transferred 2035 range equals about {S[('2035', 'p10')]} to {S[('2035', 'p90')]} of Pakistan's conventional poultry and milk value."
results[0] = "## 6. Results (budget: 1,100 words)"
results[12] = results[12] + sentence
results[22] = "**Figures or tables:** The India table above. Appendix A holds the transferred medians, sensitivities and the Pakistan conventional-value scale check."
results[26] = "**Open questions for Umar:** Decide whether the one-sentence pointer to the Appendix A scale check is enough in the body."
bind(RESULTS, "6", 13, sentence, [year_def("2035"), share_def("2035", "p10"), share_def("2035", "p90")])

appendix_path = HANDOFF / "kit/appendices.md"
appendix = appendix_path.read_text().split("\n")
assert appendix[0] == "## Appendix A. Proxy equations and Pakistan medians (budget: 800 words)"
assert appendix[20] == "**Figures or tables:** The Pakistan table above. Keep original data and equations available as companions to the joint PDF."
assert appendix[24].startswith("**Open questions for Umar:** None needed")
appendix[0] = "## Appendix A. Proxy equations, Pakistan medians and scale check (budget: 800 words)"
appendix[20] = "**Figures or tables:** The Pakistan table above and the scale-check table that follows. Keep original data and equations available as companions to the joint PDF."
appendix[24] = "**Open questions for Umar:** Scientific acceptance of the transfer assumptions remains separate. The scale check now sits here; consider moving part of the results section's word budget to this appendix."

kept = [r for r in claims if r["occurrence_file"] != BOX]
assert len(claims) - len(kept) == 47
(HANDOFF / BOX).write_text("\n".join(box) + "\n")
results_path.write_text("\n".join(results))
appendix_path.write_text("\n".join(appendix))
with CLAIMS.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=headers, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(kept + new_rows)
receipt = {
    "status": "PASS",
    "removed_box_occurrence_rows": 47,
    "added_rows": len(new_rows),
    "claim_rows": len(kept) + len(new_rows),
    "central_conventional_value_usd_billion": {y: round(v / 1000, 6) for y, v in central.items()},
    "implied_share_percent": {f"{y}_{s}": round(v, 6) for (y, s), v in share.items()},
    "implied_share_spread_percent": {y: [round(a, 6), round(b, 6)] for y, (a, b) in spread.items()},
    "grid_rows_above_p90": above,
    "grid_rows_below_p10": below,
    "limits": "Agent arithmetic and provenance checks; human review and economic mapping validity remain pending.",
}
(HANDOFF / "claude-review/box-move-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
