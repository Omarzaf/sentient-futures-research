# Methods appendix: India–Pakistan spending scenarios

**AI-assisted review draft, 27 October 2026. Human factual/code verification pending. Proposed joint-report methods contribution; definitions are proposed harmonization, not a recorded team agreement.**

## Read this first: the calculation in plain language

We ask how domestic spending on alternative-protein foods might develop in India and Pakistan in 2026, 2030 and 2035. We do not measure national adoption or predict how much conventional meat will be replaced. The following steps explain the retained model; the exact equations below are unchanged.

1. **Start with India.** GFI India/Deloitte estimates a 2022 market of INR 351 crore for plant-based meat, dairy and eggs. We assume a 2022 price basis and retail valuation, then convert it to 2025-price dollars: about $45.3 million. These interpretations are assumptions because the source does not specify them.
2. **Carry spending per person forward.** Income growth and urbanisation raise or lower the path. An additional annual growth term represents other changes imperfectly; its bounds come from a US sales decline and Indian vacancy growth. These are chosen proxies, not relationships fitted to purchases.
3. **Construct Pakistan's conditional path.** There is no equivalent verified national sales anchor in the retained evidence. We transfer India's per-person path using relative income, urban share, animal-protein supply and industry-activity proxies, then multiply by Pakistan's population. This adds uncertainty and does not establish observed Pakistani sales.
4. **Repeat under different assumptions.** The model draws four parameters 10,000 times. Each draw is reused across countries and years. The lower, middle and upper values are the 10th, 50th and 90th percentiles of those calculations; they are not calibrated probabilities of future sales.
5. **Change assumptions deliberately.** Retained sensitivities test overlapping income/industry growth and Pakistan multipliers. The new GFI companion also changes the US-derived growth floor and elasticity assumptions separately and calculates the extra growth required to reach GFI's targets. It leaves the historical reference results unchanged.
6. **Interpret the limits.** GFI's domestic scenarios, our assumption percentiles and repeated AI responses are different objects. Shared GFI inputs prevent treating their agreement as independent confirmation. The main empirical need is comparable sales and repeat-purchase evidence, especially for Pakistan.

For the numerical comparison, see [Why these scenarios sit below GFI India](gfi-gap.md). [Drivers and proposed tests](drivers.md) explain the mechanisms that the aggregate equation cannot identify separately.

## 1. Question, estimand and evidence classes

The calculation explores domestic alternative-protein spending in India and Pakistan in 2026, 2030 and 2035. Its intended scope is plant-based replacement foods and fermentation-derived human foods, excluding cultivated meat. The 2022 Indian anchor contains plant-based meat, dairy and eggs; the source's forward domestic categories include fermentation-derived meat. The model carries one aggregate forward and does not separately estimate entry of every proposed product category. Its interpretation must retain that limitation.

The proposed valuation is retail spending in market-exchange-rate US dollars at constant 2025 prices. **Retail valuation and the Indian source's nominal-2022 price basis are assumptions.** They are not explicit properties established by the original GFI/Deloitte summary. US coverage is broader and includes prepared meals. These differences prevent a fully matched cross-country market comparison.

Observed macro quantities, published external market estimates, analyst scenarios, model-elicited projections and missing evidence are recorded as different classes. The proxy scenarios estimate neither adoption probabilities nor physical protein volumes. FAOSTAT supply is an input proxy, not household consumption or alternative-protein demand. No model output is converted into an observed baseline.

The model was not fitted to a time series of alternative-protein purchases, and its future outcomes are unresolved. Calibration, predictive accuracy and probability coverage have not been demonstrated. Country-specific inference is limited to India and Pakistan.

## 2. Source selection and numerical inputs

The retained model reads **106 input rows** in `data/altprotein_proxy_inputs.csv`. Each row has an input ID, country/year, quantity, unit, source ID, tier, raw locator, capture reference/hash where available, and notes. The source collection is purposive; it was not a preregistered systematic review. Existing acquisition logs record unsuccessful and incomplete retrieval separately. Source dates and collection dates must not be conflated.

