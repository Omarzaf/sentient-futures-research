# Design review — 2026-08-18

Umar reviewed the Mecca Pact draft (`Research and Writing/Mecca Pact/makkah-pact-analysis-meaning-man-draft.html`) and gave direct feedback in conversation. This document is the brief for whoever — human or agent — picks up the work next. `readme.md` has already been updated to reflect every decision below as binding system rules; this file is the *why* and the *what's left*, not a duplicate spec.

Treat this as a punch list, not a suggestion. Everything under "Decided" is locked. Everything under "Outstanding work" is unbuilt and needs doing before the next entry ships.

## Context: what Mecca Pact got right

Before changing anything, understand why Mecca Pact is the reference for *ambition*, even though its layout is being revised. It has: a custom SVG strategic-network diagram with a dozen hand-positioned actor nodes; three interactive sliders that recompute a real deterrence-threshold equation live as you drag them; per-crisis payoff matrices; an equation box; ten well-argued sections. None of that was decorative — every bespoke element mapped to something real in the underlying research report. That discipline (bespoke effort in service of the argument, not for show) is the standard. What's being fixed is the page frame around that content, not the content-generation instinct that produced it.

## Decided (now written into readme.md — implement, don't relitigate)

1. **Spacing.** Tighter vertical rhythm between headings/sections/blocks; generous spacing preserved only where it aids reading (paragraph-to-paragraph, prose line-height). New semantic tokens in `foundations/spacing.css`: `--gap-heading-body`, `--gap-paragraph`, `--gap-block`, `--gap-section`, `--gap-page`. Use these, not raw `--space-N`, when laying out an entry.

2. **Horizontal rules, reduced by frequency (not weight, not eliminated).** Rules now appear only at genuine structural boundaries: a new numbered section, or the prose→equation/diagram transition. Cut: hairline rules between minor rows, the dashed measuring rule under every heading, borders around every note box. `--rule-weight` is unchanged; what changed is *where a rule is allowed to appear at all*.

3. **Typography — five roles, closed set.** Display, Heading (entry title/h2/h3, unified), Body, Mono-label (one style, three sizes: sm/md/lg — citations, section numbers, eyebrows, matrix headers, captions, dates all use this, nothing invents a sixth variant), Marginalia (new — italic Newsreader, right-rail personal voice). Full token definitions in `foundations/typography.css`, with inline comments explaining each role. Before adding any new type treatment to a future entry, it must be justified as one of these five — if it doesn't fit, it's probably decorative.

4. **Left rail: sticky contents nav**, replacing the old top-of-page TOC block. New `LeftNav` component (stub built, needs scroll-spy wiring — see Outstanding work). Only renders when an entry has enough sections to warrant it; short entries collapse to no left nav at all rather than a near-empty one.

5. **Sources → endnotes, always hyperlinked.** Citations move out of the right rail and become numbered endnotes at the bottom of the piece, referenced from the body via superscript markers (`Citation` component) that jump down (`Endnotes` component). Every citation must carry a real `href` to its primary source — the old draft's rail citations were tag + label with no link; that's no longer acceptable.

6. **Right rail repurposed as marginalia**, now that sources have moved out. Two content types, visually distinct, not just tonally different:
   - `MarginThought` — first person, in Umar's own voice, for things he personally learned or is thinking through while researching. Set in the new Marginalia type role (italic, no mono).
   - `MarginNote` — factual, dictionary-style term + definition. Set in the standard mono-label + body treatment.
   The rail should never sit empty — even a short personal entry has at least one thing worth flagging.

7. **Dark mode, formalized and permanent.** Not a toggle to remove — the opposite decision from what the readme previously said ("no dark mode"). New palette in `foundations/colors.css` under `[data-theme="dark"]`: a genuinely designed warm near-black ground (`#1c1815`), not a literal inversion of the light ramp, with copper (`--copper: #8a5a3b`) held fixed across both modes. `ThemeToggle` component stubbed; the Mecca Pact draft's existing toggle predates this token system and needs to be reconciled against it, not kept as-is.

8. **TL;DR block**, for research-substantial entries only. A labeled findings list (3-5 compressed conclusions) placed right after the hero — distinct from the lead paragraph (topic) and the thesis line (argument). `TLDR` component stubbed. Short personal entries should not get one.

