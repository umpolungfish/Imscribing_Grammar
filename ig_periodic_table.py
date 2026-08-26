#!/usr/bin/env python3
"""
IG Periodic Table — Janet (left-step) arrangement grounded in 12 primitives.

Primary axes:
  X: ⊡ × ⊥  (orbital winding × chirality = block structure)
  Y: ∈       (granularity = period)

Block primitive signatures:
  s-block: 𐑷,   𐑓  — no angular momentum, minimal spin-orbit
  p-block: 𐑴,  𐑒  — half-integer winding
  d-block: 𐑭,   𐑒  — integer winding, moderate SOC
  f-block: 𐑭,   𐑖/H∞ — integer winding + strong/extreme SOC

Secondary cell annotation: the one primitive most distinctive for each element's chemistry.
"""

import textwrap

# ─────────────────────────────────────────────────────────────
# Element data: symbol → (Z, period, janet_col, block)
# Janet columns 1-32, left-to-right: f(1-14) | d(15-24) | p(25-30) | s(31-32)
# ─────────────────────────────────────────────────────────────
ELEMENTS = {
    # s-block (cols 31-32)
    'H':  (1,  1, 31, 's'), 'He': (2,  1, 32, 's'),
    'Li': (3,  2, 31, 's'), 'Be': (4,  2, 32, 's'),
    'Na': (11, 3, 31, 's'), 'Mg': (12, 3, 32, 's'),
    'K':  (19, 4, 31, 's'), 'Ca': (20, 4, 32, 's'),
    'Rb': (37, 5, 31, 's'), 'Sr': (38, 5, 32, 's'),
    'Cs': (55, 6, 31, 's'), 'Ba': (56, 6, 32, 's'),
    'Fr': (87, 7, 31, 's'), 'Ra': (88, 7, 32, 's'),
    # p-block (cols 25-30)
    'B':  (5,  2, 25, 'p'), 'C':  (6,  2, 26, 'p'), 'N':  (7,  2, 27, 'p'),
    'O':  (8,  2, 28, 'p'), 'F':  (9,  2, 29, 'p'), 'Ne': (10, 2, 30, 'p'),
    'Al': (13, 3, 25, 'p'), 'Si': (14, 3, 26, 'p'), 'P':  (15, 3, 27, 'p'),
    'S':  (16, 3, 28, 'p'), 'Cl': (17, 3, 29, 'p'), 'Ar': (18, 3, 30, 'p'),
    'Ga': (31, 4, 25, 'p'), 'Ge': (32, 4, 26, 'p'), 'As': (33, 4, 27, 'p'),
    'Se': (34, 4, 28, 'p'), 'Br': (35, 4, 29, 'p'), 'Kr': (36, 4, 30, 'p'),
    'In': (49, 5, 25, 'p'), 'Sn': (50, 5, 26, 'p'), 'Sb': (51, 5, 27, 'p'),
    'Te': (52, 5, 28, 'p'), 'I':  (53, 5, 29, 'p'), 'Xe': (54, 5, 30, 'p'),
    'Tl': (81, 6, 25, 'p'), 'Pb': (82, 6, 26, 'p'), 'Bi': (83, 6, 27, 'p'),
    'Po': (84, 6, 28, 'p'), 'At': (85, 6, 29, 'p'), 'Rn': (86, 6, 30, 'p'),
    'Nh': (113,7, 25, 'p'), 'Fl': (114,7, 26, 'p'), 'Mc': (115,7, 27, 'p'),
    'Lv': (116,7, 28, 'p'), 'Ts': (117,7, 29, 'p'), 'Og': (118,7, 30, 'p'),
    # d-block (cols 15-24)
    'Sc': (21, 4, 15, 'd'), 'Ti': (22, 4, 16, 'd'), 'V':  (23, 4, 17, 'd'),
    'Cr': (24, 4, 18, 'd'), 'Mn': (25, 4, 19, 'd'), 'Fe': (26, 4, 20, 'd'),
    'Co': (27, 4, 21, 'd'), 'Ni': (28, 4, 22, 'd'), 'Cu': (29, 4, 23, 'd'),
    'Zn': (30, 4, 24, 'd'),
    'Y':  (39, 5, 15, 'd'), 'Zr': (40, 5, 16, 'd'), 'Nb': (41, 5, 17, 'd'),
    'Mo': (42, 5, 18, 'd'), 'Tc': (43, 5, 19, 'd'), 'Ru': (44, 5, 20, 'd'),
    'Rh': (45, 5, 21, 'd'), 'Pd': (46, 5, 22, 'd'), 'Ag': (47, 5, 23, 'd'),
    'Cd': (48, 5, 24, 'd'),
    'Lu': (71, 6, 15, 'd'), 'Hf': (72, 6, 16, 'd'), 'Ta': (73, 6, 17, 'd'),
    'W':  (74, 6, 18, 'd'), 'Re': (75, 6, 19, 'd'), 'Os': (76, 6, 20, 'd'),
    'Ir': (77, 6, 21, 'd'), 'Pt': (78, 6, 22, 'd'), 'Au': (79, 6, 23, 'd'),
    'Hg': (80, 6, 24, 'd'),
    'Lr': (103,7, 15, 'd'), 'Rf': (104,7, 16, 'd'), 'Db': (105,7, 17, 'd'),
    'Sg': (106,7, 18, 'd'), 'Bh': (107,7, 19, 'd'), 'Hs': (108,7, 20, 'd'),
    'Mt': (109,7, 21, 'd'), 'Ds': (110,7, 22, 'd'), 'Rg': (111,7, 23, 'd'),
    'Cn': (112,7, 24, 'd'),
    # f-block lanthanides (cols 1-14, period 6)
    'La': (57, 6,  1, 'f'), 'Ce': (58, 6,  2, 'f'), 'Pr': (59, 6,  3, 'f'),
    'Nd': (60, 6,  4, 'f'), 'Pm': (61, 6,  5, 'f'), 'Sm': (62, 6,  6, 'f'),
    'Eu': (63, 6,  7, 'f'), 'Gd': (64, 6,  8, 'f'), 'Tb': (65, 6,  9, 'f'),
    'Dy': (66, 6, 10, 'f'), 'Ho': (67, 6, 11, 'f'), 'Er': (68, 6, 12, 'f'),
    'Tm': (69, 6, 13, 'f'), 'Yb': (70, 6, 14, 'f'),
    # f-block actinides (cols 1-14, period 7)
    'Ac': (89, 7,  1, 'f'), 'Th': (90, 7,  2, 'f'), 'Pa': (91, 7,  3, 'f'),
    'U':  (92, 7,  4, 'f'), 'Np': (93, 7,  5, 'f'), 'Pu': (94, 7,  6, 'f'),
    'Am': (95, 7,  7, 'f'), 'Cm': (96, 7,  8, 'f'), 'Bk': (97, 7,  9, 'f'),
    'Cf': (98, 7, 10, 'f'), 'Es': (99, 7, 11, 'f'), 'Fm': (100,7, 12, 'f'),
    'Md': (101,7, 13, 'f'), 'No': (102,7, 14, 'f'),
}

