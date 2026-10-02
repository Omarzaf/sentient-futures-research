# Phase One paper: writing plan for Codex

Version 1, 2 October 2026. AI-assisted working plan for Muhammad Umar Zafar; human verification pending. Not mentor-approved.

This plan tells Codex how to turn the completed Phase One evidence into one paper, check its own work, and show that every citation exists and says what the paper says it says. It covers all of Phase One as defined in [PLAN.md](PLAN.md) section 6 and the [revised agentic plan](AGENTIC-PLAN.md). Codex reads the whole plan before starting any stage. To begin, give Codex the section 11 preamble with N set to 0, followed by the stage 0 addition.

## 1. The paper

Working title: Cultivated Chicken and Halal Market Access: Religious Conditions, Certification and Food Authorization across Five Legal Traditions and Seven Countries.

### Argument

Whether cultivated chicken can reach Muslim consumers as halal food is not one question. It splits into six, and different authorities answer each:

1. Donor and procurement: is the source animal acceptable, and how were the cells taken?
2. Culture inputs: are blood, serum, enzymes or other inputs impure or prohibited?
3. Transformation: does any step count as a legally consequential change of substance?
4. Category and edibility: is the resulting food in a permitted category?
5. Certification: will a halal certifier certify this product?
6. Food authorization: will a food regulator allow it to be sold?

The Phase One evidence supports a conditional, process-specific account. It does not establish one rule shared by every school, a halal certificate for any named product, or a product authorization in any focal country. The paper shows where each disagreement sits along the production chain and what evidence would settle it for a named product.

### Readers and form

Mentors and peers in the Sentient Futures incubator first, written so it can later be adapted for a journal in religion and food policy. Defaults, pending decision D3: about 12,000 words of body text (range 10,000–13,000) plus appendices; Chicago notes-bibliography footnotes, as in the [India–Pakistan brief](../india-pakistan/india-pakistan-brief.md); transliteration and spelling as in the [Phase One review](phase1/review.md).

### What it is not

Not a fatwa or product ruling, not a forecast, not a systematic review and not a scholarly certification. Agent checks do not replace a qualified jurist. These limits belong in the abstract and the method section, not only in a disclaimer.

### Files Codex creates

| Path | Contents |
| --- | --- |
| `research/halal-cultivated/paper/paper.md` | The canonical manuscript |
| `paper/outline.md` | Argument map and section plan (stage 4) |
| `paper/source-register.json` | Every source the paper may cite: canonical key, aliases, full bibliographic record, audit verdict |
| `paper/citation-audit.json` | One audit record per source (section 7) |
| `paper/claims-added.json` | New claims the paper needs (`P-` IDs), same fields as `phase1/claims.json` |
| `paper/coverage.json` | Every Phase One record and where it appears, or why it is left out |
| `paper/search-log.json` | Gap-closure searches: date, terms, hosts, result, including `none_found` |
| `paper/allowlist.json` | Acknowledged phrase-scan warnings, each with a reason |
| `paper/review-log.md` | Cross-check rounds, findings and resolutions |
| `paper/README.md` | Status, scope and how to run the checks |
| `tools/paper-checks.mjs`, `tools/test-paper-checks.mjs` | Mechanical checks (section 9) and their fixtures |
| `tools/fetch-citations.mjs` | Network step for the audit, using Node's built-in `fetch`; page captures go to `working/` only |

Fetched pages, blind-check packets, the style file and Word or PDF renderings stay in `working/`, which Git ignores. `tools/verify.mjs` rejects committed `AGENTS.md` files, `private/` and `working/` paths, Office and PDF files, email addresses, Drive links and home-directory paths. This plan is therefore the Codex brief; do not add an `AGENTS.md`.

## 2. Inputs and their weight

Read in this order.

