# Demand elasticities: four countries, twelve species questions

AI-assisted research draft; human scholarly review pending. This review records historical study estimates and their limitations. It supplies no validated coefficient for current cultivated-meat demand.

[Structured review](elasticity-review.json) · [All extracted estimates](elasticity-estimates.json) · [CSV](elasticity-estimates.csv) · [Source register](source-register.json)

## Reading the estimates

An own-price elasticity describes the response of a good to its own price; a cross-price entry describes the **row good’s quantity response to the named column good’s price**. Reversing them changes the question. Marshallian and Hicksian estimates have different conditioning; expenditure responses are separate again. The tables preserve reported signs, marks and t-values, including anomalies. Missing standard errors and confidence intervals are not zero. Fish and camel response rows and nonfocal livestock response rows are outside this extraction; their original tables remain available.

## Twelve required questions

| Requirement | Reported category | Finding and limit |
| --- | --- | --- |
| EL-IND-CHICKEN | chicken | Rural and urban chicken own-price estimates are -0.432 and -0.328; their reported t-values are -0.44 and -0.61. The unrestricted 1993–94 state-aggregate model leaves compensation and current transport unresolved. |
| EL-IND-BEEF | beef and buffalo meat | The closest original category combines beef and buffalo; rural own-price is positive 3.179 and urban is -0.476. Neither identifies beef alone. |
| EL-IND-MUTTON | mutton and goat meat | The original bundles mutton and goat. Rural and urban own-price entries are -0.030 and -3.308; separate adult-sheep mutton demand is unidentified. |
| EL-PAK-CHICKEN | chicken | HIES 2010–11 chicken own-price entries are -0.648 rural, -1.022 urban and -0.807 pooled. The source needs reconciliation of sample counts and log-model notation before forecast use. |
| EL-PAK-BEEF | beef row / beef and buffalo category unresolved | Table 7 uses a short beef response label and a beef-and-buffalo price column. Its pooled reported own entry is -1.068, but a beef-only quantity/price estimand cannot be established. |
| EL-PAK-MUTTON | mutton row / mutton and goat category unresolved | Table 7 uses a short mutton response label and a mutton-and-goat price column. Pooled reported own entry is -0.859; sheep-only mutton effects remain unidentified. |
| EL-SAU-CHICKEN | chicken | The national 1985–2010 Rotterdam model gives conditional compensated chicken own-price -0.088 and group expenditure elasticity 0.48. It does not supply a current unconditional Marshallian parameter. |
| EL-SAU-BEEF | beef | The national 1985–2010 Rotterdam model gives conditional compensated beef own-price -0.204 and group expenditure elasticity 1.07. Elasticity SE/CI are not supplied in Table 6.4. |
| EL-SAU-MUTTON | lamb | The closest original response is lamb: conditional compensated own-price -0.103 and group expenditure elasticity 1.27. The publication does not establish an adult-sheep mutton mapping. |
| EL-ARE-CHICKEN | chicken | The publication reports chicken own-price -0.319 Marshallian and -0.531 Hicksian with positive expenditure elasticity 0.690. The more-negative compensated value conflicts with the positive-share Slutsky relation. |
| EL-ARE-BEEF | beef | Reported beef own-price is +0.666 Marshallian and +0.568 Hicksian. Positive Hicksian own effect and the negative compensation increment with positive expenditure elasticity prevent coherent demand-model transfer. |
| EL-ARE-MUTTON | lamb | The source has separate lamb and goat categories, neither explicitly mutton. Lamb own-price is -0.041 Marshallian and +0.134 Hicksian; the latter also fails the nonpositive own substitution restriction. |

## IND: IND-DASTAGIRI-2004

