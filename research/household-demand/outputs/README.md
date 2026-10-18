# Household demand outputs

Task 12 writes the comparison table, Sobol ranking, holdout summary and report here.

`synthetic.py --check` scans this folder on every CI run. An artifact built from any placeholder input goes to `../synthetic/outputs/` or outside the repository. Summaries here count placeholder rows in a field such as `placeholder_stratum_households`.
