# Why these scenarios sit below GFI India

**Local review candidate, 27 October 2026. Numerical diagnostics; human factual/code verification pending.**

The retained India 2030 median is $187.8 million, compared with $964.4 million for GFI's low domestic scenario under the existing conditional price conversion. This appendix asks which parts of that disagreement are demonstrated by the equations and which remain hypotheses. No historical headline is replaced. The companion `scripts/gfi_gap.py` writes its results separately in `build/gfi-gap/`.

## Compare the same question first

The comparison is India, domestic spending, 2030. Exports, economic impact and employment are excluded. GFI's source reports rupee amounts for plant-based meat, dairy, eggs and fermentation-derived meat. Its price and retail-valuation bases are unstated. Our retained conversion assumes a common 2022 price basis, inflates to 2025 and converts at the 2025 exchange rate. Dollar comparisons below depend on that assumption. The original rupee amounts remain visible so that an unresolved definition is not hidden by conversion.[^gap-source]

GFI's low/medium/high cases are scenarios; our P10/P50/P90 values are percentiles under chosen parameter distributions. They are not equivalent statistics. Our aggregate intends to include fermentation, but has no separately estimated category-entry amount. The regional AI elicitation excludes fermentation. These distinctions limit both category attribution and comparisons between result families.

## Category decomposition

The table transcribes physical PDF page 4. Each 2030 cell gives the reported value in INR crore and the annual growth implied by its 2022 base over eight years. The price basis is unresolved, so these growth rates are not labelled nominal or real. The source's fermentation dash stays undefined; neither its CAGR nor absolute increase can be calculated from a known base.

| Category | 2022, INR crore | Low 2030: value (growth/year) | Medium 2030: value (growth/year) | High 2030: value (growth/year) |
|---|---:|---:|---:|---:|
| Plant-based meat | 100 | 1,803 (43.55%) | 3,525 (56.10%) | 5,884 (66.42%) |
| Plant-based dairy | 250 | 4,827 (44.78%) | 7,643 (53.34%) | 10,625 (59.79%) |
| Plant-based eggs | 1 | 527 (118.89%) | 989 (136.81%) | 1,416 (147.68%) |
| Fermentation-derived meat | Source dash; undefined | 318 (N/A) | 622 (N/A) | 1,038 (N/A) |
| Overall domestic market | 351 | 7,475 (46.57%) | 12,779 (56.73%) | 18,963 (64.66%) |

All three 2030 category totals reconcile. The known 2022 entries sum to the reported 351 crore, but this does not turn the dash into an observed zero. Eggs' large CAGR reflects its one-crore base: the low-case absolute increase is 526 crore, compared with 4,577 crore for dairy. Absolute changes, full precision and source locators are retained in the [category-growth table](../build/gfi-gap/category-growth.csv) and [source extraction](../data/gfi_categories.csv).

Fermentation is **4.254% of GFI's low-case total**. Subtracting its 318 crore from that target reduces the difference between the conditionally converted GFI low case and our median by **5.283%**. The denominators differ. This arithmetic exercise cannot isolate how much fermentation explains the forecasts' disagreement: our own aggregate already intends to include it, without a category-specific estimate. The [target comparison](../build/gfi-gap/target-comparison.csv) reports both denominators for all three scenarios.

## Which model factors produce the Indian path?

For any one draw, the spending multiple is exactly:

```text
M_India(2030) / A = population_ratio × income_index^elasticity
                   × urban_share_ratio × (1 + extra_growth)^8
```

Here A is the converted 2022 anchor, not a 2025 observation. The following illustration fixes elasticity and extra growth at their parameter midpoints. It is not the median of the simulated totals.

| Factor, 2022 to 2030 | Multiplier | Interpretation |
|---|---:|---|
| Population | 1.069955 | More people at a given spending per person |
| Real income raised to elasticity | 1.968639 | Chosen spending response to the real-income path |
| Urban share | 1.072066 | Proportional urban-share scaling |
| Additional growth | 1.839483 | Eight years of the midpoint extra-growth assumption |
| Product | 4.153832 | $45.286640m anchor becomes $188.113110m |
| GFI reported low/medium/high multiples | 21.296 / 36.407 / 54.026 | Reported 2030 amounts divided by 351 crore |

The retained simulated median is $187.811844 million. A product of marginal factor medians need not recover it. The companion preserves each draw's factors and exact product; additive log factors describe the same arithmetic and do not identify causal contributions. The complete draw file is available in the offline reproduction package, not loaded into the website's interactive data payload.

The fastest sampled draw grows by 33.556509% annually. Evaluating the parameter upper bounds gives an analytical maximum of 33.686486%, or $462.029988 million in 2030. Even that boundary lies below the conditionally converted GFI low case. This is a property of the selected model bounds. It does not establish that GFI is wrong or that our model is calibrated.

## What growth would reaching GFI require?

We solve the same equation backwards, holding each target and the other factors fixed:

```text
d_required(e, T) = [T / (A × population_ratio × income_index^e × urban_ratio)]^(1/8) - 1
```

The target T and anchor A must share the stated price basis. The figure varies income elasticity across the retained bounds. The dot uses midpoint elasticity; the range is assumption sensitivity, not a predictive interval.

