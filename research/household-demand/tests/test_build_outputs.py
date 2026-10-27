"""Publication gates, scope alignment and genuine panel rerun mapping."""

import json
from pathlib import Path

import build_outputs as bo
import numpy as np
import pandas as pd
import pytest


def test_comparison_has_four_methods_per_cell():
    table = bo.comparison_table()
    assert table.groupby(["country", "year"]).method.nunique().eq(4).all()
    assert set(table.year) == {2026, 2030, 2035}
    assert set(table.unit) == {"million USD, 2025 prices"}


def test_placeholder_market_never_becomes_public_by_renaming():
    table = bo.comparison_table()
    held = table[(table.country == "Pakistan") & (table.method == "household_model")]
    assert held[["p10", "p50", "p90"]].isna().all().all()
    assert held.withheld_reason.str.contains("placeholder").all()
    assert not table.status.eq("SYNTHETIC").any()
    assert bo.claim_rows(table).empty


def test_scope_mismatch_does_not_make_numeric_gap_or_residual():
    table = bo.comparison_table()
    assert table.gap_to_household_p50.isna().all()
    assert table.residual_p50.isna().all()
    assert table.total_with_residual_p50.isna().all()
    assert (
        table.loc[table.method.eq("gfi_proxy"), "scope_alignment"].eq("UNMATCHED").all()
    )


@pytest.mark.parametrize(
    "status",
    [
        "DIAGNOSTIC",
        "CONDITIONAL_TRANSFER",
        "COMPLETE_PANEL",
        "PARTIAL_PANEL",
        "SYNTHETIC",
        "UNKNOWN",
    ],
)
def test_claims_require_positive_acceptance(status):
    row = {
        "status": status,
        "review_status": "HUMAN_REVIEWED",
        "review_id": "review-1",
        "source_ids": '["source-1"]',
        "source_sha256": "a" * 64,
        "p50": 1.0,
    }
    assert bo.claim_rows(pd.DataFrame([row])).empty


def test_claims_require_review_and_bound_source_even_when_accepted():
    row = {
        "status": "ACCEPTED",
        "review_status": "HUMAN_REVIEWED",
        "review_id": "review-1",
        "source_ids": '["source-1"]',
        "source_sha256": "a" * 64,
        "p50": 1.0,
    }
    assert len(bo.claim_rows(pd.DataFrame([row]))) == 1
    for key in ("review_status", "review_id", "source_ids", "source_sha256", "p50"):
        assert bo.claim_rows(pd.DataFrame([{**row, key: None}])).empty


def test_proxy_selects_scenarios_exact_year_quantity_and_statistic():
    table = pd.DataFrame(
        [
            {
                "record_type": "scenario",
                "quantity": "market_value",
                "country": "India",
                "year": 2030,
                "statistic": q,
                "value": v,
                "source_ids": "[]",
            }
            for q, v in zip(bo.QUANTILES, [1, 2, 3])
        ]
    )
    extra = table.assign(record_type="sensitivity", value=999)
    assert bo.proxy_quantiles(pd.concat([table, extra]), "India", 2030)["p50"] == 2
    assert bo.proxy_quantiles(table, "India", 2035)["p50"] is None
    with pytest.raises(ValueError, match="duplicate"):
        bo.proxy_quantiles(pd.concat([table, table]), "India", 2030)


def test_csv_rounding_and_missingness_are_explicit(tmp_path):
    target = tmp_path / "table.csv"
    bo.write_csv(pd.DataFrame({"p50": [1.23456789, np.nan, -0.0000012]}), target)
    assert target.read_text() == 'p50\n1.234568\n""\n-0.000001\n'
    assert pd.read_csv(target).p50.isna().sum() == 1


def test_partial_panel_stays_partial_and_separate_by_model():
    records = []
    for model, count, value in [(bo.MODELS[0], 3, 1), (bo.MODELS[1], 10, 9)]:
        records.append(
            {
                "region": "India",
                "model": model,
                "measure": "headline",
                "year": 2030,
                "unit": bo.UNIT,
                "n_accepted": count,
                "p10": value,
                "p50": value,
                "p90": value,
                "status": "COMPLETE_PANEL",
            }
        )
    table = bo.comparison_table(panel=pd.DataFrame(records))
    rows = table[
        (table.method == "panel_headline")
        & (table.country == "India")
        & (table.year == 2030)
    ]
    assert dict(zip(rows.source_model, rows.status)) == {
        bo.MODELS[0]: "PARTIAL_PANEL",
        bo.MODELS[1]: "COMPLETE_PANEL",
    }
    assert sorted(rows.p50.tolist()) == [1, 9]


