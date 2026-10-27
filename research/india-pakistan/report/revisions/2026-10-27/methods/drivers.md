# Demand drivers, obstacles and proposed tests

**Local review candidate, 27 October 2026. Human factual, code and editorial review pending.**

These eight factors organize the argument. They are not an exhaustive census of demand drivers or eight estimated causal effects. A possible mechanism, an observed association, a policy announcement and a model assumption support different claims. India and Pakistan evidence remains separate, and missing Pakistan evidence is not filled with an Indian or US estimate.

The detailed [evidence ledger](../data/driver-evidence.json) records source dates and locators, geography, population/product scope, evidence class, model treatment, limitations and review status. The [recommendation register](../data/recommendations.csv) specifies proposed actors, comparators, outcomes and follow-up periods. No partner, budget or programme is represented as committed.

## Mechanisms and obstacles

| ID / factor | What could increase demand | What could constrain or reverse it |
|---|---|---|
| D01 Income | More purchasing power can expand feasible purchases. | Additional income may go to conventional foods; income distribution and actual purchase responses are unmeasured. |
| D02 Affordability | Lower real price per comparable usable serving can improve access. | Parity with meat does not necessarily imply affordability against other foods or household budgets. |
| D03 Dietary practice | Products that perform well in familiar meals may earn repeat use. | Taste, preparation, cuisine and health/processing perceptions vary by product and group. Perceptions are not clinical evidence. |
| D04 Social legitimacy | Familiarity and trusted information may reduce uncertainty. | Favourable hypothetical answers can coexist with distrust, stigma or low paid repeat purchase. |
| D05 Certification | A documented product-specific assurance route can reduce uncertainty. | Halal assessment and food authorization are distinct; neither follows from a general institution alone. |
| D06 Public policy | Implemented support can improve capabilities or entry conditions. | Announcements may not become disbursement, usable infrastructure, authorized products or purchases. |
| D07 Industry capacity and access | Verified technical capabilities and dependable distribution can improve performance, cost and availability. | Advertisements and directory entries do not establish skill shortages, capacity, product quality or repeated retail access. |
| D08 AI | Validated technical gains may improve production performance or cost. | Scale-up, validation costs and retail pass-through can absorb gains; conventional producers may improve too. |

The net direction of D03–D08 is conditional or mixed. No magnitude or country ranking is inferred from this table.

## Country evidence and observations that would change the assessment

| ID | India evidence | Pakistan evidence | Useful signpost |
|---|---|---|---|
| D01 | WEO income path is a macro input; spending elasticity is assumed.[^driver-income] | Relative-income transfer has no fitted national alternative-protein sales anchor. | Actual purchases by defined income group, alongside macro revisions. |
| D02 | SOFI estimates 40.4% unable to afford a healthy diet in 2024.[^driver-sofi] | The corresponding estimate is 60.3%; neither number measures an alternative-product premium. | Dated matched portions, retail prices, stock and paid repeat purchases. |
| D03 | An online intention study and GFI's modelled category mix provide limited product context.[^driver-bryant][^driver-gfi] | Food-balance supply cannot establish preferences for chicken or milk replacements.[^driver-fao] | Meal-specific choices, preparation success and repeat use by defined groups. |
| D04 | Familiarity correlates with acceptance in Bryant et al.'s selected sample; this is not an intervention effect.[^driver-bryant] | This retained package provides no matched national paid/repeat-purchase measure. | Separate intention, first paid purchase, repeat purchase and displacement. |
| D05 | This bounded source set establishes no product-specific determination for the proposed fermentation example. | The 2016 Act establishes institutional provisions, not a named product's status.[^driver-halal] | Written ingredient/process-specific assurance and authorization decisions. |
| D06 | BioE3 identifies smart proteins, R&D and Bio-AI/biomanufacturing infrastructure as policy aims.[^driver-bioe3] | Halal institutional provisions do not establish equivalent smart-protein funding or uptake. | Separate records of announcement, implementation, funding, approval and market outcomes. |
| D07 | Talent-study cohorts and vacancy records identify issues to investigate.[^driver-talent][^driver-jobs] | Two directory rows and 58 recorded 2025 vacancies are coverage-limited proxies, not a census. | Verified staff/facilities, process performance, unit cost and outlet availability. |
| D08 | BioE3 supplies a policy-intent reference, not an estimated AI spending effect.[^driver-bioe3] | No national AI effect is established in this retained specification; that does not show applications are absent. | AI/non-AI technical performance and cost, then separately observed retail outcomes. |

