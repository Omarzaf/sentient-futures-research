# Data dictionary

## Country protein supply

Location: [protein-data.csv](research/comparative-protein/protein-data.csv). There are 13 selected country cases: 12 with comparable values and one missing-data case, Singapore. Pakistan is not included. Blank values mean unavailable, never zero.

| Field | Meaning |
| --- | --- |
| `country` | Source country label |
| `group` | Author's descriptive comparison grouping; not a measured variable |
| `total2010`, `total2023` | Total protein supply in grams per person per day |
| `animal2010`, `animal2023` | Animal-origin protein supply in the same unit |
| `plant2023` | Derived total minus animal-origin supply, rounded to one decimal |
| `animalShare2023` | Derived animal-origin share of total supply, percent, rounded to one decimal |
| `printedPage`, `pdfPage` | Original printed page and PDF page locator |
| `source` | Original report source ID, `C01` |

These estimates describe food available for consumption, not individual intake, demand preferences, nutritional adequacy, or waste. Country selection is purposive. Regional rows were excluded in the original report because of a reported label discrepancy; no replacement region labels were inferred.

## Figure inputs

Location: [figure-data.json](research/comparative-protein/figure-data.json).

`provenance` records the source table, units, derivations, selection rules, and limits. `countries` contains the CSV observations plus intermediate years, retained source-table text (`rawLine`), and approximate coordinates. `hubs` contains 14 documented capability locations. Hub fields include `label`, `country`, `city`, coordinates, `capability`, `sourceIds`, `evidenceType`, `limitation`, and `mapCategory`.

Coordinates are approximate orientation aids. A hub record does not establish a workforce count, economic impact, present hiring activity, or a measured cluster boundary. Missing or absent numbers are not imputed.

## Sources and claims

Original source registers use collection-specific `id` values. They contain titles, authors or issuers, dates, URLs/DOIs, source types, access notes, limitations, and other research annotations. The AI/protein register's `number` is the displayed reference number; the comparative register uses `referenceNumber`.

The India–Pakistan review register, [source-register.json](research/india-pakistan/source-register.json), holds 20
records from the 14 September 2026 review. Records were collected in three batches with differing field names and are
normalized here to one schema; no record content was dropped in that normalization.

| Field | Meaning |
| --- | --- |
| `id` | Review-specific record identifier |
| `title`, `authors`, `date`, `year`, `doi`, `url` | Bibliographic identity; `url` is the primary public location |
| `additional_urls` | Further pages, full-text mirrors, and official landing pages for the same source |
| `type` | Source category as recorded in the review |
| `country` | Country the record was collected for, where the batch recorded one |
| `citation` | Journal, volume, issue, article, publisher, or document number, where applicable |
| `access` | What was actually opened and, for three records, the page-level check performed |
| `locations_checked` | Pages, tables, figures, or sections inspected |
| `sample` | Study sample or measure, for records where the batch recorded one |
| `findings` | Statements attributed to the source |
| `limitations` | What the source does not establish |
| `funding` | Funding or conflict-of-interest statements found, or their absence |
| `excerpt` | Short verbatim phrase retained for locating the claim |
| `use_in_synthesis` | How the review intended to use the record |
| `review_batch` | Originating batch file |
| `accessed`, `human_verification` | Access date and review state; all records remain `Pending` |

Some records are supplementary and are not cited in the brief. A populated `access` field records that a page was
opened during AI-assisted review, not that a human has verified the claim.

[claim-ledger.json](research/comparative-protein/claim-ledger.json) contains cited passages with `id`, `text`, `sourceIds`, and `humanReview`. A cited passage can combine evidence and the report's interpretation. Pending review remains pending. Its original image-caption passages describe the pre-curation version; the images themselves are omitted and those records are retained for provenance.

The combined [catalog](sources/catalog.json) contains normalized source identities and their original document occurrences. It is an index, not a new empirical dataset. Source access and bibliographic completeness vary by record.

## Alternative meat survey data

Location: [research/protein-survey-data](research/protein-survey-data/README.md). This package contains a structured extraction from nine published studies or reports and 29 retained findings. It is not respondent-level data, not a complete table export from every source, and not a pooled acceptance estimate.

`survey-data.json` is the canonical structured version. `sources` holds the nine study records, including `id`, title, authors, year, geography, sample size, method, DOI or URLs, access status, respondent-level data status, notes and findings. `observations` holds the 29 extracted rows and joins to `sources` through `source_id`.

`findings.csv` and `studies.csv` are CSV views of the JSON. The checker verifies that the JSON and both CSVs agree.

For findings, `unit=proportion` stores proportions as decimals, so `0.31` means 31 percent. `unit=respondents` stores a count. `unit=qualitative` has a blank numeric value. Blank `numerator` means unreported or not extracted, never zero. `measurement_type` distinguishes willingness, preference, awareness, self-reported consumption, sample composition, sample size, association and qualitative records; these measures must not be pooled.

## Halal conditionality workstream

Location: [research/halal-cultivated](research/halal-cultivated/README.md). [datapackage.json](research/halal-cultivated/datapackage.json) defines every field, type and allowed value for the eleven CSV registers of the 30 September discovery pass, now in [archive/discovery-pass](research/halal-cultivated/archive/README.md), in the Frictionless Data format, so it can also be validated with `frictionless validate`. It is the only definition; this section does not repeat it.

`market-records.csv` carries the demand forecast's keys (`category`, `geo`, `year`, `metric`, `price_basis`, `channel`, `quantile`, `source_id`) unrenamed, then the halal fields from plan section 4.3. Values are in constant 2025 USD; volumes are carcass-weight equivalent unless `unit` says retail weight. Volume and value shares use different units and are never mixed. Food-balance supply, household survey quantities, sales, stated intentions and projections are distinguished by `evidence_type` and never combined.

Blank cells are missing, never zero. A registry search that found nothing is `none_found` with its date, not a prohibition. Five registers hold provisional rows and six are header-only; Phase One, the October continuation and the working paper hold the later evidence in their own JSON registers.

## Integrity records

[File manifest](provenance/file-manifest.json) records sizes and SHA-256 hashes for the shareable file tree. [Import records](provenance/import-records.json) identify the source artifact filename, its content hash, and curation changes for imported report files. Neither record attests to empirical validity or Git-history cleanliness. No original private-folder inventory is included.