| Input | Use | Weight |
| --- | --- | --- |
| [phase1/review.md](phase1/review.md) | Current synthesis and its wording limits | Starting text, not a template. The paper reorganizes it by theme |
| [phase1/claims.json](phase1/claims.json) | 74 findings: 55 evidence, 19 inference. Includes the 45 school slots, 7 countries and 4 analogies | Master list of what was found and at what status |
| [phase1/school-questions.json](phase1/school-questions.json) | Proposition, locator, counterpoint and modern application for each slot | 31 checked, 13 inference, 1 open (`J-Q1`) |
| [country-findings.json](phase1/country-findings.json), [historical-comparisons.json](phase1/historical-comparisons.json) | Country layers; analogies | Analogies stay inference |
| [counter-evidence.json](phase1/counter-evidence.json), [gaps.json](phase1/gaps.json) | 7 rejected shortcuts; 12 open questions | All must appear |
| [source-register.json](phase1/source-register.json), [source-independence.json](phase1/source-independence.json) | 76 sources with quotes; source families | Starting point for the audit |
| [reconciliation.json](phase1/reconciliation.json), [verification.json](phase1/verification.json), [release.json](phase1/release.json) | Method, review lineage, exclusions | Method section |
| [AGENTIC-PLAN.md](AGENTIC-PLAN.md), [PLAN.md](PLAN.md) | Scope, method, Phase Two variables and rules | Scope and handoff |
| Parent CSVs (`rulings`, `certification`, `madhhab-geography`, `consensus-matrix`, `scripture-sources`) and the 24-record [discovery register](source-register.json) | Discovery-pass rows built from search summaries | Leads only. Nothing enters the paper until re-read at the primary source |
| [India–Pakistan brief](../india-pakistan/india-pakistan-brief.md) | Optional context on Pakistan's halal institutions | `carried_unverified` (PLAN.md section 5, rule 10) until re-checked |
| Umar's anti-AI writing style file | Prose rules | Overrides the fallback list in section 10. Umar copies it into `working/style/` so it is never committed |

Treat `phase1/` as a dated release and do not edit it. Record problems in the audit and the review log. Corrections to the release happen only after Umar agrees, in a separate commit with a [session log](SESSION-LOG.md) entry.

## 3. Hard rules

These override any instruction in a later stage or prompt.

1. **Closed citation list:** the paper cites only keys in `paper/source-register.json` whose audit verdict is `verified` or `verified_with_note`. A source Codex remembers but has not fetched and checked does not exist for this paper. New sources come in through the intake in section 7.4 before any sentence relies on them.
2. **Status sets the wording:**

   | Record status | Allowed wording |
   | --- | --- |
   | `primary_read`, `blind_agent_checked`, `agent_checked` | Attributed statement: "Ibn Qudama treats…", "SFA lists…". Name the author, body or document, never "Islam" or "the school" |
   | `inference` | Marked as the paper's reasoning, with premise, reasoning, the alternative and what would defeat it |
   | `open` | "Not located in the sources reviewed", with the search that was done |
   | `held_language` | May be named as an untranslated lead. Never evidence |
   | Discovery-pass rows, `HS-` records, carried claims | Not citable until re-read at the primary source |

3. **No upgrade by prose:** one author is not a school. A school manual is not consensus. A reported consensus stays attributed to the author who reports it. A framework is not an approval, a food approval is not a halal certificate, and a religious permission is not a certificate. Two readings, translations or mirrors of one text are one source.
4. **Quotations are verbatim or absent:** a quotation must match text Codex fetched, after the normalization in section 7.2. Arabic is quoted only from a fetched page. No quotation is reconstructed or translated from memory.
5. **Missing stays missing:** a search that finds nothing goes in `search-log.json` with date, terms and hosts, and is reported as `none_found`, never as absence of a ruling.
6. **Private material stays out:** nothing from the unpublished interview, its transcript, translation or interpretations, private links or working logs. The published Ghamidi essay is the only Ghamidi source.
7. **No approvals claimed:** the paper never states or implies scholarly, mentor or institutional endorsement, and Codex never sets a review flag to true.
8. **Stop rather than guess:** if a fetch is blocked, a page is a JavaScript shell or a locator cannot be found, record `not_retrieved` and move on. Search-result snippets are not a substitute; relying on them is what left the discovery pass unverified.

## 4. Covering all of Phase One

Phase One is defined twice: PLAN.md section 6 (five documents) and AGENTIC-PLAN.md (nine questions, five traditions, seven countries, historical parallels). The paper covers both.