The Indian survey contains 1,024 online respondents and is skewed urban, affluent and educated. It has no Pakistan sample. Its hypothetical willingness must not be relabelled as national paid demand. SOFI measures economic access to a healthy diet, not protein deficiency or the affordability of a particular replacement product. FAOSTAT food balances measure supply, not individual intake or substitution.

## What the current model represents

D01 enters explicitly through real income and a chosen elasticity. D03 enters Pakistan's transfer only through an animal-protein-supply multiplier, which does not separately represent taste or dietary choice. D07 supplies the vacancy-growth ceiling for additional growth and the relative industry factor for Pakistan. Their conversion into spending is assumed, not fitted to purchases.

D02 and D04–D06 have no separately identifiable coefficients. They may be among the mechanisms implicit in additional growth, but the aggregate model cannot quantify their separate effects. D08 has no AI multiplier. Adding an AI or policy bonus would require a new justification and a check for overlap with existing growth assumptions. Cultivated meat is excluded. Fermentation is in the proxy's intended scope but has no separately estimated amount. These are properties of the retained specification, not evidence that the mechanisms do not matter.[^driver-model]

## US transferability questions

The three themes below were supplied in reviewer feedback. The original US-panel passage and executed methods have not been established in this revision. They therefore remain **comparison prompts**, not newly verified original-panel findings. Umar's supplementary US arm is a separate exercise; its questionnaire provenance does not establish equivalence with another panel. No private panel quotation or questionnaire is reproduced here.

| Reviewer-supplied theme | Relevant driver IDs | Country-specific question |
|---|---|---|
| Political environment | D04–D06 | Which dated policies, assurance rules or social conditions apply to the named product, and which implementation stages are evidenced? |
| Health trends | D02–D04 | Which buyers hold which beliefs about a specific product, and do those beliefs predict paid repeat purchase at its actual price? |
| R&D landscape | D07–D08 | Which technical constraint affects product performance, cost or availability locally, and does resolving it improve a measured outcome? |

The US sales series also has three mathematical roles in the retained analysis: an elasticity bound, an additional-growth lower bound and a historical per-person comparison. The separately reported sensitivities test those assumptions. A US sales change cannot, by itself, assign signs or effect sizes to the themes above.

## Recommendations follow the evidence and its gaps

These are proposed learning activities. They are not a ranking of expected returns or an existing implementation programme. Every major obstacle has a disposition: measure it, run a bounded feasible test, seek qualified clarification, or monitor a specific stage.

| Recommendation | Driver IDs | Proposed action and outcome |
|---|---|---|
| R01 Comparable retail audit | D01, D02, D07 | Track matched prices, stock and actual purchases separately in each country; an unavailable sales series remains unavailable. |
| R02 Meal-fit and purchase study | D02, D03, D04 | Test a defined product and meal; distinguish paid trial, unsubsidized repeat purchase and separately measured displacement. |
| R03 Fermentation product dossier | D05, D06 | Specify ingredient, process, product and jurisdiction; obtain qualified assurance and food-authorization clarification separately before a pilot sale. |
| R04 India technical trial | D07 | Confirm one employer-nominated constraint and compare performance and cost against a credible baseline. |
| R05 Pakistan feasibility assessment | D07 | Verify facilities, staff, inputs and product need before deciding whether an ingredient-application trial is feasible. |
| R06 AI/non-AI comparison | D07, D08 | Measure usable output, consistency and total unit cost against a credible non-AI process; assess retail pass-through separately. |
| R07 Policy stage register | D05, D06 | Track documented implementation and product decisions; do not convert an announcement into a growth bonus. |

