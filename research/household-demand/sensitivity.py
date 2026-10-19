"""Variance-based sensitivity for independent inputs using Saltelli estimators.

For independent uniform inputs, generate base matrices A and B and one hybrid
A_Bi per parameter, replacing only column i of A with B. With centred outputs
and V = var([f(A), f(B)], ddof=0), the estimators are:

    S_i = mean(f(B) * (f(A_Bi) - f(A))) / V
    ST_i = mean((f(A) - f(A_Bi)) ** 2) / (2 * V)

Reference: Saltelli et al. (2010), Computer Physics Communications 181:259-270,
https://doi.org/10.1016/j.cpc.2009.09.018. These are Sobol indices, with ordinary
pseudorandom Monte Carlo sampling, not a Sobol low-discrepancy sequence.

The model must be deterministic and return one scalar response per input row.
For nonuniform independent distributions, use unit-cube bounds and apply each
registered inverse CDF inside the model. Correlated coefficients must not be
treated as independent Sobol factors; a joint draw can be one grouped factor.
This helper does not infer uncertainty distributions or produce market results.
"""

from __future__ import annotations

from collections.abc import Callable
from numbers import Integral

import numpy as np
import pandas as pd

__all__ = ["sobol_indices"]


def _validate_bounds(bounds: list[tuple[float, float]]) -> np.ndarray:
    """Return finite real bounds with one strictly increasing interval per row."""
    try:
        limits = np.asarray(bounds)
    except (TypeError, ValueError) as exc:
        raise ValueError("bounds must contain finite (lower, upper) pairs") from exc
    if (
        limits.ndim != 2
        or limits.shape[0] == 0
        or limits.shape[1] != 2
        or limits.dtype.kind not in "iuf"
    ):
        raise ValueError("bounds must contain finite real (lower, upper) pairs")
    limits = limits.astype(float)
    if not np.isfinite(limits).all() or np.any(limits[:, 0] >= limits[:, 1]):
        raise ValueError("bounds must be finite and satisfy lower < upper")
    return limits


def _estimate(outputs: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Estimate indices after scaling and centring to protect numerical range."""
    scale = float(np.max(np.abs(outputs)))
    if scale == 0:
        raise ValueError("Sobol indices are undefined for zero variance output")
    scaled = outputs / scale
    centred = scaled - np.mean(scaled[:2])
    variance = float(np.mean(centred[:2] ** 2))
    if variance <= 0:
        raise ValueError(
            "Sobol indices are undefined for zero variance in sampled base outputs"
        )
    difference = centred[2:] - centred[0]
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        first_order = np.mean(centred[1] * difference, axis=1) / variance
        total = 0.5 * np.mean(difference**2, axis=1) / variance
    if not np.isfinite(first_order).all() or not np.isfinite(total).all():
        raise ValueError("Sobol index estimates exceed finite numerical precision")
    return first_order, total, variance, scale


def _split_half_diagnostic(outputs: np.ndarray) -> dict:
    """Compare independent half-samples without claiming confidence or convergence."""
    n = outputs.shape[1]
    middle = n // 2
    diagnostic = {
        "n_base": [middle, n - middle],
        "status": "INSUFFICIENT_N",
        "first_order_abs_difference": None,
        "total_abs_difference": None,
        "note": "Split-half differences are not confidence intervals or convergence proof.",
    }
    if middle < 2:
        return diagnostic
    try:
        first_left, total_left, _, _ = _estimate(outputs[:, :middle])
        first_right, total_right, _, _ = _estimate(outputs[:, middle:])
    except ValueError:
        diagnostic["status"] = "UNDEFINED_HALF_ESTIMATE"
        return diagnostic
    diagnostic.update(
        status="DIAGNOSTIC_ONLY",
        first_order_abs_difference=np.abs(first_left - first_right).tolist(),
        total_abs_difference=np.abs(total_left - total_right).tolist(),
    )
    return diagnostic


def sobol_indices(
    model: Callable[[np.ndarray], np.ndarray],
    bounds: list[tuple[float, float]],
    n: int,
    seed: int = 20261018,
) -> pd.DataFrame:
    """Return unclipped first-order and total Sobol estimates for uniform inputs.

    ``n`` is the size of each base matrix, not the total number of evaluations.
    For d bounds, the single vectorized model call receives shape
    ``(n * (d + 2), d)`` and must return shape ``(n * (d + 2),)``. Inputs are
    independent uniforms over the supplied finite intervals. Fixed factors stay
    inside the model rather than appearing as zero-width bounds.

    The returned columns are ``parameter`` (x1 through xd), ``first_order`` and
    ``total``. ``frame.attrs['diagnostics']`` records the sample design, split
    differences, and any estimates outside [0, 1]. Export this metadata explicitly
    beside CSV results: DataFrame attributes do not survive CSV serialization.

    Small-sample estimates can be negative, greater than one, or have a first
    order exceeding the total; no clipping or reordering conceals those errors.
    Zero sampled base variance raises ValueError because indices are undefined.
    Reproducibility requires a deterministic model and the frozen NumPy version.
    """
    if isinstance(n, (bool, np.bool_)) or not isinstance(n, Integral) or n < 2:
        raise ValueError("n must be an integer of at least 2")
    if isinstance(seed, (bool, np.bool_)) or not isinstance(seed, Integral) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    if not callable(model):
        raise TypeError("model must be callable")
    limits = _validate_bounds(bounds)
    n, seed = int(n), int(seed)
    dimensions = len(limits)
    rng = np.random.default_rng(seed)
    unit = rng.random((n, 2, dimensions))
    # Convex interpolation avoids overflow in upper - lower for wide bounds.
    base = (1 - unit) * limits[:, 0] + unit * limits[:, 1]
    a, b = base[:, 0], base[:, 1]
    design = np.broadcast_to(a, (dimensions + 2, n, dimensions)).copy()
    design[1] = b
    for column in range(dimensions):
        design[column + 2, :, column] = b[:, column]
    evaluations = n * (dimensions + 2)
    values = np.asarray(model(design.reshape(evaluations, dimensions)))
    if values.shape != (evaluations,):
        raise ValueError(
            f"model must return shape ({evaluations},), got {values.shape}"
        )
    if values.dtype.kind not in "biuf":
        raise ValueError("model must return real numeric outputs")
    values = values.astype(float)
    if not np.isfinite(values).all():
        raise ValueError("model outputs must all be finite")
    outputs = values.reshape(dimensions + 2, n)
    first_order, total, variance, scale = _estimate(outputs)
    parameters = [f"x{column + 1}" for column in range(dimensions)]
    result = pd.DataFrame(
        {"parameter": parameters, "first_order": first_order, "total": total}
    )
    result.attrs["diagnostics"] = {
        "estimator": "Saltelli_2010_first_order_and_squared_difference_total",
        "sampling": "independent_pseudorandom_uniform",
        "seed": seed,
        "n_base": n,
        "model_evaluations": evaluations,
        "bounds": limits.tolist(),
        "output_scale": scale,
        "scaled_output_variance": variance,
        "variance_definition": "var(base outputs / output_scale), ddof=0",
        "outside_unit_interval": [
            {"parameter": parameter, "index": name, "value": float(value)}
            for parameter, first, overall in zip(parameters, first_order, total)
            for name, value in (("first_order", first), ("total", overall))
            if value < 0 or value > 1
        ],
        "first_order_exceeds_total": [
            parameter
            for parameter, first, overall in zip(parameters, first_order, total)
            if first > overall
        ],
        "split_half": _split_half_diagnostic(outputs),
        "convergence_certified": False,
    }
    return result
