# Session log: halal conditionality workstream

One entry per working session, newest first. Records what was done, what was decided, and what is still open. It contains no private links and no interview text.

## 2 October 2026: plan for the Phase One paper

**Done:** Wrote [PAPER-PLAN.md](PAPER-PLAN.md), the brief Codex follows to consolidate the Phase One registers into one thematic paper. It maps every part of Phase One to a section, sets a citation audit for all 76 sources with verdicts, adds mechanical checks and blind cross-checks, and lists 15 problems already found in the evidence (duplicate source IDs, file-sharing hosts for two English translations, consensus.app links in place of four articles, unnamed Quran translations and others).

**Decisions proposed, pending Umar:** drivers, elasticities and insect feed stay out of the paper body (D1); Malay and Indonesian rulings stay held (D2); incubator working paper of about 12,000 words with Chicago notes (D3).

**Not done:** No paper text, no source re-checks and no edits to `phase1/`. The anti-AI writing style file was not available to this session, so the plan carries a fallback list and asks for the file to be copied into `working/style/`.

## 30 September 2026 — corrections to the earlier discovery rows

**Done:** Checked the Phase One public-source edition against the first-pass registers and corrected the rows it contradicted. `certification.csv`: India and Saudi Arabia route changed from `none_found` to `statute_only` and `operational`, Singapore from `unknown` to `operational`, with notes on the UAE, Pakistan and Indonesia. `rulings.csv` and `consensus-matrix.csv`: the IIFA 265 live-donor reading withdrawn, and the MUIS monograph added. `scripture-sources.csv`: a note on Ghamidi's published treatment of flesh from a living animal. Each changed row says it was corrected and points to `phase1/review.md`.

**Note:** The corrected values rely on the Phase One review; the instruments were not re-read in this pass.

## 30 September 2026 — local execution and repository edition

**Completed:** Executed the user-edited plan, including all five delivery targets moved to 30 September. The public-source review now covers 45 school questions, seven countries and four historical comparisons. It retains 74 claims and 76 source records, blind-review reconciliation, counter-evidence, source families and explicit gaps. The full editable Word output remains local under the repository's existing Office-file exclusion.

**Decisions:** English primary texts first; Arabic fallback; contextual inference labeled; no new transcription. Agent checking serves the internal research gates, not scholarly approval. The author authorized this repository update. Unpublished interview material and its derived findings remain excluded.

**Review:** The public-source scope was checked separately from the private original. Source citation and review-lineage checks were added to the repository verifier. The earlier local 410-check validation and 17-page visual QA remain attestations of the unchanged Word package only.

**Retrospective:** Separating source reading from inference preserved unresolved questions during packaging. The earlier cloud-dependent plan no longer described the authorized work. Future releases should record the edition and exclusions before reusing validation claims.

**Still open:** Product-specific process and certification evidence, stated school/edition gaps, human scholarly review and Phase Two quantities. The earlier session below is historical; its setup requests and October Phase One dates are superseded by the revised agentic plan.

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
