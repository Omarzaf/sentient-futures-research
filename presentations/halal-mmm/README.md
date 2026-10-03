# Cultivated Chicken and Halal Market Access — HTML reading edition

An HTML reading edition of the working paper at [`research/halal-cultivated/paper/paper.md`](../../research/halal-cultivated/paper/paper.md). The author read this edition and approved public sharing on 2 October 2026, as recorded in [edition.json](edition.json). The author requested removal of the series masthead and review-status chrome. The sole canonical-text omission in this HTML is the exact frontmatter disclaimer recorded there; the canonical manuscript and exports are unchanged. The paper's AI-assistance discussion and pending independent scholarly-review limitations remain in the body. Author approval does not establish independent scholarly approval; deployment is a separate action.

## View it

Open [`index.html`](index.html) in a browser from inside this repository tree. The page is one self-contained file: the stylesheet and script are inlined, and no runtime fetch is needed for the paper, figures, notes or data.

To serve it instead, run `node tools/serve.mjs` from the repository root and open `http://127.0.0.1:8796/presentations/halal-mmm/index.html`. The server only exposes files listed in `provenance/file-manifest.json`.

The links under "The paper in other forms" (Markdown, plain reader, reviewed PDF and Word, source register) are relative to the repository, so they work only when the page sits at `presentations/halal-mmm/` in this tree.

## What is on the page

| Layer | Content | Source |
| --- | --- | --- |
| Title block | Title, subtitle and byline; the exact frontmatter disclaimer is omitted by the author's request | Manuscript lines 1–7 and `edition.json` |
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
- The series mark is absent. No continuous animation remains; reduced-motion handling is retained. In-page jumps are instant.
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

Edit `assets/mmm.css`, `assets/mmm.js` or the files in `build/`, never `index.html` directly. `build/browser-qa.mjs` runs the browser checks and needs a Playwright installation outside this repository: `PLAYWRIGHT_MODULE=/path/to/node_modules/playwright node presentations/halal-mmm/build/browser-qa.mjs [screenshot-dir]`.

The preservation checker permits only `edition.json`'s exact frontmatter line at canonical unit 1 to be absent. All remaining title text, body units, notes, sources and figure labels retain the original checks. `build-record.json` includes the edition-input hash and the separate author-approval and scholarly-review states; it is not a deployment receipt.

Test results, viewports and limits are in [QA.md](QA.md).

## Public file export

After the checks pass, `node tools/build-public-paper.mjs <new-release-directory>` from the repository root prepares a separate `site/public/` folder and Vercel configuration. The destination must be new and outside this repository. It contains this HTML at the site root and original presentation path, plus the linked canonical Markdown, plain reader, PDF, Word, source register and six figure files. All copies preserve their bytes; the downloads retain their original review labels. The receipt stays outside the deployment folder. Deploy only that `site/` directory, never the research checkout or its history.

## Not claimed

The edition adds no ruling, certificate, forecast, ranking or confidence score. Counts in the readout and figures describe documentary availability in the paper's own registers. Browser checks do not establish reader comprehension, screen-reader validation or accessibility certification.