# ─────────────────────────────────────────────────────────────
# IG primitive annotation per element (most structurally distinctive)
# ─────────────────────────────────────────────────────────────
PRIM_LABEL = {
    # H: dialetheic coupling — bonds as both donor and acceptor
    'H':  '⊥',
    # He: doubly-magic nucleus, 𐑢 — the archetypal subcritical
    'He': '⊙',
    # Alkali metals: pure ionic donors, 𐑜 coupling
    'Li': '∋', 'Na': '∋', 'K':  '∋',
    'Rb': '∋', 'Cs': '∋', 'Fr': '∋',
    # Alkaline earths: fixed Σ=2
    'Be': '⊞', 'Mg': '⊞', 'Ca': '⊞',
    'Sr': '⊞', 'Ba': '⊞', 'Ra': '⊞',
    # Group 13 — dimensionality (boundary 2D/3D)
    'B':  '⊢', 'Al': '⊢', 'Ga': '⊢',
    'In': '⊢', 'Tl': '⊢', 'Nh': '⊢',
    # Group 14 — topology (tetrahedral network)
    'C':  '⊣', 'Si': '⊣', 'Ge': '⊣',
    'Sn': '⊣', 'Pb': '⊣', 'Fl': '⊣',
    # Group 15 — fixed stoichiometry N:3
    'N':  '⊞', 'P':  '⊞', 'As': '⊞',
    'Sb': '⊞', 'Bi': '⊞', 'Mc': '⊞',
    # Group 16 — parity (O double bond, S ring topology)
    'O':  '≺', 'S':  '≺', 'Se': '≺',
    'Te': '≺', 'Po': '≺', 'Lv': '≺',
    # Group 17 halogens — fastest kinetics
    'F':  '⊤', 'Cl': '⊤', 'Br': '⊤',
    'I':  '⊤', 'At': '⊤', 'Ts': '⊤',
    # Noble gases — subcritical
    'Ne': '⊙', 'Ar': '⊙', 'Kr': '⊙',
    'Xe': '⊙', 'Rn': '⊙', 'Og': '⊙',
    # d-block: coordination chirality
    'Sc': '⊥', 'Ti': '⊥', 'V':  '⊥', 'Cr': '⊥',
    'Mn': '⊥', 'Fe': '⊥', 'Co': '⊥', 'Ni': '⊥',
    'Cu': '⊥', 'Zn': '⊥',
    'Y':  '⊥', 'Zr': '⊥', 'Nb': '⊥', 'Mo': '⊥',
    'Tc': '⊥', 'Ru': '⊥', 'Rh': '⊥', 'Pd': '⊥',
    'Ag': '⊥', 'Cd': '⊥',
    # Heavy d-block (period 6): relativistic SOC; noble metals annotated with 𐑧
    'Lu': '⊥', 'Hf': '⊥', 'Ta': '⊥', 'W':  '⊥',
    'Re': '⊥', 'Os': '⊥', 'Ir': '⊥',
    'Pt': '⊤', 'Au': '⊤',
    'Hg': '⊥',
    'Lr': '⊥', 'Rf': '⊥', 'Db': '⊥', 'Sg': '⊥',
    'Bh': '⊥', 'Hs': '⊥', 'Mt': '⊥', 'Ds': '⊥',
    'Rg': '⊥', 'Cn': '⊥',
    # f-block lanthanides: 𐑖 (strong SOC, chiral magnetics)
    'La': '⊥', 'Ce': '⊥', 'Pr': '⊥', 'Nd': '⊥',
    'Pm': '⊥', 'Sm': '⊥', 'Eu': '⊥', 'Gd': '⊥',
    'Tb': '⊥', 'Dy': '⊥', 'Ho': '⊥', 'Er': '⊥',
    'Tm': '⊥', 'Yb': '⊥',
    # f-block actinides: ⊙ (nuclear criticality dominates)
    'Ac': '⊙', 'Th': '⊙', 'Pa': '⊙', 'U':  '⊙',
    'Np': '⊙', 'Pu': '⊙', 'Am': '⊙', 'Cm': '⊙',
    'Bk': '⊙', 'Cf': '⊙', 'Es': '⊙', 'Fm': '⊙',
    'Md': '⊙', 'No': '⊙',
}

