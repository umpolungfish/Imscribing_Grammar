#!/usr/bin/env python3
"""
IG_primitive_map.py — Visual map of the Imscribing Grammar primitive space

Two-panel figure:
  Top:    Classical MDS projection of all catalog entries
  Bottom: Force-directed network of key theorem / lemma nodes with edges
          labelled by Hamming distance

Color encodes Phi (criticality tier):
  Phi_softsign         →  steel blue
  Phi_ctyogh           →  gold
  Phi_closerevepsilon   →  darkorange
  Phi_revepsilon          →  crimson
  Phi_upstep       →  mediumpurple

Node area encodes Ouroboricity O(x).
Special markers distinguish Millennium Prize problems (★) and field-theory
imscriptions (◆) from ordinary catalog entries (●).

Usage:
    python3 IG_primitive_map.py
Output:
    IG_primitive_map.png   (high-resolution, 300 dpi)
"""

import json
import sys
import math
from pathlib import Path
from collections import OrderedDict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
CATALOG_PATH = ROOT / "IG_catalog.json"

# ── Mahalanobis metric tensor (built from catalog) ────────────────────────────
sys.path.insert(0, str(ROOT))
from space_search.primitives import build_metric_tensor as _build_metric_tensor
_G = _build_metric_tensor(str(CATALOG_PATH))

# ── Extended ordinal map ─────────────────────────────────────────────────────
# Covers both catalog values and Lean-only values (D_cube, D_line, R_exact, …)
ORDINALS = {
    "D": {
        "Ð_point":    0.5,
        "Ð_line":     1.0,
        "Ð_ß":    1.5,
        "Ð_C": 2.0,
        "Ð_cube":     2.5,
        "Ð_;":    3.0,
        "Ð_ω":     4.0,
    },
    "T": {
        "Þ_linear":   0.5,
        "Þ_branched": 1.0,
        "Þ_6":  1.5,
        "Þ_K":       2.0,
        "Þ_ò":   3.0,
        "Þ_box":      3.5,
        "Þ_torus":    4.0,
        "Þ_O":     5.0,
    },
    "R": {
        "Ř_exact":      0.5,
        "Ř_subset":     0.8,
        "Ř_superset":   1.0,
        "Ř_¯":      1.0,
        "Ř_ý":        2.0,
        "Ř_catalytic":  2.1,
        "Ř_=":         2.5,
        "Ř_Ť":     3.0,
        "Ř_allosteric": 3.5,
    },
    "P": {
        "Φ_neutral": 0.5,
        "Φ_plus":    0.8,
        "Φ_minus":   0.9,
        "Φ_ɐ":    1.0,
        "Φ_υ":     2.0,
        "Φ_F":      2.5,
        "Φ_}":  3.0,
        "Φ_˙":     3.5,
    },
    "F": {
        "ƒ_noise": 0.5,
        "ƒ_ì":   1.0,
        "ƒ_ð":   2.0,
        "ƒ_ż":  3.0,
    },
    "K": {
        "Ç_-": 1.0,
        "Ç_W":  2.0,
        "Ç_@": 3.0,
        "Ç_Ù": 4.0,
        "Ç_λ":  4.5,
    },
    "G": {
        "Γ_β":  1.0,
        "Γ_γ": 2.0,
        "Γ_ʔ": 3.0,
    },
    "Gamma": {
        "ɢ_^":   1.0,
        "ɢ_˝":    2.0,
        "Γ_xor":   2.5,
        "ɢ_ˌ":   3.0,
        "Γ_impl":  3.5,
        "ɢ_Ş": 4.0,
        "Γ_disc":  4.5,
    },
    "Phi": {
        "φ̂_ž":       1.0,
        "φ̂_ÿ":         2.0,
        "φ̂_Æ": 2.33,
        "φ̂_3":        2.67,
        "φ̂_Ţ":     3.0,
    },
    "H": {
        "Ħ_Ñ":    1.0,
        "Ħ_£":    2.0,
        "Ħ_A":    3.0,
        "Ħ_!": 4.0,
    },
    "S": {
        "Σ_S": 1.0,
        "one_n":   1.5,
        "Σ_ő":     2.0,
        "Σ_ï":     3.0,
        "cat":     4.0,
    },
    "Omega": {
        "Ω_Å":  0.0,
        "Ω_2": 1.0,
        "Ω_z":  2.0,
        "Ω_C":  3.0,
        "Ω_5": 4.0,
    },
}

