#!/usr/bin/env python3
"""
Ensemble Analysis — Full Numerical View of the Imscribing Grammar Catalog.
Author: Lando⊗⊙perator
"""

import sys, json, os
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))

from numerical_encode import (
    load_ensemble, ensemble_to_matrix,
    encode_ordinal, encode_zero_centered, encode_normalized, encode_crystal_address,
    compute_correlation_matrix, compute_primitive_distribution,
    compute_tier_distribution, compute_cooccurrence, kmeans_cluster,
    detect_absorbing_signatures, filter_valid_entries,
    PRIM_KEYS, CARDINALITY, CANONICAL_VALUES, GLYPH_INDEX, ORDINALS,
    AbsorptionRule, CANONICAL_ABSORPTION, encode_absorbing,
)
from imscrbgrmr.canonical_primitives import ouroboricity_tier, CrystalAddress

# ── Load & Filter ──────────────────────────────────────────
print("=" * 90)
print("NUMERICAL ENSEMBLE ANALYSIS — Imscribing Grammar Catalog")
print("=" * 90)

raw_entries = load_ensemble()
entries = filter_valid_entries(raw_entries)
n = len(entries)
print(f"\nLoaded {n} valid catalog entries (filtered from {len(raw_entries)}).")

# ── 1. TIER DISTRIBUTION ────────────────────────────────────
print("\n── 1. OUROBORICITY TIER DISTRIBUTION ──")
tier_dist = compute_tier_distribution(entries)
for tier in ["O_0", "O_1", "O_2", "O_2†", "O_inf"]:
    cnt = tier_dist["counts"].get(tier, 0)
    pct = cnt / n * 100
    bar = "█" * int(pct / 2)
    print(f"  {tier:<8} {cnt:>5}  ({pct:5.1f}%)  {bar}")

# ── 2. PRIMITIVE VALUE DISTRIBUTION ─────────────────────────
print("\n── 2. PRIMITIVE VALUE DISTRIBUTION (ordinal encoding) ──")
matrix_ord, labels = ensemble_to_matrix(entries, scheme="ordinal")
dist = compute_primitive_distribution(matrix_ord)
print(f"  {'Prim':<5} {'Mean':>6} {'Min':>4} {'Max':>4} {'Coverage':>9} {'Most Common':>30}")
print(f"  {'-'*4:<5} {'-'*5:>6} {'-'*3:>4} {'-'*3:>4} {'-'*8:>9} {'-'*29:>30}")
for p in PRIM_KEYS:
    d = dist[p]
    mc_str = ", ".join(f"{v}({c})" for v, c in d["most_common"])
    print(f"  {p:<5} {d['mean']:6.2f} {d['min']:4.0f} {d['max']:4.0f} {d['coverage']:8.1%}  {mc_str:<30}")

# ── 3. CORRELATION MATRIX ───────────────────────────────────
print("\n── 3. PRIMITIVE CORRELATIONS (ordinal) ──")
corr = compute_correlation_matrix(matrix_ord)
print("  Strongest positive correlations:")
for a, b, r in corr["strongest_positive"]:
    print(f"    {a} ↔ {b}:  r = {r:+.3f}")
print("  Strongest negative correlations:")
for a, b, r in corr["strongest_negative"]:
    print(f"    {a} ↔ {b}:  r = {r:+.3f}")

print("\n  Full 12×12 correlation matrix:")
header = "        " + "".join(f"  {p:>4}" for p in PRIM_KEYS)
print(header)
for i, p_i in enumerate(PRIM_KEYS):
    row = f"  {p_i:>4} |" + "".join(f" {corr['correlation_matrix'][i][j]:+5.2f}" for j in range(12))
    print(row)

# ── 4. CO-OCCURRENCE / DETERMINISTIC PAIRS ──────────────────
print("\n── 4. DETERMINISTIC PRIMITIVE PAIRS ──")
cooc = compute_cooccurrence(entries)
print(f"  Found {len(cooc['strong_deterministic_pairs'])} pairs with ≥60% determinism:")
for pair in cooc["strong_deterministic_pairs"][:25]:
    g_a, a_val = pair["given"]
    g_b, b_val = pair["predicts"]
    print(f"    Given {g_a}={a_val} → {g_b}={b_val}  ({pair['confidence']:.0%}, n={pair['sample_size']})")