# Radioactive / unstable elements (dashed border)
RADIOACTIVE = {
    'Tc','Pm','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am',
    'Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt',
    'Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og',
}

# ─────────────────────────────────────────────────────────────
# FDE (First-Degree Entailment / Belnap FOUR) classification
# Proposition: "this element participates in Frobenius transformation"
#   T = True  — PGM noble-metal catalysts, always return to ground state
#   F = False — noble gases, no δ morphism exists
#   B = Both  — context-dependent (enzyme vs stoichiometric)
#   N = Neither — too transient/synthetic to characterise
# ─────────────────────────────────────────────────────────────
_FDE_T = {'Ru', 'Rh', 'Pd', 'Os', 'Ir', 'Pt', 'Au'}
_FDE_F = {'He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn'}
_FDE_N = {
    'Tc', 'Pm',
    'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr',
    'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn',
    'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og',
}
FDE_CLASS: dict = {}
for _s in _FDE_T: FDE_CLASS[_s] = 'T'
for _s in _FDE_F: FDE_CLASS[_s] = 'F'
for _s in _FDE_N: FDE_CLASS[_s] = 'N'
for _s in ELEMENTS:
    if _s not in FDE_CLASS:
        FDE_CLASS[_s] = 'B'

# Frobenius thread element sequences (the catalytic spine of chemistry)
ORGANIC_THREAD  = ['H', 'O', 'N', 'C', 'S', 'P']
METALLIC_THREAD = ['Fe', 'Ni', 'Zn', 'Mo', 'Rh', 'Pd', 'W', 'Ir', 'Pt', 'Au']

