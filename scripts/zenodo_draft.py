#!/usr/bin/env python3
"""
zenodo_draft.py — Markdown → compiled PDF for Zenodo upload.

Usage:
  python3 zenodo_draft.py paper.md              # compile to paper.pdf
  python3 zenodo_draft.py paper.md --out out.pdf
  python3 zenodo_draft.py paper.md --open       # compile and open PDF
  python3 zenodo_draft.py paper.md --tex-only   # write .tex, don't compile

Input format (paper.md):
  ---
  title: "My Paper Title"
  date: 2026-06-03
  abstract: |
    Full abstract text (multi-line).
  keywords: [keyword1, keyword2]
  figures:
    - id: orbital_belnap
      type: belnap_lattice
      labels: {N: "empty", T: "spinUp", F: "spinDown", B: "paired"}
      caption: "OrbitalState ≅ Belnap FOUR"
    - id: profile
      type: primitive_profile
      tuple: "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z"
      title: "Frobenius fixed-point profile"
    - id: tier
      type: tier_chain
      highlight: O_∞
    - id: frob
      type: frobenius
  ---

  ## Introduction

  Body text here.  Reference figures as Figure~\ref{fig:orbital_belnap} etc.
  Use ~~~figure blocks to place a figure inline:

  ~~~figure
  orbital_belnap
  ~~~

Quick start:
  python3 zenodo_draft.py my_paper.md -y          # compile, auto-everything
  python3 zenodo_draft.py my_paper.pdf --live -y  # then upload (via zenodo_upload.py)
"""

import argparse
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml not installed — run: uv pip install pyyaml")

# ── chr(92) trick: avoids Write-tool backslash doubling ───────────────────────
_B = chr(92)   # single backslash — safe to embed in string literals


# ── LaTeX preamble ─────────────────────────────────────────────────────────────