def test_panel_wrong_units_are_held():
    panel = pd.DataFrame(
        [
            {
                "region": "India",
                "model": bo.MODELS[0],
                "measure": "headline",
                "year": 2030,
                "unit": "billion USD",
                "n_accepted": 10,
                "p10": 1,
                "p50": 2,
                "p90": 3,
                "status": "COMPLETE_PANEL",
            }
        ]
    )
    table = bo.comparison_table(panel=panel)
    row = table[
        (table.method == "panel_headline")
        & (table.source_model == bo.MODELS[0])
        & (table.country == "India")
        & (table.year == 2030)
    ].iloc[0]
    assert pd.isna(row.p50)
    assert "unit" in row.withheld_reason


def test_panel_mapping_uses_all_parameters_and_preserves_dairy_conversion():
    rows = pd.DataFrame(
        {
            "country": ["India"] * 3,
            "year": [2030] * 3,
            "pair": ["meat", "vegetarian", "dairy"],
            "conversion": [0.6, 0.6, 1.0],
            "bass_p": [0.03] * 3,
            "bass_q": [0.38] * 3,
        }
    )
    inputs = bo.sm.SimInputs(rows, {}, metadata={})
    mapped = bo.panel_inputs(
        inputs,
        {
            "conversion": 0.2,
            "bass_p": 0.04,
            "bass_q": 0.5,
            "price_parity_year": 2031,
            "ai_cost_decline": 0.02,
        },
    )
    assert mapped.rows.conversion.tolist() == [0.2, 0.2, 1.0]
    assert mapped.rows.bass_p.eq(0.04).all() and mapped.rows.bass_q.eq(0.5).all()
    assert mapped.parity_year == 2031 and mapped.ai_decline == 0.02
    assert inputs.rows.conversion.tolist() == [0.6, 0.6, 1.0]
    with pytest.raises(ValueError, match="missing"):
        bo.panel_inputs(inputs, {"conversion": 0.2})


def test_panel_rerun_missing_input_never_calls_simulator(monkeypatch):
    monkeypatch.setattr(
        bo.sm, "simulate", lambda *_a, **_k: pytest.fail("must remain held")
    )
    assert bo.model_from_panel_inputs({}, pd.DataFrame(), n=10) == ({}, [])


def test_sobol_sidecar_records_fixed_factors_and_rounding():
    source = Path(__file__).parents[1] / "outputs/sobol-diagnostics.json"
    if not source.exists():
        pytest.skip("actual production run has not executed yet")
    data = json.loads(source.read_text())
    assert data["csv_decimal_places"] == 6
    assert data["n_base"] == [8192, 16384]
    assert len(data["cells"]) == 3
    assert all("bass_p" in " ".join(c["fixed_factors"]) for c in data["cells"])
    assert all(c["convergence_certified"] is False for c in data["cells"])


@pytest.fixture
def genuine_boundary_inputs():
    """Reuse labelled aggregate fixture through the real shared evaluator."""
    source = Path(__file__).parents[1] / "synthetic/simulator/inputs.json"
    fixture = json.loads(source.read_text())
    point = fixture["point"]
    estimates = bo.sm.Elasticities(
        own_price={
            k.split(":")[1]: v for k, v in point.items() if k.startswith("own_price:")
        },
        income={
            k.split(":")[1]: v for k, v in point.items() if k.startswith("income:")
        },
        cross_price={
            tuple(k.split(":")[1:]): v
            for k, v in point.items()
            if k.startswith("cross_price:")
        },
        draws=pd.DataFrame(
            {k: np.array(fixture["draw_offsets"]) + v + 0.07 for k, v in point.items()}
        ),
        level="national",
        country="India",
    )
    return bo.sm.SimInputs(
        pd.concat(
            [pd.DataFrame(fixture["rows"]).assign(year=y) for y in bo.YEARS],
            ignore_index=True,
        ),
        {"India": estimates},
        metadata={"us_intent": 0.329, "us_intent_n": 987},
        status="SYNTHETIC",
    )


