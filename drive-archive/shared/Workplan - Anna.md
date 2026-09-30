# Workplan: Alt-Protein Demand Forecasting

Source: Google Doc `Workplan - Anna` (owner: Anna Bartlett). Last modified 2026-09-25. Exported 2026-09-29 from the shared team Drive folder. Table cell text has been tidied from the export's escaping; wording is unchanged.

### Part of the wider project: "How could AI reshape the food system transition over the next 10-20 years?"

## Sub-Question

**Current (updated):** What will future demand for alternative proteins look like, and what are the key limiting or accelerating factors — including the role of AI — in that trajectory?

**Deprecated:** "Will alternative proteins meaningfully reduce animal product demand?" — narrowed because isolating the demand forecast from the substitution/displacement relationship makes each more tractable to research rigorously within a 10-week project.

**Bridging addition:** a short, explicitly caveated section translating the demand forecast into a plausible range of implied effects on animal protein demand, using historical substitution analogues rather than a new forecast.

## End Goal

A short forecasting report (~2,000-4,000 words + appendix) containing:

1. A synthesis of existing projections of both conventional meat market growth and alt-protein consumer demand, noting where and how alt-protein competition is (or isn't) already accounted for in each.
2. A literature-based driver map covering the key factors — including AI-driven ones — likely to accelerate or limit alt-protein adoption.
3. A quantitative forecast range for alt-protein demand by 2035, generated through a structured LLM-based elicitation process (used in place of a human expert panel), with identified cruxes/points of model disagreement.
4. A comparison between the LLM-elicited forecast and trend-based extrapolation from existing data/projections.
5. A short bridging estimate translating the alt-protein demand forecast into a plausible range of implied effects on animal protein demand, clearly flagged as illustrative rather than a validated forecast.

## Table of Contents (Final Report)

1. Executive Summary
2. Background & Motivation
3. Methodology
   - 4.1 Desk research approach
   - 4.2 LLM forecast elicitation protocol
   - 4.3 Comparative analysis approach
4. Desk Research Findings
   - 5.1 Existing animal protein market projections (and treatment of alt-protein competition within them)
   - 5.2 Existing alt-protein demand projections
   - 5.3 Driver map (price parity, taste/texture, culture, regulation, distribution, AI-related factors)
   - 5.4 Historical substitution analogues (margarine/butter, plant milk/dairy, etc.)
5. LLM Forecast Results
   - 6.1 Elicitation protocol summary
   - 6.2 Aggregated quantitative results (median, range)
   - 6.3 Cruxes identified from rationale analysis
6. Comparison: LLM Forecast vs. Desk Research Trends
7. Bridging Estimate: Implied Effects on Animal Protein Demand
8. Limitations
9. Recommendations for Further Work

- Appendix A: Full elicitation prompt(s) and background materials
- Appendix B: Desk research source list and notes
- Appendix C: Raw model outputs

(The section numbering is reproduced as it appears in the source document.)

## 10-Week Work Plan

**Week 1 — scoping and desk research (w/c 31 Aug 2026).** Confirm final sub-question scope. Begin desk research: define areas of desk research needed; locate existing conventional protein market projections and alt-protein demand projections; note whether alt-protein competition is factored into conventional meat projections.

**Week 2 — desk research (w/c 7 Sep 2026).** Continue desk research: build driver map (price parity, taste/texture, culture, regulation, distribution, AI-related factors). Identify 2-3 historical substitution analogues (e.g. margarine/butter, plant milk/dairy) and any literature-stated elasticity figures.
- Key event: Tues: first meeting with mentors.
- Progress/notes: "I've done some desk research, mostly gathering other resources who have made predictions including business analyses and alt protein companies/ orgs. I haven't started the driver map but I've been reconsidering how useful that is/ how useful gathering lots of forecasts are if I'm not going to give them to LLMs anyway. Tightened scope: less emphasis on desk research/ finding others forecasts and drivers. More emphasis on approach to LLM forecasting: what to ask, how to ask, what info to give."
- To do's for next week:
  - Gather as many predictions on market size as possible and compare, e.g. market analyses v altprotein orgs (why different predictions differ - identify potential cruxes)
    - Look at GFI!
  - Clarify part 1) gathering and comparing existing forecasting attempts. 2) LLM forecasting
  - Research how to use credits for LLMs and what is possible with my budget
  - Historical substitution
  - Look at Liliia's info on insects inclusion
  - New methodology: reproduce global (or US?) LLM predictions and then Rufaro and Umar will take it and look at country case studies to compare
    - Change the scope in some rounds of prompts to be US and some to be global
  - Umar is choosing specific models and giving reasoning

