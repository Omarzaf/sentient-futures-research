"""Validate independent-forecast parsing, isolation and durable queue behavior."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "elicit", Path(__file__).resolve().parents[1] / "elicitation/elicit.py"
)
el = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(el)


@pytest.fixture(autouse=True)
def mock_authorized_models(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permit both mock providers in isolated local tests; never change live scope."""
    monkeypatch.setattr(
        el,
        "execution_scope",
        lambda: {"authorized_models": list(el.MODELS), "deferred_models": []},
    )


def answer() -> dict:
    """Return a new authored parser fixture, never a real model observation."""
    return el.parse_response(el.example("valid"))


def test_rejects_non_monotone_quantiles() -> None:
    assert "quantiles not ordered for 2030" in el.validate(
        el.parse_response(el.example("non_monotone")), "india"
    )


def test_rejects_missing_year() -> None:
    assert "missing year 2035" in el.validate(
        el.parse_response(el.example("missing_2035")), "india"
    )


def test_rejects_blocked_source() -> None:
    assert "blocked source pakistan-india-protein.vercel.app" in el.validate(
        el.parse_response(el.example("cites_vercel")), "pakistan"
    )


@pytest.mark.parametrize("region,fixture", [("india", "valid"), ("us", "us_valid")])
def test_complete_response(region: str, fixture: str) -> None:
    assert el.validate(el.parse_response(el.example(fixture)), region) == []


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), True, "12", -1])
def test_rejects_invalid_numeric_values(bad: object) -> None:
    parsed = answer()
    parsed["headline"]["2030"]["p50"] = bad
    assert el.validate(parsed, "india")


def test_fenced_json_and_duplicate_keys() -> None:
    assert (
        el.parse_response("Rationale\n```json\n" + el.example("valid") + "\n```")[
            "region"
        ]
        == "india"
    )
    with pytest.raises(ValueError, match="duplicate"):
        el.parse_response('{"headline":{},"headline":{}}')
    with pytest.raises(ValueError, match="exactly one"):
        el.parse_response(
            "```json\n"
            + el.example("valid")
            + "\n```\n```json\n"
            + el.example("valid")
            + "\n```"
        )


def test_source_contamination_outside_json_is_rejected() -> None:
    text = (
        "I read https://GITHUB.com/%4Fmarzaf/project\n```json\n"
        + el.example("valid")
        + "\n```"
    )
    assert "blocked source github.com/Omarzaf" in el.validate(
        el.parse_response(text), "india"
    )
    assert not el.blocked_sources("https://github.com/Omarzafoo/project")


def test_missing_fields_and_category_arithmetic() -> None:
    parsed = answer()
    parsed["categories"]["residual"]["2030"]["p50"] = 2
    parsed["sources"] = []
    del parsed["inputs"]["bass_p"]
    errors = el.validate(parsed, "india")
    assert "category medians do not sum for 2030" in errors
    assert "missing sources" in errors
    assert "invalid quantiles for inputs.bass_p" in errors


def test_conversion_multiplier_may_exceed_one_and_null_parity_is_not_zero() -> None:
    parsed = answer()
    parsed["inputs"]["conversion"] = {"p10": 1.1, "p50": 1.2, "p90": 1.4}
    assert not el.validate(parsed, "india")
    parsed["inputs"]["price_parity_year"] = {"p10": 0, "p50": 0, "p90": 0}
    assert el.validate(parsed, "india")


def test_cultivated_sale_and_parity_consistency() -> None:
    parsed = answer()
    parsed["cultivated_sale_by_2035"] = True
    assert "invalid cultivated first sale year" in el.validate(parsed, "india")
    parsed = answer()
    parsed["parity_status"] = "NEVER"
    parsed["parity_by_2050_probability"] = 0
    assert not el.validate(parsed, "india")


def test_us_requires_original_category_questions() -> None:
    parsed = el.parse_response(el.example("us_valid"))
    del parsed["categories"]["fermentation"]
    assert "missing categories.fermentation" in el.validate(parsed, "us")
    parsed["blind_spots"] = ""
    assert "missing blind_spots" in el.validate(parsed, "us")


def test_fixture_flag_never_accepted() -> None:
    parsed = answer()
    parsed["fixture_only"] = True
    assert "fixture output is not a model response" in el.validate(parsed, "india")


def test_evidence_boundary_and_legitimate_trade_code() -> None:
    provenance = json.loads((el.BASE / "source-provenance.json").read_text())
    for region in el.REGIONS:
        text = el.load_evidence(region)
        assert not el.blocked_sources(text)
        assert not re.search(r"(?<![\d,.])(?:106|241|668|1,945)(?![\d,.])", text)
        assert (
            hashlib.sha256(text.encode()).hexdigest()
            == provenance["evidence_hashes"][region]
        )
    assert "210610" in el.load_evidence("india")
    assert any(s["id"] == "comtrade-pakistan-2025" for s in provenance["sources"])


