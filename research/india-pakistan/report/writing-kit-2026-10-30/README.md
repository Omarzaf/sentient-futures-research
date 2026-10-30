# South Asia writing-kit companion

This local branch starts from the approved report revision. The author-facing Markdown, editable DOCX, section claim register, unsent messages and review receipts are kept in the workspace's `OUTPUTS/Codex Handoff 2026-10-30/` folder. They are a writing aid for the author, not a completed regional report or a publication-approved package.

`artifact-manifest.json` binds those local deliverables by hash without importing collaborator snapshots, message contents or raw captures into the research library. The manifest paths are relative to that handoff folder. No remote action or Google Docs import is part of this task.

The new numerical companion is documented in `research/india-pakistan/data/pakistan-topdown/README.md`. It prices conditional conventional-food quantities and hypothetical monetary capture shares; it does not fit or alter the retained alternative-protein model. Price/quantity compatibility, density, dressing yield, nonmarketed consumption and time-basis assumptions remain unresolved. The approved continuation preserves the large disagreement with the transfer range.

Run the local writing-kit verifier after activating an existing Python environment:

```sh
python research/india-pakistan/tools/verify_writing_kit.py --handoff /path/to/writing-kit-handoff
```

Source-bound arithmetic and document checks are separate from human verification, scholarly acceptance, team agreement, rights clearance and publication approval.
