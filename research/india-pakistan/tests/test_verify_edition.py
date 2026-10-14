"""Independent semantic and corruption tests; no real research receipt is fabricated."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from decimal import InvalidOperation
from pathlib import Path
from unittest.mock import patch

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools"
SPEC = importlib.util.spec_from_file_location("supervisor_probes", TOOLS / "probes.py")
assert SPEC is not None and SPEC.loader is not None
p = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = p
SPEC.loader.exec_module(p)
v = p.v


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Supply a wholly synthetic file tree isolated from research deliverables."""
    result = tmp_path / "OUTPUTS" / "supervisor"
    p.fixture(result)
    return result


def test_all_ninety_six_independent_corruptions() -> None:
    """Every check must pass its baseline and reject eight different broken copies."""
    result = p.run_probes()
    assert result["caught"] == result["expected"] == 96
    assert result["per_check"] == {key: 8 for key in v.CHECK_IDS}


@pytest.mark.parametrize("raw", ["", "NaN", "Infinity", "-Infinity", " 3", "1,000"])
def test_numeric_unknowns_and_invalid_numbers_rejected(raw: str) -> None:
    """Unknown and malformed input cells must never become zero or a finite number."""
    with pytest.raises((v.InvalidEvidence, InvalidOperation)):
        v.decimal(raw)


@pytest.mark.parametrize("raw", ["a;b", "a|b", '["a","b"]'])
def test_source_id_serializations(raw: str) -> None:
    """Support the existing semicolon format and the explicit contract formats."""
    assert v.ids(raw) == ["a", "b"]


@pytest.mark.parametrize(
    "filters",
    [
        {"missing": "x"},
        {"country": {"regex": ".*"}},
        {"country": {"in": []}},
        {"country": 1},
        "__import__('os')",
    ],
)
def test_filter_language_has_no_implicit_or_executable_operations(
    filters: object,
) -> None:
    """Reject arbitrary expressions, type coercion and undefined selection columns."""
    with pytest.raises(v.InvalidEvidence):
        v.select([{"country": "Pakistan"}], filters)


def test_claim_rounding_is_decimal_half_up(root: Path) -> None:
    """A binary floating-point midpoint cannot silently change displayed rounding."""
    p.change_csv(root, "data/supply.csv", lambda data: data[0].update(value="2.675"))
    claim = v.Context(root).claims()["poultry-pakistan"]
    assert v.compute(v.Context(root), claim) == "2.68"


def test_mixed_dataset_derived_marker_cannot_inherit_A(root: Path) -> None:
    """A calculated row in a mixed observation table must remain derived."""
    data = v.rows(root / "data/supply.csv")
    for row in data:
        row["flag"] = ""
    data[0]["flag"] = "derived; production plus imports minus exports"
    p.save_csv(root / "data/supply.csv", data)
    with pytest.raises(v.InvalidEvidence, match="Derived dataset inherits"):
        v.c4(v.Context(root))


def test_derived_row_claim_cannot_become_headline(root: Path) -> None:
    """A mixed table does not confer observation status on a derived claim."""
    p.change_csv(root, "data/supply.csv", lambda data: data[0].update(tier="derived"))
    p.change_csv(root, "claims.csv", lambda data: data[0].update(tier="derived"))
    with pytest.raises(v.InvalidEvidence, match="Non-A/B headline"):
        v.c4(v.Context(root))


@pytest.mark.parametrize(
    "kind,text,expected",
    [
        ("year", "2026", True),
        ("year", "2024–25", True),
        ("year", "8720", False),
        ("date", "2026-02-30", False),
        ("date", "2026-10-13", True),
        ("chapter", "15", True),
        ("chapter", "16", False),
        ("constant", "100", False),
    ],
)
def test_number_allowances_are_scoped(kind: str, text: str, expected: bool) -> None:
    """Structural date allowances cannot legalize arbitrary research figures."""
    assert v.allowed_number(kind, text) is expected


def test_untraced_number_in_table_is_not_exempt(root: Path) -> None:
    """Only exact verified chart/source tables may bypass claim-span scanning."""
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text() + "\n| Study | Sample |\n| --- | --- |\n| A | 999 |\n"
    )
    with pytest.raises(v.InvalidEvidence, match="Untraced number"):
        v.c2(v.Context(root))


