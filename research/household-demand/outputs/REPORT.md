# Household demand, US calibration and proxy market scenarios for India and Pakistan

**Local research draft, 19 October 2026. Human scholarly review pending.** No new market estimate has been accepted into the claim ledger. This paper is a reproducible diagnostic contribution to the India-Pakistan research programme; replacing the team's D1 forecast requires separate method agreement and acceptance. These results do not measure the supply benchmark in `future-research/`.

## Abstract

This study asks what a household-based model implies for plant-based meat and liquid-milk retail value in India and Pakistan in 2026, 2030 and 2035. It combines household expenditure microdata, measured purchaser elasticities, a US conversion and spending calibration, observed retail price summaries, and official demographic and income paths. In India, the main conditional simulation produces median values of 712.415, 1,351.182, and 1,909.799 million US dollars at 2025 prices. These are conditional diagnostic model outputs, not validated market forecasts. Pakistan's national numerical results remain withheld here because the plant-meat price input is a placeholder. Complete household protein-spending shares and the egg/fermentation residual remain missing. Leave-one-state-out validation covers reported-item spending transfer, and attains 75.0% coverage for nominal 80% intervals. Elicitation coverage is 2 accepted runs with 28 pending; partial model responses cannot establish a completed panel.

## 1. Research question, estimand and comparison

The estimand is annual retail value of modern plant-based meat and liquid milk in constant 2025 US dollars, converted at market exchange rates. Tonnes refer to product mass. Traditional soya chunks are an expenditure and substitution analog, excluded from modern alternative-protein market value. The meat-eating and vegetarian plant-meat channels are mutually exclusive household segments; the plant-milk channel covers both. The model does not identify trial, repeat purchase, displaced animal consumption, nutritional equivalence or producer revenue.

The comparison proxy is the existing GFI-anchored scenario series, selected only where `record_type=scenario`, `quantity=market_value` and the exact target year and quantile match. Its producer, `tools/build_altprotein_proxy.py`, fixes price year 2025. The proxy covers all plant-based retail categories; the household calculation covers meat and liquid milk. The intended egg/fermentation residual cannot be identified from available category evidence. Subtracting US meat and milk from the entire GFI total would also include cheese, yogurt and other foods. Consequently the table is a comparison of distinct estimands: a dollar difference would be misleading and is not reported. The India proxy anchor additionally treats an ambiguously dated rupee figure as nominal 2022; this remains an explicit source assumption.[^gfi]

## 2. Data and provenance

India HCES 2023-24 supplies 261,953 household records and Pakistan HIES 2024-25 supplies 30,123. These raw records remain outside the repository. Household and bootstrap hashes are bound in the simulation artifacts. The India implementation reconstructs survey-period expenditure and quantities and keeps source and recall distinctions. Both countries use leave-one-out prices in state by price-area by sector cells. The price area is district in India and PR-code geography (rural district or urban division) in Pakistan. Pakistan maps monthly and 14-day recall to a monthly basis. Official Pakistan stratum labels remain unresolved; province-stratified PSU resampling uses the actual PSUs and does not consume invented stratum labels. This is a variance caveat, distinct from the missing plant-meat price that holds Pakistan market totals.[^surveys]

The US calibration uses BLS 2023 Diary consumer units with valid food reporting, with Interview weights checked independently. Consumer units do not match households exactly, so their use as the US household calibration base adds a comparability limitation. The primary packaged-food condition remains MISCFOOD above zero, which includes miscellaneous prepared foods and is broader than the intended Indian bakery/confectionery condition. R38 requested a narrower UCC crosswalk, but R40 parked it after the BLS dictionary could not be retrieved; `buys_packaged_food_r38.status` remains NOT_DONE. This unresolved denominator mismatch affects both the inferred meat conversion and the plant-milk addressable base. It is not evidence that the two survey segments are harmonized. For meat, GFI/SPINS 2025 sales of USD 1.0 billion and penetration of 0.11, the Bryant US intention proportion 0.329, and CE addressable share 0.607223 give conversion 0.550616 and annual spending per adopting household USD 67.595968. Plant milk uses USD 2.7 billion, penetration 0.38, CE urban-packaged share 0.739612, conversion one and annual spending USD 52.831585. Its implied conditional adoption base is 0.513783. This substitutes observed US milk purchasing for an unavailable milk-intention measure. US all-category sales of USD 7.9 billion remain contextual, not the denominator for meat conversion.[^bls][^gfi][^bryant]

