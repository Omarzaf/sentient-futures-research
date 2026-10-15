# Design spec: Pakistan–India protein edition

These are the author-approved decisions from 13 October 2026. The working reference is `preview/index.html`, served by `preview/extract.py`. When the preview and this file disagree, this file wins.

## Decisions already made

- **Style:** editorial long-read, the same family as the published halal paper.
- **Scope:** everything in INVENTORY.md marked E, plus the Phase Two search, surveys, halal summary and benchmark.
- **Review flags:** corrected and disclosed. The Pakistan model appears as a range, labelled experimental. Partial milestones are named.
- **Kashmir:** Jammu and Kashmīr, Ladākh, Azad Kashmir and Gilgit-Baltistan are drawn hatched with no data colour, following UN and World Bank practice. Their values stay in tooltips and tables.
- **Audience:** public. Supervisors read it first.

## Visual system

| Token                          | Light                             | Dark                              |
| ------------------------------ | --------------------------------- | --------------------------------- |
| Page                           | `#f4f1ea`                         | `#1c1815`                         |
| Ink (display / body / support) | `#1f1c18` / `#36322c` / `#6e685b` | `#f3ede1` / `#ddd5c5` / `#a89c85` |
| Rule                           | `#d6cfbd`                         | `#40372d`                         |
| India                          | `#2a6cb5`                         | `#4f8fd6`                         |
| Pakistan                       | `#c4572a`                         | `#d46e3c`                         |

- The India/Pakistan pair passed the dataviz validator in both modes: CVD ΔE 20.9 light / 21.8 dark, every check passing. Any new categorical colour must pass `validate_palette.js` against these page colours.
- Each map gets its own single-hue sequential ramp from soft to full country colour.
- Type: Newsreader for text and display, IBM Plex Sans for chart text and notes, IBM Plex Mono for labels and tier badges.
- Prose measure is 64 characters.
- The theme follows the operating system, with a toggle that stores its choice in `localStorage` inside try/catch.
- The layout works at 390 px with a 16 px gutter and no horizontal scroll.
- Motion: reveal on scroll, lines drawing in, dot grids filling. `prefers-reduced-motion` turns all of it off.
- Print: no sticky elements, every scrolly step visible, one chapter per page.

## Every chart

- A title that states the takeaway in plain words, a unit line, and a legend when there are two or more series. Country labels sit at the line ends.
- Hover tooltip on every mark, kept inside the viewport.
- A source line under the chart: source name, tier badge, years, and the one caveat that changes its meaning.
- A "Show data" toggle that opens the exact rows as a table.
- One y-axis per chart. Incompatible methods go in separate panels (review finding M10).
- Values that are not comparable across countries get separate scales and a sentence saying so.

## Chapters

| #   | Title (working)                        | Content and main visual                                                                                                                                          | Sources                        |
| --- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| 1   | Two neighbours, one protein question   | Title, byline, status pill, four paired numbers with bars                                                                                                        | FBS, SOFI, JME                 |
| 2   | What we found                          | 8–10 findings, each one line plus a link to its chapter                                                                                                          | claims.csv                     |
| 3   | A food is accepted before it is bought | Animated driver diagram (five drivers → acceptability → trial, purchase, habit) and five driver notes                                                            | India–Pakistan brief           |
| 4   | How much meat, and what kind           | Pinned scrolly: poultry, pulses, milk, then the OECD 2034 projection drawn apart. Seven small multiples below.                                                   | FBS, OECD-FAO                  |
| 5   | Where people eat it                    | Twin maps with the Kashmir rule. An urban/rural toggle where the data allow. Ranked bar fallback at 390 px.                                                      | NFHS-5, HIES 2024–25, NNS 2018 |
| 6   | What is on the plate                   | Diet composition by income group. The HIES chicken gradient (0.17 → 0.65 kg per person per month). India protein shares by food group.                           | HCES, HIES Table 23            |
| 7   | Protein against need                   | India's HCES group means against EAR and RDA scenarios. Pakistan's repaired model as a range band, in its own panel. A "why this is not a deficiency rate" note. | HCES, HIES model               |
| 8   | Who is at risk                         | Healthy-diet affordability lines. Stunting dot grids. Undernourishment. The "Do not add" box.                                                                    | SOFI 2025, JME                 |
| 9   | Supply futures to 2035                 | Benchmark forecasts with intervals, the coverage result (1/6 India, 6/6 Pakistan), and the "supply is not adoption" boundary                                     | `future-research`              |
| 10  | Alternative proteins                   | Pulse feedstock scale, the company status timeline including closures, and an India/Pakistan policy timeline                                                     | M5 tables                      |
| 11  | What consumers say                     | The 9 studies as a sample-size dot plot by country and measure, the do-not-pool rule, and Phase Two data leads                                                   | Surveys, Phase Two             |
| 12  | Halal and cultivated chicken           | One-screen summary and a link to the published paper                                                                                                             | Phase One paper                |
| 13  | Culture                                | Matrix of 8+ dimensions per country, each cell cited                                                                                                             | `cultural_context.csv`         |
| 14  | What holds, and what is still open     | Holds/partial cards from REVIEW-FIXES.md, sentiment status, open gaps, data requests                                                                             | REVIEW-FIXES, GAPS             |
| 15  | Methods and sources                    | Tier legend, how the numbers were checked, a searchable source ledger, and CSV downloads as data URIs                                                            | `sources.csv`, `claims.csv`    |

## Top bar and navigation

A sticky bar shows the India · Pakistan mark, the current chapter name and the theme toggle. A two-colour progress line runs along its bottom. A contents list after the opening links every chapter. Every chapter heading has an anchor link.
