"""Prepare private country-substitution drafts without running any model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

__all__ = ["adapt_text", "main", "prepare"]

COUNTRIES = {"India": "Indian", "Pakistan": "Pakistani"}
INSTRUMENT_SHA256 = "33b45e78fd3b0cedbae8d7c61e9ea1565babddc8495acb98988eebb7224c8504"
INSTRUMENT_TEXT_SHA256 = (
    "000293004ca738d65b5e300a8de331abbc9d40876e6a40d2495e4532304ca9f0"
)


def adapt_text(text: str, country: str) -> tuple[str, list[dict[str, str | int]]]:
    """Change only specified country phrases and disclose every substitution."""
    adjective = COUNTRIES[country]
    substitutions = [
        ("market in the U.S.", f"market in {country}."),
        ("terms of US sales", f"terms of sales in {country}"),
        ("total US retail dollar sales", f"total {adjective} retail dollar sales"),
        (
            "for U.S. plant-based food retail sales",
            f"for {adjective} plant-based food retail sales",
        ),
        ("what will be the US", f"what will be the {adjective}"),
        ("US consumer sales", f"{adjective} consumer sales"),
    ]
    protected = ["2025 US dollars", "CPI-U, Food at Home, U.S. city average"]
    original_counts = {phrase: text.count(phrase) for phrase in protected}
    changes = []
    for original, replacement in substitutions:
        count = text.count(original)
        if count != 1:
            raise ValueError(
                "Instrument extraction differs from the reviewed country-phrase contract"
            )
        changes.append(
            {"original": original, "replacement": replacement, "occurrences": count}
        )
        text = text.replace(original, replacement)
    if any(text.count(phrase) != count for phrase, count in original_counts.items()):
        raise ValueError(
            "Country adaptation changed a protected currency or deflator phrase"
        )
    return text, changes


def prepare(data_dir: Path) -> dict:
    """Bind private adaptation drafts to the supplied original instrument."""
    original = data_dir / "inputs/elicitation-original.docx"
    with original.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != INSTRUMENT_SHA256:
        raise ValueError(
            "Original elicitation instrument identity differs from the reviewed source"
        )
    text = (data_dir / "inputs/elicitation-original.txt").read_text(encoding="utf-8")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != INSTRUMENT_TEXT_SHA256:
        raise ValueError(
            "Instrument extraction identity differs from the reviewed text"
        )
    output = data_dir / "elicitation"
    output.mkdir(exist_ok=True)
    records = []
    for country in COUNTRIES:
        adapted, changes = adapt_text(text, country)
        payload = adapted.encode("utf-8")
        relative = f"elicitation/{country.lower()}-country-only-draft.txt"
        (data_dir / relative).write_bytes(payload)
        records.append(
            {
                "country": country,
                "path": relative,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "changes": changes,
            }
        )
    result = {
        "source_instrument_sha256": digest,
        "source_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "status": "country_substitution_drafts_not_executed",
        "execution_allowed": False,
        "models_called": 0,
        "drafts": records,
        "unresolved_before_execution": [
            "Both official reproduction gates and preregistration chronology must pass.",
            "Country substitution does not supply a matching local GFI resolution series.",
            "The US CPI and constant-2025-USD clauses remain verbatim; document any later local price/currency adaptation separately.",
            "Named model versions, repeat counts, settings, Delphi protocol and output aggregation remain to be established.",
            "Actual US model outputs are required for a numerical comparison.",
        ],
        "preserved_scope": [
            "intentional pillar overlap",
            "cultivated pet-food exception",
            "retail-only plant-based question",
            "retail-and-foodservice cultivated/fermentation question",
            "existing forecasts allowed with disclosure",
        ],
    }
    (output / "adaptation-manifest.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    """Write private drafts and the adaptation manifest without eliciting a forecast."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    arguments = parser.parse_args()
    result = prepare(arguments.data_dir)
    print(
        json.dumps(
            {"status": result["status"], "models_called": result["models_called"]}
        )
    )


if __name__ == "__main__":
    main()
