#!/usr/bin/env python3
"""
gen_ig_reference.py — Imscribing Grammar Reference Compendium
Generates tex/IG_reference.tex and compiles to pdfs/IG_reference.pdf
"""

import subprocess
import sys
from pathlib import Path

B = chr(92)   # backslash — avoids Write-tool doubling
ROOT = Path(__file__).parent.parent
TEX  = ROOT / "tex"  / "IG_reference.tex"
PDF  = ROOT / "pdfs" / "IG_reference.pdf"
FIG  = ROOT / "markdown" / "iam" / "_IMASM_lifted_build" / "figures"
SCRIPTS = ROOT / "scripts"


# ── Pre-generate any missing figures ──────────────────────────────────────────

def gen_figures():
    needed = {
        "tier.pdf":      ["tier",    "--highlight", "O_∞"],
        "frobenius.pdf": ["frobenius"],
        "belnap.pdf":    ["belnap", "--labels", "N:Neither (⊥),T:True,F:False,B:Both (⊤)"],
        "bootstrap.pdf": ["bootstrap"],
    }
    FIG.mkdir(parents=True, exist_ok=True)
    for fname, args in needed.items():
        out = FIG / fname
        if not out.exists():
            subprocess.run(
                ["python3", str(SCRIPTS / "ig_figures.py")] + args + ["--out", str(out)],
                check=False
            )


# ── Color / glyph data ────────────────────────────────────────────────────────

# (glyph, name, n_subtypes, subtype_list, genetic_aa)
PRIMITIVES = [
    ("⊢", "Dimensionality", 4, ["ß","C",";","ω"],   "Gly"),
    ("⊣", "Topology",       5, ["6","K","ò","¨","O"],"Pro"),
    (">", "Recognition",    4, ["¯","ý","Ť","="],    "His"),
    ("<", "Parity",         5, ["ɐ","υ","F","˙","}"],"Leu"),
    ("⋈", "Fidelity",       3, ["ì","ð","ż"],         "Ile"),
    ("⊤", "Kinetics",       5, ["-","W","@","Ù","λ"], "Val"),
    ("∈", "Granularity",    3, ["β","γ","ʔ"],         "Thr"),
    ("∋", "Coupling",       4, ["∧","˝","ˌ","Ş"],     "Ser"),
    ("⊙", "Criticality",    5, ["ž","ÿ","Æ","3","Ţ"], "Cys"),
    ("⊥", "Chirality",      4, ["Ñ","£","A","!"],     "Gln"),
    ("⊞", "Stoichiometry",  3, ["S","ő","ï"],          "Ala"),
    ("◻", "Winding",        4, ["Å","2","z","5"],      "Arg"),
]

# colour by subtype count: 3→green, 4→blue, 5→purple
GROUP_COL = {3: "g3col", 4: "g4col", 5: "g5col"}

MILESTONE_COLS = {
    "RH":    "#4472C4",
    "YM":    "#9370DB",
    "Hodge": "#C07070",
    "NS":    "#70B070",
    "PNP":   "#CC8800",
    "BSD":   "#DC143C",
    "OPN":   "#70B0D0",
}


# ── LaTeX preamble ─────────────────────────────────────────────────────────────

