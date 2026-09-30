# Methodology: LLM-Based Forecast Elicitation

Source: Google Doc (owner: Anna Bartlett). Last modified 2026-09-30. Exported 2026-09-30 from the shared team Drive folder.

To generate a forecast of future alt-protein demand, a structured elicitation process will be used with multiple large language models (LLMs) acting as forecasters, in place of a human expert panel. This mirrors established expert elicitation methods (e.g. Delphi-style forecasting) but substitutes LLMs for human superforecasters, given budget and time constraints.

**1. Model panel selection.** A panel of 4-6 different frontier models will be used (e.g. Claude, GPT-5, Gemini, and potentially Grok or Perplexity). Using models from different providers is important, as models from the same company may share training data and systematic biases; diversity across providers reduces the risk of correlated blind spots.

**2. Elicitation prompt design.**

A set of fixed prompts will be developed and used identically across all models.

It will include:

- relevant background context, including relevant historical data we've found in desk research
- A set of questions which have been broken down from the main question ("what might the price of the cheapest alt protein be in a) 2030 and b) 2035" / "What percentage of global protein consumption will come from alternative proteins by 2035?" / these are just examples off the top of my head, we'll need to research these properly to cover everything we want to find out, without biasing answers),
- explicit instructions requesting: quantile forecasts and a written rationale of how this forecast was reached for each question, covering key assumptions and what could invalidate them.
- Holding the prompt constant across models ensures the comparison is fair and the results are interpretable.

**3. Initial elicitation round** - APIs

- The forecasting elicitation will be run across multiple models using a simple automated script, rather than manually copy-pasting into each model's chat interface.
- Claude will be used to write this script, given no prior coding experience — the script will be provided ready-to-run, along with a short setup guide.
- This requires creating a separate account with each model provider (e.g. OpenAI, Google, xAI), each of which issues an API key — a short code allowing the script to send prompts and receive responses automatically.
- The script sends the same survey questions and background information to each model in turn, and saves all responses (point estimate, range, probability, rationale) into a single spreadsheet file for analysis.
- Technical requirements: installing Python (a free, standard programming language, taking a few minutes) and running the script via the computer's built-in terminal.
- Estimated one-time setup time: 20-30 minutes; each subsequent elicitation round can then be run in seconds.

Fall back manual method, if using APIs doesn't work: Each model will be queried in a fresh, contextless conversation to avoid bias from prior exchanges. Full responses — point estimate, range, probability, and rationale — will be logged systematically (e.g. in a spreadsheet with columns per model).

**4. Repeat runs for stability (where time allows).** Each model may be queried 2-3 times to assess response stability, since LLMs can produce somewhat different answers to an identical prompt across separate runs. The degree of variation observed will be reported as part of the study's limitations.

**5. Second elicitation round (Delphi-style).** Following the first round, anonymised rationales from all models will be compiled and fed back to each model, along with a request to state whether their estimate changes in light of the other reasoning presented, and why. This step is designed to surface genuine points of disagreement (cruxes) rather than relying solely on first-pass, independent estimates.

**6. Quantitative aggregation.** Final estimates across all models will be aggregated using the median (chosen over the mean for robustness to outliers), alongside the full range of estimates. This produces a headline forecast range, for example: "alt-protein market share of X-Y% by 2035 (median Z%)."

**7. Qualitative synthesis of rationales.** Written rationales will be reviewed and coded for recurring themes — the specific factors models cite as driving their estimates (e.g. price parity timelines, cultural acceptance, regulatory environment). These recurring factors will form the basis of a "cruxes to monitor" section, identifying the specific uncertainties most likely to shift the forecast over time.

**8. Documentation and limitations.** The full protocol (prompt wording, models used, number of runs, aggregation method) will be documented for transparency and reproducibility. Limitations will be stated explicitly, including that LLM forecasts have not been validated against real-world calibration in the way human superforecaster track records have, and that models may share correlated blind spots even when drawn from different providers.

- Future research could do this process more scientifically by varying the wording of the questions asked in multiple rounds of each model, without changing the meaning of the question, to try to limit models' bias.
