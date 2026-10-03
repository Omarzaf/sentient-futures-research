# Archive: halal workstream

Kept for lineage. Nothing here is current; the [working paper](../paper/README.md) and the [Phase One review](../phase1/README.md) supersede it for the questions they cover.

## Executed plans

- [Agentic research plan](AGENTIC-PLAN.md), revised 30 September 2026: the Phase One method and delivery targets, all completed on 30 September.
- [Paper plan](PAPER-PLAN.md), 2 October 2026: the plan the working paper was written from.

The [project plan](../PLAN.md) stays at the workstream root because it still sets the Phase Two scope and double-counting rules.

## Discovery pass, 30 September 2026

The first search-summary pass, built before direct page access was available. Five tables hold provisional rows; the others are header-only. Statuses were not upgraded after Phase One, and the rows that Phase One contradicted carry a correction note. Field names, types and allowed values are in [datapackage.json](../datapackage.json), and `node tools/verify.mjs` still validates every table.

| File | Record prefix | Contents |
| --- | --- | --- |
| [market-records.csv](discovery-pass/market-records.csv) | `MR-` | Market data: the demand forecast's keys first, then the halal fields (plan 4.1–4.3). Header only |
| [claims.csv](discovery-pass/claims.csv) | `CL-` | Interview claims (plan 6.3). Header only; the interview stays private |
| [scripture-sources.csv](discovery-pass/scripture-sources.csv) | `QS-` | Quran, hadith and Sunnah sources |
| [consensus-matrix.csv](discovery-pass/consensus-matrix.csv) | | Conditions by institution, one row per cell |
| [historical-parallels.csv](discovery-pass/historical-parallels.csv) | `HP-` | Historical food substitutions (plan 6.4A). Header only; see Phase One's historical comparisons |
| [rulings.csv](discovery-pass/rulings.csv) | `FT-` | Fatwas, resolutions and rulings on cultivated meat (plan 6.4B) |
| [elasticities.csv](discovery-pass/elasticities.csv) | `EL-` | Meat demand elasticities (plan 6.4C). Header only; see the continuation's elasticity review |
| [feed-inputs.csv](discovery-pass/feed-inputs.csv) | `FI-` | Insects as poultry feed (plan 6.4D). Header only; see the continuation's feed review |
| [madhhab-geography.csv](discovery-pass/madhhab-geography.csv) | `MD-` | Predominant schools and fatwa bodies by country, categorical only (plan 6.5) |
| [certification.csv](discovery-pass/certification.csv) | `CT-` | Certification body, standard and novel-food route per country (plan 6.5) |
| [scenarios.csv](discovery-pass/scenarios.csv) | `SC-` | Legacy scenario grid. Header only; any row is rejected until rebuilt under contract v2 |
| [source-register.json](discovery-pass/source-register.json) | `HS-`, carried `CO-`/`SA-`/`GP-` | The 24 bibliographic sources, merged into the [combined catalog](../../../sources/index.html) |
