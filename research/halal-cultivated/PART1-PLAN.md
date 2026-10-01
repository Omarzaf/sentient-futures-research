# Part 1 research plan: looped agentic execution

Version 1, 1 October 2026. Author: Muhammad Umar Zafar, AI-assisted. Status: working plan, not mentor-approved; human verification pending.

This plan builds on the [Phase One edition](phase1/README.md) and the [agentic plan](AGENTIC-PLAN.md). It replaces neither. Phase Two rules stay in [PLAN.md](PLAN.md) unless a change proposed below is approved.

## 1. Starting point

Phase One already holds 74 claims, 76 source records, 45 school-question slots (31 blind-checked readings, 13 inferences, 1 open), seven country accounts and four historical comparisons. The slots are readings and bounded inferences, not 45 settled findings. The [gaps register](phase1/gaps.json) lists what is still open. The research loop in the agentic plan (frame, retrieve, extract, blind check, counter-evidence, reconcile) is already written down and was used.

Part 1 repairs and extends that package. It does not start again.

Two inputs are missing, and no amount of Part 1 work replaces them:

- A compatible demand baseline: `D(c, y)` and the US analogue `p_US` from the demand-forecast workstream ([PLAN.md](PLAN.md) section 4.5). Requested on 30 September; no reply recorded.
- Human scholarly review of the religious chapters.

## 2. Decisions recorded

These were agreed in conversation on 1 October 2026. They are written here because the repository did not show them, which is why the 1 October review read the five chapters and 17 countries as a scope expansion.

| Topic | Decision |
|---|---|
| Structure | Part 1 has five chapters (section 4.2). Part 2 is the scenario grid in PLAN.md section 7. |
| Countries | 17: eight deep profiles and nine one-row table entries. The four focal and three precedent countries are expected among the deep profiles. The full list is open item 1. |
| Language | English for all new evidence in chapters 1, 2 and 4. Arabic stays only where Phase One already uses it for classical texts in chapter 3. |
| Missing English | The cell reads "no English source located (searched [date])", backed by a search log (section 6). It is never filled from a translation or from memory. |
| Source standard | Tiered by claim type (section 5). A third-party mirror is not an edition. A point with no legitimate edition is marked `edition_pending`. |
| Method | A looped agentic process (section 7) that pauses for review at the end of each chapter. |
| Dates | 24 October for the full Part 1 draft is provisional until the Sprint 0 pilot (section 10). 13 November for Part 2 stands. |

## 3. What changed after the 1 October review

The review of the earlier proposal was right on most points. Adopted:

1. Blind rereading tests interpretation, not search completeness. Two agents given the same incomplete sources can agree. Decisive claims now get an independent retrieval pass (step 5 in section 7.2).
2. Source authority depends on the claim. For "what did this institution decide", its own instrument is the primary evidence and a peer-reviewed paper about it is secondary. The earlier claim that the literature connectors "outperform" other tools had no project-specific test behind it and is withdrawn.
3. "No English source located" describes access, not the institution. It never becomes "silent", "no ruling" or "no regulatory position". It is reported in the chapter 5 findings, not only in a methods note.
4. Market context is not demand. Food-balance supply and population figures cannot give a certified halal market, cultivated-chicken demand or purchases. The "halal market calculation" proposed for chapter 1 is dropped.
5. Tools earn their place. Nothing is installed until the pilot shows it helps (sections 10 and 11).

Two points in the review were re-checked on 1 October:

- The K-Dense `literature-review` skill, as published with a review date of 30 September 2026, describes Parallel as optional scoping and AI schematics as optional. The review's reading (Parallel as primary search, mandatory figures) may describe an earlier version. Either way, the earlier recommendation had not checked dependencies, and the skill changes often, so any use pins a commit.
- `unjournal/cm_pq_modeling` contains a Monte Carlo model of 2036 production cost per kilogram (Squiggle and Python). It has no 2030 or 2035 output and no licence file, and its README says it is in early development. The review was right that a cost model exists.

## 4. Three changes neither plan had

### 4.1 The gate is indexed by process, segment and layer, not by country

Phase One's central result is that the religious answer depends on the process: where the founder cells came from and when, what went into the culture (serum, enzymes, scaffold), and whether the final material is treated as a changed substance. One `H_rel` value per country cannot carry that. The PLAN.md gate `G(c)` should become `G(c, s, P)`.

The process profile `P` starts from processes that exist in documents:

| Profile | Founder cells | Medium | Documented in |
|---|---|---|---|
| P1 | Chicken; procurement to be extracted from the dossier | Serum-containing | SFA approved list (allowed 26 November 2020); FDA dossier CCC000001 |
| P2 | Chicken; as P1 | Serum-free | SFA approved list (allowed 11 January 2023) |
| P3 | Chicken embryonic stem cells | No animal-derived components | SFA approved list (Vital Meat, allowed 17 October 2025) |
| P4 | Lawfully slaughtered donor | Animal-free | Reference case; the IIFA 265 and MUIS texts discuss donor conditions |

P4 is the only profile without a real product behind it. It stays as the reference case most authorities address.

The consumer segment `s` depends on what the law allows. Where the law requires halal status for meat sold, the gate binds the whole market. Where non-halal meat can be sold legally with labelling, the gate binds a segment: Muslim consumers, halal-certified food service and export. In that case a product without halal certification could still reach other consumers once the food regulator approves it, and a country-level switch would wrongly set the whole market to zero. Chapter 2 establishes which case applies in each country. India, Singapore and Malaysia are likely segmented; Saudi Arabia and Pakistan likely whole-market; the UAE and Indonesia need checking. India also has state-level disputes over halal certification; a November 2023 Uttar Pradesh order restricting halal-certified products is a lead for chapter 2. Any segment size must come from a sourced figure, such as religion-specific meat consumption in a national survey, not from population share alone.

