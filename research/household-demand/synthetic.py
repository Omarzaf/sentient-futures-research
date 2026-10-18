"""Block placeholder values from the claim ledger, reports, D1 and model outputs.

Invented values carry the status flag below and live under ``synthetic/``. The
guard scans the publication surfaces for the flag as a whole uppercase word and
fails on any hit. A missing surface also fails, so a renamed file cannot make
the check pass by being absent.

Run ``python research/household-demand/synthetic.py --check`` from the library
root. Exit 0 means no hit; exit 1 lists each hit as ``path:line``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

__all__ = ["DEFAULT_SURFACES", "SYNTHETIC", "find_synthetic", "main"]

SYNTHETIC = "SYNTHETIC"

LIBRARY_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SURFACES: tuple[Path, ...] = (
    LIBRARY_ROOT / "research" / "india-pakistan" / "data" / "claims.csv",
    LIBRARY_ROOT / "research" / "india-pakistan" / "joint-report",
    LIBRARY_ROOT / "research" / "india-pakistan" / "report",
    LIBRARY_ROOT / "research" / "household-demand" / "outputs",
)

# Letters and digits on either side make a longer word; underscores, hyphens,
# punctuation and whitespace count as separators, so status_FLAG still hits.
_PATTERN = re.compile(rf"(?<![A-Za-z0-9]){SYNTHETIC}(?![A-Za-z0-9])")


def _files(path: Path) -> list[Path]:
    """Return the path itself or every file below it, sorted for stable output."""
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*") if p.is_file())
    raise FileNotFoundError(f"publication surface not found: {path}")


def _text_lines(path: Path) -> list[str] | None:
    """Read a text file as lines; return None for binary files (NUL bytes)."""
    data = path.read_bytes()
    if b"\x00" in data:
        return None
    return data.decode("utf-8", errors="replace").splitlines()


def find_synthetic(paths: list[Path]) -> list[str]:
    """Return ``path:line`` for every line holding the flag as a whole word."""
    hits: list[str] = []
    for root in paths:
        for path in _files(Path(root)):
            lines = _text_lines(path)
            if lines is None:
                continue
            for number, line in enumerate(lines, start=1):
                if _PATTERN.search(line):
                    hits.append(f"{path}:{number}")
    return hits


def _display(hit: str) -> str:
    """Show hits under the library root as relative paths."""
    prefix = f"{LIBRARY_ROOT}/"
    return hit.removeprefix(prefix)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point; exit 1 on any hit or missing surface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        required=True,
        help="scan the surfaces and exit 1 on any hit",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="surfaces to scan (default: the registered publication surfaces)",
    )
    args = parser.parse_args(argv)
    surfaces = list(args.paths) or list(DEFAULT_SURFACES)
    try:
        hits = find_synthetic(surfaces)
    except FileNotFoundError as error:
        print(f"synthetic guard: {error}", file=sys.stderr)
        return 1
    for hit in hits:
        print(_display(hit))
    if hits:
        print(
            f"synthetic guard: {len(hits)} line(s) carry the {SYNTHETIC} flag",
            file=sys.stderr,
        )
        return 1
    print(f"synthetic guard: {len(surfaces)} surface(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