PRIM_ORDER = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

# ── Phi colour map ────────────────────────────────────────────────────────────
PHI_COLOR = {
    "φ̂_ž":       "#4472C4",   # steel blue
    "φ̂_ÿ":         "#FFD700",   # gold
    "φ̂_Æ": "#FF8C00",   # dark orange
    "φ̂_3":        "#DC143C",   # crimson
    "φ̂_Ţ":     "#9370DB",   # medium purple
}
PHI_LABEL = {
    "φ̂_ž":       r"$\Phi_\mathrm{sub}$",
    "φ̂_ÿ":         r"$\Phi_ctyogh$  (real-axis)",
    "φ̂_Æ": r"$\Phi_ctyogh^\mathbb{C}$  (complex-axis)",
    "φ̂_3":        r"$\Phi_\mathrm{EP}$  (exceptional point)",
    "φ̂_Ţ":     r"$\Phi_\mathrm{sup}$",
}

# ── Ouroboricity formula ──────────────────────────────────────────────────────
def ouroboricity(entry: dict) -> float:
    """O(x) = [Phi=Phi_ctyogh* ] * (1 + [Omega≠Omega_closeepsilon] + [H≥H_toneletterstem] + [G=G_revapostrophe])
    Returns inf when H=H_invscripta and Phi is critical."""
    phi = entry.get("Phi", "")
    is_critical = phi in ("φ̂_ÿ", "φ̂_Æ", "φ̂_3")
    if not is_critical:
        return 0.0
    h = entry.get("H", "Ħ_Ñ")
    if h == "Ħ_!":
        return float("inf")
    omega = entry.get("Omega", "Ω_Å")
    g = entry.get("G", "")
    score = 1.0
    if omega != "Ω_Å":
        score += 1
    if h in ("Ħ_£", "Ħ_A", "Ħ_!"):
        score += 1
    if g == "Γ_ʔ":
        score += 1
    return score

# ── Entry → ordinal vector ────────────────────────────────────────────────────
def to_vector(entry: dict) -> np.ndarray:
    vec = []
    for p in PRIM_ORDER:
        val = entry.get(p, "")
        vec.append(ORDINALS[p].get(val, 0.0))
    return np.array(vec, dtype=float)

# ── Hamming distance (mismatch count) — used for network edges ────────────────
def hamming(a: dict, b: dict) -> int:
    return sum(a.get(p) != b.get(p) for p in PRIM_ORDER)

# ── Mahalanobis distance — canonical metric for MDS ──────────────────────────
def mahalanobis_dist(a: dict, b: dict) -> float:
    """d = sqrt((v_a - v_b)^T G (v_a - v_b)), G = Sigma^{-1} from catalog."""
    va = to_vector(a)
    vb = to_vector(b)
    delta = va - vb
    sq = float(delta @ _G @ delta)
    return float(np.sqrt(max(sq, 0.0)))

