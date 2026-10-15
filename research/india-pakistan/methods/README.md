# Conditional physical-conversion evidence

These CSVs are exact copies of the reviewed physical-conversion model's factual factor catalogue and authored scenario-factor calculations. They supplement the processed table inventory; they contain neither respondent records nor original document bodies. Human verification pending.

- `source_factor_catalog.csv` gives each factor identifier, value, unit, source identity, original PDF page/food identifier, and the hash of the privately retained original file. A `raw_file` value is a historical provenance locator, not a bundled download. The explicitly labelled dimensional identity is a logical multiplier, not an empirical source.
- `factor_evidence.csv` joins a named scenario and food to its source factors, rational conversion and declared assumptions. `source_factor_refs` refers to the catalogue. Blank conversion and source fields preserve unresolved foods; they are not zero-valued measurements. Generic transfer assumptions are analyst assumptions.

Match an endpoint's `low_method` or `high_method` in `data/protein_model_method_ranges.csv` to `scenario_id`, then follow its factors to the original source locator. The source register supplies original public URLs. Source access, third-party rights and a defensible food match remain separate questions.

Original quantities remain in the HIES source workbook. Composition values and borrowed portions do not establish the local mix of species, processing states or egg sizes. These files reproduce conditional subtotals; they cannot establish full dietary intake, individual adequacy or uncertainty bounds on actual intake.