def _build_preamble(title: str, date: str, abstract: str, keywords: list) -> str:
    """
    Build a complete LuaLaTeX preamble for an IG publication.
    Matches the style of undeciphered_texts_structural_analysis.tex, with Everson Mono
    added for Shavian notation.
    """
    kw_str = ", ".join(keywords) if keywords else "Imscribing Grammar"

    lines = [
        f"{_B}documentclass[12pt,a4paper]{{article}}",
        "",
        f"% Fonts — LuaLaTeX",
        f"{_B}usepackage{{fontspec}}",
        f"{_B}usepackage{{unicode-math}}",
        f"{_B}setmainfont{{FreeSerif}}",
        f"{_B}setmathfont{{Latin Modern Math}}",
        f"{_B}newfontfamily{_B}igprimfont{{FreeSerif}}",
        f"{_B}newfontfamily{_B}shavfont[Scale=1.0]{{Everson Mono}}",
        f"{_B}setmonofont[Scale=0.85]{{DejaVu Sans Mono}}",
        "",
        f"% Shavian Unicode block (U+10450–U+1047F) → Everson Mono automatically",
        f"% Works in text mode, inside \\text{{}} in math, and in table cells.",
        f"{_B}usepackage{{newunicodechar}}",
    ] + [
        # Mode-independent: works in text, \text{} in math, and bare math mode
        (f"{_B}newunicodechar{{{chr(0x10450 + i)}}}"
         f"{{{_B}ifmmode{_B}text{{{{{_B}shavfont {chr(0x10450 + i)}}}}}"
         f"{_B}else{{{{{_B}shavfont {chr(0x10450 + i)}}}}}{_B}fi}}")
        for i in range(48)
    ] + [
        "",
        f"% Page layout",
        f"{_B}usepackage[top=1in, bottom=1in, left=1in, right=1in]{{geometry}}",
        f"{_B}usepackage{{microtype}}",
        f"{_B}usepackage{{parskip}}",
        "",
        f"% Language",
        f"{_B}usepackage[english]{{babel}}",
        "",
        f"% Headers",
        f"{_B}usepackage{{fancyhdr}}",
        f"{_B}pagestyle{{fancy}}",
        f"{_B}fancyhf{{}}",
        f"{_B}fancyhead[L]{{{_B}leftmark}}",
        f"{_B}fancyhead[R]{{{_B}thepage}}",
        f"{_B}fancyfoot[C]{{{_B}thepage}}",
        f"{_B}renewcommand{{{_B}headrulewidth}}{{0.4pt}}",
        f"{_B}renewcommand{{{_B}footrulewidth}}{{0pt}}",
        "",
        f"% Section styling",
        f"{_B}usepackage{{titlesec}}",
        f"{_B}titleformat{{{_B}section}}{{{_B}Large{_B}bfseries}}{{}}{{0em}}{{}}",
        f"{_B}titleformat{{{_B}subsection}}{{{_B}large{_B}bfseries}}{{{_B}thesubsection}}{{1em}}{{}}",
        f"{_B}titleformat{{{_B}subsubsection}}{{{_B}normalsize{_B}bfseries}}{{{_B}thesubsubsection}}{{1em}}{{}}",
        f"{_B}renewcommand{{{_B}thesubsection}}{{{_B}arabic{{subsection}}}}",
        f"{_B}renewcommand{{{_B}thesubsubsection}}{{{_B}thesubsection.{_B}arabic{{subsubsection}}}}",
        "",
        f"% Essential packages",
        f"{_B}usepackage{{graphicx}}",
        f"{_B}setkeys{{Gin}}{{width=0.48{_B}linewidth,height=0.32{_B}textheight,keepaspectratio}}",
        f"{_B}usepackage[table]{{xcolor}}",
        f"{_B}usepackage{{booktabs}}",
        f"{_B}usepackage{{array}}",
        f"{_B}usepackage{{tabularx}}",
        f"{_B}usepackage{{longtable}}",
        f"{_B}usepackage{{amsmath}}",
        f"% unicode-math subsumes amssymb — do not load amssymb alongside it",
        f"{_B}usepackage{{float}}",
        f"{_B}usepackage[normalem]{{ulem}}",
        f"{_B}renewcommand{{{_B}arraystretch}}{{1.3}}",
        "",
        f"% Cross-references",
        f"{_B}usepackage{{hyperref}}",
        f"{_B}usepackage{{cleveref}}",
        f"{_B}hypersetup{{colorlinks=true, linkcolor=blue, urlcolor=cyan, citecolor=teal}}",
        "",
        f"% Custom commands",
        f"{_B}newcommand{{{_B}shav}}[1]{{{{{_B}shavfont #1}}}}",
        f"{_B}newcommand{{{_B}heb}}[1]{{{{{_B}igprimfont #1}}}}",
        f"{_B}newcommand{{{_B}tupleaddr}}[1]{{${_B}langle #1 {_B}rangle$}}",
        "",
        f"% Imscription tuple box",
        f"{_B}usepackage{{tcolorbox}}",
        f"{_B}tcbuselibrary{{skins,breakable}}",
        f"{_B}newtcolorbox{{imscriptionbox}}{{enhanced, colback=blue!5, colframe=blue!75!black,"
        f" fontupper={_B}large, center upper, boxrule=1pt, arc=4pt}}",
        "",
        f"% PDF metadata",
        f"{_B}hypersetup{{",
        f"  pdftitle={{{title}}},",
        f"  pdfkeywords={{{kw_str}}},",
        f"  pdfauthor={{Lando Mills}},",
        f"}}",
        "",
        f"{_B}title{{{title}}}",
        f"{_B}date{{{date}}}",
        f"{_B}author{{Lando Mills}}",
        "",
        f"{_B}begin{{document}}",
        f"{_B}maketitle",
        "",
    ]

    # Abstract
    if abstract.strip():
        lines += [
            f"{_B}begin{{abstract}}",
            abstract.strip(),
            f"{_B}end{{abstract}}",
            "",
        ]

    return "\n".join(lines)