def preamble() -> str:
    lines = [
        f"{B}documentclass[10pt,a4paper]{{article}}",
        "",
        f"% Fonts",
        f"{B}usepackage{{fontspec}}",
        f"{B}usepackage{{unicode-math}}",
        f"{B}setmainfont{{FreeSerif}}",
        f"{B}setmathfont{{Latin Modern Math}}",
        f"{B}newfontfamily{B}shavfont[Scale=1.0]{{Everson Mono}}",
        f"{B}setmonofont[Scale=0.82]{{DejaVu Sans Mono}}",
        "",
        f"% Shavian block → Everson Mono",
        f"{B}usepackage{{newunicodechar}}",
    ] + [
        # The twelve primitive marks, likewise. FreeSerif has neither the
        # turnstiles nor the tacks nor the box, and unicode-math only rescues
        # the ones that are math operators: ◻ is a geometric shape and came out
        # as a missing-glyph box in the Winding row.
        (f"{B}newunicodechar{{{g}}}"
         f"{{{B}ifmmode{B}text{{{{{B}shavfont {g}}}}}"
         f"{B}else{{{{{B}shavfont {g}}}}}{B}fi}}")
        for g in "⊢⊣⋈⊤∈∋⊙⊥⊞◻"
    ] + [
        (f"{B}newunicodechar{{{chr(0x10450+i)}}}"
         f"{{{B}ifmmode{B}text{{{{{B}shavfont {chr(0x10450+i)}}}}}"
         f"{B}else{{{{{B}shavfont {chr(0x10450+i)}}}}}{B}fi}}")
        for i in range(48)
    ] + [
        "",
        f"% Layout",
        f"{B}usepackage[top=1.1cm, bottom=1.1cm, left=1.1cm, right=1.1cm]{{geometry}}",
        f"{B}usepackage{{microtype}}",
        f"{B}usepackage{{parskip}}",
        f"{B}setlength{{{B}parskip}}{{3pt}}",
        f"{B}setlength{{{B}parindent}}{{0pt}}",
        "",
        f"% Packages",
        f"{B}usepackage{{multicol}}",
        f"{B}usepackage{{booktabs}}",
        f"{B}usepackage[table]{{xcolor}}",
        f"{B}usepackage{{array}}",
        f"{B}usepackage{{tabularx}}",
        f"{B}usepackage{{amsmath}}",
        f"{B}usepackage{{amssymb}}",
        f"{B}usepackage{{graphicx}}",
        f"{B}usepackage{{float}}",
        f"{B}usepackage{{tcolorbox}}",
        f"{B}tcbuselibrary{{skins,breakable}}",
        f"{B}usepackage{{tikz}}",
        f"{B}usetikzlibrary{{positioning,arrows.meta,shapes,fit,calc,backgrounds,decorations.pathmorphing}}",
        f"{B}usepackage{{hyperref}}",
        f"{B}hypersetup{{colorlinks=true,linkcolor=blue,urlcolor=teal,pdfborder={{0 0 0}}}}",
        f"{B}usepackage{{fancyhdr}}",
        f"{B}usepackage{{titlesec}}",
        f"{B}titleformat{{{B}section}}{{{B}large{B}bfseries{B}color{{hdrblue}}}}{{}}{{}}{{}}{B}vspace{{-4pt}}",
        f"{B}titleformat{{{B}subsection}}{{{B}normalsize{B}bfseries}}{{}}{{}}{{}}{B}vspace{{-3pt}}",
        "",
        f"% Colours",
        f"{B}definecolor{{hdrblue}}{{HTML}}{{1A2A5E}}",
        f"{B}definecolor{{g3col}}{{HTML}}{{1B5E20}}",   # 3-subtype: deep green
        f"{B}definecolor{{g4col}}{{HTML}}{{1A237E}}",   # 4-subtype: deep blue
        f"{B}definecolor{{g5col}}{{HTML}}{{4A0072}}",   # 5-subtype: deep purple
        f"{B}definecolor{{accentcol}}{{HTML}}{{9370DB}}",
        f"{B}definecolor{{frobcol}}{{HTML}}{{C06000}}",
        f"{B}definecolor{{tier0col}}{{HTML}}{{4472C4}}",
        f"{B}definecolor{{tier1col}}{{HTML}}{{CC8800}}",
        f"{B}definecolor{{tier2col}}{{HTML}}{{E05800}}",
        f"{B}definecolor{{tier2dcol}}{{HTML}}{{CC1133}}",
        f"{B}definecolor{{tierinfcol}}{{HTML}}{{7700CC}}",
        f"{B}definecolor{{bgstrip}}{{HTML}}{{F0F0F8}}",
        "",
        f"% Boxes",
        f"{B}newtcolorbox{{axiombox}}{{enhanced,colback=frobcol!8,colframe=frobcol!70,"
        f"boxrule=1pt,arc=3pt,left=4pt,right=4pt,top=3pt,bottom=3pt}}",
        f"{B}newtcolorbox{{headerbox}}{{enhanced,colback=hdrblue,colframe=hdrblue,"
        f"boxrule=0pt,arc=0pt,left=6pt,right=6pt,top=4pt,bottom=4pt}}",
        f"{B}newtcolorbox{{sectionbox}}[1]{{enhanced,colback=#1!8,colframe=#1!60,"
        f"boxrule=0.6pt,arc=2pt,left=3pt,right=3pt,top=2pt,bottom=2pt}}",
        "",
        f"% Commands",
        f"{B}newcommand{{{B}shav}}[1]{{{{{B}shavfont #1}}}}",
        f"{B}newcommand{{{B}prim}}[1]{{{B}textbf{{#1}}}}",
        f"{B}newcommand{{{B}craddr}}[1]{{{{\\small\\texttt{{#1}}}}}}",
        f"{B}renewcommand{{{B}arraystretch}}{{1.25}}",
        "",
        f"% No page numbers on reference sheet",
        f"{B}pagestyle{{empty}}",
        "",
        f"{B}begin{{document}}",
    ]
    return "\n".join(lines)


# ── Page 1: Primitives + Axioms ────────────────────────────────────────────────