def test_real_png_crc_and_pixels_are_checked(root: Path) -> None:
    """Header-shaped bytes do not establish that an actual screenshot exists."""
    path = root / "logs/synthetic-report-page.png"
    assert v.png_size(path) == (595, 300)
    data = bytearray(path.read_bytes())
    data[-5] ^= 1
    path.write_bytes(data)
    with pytest.raises(v.InvalidEvidence, match="CRC"):
        v.png_size(path)


def test_skipped_library_check_cannot_pass(root: Path) -> None:
    """Diagnostic skipping must stay a visible failure, regardless of state labels."""
    (root / "STATE.json").write_text('{"status":"done","allow_blocked":true}')
    result = v.verify(root, ("C11",), skip_library=True)
    assert result["all_pass"] is False
    assert "skipped" in result["checks"]["C11"]["error"]


def test_missing_configuration_fails_every_check(tmp_path: Path) -> None:
    """Absence of real deliverables is never interpreted as an empty passing run."""
    result = v.verify(tmp_path)
    assert not result["all_pass"]
    assert len(result["checks"]) == 12
    assert not any(check["pass"] for check in result["checks"].values())


def test_style_stripping_preserves_authored_prose() -> None:
    """Strip code, URLs and tables but preserve words subject to the style rules."""
    sample = "Good prose.\n```js\nconst code = 999;\n```\n| Data | 100 |\n[The source](https://example.org/2026)\n"
    stripped = v.strip_prose(sample, False)
    assert "Good prose." in stripped and "The source" in stripped
    assert "999" not in stripped and "100" not in stripped and "2026" not in stripped


def test_local_style_detector_executes_real_patterns() -> None:
    """Exercise the actual installed detector rather than only mocked severity handling."""
    result = v.detector(
        "As an AI language model, I cannot provide personal opinions. Let's delve into the intricate tapestry and unlock its transformative potential."
    )
    assert result["issues"]
    assert any(
        issue.get("severity") in {"high", "critical", "medium"}
        for issue in result["issues"]
    )


def test_pandoc_ast_and_real_docx_preserve_table_text(tmp_path: Path) -> None:
    """Real Pandoc parsing excludes table borders while preserving every authored cell."""
    md = tmp_path / "sample.md"
    md.write_text(
        '# Measured supply\n\nProtein is [8.72]{.claim data-claim="p"} kg.\n\n| Country | Supply |\n| --- | ---: |\n| Pakistan | 8.72 |\n| India | 3.52 |\n'
    )
    ast = v.checked_run(
        ["pandoc", str(md), "--from=markdown+bracketed_spans", "--to=json"]
    )
    authored = v.normalized_text(v.ast_text(json.loads(ast)))
    docx = tmp_path / "sample.docx"
    v.checked_run(
        ["pandoc", str(md), "--from=markdown+bracketed_spans", "--output", str(docx)]
    )
    assert (
        authored
        == "Measured supply Protein is 8.72 kg. Country Supply Pakistan 8.72 India 3.52"
    )
    assert v.normalized_text(v.docx_text(docx)) == authored


def test_export_normalization_never_discards_numeric_differences() -> None:
    """Whitespace and ligature normalization cannot equate distinct research values."""
    assert v.normalized_text("8.72\nkg") == v.normalized_text("8.72 kg")
    assert v.normalized_text("8.72 kg") != v.normalized_text("8720 kg")
    assert v.normalized_text("Protein 5") != v.normalized_text("protein 5")


def test_library_commands_are_executed_not_accepted_from_receipt(root: Path) -> None:
    """An old success receipt cannot suppress a failing current command."""
    v.write_json(root / "logs/checks-library.json", {"pass": True, "no_drift": True})
    with p.external_mocks(root, {"fail_command": "verify.mjs"}) as calls:
        result = v.verify(root, ("C11",))
    assert result["checks"]["C11"]["pass"] is False
    assert ["node", "tools/verify.mjs"] in calls


def test_docx_privacy_scan_opens_xml(root: Path) -> None:
    """Private emails hidden in a compressed Word body must still be rejected."""
    path = root / "publication/report.docx"
    p.make_docx(path, "Private recipient person" + "@" + "example.org")
    v.write_json(
        root / "logs/publication-allowlist.json",
        {
            "files": [
                {
                    "path": "report.docx",
                    "sha256": v.sha(path),
                    "license": "Synthetic owner",
                }
            ]
        },
    )
    with p.external_mocks(root), pytest.raises(
        v.InvalidEvidence, match="Private/copyright-risk"
    ):
        v.c10(v.Context(root))


