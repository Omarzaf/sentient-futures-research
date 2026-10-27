"""Render the required-growth diagnostic using existing optional Matplotlib tooling."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

__all__ = ["main"]


def main() -> None:
    """Plot assumption ranges and record their source hash without rerunning the model."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "svg.hashsalt": "gfi-gap-20261027",
        }
    )
    fig, ax = plt.subplots(figsize=(9.2, 4.7))
    fig.patch.set_facecolor("#fffefa")
    ax.set_facecolor("#fffefa")
    labels = []
    for index, scenario in enumerate(("low", "medium", "high")):
        group = [row for row in rows if row["scenario"].lower() == scenario]
        if not group:
            raise ValueError(f"Missing scenario: {scenario}")
        values = [float(row["required_extra_growth_percent"]) for row in group]
        ordered = sorted(group, key=lambda row: float(row["elasticity"]))
        middle = float(ordered[len(ordered) // 2]["required_extra_growth_percent"])
        lo, hi = min(values), max(values)
        y = 2 - index
        ax.hlines(y, lo, hi, color="#185a62", linewidth=5, zorder=3)
        ax.scatter([middle], [y], s=62, color="#102f34", zorder=4)
        ax.text(hi + 1.5, y, f"{lo:.1f}-{hi:.1f}%", va="center", fontsize=11)
        labels.append({"scenario": scenario, "low": lo, "midpoint": middle, "high": hi})
    ceiling = float(rows[0]["current_extra_growth_ceiling_percent"])
    ax.axvline(ceiling, color="#a46923", linestyle=(0, (4, 3)), linewidth=1.7)
    ax.text(
        ceiling - 1.0,
        2.63,
        f"Current ceiling\n{ceiling:.1f}%",
        ha="right",
        va="top",
        color="#87521b",
        fontsize=10,
    )
    ax.set_yticks([2, 1, 0], ["GFI low", "GFI medium", "GFI high"])
    ax.set_xlim(0, 63)
    ax.set_ylim(-0.55, 2.8)
    ax.set_xticks(range(0, 61, 10), [f"{value}%" for value in range(0, 61, 10)])
    ax.set_xlabel("Required extra annual growth, 2022-2030", labelpad=12)
    ax.grid(axis="x", color="#dce3df", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=12)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.suptitle(
        "What reaching GFI's scenarios would require",
        x=0.04,
        ha="left",
        y=0.98,
        fontsize=16,
        fontweight="bold",
        color="#182c33",
    )
    fig.text(
        0.04,
        0.895,
        "After the retained population, income and urbanisation factors",
        fontsize=10.5,
        color="#4c6064",
    )
    fig.text(
        0.04,
        0.035,
        "Ranges vary income elasticity; dots use its midpoint. These are not predictive intervals.\nAll targets retain the unresolved GFI price-basis assumption. Source: required-growth.csv.",
        fontsize=9,
        color="#4c6064",
    )
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.24, top=0.83)
    fig.savefig(
        args.output / "gfi-required-growth.png",
        dpi=180,
        metadata={"Software": "Matplotlib"},
    )
    fig.savefig(
        args.output / "gfi-required-growth.svg",
        metadata={
            "Date": None,
            "Title": "Required extra growth to reach GFI domestic scenarios",
            "Description": "Assumption sensitivity across income elasticity, not forecast uncertainty.",
        },
    )
    svg = args.output / "gfi-required-growth.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(fig)
    receipt = {
        "source_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "matplotlib": matplotlib.__version__,
        "ceiling_percent": ceiling,
        "labels": labels,
        "limits": "Inverse-model diagnostic; unresolved source price basis; no predictive probability claim.",
    }
    (args.output / "figure-data.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
