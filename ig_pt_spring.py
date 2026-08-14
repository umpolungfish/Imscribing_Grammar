#!/usr/bin/env python3
"""
Design Spring — Force-directed IG periodic table.

The layout is derived entirely from graph structure — no manual coordinates.
Nodes: 118 elements + 12 primitive anchors.
Edges encode IG relationships; the spring algorithm finds the embedding.

Edge types and weights:
  element → primitive    weight 4.0   (dominant prim pull)
  thread sequence        weight 7.0   (Frobenius path cohesion)
  enzyme bridge          weight 4.0   (S-P → Fe bridge)
  icosahedron edges      weight 2.5   (primitive adjacency from crystal structure)
  same period            weight 0.3   (weak ∈-ring pull)
  same block             weight 0.5   (◻-family pull)

Layout: Kamada-Kawai (minimises graph-theoretic stress).
Primitive nodes seeded at icosahedron projections; elements seeded at their
primitive vertex position — algorithm is free to move everything.
"""

import math, subprocess, shutil
from pathlib import Path
from collections import defaultdict

import numpy as np
import networkx as nx

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD
from ig_pt_3d_utils import (
    ICO_VERTS, ICO_EDGES, PRIM_VERT, VERT_PRIM,
    proj as ico_proj,
    FDE_FILL, FDE_TEXT, ORGANIC_SET, METALLIC_SET, preamble,
)

SCALE_ICO = 2.0   # icosahedron seed scale
SCALE_OUT = 9.5   # scale output positions to cm (Kamada-Kawai returns ≈ unit-range)

# ─── Build graph ─────────────────────────────────────────────────────────────

def build_graph():
    G = nx.Graph()

    # Primitive nodes
    for prim in PRIM_VERT:
        G.add_node(f'P_{prim}', kind='prim', prim=prim)

    # Element nodes
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        G.add_node(sym, kind='elem', Z=Z, period=per, block=blk,
                   prim=PRIM_LABEL.get(sym, '⊥'))

    # Element → dominant primitive (strong pull)
    for sym in ELEMENTS:
        prim = PRIM_LABEL.get(sym, '⊥')
        if prim not in PRIM_VERT:
            prim = '⊥'
        G.add_edge(sym, f'P_{prim}', weight=4.0, etype='prim')

    # Frobenius thread sequence (organic)
    for i in range(len(ORGANIC_THREAD) - 1):
        G.add_edge(ORGANIC_THREAD[i], ORGANIC_THREAD[i+1], weight=7.0, etype='thread')

    # Frobenius thread sequence (metallic)
    for i in range(len(METALLIC_THREAD) - 1):
        G.add_edge(METALLIC_THREAD[i], METALLIC_THREAD[i+1], weight=7.0, etype='thread')

    # Enzyme bridge (P → Fe: last organic → first metallic)
    G.add_edge(ORGANIC_THREAD[-1], METALLIC_THREAD[0], weight=4.0, etype='bridge')

    # Icosahedron edges (primitive adjacency)
    for i, j in ICO_EDGES:
        pi = VERT_PRIM.get(i)
        pj = VERT_PRIM.get(j)
        if pi and pj:
            G.add_edge(f'P_{pi}', f'P_{pj}', weight=2.5, etype='ico')

    # Same-period pull (weak ∈ cohesion)
    by_period = defaultdict(list)
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        by_period[per].append(sym)
    for per, syms in by_period.items():
        syms_s = sorted(syms, key=lambda s: ELEMENTS[s][0])
        for i in range(len(syms_s) - 1):
            G.add_edge(syms_s[i], syms_s[i+1], weight=0.3, etype='period')

    # Same-block cohesion (◻ family)
    by_block = defaultdict(list)
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        by_block[blk].append(sym)
    for blk, syms in by_block.items():
        syms_s = sorted(syms, key=lambda s: ELEMENTS[s][0])
        for i in range(len(syms_s) - 1):
            G.add_edge(syms_s[i], syms_s[i+1], weight=0.5, etype='block')

    return G


# ─── Seed positions ───────────────────────────────────────────────────────────

def seed_positions(G):
    """Initial positions: primitives at icosahedron projection, elements at their prim."""
    pos = {}
    prim_pos = {}
    for prim, vi in PRIM_VERT.items():
        p2 = ico_proj(ICO_VERTS[vi], SCALE_ICO)
        prim_pos[prim] = np.array(p2)
        pos[f'P_{prim}'] = np.array(p2)

    for sym in ELEMENTS:
        prim = PRIM_LABEL.get(sym, '⊥')
        if prim not in prim_pos:
            prim = '⊥'
        # Slight jitter around primitive seed so elements don't stack exactly
        rng = np.random.default_rng(hash(sym) % 2**31)
        jitter = rng.uniform(-0.15, 0.15, 2)
        pos[sym] = prim_pos[prim] + jitter

    return pos


# ─── Layout ───────────────────────────────────────────────────────────────────

def compute_layout(G, seed_pos):
    # Kamada-Kawai layout: minimises stress on weighted graph-theoretic distances.
    # Use inverse weight as distance (higher weight = nodes pulled closer).
    pos = nx.kamada_kawai_layout(
        G,
        weight='weight',
        pos=seed_pos,
        scale=1.0,
    )
    # Normalise to fit SCALE_OUT cm radius
    coords = np.array(list(pos.values()))
    max_r  = np.max(np.linalg.norm(coords, axis=1))
    if max_r > 0:
        for k in pos:
            pos[k] = pos[k] / max_r * SCALE_OUT
    return pos


# ─── TikZ generation ─────────────────────────────────────────────────────────

