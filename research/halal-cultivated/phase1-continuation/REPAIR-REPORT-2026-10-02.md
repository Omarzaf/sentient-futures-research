# Repository repair and agent handoff — 2 October 2026

**All five reviewed issues were resolved in repair commit `867fcdfca743801a203e45e2486fc3fda0c8d301`.** This report records the fixes, verification and remaining work for agents continuing from this branch. It is a repository consistency review, not completion of the research or human scholarly approval.

## Start here

- Integration branch: `codex/reconcile-phase1-updates-20261002`.
- Reviewed inputs: PR13 at `1b875a187e081a8bb6ebbeaae974fb540eb1f771` and PR14 at `fd749937d55db61bd9c8701fa38e175cc309b597`; both are parents of the repair commit.
- Read the current [plan](../PLAN.md), [v2 method](../bridge-v2/METHOD.md), [synthesis](SYNTHESIS.md) and [gate table](gate-table.md) before extending them.
- The repair was committed locally first. This report is a subsequent documentation handoff on the same branch. Fetch and inspect the branch's current commit and CI before continuing; this report does not establish a merge to main or deployment.

## Findings and repairs

| Reviewed issue | Implemented correction | Inspect |
| --- | --- | --- |
| PR14's older forecast proposal conflicted with active v2 | Retained the forecast reply as metadata. Held the mixed-sales/conventional-retail-price/OECD proxy until species, channel, mass basis, conditioning and uncertainty match. Removed unsupported upper-bound and small-effect claims. Accepted v2 schema, production inputs and synthetic example stayed unchanged. | [Plan sections 4.5.1–4.5.2](../PLAN.md), [method](../bridge-v2/METHOD.md), [crosswalk](../bridge-v2/LEGACY-CROSSWALK.md) |
| An unofficial 90% all-meat sales estimate became a demand-segment assumption | Kept the attributed historical estimate as context. It does not establish chicken demand or the share of customers requiring halal certification. India's segment reading is unverified. | [Claim P1C8-I04](claims.json), [gate table](gate-table.md) |
| Limited authority accounts became universal agreement or a global product inventory | Scoped statements to named actors and documented examples. Hypothetical profiles stay hypothetical; bounded searches do not establish global absence or consensus. | [Claims P1C8-I01 and I03](claims.json), [synthesis](SYNTHESIS.md) |
| GOOD Meat process and Saudi whole-market readings exceeded their evidence | Kept the 2023 participant caveat historical, with the exact failed condition and cross-version process match unresolved. Serum-free founder lineage needs confirmation. Saudi whole-market, certification and operative food scope remain unverified. | [Claim P1C8-I02](claims.json), [six process profiles](gate-table.json) |
| Gate validation accepted inapplicable or absent evidence and omitted profiles | Required the fixed six-profile roster, identity and source provenance; checked country/layer/actor/process applicability; required checked direct support for substantive favorable and adverse readings and nonempty support for high confidence. | [Validator](../../../tools/continuation-checks.mjs), [regression cases](../../../tools/test-continuation-checks.mjs) |

Fourteen unsupported readings were downgraded. Twenty-two claims now declare gate scope. Four previously accepted invalid inputs independently failed after repair: wrong-country/layer evidence, empty high-confidence adverse evidence, a reduced profile roster, and profiles stripped of identity/provenance. All 108 displayed gate labels, next-document descriptions and notes were checked against the JSON table.

## Evidence retained

The [source register](source-register.json) contains 188 records and the [claim register](claims.json) contains 156 claims. All claim IDs, statuses and pre-existing review links were preserved. Only inference bodies P1C8-I01–I05 were corrected; the other 151 claim bodies were retained apart from added gate scope where applicable.

`SG-LIST` was carried from the earlier source register with its original fields and a record hash; it is not a new retrieval. P1C9-S04's source-family label was corrected from an unsupported MoIAT attribution to the evidenced UAE-government attribution. All 21 earlier review records remain. `R8-INTEGRATION-REPAIR` in the [review register](reviews.json) records the bounded consistency check without promoting source status or human approval.

All 143 requirements and sixteen-country coverage remain in scope. The [coverage record](coverage.json), [agentic plan](../archive/AGENTIC-PLAN.md), accepted v2 schema, production state and synthetic fixture were unchanged by the repair. Private historical evidence stayed outside this repository handoff.

## Verification at the repair snapshot

These results apply to `867fcdf`, before this report was added. Later documentation can change file/link totals; rerun the commands below on the commit being used.

| Check | Result |
| --- | --- |
| Library validator | PASS — 13,565 checks |
| All four required fixture suites | PASS — halal, Phase One, survey and privacy |
| Continuation checks | PASS — 4,831 checks; 220 negative cases, including 29 new and all 191 previous cases |
| Bridge v2 contracts | PASS — 16 positive and 78 negative cases |
| Deterministic rebuild | PASS — five generated files byte-identical across consecutive builds |
| Private preservation audit | PASS — 690 checks, including 168 frozen Run07 files; private artifacts are not bundled here |
| Independent integration review and coordinator moderation | PASS for the bounded repair |

Run from the repository root:

```sh
node tools/build-library.mjs
node tools/verify.mjs
node tools/test-halal-checks.mjs
node tools/test-phase1-checks.mjs
node tools/test-survey-checks.mjs
node tools/test-privacy-checks.mjs
node tools/build-library.mjs
```

Compare generated-file hashes after the first and final builds; the second build must introduce no drift. Structural checks do not establish source truth, current operative law or scholarly acceptance.

## Remaining work and continuation rules

1. Keep quantitative production `blocked_missing_baseline` until a compatible versioned demand baseline is accepted. Unknown inputs and gates remain missing, including when a hypothetical gate is closed. Do not divide marginal input quantiles and label the result an output quantile.
2. Require exact actor, territory, product/process version, source role and reading support for any proposed gate promotion. Do not treat another profile's rejection as acceptance of the target profile.
3. Confirm source originals, process lineage, full normative text and operative product decisions where currently unresolved. A new document or plausible match is a candidate until checked under the recorded review process.
4. Continue the full Phase One manuscript, scope reconciliation and two full-scope reviews without dropping any of the 143 requirements or sixteen countries. Human scholarly, technical and regulatory review remain pending.
5. Preserve source lineage, earlier review records and unresolved evidence. Update the [workstream log](../../../SESSION-LOG.md) and rerun repository checks after changes.

## Moderator and retrospective

**Moderator: PASS for the five bounded repairs.** No blocking repair issue remained. Missing baseline, unfinished research and human review are explicit outstanding work, not approvals inferred from green checks.

**Worked:** explicit evidence scope and independent invalid-input probes caught unsupported transfers. **Did not work:** existence-only reference checks and an older calculation plan allowed incompatible evidence and assumptions to appear usable. **Proposed practice:** check evidence applicability and input-version compatibility before accepting gate readings or calculations. No global rule or research-acceptance policy was silently changed.
