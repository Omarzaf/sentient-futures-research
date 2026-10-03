# Alternative meat survey data

Prepared 30 September 2026. AI-assisted extraction; human verification pending. The files preserve source caveats and internal inconsistencies rather than resolving them into one acceptance estimate.

## Scope

This package collects the reported figures, sample descriptors, qualitative findings and source references from nine studies and reports on Muslim-country and Southeast Asian surveys, all cited in an earlier AI-assisted draft. It is a structured extraction of published results, not individual respondent records and not every table from each paper.

## Files

| File | Contents |
| --- | --- |
| [index.html](index.html) | Open in a browser for links to the original reports, papers and supplements |
| [findings.csv](findings.csv) | The 29 findings, one reported result or descriptor per row |
| [studies.csv](studies.csv) | The nine studies: citations, samples, methods, access and caveats |
| [survey-data.json](survey-data.json) | Structured data and source metadata; the two CSVs are views of it |

An earlier version also carried the two sheets of the original Excel workbook as CSV exports. They held the same rows as `findings.csv` and `studies.csv` under different column names and were removed on 3 October 2026.

## Access limit

Original publisher PDFs are not included. Direct publisher downloads were blocked by the workspace's network. Read and download links are retained for all nine sources. Some full articles may require institutional access. No respondent-level dataset was downloaded or fabricated. Where an author-request route was verified, it is listed. No author has been contacted.

## Data definitions

- Each findings row is one reported result or descriptor. Study IDs join to the studies table.
- Value is numeric. `unit=proportion` means 0.31 represents 31%. `unit=respondents` means a count. Qualitative rows have a blank value.
- Qualifier must be retained: `>` denotes a lower bound; `Approximate` denotes a figure rounded in the earlier draft; disputed values retain the source inconsistency.
- Sample n describes the study, country or subgroup sample. It is not necessarily the exact item-response denominator. Saudi sex-specific figures use men n=758 and women n=1,450.
- Numerator is supplied only when directly checked. Blank means unreported or not extracted, not zero.
- Publication or report year and fieldwork dates are separate. Unverified dates are explicitly marked.
- Self-reported consumption, awareness, preference, willingness, price scenarios and sample composition are different measures. Do not pool their percentages or add sample counts across overlapping study summaries.

## Source issues retained

- **S01:** Correct DOI is 10.1111/1750-3841.17559. The earlier 1754-3841 form was a typo. The earlier draft stated approximately 41% willing to try; the primary abstract says more than 40%.
- **S02:** Preference shares concern UAE nationals, not all UAE residents. The sample is 80.9% women and 75.9% ages 18–24.
- **S03:** 649 Pakistan and 210 Indonesia are sample sizes. The paper's models pool multiple countries; no national adoption rates were supplied. First online 2023, journal issue 2024.
- **S05:** This study concerns edible insects; it does not establish consumption of plant-based or cultivated meat.
- **S06:** The abstract states 44.1% acceptance. Table 3 reports 50 of 102 (49.0% as printed). Table 1 reports 45 of 102 (44.1%) for awareness. All three are retained and labelled.
- **S07:** Country samples are not Muslim-only samples. Broad plant-food measures can include milk, so those figures were not relabelled as meat consumption.
- **S08:** Results are regional. More than 80% willingness refers to a hypothetical price 20% below conventional meat. The exact frequency threshold for regular consumption was not verified.
- **S09:** Acceptance ranking and associated factors do not provide a consumption prevalence estimate.

## Provenance

Each record has a study ID and source location. The studies table gives the DOI and original or institutional URLs. Results were checked against accessible primary pages, reports, abstracts or tables. Links are supplied rather than reproducing full papers.

`node tools/verify.mjs` checks that both CSVs match the JSON exactly, that IDs run S01–S09 and R01–R29, and that proportions, numerators and units agree.
