# Halal conditionality for cultivated meat: research plan

Version 2, 1 October 2026. Author: Muhammad Umar Zafar, AI-assisted. Status: working plan, not mentor-approved; AI-assisted, human verification pending.

**Phase One update:** The [revised agentic plan](AGENTIC-PLAN.md) supersedes this document's Phase One deadlines, language restriction and transcript/human-gate prerequisites. The [30 September bounded public-source review](phase1/review.md) records that edition's result; the [October continuation](phase1-continuation/README.md) remains in progress. Phase One evidence remains preserved. The approved experiment-led plan now supersedes the old Phase Two bridge, gate, survey substitution, unknown-capacity and deadline rules. [Quantitative bridge v2](bridge-v2/METHOD.md) is the active method; [the crosswalk](bridge-v2/LEGACY-CROSSWALK.md) preserves the earlier interfaces.

[datapackage.json](datapackage.json) now records the active v2 contract and the preserved v1 CSV layouts. The quantitative schema is [bridge-v2/schema.json](bridge-v2/schema.json); `tools/halal-checks.mjs` invokes its semantic checks. All numerical legacy scenario rows are blocked pending explicit reconstruction. [Production remains missing-baseline blocked](bridge-v2/production-state.json); the example is synthetic only. See [README.md](README.md) for the files.

## 1. What this workstream answers

Team umbrella question: how could AI reshape the food system transition over the next 10–20 years, and where should talent and resources go today?

This workstream asks: **under which religious, certification and regulatory conditions can cultivated meat enter Muslim-majority and large-Muslim-population markets, and what share of the existing meat market could it occupy if those conditions are met?**

It adds a halal layer to the team's work. It does not run its own forecast survey or LLM elicitation. The team's demand-forecast workstream produces a US forecast; this workstream reuses her variables, years and definitions so the two can be read side by side and joined row by row.

## 2. Decisions fixed on 30 September

| Topic | Decision |
|---|---|
| Method | No questionnaire and no LLM forecast panel in this workstream. |
| Time horizons | Same as the demand forecast: 2026, 2030, 2035, with 2025 as the base year. |
| Language | English sources only. Where no English version exists, flag it; Umar decides whether to use Urdu and translate himself. The Urdu interview being transcribed is the object of study, so it is the one standing exception. |
| Geography | Four focal cases: India, Pakistan, Saudi Arabia, UAE. Three precedents: Malaysia, Singapore, Indonesia. No readiness ranking across them. |
| Product | Cultivated chicken first. Other halal species (beef, mutton, goat) as an extension once chicken is done. |
| Insects | Poultry feed input only, valued in market terms. Never counted as human protein or as an alternative protein, which keeps the demand forecast's exclusion intact. |
| Scenarios | Evidence statuses remain separate from explicit open, closed or unresolved assumptions. Gate applicability is institution/product/process/segment specific; unknown evidence is not zero. |
| Double counting | None permitted. Rules in section 5. |
| Earlier work | The Conditional Markets paper (20–21 Sep) and the India–Pakistan brief (15 Sep) are inputs to build on and re-check, not established findings. Team material is read from the team's shared Drive, which stays the source of truth and is not copied into this repository. |
| Role question | Deferred. This plan lays groundwork. |
| Where outputs live | Repository as source of truth; Google Drive copy for mentors. |

## 3. How the work is organised

From the 30 September mind map.

**Phase 1: evidence base**

1. Transcription and translation of the interview with Ghamidi Sahab.
2. Referencing: every claim in the interview traced to Quran, Sunnah, hadith, classical and historical sources, then used for the consensus matrix.
3. Literature review: historical parallels of food substitution and changed rulings, and the contemporary rulings on cultivated meat.
4. Muslim geography: which school of thought predominates where, and how each focal country certifies halal food.

**Phase 2: scenarios**

Scenario 1 from the mind map: if the focal states declare halal-source cultivated meat halal, what share of the projected meat market could it occupy? Then the same question under the other gate states and under the two shocks.

**Cross-cutting: systems thinking.** For each scenario, record first-order effects (market access, sales) and second-order effects (conventional halal meat exports, livestock livelihoods, feed demand including insects, certification industry). Livelihood effects are handed to the team's Global North/South workstream rather than analysed twice.