The Bryant India sample is disproportionately urban, educated and affluent. Its full-sample top-two purchase-intention proportion is 0.628; it is not an India national adoption estimate. Pakistan has no equivalent observed intention value and uses the registered uniform transfer between 0.329 and 0.628. The 2019 intention versus 2025 penetration timing mismatch and GFI meat category's inclusion of seafood remain unresolved. There is no independent country validation of intent-to-purchase conversion.[^bryant]

Price inputs use the captured public retail product pages and survey chicken/milk unit values. They do not establish a representative store, city or national price distribution. Plant prices captured in 2026 are deflated to 2025 with official CPI; survey references use weighted survey-period CPI. The retained World Bank capture gives 87.158448 INR/USD and 281.143001 PKR/USD in 2025. IMF October 2026 projections provide income and CPI; GDP per capita is used as an income proxy, with the US 2025 comparison held fixed. UN WPP 2024 supplies population bands. WUP 2018 census-definition urban shares are used because WUP 2025 Degree of Urbanisation categories do not match survey urban codes.[^drivers]

### Source-ID and exact-byte inventory

The table below identifies current captured inputs. `inputs/manifest.csv` supplies URLs, capture dates, storage locations, approval notes and per-input caveats. `protocol.json` and `logs/registration-receipt.json` preserve the preregistration; later deviations are enumerated in section 7. `comparison-metadata.json` and `sobol-diagnostics.json` bind the current producer, source inventory and aggregate input hashes. Protocol source IDs are distinct from claim acceptance IDs.

| input_id | sha256 |
| --- | --- |
| bryant2019_html | 8776f02c57e929982de9954d097908e6bbacf67b02216aa6e2cedfdf5f398814 |
| bls_ce_2023_interview | 97e9a17edeee28e77a3fd5a7d874e5f4b9034222be204e25b0d902f4c82235ac |
| bls_ce_2023_diary | d9990b92f4cc6546e3d6d7a1354300ef953ffca412d90cdb41c75372f90b94d6 |
| gfi_marketresearch_html | d06e4649b1dc7ca30767f50d93428e314d5bca930bde0eae4859a4d0a18895dc |
| gfi_price_gap_png | ccd9d6108f5506fb2add7eedbe491ca7e93a87d2658530bc34353e53da724c22 |
| imf_weo_2026_10_ngdpdpc | d1143922c6ec0248cfc715d66c6d90f347396879a94ef464d150b7b98b75db17 |
| imf_weo_2026_10_ngdp_rpch | 5200170b0f19f025e4e0a4e7685d8d5182e11068bff6ef4c92aea400739f0148 |
| imf_weo_2026_10_lp | 9ddc36efbd0d0e8166afa9d00e99526425b3c484daf83f5c230af38213410dd0 |
| imf_weo_2026_10_pcpipch | e36fb78dc58c5b50df615add2656469d316fe0c11416559b473de78d56b9aa1d |
| imf_weo_2026_10_indicators | 30d77f9f74ca8c2777193db842876398688dad62f846e76fbdf4d49899e48d62 |
| un_wpp_2024_medium | 286ac36bb1415e2e1ade03acfef0a29f0e4c087e2f78e38c48f50c5df89082bc |
| un_wpp_2024_other_variants | a860504df54877e4c19788bf6e16920d6017d021b4c149eaf8b5662674180a54 |
| un_wup_2018_excel_zip | 80eb71bbabb46cb2e1599b51b16133bf28b0a99a541d72de20a1248ec6170a75 |
| un_wup_2025_f02 | 3b262c6dcad2cc0ac5eef3e42c036207184de72926207e7d39640f7d45c4cedc |
| price_snapshot_2026_10 | 65a4d6a702fbcd82c0966ad870c168defaaab2c3280615a7370d4963e10c43dd |
| gfi_us_sales_webinar_2020 | a3215062d607dbe5aa1bfcdece1d9fb1aaca1529c1d1feb9b43f06696dbd7b5d |
| gfi_us_sales_insights_2021 | c2b765e9c0acfe083640b6b32b750efecb8bfa82566216506f606d61b1e7cb07 |
| gfi_us_sales_soti_2022 | 712938d7fa3ce981dabc2c88cdfcdeca45c46a0c7fdecc915048189a813110e5 |
| gfi_us_sales_soti_2023 | 444fbb4b0d52939dda1c5991a1f7d2d9b1eba336146ea88209b3a8e8c3185cb4 |
| gfi_us_sales_soti_2024 | 148ae79cb0bd71d46023b398a55b02845a5b64cbf9d1f8eebd9cc2e3039c6699 |
| gfi_us_sales_press_2021 | abc1087bd32b3477971fc23b193f7624569c09456826b38ed9d6b569176c3850 |
| gfi_us_sales_press_2022 | 4753d2ff8c4f9a916eebd6e0b990425baed4ef7106e51a2f973aa5612d970197 |
| wdi_fx_2025_ind_pak | afc4d7b4d7f23090887403e1aabf4108679919c15bb45023b054563613b23439 |