[P1C7-EL-IND-DASTAGIRI-2004](https://doi.org/10.22004/ag.econ.344973). Observation period: 1993–1994.  Indian rural and urban residents; NSS 50th round.

Unrestricted double-log system, GLS/SURE; regional dummy. Eight price regressors including other-food and non-food; real income/expenditure held in equation. Exact compensation concept unresolved. not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification

Sample: underlying households rural: 76784; underlying households urban: 40009; estimation observation sets total: 64; unit: state/union-territory rural and urban aggregates; not 116793 independent model observations. Cross-sectional state-level quantity/value variation; no causal price instrument established.

Tables 2–4 report t-values and significance marks, not elasticity SE or CI.

| Response category | Type and compensation | Price/expenditure variable | Sample | Value | Reported t / mark |
| --- | --- | --- | --- | ---: | --- |
| mutton and goat meat | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | mutton and goat meat | rural state aggregates | -0.03 | -0.03 / None |
| beef and buffalo meat | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | beef and buffalo meat | rural state aggregates | 3.179 | 2.16 / *** |
| chicken | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | chicken | rural state aggregates | -0.432 | -0.44 / None |
| mutton and goat meat | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | mutton and goat meat | urban state aggregates | -3.308 | -1.21 / None |
| beef and buffalo meat | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | beef and buffalo meat | urban state aggregates | -0.476 | -0.27 / None |
| chicken | own_price; not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification | chicken | urban state aggregates | -0.328 | -0.61 / None |
| mutton and goat meat | expenditure; not applicable to expenditure estimand | expenditure | rural | 0.52255 | 0.3741 / None |
| mutton and goat meat | expenditure; not applicable to expenditure estimand | expenditure | urban | 3.1978 | 1.9083 / ** |
| mutton and goat meat | expenditure; not applicable to expenditure estimand | expenditure | pooled | 2.2645 | 2.6342 / * |
| beef and buffalo meat | expenditure; not applicable to expenditure estimand | expenditure | rural | 0.7484 | 0.4124 / None |
| beef and buffalo meat | expenditure; not applicable to expenditure estimand | expenditure | urban | 0.5702 | 0.2256 / None |
| beef and buffalo meat | expenditure; not applicable to expenditure estimand | expenditure | pooled | 0.327 | 0.2555 / None |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | rural | 1.5718 | 1.8277 / *** |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | urban | 0.9439 | 0.7655 / None |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | pooled | 1.1653 | 1.9364 / ** |

Limits: Author says homogeneity and symmetry restrictions could not be estimated and were not imposed. Printed significance marks do not consistently match ordinary two-sided t thresholds; retain marks and t-values without repairing. Zero consumption treatment and unit-value quality correction not established. Original repository PDF requests failed; methods and tables read from author-uploaded public full-text representation. Pooled expenditure estimates are reported, but pooled numeric price table was not recovered; do not average rural/urban price coefficients.

## PAK: PAK-AUJLA-2019

[P1C7-EL-PAK-AUJLA-2019](https://cer.salu.edu.pk/public/wp-content/uploads/2020/03/Demand-Estimates-and-Projections-for-Meat-in-Pakistan-by-the-Year-2030-AD.pdf). Observation period: 2010–2011.  Pakistan HIES households, rural and urban.

Author-reported log-linear SURE. Four meat prices and household monthly income/total expenditure; not a fixed meat-only budget. not explicitly labeled; uncompensated-intent only, model notation unresolved

Sample: table1 households: 16107; table1 rural: 9599; table1 urban: 6508; table3 households: 16082; table3 rural: 9577; table3 urban: 6505; estimation n: null; n note: The source presents both counts without a clear reconciliation or equation-specific N.. Cross-sectional HIES expenditure/quantity data; causal price identification and quality-adjusted unit values not established.

Table 5 explicitly identifies t-values and * at 1%; Table 7 gives parenthetic statistics and marks but no local legend. Preserve as printed; no SE reconstruction.

| Response category | Type and compensation | Price/expenditure variable | Sample | Value | Reported t / mark |
| --- | --- | --- | --- | ---: | --- |
| beef row / beef and buffalo category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | beef and buffalo meat | urban | -0.119 | -1.326 / None |
| mutton row / mutton and goat category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | mutton and goat meat | urban | -0.466 | -5.08 / * |
| chicken | own_price; not explicitly labeled; uncompensated-intent only, model notation unresolved | chicken | urban | -1.022 | -14.454 / * |
| beef row / beef and buffalo category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | beef and buffalo meat | rural | -1.953 | -26.26 / * |
| mutton row / mutton and goat category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | mutton and goat meat | rural | -1.292 | -19.652 / * |
| chicken | own_price; not explicitly labeled; uncompensated-intent only, model notation unresolved | chicken | rural | -0.648 | -11.036 / * |
| beef row / beef and buffalo category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | beef and buffalo meat | pooled | -1.068 | -18.674 / * |
| mutton row / mutton and goat category unresolved | own_price_author_labeled_category_unresolved; not explicitly labeled; uncompensated-intent only, model notation unresolved | mutton and goat meat | pooled | -0.859 | -15.571 / * |
| chicken | own_price; not explicitly labeled; uncompensated-intent only, model notation unresolved | chicken | pooled | -0.807 | -17.759 / * |
| beef row / beef and buffalo category unresolved | expenditure; not applicable to expenditure estimand | expenditure | rural | 0.379 | 19.987 / * |
| beef row / beef and buffalo category unresolved | expenditure; not applicable to expenditure estimand | expenditure | urban | 0.273 | 12.314 / * |
| beef row / beef and buffalo category unresolved | expenditure; not applicable to expenditure estimand | expenditure | pooled | 0.373 | 26.617 / * |
| mutton row / mutton and goat category unresolved | expenditure; not applicable to expenditure estimand | expenditure | rural | 0.262 | 24.411 / * |
| mutton row / mutton and goat category unresolved | expenditure; not applicable to expenditure estimand | expenditure | urban | 0.512 | 31.835 / * |
| mutton row / mutton and goat category unresolved | expenditure; not applicable to expenditure estimand | expenditure | pooled | 0.393 | 43.621 / * |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | rural | 0.39 | 19.991 / * |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | urban | 0.658 | 30.77 / * |
| chicken | expenditure; not applicable to expenditure estimand | expenditure | pooled | 0.563 | 40.194 / * |

Limits: Equation (1) prints Y on the left, though text calls the model log-linear; a literal level-log equation would not make price slopes elasticities. Table 7 species labels are inconsistent: short row labels versus bundled price columns. Table 7 rural -1.712 statistic carries *; exact significance interpretation unresolved. Household HIES consumption omits social events and religious rituals; projection baseline comes from separate official availability figures. Published 2030 projections are not observed demand or new elasticity estimates.

## PAK: PAK-HAYAT-2023

[P1C7-EL-PAK-HAYAT-2023](https://doi.org/10.1016/j.heliyon.2023.e19518). Observation period: 2018–2019.  Pakistan HIES households.

LA/AIDS, SUR/GLS; authors state homogeneity and symmetry imposed. Eight-food-group budget; food expenditure is income proxy, not total household income. Tables 3 and 4 explicitly uncompensated and compensated

Sample: original households: 24809; analysis households: 24620; exclusion: missing quantities/expenditures. Unit values computed as expenditure/quantity; no independent causal price variation established.

Regression SE in Table 2; no elasticity SE, CI or stars in Tables 3–4. Do not transfer regression SE to nonlinear elasticities.

| Response category | Type and compensation | Price/expenditure variable | Sample | Value | Reported t / mark |
| --- | --- | --- | --- | ---: | --- |
| meat aggregate | own_price; Marshallian, conditional on eight-food budget | meat aggregate | pooled/national | -0.12486 | Not supplied / None |
| meat aggregate | own_price; Hicksian, conditional on eight-food budget | meat aggregate | pooled/national | 0.090241 | Not supplied / None |
| meat aggregate | expenditure; not applicable; eight-food budget expenditure elasticity | expenditure | pooled/national | 1.683099 | Not supplied / None |

Limits: Pooled meat cannot identify species-specific own or cross effects. Table 4 meat compensated own-price value is positive; this fails the usual nonpositive compensated own-price restriction at the reported point estimate. Methods contain inequality/terminology inconsistencies; reported labels do not establish demand-system regularity.

## SAU: SAU-ALBALAWI-2016

[P1C7-EL-SAU-ALBALAWI-2016](https://doi.org/10.25904/1912/1672). Observation period: 1985–2010.  Saudi national annual per-capita meat and fish series.

Rotterdam demand system under preference independence, trend constants; DAP2000/DEMMOD-3. Conditional on the four-good meat-and-fish group, with Divisia group quantity/expenditure held fixed for price effects. Hicksian/Slutsky-type conditional elasticities: equation (3.5) divides Slutsky coefficients by conditional budget shares; analyst classification from model, not an invented table label.

Sample: annual levels: 26; annual changes maximum: 25; estimation n: null; data sources: ["Saudi Ministry of Agriculture","Saudi Ministry of Trade and Industry","FAO statistical publications"]. Observational annual price/quantity demand system with model restrictions; no exogenous price instrument established.

Table 6.3 coefficient SE reported; Table 6.4 elasticity SE/CI/significance absent.

| Response category | Type and compensation | Price/expenditure variable | Sample | Value | Reported t / mark |
| --- | --- | --- | --- | ---: | --- |
| beef | own_price; conditional compensated Slutsky/Hicksian-type | beef | national annual 1985–2010 | -0.204 | Not supplied / None |
| chicken | own_price; conditional compensated Slutsky/Hicksian-type | chicken | national annual 1985–2010 | -0.088 | Not supplied / None |
| lamb | own_price; conditional compensated Slutsky/Hicksian-type | lamb | national annual 1985–2010 | -0.103 | Not supplied / None |
| beef | expenditure; not applicable; meat/fish group expenditure elasticity | expenditure | pooled/national | 1.07 | Not supplied / None |
| chicken | expenditure; not applicable; meat/fish group expenditure elasticity | expenditure | pooled/national | 0.48 | Not supplied / None |
| lamb | expenditure; not applicable; meat/fish group expenditure elasticity | expenditure | pooled/national | 1.27 | Not supplied / None |

Limits: Cannot substitute these conditional compensated values for unconditional Marshallian responses. Lamb is not demonstrably adult-sheep mutton or mutton/goat. Only 26 annual levels; historical series and current target differ. Stationarity table marks beef-price changes p=.108 stationary at 11%, a weak threshold, while heading says 5%. Group income-flexibility coefficient -0.215 has SE .298; elasticity significance is not established by signs. Chapter 5 preliminary rough estimates and Chapter 7 import regressions are different estimators/markets and are not pooled with Table 6.4.

## ARE: ARE-BASARIR-2013

[P1C7-EL-ARE-BASARIR-2013](https://www.agrojournal.org/19/01-05.pdf). Observation period: not reported. Survey fieldwork year not stated in the retained article; 2012 receipt/acceptance dates are not survey dates. 500 face-to-face household questionnaires across all seven UAE emirates, allocations by emirate population; weekly purchases and prices.

LA/AIDS with demographics; SUR/maximum likelihood in SAS; fish equation dropped. Six-good meat/fish expenditure shares normalized to unity. Explicit Marshallian Table 2 and Hicksian Table 3

Sample: questionnaires: 500; random selection: author-reported; survey frame and response rate: null. Household purchase unit values and demographics; cluster average prices substituted for missing prices at zero purchases. No exogenous price instrument or full censoring model established.

Tables 2–4 have stars, not SE/CI; * .01, ** .05, *** .10.

| Response category | Type and compensation | Price/expenditure variable | Sample | Value | Reported t / mark |
| --- | --- | --- | --- | ---: | --- |
| beef | own_price; Marshallian, conditional on six-product group | beef | pooled surveyed households across seven emirates; national representativeness unestablished | 0.666 | Not supplied / *** |
| lamb | own_price; Marshallian, conditional on six-product group | lamb | pooled surveyed households across seven emirates; national representativeness unestablished | -0.041 | Not supplied / None |
| goat | own_price; Marshallian, conditional on six-product group | goat | pooled surveyed households across seven emirates; national representativeness unestablished | -0.499 | Not supplied / ** |
| chicken | own_price; Marshallian, conditional on six-product group | chicken | pooled surveyed households across seven emirates; national representativeness unestablished | -0.319 | Not supplied / None |
| beef | own_price; Hicksian, conditional on six-product group | beef | pooled surveyed households across seven emirates; national representativeness unestablished | 0.568 | Not supplied / *** |
| lamb | own_price; Hicksian, conditional on six-product group | lamb | pooled surveyed households across seven emirates; national representativeness unestablished | 0.134 | Not supplied / None |
| goat | own_price; Hicksian, conditional on six-product group | goat | pooled surveyed households across seven emirates; national representativeness unestablished | -0.156 | Not supplied / None |
| chicken | own_price; Hicksian, conditional on six-product group | chicken | pooled surveyed households across seven emirates; national representativeness unestablished | -0.531 | Not supplied / ** |
| beef | expenditure; not applicable; six-product group expenditure elasticity | expenditure | pooled surveyed households across seven emirates; national representativeness unestablished | 0.804 | Not supplied / * |
| lamb | expenditure; not applicable; six-product group expenditure elasticity | expenditure | pooled surveyed households across seven emirates; national representativeness unestablished | 1.012 | Not supplied / * |
| goat | expenditure; not applicable; six-product group expenditure elasticity | expenditure | pooled surveyed households across seven emirates; national representativeness unestablished | 1.179 | Not supplied / * |
| chicken | expenditure; not applicable; six-product group expenditure elasticity | expenditure | pooled surveyed households across seven emirates; national representativeness unestablished | 0.69 | Not supplied / * |

Limits: Positive compensated beef and lamb own-price estimates violate the usual nonpositive own substitution effect. With positive expenditure elasticities, reported Hicksian-minus-Marshallian own effects for beef and chicken are negative, inconsistent with the Slutsky identity and positive shares. Lamb and goat are separate; no demonstrated mapping to requested mutton. Low equation R-squared .089–.237 is reported; national representativeness cannot be established from the sampling description alone. Printed coefficients retained as findings about this publication; no corrected values invented.

## Cross-price evidence and excluded alternatives

The full JSON and CSV preserve every extracted cross-price direction, sample, compensation label and exact table locator. Blank CSV fields mean not supplied or unresolved, never zero. Do not average urban and rural coefficients or mix study systems. No current forecast transport is accepted.

- [P1C7-EL-USDA-ICP](https://www.ers.usda.gov/data-products/international-food-consumption-patterns/documentation): 2005 ICP international system reports broad Meats, not chicken/beef/mutton. The separate 1996 cross-price release is a different vintage. Marginal-utility-constant (Frisch) and real-income-constant elasticities must not be conflated. Reopen when: Obtain a documented species-disaggregated original for the requested country; a broad Meats spreadsheet alone does not reopen a slot.
- [P1C7-EL-PAK-MEMON-2012](https://www.researchgate.net/publication/291833833_AN_EMPIRICAL_ANALYSIS_OF_MEAT_DEMAND_A_CASE_STUDY_OF_PAKISTAN): Indexed author manuscript reports annual published HIES data 2000–2010. Adjacent text labels the price tables inconsistently as Marshallian/Hicksian; expenditure prose swaps chicken/mutton relative to Table 4 headings. No coefficient imported pending original equations and correction. Reopen when: Lawful original with stable table labels, complete definitions, and resolution of chicken/mutton order; do not choose the convenient interpretation.
- [P1C7-EL-SAU-ALMAHISH-2020](https://doi.org/10.36899/JAPS.2020.2.0040): Inverse-demand study models price responses to quantities/scale. Price flexibilities are not ordinary quantity responses to prices; do not take cellwise reciprocals. Reopen when: Full inverse-system Jacobian, expenditure conditioning and valid matrix inversion plus target model justification; or a direct-demand study.
- [P1C7-EL-SAU-KOTB-2026](https://doi.org/10.1007/s44447-026-00172-6): ECM-AIDS annual 1990–2024 study uses red meat, poultry and fish. Red meat does not isolate beef or mutton; poultry is not established as chicken only. Reopen when: Original commodity-code mapping disaggregating requested species and matching own/cross estimands.

## What would permit use

Resolve each study’s stated methodological holds, obtain a versioned baseline with matching species, population, product, geography and price/expenditure definition, and validate current transport. A correctly transcribed historical estimate is insufficient by itself. All twelve slots retain separate reopening triggers in the structured review.