def generate_tex(pos):
    L = [preamble('24cm', '24cm'), '\\begin{tikzpicture}\n']

    # ── Draw thread path first (under nodes) ──────────────────────────────────
    def path_coords(syms):
        return ' '.join(f'({pos[s][0]:.3f}cm,{pos[s][1]:.3f}cm)' for s in syms)

    org_c = path_coords(ORGANIC_THREAD)
    met_c = path_coords(METALLIC_THREAD)

    L.append(f'\\draw[red!30,line width=7pt,line cap=round,opacity=0.35]'
             f' plot[smooth,tension=0.6] coordinates {{{org_c}}};\n')
    L.append(f'\\draw[blue!30,line width=7pt,line cap=round,opacity=0.35]'
             f' plot[smooth,tension=0.6] coordinates {{{met_c}}};\n')
    L.append(f'\\draw[red!65!black,line width=1.6pt]'
             f' plot[smooth,tension=0.6] coordinates {{{org_c}}};\n')
    L.append(f'\\draw[blue!55!black,line width=1.6pt]'
             f' plot[smooth,tension=0.6] coordinates {{{met_c}}};\n')

    # Enzyme bridge P→Fe
    ps = pos[ORGANIC_THREAD[-1]]
    pf = pos[METALLIC_THREAD[0]]
    L.append(f'\\draw[purple!65!black,line width=1.6pt]'
             f' ({ps[0]:.3f}cm,{ps[1]:.3f}cm) -- ({pf[0]:.3f}cm,{pf[1]:.3f}cm);\n')
    mx, my = (ps[0]+pf[0])/2, (ps[1]+pf[1])/2
    L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=purple!58!black]'
             f' at ({mx+0.35:.3f}cm,{my:.3f}cm) {{bridge}};\n')

    # ── Primitive lines from origin ───────────────────────────────────────────
    for prim in PRIM_VERT:
        pp = pos[f'P_{prim}']
        empty = prim in ('◻','≻','∈','⋈')
        col = 'black!8' if empty else 'black!14'
        L.append(f'\\draw[{col},line width=0.35pt] (0,0) -- ({pp[0]:.3f}cm,{pp[1]:.3f}cm);\n')

    # ── Icosahedron skeleton (faint lines between primitive nodes) ────────────
    for i, j in ICO_EDGES:
        pi_name = f'P_{VERT_PRIM[i]}'
        pj_name = f'P_{VERT_PRIM[j]}'
        if pi_name in pos and pj_name in pos:
            p1, p2 = pos[pi_name], pos[pj_name]
            L.append(f'\\draw[black!12,line width=0.3pt]'
                     f' ({p1[0]:.3f}cm,{p1[1]:.3f}cm) -- ({p2[0]:.3f}cm,{p2[1]:.3f}cm);\n')

    # ── Element nodes ─────────────────────────────────────────────────────────
    # Draw thread elements last (on top)
    thread_set = ORGANIC_SET | METALLIC_SET

    for sym in ELEMENTS:
        if sym in thread_set:
            continue
        if sym not in pos:
            continue
        x, y = pos[sym]
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        L.append(f'\\node[circle,fill={fill},draw=black!18,line width=0.28pt,'
                 f'minimum size=0.40cm,inner sep=0pt]'
                 f' at ({x:.3f}cm,{y:.3f}cm)'
                 f' {{\\fontsize{{3.5}}{{3.5}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    for sym in list(ORGANIC_THREAD) + list(METALLIC_THREAD):
        if sym not in pos:
            continue
        x, y = pos[sym]
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        is_org = sym in ORGANIC_SET
        dc   = 'red!65!black' if is_org else 'blue!55!black'
        L.append(f'\\node[circle,fill={fill},draw={dc},line width=1.5pt,'
                 f'minimum size=1.0cm,inner sep=0pt]'
                 f' at ({x:.3f}cm,{y:.3f}cm)'
                 f' {{\\fontsize{{6}}{{6}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Primitive anchor nodes + labels ───────────────────────────────────────
    for prim, vi in PRIM_VERT.items():
        pp   = pos[f'P_{prim}']
        empty = prim in ('◻','≻','∈','⋈')
        col  = 'black!20' if not empty else 'black!10'
        L.append(f'\\node[circle,fill={col},minimum size=0.15cm,inner sep=0pt]'
                 f' at ({pp[0]:.3f}cm,{pp[1]:.3f}cm) {{}};\n')
        # Label offset away from origin
        r = math.sqrt(pp[0]**2 + pp[1]**2)
        if r > 0.01:
            off = 0.55
            lx  = pp[0] + pp[0]/r * off
            ly  = pp[1] + pp[1]/r * off
        else:
            lx, ly = pp[0], pp[1] + 0.55
        alpha = '!28' if empty else '!55'
        L.append(f'\\node[font={{\\igprimfont\\fontsize{{11}}{{11}}\\selectfont}},text=black{alpha}]'
                 f' at ({lx:.3f}cm,{ly:.3f}cm) {{{prim}}};\n')

    # ── Title ─────────────────────────────────────────────────────────────────
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!60]'
             ' at (0,10.6cm)'
             ' {IG Periodic Table --- Kamada-Kawai Spring Layout'
             ' (graph structure determines position)};\n')

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
    print('Building graph...')
    G   = build_graph()
    print(f'  {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

    print('Seeding positions...')
    seed = seed_positions(G)

    print('Running Kamada-Kawai layout...')
    pos = compute_layout(G, seed)
    print('  Done.')

    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_spring.tex'
    pdf_path = out_dir / 'ig_pt_spring.pdf'

    tex = generate_tex(pos)
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
            shutil.copy(pdf_path, pdfs / 'ig_pt_spring.pdf')
            print(f'Copied → pdfs/ig_pt_spring.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print(result.stdout[-2000:])
