# Independent review of the South Asia writing kit

Reviewer: Claude (Opus 5.5), separate session, 30 October 2026. Local, read-only review of Codex's P0 to P10 output. No kit, source, code, manifest, log, worktree or receipt was edited. Reproductions went to a scratch directory outside the workspace. No network fetch, install, push, message or Drive edit occurred. This is agent review, not human factual verification or scholarly acceptance.

## Verdict: Ready after targeted fixes

The kit's numbers are accurate where checked. Every value traced to an original source cell or retained row matched, and the Pakistan grid reproduces byte for byte. The structure follows the 30 October interview decisions. Five issues should be fixed before Umar writes from it: the Pakistan box text understates its own disagreement, its framing needs redesign, 31 DOCX links will break in Google Docs, sections 3 and 8 lack pre-verified material for their word budgets, and the paired contrast does not yet explain the India and Pakistan difference. None needs new research or a model change.

Severity counts: 0 BLOCK, 5 MAJOR, 9 MINOR, 4 SUGGESTION.

## Findings

### Confirmed errors

**F1. MAJOR. The Pakistan box prose misdescribes the grid.**
Location: `kit/pakistan-topdown-box.md` line 19 and `kit/WRITING-KIT.md` line 229 (the "AI draft, replace" paragraph). Same framing in `COMPLETION.md` "Pakistan check and the cleared stop".
Problem: the paragraph says "the larger share often exceeds the transfer range" and that the lowest shares "can produce low-tens-of-millions values". The grid shows something stronger. In the box's own central table, all six 2026 and 2030 cells exceed the transfer 90th percentile, including the 0.05% share (13.96 against 6.62; 14.18 against 13.68). Across the full grid, 139 of 162 combined rows exceed the 90th percentile and 0 fall below the 10th percentile. At the 0.05% share alone, 37 of 54 rows exceed it.
Evidence: recomputed from `build/pakistan-topdown/pakistan_topdown.csv`; the prior independent review records the same counts (40 above ten times, 99 above, 23 within) but no document turns them into prose. COMPLETION.md reports only the 40 extreme rows.
Why it matters: a reader copying the paragraph would say the check partly agrees with the transfer. It does not agree at any requested share before 2035.
Smallest correction: replace the first sentence with the counts. For example: "At every requested share, the conventional-value calculation exceeds the transfer's 90th percentile in 2026 and 2030; 139 of 162 grid rows exceed it and none falls below its 10th percentile."
Needs: no decision; text fix only.

**F2. MAJOR. 31 of 87 DOCX hyperlinks point to local relative paths.**
Location: `kit/WRITING-KIT.docx`, `word/_rels/document.xml.rels`. Examples: the scenario CSV, `methods/proxy.md`, `build/gfi-gap/REPORT.md`, `required-growth.csv`, the P4 grid and README, `recommendations.csv`, the collaborator snapshots, the corrigendum and the panel files.
Problem: decision 10 puts the kit in a Google Doc in Umar's Drive. After import, these 31 links cannot resolve. They also point to a local commit (`fb8c895`) that has not been pushed, so a GitHub link would not resolve either yet. The DOCX QA counted "32 local links resolve" as a pass because it tested the local filesystem only.
Why it matters: decision 9 asks for "verified numbers with hyperlinked sources". In Docs, about a third of the source links, including every link to the model outputs, would be dead.
Smallest correction: render local targets as plain-text path labels (for example `[local: research/india-pakistan/data/altprotein_proxy_scenarios.csv @ fb8c895]`) and keep only the 56 external URLs as live links. Alternatively, link to GitHub at a pushed commit once Umar authorizes a push.
Needs: Umar's choice between plain-text paths and a later push. Google Docs import itself remains untested.

**F3. MINOR. Section 6 contradicts its own placement rule.**
Location: `kit/WRITING-KIT.md` line 195 against lines 223 to 224.
Problem: line 195 says "Intermediate-year ranges and medians are reserved for Appendix A". The body box then shows the 2026 and 2030 transfer ranges (1.47 to 6.62; 2.28 to 13.68). Medians are correctly absent from the body.
Smallest correction: either move the box to Appendix A (see the Pakistan judgment below) or change line 195 to permit ranges in the box.
Needs: follows Umar's box decision.