def _build_postamble() -> str:
    return f"\n{_B}end{{document}}\n"


# ── Figure generation ──────────────────────────────────────────────────────────

_SCRIPTS_DIR = Path(__file__).parent


def _generate_figures(fig_specs: list, fig_dir: Path) -> dict:
    """
    Generate all figures declared in frontmatter.
    Returns {id: pdf_path} mapping.
    """
    if not fig_specs:
        return {}

    fig_dir.mkdir(parents=True, exist_ok=True)
    generated = {}

    try:
        # Import ig_figures as a module if available
        sys.path.insert(0, str(_SCRIPTS_DIR))
        import ig_figures as igf
    except ImportError:
        print("  WARNING: ig_figures.py not found — skipping figure generation")
        return {}

    for spec in fig_specs:
        fig_id   = spec.get("id", f"fig_{len(generated)}")
        fig_type = spec.get("type", "")
        out_path = str(fig_dir.resolve() / f"{fig_id}.pdf")

        try:
            if fig_type == "belnap_lattice":
                labels = spec.get("labels") or {}
                if isinstance(labels, dict):
                    pass  # already a dict from YAML
                igf.belnap_lattice(
                    labels=labels or None,
                    highlight=spec.get("highlight"),
                    caption=spec.get("caption", ""),
                    output=out_path,
                )
            elif fig_type == "primitive_profile":
                igf.primitive_profile(
                    tuple_str=spec.get("tuple", ""),
                    title=spec.get("title", ""),
                    output=out_path,
                )
            elif fig_type == "tier_chain":
                igf.tier_chain(
                    highlight=spec.get("highlight", "O_∞"),
                    output=out_path,
                )
            elif fig_type == "frobenius":
                igf.frobenius_triangle(output=out_path)
            elif fig_type == "bootstrap_loop":
                igf.bootstrap_loop(output=out_path)
            elif fig_type == "cetacean_scatter":
                igf.cetacean_scatter(output=out_path)
            else:
                print(f"  WARNING: unknown figure type '{fig_type}' for {fig_id}")
                continue

            generated[fig_id] = out_path
            print(f"  figure → {out_path}")

        except Exception as e:
            print(f"  WARNING: failed to generate {fig_id}: {e}")

    return generated


def _figure_latex(fig_id: str, fig_path: str, caption: str = "", label: str = "") -> str:
    """Return LaTeX for a \begin{figure} block."""
    label = label or fig_id
    cap_line = f"  {_B}caption{{{caption}}}\n" if caption else ""
    return (
        f"{_B}begin{{figure}}[htbp]\n"
        f"  {_B}centering\n"
        f"  {_B}includegraphics[width=0.85{_B}textwidth]{{{fig_path}}}\n"
        f"{cap_line}"
        f"  {_B}label{{fig:{label}}}\n"
        f"{_B}end{{figure}}\n"
    )


# ── Markdown → LaTeX body via pandoc ──────────────────────────────────────────

def _citeproc_flags(bibliography: "Path | None") -> list:
    """Return pandoc bibliography + citeproc flags, or [] if unavailable."""
    import shutil
    if not (bibliography and bibliography.exists()):
        return []
    bib = ["--bibliography", str(bibliography)]
    try:
        r = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        ver = r.stdout.split("\n")[0].split()[1].split(".")
        if (int(ver[0]), int(ver[1])) >= (2, 11):
            return bib + ["--citeproc"]
    except Exception:
        pass
    if shutil.which("pandoc-citeproc"):
        return bib + ["--filter", "pandoc-citeproc"]
    print("  INFO: no citeproc (pandoc < 2.11, no pandoc-citeproc) — bibliography skipped")
    return []