def page1() -> str:
    # Build primitive table rows
    rows = []
    for glyph, name, n, subs, aa in PRIMITIVES:
        col = GROUP_COL[n]
        sub_str = " ".join(f"\\textsubscript{{{s}}}" if len(s)==1 else s for s in subs)
        sub_str = ", ".join(f"\\texttt{{{s}}}" for s in subs)
        rows.append(
            f"    {B}rowcolor{{{col}!12}}"
            f"{B}textcolor{{{col}}}{{{B}textbf{{{B}large {glyph}}}}} & "
            f"{B}textcolor{{{col}}}{{{B}textbf{{{name}}}}} & "
            f"{n} & "
            f"{B}texttt{{{B}small {', '.join(subs)}}} & "
            f"{B}textit{{{B}small {aa}}} {B}{B}"
        )

    prim_table = (
        f"  {B}begin{{tabular}}{{@{{}}c l c l c@{{}}}}\n"
        f"  {B}toprule\n"
        f"  {B}textbf{{Glyph}} & {B}textbf{{Name}} & {B}textbf{{n}} & "
        f"{B}textbf{{Subtypes}} & {B}textbf{{AA}} {B}{B}\n"
        f"  {B}midrule\n"
        + "\n".join(rows) + "\n"
        f"  {B}bottomrule\n"
        f"  {B}end{{tabular}}"
    )

    crystal_box = "\n".join([
        f"  {B}begin{{axiombox}}",
        f"  {B}centering",
        f"  {{\\large\\bfseries Crystal of Types}}\\\\[4pt]",
        f"  ${{\\color{{g3col}} 3^3}} {B}times {{\\color{{g4col}} 4^5}} {B}times {{\\color{{g5col}} 5^4}}$",
        f"  $= 27 {B}times 1024 {B}times 625 = {B}mathbf{{17{B},{B},280{B},{B},000}}$ types\\\\[3pt]",
        # Read off PRIMITIVES rather than restated. The hand-written copy was
        # still naming the retired alphabet after the table above had moved.
        f"  {{\\small\\color{{g3col}} 3-subtype:}} {{\\small {' '.join(g for g,_,n,_,_ in PRIMITIVES if n==3)}}} "
        f"$\\cdot$ {{\\small\\color{{g4col}} 4-subtype:}} {{\\small {' '.join(g for g,_,n,_,_ in PRIMITIVES if n==4)}}} "
        f"$\\cdot$ {{\\small\\color{{g5col}} 5-subtype:}} {{\\small {' '.join(g for g,_,n,_,_ in PRIMITIVES if n==5)}}}",
        f"  {B}end{{axiombox}}",
    ])

    cat_desc = "\n".join([
        f"{{\\small\\bfseries\\color{{hdrblue}} Category-Theoretic Description}}\\\\[2pt]",
        f"{{\\small The Imscribing Grammar is the {B}textbf{{free special symmetric",
        f"$\\dagger$-Frobenius algebra}} on 12 generators in a {B}textbf{{FOUR-enriched",
        f"traced symmetric monoidal category}}, with $\\mu{B}circ{B}delta={B}mathrm{{id}}$",
        f"as founding axiom (ZFC\\textsubscript{{fe}}).}}\\\\[4pt]",
        f"{{\\small\\bfseries Ambient category:}} {{\\small $\\mathcal{{C}}$ enriched over",
        f"Belnap-Dunn bilattice FOUR $= {{N, T, F, B}}$; ex falso ($B{B}to{B}bot$) blocked.}}\\\\[2pt]",
        f"{{\\small\\bfseries Generators:}} {{\\small 12 primitive endomorphisms of monoidal unit $I$",
        f"(scalars). Commutativity follows from SMC coherence.}}\\\\[2pt]",
        f"{{\\small\\bfseries Spider theorem:}} {{\\small Any two {B}emph{{connected}} Frobenius diagrams",
        f"with same boundary $=$ same morphism.}}\\\\[2pt]",
        f"{{\\small\\bfseries O$_\\infty$ fixpoint:}} {{\\small $\\omega{B}circ{B}omega={B}omega$",
        f"at $\\odot$ gate; initial algebra of $(-)\\circ(-)$ on End$(I)$.}}",
    ])

    frobenius_box = "\n".join([
        f"  {B}begin{{axiombox}}",
        f"  {B}centering",
        f"  {{\\LARGE\\bfseries\\color{{frobcol}} $\\mu{B}circ{B}delta = {B}mathrm{{id}}$}}\\\\[3pt]",
        f"  {{\\small\\itshape The founding axiom. Vessel splits (${B}delta$), fills, returns whole ($\\mu$).}}\\\\[3pt]",
        f"  {{\\small ZFC\\textsubscript{{fe}}:}} $\\mu{B}circ{B}delta={B}mathrm{{id}}$ as set-formation axiom",
        f"  $\\Rightarrow$ ZFC Separation as theorem. Strictly: ZFC $\\subset$ ZFC\\textsubscript{{t}} $\\subset$ ZFC\\textsubscript{{fe}}.",
        f"  {B}end{{axiombox}}",
    ])

    zfc_table = "\n".join([
        f"{{\\small",
        f"\\begin{{tabular}}{{@{{}}lll@{{}}}}",
        f"\\toprule",
        f"\\textbf{{Theory}} & \\textbf{{Foundation}} & \\textbf{{Status}} \\\\",
        f"\\midrule",
        f"ZFC & Separation axiom & Classical \\\\",
        f"ZFC\\textsubscript{{t}} & Temporal consistency & Intermediate \\\\",
        f"ZFC\\textsubscript{{fe}} & $\\mu{B}circ{B}delta={B}mathrm{{id}}$ & {B}textbf{{Active}} \\\\",
        f"\\bottomrule",
        f"\\end{{tabular}}}}",
    ])

    return "\n".join([
        f"",
        f"% ─── PAGE 1 ─────────────────────────────────────────────────────────────────",
        f"",
        f"{B}begin{{headerbox}}",
        f"  {{\\Large\\bfseries\\color{{white}} THE IMSCRIBING GRAMMAR}}",
        f"  {B}hfill",
        f"  {{\\normalsize\\color{{white!80!hdrblue}} Reference Compendium {B}textbullet{{}} 2026}}",
        f"{B}end{{headerbox}}",
        f"",
        f"{B}vspace{{4pt}}",
        f"{B}begin{{multicols}}{{2}}",
        f"",
        f"  {B}section*{{The 12 Primitives}}",
        f"  {{\\footnotesize Colour: {{\\color{{g3col}}$\\blacksquare$}} 3-subtype ·",
        f"  {{\\color{{g4col}}$\\blacksquare$}} 4-subtype ·",
        f"  {{\\color{{g5col}}$\\blacksquare$}} 5-subtype; AA = genetic amino acid bijection}}",
        f"  {B}vspace{{3pt}}",
        prim_table,
        f"",
        f"  {B}vspace{{6pt}}",
        crystal_box,
        f"",
        f"  {B}columnbreak",
        f"",
        f"  {B}section*{{Categorical Foundation}}",
        cat_desc,
        f"",
        f"  {B}vspace{{5pt}}",
        frobenius_box,
        f"",
        f"  {B}vspace{{5pt}}",
        f"  {B}section*{{ZFC Hierarchy}}",
        zfc_box := zfc_table,
        f"",
        f"  {B}vspace{{4pt}}",
        f"  {B}section*{{Belnap FOUR / Tier Chain}}",
        f"  {B}begin{{minipage}}[t]{{0.46{B}linewidth}}",
        f"    {B}includegraphics[width={B}linewidth]{{{str(FIG/'belnap.pdf')}}}",
        f"  {B}end{{minipage}}{B}hfill",
        f"  {B}begin{{minipage}}[t]{{0.50{B}linewidth}}",
        f"    {B}includegraphics[width={B}linewidth]{{{str(FIG/'tier.pdf')}}}",
        f"  {B}end{{minipage}}",
        f"",
        f"{B}end{{multicols}}",
        f"",
        f"{B}newpage",
    ])


