# Policy review packet

This directory holds the 20-instrument register, single-category codebook, frozen agent coding and integrity receipts. Source PDFs and the blank author packet remain in the private workspace evidence directory. Independent author coding and Cohen's kappa remain pending.

Run commands below from the research repository root.

## Check the existing packet

    node research/protein-markets-2026/policy/verify-review.mjs

The default check prints its current result and does not write a file. The existing VERIFICATION.json is a historical receipt and is preserved.

To save a new receipt, supply a new path inside the private policy-review directory:

    node research/protein-markets-2026/policy/verify-review.mjs \
      --output "../OUTPUTS/Deep Research 2026-10/policy-review/verification-template-repair-2026-10-15.json"

An existing receipt is never overwritten. A path outside the private policy-review directory is rejected.

## Refresh the private blank HTML form

    node research/protein-markets-2026/policy/prepare-review.mjs --refresh-author-form

This checks the frozen register, codebook and agent hashes, then refreshes only ../OUTPUTS/Deep Research 2026-10/policy-review/author-form.html. It preserves the frozen files, historical verification receipt, blank author JSON and private codebook copy. Run it before author coding begins; preserve any author response files separately.

Open the private author-form.html in a browser. It has 20 blank responses and links to the captured PDFs and a private copy of the codebook. The author can download a draft or final JSON file. “Cannot classify from this source” records a null label and a reason rather than forcing a category; fewer than 20 valid pairs leave the requested criterion unmet. A separate disclosure choice lets someone who has seen agent answers save a nonblind round without falsely attesting independence. No author answers are supplied by the agent.

[Plain-language classification guidance](HOW-TO-CLASSIFY.md) explains the eight functions without revealing answers to sampled instruments. A category describes the instrument's mechanism, not its strength or effectiveness.

The source author-form.template.html uses a valid JSON placeholder object and links to the repository's codebook.json. Preparation replaces that entire placeholder with the blank packet and rewrites the generated private form's codebook link to codebook.author-copy.json. Private author material must not be copied into this source directory.

## First preparation and source retrieval

The prepare-review.mjs command without arguments is a one-time initial freeze operation. It refuses to replace an existing frozen review. It is not a routine rebuild command.

The capture-sources.mjs helper and its three checked retrieval plans document the source-capture process. They make outbound public-source requests and are separate from the read-only packet check. Historical failed-source receipts, official mirror retrievals and the fallback-count correction remain in the private raw evidence directory.

## Evidence limits

The frozen 20 source captures include the official BioE3 summary brochure used at first-round freeze. A later authorized search recovered the full policy from the current official DBT host and a BIRAC programme-access companion. These are supplemental evidence, not replacements for the frozen source hashes or extra first-round sampled instruments. A new matched coding edition would need separately preserved materials and codes. Some notification days, commencement notifications and amendment currency remain unresolved. Selected scan pages support primary-function coding; this is not a comprehensive legal-currency audit.

Keep the frozen agent responses separate from the author packet until the author finalises all 20 independent codes. Preserve both first-round files. No agreement result exists until those author responses are supplied.

[Disclosure record](disclosure-record.json): during a later assistant inspection, a tool output included the existing label map in the preparation source. Whether the author viewed it is unknown. Clean blind status cannot be certified after that disclosure. It must accompany subsequent coding and agreement reporting; a viewed round cannot satisfy independent blind comparison. The frozen files remain unchanged, and there are no author responses or agreement values.

