#!/usr/bin/env python3
"""
Design B-3D — Frobenius Helix.
Organic thread (H O N C S P) and metallic thread (Fe Ni Zn Mo Rh Pd W Ir Pt Au)
wind as two helices around a shared axis. Enzyme bridges are actual 3D links.
Satellite elements orbit the helix in a background cloud.
"""

import math, subprocess, shutil
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD, RADIOACTIVE
from ig_pt_3d_utils import (
    proj, zdepth, perp_basis,
    FDE_FILL, FDE_TEXT, ORGANIC_SET, METALLIC_SET, preamble,
    _norm3, _cross,
)

SCALE = 2.0   # cm per 3D unit

# ─── Helix parameters ────────────────────────────────────────────────────────
HELIX_R    = 1.8    # radius of helix (3D units)
HELIX_Z    = 9.0    # total z-height of helix (3D units)
N_TURNS    = 1.5    # full rotations in total height

# Organic: 6 elements spanning full height
N_ORG = len(ORGANIC_THREAD)   # 6
# Metallic: 10 elements spanning full height
N_MET = len(METALLIC_THREAD)  # 10

def helix_pos(i, n, phase_offset=0.0, r=HELIX_R, z_total=HELIX_Z):
    """3D position of element i in a helix of n elements."""
    t = i / (n - 1) if n > 1 else 0.5
    theta = t * 2 * math.pi * N_TURNS + phase_offset
    z = t * z_total - z_total / 2   # centre around z=0
    return [r * math.cos(theta), r * math.sin(theta), z]

ORG_POS3D = {s: helix_pos(i, N_ORG, phase_offset=0.0)
             for i, s in enumerate(ORGANIC_THREAD)}
MET_POS3D = {s: helix_pos(i, N_MET, phase_offset=math.pi)
             for i, s in enumerate(METALLIC_THREAD)}
THREAD_POS3D = {**ORG_POS3D, **MET_POS3D}

# ─── Satellite positions ──────────────────────────────────────────────────────
# Elements not on threads placed in concentric outer shell, z = period-based

PRIM_PHI = {   # azimuthal angle (in degrees) for each primitive family
    '∋':  20,   # alkali metals
    '⊞':  60,   # alkaline earths + group 15
    '⊢': 100,   # group 13
    '⊣': 140,   # group 14 excl C
    '≺': 200,   # group 16 excl O,S
    '⊤': 240,   # halogens
    '⊥': 280,   # d-block non-thread + lanthanides
    '⊙': 320,   # noble gases + actinides
}

def satellite_pos3d(sym):
    prim = PRIM_LABEL.get(sym, '⊥')
    if prim not in PRIM_PHI:
        prim = '⊥'
    Z, per, col, blk = ELEMENTS[sym]
    phi_deg = PRIM_PHI[prim]
    if prim == '⊥' and blk == 'f':
        phi_deg += 30
    theta = math.radians(phi_deg)
    # Outer shell radius increases slightly with period
    r_shell = 3.5 + (per - 1) * 0.15
    z = (per - 4) * 1.4   # z centred on period 4
    return [r_shell * math.cos(theta), r_shell * math.sin(theta), z]

def compute_satellite_positions():
    shown = set(THREAD_POS3D)
    # Group by (prim, period) for clustering within a prim shell
    groups = defaultdict(list)
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        if sym in shown:
            continue
        prim = PRIM_LABEL.get(sym, '⊥')
        key = (prim, per, 'f' if blk == 'f' else 's')
        groups[key].append((Z, sym))

    pos3d = {}
    for (prim, per, sub), elems in groups.items():
        elems.sort()
        n = len(elems)
        if prim not in PRIM_PHI:
            prim_use = '⊥'
        else:
            prim_use = prim
        phi_deg = PRIM_PHI[prim_use]
        if sub == 'f':
            phi_deg += 30
        theta = math.radians(phi_deg)
        r_shell = 3.5 + (per - 1) * 0.15
        z_base  = (per - 4) * 1.4

        # Perpendicular direction: vertical (z) and tangential (theta+90)
        theta_perp = theta + math.pi / 2
        tang = [math.cos(theta_perp), math.sin(theta_perp), 0.0]
        vert = [0.0, 0.0, 1.0]

        cols = min(n, 5)
        rows = math.ceil(n / cols)
        SPC = 0.28
        for i, (Z, sym) in enumerate(elems):
            row   = i // cols
            col_i = i  % cols
            dt = (col_i - (cols-1)/2) * SPC
            dz = (row   - (rows-1)/2) * SPC
            x = r_shell * math.cos(theta) + dt * tang[0]
            y = r_shell * math.sin(theta) + dt * tang[1]
            z = z_base + dz
            pos3d[sym] = [x, y, z]

    return pos3d