def panel_boundary_rows():
    """Use the elicitation writer's actual lowercase-region and unit schema."""
    return pd.DataFrame(
        [
            {
                "region": "india",
                "model": bo.MODELS[1],
                "measure": f"inputs.{key}",
                "year": np.nan,
                "unit": unit,
                "n_accepted": 10,
                "n_nonmissing": 10,
                "p10": value,
                "p50": value,
                "p90": value,
                "status": "COMPLETE_PANEL",
            }
            for key, value, unit in zip(
                bo.PARAMETERS,
                [0.2, 0.04, 0.5, 2031.5, 0.02],
                [
                    "coefficient",
                    "coefficient",
                    "coefficient",
                    "year",
                    "fraction per year",
                ],
            )
        ]
    )


def test_actual_elicitation_region_and_unit_schema_is_consumed():
    row = {
        "region": "india",
        "model": bo.MODELS[1],
        "measure": "headline",
        "year": 2030,
        "unit": "million USD_2025",
        "n_accepted": 10,
        "n_nonmissing": 10,
        "p10": 2,
        "p50": 3,
        "p90": 4,
        "status": "COMPLETE_PANEL",
    }
    table = bo.comparison_table(panel=pd.DataFrame([row]))
    selected = table[
        (table.country == "India")
        & (table.year == 2030)
        & (table.source_model == bo.MODELS[1])
        & (table.method == "panel_headline")
    ]
    assert selected.p50.iloc[0] == 3


def test_panel_medians_genuinely_rerun_evaluator(genuine_boundary_inputs):
    results, diagnostics = bo.model_from_panel_inputs(
        {"India": genuine_boundary_inputs}, panel_boundary_rows(), n=20
    )
    assert len(results) == 3
    mapped = bo.panel_inputs(
        genuine_boundary_inputs,
        dict(zip(bo.PARAMETERS, [0.2, 0.04, 0.5, 2031.5, 0.02])),
    )
    expected = bo.sm.simulate(mapped, n=20).quantiles
    for year in bo.YEARS:
        q = expected[
            (expected.year == year) & (expected.metric == "value_usd_2025")
        ].iloc[0]
        assert results[("India", year, bo.MODELS[1])]["p50"] == q.p50 / 1e6
        assert results[("India", year, bo.MODELS[1])]["status"] == "SYNTHETIC"
    assert diagnostics[1]["status"] == "COMPLETE_PANEL"


def test_panel_conversion_fixed_while_main_keeps_us_intent_uncertainty(
    genuine_boundary_inputs,
):
    cube = np.full((2, len(bo.sm.parameter_columns(genuine_boundary_inputs))), 0.5)
    cube[:, 0] = [0.1, 0.9]
    mapped = bo.panel_inputs(
        genuine_boundary_inputs, dict(zip(bo.PARAMETERS, [0.2, 0.04, 0.5, 2031, 0.02]))
    )
    result = bo.sm.evaluate(mapped, bo.sm.map_unit_parameters(mapped, cube))
    for _, rows in result.draws.groupby("year"):
        assert rows.value_usd_2025.nunique() == 1
    ordinary = bo.sm.evaluate(
        genuine_boundary_inputs,
        bo.sm.map_unit_parameters(genuine_boundary_inputs, cube),
    )
    assert ordinary.draws.groupby("year").value_usd_2025.nunique().eq(2).all()