## 4. Preserved discovery fields and the active quantitative bridge

Sections 4.1–4.4 document the preserved legacy CSV discovery layout. These fields are evidence inputs, not a validated numerical interface. The active v2 bridge in 4.5 freezes complete dimensions and conditioning before any calculation.

### 4.1 Keys shared with the demand forecast

| Field | Values | Source of the convention |
|---|---|---|
| `category` | `plant_based`, `fermentation_biomass`, `fermentation_precision`, `cultivated`, `hybrid_cultivated`; conventional comparators `chicken`, `beef`, `mutton_goat` | The demand forecast's GFI-based definitions, used word for word |
| `excluded` | insects as human protein, animal feed | Demand forecast |
| `geo` | ISO 3166 alpha-3 | Repository convention |
| `year` | 2025 base; 2026, 2030, 2035 | Demand-forecast resolution years |
| `metric` | `sales_value`, `volume`, `market_share` | See 4.2 |
| `price_basis` | constant 2025 USD | Demand forecast |
| `channel` | `retail`, `foodservice`, `all` | The demand forecast uses retail (US). Focal-market data will mostly be `all`; the field records which. |
| `quantile` | `q10`, `q50`, `q90` where a value is uncertain | Demand forecast |
| `source_id` | existing CO-, SA-, GP- plus the new prefixes in 4.4 | Conditional Markets paper |

### 4.2 Units and denominators

- **Value:** local nominal values are converted to local 2025 prices using the national food CPI, then to USD at the 2025 average exchange rate. PPP is used only for affordability comparisons, never for market size.
- **Volume:** meat in carcass-weight equivalent, the unit used by the OECD-FAO Agricultural Outlook. Retail weight only where a source gives nothing else, and the field says which.
- **Market share:** cultivated volume ÷ total meat volume, same geography, year, unit and channel. Value shares are reported separately and never mixed with volume shares.
- Food-balance supply, household survey quantities, sales and stated purchase intentions stay in separate records. This is the existing repository rule.

### 4.3 Halal fields added to each record

| Field | Values |
|---|---|
| `species_status` | `halal_species`, `non_halal_species`, `disputed_by_school` |
| `cell_origin` | `slaughtered_halal`, `live_biopsy`, `non_halal_slaughter`, `legacy_bank_unknown`, `unknown` |
| `medium_status` | `animal_free_defined`, `fetal_bovine_serum`, `other_animal_derived`, `unknown` |
| `process_flags` | `ethanol_used`, `porcine_derived_input`, `none`, `unknown` |
| `H_rel` | religious status from a named institution for a named product profile, jurisdiction and date: `permitted`, `conditional`, `prohibited`, `silent`, `unknown` |
| `L` | food-safety market access: `approved`, `pending`, `refused`, `no_pathway`, `unknown` |
| `L_includes_halal` | `true` where the food regulator's approval already requires halal status (for example Saudi SFDA), otherwise `false` |
| `cert_route` | `operational`, `statute_only`, `none_found`, `unknown` |
| `madhhab_context` | predominant school or schools, categorical |

Missing stays missing. A blank is never read as zero, and a registry search that finds nothing is recorded as `none_found` with its date, not as a prohibition.

### 4.4 New source and record prefixes

| Prefix | Record type |
|---|---|
| `TR-` | Transcript segment |
| `CL-` | Claim made in the interview |
| `QS-` | Quran or Sunnah source |
| `HP-` | Historical parallel |
| `FT-` | Fatwa, resolution or ruling |
| `MD-` | Madhhab and geography record |
| `CT-` | Certification body or standard |
| `EL-` | Elasticity estimate |
| `MR-` | Market data record (section 4 fields) |
| `FI-` | Feed-input record (insects as poultry feed) |
| `SC-` | Scenario grid row (section 7) |
| `HS-` | New bibliographic source in this workstream's source register |

The last four were added when the schema was built so that every table has a primary key. `excluded` is recorded once in the data package metadata rather than as a column, because an excluded category never appears in a record.

