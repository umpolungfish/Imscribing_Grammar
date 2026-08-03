#!/usr/bin/env python3
"""
Numerical Encoding Engine — Converts any IG catalog entry to a 12-vector
under multiple encoding schemes. This is the foundation layer for gematria.
"""
import sys, json, math
from pathlib import Path
from collections import OrderedDict
from typing import Dict, List, Tuple, Optional, Union

# ── Primitive → Glyph → Ordinal (canonical IG ordering) ──────────
PRIMITIVES = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '◻']
PRIM_CARDINALITIES = {'⊢': 4, '⊣': 5, '>': 4, '<': 5, '⋈': 3, '⊤': 5, '∈': 3, '∋': 4, '⊙': 5, '⊥': 4, '⊞': 3, '◻': 4}

# Glyph → ordinal (1-based)
GLYPH_ORDINALS: Dict[str, Dict[str, int]] = {
    '⊢': {'𐑛': 1, '𐑨': 2, '𐑼': 3, '𐑦': 4},
    '⊣': {'𐑡': 1, '𐑰': 2, '𐑥': 3, '𐑶': 4, '𐑸': 5},
    '>': {'𐑩': 1, '𐑑': 2, '𐑽': 3, '𐑾': 4},
    '<': {'𐑗': 1, '𐑿': 2, '𐑬': 3, '𐑯': 4, '𐑹': 5},
    '⋈': {'𐑱': 1, '𐑞': 2, '𐑐': 3},
    '⊤': {'𐑺': 1, '𐑪': 2, '𐑧': 3, '𐑤': 4, '𐑘': 5},
    '∈': {'𐑲': 1, '𐑚': 2, '𐑔': 3},
    '∋': {'𐑝': 1, '𐑜': 2, '𐑠': 3, '𐑵': 4},
    '⊙': {'𐑢': 1, '⊙': 2, '𐑮': 3, '𐑻': 4, '𐑣': 5},
    '⊥': {'𐑓': 1, '𐑒': 2, '𐑖': 3, '𐑫': 4},
    '⊞': {'𐑙': 1, '𐑕': 2, '𐑳': 3},
    '◻': {'𐑷': 1, '𐑴': 2, '𐑭': 3, '𐑟': 4},
}

ORDINAL_GLYPHS = {p: {v: k for k, v in m.items()} for p, m in GLYPH_ORDINALS.items()}

IG_TO_SHAVIAN = {
    '𐑦': '𐑦', '𐑛': '𐑼', '𐑨': '𐑨', '𐑼': '𐑛',
    '𐑸': '𐑸', '𐑰': '𐑰', '𐑥': '𐑥', '𐑡': '𐑡', '𐑶': '𐑶',
    '𐑾': '𐑾', '𐑽': '𐑩', '𐑩': '𐑑', '𐑑': '𐑽',
    '𐑹': '𐑹', '𐑬': '𐑯', '𐑿': '𐑬', '𐑯': '𐑿', '𐑗': '𐑗',
    '𐑐': '𐑐', '𐑱': '𐑱', '𐑞': '𐑞',
    '𐑧': '𐑧', '𐑤': '𐑪', '𐑘': '𐑺', '𐑪': '𐑘', '𐑺': '𐑤',
    '𐑲': '𐑲', '𐑔': '𐑚', '𐑚': '𐑔',
    '𐑠': '𐑠', '𐑵': '𐑜', '𐑝': '𐑝', '𐑜': '𐑵',
    '⊙': '⊙', '𐑮': '𐑮', '𐑻': '𐑻', '𐑢': '𐑢', '𐑣': '𐑣',
    '𐑖': '𐑖', '𐑫': '𐑫', '𐑓': '𐑓', '𐑒': '𐑒',
    '𐑙': '𐑙', '𐑕': '𐑕', '𐑳': '𐑳',
    '𐑭': '𐑭', '𐑴': '𐑴', '𐑷': '𐑷', '𐑟': '𐑟',
}

# ── Resolver ─────────────────────────────────────────────────────

