"""Build bounded company evidence rows; preserve unverified directory candidates."""

import csv
import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/altprotein/companies"
ACCESS = "2026-10-13"
LICENSE = "Public access; redistribution license not established"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV."""
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write rows with consistent field order."""
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


# The first source is an image PDF; the transcription is separately registered.
SOURCES = [
    (
        "chatha_annual_report_2025",
        "Chatha Foods Annual Report 2024-25",
        "Chatha Foods Limited",
        "https://bsmedia.business-standard.com/_media/bs/data/announcements/bse/07082025/9d75e574-8d61-4b37-8d63-13f847dc2a80.pdf",
        "2025",
        "C",
        "Issuer annual report mirror. Image PDF saved for provenance; figures not extracted or asserted. Status wording used from separately registered IIFL transcription.",
        ["chatha-annual2025.pdf", "chatha-annual2025.txt"],
    ),
    (
        "chatha_management_discussion_2025_iifl",
        "Chatha Foods management discussion for FY2024-25",
        "Chatha Foods; transcription hosted by India Infoline",
        "https://www.indiainfoline.com/company/chatha-foods-ltd/management-discussions",
        "2025",
        "C",
        "FY25 explicitly identified; supplier names BlueTribe and Shaka Harry as alt-protein clients with reduced traction. Does not establish status at research date.",
        ["chatha-md2025.html"],
    ),
    (
        "dyadic_fermbox_collaboration_2025",
        "Dyadic and Fermbox Bio expand strategic collaboration",
        "Dyadic Applied BioSolutions",
        "https://dyadic.com/dyadic-and-fermbox-bio-expand-strategic-collaboration-to-accelerate-commercialization-of-animal-free-proteins-and-enzymes-across-life-science-food-nutrition-and-bioindustrial-markets/",
        "2025",
        "C",
        "Dated 17 December 2025 partner press release. Commercialization announcement is not sales or verified throughput.",
        ["fermbox-dyadic2025.html"],
    ),
    (
        "fermbox_biomanufacturing_2025",
        "India biomanufacturing momentum and Fermbox Bio role in precision fermentation",
        "Fermbox Bio",
        "https://fermbox.bio/biotech-in-focus-indias-biomanufacturing-momentum-and-fermbox-bios-role-in-precision-fermentation/",
        "2025",
        "C",
        "Dated 7 August 2025. Self-description corroborates technology and Indian presence, not food approval or realized protein sales.",
        ["fermbox-self2025.html"],
    ),
    (
        "theprint_cultivated_india_2025",
        "Startups to government policies: India wants to lead the lab-grown meat revolution",
        "ThePrint",
        "https://theprint.in/ground-reports/startups-govt-policies-india-lead-lab-grown-meat-revolution/2759328/",
        "2025",
        "C",
        "Published 8 October 2025; field reporting on Clear Meat and Biokraft. No quoted sales/capacity numbers imported.",
        ["theprint-cultivated2025.html"],
    ),
    (
        "biokraft_blog_2025",
        "Biokraft Foods dated company blog entries",
        "Biokraft Foods",
        "https://www.biokraftfoods.com/blog",
        "2025",
        "C",
        "Multiple visible dated 2025 entries on cultivated chicken cook-off; self-reported development and demonstrations, not retail launch approval.",
        ["biokraft-blog.html"],
    ),
    (
        "futurebridge_zerocow_2025",
        "Startup Spotlight: Zero Cow Factory",
        "FutureBridge",
        "https://www.futurebridge.com/article/zero-cow-factory/",
        "2025",
        "C",
        "Dated 7 February 2025; consultancy profile describes precision-fermentation development and pilot/regulatory plans. Treat plans as plans; no technical benefit or financing numbers imported.",
        ["zerocow2025.html"],
    ),
    (
        "tdu_stringbio_workshop_2025",
        "New developments in alternative proteins symposium",
        "The University of Trans-Disciplinary Health Sciences and Technology",
        "https://www.tdu.edu.in/event/new-developments-in-alternative-proteins",
        "2025",
        "C",
        "University event notice dated 27 March 2025; names String Bio fermentation proteins in pilot-plant workshop. It is an announcement, not proof workshop happened or food was approved.",
        ["string-tdu2025.html"],
    ),
    (
        "stringbio_animal_nutrition_snapshot",
        "String Bio animal nutrition products",
        "String Bio",
        "https://www.stringbio.com/animal-nutrition.html",
        "",
        "C",
        "Undated primary product page; only used to distinguish methane-derived microbial biomass protein and feed application from plant-based protein or food approval.",
        ["string-animal-nutrition.html"],
    ),
    (
        "blue_tribe_product_launch_2025",
        "Blue Tribe expands portfolio with new plant-based lineup",
        "Indian Retailer / Licence India Bureau",
        "https://www.indianretailer.com/brandlicense/archives/news/blue-tribe-expands-portfolio-new-plant-based-lineup.n4519",
        "2025",
        "C",
        "Dated 14 October 2025; product availability reported for soya chaap and kebab. Current stock and commercial sales unverified. Market-size claims excluded.",
        ["blue-tribe2025.html"],
    ),
    (
        "fssai_biokraft_status_20251111",
        "Non-specified food application status 11 November 2025",
        "Food Safety and Standards Authority of India",
        "https://fssai.gov.in/upload/uploadfiles/files/StatusofApplicationason11_11_2025%281%29.pdf",
        "2025",
        "A",
        "Biokraft application in Under Process section. Some page footers retain October date; cover/section dates distinguish this snapshot.",
        ["fssai-status2025.pdf", "fssai-status2025.txt"],
    ),
    (
        "fssai_biokraft_status_20260603",
        "Non-specified food application status 3 June 2026",
        "Food Safety and Standards Authority of India",
        "https://fssai.gov.in/upload/uploadfiles/files/Status_of_Application_as_on_03_06_2026.pdf",
        "2026",
        "A",
        "PDF page65 row39: Biokraft cultivated chicken-based product in Under Process section, stage7. Legend: authority decision conveyed (clarification/approval/rejection); stage7 cannot establish approval.",
        ["fssai-status2026.pdf", "fssai-status2026.txt", "fssai-status2026-page65.png"],
    ),
    (
        "niftem_clearmeat_mou_2025",
        "NIFTEM-K newsletter July-September 2025",
        "NIFTEM-K, Ministry of Food Processing Industries",
        "https://niftem.ac.in/storage/uploads/media/NMTUuKrecwgs4RoKWD1ckPmKWH72veBfOT17E2yX.pdf",
        "2025",
        "A",
        "PDF page9, printed7, confirms Clear Meat MoU at World Food India2025. Does not establish commercially approved cultivated meat.",
        ["niftem-news2025.pdf", "niftem-news2025.txt", "niftem-news2025-page9.png"],
    ),
    (
        "countrydelight_oat_launch_2025",
        "Country Delight launches plant-based oats beverage",
        "Indian Food and Beverage",
        "https://indifoodbev.com/product-launch/country-delight-oats-beverage/",
        "2025",
        "C",
        "Dated 27 June 2025; explicitly based on a press release. Launch corroborated by GFI annual report; current sales unverified.",
        ["countrydelight2025.html"],
    ),
    (
        "symega_protein_slice_2025",
        "CFTRI symposium and Protein Plus Slice launch",
        "Star of Mysore",
        "https://starofmysore.com/plant-viruses-slash-indias-farm-yields-by-up-to-30-percent-says-iisc-expert/",
        "2025",
        "C",
        "Dated 27 July 2025; confirms Symega in CFTRI/McDonalds collaboration. GFI report explicitly identifies whey; hybrid product must not be called wholly plant-based.",
        ["symega2025.html"],
    ),
    (
        "shakaharry_product_snapshot_20261013",
        "Shaka Harry primary website HTML metadata snapshot",
        "Shaka Harry",
        "https://shakaharry.com/",
        "",
        "C",
        "Undated JavaScript shell; HTML metadata describes plant-based protein snacks. No date or verified availability inferred. Rill access rejected by automatic approval review.",
        ["shaka-current.html"],
    ),
]

