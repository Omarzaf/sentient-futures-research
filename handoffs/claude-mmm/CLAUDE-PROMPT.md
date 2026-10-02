Create a finished local HTML reading experience for my working paper, **Cultivated Chicken and Halal Market Access**, using my **Meaning, Man and Model (MMM)** design system supplied in this package.

Start from `Omarzaf/sentient-futures-research`, branch `codex/claude-mmm-handoff`, and create a new implementation branch. All paths below are relative to the repository root. Read the repository README and work within its existing validation and privacy rules. This repository edition reuses the canonical paper files instead of duplicating them.

I want the page to feel like an authored MMM research entry: warm paper, precise serif typography, restrained geometric diagrams, substantial prose and useful marginalia. Use the existing design files to reproduce the system closely. Deliver the working HTML and its local assets, not just a proposal or a screenshot.

## Read in this order

1. `handoffs/claude-mmm/START-HERE.md` and `handoffs/claude-mmm/design/DESIGN-BRIEF.md`.
2. `handoffs/claude-mmm/design/mmm/SKILL.md`, `handoffs/claude-mmm/design/mmm/readme.md`, `handoffs/claude-mmm/design/mmm/guidelines/illustration.md`, and the CSS tokens. These are supplied files; do not assume an installed skill exists elsewhere on your machine.
3. `research/halal-cultivated/paper/paper.md`, `handoffs/claude-mmm/CONTENT-CONTRACT.json` and `research/halal-cultivated/paper/figure-data.json`.
4. Inspect `handoffs/claude-mmm/design/reference/observatory-reference.html` for visual and interaction patterns, and `research/halal-cultivated/paper/index.html` for complete paper rendering and note relationships. Read `handoffs/claude-mmm/design/reference/REFERENCE-NOTES.md` for known differences from the governing brief.
5. Consult the figure SVGs, component sources and relevant `research/halal-cultivated/paper/` records as needed. The PDF and Word files are supplementary completeness references.

## What to build

Default to one continuous MMM entry with a short, accessible visual overview and findings near the top, then the full paper, appendices, bibliography and endnotes. Use a left contents rail, a measured prose column and a right rail for definitions, figure captions and evidence limits. Make the opening understandable to an interested policy reader without prior knowledge of cell culture or Islamic legal terminology.

A Basmati-style “Visual overview / Full research” pair is an optional alternative only if the user selects it. In that case, preserve complete content, direct section links, keyboard navigation and the ability to return to the original reading position. The core paper must remain available if JavaScript fails.

Prepare a short figure map before implementing, then proceed to the build in the same task. Use `handoffs/claude-mmm/design/FIGURE-PLAN.md` as a starting point. Retain the three reviewed figures' substance and labels. Redraw them with MMM's SVG vocabulary where useful; add diagrams only when their content is derivable from the supplied paper or records. Make figure-to-evidence navigation helpful rather than decorative.

## Research fidelity

Treat `research/halal-cultivated/paper/paper.md` as authoritative. Preserve its wording in the full-paper layer, including all 13 numbered sections, the abstract, five appendices, bibliography, 177 authored footnote definitions and every reference to those notes. The existing reader expands reused notes into 251 occurrences. You may deduplicate the rendered notes if every occurrence still has a correct destination and return link. Preserve all 60 distinct source URLs, locators, conditions, non-English titles and quoted passages. Pure layout changes, semantic markup and conversion of Markdown syntax are allowed. Newly written summaries or navigation labels must be separate from the complete canonical text.

Keep “AI-assisted working draft; human verification pending” visible near the title. Human scholarly and final author review remain pending. Do not turn agent checks into institutional or scholarly approval. Do not turn qualified documentary records into confidence scores or votes. No national halal verdict, product certificate, numerical adoption forecast, market-access conclusion or missing baseline may be invented. A missing or held source stays missing or held.

MMM's generic first-person writing guidance does not authorize rewriting this paper or fabricating the author's research experience. Use factual explanations and captions in the right rail. Only add first-person marginalia if genuine author notes are supplied; otherwise leave that voice unused.

## Design and implementation

Follow `handoffs/claude-mmm/design/DESIGN-BRIEF.md` where older examples conflict. Use Newsreader and IBM Plex Mono with the supplied fallbacks. Preserve warm light and dark modes, sparse copper points, thin geometry, five type roles, measured text and flat section structure. Keep essential labels legible; faint ink is for decoration. No generic card dashboard, gradients, hero photograph, stock icons or scroll-reveal animation.

Use semantic HTML, CSS, inline SVG and minimal JavaScript. The React components are design references, not a requirement to add React, Babel, a build service or a UI framework. Do not copy the unrelated Observatory dataset or findings into this paper. Do not use its outbound data-download links as this paper's downloads.

Write to `presentations/halal-mmm/`, preserving every supplied input. Deliver `index.html` plus any local CSS, JS and assets needed, and a short `README.md` explaining how to view the result. Keep all essential content, figures and controls usable without runtime fetching of the research JSON. Remote fonts may be an optional enhancement with fallbacks; list any network dependencies honestly. Do not claim fully offline font fidelity unless licensed local font files are supplied. Use contained horizontal scrolling for dense matrices; the document itself must not overflow on mobile.

Include a genuine light/dark toggle, keyboard focus, reduced-motion handling, useful SVG titles/descriptions, appropriate Arabic/Urdu language and bidirectional markup, and print styles. A linked SVG point must land on a real evidence record or section. Document any derived figure classifications beside the relevant code.

## Finish and verify

Use `handoffs/claude-mmm/qa/ACCEPTANCE.md`. Check content inventories and citation destinations against `handoffs/claude-mmm/CONTENT-CONTRACT.json`; do not assume visual similarity proves preservation. Test at desktop, tablet and phone widths, in both themes, including a citation jump and return, figure drilldown and return, long source titles, and dense tables. Record actual checks and limitations in `presentations/halal-mmm/QA.md`. If you cannot run a browser or a check, mark it untested rather than claiming it passed.

Run the repository build, verifier and fixture suites listed in its README and workflow; rebuild once more and require no generated-file drift. Update the new presentation README with its scope and viewing instructions. Keep generated research unchanged and record all new HTML assets in the normal repository manifest.

Deliver the HTML files and a concise explanation of what was built and tested. Keep the implementation local unless I separately authorize sharing it. Do not deploy, push, upload research, change repository visibility or contact anyone as part of this build task.