@pytest.mark.parametrize(
    "mutation",
    [
        "conditional_parity",
        "historical_parity",
        "wrong_units",
        "wrong_year",
        "zero_bass",
        "ai_one",
    ],
)
def test_panel_unsupported_inputs_hold_without_inventing(
    genuine_boundary_inputs, monkeypatch, mutation
):
    panel = panel_boundary_rows()
    parity = panel.measure.eq("inputs.price_parity_year")
    if mutation == "conditional_parity":
        panel.loc[parity, "n_nonmissing"] = 9
    elif mutation == "historical_parity":
        panel.loc[parity, "p50"] = 2020
    elif mutation == "wrong_units":
        panel.loc[parity, "unit"] = "fraction"
    elif mutation == "zero_bass":
        panel.loc[panel.measure.eq("inputs.bass_p"), "p50"] = 0
    elif mutation == "ai_one":
        panel.loc[panel.measure.eq("inputs.ai_cost_decline"), "p50"] = 1
    else:
        panel.loc[parity, "year"] = 2030
    monkeypatch.setattr(
        bo.sm, "simulate", lambda *_a, **_k: pytest.fail("invalid inputs must not run")
    )
    results, diagnostics = bo.model_from_panel_inputs(
        {"India": genuine_boundary_inputs}, panel, n=20
    )
    assert not results
    assert all(d["status"] == "HELD_PANEL_INPUTS" for d in diagnostics)


def test_report_keeps_actual_us_packaged_crosswalk_hold_and_authored_dash_rule():
    """A planned crosswalk cannot be described as an implemented calibration."""
    root = Path(__file__).parents[1]
    calibration = json.loads((root / "outputs/us_calibration.json").read_text())
    assert (
        calibration["ce"]["addressable_rule"]["buys_packaged_food_r38"]["status"]
        == "NOT_DONE"
    )
    report = (root / "outputs/REPORT.md").read_text()
    assert "MISCFOOD" in report and "R40" in report
    assert "was narrowed to match" not in report
    assert "\u2013" not in report and "\u2014" not in report


def test_default_comparison_consumes_saved_reruns_but_supplied_panel_is_isolated(
    monkeypatch,
):
    """Default recomputation must include actual saved model-from-input results."""
    original = bo.read_json
    record = {
        "country": "India",
        "year": 2030,
        "model": bo.MODELS[1],
        "p10": 10.0,
        "p50": 11.0,
        "p90": 12.0,
        "status": "DIAGNOSTIC",
        "n_accepted": 10,
        "panel_coverage_status": "COMPLETE_PANEL",
        "source_sha256": "a" * 64,
    }

    def saved(path, default=None):
        """Replace only the summary boundary, leaving real source artifacts intact."""
        return (
            {"records": [record]}
            if path.name == "panel-model-summary.json"
            else original(path, default)
        )

    monkeypatch.setattr(bo, "read_json", saved)
    table = bo.comparison_table()
    rows = table[
        (table.method == "model_from_panel_inputs")
        & (table.country == "India")
        & (table.year == 2030)
        & (table.source_model == bo.MODELS[1])
    ]
    assert rows.p50.iloc[0] == 11.0
    isolated = bo.comparison_table(panel=pd.DataFrame())
    assert (
        isolated.loc[isolated.method.eq("model_from_panel_inputs"), "p50"].isna().all()
    )


@pytest.mark.parametrize("source_status", ["SYNTHETIC", "UNKNOWN", None, "DIAGNOSTIC"])
def test_panel_headline_rejects_untrusted_source_status(source_status):
    """Ten numeric responses cannot sanitize taint or a missing producer status."""
    panel = pd.DataFrame(
        [
            {
                "region": "india",
                "model": bo.MODELS[1],
                "measure": "headline",
                "year": 2030,
                "unit": "million USD_2025",
                "n_accepted": 10,
                "n_nonmissing": 10,
                "p10": 100.0,
                "p50": 200.0,
                "p90": 300.0,
                "status": source_status,
            }
        ]
    )
    for include_placeholder in (False, True):
        table = bo.comparison_table(
            panel=panel, include_placeholder=include_placeholder
        )
        row = table[
            (table.method == "panel_headline")
            & (table.country == "India")
            & (table.year == 2030)
            & (table.source_model == bo.MODELS[1])
        ].iloc[0]
        assert row[list(bo.QUANTILES)].isna().all()
        assert row.status.startswith("HELD")
        assert row.panel_coverage_status not in ("COMPLETE_PANEL", "PARTIAL_PANEL")