sources = {r["source_id"]: r for r in read_csv(OUT / "source_rows.csv")}
manifest = {r["file"]: r for r in read_csv(OUT / "manifest_rows.csv")}
for source_id, title, publisher, url, year, tier, notes, filenames in SOURCES:
    sources[source_id] = {
        "source_id": source_id,
        "title": title,
        "publisher": publisher,
        "url": url,
        "year": year,
        "accessed": ACCESS,
        "tier": tier,
        "access_method": "curl; original bytes; PDF text via pdftotext -layout",
        "license": LICENSE,
        "notes": notes,
    }
    for filename in filenames:
        path = RAW / filename
        assert path.exists() and path.stat().st_size > 0, filename
        if path.suffix == ".pdf":
            assert path.read_bytes().startswith(b"%PDF"), filename
        kind = "Original downloaded bytes."
        if path.suffix == ".txt":
            kind = "Derived PDF text using pdftotext -layout; original PDF retained."
        if path.suffix == ".png":
            kind = "Derived PDF page render using pdftoppm; visually reviewed; original PDF retained."
        rel = str(path.relative_to(ROOT))
        manifest[rel] = {
            "file": rel,
            "url": url,
            "accessed_utc": datetime.fromtimestamp(
                path.stat().st_mtime, UTC
            ).isoformat(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "license": LICENSE,
            "source_id": source_id,
            "notes": kind,
        }

# Cross-workstream primary source is registered by the policy builder; copy its
# exact metadata so all references resolve in this staging bundle as well.
policy_sources = read_csv(OUT.parent / "india_policy/source_rows.csv")
latest_fssai = next(
    row
    for row in policy_sources
    if row["source_id"] == "india_fssai_nsf_status_20260901"
)
sources[latest_fssai["source_id"]] = latest_fssai
candidates = {r["company"]: r for r in read_csv(OUT / "company_candidates.csv")}
rows = []


def add(
    company: str,
    category: str,
    status: str,
    evidence_date: str,
    precision: str,
    source_id: str,
    other: str,
    locator: str,
    notes: str,
    category_source: str = "",
) -> None:
    """Add a dated, bounded status observation without inferring current operations."""
    candidate = candidates.get(company, {})
    rows.append(
        {
            "company": company,
            "country": "India",
            "category": category,
            "status": status,
            "status_checked": ACCESS,
            "source_id": source_id,
            "status_source_id": source_id,
            "status_evidence_date": evidence_date,
            "evidence_date_precision": precision,
            "supplemental_source_ids": other,
            "category_source_id": category_source
            or candidate.get("source_id", source_id),
            "directory_id": candidate.get("directory_id", ""),
            "directory_url": candidate.get("directory_url", ""),
            "evidence_locator": locator,
            "geographic_basis": "Indian company or Indian research/commercial presence identified by sources; not a legal-domicile determination",
            "notes": notes
            + " Status is bounded to the cited evidence date; continuing operations and current stock are not independently audited.",
        }
    )


add(
    "GoodDot",
    "plant-based meat alternatives",
    "2026_company_publication_product_claim; current_operations_unverified",
    "2026-06-15",
    "day",
    "gooddot_comparison_blog_2026",
    "gfi_ecosystem_company_snapshot_20261013",
    "gooddot-blog2026.html: visible date and JSON-LD datePublished",
    "Self-authored comparison establishes publication and claimed products, not competitor status or sales.",
)
add(
    "Proeon",
    "plant-based protein ingredients",
    "2026_public_company_activity_documented; production_unverified",
    "2026-06-08",
    "day",
    "gfi_proeon_dialogue_2026",
    "proeon_grant_2025;gfi_ecosystem_company_snapshot_20261013",
    "gfi-proeon-june2026.html: Proeon representative in dialogue; company grant dated2025-04-14",
    "GFI participation evidence plus a separate company grant announcement. No industrial output inferred.",
)
add(
    "Blue Tribe Foods",
    "plant-based meat alternatives",
    "2025_product_availability_reported; current_operations_unverified",
    "2025-10-14",
    "day",
    "blue_tribe_product_launch_2025",
    "chatha_management_discussion_2025_iifl;gfi_ecosystem_company_snapshot_20261013",
    "blue-tribe2025.html: dated launch paragraph; chatha-md2025.html: Revenue Mix customer discussion",
    "Product launch/availability claim is tierC; supplier separately reports reduced FY25 traction. No outlet count or sales imported.",
)
add(
    "Shaka Harry",
    "plant-based alternatives and protein snacks",
    "FY2025_supplier_customer_relationship_reported; current_operations_unknown",
    "2025-03-31",
    "fiscal_year_end",
    "chatha_management_discussion_2025_iifl",
    "shakaharry_product_snapshot_20261013;chatha_annual_report_2025",
    "chatha-md2025.html: FY25 Revenue Mix customer discussion; chatha-annual2025.pdf covering letter: fiscal year ended31March2025; shaka-current.html: HTML description",
    "Supplier states reduced traction in FY25. Undated primary site describes protein snacks; it does not establish a continuing meat-alternative assortment. Not found in this GFI India directory snapshot.",
    "shakaharry_product_snapshot_20261013",
)
add(
    "String Bio",
    "fermentation: microbial biomass protein; animal-feed products",
    "2025_university_workshop_ingredient_announcement; commercial_food_status_unknown",
    "2025-03-27",
    "day",
    "tdu_stringbio_workshop_2025",
    "stringbio_animal_nutrition_snapshot",
    "string-tdu2025.html: workshop dated27-28March2025; string-animal-nutrition.html: methane fermentation and SCP",
    "Event notice names fermentation proteins. Primary product page clarifies feed application; feed product offering is not approval for human food. Not found in this GFI India directory snapshot.",
    "stringbio_animal_nutrition_snapshot",
)
add(
    "Clear Meat",
    "cultivated meat enabling technology; cell-growth media",
    "2025_research_partnership_documented; cultivated_meat_sales_unverified",
    "2025-Q3",
    "quarter",
    "niftem_clearmeat_mou_2025",
    "theprint_cultivated_india_2025;gfi_ecosystem_company_snapshot_20261013",
    "niftem-news2025.pdf PDFp9/printedp7: WFI2025 MoU; theprint-cultivated2025.html: cell-growth medium",
    "Government institute confirms collaboration; independent reporting identifies cell-growth media. Media sales are separate from cultivated meat sales and no amounts are imported.",
)
add(
    "Biokraft Foods",
    "cultivated meat and seafood; 3D-bioprinted",
    "2026_regulatory_application_listed; approval_not_established",
    "2026-09-01",
    "day",
    "india_fssai_nsf_status_20260901",
    "fssai_biokraft_status_20260603;fssai_biokraft_status_20251111;theprint_cultivated_india_2025;biokraft_blog_2025;gfi_ecosystem_company_snapshot_20261013",
    "india_policy/fssai-nsf-status-2026-09-01.pdf PDFp66 row28; Under Process section beginsPDFp64; legendPDFp79",
    "FSSAI stage7 conveys a decision that can be clarification/approval/rejection; it is not approval proof. Dated demonstrations are not commercial launch. September2026 official snapshot supersedes the June2026 observation; ambiguous stage is unchanged.",
)
add(
    "Zero Cow Factory",
    "fermentation: precision-fermented dairy proteins",
    "2025_development_and_pilot_plans_reported; commercial_status_unknown",
    "2025-02-07",
    "day",
    "futurebridge_zerocow_2025",
    "gfi_ecosystem_company_snapshot_20261013",
    "zerocow2025.html: visible date and What should we watch for section",
    "Consultancy profile describes development, planned pilot and pending regulatory progress. No pilot commissioning or market authorization inferred.",
)
add(
    "Fermbox Bio",
    "fermentation: precision-fermented proteins and enzymes; enabling manufacturing",
    "2025_partner_commercialization_agreement_announced; realized_protein_sales_unknown",
    "2025-12-17",
    "day",
    "dyadic_fermbox_collaboration_2025",
    "fermbox_biomanufacturing_2025",
    "fermbox-dyadic2025.html: dated announcement; fermbox-self2025.html: dated Indian biomanufacturing description",
    "Partner and company statements corroborate activity. Cross-sector platform includes nonfood products; agreement does not prove retail food or India plant capacity. Not found in this GFI India directory snapshot.",
)
add(
    "Country Delight",
    "plant-based dairy alternative: oat beverage",
    "2025_oat_beverage_launch_reported; current_availability_unverified",
    "2025-06-27",
    "day",
    "countrydelight_oat_launch_2025",
    "gfi_plant_based_soi_2025",
    "countrydelight2025.html: dated launch; GFI plant-based reportPDFp15 India paragraph",
    "Conventional dairy company with a plant-based product line; not an exclusively alternative-protein company. No inference that oat beverage is protein-equivalent to dairy. Not found in this GFI India directory snapshot.",
)
add(
    "Symega",
    "plant-protein ingredients; hybrid plant-plus-whey slice",
    "2025_hybrid_product_collaboration_and_launch_documented",
    "2025-07-27",
    "day",
    "symega_protein_slice_2025",
    "gfi_plant_based_soi_2025",
    "symega2025.html: Protein Plus Slice launched section; GFI plant-based reportPDFp13 India paragraph",
    "GFI explicitly identifies whey in the launched Protein Plus slice. This row is a hybrid product collaboration, not evidence of a wholly plant-based or vegan product. Not found in this GFI India directory snapshot.",
    "gfi_plant_based_soi_2025",
)

assert len(rows) == len({r["company"] for r in rows}) >= 10
for row in rows:
    assert re.match(r"202[56]-", row["status_evidence_date"])
    for field in [
        "source_id",
        "status_source_id",
        "category_source_id",
        "supplemental_source_ids",
    ]:
        assert all(ref in sources for ref in row[field].split(";") if ref), (
            row["company"],
            field,
        )
for row in manifest.values():
    path = ROOT / row["file"]
    assert (
        path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    ), row["file"]
    assert row["source_id"] in sources, row["file"]
assert {str(p.relative_to(ROOT)) for p in RAW.iterdir() if p.is_file()} <= set(manifest)
write_csv(OUT / "company_rows.csv", rows)
write_csv(OUT / "source_rows.csv", list(sources.values()))
write_csv(OUT / "manifest_rows.csv", list(manifest.values()))
print(
    f"{len(rows)} dated company observations; {len(sources)} tiered sources; {len(manifest)} hashed artifacts; no active-company count asserted."
)
