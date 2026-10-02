# Sentient Futures Protein Research

Research drafts, data, and source references maintained by **Muhammad Umar Zafar** for peer and mentor feedback during the Sentient Futures Project Incubator.

**Start with [the research library](index.html)** or the document links below. HTML files render when downloaded and opened in a browser; GitHub's file viewer displays their source. The Markdown literature review and policy table can be read directly on GitHub.

These are **AI-assisted working drafts with human verification pending**, not finished or mentor-endorsed studies. Each document retains its original evidence cutoff. The current direction is the India–Pakistan consumption brief, the halal conditionality workstream, and the survey-data package below, with related forecast-methodology work still outside this repository; the broader research is background for that direction. [Current scope](CURRENT-SCOPE.md).

## Research

| Document | What it contains | Evidence cutoff |
| --- | --- | --- |
| [Cultivated Chicken and Halal Market Access](research/halal-cultivated/paper/index.html) · [Markdown](research/halal-cultivated/paper/paper.md) | **Working paper for author review.** Approximately 11,900 words, three figures, five appendices and audited citations. Independent agent checks complete; human scholarly review pending | 2 Oct 2026 |
| [Protein Consumption and Alternative Protein Adoption in India and Pakistan](research/india-pakistan/india-pakistan-brief.md) | **Current scope.** Comparative brief on affordability, dietary practice, legitimacy, certification, and policy; proposed comparative tests and forecast-question requirements | 14 Sep 2026 |
| [Cultivated Chicken in the Focal Countries: Where the Evidence Stands](research/halal-cultivated/phase1-continuation/SYNTHESIS.md) | **Current workstream, in progress.** October continuation: country-by-country answer, gate table across six process profiles, 188 source records and 156 claims, open leads and questions for mentors | 2 Oct 2026 |
| [Cultivated Chicken: Religious Conditions and Market Access](research/halal-cultivated/phase1/review.md) | **Current workstream.** Phase One review: 45 school questions, seven countries, four historical comparisons, evidence registers and a Phase Two handoff; uncertainty and scholarly-review limits retained | 30 Sep 2026 |
| [Alternative Meat Survey Data](research/protein-survey-data/Source_Links.html) | Structured extraction from nine Muslim-country and Southeast Asian survey studies and reports; 29 retained findings, sample caveats, source links and workbook CSV exports | 30 Sep 2026 |
| [Protein Transitions Across Unequal Food Systems](research/comparative-protein/README.md) | Comparative synthesis; supply data, adoption, research and talent policy, charts, and capability locators | 13 Sep 2026 |
| [AI and the Protein Transition](research/ai-protein/literature-review.md) | Literature review connecting technical progress, adoption, displacement, and policy | 11 Sep 2026 |
| [Policy Evidence to Decision Table](research/ai-protein/policy-decisions.md) | Six conditional policy discussion areas and evidence that would alter them | 11 Sep 2026 |
| [Alt-Protein and Food-Systems Orientation](research/orientation/food-systems-briefing.html) | Earlier technology, capital, talent, regulation, and foresight briefing | 5 Sep 2026 |
| [Alt Protein Without the Jargon](research/orientation/beginners-guide.html) | Earlier introduction to technologies, terminology, and the value chain | 5 Sep 2026 |

## Sources and data

- [Searchable source catalog](sources/index.html), [CSV index](sources/catalog.csv), and [JSON catalog](sources/catalog.json): public references retained in the included research, with occurrences linking back to original source IDs.
- Original registers: [20 India–Pakistan review records](research/india-pakistan/source-register.json), [60 comparative-report records](research/comparative-protein/source-register.json), and [44 literature-foundation records](research/ai-protein/source-register.json).
- [Phase One evidence and review](research/halal-cultivated/phase1/README.md): 74 claims and 76 public-source records. The earlier [CSV data package](research/halal-cultivated/datapackage.json) remains a separate discovery and Phase Two schema.
- [Survey data package](research/protein-survey-data/README.txt): nine studies, 29 findings, two workbook-sheet CSV exports, machine-readable CSVs, JSON and source-link page. No respondent-level data or publisher PDFs are bundled.
- [Country supply CSV](research/comparative-protein/protein-data.csv), [figure inputs and provenance](research/comparative-protein/figure-data.json), and [data dictionary](DATA-DICTIONARY.md).
- [Cited-passage review ledger](research/comparative-protein/claim-ledger.json) and [RIS bibliography](research/ai-protein/references.ris).

The country file has 12 populated cases and one missing case, and does not include Pakistan. Supply is not measured dietary intake; capability locations are not employment rankings. The India–Pakistan brief reads each country's statistics within its own survey design rather than placing them on a single intake scale. The source catalog covers this curated collection, not every private note or every publication in the field. Third-party originals remain at their source links.

## Read locally

Download a clean ZIP or archive of this file tree, extract it, and open `index.html`. Navigation, report controls, and source search work locally without installing dependencies. External source links require internet access. Do not treat every Git branch, pull request, or historical object as part of the shareable library.

For an optional local server with Node.js 22 or newer:

```sh
node tools/serve.mjs
```

Open the loopback URL printed by the command. The server exposes only files listed in the shareable manifest. It does not expose Git metadata or parent directories.

## Check and maintain

For the MMM HTML build, start with the [Claude handoff](handoffs/claude-mmm/START-HERE.md) and its [complete prompt](handoffs/claude-mmm/CLAUDE-PROMPT.md). It supplies the design system, reference entry, figure plan and content-preservation checks while reusing the canonical paper and exports. The resulting reading edition is in [presentations/halal-mmm](presentations/halal-mmm/README.md): a local build for author review, not published, with its [QA report](presentations/halal-mmm/QA.md).

Agents continuing the October workstream should read the [2 October repair report and handoff](research/halal-cultivated/phase1-continuation/REPAIR-REPORT-2026-10-02.md): the five resolved findings, repair commit, regression results and remaining research gates.

No package installation, Python environment, or API keys are required.

```sh
node tools/build-library.mjs
node tools/verify.mjs
node tools/test-halal-checks.mjs
node tools/test-phase1-checks.mjs
node tools/test-survey-checks.mjs
node tools/test-privacy-checks.mjs
```

The build regenerates the reading portal, combined catalog, and checksums. Verification checks source coverage, relative links, citation IDs, derived figures, survey-package consistency, file integrity, and common privacy hazards. It does not rerun the original research, access restricted databases, check live source availability, or certify factual accuracy.

Read [research method and AI-use disclosure](RESEARCH-METHOD.md), [feedback guidance](CONTRIBUTING.md), and [rights and reuse](RIGHTS-AND-REUSE.md). No blanket license or institutional endorsement is implied.

## What is excluded

Personal application and career material, meeting preparation, unpublished peer drafts and comments, private document links, credentials, raw working logs, Office originals, downloaded third-party publications, and respondent-level survey data are excluded from this clean file tree. The shareable artifact is a curated snapshot/export, not the original workspace, private branches, or full Git history.
