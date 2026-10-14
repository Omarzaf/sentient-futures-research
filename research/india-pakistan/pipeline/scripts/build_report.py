"""Generate the local research report from exact, uniquely selected evidence rows."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

from provenance import ROOT, read_csv

__all__ = ["build"]


def build() -> None:
    """Write findings with an executable selection ledger and bounded interpretation."""
    sources = {r["source_id"]: r for r in read_csv(ROOT / "data/processed/sources.csv")}
    selections: list[dict[str, object]] = []
    findings: list[str] = []

    def one(dataset: str, **criteria: str) -> dict[str, str]:
        """Select one source observation or fail on missing/ambiguous evidence."""
        rows = read_csv(ROOT / "data/processed" / f"{dataset}.csv")
        matches = [r for r in rows if all(r.get(k) == v for k, v in criteria.items())]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one {dataset} row for {criteria}: {len(matches)}"
            )
        row = matches[0]
        selections.append({"dataset": dataset, "criteria": criteria, "row": row})
        return row

    def number(row: dict[str, str], field: str = "value", places: int = 2) -> str:
        """Format a saved numeric value without changing its measurement basis."""
        return f"{Decimal(row[field]):,.{places}f}"

    def cite(*rows: dict[str, str]) -> str:
        """Cite every distinct primary source with its actual evidence tier."""
        ids = list(dict.fromkeys(row["source_id"] for row in rows))
        return "; ".join(
            f"[{sid}]({sources[sid]['url']}) (tier {sources[sid]['tier']})"
            for sid in ids
        )

    def add(statement: str, *rows: dict[str, str]) -> None:
        """Append one bounded finding and its linked source IDs."""
        findings.append(f"{statement} Source: {cite(*rows)}.")

    for item, label in (
        ("Poultry Meat", "Poultry"),
        ("Pulses", "Pulses"),
        ("Milk - Excluding Butter", "Milk excluding butter"),
    ):
        india, pakistan = [
            one(
                "meat_supply_national",
                country=c,
                year="2023",
                item=item,
                metric="food_supply_quantity",
            )
            for c in ("India", "Pakistan")
        ]
        add(
            f"**{label} availability differs between the national food balances.** In 2023, FAOSTAT records {number(india)} kg/person/year for India and {number(pakistan)} for Pakistan. These are food-supply estimates, with source flags retained; they do not measure individual intake or retail sales.",
            india,
            pakistan,
        )

    india, pakistan = [
        one(
            "meat_supply_national",
            country=c,
            year="2034",
            item="Poultry meat",
            metric="oecd_human_consumption_projection",
        )
        for c in ("India", "Pakistan")
    ]
    add(
        f"**The Outlook provides a separate projection series.** Its 2025–2034 vintage projects poultry consumption in 2034 at {number(india, places=4)} kg/person/year for India and {number(pakistan, places=4)} for Pakistan, in retail weight. Different weight conventions prevent splicing these values onto the FAOSTAT supply series as a measured trend.",
        india,
        pakistan,
    )

    urban, rural = [
        one(
            "cultural_context",
            country="India",
            dimension="urban_rural_diet",
            region=f"National; {r} women",
        )
        for r in ("urban", "rural")
    ]
    add(
        f"**India's food-frequency evidence varies by residence.** NFHS-5 reports {number(urban, places=1)}% of urban women and {number(rural, places=1)}% of rural women eating fish, chicken or meat at least weekly. Denominator: women aged 15–49; tabulation bases {int(urban['sample_size']):,} urban and {int(rural['sample_size']):,} rural; fieldwork June 2019–April 2021 across two phases, Table 10.26.1, printed page 438. Frequency supplies neither portion size nor a causal urbanisation effect.",
        urban,
        rural,
    )

    low, high = [
        one(
            "meat_regional",
            country="Pakistan",
            region="Pakistan",
            source_id="pakistan_hies_2024_25_table23",
            period="2024-25",
            residence="all",
            quintile=q,
            indicator="monthly_per_capita_chicken_meat_consumption",
        )
        for q in ("Q1", "Q5")
    ]
    add(
        f"**Pakistan's revised quantity table shows an expenditure gradient.** HIES 2024–25 Table 23 records chicken quantities of {low['display_value']} kg/person/month in the lowest expenditure quintile and {high['display_value']} in the highest (Sheet1 D32 and H32). Exact revised-workbook analytical sample is unknown; report household-count context is kept separately. Fieldwork began September 2024, but source end-month statements conflict. These per-capita quantities are not protein intake, a price elasticity or a measured substitution preference.",
        low,
        high,
    )

    rural, urban = [
        one(
            "protein_gap",
            country="India",
            group=f"{r}_MPCE_All-India__india_EAR_60kg",
        )
        for r in ("rural", "urban")
    ]
    add(
        f"**India has official household-based protein estimates.** HCES 2023–24 records {number(rural, 'intake_g', 1)} g/consumer-unit/day rural and {number(urban, 'intake_g', 1)} urban in the published per-consumer-unit columns, Table 3.9, printed page 38. Fieldwork was August 2023–July 2024; survey household context is {int(rural['survey_sample_size']):,} rural and {int(urban['survey_sample_size']):,} urban, while exact nutrient-table analytical bases remain unspecified. The consumer unit is an energy scale referenced to a sedentary adult man, not protein equivalence. EAR is the primary adult scenario; RDA is a labelled sensitivity. Neither comparison establishes adequacy or population deficiency prevalence.",
        rural,
        urban,
    )

    india, pakistan = [
        one(
            "deficiency_population",
            country=c,
            year="2024",
            indicator="unable_to_afford_healthy_diet",
        )
        for c in ("India", "Pakistan")
    ]
    add(
        f"**Healthy-diet affordability is a large, distinct access constraint.** SOFI 2025 gives 2024 shares unable to afford a healthy diet of {number(india, places=1)}% in India and {number(pakistan, places=1)}% in Pakistan. These modelled economic-access measures do not diagnose protein deficiency and cannot be added to malnutrition counts.",
        india,
        pakistan,
    )

    india, pakistan = [
        one(
            "deficiency_population", country=c, year="2024", indicator="under5_stunting"
        )
        for c in ("India", "Pakistan")
    ]
    add(
        f"**The selected JME vintage estimates substantial child stunting.** The March 2026 country model gives 2024 under-five rates of {number(india, places=1)}% for India and {number(pakistan, places=1)}% for Pakistan. These are modelled estimates rather than new survey measurements. Stunting has multiple causes; the rows retain estimator, vintage, intervals and population-count provenance, and remain separate from original NFHS/NNS observations.",
        india,
        pakistan,
    )

    india, pakistan = [
        one(
            "altprotein_sources",
            country=c,
            year="2024",
            source_type="pulses_total",
            metric="crop_production_potential_feedstock_context",
        )
        for c in ("India", "Pakistan")
    ]
    add(
        f"**Pulse production is potential feedstock context.** FAOSTAT QCL records {number(india)} tonnes for India and {number(pakistan)} tonnes for Pakistan in 2024. These whole-crop quantities include multiple uses and are not alternative-meat output, protein-isolate capacity or sales. Source flags and aggregate-overlap warnings remain attached.",
        india,
        pakistan,
    )

    row = one(
        "cultural_context",
        country="India",
        region="National",
        dimension="vegetarianism_religion",
    )
    add(
        f"**Vegetarian self-identification is a different construct from food frequency.** Pew's survey reports {number(row, places=0)}% of Indian adults self-identifying as vegetarian. The {int(row['sample_size']):,} interviews were conducted November 2019–March 2020; respondents supplied their own definition, and the report documents geographic exclusions. This historical identity measure does not establish current alternative-protein demand (chapter 10, printed page 186).",
        row,
    )

    row = one("cultural_context", country="Pakistan", dimension="urbanisation")
    add(
        f"**Population geography supplies context rather than consumer preference.** Pakistan's final 2023 census report records {number(row)}% urban in the cited geography of four provinces plus ICT, Figure 4.1, printed page 126. AJK and GB are outside that cited geography. The percentage alone supports no claim about alternative-protein acceptance.",
        row,
    )

    table = []
    for path in sorted((ROOT / "data/processed").glob("*.csv")):
        if path.name == "sources.csv" or path.stem.startswith("newsframing_"):
            continue
        rows = read_csv(path)
        counts = [
            sum(r.get("country") == c for r in rows) for c in ("India", "Pakistan")
        ]
        table.append(
            f"| [{path.name}](data/processed/{path.name}) | {len(rows)} | {counts[0]} | {counts[1]} |"
        )
    state = json.loads((ROOT / "STATE.json").read_text())
    milestone_table = "\n".join(
        f"| {m['id']} | {m['status']} | {m['name']} |" for m in state["milestones"]
    )
    text = "# Pakistan–India protein evidence report\n\n"
    text += "Local AI-assisted research draft, pending human scholarly review. Evidence snapshot: 13 October 2026. This report preserves source vintages and unresolved values; it is not a publication or a claim that all milestones passed.\n\n"
    text += (
        "## Findings\n\n"
        + "\n\n".join(f"{i}. {f}" for i, f in enumerate(findings, 1))
        + "\n\n"
    )
    text += "Values above are read directly from saved source-linked rows. Display rounding does not change units; the complete selected rows, locators and survey metadata are in [the finding ledger](logs/report-finding-evidence.json). Primary-source attribution is not a claim of independent replication.\n\n"
    one("protein_intake_modelled", country="Pakistan", reporting_level="national")
    ranges = [
        one("protein_model_method_ranges", group="all_all", scope=scope)
        for scope in (
            "matched_basket_subtotal",
            "five_animal_foods_subtotal",
        )
    ]
    text += "## Experimental Pakistan physical conversions\n\n"
    text += "A complete dietary-protein total remains unavailable. The previous pooled-basket cost calibration is withdrawn from current inference; its frozen outputs remain historical evidence. Partial food sums must not be substituted for total intake or compared with EAR/RDA.\n\n"
    for row in ranges:
        text += f"{row['scope']}: {number(row, 'low', 2)}–{number(row, 'high', 2)} g/person/day; low method `{row['low_method']}`, high method `{row['high_method']}`. These are conditional method extrema, not a confidence interval or an exhaustive uncertainty range. Source: {cite(row)}.\n\n"
    text += "The matched-basket subtotal covers only the foods with conditional physical conversions. Chicken, beef, mutton, eggs and fish form a separate five-food subtotal, which excludes other animal-source foods. Unresolved quantities, food-form mixtures, incomplete prepared-food scope and source reconciliation prevent a full-diet total. Residence rankings are removed. All analyst rows carry `derived`, with input-source tiers retained separately. See [the revised method](scripts/diet/supervisor_model_20261013/README.md), [food coverage](data/processed/protein_model_food_coverage.csv), and [dispositions of the previous sensitivity cases](scripts/diet/supervisor_model_20261013/old_sensitivity_disposition.csv).\n\n"
    text += (
        "## Coverage\n\n| Dataset | Rows | India | Pakistan |\n|---|---:|---:|---:|\n"
        + "\n".join(table)
        + "\n\n"
    )
    text += "These are derived inventory counts, not populations or companies currently operating. Each dataset links its observations to [the tiered source ledger](data/processed/sources.csv); [the raw manifest](data/raw/MANIFEST.csv) records retrieval and hashes. The news-framing analysis is confined to the limitations appendix below and remains pending human scholarly review.\n\n"
    text += "## Nadja audit checklist\n\nThe previous [audit notes](notes/M9-ALTPROTEIN-AUDIT.md) and [audit ledger](logs/altprotein-audit.csv) apply to the earlier snapshot. Revised policy/company rows have [source-specific evidence notes](scripts/altprotein/supervisor_revision_20261013/EVIDENCE-NOTES.md) and [integration validation](scripts/altprotein/supervisor_revision_20261013/integration-validation.json). A passing byte or source check does not establish legal approval, current operation or market coverage.\n\n- Company status: require dated evidence; an event, filing or directory appearance is not a verified operating total or sales record.\n- Geography: distinguish India/Pakistan activity from overseas examples, diaspora contexts and regional/global forecasts.\n- Category: keep plant crops, plant-based products, fermentation, cultivated cells, insects and hybrids distinct; inputs and multiuse facilities are not finished-protein output.\n- Policy date: retain historical and current document dates separately; research funding, standards, licensing processes and religious rulings are not product approvals.\n\n"
    text += "## Gaps and blockers\n\n- Pakistan complete dietary intake remains missing. The physical conversions describe partial reported foods only. Adult-equivalent intake, usual-intake distributions, source reconciliation and protein-quality adjustment are unresolved.\n- Framing collection has stopped under the supervisor plan. Subject-country and topic exclusions, the independent second annotation and unresolved holds are recorded in the limitations appendix. Framing is neither public opinion nor consumer demand. No sentiment result is approved for the edition.\n- Browser evidence from the previous build is historical. The current page needs new hash-bound browser QA; static or Node checks do not establish visual correctness.\n- Current retail sales, many pilot capacities, source uncertainty intervals, complete regional survey metadata and direct domestic cultural evidence remain incomplete. India historical scenarios are not current sales. Pakistan IndexBox ranges remain held.\n- Punjab has a general functional-food/supplement instrument containing a novel-food provision. The reviewed sources do not establish a cultivated-specific pathway or approval.\n- Nutrition indicators overlap and have different denominators. No summed deficient population or protein-deficiency prevalence is inferred.\n\nSee [GAPS.md](notes/GAPS.md) and the supervisor review ledger for the repair status.\n\n"
    text += "## Next data requests\n\nSeek compatible food-specific quantity, cost and denominator evidence, respondent-level consumer data where authorized, and independently dated retail or operating evidence. Requests remain unsent. Keep the unresolved values missing until those sources support a documented revision.\n\n"
    text += (
        "## Milestone state at report build\n\n| Milestone | Status | Scope |\n|---|---|---|\n"
        + milestone_table
        + "\n\nExecuted acceptance checks are recorded in [the latest verifier result](logs/verify-latest.json); state flags are not substitutes for those checks.\n"
    )
    primary = one("newsframing_agreement", analysis_id="admissible_primary")
    sensitivity = one(
        "newsframing_agreement", analysis_id="b_retained_provisional_sensitivity"
    )
    retained = read_csv(ROOT / "data/processed/newsframing_retained.csv")
    excluded = read_csv(ROOT / "data/processed/newsframing_excluded.csv")
    dispositions = read_csv(ROOT / "data/processed/newsframing_dispositions.csv")
    assert len(retained) + len(excluded) == len(dispositions)
    country_counts = {
        country: sum(row["subject_country"] == country for row in retained)
        for country in ("India", "Pakistan")
    }
    text += "\n## Limitations appendix: selected news framing\n\n"
    text += f"The independent Prompt B review covers all {len(dispositions)} original supplied extents. Final admissibility retains {len(retained)} and excludes {len(excluded)}, including unresolved source-access holds. Subject country is India for {country_counts['India']} retained texts and Pakistan for {country_counts['Pakistan']}; publisher country is stored separately. No article body is reproduced here.\n\n"
    text += f"For the admissible denominator, Prompt A and B agree on {primary['agreement_count']} of {primary['n']} labels. Unweighted nominal Cohen's kappa is {number(primary, 'kappa', 3)} (exact fraction {primary['kappa_numerator']}/{primary['kappa_denominator']}). The separate provisional sensitivity keeps all B-retained extents, including the unresolved holds: {sensitivity['agreement_count']}/{sensitivity['n']} agreement and kappa {number(sensitivity, 'kappa', 3)}. It is not the primary corpus.\n\n"
    text += f"Prompt B's recorded runtime model is `{primary['annotation_b_model_id']}`; Prompt A's runtime identity is `{primary['annotation_a_model_id']}`. This is blind AI annotation agreement, not accuracy or independent-model validation. It describes selected news framing, not public opinion, consumer demand, a random sample or comparable national media coverage. Human scholarly adjudication remains pending.\n\n"
    text += "The [validation method and receipt](scripts/sentiment/supervisor_validation_20261013/README.md), [retained records](data/processed/newsframing_retained.csv), [exclusion ledger](data/processed/newsframing_excluded.csv), [agreement](data/processed/newsframing_agreement.csv), and [coverage](data/processed/newsframing_coverage.csv) preserve exact identities, uncertainty and denominators. These results are excluded from dashboard payloads and edition headlines.\n"
    (ROOT / "REPORT.md").write_text(text)
    (ROOT / "logs/report-finding-evidence.json").write_text(
        json.dumps(
            {
                "build_input_sha256": {
                    str(path.relative_to(ROOT)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in sorted((ROOT / "data/processed").glob("*.csv"))
                },
                "findings": len(findings),
                "selected_rows": selections,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        f"Wrote REPORT.md: {len(findings)} source-linked findings; {len(selections)} exact row selections"
    )


if __name__ == "__main__":
    build()