![Extra annual growth required to reach GFI: low 29.2-35.7%, medium 38.1-45.1%, high 45.1-52.4%, compared with the retained 17.8% ceiling.](../report/figures/gfi-required-growth.png)

| Target | Required extra growth at midpoint elasticity | Range over elasticity assumptions |
|---|---:|---:|
| Low | 32.38% per year | 29.19-35.65% |
| Medium | 41.56% per year | 38.14-45.05% |
| High | 48.72% per year | 45.13-52.39% |

The current upper extra-growth assumption, 17.832570%, comes from Indian job-advertisement growth. It is not an estimated ceiling on purchases. GFI matching would require changing the assumptions; doing so solely to hit the target would add no independent evidence. The [required-growth grid](../build/gfi-gap/required-growth.csv), [figure data](../report/figures/figure-data.json) and [SVG figure](../report/figures/gfi-required-growth.svg) accompany the calculation.

## Testing the US-derived assumptions separately

US evidence sets an upper elasticity bound and a lower extra-growth bound, as well as providing a descriptive 2025 spending benchmark. A change to the growth floor alone therefore does not remove US influence. The companion consumes the same four uniform draws in the same order for every case; it rescales the growth draw into a new interval rather than clipping negative values to zero.

| Case | India 2030 median, $m | Pakistan 2030 median, $m |
|---|---:|---:|
| Retained baseline | 187.812 | 5.977 |
| Extra-growth floor 0% instead of -2% | 202.214 | 6.504 |
| Elasticity fixed at 1 | 156.034 | 6.566 |
| Both changes | 167.830 | 7.143 |

The zero-floor change raises India's median by 7.668%; it does not approach GFI's low case. Fixing elasticity at 1 lowers India while raising Pakistan, because Pakistan's relative-income multiplier is below one. These are diagnostic alternatives, not empirically estimated South Asian corrections. The full grid, all years, both countries and distribution summaries are in [sensitivity-summary.csv](../build/gfi-gap/sensitivity-summary.csv).

The retained overlap sensitivity lowers India's 2030 median from $187.8 million to $119.6 million, widening the same-year GFI discrepancy. Its 2035 median also falls, from $448 million to $215 million. Pakistan's existing urban/animal omission and industry-factor sensitivities are reproduced. Its industry bounds use incomplete directory and vacancy measures; the lower directory bound includes only two Pakistan records. No national Pakistan sales series fits or validates the transfer. Explaining India's disagreement with GFI cannot resolve that separate evidential gap.

## Four questions raised by the comparison

**Are older data responsible?** The GFI summary uses a 2022 baseline/context, but its exact publication and model-development dates are unresolved. Dated 2021-22 US releases contain both upbeat sector messaging and evidence of slowing growth. They establish context, not why Deloitte selected particular assumptions. The bounded [dated-source review](dated-context.md) therefore leaves the causal explanation untested.

**Does GFI include factors our model lacks?** Its methodology explicitly discusses socioeconomic-group penetration, adoption, replacement, relative conventional/plant-based prices, taste and price parity, supply-chain localization, R&D and talent investment. Page 2 attributes scenario construction to GFI's target-market research and Deloitte's proprietary market-sizing, with expert interviews informing taste/price parity. Our aggregate model has no separately identified price-parity or category-entry term. Residual growth may implicitly reflect some of these mechanisms; their individual contributions cannot be recovered from the equation. This is a documented difference in representation, not an additive attribution of the numerical gap.[^gap-source]

**Is projection from the US inappropriate?** Our starting market estimate is Indian, while two parameter bounds use US evidence. The paired tests above show their numerical influence separately. The original US panel's politics/health/R&D themes remain reviewer-supplied prompts for the [country-specific driver comparison](drivers.md), pending verified provenance of that study. A US trend cannot establish the same mechanism or effect size in India or Pakistan.

**What else could matter?** Source price/retail bases, observation years, product/channel scope, scenario definitions, chosen parameter distributions and proxy validity remain material. GFI supplies our baseline and appeared with forward estimates in the regional elicitation packets. Neither matching GFI nor agreement with those responses is independent validation. GFI's public summary does not disclose sufficient detailed proprietary parameters to calculate a definitive causal decomposition.

## Reproduction and review boundaries

From the offline package, run `python scripts/reproduce.py` and `python scripts/gfi_gap.py`, followed by the unit suite. The numerical companion reproduces 55 overlapping values at the original six-decimal precision; the retained engine still reproduces all 127 reference rows byte for byte. Its new output files are separate. Tests cover source missingness, category reconciliation, hand-calculable growth examples, target inversion, exact draw factors, paired random-number ordering, monotonic floor changes, bounds and deterministic repeatability.

These checks establish implementation consistency. Source-specific human factual/code review, scientific acceptance and rights decisions remain pending. Results may be inspected locally without implying that a release or joint-report inclusion has been approved.

[^gap-source]: GFI India and Deloitte India, [*Smart Protein Economic Analysis*](https://gfi-india.org/wp-content/uploads/2024/06/GFI-India-economic-analysis.pdf), physical PDF page 1 (Methodology), page 2 (scenario explanation), and page 4 (domestic table). The 2022 context and original reported values are retained; the URL upload path is not treated as a publication date.
