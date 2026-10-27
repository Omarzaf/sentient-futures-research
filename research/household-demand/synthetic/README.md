# Placeholder inputs

Invented values live in this folder only. Every row carries `status == "SYNTHETIC"`.

Allowed here (decision 19, 24): Pakistan unresolved strata and plant-based prices before the price snapshot exists. Nothing in the US is invented (decision 5, 31).

Artifacts derived from these inputs go to `synthetic/outputs/` or outside the repository, never to `../outputs/` (ruling R1). The guard `python research/household-demand/synthetic.py --check` blocks the flag from the claim ledger, `research/india-pakistan/report/`, `research/india-pakistan/joint-report/` (D1) and `../outputs/`.
