#!/usr/bin/env python3
"""
Design C-3D — Icosahedral Radial.
12 IG primitives at icosahedron vertices; elements cluster at their primitive's
vertex, at radius = period × scale. Projected isometrically.
Empty arms (◻ > ∈ ⋈) form a cold cap on the back hemisphere.
"""

import math, subprocess, shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD
from ig_pt_3d_utils import (
    ICO_VERTS, ICO_EDGES, PRIM_VERT, VERT_PRIM,
    proj, zdepth, ico_element_positions,
    FDE_FILL, FDE_TEXT, ORGANIC_SET, METALLIC_SET, preamble,
)

NODE_D  = 0.42   # cm diameter for element nodes
SCALE   = 2.0    # projection scale: 1 3D-unit → 2 cm


def generate_tex():
    pos3d = ico_element_positions()
    L = [preamble('24cm', '24cm'), '\\begin{tikzpicture}\n']

    # ── Icosahedron wireframe ─────────────────────────────────────────────────
    # Draw edges back-to-front; back edges dashed
    edges_with_depth = []
    for i, j in ICO_EDGES:
        mid = [(a+b)/2 for a,b in zip(ICO_VERTS[i], ICO_VERTS[j])]
        d = zdepth(mid)
        edges_with_depth.append((d, i, j))
    edges_with_depth.sort()  # back first

    for d, i, j in edges_with_depth:
        p1 = proj(ICO_VERTS[i], SCALE)
        p2 = proj(ICO_VERTS[j], SCALE)
        is_back = d < 0
        style = 'dashed,' if is_back else ''
        col   = 'black!10' if is_back else 'black!18'
        lw    = '0.3pt'
        L.append(f'\\draw[{style}{col},line width={lw}]'
                 f' ({p1[0]:.3f}cm,{p1[1]:.3f}cm) -- ({p2[0]:.3f}cm,{p2[1]:.3f}cm);\n')

    # ── Primitive arm lines from origin ──────────────────────────────────────
    for prim, vi in PRIM_VERT.items():
        v = ICO_VERTS[vi]
        d = zdepth(v)
        is_empty = prim in ('◻','>','∈','⋈')
        if is_empty:
            col = 'black!8'
        elif d < -0.1:
            col = 'black!12'
        else:
            col = 'black!20'
        p = proj([c * 5.6 for c in v], SCALE)  # arm line to r=11.2cm
        L.append(f'\\draw[{col},line width=0.4pt] (0,0) -- ({p[0]:.3f}cm,{p[1]:.3f}cm);\n')

    # ── Period shells (faint arcs — draw as small circles at each vertex-period) ─
    # (skip for cleanliness; the clustering itself shows period structure)

    # ── Primitive vertex labels ───────────────────────────────────────────────
    vert_depths = [(zdepth(ICO_VERTS[vi]), vi, prim)
                   for prim, vi in PRIM_VERT.items()]
    vert_depths.sort()
    for d, vi, prim in vert_depths:
        v = ICO_VERTS[vi]
        # Push label outward past the element cluster (max period=7 at R=3.64cm)
        r_lbl = 5.4   # labels at 5.4*2.0=10.8cm from centre
        lp = proj([c * r_lbl for c in v], SCALE)
        is_empty = prim in ('◻','>','∈','⋈')
        opacity = '!30' if (d < -0.15 or is_empty) else '!55'
        L.append(f'\\node[font={{\\igprimfont\\fontsize{{12}}{{12}}\\selectfont}},text=black{opacity}]'
                 f' at ({lp[0]:.3f}cm,{lp[1]:.3f}cm) {{{prim}}};\n')

    # ── Element nodes (back to front) ─────────────────────────────────────────
    elems_with_depth = []
    for sym in ELEMENTS:
        if sym in pos3d:
            d = zdepth(pos3d[sym])
            elems_with_depth.append((d, sym))
    elems_with_depth.sort()

    for d, sym in elems_with_depth:
        x2, y2 = proj(pos3d[sym], SCALE)
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        is_org = sym in ORGANIC_SET
        is_met = sym in METALLIC_SET
        lw = '1.4pt' if (is_org or is_met) else '0.35pt'
        dc = ('red!65!black' if is_org else 'blue!55!black' if is_met else 'black!20')
        # Depth-based opacity: back elements slightly faded
        opacity = max(0.35, min(1.0, 0.65 + d * 0.18))
        L.append(f'\\node[circle,fill={fill},draw={dc},line width={lw},'
                 f'minimum size={NODE_D:.2f}cm,inner sep=0pt,opacity={opacity:.2f}]'
                 f' at ({x2:.3f}cm,{y2:.3f}cm)'
                 f' {{\\fontsize{{3.6}}{{3.6}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Icosahedron vertex dots (over elements at each vertex) ────────────────
    for d, vi, prim in vert_depths:
        v   = ICO_VERTS[vi]
        p2  = proj(v, SCALE)
        col = 'black!35' if prim not in ('◻','>','∈','⋈') else 'black!15'
        L.append(f'\\node[circle,fill={col},minimum size=0.12cm,inner sep=0pt]'
                 f' at ({p2[0]:.3f}cm,{p2[1]:.3f}cm) {{}};\n')

    # ── Title ─────────────────────────────────────────────────────────────────
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!60]'
             ' at (0,10.6cm)'
             ' {IG Periodic Table --- Icosahedral Radial'
             ' (12 primitives at icosahedron vertices, $\\Gamma$-radius)};\n')

    # ── Legend ────────────────────────────────────────────────────────────────
    lx0, ly0 = -5.8, -10.6
    for i, (fc, tc, lbl) in enumerate([
        ('green!55!black','white','T: always Frobenius'),
        ('orange!75!red', 'white','B: context Frobenius'),
        ('black!42',      'white','F: no $\\delta$'),
        ('black!10',      'black!28','N: no stable role'),
    ]):
        lx = lx0 + i*3.0
        L.append(f'\\node[circle,fill={fc},draw=black!18,line width=0.3pt,'
                 f'minimum size=0.26cm,inner sep=0pt] at ({lx:.2f}cm,{ly0:.2f}cm) {{}};\n'
                 f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
                 f'anchor=west] at ({lx+0.17:.2f}cm,{ly0:.2f}cm) {{{lbl}}};\n')

    ly1 = ly0 - 0.52
    L.append(f'\\draw[red!65!black,line width=1.4pt] ({lx0:.2f}cm,{ly1:.2f}cm)'
             f' -- ({lx0+0.5:.2f}cm,{ly1:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
             f'anchor=west] at ({lx0+0.58:.2f}cm,{ly1:.2f}cm) {{organic thread}};\n'
             f'\\draw[blue!55!black,line width=1.4pt] ({lx0+4.5:.2f}cm,{ly1:.2f}cm)'
             f' -- ({lx0+5.0:.2f}cm,{ly1:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,'
             f'anchor=west] at ({lx0+5.08:.2f}cm,{ly1:.2f}cm) {{metallic thread}};\n')

    L.append('\\end{tikzpicture}\n\\end{document}\n')
    return ''.join(L)


if __name__ == '__main__':
    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_ico.tex'
    pdf_path = out_dir / 'ig_pt_ico.pdf'

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
            shutil.copy(pdf_path, pdfs / 'ig_pt_ico.pdf')
            print(f'Copied → pdfs/ig_pt_ico.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print(result.stdout[-2000:])