@pytest.mark.parametrize("source_status", ["SYNTHETIC", "UNKNOWN", None, "DIAGNOSTIC"])
def test_panel_input_status_rejected_before_real_diagnostic_rerun(
    genuine_boundary_inputs, source_status
):
    """One tainted parameter must not become an ordinary model derivative."""
    inputs = bo.replace(
        genuine_boundary_inputs,
        status="DIAGNOSTIC",
        rows=genuine_boundary_inputs.rows.assign(status="DIAGNOSTIC"),
    )
    panel = panel_boundary_rows()
    panel.loc[panel.measure.eq("inputs.conversion"), "status"] = source_status
    results, diagnostics = bo.model_from_panel_inputs({"India": inputs}, panel, n=20)
    assert not results
    diagnostic = next(d for d in diagnostics if d["model"] == bo.MODELS[1])
    assert diagnostic["status"].startswith("HELD")
    assert diagnostic["medians"] is None
    assert "source status" in diagnostic["reason"]


def test_explicit_partial_panel_never_upgrades_at_ten_runs(genuine_boundary_inputs):
    """Coverage can downgrade a producer label, but cannot remove its partial hold."""
    panel = panel_boundary_rows().assign(status="PARTIAL_PANEL")
    results, diagnostics = bo.model_from_panel_inputs(
        {"India": genuine_boundary_inputs}, panel, n=20
    )
    assert len(results) == 3
    assert all(r["panel_coverage_status"] == "PARTIAL_PANEL" for r in results.values())
    assert diagnostics[1]["status"] == "PARTIAL_PANEL"
    headline = pd.DataFrame(
        [
            {
                "region": "india",
                "model": bo.MODELS[1],
                "measure": "headline",
                "year": 2030,
                "unit": "million USD_2025",
                "n_accepted": 10,
                "n_nonmissing": 10,
                "p10": 1.0,
                "p50": 2.0,
                "p90": 3.0,
                "status": "PARTIAL_PANEL",
            }
        ]
    )
    table = bo.comparison_table(panel=headline)
    row = table[
        (table.method == "panel_headline")
        & (table.country == "India")
        & (table.year == 2030)
        & (table.source_model == bo.MODELS[1])
    ].iloc[0]
    assert row.status == "PARTIAL_PANEL"
    assert row.p50 == 2.0


def test_report_distinguishes_unretained_lookup_hashes_from_retained_bytes():
    """A recorded lookup digest cannot imply that source content was rechecked."""
    root = Path(__file__).parents[1]
    manifest = pd.read_csv(root / "inputs/manifest.csv")
    unstored = manifest.stored_at.str.startswith("not stored")
    report = (root / "outputs/REPORT.md").read_text()
    for source_id in manifest.loc[unstored, "input_id"]:
        row = next(
            line for line in report.splitlines() if line.startswith(f"| {source_id} |")
        )
        assert "HISTORICAL_LOOKUP_HASH_ONLY" in row
    assert f"{int((~unstored).sum())} retained" in report
    gfi_note = next(line for line in report.splitlines() if line.startswith("[^gfi]:"))
    assert "retained capture reviewed locally" not in gfi_note
    assert "contents were not reverified" in gfi_note


def us_panel_fixture(count=3):
    """Build source-bound US-only records with distinct original measures."""
    measures = ("headline", "categories.cultivated", "categories.fermentation")
    records = []
    for slot in range(1, count + 1):
        values = {
            measure: {
                str(year): {
                    "p10": 50.0,
                    "p50": float(100 * (i + 1) + slot),
                    "p90": 500.0,
                }
                for year in bo.YEARS
            }
            for i, measure in enumerate(measures)
        }
        records.append(
            {
                "region": "us",
                "model": bo.MODELS[1],
                "slot": slot,
                "attempt_id": f"test-slot-{slot}",
                "answer_sha256": f"{slot:064x}",
                "prompt_sha256": "b" * 64,
                "headline": values["headline"],
                "categories": {
                    "cultivated": values["categories.cultivated"],
                    "fermentation": values["categories.fermentation"],
                },
            }
        )
    rows = []
    for index, measure in enumerate(measures):
        qs = np.quantile(
            [100 * (index + 1) + slot for slot in range(1, count + 1)], [0.1, 0.5, 0.9]
        )
        for year in bo.YEARS:
            rows.append(
                {
                    "region": "us",
                    "model": bo.MODELS[1],
                    "measure": measure,
                    "year": year,
                    "unit": "million USD_2025",
                    "n_accepted": count,
                    "n_nonmissing": count,
                    **dict(zip(bo.QUANTILES, qs)),
                    "status": "COMPLETE_PANEL" if count == 10 else "PARTIAL_PANEL",
                }
            )
    return pd.DataFrame(rows), {"records": records}


