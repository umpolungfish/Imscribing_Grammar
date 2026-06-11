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
  R1: Φ ∈ {⊙_ÿ, ⊙_Æ} AND P = Φ_}  →  O_∞
  R2: Φ ∈ {Φ_sub, Φ_super, Φ_EP}               →  O₀
  R3: Φ ∈ {⊙_ÿ, ⊙_Æ} AND Ω = Ω_Å       →  O₁
  R4: Φ ∈ {⊙_ÿ, ⊙_Æ} AND Ω ≠ Ω_Å
      AND D ∈ {Ð_ß, Ð_C, Ð_ω}      →  O₂
  R5: Φ ∈ {⊙_ÿ, ⊙_Æ} AND Ω ≠ Ω_Å
      AND D = Ð_;                             →  O₂†
"""

import json
import itertools
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent

# ── Canonical primitive value sets (from space_search/primitives.py) ───────────
VALUES = {
    "Ð":     ["Ð_ß", "Ð_C", "Ð_;", "Ð_ω"],
    "Þ":     ["Þ_6", "Þ_K", "Þ_ò", "Þ_¨", "Þ_O"],
    "Ř":     ["Ř_¯", "Ř_ý", "Ř_Ť", "Ř_="],
    "Φ":     ["Φ_ɐ", "Φ_υ", "Φ_F", "Φ_˙", "Φ_}"],
    "ƒ":     ["ƒ^ì", "ƒ^ð", "ƒ^ż"],
    "Ç":     ["Ç^-", "Ç^W", "Ç^@", "Ç^Ù"],
    "Γ":     ["Γ_β", "Γ_γ", "Γ_ʔ"],
    "ɢ": ["ɢ^∧", "ɢ^˝", "ɢ^ˌ", "ɢ^Ş"],
    "⊙":   ["⊙_ž", "⊙_ÿ", "⊙_Æ", "⊙_3", "⊙_Ţ"],
    "Ħ":     ["Ħ_Ñ", "Ħ_£", "Ħ_A", "Ħ_!"],
    "Σ":     ["Σ_S", "Σ_ő", "Σ_ï"],
    "Ω": ["Ω_Å", "Ω_2", "Ω_z"],
}

PRIMS = list(VALUES.keys())

CRITICAL = {"⊙_ÿ", "⊙_Æ"}
NONCRITICAL = {"⊙_ž", "⊙_Ţ", "⊙_3"}
BOUNDED_D = {"Ð_ß", "Ð_C", "Ð_ω"}

def tier(phi, p, omega, d):
    if phi in CRITICAL and p == "Φ_}":
        return "O_∞"
    if phi in NONCRITICAL:
        return "O₀"
    # phi is critical, p != Φ_}
    if omega == "Ω_Å":
        return "O₁"
    if d in BOUNDED_D:
        return "O₂"
    return "O₂†"   # Ð_;


# ── Total combinatorial space ──────────────────────────────────────────────────
total = 1
for v in VALUES.values():
    total *= len(v)

print(f"Total structural types: {total:,}")


# ── Analytical enumeration of tier counts ─────────────────────────────────────
# Tier is determined by (Phi, P, Omega, D) only.
# Remaining 8 primitives (T, R, F, K, G, Gamma, H, S) are free within each tier cell.

free_count = 1
for p in ["Þ", "Ř", "ƒ", "Ç", "Γ", "ɢ", "Ħ", "Σ"]:
    free_count *= len(VALUES[p])
# free_count = 5*4*3*4*3*4*4*3 = 17,280

tier_counts = defaultdict(int)
tier_cells  = defaultdict(list)          # (Phi, P, Omega, D) cells per tier

for phi in VALUES["⊙"]:
    for p in VALUES["Φ"]:
        for omega in VALUES["Ω"]:
            for d in VALUES["Ð"]:
                t = tier(phi, p, omega, d)
                tier_counts[t] += free_count
                tier_cells[t].append((phi, p, omega, d))

print("\nTier counts:")
for t in ["O₀", "O₁", "O₂", "O₂†", "O_∞"]:
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
header = f"{'Φ':18s}  {'Ω_Å':>10}  {'Ω_2':>10}  {'Ω_z':>10}  {'Dominant tier'}"
print(header)
print("─" * len(header))

PERIOD_LABEL = {
    "⊙_ž":       "Φ_sub   (ordered)",
    "⊙_ÿ":         "⊙_ÿ     (critical)",
    "⊙_Æ": "⊙_ÿ^C   (complex-crit)",
    "⊙_3":        "Φ_EP    (exc. point)",
    "⊙_Ţ":     "⊙_Ţ (disordered)",
}

for phi in VALUES["⊙"]:
    row = {}
    dom = defaultdict(int)
    for omega in VALUES["Ω"]:
        cell_types = defaultdict(int)
        for p in VALUES["Φ"]:
            for d in VALUES["Ð"]:
                t = tier(phi, p, omega, d)
                cell_types[t] += 1
                dom[t] += 1
        row[omega] = cell_types
    dominant = max(dom, key=dom.get)
    # Count TYPES (= cells × free) for each Omega group
    def cell_total(omega):
        return sum(row[omega].values()) * free_count
    print(f"{PERIOD_LABEL[phi]:22s}  "
          f"{cell_total('Ω_Å'):>10,}  "
          f"{cell_total('Ω_2'):>10,}  "
          f"{cell_total('Ω_z'):>10,}  "
          f"{dominant}")


# ── Sub-table: P axis within each critical period ─────────────────────────────
print("\n\nP (PARITY/FROBENIUS) AXIS — within critical periods (⊙_ÿ and ⊙_Æ)\n")
print(f"{'P value':12s}  {'Ω_Å → tier':16s}  {'Ω≠0, D_bnd → tier':22s}  {'Ω≠0, D_∞ → tier':20s}")
print("─" * 75)

for p in VALUES["Φ"]:
    t_o1    = tier("⊙_ÿ", p, "Ω_Å",  "Ð_ß")
    t_o2    = tier("⊙_ÿ", p, "Ω_2", "Ð_ß")
    t_o2d   = tier("⊙_ÿ", p, "Ω_2", "Ð_;")
    print(f"{p:12s}  {t_o1:16s}  {t_o2:22s}  {t_o2d}")

print()
print("  → Φ_} collapses all three Ω columns to O_∞ (R1 overrides R3/R4/R5)")
print("  → All other P values respect the Ω/D branching (R3/R4/R5)")


# ── Cross-reference with catalog ───────────────────────────────────────────────
with open(ROOT / "IG_catalog.json") as f:
    catalog = json.load(f)

catalog_by_tier = defaultdict(list)
for entry in catalog:
    phi   = entry.get("⊙", "⊙_ž")
    p     = entry.get("Φ", "Φ_ɐ")
    omega = entry.get("Ω", "Ω_Å")
    d     = entry.get("Ð", "Ð_ß")
    t     = tier(phi, p, omega, d)
    catalog_by_tier[t].append(entry["name"])

print("\n\nCATALOG COVERAGE PER TIER\n")
for t in ["O₀", "O₁", "O₂", "O₂†", "O_∞"]:
    names = catalog_by_tier[t]
    print(f"  {t:10s}: {len(names):4d} catalog entries  ({100*len(names)/len(catalog):.1f}%)")
    # Show up to 6 example names
    sample = names[:6]
    print(f"             e.g. {', '.join(sample)}")

print(f"\n  Total catalog: {len(catalog)} entries")


# ── The 8-primitive inner crystal (free primitives within each tier cell) ──────
print("\n\nINNER CRYSTAL — 8 free primitives (T, R, F, K, G, Γ, H, S)\n")
inner_combos = {
    "Þ":     5,
    "Ř":     4,
    "ƒ":     3,
    "Ç":     4,
    "Γ":     3,
    "ɢ": 4,
    "Ħ":     4,
    "Σ":     3,
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
for t in ["O₀", "O₁", "O₂", "O₂†", "O_∞"]:
    n     = tier_counts[t]
    cells = len(tier_cells[t])
    print(f"  {t:10s}  {cells:3d} cells  ×  {free_count:,}  =  {n:>10,}  ({100*n/total:.1f}%)")
print()
print(f"  Non-critical (O₀):        {tier_counts['O₀']:>10,}  ({100*tier_counts['O₀']/total:.1f}%)")
crit = total - tier_counts["O₀"]
print(f"  Critical subtotal:         {crit:>10,}  ({100*crit/total:.1f}%)")
print(f"    Of which O_∞:          {tier_counts['O_∞']:>10,}  ({100*tier_counts['O_∞']/total:.1f}%)")