## 3. Household model and uncertainty

For each country, year and segment-product pair, expected value is the addressable household count multiplied by adoption probability and annual spend per adopter. Addressable households equal population divided by weighted survey household size, multiplied by the survey addressable share scaled by the urban-share path, bounded by all households. Adoption equals US-calibrated conversion times country intention times a relative-price adjustment times the Bass cumulative adoption fraction, bounded to [0,1]. Spending scales US adopter spending by the ratio of target to US real income raised to the measured income elasticity. Price and income terms require finite operands and coefficients: neutral exponent identities never turn absent inputs into known values.

Elasticities come from purchaser-only equations with fixed effects and leave-one-out cell unit values. They describe the intensive margin among recorded purchasers. They neither identify participation by non-purchasers nor remove quality bias or cell-price measurement error. Requiring all equation prices reduces the usable sample. Five hundred actual design/PSU bootstrap draws are recentered on the point estimates; one bootstrap row is sampled per country, preserving dependence among its price, cross-price and income coefficients. Failed coefficients propagate missingness, rather than being dropped from quantiles. Positive own-price coefficients are capped at zero in simulation (R25), leaving India dairy with little or no price response. This does not repair identification, and can materially change scenario response. The main India run caps 29,937 of 60,000 own-price coefficient evaluations.

For vegetarian households, the negative expenditure-weighted chicken-equation cross-price coefficients on paneer, soya and pulses adjust the inverse relative premium. The same substitute basket supplies its price comparison. This is a diagnostic transfer assumption, not an estimated plant-based vegetarian own-price elasticity. The literal signed alternative is reported separately with paired random draws. Halal compliance for sold Pakistan products is assumed; it is not an estimated probability or scenario switch.

No eligible local analog time series survived the registered diffusion screen, so the main path uses the fixed Bass prior p=0.03, q=0.38. South Asian launch dates remain assumptions recorded in the protocol. The US stress scenario uses its fitted shape on each country's launch clock. The fixed prior creates no sampled diffusion uncertainty; a narrow main interval cannot be read as evidence that diffusion speed is known.[^bass]

One joint Monte Carlo uses 10,000 draws and seed 20261018. India and US intention draws use Beta(mean times n, (1 minus mean) times n), with source sample sizes 1024 and 987; a fixed inverse-CDF grid is used. Pakistan uses its registered transfer range. Driver bands are mapped by an assumed piecewise-linear quantile function through low/mid/high at coordinates 0/0.5/1. The endpoints are not claimed to be calibrated tail probabilities. Dependence among these grouped factors is assumed absent except for explicitly shared US intention and joint coefficient draws. These assumptions omit important structural, measurement, source and between-model uncertainty. Reported p10-p90 values therefore describe a conditional simulation distribution, not an 80% guarantee about future markets.

