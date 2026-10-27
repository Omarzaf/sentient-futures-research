"""Simulator invariants, using only the labelled invented fixture."""

import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import simulate as sm
from elasticities import Elasticities


@pytest.fixture
def sim_inputs():
    """Read labelled synthetic aggregate rows and bootstrap draws."""
    source = Path(__file__).parents[1] / "synthetic/simulator/inputs.json"
    fixture = json.loads(source.read_text())
    point = fixture["point"]
    draws = pd.DataFrame(
        {k: np.array(fixture["draw_offsets"]) + v + 0.07 for k, v in point.items()}
    )
    el = Elasticities(
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
        draws=draws,
        level="national",
        country="India",
    )
    return sm.SimInputs(
        rows=pd.DataFrame(fixture["rows"]),
        elasticities={"India": el},
        status=fixture["status"],
        metadata={"us_intent": 0.329, "us_intent_n": 987},
    )


@pytest.fixture
def sim_inputs_huge_demand(sim_inputs):
    """Force all chicken displacement draws above a very small ceiling."""
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("meat"), "spend_us"] = 1e12
    return sim_inputs


@pytest.fixture
def sim_inputs_with_synthetic_prices(sim_inputs):
    """Taint enters through a row even if the top-level status is diagnostic."""
    sim_inputs.status = "DIAGNOSTIC"
    return sim_inputs


def test_seeded_and_ordered(sim_inputs):
    a = sm.simulate(sim_inputs, n=500)
    b = sm.simulate(sim_inputs, n=500)
    assert a.draws.equals(b.draws)
    q = a.quantiles
    assert (q.p10 <= q.p50).all() and (q.p50 <= q.p90).all()


def test_ceiling_binds(sim_inputs_huge_demand):
    r = sm.simulate(sim_inputs_huge_demand, n=200)
    assert r.ceiling_binding_share == 1.0


def test_rejects_wrong_price_basis(sim_inputs):
    sim_inputs.price_basis = "INR_2023_24"
    with pytest.raises(ValueError, match="USD_2025"):
        sm.simulate(sim_inputs, n=10)


def test_synthetic_inputs_mark_results(sim_inputs_with_synthetic_prices):
    assert sm.simulate(sim_inputs_with_synthetic_prices, n=10).status == "SYNTHETIC"


def test_row_price_basis_is_checked(sim_inputs):
    sim_inputs.rows.loc[0, "price_basis"] = "PKR_2025"
    with pytest.raises(ValueError, match="USD_2025"):
        sm.simulate(sim_inputs, n=10)


def test_joint_recentering_and_positive_own_price_cap(sim_inputs):
    parameters = sm.map_unit_parameters(
        sim_inputs, np.full((1, len(sm.parameter_columns(sim_inputs))), 0.5)
    )
    result = sm.evaluate(sim_inputs, parameters)
    pair = result.pair_draws.set_index("pair")
    assert pair.loc["meat", "price_elasticity"] == pytest.approx(-0.6)
    assert pair.loc["meat", "income_elasticity"] == pytest.approx(0.3)
    assert pair.loc["dairy", "price_elasticity"] == 0
    assert result.metadata["positive_own_price_capped"] > 0


def test_ceiling_only_caps_meat_value_and_volume(sim_inputs_huge_demand):
    result = sm.simulate(sim_inputs_huge_demand, n=10)
    meat = result.pair_draws[result.pair_draws.pair.eq("meat")]
    assert np.allclose(meat.volume_t, meat.population * 2 / 1000)
    assert np.allclose(meat.value_usd_2025, meat.volume_t * 1000 * 10)
    assert (result.pair_draws.adopt_share <= 1).all()
    assert not result.pair_draws.loc[
        result.pair_draws.pair.ne("meat"), "ceiling_binding"
    ].any()


def test_missing_component_is_not_silently_omitted(sim_inputs):
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("vegetarian"), "ratio"] = np.nan
    result = sm.simulate(sim_inputs, n=10)
    assert result.draws.value_usd_2025.isna().all()
    assert result.draws.available_value_usd_2025.notna().all()
    assert result.draws.residual_usd_2025.isna().all()
    assert result.draws.total_with_residual_usd_2025.isna().all()


def test_residual_is_separate(sim_inputs):
    base = sm.simulate(sim_inputs, n=10)
    sim_inputs.rows["residual_usd_2025"] = 123
    result = sm.simulate(sim_inputs, n=10)
    assert np.allclose(base.draws.value_usd_2025, result.draws.value_usd_2025)
    assert np.allclose(
        result.draws.total_with_residual_usd_2025, result.draws.value_usd_2025 + 123
    )


