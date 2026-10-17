"""Rebuild the baseline completion edition and its explicit research limits offline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from baseline_acceptance import evaluate_baselines
from rebuild import build_readiness
from render_completion_report import render_report

__all__ = ["complete_research"]
PACKAGE = Path(__file__).resolve().parent
EDITION = "baseline-completion-20261016"


def read_json(path: Path) -> dict:
    """Read an explicitly named local evidence file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict | list) -> None:
    """Write deterministic machine-readable research evidence."""
    path.write_text(
        json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def sha(path: Path) -> str:
    """Bind exact input or producer bytes without inferring correctness."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_baseline(script: str, arguments: list[str]) -> None:
    """Distinguish a genuine failed comparator from an execution failure."""
    result = subprocess.run(
        [sys.executable, str(PACKAGE / script), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise RuntimeError(f"{script} failed: {result.stderr}")


def complete_research(data_dir: Path, hces_dir: Path, output_dir: Path) -> dict:
    """Execute both comparators and rebuild every number in the completion report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    inputs = data_dir / EDITION
    source_tables = build_readiness(data_dir, output_dir / "source-tables", hces_dir)
    if source_tables["integrity_failures"]:
        raise ValueError("Existing raw-source identities failed")
    india_dir = output_dir / "india"
    pakistan_dir = output_dir / "pakistan"
    run_baseline(
        "reproduce_india_baseline.py",
        [
            "--candidate-dir",
            str(hces_dir),
            "--receipt",
            str(data_dir / "hces-candidate-receipt.json"),
            "--report",
            str(data_dir / "raw/mospi-report594.pdf"),
            "--cpi-data",
            str(inputs / "india/cpi-data.json"),
            "--output-dir",
            str(india_dir),
        ],
    )
    run_baseline(
        "pakistan_reconciliation.py",
        [
            "--raw-dir",
            str(data_dir / "raw"),
            "--crosswalk",
            str(
                data_dir / "code-data-audit-20261016/data/pbs-psu-stratum-crosswalk.csv"
            ),
            "--spec",
            str(inputs / "pakistan/SPEC.json"),
            "--spss-archive",
            str(inputs / "pakistan/raw/pbs-spss-2024-25.zip"),
            "--second-report",
            str(data_dir / "followup-surveys-20261015/pbs-latest-linked-report.pdf"),
            "--output-dir",
            str(pakistan_dir),
        ],
    )
    india = read_json(india_dir / "baseline-receipt.json")
    pakistan = read_json(pakistan_dir / "reconciliation.json")
    gate = evaluate_baselines(india, pakistan)
    write_json(output_dir / "baseline-acceptance.json", gate)
    alternatives = read_json(inputs / "public-alternatives.json")
    for source in alternatives["sources"]:
        if sha(inputs / source["path"]) != source["sha256"]:
            raise ValueError("Public alternative source identity failed")
    requirements = read_json(PACKAGE / "requirements.json")["requirements"]
    with (output_dir / "requirement-outcomes.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["id", "requirement", "status", "cause"]
        )
        writer.writeheader()
        writer.writerows(
            {key: row[key] for key in writer.fieldnames} for row in requirements
        )
    claims = []

    def claim(
        identifier: str,
        pointer: list[str],
        value: float,
        unit: str,
        digits: int | None = None,
        output_file: str = "baseline-acceptance.json",
        claim_type: str | None = None,
    ) -> str:
        """Bind a displayed baseline value to its exact recomputed output row."""
        reported = str(value) if digits is None else f"{value:.{digits}f}"
        claims.append(
            {
                "id": identifier,
                "value": value,
                "reported": reported,
                "unit": unit,
                "output_file": output_file,
                "output_pointer": pointer,
                "source_receipt": (
                    "india/baseline-receipt.json"
                    if identifier.startswith("IN")
                    else "pakistan/reconciliation.json"
                ),
                "source_receipt_sha256": sha(
                    india_dir / "baseline-receipt.json"
                    if identifier.startswith("IN")
                    else pakistan_dir / "reconciliation.json"
                ),
                "input_manifest": str(data_dir / "input-manifest.json"),
                "input_manifest_sha256": sha(data_dir / "input-manifest.json"),
                "source_access_date_basis": (
                    "Original acquisitions and cleaned-candidate receipt are retained; "
                    "CPI/SPSS public retrieval receipts are dated2026-10-16."
                ),
                "licence": (
                    "Raw evidence retained privately; public access or candidate "
                    "hash matching does not establish redistribution rights."
                ),
                "producer": "complete_research.py",
                "producer_sha256": sha(Path(__file__)),
                "type": claim_type
                or (
                    "published_target"
                    if "TARGET" in identifier
                    else "reproduction_attempt_not_market_estimate"
                ),
            }
        )
        return f"{reported} [{identifier}]"

    ir = claim(
        "IN-RURAL",
        ["India", "sectors", "rural", "estimate"],
        gate["India"]["sectors"]["rural"]["estimate"],
        "g/person/day",
        6,
    )
    iu = claim(
        "IN-URBAN",
        ["India", "sectors", "urban", "estimate"],
        gate["India"]["sectors"]["urban"]["estimate"],
        "g/person/day",
        6,
    )
    pk = claim(
        "PK-CHICKEN",
        ["Pakistan", "estimate"],
        gate["Pakistan"]["estimate"],
        "kg/person/month",
        6,
    )
    tr = claim(
        "IN-TARGET-R",
        ["India", "sectors", "rural", "published_target"],
        61.8,
        "g/person/day",
    )
    tu = claim(
        "IN-TARGET-U",
        ["India", "sectors", "urban", "published_target"],
        63.4,
        "g/person/day",
    )
    tp = claim("PK-TARGET", ["Pakistan", "published_target"], 0.34, "kg/person/month")
    meal = india["meal_source_diagnostic"]["sector_results"]
    mr = claim(
        "IN-MEAL-R",
        [
            "meal_source_diagnostic",
            "sector_results",
            "rural",
            "variants",
            "general",
            "estimate_g_person_day",
        ],
        meal["rural"]["variants"]["general"]["estimate_g_person_day"],
        "g/person/day",
        6,
        "india/baseline-receipt.json",
        "conditional_meal_source_diagnostic",
    )
    mu = claim(
        "IN-MEAL-U",
        [
            "meal_source_diagnostic",
            "sector_results",
            "urban",
            "variants",
            "general",
            "estimate_g_person_day",
        ],
        meal["urban"]["variants"]["general"]["estimate_g_person_day"],
        "g/person/day",
        6,
        "india/baseline-receipt.json",
        "conditional_meal_source_diagnostic",
    )
    india_point = "passes" if gate["India"]["numerical_reproduction_pass"] else "fails"
    pakistan_point = (
        "passes" if gate["Pakistan"]["numerical_reproduction_pass"] else "fails"
    )
    opening = f"""# Pakistan and India protein markets

16 October 2026. AI-assisted research for Muhammad Umar Zafar. Local review edition.

**The baseline calculations now run. The combined acceptance result is {gate['status']}. The requested national market estimates and forecast quantiles remain unestablished.**

**1. How large is each protein market?** India's complete unadjusted candidate reconstruction gives {ir} rural and {iu} urban g/person/day. It {india_point} the published numerical comparison; method and raw-lineage qualifications remain separate. Pakistan's all-channel chicken reconstruction gives {pk} kg/person/month and {pakistan_point} the report's rounding comparison. These are reproduction attempts. Neither is a new national protein-market estimate.

**2. What are the alternative-protein pillars' sizes and shares?** No compatible current country/pillar numerator is established. Published context, company/product records and broad protein imports are retained side by side. They do not identify the same finished-product sales. An unresolved value is not zero; the methods are not averaged.

**3. What explains consumption?** Published NFHS research supports discussion of food frequency and wealth/education associations. Older household-expenditure research also examines price, religion, caste and geography. Those sources do not replace the requested new respondent-level decomposition or current country elasticities. No causal contribution or new confidence interval is invented.

**4. What must change in certification, regulation and AI?** Track named product approvals, traceable process-specific halal decisions, and measured technical performance against a declared comparison. The original policy and religious texts remain available. The author's independent policy labels are absent; agreement is unmeasured. Existing linguistic/religious acceptance does not establish technical performance or food approval.

**5. What shares could the pillars reach?** No calibrated future quantiles are reported. The brief stops downstream estimation when either official baseline fails. The questionnaire and committed resolution questions are preserved. Anna's completed US outputs remain deferred.

"""
    report = opening + f"""---

## What the completed baseline work establishes

| Comparator | Recomputed value | Published target | Numerical result |
| --- | --- | --- | --- |
| India rural, unadjusted | {ir} g/person/day | {tr} | {india_point} |
| India urban, unadjusted | {iu} g/person/day | {tu} | {india_point} |
| Pakistan chicken, all channels | {pk} kg/person/month | {tp} | {pakistan_point} |
| India rural, observed-roster meal diagnostic | {mr} g/person/day | {tr} | Conditional numerical match; method unverified |
| India urban, observed-roster meal diagnostic | {mu} g/person/day | {tu} | Conditional numerical match; method unverified |

The India estimator combines coefficient-bearing physical foods and all monetary conversion factors, applies a predeclared sector CPI interpretation and uses survey household weights with the food-questionnaire denominator. The official public CPI API removes the account/download obstacle. A food-index sensitivity is retained separately; no index is selected because it happens to match a target. Meal-adjusted protein is a separate estimand. Target agreement cannot authenticate missing original official text files or redistribution rights. See the input quality checks, CPI records, source factors and design qualifications in india/baseline-receipt.json.

The additional meal-source diagnostic replaces only the item-based meal contribution with observed roster away-meal protein, forming X+G before donor adjustment. It localizes most of the discrepancy and numerically matches the targets. The source explicitly dates meal questions to the food visit, but the stored membership status can reflect later revisits, and blank meal-field semantics remain unverified. The report does not explicitly label X+G as its unadjusted formula. Therefore this remains a conditional diagnostic, with missingness counts retained; it is not selected to open the gate. The earlier statement that meal inputs could have no role in the unadjusted reconstruction was too strong: the donor adjustment is separate, while the underlying meal-source definition still needs validation.

Pakistan retains every released household denominator and all observed acquisition channels. Questionnaire recall and final household membership determine the primary comparison. Annualisation, alternative denominators and geographic domains are explicitly labelled checks. Paid-only consumption and household-weighted means of per-person ratios are different estimands; they cannot replace the primary result. The separately downloaded official SPSS release is read independently and compared with Stata. The source conflict remains a finding when consistent released data disagree with the report. See pakistan/reconciliation.json and variants.csv.

The acceptance test now evaluates calculated results and method eligibility. It has genuine passing and failing test cases. A missing value, incomplete component subtotal, fitted result or dropped channel cannot open the gate. Method acceptance and numerical agreement are recorded separately. A gate pass would establish only these prerequisites, not every later result. The current combined result is {gate['status']}.

## Market evidence and price coverage

The existing reconciliation matrix preserves every country, pillar and method separately. Its source tables retain attributed published context, original company records and broad trade responses. Imports at the requested headings do not distinguish plant-based, fermentation and cultivated finished consumer products. Domestic production, exports, intermediate uses and retail valuation are also unresolved. Three independent compatible current measures cannot be constructed from these inputs. No midpoint, extrapolated listing revenue or zero-sales assumption is supplied.

The outlet captures establish dated displayed prices and availability statements. They do not establish national coverage or delivery to an unspecified location. A price per gram of protein also requires an exact nutrition basis, edible weight, dry/cooked state and any density conversion. Those calculations remain stopped under the failed baseline prerequisite. The original captures and offline inventory remain available in source-tables/retail/.

## Public evidence that can replace part of the missing NFHS access

{alternatives['sources'][0]['finding']} Its outcome definition treats daily or weekly intake as consumption. The authors report that the wealth pattern for meat/fish differs from most other food groups: nonweekly consumption is more common in the highest wealth group. This is an observational finding, not a causal income effect. Its underlying data-sharing statement requires a request; no such request was sent. [Original NFHS analysis]({alternatives['sources'][0]['url']}).

{alternatives['sources'][1]['finding']} This establishes a useful literature comparison, with explicit differences in survey round and outcome. It supplies no replacement respondent records. [Original household study]({alternatives['sources'][1]['url']}).

Pakistan DHS child previous-day foods and the National Nutrition Survey's women's previous-day dietary diversity remain non-equivalent to the requested adult weekly outcome. The named datasets and questionnaire checks are retained in the source package. The workaround is an attributed evidence synthesis; it does not become the requested unit-level analysis.

## Certification, policy review and forecasts

The policy register covers the specified Indian institutions and Pakistan's federal and provincial authorities. Plant-based labels, fermentation process/ingredient authorisation and cultivated-product decisions must be inspected separately. A general programme, an AI objective or a patent does not establish an approved product, an operating plant, a cost saving or a market share.

The religious chapter retains named, dated original Urdu/Arabic passages and the version-bound author acceptance of the existing readings. Process conditions, product certification and food authorisation remain separate. A missing cultivated-specific Indian original is recorded as a source gap, never inferred from a general certification resolution.

Pakistan's Banuri Town Darul Iftaa gives institution-specific conditional answers dated 31 October 2018 and 17 September 2019. Muhammad Muaz Ashraf's Urdu/Arabic analysis hosted by Darul Uloom Karachi has a landing post dated 17 October 2023, with separate installment dates. India's Islamic Fiqh Academy has a general certification resolution from its March 2015 seminar and AI guidance from its November 2024 seminar; neither establishes a cultivated-product permission. These are attributed positions, not national consensus. [Banuri original](https://www.banuri.edu.pk/readquestion/144012201327/17-09-2019), [Karachi institutional post](https://darululoomkarachi.edu.pk/?p=30112), [Indian Urdu certification original](https://www.ifa-india.org/ur/pdfs/pdf-20260729113303.pdf). The retained halal chapter and claim ledger supply exact original passages and translation notes. The author's acceptance covers those existing readings without asserting an independent specialist credential.

Independent author coding is a human measurement in the brief. Generating it with an agent would change the measurement. The blank responses and disclosure remain preserved, and kappa remains unmeasured. This requirement is explicitly unresolved; it does not prevent delivery of the rest of this report.

The questionnaire, country-substitution drafts and earlier committed regulatory questions remain available. No country elicitation, Bass fit or sensitivity ranking is run across a failed baseline prerequisite. No assumed interval is relabelled as a calibrated prediction. US comparison remains deferred as instructed.

## Household-meal agenda

Test whether conventional and alternative foods fit the same household meal, whether one household member's restriction changes shared purchasing, and whether the serving size and use occasion support repeat consumption. Compare price, taste, preparation, access and religious legitimacy separately. Each test needs a specified outcome, comparison and falsifier. No new human respondent survey was conducted.

## Every success criterion and its outcome

The following table records what passed, what remains unresolved and the cause. It implements the brief's documented-failure route without claiming that missing estimates exist. The full empirical research is incomplete.

| Criterion | Status | Cause or evidence boundary |
| --- | --- | --- |
"""
    for row in requirements:
        cause = row["cause"].replace("|", "/").replace("\n", " ")
        label = row["status"].replace("_", " ")
        report += f"| {row['id']} | {label} | {cause} |\n"
    report += "\n## Reproducibility and source identities\n\nThe claims ledger binds displayed baseline findings to the recomputed JSON, source receipts and producer bytes. The source-table pipeline verifies original capture hashes. Public literature captures are separately hash-bound. This edition rebuilds without network access from the retained files; respondent records are not redistributed. The data-access guide records lawful acquisition and unresolved rights. Verification and independent moderation are separate saved receipts.\n"
    (output_dir / "OPENING.md").write_text(opening, encoding="utf-8")
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    render_report(output_dir / "OPENING.md", output_dir / "OPENING.pdf")
    render_report(output_dir / "REPORT.md", output_dir / "REPORT.pdf")
    write_json(output_dir / "claims-ledger.json", {"claims": claims})
    for item in claims:
        actual = read_json(output_dir / item["output_file"])
        for key in item["output_pointer"]:
            actual = actual[key]
        if actual != item["value"]:
            raise ValueError("Claim pointer/value mismatch")
    pdf_text = subprocess.run(
        ["pdftotext", str(output_dir / "REPORT.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for item in claims:
        token = rf"(?<![\d.]){re.escape(item['reported'])}(?![\d.])"
        if item["id"] not in report or not all(
            re.search(token, text) for text in [report, pdf_text]
        ):
            raise ValueError("Claim display missing from Markdown or PDF")
    status = {
        "scope": "Completed baseline reproduction attempts and documented research limits",
        "baseline_gate": gate["status"],
        "new_estimation_allowed": gate["new_estimation_allowed"],
        "full_empirical_research_complete": False,
        "all_success_criteria_have_outcomes_and_causes": all(
            row["status"] and row["cause"] for row in requirements
        ),
        "numeric_report_claims_verified": len(claims),
        "public_alternative_sources_verified": len(alternatives["sources"]),
        "new_market_estimates": 0,
        "forecasts_run": 0,
    }
    write_json(output_dir / "status.json", status)
    return status


def main() -> int:
    """Run the completion edition, returning two for a genuine failed baseline gate."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--hces-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = complete_research(args.data_dir, args.hces_dir, args.output_dir)
    print(json.dumps(result, indent=2))
    return 0 if result["baseline_gate"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