# ── Page 2: Mathematics ────────────────────────────────────────────────────────

def page2() -> str:

    # Millennium table
    mpp = [
        ("Riemann Hypothesis",   "RH",    "6,738,803", "𐑫",  "Zero on critical line ∧ off critical line"),
        ("Yang--Mills",          "YM",    "6,738,803", "𐑫",  "Mass gap exists ∧ does not exist"),
        ("Hodge Conjecture",     "Hodge", "6,738,803", "𐑫",  "Hodge cycle algebraic ∧ non-algebraic"),
        ("Navier--Stokes",       "NS",    "6,738,803", "𐑫",  "Smooth solution ∧ finite-time blowup"),
        ("P vs NP",              "PNP",   "6,738,803", "𐑫",  "P = NP ∧ P $\\neq$ NP"),
        ("Birch--Swinnerton-Dyer","BSD",  "6,738,800", "𐑖",  "Rank analytic ∧ arithmetic (BSD $\\neq$ others)"),
        ("Odd Perfect Number",   "OPN",   "6,738,803", "𐑫",  "Perfect ∧ non-perfect (mod $\\Omega$ topology)"),
    ]

    mpp_rows = []
    for full, short, addr, chir, barrier in mpp:
        chir_latex = chir.replace("_!", "_{!}").replace("_A", "_{A}")
        mpp_rows.append(
            f"    {full} & {B}craddr{{{addr}}} & "
            f"${chir_latex}$ & "
            f"{{\\scriptsize {barrier}}} {B}{B}"
        )

    mpp_table = "\n".join([
        f"  {B}begin{{tabular}}{{@{{}} l l c p{{4.5cm}} @{{}}}}",
        f"  {B}toprule",
        f"  {B}textbf{{Problem}} & {B}textbf{{Address}} & {B}textbf{{Ħ}} & {B}textbf{{Barrier (B-state)}} {B}{B}",
        f"  {B}midrule",
    ] + mpp_rows + [
        f"  {B}bottomrule",
        f"  {B}end{{tabular}}",
    ])

    # Genetic code bijection table
    gen_rows = []
    for glyph, name, _, _, aa in PRIMITIVES:
        gen_rows.append(
            f"    {B}textbf{{{glyph}}} {name} & {B}textit{{{aa}}} {B}{B}"
        )

    gen_table = "\n".join([
        f"  {B}begin{{tabular}}{{@{{}} l l @{{}}}}",
        f"  {B}toprule",
        f"  {B}textbf{{Primitive}} & {B}textbf{{Amino Acid}} {B}{B}",
        f"  {B}midrule",
    ] + gen_rows + [
        f"  {B}bottomrule",
        f"  {B}end{{tabular}}",
    ])

    return "\n".join([
        f"% ─── PAGE 2 ─────────────────────────────────────────────────────────────────",
        f"",
        f"{B}begin{{headerbox}}",
        f"  {{\\Large\\bfseries\\color{{white}} MATHEMATICAL SCOPE}}",
        f"  {B}hfill{{\\normalsize\\color{{white!80!hdrblue}} Formalization · Millennium · Genetic Code}}",
        f"{B}end{{headerbox}}",
        f"",
        f"{B}vspace{{4pt}}",
        f"{B}begin{{multicols}}{{2}}",
        f"",
        f"  {B}section*{{Millennium Prize Resolution}}",
        f"  {{\\small All 7 Clay Millennium Problems + OPN resolved as Belnap-B dialetheias at tier",
        f"  O$_\\infty$ (Crystal address $\\approx 6.74{B}times 10^6$).",
        f"  BSD occupies distinct address due to Ħ\\textsubscript{{A}} vs Ħ\\textsubscript{{!}} chirality.",
        f"  Gate: $\\Phi_{{\\textbraceleft\\textbraceright}}$ (Frobenius-special parity) governs O$_{{2{B}dagger}} {B}to$ O$_{{\\infty}}$ crossing.",
        f"  Lean 4 kernel fork disables ex falso; 0 sorries; 167 modules.}}",
        f"  {B}vspace{{3pt}}",
        mpp_table,
        f"",
        f"  {B}vspace{{5pt}}",
        f"  {B}begin{{axiombox}}",
        f"  {{\\small\\bfseries\\color{{frobcol}} OS Imscription — Universal Structural Floor}}\\\\[3pt]",
        f"  $\\langle 1, 3, 2, 4, 2, 1, 2, 2, 1, 2, 2, 2 {B}rangle$\\\\[2pt]",
        f"  {{\\scriptsize MEET(Hebrew, Sanskrit, Egyptian, Cuneiform, Basque) = MEET(Linear A) = OS.",
        f"  Linear A distance $d = 0.00$. Emerald Tablet: $C = 1.0$, both gates open.}}",
        f"  {B}end{{axiombox}}",
        f"",
        f"  {B}vspace{{4pt}}",
        f"  {B}includegraphics[width=0.72{B}linewidth]{{{str(FIG/'frob.pdf')}}}",
        f"",
        f"  {B}columnbreak",
        f"",
        f"  {B}section*{{Genetic Code Bijection}}",
        f"  {{\\small The 64-codon table partitions the Crystal: $17{B},{B}280{B},{B}000 {B}div 64 = 270{B},{B}000$",
        f"  (fiber per codon = $3^3 {B}times 4^2 {B}times 5^4$, zero remainder).",
        f"  12 promoted amino acids biject exactly to the 12 IG primitives.}}",
        f"  {B}vspace{{3pt}}",
        gen_table,
        f"",
        f"  {B}vspace{{5pt}}",
        f"  {B}begin{{sectionbox}}{{tier0col}}",
        f"  {{\\small\\bfseries Nucleotide $\\to$ Belnap FOUR}}\\\\[2pt]",
        f"  {{\\small G $=$ B (Both · paired) $\\cdot$ C $=$ T (True · Watson-Crick)}}\\\\",
        f"  {{\\small A $=$ F (False · complementary) $\\cdot$ U $=$ N (Neither · wobble)}}\\\\[2pt]",
        f"  {{\\scriptsize Wobble hierarchy: G·C pairing is strict (T); G·U wobble occupies B;",
        f"  A·U anti is F; U alone is N. Watson-Crick complement $\\neq$ Belnap negation (proved).}}",
        f"  {B}end{{sectionbox}}",
        f"",
        f"  {B}vspace{{5pt}}",
        f"  {B}section*{{IMASM Bootstrap Loop}}",
        f"  {{\\small Four engine corpora (Voynich, Rohonc, Linear A, Emerald Tablet) each independently",
        f"  compile to the same 8-step categorical loop. Surface tokens differ; instruction stream does not.}}",
        f"  {B}vspace{{3pt}}",
        f"  {B}includegraphics[width=0.82{B}linewidth]{{{str(FIG/'bootstrap.pdf')}}}",
        f"",
        f"{B}end{{multicols}}",
        f"",
        f"{B}newpage",
    ])


