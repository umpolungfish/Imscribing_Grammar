#!/usr/bin/env python3
"""Explore Clay Millennium Prize problems across all absorption universes."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from imscrbgrmr.registry import load_catalog_dicts
from imscrbgrmr.algebra import meet, join, tensor
from navigators.ruleset_universe import (
    RULESETS, Ruleset, AbsorptionRule, _DEFAULT_ABSORPTION
)
from navigators.crystal_navigator import _resolve_absorption

# ── Load catalog ───────────────────────────────────────────────
catalog_list = load_catalog_dicts()
catalog = {e['name']: e for e in catalog_list}

CLAY_NAMES = [
    'riemann_hypothesis',
    'yang_mills_mass_gap',
    'navier_stokes',
    'hodge_conjecture',
    'birch_swinnerton_dyer',
    'p_vs_np',
    'poincare_conjecture',
]

# ── Extract clay tuples ────────────────────────────────────────
clay_tuples = {}
for name in CLAY_NAMES:
    e = catalog.get(name)
    if e:
        clay_tuples[name] = e
        print(f"{name}: {e['⊢']} {e['⊣']} {e['≻']} {e['≺']} {e['⋈']} {e['⊤']} {e['∈']} {e['∋']} {e['⊙']} {e['⊥']} {e['⊞']} {e['⊡']}")
    else:
        print(f"WARNING: {name} not found")

# ── Define absorption universes ────────────────────────────────
NEW_RULESETS_ABSORPTION = [
    # Canonical (baseline)
    ("canonical", _DEFAULT_ABSORPTION),
    # 22: democracy
    ("democracy", ()),
    # 23: monarchy
    ("monarchy", (
        AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
        AbsorptionRule("⊞", "𐑳", ("meet", "join", "tensor")),
        AbsorptionRule("≺", "𐑹", ("meet", "join", "tensor")),
        AbsorptionRule("⊡", "𐑭", ("meet", "join", "tensor")),
    )),
    # 24: inverted
    ("inverted", (
        AbsorptionRule("⊙", "𐑢", ("meet", "join", "tensor")),
        AbsorptionRule("⊡", "𐑷", ("meet", "join", "tensor")),
        AbsorptionRule("⊞", "𐑙", ("meet", "join", "tensor")),
    )),
    # 25: tensor_only
    ("tensor_only", (
        AbsorptionRule("⊙", "⊙", ("tensor",)),
        AbsorptionRule("⊞", "𐑳", ("tensor",)),
    )),
    # 26: chirality_first
    ("chirality_first", (
        AbsorptionRule("⊥", "𐑫", ("meet", "join", "tensor")),
        AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
        AbsorptionRule("⊞", "𐑳", ("tensor",)),
    )),
    # 27: scope_empire
    ("scope_empire", (
        AbsorptionRule("∈", "𐑔", ("meet", "join", "tensor")),
        AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
        AbsorptionRule("⊞", "𐑳", ("tensor",)),
    )),
    # 28: topology_seal
    ("topology_seal", (
        AbsorptionRule("⊣", "𐑸", ("meet", "join", "tensor")),
        AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
        AbsorptionRule("⊞", "𐑳", ("tensor",)),
    )),
]

# ── Convert absorption rules to dict format ────────────────────
def abs_to_dict(abs_rules):
    """Convert AbsorptionRule tuples to the dict format _resolve_absorption expects."""
    d = {}
    for rule in abs_rules:
        if isinstance(rule, tuple):
            prim, val, ops = rule
        else:
            prim, val, ops = rule.primitive, rule.value, rule.operations
        d[prim] = (val, tuple(ops))
    return d

# ── Map letters to ordinals ────────────────────────────────────
SHORT_TO_FULL = {
    'D': '⊢', 'T': '⊣', 'R': '≻', 'P': '≺', 'F': '⋈',
    'K': '⊤', 'G': '∈', 'A': '∋', 'C': '⊙', 'H': '⊥',
    'S': '⊞', 'W': '⊡',
}

# Standard ordinal values (approximate for primitive comparison)
ORDINALS = {
    '⊢': {'𐑛': 1, '𐑨': 2, '𐑼': 3, '𐑦': 4},
    '⊣': {'𐑡': 1, '𐑰': 2, '𐑥': 3, '𐑶': 4, '𐑸': 5},
    '≻': {'𐑩': 1, '𐑑': 2, '𐑽': 3, '𐑾': 4},
    '≺': {'𐑗': 1, '𐑿': 2, '𐑬': 3, '𐑯': 4, '𐑹': 5},
    '⋈': {'𐑱': 1, '𐑞': 2, '𐑐': 3},
    '⊤': {'𐑺': 1, '𐑪': 2, '𐑧': 3, '𐑤': 4, '𐑘': 5},
    '∈': {'𐑲': 1, '𐑚': 2, '𐑔': 3},
    '∋': {'𐑝': 1, '𐑜': 2, '𐑠': 3, '𐑵': 4},
    '⊙': {'𐑢': 1, '⊙': 2, '𐑮': 3, '𐑻': 4, '𐑣': 5},
    '⊥': {'𐑓': 1, '𐑒': 2, '𐑖': 3, '𐑫': 4},
    '⊞': {'𐑙': 1, '𐑕': 2, '𐑳': 3},
    '⊡': {'𐑷': 1, '𐑴': 2, '𐑭': 3, '𐑟': 4},
}

PRIM_KEYS = ['⊢', '⊣', '≻', '≺', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '⊡']

def apply_absorption(tup, abs_dict, op):
    """Apply absorption rules to a tuple. Returns absorbed tuple."""
    result = dict(tup)
    for prim_key, (abs_val, ops) in abs_dict.items():
        if op in ops:
            if tup.get(prim_key) == abs_val:
                for pk in PRIM_KEYS:
                    result[pk] = abs_val
                return result
    return result

def tensor_with_absorption(tup_a, tup_b, abs_dict):
    """Compute tensor with absorption applied."""
    # First apply absorption under tensor
    a_abs = apply_absorption(dict(tup_a), abs_dict, 'tensor')
    b_abs = apply_absorption(dict(tup_b), abs_dict, 'tensor')
    
    # Then do element-wise max for tensor (standard definition)
    result = {}
    for pk in PRIM_KEYS:
        a_val = a_abs.get(pk, tup_a.get(pk))
        b_val = b_abs.get(pk, tup_b.get(pk))
        a_ord = ORDINALS[pk].get(a_val, 0)
        b_ord = ORDINALS[pk].get(b_val, 0)
        max_ord = max(a_ord, b_ord)
        # Find the glyph with this ordinal
        for glyph, ordv in ORDINALS[pk].items():
            if ordv == max_ord:
                result[pk] = glyph
                break
        else:
            result[pk] = a_val  # fallback
    
    # Then re-apply absorption on result
    result_abs = apply_absorption(result, abs_dict, 'tensor')
    return result_abs

def tuple_to_str(tup):
    return f"⟨{tup['⊢']};{tup['⊣']};{tup['≻']};{tup['≺']};{tup['⋈']};{tup['⊤']};{tup['∈']};{tup['∋']};{tup['⊙']};{tup['⊥']};{tup['⊞']};{tup['⊡']}⟩"

def tuple_diff_count(a, b):
    return sum(1 for pk in PRIM_KEYS if a[pk] != b[pk])

SHORT = {
    'riemann_hypothesis': 'RH',
    'yang_mills_mass_gap': 'YM',
    'navier_stokes': 'NS',
    'hodge_conjecture': 'HC',
    'birch_swinnerton_dyer': 'BSD',
    'p_vs_np': 'PNP',
    'poincare_conjecture': 'PC',
}

print("\n" + "=" * 100)
print("CLAY MILLENNIUM PROBLEMS — ABSORPTION UNIVERSE ANALYSIS")
print("=" * 100)

# ── 1. Baseline: show each Clay problem's primitives in readable notation ──
print("\n── 1. CLAY PROBLEM TUPLES (canonical) ──")
print(f"{'Problem':<6} {'⊢':<4} {'⊣':<4} {'≻':<4} {'≺':<4} {'⋈':<4} {'⊤':<4} {'∈':<4} {'∋':<4} {'⊙':<4} {'⊥':<4} {'⊞':<4} {'⊡':<4}")
print("-" * 70)
for name in CLAY_NAMES:
    t = clay_tuples[name]
    print(f"{SHORT[name]:<6} {t['⊢']:<4} {t['⊣']:<4} {t['≻']:<4} {t['≺']:<4} {t['⋈']:<4} {t['⊤']:<4} {t['∈']:<4} {t['∋']:<4} {t['⊙']:<4} {t['⊥']:<4} {t['⊞']:<4} {t['⊡']:<4}")

# ── 2. Pairwise distances (canonical) ──
print("\n── 2. PAIRWISE DISTANCES (canonical, primitive diffs) ──")
print(f"{'':>6}", end="")
for name in CLAY_NAMES:
    print(f" {SHORT[name]:>4}", end="")
print()
for a_name in CLAY_NAMES:
    print(f"{SHORT[a_name]:>6}", end="")
    for b_name in CLAY_NAMES:
        d = tuple_diff_count(clay_tuples[a_name], clay_tuples[b_name])
        print(f" {d:>4}", end="")
    print()

# ── 3. Absorption universe analysis ──
print("\n" + "=" * 100)
print("── 3. TENSOR PRODUCT ANALYSIS ACROSS ABSORPTION UNIVERSES ──")
print("=" * 100)

for abs_name, abs_rules in NEW_RULESETS_ABSORPTION:
    abs_dict = abs_to_dict(abs_rules)
    
    print(f"\n{'─'*80}")
    print(f"UNIVERSE: {abs_name}")
    if abs_rules:
        for r in abs_rules:
            if isinstance(r, tuple):
                prim, val, ops = r
            else:
                prim, val, ops = r.primitive, r.value, r.operations
            print(f"  {prim}={val} absorbs under {','.join(ops)}")
    else:
        print("  NO ABSORPTION (democratic)")
    
    # Compute all pairwise tensors
    print(f"\n  Pairwise tensor products (max ordinal per primitive):")
    print(f"  {'':>6}", end="")
    for name in CLAY_NAMES:
        print(f" {SHORT[name]:>5}", end="")
    print(f"  {'unique':>7}")
    print(f"  {'─'*60}")
    
    n_unique = 0
    seen = set()
    for a_name in CLAY_NAMES:
        print(f"  {SHORT[a_name]:>6}", end="")
        for b_name in CLAY_NAMES:
            tup_result = tensor_with_absorption(clay_tuples[a_name], clay_tuples[b_name], abs_dict)
            # Count unique primitives in the result (how "rich" is the composite)
            richness = sum(ORDINALS[pk].get(tup_result[pk], 0) for pk in PRIM_KEYS)
            tuphash = tuple(tup_result[pk] for pk in PRIM_KEYS)
            seen.add(tuphash)
            # Show how many primitives are at max value
            max_count = sum(1 for pk in PRIM_KEYS if ORDINALS[pk].get(tup_result[pk], 0) == max(ORDINALS[pk].values()))
            print(f" {richness:>5}", end="")
        print()
    
    # Show unique composite types
    print(f"\n  Unique composite types: {len(seen)}")
    for i, comp in enumerate(sorted(seen)):
        s = "⟨" + ";".join(comp) + "⟩"
        if i < 5:
            print(f"    {s}")
    if len(seen) > 5:
        print(f"    ... and {len(seen)-5} more")
    
    # Which Clay problem dominates (most absorbing power)?
    print(f"\n  Dominance analysis (how many other problems does each absorb into itself):")
    for a_name in CLAY_NAMES:
        absorbed_count = 0
        for b_name in CLAY_NAMES:
            if a_name == b_name:
                continue
            tup_res = tensor_with_absorption(clay_tuples[a_name], clay_tuples[b_name], abs_dict)
            diffs = tuple_diff_count(tup_res, clay_tuples[a_name])
            if diffs == 0:
                absorbed_count += 1
        print(f"    {SHORT[a_name]}: absorbs {absorbed_count}/6 others")

# ── 4. Special: which clay problems survive absorption under each universe ──
print("\n" + "=" * 100)
print("── 4. SURVIVAL ANALYSIS: WHICH CLAY PROBLEMS RETAIN THEIR IDENTITY ──")
print("=" * 100)

for abs_name, abs_rules in NEW_RULESETS_ABSORPTION:
    abs_dict = abs_to_dict(abs_rules)
    
    print(f"\n  Universe: {abs_name}")
    
    # For each Clay problem, check if it self-absorbs (tensor with self = self?)
    # And if other problems absorb it
    survivors = []
    for name in CLAY_NAMES:
        t = clay_tuples[name]
        # Check self-tensor
        self_tensor = tensor_with_absorption(t, t, abs_dict)
        self_same = tuple_diff_count(self_tensor, t) == 0
        
        # Check: how many others does it survive coupling with?
        survived = 0
        absorbed_by_other = 0
        for other_name in CLAY_NAMES:
            if other_name == name:
                continue
            tup_res = tensor_with_absorption(t, clay_tuples[other_name], abs_dict)
            # If result matches the other, we got absorbed
            if tuple_diff_count(tup_res, clay_tuples[other_name]) == 0 and tuple_diff_count(tup_res, t) != 0:
                absorbed_by_other += 1
            elif tuple_diff_count(tup_res, t) == 0:
                survived += 1
        
        status = "✓ self-stable" if self_same else "× self-absorbing"
        print(f"    {SHORT[name]:>5}: {status} | survives {survived}/{len(CLAY_NAMES)-1} couplings | absorbed by {absorbed_by_other}")

print("\n" + "=" * 100)
print("── 5. KEY INSIGHTS ──")
print("=" * 100)