# ─────────────────────────────────────────────────────────────
# TikZ cell colors by block × period (⊡ × ∈)
# ─────────────────────────────────────────────────────────────
BLOCK_BASE = {
    's': 'amber',
    'p': 'sky',
    'd': 'sage',
    'f': 'orchid',
}

PERIOD_SHADE = {1: 10, 2: 10, 3: 20, 4: 30, 5: 45, 6: 60, 7: 75}

def cell_color(block, period):
    shade = PERIOD_SHADE.get(period, 50)
    return f"{BLOCK_BASE[block]}!{shade}"

# ─────────────────────────────────────────────────────────────
# LaTeX generation
# ─────────────────────────────────────────────────────────────
CELL_W = 0.72   # cm
CELL_H = 0.88   # cm
GAP = 0.02      # cm between cells

def cell_x(col):
    return (col - 1) * (CELL_W + GAP)

def cell_y(period):
    return -(period - 1) * (CELL_H + GAP)


def make_cell(sym, Z, period, block):
    x = cell_x(ELEMENTS[sym][2])
    y = cell_y(period)
    color = cell_color(block, period)
    prim = PRIM_LABEL.get(sym, '')
    border = 'dashed' if sym in RADIOACTIVE else 'solid'
    border_color = 'red!60' if sym in RADIOACTIVE else 'black!40'
    # Compact: Z top-left tiny, symbol center, prim bottom tiny
    node = (
        f'\\node[cell,fill={color},draw={border_color},line width=0.3pt,'
        f'{"dashed," if sym in RADIOACTIVE else ""}]\n'
        f'  at ({x:.3f}cm,{y:.3f}cm) {{\n'
        f'    \\cellZ{{{Z}}}\\\\\n'
        f'    \\cellSym{{{sym}}}\\\\\n'
        f'    \\cellPrim{{{prim}}}\n'
        f'  }};\n'
    )
    return node


def make_block_label(block, col_start, col_end, period, label):
    x1 = cell_x(col_start)
    x2 = cell_x(col_end) + CELL_W
    xm = (x1 + x2) / 2
    y = cell_y(period) + CELL_H / 2 + 0.35
    return f'\\node[blocklab] at ({xm:.3f}cm,{y:.3f}cm) {{{label}}};\n'


def make_fde_dot(sym, col, period):
    """Belnap FOUR indicator: tiny dot at top-right of each cell."""
    x = cell_x(col) + CELL_W / 2 - 0.115
    y = cell_y(period) + CELL_H / 2 - 0.095
    fde = FDE_CLASS.get(sym, 'B')
    sz = '3.2pt'
    if fde == 'T':
        return (f'\\node[circle,fill=green!65!black,inner sep=0pt,'
                f'minimum size={sz}] at ({x:.3f}cm,{y:.3f}cm) {{}};\n')
    elif fde == 'F':
        return (f'\\node[circle,fill=black!55,inner sep=0pt,'
                f'minimum size={sz}] at ({x:.3f}cm,{y:.3f}cm) {{}};\n')
    elif fde == 'B':
        return (f'\\node[circle,fill=orange!85!red,inner sep=0pt,'
                f'minimum size={sz}] at ({x:.3f}cm,{y:.3f}cm) {{}};\n')
    else:  # N
        return (f'\\node[circle,draw=black!40,fill=white,line width=0.4pt,'
                f'inner sep=0pt,minimum size={sz}] at ({x:.3f}cm,{y:.3f}cm) {{}};\n')


