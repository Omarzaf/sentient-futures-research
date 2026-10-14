"""Stage dated India policy and capacity evidence without inferring approvals."""

from __future__ import annotations

import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from provenance import MANIFEST_FIELDS, ROOT, SOURCE_FIELDS, write_csv

__all__ = ["build"]
BASE = ROOT / "scripts/altprotein/india_policy"
RAW = ROOT / "data/raw/altprotein/india_policy"
ACCESS = "2026-10-13"

# File names are retrieval labels. Document identity is checked from content.
EVIDENCE = [
    (
        "india_ciba_loopworm_2024",
        "ICAR-CIBA Loopworm aquafeed collaboration",
        "ICAR-Central Institute of Brackishwater Aquaculture",
        "https://ciba.res.in/?p=16137&post_type=edmento_events",
        "2024",
        "A",
        "ciba-loopworm-2024",
        "Dated26June2024 institutional MoU account. Reported processing capability is insect input mass, not protein output, realised throughput, human food approval or current2026 capacity.",
    ),
    (
        "loopworm_products_snapshot_2026",
        "Loopworm product portfolio snapshot",
        "Loopworm",
        "https://loopworm.in/products/",
        "",
        "C",
        "loopworm-products-snapshot",
        "Undated company page names silkworm-derived ingredients for pets/aquaculture/poultry/swine. No numeric composition, superlative, environmental or health claims extracted; supports feed-only scope.",
    ),
    (
        "india_pib_bioe3_2024",
        "Cabinet approves BioE3 policy",
        "PIB / Government of India",
        "https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2048568&lang=2&reg=48",
        "2024",
        "A",
        "pib-bioe3-2024",
        "Dated 24 August 2024; research and biomanufacturing policy, not food-product approval.",
    ),
    (
        "india_birac_smart_protein_call_2025",
        "DBT-BIRAC Smart Proteins call",
        "DBT / BIRAC",
        "https://birac.nic.in/cfp_view.php?id=98&scheme_type=46",
        "2025",
        "A",
        "birac-smart-proteins-2025",
        "Announced 22 February 2025; extended deadline 5 April 2025; historical closed call, not current funding availability.",
    ),
    (
        "india_dbt_smart_protein_programme",
        "Smart Proteins and Functional Foods programme",
        "Department of Biotechnology",
        "https://bmi.dbt.gov.in/smart-proteins-and-functional-food.php",
        "",
        "A",
        "dbt-smart-proteins-programme",
        "Undated live programme page; access date is not publication date. Corroboration only.",
    ),
    (
        "india_dbt_pdf_retrieval_failed",
        "Attempted Smart Proteins call PDF retrieval",
        "Department of Biotechnology hostname response",
        "https://dbt.gov.in/sites/default/files/Approved_CFP_Biomanufacturing_Smart_Proteins_25.03.2025_0.pdf",
        "",
        "A",
        "dbt-smart-proteins-2025",
        "Returned HTML despite PDF extension; not policy evidence. Original dbtindia.gov.in URL failed DNS. Historical BIRAC HTML supplies the call facts.",
    ),
    (
        "india_fssai_nsf_portal_2026",
        "Non-Specified Food official portal and public frontend content",
        "FSSAI",
        "https://fssai.gov.in/standards/non-specified-food",
        "",
        "A",
        "fssai-non-specified-2026",
        "Rill denied by approval policy; curl public JS provides page text and PDF links. Undated page; access snapshot only. Regulation link unexpectedly returns January2023 application list, retained separately.",
    ),
    (
        "india_fssai_mislinked_regulation_2023",
        "January2023 application status list at mislabelled NSF regulation link",
        "FSSAI",
        "https://fssai.gov.in/docs/standards/specfic-food/NSF_Regulation_2017.pdf",
        "2023",
        "A",
        "fssai-nsf-regulation-2017",
        "stale; retrieved bytes are January2023 application status list, not regulation text; not used for regulatory claims.",
    ),
    (
        "india_fssai_nsf_compendium_2022",
        "Non-Specified Food regulations compendium Version I 14.10.2022",
        "FSSAI",
        "https://www.fssai.gov.in/upload/uploadfiles/files/Compendium_FSS_NFS_FA_17_10_2022.pdf",
        "2022",
        "A",
        "fssai-nsf-compendium-2022",
        "stale regulatory text version, corroborated by current official portal; not an exhaustive current legal consolidation or product approval.",
    ),
    (
        "india_fssai_nsf_status_20260901",
        "Non-Specified Food application status as of 1 September2026",
        "FSSAI",
        "https://fssai.gov.in/docs/standards/specfic-food/Status%20of%20application%20as%20on%2001.09.2026.pdf",
        "2026",
        "A",
        "fssai-nsf-status-2026-09-01",
        "Biokraft listed in under-process section p66 row28 at stage7. Legend p79 means decision conveyed: clarification/approval/rejection, not unequivocal approval.",
    ),
    (
        "india_pib_bioe3_platforms_2026",
        "Parliament question: BioE3 policy and biomanufacturing platforms",
        "PIB / Ministry of Science and Technology",
        "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238344&lang=1&reg=3",
        "2026",
        "A",
        "pib-bioe3-platforms-2026",
        "Dated 11 March2026; platforms reported set up. Named vessel scale is multi-purpose facility scale, not annual alternative-protein output.",
    ),
    (
        "gfi_fermentation_soi_2026",
        "2026 State of the Industry: Fermentation for meat, seafood, eggs, dairy and ingredients",
        "The Good Food Institute",
        "https://gfi.org/wp-content/uploads/2026/04/GFI-2026-State-of-the-Industry-report-Fermentation-for-meat-seafood-eggs-dairy-and-ingredients.pdf",
        "2026",
        "B",
        "gfi-fermentation-2026",
        "Retrospective primarily on2025; p38 and p47 describe India facilities. GFI describes industry facilities being set up; do not equate with measured throughput.",
    ),
    (
        "gfi_cultivated_soi_2026",
        "2026 State of the Industry: Cultivated meat, seafood and ingredients",
        "The Good Food Institute",
        "https://gfi.org/wp-content/uploads/2026/04/GFI_2026-State-of-the-Industry-report-Cultivated-meat-seafood-and-ingredients.pdf",
        "2026",
        "B",
        "gfi-cultivated-2026",
        "Retrospective primarily on2025; p13 ClearMeat partnership/Biokraft demonstration; p42 stem-cell repository. No production capacity or food approval inferred.",
    ),
]


