"""Register downloaded M1 source files without implying publication clearance."""

from __future__ import annotations

import hashlib

from provenance import ROOT, read_csv, register_raw, upsert_source

__all__ = ["register_national", "register_oecd"]


def register_national() -> None:
    """Verify specialist hashes and merge the national-report provenance records."""
    for row in read_csv(ROOT / "scripts/national/source_rows.csv"):
        upsert_source(row)
    for row in read_csv(ROOT / "scripts/national/manifest_rows.csv"):
        with (ROOT / row["file"]).open("rb") as handle:
            if hashlib.file_digest(handle, "sha256").hexdigest() != row["sha256"]:
                raise ValueError(f"Specialist raw bytes changed: {row['file']}")
        register_raw(
            row["file"],
            row["url"],
            row["source_id"] or "india_bahs_2025_pib",
            row["license"],
            row["kind"] + "; derived_from=" + row["derived_from"],
            row["accessed_utc"],
        )


def register_oecd() -> None:
    """Register the OECD vintage and all successful, failed and derived local receipts."""
    source_id = "oecd_fao_outlook_2025_2034"
    base = "https://sdmx.oecd.org/public/rest/"
    data_url = (
        base
        + "data/OECD.TAD.ATM,DSD_AGR@DF_OUTLOOK_2025_2034,1.1/IND+PAK.A....?startPeriod=2010&endPeriod=2034&dimensionAtObservation=AllDimensions"
    )
    structure_url = (
        base + "dataflow/OECD.TAD.ATM/DSD_AGR@DF_OUTLOOK_2025_2034/1.1?references=all"
    )
    license_text = "OECD Terms and Conditions, section 3 (Data); attribution required; third-party restrictions may apply"
    upsert_source(
        {
            "source_id": source_id,
            "title": "OECD-FAO Agricultural Outlook 2025-2034, national annual series",
            "publisher": "OECD/FAO",
            "url": data_url,
            "year": "2025",
            "accessed": "2026-10-13",
            "tier": "A",
            "access_method": "curl SDMX CSV and structural XML",
            "license": license_text,
            "notes": "Exact vintage AO_2025_2034. 2025-2034 projection; 2010-2024 historical/base estimates. OBS_STATUS=A does not mean historical actual. Preserve UNIT_MULT and weight convention. Retail-weight per-capita supply differs from FBS. See notes/M1-OECD-HANDOFF.md.",
        }
    )
    entries = [
        (
            "outlook_2025_2034_ind_pak.csv",
            data_url,
            "Original SDMX response; exact vintage in VERSION_ID.",
        ),
        (
            "data_retry.headers.txt",
            data_url,
            "Successful HTTP receipt for CSV download.",
        ),
        (
            "structure.xml",
            structure_url,
            "Official structural metadata, code labels and conventions.",
        ),
        (
            "structure.headers.txt",
            structure_url,
            "Successful HTTP receipt for structural metadata.",
        ),
        (
            "outlook_2025_2034.headers.txt",
            base
            + "v1/data/OECD.TAD.ATM,DSD_AGR@DF_OUTLOOK_2025_2034,1.1/IND+PAK.A....?startPeriod=2010&endPeriod=2034&dimension_at_observation=AllDimensions",
            "FAILED HTTP 403 receipt. Not evidence; superseded by direct endpoint.",
        ),
        (
            "terms.headers.txt",
            "https://www.oecd.org/en/about/terms-conditions.html",
            "FAILED HTTP 403 receipt; license reviewed through web-text retrieval noted in handoff.",
        ),
        (
            "meat_rows_staging.csv",
            data_url,
            "DERIVED staging file, not original download. Reproduce with scripts/oecd/extract_meat.py; numeric strings preserved.",
        ),
    ]
    for filename, url, notes in entries:
        register_raw("data/raw/oecd/" + filename, url, source_id, license_text, notes)


if __name__ == "__main__":
    register_oecd()
    register_national()
