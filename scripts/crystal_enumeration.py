#!/usr/bin/env python3
"""
crystal_enumeration.py — Crystal of Types

The 12-primitive tuple ⟨D; T; R; P; F; K; G; ∈; ⊙; H; S; ⊡⟩ is a coordinate chart
on the space of algebraic structures.  Each point in that space IS a type —
a class of algebra determined by the coordinate.

This script enumerates the full combinatorial space, classifies every type by its
ouroboricity tier (which is determined entirely by <, P, ⊡, D), and generates the
PERIODIC CRYSTAL OF ALGEBRAS document.

Tier rules (priority order):
  R1: < ∈ {⊙, 𐑮} AND P = 𐑹  →  O_∞
  R2: < ∈ {𐑢, 𐑣, 𐑻}               →  O₀
  R3: < ∈ {⊙, 𐑮} AND ⊡ = 𐑷       →  O₁
  R4: < ∈ {⊙, 𐑮} AND ⊡ ≠ 𐑷
      AND D ∈ {𐑛, 𐑨, 𐑦}      →  O₂
  R5: < ∈ {⊙, 𐑮} AND ⊡ ≠ 𐑷
      AND D = 𐑼                             →  O₂†
"""

import json
import itertools
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent

# ── Canonical primitive value sets (from space_search/primitives.py) ───────────
VALUES = {
    "⊢":     ["𐑛", "𐑨", "𐑼", "𐑦"],
    "⊣":     ["𐑡", "𐑰", "𐑥", "𐑶", "𐑸"],
    "≻":     ["𐑩", "𐑑", "𐑽", "𐑾"],
    "≺":     ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"],
    "⋈":     ["⋈^ì", "⋈^ð", "⋈^ż"],
    "⊤":     ["⊤^-", "⊤^W", "⊤^@", "⊤^Ù"],
    "∈":     ["𐑚", "𐑔", "𐑲"],
    "∋": ["∋^∧", "∋^˝", "∋^ˌ", "∋^Ş"],
    "⊙":   ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"],
    "⊥":     ["𐑓", "𐑒", "𐑖", "𐑫"],
    "⊞":     ["𐑙", "𐑕", "𐑳"],
    "⊡": ["𐑷", "𐑴", "𐑭"],
}

PRIMS = list(VALUES.keys())

CRITICAL = {"⊙", "𐑮"}
NONCRITICAL = {"𐑢", "𐑣", "𐑻"}
BOUNDED_D = {"𐑛", "𐑨", "𐑦"}

def tier(phi, p, omega, d):
    if phi in CRITICAL and p == "𐑹":
        return "O_∞"
    if phi in NONCRITICAL:
        return "O₀"
    # phi is critical, p != 𐑹
    if omega == "𐑷":
        return "O₁"
    if d in BOUNDED_D:
        return "O₂"
    return "O₂†"   # 𐑼


# ── Total combinatorial space ──────────────────────────────────────────────────
total = 1
for v in VALUES.values():
    total *= len(v)

print(f"Total types: {total:,}")


# ── Analytical enumeration of tier counts ─────────────────────────────────────
# Tier is determined by (Phi, P, Omega, D) only.
# Remaining 8 primitives (T, R, F, K, G, Gamma, H, S) are free within each tier cell.

free_count = 1
for p in ["⊣", "≻", "⋈", "⊤", "∈", "∋", "⊥", "⊞"]:
    free_count *= len(VALUES[p])
# free_count = 5*4*3*4*3*4*4*3 = 17,280

tier_counts = defaultdict(int)
tier_cells  = defaultdict(list)          # (Phi, P, Omega, D) cells per tier

for phi in VALUES["⊙"]:
    for p in VALUES["≺"]:
        for omega in VALUES["⊡"]:
            for d in VALUES["⊢"]:
                t = tier(phi, p, omega, d)
                tier_counts[t] += free_count
                tier_cells[t].append((phi, p, omega, d))

print("\nTier counts:")
for t in ["O₀", "O₁", "O₂", "O₂†", "O_∞"]:
    n = tier_counts[t]
    cells = len(tier_cells[t])
    pct = 100.0 * n / total
    print(f"  {t:10s}: {n:>10,}  ({pct:5.1f}%)  from {cells:3d} (<,P,⊡,D) cells  ×  {free_count:,} free combinations")

print(f"\n  free combinations per tier cell: {free_count:,}  (T×R×F×K×G×∈×H×S = 5×4×3×4×3×4×4×3)")


# ── Period × Group × Block structure ──────────────────────────────────────────
# Period = Phi (5 periods)
# Group  = Omega (3 groups)
# Block  = ouroboricity tier

