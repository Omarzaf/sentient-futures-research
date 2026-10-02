# Phase One working paper

AI-assisted working draft; human verification pending.

Read [Cultivated Chicken and Halal Market Access](index.html), or use the [auditable manuscript](paper.md). The paper has 11,851 body words, three figures and five appendices. Independent source-support, blind, adversarial, coverage and editorial checks are complete; their qualifications and corrections are recorded in the [review report](REVIEW-REPORT-2026-10-02.md). The author's final reading and qualified scholarly review remain pending.

Download the reviewed [PDF](exports/cultivated-chicken-halal-working-paper.pdf) or [editable Word document](exports/cultivated-chicken-halal-working-paper.docx). Their exact bytes are checked against the hashes in the review report; a replacement requires a new export review.

This folder executes the [writing plan](../PAPER-PLAN.md). The [execution state](execution-state.json), [review log](review-log.md) and [approved outline](outline.md) preserve the workflow. The author subsequently authorized sharing the paper source, PDF and Word on the feature branch. This authorization does not establish scholarly approval, a main-branch merge or a formal research release.

The author approved checkpoint 1 on 2 October 2026: a 103-word thesis, thirteen sections targeting 12,050 body words, Chicago notes, five appendices and three figures. It keeps all 45 comparison slots visible while limiting body assertions to admitted sources. Drivers, elasticities and feed remain outside the body; Malay and Indonesian originals remain held. Its Phase Two handoff follows the active v2 evidence dimensions without populating a numerical input or gate.

The [2 October citation audit](AUDIT-REPORT-2026-10-02.md) records an outcome for all 76 original source IDs. The subsequent [bounded supplementary research](GAP-RESEARCH-2026-10-02.md) brings the register to 95 canonical records: 63 verified with qualifications, 22 held and ten unretrieved. Country, language and full-text gaps remain explicit. Private working captures remain excluded from the repository.

The original [Phase One edition](../phase1/README.md) stays unchanged. Its source records are inputs, not freshly verified citations. Only paper audit verdicts `verified` and `verified_with_note` permit citation. The October continuation remains separately scoped; its historical agent checks do not transfer automatically.

The reader aids are a production-chain diagram, a country-by-layer evidence table and an audit chart whose counts come from the registers. They show documented conditions and gaps, without invented probabilities or market forecasts.

Run from the repository root:

```sh
node tools/build-library.mjs
node tools/verify.mjs
node tools/test-paper-checks.mjs
node tools/test-fetch-citations.mjs
node tools/test-halal-checks.mjs
node tools/test-phase1-checks.mjs
node tools/test-survey-checks.mjs
node tools/test-privacy-checks.mjs
```

Citation retrieval is a separate, explicitly invoked network step: `node tools/fetch-citations.mjs --run RUN_NAME`. It saves original bytes and retrieval receipts in ignored storage; it never promotes an audit verdict. Read the captured passages and locators before setting a verdict. Human scholarly review remains pending.

The capture helper rejects duplicate identities, unknown requested keys, literal IP hosts and non-public host names. It preserves the input snapshot and original bytes. This is a capture helper for the reviewed public-source list, not a general network sandbox; DNS addresses are not pinned. Offline tests replace the network and verify its integrity and decoding behavior.