def _resolve_glyph(entry: Dict, primitive: str) -> str:
    """Get the Shavian glyph for a primitive, handling IG notation."""
    val = entry.get(primitive, '')
    if val is None:
        val = ''
    if val in GLYPH_ORDINALS.get(primitive, {}):
        return val
    if val in IG_TO_SHAVIAN:
        return IG_TO_SHAVIAN[val]
    for ig_key, shav in IG_TO_SHAVIAN.items():
        if val == ig_key or (primitive + '_' in ig_key and val in ig_key):
            return shav
    if isinstance(val, str) and len(val) >= 3:
        for ig_key, shav in IG_TO_SHAVIAN.items():
            if ig_key in val or val in ig_key:
                return shav
    return ''

def resolve_all(entry: Dict) -> Dict[str, str]:
    """Resolve all 12 primitives to Shavian glyphs."""
    return {p: _resolve_glyph(entry, p) for p in PRIMITIVES}

def is_valid_entry(entry: Dict) -> bool:
    """Check if entry has resolvable values for all 12 primitives."""
    for p in PRIMITIVES:
        if _resolve_glyph(entry, p) == '':
            return False
    return True

# ── Encoding schemes ─────────────────────────────────────────────

def encode_ordinal(entry: Dict) -> List[float]:
    """1-based ordinal encoding. Range: [1, cardinality]."""
    vec = []
    for p in PRIMITIVES:
        g = _resolve_glyph(entry, p)
        vec.append(float(GLYPH_ORDINALS[p].get(g, 0)))
    return vec

def encode_zero_centered(entry: Dict) -> List[float]:
    """Zero-centered encoding. 3-values: -1,0,1. 4-values: -1.5,-0.5,0.5,1.5. 5-values: -2,-1,0,1,2."""
    vec = []
    for p in PRIMITIVES:
        g = _resolve_glyph(entry, p)
        o = GLYPH_ORDINALS[p].get(g, 0)
        c = PRIM_CARDINALITIES[p]
        if c == 3:
            vec.append(float(o - 2))
        elif c == 4:
            vec.append(float(o - 2.5))
        elif c == 5:
            vec.append(float(o - 3))
        else:
            vec.append(0.0)
    return vec

def encode_normalized(entry: Dict) -> List[float]:
    """Min-max normalized to [0, 1] range."""
    vec = []
    for p in PRIMITIVES:
        g = _resolve_glyph(entry, p)
        o = GLYPH_ORDINALS[p].get(g, 0)
        c = PRIM_CARDINALITIES[p]
        if c > 1:
            vec.append((o - 1) / (c - 1))
        else:
            vec.append(0.0)
    return vec

def encode_crystal_address(entry: Dict) -> int:
    """Frobenius crystal address 0..17279999 (4×5×4×5×3×5×3×4×5×4×3×4 - 1)."""
    ranges = [4, 5, 4, 5, 3, 5, 3, 4, 5, 4, 3, 4]
    addr = 0
    multiplier = 1
    for p, r in zip(PRIMITIVES, ranges):
        g = _resolve_glyph(entry, p)
        o = GLYPH_ORDINALS[p].get(g, 0) - 1
        addr += o * multiplier
        multiplier *= r
    return addr

def encode_absorbing(entry: Dict, absorbing_prims: List[str], absorbing_vals: List[str]) -> List[float]:
    """Encoding where absorbing primitives get negative values."""
    base = encode_ordinal(entry)
    for i, p in enumerate(PRIMITIVES):
        g = _resolve_glyph(entry, p)
        if p in absorbing_prims and g in absorbing_vals:
            base[i] = -abs(base[i])
    return base

def encode_integer_compact(entry: Dict) -> List[int]:
    """Integer encoding: 0..max-1 for each primitive."""
    vec = []
    for p in PRIMITIVES:
        g = _resolve_glyph(entry, p)
        o = GLYPH_ORDINALS[p].get(g, 0)
        vec.append(o - 1)
    return vec

# ── Vector algebra ───────────────────────────────────────────────

def vec_add(a: List[float], b: List[float]) -> List[float]:
    return [x + y for x, y in zip(a, b)]