| Phase One component | Evidence now | Paper | Work before writing |
| --- | --- | --- | --- |
| Nine questions across five traditions | 45 slots: 31 checked, 13 inference, `J-Q1` open | §5–8, Appendix A | Audit |
| Ghamidi's published framework | `G01`, `G02` | §5, §8 | Audit |
| Quran and hadith anchors (6.3, public part) | `T01`, `T02`; 12 provisional scripture rows | §2, §5, §8 | Name the English translation for every verse; only `Q6` and `Q6121` record one. Report hadith grading as attributed |
| Contemporary rulings (6.4B) | IIFA 198, 210 and 265 and MUIS checked; Mufti WP Irsyad 595 and JAKIM MKI 128 held in Malay; KMF 2025 and JAKIM 2025 known only from news | §9.1 | Track B1 |
| Consensus matrix (6.3) | 16 provisional cells from search summaries | §9.2 | Rebuild from checked rulings only (B1) |
| Prior scholarship | 8 `HS-` articles (Hamdan 2018 and 2024, Kashim 2020 and 2022, Miswanto 2023, Baserat 2024, Alzeer 2025, Alqurashi 2026); four link only to consensus.app summaries | §3 | Track B2 |
| Historical parallels (6.4A) | 4 bounded analogies, all inference; `historical-parallels.csv` empty | §10 | None for the four. Other PLAN.md 6.4A candidates are listed as untested, not argued |
| Madhhab geography (6.5) | 7 discovery rows: 6 unverified, 1 partly verified | §9.3 | Track B3 |
| Certification and food routes (6.5) | 7 checked country accounts; 7 discovery-pass certification rows, some corrected on 30 September | §9.4, Appendix B | Audit; certification rows only after re-check |
| Counter-evidence, independence, gaps, handoff | All present | §11, §12, Appendix C | Audit |
| Production process background | `GOOD-DOSSIER`, `SG-LIST` | §2 | Track B4 |
| Interview transcription, translation and claims (6.1–6.3) | Private | Excluded. §4 states that unpublished material is outside this edition | None |
| Drivers and elasticities (6.4C), insects as feed (6.4D) | No records | Named in §11 as Phase Two inputs not yet collected | Decision D1 |

Gap-closure tracks run in stage 3. Each is limited to one working session, stops at a bounded answer or a logged gap, and audits every new source before use.

- B1, rulings: search the bodies PLAN.md 6.4B lists as still to locate: Al-Azhar and Dar al-Ifta (Egypt), MUI (Indonesia), JAKIM, Pakistan's Council of Islamic Ideology, the Islamic Fiqh Academy (India) and Darul Uloom Deoband. Use each body's own site and one scholarly index. Accept only a dated statement issued by the body. GOOD Meat's 2023 scholar advice (`HS-013`) is a company release about private scholars and can only be cited as that. Malay and Indonesian texts wait on decision D2.
- B2, prior scholarship: resolve each `HS-` article to its DOI and publisher page through the Crossref API; match title, first author, year and journal; check for retraction or correction notices; read the passages the paper uses. Drop any that fail. Add at most five further peer-reviewed sources, each found through Crossref or a publisher index.
- B3, madhhab geography: for the seven countries: an official school where a constitution or statute names one (constituteproject.org or the official gazette), predominant schools and main fatwa bodies from a named, dated source. Categorical only, with no percentages (PLAN.md section 5, rule 9).
- B4, production chain: up to three sources describing cell sourcing, banking, media, scaffolds and harvest. Start with `GOOD-DOSSIER` and `SG-LIST`, then add one peer-reviewed review found through Crossref.

## 5. Structure

The review is arranged by source type. The paper is arranged by the six questions along the production chain, so each finding appears where it changes the analysis. The school-by-school answers move to Appendix A.

Figure 1, an inline SVG drawn by hand with no external assets, places the production stages (donor, biopsy or slaughter, founder cells, cell bank, culture medium, harvest, processing, product) against the six questions.

