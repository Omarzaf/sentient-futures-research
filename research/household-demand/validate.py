"""Honest state transfer of reported animal-item spending, not adoption validation.

The animal target is the subtotal of observed nonnegative item values. An absent
item stays missing; this subtotal is NOT a complete animal basket. Per-capita
state spending is sum(multiplier * household value) / sum(multiplier * size),
among households with a valid target and survey design inputs.

Predictions use household size, sector, religion and caste only. MPCE contains
the target; unit values, quantities and segmentation are also excluded. The
weighted log1p spending regression uses fixed demographic encodings and only
training means, scales and smearing factors. Exact sufficient statistics over
identical demographic cells accelerate honest nested state holdouts. Predictive
10th/90th quantiles use those nested state's log1p mean prediction errors. They
are empirical state-transfer intervals, not survey-design confidence intervals.

Each outer training fold independently runs estimate_elasticities(draws=0) and
reports parameter stability separately. These coefficients do not enter the
demographic predictor. This exercise does not validate structural price effects
or plant-based adoption. All real-data results remain DIAGNOSTIC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from elasticities import INDIA_GROUPS, SEED, estimate_elasticities

__all__ = [
    "ANIMAL_GROUPS",
    "DEFAULT_OUTCOME",
    "MIN_HOUSEHOLDS",
    "main",
    "observed_animal_target",
    "state_holdout",
    "summary",
    "time_comparison",
]

ANIMAL_GROUPS = (
    "chicken",
    "mutton",
    "beef_buffalo",
    "fish",
    "pork",
    "eggs",
    "milk",
    "paneer",
)
DEFAULT_OUTCOME = "value_month_observed_animal"
MIN_HOUSEHOLDS = 30
DEMOGRAPHICS = ("hh_size", "sector", "religion", "caste")
INTERVAL_METHOD = "NESTED_STATE_HOLDOUT_ERRORS"
HERE = Path(__file__).resolve().parent


def _input_status(*frames: pd.DataFrame) -> str:
    """Keep invented inputs visible; this diagnostic never grants acceptance."""
    flags = []
    for frame in frames:
        if "status" in frame:
            flags.extend(frame.status.unique().tolist())
        if "status" in frame.attrs:
            flags.append(frame.attrs["status"])
    if any(flag not in ("DIAGNOSTIC", "SYNTHETIC", "ACCEPTED") for flag in flags):
        raise ValueError("Every explicit input status must be known")
    return "SYNTHETIC" if "SYNTHETIC" in flags else "DIAGNOSTIC"


def _numeric(series: pd.Series) -> pd.Series:
    """Coerce invalid and nonfinite numbers to missing without imputing values."""
    values = pd.to_numeric(series, errors="coerce").astype(float)
    return values.where(np.isfinite(values))


def observed_animal_target(households: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Return the labelled observed-item subtotal and complete-basket coverage."""
    columns = [f"value_month_{group}" for group in ANIMAL_GROUPS]
    values = households.reindex(columns=columns).apply(_numeric)
    values = values.where(values.ge(0))
    count = values.notna().sum(axis=1)
    target = values.sum(axis=1, min_count=1).rename(DEFAULT_OUTCOME)
    return target, {
        "target": "observed_item_animal_spending",
        "whole_basket_identified": False,
        "definition": "Sum of observed nonnegative animal-item values; absent groups remain missing, not zero. This is not total animal-protein spending.",
        "animal_groups": list(ANIMAL_GROUPS),
        "households": len(households),
        "households_with_observed_items": int(count.gt(0).sum()),
        "complete_basket_households": int(count.eq(len(ANIMAL_GROUPS)).sum()),
        "households_with_no_observed_items": int(count.eq(0).sum()),
        "reporting_households_by_group": {
            group: int(values[f"value_month_{group}"].notna().sum())
            for group in ANIMAL_GROUPS
        },
        "absent_group_columns": [
            column for column in columns if column not in households
        ],
    }


