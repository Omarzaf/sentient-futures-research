"""Build source-bound revision tables without modifying shared dashboard data."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/altprotein/supervisor_revision_20261013"
DATE = "2026-10-13"


def rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV with original string values and BOM support."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, records: list[dict[str, str]]) -> None:
    """Write a staged CSV using the union of the supplied columns."""
    fields = list(dict.fromkeys(key for record in records for key in record))
    with (HERE / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def digest(path: Path) -> str:
    """Return the saved file's SHA-256."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(filename: str) -> dict[str, str]:
    """Bind a record to a newly retrieved original response."""
    path = RAW / filename
    return {"raw_file": str(path.relative_to(ROOT)), "raw_sha256": digest(path)}


def main() -> None:
    """Build the reviewable company, policy, listing and evidence batches."""
    source_definitions = [
        (
            "supervisor_uncrave_inc42_20250909",
            "UnCrave discontinuation reported by Inc42",
            "Inc42",
            "2025",
            "C",
            "uncrave-inc42.html",
            "Published 2025-09-09; reports completed discontinuation after gradual winding down. Exact effective closure date unstated; no company response reported.",
        ),
        (
            "supervisor_uncrave_etretail_20251014",
            "ETRetail reports Licious discontinued UnCrave",
            "ETRetail",
            "2025",
            "C",
            "uncrave-etretail.html",
            "Published 2025-10-14; separately reports September closure. News corroboration, not company confirmation or an exact closure-day record.",
        ),
        (
            "supervisor_fssai_dairy_consultation_20250416",
            "Consultation on compliance with provisions of Analogue in Dairy Context",
            "FSSAI",
            "2025",
            "A",
            "fssai-dairy-consultation-20250416.pdf",
            "Notice 2025-04-16 and enclosed four-page consultation. Existing requirements and consultation proposals are separate; this is not a final new labelling rule.",
        ),
        (
            "supervisor_fssai_vegan_20220610",
            "Food Safety and Standards (Vegan Foods) Regulations 2022",
            "FSSAI / Gazette of India; facsimile hosted by FAOLEX",
            "2022",
            "A",
            "fssai-vegan-original-2022-faolex.pdf",
            "Original Gazette facsimile: notification 2022-06-10, issue 2022-06-14, electronic identifier 2022-06-16. English text PDF pages 3-4; later amendments recorded separately.",
        ),
        (
            "supervisor_fssai_vegan_amendment_20260521",
            "Food Safety and Standards (Vegan Foods) Amendment Regulations 2026",
            "FSSAI / Gazette of India",
            "2026",
            "A",
            "fssai-vegan-amendment-20260521-official.pdf",
            "Notification 2026-05-21; rule 1(2) specifies commencement 2027-07-01. Logo specifications; notified but not yet in force on observation date. Legacy URL returned an HTML shell; current /docs URL supplies the PDF.",
        ),
        (
            "supervisor_fssai_vegan_amendment_20260928",
            "Food Safety and Standards (Vegan Foods) Second Amendment Regulations 2026",
            "FSSAI / Gazette of India",
            "2026",
            "A",
            "fssai-vegan-amendment-20260928-egazette.pdf",
            "Notification 2026-09-28, Gazette issue 2026-09-29, electronic identifier 2026-10-05; rule 1(2) specifies commencement 2027-04-01. Form-I for exporting-country certification; future commencement retained.",
        ),
        (
            "supervisor_phyx44_snapshot_20261013",
            "Phyx44 public product and technology page",
            "Phyx44",
            "",
            "C",
            "phyx44-fresh.html",
            "Undated company-authored page observed on access date. Precision-fermentation functional food proteins; no independent output, sales or approval verification. India identity corroborated by older country-specific source, not Pakistan.",
        ),
        (
            "supervisor_nutrasoy_snapshot_20261013",
            "Nutrasoy public soy milk and tofu catalogue",
            "Nutrasoy",
            "",
            "C",
            "nutrasoy.html",
            "Undated company-authored catalogue observed on access date; Lahore/Pakistan location stated. Human-food candidate, not independently audited production, sales, stock or meat-analogue activity.",
        ),
        (
            "supervisor_ayfoods_products_20261013",
            "A&Y Foods frozen-product catalogue",
            "A&Y Food Industries",
            "",
            "C",
            "ayfoods-products.html",
            "URL without PDF suffix returns original PDF. Page 1 lists soy meatless shami and chapli products and Karachi location. Undated catalogue, not domestic retail availability. Chapli description and weight columns conflict; no quantities extracted.",
        ),
        (
            "supervisor_ayfoods_home_20261013",
            "A&Y Food Industries public home page",
            "A&Y Food Industries",
            "",
            "C",
            "ayfoods-home.html",
            "Current public company site. Same-issuer corroboration only; not independent licensing, operating-scale or transaction evidence.",
        ),
        (
            "supervisor_ghaas_phoos_greenqueen_20250815",
            "Interview on Ghaas Phoos plant-based foods in Karachi",
            "Green Queen",
            "2025",
            "C",
            "ghaas-phoos-greenqueen.html",
            "Visible publication 2025-08-15 and earlier last-updated date 2025-08-14 both preserved. Founder-reported meal delivery and soy kebabs/patties; planned retail expansion is not completed retail distribution.",
        ),
        (
            "supervisor_nifdo_puris_listing_20261013",
            "NIFDO PURIS textured pea-protein import listing",
            "NIFDO",
            "",
            "C",
            "nifdo-puris.html",
            "Observed import-to-order offer in Pakistan. Page says it imports from Amazon USA and is not a retailer/manufacturer. No stock, completed order, pack net weight or final landed price verified.",
        ),
        (
            "supervisor_fssai_vegan_amendments_index_20261013",
            "FSSAI vegan-amendment navigation and public application assets",
            "FSSAI",
            "",
            "A",
            "fssai-vegan-amendments-index.html",
            "Supporting navigation evidence only. HTML response is an application shell; saved public JavaScript identifies dated amendment entries. Regulatory claims bind to separate authentic PDF sources, not these assets.",
        ),
        (
            "supervisor_fssai_regulations_index_20261013",
            "FSSAI regulations page response",
            "FSSAI",
            "",
            "A",
            "fssai-regulations-index.html",
            "Retrieval diagnostic only: HTTP 200 returns an application shell, not substantive regulation text. No legal claim relies on this response.",
        ),
    ]
    fetches = [
        json.loads(line) for line in (HERE / "fetch-log.jsonl").read_text().splitlines()
    ]
    fetch_by_file = {item["file"]: item for item in fetches}
    recovered_receipts = {
        "phyx44.html": "phyx44-recheck.html",
        "fssai-public-app.js": "fssai-public-app-recheck.js",
    }
    for original, repeated in recovered_receipts.items():
        if digest(RAW / original) != digest(RAW / repeated):
            raise ValueError(
                f"Re-retrieval differs from un-timestamped original: {original}"
            )
    sources = []
    for source_id, title, publisher, year, tier, filename, notes in source_definitions:
        fetch = fetch_by_file[filename]
        sources.append(
            {
                "source_id": source_id,
                "title": title,
                "publisher": publisher,
                "url": fetch["url"],
                "year": year,
                "accessed": DATE,
                "tier": tier,
                "access_method": "Public curl GET; saved original bytes; PDF text and source-locator review",
                "license": "Public access; redistribution licence not established; originals remain local",
                "notes": notes,
            }
        )
    write_csv("source_rows.csv", sources)

    policies = rows(HERE / "baseline_policy_rows.csv")
    for row in policies:
        row["stale"] = str(int(row["policy_date"][:4]) < 2025).lower()
        row["freshness"] = (
            "historical_instrument_pre2025"
            if row["stale"] == "true"
            else "dated_evidence_2025_or_later"
        )
        row["notes"] = row["notes"].replace("predates 2024", "predates 2025")
        row["application_date"] = ""
        row["effective_date"] = ""
        row["effective_date_basis"] = (
            "Not established independently; policy_date retains original event basis."
        )
        if row["country"] == "Pakistan":
            row["date_basis"] = (
                row["date_basis"]
                or "Date of the named instrument, not product approval or live operations."
            )
            row["status"] = {
                "PK_PSQCA_HALAL_FOOD_2022": "officially_listed_general_halal_standard",
                "PK_PSQCA_HALAL_BODIES_2022": "officially_listed_certification_body_standard",
                "PK_PHA_LHCB_2024": "dated_certification_body_registration_procedure",
                "PK_PHA_MARK_FLOW_2024": "dated_general_halal_mark_process",
                "PK_PHA_MARK_OPERATIONAL_2025": "general_halal_mark_scheme_operationalization_notified",
                "PK_PFA_PRODUCT_REGISTRATION_2017": "general_product_registration_regulations_published",
                "PK_PFA_FUNCTIONAL_NOVEL_2025": "functional_food_regulations_notified_and_gazetted",
            }.get(
                row["policy_id"],
                "dated_general_instrument_product_approval_not_established",
            )
        if row["policy_id"] == "PK_PFA_FUNCTIONAL_NOVEL_2025":
            row["date_basis"] = (
                "Notification dated 2025-11-27; Gazette publication separately dated 2026-09-04."
            )
            row["effective_date_basis"] = (
                "Section 1(2) says at once; no separate calendar commencement date inferred from delayed Gazette publication."
            )
            row[
                "notes"
            ] += " New visual re-read confirms PDF pages 1, 2 and 6. Section 6 defines novel foods within this functional-food/supplement instrument; a cultivated-specific route or approval was not established."
        if row["source_id"] == "india_fssai_nsf_status_20260901":
            row["application_date"] = "2025-08-20"
            row["date_basis"] = (
                "List as-of date; application filing date 2025-08-20 stored separately."
            )
            row["source_locator"] = (
                "PDF page 66 row 28, application 80/Std/PA/FSSAI/2025, filing 20.08.2025; PDF page 79 stage legend"
            )

    def policy(
        source_id: str,
        policy_id: str,
        title: str,
        date: str,
        status: str,
        locator: str,
        pathway: str,
        filename: str,
        effective: str = "",
        publication: str = "",
        notes: str = "",
    ) -> dict[str, str]:
        """Construct a separately dated policy event with a raw source binding."""
        return {
            "country": "India",
            "status": status,
            "source_id": source_id,
            "corroborating_source_id": "",
            "notes": notes,
            "freshness": (
                "historical_instrument_pre2025"
                if int(date[:4]) < 2025
                else "dated_evidence_2025_or_later"
            ),
            "tier": "A",
            "policy": title,
            "policy_id": policy_id,
            "authority": "FSSAI",
            "jurisdiction": "India",
            "policy_date": date,
            "date_basis": "Dated notice; publication and commencement separately recorded where established.",
            "date_precision": "day",
            "checked_date": DATE,
            "pathway": pathway,
            "source_locator": locator,
            "stale": str(int(date[:4]) < 2025).lower(),
            "cultivated_specific_approval": "not_established_by_this_source",
            "publication_date": publication,
            **binding(filename),
            "application_date": "",
            "effective_date": effective,
            "effective_date_basis": (
                "Express rule 1(2) commencement"
                if effective
                else (
                    "Not applicable: consultation is not a notified new rule."
                    if "CONSULTATION" in policy_id
                    else "Original rule commences on Gazette publication; exact electronic/public availability distinction retained in notes."
                )
            ),
        }

    policies.extend(
        [
            policy(
                "supervisor_fssai_vegan_20220610",
                "IN_FSSAI_VEGAN_2022",
                "Food Safety and Standards (Vegan Foods) Regulations 2022",
                "2022-06-10",
                "notified_vegan_food_framework_later_amendments_separate",
                "PDF pages 3-4, regulations 2-5; front page Gazette issue and electronic identifier",
                "Defines vegan food and requires production, traceability, labelling and endorsement compliance; no cultivated-meat approval follows.",
                "fssai-vegan-original-2022-faolex.pdf",
                publication="2022-06-14",
                notes="Gazette issue dated June 14; electronic identifier June 16. 2026 amendments have future commencement dates and do not disappear into this historical event.",
            ),
            policy(
                "supervisor_fssai_dairy_consultation_20250416",
                "IN_FSSAI_DAIRY_ANALOGUE_CONSULTATION_2025",
                "Consultation on compliance with Analogue in Dairy Context provisions",
                "2025-04-16",
                "consultation_paper_not_final_new_rule",
                "Notice PDF page 1; Annexure-1 pages 2-5, sections B and C",
                "Requests comments on nomenclature, ingredient disclosure and food-service/menu communication; separates existing rules from consultation proposals.",
                "fssai-dairy-consultation-20250416.pdf",
                notes="Do not relabel this consultation as a notified dairy-analogue labelling amendment. Later finalization not established in this source.",
            ),
            policy(
                "supervisor_fssai_vegan_amendment_20260521",
                "IN_FSSAI_VEGAN_LOGO_AMENDMENT_2026",
                "Vegan Foods Amendment Regulations 2026: logo specification",
                "2026-05-21",
                "notified_future_commencement",
                "PDF page 3 regulation 1(2) and regulation 2; page 4 logo specification",
                "Amends the vegan-logo specification, with commencement explicitly deferred to 2027-07-01.",
                "fssai-vegan-amendment-20260521-official.pdf",
                effective="2027-07-01",
                publication="2026-05-25",
                notes="Gazette issue May 25 and electronic identifier June 2; future commencement is not a current effective requirement.",
            ),
            policy(
                "supervisor_fssai_vegan_amendment_20260928",
                "IN_FSSAI_VEGAN_IMPORT_AMENDMENT_2026",
                "Vegan Foods Second Amendment Regulations 2026: import certificate",
                "2026-09-28",
                "notified_future_commencement",
                "PDF page 4 regulation 1(2) and regulation 2; pages 4-6 Form-I",
                "Amends regulation 5(3) and inserts Form-I for exporting-country certificates for vegan-logo endorsement; commencement 2027-04-01.",
                "fssai-vegan-amendment-20260928-egazette.pdf",
                effective="2027-04-01",
                publication="2026-09-29",
                notes="Gazette issue September 29 and electronic identifier October 5; future commencement is not a current effective requirement.",
            ),
        ]
    )
    pib_path = ROOT / "data/raw/altprotein/india_policy/pib-bioe3-platforms-2026.html"
    pib = {key: "" for key in policies[0]}
    pib.update(
        {
            "country": "India",
            "status": "official_implementation_update",
            "source_id": "india_pib_bioe3_platforms_2026",
            "tier": "A",
            "policy": "BioE3 parliamentary implementation update",
            "policy_id": "IN_BIOE3_IMPLEMENTATION_20260311",
            "authority": "Department of Biotechnology / BIRAC; parliamentary answer via PIB",
            "jurisdiction": "India",
            "policy_date": "2026-03-11",
            "date_basis": "PIB publication date; not each facility's commissioning date",
            "date_precision": "day",
            "checked_date": DATE,
            "freshness": "dated_evidence_2025_or_later",
            "stale": "false",
            "pathway": "Reports Biofoundry Network and Biomanufacturing Platforms with functional foods and smart proteins among multiple sectors.",
            "source_locator": "Posted On 11 MAR 2026; opening implementation paragraphs; Annexure I",
            "cultivated_specific_approval": "not_established_by_this_source",
            "raw_file": str(pib_path.relative_to(ROOT)),
            "raw_sha256": digest(pib_path),
            "notes": "Shared infrastructure across sectors; facility counts and vessel sizes are not alternative-protein annual output, food approval, adoption or realised sales.",
        }
    )
    policies.append(pib)
    write_csv("policy_rows.csv", policies)

    companies = rows(HERE / "baseline_company_rows.csv")
    excluded = []
    kept = []
    for row in companies:
        row.update(
            {
                "inclusion_status": "human_food_or_food_ingredient_evidence",
                "application_date": "",
                "closure_effective_date": "",
                "closure_reported_date": "",
            }
        )
        if row["company"] == "String Bio":
            row["inclusion_status"] = "excluded_feed_only_in_reviewed_evidence"
            feed_path = (
                ROOT / "data/raw/altprotein/companies/string-animal-nutrition.html"
            )
            row["raw_file"] = str(feed_path.relative_to(ROOT))
            row["raw_sha256"] = digest(feed_path)
            row[
                "notes"
            ] += " Apply the same feed-only exclusion as Ful Foods; this does not establish that the company has no human-food R&D."
            excluded.append(row)
            continue
        if row["company"] == "Biokraft Foods":
            row["application_date"] = "2025-08-20"
            filing_path = (
                ROOT
                / "data/raw/altprotein/india_policy/fssai-nsf-status-2026-09-01.pdf"
            )
            row["raw_file"] = str(filing_path.relative_to(ROOT))
            row["raw_sha256"] = digest(filing_path)
        if row["company"] == "Country Delight":
            row["inclusion_status"] = "adjacent_plant_dairy_product_line"
        if row["company"] == "Matco Foods Limited":
            row["evidence_date_precision"] = "day"
            row["geographic_basis"] = (
                "Pakistan/Karachi location in issuer filing; activity and end-use split remain company reported."
            )
            row["inclusion_status"] = "adjacent_food_ingredient_mixed_end_use"
        kept.append(row)

    def company(
        name: str,
        country: str,
        category: str,
        status: str,
        source_id: str,
        date: str,
        filename: str,
        locator: str,
        note: str,
        scope: str = "human_food_or_food_ingredient_evidence",
        corroborating: str = "",
    ) -> dict[str, str]:
        """Construct a bounded company observation without asserting audited activity."""
        return {
            "company": name,
            "country": country,
            "category": category,
            "status": status,
            "status_checked": DATE,
            "source_id": source_id,
            "status_source_id": source_id,
            "status_evidence_date": date,
            "evidence_date_precision": (
                "day" if date else "unknown_publication_date; access_date_only"
            ),
            "supplemental_source_ids": corroborating,
            "category_source_id": source_id,
            "directory_id": "",
            "directory_url": "",
            "evidence_locator": locator,
            "geographic_basis": "Geography explicitly identified in cited source; no inference from country-specific advertising alone.",
            "notes": note,
            "tier": "C",
            "company_focus": category,
            "corroborating_source_id": corroborating,
            "location": "",
            "product_type": category,
            **binding(filename),
            "inclusion_status": scope,
            "application_date": "",
            "closure_effective_date": "",
            "closure_reported_date": "",
        }

    uncrave = company(
        "UnCrave (Licious)",
        "India",
        "plant-based meat brand",
        "closed",
        "supervisor_uncrave_inc42_20250909",
        "2025-09-09",
        "uncrave-inc42.html",
        "Visible publication date and opening report; ETRetail 2025-10-14 closing paragraph",
        "Closure is news-reported and corroborated, with no company confirmation recovered. September 9 is the report date, not a proven last trading day. Exact effective closure date remains unknown.",
        corroborating="supervisor_uncrave_etretail_20251014",
    )
    uncrave["closure_reported_date"] = "2025-09-09"
    kept.extend(
        [
            uncrave,
            company(
                "Ghaas Phoos Plant-Based Foods",
                "Pakistan",
                "plant-based prepared meals; soy kebabs and patties",
                "2025_meal_delivery_founder_reported; current_operations_unverified",
                "supervisor_ghaas_phoos_greenqueen_20250815",
                "2025-08-15",
                "ghaas-phoos-greenqueen.html",
                "Visible publication date; section on retail and foodservice expansion",
                "Founder interview places beta meal delivery in Karachi. Retail/frozen expansion was a plan; no current retail stock or audited sales established. Article last-updated date precedes publication by one day; both retained in source note.",
            ),
            company(
                "A&Y Food Industries",
                "Pakistan",
                "soy meatless shami and chapli products",
                "undated_manufacturer_catalogue_observed; current_stock_unverified",
                "supervisor_ayfoods_products_20261013",
                "",
                "ayfoods-products.html",
                "PDF page 1, product rows 24 and 26; company location header",
                "Company catalogue lists meatless soy products in Karachi. Undated catalogue and same-issuer site do not prove domestic retail availability, realised production or sales. Contradictory chapli unit weights are not extracted.",
                corroborating="supervisor_ayfoods_home_20261013",
            ),
            company(
                "Nutrasoy",
                "Pakistan",
                "traditional soy foods; tofu and plant dairy",
                "undated_company_catalogue_observed; operations_unverified",
                "supervisor_nutrasoy_snapshot_20261013",
                "",
                "nutrasoy.html",
                "Featured tofu/soy milk products; Pakistan/Lahore footer",
                "Human-food catalogue meets the stated food/feed rule but remains adjacent to the meat-analogue question. Earlier website-template metadata defects remain unresolved; no independent production, stock, sales or vegan-certification verification.",
                scope="adjacent_traditional_soy_and_plant_dairy",
                corroborating="nutrasoy_public_snapshot_20261013",
            ),
            company(
                "Phyx44",
                "India",
                "precision-fermentation functional food proteins",
                "undated_company_portfolio_observed; commercial_approval_unverified",
                "supervisor_phyx44_snapshot_20261013",
                "",
                "phyx44-fresh.html",
                "Company portfolio and precision-fermentation description; India identity in older FoodTechBiz report",
                "India company, not Pakistan coverage. Functional food ingredients include savoury applications; animal-free and health descriptions are company claims. No commercial capacity, approval or revenue figure extracted.",
                scope="adjacent_functional_food_ingredients",
                corroborating="m6_public31_b31_ft_phyx",
            ),
        ]
    )
    ful_raw = ROOT / "data/raw/altprotein/pakistan/ful-foods.html"
    ful = {key: "" for key in excluded[0]}
    ful.update(
        {
            "company": "Ful Foods",
            "country": "Pakistan",
            "category": "duckweed-based animal feed",
            "status": "feed_development_company_reported",
            "status_checked": DATE,
            "source_id": "ful_foods_public_snapshot_20261013",
            "status_source_id": "ful_foods_public_snapshot_20261013",
            "category_source_id": "ful_foods_public_snapshot_20261013",
            "tier": "C",
            "inclusion_status": "excluded_feed_only_in_reviewed_evidence",
            "evidence_date_precision": "unknown_publication_date; access_date_only",
            "evidence_locator": "Company page title and animal-feed product description",
            "geographic_basis": "Company page identifies Pakistan; legal domicile and operating scale are not independently verified.",
            "notes": "Same feed-only rule as String Bio. Exclusion from human-food table does not imply no business or no research; no numerical trial claims used.",
            "raw_file": str(ful_raw.relative_to(ROOT)),
            "raw_sha256": digest(ful_raw),
        }
    )
    excluded.append(ful)
    write_csv("company_rows.csv", kept)
    write_csv("company_exclusions.csv", excluded)
    write_csv(
        "retail_listing_rows.csv",
        [
            {
                "listing_id": "PK_NIFDO_PURIS_20261013",
                "country": "Pakistan",
                "seller": "NIFDO",
                "product": "PURIS Pantry Textured Pea Protein",
                "category": "textured plant protein marketed as meat substitute",
                "observed_date": DATE,
                "source_id": "supervisor_nifdo_puris_listing_20261013",
                "tier": "C",
                "quoted_price": "11992",
                "currency": "PKR",
                "pack_net_weight": "",
                "unit_price": "",
                "availability_status": "import_to_order_offer; stock_and_fulfilment_unverified",
                "transaction_observed": "false",
                "source_locator": "Product title and discount price; Important guidelines state Amazon USA import after order confirmation",
                "notes": "Offer only; importer expressly distinguishes itself from a local retailer/manufacturer. No purchase, stock check, price-per-kg conversion or national market-size inference.",
                **binding("nifdo-puris.html"),
            }
        ],
    )

    manifests = []
    for path in sorted(RAW.iterdir()):
        if not path.is_file():
            continue
        origin = fetch_by_file.get(path.name)
        recovered = path.name in recovered_receipts
        if recovered:
            origin = fetch_by_file[recovered_receipts[path.name]]
        if origin is None and path.suffix == ".txt":
            origin = next(
                (
                    fetch_by_file.get(path.with_suffix(ext).name)
                    for ext in (".html", ".pdf")
                    if fetch_by_file.get(path.with_suffix(ext).name)
                ),
                None,
            )
            if origin is None and path.with_suffix(".html").name in recovered_receipts:
                origin = fetch_by_file[
                    recovered_receipts[path.with_suffix(".html").name]
                ]
                recovered = True
        if origin is None:
            raise ValueError(f"No exact retrieval receipt for {path.name}")
        note = "Original downloaded response."
        if path.suffix == ".txt":
            note = "Local text derivative of saved response; original remains authoritative."
        if path.name in {
            "fssai-vegan-amendment-20260521.pdf",
            "fssai-vegan-amendments-index.html",
            "fssai-regulations-index.html",
        }:
            note += " HTTP 200 HTML application shell, not substantive regulatory text; excluded as claim evidence."
        if path.name == "ayfoods-products.html":
            note += " Actual bytes are PDF despite saved .html suffix; content magic checked."
        if recovered:
            note += " Original manual retrieval time unknown. accessed_utc records a later logged retrieval of byte-identical original content, SHA-256 checked; it is not an inferred original retrieval time."
        manifests.append(
            {
                "file": str(path.relative_to(ROOT)),
                "url": origin["url"],
                "accessed_utc": origin["completed_utc"],
                "sha256": digest(path),
                "license": "Public access; redistribution licence not established; keep raw local",
                "source_id": origin["source_id"],
                "notes": note,
            }
        )
    write_csv("manifest_rows.csv", manifests)
    # Reused sources retain their existing rows and original retrieval timestamps.
    all_sources = {
        row["source_id"]: row for row in rows(HERE / "baseline_source_rows.csv")
    }
    referenced = {row["source_id"] for row in policies + kept + excluded}
    write_csv(
        "reused_source_rows.csv",
        [all_sources[key] for key in sorted(referenced) if key in all_sources],
    )
    print(
        json.dumps(
            {
                "companies": len(kept),
                "feed_exclusions": len(excluded),
                "policies": len(policies),
                "new_sources": len(sources),
                "raw_manifest_rows": len(manifests),
            }
        )
    )


if __name__ == "__main__":
    main()
