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

[claim-ledger.json](research/comparative-protein/claim-ledger.json) contains cited passages with `id`, `text`, `sourceIds`, and `humanReview`. A cited passage can combine evidence and the report's interpretation. Pending review remains pending. Its original image-caption passages describe the pre-curation version; the images themselves are omitted and those records are retained for provenance.

The combined [catalog](sources/catalog.json) contains normalized source identities and their original document occurrences. It is an index, not a new empirical dataset. Source access and bibliographic completeness vary by record.

## Integrity records

[File manifest](provenance/file-manifest.json) records sizes and SHA-256 hashes for the shareable repository files. [Import records](provenance/import-records.json) identify the source artifact filename, its content hash, and curation changes for imported report files. Neither record attests to empirical validity. No original private-folder inventory is included.
