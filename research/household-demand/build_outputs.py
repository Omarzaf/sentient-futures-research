"""Rebuild bounded comparison, scenarios, actual Sobol analysis and research report.

Only this module's own generated files are written. Reviewed Task8 main, US-stress
and literal-sign artifacts remain inputs. Every country-year is analysed; any
placeholder ancestry keeps its numerical derivatives under synthetic/outputs.
No acceptance status or claims-ledger mutation is granted by this builder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import simulate as sm
from sensitivity import sobol_indices

__all__ = [
    "build_scenarios",
    "build_sobol",
    "claim_rows",
    "comparison_table",
    "model_from_panel_inputs",
    "panel_inputs",
    "us_calibration_table",
    "write_csv",
]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
HELD = HERE / "synthetic/outputs"
PROXY = HERE.parents[1] / "research/india-pakistan/data/altprotein_proxy_scenarios.csv"
YEARS = (2026, 2030, 2035)
COUNTRIES = ("India", "Pakistan")
MODELS = ("claude-opus-5-5", "gpt-6-astra")
QUANTILES = ("p10", "p50", "p90")
PANEL_STATUSES = ("COMPLETE_PANEL", "PARTIAL_PANEL")
UNIT = "million USD, 2025 prices"
SCOPE = "plant-based meat and liquid milk"
PANEL_SCOPE = "plant-based meat/seafood and all dairy alternatives plus residual"
PARAMETERS = ("conversion", "bass_p", "bass_q", "price_parity_year", "ai_cost_decline")
SEED = 20261018
DECIMALS = 6


def read_json(path: Path, default: Any = None) -> Any:
    """Read a deterministic local artifact or return a caller-supplied absence value."""
    return json.loads(path.read_text()) if path.exists() else default


def sha256(path: Path) -> str:
    """Hash exact source bytes without reading individual records into logs."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_safe(value: Any) -> Any:
    """Convert nonfinite and NumPy values to strict, portable JSON."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def write_json(value: Any, path: Path) -> None:
    """Serialize deterministic finite JSON with a trailing newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(value), indent=2, allow_nan=False) + "\n")


def write_csv(table: pd.DataFrame, path: Path) -> None:
    """Write six decimal places, missing cells empty, without discarding signs."""
    if (
        "status" in table
        and table.status.eq("SYNTHETIC").any()
        and path.resolve().is_relative_to(sm.LIBRARY_ROOT)
        and not path.resolve().is_relative_to(HELD)
    ):
        raise ValueError("placeholder-derived rows require synthetic/outputs")
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(
        path, index=False, float_format=f"%.{DECIMALS}f", na_rep="", lineterminator="\n"
    )


def proxy_quantiles(table: pd.DataFrame, country: str, year: int) -> dict:
    """Select only the exact scenario/market/year quantile records."""
    rows = table[
        table.record_type.eq("scenario")
        & table.quantity.eq("market_value")
        & table.country.eq(country)
        & table.year.eq(year)
        & table.statistic.isin(QUANTILES)
    ]
    if rows.statistic.duplicated().any():
        raise ValueError("duplicate proxy quantile source")
    values = dict(zip(rows.statistic, rows.value))
    return {q: values.get(q) for q in QUANTILES}


def _panel_row(
    panel: pd.DataFrame, country: str, model: str, measure: str, year: int | None
) -> dict | None:
    """Require exactly one region/model/measure/year row, never pool models."""
    if panel.empty:
        return None
    matched = (
        panel.region.astype(str).str.casefold().eq(country.casefold())
        & panel.model.eq(model)
        & panel.measure.eq(measure)
    )
    numeric_year = pd.to_numeric(panel.year, errors="coerce")
    matched &= numeric_year.isna() if year is None else numeric_year.eq(year)
    rows = panel[matched]
    if len(rows) > 1:
        raise ValueError("duplicate panel summary row")
    return rows.iloc[0].to_dict() if len(rows) else None


def _panel_status(row: dict | None) -> str:
    """Require trusted producer ancestry before deriving bounded panel coverage."""
    if row is None:
        return "PENDING_PANEL"
    status = row.get("status")
    if not isinstance(status, str) or status not in PANEL_STATUSES:
        return "HELD_PANEL_STATUS"
    count = int(row.get("n_accepted", 0))
    if count == 0:
        return "PENDING_PANEL"
    if not 0 < count <= 10:
        return "HELD_PANEL_STATUS"
    return (
        "COMPLETE_PANEL"
        if count == 10 and status == "COMPLETE_PANEL"
        else "PARTIAL_PANEL"
    )


US_MEASURES = {
    "headline": {
        "label": "Plant-based retail",
        "channel": "retail",
        "scope": "Final plant-derived animal-food replacements and marketed plant-protein products, including traditional plant-protein foods; excludes standalone upstream ingredients and unrelated whole foods.",
    },
    "categories.cultivated": {
        "label": "Cultivated meat",
        "channel": "retail and foodservice",
        "scope": "Finished cell-cultured meat products, including seafood, cultivated pet food and cell/plant hybrids; consumer products rather than ingredient-company revenue.",
    },
    "categories.fermentation": {
        "label": "Fermentation-derived proteins",
        "channel": "retail and foodservice",
        "scope": "Finished microbial-protein animal-food replacements and functional hybrids, including fermented dairy alternatives; excludes long-established fermented foods, nonfunctional minor additives, upstream ingredient revenue and health-purpose supplements.",
    },
}


