# Reproduce the supervisor edition

Human verification pending. This package preserves the reviewed processed-data snapshot and its numerical bindings. It does not redistribute the complete raw-download collection, respondent records, article bodies or private working documents.

From the repository root, with Python 3.12 or later:

```sh
python3 research/india-pakistan/edition/build.py
python3 research/india-pakistan/tools/build_report.py
python3 tools/verify_edition.py --only C1,C2,C3,C4,C5
python3 tools/probes.py --output /tmp/supervisor-probes.json
```

The first command rebuilds the self-contained HTML from the published CSVs, local geometry and bundled D3. The second reconstructs the Markdown from the authored template and exact claims. The public diagnostic check recomputes all claims, verifies numeric prose and chart/table selections, joins sources and checks chapter/package coverage. The corruption run uses synthetic scratch files and mocked services; it tests the checker and does not certify live research or live links.

The complete local release verification additionally checks current browser images, every PDF page, original review evidence, live-link receipts, export regeneration, privacy, the library build and the fresh-review handover. Those operational records contain private machine paths and are retained locally. The public configuration deliberately supports C1–C5 only. It cannot produce a misleading full-release pass when those private receipts are absent.

For the checker regression suite, use an existing environment with pytest. Some integration cases also require Node, Pandoc, Poppler and a configured Playwright/Chromium installation; missing dependencies remain explicit. No package installer runs as part of these commands.

```sh
python3 -m pytest research/india-pakistan/tests/test_verify_edition.py
node tools/build-library.mjs
node tools/verify.mjs
```

PDF and Word are authored report exports. Their exact file hashes, actual extracted-body text and Markdown bindings are recorded in the [export registry](../../provenance/supervisor-reviewed-exports.json). The Node library check validates those bindings and exact text parity; the local C12 check separately regenerates both formats. This distinction matters: a matching file hash proves identity, not scholarly approval.

To recreate document exports in a prepared environment, generate the Word style reference with `tools/make_report_reference.py` within this package and configure `exports.reference_doc`, `exports.playwright_module` and `exports.chromium_executable` locally. Preserve the included report CSS, page-number setting and document-body parity check. The reference document is generated from the installed Pandoc template rather than redistributed as another binary exception.

The [raw manifest](data/MANIFEST.csv) records source URLs, observed download dates and hashes. A URL can point to a mutable endpoint, an access-denied response, a source document from which a text extract was derived, or a listing rather than downloadable data. The selection-only fetch helper documents these distinctions and checks exact bytes. Hash mismatch is not permission to overwrite the accepted source or to invent a replacement finding. Raw material remains outside this public package.

The [pipeline package](pipeline/README.md) preserves the selected dashboard code and tests, with its raw-dependent and publicly reproducible scopes stated separately. The complete dietary-protein total for Pakistan remains missing; the partial conversions cannot be treated as intake, adequacy or a country ranking. Forecasts concern protein supply, not adoption. Consumer study outcomes retain their own samples and questions and must not be pooled.

Boundary data are distributed by geoBoundaries under CC BY 4.0; [country-specific original licensing](edition/geo/provenance.json) is retained separately. FAOSTAT observations retain FAO attribution and CC BY 4.0 terms. D3's [ISC permission notice](edition/lib/D3-LICENSE.txt) accompanies its bundled source. The research text and code have no blanket third-party reuse licence; see [rights and reuse](../../RIGHTS-AND-REUSE.md).
