# Figure map

Planned before the build, following the build handoff's figure plan and the MMM illustration guide. The paper's three figures keep their original numbers (1, 3, 2, in the order they appear). Figures added for this edition are numbered R1–R3 ("reading figures") so they cannot be mistaken for the manuscript's own figures. Every figure is drawn at build time by `build/figures.mjs` from the inputs named below.

## Figures by location

| Location | Figure | Pattern | Input | Points link to |
| --- | --- | --- | --- | --- |
| Opening, after the findings | **R1 — Six questions, kept apart** | Corridor | Section 1, paragraph 2; Figure 1's six question labels; section 11.2 | Sections 5, 6, 7, 8, 9 and 9.4; section 11.2 |
| Section 2, canonical position | **Figure 1 — From starting cells to a food product** (redrawn) | Corridor plus numbered list | `figures/figure-1-process.svg` labels and canonical caption | Sections 5–9 |
| Section 4, after paragraph 1 | **R2 — The 45 comparison slots** | Dot matrix | Appendix A tables (the "Currently admitted answer" column, read verbatim) | The matching Appendix A row |
| Section 4, canonical position | **Figure 3 — Evidence available to this paper** (redrawn) | Dot strips | `figure-data.json` counts; `appendices-data.json` sources (same order as Appendix D) | The matching Appendix D record row |
| Section 9.4, canonical position | **Figure 2 — Documentary scope by jurisdiction** (redrawn) | Dot matrix with every cell label kept | `figure-data.json` countries | The country's Appendix B table, or its bounded-gap paragraph |
| Section 11.2, after paragraph 4 | **R3 — From a dossier to separate decisions** | Corridor with a closed gate | Section 11.2, paragraphs 1–4 | Sections 11.2 and Appendix C |

## Sections without a figure

| Section | Reason |
| --- | --- |
| Abstract, 1 | R1 sits directly above them and covers the framing. |
| 3. Prior scholarship | The reading-scope split (six full-text, three abstract-only articles) is the second panel of Figure 3. A separate drawing would repeat it. |
| 5–8 | The optional process-stage comparison was not drawn. It would need a stage-by-stage legal classification that the paper does not make; Figure 1 and R1 carry the sequence. |
| 9.1–9.3 | The position table in 9.2 is the structure. A condition-by-issuer matrix would invite reading agreement into the table, which section 9.2 warns against. |
| 10. Historical analogies | The paper's own four-row table already sets out each test and what would defeat it. |
| 12, 13 | Prose limits and conclusion; no sequence, proportion or comparison to draw. |
| Appendices C–E | Tables and glossary; Appendix D is the evidence ledger that Figure 3 links into. |

## Encodings (stated once per figure caption)

- **Figure 3 and Figure 2 use one documentary-state encoding.** Filled point: admitted, bounded document. Hollow point: held, or held under the language policy. Dashed hollow point or em-rule: not retrieved, not located or not established in this review. These are named states, not a confidence scale.
- **R2** uses filled for an attributed answer, hollow for the paper's labeled inference, an em-rule for "no answer admitted" and a dashed ring for the one slot recorded as open.
- **Copper** appears once in Figure 3 (the qualified record that supplies index metadata only, which the canonical caption names) and once in R3 (the blocked quantitative handoff). The opening view's only copper point is the series mark.
- Spacing, point position and line length never encode magnitude except as counts of individual records in Figure 3 and R2.

## Derived classifications

Each rule is an ordered list where the first match wins, written beside the code in `build/figures.mjs`.

- **Figure 2 cell state** (unchanged from `tools/build_paper_figures.py`): label starts with "Not " or "Unretrieved" → missing in this review; label is "Language hold" → held lead; otherwise → admitted, bounded document.
- **R2 slot state**: answer text starts with "Open" → open; starts with "No answer admitted" → no admitted answer; starts with "Inference:" → the paper's inference; otherwise → attributed answer.
- **Figure 3 record state**: the `verdict` field in `appendices-data.json` (verified_with_note / held / not_retrieved); the article panel uses `reading_scope` for admitted journal articles.
