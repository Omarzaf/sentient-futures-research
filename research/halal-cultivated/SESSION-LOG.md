# Session log: halal conditionality workstream

One entry per working session, newest first. Records what was done, what was decided, and what is still open. It contains no private links and no interview text.

## 30 September 2026

**Done**

- Formatted the interview transcript into numbered segments (`TR-01` to `TR-25`) and wrote an English translation with a confidence rating per segment. Both are in the team Drive, not in this repository. The source was a TurboScribe English rendering of the Urdu, so the Urdu is still to come from the audio.
- Wrote the Phase 1 literature review (Drive) on the foundations, rulings, schools and consensus.
- Added first rows to five registers: scripture sources, rulings, consensus matrix, madhhab geography, certification. Added 24 sources. See PR 7.
- Wrote the [agentic research plan](AGENTIC-PLAN.md) for running Phase 1.

**Decisions**

- The review maps positions and tests agreement. It does not say whether cultivated meat is halal.
- The test case is donor slaughter versus live biopsy. Istihalah and fetal bovine serum are secondary tests.
- Schools covered: Hanafi, Maliki, Shafi'i, Hanbali, Ja'fari, with Ghamidi as a fifth reference point.
- Only dated statements from named institutions enter `rulings.csv`. Undated, individual or single-source statements stay in the review.
- Scripture quotes use one named English translation, with hadith collection and grading. Nothing is marked `verified`.
- No claim rows and no Ghamidi column in the repository matrix until the audio gives timestamps and Urdu text.

**Limits of this session**

- Direct page fetches were blocked for every host tried, so all rows come from search summaries and abstracts. Statuses are `partially_verified` or `unverified`.
- The speech-model host was blocked, so the audio (10 min 48 s) is not yet transcribed.

**Open**

| Item | Owner | Needed for |
|---|---|---|
| Add the research hosts under Network access, starting with `huggingface.co` | Umar | Transcript, primary-text checks |
| Choose how to transcribe: cloud after the allowlist change, or on a Mac | Umar | Wave 1 |
| Decide whether Arabic primary texts become a second source exception (recommended) | Umar | School positions |
| Name an Urdu-literate reviewer and a jurisprudence reviewer | Umar | Gates G1 and G2 |
| Export the Shamela books listed in the agentic plan and confirm they installed | Umar | Wave 2 |
| Say what the Harvard library guide covers | Umar | Source list |
| Upload the anti-AI writing style file to Drive | Umar | Style audit |
| Write the agent prompts as files in `research/halal-cultivated/agents/` | Claude | Wave 0 |
| Log this session in the Umar Operating System sheet (needs the Sheets connector) | Claude | Record |

**State**

Branch `claude/eager-mayer-ccy675`, draft PR 7, checks passing. Phase 1 target end date is 28 October 2026.
