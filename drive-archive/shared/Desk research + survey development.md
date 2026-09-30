# Tab 1  

# Desk Research doc

### **Part of the wider project: "How could AI reshape the food system transition over the next 10-20 years?"**

## **Sub-Question** **Current (updated):** What will future demand for alternative proteins look like, and what are the key limiting or accelerating factors — including the role of AI — in that trajectory?

Goals:

  - Define what we’re considering alt proteins - insects? Cultured meat?
  - How to measure demand - money or units? Do we mean demand or consumption?

  

  - locate existing conventional protein market projections and alt-protein demand projections; note whether alt-protein competition is factored into conventional meat projections. - ONGOING - repository
  - A synthesis of existing projections of both conventional meat market growth and alt-protein consumer demand, noting where and how alt-protein competition is (or isn't) already accounted for in each. - NOT DONE - need to do synthesis
  - A literature-based driver map covering the key factors — including AI-driven ones — likely to accelerate or limit alt-protein adoption. - NOT DONE
      
      - And the data of each
      -  proxy measures eg google searches for pea protein
  - build driver map (price parity, taste/texture, culture, regulation, distribution, AI-related factors). - ONGOING
  -  Identify 2-3 historical substitution analogues (e.g. margarine/butter, plant milk/dairy) and any literature-stated elasticity figures. - ONGOING

  

Umar help with: LLM tools, making questionnaires  

# Driver map  

Driver map

  

List:

  - Price
  -  taste, texture, 
  - Convenience (cooking, RTE) 
  - marketing, 
  - Demographics
  - Economic development
  - Education levels
  - Political trends/climate
  - Quality of life trends
  - celebrity endorsement,
  -  regulation, subsidies,
  -  retail shelf space,
  -  restaurant menu adoption, 
  - cultural/religious factors, 
  - environmental awareness,Awareness of animal welfare, (UBI/working hours)
  -  health perceptions, 
  - AI-driven R\&D speed,
  -  AI-personalized marketing, 
  - supply chain costs

  

Categories

  - Price
  - Public perception
  - Regulation
  - Exogenous: economics demographics, conflict etc

  
  

# rethinkX  

**RethinkX — "Rethinking Food and Agriculture 2020-2030" (Tubb & Seba, 2019)**

**Core claim:** The US cattle/dairy industry will collapse by 2030 (cow numbers down \~50%, dairy/cow-product demand down \~70%), driven by precision fermentation and cellular agriculture out-competing animal protein on cost.

**Methodology — how they got there:**

1.  **The Seba Technology Disruption Framework (STDF)** — their overarching lens, originally developed for and validated against historical technology disruptions (they cite examples like digital photography, solar PV, and EVs). The core thesis: technology disruptions are non-linear (S-curve) rather than gradual/linear, and mainstream analysts systematically underestimate speed and scale because they extrapolate the present forward in a straight line instead of modeling exponential adoption curves.
2.  **Cost-curve modeling as the engine of disruption** — their central mechanism is economic, not behavioral: they model the falling cost trajectory of precision fermentation (their published trajectory: below $10/kg by 2025, 5x cheaper than animal protein by 2030, 10x cheaper by 2035) and argue that once a technology substantially undercuts incumbents on cost *and* matches or exceeds them on quality, adoption becomes inevitable and rapid — consumers and businesses will switch simply because it's the rational economic choice, not because of a shift in preferences or culture.
3.  **A "weakest link" argument** — they argue disruption doesn't require full product substitution: since only \~3.3% of milk (its protein content) needs replacing to undermine the economics of the whole dairy supply chain, they treat the disruption threshold as much lower than "alt-protein has to functionally replace the whole product."
4.  **Explicitly labeled as an early-stage, low-data model.** Notably, RethinkX's own report says its cost curves are "based on limited data given the early stage of the application of these technologies" and should be seen as a "beta" analysis — this is a significant caveat that's often dropped when the report is cited elsewhere.

**How it's viewed by other experts:**

  - **Even sympathetic organizations are skeptical.** GFI's own science leadership publicly called the RethinkX transition "far from inevitable" while still saying the report was worth paying attention to — a fairly telling response from a group that otherwise wants alt-protein adoption to succeed.
  - **Agricultural/dairy-sector commentators have been more directly critical**, arguing the report reads as "science fiction" rather than rigorous science, questioning the credibility and independence of RethinkX as an organization, and noting that the analysis doesn't adequately account for second-order responses — e.g. critics point out the model doesn't account for meat/dairy producers potentially absorbing novel proteins into their own supply chains (as feed or ingredients) rather than simply being replaced by them.
  - **Industry analysts (e.g. Synthesis Capital) treat it as an outlier, not a norm** — they note RethinkX is essentially the *only* major forecaster using S-curve adoption modeling, with virtually everyone else in the market-research space defaulting to linear extrapolation. This cuts both ways: it makes RethinkX methodologically distinctive and interesting, but also means it hasn't been cross-validated by independent replication.
  - **A useful empirical check for you:** RethinkX's own published trajectory said precision fermentation protein costs would fall below $10/kg by 2025. As of today, cost parity is still widely discussed in 2026 industry reports as an ongoing challenge rather than an achieved milestone — which suggests this specific early milestone in their forecast did not play out on schedule, a genuinely useful, low-effort track-record data point for your limitations/comparison section.

**Why this matters for your project specifically:** RethinkX is the sharpest existing example of exactly the methodological question your report should engage with — S-curve vs. linear adoption modeling — but it's a single, contested, non-independently-replicated forecast built on admittedly thin cost data, from an organization with a track record of dramatic disruption predictions across multiple sectors. That's a good foil for your LLM panel: you could explicitly ask your models to weigh in on whether S-curve or linear adoption is more appropriate here, and why, using RethinkX vs. the mainstream market-research reports as the two poles of existing opinion.

  
  

# Historical substitution analogues  

[Science direct](https://www.sciencedirect.com/science/article/pii/S0306919226000862) - each gallon of plant-based milk displaced 0.68 gallons of cow’s milk. While plant-based milk continues to affect the demand for fluid cow’s milk products, especially the higher-priced organic and lactose-free products, evidence shows that it has not been the primary driver in the recent accelerated decline in the consumption of fluid cow’s milk.

  

The availability of non-dairy alternatives accounted for about one-third of the decline in U.S. fluid cow's milk consumption between 2006 and 2020 (reducing consumption by roughly 1.6 gallons per capita)  

# scratch survey development notes  

## Survey structure

  - Instructions (inc definitions and details like whether we are including insects), quantiles explainer, and purpose: accuracy goal framing
  - 4 questions, each to be asked with 10th, 50th and 90th quantiles and rationales
  - Each question should have its own info pack 
  - Question at the end asking for anything we’ve missed from this survey wording

  

## Info packs per question

Info pack to include

  - 1\. definitions 
  - ~~\~\~2. Historical data relevant to the question\~\~~~
  - 3\. Resolution criteria

Info pack to exclude

  - Rethinkx or other ‘predictions’
  - Leading wording or language
  - *\*Historial data\**

  

## Questions

  - 2026 market share of alt proteins - [newmarketpitch ](https://newmarketpitch.com/blogs/news/alternative-protein-market-size)article shows the possible range from other business research and the range of data that goes into it 2024
      
      - But beware of different definitions causing the different predictions: New Market Pitch table shows across real research firms: GFI's US-retail-only $8.1B vs. Grand View's broader feed-inclusive $22.95B are describing different things, not disagreeing about the same thing
      - So info pack needs to contain a specific definition
  - Growth rate (can be negative or 0) of market share to:
      
      - 20262028
      - 2030
      - 2035
  - (ALL: ask for quantiles - 10th,50th, 90th, and rationales)

  
  

  -   
      

# LLM selection  

## LLM selection

Final methodology: Maximising diversity with geographical choices, and then from these categories selecting those ranked highest on forecasting via ForecastBench Baseline Leaderboard.

  

**Final choices:** ***category: name of model, FB score, pric*****e**

  - 1 US closed: claude-sonnet-4-6-adaptive-thinking-16000, 62.0, free
  - 1 US open: meta-llama-3.1-405b-instruct-turbo, 58.9, free
  - 1 china closed: minimax-m3-adaptive-thinking-12000, 61.5, free(?)\*
  - 1 china open: deepseek-r1-scratchpad, 59.0, free
  - 1 european open weights:  mistral-large-2411, 56.3, free(?)
  - 1 european closed weights: [Cassi.ai](http://cassi.ai), contact: Matthew Cox, free (in return for their use-case)
  - JGev - is practically free  

*Selection is based on leaderboard updated on: 29-09-2026*

  
  

**Note on forecastbench baseline leaderboard:**

To ensure leaderboard stability, models are included on the leaderboard 50 days after forecast submission.

  

*We should also put a note in the report that these are ranked as out of the box models, not with searching / tools enabled, which differs to how we’re using them. It also has a bias toward older models (but they try to counteract this with some weighting/equation?).*

  

\*MiniMax runs its global consumer-facing chatbot and creation engine through **Hailuo AI**. Navigate to[ hailuoai.com](https://www.hailuoai.com/) 

  

Jev  

# Survey instructions  

## Notes on instructions for LLMS

Avoiding bias from previous work eg rethinkX

  - Base your estimate on first-principles reasoning from the information provided, rather than deferring to or citing any specific existing named forecast or report you may be aware of.
  - Are you aware of any specific existing reports or predictions about this topic, and if so,name and link them specifically and how they influenced your estimate
  - Question at the end asking for questions for future rounds - to pick up anything we’ve missed from this survey wording

  

Ensuring every claim is backed up

  - Ensure every claim you make is evidenced, and link the evidence ideally with the exact page number or section you are referencing
  - State any assumptions you are making

  

Give it an incentive

  - I’ll be assessing you on your accuracy, the aim is to be as accurate as possible when the date of resolution comes
  - You are allowed to disagree or agree with any of the material ive given you
  - You can draw on any other available data

  

Accuracy

  - Framing the goal as accuracy, if we check at the resolution date, the winner will be the closest one to the real
  - Ask for a specific value for each quantile, not a range

  

**Content-focussed instructions:**

AI focus

  - Development of AI seems likely to change the landscape of alternative proteins and plant based foods, including fermented and cultivated categories. LLMs should give adequate attention to this when considering the drivers and obstacles of demand. 

Drivers and obstacles

  - In your rationale, you should consider the main factors (drivers and/or obstacles) you believe will affect the trajectory of demand over the given timescales, and you should explain how much of the change in trajectory you assign to each factor.
  - Drivers = any factors that could be considered catalysts, enablers, or accelerators.
  - Obstacles = any factors that could be considered headwinds, constraints, bottlenecks or impediments.

Demand

  - We are looking at demand in terms of US sales, but you should also consider supply side effects that could be captured in these figures.

  
  

# Claude’s attempt at drafting instructions \[edited\]:

## **Part A: General Instructions**

*Method: (given to every model as a background doc)*

You are participating in a structured forecasting exercise. You will be asked several questions about the future of alternative protein consumption. For each question, you will be given background information and asked to provide a probabilistic forecast.

**Definitions:**

  - "Alternative proteins" in this exercise means: plant-based meat/dairy/egg analogues, fermentation-derived proteins (biomass and precision fermentation), and cultivated/cultured meat, seafood, dairy, and egg products.
  - **Insects are explicitly excluded** from this definition, as they represent a distinct product category with different regulatory, cultural, and use-case (food vs. feed) dynamics.
  - **Animal feed applications are excluded.** This exercise concerns human food consumption only.
  - All figures and forecasts should refer to **US** consumption.

**Quantile format:** For each numerical question, provide your 10th percentile, 50th percentile (median), and 90th percentile estimates. This means: you believe there is a 10% chance the true value will be below your 10th percentile estimate, a 50% chance it will be below your median estimate, and a 90% chance it will be below your 90th percentile estimate. Your 10th-to-90th percentile range should reflect an interval you are 80% confident contains the true value. For each quantile forecast, provide a specific value in the metric stated in the question rather than a range.

Rationale instructions:

  - Your rationale should explain why you chose the specific value you gave for your forecasts. It should include and drivers/ obstacles you thought were important and how much of the forecaste(d) values each factor accounted for.
  - State any assumptions you are making explicitly
  - **Evidence standard:** Ensure every substantive claim you make is evidenced. Where possible, cite the specific source and section from the information provided, or name your source clearly if drawing on outside knowledge.
  - **Awareness check:** In your rationale, state whether you are aware of any specific existing named reports, forecasts, or predictions on this topic and, if so, name them and explain whether and if/how they influenced your estimate.

**Purpose and accuracy framing:** This exercise is designed to produce the most accurate possible forecasts. At the resolution date, your estimates will be compared against the actual outcome. Reason as carefully and rigorously as you can, as if your accuracy will be evaluated.

**Reasoning approach:** Base your estimate on first-principles reasoning from the information provided, rather than deferring to or citing any specific existing named forecast or report you may be aware of. You are encouraged to disagree or agree with any of the material provided to you, and you may draw on any other relevant information you are aware of, provided you state this explicitly.

  
  

# resolution criteria and metrics - main question  

### **Definition of alt-protein**

  - Which term: are we using alt-protein or plant based protein?

**Claude’s definition, taken from GFI’s 2026 report how they define specifically plant based protein:**

  - **Plant-based protein products** are food products made from plant- or fungus-derived ingredients that are designed and marketed to directly replace conventional animal products, either as stand-alone products or within recipes. The category includes plant-based alternatives to meat and seafood (including burgers, sausages, nuggets, mince, and shreds, chunks, and strips); eggs; and dairy, including milk, creamer, yogurt, cheese, and ice cream and other frozen desserts. It also includes traditional plant-protein foods such as tofu, tempeh, and seitan, as well as other plant-based products positioned as protein sources or animal-product replacements, such as protein powders and liquids, ready-to-drink beverages, bars, prepared meals, and baked goods and desserts. Products such as black bean or veggie burgers are included even when they don't simulate meat, because they serve as a direct replacement for an animal-based product. Upstream plant protein ingredients, such as protein isolates, concentrates, and textured vegetable protein, form part of the plant-based supply chain but are distinct from the final consumer products they are used to make. The category excludes inherently plant-based whole foods, such as chickpeas and kale, that are not positioned as alternatives to animal products. It also excludes cultivated (cell-based) products, fermentation-derived proteins, and blended products that combine plant-based and conventional animal ingredients.

Claudes definition, inspired by GFI of cultivated and fermented:

  - **Cultivated meat** is genuine animal meat, including poultry, seafood, and organ meats, produced by growing animal cells directly in a controlled environment rather than by raising and slaughtering animals. The resulting meat is composed of the same cell types as conventional meat and is designed to replicate its taste, texture, and nutritional profile. Final products may consist entirely of cultivated cells or combine cultivated cells with plant-based ingredients. The category is also referred to as cultured or cell-based meat.
  - **Fermentation-derived proteins** are alternative proteins produced by cultivating microorganisms, such as fungi, yeast, bacteria, and microalgae, to make food or food ingredients that replace or improve on animal products. GFI identifies three approaches: traditional fermentation, biomass fermentation and precision fermentation. Fermentation-derived ingredients may be sold as stand-alone products or incorporated into plant-based and cultivated products to improve their taste, texture, and nutrition.
  -   

<!-- end list -->

  - Definition: a product that replaces an animal product (sector convention). This includes butter, ice cream, creamer and other dairy analogues. It matches GFI and most published forecasts, so comparisons are easier. It also fits your displacement question, since plant-based butter displaces dairy butter just as oat milk displaces cow's milk.
  - Source:
      
      -  **GFI, "Introduction to alternative proteins" (Nov 2023, PDF).** This is the most useful single source. It defines alternative proteins as foods produced to provide the sensory experience of animal meat, dairy, and eggs using plants, fermentation, or cellular agriculture, citing the Center for Strategic & International Studies (2023). It also ***excludes animal feed and insect-based proteins, and says this usage is shared by CSIS, Climate Advisers and GFI.*** That matches your project's scope exactly, including the exclusions, and gives you a non-GFI source (CSIS) to cite as well.[ GFIGFI](https://gfi.org/wp-content/uploads/2023/11/COM23042_Intro-to-APs.pdf)
      - **NC State Extension, "An extension guide to alternative proteins."** An independent academic source: it describes alternative proteins as products made to look and taste like conventional animal protein products, including burgers, nuggets, dairy products, fish and eggs, whether used as main-course foods or consumed like dairy.[ ncsu](https://content.ces.ncsu.edu/an-extension-guide-to-alternative-proteins)
  - The idea that plant-based butter displaces dairy butter, just as oat milk displaces cow's milk, is my own reasoning, not something from these sources. In the report, present it as your justification for following the convention rather than as a cited claim. 

## Resolution criteria

  -  the figure reported in GFI’s annual report for US dollar sales for plant-based food
  - The report is published in April/May the year after, so the 2026 question will resolve in roughly April–May 2027, and 2030 and 2035 will resolve against the same series.
  - US only: [“Plant-based meat and seafood sales were $1 billion in 2025. “ p19](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

## Caveats to handle in the definition

### Drawbacks of GFI data:

  - \[not acting on, acknowledge in final report\] Retail only. SPINS doesn't cover foodservice. Many market reports include it, so their totals will run higher. Comparisons with those reports will be approximate. Comparisons with GFI's own data will be exact.
  - GFI's categories are broader than just alt protein - they look at all plant based food. They include tofu, ready meals, protein powders and baked goods. For the questions to resolve cleanly, **adopt GFI's category set as your definition of plant based food, rather than your own definition.**
  - **\*\*Fermentation-derived and cultivated products are almost absent from SPINS retail data.GFI also does not directly report their sales figues\*\***
  - \[not acting on, acknowledge in final report\] 2026 report notes this: Please note that this study’s methodology has changed compared to that used in previous reporting by GFI. We do not recommend comparing data released in prior years to the data included here.

  

## METRICS

###   
Dollar sales v unit sales

  

### Dollars vs mass

  

### 2026 dollars:

  - Why 2025 rather than 2026 dollars: 2025 is the latest full year of GFI data, so it's the year your info pack describes. Forecasts in 2025 dollars can be compared directly with the baseline the models were given. 2026 isn't over yet, and GFI's data year ends on November 30, so "2026 dollars" would be ambiguous.

Use the **CPI-U, food at home, U.S. city average, not seasonally adjusted**. Its BLS series ID is **CUUR0000SAF11**, and you'd use the annual average.

**Why this version of the index**

  - **CPI-U** covers all urban consumers, about 90% of the population. It's the standard default and the one most people will recognise.
  - **Food at home** measures grocery prices, which matches retail sales data. Headline CPI includes housing and energy, which have little to do with grocery prices. The all-food index includes restaurants, which your retail metric excludes.
  - **Not seasonally adjusted** matters because BLS publishes annual averages for the unadjusted series, and an annual average is what you need for annual sales.
  - **Not a narrower index.** The meat, poultry, fish and eggs index tracks animal-product prices, not plant-based ones, so it would build beef price swings into your deflator. You want a general grocery deflator; relative price effects belong in the forecast itself.

**How to convert**

For any year Y, divide the reported nominal figure by that year's index and multiply by the 2025 index:

real 2025 $ = nominal $ × (CPI 2025 ÷ CPI Y)

**One detail to state**

GFI's data year runs December to November, while the BLS annual average runs January to December. Over a ten-year horizon the difference is negligible, so I'd just use the calendar-year average and say so.

Suggested wording for the resolution criteria:

Dollar figures are in constant 2025 US dollars. Reported nominal values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.

  

## If data source no longer exists caveat

  - If the GFI data source is no longer reported at the resolution dates, a close analogue will be calculated using the SPINS data directly, or with a panel of industry experts if no alternative is available. 

## Question format

Why this approach and not “in what year will plant based US sales reach $Xbil”?

  
  
  

## Working question Wording

What will total US retail dollar sales of all plant-based categories be in the following years? Give 10th/50th/90th percentile estimates in nominal billions of 2025 USD. 

2026

2030

2035

  
  

# \[clean\] resolution criteria  

  

## Main question Resolution criteria

  -  the figure reported in GFI’s annual report for US dollar sales for plant-based food.
  - GFI defines plant based food as: 
      
      - **Plant-based protein products** are food products made from plant- or fungus-derived ingredients that are designed and marketed to directly replace conventional animal products, either as stand-alone products or within recipes. The category includes plant-based alternatives to meat and seafood (including burgers, sausages, nuggets, mince, and shreds, chunks, and strips); eggs; and dairy, including milk, creamer, yogurt, cheese, and ice cream and other frozen desserts. It also includes traditional plant-protein foods such as tofu, tempeh, and seitan, as well as other plant-based products positioned as protein sources or animal-product replacements, such as protein powders and liquids, ready-to-drink beverages, bars, prepared meals, and baked goods and desserts. Products such as black bean or veggie burgers are included even when they don't simulate meat, because they serve as a direct replacement for an animal-based product. Upstream plant protein ingredients, such as protein isolates, concentrates, and textured vegetable protein, form part of the plant-based supply chain but are distinct from the final consumer products they are used to make. The category excludes inherently plant-based whole foods, such as chickpeas and kale, that are not positioned as alternatives to animal products. It also excludes cultivated (cell-based) products, fermentation-derived proteins, and blended products that combine plant-based and conventional animal ingredients.
  - The report is published in April/May the year after, so the 2026 question will resolve in roughly April–May 2027, and 2030 and 2035 will resolve against the same series.

### Drawbacks of GFI data:

  - \[not acting on, acknowledge in final report\] Retail only. SPINS doesn't cover foodservice. Many market reports include it, so their totals will run higher. Comparisons with those reports will be approximate. Comparisons with GFI's own data will be exact.
  - GFI's categories are broader than just alt protein - they look at all plant based food. They include tofu, ready meals, protein powders and baked goods. For the questions to resolve cleanly, **adopt GFI's category set as your definition of plant based food, rather than your own definition.**
  - **\*\*Fermentation-derived and cultivated products are almost absent from SPINS retail data.GFI also does not directly report their sales figues\*\***
  - \[not acting on, acknowledge in final report\] 2026 report notes this: Please note that this study’s methodology has changed compared to that used in previous reporting by GFI. We do not recommend comparing data released in prior years to the data included here.

  

## METRICS

###   
Dollar sales v unit sales

  

### Dollars vs mass

  

### 2026 dollars:

  - Why 2025 rather than 2026 dollars: 2025 is the latest full year of GFI data, so it's the year your info pack describes. Forecasts in 2025 dollars can be compared directly with the baseline the models were given. 2026 isn't over yet, and GFI's data year ends on November 30, so "2026 dollars" would be ambiguous.

Use the **CPI-U, food at home, U.S. city average, not seasonally adjusted**. Its BLS series ID is **CUUR0000SAF11**, and you'd use the annual average.

**Why this version of the index**

  - **CPI-U** covers all urban consumers, about 90% of the population. It's the standard default and the one most people will recognise.
  - **Food at home** measures grocery prices, which matches retail sales data. Headline CPI includes housing and energy, which have little to do with grocery prices. The all-food index includes restaurants, which your retail metric excludes.
  - **Not seasonally adjusted** matters because BLS publishes annual averages for the unadjusted series, and an annual average is what you need for annual sales.
  - **Not a narrower index.** The meat, poultry, fish and eggs index tracks animal-product prices, not plant-based ones, so it would build beef price swings into your deflator. You want a general grocery deflator; relative price effects belong in the forecast itself.

**How to convert**

For any year Y, divide the reported nominal figure by that year's index and multiply by the 2025 index:

real 2025 $ = nominal $ × (CPI 2025 ÷ CPI Y)

**One detail to state**

GFI's data year runs December to November, while the BLS annual average runs January to December. Over a ten-year horizon the difference is negligible, so I'd just use the calendar-year average and say so.

Suggested wording for the resolution criteria:

Dollar figures are in constant 2025 US dollars. Reported nominal values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.

  

## If data source no longer exists caveat

  - If the GFI data source is no longer reported at the resolution dates, a close analogue will be calculated using the SPINS data directly, or with a panel of industry experts if no alternative is available. 

## Question format

Why this approach and not “in what year will plant based US sales reach $Xbil”?

  
  
  

# Resolution criteria for open ended questions:

Question 2:

  - There is currently no direct measure of sales for cultivated and fermented categories. Therefore, for this question we will resolve it with the closest possible available measure at the time if one exists, but we are more interested in your reasoning for your forecast than it’s accuracy, given we don’t currently have an accurate measure. 

**definitions:**

  - **Cultivated meat** is genuine animal meat, including poultry, seafood, and organ meats, produced by growing animal cells directly in a controlled environment rather than by raising and slaughtering animals. The resulting meat is composed of the same cell types as conventional meat and is designed to replicate its taste, texture, and nutritional profile. Final products may consist entirely of cultivated cells or combine cultivated cells with plant-based ingredients. The category is also referred to as cultured or cell-based meat.
  - **Fermentation-derived proteins** are alternative proteins produced by cultivating microorganisms, such as fungi, yeast, bacteria, and microalgae, to make food or food ingredients that replace or improve on animal products. GFI identifies three approaches: traditional fermentation, biomass fermentation and precision fermentation. Fermentation-derived ingredients may be sold as stand-alone products or incorporated into plant-based and cultivated products to improve their taste, texture, and nutrition.

  
  

# \[deprecated\] questions and Infopacks  

# **LLM Forecasting Elicitation: Alt-Protein Demand Survey**

  

## **Part A: General Instructions**

*Method: (given to every model as a background memory doc)*

You are participating in a structured forecasting exercise. You will be asked several questions about the future of alternative protein consumption. For each question, you will be given background information and asked to provide a probabilistic forecast.

**Definitions:**

  - "Alternative proteins" in this exercise means: plant-based meat/dairy/egg analogues, fermentation-derived proteins (biomass and precision fermentation), and cultivated/cultured meat, seafood, dairy, and egg products.
  - **Insects are explicitly excluded** from this definition, as they represent a distinct product category with different regulatory, cultural, and use-case (food vs. feed) dynamics.
  - **Animal feed applications are excluded.** This exercise concerns human food consumption only.
  - All figures should refer to **USglobal** consumption unless a question specifies a region.
  - If you use a different scope or definition than the one specified for any reason, state this explicitly in your rationale.

**Quantile format:** For each numerical question, provide your 10th percentile, 50th percentile (median), and 90th percentile estimates. This means: you believe there is a 10% chance the true value will be below your 10th percentile estimate, a 50% chance it will be below your median estimate, and a 90% chance it will be below your 90th percentile estimate. Your 10th-to-90th percentile range should reflect an interval you are 80% confident contains the true value.

**Purpose and accuracy framing:** This exercise is designed to produce the most accurate possible forecasts. At the resolution date, your estimates will be compared against the actual outcome. Reason as carefully and rigorously as you can, as if your accuracy will be evaluated.

**Reasoning approach:** Base your estimate on first-principles reasoning from the information provided, rather than deferring to or citing any specific existing named forecast or report you may be aware of. You are encouraged to disagree or agree with any of the material provided to you, and you may draw on any other relevant information you are aware of, provided you state this explicitly.

**Evidence standard:** Ensure every substantive claim you make is evidenced. Where possible, cite the specific source and section from the information provided, or name your source clearly if drawing on outside knowledge. State any assumptions you are making explicitly.

**Awareness check:** In your rationale, state whether you are aware of any specific existing named reports, forecasts, or predictions on this topic and, if so, name them and explain whether and if/how they influenced your estimate.

-----

## **Part B: Questions**

  - *\*Method: give these in one go, alongside the instructions and background infoto LLMs one question at a time to maximise chance of getting quality answers\**

### **Q1: 2026 alt-protein market share**

As of 2026, what percentage of global human food protein consumption (by mass, excluding animal feed) comes from alternative proteins as defined above? 

*Provide 10th/50th/90th percentile estimates as a percentage, and a written rationale*

### **Q2: 2030 alt-protein market share**

What percentage of global human food protein consumption (by mass, excluding animal feed) will come from alternative proteins as defined above, as of 2030? 

*Provide 10th/50th/90th percentile estimates as a percentage, and a written rationale*

### **Q3: 2035 alt-protein market share**

What percentage of global human food protein consumption (by mass, excluding animal feed) will come from alternative proteins as defined above, as of 2035? 

*Provide 10th/50th/90th percentile estimates as a percentage, and a written rationale*

  

### **NEW: Q1-3 combined:**

What will total US retail dollar sales of all plant-based categories be in the following years? Give 10th/50th/90th percentile estimates in nominal billions of 2025 USD. 

2026

2030

2035

  

### **Q4: Adoption shape reasoning**

Based on your answers above, and any other ideas you have, do you expect the growth in alt-protein market share between 2026 and 2035 to follow a roughly linear trajectory, an S-curve (slow initial growth, then rapid acceleration, then plateau), or another shape? Explain your reasoning, referencing which specific factors you believe would drive acceleration or deceleration.

### **NEW q4: cultivated and fermented:**

Option1: 

1.  What will be US sales of the following categories in the following resolution years
      
    1.  Fermented
    2.  Cultivated

  Years

1.  2026
2.  2030
3.  2035

  

Option 2: In 2030, what will be the US sales of cultivated and fermented categories (in 2025 USD)? In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries 

  

\*\*for this section, note that we dont have strict resolution criteria because it isnt really being measured yet (GFI measure indicators like new companies and investment), but we still want to know their ideas on what the dirvers/obstacles will be

### **Q5: Suggestions for future rounds**

*Optional - It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’. Again, we’d rather you be accurate in what you think than offer something for the sake of answering the question.*

Is there anything important that you havent included in your answers?

Is there any literature or data you think particularly important that we mightve missed?

Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration? 

-----

## Quantiles Explainer\!

## **Part C: Info Pack (given alongside every numerical question, Q1-Q4)**

All data below is presented as of the source's stated date. Where sources disagree, this is noted rather than resolved, so that you can reason about the disagreement yourself.

### **C.1 — Current market size and definitional variation**

Multiple market research firms publish different alt-protein market size estimates for the same period, largely because they define the market's scope differently:

  - One estimate (US retail alt-protein sales only) puts the market at approximately $8.1 billion.
  - A broader estimate that includes alternative proteins used in animal feed puts the global market at approximately $22.95 billion.
  - Growth rate projections across nine different published forecasts range from 5.29% to 21.32% CAGR, with a cluster of estimates in the 8-14% range. *(Source: New Market Pitch market analysis, "What is the real market size of the alternative protein market?", 13 March 2026 — a secondary aggregator; figures above are drawn from its comparison of GFI, Mordor Intelligence, Grand View Research, MarketsandMarkets, Precedence Research, IMARC, and Arizton reports.)*

### **C.2 — Historical baseline: global protein supply composition**

As of the most recent comprehensive estimate: globally, most dietary protein comes from plant sources (57%), followed by meat (18%), dairy (10%), fish and shellfish (6%), and other animal products (9%). *(Source: FAO data, as reported in Henchion et al., "Future Protein Supply and Demand," Foods journal, 2017, and reaffirmed in the 2024 European Parliament STOA study below.)*

Global meat consumption increased by approximately 60% between 1990 and 2009, and this growth trend has continued, driven particularly by income growth in Asia, Latin America, and the Middle East. *(Source: Henchion et al. 2017, citing FAO Food Balance Sheet data.)*

### **C.3 — Existing projections for alternative protein market share (the most directly relevant prior forecasts)**

A 2021 industry study estimated that in 2020, total alternative protein consumption (including plant-based alternatives) was approximately 13 million metric tonnes, representing approximately 2% of the animal protein market.

The same study's base-case scenario projects that by 2035, alternative proteins (including plant-based alternatives) will account for **11% of the global protein market for food**, with an upside scenario reaching **22%**. This study identifies Europe and North America as the currently most mature markets, but projects Asia-Pacific to account for roughly two-thirds of global alternative protein consumption by 2035.

For fermentation-derived alternatives specifically, the same study's base case projects these will reach 22 million metric tonnes globally by 2035, representing 2.5% of the global protein market for meat and meat alternatives — this assumes price parity with conventional meat is reached by 2025. *(Source: Witte et al., "Food for Thought: The Protein Transformation," Boston Consulting Group / Blue Horizon, 2021, as reported in the European Parliament's 2024 STOA study "Alternative protein sources for food and feed," Part 1, Section 4.2.)*

**Cultured/cultivated meat specifically has highly divergent existing projections** — worth noting given the wide disagreement:

  - One academic forecasting exercise (using expert probability elicitation across three time horizons) found a 54% aggregated probability that less than 100,000 tonnes of cultured meat would be sold globally (at any price point) before the end of 2051, and less than a 10% probability of more than 50 million tonnes being sold by that date.
  - By contrast, a McKinsey & Company analysis estimated cultured meat could provide up to 0.5% of the world's meat supply by 2030.
  - The BCG/Blue Horizon study above projects cultured meat reaching price parity with conventional meat by 2032, and production reaching 6 million metric tonnes by 2035 in its base case. *(Sources, respectively: Dullaghan & Linch, "Forecasts estimate limited cultured meat production through 2050," Effective Altruism Forum, 2022; Brennan et al., "Cultivated meat: Out of the lab, into the frying pan," McKinsey & Company, 2021; Witte et al. 2021 — all as reported in the European Parliament's 2024 STOA study, Section 4.2.4.)*

Conventional protein consumption to 2050 is separately projected to increase by 57% for meat and 48% for dairy under business-as-usual assumptions (though this and other conventional-protein projections generally do not explicitly model alt-protein competition as a factor). *(Source: Alexandratos & Bruinsma, FAO working paper, 2012, as reported in the European Parliament's 2024 STOA study, Section 4.1.)*

### **C.4 — Cost and price trends**

Plant-based meat currently carries an approximately 82% price premium over conventional meat; plant-based milk carries an approximately 103% premium over dairy milk.

Cultivated meat production costs fell from approximately $325,000 per pound in 2013 to approximately $17 per pound in 2024 — still 5-10 times the cost of conventional meat. An industry target for cultivated meat cost parity is approximately $2.92 per pound. *(Source: GFI market research and Food Navigator reporting, as compiled in New Market Pitch, 13 March 2026.)*

### **C.5 — Consumer behaviour and repeat purchase**

96% of plant-based meat buyers also still purchase conventional meat, indicating low category exclusivity. US plant-based meat sales have recently declined by approximately 7% year-over-year. Approximately 59% of US households purchase some plant-based food product, but only approximately 13% specifically purchase plant-based meat. *(Source: GFI market research, as compiled in New Market Pitch, 13 March 2026.)*

### **C.6 — Regulatory status**

As of 2024, cultured meat had been approved for commercial sale in three jurisdictions: Singapore (since 2020), the United States (2023), and Israel. It is not yet authorised in the EU. Separately, seven US states have enacted bans on the sale of cultivated meat. *(Sources: European Parliament 2024 STOA study, Section 3.2.2; state ban figure from New Market Pitch, 13 March 2026 — this latter figure has not been independently verified against primary legislative sources.)*

### **C.7 — Investment and industry structure**

Alternative protein industry investment has declined by approximately 78% from its 2021 peak. Over 40 companies in the sector shut down, merged, or were acquired between September 2024 and August 2025. *(Source: GFI investment data and Green Queen reporting, as compiled in New Market Pitch, 13 March 2026.)*

-----

# NOTES - not for LLM

## **Sourcing Summary Table**

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Source\*\* | \*\*Type\*\* | \*\*Date\*\* | \*\*What it contributes\*\* |
| Witte et al. ("Food for Thought: The Protein Transformation"), BCG/Blue Horizon | Industry consultancy study | 2021 | Core existing projections: 11-22% alt-protein share by 2035; fermentation and cultured meat sub-projections |
| European Parliament STOA study, "Alternative protein sources for food and feed" | Government research body, literature review | April 2024 | Synthesizes and cross-checks multiple projections; historical baseline; regulatory status; conventional protein 2050 projections |
| Henchion et al., "Future Protein Supply and Demand," \*Foods\* journal | Peer-reviewed academic review | 2017 | Historical protein consumption composition and trends; older but foundational |
| Dullaghan & Linch, Effective Altruism Forum | Independent forecasting analysis using expert elicitation | 2022 | Contrasting, more conservative cultured meat projection |
| Brennan et al., McKinsey & Company | Industry consultancy | 2021 | Contrasting, more aggressive cultured meat projection |
| New Market Pitch, "What is the real market size of the alternative protein market?" | Market-research aggregator/blog | 13 March 2026 | Most current market size, price, investment, and consumer behaviour data; \*\*note: this is a secondary source aggregating GFI, Green Queen, Food Navigator, and others — spot-check against primaries before using in the final report\*\* |
| GFI (Good Food Institute) | Nonprofit industry body, cited via New Market Pitch | Various | Underlying primary source for several figures above |

  
  
  

**Not yet accessed:** Fortune Business Insights, GMInsights, and MarketsAndMarkets reports from the original source list are paywalled/not yet reviewed in full; the Iowa State Digital Press article on consumer intention data was inaccessible (bot-blocked) — worth accessing manually before Week 4 finalization if these contain data not otherwise covered above.

  
  
  

# draft questions  

1.  Main forecast

What will total US retail dollar sales of all plant-based categories be in the following years? Give 10th/50th/90th percentile estimates in nominal billions of 2025 USD. 

2026

2030

2035

  

1.  In 2030, what will be the US sales of cultivated and fermented categories (in 2025 USD)?

  

Please give 10th,50th and 90th quantile forecasts. In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries 

  

Definition of cultivated and fermented: same as GFI

Resolution criteria: There is currently no direct measure of sales for cultivated and fermented categories. Therefore, for this question we will resolve it with the closest possible available measure at the time if one exists, but we are more interested in your reasoning for your forecast than it’s accuracy, given we don’t currently have an accurate measure. 

  

1.  Blind spots/ Any other information

*Optional - It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’. Again, we’d rather you be accurate in what you say here than offer something for the sake of answering the question.*

Is there anything important that you havent included in your forecasts or rationales?

Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration? 

  
  
  

# \[clean\] questions  

1.  What will total US retail dollar sales of all plant-based categories be in the following years? Give 10th/50th/90th percentile estimates in billions of 2025 USD. 

2026, 2030, 2035

 

 

1.  fermented/cultivated question

In 2030, what will be the US sales of cultivated and fermented categories (in 2025 USD)? In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries.

  
  

1.  Any other information/ sources 

  

*Optional - It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’. Again, we’d rather you be accurate in what you say here than offer something for the sake of answering the question.*

Is there anything important that you havent included in your forecasts or rationales?

Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration? 

  
  
  
  

# \[deprecated\] Final survey  

# Introduction

You are participating in a structured forecasting exercise. You will be asked several questions about the future of the alternative protein market in the U.S. For the forecasting questions, you will be given background information and asked to provide a probabilistic forecast and a rationale. 

# Instructions

**General Instructions:**

Accuracy

  - When making forecasts, please give a specific value in the metric stated in the question rather than a range.
  - You should give a specific value for each question, year and quantile (where applicable) rather than a range.

Alternative proteins definitions

  - Definitions relevant to each forecasting question are given in the background/resolution criteria section of each question.

<!-- end list -->

  - Insects/ insect-derived protein are explicitly excluded from this exercise, as they represent a distinct non-plant based product category.
  - Animal feed applications are excluded. This exercise concerns human food consumption only.

Demand

  - We are looking at demand in terms of US sales, but you should also consider supply side effects that could be captured in these figures.

AI focus

  - Development of AI seems likely to change the landscape of alternative proteins and plant based foods, including fermented and cultivated categories. You should give adequate attention to this when considering the factors affecting your forecasts.

  

**Rationale instructions:**

  - Your rationale should explain why you chose the specific value you gave for your forecasts, we encourage as much detail as required to fully explain your reasoning.

<!-- end list -->

  - In your rationale, you should consider the main factors (drivers and/or obstacles) you believe will affect the trajectory of demand over the given timescales, and you should explain how much of the change in trajectory you assign to each factor. You can draw on any factor you deem relevant to the forecast question.
      
      - Drivers = any factors that could be considered catalysts, enablers, or accelerators.
      - Obstacles = any factors that could be considered headwinds, constraints, bottlenecks or impediments.
  - Evidence standard: Ensure every substantive claim you make is evidenced. Where possible, cite the specific source and section from the information provided, or name your source clearly if drawing on outside knowledge. Also explain the method you used to come to your forecasted figure(s).
  - State any assumptions you’ve made clearly in your rationale.

**Quantile forecasts**

  - Where required, you may be asked to give quantile forecasts. For these, please, provide your 10th percentile, 50th percentile (median), and 90th percentile estimates. 
  - This means: you believe there is a 10% chance the true value will be below your 10th percentile estimate, a 50% chance it will be below your median estimate, and a 90% chance it will be below your 90th percentile estimate. Your 10th-to-90th percentile range should reflect an interval you are 80% confident contains the true value. 
  - For each quantile forecast, provide a specific value in the metric stated in the question rather than a range.

  
  
  
  

# Questions

1.  ## Main forecast

  
  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | What will total US retail dollar sales of plant-based protein be in the following years (in 2025 USD)?  |
| Background/ Resolution criteria | This question will resolve to the figure reported in GFI’s State of the Industry report for U.S. plant-based food retail sales, for the respective resolution year. The report is published in April/May the year after, so the 2026 question will resolve in roughly April–May 2027, and 2030 and 2035 will resolve against the same series. GFI defines plant based food as: Plant-based protein products are food products made from plant- or fungus-derived ingredients that are designed and marketed to directly replace conventional animal products, either as stand-alone products or within recipes. The category includes plant-based alternatives to meat and seafood; eggs; and dairy, including milk, creamer, yogurt, cheese, and ice cream. It also includes traditional plant-protein foods such as tofu, tempeh, and seitan, as well as other plant-based products positioned as protein sources or animal-product replacements, such as protein powders and liquids, ready-to-drink beverages, bars, prepared meals, and baked goods and desserts. Products such as veggie burgers are included even when they don't simulate meat, because they serve as a direct replacement for an animal-based product. Upstream plant protein ingredients, such as protein isolates, concentrates, and textured vegetable protein, form part of the plant-based supply chain but are distinct from the final consumer products they are used to make. The category excludes inherently plant-based whole foods, such as chickpeas and kale, that are not positioned as alternatives to animal products. It also excludes cultivated (cell-based) products, fermentation-derived proteins, and blended products that combine plant-based and conventional animal ingredients. GFI’s 2026 State of the Industry report \\\[\<https://gfi.org/wp-content/uploads/2026/05/GFI\_2026\_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf\>\\\]  notes that: “this study’s methodology has changed compared to that used in previous reporting by GFI. We do not recommend comparing data released in prior years to the data included here.” Dollar figures are in constant 2025 US dollars. Reported nominal values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages. If the GFI data source is no longer reported at the resolution dates, a close analogue will be calculated using the SPINS data directly, or with a panel of industry experts if no alternative is available.  |
| Years  | 2026, 2030, 2035 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions |   |

  

## Open ended questions:

1.  ### Cultivated and fermented categories

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | In 2030, what will be the US sales of cultivated and fermented categories (in 2025 USD)?  |
| Background/ Resolution criteria | There is currently no direct measure of sales for cultivated and fermented categories. Therefore, for this question we will resolve it with the closest possible available measure at the time if one exists, but for this question we are more interested in your reasoning for your forecast than it’s accuracy, given we don’t currently have an accurate measure.  Definitions:Cultivated meat is genuine animal meat, including poultry, seafood, and organ meats, produced by growing animal cells directly in a controlled environment rather than by raising and slaughtering animals. The resulting meat is composed of the same cell types as conventional meat and is designed to replicate its taste, texture, and nutritional profile. Final products may consist entirely of cultivated cells or combine cultivated cells with plant-based ingredients. The category is also referred to as cultured or cell-based meat. Fermentation-derived proteins are alternative proteins produced by cultivating microorganisms, such as fungi, yeast, bacteria, and microalgae, to make food or food ingredients that replace or improve on animal products. GFI identifies three approaches: traditional fermentation, biomass fermentation and precision fermentation. Fermentation-derived ingredients may be sold as stand-alone products or incorporated into plant-based and cultivated products to improve their taste, texture, and nutrition.  |
| Years  |  2030 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions | In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries. |

  

1.  ### Blind spots

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration?  |
| Background/ Resolution criteria | None: numerical forecast not required |
| Years  | None: numerical forecast not required |
| Quantiles | None: numerical forecast not required |
| Rationale Instructions | Open-ended: It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’.We’d rather you accurately reflect your thinking here than offer something for the sake of answering the question. |

  
  
  

Thank you for completing this survey.  

# testing output  

***Result of survey on Claude Opus 5.5, medium effort, incognito mode:***

  

I read GFI's 2026 report and checked 2026 data on Beyond Meat, CPI, cultivated meat, and precision fermentation. My forecasts and rationales follow, in the survey's order.

-----

## **Main forecast: US plant-based retail sales (constant 2025 USD)**

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Year\*\* | \*\*P10\*\* | \*\*P50 (median)\*\* | \*\*P90\*\* |
| 2026 | $7.15B | $7.60B | $8.00B |
| 2030 | $6.00B | $7.30B | $8.80B |
| 2035 | $5.20B | $7.20B | $10.00B |

### **Starting point**

The 2025 figure is already in 2025 dollars, so it is my starting value. SPINS data put U.S. plant-based food retail sales at $7.9 billion in 2025, down 2% in dollars and 3% in units from 2024. By category:

  - **Meat and seafood:** about $1 billion, with dollars down 10% and units down 11%.
  - **Milk:** the largest category at $2.7 billion, a 13% share of retail milk, down 2%.
  - **Growing categories:** creamer, yogurt, ready-to-drink beverages, protein powders and liquids, bars, baked goods and desserts, and tofu, tempeh and seitan.

The other \~$4.2B (everything outside meat and milk) was roughly flat in aggregate. Some parts grew and others, like cheese and frozen meals, shrank.

### **Method**

For 2026, I built the estimate category by category. I projected nominal sales for the SPINS year ending November 2026, then deflated them by expected food-at-home CPI growth. For 2030 and 2035, I used scenario-weighted real growth rates, then attributed the gap from 2025 to individual drivers.

### **2026 build**

**Meat and seafood: −8% nominal, about −$0.08B.** 2026 data from the largest pure-play brand shows the decline continuing:

  - Beyond Meat's U.S. retail revenue fell 15.3% in Q1 2026.
  - It fell 9.9% in Q2, which the company blamed on weak category demand and fewer points of distribution.
  - Mintel likewise projects the US plant-based protein market falling to about $1.075 billion in 2026, from a 2021 peak of $1.65 billion. That uses a different definition from GFI's, but the direction matches.

The decline is slowing, so I use −8% rather than −10%.

**Milk: −1.5%, about −$0.04B.** It is a mature category with brand-level pockets of growth.

**Everything else: flat to slightly up.** Protein-positioned products offset declines in cheese and meals.

**Nominal total: about $7.78B (−1.5%).** SPINS itself describes plant-based unit declines narrowing substantially between 2023 and 2025. That supports a smaller decline than 2025's −2%, not a reversal.

**Deflator: about 2.4%.** Food-at-home CPI rose 2.2% in the 12 months to August 2026, after +2.9% year over year in January 2026. I assume a calendar-year average of about 2.4%.

**Result: 7.78 / 1.024 ≈ $7.60B median.**

**Why the band is ±5%:** SPINS channel coverage or the category build could change again. GFI says outright that its methodology changed from prior years and it advises against comparing to earlier data. The P90 of $8.0B needs flat nominal sales plus low inflation. The P10 of $7.15B covers a steeper meat decline, a milk downturn, or a downward restatement.

### **2030 and 2035: drivers and how much weight I give them**

**2030 median of** **7.3Bis-****0.6B versus 2025 (real).**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Factor\*\* | \*\*Type\*\* | \*\*Contribution\*\* |
| Meat-analog retreat: taste/price gaps, lost distribution and shelf visibility, "ultra-processed" framing | Obstacle | −$0.35B |
| Plant milk maturing, losing share to high-protein and lactose-free dairy | Obstacle | −$0.30B |
| De-positioning: brands dropping "plant-based" framing so products fall out of SPINS's plant-based attribute; consolidation and closures | Obstacle (partly a measurement effect) | −$0.20B |
| Price deflation and private label: falling real prices cut constant-dollar sales even at stable volume | Obstacle | −$0.15B |
| Protein trend: powders, RTD, bars, yogurt, creamer | Driver | \\+$0.30B |
| AI-accelerated formulation and ingredient cost reduction | Driver | \\+$0.10B |
| Beef price cycle: narrows the gap now, likely reverses as the herd rebuilds | Roughly neutral by 2030 | $0 |

Evidence behind the main rows:

  - **Meat obstacles.** Consumers say taste and price are the top barriers. 70% of plant-based meat units now sell from the frozen section, up from 66% in 2023. Only about 14% of locations at the top 250 chains that serve meat also offer a plant-based analog, likely lower than before.
  - **Capital.** At least 19 plant-based companies were acquired, and several paused or shut down after failing to raise follow-on funding.
  - **Protein trend.** The protein-positioned categories are the ones growing. Consumers who see plant-based meat as healthier spend 56% more on it.
  - **Beef prices.** Plant-based beef's price premium over conventional fell to 8% in 2025 from 14% in 2024. That is a tailwind for now, but I expect it to fade as the cattle herd rebuilds.

**AI gets a small weight by 2030.** Sensory and texture advances are real, for example AI-designed ingredients such as Shiru's OleoPro fat. But the bottleneck to sales is mostly distribution, price, and consumer reason-to-buy, not ingredient discovery. Reformulation-to-shelf cycles also take 2–4 years.

**AI also cuts the other way, through capital.** AI captured nearly half of all global funding in 2025, and venture capital tightened in most other sectors. That crowding out slows scale-up of AI-found improvements.

**2035 median of** **7.2Bis-****0.1B versus 2030.**

  - AI-enabled taste and cost improvements finally reach products: +$0.4B
  - Protein trend continues: +$0.2B
  - Further meat and milk attrition: −$0.4B
  - Growth shifting into blended and fermentation-hybrid products that GFI's definition excludes: −$0.3B

The last factor matters. GFI's own research found that half of those willing to buy blended products had low intent to buy fully plant-based meat. That suggests future growth may land outside this metric.

**Why the bands are so wide.** The 2035 P90 of $10B is a real re-acceleration scenario: price parity plus a health halo, about +3%/yr real from 2030. The P10 of $5.2B is continued \~−3%/yr real attrition plus heavy de-positioning.

### **Assumptions**

  - GFI and SPINS continue the current methodology and channel set.
  - No federal policy shock such as labeling bans.
  - Food-at-home inflation of about 2–3% a year.
  - GLP-1 adoption is roughly neutral. It cuts total calories but raises protein-seeking, which helps powders and RTD and hurts indulgent categories.

-----

## **Cultivated and fermented categories, 2030 (US, 2025 USD)**

|  |  |  |
| :-: | :-: | :-: |
| \*\*P10\*\* | \*\*P50\*\* | \*\*P90\*\* |
| $120M | $400M | $1.6B |

### **Scope I am forecasting**

I count consumer-facing US sales (retail plus foodservice) of products where cultivated cells or biomass/precision fermentation provide the primary protein or value proposition.

I exclude three things:

  - **Minor fermentation inputs.** Examples are fermentation-derived rennet in ordinary cheese and heme in a plant burger. Counting these would push the total into billions.
  - **Traditional fermented plant foods** like tempeh, which GFI already counts as plant-based.
  - **B2B ingredient revenue**, counted separately from the finished products it goes into.

### **Median build**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Component\*\* | \*\*2030 median\*\* | \*\*Reasoning\*\* |
| Cultivated meat | \\\~$10M | Explained below |
| Biomass fermentation (mycoprotein, mycelium) | \\\~$120M | Explained below |
| Precision-fermentation-led consumer products | \\\~$270M | Explained below |

**Cultivated meat.** Five products have US clearance, but Believer, one of them, shut down in December 2025. Sales are tiny: restaurant placements plus Mission Barns' pork meatballs, a hybrid of cultivated fat and plant protein, at $13.99 a tray.

State bans are spreading. South Dakota became the 8th state to ban cultivated meat, and in March a federal appeals court let Florida's ban stand despite federal approval.

The binding constraints are capex, bioreactor scale, and the cost of growth media. Reaching $80M (my P90 for this component) would need a hybrid-fat product in mainstream retail at scale.

**Biomass fermentation (mycoprotein, mycelium).** This includes Quorn, mycelium bacon and whole cuts, and Beyond Meat's whole-cut mycelium steak. The segment has had high-profile failures. It grows only modestly because its products face the same taste, price, and visibility headwinds as plant-based meat.

**Precision-fermentation-led products.** This is the most likely growth engine: animal-free whey and egg proteins in protein powders, RTD, bars, and ice cream, riding the protein trend. Examples include Perfect Day's whey supply agreements in early 2026 and Vivici launching its precision-fermented lactoferrin in the US under self-affirmed GRAS. High-value, low-volume proteins like lactoferrin reach profitability first, which favors supplements over commodity dairy.

### **Main drivers and obstacles**

**Drivers**

  - **AI in strain engineering and bioprocess optimization.** This is where AI matters most for fermentation. Better titers and yields directly cut cost per kg.
  - **Demand for protein**, which fits precision-fermentation whey especially well.
  - **Self-affirmed GRAS** as a relatively fast US regulatory route for fermentation ingredients.

**Obstacles**

  - **Fermentation capacity and capex.** This, not discovery, is the binding constraint. AI does not build stainless steel.
  - **Scarce capital.** The whole alternative protein ecosystem, including cultivated and fermentation companies, raised $881 million in 2025, and AI is crowding out other investment.
  - **State bans on cultivated meat** and possible federal regulatory hostility, including a possible end to self-affirmed GRAS, which MAHA has targeted.
  - **Price gaps with commodity dairy protein.**

**Why the range is so wide.** Market-research estimates disagree hugely. One firm puts precision-fermentation dairy protein ingredients at USD 87.2 million in 2026. Another puts the precision fermentation dairy alternatives market at USD 3.0 billion in 2026. That spread comes from scope differences, which means a resolution measure could land almost anywhere. My current-year baseline is about $150–250M on my definition, and that figure is itself uncertain. My P90 of $1.6B reflects both a real breakout of precision-fermentation whey and a broader resolution definition.

-----

## **Blind spots**

1.  **The time windows don't match.** GFI's "annual" figure is SPINS 52 weeks ending November 30, but the deflator uses calendar-year CPI averages. Also, BLS has no October 2025 CPI value because of the 2025 lapse in appropriations, so the 2025 base-year average needs a stated imputation rule.  
      
2.  **Which figure resolves the question isn't pinned down.** The same report says both $8 billion and $7.9 billion. GFI has changed methodology before and may restate. The survey should specify first-published versus revised, and the rounding precision.  
      
3.  **"Demand" is measured as retail dollars under a marketing label.** Inclusion depends on SPINS's "plant-based positioned" attribute. If brands reframe products as "protein" rather than "plant-based," the category can shrink without anyone eating less plant protein. This may be the biggest structural bias in the series. The metric also leaves out foodservice ($291 million in plant-based protein distributor sales, plus $288 million in plant milk), and much of e-commerce and Costco appear only as projections.  
      
4.  **Definitions overlap and exclude.** GFI's plant-based definition includes fungus-derived products and tempeh, which the fermentation question also claims. Products like Impossible, which uses precision-fermented heme, sit on the boundary. Blends are excluded even though GFI's own research names them as a route to new consumers. Growth moving into hybrids will read as "decline" in the main series.  
      
5.  **The AI instruction invites overweighting.** On 2030 timescales, AI's biggest effect may be negative: pulling capital away from the sector. The prompt asks mainly about AI as a driver of product improvement.  
      
6.  **Major policy and health factors aren't mentioned.** These include state cultivated-meat bans, federal food policy and "ultra-processed" framing, GRAS reform, tariffs, and GLP-1 drugs. Any of these could plausibly matter as much as AI.  
      
7.  **Deflating by food-at-home CPI mixes price and volume.** If plant-based prices fall faster than general food prices, which is the goal of cost parity, constant-dollar sales can fall even as consumption rises.  
      
8.  **The fermentation question has no resolution source.** Scoring it against "the closest available measure" rewards guessing the analyst's scope rather than forecasting the market.  
      

I can put this into a document if you'd like to submit it in that form.

  
  
  
  

# Same answer, with hyperlinks (pasted keeping source formatting)

I read GFI's 2026 report and checked 2026 data on Beyond Meat, CPI, cultivated meat, and precision fermentation. My forecasts and rationales follow, in the survey's order.

-----

### **Main forecast: US plant-based retail sales (constant 2025 USD)**

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Year\*\* | \*\*P10\*\* | \*\*P50 (median)\*\* | \*\*P90\*\* |
| 2026 | $7.15B | $7.60B | $8.00B |
| 2030 | $6.00B | $7.30B | $8.80B |
| 2035 | $5.20B | $7.20B | $10.00B |

#### **Starting point**

The 2025 figure is already in 2025 dollars, so it is my starting value. SPINS data put U.S. plant-based food retail sales at $7.9 billion in 2025, down 2% in dollars and 3% in units from 2024. By category:[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

  - **Meat and seafood:** about $1 billion, with dollars down 10% and units down 11%.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **Milk:** the largest category at $2.7 billion, a 13% share of retail milk, down 2%.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **Growing categories:** creamer, yogurt, ready-to-drink beverages, protein powders and liquids, bars, baked goods and desserts, and tofu, tempeh and seitan.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

The other \~$4.2B (everything outside meat and milk) was roughly flat in aggregate. Some parts grew and others, like cheese and frozen meals, shrank.

#### **Method**

For 2026, I built the estimate category by category. I projected nominal sales for the SPINS year ending November 2026, then deflated them by expected food-at-home CPI growth. For 2030 and 2035, I used scenario-weighted real growth rates, then attributed the gap from 2025 to individual drivers.

#### **2026 build**

**Meat and seafood: −8% nominal, about −$0.08B.** 2026 data from the largest pure-play brand shows the decline continuing:

  - Beyond Meat's U.S. retail revenue fell 15.3% in Q1 2026.[ sec](https://www.sec.gov/Archives/edgar/data/0001655210/000165521026000033/ex991pressrelease-q12026ea.htm)
  - It fell 9.9% in Q2, which the company blamed on weak category demand and fewer points of distribution.[ sec](https://www.sec.gov/Archives/edgar/data/0001655210/000165521026000053/ex991pressrelease-q22026ea.htm)
  - Mintel likewise projects the US plant-based protein market falling to about $1.075 billion in 2026, from a 2021 peak of $1.65 billion. That uses a different definition from GFI's, but the direction matches.[ mintel](https://store.mintel.com/report/us-plant-based-proteins-market-report)

The decline is slowing, so I use −8% rather than −10%.

**Milk: −1.5%, about −$0.04B.** It is a mature category with brand-level pockets of growth.

**Everything else: flat to slightly up.** Protein-positioned products offset declines in cheese and meals.

**Nominal total: about $7.78B (−1.5%).** SPINS itself describes plant-based unit declines narrowing substantially between 2023 and 2025. That supports a smaller decline than 2025's −2%, not a reversal.[ spins](https://www.spins.com/resources/report/the-evolution-of-plant-based-the-next-wave/)

**Deflator: about 2.4%.** Food-at-home CPI rose 2.2% in the 12 months to August 2026, after +2.9% year over year in January 2026. I assume a calendar-year average of about 2.4%.[ bls](https://www.bls.gov/news.release/archives/cpi_09112026.htm)[getfoodfacts](https://getfoodfacts.com/prices/food-at-home)

**Result: 7.78 / 1.024 ≈ $7.60B median.**

**Why the band is ±5%:** SPINS channel coverage or the category build could change again. GFI says outright that its methodology changed from prior years and it advises against comparing to earlier data. The P90 of $8.0B needs flat nominal sales plus low inflation. The P10 of $7.15B covers a steeper meat decline, a milk downturn, or a downward restatement.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

#### **2030 and 2035: drivers and how much weight I give them**

**2030 median of** **7.3Bis-****0.6B versus 2025 (real).**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Factor\*\* | \*\*Type\*\* | \*\*Contribution\*\* |
| Meat-analog retreat: taste/price gaps, lost distribution and shelf visibility, "ultra-processed" framing | Obstacle | −$0.35B |
| Plant milk maturing, losing share to high-protein and lactose-free dairy | Obstacle | −$0.30B |
| De-positioning: brands dropping "plant-based" framing so products fall out of SPINS's plant-based attribute; consolidation and closures | Obstacle (partly a measurement effect) | −$0.20B |
| Price deflation and private label: falling real prices cut constant-dollar sales even at stable volume | Obstacle | −$0.15B |
| Protein trend: powders, RTD, bars, yogurt, creamer | Driver | \\+$0.30B |
| AI-accelerated formulation and ingredient cost reduction | Driver | \\+$0.10B |
| Beef price cycle: narrows the gap now, likely reverses as the herd rebuilds | Roughly neutral by 2030 | $0 |

Evidence behind the main rows:

  - **Meat obstacles.** Consumers say taste and price are the top barriers. 70% of plant-based meat units now sell from the frozen section, up from 66% in 2023. Only about 14% of locations at the top 250 chains that serve meat also offer a plant-based analog, likely lower than before.[ gfigfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **Capital.** At least 19 plant-based companies were acquired, and several paused or shut down after failing to raise follow-on funding.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **Protein trend.** The protein-positioned categories are the ones growing. Consumers who see plant-based meat as healthier spend 56% more on it.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **Beef prices.** Plant-based beef's price premium over conventional fell to 8% in 2025 from 14% in 2024. That is a tailwind for now, but I expect it to fade as the cattle herd rebuilds.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

**AI gets a small weight by 2030.** Sensory and texture advances are real, for example AI-designed ingredients such as Shiru's OleoPro fat. But the bottleneck to sales is mostly distribution, price, and consumer reason-to-buy, not ingredient discovery. Reformulation-to-shelf cycles also take 2–4 years.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

**AI also cuts the other way, through capital.** AI captured nearly half of all global funding in 2025, and venture capital tightened in most other sectors. That crowding out slows scale-up of AI-found improvements.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

**2035 median of** **7.2Bis-****0.1B versus 2030.**

  - AI-enabled taste and cost improvements finally reach products: +$0.4B
  - Protein trend continues: +$0.2B
  - Further meat and milk attrition: −$0.4B
  - Growth shifting into blended and fermentation-hybrid products that GFI's definition excludes: −$0.3B

The last factor matters. GFI's own research found that half of those willing to buy blended products had low intent to buy fully plant-based meat. That suggests future growth may land outside this metric.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

**Why the bands are so wide.** The 2035 P90 of $10B is a real re-acceleration scenario: price parity plus a health halo, about +3%/yr real from 2030. The P10 of $5.2B is continued \~−3%/yr real attrition plus heavy de-positioning.

#### **Assumptions**

  - GFI and SPINS continue the current methodology and channel set.
  - No federal policy shock such as labeling bans.
  - Food-at-home inflation of about 2–3% a year.
  - GLP-1 adoption is roughly neutral. It cuts total calories but raises protein-seeking, which helps powders and RTD and hurts indulgent categories.

-----

### **Cultivated and fermented categories, 2030 (US, 2025 USD)**

|  |  |  |
| :-: | :-: | :-: |
| \*\*P10\*\* | \*\*P50\*\* | \*\*P90\*\* |
| $120M | $400M | $1.6B |

#### **Scope I am forecasting**

I count consumer-facing US sales (retail plus foodservice) of products where cultivated cells or biomass/precision fermentation provide the primary protein or value proposition.

I exclude three things:

  - **Minor fermentation inputs.** Examples are fermentation-derived rennet in ordinary cheese and heme in a plant burger. Counting these would push the total into billions.
  - **Traditional fermented plant foods** like tempeh, which GFI already counts as plant-based.
  - **B2B ingredient revenue**, counted separately from the finished products it goes into.

#### **Median build**

|  |  |  |
| :-: | :-: | :-: |
| \*\*Component\*\* | \*\*2030 median\*\* | \*\*Reasoning\*\* |
| Cultivated meat | \\\~$10M | Explained below |
| Biomass fermentation (mycoprotein, mycelium) | \\\~$120M | Explained below |
| Precision-fermentation-led consumer products | \\\~$270M | Explained below |

**Cultivated meat.** Five products have US clearance, but Believer, one of them, shut down in December 2025. Sales are tiny: restaurant placements plus Mission Barns' pork meatballs, a hybrid of cultivated fat and plant protein, at $13.99 a tray.[ foodnavigator](https://www.foodnavigator.com/Article/2026/02/18/cultivated-meat-regulation-where-countries-stand-in-2026/)[greenqueen](https://www.greenqueen.com.hk/mission-barns-lab-grown-meat-cultivated-pork-supermarket-berkeley-bowl/)

State bans are spreading. South Dakota became the 8th state to ban cultivated meat, and in March a federal appeals court let Florida's ban stand despite federal approval.[ SubstackSubstack](https://cultivatedbites.substack.com/p/the-month-in-cultivated-meat-march-1e7)

The binding constraints are capex, bioreactor scale, and the cost of growth media. Reaching $80M (my P90 for this component) would need a hybrid-fat product in mainstream retail at scale.

**Biomass fermentation (mycoprotein, mycelium).** This includes Quorn, mycelium bacon and whole cuts, and Beyond Meat's whole-cut mycelium steak. The segment has had high-profile failures. It grows only modestly because its products face the same taste, price, and visibility headwinds as plant-based meat.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)

**Precision-fermentation-led products.** This is the most likely growth engine: animal-free whey and egg proteins in protein powders, RTD, bars, and ice cream, riding the protein trend. Examples include Perfect Day's whey supply agreements in early 2026 and Vivici launching its precision-fermented lactoferrin in the US under self-affirmed GRAS. High-value, low-volume proteins like lactoferrin reach profitability first, which favors supplements over commodity dairy.[ openpr](https://www.openpr.com/news/4619521/precision-fermentation-market-2035-dairy-proteins-whey)[nutritioninsight](https://www.nutritioninsight.com/news/vivici-lactoferrin-precision-fermentation.html)

#### **Main drivers and obstacles**

**Drivers**

  - **AI in strain engineering and bioprocess optimization.** This is where AI matters most for fermentation. Better titers and yields directly cut cost per kg.
  - **Demand for protein**, which fits precision-fermentation whey especially well.
  - **Self-affirmed GRAS** as a relatively fast US regulatory route for fermentation ingredients.

**Obstacles**

  - **Fermentation capacity and capex.** This, not discovery, is the binding constraint. AI does not build stainless steel.
  - **Scarce capital.** The whole alternative protein ecosystem, including cultivated and fermentation companies, raised $881 million in 2025, and AI is crowding out other investment.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
  - **State bans on cultivated meat** and possible federal regulatory hostility, including a possible end to self-affirmed GRAS, which MAHA has targeted.
  - **Price gaps with commodity dairy protein.**

**Why the range is so wide.** Market-research estimates disagree hugely. One firm puts precision-fermentation dairy protein ingredients at USD 87.2 million in 2026. Another puts the precision fermentation dairy alternatives market at USD 3.0 billion in 2026. That spread comes from scope differences, which means a resolution measure could land almost anywhere. My current-year baseline is about $150–250M on my definition, and that figure is itself uncertain. My P90 of $1.6B reflects both a real breakout of precision-fermentation whey and a broader resolution definition.[ futuremarketinsights](https://www.futuremarketinsights.com/reports/precision-fermentation-dairy-protein-ingredients-market)[openpr](https://www.openpr.com/news/4586099/usa-precision-fermentation-dairy-alternatives-market-expands)

-----

### **Blind spots**

1.  **The time windows don't match.** GFI's "annual" figure is SPINS 52 weeks ending November 30, but the deflator uses calendar-year CPI averages. Also, BLS has no October 2025 CPI value because of the 2025 lapse in appropriations, so the 2025 base-year average needs a stated imputation rule.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)[bls](https://www.bls.gov/news.release/archives/cpi_09112026.htm)
2.  **Which figure resolves the question isn't pinned down.** The same report says both $8 billion and $7.9 billion. GFI has changed methodology before and may restate. The survey should specify first-published versus revised, and the rounding precision.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
3.  **"Demand" is measured as retail dollars under a marketing label.** Inclusion depends on SPINS's "plant-based positioned" attribute. If brands reframe products as "protein" rather than "plant-based," the category can shrink without anyone eating less plant protein. This may be the biggest structural bias in the series. The metric also leaves out foodservice ($291 million in plant-based protein distributor sales, plus $288 million in plant milk), and much of e-commerce and Costco appear only as projections.[ gfi](https://gfi.org/wp-content/uploads/2026/05/GFI_2026_State-of-the-Industry-Plant-based-meat-seafood-eggs-dairy-and-ingredients.pdf)
4.  **Definitions overlap and exclude.** GFI's plant-based definition includes fungus-derived products and tempeh, which the fermentation question also claims. Products like Impossible, which uses precision-fermented heme, sit on the boundary. Blends are excluded even though GFI's own research names them as a route to new consumers. Growth moving into hybrids will read as "decline" in the main series.
5.  **The AI instruction invites overweighting.** On 2030 timescales, AI's biggest effect may be negative: pulling capital away from the sector. The prompt asks mainly about AI as a driver of product improvement.
6.  **Major policy and health factors aren't mentioned.** These include state cultivated-meat bans, federal food policy and "ultra-processed" framing, GRAS reform, tariffs, and GLP-1 drugs. Any of these could plausibly matter as much as AI.
7.  **Deflating by food-at-home CPI mixes price and volume.** If plant-based prices fall faster than general food prices, which is the goal of cost parity, constant-dollar sales can fall even as consumption rises.
8.  **The fermentation question has no resolution source.** Scoring it against "the closest available measure" rewards guessing the analyst's scope rather than forecasting the market.

I can put this into a document if you'd like to submit it in that form.

  
  
  
  

# edits from survey iteration  

  - Scope for the fermentation/cultivated question - should we still tell it what to include/not eg foodservice and minor ingredients?
      
      - ~~\~\~And add this for the overlap issue: This question is designed to identify the dynamics specific to cultivated and fermentation-derived proteins, not to produce a figure that adds to the main forecast. Some products counted here, such as mycoprotein and other fungus-derived products, may also be counted in the plant-based figure in the main question. That overlap is fine: do not adjust your answer to avoid it. Where your forecast includes products that may also fall under the plant-based definition, say which ones.\~\~~~
      - Also this so they dont waste effort deifning what toinclude in this:

~~**Include:**~~

  - ~~\~\~US consumer sales through both retail and foodservice (restaurants, catering and other food-away-from-home outlets).\~\~~~
  - ~~\~\~Products where cultivated cells or fermentation-derived ingredients provide the main protein or the main reason to buy, such as cultivated chicken, mycoprotein products, or protein powders made with animal-free whey.\~\~~~
  - ~~\~\~Blended products containing cultivated cells, even when most of the product is plant-based.\~\~~~
  - ~~\~\~Food and drink products, including protein powders and ready-to-drink shakes.\~\~~~

~~**Exclude:**~~

  - ~~\~\~Products where a fermentation-derived ingredient is a minor input rather than the main protein, such as rennet in cheese, enzymes, flavourings, colourings, or heme in a plant-based burger.\~\~~~
  - ~~\~\~Long-established traditional fermented foods such as tempeh, miso and natto.\~\~~~
  - ~~\~\~Revenue from ingredients sold to other companies. Count only the finished products sold to consumers, so the same product is not counted twice.\~\~~~
  - ~~\~\~Dietary supplements sold as capsules or tablets.\~\~~~
  - ~~\~\~Insects and animal feed, as in the rest of the survey.\~\~~~

<!-- end list -->

  - ~~\~\~Add: “consider any policy, health or economic factors” - otherwise it tends to think some factors like GLP-1s are outside the scope of the exercise\~\~~~
  - New inflation wording:
      
      - GFI's annual figure covers the SPINS 52-week period ending in late November or early December. Nominal values are converted to constant 2025 dollars using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11). The deflator for each year is the average of the monthly index values from December of the previous year to November of that year. The 2025 base is the average of December 2024 to November 2025. The October 2025 value was not published because of the 2025 federal government shutdown, so the 2025 base uses the 11 available months. If any other month's value is unavailable, that year's average uses the months that are available. 
      - ~~\~\~\*\*Tell the models they don't need to do this.\*\*\~\~ \~\~Add a line to the instructions such as: "You do not need to calculate the inflation adjustment precisely. Forecast in constant 2025 dollars and state the annual food-at-home inflation rate you assumed." This keeps the rule for resolution and stops models from spending their rationale on CPI arithmetic, which was your concern in the pilot.\~\~~~
      - **Resolution timing still works.** November CPI is published in mid-December, well before GFI's report in April or May, so every year's deflator is available by the time the question resolves.
  - About searching abilities: **Give every model the same access.** Open-weights models usually don't come with built-in search, while the closed ones do, and each provider's search tool behaves differently. If some models can search and others can't, you'll partly be measuring access rather than forecasting skill. Ideally run all models through the same search tool in your setup (for example via Claude Code). If that isn't possible, record exactly which tool each model had, and treat it as a limitation.
  - **Log what they looked at.** Ask each model to list the sources it consulted, with URLs. With real search, links are checkable rather than likely to be invented. Also keep the date and time of each run, since search results change. Run the whole panel within a short window so all models see roughly the same information.
  -   
      

# \[deprecated\] Final survey 1  

# Introduction

You are participating in a structured forecasting exercise. You will be asked several questions about the future of the alternative protein market in the U.S. For the forecasting questions, you will be given background information and asked to provide a probabilistic forecast and a rationale. 

# Instructions

**General Instructions:**

Accuracy

  - When making forecasts, please give a specific value in the metric stated in the question rather than a range.
  - You should give a specific value for each question, year and quantile (where applicable) rather than a range.

Resources

  - You should use any publicly available resources you can find to help you with making your forecasts, provided you cite them clearly, and how they shaped your thinking.

Alternative proteins definitions

  - Definitions relevant to each forecasting question are given in the background/resolution criteria section of each question.

<!-- end list -->

  - Insects/ insect-derived protein are explicitly excluded from this exercise, as they represent a distinct non-plant based product category.
  - Animal feed applications are excluded. This exercise concerns human food consumption only.

Demand

  - We are looking at demand in terms of US sales, but you should also consider supply side effects that could be captured in these figures.

AI focus

  - Development of AI seems likely to change the landscape of alternative proteins and plant based foods, including fermented and cultivated categories. You should give adequate attention to this when considering the factors affecting your forecasts.

  

**Rationale instructions:**

  - Your rationale should explain why you chose the specific value you gave for your forecasts, we encourage as much detail as required to fully explain your reasoning.

<!-- end list -->

  - In your rationale, you should consider the main factors (drivers and/or obstacles) you believe will affect the trajectory of demand over the given timescales, and you should explain how much of the change in trajectory you assign to each factor. You can draw on any factor you deem relevant to the forecast question, including but not limited to: policy, health or economic factors.
      
      - Drivers = any factors that could be considered catalysts, enablers, or accelerators.
      - Obstacles = any factors that could be considered headwinds, constraints, bottlenecks or impediments.
  - Evidence standard: Ensure every substantive claim you make is evidenced. Where possible, cite the specific source and section from the information provided, or name your source clearly if drawing on outside knowledge. Also explain the method you used to come to your forecasted figure(s).
  - State any assumptions you’ve made clearly in your rationale.

**Quantile forecasts**

  - Where required, you may be asked to give quantile forecasts. For these, please, provide your 10th percentile, 50th percentile (median), and 90th percentile estimates. 
  - This means: you believe there is a 10% chance the true value will be below your 10th percentile estimate, a 50% chance it will be below your median estimate, and a 90% chance it will be below your 90th percentile estimate. Your 10th-to-90th percentile range should reflect an interval you are 80% confident contains the true value. 
  - For each quantile forecast, provide a specific value in the metric stated in the question rather than a range.

# Questions

1.  ## Main forecast

  
  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | What will total US retail dollar sales of plant-based protein be in the following years (in 2025 USD)?  |
| Background/ Resolution criteria | This question will resolve to the figure reported in GFI’s State of the Industry report for U.S. plant-based food retail sales, for the respective resolution year. The report is published in April/May the year after, so the 2026 question will resolve in roughly April–May 2027, and 2030 and 2035 will resolve against the same series. GFI defines plant based food as: Plant-based protein products are food products made from plant- or fungus-derived ingredients that are designed and marketed to directly replace conventional animal products, either as stand-alone products or within recipes. The category includes plant-based alternatives to meat and seafood; eggs; and dairy, including milk, creamer, yogurt, cheese, and ice cream. It also includes traditional plant-protein foods such as tofu, tempeh, and seitan, as well as other plant-based products positioned as protein sources or animal-product replacements, such as protein powders and liquids, ready-to-drink beverages, bars, prepared meals, and baked goods and desserts. Products such as veggie burgers are included even when they don't simulate meat, because they serve as a direct replacement for an animal-based product. Upstream plant protein ingredients, such as protein isolates, concentrates, and textured vegetable protein, form part of the plant-based supply chain but are distinct from the final consumer products they are used to make. The category excludes inherently plant-based whole foods, such as chickpeas and kale, that are not positioned as alternatives to animal products. It also excludes cultivated (cell-based) products, fermentation-derived proteins, and blended products that combine plant-based and conventional animal ingredients. Dollar figures are in constant 2025 US dollars. Reported values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.You do not need to calculate the inflation adjustment precisely. Forecast in constant 2025 dollars and state the annual food-at-home inflation rate you assumed If the GFI data source is no longer reported at the resolution dates, a close analogue will be calculated using the SPINS data directly, or with a panel of industry experts if no alternative is available.  |
| Years  | 2026, 2030, 2035 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions |   |

  

## Open ended questions:

1.  ### Cultivated and fermented categories

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | In 2030, what will be the US sales of cultivated and fermented categories (in 2025 USD)?  |
| Background/ Resolution criteria | There is currently no direct measure of sales for cultivated and fermented categories. Therefore, for this question we will resolve it with the closest possible available measure at the time if one exists, but for this question we are more interested in your reasoning for your forecast than it’s accuracy, given we don’t currently have an accurate measure. This question is designed to identify the dynamics specific to cultivated and fermentation-derived proteins, not to produce a figure that adds to the main forecast. Some products counted here, such as mycoprotein and other fungus-derived products, may also be counted in the plant-based figure in the main question. That overlap is fine: do not adjust your answer to avoid it. Definitions:Cultivated meat is genuine animal meat, including poultry, seafood, and organ meats, produced by growing animal cells directly in a controlled environment rather than by raising and slaughtering animals. The resulting meat is composed of the same cell types as conventional meat and is designed to replicate its taste, texture, and nutritional profile. Final products may consist entirely of cultivated cells or combine cultivated cells with plant-based ingredients. The category is also referred to as cultured or cell-based meat. Fermentation-derived proteins are alternative proteins produced by cultivating microorganisms, such as fungi, yeast, bacteria, and microalgae, to make food or food ingredients that replace or improve on animal products. GFI identifies three approaches: traditional fermentation, biomass fermentation and precision fermentation. Fermentation-derived ingredients may be sold as stand-alone products or incorporated into plant-based and cultivated products to improve their taste, texture, and nutrition. Include:  - US consumer sales through both retail and foodservice (restaurants, catering and other food-away-from-home outlets).&#10;  - Products where cultivated cells or fermentation-derived ingredients provide the main protein or the main reason to buy, such as cultivated chicken, mycoprotein products, or protein powders made with animal-free whey.&#10;  - Blended products containing cultivated cells, even when most of the product is plant-based.&#10;  - Food and drink products, including protein powders and ready-to-drink shakes.Exclude:  - Products where a fermentation-derived ingredient is a minor input rather than the main protein, such as rennet in cheese, enzymes, flavourings, colourings, or heme in a plant-based burger.&#10;  - Long-established traditional fermented foods such as tempeh, miso and natto.&#10;  - Revenue from ingredients sold to other companies. Count only the finished products sold to consumers, so the same product is not counted twice.&#10;  - Dietary supplements sold as capsules or tablets.&#10;  - Insects and animal feed, as in the rest of the survey.Dollar figures are in constant 2025 US dollars. Reported values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.You do not need to calculate the inflation adjustment precisely. Forecast in constant 2025 dollars and state the annual food-at-home inflation rate you assumed. |
| Years  |  2030 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions | In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries. |

  

1.  ### Blind spots

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration?  |
| Background/ Resolution criteria | None: numerical forecast not required |
| Years  | None: numerical forecast not required |
| Quantiles | None: numerical forecast not required |
| Rationale Instructions | Open-ended: It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’.We’d rather you accurately reflect your thinking here than offer something for the sake of answering the question. |

  
  
  

Thank you for completing this survey.  

# testing output 2  

***Result of \[most recent\] survey on Claude Opus 5.5,*** ***high*** ***effort, incognito mode:***

  

## **US Alternative Protein Forecasting Survey: Responses**

### **Main forecast: US plant-based retail dollar sales (constant 2025 USD)**

|  |  |  |  |
| :-: | :-: | :-: | :-: |
| \*\*Year\*\* | \*\*10th percentile\*\* | \*\*Median\*\* | \*\*90th percentile\*\* |
| 2026 | $7.20B | $7.65B | $8.05B |
| 2030 | $6.20B | $7.35B | $8.90B |
| 2035 | $5.30B | $7.20B | $10.60B |

**Inflation assumption (CPI-U food at home):** 2.5% for 2026, 2.1% for 2027, and 2.5% a year for 2028–2035. The first two are USDA ERS's August 2026 forecasts: food-at-home prices are forecast to increase 2.5 percent in 2026, and 2.1 percent in 2027. The later years use roughly the long-run norm, which ERS puts at the 20-year historical average of 2.6%. I forecast directly in real terms, so this assumption only matters when I translate nominal category trends into 2025 dollars.[ usda](https://www-tx.ers.usda.gov/data-products/food-price-outlook/summary-findings)[supermarketnews](https://www.supermarketnews.com/grocery-categories/grocery-prices-will-continue-to-increase-in-2026-usda)

#### **Starting point**

The 2025 base is $7.9 billion, with plant-based unit sales down 3 percent from 2024 and dollars down 2 percent, both smaller declines than those experienced from 2023 to 2024. The prior year fell faster: dollar sales fell 4% from 2023 to 2024 and 2% from 2024 to 2025. In real terms that is roughly −5% in 2024 and −4.4% in 2025.[ gfi](https://gfi.org/marketresearch/)[foodbusinessnews](https://www.foodbusinessnews.net/articles/30327-plant-based-sales-in-the-us-continue-to-slide)

Two methodology facts matter for resolution. First, GFI states that this study's methodology has changed compared to that used in previous reporting by GFI and advises against comparisons with earlier releases. Second, the "annual" data actually covers 52-week periods ending November 30, 2025, not the calendar year.[ gfigfi](https://gfi.org/marketresearch/)

The categories are diverging sharply. Plant-based meat and seafood fell 10% to $1 billion in 2025, while plant-based milk fell 2% to $2.7 billion. Meanwhile, ready-to-drink beverages were up 12%, yogurt up 7%, protein liquids and powders up 2%, and creamers up 2%, and plant-based bars had the highest dollar growth of any tracked category at 16 percent.[ US alt-meat slump continues, but plant protein gains traction in beverages - GFI +2](https://agfundernews.com/us-alt-meat-slump-continues-but-plant-protein-gains-traction-in-beverages-gfi)

Diagnostically, the decline looks more like shelf loss than demand collapse. Distribution losses appeared to drive sales declines, but dollar and unit velocities were up in both the conventional multi-outlet and natural channels, and six in 10 households bought plant-based foods, with 78 percent buying more than once, similar to the prior year.[ gfigfi](https://gfi.org/marketresearch/)

#### **Evidence from 2026 so far**

Company results through mid-2026 point to decelerating declines, not a turnaround. Beyond Meat's U.S. retail net revenues decreased 9.9% in Q2 2026, driven by weak category demand and reduced points of distribution. That is still an improvement: total net revenue fell 8.2%, an improvement from year-over-year declines of 15.3% in Q1 2026 and 19.7% in Q4 2025.[ sec](https://www.sec.gov/Archives/edgar/data/0001655210/000165521026000053/ex991pressrelease-q22026ea.htm)[theglobeandmail](https://www.theglobeandmail.com/investing/markets/markets-news/Motley%20Fool/3815492/beyond-meat-bynd-q2-2026-earnings-call-transcript/)

Oatly's North America business grew. Q2 was its second consecutive quarter of positive volume growth after declines throughout 2025. But management said the milk-alternative category remains challenged by tight household financial conditions and saturation in protein-fortified products.[ marketbeatmarketbeat](https://www.marketbeat.com/instant-alerts/oatly-group-q2-earnings-call-highlights-2026-07-22/)

#### **Method: category build-up**

I split the 2025 base into four blocks. Meat is $1.0B and milk is $2.7B, both from GFI. I assume the remaining $4.2B is roughly $2.2B in a "growth cluster" (creamer, yogurt, bars, RTD, protein powders and liquids, tofu/tempeh/seitan, baked goods, eggs) and $2.0B in a "declining cluster" (cheese, butter, ice cream, spreads, meals, condiments). This split is my estimate; GFI's category table isn't machine-readable.

For **2026**, I assume these nominal changes:

  - meat −8%, reflecting Beyond's improving but still negative trend;
  - milk −1.5%;
  - growth cluster +5%;
  - declining cluster −4%.

That gives about $7.81B nominal (−1.1%), or about $7.62B in 2025 dollars. I rounded the median to $7.65B.

The 10–90 band (±\~5%) is narrow because half the year is already visible in company data. It is not tighter because GFI has just re-based its methodology and could revise it again.

For **2030**, I assume these real annual rates from 2025:

  - meat −6%;
  - milk −2.5%;
  - growth cluster +3.5%;
  - declining cluster −3%.

That sums to about $7.44B. I trimmed it to $7.35B for "attribution leakage," explained under obstacles below.

For **2035**, I assume the meat decline slows to −3% real, milk −2%, growth cluster +3%, and declining cluster −2.5%. That gives about $7.33B, trimmed to $7.2B. The distribution is deliberately right-skewed; the reasons are in the AI section.

#### **Drivers and obstacles, with attribution**

Simply extrapolating the 2024–25 real decline (\~−4.5%/yr) would give about $6.3B in 2030. My median is about $1.05B higher. This is how I allocate that gap:

|  |  |  |
| :-: | :-: | :-: |
| \*\*Factor\*\* | \*\*Effect on 2030 median vs. extrapolation\*\* | \*\*Evidence and reasoning\*\* |
| Protein/health-positioned formats (bars, RTD, powders, yogurt, tofu) | \\+$0.65B | These are the fastest-growing blocks (cited above). The protein boom rides on GLP-1 adoption and consumers' focus on protein. |
| Plant-based meat bottoming out | \\+$0.35B | Losses come from households leaving and shelf cuts while repeat rates hold. Some formats are growing: shreds, chunks, and strips grew 8 percent in unit sales. A shrinking base means smaller absolute declines. |
| AI-enabled formulation and cost reduction | \\+$0.15B | Faster taste/texture iteration and cheaper inputs; bounded before 2030 (see AI section). |
| Price gap vs. animal products | \\+$0.10B | The gap decreased slightly in 2025, largely driven by increases in conventional beef prices. ERS expects beef and veal prices to increase 5.5% in 2026. I assume this fades as the cattle herd rebuilds later in the decade. |
| MAHA / ultra-processed food (UPF) policy | −$0.10B | HHS and USDA advanced a proposed definition of ultra-processed foods for federal nutrition policy and research. Meat analogs are the most exposed products. The effect is partly offset by evidence that plant-based UPFs such as breads, cereals, and meat alternatives showed beneficial or neutral health effects, which may soften the final definition. |
| GLP-1 volume effects | −$0.05B | Less total food bought, partly offset by more demand for protein-dense products. The net effect is small. |
| Attribution leakage | −$0.05B | Brands dropping "plant-based" claims fall out of SPINS's plant-based-positioned attribute even if their sales continue. |

Some obstacles are already embedded in the base trend rather than listed as adjustments:

  - **Price premium:** most plant-based categories were still priced more than double their conventional counterparts.[ gfi](https://gfi.org/marketresearch/)
  - **Consolidation:** 19 plant-based companies were acquired last year, and several others paused or ceased operations.[ greenqueen](https://www.greenqueen.com.hk/gfi-state-of-the-industry-report-2025-2026-plant-based-sales/)
  - **Distribution losses** and a cost-constrained consumer.

The low tails (2030: $6.2B; 2035: $5.3B) correspond to the current −4%/yr real decline persisting, plus a stricter UPF regime or another methodology change.

#### **How AI factors in**

I separate three channels of AI influence.

**1. R\&D and cost.** This channel is most concrete in fermentation-adjacent inputs. GFI highlights a Pow.Bio/Bühler demonstration that achieved over threefold productivity gains and a 50 percent reduction in costs, enabled by a continuous process and ML-based bioprocess control. However, GFI also notes that data standardization is needed to enable cross-sector developments over siloed in-house solutions.[ gfigfi](https://gfi.org/resource/fermentation-meat-seafood-eggs-dairy-and-ingredients-state-of-the-industry/)

For plant-based products, AI mostly speeds up formulation. It does not fix the binding constraints before 2030: ingredient cost, processing capacity, shelf space and consumer perception. So I treat it as a small positive by 2030 and the main source of the fat right tail by 2035. In that tail, AI-accelerated taste and price parity pushes real growth to about 3%/yr or more.

**2. Retail.** AI-driven assortment and pricing optimization tends to cut slow-moving products. That could accelerate the distribution losses already driving the decline, which makes it a modest headwind.

**3. Macro.** Plant-based buyers skew toward households with incomes over $100K and post-college-educated households. AI-driven labor-market disruption in white-collar work could squeeze exactly this group's discretionary food spend. AI-driven productivity gains could do the opposite. This channel widens both tails rather than moving the median.[ gfi](https://gfi.org/marketresearch/)

### **Open question: cultivated and fermentation-derived sales, 2030 (constant 2025 USD, retail plus foodservice)**

|  |  |  |
| :-: | :-: | :-: |
| \*\*10th\*\* | \*\*Median\*\* | \*\*90th\*\* |
| $90M | $260M | $850M |

I used the same inflation assumption as above.

**Method.** I built the median bottom-up from three segments:

  - **Mycoprotein and biomass-fermented finished products: about $135M.** This covers Quorn US, Meati, Prime Roots, MyForest, Nature's Fynd and similar brands. I estimate the current US total at roughly $80–110M at consumer prices, growing about 5–8% a year.
  - **Products where precision-fermented (PF) protein is the main protein: about $120M.** This covers PF whey protein powders, RTD shakes, milk and ice cream. I estimate the current total at roughly $25–50M.
  - **Cultivated meat, including hybrids: about $3M.**

These current-size estimates are my own and should be read as order-of-magnitude figures. No public tracker exists. Commercial market reports exist, but I treat them as weak evidence; for example, one puts the global fermented mycoprotein market at USD 312.5 million in 2025.[ futuremarketinsights](https://www.futuremarketinsights.com/reports/fermented-mycoprotein-market)

#### **Segment dynamics**

**Cultivated meat is essentially at zero, and the 2030 obstacles are mostly political and financial rather than technical.** As of April 2026, lab-grown meats were not being produced for consumption or sale in the United States. Globally, no cultivated meat product is currently sold at a commercial scale.[ csgmidwest](https://csgmidwest.org/2026/05/04/though-not-yet-on-grocery-shelves-lab-grown-meat-is-focus-of-new-laws-and-legislation/)[maubon](https://cultivated-meat.maubon.com/2026/09/02/cultivated-meat-in-2026-close-to-a-dozen-approvals-none-yet-selling-at-scale-vegconomist-the-vegan-business-magazine/)

The political barriers are growing:

  - Seven states ban sales: Florida, Alabama, Mississippi, Montana, Indiana, Nebraska, and Texas.[ scrunchyliving](https://scrunchyliving.com/blogs/non-toxic-living/lab-grown-meat-at-sprouts-is-it-sold-in-your-state)
  - Louisiana's ban becomes enforceable if the U.S. Supreme Court rules that state bans on cultivated meat are constitutional.[ Substack](https://cultivatedbites.substack.com/p/the-month-in-cultivated-meat-august-523)
  - In the Texas case, the commerce-clause claim survived a motion to dismiss, but the request for a preliminary injunction was denied, meaning the ban remains in effect for now.[ vegconomist](https://vegconomist.com/category/cultivated-cell-cultured-biotechnology/cultivated-meat/)

Retail access is also weak. Sprouts posted that it does not sell cultivated meat, denying a partnership with Mission Barns. The capital environment is poor: UPSIDE Foods withdrew its $50M offer to purchase defunct Believer Meats' North Carolina facility.[ SubstackSubstack](https://cultivatedbites.substack.com/p/the-month-in-cultivated-meat-august-523)

The upside case needs two things by roughly 2028: a favorable federal court ruling, and a large incumbent launching hybrid products with a low cultivated-cell share. Mission Barns already follows a hybrid model, selling meatballs made with a base of pea protein plus cultivated pork fat. That scenario is roughly my 90th percentile, contributing about $50–80M.[ Fast Company](https://www.fastcompany.com/91431270/bay-area-grocery-store-first-sell-cell-cultivated-meat-in-us-limited-time)

**Mycoprotein and biomass fermentation is the most commercially mature segment but financially fragile.** GFI notes that biomass-fermented products are more widely available than precision-fermented ones. Meati, the segment's growth story, was set to sell for just $4M after a financial crisis when a lender repossessed approximately two-thirds of its cash reserves. The brand continues under new ownership: Meati Holdings continued the brand following the October 31, 2025 transfer of all Meati assets.[ State of the Industry: Fermentation for meat, seafood, eggs, dairy, and ingredients +3](https://gfi.org/resource/fermentation-meat-seafood-eggs-dairy-and-ingredients-state-of-the-industry/)

The segment's drivers are its clean-label, high-protein and high-fiber profile, which fits both MAHA and GLP-1 consumer framing. Its obstacles are the same shelf-space and price dynamics hurting plant-based meat.

**Precision fermentation has the most upside in the near term, because a supply shock in conventional whey coincides with falling production costs.** Perfect Day is re-emerging with the whey market in overdrive. Regulation has been moving: 10 precision- and biomass-fermented products obtained a 'no questions' letter from the FDA in 2025. ML-driven cost reductions like Pow.Bio's (cited above) are the most direct AI channel anywhere in this survey.[ greenqueen](https://www.greenqueen.com.hk/perfect-day-precision-fermentation-animal-free-dairy-whey-protein/)[greenqueen](https://www.greenqueen.com.hk/gfi-state-of-the-industry-report-2025-2026-plant-based-sales/)

The obstacles are real:

  - **Funding has roughly halved:** $357 million raised in 2025, down from $632 million in 2024.[ gfi](https://gfi.org/resource/fermentation-meat-seafood-eggs-dairy-and-ingredients-state-of-the-industry/)
  - **Regulatory friction:** the proposed rule would make GRAS notifications mandatory, ending the long-standing voluntary pathway, adding time and cost for new ingredients.[ ajmc](https://www.ajmc.com/view/fda-proposes-gras-rule-advances-ultra-processed-food-definition)
  - **Litigation:** GFI flags IP disputes as a commercialization risk, and Perfect Day faces consumer-group claims that it misleadingly markets ProFerm as 'whey protein' or 'milk-identical'.[ gfi](https://gfi.org/resource/fermentation-meat-seafood-eggs-dairy-and-ingredients-state-of-the-industry/)[foodbev](https://www.foodbev.com/news/perfect-day-sued-over-misleading-marketing-of-animal-free-dairy)

The 90th percentile ($850M) mostly reflects PF whey reaching cost parity in mainstream protein powders and RTDs before 2030. Even a low single-digit share of that market would dwarf today's figures.

**AI in this sector** matters more than for plant-based products because production cost is the core constraint. Its benefits are capped before 2030 by steel-in-the-ground: fermentation capacity takes years to finance and build, and AI does not shorten that much. So AI shifts the upper tail far more than the median.

### **Blind spots**

1.  **Methodology vintage.** GFI re-based its series in 2026 and warns against comparing it with earlier releases. The survey doesn't say whether a later restatement of a resolution year would count, or which vintage wins.
2.  **Measurement of "plant-based."** The series depends on SPINS's "plant-based positioned / vegan-labeled" attributes. Brands are actively repositioning away from "plant-based" toward "protein" or "fiber" claims. Measured sales could therefore fall while consumption of the same products holds steady. The headline number may drift away from the underlying variable of interest: displacement of animal products.
3.  **The deflator conflates price with volume.** Plant-based prices were roughly flat in 2025 while food-at-home CPI rose. Deflating by CPI records price discipline as a real decline. Unit sales, or a category-specific deflator, would separate the two. The CPI also runs on a calendar year, while GFI's data period ends November 30.
4.  **Category composition.** The growth in the definition now comes mainly from bars, RTD drinks, powders and baked goods, which are not meat or dairy replacements in the usual sense. Forecasters may be scored on protein-snack trends rather than alternative-protein adoption.
5.  **Retail only.** Foodservice, where some plant-based and nearly all cultivated activity happens, is excluded from the main question. Retailers that don't report scan data are captured only through projections.
6.  **Unclear boundaries in the fermentation question.** "Main protein" is undefined for blends: PF whey mixed with dairy whey, or mycoprotein-meat blends. Blends with cultivated cells are included explicitly, but mycoprotein-meat blends aren't mentioned. Mushroom fruiting-body products and koji sit ambiguously between fermentation and plant-based.
7.  **Pet food exclusion.** The exclusion is sensible for measurement. But cultivated pet food is emerging as a first commercial scale-up path (for example, cultivated quail broth toppers added to a Singaporean pet food line). Cost reductions there will feed into human-food economics.[ Substack](https://cultivatedbites.substack.com/p/the-month-in-cultivated-meat-august-523)
8.  **AI framing.** Instructing forecasters to give "adequate attention" to AI risks anchoring them toward transformative effects. It also merges three distinct channels (R\&D, retail, macro), which can push in opposite directions within the forecast window.
9.  **Missing supply-side shocks.** Tariffs, ingredient trade measures and energy costs are unmentioned. Oatly, for example, cited the impact of the conflict in the Middle East on energy and logistics costs. Such shocks can move a premium-priced category's real sales as much as demand factors can.[ theplantbasemag](https://www.theplantbasemag.com/news/oatly-boosts-2026-outlook-in-q2-financial-results)

I can put this into a doc if you'd like to share or keep editing it.

  
  

# Final survey 2  

# Introduction

You are participating in a structured forecasting exercise. You will be asked several questions about the future of the alternative protein market in the U.S. For the forecasting questions, you will be given background information and asked to provide a probabilistic forecast and a rationale. 

# Instructions

**General Instructions:**

Accuracy

  - When making forecasts, please give a specific value in the metric stated in the question rather than a range.
  - You should give a specific value for each question, year and quantile (where applicable) rather than a range.

Resources

  - You should use any publicly available resources you can find to help you with making your forecasts, provided you cite them clearly, and how they shaped your thinking.

Alternative proteins definitions

  - Definitions relevant to each forecasting question are given in the background/resolution criteria section of each question.

<!-- end list -->

  - Insects/ insect-derived protein are explicitly excluded from this exercise, as they represent a distinct non-plant based product category.
  - Animal feed applications are excluded. This exercise concerns human food consumption only.

Demand

  - We are looking at demand in terms of US sales, but you should also consider supply side effects that could be captured in these figures.

AI focus

  - Development of AI seems likely to change the landscape of alternative proteins and plant based foods, including fermented and cultivated categories. You should give adequate attention to this when considering the factors affecting your forecasts.

  

**Rationale instructions:**

  - Your rationale should explain why you chose the specific value you gave for your forecasts, we encourage as much detail as required to fully explain your reasoning.

<!-- end list -->

  - In your rationale, you should consider the main factors (drivers and/or obstacles) you believe will affect the trajectory of demand over the given timescales, and you should explain how much of the change in trajectory you assign to each factor. You can draw on any factor you deem relevant to the forecast question, including but not limited to: policy, health or economic factors.
      
      - Drivers = any factors that could be considered catalysts, enablers, or accelerators.
      - Obstacles = any factors that could be considered headwinds, constraints, bottlenecks or impediments.
  - Evidence standard: Ensure every substantive claim you make is evidenced. Where possible, cite the specific source and section from the information provided, or name your source clearly if drawing on outside knowledge. Also explain the method you used to come to your forecasted figure(s).
  - State any assumptions you’ve made clearly in your rationale.

**Quantile forecasts**

  - Where required, you may be asked to give quantile forecasts. For these, please, provide your 10th percentile, 50th percentile (median), and 90th percentile estimates. 
  - This means: you believe there is a 10% chance the true value will be below your 10th percentile estimate, a 50% chance it will be below your median estimate, and a 90% chance it will be below your 90th percentile estimate. Your 10th-to-90th percentile range should reflect an interval you are 80% confident contains the true value. 
  - For each quantile forecast, provide a specific value in the metric stated in the question rather than a range.

# Questions

1.  ## Main forecast

  
  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | What will total US retail dollar sales of plant-based protein be in the following years (in 2025 USD)?  |
| Background/ Resolution criteria | This question will resolve to the figure reported in GFI’s State of the Industry report for U.S. plant-based food retail sales, for the respective resolution year. The report is published in April/May the year after, so the 2026 question will resolve in roughly April–May 2027, and 2030 and 2035 will resolve against the same series. GFI defines plant based food as: Plant-based protein products are food products made from plant- or fungus-derived ingredients that are designed and marketed to directly replace conventional animal products, either as stand-alone products or within recipes. The category includes plant-based alternatives to meat and seafood; eggs; and dairy, including milk, creamer, yogurt, cheese, and ice cream. It also includes traditional plant-protein foods such as tofu, tempeh, and seitan, as well as other plant-based products positioned as protein sources or animal-product replacements, such as protein powders and liquids, ready-to-drink beverages, bars, prepared meals, and baked goods and desserts. Products such as veggie burgers are included even when they don't simulate meat, because they serve as a direct replacement for an animal-based product. Upstream plant protein ingredients, such as protein isolates, concentrates, and textured vegetable protein, form part of the plant-based supply chain but are distinct from the final consumer products they are used to make. The category excludes inherently plant-based whole foods, such as chickpeas and kale, that are not positioned as alternatives to animal products. It also excludes cultivated (cell-based) products, fermentation-derived proteins, and blended products that combine plant-based and conventional animal ingredients. Dollar figures are in constant 2025 US dollars. Reported values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.You do not need to calculate the inflation adjustment precisely. Forecast in constant 2025 dollars and state the annual food-at-home inflation rate you assumed If the GFI data source is no longer reported at the resolution dates, a close analogue will be calculated using the SPINS data directly, or with a panel of industry experts if no alternative is available.  |
| Years  | 2026, 2030, 2035 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions |   |

  

## Open ended questions:

1.  ### Cultivated and fermented categories

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | In 2030, what will be the US sales of each of the following categories (in 2025 USD)? 1\.  Cultivated meat&#10;2.  Fermentation-derived proteins |
| Background/ Resolution criteria | There is currently no direct measure of sales for cultivated and fermented categories. Therefore, for this question we will resolve it with the closest possible available measure at the time if one exists, but for this question we are more interested in your reasoning for your forecast than it’s accuracy, given we don’t currently have an accurate measure. This question is designed to identify the dynamics specific to cultivated and fermentation-derived proteins, not to produce a figure that adds to the main forecast. Some products counted here, such as mycoprotein and other fungus-derived products, may also be counted in the plant-based figure in the main question. That overlap is fine: do not adjust your answer to avoid it. Definitions:Cultivated meat is genuine animal meat, including poultry, seafood, and organ meats, produced by growing animal cells directly in a controlled environment rather than by raising and slaughtering animals. The resulting meat is composed of the same cell types as conventional meat and is designed to replicate its taste, texture, and nutritional profile. Final products may consist entirely of cultivated cells or combine cultivated cells with plant-based ingredients. The category is also referred to as cultured or cell-based meat. Fermentation-derived proteins are alternative proteins produced by cultivating microorganisms, such as fungi, yeast, bacteria, and microalgae, to make food or food ingredients that replace or improve on animal products. GFI identifies three approaches: traditional fermentation, biomass fermentation and precision fermentation. Fermentation-derived ingredients may be sold as stand-alone products or incorporated into plant-based and cultivated products to improve their taste, texture, and nutrition. Include:  - US consumer sales through both retail and foodservice (restaurants, catering and other food-away-from-home outlets).&#10;  - Products where cultivated cells or fermentation-derived ingredients provide the main protein or the main reason to buy, such as cultivated chicken, mycoprotein products, or protein powders made with animal-free whey.&#10;  - Blended products containing cultivated cells, even when most of the product is plant-based.&#10;  - Food and drink products, including protein powders and ready-to-drink shakes.Exclude:  - Products where a fermentation-derived ingredient is a minor input rather than the main protein, such as rennet in cheese, enzymes, flavourings, colourings, or heme in a plant-based burger.&#10;  - Long-established traditional fermented foods such as tempeh, miso and natto.&#10;  - Revenue from ingredients sold to other companies. Count only the finished products sold to consumers, so the same product is not counted twice.&#10;  - Dietary supplements sold as capsules or tablets.&#10;  - Insects and animal feed, as in the rest of the survey.Dollar figures are in constant 2025 US dollars. Reported values are converted using the BLS CPI-U, Food at Home, U.S. city average, not seasonally adjusted (series CUUR0000SAF11), calendar-year annual averages.You do not need to calculate the inflation adjustment precisely. Forecast in constant 2025 dollars and state the annual food-at-home inflation rate you assumed. |
| Years  |  2030 |
| Quantiles | 10, 50, 90 |
| Rationale Instructions | In your rationale please highlight the specific drivers and/or obstacles you believe will affect these specific industries. You may separate your rationale into two parts; one for each category, should you find it helpful.  |

  

1.  ### Blind spots

  

|  |  |
| :-: | :-: |
| \*\*Part\*\* | \*\*Wording\*\* |
| Question | Is there anything about the framing, scope, or wording of this survey that you believe introduced ambiguity, bias, or missed an important consideration?  |
| Background/ Resolution criteria | None: numerical forecast not required |
| Years  | None: numerical forecast not required |
| Quantiles | None: numerical forecast not required |
| Rationale Instructions | Open-ended: It’s fine to give an answer or if you don’t have one, to mark as ‘skipped’.We’d rather you accurately reflect your thinking here than offer something for the sake of answering the question. |

  
  
  

Thank you for completing this survey.
