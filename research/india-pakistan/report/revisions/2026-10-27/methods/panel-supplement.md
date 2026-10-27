# Separate forecast-elicitation supplement

**AI-assisted methods draft, 22 October 2026. Human verification pending. Authored for Muhammad Umar Zafar. This is a separate protocol and sample, not an accepted joint result.**

## 1. Purpose and limits

The exercise records repeated model-generated projections under specified prompts and execution conditions. It can describe within-workflow repetition and between-workflow disagreement. It cannot establish forecast calibration, independent expert opinion, causal effects of AI on food demand, or why a provider's outputs differ from another's.

The approved target was ten accepted responses per requested model and region: two models across India, Pakistan and the US, giving six cells and 60 accepted responses. All registered cells reached ten accepted responses. “Complete” describes that target, not scientific acceptance.

## 2. Instrument and country scope

The US questionnaire preserves the author-designated source text received for this execution. The source DOCX and derived text hashes are retained. Byte agreement proves provenance of this supplied version; it does not prove that every run in another study used exactly that prompt, background material or software. The original instrument and regional adaptations are local private inputs because public redistribution rights are not established.

| Arm | Outcome and product scope | Conditioning |
|---|---|---|
| India/Pakistan | Retail plant-based meat/seafood replacements; all dairy alternatives; other in-scope plant-based replacement products. Headline excludes fermentation and cultivated technologies, conventional staples and foodservice. | Country-adapted questions plus frozen public evidence summaries. |
| US | Original broad all-category plant-based retail question. Separate cultivated and fermentation questions retain their original retail/foodservice and pet-food inclusions. | Original questionnaire; no added project market figures in the US evidence pack. |

Forecast years are 2026, 2030 and 2035. Headline unit is **million USD at constant 2025 prices**. Regional category medians must sum to headline medians; marginal tail quantiles are not required to sum. All dairy alternatives in the questionnaire are broader than the milk-only calibration used in a separate household simulator. Results must not be relabelled as milk-only or as that simulator's validated inputs.

The regional instrument also requests stated-intent conversion, Bass coefficients, price-parity conditions, AI-attributed manufacturing-cost decline and separately defined trade/listing/external-estimate proxies. Those variables have different units and resolution conditions; none is a substitute for measured headline retail demand. The India/Pakistan national headline is presently unresolvable from a complete observed series. A null parity year denotes the stated unknown/never condition, not zero. AI manufacturing-cost decline is not retail pass-through. A “first legal sale” question is distinct from a sales total.

## 3. Evidence selection and possible anchoring

Country evidence packs were frozen on 19 October 2026. India includes the external GFI/Deloitte estimate and forward scenarios, conventional household consumption context, sample-specific stated-intent research, trade-proxy limitations and policy context. Pakistan includes conventional household context, an upstream trade observation, the same non-Pakistan intent comparison, and explicitly identified India-only external estimates. Neither pack includes project household-model results, internal price ratios, project market forecasts or unit-record data.

The packets themselves disclose that some cited sources rely on earlier catalogue review rather than a fresh freeze-day retrieval. An empty Comtrade capture means missing data, not zero trade. Upstream protein concentrates and listing counts are not alternative-protein retail sales. The GFI forward scenarios may anchor respondents; their broader technology scope differs from the regional headline.

The US evidence file does not receive the added regional facts. Therefore “all runs had the same evidence pack” is false across regions. Similar isolation rules also do not establish equal executed retrieval. Evidence-conditioned elicitation differs from a blank-slate protocol that omits supplied historical observations and external forecasts. This exercise does not isolate that effect and is not a controlled experiment on evidence provision.

## 4. Execution, model identity and dates

Requested model labels were `gpt-6-astra` and `claude-opus-5-5`. Every accepted Claude receipt reports `claude-opus-5-5`. Accepted Astra receipts have an empty `reported_models` field; their identity is documented as requested, **not independently confirmed by provider-returned model metadata**. Different service names do not establish independent architectures or independent evidence.

| Requested model | Accepted-run time window, UTC | Accepted cells |
|---|---|---|
| gpt-6-astra | 19 October 2026, 18:40:58–19:50:24 | Ten India, ten Pakistan, ten US |
| claude-opus-5-5 | 20 October 2026, 19:15:23 to 21 October 2026, 15:12:55 | Ten India, ten Pakistan, ten US |

Each attempt uses a fresh temporary working directory, no resumed conversation and no prior model answers. Claude is configured with WebSearch/WebFetch, restricted mode, an explicit system instruction, no user/project settings and an empty strict MCP configuration. Codex is configured to disable shell, project instructions, memories, apps, skill discovery and delegation, and to use read-only sandboxing with provider-event auditing. The runner documents that Codex has no demonstrated blanket end-user tool allowlist; observed prohibited command/file/MCP/delegation use is rejected. These are implementation and configuration claims, not proof that every possible contamination route was absent.

The retained receipt audit establishes configured web access for completed recorded attempts. It does **not** establish that all runs executed the same searches, fetched the same pages or had equivalent tool behavior. Search parity requires a separate event-level extraction and is not asserted here. Prompts, provider events and answers stay private; their hashes and sanitized metadata can support integrity checks without redistributing their contents.

## 5. Attempts, exclusions and protocol change

The receipt inventory contains **79 recorded attempts**, not 79 demonstrated completed model calls:

| Requested model / region | Accepted | Rejected | Execution error | Incomplete RUNNING record |
|---|---:|---:|---:|---:|
| Astra / India | 10 | 0 | 0 | 0 |
| Astra / Pakistan | 10 | 0 | 0 | 0 |
| Astra / US | 10 | 0 | 0 | 0 |
| Claude / India | 10 | 7 | 1 | 0 |
| Claude / Pakistan | 10 | 0 | 1 | 0 |
| Claude / US | 10 | 8 | 1 | 1 |
| **Total** | **60** | **15** | **3** | **1** |

Seven rejected Claude India receipts cite a first-sale-year validation rule. Six Claude US receipts cite an unapproved reported model, and two cite JSON parsing. The three execution errors are retained separately. The RUNNING record lacks a command receipt; its existence alone establishes neither a sent call nor completion. No attempt is retroactively renamed accepted to make the design look cleaner. `data/panel-attempts.csv` contains sanitized record states, model identities, dates, reason categories and receipt/parsed hashes.

On 20 October, a parser amendment allowed a cultivated first-sale year accompanying a “no” answer to be normalized to null. The original supplied year is retained as `cultivated_conditional_year_dropped`. Before that amendment, seven of eleven Claude India attempts had been rejected for this condition alone, compared with zero of the thirty Astra attempts. Previously rejected receipts remained rejected. Ten accepted responses per cell therefore do not imply equal selection mechanisms. The amendment, failures and retries may affect the accepted distributions; this supplement does not estimate that selection effect.

The runner validates units, finite values, year coverage, monotone quantiles, category coherence and prohibited source/tool contamination. It retains failures and uses fresh retries. Configuration defaults include bounded validation attempts and a 900-second timeout; actual slot histories can exceed one default batch through continuation. The attempt table, not a default-limit description, is the executed count record. No rerun was performed for this drafting task.

## 6. Aggregation and retained results

For each model, region, measure and year, the summary takes each accepted response's stated P50 and computes empirical percentiles across those run medians. It does **not** pool all response P10/P50/P90 values into one predictive distribution. Original quantiles are retained in the numeric response archive. Missing conditional values are excluded for that measure and `n_nonmissing` is reported; missingness is not filled with zero.

Sort the run medians as `x[0]…x[n−1]`. For fraction `q`, let `h=(n−1)q`, `i=floor(h)`, `j=min(i+1,n−1)`; return `x[i]+(x[j]−x[i])(h−i)`. For ten nonmissing runs, the median is the mean of the fifth and sixth ordered values, P10 is `0.1×first + 0.9×second`, and P90 is `0.9×ninth + 0.1×tenth`.

For a purely illustrative ordered set of ten run medians `1,2,…,10`, this rule gives P10=1.9, P50=5.5 and P90=9.1. These example numbers explain the interpolation; they are not study results or a model's own predictive quantiles.

| Region | Requested model | 2035 P10 of run medians | Median of run medians | P90 of run medians |
|---|---|---:|---:|---:|
| India | Astra | 324 | 370 | 422 |
| India | Claude | 84.2 | 157.5 | 190.7 |
| Pakistan | Astra | 27.6 | 37 | 60 |
| Pakistan | Claude | 7.96 | 9.35 | 15.32 |
| US | Astra | 10,500 | 10,650 | 11,000 |
| US | Claude | 6,880 | 7,000 | 7,320 |

All values are million USD at 2025 prices; each cell has ten accepted, nonmissing headline medians. These are descriptive workflow outputs, **not calibrated predictive intervals**. No provider weights or grand pooled median are introduced. The India/Pakistan panel excludes fermentation whereas the proxy model includes it; their differences cannot be attributed solely to model optimism or evidence conditioning. The US arm remains in this separately authored methods supplement and does not expand Umar's main regional chapter into a US research claim.

## 7. Relationship to other forecasting studies

Any comparison requires the other study's executed-method record and author approval. Product scope, prompts, supplied evidence, execution date, tool use, model identity, number of submissions and aggregation can all differ. An envelope formed from minimum P10 and maximum P90 is not the same statistic as percentiles of repeated-run medians. An internally aggregated submission must not be counted as several equivalent observed runs.

A terminology decision after execution cannot change those differences. Discuss compatible summaries side by side with their definitions; do not pool them into a larger supposedly independent panel. This package contains no collaborator draft, private result table or claim of another author's approval.

## 8. Reproduction, rights and acceptance

Run `python scripts/reproduce.py` from the package root to reconstruct the **headline table** from `data/panel_runs.json`. The packaged `scripts/build_panel.py` implements the linear quantile rule above; it checks all six ten-run cells and rejects invalid units, duplicate slots and non-finite, negative or crossed quantiles. The reproduced 18 summaries are compared with `data/reference_panel_aggregates.json` at absolute tolerance 1e-12. This route uses only the Python standard library and no private answers, questionnaire text, provider logs, credentials or new model calls.

The complete elicitation is not independently rerunnable from a public package while questionnaire rights remain unresolved. An integrity hash does not grant redistribution rights. Retain original records privately and state this reproducibility boundary. Publicly proposed rows and metadata still require a content/rights review and human verification.

No other author's acceptance or agreement is claimed. Human factual/code review, author approval and source-specific release review are outstanding. Joint inclusion requires a separate editorial decision. Source pointers and hashes are recorded in the companion claim map and provenance files.