def make_thread_highlights():
    """Ring highlights on Frobenius-threaded elements + smooth connecting curves
    and an enzyme-bridge arc that visually crosses the p/d block boundary
    (the braid crossing σ₁)."""
    lines = []
    # Organic thread — red rings
    for sym in ORGANIC_THREAD:
        if sym in ELEMENTS:
            _, period, col, _ = ELEMENTS[sym]
            x, y = cell_x(col), cell_y(period)
            lines.append(
                f'\\node[rectangle,rounded corners=2pt,draw=red!60,line width=1.2pt,'
                f'fill=none,minimum width=0.78cm,minimum height=0.94cm]'
                f' at ({x:.3f}cm,{y:.3f}cm) {{}};\n'
            )
    # Metallic thread — blue rings
    for sym in METALLIC_THREAD:
        if sym in ELEMENTS:
            _, period, col, _ = ELEMENTS[sym]
            x, y = cell_x(col), cell_y(period)
            lines.append(
                f'\\node[rectangle,rounded corners=2pt,draw=blue!55,line width=1.2pt,'
                f'fill=none,minimum width=0.78cm,minimum height=0.94cm]'
                f' at ({x:.3f}cm,{y:.3f}cm) {{}};\n'
            )
    # Organic smooth curve
    org_pts = ' '.join(
        f'({cell_x(ELEMENTS[s][2]):.3f}cm,{cell_y(ELEMENTS[s][1]):.3f}cm)'
        for s in ORGANIC_THREAD if s in ELEMENTS
    )
    lines.append(
        f'\\draw[red!50,line width=0.65pt,opacity=0.75]'
        f' plot[smooth,tension=0.55] coordinates {{{org_pts}}};\n'
    )
    # Metallic smooth curve
    met_pts = ' '.join(
        f'({cell_x(ELEMENTS[s][2]):.3f}cm,{cell_y(ELEMENTS[s][1]):.3f}cm)'
        for s in METALLIC_THREAD if s in ELEMENTS
    )
    lines.append(
        f'\\draw[blue!50,line width=0.65pt,opacity=0.75]'
        f' plot[smooth,tension=0.55] coordinates {{{met_pts}}};\n'
    )
    # Enzyme bridge 1 (dashed, σ₁ over-crossing): S ──► Zn
    Sx  = cell_x(ELEMENTS['S'][2]);  Sy  = cell_y(ELEMENTS['S'][1])
    Znx = cell_x(ELEMENTS['Zn'][2]); Zny = cell_y(ELEMENTS['Zn'][1])
    lines.append(
        f'\\draw[purple!65,line width=0.9pt,dashed,opacity=0.85]'
        f' ({Sx:.3f}cm,{Sy:.3f}cm) .. controls'
        f' ({Sx-0.9:.3f}cm,{Sy-0.50:.3f}cm) and'
        f' ({Znx+0.6:.3f}cm,{Zny+0.50:.3f}cm) ..'
        f' ({Znx:.3f}cm,{Zny:.3f}cm);\n'
    )
    # Enzyme bridge 2 (dotted, σ₁⁻¹ under-crossing): Fe ──► N  (nitrogenase)
    Fex = cell_x(ELEMENTS['Fe'][2]); Fey = cell_y(ELEMENTS['Fe'][1])
    Nx  = cell_x(ELEMENTS['N'][2]);  Ny  = cell_y(ELEMENTS['N'][1])
    lines.append(
        f'\\draw[purple!45,line width=0.9pt,dotted,opacity=0.70]'
        f' ({Fex:.3f}cm,{Fey:.3f}cm) .. controls'
        f' ({Fex+1.6:.3f}cm,{Fey+0.60:.3f}cm) and'
        f' ({Nx-0.4:.3f}cm,{Ny-0.60:.3f}cm) ..'
        f' ({Nx:.3f}cm,{Ny:.3f}cm);\n'
    )
    # Crossing marker (braid crossing σ₁ label) at the bridge midpoint
    cx = (Sx + Fex) / 2 + 0.6;  cy = (Sy + Fey) / 2
    lines.append(
        f'\\node[circle,fill=purple!55,opacity=0.85,inner sep=0pt,minimum size=5pt]'
        f' at ({cx:.3f}cm,{cy:.3f}cm) {{}};\n'
    )
    lines.append(
        f'\\node[font=\\fontsize{{4.5}}{{4.5}}\\selectfont,text=purple!75,anchor=west]'
        f' at ({cx+0.08:.3f}cm,{cy:.3f}cm) {{$\\sigma_1$}};\n'
    )
    return ''.join(lines)


