# Market-source review

This is source collection and an eligibility audit. No new market size or projection is computed. Human scholarly review remains pending.

From the repository root, rebuild the available evidence tables with:

```sh
node research/protein-markets-2026/market/build-evidence.mjs PRIVATE_MARKET_DATA_DIR OUTPUT_DIR
node research/protein-markets-2026/market/test-evidence.mjs
```

The private market directory contains the three capture receipts and their unchanged `raw/` files. The builder checks every capture hash before writing source, published-context, import-context and reconciliation CSVs. It performs no network retrieval. Reconciliation cells remain null. Its successful exit verifies this evidence inventory, not a market estimate.

## Published estimates

The [Ipsos–PBFIA original report](https://www.ipsos.com/sites/default/files/ct/publication/documents/2025-03/Ipsos_PBFIA_Plant%20based%20foods%20report%202025.pdf) reports an Indian plant-based market estimate for an earlier year. Its glossary excludes soya chunks and chaap while including some protein bars and snacks. The source does not establish Anna-compatible current sales. The [earlier GFI India–Deloitte analysis](https://gfi-india.org/wp-content/uploads/2022/10/gfi_economic_analysis.pdf) separately reports historical domestic estimates, growth scenarios, exports and economic impact. The two series must not be spliced. Published growth cases are not calibrated forecast quantiles.

The inspected Pakistan public report offers describe purchasable studies. Their catalogue pages do not expose sufficient underlying methods and observations for an auditable current pillar estimate. No purchase, sample request or contact was made. This is a limitation of the inspected evidence, not proof that no suitable estimate exists.

## Company records

A product listing is evidence of a listing; development and funding announcements are evidence of those announcements. Neither establishes annual sales. The inspected [MyoWorks page](https://myoworks.in/) describes ancillary inputs for other cultivated-meat producers. The [Laurus Bio review](https://www.lauruslabs.com/AR_FY25-26/business-review.html) spans multiple biotechnology applications. These inputs and diversified segment revenues cannot fill a finished-consumer-food numerator. ClearMeat and Biokraft company claims likewise require separate product authorisation, actual sales, geographic allocation and channel evidence. The inspected set is not a census of firms.

## Trade reconciliation

The [UN public preview documentation](https://uncomtrade.org/docs/un-comtrade-api/) supplies the retrieval route. The Pakistan response preserves its aggregate and `isReported=false` flags. The India annual query returned no rows after the recorded failures; absence in that response is not zero imports. The captured [Pakistan tariff edition](https://download1.fbr.gov.pk/Docs/20258111683941732Tariff-2025-26.pdf) confirms broad protein-substance descriptions. It is used for classification scope, not current duty advice.

HS 2106.10 and 3504.00 do not partition finished alternative foods by plant, fermentation or cultivation. They also do not establish retail margins, domestic production, exports, inventories, food/nonfood end-use or household expenditure. These are upstream context records. No trade-to-market multiplier, pillar allocation or three-method average is applied. The twofold-disagreement test remains unassessed while comparable values are absent.

## Additional survey check

The [Pakistan DHS questionnaire](https://microdata.worldbank.org/catalog/3411/download/46312), questions 649–650, asks about the youngest child's previous-day food. That outcome cannot replace NFHS adult weekly food frequency. The [National Nutrition Survey original report](https://www.unicef.org/pakistan/media/2826/file/National%20Nutrition%20Survey%202018%20Volume%201.pdf), section 6.4, measures women's previous-day dietary diversity; section 2.3.1.1 mentions household religion. It is a candidate for a differently defined analysis, with unit-level access and caste comparability unresolved. Neither report inspection produces the requested variance decomposition or confidence intervals.

## AI and diffusion-model evidence

The primary [extrusion comparison](https://doi.org/10.1016/j.crfs.2025.101157) studies pilot processing outside the two target countries. The [Tufts media programme](https://sites.tufts.edu/usdacellag/program-overview/economical-media/) is technical research context. The [NSF fermentation project](https://nsf.elsevierpure.com/en/projects/ai-designed-microbial-strains-for-efficient-food-protein-producti-3/) describes project objectives. These sources motivate proposed technical tests; they do not establish local adoption or realised commercial savings.

The inspected Lens public HTML does not contain a verified classification result set. Its [API policy](https://support.lens.org/knowledge-base/lens-patent-and-scholar-api/) requires personal account approval and a token. No account or request was made. A future A23J/G06N intersection must distinguish classifications from keywords, record classification versions, deduplicate families and specify country assignment and publication lags. Even a correct count would measure documented invention activity, not the causal market effect of AI.

No Bass or reference-class model is fitted. The reproduction gate forbids projections; a compatible analogue series is also unestablished. The attempted official Pakistan dairy-company report returned an access denial. Aggregate company revenue would need stable category definitions, volumes/adopters, price deflation, exposure and an adoption denominator before it could support a diffusion fit. This single failure does not establish that all analogue data are unavailable.
