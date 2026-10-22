"""Re-run the notebook and export its key results as slide-ready PDF figures.

Usage, from the repository root:  .venv/bin/python slides/make_figures.py   (about 5 minutes)
"""
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
os.environ["FIG_DIR"] = str(ROOT / "slides" / "figures")
Path(os.environ["FIG_DIR"]).mkdir(exist_ok=True)

nb = nbformat.read(ROOT / "src" / "bankruptcy_prediction.ipynb", as_version=4)
nb.cells.append(nbformat.v4.new_code_cell((ROOT / "slides" / "figures.py").read_text()))
NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(ROOT / "src")}}).execute()
print(nb.cells[-1].outputs[-1].get("text", ""))
