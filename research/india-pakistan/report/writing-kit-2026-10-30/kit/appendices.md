## Appendix A. Proxy equations, Pakistan medians and scale check (budget: 800 words)

**Claim:** The complete specification and retained medians allow a reader to inspect the transfer without elevating its precision into a body headline.

**Evidence:** The [proxy methods](../../revisions/2026-10-27/methods/proxy.md), **27 October 2026**, and [reference rows](../../../data/altprotein_proxy_scenarios.csv), calculation edition **15 October 2026**, define the following conditional results in **million US dollars at constant 2025 prices**. Evidence family: model specification and derived scenarios. Lower, median and upper refer to the **10th, 50th and 90th percentiles** of selected draws.

| Pakistan year | Lower | Median | Upper |
| --- | ---: | ---: | ---: |
| 2026 | 1.5 | 3.6 | 6.6 |
| 2030 | 2.3 | 6.0 | 13.7 |
| 2035 | 3.6 | 11.8 | 36.1 |

Dropping Pakistan's relative urban-share and animal-supply multipliers lowers its **2035** median to **$8.3 million**. The original **2035** median is approximately **$0.040/person/year**, or **0.17%** of the fixed US **2025** per-person benchmark. These are diagnostic and denominator-specific quantities, not national observations.

**Equation guide:** Indian spending per person equals the converted anchor per person, multiplied by the real-income index raised to the income elasticity, the urban-share ratio and accumulated additional growth. Pakistan's per-person value equals that Indian value multiplied by the relative-income ratio raised to the same elasticity, the relative urban share, the animal-supply ratio raised to its sampled weight and the sampled industry factor. Multiply each per-person value by its population to obtain national spending. The exact symbols, equations, input rows and seed remain in the linked methods and engine; do not retype rounded parameter values as a new specification.

**Caveat:** The input mappings are assumptions, not fitted causal effects. Beyond the IMF horizon of **2031**, the model extends the last available growth rates; this is not an additional IMF forecast. A reproducible calculation does not validate the transfer.

**Cross-reference:** Use the shared definitions discussion for scope and price basis; retain the regional specification here.

**Figures or tables:** The Pakistan table above and the scale-check table that follows. Keep original data and equations available as companions to the joint PDF.

**AI draft, replace:** The appendix retains the numerical detail needed to audit the regional estimates. Pakistan's medians depend on its transfer multipliers, and the overlap sensitivity shows why these amounts should not be treated as precise national forecasts. The body therefore uses the approved order-of-magnitude presentation, while the exact reference rows remain unchanged and available for review.

**Open questions for Umar:** Scientific acceptance of the transfer assumptions remains separate. The scale check now sits here; consider moving part of the results section's word budget to this appendix.

## Appendix B. Exploratory elicitation supplement (budget: 450 words)

**Claim:** The separate elicitation documents repeated AI responses and workflow disagreement; its inclusion is a proposed, explicitly disclosed departure from the earlier team decision.

**Evidence:** The [panel methods](../../revisions/2026-10-27/methods/panel-supplement.md), dated **22 October 2026**, report **60 accepted responses** from **79 recorded entries**: **15 rejected**, **3 execution errors** and **1 entry without a recorded command**, in addition to the accepted set. Retained panel data (workspace file: `.worktrees/report-review-20261027/data/panel_runs.json`) and attempt register (workspace file: `.worktrees/report-review-20261027/data/panel-attempts.csv`). Evidence family: exploratory elicited outputs and execution accounting, not independent experts.

The binding interview record (workspace file: `OUTPUTS/Drive Review 2026-10-29/CONSOLIDATION-STRATEGY.md`), **30 October 2026**, requires this appendix to disclose departure from the **13 October 2026** collaboration decision that the Global South sections use proxies rather than LLMs. Inclusion remains a team decision. Anna's study and the supplementary US arm remain separately authored exercises.

**Caveat:** The regional prompts exclude fermentation while the proxy includes it in intended scope. Regional evidence packs included GFI material, so agreement is not independent corroboration. Search parity and requested provider identity are not automatically established by the receipts. Selection, retries and a parser amendment can affect the accepted set. Between-run dispersion is not predictive uncertainty. No pooled median or new model call is added.

**Cross-reference:** Keep a single sentence in the main body and the methods disclosure here. Do not present this as Anna's approved protocol or an accepted joint result.

**Figures or tables:** Use the attempt accounting above; detailed retained numerical summaries remain in the companion. Private prompts and raw response text are not reproduced.

**AI draft, replace:** This supplement records a separately authored exploratory exercise. Its repeated responses reveal stability and disagreement within the recorded workflows, subject to the supplied evidence and acceptance rules. It departs from the earlier team choice to use proxies for the Global South sections and is proposed for appendix treatment only. Its results do not replace the main scenarios, establish calibrated uncertainty or provide independent confirmation.

