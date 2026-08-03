#!/usr/bin/env python3
"""
Design B — Frobenius Spine periodic arrangement.

The Frobenius thread (organic + metallic) is the backbone of the page.
All other elements are satellites ordered by FDE distance from the thread.
The chemical truth is made spatial: μ∘δ=id is the spine; everything else
is peripheral.

Layout (left → right):
  noble gases (F-state) | ← p-block satellites | SPINE | d/f-block satellites → | T-state attached
  x ≈ -7.5                x ≈ -4.5               x=±2.2   x ≈ 4.5–9              x ≈ 5.5
"""

import math, subprocess, shutil
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import (
    ELEMENTS, PRIM_LABEL, FDE_CLASS,
    ORGANIC_THREAD, METALLIC_THREAD, RADIOACTIVE,
)

ORGANIC_SET  = set(ORGANIC_THREAD)
METALLIC_SET = set(METALLIC_THREAD)
T_SET   = {s for s, c in FDE_CLASS.items() if c == 'T'}
F_SET   = {s for s, c in FDE_CLASS.items() if c == 'F'}
N_SET   = {s for s, c in FDE_CLASS.items() if c == 'N'}

# ─── Spine geometry ─────────────────────────────────────────────────────────
X_ORG   = -2.2   # organic thread x
X_MET   =  2.2   # metallic thread x
Y_STEP  =  1.85  # cm between consecutive thread elements

def org_y(i):  return -i * Y_STEP
def met_y(i):  return -i * Y_STEP

THREAD_POS = {}
for i, s in enumerate(ORGANIC_THREAD):
    THREAD_POS[s] = (X_ORG, org_y(i))
for i, s in enumerate(METALLIC_THREAD):
    THREAD_POS[s] = (X_MET, met_y(i))

# T-state non-thread: Ru (between Mo idx=3 and Rh idx=4) and Os (between W idx=6 and Ir idx=7)
T_SAT_POS = {
    'Ru': (5.2, (met_y(3) + met_y(4)) / 2),
    'Os': (5.2, (met_y(6) + met_y(7)) / 2),
}

# Noble gases — isolated column on far left
X_NOBLE = -6.8
NOBLE_ORDER = ['He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn']
NOBLE_POS = {s: (X_NOBLE, -i * 1.65) for i, s in enumerate(NOBLE_ORDER)}

# ─── Satellite element positions ─────────────────────────────────────────────
# Group all remaining elements by prim family and period, spread horizontally.
PRIM_X = {
    '∋': -8.8,   # alkali metals  (far left)
    '⊞': -7.2,   # alkaline earths + group 15 excl N,P
    '⊢': -5.5,   # group 13
    '⊣': -4.1,   # group 14 excl C
    '<':  4.1,   # group 16 excl O,S
    '⊤':  5.4,   # halogens (F-state noble metals Pt,Au handled as thread)
    '⊥':  7.0,   # d-block non-thread (sub-f at 8.8)
    '⊙':  9.5,   # actinides (noble gases handled separately)
}
PRIM_X_F = 8.8   # f-block lanthanides sub-arm of ⊥


def compute_satellite_positions():
    shown = set(THREAD_POS) | set(T_SAT_POS) | set(NOBLE_POS)
    groups = defaultdict(lambda: defaultdict(list))

    for sym, (Z, per, col, blk) in ELEMENTS.items():
        if sym in shown:
            continue
        prim = PRIM_LABEL.get(sym, '⊥')
        # Noble gases go to NOBLE_POS, not satellite
        if prim == '⊙' and sym in F_SET:
            continue
        key = (prim, 'f' if blk == 'f' else 'd')
        groups[key][per].append((Z, sym))

    positions = {}
    SAT_SPACING = 0.52  # cm horizontal spread within a (prim, period) group

    for (prim, subtype), per_dict in groups.items():
        if prim not in PRIM_X:
            x_base = 7.0
        else:
            x_base = PRIM_X[prim]
        if subtype == 'f' and prim == '⊥':
            x_base = PRIM_X_F

        for per, elems in per_dict.items():
            elems.sort()
            n = len(elems)
            y = -per * 1.55
            for i, (Z, sym) in enumerate(elems):
                x = x_base + (i - (n - 1) / 2) * SAT_SPACING
                positions[sym] = (x, y)

    return positions


