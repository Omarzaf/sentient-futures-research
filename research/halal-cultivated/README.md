# Halal conditionality for cultivated meat

[Read the completed Phase One review](phase1/review.md), its [evidence registers](phase1/README.md), and the [revised agentic plan](AGENTIC-PLAN.md). The [Part 1 plan](PART1-PLAN.md) of 1 October records the five-chapter scope, the looped research process and the decisions still open. The [original project plan](PLAN.md) remains the reference for Phase Two. Session history is in the [session log](SESSION-LOG.md). Updated 30 September 2026; AI-assisted working draft with human verification pending. Not mentor-approved.

The new `phase1/` edition contains 74 public-source claims, 76 source records, 45 school questions, seven country accounts and four historical comparisons, with independent review decisions and explicit gaps. Its findings supersede the earlier search-summary pass for the questions it covers. The parent CSV tables and 24-source register below are retained as that earlier discovery snapshot: five tables contain provisional rows and the others remain empty. Their original statuses have not been silently upgraded. Phase Two quantities and interview CSV rows have not been fabricated.

## Files

| File | Record prefix | Contents |
| --- | --- | --- |
| [datapackage.json](datapackage.json) | | Field names, types and allowed values for every table (Frictionless Data format). The single place these are defined. |
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
| [scenarios.csv](scenarios.csv) | `SC-` | Phase 2 grid: `Q = D × p × G`, capped by `K` (plan 4.5 and 7) |
| [source-register.json](source-register.json) | `HS-`, carried `CO-`/`SA-`/`GP-` | Bibliographic sources, merged into the [combined catalog](../../sources/index.html) |

The interview transcript and translation (`TR-` segments) are someone else's unpublished work. They stay in private storage and are referenced here only by segment ID.

## Checks

`node tools/verify.mjs` checks every table against `datapackage.json`: exact headers in order, types, required fields, allowed values, patterns and unique IDs. It also enforces the double-counting rules in plan section 5 and the missing-data rules:

- `G` is 0 or 1 and matches the gate state, `H_rel`, `L` and `L_includes_halal`.
- One acceptance carrier per scenario: `p_US` from the demand forecast's cultivated question, or a local survey, never both.
- `Q_uncapped` equals `D × p × G`, `Q` equals it capped by `K`, and every zero or missing `Q` carries a reason code.
- A shock changes only the variables its mechanism names, and never `p`.
- Hybrids are counted once, insects appear only as poultry feed, and consensus cells cite an original ruling, not a report of it.
- Madhhab is categorical; no percentages.
- Carried values from earlier work stay `carried_unverified` until re-checked on a recorded date.
- `none_found` needs a search date, and `H_rel` needs the `FT-` ruling it comes from.

`node tools/test-halal-checks.mjs` runs these checks against a valid fixture and against broken variants to confirm that each rule catches what it should.

Add a column by editing `datapackage.json` and the CSV header together, and tell the demand-forecast workstream if a shared key changes.
