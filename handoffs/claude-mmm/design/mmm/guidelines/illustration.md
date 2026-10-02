# Illustration — figures that explain

Binding guidance for diagrams in Meaning, Man and Model entries. Read it together with `readme.md` before building or revising any entry. The reference implementation is Entry III, the Pakistan AI Policy Observatory. Its generator is `tools/build_html_report.mjs` in the PDP-2026 repository; the public copy is `03-pakistan-ai-policy-observatory/index.html` in `github.com/Omarzaf/MMM`, live at `meaning-man-and-model.vercel.app/pakistan-ai-policy-observatory.html`.

## The expectation

A research-substantial entry (every Project, and any Essay built on data or a formal model) **explains its hard ideas with figures by default**. Prose carries the argument; figures carry structure the reader would otherwise have to hold in their head.

Plan the figures before writing the page. For each numbered section, ask one question: *does this section rest on a sequence, a hierarchy, a proportion, a distribution in time, or a comparison across groups?* If it does, and the entry has the data, that section gets a figure. In practice:

- **One overview figure near the top.** It shows the whole record at a glance and introduces the entry's visual vocabulary (Fig. 01 in the observatory: every record on one orrery).
- **One figure per major argument** that has structure (the observatory has ten figures across nine sections).
- **Small inline marks** that repeat a figure's encoding in lists and tables, so a reader can scan them (a five-stop rung track on every ledger row).
- **A short personal essay or dialogue** with no data may have no figures. A figure that is decoration fails the test; a figure that answers "how do these parts relate?" passes.

## Visual language

Everything is line geometry from the series mark and glyphs: rings, orbits, ellipses, radial ticks, rules, single points. No fills except small data points, no gradients, no shadows, no 3D, no pictograms, no charting libraries. Draw inline SVG by hand or generate it in code.

- **Strokes.** 0.6–1.2px. Structure uses `--ink-7` (faint) and `--ink-5`; emphasis uses `--ink-3`/`--ink-2`. Use CSS custom properties, never hex, so both themes work.
- **Encoding a confidence or quality scale.** Filled point (`--ink-3`) = strong, hollow point (`--ink-5` stroke) = medium, dashed hollow point = weak. Reuse one encoding across every figure in an entry and state it once in a caption.
- **Copper.** At most one copper point per figure, marking the single thing the figure is about: the empty centre, the gate nobody passed, the step no script performs. Copper is never a fill or a line.
- **Type inside figures.** Only two roles. IBM Plex Mono uppercase, tracked 0.06–0.12em, 7.5–10px, for labels; Newsreader 12–15px for counts and names. Never a third style.
- **Labels that sit on a ring or rule.** Put a paper-coloured plate behind them (a `rect` filled with `--surface-page`) so the line breaks cleanly; a text halo alone leaks through letter-spacing. Leave an empty wedge at the top of radial figures for orbit labels.
- **Motion.** At most one slow drift, such as an outer tick ring rotating once per 180s, and it must stop under `prefers-reduced-motion`. Hover states are a 160ms scale or tint.

## Pattern catalogue

Pick the pattern that matches the structure of the idea, not the one that looks best. Every pattern below was built for the observatory from its dataset.

