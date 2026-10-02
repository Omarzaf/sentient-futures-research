# Phase One paper preparation

AI-assisted working draft; human verification pending.

This folder executes the [writing plan](../PAPER-PLAN.md). Start with the [execution state](execution-state.json), [review log](review-log.md) and [outline](outline.md). The [manuscript](paper.md) is a scaffold. Author approval of the completed outline is required before drafting.

The original [Phase One edition](../phase1/README.md) stays unchanged. Its source records are inputs, not freshly verified citations. Only paper audit verdicts `verified` and `verified_with_note` permit citation. The October continuation remains separately scoped; its historical agent checks do not transfer automatically.

The planned reader aids are a production-chain diagram, a country-by-layer evidence table and an audit chart whose counts come from the registers. They will show documented conditions and gaps, without invented probabilities or market forecasts.

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

Citation retrieval is a separate, explicitly invoked network step: `node tools/fetch-citations.mjs --run RUN_NAME`. It saves original bytes and retrieval receipts in ignored storage; it never promotes an audit verdict. Read the captured passages and locators before setting a verdict. The manuscript is not yet listed as a finished library document.

The capture helper rejects duplicate identities, unknown requested keys, literal IP hosts and non-public host names. It preserves the input snapshot and original bytes. This is a capture helper for the reviewed public-source list, not a general network sandbox; DNS addresses are not pinned. Offline tests replace the network and verify its integrity and decoding behavior.
