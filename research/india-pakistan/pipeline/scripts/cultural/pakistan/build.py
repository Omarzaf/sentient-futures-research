"""Build source-bound Pakistan cultural staging without altering shared registries."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/cultural/pakistan"
ACCESS = "2026-10-13"
LICENSE = (
    "Public access; redistribution rights not established; no publication authorized"
)

SOURCE_META = {
    "pk_cultural_iifa_2025": (
        "Resolution 265 (10/26): consumption and marketing of cultivated meat",
        "International Islamic Fiqh Academy, Organization of Islamic Cooperation",
        "2025",
        "B",
        "Primary institutional religious resolution, not Pakistani food approval. Session 4-8 May2025; English webpage published20November2025. Source-register HS001 independently opened and read.",
    ),
    "pk_cultural_muis_2024": (
        "Fatwa on cultivated meat",
        "Majlis Ugama Islam Singapura",
        "2024",
        "A",
        "Singapore government religious authority,3February2024. Curl403 retained; official full page opened/read through web fallback. Not Pakistani certification or consumer survey. HS002 independently read.",
    ),
    "pk_cultural_halal_act_2016": (
        "Pakistan Halal Authority Act,2016",
        "Government of Pakistan / Pakistan Code",
        "2016",
        "A",
        "Statute dated27February2016; stale original legislation, no current consolidated-amendment claim. Cross-read with registered PHA2024 and2025 operational documents. HS017 directly downloaded/read.",
    ),
    "pk_cultural_eid_pide_2024": (
        "The Economy of Sacrificed Animals; Knowledge Brief2024:126",
        "Muhammad Faisal Ali / Pakistan Institute of Development Economics",
        "2024",
        "C",
        "August2024 brief. Underlying counts attributed to Pakistan Tanners Association hides received, not official animal census. TierC follows industry estimate lineage despite institutional host. HTML403; linked official PDF successfully downloaded and visually read.",
    ),
    "pk_cultural_eid_planning_2025": (
        "Planning Minister calls for joint efforts to boost leather exports",
        "Ministry of Planning, Development and Special Initiatives, Pakistan",
        "2025",
        "A",
        "Official7January2025 account of PTA meeting. Supports Eid/slaughter/hide infrastructure context only; quoted industry approximate volume is not promoted to an official statistic.",
    ),
    "pk_cultural_british_pakistanis_2024": (
        "Food and exercise practices among British Pakistanis; how can Bourdieu's theory of practice help to understand them?",
        "B Hussain, I Shaw and S Timmons / Perspectives in Public Health",
        "2024",
        "A",
        "Peer-reviewed qualitative study; online25October2024, issue collectionMay2026. UK city, purposive/snowball sample, not Pakistani national prevalence. Fieldwork dates not stated in inspected Methods.",
    ),
    "pk_cultural_food_demand_2023": (
        "Households food consumption pattern in Pakistan: Evidence from recent household integrated economic survey",
        "Naveed Hayat et al. / Heliyon9:e19518",
        "2023",
        "A",
        "Peer-reviewed demand model of HIES2018-19;24,620 retained households of24,809 reported initial. Expenditure proxy for income; derived unit values for price. Historical model, not alternative-protein willingness to pay.",
    ),
    "pk_cultural_dietary_guidelines_2018": (
        "Pakistan Dietary Guidelines for Better Nutrition",
        "Planning Commission, Government of Pakistan / FAO",
        "2019",
        "A",
        "Downloaded cover says2019; foreword dated28May2018. Source_id retains acquisition name but sourceyear is cover2019. Prescriptive guideline, not observed consumption survey; stale historical edition.",
    ),
    "pk_cultural_census_2023": (
        "National Census Report:7th Population and Housing Census2023",
        "Pakistan Bureau of Statistics",
        "2023",
        "A",
        "Year is census edition. Figure4.1 final-report urban38.88% differs from earlier38.82% announcement. Four provinces+ICT in cited table; AJK/GB absent. Religion table excludes restricted-area detailed records.",
    ),
    "pk_cultural_food_insecurity_diaspora_2018": (
        "Hidden hunger? Experiences of food insecurity amongst Pakistani and white British women",
        "Maddy Power, Neil Small, Bob Doherty and Kate E Pickett / British Food Journal",
        "2018",
        "A",
        "Qualitative Bradford study;16 women,8 of Pakistani origin; July-November2016. Community-recruited sample is not representative of Pakistan or UK Pakistani population.",
    ),
}


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    """Write a deterministic staging CSV."""
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


jobs = json.loads((OUT / "jobs.json").read_text()) + json.loads(
    (OUT / "jobs2.json").read_text()
)
sources = []
for source_id, (title, publisher, year, tier, notes) in SOURCE_META.items():
    candidates = [job for job in jobs if job["source_id"] == source_id]
    selected = candidates[-1]
    license_text = LICENSE
    if source_id in {
        "pk_cultural_british_pakistanis_2024",
        "pk_cultural_food_insecurity_diaspora_2018",
    }:
        license_text = "CC BY4.0 as stated in article; attribution required"
    sources.append(
        {
            "source_id": source_id,
            "title": title,
            "publisher": publisher,
            "url": selected["url"],
            "year": year,
            "accessed": ACCESS,
            "tier": tier,
            "access_method": "curl original bytes and outcomes; PDF render review; web fallback explicitly identified",
            "license": license_text,
            "notes": notes,
        }
    )

rows = []


def add(dimension: str, finding: str, source_id: str, **extra: str) -> None:
    """Append a contextual claim with explicit scope and source metadata."""
    row = {
        "country": "Pakistan",
        "region": "National",
        "dimension": dimension,
        "finding": finding,
        "value": "",
        "unit": "",
        "date": "",
        "source_id": source_id,
        "evidence_source_ids": "",
        "table_page": "",
        "sample_size": "not applicable",
        "denominator": "not applicable",
        "fieldwork_dates": "not applicable",
        "evidence_scope": "",
        "notes": "",
        "date_basis": "source date",
        "evidence_type": "qualitative_context",
        "tier": SOURCE_META[source_id][3],
        "raw_file": "",
        "value_status": "qualitative_no_numeric_claim",
        "display_rule": "Context only; retain geography, dates and limitations",
    }
    row.update(extra)
    rows.append(row)


add(
    "halal_certification",
    "Pakistan's statutory halal framework treats certification as conformity assessment including audit, inspection, testing and evaluation. Current PHA procedures distinguish certifier registration and use of its certification mark from approval of a particular novel food.",
    "pk_cultural_halal_act_2016",
    date="2025-05-20",
    date_basis="latest corroborating PHA operational notification; statute2016",
    evidence_source_ids="pha_lhcb_registration_2024;pha_mark_operationalization_2025",
    table_page="Act section2(i)-(l),PDFp4; PHA registration procedure2024; mark notification2025",
    evidence_scope="Pakistan statutory and administrative framework",
    notes="Statute is stale2016 original; contemporaneous operational documents corroborate pathway only. No Pakistan cultivated-meat approval or consumer acceptance inferred.",
    raw_file="data/raw/cultural/pakistan/halal-act-2016.pdf",
)

add(
    "cultivated_meat_fiqh",
    "IIFA permits cultivated meat conditionally, addressing lawful cell sources and media, supervision, disclosure and safety, and describes use alongside conventional meat. Singapore MUIS also conditions permissibility on lawful sources and ingredients and product cleanliness/safety; neither establishes Pakistan product approval.",
    "pk_cultural_iifa_2025",
    region="International Islamic context; not domestic Pakistan ruling",
    date="2025-11-20",
    date_basis="IIFA webpage publication; resolution session2025-05-04/2025-05-08; MUIS2024-02-03",
    evidence_source_ids="pk_cultural_muis_2024;pha_mark_operationalization_2025",
    table_page="IIFA resolution265,clauses3-6; MUIS paragraphs8,10",
    evidence_scope="Primary institutional religious positions with separate jurisdiction; no prevalence measurement",
    notes="Do not simplify IIFA cell-source condition into a universal prior-slaughter requirement. MUIS notes taste,cost and preference remain relevant. No universal Muslim consensus or Pakistani statutory adoption established.",
    raw_file="data/raw/cultural/pakistan/iifa-2025.html",
)

add(
    "eid_sacrifice",
    "PIDE's Eid brief reports an approximate sacrifice volume derived from Pakistan Tanners Association hide receipts. The volume is an industry proxy; the separate official ministry account confirms the Eid slaughter and hide-storage context, not this exact count.",
    "pk_cultural_eid_pide_2024",
    date="2024",
    value="6.8087",
    unit="million animals; reported approximate industry estimate",
    date_basis="Eid2024; briefAugust2024",
    evidence_source_ids="pk_cultural_eid_planning_2025",
    table_page="PIDE PDFp1 Figure1 and p2 opening paragraph,visually reviewed",
    sample_size="not stated; industry hide receipt estimate",
    denominator="animals reportedly sacrificed nationally at Eid2024; hide-collection coverage unknown",
    fieldwork_dates="Eid2024; exact hide-collection dates not stated",
    evidence_scope="Industry estimate reported by PIDE,not official slaughter census",
    notes="No source uncertainty interval or independent exact-count corroboration. Hide losses and collection coverage limit inference. Do not convert to people,meat tonnage or annual dietary intake.",
    value_status="reported_approximate_point_estimate_no_range",
    display_rule="TierC context only; do not use in headline/chart or invent a range. Preserve estimate with missing uncertainty warning.",
    raw_file="data/raw/cultural/pakistan/eid-pide.pdf",
)

add(
    "meat_status_and_hospitality",
    "In a qualitative British Pakistani sample, meat dishes signalled hospitality and status; serving only vegetables or lentils to guests could be perceived as inadequate. A separate Bradford study describes obligations to provide food and protect household honour.",
    "pk_cultural_british_pakistanis_2024",
    region="UK Pakistani diaspora; domestic generalisation unavailable",
    date="2024-10-25",
    evidence_source_ids="pk_cultural_food_insecurity_diaspora_2018",
    table_page="Food practices:High consumption of meat and sweets; Power2018:Household structure,cultural norms,and honour",
    sample_size="40 individual interviewees;5 community-leader interviews;2 focus groups; overlap not established",
    denominator="purposive/snowball qualitative participants in one UK city; not a population denominator",
    fieldwork_dates="not stated in inspected2024 paper Methods",
    evidence_scope="Participant accounts; UK diaspora only",
    notes="No Pakistan-wide prevalence or universal preference inferred. No health claim is taken from participants' opinions. Missing domestic ethnographic coverage retained as a gap.",
    raw_file="data/raw/cultural/pakistan/food-british-pakistanis.html",
)

add(
    "dairy_role",
    "Pakistan's dietary guidelines identify milk, yogurt, cheese, custard and lassi as a distinct food group. Dairy is treated separately from meat and pulses; the guidance should not be interpreted as measured household consumption.",
    "pk_cultural_dietary_guidelines_2018",
    date="2019",
    date_basis="cover year2019; foreword2018",
    evidence_source_ids="pakistan_hies_2024_25_table23",
    table_page="Printedp30/PDFp44,Milk and milk products; HIES Table23 item grouping",
    evidence_scope="Official prescriptive food categories,corroborated by household survey item definitions",
    notes="Stale historical guideline edition. HIES categorisation confirms products are measured,not that households attain guideline servings. No implied dairy-free or vegetarian prevalence.",
    raw_file="data/raw/cultural/pakistan/dietary-guidelines.pdf",
)

add(
    "urbanisation",
    "The final national census report records the urban population share. This demographic context does not establish an urban preference for alternative protein or a causal effect on meat consumption.",
    "pk_cultural_census_2023",
    region="Four provinces and Islamabad Capital Territory",
    date="2023",
    value="38.88",
    unit="percent of census population classified urban",
    date_basis="Census2023 observation",
    table_page="Figure4.1 printedp126/PDFp153; section4.1.3 printedp125; visually reviewed",
    sample_size="Census enumeration,not a sample",
    denominator="241499431 residents; urban numerator93884702; AJK/GB absent from cited geography",
    fieldwork_dates="March-May2023; report also describes July2023 post-enumeration survey",
    evidence_scope="Official geographic population classification,not dietary or consumer evidence",
    notes="Final report vintage uses38.88%,where earlier announcement reported38.82%; do not mix vintages. Demographic-detail denominator differs from overall population because restricted areas provide headcounts only.",
    value_status="source_reported_census_percentage",
    raw_file="data/raw/cultural/pakistan/census-national-2023.pdf",
)

add(
    "diaspora_food_adaptation",
    "Bradford Pakistani-origin participants described combining South Asian and Western foods and drawing on family food-sharing networks. A separate UK study found both identity-linked food practices and variation across generations and individuals.",
    "pk_cultural_food_insecurity_diaspora_2018",
    region="Bradford,UK Pakistani diaspora",
    date="2018-11-05",
    evidence_source_ids="pk_cultural_british_pakistanis_2024",
    table_page="Methods; Food and eating practices; Apparent reasons for lower reporting of food insecurity",
    sample_size="16 women total;8 Pakistani-origin women",
    denominator="qualitative community-recruited women in Bradford; no representative population denominator",
    fieldwork_dates="2016-07 to2016-11",
    evidence_scope="Diaspora experiences from selected women,not Pakistan-national behaviour",
    notes="Historical fieldwork. Findings are descriptive; no prevalence estimate,causal migration effect or cultivated-meat acceptance inference.",
    raw_file="data/raw/cultural/pakistan/food-insecurity-diaspora.html",
)

add(
    "price_and_income_constraints",
    "A demand model using Pakistan household survey data classified meat and milk as income-elastic categories while estimating inelastic compensated own-price demand. Affordability can shape food access, but this study does not measure willingness to pay for alternative protein.",
    "pk_cultural_food_demand_2023",
    date="2023-08-25",
    date_basis="publication date; observed data2018-19",
    evidence_source_ids="pakistan_hies_2024_25_table23",
    table_page="Sections3,4,5.3 and6; model tables4-5",
    sample_size="24620 retained households from24809 reported initial records",
    denominator="analysed HIES2018-19 households;eight modelled food groups",
    fieldwork_dates="HIES2018-19; exact dates not stated in inspected article",
    evidence_scope="Cross-sectional LA/AIDS model; food expenditure proxy for income; unit values as price proxies",
    notes="Historical model. HIES2024-25 is only later descriptive quantity context,not an independent elasticity replication. No numerical elasticities or causal effect exported; potential quality/unit-value confounding remains.",
    raw_file="data/raw/cultural/pakistan/food-demand-2023.html",
)

add(
    "religion_and_dietary_data_limits",
    "The census distinguishes religious affiliation and a Scheduled Castes category, but its religion table does not measure vegetarianism, meat consumption or acceptance of cultivated meat. Those dietary estimates remain missing; religious identity is not substituted for behaviour.",
    "pk_cultural_census_2023",
    region="Four provinces and Islamabad Capital Territory",
    date="2023",
    date_basis="Census2023 observation",
    table_page="Table4.13 printedp137/PDFp164; section4.1.2 printedp124; visually reviewed",
    sample_size="Census detailed demographic records",
    denominator="240458089 people with demographic detail; restricted-area headcounts omitted",
    fieldwork_dates="March-May2023",
    evidence_scope="Religious composition context and explicit missing dietary cross-tabulation",
    notes="Do not infer uniform diet among Muslims,Hindus,Christians,Ahmadis,Scheduled Castes or other groups. Vegetarianism by religion/caste remains an unfilled research gap.",
    raw_file="data/raw/cultural/pakistan/census-national-2023.pdf",
)

manifest = []
assignments = {}
for job in jobs:
    original = RAW / job["file"]
    metadata_path = original.with_suffix(original.suffix + ".request.json")
    metadata = json.loads(metadata_path.read_text())
    for path in [original, Path(str(original) + ".headers"), metadata_path]:
        if path.exists():
            assignments[path] = (
                job,
                metadata,
                "original response/header or request outcome; failed response is not evidence",
            )
    text_path = original.with_suffix(".txt")
    if text_path.exists() and text_path not in assignments:
        assignments[text_path] = (
            job,
            metadata,
            "derived text extraction; original bytes retained",
        )
extra_files = {
    "muis-web-extract.json": "muis-2024.html",
    "eid-pide-pdf.txt": "eid-pide.pdf",
    "eid-pide-page1.png": "eid-pide.pdf",
    "eid-pide-page2.png": "eid-pide.pdf",
    "census-urban-page153.png": "census-national-2023.pdf",
    "census-religion-page164.png": "census-national-2023.pdf",
    "dietary-dairy-page44.png": "dietary-guidelines.pdf",
}
for file, origin in extra_files.items():
    job = next(job for job in jobs if job["file"] == origin)
    metadata = json.loads((RAW / (origin + ".request.json")).read_text())
    assignments[RAW / file] = (
        job,
        metadata,
        (
            "tool-extracted official-page fallback"
            if file.endswith(".json")
            else "derived PDF text/render,visually inspected where PNG"
        ),
    )
for path, (job, metadata, note) in sorted(assignments.items()):
    manifest.append(
        {
            "file": str(path.relative_to(ROOT)),
            "url": job["url"],
            "accessed_utc": metadata["accessed_utc"],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "license": LICENSE,
            "source_id": job["source_id"],
            "notes": note,
        }
    )

known = set(SOURCE_META)
existing = {
    row["source_id"]
    for row in csv.DictReader((ROOT / "data/processed/sources.csv").open())
}
for row in rows:
    assert row["source_id"] in known
    assert all(
        i in known | existing for i in row["evidence_source_ids"].split(";") if i
    )
    assert not row["value"] or all(
        row[k]
        for k in ["unit", "denominator", "fieldwork_dates", "table_page", "sample_size"]
    )
assert len({row["dimension"] for row in rows}) >= 8
assert set(assignments) == {path for path in RAW.iterdir() if path.is_file()}
write_csv("cultural_rows.csv", rows)
write_csv("source_rows.csv", sources)
write_csv("manifest_rows.csv", manifest)
print(
    f"Cultural staging:{len(rows)} rows/{len({row['dimension'] for row in rows})} dimensions;{len(sources)} sources;{len(manifest)} raw artifacts"
)