**F4. MINOR. Rough paragraphs carry internal process language.**
Location: `kit/WRITING-KIT.md` line 229 ("This triggered the prescribed stop; Umar approved continuing with explicit caveats") and line 213 ("Conditional diagnostic for Umar to interpret").
Problem: these sentences describe the agent workflow. Copied into the regional report, they would read as an internal approval record.
Smallest correction: move workflow history to the open-questions line; keep the rough paragraph to the economic result.
Needs: no decision.

### Methodological disagreements

**F5. MAJOR. The capture shares have no empirical anchor; the implied-share framing is more informative.**
Location: `kit/pakistan-topdown-box.md`; decision 4 specified the 0.05%, 0.1% and 0.5% shares.
Problem: the box multiplies about USD 28 billion of conventional poultry and milk value (central profile) by shares that no source anchors. Inverting the same arithmetic shows what the transfer itself implies. Its 10th to 90th percentile range equals 0.005% to 0.024% of central conventional value in 2026, 0.008% to 0.048% in 2030 and 0.012% to 0.125% in 2035. The lowest requested share is two to ten times the 2026 implied range.
Basket compatibility is weak in four ways:
- The conventional value includes nonmarketed, rural and loose fresh milk. Plant-based alternatives sell almost entirely through formal urban retail.
- FAOSTAT milk excluding butter is a milk-equivalent food account. It is valued here at an urban weekly fresh-milk price.
- Poultry uses a live-bird price divided by an assumed yield, which values meat below retail.
- The transfer basket contains plant-based meat, dairy and eggs. The conventional basket omits red meat and eggs.
A ratio of "alternative spending to total conventional value" is therefore not a market share in the usual sense. Without an anchor, the grid mainly shows that the chosen shares are larger than the transfer.
Smallest correction: report the transfer's implied share of conventional poultry and milk value as the box's main result, and keep the requested-share grid in the companion CSV. A useful anchor would be the same ratio for India's 2022 GFI level, using Indian poultry and milk value; Indian price inputs are not retained, so this needs further evidence.
Needs: Umar's decision on framing; further evidence only for the India anchor.

**F6. MINOR. The quantity family nearly doubles the milk component, and the box does not say so.**
Location: box line 17 ("The complete grid retains alternative quantity definitions").
Problem: Economic Survey 2024 to 25 "Milk (Human Consumption)" is 58,300 thousand tonnes. FAOSTAT 2023 milk food is 32,104 thousand tonnes, 1.8 times smaller. FAOSTAT also lists Pakistan butter and ghee separately (1,268 thousand tonnes food), so FAOSTAT milk excludes milk diverted to ghee. The Economic Survey series likely includes it and values it at a fresh-milk price. Central 2026 conventional value is USD 27.9 billion with FAOSTAT milk against USD 46.5 billion with the Economic Survey family.
Smallest correction: one sentence in the box naming both milk totals and the ghee difference.
Needs: no decision.

**F7. MINOR. The paired contrast table does not state the differences it exists to show.**
Location: `kit/WRITING-KIT.md` lines 42 to 48.
Problem: the "Purchasing power" row has identical text for India and Pakistan. The kit already holds the numbers that differ: healthy-diet unaffordability 40.4% against 60.3% (SOFI, 2024); retained 2035 real-income indices 2.168 for India against 1.255 for Pakistan (`methods/proxy.md` line 71). The India "Religious assurance" cell ("Relevant populations and product routes differ") says nothing. The kit never explains why Pakistan's 2035 per-person median (USD 0.040) is about one seventh of India's (USD 0.28). The transfer's multipliers produce that gap: the slower income index lowers Pakistan, and dropping the urban-share and animal-supply multipliers lowers the 2035 median from 11.8 to 8.3, so those two raise it.
Why it matters: decision 13 makes the paired contrast the report's comparative logic. A reader cannot tell which differences are measured and which come from the transfer's construction.
Smallest correction: put the SOFI and income-index values in the table, rewrite the India assurance cell, and add two sentences to section 6 on what drives the per-person gap. All the numbers are already retained.
Needs: no new evidence.