def test_command_failure_is_not_silently_ignored() -> None:
    """External process failure surfaces as a failed check, including stderr context."""
    failed = subprocess.CompletedProcess(["example"], 2, "", "Failure evidence")
    with patch.object(v, "run", return_value=failed), pytest.raises(
        v.InvalidEvidence, match="Failure evidence"
    ):
        v.checked_run(["example"])


def test_exact_source_cell_bindings_preserve_numeric_titles(root: Path) -> None:
    """Source titles retain their original digits without granting a blanket exemption."""
    p.change_csv(
        root,
        "data/sources.csv",
        lambda data: data[0].update(title="Protein survey 2023: Report 594"),
    )
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + '\n[Protein survey 2023: Report 594]{.source-cell data-source-id="official" data-source-column="title"}\n'
    )
    v.c2(v.Context(root))
    report.write_text(report.read_text().replace("Report 594", "Report 595"))
    with pytest.raises(v.InvalidEvidence, match="Source-cell prose differs"):
        v.c2(v.Context(root))


def test_source_code_publication_has_no_private_literals(root: Path) -> None:
    """Scan the actual checker/probe/test bytes without exempting Python source files."""
    candidates = [TOOLS / "verify_edition.py", TOOLS / "probes.py", Path(__file__)]
    files = []
    for source in candidates:
        target = root / "publication" / source.name
        target.write_bytes(source.read_bytes())
        files.append(
            {
                "path": target.name,
                "sha256": v.sha(target),
                "license": "Project-authored verification source",
            }
        )
    files.append(
        {
            "path": "README.md",
            "sha256": v.sha(root / "publication/README.md"),
            "license": "Project-authored synthetic fixture",
        }
    )
    v.write_json(root / "logs/publication-allowlist.json", {"files": files})
    with p.external_mocks(root):
        assert v.c10(v.Context(root))["allowlisted_files_scanned"] == 4


@pytest.mark.parametrize(
    ("content", "accepted"),
    [
        ("https://example.org/" + "ar" + "chive/paper.pdf", True),
        ("https://example.org/" + "AR" + "CHIVE/paper.pdf", True),
        ("./" + "AR" + "CHIVE/private.md", False),
        ("source: " + "ar" + "chive/private.md", False),
        ("https://localhost/" + "ar" + "chive/private.md", False),
        ("https://example.local/" + "ar" + "chive/private.md", False),
        ("https://example.org/" + "ar" + "chive/person" + "@" + "example.org", False),
        ("https://example.org/" + "ar" + "chive/Updated" + " Report.md", False),
    ],
)
def test_public_archive_urls_do_not_exempt_private_content(
    root: Path, content: str, accepted: bool
) -> None:
    """A public URL component is distinct from a local archive or sensitive content."""
    target = root / "publication/README.md"
    target.write_text(content)
    receipt = v.read_json(root / "logs/publication-allowlist.json")
    receipt["files"][0]["sha256"] = v.sha(target)
    v.write_json(root / "logs/publication-allowlist.json", receipt)
    with p.external_mocks(root):
        if accepted:
            v.c10(v.Context(root))
        else:
            with pytest.raises(v.InvalidEvidence, match="Private/copyright-risk"):
                v.c10(v.Context(root))


def test_real_pandoc_footnotes_are_detected_and_not_falsely_certified(
    tmp_path: Path,
) -> None:
    """Declare the exact-order supported citation route rather than silently reorder notes."""
    md = tmp_path / "notes.md"
    md.write_text(
        "Protein is 8.72 kg.[^source]\n\n[^source]: Original survey, 2023, table 5.\n"
    )
    ast = json.loads(v.checked_run(["pandoc", str(md), "--to=json"]))
    assert v.ast_has_note(ast) is True
    assert "8.72" in v.ast_text(ast) and "2023" in v.ast_text(ast)


def test_unlisted_extra_prose_cannot_escape_style_check(root: Path) -> None:
    """An authored report appendix receives the same style gate as the main text."""
    (root / "report/appendix.md").write_text("A missed—appendix.")
    with p.external_mocks(root), pytest.raises(v.InvalidEvidence, match="omitted"):
        v.c8(v.Context(root))