9. **Entry-type scaling.** All three entry types (Essay, Project, Dialogue) share the same page chrome (left nav, right rail, dark-mode toggle) for series consistency, but what fills that chrome scales with how substantial the entry is — see readme.md "Entry template: the three-zone frame" for the exact rules per element.

10. **Bespoke-element policy, made explicit.** Custom diagrams/interactives are content-driven: build one flagship bespoke element for the single hardest-to-convey-in-prose idea in the piece; everything else stays in the base component set. Not a quota, not applied uniformly regardless of topic.

## Outstanding work — what the next agent should actually do

In rough priority order:

1. **Rebuild the Mecca Pact draft against the new frame.** This is the reference implementation and should be first. Concretely: move the TOC from top-of-page into `LeftNav` with scroll-spy; move the right-rail source list into `Endnotes` + inline `Citation` markers, all with real hrefs (the deep-research-report.md has the source URLs already — cross-reference them); split the right rail's remaining space between `MarginThought` and `MarginNote` entries pulled from the actual research (see item 3 below for where that content comes from); add a `TLDR` block after the hero (5 findings, pulled from the deep-research-report's executive summary); reconcile the existing night-mode JS toggle against the new `[data-theme="dark"]` token system in `foundations/colors.css`; audit every horizontal rule against rule #2 above and cut the ones that aren't marking a real boundary; audit type sizes against the five-role palette and collapse any one-off label styles found in the draft's `<style>` block.

2. **Wire up the interactive chrome.** `LeftNav`'s `activeId` prop needs a scroll-spy (IntersectionObserver against each section, or scroll-position math) — currently the component accepts the prop but nothing sets it. `ThemeToggle` needs to actually flip `document.documentElement.dataset.theme` and, on the real published site (not a Claude-hosted artifact — this restriction doesn't apply there), persist the choice in `localStorage`.

3. **Define where marginalia content comes from during research**, not just how it's styled. The right rail's `MarginThought` entries should be sourced from wherever the writer flags something as "TIL" / "worth explaining" *during the research phase*, not invented retroactively while building the HTML. If future entries follow a research-report-first workflow (as Mecca Pact did), the research report itself should carry a lightweight marker (even just a `> NOTE:` blockquote convention) for moments worth pulling into the rail later, so the marginalia reads as genuinely captured-in-the-moment rather than manufactured after the fact for design purposes.

4. **Add guideline specimen cards** for the six new components (`guidelines/*.card.html` currently only covers the original inventory: brand-glyphs, brand-mark, brand-numerals, colors, rules, spacing, type). `LeftNav`, `MarginNote`/`MarginThought`, `TLDR`, `Endnotes`, `ThemeToggle` have no specimen card yet — needed so future entries can be built by referencing a rendered example rather than reading component source.

5. **Decide and document the exact left-rail behavior on narrow viewports.** Nothing here specifies what happens to the left nav on a page too narrow for three zones (left rail + 760px content + right rail comfortably needs ~1400px+). This wasn't discussed in the review conversation and needs either a decision from Umar or a reasonable default (most likely: left nav collapses first, then right rail stacks below content) proposed and flagged for confirmation rather than silently assumed.

## Files touched in this pass

- `readme.md` — substantially revised (see revision note at top of that file)
- `foundations/colors.css` — added `[data-theme="dark"]` block
- `foundations/typography.css` — restructured into the five-role system, added Marginalia and Heading (h2/h3) tokens
- `foundations/spacing.css` — added semantic `--gap-*` aliases and left-rail sizing tokens
- `components/core/MarginThought.*`, `MarginNote.*`, `LeftNav.*`, `TLDR.*`, `Endnotes.*`, `ThemeToggle.*` — new, stubbed (functional but not yet wired into a real page or given guideline cards)

## Files NOT touched — still needs doing

- `Research and Writing/Mecca Pact/makkah-pact-analysis-meaning-man-draft.html` and the sibling `.html` — still on the old frame
- `guidelines/*.card.html` — no new specimens added
- `ui_kits/blog/` — index/entry click-through templates not updated against the new frame
- `.design-sync/` sync state — not re-synced to Claude Design; this pass only touched the local folder
