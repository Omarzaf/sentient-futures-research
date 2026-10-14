"""Build distinct nutritional-risk proxies without claiming protein deficiency."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from provenance import ROOT, read_csv, register_raw, upsert_source, write_csv

__all__ = [
    "affected_count",
    "build",
    "register_evidence",
    "validate_registered_evidence",
]


def validate_registered_evidence() -> None:
    """Require pre-registered evidence without rewriting coordinator-owned ledgers."""
    sources = {r["source_id"] for r in read_csv(ROOT / "data/processed/sources.csv")}
    manifest = {r["file"]: r for r in read_csv(ROOT / "data/raw/MANIFEST.csv")}
    for group in ("anthropometry", "sofi"):
        base = ROOT / "scripts/deficiency" / group
        if any(
            r["source_id"] not in sources for r in read_csv(base / "source_rows.csv")
        ):
            raise ValueError(
                f"Unregistered {group} source; coordinator registration required"
            )
        for row in read_csv(base / "manifest_rows.csv"):
            registered = manifest.get(row["file"], {})
            if any(registered.get(f) != row[f] for f in ("sha256", "source_id", "url")):
                raise ValueError(f"Unregistered or changed evidence: {row['file']}")


def register_evidence() -> None:
    """Merge the two specialist evidence ledgers before joining their rows."""
    for group in ("anthropometry", "sofi"):
        base = ROOT / "scripts/deficiency" / group
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


def affected_count(row: dict[str, str]) -> tuple[str, str]:
    """Prefer source counts; otherwise scale only a documented matched population."""
    if row.get("population_affected_published", ""):
        return row["population_affected_published"], "direct_source_reported_count"
    if not row.get("population_base", ""):
        return "", "missing_compatible_population_base"
    if row.get("population_alignment") not in (
        "source_matched",
        "documented_approximation",
    ):
        raise ValueError("Population denominator needs an explicit coverage alignment")
    if row["unit"] not in ("percent", "%", "percent_of_children_under5"):
        raise ValueError("Only a population prevalence may scale a population")
    rate, base = Decimal(row["value"]), Decimal(row["population_base"])
    if not 0 <= rate <= 100 or base <= 0:
        raise ValueError("Population arithmetic outside its domain")
    count = (rate * base / 100).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return (
        str(count),
        "published_rate_times_source_population_divided_by_100_rounded_to_person",
    )


def build() -> None:
    """Combine source-bounded proxies, preserving missing counts and source vintages."""
    validate_registered_evidence()
    rows = []
    for group in ("anthropometry", "sofi"):
        incoming = read_csv(ROOT / "scripts/deficiency" / group / "extracted_rows.csv")
        if not incoming:
            raise ValueError(f"Missing {group} evidence rows")
        for source_row in incoming:
            row = dict(source_row)
            if not row.get("estimate_type"):
                row["estimate_type"] = "modelled_population_proxy"
            if not row.get("period"):
                row["period"] = row.get("survey_period") or row["year"]
            row["population_affected"], row["affected_count_method"] = affected_count(
                row
            )
            row["population_deficiency_prevalence"] = ""
            row["notes"] = (
                row.get("notes", "")
                + " This is a separately defined nutrition-risk proxy, not measured protein deficiency. Indicators and repeated source vintages overlap and must not be summed."
            )
            rows.append(row)
    sources = {r["source_id"] for r in read_csv(ROOT / "data/processed/sources.csv")}
    source_tiers = {
        r["source_id"]: r["tier"] for r in read_csv(ROOT / "data/processed/sources.csv")
    }
    for row in rows:
        row["source_tier"] = source_tiers[row["source_id"]]
        row["tier"] = (
            "derived"
            if row["affected_count_method"].startswith("published_rate_times")
            else row["source_tier"]
        )
        for field, value in row.items():
            if (
                (field == "source_id" or field.endswith("_source_id"))
                and value
                and value not in sources
            ):
                raise ValueError(f"Unresolved {field}: {value}")
    fields = [
        "country",
        "region",
        "year",
        "indicator",
        "value",
        "unit",
        "population_affected",
        "source_id",
    ]
    fields += sorted(set().union(*(r.keys() for r in rows)) - set(fields))
    write_csv(
        ROOT / "data/processed/deficiency_population.csv",
        fields,
        [{f: r.get(f, "") for f in fields} for r in rows],
    )
    n_counts = sum(bool(r["population_affected"]) for r in rows)
    print(
        f"Distinct proxy observations: {len(rows)}; with affected counts: {n_counts}; no protein-specific prevalence inferred."
    )


if __name__ == "__main__":
    build()
