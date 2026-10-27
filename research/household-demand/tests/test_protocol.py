"""Tests that the registered protocol is complete and PROTOCOL.md matches protocol.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads((HERE / "protocol.json").read_text())
MARKDOWN = (HERE / "PROTOCOL.md").read_text()


def _percent(share: float) -> str:
    return f"{share * 100:.1f}%"


def test_required_keys_and_seed():
    required = {"version", "registered_at_utc", "decisions", "analogs", "priors"}
    assert required | {"metrics", "seed"} <= set(PROTOCOL)
    assert PROTOCOL["seed"] == 20261018
    assert str(PROTOCOL["seed"]) in MARKDOWN


def test_every_decision_row_rendered_verbatim():
    assert len(PROTOCOL["decisions"]) == 30
    for row in PROTOCOL["decisions"]:
        numbers = ", ".join(str(n) for n in row["numbers"])
        assert f"| {numbers} | {row['decision']} |" in MARKDOWN, numbers


def test_analog_candidates_and_fallback_prior():
    ids = [c["id"] for c in PROTOCOL["analogs"]["candidates"]]
    assert ids == ["packaged_liquid_milk", "soya_chunks", "branded_rtc_chicken"]
    for candidate in PROTOCOL["analogs"]["candidates"]:
        assert candidate["series_needed"]
        assert candidate["product"] in MARKDOWN
    prior = PROTOCOL["priors"]["bass_fallback"]
    assert (prior["p"], prior["q"]) == (0.03, 0.38)
    assert "p 0.03" in MARKDOWN and "q 0.38" in MARKDOWN
    assert "Sultan, Farley and Lehmann (1990)" in MARKDOWN
    assert "2018 to 2025" in MARKDOWN


def test_launch_years_registered_as_assumptions():
    years = PROTOCOL["priors"]["bass_launch_year"]
    assert years["India"] == {**years["India"], "year": 2019, "basis": "assumption"}
    assert years["Pakistan"] == {
        **years["Pakistan"],
        "year": 2023,
        "basis": "assumption",
    }
    assert "India 2019" in MARKDOWN and "Pakistan 2023" in MARKDOWN


def test_intent_values_and_pakistan_missing():
    primary = PROTOCOL["intent_sources"]["primary"]
    assert primary["doi"] == "10.3389/fsufs.2019.00011"
    for country in ("USA", "India"):
        values = primary["values"][country]
        assert _percent(values["plant_based_very_or_extremely_likely"]) in MARKDOWN
        assert f"{values['plant_based_mean_1_to_5']:.2f}" in MARKDOWN
    assert primary["values"]["USA"]["plant_based_very_or_extremely_likely"] == 0.329
    assert primary["values"]["India"]["plant_based_very_or_extremely_likely"] == 0.628
    pakistan = PROTOCOL["intent_sources"]["Pakistan"]
    assert pakistan["value"] is None and pakistan["status"] == "missing"
    assert pakistan["treatment"] == "CONDITIONAL_TRANSFER"
    assert "CONDITIONAL_TRANSFER" in MARKDOWN


def test_calibration_and_mpce_rulings():
    formula = PROTOCOL["us_calibration"]["conversion"]
    assert (
        formula == "conversion = min(1, penetration / addressable_share) / intent_share"
    )
    assert formula in MARKDOWN
    assert "divided by household size" in PROTOCOL["household_tables"]["Pakistan_mpce"]
    assert "divided by household size" in MARKDOWN


def test_metrics_rendered():
    stats = PROTOCOL["metrics"]["validation"]["statistics"]
    for name in stats:
        assert f"`{name}`" in MARKDOWN
    assert PROTOCOL["metrics"]["simulation"]["draws"] == 10000


def test_registration_receipt_matches_protocol():
    receipt = json.loads((HERE / "logs" / "registration-receipt.json").read_text())
    digest = hashlib.sha256((HERE / "protocol.json").read_bytes()).hexdigest()
    assert receipt["protocol_sha256"] == digest
    assert receipt["registered_at_utc"] == PROTOCOL["registered_at_utc"]


def _check_authored_punctuation(root: Path) -> None:
    """Check research text while excluding hidden local tooling state."""
    for path in sorted(root.rglob("*")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix in {".md", ".json", ".py", ".csv"}:
            if path == root / "elicitation" / "questionnaire-us.md":
                # R49 preserves the author's source bytes, including punctuation.
                assert hashlib.sha256(path.read_bytes()).hexdigest() == (
                    "000293004ca738d65b5e300a8de331abbc9d40876e6a40d2495e4532304ca9f0"
                )
                continue
            text = path.read_text()
            assert chr(0x2014) not in text and chr(0x2013) not in text, path


def test_no_long_dashes_in_household_demand_files():
    _check_authored_punctuation(HERE)


@pytest.mark.parametrize(
    "checkpoint", [".governor/checkpoint.md", "elicitation/.governor/checkpoint.md"]
)
def test_punctuation_scope_excludes_hidden_state_but_checks_authored_text(
    tmp_path: Path, checkpoint: str
) -> None:
    """Tool checkpoints are excluded without weakening authored-text checks."""
    hidden = tmp_path / checkpoint
    hidden.parent.mkdir(parents=True)
    hidden.write_text("Machine checkpoint " + chr(0x2014) + " retained unchanged.")
    authored = tmp_path / "REPORT.md"
    authored.write_text("Authored research uses a normal hyphen.")
    _check_authored_punctuation(tmp_path)
    authored.write_text("Authored research " + chr(0x2013) + " invalid punctuation.")
    with pytest.raises(AssertionError, match="REPORT.md"):
        _check_authored_punctuation(tmp_path)


def test_pakistan_transfer_distribution():
    pakistan = PROTOCOL["intent_sources"]["Pakistan"]
    usa = PROTOCOL["intent_sources"]["primary"]["values"]["USA"]
    india = PROTOCOL["intent_sources"]["primary"]["values"]["India"]
    dist = pakistan["distribution"]
    assert dist == {"type": "uniform", "low": 0.329, "high": 0.628}
    assert dist["low"] == usa["plant_based_very_or_extremely_likely"]
    assert dist["high"] == india["plant_based_very_or_extremely_likely"]
    assert "R13" in pakistan["distribution_rationale"]
    assert "uniform between 0.329 (USA) and 0.628 (India)" in MARKDOWN


def test_controller_rulings_r1_to_r14():
    assert "R1 to R14" in PROTOCOL["spec_source"]["controller_rulings"]
    assert "R1 to R14" in MARKDOWN and "R1 to R11" not in MARKDOWN
    for ruling in ("R12", "R13", "R14"):
        assert ruling in PROTOCOL["spec_source"]["rulings_added"]
        assert f"- {ruling}:" in MARKDOWN


def test_receipt_records_amendment_with_prior_entry():
    receipt = json.loads((HERE / "logs" / "registration-receipt.json").read_text())
    assert receipt["amended_at_utc"] == PROTOCOL["amended_at_utc"]
    prior = receipt["prior_entries"][0]
    assert prior["protocol_sha256"] == (
        "39c5237fe05a6bb79119bfc64334361723f15593bbb67a44aa4d804646f20d07"
    )
    assert prior["registered_at_utc"] == "2026-10-18T17:38:19Z"
    assert prior["commit"] == "c5ed171"
    assert receipt["amendment_before_any_estimate"] is True
