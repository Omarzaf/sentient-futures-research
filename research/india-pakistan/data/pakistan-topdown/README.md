# Pakistan top-down value-scale companion

This is an independent conditional diagnostic for the 30 October writing kit. It does not change the original spending model or its 127 reference rows, estimate adoption, predict displacement, or establish national retail sales. No animal translation is performed.

## Reproduce

Activate an existing Python environment, then run from any directory:

```sh
python research/india-pakistan/tools/pakistan_topdown.py --workspace /path/to/your/Sentient-Futures-workspace
```

The relative script path above assumes the writing-kit worktree is the current directory. Python standard library only; no network during reproduction. Outputs go to `research/india-pakistan/build/pakistan-topdown/`; `--output-dir` can select a fresh verification directory. The full private workspace is required because the manifest binds original retained captures outside this checkout. This is not a publicly portable data package or permission to redistribute source captures.

`input-manifest.json` identifies and checks fourteen original/transcription files. Twenty-six selected Naheed HTML hashes are additionally checked against the original acquisition manifest. `sources.json` records each source, date, locator and limit. PBS price columns were checked visually against the original PDF as well as extracted text. The source page and code-native quantity definitions control over shorthand labels in older CSV exports.

## Quantity scenarios

- **FAO2023_fixed:** original food-balance food-availability totals, poultry and milk excluding butter, held constant across the comparison years. These are neither purchases nor forecasts for those comparison years.
- **EconomicSurvey2024_25_fixed:** poultry production and source-estimated milk for human consumption from Table 2.6, held constant. Fiscal-year production/supply estimates differ from FAOSTAT food balances and are not substituted into the original model.
- **OECD_poultry_FAO_milk:** OECD–FAO 2025–2034-vintage poultry consumption volume (`QC`, thousand tonnes, ready-to-cook weight) at the requested years. The 2035 value explicitly carries 2034 forward unchanged; it is not an OECD forecast for 2035. Milk remains the historical FAOSTAT total because a matched future retail-milk quantity is not established here. This mixed-source check is a scale comparison, not a coherent national forecast.

FAOSTAT per-person food-supply quantities are extracted separately for context; they are not multiplied by a different source's population. OECD retail-weight per-person measures are not combined with its ready-to-cook aggregate quantities.

## Price and conversion assumptions

The primary PBS issue is dated 24 December 2025. Its national-average values come from its urban-market sample, not a census of every transaction. Chicken is priced per kilogram **live broiler**. Accordingly, every primary poultry calculation requires an explicit analyst dressed/live yield assumption: 0.60, 0.70 or 0.80. These values are a sensitivity grid, not locally measured yields. The result is a live-bird-price equivalent for a meat quantity. Processing margins, cut composition, offal revenue and retail markups are not estimated; it is not a validated dressed-meat retail price.

PBS fresh milk is priced per litre. The milk-equivalent quantity is divided by an explicit liquid-milk density reference of 1.031 or 1.04 kg/litre, taken from the retained FAO INFOODS database's DK whole-liquid-milk and KEN whole-cow-milk rows. The source factor is documented, but its transfer to Pakistan's mixed-species, processed-product milk-equivalent basket is **unvalidated**. Fresh milk is a valuation proxy for that basket, not proof of its retail composition. Self-produced/nonmarketed consumption is not separated.

The three official profiles are transparent paired sensitivities: lower value uses yield 0.80/density 1.04; central sensitivity uses 0.70/1.031; upper value uses 0.60/1.031. They are not percentiles or a comprehensive joint uncertainty distribution.

Naheed's captured chicken-cut and packaged-milk prices provide minimum/median/maximum premium-outlet sensitivities. Bone-in/boneless cuts, package sizes and products differ; no market weights are assigned. Every original listing, including out-of-stock observations, remains visible. The eleven alternative-milk listings are normalized and retained as product-price context, but are not added to conventional-milk value or used to imply actual sales. Doing so would double count or change the meaning of the capture-share assumption.

Prices captured in October 2026 are divided mechanically by 1.071, using the retained IMF October 2026 Pakistan annual CPI-change value, and converted with the retained 2025 period-average exchange rate. This is a national annual/fiscal-year CPI sensitivity, **not** an observed category-specific or exact October-to-2025 deflator. All Naheed results retain this mismatch. The PBS weekly 2025 price likewise is not an annual-average price. The common reference-price label is conditional on these conversions.

## Arithmetic and interpretation

For each commodity: thousand tonnes × price per compatible kilogram ÷ PKR/USD = million USD. Kilogram and million-dollar factors cancel. Multiply the resulting conventional-value proxy by the user-specified 0.05%, 0.1% and 0.5% capture shares. Sum poultry and milk only after keeping component values visible. Capture shares are hypothetical monetary shares, not volume substitution rates or an empirical demand curve.

Each of 162 rows records source years, comparison year, price date, price adjustment, FX, conversion assumptions, component values, combined value, transfer lower/upper endpoints and three comparison flags. A component and its combined total are both compared with the full transfer range for transparency; this does not assert that their product baskets match. Many shares lie above that range. The first milk-only calculation triggered the required stop; Umar subsequently approved: **“Continue the conditional check with explicit caveats.”** All large discrepancies remain reported, including later extreme grid cells. The initial stop receipt is preserved under the handoff's `p4/` folder.

The check is computationally independent of India's transfer equation but shares some source context. Its large values can reflect broad conventional-food scope, nonmarketed supply, mapping assumptions or an unsuitable capture share. They do not prove that the transfer is wrong or that any alternative-protein sales level is achievable. The primary empirical recommendation remains a documented Pakistan sales baseline and matched retail quantities/prices.

Agent source and arithmetic checks do not substitute for human factual/code review or acceptance of these assumptions.