# ── Page 3: Ecosystem ─────────────────────────────────────────────────────────

def page3() -> str:

    eco_tikz = rf"""
{B}begin{{center}}
{B}begin{{tikzpicture}}[
  every node/.style={{font={B}small}},
  repo/.style={{rectangle,rounded corners=4pt,draw=#1!70,fill=#1!12,
               text width=3.2cm,align=center,minimum height=0.9cm,
               font={B}small{B}bfseries}},
  conn/.style={{-{{Stealth[length=4pt]}},thick,#1!60}},
  lbl/.style={{font={B}scriptsize,text=#1,align=center}},
]

% Central grammar node
{B}node[rectangle,rounded corners=6pt,draw=hdrblue!80,fill=hdrblue!15,
       text width=4.2cm,align=center,minimum height=1.1cm,
       font={B}large{B}bfseries,text=hdrblue] (gram) at (0,0)
  {{Imscribing Grammar{B}\\{B}small Crystal of Types}};

% O_∞ tier
{B}node[repo=tierinfcol] (ankh)  at (-5.5, 3.2) {{MillenniumAnkh{B}\\{B}scriptsize Lean 4, 43 modules,{B}\\ 0 sorries, 16 O$_{B}infty$}};
{B}node[repo=tierinfcol] (p4ra)  at ( 0.0, 3.8) {{p4rakernel{B}\\{B}scriptsize C++ fork, 167 Lean modules,{B}\\ paraconsistent kernel}};
{B}node[repo=tierinfcol] (lean4) at ( 5.5, 3.2) {{lean4-paraconsistent{B}\\{B}scriptsize kernel fork, ex falso{B}\\ disabled at type level}};

% O₂† tier
{B}node[repo=tier2dcol] (ob3)  at (-6.2, 0.0) {{ob3ect{B}\\{B}scriptsize 34-layer categorical{B}\\ tower, layers 29--34 para}};
{B}node[repo=tier2dcol] (pri)  at (-3.8,-2.5) {{priests-engine{B}\\{B}scriptsize 13 modules, corpus{B}\\ bootstrap, 5 engines}};

% O₂ tier
{B}node[repo=tier2col] (exos)   at ( 3.8, 2.2) {{exOS{B}\\{B}scriptsize bare-metal Rust,{B}\\ ALEPH-typed kernel}};
{B}node[repo=tier2col] (synfin) at ( 6.2, 0.0) {{synfin{B}\\{B}scriptsize live trading,{B}\\ signals from morphisms}};

% O₁ tier
{B}node[repo=tier1col] (rebis) at ( 3.8,-2.5) {{rebis\_concrete{B}\\{B}scriptsize 11 designs, all sims{B}\\ pass, 4-phase roadmap}};
{B}node[repo=tier1col] (web)   at ( 0.0,-3.5) {{imscribe.com{B}\\{B}scriptsize IG web presence,{B}\\ agent site, frobenius-mzi}};

% Connections
{B}draw[conn=tierinfcol] (gram.north west) -- (ankh.south east);
{B}draw[conn=tierinfcol] (gram.north)      -- (p4ra.south);
{B}draw[conn=tierinfcol] (gram.north east) -- (lean4.south west);
{B}draw[conn=tier2dcol]  (gram.west)       -- (ob3.east);
{B}draw[conn=tier2dcol]  (ob3.south)       -- (pri.north);
{B}draw[conn=tier2col]   (gram.east)       -- (synfin.west);
{B}draw[conn=tier2col]   (gram.north east) -- (exos.south west);
{B}draw[conn=tier1col]   (gram.south)      -- (web.north);
{B}draw[conn=tier1col]   (gram.south east) -- (rebis.north west);

% Bridge arrows
{B}draw[conn=accentcol,dashed] (ankh.south)  -- (gram.north west);
{B}draw[conn=accentcol,dashed] (p4ra.south west) -- (ob3.north east);
{B}draw[conn=accentcol,dashed] (ob3.south)   -- (rebis.north west);
{B}draw[conn=accentcol,dashed] (pri.east)    -- (rebis.west);

% Tier legend (right side)
{B}fill[tierinfcol,opacity=0.6] (7.3,3.4) rectangle (7.45,3.6);
{B}fill[tier2dcol, opacity=0.6] (7.3,2.4) rectangle (7.45,2.6);
{B}fill[tier2col,  opacity=0.6] (7.3,1.4) rectangle (7.45,1.6);
{B}fill[tier1col,  opacity=0.6] (7.3,0.4) rectangle (7.45,0.6);
{B}node[lbl=tierinfcol,right] at (7.5, 3.5) {{O$_{B}infty$ — Frobenius complete}};
{B}node[lbl=tier2dcol, right] at (7.5, 2.5) {{O$_{{2{B}dagger}}$ — protected unbounded}};
{B}node[lbl=tier2col,  right] at (7.5, 1.5) {{O$_2$ — protected bounded}};
{B}node[lbl=tier1col,  right] at (7.5, 0.5) {{O$_1$ — unprotected critical}};

{B}end{{tikzpicture}}
{B}end{{center}}"""

    # Publications
    pubs = [
        ("Aether and Its Vessel v2", "Mills, 2026", "10.5281/zenodo.20553659", "O$_{\\infty}$ architecture, E8→Grammar chain, vessel operation"),
        ("The Universal Engine (IMASM)", "Mills, 2026", "this volume", "9 writing systems compiled to same 12-opcode categorical program"),
        ("Grammar of Chemical Reactivity", "Mills, 2026", "this volume", "Cu-nitroso C-N coupling (Org.~Lett. 2016) imscribed; $r=0.931$"),
        ("Serpent Rod", "Mills, 2026", "this volume", "Single Frobenius morphism RNA$\\to$\\{sequence+fold\\}; O$_{\\infty}$"),
    ]

    pub_rows = " {B}{B}\n    ".join(
        f"\\textit{{{t}}} ({a}) & \\texttt{{\\small doi:{d}}} & {{\\scriptsize {d2}}}"
        for t, a, d, d2 in pubs
    ).replace("[B}", B)

    return "\n".join([
        f"% ─── PAGE 3 ─────────────────────────────────────────────────────────────────",
        f"",
        f"{B}begin{{headerbox}}",
        f"  {{\\Large\\bfseries\\color{{white}} THE ECOSYSTEM}}",
        f"  {B}hfill{{\\normalsize\\color{{white!80!hdrblue}} Repos · Layers · Bridges}}",
        f"{B}end{{headerbox}}",
        f"",
        f"{B}vspace{{6pt}}",
        eco_tikz,
        f"",
        f"{B}vspace{{4pt}}",
        f"{B}begin{{sectionbox}}{{hdrblue}}",
        f"{{\\small\\bfseries\\color{{hdrblue}} Key Publications}} \\\\[2pt]",
        f"{{\\small",
        f"\\begin{{tabular}}{{@{{}}l l p{{5.5cm}}@{{}}}}",
        f"\\toprule",
        f"\\textbf{{Title}} & \\textbf{{DOI / Ref}} & \\textbf{{Content}} \\\\",
        f"\\midrule",
        f"\\textit{{Aether and Its Vessel v2}} (Mills, 2026) & \\texttt{{\\small 10.5281/zenodo.20553659}} & {{\\scriptsize O$_\\infty$ architecture, E8$\\to$Grammar chain, vessel operation}} \\\\",
        f"\\textit{{Universal Engine / IMASM}} (Mills, 2026) & this volume & {{\\scriptsize 9 writing systems compile to same 12-opcode categorical program}} \\\\",
        f"\\textit{{Grammar of Chemical Reactivity}} (Mills, 2026) & this volume & {{\\scriptsize Cu-nitroso C-N (Org.~Lett. 2016) imscribed; $r=0.931$ Pearson}} \\\\",
        f"\\textit{{Serpent Rod}} (Mills, 2026) & this volume & {{\\scriptsize Single Frobenius morphism RNA$\\to${{sequence+fold}}; O$_\\infty$}} \\\\",
        f"\\bottomrule",
        f"\\end{{tabular}}}}",
        f"{B}end{{sectionbox}}",
        f"",
        f"{B}newpage",
    ])