def us_calibration_table(
    *,
    panel: pd.DataFrame | None = None,
    accepted_runs: dict | None = None,
    models: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Keep the original US measures separate and bind summaries to accepted records."""
    if panel is None:
        path = HERE / "elicitation/results.csv"
        panel = pd.read_csv(path) if path.exists() else pd.DataFrame()
    if accepted_runs is None:
        accepted_runs = read_json(
            HERE / "elicitation/accepted-runs.json", {"records": []}
        )
    if models is None:
        execution = read_json(HERE / "elicitation/execution-scope.json", {})
        models = tuple(execution.get("authorized_models", ["gpt-6-astra"]))
    if (
        not models
        or len(set(models)) != len(models)
        or any(model not in MODELS for model in models)
    ):
        raise ValueError("US calibration requires distinct registered models")
    rows, bindings = [], {}
    for model in models:
        records = [
            r
            for r in accepted_runs.get("records", [])
            if r.get("region") == "us" and r.get("model") == model
        ]
        slots = [r.get("slot") for r in records]
        digest_fields_ok = all(
            isinstance(r.get(key), str)
            and len(r[key]) == 64
            and all(c in "0123456789abcdef" for c in r[key])
            for r in records
            for key in ("answer_sha256", "prompt_sha256")
        )
        records_ok = (
            bool(records)
            and accepted_runs.get("status", "ACCEPTED") == "ACCEPTED"
            and len(set(slots)) == len(slots)
            and all(
                isinstance(slot, int) and not isinstance(slot, bool) and 1 <= slot <= 10
                for slot in slots
            )
            and digest_fields_ok
            and all(r.get("status", "ACCEPTED") == "ACCEPTED" for r in records)
        )
        bindings[model] = (
            [
                {
                    key: r.get(key)
                    for key in ("slot", "attempt_id", "answer_sha256", "prompt_sha256")
                }
                for r in records
            ]
            if records_ok
            else []
        )
        for measure, scope in US_MEASURES.items():
            for year in YEARS:
                row = _panel_row(panel, "us", model, measure, year)
                count = int((row or {}).get("n_accepted", 0))
                nonmissing = int((row or {}).get("n_nonmissing", 0))
                coverage = _panel_status(row)
                reason = ""
                if row is None:
                    reason = "US summary measure/year unavailable"
                elif coverage not in PANEL_STATUSES:
                    reason = "US panel source status untrusted or no accepted coverage"
                elif row.get("unit") not in (UNIT, "million USD_2025"):
                    reason = "US summary unit does not match constant2025 million USD"
                elif accepted_runs.get("status", "ACCEPTED") != "ACCEPTED":
                    reason = (
                        "US accepted-record export has an untrusted explicit status"
                    )
                elif nonmissing != count or not records_ok or count != len(records):
                    reason = "US accepted-record count, coverage or recorded digest fields incomplete"
                else:
                    try:
                        medians = np.array(
                            [
                                (
                                    r["headline"]
                                    if measure == "headline"
                                    else r["categories"][measure.split(".")[1]]
                                )[str(year)]["p50"]
                                for r in records
                            ],
                            dtype=float,
                        )
                        supplied = np.array([row[q] for q in QUANTILES], dtype=float)
                        expected = np.quantile(medians, [0.1, 0.5, 0.9])
                        if (
                            not np.isfinite(medians).all()
                            or not np.isfinite(supplied).all()
                            or (medians < 0).any()
                            or not np.allclose(supplied, expected, atol=5e-7, rtol=0)
                        ):
                            reason = "US summary does not reproduce accepted run medians at six decimals"
                    except (KeyError, TypeError, ValueError):
                        reason = "US accepted-record measure/year values missing"
                rows.append(
                    {
                        "region": "US",
                        "source_model": model,
                        "measure": measure,
                        "label": scope["label"],
                        "year": year,
                        "channel": scope["channel"],
                        "scope": scope["scope"],
                        "n_accepted": count,
                        "n_nonmissing": nonmissing,
                        **{q: row[q] if not reason else None for q in QUANTILES},
                        "unit": UNIT,
                        "status": coverage if not reason else "HELD_US_CALIBRATION",
                        "public_reporting": "HELD_AUTHOR_NOTIFICATION_AND_SCHOLARLY_REVIEW",
                        "withheld_reason": reason,
                        "spread_definition": "empirical across-run point-median percentiles; not predictive intervals or accuracy scores",
                        "source_ids": '["elicitation_results", "elicitation_accepted_runs", "elicitation_scope", "elicitation_instrument_provenance"]',
                    }
                )
    table = pd.DataFrame(rows)
    table.attrs["accepted_record_bindings"] = bindings
    return table


def comparison_table(
    *,
    main: dict | None = None,
    proxy: pd.DataFrame | None = None,
    panel: pd.DataFrame | None = None,
    panel_models: dict | None = None,
    include_placeholder: bool = False,
) -> pd.DataFrame:
    """Four methods per target cell, with per-model panel rows and explicit holds."""
    read_saved_reruns = panel is None and panel_models is None
    if main is None:
        main = {
            c: read_json(
                (OUT if c == "India" else HELD) / f"simulation-{c.lower()}.json"
            )
            for c in COUNTRIES
        }
    if proxy is None:
        proxy = pd.read_csv(PROXY)
    if panel is None:
        panel_path = HERE / "elicitation/results.csv"
        panel = pd.read_csv(panel_path) if panel_path.exists() else pd.DataFrame()
    if panel_models is None:
        saved = (
            read_json(HELD / "panel-model-summary.json", {"records": []})
            if read_saved_reruns
            else {"records": []}
        )
        panel_models = {
            (r["country"], r["year"], r["model"]): r for r in saved["records"]
        }
    records = []
    for country in COUNTRIES:
        for year in YEARS:
            common = {
                "country": country,
                "year": year,
                "unit": UNIT,
                "review_status": "PENDING",
                "review_id": "",
                "panel_coverage_status": "",
                "residual_p50": None,
                "total_with_residual_p50": None,
                "gap_to_household_p50": None,
            }
            artifact = main.get(country)
            qrows = [
                r
                for r in (artifact or {}).get("quantiles", [])
                if r["year"] == year and r["metric"] == "value_usd_2025"
            ]
            if len(qrows) > 1:
                raise ValueError("duplicate household quantile cell")
            qrow = qrows[0] if qrows else {}
            tainted = (artifact or {}).get("status") == "SYNTHETIC" or qrow.get(
                "status"
            ) == "SYNTHETIC"
            visible = bool(qrow) and (not tainted or include_placeholder)
            records.append(
                {
                    **common,
                    "method": "household_model",
                    "source_model": "",
                    **{
                        q: (
                            qrow.get(q) / 1e6
                            if visible and qrow.get(q) is not None
                            else None
                        )
                        for q in QUANTILES
                    },
                    "status": (
                        qrow.get("status", "HELD_MISSING_INPUT")
                        if visible
                        else (
                            "HELD_PLACEHOLDER_INPUT"
                            if tainted
                            else "HELD_MISSING_INPUT"
                        )
                    ),
                    "scope": SCOPE,
                    "scope_alignment": "SUBTOTAL_ONLY",
                    "withheld_reason": (
                        ""
                        if visible
                        else (
                            "Pakistan plant-meat price placeholder; numerical derivatives retained in restricted research outputs"
                            if tainted
                            else "household simulation missing"
                        )
                    ),
                    "n_accepted": None,
                    "source_ids": '["household_simulator"]',
                    "source_sha256": sha256(
                        (OUT if country == "India" else HELD)
                        / f"simulation-{country.lower()}.json"
                    ),
                    "spread_definition": "conditional Monte Carlo 10th/50th/90th quantiles",
                }
            )
            proxy_values = proxy_quantiles(proxy, country, year)
            records.append(
                {
                    **common,
                    "method": "gfi_proxy",
                    "source_model": "",
                    **proxy_values,
                    "status": "PROXY_SCENARIO",
                    "scope": "all plant-based retail categories",
                    "scope_alignment": "UNMATCHED",
                    "withheld_reason": "numeric gap held: category scopes differ; no disaggregated egg/fermentation residual",
                    "n_accepted": None,
                    "source_ids": '["altprotein_proxy_scenarios"]',
                    "source_sha256": sha256(PROXY),
                    "spread_definition": "existing proxy scenario quantiles",
                }
            )
            for model in MODELS:
                panel_row = _panel_row(panel, country, model, "headline", year)
                valid_unit = panel_row is not None and panel_row.get("unit") in (
                    UNIT,
                    "million USD_2025",
                )
                count = int((panel_row or {}).get("n_accepted", 0))
                nonmissing = int((panel_row or {}).get("n_nonmissing", count))
                panel_status = _panel_status(panel_row)
                trusted_status = panel_status in PANEL_STATUSES
                usable = (
                    trusted_status and valid_unit and count > 0 and nonmissing == count
                )
                records.append(
                    {
                        **common,
                        "method": "panel_headline",
                        "source_model": model,
                        "panel_coverage_status": _panel_status(panel_row),
                        **{q: panel_row.get(q) if usable else None for q in QUANTILES},
                        "status": _panel_status(panel_row) if usable else "HELD_PANEL",
                        "scope": PANEL_SCOPE,
                        "scope_alignment": "UNMATCHED",
                        "withheld_reason": (
                            "numeric gap held: panel dairy scope exceeds liquid milk"
                            if usable
                            else (
                                "no accepted panel answers"
                                if not count
                                else (
                                    "panel source status untrusted or placeholder-derived"
                                    if not trusted_status
                                    else "panel unit mismatch or missing run median"
                                )
                            )
                        ),
                        "n_accepted": count,
                        "source_ids": '["elicitation_results"]',
                        "source_sha256": (
                            sha256(HERE / "elicitation/results.csv")
                            if (HERE / "elicitation/results.csv").exists()
                            else ""
                        ),
                        "spread_definition": "across accepted runs' point medians; not a predictive interval",
                    }
                )
                rerun = panel_models.get((country, year, model), {})
                tainted = rerun.get("status") == "SYNTHETIC"
                rerun_coverage = (
                    _panel_status(
                        {
                            "n_accepted": rerun.get("n_accepted", 0),
                            "status": rerun.get("panel_coverage_status"),
                        }
                    )
                    if rerun
                    else "PENDING_PANEL"
                )
                known_result_status = rerun.get("status") in (
                    "DIAGNOSTIC",
                    "ACCEPTED",
                    "SYNTHETIC",
                )
                visible = (
                    bool(rerun)
                    and known_result_status
                    and rerun_coverage in PANEL_STATUSES
                    and (not tainted or include_placeholder)
                )
                records.append(
                    {
                        **common,
                        "method": "model_from_panel_inputs",
                        "source_model": model,
                        "panel_coverage_status": rerun_coverage,
                        **{q: rerun.get(q) if visible else None for q in QUANTILES},
                        "status": (
                            rerun.get("status")
                            if visible
                            else (
                                "HELD_PLACEHOLDER_INPUT"
                                if tainted
                                else "HELD_PANEL_INPUTS"
                            )
                        ),
                        "scope": SCOPE,
                        "scope_alignment": "UNMATCHED",
                        "withheld_reason": (
                            "numeric gap held: panel category scope does not match liquid-milk subtotal"
                            if visible
                            else (
                                "Pakistan plant-meat price placeholder"
                                if tainted
                                else "all five genuine, complete median panel inputs required"
                            )
                        ),
                        "n_accepted": rerun.get("n_accepted", 0),
                        "source_ids": '["elicitation_results", "household_simulator"]',
                        "source_sha256": rerun.get("source_sha256", ""),
                        "spread_definition": "conditional Monte Carlo around fixed per-model input medians; not across-run spread",
                    }
                )
    return pd.DataFrame(records)


def claim_rows(table: pd.DataFrame) -> pd.DataFrame:
    """Allow only affirmative human-reviewed, source-bound accepted numeric rows."""
    required = {
        "status",
        "review_status",
        "review_id",
        "source_ids",
        "source_sha256",
        "p50",
    }
    if not required.issubset(table):
        return table.iloc[:0].copy()

    def bound(value: Any) -> bool:
        """Require a nonempty explicit source-ID JSON array."""
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return False
        return (
            isinstance(parsed, list)
            and bool(parsed)
            and all(isinstance(v, str) and bool(v.strip()) for v in parsed)
        )

    approved = (
        table.status.eq("ACCEPTED")
        & table.review_status.eq("HUMAN_REVIEWED")
        & table.review_id.fillna("").astype(str).str.strip().ne("")
        & table.source_ids.map(bound)
        & table.source_sha256.fillna("").astype(str).str.fullmatch(r"[a-f0-9]{64}")
        & pd.to_numeric(table.p50, errors="coerce").map(np.isfinite)
    )
    return table[approved].copy()


def panel_inputs(inputs: sm.SimInputs, medians: dict) -> sm.SimInputs:
    """Map five genuine medians to the evaluator; dairy keeps its observed anchor."""
    if any(k not in medians or not np.isfinite(medians[k]) for k in PARAMETERS):
        raise ValueError("missing finite median panel inputs")
    if (
        not 0 <= medians["conversion"]
        or not 0 < medians["bass_p"]
        or not 0 <= medians["bass_q"]
        or not 0 <= medians["ai_cost_decline"] < 1
        or medians["price_parity_year"] <= 2026
    ):
        raise ValueError("invalid panel parameter domain")
    rows = inputs.rows.copy()
    rows.loc[rows.pair.ne("dairy"), "conversion"] = medians["conversion"]
    rows["bass_p"], rows["bass_q"] = medians["bass_p"], medians["bass_q"]
    return replace(
        inputs,
        rows=rows,
        parity_year=float(medians["price_parity_year"]),
        ai_decline=float(medians["ai_cost_decline"]),
        metadata={
            **inputs.metadata,
            "panel_input_medians": medians,
            "us_intent_n": None,
            "panel_conversion_uncertainty": "fixed per-model median; US intention sampling disabled so it cancels from conversion",
            "panel_ai_pass_through_assumption": "illustrative full manufacturing-cost to retail-price pass-through; not elicited or empirically identified",
            "panel_mapping_note": "conversion applies to meat and vegetarian pairs; dairy conversion stays at its observed US-milk calibration; Bass shape, parity and AI apply to each modelled pair",
        },
    )


def model_from_panel_inputs(
    inputs_by_country: dict[str, sm.SimInputs],
    panel: pd.DataFrame,
    *,
    n: int = 10000,
    write: bool = False,
) -> tuple[dict, list]:
    """Actually simulate each model's median inputs; missing/partial coverage is visible."""
    results, diagnostics = {}, []
    for country, inputs in inputs_by_country.items():
        for model in MODELS:
            rows = [
                _panel_row(panel, country, model, f"inputs.{p}", None)
                for p in PARAMETERS
            ]
            medians = {p: r.get("p50") if r else None for p, r in zip(PARAMETERS, rows)}
            counts = [int((r or {}).get("n_accepted", 0)) for r in rows]
            complete = all(
                r
                and int(r.get("n_nonmissing", r.get("n_accepted", 0)))
                == int(r.get("n_accepted", 0))
                and int(r.get("n_accepted", 0)) > 0
                for r in rows
            )
            expected_units = (
                "coefficient",
                "coefficient",
                "coefficient",
                "year",
                "fraction per year",
            )
            complete = complete and all(
                r.get("unit") == unit for r, unit in zip(rows, expected_units)
            )
            complete = complete and len(set(counts)) == 1 and max(counts) <= 10
            diagnostic = {
                "country": country,
                "model": model,
                "n_accepted": min(counts),
                "medians": medians,
                "scope_alignment": "UNMATCHED",
                "gap_p50": None,
            }
            rejected = [
                p
                for p, row in zip(PARAMETERS, rows)
                if row is not None and _panel_status(row) == "HELD_PANEL_STATUS"
            ]
            if rejected:
                diagnostics.append(
                    {
                        **diagnostic,
                        "medians": None,
                        "status": "HELD_PANEL_INPUTS",
                        "rejected_measures": rejected,
                        "reason": "panel source status untrusted or placeholder-derived; no numerical derivative produced",
                    }
                )
                continue
            coverage = (
                "COMPLETE_PANEL"
                if all(_panel_status(row) == "COMPLETE_PANEL" for row in rows)
                else "PARTIAL_PANEL"
            )
            if not complete or any(
                v is None or not np.isfinite(v) for v in medians.values()
            ):
                diagnostics.append(
                    {
                        **diagnostic,
                        "status": "HELD_PANEL_INPUTS",
                        "reason": "all five genuine finite input medians required; unresolved parity is not assigned a date",
                    }
                )
                continue
            if medians["price_parity_year"] <= 2026:
                diagnostics.append(
                    {
                        **diagnostic,
                        "status": "HELD_PANEL_INPUTS",
                        "reason": "panel parity at or before2026 is outside the evaluator scenario contract; date not clamped",
                    }
                )
                continue
            try:
                panel_inputs(inputs, medians)
            except ValueError as exc:
                diagnostics.append(
                    {
                        **diagnostic,
                        "status": "HELD_PANEL_INPUTS",
                        "reason": f"valid elicited value outside evaluator domain; no clamping or replacement: {exc}",
                    }
                )
                continue
            for year in YEARS:
                cell = replace(
                    inputs, rows=inputs.rows[inputs.rows.year.eq(year)].copy()
                )
                result = sm.simulate(panel_inputs(cell, medians), n=n, seed=SEED)
                result.metadata.update(
                    {
                        "panel_model": model,
                        "panel_source_hashes": {
                            name: sha256(HERE / "elicitation" / name)
                            for name in (
                                "results.csv",
                                "accepted-runs.json",
                                "scope.json",
                            )
                            if (HERE / "elicitation" / name).exists()
                        },
                        "panel_n_accepted": min(counts),
                        "panel_completion": coverage,
                    }
                )
                row = result.quantiles[
                    result.quantiles.metric.eq("value_usd_2025")
                ].iloc[0]
                directory = HELD if result.status == "SYNTHETIC" else OUT
                target = (
                    directory
                    / f"model-from-panel-inputs-{model}-{country.lower()}-{year}.json"
                )
                if write:
                    sm.write_result(result, target)
                results[(country, year, model)] = {
                    q: row[q] / 1e6 for q in QUANTILES
                } | {
                    "status": result.status,
                    "n_accepted": min(counts),
                    "panel_coverage_status": coverage,
                    "source_sha256": sha256(target) if write else "",
                }
            diagnostics.append(
                {
                    **diagnostic,
                    "status": coverage,
                    "reason": "computed conditional scenario; dairy scope mismatch holds headline gap",
                }
            )
    return results, diagnostics


def build_scenarios(inputs: sm.SimInputs, *, n: int = 10000) -> pd.DataFrame:
    """Compute paired main/stress/AI/parity/sign scenarios without overwriting Task8."""
    scenarios = {
        "main": {},
        "us_stress": {"diffusion": "us_stress"},
        "ai_2pct": {"ai_decline": 0.02},
        "ai_5pct": {"ai_decline": 0.05},
        "parity_2030": {"parity_year": 2030},
        "literal_signed": {"vegetarian_mapping": "literal_signed"},
    }
    records = []
    baseline = None
    for name, controls in scenarios.items():
        result = sm.simulate(replace(inputs, **controls), n=n, seed=SEED)
        if baseline is None:
            baseline = result.draws.set_index(
                ["country", "year", "draw"]
            ).value_usd_2025
        delta = (
            result.draws.set_index(["country", "year", "draw"]).value_usd_2025
            - baseline
        )
        for row in result.quantiles[
            result.quantiles.metric.eq("value_usd_2025")
        ].to_dict("records"):
            country, year = row["country"], row["year"]
            d = (
                np.quantile(delta.loc[(country, year)].to_numpy(), [0.1, 0.5, 0.9])
                / 1e6
            )
            records.append(
                {
                    "country": country,
                    "year": year,
                    "scenario": name,
                    **{q: row[q] / 1e6 for q in QUANTILES},
                    **{f"paired_delta_{q}": v for q, v in zip(QUANTILES, d)},
                    "unit": UNIT,
                    "status": row["status"],
                    "n_draws": n,
                    "seed": SEED,
                    "ceiling_binding_share": result.ceiling_binding_share,
                    "scope": SCOPE,
                    "assumption": (
                        "illustrative parity date"
                        if name == "parity_2030"
                        else (
                            "supplied sensitivity assumption"
                            if name.startswith("ai_")
                            else "registered diagnostic scenario"
                        )
                    ),
                }
            )
        if name in ("ai_2pct", "ai_5pct", "parity_2030"):
            directory = HELD if result.status == "SYNTHETIC" else OUT
            sm.write_result(
                result,
                directory
                / f"scenario-{inputs.rows.country.iloc[0].lower()}-{name}.json",
            )
    return pd.DataFrame(records)


def build_sobol(inputs: sm.SimInputs, *, n: int = 8192) -> tuple[pd.DataFrame, dict]:
    """Run actual deterministic country-year Sobol callbacks at n and 2n."""
    records, diagnostics = [], []
    for (country, year), rows in inputs.rows.groupby(["country", "year"], sort=True):
        cell = replace(inputs, rows=rows.copy())
        names = sm.parameter_columns(cell)
        fixed = [f"{country}:bass_p", f"{country}:bass_q"]
        fixed.extend(
            f"{country}:{factor}"
            for factor in ("urban", "income", "population")
            if rows[f"{factor}_low"].eq(rows[f"{factor}_high"]).all()
        )

        def model(cube: np.ndarray, cell: sm.SimInputs = cell) -> np.ndarray:
            """Use the shared evaluator and preserve draw order for one complete cell."""
            return sm.evaluate(
                cell, sm.map_unit_parameters(cell, cube)
            ).draws.value_usd_2025.to_numpy(float)

        runs = []
        for sample_n in (n, 2 * n):
            table = sobol_indices(model, [(0.0, 1.0)] * len(names), sample_n, seed=SEED)
            details = table.attrs["diagnostics"]
            table["parameter"] = names
            table["country"], table["year"], table["n_base"] = country, year, sample_n
            table["status"] = sm.evaluate(
                cell, sm.map_unit_parameters(cell, np.full((1, len(names)), 0.5))
            ).status
            table["factor_kind"] = np.where(
                table.parameter.isin(fixed), "FIXED_OR_INACTIVE", "UNCERTAIN"
            )
            table["rank_total"] = table.total.rank(
                method="min", ascending=False
            ).astype(int)
            records.extend(table.to_dict("records"))
            details["parameter_map"] = dict(
                zip((f"x{i + 1}" for i in range(len(names))), names)
            )
            runs.append((table, details))
        low, high = runs[0][0], runs[1][0]
        ranked_low = (
            low[~low.parameter.isin(fixed)]
            .sort_values("total", ascending=False)
            .parameter.tolist()
        )
        ranked_high = (
            high[~high.parameter.isin(fixed)]
            .sort_values("total", ascending=False)
            .parameter.tolist()
        )
        diagnostics.append(
            {
                "country": country,
                "year": int(year),
                "fixed_factors": fixed,
                "parameter_names": names,
                "runs": [v[1] for v in runs],
                "first_order_abs_change": np.abs(
                    high.first_order.to_numpy() - low.first_order.to_numpy()
                ).tolist(),
                "total_abs_change": np.abs(
                    high.total.to_numpy() - low.total.to_numpy()
                ).tolist(),
                "rank_n": ranked_low,
                "rank_2n": ranked_high,
                "top_two_set_stable": set(ranked_low[:2]) == set(ranked_high[:2]),
                "full_rank_stable": ranked_low == ranked_high,
                "convergence_certified": False,
                "interpretation": "Nested same-seed n/2n and split-half stability diagnostics; no sampling-error confidence interval or universal convergence certificate",
            }
        )
    return pd.DataFrame(records), {
        "seed": SEED,
        "n_base": [n, 2 * n],
        "csv_decimal_places": DECIMALS,
        "cells": diagnostics,
        "source_hashes": source_hashes(),
        "simulation_source_hashes": inputs.metadata.get("source_hashes", {}),
        "environment": {"numpy": np.__version__, "pandas": pd.__version__},
        "grouping": "one joint elasticity-bootstrap row per country, preserving all coefficient dependence",
        "factor_distribution": "unit-cube inverse mappings in simulate.evaluate; independent grouped factors; fixed Bass and degenerate bands have zero sensitivity by construction",
    }


def source_hashes() -> dict:
    """Bind code, registered protocol, source inventory and all consumed aggregates."""
    paths = [
        HERE / name
        for name in (
            "build_outputs.py",
            "simulate.py",
            "sensitivity.py",
            "protocol.json",
            "inputs/manifest.csv",
        )
    ]
    paths += [
        OUT / f"{name}.json"
        for name in (
            "simulation-india",
            "simulation-india-us-stress",
            "simulation-india-literal-signed",
            "holdout-summary",
            "us_calibration",
            "drivers",
            "diffusion",
            "prices_summary",
            "elasticities_national",
            "segments_summary",
        )
    ]
    paths += [
        PROXY,
        HERE / "elicitation/results.csv",
        HERE / "elicitation/accepted-runs.json",
        HERE / "elicitation/completion.json",
        HERE / "elicitation/scope.json",
        HERE / "elicitation/instrument-provenance.json",
        HERE / "elicitation/execution-scope.json",
    ]
    return {str(p.relative_to(sm.LIBRARY_ROOT)): sha256(p) for p in paths if p.exists()}


def markdown_table(table: pd.DataFrame, columns: list[str]) -> str:
    """Render a small source-bound table without an optional table dependency."""
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for values in table[columns].itertuples(index=False, name=None):
        formatted = [
            (
                "held"
                if pd.isna(v)
                else f"{v:,.3f}" if isinstance(v, (float, np.floating)) else str(v)
            )
            for v in values
        ]
        lines.append("| " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def write_report(
    comparison: pd.DataFrame,
    scenarios: pd.DataFrame,
    sobol: pd.DataFrame,
    sobol_details: dict,
    panel_diagnostics: list,
    us_calibration: pd.DataFrame | None = None,
) -> None:
    """Write a standalone methods/results paper from current computed aggregates."""
    if us_calibration is None:
        us_calibration = us_calibration_table()
    holdout = read_json(OUT / "holdout-summary.json")
    main = read_json(OUT / "simulation-india.json")
    panel_completion = read_json(HERE / "elicitation/completion.json", {})
    execution = read_json(HERE / "elicitation/execution-scope.json", {})
    selected_models = panel_completion.get(
        "active_authorized_models", execution.get("authorized_models", ["gpt-6-astra"])
    )
    selected_required = int(
        panel_completion.get("active_authorized_required", 30 * len(selected_models))
    )
    accepted = sum(
        row["status"] == "ACCEPTED" and row["model"] in selected_models
        for row in panel_completion.get("slots", [])
    )
    pending = selected_required - accepted
    n_required = int(panel_completion.get("required_for_registered_study", 60))
    headline = comparison[comparison.method.isin(["household_model", "gfi_proxy"])]
    panel_display = comparison[
        comparison.method.isin(["panel_headline", "model_from_panel_inputs"])
    ]
    leaders = sobol[(sobol.n_base == sobol.n_base.max()) & (sobol.rank_total <= 2)]
    components = pd.DataFrame(main["component_quantiles"])
    components = components[components.metric.eq("value_usd_2025")].copy()
    components[list(QUANTILES)] = components[list(QUANTILES)] / 1e6
    volume = pd.DataFrame(main["quantiles"])
    volume = volume[volume.metric.eq("volume_t")]
    inventory = pd.read_csv(HERE / "inputs/manifest.csv")
    unretained = inventory.stored_at.str.startswith("not stored")
    inventory["capture_availability"] = np.where(
        unretained, "HISTORICAL_LOOKUP_HASH_ONLY", "RETAINED_BYTES"
    )
    retained_count, lookup_only_count = int((~unretained).sum()), int(unretained.sum())
    inventory_table = markdown_table(
        inventory, ["input_id", "sha256", "capture_availability"]
    )
    stability = "\n".join(
        f"- India {c['year']}: top-two set stable = {c['top_two_set_stable']}; full uncertain-factor order stable = {c['full_rank_stable']}; maximum total-index change = {max(c['total_abs_change']):.6f}."
        for c in sobol_details["cells"]
    )
    panel_notes = "\n".join(
        f"- {d['country']}, {d['model']}: {d['status']}; accepted runs {d['n_accepted']}; {d['reason']}."
        for d in panel_diagnostics
    )
    parameter_labels = {
        "conversion": "conversion (coefficient)",
        "bass_p": "Bass p (coefficient)",
        "bass_q": "Bass q (coefficient)",
        "price_parity_year": "price parity (year)",
        "ai_cost_decline": "AI cost decline (fraction/year)",
    }
    median_inputs = pd.DataFrame(
        [
            {
                **{key: d[key] for key in ("country", "model", "n_accepted", "status")},
                **{
                    label: (
                        f"{d['medians'][parameter]:.6f}"
                        if d.get("status") in PANEL_STATUSES
                        else None
                    )
                    for parameter, label in parameter_labels.items()
                },
            }
            for d in panel_diagnostics
        ],
        columns=[
            "country",
            "model",
            "n_accepted",
            "status",
            *parameter_labels.values(),
        ],
    )
    text = f"""# Household demand, US calibration and proxy market scenarios for India and Pakistan

**Local research draft, 19 October 2026. Human scholarly review pending.** No new market estimate has been accepted into the claim ledger. This paper is a reproducible diagnostic contribution to the India-Pakistan research programme; replacing the team's D1 forecast requires separate method agreement and acceptance. These results do not measure the supply benchmark in `future-research/`.

## Abstract

This study asks what a household-based model implies for plant-based meat and liquid-milk retail value in India and Pakistan in 2026, 2030 and 2035. It combines household expenditure microdata, measured purchaser elasticities, a US conversion and spending calibration, observed retail price summaries, and official demographic and income paths. In India, the main conditional simulation produces median values of {headline[(headline.country == 'India') & (headline.year == 2026) & (headline.method == 'household_model')].p50.iloc[0]:,.3f}, {headline[(headline.country == 'India') & (headline.year == 2030) & (headline.method == 'household_model')].p50.iloc[0]:,.3f}, and {headline[(headline.country == 'India') & (headline.year == 2035) & (headline.method == 'household_model')].p50.iloc[0]:,.3f} million US dollars at 2025 prices. These are conditional diagnostic model outputs, not validated market forecasts. Pakistan's national numerical results remain withheld here because the plant-meat price input is a placeholder. Complete household protein-spending shares and the egg/fermentation residual remain missing. Leave-one-state-out validation covers reported-item spending transfer, and attains {100 * holdout['coverage_80']:.1f}% coverage for nominal 80% intervals. Elicitation coverage is {accepted} accepted runs with {pending} pending; partial model responses cannot establish a completed panel.

## 1. Research question, estimand and comparison

The estimand is annual retail value of modern plant-based meat and liquid milk in constant 2025 US dollars, converted at market exchange rates. Tonnes refer to product mass. Traditional soya chunks are an expenditure and substitution analog, excluded from modern alternative-protein market value. The meat-eating and vegetarian plant-meat channels are mutually exclusive household segments; the plant-milk channel covers both. The model does not identify trial, repeat purchase, displaced animal consumption, nutritional equivalence or producer revenue.

The comparison proxy is the existing GFI-anchored scenario series, selected only where `record_type=scenario`, `quantity=market_value` and the exact target year and quantile match. Its producer, `tools/build_altprotein_proxy.py`, fixes price year 2025. The proxy covers all plant-based retail categories; the household calculation covers meat and liquid milk. The intended egg/fermentation residual cannot be identified from available category evidence. Subtracting US meat and milk from the entire GFI total would also include cheese, yogurt and other foods. Consequently the table is a comparison of distinct estimands: a dollar difference would be misleading and is not reported. The India proxy anchor additionally treats an ambiguously dated rupee figure as nominal 2022; this remains an explicit source assumption.[^gfi]

## 2. Data and provenance

India HCES 2023-24 supplies 261,953 household records and Pakistan HIES 2024-25 supplies 30,123. These raw records remain outside the repository. Household and bootstrap hashes are bound in the simulation artifacts. The India implementation reconstructs survey-period expenditure and quantities and keeps source and recall distinctions. Both countries use leave-one-out prices in state by price-area by sector cells. The price area is district in India and PR-code geography (rural district or urban division) in Pakistan. Pakistan maps monthly and 14-day recall to a monthly basis. Official Pakistan stratum labels remain unresolved; province-stratified PSU resampling uses the actual PSUs and does not consume invented stratum labels. This is a variance caveat, distinct from the missing plant-meat price that holds Pakistan market totals.[^surveys]

The US calibration uses BLS 2023 Diary consumer units with valid food reporting, with Interview weights checked independently. Consumer units do not match households exactly, so their use as the US household calibration base adds a comparability limitation. The primary packaged-food condition remains MISCFOOD above zero, which includes miscellaneous prepared foods and is broader than the intended Indian bakery/confectionery condition. R38 requested a narrower UCC crosswalk, but R40 parked it after the BLS dictionary could not be retrieved; `buys_packaged_food_r38.status` remains NOT_DONE. This unresolved denominator mismatch affects both the inferred meat conversion and the plant-milk addressable base. It is not evidence that the two survey segments are harmonized. For meat, GFI/SPINS 2025 sales of USD 1.0 billion and penetration of 0.11, the Bryant US intention proportion 0.329, and CE addressable share 0.607223 give conversion 0.550616 and annual spending per adopting household USD 67.595968. Plant milk uses USD 2.7 billion, penetration 0.38, CE urban-packaged share 0.739612, conversion one and annual spending USD 52.831585. Its implied conditional adoption base is 0.513783. This substitutes observed US milk purchasing for an unavailable milk-intention measure. US all-category sales of USD 7.9 billion remain contextual, not the denominator for meat conversion.[^bls][^gfi][^bryant]

The Bryant India sample is disproportionately urban, educated and affluent. Its full-sample top-two purchase-intention proportion is 0.628; it is not an India national adoption estimate. Pakistan has no equivalent observed intention value and uses the registered uniform transfer between 0.329 and 0.628. The 2019 intention versus 2025 penetration timing mismatch and GFI meat category's inclusion of seafood remain unresolved. There is no independent country validation of intent-to-purchase conversion.[^bryant]

Price inputs use the captured public retail product pages and survey chicken/milk unit values. They do not establish a representative store, city or national price distribution. Plant prices captured in 2026 are deflated to 2025 with official CPI; survey references use weighted survey-period CPI. The retained World Bank capture gives 87.158448 INR/USD and 281.143001 PKR/USD in 2025. IMF October 2026 projections provide income and CPI; GDP per capita is used as an income proxy, with the US 2025 comparison held fixed. UN WPP 2024 supplies population bands. WUP 2018 census-definition urban shares are used because WUP 2025 Degree of Urbanisation categories do not match survey urban codes.[^drivers]

### Source IDs and capture availability

The manifest lists {retained_count} retained inputs and {lookup_only_count} historical lookup hashes whose original bytes were not retained. The coordinator's 19 October Stage A static recomputation audit verified SHA-256 and byte size for the 20 retained inputs. The three lookup-only records are `bryant2019_html`, `gfi_marketresearch_html` and `gfi_price_gap_png`: their recorded digests identify the original lookups, but do not establish present file availability or a fresh source-content check. Their original contents were not reverified in that audit. The table labels this distinction per source. `inputs/manifest.csv` supplies URLs, recorded lookup or capture dates, storage status, approval notes and per-input caveats. `protocol.json` and `logs/registration-receipt.json` preserve the preregistration; later deviations are enumerated in section 7. `comparison-metadata.json` and `sobol-diagnostics.json` bind the current producer, source inventory and aggregate input hashes. Protocol source IDs are distinct from claim acceptance IDs.

{inventory_table}

## 3. Household model and uncertainty

For each country, year and segment-product pair, expected value is the addressable household count multiplied by adoption probability and annual spend per adopter. Addressable households equal population divided by weighted survey household size, multiplied by the survey addressable share scaled by the urban-share path, bounded by all households. Adoption equals US-calibrated conversion times country intention times a relative-price adjustment times the Bass cumulative adoption fraction, bounded to [0,1]. Spending scales US adopter spending by the ratio of target to US real income raised to the measured income elasticity. Price and income terms require finite operands and coefficients: neutral exponent identities never turn absent inputs into known values.

Elasticities come from purchaser-only equations with fixed effects and leave-one-out cell unit values. They describe the intensive margin among recorded purchasers. They neither identify participation by non-purchasers nor remove quality bias or cell-price measurement error. Requiring all equation prices reduces the usable sample. Five hundred actual design/PSU bootstrap draws are recentered on the point estimates; one bootstrap row is sampled per country, preserving dependence among its price, cross-price and income coefficients. Failed coefficients propagate missingness, rather than being dropped from quantiles. Positive own-price coefficients are capped at zero in simulation (R25), leaving India dairy with little or no price response. This does not repair identification, and can materially change scenario response. The main India run caps {main['metadata']['positive_own_price_capped']:,} of {main['metadata']['own_price_evaluations']:,} own-price coefficient evaluations.

For vegetarian households, the negative expenditure-weighted chicken-equation cross-price coefficients on paneer, soya and pulses adjust the inverse relative premium. The same substitute basket supplies its price comparison. This is a diagnostic transfer assumption, not an estimated plant-based vegetarian own-price elasticity. The literal signed alternative is reported separately with paired random draws. Halal compliance for sold Pakistan products is assumed; it is not an estimated probability or scenario switch.

No eligible local analog time series survived the registered diffusion screen, so the main path uses the fixed Bass prior p=0.03, q=0.38. South Asian launch dates remain assumptions recorded in the protocol. The US stress scenario uses its fitted shape on each country's launch clock. The fixed prior creates no sampled diffusion uncertainty; a narrow main interval cannot be read as evidence that diffusion speed is known.[^bass]

One joint Monte Carlo uses 10,000 draws and seed 20261018. India and US intention draws use Beta(mean times n, (1 minus mean) times n), with source sample sizes 1024 and 987; a fixed inverse-CDF grid is used. Pakistan uses its registered transfer range. Driver bands are mapped by an assumed piecewise-linear quantile function through low/mid/high at coordinates 0/0.5/1. The endpoints are not claimed to be calibrated tail probabilities. Dependence among these grouped factors is assumed absent except for explicitly shared US intention and joint coefficient draws. These assumptions omit important structural, measurement, source and between-model uncertainty. Reported p10-p90 values therefore describe a conditional simulation distribution, not an 80% guarantee about future markets.

Volumes divide value by projected plant-product prices. Liquid milk uses the explicit one litre equals one kilogram convention; no protein-tonnage claim follows. The meat-eating channel is capped by 2023 FAOSTAT poultry food supply per person scaled with population, with one kilogram plant product assumed to displace one kilogram chicken product. The cap reduces value and volume together; it does not constrain the vegetarian channel. No India main or stress draw binds this ceiling. This is a supply-based plausibility bound, not observed substitution evidence.

## 4. Results and scope coverage

All values in the next table are million USD at 2025 prices. Held cells are not zero. Pakistan proxy values are retained because they come from a separate existing proxy calculation, not from the held household plant-price input.

{markdown_table(headline, ['country', 'year', 'method', 'p10', 'p50', 'p90', 'status'])}

India component results separate the modelled channels. Their medians need not sum exactly to the median of the joint total.

{markdown_table(components, ['year', 'pair', 'p10', 'p50', 'p90'])}

India product-volume quantiles, tonnes:

{markdown_table(volume, ['year', 'p10', 'p50', 'p90'])}

Neither country has a complete observed mapped protein-food basket for any household: India 0 of 261,953; Pakistan 0 of 30,123. Missing purchase observations are not assigned zero. Whole-protein monetary spending denominators and spending shares therefore remain null. The supply benchmark's grams of protein per person per day cannot supply a monetary denominator. Likewise the modelled subtotal plus the requested residual remains null. These are identification limits, not failed formatting or a zero-sized category.

### Paired scenario results

Each row below uses the same 10,000 factor draws. `paired_delta_p50` is the median of draw-by-draw differences from main, not a subtraction of marginal medians. AI declines of 2% and 5% annually are illustrative input assumptions; price parity by 2030 is an illustrative date, not a source-backed forecast. AI affects the plant price ratio and its price/volume consequences, rather than adding an arbitrary market-growth premium.

{markdown_table(scenarios, ['year', 'scenario', 'p10', 'p50', 'p90', 'paired_delta_p50'])}

The large early sensitivity to the transferred US diffusion shape shows why the fixed-prior main interval is incomplete as a total uncertainty account. The vegetarian sign comparison isolates a consequential transfer assumption. An AI price change can affect product volume even when the own-price response is capped; the inferred value response remains conditional on that cap and the cross-price mapping.

### Global sensitivity on actual model cells

Saltelli first-order and squared-difference total indices were computed from the shared deterministic evaluator for each country-year at base n=8192 and 2n=16384, eight unit-cube factors and 81,920/163,840 model evaluations per cell. Each country-year is evaluated independently with all required components retained. The largest total-effect factors for India at 2n are:[^saltelli]

{markdown_table(leaders, ['year', 'parameter', 'first_order', 'total', 'rank_total'])}

{stability}

The complete CSV retains both sample sizes, negative estimates and any first-order estimate above its total. The JSON sidecar preserves split-half differences, exact estimator settings, source hashes, fixed/inactive factors and rank diagnostics. Fixed Bass factors and degenerate urban bands have zero sensitivity by construction. Income and population effects are conditional on their chosen bands. The joint elasticity factor measures combined coefficient uncertainty; it cannot identify separate causal contributions for each coefficient. n/2n agreement is a numerical stability check, not a convergence certificate or validation of the input distributions. Pakistan calculations and their diagnostics remain in the separate placeholder-derived research directory; no Pakistan numerical sensitivity is copied into this report.

## 5. Validation and falsification limits

Leave-one-state-out validation evaluates observed-item animal spending per person per month, in survey-price INR, using demographics only: household size, urban/rural sector, religion and caste. Training-only weighted log1p regression, centering, scaling and smearing prevent heldout outcome leakage. MPCE, food quantities, unit values, segments and state effects are excluded. Within each training fold, nested heldout-state log errors supply the empirical 10th/90th interval; no outer heldout outcome calibrates its own interval.

The real run evaluates {holdout['target_metadata']['households_with_observed_items']:,} households across {holdout['states_evaluated']} states; {holdout['target_metadata']['households_with_no_observed_items']:,} households have no valid animal-item observation. All eight animal groups are observed together for zero households. State MAE is INR{holdout['mae']:.6f} per person per month; median absolute percentage error is {holdout['median_ape'] * 100:.6f}%; measured coverage is {holdout['coverage_80'] * 100:.1f}% ({int(holdout['coverage_80'] * holdout['states_with_intervals'])}/{holdout['states_with_intervals']}) against nominal 80%. The model compresses state differences and nine states miss their interval. This is informative evidence of imperfect geographic transfer.

These intervals are empirical state-transfer predictive intervals, not survey-design confidence intervals. Observed-item sums vary in coverage and cannot validate complete spending totals. The separately refitted training-fold elasticities diagnose coefficient stability; they do not drive the demographic predictions. This exercise does not validate plant adoption, the structural price response or future alternative-protein value. Temporal validation against earlier harmonized HCES rounds remains unrun pending the author's microdata registration and compatible data.

## 6. Elicitation and model-from-input comparison

The protocol requires 10 fresh contexts for each of two named models in each of three regions, 60 total. The author currently authorized Astra only: selected models {selected_models}, active requirement {selected_required} runs; Claude is deferred by the author. Current recorded active coverage: {accepted} accepted, {pending} pending; registered study size {n_required}. Completing the Astra phase does not complete the registered two-model study. The completion artifact's provider holds, attempts and individual slots are authoritative. A partly completed region/model panel remains PARTIAL_PANEL and is never described as completion. Repeated outputs of an AI model are dependent machine responses, not independent human forecasts.

The exact US questionnaire is hash-bound and stored separately because public redistribution rights are unestablished. India and Pakistan adaptations preserve explicit unresolved forecast questions and resolvable proxy questions. Project domains and project-derived estimate contamination are screened. The original US cultivated/fermentation and blind-spot questions remain intact. Public reporting remains held pending scholarly review; Anna must also be notified before the US comparison is reported outside this local draft.

Values below are million USD at constant 2025 prices; held cells are not zero.

{markdown_table(panel_display, ['country', 'year', 'method', 'source_model', 'n_accepted', 'p10', 'p50', 'p90', 'status'])}

Panel headline p10/p50/p90 summarize accepted runs' point medians. They are not pooled respondent predictive bounds. For each model separately, the adapter takes its median conversion, Bass p, Bass q, price-parity year and annual AI decline, then genuinely reruns the same evaluator with 10,000 paired draws. Conversion changes the meat and vegetarian channels; observed US-milk conversion remains its category-specific anchor. Bass and parity affect each modelled pair. The elicited AI input is a manufacturing-cost decline, while the evaluator changes retail price; this rerun explicitly assumes full retail pass-through as an extra sensitivity assumption, not a panel-endorsed or observed relationship. US-intention sampling is disabled for these reruns so the supplied fixed conversion median is not contaminated by the empirical US conversion denominator. The resulting Monte Carlo interval is conditional on fixed panel medians and is not the panel's across-run spread. An unresolved parity answer stays null and holds that rerun; a date is never invented.

The following fixed input medians come directly from the computed per-country/model diagnostics. Counts and coverage apply to all five inputs; held or unrecognized diagnostic statuses do not supply numbers. Six decimal places preserve small coefficients. These are elicited inputs, not market values; Pakistan's placeholder-derived market outputs remain withheld. AI decline retains the additional full-retail-pass-through assumption described above.

{markdown_table(median_inputs, list(median_inputs.columns))}

{panel_notes}

Only explicit COMPLETE_PANEL or PARTIAL_PANEL producer statuses may supply headline or input values. Placeholder-derived, absent or unknown source-status labels are held before publication and before any model evaluation; rejected input medians are not copied to the public summary. Coverage can downgrade an incomplete count, but never upgrades an explicitly partial panel. The elicited dairy category includes other dairy alternatives, while the household engine covers liquid milk. Therefore even a completed panel does not yield a matched-scope dollar gap. Raw headline and conditional rerun values can be inspected as separately labelled local diagnostics; the numerical gap remains null. US serves calibration/comparison only and does not become a target-market row.

### US questionnaire calibration appendix: local comparison only

The original US instrument is reported separately from the India/Pakistan target market estimates. This appendix shows its plant-based retail headline and its cultivated and fermentation questions for each requested year, keeping each original channel and scope. Values are million USD at 2025 prices. Coverage remains per model; Claude is deferred in the current Astra-only phase. Empty cells are held, not zero. Public reporting requires author notification to Anna and human scholarly review; neither notification nor approval is established here.

{markdown_table(us_calibration, ['source_model', 'label', 'year', 'channel', 'n_accepted', 'n_nonmissing', 'p10', 'p50', 'p90', 'status'])}

The plant-based headline concerns finished retail products marketed as animal-food replacements or plant-protein foods, including traditional plant-protein products. It excludes standalone upstream ingredients and unrelated whole foods. Cultivated consumer sales cover retail and foodservice and include cultivated pet food and hybrids with plant ingredients. Fermentation consumer sales also span retail and foodservice; they include functional microbial-protein hybrids and fermented dairy alternatives, while excluding long-established fermented foods, minor additives without the replacement function, ingredient-company revenue and health-purpose supplements. The original exclusions and category definitions remain in the separately supplied instrument; this appendix paraphrases scope without redistributing its text. These measures can overlap and use different channels. They are not added into a combined market total.

The table's percentiles are the empirical 10th/50th/90th percentiles of accepted runs' point medians, not respondent predictive intervals. The builder recomputes the summary from the corresponding accepted numeric records, hashes the aggregate source files, and retains the recorded answer/prompt digest fields in `us-calibration-metadata.json`. It checks those fields' presence and format; it does not reopen or rehash private raw response or prompt bytes. Raw byte-integrity verification belongs to the elicitation runner and final numerical reviewer. The original rationale and blind-spots questions remain in the instrument and local raw responses. No Anna forecast values were supplied for this comparison, so there is no Anna forecast column or forecaster-error comparison. Future outcomes remain unresolved; “calibration” describes the registered questionnaire comparison exercise, not demonstrated predictive accuracy.

## 7. Tracked methods deviations and interpretation

The frozen registration predates implementation rulings; it is preserved rather than silently rewritten. The controller ledger is not distributed with the repository, so consequential decisions are recorded here. R24 recenters bootstrap coefficients; R25 caps positive own-price draws; R26 restricts interpretation to purchasers; R27 collapses singleton design strata into the stated pooled strata; R28 uses leave-one-out cell prices; R29 records attenuation. R30-R33 define an India vegetarian addressable segment, keep no-food households unknown, and leave NFHS calibration unused until a valid crosswalk and approved data exist. R34-R39 specify category-specific US calibration and food-reporting exclusions, and requested a packaged-food crosswalk. R40 holds that R38 crosswalk unresolved; the broader MISCFOOD primary condition remains, so cross-country denominator alignment is incomplete. R41 holds main AI decline at zero; R43 propagates Pakistan price taint; R44-R46 specify intention, addressable scaling and Beta uncertainty.

| Ruling | Implemented decision | Consequence retained |
| --- | --- | --- |
| R47 | Bass p and q fixed at registered prior; US shape separate stress | Main uncertainty omits unknown diffusion spread; zero Sobol effect does not imply knowledge |
| R48 | Negative expenditure-weighted chicken cross-price transfer for vegetarian premium; literal sign separate | Vegetarian price response is a transfer assumption, not identified plant demand |
| R49 | Exact US instrument, including punctuation, hash-preserved | Source instrument fidelity takes priority over prose conventions |
| R50 | Supplied instrument and adaptations remain local and ignored | Reproduction needs separately supplied rights-bounded text; no text embedded here |
| R51 | Missing complete-basket denominator and disaggregated residual stay null | No whole-protein spending share or GFI-matched total claimed |
| R52 | Contamination guard matches complete numeric claims, plus provenance and domain controls | Arbitrary digit fragments such as Comtrade 210610 do not trigger false matches; source inspection remains necessary |
| R53 | Leakage-free demographic transfer of observed-item spending; separate training elasticity stability | No structural/adoption validation; final corrected eight-group complete-basket count is zero |

Further limitations include NFHS non-access and the zero-recall vegetarian diagnostic, limited retailer/city coverage, the unresolved MISCFOOD versus Indian packaged-food denominator mismatch, uncertain Pakistan country intention, source-price vintage ambiguity, real-income proxy choice, lack of independent baseline acceptance, and the assumed product-mass displacement and liquid density. No supplied holdout or code test resolves these scholarly questions.

## 8. Reproduction and acceptance gates

From the library root, use the existing environment and local inputs:

```sh
source '../OUTPUTS/Deep Research 2026-10/.venv/bin/activate'
python research/household-demand/build_outputs.py --n 10000 --sobol-n 8192
python -m pytest research/household-demand/tests/test_build_outputs.py -q
python -m ruff check research/household-demand/build_outputs.py research/household-demand/tests/test_build_outputs.py
python -m black --check research/household-demand/build_outputs.py research/household-demand/tests/test_build_outputs.py
python research/household-demand/synthetic.py --check
```

The default builder reads source- and code-hashed external bootstrap caches, never downloads data or changes claim acceptance. CSV values use six decimal places; Markdown tables use three. Strict JSON preserves higher precision. Empty CSV numeric cells represent missing values. `comparison-metadata.json` hashes the source files and resulting CSV; Sobol sidecars bind their analysis separately. No rounded CSV value is fed back into the simulation.

The current code/test review is distinct from the independent recomputation receipt and full library/workspace verification, which the coordinator records separately. Exact agreement at stated rounding is required for `comparison.csv` and `sobol.csv`; this manuscript does not claim that an unrun recomputation passed. Separate remaining gates are official baseline/lineage acceptance, independent empirical source reconciliation, NFHS/historical-round access, complete genuine panel coverage, team agreement before replacing D1, author-controlled US notification and human scholarly review. No email, form, message, push or publication is performed by this builder. `team-method-note.md` is a draft for the author.

## Notes

[^surveys]: Ministry of Statistics and Programme Implementation, *Household Consumption Expenditure Survey 2023-24*, source definitions and local input provenance in `households_india.py`, `codes.py` and `logs/india-households-run.json`; Pakistan Bureau of Statistics, *Household Integrated Economic Survey 2024-25*, source definitions and local input provenance in `households_pakistan.py` and `logs/pakistan-households-run.json`. Baseline acceptance remains separate from code-level parsing and reproduction.
[^bls]: US Bureau of Labor Statistics, *Consumer Expenditure Survey 2023 Public-Use Microdata*, Diary and Interview files, retained capture reviewed locally October 19, 2026, https://www.bls.gov/cex/pumd.htm. Exact source ZIP hashes and weight/food definitions appear in `inputs/manifest.csv` and `outputs/us_calibration.json`.
[^gfi]: Good Food Institute, “Plant-Based Retail Market Overview,” 2025 SPINS retail results, historical lookup recorded October 19, 2026, https://gfi.org/marketresearch/. Original HTML and price-graphic bytes were not retained; their contents were not reverified in the static audit. Recorded hashes, extracted calibration values and locators remain in the manifest and calibration artifact. Existing India anchor and proxy Source IDs: `gfi_india_smart_protein_economic_analysis_2022`, `gfi_us_plant_based_retail_2025`, `imf_weo_2026_10`, and `worldbank_wdi_official_exchange_rate_2026`, in `research/india-pakistan/data/altprotein_proxy_inputs.csv` and `altprotein_proxy_scenarios.csv`.
[^bryant]: Christopher Bryant, Keri Szejda, Nishant Parekh, Varun Deshpande, and Brian Tse, “A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China,” *Frontiers in Sustainable Food Systems* 3 (2019), article 11, https://doi.org/10.3389/fsufs.2019.00011. The registered top-two intention definition, values and sample caveat are in `protocol.json`. The manifest records the October 18, 2026 historical HTML lookup hash; its original bytes were not retained and its source contents were not freshly rechecked in the static audit.
[^drivers]: International Monetary Fund, *World Economic Outlook*, October 2026, DataMapper series NGDPDPC, NGDP_RPCH, LP and PCPIPCH, https://www.imf.org/external/datamapper/; United Nations, *World Population Prospects 2024*, https://population.un.org/wpp/; United Nations, *World Urbanization Prospects 2018*, https://population.un.org/wup/; World Bank, “Official Exchange Rate (PA.NUS.FCRF),”2025 values in the retained official capture. Exact hashes, methods and vintage exclusions are in the input manifest and `outputs/drivers.json`.
[^bass]: Frank M. Bass, “A New Product Growth for Model Consumer Durables,” *Management Science* 15, no. 5 (1969): 215-27, https://doi.org/10.1287/mnsc.15.5.215; Fareena Sultan, John U. Farley, and Donald R. Lehmann, “A Meta-Analysis of Applications of Diffusion Models,” *Journal of Marketing Research* 27, no. 1 (1990): 70-77. The prior is the pre-registered fallback; `protocol.json` records its secondary-source verification limitation and `outputs/diffusion.json` records rejected analogs and the separate US stress fit.
[^saltelli]: Andrea Saltelli et al., “Variance Based Sensitivity Analysis of Model Output: Design and Estimator for the Total Sensitivity Index,” *Computer Physics Communications* 181 (2010): 259-70, https://doi.org/10.1016/j.cpc.2009.09.018. The implementation uses ordinary pseudorandom Monte Carlo, not a low-discrepancy Sobol sequence.
"""
    (OUT / "REPORT.md").write_text(text)
    (OUT / "team-method-note.md").write_text(
        f"# Draft only: method note for Anna and Rufaro\n\n**Not sent. Human review required.** We have built a local household-demand diagnostic for India and Pakistan only, using HCES/HIES expenditure patterns, a category-specific US purchasing calibration, price comparisons and official demographic/income paths, alongside the existing GFI-anchored proxy. The household subtotal covers plant-based meat and liquid milk, so it is not yet a scope-matched replacement for D1. India remains diagnostic, Pakistan's household total is held because its plant-meat price input is a placeholder, and protein-spending shares and the egg/fermentation residual remain unavailable. The elicitation workflow uses Anna's exact US questionnaire on Claude Opus 5.5 and GPT Astra as a labelled calibration, with country adaptations; the author currently selected the 30-run Astra phase and deferred Claude. Current execution has {accepted} accepted runs and {pending} active runs pending against 60 registered study runs; completing Astra alone does not complete the two-model study. The author should notify Anna before reporting the US comparison. If the team accepts the method and the independent baseline, source and scholarly gates are met, D1 would gain a clearly scoped household estimate beside the proxy and separately labelled scenario/model-elicitation comparisons. This draft asks for method agreement; it does not record agreement or authorize sending.\n"
    )


def main(argv: list[str] | None = None) -> int:
    """Build current diagnostics locally, preserving placeholder and human gates."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=10000)
    parser.add_argument("--sobol-n", type=int, default=8192)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Refresh comparison/report using existing scenario and Sobol outputs",
    )
    args = parser.parse_args(argv)
    panel_path = HERE / "elicitation/results.csv"
    panel = pd.read_csv(panel_path) if panel_path.exists() else pd.DataFrame()
    if not args.report_only:
        inputs = {
            country: sm.load_inputs(countries=(country,)) for country in COUNTRIES
        }
        for country, source in inputs.items():
            directory = OUT if country == "India" else HELD
            scenarios = build_scenarios(source, n=args.n)
            write_csv(scenarios, directory / "scenarios.csv")
            sobol, details = build_sobol(source, n=args.sobol_n)
            write_csv(sobol, directory / "sobol.csv")
            details["csv_sha256"] = sha256(directory / "sobol.csv")
            details["simulation_source_hashes"] = source.metadata["source_hashes"]
            details["household_provenance"] = source.metadata["household_provenance"]
            write_json(details, directory / "sobol-diagnostics.json")
            print(
                f"completed {country}: {len(scenarios)} scenarios; {len(sobol)} Sobol rows",
                flush=True,
            )
        panel_models, panel_details = model_from_panel_inputs(
            inputs, panel, n=args.n, write=True
        )
        write_json(
            {
                "records": [
                    {"country": k[0], "year": k[1], "model": k[2], **v}
                    for k, v in panel_models.items()
                    if v["status"] != "SYNTHETIC"
                ],
                "diagnostics": panel_details,
            },
            OUT / "panel-model-summary.json",
        )
        write_json(
            {
                "records": [
                    {"country": k[0], "year": k[1], "model": k[2], **v}
                    for k, v in panel_models.items()
                ],
                "diagnostics": panel_details,
            },
            HELD / "panel-model-summary.json",
        )
    else:
        saved = read_json(
            HELD / "panel-model-summary.json", {"records": [], "diagnostics": []}
        )
        panel_models = {
            (r["country"], r["year"], r["model"]): r for r in saved["records"]
        }
        panel_details = saved["diagnostics"]
    comparison = comparison_table(panel=panel, panel_models=panel_models)
    write_csv(comparison, OUT / "comparison.csv")
    write_csv(
        comparison_table(
            panel=panel, panel_models=panel_models, include_placeholder=True
        ),
        HELD / "comparison-research.csv",
    )
    write_json(
        {
            "csv_decimal_places": DECIMALS,
            "source_hashes": source_hashes(),
            "csv_sha256": sha256(OUT / "comparison.csv"),
            "seed": SEED,
            "n_draws": args.n,
            "scope_alignment": "UNMATCHED: household meat+liquid-milk versus all-category proxy and broader dairy panel",
            "claim_rows_emitted": len(claim_rows(comparison)),
            "panel_numerical_public_reporting": "HELD_PENDING_HUMAN_REVIEW",
            "review_status": "human scholarly review pending",
        },
        OUT / "comparison-metadata.json",
    )
    us_table = us_calibration_table(panel=panel)
    write_csv(us_table, OUT / "us-calibration.csv")
    write_json(
        {
            "csv_decimal_places": DECIMALS,
            "source_hashes": source_hashes(),
            "csv_sha256": sha256(OUT / "us-calibration.csv"),
            "accepted_record_bindings": us_table.attrs["accepted_record_bindings"],
            "raw_answer_bytes_rehashed": False,
            "raw_prompt_bytes_rehashed": False,
            "recorded_digest_check": "Presence and SHA-256 format only; raw byte-integrity verification belongs to the elicitation runner and final numerical reviewer",
            "public_reporting": "HELD_AUTHOR_NOTIFICATION_AND_SCHOLARLY_REVIEW",
            "scope_rule": "Original US measures kept separate; no mixed-scope total; no Anna forecasts or accuracy scores",
            "summary_recomputation": "Across accepted run p50 values; compared with source summary at six decimal places",
        },
        OUT / "us-calibration-metadata.json",
    )
    write_report(
        comparison,
        pd.read_csv(OUT / "scenarios.csv"),
        pd.read_csv(OUT / "sobol.csv"),
        read_json(OUT / "sobol-diagnostics.json"),
        panel_details,
        us_calibration=us_table,
    )
    print(
        f"wrote {len(comparison)} comparison rows; accepted claims {len(claim_rows(comparison))}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
