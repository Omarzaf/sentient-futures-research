# Halal conditionality for cultivated meat

[Read the research plan](PLAN.md). Version 1, 30 September 2026. Current workstream; AI-assisted working plan with human verification pending. Not mentor-approved.

This folder holds the plan, the shared data schema and the registers that the plan's Phase 1 and Phase 2 documents will fill. The rulings, madhhab and certification registers hold first-pass records from 30 September 2026; every one is `unverified`. The other registers are empty. Nothing here is a finding yet.

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

## Rulings search, 30 September

The primary sites (iifa-aifi.org, muis.gov.sg, muftiwp.gov.my, goodmeat.co, pewresearch.org, constituteproject.org and others) were blocked by the session's network policy. Records were therefore built from web search summaries, each with its source URL in [source-register.json](source-register.json). All are `unverified` until the page is opened.

Entered:

- 6 rulings (`FT-001`–`FT-006`), including JAKIM's September 2025 Muzakarah decision, which the plan had not yet listed.
- 7 madhhab records (`MD-001`–`MD-007`).
- 9 certification records (`CT-001`–`CT-009`).
- 24 sources (`HS-`).

Predominant schools for Pakistan, India, Saudi Arabia and Indonesia are still the plan's hypotheses and have no source. Official madhhab is filled only where a statute was found: Singapore (AMLA s.33) and Malaysia (Act 505 s.39). The UAE's 2005 personal status law orders the schools rather than naming one, and it has since been replaced.

Not located, or located only in secondary reports. None of these is entered as an `FT-` record:

| Body | What the search found |
| --- | --- |
| Al-Azhar and Dar al-Ifta (Egypt) | No ruling on cultivated meat found. |
| MUI (Indonesia) | A secondary review says Indonesian bodies treat cells from live animals as impure; no MUI fatwa located. |
| Council of Islamic Ideology (Pakistan) | No statement found. News reports attribute a conditional ruling (slaughtered source animal) to scholars led by Mufti Taqi Usmani; primary text not located. |
| Islamic Fiqh Academy (India) | No resolution found. |
| Darul Uloom Deoband | A ruling attributed to Deoband appears on UK sites (Wifaq ul Ulama, fatwaa.com). It permits cells from a slaughtered animal and possibly feather-derived cells. The attribution is not confirmed. |
