# Household demand model protocol

Version 1.1.0, registered 2026-10-18T17:38:19Z and amended 2026-10-18T17:43:56Z (amendment 1, before any estimate) on branch `codex/household-demand-20261018`. This file renders `protocol.json`; the JSON is the registered record and `logs/registration-receipt.json` holds its SHA-256. No estimate existed on the branch before this registration.

Seed `20261018` for every Monte Carlo and bootstrap. Headline unit: million USD, 2025 prices, years 2026, 2030 and 2035, India and Pakistan, with the USA as the comparison and calibration market.

## Decision record

Copied verbatim from the plan's Decision record (`OUTPUTS/Sentient Futures/2026-10-18-household-demand-model-plan.md`, SHA-256 `7be5491f5d8ea080685a84721ec6453f2fbd1a5723082edef3a179f8749f7495`). Numbers refer to the design-review questions. Controller rulings R1 to R14 apply.

| # | Decision |
| --- | --- |
| 1 | Standalone reproducible model and paper; the D1 table is one output. |
| 2 | Headline: retail value, US dollars, constant 2025 prices, market exchange rates. Also report volume (tonnes) and share of household protein spending. The model works in shares. |
| 3 | Household model covers plant-based meat and dairy alternatives. Egg and fermentation products are carried from the proxy as a labelled residual so totals match GFI scope. |
| 4 | Report beside the GFI-anchored proxy and discuss the gap. |
| 5, 31 | The US is the comparison and calibration market: BLS Consumer Expenditure Survey microdata plus GFI/SPINS 2025 retail sales of $7.9 billion. Nothing in the US is invented. |
| 6, 30 | Code lives in the public library at `sentient-futures-research/research/household-demand/`. `future-research/` stays the supply benchmark; its AGENTS.md role is unchanged. |
| 7, 20 | One price snapshot of public product pages, collected once: India Delhi NCR, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, one tier-2 city; Pakistan Karachi, Lahore, Islamabad. Price per kg product and per kg protein. |
| 8 | Validation: leave-one-state-out holdout is primary. A time comparison against HCES 2011-12 and 2022-23 is secondary, after the author registers at microdata.gov.in. |
| 9 | Vegetarian households are calibrated to NFHS-5 never-eat rates by state, religion and caste, after the author registers with the DHS Program. Until then, a 7-day zero-purchase rule runs as a labelled diagnostic. |
| 10, 22, 26, 32, 38 | Elicitation uses Claude Opus 5.5 and GPT Astra (`gpt-6-astra`) only, with tools already on this machine. No paid gateway. |
| 11 | Drivers: IMF and UN official projections with low, mid and high bands, plus an AI cost-decline path and a price-parity scenario. |
| 12 | Acceptance: protocol registered before any estimate; Codex recomputes every number; the team agrees the method before D1; human scholarly review stays pending. |
| 13 | Intent-to-purchase conversion from the US, adjusted by each country's price gap through measured price elasticity. |
| 14 | Adoption over time: Bass diffusion fitted to South Asian analog products fixed in the protocol; the US plant-based sales path is a stress test. |
| 15 | Soya chunks (HCES item 152) are an analog for price, diffusion and substitution, excluded from the market figure. |
| 16 | Plant-based meat substitutes for chicken in meat-eating households and competes with paneer, soya chunks and pulses in vegetarian households. Dairy alternatives substitute for liquid milk. Cross-price elasticities come from the microdata. |
| 17 | Halal certification is assumed met for any product sold in Pakistan. No scenario switch. |
| 18 | Design-based variance where strata are resolved; PSU-clustered bootstrap elsewhere, flagged. |
| 19, 24 | India runs on real HCES microdata labelled diagnostic until baseline acceptance. Invented values only where data are absent: Pakistan unresolved strata and plant-based prices before the snapshot. |
| 21 | Publish summarised prices or publicly available data only; respect robots.txt; raw page captures stay local. |
| 23 | One joint Monte Carlo over elasticities, conversion, diffusion and driver bands; Sobol first-order and total indices. |
| 25 | Invented values carry a `SYNTHETIC` flag, live in their own folder, and a CI check blocks them from the claim ledger, reports and D1. |
| 27, 37 | Run Anna's exact US questionnaire on the same two models as a labelled calibration; tell Anna before reporting it. |
| 29 | Chicken prices come from HCES and HIES unit values by state or province. The scraped chicken rows are not used. |
| 33 | Questionnaire asks for both the headline forecast and model inputs; compare the panel headline with the model computed from panel inputs. |
| 34 | India and Pakistan headline questions are marked unresolvable now, plus resolvable proxy questions: Comtrade HS 210610 imports, snapshot product counts, a republished GFI India estimate. |
| 35 | Replace the cultivated and fermentation category question with a plant-based meat versus dairy-alternative split, plus a yes/no question on the year of first approved cultivated-meat sale (FSSAI; Pakistan equivalent). |
| 36 | Each country gets a public evidence pack shaped like the US one, excluding this project's own estimates. |
| 39 | 10 fresh-context runs per model per region; report the median and the 10th to 90th percentile spread across runs. |
| 40 | Web search allowed; sources logged; runs citing `github.com/Omarzaf`, `pakistan-india-protein.vercel.app` or `cultivated-chicken-halal.vercel.app` are discarded and rerun. |

