# Sentient Futures Protein Research

Research drafts, data, and source references maintained by **Muhammad Umar Zafar** for peer and mentor feedback during the Sentient Futures Project Incubator.

**Start with [the research library](index.html)** or the document links below. HTML files render when downloaded and opened in a browser; GitHub's file viewer displays their source. The Markdown literature review and policy table can be read directly on GitHub.

These are **AI-assisted working drafts with human verification pending**, not finished or mentor-endorsed studies. Each document retains its original evidence cutoff. The current direction is an India–Pakistan consumption brief with related forecast-methodology work; the broader research below is background for that direction. [Current scope](CURRENT-SCOPE.md).

## Research

| Document | What it contains | Evidence cutoff |
| --- | --- | --- |
| [Protein Transitions Across Unequal Food Systems](research/comparative-protein/README.md) | Comparative synthesis; supply data, adoption, research and talent policy, charts, and capability locators | 13 Sep 2026 |
| [AI and the Protein Transition](research/ai-protein/literature-review.md) | Literature review connecting technical progress, adoption, displacement, and policy | 11 Sep 2026 |
| [Policy Evidence to Decision Table](research/ai-protein/policy-decisions.md) | Six conditional policy discussion areas and evidence that would alter them | 11 Sep 2026 |
| [Alt-Protein and Food-Systems Orientation](research/orientation/food-systems-briefing.html) | Earlier technology, capital, talent, regulation, and foresight briefing | 5 Sep 2026 |
| [Alt Protein Without the Jargon](research/orientation/beginners-guide.html) | Earlier introduction to technologies, terminology, and the value chain | 5 Sep 2026 |

## Sources and data

- [Searchable source catalog](sources/index.html), [CSV index](sources/catalog.csv), and [JSON catalog](sources/catalog.json): public references retained in the included research, with occurrences linking back to original source IDs.
- Original registers: [60 comparative-report records](research/comparative-protein/source-register.json) and [44 literature-foundation records](research/ai-protein/source-register.json).
- [Country supply CSV](research/comparative-protein/protein-data.csv), [figure inputs and provenance](research/comparative-protein/figure-data.json), and [data dictionary](DATA-DICTIONARY.md).
- [Cited-passage review ledger](research/comparative-protein/claim-ledger.json) and [RIS bibliography](research/ai-protein/references.ris).

The country file has 12 populated cases and one missing case. Supply is not measured dietary intake; capability locations are not employment rankings. The source catalog covers this curated collection, not every private note or every publication in the field. Third-party originals remain at their source links.

## Read locally

Download the repository ZIP, extract it, and open `index.html`. Navigation, report controls, and source search work locally without installing dependencies. External source links require internet access.

For an optional local server with Node.js 22 or newer:

```sh
node tools/serve.mjs
```

Open the loopback URL printed by the command. The server exposes only files listed in the shareable manifest. It does not expose Git metadata or parent directories.

## Check and maintain

No package installation, Python environment, or API keys are required.

```sh
node tools/build-library.mjs
node tools/verify.mjs
```

The build regenerates the reading portal, combined catalog, and checksums. Verification checks source coverage, relative links, citation IDs, derived figures, file integrity, and common privacy hazards. It does not rerun the original research, access restricted databases, check live source availability, or certify factual accuracy.

Read [research method and AI-use disclosure](RESEARCH-METHOD.md), [feedback guidance](CONTRIBUTING.md), and [rights and reuse](RIGHTS-AND-REUSE.md). No blanket license or institutional endorsement is implied.

## What is excluded

Personal application and career material, meeting preparation, unpublished peer drafts and comments, private document links, credentials, raw working logs, Office originals, and downloaded third-party publications are excluded. The repository contains a curated snapshot, not the original workspace or its history.
