"""Build a bounded company directory snapshot, preserving status uncertainty."""

import csv
import hashlib
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/altprotein/companies"
OUT = Path(__file__).parent
ACCESS = "2026-10-13"
SOURCE = "gfi_ecosystem_company_snapshot_20261013"


def clean(value: str) -> str:
    """Remove markup and collapse whitespace without adding facts."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def write(name: str, rows: list[dict]) -> None:
    """Write a staging CSV with consistent columns."""
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


sources = [
    (
        SOURCE,
        "GFI alternative protein ecosystem country snapshot",
        "Good Food Institute",
        "https://ecosystem.gfi.org/country/india/",
        "",
        "B",
        "Undated directory snapshot; listing does not establish current operating status. Pakistan country page has researcher records only, not proof of no companies in country.",
    ),
    (
        "gfi_proeon_dialogue_2026",
        "Local crops, global scale",
        "GFI India",
        "https://gfi-india.org/local-crops-global-scale/",
        "2026",
        "B",
        "Published June 8 2026; participation by Proeon representative is evidence of activity, not sales or verified continuing operations.",
    ),
    (
        "proeon_grant_2025",
        "Proeon secures grant in Project EGGcellent",
        "Proeon",
        "https://proeon.co/proeon-secures-e1-million-grant/",
        "2025",
        "C",
        "Company announcement dated 14 April 2025; self-reported.",
    ),
    (
        "gooddot_comparison_blog_2026",
        "GoodDot vs Shaka Harry: Plant-Based Brand Review 2026",
        "GoodDot",
        "https://gooddot.in/blogs/news/gooddot-vs-shaka-harry-comparison",
        "2026",
        "C",
        "Company blog published June 15 2026; evidence of company publishing and claimed product offering only. Not independent verification of competitors.",
    ),
    (
        "gfi_plant_based_soi_2025",
        "State of the Industry Report: Plant-based meat seafood eggs dairy and ingredients 2025",
        "Good Food Institute",
        "https://gfi.org/wp-content/uploads/2026/04/GFI_State-of-the-Industry-report-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf",
        "2026",
        "B",
        "Reporting year 2025; PDF includes RELSUS India facility, Symega partnership, Country Delight oat beverage. Foreign headquarters and hybrid whey must not be relabelled as Indian plant-only manufacturers.",
    ),
    (
        "gfi_india_industry_catalog",
        "GFI India industry resource page",
        "GFI India",
        "https://gfi-india.org/industry/",
        "",
        "B",
        "Undated resource catalog; not dated operating-status evidence.",
    ),
]
write(
    "source_rows.csv",
    [
        {
            "source_id": i,
            "title": t,
            "publisher": p,
            "url": u,
            "year": y,
            "accessed": ACCESS,
            "tier": tier,
            "access_method": "curl; public HTML and read-only JSON endpoints",
            "license": "Public access; redistribution license not established",
            "notes": n,
        }
        for i, t, p, u, y, tier, n in sources
    ],
)
records = json.loads((RAW / "gfi-india-markers.json").read_text())
rows = []
for record in records:
    if record["type"] != "company":
        continue
    path = RAW / f"gfi-record-{record['id']}.json"
    content = json.loads(path.read_text())["content"] if path.exists() else ""
    terms = {
        clean(k): clean(v)
        for k, v in re.findall(
            r"<li><strong>(.*?)</strong>(.*?)</li>", content, re.DOTALL
        )
    }
    row = {
        "company": html.unescape(record["title"]),
        "country": "India",
        "category": terms.get("Alternative protein type:", ""),
        "status": "directory_listed_operating_status_unverified",
        "status_checked": ACCESS,
        "status_evidence_date": "",
        "source_id": SOURCE,
        "status_source_id": "",
        "directory_url": record["permalink"],
        "directory_id": record["id"],
        "company_focus": terms.get("Company focus:", ""),
        "product_type": terms.get("Product type:", ""),
        "location": record["location"],
        "evidence_locator": f"gfi-india-markers.json id={record['id']}; {path.name}",
        "notes": "Directory country is recorded location; listing date is unknown. Do not count as confirmed operating in 2025/2026.",
    }
    if record["id"] == 4735:
        row.update(
            status="2026_public_activity_documented_operating_status_unverified",
            status_evidence_date="2026-06-08",
            status_source_id="gfi_proeon_dialogue_2026",
            notes="GFI identifies Proeon participant in dialogue; company grant announcement dated 2025-04-14 corroborates historical activity. No sales or ongoing production inference.",
        )
    if record["id"] == 4542:
        row.update(
            status="2026_company_publication_product_claim_operating_status_unverified",
            status_evidence_date="2026-06-15",
            status_source_id="gooddot_comparison_blog_2026",
            notes="Dated company-authored marketing article establishes publishing activity and self-claimed offering; independent operating verification remains missing.",
        )
    if not path.exists():
        row["notes"] += " Record detail curl timed out; category remains missing."
    rows.append(row)
write("company_candidates.csv", rows)
url_map = {
    "gfi-ecosystem.html": ("https://ecosystem.gfi.org/", SOURCE),
    "gfi-india.html": ("https://ecosystem.gfi.org/country/india/", SOURCE),
    "gfi-pakistan.html": ("https://ecosystem.gfi.org/country/pakistan/", SOURCE),
    "gfi-india-markers.json": (
        "https://ecosystem.gfi.org/wp-json/ecosystem/markers",
        SOURCE,
    ),
    "gfi-theme.js": (
        "https://ecosystem.gfi.org/wp-content/themes/ecosystem/dist/theme.min.js?ver=1789056479",
        SOURCE,
    ),
    "gfi-pakistan-record-261105.json": (
        "https://ecosystem.gfi.org/wp-json/ecosystem/content/261105",
        SOURCE,
    ),
    "gfi-india-industry.html": (sources[5][3], sources[5][0]),
    "gfi-proeon-june2026.html": (sources[1][3], sources[1][0]),
    "proeon-grant-april2025.html": (sources[2][3], sources[2][0]),
    "gooddot-blog2026.html": (sources[3][3], sources[3][0]),
    "gfi-plant-based-2025-published2026.pdf": (sources[4][3], sources[4][0]),
    "gfi-plant-based-2025-published2026.txt": (sources[4][3], sources[4][0]),
}
manifest = []
for path in sorted(RAW.iterdir()):
    if path.name.startswith("gfi-record-"):
        url_map[path.name] = (
            f"https://ecosystem.gfi.org/wp-json/ecosystem/content/{path.stem.split('-')[-1]}",
            SOURCE,
        )
    url, source = url_map[path.name]
    manifest.append(
        {
            "file": str(path.relative_to(ROOT)),
            "url": url,
            "accessed_utc": datetime.fromtimestamp(
                path.stat().st_mtime, UTC
            ).isoformat(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "license": "Public access; redistribution license not established",
            "source_id": source,
            "notes": (
                "Derived PDF text via pdftotext -layout."
                if path.suffix == ".txt"
                else "Original downloaded bytes. Markers endpoint is read-only POST of country-page marker_ids."
            ),
        }
    )
write("manifest_rows.csv", manifest)
assert len({r["directory_id"] for r in rows}) == len(rows)
assert all(r["source_id"] == SOURCE for r in rows)
print(
    f"{len(rows)} India directory candidates; {len(manifest)} raw artifacts; {len(sources)} sources. No current operating count asserted."
)
