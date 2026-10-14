# Dashboard pipeline: public code and aggregate checks

This directory preserves 58 authored Python scripts from the dashboard research
pipeline. The runnable public edition uses the processed tables in `../data/`.
The report and edition can be reviewed without downloading the historical inputs.

The default test suite checks arithmetic, missingness, source registration, row
tiers, released benchmark calculations, method-range endpoints and a bounded input
fetcher. It does **not** claim to recreate the report from raw documents or to
independently repeat scholarly source review. Pakistan complete dietary intake
remains missing; physical-food subtotals remain conditional diagnostics. India
consumer units remain an energy scale, separate from adult protein requirements.

## Run the offline public checks

Use Python 3.11 or later in an activated environment with the versions in
`requirements-dev.txt`. No installation or network call is performed by these
commands. From this directory:

```sh
python -m pytest -c pytest.ini tests -q
python -m compileall -q scripts
```

The tests reject actual socket creation. Three original suites run unchanged;
the additional tests exercise released aggregates and isolated mock downloads.
The six files in `fixtures/supervisor_model/` are aggregate scenario tables,
coverage, source metadata and a historical checksum receipt. The tests bind the
four shipped output tables to that receipt. They do not certify unshipped inputs
or the omitted component ledger.

## Historical scripts and tests

All 58 non-sentiment scripts are retained byte-for-byte for inspection, including
their source-hash guards and their historical acquisition routines. Nine original
main test modules are preserved in `historical_tests/`. Several need the original
local folder layout, documents, spreadsheet workbooks, model intermediates and
microdata. They are deliberately outside the default test discovery path. The two
tests beneath `scripts/` have the same historical-input boundary. Do not invoke
the entire script collection or historical suite expecting a self-contained
rebuild.

The old acquisition routines are preserved source code, not the recommended public
download interface. Some use batch requests. No acquisition script runs during
normal edition generation or these public tests. Eight authored R helpers invoked by historical Python wrappers are also retained
verbatim and checked for syntax only. Executing them requires an appropriate R
environment with data.table and separately obtained source microdata. No R model
was rerun when preparing this projection.

No source document, article capture, household record, downloaded binary or
sentiment alias archive is shipped here. The 23 MB detailed component ledger and
other unnecessary intermediate exports remain local. Short factual parameters,
source locators and analyst-authored aggregate calculations support the tests;
they do not confer rights over the underlying publications. The repository's
rights policy governs reuse. Human scholarly verification remains pending.

## Explicit input retrieval

`../data/MANIFEST.csv` records 1,974 historical artifacts. A provenance URL is not
always the byte-download URL: many entries are locally generated text extractions,
page images, request receipts, failed requests or user-provided extracts. The
manifest is metadata, not a promise that every artifact can be downloaded again.

Inspect one exact source selection offline first:

```sh
python ../data/fetch_raw.py --source usda_gain_pakistan_pk2026_0004 \
  --cache-dir /tmp/research-input-cache --list
```

To retrieve a selected original candidate, specify its exact `--file` identity
from the manifest and omit `--list`. An exact `--source` selection is also
supported and may select multiple records. At least one selector and an explicit
cache directory outside this checkout are required. There is no default bulk
download. Generated artifacts and ambiguous records are reported without fetching.

The utility performs GET only, disables redirects/proxies, rejects local network
destinations and uses bounded size/time settings. It promotes a response only when
its SHA-256 matches the historical manifest. Existing cache files are never
overwritten; mismatches and retrieval failures are recorded as metadata in the
cache's `fetch-receipts.jsonl`. A changed source must be reviewed as a new evidence
identity. Derivatives must be recreated with the relevant historical extraction
steps and independently checked; downloading a parent PDF does not reproduce a
text-extraction hash. Historical hashes can legitimately become unavailable.

`PROJECTION.json` binds the exact authored-code and aggregate fixture copies.
The detailed local selection receipt separately records every excluded original
path and its reason. No raw-source retrieval was performed while preparing this
projection.
