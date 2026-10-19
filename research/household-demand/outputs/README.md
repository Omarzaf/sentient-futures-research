# Household-demand outputs

Start with [REPORT.md](REPORT.md), a standalone diagnostic paper with methods, sources, results and limitations. Human scholarly review remains pending. [team-method-note.md](team-method-note.md) is a draft only and has not been sent.

| Artifact | Meaning |
| --- | --- |
| `comparison.csv` | Four methods per India/Pakistan year; model elicitation stays separate by named model. Pakistan household values and unsupported comparisons remain null. |
| `comparison-metadata.json` | Producer/source hashes, exact CSV hash, six-decimal rounding, seed and acceptance boundaries. |
| `scenarios.csv` | India main, US stress, AI2%/5%, illustrative2030 parity and literal-sign scenarios with paired draw-difference quantiles. |
| `scenario-india-*.json` | Full-precision aggregates and source provenance for additional AI/parity cases. |
| `sobol.csv` | Actual India country-year indices at base8192 and16384; unclipped sampling error and fixed factors retained. |
| `sobol-diagnostics.json` | Saltelli estimator settings, source/household hashes, split-half differences and n/2n rank diagnostics. No convergence certificate. |
| `panel-model-summary.json` | Genuine rerun summaries or explicit missing/unsupported-input holds, with per-model coverage. |
| `holdout.csv`, `holdout-summary.json` | Real observed-item demographic spending-transfer validation; not full-basket or adoption validation. |
| `simulation-india*.json` | Reviewed main, US-stress and literal-sign Task8 outputs, preserved by the Task12 builder. |

All monetary comparison/scenario values use million USD at2025 prices; simulator JSON values use USD at2025 prices. Product volume uses tonnes with an explicit liquid-density convention. Empty CSV numeric cells are missing. Components can have different marginal medians from their joint total.

The ordinary report and tables do not expose placeholder-derived Pakistan market values or sensitivity indices. They are retained in `../synthetic/outputs/` for bounded research and reproducibility. The publication guard scans this folder and the claim ledger. Raw microdata, exact rights-bounded instruments, retailer captures and bootstrap caches stay outside the publication outputs.

Rebuild from the library root after activating the existing environment:

```sh
python research/household-demand/build_outputs.py --n 10000 --sobol-n 8192
```

A new accepted panel batch requires a full rebuild to produce genuine conditional reruns. `--report-only` refreshes prose/tables from saved results and cannot substitute for those evaluations. Full-library verification and independent exact-rounding recomputation remain separate coordinator receipts.
