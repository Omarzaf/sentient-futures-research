"""Stage bounded Pakistan company, policy and commercial forecast evidence."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/altprotein/pakistan"
ACCESS = "2026-10-13"
LICENSE = "Public access; reuse license not established; no publication authorized"


def write_csv(
    name: str, rows: list[dict[str, str]], fields: list[str] | None = None
) -> None:
    """Write reviewable staging rows without editing shared outputs."""
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plain(name: str) -> str:
    """Normalize visible HTML text for deterministic source assertions."""
    text = (RAW / name).read_text(errors="replace")
    text = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.IGNORECASE | re.DOTALL
    )
    return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", text)))


def sha(path: Path) -> str:
    """Hash raw or derived bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def company() -> list[dict[str, str]]:
    """Record rice-protein activity separately from cultivated/finished products."""
    text = (RAW / "matco-q3-2026.txt").read_text()
    assert "Rice Protein export volumes improved" in text
    assert "April 28, 2026" in text
    assert "processing and export of rice, rice glucose and rice protein" in text
    return [
        {
            "company": "Matco Foods Limited",
            "country": "Pakistan",
            "category": "Plant-based ingredient (rice protein)",
            "status": "commercial_production_and_exports_company_reported",
            "status_checked": ACCESS,
            "status_evidence_date": "2026-04-28",
            "source_id": "matco_q3_2026",
            "status_source_id": "matco_q3_2026",
            "corroborating_source_id": "matco_annual_2025",
            "tier": "C",
            "directory_url": "",
            "directory_id": "",
            "company_focus": "Food ingredients",
            "product_type": "Rice protein",
            "location": "Karachi, Pakistan",
            "evidence_locator": "Q3 filing PDF pages 4 and 9: product/facility profile and Rice Glucose Division discussion; page 10: directors date; page 22 note 1.1: processing/export business. Annual report PDF page 4 corroborates rice-protein product/facility.",
            "raw_file": "data/raw/altprotein/pakistan/matco-q3-2026.pdf",
            "raw_sha256": sha(RAW / "matco-q3-2026.pdf"),
            "notes": "Status reflects company-reported activity for nine months ended 2026-03-31, not independent plant inspection or current sales audit. Cover retains 2025 wording while filing body and directors date are 2026; body governs period. Ingredient supplier; not cultivated meat, a finished meat analogue, or proof of exclusively human-food end use. No standalone rice-protein sales value or quantity is extracted. Annual and quarterly evidence share the issuer; PSX hosting is not independent confirmation.",
        }
    ]