| § | Section | Content | Records | Words |
| --- | --- | --- | --- | --- |
| | Abstract | Question, sources, result, limits | | 250 |
| 1 | Introduction | Why the question decides market access and the Phase Two gate; the six questions; contribution; roadmap | `R01`, `R02`, `C-*`, `I03` | 800 |
| 2 | Production and legal vocabulary | Production stages; maytah, tayyib and khabith, dhabiha and tasmiya, istihalah and istihlak, impurity and prohibition | `GOOD-DOSSIER`, `SG-LIST`, B4; terms from `HAN-D`, `SIS-EN`, `IIFA198`, `IIFA210` | 900 |
| 3 | Prior scholarship | What earlier studies conclude, where they merge layers or rest on one school, and what this paper adds | B2 | 800 |
| 4 | Sources and method | Questions, traditions, language policy, extraction, blind checks, reconciliation, status labels, independence, counter-evidence, exclusions, AI use | AGENTIC-PLAN, reconciliation, verification, source-independence, release | 900 |
| 5 | Donor and procurement | Detached-part doctrine in five accounts and Ghamidi; invocation; IIFA's living-donor clause; MUIS on slaughter and egg embryos; founder line versus descendant biomass | `*-Q3`, `*-Q5`, `*-Q9`, `S01`, `S03`, `G01`, `G02`, `T02`, `R01`, `R05`, `I01`, `H04`, CE1–2 | 1,300 |
| 6 | Culture inputs | Blood, liver and spleen; serum, enzymes, gelatin and rennet; IIFA 198 then 210; residual bovine serum albumin in the GOOD Meat dossier; the SFA serum-free entry; Sistani's gelatin answers | `*-Q4`, `*-Q7`, `S06`, `H02`, `H03`, CE4, CE5, CE7 | 1,200 |
| 7 | Transformation | Istihalah by authority; wine to vinegar; what a process must show | `*-Q6`, `S02`, `S04`, `S05`, `H01`, CE3 | 1,000 |
| 8 | Category and edibility | Who decides tayyib and khabith and whether disgust counts; whether the four prohibitions are exhaustive; aquatic exceptions and why they do not transfer | `*-Q1`, `*-Q2`, `*-Q8`, `T01`; `J-Q1` open | 800 |
| 9 | Certification and food authorization | 9.1 institutional positions; 9.2 rebuilt consensus table; 9.3 school geography; 9.4 seven countries by layer | `R01`–`R06`, B1, B3, `C-IN` to `C-ID`, CE6 | 1,600 |
| 10 | Historical analogies as tests | What each of the four analogies tests and where it breaks | `H01`–`H04` | 800 |
| 11 | Discussion | Shortcuts the evidence rejects; the two competing readings; which Phase Two fields (`H_rel`, `L`, `L_includes_halal`, `cert_route`) the evidence can and cannot fill; the product dossier a ruling would need | CE1–7, `I01`, `I03`, PLAN.md 4.3–4.5 | 1,200 |
| 12 | Limitations | Selection, language, mirrors and editions, agent checking, no scholarly review, regulatory freshness | gaps, release | 450 |
| 13 | Conclusion | | | 300 |
| A | 45-slot matrix | School by question: short answer, status, note | school-questions | table |
| B | Countries by layer | Food route, halal layer, product evidence, gap, candidate Phase Two values | country-findings | table |
| C | Open questions | `gaps.json` in one shape, plus new gaps | gaps, search-log | table |
| D | Source audit summary | Counts by verdict and host type; edition notes | citation-audit | table |
| E | Glossary | | | |

`*-Q3` means the five slots `HN-Q3`, `M-Q3`, `S-Q3`, `HB-Q3` and `J-Q3`. CE1–CE7 number the counter-evidence records in file order. In §11, every candidate Phase Two value is labeled inference with the document that would confirm it, and the gate `G` stays unset for every focal country.

### Traceability in the manuscript

Each substantive paragraph ends with a trace comment that GitHub does not render:

```
<!-- trace: HN-Q3 M-Q3 S01 gap:G2 | kind: evidence -->
```

Claim IDs are bare; gaps take `gap:`, counter-evidence `ce:`, added claims `P-`. Kinds are `evidence`, `inference`, `mixed`, `gap` and `framing`; a framing paragraph makes no factual claim and has no footnote. Footnote definitions end with their register keys in brackets, for example `… vol. 6, 310–11. [HAN-D]`. Raw IDs never appear in the prose.

## 6. Stages and gates

Work on branch `codex/phase1-paper`, open a draft pull request after stage 0 and commit at the end of each stage. Before every commit run `node tools/build-library.mjs`, `node tools/verify.mjs`, `node tools/test-halal-checks.mjs`, `node tools/test-phase1-checks.mjs` and, from stage 0 on, `node tools/test-paper-checks.mjs`. CI runs the same and fails if the build changes tracked files. Stages 2 and 3 need web access; run them where Codex has network access enabled.