| Input family | Source/vintage and retained use | Main limitation |
|---|---|---|
| Indian market anchor and external scenarios | GFI India/Deloitte, 2022-context analysis, final-page domestic table: 351 crore in 2022; 2030 low/medium/high 7,475/12,779/18,963 crore | Published model estimates; price/valuation basis unstated; 2030 scenarios are not observations or probability bounds. |
| US sales benchmark | GFI/SPINS 2025 plant-based retail sales, $7.9B; reported annual dollar change −2% | Broad US categories; nominal annual sales change is repurposed as a real non-income drift bound by assumption. |
| Population, GDP growth, inflation | IMF WEO October 2026: LP, NGDP_RPCH, PCPIPCH | Mixed historical estimates/outturns and projections; published horizon ends in 2031. |
| Urban share | WDI SP.URB.TOTL.IN.ZS, 2015–2025 | National urban definitions differ; future trend is extrapolated. |
| Exchange rate and income levels | WDI PA.NUS.FCRF; NY.GDP.PCAP.CN/CD | Market exchange rates, not PPP; observation years differ in the US–India elasticity construction. |
| Animal-protein supply | FAOSTAT 2023 protein supply, seven animal-food groups | Supply balance, not individual intake, willingness or replacement-product demand. |
| Industry activity | AltProtein.Jobs directory described as 2024 and annual vacancies 2023–2025 | Job-board coverage and country assignment are imperfect; directory records may overlap; not employment or skill shortages. |

The source ledger and source-specific rights should accompany extracted facts. Reproduction from the numeric input CSV does not require redistributing source workbooks, full PDFs, cached web pages or private team documents.

## 3. Exact implemented transformations

Notation: country `c` is India `I` or Pakistan `P`; year is `t`; `P_c(t)` denotes population **in millions**, `U_c(t)` urban share **in percent**, `I_c(t)` real GDP per person relative to 2022, `s_c(t)` annual dollars per person, and `M_c(t)` total spending **in million dollars**. Percentage units cancel in urban-share ratios.

### 3.1 Price conversion and anchors

Let `F = (1 + 5.4/100)(1 + 4.6/100)(1 + 2.0/100)`, using Indian consumer-price inflation in 2023–2025. Let `X = 87.158448` INR per USD, the retained rounded WDI 2025 period-average exchange rate.

```text
Indian anchor A = 351 × 10 × F / X = 45.286640 million USD at 2025 prices
s_I(2022) = A / P_I(2022) = 0.031771 USD per person
s_US(2025) = 7.9 × 1,000 / P_US(2025) = 23.106847 USD per person
```

The factor 10 converts crore rupees to million rupees. The US 2025 dollars already use the selected price year. The Indian anchor is **a 2022 observation-year estimate converted to 2025 prices**, not a 2025 market observation.

### 3.2 Population and real-income paths

The retained IMF population series is used through 2031. Beyond it:

```text
P_c(t) = P_c(2031) × [P_c(2031)/P_c(2030)]^(t−2031), for t > 2031
I_c(2022) = 1
I_c(t) = product over y=2023…t of [(1 + g_c(min(y,2031))/100)
                                      / (P_c(y)/P_c(y−1))]
```

Here `g` is real GDP growth. Holding the 2031 GDP and population growth rates through 2035 is an analyst extrapolation, not an additional IMF forecast. Retained 2035 income indices are 2.167826 for India and 1.254629 for Pakistan.

For each country, ordinary least squares on the eleven annual urban-share observations from 2015 through 2025 supplies a slope `b_c`. Future urban share is `U_c(2025) + b_c(t−2025)`. The function uses observed values through 2025. No estimated uncertainty or cross-country harmonization is added. Retained 2035 shares are 38.831347% and 43.289498%.

