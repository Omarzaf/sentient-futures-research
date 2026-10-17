# Pakistan and India protein markets protocol

This package supports the author-approved October 2026 research brief. Human verification pending. Complete observed-data baseline attempts now run, with dynamic acceptance and explicit method qualifications. No new market estimate or projection is accepted.

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
python research/protein-markets-2026/complete_research.py --data-dir PATH_TO_PRIVATE_DATA --output-dir PATH_TO_PRIVATE_COMPLETION_EDITION --hces-dir PATH_TO_HCES_CHECKOUT
```

The current command rebuilds source tables, the complete physical/monetary India candidate reconstruction, Pakistan's all-channel comparator and independent SPSS check, the dynamic acceptance result, criterion outcomes, claim ledger, Markdown report/opening and PDFs. Exit2 records a genuine failed prerequisite; execution or source-integrity failures are errors. The earlier `rebuild.py` remains the source-table/component diagnostic command. The completion command runs offline and calls no model. Missing or unmeasured results are explicit; matching a target does not authenticate raw lineage or establish a variance design.

The public CPI capture and official SPSS archive, fixed specifications and public-literature fallback captures are under the private data directory's `baseline-completion-20261016/`. Acquisition receipts preserve URLs, dates and hashes; raw respondent files remain private. The report build needs Pandoc, Poppler, ReportLab and R with its `foreign` package for the independent SPSS reader, alongside the existing pandas/NumPy/PyArrow environment. Exact installed versions are recorded with the completion receipt.

Read [the protocol](PROTOCOL.md) and [the requirement register](requirements.json) for the complete scope and unresolved work. The original questionnaire and household records remain outside the shareable repository.

[Source access instructions](DATA-ACCESS.md) identify the checked official releases, the supplied cleaned-data candidate and unresolved redistribution rights.

The [household-meal research agenda](HOUSEHOLD-MEAL-AGENDA.md) contains proposed tests, not findings. The [supplementary forecast questions](forecast-questions.json) concern observable regulatory signposts and do not replace the questionnaire's sales questions. Their first local Git commit is the preregistration identity.

`prepare_elicitation.py --data-dir PATH_TO_PRIVATE_DATA` creates auditable country-substitution drafts, preserves the original currency and scope clauses, and records unresolved local-resolution choices. It calls no model. `reproduce_pakistan.py --raw-dir PATH_TO_PRIVATE_RAW --output PATH_TO_PRIVATE_RECEIPT` diagnoses the fixed public PBS release. A held baseline returns exit code 2; it is not a passing reproduction.

[Market-source review](market/README.md) and [original halal-source chapter](halal/README.md) preserve attributed observations and explicit gaps. The additional source audits do not pass the official reproduction gate.

`verify_report.py --data-dir PATH_TO_PRIVATE_DATA` checks the listed numerical checkpoint findings against source/producer hashes, saved outputs, Markdown and the rendered PDF. It is read-only and does not certify the missing empirical estimates or qualified scholarly review.