# ── 5. ABSORBING SIGNATURES ─────────────────────────────────
print("\n── 5. ABSORBING SIGNATURE DETECTION (canonical rules) ──")
absig = detect_absorbing_signatures(entries)
s = absig["summary"]
print(f"  ⊙=⊙ (self-modeling gate):   {s['absorb_phi_only']:>5} entries")
print(f"  Σ=𐑳 (n:m stoichiometry):    {s['absorb_sigma_only']:>5} entries")
print(f"  Both absorbing:              {s['absorb_both']:>5} entries")
print(f"  Neither absorbing:           {s['absorb_neither']:>5} entries")
print(f"  Any absorbing:               {s['any_absorbing']:>5} entries ({s['any_absorbing']/n*100:.1f}%)")

# ── 6. ZERO-CENTERED VIEW ───────────────────────────────────
print("\n── 6. ZERO-CENTERED ENSEMBLE VIEW ──")
matrix_zc, _ = ensemble_to_matrix(entries, scheme="zero_centered")
print(f"  {'Prim':<5} {'Mean':>8} {'Std':>8} {'Mode':>5} {'Range':>18}")
for j, p in enumerate(PRIM_KEYS):
    vals = [row[j] for row in matrix_zc]
    mean = sum(vals) / n
    std = (sum((v - mean)**2 for v in vals) / n) ** 0.5
    cnt = Counter(vals)
    mode_val, mode_cnt = cnt.most_common(1)[0]
    print(f"  {p:<5} {mean:8.3f} {std:8.3f} {int(mode_val):5d}  [{min(vals):.0f} .. {max(vals):.0f}] (mode: {mode_cnt})")

# ── 7. CLUSTERING ───────────────────────────────────────────
print("\n── 7. K-MEANS CLUSTERING (k=7, ordinal encoding) ──")
km = kmeans_cluster(matrix_ord, k=7)
print(f"  Cluster sizes: {km['cluster_sizes']}")
print(f"  Converged in {km['iterations']} iterations.")
print("  Cluster centroids (ordinal values):")
for c in range(7):
    cent = km['centroids'][c]
    centroid_str = " ".join(f"{cent[j]:5.2f}" for j in range(12))
    print(f"    C{c}: [{centroid_str}]")

# Show top entries per cluster
print("\n  Top entries per cluster:")
cluster_entries = {c: [] for c in range(7)}
for i, e in enumerate(entries):
    c = km['assignments'][i]
    cluster_entries[c].append(e.get('name', '?'))
for c in range(7):
    names = cluster_entries[c][:8]
    print(f"    C{c} ({len(cluster_entries[c])}): {', '.join(names)}")

# ── 8. CRYSTAL ADDRESS RANGE ─────────────────────────────────
print("\n── 8. CRYSTAL ADDRESS DISTRIBUTION ──")
addrs = [encode_crystal_address(e) for e in entries]
print(f"  Min address:  {min(addrs):>9,}")
print(f"  Max address:  {max(addrs):>9,}")
print(f"  Range:        {max(addrs)-min(addrs):>9,}")
print(f"  Full crystal: {17_280_000:>9,} (3³×4⁵×5⁴)")
print(f"  Coverage:     {len(set(addrs))/17_280_000*100:.4f}%")
print(f"  Unique addrs: {len(set(addrs))} / {n} entries")

# ── 9. CLAY PROBLEMS IN NUMERICAL VIEW ────────────────────────
print("\n── 9. CLAY MILLENNIUM PROBLEMS — NUMERICAL VIEW ──")
CLAY_NAMES = [
    'riemann_hypothesis', 'yang_mills_mass_gap', 'navier_stokes',
    'hodge_conjecture', 'birch_swinnerton_dyer', 'p_vs_np',
    'poincare_conjecture'
]
clay_entries = [e for e in entries if e.get("name") in CLAY_NAMES]
if clay_entries:
    print(f"  Found {len(clay_entries)}/7 Clay problems in catalog.")
    print(f"  {'Problem':<30} {'Crystal Addr':>10} {'Tier':<8} {'Ordinal Vector'}")
    print(f"  {'-'*29:>30} {'-'*9:>10} {'-'*7:<8} {'-'*70}")
    for e in clay_entries:
        name = e.get("name", "?")
        addr = encode_crystal_address(e)
        tier = ouroboricity_tier(CrystalAddress.from_dict(e))
        vec = encode_ordinal(e)
        vec_str = " ".join(f"{v:4.0f}" for v in vec)
        print(f"  {name:<30} {addr:>10,} {tier:<8} [{vec_str}]")