def test_vegetarian_signed_sensitivity_uses_same_draws(sim_inputs):
    base = sm.simulate(sim_inputs, n=10)
    sim_inputs.vegetarian_mapping = "literal_signed"
    literal = sm.simulate(sim_inputs, n=10)
    a = base.pair_draws.query("pair == 'vegetarian'")
    b = literal.pair_draws.query("pair == 'vegetarian'")
    assert np.allclose(a.price_elasticity, -b.price_elasticity)
    assert np.allclose(
        base.pair_draws.query("pair != 'vegetarian'").value_usd_2025,
        literal.pair_draws.query("pair != 'vegetarian'").value_usd_2025,
    )


def test_deterministic_adapter_and_monte_carlo_use_same_evaluator(sim_inputs):
    p = sm.sample_parameters(sim_inputs, n=10)
    assert sm.evaluate(sim_inputs, p).draws.equals(sm.simulate(sim_inputs, n=10).draws)
    before = deepcopy(sim_inputs.rows)
    sm.evaluate(sim_inputs, p)
    pd.testing.assert_frame_equal(sim_inputs.rows, before)


def test_synthetic_write_guard(sim_inputs, tmp_path):
    result = sm.simulate(sim_inputs, n=10)
    with pytest.raises(ValueError, match="synthetic"):
        sm.write_result(result, sm.HERE / "outputs/test-must-not-exist.json")
    sm.write_result(result, tmp_path / "result.json")
    saved = json.loads((tmp_path / "result.json").read_text())
    assert saved["status"] == "SYNTHETIC"
    assert "NaN" not in (tmp_path / "result.json").read_text()


def test_missing_bootstrap_coefficient_stays_missing(sim_inputs):
    sim_inputs.elasticities["India"].draws["own_price:chicken"] = np.nan
    assert sm.simulate(sim_inputs, n=10).draws.value_usd_2025.isna().all()


def test_ancestor_input_taint_propagates(sim_inputs):
    sim_inputs.status = "DIAGNOSTIC"
    sim_inputs.rows["status"] = "DIAGNOSTIC"
    sim_inputs.source_statuses["calibration"] = "SYNTHETIC"
    assert sm.simulate(sim_inputs, n=10).status == "SYNTHETIC"


def test_fixed_bass_factor_has_exactly_zero_effect(sim_inputs):
    matrix = np.full((2, len(sm.parameter_columns(sim_inputs))), 0.5)
    matrix[0, sm.parameter_columns(sim_inputs).index("India:bass_p")] = 0
    matrix[1, sm.parameter_columns(sim_inputs).index("India:bass_p")] = 1
    result = sm.evaluate(sim_inputs, sm.map_unit_parameters(sim_inputs, matrix))
    assert result.draws.value_usd_2025.iloc[0] == result.draws.value_usd_2025.iloc[1]


def test_us_conversion_shared_and_india_intent_sampled(sim_inputs):
    matrix = np.full((2, len(sm.parameter_columns(sim_inputs))), 0.5)
    matrix[0, 0], matrix[1, 0] = 0.1, 0.9
    result = sm.evaluate(sim_inputs, sm.map_unit_parameters(sim_inputs, matrix))
    pair = result.pair_draws
    for group in ("meat", "vegetarian"):
        values = pair[pair.pair.eq(group)].value_usd_2025
        assert values.iloc[0] > values.iloc[1]
    dairy = pair[pair.pair.eq("dairy")].value_usd_2025
    assert dairy.iloc[0] == dairy.iloc[1]


def test_missing_price_does_not_bypass_chicken_ceiling(sim_inputs):
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("meat"), "price_usd_2025_kg"] = np.nan
    result = sm.simulate(sim_inputs, n=10)
    assert result.draws.value_usd_2025.isna().all()
    assert result.draws.volume_t.isna().all()


def test_missing_vegetarian_coefficient_is_not_renormalized(sim_inputs):
    del sim_inputs.elasticities["India"].cross_price[("chicken", "pulses")]
    result = sm.simulate(sim_inputs, n=10)
    assert (
        result.pair_draws.loc[result.pair_draws.pair.eq("vegetarian"), "value_usd_2025"]
        .isna()
        .all()
    )


def test_invalid_unit_cube_and_draw_count_rejected(sim_inputs):
    with pytest.raises(ValueError):
        sm.map_unit_parameters(
            sim_inputs, np.full((2, len(sm.parameter_columns(sim_inputs))), 1.1)
        )
    with pytest.raises(ValueError):
        sm.simulate(sim_inputs, n=0)


def test_beta_transform_preserves_registered_mean_and_sample_precision():
    """The deterministic inverse CDF agrees with a symmetric Beta's known median."""
    x, cdf = sm._beta_grid(0.5, 1000)
    assert np.interp(0.5, cdf, x) == pytest.approx(0.5, abs=1e-8)
    q = sm._intent(0.628, 1024, np.array([0.1, 0.5, 0.9]))
    assert 0.60 < q[0] < q[1] < q[2] < 0.66