**F8. MINOR. The GFI section omits GFI's own dollar conversions.**
Location: `kit/WRITING-KIT.md` lines 239 to 242; original `gfi-india-economic-analysis.txt` lines 84 to 125.
Problem: GFI's summary states its own USD equivalents, for example the 2030 domestic range "INR 7,475 crore (USD 946 million) to INR 18,963 crore (USD 2.4 billion)". The kit shows only its conditional conversion of USD 964.4 million for the low case. A reader comparing with GFI's text will see two different dollar figures without explanation.
Smallest correction: cite GFI's USD 946 million beside the conditional USD 964.4 million at 2025 prices, and state that the difference reflects the retained price-year and exchange-rate assumptions.
Needs: no decision.

**F9. MINOR. "Verified" mixes source checks, local-mirror checks and administrative numbers.**
Location: `kit/claims-by-section.csv`, `status` column.
Problem: 106 of 412 verified rows are section numbers, word budgets, document dates, axis ticks or workflow counts. 149 verified rows match a derived local CSV, not an original source. Two cases matter:
- WK-C-072 (Bryant India sample 1,024): checked only against `phase_two_leads.csv`, whose own row says "not_rechecked" and "Published India subgroup size, not verified". The kit states it as a fact (line 76). This review did not find a local copy of the paper; the value remains unchecked against the original.
- WK-C-067 to 071 (MoSPI): notes say "Needs table-specific extraction ... before use", but status is verified. This review checked the original PDF, Table 3.9, page 57: rural 66.6 and urban 69.9 g per consumer unit per day for 2023 to 24 are correct. The values are right; the register's own note is stale.
The `evidence_family` column does separate observations, derived values, assumptions and editorial numbers, so the register mostly meets the classification requirement.
Why it matters: "313 of 313 numeric occurrences verified" sounds like 313 source checks. About a third are administrative numbers, and many are mirror matches.
Smallest correction: add a `check_level` column (original source / derived local file / arithmetic / administrative), or report coverage counts by that split in COMPLETION.md. Recheck Bryant against the paper or soften to "reported Indian subgroup of 1,024".
Needs: further evidence for Bryant only.

### Usability and editorial gaps

**F10. MAJOR. Sections 3 and 8 carry the largest budgets with the thinnest verified material.**
Location: section map rows 3 (1,800 words) and 8 (1,400 words); `kit/WRITING-KIT.md` lines 60 to 88 and 266 to 293.
Problem: section 3 supplies five table rows and three bullets. Its "Material to develop" asks Umar to write about food frequency, food budgets and protein shares from `REPORT.md` lines 94 to 196 (2,386 words). That edition predates the 22 October corrigendum, and its numbers are not in the claim register. Section 8 supplies three sources and a table for 1,400 words. The handoff's writing rule says "every number checked against the claim map before it goes into the shared doc"; for these sections the map does not contain the numbers Umar will need.
Why it matters: these are the sections where Umar is most likely to lift an unchecked number from the old edition.
Smallest correction: extend the register to the numeric claims in `REPORT.md` lines 94 to 196 and 440 to 503 that the section map names, with status per row. The existing ledger match (546 displays, per the independent review) makes this mostly mechanical.
Needs: no decision; agent work.

**F11. MAJOR. The executive summary omits the report's main findings.**
Location: `kit/WRITING-KIT.md` lines 11 to 30.
Problem: the four evidence bullets give India's range, Pakistan's range, the GFI anchor and affordability. They omit the findings a funder would look for: no draw reaches GFI India's low 2030 case (the analytical maximum is USD 462.0 million against a converted target of USD 964.4 million); AI's beneficiary is untested on both sides; and halal assurance, certification and authorization are separate gates. The 29 October strategy's bottom line ("constraints lower the outlook") does not appear.
Smallest correction: add three evidence bullets with these results, each already registered elsewhere in the kit.
Needs: no decision.