# ── Classical MDS ─────────────────────────────────────────────────────────────
def cmds(D_sq: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Classical MDS from squared distance matrix."""
    n = D_sq.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * H @ D_sq @ H
    vals, vecs = np.linalg.eigh(B)
    # Sort descending
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    # Take top components; clip negative eigenvalues to 0
    vals_pos = np.maximum(vals[:n_components], 0)
    coords = vecs[:, :n_components] * np.sqrt(vals_pos)[np.newaxis, :]
    return coords

# ── Load catalog ──────────────────────────────────────────────────────────────
with open(CATALOG_PATH) as f:
    catalog: list[dict] = json.load(f)

print(f"Loaded {len(catalog)} catalog entries.")

# ── Compute MDS coords for full catalog ───────────────────────────────────────
vecs = np.stack([to_vector(e) for e in catalog])
n = len(vecs)

# Mahalanobis distance matrix for MDS (g = Sigma^{-1}, §26.2) — vectorised
print("Computing pairwise Mahalanobis distances (vectorised) …")
vG = vecs @ _G                            # (n, 12)
diag_maha = (vG * vecs).sum(axis=1)      # (n,)
cross = vG @ vecs.T                       # (n, n)
D_sq_full = diag_maha[:, None] + diag_maha[None, :] - 2.0 * cross
maha_mat = np.sqrt(np.maximum(D_sq_full, 0.0)).astype(np.float32)

# Separate Hamming matrix — vectorised
print("Computing pairwise Hamming distances (vectorised, for sibling edges) …")
hamm_mat = np.sum(
    vecs[:, None, :] != vecs[None, :, :], axis=2
).astype(np.float32)

mds_coords = cmds(maha_mat ** 2)
print("MDS projection done.")

# ── Key theorem / lemma nodes ─────────────────────────────────────────────────
# These include both catalog entries and the Lean-defined imscriptions in Imscription.lean
# and PrimitiveBridge.lean (encoded in catalog-compatible format).
KEY_imscriptions: dict[str, dict] = {
    # ── Millennium Prize encodings (PrimitiveBridge.lean) ─────────────────
    "YM classical":      {"D":"Ð_cube",  "T":"Þ_6","R":"Ř_exact",     "P":"Φ_F",     "F":"ƒ_ð",  "K":"Ç_W",  "G":"Γ_β",  "Gamma":"ɢ_^",  "Phi":"φ̂_ž",       "H":"Ħ_£",  "S":"one_n", "Omega":"Ω_z"},
    "YM quantum\n(target)": {"D":"Ð_cube","T":"Þ_6","R":"Ř_exact",    "P":"Φ_F",     "F":"ƒ_ż", "K":"Ç_Ù", "G":"Γ_ʔ", "Gamma":"ɢ_^",  "Phi":"φ̂_ÿ",         "H":"Ħ_£",  "S":"one_n", "Omega":"Ω_z"},
    "RH (ζ zeros)":      {"D":"Ð_line",  "T":"Þ_6","R":"Ř_exact",     "P":"Φ_neutral","F":"ƒ_ż", "K":"Ç_@", "G":"Γ_ʔ", "Gamma":"ɢ_^",  "Phi":"φ̂_Æ", "H":"Ħ_Ñ",  "S":"one_n", "Omega":"Ω_Å"},
    "Lee-Yang\n(proved)":{"D":"Ð_line",  "T":"Þ_ò", "R":"Ř_exact",     "P":"Φ_υ",    "F":"ƒ_ì",  "K":"Ç_W",  "G":"Γ_γ", "Gamma":"ɢ_^",  "Phi":"φ̂_Æ", "H":"Ħ_£",  "S":"Σ_ï",   "Omega":"Ω_Å"},
    "NS smooth\nsoln":   {"D":"Ð_cube",  "T":"Þ_6","R":"Ř_catalytic",  "P":"Φ_neutral","F":"ƒ_ð",  "K":"Ç_W",  "G":"Γ_β",  "Gamma":"ɢ_^",  "Phi":"φ̂_ž",       "H":"Ħ_Ñ",  "S":"Σ_ï",   "Omega":"Ω_Å"},
    "OPN\nconstraint":   {"D":"Ð_point", "T":"Þ_linear", "R":"Ř_exact",     "P":"Φ_neutral","F":"ƒ_ì",  "K":"Ç_Ù", "G":"Γ_ʔ", "Gamma":"ɢ_^",  "Phi":"φ̂_ÿ",         "H":"Ħ_Ñ",  "S":"one_n", "Omega":"Ω_Å"},
    # ── Field-theory imscriptions (Imscription.lean) ──────────────────────────────
    "Higgs / axion\n/ inflaton":{"D":"Ð_point","T":"Þ_ò","R":"Ř_catalytic","P":"Φ_}","F":"ƒ_ż","K":"Ç_@","G":"Γ_β","Gamma":"ɢ_^","Phi":"φ̂_ÿ","H":"Ħ_£","S":"one_n","Omega":"Ω_Å"},
    "Standard\nModel":   {"D":"Ð_cube",  "T":"Þ_6","R":"Ř_allosteric", "P":"Φ_F",     "F":"ƒ_ð",  "K":"Ç_W",  "G":"Γ_ʔ", "Gamma":"ɢ_^",  "Phi":"φ̂_ÿ",         "H":"Ħ_A",  "S":"Σ_ï",   "Omega":"Ω_z"},
    "Quantum\nGravity":  {"D":"Ð_ω",  "T":"Þ_O",   "R":"Ř_exact",     "P":"Φ_neutral","F":"ƒ_ż", "K":"Ç_Ù", "G":"Γ_ʔ", "Gamma":"Γ_impl", "Phi":"φ̂_ÿ",         "H":"Ħ_!","S":"Σ_ï",  "Omega":"Ω_5"},
    "General\nRelativity":{"D":"Ð_cube", "T":"Þ_6","R":"Ř_catalytic",  "P":"Φ_neutral","F":"ƒ_ż", "K":"Ç_@", "G":"Γ_γ", "Gamma":"ɢ_^",  "Phi":"φ̂_ž",       "H":"Ħ_£",  "S":"one_n", "Omega":"Ω_Å"},
    "Asymptotic\nSafety":{"D":"Ð_cube",  "T":"Þ_6","R":"Ř_catalytic",  "P":"Φ_neutral","F":"ƒ_ż", "K":"Ç_W",  "G":"Γ_ʔ", "Gamma":"ɢ_^",  "Phi":"φ̂_ÿ",         "H":"Ħ_£",  "S":"one_n", "Omega":"Ω_Å"},
}

# Supplement with catalog entries by name
KEY_CATALOG = [
    "abc_conjecture", "ising_3d", "lee_yang_edge", "exceptional_point_nh",
    "complex_rg_fixed_point", "thylakoid_membrane", "artificial_leaf",
    "photosystem_II", "yhwh", "aleph_tav_join",
]
catalog_by_name = {e["name"]: e for e in catalog}
for name in KEY_CATALOG:
    if name in catalog_by_name:
        label = name.replace("_", "\n")
        KEY_imscriptions[label] = catalog_by_name[name]

# Assign a marker type
MILLENNIUM = {"YM classical", "YM quantum\n(target)", "RH (ζ zeros)",
              "Lee-Yang\n(proved)", "NS smooth\nsoln", "OPN\nconstraint"}
FIELD_THEORY = {"Higgs / axion\n/ inflaton", "Standard\nModel", "Quantum\nGravity",
                "General\nRelativity", "Asymptotic\nSafety"}

# ── Compute key-node pairwise distances & spring layout ───────────────────────
key_names = list(KEY_imscriptions.keys())
key_entries = [KEY_imscriptions[k] for k in key_names]
k = len(key_names)

key_dist = np.zeros((k, k), dtype=float)
for i in range(k):
    for j in range(k):
        key_dist[i, j] = hamming(key_entries[i], key_entries[j])

# NetworkX graph for spring layout
G = nx.Graph()
for i, name in enumerate(key_names):
    G.add_node(i, label=name, phi=key_entries[i].get("Phi", "φ̂_ž"))
# Add edges for pairs with distance ≤ 7
EDGE_THRESHOLD = 7
for i in range(k):
    for j in range(i + 1, k):
        d = key_dist[i, j]
        if d <= EDGE_THRESHOLD:
            G.add_edge(i, j, weight=float(EDGE_THRESHOLD - d + 1) / EDGE_THRESHOLD,
                       dist=int(d))

# Spring layout seeded for reproducibility
try:
    pos = nx.kamada_kawai_layout(G, weight="weight")
except Exception:
    pos = nx.spring_layout(G, weight="weight", seed=42, k=1.8, iterations=400)

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — MDS scatter of full catalog
# ─────────────────────────────────────────────────────────────────────────────
fig_mds = plt.figure(figsize=(20, 16), facecolor="#0F0F1A")
fig_mds.patch.set_facecolor("#0F0F1A")
fig_mds.subplots_adjust(top=0.94, bottom=0.07, left=0.06, right=0.97)
ax_mds = fig_mds.add_subplot(111)
ax_mds.set_facecolor("#0F0F1A")
for spine in ax_mds.spines.values():
    spine.set_visible(False)
ax_mds.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax_mds.set_title(
    f"Imscribing Grammar Primitive Space — Classical MDS Projection of {len(catalog)} Catalog Entries"
    r"  (Mahalanobis metric $g = \Sigma^{-1}$, §26.2)",
    color="white", fontsize=17, pad=14, fontweight="bold"
)

xs, ys = mds_coords[:, 0], mds_coords[:, 1]

for entry, x, y in zip(catalog, xs, ys):
    phi = entry.get("Phi", "φ̂_ž")
    color = PHI_COLOR.get(phi, "#888888")
    ou = ouroboricity(entry)
    size = 60 if math.isinf(ou) else 22 + ou * 18
    alpha = 0.80
    ax_mds.scatter(x, y, s=size, c=color, alpha=alpha, linewidths=0,
                   zorder=2)

# Draw thin edges for pairs with Hamming distance = 1 (structural siblings)
SIB_THRESHOLD = 1
print("Drawing sibling edges (Hamming d=1) …")
n_edge_drawn = 0
for i in range(n):
    for j in range(i + 1, n):
        if hamm_mat[i, j] <= SIB_THRESHOLD:
            ax_mds.plot([xs[i], xs[j]], [ys[i], ys[j]],
                        color="#FFFFFF", alpha=0.04, linewidth=0.4, zorder=1)
            n_edge_drawn += 1
print(f"  drew {n_edge_drawn} sibling edges")

# Label a handful of key named entries in the MDS space
LABEL_NAMES = {
    "abc_conjecture": "ABC conjecture",
    "ising_3d": "3D Ising",
    "lee_yang_edge": "Lee-Yang edge",
    "exceptional_point_nh": "Exceptional point",
    "complex_rg_fixed_point": "Complex RG FP",
    "thylakoid_membrane": "Thylakoid",
    "artificial_leaf": "Artificial leaf",
    "yhwh": "YHWH  ∞",
    "aleph_tav_join": "ℵ–τ join  ∞",
    "photosystem_II": "PSII",
}
for entry, x, y in zip(catalog, xs, ys):
    if entry["name"] in LABEL_NAMES:
        ax_mds.annotate(
            LABEL_NAMES[entry["name"]],
            (x, y), xytext=(6, 6), textcoords="offset points",
            color="white", fontsize=9.5, alpha=0.95,
            bbox=dict(boxstyle="round,pad=0.3", fc="#0F0F1A", ec="#333355", alpha=0.82),
            zorder=5
        )

# Criticality legend — lower right
phi_patches = [
    mpatches.Patch(facecolor=PHI_COLOR[p], label=PHI_LABEL[p], linewidth=0)
    for p in ["φ̂_ž", "φ̂_ÿ", "φ̂_Æ", "φ̂_3", "φ̂_Ţ"]
]
leg1 = ax_mds.legend(
    handles=phi_patches, loc="lower right",
    bbox_to_anchor=(1.0, 0.02), bbox_transform=ax_mds.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Criticality (Φ)",
    title_fontsize=14, borderpad=1.0, labelspacing=0.6
)
leg1.get_title().set_color("white")

# Ouroboricity legend — directly above Criticality, right-aligned
from matplotlib.lines import Line2D
size_items = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#AAAAAA',
           markersize=math.sqrt(22 + ou * 18) * 0.8, linestyle='None',
           label=f"O = {ou}")
    for ou in [0, 1, 2, 3, 4]
] + [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='white',
           markersize=14, linestyle='None', label="O = ∞")
]
leg2 = ax_mds.legend(
    handles=size_items, loc="lower right",
    bbox_to_anchor=(1.0, 0.20), bbox_transform=ax_mds.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Ouroboricity (O)",
    title_fontsize=14, ncol=2, borderpad=1.0, labelspacing=0.6
)
leg2.get_title().set_color("white")
ax_mds.add_artist(leg1)   # keep both legends

# Axis labels — eigenmode descriptions only (§26.6)
ax_mds.set_xlabel(
    r"$\mathbf{e}_1$: topological-criticality  $\Omega$ vs $G+\Phi$",
    color="#888899", fontsize=12)
ax_mds.set_ylabel(
    r"$\mathbf{e}_2$: criticality  $\Phi$ vs $G+D$",
    color="#888899", fontsize=12)
ax_mds.tick_params(labelbottom=True, labelleft=True, colors="#888899")
ax_mds.xaxis.label.set_color("#888899")

# ── Save figure 1 ─────────────────────────────────────────────────────────────
fig_mds.text(
    0.5, 0.995,
    "Imscribing Grammar — Primitive Space Map  •  2026-04-08",
    ha="center", va="top", color="white", fontsize=12, alpha=0.6,
    fontfamily="monospace"
)
out_mds = ROOT / "IG_primitive_map_mds.png"
fig_mds.savefig(out_mds, dpi=300, facecolor=fig_mds.get_facecolor())
print(f"Saved: {out_mds}")
plt.close(fig_mds)

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Key theorem network
# ─────────────────────────────────────────────────────────────────────────────
fig_net = plt.figure(figsize=(20, 18), facecolor="#0F0F1A")
fig_net.patch.set_facecolor("#0F0F1A")
fig_net.subplots_adjust(top=0.94, bottom=0.07, left=0.06, right=0.97)
ax_net = fig_net.add_subplot(111)
ax_net.set_facecolor("#0F0F1A")
for spine in ax_net.spines.values():
    spine.set_visible(False)
ax_net.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax_net.set_title(
    "Primitive-Space Theorem Network — Key Lemma Nodes (edges: Hamming ≤ 7)",
    color="white", fontsize=18, pad=14, fontweight="bold"
)

# Draw edges
for u, v, data in G.edges(data=True):
    d = data["dist"]
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    # Width and alpha by proximity
    lw = max(0.4, 3.5 - d * 0.45)
    alpha = max(0.12, 0.75 - d * 0.10)
    ax_net.plot([x0, x1], [y0, y1], color="#7777CC", lw=lw, alpha=alpha, zorder=1)
    # Edge distance label at midpoint
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax_net.text(mx, my, str(d), fontsize=7.5, color="#BBBBDD", ha="center", va="center",
                zorder=3, alpha=0.85,
                bbox=dict(boxstyle="round,pad=0.1", fc="#0F0F1A", ec="none", alpha=0.5))

# Draw nodes
for i, name in enumerate(key_names):
    entry = key_entries[i]
    phi = entry.get("Phi", "φ̂_ž")
    color = PHI_COLOR.get(phi, "#888888")
    ou = ouroboricity(entry)
    x, y = pos[i]

    if name in MILLENNIUM:
        marker = "*"
        size = 600 if math.isinf(ou) else 350 + ou * 60
        edgecolor = "white"
        ew = 1.6
    elif name in FIELD_THEORY:
        marker = "D"
        size = 450 if math.isinf(ou) else 280 + ou * 50
        edgecolor = "#CCCCCC"
        ew = 1.0
    else:
        marker = "o"
        size = 400 if math.isinf(ou) else 240 + ou * 45
        edgecolor = "#888888"
        ew = 0.7

    ax_net.scatter(x, y, s=size, c=color, marker=marker,
                   edgecolors=edgecolor, linewidths=ew, zorder=4, alpha=0.92)

    # O-score badge for high-ouroboricity nodes
    if math.isinf(ou):
        badge = "O∞"
    elif ou >= 3:
        badge = f"O{int(ou)}"
    else:
        badge = ""

    # Node label — offset in screen points so distance is consistent regardless of layout scale
    ax_net.annotate(
        name, (x, y), xytext=(0, -16), textcoords="offset points",
        ha="center", va="top", fontsize=11,
        color="white", fontweight="normal", zorder=5,
        annotation_clip=False,
        bbox=dict(boxstyle="round,pad=0.35", fc="#0F0F1A", ec="#333355", alpha=0.82),
    )
    if badge:
        ax_net.text(x + 0.04, y + 0.04, badge, ha="left", va="bottom",
                    fontsize=9, color="#FFD700", fontweight="bold", zorder=6)

# Criticality legend — lower left (bottom)
phi_patches2 = [
    mpatches.Patch(facecolor=PHI_COLOR[p], label=PHI_LABEL[p], linewidth=0)
    for p in ["φ̂_ž", "φ̂_ÿ", "φ̂_Æ", "φ̂_3", "φ̂_Ţ"]
]
leg4 = ax_net.legend(
    handles=phi_patches2, loc="lower left",
    bbox_to_anchor=(0.0, 0.02), bbox_transform=ax_net.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Criticality (Φ)",
    title_fontsize=14, borderpad=1.0, labelspacing=0.6
)
leg4.get_title().set_color("white")

# Node type legend — directly above Criticality, left-aligned
marker_items = [
    Line2D([0], [0], marker='*', color='w', markerfacecolor='#AAAAAA',
           markersize=13, linestyle='None', label="Millennium Prize problem"),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#AAAAAA',
           markersize=8,  linestyle='None', label="Field-theory imscription (Lean)"),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#AAAAAA',
           markersize=8,  linestyle='None', label="Catalog entry"),
]
leg3 = ax_net.legend(
    handles=marker_items, loc="lower left",
    bbox_to_anchor=(0.0, 0.18), bbox_transform=ax_net.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Node type",
    title_fontsize=14, borderpad=1.0, labelspacing=0.6
)
leg3.get_title().set_color("white")
ax_net.add_artist(leg4)

# ── Save figure 2 ─────────────────────────────────────────────────────────────
fig_net.text(
    0.5, 0.995,
    "Imscribing Grammar — Primitive Space Map  •  2026-04-08",
    ha="center", va="top", color="white", fontsize=12, alpha=0.6,
    fontfamily="monospace"
)
out_net = ROOT / "IG_primitive_map_network.png"
fig_net.savefig(out_net, dpi=300, facecolor=fig_net.get_facecolor())
print(f"Saved: {out_net}")
plt.close(fig_net)