### 4.5 Active bridge v2

Use the [method, worked example and limits](bridge-v2/METHOD.md) with the [machine-readable schema](bridge-v2/schema.json). Compatible observed or forecast **mass share** can transfer only as an explicit assumption. A two-component value share requires same-market relative mass prices: `p_mass = s / (s + (1-s) * r)`. Value share cannot multiply meat mass directly. Survey attitudes never substitute for sales penetration.

`Q_unconstrained = D_compatible * p_mass_assumed * G_scenario`. The gate maps open/closed/unresolved to 1/0/null **within the scenario**, not within an evidence assessment. `Q_feasible = min(Q_unconstrained, K_allocated)` only when supply is known and compatible; otherwise it is null. Missing inputs remain null even under a hypothetical closed gate.

Unknown, conditional, conflicting and bounded-search-not-found evidence remains explicit. Religious positions, certification routes, specific certificates, food authorization and import access use separate scope-specific records. An institution's prohibition cannot close every national consumer segment. An evidence-led national closure requires binding national access evidence; hypothetical closure must be labeled. No generic `L_includes_halal` bypass survives in v2.

## 5. Active invariants and double-counting rules

1. Freeze geography, mutually exclusive segment, year, species/product, channel, denominator, currency/price year, mass basis, evidence type and source vintage. No silent channel, species, year or weight conversion.
2. Document embedded acceptance, religion, legal timing, certification, price and supply mechanisms. Reject a second adjustment of the same mechanism. An unconditional/rejection-adjusted forecast needs a new owner-supported reference baseline before numerical transfer.
3. Use deterministic sensitivities in this version. Marginal q10/q10 ratios are not output quantiles; a probabilistic method requires a registered implementation and dependence evidence.
4. Allocate each capacity pool once within a simultaneous scenario group. Distinct alternatives are identified separately. Unknown or incompatible capacity cannot produce a feasible number.
5. Count each finished hybrid observation once. Use its cultivated fraction for biomass only; no displacement coefficient is inferred. Segment aggregation requires a documented disjoint partition.
6. Survey responses, aggregate available-protein supply and demand/penetration remain different measurements. The earlier comparative calculator's behavioral retained-demand share is not a religious gate.
7. Record every shock's parameter, evidence and assumed status once. Fixed penetration with a conventional-price shock is a restricted accounting exercise, not price-induced substitution.
8. Related evidence counts once. Consensus records cite the original ruling, and repeated studies share evidence groups.
9. Madhhab is context, not a population weight. Insects remain poultry feed inputs, never added as human protein.
10. Preserve carried claims as unverified until their dated source re-check. Machine validation is not human scholarly review.

## 6. Phase 1 deliverables

### 6.1 Document 1: Transcription (Urdu)

- **Input:** the interview recording (`IMG 7313.*`, not yet in the repository), with its date and the interviewer's name.
- **Method:**
  - Whisper large-v3 run on CPU, then a manual correction pass.
  - Speaker separation (interviewer and Ghamidi Sahab), so each segment carries a speaker label and only Ghamidi Sahab's statements enter the claims register.
  - Arabic recitations are matched to the standard Quran text, not to the speech-recognition output.
- **Format:**
  - Clean verbatim in Urdu script, cut into numbered, timestamped segments (`TR-001` onwards).
  - Quranic and Arabic passages stay in Arabic script, tagged inline (for example `[Q 6:145]`).
  - Unclear audio is marked, never guessed.
  - The unedited machine output is kept alongside.
- **Done when:** every segment has a timestamp and every Arabic quotation is matched to a reference or flagged.

### 6.2 Document 2: Translation (English)

- **Alignment:** segment IDs match Document 1 one to one.
- **Quran verses:**
  - Use Ghamidi Sahab's own *Al-Bayan* in its English translation (Shehzad Saleem), so his reading of a verse is not replaced by another translator's.
  - A second standard English translation is noted where the two differ.
  - Where no English *Al-Bayan* rendering exists for a verse, flag it.
- **Supporting material:**
  - A glossary covering istihala, dhabiha, tayyibat and khaba'ith, fitra, and "Sunnah" in Ghamidi Sahab's specific sense.
  - Translator's notes wherever the wording carries legal weight.
