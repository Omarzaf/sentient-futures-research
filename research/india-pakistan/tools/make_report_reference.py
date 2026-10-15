"""Create the report's Word reference styles from the installed Pandoc default."""

from __future__ import annotations

import io
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", NS)


def element(parent: ET.Element, tag: str, **attributes: str) -> ET.Element:
    """Find or add one WordprocessingML property and set its supplied attributes."""
    found = parent.find(f"{{{NS}}}{tag}")
    if found is None:
        found = ET.SubElement(parent, f"{{{NS}}}{tag}")
    for key, value in attributes.items():
        found.set(f"{{{NS}}}{key}", value)
    return found


def main() -> None:
    """Write a reproducible reference without editing the content document."""
    data = subprocess.check_output(
        ["pandoc", "--print-default-data-file", "reference.docx"]
    )
    with zipfile.ZipFile(io.BytesIO(data)) as source:
        parts = {name: source.read(name) for name in source.namelist()}
    styles = ET.fromstring(parts["word/styles.xml"])
    for style in styles.findall(f"{{{NS}}}style"):
        key = style.get(f"{{{NS}}}styleId", "")
        if key == "Table":
            element(element(style, "trPr"), "cantSplit")
        if key in {
            "Title",
            "Subtitle",
            "Normal",
            "BodyText",
            "FirstParagraph",
        } or key.startswith("Heading"):
            run = element(style, "rPr")
            font = element(
                run, "rFonts", ascii="Georgia", hAnsi="Georgia", cs="Georgia"
            )
            for attribute in list(font.attrib):
                if attribute.endswith("Theme"):
                    del font.attrib[attribute]
            element(run, "color", val="25221D")
            size = (
                "54"
                if key == "Title"
                else (
                    "34"
                    if key in {"Heading1", "Heading2"}
                    else "25" if key.startswith("Heading") else "21"
                )
            )
            element(run, "sz", val=size)
            paragraph = element(style, "pPr")
            borders = paragraph.find(f"{{{NS}}}pBdr")
            if borders is not None:
                paragraph.remove(borders)
            if key == "Title":
                element(paragraph, "spacing", before="0", after="280")
            elif not key.startswith("Heading"):
                element(paragraph, "spacing", after="140", line="288", lineRule="auto")
    parts["word/styles.xml"] = ET.tostring(
        styles, encoding="utf-8", xml_declaration=True
    )
    document = ET.fromstring(parts["word/document.xml"])
    section = document.find(f".//{{{NS}}}sectPr")
    if section is None:
        raise ValueError("Pandoc reference has no section properties")
    element(section, "pgSz", w="11906", h="16838")
    element(section, "pgMar", top="1020", bottom="1020", left="907", right="907")
    parts["word/document.xml"] = ET.tostring(
        document, encoding="utf-8", xml_declaration=True
    )
    with zipfile.ZipFile(
        ROOT / "report/reference.docx", "w", zipfile.ZIP_DEFLATED
    ) as output:
        for name, content in sorted(parts.items()):
            info = zipfile.ZipInfo(name, (2026, 10, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, content)


if __name__ == "__main__":
    main()