def market() -> list[dict[str, str]]:
    """Preserve publisher ranges as held provenance, excluded from numeric use."""
    text = plain("indexbox-synthetic-protein-pakistan.html")
    section = text.split("Market Forecast to 2035", 1)[1].split(
        "Market Opportunities", 1
    )[0]
    assert "Report Update Sep 21, 2026" in text
    assert "base-case volume CAGR of roughly 12-18% through 2035" in section
    assert "Upside scenarios see the market growing at 20-25% annually" in section
    assert "downside scenarios see growth closer to 8-12%" in section
    assert "MICROBIAL BIOMASS PROTEIN FOR FOOD AND FEED" in text
    assert "PLANT PROTEINS FROM TRADITIONAL AGRICULTURE" in text
    rows = []
    for scenario, low, high, metric in [
        ("base", "12", "18", "forecast_volume_cagr"),
        ("upside", "20", "25", "forecast_annual_market_growth"),
        ("downside", "8", "12", "forecast_annual_market_growth"),
    ]:
        rows.append(
            {
                "country": "Pakistan",
                "year": "2035",
                "segment": "synthetic_protein_food_feed_" + scenario + "_scenario",
                "metric": metric,
                "low": low,
                "central": "",
                "high": high,
                "unit": "percent_per_year",
                "source_id": "indexbox_synthetic_protein_pakistan_2026",
                "tier": "C",
                "evidence_status": "HELD_AI_METHOD_UNRESOLVED",
                "methodology_source_id": "indexbox_methodology_snapshot_20261013",
                "evidence_hold_reason": "Publisher methodology uses AI normalization, imputation and forecasting. The specific ranges' derivation is undisclosed, so compliance with the project's ban on AI-estimated numbers cannot be established. Held pending compatible source-specific evidence; not proof that these particular numbers were AI-generated.",
                "market_scope": "Pakistan synthetic proteins for food and feed; microbial biomass, precision fermentation, fungal mycoprotein and algal proteins; excludes conventional animal proteins and traditional agricultural plant proteins",
                "estimate_type": "source_published_commercial_growth_scenario_range",
                "range_semantics": "Separate source-published "
                + scenario
                + " scenario band; not confidence bounds. No central estimate is published and no midpoint is inferred.",
                "source_locator": "Visible report narrative: Market Forecast to 2035 section; "
                + scenario
                + " scenario. Base also repeated in Market Size and Growth. These precede the separate demo dashboard.",
                "method": "Direct transcription retained for provenance only. Opaque commercial model, not independently validated. Linked platform methodology uses AI/machine-learning normalization, imputation, smart extrapolation and regression. Pakistan-specific inputs, coefficients, uncertainty method and numerical baseline are undisclosed. Eligibility under the ban on AI-estimated numbers is unresolved; numeric use is withheld.",
                "source_date": "2026-09-21",
                "source_date_note": "Visible Report Update date.",
                "source_vintage": "2026 report; forecast horizon 2035",
                "stale": "false",
                "stale_note": "",
                "currency_basis": "Not a currency measure.",
                "segment_scope_note": "Not current sales, market size, retail revenue, or the complete alternative-protein market. Food and feed are not separable. "
                + (
                    "Base explicitly says volume CAGR."
                    if scenario == "base"
                    else "Upside/downside sentences call this market growth; value versus volume is not separately specified, so retain generic growth metric."
                ),
                "source_conflict": "Unrelated lower-page demo dashboards use differing forecast labels and are excluded. No values are taken from demo graphics.",
                "missing_reason": "Central estimate, exact CAGR base year, current market value/sales and source-specific numerical inputs not published.",
                "forecast_end_year": "2035",
                "forecast_start_year": "",
                "raw_file": "data/raw/altprotein/pakistan/indexbox-synthetic-protein-pakistan.html",
                "raw_sha256": sha(RAW / "indexbox-synthetic-protein-pakistan.html"),
                "notes": "HELD: preserve exact source ranges locally for provenance, exclude from dashboard numeric payloads and downloads. This supersedes earlier bounded range acceptance; absence of an LLM-generation disclaimer does not establish compliance with the broader AI-estimate ban. See notes/M5-AI-METHOD-ELIGIBILITY-2026-10-13.md.",
            }
        )
    return rows


