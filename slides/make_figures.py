"""Re-run the notebook and export its key results as slide-ready PDF figures.

Usage, from the repository root:  .venv/bin/python slides/make_figures.py [font]   (about 5 minutes)
  Arial (default) -> slides/figures/ for the slide deck;  "IBM Plex Sans" -> report/figures/ for the report
"""
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
FONT = sys.argv[1] if len(sys.argv) > 1 else "Arial"
OUT = ROOT / ("slides" if FONT == "Arial" else "report") / "figures"
os.environ["FIG_FONT"], os.environ["FIG_DIR"] = FONT, str(OUT)
Path(os.environ["FIG_DIR"]).mkdir(exist_ok=True)

nb = nbformat.read(ROOT / "src" / "bankruptcy_prediction.ipynb", as_version=4)
nb.cells.append(nbformat.v4.new_code_cell((ROOT / "slides" / "figures.py").read_text()))
NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(ROOT / "src")}}).execute()
print(nb.cells[-1].outputs[-1].get("text", ""))
