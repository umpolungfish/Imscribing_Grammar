#!/usr/bin/env python3
"""
IG_primitive_map.py — Visual map of the Imscribing Grammar primitive space

Two-panel figure:
  Top:    Classical MDS projection of all catalog entries
  Bottom: Force-directed network of key theorem / lemma nodes with edges
          labelled by Hamming distance

Color encodes Phi (criticality tier):
  Phi_softsign         →  steel blue
  ⊙           →  gold
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
        "𐑛":    0.5,
        "𐑛":     1.0,
        "𐑛":    1.5,
        "𐑨": 2.0,
        "𐑨":     2.5,
        "𐑼":    3.0,
        "𐑦":     4.0,
    },
    "T": {
        "𐑰":   0.5,
        "𐑰": 1.0,
        "𐑡":  1.5,
        "𐑰":       2.0,
        "𐑥":   3.0,
        "𐑶":      3.5,
        "𐑥":    4.0,
        "𐑸":     5.0,
    },
    "R": {
        "𐑑":      0.5,
        "𐑩":     0.8,
        "𐑩":   1.0,
        "𐑩":      1.0,
        "𐑑":        2.0,
        "𐑽":  2.1,
        "𐑾":         2.5,
        "𐑽":     3.0,
        "𐑽": 3.5,
    },
    "P": {
        "𐑯": 0.5,
        "𐑬":    0.8,
        "𐑬":   0.9,
        "𐑗":    1.0,
        "𐑿":     2.0,
        "𐑬":      2.5,
        "𐑹":  3.0,
        "𐑯":     3.5,
    },
    "F": {
        "𐑱": 0.5,
        "⋈^ì":   1.0,
        "⋈^ð":   2.0,
        "⋈^ż":  3.0,
    },
    "K": {
        "⊤^-": 1.0,
        "⊤^W":  2.0,
        "⊤^@": 3.0,
        "⊤^Ù": 4.0,
        "⊤^λ":  4.5,
    },
    "G": {
        "𐑚":  1.0,
        "𐑔": 2.0,
        "𐑲": 3.0,
    },
    "Gamma": {
        "ɢ^∧":   1.0,
        "ɢ^˝":    2.0,
        "Γ_xor":   2.5,
        "ɢ^ˌ":   3.0,
        "Γ_impl":  3.5,
        "ɢ^Ş": 4.0,
        "∈_disc":  4.5,
    },
    "Phi": {
        "𐑢":       1.0,
        "⊙":         2.0,
        "𐑮": 2.33,
        "𐑻":        2.67,
        "𐑣":     3.0,
    },
    "H": {
        "𐑓":    1.0,
        "𐑒":    2.0,
        "𐑖":    3.0,
        "𐑫": 4.0,
    },
    "S": {
        "𐑙": 1.0,
        "one_n":   1.5,
        "𐑕":     2.0,
        "𐑳":     3.0,
        "cat":     4.0,
    },
    "Omega": {
        "𐑷":  0.0,
        "𐑴": 1.0,
        "𐑭":  2.0,
        "Ω_C":  3.0,
        "𐑟": 4.0,
    },
}

PRIM_ORDER = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

# ── Phi colour map ────────────────────────────────────────────────────────────
PHI_COLOR = {
    "𐑢":       "#4472C4",   # steel blue
    "⊙":         "#FFD700",   # gold
    "𐑮": "#FF8C00",   # dark orange
    "𐑻":        "#DC143C",   # crimson
    "𐑣":     "#9370DB",   # medium purple
}
PHI_LABEL = {
    "𐑢":       r"$\Phi_\mathrm{sub}$",
    "⊙":         r"$\⊙$  (real-axis)",
    "𐑮": r"$\⊙^\mathbb{C}$  (complex-axis)",
    "𐑻":        r"$\Phi_\mathrm{EP}$  (exceptional point)",
    "𐑣":     r"$\Phi_\mathrm{sup}$",
}

# ── Ouroboricity formula ──────────────────────────────────────────────────────
def ouroboricity(entry: dict) -> float:
    """O(x) = [Phi=⊙* ] * (1 + [Omega≠Omega_closeepsilon] + [H≥H_toneletterstem] + [G=G_revapostrophe])
    Returns inf when H=H_invscripta and Phi is critical."""
    phi = entry.get("Phi", "")
    is_critical = phi in ("⊙", "𐑮", "𐑻")
    if not is_critical:
        return 0.0
    h = entry.get("H", "𐑓")
    if h == "𐑫":
        return float("inf")
    omega = entry.get("Omega", "𐑷")
    g = entry.get("G", "")
    score = 1.0
    if omega != "𐑷":
        score += 1
    if h in ("𐑒", "𐑖", "𐑫"):
        score += 1
    if g == "𐑲":
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
    "YM classical":      {"D":"𐑨",  "T":"𐑡","R":"𐑑",     "P":"𐑬",     "F":"⋈^ð",  "K":"⊤^W",  "G":"𐑚",  "Gamma":"ɢ^∧",  "Phi":"𐑢",       "H":"𐑒",  "S":"one_n", "Omega":"𐑭"},
    "YM quantum\n(target)": {"D":"𐑨","T":"𐑡","R":"𐑑",    "P":"𐑬",     "F":"⋈^ż", "K":"⊤^Ù", "G":"𐑲", "Gamma":"ɢ^∧",  "Phi":"⊙",         "H":"𐑒",  "S":"one_n", "Omega":"𐑭"},
    "RH (ζ zeros)":      {"D":"𐑛",  "T":"𐑡","R":"𐑑",     "P":"𐑯","F":"⋈^ż", "K":"⊤^@", "G":"𐑲", "Gamma":"ɢ^∧",  "Phi":"𐑮", "H":"𐑓",  "S":"one_n", "Omega":"𐑷"},
    "Lee-Yang\n(proved)":{"D":"𐑛",  "T":"𐑥", "R":"𐑑",     "P":"𐑿",    "F":"⋈^ì",  "K":"⊤^W",  "G":"𐑔", "Gamma":"ɢ^∧",  "Phi":"𐑮", "H":"𐑒",  "S":"𐑳",   "Omega":"𐑷"},
    "NS smooth\nsoln":   {"D":"𐑨",  "T":"𐑡","R":"𐑽",  "P":"𐑯","F":"⋈^ð",  "K":"⊤^W",  "G":"𐑚",  "Gamma":"ɢ^∧",  "Phi":"𐑢",       "H":"𐑓",  "S":"𐑳",   "Omega":"𐑷"},
    "OPN\nconstraint":   {"D":"𐑛", "T":"𐑰", "R":"𐑑",     "P":"𐑯","F":"⋈^ì",  "K":"⊤^Ù", "G":"𐑲", "Gamma":"ɢ^∧",  "Phi":"⊙",         "H":"𐑓",  "S":"one_n", "Omega":"𐑷"},
    # ── Field-theory imscriptions (Imscription.lean) ──────────────────────────────
    "Higgs / axion\n/ inflaton":{"D":"𐑛","T":"𐑥","R":"𐑽","P":"𐑹","F":"⋈^ż","K":"⊤^@","G":"𐑚","Gamma":"ɢ^∧","Phi":"⊙","H":"𐑒","S":"one_n","Omega":"𐑷"},
    "Standard\nModel":   {"D":"𐑨",  "T":"𐑡","R":"𐑽", "P":"𐑬",     "F":"⋈^ð",  "K":"⊤^W",  "G":"𐑲", "Gamma":"ɢ^∧",  "Phi":"⊙",         "H":"𐑖",  "S":"𐑳",   "Omega":"𐑭"},
    "Quantum\nGravity":  {"D":"𐑦",  "T":"𐑸",   "R":"𐑑",     "P":"𐑯","F":"⋈^ż", "K":"⊤^Ù", "G":"𐑲", "Gamma":"Γ_impl", "Phi":"⊙",         "H":"𐑫","S":"𐑳",  "Omega":"𐑟"},
    "General\nRelativity":{"D":"𐑨", "T":"𐑡","R":"𐑽",  "P":"𐑯","F":"⋈^ż", "K":"⊤^@", "G":"𐑔", "Gamma":"ɢ^∧",  "Phi":"𐑢",       "H":"𐑒",  "S":"one_n", "Omega":"𐑷"},
    "Asymptotic\nSafety":{"D":"𐑨",  "T":"𐑡","R":"𐑽",  "P":"𐑯","F":"⋈^ż", "K":"⊤^W",  "G":"𐑲", "Gamma":"ɢ^∧",  "Phi":"⊙",         "H":"𐑒",  "S":"one_n", "Omega":"𐑷"},
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
    G.add_node(i, label=name, phi=key_entries[i].get("Phi", "𐑢"))
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
    phi = entry.get("Phi", "𐑢")
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
    for p in ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"]
]
leg1 = ax_mds.legend(
    handles=phi_patches, loc="lower right",
    bbox_to_anchor=(1.0, 0.02), bbox_transform=ax_mds.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Criticality (<)",
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
    phi = entry.get("Phi", "𐑢")
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
    for p in ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"]
]
leg4 = ax_net.legend(
    handles=phi_patches2, loc="lower left",
    bbox_to_anchor=(0.0, 0.02), bbox_transform=ax_net.transAxes,
    framealpha=0.4, facecolor="#1A1A2E", edgecolor="#555577",
    labelcolor="white", fontsize=13, title="Criticality (<)",
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
