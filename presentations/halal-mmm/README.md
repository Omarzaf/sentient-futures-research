# Cultivated Chicken and Halal Market Access — MMM edition

A Meaning, Man and Model reading edition of the working paper at [`research/halal-cultivated/paper/paper.md`](../../research/halal-cultivated/paper/paper.md). It is a local build for author review. It has not been published or deployed, and the paper remains an AI-assisted working draft with final author read and human scholarly review pending.

## View it

Open [`index.html`](index.html) in a browser from inside this repository tree. The page is one self-contained file: the stylesheet and script are inlined, and no runtime fetch is needed for the paper, figures, notes or data.

To serve it instead, run `node tools/serve.mjs` from the repository root and open `http://127.0.0.1:8796/presentations/halal-mmm/index.html`. The server only exposes files listed in `provenance/file-manifest.json`.

The links under "The paper in other forms" (Markdown, plain reader, source register) are relative to the repository, so they work only when the page sits at `presentations/halal-mmm/` in this tree.

## What is on the page

| Layer | Content | Source |
| --- | --- | --- |
| Title block | Title, draft status, subtitle and byline, plus the two pending review states | Manuscript lines 1–7 |
| Reading guide | Lead, four-number readout, five findings with section links, Fig. R1 | Written for this edition (`build/editorial.mjs`); every finding links to the sections that carry it |
| The paper | Abstract, sections 1–13, Appendices A–E and the bibliography, in manuscript order and wording | `paper.md`, rendered by `build/markdown.mjs` |
| Margin rail | 20 explanations: terms (mostly Appendix E wording), institution names, reading scope, inference limits | Written for this edition; no new findings |
| Figures | Figures 1, 3 and 2 redrawn with their reviewed labels and captions; reading figures R1–R3 | `figure-data.json`, `appendices-data.json`, manuscript text; see [FIGURE-MAP.md](FIGURE-MAP.md) |
| Notes | The 177 authored notes, each listed once with a return link to every one of its 251 citations | Manuscript footnote definitions |

Edition material is labelled on the page ("Reading guide, written for this edition", "A reading figure for this edition", "Redrawn for this edition", "Record (edition)"). Two derived additions sit beside canonical tables and entries without changing them: a Record column on the three Appendix D record tables (register key, aliases, and a bibliography link or the recorded host), and a register line under each bibliography entry (audit state, reading scope, citing notes). Trace comments from the Markdown are kept as `data-kind` attributes and are not displayed.

## Interaction

- Contents rail on the left (desktop); a Contents button opens it as a full-screen sheet below 980px. Without JavaScript, an inline contents list appears instead.
- Superscripts jump to the endnote; the endnote marks the back-link for the citation you came from. After any in-page detour (note, figure point, cross-reference) a "Return to …" control takes you back to the exact link. Browser Back also works.
- Figure points are links: Figure 3 points open their Appendix D record row, R2 points open their Appendix A slot row, Figure 2 cells open the country in Appendix B. Each figure has a skip link past its record links.
- Theme toggle (light/dark), remembered in `localStorage` when available. Without JavaScript the page follows the system setting.
- Reduced motion stops the series mark's 180-second drift. In-page jumps are instant.
- Print styles hide the chrome, force the light palette and fold margin notes inline.

## Network and fonts

Nothing is fetched automatically. The intended typefaces are Newsreader and IBM Plex Mono; no licensed font files were supplied, so the page uses them only if installed and otherwise falls back to Georgia and the system monospace. The colophon has a button that loads both families from Google Fonts on request (fonts.googleapis.com and fonts.gstatic.com) and remembers the choice in `localStorage`. External source links in the notes and bibliography need internet access only when followed.

## Rebuild and check

From the repository root, with Node.js 22 or newer and no installed packages:

```sh
node presentations/halal-mmm/build/build.mjs   # writes index.html and build-record.json
node presentations/halal-mmm/build/check.mjs   # content preservation, notes, links, URLs, figures
node tools/build-library.mjs                    # refreshes the repository manifest
node tools/verify.mjs
```

Edit `assets/mmm.css`, `assets/mmm.js` or the files in `build/`, never `index.html` directly. `build/browser-qa.mjs` runs the browser checks and needs a Playwright installation outside this repository: `PLAYWRIGHT_MODULE=/path/to/node_modules/playwright node presentations/halal-mmm/build/browser-qa.mjs [screenshot-dir]`. Screenshots written to `presentations/halal-mmm/qa/` are ignored by Git.

Test results, viewports and limits are in [QA.md](QA.md).

## Not claimed

The edition adds no ruling, certificate, forecast, ranking or confidence score. Counts in the readout and figures describe documentary availability in the paper's own registers. Browser checks do not establish reader comprehension, screen-reader validation or accessibility certification.
