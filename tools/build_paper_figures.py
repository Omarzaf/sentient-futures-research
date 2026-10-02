"""Build source-bounded paper figures from the live citation register."""

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

__all__ = ["main"]
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "research/halal-cultivated/paper"
INK = "#193b38"
GREEN = "#306f69"
GOLD = "#ab7032"
GRAY = "#67727a"


def save(fig: plt.Figure, name: str) -> None:
    """Write the vector source and a print-resolution raster companion."""
    for ext in ("svg", "png"):
        fig.savefig(
            PAPER / "figures" / f"{name}.{ext}",
            dpi=220,
            facecolor="white",
            metadata={"Date": None} if ext == "svg" else None,
        )
    plt.close(fig)


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str) -> None:
    """Draw one process stage with an explicit text label."""
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012",
            linewidth=0.7,
            edgecolor=GREEN,
            facecolor="#eff5f3",
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, color=INK)


def process_figure() -> None:
    """Separate the schematic manufacturing sequence from analytical questions."""
    fig, ax = plt.subplots(figsize=(7.2, 5.5))
    fig.subplots_adjust(left=0.035, right=0.98, top=0.97, bottom=0.02)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ax.text(
        0,
        0.98,
        "From starting cells to a food product",
        fontsize=11,
        weight="bold",
        color=INK,
        va="top",
    )
    stages = [
        ("Donor / egg\nsource", 0.02),
        ("Founder cells\nand bank", 0.27),
        ("Culture\nand inputs", 0.52),
        ("Harvest / wash\nformulation", 0.77),
    ]
    for label, x in stages:
        box(ax, x, 0.77, 0.20, 0.13, label)
        if x < 0.7:
            ax.annotate(
                "",
                xy=(x + 0.245, 0.835),
                xytext=(x + 0.205, 0.835),
                arrowprops={"arrowstyle": "->", "color": GRAY},
            )
    ax.text(
        0.02,
        0.72,
        "Alternative sources include biopsy, post-mortem tissue and embryonic routes.\nBanking, media and final formulation vary by process; this is not a universal recipe.",
        fontsize=8.7,
        va="top",
        color=GRAY,
    )
    rows = [
        ("1  Donor / procurement", "Species, tissue, collection and slaughter history"),
        ("2  Culture inputs", "Origin, function, carryover and removal of each input"),
        (
            "3  Transformation",
            "Named authority's criterion and relevant process evidence",
        ),
        (
            "4  Edibility",
            "Status of the final object under the attributed dietary rule",
        ),
        (
            "5  Certification",
            "Applicable route and an actual certificate for that product",
        ),
        (
            "6  Food authorization",
            "Regulator, product, process, territory and effective date",
        ),
    ]
    for i, (label, detail) in enumerate(rows):
        y = 0.59 - i * 0.085
        ax.text(0.02, y, label, fontsize=9.2, color=INK, weight="bold")
        ax.text(0.02, y - 0.037, detail, fontsize=8.8, color=GRAY)
    ax.text(
        0.02,
        0.025,
        "Arrows show manufacturing sequence only. The six questions are this paper's analytical framework.",
        fontsize=8.2,
        color=GRAY,
    )
    save(fig, "figure-1-process")


def country_figure() -> list[dict]:
    """Visualize admitted document scope without assigning national access states."""
    # Labels are documentary scope, not probabilities or legal conclusions.
    data = [
        (
            "India",
            [
                "Not located",
                "Not established",
                "Not established",
                "2017 route",
                "Not located",
                "Regional only",
            ],
        ),
        (
            "Pakistan",
            [
                "Not located",
                "2016 remit",
                "Not established",
                "Not established",
                "Not located",
                "Constitution",
            ],
        ),
        (
            "Saudi Arabia",
            [
                "Not located",
                "Guide / scope",
                "Not established",
                "Novel-food docs",
                "Not located",
                "Basic Law only",
            ],
        ),
        (
            "UAE",
            [
                "Not located",
                "Halal system",
                "Not established",
                "Unretrieved lead",
                "Not located",
                "Unretrieved",
            ],
        ),
        (
            "Singapore",
            [
                "MUIS conditions",
                "2024 framework",
                "Not established",
                "SFA framework",
                "Named processes",
                "Dated plurality",
            ],
        ),
        (
            "Malaysia",
            [
                "Language hold",
                "Foreign bodies",
                "Not established",
                "Not established",
                "Not located",
                "Territories only",
            ],
        ),
        (
            "Indonesia",
            [
                "Language hold",
                "2025 mechanism",
                "Not established",
                "Not established",
                "Not located",
                "Dated study",
            ],
        ),
    ]
    headers = [
        "Religious\nposition",
        "Certification\nmechanism",
        "Product\ncertificate",
        "Food\nroute",
        "Product food\nlisting",
        "Authority /\ncommunity",
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.7))
    fig.subplots_adjust(left=0.015, right=0.995, top=0.99, bottom=0.025)
    ax.set(xlim=(-1.15, 6), ylim=(-1.2, 8))
    ax.axis("off")
    ax.text(
        -1.12,
        7.75,
        "Documentary evidence is uneven across layers",
        fontsize=12,
        weight="bold",
        color=INK,
    )
    for j, header in enumerate(headers):
        ax.text(
            j + 0.48, 6.95, header, ha="center", va="center", fontsize=8.3, color=INK
        )
    for i, (country, cells) in enumerate(data):
        y = 5.9 - i * 0.87
        ax.text(-1.1, y + 0.3, country, fontsize=9, va="center", color=INK)
        for j, cell in enumerate(cells):
            missing = cell.startswith(("Not ", "Unretrieved"))
            held = cell == "Language hold"
            color = "#f0f1f2" if missing else "#f8ebd9" if held else "#deede9"
            ax.add_patch(
                FancyBboxPatch(
                    (j, y),
                    0.94,
                    0.64,
                    boxstyle="round,pad=0.01",
                    linewidth=0,
                    facecolor=color,
                )
            )
            ax.text(
                j + 0.47,
                y + 0.32,
                cell.replace("Not established", "Not\nestablished")
                .replace("Unretrieved lead", "Unretrieved\nlead")
                .replace("2025 mechanism", "2025\nmechanism")
                .replace("Novel-food docs", "Novel-food\ndocuments"),
                ha="center",
                va="center",
                fontsize=7.6,
                color=INK,
            )
    ax.text(
        -1.1,
        -0.62,
        "Green: admitted, bounded document   •   Amber: language hold   •   Gray: missing in this review",
        fontsize=8.2,
        color=GRAY,
    )
    ax.text(
        -1.1,
        -1.02,
        "Evidence checked 2 October 2026. A document is not a national verdict. Detailed scope and citations: §9 and Appendix B.",
        fontsize=8.2,
        color=GRAY,
    )
    save(fig, "figure-2-countries")
    return [{"country": country, "scope_labels": labels} for country, labels in data]


