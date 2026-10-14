"""Assemble the report from authored prose, exact claims and public source metadata."""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_csv(name: str) -> list[dict[str, str]]:
    """Read a local UTF-8 CSV without coercing numbers or missing values."""
    with (ROOT / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


CLAIMS = {row["claim_id"]: row for row in read_csv("claims.csv")}
SOURCES = {row["source_id"]: row for row in read_csv("data/sources.csv")}
USED: set[str] = set()
USED_SOURCES: set[str] = set()


def claim(key: str) -> str:
    """Bind the displayed quantity to its exact ledger value."""
    row = CLAIMS[key]
    USED.add(key)
    USED_SOURCES.update(json.loads(row["source_ids"]))
    return f'[{row["display"]}]{{.claim data-claim="{key}"}}'


def allowed(text: str, kind: str = "year") -> str:
    """Mark a date or structural year for independent validation."""
    return f'[{text}]{{.allow-number data-number-kind="{kind}"}}'


def source_cell(key: str, column: str) -> str:
    """Bind an unchanged registry field instead of retyping its digits."""
    text = SOURCES[key][column]
    if not text:
        return "Not recorded"
    if "\n" in text:
        raise ValueError(
            f"Source field needs explicit Markdown treatment: {key}/{column}"
        )
    escaped = (
        html.escape(text, quote=True)
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace("|", "&#124;")
    )
    date_class = " .keep-word" if column in {"accessed", "year"} else ""
    return f'[{escaped}]{{.source-cell{date_class} data-source-id="{key}" data-source-column="{column}"}}'


def cite(key: str, label: str = "Source") -> str:
    """Link to the registry URL, retaining local-only records as unlinked metadata."""
    USED_SOURCES.add(key)
    mapping_path = ROOT / "data/reader-links.json"
    mapping = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    alternative = mapping.get(key, {})
    status_path = ROOT / "data/link-status.json"
    status = (
        json.loads(status_path.read_text()).get(key, {}) if status_path.exists() else {}
    )
    if not alternative and status.get("inactive") is True:
        return (
            label
            + " (publisher access unavailable in the recorded direct-link audit; "
            + "original bibliographic URL retained in the companion source CSV)"
        )
    url = (
        alternative.get("url", SOURCES[key]["url"])
        .replace("(", "%28")
        .replace(")", "%29")
        .replace("&", "&amp;")
    )
    return f"[{label}](<{url}>)" if url.startswith(("https://", "http://")) else label


def source_title(key: str) -> str:
    """Preserve titles, labelling the Urdu title translation for portable text export."""
    if key == "m6_public5_b5_11d16c01cf6ac76c":
        return (
            "Laboratory-grown onions, eggs and chicken — Express Urdu "
            "(English translation; original Urdu title retained in the source CSV)"
        )
    return source_cell(key, "title")


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a Markdown table from already validated reader-facing cells."""
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        + ["| " + " | ".join(row) + " |" for row in rows]
    )


def keep_compounds_together(markdown: str) -> str:
    """Keep authored hyphenated words intact at PDF line breaks without changing text."""
    tokens = re.split(
        r"(```[\s\S]*?```|\[[^\]\n]*\]\{[^}\n]*\}|\{[^}\n]*\}|\]\([^\n]*?\)|https?://[^\s<>]+|`[^`\n]*`)",
        markdown,
    )
    for index in range(0, len(tokens), 2):
        tokens[index] = re.sub(
            r"(?<![A-Za-z0-9_-])[A-Za-z]+(?:-[A-Za-z]+)+(?![A-Za-z0-9_-])",
            lambda match: "[" + match.group() + "]{.keep-word}",
            tokens[index],
        )
    return "".join(tokens)


def benchmark_table() -> str:
    """Display the selected forecasts with their model and unit boundary."""
    result = []
    for country in ("india", "pakistan"):
        for series in ("animal", "total"):
            prefix = f"benchmark_{country}_{series}_"
            result.append(
                [
                    country.title(),
                    "Animal-source" if series == "animal" else "Total",
                    claim(prefix + "forecast_2035"),
                    claim(prefix + "lower80_2035"),
                    claim(prefix + "upper80_2035"),
                ]
            )
    return "\n".join(
        [
            "Selected persistence forecasts for "
            + allowed("2035")
            + ", grams per person per day. The lower and upper bounds are the benchmark's nominal "
            + claim("benchmark_india_total_nominal_level")
            + " percent interval, with the coverage limitations below.",
            "",
            table(["Country", "Protein supply", "Point", "Lower", "Upper"], result),
            "",
            "Source: "
            + cite("package_P08", "Protein-supply benchmark")
            + ". All forecasts are derived.",
        ]
    )


def studies_table() -> str:
    """Keep all study samples separate with accurate product and geography descriptions."""
    descriptions = {
        "S01": ("Arab countries, pooled", "Artificial-meat attitudes"),
        "S02": ("UAE nationals", "Alternative-protein preferences"),
        "S03": (
            "Multinational sample including Pakistan",
            "Willingness to pay a premium",
        ),
        "S04": ("Turkish adults", "Cultured-meat acceptance"),
        "S05": ("Saudi adults", "Edible-insect acceptance"),
        "S06": ("Urban Muslim consumers in Selangor", "Cultured-beef acceptance"),
        "S07": (
            "Asian markets",
            "Extracted findings: willingness to eat cultivated meat",
        ),
        "S08": (
            "Selected Southeast Asian countries",
            "Alternative-protein demand measures",
        ),
        "S09": ("Singapore", "Product-specific consumer measures"),
    }
    result = []
    for row in read_csv("data/survey_studies.csv"):
        key = row["study_id"]
        geography, outcome = descriptions[key]
        result.append(
            [
                source_cell(key, "title"),
                geography,
                outcome,
                claim(f"study_{key.lower()}_sample_n"),
                cite(key),
            ]
        )
    return (
        table(
            ["Study and sample record"],
            [
                [
                    r[0]
                    + ". Geography: "
                    + r[1]
                    + ". Topic: "
                    + r[2]
                    + ". Reported full study sample: "
                    + r[3]
                    + ". "
                    + r[4]
                ]
                for r in result
            ],
        )
        + "\n\nThe sample column is the source register's total study sample, not a common analytical denominator. Publication dates in titles are not fieldwork dates. Recruitment and exclusions remain in the accompanying study CSV and original sources."
    )


def policy_table() -> str:
    """Read actual policy dates while avoiding a claim that every event is an approval."""
    labels = {
        "IN_INDIA_FSSAI_NSF_COMPENDIUM_2022": "Non-specified-food compendium of earlier regulations",
        "PK_PSQCA_HALAL_FOOD_2022": "General requirements for halal food",
        "PK_PSQCA_HALAL_BODIES_2022": "Requirements for halal certification bodies",
        "PK_PFA_PRODUCT_REGISTRATION_2017": "Product registration and logo regulations",
        "PK_PFA_FUNCTIONAL_NOVEL_2025": "Functional foods and supplements instrument, with novel-food provision",
        "IN_FSSAI_VEGAN_2022": "Vegan-food regulations",
        "IN_FSSAI_VEGAN_LOGO_AMENDMENT_2026": "Vegan-food logo amendment",
        "IN_FSSAI_VEGAN_IMPORT_AMENDMENT_2026": "Vegan-food import-certificate amendment",
    }
    result = []
    for row in read_csv("data/altprotein_policy.csv"):
        date = row["policy_date"]
        label = labels.get(row["policy_id"], row["policy"])
        basis = row["date_basis"]
        if row["policy_id"] == "IN_INDIA_FSSAI_NSF_COMPENDIUM_2022":
            basis = "Compendium version; underlying regulation " + allowed("2017")
        elif row["policy_id"] == "IN_INDIA_FSSAI_NSF_STATUS_20260901":
            basis = "List as-of date; filing shown separately"
        elif row["policy_id"] == "PK_PFA_FUNCTIONAL_NOVEL_2025":
            basis = "Notification; later gazette publication shown separately"
        extra_dates = []
        for field, caption in (
            ("application_date", "Filed"),
            ("publication_date", "Published"),
            ("effective_date", "Commences"),
        ):
            if row[field]:
                extra_dates.append(caption + " " + allowed(row[field], "date"))
        dates = allowed(date, "date" if len(date) == 10 else "year")
        if extra_dates:
            dates += "; " + "; ".join(extra_dates)
        status = row["status"].replace("_", " ")
        if row["policy_id"] == "IN_INDIA_FSSAI_NSF_STATUS_20260901":
            status = "Application stage remains ambiguous; no approval inferred"
        result.append(
            [
                row["country"],
                label,
                dates,
                basis.rstrip(".") + ". Status: " + status.rstrip("."),
                cite(row["source_id"]),
            ]
        )
    return (
        table(
            ["Instrument and date record"],
            [
                [r[0] + ": " + r[1] + ". " + r[2] + ". " + r[3] + ". " + r[4]]
                for r in result
            ],
        )
        + "\n\nDates retain the source's event basis. The accompanying policy CSV separately records publication, application and commencement where established."
    )


def claim_context(row: dict[str, str]) -> str:
    """Print exact selection metadata and name the estimate's role."""
    filters = json.loads(row["filter_json"])
    fields = []
    for name, value in filters.items():
        label = name.replace("_", " ")
        if name == "unique_id":
            country, series = value.split("_", 1)
            fields.append({"IND": "India", "PAK": "Pakistan"}.get(country, country))
            fields.append(
                "animal-source protein supply"
                if series == "animal"
                else "total protein supply"
            )
        elif name == "year":
            fields.append("year " + allowed(value))
        else:
            fields.append(
                label + " " + claim_meta(row["claim_id"], "filter." + name, value)
            )
    kind = {
        "point": "point estimate",
        "lower80": "lower interval bound",
        "upper80": "upper interval bound",
        "low": "low method endpoint",
        "high": "high method endpoint",
    }.get(
        row["value_column"],
        claim_meta(row["claim_id"], "value_column", row["value_column"]),
    )
    return "; ".join(fields + [kind])


def claim_meta(key: str, field: str, value: str) -> str:
    """Display exact claim identity or selection metadata through a strict binding."""
    escaped = (
        html.escape(value, quote=False)
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace("|", "&#124;")
    )
    return (
        f'[{escaped}]{{.claim-meta data-claim-meta="{key}" data-claim-field="{field}"}}'
    )


def period(text: str) -> str:
    """Bind source-reported fieldwork years as structural year metadata."""
    return re.sub(
        r"\b(?:19|20)\d{2}\b",
        lambda m: allowed(m.group()),
        text.replace("–", " to ").replace("-", " to "),
    )


def outcomes_table() -> str:
    """Show verified source-specific outcomes without creating a pooled rate."""
    data = [
        r
        for r in read_csv("data/survey_findings.csv")
        if r["admitted_for_synthesis"] == "true"
    ]
    result = []
    for sid in dict.fromkeys(r["source_id"] for r in data):
        selected = [r for r in data if r["source_id"] == sid]
        first = selected[0]
        result += [
            "### " + source_cell(sid, "title"),
            "",
            first["question_wording"].rstrip(".")
            + ". Fieldwork: "
            + period(first["fieldwork"])
            + ". Recruitment: "
            + first["recruitment"].rstrip(".")
            + ".",
            "",
            table(
                [
                    "Geography and product",
                    "Source result, percent",
                    "Reported group sample",
                ],
                [
                    [
                        r["geography"] + "; " + r["protein"],
                        claim("survey_" + r["record_id"].lower() + "_value_percent"),
                        claim("survey_" + r["record_id"].lower() + "_sample_n"),
                    ]
                    for r in selected
                ],
            ),
            "",
            first["denominator"]
            + ". "
            + first["limitation"]
            + " "
            + cite(sid, "Original source")
            + ".",
            "",
        ]
    result += [
        "The remaining extracted findings stay in the companion CSV. The approximate Arab-country willingness figure is held because the abstract supports a lower-bound description, and the Selangor paper retains conflicting acceptance figures. Summary-only outcomes whose question bases remain unresolved are also excluded from this synthesis. A verified study sample does not verify every finding attributed to that study."
    ]
    return "\n".join(result)


def reviews_table() -> str:
    """Describe every review resolution without importing private evidence paths."""
    descriptions = {
        "H1": "Recompute claims and test deliberate corruptions; historical shape checks remain dated.",
        "H2": "Withdraw the pooled-basket total and use named physical conversions for partial foods.",
        "H3": "Bind partial-food range endpoints to named methods and coverage; withdraw the old complete-total range.",
        "H4": "Compare a fresh-context annotation with the earlier labels and disclose uncertainty and unknown earlier model identity.",
        "H5": "Keep publisher and subject geography separate; reconcile exclusions and holds; confine results to the report appendix.",
        "H6": "Retain the reported UnCrave closure as a dated event with an unknown exact cessation date.",
        "H7": "Add the vegan-food rules and dairy-analogue consultation with their distinct legal status.",
        "M8": "Use published consumer-unit intake with a primary EAR scenario and an explicit denominator caveat.",
        "M9": "Remove rural and urban model rows and rankings from active projections while preserving historical artifacts.",
        "M10": "Place incompatible measures in separate panels and retain their source definitions.",
        "M11": "Remove the unweighted fraction of groups below the reference; it was not a population rate.",
        "M12": "Tag analyst calculations as derived and retain input-source tiers separately.",
        "M13": "Apply the revised freshness cutoff and integrate the saved parliamentary programme update; retain the old rule as historical.",
        "M14": "Apply the human-food versus feed rule consistently and retain explicit exclusions.",
        "M15": "Require browser receipts for the actual edition bytes; old screenshots do not validate this page.",
        "M16": "Fail missing evidence and skipped required checks; self-authored completion or blocked states cannot produce a pass.",
        "M17": "Correct the broad Pakistan rule-absence statement while distinguishing the general provincial provision from cultivated-specific approval.",
        "L1": "Correct the revised HIES quantity denominator to per capita.",
        "L2": "Name the Pakistan demographic and health survey by its actual fieldwork period.",
        "L3": "Read sample and fieldwork metadata from source rows, retain unknowns and populate badges from actual row and source tiers.",
        "L4": "Add Pakistan policy date, status and freshness; retain the Biokraft filing date separately from its list date.",
        "L5": "Reconcile annotation coverage to every original record, including unresolved extent holds.",
        "Y1": "Move large annotation inputs into ignored local storage with hashes, compatibility references and an undo record.",
        "Y2": "Exclude environments, caches and screenshots from versioning without deleting local evidence.",
        "Y3": "Create a local baseline and a repair branch for the dashboard; no remote is configured.",
        "Y4": "Preserve internal review history untouched and exclude it from the publication export.",
        "E1": "Require explicit retrieval timestamps for new evidence and preserve original identity and dates on routine reuse.",
        "E2": "Run calibration tests in temporary replicas and verify that frozen research outputs remain unchanged.",
        "E3": "Require an explicit publication allowlist with reviewed file hashes and rights.",
    }
    result = []
    for row in read_csv("data/review_status.csv"):
        key = row["review_id"]
        # The exact ID stays in an anchor and in the public review CSV.
        finding = row["finding"]
        if re.search(r"\d", finding):
            finding = descriptions[key].split(";")[0]
        result.append([f"[{finding}]{{#{key}}}", row["status"], descriptions[key]])
    return table(
        ["Review finding and resolution"],
        [[r[0] + ". Recorded status: " + r[1] + ". " + r[2]] for r in result],
    )


def news_appendix() -> str:
    """Keep all framing quantities in the dedicated limitations appendix only."""
    return "\n".join(
        [
            "## Appendix F News framing remains annotation evidence",
            "",
            "Collection stopped. The bounded review reconciles "
            + claim("news_original_all_all")
            + " original records to "
            + claim("news_final_admissible_all_all")
            + " admissible items, "
            + claim("news_b_excluded_all_all")
            + " excluded items and "
            + claim("news_additional_held_all_all")
            + " additional extent holds. The admissible set contains "
            + claim("news_final_admissible_subject_country_india")
            + " India-focused items and "
            + claim("news_final_admissible_subject_country_pakistan")
            + " Pakistan-focused item. That composition does not support a country comparison or an estimate of public sentiment.",
            "",
            "The second annotation ran without the earlier labels. On the admissible primary set, the runs agree on "
            + claim("news_primary_agreement_count")
            + " of "
            + claim("news_primary_n")
            + " items. Cohen's kappa is "
            + claim("news_primary_kappa")
            + ", with exact arithmetic "
            + claim("news_primary_kappa_numerator")
            + " divided by "
            + claim("news_primary_kappa_denominator")
            + ". The comparison is conditioned on the second run's eligibility decisions and the source-access holds.",
            "",
            "A sensitivity retaining the second run's held extents has "
            + claim("news_provisional_sensitivity_agreement_count")
            + " agreements among "
            + claim("news_provisional_sensitivity_n")
            + " items, with kappa "
            + claim("news_provisional_sensitivity_kappa")
            + ". Its inclusion does not resolve the extent holds. The primary set includes "
            + claim("news_final_admissible_uncertainty_b_high")
            + " high-uncertainty second-run decisions. Neither statistic measures accuracy or human consensus.",
            "",
            "```text\nSecond-run runtime model: gpt-6-astra\nEarlier-run runtime model: not established\nHuman adjudication: pending\n```",
            "",
            "The method record preserves the prompt, immutable inputs, individual labels, exclusions and disagreements locally. Runtime identity does not establish independent model families, and the unknown earlier identity is not filled by inference. Only bounded metadata and derived results are prepared for the report; article bodies are excluded from publication. No framing statistic appears in the edition's content or downloads.",
        ]
    )


def appendices() -> str:
    """Assemble source, claim, review, inventory and glossary reference sections."""
    news_text = news_appendix()
    source_rows = []
    for key in sorted(USED_SOURCES):
        source_rows.append(
            [
                source_cell(key, "source_id")
                + ": "
                + source_title(key)
                + "; tier "
                + source_cell(key, "tier")
                + "; vintage "
                + source_cell(key, "year")
                + "; accessed "
                + source_cell(key, "accessed")
                + "; "
                + cite(key, "Open source")
            ]
        )
    inventory = []
    inventory_meanings = {
        "altprotein_companies": "Dated company/activity records; inclusion does not verify current sales or operating capacity.",
        "altprotein_company_exclusions": "Candidates excluded by the human-food scope rule; retained for an auditable boundary.",
        "altprotein_market": "Source-specific market/context quantities; geography, product definition and units are not interchangeable.",
        "altprotein_policy": "Dated rules, drafts and programme events; a policy mention is not product authorization.",
        "altprotein_retail_offers": "Observed listing evidence; an offer does not establish local stock, sales or demand.",
        "altprotein_sources": "Feedstock, ingredient and capacity context records; production potential is not alternative-protein adoption.",
        "cultural_context": "Source-bounded cultural observations and survey context; affiliation alone does not identify purchasing behaviour.",
        "deficiency_population": "Country/period/proxy indicators with separate denominators; proxies do not identify protein-deficient people.",
        "diet_composition": "Food/group/period nutrient-share, quantity or expenditure records; units and household bases remain separate.",
        "meat_regional": "Region/indicator/period records including production and reported food frequency; these cannot be pooled as intake.",
        "meat_supply_national": "Country/item/measure/year supply and projection records; availability and forecasts differ from consumed intake.",
        "protein_gap": "Group/reference scenarios; comparisons are not population deficiency prevalence, and incompatible cases remain withheld.",
        "protein_gap_group_summary": "Residence/reference summaries of tabulated groups; group counts are not population-weighted rates.",
        "protein_intake_consumer_unit": "Published Indian group/sector estimates per consumer unit; the denominator is an energy-equivalence scale.",
        "protein_intake_modelled": "Withdrawn complete Pakistan group estimates; intake values remain blank.",
        "protein_intake_observed": "Published Indian group/sector estimates per person; preserve their distinct denominator.",
        "protein_model_food_coverage": "Food conversion coverage records, including unresolved and excluded inputs; a row is not a complete diet.",
        "protein_model_method_ranges": "Group/subtotal endpoints across named methods; conditional ranges are not confidence intervals.",
        "protein_model_physical_subtotals": "Method/group combinations for incomplete physical-food subtotals; total dietary intake is not inferred.",
        "protein_model_sensitivity": "Named conversion-method scenarios; no scenario establishes an observed national intake.",
        "region_boundary_crosswalk": "Source-region to boundary matches and holds; geometries do not validate the attached indicator.",
        "packages": "Research-package coverage records; coverage is separate from scholarly approval.",
        "package_metrics": "Package-specific scope and historical artifact counts; these are not independent empirical findings.",
        "benchmark_annual": "Supply observations by country, protein series and year, used by the benchmark; not alternative-protein consumption.",
        "benchmark_forecast": "Point and interval outputs by country, series and target year; exploratory supply forecasts, not adoption forecasts.",
        "benchmark_coverage": "Series-specific evaluation metrics and denominators; small evaluation samples limit calibration claims.",
        "survey_studies": "Study descriptions with separate samples and recruitment; respondent totals must not be pooled.",
        "survey_findings": "Heterogeneous reported outcomes, including held findings; only explicitly admitted outcomes enter the synthesis.",
        "phase_two_leads": "Access-route metadata; source-reported samples do not mean respondent files were acquired.",
        "reference_requirements": "Country/reference/weight scenarios; published coefficients and assumed body weights are distinct inputs.",
        "household_size_context": "Pakistani group-level household-size context; these values do not convert quantities into protein-equivalent people.",
        "review_status": "Review findings and recorded resolutions; software repair does not establish human scholarly approval.",
        "boundary_licenses": "Boundary-source and distribution attribution records; rights statements are asset-specific.",
        "sources": "Registered source identities; records need not be independent studies or currently accessible links.",
        "raw_manifest": "Preserved raw-file manifest entries; retrieval and file counts do not establish research validity or redistribution rights.",
        "claims": "Numeric display bindings to selected source rows, including appendix-only claims; repeated displays can share one claim.",
    }
    for row in read_csv("data/inventory_counts.csv"):
        key = row["dataset_id"]
        inventory.append(
            [
                key.replace("_", " "),
                claim(f"inventory_{key}_rows"),
                inventory_meanings[key],
            ]
        )
    used_before_appendix = sorted(USED)
    selected = []
    for key in used_before_appendix:
        row = CLAIMS[key]
        if key.startswith("news_"):
            continue
        selected.append(
            [
                claim_meta(key, "claim_id", key)
                + ". "
                + row["dataset"].replace("_", " ")
                + "; "
                + claim_context(row),
                claim(key),
                row["unit"],
                row["tier"],
                "; ".join(cite(source) for source in json.loads(row["source_ids"])),
            ]
        )
    glossary = [
        [
            "SOFI",
            "The State of Food Security and Nutrition in the World: the interagency report series supplying the affordability estimates.",
        ],
        [
            "JME",
            "Joint Child Malnutrition Estimates, produced by UNICEF, WHO and the World Bank.",
        ],
        [
            "MUIS",
            "Majlis Ugama Islam Singapura, Singapore's Islamic Religious Council.",
        ],
        ["FSSAI", "Food Safety and Standards Authority of India."],
        [
            "BioE3",
            "Biotechnology for Economy, Environment and Employment, India's biotechnology policy programme.",
        ],
        [
            "FBS",
            "Food balance sheets: national accounting estimates of food available for human consumption.",
        ],
        [
            "HIES",
            "Household Integrated Economic Survey: the Pakistani household survey and its stated quantity or expenditure measures.",
        ],
        [
            "HCES",
            "Household Consumption Expenditure Survey: the Indian household survey used for published nutrient estimates.",
        ],
        [
            "MPCE and expenditure fractiles",
            "Monthly per-capita consumption expenditure. Fractiles rank the population from lower to higher expenditure, separately within rural and urban sectors; they do not measure protein deficiency.",
        ],
        [
            "NFHS",
            "National Family Health Survey: respondent and household health measures, including reported food frequency.",
        ],
        [
            "EAR",
            "Estimated Average Requirement: a requirement reference, not an observed individual intake.",
        ],
        [
            "RDA",
            "Recommended Dietary Allowance: a distinct reference retained here as a labelled sensitivity.",
        ],
        [
            "Consumer unit",
            "An energy-based equivalence scale, not a protein-equivalent person.",
        ],
        [
            "Tier",
            "A source category whose use remains bounded by method, date, denominator and claim scope.",
        ],
        [
            "Tier A",
            "National statistics offices, ministries, FAO/WHO/World Bank/OECD datasets, and peer-reviewed papers with a stated sample.",
        ],
        [
            "Tier B",
            "GFI, USDA FAS GAIN, UN agency reports and reputable trackers under the project classification.",
        ],
        [
            "Tier C",
            "Market-research summaries, news and company press releases; a recorded claim is not independent confirmation.",
        ],
        [
            "Tier D",
            "Social media, Google Trends and LLM output. These cannot supply headline evidence; annotation results are confined to the report appendix.",
        ],
        [
            "Derived",
            "An analyst calculation or model output; the source tier is retained separately.",
        ],
        [
            "Acceptance",
            "A study-specific response that must not be substituted for observed purchase or habitual use.",
        ],
        [
            "Adoption",
            "An outcome requiring a stated product, population, behaviour, denominator and period.",
        ],
        [
            "Halal certification",
            "A scoped institutional decision for a product and process, distinct from general religious conditions and food authorization.",
        ],
    ]
    return "\n\n".join(
        [
            "## Appendix A Source ledger",
            "Sources cited in this report are listed by stable identifier, title, tier, recorded vintage, access date and public URL where available. The complete [source CSV](../data/sources.csv) also preserves discovery records, failed retrievals and held sources, with publishers, rights notes and access limitations. An empty public link marks a local research record. Inclusion in the companion ledger is not approval for substantive use.",
            table(["Source record"], source_rows),
            "## Appendix B Claims ledger summary",
            "The rows below summarize numerical bindings used in the report. The complete [claims CSV](../claims.csv) retains each exact filter, operation, rounding rule and original locator. Repeated quantities can share a dataset but refer to different groups or scenarios, so the filter must be read before comparison. News-framing results are confined to their separate appendix.",
            table(
                ["Claim record"],
                [
                    [r[0] + ": " + r[1] + " " + r[2] + "; tier " + r[3] + "; " + r[4]]
                    for r in selected
                ],
            ),
            "## Appendix C Review resolutions",
            "Each finding retains its recorded state. These descriptions are concise; the [review CSV](../data/review_status.csv) preserves stable identifiers and the detailed repair account. Open final-output requirements remain open until their evidence exists.",
            reviews_table(),
            "## Appendix D Data inventory",
            "The inventory distinguishes table rows from observations, people and independent sources. The raw-manifest count refers to preserved local inputs, which are not redistributed as a whole. Dataset versions and source locators accompany the CSVs. The original package inventory remains a dated historical checkpoint; these counts describe the assembled edition/report data.",
            table(
                ["Table or record set", "Rows", "Unit of record and boundary"],
                inventory,
            ),
            "## Appendix E Glossary",
            "The key gives general categories; retained records can carry a more conservative historical grade. The survey extraction keeps B for sampled papers and C for the GFI commissioned market survey. These grades are preserved for provenance and do not establish a new quality review.",
            table(["Term", "Meaning here"], glossary),
            news_text,
        ]
    )


def main() -> None:
    """Fail on unresolved placeholders and write the reader report deterministically."""
    template = (ROOT / "report/REPORT.template.md").read_text()
    template = template.replace(
        "package_p06_access_route_records", "package_p06_access_routes"
    ).replace("package_p06_contextual_source_records", "package_p06_contextual_routes")
    for key, builder in (
        ("benchmark_table", benchmark_table),
        ("studies_table", studies_table),
        ("outcomes_table", outcomes_table),
        ("policy_table", policy_table),
    ):
        template = template.replace("{{" + key + "}}", builder())

    def substitute(match: re.Match[str]) -> str:
        """Resolve a numeric or citation marker from its declared evidence table."""
        kind, value = match.groups()
        if kind == "claim":
            return claim(value)
        if kind in {"date", "year"}:
            return allowed(value, kind)
        key, label = value.split("|", 1)
        return cite(key, label)

    template = re.sub(r"\{\{(claim|date|year|cite):([^}]+)\}\}", substitute, template)
    template = template.replace("{{appendices}}", appendices())
    if "{{" in template:
        raise ValueError("Unresolved report marker")
    (ROOT / "report/REPORT.md").write_text(keep_compounds_together(template))
    print(
        json.dumps(
            {
                "report": "report/REPORT.md",
                "used_claims": len(USED),
                "source_rows": len(SOURCES),
                "template_words": len(
                    (ROOT / "report/REPORT.template.md").read_text().split()
                ),
            }
        )
    )


if __name__ == "__main__":
    main()