def build() -> None:
    """Write staged sources, hashes, bounded policies and facility observations."""
    sources, manifest, mapped = [], [], set()
    for sid, title, publisher, url, year, tier, stem, notes in EVIDENCE:
        license_note = "No explicit reuse license established; public access only"
        sources.append(
            dict(
                zip(
                    SOURCE_FIELDS,
                    [
                        sid,
                        title,
                        publisher,
                        url,
                        year,
                        ACCESS,
                        tier,
                        "curl; saved original; text extraction and selected PDF visual inspection",
                        license_note,
                        notes,
                    ],
                    strict=True,
                )
            )
        )
        files = sorted(RAW.glob(stem + ".*"))
        if sid == "india_fssai_nsf_portal_2026":
            files += [
                RAW / "fssai-public-app.js",
                RAW / "fssai-non-specified-content.js",
            ]
        render_names = {
            "gfi_fermentation_soi_2026": ["gfi-fermentation-page38.png"],
            "gfi_cultivated_soi_2026": ["gfi-cultivated-page13.png"],
            "india_fssai_nsf_compendium_2022": ["fssai-nsf-compendium-page1.png"],
            "india_fssai_nsf_status_20260901": [
                "fssai-status-page66.png",
                "fssai-status-page79.png",
            ],
        }
        files += [RAW / name for name in render_names.get(sid, [])]
        for path in files:
            if not path.is_file():
                raise ValueError(f"Missing evidence {path}")
            file_url = url
            if path.name == "fssai-public-app.js":
                file_url = "https://fssai.gov.in/assets/index-Bi3xUbnI.js"
            elif path.name == "fssai-non-specified-content.js":
                file_url = "https://fssai.gov.in/assets/NonSpecifiedFood-Bnoz7hyk.js"
            with path.open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            manifest.append(
                dict(
                    zip(
                        MANIFEST_FIELDS,
                        [
                            str(path.relative_to(ROOT)),
                            file_url,
                            datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(
                                timespec="seconds"
                            ),
                            digest,
                            license_note,
                            sid,
                            (
                                "Derived extraction/render from saved original"
                                if path.suffix in (".txt", ".png")
                                else "Original downloaded bytes"
                            )
                            + "; "
                            + notes,
                        ],
                        strict=True,
                    )
                )
            )
            mapped.add(path.name)
    if mapped != {p.name for p in RAW.iterdir() if p.is_file()}:
        raise ValueError("Unmapped raw India policy artifact")
    write_csv(BASE / "source_rows.csv", SOURCE_FIELDS, sources)
    write_csv(BASE / "manifest_rows.csv", MANIFEST_FIELDS, manifest)
    policies = [
        (
            "BioE3",
            "2024-08-24",
            "innovation_policy_approved",
            "Supports smart proteins and functional foods within high-performance biomanufacturing.",
            "india_pib_bioe3_2024",
            "india_birac_smart_protein_call_2025",
            "PIB Cabinet decision; BIRAC introduction",
            "Research/industrial policy is not authorization to sell a specific food.",
            "current_dated_evidence",
        ),
        (
            "DBT-BIRAC Smart Proteins call",
            "2025-02-22",
            "historical_call_closed",
            "Invited plant-based, fermentation-derived and cell-culture-based proteins; extended submission deadline 2025-04-05.",
            "india_birac_smart_protein_call_2025",
            "india_dbt_smart_protein_programme",
            "Announcement Date / Last Submission Date and Scope",
            "Funding call, not evidence of award or current application window; no application submitted.",
            "current_dated_evidence",
        ),
        (
            "FSSAI Non-Specified Food",
            "2022-10-14",
            "general_prior_approval_framework",
            "Saved compendium requires prior food-authority approval to manufacture or import a non-specified food or ingredient.",
            "india_fssai_nsf_compendium_2022",
            "india_fssai_nsf_portal_2026",
            "Compendium page1 regulations3-4; current portal introduction",
            "stale compendium version; general pathway, not a cultivated-meat approval or legal advice. No license/application submitted.",
            "stale_text_current_portal_corroboration",
        ),
        (
            "FSSAI Biokraft application",
            "2026-09-01",
            "application_status_ambiguous_stage7",
            "Cultivated chicken-based product is listed under process; stage7 conveys a decision that may be clarification, approval or rejection.",
            "india_fssai_nsf_status_20260901",
            "",
            "PDF66 row28; PDF79 stage legend",
            "Do not infer regulatory approval from this status code or the company demonstration.",
            "current_dated_evidence",
        ),
    ]
    fields = [
        "country",
        "authority_or_pathway",
        "date",
        "status",
        "finding",
        "source_id",
        "corroborating_source_id",
        "raw_locator",
        "notes",
        "freshness",
        "checked",
    ]
    write_csv(
        BASE / "policy_rows.csv",
        fields,
        [dict(zip(fields, ["India", *row, ACCESS], strict=True)) for row in policies],
    )
    capacity_specs = [
        (
            "Loopworm",
            "Bangalore",
            "insect_processing_animal_feed",
            "2024",
            "6000",
            "tonnes_insect_input_per_year",
            "reported_input_processing_capability",
            "india_ciba_loopworm_2024",
            "A",
            "Opening paragraph; MoU dated26June2024",
            "Historical institutional report of input processing capability, not protein yield or actual output. Company product page independently confirms animal-feed scope; no human-food use or current capacity inferred.",
            "reported_historical_processing_capability",
        ),
        (
            "HiMedia Laboratories",
            "Mumbai",
            "fermentation_shared_infrastructure",
            "2026",
            "1",
            "kilolitre",
            "reported_multiuse_facility_scale",
            "india_pib_bioe3_platforms_2026",
            "A",
            "Annexure I biomanufacturing platforms item9",
            "Reported food-products/additives/probiotics/cell-growth facility scale; no protein-only allocation, working volume, utilisation or annual mass output published.",
            "government_reports_platform_set_up",
        ),
        (
            "Laurus Bio",
            "Visakhapatnam",
            "fermentation_shared_infrastructure",
            "2026",
            "",
            "",
            "protein_capacity_not_disclosed",
            "india_pib_bioe3_platforms_2026",
            "A",
            "Annexure I biomanufacturing platforms item5",
            "Functional foods, smart proteins and other applications; protein-specific numeric capacity unknown.",
            "government_reports_platform_set_up",
        ),
        (
            "Sundyota Numandis",
            "Ahmedabad",
            "fermentation_shared_infrastructure",
            "2026",
            "",
            "",
            "protein_capacity_not_disclosed",
            "india_pib_bioe3_platforms_2026",
            "A",
            "Annexure I biomanufacturing platforms item10",
            "Platform described for probiotics and smart proteins; no numeric capacity or measured throughput given.",
            "government_reports_platform_set_up",
        ),
        (
            "BRIC National Agri-Food and Biomanufacturing Institute",
            "India",
            "microbial_protein_biofoundry",
            "2025",
            "",
            "",
            "protein_capacity_not_disclosed",
            "gfi_fermentation_soi_2026",
            "B",
            "PDF38 and47",
            "Biofoundry described as established; future industrial-scale development from corn-starch side streams; no numeric throughput disclosed.",
            "research_scaleup_infrastructure_reported",
        ),
        (
            "ClearMeat / NIFTEM APEX",
            "India",
            "cultivated_research_manufacturing_partnership",
            "2025",
            "",
            "",
            "protein_capacity_not_disclosed",
            "gfi_cultivated_soi_2026",
            "B",
            "PDF13",
            "Partnership to create research/manufacturing facility; no commissioned capacity or annual output disclosed.",
            "partnership_announced",
        ),
        (
            "Biokraft Foods",
            "India",
            "cultivated_product_demonstration",
            "2025",
            "",
            "",
            "protein_capacity_not_disclosed",
            "gfi_cultivated_soi_2026",
            "B",
            "PDF13",
            "Cultivated-chicken cook-off demonstrates product engagement; not production capacity, regulatory approval or sales.",
            "demonstration_reported",
        ),
    ]
    rows = []
    for (
        entity,
        location,
        kind,
        year,
        value,
        unit,
        metric,
        sid,
        tier,
        locator,
        note,
        status,
    ) in capacity_specs:
        rows.append(
            {
                "country": "India",
                "source_type": kind,
                "year": year,
                "metric": metric,
                "value": value,
                "unit": unit,
                "source_id": sid,
                "tier": tier,
                "entity": entity,
                "location": location,
                "evidence_status": status,
                "raw_locator": locator,
                "method": "Source-reported scale or explicit unknown; no throughput conversion or extrapolation.",
                "notes": note,
                "freshness": (
                    "historical_2024_evidence"
                    if year == "2024"
                    else "dated_2025_or_2026_evidence"
                ),
                "checked": ACCESS,
            }
        )
    write_csv(BASE / "capacity_rows.csv", list(rows[0]), rows)
    print(
        f"Staged {len(sources)} sources, {len(manifest)} artifacts, {len(policies)} policies, {len(rows)} capacity/context rows"
    )


if __name__ == "__main__":
    build()
