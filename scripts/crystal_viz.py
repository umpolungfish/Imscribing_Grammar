#!/usr/bin/env python3
"""
crystal_viz.py — Crystal of Types: Visualizations

Generates four figures:
  1. crystal_periodic_table.png   — 5×3 <×Ω periodic table with tier distributions
  2. crystal_tier_census.png      — Treemap of 10.4M types by tier
  3. crystal_p_axis.png           — P-axis Frobenius collapse matrix
  4. crystal_inner_crystal.png    — Inner 34,560-type sub-crystal quadrant diagram
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

ROOT = Path(__file__).parent

BG   = "#0F0F1A"
BG2  = "#1A1A2E"

TIER_COLOR = {
    "O₀":       "#4472C4",   # steel blue
    "O₁":       "#FFD700",   # gold
    "O₂":       "#FF8C00",   # dark orange
    "O₂†":   "#DC143C",   # crimson
    "O_∞":     "#9370DB",   # medium purple
}
TIER_LABEL = {
    "O₀":       r"$O₀$  (inert)",
    "O₁":       r"$O₁$  (unprotected critical)",
    "O₂":       r"$O₂$  (protected, bounded)",
    "O₂†":   r"$O₂^\dagger$  (protected, unbounded)",
    "O_∞":     r"$O_\infty$  (Frobenius complete)",
}

PHI_VALUES   = ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"]
OMEGA_VALUES = ["𐑷", "𐑴", "𐑭"]
P_VALUES     = ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"]
D_VALUES     = ["𐑛", "𐑨", "𐑼", "𐑦"]

CRITICAL   = {"⊙", "𐑮", "⊙", "𐑮"}      # ⊙ + 𐑮, old + Shavian
NONCRIT    = {"𐑢", "𐑣", "𐑻", "𐑢", "𐑻", "𐑣"}   # 𐑢/EP/super
BOUNDED_D  = {"𐑛", "𐑨", "𐑦", "𐑛", "𐑨", "𐑦"}   # non-D_odot
P_PM_SYM   = {"𐑹", "𐑹"}                  # Frobenius polarity, old + Shavian
OMEGA_0    = {"𐑷", "𐑷", ""}              # no topological protection

def get_tier(phi, p, omega, d):
    # R1 (Lean-authoritative): ⊙ + P_pm_sym → O_∞
    if phi in CRITICAL and p in P_PM_SYM:
        return "O_∞"
    if phi in NONCRIT:
        return "O₀"
    if omega in OMEGA_0:
        return "O₁"
    if d in BOUNDED_D:
        return "O₂"
    return "O₂†"

INNER_PER_CELL = 34_560   # T(5)×R(4)×F(3)×K(4)×G(3)×∋(4)×H(4)×S(3)

def cell_tier_breakdown(phi, omega):
    """Return {tier: count} for one (Phi, Omega) cell — all P and D values."""
    counts = {t: 0 for t in TIER_COLOR}
    for p in P_VALUES:
        for d in D_VALUES:
            t = get_tier(phi, p, omega, d)
            counts[t] += INNER_PER_CELL
    return counts

PHI_LABEL = {
    "𐑢":       r"$\Phi_\mathrm{sub}$" + "\nordered",
    "⊙":         r"$\⊙$" + "\nreal-axis critical",
    "𐑮": r"$\⊙^\mathbb{C}$" + "\ncomplex-axis critical",
    "𐑻":        r"$\Phi_\mathrm{EP}$" + "\nexceptional point",
    "𐑣":     r"$\Phi_\mathrm{sup}$" + "\ndisordered",
}
OMEGA_LABEL = {
    "𐑷":  r"$\𐑷$" + "\nno protection",
    "𐑴": r"$\Omega_{Z_2}$" + "\nbinary protection",
    "𐑭":  r"$\Omega_\mathbb{Z}$" + "\ninteger winding",
}


# ══════════════════════════════════════════════════════════════════════
# FIGURE 1 — Periodic Table
# ══════════════════════════════════════════════════════════════════════
fig1, axes = plt.subplots(5, 3, figsize=(22, 22), facecolor=BG)
fig1.patch.set_facecolor(BG)
fig1.subplots_adjust(hspace=0.08, wspace=0.06, top=0.92, bottom=0.08, left=0.12, right=0.97)

fig1.text(0.5, 0.965, "Crystal of Types",
          ha="center", va="top", color="white",
          fontsize=26, fontweight="bold", fontfamily="sans-serif")
fig1.text(0.5, 0.945,
          r"10,368,000 types  ·  $5(\Phi) \times 3(\Omega)$ periods/groups  ·  "
          r"each cell: $5(P)\times4(D)\times34{,}560\text{ inner} = 691{,}200$ types",
          ha="center", va="top", color="#AAAACC", fontsize=13)

TIER_ORDER = ["O₀", "O₁", "O₂", "O₂†", "O_∞"]

for row_i, phi in enumerate(PHI_VALUES):
    for col_j, omega in enumerate(OMEGA_VALUES):
        ax = axes[row_i, col_j]
        ax.set_facecolor(BG2)
        for spine in ax.spines.values():
            spine.set_color("#333355")
            spine.set_linewidth(1.2)

        breakdown = cell_tier_breakdown(phi, omega)
        total     = sum(breakdown.values())   # always 691,200

        # Stacked horizontal bar
        left = 0.0
        bar_y = 0.62
        bar_h = 0.26
        for tier in TIER_ORDER:
            w = breakdown[tier] / total
            if w > 0:
                ax.barh(bar_y, w, left=left, height=bar_h,
                        color=TIER_COLOR[tier], edgecolor="none",
                        zorder=3)
                if w > 0.06:
                    label = {"O₀":"O₀","O₁":"O₁","O₂":"O₂",
                             "O₂†":"O₂†","O_∞":"O∞"}[tier]
                    ax.text(left + w/2, bar_y, label,
                            ha="center", va="center",
                            fontsize=9, color="black" if tier in ("O₁","O_∞") else "white",
                            fontweight="bold", zorder=4)
                left += w

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

        # Percentage annotations
        y_ann = 0.38
        for tier in TIER_ORDER:
            pct = breakdown[tier] / total
            if pct > 0.005:
                ax.text(left - (1 - left)/2 if pct == 1 else 0.5, y_ann,
                        "",  ha="center", fontsize=8, color="#CCCCCC")

        # Summary text — largest tier + pct
        dominant = max(TIER_ORDER, key=lambda t: breakdown[t])
        dom_pct  = breakdown[dominant] / total * 100
        ax.text(0.5, 0.22,
                f"691,200 types\n"
                f"dom: {dominant.replace('_dag','†').replace('_inf','∞')}  {dom_pct:.0f}%",
                ha="center", va="center", color="#AAAACC",
                fontsize=8.5, zorder=4)

        # Cell border highlight for critical rows
        if phi in CRITICAL:
            for spine in ax.spines.values():
                spine.set_color("#FFD700")
                spine.set_linewidth(2.0)

        # Column headers (top row only)
        if row_i == 0:
            ax.set_title(OMEGA_LABEL[omega], color="white",
                         fontsize=12, pad=10, fontweight="bold")

    # Row label (leftmost col)
    axes[row_i, 0].text(-0.18, 0.5, PHI_LABEL[phi],
                        transform=axes[row_i, 0].transAxes,
                        ha="right", va="center", color="white",
                        fontsize=11, fontweight="bold",
                        multialignment="right")

# Legend
tier_patches = [
    mpatches.Patch(facecolor=TIER_COLOR[t], label=TIER_LABEL[t], linewidth=0)
    for t in TIER_ORDER
]
fig1.legend(handles=tier_patches, loc="lower center",
            ncol=5, bbox_to_anchor=(0.5, 0.01),
            framealpha=0.4, facecolor=BG2, edgecolor="#555577",
            labelcolor="white", fontsize=12,
            title="Ouroboricity tier", title_fontsize=13)

out1 = ROOT / "crystal_periodic_table.png"
fig1.savefig(out1, dpi=300, facecolor=BG, bbox_inches="tight")
print(f"Saved: {out1}")
plt.close(fig1)


# ══════════════════════════════════════════════════════════════════════
# FIGURE 2 — Tier Census (nested rectangles / treemap-style)
# ══════════════════════════════════════════════════════════════════════
TOTAL       = 10_368_000
TIER_TOTALS = {
    "O₀":     6_220_800,
    "O₁":     1_105_920,
    "O₂":     1_658_880,
    "O₂†":   552_960,
    "O_∞":     829_440,
}
TIER_CELLS = {"O₀":180, "O₁":32, "O₂":48, "O₂†":16, "O_∞":24}

fig2, ax2 = plt.subplots(figsize=(20, 10), facecolor=BG)
fig2.patch.set_facecolor(BG)
ax2.set_facecolor(BG)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_title("Periodic Crystal — Tier Census: 10,368,000 = $4^5 \\times 5^3 \\times 3^4$ types",
              color="white", fontsize=20, fontweight="bold", pad=16)

# Simple horizontal stacked bar for the full space
bar_y = 0.42
bar_h = 0.22
left  = 0.04
bar_w = 0.92

for tier in TIER_ORDER:
    w = TIER_TOTALS[tier] / TOTAL * bar_w
    pct = TIER_TOTALS[tier] / TOTAL * 100
    ax2.add_patch(FancyBboxPatch(
        (left, bar_y), w, bar_h,
        boxstyle="round,pad=0.005",
        facecolor=TIER_COLOR[tier], edgecolor="none", zorder=3
    ))
    # Label inside bar
    ax2.text(left + w/2, bar_y + bar_h/2,
             f"{tier.replace('_dag','†').replace('_inf','∞')}\n"
             f"{TIER_TOTALS[tier]:,}\n{pct:.1f}%",
             ha="center", va="center",
             fontsize=11.5 if w > 0.07 else 9,
             color="black" if tier in ("O₁",) else "white",
             fontweight="bold", zorder=4)
    left += w

# Add cell-count bar below
bar_y2 = 0.17
bar_h2 = 0.10
left2  = 0.04
for tier in TIER_ORDER:
    w = TIER_CELLS[tier] / 300 * bar_w
    ax2.add_patch(FancyBboxPatch(
        (left2, bar_y2), w, bar_h2,
        boxstyle="round,pad=0.005",
        facecolor=TIER_COLOR[tier], edgecolor="none", alpha=0.7, zorder=3
    ))
    ax2.text(left2 + w/2, bar_y2 + bar_h2/2,
             f"{TIER_CELLS[tier]} cells",
             ha="center", va="center", fontsize=9,
             color="black" if tier in ("O₁",) else "white", zorder=4)
    left2 += w

ax2.text(0.02, bar_y + bar_h/2, "Types:", color="white", fontsize=12,
         va="center", ha="right", transform=ax2.transAxes)
ax2.text(0.02, bar_y2 + bar_h2/2, "Tier\ncells:", color="white", fontsize=10,
         va="center", ha="right", transform=ax2.transAxes)

# Right-side annotation
ax2.text(0.5, 0.94,
         "300 tier cells  ×  34,560 inner types  =  10,368,000",
         ha="center", va="top", color="#AAAACC", fontsize=13,
         transform=ax2.transAxes)
ax2.text(0.5, 0.88,
         "Inner crystal:  T(5)×R(4)×F(3)×K(4)×G(3)×∋(4)×H(4)×S(3)  =  34,560  per tier cell",
         ha="center", va="top", color="#888899", fontsize=11,
         transform=ax2.transAxes)

fig2.text(0.5, 0.02, "Imscribing Grammar — Crystal Census  ·  2026-04-08",
          ha="center", va="bottom", color="white", fontsize=10, alpha=0.5,
          fontfamily="monospace")

out2 = ROOT / "crystal_tier_census.png"
fig2.savefig(out2, dpi=300, facecolor=BG, bbox_inches="tight")
print(f"Saved: {out2}")
plt.close(fig2)


# ══════════════════════════════════════════════════════════════════════
# FIGURE 3 — P-axis Frobenius collapse matrix
# ══════════════════════════════════════════════════════════════════════
# Rows: P values (5)
# Columns: 6 combinations of (Ω, D-type): (Ω0,any), (ΩZ2,D_bnd), (ΩZ2,D_inf), (ΩZ,D_bnd), (ΩZ,D_inf) — 5 combos
# + 1 column for "𐑹 collapses all" label

OMEGA_D_COMBOS = [
    ("𐑷",  "𐑛",    r"$\𐑷$" + "\n(any $D$)"),
    ("𐑴", "𐑛",    r"$\Omega_{Z_2}$" + "\nbounded $D$"),
    ("𐑴", "𐑼",    r"$\Omega_{Z_2}$" + "\n$D_\infty$"),
    ("𐑭",  "𐑛",    r"$\Omega_\mathbb{Z}$" + "\nbounded $D$"),
    ("𐑭",  "𐑼",    r"$\Omega_\mathbb{Z}$" + "\n$D_\infty$"),
]
P_SHORT = {
    "𐑗":    r"$P_\mathrm{asym}$",
    "𐑿":     r"$P_\psi$",
    "𐑬":      r"$P_{\pm}$",
    "𐑯":     r"$P_\mathrm{sym}$",
    "𐑹":  r"$P_{\pm}^\mathrm{sym}$" + "\n(Frobenius)",
}

fig3, ax3 = plt.subplots(figsize=(18, 9), facecolor=BG)
fig3.patch.set_facecolor(BG)
ax3.set_facecolor(BG)
ax3.set_xlim(-0.5, len(OMEGA_D_COMBOS) - 0.5)
ax3.set_ylim(-0.5, len(P_VALUES) - 0.5)
for spine in ax3.spines.values():
    spine.set_visible(False)

ax3.set_title(r"P-axis Frobenius Collapse: $P_{\pm}^\mathrm{sym}$ overrides all $\Omega$ and $D$ branching",
              color="white", fontsize=19, fontweight="bold", pad=18)

for p_i, p in enumerate(P_VALUES):
    for od_j, (omega, d, _) in enumerate(OMEGA_D_COMBOS):
        t = get_tier("⊙", p, omega, d)
        color = TIER_COLOR[t]
        label = t.replace("_dag","†").replace("_inf","∞").replace("O_","O")

        ax3.add_patch(FancyBboxPatch(
            (od_j - 0.44, p_i - 0.4), 0.88, 0.80,
            boxstyle="round,pad=0.03",
            facecolor=color, edgecolor=BG, linewidth=2, zorder=3
        ))
        ax3.text(od_j, p_i, label,
                 ha="center", va="center",
                 fontsize=14, fontweight="bold",
                 color="black" if t in ("O₁","O_∞") else "white",
                 zorder=4)

# Highlight the 𐑹 row with golden border
p_frobenius = P_VALUES.index("𐑹")
ax3.add_patch(plt.Rectangle(
    (-0.5, p_frobenius - 0.5), len(OMEGA_D_COMBOS), 1.0,
    fill=False, edgecolor="#FFD700", linewidth=3, zorder=5
))

# Column headers
for od_j, (_, _, label) in enumerate(OMEGA_D_COMBOS):
    ax3.text(od_j, len(P_VALUES) - 0.05, label,
             ha="center", va="bottom", color="white", fontsize=11)

# Row labels
for p_i, p in enumerate(P_VALUES):
    ax3.text(-0.55, p_i, P_SHORT[p],
             ha="right", va="center", color="white",
             fontsize=12, fontweight="bold" if p == "𐑹" else "normal")

ax3.set_xticks([])
ax3.set_yticks([])
ax3.invert_yaxis()   # 𐑗 at top, 𐑹 at bottom... actually keep natural order

# Annotation
ax3.text(len(OMEGA_D_COMBOS)/2 - 0.5, -0.9,
         r"R1: $\⊙ + P_{\pm}^\mathrm{sym} \rightarrow O_\infty$ (overrides R3/R4/R5)    "
         r"R3: $\⊙ + \𐑷 \rightarrow O₁$    "
         r"R4: bounded $D \rightarrow O₂$    "
         r"R5: $D_\infty \rightarrow O₂^\dagger$",
         ha="center", va="top", color="#AAAACC", fontsize=10)

# Legend
tier_patches3 = [
    mpatches.Patch(facecolor=TIER_COLOR[t], label=TIER_LABEL[t], linewidth=0)
    for t in ["O₁", "O₂", "O₂†", "O_∞"]
]
ax3.legend(handles=tier_patches3, loc="lower right",
           bbox_to_anchor=(1.0, -0.05),
           framealpha=0.4, facecolor=BG2, edgecolor="#555577",
           labelcolor="white", fontsize=11)

fig3.text(0.5, 0.01, "Imscribing Grammar — Crystal: P-axis  ·  2026-04-08",
          ha="center", va="bottom", color="white", fontsize=9, alpha=0.5,
          fontfamily="monospace")

out3 = ROOT / "crystal_p_axis.png"
fig3.savefig(out3, dpi=300, facecolor=BG, bbox_inches="tight")
print(f"Saved: {out3}")
plt.close(fig3)


# ══════════════════════════════════════════════════════════════════════
# FIGURE 4 — Inner Crystal: 4 sub-groups
# ══════════════════════════════════════════════════════════════════════
fig4, ax4 = plt.subplots(figsize=(18, 10), facecolor=BG)
fig4.patch.set_facecolor(BG)
ax4.set_facecolor(BG)
ax4.set_xlim(0, 1)
ax4.set_ylim(0, 1)
for spine in ax4.spines.values():
    spine.set_visible(False)
ax4.set_xticks([])
ax4.set_yticks([])
ax4.set_title(r"Inner Crystal: 34,560 types per tier cell  =  "
              r"$20_\mathrm{geom} \times 12_\mathrm{exist} \times 12_\mathrm{scope} \times 12_\mathrm{temp}$",
              color="white", fontsize=19, fontweight="bold", pad=16)

# Draw four quadrant boxes
QUADS = [
    {
        "label": "Geometric",
        "prims": "T × R",
        "size":  "5 × 4 = 20",
        "vals":  "⊣: network, in, bowtie, box, ⊙\nR: super, cat, dagger, lr",
        "role":  "Topology × Relational mode\n(how the algebra connects)",
        "color": "#2255AA",
        "x": 0.03, "y": 0.12, "w": 0.44, "h": 0.72,
    },
    {
        "label": "Existence",
        "prims": "F × K",
        "size":  "3 × 4 = 12",
        "vals":  "⋈: ℓ, ℏ, ħ\nK: fast, mod, slow, trap",
        "role":  "Fidelity × Kinetics\n(how faithfully and how fast)",
        "color": "#225522",
        "x": 0.51, "y": 0.57, "w": 0.46, "h": 0.27,
    },
    {
        "label": "Scope",
        "prims": "G × ∈",
        "size":  "3 × 4 = 12",
        "vals":  "∈: ℶ, ℷ, ℵ\n∈: and, or, seq, broad",
        "role":  "Granularity × Interaction grammar\n(how wide and how structured)",
        "color": "#552222",
        "x": 0.51, "y": 0.35, "w": 0.46, "h": 0.20,
    },
    {
        "label": "Temporal",
        "prims": "H × S",
        "size":  "4 × 3 = 12",
        "vals":  "Ħ: H₀, H₁, H₂, H∞\nS: 1:1, n:n, n:m",
        "role":  "Chirality depth × Stoichiometry\n(how deep and how many)",
        "color": "#442255",
        "x": 0.51, "y": 0.12, "w": 0.46, "h": 0.21,
    },
]

for q in QUADS:
    ax4.add_patch(FancyBboxPatch(
        (q["x"], q["y"]), q["w"], q["h"],
        boxstyle="round,pad=0.015",
        facecolor=q["color"], edgecolor="#AAAACC",
        linewidth=1.5, alpha=0.85, zorder=2
    ))
    cx = q["x"] + q["w"]/2
    cy = q["y"] + q["h"]/2

    ax4.text(cx, q["y"] + q["h"] - 0.03,
             q["label"] + " sub-group",
             ha="center", va="top", color="white",
             fontsize=15, fontweight="bold", zorder=3)
    ax4.text(cx, q["y"] + q["h"] - 0.095,
             q["prims"] + "   →   " + q["size"],
             ha="center", va="top", color="#FFD700",
             fontsize=13, zorder=3)
    ax4.text(cx, cy - 0.01,
             q["vals"],
             ha="center", va="center", color="#CCCCCC",
             fontsize=10.5, zorder=3, linespacing=1.6)
    ax4.text(cx, q["y"] + 0.03,
             q["role"],
             ha="center", va="bottom", color="#AAAACC",
             fontsize=10, style="italic", zorder=3, linespacing=1.5)

# Product annotation
ax4.text(0.5, 0.955,
         "34,560  =  20 × 12 × 12 × 12  (exact four-factor product)",
         ha="center", va="top", color="white", fontsize=14,
         transform=ax4.transAxes)

# Multiplication symbols between boxes
for xmid, ymid, sym in [
    (0.49, 0.71, "×"), (0.49, 0.45, "×"), (0.49, 0.225, "×"),
]:
    ax4.text(xmid, ymid, sym, ha="center", va="center",
             color="#FFD700", fontsize=20, fontweight="bold",
             transform=ax4.transAxes)

fig4.text(0.5, 0.01, "Imscribing Grammar — Crystal: Inner sub-crystal  ·  2026-04-08",
          ha="center", va="bottom", color="white", fontsize=9, alpha=0.5,
          fontfamily="monospace")

out4 = ROOT / "crystal_inner_crystal.png"
fig4.savefig(out4, dpi=300, facecolor=BG, bbox_inches="tight")
print(f"Saved: {out4}")
plt.close(fig4)

print("\nAll crystal visualizations complete.")
