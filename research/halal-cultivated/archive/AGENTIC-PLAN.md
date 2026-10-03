# Agentic research plan: cultivated chicken, Phase One

**Status: executed 30 September 2026; kept as a record.** The current output is the [working paper](../paper/README.md).

Revised 30 September 2026 from the author's edited local Word plan. AI-assisted working protocol; human verification pending. This replaces the earlier cloud setup, new-transcription dependencies and October Phase One schedule. Read the [30 September bounded public-source review](../phase1/review.md), its [coverage and limitations](../phase1/README.md), and the [in-progress October continuation](../phase1-continuation/README.md).

## Objective and scope

Map religious conditions, certification and market access for cultivated chicken. India, Pakistan, Saudi Arabia and the UAE remain the focal countries; Singapore, Malaysia and Indonesia are comparisons. Examine Hanafi, Maliki, Shafii and Hanbali primary accounts and Ali al-Sistani's named positions. Sistani is not a proxy for consensus across all Jafari authorities. Ghamidi's published account is a separate reference point.

The earlier [project plan](../PLAN.md) remains the reference for Phase Two demand inputs and double-counting rules. This document controls the revised Phase One method and delivery targets.

## Decisions in force

- Work locally. Cloud environment changes, model downloads and Drive uploads are not prerequisites.
- Use the existing interview only in the private working package. No new transcription, Urdu reconstruction or invented timestamps. Locate private passages by stable IDs and exact character offsets; never invent missing words or speaker identities.
- Seek English primary texts first, including identifiable translations. Use Arabic when a suitable English passage is unavailable or cannot resolve the wording. Record actual edition and translation information; hold other-language leads outside accepted findings.
- Use contextual inference where evidence is incomplete: identify premises, thematic alignment, reasoning, alternatives and what would defeat the inference. Keep it distinct from an author's explicit statement.
- Agent checking replaces the proposed human transcript and jurisprudence gates for internal research. It does not confer scholarly authority or certify translation accuracy. Mentor approval remains pending. The author subsequently authorized a public-source repository edition for review.
- Preserve original inputs. Only the coordinator edits the durable research package and repository. Public files exclude unpublished interview text and derived interpretations, Office originals, private links and raw working logs.

## Repeatable research loop

1. Frame one answerable question and the evidence that could change its answer.
2. Retrieve and read primary passages; retain short excerpts, URLs, dates and locators.
3. Extract attributed evidence and contextual inference into separate records.
4. Give a fresh checker the question and source locators without the first answer.
5. Search for counter-evidence, exceptions, later decisions and fuller texts; audit shared source families.
6. Reconcile answers, update the evidence and repeat on the next gap.

Stop a cycle at a defensible bounded answer or a clearly documented unresolved point. Continue independent work. Dates do not convert missing evidence into a fact. Two readings of one authority are not two independent sources.

## Roles and records

Run at most two specialist agents simultaneously. Extraction specialists cover primary texts, named schools, institutional rulings, countries and historical parallels. Blind checkers record their own answers before comparison. The coordinator reconciles them; the counter-evidence and independence passes test the synthesis. The writer uses accepted findings and labeled inferences without suppressing disagreement.

Evidence records identify author, source, language, passage, locator, supporting excerpt and scope. Inference records identify premises, reasoning, alternatives and the missing test. Statuses distinguish `primary_read`, `blind_agent_checked`, `agent_checked`, `inference`, `disputed` and `open`. A checked source reading can support an unresolved conclusion. Reported consensus stays attributed and bounded.

The [Phase One JSON registers](../phase1/README.md) carry these distinctions. The older CSV discovery registers and their original schema remain historical; they are not upgraded by this execution. In particular, the earlier interview CSV's timestamp and Urdu requirements are not filled with fabricated values.

## Delivery targets in the edited plan

| Target | Deliverable |
| --- | --- |
| 30 September 2026 | Local source inventory and initial evidence map; begin ready tracks |
| 30 September 2026 | School and institutional comparisons with disputes and missing passages |
| 30 September 2026 | Consolidated claims and private interview interpretation; no new transcript dependency |
| 30 September 2026 | Country comparison, historical parallels and counter-evidence pass |
| 30 September 2026 | Phase One review and Phase Two handoff with unfinished evidence explicit |

These are the five user-edited targets. Completion means complete question coverage and a usable review, not resolution of every question. Phase Two quantitative work is not represented as completed.

## Nine questions for each tradition

1. What makes food tayyib or khabith, and who decides?
2. Are the four Quranic prohibitions exhaustive?
3. How are unslaughtered animals and parts detached during life classified?
4. How are flowing blood, liver and spleen treated?
5. How does invocation operate, including deliberate omission and forgetting?
6. Which transformations purify, and what exceptions or disagreements exist?
7. How are processed serum, enzymes, gelatin and similar inputs treated?
8. Which sea animals can be consumed without slaughter?
9. How are living cells and tissue classified, and what supports the modern analogy?

Use accessible named primary works and their locators. Shamela exports can supplement missing passages, but installation or export is not a gate for accessible sources. Distinguish original text, commentary and modern footnotes. Record dissent and uncertainty without converting selected authors into whole-school agreement.

## Completion and next handoff

The local execution examined all 45 school slots, seven countries and four historical comparisons, reconciled blind readings and produced an editable Word review. The public edition contains 74 claims and 76 source records; the private original additionally retains the interview and its interpretations. The [release record](../phase1/release.json) documents this difference.

Product-specific rulings, complete current certification instruments, missing classical locators and a fully specified manufacturing dossier remain open where stated. Religious permission, purity, permission to eat, halal certification, food authorization and civil market access remain separate evidence layers. Next work should test a named process—donor, procurement, cell line, medium, scaffold, processing aids and finished product—before supplying any conditional gate to Phase Two.

Run `node tools/build-library.mjs`, `node tools/verify.mjs` and `node tools/test-halal-checks.mjs` before pushing changes. Structural checks do not certify scholarship. No autonomous background research or publication schedule is implied.
