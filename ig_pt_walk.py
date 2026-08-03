#!/usr/bin/env python3
"""
Design Combined — Walk on the Icosahedron.

The Frobenius thread is a walk on the icosahedron: each thread element sits at
(or near) the vertex of its dominant IG primitive, and the thread path visits
primitive vertices in sequence. All other elements cluster near their primitive's
vertex. The icosahedron wireframe is the ambient grammar structure; the walk is
what chemistry selects from it.

Thread walk (prim sequence):
  ⊥ → < → Σ → ⊣ → < → Σ   (organic: H O N C S P)
  ──enzyme bridge──
  ⊥×8 → ⊤×2               (metallic: Fe Ni Zn Mo Rh Pd W Ir Pt Au)

The organic thread zigzags between <-Σ-⊣; metallic plants at ⊥ then tips to ⊤.
"""

import math, subprocess, shutil
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD
from ig_pt_3d_utils import (
    ICO_VERTS, ICO_EDGES, PRIM_VERT, VERT_PRIM,
    proj, zdepth, ico_element_positions,
    perp_basis, _norm3, _cross,
    FDE_FILL, FDE_TEXT, ORGANIC_SET, METALLIC_SET, preamble,
    R_PERIOD, CLUST_SPC,
)

SCALE = 2.0
NODE_D_THREAD = 1.05   # cm — thread element nodes
NODE_D_SAT    = 0.40   # cm — satellite element nodes

# ─── Thread element 3D positions ─────────────────────────────────────────────
# Each thread element sits at its primitive vertex, offset by index within the
# group (multiple thread elements on the same primitive are staggered).

def thread_positions_3d():
    pos = {}
    # Count how many thread elements share each primitive vertex
    from collections import Counter
    prim_counts = Counter(PRIM_LABEL.get(s, '⊥') for s in (ORGANIC_THREAD + METALLIC_THREAD))

    prim_idx = defaultdict(int)   # how many already placed at this prim

    full_thread = list(ORGANIC_THREAD) + list(METALLIC_THREAD)
    for sym in full_thread:
        prim = PRIM_LABEL.get(sym, '⊥')
        if prim not in PRIM_VERT:
            prim = '⊥'
        vi = PRIM_VERT[prim]
        v  = ICO_VERTS[vi]
        n  = prim_counts[prim]
        i  = prim_idx[prim]
        prim_idx[prim] += 1

        # Place at period radius on the vertex arm
        per = ELEMENTS[sym][1]
        r   = per * R_PERIOD

        # Cluster offset perpendicular to arm (fan out if n > 1)
        u, w = perp_basis(v)
        SPC = CLUST_SPC * 1.5    # slightly wider for thread nodes (they're bigger)
        cols = min(n, 4)
        rows = math.ceil(n / cols)
        row   = i // cols
        col_i = i  % cols
        pu = (col_i - (cols-1)/2) * SPC
        pw = (row   - (rows-1)/2) * SPC

        pos[sym] = [r*v[k] + pu*u[k] + pw*w[k] for k in range(3)]

    return pos


# ─── Walk path in 3D ─────────────────────────────────────────────────────────
def walk_path_3d(thread_pos):
    """Return list of 3D points tracing the thread walk in order."""
    full = list(ORGANIC_THREAD) + list(METALLIC_THREAD)
    return [thread_pos[s] for s in full]


# ─── Smooth curve through control points ─────────────────────────────────────
def smooth_curve_tikz(pts_3d, color, lw='1.8pt', dash=''):
    coords = ' '.join(
        f'({proj(p, SCALE)[0]:.3f}cm,{proj(p, SCALE)[1]:.3f}cm)'
        for p in pts_3d
    )
    style = f'{dash}{color},line width={lw}'
    return f'\\draw[{style}] plot[smooth,tension=0.5] coordinates {{{coords}}};\n'


