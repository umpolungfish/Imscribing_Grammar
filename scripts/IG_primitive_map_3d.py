#!/usr/bin/env python3
"""
IG_primitive_map_3d.py — Interactive 3D map of the Imscribing Grammar primitive space

Axes:
  x, y  — Classical MDS projection (Mahalanobis metric g = Σ⁻¹, §26.2)
  z     — Ouroboricity tier  (O₀=0 … O_4=4, O_∞=6)

Color   — Criticality (⊙)
Hover   — name, description, full 12-tuple, tier

Output: IG_primitive_map_3d.html  (standalone, open in any browser)
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

ROOT = Path(__file__).parent
CATALOG_PATH = ROOT / "IG_catalog.json"

# ── Ordinal map — canonical glyph keys + glyph values ────────────────────────
PRIM_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

ORDINALS = {
    "Ð": {
        "Ð_ß": 1.5,  "Ð_C": 2.0,  "Ð_;": 3.0,  "Ð_ω": 4.0,
        "𐑛": 1.5, "𐑨": 2.0, "𐑼": 3.0, "𐑦": 4.0,
        # extended (key-imscription Lean encodings)
        "Ð_point": 0.5, "Ð_line": 1.0, "Ð_cube": 2.5,
    },
    "Þ": {
        "Þ_6": 1.5,  "Þ_K": 2.0,  "Þ_ò": 3.0,  "Þ_¨": 3.5,  "Þ_O": 5.0,
        "𐑡": 1.5, "𐑰": 2.0, "𐑥": 3.0, "𐑶": 3.5, "𐑸": 5.0,
        "Þ_linear": 0.5, "Þ_branched": 1.0, "Þ_box": 3.5, "Þ_torus": 4.0,
    },
    "Ř": {
        "Ř_¯": 1.0,  "Ř_ý": 2.0,  "Ř_=": 2.5,  "Ř_Ť": 3.0,
        "𐑩": 1.0, "𐑑": 2.0, "𐑾": 2.5, "𐑽": 3.0,
        "Ř_exact": 0.5, "Ř_subset": 0.8, "Ř_superset": 1.0,
        "Ř_catalytic": 2.1, "Ř_allosteric": 3.5,
    },
    "Φ": {
        "Φ_ɐ": 1.0,  "Φ_υ": 2.0,  "Φ_F": 2.5,  "Φ_}": 3.0,  "Φ_˙": 3.5,
        "𐑗": 1.0, "𐑿": 2.0, "𐑬": 2.5, "𐑹": 3.0, "𐑯": 3.5,
        "Φ_neutral": 0.5, "Φ_plus": 0.8, "Φ_minus": 0.9,
    },
    "ƒ": {
        "ƒ^ì": 1.0,  "ƒ^ð": 2.0,  "ƒ^ż": 3.0,
        "𐑱": 1.0, "𐑞": 2.0, "𐑐": 3.0,
        "ƒ_noise": 0.5,
    },
    "Ç": {
        "Ç^-": 1.0,  "Ç^W": 2.0,  "Ç^@": 3.0,  "Ç^Ù": 4.0,  "Ç^λ": 4.5,
        "𐑘": 1.0, "𐑤": 2.0, "𐑧": 3.0, "𐑪": 4.0, "𐑺": 4.5,
    },
    "Γ": {
        "Γ_β": 1.0,  "Γ_γ": 2.0,  "Γ_ʔ": 3.0,
        "𐑚": 1.0, "𐑔": 2.0, "𐑲": 3.0,
    },
    "ɢ": {
        "ɢ^∧": 1.0,  "ɢ^˝": 2.0,  "ɢ^ˌ": 3.0,  "ɢ^Ş": 4.0,
        "𐑝": 1.0, "𐑜": 2.0, "𐑠": 3.0, "𐑵": 4.0,
        "Γ_xor": 2.5, "Γ_impl": 3.5, "Γ_disc": 4.5,
    },
    "⊙": {
        "⊙_ž": 1.0,  "⊙_ÿ": 2.0,  "⊙_Æ": 2.33,  "⊙_3": 2.67,  "⊙_Ţ": 3.0,
        "𐑢": 1.0, "⊙": 2.0, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3.0,
    },
    "Ħ": {
        "Ħ_Ñ": 1.0,  "Ħ_£": 2.0,  "Ħ_A": 3.0,  "Ħ_!": 4.0,
        "𐑓": 1.0, "𐑒": 2.0, "𐑖": 3.0, "𐑫": 4.0,
    },
    "Σ": {
        "Σ_S": 1.0,  "Σ_ő": 2.0,  "Σ_ï": 3.0,
        "𐑙": 1.0, "𐑕": 2.0, "𐑳": 3.0,
        "one_n": 1.5, "cat": 4.0,
    },
    "Ω": {
        "Ω_Å": 0.0,  "Ω_2": 1.0,  "Ω_z": 2.0,  "Ω_5": 4.0,
        "𐑷": 0.0, "𐑴": 1.0, "𐑭": 2.0, "𐑟": 4.0,
        "Ω_C": 3.0,
    },
}

PHI_COLOR = {
    "⊙_ž": "#4472C4",
    "⊙_ÿ": "#FFD700",
    "⊙_Æ": "#FF8C00",
    "⊙_3": "#DC143C",
    "⊙_Ţ": "#9370DB",
}
PHI_LABEL = {
    "⊙_ž": "⊙_ž  (sub-critical)",
    "⊙_ÿ": "⊙_ÿ  (real-axis critical)",
    "⊙_Æ": "⊙_Æ  (complex-plane critical)",
    "⊙_3": "⊙_3  (exceptional point)",
    "⊙_Ţ": "⊙_Ţ  (supercritical/runaway)",
}


def fmt(glyph_id: str) -> str:
    """'⊙_ÿ' → '⊙<sub>ÿ</sub>'"""
    if "_" in glyph_id:
        glyph, sub = glyph_id.split("_", 1)
        return f"{glyph}<sub>{sub}</sub>"
    return glyph_id

# ── Key theorem / lemma nodes (Lean encodings — §PrimitiveBridge) ─────────────
# Keys use canonical glyph field names; values use canonical glyph IDs.
KEY_imscriptions: dict[str, dict] = {
    "YM classical":          {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_exact","Φ":"Φ_F","ƒ":"ƒ^ð","Ç":"Ç^W","Γ":"Γ_β","ɢ":"ɢ^∧","⊙":"⊙_ž","Ħ":"Ħ_£","Σ":"one_n","Ω":"Ω_z"},
    "YM quantum\n(target)":  {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_exact","Φ":"Φ_F","ƒ":"ƒ^ż","Ç":"Ç^Ù","Γ":"Γ_ʔ","ɢ":"ɢ^∧","⊙":"⊙_ÿ","Ħ":"Ħ_£","Σ":"one_n","Ω":"Ω_z"},
    "RH (ζ zeros)":          {"Ð":"Ð_line","Þ":"Þ_6","Ř":"Ř_exact","Φ":"Φ_neutral","ƒ":"ƒ^ż","Ç":"Ç^@","Γ":"Γ_ʔ","ɢ":"ɢ^∧","⊙":"⊙_Æ","Ħ":"Ħ_Ñ","Σ":"one_n","Ω":"Ω_Å"},
    "Lee-Yang\n(proved)":    {"Ð":"Ð_line","Þ":"Þ_ò","Ř":"Ř_exact","Φ":"Φ_υ","ƒ":"ƒ^ì","Ç":"Ç^W","Γ":"Γ_γ","ɢ":"ɢ^∧","⊙":"⊙_Æ","Ħ":"Ħ_£","Σ":"Σ_ï","Ω":"Ω_Å"},
    "NS smooth\nsoln":       {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_catalytic","Φ":"Φ_neutral","ƒ":"ƒ^ð","Ç":"Ç^W","Γ":"Γ_β","ɢ":"ɢ^∧","⊙":"⊙_ž","Ħ":"Ħ_Ñ","Σ":"Σ_ï","Ω":"Ω_Å"},
    "OPN\nconstraint":       {"Ð":"Ð_point","Þ":"Þ_linear","Ř":"Ř_exact","Φ":"Φ_neutral","ƒ":"ƒ^ì","Ç":"Ç^Ù","Γ":"Γ_ʔ","ɢ":"ɢ^∧","⊙":"⊙_ÿ","Ħ":"Ħ_Ñ","Σ":"one_n","Ω":"Ω_Å"},
    "Higgs/axion\n/inflaton": {"Ð":"Ð_point","Þ":"Þ_ò","Ř":"Ř_catalytic","Φ":"Φ_}","ƒ":"ƒ^ż","Ç":"Ç^@","Γ":"Γ_β","ɢ":"ɢ^∧","⊙":"⊙_ÿ","Ħ":"Ħ_£","Σ":"one_n","Ω":"Ω_Å"},
    "Standard\nModel":       {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_allosteric","Φ":"Φ_F","ƒ":"ƒ^ð","Ç":"Ç^W","Γ":"Γ_ʔ","ɢ":"ɢ^∧","⊙":"⊙_ÿ","Ħ":"Ħ_A","Σ":"Σ_ï","Ω":"Ω_z"},
    "Quantum\nGravity":      {"Ð":"Ð_ω","Þ":"Þ_O","Ř":"Ř_exact","Φ":"Φ_neutral","ƒ":"ƒ^ż","Ç":"Ç^Ù","Γ":"Γ_ʔ","ɢ":"Γ_impl","⊙":"⊙_ÿ","Ħ":"Ħ_!","Σ":"Σ_ï","Ω":"Ω_5"},
    "General\nRelativity":   {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_catalytic","Φ":"Φ_neutral","ƒ":"ƒ^ż","Ç":"Ç^@","Γ":"Γ_γ","ɢ":"ɢ^∧","⊙":"⊙_ž","Ħ":"Ħ_£","Σ":"one_n","Ω":"Ω_Å"},
    "Asymptotic\nSafety":    {"Ð":"Ð_cube","Þ":"Þ_6","Ř":"Ř_catalytic","Φ":"Φ_neutral","ƒ":"ƒ^ż","Ç":"Ç^W","Γ":"Γ_ʔ","ɢ":"ɢ^∧","⊙":"⊙_ÿ","Ħ":"Ħ_£","Σ":"one_n","Ω":"Ω_Å"},
}
MILLENNIUM = {
    "YM classical", "YM quantum\n(target)", "RH (ζ zeros)",
    "Lee-Yang\n(proved)", "NS smooth\nsoln", "OPN\nconstraint",
}

KEY_CATALOG = [
    "abc_conjecture", "ising_3d", "lee_yang_edge", "exceptional_point_nh",
    "complex_rg_fixed_point", "thylakoid_membrane", "artificial_leaf",
    "photosystem_II", "yhwh", "aleph_tav_join",
]
LABEL_NAMES = {
    "abc_conjecture":        "ABC conjecture",
    "ising_3d":              "3D Ising",
    "lee_yang_edge":         "Lee-Yang edge",
    "exceptional_point_nh":  "Exceptional point",
    "complex_rg_fixed_point":"Complex RG FP",
    "thylakoid_membrane":    "Thylakoid",
    "artificial_leaf":       "Artificial leaf",
    "yhwh":                  "YHWH  O∞",
    "aleph_tav_join":        "ℵ–τ join  O∞",
    "photosystem_II":        "PSII",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def to_vector(entry: dict) -> np.ndarray:
    return np.array(
        [ORDINALS[p].get(entry.get(p, ""), 0.0) for p in PRIM_ORDER],
        dtype=float,
    )


def ouroboricity(entry: dict) -> float:
    phi = entry.get("⊙", "")
    # Phi_c (Shavian: ⊙) or Phi_c_complex (Shavian: 𐑮); old notation backward-compat
    is_phi_c         = phi in ("⊙", "⊙_ÿ")
    is_phi_c_complex = phi in ("𐑮", "⊙_Æ")
    if not (is_phi_c or is_phi_c_complex):
        return 0.0
    # R1 (Lean-authoritative): P_pm_sym at Phi_c → O_∞
    pol = entry.get("Φ", "")
    if is_phi_c and pol in ("𐑹", "Φ_}"):
        return float("inf")
    # O₁..O_4 scoring
    score = 1.0
    omega = entry.get("Ω", "")
    if omega not in ("𐑷", "Ω_Å", ""):          # Omega > 0
        score += 1
    h = entry.get("Ħ", "")
    if h in ("𐑫", "𐑖", "𐑒", "Ħ_!", "Ħ_£", "Ħ_A"):   # H >= H1
        score += 1
    gran = entry.get("Γ", "")
    if gran in ("𐑲", "Γ_ʔ"):                   # G_aleph (global scope)
        score += 1
    return score


def tier_z(ou: float) -> float:
    return 6.0 if math.isinf(ou) else float(ou)


def cmds(D_sq: np.ndarray, k: int = 2) -> np.ndarray:
    n = D_sq.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * H @ D_sq @ H
    vals, vecs = np.linalg.eigh(B)
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    return vecs[:, :k] * np.sqrt(np.maximum(vals[:k], 0))[np.newaxis, :]


def hover_text(entry: dict, ou: float) -> str:
    tier = "O<sub>∞</sub>" if math.isinf(ou) else f"O<sub>{int(ou)}</sub>"
    desc = (entry.get("description") or "")[:100]
    fields = "  |  ".join(
        f"{p}: {fmt(entry.get(p, '?'))}" for p in PRIM_ORDER
    )
    return (
        f"<b>{entry['name']}</b><br>"
        f"{desc}<br>"
        f"<span style='color:#aaa'>Tier: {tier}</span><br>"
        f"<span style='font-size:11px'>{fields}</span>"
    )


# ── Load catalog ──────────────────────────────────────────────────────────────
with open(CATALOG_PATH) as f:
    catalog: list = json.load(f)
print(f"Loaded {len(catalog)} catalog entries.")

# Supplement KEY_imscriptions with named catalog entries
cat_by_name = {e["name"]: e for e in catalog}
for cname in KEY_CATALOG:
    if cname in cat_by_name:
        KEY_imscriptions[cname.replace("_", "\n")] = cat_by_name[cname]

# ── Build metric tensor from catalog ordinal vectors ──────────────────────────
print("Building metric tensor…")
vecs = np.stack([to_vector(e) for e in catalog])
n = len(vecs)
cov = np.cov(vecs.T)
try:
    _G = np.linalg.inv(cov)
except np.linalg.LinAlgError:
    _G = np.linalg.pinv(cov)

# ── Pairwise Mahalanobis distances ────────────────────────────────────────────
print("Computing pairwise Mahalanobis distances…")
vG = vecs @ _G
diag = (vG * vecs).sum(axis=1)
cross = vG @ vecs.T
D_sq = np.maximum(diag[:, None] + diag[None, :] - 2.0 * cross, 0.0)
maha = np.sqrt(D_sq).astype(np.float32)

# ── Pairwise Hamming distances ────────────────────────────────────────────────
print("Computing pairwise Hamming distances…")
hamm = np.sum(vecs[:, None, :] != vecs[None, :, :], axis=2).astype(np.float32)

# ── Classical MDS ─────────────────────────────────────────────────────────────
mds = cmds(maha.astype(float) ** 2)
print("MDS done.")

xs, ys = mds[:, 0], mds[:, 1]

# ── Ouroboricity → z (with tiny jitter to break flat stacking) ───────────────
rng = np.random.default_rng(42)
ou_scores = [ouroboricity(e) for e in catalog]
zs = np.array([tier_z(ou) for ou in ou_scores]) + rng.uniform(-0.15, 0.15, n)

# ── Sibling edge trace (Hamming d = 1) ───────────────────────────────────────
print("Building sibling edge trace (d=1)…")
ex, ey, ez = [], [], []
for i in range(n):
    js = np.where(hamm[i, i+1:] <= 1)[0] + i + 1
    for j in js:
        ex += [float(xs[i]), float(xs[j]), None]
        ey += [float(ys[i]), float(ys[j]), None]
        ez += [float(zs[i]), float(zs[j]), None]
print(f"  {len(ex)//3} sibling edges")

edge_trace = go.Scatter3d(
    x=ex, y=ey, z=ez,
    mode="lines",
    line=dict(color="rgb(38,40,65)", width=1),
    hoverinfo="none",
    showlegend=False,
)

# ── Traces ───────────────────────────────────────────────────────────────────
# go.Scatter3d does not render HTML in legend name; plain-text names are used
# here and a post_script JS snippet patches the SVG tspan subscripts after render.

traces: list = [edge_trace]

for phi_val, phi_color in PHI_COLOR.items():
    idx = [i for i, e in enumerate(catalog) if e.get("⊙", "⊙_ž") == phi_val]
    if not idx:
        continue
    sel_ou = [ou_scores[i] for i in idx]
    sizes  = [10 if math.isinf(ou) else 4 + ou * 1.8 for ou in sel_ou]
    syms   = ["diamond" if math.isinf(ou) else "circle" for ou in sel_ou]
    hovers = [hover_text(catalog[i], ou_scores[i]) for i in idx]

    traces.append(go.Scatter3d(
        x=xs[idx], y=ys[idx], z=zs[idx],
        mode="markers",
        name=PHI_LABEL[phi_val],
        showlegend=True,
        marker=dict(
            color=phi_color,
            size=sizes,
            symbol=syms,
            opacity=0.82,
            line=dict(width=0),
        ),
        text=hovers,
        hovertemplate="%{text}<extra></extra>",
    ))

# ── Key-node label and marker traces ─────────────────────────────────────────
# Project key imscriptions into MDS space via their ordinal vectors
key_names  = list(KEY_imscriptions.keys())
key_vecs   = np.stack([to_vector(KEY_imscriptions[k]) for k in key_names])
key_ou     = [ouroboricity(KEY_imscriptions[k]) for k in key_names]

# Project onto the MDS eigenvectors:
# MDS found coords = vecs_all @ eigvecs * sqrt(eigvals)
# We recover the projection matrix from the full run.
# Simpler: use the nearest catalog entry for each key node.
key_xs, key_ys, key_zs = [], [], []
key_hovers = []
for kname, kvec, kou in zip(key_names, key_vecs, key_ou):
    # nearest catalog entry by Euclidean ordinal distance
    dists = np.linalg.norm(vecs - kvec, axis=1)
    nearest_i = int(np.argmin(dists))
    key_xs.append(float(xs[nearest_i]))
    key_ys.append(float(ys[nearest_i]))
    key_zs.append(float(zs[nearest_i]) + 0.3)
    e = KEY_imscriptions[kname]
    tier = "O<sub>∞</sub>" if math.isinf(kou) else f"O<sub>{int(kou)}</sub>"
    key_hovers.append(
        f"<b>{kname.replace(chr(10), ' ')}</b><br>"
        f"Key node  ·  {tier}"
    )

traces.append(go.Scatter3d(
    x=key_xs, y=key_ys, z=key_zs,
    mode="markers+text",
    text=[k.replace("\n", " ") for k in key_names],
    textfont=dict(color="white", size=10),
    textposition="top center",
    marker=dict(
        color="white", size=9,
        symbol=["diamond" if k in MILLENNIUM else "circle" for k in key_names],
        opacity=0.92,
        line=dict(color="#FFD700", width=2),
    ),
    hovertemplate="%{text}<extra></extra>",
    customdata=key_hovers,
    showlegend=True,
    name="Key nodes",
))

# ── Layout ────────────────────────────────────────────────────────────────────
z_tickvals = [0, 1, 2, 3, 4, 6]
z_ticktext  = ["O₀ (sub-crit)", "O₁", "O₂", "O₃", "O₄", "O∞ (holographic)"]

layout = go.Layout(
    title=dict(
        text=(
            f"Imscribing Grammar — Primitive Space  ({len(catalog)} catalog entries)"
            "  ·  x,y: Mahalanobis MDS (§26.2)  ·  z: Ouroboricity tier"
        ),
        font=dict(color="white", size=15),
        x=0.5,
    ),
    paper_bgcolor="#0F0F1A",
    plot_bgcolor="#0F0F1A",
    scene=dict(
        bgcolor="#0F0F1A",
        xaxis=dict(
            title=dict(text="e₁: topological-criticality  Ω vs Γ+⊙", font=dict(color="#888899")),
            tickfont=dict(color="#888899"),
            gridcolor="#222233",
            zerolinecolor="#333344",
            showbackground=True,
            backgroundcolor="#0F0F1A",
        ),
        yaxis=dict(
            title=dict(text="e₂: criticality  ⊙ vs Γ+Ð", font=dict(color="#888899")),
            tickfont=dict(color="#888899"),
            gridcolor="#222233",
            zerolinecolor="#333344",
            showbackground=True,
            backgroundcolor="#0F0F1A",
        ),
        zaxis=dict(
            title=dict(text="Ouroboricity  O(x)", font=dict(color="#888899")),
            tickfont=dict(color="#888899"),
            gridcolor="#222233",
            zerolinecolor="#333344",
            tickvals=z_tickvals,
            ticktext=z_ticktext,
            showbackground=True,
            backgroundcolor="#0F0F1A",
        ),
        camera=dict(eye=dict(x=1.6, y=1.4, z=0.9)),
    ),
    legend=dict(
        font=dict(color="white", size=12),
        bgcolor="rgba(15,15,26,0.75)",
        bordercolor="#555577",
        borderwidth=1,
        x=0.01, y=0.99,
    ),
    margin=dict(l=0, r=0, t=55, b=0),
    hoverlabel=dict(
        bgcolor="#1A1A2E",
        bordercolor="#555577",
        font=dict(color="white", size=12),
    ),
)

fig = go.Figure(data=traces, layout=layout)

_POST_SCRIPT = r"""
(function() {
    var NS = 'http://www.w3.org/2000/svg';
    var SUBS = [
        ["⊙_ž  (sub-critical)",          "⊙", "ž", "  (sub-critical)"],
        ["⊙_ÿ  (real-axis critical)",    "⊙", "ÿ", "  (real-axis critical)"],
        ["⊙_Æ  (complex-plane critical)","⊙", "Æ", "  (complex-plane critical)"],
        ["⊙_3  (exceptional point)",     "⊙", "3", "  (exceptional point)"],
        ["⊙_Ţ  (supercritical/runaway)", "⊙", "Ţ", "  (supercritical/runaway)"]
    ];
    function patch() {
        document.querySelectorAll('.legendtext').forEach(function(el) {
            var txt = el.textContent;
            for (var i = 0; i < SUBS.length; i++) {
                if (txt === SUBS[i][0]) {
                    while (el.firstChild) el.removeChild(el.firstChild);
                    el.appendChild(document.createTextNode(SUBS[i][1]));
                    var sp = document.createElementNS(NS, 'tspan');
                    sp.setAttribute('baseline-shift', 'sub');
                    sp.setAttribute('font-size', '0.75em');
                    sp.textContent = SUBS[i][2];
                    el.appendChild(sp);
                    el.appendChild(document.createTextNode(SUBS[i][3]));
                    break;
                }
            }
        });
    }
    var gd = document.getElementById('{plot_id}');
    gd.on('plotly_afterplot', patch);
    patch();

    // ── Jiggle ────────────────────────────────────────────────────────────────
    var _jigId   = null;
    var _jigBase = null;

    function _startJiggle() {
        var cam = (gd.layout.scene && gd.layout.scene.camera) || {};
        var eye = cam.eye || {x: 1.6, y: 1.4, z: 0.9};
        var r   = Math.sqrt(eye.x * eye.x + eye.y * eye.y);
        _jigBase = {az: Math.atan2(eye.y, eye.x), r: r, z: eye.z, t0: performance.now()};
        gd.removeListener('plotly_afterplot', patch);
        function frame(ts) {
            var phase = (ts - _jigBase.t0) / 7000 * 2 * Math.PI;
            var az    = _jigBase.az + 0.18 * Math.sin(phase);
            Plotly.relayout(gd, {'scene.camera.eye': {
                x: _jigBase.r * Math.cos(az),
                y: _jigBase.r * Math.sin(az),
                z: _jigBase.z + 0.06 * Math.sin(phase * 0.67)
            }});
            _jigId = requestAnimationFrame(frame);
        }
        _jigId = requestAnimationFrame(frame);
    }

    function _stopJiggle() {
        cancelAnimationFrame(_jigId);
        _jigId = null;
        gd.on('plotly_afterplot', patch);
        patch();
    }

    var btn = document.createElement('button');
    btn.innerHTML = '&#8645; Jiggle';
    Object.assign(btn.style, {
        position: 'fixed', bottom: '24px', right: '24px',
        padding: '7px 18px',
        background: '#0e0e1e', color: '#99aacc',
        border: '1px solid #334',
        borderRadius: '6px', cursor: 'pointer',
        fontSize: '13px', fontFamily: 'sans-serif',
        letterSpacing: '0.05em', zIndex: '9999',
        transition: 'border-color 0.2s, color 0.2s'
    });
    btn.addEventListener('click', function() {
        if (_jigId) {
            _stopJiggle();
            btn.style.borderColor = '#334';
            btn.style.color = '#99aacc';
        } else {
            _startJiggle();
            btn.style.borderColor = '#FFD700';
            btn.style.color = '#FFD700';
        }
    });
    document.body.appendChild(btn);
})();
"""

html = fig.to_html(
    include_plotlyjs="cdn",
    full_html=True,
    post_script=_POST_SCRIPT,
    config={"scrollZoom": True, "displayModeBar": True},
)
html = html.replace(
    "<body>",
    '<body style="background:#0F0F1A;margin:0;padding:0;">',
)

out = ROOT / "IG_primitive_map_3d.html"
with open(str(out), "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {out}")

# Copy to MillenniumAnkh
import shutil
ankh = ROOT.parent / "MillenniumAnkh"
if ankh.exists():
    dest = ankh / "IG_primitive_map_3d.html"
    shutil.copy(out, dest)
    print(f"Copied to: {dest}")
