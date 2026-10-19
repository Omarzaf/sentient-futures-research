"""State holdouts must use unseen-state predictions and preserve missing items."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import validate as va


@pytest.fixture
def india_fixture() -> pd.DataFrame:
    """Return a deterministic multi-state fixture with known spending."""
    state = np.repeat(np.arange(1, 6), 60)
    size = np.tile(np.repeat([2.0, 4.0, 6.0], 20), 5)
    urban = np.tile([1, 2], 150)
    per_capita = 50.0 * size**0.25 * np.exp(0.2 * (urban == 2))
    return pd.DataFrame(
        {
            "state": state,
            "hh_size": size,
            "sector": urban,
            "religion": np.tile([1, 2, 3], 100),
            "caste": np.tile([1, 2], 150),
            "multiplier": np.tile([1.0, 3.0, 2.0], 100),
            "value_month_chicken": per_capita * size,
            "currency": "INR",
            "psu": state * 1000 + np.tile(np.arange(60), 5),
            "district": 1,
            "stratum": 1,
            "stratum_status": "RESOLVED",
            "status": "SYNTHETIC",
        }
    )


def test_holdout_excludes_target_state(india_fixture, monkeypatch):
    """Preserve the plan's monkeypatch interface and exclude each target state."""
    seen = []
    monkeypatch.setattr(
        va, "_fit", lambda d, o: seen.append(set(d.state)) or (lambda x: x[o])
    )
    va.state_holdout(india_fixture, "value_month_chicken")
    assert all(len(s) == india_fixture.state.nunique() - 1 for s in seen)
    assert len(seen) == india_fixture.state.nunique()


def test_time_comparison_needs_registration(tmp_path):
    """Missing earlier rounds must retain the official registration boundary."""
    with pytest.raises(FileNotFoundError, match="microdata.gov.in"):
        va.time_comparison(None, None)


def test_known_data_accuracy_and_weighted_per_capita(india_fixture):
    """Recover a shared demographic spending law on genuinely heldout states."""
    result = va.state_holdout(india_fixture, "value_month_chicken")
    assert {"state", "observed", "predicted", "abs_error", "interval_hit"} <= set(
        result
    )
    assert result.abs_error.max() < 0.05
    group = india_fixture.loc[india_fixture.state.eq(1)]
    expected = np.sum(group.multiplier * group.value_month_chicken) / np.sum(
        group.multiplier * group.hh_size
    )
    assert result.loc[result.state.eq(1), "observed"].iloc[0] == pytest.approx(expected)


def test_heldout_outcome_and_derived_feature_perturbation(india_fixture):
    """Heldout spending, MPCE, unit values and segment labels cannot affect prediction."""
    base = india_fixture.assign(mpce_local=1000.0, unit_value_chicken=80.0, segment="a")
    first = va.state_holdout(base, "value_month_chicken").set_index("state").loc[1]
    changed = base.copy()
    heldout = changed.state.eq(1)
    changed.loc[heldout, "value_month_chicken"] *= 100
    changed.loc[heldout, "mpce_local"] *= 200
    changed.loc[heldout, "unit_value_chicken"] *= 500
    changed.loc[heldout, "segment"] = "changed"
    second = va.state_holdout(changed, "value_month_chicken").set_index("state").loc[1]
    for col in ["predicted", "lower_10", "upper_90"]:
        assert second[col] == pytest.approx(first[col])
    assert second.observed == pytest.approx(first.observed * 100)


def test_predictor_input_masks_outcomes(india_fixture, monkeypatch):
    """The holdout boundary provides demographics and an empty compatibility sentinel."""
    seen = []

    def fit(data, outcome):
        """Capture the frame supplied to each prediction callback."""

        def predict(frame):
            """Return a constant forecast, never a target-derived value."""
            seen.append(frame.copy())
            return pd.Series(100.0, index=frame.index)

        return predict

    monkeypatch.setattr(va, "_fit", fit)
    va.state_holdout(india_fixture.assign(mpce_local=900), "value_month_chicken")
    assert all(frame.value_month_chicken.isna().all() for frame in seen)
    assert all("mpce_local" not in frame for frame in seen)


def test_observed_target_never_calls_missing_groups_zero(india_fixture):
    """Keep absent and invalid group values missing while naming the observed subtotal."""
    data = india_fixture.iloc[:4].copy()
    data["value_month_milk"] = [40.0, np.nan, np.inf, -5.0]
    data.loc[data.index[1:], "value_month_chicken"] = np.nan
    target, metadata = va.observed_animal_target(data)
    assert target.iloc[0] == pytest.approx(data.value_month_chicken.iloc[0] + 40)
    assert target.iloc[1:].isna().all()
    assert metadata["complete_basket_households"] == 0
    assert metadata["target"] == "observed_item_animal_spending"
    assert metadata["whole_basket_identified"] is False


