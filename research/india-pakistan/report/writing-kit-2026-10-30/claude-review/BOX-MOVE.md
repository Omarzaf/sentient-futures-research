# Pakistan box moved to Appendix A

30 October 2026. Umar asked: "Move the Pakistan box to Appendix A, redesign it around implied capture shares, and keep one body sentence." Claude made the change locally. Nothing was committed, pushed, sent or imported into Google Docs.

## What changed

- `kit/pakistan-topdown-box.md` is rewritten as "Pakistan: conventional-value scale check". Its main table now reports each year's conventional poultry and milk value and the transfer's 10th to 90th percentile range as a share of that value: 0.005% to 0.024% in 2026, 0.008% to 0.048% in 2030, 0.012% to 0.125% in 2035 (central conversion assumptions). The requested 0.05%, 0.1% and 0.5% shares appear only as a comparison: each exceeds the 2026 share under all 18 profiles, and 139 of 162 grid rows exceed the transfer's 90th percentile. The basket caveats now name the FAOSTAT and Economic Survey milk totals (32,104 and 58,300 thousand tonnes) and the separate butter and ghee line (1,268 thousand tonnes). Workflow language about the stop and approval was removed from the rough paragraph. This addresses review findings F1, F3, F4 (for the box), F5 and F6.
- `tools/assemble_kit.mjs` now splices the box at the end of Appendix A, before Appendix B, and no longer places it after section 6.
- `kit/06-results.md`: the heading is "6. Results". Line 13 gains one sentence giving the 2035 share (0.012% to 0.125%) and pointing to Appendix A. The figures line and open question are updated. All other lines keep their positions.
- `kit/appendices.md`: the Appendix A heading, figures line and open question mention the scale check. Appendix A's 800-word budget was not changed; the box adds about 520 words, so the open question suggests moving part of the results budget.
- `kit/00-section-map.md`: rows for section 6 and Appendix A updated.
- `kit/claims-by-section.csv`: the 47 rows bound to the old box were removed. 67 rows were added (`WK-B-001` to `WK-B-067`): repeated inputs reuse the accepted P4 rows with a note naming the source row, and new values are computed by `claude-review/tools/redesign_p4_box.py`. Total rows: 438. The old rows remain in `support/p4-occurrence-claims.csv`.
- Regenerated: `kit/WRITING-KIT.md`, `kit/WRITING-KIT.docx`, `support/assembly-map.json`, `verification/assembly.json`.

Every new number is computed from `build/pakistan-topdown/pakistan_topdown.csv`, the 127 reference rows, `extracted-inputs.json`, the original FAOSTAT ZIP and the Economic Survey text. The script asserts each displayed value at its display precision before writing anything. Run receipt: `claude-review/box-move-receipt.json`.

## Checks

- Kit verifier (`verify_writing_kit.verify`, called directly so `verification/kit-check.json` was not overwritten): **PASS**. 11 numbered sections, 438 claim rows, 335 visible numeric occurrences, 0 unregistered. DOCX parity: 64,336 normalized characters, 87 of 87 hyperlinks, 13 tables, 1 image, no hidden claim IDs or footnotes. Receipt: `claude-review/kit-check-after-box-move.json`.
- DOCX rendered with the previously used local LibreOffice runtime: 21 pages. Pages 9, 18 and 19 inspected; layout is clean. The scale-check table starts at the top of page 19, one line after its caption on page 18.
- The model, the 127 reference rows and the P4 grid were not changed.

## Preservation and drift

- Before-copies of every changed file, plus the prior `verification/kit-check.json`, are in `claude-review/before-box-move/` with `SHA256SUMS`.
- The committed artifact manifest at `fb8c895` (`.worktrees/writing-kit-20261030/research/india-pakistan/report/writing-kit-2026-10-30/artifact-manifest.json`) now differs for 7 of its 25 files: `00-section-map.md`, `06-results.md`, `appendices.md`, `pakistan-topdown-box.md`, `claims-by-section.csv`, `WRITING-KIT.md`, `WRITING-KIT.docx`. At Umar's request, those seven entries were rebound in local commit `c16672bfc1e065ff450d0d674ce6b3e96df3d9ca` (parent `fb8c895`), with the artifact manifest's import record and the regenerated `provenance/file-manifest.json`. The other eighteen bindings were unchanged. Library build ran twice with no drift; library verifier PASS 32,487 checks; 15 kit and P4 tests pass. `WORKSPACE-STATE.json` records the new commit (before-copy in `before-box-move/root/`); workspace verifier PASS 425. Not pushed.
- `COMPLETION.md` and the earlier verification receipts describe the earlier box location and remain historical.

## Not done

Other review findings (F2 local DOCX links, F7 paired contrast, F8 GFI dollar figures, F9 register semantics, F10 sections 3 and 8 coverage, F11 executive summary, F12 to F19) are untouched. Human review of the new arithmetic and interpretation is pending. No `SESSION-LOG.md` entry was added.