Phase One keeps religious permission, certification and food authorisation apart. The gate does the same: `H_rel` (a named authority's position on profile P), `C` (a certifier that can issue a certificate for P) and `L` (food authorisation for P). `L_includes_halal` stays. `G(c, s, P)` is 1 only when all three are open. It remains a switch, never a fraction (PLAN.md rule 1).

This changes PLAN.md section 4.5 and `datapackage.json`, so it is proposed here, not made (open item 2). It adds two columns, `segment` and `process_profile`, and leaves every key shared with the demand forecast unchanged, so the row-by-row join still works.

### 4.2 Each chapter is built backwards from a Phase Two field

| Chapter | Question | Feeds | Done when |
|---|---|---|---|
| 1. Market context | How large is the conventional meat market, chicken first, and how is it projected to move? | `D(c, y)` candidates; segment sizes for 4.1 | Supply, survey consumption and projections sit in separate `MR-` rows with their metric types; no multiplied "halal market" figure |
| 2. Institutions and certification | Who decides halal status and food authorisation for a new food, under which instrument? | `C`, `L`, `L_includes_halal`, `cert_route`; whole-market or segment | Eight deep profiles with dated instruments; nine table rows; every empty cell has a search log |
| 3. Foundations re-check | Do the Phase One readings hold on legitimate editions? | The conditions that define the process profiles | Each Phase One citation is on a tier A or B edition or marked `edition_pending`; Ghamidi column added from his published English works |
| 4. Contemporary rulings | What has each named institution said about cultivated meat, and for which process? | `H_rel` per institution and profile | About ten institutions; each cell holds a position with instrument and date, or "no English source located" with its log |
| 5. Synthesis | Which gate cells are open, shut, conditional or unknown, and why? | The Part 2 gate table | Gate table, limitations including English coverage, reviewer packet, handoff |

Chapters 2 and 4 decide the gate. Chapter 1 is the cheapest and least decisive. Effort follows that order.

### 4.3 Reviewer time is the scarcest input

No agent check gives scholarly authority, and a reviewer will not read the whole report. The loop therefore keeps a decisive-claims register: claims that would open or shut a gate cell or change a chapter conclusion. Each entry carries the exact excerpt, source and edition, the reading, the inference drawn, and what would defeat it. The packet for chapters 3 and 4 is that register, kept to about 20 to 25 entries. The reviewer should be asked now, because finding one will take longer than any chapter.

## 5. Source standard by claim type

| Claim type | Tier A | Tier B | Lead only, never cited |
|---|---|---|---|
| What an institution decided | The instrument on the institution's own site or in an official gazette | An official translation; a copy hosted by another official body | News, blogs, company releases, secondary summaries |
| What a classical text says | Print edition or translation with a named editor or translator | Publisher-hosted e-text of that edition | Third-party mirrors (`edition_pending`) |
| Quran and hadith locator | Print edition | sunnah.com with collection, number and grading as given | API copies such as fawazahmed0/hadith-api, used only to check numbers |
| Market and statistics | FAOSTAT, OECD-FAO Outlook, national statistical offices | USDA FAS GAIN reports | Industry market-size estimates |
| Process and science | Regulatory dossier; peer-reviewed study | Company technical documents | Press releases |
| Scholarly interpretation | Peer-reviewed article or book by a named scholar | Working paper | Opinion pieces |

Two Phase One rules stay. Two readings of one authority are one source. A mirror or API that copies sunnah.com does not corroborate sunnah.com.

Where an official English text exists but the institution names another language as authoritative (BPJPH Decree 221/2025 says Indonesian prevails), the cell records that.

## 6. The English-only rule in practice

- Search order for each institution: its English site or section; its official English publications; English documents it has filed with other bodies, such as WTO TBT and SPS notifications; English-language official journals.
- Every empty cell has a record of the date, tool, query, sites searched, results screened and why none qualified.
- Chapter 5 states which institutions could not be read in English and what that means for each gate cell: the cell stays `unknown`, never `silent`.
- The institutions that publish in English are mostly the export-facing ones (JAKIM, MUIS, IIFA, Dar al-Ifta's English site). Their English output may lag or simplify their domestic rulings. Chapter 5 says so.
- Other-language leads are logged as leads, as Phase One did with the Malay records, and are not read into findings.

## 7. The loop

### 7.1 Unit of work

A unit is one answerable question tied to one cell: a country instrument, an institution's position on a profile, an edition check or a statistics pull. Units sit in a queue file, `part1/queue.json`, with id, chapter, question, the cell it feeds, whether it is decisive, priority, state, budget used and links to its records.

Order: decisive units for chapters 2 and 4 first, then chapter 3 edition repairs that touch decisive claims, then the rest.

### 7.2 Steps for each unit

These extend the six steps in the agentic plan. Steps 2 and 5 are new.

1. **Frame.** State the question, its claim type (which sets the source tier) and what evidence would change the answer.
2. **Search, logged.** Follow the search order in section 6 and write a log record for every query, including those that find nothing.
3. **Read and extract.** Keep evidence records and inference records apart. Record edition status.
4. **Blind check (interpretation).** A fresh agent gets the question and the source locators, not the first answer, and writes its own reading.
5. **Independent retrieval (completeness), decisive units only.** A fresh agent gets the question alone, no source list, and searches by a different route. If it finds a relevant source the first pass missed, return to step 3.
6. **Counter-evidence.** Look for later decisions, revocations, fuller texts and other-language versions (as leads).
7. **Reconcile.** The coordinator compares readings and closes the unit in one of the states in 7.3.
8. **Check and commit.** Run `node tools/build-library.mjs`, `node tools/verify.mjs`, `node tools/test-halal-checks.mjs` and `node tools/test-phase1-checks.mjs`; update the queue and metrics; commit.

### 7.3 Stop rules

A unit closes as:

- `answered`: a tier A or B source supports a bounded answer, and the blind check agrees or the disagreement is recorded;
- `gap`: three search rounds, or two rounds in a row with no new relevant source, shown in the log;
- `blocked`: it needs a person, a paywalled document or a non-English text, and goes on the human-input list with exactly what is needed.

A chapter pauses for your review when all its units are closed. The loop also stops and asks when a new finding contradicts a Phase One claim. Phase One records are corrected only with a note, never silently.

### 7.4 Roles

At most two agents run at once, as the agentic plan already says. Extractors and checkers write records to a working area; only the coordinator writes to the repository. The writer drafts from accepted records and labelled inferences and keeps disagreement visible.

### 7.5 What the loop measures

For each chapter:

- units answered, gapped and blocked;
- blind-check disagreements and how each was settled;
- independent-retrieval hit rate: the share of decisive units where the second search found a relevant source the first missed. While it stays high, the search is not saturated and the chapter is not done;
- decisive claims resting on tier A sources;
- the `edition_pending` count.

### 7.6 How the loop runs

Each working session takes the top units from the queue, closes them, commits to a branch and updates one draft pull request per chapter. Running it on a schedule, with a routine that starts a session once or twice a day, would change the agentic plan's statement that no autonomous background research runs, so it needs your approval (open item 3).

## 8. Who is needed

| Need | For | When |
|---|---|---|
| A reviewer with fiqh training | The chapters 3 and 4 decisive-claims packet | Ask now; packet ready about 22 October |
| Demand-forecast workstream reply | `D`, `p_US` and the US meat denominator (PLAN.md 4.5) | Before Part 2; chapter 1 can proceed without it |
| Your 17-country list | Chapters 1 and 2 | Before chapter 1 starts |
| You, at each chapter gate | Accept, correct or send back | About once a week |

## 9. Timeline (provisional)

| Dates | Work |
|---|---|
| 1–3 October | Sprint 0: build the queue, run the ten-unit pilot (section 10) |
| 5 October | Recalibrate the dates below from pilot throughput |
| By 8 October | Chapter 1; chapter 2 under way |
| By 14 October | Chapter 2 |
| By 18 October | Chapter 3 |
| By 22 October | Chapter 4; reviewer packet sent |
| By 24 October | Chapter 5 and the full Part 1 draft |
| 26 October – 13 November | Part 2 scenario grid, once `D` and `p_US` arrive |

## 10. Sprint 0 pilot

Ten units, each chosen because it would change a gate cell or a decisive Phase One reading. They are real research, and the tool comparison runs alongside.

| # | Unit | Chapter | Feeds |
|---|---|---|---|
| 1 | Controlling SFDA novel-food regulation number and version (official English documents show 513/2020, 5031:2020 and 5013); check WTO TBT notifications for an English text | 2 | Saudi Arabia `L` |
| 2 | Operative UAE novel-food instrument, ADAFSA or federal | 2 | UAE `L` |
| 3 | Pakistan: which food authority approves a new food, and which Pakistan Halal Authority Act sections are in force | 2 | Pakistan `L`, `C` |
| 4 | India: FSSAI non-specified food approvals list, read in a browser (the page returned only a script shell before) | 2 | India `L` |
| 5 | MUIS: current certification position on cultivated meat after the 2024 monograph | 2, 4 | Singapore `C`, `H_rel` |
| 6 | JAKIM or a Malaysian federal mufti position, in English | 4 | Malaysia `H_rel` |
| 7 | MUI or BPJPH position, in English | 4 | Indonesia `H_rel` |
| 8 | Dar al-Ifta Egypt or Al-Azhar position, in English | 4 | Institution column |
| 9 | Replace third-party mirrors for the English classical manuals (gap G4), or mark them `edition_pending` | 3 | Decisive Phase One readings |
| 10 | Peer-reviewed literature on the halal status of cultivated meat, 2018–2026 | 4 | Scholarly column; tool comparison |

The tool comparison:

- Units 1 to 9 are retrieval of official documents. No candidate repository is built for that, so the existing tools (web search and fetch, Playwright for script-rendered pages) are the baseline. If that holds in the pilot, the constraint on this project is access to official documents and human review, not search software.
- Unit 10 runs twice: once with the Elicit, Consensus and Scholar Gateway connectors, once with K-Dense `paper-lookup` at a pinned commit. Hamdan et al. (2018) and Alqurashi et al. (2026) are already known to be relevant; a search that misses them fails the recall check. Compare relevant sources found, citations usable without correction and time to close.
- Unit 9 uses fawazahmed0/hadith-api only to cross-check hadith numbers.

Ten units are too few for a statistical comparison. Decision rule: adopt a tool if it found a relevant tier A or B source the baseline missed, or produced citations that needed fewer corrections. Otherwise leave it out.

## 11. Tools decision

| Asset | Decision | Reason |
|---|---|---|
| K-Dense `paper-lookup` | Pilot in unit 10, pinned commit | MIT licence, Python standard library, no keys required; covers OpenAlex, Crossref, Semantic Scholar, CORE, Unpaywall and DOAJ |
| K-Dense `citation-management` | Consider only if `paper-lookup` is adopted | DOI to clean metadata; check output against the repository's RIS use first |
| K-Dense `literature-review` | Not now | Built around biomedical databases, with optional Parallel and OpenRouter steps; revised often |
| fawazahmed0/hadith-api | Check only, never cite | Its references include sunnah.com, so agreement is not corroboration; neither numbering nor wording settles interpretation |
| unjournal/cm_pq_modeling | Read and cite in Part 2; do not copy code | 2036 cost model; no 2030 or 2035 output; no licence file; early development. A cost model is not a retail price or adoption estimate |
| assafelovic/gpt-researcher | Defer | OpenAI and Tavily are defaults, not requirements, and it can work from supplied URLs and local documents. No evidence yet that it improves on this loop |
| Forward-Future/loopy | Not now | The loop and stop rules are written here. Revisit if the chapter 1 debrief proves too thin |
| hardikpandya/stop-slop | Last editorial pass only | It must never strip uncertainty, qualifiers or technical distinctions |

## 12. Open items

1. Write the 17-country list (eight deep, nine rows) into section 2.
2. Approve or reject the gate change in 4.1 (adds `segment` and `process_profile`; shared keys unchanged).
3. Approve or reject scheduled loop runs (7.6).
4. Name a reviewer for chapters 3 and 4.
5. Reply from the demand-forecast workstream on `D`, `p_US` and the US meat denominator.
