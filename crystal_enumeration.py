#!/usr/bin/env python3
"""
crystal_enumeration.py — Crystal of Types

The 12-primitive tuple ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩ is a coordinate chart
on the space of algebraic structures.  Each point in that space IS a structural type —
a class of algebra determined by the coordinate.

This script enumerates the full combinatorial space, classifies every type by its
ouroboricity tier (which is determined entirely by Φ, P, Ω, D), and generates the
PERIODIC CRYSTAL OF ALGEBRAS document.

Tier rules (priority order):
  R1: Φ ∈ {Φ_c, Φ_c_complex} AND P = P_pm_sym  →  O_∞
  R2: Φ ∈ {Φ_sub, Φ_super, Φ_EP}               →  O_0
  R3: Φ ∈ {Φ_c, Φ_c_complex} AND Ω = Ω_0       →  O_1
  R4: Φ ∈ {Φ_c, Φ_c_complex} AND Ω ≠ Ω_0
      AND D ∈ {D_wedge, D_triangle, D_holo}      →  O_2
  R5: Φ ∈ {Φ_c, Φ_c_complex} AND Ω ≠ Ω_0
      AND D = D_infty                             →  O_2†
"""

import json
import itertools
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent

# ── Canonical primitive value sets (from space_search/primitives.py) ───────────
VALUES = {
    "D":     ["D_wedge", "D_triangle", "D_infty", "D_odot"],
    "T":     ["T_network", "T_in", "T_bowtie", "T_boxtimes", "T_odot"],
    "R":     ["R_super", "R_cat", "R_dagger", "R_lr"],
    "P":     ["P_asym", "P_psi", "P_pm", "P_sym", "P_pm_sym"],
    "F":     ["F_ell", "F_eth", "F_hbar"],
    "K":     ["K_fast", "K_mod", "K_slow", "K_trap"],
    "G":     ["G_beth", "G_gimel", "G_aleph"],
    "Gamma": ["G_and", "G_or", "G_seq", "G_broad"],
    "Phi":   ["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"],
    "H":     ["H0", "H1", "H2", "H_inf"],
    "S":     ["one_one", "n_n", "n_m"],
    "Omega": ["Omega_0", "Omega_Z2", "Omega_Z"],
}

PRIMS = list(VALUES.keys())

CRITICAL = {"Phi_c", "Phi_c_complex"}
NONCRITICAL = {"Phi_sub", "Phi_super", "Phi_EP"}
BOUNDED_D = {"D_wedge", "D_triangle", "D_odot"}

def tier(phi, p, omega, d):
    if phi in CRITICAL and p == "P_pm_sym":
        return "O_inf"
    if phi in NONCRITICAL:
        return "O_0"
    # phi is critical, p != P_pm_sym
    if omega == "Omega_0":
        return "O_1"
    if d in BOUNDED_D:
        return "O_2"
    return "O_2_dag"   # D_infty


# ── Total combinatorial space ──────────────────────────────────────────────────
total = 1
for v in VALUES.values():
    total *= len(v)

print(f"Total structural types: {total:,}")


# ── Analytical enumeration of tier counts ─────────────────────────────────────
# Tier is determined by (Phi, P, Omega, D) only.
# Remaining 8 primitives (T, R, F, K, G, Gamma, H, S) are free within each tier cell.

free_count = 1
for p in ["T", "R", "F", "K", "G", "Gamma", "H", "S"]:
    free_count *= len(VALUES[p])
# free_count = 5*4*3*4*3*4*4*3 = 17,280

tier_counts = defaultdict(int)
tier_cells  = defaultdict(list)          # (Phi, P, Omega, D) cells per tier

for phi in VALUES["Phi"]:
    for p in VALUES["P"]:
        for omega in VALUES["Omega"]:
            for d in VALUES["D"]:
                t = tier(phi, p, omega, d)
                tier_counts[t] += free_count
                tier_cells[t].append((phi, p, omega, d))

print("\nTier counts:")
for t in ["O_0", "O_1", "O_2", "O_2_dag", "O_inf"]:
    n = tier_counts[t]
    cells = len(tier_cells[t])
    pct = 100.0 * n / total
    print(f"  {t:10s}: {n:>10,}  ({pct:5.1f}%)  from {cells:3d} (Φ,P,Ω,D) cells  ×  {free_count:,} free combinations")

print(f"\n  free combinations per tier cell: {free_count:,}  (T×R×F×K×G×Γ×H×S = 5×4×3×4×3×4×4×3)")


# ── Period × Group × Block structure ──────────────────────────────────────────
# Period = Phi (5 periods)
# Group  = Omega (3 groups)
# Block  = ouroboricity tier

print("\n\nPERIODIC TABLE STRUCTURE  (Period=Φ × Group=Ω, counting (Φ,P,Ω,D) tier cells)\n")
header = f"{'Φ':18s}  {'Ω_0':>10}  {'Ω_Z2':>10}  {'Ω_Z':>10}  {'Dominant tier'}"
print(header)
print("─" * len(header))

PERIOD_LABEL = {
    "Phi_sub":       "Φ_sub   (ordered)",
    "Phi_c":         "Φ_c     (critical)",
    "Phi_c_complex": "Φ_c^C   (complex-crit)",
    "Phi_EP":        "Φ_EP    (exc. point)",
    "Phi_super":     "Phi_sup (disordered)",
}

