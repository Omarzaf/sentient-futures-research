# Pakistan and India protein markets protocol

This package supports the author-approved October 2026 research brief. Human verification pending. It is a local implementation checkpoint, with no new market estimate or projection.

The target remains the full report, auditable data package and one-command rebuild of every reported number. A readiness table is not completion of that target. Unmet requirements stay open with their causes.

## Execution order

1. Preserve the author-designated elicitation instrument and its hash in private working storage.
2. Register forecast questions and commit them before any projection.
3. Acquire official survey data through authorized routes and document licences and survey designs.
4. Reproduce both official survey targets from unit-level data. Published-table transcription does not pass this gate.
5. Only after both pass, estimate expenditure denominators, demand relationships, market reconciliation and projections.
6. Verify every claim against its source and code output; run the library checks and independently review the result.

## Current command

Activate the task's Python environment. From the repository root:

```sh
python research/protein-markets-2026/rebuild.py --data-dir PATH_TO_PRIVATE_DATA --output-dir PATH_TO_PRIVATE_TABLES --hces-dir PATH_TO_HCES_CHECKOUT
```

The current command rebuilds readiness tables and both available baseline diagnostics, then returns exit code 2 for the held estimation gate. Omit the optional HCES checkout argument to inspect only the sources available in the private data directory. It makes no network calls and does not run an LLM, a supply model or a proxy projection. Empirical table builders will be added only with inspected data and a documented design. Missing inputs are reported as missing, never as zero.

Read [the protocol](PROTOCOL.md) and [the requirement register](requirements.json) for the complete scope and unresolved work. The original questionnaire and household records remain outside the shareable repository.

[Source access instructions](DATA-ACCESS.md) identify the checked official releases, the supplied cleaned-data candidate and unresolved redistribution rights.

The [household-meal research agenda](HOUSEHOLD-MEAL-AGENDA.md) contains proposed tests, not findings. The [supplementary forecast questions](forecast-questions.json) concern observable regulatory signposts and do not replace the questionnaire's sales questions. Their first local Git commit is the preregistration identity.

`prepare_elicitation.py --data-dir PATH_TO_PRIVATE_DATA` creates auditable country-substitution drafts, preserves the original currency and scope clauses, and records unresolved local-resolution choices. It calls no model. `reproduce_pakistan.py --raw-dir PATH_TO_PRIVATE_RAW --output PATH_TO_PRIVATE_RECEIPT` diagnoses the fixed public PBS release. A held baseline returns exit code 2; it is not a passing reproduction.
