"""Audit the reviewed M5 snapshot without rewriting research data or source evidence."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_HASHES = {
    "altprotein_sources": "77ed0e51df2c257d4eaa1338afe51461e23dda2ee3682ed90d317f64d5d6ef79",
    "altprotein_companies": "6e68c9d258b431ada2b4edefa3d59fff102ee9946be01568865ccba9bd14367d",
    "altprotein_market": "61f0b3d92bfd0abeec433e626c4bbe244a21d621bdadbd3c79a2c8c8e84c8c10",
    "altprotein_policy": "dd1741e4f0d61f8c79e77abcbde2635da715fca0995faf9a961bc3935c06a4f0",
}
REVIEW_NOTES = {
    "altprotein_sources": "notes/M5-SOURCES-REVIEW.md;notes/M5-POLICY-CAPACITY-REVIEW.md;notes/M5-PAKISTAN-REVIEW.md",
    "altprotein_companies": "notes/M5-COMPANIES-REVIEW.md;notes/M5-INDEPENDENT-REVIEW.md;notes/M5-PAKISTAN-REVIEW.md",
    "altprotein_market": "notes/M5-MARKET-HANDOFF.md;notes/M5-PAKISTAN-REVIEW.md;notes/M5-AI-METHOD-ELIGIBILITY-2026-10-13.md",
    "altprotein_policy": "notes/M5-POLICY-CAPACITY-REVIEW.md;notes/M5-PAKISTAN-REVIEW.md;notes/M5-INDEPENDENT-REVIEW.md",
}
COMPANY_BOUNDARIES = {
    "GoodDot": "Company publication/product claim; continuing operations and stock unverified.",
    "Proeon": "Public participation/grant activity; no industrial output established.",
    "Blue Tribe Foods": "Dated product availability report; supplier reports reduced traction; no current sales audit.",
    "Shaka Harry": "Fiscal-year supplier relationship; current meat-alternative assortment unknown.",
    "String Bio": "Fermentation biomass and animal-feed scope; no human-food commercialization established.",
    "Clear Meat": "Research MoU and cell-growth media; not cultivated-meat sales approval.",
    "Biokraft Foods": "Official application under process; stage7 can mean clarification, approval or rejection.",
    "Zero Cow Factory": "Precision-fermentation development and planned pilot; commissioning unknown.",
    "Fermbox Bio": "Partner agreement across food/nonfood sectors; no realized food sales or India output inferred.",
    "Country Delight": "Dairy incumbent with oat-beverage line; not an exclusive alt-protein firm or protein equivalence.",
    "Symega": "Hybrid plant-plus-whey product; not vegan or wholly plant-based.",
    "Matco Foods Limited": "Issuer-reported rice-protein production/exports; no independent inspection or food/feed split.",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read original CSV records without type coercion or field replacement."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def file_hash(path: Path) -> str:
    """Hash bytes without loading a large raw source into memory."""
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def source_ids(row: dict[str, str]) -> set[str]:
    """Resolve every structured primary or supplemental source field."""
    result = set()
    for key, value in row.items():
        if key == "source_id" or key.endswith(("_source_id", "_source_ids")):
            result.update(value.strip() for value in value.split(";") if value.strip())
    return result


def original_qcl_rows() -> dict[tuple[str, str, str], dict[str, str]]:
    """Independently select original FAO country/item/year production observations."""
    result = {}
    with zipfile.ZipFile(ROOT / "data/raw/faostat_qcl_2025-12-31.zip") as archive:
        name = "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
        with archive.open(name) as binary, io.TextIOWrapper(
            binary, encoding="utf-8-sig"
        ) as text:
            for row in csv.DictReader(text):
                if (
                    row["Area Code"] in {"100", "165"}
                    and row["Item Code"] in {"1726", "236", "242"}
                    and row["Element Code"] == "5510"
                    and 2010 <= int(row["Year"]) <= 2024
                ):
                    key = (row["Area"], row["Item Code"], row["Year"])
                    if key in result:
                        raise ValueError(f"Duplicate original QCL observation: {key}")
                    result[key] = row
    return result


def audit_row(
    table: str,
    row: dict[str, str],
    number: int,
    registry: dict[str, dict[str, str]],
    evidence: dict[str, list[dict[str, str]]],
    raw_results: dict[str, str],
    qcl: dict[tuple[str, str, str], dict[str, str]],
    snapshot_unchanged: bool,
) -> dict[str, str]:
    """Combine a reviewed claim boundary with structural and original-evidence checks."""
    warnings: list[str] = []
    failures: list[str] = []
    refs = source_ids(row)
    missing = refs - registry.keys()
    if missing:
        failures.append("Unresolved sources: " + ";".join(sorted(missing)))
    if not row.get("source_id"):
        failures.append("Missing primary source_id")
    if not snapshot_unchanged:
        failures.append(
            "Input bytes changed since semantic review; new review required"
        )
    primary = registry.get(row.get("source_id", ""), {})
    if row.get("tier") != primary.get("tier"):
        failures.append("Row tier does not match registered primary-source tier")
    if row.get("country") not in {"India", "Pakistan"}:
        failures.append("Country outside reviewed scope")
    raw_paths = sorted(
        {artifact["file"] for sid in refs for artifact in evidence.get(sid, [])}
    )
    for sid in refs:
        if not evidence.get(sid):
            failures.append(f"No manifest evidence associated with source {sid}")
    failures.extend(raw_results[path] for path in raw_paths if raw_results[path])
    if row.get("raw_file"):
        if row["raw_file"] not in raw_results:
            failures.append("Direct raw_file is absent from audited source manifest")
        elif (
            row.get("raw_sha256")
            and file_hash(ROOT / row["raw_file"]) != row["raw_sha256"]
        ):
            failures.append("Direct row raw_sha256 differs from bytes")
    company = "N/A: observation is not a company status record."
    geography = (
        f"PASS: explicitly scoped to {row.get('country')}; see claim scope below."
    )
    category = ""
    policy = "N/A: observation is not a policy or product approval."
    claim = ""
    if table == "altprotein_sources":
        metric = row["metric"]
        category = "PASS: " + (row.get("category") or row.get("source_type", ""))
        if not row.get("category"):
            warnings.append(
                "Category column blank; technology is carried in source_type; rendering must retain it"
            )
        if row["source_id"] == "fao_qcl_2025_12_31":
            key = (row["country"], row["item_code"], row["year"])
            original = qcl.get(key)
            if not original:
                failures.append("Original QCL country/item/year not found")
            elif any(
                [
                    row["value"] != original["Value"],
                    row["flag"] != original["Flag"],
                    row["source_item"] != original["Item"],
                    row["source_unit"] != original["Unit"],
                ]
            ):
                failures.append("Original QCL value/flag/item/unit mismatch")
            if (
                metric != "crop_production_potential_feedstock_context"
                or row["category"] != "plant_crop"
            ):
                failures.append(
                    "Crop production misclassified as alternative-protein production"
                )
            claim = "Raw crop-production context, including food/feed uses; no alternative-protein allocation or isolate yield. Groundnuts are in-shell."
            if row["flag"] == "E":
                warnings.append(
                    "FAO estimated observation flag E retained; do not present as reported actual"
                )
        elif row["source_id"] == "sopa_soymeal_tables_snapshot_2026_10_13":
            if Decimal(row["value"]) != Decimal(row["source_value"]) * Decimal(1000000):
                failures.append("SOPA million-tonne source value conversion mismatch")
            if row["category"] != "plant_processing_output":
                failures.append("Soymeal processing output category mismatch")
            if not row.get("period"):
                failures.append("Missing original SOPA reporting period")
            warnings.append(
                "Release date and actual/estimate/projection status unknown; year is period start"
            )
            claim = "Soymeal mass can serve feed/food/industrial uses; no food-grade allocation; overlapping periods/series cannot be summed."
        elif metric == "reported_input_processing_capability":
            if row["unit"] != "tonnes_insect_input_per_year":
                failures.append("Insect input mass loses input/year semantics")
            company = "WARN: historical institutional capacity report, not current operations or utilization."
            warnings.append(
                "Historical insect-input capability for animal feed; not edible protein output"
            )
            claim = row["notes"]
        elif metric == "reported_multiuse_facility_scale":
            if row["unit"] != "kilolitre":
                failures.append("Facility volume loses volumetric unit")
            company = "WARN: platform reported set up; no measured protein throughput."
            warnings.append(
                "Multiuse vessel/facility scale; no annual mass output or protein-only allocation"
            )
            claim = row["notes"]
        else:
            if row.get("value"):
                failures.append(
                    "Unquantified capacity record contains an unsupported numerical value"
                )
            company = (
                "WARN: research, demonstration, partnership or pilot announcement only."
            )
            warnings.append(
                "Numeric capacity and/or commissioning remain missing, never zero"
            )
            claim = row["notes"]
        if row.get("location"):
            geography += (
                " Location: "
                + row["location"]
                + "; no foreign partnership capacity assigned domestically."
            )
    elif table == "altprotein_companies":
        name = row["company"]
        claim = COMPANY_BOUNDARIES.get(name, "")
        if not claim:
            failures.append("Company lacks manual status/category review")
        evidence_date = row.get("status_evidence_date", "")
        if not re.fullmatch(r"202[56]-(?:\d{2}-\d{2}|Q[1-4])", evidence_date):
            failures.append("Company status has no reviewed 2025/2026 evidence date")
        if not row.get("status_checked") or not row.get("status_source_id"):
            failures.append("Missing status check date or dated source reference")
        if not row.get("evidence_date_precision"):
            warnings.append(
                "Separate evidence_date_precision missing; complete filing date is stored"
            )
        company = "WARN: dated evidence " + evidence_date + ". " + claim
        warnings.append(claim)
        category = "PASS: " + row["category"]
        for marker in ("String Bio", "Zero Cow Factory", "Fermbox Bio"):
            if name == marker and "fermentation" not in row["category"].lower():
                failures.append("Fermentation entity loses technology category")
        if name == "Symega" and not all(
            word in row["category"].lower() for word in ("hybrid", "whey")
        ):
            failures.append(
                "Hybrid whey product misrepresented as entirely plant-based"
            )
        geography += " " + (row.get("geographic_basis") or row.get("location", ""))
        if name == "Biokraft Foods":
            policy = "WARN: stage7 decision code is ambiguous; no product approval established."
    elif table == "altprotein_market":
        category = "PASS: separate source segment " + row["segment"]
        numerical = [
            Decimal(row[key]) for key in ("low", "central", "high") if row[key]
        ]
        if numerical != sorted(numerical):
            failures.append("Market bounds are not ordered")
        if row["tier"] == "C" and not (row["low"] and row["high"]):
            failures.append("Tier-C market observation lacks published range endpoints")
        if not numerical and not row.get("missing_reason"):
            failures.append("Missing market values have no explanation")
        if row["country"] == "India":
            if row.get("stale") != "true":
                failures.append("Historical GFI market model lacks stale flag")
            warnings.append(
                "Stale source model; not current sales; proprietary inputs and price basis undisclosed"
            )
            if row["estimate_type"] == "source_published_forward_scenarios":
                warnings.append(
                    "Source scenario bounds are not confidence intervals or expected values"
                )
            claim = row["range_semantics"] + " " + row["segment_scope_note"]
            geography += " Domestic market and export potential remain separate; exports are not domestic demand."
            if row["segment"] == "cultivated_meat":
                warnings.append(
                    "Cultivated export category includes growth factors/recombinant proteins, not solely finished meat"
                )
            if row["segment"] == "all_smart_protein":
                warnings.append(
                    "Total overlaps component rows; never add total to components"
                )
            if row.get("source_conflict"):
                warnings.append(
                    "Source narrative/table conflicts retained; use declared table cells only"
                )
        else:
            warnings.append(
                "Tier-C opaque publisher growth scenarios mix food/feed and omit baseline/input details"
            )
            if row["central"]:
                failures.append("Unpublished Pakistan central estimate filled")
            claim = row["segment_scope_note"] + " " + row["missing_reason"]
            geography += " Pakistan-specific commercial narrative, not an APAC value allocated to Pakistan."
        if row["source_id"] == "indexbox_synthetic_protein_pakistan_2026":
            if row.get("evidence_status") != "HELD_AI_METHOD_UNRESOLVED":
                failures.append(
                    "IndexBox numeric ranges must remain HELD pending AI-method eligibility evidence"
                )
            if (
                not row.get("evidence_hold_reason")
                or row.get("methodology_source_id")
                != "indexbox_methodology_snapshot_20261013"
            ):
                failures.append(
                    "Held evidence lacks its reason or methodology provenance"
                )
            warnings.append(
                "HELD: numeric use excluded; specific AI derivation unresolved, not proved AI-generated"
            )
            claim = (
                "HELD provenance only; excluded from dashboard numbers and downloads. "
                + claim
            )
        company = "N/A: a market model is not evidence of any named firm's operations."
    else:
        policy_date = row.get("policy_date", "")
        if not re.fullmatch(r"\d{4}(?:-\d{2}-\d{2})?", policy_date):
            failures.append(
                "Policy date missing or does not preserve year/day precision"
            )
        if (
            policy_date
            and int(policy_date[:4]) < 2024
            and "stale" not in (row.get("notes", "") + row.get("freshness", "")).lower()
        ):
            failures.append("Pre-2024 policy lacks stale limitation")
        if not row.get("date_basis"):
            warnings.append(
                "Structured date_basis absent; edition/issue/notification meaning is in notes and prior source review"
            )
        if row.get("cultivated_specific_approval") != "not_established_by_this_source":
            failures.append(
                "Policy row overstates product-specific cultivated authorization"
            )
        policy = (
            "PASS: "
            + policy_date
            + "; "
            + (row.get("date_basis") or "source-document date reviewed; see notes")
        )
        if row.get("publication_date"):
            policy += "; Gazette publication separately " + row["publication_date"]
        geography = (
            "PASS: jurisdiction explicitly "
            + row["jurisdiction"]
            + "; provincial PFA rules are not national law."
        )
        category = "N/A: policy pathway, not protein-production technology or a company's product category."
        company = "N/A: general framework, standard, funding call or application status is not company operating proof."
        claim = row["notes"]
        warnings.append(
            "No specific cultivated-meat approval established; policy pathway must retain scope"
        )
        if "ambiguous" in row.get("status", ""):
            warnings.append(
                "FSSAI stage7 can mean clarification, approval or rejection"
            )
    canonical = json.dumps(
        row, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return {
        "dataset": table + ".csv",
        "data_row": str(number),
        "row_id": table + ":" + digest[:16],
        "row_sha256": digest,
        "entity_or_segment": row.get("company")
        or row.get("entity")
        or row.get("policy")
        or row.get("segment")
        or row.get("source_type", ""),
        "country": row["country"],
        "source_id": row["source_id"],
        "all_source_ids": ";".join(sorted(refs)),
        "tier": row["tier"],
        "evidence_status": row.get("evidence_status", ""),
        "numeric_use_held": str(
            row.get("evidence_status", "").upper().startswith("HELD")
        ).lower(),
        "company_status_review": company,
        "geography_review": geography,
        "category_review": category,
        "policy_date_review": policy,
        "claim_boundary": claim,
        "integrity_review": (
            "FAIL: see failures"
            if failures
            else "PASS: source references, tiers, raw presence/hashes and relevant value checks"
        ),
        "outcome": "FAIL" if failures else "WARN" if warnings else "PASS",
        "warnings": " | ".join(warnings),
        "failures": " | ".join(failures),
        "prior_evidence_review": REVIEW_NOTES[table],
        "raw_artifact_count": str(len(raw_paths)),
    }


def main() -> None:
    """Write a rowwise ledger and concise audit summary; exit nonzero on material failure."""
    registry_rows = read_csv(ROOT / "data/processed/sources.csv")
    registry = {row["source_id"]: row for row in registry_rows}
    tables = {
        name: read_csv(ROOT / "data/processed" / (name + ".csv"))
        for name in REVIEWED_HASHES
    }
    refs = set().union(*(source_ids(row) for rows in tables.values() for row in rows))
    evidence: dict[str, list[dict[str, str]]] = {}
    raw_results = {}
    for artifact in read_csv(ROOT / "data/raw/MANIFEST.csv"):
        if artifact["source_id"] in refs:
            evidence.setdefault(artifact["source_id"], []).append(artifact)
            path = ROOT / artifact["file"]
            raw_results[artifact["file"]] = (
                "Missing raw file: " + artifact["file"]
                if not path.is_file()
                else (
                    "Raw hash mismatch: " + artifact["file"]
                    if file_hash(path) != artifact["sha256"]
                    else ""
                )
            )
    qcl = original_qcl_rows()
    ledger = []
    snapshots = {}
    for table, rows in tables.items():
        digest = file_hash(ROOT / "data/processed" / (table + ".csv"))
        snapshots[table] = {
            "sha256": digest,
            "semantic_review_snapshot_matches": digest == REVIEWED_HASHES[table],
        }
        for number, row in enumerate(rows, 1):
            try:
                ledger.append(
                    audit_row(
                        table,
                        row,
                        number,
                        registry,
                        evidence,
                        raw_results,
                        qcl,
                        digest == REVIEWED_HASHES[table],
                    )
                )
            except (InvalidOperation, ValueError, KeyError) as exc:
                raise ValueError(f"Malformed {table} row {number}: {exc}") from exc
    summary = {
        "checked_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "audit_scope": "Nadja rowwise status/geography/category/policy-date review of saved M5 evidence; no new external facts or publication",
        "pass": all(row["outcome"] != "FAIL" for row in ledger),
        "verdict": (
            "PASS_WITH_WARNINGS"
            if all(row["outcome"] != "FAIL" for row in ledger)
            else "NEEDS_FIXES"
        ),
        "rows_audited": len(ledger),
        "by_table": {name: len(rows) for name, rows in tables.items()},
        "outcomes": dict(Counter(row["outcome"] for row in ledger)),
        "held_numeric_rows": sum(row["numeric_use_held"] == "true" for row in ledger),
        "held_interpretation": "Held source values remain provenance only; audit integrity PASS does not make them eligible for numeric use.",
        "unique_sources": len(refs),
        "raw_artifacts_hashed": len(raw_results),
        "qcl_original_observations_reconciled": len(qcl),
        "input_snapshots": snapshots,
        "failures": [
            {"row_id": row["row_id"], "reason": row["failures"]}
            for row in ledger
            if row["failures"]
        ],
        "warning_interpretation": "WARN is a qualified evidence/use limitation, not a numeric or categorical error. N/A checklist cells explain why an axis is inapplicable.",
        "no_processed_data_modified": True,
    }
    with (ROOT / "logs/altprotein-audit.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ledger[0]))
        writer.writeheader()
        writer.writerows(ledger)
    (ROOT / "logs/altprotein-audit.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "verdict",
                    "rows_audited",
                    "outcomes",
                    "unique_sources",
                    "raw_artifacts_hashed",
                    "failures",
                )
            },
            indent=2,
        )
    )
    if not summary["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
