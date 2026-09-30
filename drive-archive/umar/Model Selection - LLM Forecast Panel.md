# 14 Sept 2026  

# **Umar — Scope Note (as of 14 Sept 2026)**

This replaces the three-workstream draft in the earlier Personal Research Plan v1. Scope below reflects the team's internal alignment; mentor sign-off still pending.

## **Shared workstream**

Supporting Anna's LLM forecast-elicitation methodology — the multi-model questionnaire used as a Delphi-style superforecaster-panel proxy. Reviewing the methodology doc and questionnaire design; flagging protocol issues (source-quality checks, independent first rounds, model identification, disagreement vs. predictive uncertainty).

## **Solo deliverable**

Comparative brief: India vs. Pakistan — socio-cultural drivers of protein consumption and alt-protein market futures.

  

**Axes:**

  

  - Religion-driven dietary norms — India's large vegetarian/Jain population as an existing plant-protein base, vs. Pakistan's Halal-majority meat-centric culture
  - Caste and class as determinants of who can afford alt-protein at price parity
  - Urbanization and diaspora-driven demand signals
  - The policy-attention gap between the two states — India has an active biotech/food-tech push; Pakistan has close to none. This is the sharpest single finding candidate.

  

Format: standalone comparative policy brief, \~5-10 pages, written to also function as a chapter in the team's shared report.

Framing note: policy treated primarily as a driver of the transition in this project, secondarily as an outcome.

## Open questions for the mentor call

1.  Confirm India–Pakistan as the solo lane.
2.  Is there a South Asia-specific data source (Tälist/AltProtein.Jobs or otherwise) worth pointing me toward?
3.  What does "done" look like for this piece specifically by 13 Nov?

  
  
  

# Model Selection — LLM Forecast Panel  

**Model Selection — LLM Forecast Panel**

**Sentient Futures — AI and the Protein Transition | Zafar × Anna workstream**

Sep 16, 2026 · @Zafar · Budget: $300 compute credits · Target: 10 frontier models

## **What I'm choosing for**

We're running Anna's questionnaire across a panel of LLMs as a superforecaster-panel — Delphi-style elicitation, where the models stand in for a forecaster panel.

That means the selection logic is going to be based on whose disagreements are informative. A panel of ten near-identical American frontier models would give us ten correlated opinions dressed up as ten data points. For genuine diversity of training lineage, corpus, and geographic prior, spread across a capability range we can afford to run at volume.

So I'm optimizing three things at once: **reasoning quality** (the models need to produce defensible rationales, not just point estimates), **provenance diversity** (different labs, different data, different national priors, which matters directly for an India–Pakistan food-and-policy question), and **cost fit** (the $300 has to cover enough passes to be statistically meaningful).

## **The panel: 5 US / 3 Chinese / 2 European**

|  |  |  |  |  |
| :-: | :-: | :-: | :-: | :-: |
| \*\*\\\#\*\* | \*\*Model\*\* | \*\*Lab\*\* | \*\*Region\*\* | \*\*Role on the panel\*\* |
| 1 | Claude Opus 4.8 | Anthropic | US | Reasoning anchor; premium, low-volume |
| 2 | GPT-6 | OpenAI | US | Best US Flagship |
| 3 | GPT-5.6 Sol | OpenAI | US | Reasoning tier,  within-lab capability control |
| 4 | Grok 4.6 | xAI | US | Distinct RLHF/web-native prior |
| 5 | Gemini 3.1 Pro | Google | US | Third US lineage; 1M-token context for long dossiers |
| 6 | DeepSeek-V4 | DeepSeek | China | High-volume workhorse (\\\~50x cheaper output); distinct Global South prior |
| 7 | Qwen3.8-Max | Alibaba | China | 2.4T flagship; strong multilingual/South Asian grounding |
| 8 | GLM-5.3 | Z.ai | China | Third Chinese lineage, lets us test clustering |
| 9 | Mistral Medium 3.5 | Mistral | Europe | Only viable EU frontier lab; multimodal merged model |
| 10 | Mistral Large 3 | Mistral | Europe | 675B MoE, within-lab EU capability comparison |

  

## **One Last thing:**

  - On twitter, I saw the release of a new model, by a former OpenAI founding team member. We could also give that a try. The interesting thing about it is the use case, it is designed on Agentic feedback learning based on statistical weights rather than Human as a feedback mechanism.
  - I will add the name soon, researching it for now.

<https://typesafe.ai/> check this

  

# Anna