def _md_to_latex_body(md_text: str, tmp_dir: Path, bibliography: "Path | None" = None) -> str:
    """Convert markdown body to LaTeX using pandoc."""
    md_path  = tmp_dir / "_body.md"
    tex_path = tmp_dir / "_body.tex"

    md_path.write_text(md_text, encoding="utf-8")

    cmd = ["pandoc", str(md_path), "--from", "markdown+raw_tex", "--to", "latex", "--no-highlight",
           "-o", str(tex_path)] + _citeproc_flags(bibliography)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  pandoc error: {result.stderr}")
        sys.exit(1)

    return tex_path.read_text(encoding="utf-8")




# ── Image path resolution ────────────────────────────────────────────────────

def _resolve_image_paths(tex_body: str, source_dir: Path) -> str:
    """
    Rewrite relative \\includegraphics paths to be absolute (resolved against
    source_dir) so that lualatex can find images when compiling from a temp
    working directory. Absolute paths, http(s) URLs, and paths already starting
    with / are left unchanged.

    Also handles \\graphicspath{{}} and TEXINPUTS-style path resolution by
    resolving paths relative to source_dir first, then falling back to the
    original path if the file doesn't exist at the resolved location.

    Supports both: \\includegraphics[...]{{rel/path}} and
    \\includegraphics{{rel/path}}.
    """
    def _resolve(m):
        opts = m.group(1) or ''
        img_path = m.group(2).strip()

        # Skip absolutes, URLs, and paths already resolved
        if img_path.startswith('/') or img_path.startswith('http'):
            return m.group(0)

        # Resolve relative to source_dir
        resolved = (source_dir / img_path).resolve()
        if resolved.exists():
            return f'\\includegraphics{opts}{{{resolved}}}'

        # Fallback: return original (let LaTeX fail with a clear error)
        return m.group(0)

    tex_body = re.sub(
        r'\\includegraphics(\[[^\]]*\])?\{([^}]+)\}',
        _resolve,
        tex_body
    )
    return tex_body

# ── ~~~figure block substitution ──────────────────────────────────────────────

def _substitute_figure_blocks(tex_body: str, fig_specs: list, generated: dict) -> str:
    """
    Replace verbatim ~~~figure blocks in the pandoc output with actual LaTeX figure envs.
    pandoc renders ~~~figure ... ~~~ as a verbatim block; we intercept.
    """
    # pandoc renders fenced code blocks as \begin{verbatim}...\end{verbatim}
    # or as lstlisting. We look for the pattern and replace.
    def replacer(m):
        fig_id = m.group(1).strip()
        if fig_id not in generated:
            return f"% [figure {fig_id} not generated]\n"
        spec    = next((s for s in fig_specs if s.get("id") == fig_id), {})
        caption = spec.get("caption", "")
        return _figure_latex(fig_id, generated[fig_id], caption)

    # pandoc may render ~~~figure\nfig_id\n~~~ as \begin{verbatim} or as text
    # Try both patterns
    tex_body = re.sub(
        r"\\begin\{verbatim\}\s*(\w+)\s*\\end\{verbatim\}",
        replacer, tex_body
    )
    # Also handle if pandoc left it as raw text blocks
    tex_body = re.sub(
        r"\\begin\{lstlisting\}.*?\n(\w+)\n\\end\{lstlisting\}",
        replacer, tex_body, flags=re.DOTALL
    )
    return tex_body