| Stage | Work | Gate |
| --- | --- | --- |
| 0. Scaffold | Create the files in section 1. Write `paper-checks.mjs` and its tests (section 9) and call it from `verify.mjs`. Add `paper/source-register.json` to the register list in `build-library.mjs` and to the register count in `verify.mjs`. Do not add the paper to `library.json` yet | All checks pass; each new rule rejects a broken fixture |
| 1. Consolidate | Build `paper/source-register.json` from the Phase One register with one canonical key per passage and its aliases, plus full bibliographic fields: author, title, translator, editor, publisher, place, year, volume and page, host, URL, accessed. Build `coverage.json` for all 74 claims, CE1–CE7, the 12 gap records and all 76 sources. Start the problem list from section 13 | Every record mapped to a section or excluded with a reason |
| 2. Audit citations | Run section 7 on every source. Re-check each claim in `claims.json` against the passage it cites | Every source has a verdict. Claims resting only on uncitable sources are flagged in `coverage.json` for rewording or removal. Summary in the review log |
| 3. Close gaps | Tracks B1–B4 | Every search logged; every new source audited; new claims in `claims-added.json` with a status |
| 4. Outline | `outline.md`: thesis in 120 words or fewer; for each section its one-sentence claim, the records it rests on, the strongest objection and where the paper answers it, and a paragraph plan | **Umar checkpoint 1:** outline and decisions D1–D3 approved. No drafting before this |
| 5. Draft | Write §5–10 first, then §11–12, then §2–4, then §1, the abstract and §13. Run the paper checks after each section and fix failures before moving on. Generate Appendices A, B and D from the registers by script so the tables cannot drift from the data | Full draft; all checks pass; word counts in range |
| 6. Cross-check | Section 8, in rounds | A full round finds no blocking findings and no unjustified major ones |
| 7. Release | Generate the bibliography from `paper/source-register.json`. Add the paper to `build-library.mjs` and raise the document count in `verify.mjs` from 7 to 8. Link it from the [workstream README](README.md) and the main README table. Add a session-log entry. Render Word and PDF copies with pandoc into `working/` for mentors | **Umar checkpoint 2:** final read. Merge only after his approval |

## 7. Citation legitimacy

### 7.1 Checks for each source

1. Exists: the URL resolves. Record final URL, HTTP status, content type and retrieval time. A JavaScript shell, login wall or error page is `not_retrieved`.
2. Identity: title, author or issuer and date on the page match the record.
3. Locator: the cited section, ruling number, page or paragraph exists.
4. Passage: the register's `short_exact_quote` occurs at that locator after normalization.
5. Support: read in context with its qualifications, the passage supports each claim that cites it.
6. Bibliographic record: complete for the source type (7.3).
7. Host: issuer, publisher or recognized digital library. Copies of in-copyright books on file-sharing sites are not linked; the footnote cites the print edition.
8. Archive: look up or request an Internet Archive snapshot and record its URL. Not blocking.
9. Family: assign the source family and confirm that no claim counts two members of one family as independent support.

### 7.2 Normalization

Unicode NFC; collapse whitespace; unify straight and curly quotation marks and dash variants. For Arabic, also remove harakat (U+064B–U+0652), the superscript alef (U+0670) and tatweel (U+0640); map أ إ آ ٱ to ا and ى to ي. A match after normalization is a match. A paraphrase is not. Extract PDF text with whatever tool is installed locally and add no repository dependency.

### 7.3 Rules by source type

