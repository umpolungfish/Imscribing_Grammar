#!/usr/bin/env python3
"""
ig_figures.py — Programmatic figure generation for IG publications.

Generates publication-ready PDF figures for the three recurring figure types
that appear in most IG papers.  All figures match the crystal_viz.py dark style.

CLI:
  python3 ig_figures.py belnap [--labels "N:empty,T:spinUp,F:spinDown,B:paired"]
                                [--highlight B] [--caption "..."] [--out fig.pdf]

  python3 ig_figures.py profile --tuple "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z"
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

# ── Style constants (matching crystal_viz.py) ──────────────────────────────────

BG      = "#0F0F1A"
BG2     = "#1A1A2E"
FG      = "#E8E8F0"
ACCENT  = "#9370DB"   # medium purple — O_∞ colour

TIER_COLOR = {
    "O_0":   "#4472C4",
    "O_1":   "#FFD700",
    "O_2":   "#FF8C00",
    "O_2†":  "#DC143C",
    "O_∞":   "#9370DB",
}

PRIM_GLYPHS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
PRIM_NAMES  = [
    "Dimensionality", "Topology", "Recognition", "Parity",
    "Fidelity",       "Kinetics", "Granularity", "Coupling",
    "Criticality",    "Chirality","Stoichiometry","Winding",
]

# Subtype ordinal order per primitive (0-indexed, ascending complexity)
SUBTYPE_ORDER = {
    "Ð": ["ß","C",";","ω"],
    "Þ": ["6","K","ò","¨","O"],
    "Ř": ["¯","ý","Ť","="],
    "Φ": ["ɐ","υ","F","˙","}"],
    "ƒ": ["ì","ð","ż"],
    "Ç": ["-","W","@","Ù","λ"],
    "Γ": ["β","γ","ʔ"],
    "ɢ": ["∧","˝","ˌ","Ş"],
    "⊙": ["ž","ÿ","Æ","3","Ţ"],
    "Ħ": ["Ñ","£","A","!"],
    "Σ": ["S","ő","ï"],
    "Ω": ["Å","2","z","5"],
}


def _fig_setup(w=7, h=5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG2)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    return fig, ax


def _save(fig, output):
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(path), dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
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

    # Node positions
    pos = {"N": (0.5, 0.0), "T": (1.0, 0.5), "F": (0.0, 0.5), "B": (0.5, 1.0)}
    edges = [("N", "T"), ("N", "F"), ("T", "B"), ("F", "B")]

    b4_colors = {
        "N": "#4472C4",
        "T": "#70B070",
        "F": "#C07070",
        "B": ACCENT,
    }

    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-0.25, 1.25)
    ax.axis("off")

    # Draw edges
    for a, b in edges:
        x0, y0 = pos[a]
        x1, y1 = pos[b]
        ax.plot([x0, x1], [y0, y1], color="#555577", lw=2, zorder=1)

    # Draw nodes and labels
    for key, (x, y) in pos.items():
        col = b4_colors.get(key, FG)
        if key == highlight:
            col = "#FFDD44"
            ring_r = 0.065
            circle_outer = plt.Circle((x, y), ring_r,
                                       color="#FFDD44", zorder=2, alpha=0.35)
            ax.add_patch(circle_outer)

        circle = plt.Circle((x, y), 0.055, color=col, zorder=3)
        ax.add_patch(circle)

        # Primary label (B4 value)
        ax.text(x, y, key, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", zorder=4)

        # Secondary label (user-supplied name)
        display = labels.get(key, key)
        if display != key:
            offset_x = -0.18 if x < 0.5 else (0.18 if x > 0.5 else 0)
            offset_y = -0.10 if y < 0.5 else 0.10
            if x == 0.5:
                offset_y = -0.12 if y == 0.0 else 0.12
            ax.text(x + offset_x, y + offset_y, display,
                    ha="center", va="center",
                    fontsize=8.5, color=FG, zorder=4,
                    fontstyle="italic")

    # Axis labels
    ax.text(-0.25, 0.5, "information\norder ⊑",
            ha="center", va="center", fontsize=7.5, color="#888899",
            rotation=90)
    ax.text(0.5, -0.20, "truth order →",
            ha="center", va="center", fontsize=7.5, color="#888899")

    if caption:
        fig.text(0.5, 0.01, caption, ha="center", va="bottom",
                 fontsize=8, color=FG, style="italic")

    return _save(fig, output)


# ── Figure 2: Primitive Profile ────────────────────────────────────────────────

def primitive_profile(
    tuple_str: str,
    title: str = "",
    output: str = "fig_profile.pdf",
) -> Path:
    """
    Horizontal bar chart showing ordinal level of each primitive in a structural tuple.

    tuple_str: space/semicolon-separated entries like "Ð_ω Þ_O Ř_= ..."
               Separators ^ and _ are both accepted.
    """
    # Parse tuple
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

    # Build display order (canonical PRIM_GLYPHS order)
    bar_data = []
    for g in PRIM_GLYPHS:
        if g in prim_vals:
            sub, level, max_level = prim_vals[g]
            bar_data.append((g, sub, level, max_level))
        else:
            bar_data.append((g, "?", 0, 1))

    fig, ax = _fig_setup(w=7, h=4.5)

    ys     = list(range(len(bar_data)))
    labels = [f"{g} ({sub})" for g, sub, _, _ in bar_data]
    levels = [level for _, _, level, _ in bar_data]
    maxes  = [m for _, _, _, m in bar_data]

    # Fraction bars (background)
    ax.barh(ys, maxes, color="#222244", height=0.6, zorder=1)

    # Level bars (foreground)
    colors = [ACCENT if lv == mx else "#5566AA"
              for lv, mx in zip(levels, maxes)]
    bars = ax.barh(ys, levels, color=colors, height=0.6, zorder=2)

    # Max-level annotation
    for i, (lv, mx) in enumerate(zip(levels, maxes)):
        ax.text(mx + 0.05, i, f"{lv}/{mx}",
                va="center", ha="left", fontsize=8, color="#9999BB")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=10, color=FG)
    ax.set_xlabel("Ordinal level", color=FG, fontsize=9)
    ax.set_xlim(0, max(maxes) + 1.2)
    ax.invert_yaxis()
    ax.grid(axis="x", color="#333355", alpha=0.5, linewidth=0.5)

    if title:
        ax.set_title(title, color=FG, fontsize=11, pad=8)

    # Legend
    patch_max = mpatches.Patch(color=ACCENT, label="at maximum")
    patch_mid = mpatches.Patch(color="#5566AA", label="below maximum")
    ax.legend(handles=[patch_max, patch_mid], fontsize=8,
              facecolor=BG2, edgecolor="#333355", labelcolor=FG,
              loc="lower right")

    return _save(fig, output)


# ── Figure 3: Tier Chain ───────────────────────────────────────────────────────

def tier_chain(
    highlight: str | None = "O_∞",
    output: str = "fig_tier.pdf",
) -> Path:
    """
    Horizontal tier hierarchy: O_0 → O_1 → O_2 → O_2† → O_∞
    Optional highlight of one tier.
    """
    tiers = ["O_0", "O_1", "O_2", "O_2†", "O_∞"]
    tier_labels = {
        "O_0":  "inert",
        "O_1":  "unprotected\ncritical",
        "O_2":  "protected\nbounded",
        "O_2†": "protected\nunbounded",
        "O_∞":  "Frobenius\ncomplete",
    }

    fig, ax = plt.subplots(figsize=(9, 2.8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")

    n = len(tiers)
    xs = np.linspace(0.1, 0.9, n)
    y  = 0.55

    # Arrows between tiers
    for i in range(n - 1):
        ax.annotate("", xy=(xs[i+1] - 0.05, y), xytext=(xs[i] + 0.05, y),
                    arrowprops=dict(arrowstyle="->", color="#555577", lw=2))

    # Tier nodes
    for i, tier in enumerate(tiers):
        col  = TIER_COLOR.get(tier, FG)
        ring = tier == highlight
        r    = 0.052

        if ring:
            outer = plt.Circle((xs[i], y), r * 1.45,
                                color=col, alpha=0.25,
                                transform=ax.transData, zorder=2)
            ax.add_patch(outer)

        circle = plt.Circle((xs[i], y), r,
                             color=col, zorder=3,
                             transform=ax.transData)
        ax.add_patch(circle)

        ax.text(xs[i], y, tier.replace("O_", "O₀")[0]
                if False else tier,
                ha="center", va="center",
                fontsize=8.5, fontweight="bold",
                color="white", zorder=4)

        # Sub-label
        sub = tier_labels.get(tier, "")
        ax.text(xs[i], y - 0.22, sub,
                ha="center", va="top",
                fontsize=7.5, color=FG, alpha=0.85)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    return _save(fig, output)


# ── Figure 4: Frobenius Triangle ───────────────────────────────────────────────

def frobenius_triangle(output: str = "fig_frobenius.pdf") -> Path:
    """
    μ∘δ=id triangle: A → A⊗A → A with labels.
    """
    fig, ax = plt.subplots(figsize=(4, 3.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.15, 1.1)

    nodes = {"A_top": (0.5, 0.9), "AA": (0.5, 0.1), "A_bot": (0.5, 0.9)}
    left  = (0.1, 0.5)
    right = (0.9, 0.5)
    top   = (0.5, 0.9)
    mid   = (0.5, 0.1)

    def arrow(src, dst, label="", side="left"):
        ax.annotate("", xy=dst, xytext=src,
                    arrowprops=dict(arrowstyle="->", color=ACCENT, lw=2))
        mx, my = (src[0]+dst[0])/2, (src[1]+dst[1])/2
        off = (-0.12, 0) if side == "left" else (0.12, 0)
        ax.text(mx + off[0], my + off[1], label,
                ha="center", va="center", fontsize=11,
                color=FG, fontweight="bold")

    # A at top; A⊗A at bottom; identity arrow along the side
    arrow(top,  left,  "δ",   "left")
    arrow(left, mid,   "",    "left")
    arrow(top,  right, "",    "right")
    arrow(right, mid,  "μ",   "right")

    # Straight identity
    ax.annotate("", xy=(0.5, 0.12), xytext=(0.5, 0.88),
                arrowprops=dict(arrowstyle="->", color="#FFDD44", lw=2,
                                linestyle="dashed"))
    ax.text(0.62, 0.5, "id", ha="center", va="center",
            fontsize=12, color="#FFDD44", fontweight="bold")

    # Node labels
    for (x, y), lbl in [(top, "A"), (left, "A⊗A"), (right, "A⊗A")]:
        ax.text(x, y, lbl, ha="center", va="center",
                fontsize=11, color=FG, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc=BG2, ec=ACCENT, lw=1))

    ax.text(0.5, -0.10, "μ∘δ = id", ha="center", va="center",
            fontsize=13, color=ACCENT, fontweight="bold")

    return _save(fig, output)


# ── Figure 5: IMASM Bootstrap Loop ────────────────────────────────────────────

def bootstrap_loop(output: str = "fig_bootstrap.pdf") -> Path:
    """
    Circular diagram of the 8-instruction IMASM bootstrap loop.
    Nodes colour-coded by role: identity, Frobenius, direction, fixation.
    VINIT/TANCH bookends shown as boundary anchors outside the cycle.
    """
    import math

    NODES = [
        ("IMSCRIB", "identity",   "#FFDD44"),
        ("AREV",    "direction",  "#70B0D0"),
        ("FSPLIT",  "frobenius",  ACCENT),
        ("AFWD",    "direction",  "#70B0D0"),
        ("FFUSE",   "frobenius",  ACCENT),
        ("CLINK",   "identity",   "#FFDD44"),
        ("IFIX",    "fixation",   "#DC143C"),
    ]
    N   = len(NODES)
    R   = 0.36
    cx, cy = 0.5, 0.52

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Node positions — start at top, go clockwise
    angles = [math.pi/2 - 2*math.pi*i/N for i in range(N)]
    pos    = [(cx + R*math.cos(a), cy + R*math.sin(a)) for a in angles]

    # Draw arrows between consecutive nodes (curved)
    for i in range(N):
        x0, y0 = pos[i]
        x1, y1 = pos[(i+1) % N]
        # midpoint nudge toward centre for slight curve
        mx = (x0 + x1)/2 + 0.05*(cx - (x0+x1)/2)
        my = (y0 + y1)/2 + 0.05*(cy - (y0+y1)/2)
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle="->", color="#555577", lw=1.8,
                        connectionstyle="arc3,rad=0.15",
                    ))

    # Draw nodes
    node_r = 0.055
    for i, (name, role, col) in enumerate(NODES):
        x, y = pos[i]
        circle = plt.Circle((x, y), node_r, color=col, zorder=3)
        ax.add_patch(circle)
        # label outside the circle
        lx = cx + (R + 0.085)*math.cos(angles[i])
        ly = cy + (R + 0.085)*math.sin(angles[i])
        ax.text(lx, ly, name, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=FG, zorder=4)

    # Central label
    ax.text(cx, cy, "μ∘δ=id", ha="center", va="center",
            fontsize=11, color=ACCENT, fontweight="bold")

    # VINIT / TANCH bookends
    ax.text(0.5, 0.06, "VINIT  ·  TANCH",
            ha="center", va="center", fontsize=9, color="#888899",
            style="italic")
    ax.text(0.5, 0.02, "(boundary conditions — not part of loop proper)",
            ha="center", va="center", fontsize=7.5, color="#666677")

    # Legend
    legend_items = [
        ("#FFDD44", "identity  (IMSCRIB, CLINK)"),
        (ACCENT,    "Frobenius  (FSPLIT δ, FFUSE μ)"),
        ("#70B0D0",  "direction  (AFWD, AREV)"),
        ("#DC143C",  "fixation  (IFIX)"),
    ]
    for j, (col, lbl) in enumerate(legend_items):
        ax.add_patch(plt.Circle((0.08, 0.92 - j*0.05), 0.012,
                                color=col, zorder=3))
        ax.text(0.11, 0.92 - j*0.05, lbl, va="center",
                fontsize=8, color=FG)

    return _save(fig, output)


# ── Figure 6: Cetacean Structural Space ────────────────────────────────────────

def cetacean_scatter(output: str = "fig_cetacean.pdf") -> Path:
    """
    Scatter plot of cetacean call types in (distance, paradox density) space.
    Point size encodes fixed register count.
    """
    # Data from IMASM_MANUSCRIPT §4.3
    calls = [
        # (label, distance, paradox_density, fixed_regs, species)
        ("Humpback\nsong",        5.10, 0.00, 4, "humpback"),
        ("Orca\nsocial bonding",  0.57, 0.15, 3, "orca"),
        ("Orca\ncoordination",    0.38, 0.30, 1, "orca"),
        ("Orca\ncross-pod",       1.01, 0.06, 3, "orca"),
        ("Orca\necholocation",    0.00, 0.00, 0, "orca"),
        ("Sperm whale\ncoda",     0.95, 0.08, 2, "sperm"),
    ]
    species_color = {
        "humpback": "#FFD700",
        "orca":     "#9370DB",
        "sperm":    "#70C0A0",
    }

    fig, ax = _fig_setup(w=7, h=5.5)

    for label, dist, paradox, fixed, sp in calls:
        col  = species_color[sp]
        size = 120 + fixed * 80
        ax.scatter(dist, paradox, s=size, c=col, zorder=3,
                   edgecolors="#333355", linewidths=0.8)
        off_x = 0.08 if dist < 4 else -0.15
        off_y = 0.015 if paradox < 0.25 else -0.025
        ax.text(dist + off_x, paradox + off_y, label,
                fontsize=8, color=FG, va="center")

    # Alarm threshold line
    ax.axhline(0.33, color="#FF4444", lw=1.5, linestyle="--", alpha=0.7, zorder=2)
    ax.text(4.5, 0.345, "alarm threshold (0.33)",
            fontsize=8, color="#FF4444", va="bottom")

    ax.set_xlabel("Distance to closest human expression", color=FG, fontsize=10)
    ax.set_ylabel("Paradox density", color=FG, fontsize=10)
    ax.set_title("Cetacean call types in structural space", color=FG, fontsize=11)
    ax.set_xlim(-0.3, 6.0)
    ax.set_ylim(-0.03, 0.42)
    ax.grid(color="#222244", alpha=0.6, linewidth=0.5)

    # Legend
    for sp, col in species_color.items():
        ax.scatter([], [], c=col, s=100,
                   edgecolors="#333355", linewidths=0.8, label=sp.capitalize())
    ax.legend(fontsize=9, facecolor=BG2, edgecolor="#333355",
              labelcolor=FG, loc="upper right")

    # Size legend note
    ax.text(0.02, 0.97, "Point size ∝ fixed register count",
            transform=ax.transAxes, fontsize=7.5,
            color="#888899", va="top")

    return _save(fig, output)


# ── Figure 7: Psychedelic Access Heatmap ──────────────────────────────────────

def psychedelic_heatmap(output: str = "fig_psychedelic_heatmap.pdf") -> Path:
    """
    Compounds × universes access matrix as a heatmap.
    Green = access granted; dark = access denied.
    Compounds sorted by total access count (descending).
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
    # Access matrix from §3.2 of psychedelic_access_lifted.md
    # Rows = universes, Cols = compounds
    # fmt: off
    data = [
        #5MeO DMT  Aya  LSD  Ibo  Psi  Mesc Salv Keta MDMA Can
        [1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   0],  # chirality_first
        [1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   0],  # critical_first
        [1,   1,   1,   1,   1,   1,   1,   1,   1,   1,   0],  # winding_first
        [1,   1,   1,   1,   1,   0,   0,   0,   0,   0,   0],  # chirality_tight
        [1,   1,   1,   1,   1,   0,   0,   0,   0,   0,   0],  # critical_tight
        [1,   1,   1,   1,   1,   0,   0,   0,   0,   0,   0],  # winding_tight
        [1,   1,   1,   1,   0,   1,   0,   1,   1,   1,   0],  # parity_hard
        [1,   1,   1,   1,   1,   1,   1,   1,   0,   1,   0],  # chirality_mod
        [1,   1,   1,   1,   1,   1,   1,   1,   1,   0,   0],  # protection_weak
        [1,   1,   1,   1,   1,   1,   1,   0,   0,   0,   0],  # psi_parity
        [1,   1,   1,   1,   1,   1,   1,   0,   0,   0,   0],  # dual_gate
        [1,   1,   1,   1,   1,   1,   1,   0,   0,   0,   0],  # slow_only
        [1,   1,   1,   1,   1,   1,   1,   0,   0,   0,   0],  # memory_free
        [1,   1,   1,   1,   1,   1,   1,   0,   1,   0,   0],  # binary_only
        [1,   1,   1,   1,   1,   1,   1,   1,   0,   1,   0],  # quantum_only
        [1,   1,   1,   1,   1,   1,   0,   0,   0,   0,   0],  # one_gate
        [1,   1,   1,   1,   1,   0,   0,   0,   0,   0,   0],  # null_universe
    ]
    # fmt: on

    import numpy as np
    matrix = np.array(data, dtype=float)

    # Tier colour bands on y-axis
    tier_colors = {
        "5-MeO-DMT": ACCENT, "DMT": ACCENT, "Ayahuasca": ACCENT,
        "LSD": ACCENT, "Ibogaine": ACCENT,
        "Psilocybin": "#DC143C",
        "Mescaline": "#FF8C00",
        "Salvinorin A": "#FFD700", "Ketamine": "#FFD700",
        "MDMA": "#FFD700",
        "Cannabis": "#4472C4",
    }

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    cmap = plt.cm.colors.LinearSegmentedColormap.from_list(
        "access", ["#1A1A2E", "#2D6A4F"]
    )
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1,
                   interpolation="nearest")

    # Grid lines
    for x in range(len(compounds) + 1):
        ax.axvline(x - 0.5, color="#333355", lw=0.5)
    for y in range(len(universes) + 1):
        ax.axhline(y - 0.5, color="#333355", lw=0.5)

    # Compound access counts (column sums)
    col_sums = matrix.sum(axis=0)

    ax.set_xticks(range(len(compounds)))
    ax.set_xticklabels(
        [f"{c}\n({int(col_sums[i])})" for i, c in enumerate(compounds)],
        fontsize=7.5, color=FG, rotation=35, ha="right"
    )
    # Colour compound labels by tier
    for i, lbl in enumerate(ax.get_xticklabels()):
        lbl.set_color(tier_colors.get(compounds[i], FG))

    ax.set_yticks(range(len(universes)))
    ax.set_yticklabels(universes, fontsize=8, color=FG)

    # Row sums on right
    row_sums = matrix.sum(axis=1)
    for j, s in enumerate(row_sums):
        ax.text(len(compounds) + 0.1, j, f"{int(s)}",
                va="center", fontsize=7.5, color="#888899")

    ax.set_title("Universe access by compound and ruleset",
                 color=FG, fontsize=11, pad=10)
    ax.set_xlim(-0.5, len(compounds) - 0.5 + 1.2)

    # Tier legend
    tier_items = [
        (ACCENT,     "O_∞  (5-MeO-DMT, DMT, Aya, LSD, Ibogaine)"),
        ("#DC143C",  "O_2†  (Psilocybin)"),
        ("#FF8C00",  "O_2   (Mescaline)"),
        ("#FFD700",  "O_1   (Salvinorin A, Ketamine, MDMA)"),
        ("#4472C4",  "O_0   (Cannabis)"),
    ]
    for j, (col, lbl) in enumerate(tier_items):
        ax.add_patch(plt.Rectangle((-0.5 + j*2.1 - 0.2,
                                    len(universes) + 0.3), 0.3, 0.5,
                                   color=col, transform=ax.transData,
                                   clip_on=False))
        ax.text(-0.5 + j*2.1 + 0.2, len(universes) + 0.55, lbl,
                fontsize=6.5, color=FG, transform=ax.transData,
                va="center", clip_on=False)

    fig.tight_layout()
    return _save(fig, output)