**Open questions for Umar:** Obtain the team's appendix-only inclusion decision; the heads-up to Anna remains unsent.

## Appendix C. Sources and review trail (budget: 350 words)

**Claim:** Readers should be able to trace each retained numerical statement to its source and transformation without confusing an agent check with human acceptance.

**Evidence:** [Claims by section](claims-by-section.csv), [conflicts and unresolved items](conflicts.md), and [section/source map](00-section-map.md) provide the writing trail. Evidence family: local provenance and review records. Original source links accompany evidence throughout the kit; their source dates are distinguished from observation and access dates.

**Caveat:** “Verified” and “corrected” in the CSV mean the specified agent source/arithmetic checks passed. Human factual/code verification remains pending unless a named human supplies a dated disposition. Unknown publication dates remain unknown. A working link or retained hash does not establish rights, current availability or national representativeness. Draft collaborator snapshots are for cross-reference only.

**Cross-reference:** The joint report should use a common bibliography with hyperlinks after its authors agree the definitions and final text.

**Figures or tables:** Use the CSV as an editing and review aid, not as hidden identifiers in the DOCX. The final joint PDF is the citable version; website and repository materials are companions.

**AI draft, replace:** The source register separates original observations, published model estimates, analyst calculations and proposed tests. It records what each source supports and the limits that remain. Before submission, the author and named reviewers should complete the factual, numerical and code checks and carry unresolved items into the text or omit them. The existence of a reproducible companion does not replace that review.

**Open questions for Umar:** Assign the remaining human review and confirm source-specific reuse requirements before external sharing.

### Source list for bibliography assembly

- FAO, [FAOSTAT Food Balances](https://www.fao.org/faostat/en/#data/FBS).
- FAO and partners, [The State of Food Security and Nutrition in the World](https://www.fao.org/fileadmin/templates/cfs/CFS53/Plenary_documents/Inf.15_SOFI_Report/EN_compiled.pdf).
- UNICEF, WHO and World Bank, [Joint Child Malnutrition Estimates](https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/jme-country-estimates-march2026.xlsx?sfvrsn=65301f6b_3).
- Pakistan Bureau of Statistics, [Household Integrated Economic Survey revised quantity table](https://www.pbs.gov.pk/wp-content/uploads/2020/07/TABLE_23-2.xls).
- Government of India, MoSPI, [Nutritional Intake in India](https://www.mospi.gov.in/sites/default/files/publication_reports/Nutritional_Intake_in_India_L.pdf).
- Bryant and colleagues, [A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China](https://doi.org/10.3389/fsufs.2019.00011).
- GFI India and Deloitte, [Smart Protein Economic Analysis](https://gfi-india.org/wp-content/uploads/2024/06/GFI-India-economic-analysis.pdf).
- GFI, [US retail market data](https://gfi.org/marketresearch/).
- IMF, [World Economic Outlook macroeconomic series](https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH); World Bank, [official exchange-rate series](https://api.worldbank.org/v2/country/PAK/indicator/PA.NUS.FCRF?format=json).
- Government of India, [BioE3 Cabinet approval](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2048568&lang=2&reg=3); DBT-BIRAC, [Smart Proteins research call](https://www.birac.nic.in/cfp_view.php?id=98&scheme_type=46).
- Cosenza and colleagues, [Bayesian optimisation of culture media](https://doi.org/10.1002/elsc.202300005); Watson and colleagues, [protein design and experimental validation](https://doi.org/10.1038/s41586-023-06415-8).
- [Cell Forge](https://cellforge.in/), [Cowlar](https://www.dairy.cowlar.com/howItWorks) and [Poulta](https://poulta.com/), first-party application descriptions; [SUN Business Network account](https://sunbusinessnetwork.org/stories/alis-out-of-the-box-idea/) for Poulta's reported Pakistan connection. These are not independent performance evaluations.
- Pakistan, [Pakistan Halal Authority Act](https://pakistancode.gov.pk/pdffiles/administrator1d376dbb967abb1d9ed2dcb3ae978dbc.pdf); Punjab Food Authority, [functional-food regulations with a novel-food provision](https://pfa.gop.pk/wp-content/uploads/2023/05/Punjab_Food_Authority_%28Functional_Food,_Foods_Supplements%29_Regulations,_2025.pdf).
- International Islamic Fiqh Academy, [cultivated-meat resolution](https://iifa-aifi.org/en/56085.html); MUIS, [cultivated-meat guidance](https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/).

Dates, exact locators and acceptance limits are attached to their uses above and in the companion CSV. P4's official-price and quantity sources are documented in its box and reproducibility records. The collaborator snapshots are working cross-references and should not be cited as final publications.