def vec_sub(a: List[float], b: List[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]

def vec_hadamard(a: List[float], b: List[float]) -> List[float]:
    """Element-wise product."""
    return [x * y for x, y in zip(a, b)]

def vec_dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

def vec_norm(v: List[float]) -> float:
    return math.sqrt(sum(x*x for x in v))

def vec_cosine(a: List[float], b: List[float]) -> float:
    na, nb = vec_norm(a), vec_norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return vec_dot(a, b) / (na * nb)

def vec_l1(a: List[float], b: List[float]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))

def vec_l2(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y)**2 for x, y in zip(a, b)))

def vec_mean(vectors: List[List[float]]) -> List[float]:
    n = len(vectors)
    if n == 0:
        return [0.0] * 12
    return [sum(v[i] for v in vectors) / n for i in range(12)]

def vec_to_closest_glyph(v: List[float], scheme: str = 'ordinal') -> Dict[str, str]:
    """Snap a real-valued vector back to the nearest valid glyph tuple."""
    result = {}
    for i, p in enumerate(PRIMITIVES):
        c = PRIM_CARDINALITIES[p]
        if scheme == 'ordinal':
            target = max(1, min(c, round(v[i])))
        elif scheme == 'zero_centered':
            if c == 3:
                target_raw = max(-1, min(1, round(v[i])))
                target = target_raw + 2
            elif c == 4:
                target_raw = max(-1.5, min(1.5, round(v[i] * 2) / 2))
                target = int(target_raw + 2.5)
            elif c == 5:
                target_raw = max(-2, min(2, round(v[i])))
                target = target_raw + 3
            else:
                target = 1
        elif scheme == 'normalized':
            target = max(1, min(c, round(v[i] * (c - 1)) + 1))
        else:
            target = max(1, min(c, round(v[i])))
        result[p] = ORDINAL_GLYPHS[p].get(target, list(GLYPH_ORDINALS[p].keys())[0])
    return result

# ── Batch encoding ───────────────────────────────────────────────

def encode_catalog(entries: List[Dict], scheme: str = 'ordinal') -> Tuple[List[List[float]], List[str], List[Dict]]:
    """Encode all valid entries in a catalog. Returns (vectors, names, entries)."""
    vectors, names, valid_entries = [], [], []
    for e in entries:
        if is_valid_entry(e):
            if scheme == 'ordinal':
                v = encode_ordinal(e)
            elif scheme == 'zero_centered':
                v = encode_zero_centered(e)
            elif scheme == 'normalized':
                v = encode_normalized(e)
            elif scheme == 'integer_compact':
                v = [float(x) for x in encode_integer_compact(e)]
            else:
                v = encode_ordinal(e)
            vectors.append(v)
            names.append(e.get('name', 'unknown'))
            valid_entries.append(e)
    return vectors, names, valid_entries

def vector_to_tuple_str(v: List[float], scheme: str = 'ordinal') -> str:
    """Convert a vector back to a human-readable tuple string."""
    glyphs = vec_to_closest_glyph(v, scheme)
    parts = [f"{glyphs[p]}" for p in PRIMITIVES]
    return "⟨" + ";".join(parts) + "⟩"

if __name__ == '__main__':
    print("numerical_encode.py — IG Gematria Engine")
    print(f"  Primitives: {len(PRIMITIVES)}")
    print(f"  Crystal size: 4×5×4×5×3×5×3×4×5×4×3×4 = 17,280,000")
    print(f"  IG→Shavian transcoding entries: {len(IG_TO_SHAVIAN)}")
    # Smoke test
    test = {'⊢': '𐑦', '⊣': '𐑸', '>': '𐑾', '<': '𐑹', '⋈': '𐑐', '⊤': '𐑧',
            '∈': '𐑲', '∋': '𐑠', '⊙': '⊙', '⊥': '𐑖', '⊞': '𐑳', '◻': '𐑭'}
    v = encode_ordinal(test)
    print(f"  Smoke test (RH ordinal): {v}")
    v2 = encode_zero_centered(test)
    print(f"  Smoke test (RH zero-centered): {v2}")
    addr = encode_crystal_address(test)
    print(f"  Smoke test (RH crystal addr): {addr}")
