"""Protect source dates, exclusions and receipt immutability during integration."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import provenance
import register_m5_evidence as builder

PROJECT = Path(__file__).resolve().parents[1]
BATCH = PROJECT / builder.REVISION


@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Use real frozen rows and raw bytes with isolated mutable registries."""
    stage = tmp_path / builder.REVISION
    stage.mkdir(parents=True)
    for path in BATCH.glob("*.csv"):
        shutil.copyfile(path, stage / path.name)
    baseline = json.loads((BATCH / "integration-baseline.json").read_text())
    for name, entry in baseline.items():
        records = list(entry["rows"].values())
        provenance.write_csv(tmp_path / name, list(records[0]), records)
    needed = {row["file"] for row in provenance.read_csv(stage / "manifest_rows.csv")}
    for name in builder.TABLES:
        needed.update(
            row["raw_file"]
            for row in provenance.read_csv(stage / name)
            if row.get("raw_file")
        )
    for name in needed:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, target)
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(provenance, "ROOT", tmp_path)
    return tmp_path


def test_two_builds_preserve_registry_history_and_frozen_row_counts(
    isolated: Path,
) -> None:
    """A repeated build must neither renew receipts nor append output observations."""
    before = {
        name: provenance.read_csv(isolated / name)
        for name in ("data/processed/sources.csv", "data/raw/MANIFEST.csv")
    }
    builder.register()
    first = {
        str(path.relative_to(isolated)): path.read_bytes()
        for path in (isolated / "data").rglob("*.csv")
    }
    builder.register()
    second = {
        str(path.relative_to(isolated)): path.read_bytes()
        for path in (isolated / "data").rglob("*.csv")
    }
    assert first == second
    for name, old_rows in before.items():
        key = "source_id" if name.endswith("sources.csv") else "file"
        current = {row[key]: row for row in provenance.read_csv(isolated / name)}
        assert all(current[row[key]] == row for row in old_rows)
        assert len(current) - len(old_rows) == (14 if key == "source_id" else 35)
    expected = {
        "altprotein_policy.csv": 16,
        "altprotein_companies.csv": 16,
        "altprotein_company_exclusions.csv": 2,
        "altprotein_retail_offers.csv": 1,
    }
    for filename, count in expected.items():
        assert len(provenance.read_csv(isolated / "data/processed" / filename)) == count


def test_changed_raw_fails_before_registry_or_output_mutation(isolated: Path) -> None:
    """Corrupted newly staged source bytes cannot be silently registered."""
    manifests = provenance.read_csv(isolated / builder.REVISION / "manifest_rows.csv")
    (isolated / manifests[0]["file"]).write_bytes(b"changed source")
    before = {
        str(path): path.read_bytes() for path in (isolated / "data").rglob("*.csv")
    }
    with pytest.raises(ValueError, match="Staged raw hash differs"):
        builder.register()
    assert {
        str(path): path.read_bytes() for path in (isolated / "data").rglob("*.csv")
    } == before


def test_source_year_cannot_refresh_an_older_event() -> None:
    """Recent publication/access metadata must not make a historical event fresh."""
    source = {"year": "2026", "tier": "A"}
    row = builder.dated_row(
        {"source_id": "example", "tier": "A", "policy_date": "2024-08-24"},
        source,
        "policy_date",
    )
    assert row["source_year"] == "2026"
    assert row["policy_year"] == "2024"
    assert row["stale"] == "true"
    undated = builder.dated_row(
        {
            "source_id": "example",
            "tier": "A",
            "status_evidence_date": "",
            "status_checked": "2026-10-13",
        },
        source,
        "status_evidence_date",
    )
    assert undated["evidence_year"] == ""
    assert undated["stale"] == "unknown"


def test_decision_critical_dates_and_scope_survive_integration(isolated: Path) -> None:
    """Future law dates, unknown closure dates and feed-only scope stay explicit."""
    builder.register()
    policies = {
        row["policy_id"]: row
        for row in provenance.read_csv(
            isolated / "data/processed/altprotein_policy.csv"
        )
    }
    assert (
        policies["IN_FSSAI_VEGAN_LOGO_AMENDMENT_2026"]["effective_date"] == "2027-07-01"
    )
    assert (
        policies["IN_FSSAI_VEGAN_IMPORT_AMENDMENT_2026"]["effective_date"]
        == "2027-04-01"
    )
    assert (
        policies["IN_FSSAI_DAIRY_ANALOGUE_CONSULTATION_2025"]["status"]
        == "consultation_paper_not_final_new_rule"
    )
    assert (
        policies["PK_PFA_FUNCTIONAL_NOVEL_2025"]["cultivated_specific_approval"]
        == "not_established_by_this_source"
    )
    companies = {
        row["company"]: row
        for row in provenance.read_csv(
            isolated / "data/processed/altprotein_companies.csv"
        )
    }
    assert companies["UnCrave (Licious)"]["closure_reported_date"] == "2025-09-09"
    assert companies["UnCrave (Licious)"]["closure_effective_date"] == ""
    assert companies["Biokraft Foods"]["application_date"] == "2025-08-20"
    assert companies["Phyx44"]["country"] == "India"
    exclusions = provenance.read_csv(
        isolated / "data/processed/altprotein_company_exclusions.csv"
    )
    assert {row["company"] for row in exclusions} == {"String Bio", "Ful Foods"}
    assert not {"String Bio", "Ful Foods"} & companies.keys()
    for row in provenance.read_csv(isolated / builder.REVISION / "manifest_rows.csv"):
        assert (
            hashlib.sha256((isolated / row["file"]).read_bytes()).hexdigest()
            == row["sha256"]
        )
