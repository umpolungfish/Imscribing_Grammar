#!/usr/bin/env python3
"""
ig_figures.py — Programmatic figure generation for IG publications.

All figures output with transparent backgrounds, dark text — suitable for
inclusion in white-background PDF documents.

CLI:
  python3 ig_figures.py belnap [--labels "N:empty,T:spinUp,F:spinDown,B:paired"]
                                [--highlight B] [--caption "..."] [--out fig.pdf]

  python3 ig_figures.py profile --tuple "𐑦 𐑸 𐑾 𐑹 ⋈^ż ⊤^@ 𐑲 ∋^ˌ ⊙ 𐑖 𐑳 𐑭"
                                 [--title "..."] [--out fig.pdf]

  python3 ig_figures.py tier [--highlight O_∞] [--out fig.pdf]

  python3 ig_figures.py frobenius [--out fig.pdf]
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

# ── Style constants ────────────────────────────────────────────────────────────

# Text on transparent/white backgrounds — dark navy
TEXT   = "#1A1A2E"
# Text on dark/coloured node backgrounds — near-white
FG     = "#E8E8F0"
ACCENT = "#9370DB"   # medium purple — O_∞ colour

TIER_COLOR = {
    "O₀":   "#4472C4",
    "O₁":   "#FFD700",
    "O₂":   "#FF8C00",
    "O₂†":  "#DC143C",
    "O_∞":   "#9370DB",
}

PRIM_GLYPHS = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]
PRIM_NAMES  = [
    "Dimensionality", "Topology", "Recognition", "Parity",
    "Fidelity",       "Kinetics", "Granularity", "Coupling",
    "Criticality",    "Chirality","Stoichiometry","Winding",
]

SUBTYPE_ORDER = {
    "⊢": ["ß","C",";","ω"],
    "⊣": ["6","K","ò","¨","O"],
    ">": ["¯","ý","Ť","="],
    "<": ["ɐ","υ","F","˙","}"],
    "⋈": ["ì","ð","ż"],
    "⊤": ["-","W","@","Ù","λ"],
    "∈": ["β","γ","ʔ"],
    "∋": ["∧","˝","ˌ","Ş"],
    "⊙": ["ž","ÿ","Æ","3","Ţ"],
    "⊥": ["Ñ","£","A","!"],
    "⊞": ["S","ő","ï"],
    "◻": ["Å","2","z","5"],
}


def _fig_setup(w=7, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    for spine in ax.spines.values():
        spine.set_edgecolor("#AAAACC")
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    return fig, ax


def _save(fig, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), dpi=150, bbox_inches="tight",
                facecolor="none", edgecolor="none", transparent=True)
    plt.close(fig)
    return path


# ── Figure 1: Belnap Lattice ───────────────────────────────────────────────────

def belnap_lattice(
    labels: dict | None = None,
    highlight: str | None = None,
    caption: str = "",
    output: str = "fig_belnap.pdf",
) -> Path:
    """
    Hasse diagram of Belnap FOUR.

    labels: dict mapping B4 values to display strings, e.g.
            {"N": "empty", "T": "spinUp", "F": "spinDown", "B": "paired"}
    highlight: one of "N","T","F","B" — drawn in accent colour
    """
    labels = labels or {"N": "N", "T": "T", "F": "F", "B": "B"}

    pos   = {"N": (0.5, 0.0), "T": (1.0, 0.5), "F": (0.0, 0.5), "B": (0.5, 1.0)}
    edges = [("N", "T"), ("N", "F"), ("T", "B"), ("F", "B")]

    b4_colors = {
        "N": "#4472C4",
        "T": "#70B070",
        "F": "#C07070",
        "B": ACCENT,
    }

    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    # extra horizontal room so F-node (x=0) and T-node (x=1) labels don't clip
    ax.set_xlim(-0.55, 1.55)
    ax.set_ylim(-0.30, 1.30)
    ax.axis("off")

    for a, b in edges:
        x0, y0 = pos[a]
        x1, y1 = pos[b]
        ax.plot([x0, x1], [y0, y1], color="#AAAACC", lw=2, zorder=1)

    for key, (x, y) in pos.items():
        col = b4_colors.get(key, ACCENT)
        if key == highlight:
            col = "#FF9900"
            outer = plt.Circle((x, y), 0.065, color="#FF9900", zorder=2, alpha=0.35)
            ax.add_patch(outer)

        circle = plt.Circle((x, y), 0.055, color=col, zorder=3)
        ax.add_patch(circle)

        # B4 value label inside circle (white on colour)
        ax.text(x, y, key, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", zorder=4)

        # secondary label outside circle
        display = labels.get(key, key)
        if display != key:
            # place label away from edge towards centre
            off_x = 0.20 if x < 0.5 else (-0.20 if x > 0.5 else 0)
            off_y = 0.0
            if x == 0.5:
                off_y = -0.14 if y == 0.0 else 0.14
            ax.text(x + off_x, y + off_y, display,
                    ha="center", va="center",
                    fontsize=8.5, color=TEXT, zorder=4,
                    fontstyle="italic")

    # axis order annotations
    ax.text(-0.48, 0.5, "information\norder ⊑",
            ha="center", va="center", fontsize=7.5, color="#888899",
            rotation=90)
    ax.text(0.5, -0.26, "truth order →",
            ha="center", va="center", fontsize=7.5, color="#888899")

    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="bottom",
                 fontsize=8, color=TEXT, style="italic")

    return _save(fig, output)


# ── Figure 2: Primitive Profile ────────────────────────────────────────────────

def primitive_profile(
    tuple_str: str,
    title: str = "",
    output: str = "fig_profile.pdf",
) -> Path:
    """
    Horizontal bar chart showing ordinal level of each primitive in a tuple.

    tuple_str: space/semicolon-separated entries like "𐑦 𐑸 𐑾 ..."
               Both ^ and _ separators accepted.
    """
    entries = [e.strip().strip("⟨⟩") for e in tuple_str.replace(";", " ").split()]
    entries = [e for e in entries if e]

    prim_vals = {}
    for entry in entries:
        for sep in ("_", "^"):
            if sep in entry:
                prim, sub = entry.split(sep, 1)
                prim = prim.strip()
                sub  = sub.strip()
                if prim in SUBTYPE_ORDER:
                    order = SUBTYPE_ORDER[prim]
                    level = order.index(sub) + 1 if sub in order else 1
                    prim_vals[prim] = (sub, level, len(order))
                break

    bar_data = []
    for g in PRIM_GLYPHS:
        if g in prim_vals:
            sub, level, max_level = prim_vals[g]
            bar_data.append((g, sub, level, max_level))
        else:
            bar_data.append((g, "?", 0, 1))

    fig, ax = _fig_setup(w=7, h=4.5)

    ys     = list(range(len(bar_data)))
    ylabels = [f"{g} ({sub})" for g, sub, _, _ in bar_data]
    levels = [level for _, _, level, _ in bar_data]
    maxes  = [m for _, _, _, m in bar_data]

    # background (max extent) bars
    ax.barh(ys, maxes, color="#E8E8F4", height=0.6, zorder=1)

    # foreground (actual level) bars
    colors = [ACCENT if lv == mx else "#7788CC"
              for lv, mx in zip(levels, maxes)]
    ax.barh(ys, levels, color=colors, height=0.6, zorder=2)

    # level/max annotations
    for i, (lv, mx) in enumerate(zip(levels, maxes)):
        ax.text(mx + 0.08, i, f"{lv}/{mx}",
                va="center", ha="left", fontsize=8, color="#666688")

    ax.set_yticks(ys)
    ax.set_yticklabels(ylabels, fontsize=10)
    ax.set_xlabel("Ordinal level", fontsize=9)
    ax.set_xlim(0, max(maxes) + 1.2)
    ax.invert_yaxis()
    ax.grid(axis="x", color="#CCCCDD", alpha=0.7, linewidth=0.5)

    if title:
        ax.set_title(title, color=TEXT, fontsize=11, pad=8)

    patch_max = mpatches.Patch(color=ACCENT, label="at maximum")
    patch_mid = mpatches.Patch(color="#7788CC", label="below maximum")
    ax.legend(handles=[patch_max, patch_mid], fontsize=8,
              facecolor="white", edgecolor="#AAAACC", labelcolor=TEXT,
              loc="lower right")

    return _save(fig, output)


# ── Figure 3: Tier Chain ───────────────────────────────────────────────────────

def tier_chain(
    highlight: str | None = "O_∞",
    output: str = "fig_tier.pdf",
) -> Path:
    """
    Horizontal tier hierarchy: O₀ → O₁ → O₂ → O₂† → O_∞
    """
    tiers = ["O₀", "O₁", "O₂", "O₂†", "O_∞"]
    tier_labels = {
        "O₀":  "inert",
        "O₁":  "unprotected\ncritical",
        "O₂":  "protected\nbounded",
        "O₂†": "protected\nunbounded",
        "O_∞":  "Frobenius\ncomplete",
    }

    fig, ax = plt.subplots(figsize=(9, 2.8))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.axis("off")

    n  = len(tiers)
    xs = np.linspace(0.1, 0.9, n)
    y  = 0.62

    for i in range(n - 1):
        ax.annotate("", xy=(xs[i+1] - 0.05, y), xytext=(xs[i] + 0.05, y),
                    arrowprops=dict(arrowstyle="->", color="#888899", lw=2))

    for i, tier in enumerate(tiers):
        col  = TIER_COLOR.get(tier, ACCENT)
        ring = tier == highlight
        r    = 0.052

        if ring:
            outer = plt.Circle((xs[i], y), r * 1.45,
                                color=col, alpha=0.22,
                                transform=ax.transData, zorder=2)
            ax.add_patch(outer)

        circle = plt.Circle((xs[i], y), r,
                             color=col, zorder=3,
                             transform=ax.transData)
        ax.add_patch(circle)

        ax.text(xs[i], y, tier,
                ha="center", va="center",
                fontsize=7.5, fontweight="bold",
                color="white", zorder=4)

        sub = tier_labels.get(tier, "")
        ax.text(xs[i], y - 0.24, sub,
                ha="center", va="top",
                fontsize=7.5, color=TEXT, alpha=0.85)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return _save(fig, output)


# ── Figure 4: Frobenius Triangle ───────────────────────────────────────────────

def frobenius_triangle(output: str = "fig_frobenius.pdf") -> Path:
    """
    μ∘δ=id diamond: A (top) → A⊗A (sides) → A (bottom), plus direct id arrow.
    """
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.axis("off")
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.18, 1.1)

    top   = (0.5, 0.88)
    left  = (0.12, 0.50)
    right = (0.88, 0.50)
    mid   = (0.5,  0.12)

    def arrow(src, dst, label="", side="left"):
        ax.annotate("", xy=dst, xytext=src,
                    arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2.0))
        mx, my = (src[0]+dst[0])/2, (src[1]+dst[1])/2
        off = (-0.13, 0) if side == "left" else (0.13, 0)
        if label:
            ax.text(mx + off[0], my + off[1], label,
                    ha="center", va="center", fontsize=12,
                    color=TEXT, fontweight="bold")

    arrow(top,  left,  "δ",  "left")
    arrow(left, mid,   "",   "left")
    arrow(top,  right, "",   "right")
    arrow(right, mid,  "μ",  "right")

    # dashed identity: A (top) → A (bottom)
    ax.annotate("", xy=(mid[0], mid[1] + 0.06), xytext=(top[0], top[1] - 0.06),
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2.0,
                                linestyle="dashed"))
    ax.text(0.66, 0.50, "id", ha="center", va="center",
            fontsize=12, color=ACCENT, fontweight="bold")

    # node labels — all four nodes now present
    node_style = dict(boxstyle="round,pad=0.25", fc="white", ec=ACCENT, lw=1.5)
    for (x, y), lbl in [(top, "A"), (left, "A⊗A"), (right, "A⊗A"), (mid, "A")]:
        ax.text(x, y, lbl, ha="center", va="center",
                fontsize=11, color=TEXT, fontweight="bold",
                bbox=node_style, zorder=5)

    ax.text(0.5, -0.13, "μ∘δ = id", ha="center", va="center",
            fontsize=13, color=ACCENT, fontweight="bold")

    return _save(fig, output)


# ── Figure 5: IMASM Bootstrap Loop ────────────────────────────────────────────

def bootstrap_loop(output: str = "fig_bootstrap.pdf") -> Path:
    """
    Circular diagram of the 8-instruction IMASM bootstrap loop.
    """
    import math

    NODES = [
        ("ISCRIB", "identity",   "#FFAA00"),   # warm amber instead of yellow
        ("AREV",   "direction",  "#5599CC"),
        ("FSPLIT", "frobenius",  ACCENT),
        ("AFWD",   "direction",  "#5599CC"),
        ("FFUSE",  "frobenius",  ACCENT),
        ("CLINK",  "identity",   "#FFAA00"),
        ("IFIX",   "fixation",   "#CC2233"),
    ]
    N   = len(NODES)
    R   = 0.33
    cx, cy = 0.50, 0.50

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    angles = [math.pi/2 - 2*math.pi*i/N for i in range(N)]
    pos    = [(cx + R*math.cos(a), cy + R*math.sin(a)) for a in angles]

    for i in range(N):
        x0, y0 = pos[i]
        x1, y1 = pos[(i+1) % N]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle="->", color="#888899", lw=1.8,
                        connectionstyle="arc3,rad=0.15",
                    ))

    node_r = 0.050
    for i, (name, role, col) in enumerate(NODES):
        x, y = pos[i]
        circle = plt.Circle((x, y), node_r, color=col, zorder=3)
        ax.add_patch(circle)
        # label outside circle, pushed slightly further out to avoid overlap
        lx = cx + (R + 0.100)*math.cos(angles[i])
        ly = cy + (R + 0.100)*math.sin(angles[i])
        ax.text(lx, ly, name, ha="center", va="center",
                fontsize=9, fontweight="bold", color=TEXT, zorder=4)

    # central label
    ax.text(cx, cy + 0.04, "μ∘δ = id", ha="center", va="center",
            fontsize=12, color=ACCENT, fontweight="bold")
    ax.text(cx, cy - 0.04, "bootstrap", ha="center", va="center",
            fontsize=8.5, color="#888899")

    # VINIT / TANCH boundary note — bottom centre
    ax.text(0.50, 0.06, "VINIT  ·  TANCH",
            ha="center", va="center", fontsize=9, color="#666677",
            style="italic")
    ax.text(0.50, 0.02, "(boundary conditions — not part of loop proper)",
            ha="center", va="center", fontsize=7.5, color="#999999")

    # legend — bottom right to avoid circle overlap
    legend_items = [
        ("#FFAA00", "identity  (ISCRIB, CLINK)"),
        (ACCENT,    "Frobenius  (FSPLIT δ, FFUSE μ)"),
        ("#5599CC", "direction  (AFWD, AREV)"),
        ("#CC2233", "fixation  (IFIX)"),
    ]
    for j, (col, lbl) in enumerate(legend_items):
        bx = 0.60
        by = 0.20 - j*0.055
        ax.add_patch(plt.Circle((bx, by), 0.012, color=col, zorder=3))
        ax.text(bx + 0.028, by, lbl, va="center", fontsize=8, color=TEXT)

    return _save(fig, output)


# ── Figure 6: Cetacean Structural Space ────────────────────────────────────────

def cetacean_scatter(output: str = "fig_cetacean.pdf") -> Path:
    """
    Scatter plot of cetacean call types in (distance, paradox density) space.
    """
    calls = [
        ("Humpback\nsong",        5.10, 0.00, 4, "humpback"),
        ("Orca\nsocial bonding",  0.57, 0.15, 3, "orca"),
        ("Orca\ncoordination",    0.38, 0.30, 1, "orca"),
        ("Orca\ncross-pod",       1.01, 0.06, 3, "orca"),
        ("Orca\necholocation",    0.00, 0.00, 0, "orca"),
        ("Sperm whale\ncoda",     0.95, 0.08, 2, "sperm"),
    ]
    species_color = {
        "humpback": "#CC8800",
        "orca":     "#7755BB",
        "sperm":    "#448866",
    }

    fig, ax = _fig_setup(w=7, h=5.5)

    for label, dist, paradox, fixed, sp in calls:
        col  = species_color[sp]
        size = 120 + fixed * 80
        ax.scatter(dist, paradox, s=size, c=col, zorder=3,
                   edgecolors="#AAAACC", linewidths=0.8)
        off_x = 0.08 if dist < 4 else -0.15
        off_y = 0.015 if paradox < 0.25 else -0.025
        ax.text(dist + off_x, paradox + off_y, label,
                fontsize=8, color=TEXT, va="center")

    ax.axhline(0.33, color="#CC3333", lw=1.5, linestyle="--", alpha=0.7, zorder=2)
    ax.text(4.5, 0.345, "alarm threshold (0.33)",
            fontsize=8, color="#CC3333", va="bottom")

    ax.set_xlabel("Distance to closest human expression", fontsize=10)
    ax.set_ylabel("Paradox density", fontsize=10)
    ax.set_title("Cetacean call types in structural space", color=TEXT, fontsize=11)
    ax.set_xlim(-0.3, 6.0)
    ax.set_ylim(-0.03, 0.42)
    ax.grid(color="#DDDDEE", alpha=0.7, linewidth=0.5)

    for sp, col in species_color.items():
        ax.scatter([], [], c=col, s=100,
                   edgecolors="#AAAACC", linewidths=0.8, label=sp.capitalize())
    ax.legend(fontsize=9, facecolor="white", edgecolor="#AAAACC",
              labelcolor=TEXT, loc="upper right")

    ax.text(0.02, 0.97, "Point size ∝ fixed register count",
            transform=ax.transAxes, fontsize=7.5, color="#888899", va="top")

    return _save(fig, output)


# ── Figure 7: Psychedelic Access Heatmap ──────────────────────────────────────

def psychedelic_heatmap(output: str = "fig_psychedelic_heatmap.pdf") -> Path:
    """
    Compounds × universes access matrix as a heatmap.
    """
    compounds = [
        "5-MeO-DMT", "DMT", "Ayahuasca", "LSD", "Ibogaine",
        "Psilocybin", "Mescaline", "Salvinorin A", "Ketamine", "MDMA", "Cannabis"
    ]
    universes = [
        "chirality_first", "critical_first", "winding_first",
        "chirality_tight", "critical_tight", "winding_tight",
        "parity_hard", "chirality_mod", "protection_weak",
        "psi_parity", "dual_gate", "slow_only",
        "memory_free", "binary_only", "quantum_only",
        "one_gate", "null_universe",
    ]
    # fmt: off
    data = [
        [1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,0,0,0,0,0,0],
        [1,1,1,1,1,0,0,0,0,0,0],
        [1,1,1,1,1,0,0,0,0,0,0],
        [1,1,1,1,0,1,0,1,1,1,0],
        [1,1,1,1,1,1,1,1,0,1,0],
        [1,1,1,1,1,1,1,1,1,0,0],
        [1,1,1,1,1,1,1,0,0,0,0],
        [1,1,1,1,1,1,1,0,0,0,0],
        [1,1,1,1,1,1,1,0,0,0,0],
        [1,1,1,1,1,1,1,0,0,0,0],
        [1,1,1,1,1,1,1,0,1,0,0],
        [1,1,1,1,1,1,1,1,0,1,0],
        [1,1,1,1,1,1,0,0,0,0,0],
        [1,1,1,1,1,0,0,0,0,0,0],
    ]
    # fmt: on

    matrix = np.array(data, dtype=float)

    tier_colors = {
        "5-MeO-DMT": ACCENT, "DMT": ACCENT, "Ayahuasca": ACCENT,
        "LSD": ACCENT, "Ibogaine": ACCENT,
        "Psilocybin": "#DC143C",
        "Mescaline": "#FF8C00",
        "Salvinorin A": "#CC9900", "Ketamine": "#CC9900",
        "MDMA": "#CC9900",
        "Cannabis": "#4472C4",
    }

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "access", ["#E8E8F4", "#2D6A4F"]
    )
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1,
              interpolation="nearest")

    for x in range(len(compounds) + 1):
        ax.axvline(x - 0.5, color="#CCCCDD", lw=0.5)
    for y in range(len(universes) + 1):
        ax.axhline(y - 0.5, color="#CCCCDD", lw=0.5)

    col_sums = matrix.sum(axis=0)
    ax.set_xticks(range(len(compounds)))
    ax.set_xticklabels(
        [f"{c}\n({int(col_sums[i])})" for i, c in enumerate(compounds)],
        fontsize=7.5, color=TEXT, rotation=35, ha="right"
    )
    for i, lbl in enumerate(ax.get_xticklabels()):
        lbl.set_color(tier_colors.get(compounds[i], TEXT))

    ax.set_yticks(range(len(universes)))
    ax.set_yticklabels(universes, fontsize=8, color=TEXT)

    row_sums = matrix.sum(axis=1)
    for j, s in enumerate(row_sums):
        ax.text(len(compounds) + 0.1, j, f"{int(s)}",
                va="center", fontsize=7.5, color="#888899")

    ax.set_title("Universe access by compound and ruleset",
                 color=TEXT, fontsize=11, pad=10)
    ax.set_xlim(-0.5, len(compounds) - 0.5 + 1.2)

    tier_items = [
        (ACCENT,     "O_∞  (5-MeO-DMT, DMT, Aya, LSD, Ibogaine)"),
        ("#DC143C",  "O₂†  (Psilocybin)"),
        ("#FF8C00",  "O₂   (Mescaline)"),
        ("#CC9900",  "O₁   (Salvinorin A, Ketamine, MDMA)"),
        ("#4472C4",  "O₀   (Cannabis)"),
    ]
    for j, (col, lbl) in enumerate(tier_items):
        ax.add_patch(plt.Rectangle((-0.5 + j*2.1 - 0.2,
                                    len(universes) + 0.3), 0.3, 0.5,
                                   color=col, transform=ax.transData,
                                   clip_on=False))
        ax.text(-0.5 + j*2.1 + 0.2, len(universes) + 0.55, lbl,
                fontsize=6.5, color=TEXT, transform=ax.transData,
                va="center", clip_on=False)

    fig.tight_layout()
    return _save(fig, output)


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_labels(s: str) -> dict:
    result = {}
    for part in s.split(","):
        part = part.strip()
        if ":" in part:
            k, v = part.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def main():
    p = argparse.ArgumentParser(
        description="Generate IG publication figures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 ig_figures.py belnap --labels "N:empty,T:spinUp,F:spinDown,B:paired"
  python3 ig_figures.py profile --tuple "𐑦 𐑸 𐑾 𐑹 ⋈^ż ⊤^@ 𐑲 ∋^ˌ ⊙ 𐑖 𐑳 𐑭"
  python3 ig_figures.py tier --highlight O_∞
  python3 ig_figures.py frobenius
""",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("belnap",    help="Belnap FOUR Hasse diagram")
    pb.add_argument("--labels",    default="", help="N:lbl,T:lbl,F:lbl,B:lbl")
    pb.add_argument("--highlight", default="", help="N|T|F|B")
    pb.add_argument("--caption",   default="")
    pb.add_argument("--out",       default="fig_belnap.pdf")

    pp = sub.add_parser("profile",   help="12-primitive profile bar chart")
    pp.add_argument("--tuple", required=True)
    pp.add_argument("--title", default="")
    pp.add_argument("--out",   default="fig_profile.pdf")

    pt = sub.add_parser("tier",      help="Tier hierarchy chain")
    pt.add_argument("--highlight", default="O_∞")
    pt.add_argument("--out",       default="fig_tier.pdf")

    pf = sub.add_parser("frobenius", help="μ∘δ=id triangle")
    pf.add_argument("--out", default="fig_frobenius.pdf")

    pb2 = sub.add_parser("bootstrap", help="IMASM 8-instruction bootstrap loop")
    pb2.add_argument("--out", default="fig_bootstrap.pdf")

    pc = sub.add_parser("cetacean",   help="Cetacean structural space scatter")
    pc.add_argument("--out", default="fig_cetacean.pdf")

    ph = sub.add_parser("psychedelic", help="Compound × universe access heatmap")
    ph.add_argument("--out", default="fig_psychedelic_heatmap.pdf")

    args = p.parse_args()

    if args.cmd == "belnap":
        labels = _parse_labels(args.labels) if args.labels else None
        out = belnap_lattice(labels=labels, highlight=args.highlight or None,
                             caption=args.caption, output=args.out)
    elif args.cmd == "profile":
        out = primitive_profile(tuple_str=args.tuple, title=args.title, output=args.out)
    elif args.cmd == "tier":
        out = tier_chain(highlight=args.highlight or None, output=args.out)
    elif args.cmd == "frobenius":
        out = frobenius_triangle(output=args.out)
    elif args.cmd == "bootstrap":
        out = bootstrap_loop(output=args.out)
    elif args.cmd == "cetacean":
        out = cetacean_scatter(output=args.out)
    elif args.cmd == "psychedelic":
        out = psychedelic_heatmap(output=args.out)
    else:
        p.print_help()
        sys.exit(1)

    print(f"  written → {out}")


if __name__ == "__main__":
    main()