Volumes divide value by projected plant-product prices. Liquid milk uses the explicit one litre equals one kilogram convention; no protein-tonnage claim follows. The meat-eating channel is capped by 2023 FAOSTAT poultry food supply per person scaled with population, with one kilogram plant product assumed to displace one kilogram chicken product. The cap reduces value and volume together; it does not constrain the vegetarian channel. No India main or stress draw binds this ceiling. This is a supply-based plausibility bound, not observed substitution evidence.

## 4. Results and scope coverage

All values in the next table are million USD at 2025 prices. Held cells are not zero. Pakistan proxy values are retained because they come from a separate existing proxy calculation, not from the held household plant-price input.

| country | year | method | p10 | p50 | p90 | status |
| --- | --- | --- | --- | --- | --- | --- |
| India | 2026 | household_model | 675.554 | 712.415 | 754.481 | DIAGNOSTIC |
| India | 2026 | gfi_proxy | 68.638 | 93.237 | 124.506 | PROXY_SCENARIO |
| India | 2030 | household_model | 1,280.380 | 1,351.182 | 1,431.195 | DIAGNOSTIC |
| India | 2030 | gfi_proxy | 101.825 | 187.812 | 334.480 | PROXY_SCENARIO |
| India | 2035 | household_model | 1,803.716 | 1,909.799 | 2,024.744 | DIAGNOSTIC |
| India | 2035 | gfi_proxy | 165.637 | 447.504 | 1,141.553 | PROXY_SCENARIO |
| Pakistan | 2026 | household_model | held | held | held | HELD_PLACEHOLDER_INPUT |
| Pakistan | 2026 | gfi_proxy | 1.472 | 3.645 | 6.617 | PROXY_SCENARIO |
| Pakistan | 2030 | household_model | held | held | held | HELD_PLACEHOLDER_INPUT |
| Pakistan | 2030 | gfi_proxy | 2.280 | 5.977 | 13.682 | PROXY_SCENARIO |
| Pakistan | 2035 | household_model | held | held | held | HELD_PLACEHOLDER_INPUT |
| Pakistan | 2035 | gfi_proxy | 3.592 | 11.759 | 36.100 | PROXY_SCENARIO |

India component results separate the modelled channels. Their medians need not sum exactly to the median of the joint total.

| year | pair | p10 | p50 | p90 |
| --- | --- | --- | --- | --- |
| 2026 | dairy | 272.975 | 285.977 | 298.920 |
| 2026 | meat | 250.915 | 273.825 | 299.854 |
| 2026 | vegetarian | 138.644 | 152.389 | 167.609 |
| 2030 | dairy | 534.009 | 560.598 | 586.957 |
| 2030 | meat | 465.620 | 507.974 | 555.532 |
| 2030 | vegetarian | 257.164 | 282.836 | 311.057 |
| 2035 | dairy | 781.357 | 823.311 | 865.857 |
| 2035 | meat | 638.748 | 697.462 | 762.334 |
| 2035 | vegetarian | 352.972 | 388.231 | 427.295 |

India product-volume quantiles, tonnes:

| year | p10 | p50 | p90 |
| --- | --- | --- | --- |
| 2026 | 163,833.076 | 170,888.948 | 177,866.629 |
| 2030 | 316,530.274 | 330,640.184 | 345,092.939 |
| 2035 | 456,133.518 | 478,613.339 | 502,049.887 |

Neither country has a complete observed mapped protein-food basket for any household: India 0 of 261,953; Pakistan 0 of 30,123. Missing purchase observations are not assigned zero. Whole-protein monetary spending denominators and spending shares therefore remain null. The supply benchmark's grams of protein per person per day cannot supply a monetary denominator. Likewise the modelled subtotal plus the requested residual remains null. These are identification limits, not failed formatting or a zero-sized category.

### Paired scenario results

Each row below uses the same 10,000 factor draws. `paired_delta_p50` is the median of draw-by-draw differences from main, not a subtraction of marginal medians. AI declines of 2% and 5% annually are illustrative input assumptions; price parity by 2030 is an illustrative date, not a source-backed forecast. AI affects the plant price ratio and its price/volume consequences, rather than adding an arbitrary market-growth premium.

