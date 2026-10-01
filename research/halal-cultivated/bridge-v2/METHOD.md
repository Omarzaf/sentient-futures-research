# Quantitative bridge v2

Version 2.0.0 · 1 October 2026 · AI-assisted working method; human verification pending.

This is the active Phase Two quantitative contract. It replaces the incompatible v1 bridge, gate, survey-substitution and unknown-capacity rules. It does not alter Phase One evidence, the original CSV bytes, or the earlier comparative calculator. The [crosswalk](LEGACY-CROSSWALK.md) records those boundaries. [Production](production-state.json) remains `blocked_missing_baseline`; the [worked example](synthetic-example.json) is synthetic and is not a country estimate.

## Estimand and arithmetic

Freeze geography, segment, year, species, finished-product definition, channel, denominator, currency and price year, and mass basis. Each baseline separately records source vintage, observed-versus-forecast sales, uncertainty interpretation, permitted transformations and documented conditioning. Sources have a citation locator and review status. Machine checks establish consistency, not the accuracy of an attributed source.

Use cultivated finished-product mass divided by the total compatible cultivated-plus-conventional market mass. When the input is a **two-component value share** `s` and prices describe the same market and period, the relative finished-product mass price `r = P_cult / P_other` permits:

```text
p_mass = s / (s + (1 - s) * r)
Q_unconstrained = D_compatible * p_mass_assumed * G_scenario
Q_feasible = min(Q_unconstrained, K_allocated)   when capacity is compatible and known
Q_feasible = null                              otherwise
cultivated_biomass = Q_feasible * cultivated_fraction
```

`D_compatible` is the declared total reference market, not a protein-supply forecast. The current implementation accepts only kg or tonnes of finished product. Carcass, retail and biomass conversions must be independently evidenced and performed in a separately registered upstream transformation before use; there is no default yield conversion. The current two-component price method also cannot use a cultivated/conventional **ratio**, an aggregate unweighted price, or an all-meat denominator for chicken. A multicomponent price conversion requires a separately checked method; it is not approximated here.

Borrowing a US share is a geographic/segment **assumption**, even when the US measurement is observed. Forecast input stays forecast. Source and target must otherwise match their declared dimensions, including year and channel. A retail input cannot become an all-channel input without an explicit reviewed upstream conversion. No extrapolation/interpolation is implemented. Stated willingness, preference, awareness and willingness to pay cannot supply penetration; a calibrated purchase model would require its own study and contract.

The supported uncertainty method is a **deterministic sensitivity**, labeled `sensitivity`. Input marginal q10/q50/q90 values cannot be divided and relabeled as output quantiles. Joint-draw or fixed-denominator probabilistic methods are intentionally blocked until a registered implementation, dependence assumptions, input draws and independent checks exist. There are no inferred scenario probabilities.

## Evidence and assumptions

An assessment records institution, jurisdiction, territorial and segment scope, product, process, dimension, status, conditions and supporting locators, issuance/effectivity/check dates, document type, identifier, amendment check and review limits. Distinct dimensions use distinct positive statuses:

| Dimension | Example positive status | What it does not establish |
| --- | --- | --- |
| Religious position | `permitted` | A product certificate or food approval |
| Certification route | `route_available` | An issued certificate |
| Product certificate | `certificate_issued` | Food authorization in another country |
| Food authorization | `authorized` | Import access or religious approval |
| Import access | `access_allowed` | Permission for another process or product |

Unknown, conflicting and bounded-search-not-found states remain in the evidence record. `not_applicable` requires a sourced reason. A conditional position includes every applicable condition and evidence for each claim that it is met. Certificate validity, legal effect and later amendments remain separate from a general institutional position. An official announcement or proposal cannot be treated as adopted law.

A separate scenario declares `open`, `closed` or `unresolved`, mapping to `1`, `0` or `null`. An evidence-led open gate requires applicable positive support for every required dimension, including food authorization. Product, process, territory, segment and dates cannot be transferred by relabeling. Any needed import or certificate dimension must be declared according to the actual product route; this schema cannot discover an omitted factual requirement. Qualified regulatory review remains necessary.

A counterfactual gate can assume future conditions but must retain its label, rationale, assumed conditions and any known contradiction. It does not assert present lawful access. Religious prohibition can close only the supported institution/product/segment case. Closing all national sales requires a binding national access restriction or an explicitly labeled counterfactual. This distinction is especially important for an all-consumer India estimand. There is no generic `L_includes_halal` bypass: every required dimension must have its own scoped support.

## Conditioning, supply and aggregation

Before transfer, document whether religious acceptance, legal timing, certification, price or supply is already embedded in the baseline. The current numerical path requires a full-access reference baseline with permitted transformations. An unconditional sales or rejection-adjusted forecast cannot receive a generic gate/retention discount. Reusing an embedded mechanism is rejected. A replacement must be a newly versioned, source/owner-supported baseline with the old mechanism removed and the revised conditioning documented; a boolean waiver is not sufficient.

Shock mechanisms are explicit, sourced and unique per scenario. This implementation records pre-specified changes to demand, capacity, gate or conventional price; it does not simulate price-induced substitution. A change to the transferred share is rejected pending a separate behavioral model. Input pre/post lineage and causal interpretation still require research review.

Capacity is assigned once from a named pool within an `allocation_group`. A group represents one simultaneous world; alternative scenarios use separate documented groups. Allocations in a group cannot exceed the pool, and allocation IDs cannot be reused. Missing capacity, an unknown pool or an incompatible mass basis leaves feasible quantity null. A hypothetical closed gate still cannot supply a missing demand/share/price value.

`aggregation_group` declares cells intended to be added. Cells share an estimand apart from mutually exclusive segments. More than one segment requires the same documented partition with disjoint member keys and source lineage. The validator catches declared overlaps; it cannot independently certify a real population partition. Channels are not added across incompatible scopes. A finished hybrid observation counts once, and its fraction affects biomass only. No displacement, production response, animals spared or causal effect is inferred from market share.

## Independent synthetic example

Take cultivated value 10 and conventional value 90. At respective prices 2 and 1 per kg, their masses are 5 and 90 kg. Therefore the cultivated mass share is `5 / 95 = 1 / 19 = 0.05263157894736842`, while value share is 0.10. This independently reproduces the two-component identity above.

At an assumed compatible reference market of 1,000 kg, a hypothetical open gate gives `1,000 / 19 = 52.63157894736842` kg unconstrained. Allocated finished-product capacity of 40 kg caps feasible quantity at 40 kg. A 20% cultivated hybrid fraction yields 8 kg cultivated biomass. None of these values is an observation or research forecast.

## Verification and limits

[schema.json](schema.json) is a strict JSON Schema using the documented subset implemented in `tools/bridge-v2-checks.mjs`. Unknown fields and unsupported schema keywords fail. Semantic checks run before results are released, and invalid contracts return no numerical results. Stored expected outputs are compared with the calculation. The production fixture proves the unresolved path as well as the synthetic positive path.

From the repository root run `node tools/test-halal-checks.mjs`; it invokes both historical CSV checks and the adversarial v2 fixtures. The real `node tools/verify.mjs` also checks the v2 schema, synthetic example and production state through `checkHalal`. The standalone v2 suite is `node tools/test-bridge-v2-checks.mjs`.

These tests do not establish scholarly approval, source truth, observed adoption, manufacturing facts or lawful access. Missing compatible demand inputs and scoped human review remain outstanding. Earlier evidence and numerical outputs are historical snapshots, not silently migrated results.