def _prepare(households: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Validate survey units and mark eligible rows, retaining exclusion counts."""
    required = {"state", "hh_size", "multiplier", "currency"}
    missing = required.difference(households.columns)
    if missing:
        raise ValueError(f"Missing household columns: {sorted(missing)}")
    currencies = households["currency"].dropna().unique()
    if len(currencies) != 1 or households.currency.isna().any():
        raise ValueError("One explicit currency is required for every household")
    data = households.copy()
    if outcome == DEFAULT_OUTCOME:
        data[outcome], metadata = observed_animal_target(data)
        values = data.reindex(
            columns=[f"value_month_{g}" for g in ANIMAL_GROUPS]
        ).apply(_numeric)
        data["_observed_groups"] = values.where(values.ge(0)).notna().sum(axis=1)
        data.attrs["target_metadata"] = metadata
    elif outcome not in data:
        raise ValueError(f"Outcome column {outcome!r} is missing")
    else:
        data.attrs["target_metadata"] = {
            "target": outcome,
            "whole_basket_identified": False,
            "definition": "Reported monthly household item expenditure, with missing observations excluded, not zero-filled.",
        }
    for column in ["hh_size", "multiplier", outcome]:
        data[column] = _numeric(data[column])
    data[outcome] = data[outcome].where(data[outcome].ge(0))
    data["_valid_design"] = (
        data.hh_size.gt(0) & data.multiplier.gt(0) & data.state.notna()
    )
    data["_eligible"] = data._valid_design & data[outcome].notna()
    data.attrs["outcome"] = outcome
    data.attrs["currency"] = str(currencies[0])
    data.attrs["status"] = _input_status(households)
    return data


def _demographics(frame: pd.DataFrame) -> pd.DataFrame:
    """Encode fixed HCES categories; missing or unknown codes have their own level."""
    out = pd.DataFrame({"hh_size": _numeric(frame.hh_size)}, index=frame.index)
    for name, codes in [
        ("sector", (1, 2)),
        ("religion", tuple(range(1, 10))),
        ("caste", (1, 2, 3, 9)),
    ]:
        values = (
            _numeric(frame[name])
            if name in frame
            else pd.Series(np.nan, index=frame.index)
        )
        out[name] = values.where(values.isin(codes), 0).astype(int)
    return out


def _design(frame: pd.DataFrame) -> np.ndarray:
    """Return a fixed design; no outcome or heldout-learned transformations enter."""
    data = _demographics(frame)
    columns = [np.ones(len(data)), np.log(data.hh_size.to_numpy(float))]
    for name, categories in [
        ("sector", (2, 0)),
        ("religion", (*range(2, 10), 0)),
        ("caste", (2, 3, 9, 0)),
    ]:
        columns.extend(data[name].eq(value).to_numpy(float) for value in categories)
    return np.column_stack(columns)


def _cells(frame: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Compress identical demographics exactly, preserving WLS and smearing sums."""
    valid = frame.loc[frame._eligible]
    cells = _demographics(valid)
    person_weight = valid.multiplier * valid.hh_size
    person_value = valid[outcome] / valid.hh_size
    cells = cells.assign(
        state=valid.state,
        weight=person_weight,
        weighted_log=person_weight * np.log1p(person_value),
        weighted_plus=person_weight * (person_value + 1),
    )
    return (
        cells.groupby(["state", *DEMOGRAPHICS], dropna=False, sort=True)
        .agg(
            weight=("weight", "sum"),
            weighted_log=("weighted_log", "sum"),
            weighted_plus=("weighted_plus", "sum"),
            count=("weight", "size"),
        )
        .reset_index()
    )


def _solve(gram: np.ndarray, rhs: np.ndarray) -> tuple[np.ndarray, int]:
    """Solve WLS with means/scales calculated only from this training Gram matrix."""
    if gram[0, 0] <= 0:
        raise ValueError("No eligible training households")
    mean = gram[0] / gram[0, 0]
    variance = np.maximum(np.diag(gram) / gram[0, 0] - mean**2, 0)
    mean[0], variance[0] = 0.0, 1.0
    scale = np.sqrt(variance)
    scale[scale < 1e-7] = 1.0
    transform = np.diag(1 / scale)
    transform[0, 1:] = -mean[1:] / scale[1:]
    standardized = transform.T @ gram @ transform / gram[0, 0]
    coefficient, _, rank, _ = np.linalg.lstsq(
        standardized,
        transform.T @ rhs / gram[0, 0],
        rcond=1e-10,
    )
    return transform @ coefficient, int(rank)


def _smearing(cells: pd.DataFrame, design: np.ndarray, beta: np.ndarray) -> float:
    """Compute the weighted training retransformation factor without household loss."""
    with np.errstate(over="ignore", invalid="ignore"):
        smear = (
            np.sum(cells.weighted_plus.to_numpy(float) * np.exp(-(design @ beta)))
            / cells.weight.sum()
        )
    if not np.isfinite(smear) or smear <= 0:
        raise ValueError("Training smearing factor is not finite and positive")
    return float(smear)


def _backtransform(linear: np.ndarray, smear: float) -> np.ndarray:
    """Return nonnegative original-unit predictions, preserving overflow as missing."""
    with np.errstate(over="ignore", invalid="ignore"):
        prediction = np.expm1(linear + np.log(smear))
    return np.where(np.isfinite(prediction), np.maximum(prediction, 0), np.nan)


@dataclass
class _Predictor:
    """An outcome-blind predictor plus training-only nested state error quantiles."""

    beta: np.ndarray
    smear: float
    transfer_errors: np.ndarray
    n_training: int
    rank: int
    elasticities: dict

    def __call__(self, frame: pd.DataFrame) -> pd.Series:
        """Predict per-capita monthly spending from demographics alone."""
        return pd.Series(
            _backtransform(_design(frame) @ self.beta, self.smear), index=frame.index
        )

    def interval(self, predicted: float) -> tuple[float, float]:
        """Apply the 10th/90th percentiles of honest training-state transfer errors."""
        if len(self.transfer_errors) < 3 or not np.isfinite(predicted):
            return np.nan, np.nan
        lower, upper = np.quantile(self.transfer_errors, [0.1, 0.9])
        return tuple(
            _backtransform(np.log1p(predicted) + np.array([lower, upper]), 1.0)
        )


def _elasticity_diagnostic(frame: pd.DataFrame) -> dict:
    """Estimate and retain training-fold structural parameters separately from prediction."""
    required = {
        "mpce_status",
        "mpce_local",
        "psu",
        "stratum",
        "stratum_status",
        "district",
        "sector",
    }
    groups = [
        g
        for g in INDIA_GROUPS
        if {f"value_month_{g}", f"unit_value_{g}"}.issubset(frame.columns)
    ]
    if not required.issubset(frame.columns) or not groups:
        return {
            "status": "UNAVAILABLE_SCHEMA",
            "missing_columns": sorted(required.difference(frame.columns)),
            "groups": groups,
        }
    clean = frame.copy()
    for col in [
        "mpce_local",
        "hh_size",
        "multiplier",
        *[f"unit_value_{g}" for g in groups],
        *[f"value_month_{g}" for g in groups],
    ]:
        clean[col] = _numeric(clean[col]).where(_numeric(clean[col]).ge(0))
    clean = clean.loc[clean._valid_design & clean.state.notna()]
    try:
        result = estimate_elasticities(
            clean, groups, cluster="psu", seed=SEED, draws=0, level="national"
        )
    except (ValueError, np.linalg.LinAlgError) as exc:
        return {
            "status": "UNAVAILABLE_ESTIMATION",
            "reason": str(exc),
            "groups": groups,
            "bootstrap_draws": 0,
        }
    coefficients = {}
    for name, value in result.estimates.items():
        enough = all(
            result.n_households.get(group, 0) >= MIN_HOUSEHOLDS
            for group in name.split(":")[1:]
        )
        coefficients[name] = float(value) if enough and np.isfinite(value) else None
    return {
        "status": (
            "DIAGNOSTIC"
            if all(v is not None for v in coefficients.values())
            else "PARTIAL_DIAGNOSTIC"
        ),
        "coefficients": coefficients,
        "n_households": result.n_households,
        "groups": groups,
        "bootstrap_draws": 0,
        "role": "Training-fold structural parameter stability only; not used in demographic predictions.",
    }


def _fit(data: pd.DataFrame, outcome: str) -> _Predictor:
    """Fit only training data and crossfit each remaining state for transfer uncertainty."""
    frame = data if "_eligible" in data else _prepare(data, outcome)
    cells = _cells(frame, outcome)
    if cells["count"].sum() < MIN_HOUSEHOLDS:
        raise ValueError("Fewer than30 eligible training households")
    design = _design(cells)
    weight = cells.weight.to_numpy(float)
    gram = design.T @ (design * weight[:, None])
    rhs = design.T @ cells.weighted_log.to_numpy(float)
    beta, rank = _solve(gram, rhs)
    smear = _smearing(cells, design, beta)
    errors = []
    states = cells.state.to_numpy()
    for state in pd.unique(states):
        hold = states == state
        if (
            cells.loc[hold, "count"].sum() < MIN_HOUSEHOLDS
            or cells.loc[~hold, "count"].sum() < MIN_HOUSEHOLDS
        ):
            continue
        training_x = design[~hold]
        inner_gram = training_x.T @ (training_x * weight[~hold, None])
        inner_rhs = training_x.T @ cells.loc[~hold, "weighted_log"].to_numpy(float)
        inner_beta, _ = _solve(inner_gram, inner_rhs)
        inner_smear = _smearing(cells.loc[~hold], training_x, inner_beta)
        prediction = _backtransform(design[hold] @ inner_beta, inner_smear)
        observed = cells.loc[hold, "weighted_plus"].sum() / weight[hold].sum() - 1
        if np.isfinite(prediction).all():
            predicted = np.average(prediction, weights=weight[hold])
            errors.append(float(np.log1p(observed) - np.log1p(predicted)))
    return _Predictor(
        beta,
        smear,
        np.array(errors),
        int(cells["count"].sum()),
        rank,
        _elasticity_diagnostic(frame),
    )


def _prediction_input(frame: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Expose only demographic inputs and an all-missing brief-compatibility sentinel."""
    data = frame.reindex(columns=DEMOGRAPHICS).copy()
    data[outcome] = np.nan
    return data


def _evaluate(
    frame: pd.DataFrame, outcome: str, predictor: Callable | None, error: str = ""
) -> dict:
    """Evaluate one state's matching observed/predicted cohort and apply suppression."""
    valid = frame.loc[frame._eligible]
    row = {
        "state": frame.state.iloc[0],
        "observed": np.nan,
        "predicted": np.nan,
        "abs_error": np.nan,
        "interval_hit": None,
        "lower_10": np.nan,
        "upper_90": np.nan,
        "n_households": len(frame),
        "n_evaluated": len(valid),
        "n_missing_outcome": int(frame[outcome].isna().sum()),
        "n_invalid_design": int((~frame._valid_design).sum()),
        "n_training": getattr(predictor, "n_training", None),
        "n_nested_states": len(getattr(predictor, "transfer_errors", [])),
        "interval_method": INTERVAL_METHOD,
        "status": _input_status(frame),
        "fold_status": (
            "SUPPRESSED_SMALL_CELL"
            if len(valid) < MIN_HOUSEHOLDS
            else "PREDICTION_UNAVAILABLE"
        ),
        "fit_error": error,
    }
    if "_observed_groups" in frame:
        row["complete_basket_households"] = int(
            frame._observed_groups.eq(len(ANIMAL_GROUPS)).sum()
        )
        row["mean_observed_groups"] = (
            float(valid._observed_groups.mean())
            if len(valid) >= MIN_HOUSEHOLDS
            else np.nan
        )
    if len(valid) < MIN_HOUSEHOLDS or predictor is None:
        return row
    predictions = np.asarray(predictor(_prediction_input(valid, outcome)), dtype=float)
    if (
        predictions.shape != (len(valid),)
        or not np.isfinite(predictions).all()
        or (predictions < 0).any()
    ):
        row["fit_error"] = (
            "Prediction vector must contain one finite nonnegative value per eligible household"
        )
        return row
    person_weight = valid.multiplier * valid.hh_size
    observed = float(np.sum(valid.multiplier * valid[outcome]) / person_weight.sum())
    predicted = float(np.average(predictions, weights=person_weight))
    lower, upper = (
        predictor.interval(predicted)
        if hasattr(predictor, "interval")
        else (np.nan, np.nan)
    )
    row.update(
        observed=observed,
        predicted=predicted,
        abs_error=abs(observed - predicted),
        lower_10=lower,
        upper_90=upper,
    )
    if np.isfinite([lower, upper]).all():
        row.update(interval_hit=bool(lower <= observed <= upper), fold_status="OK")
    else:
        row["fold_status"] = "INTERVAL_UNAVAILABLE"
    return row


def state_holdout(
    households: pd.DataFrame, outcome: str = DEFAULT_OUTCOME
) -> pd.DataFrame:
    """Leave out every state, predict it without outcomes and return suppressed aggregates."""
    data = _prepare(households, outcome)
    states = data.state.dropna().unique()
    if len(states) < 2:
        raise ValueError("State holdout requires at least two states")
    rows, diagnostics = [], {}
    for state in sorted(states):
        heldout = data.state.eq(state)
        predictor, error = None, ""
        try:
            predictor = _fit(data.loc[~heldout & data.state.notna()].copy(), outcome)
        except (ValueError, np.linalg.LinAlgError) as exc:
            error = str(exc)
        rows.append(_evaluate(data.loc[heldout], outcome, predictor, error))
        diagnostics[str(state)] = getattr(
            predictor,
            "elasticities",
            {"status": "UNAVAILABLE", "reason": error or "custom predictor"},
        )
    result = pd.DataFrame(rows)
    # Every fold uses other states as training data: taint is dataset-wide.
    result["status"] = data.attrs["status"]
    result.attrs.update(
        target_metadata=data.attrs["target_metadata"],
        currency=data.attrs["currency"],
        n_missing_state=int(data.state.isna().sum()),
        training_elasticity_diagnostics=diagnostics,
    )
    return result


def summary(holdout: pd.DataFrame) -> dict:
    """Report unweighted state MAE, median fractional APE and measured80% interval coverage."""
    good = np.isfinite(holdout.observed) & np.isfinite(holdout.predicted)
    evaluated = holdout.loc[good]
    positive = evaluated.observed.gt(0)
    errors = (evaluated.observed - evaluated.predicted).abs()
    intervals = evaluated.interval_hit.dropna()
    return {
        "mae": float(errors.mean()) if len(errors) else None,
        "median_ape": (
            float((errors[positive] / evaluated.loc[positive, "observed"]).median())
            if positive.any()
            else None
        ),
        "coverage_80": (
            float(intervals.astype(float).mean()) if len(intervals) else None
        ),
        "states_total": len(holdout),
        "states_evaluated": int(good.sum()),
        "states_without_prediction": int((~good).sum()),
        "states_ape": int(positive.sum()),
        "states_with_intervals": len(intervals),
        "states_suppressed": int(
            holdout.get("fold_status", pd.Series(dtype=str))
            .eq("SUPPRESSED_SMALL_CELL")
            .sum()
        ),
        "metric_weighting": "Each evaluable state has equal weight; median_ape is a fraction, not a percentage.",
        "per_capita_definition": "sum(household multiplier * observed household monthly value) / sum(household multiplier * household size), in matching eligible cohorts.",
        "prediction_method": "Person-weighted log1p reported spending on fixed demographic features, training-only centering/scaling and smearing.",
        "prediction_features": list(DEMOGRAPHICS),
        "interval_method": "Empirical10th and90th percentiles of honest nested training-state log1p mean prediction errors. State-transfer predictive intervals, not design-based survey confidence intervals. Coverage is measured, not assumed.",
        "min_cell_households": MIN_HOUSEHOLDS,
        "limitations": [
            "Validates demographic transfer of reported spending, not plant-based adoption or structural price response.",
            "Observed-item target omits unreported groups; it is not complete animal-protein spending or a population total.",
            "Nested state-transfer errors assume the heldout state is exchangeable with training states; heterogeneity can violate this assumption.",
            "No survey-design confidence interval is claimed; parameter stability diagnostics have zero bootstrap draws.",
            "India microdata lineage and baseline acceptance remain unresolved; human scholarly review remains pending.",
        ],
        **holdout.attrs,
        "status": _input_status(holdout),
    }


def time_comparison(earlier: pd.DataFrame | None, later: pd.DataFrame | None) -> dict:
    """Train earlier and evaluate later, with explicit harmonization metadata.

    Each frame's ``attrs['validation_metadata']`` must declare survey_year,
    currency, price_basis (for example INR_2025), outcome, outcome_unit,
    recall_basis (monthly_harmonized), item_mapping and weight_definition.
    Monetary units are per household per month; both rounds must use the same
    constant price year and canonical demographic codes. Metadata are caller
    assertions of harmonization, not independent evidence of its correctness.
    """
    if earlier is None or later is None:
        raise FileNotFoundError(
            "Register at https://microdata.gov.in and supply the earlier and later household microdata rounds; no earlier round is substituted."
        )
    keys = (
        "currency",
        "price_basis",
        "outcome",
        "outcome_unit",
        "recall_basis",
        "item_mapping",
        "weight_definition",
    )
    first, second = (
        frame.attrs.get("validation_metadata", {}) for frame in (earlier, later)
    )
    for metadata in (first, second):
        for key in (*keys, "survey_year"):
            if key not in metadata or metadata[key] in (None, ""):
                raise ValueError(f"validation_metadata requires {key}")
    for key in keys:
        if first[key] != second[key]:
            raise ValueError(
                f"Incompatible round {key}: {first[key]!r} versus {second[key]!r}"
            )
    if first["outcome_unit"] != f"{first['currency']}_per_household_per_month":
        raise ValueError("outcome_unit must specify currency per household per month")
    if first["recall_basis"] != "monthly_harmonized":
        raise ValueError("recall_basis must be monthly_harmonized")
    if not re.fullmatch(
        rf"{re.escape(str(first['currency']))}_[0-9]{{4}}", str(first["price_basis"])
    ):
        raise ValueError(
            "price_basis must identify the shared currency and constant price year"
        )
    if int(first["survey_year"]) >= int(second["survey_year"]):
        raise ValueError("Earlier survey_year must precede later survey_year")
    outcome = first["outcome"]
    if outcome == DEFAULT_OUTCOME:
        animal_columns = {f"value_month_{group}" for group in ANIMAL_GROUPS}
        if animal_columns.intersection(earlier.columns) != animal_columns.intersection(
            later.columns
        ):
            raise ValueError("Incompatible animal-item column schema between rounds")
    training, testing = _prepare(earlier, outcome), _prepare(later, outcome)
    if (
        training.attrs["currency"] != first["currency"]
        or testing.attrs["currency"] != second["currency"]
    ):
        raise ValueError("currency metadata disagree with household currency")
    predictor = _fit(training, outcome)
    states = pd.DataFrame(
        [
            _evaluate(group, outcome, predictor)
            for _, group in testing.groupby("state", sort=True)
        ]
    )
    states["status"] = _input_status(training, testing)
    result = summary(states)
    result.update(
        earlier_year=int(first["survey_year"]),
        later_year=int(second["survey_year"]),
        compatibility=first,
        states=json.loads(states.to_json(orient="records")),
        training_elasticity_diagnostic=predictor.elasticities,
    )
    return result


def main(argv: list[str] | None = None) -> int:
    """Read a local household parquet and save state/national diagnostics only."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--india", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=HERE / "outputs" / "holdout.csv")
    parser.add_argument(
        "--summary", type=Path, default=HERE / "outputs" / "holdout-summary.json"
    )
    args = parser.parse_args(argv)
    households = pd.read_parquet(args.india)
    if not households.currency.eq("INR").all():
        raise ValueError("The India validation CLI requires INR household data")
    if _input_status(households) == "SYNTHETIC":
        raise ValueError(
            "Placeholder-derived validation cannot be written to ordinary outputs"
        )
    for col in ["status", "stratum_status"]:
        if col in households and households[col].eq("SYNTHETIC").any():
            raise ValueError(
                "Placeholder-derived validation cannot be written to ordinary outputs"
            )
    result = state_holdout(households)
    report = summary(result)
    report.update(
        source="Existing HCES2023-24 household table; local unit data not included",
        input_sha256=hashlib.sha256(args.india.read_bytes()).hexdigest(),
        implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        library_versions={"numpy": np.__version__, "pandas": pd.__version__},
        method_ruling="R53",
        randomness="None: nested state fits and empirical quantiles are deterministic; elasticity point diagnostics use draws=0.",
        outcome_unit="INR_per_person_per_month_survey_prices",
        price_basis="HCES2023-24 nominal INR; no USD conversion needed for within-round validation",
        secondary_time_comparison="NOT_RUN: earlier harmonized rounds require author registration at microdata.gov.in",
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    args.summary.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                key: report[key]
                for key in [
                    "mae",
                    "median_ape",
                    "coverage_80",
                    "states_evaluated",
                    "states_suppressed",
                ]
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