Here’s the method of model selection I suggest:

  - Begin here, a sound ranking of LLM’s forecasting ablities: <https://www.forecastbench.org/>
  - From this I would pick the top one from each different company (minus minimax). I think this approach prioritises accuracy in forecasting with a nod to diversity of models as well
  - That gives:
      
      - claude-sonnet-4-6-adaptive-thinking-16000 
      - OpenAI o3-2025-04-16-scratchpad
      - grok-4.20-0309-reasoning 
      - gemini-2.5-pro-preview-03-25 
  - So we have 4, and perhaps we can add deepseek-r1-scratchpad as well, but it’s much farther down the leaderboard
  - Other models to consider would be [Cassi.AI](http://cassi.ai) and Torchcast, since these are specifically developed for forecasting, but they are not yet publically available, therefore I wouldn’t include them.

  
  

## Final methodology: 

  - Maximising diversity with geographical choices, and then from these categories selecting those ranked highest on forecasting

Final choices:

  - 1 US closed
  - 1 US open
  - 1 china closed
  - 1 china open
  - Mistral
  - (potential cassi)
  - Gev - is practically free   

# Conditional Markets  

21 SEPTEMBER 2026

**Conditional Markets for Cultivated Chicken**

*Updated research report and source audit*

Prepared for Muhammad Umar Zafar  |  Review date 21 September 2026

This report reviews the supplied 20 September 2026 paper together with the Sentient Futures research repository, including the newer India–Pakistan branch. It updates the substantive argument, checks the available data and citations, and specifies the evidence still needed for a defensible market or animal welfare estimate.

The central conclusion survives review: cultivated chicken has conditional pathways through religious interpretation, certification, food regulation, production and purchasing. The available evidence does not establish blanket halal acceptance, permission to sell a particular product in all four focal markets, scalable supply, representative demand, or net reductions in animal production.

**Decisions supported by the review**

Retain India, Pakistan, Saudi Arabia and the UAE as institutional case studies. Use Singapore, Malaysia and Indonesia as scoped precedents. Do not turn these cases into a readiness league table.

Keep cultivated chicken separate from the repository’s proposed plant-based consumer pilot. Plant-based trials may generate useful local evidence, but their adoption rates cannot calibrate cultivated chicken demand.

Keep the scenario output uncomputed until a compatible demand baseline, product decisions and supply allocations exist. Missing information is not zero demand.

Publish a reproducibility repair before describing the PDF model as independently verified. Its claimed 23 tests and supporting evidence files are absent from both repository snapshots inspected.

The most useful additions are verified Pakistan household food quantities, a clearer distinction between adjusted and unadjusted Indian nutrient estimates, an official Malaysian religious discussion, and a more explicit route from product sales to animal outcomes. Existing correct cautions and corrected consumer percentages are preserved.

Read sections 1–3 for the review findings and decision framework, sections 4–9 for the updated evidence, and sections 10–11 for the research and repair plan. Appendices contain the full stored country dataset, all 54 PDF reference dispositions, and all 159 repository catalog retrieval results.

Status: AI-assisted research review. No new consumer experiment, laboratory validation, regulatory opinion or independent human scholarly review was conducted. Evidence access and remaining uncertainties are stated where they affect a conclusion.

**1 What the review established**

|  |  |
| :-: | :-: |
| \*\*Finding\*\* | \*\*Evidence and implication\*\* |
| Repository integrity passes | The main snapshot passed 2,218 existing checks; the newer branch passed 2,432. These validate packaging, internal references and specified arithmetic, not the truth of every research claim. |
| The PDF has a reproducibility gap | The paper describes executable scenarios, 23 tests, evidence tables and review records that were not present in either inspected snapshot. The report’s methodological description can be evaluated, but its implementation cannot be reproduced from this repository. |
| The research scope has changed | The main branch treats India–Pakistan work as proposed. The newer branch contains a completed brief recommending a plant-based urban pilot. The PDF instead studies cultivated chicken across four jurisdictions. |
| The numerical data need separate denominators | Food-balance supply, household nutrient estimates, food quantities, expenditure shares and hypothetical purchase intentions answer different questions. A single combined demand score would be misleading. |
| The reference system is navigable | All 54 source codes extracted from the PDF resolve to linked bibliography entries. The original Bryant study and its correction are one evidence family, not two independent studies. |
| Access is incomplete | For the repository catalog, 94 URLs returned text, 4 returned only limited or challenge content, and 61 could not be retrieved. Text returned can mean metadata or an abstract; it is not full verification. |

These findings support a revised working report rather than a claim that the entire literature has been independently replicated. All source URL checks were attempted, and decision-critical claims were inspected in available primary material. The breadth of the repository exceeds the set of claims for which full-text methods, underlying datasets and current legal instruments could be rechecked.

**Corrections and additions**

The PDF already uses the corrected Indian willingness figures and already refuses to output a forecast without a baseline. Those are strengths to retain. The material changes are to qualify the unreproduced model-validation claim, connect the branch’s household evidence to this report, add a named Malaysian source rather than a general national judgment, and make the animal-impact mechanism explicit.

Several bibliography entries can be completed. The FAO webinar page is dated 29 March 2024, although the event it describes occurred in April 2023. The Chong study belongs to Future Foods 9, article 100326, June 2024. Ahsan and colleagues’ article is in volume 2 issue 1, 2022, pages 111–122; the repository records an earlier online publication date. Keep online and issue dates distinct. The Risner paper similarly needs its online date distinguished from its journal issue year.[ \[CO-S04\]](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en)[ \[CO-S10\]](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/)[ \[CO-S08\]](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766)[ \[R-IP\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/india-pakistan/india-pakistan-brief.md)

**2 Materials and verification boundaries**

The supplied PDF, Conditional Markets for Cultivated Chicken, is dated 20 September 2026 and contains 25 pages: 14 main pages, four appendix pages and seven reference pages. Its SHA256 is 04dc5ca193c8ceaace2b4cbfce1ee806d93f0239a7c488f478f46ee8f784f217. The review used the supplied file, not an assumed repository copy.

|  |  |  |
| :-: | :-: | :-: |
| \*\*Snapshot\*\* | \*\*Pinned revision\*\* | \*\*Review result\*\* |
| Main | fc13b3bcf1287df372c673bf2814d0aff1a7bf95 | 45 packaged files; five documents; 143 source identities; 104 original source-register records.\[ \\\[R-MAIN\\\]\](https://github.com/Omarzaf/sentient-futures-research/tree/fc13b3bcf1287df372c673bf2814d0aff1a7bf95) |
| India Pakistan branch | 9896751e53c1b851a874153cbdf6cd72c217058a | 49 packaged files; six documents; 159 source identities; 124 original source-register records.\[ \\\[R-BRANCH\\\]\](https://github.com/Omarzaf/sentient-futures-research/tree/9896751e53c1b851a874153cbdf6cd72c217058a) |

The second revision is from codex/consolidated-india-pakistan. Local review copies were matched against the remote Git blob hashes, and each snapshot’s existing verification script was run without editing its research content. This report does not modify or merge either branch. The older branches were not separately audited beyond the material represented in these snapshots.

The newer catalog combines 60 comparative-protein records, 44 AI/protein records and 20 India–Pakistan records, plus links from the orientation material. Its 159 identities are a navigation inventory, not 159 independent empirical studies. Exact nonempty DOI duplicates were not found in that consolidated catalog; semantic duplicates, versions and overlapping evidence still require judgment.[ \[R-CATALOG\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/sources/catalog.json)

The review distinguishes four levels: internal integrity; external URL retrieval; claim-level inspection of accessible primary text; and empirical replication. The first two were broad. The third focused on claims that affect the argument. The fourth was not possible without original survey data, production records, the missing scenario package and authoritative product decisions. No search was an exhaustive multilingual legal or systematic literature review.

**3 Define the product and decision before the market**

The appropriate unit is a specified product and process, considered by a named institution, for a jurisdiction, channel, consumer segment and date. “Cultivated meat is acceptable” is too broad to function as a regulatory, religious or commercial variable. A finding for one donor source, cell bank, medium or formulation should not automatically transfer to another.

|  |  |
| :-: | :-: |
| \*\*Product profile\*\* | \*\*Information that determines the next decision\*\* |
| Traced slaughter-origin cells | Document species, donor and slaughter chain, tissue, cell-bank establishment, all media and processing inputs, production site and final formulation. |
| Cells from a living animal | Resolve the named authority’s treatment of tissue removal and donor status. Do not infer permission from guidance that addresses a different cell source. |
| Legacy bank with incomplete history | Record the unknown historical inputs. A later serum-free production phase does not reconstruct the earlier provenance. |
| Hybrid finished product | Disclose cultivated fraction and every other ingredient. Approvals, certificates, nutrition, cost and substitution concern the finished product as well as its cultured component. |

Use a sequence of separate questions: Is the proposed process religiously permissible under the relevant interpretation? Can the product and site obtain an applicable certificate? Is the certifier recognized for the destination and scope? Is food approval granted for that product and process? Are import, labeling and channel requirements satisfied? Can dependable supply be delivered at the relevant price? Do people purchase it repeatedly, and what does it replace?

Each record should retain the institution, document version, effective date, product and process identifiers, territorial scope, conditions and evidence locator. Unknown, pending, conditional, approved and refused are different states. A blank registry search cannot establish a prohibition or a universal absence of applications.

**4 Religious evidence remains institution specific**

**International Islamic Fiqh Academy**

Resolution 265 was adopted during the May 2025 session; the inspected English webpage is dated 20 November 2025. It sets conditions concerning cell origin, permissible inputs, credible supervision, disclosure and safety. Its wording about live animals and slaughter where required needs qualified interpretation for a specific tissue source; this review does not convert it into a universal live-biopsy permission. Its statement favoring use alongside conventional meat is a normative position, not an estimated numerical displacement ceiling.[ \[CO-S01\]](https://iifa-aifi.org/en/56085.html)

**Singapore MUIS**

MUIS’s February 2024 statement permits cultivated meat subject to halal animal origin, halal ingredients and a clean, non-toxic final product. A general fatwa does not certify every product. The statement also acknowledges that consumers may consider taste, price and preference. Religious permissibility therefore cannot stand in for observed purchasing or issuer-specific trust.[ \[CO-S02\]](https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/)

**Malaysia source added to the review**

The Federal Territories Mufti Office published Irsyad Hukum 595 on 24 July 2021. For land animals, its discussion distinguishes tissue from lawful slaughter from tissue taken while the animal is alive or after death without the required slaughter. It also addresses prohibited material and harm. This adds a named, inspectable Malaysian interpretation to the evidence base. It is not proof of a product certificate, an operative national approval or consensus among all Malaysian authorities.[ \[A02\]](https://muftiwp.gov.my/en/artikel/irsyad-fatwa/irsyad-fatwa-umum-cat/4887-irsyad-al-fatwa-siri-ke-595-daging-kultur-cultured-meat-menurut-perspektif-syarak)

This paragraph is an AI-assisted interpretation of the Malay original, not a certified translation. A Malaysian reviewer should confirm its doctrinal and institutional application. The separate JAKIM CIRi record cited in the PDF could not be retrieved in this review; the new source does not silently replace it.[ \[GP-S17\]](https://ciri.islam.gov.my/view/fatwa_cetak.php?id=16914)

**Company reported advice and recognition agreements**

GOOD Meat’s 2023 announcement describes advice obtained from scholars. It should remain labeled a company account of religious advice, not a Saudi regulator’s permit or a current product certificate. The PDF’s detailed process-compliance interpretation was not independently re-established from the announcement text during this review.[ \[GP-S01\]](https://www.goodmeat.co/all-news/leading-shariah-scholars-rule-cultivated-meat-can-be-halal)

MUIS’s annual report confirms halal recognition MoUs with Saudi Arabia, the UAE and Jordan. That verifies institutional cooperation; it does not establish that a particular cultivated product lies within recognized scope. Indonesia’s Decree 221/2025 also shows why recognition and destination registration must be recorded separately.[ \[GP-S08\]](https://isomer-user-content.by.gov.sg/48/c463da6b-c40f-4595-b13e-2ec8b5e672dc/Muis%20Annual%20Report%202023.pdf)[ \[GP-S18\]](https://cmsbl.halal.go.id/uploads/Decree_Kepkaban_221_2025_Implementation_Procedure_of_Foreign_Halal_Certificate_Registration_bb95097144.pdf)

**5 Regulatory pathways and unresolved product decisions**

This section reports the inspected institutional evidence and the questions that remain. It does not establish legal clearance for a particular commercial product. Dated registers and guidance must be checked again against the actual application, process and intended channel before a market-access variable is assigned.

|  |  |  |
| :-: | :-: | :-: |
| \*\*Jurisdiction\*\* | \*\*What is supported\*\* | \*\*What is still required\*\* |
| India | FSSAI’s non-specified food regulations provide an application and prior-approval framework. The March 2026 application register is a dated administrative snapshot.\[ \\\[SA-S09\\\]\](https://www.fssai.gov.in/upload/uploadfiles/files/Gazette\_Notification\_NonSpecified\_Food\_Ingredients\_15\_09\_2017.pdf)\[ \\\[SA-S10\\\]\](https://fssai.gov.in/upload/uploadfiles/files/Compendium\_FSS\_NFS\_FA\_17\_10\_2022.pdf)\[ \\\[SA-S11\\\]\](https://fssai.gov.in/upload/uploadfiles/files/Status\_of\_Application\_as\_on\_09\_03\_2026.pdf) | A current, named cultivated-chicken decision; exact formulation and process scope; manufacturing or import conditions; labeling and channel requirements. |
| Pakistan | The Pakistan Halal Authority Act and Punjab Food Authority Act identify relevant institutions and powers. Federal trade and provincial food responsibilities need separate treatment.\[ \\\[SA-S03\\\]\](https://faolex.fao.org/docs/pdf/pak164529.pdf)\[ \\\[SA-S08\\\]\](https://faolex.fao.org/docs/pdf/pak115231.pdf) | Current commencement and amendments, operative product route, applicable provincial rules, import conditions, certifier scope and a product-level decision. |
| Saudi Arabia | SFDA guidance explicitly addresses novel foods, including cell or tissue sources, and an application process. Halal conditions coexist with food review.\[ \\\[GP-S02\\\]\](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf)\[ \\\[GP-S03\\\]\](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf) | An authoritative current dossier route, the product approval, recognized certification scope, registration and import conditions; Arabic controlling text where applicable. |
| United Arab Emirates | Codex country material describes a premarket route; Abu Dhabi announced a novel-food initiative in October 2025. These establish institutional activity.\[ \\\[GP-S23\\\]\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/fr/?lnk=1\&url=https://workspace.fao.org/sites/codex/Meetings/CX-701-47/CRDs/cac47\_crd04x.pdf)\[ \\\[GP-S11\\\]\](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework) | Operative federal and emirate requirements, current standards and certification registers, and a named product authorization for the planned sale or import. |

**India**

The i-CAS Halal material and DGFT export conditions concern specified export products and destinations. They do not, by themselves, create a domestic cultivated-food approval. The inspected PC 048 accreditation page has a defined conventional animal-product scope and validity period; it cannot be extended to cultivated chicken by analogy. The February 2026 DGFT amendment was located but its text could not be retrieved, so the current consolidated export position remains unresolved.[ \[SA-S12\]](https://i-cas-halal.qcin.org/)[ \[SA-S13\]](https://content.dgft.gov.in/Website/Notification_ITCHS.pdf)[ \[SA-S14\]](https://content.dgft.gov.in/Website/dgftprod/25fb264d-cd73-40f5-851f-31b5263357ef/Notification%2059%20dated%2009.02.26.pdf)[ \[SA-S15\]](https://nabcb.qci.org.in/pc-048/)

India’s BioE3 program supplies a separate research-policy signal. An official parliamentary answer of 23 July 2026 reports nine supported smart-protein projects across fermentation, plant-based and cell-culture categories. That is evidence of support, not nine cultivated-chicken approvals or commercial plants. Biokraft’s website is company evidence and should not be used as audited output or operating capacity.[ \[A03\]](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306)[ \[SA-S16\]](https://www.biokraftfoods.com/)

**Pakistan**

The 2016 Act’s application and commencement provisions deserve particular care: some provisions concerning regulated activity depend on notification. The 2025 mark-scheme image, current PNAC list and cited Import Policy Order could not be reread in this review. Do not infer that an institution’s existence settles commencement, certifier recognition or a cultivated-product classification. A current regulatory map should identify the federal trade role and the relevant provincial food authority for the actual site and channel.[ \[SA-S03\]](https://faolex.fao.org/docs/pdf/pak164529.pdf)[ \[SA-S04\]](https://pakistanhalalauthority.gov.pk/Files/PHA%20Halal%20Mark%20Scheme%20operationalization%20notification.jpg)[ \[SA-S05\]](https://pnac.gov.pk/Halal-Certification-Bodies/Active)[ \[SA-S07\]](https://logcluster.org/sites/default/files/public/2022-10/pakistanimport-policyministry-commerce22-april-2022-compressed1-compressed.pdf)[ \[SA-S08\]](https://faolex.fao.org/docs/pdf/pak115231.pdf)

**Saudi Arabia and the UAE**

The SFDA novel-food documents show a real route for review, but the cited general-requirements cover and application guide use different identifier presentations. Preserve the source version and obtain confirmation of the controlling standard rather than silently normalizing them. The 2023 recognized-body list is historical; the 2026 English registration-guide URL did not return its text. Neither can establish today’s approval or recognition for a named product.[ \[GP-S02\]](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf)[ \[GP-S03\]](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf)[ \[GP-S04\]](https://www.sfda.gov.sa/sites/default/files/2026-08/SFDA-FRigsterE.pdf)[ \[GP-S06\]](https://www.sfda.gov.sa/sites/default/files/2023-11/511hala.pdf)

For the UAE, the WAM report describes an initiative and expected time savings; it does not measure realized review times. The ADIO–Believer announcement records a development plan, not proof that a commercial facility is now operating. Federal legislation and the MOIAT pages were not accessible in this check. Their absence from the retrieved evidence must remain a gap, not a claim that no requirements exist.[ \[GP-S11\]](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework)[ \[GP-S12\]](https://investinabudhabi.gov.ae/News/AGWA-and-Believer-Meats-to-Develop-Cultivated-Meat-Capabilities-in-Abu-Dhabi)[ \[GP-S09\]](https://www.moiat.gov.ae/en/programs/halal)[ \[GP-S10\]](https://moiat.gov.ae/en/programs/halal/registered-halal-certification-bodies)[ \[GP-S20\]](https://www.uaelegislation.gov.ae/en/legislations/1161/download)[ \[GP-S21\]](https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips)

**Singapore and Indonesia as bounded precedents**

Singapore’s current guidance requires renewed approval for manufacturing changes that affect the safety assessment, including changes to cell lines or medium components, and for expanded uses. An old approval cannot automatically travel with a reformulated product. Indonesia’s 2025 decree requires registration of qualifying foreign halal certificates before circulation; a bilateral MoU alone does not complete that step. These are precedents for how to structure records, not transferable permission to sell elsewhere.[ \[GP-S14\]](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food)[ \[GP-S15\]](https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Subsidiary%20Legislation%20Supplement/713.pdf)[ \[GP-S18\]](https://cmsbl.halal.go.id/uploads/Decree_Kepkaban_221_2025_Implementation_Procedure_of_Foreign_Halal_Certificate_Registration_bb95097144.pdf)[ \[GP-S19\]](https://www.muis.gov.sg/resources/media-releases/8-aug-24-singapore-signs-halal-cooperation-memorandum-of-understanding-with-indonesia/)

**6 Consumer evidence and household food data**

**What the consumer studies can answer**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Evidence\*\* | \*\*Finding that can be retained\*\* | \*\*Boundary\*\* |
| India Bryant survey and correction | For the Indian panel, 56.3% were very or extremely likely to buy clean meat, versus 62.8% for plant-based meat. The PDF already uses the corrected figures.\[ \\\[CO-S06\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full)\[ \\\[CO-S07\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2020.00086/full) | Hypothetical intention in a panel, not national market share, repeat purchasing, willingness at a verified price, or the effect of halal certification. |
| Pakistan Ahsan study | A Pakistan consumer study predates the 2026 article. Publication metadata supports retaining it in the evidence history.\[ \\\[CO-S08\\\]\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766) | Full methods were not re-obtained in this review. The branch reports sample limitations and inconsistent acceptance measures; its estimates are not newly verified here. |
| Pakistan Irfan study | Publisher material and the accepted manuscript describe a 102-person sample.\[ \\\[CO-S09\\\]\](https://www.nature.com/articles/s41598-026-62416-3)\[ \\\[A04\\\]\](https://www.nature.com/articles/s41598-026-62416-3\_reference.pdf) | The abstract and introductory material were inspected; full methods and data were not independently verified. Its claim of first empirical evidence is contradicted by the earlier study. |
| Singapore tasting study | The author record describes 107 diners in a 2023 on-site tasting study.\[ \\\[CO-S10\\\]\](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/) | A tasting sample does not establish representative demand, long-run repurchase, price elasticity or a causal effect of a religious issuer. |
| UAE consumer study | Retain as exploratory consumer evidence within its stated sample and method.\[ \\\[CO-S16\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11722975/) | The PDF reports 577 convenience and snowball respondents. Detailed methods and that count were not freshly verified here; no national acceptance parameter is assigned. |

These studies should not be pooled into one acceptance percentage. They differ in product description, sampling frame, exposure, language, outcome, timing and whether respondents tasted a product. A comparable synthesis would extract wording, denominators, recruitment, exclusions, weighting, missingness, confidence intervals, preregistration, funding and conflicts for each study. A sample size alone does not make two estimates comparable.

The older Ahsan record also prevents a false novelty claim from propagating into the updated report. The 2026 article’s existence is verified, but neither a publisher record nor an accepted-manuscript abstract is a substitute for checking questionnaire construction and analysis. Access limits stay attached to the affected claim.

**India household nutrition**

The official July 2025 release gives two versions of the 2023–24 household-derived protein estimate. Use the adjusted values for the corresponding adjusted series; retain the unadjusted values only with their label. Both are survey-derived nutrient estimates, not individual dietary recalls.[ \[A01\]](https://mospi.gov.in/sites/default/files/press_release/press_note_Nutritional%20Intake%20in%20India_02072025.pdf)

|  |  |  |
| :-: | :-: | :-: |
| \*\*India 2023 to 2024 measure\*\* | \*\*Rural\*\* | \*\*Urban\*\* |
| Unadjusted protein g per person per day | 61.8 | 63.4 |
| Adjusted protein g per person per day | 61.2 | 62.9 |
| Cereals as percent of reported protein | 45.9% | 38.7% |
| Egg fish and meat as percent of reported protein | 12.4% | 14.1% |

Source locators: Table 3, printed page 7, for adjustment; Figures 5R and 5U, page 5, for food-group shares. The egg/fish/meat category excludes dairy and is not the entire animal-protein share. Its denominator differs from FAO food-balance supply.[ \[A01\]](https://mospi.gov.in/sites/default/files/press_release/press_note_Nutritional%20Intake%20in%20India_02072025.pdf)

The PDF also quotes HCES expenditure values from Report 592. The original report URL did not return the document in this review, so those rupee values are not republished as freshly checked figures. The source remains in the audit. NFHS frequency findings in the repository likewise should remain frequency evidence, not grams consumed or a direct vegetarian-identity measure.[ \[SA-S18\]](https://mospi.gov.in/sites/default/files/publication_reports/Final_Report_HCES_2023-24L.pdf)[ \[R-IP\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/india-pakistan/india-pakistan-brief.md)

**Pakistan household food quantities**

Pakistan’s HIES 2024–25 supplies direct household context. The following values are transcribed from Table 3.7.C, printed page 25, PDF page 42. They describe monthly food quantities per person, not cultivated demand or grams of protein.[ \[SA-S17\]](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf)

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Food and unit per person per month\*\* | \*\*Urban\*\* | \*\*Rural\*\* | \*\*Total\*\* |
| Wheat and wheat flour kg | 5.76 | 7.12 | 6.59 |
| Pulses kg | 0.27 | 0.25 | 0.26 |
| Milk litres | 6.12 | 6.17 | 6.15 |
| Chicken meat kg | 0.41 | 0.29 | 0.34 |
| Eggs number | 3.44 | 2.44 | 2.83 |

Use the tabulated quantities rather than the nearby generalization that urban consumption is higher across examples; milk is slightly higher in the rural column. Survey coverage, weights and item definitions must be recovered before microdata replication or population extrapolation. The monthly chicken quantity should not be treated as total national chicken supply or multiplied by an intention percentage to create a cultivated market forecast.[ \[SA-S17\]](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf)

**Food balance data and affordability**

The repository’s FAO-derived table contains 12 populated country cases and one missing Singapore row. Pakistan is absent. Stored plant-protein values equal total minus animal protein, and animal shares reproduce to the shown precision. The underlying FAO Table 50 could not be re-downloaded in this review, so this is a successful arithmetic check, not fresh external transcription verification. Appendix A preserves the values and provenance.[ \[R-DATA\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/comparative-protein/protein-data.csv)

The practical consumer unit should be a meal and purchase occasion. Record disposable food spending, household size, cooking facilities, preparation time, product format, cold-chain access and the alternative actually available. Compare cultivated chicken with local chicken dishes and relevant plant foods, not only premium imported substitutes. Currency conversion cannot replace a local affordability comparison at a dated price.

**7 Production economics environmental effects and safety**

**Production claims require a complete process boundary**

A laboratory growth result, pilot batch, announced factory and sustained commercial output are different observations. A usable production record needs viable cell yield, doubling time, medium recipe and grade, transfer efficiency, contamination losses, downtime, utilization, downstream losses, quality acceptance and the final formulation. Preserve unsuccessful runs and supplier assumptions as well as the best result.

Serum-free is not automatically animal-component-free, chemically defined, food-grade, affordable or halal-compliant throughout the cell-bank history. The Schenzle paper addresses alternatives to serum albumins in FBS-free media; its title and research record do not certify an industrial chicken process. The PDF’s detailed historical-input claim still needs full-methods confirmation. General culture-media guidance likewise cannot determine food or religious compliance.[ \[CO-S15\]](https://www.nature.com/articles/s41598-025-99603-7)[ \[CO-S05\]](https://www.thermofisher.com/us/en/home/references/gibco-cell-culture-basics/cell-culture-environment/culture-media.html)

**One verified retail example**

GOOD Meat’s May 2024 announcement describes a 120 g pack priced at SGD 7.20, with 3% cultivated chicken. Dividing the pack price by its finished mass gives SGD 60 per kg of finished product. If the declared percentage is a mass fraction, the pack contains 3.6 g of cultivated component. Neither calculation is the production cost or selling price of pure cultured biomass. The announcement is a dated company launch record, not evidence of continued availability in September 2026 or profitable sales volume.[ \[CO-S11\]](https://www.goodmeat.co/all-news/good-meat-begins-the-worlds-first-retail-sales-of-cultivated-chicken)

**Economics and environmental comparisons**

Humbird’s scale-up analysis, Sinke’s prospective 2030 assessment and Risner’s cradle-to-gate assessment concern modeled systems with different assumptions. Their results should remain scenario-specific. This review does not freshly reproduce their inventories or claim a universal numerical advantage over chicken. The Risner full text was not accessible through the cited link during this audit.[ \[CO-S12\]](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/bit.27848)[ \[CO-S13\]](https://ce.nl/wp-content/uploads/2023/01/CE_Delft_200220_Ex-ante-LCA-of-commercial-scale-CM-production-in-2030_FINAL_2.pdf)[ \[CO-S14\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC11744764/)

The next comparison should state electricity and heat sources, medium purity, yield, utilization, capital assumptions, financing, waste treatment, transport and the conventional comparator. Use a finished-product kilogram, an edible serving and an appropriate protein or nutritional basis where data permit. Keep the cultivated fraction explicit. A beef comparator alone does not answer a cultivated-chicken decision, and a future clean-energy case is not the current local grid.

A claim about net environmental benefit also needs deployment and displacement. Calculate impacts of the alternative actually sold, subtract the impacts of the food actually displaced, and include additional consumption or rebound. Avoid combining the most favorable assumptions from incompatible production systems. Report sensitivity to uncertain parameters rather than a single apparently precise cost or emissions figure.

**Safety nutrition and product stewardship**

FAO and WHO’s 2023 report is a relevant foundation, but the full report was not successfully obtained in this review; the accessible institutional summaries do not establish the safety of an individual product. Singapore’s guidance explicitly asks for evidence on toxicity, allergenicity, production methods and dietary exposure.[ \[CO-S03\]](https://www.who.int/publications/i/item/9789240070943)[ \[CO-S04\]](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en)[ \[GP-S14\]](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food)

For a proposed dossier, document cell identity and stability, microbiological controls, residual processing substances, scaffold and medium inputs, allergens, validated cleaning, traceability, storage conditions and shelf life. These are review questions, not findings that every listed hazard is present. Define release criteria, recall responsibility and the change-control process for reformulation.

Measure the finished product’s composition and serving size. Assess protein quality where relevant, sodium, fats, fortification, allergens and the meal displaced. “Animal-free,” “healthy,” “equivalent to chicken” and “nutritionally superior” each need their own substantiation. None follows automatically from cultivation technology or a halal determination.

**8 Implications for the wider repository**

The AI/protein review, comparative synthesis and orientation material remain useful background, but they answer broader questions than the cultivated-chicken PDF. Their own methodology appropriately labels the work a selective scoping synthesis, with pending human verification. The updated report retains those boundaries.[ \[R-AI\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/ai-protein/literature-review.md)[ \[R-METHOD\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/RESEARCH-METHOD.md)

**AI and the production counterfactual**

Evaluate AI against a suitable non-AI workflow using held-out performance, experiments required, reproducibility, usable yield and cost at the relevant scale. A protein-structure prediction or media-optimization result should not be converted directly into lower retail prices or fewer animals. The conventional sector’s technology also changes; a stationary incumbent comparator can overstate the alternative’s advantage. These are proposed evaluation standards, not newly measured effects.

**Forecasting methods**

Repeated model responses are not independent empirical observations. A spread of answers is not a calibrated prediction interval. A forecasting pilot needs resolvable questions, source cutoffs, model versions, aggregation rules and scores on resolved outcomes. Historical tests using current models can be contaminated by prior training exposure. Keep exploratory scenarios separate from probabilities, and score source reliability separately from forecast accuracy. These distinctions are already present in the repository and should survive any condensed presentation.[ \[R-AI\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/ai-protein/literature-review.md)

**Capabilities market claims and policy evidence**

The comparative dataset’s 14 capability locations mark documented institutions or programs. They do not measure the size of a workforce, vacancies, labor shortages or national technical readiness. A map should preserve approximate-location labels and evidence type. A workforce claim requires occupation-specific demand, skills, time to hire and evidence that missing staff delay production.

Orientation sources include advocacy reports, company announcements and public career information. Record the publication year separately from the year of activity, the category boundary and the original data provider. Broad plant-based-food sales are not plant-based-meat sales. Funding commitments, awards, disbursements, private investment and operating infrastructure are different quantities. This review checked their catalog links but did not re-estimate those market or employment statistics.

Policy recommendations should be conditional on a demonstrated constraint and an observable outcome. Shared pilot infrastructure, public data and regulatory support may be useful, but their marginal value requires costs, additionality, alternatives and local delivery evidence. Include nutrition, affordability, farmer and worker transitions, ownership of technology and access to benefits alongside animal welfare. Do not assume advanced biomanufacturing must be the best use of every research or policy budget.

**9 Scenario design and animal outcomes**

**A defensible model contract**

The PDF’s proposed scenario structure is reasonable only under its stated baseline contract: reference demand must describe full access and acceptance before the new adjustments. If the baseline already incorporates those constraints, multiplying by them again double-counts their effects. The baseline owner must confirm units, product category, price, year, segments, channels and partitions before the model runs.

|  |  |
| :-: | :-: |
| \*\*Input or output\*\* | \*\*Required interpretation\*\* |
| Reference demand D | Finished-product kg per year at a stated price, product and market definition. Not population multiplied by willingness to try. |
| Legal access L | A scoped 0 or 1 only when supported; otherwise unknown. An application or general pathway does not equal 1. |
| Acceptance factor H | A defined fraction from 0 to 1, or unknown. Religious eligibility and ordinary consumer preference must not be counted twice. |
| Allocated supply K | Saleable finished-product capacity allocated across markets and channels; shared supply cannot be assigned in full to each market. |
| Realized sales Q | Limited by both eligible demand and allocated supply. Calculate only for compatible, non-overlapping records. |
| Cultivated fraction | A separate formulation field for biomass accounting, nutrition and environmental inventory; it is not a displacement coefficient. |
| Missing output | A reason-coded non-result such as blocked\\\_missing\\\_baseline. Do not silently substitute zero or manufacture probability estimates. |

In words, calculate adjusted demand within each disjoint segment by applying the supported access and acceptance factors to reference demand. Sum only compatible segments, then limit sales to the supply allocated to that market. Validate shared supply pools, product and price compatibility, nonnegative quantities and unknown values before any aggregation. The research question must specify whether the output is potential demand, orders, fulfilled sales or consumption.

**From sales to animal welfare**

Finished-product sales do not equal animals spared. First measure which conventional foods decline relative to a credible counterfactual. Then estimate how that demand change affects production after trade, inventory, prices and supply response. Finally convert the production change by species using appropriate edible yields and welfare assumptions. Track donor animals and other animal-derived production inputs separately.

For a hybrid product, the cultivated fraction determines biomass use but does not mechanically determine what the finished meal displaces. A 3% hybrid might replace a whole conventional meal, replace a plant-based meal, or add an extra purchase. Those possibilities require observed evidence. Use a vector of displaced products rather than one universal coefficient, and allow zero, additive consumption or cross-species substitution where the data support it.

Distinguish avoided growth from an absolute fall in production. A future industry that is smaller than the no-intervention counterfactual may still be larger than today. Do not apply a supply-response factor twice if a published animal-impact conversion already contains it. Report animal numbers and welfare consequences separately from tonnes, emissions and nutritional outcomes.

**Scenarios worth testing once inputs exist**

|  |  |
| :-: | :-: |
| \*\*Exploratory condition\*\* | \*\*Evidence that would change the decision\*\* |
| Product clears review and replaces chicken | Named approvals and certificates, reproducible supply, repeated purchases and measured chicken substitution. |
| Scientific progress stalls before sale | Good laboratory results alongside unresolved dossier, finance, manufacturing, price or trust constraints. |
| Accessible plant foods outperform the new product | Comparable meal experiments show greater substitution or value from available alternatives. |
| Conventional production retains its advantage | The alternative adds consumption, fails to scale, or improves less quickly than its actual competitor. |

These cases are stress tests, not mutually exclusive probability buckets. No calibrated sales, approval-date, climate or animal-welfare forecast is supplied because the necessary baseline and empirical links are absent.

**10 A research plan that closes the important gaps**

**Product and institutional work**

Choose one target formulation, origin history, site and channel before approaching reviewers. Prepare a versioned dossier summary. Seek written clarification from the relevant food authority and certification body on product classification, acceptable evidence, cell origin, medium history, recognition and change control. Use competent local readers for Arabic, Urdu, Malay and relevant Indian-language material. Store the actual response, institution, scope and date rather than converting an informal conversation into an approval.

**A staged consumer design**

Keep the branch’s plant-based pilot as a distinct near-term study of ordinary food choice. For cultivated chicken, begin with interviews and comprehension testing until a legally available product and suitable tasting permissions exist. An urban feasibility sample can locate barriers and improve questions; it is not nationally representative.

Recruit across food budgets, dietary practices and household purchasing roles. Predefine the meal and its alternatives. In a later authorized study, vary price, formulation information and verified certification information in a randomized design that can separate their effects. Never display a fictitious certificate or claim approval the product lacks. Measure understanding, trial, actual spending, repeat purchase, waste and the displaced food, including changes elsewhere in the household diet.

Set sample size from the primary outcome, expected variation and clustering, rather than importing the size of a previous convenience survey. Preregister exclusions and comparisons, retain attrition and null results, document translation and consent, and analyze subgroup differences without treating national or religious identity as a fixed preference. Repeated purchasing and substitution need follow-up, not a single tasting score.

**Prioritized work packages**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Priority\*\* | \*\*Deliverable\*\* | \*\*Completion condition\*\* |
| 1 Reproducibility | Recover the exact PDF source package and missing model files. | A pinned revision rebuilds the report and runs the claimed tests with documented expected outputs. |
| 1 Scope and permissions | One product dossier and jurisdiction-specific decision map. | Each access field has a dated, scoped primary record or an explicit unknown status. |
| 2 Data provenance | Re-obtain the FAO table, inaccessible household report and key full texts. | Values and methods are checked against originals, with page locators and discrepancies logged. |
| 2 Demand evidence | Pilot instrument and feasible recruitment plan. | The primary outcome and counterfactual are defined; no national demand estimate is implied. |
| 3 Supply and impacts | Comparable process, cost, environmental and substitution records. | Uncertainty and product boundaries are explicit and independent validation is available. |
| 3 Model release | Versioned baseline and integrated scenario outputs. | Units, partitions, supply constraints and unknown states pass tests; outputs can be traced to inputs. |

These priorities are a proposed order of work, not commitments or estimates of how quickly regulators, data owners or suppliers will respond. Expand commercial or welfare claims only when the relevant completion condition is satisfied.

**11 Reproducibility and citation repairs**

The repository verification script is useful and passed in both snapshots. It is not the PDF’s claimed test suite. The following files named in the PDF were absent: tools/integrate.mjs, tools/scenario.mjs, tools/scenario.test.mjs, tools/build-figures.mjs, tools/validate.mjs, tools/build-report.mjs and tools/render-report.mjs. The named analysis/baseline.json and analysis/scenario-results.json were also absent.

The same problem affects the 15 evidence tables, six figure-data files, four focal dossiers, three precedent dossiers and review or defect records described by the PDF. Recover their original paths and revision from the author; do not reconstruct missing code and present it as the code that generated the paper. Until recovered, revise the validation sentence to: “The paper reports 23 passing synthetic tests; that result was not reproducible from the repository snapshots available for this review.”

A release manifest should link report version, source records, extracted evidence, raw-data provenance, transformations, test command and environment. Store retrieval date, original publication or effective date, exact locator, evidence type, access level, funding or conflict information, and the claim each source supports. Keep “author reported,” “independently checked,” “unresolved” and “contradicted” separate.

Preserve the PDF’s CO, SA and GP identifiers as stable references. Fill missing bibliographic fields from inspected records without renumbering them merely to remove gaps. Link the Bryant original and correction under one evidence-family identifier. Apply the same approach to preprints, accepted manuscripts, publisher records, company restatements and multiple pages about one policy decision.

Separate automated link status from evidence appraisal in the repository. A successful HTTP retrieval or matching title does not validate a coefficient, causal interpretation, regulatory scope or current commercial claim. A blocked page is not necessarily a dead link. Update the dated branch scope before merging, and keep the cultivated-chicken report linked to its own source package rather than silently treating the broader catalog as its supporting data.

**Appendix A Stored protein supply data**

These are the repository’s FAO-derived values, not a newly downloaded FAO extract. Supply is measured in grams of protein per person per day; the share column is percent. All 12 populated rows reproduce internally at the displayed precision. Supply availability is not measured individual intake. The country selection is purposive and is not a representative North–South sample.[ \[R-DATA\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/comparative-protein/protein-data.csv)

|  |  |  |  |  |  |  |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| \*\*Country\*\* | \*\*Total 2010\*\* | \*\*Animal 2010\*\* | \*\*Total 2023\*\* | \*\*Animal 2023\*\* | \*\*Plant 2023\*\* | \*\*Animal share 2023\*\* |
| United States | 119.1 | 80.4 | 123.1 | 82.9 | 40.2 | 67.3 |
| Germany | 110.2 | 70.1 | 109.2 | 73.6 | 35.6 | 67.4 |
| United Kingdom | 105.9 | 62.5 | 110 | 65.1 | 44.9 | 59.2 |
| Netherlands | 110.1 | 75.3 | 117.1 | 81.5 | 35.6 | 69.6 |
| Denmark | 112.3 | 70 | 126.3 | 86.8 | 39.5 | 68.7 |
| China | 108.7 | 43.3 | 131 | 54.2 | 76.8 | 41.4 |
| India | 60.4 | 11.5 | 74.6 | 20 | 54.6 | 26.8 |
| Brazil | 101.8 | 56.8 | 106.5 | 68 | 38.5 | 63.8 |
| South Africa | 78.9 | 35.3 | 79.2 | 36.5 | 42.7 | 46.1 |
| Kenya | 57.8 | 17.9 | 55.8 | 14.5 | 41.3 | 26 |
| Nigeria | 62.1 | 9.4 | 57 | 6.6 | 50.4 | 11.6 |
| Zimbabwe | 61.2 | 30.5 | 69.1 | 31.3 | 37.8 | 45.3 |
| Singapore | Missing | Missing | Missing | Missing | Missing | Missing |

Derivations: plant protein is total protein less animal protein; animal share is animal protein divided by total protein, expressed as percent. The stored provenance identifies FAO Statistical Yearbook 2025, Table 50, Food Balances, with retrieval on 28 October 2025 and printed-page locators 325–329. The external FAO document could not be retrieved during this review, leaving transcription against the original unresolved.

Singapore is explicitly missing, not zero. Pakistan is not in this extract and no Pakistan value has been imputed. Do not insert the HIES quantities or Indian household nutrient estimates into this supply table: they have different units, data-generation processes and denominators.

**Appendix B Every reference in the supplied PDF**

All 54 unique linked references were checked for retrieval. The source codes found in the PDF matched these 54 entries; no unmatched code was detected. The initial and follow-up retrievals returned text for 41 URLs, limited challenge content for one, and no usable content for 12. The claim-use column below gives the more important limit on interpretation. A title, landing page or abstract is not full-text verification. Access reflects this review on 21 September 2026, not a guarantee of continued availability.

Codes link directly to the cited source. Titles are shortened for navigation. “Unretrieved” means this environment could not obtain the source; it does not establish that the original URL is permanently broken. “Partial” includes metadata, abstract-only material, accessible summaries and incomplete methods review. “Checked” refers to the named passage or fact, not every claim in that publication.

**Core evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[CO-S01\\\]  &#10;\](https://iifa-aifi.org/en/56085.html)IIFA Resolution 265 on cultivated meat | Checked | Conditional religious position; read clauses Third to Sixth. No universal process permission or numeric substitution cap. |
| \[\\\[CO-S02\\\]  &#10;\](https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/)MUIS fatwa statement 3 February 2024 | Checked | Conditional permissibility; distinguish product certification and purchasing. |
| \[\\\[CO-S03\\\]  &#10;\](https://www.who.int/publications/i/item/9789240070943)FAO WHO Food safety aspects of cell based food | Partial | WHO landing page available; full report not extracted. Do not claim full-report review. |
| \[\\\[CO-S04\\\]  &#10;\](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en)FAO global webinar report | Checked | Institutional summary dated 29 March 2024; event was in April 2023. Not product safety clearance. |
| \[\\\[CO-S05\\\]  &#10;\](https://www.thermofisher.com/us/en/home/references/gibco-cell-culture-basics/cell-culture-environment/culture-media.html)Thermo Fisher Basics of Culture Media | Partial | General technical material. No food-grade, halal or industrial cost conclusion. |
| \[\\\[CO-S06\\\]  &#10;\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full)Bryant and colleagues consumer survey 2019 | Partial | Original text available; interpret with the correction. Methods were not independently replicated. |
| \[\\\[CO-S07\\\]  &#10;\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2020.00086/full)Bryant and colleagues corrigendum 2020 | Checked | Retain corrected Indian 56.3% and 62.8% intention figures; same evidence family as CO-S06. |
| \[\\\[CO-S08\\\]  &#10;\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766)Ahsan and colleagues Pakistan consumer study | Partial | Journal metadata recovered; full methods not re-obtained. 2022 volume 2 issue 1 pages 111–122. |
| \[\\\[CO-S09\\\]  &#10;\](https://www.nature.com/articles/s41598-026-62416-3)Irfan and colleagues Pakistan study 2026 | Partial | Publisher and accepted-manuscript abstract inspected; n 102. Full methods and background statistics unverified. |
| \[\\\[CO-S10\\\]  &#10;\](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/)Chong and colleagues on site sensory experience | Partial | Author record supports n 107; Future Foods 9 100326 June 2024. No long-run demand inference. |
| \[\\\[CO-S11\\\]  &#10;\](https://www.goodmeat.co/all-news/good-meat-begins-the-worlds-first-retail-sales-of-cultivated-chicken)GOOD Meat retail launch May 2024 | Checked | Company launch announcement supports pack, price and formulation. Not current sales or pure biomass cost. |
| \[\\\[CO-S12\\\]  &#10;\](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/bit.27848)Humbird Scale up economics for cultured meat | Partial | Publisher material returned. Prospective economic model; no fresh recalculation or achieved-cost verification. |
| \[\\\[CO-S13\\\]  &#10;\](https://ce.nl/wp-content/uploads/2023/01/CE\_Delft\_200220\_Ex-ante-LCA-of-commercial-scale-CM-production-in-2030\_FINAL\_2.pdf)Sinke and colleagues prospective 2030 LCA | Partial | Author-hosted article retrieved. Inventory and calculations not independently reproduced. |
| \[\\\[CO-S14\\\]  &#10;\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11744764/)Risner and colleagues cradle to gate LCA | Unretrieved | PMC returned a challenge and alternate publisher access failed. No newly verified effect estimate. |
| \[\\\[CO-S15\\\]  &#10;\](https://www.nature.com/articles/s41598-025-99603-7)Schenzle and colleagues alternatives to serum albumins | Partial | Article and publisher PDF located; detailed historical-input and methods claims still require confirmation. |
| \[\\\[CO-S16\\\]  &#10;\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11722975/)Khaleel and colleagues UAE consumer study | Partial | Article material initially returned; methods could not be fully rechecked. Keep sample-limited interpretation. |

**South Asia evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[SA-S03\\\]  &#10;\](https://faolex.fao.org/docs/pdf/pak164529.pdf)Pakistan Halal Authority Act 2016 | Checked | Gazette text via FAOLEX. Check territorial scope and commencement; later consolidation not established. |
| \[\\\[SA-S04\\\]  &#10;\](https://pakistanhalalauthority.gov.pk/Files/PHA%20Halal%20Mark%20Scheme%20operationalization%20notification.jpg)PHA mark scheme notification 2025 | Unretrieved | Notification image unavailable. Do not upgrade the PDF’s reported reading to a fresh check. |
| \[\\\[SA-S05\\\]  &#10;\](https://pnac.gov.pk/Halal-Certification-Bodies/Active)PNAC active halal certification bodies | Unretrieved | Current register not recovered. No inferred certifier count, validity or cultivated scope. |
| \[\\\[SA-S06\\\]  &#10;\](https://smiic.org/en/accreditation-council-ac)SMIIC Accreditation Council | Partial | Institutional page returned. Membership and accreditation are not a product certificate. |
| \[\\\[SA-S07\\\]  &#10;\](https://logcluster.org/sites/default/files/public/2022-10/pakistanimport-policyministry-commerce22-april-2022-compressed1-compressed.pdf)Pakistan Import Policy Order 2022 | Unretrieved | Cited reproduction unavailable; amendments and present import classification unresolved. |
| \[\\\[SA-S08\\\]  &#10;\](https://faolex.fao.org/docs/pdf/pak115231.pdf)Punjab Food Authority Act 2011 | Checked | FAOLEX reproduction available; authority mapping supported. Current complete amendments need confirmation. |
| \[\\\[SA-S09\\\]  &#10;\](https://www.fssai.gov.in/upload/uploadfiles/files/Gazette\_Notification\_NonSpecified\_Food\_Ingredients\_15\_09\_2017.pdf)FSSAI non specified food regulations 2017 | Checked | Gazette approval route available; no named cultivated-product clearance inferred. |
| \[\\\[SA-S10\\\]  &#10;\](https://fssai.gov.in/upload/uploadfiles/files/Compendium\_FSS\_NFS\_FA\_17\_10\_2022.pdf)FSSAI regulations compendium 2022 | Checked | Prior-approval framework and application requirements. Process deadlines are not observed approval times. |
| \[\\\[SA-S11\\\]  &#10;\](https://fssai.gov.in/upload/uploadfiles/files/Status\_of\_Application\_as\_on\_09\_03\_2026.pdf)FSSAI application status 9 March 2026 | Partial | Dated register retrieved; exhaustive current product-name search not independently repeated. |
| \[\\\[SA-S12\\\]  &#10;\](https://i-cas-halal.qcin.org/)QCI i CAS Halal export portal | Partial | Portal available. Export conformity and domestic food approval are separate. |
| \[\\\[SA-S13\\\]  &#10;\](https://content.dgft.gov.in/Website/Notification\_ITCHS.pdf)DGFT ITC HS export schedule | Checked | Specified export conditions include destination requirements. Read with amendments, not as universal scope. |
| \[\\\[SA-S14\\\]  &#10;\](https://content.dgft.gov.in/Website/dgftprod/25fb264d-cd73-40f5-851f-31b5263357ef/Notification%2059%20dated%2009.02.26.pdf)DGFT Notification 59 February 2026 | Unretrieved | Official file located in search but text unavailable. Consolidated current requirements remain unresolved. |
| \[\\\[SA-S15\\\]  &#10;\](https://nabcb.qci.org.in/pc-048/)NABCB accreditation PC 048 | Checked | Scope and validity visible. Conventional animal-product scope does not itself cover cultivated chicken. |
| \[\\\[SA-S16\\\]  &#10;\](https://www.biokraftfoods.com/)Biokraft Foods company website | Partial | Company material returned. No independently audited capacity, throughput or approval verified. |
| \[\\\[SA-S17\\\]  &#10;\](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf)Pakistan HIES 2024 to 2025 economic report | Checked | Table 3.7.C page 25 quantities reread. Use table values; microdata and weighting not replicated. |
| \[\\\[SA-S18\\\]  &#10;\](https://mospi.gov.in/sites/default/files/publication\_reports/Final\_Report\_HCES\_2023-24L.pdf)India HCES Report 592 | Unretrieved | Original report link failed. Previously quoted expenditure values not treated as freshly verified. |

**Gulf and precedent evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[GP-S01\\\]  &#10;\](https://www.goodmeat.co/all-news/leading-shariah-scholars-rule-cultivated-meat-can-be-halal)GOOD Meat scholar advice announcement 2023 | Partial | Announcement located; company-reported advice. Detailed process-compliance claim not freshly re-established. |
| \[\\\[GP-S02\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf)SFDA General Requirements of Novel Foods | Checked | Cell and tissue scope and novel-food requirements visible. Verify controlling version and Arabic text. |
| \[\\\[GP-S03\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf)SFDA guide to novel food approval | Checked | Application information available. Guide does not prove product permission or achieved review speed. |
| \[\\\[GP-S04\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2026-08/SFDA-FRigsterE.pdf)SFDA food registration guide 2026 | Unretrieved | Cited English file not recovered. Current route and version require confirmation. |
| \[\\\[GP-S05\\\]  &#10;\](https://sfda.gov.sa/en/faq/what-are-halal-centers-and-how-apply-approval-request-external-centers)SFDA FAQ on external halal centers | Partial | Official FAQ returned. General role does not settle a specific certificate or destination scope. |
| \[\\\[GP-S06\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2023-11/511hala.pdf)Saudi recognized bodies list 2023 | Partial | Historical PDF available. Recheck current recognition and category for the proposed product. |
| \[\\\[GP-S07\\\]  &#10;\](https://sfda.gov.sa/en/news/saudi-arabia-singapore-sign-mou-mutual-recognition-halal-certificates-product-quality)Saudi Singapore halal recognition MoU news | Unretrieved | News URL unavailable; existence corroborated by MUIS annual report, GP-S08. |
| \[\\\[GP-S08\\\]  &#10;\](https://isomer-user-content.by.gov.sg/48/c463da6b-c40f-4595-b13e-2ec8b5e672dc/Muis%20Annual%20Report%202023.pdf)MUIS Annual Report 2023 | Checked | Printed page 32 records Saudi UAE and Jordan MoUs. No cultivated-product scope inferred. |
| \[\\\[GP-S09\\\]  &#10;\](https://www.moiat.gov.ae/en/programs/halal)MOIAT halal programme | Unretrieved | Official page inaccessible. Do not infer absence of a program or of conditions. |
| \[\\\[GP-S10\\\]  &#10;\](https://moiat.gov.ae/en/programs/halal/registered-halal-certification-bodies)MOIAT registered certification bodies | Unretrieved | Register not recovered. Current recognized issuer and scope unresolved. |
| \[\\\[GP-S11\\\]  &#10;\](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework)WAM Abu Dhabi novel food initiative 2025 | Checked | Prospective initiative and expected time savings. No measured approval performance or product permit. |
| \[\\\[GP-S12\\\]  &#10;\](https://investinabudhabi.gov.ae/News/AGWA-and-Believer-Meats-to-Develop-Cultivated-Meat-Capabilities-in-Abu-Dhabi)ADIO and Believer development announcement 2024 | Checked | Investment and development announcement. No confirmed operating plant or production volume. |
| \[\\\[GP-S14\\\]  &#10;\](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food)SFA premarket novel food guidelines | Checked | Product and process-specific review; material process changes need renewed approval. |
| \[\\\[GP-S15\\\]  &#10;\](https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Subsidiary%20Legislation%20Supplement/713.pdf)Singapore authorization regulations S 713 2025 | Partial | Gazette available; complete legal consolidation and a product-specific application not reviewed. |
| \[\\\[GP-S16\\\]  &#10;\](https://www.halal.gov.my/?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D\&utama=CB\_LIST)JAKIM foreign halal certification body portal | Partial | Portal returned. Referenced standard versions and current recognition need direct confirmation. |
| \[\\\[GP-S17\\\]  &#10;\](https://ciri.islam.gov.my/view/fatwa\_cetak.php?id=16914)JAKIM CIRi cultured meat record | Unretrieved | Cited record timed out. Added A02 is a separate named authority and must not be conflated with it. |
| \[\\\[GP-S18\\\]  &#10;\](https://cmsbl.halal.go.id/uploads/Decree\_Kepkaban\_221\_2025\_Implementation\_Procedure\_of\_Foreign\_Halal\_Certificate\_Registration\_bb95097144.pdf)BPJPH Decree 221 of 2025 | Checked | Foreign-certificate registration provisions read. Recognition does not by itself complete registration. |
| \[\\\[GP-S19\\\]  &#10;\](https://www.muis.gov.sg/resources/media-releases/8-aug-24-singapore-signs-halal-cooperation-memorandum-of-understanding-with-indonesia/)MUIS Indonesia cooperation MoU 2024 | Partial | Official statement available. Bilateral cooperation does not settle destination product registration. |
| \[\\\[GP-S20\\\]  &#10;\](https://www.uaelegislation.gov.ae/en/legislations/1161/download)UAE Federal Food Safety Law 10 of 2015 | Unretrieved | Download refused. No fresh complete statutory interpretation is claimed. |
| \[\\\[GP-S21\\\]  &#10;\](https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips)UAE government food safety overview | Unretrieved | No readable text returned. Overview cannot replace legislation or product decisions. |
| \[\\\[GP-S22\\\]  &#10;\](https://www.sfda.gov.sa/en/news/18781)SFDA food innovation statement December 2025 | Partial | Official statement retrieved. Authority self-report, not a named product permit or performance audit. |
| \[\\\[GP-S23\\\]  &#10;\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/fr/?lnk=1\&url=https://workspace.fao.org/sites/codex/Meetings/CX-701-47/CRDs/cac47\_crd04x.pdf)Codex CAC47 CRD04 country contributions 2024 | Checked | Saudi and UAE country descriptions inspected. September 2024 snapshot, not a consolidated current law review. |

**Additional primary sources**

|  |  |
| :-: | :-: |
| \*\*Reference\*\* | \*\*Locator and contribution\*\* |
| \[\\\[A01\\\]\](https://mospi.gov.in/sites/default/files/press\_release/press\_note\_Nutritional%20Intake%20in%20India\_02072025.pdf) MoSPI Nutritional Intake in India | 2 July 2025 press note. Pages 5 and 7 distinguish food-group shares and adjusted from unadjusted nutrient estimates. The source also appears in the repository branch. |
| \[\\\[A02\\\]\](https://muftiwp.gov.my/en/artikel/irsyad-fatwa/irsyad-fatwa-umum-cat/4887-irsyad-al-fatwa-siri-ke-595-daging-kultur-cultured-meat-menurut-perspektif-syarak) Federal Territories Mufti Office | Irsyad Hukum 595, 24 July 2021. Official Malay discussion of cultivated meat; AI-assisted interpretation in section 4 requires qualified local confirmation. |
| \[\\\[A03\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306) Press Information Bureau | Implementation of BioE3 Policy, 23 July 2026, smart-protein paragraph. Nine supported projects across three categories, not nine cultivated-product approvals. |
| \[\\\[A04\\\]\](https://www.nature.com/articles/s41598-026-62416-3\_reference.pdf) Irfan accepted manuscript | Publisher-hosted accepted version. Abstract and introductory material inspected; full methods not verified. Same evidence family as CO-S09. |

**Appendix C Repository catalog retrieval audit**

This appendix accounts for every one of the 159 catalog identities in the newer branch. These records overlap the PDF bibliography and one another in topic and evidence families; the two counts must not be added and called independent studies. Catalog IDs are navigation aids. Original collection IDs and their existing pending human-review fields remain authoritative.[ \[R-CATALOG\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/sources/catalog.json)

Legend: Returned means the cited URL returned text in at least one attempt, including publisher metadata, a landing page or an abstract. Limited means only a short or challenge response was recovered. Unavailable means no usable content was retrieved. Best access across attempts is shown; several pages were intermittent. Totals are 94 Returned, 4 Limited and 61 Unavailable. The columns do not certify full-text reading, claim validity or link permanence. Some sources were available through a different URL, as recorded in Appendix B.

Titles below are shortened to keep the inventory readable. Each catalog code opens the original source URL. The pinned catalog retains the full title, collection occurrences, original source IDs and prior access or limitation notes. Marketing pages and advocacy sources retain their original evidence type; being included is not endorsement.

|  |  |  |
| :-: | :-: | :-: |
| \*\*Catalog ID\*\* | \*\*Source title\*\* | \*\*Retrieval\*\* |
| \[\\\[SRC-001\\\]\](https://onlinelibrary.wiley.com/doi/10.1002/aepp.13232) | Meet the meatless: Demand for new generation plant-based meat alternatives | Returned |
| \[\\\[SRC-002\\\]\](https://onlinelibrary.wiley.com/doi/10.1002/aepp.13280) | Consumer spending patterns for plant-based meat alternatives | Returned |
| \[\\\[SRC-003\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201/) | Scale-up economics for cultured meat | Limited |
| \[\\\[SRC-004\\\]\](https://par.nsf.gov/servlets/purl/10466545) | Multi-objective Bayesian algorithm automatically discovers low-cost high-growth serum-free media for… | Unavailable |
| \[\\\[SRC-005\\\]\](https://doi.org/10.1007/s11367-020-01771-3) | A life cycle environmental sustainability analysis of microbial protein production via power-to-food approaches | Unavailable |
| \[\\\[SRC-006\\\]\](https://doi.org/10.1007/s11367-022-02128-8) | Ex-ante life cycle assessment of commercial-scale cultivated meat production in 2030 | Returned |
| \[\\\[SRC-007\\\]\](https://pubmed.ncbi.nlm.nih.gov/33276014/) | A systematic review on consumer acceptance of alternative proteins: Pulses, algae, insects, plant-based… | Unavailable |
| \[\\\[SRC-008\\\]\](https://doi.org/10.1016/j.biosystemseng.2022.02.013) | A machine learning framework to predict the next month's daily milk yield, milk composition and milking… | Unavailable |
| \[\\\[SRC-009\\\]\](https://www.sciencedirect.com/science/article/pii/S0956713520303066) | Consumer acceptance of cultured meat in urban areas of three cities in China | Unavailable |
| \[\\\[SRC-010\\\]\](https://www.sciencedirect.com/science/article/abs/pii/S0306919220301354) | Consumer preferences for farm-raised meat, lab-grown meat, and plant-based meat alternatives: Does… | Unavailable |
| \[\\\[SRC-011\\\]\](https://www.sciencedirect.com/science/article/pii/S0306919222001099) | The social impacts of a transition from conventional to cultivated and plant-based meats: Evidence from Brazil | Unavailable |
| \[\\\[SRC-012\\\]\](https://www.sciencedirect.com/science/article/pii/S0306919226000862) | Estimating plant-based milk impacts on U.S. fluid milk prices and quantities | Unavailable |
| \[\\\[SRC-013\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329318309996) | Consumers' willingness to purchase three alternatives to meat proteins in the United Kingdom, Spain, Brazil… | Unavailable |
| \[\\\[SRC-014\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329323001568) | Estimating consumers' willingness to pay for plant-based meat and cultured meat in China | Unavailable |
| \[\\\[SRC-015\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329323002616) | A meta-review of consumer behaviour studies on meat reduction and alternative protein acceptance | Unavailable |
| \[\\\[SRC-016\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329325003362) | Feeding the future: A comparison of drivers and barriers towards consumers' acceptance of plant-based… | Unavailable |
| \[\\\[SRC-017\\\]\](https://www.sciencedirect.com/science/article/pii/S2666833524001175) | Beyond the cow: Consumer perceptions and information impact on acceptance of precision… | Unavailable |
| \[\\\[SRC-018\\\]\](https://eref.uni-bayreuth.de/id/eprint/92470/) | How innovation-friendly is the EU Novel Food Regulation? The case of cellular agriculture | Returned |
| \[\\\[SRC-019\\\]\](https://ris.utwente.nl/ws/files/247793059/Haasnoot2013dynamic.pdf) | Dynamic adaptive policy pathways A method for crafting robust decisions for a deeply uncertain world | Returned |
| \[\\\[SRC-020\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC10481291/) | Households food consumption pattern in Pakistan: Evidence from recent household integrated economic survey | Limited |
| \[\\\[SRC-021\\\]\](https://doi.org/10.1016/j.isci.2021.102229) | Behavioral and neurophysiological evidence suggests affective pain experience in octopus | Unavailable |
| \[\\\[SRC-022\\\]\](https://doi.org/10.1016/j.jclepro.2021.127177) | Life cycle assessment of burger patties produced with extruded meat substitutes | Unavailable |
| \[\\\[SRC-023\\\]\](https://doi.org/10.1016/j.jenvp.2021.101589) | Price of change: Does a small alteration to the price of meat and vegetarian options affect their sales? | Unavailable |
| \[\\\[SRC-024\\\]\](https://doi.org/10.1016/j.jenvp.2023.102226) | Can you default to vegan? Plant-based defaults to change dining practices on college campuses | Unavailable |
| \[\\\[SRC-025\\\]\](https://pubmed.ncbi.nlm.nih.gov/31732401/) | Consumer acceptance of cultured meat in Germany | Returned |
| \[\\\[SRC-026\\\]\](https://www.sciencedirect.com/science/article/pii/S2468227622002113) | Planetary health and the promises of plant-based meat from a sub-Saharan African perspective: A review | Unavailable |
| \[\\\[SRC-027\\\]\](https://doi.org/10.1016/j.scitotenv.2023.164988) | Toward sustainable culture media: Using artificial intelligence to optimize reduced-serum formulations for… | Unavailable |
| \[\\\[SRC-028\\\]\](https://www.sciencedirect.com/science/article/pii/S2352550922003049) | Why can't the alternative become mainstream? Unpacking the barriers and enablers of sustainable protein… | Unavailable |
| \[\\\[SRC-029\\\]\](https://www.cambridge.org/core/journals/journal-of-agricultural-and-applied-economics/article/alternative-livestock-revolution-prospects-for-consumer-acceptance-of-plantbased-and-cultured-meat-in-south-africa/A79AF7AC795CF15549EFDB3AC7A1B380) | The alternative livestock revolution: Prospects for consumer acceptance of plant-based and cultured meat in… | Returned |
| \[\\\[SRC-030\\\]\](https://doi.org/10.1017/awf.2023.4) | Estimating global numbers of farmed fishes killed for food annually from 1990 to 2019 | Unavailable |
| \[\\\[SRC-031\\\]\](https://doi.org/10.1021/acs.est.5b01614) | Anticipatory Life Cycle Analysis of In Vitro Biomass Cultivation for Cultured Meat Production in the United… | Unavailable |
| \[\\\[SRC-032\\\]\](https://doi.org/10.1021/acsfoodscitech.4c00281) | Environmental Impacts of Cultured Meat: A Cradle-to-Gate Life Cycle Assessment | Unavailable |
| \[\\\[SRC-033\\\]\](https://doi.org/10.1021/es200130u) | Environmental Impacts of Cultured Meat Production | Unavailable |
| \[\\\[SRC-034\\\]\](https://www.nature.com/articles/s41467-025-58475-1) | Associations between national plant-based vs animal-based protein supplies and age-specific mortality in… | Returned |
| \[\\\[SRC-035\\\]\](https://www.nature.com/articles/s41538-026-00841-4) | Trends, challenges, and opportunities for the United States alternative meat and seafood sector:… | Returned |
| \[\\\[SRC-036\\\]\](https://doi.org/10.1038/s41586-021-03819-2) | Highly accurate protein structure prediction with AlphaFold | Unavailable |
| \[\\\[SRC-037\\\]\](https://doi.org/10.1038/s41586-022-04629-w) | Projected environmental benefits of replacing beef with microbial protein | Unavailable |
| \[\\\[SRC-038\\\]\](https://doi.org/10.1038/s41598-022-16996-5) | Most plant-based meat alternative buyers also buy meat: an analysis of household demographics, habit… | Unavailable |
| \[\\\[SRC-039\\\]\](https://doi.org/10.1038/s42003-022-03423-8) | Simple and effective serum-free medium for sustained expansion of bovine satellite cells for cell cultured meat | Unavailable |
| \[\\\[SRC-040\\\]\](https://doi.org/10.1038/s43016-022-00658-w) | Spontaneous immortalization of chicken fibroblasts generates stable, high-yield cell lines for serum-free… | Unavailable |
| \[\\\[SRC-041\\\]\](https://www.nature.com/articles/s43016-024-01022-w) | Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken using… | Unavailable |
| \[\\\[SRC-042\\\]\](https://doi.org/10.1088/1748-9326/ac4fda) | Impact of plant-based meat alternatives on cattle inventories and greenhouse gas emissions | Unavailable |
| \[\\\[SRC-043\\\]\](https://doi.org/10.1093/ajcn/nqaa203) | A randomized crossover trial on the effect of plant-based compared with animal-based meat on… | Unavailable |
| \[\\\[SRC-044\\\]\](https://pubmed.ncbi.nlm.nih.gov/36151900/) | Plant-based meats in China: a cross-sectional study of attitudes and behaviours | Unavailable |
| \[\\\[SRC-045\\\]\](https://doi.org/10.1126/sciadv.adp1528) | Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy | Unavailable |
| \[\\\[SRC-046\\\]\](https://doi.org/10.1146/annurev-animal-021022-055132) | Cultivated Meat: Progress and Remaining Challenges | Unavailable |
| \[\\\[SRC-047\\\]\](https://doi.org/10.1177/1745691615577794) | Identifying and Cultivating Superforecasters as a Method of Improving Probabilistic Predictions | Returned |
| \[\\\[SRC-048\\\]\](https://www.scielo.org.za/scielo.php?pid=S0038-23532025000400011\&script=sci\_arttext) | Mapping underutilised and emerging food sources and technologies as solutions to food insecurity in South… | Returned |
| \[\\\[SRC-049\\\]\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766) | Attitudes and Perceptions Towards Cultured Meat Among General Population in Pakistan | Returned |
| \[\\\[SRC-050\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report/agricultural-and-food-markets-trends-and-prospects\_c5cd366b.html) | OECD–FAO Agricultural Outlook 2026–2035: Agricultural and food markets: Trends and prospects | Returned |
| \[\\\[SRC-051\\\]\](https://ers.usda.gov/publications/113704) | Precision Dairy Farming, Robotic Milking, and Profitability in the United States | Returned |
| \[\\\[SRC-052\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full) | A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China | Returned |
| \[\\\[SRC-053\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2021.678491/full) | Don't Have a Cow, Man: Consumer Acceptance of Animal-Free Dairy Products in Five Countries | Returned |
| \[\\\[SRC-054\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1303448/full) | Price above all else: an analysis of expert opinion on the priority actions to scale up production and… | Returned |
| \[\\\[SRC-055\\\]\](https://www.mdpi.com/2072-6643/14/16/3292) | Understanding Key Factors Influencing Consumers' Willingness to Try, Buy, and Pay a Price Premium for… | Unavailable |
| \[\\\[SRC-056\\\]\](https://www.mdpi.com/2071-1050/12/11/4377) | Is India Ready for Alt-Meat? Preferences and Willingness to Pay for Meat Alternatives | Unavailable |
| \[\\\[SRC-057\\\]\](https://www.nsfc.gov.cn/csc/20345/20348/pdf/2025/202505-799-806.pdf) | 食品化工核心技术的关键科学问题 \\\[Key scientific issues in the core technologies of food chemical engineering\\\] | Returned |
| \[\\\[SRC-058\\\]\](https://doi.org/10.3758/s13428-023-02307-x) | Diminished diversity-of-thought in a standard large language model | Unavailable |
| \[\\\[SRC-059\\\]\](https://www.fao.org/3/cc3912en/cc3912en.pdf) | Contribution of terrestrial animal source food to healthy diets for improved nutrition and health outcomes:… | Unavailable |
| \[\\\[SRC-060\\\]\](https://openknowledge.fao.org/3/cd4313en/cd4313en.pdf) | World Food and Agriculture – Statistical Yearbook 2025 | Unavailable |
| \[\\\[SRC-061\\\]\](https://arxiv.org/abs/2402.18563) | Approaching Human-Level Forecasting with Language Models | Returned |
| \[\\\[SRC-062\\\]\](https://aifs.ucdavis.edu/about/aifs) | AI Institute for Next Generation Food Systems | Returned |
| \[\\\[SRC-063\\\]\](https://altprotein.jobs/career-hiring-report) | AltProtein.Jobs Career and Hiring Report 2025 | Unavailable |
| \[\\\[SRC-064\\\]\](https://cb.apps.fao.org/country.jsp?code=PAK) | Country Brief: Pakistan | Returned |
| \[\\\[SRC-065\\\]\](https://cedelft.eu/publications/tea-of-cultivated-meat/) | CE Delft techno-economic analysis | Returned |
| \[\\\[SRC-066\\\]\](https://coefficientgiving.org/funds/farm-animal-welfare/alternatives-to-animal-products/) | Coefficient Giving alternatives-to-animal-products programme | Returned |
| \[\\\[SRC-067\\\]\](https://coefficientgiving.org/funds/farm-animal-welfare/request-for-proposals-alternative-protein-rd/) | Coefficient Giving alternative-protein R\\\&D RFP | Returned |
| \[\\\[SRC-068\\\]\](https://data.fao.org/catalog/iso/2f264bb6-1238-459a-bf8b-0e2d0a16804a) | Food balances (Global, National - 2010-2023 - Annual) - FAOSTAT | Returned |
| \[\\\[SRC-069\\\]\](https://dhsprogram.com/pubs/pdf/FR375/FR375.pdf) | National Family Health Survey (NFHS-5), 2019-21: India: Volume I | Unavailable |
| \[\\\[SRC-070\\\]\](https://en.fvm.dk/news-and-contact/focus-on/action-plan-on-plant-based-foods) | Action Plan on Plant-Based Foods | Returned |
| \[\\\[SRC-071\\\]\](https://engrxiv.org/preprint/download/1438/2973/2173) | Humbird techno-economic analysis | Unavailable |
| \[\\\[SRC-072\\\]\](https://eprints.lse.ac.uk/125626/1/sciadv.adp1528.pdf) | Published full text | Unavailable |
| \[\\\[SRC-073\\\]\](https://faunalytics.org/animal-product-impact-scales-2026-updated-u-s-estimates-and-the-u-k-s-first-animal-product-impact-data/) | Animal Product Impact Scales 2026 Updated U.S. Estimates And The U.K.’s First Animal Product Impact Data | Returned |
| \[\\\[SRC-074\\\]\](https://food.ec.europa.eu/food-safety/novel-food/legislation\_en) | Novel Food legislation: Regulation (EU) 2015/2283 and implementing acts | Returned |
| \[\\\[SRC-075\\\]\](https://foresight4food.net/) | Foresight4Food | Unavailable |
| \[\\\[SRC-076\\\]\](https://foresight4food.net/wp-content/uploads/2026/03/FS4F\_Criteria-for-High-Quality-Guide-Feb-2026.pdf) | Criteria for High-Quality Food Systems Foresight | Returned |
| \[\\\[SRC-077\\\]\](https://gfi-india.org/resource/smart-protein-skills-mapping/) | Smart Protein Skills Mapping | Returned |
| \[\\\[SRC-078\\\]\](https://gfi.org/blog/alternative-protein-startups-underscore-the-need-for-scientific-and-engineering-talent/) | Alternative-protein startups’ talent needs | Returned |
| \[\\\[SRC-079\\\]\](https://gfi.org/resource/investment-methodology/) | GFI investment methodology | Returned |
| \[\\\[SRC-080\\\]\](https://gfi.org/wp-content/uploads/2026/04/2026-State-of-the-Industry-report-Fermentation-for-meat-seafood-eggs-dairy-and-ingredients.pdf) | GFI 2026 Fermentation State of the Industry | Returned |
| \[\\\[SRC-081\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI\_State-of-the-Industry-report-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf) | GFI 2026 Plant-Based State of the Industry | Unavailable |
| \[\\\[SRC-082\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI-2026-State-of-Global-Policy-Public-investment-in-protein-diversification-to-feed-a-growing-world.pdf) | GFI 2026 State of Global Policy | Returned |
| \[\\\[SRC-083\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI-2026-State-of-the-Industry-report-Cultivated-meat-seafood-and-ingredients.pdf) | GFI 2026 Cultivated Meat State of the Industry | Unavailable |
| \[\\\[SRC-084\\\]\](https://gfieurope.org/de/blog/private-investitionen-alternative-proteine/) | GFI Europe H1 2026 private investment update | Returned |
| \[\\\[SRC-085\\\]\](https://gfieurope.org/resource/state-of-the-european-alternative-protein-research-ecosystem-funding-and-publications/) | GFI Europe public R\\\&I funding tracker | Returned |
| \[\\\[SRC-086\\\]\](https://github.com/magpiemodel/magpie) | MAgPIE model repository and documentation | Returned |
| \[\\\[SRC-087\\\]\](https://globiom.org/documentation.html) | GLOBIOM documentation | Returned |
| \[\\\[SRC-088\\\]\](https://hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=animalcellculturefoods) | FDA inventory of completed premarket consultations | Returned |
| \[\\\[SRC-089\\\]\](https://innovationisrael.org.il/winner/cultivate-meat/) | בשר מתורבת \\\[Cultivated meat consortium\\\] | Unavailable |
| \[\\\[SRC-090\\\]\](https://ised-isde.canada.ca/site/global-innovation-clusters/en/node/83) | Ecosystem insight to build effective and relevant workforce solutions | Returned |
| \[\\\[SRC-091\\\]\](https://law.justia.com/cases/federal/appellate-courts/ca11/24-13640/24-13640-2026-03-23.html) | Eleventh Circuit opinion in UPSIDE Foods v | Returned |
| \[\\\[SRC-092\\\]\](https://mospi.gov.in/sites/default/files/press\_release/press\_note\_Nutritional%20Intake%20in%20India\_02072025.pdf) | Household Consumption Expenditure Survey: 2022-23 & 2023-24: Nutritional Intake in India | Returned |
| \[\\\[SRC-093\\\]\](https://pakistanhalalauthority.gov.pk/intro.aspx) | Pakistan Halal Authority official pages | Unavailable |
| \[\\\[SRC-094\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC12026562/) | Plant-based meat analogues review | Limited |
| \[\\\[SRC-095\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC3790135/) | Morphological analysis of food-system futures | Returned |
| \[\\\[SRC-096\\\]\](https://resources.sentientfutures.ai/fellowships/aianimals) | AI x Animals curriculum | Returned |
| \[\\\[SRC-097\\\]\](https://rethinkpriorities.org/research-area/ai-and-cultivated-meat/) | AI and Cultivated Meat. Near-Term Impacts of AI on the Commercial Viability of Cultivated Meat | Returned |
| \[\\\[SRC-098\\\]\](https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-map/) | Blue Marble: Next Generation — Base Map | Returned |
| \[\\\[SRC-099\\\]\](https://training-portal.nifa.usda.gov/web/crisprojectpages/1027058-cultured-10-leading-higher-education-initiatives-in-emerging-innovations-for-sustainable-food-production.html) | CULTURED 1.0: Leading Higher Education Initiatives in Emerging Innovations for Sustainable Food Production | Returned |
| \[\\\[SRC-100\\\]\](https://training-portal.nifa.usda.gov/web/crisprojectpages/1027620-integrated-approaches-to-enhance-sustainability-resiliency-and-robustness-in-us-agri-food-systems.html) | Integrated Approaches to Enhance Sustainability, Resiliency and Robustness in US Agri-Food Systems | Returned |
| \[\\\[SRC-101\\\]\](https://wfpc.sanford.duke.edu/reports/exploring-the-u-s-regulatory-and-legislative-landscapes-for-cell-cultivated-meat-and-seafood/) | Duke review of US cultivated-meat law | Returned |
| \[\\\[SRC-102\\\]\](https://www-pub.iaea.org/mtcd/publications/pdf/nvs-3-cd/pdf/nvs3\_scr.pdf) | IAEA acquisition-path and indicator guidance | Returned |
| \[\\\[SRC-103\\\]\](https://www.apac-sca.org/post/apac-sca-welcomes-singapore-s-approval-of-aleph-farms-cultivated-beef-marking-another-major-milest) | Aleph Farms Singapore approval announcement | Returned |
| \[\\\[SRC-104\\\]\](https://www.ars.usda.gov/oc/images/copyright/) | image-use policy | Returned |
| \[\\\[SRC-105\\\]\](https://www.ars.usda.gov/oc/images/photos/featuredphoto/aug19/beans/) | D502-1: Dry beans | Returned |
| \[\\\[SRC-106\\\]\](https://www.ars.usda.gov/oc/images/photos/nov21/d4744-1/) | D4744-1: A bioreactor conducting fermentation processes to produce ethanol | Returned |
| \[\\\[SRC-107\\\]\](https://www.bezosearthfund.org/news-and-insights/lauren-sanchez-announces-60-million-establish-bezos-centers-for-sustainable-protein) | Bezos Earth Fund sustainable-protein initiative | Returned |
| \[\\\[SRC-108\\\]\](https://www.birac.nic.in/cfp\_view.php?id=98\&scheme\_type=46) | DBT-BIRAC Joint Call for Proposals on 'Smart Proteins' for Fostering High Performance Biomanufacturing… | Returned |
| \[\\\[SRC-109\\\]\](https://www.cell-ag.de/) | CellAg Deutschland project overview | Returned |
| \[\\\[SRC-110\\\]\](https://www.cell-ag.de/\_files/ugd/cd7689\_34c289309fbd4cdbae0a16acbbb40967.pdf) | National Action Plan Germany | Unavailable |
| \[\\\[SRC-111\\\]\](https://www.cgiar.org/news-events/news/augmented-foresight-how-ai-can-make-food-systems-analysis-smarter-faster-and-more) | Augmented Foresight | Returned |
| \[\\\[SRC-112\\\]\](https://www.eda.gov/archives/2022/arpa/build-back-better/finalists/North-Carolina-Biotechnology-Center.htm) | Accelerate NC - Life Sciences Manufacturing | Unavailable |
| \[\\\[SRC-113\\\]\](https://www.efsa.europa.eu/en/applications/novel-food) | EFSA novel-food application guidance | Returned |
| \[\\\[SRC-114\\\]\](https://www.europarl.europa.eu/pdfs/news/expert/2026/6/press\_release/20260611IPR45209/20260611IPR45209\_en.pdf) | European Parliament meat-designation vote | Limited |
| \[\\\[SRC-115\\\]\](https://www.fao.org/4/i2744e/i2744e00.htm) | Livestock sector development for poverty reduction: an economic and policy perspective - Livestock's many… | Returned |
| \[\\\[SRC-116\\\]\](https://www.fao.org/4/X9892E/X9892e00.htm) | Food Balance Sheets: A Handbook | Unavailable |
| \[\\\[SRC-117\\\]\](https://www.fao.org/4/X9892E/X9892e01.htm) | Food Balance Sheets: A Handbook | Returned |
| \[\\\[SRC-118\\\]\](https://www.fao.org/4/x9892e/x9892e02.htm) | Food Balance Sheets: A Handbook, II. Concepts and definitions used in food balance sheets | Returned |
| \[\\\[SRC-119\\\]\](https://www.fao.org/agrifood-economics/news/detail-events/en/c/1757552/) | FAO analysis highlights strategic policy reform to narrow Pakistan's healthy diet gap | Returned |
| \[\\\[SRC-120\\\]\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1\&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FMeetings%252FCX-701-47%252FCRDs%252Fcac47\_crd04x.pdf) | Food Safety Aspects of Cell-Based Food and Precision Fermentation Derived Food Products | Returned |
| \[\\\[SRC-121\\\]\](https://www.fao.org/media/docs/unfoodsystemslibraries/foresight-for-food-systems/foresight-guide.pdf) | Using Foresight for Food Systems Transformation A guide for policy makers practitioners and researchers | Returned |
| \[\\\[SRC-122\\\]\](https://www.fao.org/research-extension-systems/agricultural-innovation-systems/en) | Agricultural innovation systems | Returned |
| \[\\\[SRC-123\\\]\](https://www.fda.gov/food/hfp-constituent-updates/fda-completes-first-pre-market-consultation-human-food-made-using-animal-cell-culture-technology) | FDA Completes First Pre-Market Consultation for Human Food Made Using Animal Cell Culture Technology | Returned |
| \[\\\[SRC-124\\\]\](https://www.food.gov.uk/print/pdf/node/27246) | UK FSA sandbox progress report | Unavailable |
| \[\\\[SRC-125\\\]\](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1424012/full) | Artificial intelligence in cultivated meat | Returned |
| \[\\\[SRC-126\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1378883/full) | Backcasting for food-system transformation | Returned |
| \[\\\[SRC-127\\\]\](https://www.fsis.usda.gov/inspection/compliance-guidance/labeling/labeling-policies/human-food-made-cultured-animal-cells) | USDA-FSIS cultivated-cell labeling and inspection policy | Unavailable |
| \[\\\[SRC-128\\\]\](https://www.gov.uk/government/statistics/national-diet-and-nutrition-survey-2019-to-2023/national-diet-and-nutrition-survey-2019-to-2023-report) | National Diet and Nutrition Survey 2019 to 2023: report | Returned |
| \[\\\[SRC-129\\\]\](https://www.gov.za/news/media-statements/science-technology-and-innovation-partners-un-food-and-agriculture) | Science, Technology and Innovation partners with UN Food and Agriculture Organization on roadmap to… | Unavailable |
| \[\\\[SRC-130\\\]\](https://www.greenqueen.com.hk/swap-food-vegan-chicken-plant-based-meat-startup-liquidation-shuts/) | Green Queen consolidation tracker | Returned |
| \[\\\[SRC-131\\\]\](https://www.infoteca.cnptia.embrapa.br/handle/doc/1150307) | Guide for technological functional characterization of protein ingredients for the plant-based market | Returned |
| \[\\\[SRC-132\\\]\](https://www.ipcc.ch/report/ar6/wg2/chapter/annex-ii/) | Annex II: Glossary - scenario, climate prediction, and climate projection definitions | Unavailable |
| \[\\\[SRC-133\\\]\](https://www.mse.gov.sg/latest-news/newsletter-climate-action-in-sg-dec/) | Climate Action in SG (Dec 2020): Novel food as a sustainable food option | Returned |
| \[\\\[SRC-134\\\]\](https://www.mse.gov.sg/latest-news/written-reply-to-parliamentary-question-on-lab-grown-seafood-and-cultured-meat-sector/) | Written Reply to Parliamentary Question on Lab-Grown Seafood and Cultured Meat Sector | Returned |
| \[\\\[SRC-135\\\]\](https://www.mti.gov.sg/newsroom/speech-by-mos-alvin-tan-at-the-singapore-international-agri-food-week-welcome-reception/) | Speech by MOS Alvin Tan at the Singapore International Agri-Food Week Welcome Reception | Returned |
| \[\\\[SRC-136\\\]\](https://www.nationaalgroeifonds.nl/overzicht-lopende-projecten/thema-landbouw-voedsel-en-land-en-watergebruik/cellulaire-agricultuur) | Cellulaire Agricultuur | Returned |
| \[\\\[SRC-137\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report.html) | OECD-FAO Agricultural Outlook 2026-2035 | Returned |
| \[\\\[SRC-138\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report/meat\_149b4ca3.html) | OECD–FAO Agricultural Outlook 2026–2035: Meat | Returned |
| \[\\\[SRC-139\\\]\](https://www.pbs.gov.pk/hies/) | Household Integrated Economic Survey (HIES) | Returned |
| \[\\\[SRC-140\\\]\](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-2.pdf) | Household Integrated Economic Survey (HIES) 2024-25 | Returned |
| \[\\\[SRC-141\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238344\&lang=1\&reg=3) | Parliament Question: BioE3 Policy | Returned |
| \[\\\[SRC-142\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306\&lang=1\&reg=3) | PARLIAMENT QUESTION: IMPLEMENTATION OF BIOE3 POLICY | Returned |
| \[\\\[SRC-143\\\]\](https://www.psqca.com.pk/division-wise-standards/halaal/) | Halaal standards and Halal Certification Bodies (PS 4992-OIC/SMIIC 2) | Returned |
| \[\\\[SRC-144\\\]\](https://www.sciencedirect.com/science/article/pii/S0308521X25000101) | Quantitative scenarios for food-system futures | Unavailable |
| \[\\\[SRC-145\\\]\](https://www.sciencedirect.com/science/article/pii/S0924224417303400) | Bringing cultured meat to market: Technical, socio-political, and regulatory challenges in cellular agriculture | Unavailable |
| \[\\\[SRC-146\\\]\](https://www.sciencedirect.com/science/article/pii/S0924224426004413) | AI in alternative-protein development review | Unavailable |
| \[\\\[SRC-147\\\]\](https://www.sentientfutures.ai/incubator/gallery/) | Sentient Futures Incubator gallery | Returned |
| \[\\\[SRC-148\\\]\](https://www.sentientfutures.ai/incubator/gallery/advocacy-intel-map/) | Effective Advocacy Project | Returned |
| \[\\\[SRC-149\\\]\](https://www.sentientfutures.ai/incubator/gallery/cheese-analogue-ai/) | Optimising Cheese Analogues Formulation using AI Applications | Returned |
| \[\\\[SRC-150\\\]\](https://www.sentientfutures.ai/incubator/gallery/ideosphere-forecasting/) | Ideosphere | Returned |
| \[\\\[SRC-151\\\]\](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/overview-of-pre-market-approval-framework-for-novel-food) | Singapore SFA novel-food framework | Unavailable |
| \[\\\[SRC-152\\\]\](https://www.ukri.org/news/national-alternative-protein-innovation-centre-launches/) | National alternative protein innovation centre launches | Returned |
| \[\\\[SRC-153\\\]\](https://www.ukri.org/opportunity/alternative-proteins-innovation-and-knowledge-centre/) | Alternative Proteins Innovation and Knowledge Centre | Returned |
| \[\\\[SRC-154\\\]\](https://www.ukri.org/publications/alternative-proteins-roadmap-identifying-uk-priorities/) | Alternative Proteins Roadmap: identifying UK priorities | Returned |
| \[\\\[SRC-155\\\]\](https://www.un.org/scientific-advisory-board/sites/default/files/2025-06/verification\_of\_frontier\_ai.pdf) | Verification of frontier AI | Unavailable |
| \[\\\[SRC-156\\\]\](https://www.unep.org/resources/whats-cooking-assessment-potential-impacts-selected-novel-alternatives-conventional) | What’s Cooking? An assessment of potential impacts of selected novel alternatives to conventional animal… | Returned |
| \[\\\[SRC-157\\\]\](https://www.who.int/news-room/fact-sheets/detail/healthy-diet) | Healthy diet | Returned |
| \[\\\[SRC-158\\\]\](https://www.who.int/publications/i/item/9789240070943) | Food safety aspects of cell-based food | Returned |
| \[\\\[SRC-159\\\]\](https://www.who.int/publications/i/item/B09677) | WHO-PREZODE zoonotic-risk indicators | Returned |

**Appendix D Records required for the next release**

The following record types make the report’s next update reviewable without implying that the missing evidence already exists. They are proposed specifications, not reconstructed outputs of the absent PDF model.

|  |  |
| :-: | :-: |
| \*\*Record\*\* | \*\*Minimum fields\*\* |
| Source and evidence family | Stable source ID; full citation; DOI or URL; publication and access dates; version; family ID; exact page or clause; evidence type; funding; access level; human review status. |
| Claim | Claim ID; exact assertion; product and jurisdiction; source IDs; supporting locator; interpretation; uncertainty; checked by and date; superseded or conflicting evidence. |
| Institutional decision | Issuer; legal or religious function; scope; process and formulation; site; territory; effective and expiry dates; certificate or decision identifier; conditions; recognition and registration dependencies. |
| Production observation | Facility and batch; product; inputs and provenance; scale; run date; yields; losses; downtime; utilization; energy; costs; independent validation; confidentiality limits. |
| Consumer observation | Sampling frame; recruitment; weights; language; exact stimulus; price; meal; choice set; stated or observed outcome; follow-up; attrition; substitution; preregistration and consent. |
| Scenario baseline | Dataset and revision; full-access contract; price and year; units; segment and channel partitions; supply-pool ID; access and acceptance assumptions; uncertainty and missingness rules. |
| Animal impact | Species and product displaced; counterfactual; demand effect; supply and trade response; yield; number affected; welfare assumptions; donor and input animals; uncertainty; double-counting checks. |

Release condition: each headline claim can be traced to a scoped record, each numerical output to a compatible input and transformation, and each unresolved item remains visibly unresolved. The present evidence justifies focused research and institutional clarification. It does not yet justify a commercial forecast or a quantified claim of animals spared.

Updated research and evidence audit  • 

  
  

# 20 September - review-memo.md  

# Review — *Conditional markets for cultivated chicken*

**Reviewed 20 September 2026 · against the local package at** **OUTPUTS/Cultivated Meat Comparative Research 2026-09-20/**

## The short version

The citation machinery is clean. The sourcing discipline is not, in two specific ways: 28 of 54 source records carry no publication date, and the bounded English-only search missed two things that were sitting inside its own window — an Indonesian regulation from this month that undercuts the draft's best transmission episode, and the one directly on-topic peer-reviewed review published in April.

  

The draft's evidence cutoff is 20 September 2026, which is the day it was built. So there is nothing to "update since the cutoff." The real question is what the search missed inside the window, and the answer is: two things that matter and two that don't.

  

-----

## 1\. Substantive updates needed

### 1.1 Indonesia — Decree 221/2025 is no longer the operative instrument

**BPJPH Regulation No. 4 of 2026**, issued September 2026, sets an assurance guideline for foreign halal-certified products entering, circulating and traded in Indonesia, via an integrated electronic system, ahead of a **mandatory halal certification deadline in October 2026**.

  

This lands directly on §7, process-tracing episode 3 ("Recognition plus registration, Singapore–Indonesia"), which is the draft's strongest documented transmission link. The argument there — that a recognition MoU still leaves a registration obligation downstream — survives. But it currently rests on Decree 221/2025 alone, and a reader who knows the file will ask why a September 2026 instrument on exactly that question is absent from a paper dated 20 September 2026.

  

**Fix:** add Reg 4/2026 as a source, and rewrite the episode so the point is *sequence* — recognition (Aug 2024) → registration procedure (Decree 221/2025) → assurance regime (Reg 4/2026) → mandatory deadline (Oct 2026). That is a stronger version of the same claim, not a retreat from it. Flag that the Indonesian text controls and the English reporting is secondary, consistent with how the draft already handles the Malay CIRi record.

### 1.2 The missing peer-reviewed review

Alqurashi, Sikora, Rzymski & Poniedziałek, "Cultured Meat and Its Acceptability in Muslim Societies: A Narrative Perspective on Halal Perspectives and Regulatory Challenges," *Foods* 15(8), art. 1288, **9 April 2026**. It maps cell sourcing, growth media, scaffolding and processing against halal requirements, and reviews SFDA / Saudi Halal Center, JAKIM, IFANCA and OIC, covering Saudi Arabia, Malaysia, Singapore and the GCC. It proposes a "Halal-by-Design" protocol.

  

This is the single absence a specialist reviewer will notice first. It overlaps the draft's §2 and §3 almost exactly. Engaging it is also an opportunity rather than a concession: the draft's contribution is the *decision map* (jurisdiction × institution × product × channel × segment × time) and the explicit refusal to amalgamate positions into a global halal rule. A narrative review that proposes harmonised certification is a natural foil. Cite it, then say why this paper does something different.

### 1.3 Two lower-priority items inside the window

  - **FSSAI non-specified food status list.** The draft uses the 9 March 2026 register (SA-S11) and records a bounded negative search (SA-X05: no "cultiv" or "meat" match). A 15 January 2026 version also exists, so FSSAI republishes this periodically — the March list was already six months old at the cutoff. Check for a post-March list before restating the negative finding. Separately, that PDF returned a server error when I tried to fetch it today; archive a copy now.
  - **Malaysia, Food (Amendment No. 3) Regulations 2026**, 26 August 2026, requiring imported food to originate from recognised food-safety assurance programmes, effective 1 March 2027. Peripheral to the cultivated question, but it touches the Malaysia precedent dossier's recognition logic and is cheap to note.

  

-----

## 2\. Citation integrity — mechanically sound

I resolved the whole chain from manuscript to claims to sources:

  

  - 90 claim references in the manuscript, 52 unique. **Zero dangling references.** Every \[\[...\]\] marker resolves to a claim record.
  - **Zero claims pointing at nonexistent sources.**
  - 109 citation-map entries, all resolving.

  

That is better than most working drafts and worth keeping. Three things are off, though:

  

**Ten sources are unreachable from the paper.** CO-S03, CO-S04, GP-S06, GP-S07, GP-S08, GP-S09, GP-S10, GP-S15, GP-S20, GP-S21 are in the register but no cited claim reaches them. Only **44** of the 54 records are load-bearing. The README's "54 canonical source records" headline therefore overstates the base by 23%. Either cite them, move them to a clearly labelled background register, or change the headline number. The draft is scrupulous about not overstating everywhere else; this one number breaks the pattern.

  

**Seventeen of 69 claims are never cited** (CO-C03, CO-C05, GP-C04, C06–C09, C11, C13, C15, C17, C23, C24, C26, SA-C02, C04, C23). Fine as provenance, but say so.

  

**Twenty-eight of 54 sources have no publication date.** This is the one that bothers me, because the project's own standing sourcing rule is *verification before visualisation, sources with dates, name the funder*. More than half the register fails the second clause.

  

Two of those dates are recoverable right now, and both improve the paper:

  

|  |  |  |
| :-: | :-: | :-: |
| \*\*Source\*\* | \*\*Currently\*\* | \*\*Should be\*\* |
| GP-S02 — SFDA novel food general requirements | no date | \*\*SFDA.FD 513/2020\*\*, adopted 30 November 2020 (CEO order 12/7-18-1440) |
| SA-S17 — Pakistan HIES 2024-25 | no date | Published \*\*December 2025\*\*; fieldwork September 2024 – June 2025; 32,000+ households; Pakistan Bureau of Statistics |

  

The HIES one is not housekeeping. §9 currently says the HIES documentation "requires reconciliation of survey scope and period." The period is now in hand: Sept 2024–June 2025, against India's HCES 2023-24. That is a real and statable non-overlap, which is a better sentence than an admission that you didn't check.

  

-----

## 3\. Source-quality risks, ranked

**Four cited claims rest entirely on sources never read in full.** CO-C09, CO-C10, CO-C11 and GP-C19 have no source in their set with better than abstract-, index- or landing-page-level access. CO-C10 and CO-C11 I verified independently today and they hold (see §4), so the exposure is narrower than it looks — but the access status in the register should be upgraded to reflect that they were confirmed.

  

**SA-S04 is a JPEG.** The PHA Halal Mark Scheme operationalisation notice (20 May 2025) is cited as retrieved\_original, but the URL is a .jpg. An image cannot be quoted, text-searched or verified by a reader, and this is the sole support for the §5 finding that Pakistan has an *operational* scheme rather than merely a statute — which is one of the draft's better Pakistan contributions. Get a PDF or gazette citation, or downgrade the access status and say in the text that the instrument was read from a scanned image.

  

**GP-S04 is probably not a real register.** The filename SFDA-FRigsterE.pdf reads like a typo for "Register," it is marked search-index-only, and it returned no readable text when I fetched it today. It underpins the §6 passage about "identifier differences in inspected documents and an apparent novelty-date difference." That passage already discloses its own weakness honestly, but it is resting on a document nobody has opened. Either locate the actual SFDA register or demote the passage to a footnote.

  

**Four cited claims are** **candidate** **— unreviewed — and all four are absence findings.** GP-C12 (no UAE approval located), GP-C25 (no Saudi permit located), SA-C24 (no Pakistan authorization or import precedent located), GP-C19 (Malay-language CIRi record). The draft handles these correctly: it never promotes them to claims of prohibition, and the FINAL\_REVIEW says so explicitly. But absence findings are exactly what a hostile reader attacks, and these are the four with the least review behind them. Give them a paragraph of their own in §13 rather than leaving them distributed.

  

**One genuine strength worth protecting:** the 19-record exclusions register, which logs failed retrievals with query strings, dates and unanswered questions (WHO 403s, UPI PDF failure, QCI scheme 403). Most work at this level hides its retrieval failures. Do not let this get compressed out when the paper is shortened.

  

-----

## 4\. What I checked against originals and what held

|  |  |
| :-: | :-: |
| \*\*Claim\*\* | \*\*Verdict\*\* |
| IIFA Resolution 265 (10/26) — 26th session, 4–8 May 2025, English page 20 Nov 2025 | \*\*Confirmed.\*\* Five conditions and the Sixth-clause coexistence language are as described. The draft's refusal to read a numerical displacement limit into that clause is correct. |
| MUIS fatwa on cultivated meat, 3 Feb 2024 | \*\*Confirmed\*\*, URL live |
| SFDA novel food requirements cover animal cell/tissue culture | \*\*Confirmed.\*\* §3.1 lists cell/tissue culture; §4.2 makes SFDA approval mandatory before sale; §4.3 requires halal source. English version informational, Arabic controlling — exactly as the draft states. |
| Chong et al. — 107 Singapore diners, April–June 2023, post-tasting acceptance | \*\*Confirmed.\*\* \*Future Foods\*, June 2024, Huber's Butchery. Upgrade CO-S10 from abstract-only. |
| Irfan et al. — 102 Pakistani university respondents, cross-sectional online, 21 July 2026 | \*\*Confirmed\*\*, including the "first empirical study in Pakistan" novelty claim the exclusions register flagged as unresolved (CO-X05). That can now be resolved. |
| Pakistan HIES 2024-25 | \*\*Confirmed\*\*, with the date and period above |

  

Nothing I checked came back wrong. The errors in this draft are omissions and metadata gaps, not misstatements.

  

-----

## 5\. Fix list, in order

1.  Add BPJPH Reg 4/2026 and rewrite §7 episode 3 as a four-step sequence. *(substantive — do this first)*
2.  Add and engage *Foods* 15(8):1288. *(substantive)*
3.  Fill the two recoverable dates; rewrite the §9 HIES sentence to state the actual period mismatch.
4.  Upgrade access status on CO-S09, CO-S10, CO-S11; close exclusion CO-X05.
5.  Fix or downgrade SA-S04 (JPEG) and GP-S04 (unopened register).
6.  Reconcile the "54 sources" headline with the 44 that are load-bearing.
7.  Re-check the FSSAI register for a post-March 2026 list; archive the PDF either way.
8.  Consolidate the four candidate absence findings into one paragraph in §13.
9.  Sweep the remaining 26 undated sources; date what can be dated, mark the rest undated explicitly.
10. Note Malaysia Amendment No. 3 Regulations 2026 in the Malaysia dossier.

  

Items 1–3 change what the paper says. The rest change how well it survives someone checking.

  

-----

## Note on process

There is no ABOUT ME/ folder in the connected Sentient Futures folder. Drive has one "About me" doc from 1 August 2026; I found no anti-ai-writing-style or my-company file in either place. Slack returned nothing on cultivated meat or halal. If those files live somewhere I can't see, point me at them and I'll re-audit this memo's register against them.

  
  
  

# Grill-me session, 19 September  

**SENTIENT FUTURES — CONCEPT NOTE**

Halal, Sharia and the Cultivated Meat Market

Grill-me session, 19 September 2026

Supersedes nothing in the 14 Sept concept note; extends it.

  

**1. WHAT CHANGED**

  

The original lane was a comparative India–Pakistan brief on socio-cultural drivers of protein consumption. This session expanded it to include the Gulf and to organise the whole document around Islamic jurisprudence and certification capacity.

  

Decision: the Gulf is an extension, not a replacement. India–Pakistan stays the spine. The document remains one artifact rather than splitting into a team deliverable plus a standalone published piece.

  

Accepted cost: the India–Pakistan comparison compresses to make room, and the named deliverable the mentors scoped becomes a section rather than the whole brief. This needs flagging at the mentor call rather than discovered there.

  

**2. THE ARGUMENT**

  

The jurisdictions with the most Muslim consumers have the least capacity to decide whether cultivated meat is permissible for them. The decision is being made elsewhere, by regulators optimising for export access rather than domestic doctrine. Pakistan inherits a standard it had no hand in writing.

  

Supporting claim: cultivated meat's ceiling in Muslim markets is set by jurisprudence and certification capacity, not by price or consumer appetite.

  

This maps onto the governance-capacity-asymmetry argument Zafar already makes in AI policy, which is part of why the brief works as a work sample.

  

**3. SCOPE AND CASES**

  

Pakistan — large Muslim population, negligible regulatory capacity, no food-tech policy attention. Standard-taker by default.

  

India — the control case. Non-Islamic constraint structure, active biotech and food-tech policy push, and a domestic halal export industry it regulates for other people's markets.

  

UAE and Saudi Arabia — the Gulf pair. Food-security strategies with explicit import-substitution logic, sovereign capital already exposed to the sector, and formal fatwa infrastructure. Means and incentive to rule early.

  

Malaysia, Singapore, Indonesia — precedent benchmark, not cases. One to two pages. Singapore approved cultivated meat for sale first, which means the first serious halal question about a commercially approved product was asked in Southeast Asia rather than the Gulf. JAKIM is the reference standard much of the Muslim world harmonises toward. Indonesia is the largest Muslim market and its mandatory certification regime cannot be omitted entirely without the gap being visible to anyone who knows the sector.

  

**4. HOW THE PERMISSIBILITY QUESTION IS HANDLED**

  

The brief maps the dispute. It does not adjudicate it. Policymakers do not need a ruling from a policy researcher; they need to know what the scholars are likely to do and what follows if the scholars disagree.

  

Four branches, each tied to a production or regulatory consequence:

  

\- Source cells. Taken from an animal slaughtered per Islamic rites, from a live biopsy, or from a non-halal animal. Cleanest branch, and the one a producer can simply comply with.

\- Growth medium. Fetal bovine serum is the obvious problem. Serum-free media largely resolve it. A jurisprudential objection with an engineering fix.

\- Istihalah, the transformation principle. Whether a substance changing in nature changes its ruling. The deep branch, where the schools diverge, and the argument that could permit cultivated meat from otherwise impermissible inputs.

\- Whether slaughter is a requirement of the meat or of the animal. If permissibility attaches to the act, cultivated meat has no path. If it attaches to the substance, it does.

  

Finding that falls out: the permissibility question is mostly not theological. It turns on production choices already within producers' control, and the jurisdictions that specify those choices early will shape the product for everyone else.

  

Attribution rule, strictly applied: every position tied to a named body or scholar with a date. No "some scholars hold." If a position cannot be sourced cleanly, it does not appear.

  

**5. STRUCTURE**

  

Thematic, not country-by-country. Countries appear as evidence inside sections. Target 12–15 pages.

  

1\. Framing: the gated market. 1.5 pp. Finding stated in the first 200 words.

2\. The permissibility question and what it turns on. 3 pp. Four branches as a table plus commentary, each tagged with its production consequence.

3\. Who gets to decide. 4 pp. The capacity asymmetry. Core section. India, Pakistan, UAE, Saudi as evidence, plus the Southeast Asia precedent box. Population against rulemaking capacity is the contrast that carries it.

4\. Demand under a permissibility gate. 2.5 pp.

5\. Policy implications. 2.5 pp. Separated by actor: producers, standard-setting bodies, importing states, and states with population but no capacity.

6\. Methodology and limits. 1 p.

  

**6. THE MARKET LAYER**

  

No independent 20-year projection. Two reasons: Anna leads consumption-centric demand forecasting for this team, and a team report containing two incompatible projections is worse than one containing none. Separately, credible 20-year cultivated meat projections do not exist in citable form — the 2021-era consultancy scenarios assumed cost curves that did not materialise, and presenting one as a finding would be visible to any informed reader.

  

Instead: take Anna's elicitation output as the baseline demand curve and add the conditional layer. How much of that curve is gated on halal status. What share of the projected addressable market in 2046 sits in Muslim-majority jurisdictions, and the observation that this share is a jurisprudential variable rather than a demand one.

  

Three scenarios, with prolonged silence treated as a real case rather than a rounding error:

\- Ruled halal. In the baseline.

\- Ruled haram. Excluded regardless of price or willingness to pay.

\- Prolonged silence. Most likely over a 20-year horizon. No import pathway and no domestic industry, but no doctrinal barrier to later reversal either.

  

Existing market forecasts are cited as inputs being stress-tested, with the funder named on each.

  

**7. SOURCING AND LIMITS**

  

English-language sources only. Stated explicitly in the methodology section rather than left implicit: scholarly positions are represented as their certification bodies and English-publishing institutions frame them.

  

This pushes the evidence base toward standards documents — SMIIC, GSO, JAKIM, the UAE scheme — which are published in English and are stronger evidence for a policy argument than sermon-level sources would be.

  

Carried-over rules: verification before visualisation, sources with dates, funder named on interested reports.

  

**8. PRIOR ARTIFACTS**

  

The "Protein Transitions Across Unequal Food Systems" report and the "Research Foundation" package are kept as is.

  

The AI-assisted provenance of that prior research will be disclosed to the mentors, briefly and unprompted. The project is about AI and forecasting; volunteering it is better than it surfacing later.

  

**9. OPEN ITEMS**

  

\- Scope-note email to Liliia not yet drafted or sent.

\- Anna not yet told that her baseline is needed by \~20 Oct.

\- Gulf fatwa-body ruling status unverified.

\- How far Indonesia's regime intrudes into section 3 not yet settled.

  
  
  
  

# Rough  

**Conditional Markets for Cultivated Chicken**

This report reviews the supplied 20 September 2026 paper together with the Sentient Futures research repository, including the newer India–Pakistan branch. It updates the substantive argument, checks the available data and citations, and specifies the evidence still needed for a defensible market or animal welfare estimate.

The central conclusion survives review: cultivated chicken has conditional pathways through religious interpretation, certification, food regulation, production and purchasing. The available evidence does not establish blanket halal acceptance, permission to sell a particular product in all four focal markets, scalable supply, representative demand, or net reductions in animal production.

## **Decisions supported by the review**

Retain India, Pakistan, Saudi Arabia and the UAE as institutional case studies. Use Singapore, Malaysia and Indonesia as scoped precedents. Do not turn these cases into a readiness league table.

Keep cultivated chicken separate from the repository’s proposed plant-based consumer pilot. Plant-based trials may generate useful local evidence, but their adoption rates cannot calibrate cultivated chicken demand.

Keep the scenario output uncomputed until a compatible demand baseline, product decisions and supply allocations exist. Missing information is not zero demand.

Publish a reproducibility repair before describing the PDF model as independently verified. Its claimed 23 tests and supporting evidence files are absent from both repository snapshots inspected.

  

The most useful additions are verified Pakistan household food quantities, a clearer distinction between adjusted and unadjusted Indian nutrient estimates, an official Malaysian religious discussion, and a more explicit route from product sales to animal outcomes. Existing correct cautions and corrected consumer percentages are preserved.

Read sections 1–3 for the review findings and decision framework, sections 4–9 for the updated evidence, and sections 10–11 for the research and repair plan. Appendices contain the full stored country dataset, all 54 PDF reference dispositions, and all 159 repository catalog retrieval results.

Status: AI-assisted research review. No new consumer experiment, laboratory validation, regulatory opinion or independent human scholarly review was conducted. Evidence access and remaining uncertainties are stated where they affect a conclusion.

  

**1) What the review established**

|  |  |
| :-: | :-: |
| \*\*Finding\*\* | \*\*Evidence and implication\*\* |
| Repository integrity passes | The main snapshot passed 2,218 existing checks; the newer branch passed 2,432. These validate packaging, internal references and specified arithmetic, not the truth of every research claim. |
| The PDF has a reproducibility gap | The paper describes executable scenarios, 23 tests, evidence tables and review records that were not present in either inspected snapshot. The report’s methodological description can be evaluated, but its implementation cannot be reproduced from this repository. |
| The research scope has changed | The main branch treats India–Pakistan work as proposed. The newer branch contains a completed brief recommending a plant-based urban pilot. The PDF instead studies cultivated chicken across four jurisdictions. |
| The numerical data need separate denominators | Food-balance supply, household nutrient estimates, food quantities, expenditure shares and hypothetical purchase intentions answer different questions. A single combined demand score would be misleading. |
| The reference system is navigable | All 54 source codes extracted from the PDF resolve to linked bibliography entries. The original Bryant study and its correction are one evidence family, not two independent studies. |
| Access is incomplete | For the repository catalog, 94 URLs returned text, 4 returned only limited or challenge content, and 61 could not be retrieved. Text returned can mean metadata or an abstract; it is not full verification. |

 

These findings support a revised working report rather than a claim that the entire literature has been independently replicated. All source URL checks were attempted, and decision-critical claims were inspected in available primary material. The breadth of the repository exceeds the set of claims for which full-text methods, underlying datasets and current legal instruments could be rechecked.

## **Corrections and additions**

The PDF already uses the corrected Indian willingness figures and already refuses to output a forecast without a baseline. Those are strengths to retain. The material changes are to qualify the unreproduced model-validation claim, connect the branch’s household evidence to this report, add a named Malaysian source rather than a general national judgment, and make the animal-impact mechanism explicit.

Several bibliography entries can be completed. The FAO webinar page is dated 29 March 2024, although the event it describes occurred in April 2023. The Chong study belongs to Future Foods 9, article 100326, June 2024. Ahsan and colleagues’ article is in volume 2 issue 1, 2022, pages 111–122; the repository records an earlier online publication date. Keep online and issue dates distinct. The Risner paper similarly needs its online date distinguished from its journal issue year.[ \[CO-S04\]](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en)[ \[CO-S10\]](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/)[ \[CO-S08\]](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766)[ \[R-IP\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/india-pakistan/india-pakistan-brief.md)

# **2 Materials and verification boundaries**

The supplied PDF, Conditional Markets for Cultivated Chicken, is dated 20 September 2026 and contains 25 pages: 14 main pages, four appendix pages and seven reference pages. Its SHA256 is 04dc5ca193c8ceaace2b4cbfce1ee806d93f0239a7c488f478f46ee8f784f217. The review used the supplied file, not an assumed repository copy.

|  |  |  |
| :-: | :-: | :-: |
| \*\*Snapshot\*\* | \*\*Pinned revision\*\* | \*\*Review result\*\* |
| Main | fc13b3bcf1287df372c673bf2814d0aff1a7bf95 | 45 packaged files; five documents; 143 source identities; 104 original source-register records.\[ \\\[R-MAIN\\\]\](https://github.com/Omarzaf/sentient-futures-research/tree/fc13b3bcf1287df372c673bf2814d0aff1a7bf95) |
| India & Pakistan branch | 9896751e53c1b851a874153cbdf6cd72c217058a | 49 packaged files; six documents; 159 source identities; 124 original source-register records.\[ \\\[R-BRANCH\\\]\](https://github.com/Omarzaf/sentient-futures-research/tree/9896751e53c1b851a874153cbdf6cd72c217058a) |

 

The second revision is from codex/consolidated-india-pakistan. Local review copies were matched against the remote Git blob hashes, and each snapshot’s existing verification script was run without editing its research content. This report does not modify or merge either branch. The older branches were not separately audited beyond the material represented in these snapshots.

The newer catalog combines 60 comparative-protein records, 44 AI/protein records and 20 India–Pakistan records, plus links from the orientation material. Its 159 identities are a navigation inventory, not 159 independent empirical studies. Exact nonempty DOI duplicates were not found in that consolidated catalog; semantic duplicates, versions and overlapping evidence still require judgment.[ \[R-CATALOG\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/sources/catalog.json)

The review distinguishes four levels: internal integrity; external URL retrieval; claim-level inspection of accessible primary text; and empirical replication. The first two were broad. The third focused on claims that affect the argument. The fourth was not possible without original survey data, production records, the missing scenario package and authoritative product decisions. No search was an exhaustive multilingual legal or systematic literature review.

# **3 Define the product and decision before the market**

The appropriate unit is a specified product and process, considered by a named institution, for a jurisdiction, channel, consumer segment and date. “Cultivated meat is acceptable” is too broad to function as a regulatory, religious or commercial variable. A finding for one donor source, cell bank, medium or formulation should not automatically transfer to another.

|  |  |
| :-: | :-: |
| \*\*Product profile\*\* | \*\*Information that determines the next decision\*\* |
| Traced slaughter-origin cells | Document species, donor and slaughter chain, tissue, cell-bank establishment, all media and processing inputs, production site and final formulation. |
| Cells from a living animal | Resolve the named authority’s treatment of tissue removal and donor status. Do not infer permission from guidance that addresses a different cell source. |
| Legacy bank with incomplete history | Record the unknown historical inputs. A later serum-free production phase does not reconstruct the earlier provenance. |
| Hybrid finished product | Disclose cultivated fraction and every other ingredient. Approvals, certificates, nutrition, cost and substitution concern the finished product as well as its cultured component. |

 

Use a sequence of separate questions: Is the proposed process religiously permissible under the relevant interpretation? Can the product and site obtain an applicable certificate? Is the certifier recognized for the destination and scope? Is food approval granted for that product and process? Are import, labeling and channel requirements satisfied? Can dependable supply be delivered at the relevant price? Do people purchase it repeatedly, and what does it replace?

Each record should retain the institution, document version, effective date, product and process identifiers, territorial scope, conditions and evidence locator. Unknown, pending, conditional, approved and refused are different states. A blank registry search cannot establish a prohibition or a universal absence of applications.

# **4 Religious evidence remains institution specific**

## **International Islamic Fiqh Academy**

Resolution 265 was adopted during the May 2025 session; the inspected English webpage is dated 20 November 2025. It sets conditions concerning cell origin, permissible inputs, credible supervision, disclosure and safety. Its wording about live animals and slaughter where required needs qualified interpretation for a specific tissue source; this review does not convert it into a universal live-biopsy permission. Its statement favoring use alongside conventional meat is a normative position, not an estimated numerical displacement ceiling.[ \[CO-S01\]](https://iifa-aifi.org/en/56085.html)

## **Singapore MUIS**

MUIS’s February 2024 statement permits cultivated meat subject to halal animal origin, halal ingredients and a clean, non-toxic final product. A general fatwa does not certify every product. The statement also acknowledges that consumers may consider taste, price and preference. Religious permissibility therefore cannot stand in for observed purchasing or issuer-specific trust.[ \[CO-S02\]](https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/)

## **Malaysia source added to the review**

The Federal Territories Mufti Office published Irsyad Hukum 595 on 24 July 2021. For land animals, its discussion distinguishes tissue from lawful slaughter from tissue taken while the animal is alive or after death without the required slaughter. It also addresses prohibited material and harm. This adds a named, inspectable Malaysian interpretation to the evidence base. It is not proof of a product certificate, an operative national approval or consensus among all Malaysian authorities.[ \[A02\]](https://muftiwp.gov.my/en/artikel/irsyad-fatwa/irsyad-fatwa-umum-cat/4887-irsyad-al-fatwa-siri-ke-595-daging-kultur-cultured-meat-menurut-perspektif-syarak)

This paragraph is an AI-assisted interpretation of the Malay original, not a certified translation. A Malaysian reviewer should confirm its doctrinal and institutional application. The separate JAKIM CIRi record cited in the PDF could not be retrieved in this review; the new source does not silently replace it.[ \[GP-S17\]](https://ciri.islam.gov.my/view/fatwa_cetak.php?id=16914)

## **Company reported advice and recognition agreements**

GOOD Meat’s 2023 announcement describes advice obtained from scholars. It should remain labeled a company account of religious advice, not a Saudi regulator’s permit or a current product certificate. The PDF’s detailed process-compliance interpretation was not independently re-established from the announcement text during this review.[ \[GP-S01\]](https://www.goodmeat.co/all-news/leading-shariah-scholars-rule-cultivated-meat-can-be-halal)

MUIS’s annual report confirms halal recognition MoUs with Saudi Arabia, the UAE and Jordan. That verifies institutional cooperation; it does not establish that a particular cultivated product lies within recognized scope. Indonesia’s Decree 221/2025 also shows why recognition and destination registration must be recorded separately.[ \[GP-S08\]](https://isomer-user-content.by.gov.sg/48/c463da6b-c40f-4595-b13e-2ec8b5e672dc/Muis%20Annual%20Report%202023.pdf)[ \[GP-S18\]](https://cmsbl.halal.go.id/uploads/Decree_Kepkaban_221_2025_Implementation_Procedure_of_Foreign_Halal_Certificate_Registration_bb95097144.pdf)

# **5 Regulatory pathways and unresolved product decisions**

This section reports the inspected institutional evidence and the questions that remain. It does not establish legal clearance for a particular commercial product. Dated registers and guidance must be checked again against the actual application, process and intended channel before a market-access variable is assigned.

  

|  |  |  |
| :-: | :-: | :-: |
| \*\*Jurisdiction\*\* | \*\*What is supported\*\* | \*\*What is still required\*\* |
| India | FSSAI’s non-specified food regulations provide an application and prior-approval framework. The March 2026 application register is a dated administrative snapshot.\[ \\\[SA-S09\\\]\](https://www.fssai.gov.in/upload/uploadfiles/files/Gazette\_Notification\_NonSpecified\_Food\_Ingredients\_15\_09\_2017.pdf)\[ \\\[SA-S10\\\]\](https://fssai.gov.in/upload/uploadfiles/files/Compendium\_FSS\_NFS\_FA\_17\_10\_2022.pdf)\[ \\\[SA-S11\\\]\](https://fssai.gov.in/upload/uploadfiles/files/Status\_of\_Application\_as\_on\_09\_03\_2026.pdf) | A current, named cultivated-chicken decision; exact formulation and process scope; manufacturing or import conditions; labeling and channel requirements. |
| Pakistan | The Pakistan Halal Authority Act and Punjab Food Authority Act identify relevant institutions and powers. Federal trade and provincial food responsibilities need separate treatment.\[ \\\[SA-S03\\\]\](https://faolex.fao.org/docs/pdf/pak164529.pdf)\[ \\\[SA-S08\\\]\](https://faolex.fao.org/docs/pdf/pak115231.pdf) | Current commencement and amendments, operative product route, applicable provincial rules, import conditions, certifier scope and a product-level decision. |
| Saudi Arabia | SFDA guidance explicitly addresses novel foods, including cell or tissue sources, and an application process. Halal conditions coexist with food review.\[ \\\[GP-S02\\\]\](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf)\[ \\\[GP-S03\\\]\](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf) | An authoritative current dossier route, the product approval, recognized certification scope, registration and import conditions; Arabic controlling text where applicable. |
| United Arab Emirates | Codex country material describes a premarket route; Abu Dhabi announced a novel-food initiative in October 2025. These establish institutional activity.\[ \\\[GP-S23\\\]\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/fr/?lnk=1\&url=https://workspace.fao.org/sites/codex/Meetings/CX-701-47/CRDs/cac47\_crd04x.pdf)\[ \\\[GP-S11\\\]\](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework) | Operative federal and emirate requirements, current standards and certification registers, and a named product authorization for the planned sale or import. |

 

## **India**

The i-CAS Halal material and DGFT export conditions concern specified export products and destinations. They do not, by themselves, create a domestic cultivated-food approval. The inspected PC 048 accreditation page has a defined conventional animal-product scope and validity period; it cannot be extended to cultivated chicken by analogy. The February 2026 DGFT amendment was located but its text could not be retrieved, so the current consolidated export position remains unresolved.[ \[SA-S12\]](https://i-cas-halal.qcin.org/)[ \[SA-S13\]](https://content.dgft.gov.in/Website/Notification_ITCHS.pdf)[ \[SA-S14\]](https://content.dgft.gov.in/Website/dgftprod/25fb264d-cd73-40f5-851f-31b5263357ef/Notification%2059%20dated%2009.02.26.pdf)[ \[SA-S15\]](https://nabcb.qci.org.in/pc-048/)

India’s BioE3 program supplies a separate research-policy signal. An official parliamentary answer of 23 July 2026 reports nine supported smart-protein projects across fermentation, plant-based and cell-culture categories. That is evidence of support, not nine cultivated-chicken approvals or commercial plants. Biokraft’s website is company evidence and should not be used as audited output or operating capacity.[ \[A03\]](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306)[ \[SA-S16\]](https://www.biokraftfoods.com/)

## **Pakistan**

The 2016 Act’s application and commencement provisions deserve particular care: some provisions concerning regulated activity depend on notification. The 2025 mark-scheme image, current PNAC list and cited Import Policy Order could not be reread in this review. Do not infer that an institution’s existence settles commencement, certifier recognition or a cultivated-product classification. A current regulatory map should identify the federal trade role and the relevant provincial food authority for the actual site and channel.[ \[SA-S03\]](https://faolex.fao.org/docs/pdf/pak164529.pdf)[ \[SA-S04\]](https://pakistanhalalauthority.gov.pk/Files/PHA%20Halal%20Mark%20Scheme%20operationalization%20notification.jpg)[ \[SA-S05\]](https://pnac.gov.pk/Halal-Certification-Bodies/Active)[ \[SA-S07\]](https://logcluster.org/sites/default/files/public/2022-10/pakistanimport-policyministry-commerce22-april-2022-compressed1-compressed.pdf)[ \[SA-S08\]](https://faolex.fao.org/docs/pdf/pak115231.pdf)

## **Saudi Arabia and the UAE**

The SFDA novel-food documents show a real route for review, but the cited general-requirements cover and application guide use different identifier presentations. Preserve the source version and obtain confirmation of the controlling standard rather than silently normalizing them. The 2023 recognized-body list is historical; the 2026 English registration-guide URL did not return its text. Neither can establish today’s approval or recognition for a named product.[ \[GP-S02\]](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf)[ \[GP-S03\]](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf)[ \[GP-S04\]](https://www.sfda.gov.sa/sites/default/files/2026-08/SFDA-FRigsterE.pdf)[ \[GP-S06\]](https://www.sfda.gov.sa/sites/default/files/2023-11/511hala.pdf)

For the UAE, the WAM report describes an initiative and expected time savings; it does not measure realized review times. The ADIO–Believer announcement records a development plan, not proof that a commercial facility is now operating. Federal legislation and the MOIAT pages were not accessible in this check. Their absence from the retrieved evidence must remain a gap, not a claim that no requirements exist.[ \[GP-S11\]](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework)[ \[GP-S12\]](https://investinabudhabi.gov.ae/News/AGWA-and-Believer-Meats-to-Develop-Cultivated-Meat-Capabilities-in-Abu-Dhabi)[ \[GP-S09\]](https://www.moiat.gov.ae/en/programs/halal)[ \[GP-S10\]](https://moiat.gov.ae/en/programs/halal/registered-halal-certification-bodies)[ \[GP-S20\]](https://www.uaelegislation.gov.ae/en/legislations/1161/download)[ \[GP-S21\]](https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips)

## **Singapore and Indonesia as bounded precedents**

Singapore’s current guidance requires renewed approval for manufacturing changes that affect the safety assessment, including changes to cell lines or medium components, and for expanded uses. An old approval cannot automatically travel with a reformulated product. Indonesia’s 2025 decree requires registration of qualifying foreign halal certificates before circulation; a bilateral MoU alone does not complete that step. These are precedents for how to structure records, not transferable permission to sell elsewhere.[ \[GP-S14\]](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food)[ \[GP-S15\]](https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Subsidiary%20Legislation%20Supplement/713.pdf)[ \[GP-S18\]](https://cmsbl.halal.go.id/uploads/Decree_Kepkaban_221_2025_Implementation_Procedure_of_Foreign_Halal_Certificate_Registration_bb95097144.pdf)[ \[GP-S19\]](https://www.muis.gov.sg/resources/media-releases/8-aug-24-singapore-signs-halal-cooperation-memorandum-of-understanding-with-indonesia/)

# **6 Consumer evidence and household food data**

## **What the consumer studies can answer**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Evidence\*\* | \*\*Finding that can be retained\*\* | \*\*Boundary\*\* |
| India Bryant survey and correction | For the Indian panel, 56.3% were very or extremely likely to buy clean meat, versus 62.8% for plant-based meat. The PDF already uses the corrected figures.\[ \\\[CO-S06\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full)\[ \\\[CO-S07\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2020.00086/full) | Hypothetical intention in a panel, not national market share, repeat purchasing, willingness at a verified price, or the effect of halal certification. |
| Pakistan Ahsan study | A Pakistan consumer study predates the 2026 article. Publication metadata supports retaining it in the evidence history.\[ \\\[CO-S08\\\]\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766) | Full methods were not re-obtained in this review. The branch reports sample limitations and inconsistent acceptance measures; its estimates are not newly verified here. |
| Pakistan Irfan study | Publisher material and the accepted manuscript describe a 102-person sample.\[ \\\[CO-S09\\\]\](https://www.nature.com/articles/s41598-026-62416-3)\[ \\\[A04\\\]\](https://www.nature.com/articles/s41598-026-62416-3\_reference.pdf) | The abstract and introductory material were inspected; full methods and data were not independently verified. Its claim of first empirical evidence is contradicted by the earlier study. |
| Singapore tasting study | The author record describes 107 diners in a 2023 on-site tasting study.\[ \\\[CO-S10\\\]\](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/) | A tasting sample does not establish representative demand, long-run repurchase, price elasticity or a causal effect of a religious issuer. |
| UAE consumer study | Retain exploratory consumer evidence within its stated sample and method.\[ \\\[CO-S16\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11722975/) | The PDF reports 577 convenience and snowball respondents. Detailed methods and that count were not freshly verified here; no national acceptance parameter is assigned. |

 

These studies should not be pooled into one acceptance percentage. They differ in product description, sampling frame, exposure, language, outcome, timing and whether respondents tasted a product. A comparable synthesis would extract wording, denominators, recruitment, exclusions, weighting, missingness, confidence intervals, preregistration, funding and conflicts for each study. A sample size alone does not make two estimates comparable.

The older Ahsan record also prevents a false novelty claim from propagating into the updated report. The 2026 article’s existence is verified, but neither a publisher record nor an accepted-manuscript abstract is a substitute for checking questionnaire construction and analysis. Access limits stay attached to the affected claim.

## **India household nutrition**

The official July 2025 release gives two versions of the 2023–24 household-derived protein estimate. Use the adjusted values for the corresponding adjusted series; retain the unadjusted values only with their label. Both are survey-derived nutrient estimates, not individual dietary recalls.[ \[A01\]](https://mospi.gov.in/sites/default/files/press_release/press_note_Nutritional%20Intake%20in%20India_02072025.pdf)

|  |  |  |
| :-: | :-: | :-: |
| \*\*India 2023 to 2024 measure\*\* | \*\*Rural\*\* | \*\*Urban\*\* |
| Unadjusted protein g per person per day | 61.8 | 63.4 |
| Adjusted protein g per person per day | 61.2 | 62.9 |
| Cereals as percent of reported protein | 45.9% | 38.7% |
| Egg fish and meat as percent of reported protein | 12.4% | 14.1% |

 

Source locators: Table 3, printed page 7, for adjustment; Figures 5R and 5U, page 5, for food-group shares. The egg/fish/meat category excludes dairy and is not the entire animal-protein share. Its denominator differs from FAO food-balance supply.[ \[A01\]](https://mospi.gov.in/sites/default/files/press_release/press_note_Nutritional%20Intake%20in%20India_02072025.pdf)

The PDF also quotes HCES expenditure values from Report 592. The original report URL did not return the document in this review, so those rupee values are not republished as freshly checked figures. The source remains in the audit. NFHS frequency findings in the repository likewise should remain frequency evidence, not grams consumed or a direct vegetarian-identity measure.[ \[SA-S18\]](https://mospi.gov.in/sites/default/files/publication_reports/Final_Report_HCES_2023-24L.pdf)[ \[R-IP\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/india-pakistan/india-pakistan-brief.md)

## **Pakistan household food quantities**

Pakistan’s HIES 2024–25 supplies direct household context. The following values are transcribed from Table 3.7.C, printed page 25, PDF page 42. They describe monthly food quantities per person, not cultivated demand or grams of protein.[ \[SA-S17\]](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf)

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Food and unit per person per month\*\* | \*\*Urban\*\* | \*\*Rural\*\* | \*\*Total\*\* |
| Wheat and wheat flour kg | 5.76 | 7.12 | 6.59 |
| Pulses kg | 0.27 | 0.25 | 0.26 |
| Milk litres | 6.12 | 6.17 | 6.15 |
| Chicken meat kg | 0.41 | 0.29 | 0.34 |
| Eggs number | 3.44 | 2.44 | 2.83 |

 

Use the tabulated quantities rather than the nearby generalization that urban consumption is higher across examples; milk is slightly higher in the rural column. Survey coverage, weights and item definitions must be recovered before microdata replication or population extrapolation. The monthly chicken quantity should not be treated as total national chicken supply or multiplied by an intention percentage to create a cultivated market forecast.[ \[SA-S17\]](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf)

## **Food balance data and affordability**

The repository’s FAO-derived table contains 12 populated country cases and one missing Singapore row. Pakistan is absent. Stored plant-protein values equal total minus animal protein, and animal shares reproduce to the shown precision. The underlying FAO Table 50 could not be re-downloaded in this review, so this is a successful arithmetic check, not fresh external transcription verification. Appendix A preserves the values and provenance.[ \[R-DATA\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/comparative-protein/protein-data.csv)

The practical consumer unit should be a meal and purchase occasion. Record disposable food spending, household size, cooking facilities, preparation time, product format, cold-chain access and the alternative actually available. Compare cultivated chicken with local chicken dishes and relevant plant foods, not only premium imported substitutes. Currency conversion cannot replace a local affordability comparison at a dated price.

  

# **7 Production economics environmental effects and safety**

## **Production claims require a complete process boundary**

A laboratory growth result, pilot batch, announced factory and sustained commercial output are different observations. A usable production record needs viable cell yield, doubling time, medium recipe and grade, transfer efficiency, contamination losses, downtime, utilization, downstream losses, quality acceptance and the final formulation. Preserve unsuccessful runs and supplier assumptions as well as the best result.

Serum-free is not automatically animal-component-free, chemically defined, food-grade, affordable or halal-compliant throughout the cell-bank history. The Schenzle paper addresses alternatives to serum albumins in FBS-free media; its title and research record do not certify an industrial chicken process. The PDF’s detailed historical-input claim still needs full-methods confirmation. General culture-media guidance likewise cannot determine food or religious compliance.[ \[CO-S15\]](https://www.nature.com/articles/s41598-025-99603-7)[ \[CO-S05\]](https://www.thermofisher.com/us/en/home/references/gibco-cell-culture-basics/cell-culture-environment/culture-media.html)

## **One verified retail example**

GOOD Meat’s May 2024 announcement describes a 120 g pack priced at SGD 7.20, with 3% cultivated chicken. Dividing the pack price by its finished mass gives SGD 60 per kg of finished product. If the declared percentage is a mass fraction, the pack contains 3.6 g of cultivated component. Neither calculation is the production cost or selling price of pure cultured biomass. The announcement is a dated company launch record, not evidence of continued availability in September 2026 or profitable sales volume.[ \[CO-S11\]](https://www.goodmeat.co/all-news/good-meat-begins-the-worlds-first-retail-sales-of-cultivated-chicken)

## **Economics and environmental comparisons**

Humbird’s scale-up analysis, Sinke’s prospective 2030 assessment and Risner’s cradle-to-gate assessment concern modeled systems with different assumptions. Their results should remain scenario-specific. This review does not freshly reproduce their inventories or claim a universal numerical advantage over chicken. The Risner full text was not accessible through the cited link during this audit.[ \[CO-S12\]](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/bit.27848)[ \[CO-S13\]](https://ce.nl/wp-content/uploads/2023/01/CE_Delft_200220_Ex-ante-LCA-of-commercial-scale-CM-production-in-2030_FINAL_2.pdf)[ \[CO-S14\]](https://pmc.ncbi.nlm.nih.gov/articles/PMC11744764/)

The next comparison should state electricity and heat sources, medium purity, yield, utilization, capital assumptions, financing, waste treatment, transport and the conventional comparator. Use a finished-product kilogram, an edible serving and an appropriate protein or nutritional basis where data permit. Keep the cultivated fraction explicit. A beef comparator alone does not answer a cultivated-chicken decision, and a future clean-energy case is not the current local grid.

A claim about net environmental benefit also needs deployment and displacement. Calculate impacts of the alternative actually sold, subtract the impacts of the food actually displaced, and include additional consumption or rebound. Avoid combining the most favorable assumptions from incompatible production systems. Report sensitivity to uncertain parameters rather than a single apparently precise cost or emissions figure.

## **Safety nutrition and product stewardship**

FAO and WHO’s 2023 report is a relevant foundation, but the full report was not successfully obtained in this review; the accessible institutional summaries do not establish the safety of an individual product. Singapore’s guidance explicitly asks for evidence on toxicity, allergenicity, production methods and dietary exposure.[ \[CO-S03\]](https://www.who.int/publications/i/item/9789240070943)[ \[CO-S04\]](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en)[ \[GP-S14\]](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food)

For a proposed dossier, document cell identity and stability, microbiological controls, residual processing substances, scaffold and medium inputs, allergens, validated cleaning, traceability, storage conditions and shelf life. These are review questions, not findings that every listed hazard is present. Define release criteria, recall responsibility and the change-control process for reformulation.

Measure the finished product’s composition and serving size. Assess protein quality where relevant, sodium, fats, fortification, allergens and the meal displaced. “Animal-free,” “healthy,” “equivalent to chicken” and “nutritionally superior” each need their own substantiation. None follows automatically from cultivation technology or a halal determination.

# **8 Implications for the wider repository**

The AI/protein review, comparative synthesis and orientation material remain useful background, but they answer broader questions than the cultivated-chicken PDF. Their own methodology appropriately labels the work a selective scoping synthesis, with pending human verification. The updated report retains those boundaries.[ \[R-AI\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/ai-protein/literature-review.md)[ \[R-METHOD\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/RESEARCH-METHOD.md)

## **AI and the production counterfactual**

Evaluate AI against a suitable non-AI workflow using held-out performance, experiments required, reproducibility, usable yield and cost at the relevant scale. A protein-structure prediction or media-optimization result should not be converted directly into lower retail prices or fewer animals. The conventional sector’s technology also changes; a stationary incumbent comparator can overstate the alternative’s advantage. These are proposed evaluation standards, not newly measured effects.

## **Forecasting methods**

Repeated model responses are not independent empirical observations. A spread of answers is not a calibrated prediction interval. A forecasting pilot needs resolvable questions, source cutoffs, model versions, aggregation rules and scores on resolved outcomes. Historical tests using current models can be contaminated by prior training exposure. Keep exploratory scenarios separate from probabilities, and score source reliability separately from forecast accuracy. These distinctions are already present in the repository and should survive any condensed presentation.[ \[R-AI\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/ai-protein/literature-review.md)

## **Capabilities market claims and policy evidence**

The comparative dataset’s 14 capability locations mark documented institutions or programs. They do not measure the size of a workforce, vacancies, labor shortages or national technical readiness. A map should preserve approximate-location labels and evidence type. A workforce claim requires occupation-specific demand, skills, time to hire and evidence that missing staff delay production.

Orientation sources include advocacy reports, company announcements and public career information. Record the publication year separately from the year of activity, the category boundary and the original data provider. Broad plant-based-food sales are not plant-based-meat sales. Funding commitments, awards, disbursements, private investment and operating infrastructure are different quantities. This review checked their catalog links but did not re-estimate those market or employment statistics.

Policy recommendations should be conditional on a demonstrated constraint and an observable outcome. Shared pilot infrastructure, public data and regulatory support may be useful, but their marginal value requires costs, additionality, alternatives and local delivery evidence. Include nutrition, affordability, farmer and worker transitions, ownership of technology and access to benefits alongside animal welfare. Do not assume advanced biomanufacturing must be the best use of every research or policy budget.

# **9 Scenario design and animal outcomes**

## **A defensible model contract**

The PDF’s proposed scenario structure is reasonable only under its stated baseline contract: reference demand must describe full access and acceptance before the new adjustments. If the baseline already incorporates those constraints, multiplying by them again double-counts their effects. The baseline owner must confirm units, product category, price, year, segments, channels and partitions before the model runs.

  
  

|  |  |
| :-: | :-: |
| \*\*Input or output\*\* | \*\*Required interpretation\*\* |
| Reference demand D | Finished-product kg per year at a stated price, product and market definition. Not population multiplied by willingness to try. |
| Legal access L | A scoped 0 or 1 only when supported; otherwise unknown. An application or general pathway does not equal 1. |
| Acceptance factor H | A defined fraction from 0 to 1, or unknown. Religious eligibility and ordinary consumer preference must not be counted twice. |
| Allocated supply K | Saleable finished-product capacity allocated across markets and channels; shared supply cannot be assigned in full to each market. |
| Realized sales Q | Limited by both eligible demand and allocated supply. Calculate only for compatible, non-overlapping records. |
| Cultivated fraction | A separate formulation field for biomass accounting, nutrition and environmental inventory; it is not a displacement coefficient. |
| Missing output | A reason-coded non-result such as blocked\\\_missing\\\_baseline. Do not silently substitute zero or manufacture probability estimates. |

 

In words, calculate adjusted demand within each disjoint segment by applying the supported access and acceptance factors to reference demand. Sum only compatible segments, then limit sales to the supply allocated to that market. Validate shared supply pools, product and price compatibility, nonnegative quantities and unknown values before any aggregation. The research question must specify whether the output is potential demand, orders, fulfilled sales or consumption.

## **From sales to animal welfare**

Finished-product sales do not equal animals spared. First measure which conventional foods decline relative to a credible counterfactual. Then estimate how that demand change affects production after trade, inventory, prices and supply response. Finally convert the production change by species using appropriate edible yields and welfare assumptions. Track donor animals and other animal-derived production inputs separately.

For a hybrid product, the cultivated fraction determines biomass use but does not mechanically determine what the finished meal displaces. A 3% hybrid might replace a whole conventional meal, replace a plant-based meal, or add an extra purchase. Those possibilities require observed evidence. Use a vector of displaced products rather than one universal coefficient, and allow zero, additive consumption or cross-species substitution where the data support it.

Distinguish avoided growth from an absolute fall in production. A future industry that is smaller than the no-intervention counterfactual may still be larger than today. Do not apply a supply-response factor twice if a published animal-impact conversion already contains it. Report animal numbers and welfare consequences separately from tonnes, emissions and nutritional outcomes.

## **Scenarios worth testing once inputs exist**

|  |  |
| :-: | :-: |
| \*\*Exploratory condition\*\* | \*\*Evidence that would change the decision\*\* |
| Product clears review and replaces chicken | Named approvals and certificates, reproducible supply, repeated purchases and measured chicken substitution. |
| Scientific progress stalls before sale | Good laboratory results alongside unresolved dossier, finance, manufacturing, price or trust constraints. |
| Accessible plant foods outperform the new product | Comparable meal experiments show greater substitution or value from available alternatives. |
| Conventional production retains its advantage | The alternative adds consumption, fails to scale, or improves less quickly than its actual competitor. |

 

These cases are stress tests, not mutually exclusive probability buckets. No calibrated sales, approval-date, climate or animal-welfare forecast is supplied because the necessary baseline and empirical links are absent.

# **10 A research plan that closes the important gaps**

## **Product and institutional work**

Choose one target formulation, origin history, site and channel before approaching reviewers. Prepare a versioned dossier summary. Seek written clarification from the relevant food authority and certification body on product classification, acceptable evidence, cell origin, medium history, recognition and change control. Use competent local readers for Arabic, Urdu, Malay and relevant Indian-language material. Store the actual response, institution, scope and date rather than converting an informal conversation into an approval.

## **A staged consumer design**

Keep the branch’s plant-based pilot as a distinct near-term study of ordinary food choice. For cultivated chicken, begin with interviews and comprehension testing until a legally available product and suitable tasting permissions exist. An urban feasibility sample can locate barriers and improve questions; it is not nationally representative.

Recruit across food budgets, dietary practices and household purchasing roles. Predefine the meal and its alternatives. In a later authorized study, vary price, formulation information and verified certification information in a randomized design that can separate their effects. Never display a fictitious certificate or claim approval the product lacks. Measure understanding, trial, actual spending, repeat purchase, waste and the displaced food, including changes elsewhere in the household diet.

Set sample size from the primary outcome, expected variation and clustering, rather than importing the size of a previous convenience survey. Preregister exclusions and comparisons, retain attrition and null results, document translation and consent, and analyze subgroup differences without treating national or religious identity as a fixed preference. Repeated purchasing and substitution need follow-up, not a single tasting score.

## **Prioritized work packages**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Priority\*\* | \*\*Deliverable\*\* | \*\*Completion condition\*\* |
| 1 Reproducibility | Recover the exact PDF source package and missing model files. | A pinned revision rebuilds the report and runs the claimed tests with documented expected outputs. |
| 1 Scope and permissions | One product dossier and jurisdiction-specific decision map. | Each access field has a dated, scoped primary record or an explicit unknown status. |
| 2 Data provenance | Re-obtain the FAO table, inaccessible household report and key full texts. | Values and methods are checked against originals, with page locators and discrepancies logged. |
| 2 Demand evidence | Pilot instrument and feasible recruitment plan. | The primary outcome and counterfactual are defined; no national demand estimate is implied. |
| 3 Supply and impacts | Comparable process, cost, environmental and substitution records. | Uncertainty and product boundaries are explicit and independent validation is available. |
| 3 Model release | Versioned baseline and integrated scenario outputs. | Units, partitions, supply constraints and unknown states pass tests; outputs can be traced to inputs. |

 

These priorities are a proposed order of work, not commitments or estimates of how quickly regulators, data owners or suppliers will respond. Expand commercial or welfare claims only when the relevant completion condition is satisfied.

# **11 Reproducibility and citation repairs**

The repository verification script is useful and passed in both snapshots. It is not the PDF’s claimed test suite. The following files named in the PDF were absent: tools/integrate.mjs, tools/scenario.mjs, tools/scenario.test.mjs, tools/build-figures.mjs, tools/validate.mjs, tools/build-report.mjs and tools/render-report.mjs. The named analysis/baseline.json and analysis/scenario-results.json were also absent.

The same problem affects the 15 evidence tables, six figure-data files, four focal dossiers, three precedent dossiers and review or defect records described by the PDF. Recover their original paths and revision from the author; do not reconstruct missing code and present it as the code that generated the paper. Until recovered, revise the validation sentence to: “The paper reports 23 passing synthetic tests; that result was not reproducible from the repository snapshots available for this review.”

A release manifest should link report version, source records, extracted evidence, raw-data provenance, transformations, test command and environment. Store retrieval date, original publication or effective date, exact locator, evidence type, access level, funding or conflict information, and the claim each source supports. Keep “author reported,” “independently checked,” “unresolved” and “contradicted” separate.

Preserve the PDF’s CO, SA and GP identifiers as stable references. Fill missing bibliographic fields from inspected records without renumbering them merely to remove gaps. Link the Bryant original and correction under one evidence-family identifier. Apply the same approach to preprints, accepted manuscripts, publisher records, company restatements and multiple pages about one policy decision.

Separate automated link status from evidence appraisal in the repository. A successful HTTP retrieval or matching title does not validate a coefficient, causal interpretation, regulatory scope or current commercial claim. A blocked page is not necessarily a dead link. Update the dated branch scope before merging, and keep the cultivated-chicken report linked to its own source package rather than silently treating the broader catalog as its supporting data.

# **Appendix A Stored protein supply data**

These are the repository’s FAO-derived values, not a newly downloaded FAO extract. Supply is measured in grams of protein per person per day; the share column is percent. All 12 populated rows reproduce internally at the displayed precision. Supply availability is not measured by individual intake. The country selection is purposive and is not a representative North–South sample.[ \[R-DATA\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/research/comparative-protein/protein-data.csv)

|  |  |  |  |  |  |  |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| \*\*Country\*\* | \*\*Total 2010\*\* | \*\*Animal 2010\*\* | \*\*Total 2023\*\* | \*\*Animal 2023\*\* | \*\*Plant 2023\*\* | \*\*Animal share 2023\*\* |
| United States | 119.1 | 80.4 | 123.1 | 82.9 | 40.2 | 67.3 |
| Germany | 110.2 | 70.1 | 109.2 | 73.6 | 35.6 | 67.4 |
| United Kingdom | 105.9 | 62.5 | 110 | 65.1 | 44.9 | 59.2 |
| Netherlands | 110.1 | 75.3 | 117.1 | 81.5 | 35.6 | 69.6 |
| Denmark | 112.3 | 70 | 126.3 | 86.8 | 39.5 | 68.7 |
| China | 108.7 | 43.3 | 131 | 54.2 | 76.8 | 41.4 |
| India | 60.4 | 11.5 | 74.6 | 20 | 54.6 | 26.8 |
| Brazil | 101.8 | 56.8 | 106.5 | 68 | 38.5 | 63.8 |
| South Africa | 78.9 | 35.3 | 79.2 | 36.5 | 42.7 | 46.1 |
| Kenya | 57.8 | 17.9 | 55.8 | 14.5 | 41.3 | 26 |
| Nigeria | 62.1 | 9.4 | 57 | 6.6 | 50.4 | 11.6 |
| Zimbabwe | 61.2 | 30.5 | 69.1 | 31.3 | 37.8 | 45.3 |
| Singapore | Missing | Missing | Missing | Missing | Missing | Missing |

 

Derivations: plant protein is total protein less animal protein; animal share is animal protein divided by total protein, expressed as percent. The stored provenance identifies FAO Statistical Yearbook 2025, Table 50, Food Balances, with retrieval on 28 October 2025 and printed-page locators 325–329. The external FAO document could not be retrieved during this review, leaving transcription against the original unresolved.

Singapore is explicitly missing, not zero. Pakistan is not in this extract and no Pakistan value has been imputed. Do not insert the HIES quantities or Indian household nutrient estimates into this supply table: they have different units, data-generation processes and denominators.

# 

# **Appendix B Every reference in the supplied PDF**

All 54 unique linked references were checked for retrieval. The source codes found in the PDF matched these 54 entries; no unmatched code was detected. The initial and follow-up retrievals returned text for 41 URLs, limited challenge content for one, and no usable content for 12. The claim-use column below gives the more important limit on interpretation. A title, landing page or abstract is not full-text verification. Access reflects this review on 21 September 2026, not a guarantee of continued availability.

Codes link directly to the cited source. Titles are shortened for navigation. “Unretrieved” means this environment could not obtain the source; it does not establish that the original URL is permanently broken. “Partial” includes metadata, abstract-only material, accessible summaries and incomplete methods review. “Checked” refers to the named passage or fact, not every claim in that publication.

## **Core evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[CO-S01\\\]  &#10;\](https://iifa-aifi.org/en/56085.html) IIFA Resolution 265 on cultivated meat | Checked | Conditional religious position; read clauses Third to Sixth. No universal process permission or numeric substitution cap. |
| \[\\\[CO-S02\\\]  &#10;\](https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/) MUIS fatwa statement 3 February 2024 | Checked | Conditional permissibility; distinguish product certification and purchasing. |
| \[\\\[CO-S03\\\]  &#10;\](https://www.who.int/publications/i/item/9789240070943) FAO WHO Food safety aspects of cell based food | Partial | WHO landing page available; full report not extracted. Do not claim full-report review. |
| \[\\\[CO-S04\\\]  &#10;\](https://www.fao.org/food-safety/news/detail/Growing-interest-in-cell-based-food-Global-webinar-report/en) FAO global webinar report | Checked | Institutional summary dated 29 March 2024; event was in April 2023. Not product safety clearance. |
| \[\\\[CO-S05\\\]  &#10;\](https://www.thermofisher.com/us/en/home/references/gibco-cell-culture-basics/cell-culture-environment/culture-media.html) Thermo Fisher Basics of Culture Media | Partial | General technical material. No food-grade, halal or industrial cost conclusion. |
| \[\\\[CO-S06\\\]  &#10;\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full) Bryant and colleagues consumer survey 2019 | Partial | Original text available; interpret with the correction. Methods were not independently replicated. |
| \[\\\[CO-S07\\\]  &#10;\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2020.00086/full) Bryant and colleagues corrigendum 2020 | Checked | Retain corrected Indian 56.3% and 62.8% intention figures; same evidence family as CO-S06. |
| \[\\\[CO-S08\\\]  &#10;\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766) Ahsan and colleagues Pakistan consumer study | Partial | Journal metadata recovered; full methods not re-obtained. 2022 volume 2 issue 1 pages 111–122. |
| \[\\\[CO-S09\\\]  &#10;\](https://www.nature.com/articles/s41598-026-62416-3) Irfan and colleagues Pakistan study 2026 | Partial | Publisher and accepted-manuscript abstract inspected; n 102. Full methods and background statistics unverified. |
| \[\\\[CO-S10\\\]  &#10;\](https://research.cuhk.edu.hk/en/publications/on-site-sensory-experience-boosts-acceptance-of-cultivated-chicke/) Chong and colleagues on site sensory experience | Partial | Author record supports n 107; Future Foods 9 100326 June 2024. No long-run demand inference. |
| \[\\\[CO-S11\\\]  &#10;\](https://www.goodmeat.co/all-news/good-meat-begins-the-worlds-first-retail-sales-of-cultivated-chicken) GOOD Meat retail launch May 2024 | Checked | Company launch announcement supports pack, price and formulation. Not current sales or pure biomass cost. |
| \[\\\[CO-S12\\\]  &#10;\](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/bit.27848) Humbird Scale up economics for cultured meat | Partial | Publisher material returned. Prospective economic model; no fresh recalculation or achieved-cost verification. |
| \[\\\[CO-S13\\\]  &#10;\](https://ce.nl/wp-content/uploads/2023/01/CE\_Delft\_200220\_Ex-ante-LCA-of-commercial-scale-CM-production-in-2030\_FINAL\_2.pdf) Sinke and colleagues prospective 2030 LCA | Partial | Author-hosted article retrieved. Inventory and calculations not independently reproduced. |
| \[\\\[CO-S14\\\]  &#10;\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11744764/) Risner and colleagues cradle to gate LCA | Unretrieved | PMC returned a challenge and alternate publisher access failed. No newly verified effect estimate. |
| \[\\\[CO-S15\\\]  &#10;\](https://www.nature.com/articles/s41598-025-99603-7) Schenzle and colleagues alternatives to serum albumins | Partial | Article and publisher PDF located; detailed historical-input and methods claims still require confirmation. |
| \[\\\[CO-S16\\\]  &#10;\](https://pmc.ncbi.nlm.nih.gov/articles/PMC11722975/) Khaleel and colleagues UAE consumer study | Partial | Article material initially returned; methods could not be fully rechecked. Keep sample-limited interpretation. |

**South Asia evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[SA-S03\\\]  &#10;\](https://faolex.fao.org/docs/pdf/pak164529.pdf) Pakistan Halal Authority Act 2016 | Checked | Gazette text via FAOLEX. Check territorial scope and commencement; later consolidation not established. |
| \[\\\[SA-S04\\\]  &#10;\](https://pakistanhalalauthority.gov.pk/Files/PHA%20Halal%20Mark%20Scheme%20operationalization%20notification.jpg) PHA mark scheme notification 2025 | Unretrieved | Notification image unavailable. Do not upgrade the PDF’s reported reading to a fresh check. |
| \[\\\[SA-S05\\\]  &#10;\](https://pnac.gov.pk/Halal-Certification-Bodies/Active) PNAC active halal certification bodies | Unretrieved | Current register not recovered. No inferred certifier count, validity or cultivated scope. |
| \[\\\[SA-S06\\\]  &#10;\](https://smiic.org/en/accreditation-council-ac) SMIIC Accreditation Council | Partial | Institutional page returned. Membership and accreditation are not a product certificate. |
| \[\\\[SA-S07\\\]  &#10;\](https://logcluster.org/sites/default/files/public/2022-10/pakistanimport-policyministry-commerce22-april-2022-compressed1-compressed.pdf) Pakistan Import Policy Order 2022 | Unretrieved | Cited reproduction unavailable; amendments and present import classification unresolved. |
| \[\\\[SA-S08\\\]  &#10;\](https://faolex.fao.org/docs/pdf/pak115231.pdf) Punjab Food Authority Act 2011 | Checked | FAOLEX reproduction available; authority mapping supported. Current complete amendments need confirmation. |
| \[\\\[SA-S09\\\]  &#10;\](https://www.fssai.gov.in/upload/uploadfiles/files/Gazette\_Notification\_NonSpecified\_Food\_Ingredients\_15\_09\_2017.pdf) FSSAI non specified food regulations 2017 | Checked | Gazette approval route available; no named cultivated-product clearance inferred. |
| \[\\\[SA-S10\\\]  &#10;\](https://fssai.gov.in/upload/uploadfiles/files/Compendium\_FSS\_NFS\_FA\_17\_10\_2022.pdf) FSSAI regulations compendium 2022 | Checked | Prior-approval framework and application requirements. Process deadlines are not observed approval times. |
| \[\\\[SA-S11\\\]  &#10;\](https://fssai.gov.in/upload/uploadfiles/files/Status\_of\_Application\_as\_on\_09\_03\_2026.pdf) FSSAI application status 9 March 2026 | Partial | Dated register retrieved; exhaustive current product-name search not independently repeated. |
| \[\\\[SA-S12\\\]  &#10;\](https://i-cas-halal.qcin.org/) QCI i CAS Halal export portal | Partial | Portal available. Export conformity and domestic food approval are separate. |
| \[\\\[SA-S13\\\]  &#10;\](https://content.dgft.gov.in/Website/Notification\_ITCHS.pdf) DGFT ITC HS export schedule | Checked | Specified export conditions include destination requirements. Read with amendments, not as universal scope. |
| \[\\\[SA-S14\\\]  &#10;\](https://content.dgft.gov.in/Website/dgftprod/25fb264d-cd73-40f5-851f-31b5263357ef/Notification%2059%20dated%2009.02.26.pdf) DGFT Notification 59 February 2026 | Unretrieved | Official file located in search but text unavailable. Consolidated current requirements remain unresolved. |
| \[\\\[SA-S15\\\]  &#10;\](https://nabcb.qci.org.in/pc-048/) NABCB accreditation PC 048 | Checked | Scope and validity visible. Conventional animal-product scope does not itself cover cultivated chicken. |
| \[\\\[SA-S16\\\]  &#10;\](https://www.biokraftfoods.com/) Biokraft Foods company website | Partial | Company material returned. No independently audited capacity, throughput or approval verified. |
| \[\\\[SA-S17\\\]  &#10;\](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-1.pdf) Pakistan HIES 2024 to 2025 economic report | Checked | Table 3.7.C page 25 quantities reread. Use table values; microdata and weighting not replicated. |
| \[\\\[SA-S18\\\]  &#10;\](https://mospi.gov.in/sites/default/files/publication\_reports/Final\_Report\_HCES\_2023-24L.pdf) India HCES Report 592 | Unretrieved | Original report link failed. Previously quoted expenditure values not treated as freshly verified. |

 

## **Gulf and precedent evidence**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Reference\*\* | \*\*Review level\*\* | \*\*Use and remaining limit\*\* |
| \[\\\[GP-S01\\\]  &#10;\](https://www.goodmeat.co/all-news/leading-shariah-scholars-rule-cultivated-meat-can-be-halal) GOOD Meat scholar advice announcement 2023 | Partial | Announcement located; company-reported advice. Detailed process-compliance claim not freshly re-established. |
| \[\\\[GP-S02\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2021-10/NovelFoodGeneralRequirements.pdf) SFDA General Requirements of Novel Foods | Checked | Cell and tissue scope and novel-food requirements visible. Verify controlling version and Arabic text. |
| \[\\\[GP-S03\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2021-10/GuideApplyApprovalNovelFoods.pdf) SFDA guide to novel food approval | Checked | Application information available. Guide does not prove product permission or achieved review speed. |
| \[\\\[GP-S04\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2026-08/SFDA-FRigsterE.pdf) SFDA food registration guide 2026 | Unretrieved | Cited English file not recovered. Current route and version require confirmation. |
| \[\\\[GP-S05\\\]  &#10;\](https://sfda.gov.sa/en/faq/what-are-halal-centers-and-how-apply-approval-request-external-centers) SFDA FAQ on external halal centers | Partial | Official FAQ returned. General role does not settle a specific certificate or destination scope. |
| \[\\\[GP-S06\\\]  &#10;\](https://www.sfda.gov.sa/sites/default/files/2023-11/511hala.pdf) Saudi recognized bodies list 2023 | Partial | Historical PDF available. Recheck current recognition and category for the proposed product. |
| \[\\\[GP-S07\\\]  &#10;\](https://sfda.gov.sa/en/news/saudi-arabia-singapore-sign-mou-mutual-recognition-halal-certificates-product-quality) Saudi Singapore halal recognition MoU news | Unretrieved | News URL unavailable; existence corroborated by MUIS annual report, GP-S08. |
| \[\\\[GP-S08\\\]  &#10;\](https://isomer-user-content.by.gov.sg/48/c463da6b-c40f-4595-b13e-2ec8b5e672dc/Muis%20Annual%20Report%202023.pdf) MUIS Annual Report 2023 | Checked | Printed page 32 records Saudi UAE and Jordan MoUs. No cultivated-product scope inferred. |
| \[\\\[GP-S09\\\]  &#10;\](https://www.moiat.gov.ae/en/programs/halal) MOIAT halal programme | Unretrieved | Official page inaccessible. Do not infer absence of a program or of conditions. |
| \[\\\[GP-S10\\\]  &#10;\](https://moiat.gov.ae/en/programs/halal/registered-halal-certification-bodies) MOIAT registered certification bodies | Unretrieved | Register not recovered. Current recognized issuer and scope unresolved. |
| \[\\\[GP-S11\\\]  &#10;\](https://www.wam.ae/en/article/bmd6z4n-abu-dhabi-launches-pioneering-regulatory-framework) WAM Abu Dhabi novel food initiative 2025 | Checked | Prospective initiative and expected time savings. No measured approval performance or product permit. |
| \[\\\[GP-S12\\\]  &#10;\](https://investinabudhabi.gov.ae/News/AGWA-and-Believer-Meats-to-Develop-Cultivated-Meat-Capabilities-in-Abu-Dhabi) ADIO and Believer development announcement 2024 | Checked | Investment and development announcement. No confirmed operating plant or production volume. |
| \[\\\[GP-S14\\\]  &#10;\](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/guidelines-on-applying-for-pre-market-approval-for-a-novel-food) SFA premarket novel food guidelines | Checked | Product and process-specific review; material process changes need renewed approval. |
| \[\\\[GP-S15\\\]  &#10;\](https://assets.egazette.gov.sg/2025/Legislative%20Supplements/Subsidiary%20Legislation%20Supplement/713.pdf) Singapore authorization regulations S 713 2025 | Partial | Gazette available; complete legal consolidation and a product-specific application not reviewed. |
| \[\\\[GP-S16\\\]  &#10;\](https://www.halal.gov.my/?data=bW9kdWxlcy9jb2xsYXBzaWJsZV9jb250ZW50Ozs7Ow%3D%3D\&utama=CB\_LIST) JAKIM foreign halal certification body portal | Partial | Portal returned. Referenced standard versions and current recognition need direct confirmation. |
| \[\\\[GP-S17\\\]  &#10;\](https://ciri.islam.gov.my/view/fatwa\_cetak.php?id=16914) JAKIM CIRi cultured meat record | Unretrieved | Cited record timed out. Added A02 is a separate named authority and must not be conflated with it. |
| \[\\\[GP-S18\\\]  &#10;\](https://cmsbl.halal.go.id/uploads/Decree\_Kepkaban\_221\_2025\_Implementation\_Procedure\_of\_Foreign\_Halal\_Certificate\_Registration\_bb95097144.pdf) BPJPH Decree 221 of 2025 | Checked | Foreign-certificate registration provisions read. Recognition does not by itself complete registration. |
| \[\\\[GP-S19\\\]  &#10;\](https://www.muis.gov.sg/resources/media-releases/8-aug-24-singapore-signs-halal-cooperation-memorandum-of-understanding-with-indonesia/) MUIS Indonesia cooperation MoU 2024 | Partial | Official statement available. Bilateral cooperation does not settle destination product registration. |
| \[\\\[GP-S20\\\]  &#10;\](https://www.uaelegislation.gov.ae/en/legislations/1161/download) UAE Federal Food Safety Law 10 of 2015 | Unretrieved | Download refused. No fresh complete statutory interpretation is claimed. |
| \[\\\[GP-S21\\\]  &#10;\](https://u.ae/en/information-and-services/health-and-fitness/food-safety-and-health-tips) UAE government food safety overview | Unretrieved | No readable text returned. Overview cannot replace legislation or product decisions. |
| \[\\\[GP-S22\\\]  &#10;\](https://www.sfda.gov.sa/en/news/18781) SFDA food innovation statement December 2025 | Partial | Official statement retrieved. Authority self-report, not a named product permit or performance audit. |
| \[\\\[GP-S23\\\]  &#10;\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/fr/?lnk=1\&url=https://workspace.fao.org/sites/codex/Meetings/CX-701-47/CRDs/cac47\_crd04x.pdf) Codex CAC47 CRD04 country contributions 2024 | Checked | Saudi and UAE country descriptions inspected. September 2024 snapshot, not a consolidated current law review. |

 

## **Additional primary sources**

|  |  |
| :-: | :-: |
| \*\*Reference\*\* | \*\*Locator and contribution\*\* |
| \[\\\[A01\\\]\](https://mospi.gov.in/sites/default/files/press\_release/press\_note\_Nutritional%20Intake%20in%20India\_02072025.pdf) MoSPI Nutritional Intake in India | 2 July 2025 press note. Pages 5 and 7 distinguish food-group shares and adjusted from unadjusted nutrient estimates. The source also appears in the repository branch. |
| \[\\\[A02\\\]\](https://muftiwp.gov.my/en/artikel/irsyad-fatwa/irsyad-fatwa-umum-cat/4887-irsyad-al-fatwa-siri-ke-595-daging-kultur-cultured-meat-menurut-perspektif-syarak) Federal Territories Mufti Office | Irsyad Hukum 595, 24 July 2021. Official Malay discussion of cultivated meat; AI-assisted interpretation in section 4 requires qualified local confirmation. |
| \[\\\[A03\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306) Press Information Bureau | Implementation of BioE3 Policy, 23 July 2026, smart-protein paragraph. Nine supported projects across three categories, not nine cultivated-product approvals. |
| \[\\\[A04\\\]\](https://www.nature.com/articles/s41598-026-62416-3\_reference.pdf) Irfan accepted manuscript | Publisher-hosted accepted version. Abstract and introductory material inspected; full methods not verified. Same evidence family as CO-S09. |

# **Appendix C Repository catalog retrieval audit**

This appendix accounts for every one of the 159 catalog identities in the newer branch. These records overlap the PDF bibliography and one another in topic and evidence families; the two counts must not be added and called independent studies. Catalog IDs are navigation aids. Original collection IDs and their existing pending human-review fields remain authoritative.[ \[R-CATALOG\]](https://github.com/Omarzaf/sentient-futures-research/blob/9896751e53c1b851a874153cbdf6cd72c217058a/sources/catalog.json)

Legend: Returned means the cited URL returned text in at least one attempt, including publisher metadata, a landing page or an abstract. Limited means only a short or challenge response was recovered. Unavailable means no usable content was retrieved. Best access across attempts is shown; several pages were intermittent. Totals are 94 Returned, 4 Limited and 61 Unavailable. The columns do not certify full-text reading, claim validity or link permanence. Some sources were available through a different URL, as recorded in Appendix B.

Titles below are shortened to keep the inventory readable. Each catalog code opens the original source URL. The pinned catalog retains the full title, collection occurrences, original source IDs and prior access or limitation notes. Marketing pages and advocacy sources retain their original evidence type; being included is not endorsement.

  

|  |  |  |
| :-: | :-: | :-: |
| \*\*Catalog ID\*\* | \*\*Source title\*\* | \*\*Retrieval\*\* |
| \[\\\[SRC-001\\\]\](https://onlinelibrary.wiley.com/doi/10.1002/aepp.13232) | Meet the meatless: Demand for new generation plant-based meat alternatives | Returned |
| \[\\\[SRC-002\\\]\](https://onlinelibrary.wiley.com/doi/10.1002/aepp.13280) | Consumer spending patterns for plant-based meat alternatives | Returned |
| \[\\\[SRC-003\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201/) | Scale-up economics for cultured meat | Limited |
| \[\\\[SRC-004\\\]\](https://par.nsf.gov/servlets/purl/10466545) | Multi-objective Bayesian algorithm automatically discovers low-cost high-growth serum-free media for… | Unavailable |
| \[\\\[SRC-005\\\]\](https://doi.org/10.1007/s11367-020-01771-3) | A life cycle environmental sustainability analysis of microbial protein production via power-to-food approaches | Unavailable |
| \[\\\[SRC-006\\\]\](https://doi.org/10.1007/s11367-022-02128-8) | Ex-ante life cycle assessment of commercial-scale cultivated meat production in 2030 | Returned |
| \[\\\[SRC-007\\\]\](https://pubmed.ncbi.nlm.nih.gov/33276014/) | A systematic review on consumer acceptance of alternative proteins: Pulses, algae, insects, plant-based… | Unavailable |
| \[\\\[SRC-008\\\]\](https://doi.org/10.1016/j.biosystemseng.2022.02.013) | A machine learning framework to predict the next month's daily milk yield, milk composition and milking… | Unavailable |
| \[\\\[SRC-009\\\]\](https://www.sciencedirect.com/science/article/pii/S0956713520303066) | Consumer acceptance of cultured meat in urban areas of three cities in China | Unavailable |
| \[\\\[SRC-010\\\]\](https://www.sciencedirect.com/science/article/abs/pii/S0306919220301354) | Consumer preferences for farm-raised meat, lab-grown meat, and plant-based meat alternatives: Does… | Unavailable |
| \[\\\[SRC-011\\\]\](https://www.sciencedirect.com/science/article/pii/S0306919222001099) | The social impacts of a transition from conventional to cultivated and plant-based meats: Evidence from Brazil | Unavailable |
| \[\\\[SRC-012\\\]\](https://www.sciencedirect.com/science/article/pii/S0306919226000862) | Estimating plant-based milk impacts on U.S. fluid milk prices and quantities | Unavailable |
| \[\\\[SRC-013\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329318309996) | Consumers' willingness to purchase three alternatives to meat proteins in the United Kingdom, Spain, Brazil… | Unavailable |
| \[\\\[SRC-014\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329323001568) | Estimating consumers' willingness to pay for plant-based meat and cultured meat in China | Unavailable |
| \[\\\[SRC-015\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329323002616) | A meta-review of consumer behaviour studies on meat reduction and alternative protein acceptance | Unavailable |
| \[\\\[SRC-016\\\]\](https://www.sciencedirect.com/science/article/pii/S0950329325003362) | Feeding the future: A comparison of drivers and barriers towards consumers' acceptance of plant-based… | Unavailable |
| \[\\\[SRC-017\\\]\](https://www.sciencedirect.com/science/article/pii/S2666833524001175) | Beyond the cow: Consumer perceptions and information impact on acceptance of precision… | Unavailable |
| \[\\\[SRC-018\\\]\](https://eref.uni-bayreuth.de/id/eprint/92470/) | How innovation-friendly is the EU Novel Food Regulation? The case of cellular agriculture | Returned |
| \[\\\[SRC-019\\\]\](https://ris.utwente.nl/ws/files/247793059/Haasnoot2013dynamic.pdf) | Dynamic adaptive policy pathways A method for crafting robust decisions for a deeply uncertain world | Returned |
| \[\\\[SRC-020\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC10481291/) | Households food consumption pattern in Pakistan: Evidence from recent household integrated economic survey | Limited |
| \[\\\[SRC-021\\\]\](https://doi.org/10.1016/j.isci.2021.102229) | Behavioral and neurophysiological evidence suggests affective pain experience in octopus | Unavailable |
| \[\\\[SRC-022\\\]\](https://doi.org/10.1016/j.jclepro.2021.127177) | Life cycle assessment of burger patties produced with extruded meat substitutes | Unavailable |
| \[\\\[SRC-023\\\]\](https://doi.org/10.1016/j.jenvp.2021.101589) | Price of change: Does a small alteration to the price of meat and vegetarian options affect their sales? | Unavailable |
| \[\\\[SRC-024\\\]\](https://doi.org/10.1016/j.jenvp.2023.102226) | Can you default to vegan? Plant-based defaults to change dining practices on college campuses | Unavailable |
| \[\\\[SRC-025\\\]\](https://pubmed.ncbi.nlm.nih.gov/31732401/) | Consumer acceptance of cultured meat in Germany | Returned |
| \[\\\[SRC-026\\\]\](https://www.sciencedirect.com/science/article/pii/S2468227622002113) | Planetary health and the promises of plant-based meat from a sub-Saharan African perspective: A review | Unavailable |
| \[\\\[SRC-027\\\]\](https://doi.org/10.1016/j.scitotenv.2023.164988) | Toward sustainable culture media: Using artificial intelligence to optimize reduced-serum formulations for… | Unavailable |
| \[\\\[SRC-028\\\]\](https://www.sciencedirect.com/science/article/pii/S2352550922003049) | Why can't the alternative become mainstream? Unpacking the barriers and enablers of sustainable protein… | Unavailable |
| \[\\\[SRC-029\\\]\](https://www.cambridge.org/core/journals/journal-of-agricultural-and-applied-economics/article/alternative-livestock-revolution-prospects-for-consumer-acceptance-of-plantbased-and-cultured-meat-in-south-africa/A79AF7AC795CF15549EFDB3AC7A1B380) | The alternative livestock revolution: Prospects for consumer acceptance of plant-based and cultured meat in… | Returned |
| \[\\\[SRC-030\\\]\](https://doi.org/10.1017/awf.2023.4) | Estimating global numbers of farmed fishes killed for food annually from 1990 to 2019 | Unavailable |
| \[\\\[SRC-031\\\]\](https://doi.org/10.1021/acs.est.5b01614) | Anticipatory Life Cycle Analysis of In Vitro Biomass Cultivation for Cultured Meat Production in the United… | Unavailable |
| \[\\\[SRC-032\\\]\](https://doi.org/10.1021/acsfoodscitech.4c00281) | Environmental Impacts of Cultured Meat: A Cradle-to-Gate Life Cycle Assessment | Unavailable |
| \[\\\[SRC-033\\\]\](https://doi.org/10.1021/es200130u) | Environmental Impacts of Cultured Meat Production | Unavailable |
| \[\\\[SRC-034\\\]\](https://www.nature.com/articles/s41467-025-58475-1) | Associations between national plant-based vs animal-based protein supplies and age-specific mortality in… | Returned |
| \[\\\[SRC-035\\\]\](https://www.nature.com/articles/s41538-026-00841-4) | Trends, challenges, and opportunities for the United States alternative meat and seafood sector:… | Returned |
| \[\\\[SRC-036\\\]\](https://doi.org/10.1038/s41586-021-03819-2) | Highly accurate protein structure prediction with AlphaFold | Unavailable |
| \[\\\[SRC-037\\\]\](https://doi.org/10.1038/s41586-022-04629-w) | Projected environmental benefits of replacing beef with microbial protein | Unavailable |
| \[\\\[SRC-038\\\]\](https://doi.org/10.1038/s41598-022-16996-5) | Most plant-based meat alternative buyers also buy meat: an analysis of household demographics, habit… | Unavailable |
| \[\\\[SRC-039\\\]\](https://doi.org/10.1038/s42003-022-03423-8) | Simple and effective serum-free medium for sustained expansion of bovine satellite cells for cell cultured meat | Unavailable |
| \[\\\[SRC-040\\\]\](https://doi.org/10.1038/s43016-022-00658-w) | Spontaneous immortalization of chicken fibroblasts generates stable, high-yield cell lines for serum-free… | Unavailable |
| \[\\\[SRC-041\\\]\](https://www.nature.com/articles/s43016-024-01022-w) | Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken using… | Unavailable |
| \[\\\[SRC-042\\\]\](https://doi.org/10.1088/1748-9326/ac4fda) | Impact of plant-based meat alternatives on cattle inventories and greenhouse gas emissions | Unavailable |
| \[\\\[SRC-043\\\]\](https://doi.org/10.1093/ajcn/nqaa203) | A randomized crossover trial on the effect of plant-based compared with animal-based meat on… | Unavailable |
| \[\\\[SRC-044\\\]\](https://pubmed.ncbi.nlm.nih.gov/36151900/) | Plant-based meats in China: a cross-sectional study of attitudes and behaviours | Unavailable |
| \[\\\[SRC-045\\\]\](https://doi.org/10.1126/sciadv.adp1528) | Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy | Unavailable |
| \[\\\[SRC-046\\\]\](https://doi.org/10.1146/annurev-animal-021022-055132) | Cultivated Meat: Progress and Remaining Challenges | Unavailable |
| \[\\\[SRC-047\\\]\](https://doi.org/10.1177/1745691615577794) | Identifying and Cultivating Superforecasters as a Method of Improving Probabilistic Predictions | Returned |
| \[\\\[SRC-048\\\]\](https://www.scielo.org.za/scielo.php?pid=S0038-23532025000400011\&script=sci\_arttext) | Mapping underutilised and emerging food sources and technologies as solutions to food insecurity in South… | Returned |
| \[\\\[SRC-049\\\]\](https://ejournal.upi.edu/index.php/AJSEE/article/view/38766) | Attitudes and Perceptions Towards Cultured Meat Among General Population in Pakistan | Returned |
| \[\\\[SRC-050\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report/agricultural-and-food-markets-trends-and-prospects\_c5cd366b.html) | OECD–FAO Agricultural Outlook 2026–2035: Agricultural and food markets: Trends and prospects | Returned |
| \[\\\[SRC-051\\\]\](https://ers.usda.gov/publications/113704) | Precision Dairy Farming, Robotic Milking, and Profitability in the United States | Returned |
| \[\\\[SRC-052\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2019.00011/full) | A Survey of Consumer Perceptions of Plant-Based and Clean Meat in the USA, India, and China | Returned |
| \[\\\[SRC-053\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2021.678491/full) | Don't Have a Cow, Man: Consumer Acceptance of Animal-Free Dairy Products in Five Countries | Returned |
| \[\\\[SRC-054\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1303448/full) | Price above all else: an analysis of expert opinion on the priority actions to scale up production and… | Returned |
| \[\\\[SRC-055\\\]\](https://www.mdpi.com/2072-6643/14/16/3292) | Understanding Key Factors Influencing Consumers' Willingness to Try, Buy, and Pay a Price Premium for… | Unavailable |
| \[\\\[SRC-056\\\]\](https://www.mdpi.com/2071-1050/12/11/4377) | Is India Ready for Alt-Meat? Preferences and Willingness to Pay for Meat Alternatives | Unavailable |
| \[\\\[SRC-057\\\]\](https://www.nsfc.gov.cn/csc/20345/20348/pdf/2025/202505-799-806.pdf) | 食品化工核心技术的关键科学问题 \\\[Key scientific issues in the core technologies of food chemical engineering\\\] | Returned |
| \[\\\[SRC-058\\\]\](https://doi.org/10.3758/s13428-023-02307-x) | Diminished diversity-of-thought in a standard large language model | Unavailable |
| \[\\\[SRC-059\\\]\](https://www.fao.org/3/cc3912en/cc3912en.pdf) | Contribution of terrestrial animal source food to healthy diets for improved nutrition and health outcomes:… | Unavailable |
| \[\\\[SRC-060\\\]\](https://openknowledge.fao.org/3/cd4313en/cd4313en.pdf) | World Food and Agriculture – Statistical Yearbook 2025 | Unavailable |
| \[\\\[SRC-061\\\]\](https://arxiv.org/abs/2402.18563) | Approaching Human-Level Forecasting with Language Models | Returned |
| \[\\\[SRC-062\\\]\](https://aifs.ucdavis.edu/about/aifs) | AI Institute for Next Generation Food Systems | Returned |
| \[\\\[SRC-063\\\]\](https://altprotein.jobs/career-hiring-report) | AltProtein.Jobs Career and Hiring Report 2025 | Unavailable |
| \[\\\[SRC-064\\\]\](https://cb.apps.fao.org/country.jsp?code=PAK) | Country Brief: Pakistan | Returned |
| \[\\\[SRC-065\\\]\](https://cedelft.eu/publications/tea-of-cultivated-meat/) | CE Delft techno-economic analysis | Returned |
| \[\\\[SRC-066\\\]\](https://coefficientgiving.org/funds/farm-animal-welfare/alternatives-to-animal-products/) | Coefficient Giving alternatives-to-animal-products programme | Returned |
| \[\\\[SRC-067\\\]\](https://coefficientgiving.org/funds/farm-animal-welfare/request-for-proposals-alternative-protein-rd/) | Coefficient Giving alternative-protein R\\\&D RFP | Returned |
| \[\\\[SRC-068\\\]\](https://data.fao.org/catalog/iso/2f264bb6-1238-459a-bf8b-0e2d0a16804a) | Food balances (Global, National - 2010-2023 - Annual) - FAOSTAT | Returned |
| \[\\\[SRC-069\\\]\](https://dhsprogram.com/pubs/pdf/FR375/FR375.pdf) | National Family Health Survey (NFHS-5), 2019-21: India: Volume I | Unavailable |
| \[\\\[SRC-070\\\]\](https://en.fvm.dk/news-and-contact/focus-on/action-plan-on-plant-based-foods) | Action Plan on Plant-Based Foods | Returned |
| \[\\\[SRC-071\\\]\](https://engrxiv.org/preprint/download/1438/2973/2173) | Humbird techno-economic analysis | Unavailable |
| \[\\\[SRC-072\\\]\](https://eprints.lse.ac.uk/125626/1/sciadv.adp1528.pdf) | Published full text | Unavailable |
| \[\\\[SRC-073\\\]\](https://faunalytics.org/animal-product-impact-scales-2026-updated-u-s-estimates-and-the-u-k-s-first-animal-product-impact-data/) | Animal Product Impact Scales 2026 Updated U.S. Estimates And The U.K.’s First Animal Product Impact Data | Returned |
| \[\\\[SRC-074\\\]\](https://food.ec.europa.eu/food-safety/novel-food/legislation\_en) | Novel Food legislation: Regulation (EU) 2015/2283 and implementing acts | Returned |
| \[\\\[SRC-075\\\]\](https://foresight4food.net/) | Foresight4Food | Unavailable |
| \[\\\[SRC-076\\\]\](https://foresight4food.net/wp-content/uploads/2026/03/FS4F\_Criteria-for-High-Quality-Guide-Feb-2026.pdf) | Criteria for High-Quality Food Systems Foresight | Returned |
| \[\\\[SRC-077\\\]\](https://gfi-india.org/resource/smart-protein-skills-mapping/) | Smart Protein Skills Mapping | Returned |
| \[\\\[SRC-078\\\]\](https://gfi.org/blog/alternative-protein-startups-underscore-the-need-for-scientific-and-engineering-talent/) | Alternative-protein startups’ talent needs | Returned |
| \[\\\[SRC-079\\\]\](https://gfi.org/resource/investment-methodology/) | GFI investment methodology | Returned |
| \[\\\[SRC-080\\\]\](https://gfi.org/wp-content/uploads/2026/04/2026-State-of-the-Industry-report-Fermentation-for-meat-seafood-eggs-dairy-and-ingredients.pdf) | GFI 2026 Fermentation State of the Industry | Returned |
| \[\\\[SRC-081\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI\_State-of-the-Industry-report-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf) | GFI 2026 Plant-Based State of the Industry | Unavailable |
| \[\\\[SRC-082\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI-2026-State-of-Global-Policy-Public-investment-in-protein-diversification-to-feed-a-growing-world.pdf) | GFI 2026 State of Global Policy | Returned |
| \[\\\[SRC-083\\\]\](https://gfi.org/wp-content/uploads/2026/04/GFI-2026-State-of-the-Industry-report-Cultivated-meat-seafood-and-ingredients.pdf) | GFI 2026 Cultivated Meat State of the Industry | Unavailable |
| \[\\\[SRC-084\\\]\](https://gfieurope.org/de/blog/private-investitionen-alternative-proteine/) | GFI Europe H1 2026 private investment update | Returned |
| \[\\\[SRC-085\\\]\](https://gfieurope.org/resource/state-of-the-european-alternative-protein-research-ecosystem-funding-and-publications/) | GFI Europe public R\\\&I funding tracker | Returned |
| \[\\\[SRC-086\\\]\](https://github.com/magpiemodel/magpie) | MAgPIE model repository and documentation | Returned |
| \[\\\[SRC-087\\\]\](https://globiom.org/documentation.html) | GLOBIOM documentation | Returned |
| \[\\\[SRC-088\\\]\](https://hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=animalcellculturefoods) | FDA inventory of completed premarket consultations | Returned |
| \[\\\[SRC-089\\\]\](https://innovationisrael.org.il/winner/cultivate-meat/) | בשר מתורבת \\\[Cultivated meat consortium\\\] | Unavailable |
| \[\\\[SRC-090\\\]\](https://ised-isde.canada.ca/site/global-innovation-clusters/en/node/83) | Ecosystem insight to build effective and relevant workforce solutions | Returned |
| \[\\\[SRC-091\\\]\](https://law.justia.com/cases/federal/appellate-courts/ca11/24-13640/24-13640-2026-03-23.html) | Eleventh Circuit opinion in UPSIDE Foods v | Returned |
| \[\\\[SRC-092\\\]\](https://mospi.gov.in/sites/default/files/press\_release/press\_note\_Nutritional%20Intake%20in%20India\_02072025.pdf) | Household Consumption Expenditure Survey: 2022-23 & 2023-24: Nutritional Intake in India | Returned |
| \[\\\[SRC-093\\\]\](https://pakistanhalalauthority.gov.pk/intro.aspx) | Pakistan Halal Authority official pages | Unavailable |
| \[\\\[SRC-094\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC12026562/) | Plant-based meat analogues review | Limited |
| \[\\\[SRC-095\\\]\](https://pmc.ncbi.nlm.nih.gov/articles/PMC3790135/) | Morphological analysis of food-system futures | Returned |
| \[\\\[SRC-096\\\]\](https://resources.sentientfutures.ai/fellowships/aianimals) | AI x Animals curriculum | Returned |
| \[\\\[SRC-097\\\]\](https://rethinkpriorities.org/research-area/ai-and-cultivated-meat/) | AI and Cultivated Meat. Near-Term Impacts of AI on the Commercial Viability of Cultivated Meat | Returned |
| \[\\\[SRC-098\\\]\](https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-map/) | Blue Marble: Next Generation — Base Map | Returned |
| \[\\\[SRC-099\\\]\](https://training-portal.nifa.usda.gov/web/crisprojectpages/1027058-cultured-10-leading-higher-education-initiatives-in-emerging-innovations-for-sustainable-food-production.html) | CULTURED 1.0: Leading Higher Education Initiatives in Emerging Innovations for Sustainable Food Production | Returned |
| \[\\\[SRC-100\\\]\](https://training-portal.nifa.usda.gov/web/crisprojectpages/1027620-integrated-approaches-to-enhance-sustainability-resiliency-and-robustness-in-us-agri-food-systems.html) | Integrated Approaches to Enhance Sustainability, Resiliency and Robustness in US Agri-Food Systems | Returned |
| \[\\\[SRC-101\\\]\](https://wfpc.sanford.duke.edu/reports/exploring-the-u-s-regulatory-and-legislative-landscapes-for-cell-cultivated-meat-and-seafood/) | Duke review of US cultivated-meat law | Returned |
| \[\\\[SRC-102\\\]\](https://www-pub.iaea.org/mtcd/publications/pdf/nvs-3-cd/pdf/nvs3\_scr.pdf) | IAEA acquisition-path and indicator guidance | Returned |
| \[\\\[SRC-103\\\]\](https://www.apac-sca.org/post/apac-sca-welcomes-singapore-s-approval-of-aleph-farms-cultivated-beef-marking-another-major-milest) | Aleph Farms Singapore approval announcement | Returned |
| \[\\\[SRC-104\\\]\](https://www.ars.usda.gov/oc/images/copyright/) | image-use policy | Returned |
| \[\\\[SRC-105\\\]\](https://www.ars.usda.gov/oc/images/photos/featuredphoto/aug19/beans/) | D502-1: Dry beans | Returned |
| \[\\\[SRC-106\\\]\](https://www.ars.usda.gov/oc/images/photos/nov21/d4744-1/) | D4744-1: A bioreactor conducting fermentation processes to produce ethanol | Returned |
| \[\\\[SRC-107\\\]\](https://www.bezosearthfund.org/news-and-insights/lauren-sanchez-announces-60-million-establish-bezos-centers-for-sustainable-protein) | Bezos Earth Fund sustainable-protein initiative | Returned |
| \[\\\[SRC-108\\\]\](https://www.birac.nic.in/cfp\_view.php?id=98\&scheme\_type=46) | DBT-BIRAC Joint Call for Proposals on 'Smart Proteins' for Fostering High Performance Biomanufacturing… | Returned |
| \[\\\[SRC-109\\\]\](https://www.cell-ag.de/) | CellAg Deutschland project overview | Returned |
| \[\\\[SRC-110\\\]\](https://www.cell-ag.de/\_files/ugd/cd7689\_34c289309fbd4cdbae0a16acbbb40967.pdf) | National Action Plan Germany | Unavailable |
| \[\\\[SRC-111\\\]\](https://www.cgiar.org/news-events/news/augmented-foresight-how-ai-can-make-food-systems-analysis-smarter-faster-and-more) | Augmented Foresight | Returned |
| \[\\\[SRC-112\\\]\](https://www.eda.gov/archives/2022/arpa/build-back-better/finalists/North-Carolina-Biotechnology-Center.htm) | Accelerate NC - Life Sciences Manufacturing | Unavailable |
| \[\\\[SRC-113\\\]\](https://www.efsa.europa.eu/en/applications/novel-food) | EFSA novel-food application guidance | Returned |
| \[\\\[SRC-114\\\]\](https://www.europarl.europa.eu/pdfs/news/expert/2026/6/press\_release/20260611IPR45209/20260611IPR45209\_en.pdf) | European Parliament meat-designation vote | Limited |
| \[\\\[SRC-115\\\]\](https://www.fao.org/4/i2744e/i2744e00.htm) | Livestock sector development for poverty reduction: an economic and policy perspective - Livestock's many… | Returned |
| \[\\\[SRC-116\\\]\](https://www.fao.org/4/X9892E/X9892e00.htm) | Food Balance Sheets: A Handbook | Unavailable |
| \[\\\[SRC-117\\\]\](https://www.fao.org/4/X9892E/X9892e01.htm) | Food Balance Sheets: A Handbook | Returned |
| \[\\\[SRC-118\\\]\](https://www.fao.org/4/x9892e/x9892e02.htm) | Food Balance Sheets: A Handbook, II. Concepts and definitions used in food balance sheets | Returned |
| \[\\\[SRC-119\\\]\](https://www.fao.org/agrifood-economics/news/detail-events/en/c/1757552/) | FAO analysis highlights strategic policy reform to narrow Pakistan's healthy diet gap | Returned |
| \[\\\[SRC-120\\\]\](https://www.fao.org/fao-who-codexalimentarius/sh-proxy/en/?lnk=1\&url=https%253A%252F%252Fworkspace.fao.org%252Fsites%252Fcodex%252FMeetings%252FCX-701-47%252FCRDs%252Fcac47\_crd04x.pdf) | Food Safety Aspects of Cell-Based Food and Precision Fermentation Derived Food Products | Returned |
| \[\\\[SRC-121\\\]\](https://www.fao.org/media/docs/unfoodsystemslibraries/foresight-for-food-systems/foresight-guide.pdf) | Using Foresight for Food Systems Transformation A guide for policy makers practitioners and researchers | Returned |
| \[\\\[SRC-122\\\]\](https://www.fao.org/research-extension-systems/agricultural-innovation-systems/en) | Agricultural innovation systems | Returned |
| \[\\\[SRC-123\\\]\](https://www.fda.gov/food/hfp-constituent-updates/fda-completes-first-pre-market-consultation-human-food-made-using-animal-cell-culture-technology) | FDA Completes First Pre-Market Consultation for Human Food Made Using Animal Cell Culture Technology | Returned |
| \[\\\[SRC-124\\\]\](https://www.food.gov.uk/print/pdf/node/27246) | UK FSA sandbox progress report | Unavailable |
| \[\\\[SRC-125\\\]\](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1424012/full) | Artificial intelligence in cultivated meat | Returned |
| \[\\\[SRC-126\\\]\](https://www.frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1378883/full) | Backcasting for food-system transformation | Returned |
| \[\\\[SRC-127\\\]\](https://www.fsis.usda.gov/inspection/compliance-guidance/labeling/labeling-policies/human-food-made-cultured-animal-cells) | USDA-FSIS cultivated-cell labeling and inspection policy | Unavailable |
| \[\\\[SRC-128\\\]\](https://www.gov.uk/government/statistics/national-diet-and-nutrition-survey-2019-to-2023/national-diet-and-nutrition-survey-2019-to-2023-report) | National Diet and Nutrition Survey 2019 to 2023: report | Returned |
| \[\\\[SRC-129\\\]\](https://www.gov.za/news/media-statements/science-technology-and-innovation-partners-un-food-and-agriculture) | Science, Technology and Innovation partners with UN Food and Agriculture Organization on roadmap to… | Unavailable |
| \[\\\[SRC-130\\\]\](https://www.greenqueen.com.hk/swap-food-vegan-chicken-plant-based-meat-startup-liquidation-shuts/) | Green Queen consolidation tracker | Returned |
| \[\\\[SRC-131\\\]\](https://www.infoteca.cnptia.embrapa.br/handle/doc/1150307) | Guide for technological functional characterization of protein ingredients for the plant-based market | Returned |
| \[\\\[SRC-132\\\]\](https://www.ipcc.ch/report/ar6/wg2/chapter/annex-ii/) | Annex II: Glossary - scenario, climate prediction, and climate projection definitions | Unavailable |
| \[\\\[SRC-133\\\]\](https://www.mse.gov.sg/latest-news/newsletter-climate-action-in-sg-dec/) | Climate Action in SG (Dec 2020): Novel food as a sustainable food option | Returned |
| \[\\\[SRC-134\\\]\](https://www.mse.gov.sg/latest-news/written-reply-to-parliamentary-question-on-lab-grown-seafood-and-cultured-meat-sector/) | Written Reply to Parliamentary Question on Lab-Grown Seafood and Cultured Meat Sector | Returned |
| \[\\\[SRC-135\\\]\](https://www.mti.gov.sg/newsroom/speech-by-mos-alvin-tan-at-the-singapore-international-agri-food-week-welcome-reception/) | Speech by MOS Alvin Tan at the Singapore International Agri-Food Week Welcome Reception | Returned |
| \[\\\[SRC-136\\\]\](https://www.nationaalgroeifonds.nl/overzicht-lopende-projecten/thema-landbouw-voedsel-en-land-en-watergebruik/cellulaire-agricultuur) | Cellulaire Agricultuur | Returned |
| \[\\\[SRC-137\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report.html) | OECD-FAO Agricultural Outlook 2026-2035 | Returned |
| \[\\\[SRC-138\\\]\](https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035\_47874669-en/full-report/meat\_149b4ca3.html) | OECD–FAO Agricultural Outlook 2026–2035: Meat | Returned |
| \[\\\[SRC-139\\\]\](https://www.pbs.gov.pk/hies/) | Household Integrated Economic Survey (HIES) | Returned |
| \[\\\[SRC-140\\\]\](https://www.pbs.gov.pk/wp-content/uploads/2020/07/HIES-2024-25-Report-Final-2.pdf) | Household Integrated Economic Survey (HIES) 2024-25 | Returned |
| \[\\\[SRC-141\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2238344\&lang=1\&reg=3) | Parliament Question: BioE3 Policy | Returned |
| \[\\\[SRC-142\\\]\](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2288306\&lang=1\&reg=3) | PARLIAMENT QUESTION: IMPLEMENTATION OF BIOE3 POLICY | Returned |
| \[\\\[SRC-143\\\]\](https://www.psqca.com.pk/division-wise-standards/halaal/) | Halaal standards and Halal Certification Bodies (PS 4992-OIC/SMIIC 2) | Returned |
| \[\\\[SRC-144\\\]\](https://www.sciencedirect.com/science/article/pii/S0308521X25000101) | Quantitative scenarios for food-system futures | Unavailable |
| \[\\\[SRC-145\\\]\](https://www.sciencedirect.com/science/article/pii/S0924224417303400) | Bringing cultured meat to market: Technical, socio-political, and regulatory challenges in cellular agriculture | Unavailable |
| \[\\\[SRC-146\\\]\](https://www.sciencedirect.com/science/article/pii/S0924224426004413) | AI in alternative-protein development review | Unavailable |
| \[\\\[SRC-147\\\]\](https://www.sentientfutures.ai/incubator/gallery/) | Sentient Futures Incubator gallery | Returned |
| \[\\\[SRC-148\\\]\](https://www.sentientfutures.ai/incubator/gallery/advocacy-intel-map/) | Effective Advocacy Project | Returned |
| \[\\\[SRC-149\\\]\](https://www.sentientfutures.ai/incubator/gallery/cheese-analogue-ai/) | Optimising Cheese Analogues Formulation using AI Applications | Returned |
| \[\\\[SRC-150\\\]\](https://www.sentientfutures.ai/incubator/gallery/ideosphere-forecasting/) | Ideosphere | Returned |
| \[\\\[SRC-151\\\]\](https://www.sfa.gov.sg/regulatory-standards-frameworks-guidelines/novel-food-framework/overview-of-pre-market-approval-framework-for-novel-food) | Singapore SFA novel-food framework | Unavailable |
| \[\\\[SRC-152\\\]\](https://www.ukri.org/news/national-alternative-protein-innovation-centre-launches/) | National alternative protein innovation centre launches | Returned |
| \[\\\[SRC-153\\\]\](https://www.ukri.org/opportunity/alternative-proteins-innovation-and-knowledge-centre/) | Alternative Proteins Innovation and Knowledge Centre | Returned |
| \[\\\[SRC-154\\\]\](https://www.ukri.org/publications/alternative-proteins-roadmap-identifying-uk-priorities/) | Alternative Proteins Roadmap: identifying UK priorities | Returned |
| \[\\\[SRC-155\\\]\](https://www.un.org/scientific-advisory-board/sites/default/files/2025-06/verification\_of\_frontier\_ai.pdf) | Verification of frontier AI | Unavailable |
| \[\\\[SRC-156\\\]\](https://www.unep.org/resources/whats-cooking-assessment-potential-impacts-selected-novel-alternatives-conventional) | What’s Cooking? An assessment of potential impacts of selected novel alternatives to conventional animals… | Returned |
| \[\\\[SRC-157\\\]\](https://www.who.int/news-room/fact-sheets/detail/healthy-diet) | Healthy diet | Returned |
| \[\\\[SRC-158\\\]\](https://www.who.int/publications/i/item/9789240070943) | Food safety aspects of cell-based food | Returned |
| \[\\\[SRC-159\\\]\](https://www.who.int/publications/i/item/B09677) | WHO-PREZODE zoonotic-risk indicators | Returned |

  

**Appendix D Records required for the next release**

The following record types make the report’s next update reviewable without implying that the missing evidence already exists. They are proposed specifications, not reconstructed outputs of the absent PDF model.

|  |  |
| :-: | :-: |
| \*\*Record\*\* | \*\*Minimum fields\*\* |
| Source and evidence family | Stable source ID; full citation; DOI or URL; publication and access dates; version; family ID; exact page or clause; evidence type; funding; access level; human review status. |
| Claim | Claim ID; exact assertion; product and jurisdiction; source IDs; supporting locator; interpretation; uncertainty; checked by and date; superseded or conflicting evidence. |
| Institutional decision | Issuer; legal or religious function; scope; process and formulation; site; territory; effective and expiry dates; certificate or decision identifier; conditions; recognition and registration dependencies. |
| Production observation | Facility and batch; product; inputs and provenance; scale; run date; yields; losses; downtime; utilization; energy; costs; independent validation; confidentiality limits. |
| Consumer observation | Sampling frame; recruitment; weights; language; exact stimulus; price; meal; choice set; stated or observed outcome; follow-up; attrition; substitution; preregistration and consent. |
| Scenario baseline | Dataset and revision; full-access contract; price and year; units; segment and channel partitions; supply-pool ID; access and acceptance assumptions; uncertainty and missingness rules. |
| Animal impact | Species and product displaced; counterfactual; demand effect; supply and trade response; yield; number affected; welfare assumptions; donor and input animals; uncertainty; double-counting checks. |

 

Release condition: each headline claim can be traced to a scoped record, each numerical output to a compatible input and transformation, and each unresolved item remains visibly unresolved. The present evidence justifies focused research and institutional clarification. It does not yet justify a commercial forecast or a quantified claim of animals spared.

  
  