@pytest.mark.parametrize("numbered", [False, True])
def test_real_chromium_and_docx_exports_match_authored_table_text(
    root: Path, tmp_path: Path, numbered: bool
) -> None:
    """Exercise actual installed export tools on a small, source-span-bearing report."""
    module = (
        Path.home()
        / ".npm"
        / "_npx"
        / "86170c4cd1c5da32"
        / "node_modules"
        / "playwright"
    )
    browser = (
        Path.home()
        / "Library"
        / "Caches"
        / "ms-playwright"
        / "chromium-1234"
        / "chrome-mac-arm64"
        / "Google Chrome for Testing.app"
        / "Contents"
        / "MacOS"
        / "Google Chrome for Testing"
    )
    assert (
        module.is_dir() and browser.is_file()
    ), "Installed export tools must be available for this integration check"
    p.change_json(
        root,
        "verification-config.json",
        lambda data: data.update(
            exports={
                "pdf_engine": "chromium",
                "playwright_module": str(module),
                "chromium_executable": str(browser),
            }
        ),
    )
    (root / "report/REPORT.md").write_text(
        '# Measured supply\n\nProtein is [8.72]{.claim data-claim="p"} kg. [Official source](https://example.org).\n\n| Country | Supply |\n| --- | ---: |\n| Pakistan | 8.72 |\n| India | 3.52 |\n'
    )
    if numbered:
        css = root / "report-pagination.css"
        css.write_text("@page { margin: 20mm; } h2 { break-before: page; }")
        p.change_json(
            root,
            "verification-config.json",
            lambda data: data["exports"].update(
                page_numbers=True,
                css={"path": "report-pagination.css", "sha256": v.sha(css)},
            ),
        )
        report = root / "report/REPORT.md"
        report.write_text(
            report.read_text()
            + "\n\n## Second sheet\n\nThe second-page quantity remains 3.52 kg.\n"
        )
    scratch = tmp_path / "actual-export"
    scratch.mkdir()
    pdf, docx, authored = v.export_files(v.Context(root), scratch)
    expected = v.normalized_text(authored)
    assert v.normalized_text(v.docx_text(docx)) == expected
    assert v.normalized_text(v.report_pdf_text(v.Context(root), pdf)) == expected
    if numbered:
        raw_pdf_text = v.artifact_text(pdf)
        assert "Page 1 of 2" in raw_pdf_text and "Page 2 of 2" in raw_pdf_text


def test_external_script_resource_cannot_claim_self_contained_QA(root: Path) -> None:
    """A new network dependency fails even with a refreshed HTML receipt hash."""
    p.replace(
        root,
        "edition/index.html",
        "</head>",
        '<script src="https://example.org/library.js"></script></head>',
    )
    p.change_json(
        root,
        "logs/checks-browser.json",
        lambda data: data.update(html_sha256=v.sha(root / "edition/index.html")),
    )
    with p.external_mocks(root), pytest.raises(
        v.InvalidEvidence, match="external resource"
    ):
        v.c7(v.Context(root))


def test_frozen_proof_must_cover_each_check(root: Path) -> None:
    """A total count alone cannot conceal a missing check's corruption coverage."""
    v.write_json(
        root / "logs/checks-frozen.json",
        {"synthetic_probes_caught": 96, "per_check": {"C1": 96}},
    )
    result = v.final_gates(root)
    assert result and "eight corruptions per check" in result[0]


@pytest.mark.parametrize(
    ("field", "shown", "accepted"),
    [
        ("claim_id", "poultry-pakistan", True),
        ("value_column", "value", True),
        ("filter.year", "2023", True),
        ("filter.year", "2024", False),
        ("filter.absent", "missing", False),
        ("unit", "kg per person per year", False),
        ("value_column", "other", False),
    ],
)
def test_exact_claim_metadata_spans(
    root: Path, field: str, shown: str, accepted: bool
) -> None:
    """Appendix metadata binds exact allowed ledger fields, never arbitrary literals."""
    p.change_csv(
        root,
        "claims.csv",
        lambda data: data[0].update(filter_json='{"country":"Pakistan","year":"2023"}'),
    )
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + f'\n[{shown}]{{.claim-meta data-claim-meta="poultry-pakistan" data-claim-field="{field}"}}\n'
    )
    if accepted:
        v.c2(v.Context(root))
    else:
        with pytest.raises(v.InvalidEvidence):
            v.c2(v.Context(root))


