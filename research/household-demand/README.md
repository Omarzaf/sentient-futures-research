# Household-demand diagnostic

Local India-Pakistan research model, calibrated on the US. Human scholarly review and official baseline acceptance remain pending. The measured output is retail value of plant-based meat and liquid milk, with product tonnes; this is distinct from the protein-supply benchmark in `future-research/`.

Read [the standalone report](outputs/REPORT.md) for data, equations, results, deviations R47-R53, validation, source footnotes and acceptance gates. [The frozen protocol](PROTOCOL.md) and [machine-readable registration](protocol.json) preserve the original design. Later implementation deviations are recorded in the report, not silently backdated into the registration.

## Reproduce locally

From the library root:

```sh
source '../OUTPUTS/Deep Research 2026-10/.venv/bin/activate'
python research/household-demand/build_outputs.py --n 10000 --sobol-n 8192
python -m pytest research/household-demand -q
python -m ruff check research/household-demand
python -m black --check research/household-demand
python research/household-demand/synthetic.py --check
```

The existing local HCES/HIES parquets, official captures and bootstrap caches must be available under the parent workspace's `OUTPUTS/Household Demand 2026-10/`. The builder uses existing source/code-hashed bootstrap caches and does not download data, contact providers, install dependencies or grant acceptance. Changing estimator/source hashes may require genuine bootstrap recomputation. Household records and raw retailer captures are not copied into this repository.

Task8's six reviewed main, US-stress and literal-sign simulation artifacts are consumed unchanged. The builder generates paired AI2%, AI5% and illustrative2030 parity artifacts, both-sample-size actual Sobol tables, comparison tables and a report. Numerical CSV values use six decimal places; empty cells mean missing, never zero. JSON keeps full precision. Both Sobol sample sizes and all unclipped signs are retained with convergence/ranking diagnostics and source hashes.

`--report-only` refreshes comparison/prose from already computed artifacts. It does not perform new panel reruns; use the full command after new accepted panel results arrive. The coordinator separately records full-library checks and the independent recomputation receipt. A successful builder is not scientific acceptance.

## Boundaries

- India estimates remain diagnostic. Pakistan household totals depend on a placeholder plant-meat price and stay under `synthetic/outputs/`; ordinary comparison rows are null with an explicit reason. Pakistan's independently produced existing proxy remains visible.
- Household meat-plus-liquid-milk, all-category GFI proxy, and broad-dairy panel scopes differ. No scope-matched numerical gap or fabricated egg/fermentation residual is emitted.
- Complete protein-food monetary denominators are unavailable without zero-filling missing records. Shares remain null. Supply grams cannot replace a spending denominator.
- Panel outputs are machine elicitation, separated by named model. Across-run point-median spread differs from predictive uncertainty. The active phase is author-approved Astra only; Claude is deferred, so the original60-run study is not complete after30 Astra runs.
- A genuine model-from-panel-inputs rerun fixes each model's median conversion, Bass p/q, parity year and AI decline. It disables US-intent variance to avoid reintroducing US conversion uncertainty; unresolved inputs or values outside the engine's supported domain stay held. Manufacturing-cost decline to retail-price decline assumes full pass-through and is explicitly a sensitivity assumption.
- `claim_rows()` only permits explicit ACCEPTED, HUMAN_REVIEWED rows with a review identifier, source IDs, source SHA-256 and finite value. This builder emits zero new accepted claims and never writes the claim ledger.

The [team note](outputs/team-method-note.md) is a draft only. No message, publication, push or D1 replacement is implied.
