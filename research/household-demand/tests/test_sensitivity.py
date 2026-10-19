"""Analytic benchmarks and contract checks for independent-factor Sobol indices."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
import sensitivity


def ishigami(x: np.ndarray) -> np.ndarray:
    """Return the standard Ishigami benchmark with a=7 and b=0.1."""
    return (
        np.sin(x[:, 0])
        + 7 * np.sin(x[:, 1]) ** 2
        + 0.1 * x[:, 2] ** 4 * np.sin(x[:, 0])
    )


def additive(x: np.ndarray) -> np.ndarray:
    """Return an additive model with variance shares 1/5, 4/5 and zero."""
    return x[:, 0] + 2 * x[:, 1]


def test_ishigami_known_indices() -> None:
    """Recover analytic first-order and total indices, including interaction."""
    out = sensitivity.sobol_indices(ishigami, [(-np.pi, np.pi)] * 3, n=20_000)
    assert list(out.columns) == ["parameter", "first_order", "total"]
    assert out.parameter.tolist() == ["x1", "x2", "x3"]
    np.testing.assert_allclose(out.first_order, [0.3139, 0.4424, 0.0], atol=0.03)
    np.testing.assert_allclose(out.total, [0.5576, 0.4424, 0.2437], atol=0.03)


def test_additive_variance_shares_and_unused_factor() -> None:
    """Separate unequal additive variance shares and identify an unused input."""
    out = sensitivity.sobol_indices(additive, [(0.0, 1.0)] * 3, n=20_000)
    np.testing.assert_allclose(out.first_order, [0.2, 0.8, 0.0], atol=0.03)
    np.testing.assert_allclose(out.total, [0.2, 0.8, 0.0], atol=0.03)
    assert out.loc[2, "first_order"] == 0.0
    assert out.loc[2, "total"] == 0.0


def test_single_factor_has_full_variance_share() -> None:
    """Handle the single-factor case without silently discarding its axis."""
    out = sensitivity.sobol_indices(lambda x: x[:, 0] ** 2, [(2, 4)], n=20_000)
    assert out.loc[0, "first_order"] == pytest.approx(1, abs=0.03)
    assert out.loc[0, "total"] == pytest.approx(1, abs=0.03)


def test_one_vectorized_call_respects_bounds() -> None:
    """Pass all base and pick-freeze samples in one correctly bounded batch."""
    seen: list[np.ndarray] = []

    def model(x: np.ndarray) -> np.ndarray:
        """Record the submitted batch and return a nonconstant scalar output."""
        seen.append(x.copy())
        return x[:, 0] - x[:, 1]

    out = sensitivity.sobol_indices(model, [(2, 4), (-7, -3)], n=500)
    assert len(seen) == 1
    assert seen[0].shape == (2_000, 2)
    assert np.all(seen[0] >= np.array([2, -7]))
    assert np.all(seen[0] <= np.array([4, -3]))
    assert out.attrs["diagnostics"]["model_evaluations"] == 2_000


def test_reproducibility_and_seed_changes() -> None:
    """Repeat all estimates and diagnostics with a seed and vary another seed."""
    first = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=500)
    repeat = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=500)
    changed = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=500, seed=3)
    pd.testing.assert_frame_equal(first, repeat)
    assert first.attrs == repeat.attrs
    assert not first.equals(changed)


def test_global_random_state_is_untouched() -> None:
    """Keep the helper's seed local rather than changing NumPy's global RNG."""
    before = np.random.get_state()
    sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=50)
    after = np.random.get_state()
    assert before[0] == after[0]
    np.testing.assert_array_equal(before[1], after[1])
    assert before[2:] == after[2:]


@pytest.mark.parametrize("scale", [1e-200, -3.0, 1e150])
def test_output_scaling_preserves_indices(scale: float) -> None:
    """Avoid variance underflow or overflow when changing output units."""
    base = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=500)
    scaled = sensitivity.sobol_indices(
        lambda x: scale * additive(x), [(0, 1)] * 3, n=500
    )
    np.testing.assert_allclose(scaled.iloc[:, 1:], base.iloc[:, 1:], atol=1e-12)


def test_output_offset_preserves_indices() -> None:
    """Centre outputs so first-order estimates do not depend on the intercept."""
    base = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=500)
    shifted = sensitivity.sobol_indices(
        lambda x: 1_000_000 + additive(x), [(0, 1)] * 3, n=500
    )
    np.testing.assert_allclose(shifted.iloc[:, 1:], base.iloc[:, 1:], atol=1e-8)


def test_negative_estimates_are_not_clipped() -> None:
    """Preserve negative sampling error in the zero-first-order Ishigami factor."""
    out = sensitivity.sobol_indices(ishigami, [(-np.pi, np.pi)] * 3, n=64)
    assert out.loc[2, "first_order"] < 0
    assert out.attrs["diagnostics"]["outside_unit_interval"]


def test_estimates_above_one_are_not_clipped() -> None:
    """Preserve upward sampling error in a pure interaction's total effects."""
    out = sensitivity.sobol_indices(lambda x: x[:, 0] * x[:, 1], [(-1, 1)] * 2, n=64)
    assert (out.total > 1).any()
    assert out.attrs["diagnostics"]["outside_unit_interval"]


