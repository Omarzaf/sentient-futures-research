# QA report — MMM edition of "Cultivated Chicken and Halal Market Access"

Checked 2 October 2026 on branch `claude/friendly-knuth-tdkxnf`, created from `codex/claude-mmm-handoff` at `587bd9a`. Checks follow `handoffs/claude-mmm/qa/ACCEPTANCE.md`. Everything below was run; what was not run is listed at the end.

Environment: Linux container, Node.js 22.22.0, Playwright 1.56.1 driving headless Chromium (build 1194). No other browser engine was available.

## Commands and results

| Command | Result |
| --- | --- |
| `node presentations/halal-mmm/build/build.mjs` (run twice) | Identical `index.html` and `build-record.json` both times (SHA-256 recorded in `build-record.json`) |
| `node presentations/halal-mmm/build/check.mjs` | PASS, 3,082 checks, 0 failures |
| `build/browser-qa.mjs` against `file://` | PASS, 70 of 70 |
| `build/browser-qa.mjs` against `node tools/serve.mjs` (http://127.0.0.1) | PASS, 70 of 70 |
| `node tools/build-library.mjs` then `node tools/verify.mjs` | PASS, 28,603 checks, 258 files, 4,232 internal links, 0 failures |
| `node tools/build-library.mjs` again | No drift: only `provenance/file-manifest.json` differs from the base branch, and a second build leaves every generated file byte-identical |
| `node tools/test-halal-checks.mjs`, `test-phase1-checks.mjs`, `test-paper-checks.mjs`, `test-fetch-citations.mjs`, `test-survey-checks.mjs`, `test-privacy-checks.mjs` (the six workflow suites), plus `test-bridge-v2-checks.mjs` and `test-continuation-checks.mjs` | All PASS. `test-fetch-citations.mjs` passed on all 22 runs, with 0 real network attempts |

Baseline before the build: `verify.mjs` PASS with 25,636 checks over 239 files; all fixture suites passed.

## Content preservation (`check.mjs`)

The checker reads the generated HTML as text and compares it with `paper.md` and `handoffs/claude-mmm/CONTENT-CONTRACT.json`. It was also run against five deliberately damaged copies (one word changed, one citation removed, one URL altered, the Urdu language marker removed, one figure label changed); each was caught.

| Check | Result |
| --- | --- |
| 16 canonical inputs and 47 copied handoff files vs `PROVENANCE.json` | All byte-identical; `git diff` against the base branch shows no change under `research/`, `handoffs/`, `tools/` or `sources/` |
| Every paragraph, heading, list item, table cell, figure caption and figure description of `paper.md`, in order | 974 of 974 units found in sequence (Markdown syntax and trace comments excepted) |
| Title, draft status, subtitle, byline | Present in the title block; "AI-assisted working draft; human verification pending" sits directly under the title, with "Final author read — pending" and "Human scholarly review — pending" |
| Headings | The 20 contract headings, in order (plus an added "Notes" heading) |
| Notes | 177 definitions, ids and order identical to the contract; each note's text present |
| Citations | 251 reference occurrences, sequence identical to the contract; every occurrence has its own return link in its note |
| Links | 1,025 unique ids; all 1,384 fragment links land; all local file links resolve inside the repository |
| External URLs | Exactly the contract's 60 distinct URLs, each displayed as written (Arabic-script paths included) |
| Figures | The three original figure descriptions present; all 42 Figure 2 cell labels match `figure-data.json` and link to the right Appendix B target; 95 Figure 3 points in Appendix D order; 9 article points; 45 R2 points, each landing on its Appendix A row; three copper marks in the whole page (series mark, Figure 3, R3) |
| Language | No Arabic-script text outside a `lang` + `dir="rtl"` span or a URL; the Urdu held-record title is marked `lang="ur"` |

Notes are deduplicated: a note cited several times is listed once, with one return link per citation, labelled by section.

## Browser checks (`browser-qa.mjs`)

**Viewports.** 1440, 1280, 1024, 768, 390 and 375 px, each in light and dark. Document-level horizontal overflow was zero at every size, and no element outside a figure, table or contents container extended past the viewport. No console errors, no failed requests and no network requests at any size. The theme followed the system preference in each case. Margin notes sat in the right rail at 1440 and 1280 and folded inline at 1024 and below; the left contents rail showed at 1024 and above and was replaced by the Contents control below 980.

**Paths walked.**

- Citation jump and return by pointer: section 5 citation → note 29, whose back-link for that occurrence is marked → "Return to note 29" → focus back on the exact superscript. Passed.
- A note's own back-link for a different occurrence lands on that occurrence. Passed.
- Browser Back after following a note returns to the citation. Passed.
- Keyboard: Enter on a citation, Enter on the return control, Enter on a Figure 3 point (lands on its Appendix D row, which is highlighted), return to the point. Focus ring visible (2px solid). First Tab reaches the skip link. Passed.
- Figure drilldown and return: a Figure 2 admitted cell (Singapore, product food listing) and missing cell (India, product certificate → bounded-gap paragraph), an R2 slot, an R1 station, a readout number and a prose cross-reference. All landed and returned. Passed.
- Deep link to a note, then reload. Passed.
- Phone contents (390): opens as a full-screen sheet with focus inside, Escape closes and returns focus to the button, choosing Appendix B navigates and closes. Passed.
- Dense tables and wide figures at 390 scroll inside their own containers (Appendix D table 645 px in a 350 px frame; Figure 2 780 px in 370 px) while the page does not. Passed.
- Theme toggle switches to dark, persists after reload; copper stays `#8a5a3b`. Passed.
- Reduced motion: the series-mark drift runs by default and stops under `prefers-reduced-motion`. Passed.
- JavaScript disabled at 1280 and 390: all headings, 177 notes and 251 citations present, citation links work, the inline contents list appears on the phone, no overflow, and the JavaScript-only buttons stay hidden. Passed.
- Arabic and Urdu spans compute to `direction: rtl`, URLs to `ltr`, and no non-Latin text is uppercased. Passed.
- Each of the six figures has a title, a description of more than 80 characters, and `role="group"` (figures with links) or `role="img"` (R3). Passed.
- Print media (emulated, and a Chromium A4 PDF of about 114 pages): contents rail and controls hidden, white ground even from dark mode, margin notes inline, figures kept whole. Passed.
- Web fonts: no request before the opt-in; after it, Newsreader and IBM Plex Mono loaded from Google Fonts. Passed (this check used the network).

**Contrast.** Measured from computed colours against the page ground.

| Role | Light | Dark |
| --- | --- | --- |
| Body prose, figure cell text, canonical captions | 9.86 | 12.09 |
| Contents links | 12.49 | 15.13 |
| Note superscripts | 6.28 | 8.97 |
| Mono labels, table headers, margin notes, edition captions, back-links, register lines, SVG labels and notes (`--ink-4`) | 4.63 | 6.52 |
| Copper (decorative points; link hover only) | 5.16 | 3.03 |

Every essential text role meets 4.5:1. The light-theme `--ink-4` roles pass with little margin (4.63). Copper is never the only carrier of meaning; in dark mode it is below 4.5:1 and appears only as points and as a hover tint on links that are already underlined.

## Screenshots

In `qa/`: [desktop light](qa/desktop-1440-light.png), [desktop dark](qa/desktop-1440-dark.png), [phone](qa/phone-390-light.png), [phone contents sheet](qa/phone-390-contents.png), [phone Figure 2 scrolling](qa/phone-390-figure-2.png) and [desktop with the optional web fonts](qa/desktop-1280-web-fonts.png). All other screenshots use the fallback fonts.

## Design decisions made during QA

- **Inlined stylesheet and script.** `tools/serve.mjs` serves only listed MIME types with `nosniff`, so a separate `.css` or `.js` file would be blocked when the page is served from the repository. The build now inlines `assets/mmm.css` and `assets/mmm.js`.
- **No smooth scrolling.** On a page about 110,000 px tall, smooth scrolling made note jumps and returns take more than a second. Jumps are instant.
- **Readout moved into the reading guide**, beside the findings, because floating it in the title block left a large gap.
- **Editorial wording audited** with the avoid-ai-writing detector (score 1, labelled "Minimal AI signals"; it flagged em-dash separators required by MMM label style and low vocabulary diversity from repeated captions). One fragment, one doubled "X, not Y" construction and two margin tags were rewritten.

## Not run or not established

- Firefox, Safari/WebKit and real phones or tablets. Only headless Chromium was available.
- Screen-reader testing, forced-colours or high-contrast modes, and browser zoom above 100%.
- A physical print; print was checked only as emulated print media and a Chromium PDF.
- Live availability of the 60 external source links. They were compared with the contract, not fetched.
- Rendering with licensed local copies of Newsreader and IBM Plex Mono; none were supplied. The intended faces were seen only through the optional Google Fonts load.
- A qualified reader's check of the Arabic and Urdu text display. Glyphs rendered through the container's fallback fonts.
- Reader comprehension, specialist accessibility audit or certification.

## Known limits

- Figure 3 points are small (2.9 px marks, 5 px hit area). Each row label is a larger link to the same Appendix D table, and a skip link passes the 107 record links.
- SVG point titles that contain an Arabic source title cannot carry a separate `lang` marker, so a screen reader may read them with English rules.
- The `assets/` and `build/` files are sources. Edit those and rebuild; do not edit `index.html` by hand.
- The paper is an AI-assisted working draft. This edition changes its presentation, not its review status.
