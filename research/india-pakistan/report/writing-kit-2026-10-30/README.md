# South Asia writing-kit companion

This local branch starts from the approved report revision. The author-facing Markdown, editable DOCX, section claim register, unsent messages and review receipts are kept in the workspace's `OUTPUTS/Codex Handoff 2026-10-30/` folder. They are a writing aid for the author, not a completed regional report or a publication-approved package.

`artifact-manifest.json` binds those local deliverables by hash without importing collaborator snapshots, message contents or raw captures into the research library. The manifest paths are relative to that handoff folder. No remote action or Google Docs import is part of this task.

On 30 October 2026, at the author's request, repository copies of 19 `kit/` files (Markdown modules, assembled `WRITING-KIT.md`, claim register and figure) were added under `kit/`, together with Claude's independent review and Pakistan-box change record under `claude-review/`. In the Markdown copies, relative links were rewritten to resolve inside this repository; links to files outside it are shown as plain-text workspace paths. No other text changed. `artifact-manifest.json` binds the original workspace bytes, and `provenance/import-records.json` records each original hash. The DOCX, the five unsent messages and the collaborator snapshots stay outside the repository; the DOCX text matches `kit/WRITING-KIT.md`.

The new numerical companion is documented in `research/india-pakistan/data/pakistan-topdown/README.md`. It prices conditional conventional-food quantities and hypothetical monetary capture shares; it does not fit or alter the retained alternative-protein model. Price/quantity compatibility, density, dressing yield, nonmarketed consumption and time-basis assumptions remain unresolved. The approved continuation preserves the large disagreement with the transfer range.

Run the local writing-kit verifier after activating an existing Python environment:

```sh
python research/india-pakistan/tools/verify_writing_kit.py --handoff /path/to/writing-kit-handoff
```

Source-bound arithmetic and document checks are separate from human verification, scholarly acceptance, team agreement, rights clearance and publication approval.