@pytest.mark.parametrize("constant", [0.0, 7.0, 1e300])
def test_constant_output_is_undefined(constant: float) -> None:
    """Reject constant responses instead of reporting zero or perfect indices."""
    with pytest.raises(ValueError, match="zero variance"):
        sensitivity.sobol_indices(lambda x: np.full(len(x), constant), [(0, 1)], n=100)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_output_is_rejected(bad: float) -> None:
    """Reject any missing or infinite model output, including hybrid draws."""

    def model(x: np.ndarray) -> np.ndarray:
        """Place the invalid output in the last hybrid sample."""
        values = x[:, 0].copy()
        values[-1] = bad
        return values

    with pytest.raises(ValueError, match="finite"):
        sensitivity.sobol_indices(model, [(0, 1)], n=100)


@pytest.mark.parametrize("kind", ["scalar", "column", "short", "matrix"])
def test_invalid_output_shape_is_rejected(kind: str) -> None:
    """Require exactly one scalar output per sampled input row."""

    def model(x: np.ndarray) -> np.ndarray:
        """Return a deliberately malformed output with the selected shape."""
        shapes = {
            "scalar": (),
            "column": (len(x), 1),
            "short": (len(x) - 1,),
            "matrix": (len(x), 2),
        }
        return np.ones(shapes[kind])

    with pytest.raises(ValueError, match="shape"):
        sensitivity.sobol_indices(model, [(0, 1)], n=100)


@pytest.mark.parametrize("dtype", [complex, str, object])
def test_nonreal_output_is_rejected(dtype: type) -> None:
    """Do not silently discard imaginary parts or coerce strings to numbers."""
    with pytest.raises(ValueError, match="real numeric"):
        sensitivity.sobol_indices(lambda x: x[:, 0].astype(dtype), [(0, 1)], n=100)


@pytest.mark.parametrize(
    "bounds",
    [[], [(0, 0)], [(2, 1)], [(0, np.inf)], [(np.nan, 1)], [0, 1], [(0, 1, 2)]],
)
def test_invalid_bounds_are_rejected(bounds: list) -> None:
    """Require a nonempty sequence of finite, strictly ordered intervals."""
    with pytest.raises(ValueError, match="bounds"):
        sensitivity.sobol_indices(lambda x: x[:, 0], bounds, n=100)


@pytest.mark.parametrize("n", [0, 1, -2, 2.5, True])
def test_invalid_sample_count_is_rejected(n: int) -> None:
    """Require an integer base sample count of at least two."""
    with pytest.raises(ValueError, match="n must"):
        sensitivity.sobol_indices(lambda x: x[:, 0], [(0, 1)], n=n)


@pytest.mark.parametrize("seed", [-1, 1.5, None, True])
def test_invalid_seed_is_rejected(seed: int) -> None:
    """Require a nonnegative integer seed so runs always remain reproducible."""
    with pytest.raises(ValueError, match="seed must"):
        sensitivity.sobol_indices(lambda x: x[:, 0], [(0, 1)], n=100, seed=seed)


def test_diagnostics_are_serializable_and_do_not_claim_convergence() -> None:
    """Expose split-half differences as a diagnostic rather than an interval."""
    out = sensitivity.sobol_indices(additive, [(0, 1)] * 3, n=501)
    diagnostics = out.attrs["diagnostics"]
    json.dumps(diagnostics, allow_nan=False)
    assert diagnostics["seed"] == 20261018
    assert diagnostics["n_base"] == 501
    assert diagnostics["split_half"]["n_base"] == [250, 251]
    assert diagnostics["split_half"]["status"] == "DIAGNOSTIC_ONLY"
    assert len(diagnostics["split_half"]["first_order_abs_difference"]) == 3
    assert len(diagnostics["split_half"]["total_abs_difference"]) == 3
    assert diagnostics["convergence_certified"] is False


def test_smallest_sample_has_unassessed_split_half_diagnostic() -> None:
    """Avoid presenting one-row half-samples as a useful convergence check."""
    out = sensitivity.sobol_indices(lambda x: x[:, 0], [(0, 1)], n=2)
    assert out.attrs["diagnostics"]["split_half"]["status"] == "INSUFFICIENT_N"
