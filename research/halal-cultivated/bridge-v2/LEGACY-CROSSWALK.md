# Legacy crosswalk and migration boundary

Version 2.0.0 · 1 October 2026 · AI-assisted; human verification pending.

All existing CSV bytes and Phase One evidence remain preserved. The old `scenarios.csv` is header-only at the migration checkpoint. Its schema remains readable for lineage, but **any populated legacy scenario row fails production validation**. No adapter guesses whether old `p`, `G`, `D` or `Q` meanings were compatible.

| Earlier interface | V2 handling | Required evidence before numerical use |
| --- | --- | --- |
| `p_US` as cultivated sales value / meat sales value | `basis = value_share_two_component`, then mass conversion | Inclusive denominator, same-market component prices, currency/year, weight basis, dimensions and conditioning |
| `p_US` as observed/forecast volume share | `basis = mass_share` | Compatible finished-product numerator and denominator, actual source type and allowed transfer |
| `acceptance_source = local_survey` | No migration to penetration | New independently validated purchase calibration; survey attitudes retained as contextual evidence |
| Legacy `H_rel`, `L`, `cert_route` | Separate dimension-specific assessments | Institution, exact product/process/territory/segment, conditions, instrument and dates |
| `L_includes_halal = true` | No bypass field | Separate evidence for each dimension; an instrument may support several records with precise locators |
| Legacy `G = 0` for silence/unknown | Scenario gate unresolved (`null`) unless an explicit closure is supported | A scenario assumption or scoped binding closure; search failure is insufficient |
| `D` in carcass-weight equivalent | No implicit conversion | Reviewed upstream conversion to the same finished-product basis; national available-protein supply remains a different measure |
| `Q` when `K` missing | `Q_feasible = null`; `Q_unconstrained` separately labeled | Compatible allocated finished-product capacity and pool |
| Legacy `quantile` labels | Deterministic sensitivity only in this implementation | A separately registered uncertainty model before probabilistic output |
| Shock that modifies price while `p` fixed | Restricted accounting sensitivity | No claim of price-induced substitution; a behavioral response needs a separate model |

The earlier comparative calculator (the 20 September Conditional Markets package) remains unchanged. It defines `D` as full-access reference demand in finished-product kg/year, `H` as a behavioral **retained-demand share**, `L` as legal access and `K` as an allocated pool. Its `H` is not v1 `H_rel` and is not the v2 scenario gate. Do not multiply its behavioral retention by the transferred market share as though they were independent inputs. Its displacement coefficient is a separate measured quantity; the v2 bridge does not implement displacement.

There is deliberately no automatic numerical adapter between those models. To migrate an input, reconstruct a v2 object with an exact version, source and dimensional/conditioning provenance; retain the original; compare an independent worked example; run all v2 negative and positive fixtures; then record author and relevant human review separately. If any required meaning is unresolved, preserve null and its reason. A synthetic pass or parser success is not baseline acceptance.

The v2 package marker in [datapackage.json](../datapackage.json) versions the **active quantitative contract**, while `legacyCsvSchemaVersion = 1.0.0` documents the unchanged discovery-table layout. Phase One, original source records and historical release receipts are not reclassified by this version increment.
