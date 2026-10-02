# Meaning, Man and Model — Design System

> Repository edition: this is a selected design-reference bundle. Original `tokens/` files are renamed `foundations/`; automatic remote font imports are disabled, so the supplied fallbacks are used until licensed local fonts are supplied. Historical specimen cards, the runnable blog UI kit and component prompt examples are omitted. Their mentions below describe the original full skill. Use the repository handoff brief when historical examples conflict.

The visual system for **Meaning, Man and Model**, a series by Umar Zafar on AI, society, and the projects and conversations in between. Entries come in three kinds: **Essay**, **Project**, and **Dialogue**.

The system was authored from scratch for this series. The stated visual reference was *The Way of Code* (thewayofcode.com) — warm paper grounds, wide-tracked serif display type, generous whitespace — combined with the geometric, astronomical language of the Voyager Golden Record cover: concentric rings, radial tick marks, orbital diagrams.

**Sources:** no codebase, Figma file, or brand assets were provided. Everything here derives from the series page built in this project (`Meaning Man and Model.dc.html`), the first real entry (`Research and Writing/Mecca Pact/`), and the design review recorded in `DESIGN-REVIEW-2026-08-18.md`.

> **Revision note (2026-09-25):** figures are now expected on research-substantial entries, not rationed to one. See **Figures** below and `guidelines/illustration.md`, written from the Pakistan AI Policy Observatory (Entry III), which is the reference implementation.
>
> **Revision note (2026-08-18):** this document was substantially revised after Umar reviewed the Mecca Pact draft and gave direct feedback. Read `DESIGN-REVIEW-2026-08-18.md` for the reasoning behind each change and the open work it hands off. The rules below are the current, binding version — where they differ from anything in an older entry file, this document wins.

## Index

