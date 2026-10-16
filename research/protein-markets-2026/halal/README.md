# India–Pakistan halal original-source review

AI-assisted working draft, 15 October 2026. The author checked and accepted the existing Urdu/Arabic translations and religious interpretations. [The review receipt](author-review.json) records the statement, exact edition hashes and scope. Regulatory/technical claims and missing originals remain open. No market estimates or projections were computed.

- [Chapter draft](CHAPTER-DRAFT.md): bounded country comparison and AI role.
- [Source register](source-register.json): 17 captured originals/indexes; 2 unretrieved originals held. Language witnesses/indexes are not independent authorities.
- [Claim ledger](claims.json): 9 bounded claims with original short passages and exact locators. Its pre-review statuses are preserved; the subsequent author acceptance covers the 6 linguistic/religious claims in the review receipt.
- [Signposts](signposts.json): 4 proposed certification questions plus 2 AI monitoring definitions. Not approved/preregistered and not product approvals.
- [Gaps](GAPS.md): missing Indian cultivated ruling/Arabic original, CII ruling, domestic product certificates and remaining review scope.

Original HTML/PDFs, inspected page images, extraction files, retrieval receipts and `capture-manifest.json` are retained only in the private workspace directory `OUTPUTS/Deep Research 2026-10/halal/`. No licence for redistribution of full captures was established. The register records SHA256, byte count, URL and UTC capture time. The 12.5 MB Urdu original remains private; no raw file is copied into this source directory.

From `sentient-futures-research/`, run the read-only local checks:

```bash
node --check research/protein-markets-2026/halal/capture-originals.mjs
node --check research/protein-markets-2026/halal/assemble-evidence.mjs
node --check research/protein-markets-2026/halal/verify-evidence.mjs
node research/protein-markets-2026/halal/verify-evidence.mjs
```

The verifier requires the private packet and checks source/inspection hashes, source-to-claim links, short excerpt bounds, Banuri original passage matches, held-source retry caps and draft-signpost status. It validates the author review receipt against current edition hashes; changing reviewed text invalidates that acceptance. It does not independently certify translation or scholarly correctness. It writes no files. Run `node --test research/protein-markets-2026/halal/test-review-state.mjs` to check review-scope and stale-version rejection.

`capture-originals.mjs` and the three retrieval plans document the authorized public GET route. `assemble-evidence.mjs` constructs the original ledger from those receipts. Both use exclusive creation and preserve existing captures; they are not routine validation commands. Do not rerun to overwrite a historical snapshot. Deoband's two targets reached three failed attempts and must not be retried within this task.

Agent-Reach's local CLIs were unavailable; native public search/read and public GET/curl supplied the fallback. No account, registration, correspondence, payment, form submission or publication occurred. This packet contains no independent author policy codes and no kappa result.