### 3.3 Parameter bounds

Four parameters are independently sampled from uniform distributions once per draw. The **same sampled parameters are reused across years and countries** within that draw; country/year results are therefore related, not independent samples.

| Parameter | Distribution/bounds | Construction and interpretation |
|---|---|---|
| Income elasticity `e` | Uniform(1, 1.810389…) | Lower bound assumes proportional income scaling. Upper bound attributes the entire US–India per-person spending gap to the market-dollar income gap. It is not an estimated causal elasticity. |
| Additional annual drift `d` | Uniform(−0.02, 0.17832570…) | Lower bound is US 2025 nominal retail dollar decline; upper bound is `(529/381)^(1/2)−1`, Indian vacancy CAGR for 2023–2025. Mapping these into future spending is an assumption. |
| Animal-supply weight `w` | Uniform(0,1) | Applies none to all of Pakistan's animal-supply ratio multiplicatively. |
| Pakistan industry factor `k` | Uniform(0.102303…,0.667385…) | Bounds are Pakistan/India directory-row density and vacancy density, both divided by 2025 population. |

The full-precision values are computed by the retained code from inputs, not from the rounded bounds above. Directory counts are 119 for India and 2 for Pakistan. 2025 vacancies are 529 and 58. Neither defines a complete national industry census.

For the upper elasticity bound, India's 2022 GDP per person in local currency is inflated by `F` and divided by `X`. US 2025 GDP per person is already in market dollars at 2025 prices. Then:

```text
e_max = log[s_US(2025)/s_I(2022)]
        / log[GDPpc_US(2025)/(GDPpc_I(2022, INR) × F/X)]
```

The retained spending and income ratios are 727.301293 and 38.081810. They have a common price basis but different observation years. A same-price-basis conversion does not make them a matched contemporaneous comparison. Urbanisation, tastes, availability, category coverage and measurement also contribute to the observed gap; attributing it entirely to income is only a bounding assumption.

### 3.4 India and Pakistan equations

```text
s_I(t) = s_I(2022) × I_I(t)^e × [U_I(t)/U_I(2022)] × (1+d)^(t−2022)

R_income(t) = [GDPpc_P(2025)/GDPpc_I(2025)]
              × [I_P(t)/I_P(2025)] / [I_I(t)/I_I(2025)]

s_P(t) = s_I(t) × R_income(t)^e × [U_P(t)/U_I(t)] × R_animal^w × k

M_c(t) = s_c(t) × P_c(t)
US comparison percentage_c(t) = 100 × s_c(t)/s_US(2025)
```

The 2025 Pakistan/India income ratio is 0.590535. `R_animal = 31.52/19.67 = 1.602440…`, from the sum of bovine meat, eggs, fish/seafood, milk excluding butter, mutton/goat, pigmeat and poultry protein supply. The industry and dietary multipliers are not independently identified effects. Their multiplication may double-count correlated conditions.

No Pakistan retail observation is used to fit or validate the transfer equation. Missing baseline evidence is never assigned a zero. No separate AI or policy multiplier is applied. No cultivated-meat entry term is present.

## 4. Draws, aggregation and output

The implementation uses Python's standard-library pseudorandom generator, `random.Random(20261015)`, and 10,000 draws. Every iteration draws `e`, `d`, `w`, `k` in that order. Results for each country/year are sorted. For quantile fraction `q`, compute `h=(n−1)q`, `i=floor(h)`, `j=ceil(h)`, and return `x[i]+(x[j]−x[i])(h−i)` with zero-based indexing. Output CSV values are formatted to six decimal places.

The main table reports q=.1, .5 and .9. They describe variation under chosen parameter distributions. They are **not** confidence bounds, a calibrated 80% predictive interval, or empirical household uncertainty. Display rounding must not imply greater accuracy. The chapter uses $448m and $11.8m for the retained 2035 medians 447.504341 and 11.759263.

## 5. Retained sensitivities and external benchmark