def test_exact_instrument_hash_and_prompt_preservation() -> None:
    if not (el.BASE / "questionnaire-us.md").exists():
        pytest.skip("private source instrument is intentionally not in Git")
    raw = (el.BASE / "questionnaire-us.md").read_bytes()
    assert len(raw) == 22419
    assert hashlib.sha256(raw).hexdigest() == el.US_HASH
    assert raw.decode() in el.build_prompt("us")
    for region in ("india", "pakistan"):
        text = (el.BASE / f"questionnaire-{region}.md").read_text()
        assert not re.search("[\u2013\u2014]", text)
        assert "UNRESOLVABLE_NOW" in text
        assert "HS 210610" in text


def test_cli_isolation_flags(tmp_path: Path) -> None:
    for model in el.MODELS:
        command = el.command(model, tmp_path, tmp_path / "answer")
        assert model in command
        assert not any("bypass" in c for c in command)
        assert "--resume" not in command
    codex = el.command(el.MODELS[1], tmp_path, tmp_path / "answer")
    assert "--ephemeral" in codex
    assert "--ignore-user-config" in codex
    assert "features.shell_tool=false" in codex
    assert "project_doc_max_bytes=0" in codex
    assert "memories.use_memories=false" in codex
    claude = el.command(el.MODELS[0], tmp_path, tmp_path / "answer")
    assert "--no-session-persistence" in claude
    assert "WebSearch,WebFetch" in claude


def test_provider_tool_audit(tmp_path: Path) -> None:
    target = tmp_path / "answer"
    target.write_text("answer")
    _, reported, violations = el.provider_output(
        el.MODELS[1],
        '{"type":"item.completed","item":{"type":"command_execution","command":"cat private"}}',
        target,
    )
    assert reported == []
    assert violations == ["disallowed tool observed: command_execution"]


def test_real_execution_failure_receipt_stops_queue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(el, "build_prompt", lambda region: f"isolated test {region}")
    monkeypatch.setattr(el, "instrument_hashes", lambda region: {})
    calls = []

    def fail_command(*args: object, **kwargs: object) -> object:
        """Return a provider-shaped capacity failure without any network request."""
        import subprocess

        calls.append(args)
        return subprocess.CompletedProcess(
            args, 1, '{"result":"You have hit your weekly limit, resets tomorrow"}', ""
        )

    monkeypatch.setattr(el.subprocess, "run", fail_command)
    raw, out = tmp_path / "raw", tmp_path / "out"
    el.run_all([el.MODELS[0]], ["india", "pakistan", "us"], raw_dir=raw, output_dir=out)
    assert len(calls) == 1
    completion = json.loads((out / "completion.json").read_text())
    assert completion["accepted"] == 0
    assert completion["pending"] == 60
    assert completion["selected_pending"] == 30
    assert completion["model_holds"] == {el.MODELS[0]: "PROVIDER_LIMIT"}
    receipt = json.loads(next(raw.glob("*/receipt.json")).read_text())
    assert receipt["quarantined"] is True
    assert receipt["stdout_sha256"]
    el.run_all([el.MODELS[0]], ["india"], raw_dir=raw, output_dir=out)
    assert len(calls) == 1


def test_genuine_acceptance_summary_and_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(el, "build_prompt", lambda region: f"isolated test {region}")
    monkeypatch.setattr(el, "instrument_hashes", lambda region: {})
    calls = []

    def model_answer(*args: object, **kwargs: object) -> object:
        """Supply authored fixture bytes through a mocked provider in temporary output."""
        import subprocess

        calls.append(args)
        return subprocess.CompletedProcess(
            args,
            0,
            json.dumps(
                {"result": el.example("valid"), "modelUsage": {el.MODELS[0]: {}}}
            ),
            "",
        )

    monkeypatch.setattr(el.subprocess, "run", model_answer)
    raw, out = tmp_path / "raw", tmp_path / "out"
    el.run_all([el.MODELS[0]], ["india"], runs=2, raw_dir=raw, output_dir=out)
    assert len(calls) == 2
    el.run_all([el.MODELS[0]], ["india"], runs=2, raw_dir=raw, output_dir=out)
    assert len(calls) == 2
    completion = json.loads((out / "completion.json").read_text())
    assert completion["accepted"] == 2
    assert completion["status"] == "INCOMPLETE"
    records = json.loads((out / "accepted-runs.json").read_text())["records"]
    assert len(records) == 2
    assert records[0]["inputs"]["price_parity_year"] is None
    assert "inputs.price_parity_year" not in (out / "results.csv").read_text()
    receipt_path = next(raw.glob("*/answer.txt"))
    receipt_path.write_text("tampered")
    with pytest.raises(ValueError, match="hash drift"):
        el.run_all([el.MODELS[0]], ["india"], runs=2, raw_dir=raw, output_dir=out)