def test_small_cells_and_missing_outcomes_are_not_published(india_fixture):
    """Count each exclusion and suppress every scalar spending result below30 rows."""
    data = india_fixture.copy()
    data.loc[data.state.eq(1) & (data.index % 3 != 0), "value_month_chicken"] = np.nan
    result = va.state_holdout(data, "value_month_chicken").set_index("state")
    assert result.loc[1, "n_evaluated"] == 20
    assert result.loc[1, "n_missing_outcome"] == 40
    assert result.loc[1, "fold_status"] == "SUPPRESSED_SMALL_CELL"
    assert (
        result.loc[1, ["observed", "predicted", "abs_error", "lower_10", "upper_90"]]
        .isna()
        .all()
    )
    metrics = va.summary(result.reset_index())
    assert metrics["states_evaluated"] == 4
    assert metrics["states_suppressed"] == 1


def test_invalid_weights_sizes_outcomes_excluded(india_fixture):
    """Nonfinite or nonpositive design inputs cannot silently propagate into metrics."""
    data = india_fixture.copy()
    data.loc[0, "multiplier"] = np.inf
    data.loc[1, "hh_size"] = 0
    data.loc[2, "value_month_chicken"] = -1
    data.loc[3, "value_month_chicken"] = np.inf
    result = va.state_holdout(data, "value_month_chicken").set_index("state")
    assert result.loc[1, "n_evaluated"] == 56
    assert np.isfinite(result[["observed", "predicted", "abs_error"]]).all().all()


def test_actual_intervals_use_nested_state_errors(india_fixture):
    """Unseen geographic variation creates predictive spread without target leakage."""
    data = india_fixture.copy()
    data["value_month_chicken"] *= data.state.map(
        {1: 0.6, 2: 0.8, 3: 1, 4: 1.3, 5: 1.7}
    )
    result = va.state_holdout(data, "value_month_chicken")
    assert (result.upper_90 > result.lower_10).all()
    assert (result.n_nested_states == 4).all()
    assert (result.interval_method == "NESTED_STATE_HOLDOUT_ERRORS").all()
    assert va.summary(result)["coverage_80"] == pytest.approx(
        result.interval_hit.mean()
    )


def test_nested_errors_match_independent_refits(india_fixture):
    """Check the sufficient-statistic shortcut against independently refitted models."""
    data = india_fixture.copy()
    data["value_month_chicken"] *= 0.6 + data.state / 5
    fitted = va._fit(data, "value_month_chicken")
    errors = []
    for state in sorted(data.state.unique()):
        test = data.loc[data.state.eq(state)]
        model = va._fit(data.loc[data.state.ne(state)], "value_month_chicken")
        weights = test.multiplier * test.hh_size
        predicted = np.average(model(test), weights=weights)
        observed = np.sum(test.multiplier * test.value_month_chicken) / weights.sum()
        errors.append(np.log1p(observed) - np.log1p(predicted))
    np.testing.assert_allclose(fitted.transfer_errors, errors, atol=1e-10)


def test_predictor_uses_training_transform_in_every_batch(india_fixture):
    """Adding extreme heldout covariates cannot change another row's prediction."""
    train = india_fixture.loc[india_fixture.state.ne(1)]
    test = india_fixture.loc[india_fixture.state.eq(1)].copy()
    model = va._fit(train, "value_month_chicken")
    first = model(test.iloc[:1]).iloc[0]
    test.loc[test.index[1:], "hh_size"] = 1000
    test["value_month_chicken"] = 1e20
    assert model(test).iloc[0] == pytest.approx(first)


def test_zero_spending_stays_observed(india_fixture):
    """Real recorded zeros are valid outcomes; missing is not the same as zero."""
    data = india_fixture.copy()
    data["value_month_chicken"] = 0.0
    result = va.state_holdout(data, "value_month_chicken")
    assert result.observed.eq(0).all()
    assert result.predicted.eq(0).all()
    assert va.summary(result)["median_ape"] is None


def test_no_training_states_or_outcomes_fail_explicitly(india_fixture):
    """A single-state dataset cannot masquerade as cross-state validation."""
    with pytest.raises(ValueError, match="two states"):
        va.state_holdout(india_fixture.query("state == 1"), "value_month_chicken")
    empty = india_fixture.copy()
    empty["value_month_chicken"] = np.nan
    result = va.state_holdout(empty, "value_month_chicken")
    assert result.predicted.isna().all()
    assert va.summary(result)["mae"] is None


