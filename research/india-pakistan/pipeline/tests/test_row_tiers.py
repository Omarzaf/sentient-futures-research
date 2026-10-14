"""Keep analyst calculations distinct from the authority of their input source."""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import provenance


def test_derived_metric_cannot_inherit_official_tier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Source tier A remains a source property, not the analyst result's grade."""
    monkeypatch.setattr(provenance, "ROOT", tmp_path)
    folder = tmp_path / "data/processed"
    folder.mkdir(parents=True)
    (folder / "sources.csv").write_text("source_id,tier\ns1,A\n")
    path = folder / "meat_supply_national.csv"
    provenance.write_csv(
        path,
        ["source_id", "metric", "value", "tier"],
        [
            {
                "source_id": "s1",
                "metric": "apparent_consumption_production_plus_imports_minus_exports",
                "value": "4",
                "tier": "A",
            },
            {
                "source_id": "s1",
                "metric": "food_supply_quantity",
                "value": "5",
                "tier": "",
            },
        ],
    )
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    assert [r["tier"] for r in rows] == ["derived", "A"]
    assert [r["source_tier"] for r in rows] == ["A", "A"]


def test_unknown_source_is_not_assigned_a_default_tier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing source join must fail instead of silently grading the observation."""
    monkeypatch.setattr(provenance, "ROOT", tmp_path)
    path = tmp_path / "data/processed/diet_composition.csv"
    with pytest.raises(ValueError, match="Unregistered processed source"):
        provenance.write_csv(
            path, ["source_id", "value"], [{"source_id": "unknown", "value": "2"}]
        )