Sensitivities reset the same seed, retaining paired draws. Even a fixed or unused parameter is drawn before being replaced; this preserves pairing.

1. **Income/drift overlap:** annual real income growth from 2023 to 2025 is 6.548202%. The alternative upper drift is `d_max − income_growth × e_max = 5.977774%`; the lower bound stays −2%. India's 2035 p10/p50/p90 become 134.658168 / 215.060659 / 341.253412 million; Pakistan's become 2.382182 / 5.964900 / 11.690860 million. This is a sensitivity, not a fitted correction.
2. **Pakistan overlap:** set its relative urban share and animal-supply multipliers to 1 while retaining India's path, income ratio and industry factor. Pakistan's 2035 p10/p50/p90 become 2.575709 / 8.318219 / 25.341349 million.
3. **One parameter fixed:** hold each parameter at its lower and upper bound while drawing the others. India's 2035 median ranges are 332.438965–622.332639 million for elasticity and 127.357046–1398.084812 for drift. Pakistan's corresponding pairs are 12.293369 / 11.255477 for elasticity, 3.652403 / 40.094912 for drift, 9.273218 / 14.859778 for animal weight, and 3.468582 / 22.627744 for industry factor. These are pairs of conditional medians, not uncertainty intervals or variance decompositions. Higher elasticity need not increase Pakistan's transfer estimate because its relative income factor is below one.

The existing comparison converts GFI India's 2030 external scenarios using the **same 2022-to-2025 inflation and exchange-rate transformation** as the anchor, yielding 964.437694 / 1648.769136 / 2446.639731 million. This assumes the external scenarios share that source price base; the summary does not establish it. The fact that all retained proxy draws fall below GFI's low case is a conditional disagreement, not a validation test or proof of which forecast is correct. Preserve source rupee values alongside any converted comparison until the price basis is resolved.

## 6. Behaviour, policy and talent evidence

Behavioural evidence is read for the actual question and sampled population. Stated willingness, paid first purchase, unsubsidized repeat purchase and animal-food displacement are separate outcomes. The selective nine-study extraction package has no India finding and is not a systematic review of national adoption; the bilateral discussion draws on additional studies. Do not turn “not measured in these sources” into “does not occur.”

Policy sources establish the dated instrument or announcement and its stated jurisdiction. Implementation, disbursement, product authorization and uptake need different evidence. Halal status and food authorization are distinct questions. This appendix does not provide a legal determination or assume a product's certification from general institutional powers.

Talent evidence separates job-board advertisements, directory entries, sampled employer testimony and national workforce measures. GFI India's study's 20 industry responses and 19 academic participants are study cohorts. Its findings may motivate a pilot; they do not identify a nationally optimal training portfolio. Recommendations in the chapter are author proposals that require baseline and outcome checks.

## 7. Validation, reproducibility and remaining holds

Run `python scripts/reproduce.py` from the package root. The packaged engine `scripts/build_altprotein_proxy.py` reads the 106 aggregate input rows and writes `build/proxy_scenarios.csv`. Its private acquisition/transcription mode has been removed; the mathematical engine, random draw order and output format are preserved. No source acquisition or model call is required.

The 22 October package verification regenerated all 127 rows byte for byte against `data/reference_proxy_scenarios.csv`. Independent denominator and sensitivity checks are included in `tests/test_reproduction.py`. Clean-folder verification is recorded in the release receipt. Reproduction establishes consistency with the specified assumptions, not empirical validity.

Human reviewers must resolve the Indian price/retail basis, judge the crosswalk and proxy assumptions, verify included sources/data/code, and sign off the final claims. A new national sales series should be documented as new evidence and evaluated explicitly rather than silently replacing the original anchor. The separate supply benchmark's out-of-sample performance does not validate alternative-protein spending. Full source/capture pointers and rights limits are in [claim map](../provenance/claims.md) and [source ledger](../provenance/sources.md).
