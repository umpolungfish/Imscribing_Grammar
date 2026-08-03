#!/usr/bin/env python3
"""
Numerical Encoder for Imscribing Grammar Catalog Entries.

Converts any catalog entry (12 Shavian glyphs) into numerical vectors.
Supports multiple encoding schemes:

  1. ORDINAL (1-based): Each glyph → its ordinal position (1..cardinality)
  2. ZERO_CENTERED: Centered integers, e.g. 5-value → [-2,-1,0,1,2]
  3. ABSORBING: Negative values for absorbing primitives under given ruleset
  4. NORMALIZED: [0,1] normalized per primitive
  5. CRYSTAL: Single integer 0..17279999 (Frobenius address)

Author: Lando⊗⊙perator
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
import json

# ── Add parent to path ─────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))

from imscrbgrmr.canonical_primitives import (
    PRIMITIVE_ORDER, CANONICAL_VALUES, ORDINALS, WEIGHTS, CrystalAddress
)

PRIM_KEYS: List[str] = PRIMITIVE_ORDER  # ["⊢","⊣",">","<","⋈","⊤","∈","∋","⊙","⊥","⊞","◻"]

# ── Cardinality per primitive ──────────────────────────────────
CARDINALITY: Dict[str, int] = {p: len(vals) for p, vals in CANONICAL_VALUES.items()}

# ── Glyph → index mapping (0-based within each primitive) ─────
GLYPH_INDEX: Dict[str, Dict[str, int]] = {
    p: {g: i for i, g in enumerate(vals)}
    for p, vals in CANONICAL_VALUES.items()
}

# ── Reverse mapping: index → glyph ─────────────────────────────
INDEX_GLYPH: Dict[str, Dict[int, str]] = {
    p: {i: g for g, i in gmap.items()}
    for p, gmap in GLYPH_INDEX.items()
}


# ═══════════════════════════════════════════════════════════════
# ENCODING SCHEMES
# ═══════════════════════════════════════════════════════════════

def encode_ordinal(entry: dict) -> List[float]:
    """1-based ordinal: glyph → its ordinal rank (1..cardinality)."""
    return [ORDINALS[p][entry[p]] for p in PRIM_KEYS]


def encode_zero_centered(entry: dict) -> List[float]:
    """Zero-centered integer encoding. 
    3-value: [-1, 0, 1]; 4-value: [-2, -1, 1, 2]; 5-value: [-2, -1, 0, 1, 2]
    The '0' position is the middle value for odd cardinalities;
    for even cardinalities it skips 0.
    """
    result = []
    for p in PRIM_KEYS:
        idx = GLYPH_INDEX[p][entry[p]]
        card = CARDINALITY[p]
        if card % 2 == 0:
            # Even: skip 0. Map 0→-card//2, ..., card//2-1 → -1, card//2 → 1, ... card-1 → card//2
            mid = card // 2
            if idx < mid:
                result.append(float(idx - mid))
            else:
                result.append(float(idx - mid + 1))
        else:
            # Odd: 0 is the middle
            mid = card // 2
            result.append(float(idx - mid))
    return result


def encode_normalized(entry: dict) -> List[float]:
    """Each primitive normalized to [0, 1] range."""
    result = []
    for p in PRIM_KEYS:
        idx = GLYPH_INDEX[p][entry[p]]
        card = CARDINALITY[p]
        result.append(idx / (card - 1) if card > 1 else 0.0)
    return result


def encode_crystal_address(entry: dict) -> int:
    """Frobenius address: single integer 0..17279999.
    Mixed-radix: d0*m1*m2*... + d1*m2*m3*... + ... + d11
    where d_i = GLYPH_INDEX[p_i][value_i] and m_i = CARDINALITY[p_i]
    """
    addr = 0
    multiplier = 1
    # Process in reverse order (least significant first)
    for p in reversed(PRIM_KEYS):
        idx = GLYPH_INDEX[p][entry[p]]
        addr += idx * multiplier
        multiplier *= CARDINALITY[p]
    return addr


def decode_crystal_address(addr: int) -> Dict[str, str]:
    """Decode Frobenius address back to glyph dict."""
    result = {}
    remaining = addr
    # Process in reverse order
    for p in reversed(PRIM_KEYS):
        card = CARDINALITY[p]
        idx = remaining % card
        result[p] = INDEX_GLYPH[p][idx]
        remaining //= card
    # Reorder to match PRIM_KEYS
    return {p: result[p] for p in PRIM_KEYS}

# ═══════════════════════════════════════════════════════════════
# ABSORPTION-AWARE ENCODING
# ═══════════════════════════════════════════════════════════════

@dataclass
class AbsorptionRule:
    """Rule: when a primitive has `value`, it absorbs under `operations`."""
    primitive: str       # e.g., "⊙"
    value: str           # e.g., "⊙"
    operations: Tuple[str, ...]  # e.g., ("meet", "join", "tensor")


def encode_absorbing(entry: dict, 
                     absorption_rules: Tuple[AbsorptionRule, ...] = (),
                     operation: str = "tensor") -> List[float]:
    """
    Absorbing-aware encoding. For each primitive in the entry:
      - If the primitive is an absorber (matches a rule) AND operation is in its ops → NEGATIVE ordinal
      - Otherwise → positive ordinal (zero-centered)
    This makes absorbing primitives visually jump out as negative values.
    
    Example: ⊙=⊙ absorbs under tensor → ⊙ gets negative value for that entry.
    """
    # Build absorber set
    absorbers: Dict[str, str] = {}
    for rule in absorption_rules:
        if operation in rule.operations:
            absorbers[rule.primitive] = rule.value
    
    result = []
    for p in PRIM_KEYS:
        val = entry[p]
        idx = GLYPH_INDEX[p][val]
        card = CARDINALITY[p]
        
        if p in absorbers and val == absorbers[p]:
            # Absorbing: negative zero-centered
            if card % 2 == 0:
                mid = card // 2
                if idx < mid:
                    result.append(-float(mid - idx))
                else:
                    result.append(-float(idx - mid + 1))
            else:
                mid = card // 2
                result.append(-float(abs(idx - mid)))
        else:
            # Normal zero-centered
            if card % 2 == 0:
                mid = card // 2
                if idx < mid:
                    result.append(float(idx - mid))
                else:
                    result.append(float(idx - mid + 1))
            else:
                mid = card // 2
                result.append(float(idx - mid))
    return result


# ═══════════════════════════════════════════════════════════════
# CANONICAL ABSORPTION RULES (from new_universes.py)
# ═══════════════════════════════════════════════════════════════

CANONICAL_ABSORPTION: Tuple[AbsorptionRule, ...] = (
    AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
    AbsorptionRule("⊞", "𐑳", ("tensor",)),
)

# ═══════════════════════════════════════════════════════════════
# ENSEMBLE LOADING
# ═══════════════════════════════════════════════════════════════

def load_ensemble(catalog_path: Optional[str] = None) -> List[dict]:
    """Load all catalog entries as dicts. Returns deduplicated list."""
    from imscrbgrmr.registry import load_catalog_dicts
    return load_catalog_dicts(catalog_path)


def ensemble_to_matrix(entries: List[dict], 
                       scheme: str = "ordinal",
                       absorption_rules: Tuple[AbsorptionRule, ...] = (),
                       absorption_op: str = "tensor") -> Tuple[List[List[float]], List[str]]:
    """
    Convert list of catalog entries to numerical matrix.
    Returns (matrix, labels) where matrix[i][j] is primitive j of entry i.
    """
    if scheme == "ordinal":
        vectors = [encode_ordinal(e) for e in entries]
    elif scheme == "zero_centered":
        vectors = [encode_zero_centered(e) for e in entries]
    elif scheme == "normalized":
        vectors = [encode_normalized(e) for e in entries]
    elif scheme == "absorbing":
        vectors = [encode_absorbing(e, absorption_rules, absorption_op) for e in entries]
    else:
        raise ValueError(f"Unknown scheme: {scheme}")
    
    labels = [e.get("name", f"entry_{i}") for i, e in enumerate(entries)]
    return vectors, labels

# ═══════════════════════════════════════════════════════════════
# ENSEMBLE ANALYSIS
# ═══════════════════════════════════════════════════════════════

def compute_correlation_matrix(matrix: List[List[float]], 
                               prim_labels: List[str] = None) -> Dict:
    """Compute Pearson correlation between primitives across the ensemble."""
    if prim_labels is None:
        prim_labels = PRIM_KEYS.copy()
    
    n_prims = len(matrix[0])
    # Compute means
    means = [0.0] * n_prims
    for row in matrix:
        for j in range(n_prims):
            means[j] += row[j]
    n = len(matrix)
    means = [m / n for m in means]
    
    # Compute covariance and std
    cov = [[0.0] * n_prims for _ in range(n_prims)]
    stds = [0.0] * n_prims
    for row in matrix:
        for j in range(n_prims):
            dev_j = row[j] - means[j]
            stds[j] += dev_j * dev_j
            for k in range(j, n_prims):
                cov[j][k] += dev_j * (row[k] - means[k])
    
    for j in range(n_prims):
        stds[j] = (stds[j] / n) ** 0.5
        for k in range(j, n_prims):
            cov[j][k] /= n
            cov[k][j] = cov[j][k]
    
    # Correlation
    corr = [[0.0] * n_prims for _ in range(n_prims)]
    for j in range(n_prims):
        for k in range(n_prims):
            if stds[j] > 0 and stds[k] > 0:
                corr[j][k] = cov[j][k] / (stds[j] * stds[k])
    
    # Find strongest correlations
    pairs = []
    for j in range(n_prims):
        for k in range(j+1, n_prims):
            pairs.append((prim_labels[j], prim_labels[k], corr[j][k]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    
    return {
        "correlation_matrix": corr,
        "primitive_labels": prim_labels,
        "strongest_pairs": pairs[:10],
        "strongest_negative": [p for p in pairs if p[2] < 0][:5],
        "strongest_positive": [p for p in pairs if p[2] > 0][:5],
    }


def compute_primitive_distribution(matrix: List[List[float]]) -> Dict:
    """Compute value distribution per primitive across the ensemble."""
    n_prims = len(matrix[0])
    dist = {}
    for j, p in enumerate(PRIM_KEYS):
        vals = [row[j] for row in matrix]
        from collections import Counter
        cnt = Counter(vals)
        dist[p] = {
            "mean": sum(vals) / len(vals),
            "min": min(vals),
            "max": max(vals),
            "unique_count": len(cnt),
            "most_common": cnt.most_common(3),
            "cardinality": CARDINALITY[p],
            "coverage": len(cnt) / CARDINALITY[p],
        }
    return dist


def compute_tier_distribution(entries: List[dict]) -> Dict:
    """Compute ouroboricity tier distribution across the ensemble."""
    from collections import Counter
    from imscrbgrmr.canonical_primitives import ouroboricity_tier, CrystalAddress
    
    tiers = []
    for e in entries:
        try:
            addr = CrystalAddress.from_dict(e)
            tier = ouroboricity_tier(addr)
            tiers.append(tier)
        except (KeyError, ValueError):
            tiers.append("UNKNOWN")
    
    cnt = Counter(tiers)
    return {
        "counts": dict(cnt),
        "total": len(entries),
        "O_0_pct": cnt.get("O₀", 0) / len(entries) * 100,
        "O_1_pct": cnt.get("O₁", 0) / len(entries) * 100,
        "O_2_pct": cnt.get("O₂", 0) / len(entries) * 100,
        "O_2_dagger_pct": cnt.get("O₂†", 0) / len(entries) * 100,
        "O_inf_pct": cnt.get("O_∞", 0) / len(entries) * 100,
    }

# ═══════════════════════════════════════════════════════════════
# PRIMITIVE CO-OCCURRENCE / MUTUAL INFORMATION
# ═══════════════════════════════════════════════════════════════

def compute_cooccurrence(entries: List[dict]) -> Dict:
    """
    For each pair of primitives, compute: given value X at primitive A,
    what is the distribution of values at primitive B?
    Returns a contingency structure: cooc[A][a_val][B][b_val] = count.
    """
    from collections import defaultdict, Counter
    
    # Build per-primitive value lists
    cooc = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
    
    for e in entries:
        for a in PRIM_KEYS:
            a_val = e[a]
            for b in PRIM_KEYS:
                if a >= b:
                    continue
                b_val = e[b]
                cooc[a][a_val][b][b_val] += 1
    
    # Find most deterministic pairs (one value strongly predicts another)
    strong_pairs = []
    for a in PRIM_KEYS:
        for a_val in CANONICAL_VALUES[a]:
            for b in PRIM_KEYS:
                if a >= b:
                    continue
                inner = cooc[a][a_val][b]
                total = sum(inner.values())
                if total > 5:  # threshold
                    most_common_b, mc_count = inner.most_common(1)[0]
                    ratio = mc_count / total
                    if ratio > 0.6:  # 60%+ determinism
                        strong_pairs.append({
                            "given": (a, a_val),
                            "predicts": (b, most_common_b),
                            "confidence": round(ratio, 3),
                            "sample_size": total,
                        })
    
    strong_pairs.sort(key=lambda x: x["confidence"], reverse=True)
    return {"strong_deterministic_pairs": strong_pairs[:30]}


# ═══════════════════════════════════════════════════════════════
# CLUSTERING (simple k-means on ordinal vectors)
# ═══════════════════════════════════════════════════════════════

def kmeans_cluster(matrix: List[List[float]], k: int = 7, 
                   max_iters: int = 50) -> Dict:
    """Simple k-means clustering. Returns cluster assignments and centroids."""
    import random
    random.seed(42)
    
    n = len(matrix)
    d = len(matrix[0])
    
    # Initialize centroids randomly from data points
    indices = list(range(n))
    random.shuffle(indices)
    centroids = [matrix[i][:] for i in indices[:k]]
    
    for _iter in range(max_iters):
        # Assign points to nearest centroid
        assignments = []
        for row in matrix:
            best_c = 0
            best_dist = float('inf')
            for c, centroid in enumerate(centroids):
                dist = sum((row[j] - centroid[j])**2 for j in range(d))
                if dist < best_dist:
                    best_dist = dist
                    best_c = c
            assignments.append(best_c)
        
        # Recompute centroids
        new_centroids = [[0.0]*d for _ in range(k)]
        counts = [0]*k
        for i, row in enumerate(matrix):
            c = assignments[i]
            counts[c] += 1
            for j in range(d):
                new_centroids[c][j] += row[j]
        
        moved = False
        for c in range(k):
            if counts[c] > 0:
                for j in range(d):
                    new_centroids[c][j] /= counts[c]
            if new_centroids[c] != centroids[c]:
                moved = True
        centroids = new_centroids
        if not moved:
            break
    
    # Cluster sizes
    from collections import Counter
    sizes = Counter(assignments)
    
    return {
        "k": k,
        "assignments": assignments,
        "centroids": centroids,
        "cluster_sizes": {str(c): sizes[c] for c in range(k)},
        "iterations": _iter + 1,
    }


# ═══════════════════════════════════════════════════════════════
# ABSORBING-SIGNATURE DETECTION
# ═══════════════════════════════════════════════════════════════

def detect_absorbing_signatures(entries: List[dict]) -> Dict:
    """
    Detect which entries have absorbing primitives under canonical rules.
    An entry is "absorbing" if it has ⊙=⊙ (self-modeling gate) or Σ=𐑳 (n:m).
    """
    absorbing_mask = {
        "⊙": "⊙",
        "⊞": "𐑳",
    }
    
    results = {
        "absorbing_Phi_c": [],   # entries with ⊙=⊙
        "absorbing_Sigma_nm": [],  # entries with Σ=𐑳
        "both": [],
        "neither": [],
    }
    
    for e in entries:
        name = e.get("name", "?")
        has_phi = e.get("⊙") == absorbing_mask["⊙"]
        has_sigma = e.get("⊞") == absorbing_mask["⊞"]
        
        if has_phi and has_sigma:
            results["both"].append(name)
        elif has_phi:
            results["absorbing_Phi_c"].append(name)
        elif has_sigma:
            results["absorbing_Sigma_nm"].append(name)
        else:
            results["neither"].append(name)
    
    results["summary"] = {
        "total": len(entries),
        "absorb_phi_only": len(results["absorbing_Phi_c"]),
        "absorb_sigma_only": len(results["absorbing_Sigma_nm"]),
        "absorb_both": len(results["both"]),
        "absorb_neither": len(results["neither"]),
        "any_absorbing": len(results["absorbing_Phi_c"]) + len(results["absorbing_Sigma_nm"]) + len(results["both"]),
    }
    return results

# ═══════════════════════════════════════════════════════════════
# FILTER: Exclude entries missing primitive glyphs
# ═══════════════════════════════════════════════════════════════

def filter_valid_entries(entries: List[dict]) -> List[dict]:
    """Remove entries that lack all 12 primitive glyphs."""
    valid = []
    bad_count = 0
    for e in entries:
        if all(p in e and e[p] is not None for p in PRIM_KEYS):
            valid.append(e)
        else:
            bad_count += 1
    if bad_count:
        import sys
        print(f"  [numerical_encode] Filtered {bad_count} entries missing primitives.", file=sys.stderr)
    return valid


# Patch ensemble_to_matrix to auto-filter
_original_ensemble_to_matrix = ensemble_to_matrix

def ensemble_to_matrix(entries: List[dict], 
                       scheme: str = "ordinal",
                       absorption_rules: Tuple[AbsorptionRule, ...] = (),
                       absorption_op: str = "tensor") -> Tuple[List[List[float]], List[str]]:
    """Auto-filters invalid entries before conversion."""
    valid = filter_valid_entries(entries)
    return _original_ensemble_to_matrix(valid, scheme, absorption_rules, absorption_op)

# ═══════════════════════════════════════════════════════════════
# IG NOTATION → SHAVIAN GLYPH TRANSLATOR
# Some catalog entries use IG notation (e.g. "𐑦") instead of
# Shavian glyphs (e.g. "𐑦"). This maps all known IG notation to glyphs.
# ═══════════════════════════════════════════════════════════════

IG_TO_SHAVIAN: Dict[str, Dict[str, str]] = {
    "⊢": {
        "𐑦": "𐑦", "𐑛": "𐑨", "𐑨": "𐑼", "𐑼": "𐑛",
        "D_odot": "𐑦", "D_infty": "𐑨", "D_triangle": "𐑼", "D_wedge": "𐑛",
    },
    "⊣": {
        "𐑸": "𐑸", "𐑡": "𐑡", "𐑰": "𐑰", "𐑥": "𐑥", "𐑶": "𐑶",
        "T_odot": "𐑸", "T_net": "𐑡", "T_in": "𐑰", "T_bowtie": "𐑥", "T_boxtimes": "𐑶",
    },
    ">": {
        "𐑽": "𐑩", "𐑩": "𐑑", "𐑑": "𐑽", "𐑾": "𐑾",
        "R_super": "𐑩", "R_cat": "𐑑", "R_dagger": "𐑽", "R_lr": "𐑾",
    },
    "<": {
        "𐑿": "𐑗", "𐑬": "𐑿", "𐑯": "𐑬", "𐑹": "𐑯", "𐑗": "𐑹",
        "P_asym": "𐑗", "P_psi": "𐑿", "P_pm": "𐑬", "P_sym": "𐑯", "P_pm_sym": "𐑹",
    },
    "⋈": {
        "𐑱": "𐑱", "𐑞": "𐑞", "𐑐": "𐑐",
        "F_ell": "𐑱", "F_eth": "𐑞", "F_hbar": "𐑐",
    },
    "⊤": {
        "𐑘": "𐑺", "𐑤": "𐑪", "𐑧": "𐑧", "𐑪": "𐑤", "𐑺": "𐑘",
        "K_fast": "𐑺", "K_mod": "𐑪", "K_slow": "𐑧", "K_trap": "𐑤", "K_MBL": "𐑘",
    },
    "∈": {
        "𐑔": "𐑲", "𐑚": "𐑚", "𐑲": "𐑔",
        "G_beth": "𐑲", "G_gimel": "𐑚", "G_aleph": "𐑔",
    },
    "∋": {
        "𐑵": "𐑝", "𐑝": "𐑜", "𐑜": "𐑠", "𐑠": "𐑵",
        "Gamma_and": "𐑝", "Gamma_or": "𐑜", "Gamma_seq": "𐑠", "Gamma_broad": "𐑵",
    },
    "⊙": {
        "𐑢": "𐑢", "⊙": "⊙", "𐑮": "𐑮", "𐑻": "𐑻", "𐑣": "𐑣",
        "⊙": "⊙", "𐑢": "𐑢", "𐑮": "𐑮", "𐑻": "𐑻", "Phi_super": "𐑣",
    },
    "⊥": {
        "𐑓": "𐑓", "𐑒": "𐑒", "𐑖": "𐑖", "𐑫": "𐑫",
        "H0": "𐑓", "H1": "𐑒", "H2": "𐑖", "H_inf": "𐑫",
    },
    "⊞": {
        "𐑙": "𐑙", "𐑕": "𐑕", "𐑳": "𐑳",
        "S_1_1": "𐑙", "S_n_n": "𐑕", "S_n_m": "𐑳",
    },
    "◻": {
        "𐑷": "𐑷", "𐑴": "𐑴", "𐑭": "𐑭", "𐑟": "𐑟",
        "Omega_0": "𐑷", "Omega_Z2": "𐑴", "Omega_Z": "𐑭", "Omega_NA": "𐑟",
    },
}


def transcribe_ig_to_shavian(entry: dict) -> dict:
    """Convert any IG-notation values in an entry to Shavian glyphs.
    Returns a new dict (does not mutate original)."""
    result = dict(entry)
    for p in PRIM_KEYS:
        if p in result:
            val = result[p]
            if val is not None and val not in CANONICAL_VALUES[p]:
                # Try IG notation mapping
                shavian = IG_TO_SHAVIAN.get(p, {}).get(val)
                if shavian is not None:
                    result[p] = shavian
    return result


# Patch filter_valid_entries to also transcribe
def filter_valid_entries(entries: List[dict]) -> List[dict]:
    """Remove entries that lack all 12 primitive glyphs after transcription."""
    valid = []
    bad_count = 0
    for e in entries:
        transcribed = transcribe_ig_to_shavian(e)
        if all(p in transcribed and transcribed[p] is not None and transcribed[p] in CANONICAL_VALUES[p] for p in PRIM_KEYS):
            valid.append(transcribed)
        else:
            bad_count += 1
    if bad_count:
        import sys
        print(f"  [numerical_encode] Filtered {bad_count} entries (missing or invalid primitives).", file=sys.stderr)
    return valid
