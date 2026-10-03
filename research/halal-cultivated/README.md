# Halal conditionality for cultivated meat

Under which religious, certification and regulatory conditions could cultivated chicken enter India, Pakistan, Saudi Arabia and the UAE, and what share of the meat market could it reach if those conditions are met? AI-assisted working draft; human verification pending. Not mentor-approved.

## Current output

[Cultivated Chicken and Halal Market Access](paper/index.html) is the working paper, prepared on 2 October 2026 with three figures and five appendices. Read the [auditable Markdown](paper/paper.md), the [MMM reading edition](../../presentations/halal-mmm/index.html) or the [independent review report](paper/process/REVIEW-REPORT-2026-10-02.md). The author's final read and human scholarly review remain pending.

## Evidence behind the paper

| Folder | What it holds |
| --- | --- |
| [phase1/](phase1/README.md) | The 30 September Phase One review: 74 public-source claims, 76 source records, 45 school questions, seven countries and four historical comparisons |
| [phase1-continuation/](phase1-continuation/README.md) | The October continuation: country institutions, manufacturing dossier, elasticities, feed, history, and the [synthesis](phase1-continuation/SYNTHESIS.md) and [gate table](phase1-continuation/gate-table.md) for each focal country |
| `paper/process/` | The paper's [approved outline](paper/process/outline.md), [citation audit](paper/process/AUDIT-REPORT-2026-10-02.md), [supplementary research](paper/process/GAP-RESEARCH-2026-10-02.md), [review log](paper/process/review-log.md) and [review report](paper/process/REVIEW-REPORT-2026-10-02.md) |

## Phase Two method

- [Project plan](PLAN.md): scope, shared keys with the demand-forecast workstream, and double-counting rules.
- [Quantitative contract v2](bridge-v2/METHOD.md), its [schema](bridge-v2/schema.json) and [legacy crosswalk](bridge-v2/LEGACY-CROSSWALK.md). A [synthetic example](bridge-v2/synthetic-example.json) tests the arithmetic; the [production state](bridge-v2/production-state.json) keeps missing inputs null, so production stays blocked.
- [Pilot feedback](bridge-v2/PILOT-FEEDBACK.md) from 1 October ([HTML](bridge-v2/PILOT-FEEDBACK.html)): proposed next steps, not an adopted protocol change.
- [datapackage.json](datapackage.json) versions the active contract and keeps the field definitions for the archived discovery tables.

Unknown evidence is kept separate from scenario assumptions. Surveys cannot stand in for sales penetration. Value shares need an explicit price conversion before they multiply mass. Missing or incompatible capacity leaves feasible quantity null.

## Archive

[archive/](archive/README.md) holds the 30 September discovery-pass tables and their 24-source register, kept for lineage and still validated, plus the executed agentic and paper plans. Phase One and the paper supersede the discovery rows for the questions they cover.

## Checks

`node tools/verify.mjs` checks the archived tables against `datapackage.json`, the v2 contract, Phase One, the continuation and the paper's citations. Every legacy scenario row is rejected, so the old rules cannot become production numbers. `node tools/test-halal-checks.mjs` runs the discovery-table rules and the adversarial v2 suite. Passing checks do not certify the evidence.

## Private material

The interview transcript and translation (`TR-` segments) are someone else's unpublished work. They stay in private storage and are referenced only by segment ID. Session history is in the repository [session log](../../SESSION-LOG.md).