- **Done when:** an Urdu-literate reviewer has signed off.
- **Access:** the full transcript and translation are someone else's unpublished interview. They are kept in private Drive storage, not in this repository, and are not published without permission. This repository holds only the claims register with short excerpts.

### 6.3 Document 3: Claims and source verification register

- **One row per claim (`CL-`):**
  - timestamp and segment ID
  - Urdu and English text
  - claim type: Quran, Sunnah, hadith, fiqh position, historical, scientific, or the speaker's own reasoning
  - what the speaker cited
  - the original source found (`QS-`, `HP-`)
  - exact locator
  - verification status
- **Locators:**
  - Quran: surah and ayah.
  - Hadith: collection, book and number, with grading and who graded it.
  - Classical works: English edition and page.
- **Statuses:** `verified`, `partially_verified`, `misattributed`, `not_found`, `speaker_reasoning`. The last is not an error. It marks the speaker's own ijtihad, meaning his reasoning rather than a quoted source.
- **Ghamidi's framework:** his "Sunnah" claims are checked against his own framework in *Mizan* (English: *Islam: A Comprehensive Introduction*) as well as the hadith collections. He defines Sunnah as practice transmitted by consensus, not the hadith corpus, and checking him only against hadith would mark him wrong by a standard he does not use.
- **English classical sources first:**

  | School | English source |
  |---|---|
  | Hanafi | *al-Hidaya* |
  | Shafi'i | *Reliance of the Traveller* |
  | Maliki | *al-Risala* |
  | Hanbali | Ibn Qudama's *'Umdat al-Fiqh* |

  Anything available only in Arabic or Urdu (for example the full *al-Mughni* or *Radd al-Muhtar*) is flagged for Umar.

- **Consensus matrix** (feeds Document 4):
  - **Rows** are conditions:
    - species
    - slaughtered donor vs live biopsy
    - growth medium
    - whether istihala applies to cell culture
    - whether slaughter is required
    - safety
    - labelling
  - **Columns** are institutions and scholars, including Ghamidi Sahab.
  - **Each cell** holds a position, citation and date.
  - **Output per row:** `unanimous`, `majority`, `disputed` or `single_source`, with the outliers named.

### 6.4 Document 4: Literature review

**4A. Historical parallels.** The mind-map question: when did people change a popular food into something else, and what about that time and place caused it? Each `HP-` record holds:

- the food before and after
- the driver: religious ruling, price, scarcity, disease, technology, policy or sovereignty, taste
- the jurisprudential mechanism where there is one: istihala, necessity (darura), custom ('urf), public interest (maslaha), avoidance of harm
- time and place
- the speed of change and any elasticity evidence
- which variable in section 4 it informs: `H_rel`, `D`, `p` or `K`

Candidates, all to be verified:

| Group | Candidates | Notes |
|---|---|---|
| Religious rulings | Wine to vinegar, and the dispute over deliberate conversion; tanned hides; musk; jallala animals and quarantine; rennet and the cheese of non-Muslims; gelatin and the 1995 IOMS seminar; the 2001 Ajinomoto case in Indonesia (pork-derived enzyme in the process); porcine insulin and vaccines; stunning and machine slaughter; meat of the People of the Book (Q 5:5); alcohol thresholds in flavourings; horse meat and shrimp across schools; coffee in Mecca, 1511 | |
| Market substitutions | Margarine for butter; plant milk for dairy | Shared with the demand forecast's analogue list, using the same source IDs |
| South Asian substitutions | Vanaspati for desi ghee; broiler chicken replacing mutton and beef | |
| Disease shocks | African swine fever in China (2019) and the shift to poultry; avian influenza culls | |
| Food sovereignty | The 2017 Qatar blockade and domestic dairy; Gulf food-security strategies | |

This part also builds the **precedent-setting** summary. For each driver, which precedents make a quick ruling on cultivated meat more or less likely?

**4B. Contemporary rulings on cultivated meat.** Confirmed so far:

- IIFA Resolution 265 (2025)
- MUIS fatwa (2024)
- Malaysia Mufti WP Irsyad 595 (2021)
- GOOD Meat's 2023 scholar advice
- Hamdan et al. (2018)
- Alqurashi et al. (2026, *Foods*)

To locate: Al-Azhar and Dar al-Ifta (Egypt), MUI (Indonesia), JAKIM, Pakistan's Council of Islamic Ideology, Islamic Fiqh Academy India, Darul Uloom Deoband. Each becomes an `FT-` record and a column in the consensus matrix.

**4C. Drivers.** The AI adoption factors from the mind map, mapped onto the demand forecast's driver-map names so the two lists join.

| Mind-map factor | Demand-forecast driver name | Note |
|---|---|---|
| Mass-scaling production | supply chain costs; AI-driven R&D speed | |
| Cheap | price | |
| Taste | taste and texture | |
| Premade | convenience | |
| Nutrition | health perceptions | |
| Variety and cuisine | new: cuisine fit | Whether the product works in local dishes. This matters most for South Asian and Gulf cooking, so the field is added to the shared list, not kept separate. |

Meat elasticity (own-price and cross-price for chicken, beef and mutton) is collected per focal country as `EL-` records. The USDA ERS international food-demand elasticities and Hayat et al. for Pakistan are the starting points.

**4D. Insects as poultry feed.** Market value of insect meal as a feed input in the focal countries, its effect on conventional chicken cost, and its halal status as feed by school. Human collection and eating of insects in South Asia gets one descriptive paragraph only.

### 6.5 Document 5: Muslim geography and certification

This is kept as its own document because it is a reference table other sections cite.

**`MD-` table, one row per country from the Middle East to South Asia to Southeast Asia:**

- predominant school or schools
- official state madhhab where a constitution or law names one (English texts from constituteproject.org)
- Sunni/Shia/Ibadi composition from a named source
- main fatwa bodies
- date of each figure

Madhhab shares are rarely measured directly, so the field is categorical. No percentages are invented.

**Starting hypotheses to source:**

| Region | Predominant school(s) |
|---|---|
| South and Central Asia | Hanafi (Deobandi and Barelvi in South Asia); Shafi'i in Kerala and the Konkan coast; Ja'fari Shia minorities |
| Southeast Asia | Shafi'i |
| Saudi Arabia, Qatar | Hanbali |
| UAE | Maliki as the official school |
| Kuwait, Bahrain (ruling families) | Maliki |
| Oman | Ibadi |
| Iran; majorities in Iraq and Bahrain | Ja'fari |
| Northern Yemen | Zaydi |

**`CT-` table, certification process per focal and precedent country:**

- the certifying body
- the standard
- whether certification is mandatory
- import and recognition rules
- whether any route covers novel or cell-based foods

Starting points:

| Country | Body and standard |
|---|---|
| Pakistan | Pakistan Halal Authority |
| India | Private certifiers for the domestic market, i-CAS for exports |
| Saudi Arabia | SFDA Halal Center |
| UAE | MoIAT and UAE.S 2055-1 |
| Malaysia | JAKIM and MS 1500 |
| Indonesia | BPJPH, with mandatory certification from October 2026 |
| Singapore | MUIS |
| International | OIC/SMIIC 1 and GSO 2055-1 |

## 7. Phase Two state

[The production state](bridge-v2/production-state.json) is blocked on a compatible versioned baseline, finished-product reference market, scoped gate evidence and allocated capacity. [The synthetic example](bridge-v2/synthetic-example.json) tests arithmetic only. No near-zero 2026 outcome, silence-to-zero assumption, country forecast or scenario probability is asserted. Years remain separate; missing values remain missing.

The active experiment-led sequence repairs contracts, executes a bounded pilot, and reviews gaps before expanding research or producing conditional scenarios. Completion follows acceptance criteria rather than delivery deadlines.

## 8. Historical v1 timeline — superseded, retained for provenance

The table below records the former deadline-based plan only. It authorizes no communication, publication or missing-data substitution. The experiment-led acceptance gates now control execution.

| Week of | Work |
|---|---|
| 30 Sep | Set up the schema, registers and verify checks. Send the demand-forecast workstream the two requests in 4.5. Transcription and translation once the recording arrives. |
| 7 Oct | Document 3 (claims register). Document 5 tables. |
| 14 Oct | Document 4A and 4B. Consensus matrix. The demand forecast's first aggregated results are due. |
| 21 Oct | Document 4C and 4D. Elasticities. OECD-FAO baselines. |
| 28 Oct | Phase 2 scenario grid using the demand forecast's medians and quantiles. |
| 4 Nov | Write-up, human review of translations and fiqh sources, final verification run. Buffer to 13 November. |

## 9. Resources needed

**From Umar**

- The interview recording (`IMG 7313.*`), with its date and the interviewer's name.
- Repository access for the working session.
- Flags answered on any Urdu-only source.

**From the demand-forecast workstream**

- Her cultivated q10/q50/q90 for 2026, 2030 and 2035.
- Her US meat sales denominator.

**Data (English, mostly free)**

| Use | Sources |
|---|---|
| Baselines | OECD-FAO Agricultural Outlook (meat consumption projections by country) |
| Country poultry detail | USDA FAS GAIN country reports |
| Elasticities | USDA ERS international food-demand elasticities |
| Supply | FAOSTAT food balances |
| Price conversion | National food CPI; World Bank exchange rates |
| Religious composition | Pew (2009, 2012) |
| Official state madhhab | constituteproject.org |
| Halal standards (some paywalled) | GSO 2055-1, MS 1500, OIC/SMIIC 1 |

**Texts in English**

- *Islam: A Comprehensive Introduction* (the English *Mizan*) and *Al-Bayan* in English.
- An English Quran translation and sunnah.com English hadith.
- *al-Hidaya*, *Reliance of the Traveller*, *al-Risala*, *'Umdat al-Fiqh*.
- The Encyclopaedia of Islam entry on istihala (library access).

**People**

- An Urdu–English translation reviewer.
- A fiqh reviewer (ideally one Hanafi and one from another school).
- A Malay/Indonesian reader for JAKIM and BPJPH documents that lack English versions.

**Environment**

Network access to: huggingface.co (Whisper weights), youtube.com (only if the interview is also online), sunnah.com, api.quran.com, tanzil.net, cdn.jsdelivr.net, oecd.org, fao.org, ers.usda.gov, fas.usda.gov, pewresearch.org, constituteproject.org and github.com.

**Research connectors already available**

Consensus, Elicit and Scholar Gateway for literature searches.

## 10. Repositories and tools

| Repository | Use here |
|---|---|
| `SYSTRAN/faster-whisper`, `openai/whisper` | Urdu transcription on CPU |
| `m-bain/whisperX`, `pyannote/pyannote-audio` | Word-level timestamps; separating speakers in a Q&A |
| `yt-dlp/yt-dlp` | Pulling the audio if the interview is also online |
| `fawazahmed0/quran-api`, `fawazahmed0/hadith-api` | Quran and hadith in English (and Urdu) as JSON, for checking every citation automatically |
| `frictionlessdata/frictionless-py` | Validating every CSV against the shared schema in section 4, so field names and allowed values cannot drift from the demand forecast's |
| `jgm/pandoc`, `citation-style-language/styles` | Producing the Word/PDF and Google Doc versions from Markdown with proper citations |
| `zotero/translation-server` | Clean bibliography records from URLs and DOIs (the repository already uses `.ris`) |
| `nvkelso/natural-earth-vector`, `geopandas/geopandas` | The madhhab and certification map |
| `OpenITI` (organisation) | Optional. Arabic classical texts for the flagged cases where no English exists. |
| This repository's `tools/verify.mjs` | Extended to check the new prefixes, allowed values and the double-counting rules in section 5 |

## 11. Open items

- Interview recording (`IMG 7313.*`) not yet in the repository.
- Demand-forecast workstream asked on 30 September for the 2026/2035 extension, the US meat denominator, and whether cultivated sales are reported separately from fermentation. Awaiting reply.
- Mentor sign-off on the halal scope and the role question, deferred by decision.
- Flags for Urdu-only sources: none yet.
