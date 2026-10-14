"""Run the published supervisor verifier against its public data package."""

from pathlib import Path
import runpy
import sys

package = Path(__file__).resolve().parents[1] / "research/india-pakistan"
if "--root" not in sys.argv:
    sys.argv.extend(["--root", str(package)])
runpy.run_path(str(package / "tools/verify_edition.py"), run_name="__main__")
