# Pilot feedback: turn the checkpoint into a research decision

1 October 2026 · Codex review, revised the same day · AI-assisted; human verification pending.

**Assessment:** the next deliverable should be one short India–Pakistan section built on the v2 contract, not more tooling or more countries. The pilot's best result is the repaired quantitative contract and the way it keeps unresolved evidence unresolved. What it lacks is a decision for that contract to serve.

These are proposals. They are not an approved protocol amendment or a new empirical finding. They review the code at `26a3581`. The Sprint 0 pilot checkpoint that prompted the review is not committed to this repository, so this version cites only files that are; where a point depends on the pilot run itself, it says so. Read the [active method](METHOD.md), [blocked production state](production-state.json) and [legacy crosswalk](LEGACY-CROSSWALK.md) alongside it.

**Recommended order:** split the gates (1), pick one India–Pakistan question (2), test a baseline for that question (3), put one interpretation to reviewers (4), then measure claim readiness and tool benefit (5).

## 1. Split the single blocked status into four gates

**High priority.** Production reports one status, `blocked_missing_baseline`, but at least four separate things are blocked, and each blocks a different decision. One status hides which work can still go ahead.

| Gate | Decision it blocks | Work that can go ahead | Evidence needed to close it |
| --- | --- | --- | --- |
| Tool comparison | Claims that one research tool beats another; routine adoption of a candidate tool | Standalone lookup results, disclosed as such | A real comparator, frozen matched tasks and effort accounting |
| Country precision | Calling India's reported and reconstructed supply totals reconciled; reusing a rounding tolerance | Source value, reconstruction, gap and precision status shown side by side | Precision documentation for that data release, or a method justified before it is applied |
| Scholarly calibration | Accepting or scaling the disputed procurement reading (see 4) | Exact passages, competing readings and targeted questions | Qualified reviewer feedback on an exact version |
| Demand and supply inputs | Any production estimate; feasible quantity also needs capacity | Tested contract and an exact missing-input handoff | Compatible baseline, reference market, scoped gate evidence and allocated capacity |

The India row comes from the pilot run, which found a small gap between the reported and reconstructed supply totals. Keep both numbers and the gap in separate columns. The gap is a reconciliation result. It is not evidence of extra consumption or of cultivated demand, and supply is not intake, purchases or adoption. Until the precision basis is documented, treat nearest-rounding as a sensitivity and record the reconciliation as partial. This gap does not block any current decision, so it belongs here as one row rather than as a recommendation of its own.

**Do it through a prospective amendment.** Keep the original blocked result and the current authorization boundary until the amendment is accepted. A missing comparator does not invalidate a checked source identity, and a working comparator would not supply a demand baseline.

**Test:** for any piece of planned work, a reader can name the gate it waits on, or see that it waits on none.

## 2. Pick one India–Pakistan question for the next deliverable

**High priority.** The [current scope](../../../CURRENT-SCOPE.md) puts the bilateral [India–Pakistan brief](../../india-pakistan/india-pakistan-brief.md) first and the halal work second. The India supply example and the international institutional cases test the workflow. They do not yet add to the bilateral question, and without one, the baseline search in 3 has nothing to aim at.

Write one short comparative section that answers a single approved question. Include an evidence table, a note on comparability and an explicit Pakistan gap where the evidence runs out. Before collecting a second national number, check that definitions, year and denominator allow the comparison. If they do not, present the two observations separately.

**Test:** a reader can say what the comparison shows, what it cannot show and what observation would change the conclusion. This does not authorize adding countries or new retrieval.

## 3. Test baseline feasibility for that question

**High priority.** [production-state.json](production-state.json) lists four reason codes: `missing_baseline`, `missing_reference_market`, `unresolved_gate` and `missing_capacity`. Its Pakistan 2030 scenario is synthetic. Neither it nor the India supply example is a first real quantitative application.

For the question chosen in 2, write a one-page brief naming the decision, country, segment, product, year, channel, denominator and intended output. Say whether the output is a supply description, a conditional scenario or an adoption forecast. Then list candidate baselines with:

- source and version, and whether the figure is observed or forecast
- finished-product units and price basis
- any acceptance, access or supply mechanism already built in
- permitted transformations
- a specific pass or fail reason against [the method](METHOD.md)

Name the reviewer role and the capacity input the output would need.

**Test:** a reviewer can decide whether a candidate fits the contract without guessing its denominator or conditioning. If none fits, deliver the blocked-input handoff or pick a separately approved descriptive output. Do not relabel broad market totals or survey willingness as the missing sales baseline.

## 4. Ask reviewers to decide the donor-procurement question

**High priority.** The [Phase One review](../phase1/review.md) leaves an open tension. IIFA's living-donor wording and MUIS's certification discussion, which describes slaughtered permitted animals, set different procurement conditions, and the review's detached-part precedent bears most directly on that point. It is the best next calibration target because the answer changes how any process would be assessed. Asking reviewers to look over the whole package would bury it.

Send the full applicable texts with authority and version, the exact passages, the competing readings and the manufacturing facts each reading needs. Keep process verification, religious interpretation and civil regulatory review separate. Both current process profiles are hypothetical, and changing medium assumptions does not show that either complies.

**Test:** the reply states, for an exact version, which wording is accepted, which is rejected, what process evidence is required, the institutional scope and what remains open. A general endorsement does not close the gate. Contacting anyone is a separate, human-authorized step.

## 5. Measure claim readiness, then tool benefit

**Next priority.** Counts of units processed and outputs produced measure activity. Bibliographic checks, institutional interpretation and reproduced arithmetic do not add up to a percentage of scientific completion.

For each claim selected for the next section, record the assertion, exact locator, source-family dependence, independent check, contrary evidence, review status and the decision it supports. A register of principal summaries is not a full inventory of every assertion in the linked reports. Keep agent checking and human acceptance separate.

If the tool comparison resumes, use held-out substantive questions, manually adjudicated relevance, extraction-error scoring, usable full-text yield and observed effort. Recovering DOIs that were supplied in advance tests known-item lookup. It does not measure discovery coverage or synthesis quality. Keep failed trials and reconstructed logs, but put engineering detail after the research argument.

## Counterargument

A controlled pilot should meet its frozen gates before scaling, and relaxing them after seeing results moves the goalposts. I agree. That is why 1 keeps the original blocked outcome and proposes a transparent amendment rather than a relabel. An unavailable comparison is not a successful experiment, and agent checking is not scholarly approval.

Clearly labeled local preparation can continue where authorized. Numerical production and any interpretive expansion that depends on it stay gated.

## Review status

These recommendations have not been adopted as research policy. Keep the existing safeguards: source lineage, unknown values, product, process and institution scope, once-only adjustments, capacity limits and independent negative tests. Technical consistency and scientific acceptance remain separate judgments.