def test_summary_zero_observed_ape_has_defined_denominator():
    """Undefined percentage errors at zero are excluded and counted."""
    frame = pd.DataFrame(
        {
            "state": [1, 2],
            "observed": [0.0, 10.0],
            "predicted": [2.0, 12.0],
            "abs_error": [2.0, 2.0],
            "interval_hit": [True, False],
        }
    )
    result = va.summary(frame)
    assert result["mae"] == 2
    assert result["median_ape"] == pytest.approx(0.2)
    assert result["states_ape"] == 1
    assert result["coverage_80"] == 0.5


def test_training_elasticity_diagnostic_excludes_target_state(
    india_fixture, monkeypatch
):
    """Record actual fold coefficients and counts, not a dummy estimator call."""
    from types import SimpleNamespace

    seen = []

    def estimate(data, groups, **kwargs):
        """Return a known fold diagnostic for verification of the integration."""
        seen.append(set(data.state))
        return SimpleNamespace(
            estimates={"income:chicken": 0.5},
            n_households={"chicken": len(data)},
        )

    monkeypatch.setattr(va, "estimate_elasticities", estimate)
    data = india_fixture.assign(
        mpce_local=1000.0, mpce_status="OK", unit_value_chicken=50.0
    )
    result = va.state_holdout(data, "value_month_chicken")
    details = va.summary(result)["training_elasticity_diagnostics"]
    assert len(seen) == 5
    assert all(len(states) == 4 for states in seen)
    assert all(d["coefficients"]["income:chicken"] == 0.5 for d in details.values())
    assert all(d["n_households"]["chicken"] == 240 for d in details.values())


def _round(data: pd.DataFrame, year: int) -> pd.DataFrame:
    """Attach explicit compatible units and item mapping to a supplied round."""
    result = data.copy()
    result.attrs["validation_metadata"] = {
        "survey_year": year,
        "currency": "INR",
        "price_basis": "INR_2025",
        "outcome": "value_month_chicken",
        "outcome_unit": "INR_per_household_per_month",
        "recall_basis": "monthly_harmonized",
        "item_mapping": "chicken_195",
        "weight_definition": "household_survey_multiplier",
    }
    return result


def test_time_comparison_runs_on_real_compatible_schema(india_fixture):
    """Compatible supplied rounds permit train-earlier predict-later comparison."""
    result = va.time_comparison(
        _round(india_fixture, 2012), _round(india_fixture, 2023)
    )
    assert result["earlier_year"] == 2012
    assert result["later_year"] == 2023
    assert result["mae"] < 0.05
    assert result["states_evaluated"] == 5


@pytest.mark.parametrize(
    "field,value",
    [
        ("price_basis", "INR_2023"),
        ("item_mapping", "different"),
        ("outcome_unit", "INR_weekly"),
    ],
)
def test_time_comparison_rejects_incompatible_rounds(india_fixture, field, value):
    """Currency years, recall and item mappings must be established before comparison."""
    early, late = _round(india_fixture, 2012), _round(india_fixture, 2023)
    late.attrs["validation_metadata"][field] = value
    with pytest.raises(ValueError, match=field):
        va.time_comparison(early, late)


def test_input_taint_propagates_through_holdout_and_summary(india_fixture):
    """One invented training/target row taints every coupled holdout and its summary."""
    data = india_fixture.assign(status="DIAGNOSTIC")
    data.loc[0, "status"] = "SYNTHETIC"
    heldout = va.state_holdout(data, "value_month_chicken")
    assert heldout.status.eq("SYNTHETIC").all()
    heldout.attrs["status"] = "ACCEPTED"
    assert va.summary(heldout)["status"] == "SYNTHETIC"


def test_temporal_training_taint_cannot_be_hidden(india_fixture):
    """Invented earlier-round values taint predictions on diagnostic later data."""
    early = _round(india_fixture, 2012)
    late = _round(india_fixture.assign(status="DIAGNOSTIC"), 2023)
    result = va.time_comparison(early, late)
    assert result["status"] == "SYNTHETIC"
    assert all(row["status"] == "SYNTHETIC" for row in result["states"])


def test_missing_status_defaults_to_diagnostic_but_unknown_is_rejected(india_fixture):
    """Unlabelled real frames cannot become accepted, and explicit unknowns fail closed."""
    data = india_fixture.drop(columns="status")
    assert va.state_holdout(data, "value_month_chicken").status.eq("DIAGNOSTIC").all()
    with pytest.raises(ValueError, match="status"):
        va.state_holdout(data.assign(status="UNREVIEWED"), "value_month_chicken")
