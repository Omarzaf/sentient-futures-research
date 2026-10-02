# Phase One paper preparation

AI-assisted working draft; human verification pending.

This folder executes the [writing plan](../PAPER-PLAN.md). Start with the [execution state](execution-state.json), [review log](review-log.md) and [outline](outline.md). The [manuscript](paper.md) is a complete local draft following the author-approved outline. Independent source support, adversarial and editorial reviews are the next gate.

The author approved checkpoint 1 on 2 October 2026: a 103-word thesis, thirteen sections targeting 12,050 body words, Chicago notes, five appendices and three figures. It keeps all 45 comparison slots visible while limiting body assertions to admitted sources. Drivers, elasticities and feed remain outside the body; Malay and Indonesian originals remain held. Its Phase Two handoff follows the active v2 evidence dimensions without populating a numerical input or gate.

The [2 October citation audit](AUDIT-REPORT-2026-10-02.md) records an outcome for all 76 original source IDs. The subsequent [bounded supplementary research](GAP-RESEARCH-2026-10-02.md) brings the register to 95 canonical records: 63 verified with qualifications, 22 held and ten unretrieved. Country, language and full-text gaps remain explicit. Work remains local at the author's request.

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

Citation retrieval is a separate, explicitly invoked network step: `node tools/fetch-citations.mjs --run RUN_NAME`. It saves original bytes and retrieval receipts in ignored storage; it never promotes an audit verdict. Read the captured passages and locators before setting a verdict. The manuscript is not yet added to the reading portal; that release-preparation step follows independent review. Human scholarly review remains pending.

The capture helper rejects duplicate identities, unknown requested keys, literal IP hosts and non-public host names. It preserves the input snapshot and original bytes. This is a capture helper for the reviewed public-source list, not a general network sandbox; DNS addresses are not pinned. Offline tests replace the network and verify its integrity and decoding behavior.
