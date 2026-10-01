# Halal conditionality for cultivated meat

[Read the completed Phase One review](phase1/review.md), its [evidence registers](phase1/README.md), and the [revised agentic plan](AGENTIC-PLAN.md). The [updated project plan](PLAN.md) points to the active [Phase Two bridge v2](bridge-v2/METHOD.md). Session history is in the [session log](SESSION-LOG.md). Updated 1 October 2026; AI-assisted working draft with human verification pending. Not mentor-approved.

The new `phase1/` edition contains 74 public-source claims, 76 source records, 45 school questions, seven country accounts and four historical comparisons, with independent review decisions and explicit gaps. Its findings supersede the earlier search-summary pass for the questions it covers. The parent CSV tables and 24-source register below are retained as that earlier discovery snapshot: five tables contain provisional rows and the others remain empty. Their original statuses have not been silently upgraded. Phase Two quantities and interview CSV rows have not been fabricated.

## Files

| File | Record prefix | Contents |
| --- | --- | --- |
| [datapackage.json](datapackage.json) | | Preserved CSV discovery schemas and versioned pointer to the active quantitative contract. |
| [market-records.csv](market-records.csv) | `MR-` | Market data: the demand forecast's keys first, then the halal fields (plan 4.1–4.3) |
| [claims.csv](claims.csv) | `CL-` | Claims from the interview, with short excerpts only (plan 6.3) |
| [scripture-sources.csv](scripture-sources.csv) | `QS-` | Quran, hadith and Sunnah sources found for those claims |
| [consensus-matrix.csv](consensus-matrix.csv) | | Conditions by institutions and scholars, one row per cell |
| [historical-parallels.csv](historical-parallels.csv) | `HP-` | Historical food substitutions and changed rulings (plan 6.4A) |
| [rulings.csv](rulings.csv) | `FT-` | Fatwas, resolutions and rulings on cultivated meat (plan 6.4B) |
| [elasticities.csv](elasticities.csv) | `EL-` | Meat demand elasticities per focal country (plan 6.4C) |
| [feed-inputs.csv](feed-inputs.csv) | `FI-` | Insects as a poultry feed input only (plan 6.4D) |
| [madhhab-geography.csv](madhhab-geography.csv) | `MD-` | Predominant schools and fatwa bodies by country, categorical only (plan 6.5) |
| [certification.csv](certification.csv) | `CT-` | Halal certification body, standard and novel-food route per country (plan 6.5) |
| [scenarios.csv](scenarios.csv) | `SC-` | Legacy header-only grid; any numerical row is blocked until explicit v2 reconstruction. |
| [source-register.json](source-register.json) | `HS-`, carried `CO-`/`SA-`/`GP-` | Bibliographic sources, merged into the [combined catalog](../../sources/index.html) |

The interview transcript and translation (`TR-` segments) are someone else's unpublished work. They stay in private storage and are referenced here only by segment ID.

## Quantitative contract and checks

- [Method and limitations](bridge-v2/METHOD.md), [schema](bridge-v2/schema.json) and [legacy crosswalk](bridge-v2/LEGACY-CROSSWALK.md).
- [Synthetic worked example](bridge-v2/synthetic-example.json): tests value-to-mass arithmetic; no research estimate.
- [Production state](bridge-v2/production-state.json): missing compatible inputs remain null and production remains blocked.

`node tools/verify.mjs` checks exact legacy CSV headers/types/references and the active v2 quantitative contract through `tools/halal-checks.mjs`. Every legacy scenario row is rejected, so the old rules cannot silently become production numbers. `node tools/test-halal-checks.mjs` runs legacy discovery invariants and the adversarial v2 suite; `node tools/test-bridge-v2-checks.mjs` runs the latter alone.

Unknown evidence is separate from scenario assumptions. Surveys cannot replace sales penetration. Value shares need an explicit compatible price conversion before multiplying mass. Missing or incompatible capacity leaves feasible quantity null. Conditioning, scope, overlapping segments, allocation reuse, hybrid counting and false output quantiles are checked.

Discovery-table rules still preserve source lineage, original-ruling deduplication, categorical madhhab context, carried-claim status, dated bounded searches and poultry-feed exclusions. Human scholarly/source review remains pending; test success does not certify evidence.