- `styles.css` — the entry point; imports everything below.
- `foundations/` — `fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `motion.css`.
- `components/core/` — SeriesMark, TypeGlyph, MonoLabel, DashedRule, EntryRow, Figure, MetaList, plus the new entry-chrome primitives: `LeftNav`, `MarginRail` (with `MarginNote` / `MarginThought` variants), `TLDR`, `Endnotes`, `ThemeToggle`.
- `ui_kits/blog/` — the series index and entry page, click-through.
- `guidelines/` — foundation specimen cards (specimens for the new components are outstanding — see the review doc), and `guidelines/illustration.md`, the binding guide to figures: when to draw them, the pattern catalogue, construction and honesty rules.
- `assets/` — the series mark and the three entry glyphs, as SVG.
- `SKILL.md` — packaging for use as an Agent Skill.
- `DESIGN-REVIEW-2026-08-18.md` — the brief for whoever (human or agent) builds the next entry or extends this system further.

## Visual foundations

**Ground.** One paper colour per mode, `--paper-1`. Light is warm paper (#f4f1ea); dark is a warm near-black (#1c1815) — a deliberately designed second ground, not an inverted negative of the light one. See **Dark mode** below. Sections are separated by rules, not by blocks of colour.

**Ink.** A seven-step warm-grey ramp from `--ink-1` (display) down to `--ink-7` (faint numerals and tick marks), redefined per mode. Text tone carries hierarchy; size and weight do less work than in most systems.

**Accent.** `--copper` (#8a5a3b) appears exactly once per view, as a point: the orbiting body in a Project glyph, the outer planet on the series mark, a link on hover. It is never a fill, a background, a border, or a button — and it never changes between light and dark mode. It's the one constant that makes an entry recognizably part of the series regardless of theme.

**Type.** Five roles, and only five — see `foundations/typography.css` for the full breakdown:

1. **Display** — the series title only. Uppercase, tracked 0.09em, weight 400.
2. **Heading** — entry titles (46px), section h2s (30px), subhead h3s (21px). Sentence case, one shared style, differentiated by size only.
3. **Body** — Newsreader prose, 18px / 1.78, 64ch measure.
4. **Mono-label** — every uppercase tracked tag in the system (citations, section numbers, eyebrows, matrix headers, figure captions, dates). One style, three fixed sizes (sm/md/lg). Nothing invents a fourth.
5. **Marginalia** — the right-rail personal-notes voice. Running italic Newsreader, larger and looser than body, never mono, never uppercase. This is the one register written to sound like Umar thinking on the page, not the system labeling something.

Before adding any new type treatment anywhere in an entry, it must be justified as one of these five roles. If it doesn't fit, it's very likely decorative and shouldn't exist.

**Layout.** Three zones on an entry page: a **left rail** (200px, sticky contents nav), a **content column** (max 760px), and a **right rail** (300px, the marginalia rail). Left gutter 48px, right gutter 76px — the right gutter stays wider because it separates two different *kinds* of reading (argument vs. marginalia), while the left gutter separates content from pure navigation chrome. The series index page remains a single centred column; only entry pages get the three-zone frame. The 1120px page max applies to the index. An entry's three zones need about 1384px (200 + 48 + 760 + 76 + 300) and step down gracefully: the rail narrows to 260px below 1400px, folds inline below 1240px, and the left nav hides below 980px. Wide figures and ledgers may span the content column and the right rail together.

**Rules.** One radius exists: `--radius-image` (2px), for images. Nothing else is rounded. There are no shadows, no cards, no elevation. Horizontal rules exist only where they mark something real — a new numbered section, or the boundary between prose and an equation/diagram block. They do **not** appear between every row, under every heading, or around every note box; a rule that isn't marking a genuine structural break should be spacing instead (see `--gap-*` tokens in `foundations/spacing.css`). This was tightened in the 2026-08-18 review — the earlier version of this system over-used rules as a default decoration, which read as clutter once a full entry was built out.

**Spacing.** Generous where it aids reading (paragraph-to-paragraph, prose line-height); tight where it's purely structural (heading-to-body, block-to-block). Use the semantic `--gap-*` tokens rather than reaching for a raw `--space-N` so this rhythm stays consistent across entries — see `foundations/spacing.css`.

**Imagery.** Photographs are small and subordinate. They live in the right rail at 230px tall (320px absolute ceiling), 2px radius, hairline border, mono caption beneath in the form `FIG. 0N — DESCRIPTION`. No full-bleed imagery, no hero images, no decorative photography. Figures (diagrams drawn from the entry's data) are different: they sit in the content column or span column and rail, with their caption in the rail — see **Figures** below.

**Motion.** Almost none. The series mark's outer tick ring rotates once every 180 seconds — slow enough to read as drift rather than animation. Hover is a 160ms tint plus an 8px indent on contents rows. No fades on load, no scroll-triggered reveals, no bounce.

**Diagrams.** All marks are line geometry: circles, ellipses, radial ticks, single points. Stroke weights 0.75–1.2px, drawn from `--ink-5` and `--ink-7`. Never filled shapes, never gradients.

## Dark mode

Dark mode is an official, permanent part of the system — not a toggle to be removed. It ships as a real second palette (`[data-theme="dark"]` in `foundations/colors.css`), designed on its own terms rather than mechanically inverted, so it keeps the same warm, considered personality as light mode. Copper stays fixed across both modes. A `ThemeToggle` component sits with the entry chrome (see Mecca Pact draft for the reference implementation, currently ad hoc and due to be rebuilt against the token system per the review doc).

## Entry template: the three-zone frame

Every entry (Essay, Project, or Dialogue) uses the same page chrome — left nav, content column, right rail, dark-mode toggle — for consistency across the series. What varies is how *full* that chrome is, scaled to how substantial the entry is:

- **Left nav (sticky contents)** — only renders if there are genuinely multiple sections to jump between. A short Project or Dialogue entry with two or three sections doesn't force an near-empty nav; it collapses away.
- **Right rail (marginalia)** — always present, never empty. It always carries *something* — even a short personal entry has at least one concept or note worth flagging. See **Marginalia** below for what goes in it.
- **TL;DR** — only appears on entries substantial enough to have compressible findings (typically Essay-type, occasionally a heavily researched Project). It never duplicates the lead paragraph or the thesis line — see below.
- **Endnotes** — only exist if the entry has citations at all. A purely personal Dialogue entry may have none.

### TL;DR

A labeled block (`MonoLabel`-tagged `TL;DR`) directly after the hero, present only on research-substantial entries. It is a short **findings list** — the concrete conclusions compressed to 3–5 lines — and it is structurally and functionally distinct from two things that already exist in the hero:

- the **lead paragraph** (one sentence, what the piece is about)
- the **thesis line** (the italic claim-statement — the *argument*)

The TL;DR is the *findings*, not the argument and not the topic description. If a piece has nothing to compress beyond its thesis line, it doesn't get a TL;DR.

### Sources: hyperlinked, and living in endnotes

Every citation must link to its actual primary source — no citation tag ships without an `href`. Citations no longer live as a static list in the right rail (that was the old Mecca Pact draft pattern); they move to **numbered endnotes** at the bottom of the piece, referenced from the body as superscript markers that jump down. This frees the entire right rail for marginalia — the rail is Umar's margin, not a bibliography.

### Marginalia (right rail)

The right rail carries three kinds of content, and the distinction between the first two must be visually obvious at a glance, not just tonal:

- **Notes / concepts learned** — written in first person, in Umar's own voice, as if jotted in the margin while researching: "I hadn't realized how much of alliance credibility comes down to subgame perfection — a treaty can promise anything, but if honoring it wouldn't be rational in the moment, the promise doesn't deter." Set in the **Marginalia** type role (italic Newsreader, no mono treatment) — this is the one part of the page that should read as unmistakably human and unpolished, not systematized.
- **Explanations** — factual, dictionary-style definitions of a term or concept, e.g. "Subgame perfection: an equilibrium concept requiring that a strategy remain optimal at every point in the game, not just at the start." Set in the normal **Mono-label** rail treatment (uppercase tag + body-style detail) — impersonal and functional, distinct from the notes above.
- **Sources** — moved to endnotes (see above); no longer rail content.

A future agent building a new entry should be able to look at the research notes/report for that piece and pull marginalia directly from wherever the writer (Umar) flagged something as "TIL" or "worth explaining" during research — this is why the two-stage research→draft process matters (see `DESIGN-REVIEW-2026-08-18.md`).

## Figures — explain hard ideas with drawings, by default

Every research-substantial entry (each Project, and any Essay built on data or a formal model) explains its structure with figures, planned before the page is written. Read `guidelines/illustration.md` before building an entry; it is binding. In short:

- **Plan per section.** For each numbered section ask whether it rests on a sequence, a hierarchy, a proportion, a distribution in time, or a comparison across groups. If it does and the data exists, it gets a figure.
- **Open with an overview figure** that shows the whole record and teaches the entry's visual vocabulary, then add one figure per argument with structure. Repeat a figure's encoding as small inline marks in lists and tables (for example a five-stop rung track on every ledger row).
- **Line geometry only:** rings, orbits, ticks, rules and single points in the series' ink tokens; one quality encoding (filled / hollow / dashed) used throughout; at most one copper point per figure. No charting libraries, fills, gradients or pictograms.
- **Pick the pattern that matches the idea:** orrery, ladder, grounding rings, corridor, spiral clock, calendar axis, hierarchy orbit, dot matrix or inline track. The catalogue in the guide says when each fits.
- **Data-derived and checkable.** Every figure is computed from the entry's data, every derived classification is a documented ordered rule, and every figure has `<title>`, `<desc>` and a `FIG. NN — NAME` caption in the rail.
- **Interactive where it helps reading.** Points link to their record in the ledger; keys and rungs filter the list below.

A short personal essay or dialogue with no data may have no figures. The test is still *would this be hard to hold in your head from prose alone?* The difference from the earlier rule is that a research entry usually has several such ideas, not one, and each deserves its own drawing. Interactives beyond figures (a live slider, a payoff matrix) remain content-driven, as before.

## Content fundamentals

First person, past tense, plainly stated. The series writes about what was built and what happened, not about what technology means in the abstract.

- **Titles** are sentence case and admit something: "Building a grief companion, badly", "A search engine that admits what it doesn't know."
- **Excerpts** are one sentence, concrete, and stop early: "What broke first when I tried to automate comfort."
- **Thesis lines** — the italic line under each title — state the claim without hedging: "A model can reproduce a voice. It can't carry the fact that the person is gone."
- **Labels** are uppercase mono and factual: `ENTRY I — PROJECT — AUGUST 2026`, `STATUS — SHELVED, DELIBERATELY`.
- **Numbering** uses Roman numerals for entries and for the colophon year (MMXXVI). Arabic numerals appear only in figure numbers and dates.

No exclamation marks. No emoji, anywhere. No second-person marketing address ("you'll love…"), no rhetorical questions as headings, no "here's why this matters." The tone is a working notebook, not a publication pitch. The one deliberate exception is the marginalia rail, which is allowed — expected — to sound like a person, not a publication.

## Iconography

There is no icon library and none should be added. The only marks in the system are the **series mark** and the **three entry glyphs**, all in `assets/` as SVG:

- `series-mark.svg` — concentric rings, a 24-tick rotating outer ring, an orbital ellipse, one copper point.
- `glyph-essay.svg` — a single ring.
- `glyph-project.svg` — a ring with an orbiting body (the copper point).
- `glyph-dialogue.svg` — two intersecting orbits.

If a UI affordance genuinely needs an arrow, use the typographic characters `←` and `→`. Unicode over icon fonts; no emoji.

## Intentional additions

- **MonoLabel, DashedRule** — no external source defined a component inventory, so the primitives here were extracted from the series page itself rather than borrowed from a generic system. Nothing that the page does not use has been invented: there are no buttons, inputs, modals, toasts, or tabs, because the series has none.
- **LeftNav, MarginRail (MarginNote/MarginThought), TLDR, Endnotes, ThemeToggle** — added 2026-08-18, extracted from the same review that revised this document. See `DESIGN-REVIEW-2026-08-18.md` for full rationale; the components currently ship as stubs and need to be built out against the Mecca Pact draft as the reference implementation.

## Caveats

- **Fonts** are loaded from Google Fonts (Newsreader, IBM Plex Mono); no licensed binaries were supplied. Replace `foundations/fonts.css` with `@font-face` rules if brand-owned files become available.
- **No logo** was provided. The series mark is an original geometric device made for this project, not a reconstruction of any existing brand; the wordmark is simply the title set in Newsreader.
- **Imagery** is unresolved — the entry template ships with an empty figure frame, since no photography or diagram style has been chosen yet.
- **The Mecca Pact draft predates this revision.** It is the reference for *content depth and bespoke-diagram ambition*, but its layout (top TOC, right-rail sources, no left nav, ad hoc dark toggle, dense rule usage) does not yet match the rules above. Rebuilding it against the new frame is the first item in `DESIGN-REVIEW-2026-08-18.md`.