The register's 8–12-week purchase follow-ups, 3–6-month technical pilots and quarterly policy reviews are proposed design horizons, not empirical findings or booked activities. Feasibility, sample, comparator, cost ceiling and decision threshold must be set before a study begins. Current evidence does not justify numeric success thresholds. Product-specific assurance questions must be resolved before any proposed sale, regardless of a nominal study timetable.

[^driver-income]: IMF, *World Economic Outlook database*, October 2026, LP and NGDP_RPCH series. [Official DataMapper source](https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH). Retained source ID `imf_weo_2026_10`; see proxy methods §3.2 for extrapolation beyond 2031.
[^driver-sofi]: FAO, IFAD, UNICEF, WFP and WHO, *The State of Food Security and Nutrition in the World 2025*, Annex A1.6, physical PDF page 176, India and Pakistan, 2024 percentage column. [Original report](https://www.fao.org/fileadmin/templates/cfs/CFS53/Plenary_documents/Inf.15_SOFI_Report/EN_compiled.pdf). Source ID `fao_sofi_2025`.
[^driver-bryant]: Christopher Bryant et al., “A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China,” *Frontiers in Sustainable Food Systems* 3 (2019), physical PDF pages 1–3, abstract and methods. [Original article](https://doi.org/10.3389/fsufs.2019.00011). Source ID `india_cultural_bryant_2019`.
[^driver-gfi]: GFI India and Deloitte India, *Smart Protein Economic Analysis*, physical PDF page 1, Methodology, and page 4, domestic table. [Original report](https://gfi-india.org/wp-content/uploads/2024/06/GFI-India-economic-analysis.pdf). Source ID `gfi_india_smart_protein_economic_analysis_2022`; exact publication date and valuation basis remain unestablished.
[^driver-fao]: FAO, [FAOSTAT Food Balances](https://www.fao.org/faostat/en/#data/FBS), 28 October 2025 vintage, 2023 observations. Source ID `fao_fbs_2025_10_28`; seven animal-source protein-supply inputs are identified in proxy methods §3.4.
[^driver-halal]: *Pakistan Halal Authority Act, 2016*, Act VIII of 2016, §§1, 3 and 10. [Dated institutional text](https://pakistancode.gov.pk/pdffiles/administrator1d376dbb967abb1d9ed2dcb3ae978dbc.pdf). Source ID `pakistan_cultural_halal_act_2016`. This reference is not an exhaustive current legal or commencement assessment.
[^driver-bioe3]: Government of India, Press Information Bureau, “Cabinet approves BioE3 policy,” 24 August 2024, paragraphs on R&D, Bio-AI infrastructure and smart proteins. [Official announcement](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2048568&lang=2&reg=3). Source ID `india_pib_bioe3_2024`.
[^driver-talent]: Amrutha Girivasan and Chandana Tekkatte, GFI India, *A comprehensive analysis of India's talent landscape for the smart protein sector*, physical PDF page 10, industry and academic cohorts; page 12, technical skill gaps. [Official source](https://gfi-india.org/resource/smart-protein-skills-mapping/). The listing is dated 19 December 2025; the PDF is undated. Source ID `gfi_india_talent_landscape`; 20 industry and 19 academic respondents are cohorts, not workforce totals.
[^driver-jobs]: Retained aggregate inputs in `altprotein_proxy_inputs.csv`, source IDs `altprotein_jobs_vacancy_2023_2025` and `altprotein_jobs_company_directory_2024`; proxy methods §3.3. These records do not establish a national company census or independently verified board coverage. Original workbooks are not redistributed.
[^driver-model]: Retained [proxy specification](proxy.md), §§1, 3.3–3.4 and 6. Model-specification and missing-evidence statements are bounded to this package, not claims that no relevant evidence exists elsewhere.