**Week 3 (14 Sep 2026).** Synthesize desk research into driver map and source list. Draft funding one-pager. Identify remaining data gaps for the LLM elicitation to address. Begin drafting the elicitation prompt and background pack.
- Progress/notes: **Prompt created but needs refining (metric, geographical scope, iterate with LLM feedback).** **Looked a bit into substitution analogues but needs work.**
- To do's for next week:
  - **Narrow the scope to US: because global is too wide, and not comparable. Con = misses any insights LLMs might have for the non west**
  - **Using 10, 50, 90**
  - **EXCLUDE historical data: this will only bias them. Only use to compare in a literature review**
  - **Meeting with Cassi: as when it will be public, pricing, concern over 'marking them'?**
  - **Finalize LLM choices from new methodology**
  - **Iterate survey wording with LLM for feedback**
  - ~~ORGANISE Cassi meeting!~~
  - **Also consider future part of project: putting question on Metaculus/ look at Metaculus forecasts!**

**Week 4 — LLM elicitation (21 Sep 2026).** Finalize elicitation prompt. Select model panel (4-6 models from different providers). Pilot prompt on 1-2 models and refine. Key event: ~~Funding pitch submitted~~.

**Week 5 — LLM elicitation (28 Sep 2026).** Run full round-1 elicitation across all models using Claude's code. Log all responses (estimate, range, probability, rationale) systematically.

**Week 6 — LLM elicitation (5 Oct 2026).** Repeat each model's elicitation 2-3 times to check stability. Compile anonymized round-1 rationales; run round 2 (Delphi-style) elicitation. Key event: Funding outcome known — begin scoping validation check (if funded) or protocol stress-testing (if not), in parallel with round 2.

**Week 7 — Analysis of LLM (12 Oct 2026).** Aggregate round-2 estimates (median, range). Code rationales for recurring themes/cruxes. Compare LLM forecast against desk research trends and existing projections.

**Week 8 — substitution research (19 Oct 2026).** Produce the bridging estimate: apply historical substitution ratios to the alt-protein forecast to generate an illustrative range of implied effects on animal protein demand, with explicit caveats.

**Week 9 (26 Oct 2026).** Draft full report following the table of contents above.

**Week 10 (2 Nov 2026).** Incorporate mentor feedback and finalize the report. Share findings with Rufaro and Umar for their parallel workstreams. Project complete.

## Limitations to State Explicitly in the Final Report

- LLM forecasts have not been validated against real-world calibration in the way human superforecaster track records have.
- Models may share correlated blind spots even when drawn from different providers.
- The bridging estimate relies on historical analogues that may not transfer cleanly to alt proteins, given differences in product category, cultural/psychological substitutability, and starting market conditions.

## Key Risks

| Risk | Mitigation |
| :-: | :-: |
| Topic too big to scope | Force yourself to pick 2-3 crisp sub-questions by end of Week 1; treat anything else as future work |
| Not enough evidence for quantitative forecasts | LLM elicitation + qualitative driver map still constitutes a valid, useful output even without hard data |
| No funding / no expert survey | LLM forecasting *is* the Plan A output now, not a fallback — report stands on its own as an MVP |
| LLM forecast validity uncertain | Be explicit about this limitation in the report; frame as hypothesis-generating, not final answer |
