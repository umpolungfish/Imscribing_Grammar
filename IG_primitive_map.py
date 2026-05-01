#!/usr/bin/env python3
"""
IG_primitive_map.py — Visual map of the Imscribing Grammar primitive space

Two-panel figure:
  Top:    Classical MDS projection of all catalog entries
  Bottom: Force-directed network of key theorem / lemma nodes with edges
          labelled by Hamming distance

Color encodes Phi (criticality tier):
  Phi_sub         →  steel blue
  Phi_c           →  gold
  Phi_c_complex   →  darkorange
  Phi_EP          →  crimson
  Phi_super       →  mediumpurple

Node area encodes Ouroboricity O(x).
Special markers distinguish Millennium Prize problems (★) and field-theory
synthons (◆) from ordinary catalog entries (●).

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
        "D_point":    0.5,
        "D_line":     1.0,
        "D_wedge":    1.5,
        "D_triangle": 2.0,
        "D_cube":     2.5,
        "D_infty":    3.0,
        "D_holo":     4.0,
    },
    "T": {
        "T_linear":   0.5,
        "T_branched": 1.0,
        "T_network":  1.5,
        "T_in":       2.0,
        "T_bowtie":   3.0,
        "T_box":      3.5,
        "T_torus":    4.0,
        "T_holo":     5.0,
    },
    "R": {
        "R_exact":      0.5,
        "R_subset":     0.8,
        "R_superset":   1.0,
        "R_super":      1.0,
        "R_cat":        2.0,
        "R_catalytic":  2.1,
        "R_lr":         2.5,
        "R_dagger":     3.0,
        "R_allosteric": 3.5,
    },
    "P": {
        "P_neutral": 0.5,
        "P_plus":    0.8,
        "P_minus":   0.9,
        "P_asym":    1.0,
        "P_psi":     2.0,
        "P_pm":      2.5,
        "P_pm_sym":  3.0,
        "P_sym":     3.5,
    },
    "F": {
        "F_noise": 0.5,
        "F_ell":   1.0,
        "F_eth":   2.0,
        "F_hbar":  3.0,
    },
    "K": {
        "K_fast": 1.0,
        "K_mod":  2.0,
        "K_slow": 3.0,
        "K_trap": 4.0,
        "K_MBL":  4.5,
    },
    "G": {
        "G_beth":  1.0,
        "G_gimel": 2.0,
        "G_aleph": 3.0,
    },
    "Gamma": {
        "G_and":   1.0,
        "G_or":    2.0,
        "G_xor":   2.5,
        "G_seq":   3.0,
        "G_impl":  3.5,
        "G_broad": 4.0,
        "G_disc":  4.5,
    },
    "Phi": {
        "Phi_sub":       1.0,
        "Phi_c":         2.0,
        "Phi_c_complex": 2.33,
        "Phi_EP":        2.67,
        "Phi_super":     3.0,
    },
    "H": {
        "H0":    1.0,
        "H1":    2.0,
        "H2":    3.0,
        "H_inf": 4.0,
    },
    "S": {
        "one_one": 1.0,
        "one_n":   1.5,
        "n_n":     2.0,
        "n_m":     3.0,
        "cat":     4.0,
    },
    "Omega": {
        "Omega_0":  0.0,
        "Omega_Z2": 1.0,
        "Omega_Z":  2.0,
        "Omega_C":  3.0,
        "Omega_NA": 4.0,
    },
}

PRIM_ORDER = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

# ── Phi colour map ────────────────────────────────────────────────────────────
PHI_COLOR = {
    "Phi_sub":       "#4472C4",   # steel blue
    "Phi_c":         "#FFD700",   # gold
    "Phi_c_complex": "#FF8C00",   # dark orange
    "Phi_EP":        "#DC143C",   # crimson
    "Phi_super":     "#9370DB",   # medium purple
}
PHI_LABEL = {
    "Phi_sub":       r"$\Phi_\mathrm{sub}$",
    "Phi_c":         r"$\Phi_c$  (real-axis)",
    "Phi_c_complex": r"$\Phi_c^\mathbb{C}$  (complex-axis)",
    "Phi_EP":        r"$\Phi_\mathrm{EP}$  (exceptional point)",
    "Phi_super":     r"$\Phi_\mathrm{sup}$",
}

# ── Ouroboricity formula ──────────────────────────────────────────────────────
def ouroboricity(entry: dict) -> float:
    """O(x) = [Phi=Phi_c* ] * (1 + [Omega≠Omega_0] + [H≥H1] + [G=G_aleph])
    Returns inf when H=H_inf and Phi is critical."""
    phi = entry.get("Phi", "")
    is_critical = phi in ("Phi_c", "Phi_c_complex", "Phi_EP")
    if not is_critical:
        return 0.0
    h = entry.get("H", "H0")
    if h == "H_inf":
        return float("inf")
    omega = entry.get("Omega", "Omega_0")
    g = entry.get("G", "")
    score = 1.0
    if omega != "Omega_0":
        score += 1
    if h in ("H1", "H2", "H_inf"):
        score += 1
    if g == "G_aleph":
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
# These include both catalog entries and the Lean-defined synthons in Synthon.lean
# and PrimitiveBridge.lean (encoded in catalog-compatible format).
KEY_SYNTHONS: dict[str, dict] = {
    # ── Millennium Prize encodings (PrimitiveBridge.lean) ─────────────────
    "YM classical":      {"D":"D_cube",  "T":"T_network","R":"R_exact",     "P":"P_pm",     "F":"F_eth",  "K":"K_mod",  "G":"G_beth",  "Gamma":"G_and",  "Phi":"Phi_sub",       "H":"H1",  "S":"one_n", "Omega":"Omega_Z"},
    "YM quantum\n(target)": {"D":"D_cube","T":"T_network","R":"R_exact",    "P":"P_pm",     "F":"F_hbar", "K":"K_trap", "G":"G_aleph", "Gamma":"G_and",  "Phi":"Phi_c",         "H":"H1",  "S":"one_n", "Omega":"Omega_Z"},
    "RH (ζ zeros)":      {"D":"D_line",  "T":"T_network","R":"R_exact",     "P":"P_neutral","F":"F_hbar", "K":"K_slow", "G":"G_aleph", "Gamma":"G_and",  "Phi":"Phi_c_complex", "H":"H0",  "S":"one_n", "Omega":"Omega_0"},
    "Lee-Yang\n(proved)":{"D":"D_line",  "T":"T_bowtie", "R":"R_exact",     "P":"P_psi",    "F":"F_ell",  "K":"K_mod",  "G":"G_gimel", "Gamma":"G_and",  "Phi":"Phi_c_complex", "H":"H1",  "S":"n_m",   "Omega":"Omega_0"},
    "NS smooth\nsoln":   {"D":"D_cube",  "T":"T_network","R":"R_catalytic",  "P":"P_neutral","F":"F_eth",  "K":"K_mod",  "G":"G_beth",  "Gamma":"G_and",  "Phi":"Phi_sub",       "H":"H0",  "S":"n_m",   "Omega":"Omega_0"},
    "OPN\nconstraint":   {"D":"D_point", "T":"T_linear", "R":"R_exact",     "P":"P_neutral","F":"F_ell",  "K":"K_trap", "G":"G_aleph", "Gamma":"G_and",  "Phi":"Phi_c",         "H":"H0",  "S":"one_n", "Omega":"Omega_0"},
    # ── Field-theory synthons (Synthon.lean) ──────────────────────────────
    "Higgs / axion\n/ inflaton":{"D":"D_point","T":"T_bowtie","R":"R_catalytic","P":"P_pm_sym","F":"F_hbar","K":"K_slow","G":"G_beth","Gamma":"G_and","Phi":"Phi_c","H":"H1","S":"one_n","Omega":"Omega_0"},
    "Standard\nModel":   {"D":"D_cube",  "T":"T_network","R":"R_allosteric", "P":"P_pm",     "F":"F_eth",  "K":"K_mod",  "G":"G_aleph", "Gamma":"G_and",  "Phi":"Phi_c",         "H":"H2",  "S":"n_m",   "Omega":"Omega_Z"},
    "Quantum\nGravity":  {"D":"D_holo",  "T":"T_holo",   "R":"R_exact",     "P":"P_neutral","F":"F_hbar", "K":"K_trap", "G":"G_aleph", "Gamma":"G_impl", "Phi":"Phi_c",         "H":"H_inf","S":"n_m",  "Omega":"Omega_NA"},
    "General\nRelativity":{"D":"D_cube", "T":"T_network","R":"R_catalytic",  "P":"P_neutral","F":"F_hbar", "K":"K_slow", "G":"G_gimel", "Gamma":"G_and",  "Phi":"Phi_sub",       "H":"H1",  "S":"one_n", "Omega":"Omega_0"},
    "Asymptotic\nSafety":{"D":"D_cube",  "T":"T_network","R":"R_catalytic",  "P":"P_neutral","F":"F_hbar", "K":"K_mod",  "G":"G_aleph", "Gamma":"G_and",  "Phi":"Phi_c",         "H":"H1",  "S":"one_n", "Omega":"Omega_0"},
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
        KEY_SYNTHONS[label] = catalog_by_name[name]

# Assign a marker type
MILLENNIUM = {"YM classical", "YM quantum\n(target)", "RH (ζ zeros)",
              "Lee-Yang\n(proved)", "NS smooth\nsoln", "OPN\nconstraint"}
FIELD_THEORY = {"Higgs / axion\n/ inflaton", "Standard\nModel", "Quantum\nGravity",
                "General\nRelativity", "Asymptotic\nSafety"}

# ── Compute key-node pairwise distances & spring layout ───────────────────────
key_names = list(KEY_SYNTHONS.keys())
key_entries = [KEY_SYNTHONS[k] for k in key_names]
k = len(key_names)

key_dist = np.zeros((k, k), dtype=float)
for i in range(k):
    for j in range(k):
        key_dist[i, j] = hamming(key_entries[i], key_entries[j])

# NetworkX graph for spring layout
G = nx.Graph()
for i, name in enumerate(key_names):
    G.add_node(i, label=name, phi=key_entries[i].get("Phi", "Phi_sub"))
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
    phi = entry.get("Phi", "Phi_sub")
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
    for p in ["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"]
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
    phi = entry.get("Phi", "Phi_sub")
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
    for p in ["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"]
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
           markersize=8,  linestyle='None', label="Field-theory synthon (Lean)"),
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
