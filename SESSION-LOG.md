# Session log: repository curation

One entry per repository-curation session, newest first. This log describes the clean file tree, not private branches or local workspaces.

## 1 October 2026 — pilot feedback revision

Revised the [pilot feedback](research/halal-cultivated/bridge-v2/PILOT-FEEDBACK.md) and regenerated its [HTML version](research/halal-cultivated/bridge-v2/PILOT-FEEDBACK.html). The India supply reconciliation is now one row of the gate table rather than a separate recommendation. Reconnecting to India–Pakistan moves to second, so the baseline test follows a chosen bilateral question. References to the uncommitted Sprint 0 pilot report (section names, item numbers, its hash and the exact India figures) are removed; the donor-procurement point now cites the Phase One review. Recommendations lead with the action. They remain proposals, not adopted protocol changes. Source registers, numerical inputs and contract behavior are unchanged.

## 1 October 2026 — pilot feedback branch

Added a separate [review](research/halal-cultivated/bridge-v2/PILOT-FEEDBACK.html) and [Markdown version](research/halal-cultivated/bridge-v2/PILOT-FEEDBACK.md) on `codex/pilot-feedback-20261001`, based on `26a3581`. Recommendations concern separate acceptance gates, one concrete decision/baseline handoff, transparent country reconciliation, targeted scholarly calibration, claim readiness and the India–Pakistan contribution. They are proposals, not adopted protocol changes or human approval. Source registers, numerical inputs, contract behavior and research acceptance states are unchanged.

Independent review found no blocking corrections. Pushed to `origin` at `a189f2a`; no PR or publication at that point.

## 1 October 2026 — quantitative contract v2

Implemented the approved pilot's local method repairs. The active v2 contract separates evidence from scenario assumptions, rejects survey substitution and incompatible dimensions, preserves unknown gates, and leaves feasible quantity unestimated without compatible allocated capacity. A crosswalk preserves earlier meanings; all eleven legacy CSVs remain byte-identical. Numerical production remains blocked by the missing compatible demand baseline. The worked example is synthetic.

Verification: 7,626 library checks; 16 positive and 78 adversarial v2 cases; all four existing regression suites pass. Private tool/runtime paths now fail the actual publication-manifest boundary. Rebuild stability is checked separately at the final handoff. Research interpretations and human approvals are not certified by these tests. Local commit only; no push or publication is implied.

## 1 October 2026 — survey package and shareable-boundary repair

**Done:** Promoted the alternative meat survey data package to a first-class library entry, added survey-specific validation for nine studies and 29 findings, and added privacy-detector fixtures so public URL paths with home/reference words are not mistaken for local home paths. Clarified that the shareable artifact is the clean checked file tree, not full Git history or private archive branches.

**Validation repair:** Environment-file exclusions now reject suffixed variants as well as the base environment filename. Privacy fixture totals are counted from executed assertions. The full library verifier passes 6,060 checks; survey validation and all regression fixtures pass.

**Preserved:** Survey JSON, machine CSVs, workbook-export CSVs, underlying source URLs, evidence values and unresolved caveats remain intact. Halal Phase One literature leads remain leads only; no claim, school-question or gap record was upgraded.

**Still open:** Human source review, scholarly or mentor approval, live URL checks, respondent-level survey access, and any public-release history sanitation are outside these local packaging checks.

## 2 October 2026 — Claude / MMM repository handoff

The author requested a repository branch containing the local handoff so Claude can begin the HTML build. Added [the handoff entry point](handoffs/claude-mmm/START-HERE.md), full prompt, actual MMM design source, figure plan, content contract and verification checklist on `codex/claude-mmm-handoff`, based on paper commit `3aa03d4`. The paper, PDF, Word, evidence and figure files are reused unchanged at their canonical paths. The intended future output is `presentations/halal-mmm/`.

Independent review: PASS; sixteen canonical inputs match the base commit, 47 copied-file hashes match provenance, and all required design files and five CSS imports resolve. The verifier and all six workflow suites passed. Final manifest verification and a stable rebuild are required before commit. Privacy guards, binary exceptions, research source counts and evidence status remain unchanged. [Review and retrospective](handoffs/claude-mmm/REVIEW-2026-10-02.md).

This prepares the authorized feature-branch push. It does not build or deploy the final HTML, merge into main, or establish human scholarly approval. No new private raw evidence, ZIP or Git metadata is included in the handoff.
