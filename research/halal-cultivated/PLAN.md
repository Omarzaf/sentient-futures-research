# Halal conditionality for cultivated meat: research plan

Version 1, 30 September 2026. Author: Muhammad Umar Zafar, AI-assisted. Status: working plan, not mentor-approved; AI-assisted, human verification pending.

**2 October update:** The demand-forecast workstream replied to the requests in 4.5. Sections 4.1, 4.5, 5, 9 and 11 now reflect that reply. The main change is that this workstream supplies its own US meat denominator.

**Phase One update:** The [revised agentic plan](AGENTIC-PLAN.md) supersedes this document's Phase One deadlines, language restriction and transcript/human-gate prerequisites. The [completed public-source review](phase1/review.md) records the result. Phase Two scope and schema rules below remain unchanged.

The schema in section 4 is implemented in [datapackage.json](datapackage.json), and the section 5 rules are checked by `tools/halal-checks.mjs`. See [README.md](README.md) for the files.

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
| Scenarios | Halal status is the gate (declared halal, declared haram, prolonged silence). Animal-disease shocks and food-sovereignty policy are layered on top of each gate state. |
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

## 4. Shared variables with the demand-forecast workstream

This is the fix for the category mismatch. Every data record in this workstream carries the demand forecast's keys first, then the halal fields. Nothing in its schema is renamed.

### 4.1 Keys shared with the demand forecast

| Field | Values | Source of the convention |
|---|---|---|
| `category` | `plant_based`, `fermentation_biomass`, `fermentation_precision`, `cultivated`, `hybrid_cultivated`; conventional comparators `chicken`, `beef`, `mutton_goat` | The demand forecast's GFI-based definitions, used word for word |
| `excluded` | insects as human protein, animal feed | Demand forecast |
| `geo` | ISO 3166 alpha-3 | Repository convention |
| `year` | 2025 base; 2026, 2030, 2035 | Demand-forecast resolution years |
| `metric` | `sales_value`, `volume`, `market_share` | See 4.2 |
| `price_basis` | constant 2025 USD | Demand forecast. US values are deflated with BLS CPI-U Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year averages. |
| `channel` | `retail`, `foodservice`, `all` | The demand forecast's plant-based question is retail only. Its cultivated and fermentation question covers retail plus foodservice, so anything bridged from it is `all`. Focal-market data will mostly be `all`; the field records which. |
| `quantile` | `q10`, `q50`, `q90` where a value is uncertain | Demand forecast |
| `source_id` | existing CO-, SA-, GP- plus the new prefixes in 4.4 | Conditional Markets paper |

The demand forecast asks for cultivated and fermentation-derived sales as two separate answers. Fermentation comes back as one total, so `fermentation_biomass` and `fermentation_precision` apply only to this workstream's own records. Its cultivated answer includes hybrids at their full product value, so it maps to `cultivated` and `hybrid_cultivated` together and cannot be split between them.

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

### 4.5 The bridge to the demand-forecast numbers

The demand forecast's second question gives US cultivated sales and US fermentation-derived sales as separate answers, each as q10, q50 and q90. On 2 October the workstream agreed to ask it for 2026, 2030 and 2035. The bridge uses only the cultivated answer.

1. **US analogue penetration:** `p_US(y, q)` = the forecast's cultivated sales ÷ the US meat denominator in 4.5.1, for the same year, quantile and 2025-USD basis.
2. **Baseline market in each focal country:** `D(c, y)` = projected meat consumption from the OECD-FAO Agricultural Outlook for the same years, in the units of 4.2.
3. **Conditional quantity:** `Q(c, y, q)` = `D(c, y)` × `p_US(y, q)` × `G(c)`, then capped by allocated supply `K(c, y)` where supply evidence exists. Otherwise the cap is recorded as unknown. `p_US` is a value share and `D` is a volume, so this step assumes cultivated meat sells at the same price per kilogram as the meat it replaces. Each scenario row states that assumption in `notes`.
4. **The gate `G(c)`** is 1 only when `H_rel` is `permitted` or `conditional` (with the condition met in the scenario) and `L` is `approved`. Otherwise it is 0. It is a switch, never a fraction.

The result is a conditional share ("if the gate is open and adoption follows the US path"), not a forecast.

**4.5.1 The US meat denominator.** The demand forecast does not use a meat denominator, and its survey has no meat question. This workstream therefore supplies its own, matched to the scope of the cultivated answer:

- US sales through retail and foodservice (`channel` = `all`).
- Meat, poultry and seafood, because the forecast's cultivated definition covers all animal meat, seafood included.
- Constant 2025 USD, using the same CPI series as the forecast (4.1).
- 2025 as the base year. 2026, 2030 and 2035 values are the 2025 value grown at the OECD-FAO projected rate for US meat consumption. At constant prices, value grows with volume.

Candidate sources, none yet checked: BEA personal consumption expenditure by type of product (meat, poultry, fish and seafood bought for home use) as a retail-only lower bound, and USDA ERS food availability volumes valued at BLS average retail prices as an all-channel estimate. Whichever is chosen is recorded once as an `MR-` row with its locator, and every `p_US` uses that row. The `category` list has no value for total meat, poultry and seafood, so one is added to `datapackage.json` with that row.

**4.5.2 What the cultivated answer contains.** Four features of the forecast's resolution criteria carry into `p_US`:

- **Pet food is included.** This workstream covers human food, so pet food inflates `p_US`. Where a respondent's rationale states the pet-food portion, it is removed before dividing. Otherwise `p_US` is marked in `notes` as an upper bound.
- **Hybrids count at full value.** A product with a small cultivated share counts entirely as cultivated. `p_US` is therefore the share of meat spending on products that contain cultivated cells, not the share of cultivated tissue. This matches rule 4.
- **There is no resolution source.** No published series measures US cultivated sales. The question resolves against the closest measure available at the time, and the forecast weights the reasoning above accuracy. `p_US` is an elicited judgment, and outputs say so.
- **It is close to unforecastable.** The forecast's LLM respondents report that the cultivated question is already nearly impossible to forecast for 2030. The quantiles are carried as given, never narrowed or averaged into a single figure. At the magnitudes involved, `Q` will be small in every focal country even with the gate open, so Phase 2 results will turn mainly on whether `G` is 0 or 1. `p_US` also carries US-specific obstacles, such as state sales bans, that do not apply in the focal countries. That limitation is stated alongside every result.

**Requests sent to the demand-forecast workstream on 30 September, answered 2 October:**

| Request | Answer |
|---|---|
| Extend the cultivated question from 2030 to 2026 and 2035 | Agreed. All three years will be asked. |
| Share the US meat sales denominator | None is used. This workstream supplies its own (4.5.1). |
| Are cultivated and fermentation reported separately? | Yes, as two answers. |

## 5. Double-counting rules

Each rule becomes a check in `tools/verify.mjs` where it can be tested mechanically.

1. **The religious gate is a switch.** `H_rel` enters as 0 or 1 through `G`. It is never multiplied in as a percentage.
2. **Consumer acceptance enters once.** The default carrier is the US analogue `p_US`. Local consumer surveys (Bryant et al. for India; Ahsan et al. and Irfan et al. for Pakistan) can replace `p_US` in a sensitivity run. They are never multiplied with it. They already include religious concerns, so they are also never combined with `H_rel` as a fraction.
3. **Food approval and religious status are counted once each.** Where `L_includes_halal` is `true`, the food approval already carries the halal condition, and `H_rel` is not applied a second time.
4. **Hybrid products are counted once.** Hybrid sales are counted once at the finished product under `hybrid_cultivated`. `cultivated_fraction` is used for supply and biomass accounting only, never as a displacement coefficient.
5. **The demand forecast's answers are never added together.** Its plant-based figure can include fermentation-derived products marketed as plant-based, and the forecast states that its cultivated and fermentation question does not add to the plant-based one. The bridge also never sums the cultivated and fermentation answers. It uses the cultivated answer alone.
6. **Insect protein is a feed input.** It affects the cost and supply of conventional chicken. It is never added to human protein supply, which would count the same protein twice (insect, then chicken).
7. **Each shock has a declared mechanism.** The animal-disease shock changes `D` and conventional price only; the food-sovereignty shock changes `K` and `L` only (section 7). Each scenario row records which, and no shock changes `p_US`.
8. **Related evidence counts once.** An original study and its correction count as one piece of evidence, as does a ruling and the reports that repeat it.
9. **Madhhab is context, not a weight.** No population-weighted acceptance figure is produced.
10. **Carried claims are re-checked.** Every claim taken from the Conditional Markets paper or the India–Pakistan brief starts with status `carried_unverified` and changes only after re-checking against the source.

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

## 7. Phase 2: scenarios

For each focal country and each year (2026, 2030, 2035):

| Gate state | No shock | Animal-disease shock | Food-sovereignty shock |
|---|---|---|---|
| Declared halal (Scenario 1) | compute `Q` | compute `Q` | compute `Q` |
| Declared haram | `Q` = 0 | `Q` = 0 | `Q` = 0 |
| Prolonged silence | no import pathway: `Q` = 0, reason-coded | reason-coded | reason-coded |

- **Animal-disease shock:** a natural or deliberate outbreak that cuts conventional poultry supply. It changes `D` and conventional price only. The size of the cut comes from `HP-` records of past outbreaks. Impact is analysed at the supply level only.
- **Food-sovereignty shock:** a state import-substitution or self-sufficiency push. It changes `K` (domestic capacity) and the time to `L`, never `p_US`.
- **2026** is expected to be near zero everywhere. It serves as a check that the model reproduces the present.

Outputs report `q10`, `q50` and `q90`, the reason code for every zero or missing cell, and the first- and second-order effects from section 3.

## 8. Timeline to 13 November

| Week of | Work |
|---|---|
| 30 Sep | Set up the schema, registers and verify checks. Send the demand-forecast workstream the requests in 4.5. Transcription and translation once the recording arrives. |
| 7 Oct | Document 3 (claims register). Document 5 tables. |
| 14 Oct | Document 4A and 4B. Consensus matrix. The demand forecast's first aggregated results are due. |
| 21 Oct | Document 4C and 4D. Elasticities. OECD-FAO baselines. US meat denominator (4.5.1). |
| 28 Oct | Phase 2 scenario grid using the demand forecast's medians and quantiles. |
| 4 Nov | Write-up, human review of translations and fiqh sources, final verification run. Buffer to 13 November. |

## 9. Resources needed

**From Umar**

- The interview recording (`IMG 7313.*`), with its date and the interviewer's name.
- Repository access for the working session.
- Flags answered on any Urdu-only source.

**From the demand-forecast workstream**

- Her cultivated q10/q50/q90 for 2026, 2030 and 2035 (agreed 2 October).
- Where a respondent states it, the pet-food portion of each cultivated answer (4.5.2).

The US meat sales denominator is no longer requested. This workstream sources it (4.5.1).

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
- Demand-forecast workstream answered on 2 October (4.5): all three years will be asked, cultivated and fermentation are separate answers, and it uses no meat denominator.
- Choose and source the US meat denominator (4.5.1) and record it as one `MR-` row.
- Ask the demand-forecast workstream whether respondents can state the pet-food portion of the cultivated answer separately (4.5.2).
- Mentor sign-off on the halal scope and the role question, deferred by decision.
- Flags for Urdu-only sources: none yet.