def audit_figure(sources: list[dict], audit: list[dict]) -> dict:
    """Count canonical audit records and admitted article reading scopes separately."""
    counts = Counter(row["verdict"] for row in audit)
    assert len(audit) == len(sources) == len({s["key"] for s in sources})
    admitted = [
        s for s in sources if s["audit_verdict"] in ("verified", "verified_with_note")
    ]
    articles = [s for s in admitted if s["source_type"] == "journal_article"]
    scopes = Counter(s["reading_scope"] for s in articles)
    fig, axes = plt.subplots(
        2, 1, figsize=(7.2, 4.5), gridspec_kw={"height_ratios": [3, 2]}
    )
    fig.subplots_adjust(left=0.32, right=0.90, top=0.86, bottom=0.12, hspace=1.0)
    labels = ["Qualified records", "Held", "Not retrieved"]
    values = [
        counts["verified_with_note"] + counts["verified"],
        counts["held"],
        counts["not_retrieved"],
    ]
    panels = [
        (labels, values, [GREEN, GOLD, GRAY], f"Canonical records · n = {len(audit)}"),
        (
            ["Full-text passages", "English abstract only"],
            [scopes["full_text_scoped_passages"], scopes["abstract_only"]],
            [GREEN, GOLD],
            f"Admitted journal articles · n = {len(articles)}",
        ),
    ]
    for ax, (lab, val, colors, title) in zip(axes, panels):
        ax.barh(lab, val, color=colors, height=0.6)
        ax.invert_yaxis()
        ax.set_xlim(0, max(val) * 1.18)
        for i, value in enumerate(val):
            ax.text(
                value + max(val) * 0.02,
                i,
                str(value),
                va="center",
                fontsize=11,
                color=INK,
            )
        ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
        ax.set_xticks([])
        ax.tick_params(axis="y", length=0, labelsize=10, colors=INK)
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.text(
        0.04,
        0.97,
        "Evidence available to this paper",
        fontsize=12,
        weight="bold",
        color=INK,
        va="top",
    )
    fig.text(
        0.04,
        0.035,
        "Counts measure research availability, not independent authorities, agreement or legal validity.\nFive aliases are folded into canonical records; one qualified record supplies index metadata only.",
        fontsize=8.5,
        color=GRAY,
    )
    save(fig, "figure-3-audit")
    return {
        "canonical_records": len(audit),
        "verdicts": dict(counts),
        "admitted_article_reading_scopes": dict(scopes),
        "aliases": sum(len(s["aliases"]) for s in sources),
    }


def main() -> None:
    """Generate three figures and their auditable data receipt."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "svg.fonttype": "none",
            "svg.hashsalt": "halal-paper-2026",
        }
    )
    (PAPER / "figures").mkdir(exist_ok=True)
    sources = json.loads((PAPER / "source-register.json").read_text())
    audit = json.loads((PAPER / "citation-audit.json").read_text())
    process_figure()
    countries = country_figure()
    counts = audit_figure(sources, audit)
    receipt = {
        "as_of": "2026-10-02",
        "human_review": "pending",
        "counts": counts,
        "countries": countries,
        "manufacturing_sources": ["B4-CELLS", "GOOD-DOSSIER", "SG-LIST"],
        "interpretation": "Document availability and scope only; no country access assessment or religious vote.",
    }
    (PAPER / "figure-data.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
