"""Build the LaTeX inputs of the LLM-assistance appendix (report/appendix/), rendered from Markdown with pandoc.

- instructions.tex : INSTRUCTIONS.md, in full
- excerpts.tex     : short excerpts of the AgentDiscussion plan and recap files

Usage, from the repository root:
  uv run --isolated --no-project --with pypandoc-binary python report/build_appendix.py
"""
import re
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report" / "appendix"
OUT.mkdir(exist_ok=True)

# (file, section heading, box label)
EXCERPTS = [
    ("AgentDiscussion/step1/step1_plan.md", "## 5. Points for you to confirm or change", "plan: open points, as edited during review"),
    ("AgentDiscussion/step3/step3_plan.md", "## 6. Points for you to confirm or change", "plan: decisions recorded after review"),
    ("AgentDiscussion/step3/step3_recap.md", "## Differences from the plan", "recap: what changed while coding"),
]

SYMBOLS = {"ρ": r"\ensuremath{\rho}", "√": r"\ensuremath{\surd}", "←": r"\ensuremath{\leftarrow}",
           "→": r"\ensuremath{\rightarrow}", "−": r"\ensuremath{-}", "✔": r"\ensuremath{\checkmark}"}


def markdown_to_tex(text):
    tex = pypandoc.convert_text(text, "latex", format="gfm+tex_math_dollars-gfm_auto_identifiers", extra_args=["--wrap=preserve"])
    for level, cmd in enumerate(["section", "subsection", "subsubsection", "paragraph"], 1):
        tex = tex.replace(f"\\{cmd}{{", f"\\mdh{{{level}}}{{")
    for ch, rep in SYMBOLS.items():   # symbols missing from the fonts are set in math
        tex = tex.replace(ch, rep)
    return tex


def section(path, heading):
    """Markdown of one section: from its heading to the next heading of the same or a higher level."""
    lines = (ROOT / path).read_text().splitlines()
    start = lines.index(heading)
    level = len(heading) - len(heading.lstrip("#"))
    end = next((i for i in range(start + 1, len(lines)) if re.match(rf"#{{1,{level}}} ", lines[i])), len(lines))
    return "\n".join(lines[start:end])


box = lambda path, label, tex: f"\\begin{{mdfile}}{{{path.replace('_', chr(92) + '_')}}}{{{label}}}\n{tex}\\end{{mdfile}}\n"
(OUT / "instructions.tex").write_text(box("INSTRUCTIONS.md", "full file", markdown_to_tex((ROOT / "INSTRUCTIONS.md").read_text())))
(OUT / "excerpts.tex").write_text("\n".join(box(p, f"excerpt, {label}", markdown_to_tex(section(p, h))) for p, h, label in EXCERPTS))
print(f"INSTRUCTIONS.md and {len(EXCERPTS)} excerpts written to {OUT}")