def policies() -> list[dict[str, str]]:
    """Stage visually reviewed legal dates and bounded pathway descriptions."""
    rows = []

    def row(
        policy_id: str,
        authority: str,
        name: str,
        policy_date: str,
        date_precision: str,
        publication_date: str,
        pathway: str,
        source_id: str,
        locator: str,
        raw: str,
        stale: str = "false",
        notes: str = "",
    ) -> None:
        """Append one dated, source-limited regulatory pathway record."""
        rows.append(
            {
                "policy_id": policy_id,
                "country": "Pakistan",
                "jurisdiction": (
                    "Punjab province"
                    if authority == "Punjab Food Authority"
                    else "Pakistan"
                ),
                "authority": authority,
                "policy": name,
                "policy_date": policy_date,
                "date_precision": date_precision,
                "publication_date": publication_date,
                "checked_date": ACCESS,
                "pathway": pathway,
                "cultivated_specific_approval": "not_established_by_this_source",
                "source_id": source_id,
                "tier": "A",
                "source_locator": locator,
                "raw_file": "data/raw/altprotein/pakistan/" + raw,
                "raw_sha256": sha(RAW / raw),
                "stale": stale,
                "notes": notes,
            }
        )

    psqca = plain("psqca-halal.html")
    assert "PS:3733-2022" in psqca and "PS:4992-2022" in psqca
    row(
        "PK_PSQCA_HALAL_FOOD_2022",
        "Pakistan Standards and Quality Control Authority",
        "PS:3733-2022 (R), General Requirements for Halal Food",
        "2022",
        "year",
        "",
        "General halal food standard; modified adoption of OIC/SMIIC 1:2019 listed by official standardization authority.",
        "psqca_halal_standards_snapshot_20261013",
        "Established/Revised Pakistan Standards on Halal: PS:3733-2022 (R)",
        "psqca-halal.html",
        "true",
        "stale: standard edition predates 2024; current index was checked in 2026. Index establishes title and edition, not detailed clauses or cell-line/media eligibility. No novel-protein or cultivated approval is inferred.",
    )
    row(
        "PK_PSQCA_HALAL_BODIES_2022",
        "Pakistan Standards and Quality Control Authority",
        "PS:4992-2022 (R), Requirements for Bodies Providing Halal Certification",
        "2022",
        "year",
        "",
        "General conformity-assessment requirements for halal certification bodies; modified adoption of OIC/SMIIC 2:2019.",
        "psqca_halal_standards_snapshot_20261013",
        "Established/Revised Pakistan Standards on Halal: PS:4992-2022 (R)",
        "psqca-halal.html",
        "true",
        "stale: edition predates 2024. Certification-body standard is distinct from a product authorization; detailed clauses not reviewed.",
    )
    assert "21-05-2024" in (RAW / "pha-lhcb-2024.txt").read_text()
    row(
        "PK_PHA_LHCB_2024",
        "Pakistan Halal Authority",
        "Procedure for registration of local halal certification bodies",
        "2024-05-21",
        "day",
        "",
        "Registration criteria and verification process for certification bodies, with PS:4992-2022 among normative references.",
        "pha_lhcb_registration_2024",
        "PDF page 1 scope/references and pages 3-4 criteria/procedure; issue date 21-05-2024, revision 01",
        "pha-lhcb-2024.pdf",
        notes="This governs bodies that certify halal products, not direct approval of any cultivated product. No application or payment undertaken.",
    )
    row(
        "PK_PHA_MARK_FLOW_2024",
        "Pakistan Halal Authority",
        "Process flow for PHA halal certification mark license",
        "2024-12-02",
        "day",
        "",
        "Application and fee, documentation scrutiny, compliance approval, on-site inspection with sampling/testing if required, inspection review, and licensing decision.",
        "pha_mark_license_flowchart",
        "Single-page official process diagram, issue date 02-12-2024",
        "pha-halal-mark-flowchart.pdf",
        notes="General halal mark process; diagram does not authorize a named novel-protein product. No application or fee submission undertaken.",
    )
    row(
        "PK_PHA_MARK_OPERATIONAL_2025",
        "Pakistan Halal Authority",
        "Halal Certification Mark License Scheme operationalization",
        "2025-05-20",
        "day",
        "",
        "Official notification operationalizes the halal mark scheme and restricts mark display to licensed entities for the specific articles/processes covered by their license.",
        "pha_mark_operationalization_2025",
        "Official notification image: date at top; paragraphs 1-2",
        "pha-mark-operationalization.jpg",
        notes="Date visually read from signed notification; board approval 2025-04-16 is separate from notification date. General halal licensing, not blanket cultivated-meat approval.",
    )
    row(
        "PK_PFA_PRODUCT_REGISTRATION_2017",
        "Punjab Food Authority",
        "Product Registration and Display of PFA Logo Regulations 2017",
        "2017-03-13",
        "day",
        "2017-03-15",
        "Regulations require Certificate of Product Registration for relevant food business activity; issue depends on food safety, quality, labeling and hygiene conformity. Official current webpage describes ingredient, analysis, halal and label documents.",
        "pfa_product_registration_regulations_2017",
        "PDF pages 2-4 (printed 5023-5025), notification and Part II sections 5-6; current website corroborates procedure",
        "pfa-registration-regulations-2017.pdf",
        "true",
        "stale: original regulation predates 2024, retained as current-linked background; HTML corroboration pfa_product_registration_snapshot_20261013. Punjab scope only; no cultivated-specific license or exemption inferred.",
    )
    row(
        "PK_PFA_FUNCTIONAL_NOVEL_2025",
        "Punjab Food Authority",
        "Functional Foods/Food Supplements Regulations 2025",
        "2025-11-27",
        "day",
        "2026-09-04",
        "Within functional foods/food supplements, defines novel food by absent consumption history or significant change from new technology; provides scientific-evaluation and claim-evidence requirements and prior approval for relevant plant/botanical functional foods.",
        "pfa_functional_food_regulations_2025",
        "PDF pages 1-2 dates/objective; page 4 section 4(23); page 6 sections 5(4) and 6; page 7 sections 7-9",
        "pfa-functional-food-2025.pdf",
        notes="Scanned document visually reviewed. Notification date 2025-11-27 and Gazette publication 2026-09-04 preserved; /2023/05/ URL is not policy date. These are general functional-food/novel-food provisions, not an explicit cultivated-meat authorization. Applicability to a specific novel product requires regulator determination; no submitted inquiry or application.",
    )
    return rows