def test_unknown_claim_metadata_id_is_rejected(root: Path) -> None:
    """Even nonnumeric metadata cannot claim a nonexistent ledger identity."""
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + '\n[value]{.claim-meta data-claim-meta="unknown" data-claim-field="value_column"}\n'
    )
    with pytest.raises(v.InvalidEvidence):
        v.c2(v.Context(root))


def test_claim_metadata_rejects_filter_objects(root: Path) -> None:
    """Membership objects are not scalar metadata exceptions."""
    p.change_csv(
        root,
        "claims.csv",
        lambda data: data[0].update(filter_json='{"country":{"in":["Pakistan"]}}'),
    )
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + '\n[Pakistan]{.claim-meta data-claim-meta="poultry-pakistan" data-claim-field="filter.country"}\n'
    )
    with pytest.raises(v.InvalidEvidence):
        v.c2(v.Context(root))


def test_markdown_source_span_decodes_entities_once(root: Path) -> None:
    """Escaped ampersands preserve exact registry titles with no numeric exemption."""
    p.change_csv(
        root, "data/sources.csv", lambda data: data[0].update(title="Food & meat 2023")
    )
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + '\n[Food &amp; meat 2023]{.source-cell data-source-id="official" data-source-column="title"}\n'
    )
    v.c2(v.Context(root))
    report.write_text(report.read_text().replace("&amp;", "&amp;amp;"))
    with pytest.raises(v.InvalidEvidence, match="Source-cell"):
        v.c2(v.Context(root))


def test_encoded_claim_numbers_match_only_after_one_decode(root: Path) -> None:
    """Encoded claim displays are checked; neither changed nor double-encoded values pass."""
    report = root / "report/REPORT.md"
    report.write_text(report.read_text().replace("[8.72]{.claim", "[&#56;.72]{.claim"))
    v.c2(v.Context(root))
    report.write_text(report.read_text().replace("&#56;", "&amp;#56;"))
    with pytest.raises(v.InvalidEvidence, match="Prose value"):
        v.c2(v.Context(root))


def test_unbound_encoded_number_is_rejected(root: Path) -> None:
    """Entity encoding does not create an escape from numeric traceability."""
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text() + "\nThe untraced sample is &#57;&#57;&#57;.\n"
    )
    with pytest.raises(v.InvalidEvidence, match="Untraced number"):
        v.c2(v.Context(root))


@pytest.mark.parametrize(
    ("extracted", "pages", "accepted"),
    [
        ("Protein 8.72 kg.\nPage 1 of 2\fSupply 3.52 kg.\nPage 2 of 2\f", 2, True),
        ("Protein 8.72 kg.\nPage 1 of 2\fSupply 3.52 kg.\nPage 2 of 2\f", 3, False),
        ("Protein 8.72 kg.\nPage 1 of 2\fSupply 3.52 kg.\f", 2, False),
        ("Protein 8.72 kg.\nPage 2 of 2\fSupply 3.52 kg.\nPage 1 of 2\f", 2, False),
        ("Protein 8.72 kg.\nPage 1 of 9\fSupply 3.52 kg.\nPage 2 of 9\f", 2, False),
        (
            "Protein 8.72 kg.\nPage 1 of 2\nExtra body text\fSupply 3.52 kg.\nPage 2 of 2\f",
            2,
            False,
        ),
        (
            "Protein 8.72 kg.\nPage 1 of 2\fSupply 3.52 kg.\nPage 2 of 2 extra\f",
            2,
            False,
        ),
    ],
)
def test_pdf_footer_validation(
    root: Path, extracted: str, pages: int, accepted: bool
) -> None:
    """Only exact final sequential footers may be removed from PDF body comparison."""
    p.change_json(
        root,
        "verification-config.json",
        lambda data: data["exports"].update(page_numbers=True),
    )
    with patch.object(v, "artifact_text", return_value=extracted), patch.object(
        v, "checked_run", return_value=f"Pages: {pages}\n"
    ):
        if accepted:
            body = v.report_pdf_text(v.Context(root), root / "report/report.pdf")
            assert v.normalized_text(body) == "Protein 8.72 kg. Supply 3.52 kg."
        else:
            with pytest.raises(v.InvalidEvidence):
                v.report_pdf_text(v.Context(root), root / "report/report.pdf")


