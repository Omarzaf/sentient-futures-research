# Source access and redistribution limits

Human verification pending. Source accessibility does not establish redistribution rights. Keep the original instrument, respondent-level files and downloaded publications in private working storage. This repository preserves authored code and source metadata, not permission to redistribute third-party files.

## India household survey

The official [HCES 2023-24 catalogue 237](https://microdata.gov.in/NADA/index.php/catalog/237) provides public metadata. Its microdata download route requires personal login or registration. The author must obtain any account-bound file; an agent must not register or submit a data request.

The author supplied [the hces_2023 repository](https://github.com/advaitmoharir/hces_2023). The inspected checkout is pinned at `4ad86c589c7b280309721af16fad4365c9810b04`. It contains fifteen cleaned Parquet levels, documentation and cleaning code. Its original raw-text directory is absent, no repository licence file was located, and its README links a different catalogue identifier. Use it as an explicitly identified third-party candidate. Matching survey counts and candidate hashes do not authenticate the omitted official raw bytes.

Inspect the checkout and its documentation before running anything. The research command does not execute its Stata scripts or notebook. Preserve the task's candidate manifest with each Parquet hash and the exact checkout commit.

The [official nutritional-intake report](https://www.mospi.gov.in/sites/default/files/publication_reports/Nutritional_Intake_in_India_L.pdf) supplies the target values and conversion methodology. The diagnostic pins its source hash. Table3.18R/U printed51 explicitly identifies the brief's61.8/63.4 as unadjusted; meal-adjusted61.2/62.9 is a separate estimand. Table2.2 already supplies the coarse-grain parent coefficients used by the physical join; a new variety-specific nutrient lookup is not required to reproduce that official composite. The completion code implements monetary-food conversion under a declared CPI interpretation. Section2.10.1 specifies the period and separate rural/urban indices but does not expressly identify the exact index family or demand an item-by-item crosswalk. No fitted correction or imputed unknown contribution is accepted. A separate observed-roster meal diagnostic localizes the discrepancy; numerical agreement does not validate its unadjusted-formula, membership or blank-field interpretation.

The cleaned household, food, survey-design and meal-count inputs already exist locally. The H roster and F household fields need their actual questionnaire codes and missingness semantics respected. These are implementation/cleaning tasks, not grounds to ask the author to supply the same processed dataset again. Original raw-text lineage and redistribution rights remain separate unresolved provenance issues. The local Git/data audit is recorded in [the current review](REVIEW-CODE-DATA-2026-10-16.md).

The completion code now implements all source-table physical and monetary coefficients. Normal unauthenticated GETs to the official MoSPI CPI API returned the historical rural/urban series during this session; `fetch_india_cpi.py` preserves the response pages and retrieval identity. Its Swagger also lists bearer authentication, so the captures establish observed accessibility rather than a permanent access promise. General CPI is a predeclared interpretation, with Food-and-Beverages retained as a separately named sensitivity. Neither is selected by target fit. A newly checked third-party CSV-import provenance document still requires a personal NADA API key for original unit files; it is not an unauthenticated raw-data route. No key was read or registration attempted.

## Pakistan household survey

The inspected public releases are linked below. Preserve their response metadata and exact byte hashes in a private input manifest before parsing:

- [Stata microdata archive](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Stata-data-1.zip)
- [HIES 2024-25 report](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-2.pdf)
- [Table 23 workbook](https://www.pbs.gov.pk/wp-content/uploads/2020/07/TABLE_23-2.xls)
- [Female questionnaire](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Female-Questionnaire-HIES-2024-25-English.pdf)
- [Instruction manual](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Manual-of-Instruction-HIES-2024-25.pdf)
- [Rural and urban coding scheme](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Coding-Scheme-HIES-2024-25-RUralUrban.xlsx)

The diagnostic requires all six inspected versions. A replacement response with a changed checksum is a new evidence identity requiring review. The report target, workbook value and microdata diagnostics are retained separately. The source conflict and sampling-stratum mapping remain unresolved. Do not select a consumption channel merely because it matches a target.

`pakistan_reconciliation.py` adds an independently read official SPSS archive, source-declared alternative/comparator checks and a genuine numerical target test. SPSS and Stata agree to storage precision, while the published report and standalone workbook disagree. Repeated report URLs with identical bytes are one source. The completed point comparator does not establish final survey variance or explain undocumented report processing.

## Other inputs

NFHS-5 unit-level data have not been obtained through the checked official routes. Record the actual access failures; do not infer that no dataset exists. The [World Bank NFHS-5 catalogue](https://microdata.worldbank.org/catalog/4482) describes DHS registration and project approval and restricts onward sharing without DHS consent. The [IIPS data-center page](https://iipsindia.ac.in/content/data-center) separately describes registration, identity proof and review for its general portal; NFHS-5 availability there has not been established. No account or request was submitted. Registration, paid access and external data requests require the author. Country comparability and the Pakistani equivalent remain separate research questions.

The elicitation instrument is author supplied for local work. Preserve its original bytes and the adaptation manifest; do not redistribute the document by default. US panel outputs and execution metadata have not been supplied. A questionnaire is not a dataset of completed forecasts.

The policy register records original official URLs and private capture hashes. Its frozen BioE3 source is explicitly an official summary brochure. A subsequent follow-up recovered [the full policy](https://bmi.dbt.gov.in/pdf/folder.pdf) and [the user-access companion](https://www.birac.nic.in/webcontent/1754376631_BioFoundries_Biomanufacturing_Hubs_User_access_policy.pdf) as supplemental evidence outside the first-round coding sample. Date precision, commencement and legal-version limitations remain. Its independent author-coding packet is generated privately; no agreement statistic exists before actual author coding.

Retail, trade, company and analogue sources require their own coverage, version and rights records. Missing or unattempted retrieval is not evidence of zero sales or absent products. Never treat upstream HS protein ingredients as an automatically equivalent consumer market.

The additional Pakistan documentation check inspected PDHS2017-18 women’s questions649–650 (youngest child previous-day foods) and NNS2018 section6.4 (women’s previous-day dietary diversity). These do not establish the requested respondent-level weekly NFHS-equivalent outcome. Original document identities and boundaries are retained in `market/reviews.json`; unit data and caste comparability remain unresolved.
