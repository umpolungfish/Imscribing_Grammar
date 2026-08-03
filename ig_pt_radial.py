#!/usr/bin/env python3
"""
Design C — 12-Primitive Radial periodic arrangement.

Each element sits on the arm of its dominant IG primitive.
Radial distance from centre = period (∈).
Empty arms (◻ > ∈ ⋈) are structurally meaningful: no element incarnates
those primitives as its dominant character at the atomic level.
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

R_SCALE = 1.38    # cm per period level
NODE_D  = 0.44    # node circle diameter cm

# Arm angles in TikZ convention (CCW from east).
# Populated arms on right/top; empty arms cluster on left.
ARM_DEG = {
    '⊥': 90,   # up       — d-block, f-lanthanides, H
    '⊙': 60,   # UR       — noble gases, He, actinides
    '⊤': 30,   # R-upper  — halogens, Pt, Au
    '<':  0,   # right    — group 16
    '⊞': 330,  # R-lower  — alkaline earths + group 15
    '∋': 300,  # L-lower  — alkali metals
    '⊣': 270,  # down     — group 14
    '⊢': 240,  # DL       — group 13
    '◻': 210,  # L-lower  — empty
    '>': 180,  # left     — empty
    '∈': 150,  # L-upper  — empty
    '⋈': 120,  # UL       — empty
}

FDE_FILL = {
    'T': 'green!55!black',
    'F': 'black!42',
    'B': 'orange!75!red',
    'N': 'black!11',
}
FDE_TEXT = {
    'T': 'white',
    'F': 'white',
    'B': 'white',
    'N': 'black!30',
}

ORGANIC_SET  = set(ORGANIC_THREAD)
METALLIC_SET = set(METALLIC_THREAD)


def place_elements():
    groups = defaultdict(list)
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        prim = PRIM_LABEL.get(sym, '⊥')
        if prim not in ARM_DEG:
            prim = '⊥'
        groups[(prim, per)].append((Z, sym))

    positions = {}
    SPACING = 0.50  # cm between nodes

    for (prim, per), elems in groups.items():
        elems.sort()
        n = len(elems)
        theta = math.radians(ARM_DEG[prim])
        r_base = per * R_SCALE

        arm_x,  arm_y  =  math.cos(theta),  math.sin(theta)
        perp_x, perp_y = -math.sin(theta),   math.cos(theta)

        cols = min(n, 8)
        rows = math.ceil(n / cols)

        for i, (Z, sym) in enumerate(elems):
            row   = i // cols
            col_i = i  % cols
            perp_off   = (col_i - (cols - 1) / 2) * SPACING
            radial_off = (row   - (rows - 1) / 2) * SPACING
            x = r_base * arm_x + perp_off * perp_x + radial_off * arm_x
            y = r_base * arm_y + perp_off * perp_y + radial_off * arm_y
            positions[sym] = (x, y)

    return positions


def generate_tex():
    positions = place_elements()
    L = []

    L.append('\\documentclass{article}\n'
             '\\usepackage{fontspec}\n'
             '\\usepackage[paperwidth=24cm,paperheight=24cm,margin=0.6cm]{geometry}\n'
             '\\usepackage[warnings-off={mathtools-colon,mathtools-overbracket}]{unicode-math}\n'
             '\\ExplSyntaxOn\\msg_redirect_name:nnn{lualatex-math}{wrong-meaning}{none}\\ExplSyntaxOff\n'
             '\\setmathfont{Latin Modern Math}\n'
             '\\newfontface\\igprimfont{Everson Mono}\n'
             '\\usepackage{tikz}\n'
             '\\usetikzlibrary{backgrounds}\n'
             '\\pagestyle{empty}\n'
             '\\begin{document}\n'
             '\\centering\n'
             '\\begin{tikzpicture}\n')

    # Arm guidelines
    for prim, deg in ARM_DEG.items():
        t = math.radians(deg)
        x2 = 10.5 * math.cos(t)
        y2 = 10.5 * math.sin(t)
        L.append(f'\\draw[black!9,line width=0.4pt] (0,0) -- ({x2:.3f}cm,{y2:.3f}cm);\n')

    # Period rings
    for per in range(1, 8):
        r = per * R_SCALE
        L.append(f'\\draw[black!8,line width=0.3pt] (0,0) circle ({r:.3f}cm);\n')

    # Arm labels
    for prim, deg in ARM_DEG.items():
        t = math.radians(deg)
        r_lbl = 10.0
        lx = r_lbl * math.cos(t)
        ly = r_lbl * math.sin(t)
        L.append(f'\\node[font={{\\igprimfont\\fontsize{{13}}{{13}}\\selectfont}},text=black!38]'
                 f' at ({lx:.3f}cm,{ly:.3f}cm) {{{prim}}};\n')

    # Period ring labels (near the < arm at 0°)
    for per in range(1, 8):
        r = per * R_SCALE + 0.08
        L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=black!22,'
                 f'anchor=south west] at ({r:.3f}cm,0.08cm) {{\\textit{{n={per}}}}};\n')

    # Draw nodes — layer order: N, B, F, T, thread on top
    def draw_node(sym):
        if sym not in positions:
            return ''
        x, y = positions[sym]
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        is_org = sym in ORGANIC_SET
        is_met = sym in METALLIC_SET
        lw = '1.4pt' if (is_org or is_met) else '0.35pt'
        dc  = ('red!65!black'  if is_org else
               'blue!55!black' if is_met else
               'black!22')
        return (f'\\node[circle,fill={fill},draw={dc},line width={lw},'
                f'minimum size={NODE_D:.2f}cm,inner sep=0pt]'
                f' at ({x:.3f}cm,{y:.3f}cm)'
                f' {{\\fontsize{{3.8}}{{3.8}}\\selectfont'
                f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    for fde_class in ('N', 'B', 'F', 'T'):
        for sym in ELEMENTS:
            if (FDE_CLASS.get(sym, 'B') == fde_class
                    and sym not in ORGANIC_SET
                    and sym not in METALLIC_SET):
                L.append(draw_node(sym))

    for sym in ORGANIC_THREAD:
        if sym in ELEMENTS:
            L.append(draw_node(sym))
    for sym in METALLIC_THREAD:
        if sym in ELEMENTS:
            L.append(draw_node(sym))

    # Centre label
    L.append('\\node[font={\\fontsize{7}{9}\\selectfont\\bfseries},text=black!50,'
             'align=center] at (0,0) {IG\\\\Radial};\n')

    # Title
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!65]'
             ' at (0,10.8cm) {Periodic Table of Elements'
             ' --- IG Primitive Radial ($\\Gamma$-distance from centre)};\n')

    # FDE legend
    lx0, ly0 = -5.8, -10.8
    fde_entries = [
        ('green!55!black', 'white',    'T: always Frobenius (PGMs)'),
        ('orange!75!red',  'white',    'B: context Frobenius'),
        ('black!42',       'white',    'F: no $\\delta$ (noble gases)'),
        ('black!11',       'black!30', 'N: no stable role (synthetic)'),
    ]
    for i, (fc, tc, lbl) in enumerate(fde_entries):
        lx = lx0 + i * 3.0
        L.append(f'\\node[circle,fill={fc},draw=black!18,line width=0.3pt,'
                 f'minimum size=0.28cm,inner sep=0pt] at ({lx:.2f}cm,{ly0:.2f}cm) {{}};\n'
                 f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!58,'
                 f'anchor=west] at ({lx+0.18:.2f}cm,{ly0:.2f}cm) {{{lbl}}};\n')

    ly1 = ly0 - 0.55
    L.append(f'\\draw[red!65!black,line width=1.4pt] ({lx0:.2f}cm,{ly1:.2f}cm)'
             f' -- ({lx0+0.55:.2f}cm,{ly1:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!58,anchor=west]'
             f' at ({lx0+0.62:.2f}cm,{ly1:.2f}cm) {{organic thread: H O N C S P}};\n'
             f'\\draw[blue!55!black,line width=1.4pt] ({lx0+5.2:.2f}cm,{ly1:.2f}cm)'
             f' -- ({lx0+5.75:.2f}cm,{ly1:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!58,anchor=west]'
             f' at ({lx0+5.82:.2f}cm,{ly1:.2f}cm)'
             f' {{metallic thread: Fe Ni Zn Mo Rh Pd W Ir Pt Au}};\n')

    L.append('\\end{tikzpicture}\n\\end{document}\n')
    return ''.join(L)


if __name__ == '__main__':
    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_radial.tex'
    pdf_path = out_dir / 'ig_pt_radial.pdf'

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
            shutil.copy(pdf_path, pdfs / 'ig_pt_radial.pdf')
            print(f'Copied → {pdfs}/ig_pt_radial.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print('--- last 2000 chars of log ---')
        print(result.stdout[-2000:])