def test_pdf_footer_removal_preserves_all_body_numbers(root: Path) -> None:
    """A legitimate page footer cannot hide a changed research value or body page phrase."""
    p.change_json(
        root,
        "verification-config.json",
        lambda data: data["exports"].update(page_numbers=True),
    )
    extracted = "Protein 8720 kg. Page 1 of 1 is also body text.\nPage 1 of 1\f"
    with patch.object(v, "artifact_text", return_value=extracted), patch.object(
        v, "checked_run", return_value="Pages: 1\n"
    ):
        body = v.report_pdf_text(v.Context(root), root / "report/report.pdf")
    assert "8720" in body and "Page 1 of 1 is also body text." in body
    assert v.normalized_text(body) != "Protein 8.72 kg. Page 1 of 1 is also body text."


def test_unnumbered_pdf_path_preserves_raw_text(root: Path) -> None:
    """Number removal is opt-in and cannot affect privacy extraction or ordinary PDFs."""
    with patch.object(v, "artifact_text", return_value="Body\nPage 1 of 1\f"):
        assert (
            v.report_pdf_text(v.Context(root), root / "report/report.pdf")
            == "Body\nPage 1 of 1\f"
        )


def test_numeric_claim_identity_is_exact_metadata(root: Path) -> None:
    """Ledger identity digits are metadata only when the whole ID matches exactly."""
    new_id = "poultry-2023-pakistan"
    p.change_csv(root, "claims.csv", lambda data: data[0].update(claim_id=new_id))
    for name in ("edition/index.html", "report/REPORT.md"):
        path = root / name
        path.write_text(path.read_text().replace("poultry-pakistan", new_id))
    report = root / "report/REPORT.md"
    report.write_text(
        report.read_text()
        + f'\n[{new_id}]{{.claim-meta data-claim-meta="{new_id}" data-claim-field="claim_id"}}\n'
    )
    v.c2(v.Context(root))
    report.write_text(
        report.read_text().replace(f"[{new_id}]", "[poultry-2024-pakistan]")
    )
    with pytest.raises(v.InvalidEvidence, match="metadata differs"):
        v.c2(v.Context(root))


@pytest.mark.parametrize(
    "sentence", ["Untraced sample 999.", "Untraced sample &lt;999&gt;."]
)
def test_package_closing_fence_cannot_swallow_next_paragraph(
    root: Path, sentence: str
) -> None:
    """Whitespace around a package fence never consumes the following numeric prose."""
    report = root / "report/REPORT.md"
    report.write_text(report.read_text() + "\n\n" + sentence + "\n")
    with pytest.raises(v.InvalidEvidence, match="Untraced number"):
        v.c2(v.Context(root))


def test_c12_rejects_body_number_change_with_valid_footer(
    root: Path, tmp_path: Path
) -> None:
    """C12 still rejects changed research values after accepting correct page footers."""
    p.change_json(
        root,
        "verification-config.json",
        lambda data: data["exports"].update(page_numbers=True),
    )
    existing = root / "report/report.pdf"
    existing.write_text("%PDF-1.7\nSynthetic report text 8720 kg.\nPage 1 of 1\f")
    generated_pdf = tmp_path / "regenerated.pdf"
    generated_pdf.write_text("%PDF-1.7\nSynthetic report text 8.72 kg.\nPage 1 of 1\f")
    generated_docx = root / "report/report.docx"
    with p.external_mocks(root), patch.object(
        v,
        "export_files",
        return_value=(generated_pdf, generated_docx, "Synthetic report text 8.72 kg."),
    ), pytest.raises(v.InvalidEvidence, match="existing_pdf"):
        v.c12(v.Context(root))


@pytest.mark.parametrize(
    ("content", "accepted"),
    [
        (
            "https://www.fao.org/statistics/highlights-archive/highlights-detail/food-balance-sheets-2010-2023/en",
            True,
        ),
        ("data/raw/sentiment_gdelt90_india_recovery/public-source.html", True),
        ("data/raw/highlights-archive/public-source.html", True),
        ("REC" + "OVERY/private-note.md", False),
        ("source: REC" + "OVERY/private-note.md", False),
        ("/AR" + "CHIVE/private-note.md", False),
        ('path="AR' + 'CHIVE/private-note.md"', False),
        ("file:///workspace/REC" + "OVERY/private-note.md", False),
    ],
)
def test_exact_private_directory_components(
    root: Path, content: str, accepted: bool
) -> None:
    """Public retrieval filenames are distinct from exact private workspace directories."""
    p.public_mutation(root, content)
    with p.external_mocks(root):
        if accepted:
            v.c10(v.Context(root))
        else:
            with pytest.raises(v.InvalidEvidence, match="Private/copyright-risk"):
                v.c10(v.Context(root))