for phi in VALUES["Phi"]:
    row = {}
    dom = defaultdict(int)
    for omega in VALUES["Omega"]:
        cell_types = defaultdict(int)
        for p in VALUES["P"]:
            for d in VALUES["D"]:
                t = tier(phi, p, omega, d)
                cell_types[t] += 1
                dom[t] += 1
        row[omega] = cell_types
    dominant = max(dom, key=dom.get)
    # Count TYPES (= cells × free) for each Omega group
    def cell_total(omega):
        return sum(row[omega].values()) * free_count
    print(f"{PERIOD_LABEL[phi]:22s}  "
          f"{cell_total('Omega_0'):>10,}  "
          f"{cell_total('Omega_Z2'):>10,}  "
          f"{cell_total('Omega_Z'):>10,}  "
          f"{dominant}")


# ── Sub-table: P axis within each critical period ─────────────────────────────
print("\n\nP (PARITY/FROBENIUS) AXIS — within critical periods (Φ_c and Φ_c_complex)\n")
print(f"{'P value':12s}  {'Ω_0 → tier':16s}  {'Ω≠0, D_bnd → tier':22s}  {'Ω≠0, D_∞ → tier':20s}")
print("─" * 75)

for p in VALUES["P"]:
    t_o1    = tier("Phi_c", p, "Omega_0",  "D_wedge")
    t_o2    = tier("Phi_c", p, "Omega_Z2", "D_wedge")
    t_o2d   = tier("Phi_c", p, "Omega_Z2", "D_infty")
    print(f"{p:12s}  {t_o1:16s}  {t_o2:22s}  {t_o2d}")

print()
print("  → P_pm_sym collapses all three Ω columns to O_inf (R1 overrides R3/R4/R5)")
print("  → All other P values respect the Ω/D branching (R3/R4/R5)")


# ── Cross-reference with catalog ───────────────────────────────────────────────
with open(ROOT / "IG_catalog.json") as f:
    catalog = json.load(f)

catalog_by_tier = defaultdict(list)
for entry in catalog:
    phi   = entry.get("Phi", "Phi_sub")
    p     = entry.get("P", "P_asym")
    omega = entry.get("Omega", "Omega_0")
    d     = entry.get("D", "D_wedge")
    t     = tier(phi, p, omega, d)
    catalog_by_tier[t].append(entry["name"])

print("\n\nCATALOG COVERAGE PER TIER\n")
for t in ["O_0", "O_1", "O_2", "O_2_dag", "O_inf"]:
    names = catalog_by_tier[t]
    print(f"  {t:10s}: {len(names):4d} catalog entries  ({100*len(names)/len(catalog):.1f}%)")
    # Show up to 6 example names
    sample = names[:6]
    print(f"             e.g. {', '.join(sample)}")

print(f"\n  Total catalog: {len(catalog)} entries")


# ── The 8-primitive inner crystal (free primitives within each tier cell) ──────
print("\n\nINNER CRYSTAL — 8 free primitives (T, R, F, K, G, Γ, H, S)\n")
inner_combos = {
    "T":     5,
    "R":     4,
    "F":     3,
    "K":     4,
    "G":     3,
    "Gamma": 4,
    "H":     4,
    "S":     3,
}
print("  These 8 primitives vary freely within each tier cell:")
running = 1
for prim, n in inner_combos.items():
    running *= n
    print(f"    {prim:5s}: {n} values  (running product: {running:,})")

print(f"\n  Inner crystal size: {running:,} types per (Φ,P,Ω,D) tier cell")

# Show the sub-crystal dimensions as factored groups
print("\n  Factored structure of inner crystal:")
print("    Existence tier  [F, K]:                    3 × 4  =   12  (fidelity × kinetics)")
print("    Scope tier      [G, Γ]:                    3 × 4  =   12  (granularity × grammar)")
print("    Geometric tier  [T, R]:                    5 × 4  =   20  (topology × relation)")
print("    Temporal tier   [H, S]:                    4 × 3  =   12  (depth × stoichiometry)")
print(f"    Combined:        12 × 12 × 20 × 12          = {12*12*20*12:,}  ≠ {running}  (factorisation not clean — corrected:)")
print(f"    True product:    5×4×3×4×3×4×4×3          = {running:,}")


# ── Summary: the full crystal in numbers ──────────────────────────────────────
print("\n\n" + "═"*70)
print("PERIODIC CRYSTAL OF ALGEBRAS — SUMMARY")
print("═"*70)
print(f"  Total structural types:   {total:>12,}")
print(f"  Tier-determining axes:     Φ (5) × P (5) × Ω (3) × D (4) = {5*5*3*4:,} tier cells")
print(f"  Free inner dimensions:     T(5)×R(4)×F(3)×K(4)×G(3)×Γ(4)×H(4)×S(3) = {free_count:,} per cell")
print()
for t in ["O_0", "O_1", "O_2", "O_2_dag", "O_inf"]:
    n     = tier_counts[t]
    cells = len(tier_cells[t])
    print(f"  {t:10s}  {cells:3d} cells  ×  {free_count:,}  =  {n:>10,}  ({100*n/total:.1f}%)")
print()
print(f"  Non-critical (O_0):        {tier_counts['O_0']:>10,}  ({100*tier_counts['O_0']/total:.1f}%)")
crit = total - tier_counts["O_0"]
print(f"  Critical subtotal:         {crit:>10,}  ({100*crit/total:.1f}%)")
print(f"    Of which O_inf:          {tier_counts['O_inf']:>10,}  ({100*tier_counts['O_inf']/total:.1f}%)")