| Type | Sources | Citable when | Footnote |
| --- | --- | --- | --- |
| Classical Arabic text on a digital library (islamweb, islamicbook.ws, taqrib.ir) | `H1`–`H3`, `H5`, `H6`, `S1`, `S3`–`S7`, `M-*`, `H-MUGH-*`, `H-MUBDI`, `H-TAY-IST`, `H-INS-BLOOD` | Passage found; work, author, volume and page as displayed. Cross-check one passage per work against a second library such as Shamela or OpenITI. Identify the print edition where the host names it | Author, title, editor and publisher if established, volume and page as displayed, host. Say "edition not established" where that is true |
| English translation of a classical work | `H4` (studylib.net), `S2` (dokumen.pub), `M-RIS29` (IIUM), `H-UM-*` (umdatalfiqh.com) | Translator and edition identified from the publisher or a library catalogue, and the passage matches. If the edition cannot be confirmed, quote from the Arabic instead and mark `verified_with_note` | Translator, title, publisher, year, section. No link to file-sharing copies |
| Quran | `Q5`, `Q6`, `Q6121`, `Q7` | Surah and verse, with the translation named | Translation named once in a note on sources |
| Hadith | `AD2858` | Collection, book and number in both numbering systems; grading stated as displayed and attributed | |
| Religious rulings and releases | `IIFA265`, `IIFA-AR`, `IIFA198`, `IIFA210`, `MUIS2024`, `MUIS-BOOK`, `J1`–`J10` | On the issuer's own domain, with resolution number, session and dates. Arabic and English versions are one family | |
| Regulators and statutes | `IN2017`, `PK2016`, `SA-*`, `AE-*`, `SG-*`, `MY-HALAL`, `ID221` | Issuer's domain, official gazette or FAOLEX, with instrument number, date and version. Re-retrieve and record any change since 30 September 2026 | |
| Applicant dossier | `GOOD-DOSSIER` | FDA-hosted, described as the applicant's own account | |
| Published essay | `GHAMIDI` | Publisher's site, translator named | |
| Peer-reviewed article | `HS-006` to `HS-012`, `HS-024`, new | DOI resolves; Crossref metadata matches title, authors, year and journal; no retraction. A summary page (consensus.app or similar) is never the citation | |
| News and press releases | `HS-004`, `HS-005`, `HS-013`, `AE-2025` | Only as evidence that the outlet or company said something, attributed. Never as the ruling it reports | |
| Forums and question sites | `HS-014`, `HS-015` | Not cited | |

### 7.4 New sources

Find through a logged search (Crossref query, issuer site search or library catalogue), fetch, write the full record with a short exact quote, audit, then cite. Never add a source from memory.

### 7.5 Audit record

```json
{
  "key": "IIFA265",
  "aliases": [],
  "url_checked": "https://iifa-aifi.org/en/56085.html",
  "final_url": "",
  "http_status": 200,
  "retrieved_at": "",
  "identity": {"title": true, "issuer": true, "date": true},
  "locator_found": true,
  "quote_expected": "lawful to eat if it is alive",
  "quote_found": true,
  "normalization": "nfc+ws",
  "host_type": "issuer",
  "bibliographic_complete": true,
  "doi": null,
  "crossref_match": null,
  "archive_url": "",
  "family": "IIFA",
  "claims_rechecked": [{"id": "R01", "result": "supported"}],
  "verdict": "verified",
  "notes": ""
}
```

Verdicts: `verified`; `verified_with_note` (for example, edition not established); `replace_link` (content sound, host not citable; becomes citable once the footnote cites the print edition); `not_retrieved`; `quote_not_found`; `failed` (missing, wrong document, metadata mismatch or retracted); `held` (language policy). Only `verified` and `verified_with_note` are citable.

## 8. Cross-checking

Each check runs in a fresh Codex session that has not seen the drafting conversation, for example `codex exec` with the prompts in section 11. Checkers receive only the inputs listed and write to `working/checks/`. The drafting session records each outcome in `paper/review-log.md`.

| Check | Checker receives | Checker does not receive | Output |
| --- | --- | --- | --- |
| A. Blind re-derivation, per section §5–10 | The section's questions, record IDs, source URLs and locators | The draft, the review, the claim statements | Its own short answer per question, compared with the draft by the drafting session |
| B. Claim support | Section text and the fetched captures of its footnoted sources | Drafting notes | For every footnoted sentence: supported, partly supported, unsupported or overstated, with the passage |
| C. Adversarial reading | Full draft and registers | | Overclaims, status upgrades, missing qualifications, dropped dissent, merged layers, unattributed consensus, and the strongest objection the paper leaves unanswered |
| D. Coverage and numbers | `coverage.json`, draft, registers | | Records neither traced nor excluded; counts in the text that differ from the registers |
| E. Style | Draft and style file | | Violations with line references |
| F. Outside model (optional) | Same as C | | One run with a different model, such as Claude Code, to catch errors Codex sessions share |