# ── YAML frontmatter parsing ───────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Split YAML frontmatter from markdown body.
    Returns (meta_dict, body_text).
    """
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    fm_text  = text[3:end].strip()
    body     = text[end+4:].strip()
    meta     = yaml.safe_load(fm_text) or {}
    return meta, body


# ── Main pipeline ──────────────────────────────────────────────────────────────

def compile_pdf(md_path: Path, out_path: Path | None = None,
                tex_only: bool = False) -> Path:
    md_text = md_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(md_text)

    title    = meta.get("title", md_path.stem.replace("_", " ").title())
    date     = str(meta.get("date", "\\today"))
    abstract = meta.get("abstract", "")
    keywords = meta.get("keywords", [])
    fig_specs = meta.get("figures", [])

    if isinstance(abstract, dict):
        # YAML block scalar can come through oddly
        abstract = str(abstract)

    stem    = md_path.stem
    out_dir = md_path.parent
    tmp_dir = out_dir / f"_{stem}_build"
    tmp_dir.mkdir(exist_ok=True)

    fig_dir   = tmp_dir / "figures"
    generated = _generate_figures(fig_specs, fig_dir)

    bib_field = meta.get("bibliography")
    bib_path  = (md_path.parent / bib_field).resolve() if bib_field else None

    # Convert body
    print("  pandoc: converting body ...")
    tex_body = _md_to_latex_body(body, tmp_dir, bib_path)
    tex_body = _resolve_image_paths(tex_body, md_path.parent.resolve())
    tex_body = _substitute_figure_blocks(tex_body, fig_specs, generated)

    # Assemble
    preamble  = _build_preamble(title, date, abstract, keywords)
    postamble = _build_postamble()
    full_tex  = preamble + tex_body + postamble

    tex_out = tmp_dir / f"{stem}.tex"
    tex_out.write_text(full_tex, encoding="utf-8")
    print(f"  tex → {tex_out}")

    if tex_only:
        return tex_out

    # Compile with ltx
    ltx = Path.home() / ".local" / "bin" / "ltx"
    if not ltx.exists():
        ltx = Path("/usr/bin/lualatex")

    print(f"  compiling with {ltx.name} ...")
    result = subprocess.run(
        [str(ltx), str(tex_out.name)],
        capture_output=True, text=True,
        cwd=str(tmp_dir),
    )
    if result.returncode != 0:
        # Show last 30 lines of log for diagnostics
        log_path = tmp_dir / f"{stem}.log"
        if log_path.exists():
            lines = log_path.read_text(errors="replace").splitlines()
            print("  LaTeX errors (last 30 lines):")
            for l in lines[-30:]:
                print(f"    {l}")
        else:
            print(f"  lualatex stderr: {result.stderr[-800:]}")
        sys.exit(1)

    pdf_built = tmp_dir / f"{stem}.pdf"
    if not pdf_built.exists():
        sys.exit(f"Compilation succeeded but PDF not found at {pdf_built}")

    # Move to output location
    final = out_path or (out_dir / f"{stem}.pdf")
    import shutil
    shutil.copy2(str(pdf_built), str(final))
    print(f"  PDF  → {final}")
    return final


def main():
    p = argparse.ArgumentParser(
        description="Compile an IG markdown paper to a Zenodo-ready PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python3 zenodo_draft.py paper.md
              python3 zenodo_draft.py paper.md --out publications/paper.pdf
              python3 zenodo_draft.py paper.md --tex-only   # inspect .tex before compiling
              python3 zenodo_draft.py paper.md --open       # open after compile

            Then upload:
              python3 zenodo_upload.py paper.pdf -y --live
        """),
    )
    p.add_argument("input",     help="Markdown source file (.md)")
    p.add_argument("--out",     default=None, help="Output PDF path")
    p.add_argument("--tex-only", action="store_true",
                   help="Write .tex only, skip compilation")
    p.add_argument("--open",    action="store_true",
                   help="Open the PDF after compilation")

    args = p.parse_args()

    md_path = Path(args.input)
    if not md_path.exists():
        sys.exit(f"File not found: {md_path}")
    if md_path.suffix.lower() not in (".md", ".markdown"):
        sys.exit("Input must be a .md file")

    out_path = Path(args.out) if args.out else None

    import textwrap as _tw
    print(f"\n  IG draft compiler")
    print(f"  input  : {md_path}")
    print()

    result = compile_pdf(md_path, out_path, tex_only=args.tex_only)

    if args.open and not args.tex_only:
        opener = "xdg-open"
        subprocess.Popen([opener, str(result)])

    print(f"\n  done.")


if __name__ == "__main__":
    import textwrap
    main()
