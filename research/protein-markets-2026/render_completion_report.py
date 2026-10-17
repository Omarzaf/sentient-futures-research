"""Export reviewed Markdown through Pandoc into a paginated research PDF."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

__all__ = ["render_report"]


def inline(nodes: list[dict]) -> str:
    """Render Pandoc inline nodes with escaped text and source links."""
    result = []
    for node in nodes:
        kind = node["t"]
        value = node.get("c")
        if kind == "Str":
            result.append(html.escape(value))
        elif kind in {"Space", "SoftBreak", "LineBreak"}:
            result.append(" ")
        elif kind in {"Strong", "Emph"}:
            tag = "b" if kind == "Strong" else "i"
            result.append(f"<{tag}>{inline(value)}</{tag}>")
        elif kind == "Code":
            result.append(html.escape(value[1]))
        elif kind == "Link":
            url = html.escape(value[2][0], quote=True)
            result.append(
                f'<link href="{url}" color="#234b62">{inline(value[1])}</link>'
            )
        elif kind == "Quoted":
            result.append('"' + inline(value[1]) + '"')
        elif kind == "Span":
            result.append(inline(value[1]))
        else:
            raise ValueError(f"Unsupported report inline: {kind}")
    return "".join(result)


def block_text(blocks: list[dict]) -> str:
    """Read simple paragraphs in a table cell or list item without data loss."""
    texts = []
    for node in blocks:
        if node["t"] not in {"Para", "Plain"}:
            raise ValueError(f"Unsupported nested report block: {node['t']}")
        texts.append(inline(node["c"]))
    return "<br/>".join(texts)


def render_report(markdown: Path, output: Path) -> None:
    """Build a PDF from Pandoc's parsed document, preserving tables and links."""
    parsed = subprocess.run(
        ["pandoc", str(markdown), "--from=markdown", "--to=json"],
        check=True,
        capture_output=True,
        text=True,
    )
    document = json.loads(parsed.stdout)
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "ResearchBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13.2,
        spaceAfter=7,
        textColor=colors.HexColor("#202c32"),
    )
    small = ParagraphStyle("ResearchCell", parent=body, fontSize=8.1, leading=10.8)
    heading = ParagraphStyle(
        "ResearchHeading",
        parent=styles["Heading2"],
        keepWithNext=True,
        fontSize=13,
        leading=16,
        spaceBefore=11,
        spaceAfter=7,
        textColor=colors.HexColor("#234b62"),
    )
    title = ParagraphStyle(
        "ResearchTitle",
        parent=styles["Title"],
        alignment=0,
        fontSize=21,
        leading=24,
        spaceAfter=13,
        textColor=colors.HexColor("#183847"),
    )
    story = []
    for node in document["blocks"]:
        kind, content = node["t"], node.get("c")
        if kind == "Header":
            story.append(
                Paragraph(inline(content[2]), title if content[0] == 1 else heading)
            )
        elif kind in {"Para", "Plain"}:
            story.append(Paragraph(inline(content), body))
        elif kind == "BulletList":
            for item in content:
                story.append(Paragraph(block_text(item), body, bulletText="-"))
        elif kind == "HorizontalRule":
            story.append(PageBreak())
        elif kind == "Table":
            rows = list(content[3][1])
            for table_body in content[4]:
                rows.extend(table_body[2])
                rows.extend(table_body[3])
            rows.extend(content[5][1])
            cells = [
                [Paragraph(block_text(cell[4]), small) for cell in row[1]]
                for row in rows
            ]
            if not cells or not cells[0]:
                raise ValueError("Empty report table")
            available = A4[0] - 36 * mm
            widths = (
                [available * share for share in (0.11, 0.25, 0.64)]
                if len(cells[0]) == 3
                else [available / len(cells[0])] * len(cells[0])
            )
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eff1")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        (
                            "LINEBELOW",
                            (0, 0),
                            (-1, -1),
                            0.25,
                            colors.HexColor("#ccd8dd"),
                        ),
                    ]
                )
            )
            story.extend([table, Spacer(1, 8)])
        else:
            raise ValueError(f"Unsupported report block: {kind}")

    def footer(canvas: object, doc: object) -> None:
        """Draw a stable page footer without a changing generation timestamp."""
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52676f"))
        canvas.drawString(
            18 * mm, 12 * mm, "India-Pakistan research | 16 October 2026 | Local review"
        )
        canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, str(doc.page))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=20 * mm,
        title="India-Pakistan protein markets: baseline completion and evidence limits",
        author="Muhammad Umar Zafar; AI-assisted research",
        invariant=1,
    )
    pdf.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    """Export the selected reviewed Markdown edition without network access."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render_report(args.markdown, args.output)


if __name__ == "__main__":
    main()