Blocking findings are always fixed: an unsupported or overstated claim, an uncitable source, a status upgrade, a wrong count or a privacy breach. Major findings are fixed or justified in the log: a missing qualification, an unanswered objection or a blurred layer. Minor findings, on style and flow, are fixed in a batch.

When a blind answer differs from the draft, re-read the source. If the source is ambiguous, the paper reports the ambiguity. Agreement between agents is not evidence and never settles a reading.

Stop rule: release when one full round of A–E finds nothing blocking and no unjustified major finding. Log every round.

## 9. Mechanical checks

`tools/paper-checks.mjs` follows the pattern of `tools/phase1-checks.mjs` and is called from `verify.mjs`. `tools/test-paper-checks.mjs` confirms that a broken variant fails for each rule.

1. Every footnote definition ends with at least one bracketed key that resolves in `paper/source-register.json`; aliases resolve to their canonical key.
2. Every cited key has verdict `verified` or `verified_with_note`.
3. Every paragraph with a footnote, and every paragraph in §5–11, carries a trace comment, and every traced ID resolves.
4. A paragraph's footnoted keys fall within the sources of the records it traces, except entries in `allowlist.json` with a reason.
5. A paragraph tracing an inference record is marked `inference` or `mixed`; `J-Q1` is traced only as open.
6. All 74 claims, CE1–CE7 and every gap record are traced, or excluded in `coverage.json` with a reason.
7. Quotations of four or more words match, after normalization, a passage stored in `citation-audit.json` for a key cited in the same paragraph.
8. A phrase scan warns on "is halal", "are halal", "halal-certified", "unanimous", "consensus", "all schools", "approved" near a country or product, "proves", "confirms", "settles", "Islam permits" and "Islam forbids". Each warning is fixed or acknowledged in `allowlist.json`.
9. Stated register counts (74 claims, 76 sources, 45 slots and so on) match the registers.
10. The privacy patterns in `phase1-checks.mjs` and the hazards in `verify.mjs` find nothing.
11. The notice "AI-assisted working draft; human verification pending" appears under the title, and nothing claims scholarly or mentor approval.
12. The bibliography lists exactly the cited keys.
13. Section word counts within 20 percent of the targets in section 5 (warning only).

## 10. Writing rules

The fallback when Umar's style file is unavailable. Where they differ, the style file wins.

- Attribute every position to a named author, body or document.
- Write short declarative sentences, one claim per sentence where the evidence differs.
- Use concrete verbs: treats, requires, lists, permits, rejects, records.
- Avoid: delve, crucial, pivotal, robust, comprehensive, nuanced, landscape, navigate, leverage, underscore, foster, multifaceted, intricate, notably, moreover, furthermore, "it is worth noting", "plays a key role".
- No "not X but Y" flourishes, reflexive lists of three, rhetorical questions, closing sentences that restate the paragraph, or bold pseudo-headings inside paragraphs.
- Put each hedge once, on the claim it limits, in the status vocabulary of rule 2.
- At first use, give the transliterated term with a plain English gloss.

## 11. Prompts

### Preamble for every stage

> You are writing the Phase One paper in this repository. Read `research/halal-cultivated/PAPER-PLAN.md` in full, then the inputs in its section 2. Its section 3 rules override everything else, including this prompt. Do stage N only. At the stage's gate, run the checks, commit to `codex/phase1-paper` and report what you did, the gate result, open problems and anything you need from Umar. Never fill a gap from memory.

### Stage additions

- Stage 0: "Build the scaffold and checks in sections 1 and 9. Each check needs a failing fixture."
- Stage 1: "Build the paper register and coverage map. List every data problem you find, starting from section 13."
- Stage 2: "Audit every source under section 7. Fetch pages; do not rely on search snippets. Record `not_retrieved` when blocked."
- Stage 3: "Run tracks B1–B4 under section 4. Log every search, including empty ones."
- Stage 4: "Write the outline under section 6. Do not draft prose."
- Stage 5: "Draft the sections in the order in section 6. Trace every paragraph. Run the paper checks after each section."
- Stage 6: "Run checks A–E in fresh sessions with the prompts below. Fix blocking findings, then repeat until the stop rule is met."
- Stage 7: "Release under section 6. Do not merge."

### Blind checker (check A)