# ─── Helix curve (many points for a smooth tube) ─────────────────────────────
def helix_curve(n_pts, phase_offset):
    pts = []
    for i in range(n_pts):
        t = i / (n_pts - 1)
        theta = t * 2 * math.pi * N_TURNS + phase_offset
        z = t * HELIX_Z - HELIX_Z / 2
        pts.append([HELIX_R * math.cos(theta), HELIX_R * math.sin(theta), z])
    return pts

def tikz_curve(pts, color, lw='1.6pt', opacity=1.0):
    """TikZ plot coordinates string for a smooth curve through 3D-projected points."""
    coords = ' '.join(f'({proj(p, SCALE)[0]:.3f}cm,{proj(p, SCALE)[1]:.3f}cm)' for p in pts)
    return (f'\\draw[{color},line width={lw},opacity={opacity:.2f}]'
            f' plot[smooth,tension=0.6] coordinates {{{coords}}};\n')


def generate_tex():
    sat_pos = compute_satellite_positions()
    L = [preamble('24cm', '26cm'), '\\begin{tikzpicture}\n']

    # ── Satellite cloud (back-to-front) ───────────────────────────────────────
    sats_with_d = []
    for sym, pos in sat_pos.items():
        sats_with_d.append((zdepth(pos), sym, pos))
    sats_with_d.sort()

    for d, sym, pos in sats_with_d:
        x2, y2 = proj(pos, SCALE)
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        op   = max(0.2, min(0.7, 0.45 + d * 0.08))
        r_sz = 0.16 if fde == 'N' else 0.19
        L.append(f'\\node[circle,fill={fill},draw=black!18,line width=0.25pt,'
                 f'minimum size={2*r_sz:.2f}cm,inner sep=0pt,opacity={op:.2f}]'
                 f' at ({x2:.3f}cm,{y2:.3f}cm)'
                 f' {{\\fontsize{{3.2}}{{3.2}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')

    # ── Helix tube ribbons ─────────────────────────────────────────────────────
    org_curve = helix_curve(80, phase_offset=0.0)
    met_curve = helix_curve(80, phase_offset=math.pi)
    L.append(tikz_curve(org_curve, 'red!30', lw='8pt', opacity=0.30))
    L.append(tikz_curve(met_curve, 'blue!30', lw='8pt', opacity=0.30))
    L.append(tikz_curve(org_curve, 'red!70!black', lw='0.7pt', opacity=0.6))
    L.append(tikz_curve(met_curve, 'blue!55!black', lw='0.7pt', opacity=0.6))

    # ── Enzyme bridge arcs (3D straight lines) ────────────────────────────────
    # S → Zn  (organic index 4, metallic index 2)
    ps  = proj(ORG_POS3D['S'],  SCALE)
    pzn = proj(MET_POS3D['Zn'], SCALE)
    L.append(f'\\draw[purple!65!black,line width=1.6pt]'
             f' ({ps[0]:.3f}cm,{ps[1]:.3f}cm) -- ({pzn[0]:.3f}cm,{pzn[1]:.3f}cm);\n')
    mid_szn = [(a+b)/2 for a,b in zip(ORG_POS3D['S'], MET_POS3D['Zn'])]
    pm = proj(mid_szn, SCALE)
    L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=purple!60!black]'
             f' at ({pm[0]+0.3:.3f}cm,{pm[1]+0.2:.3f}cm) {{$\\sigma_1$}};\n')

    # Fe → N  (metallic index 0, organic index 2)
    pfe = proj(MET_POS3D['Fe'], SCALE)
    pn  = proj(ORG_POS3D['N'],  SCALE)
    L.append(f'\\draw[purple!65!black,line width=1.6pt,dashed]'
             f' ({pfe[0]:.3f}cm,{pfe[1]:.3f}cm) -- ({pn[0]:.3f}cm,{pn[1]:.3f}cm);\n')
    mid_fen = [(a+b)/2 for a,b in zip(MET_POS3D['Fe'], ORG_POS3D['N'])]
    pm2 = proj(mid_fen, SCALE)
    L.append(f'\\node[font={{\\fontsize{{4.5}}{{4.5}}\\selectfont}},text=purple!60!black]'
             f' at ({pm2[0]+0.3:.3f}cm,{pm2[1]-0.2:.3f}cm) {{$\\sigma_1^{{-1}}$}};\n')

    # ── Thread nodes (back-to-front) ───────────────────────────────────────────
    thread_syms = list(ORGANIC_THREAD) + list(METALLIC_THREAD)
    thread_with_d = [(zdepth(THREAD_POS3D[s]), s) for s in thread_syms]
    thread_with_d.sort()

    for d, sym in thread_with_d:
        x2, y2 = proj(THREAD_POS3D[sym], SCALE)
        fde  = FDE_CLASS.get(sym, 'B')
        fill = FDE_FILL[fde]
        tc   = FDE_TEXT[fde]
        is_org = sym in ORGANIC_SET
        dc   = 'red!65!black' if is_org else 'blue!55!black'
        L.append(f'\\node[circle,fill={fill},draw={dc},line width=1.6pt,'
                 f'minimum size=1.1cm,inner sep=0pt]'
                 f' at ({x2:.3f}cm,{y2:.3f}cm)'
                 f' {{\\fontsize{{6.5}}{{6.5}}\\selectfont'
                 f'\\textcolor{{{tc}}}{{\\textbf{{{sym}}}}}}};\n')
        Z = ELEMENTS[sym][0]
        L.append(f'\\node[font={{\\fontsize{{3.8}}{{3.8}}\\selectfont}},text=black!38]'
                 f' at ({x2:.3f}cm,{y2+0.70:.3f}cm) {{{Z}}};\n')

    # ── Axis indicator (dashed line through helix centre) ─────────────────────
    ax_top = proj([0, 0,  HELIX_Z/2 + 0.5], SCALE)
    ax_bot = proj([0, 0, -HELIX_Z/2 - 0.5], SCALE)
    L.append(f'\\draw[black!18,line width=0.4pt,dashed]'
             f' ({ax_top[0]:.3f}cm,{ax_top[1]:.3f}cm)'
             f' -- ({ax_bot[0]:.3f}cm,{ax_bot[1]:.3f}cm);\n')

    # ── Title ─────────────────────────────────────────────────────────────────
    L.append('\\node[font={\\fontsize{9}{9}\\selectfont\\bfseries},text=black!60]'
             ' at (0,11.2cm)'
             ' {IG Periodic Table --- Frobenius Helix'
             ' ($\\mu\\circ\\delta=\\mathrm{id}$ as double helix)};\n')

    # ── Legend ────────────────────────────────────────────────────────────────
    lx0, ly0 = -5.8, -11.2
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
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,anchor=west]'
             f' at ({lx0+0.58:.2f}cm,{ly1:.2f}cm) {{organic thread (H O N C S P)}};\n'
             f'\\draw[blue!55!black,line width=1.4pt] ({lx0+5.5:.2f}cm,{ly1:.2f}cm)'
             f' -- ({lx0+6.0:.2f}cm,{ly1:.2f}cm);\n'
             f'\\node[font={{\\fontsize{{4.8}}{{4.8}}\\selectfont}},text=black!55,anchor=west]'
             f' at ({lx0+6.08:.2f}cm,{ly1:.2f}cm) {{metallic thread (Fe Ni Zn Mo Rh Pd W Ir Pt Au)}};\n')

    L.append('\\end{tikzpicture}\n\\end{document}\n')
    return ''.join(L)


if __name__ == '__main__':
    out_dir  = Path(__file__).parent
    tex_path = out_dir / 'ig_pt_helix.tex'
    pdf_path = out_dir / 'ig_pt_helix.pdf'

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
            shutil.copy(pdf_path, pdfs / 'ig_pt_helix.pdf')
            print(f'Copied → pdfs/ig_pt_helix.pdf')
    else:
        for line in result.stdout.splitlines():
            if line.startswith('!') or 'Error' in line:
                print(line)
        print(result.stdout[-2000:])