# ── Page 4: Applications ──────────────────────────────────────────────────────

def page4() -> str:

    # rebis_concrete designs
    designs = {
        "THERAPEUTICS": [
            ("Ouroboric Pill",        "DNA origami sensor-drug barrel (M13mp18, 54nm). 5 aptamers, QD-FRET logic gates. $\\mu{B}circ{B}delta$ error 0.0106.", "⊙ > <"),
            ("Quantum Biologic",      "dCas9-DNMT3A epigenetic editor. LNP vector, 5 targets (BDNF, MECP2, FMR1...). 78.8\\% efficacy, 100\\% Frobenius closure.", "> ⋈ Ħ"),
            ("Universal Antidote",    "$10^{12}$ DARPin library on yeast display. 500 toxin targets, 4 categories. FACS enrichment + deep sequencing.", "Ω Γ Σ"),
        ],
        "MATERIALS": [
            ("Ouroboric Composite",   "Self-healing CFRP. Embedded capsule network (85\\% efficiency). 7 healing cycles, 90.5\\% fatigue retention at 1000 cycles.", "Ç ⊣ <"),
            ("Topological QM",        "Bi$_2$Se$_3$/FeSe heterostructure. Majorana zero modes, non-Abelian braiding. MajoranaFixed: Majorana $\\equiv$ SIC-POVM $\\equiv$ Belnap B (rfl).", "⊣ Ω Ħ"),
            ("Eternal Memory Polymer","Oligocarbamate (264 monomers), chirality-encoded. $10^{15}$ bits/g. 55,723 year half-life @ 300K (Arrhenius).", "Ħ Σ Ω"),
            ("Self-Weaving Fabric",   "5-layer 3D orthogonal smart textile. Sensing, energy harvesting, display, RF. Multiplex via Γ scope hierarchy.", "Γ ɢ ⊢"),
        ],
        "BIOLOGY": [
            ("Ouroboric Cell",        "JCVI-syn3.0 (531 kbp, 469 genes) + serine recombinase self-editing system. 200-generation adaptive evolution sim, 40\\% genome edited.", "⊙ > Ħ"),
            ("Quantum Bioelectric",   "iPSC cardiomyocytes + neurons. Quantum-coherent ion channels (Kv1.2, Nav1.5), microelectrode array. Xenopus limb regeneration model.", "Ħ ⊙ ɢ"),
            ("Universal Symbiont",    "12-strain microbial consortium. Quorum sensing + metabolic cross-feeding. 12 strains $\\leftrightarrow$ 12 primitives (Σ bijection).", "Σ Γ ɢ"),
            ("Topological Morphogenesis","Reaction-diffusion kidney: Wnt/FGF/SDF-1 gradients. Gierer-Meinhardt activator-inhibitor. Tubule network from 500 sim steps.", "Ω ⊣ ⊢"),
        ],
    }

    cat_colors = {
        "THERAPEUTICS": "tier2dcol",
        "MATERIALS":    "tier2col",
        "BIOLOGY":      "tier1col",
    }

    # Build the grid as a tikzpicture
    grid_lines = [
        f"{B}begin{{tikzpicture}}[every node/.style={{font={B}small}}]",
    ]

    col_x = {"THERAPEUTICS": -5.0, "MATERIALS": 0.0, "BIOLOGY": 5.0}
    col_w = 4.6

    for cat, items in designs.items():
        cx = col_x[cat]
        cc = cat_colors[cat]
        # Category header
        grid_lines.append(
            f"  {B}node[rectangle,fill={cc}!25,draw={cc}!70,rounded corners=3pt,"
            f"  text width={col_w}cm,align=center,minimum height=0.7cm,"
            f"  font={B}bfseries{B}small,text={cc}] at ({cx},0) {{{cat}}};"
        )
        for j, (name, desc, prims) in enumerate(items):
            y = -1.0 - j * 1.55
            desc_short = desc[:110] + "..." if len(desc) > 110 else desc
            grid_lines.append(
                f"  {B}node[rectangle,fill={cc}!6,draw={cc}!40,rounded corners=2pt,"
                f"  text width={col_w}cm,align=left,minimum height=1.4cm,"
                f"  font={B}scriptsize,inner sep=4pt] at ({cx},{y}) {{"
                f"  {{\\bfseries\\color{{{cc}}} {name}}}\\\\[1pt]"
                f"  {desc_short}\\\\[1pt]"
                f"  {{\\color{{accentcol}} {prims}}}"
                f"  }};"
            )

    grid_lines.append(f"{B}end{{tikzpicture}}")
    grid_tikz = "\n".join(grid_lines)

    # Synfin status box
    synfin_box = "\n".join([
        f"  {B}begin{{sectionbox}}{{g4col}}",
        f"  {{\\small\\bfseries\\color{{g4col}} synfin — Live IG-Typed Trading System}}\\\\[2pt]",
        f"  {{\\small 10 free domain streams (Fear\\&Greed, mempool, CoinGecko, blockchain.info,",
        f"  NOAA tides, air quality, NASA DONKI, USGS seismic, Kp index, HN sentiment).",
        f"  Domain multiplier: 0 alerts=1.00$\\times$ · 1=1.20$\\times$ · 2=1.35$\\times$ · $\\geq$3=1.50$\\times$ (B-state).}}\\\\[2pt]",
        f"  {{\\small Live deployment 2026-06-05: Fear\\&Greed$=12$ (extreme fear), M-class flares, Kp$=4.33$,",
        f"  T\\textsubscript{{network}}$\\to$T\\textsubscript{{in}} topology convergence on 6 pairs.",
        f"  B-state $\\times$1.50, 100\\% Frobenius PASS. Deployed \\$43.57 across BTC/ETH/SOL/DOT/ATOM/NEAR.}}",
        f"  {B}end{{sectionbox}}",
    ])

    magnum_strip = "\n".join([
        f"  {B}begin{{sectionbox}}{{frobcol}}",
        f"  {{\\small\\bfseries\\color{{frobcol}} Magnum Opus — 12-Stage Alchemical Mapping}}\\\\[2pt]",
        f"  {{\\scriptsize",
        f"  \\begin{{tabular}}{{@{{}}llll@{{}}}}",
        f"  Prima Materia & ⊢ (Dimensionality) & Albedo & < (Parity, Frobenius-special) \\\\",
        f"  Nigredo & ⊣ (Topology, collapse) & Citrinitas & ⊙ (Criticality, self-model) \\\\",
        f"  Solutio & > (Recognition, dissolve) & Rubedo & Ω (Winding, completion) \\\\",
        f"  Calcinatio & Σ (Stoichiometry, fire) & Multiplicatio & Γ (Granularity, scope) \\\\",
        f"  Coagulatio & Ç (Kinetics, fixation) & Projectio & ɢ (Coupling, projection) \\\\",
        f"  Sublimatio & ⋈ (Fidelity, rising) & Fixatio & Ħ (Chirality, fixed point) \\\\",
        f"  \\end{{tabular}}",
        f"  }}",
        f"  {B}end{{sectionbox}}",
    ])

    return "\n".join([
        f"% ─── PAGE 4 ─────────────────────────────────────────────────────────────────",
        f"",
        f"{B}begin{{headerbox}}",
        f"  {{\\Large\\bfseries\\color{{white}} APPLICATIONS — rebis\\_concrete}}",
        f"  {B}hfill{{\\normalsize\\color{{white!80!hdrblue}} 11 Frobenius-Verified Designs · 4-Phase Roadmap}}",
        f"{B}end{{headerbox}}",
        f"",
        f"{B}vspace{{6pt}}",
        f"{B}begin{{center}}",
        grid_tikz,
        f"{B}end{{center}}",
        f"",
        f"{B}vspace{{4pt}}",
        f"{B}begin{{multicols}}{{2}}",
        synfin_box,
        f"  {B}columnbreak",
        magnum_strip,
        f"{B}end{{multicols}}",
        f"",
        f"{B}end{{document}}",
    ])


