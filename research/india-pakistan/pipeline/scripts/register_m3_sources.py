"""Register M3 official evidence and specialist provenance ledgers."""

from __future__ import annotations

from datetime import UTC, datetime

from provenance import ROOT, read_csv, register_raw, upsert_source

__all__ = ["register"]

LICENSE = (
    "Publicly accessible; redistribution license not established. Local research only."
)


def register() -> None:
    """Merge source-led evidence without changing downloaded originals."""
    documents = [
        (
            "pbs_hies_2024_25_manual",
            "Manual of Instruction HIES 2024-25",
            "Manual-of-Instruction-HIES-2024-25.pdf",
            "pakistan-hies-2024-25-manual",
            "Printed91: month convention is preceding30 days; printed94: consumed quantity, not purchased; at-home food class excludes restaurant/catered meals. Retains source's internally inconsistent example dates.",
        ),
        (
            "pbs_hies_2024_25_female_questionnaire",
            "Female Questionnaire HIES 2024-25 English",
            "Female-Questionnaire-HIES-2024-25-English.pdf",
            "pakistan-hies-2024-25-female-questionnaire",
            "Official item codes/units and food questionnaire; does not supply complete item-to-nutrient mappings or edible-portion factors.",
        ),
    ]
    for source_id, title, basename, stem, notes in documents:
        path = ROOT / "data/raw/diet" / (stem + ".pdf")
        if not path.exists():
            raise FileNotFoundError(path)
        url = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/" + basename
        accessed = datetime.fromtimestamp(path.stat().st_mtime, UTC).date().isoformat()
        upsert_source(
            {
                "source_id": source_id,
                "title": title,
                "publisher": "Pakistan Bureau of Statistics",
                "url": url,
                "year": "2024",
                "accessed": accessed,
                "tier": "A",
                "access_method": "curl; pdftotext -layout; local page inspection",
                "license": LICENSE,
                "notes": notes,
            }
        )
        for extension in ("pdf", "txt"):
            relative = f"data/raw/diet/{stem}.{extension}"
            register_raw(
                relative,
                url,
                source_id,
                LICENSE,
                (
                    "Original download"
                    if extension == "pdf"
                    else "DERIVED pdftotext -layout from same-stem PDF"
                ),
            )
    for name in ("composition", "requirements"):
        base = ROOT / "scripts/diet" / name
        for row in read_csv(base / "source_rows.csv"):
            upsert_source(row)
        for row in read_csv(base / "manifest_rows.csv"):
            register_raw(
                row["file"],
                row["url"],
                row["source_id"],
                row["license"],
                row.get("notes", ""),
                row.get("accessed_utc") or None,
            )


if __name__ == "__main__":
    register()