> You are an independent checker and have not seen any draft. Using only the sources at these locators, answer each question in two to four sentences. Quote the passage that supports your answer and say what the source does not settle. Questions: … Sources: …

### Adversarial reader (check C)

> Find every place this draft says more than its sources. For each, give the sentence, the record and status it relies on, the source passage, and a corrected sentence. Then state the strongest objection to the paper's argument that it does not answer.

## 12. Decisions for Umar

| ID | Decision | Default if not answered |
| --- | --- | --- |
| D1 | Whether drivers, elasticities (6.4C) and insects as feed (6.4D) belong in this paper | Out of the body and named in §11 as Phase Two inputs. They are market quantities with no records yet, and the revised plan's Phase One objective does not include them |
| D2 | Whether Malay and Indonesian rulings (Mufti WP Irsyad 595, JAKIM MKI 128, MUI, BPJPH originals) may enter through a labeled `unverified_translation` lane or a named reader | They stay held and are named only as untranslated leads |
| D3 | Venue, length and citation style | Incubator working paper, about 12,000 words, Chicago notes-bibliography |
| D4 | A local version that includes the private interview | Not part of this plan |
| D5 | Who provides human scholarly review before any external submission | Pending; the paper states it has had none |

## 13. Problems already found in the evidence

Found while preparing this plan. Stage 1 confirms and extends the list.

1. Five passages carry two IDs: `HAN` and `H1`, `HAN-D` and `H2`, `SHA-D` and `S3`, `SHA-T` and `S4`, `SIS-EN` and `J4`. Pick one canonical key per passage, keep the other as an alias, and never count the pair as two sources.
2. The ID schemes collide. `H1`–`H7` are Hanafi sources while `H-…` keys are Hanbali; `H01`–`H04` are both claim IDs and historical-comparison IDs; `G01`–`G02` are Ghamidi claims while `G1`–`G8` are gaps. Keep IDs out of the prose and namespace the trace comments.
3. `S2` (Reliance of the Traveller, on dokumen.pub; the URL carries ISBN 0915957728) and `H4` (an English Quduri, on studylib.net) are hosted on file-sharing sites, not by their publishers. Cite the print editions and drop the links.
4. Translator or edition is not established for `H-UM-*` (umdatalfiqh.com). `M-RIS29` credits Alhaj Bello Mohammad Daura and warns the translation is not final. Host-edition pagination is unconfirmed for several Arabic texts (gaps `G-BIBLIO`, `G-ENGLISH`, `G4`, `G8`; `H7` is on camquran.site).
5. Only `Q6` and `Q6121` name their translation (The Clear Quran). `Q5` and `Q7` do not.
6. `AD2858` displays a grading attributed to al-Albani. Report it as that attribution.
7. The SFDA documents show three regulation numbers: 513/2020, 5031:2020 and 5013. Keep the discrepancy visible until the Arabic text resolves it.
8. `HS-010`, `HS-011`, `HS-012` and `HS-024` point to consensus.app summaries, not publications.
9. The KMF 2025 and JAKIM 2025 cells in `consensus-matrix.csv` rest on news reports (`HS-004`, `HS-005`). The JAKIM primary (`MKI128`) is held in Malay.
10. `HS-014` (a fatwa site via islamqa.org) and `HS-015` (an Ask Ghamidi forum thread) are not institutional positions.
11. `HS-016` (the English Mizan on archive.org) should be checked against al-Mawrid's own publication before citation.
12. `gaps.json` mixes two record shapes; Appendix C presents them in one.
13. Extraction typos ("FormI", "AnnexI chaptersI–II", "The2013", "Rejected;2015") must not be copied into the paper.
14. `M-RIS-INDEX` is checked but uncited. `WP595` and `MKI128` are uncited because they are held.
15. SFA's list of 14 August 2026 and its framework page updated 27 August 2026 can change. Re-retrieve them and record any difference from the 30 September reading.

## 14. Done

- `paper.md` passes every check, and every cited source has a `verified` or `verified_with_note` audit record.
- Every Phase One record appears in the paper or is excluded with a reason.
- The final cross-check round is clean and logged.
- Both of Umar's checkpoints are passed.
- The library, READMEs and session log are updated.
- The draft notice remains, and the paper says that scholarly review has not taken place.