| year | scenario | p10 | p50 | p90 | paired_delta_p50 |
| --- | --- | --- | --- | --- | --- |
| 2026 | main | 675.554 | 712.415 | 754.481 | 0.000 |
| 2030 | main | 1,280.380 | 1,351.182 | 1,431.195 | 0.000 |
| 2035 | main | 1,803.716 | 1,909.799 | 2,024.744 | 0.000 |
| 2026 | us_stress | 34.162 | 36.026 | 38.153 | -676.389 |
| 2030 | us_stress | 497.969 | 525.506 | 556.624 | -825.676 |
| 2035 | us_stress | 1,744.677 | 1,847.288 | 1,958.471 | -62.511 |
| 2026 | ai_2pct | 675.554 | 712.415 | 754.481 | 0.000 |
| 2030 | ai_2pct | 1,308.710 | 1,380.273 | 1,461.371 | 29.363 |
| 2035 | ai_2pct | 1,892.911 | 2,003.502 | 2,121.723 | 93.495 |
| 2026 | ai_5pct | 675.554 | 712.415 | 754.481 | 0.000 |
| 2030 | ai_5pct | 1,354.872 | 1,428.450 | 1,511.409 | 77.346 |
| 2035 | ai_5pct | 2,048.511 | 2,168.125 | 2,297.181 | 258.470 |
| 2026 | parity_2030 | 675.554 | 712.415 | 754.481 | 0.000 |
| 2030 | parity_2030 | 2,022.134 | 2,172.179 | 2,344.281 | 821.832 |
| 2035 | parity_2030 | 2,826.249 | 3,036.787 | 3,277.377 | 1,127.557 |
| 2026 | literal_signed | 703.887 | 744.577 | 791.868 | 32.537 |
| 2030 | literal_signed | 1,333.300 | 1,410.739 | 1,499.654 | 60.302 |
| 2035 | literal_signed | 1,877.851 | 1,991.079 | 2,117.492 | 82.744 |

The large early sensitivity to the transferred US diffusion shape shows why the fixed-prior main interval is incomplete as a total uncertainty account. The vegetarian sign comparison isolates a consequential transfer assumption. An AI price change can affect product volume even when the own-price response is capped; the inferred value response remains conditional on that cap and the cross-price mapping.

### Global sensitivity on actual model cells

Saltelli first-order and squared-difference total indices were computed from the shared deterministic evaluator for each country-year at base n=8192 and 2n=16384, eight unit-cube factors and 81,920/163,840 model evaluations per cell. Each country-year is evaluated independently with all required components retained. The largest total-effect factors for India at 2n are:[^saltelli]

| year | parameter | first_order | total | rank_total |
| --- | --- | --- | --- | --- |
| 2026 | us_intent | 0.400 | 0.403 | 2 |
| 2026 | India:elasticities | 0.460 | 0.463 | 1 |
| 2030 | us_intent | 0.377 | 0.379 | 2 |
| 2030 | India:elasticities | 0.402 | 0.406 | 1 |
| 2035 | us_intent | 0.329 | 0.332 | 1 |
| 2035 | India:elasticities | 0.319 | 0.324 | 2 |

- India 2026: top-two set stable = True; full uncertain-factor order stable = True; maximum total-index change = 0.003588.
- India 2030: top-two set stable = True; full uncertain-factor order stable = True; maximum total-index change = 0.002901.
- India 2035: top-two set stable = True; full uncertain-factor order stable = True; maximum total-index change = 0.002102.

The complete CSV retains both sample sizes, negative estimates and any first-order estimate above its total. The JSON sidecar preserves split-half differences, exact estimator settings, source hashes, fixed/inactive factors and rank diagnostics. Fixed Bass factors and degenerate urban bands have zero sensitivity by construction. Income and population effects are conditional on their chosen bands. The joint elasticity factor measures combined coefficient uncertainty; it cannot identify separate causal contributions for each coefficient. n/2n agreement is a numerical stability check, not a convergence certificate or validation of the input distributions. Pakistan calculations and their diagnostics remain in the separate placeholder-derived research directory; no Pakistan numerical sensitivity is copied into this report.

## 5. Validation and falsification limits