def provenance() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Register every acquired/derived file, including unused partial evidence."""
    acquisitions = []
    for path in sorted(OUT.glob("acquisitions*.json")):
        acquisitions.extend(json.loads(path.read_text()))
    for item in acquisitions:
        if item["source_id"] == "pha_mark_operationalization_2024":
            item["source_id"] = "pha_mark_operationalization_2025"
    metadata = {
        "pak_bsf_pilot_app_2024": (
            "Black Soldier Fly poultry-feed pilot launch ordered",
            "Associated Press of Pakistan",
            "2024",
            "C",
            "State news agency report dated 2024-08-23; announced pilot only. Poultry-feed context, no capacity or subsequent commissioning verified. UrduPoint carries the same APP wire and is not independent corroboration.",
        ),
        "matco_annual_2025": (
            "Annual Report 2025",
            "Matco Foods Limited / Pakistan Stock Exchange",
            "2025",
            "C",
            "Issuer annual report; company-reported operation, not independent certification.",
        ),
        "matco_q3_2026": (
            "Third quarterly report: nine months ended March 31 2026",
            "Matco Foods Limited",
            "2026",
            "C",
            "Unaudited interim filing; directors date 2026-04-28. Cover says 2025 but financial body says 2026. Rice-protein sales are not separately quantified.",
        ),
        "ful_foods_public_snapshot_20261013": (
            "Ful Foods: duckweed-based animal feed",
            "Ful Foods",
            "",
            "C",
            "Excluded from human-food company output: animal feed product development/trials. Self-reported numerical trial results are not extracted.",
        ),
        "nutrasoy_public_snapshot_20261013": (
            "Nutrasoy: About",
            "Nutrasoy",
            "2026",
            "C",
            "Candidate only. Self-authored soy milk/tofu catalog; JSON-LD says published 2025-10-23 and modified 2026-05-14 but retains unrelated cosmetics organization metadata. Not independently dated commercial activity.",
        ),
        "pakistan_altprotein_market_6w_2026": (
            "Pakistan Food Alternative Protein Market 2026-2032",
            "6Wresearch",
            "2026",
            "C",
            "Visible update February 2026; public summary lacks market size and scenario bands. Percentage trade changes excluded; no undisclosed HS definitions inferred. Request/purchase is human-gated.",
        ),
        "pakistan_meat_substitutes_market_wms_2025": (
            "Pakistan Meat Substitutes Market: analysis and forecast",
            "Williams & Marshall Strategy via MarketResearch.com",
            "2025",
            "C",
            "Public search fallback read dated 2025-03-03. Paid report advertises pessimistic/base/optimistic scenarios but not their values. Curl failed; Rill denied before tab creation. No values extracted.",
        ),
        "psqca_halal_standards_snapshot_20261013": (
            "PSQCA Halal Division and standards list",
            "Pakistan Standards and Quality Control Authority",
            "2022",
            "A",
            "Official index lists 2022 editions; stale original edition. Full clauses not reviewed and no cultivated approval inferred.",
        ),
        "pha_downloads_snapshot_20261013": (
            "PHA public downloads",
            "Pakistan Halal Authority",
            "",
            "A",
            "Undated official index; original linked documents retain their own issue dates.",
        ),
        "pha_newsletter_2025": (
            "PHA Newsletter 2025",
            "Pakistan Halal Authority",
            "2025",
            "A",
            "Download timed out and retained partial PDF is invalid. Not used for policy extraction.",
        ),
        "pfa_product_registration_snapshot_20261013": (
            "PFA Product Registration",
            "Punjab Food Authority",
            "",
            "A",
            "Undated current page describes general registration and cites 2017 regulations; not a new regulation date.",
        ),
        "pfa_gazette_snapshot_20261013": (
            "PFA Gazette and Notifications",
            "Punjab Food Authority",
            "",
            "A",
            "Official link index; date of underlying gazette checked in PDF, not inferred from upload URL.",
        ),
        "pha_mark_operationalization_2025": (
            "Halal certification mark license scheme operationalization notification",
            "Pakistan Halal Authority",
            "2025",
            "A",
            "Signed image visually checked, dated 2025-05-20. Restricts mark to articles/processes covered by license.",
        ),
        "pha_mark_license_flowchart": (
            "Process flow diagram for PHA Halal Certification Mark License",
            "Pakistan Halal Authority",
            "2024",
            "A",
            "Issue date 2024-12-02, revision 01. General mark procedure, not a product approval.",
        ),
        "pha_lhcb_registration_2024": (
            "Procedure for registration of local halal certification bodies",
            "Pakistan Halal Authority",
            "2024",
            "A",
            "Issue date 2024-05-21, revision 01. Certifier registration, not a specific product approval.",
        ),
        "indexbox_synthetic_protein_pakistan_2026": (
            "Pakistan Synthetic Protein Market 2026 Analysis and Forecast to 2035",
            "IndexBox",
            "2026",
            "C",
            "Visible update 2026-09-21; source-published scenario growth bands. Food/feed mixed, opaque commercial model; no current market size. Narrative ranges are not in lower-page Demo panels. No central estimate. Linked general methodology uses AI/statistical imputation and extrapolation; specific inputs not disclosed.",
        ),
        "pfa_product_registration_regulations_2017": (
            "Food Authority Product Registration and Display of PFA Logo Regulations 2017",
            "Punjab Food Authority / Punjab Gazette",
            "2017",
            "A",
            "stale: notification 2017-03-13, Gazette 2017-03-15. Scanned PDF has blank first page; pages 2-4 visually reviewed.",
        ),
        "pfa_functional_food_regulations_2025": (
            "Punjab Food Authority Functional Foods/Food Supplements Regulations 2025",
            "Punjab Food Authority / Punjab Gazette",
            "2026",
            "A",
            "Notification 2025-11-27, Gazette 2026-09-04. Scanned PDF; relevant pages visually reviewed. General novel-food provisions do not establish cultivated approval.",
        ),
        "indexbox_terms_snapshot_20261013": (
            "IndexBox Terms and Policies",
            "IndexBox",
            "",
            "C",
            "Read-only supporting source for disclosure assessment. No LLM-generation disclaimer identified for specific report.",
        ),
        "indexbox_methodology_snapshot_20261013": (
            "IndexBox Metadata and Definitions / Research Methodology and AI Platform",
            "IndexBox",
            "",
            "C",
            "Publisher describes statistical normalization, missing-data treatment, extrapolation/regression and analyst review, but no Pakistan synthetic-protein inputs.",
        ),
    }
    unique = {item["source_id"]: item for item in acquisitions}
    source_rows = []
    for sid, item in unique.items():
        title, publisher, year, tier, notes = metadata[sid]
        source_rows.append(
            {
                "source_id": sid,
                "title": title,
                "publisher": publisher,
                "url": item["url"],
                "year": year,
                "accessed": ACCESS,
                "tier": tier,
                "access_method": (
                    "curl public file/page; source-specific visual PDF or image inspection where noted"
                    if item["returncode"] == "0"
                    else "curl failed; public web search fallback reviewed"
                ),
                "license": LICENSE,
                "notes": notes,
            }
        )
    originals = {
        Path(item["file"]).name: item
        for item in acquisitions
        if (ROOT / item["file"]).exists()
    }
    manifest = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        if path.name in originals:
            item = originals[path.name]
            note = (
                "Original downloaded bytes."
                if item["returncode"] == "0"
                else "INCOMPLETE transfer, curl error "
                + item["returncode"]
                + "; unused as evidence; preserved for audit."
            )
            accessed = item["accessed_utc"]
        else:
            stems = [(Path(name).stem, data) for name, data in originals.items()]
            matches = [
                (stem, data)
                for stem, data in stems
                if path.stem == stem or path.stem.startswith(stem + "-")
            ]
            assert matches, f"No raw parent for {path.name}"
            _, item = max(matches, key=lambda pair: len(pair[0]))
            accessed = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
            note = "Derived locally with pdftotext -layout or pdftoppm. Scanned PFA PDF text may be blank; rendered images govern visual review."
        manifest.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": item["url"],
                "accessed_utc": accessed,
                "sha256": sha(path),
                "license": LICENSE,
                "source_id": item["source_id"],
                "notes": note,
            }
        )
    return source_rows, manifest


def insect_context() -> list[dict[str, str]]:
    """Preserve Pakistan insect pilot evidence with unreported capacity missing."""
    text = plain("app-bsf-pilot-2024.html")
    assert "ordered to launch a pilot project" in text
    assert "Air University Multan" in text
    return [
        {
            "country": "Pakistan",
            "source_type": "insect_black_soldier_fly",
            "year": "2024",
            "metric": "announced_poultry_feed_pilot_capacity_unreported",
            "value": "",
            "unit": "",
            "source_id": "pak_bsf_pilot_app_2024",
            "tier": "C",
            "category": "insect_feed_pilot",
            "raw_file": "data/raw/altprotein/pakistan/app-bsf-pilot-2024.html",
            "raw_locator": "Report dated 2024-08-23; opening paragraphs on Punjab Secretary Livestock visit to Air University Multan",
            "method": "Qualitative source report; no capacity, operating output, sales, or protein yield quantified.",
            "notes": "Poultry feed pilot launch was ordered; source does not establish commissioning or commercial operation. Not human-food approval. Capacity and current operating status missing, not zero. UrduPoint carries the same APP wire; no independent corroboration found in this bounded pass.",
            "checked": ACCESS,
            "entity": "Punjab Livestock Department / Air University Multan research context",
            "evidence_status": "pilot_launch_ordered_current_status_unknown",
            "freshness": "dated_2024_report_current_status_unknown",
            "location": "Punjab, Pakistan",
            "period": "2024-08-23",
            "source_value": "",
        }
    ]


def main() -> None:
    """Build and audit all staging outputs without changing shared files."""
    companies, markets, policy_rows = company(), market(), policies()
    source_rows, manifest = provenance()
    write_csv("company_rows.csv", companies)
    write_csv("capacity_rows.csv", insect_context())
    write_csv("market_rows.csv", markets)
    write_csv("policy_rows.csv", policy_rows)
    write_csv("source_rows.csv", source_rows)
    write_csv("manifest_rows.csv", manifest)
    source_ids = {row["source_id"] for row in source_rows}
    assert len(source_ids) == len(source_rows)
    for rows in [companies, markets, policy_rows, manifest]:
        assert all(row["source_id"] in source_ids for row in rows)
    assert all(
        not row["central"] and float(row["low"]) < float(row["high"]) for row in markets
    )
    assert all(sha(ROOT / row["file"]) == row["sha256"] for row in manifest)
    assert len({row["file"] for row in manifest}) == len(list(RAW.iterdir()))
    print(
        json.dumps(
            {
                "companies": len(companies),
                "market_ranges": len(markets),
                "policy_pathways": len(policy_rows),
                "sources": len(source_rows),
                "raw_manifest": len(manifest),
                "status": "staging checks passed",
            }
        )
    )


if __name__ == "__main__":
    main()