| Pattern | Use it for | Construction |
| --- | --- | --- |
| **Orrery / orbit map** | The whole record at once: items by stage (orbit) and category (sector) | Concentric orbits = ordered stages, outermost = earliest. Sectors = categories, split by dotted radial rules and numbered at the rim. One point per item, spaced within its sector; an empty centre is the unreached end state. Pair with a key and a hover readout in the rail. |
| **Ladder / dot strips** | Counts per stage, split by quality | One row per stage; one point per item, ordered strong → weak; a copper point flags the row whose quality breaks the pattern. |
| **Grounding rings (small multiples)** | *Why* a pattern holds: what each group rests on | One small orrery per group; the claim is at the centre, rings step outward by how directly the evidence speaks to it, and a dashed rim holds items with no direct evidence. The comparison across panels is the finding. |
| **Corridor / pipeline** | A process where items stall at a gate | Stations on one rule; items stacked above their station. A double rule marks the gate; the rule beyond is dashed and its stations are drawn but empty. |
| **Spiral clock** | Coverage or sampling across time of day and days | One turn per day, midnight at the top, winding outward; observed windows are heavy strokes at their true times. A bracket on the rim marks any cluster. |
| **Calendar axis + undated orbit** | What falls due, and what has no date | A day axis from "now" (a copper point), with items at their dates; undated items sit on a separate dashed orbit, which makes the count of unscheduled items visible. |
| **Hierarchy orbit** | A population sorted by tier | Rings by tier, nearest the centre = most direct; one point per member, spread evenly with a label wedge at the top. |
| **Dot matrix** | Category × stage | A row per category, a column per stage, a cell of points (confidence-encoded) and an em-rule for empty cells. Rows can be buttons that filter a list. |
| **Rung track (inline)** | Repeating a figure's position encoding on every row of a list | A 100 × 14 SVG: a faint rule, five small stops, the item's stop drawn as its quality mark. Define the base once with `<symbol>`/`<use>`. |
| **Timeline with coverage ticks** | Events per day against when anyone was watching | Events stacked above a day axis; observation windows as ticks on a second rule below; copper ticks for empty days. |

## Honesty rules

- **Every figure is computed from the entry's data at build time.** Nothing is hand-placed to look right, and no number appears in a figure that is not in the data.
- **Every derived classification is a documented, checkable rule.** Examples: a stage read from a status string, or a tier read from a source type. Write the rule as an ordered keyword list beside the code where the first match wins, and keep the verbatim input visible somewhere on the page so a reader can argue with a placement.
- **Captions say what the encoding means and what the figure does not show.** Use the form `FIG. NN — SHORT NAME`, then two to four plain sentences. State an absence as a finding ("no record reaches it", "no award was verified"), not as an empty chart.
- **Each figure needs a `<title>` and `<desc>`.** The `<desc>` gives the figure's numbers as a sentence, so the data is available without the drawing.

## Layout and interaction

- **Placement.** Figures sit in the content column with their caption in the right rail; the rail caption is the figure's marginalia. Figures too wide for the column (small multiples, corridors, calendars, matrices) span column + rail, with the caption beneath at prose measure. Below the rail breakpoint, captions fold under the figure.
- **Naming.** Give the full-width modifier a unique name (the observatory uses `.figure-block.full`). Check it doesn't collide with an existing class: `.wide` was already taken by table sections and silently capped figures at 760px.
- **Phones.** Square figures scale down. Wide figures scroll horizontally inside their frame (`.scroll-x`, SVG at a fixed 760px) instead of shrinking their labels to unreadable sizes. The page itself must never scroll sideways.
- **Points are links.** Each data point is an `<a>` to its record in the page's ledger or register, carrying a `<title>` for the tooltip and accessible name. The target row opens its details and is marked with copper. Use `role="group"` for SVGs that contain links and `role="img"` for static ones.
- **Keys and rungs filter the list below.** A domain key or a ladder row sets the same filter as the list's own controls, then scrolls to it.
- **Weight.** Keep point markup lean: href, one data attribute and a `<title>`. Read other details from the target row at hover time. Draw spirals with arc segments, not thousands of line segments.

## Checklist before shipping an entry

- [ ] Every numbered section with structural content has a figure, or a stated reason not to.
- [ ] One encoding for quality or confidence, used everywhere and stated once.
- [ ] No more than one copper point per figure.
- [ ] Every classification rule is in the code beside its figure and matches the data.
- [ ] Every figure has `<title>`, `<desc>` and a `FIG. NN` caption.
- [ ] Every point link lands on a real row (run a link and anchor audit).
- [ ] The figures read in both themes, at 1440px, 1280px and 375px, with no page-level horizontal overflow.
- [ ] Reduced motion stops the drift.
