# Supervisor data snapshot

These UTF-8 CSVs contain source-bound observations, derived calculations and explicitly missing values used by the edition and report. Human verification pending.

- `sources.csv` preserves stable identities, public URLs, tiers, dates, access limits and source rights notes. Source inclusion does not establish claim validity or current accessibility.
- `claims.csv` records exact dataset filters, arithmetic, rounding and displayed values. It is identical to the package-level ledger used by the report.
- `edition_claims.csv` excludes report-only news-framing material. The HTML uses only that restricted ledger.
- `dataset-manifest.json` records each table's source columns, derivation status and permitted audience.
- `reader-links.json` records verified alternate reader links while the original registry URLs remain unchanged. `link-status.json` records inactive access routes; unsuccessful historical URLs are retained as metadata, not represented as working links.
- `MANIFEST.csv` is the original raw-input inventory. It contains no raw response bodies. Its hashes identify saved bytes, including separately labelled failures and derived extracts; they do not imply all URLs can now reproduce those bytes.

The public source register preserves the original bibliographic fields. A small set of source notes was projected to remove local path or ingestion-key references. `source-metadata-projections.csv` records original and public field hashes. Core processed tables preserve their source strings; derived adapters add explicit definitions rather than substituting inferred values.

The consumer findings table preserves all extracted findings and their source conflicts. Only rows marked `admitted_for_synthesis=true` appear in the outcome display. A verified sample size does not independently verify every study percentage. Fieldwork, recruitment, denominator and source-locator limitations remain separate fields.

News-framing aggregates are included only to reproduce the report's limitations appendix. They describe bounded AI annotation agreement, not sentiment prevalence, public opinion, accuracy or human consensus. The edition does not expose those tables or claims.

See [reproduction instructions](../REPRODUCE.md) and the report's methods and limitations before using these files.
