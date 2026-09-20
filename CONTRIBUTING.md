# Giving feedback

The most useful feedback identifies a specific passage, source, definition, or calculation.

For a source correction, include the report path, its original source ID, the exact claim, and the relevant page or section in the original publication. Distinguish a bibliographic correction from a change to the interpretation. Do not mark a source as human-verified until the cited claim has actually been checked.

For the India–Pakistan brief, cite the section heading and the footnote number, and give the record `id` from its `source-register.json` where the correction concerns a source. For the comparative report, use its `claim-ledger.json` passage IDs. For the AI/protein literature review, use the numbered references and the source-register IDs. For orientation notes, include the heading and linked source.

Suggest changes on a feature branch or in a review comment after repository access is arranged. Keep private correspondence, participant information, restricted datasets, credentials, and downloaded third-party publications out of commits and issues. Do not add unpublished team work without its author's agreement.

Run `node tools/build-library.mjs` followed by `node tools/verify.mjs` after changing library inputs. These checks validate packaging and consistency; record substantive human review separately. Proposed new conclusions should state the evidence, uncertainty, and what would change the interpretation.