def test_us_calibration_preserves_original_measures_years_scopes_and_hold():
    panel, accepted = us_panel_fixture()
    table = bo.us_calibration_table(
        panel=panel, accepted_runs=accepted, models=(bo.MODELS[1],)
    )
    assert len(table) == 9
    assert set(table.measure) == {
        "headline",
        "categories.cultivated",
        "categories.fermentation",
    }
    assert set(table.year) == set(bo.YEARS)
    assert set(table.status) == {"PARTIAL_PANEL"}
    assert table.n_accepted.eq(3).all() and table.n_nonmissing.eq(3).all()
    assert table.public_reporting.eq(
        "HELD_AUTHOR_NOTIFICATION_AND_SCHOLARLY_REVIEW"
    ).all()
    assert table.loc[table.measure.eq("headline"), "channel"].eq("retail").all()
    assert (
        table.loc[table.measure.ne("headline"), "channel"]
        .eq("retail and foodservice")
        .all()
    )
    assert (
        table.loc[table.measure.eq("categories.cultivated"), "scope"]
        .str.contains("pet food")
        .all()
    )
    assert (
        table.loc[table.measure.eq("categories.fermentation"), "scope"]
        .str.contains("long-established")
        .all()
    )
    assert not any("anna" in c or "error" in c for c in table.columns)
    assert set(bo.comparison_table().country) == {"India", "Pakistan"}
    assert len(table.attrs["accepted_record_bindings"][bo.MODELS[1]]) == 3


@pytest.mark.parametrize(
    "mutation",
    [
        "taint",
        "unknown",
        "unit",
        "year",
        "coverage",
        "record_mismatch",
        "missing_hash",
        "record_taint",
        "export_taint",
        "export_unknown",
        "export_null",
        "quantile_mismatch",
    ],
)
def test_us_calibration_holds_untrusted_or_unbound_summary(mutation):
    panel, accepted = us_panel_fixture()
    target = panel.measure.eq("headline") & panel.year.eq(2030)
    if mutation == "taint":
        panel.loc[target, "status"] = "SYNTHETIC"
    elif mutation == "unknown":
        panel.loc[target, "status"] = "UNKNOWN"
    elif mutation == "unit":
        panel.loc[target, "unit"] = "billion USD"
    elif mutation == "year":
        panel.loc[target, "year"] = 2031
    elif mutation == "coverage":
        panel.loc[target, "n_nonmissing"] = 2
    elif mutation == "record_mismatch":
        accepted["records"].pop()
    elif mutation == "missing_hash":
        accepted["records"][0]["answer_sha256"] = ""
    elif mutation == "record_taint":
        accepted["records"][0]["status"] = "SYNTHETIC"
    elif mutation.startswith("export_"):
        accepted["status"] = {
            "export_taint": "SYNTHETIC",
            "export_unknown": "UNKNOWN",
            "export_null": None,
        }[mutation]
    else:
        panel.loc[target, "p50"] = 9999.0
    table = bo.us_calibration_table(
        panel=panel, accepted_runs=accepted, models=(bo.MODELS[1],)
    )
    row = table[table.measure.eq("headline") & table.year.eq(2030)].iloc[0]
    assert row[list(bo.QUANTILES)].isna().all()
    assert row.status.startswith("HELD")
    assert row.withheld_reason


def test_us_explicit_partial_is_not_upgraded_and_missing_model_stays_null():
    panel, accepted = us_panel_fixture(10)
    panel["status"] = "PARTIAL_PANEL"
    table = bo.us_calibration_table(
        panel=panel, accepted_runs=accepted, models=bo.MODELS
    )
    assert (
        table.loc[table.source_model.eq(bo.MODELS[1]), "status"]
        .eq("PARTIAL_PANEL")
        .all()
    )
    assert (
        table.loc[table.source_model.eq(bo.MODELS[0]), list(bo.QUANTILES)]
        .isna()
        .all()
        .all()
    )