Leave-one-state-out validation evaluates observed-item animal spending per person per month, in survey-price INR, using demographics only: household size, urban/rural sector, religion and caste. Training-only weighted log1p regression, centering, scaling and smearing prevent heldout outcome leakage. MPCE, food quantities, unit values, segments and state effects are excluded. Within each training fold, nested heldout-state log errors supply the empirical 10th/90th interval; no outer heldout outcome calibrates its own interval.

The real run evaluates 254,364 households across 36 states; 7,589 households have no valid animal-item observation. All eight animal groups are observed together for zero households. State MAE is INR203.569486 per person per month; median absolute percentage error is 25.438567%; measured coverage is 75.0% (27/36) against nominal 80%. The model compresses state differences and nine states miss their interval. This is informative evidence of imperfect geographic transfer.

These intervals are empirical state-transfer predictive intervals, not survey-design confidence intervals. Observed-item sums vary in coverage and cannot validate complete spending totals. The separately refitted training-fold elasticities diagnose coefficient stability; they do not drive the demographic predictions. This exercise does not validate plant adoption, the structural price response or future alternative-protein value. Temporal validation against earlier harmonized HCES rounds remains unrun pending the author's microdata registration and compatible data.

## 6. Elicitation and model-from-input comparison

The protocol requires 10 fresh contexts for each of two named models in each of three regions, 60 total. The author currently authorized Astra only: selected models ['gpt-6-astra'], active requirement 30 runs; Claude is deferred by the author. Current recorded active coverage: 2 accepted, 28 pending; registered study size 60. Completing the Astra phase does not complete the registered two-model study. The completion artifact's provider holds, attempts and individual slots are authoritative. A partly completed region/model panel remains PARTIAL_PANEL and is never described as completion. Repeated outputs of an AI model are dependent machine responses, not independent human forecasts.

The exact US questionnaire is hash-bound and stored separately because public redistribution rights are unestablished. India and Pakistan adaptations preserve explicit unresolved forecast questions and resolvable proxy questions. Project domains and project-derived estimate contamination are screened. The original US cultivated/fermentation and blind-spot questions remain intact. Public reporting remains held pending scholarly review; Anna must also be notified before the US comparison is reported outside this local draft.

| country | year | method | source_model | n_accepted | p50 | status |
| --- | --- | --- | --- | --- | --- | --- |
| India | 2026 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| India | 2026 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| India | 2026 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| India | 2026 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |
| India | 2030 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| India | 2030 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| India | 2030 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| India | 2030 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |
| India | 2035 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| India | 2035 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| India | 2035 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| India | 2035 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2026 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| Pakistan | 2026 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2026 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| Pakistan | 2026 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2030 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| Pakistan | 2030 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2030 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| Pakistan | 2030 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2035 | panel_headline | claude-opus-5-5 | 0.000 | held | HELD_PANEL |
| Pakistan | 2035 | model_from_panel_inputs | claude-opus-5-5 | 0.000 | held | HELD_PANEL_INPUTS |
| Pakistan | 2035 | panel_headline | gpt-6-astra | 0.000 | held | HELD_PANEL |
| Pakistan | 2035 | model_from_panel_inputs | gpt-6-astra | 0.000 | held | HELD_PANEL_INPUTS |

Panel headline p10/p50/p90 summarize accepted runs' point medians. They are not pooled respondent predictive bounds. For each model separately, the adapter takes its median conversion, Bass p, Bass q, price-parity year and annual AI decline, then genuinely reruns the same evaluator with 10,000 paired draws. Conversion changes the meat and vegetarian channels; observed US-milk conversion remains its category-specific anchor. Bass and parity affect each modelled pair. The elicited AI input is a manufacturing-cost decline, while the evaluator changes retail price; this rerun explicitly assumes full retail pass-through as an extra sensitivity assumption, not a panel-endorsed or observed relationship. US-intention sampling is disabled for these reruns so the supplied fixed conversion median is not contaminated by the empirical US conversion denominator. The resulting Monte Carlo interval is conditional on fixed panel medians and is not the panel's across-run spread. An unresolved parity answer stays null and holds that rerun; a date is never invented.