# ─── LaTeX generation ─────────────────────────────────────────────────────────

PREAMBLE = ('\\documentclass{article}\n'
            '\\usepackage{fontspec}\n'
            '\\usepackage[paperwidth=26cm,paperheight=26cm,margin=0.7cm]{geometry}\n'
            '\\usepackage[warnings-off={mathtools-colon,mathtools-overbracket}]{unicode-math}\n'
            '\\ExplSyntaxOn\\msg_redirect_name:nnn{lualatex-math}{wrong-meaning}{none}\\ExplSyntaxOff\n'
            '\\setmathfont{Latin Modern Math}\n'
            '\\newfontface\\igprimfont{Everson Mono}\n'
            '\\usepackage{tikz}\n'
            '\\usetikzlibrary{backgrounds,calc}\n'
            '\\pagestyle{empty}\n'
            '\\begin{document}\n'
            '\\centering\n')


def fde_colors(sym):
    fde = FDE_CLASS.get(sym, 'B')
    fill = {'T': 'green!55!black', 'F': 'black!40',
            'B': 'orange!70!red',  'N': 'black!10'}[fde]
    tc   = {'T': 'white', 'F': 'white', 'B': 'white', 'N': 'black!28'}[fde]
    return fill, tc


def thread_node(sym, x, y, r_cm):
    fill, tc = fde_colors(sym)
    Z = ELEMENTS[sym][0]
    is_org = sym in ORGANIC_SET
    dc = 'red!65!black' if is_org else 'blue!55!black'
    return (f'\\node[circle,fill={fill},draw={dc},line width=1.6pt,'
            f'minimum size={2*r_cm:.2f}cm,inner sep=0pt]'
            f' at ({x:.2f}cm,{y:.2f}cm)'
            f' {{\\fontsize{{6}}{{6}}\\selectfont'
            f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')


def sat_node(sym, x, y, r_cm, lw='0.35pt'):
    fill, tc = fde_colors(sym)
    dc = 'black!22'
    rad = RADIOACTIVE
    if sym in rad:
        dc = 'red!45'
        lw = '0.5pt'
    return (f'\\node[circle,fill={fill},draw={dc},line width={lw},'
            f'minimum size={2*r_cm:.2f}cm,inner sep=0pt]'
            f' at ({x:.2f}cm,{y:.2f}cm)'
            f' {{\\fontsize{{3.6}}{{3.6}}\\selectfont'
            f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')


def generate_tex():
    sat_pos = compute_satellite_positions()
    L = [PREAMBLE, '\\begin{tikzpicture}\n']

    # ── Background: satellite elements (N first so they render behind) ────────
    for fde_class in ('N', 'B', 'F'):
        for sym, (Z, per, col, blk) in ELEMENTS.items():
            if (FDE_CLASS.get(sym, 'B') != fde_class
                    or sym in THREAD_POS
                    or sym in T_SAT_POS
                    or sym in NOBLE_POS):
                continue
            if sym not in sat_pos:
                continue
            x, y = sat_pos[sym]
            r = 0.18 if fde_class == 'N' else 0.22
            L.append(sat_node(sym, x, y, r))

    # ── Noble gas column (F-state, isolated) ─────────────────────────────────
    L.append(f'\\node[font={{\\fontsize{{5}}{{5}}\\selectfont}},text=black!35,'
             f'anchor=south] at ({X_NOBLE:.2f}cm, 0.6cm) {{no $\\delta$}};\n')
    for sym, (x, y) in NOBLE_POS.items():
        fill, tc = fde_colors(sym)
        L.append(f'\\node[circle,fill={fill},draw=black!35,line width=0.6pt,'
                 f'minimum size=0.52cm,inner sep=0pt]'
                 f' at ({x:.2f}cm,{y:.2f}cm)'
                 f' {{\\fontsize{{4.5}}{{4.5}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── T-state satellite nodes (Ru, Os) ─────────────────────────────────────
    for sym, (x, y) in T_SAT_POS.items():
        fill, tc = fde_colors(sym)
        # Connect to metallic thread with dotted line
        L.append(f'\\draw[green!50!black,line width=0.6pt,dotted]'
                 f' ({X_MET:.2f}cm,{y:.2f}cm) -- ({x-0.38:.2f}cm,{y:.2f}cm);\n')
        L.append(f'\\node[circle,fill={fill},draw=green!45!black,line width=1.0pt,'
                 f'minimum size=0.72cm,inner sep=0pt]'
                 f' at ({x:.2f}cm,{y:.2f}cm)'
                 f' {{\\fontsize{{5.2}}{{5.2}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Thread paths (draw before nodes so nodes sit on top) ──────────────────
    org_coords = ' '.join(f'({X_ORG:.2f}cm,{org_y(i):.2f}cm)'
                          for i in range(len(ORGANIC_THREAD)))
    met_coords = ' '.join(f'({X_MET:.2f}cm,{met_y(i):.2f}cm)'
                          for i in range(len(METALLIC_THREAD)))

    L.append(f'\\draw[red!25,line width=9pt,line cap=round,opacity=0.45]'
             f' {org_coords};\n')
    L.append(f'\\draw[blue!25,line width=9pt,line cap=round,opacity=0.45]'
             f' {met_coords};\n')

    # ── Enzyme bridge arcs ────────────────────────────────────────────────────
    # S = ORGANIC index 4, Zn = METALLIC index 2
    sx, sy   = THREAD_POS['S']
    znx, zny = THREAD_POS['Zn']
    # Fe = METALLIC index 0, N = ORGANIC index 2
    fex, fey = THREAD_POS['Fe']
    nx,  ny  = THREAD_POS['N']

    # S→Zn arc (over-crossing: curves upward between the two threads)
    ctrl1x = (sx + znx) / 2
    ctrl1y = (sy + zny) / 2 + 1.0
    L.append(f'\\draw[purple!65!black,line width=1.5pt]'
             f' ({sx:.2f}cm,{sy:.2f}cm)'
             f' .. controls ({ctrl1x:.2f}cm,{ctrl1y:.2f}cm) ..'
             f' ({znx:.2f}cm,{zny:.2f}cm);\n')
    L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=purple!60!black]'
             f' at ({ctrl1x:.2f}cm,{ctrl1y+0.22:.2f}cm) {{$\\sigma_1$}};\n')

    # Fe→N arc (under-crossing: curves below/straight)
    ctrl2x = (fex + nx) / 2
    ctrl2y = (fey + ny) / 2 - 0.8
    L.append(f'\\draw[purple!65!black,line width=1.5pt,dashed]'
             f' ({fex:.2f}cm,{fey:.2f}cm)'
             f' .. controls ({ctrl2x:.2f}cm,{ctrl2y:.2f}cm) ..'
             f' ({nx:.2f}cm,{ny:.2f}cm);\n')
    L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=purple!60!black]'
             f' at ({ctrl2x:.2f}cm,{ctrl2y-0.22:.2f}cm) {{$\\sigma_1^{{-1}}$}};\n')

    # ── Thread element nodes (on top) ─────────────────────────────────────────
    for sym, (x, y) in THREAD_POS.items():
        L.append(thread_node(sym, x, y, 0.55))

    # ── Thread element labels (Z above each node) ─────────────────────────────
    for sym, (x, y) in THREAD_POS.items():
        Z = ELEMENTS[sym][0]
        L.append(f'\\node[font={{\\fontsize{{4}}{{4}}\\selectfont}},text=black!40]'
                 f' at ({x:.2f}cm,{y+0.70:.2f}cm) {{{Z}}};\n')

    # ── Thread lane headers ────────────────────────────────────────────────────
    top_y = 0.9
    L.append(f'\\node[font={{\\fontsize{{7}}{{7}}\\selectfont\\bfseries}},text=red!55!black]'
             f' at ({X_ORG:.2f}cm,{top_y:.2f}cm) {{organic}};\n')
    L.append(f'\\node[font={{\\fontsize{{7}}{{7}}\\selectfont\\bfseries}},text=blue!50!black]'
             f' at ({X_MET:.2f}cm,{top_y:.2f}cm) {{metallic}};\n')
    L.append(f'\\node[font={{\\fontsize{{6}}{{6}}\\selectfont}},text=black!35]'
             f' at ({X_NOBLE:.2f}cm,{top_y:.2f}cm) {{noble}};\n')

    # ── Title ─────────────────────────────────────────────────────────────────
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!65]'
             ' at (0,1.85cm)'
             ' {Periodic Table of Elements --- Frobenius Spine'
             ' ($\\mu\\circ\\delta=\\mathrm{id}$ as backbone)};\n')

    # ── Legend ────────────────────────────────────────────────────────────────
    bot_y = met_y(len(METALLIC_THREAD) - 1) - 1.3
    lx0 = -6.0
    entries = [
        ('green!55!black', 'white',    'T: always Frobenius'),
        ('orange!70!red',  'white',    'B: context Frobenius'),
        ('black!40',       'white',    'F: no $\\delta$'),
        ('black!10',       'black!28', 'N: no stable role'),
    ]
    for i, (fc, tc, lbl) in enumerate(entries):
        lx = lx0 + i * 3.1
        L.append(f'\\node[circle,fill={fc},draw=black!18,line width=0.3pt,'
                 f'minimum size=0.26cm,inner sep=0pt]'
                 f' at ({lx:.2f}cm,{bot_y:.2f}cm) {{}};\n'
                 f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
                 f'anchor=west] at ({lx+0.17:.2f}cm,{bot_y:.2f}cm) {{{lbl}}};\n')

    bot_y2 = bot_y - 0.55
    L.append(f'\\draw[purple!65!black,line width=1.5pt] ({lx0:.2f}cm,{bot_y2:.2f}cm)'
             f' -- ({lx0+0.55:.2f}cm,{bot_y2:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
             f'anchor=west] at ({lx0+0.62:.2f}cm,{bot_y2:.2f}cm)'
             f' {{$\\sigma_1$ arc: enzyme bridge S$\\to$Zn (metalloenzyme)}};\n'
             f'\\draw[purple!65!black,line width=1.5pt,dashed]'
             f' ({lx0+7.5:.2f}cm,{bot_y2:.2f}cm)'
             f' -- ({lx0+8.05:.2f}cm,{bot_y2:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
             f'anchor=west] at ({lx0+8.12:.2f}cm,{bot_y2:.2f}cm)'
             f' {{$\\sigma_1^{{-1}}$ arc: Fe$\\to$N (porphyrin/haem)}};\n')

    L.append('\\end{tikzpicture}\n\\end{document}\n')
    return ''.join(L)


if __name__ == '__main__':
    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_spine.tex'
    pdf_path = out_dir / 'ig_pt_spine.pdf'

    tex = generate_tex()
    tex_path.write_text(tex)
    print(f'Wrote {tex_path}')

    result = subprocess.run(
        ['lualatex', '--interaction=nonstopmode',
         '--output-directory', str(out_dir), str(tex_path)],
        capture_output=True, text=True, cwd=str(out_dir),
    )
    if result.returncode == 0:
        print(f'Compiled → {pdf_path}')
        pdfs = out_dir / 'pdfs'
        if pdfs.exists():
            shutil.copy(pdf_path, pdfs / 'ig_pt_spine.pdf')
            print(f'Copied → {pdfs}/ig_pt_spine.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print('--- last 2000 chars ---')
        print(result.stdout[-2000:])