**F12. MINOR. The only Pakistan alternative-protein price evidence is unused.**
Location: `build/pakistan-topdown/naheed_normalized.csv`; box line 17 calls plant-milk prices "context".
Problem: Naheed's 11 plant-milk listings are PKR 2,000 to 3,167 per litre (16 October 2026). Packaged dairy milk at the same outlet is PKR 360 to 500 per litre. That is roughly a five- to nine-fold premium. Caveats: one premium outlet, mostly imported brands, list prices.
Why it matters: driver D02 and recommendation R01 rest on price, and the kit otherwise cites no product price gap for Pakistan.
Smallest correction: one bullet in section 3 or 4 with these caveats.
Needs: Umar's editorial choice.

**F13. MINOR. Two retained consumer studies are dropped without mention.**
Location: `kit/WRITING-KIT.md` line 76; source `REPORT.md` lines 416 to 438.
Problem: the kit cites only Bryant. The section map's own source span also covers Arora, Brent and Jaenicke (2020; face-to-face discrete-choice survey in Mumbai with price attributes) and Ahsan, Uzair and Ali (the only retained Pakistan sample, on cultured meat). "No Pakistan sample ... follows" after Bryant can read as "no Pakistan study exists".
Smallest correction: one sentence naming both, with their sampling limits.
Needs: no decision.

**F14. MINOR. AI is a subsection, not the "full section" decision 5 named.**
Location: section map note line 25; `kit/WRITING-KIT.md` line 117.
Assessment: the content meets decision 5. It covers conventional poultry and dairy as well as alternatives, names no effect size, labels Cell Forge, Cowlar and Poulta as dated first-party descriptions, and gives signposts for 2026, 2030 and 2035. The placement inside section 4 is a defensible reading that keeps the 11-section plan intact.
Needs: Umar's decision on promotion to a numbered section.

**F15. MINOR. "Low tens of millions at most" conflicts with "not a hard upper limit".**
Location: `kit/WRITING-KIT.md` lines 18 and 195.
Problem: the 90th percentile is USD 36.1 million; "at most" implies a ceiling the kit itself disclaims. The wording comes from decision 3.
Smallest correction: "in the low tens of millions or below by 2035 in the central range".
Needs: Umar's decision, since it changes his decision wording.

**F16. SUGGESTION.** Add horizons and decision rules from `recommendations.csv` (for example 8 to 12 weeks for R01 and R02; 3 to 6 months for R04 and R06) to the section 10 table. Funders read scale and timing first. Driver links and measurable outcomes are already correct for R01 to R08.

**F17. SUGGESTION.** Rename the box from "independent conventional-food value check" to "conventional-value scale check". Its README says it shares source context with the model.

**F18. SUGGESTION.** Move the GFI figure (DOCX page 12) above section 7's "AI draft" paragraph, next to its table. It currently follows the open questions.

**F19. SUGGESTION.** In the Anna showcase, "Price ... is a central constraint" is asserted without a measured premium. F12's plant-milk ratio, with its caveats, would support it. The 82-word slide text matches the length of Umar's own 81-word draft.

## Judgment on the Pakistan box

Recommendation: move the box to Appendix A, redesign it around implied capture shares, and keep one sentence in section 6.

Reasons:
1. Placement conflicts with decision 3. The body states Pakistan as "low tens of millions at most". A body table showing USD 139.6 million beside that sentence invites readers to treat the larger figure as an alternative estimate.
2. The capture shares have no anchor (F5). With 139 of 162 rows above the transfer range regardless of share, the grid's message reduces to "the chosen shares exceed what the transfer implies".
3. The baskets are not compatible enough for a numerical contradiction (F5, F6). Conventional value includes nonmarketed and loose milk at urban prices; alternative proteins sell through formal retail.
4. The useful result survives redesign. The transfer implies alternative spending of about 0.005% to 0.024% of conventional poultry and milk value in 2026, rising to 0.012% to 0.125% by 2035. That sentence tells a funder how small the modelled market is relative to the food system, and it needs no arbitrary share.
5. The current caveats are accurate and complete about the mappings (yield, density, nonmarketed supply, CPI, carry-forward). They do not repair the framing, and the rough paragraph misstates the result (F1).

The authorization to continue the diagnostic stands; this judgment concerns presentation only. Omitting the box entirely would lose the implied-share result and the documented reproduction. Keeping it in the body as is would put an unanchored figure next to the headline.