def generate_tex():
    # All element positions on icosahedron
    all_pos3d = ico_element_positions()
    # Thread-specific positions (override for thread elements)
    thread_pos3d = thread_positions_3d()
    # Merge: thread elements use thread_pos3d
    for sym, pos in thread_pos3d.items():
        all_pos3d[sym] = pos

    L = [preamble('24cm', '24cm'), '\\begin{tikzpicture}\n']

    # ── Icosahedron wireframe (back edges dashed, faint) ──────────────────────
    edges_d = []
    for i, j in ICO_EDGES:
        mid = [(a+b)/2 for a,b in zip(ICO_VERTS[i], ICO_VERTS[j])]
        edges_d.append((zdepth(mid), i, j))
    edges_d.sort()

    for d, i, j in edges_d:
        p1 = proj(ICO_VERTS[i], SCALE)
        p2 = proj(ICO_VERTS[j], SCALE)
        back = d < 0
        col  = 'black!8' if back else 'black!15'
        sty  = 'dashed,' if back else ''
        L.append(f'\\draw[{sty}{col},line width=0.3pt]'
                 f' ({p1[0]:.3f}cm,{p1[1]:.3f}cm) -- ({p2[0]:.3f}cm,{p2[1]:.3f}cm);\n')

    # ── Primitive arm axes ────────────────────────────────────────────────────
    for prim, vi in PRIM_VERT.items():
        v = ICO_VERTS[vi]
        d = zdepth(v)
        empty = prim in ('◻','>','∈','⋈')
        col = 'black!6' if empty else ('black!10' if d < 0 else 'black!16')
        p2  = proj([c * 5.4 for c in v], SCALE)
        L.append(f'\\draw[{col},line width=0.35pt] (0,0) -- ({p2[0]:.3f}cm,{p2[1]:.3f}cm);\n')

    # ── Satellite elements (back-to-front, small) ─────────────────────────────
    shown_thread = set(ORGANIC_THREAD) | set(METALLIC_THREAD)
    sats = [(zdepth(pos), sym, pos)
            for sym, pos in all_pos3d.items()
            if sym not in shown_thread]
    sats.sort()

    for d, sym, pos in sats:
        x2, y2 = proj(pos, SCALE)
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        op   = max(0.25, min(0.75, 0.50 + d * 0.12))
        L.append(f'\\node[circle,fill={fill},draw=black!18,line width=0.28pt,'
                 f'minimum size={NODE_D_SAT:.2f}cm,inner sep=0pt,opacity={op:.2f}]'
                 f' at ({x2:.3f}cm,{y2:.3f}cm)'
                 f' {{\\fontsize{{3.5}}{{3.5}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Walk path: organic segment (red) ─────────────────────────────────────
    org_pts = [thread_pos3d[s] for s in ORGANIC_THREAD]
    L.append(smooth_curve_tikz(org_pts, 'red!65!black', lw='1.8pt'))

    # ── Enzyme bridge (organic end → metallic start, purple) ─────────────────
    bridge_pts = [thread_pos3d[ORGANIC_THREAD[-1]], thread_pos3d[METALLIC_THREAD[0]]]
    ps  = proj(bridge_pts[0], SCALE)
    pe  = proj(bridge_pts[1], SCALE)
    L.append(f'\\draw[purple!65!black,line width=1.8pt]'
             f' ({ps[0]:.3f}cm,{ps[1]:.3f}cm) -- ({pe[0]:.3f}cm,{pe[1]:.3f}cm);\n')
    mid_b = [(a+b)/2 for a,b in zip(bridge_pts[0], bridge_pts[1])]
    pm    = proj(mid_b, SCALE)
    L.append(f'\\node[font={{\\fontsize{{5}}{{5}}\\selectfont}},text=purple!60!black]'
             f' at ({pm[0]+0.4:.3f}cm,{pm[1]:.3f}cm) {{enzyme bridge}};\n')

    # ── Walk path: metallic segment (blue) ────────────────────────────────────
    met_pts = [thread_pos3d[s] for s in METALLIC_THREAD]
    L.append(smooth_curve_tikz(met_pts, 'blue!55!black', lw='1.8pt'))

    # ── Thread element nodes (back-to-front, large) ───────────────────────────
    thread_syms = list(ORGANIC_THREAD) + list(METALLIC_THREAD)
    thread_d = [(zdepth(thread_pos3d[s]), s) for s in thread_syms]
    thread_d.sort()

    for d, sym in thread_d:
        x2, y2 = proj(thread_pos3d[sym], SCALE)
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        is_org = sym in ORGANIC_SET
        dc   = 'red!65!black' if is_org else 'blue!55!black'
        L.append(f'\\node[circle,fill={fill},draw={dc},line width=1.5pt,'
                 f'minimum size={NODE_D_THREAD:.2f}cm,inner sep=0pt]'
                 f' at ({x2:.3f}cm,{y2:.3f}cm)'
                 f' {{\\fontsize{{6}}{{6}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Primitive vertex labels ───────────────────────────────────────────────
    vert_d = [(zdepth(ICO_VERTS[vi]), vi, prim)
              for prim, vi in PRIM_VERT.items()]
    vert_d.sort()

    for d, vi, prim in vert_d:
        v    = ICO_VERTS[vi]
        r_lbl = 5.3
        lp   = proj([c * r_lbl for c in v], SCALE)
        empty = prim in ('◻','>','∈','⋈')
        alpha = '!22' if (d < -0.1 or empty) else '!52'
        L.append(f'\\node[font={{\\igprimfont\\fontsize{{12}}{{12}}\\selectfont}},text=black{alpha}]'
                 f' at ({lp[0]:.3f}cm,{lp[1]:.3f}cm) {{{prim}}};\n')

    # ── Title ─────────────────────────────────────────────────────────────────
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!60]'
             ' at (0,10.6cm)'
             ' {IG Periodic Table --- Frobenius Walk on the Icosahedron};\n')

    # ── Walk annotation (which primitives visited, in order) ──────────────────
    walk_prims = [PRIM_LABEL.get(s,'⊥') for s in (list(ORGANIC_THREAD)+list(METALLIC_THREAD))]
    walk_str   = ' $\\to$ '.join(f'{{\\igprimfont {p}}}' for p in walk_prims)
    ann_y = 10.0
    L.append(f'\\node[font={{\\fontsize{{5}}{{5}}\\selectfont}},text=black!45]'
             f' at (0,{ann_y:.2f}cm) {{walk: {walk_str}}};\n')

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

    L.append('\\end{tikzpicture}\n\\end{document}\n')
    return ''.join(L)


if __name__ == '__main__':
    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_walk.tex'
    pdf_path = out_dir / 'ig_pt_walk.pdf'

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
            shutil.copy(pdf_path, pdfs / 'ig_pt_walk.pdf')
            print(f'Copied → pdfs/ig_pt_walk.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print(result.stdout[-2000:])