def test_diagnostic_ancestor_cannot_be_promoted(sim_inputs):
    sim_inputs.status = "ACCEPTED"
    sim_inputs.rows["status"] = "ACCEPTED"
    sim_inputs.source_statuses["calibration"] = "DIAGNOSTIC"
    assert sm.simulate(sim_inputs, n=10).status == "DIAGNOSTIC"


def test_placeholder_variance_remains_diagnostic(sim_inputs):
    sim_inputs.status = "ACCEPTED"
    sim_inputs.rows["status"] = "ACCEPTED"
    sim_inputs.elasticities["India"].variance_strata_placeholder = True
    assert sm.simulate(sim_inputs, n=10).status == "DIAGNOSTIC"


def test_unknown_ancestor_status_rejected(sim_inputs):
    sim_inputs.source_statuses["calibration"] = "UNKNOWN"
    with pytest.raises(ValueError, match="status"):
        sm.simulate(sim_inputs, n=10)


def test_omitted_pair_cannot_be_reported_as_total(sim_inputs):
    sim_inputs.rows = sim_inputs.rows[sim_inputs.rows.pair.ne("vegetarian")]
    with pytest.raises(ValueError, match="segment-product pairs"):
        sm.simulate(sim_inputs, n=10)


def test_zero_price_response_does_not_erase_missing_ratio(sim_inputs):
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("dairy"), "ratio"] = np.nan
    result = sm.simulate(sim_inputs, n=10)
    assert (
        result.pair_draws.loc[result.pair_draws.pair.eq("dairy"), "value_usd_2025"]
        .isna()
        .all()
    )
    assert result.draws.value_usd_2025.isna().all()


def test_infinite_monetary_input_rejected(sim_inputs):
    sim_inputs.rows["spend_us"] = sim_inputs.rows.spend_us.astype(float)
    sim_inputs.rows.loc[0, "spend_us"] = np.inf
    with pytest.raises(ValueError, match="finite"):
        sm.simulate(sim_inputs, n=10)


def test_component_taint_does_not_taint_unrelated_dairy_component(sim_inputs):
    sim_inputs.status = "DIAGNOSTIC"
    sim_inputs.rows["status"] = "DIAGNOSTIC"
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("meat"), "status"] = "SYNTHETIC"
    result = sm.simulate(sim_inputs, n=10)
    assert result.status == "SYNTHETIC"
    assert (
        result.pair_draws.loc[result.pair_draws.pair.eq("dairy"), "status"]
        .eq("DIAGNOSTIC")
        .all()
    )


def test_missing_launch_year_does_not_become_zero_adoption(sim_inputs):
    sim_inputs.rows.loc[sim_inputs.rows.pair.eq("meat"), "launch_year"] = np.nan
    result = sm.simulate(sim_inputs, n=10)
    assert result.draws.value_usd_2025.isna().all()


@pytest.mark.parametrize("coefficient", ["own_price:chicken", "income:chicken"])
def test_unit_ratio_cannot_erase_missing_coefficient(sim_inputs, coefficient):
    """A neutral price/income ratio cannot silently replace an absent response."""
    meat = sim_inputs.rows.pair.eq("meat")
    sim_inputs.rows.loc[meat, "ratio"] = sim_inputs.rows.loc[meat, "ratio_us"]
    for band in ("low", "mid", "high"):
        sim_inputs.rows.loc[meat, f"income_{band}"] = sim_inputs.rows.loc[
            meat, "income_us"
        ]
    sim_inputs.elasticities["India"].draws[coefficient] = np.nan
    result = sm.simulate(sim_inputs, n=10)
    assert result.draws.value_usd_2025.isna().all()
    assert (
        result.pair_draws.loc[result.pair_draws.pair.eq("meat"), "value_usd_2025"]
        .isna()
        .all()
    )


@pytest.mark.parametrize("missing", ["ratio_us", "income_us", "income_mid"])
def test_zero_response_preserves_missing_reference_inputs(sim_inputs, missing):
    """Zero elasticities cannot turn missing relative-price or income bases into one."""
    dairy = sim_inputs.rows.pair.eq("dairy")
    sim_inputs.rows.loc[dairy, missing] = np.nan
    sim_inputs.elasticities["India"].income["milk"] = 0.0
    sim_inputs.elasticities["India"].draws["income:milk"] = 0.0
    result = sm.simulate(sim_inputs, n=10)
    assert result.draws.value_usd_2025.isna().all()
    assert (
        result.pair_draws.loc[result.pair_draws.pair.eq("dairy"), "value_usd_2025"]
        .isna()
        .all()
    )