def make_braid_diagram(bx, by):
    """Frobenius threading braid using the braids TikZ library.
    3 strands: p/s (red), d (blue), Frobenius thread (orange).
    Braid word s_1 s_2^{-1} s_1 s_2^{-1} s_1 represents one full
    catalytic cycle: organic ↔ enzyme ↔ substrate transformation."""
    lines = []
    lines.append(
        f'\\node[font=\\scriptsize\\bfseries,text=black!65,anchor=west]'
        f' at ({bx:.2f}cm,{by+0.55:.2f}cm)'
        r' {Frobenius threading braid \ $\mu \circ \delta = \mathrm{id}$};' + '\n'
    )
    # Strand color labels above braid
    for i, (col, lab) in enumerate([
        ('red!70!black',    'p/s'),
        ('blue!60!black',   'd'),
        ('orange!70!black', r'$\mu\!\circ\!\delta$'),
    ]):
        sx = bx + i * 0.50
        lines.append(
            f'\\node[font=\\fontsize{{5}}{{5}}\\selectfont,text={col},anchor=south]'
            f' at ({sx:.2f}cm,{by+0.05:.2f}cm) {{{lab}}};\n'
        )
    lines.append(
        f'\\pic[\n'
        f'  braid/.cd,\n'
        f'  number of strands=3,\n'
        f'  strand 1/.style={{draw=red!70!black, line width=1.1pt}},\n'
        f'  strand 2/.style={{draw=blue!60!black, line width=1.1pt}},\n'
        f'  strand 3/.style={{draw=orange!70!black, line width=1.1pt}},\n'
        f'  height=-0.46cm,\n'
        f'  width=0.50cm,\n'
        f'  gap=0.07,\n'
        f'] at ({bx:.2f}cm,{by:.2f}cm)'
        r' {braid={s_1 s_2^{-1} s_1 s_2^{-1} s_1}};' + '\n'
    )
    return ''.join(lines)