Rulings added after the first registration:

- R12: intent_share is the top-two box (4 or 5 on the 5-point scale) for USA and India.
- R13: Pakistan CONDITIONAL_TRANSFER intent is drawn uniformly between 0.329 (USA) and 0.628 (India), the two observed values from the same instrument.
- R14: outputs/README.md accepted; Bass prior via a citing paper accepted with its note; workspace-state drift expected until Task 12.

## Status flags and the guard

- Flags: `DIAGNOSTIC`, the placeholder flag, `ACCEPTED` and `CONDITIONAL_TRANSFER`.
- Placeholder inputs live in `synthetic/`; artifacts built from them go to `synthetic/outputs/` or outside the repository (ruling R1).
- `python3 research/household-demand/synthetic.py --check` scans `research/india-pakistan/data/claims.csv`, `research/india-pakistan/joint-report`, `research/india-pakistan/report` and `research/household-demand/outputs`. The placeholder flag as a whole uppercase word on any line of a text file is a hit. A missing surface fails. CI runs the guard on every push.

## Diffusion analogs

Task 7 gathers each candidate series with source, locator and years. A candidate with no public annual series of at least 5 points is dropped and recorded with the reason (ruling R8).

| Analog | Countries | Role | Series needed | Source status |
| --- | --- | --- | --- | --- |
| packaged liquid milk | India, Pakistan | diffusion analog for dairy alternatives | annual packaged (pouch, UHT or carton) liquid milk volume or household penetration, national, at least 5 consecutive years | candidate_unverified: India: annual reports of national dairy cooperatives and listed dairies, or NDDB statistics, if they split packaged from loose milk; Pakistan: annual reports of listed UHT milk processors, or Pakistan Economic Survey dairy tables, if they split packaged from loose milk |
| soya chunks (HCES item 152) | India | analog for price, diffusion and substitution; excluded from the market figure (decision 15) | per capita quantity and share of households reporting purchase, by NSS consumption round | candidate_unverified: NSS 68th round 2011-12, HCES 2022-23 and HCES 2023-24 item 152 aggregates (2011-12 and 2022-23 need the author's microdata.gov.in registration) |
| branded ready-to-cook chicken | India, Pakistan | diffusion analog for plant-based meat | annual branded ready-to-cook or processed chicken sales value or volume, national, at least 5 consecutive years | candidate_unverified: India: annual reports of listed poultry processors with a processed or ready-to-cook segment; Pakistan: public filings or trade statistics for branded frozen chicken, if any exist |

US stress test: GFI US plant-based retail sales (SPINS), 2018 to 2025. Anchor 2025: 7.9 billion USD (GFI/SPINS). The US path is a sensitivity row only; main results use the analog diffusion.

## Priors

- Fallback Bass prior, used only if no analog survives for a country: p 0.03, q 0.38. Source: Sultan, Farley and Lehmann (1990), A Meta-Analysis of Applications of Diffusion Models, Journal of Marketing Research 27(1), 70 to 77. Citation verified 18 October 2026. p and q confirmed through a citing paper; the original article's tables were not reached.
- Bass launch years: India 2019 (first national plant-based meat retail launches) and Pakistan 2023. Both are assumptions; no source was found.
- Halal certification is assumed met for any product sold in Pakistan (decision 17).

## Intent sources

Primary: Bryant, C., Szejda, K., Parekh, N., Deshpande, V. and Tse, B. (2019). A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China. Frontiers in Sustainable Food Systems 3, article 11. DOI 10.3389/fsufs.2019.00011, published 2019-02-27, accessed 2026-10-18T17:35:44Z. Corrigendum 10.3389/fsufs.2020.00086: Corrects the spelling of Deshpande and the clean meat purchase-likelihood figures. No plant-based meat figure changes.

- Instrument: One online questionnaire, CINT panel. Purchase likelihood on a 5-point Likert scale from 1 (not at all likely) to 5 (extremely likely). Locator: Materials and Methods, Materials.
- Sample: 3,030 in total; USA 987, India 1,024, China 1,019 (Materials and Methods, Participants). India sample disproportionately urban, high income and well educated (Abstract).

| Plant-based meat purchase likelihood | USA | India | Locator |
| --- | --- | --- | --- |
| Very or extremely likely (4 or 5) | 32.9% | 62.8% | Results, Descriptive Statistics, Acceptance, second paragraph |
| Slightly, somewhat or moderately likely | 41.8% | 31.7% | same |
| Not at all likely | 25.3% | 5.5% | same |
| Mean on 1 to 5 (SD) | 2.78 (1.40) | 3.73 (1.19) | Table 1, ANOVA results showing omnibus results and pairwise comparisons, row Likelihood of purchasing plant-based meat |

- Intent share (R12): Share answering 4 or 5 (very or extremely likely) to plant-based meat purchase likelihood. USA 0.329, India 0.628.
- Missing: India urban meat-eater subset (not reported in the article), fieldwork dates (not checked), dairy-alternative intent (not covered).
- Pakistan: no country intent value. Missing. Treatment `CONDITIONAL_TRANSFER`: the intent range spanned by the USA and India values is transferred, and the Pakistan household-model result is a scenario that never enters claims as a headline (ruling R9). Distribution (R13): uniform between 0.329 (USA) and 0.628 (India), the two observed top-two-box values from the same instrument.

## US calibration

- `conversion = min(1, penetration / addressable_share) / intent_share`
- `spend_per_adopter_usd = sales_usd / (us_households * penetration)`
- `addressable_share` defaults to 1.0. All US buyers sit in the addressable segment (ruling R7). Overstates conversion if buyers sit outside it.
- Addressable rule, shared by the USA, India and Pakistan: urban, buys meat, buys prepared or packaged food (Task 5), applied to the US, India and Pakistan alike.
- Inputs: BLS CE public-use microdata (after author approval), GFI/SPINS 2025 retail sales 7.9e9 USD, GFI 2025 US household penetration (captured in Task 6 with locator), intent_sources.primary USA intent share.

## Household tables

- India MPCE: HCES 2023-24 monthly per capita consumption expenditure, mpce_inr; mpce_local = mpce_inr; currency INR.
- Pakistan MPCE: Total monthly household consumption expenditure from HIES 2024-25 divided by household size: use the PBS household total if a file holds it, else sum the consumption sections; document the source. mpce_pkr; mpce_local = mpce_pkr; currency PKR (ruling R4).
- Clusters: psu (India: FSU identifier from level_01; Pakistan: prcode), stratum and stratum_status; India always RESOLVED (ruling R2).
- Pakistan geography: state = province code, sector = region (1 rural, 2 urban); province and region kept (ruling R3).

## Metrics

- Simulation: 10,000 draws; quantiles `p10`, `p50`, `p90` of `value_usd_2025`, `volume_t` and `share`; FAOSTAT supply ceiling with `ceiling_binding_share`. Main diffusion `analog`, sensitivity `us_stress`.
- Sensitivity: Saltelli 2010 estimators, Sobol `first_order` and `total` indices.
- Validation, primary: leave-one-state-out holdout in India. Outcome: weighted per capita monthly spending on animal protein by state.
  - `mae`: mean absolute error across held-out states.
  - `median_ape`: median absolute percentage error across held-out states.
  - `coverage_80`: share of states whose observed value falls inside the predicted 10th to 90th percentile.
- Validation, secondary: time comparison against HCES 2011-12 and 2022-23 after the author registers at microdata.gov.in.
- Elicitation: `claude-opus-5-5` and `gpt-6-astra`, 10 runs per model per region; median and 10th to 90th percentile spread across runs. Runs citing `github.com/Omarzaf`, `pakistan-india-protein.vercel.app`, `cultivated-chicken-halal.vercel.app` are discarded and rerun.
- Comparison methods per country and year: `household_model`, `gfi_proxy`, `panel_headline`, `model_from_panel_inputs`.