Proposed body sentence (rough, replace): "A scale check against conventional poultry and milk value shows the transferred scenarios equal roughly one to twelve hundredths of one percent of that value by 2035; Appendix A explains why this is a scale comparison, not a market estimate."

## Requested checks not covered by a finding

- Food supply, household quantities, consumer-unit intake, intentions and market sales stay separate throughout. Section 3's caveat is explicit.
- UAE, Turkey and Saudi studies (S02, S04, S05) appear only as exclusions in `conflicts.md` and the section map. No affirmative use found in any kit or message file.
- Publication, observation and access dates are separated. Examples checked: Punjab regulation notified 27 November 2025 and gazetted 4 September 2026 (gazette cover image inspected); GFI publication date marked unstated; company pages marked as 17 October 2026 observations.
- GFI section: accepts the 2022 level, examines growth conditions separately, represents GFI's disclosed method fairly against the original text, and states the proxy's restrictive bounds and missing price-parity term as the antithesis.
- Halal interpretation, certification, food authorization and consumer response are four separate rows in section 8.
- Pakistan medians appear only in Appendix A.
- The panel is labelled exploratory, confined to Appendix B with one body sentence, and its departure from the 13 October team decision is disclosed in the kit and in the Anna heads-up.
- Collaborator snapshots are used only for qualitative cross-references, with draft status stated and no agreement implied.
- Recommendations R01 to R07 match the driver IDs in `recommendations.csv`; R08 is added with drivers, outcome and condition.
- Five messages: all under 200 words (149, 154, 171, 178, 194, including headers). Numbers match the kit. None claims team agreement. The Nadja update labels remote status as a 28 October observation.

## P0 to P10 completion assessment

| Package | Assessment |
| --- | --- |
| P0 | Complete. Branch `codex/writing-kit-20261030` at `fb8c895`, parent `32a1784`, checkout clean. Workspace verifier PASS 423, reproduced. |
| P1 | Complete. Budgets sum to 14,000 words. Allocation is credible except that sections 3 and 8 lack matching verified material (F10). |
| P2 | Substantially complete. Every value checked against an original source matched. Register semantics (F9) and thin coverage for sections 3 and 8 (F10) remain. |
| P3 | Complete and accurate. Slide 1 correction matches the method. |
| P4 | Computationally complete and reproducible. Interpretation text needs correction (F1) and redesign (F5). |
| P5 | Complete in content; placement is Umar's decision (F14). |
| P6 | Complete. Driver links, outcomes and conditions present; no return estimates. |
| P7 | Complete and fair; add GFI's own dollar figures (F8). GFI note unsent and appropriately conditional. |
| P8 | Complete. All under 200 words; no agreement claimed. |
| P9 | Complete locally. DOCX links (F2), paired contrast (F7) and executive summary (F11) need fixes. |
| P10 | Complete as receipts. Prior reviews missed F1, F2, F5 to F8 and F10 to F12. |

## What the earlier reviews missed

- The independent source review computed the 139 above-range rows but did not check that the box prose reflects them (F1).
- The DOCX QA counted local links as resolving. Google Docs import was disclosed as untested, but the link consequence was not identified (F2).
- No review examined the capture shares' anchor or the implied-share inversion (F5).
- No review compared the two milk quantity families or the ghee exclusion (F6).
- No review tested whether the paired contrast states measured differences (F7).
- No review compared the kit's GFI dollar figure with GFI's own (F8).
- No review measured the verified evidence available against section budgets (F10).

## Coverage

Files read in full: root `AGENTS.md`, `README.md`, relevant `SESSION-LOG.md` entries (29 and 30 October), `CONSOLIDATION-STRATEGY.md`, `HANDOFF.md`, `COMPLETION.md`, `p4/STOP-DECISION.md`, `p4/RESUMED.md`, `verification/authorization.md`, `kit/WRITING-KIT.md`, `kit/00-section-map.md`, `kit/conflicts.md`, `kit/pakistan-topdown-box.md`, all five `messages/*.md`, `tools/pakistan_topdown.py`, `data/pakistan-topdown/README.md`, `build/pakistan-topdown/receipt.json` and `extracted-inputs.json`, `verification/INDEPENDENT-SOURCE-REVIEW.md`, `verification/MODERATOR-REVIEW.md`.