- India, claude-opus-5-5: HELD_PANEL_INPUTS; accepted runs 0; all five genuine finite input medians required; unresolved parity is not assigned a date.
- India, gpt-6-astra: HELD_PANEL_INPUTS; accepted runs 0; all five genuine finite input medians required; unresolved parity is not assigned a date.
- Pakistan, claude-opus-5-5: HELD_PANEL_INPUTS; accepted runs 0; all five genuine finite input medians required; unresolved parity is not assigned a date.
- Pakistan, gpt-6-astra: HELD_PANEL_INPUTS; accepted runs 0; all five genuine finite input medians required; unresolved parity is not assigned a date.

Only explicit COMPLETE_PANEL or PARTIAL_PANEL producer statuses may supply headline or input values. Placeholder-derived, absent or unknown source-status labels are held before publication and before any model evaluation; rejected input medians are not copied to the public summary. Coverage can downgrade an incomplete count, but never upgrades an explicitly partial panel. The elicited dairy category includes other dairy alternatives, while the household engine covers liquid milk. Therefore even a completed panel does not yield a matched-scope dollar gap. Raw headline and conditional rerun values can be inspected as separately labelled local diagnostics; the numerical gap remains null. US serves calibration/comparison only and does not become a target-market row.

## 7. Tracked methods deviations and interpretation

The frozen registration predates implementation rulings; it is preserved rather than silently rewritten. The controller ledger is not distributed with the repository, so consequential decisions are recorded here. R24 recenters bootstrap coefficients; R25 caps positive own-price draws; R26 restricts interpretation to purchasers; R27 collapses singleton design strata into the stated pooled strata; R28 uses leave-one-out cell prices; R29 records attenuation. R30-R33 define an India vegetarian addressable segment, keep no-food households unknown, and leave NFHS calibration unused until a valid crosswalk and approved data exist. R34-R39 specify category-specific US calibration and food-reporting exclusions, and requested a packaged-food crosswalk. R40 holds that R38 crosswalk unresolved; the broader MISCFOOD primary condition remains, so cross-country denominator alignment is incomplete. R41 holds main AI decline at zero; R43 propagates Pakistan price taint; R44-R46 specify intention, addressable scaling and Beta uncertainty.

| Ruling | Implemented decision | Consequence retained |
| --- | --- | --- |
| R47 | Bass p and q fixed at registered prior; US shape separate stress | Main uncertainty omits unknown diffusion spread; zero Sobol effect does not imply knowledge |
| R48 | Negative expenditure-weighted chicken cross-price transfer for vegetarian premium; literal sign separate | Vegetarian price response is a transfer assumption, not identified plant demand |
| R49 | Exact US instrument, including punctuation, hash-preserved | Source instrument fidelity takes priority over prose conventions |
| R50 | Supplied instrument and adaptations remain local and ignored | Reproduction needs separately supplied rights-bounded text; no text embedded here |
| R51 | Missing complete-basket denominator and disaggregated residual stay null | No whole-protein spending share or GFI-matched total claimed |
| R52 | Contamination guard matches complete numeric claims, plus provenance and domain controls | Arbitrary digit fragments such as Comtrade 210610 do not trigger false matches; source inspection remains necessary |
| R53 | Leakage-free demographic transfer of observed-item spending; separate training elasticity stability | No structural/adoption validation; final corrected eight-group complete-basket count is zero |

Further limitations include NFHS non-access and the zero-recall vegetarian diagnostic, limited retailer/city coverage, the unresolved MISCFOOD versus Indian packaged-food denominator mismatch, uncertain Pakistan country intention, source-price vintage ambiguity, real-income proxy choice, lack of independent baseline acceptance, and the assumed product-mass displacement and liquid density. No supplied holdout or code test resolves these scholarly questions.

## 8. Reproduction and acceptance gates

From the library root, use the existing environment and local inputs:

```sh
source '../OUTPUTS/Deep Research 2026-10/.venv/bin/activate'
python research/household-demand/build_outputs.py --n 10000 --sobol-n 8192
python -m pytest research/household-demand/tests/test_build_outputs.py -q
python -m ruff check research/household-demand/build_outputs.py research/household-demand/tests/test_build_outputs.py
python -m black --check research/household-demand/build_outputs.py research/household-demand/tests/test_build_outputs.py
python research/household-demand/synthetic.py --check
```

