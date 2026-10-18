"""Tests for the guard that keeps placeholder values off publication surfaces."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import synthetic

TOKEN = synthetic.SYNTHETIC


def test_flags_synthetic_in_claims(tmp_path: Path):
    claims = tmp_path / "claims.csv"
    claims.write_text(f"claim_id,value,status\nx,1.0,{TOKEN}\n")
    assert synthetic.find_synthetic([claims]) == [f"{claims}:2"]


def test_clean_file_passes(tmp_path: Path):
    report = tmp_path / "D1.md"
    report.write_text("India 2030: 241 million USD\n")
    assert synthetic.find_synthetic([report]) == []


def test_default_surfaces_cover_d1_and_claims():
    names = {p.name for p in synthetic.DEFAULT_SURFACES}
    assert {"claims.csv", "joint-report", "report"} <= names


def test_default_surfaces_include_household_outputs():
    parts = {p.parts[-2:] for p in synthetic.DEFAULT_SURFACES}
    assert ("household-demand", "outputs") in parts


def test_token_value():
    assert synthetic.SYNTHETIC == "S" + "YNTHETIC"


def test_whole_word_only(tmp_path: Path):
    f = tmp_path / "notes.md"
    f.write_text(
        "synthetic biology is lowercase\n"
        f"NON{TOKEN} is a longer word\n"
        f"{TOKEN}S is a longer word\n"
        f"status_{TOKEN} uses an underscore separator\n"
        f"({TOKEN})\n"
    )
    assert synthetic.find_synthetic([f]) == [f"{f}:4", f"{f}:5"]


def test_directories_scanned_recursively_in_sorted_order(tmp_path: Path):
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "deep").mkdir(parents=True)
    (tmp_path / "b" / "x.csv").write_text(f"{TOKEN}\n")
    (tmp_path / "a" / "deep" / "y.md").write_text(f"ok\n{TOKEN}\n")
    (tmp_path / "a" / "clean.md").write_text("ok\n")
    assert synthetic.find_synthetic([tmp_path]) == [
        f"{tmp_path / 'a' / 'deep' / 'y.md'}:2",
        f"{tmp_path / 'b' / 'x.csv'}:1",
    ]


def test_binary_files_are_skipped(tmp_path: Path):
    blob = tmp_path / "report.pdf"
    blob.write_bytes(b"%PDF\x00\x01" + TOKEN.encode() + b"\n")
    assert synthetic.find_synthetic([blob]) == []


def test_missing_surface_fails_closed(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        synthetic.find_synthetic([tmp_path / "absent.csv"])


def test_cli_exit_codes(tmp_path: Path):
    script = Path(synthetic.__file__)
    clean = tmp_path / "clean.md"
    clean.write_text("ok\n")
    dirty = tmp_path / "dirty.csv"
    dirty.write_text(f"a\n{TOKEN}\n")
    ok = subprocess.run(
        [sys.executable, str(script), "--check", str(clean)],
        capture_output=True,
        check=False,
        text=True,
    )
    bad = subprocess.run(
        [sys.executable, str(script), "--check", str(dirty)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert ok.returncode == 0
    assert bad.returncode == 1
    assert f"{dirty}:2" in bad.stdout + bad.stderr
