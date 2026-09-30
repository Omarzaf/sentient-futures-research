# Compute finance request form

Source: Google Doc (owner: Anna Bartlett). Last modified 2026-09-04. Exported 2026-09-29 from the shared team Drive folder. Contains the team's compute and API funding request to the Sentient Futures Project Incubator (approved for $300 and 1 Claude Standard seat, per Meeting_notes 15.09.2026).

**Title of project(s)**

How could AI reshape the food system transition over the next 10–20 years, and where should the talent and resources be directed today to achieve the best possible outcome?

**Brief description of project(s)**

This project addresses one strand of a wider research effort exploring how AI could reshape the food system transition over the next 10-20 years, and where talent and resources should be directed today to achieve the best possible outcome. Within that broader question, this section focuses specifically on adoption and displacement dynamics in the alternative protein space.

The specific research question is: what will future demand for alternative proteins look like, and what are the key limiting or accelerating factors — including the role of AI — in that trajectory? This is examined through a combination of desk research (synthesizing existing market projections and identifying the drivers and historical analogues relevant to alt-protein adoption) and a structured forecasting exercise using multiple large language models as a substitute for a human expert panel, given the constraints of a short, low-budget project. The project closes with a short, explicitly caveated estimate of the plausible range of implied effects on animal protein demand, intended as a starting hypothesis rather than a definitive answer.

This work is designed to complement the other strands of the wider project — including analysis of policy, resource, and talent allocation, and of Global North/South and post-transition dynamics — by providing an evidence-based forecast of the pace and shape of alt-protein adoption that those other strands can draw on.

**Requested support**

- ✅ API/GPU access
- ✅ Claude subscription via Sentient Futures
- Other (please indicate)

**Claude subscription**

Standard: annarbartlett@gmail.com

Number of Claude Standard seats requested: 1
Number of Claude Premium seats requested: 0

Justification: The project involves developing a Python script to automate a structured forecasting elicitation process across multiple LLM APIs. As I have no prior coding experience, Claude will be used to write and lightly debug this script, following a documented, step-by-step approach.

This is a light, occasional coding task — a single script of modest length, used intermittently rather than continuously, with no large codebase, long-running sessions, or repeated heavy iteration involved, so a Standard seat is the appropriate and proportionate request.

**Initial reimbursement requested: $300**

Justification: API Budget Request ($300)

The project's methodology requires running a structured forecasting elicitation across a panel of 6 different LLM providers, in two rounds, with stability checks to assess response consistency. This breaks down as follows:

- Round 1 elicitation: 6 models × 1 call = 6 calls
- Stability checks (2-3 repeats per model): 6 × 3 = 18 calls
- Round 2 Delphi-style elicitation: 6 × 1 = 6 calls
- Prompt piloting and refinement (testing on 1-2 models before finalizing wording): ~15-20 calls
- Subtotal: ~45-50 calls

Each call involves a substantial amount of context (background information and survey questions, roughly 1,000-2,000 words) and returns a written rationale, rather than a brief one-line response. Based on typical frontier-model API pricing, a realistic cost per call is $0.05-$0.50, with more expensive reasoning-focused models at the higher end. This gives a raw cost estimate of roughly $2.50-$25 at the low end, rising to $50-100 if relying more heavily on pricier models throughout.

The $300 request exceeds this raw estimate by a factor of 3-6x to account for practical risks: six separate provider accounts and billing setups increase the likelihood of needing to retry or re-run calls due to formatting errors, invalid API keys, or script issues on first attempts.

The typical limit of requests we consider is $900 USD. Please provide brief justification for requests over this amount. (No entry.)

**Intermediary outcomes for the midpoint check-in**

By the midpoint of the project (approximately Week 5), the following will be ready to show:

1. Completed desk research synthesis — a driver map covering the key factors likely to accelerate or limit alt-protein adoption (including AI-related factors), historical substitution analogues with supporting data (e.g. margarine/butter, plant milk/dairy), and a comparison of existing conventional animal protein market projections against existing alt-protein demand projections, explicitly noting whether alt-protein competition is already factored into the former.
2. A finalized, working LLM elicitation protocol — the survey questions and background information pack to be sent to each model, along with the automated script (built using Claude) that sends prompts to the full 6-model panel and logs responses systematically. This will have been piloted and refined on at least 1-2 models prior to the full run.
3. Initial round-1 forecast results — quantitative estimates, ranges, and written rationales collected from all 6 models in the panel, providing the first direct evidence of the funded compute/API access being put to use.

Should we identify a significant, unexplained lack of progress by midpoint check-in, we reserve the right to terminate your eligibility for further reimbursements. In this case, you'll still be reimbursed for documented costs up until this point.

We understand the project may evolve between now and the midpoint check-in and encourage proactive communication with the Project Incubator team. You're always welcome to reach out to us if you have questions or concerns.