Files read in part: `WORKSPACE-STATE.json` (not opened; workspace verifier run instead), `claims-by-section.csv` (all 418 rows profiled; about 30 rows inspected individually), `recommendations.csv`, `methods/proxy.md` (method lines), `build/gfi-gap/REPORT.md`, `required-growth.csv`, `target-comparison.csv`, `REPORT.md` (Gulf-study lines and section-map spans), original GFI summary text, `DOCX-VISUAL-QA.md` (link and import lines).

Not read: the individual `kit/0x-*.md` modules apart from the box (assembled `WRITING-KIT.md` read instead), `kit/appendices.md` as a separate file, the 27 October chapter and limitations file, the 22 October corrigendum, `PLAN.md`, `PREFLIGHT.md`, the collaborator snapshots, `tests/test_pakistan_topdown.py` source, `sources.json`, the Python and Node suite receipts. The 210-test Python suite and nine Node suites were not rerun.

Source cells checked against originals: FAOSTAT 2023 poultry, pulses and milk for India and Pakistan (food and per-person elements), plus Pakistan milk production, domestic supply and butter/ghee; GFI 2022 and 2030 domestic table and methodology; MoSPI Table 3.9 all-India row; Punjab gazette cover date. Checked against retained derived files only: SOFI, JME, HIES values; all 18 scenario market-value rows and the cited sensitivity rows; required-growth ranges and the 462.0, 202.2 and 964.4 diagnostics.

Calculations performed: full re-derivation of box cells and all flag categories from the P4 CSV; implied capture shares for all 54 quantity, year and price combinations; milk-quantity family comparison; Naheed price ratios; per-person ratio check.

Reproduction and checks run (non-destructive): `pakistan_topdown.py` into a scratch output directory, four outputs byte-identical to the committed files; `test_pakistan_topdown.py` and `test_writing_kit.py`, 15 passed, using the existing `Deep Research 2026-10/.venv` without installation; reference CSV 127 rows, SHA-256 `98c5a19c...` equal to the approved base; model engine and reference rows unchanged between `32a1784` and `fb8c895`; artifact manifest 25 of 25 hashes match; panel data 60 accepted responses and 79 attempt rows; original worktrees clean at `32a1784` and `2969e14`; `node tools/verify-workspace.mjs` PASS 423.

DOCX: XML inspected for 13 tables, 87 hyperlinks, 1 image, 0 footnotes, 0 hidden claim IDs. Rendered pages 2, 10 and 12 of 20 viewed; layout clean. Google Docs import not tested.

## Prioritized fixes before writing

1. Correct the box paragraph to state that every share exceeds the transfer range in 2026 and 2030 (F1).
2. Decide the box placement and framing; move it to Appendix A with implied shares as the main result (F5, F3).
3. Convert the 31 local DOCX links to plain-text path labels before import (F2).
4. Extend the claim register to the numbers in `REPORT.md` spans that sections 3 and 8 depend on (F10).
5. Add the main findings to the executive summary (F11).
6. Put measured differences in the paired contrast and explain the per-person gap (F7).
7. Add GFI's own USD figures, the milk-family note and the plant-milk premium (F8, F6, F12).
8. Strip workflow language from rough paragraphs (F4).

Fixes 1, 3, 4, 5, 7 and 8 need no decision.

## Decisions that remain Umar's

- Pakistan box: appendix with implied shares (recommended), body as is, or omission.
- Wording of "at most" in the Pakistan order-of-magnitude sentence (F15).
- Whether AI becomes a numbered section (F14).
- Whether to use the Naheed plant-milk premium in the body (F12).
- Link strategy for the Google Doc: plain-text paths now, or GitHub links after an authorized push (F2).
- Whether to obtain Indian price inputs for an India-anchored capture share (F5); this reopens bounded data collection.
- The team-level decisions already listed in COMPLETION.md (definitions box, Anna's medians, panel placement, overview matrix) and permission to send any of the five messages.