def test_bounded_rejection_retries_and_outside_git(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(el, "build_prompt", lambda region: "test")
    monkeypatch.setattr(el, "instrument_hashes", lambda region: {})
    calls = []

    def invalid(*args: object, **kwargs: object) -> object:
        """Return malformed text to exercise the genuine retry state machine."""
        import subprocess

        calls.append(args)
        return subprocess.CompletedProcess(
            args, 0, json.dumps({"result": "invalid"}), ""
        )

    monkeypatch.setattr(el.subprocess, "run", invalid)
    raw, out = tmp_path / "raw", tmp_path / "out"
    el.run_all(
        [el.MODELS[0]], ["india"], runs=1, max_attempts=2, raw_dir=raw, output_dir=out
    )
    assert len(calls) == 2
    assert (
        json.loads((out / "completion.json").read_text())["slots"][0]["status"]
        == "RETRY_EXHAUSTED"
    )
    with pytest.raises(ValueError, match="outside"):
        el.run_all([el.MODELS[0]], ["india"], raw_dir=el.BASE / "raw")


def test_malformed_urls_and_boolean_parity_do_not_pass() -> None:
    parsed = answer()
    parsed["sources"] = ["https://[broken"]
    assert "invalid source URL" in el.validate(parsed, "india")
    parsed = answer()
    parsed["parity_status"] = "NEVER"
    parsed["parity_by_2050_probability"] = False
    assert "null parity requires NEVER/0 or UNKNOWN/null" in el.validate(
        parsed, "india"
    )


def test_completion_checkpoint_precedes_next_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(el, "build_prompt", lambda region: "test")
    monkeypatch.setattr(el, "instrument_hashes", lambda region: {})
    raw, out = tmp_path / "raw", tmp_path / "out"
    calls = []

    def interrupted(*args: object, **kwargs: object) -> object:
        """Interrupt after one accepted mocked answer to test durable state."""
        import subprocess

        if calls:
            assert json.loads((out / "completion.json").read_text())["accepted"] == 1
            raise KeyboardInterrupt
        calls.append(args)
        return subprocess.CompletedProcess(
            args, 0, json.dumps({"result": el.example("valid")}), ""
        )

    monkeypatch.setattr(el.subprocess, "run", interrupted)
    with pytest.raises(KeyboardInterrupt):
        el.run_all([el.MODELS[0]], ["india"], runs=2, raw_dir=raw, output_dir=out)
    assert json.loads((out / "completion.json").read_text())["accepted"] == 1


def test_deferred_model_cannot_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        el,
        "execution_scope",
        lambda: {
            "authorized_models": [el.MODELS[1]],
            "deferred_models": [el.MODELS[0]],
        },
    )
    with pytest.raises(ValueError, match="deferred"):
        el.run_all([el.MODELS[0]], ["us"], raw_dir=tmp_path / "raw")


def test_codex_nested_warning_with_completed_turn_is_success() -> None:
    events = [
        {"type": "thread.started", "thread_id": "test-thread"},
        {
            "type": "item.completed",
            "item": {
                "id": "item_0",
                "type": "error",
                "message": "Under-development features enabled: skip_host_skill_discovery. Under-development features are incomplete and may behave unpredictably.",
            },
        },
        {"type": "turn.started"},
        {
            "type": "item.completed",
            "item": {"type": "web_search", "query": "public source"},
        },
        {"type": "item.completed", "item": {"type": "agent_message", "text": "answer"}},
        {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 5}},
    ]
    stdout = "\n".join(json.dumps(event) for event in events)
    failed, warnings = el.provider_status(el.MODELS[1], stdout, 0)
    assert failed is False
    assert len(warnings) == 1
    assert "skip_host_skill_discovery" in warnings[0]
    assert el.provider_status(el.MODELS[1], stdout, 1)[0] is True
    assert (
        el.provider_status(
            el.MODELS[1],
            stdout + '\n{"type":"turn.failed","error":{"message":"quota"}}',
            0,
        )[0]
        is True
    )
    assert (
        el.provider_status(el.MODELS[1], '{"type":"error","message":"quota"}', 0)[0]
        is True
    )
    assert el.provider_status(el.MODELS[1], '{"type":"turn.started"}', 0)[0] is True