def generate_tex():
    lines = []

    lines.append(r"""\documentclass[12pt,a4paper,landscape]{article}
\usepackage{fontspec}
\usepackage[top=0.8cm,bottom=1.2cm,left=0.6cm,right=0.6cm]{geometry}
\usepackage[warnings-off={mathtools-colon,mathtools-overbracket}]{unicode-math}
\ExplSyntaxOn\msg_redirect_name:nnn{lualatex-math}{wrong-meaning}{none}\ExplSyntaxOff
\setmathfont{Latin Modern Math}
\newfontface\igprimfont{Everson Mono}
\usepackage{tikz}
\usetikzlibrary{positioning,fit,backgrounds,braids}
\usepackage{xcolor}
\usepackage{microtype}
\pagestyle{empty}

% Custom colors
\definecolor{amber}{RGB}{255,200,80}
\definecolor{sky}{RGB}{100,180,240}
\definecolor{sage}{RGB}{120,200,140}
\definecolor{orchid}{RGB}{210,140,220}

\tikzset{
  cell/.style={
    rectangle, minimum width=0.72cm, minimum height=0.88cm,
    text width=0.70cm, align=center,
    inner sep=1pt, outer sep=0pt,
  },
  blocklab/.style={font=\tiny\bfseries, text=black!60},
}

\newcommand{\cellZ}[1]{{\fontsize{4}{4}\selectfont\textcolor{black!55}{#1}}}
\newcommand{\cellSym}[1]{{\fontsize{7}{7}\selectfont\textbf{#1}}}
\newcommand{\cellPrim}[1]{{\igprimfont\fontsize{5}{5}\selectfont\textcolor{black!65}{#1}}}

\begin{document}
\begin{center}
{\large\bfseries Imscribing Grammar Periodic Table}\\[2pt]
{\small Janet (left-step) arrangement $\cdot$ primary axes: $\Omega \times$ ⊥ (block) and $\Gamma$ (period)}\\[6pt]

\begin{tikzpicture}
""")

    # Generate all element cells
    for sym, (Z, period, col, block) in sorted(ELEMENTS.items(), key=lambda x: x[1][0]):
        lines.append(make_cell(sym, Z, period, block))

    # Frobenius thread highlights + bridge arcs (drawn on top of cells)
    lines.append(make_thread_highlights())

    # FDE Belnap FOUR dots (top-right corner of each cell)
    for sym, (Z, period, col, block) in ELEMENTS.items():
        lines.append(make_fde_dot(sym, col, period))

    # Block bracket labels (above period 1 row)
    lines.append(make_block_label('f', 1, 14, 1,
        r'f-block: $\Omega_{\mathbb{Z}}$, {\igprimfont ⊥}$_2$/{\igprimfont ⊥}$_\infty$'))
    lines.append(make_block_label('d', 15, 24, 1,
        r'd-block: $\Omega_{\mathbb{Z}}$, {\igprimfont ⊥}$_1$'))
    lines.append(make_block_label('p', 25, 30, 1,
        r'p-block: $\Omega_{\mathbb{Z}_2}$, {\igprimfont ⊥}$_1$'))
    lines.append(make_block_label('s', 31, 32, 1,
        r's-block: $\Omega_0$, {\igprimfont ⊥}$_0$'))

    # Period ∈ labels on left  (\beth \gimel \aleph work with amssymb)
    gamma = {1: r'$\Gamma_\beth$ (1)', 2: r'$\Gamma_\beth$ (2)',
             3: r'$\Gamma_\gimel$ (3)', 4: r'$\Gamma_\gimel$ (4)',
             5: r'$\Gamma_\aleph$ (5)', 6: r'$\Gamma_\aleph$ (6)',
             7: r'$\Gamma_\aleph$ (7)'}
    for period, lab in gamma.items():
        y = cell_y(period)
        lines.append(
            f'\\node[font=\\tiny, text=black!50, anchor=east] '
            f'at (-0.15cm,{y:.3f}cm) {{{lab}}};\n'
        )

    # Legend
    legend_y = cell_y(7) - CELL_H - 0.5
    legend_items = [
        (r'\colorbox{amber!40}{\phantom{X}} s-block ($\Omega_0$, {\igprimfont ⊥}$_0$)', 0),
        (r'\colorbox{sky!40}{\phantom{X}} p-block ($\Omega_{\mathbb{Z}_2}$, {\igprimfont ⊥}$_1$)', 5.5),
        (r'\colorbox{sage!40}{\phantom{X}} d-block ($\Omega_{\mathbb{Z}}$, {\igprimfont ⊥}$_1$)', 11.5),
        (r'\colorbox{orchid!40}{\phantom{X}} f-block ($\Omega_{\mathbb{Z}}$, {\igprimfont ⊥}$_{\geq 2}$)', 17),
        (r'{\footnotesize darker shade = higher $\Gamma$ (period)}', 23.5),
    ]
    for text, xoff in legend_items:
        lines.append(
            f'\\node[anchor=west, font=\\footnotesize] '
            f'at ({xoff:.1f}cm,{legend_y:.3f}cm) {{{text}}};\n'
        )

    # Cell primitive annotation legend
    prim_y = legend_y - 0.55
    lines.append(
        f'\\node[anchor=west, font=\\scriptsize, text=black!60] '
        f'at (0cm,{prim_y:.3f}cm) {{'
        r'Cell annotation (bottom): dominant IG primitive --- '
        r'{\igprimfont ⊥}=Chirality $\cdot$ {\igprimfont ⊙}=Criticality $\cdot$ {\igprimfont ∋}=Coupling $\cdot$ '
        r'{\igprimfont Σ}=Stoichiometry $\cdot$ {\igprimfont ⊣}=Topology $\cdot$ {\igprimfont <}=Parity $\cdot$ {\igprimfont ⊤}=Kinetics $\cdot$ '
        r'{\igprimfont ⊢}=Dimensionality'
        '. Dashed border = radioactive.};\n'
    )

    # FDE dot legend
    fde_y = prim_y - 0.50
    lines.append(
        f'\\node[anchor=west, font=\\scriptsize, text=black!60]'
        f' at (0cm,{fde_y:.3f}cm) {{'
        r'Top-right dot (FDE / Belnap FOUR): '
        r'\tikz\node[circle,fill=green!65!black,inner sep=0pt,minimum size=5pt]{};\ '
        r'\textbf{T}=PGM catalysts (always Frobenius) \ '
        r'\tikz\node[circle,fill=orange!85!red,inner sep=0pt,minimum size=5pt]{};\ '
        r'\textbf{B}=context-dependent ($\mu\circ\delta=\mathrm{id}$ sometimes) \ '
        r'\tikz\node[circle,draw=black!40,fill=white,line width=0.5pt,inner sep=0pt,minimum size=5pt]{};\ '
        r'\textbf{N}=indeterminate \ '
        r'\tikz\node[circle,fill=black!55,inner sep=0pt,minimum size=5pt]{};\ '
        r'\textbf{F}=noble gas (no $\delta$).};'
        '\n'
    )

    # Thread legend
    thread_y = fde_y - 0.50
    lines.append(
        f'\\node[anchor=west, font=\\scriptsize, text=black!60]'
        f' at (0cm,{thread_y:.3f}cm) {{'
        r'\tikz\draw[red!60,line width=1pt] (0,0)--(0.4cm,0);\ organic thread (H C N O S P) '
        r'\tikz\draw[blue!55,line width=1pt] (0,0)--(0.4cm,0);\ metallic thread (Fe Ni Zn Mo Rh Pd W Ir Pt Au) '
        r'\tikz\draw[purple!65,line width=1pt,dashed] (0,0)--(0.4cm,0);\ enzyme bridge ($\sigma_1$ crossing).};'
        '\n'
    )

    # Frobenius threading braid diagram (right side, same height as thread legend)
    lines.append(make_braid_diagram(17.5, thread_y - 0.55))

    lines.append(r"""\end{tikzpicture}
\end{center}
\end{document}
""")

    return ''.join(lines)


if __name__ == '__main__':
    import subprocess, sys
    from pathlib import Path

    out_dir = Path(__file__).parent
    tex_path = out_dir / 'ig_periodic_table.tex'
    pdf_path = out_dir / 'ig_periodic_table.pdf'
    pdfs_dir = out_dir / 'pdfs' if (out_dir / 'pdfs').exists() else out_dir

    tex = generate_tex()
    tex_path.write_text(tex)
    print(f'Wrote {tex_path}')

    result = subprocess.run(
        ['lualatex', '--interaction=nonstopmode', '--output-directory', str(out_dir), str(tex_path)],
        capture_output=True, text=True, cwd=str(out_dir),
    )
    if result.returncode == 0:
        print(f'Compiled → {pdf_path}')
        import shutil
        dest = pdfs_dir / 'ig_periodic_table.pdf'
        shutil.copy(pdf_path, dest)
        print(f'Copied → {dest}')
    else:
        print('lualatex errors:')
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(' ', line)
        sys.exit(1)