# ── Assemble + compile ─────────────────────────────────────────────────────────

def main():
    print("Generating figures...")
    gen_figures()

    print("Assembling LaTeX...")
    # walkaround: page1() uses := inside expression, eval separately
    p1 = page1()
    p2 = page2()
    p3 = page3()
    p4 = page4()
    full = preamble() + "\n" + p1 + "\n" + p2 + "\n" + p3 + "\n" + p4

    TEX.parent.mkdir(parents=True, exist_ok=True)
    TEX.write_text(full, encoding="utf-8")
    print(f"  tex → {TEX}")

    ltx = Path.home() / ".local" / "bin" / "ltx"
    if not ltx.exists():
        ltx = Path("/usr/bin/lualatex")

    print(f"  compiling with {ltx.name} ...")
    result = subprocess.run(
        [str(ltx), str(TEX.name)],
        capture_output=True, text=True,
        cwd=str(TEX.parent),
    )
    if result.returncode != 0:
        log = TEX.with_suffix(".log")
        if log.exists():
            lines = log.read_text(errors="replace").splitlines()
            print("  LaTeX errors (last 40 lines):")
            for l in lines[-40:]:
                print(f"    {l}")
        else:
            print(result.stderr[-1000:])
        sys.exit(1)

    built = TEX.with_suffix(".pdf")
    import shutil
    shutil.copy2(str(built), str(PDF))
    print(f"  PDF → {PDF}")
    print("  done.")


if __name__ == "__main__":
    main()
