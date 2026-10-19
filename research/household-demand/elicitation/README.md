# Independent forecast elicitation

This module implements the approved 60-response design: ten fresh contexts for each of two exact models in India, Pakistan and the US. Implementation readiness and actual completion are separate. `completion.json` is the authoritative accepted/pending ledger; raw failures are retained outside Git. `results.csv` must not be presented as a completed study unless all six panels have ten accepted responses.

The original US instrument and country adaptations are ignored local inputs because public redistribution rights are not established. `instrument-provenance.json` binds the original DOCX and unchanged 22,419-byte US text. No complete source text is embedded in the code or tests. Public evidence packs contain short attributed summaries only; `source-provenance.json` preserves capture hashes and explicitly weaker catalog-only verification. Exact questionnaire availability is required for execution, but its test is skipped in a public checkout without the private source.

Each attempt has a fresh empty temporary working directory, no resumed session and no prior answers. Claude has only WebSearch and WebFetch enabled, restricted mode, explicit system instructions, no user/project settings and no MCP servers. Codex disables shell, project instructions, memories, apps, skill discovery and delegation, uses read-only sandboxing and audits provider events. Codex has no demonstrated end-user blanket tool allowlist; any observed command/file/MCP/delegation use is rejected. This limitation is recorded in each receipt. Requested model and provider-reported model are distinct; absent identity metadata stays absent. Models are not substituted.

Raw prompts, provider events, answers, parsed results and immutable attempt receipts live under workspace `OUTPUTS/Household Demand 2026-10/elicitation/raw/`. A nonaccepted attempt is quarantined logically through its receipt and never summarized. Source contamination, missing years, invalid units, nonfinite values, incoherent categories and nonmonotone quantiles trigger bounded fresh retries. Provider capacity and execution errors stop that model queue immediately. A lock prevents accidental overlapping runners. Inspect its PID before manually recovering a stale lock.

`accepted-runs.json` retains numeric responses, sources and hashes without questionnaire or raw rationale text. CSV rows preserve model and region; p10/p50/p90 are empirical percentiles across run medians, not pooled respondent uncertainty, human-expert disagreement or calibrated probability coverage. The original response quantiles remain in accepted-runs. Null parity remains unknown/never and is never coerced to zero. `scope.json` defines units and the material difference between all dairy alternatives in the questionnaire and milk-only model calibration.

Activate workspace `OUTPUTS/Deep Research 2026-10/.venv` before Python. Existing dependencies only.

```sh
python research/household-demand/elicitation/elicit.py --models gpt-6-astra --regions us india pakistan --runs 10
```

Current user instruction is "just do astra for now". execution-scope.json authorizes Astra only and defers Claude; the runner enforces that selection. The active target is 30, while completion.json preserves all 60 registered slots and checkpoints after each attempt.

A one-attempt preflight adds `--max-new-attempts 1`. The explicit `--resume-limits` flag retries a held provider only after capacity or the execution route has been resolved and execution is authorized. Maximum validation attempts per slot default to three; process timeout defaults to 900 seconds. No CLI fallback, paid gateway, key setup, account creation, outreach or publication is performed. A rejected automatic approval review is not permission to use a different execution route.

Current local reporting remains held for scholarly review; public reporting of the US comparison also needs prior author/team notification. This runner does not send it.