# ── 10. ABSORBING ENCODING: CLAY PROBLEMS ─────────────────────
print("\n── 10. ABSORBING-ENCODED CLAY PROBLEMS (negative = absorber) ──")
clay_absorbing = [encode_absorbing(e, CANONICAL_ABSORPTION, "tensor") for e in clay_entries]
print(f"  {'Problem':<30} {'Absorbing Vector (neg=absorber)'}")
print(f"  {'-'*29:>30} {'-'*60}")
for i, e in enumerate(clay_entries):
    name = e.get("name", "?")
    vec_str = " ".join(f"{v:+5.0f}" for v in clay_absorbing[i])
    print(f"  {name:<30} [{vec_str}]")

# ── 11. ENSEMBLE-WIDE PATTERNS ──────────────────────────────
print("\n── 11. ENSEMBLE-WIDE PATTERN SUMMARY ──")
all_vals_usage = {}
for p in PRIM_KEYS:
    vals = [e[p] for e in entries]
    cnt = Counter(vals)
    all_vals_usage[p] = cnt

print("  Most-used value per primitive:")
for p in PRIM_KEYS:
    mc = all_vals_usage[p].most_common(1)[0]
    print(f"    {p}: {mc[0]} ({mc[1]}/{n}, {mc[1]/n*100:.1f}%)")

print("  Least-used value per primitive:")
for p in PRIM_KEYS:
    lc = all_vals_usage[p].most_common()[-1]
    print(f"    {p}: {lc[0]} ({lc[1]}/{n}, {lc[1]/n*100:.1f}%)")

# ── 12. VECTOR SPACE PROPERTIES ──────────────────────────────
print("\n── 12. VECTOR SPACE PROPERTIES ──")
mean_vec = [sum(row[j] for row in matrix_ord) / n for j in range(12)]
print(f"  Ensemble centroid: [{' '.join(f'{v:5.2f}' for v in mean_vec)}]")

print(f"\n  Distance of Clay problems from ensemble centroid:")
for e in clay_entries:
    vec = encode_ordinal(e)
    name = e.get("name", "?")
    dist = sum((vec[j] - mean_vec[j])**2 for j in range(12)) ** 0.5
    print(f"    {name:<30}  d = {dist:.3f}")

# ── 13. TIER-BY-VALUE BREAKDOWN ──────────────────────────────
print("\n── 13. TIER-BY-VALUE: PRIMITIVE ENRICHMENT ──")
# For each tier, compute mean ordinal value per primitive
tier_groups = {"O_0": [], "O_1": [], "O_2": [], "O_2†": [], "O_inf": []}
for e in entries:
    tier = ouroboricity_tier(CrystalAddress.from_dict(e))
    vec = encode_ordinal(e)
    tier_groups[tier].append(vec)

print(f"  {'Tier':<8} " + " ".join(f"{p:>5}" for p in PRIM_KEYS))
for tier in ["O_0", "O_1", "O_2", "O_2†", "O_inf"]:
    if tier_groups[tier]:
        avg = [sum(row[j] for row in tier_groups[tier]) / len(tier_groups[tier]) for j in range(12)]
        print(f"  {tier:<8} " + " ".join(f"{v:5.2f}" for v in avg))

# ── 14. PRIMITIVE COVERAGE GAPS ──────────────────────────────
print("\n── 14. PRIMITIVE VALUE USAGE GAPS ──")
for p in PRIM_KEYS:
    used_vals = set(e[p] for e in entries)
    all_vals = set(CANONICAL_VALUES[p])
    unused = all_vals - used_vals
    if unused:
        print(f"  {p}: UNUSED values: {unused}")
    else:
        print(f"  {p}: All {len(all_vals)} values used ✓")

print("\n" + "=" * 90)
print("ENSEMBLE ANALYSIS COMPLETE")
print("=" * 90)
