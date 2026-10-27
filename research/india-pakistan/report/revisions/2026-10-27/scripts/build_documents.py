"""Build an offline readable HTML document from the packaged Markdown sources."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "report/chapter.md",
    "methods/proxy.md",
    "methods/gfi-gap.md",
    "methods/drivers.md",
    "methods/dated-context.md",
    "methods/measurement-crosswalk.md",
    "methods/panel-supplement.md",
    "report/limitations-and-ai-use.md",
)

ANCHORS = {
    "report/chapter.md": "chapter",
    "methods/proxy.md": "proxy-method",
    "methods/gfi-gap.md": "gfi-gap",
    "methods/drivers.md": "drivers",
    "methods/dated-context.md": "dated-context",
    "methods/measurement-crosswalk.md": "measurement-crosswalk",
    "methods/panel-supplement.md": "panel-method",
    "report/limitations-and-ai-use.md": "limitations",
}


def document_source(name: str) -> str:
    """Resolve source-relative links for the combined report and anchor included sections."""
    source = ROOT / name
    text = source.read_text()
    text = re.sub(
        r"^# (.+)$", rf"# \1 {{#{ANCHORS[name]}}}", text, count=1, flags=re.MULTILINE
    )

    def relative_link(match: re.Match[str]) -> str:
        """Keep external URLs and convert packaged paths relative to report/review.html."""
        target = match.group(1)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            return match.group(0)
        resolved = (source.parent / unquote(parts.path)).resolve()
        if not resolved.is_relative_to(ROOT):
            raise ValueError(f"Link outside package in {name}")
        relative = resolved.relative_to(ROOT).as_posix()
        if relative in ANCHORS and not parts.fragment:
            return "](#" + ANCHORS[relative] + ")"
        output = Path(os.path.relpath(resolved, ROOT / "report")).as_posix()
        return (
            "]("
            + output.replace(" ", "%20")
            + ("#" + parts.fragment if parts.fragment else "")
            + ")"
        )

    return re.sub(r"\]\(([^)\s]+)\)", relative_link, text)


def main() -> None:
    """Use optional local Pandoc; numerical reproduction does not require it."""
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise SystemExit(
            "Pandoc is optional and not installed. Read the supplied HTML/PDF or Markdown."
        )
    combined = "\n\n".join(document_source(name) for name in SOURCES)
    subprocess.run(
        [
            pandoc,
            "--from=markdown",
            "--to=html5",
            "--standalone",
            "--toc",
            "--toc-depth=1",
            "--metadata=lang:en",
            "--metadata=title:Alternative-protein spending in India and Pakistan",
            "--metadata=subtitle:Drivers, conditional scenarios and the GFI comparison",
            "--metadata=author:Muhammad Umar Zafar",
            "--metadata=date:27 October 2026 · Local review candidate",
            "--css=report.css",
            "--output=" + str(ROOT / "report/review.html"),
        ],
        input=combined,
        text=True,
        check=True,
    )
    html_path = ROOT / "report/review.html"
    html = html_path.read_text()
    table_index = 0

    def wrap_table(match: re.Match[str]) -> str:
        """Keep wide method tables readable with keyboard-accessible local scroll."""
        nonlocal table_index
        table_index += 1
        compact = (
            " compact-table"
            if match.group(0).count("<tr") <= 8 and len(match.group(0)) < 4500
            else ""
        )
        return (
            '<p class="table-hint">Scroll the table horizontally on a narrow screen.</p>'
            f'<div class="table-scroll{compact}" role="region" aria-label="Data table {table_index}" tabindex="0">'
            + match.group(0)
            + "</div>"
        )

    html = re.sub(r"<table\b.*?</table>", wrap_table, html, flags=re.DOTALL)
    html = re.sub(
        r"(<figure\b.*?</figure>)",
        r'<div class="figure-scroll" role="region" aria-label="Required growth figure" tabindex="0">\1</div>',
        html,
        flags=re.DOTALL,
    )
    html_path.write_text(html)
    record = {
        "status": "AI-assisted review draft; human verification pending",
        "pandoc": subprocess.check_output(
            [pandoc, "--version"], text=True
        ).splitlines()[0],
        "sources": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in SOURCES
        },
        "html_sha256": hashlib.sha256(
            (ROOT / "report/review.html").read_bytes()
        ).hexdigest(),
        "pdf_rendering": "The supplied PDF was rendered with sandboxed Chromium from a temporary print copy with inline CSS and local file hyperlinks removed. Re-rendering must repeat those precautions and inspect PDF metadata, text and link annotations for local paths. Rendering is optional; the supplied PDF is ready to read.",
        "limits": "Document rendering is separate from numerical reproduction. PDF visual QA and renderer version are recorded in the external release receipt.",
    }
    (ROOT / "provenance/document-build.json").write_text(
        json.dumps(record, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "status": "HTML_BUILT",
                "source_count": len(SOURCES),
                "html_sha256": record["html_sha256"],
            }
        )
    )


if __name__ == "__main__":
    main()