print("\n\nPERIODIC TABLE STRUCTURE  (Period=< × Group=⊡, counting (<,P,⊡,D) tier cells)\n")
header = f"{'≺':18s}  {'𐑷':>10}  {'𐑴':>10}  {'𐑭':>10}  {'Dominant tier'}"
print(header)
print("─" * len(header))

PERIOD_LABEL = {
    "𐑢":       "𐑢   (ordered)",
    "⊙":         "⊙     (critical)",
    "𐑮": "⊙^C   (complex-crit)",
    "𐑻":        "𐑻    (exc. point)",
    "𐑣":     "𐑣 (disordered)",
}

for phi in VALUES["⊙"]:
    row = {}
    dom = defaultdict(int)
    for omega in VALUES["⊡"]:
        cell_types = defaultdict(int)
        for p in VALUES["≺"]:
            for d in VALUES["⊢"]:
                t = tier(phi, p, omega, d)
                cell_types[t] += 1
                dom[t] += 1
        row[omega] = cell_types
    dominant = max(dom, key=dom.get)
    # Count TYPES (= cells × free) for each Omega group
    def cell_total(omega):
        return sum(row[omega].values()) * free_count
    print(f"{PERIOD_LABEL[phi]:22s}  "
          f"{cell_total('𐑷'):>10,}  "
          f"{cell_total('𐑴'):>10,}  "
          f"{cell_total('𐑭'):>10,}  "
          f"{dominant}")


# ── Sub-table: P axis within each critical period ─────────────────────────────
print("\n\nP (PARITY/FROBENIUS) AXIS — within critical periods (⊙ and 𐑮)\n")
print(f"{'P value':12s}  {'𐑷 → tier':16s}  {'⊡≠0, D_bnd → tier':22s}  {'⊡≠0, D_∞ → tier':20s}")
print("─" * 75)

for p in VALUES["≺"]:
    t_o1    = tier("⊙", p, "𐑷",  "𐑛")
    t_o2    = tier("⊙", p, "𐑴", "𐑛")
    t_o2d   = tier("⊙", p, "𐑴", "𐑼")
    print(f"{p:12s}  {t_o1:16s}  {t_o2:22s}  {t_o2d}")

print()
print("  → 𐑹 collapses all three ⊡ columns to O_∞ (R1 overrides R3/R4/R5)")
print("  → All other P values respect the ⊡/D branching (R3/R4/R5)")


# ── Cross-reference with catalog ───────────────────────────────────────────────
with open(ROOT / "IG_catalog.json") as f:
    catalog = json.load(f)

catalog_by_tier = defaultdict(list)
for entry in catalog:
    phi   = entry.get("⊙", "𐑢")
    p     = entry.get("≺", "𐑗")
    omega = entry.get("⊡", "𐑷")
    d     = entry.get("⊢", "𐑛")
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
print("\n\nINNER CRYSTAL — 8 free primitives (T, R, F, K, G, ∈, H, S)\n")
inner_combos = {
    "⊣":     5,
    "≻":     4,
    "⋈":     3,
    "⊤":     4,
    "∈":     3,
    "∋": 4,
    "⊥":     4,
    "⊞":     3,
}
print("  These 8 primitives vary freely within each tier cell:")
running = 1
for prim, n in inner_combos.items():
    running *= n
    print(f"    {prim:5s}: {n} values  (running product: {running:,})")

print(f"\n  Inner crystal size: {running:,} types per (<,P,⊡,D) tier cell")

# Show the sub-crystal dimensions as factored groups
print("\n  Factored structure of inner crystal:")
print("    Existence tier  [F, K]:                    3 × 4  =   12  (fidelity × kinetics)")
print("    Scope tier      [G, ∈]:                    3 × 4  =   12  (granularity × grammar)")
print("    Geometric tier  [T, R]:                    5 × 4  =   20  (topology × relation)")
print("    Temporal tier   [H, S]:                    4 × 3  =   12  (depth × stoichiometry)")
print(f"    Combined:        12 × 12 × 20 × 12          = {12*12*20*12:,}  ≠ {running}  (factorisation not clean — corrected:)")
print(f"    True product:    5×4×3×4×3×4×4×3          = {running:,}")


# ── Summary: the full crystal in numbers ──────────────────────────────────────
print("\n\n" + "═"*70)
print("PERIODIC CRYSTAL OF ALGEBRAS — SUMMARY")
print("═"*70)
print(f"  Total types:   {total:>12,}")
print(f"  Tier-determining axes:     < (5) × P (5) × ⊡ (3) × D (4) = {5*5*3*4:,} tier cells")
print(f"  Free inner dimensions:     T(5)×R(4)×F(3)×K(4)×G(3)×∋(4)×H(4)×S(3) = {free_count:,} per cell")
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
