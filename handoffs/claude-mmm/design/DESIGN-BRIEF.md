# MMM design brief for the cultivated-chicken paper

The target is the main Meaning, Man and Model research-entry system. The installed design guidance includes the September 2026 figure revision. Entry III, the Pakistan AI Policy Observatory, is a concrete visual reference. This is a style adaptation of an existing reviewed manuscript, not permission to rewrite its argument.

## Authority and conflicts

For research wording and findings, `research/halal-cultivated/paper/paper.md` governs. For this build's layout and implementation decisions, this brief governs, followed by `mmm/readme.md` and `mmm/guidelines/illustration.md`, then token/component files, then example pages. The existing paper reader and print PDF govern completeness, not MMM styling. Example text and datasets are never research inputs.

The historical examples are imperfect implementations. Resolve these known conflicts deliberately:

| Reference issue | Decision for this HTML |
| --- | --- |
| Observatory dark mode changes copper to `#c07f52`; the MMM specification says copper stays fixed. | Keep `--copper: #8a5a3b` in both modes. Reserve it for a small optional point, never essential text or a sole status signal. |
| Older tokens use faint `--ink-6` for small essential labels. | Use at least the stronger `--ink-4` semantic label role, as the Observatory does, then measure contrast and strengthen further if needed. Faint ink stays decorative. |
| Generic “first person, past tense” brand copy guidance. | Preserve the research manuscript's existing voice. No invented personal marginalia, rewritten conclusions or newly confident thesis. |
| Older blog kit uses two columns, remote React/Babel, placeholders and rail sources. | Implement the current three-zone entry, meaningful rail content, local runtime and numbered endnotes. The legacy runnable blog kit and editor helper scripts are intentionally excluded. |
| Copied SVG marks hard-code light-palette values. | Inline the geometry and bind strokes/fills to the existing theme tokens. Preserve the original asset files as reference. |
| Illustration guide suggests filled/hollow/dashed confidence encodings. | This paper has documentary admission states, not calibrated confidence. Use explicit status labels; filled/hollow/dashed may encode those named states only with a clear legend. Do not imply a confidence scale. |
| Readme says one copper point per view; illustration guide permits one per figure. | Keep at most one copper emphasis visible at a time where practical, and never more than one per figure. Use ink for other data marks and keyboard outlines. |

## Visual contract

| Element | MMM treatment |
| --- | --- |
| Light ground | Warm paper `#f4f1ea`; strongest ink `#2e2b27`. |
| Dark ground | Warm near-black `#1c1815`; strongest ink `#f3ede1`. |
| Display | Newsreader, uppercase and tracked `0.09em`, regular weight; reserved for the series wordmark. |
| Headings | Newsreader, sentence case; nominal entry title 46px, h2 30px, h3 21px. Scale title down on phones. Preserve the supplied paper title wording. |
| Prose | Newsreader 18px / 1.78, about 64ch. Georgia/serif fallback. |
| Labels | IBM Plex Mono, uppercase with tracking; the existing sm/md/lg label roles, no ad hoc extra style. Use readable contrast and minimum practical touch targets. |
| Marginalia | Factual explanations use a mono heading and normal prose. Only authentic author thoughts use italic Newsreader, 16px / 1.6. |
| Frame | Left navigation 200px; prose up to 760px; right rail 300px; left gap 48px, right gap 76px. Calculate actual available width including both gaps and padding. |
| Responsive behavior | Right rail narrows around 1400px, folds inline below 1240px; left contents rail hides below 980px but retains an accessible compact contents control. Reflow early if needed to prevent overflow. |
| Structure | Flat paper, whitespace and occasional meaningful hairline rules. No cards, shadows, gradients or rounded UI boxes. Image radius is 2px only. |
| Figures | Inline SVG line geometry: thin rules, points, rings, ticks and matrices. Geometry must encode a stated relationship. Default marks use ink tokens. |
| Motion | Optional single 180-second drift, stopped by reduced motion; 160ms hover tint. No load fades, bounce or scroll reveals. |
| Theme | Both themes are required. Keep toggle keyboard-operable and persistent only through a guarded local preference when appropriate. |

The nominal frame totals 200 + 48 + 760 + 76 + 300 = **1,384px** before page padding. A full fixed frame therefore needs more than a 1,384px viewport. Let the prose shrink, collapse earlier, or use fluid gutters; never force overflow to satisfy a nominal width.

## Reader experience

Start with the title, author, draft/review status, a concise lead, then a three-to-five-line findings list and the overview figure. Findings must distinguish religious conditions, a specified process, certification and food authorization. Keep the original abstract in the full paper. Do not turn the abstract, lead and findings into three repetitions of the same paragraph.

The full paper remains the stable reading spine. Right-rail content should explain a term, delimit an inference or caption a figure at the paragraph where it matters. Use source links in endnotes, with return links to every reference. Preserve Arabic and Urdu text with suitable `lang`, direction isolation and fonts/fallbacks; do not uppercase non-Latin source titles.

Wide figures and tables may span prose plus the right rail. On narrow screens, place captions below and scroll dense diagrams inside their own containers. Never shrink source labels until they become illegible. In a two-tab variant, direct links must reveal the correct panel and keyboard focus must return sensibly.

## Working defaults

- Audience: an interested policy/research reader who may not know the technical or legal vocabulary.
- Output: a portable HTML folder, with core content rendered statically and progressive enhancement.
- Series label: MMM research working paper; no invented entry numeral or publication date beyond the supplied paper date.
- Author: exactly as supplied in the manuscript. No invented affiliation, institutional logo or endorsement.
- Research state: AI-assisted working draft, human verification pending; no market forecast or product certification.
- Photographs: none required. Existing diagrams and source-grounded SVG explanations are sufficient.

Optional author inputs can refine the page: an annotated favorite MMM screenshot, a preferred reading structure, or genuine first-person margin notes. Their absence does not block the default build.
