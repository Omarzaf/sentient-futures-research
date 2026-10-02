# Build the working paper in the MMM style

This is the repository edition of Muhammad Umar Zafar's Claude handoff for **Cultivated Chicken and Halal Market Access**. It contains the Meaning, Man and Model design references and build instructions. The reviewed paper, figures, evidence and PDF/Word exports are already tracked at their canonical paths in this same branch.

## Start the task

Use branch **`codex/claude-mmm-handoff`** of **`Omarzaf/sentient-futures-research`**. Read [CLAUDE-PROMPT.md](CLAUDE-PROMPT.md) and follow its complete build brief. All paths in that prompt are relative to the repository root.

Create a new implementation branch from this handoff branch before building. Write the HTML experience to `presentations/halal-mmm/`. Keep the paper and handoff inputs unchanged. This handoff does not authorize a deployment or push of the future implementation.

## Inputs

| Read | Purpose |
| --- | --- |
| [Canonical Markdown](../../research/halal-cultivated/paper/paper.md) | Full research wording, 13 sections, five appendices, bibliography and 177 authored notes. Highest content authority. |
| [Existing reader](../../research/halal-cultivated/paper/index.html) | Complete rendering and 251 note-reference occurrences, including reused notes. Content/navigation reference, not target styling. |
| [Reviewed PDF](../../research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.pdf) and [Word](../../research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.docx) | Existing print and editable-document references. Final author and scholarly review remain pending. |
| [Design brief](design/DESIGN-BRIEF.md) | MMM rules for this paper and known conflicts resolved. |
| [MMM skill](design/mmm/SKILL.md), [design system](design/mmm/readme.md), [illustration guide](design/mmm/guidelines/illustration.md) | Actual supplied brand guidance and research-figure expectations. |
| [CSS entry point](design/mmm/styles.css) | Loads `foundations/`: the original token directory is renamed to avoid the repository's credential-related filename exclusions. |
| [Existing MMM entry](design/reference/observatory-reference.html) and [reference notes](design/reference/REFERENCE-NOTES.md) | Substantial layout and interaction example. Its research is unrelated and must not become content in this paper. |
| [Figure plan](design/FIGURE-PLAN.md) and [figure data](../../research/halal-cultivated/paper/figure-data.json) | Proposed source-grounded diagrams; preserve the existing figures' substance. |
| [Process SVG](../../research/halal-cultivated/paper/figures/figure-1-process.svg), [country SVG](../../research/halal-cultivated/paper/figures/figure-2-countries.svg), [audit SVG](../../research/halal-cultivated/paper/figures/figure-3-audit.svg) | Editable reviewed figures; matching PNG files are alongside them. |
| [Source register](../../research/halal-cultivated/paper/source-register.json), [citation audit](../../research/halal-cultivated/paper/citation-audit.json), [coverage](../../research/halal-cultivated/paper/coverage.json), [appendix data](../../research/halal-cultivated/paper/appendices-data.json) | Consult selectively for source status, evidence drilldowns and preservation. Raw private captures are not supplied. |
| [Content contract](CONTENT-CONTRACT.json), [acceptance checklist](qa/ACCEPTANCE.md), [provenance](PROVENANCE.json) | Exact content inventories, required checks and original-input hashes. JSON paths are repository-root relative unless explicitly labeled as source-package paths. |

The default is a continuous MMM research entry: warm paper, a short visual overview, the entire paper, left contents navigation, right-hand explanations, geometric figures, and light/dark modes. A Basmati-style visual-overview/full-research pair is optional only if the author selects it. No personal anecdote, new series numeral, research conclusion or institutional approval should be invented.

The PDF alone is not the design brief: use Markdown for structure and citations, SVG/data for figures, and MMM source files for the visual system. Font binaries are absent; automatic remote font imports are disabled in this repository reference edition. The desired families remain Newsreader and IBM Plex Mono, with local fallbacks. See the reference notes before interpreting fallback rendering as the intended typeface.

## Verification and scope

Run the existing commands in the [repository README](../../README.md), then rebuild and require no generated-file drift. Inspect the eventual page at phone, tablet and desktop widths, with keyboard navigation, both themes and reduced motion. Report actual results in `presentations/halal-mmm/QA.md`; unperformed checks stay unperformed.

This branch prepares Claude to build the HTML. The finished MMM HTML does not yet exist. The manuscript remains an AI-assisted working draft with human verification pending. The original local package is preserved separately; no ZIP, private captures, interview, credentials, Git metadata or editor integration scripts are added here.