The default builder reads source- and code-hashed external bootstrap caches, never downloads data or changes claim acceptance. CSV values use six decimal places; Markdown tables use three. Strict JSON preserves higher precision. Empty CSV numeric cells represent missing values. `comparison-metadata.json` hashes the source files and resulting CSV; Sobol sidecars bind their analysis separately. No rounded CSV value is fed back into the simulation.

The current code/test review is distinct from the independent recomputation receipt and full library/workspace verification, which the coordinator records separately. Exact agreement at stated rounding is required for `comparison.csv` and `sobol.csv`; this manuscript does not claim that an unrun recomputation passed. Separate remaining gates are official baseline/lineage acceptance, independent empirical source reconciliation, NFHS/historical-round access, complete genuine panel coverage, team agreement before replacing D1, author-controlled US notification and human scholarly review. No email, form, message, push or publication is performed by this builder. `team-method-note.md` is a draft for the author.

## Notes

[^surveys]: Ministry of Statistics and Programme Implementation, *Household Consumption Expenditure Survey 2023-24*, source definitions and local input provenance in `households_india.py`, `codes.py` and `logs/india-households-run.json`; Pakistan Bureau of Statistics, *Household Integrated Economic Survey 2024-25*, source definitions and local input provenance in `households_pakistan.py` and `logs/pakistan-households-run.json`. Baseline acceptance remains separate from code-level parsing and reproduction.
[^bls]: US Bureau of Labor Statistics, *Consumer Expenditure Survey 2023 Public-Use Microdata*, Diary and Interview files, retained capture reviewed locally October 19, 2026, https://www.bls.gov/cex/pumd.htm. Exact source ZIP hashes and weight/food definitions appear in `inputs/manifest.csv` and `outputs/us_calibration.json`.
[^gfi]: Good Food Institute, “Plant-Based Retail Market Overview,” 2025 SPINS retail results, retained capture reviewed locally October 19, 2026, https://gfi.org/marketresearch/. Existing India anchor and proxy Source IDs: `gfi_india_smart_protein_economic_analysis_2022`, `gfi_us_plant_based_retail_2025`, `imf_weo_2026_10`, and `worldbank_wdi_official_exchange_rate_2026`, in `research/india-pakistan/data/altprotein_proxy_inputs.csv` and `altprotein_proxy_scenarios.csv`.
[^bryant]: Christopher Bryant, Keri Szejda, Nishant Parekh, Varun Deshpande, and Brian Tse, “A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China,” *Frontiers in Sustainable Food Systems* 3 (2019), article 11, https://doi.org/10.3389/fsufs.2019.00011. The registered top-two intention definition, values and sample caveat are in `protocol.json`.
[^drivers]: International Monetary Fund, *World Economic Outlook*, October 2026, DataMapper series NGDPDPC, NGDP_RPCH, LP and PCPIPCH, https://www.imf.org/external/datamapper/; United Nations, *World Population Prospects 2024*, https://population.un.org/wpp/; United Nations, *World Urbanization Prospects 2018*, https://population.un.org/wup/; World Bank, “Official Exchange Rate (PA.NUS.FCRF),”2025 values in the retained official capture. Exact hashes, methods and vintage exclusions are in the input manifest and `outputs/drivers.json`.
[^bass]: Frank M. Bass, “A New Product Growth for Model Consumer Durables,” *Management Science* 15, no. 5 (1969): 215-27, https://doi.org/10.1287/mnsc.15.5.215; Fareena Sultan, John U. Farley, and Donald R. Lehmann, “A Meta-Analysis of Applications of Diffusion Models,” *Journal of Marketing Research* 27, no. 1 (1990): 70-77. The prior is the pre-registered fallback; `protocol.json` records its secondary-source verification limitation and `outputs/diffusion.json` records rejected analogs and the separate US stress fit.
[^saltelli]: Andrea Saltelli et al., “Variance Based Sensitivity Analysis of Model Output: Design and Estimator for the Total Sensitivity Index,” *Computer Physics Communications* 181 (2010): 259-70, https://doi.org/10.1016/j.cpc.2009.09.018. The implementation uses ordinary pseudorandom Monte Carlo, not a low-discrepancy Sobol sequence.