@pytest.mark.parametrize(
    ("state", "accepted"),
    [
        ("unchanged", True),
        ("markdown", True),
        ("json", True),
        ("changed", False),
        ("missing", False),
        ("symlink", False),
        ("new_filename", False),
        ("suffix", False),
        ("traversal", False),
        ("absolute", False),
        ("wrong_namespace", False),
        ("private_alongside", False),
        ("payload", False),
    ],
)
def test_curated_archive_references_are_exact_and_hash_bound(
    root: Path, state: str, accepted: bool
) -> None:
    """Only immutable curated references qualify, never archive publication payloads."""
    reference = "research/halal-cultivated/" + "arch" + "ive/README.md"
    target = root / "publication" / reference
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("Synthetic reviewed lineage only.\n")
    bindings = {reference: v.sha(target)}
    content = reference
    if state == "markdown":
        content = f"[Lineage]({reference})"
    elif state == "json":
        content = json.dumps({"path": reference})
    elif state == "changed":
        target.write_text("Changed synthetic lineage.\n")
    elif state == "missing":
        target.unlink()
    elif state == "symlink":
        outside = root / "outside.txt"
        outside.write_text(target.read_text())
        target.unlink()
        target.symlink_to(outside)
    elif state == "new_filename":
        content = reference.replace("README.md", "new-secret.md")
    elif state == "suffix":
        content += ".private"
    elif state == "traversal":
        content = "../" + reference
    elif state == "absolute":
        content = "/" + reference
    elif state == "wrong_namespace":
        content = content.replace("halal-cultivated", "other-workstream")
    elif state == "private_alongside":
        content += " REC" + "OVERY/private.md"
    p.public_mutation(root, content, reference if state == "payload" else "README.md")
    with patch.object(
        v, "CURATED_PUBLIC_REFERENCES", bindings, create=True
    ), p.external_mocks(root):
        if accepted:
            v.c10(v.Context(root))
        else:
            with pytest.raises(v.InvalidEvidence):
                v.c10(v.Context(root))


@pytest.mark.parametrize(
    ("document", "prefix", "fragment", "accepted"),
    [
        ("sources/catalog.csv", "", "#HS-016", True),
        ("sources/index.html", "../", "", True),
        ("sources/index.html", "../", "#HS-016", True),
        ("sources/nested/index.html", "../../", "#HS-016", True),
        ("README.md", "../", "#HS-016", False),
        ("sources/index.html", "../../", "#HS-016", False),
        ("sources/nested/index.html", "../", "#HS-016", False),
        ("sources/index.html", "./../", "#HS-016", False),
        ("sources/index.html", "../", "#REC" + "OVERY/private.md", False),
        ("sources/catalog.csv", "", "#person" + "@example.org", False),
        ("sources/index.html", "../", "#API_" + "KEY=private", False),
    ],
)
def test_curated_links_resolve_from_actual_document_and_preserve_fragments(
    root: Path, document: str, prefix: str, fragment: str, accepted: bool
) -> None:
    """Relative links require their actual base; fragment content stays privacy-scanned."""
    reference = (
        "research/halal-cultivated/"
        + "arch"
        + "ive/discovery-pass/source-register.json"
    )
    target = root / "publication" / reference
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('[{"id":"HS-016","scope":"Synthetic reference only"}]\n')
    bindings = {reference: v.sha(target)}
    (root / "publication" / document).parent.mkdir(parents=True, exist_ok=True)
    link = prefix + reference + fragment
    content = f'<a href="{link}">Reference</a>' if document.endswith("html") else link
    p.public_mutation(root, content, document)
    if document != "README.md":
        p.change_json(
            root,
            "logs/publication-allowlist.json",
            lambda data: data["files"].append(
                {
                    "path": "README.md",
                    "sha256": v.sha(root / "publication/README.md"),
                    "license": "Author-owned synthetic fixture",
                }
            ),
        )
    with patch.object(v, "CURATED_PUBLIC_REFERENCES", bindings), p.external_mocks(root):
        if accepted:
            v.c10(v.Context(root))
        else:
            with pytest.raises(v.InvalidEvidence):
                v.c10(v.Context(root))
