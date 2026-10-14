"""Run the supervisor checker's ninety-six isolated synthetic corruptions."""

from pathlib import Path
import runpy

package = Path(__file__).resolve().parents[1] / "research/india-pakistan"
runpy.run_path(str(package / "tools/probes.py"), run_name="__main__")
