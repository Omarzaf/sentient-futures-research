# Acceptance checklist for Claude's eventual HTML

These are checks to perform on the future redesign. Inclusion in this package does not mean they have been run on an HTML page that does not yet exist.

## Content preservation

- Compare the complete paper layer with `research/halal-cultivated/paper/paper.md`, allowing Markdown/HTML syntax and whitespace differences, not rewritten research prose. Preserve paragraph, list, table, figure-caption and quotation content.
- Check all 13 numbered sections, abstract, five appendices, bibliography, three original figures and their substantive labels.
- Preserve all 177 authored footnote IDs and every reference occurrence. Existing rendering has 251 note occurrences. Deduplication is allowed only with correct destinations and return links for every occurrence.
- Compare the 60 distinct source URLs, source titles, edition/translation notes and locators against `handoffs/claude-mmm/CONTENT-CONTRACT.json` and the Markdown.
- Keep held/unretrieved records, excluded interpretations, language holds, evidence categories, human-review status and missing quantitative inputs explicit.
- Do not count aliases as new sources or turn source readiness into scholarly consensus. Do not import Observatory example facts.
- Preserve source inputs byte-for-byte. Record hashes before and after the build if tools are available.

## Style and structure

- Use the supplied MMM tokens and five type roles; honor the conflict decisions in `handoffs/claude-mmm/design/DESIGN-BRIEF.md`.
- Inspect light and dark palettes, including labels, evidence status marks, focus rings, links and the original SVG assets if inlined/recolored.
- Provide meaningful rail content, a stable contents route, complete endnotes and a concise opening.
- Tie every figure to supplied prose/data and explain its encoding. For new classifications, document the ordered rule and retain the verbatim input.
- No decorative figures, fabricated first-person notes, card grid, hero image, extra icon library or invented series entry number.

## Functional and browser checks

- Run a local asset and fragment-link audit. Require unique IDs and working citation, return, contents and figure targets.
- Confirm no runtime fetch is needed to display the core paper or data. List optional remote fonts separately from essential local assets.
- Inspect at 1440px, 1280px, 768px and 375px widths in both themes. A 390px phone check is also useful. Document-level horizontal overflow must be zero; deliberate table/diagram scrolling stays inside its container.
- Walk through: opening → a section → source note → exact return location; and figure → evidence record → return. Test both pointer and keyboard paths.
- Test mobile contents navigation, theme toggle, deep links after reload and focus visibility. If tabs are used, test arrow/Tab behavior, panel state and return from deep evidence.
- Check reduced motion, JavaScript-disabled core reading, long URLs, table headings, mixed Arabic/Urdu/Latin direction, and print output.
- Measure essential text contrast. Do not use copper or faint marks as the sole carrier of meaning. Inspect SVG titles/descriptions and keyboard-operable links.
- Check the browser console for page errors and failed essential resources.

Record commands, viewport sizes, actual results and any screenshots in the output's `QA.md`. Mark unavailable checks “not run.” Browser inspection alone does not establish real-reader comprehension, specialist screen-reader validation or accessibility certification.
