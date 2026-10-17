# T7 integration notes

Added T3's drift-overlap and Pakistan multiplier sentences to REPORT.template.md and regenerated REPORT.md with build_report.py. Changed the scenario row count from 104 to 127 in inventory_counts.csv and both claims.csv files. Updated data/claim-index.csv to 127 and added the three T3 claims.

Kept joint-report in place. Import records support project-authored drafts without an external source, preserving authorship and links without moving files. Corrected 10 descriptions: the coordinator applied T1 on 17 October 2026.

Chromium aborted inside the sandbox (SIGABRT; kill EPERM), so the coordinator regenerated report.pdf and report.docx outside it. Updated supervisor-export-text and the export registry to bind REPORT.md and both exports. Both extracted bodies match the 154,413-character canonical body.

Kept logs/report-export-parity.json with its import record for the coordinator's commit. No .gitignore change.

Commands: node tools/build-library.mjs twice; node tools/verify.mjs; supplied run_tests.py for test_altprotein_proxy.py; all eight node tools/test-*-checks.mjs.

Moderator: check exact scope, claim agreement and export bindings. Retrospective: stale metadata caused failure; reconcile provenance, indexes and handoff notes together.
