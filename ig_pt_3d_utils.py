#!/usr/bin/env python3
"""Shared 3D geometry and projection utilities for IG periodic table designs."""

import math
from collections import defaultdict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ig_periodic_table import ELEMENTS, PRIM_LABEL, FDE_CLASS, ORGANIC_THREAD, METALLIC_THREAD

# ─── Icosahedron ─────────────────────────────────────────────────────────────
phi = (1 + math.sqrt(5)) / 2
_INORM = math.sqrt(1 + phi**2)

_ICO_RAW = [
    ( 0,  1,  phi),  # 0 front-top
    ( 0, -1,  phi),  # 1 front-bottom
    ( 0,  1, -phi),  # 2 back-top
    ( 0, -1, -phi),  # 3 back-bottom
    ( 1,  phi,  0),  # 4 right-top
    (-1,  phi,  0),  # 5 left-top
    ( 1, -phi,  0),  # 6 right-bottom
    (-1, -phi,  0),  # 7 left-bottom
    ( phi,  0,  1),  # 8 right-front
    (-phi,  0,  1),  # 9 left-front
    ( phi,  0, -1),  # 10 right-back
    (-phi,  0, -1),  # 11 left-back
]
ICO_VERTS = [(x/_INORM, y/_INORM, z/_INORM) for x,y,z in _ICO_RAW]

_ELEN = 2.0 / _INORM
ICO_EDGES = [
    (i, j) for i in range(12) for j in range(i+1, 12)
    if abs(math.sqrt(sum((a-b)**2 for a,b in zip(ICO_VERTS[i], ICO_VERTS[j]))) - _ELEN) < 1e-6
]

# Primitive → icosahedron vertex index
# Populated primitives on front hemisphere; empty arms (Ω Ř Γ ƒ) pushed back.
PRIM_VERT = {
    'Ħ':  0,   # front-top        — d/f-block + H, most elements
    'ɢ':  1,   # front-bottom     — alkali metals
    '⊙':  4,   # right-top        — noble gases + actinides
    'Σ':  5,   # left-top         — alkaline earths + group 15
    'Ç':  8,   # right-front      — halogens + Pt/Au
    'Φ':  9,   # left-front       — group 16
    'Ð':  6,   # right-bottom     — group 13
    'Þ':  7,   # left-bottom      — group 14
    'Ω': 10,   # right-back       — empty
    'Ř': 11,   # left-back        — empty
    'Γ':  2,   # back-top         — empty
    'ƒ':  3,   # back-bottom      — empty
}
VERT_PRIM = {v: p for p, v in PRIM_VERT.items()}

# ─── Rotation + orthographic projection ──────────────────────────────────────
def _rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1,0,0],[0,c,-s],[0,s,c]]

def _rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c,0,s],[0,1,0],[-s,0,c]]

def _mv(M, v):
    return [sum(M[i][j]*v[j] for j in range(3)) for i in range(3)]

# Default view angles tuned to show front hemisphere clearly
_RX = math.radians(22)
_RY = math.radians(-32)

def rotate3(v3, rx=_RX, ry=_RY):
    v = _mv(_rot_x(rx), v3)
    return _mv(_rot_y(ry), v)

def proj(v3, scale=5.2, rx=_RX, ry=_RY):
    r = rotate3(v3, rx, ry)
    return (r[0]*scale, r[1]*scale)

def zdepth(v3, rx=_RX, ry=_RY):
    return rotate3(v3, rx, ry)[2]

# ─── 3D perpendicular basis ───────────────────────────────────────────────────
def _norm3(v):
    n = math.sqrt(sum(x**2 for x in v))
    return [x/n for x in v]

def _cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]

def perp_basis(v):
    vx, vy, vz = v
    u = _norm3([0,-vz,vy] if abs(vx) < 0.9 else [vz,0,-vx])
    w = _norm3(_cross(v, u))
    return u, w

# ─── Element → 3D position on icosahedron ────────────────────────────────────
R_PERIOD   = 0.61    # period radius in 3D space (proj × SCALE gives cm)
CLUST_SPC  = 0.22    # cluster node spacing in 3D space

def ico_element_positions():
    groups = defaultdict(list)
    for sym, (Z, per, col, blk) in ELEMENTS.items():
        prim = PRIM_LABEL.get(sym, 'Ħ')
        if prim not in PRIM_VERT:
            prim = 'Ħ'
        groups[(prim, per)].append((Z, sym))

    pos3d = {}
    for (prim, per), elems in groups.items():
        elems.sort()
        n = len(elems)
        v = ICO_VERTS[PRIM_VERT[prim]]
        r = per * R_PERIOD
        u, w = perp_basis(v)
        cols = min(n, 6)
        rows = math.ceil(n / cols)
        for i, (Z, sym) in enumerate(elems):
            row   = i // cols
            col_i = i  % cols
            pu = (col_i - (cols-1)/2) * CLUST_SPC
            pw = (row   - (rows-1)/2) * CLUST_SPC
            pos3d[sym] = [r*v[k] + pu*u[k] + pw*w[k] for k in range(3)]
    return pos3d

# ─── FDE colours ─────────────────────────────────────────────────────────────
FDE_FILL = {'T':'green!55!black','F':'black!42','B':'orange!75!red','N':'black!10'}
FDE_TEXT = {'T':'white',        'F':'white',   'B':'white',        'N':'black!28'}

ORGANIC_SET  = set(ORGANIC_THREAD)
METALLIC_SET = set(METALLIC_THREAD)

# ─── Shared LaTeX preamble ────────────────────────────────────────────────────
def preamble(pw='24cm', ph='24cm'):
    return ('\\documentclass{article}\n'
            '\\usepackage{fontspec}\n'
            f'\\usepackage[paperwidth={pw},paperheight={ph},margin=0.5cm]{{geometry}}\n'
            '\\usepackage[warnings-off={mathtools-colon,mathtools-overbracket}]{unicode-math}\n'
            '\\ExplSyntaxOn\\msg_redirect_name:nnn{lualatex-math}{wrong-meaning}{none}\\ExplSyntaxOff\n'
            '\\setmathfont{Latin Modern Math}\n'
            '\\newfontface\\igprimfont{Everson Mono}\n'
            '\\usepackage{tikz}\n'
            '\\usetikzlibrary{backgrounds,calc}\n'
            '\\pagestyle{empty}\n'
            '\\begin{document}\\centering\n')
