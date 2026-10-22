"""Build the LaTeX inputs of the LLM-assistance appendix (report/appendix/).

- files.tex   : INSTRUCTIONS.md and every AgentDiscussion/*.md file, rendered from Markdown with pandoc
- prompts.tex : the authors' prompts, verbatim, read from appendix/prompts.json
                (extracted from the Claude Code session transcript when its path is given)

Usage, from the repository root:
  uv run --isolated --no-project --with pypandoc-binary python report/build_appendix.py [session.jsonl]
"""
import json
import re
import sys
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "report" / "appendix"
OUT.mkdir(exist_ok=True)

FILES = [("INSTRUCTIONS.md", "Working rules and workflow, written by the authors")] + [
    (f"AgentDiscussion/step{k}/step{k}_{kind}.md", f"Step {k} {kind}: written by the LLM" + (", reviewed and edited by the authors" if kind == "plan" else ", reviewed by the authors"))
    for k in range(1, 5) for kind in ("plan", "recap")]

# Phase of each prompt, given by the number of its first prompt
PHASES = [(1, "Setup"), (3, "Step 1"), (6, "Step 2"), (11, "Step 3"), (13, "Step 4"), (16, "Final review"),
          (34, "Repository"), (38, "Slide deck"), (40, "Report"), (41, "Slide deck"), (43, "Appendix")]


def tex_escape(s):
    rep = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#",
           "^": r"\textasciicircum{}", "_": r"\_", "%": r"\%", "~": r"\textasciitilde{}"}
    s = re.sub(r"-(?=-)", "-{}", "".join(rep.get(ch, ch) for ch in s))   # keep "--" as typed, not as a dash
    return re.sub(r"(/|\?|=)(?=\S{12})", r"\1\\allowbreak{}", s)   # let long URLs break


SYMBOLS = {"ρ": r"\ensuremath{\rho}", "√": r"\ensuremath{\surd}", "←": r"\ensuremath{\leftarrow}",
           "→": r"\ensuremath{\rightarrow}", "−": r"\ensuremath{-}", "✔": r"\ensuremath{\checkmark}"}


def wrap_table(m):
    """Plain l/c/r tables: first column as is, the others wrap to the box width."""
    cols = m.group(1)
    spec = cols[0] + "".join(r">{\raggedright\arraybackslash}X" for _ in cols[1:])
    return f"\\begin{{tabularx}}{{\\linewidth}}{{@{{}}{spec}@{{}}}}{m.group(2)}\\end{{tabularx}}"


def markdown_to_tex(path):
    tex = pypandoc.convert_file(str(ROOT / path), "latex", format="gfm+tex_math_dollars-gfm_auto_identifiers",
                                extra_args=["--wrap=preserve"])
    for level, cmd in enumerate(["section", "subsection", "subsubsection", "paragraph"], 1):
        tex = tex.replace(f"\\{cmd}{{", f"\\mdh{{{level}}}{{")
    # longtable cannot sit inside a box: turn each table into a plain tabular (tables may be indented in lists)
    tex = re.sub(r"[ \t]*\\bottomrule\\noalign\{\}\n[ \t]*\\endlastfoot\n", "", tex)
    tex = re.sub(r"[ \t]*\\end(head|firsthead|foot)\n", "", tex)
    tex = re.sub(r"\\begin\{longtable\}\[\]\{@\{\}([lcr]+)@\{\}\}(.*?)\\end\{longtable\}", lambda m: wrap_table(m), tex, flags=re.S)
    tex = tex.replace("\\begin{longtable}[]", "\\begin{tabular}").replace("\\end{longtable}", "\\bottomrule\n\\end{tabular}")
    tex = tex.replace("\\end{tabularx}", "\\bottomrule\n\\end{tabularx}")
    # code blocks wrap long lines; symbols missing from the fonts are set in math, outside code blocks
    parts = re.split(r"(\\begin\{verbatim\}.*?\\end\{verbatim\})", tex, flags=re.S)
    for i in range(0, len(parts), 2):
        for ch, rep in SYMBOLS.items():
            parts[i] = parts[i].replace(ch, rep)
    tex = "".join(parts)
    return tex.replace("\\begin{verbatim}", "\\begin{Verbatim}[breaklines, fontsize=\\footnotesize]").replace("\\end{verbatim}", "\\end{Verbatim}")


def extract_prompts(transcript):
    prompts = []
    for line in open(transcript):
        d = json.loads(line)
        if d.get("type") != "user" or d.get("isMeta"):
            continue
        c = d["message"]["content"]
        if isinstance(c, list) and any(b.get("type") == "tool_result" for b in c):
            continue
        texts = [c] if isinstance(c, str) else [b.get("text", "") for b in c if b.get("type") == "text"]
        kept = [re.sub(r"<(ide_opened_file|ide_selection|system-reminder)>.*?</\1>", "", t, flags=re.S).strip() for t in texts]
        kept = [re.sub(r"</?pasted_content[^>]*>", "", t).strip() for t in kept if t and (not t.startswith("<") or t.startswith("<pasted"))]
        if not kept:
            continue
        if kept == ["[Request interrupted by user]"] and prompts:   # attach the interruption to the prompt it stopped
            prompts[-1]["text"] += " [Request interrupted by user]"
            continue
        prompts.append({"time": d["timestamp"][:16].replace("T", " ") + " UTC", "text": "\n".join(kept)})
    return prompts


if len(sys.argv) > 1:
    (OUT / "prompts.json").write_text(json.dumps(extract_prompts(sys.argv[1]), indent=1, ensure_ascii=False))
prompts = json.loads((OUT / "prompts.json").read_text())

lines = []
for i, p in enumerate(prompts, 1):
    phase = [name for start, name in PHASES if start <= i][-1]
    body = "\\par ".join(tex_escape(par.strip()).replace("\n", "\\newline ") for par in p["text"].split("\n\n") if par.strip())
    lines.append(f"\\promptentry{{{i}}}{{{phase}}}{{{p['time']}}}{{{body}}}")
(OUT / "prompts.tex").write_text("% Generated by build_appendix.py: the authors' prompts, verbatim\n" + "\n".join(lines) + "\n")

blocks = [f"\\begin{{mdfile}}{{{tex_escape(path)}}}{{{role}}}\n{markdown_to_tex(path)}\\end{{mdfile}}\n" for path, role in FILES]
(OUT / "files.tex").write_text("% Generated by build_appendix.py: INSTRUCTIONS.md and AgentDiscussion files rendered with pandoc\n" + "\n".join(blocks))
print(f"{len(prompts)} prompts, {len(FILES)} files written to {OUT}")