# ── CLI ────────────────────────────────────────────────────────────────────────

def _parse_labels(s: str) -> dict:
    """Parse 'N:empty,T:spinUp,F:spinDown,B:paired' → dict."""
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
  python3 ig_figures.py profile --tuple "Ð_ω Þ_O Ř_= Φ_} ƒ^ż Ç^@ Γ_ʔ ɢ^ˌ ⊙_ÿ Ħ_A Σ_ï Ω_z"
  python3 ig_figures.py tier --highlight O_inf
  python3 ig_figures.py frobenius
""",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # belnap
    pb = sub.add_parser("belnap", help="Belnap FOUR Hasse diagram")
    pb.add_argument("--labels",    default="", help="N:lbl,T:lbl,F:lbl,B:lbl")
    pb.add_argument("--highlight", default="", help="N|T|F|B")
    pb.add_argument("--caption",   default="")
    pb.add_argument("--out",       default="fig_belnap.pdf")

    # profile
    pp = sub.add_parser("profile", help="12-primitive profile bar chart")
    pp.add_argument("--tuple", required=True,
                    help="Structural tuple string")
    pp.add_argument("--title", default="")
    pp.add_argument("--out",   default="fig_profile.pdf")

    # tier
    pt = sub.add_parser("tier", help="Tier hierarchy chain")
    pt.add_argument("--highlight", default="O_∞",
                    help="Tier to highlight (O_0|O_1|O_2|O_2†|O_∞)")
    pt.add_argument("--out", default="fig_tier.pdf")

    # frobenius
    pf = sub.add_parser("frobenius", help="μ∘δ=id triangle")
    pf.add_argument("--out", default="fig_frobenius.pdf")

    # bootstrap
    ph = sub.add_parser("psychedelic", help="Compound × universe access heatmap")
    ph.add_argument("--out", default="fig_psychedelic_heatmap.pdf")

    pb2 = sub.add_parser("bootstrap", help="IMASM 8-instruction bootstrap loop")
    pb2.add_argument("--out", default="fig_bootstrap.pdf")

    # cetacean
    pc = sub.add_parser("cetacean", help="Cetacean structural space scatter")
    pc.add_argument("--out", default="fig_cetacean.pdf")

    args = p.parse_args()

    if args.cmd == "belnap":
        labels = _parse_labels(args.labels) if args.labels else None
        out = belnap_lattice(
            labels=labels,
            highlight=args.highlight or None,
            caption=args.caption,
            output=args.out,
        )
    elif args.cmd == "profile":
        out = primitive_profile(
            tuple_str=args.tuple,
            title=args.title,
            output=args.out,
        )
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
