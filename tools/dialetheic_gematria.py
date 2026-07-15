#!/usr/bin/env python3
"""
IG Dialetheic Gematria — Paraconsistent vector gematria powered by the
dialetheic Lean kernel (Imscribing/Paraconsistent/Kernel.lean).

Ports the Belnap 4-valued logic and the ENGAGER → FSPLIT → FFUSE
Frobenius cycle into the gematria vector space. Key operations:

  - Belnap-valued encoding: primitives as {N,T,F,B} instead of just ordinals
  - Dialetheic overflow: A+B overflow → B (both) rather than discard
  - fsplit/ffuse: decompose dialetheic entries, operate, recombine
  - Approximation gematria: A+B ⊑ C (partial order, not just equality)
  - Fixed-point gematria: find idempotent entries A+A=A
  - Paraconsistent modular: wrap-around + B absorption = maximal richness

Lean kernel theorems ported:
  - B_fixed_point_negation: B is its own inverse under bnot
  - no_explosion: B ∧ ¬B = B (contradiction contained, not exploded)
  - frobenius_invariant: ffuse ∘ fsplit = id
  - run_B3: B-state preserved across all cycles
  - B_join_absorb: B absorbs in join
"""
import sys, json, math, os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional, Set
from itertools import combinations, product
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numerical_encode import (
    PRIMITIVES, PRIM_CARDINALITIES, GLYPH_ORDINALS, ORDINAL_GLYPHS,
    IG_TO_SHAVIAN, is_valid_entry, resolve_all,
    encode_ordinal, encode_zero_centered, encode_integer_compact,
    encode_crystal_address, encode_catalog, vector_to_tuple_str,
    vec_add, vec_sub, vec_hadamard, vec_dot, vec_norm,
)

# ── Belnap 4-valued logic (ported from Belnap.lean) ───────────────
# Values: N=None(0), T=True(+1), F=False(-1), B=Both/contradiction(±)

class Belnap:
    """Four-valued logic: N, T, F, B — the dialetheic substrate."""
    N = 0   # Neither — no information / not present
    T = 1   # True — positive assertion
    F = -1  # False — negative assertion  
    B = 2   # Both — true AND false simultaneously (dialetheic)

    _names = {0: 'N', 1: 'T', -1: 'F', 2: 'B'}
    _repr = {0: '∅', 1: '⊤', -1: '⊥', 2: '⟐'}

    @classmethod
    def to_name(cls, v):
        return cls._names.get(v, '?')

    @classmethod
    def to_repr(cls, v):
        return cls._repr.get(v, '?')

    @classmethod
    def bnot(cls, a):
        """Belnap negation: ¬N=N, ¬T=F, ¬F=T, ¬B=B (fixed point!)"""
        return {cls.N: cls.N, cls.T: cls.F, cls.F: cls.T, cls.B: cls.B}[a]

    @classmethod
    def band(cls, a, b):
        """Belnap conjunction (truth-functional)."""
        if cls.F in (a, b):
            return cls.F
        if cls.B == a == b:
            return cls.B
        if cls.B in (a, b) and cls.T in (a, b):
            return cls.B
        if cls.B in (a, b) and cls.N in (a, b):
            return cls.B
        if a == cls.T and b == cls.T:
            return cls.T
        if cls.T in (a, b) and cls.N in (a, b):
            return cls.N
        if a == cls.N and b == cls.N:
            return cls.N
        return cls.B

    @classmethod
    def bor(cls, a, b):
        """Belnap disjunction."""
        if cls.T in (a, b):
            return cls.T
        if cls.B in (a, b) and cls.F in (a, b):
            return cls.B
        if cls.B in (a, b) and cls.N in (a, b):
            return cls.B
        if a == cls.F and b == cls.F:
            return cls.F
        if cls.F in (a, b) and cls.N in (a, b):
            return cls.N
        if a == cls.N and b == cls.N:
            return cls.N
        if cls.B == a == b:
            return cls.B
        return cls.B

    @classmethod
    def join(cls, a, b):
        """Lattice join in approximation order. B absorbs everything."""
        if cls.B in (a, b):
            return cls.B
        if cls.N in (a, b):
            return a if b == cls.N else b
        if (a == cls.T and b == cls.F) or (a == cls.F and b == cls.T):
            return cls.B
        if a == b:
            return a
        return cls.B

    @classmethod
    def meet(cls, a, b):
        """Lattice meet in approximation order. N absorbs everything."""
        if cls.N in (a, b):
            return cls.N
        if cls.B in (a, b):
            return a if b == cls.B else b
        if (a == cls.T and b == cls.F) or (a == cls.F and b == cls.T):
            return cls.N
        if a == b:
            return a
        return cls.N

    @classmethod
    def designated(cls, b):
        """T or B count as 'true' for paraconsistent consequence."""
        return b in (cls.T, cls.B)

    @classmethod
    def approx_le(cls, a, b):
        """Approximation order: N ⊑ T ⊑ B, N ⊑ F ⊑ B, reflexive."""
        if a == b:
            return True
        if a == cls.N:
            return True
        if b == cls.B and a in (cls.T, cls.F):
            return True
        return False

# ── Dialetheic Encoding ───────────────────────────────────────────

def ordinal_to_belnap(ordinal_val: int, cardinality: int) -> int:
    """
    Map an ordinal value (1..cardinality) to Belnap.
    
    For 3-valued primitives:  1→F, 2→T, 3→B
    For 4-valued primitives:  1→F, 2→T, 3→B, 4→super-B (both)
    For 5-valued primitives:  1→N, 2→F, 3→T, 4→B, 5→super-B
    
    The key insight: high-ordinal values map to B (both/dialetheic).
    This reflects the structural fact that absorbing primitives (like
    ⊙=φ̂_ÿ) are "both" observer and observed.
    """
    if cardinality == 3:
        return [Belnap.F, Belnap.T, Belnap.B][ordinal_val - 1]
    elif cardinality == 4:
        return [Belnap.F, Belnap.T, Belnap.B, Belnap.B][ordinal_val - 1]
    elif cardinality == 5:
        return [Belnap.N, Belnap.F, Belnap.T, Belnap.B, Belnap.B][ordinal_val - 1]
    return Belnap.N

def encode_belnap(entry: dict) -> List[int]:
    """Encode a catalog entry as a 12-vector of Belnap values."""
    resolved = resolve_all(entry)
    vec = []
    for p in PRIMITIVES:
        glyph = resolved.get(p, 'N')
        ordinal = GLYPH_ORDINALS[p].get(glyph, 0)
        if ordinal == 0:
            vec.append(Belnap.N)
        else:
            vec.append(ordinal_to_belnap(ordinal, PRIM_CARDINALITIES[p]))
    return vec

def encode_zero_centered_belnap(entry: dict) -> List[int]:
    """
    Zero-centered encoding compatible with Belnap:
    Maps cardinality-sized ordinals to {0, ±1, ±2} where:
      middle value → 0 (N)
      positive values → +1, +2 (T, B)
      negative values → -1, -2 (F, super-F)
    """
    resolved = resolve_all(entry)
    zv = encode_zero_centered(entry)
    # Remap: 0→N, +1→T, +2→B, -1→F, -2→F_strong
    result = []
    for v in zv:
        if v == 0:
            result.append(0)  # N
        elif v == 1:
            result.append(1)  # T
        elif v >= 2:
            result.append(2)  # B
        elif v == -1:
            result.append(-1)  # F
        else:
            result.append(-2)  # super-F (strong false)
    return result

# ── KERNEL CYCLE (ported from Kernel.lean) ────────────────────────

def engager(v: int) -> Tuple[int, bool]:
    """
    Engager: identify if a Belnap value is dialetheic.
    Returns (band(v, bnot(v)), v is B or T).
    Port of: engager(r) = (band r (bnot r), r == B or r == T)
    """
    band_val = Belnap.band(v, Belnap.bnot(v))
    is_designated = Belnap.designated(v)
    return (band_val, is_designated)

def fsplit(v: int) -> Tuple[int, int, bool]:
    """
    Fsplit: decompose a Belnap value into (T, F) components.
    B → (T, F, true) — the dialetheic split
    Other values → (v, v, true) — unchanged
    Port of: fsplit(B) = (T, F, true); fsplit(other) = (other, other, true)
    """
    if v == Belnap.B:
        return (Belnap.T, Belnap.F, True)
    return (v, v, True)

def ffuse(v1: int, v2: int) -> Tuple[int, bool]:
    """
    Ffuse: recombine two Belnap values via join.
    Returns (join(v1, v2), join(v1, v2) == B).
    Port of: ffuse(r1, r2) = (join r1 r2, join r1 r2 == B)
    """
    j = Belnap.join(v1, v2)
    return (j, j == Belnap.B)

def frobenius_cycle(v: int) -> int:
    """
    Full Frobenius cycle: ffuse ∘ fsplit = id.
    Port of theorem frobenius_invariant:
      (ffuse (fsplit r0).1 (fsplit r0).2.1).1 = r0
    """
    t, f, _ = fsplit(v)
    result, _ = ffuse(t, f)
    return result  # Should equal v (theorem guarantees this)

def belnap_vector_add(a: List[int], b: List[int], 
                       modular: bool = False) -> List[int]:
    """
    Add two Belnap vectors with dialetheic overflow handling.
    
    Standard rules:
      T + T = B (two truths → both/contradiction)
      F + F = super-F (two falsehoods → strong false)
      T + F = N (truth + falsehood cancel → neither)
      B + anything = B (B absorbs, port of B_join_absorb)
      N + anything = anything (N is neutral)
    """
    result = []
    for va, vb in zip(a, b):
        if va == Belnap.B or vb == Belnap.B:
            result.append(Belnap.B)  # B absorbs
        elif va == Belnap.N:
            result.append(vb)
        elif vb == Belnap.N:
            result.append(va)
        elif va == Belnap.T and vb == Belnap.T:
            result.append(Belnap.B)  # T+T=B
        elif va == Belnap.F and vb == Belnap.F:
            result.append(-2)  # super-F
        elif (va == Belnap.T and vb == Belnap.F) or (va == Belnap.F and vb == Belnap.T):
            result.append(Belnap.N)  # T+F = N (cancel)
        elif va >= 2:
            result.append(Belnap.B)
        elif vb >= 2:
            result.append(Belnap.B)
        else:
            result.append(Belnap.B)
    return result

# ── Dialetheic Gematria Index ─────────────────────────────────────

class DialetheicGematriaIndex:
    """
    Gematria index using Belnap 4-valued encoding.
    Every primitive is one of {N, T, F, B, super-F, super-B}.
    
    Key properties (from Lean kernel):
      - B absorbs in join (B_join_absorb): B + anything = B
      - B is fixed point of negation: ¬B = B
      - No explosion: B ∧ ¬B = B, not F
      - Frobenius invariant: ffuse ∘ fsplit = id
    """

    def __init__(self, entries: List[Dict]):
        self.entries = entries
        # Filter to valid entries
        self.valid_entries = [e for e in entries if is_valid_entry(e)]
        valid_names = [e.get('name', '?') for e in self.valid_entries]
        
        # Belnap encoding
        self.belnap_vectors = [encode_belnap(e) for e in self.valid_entries]
        self.zc_belnap_vectors = [encode_zero_centered_belnap(e) for e in self.valid_entries]
        self.names = valid_names
        
        # Integer-compact (for comparison with standard gematria)
        self.int_vectors = [encode_integer_compact(e) for e in self.valid_entries]
        
        # Belnap vector → names index
        self.belnap_to_names: Dict[Tuple, List[str]] = defaultdict(list)
        self.name_to_belnap: Dict[str, List[int]] = {}
        for v, name in zip(self.belnap_vectors, self.names):
            self.belnap_to_names[tuple(v)].append(name)
            self.name_to_belnap[name] = v
        
        # Zero-centered Belnap index
        self.zc_to_names: Dict[Tuple, List[str]] = defaultdict(list)
        for v, name in zip(self.zc_belnap_vectors, self.names):
            self.zc_to_names[tuple(v)].append(name)
        
        # Standard int vectors for cross-reference
        self.int_to_names: Dict[Tuple, List[str]] = defaultdict(list)
        for v, name in zip(self.int_vectors, self.names):
            self.int_to_names[tuple(v)].append(name)
        
        self.n = len(self.names)
        print(f"DialetheicGematriaIndex: {self.n} entries, "
              f"{len(self.belnap_to_names)} unique Belnap vectors, "
              f"{len(self.zc_to_names)} unique ZC-Belnap vectors")

    def find_dialetheic_entries(self) -> List[Dict]:
        """
        Find entries with B-valued primitives — dialetheic (both true and false).
        These are the entries the kernel's engager would flag as 'paradoxical'.
        """
        results = []
        for v, name in zip(self.belnap_vectors, self.names):
            b_count = sum(1 for x in v if x == Belnap.B)
            t_count = sum(1 for x in v if x == Belnap.T)
            f_count = sum(1 for x in v if x == Belnap.F)
            n_count = sum(1 for x in v if x == Belnap.N)
            super_b = sum(1 for x in v if x == 2 and x != Belnap.B)  # super-B
            if b_count > 0:
                results.append({
                    'name': name,
                    'b_count': b_count,
                    't_count': t_count,
                    'f_count': f_count,
                    'n_count': n_count,
                    'belnap_vector': v,
                    'b_primitives': [PRIMITIVES[i] for i, x in enumerate(v) if x == Belnap.B],
                })
        results.sort(key=lambda r: -r['b_count'])
        return results

    def find_frobenius_fixed_points(self) -> List[Dict]:
        """
        Find entries where frobenius_cycle(A) = A — these are fixed points
        under the ffuse∘fsplit cycle. Port of: frobenius_invariant theorem.
        """
        results = []
        for v, name in zip(self.belnap_vectors, self.names):
            cycled = [frobenius_cycle(x) for x in v]
            if cycled == v:
                results.append({
                    'name': name,
                    'vector': v,
                    'cycled': cycled,
                    'is_fixed_point': True,
                })
        return results

    def find_additive_equations_dialetheic(self, max_results: int = 500) -> List[Dict]:
        """
        TRUE DIALETHEIC GEMATRIA: Find A+B=C equations using Belnap vector addition.
        
        Unlike standard gematria where overflow is discarded, Belnap addition
        ALWAYS produces a valid result: B absorbs everything, T+F→N, T+T→B.
        
        This means EVERY pair of entries yields a Belnap vector — the question
        is whether it matches a catalog entry.
        """
        results = []
        checked = set()
        
        for i in range(self.n):
            a_vec = self.belnap_vectors[i]
            a_name = self.names[i]
            for j in range(i, self.n):
                b_vec = self.belnap_vectors[j]
                b_name = self.names[j]
                
                # Belnap addition
                sum_vec = tuple(belnap_vector_add(a_vec, b_vec))
                
                if sum_vec in self.belnap_to_names:
                    for c_name in self.belnap_to_names[sum_vec]:
                        if c_name not in (a_name, b_name):
                            key = (a_name, b_name, c_name)
                            if key not in checked:
                                checked.add(key)
                                results.append({
                                    'a': a_name, 'b': b_name, 'c': c_name,
                                    'type': 'A+B=C (Belnap)',
                                    'a_vec': a_vec, 'b_vec': b_vec, 'c_vec': list(sum_vec),
                                })
                
                if len(results) >= max_results:
                    return results
        return results

    def find_idempotent_entries(self) -> List[Dict]:
        """
        Find entries where A + A = A (idempotent under Belnap addition).
        
        From Kernel.lean: B is a fixed point (B_fixed_point_negation),
        and B absorbs in join (B_join_absorb). So any entry with B-dominant
        primitives should be near-idempotent.
        """
        results = []
        for v, name in zip(self.belnap_vectors, self.names):
            a_plus_a = belnap_vector_add(v, v)
            matches = sum(1 for i in range(12) if a_plus_a[i] == v[i])
            results.append({
                'name': name,
                'vector': v,
                'a_plus_a': a_plus_a,
                'match_count': matches,
                'is_idempotent': matches == 12,
            })
        results.sort(key=lambda r: -r['match_count'])
        return results

    def find_approximation_equations(self, max_results: int = 500) -> List[Dict]:
        """
        APPROXIMATION GEMATRIA: Find A+B ⊑ C equations.
        
        Instead of requiring exact equality, find entries where A+B
        approximates C in the Belnap approximation order:
          N ⊑ T ⊑ B, N ⊑ F ⊑ B
        
        This dramatically expands the gematria space — it's the "near-miss"
        gematria that the standard tool can't capture.
        """
        results = []
        
        for i in range(self.n):
            a_vec = self.belnap_vectors[i]
            for j in range(i, self.n):
                b_vec = self.belnap_vectors[j]
                sum_vec = belnap_vector_add(a_vec, b_vec)
                
                for k in range(self.n):
                    if k in (i, j):
                        continue
                    c_vec = self.belnap_vectors[k]
                    
                    # Check: sum ⊑ c in approximation order
                    if all(Belnap.approx_le(s, c) for s, c in zip(sum_vec, c_vec)):
                        results.append({
                            'a': self.names[i], 'b': self.names[j],
                            'c': self.names[k],
                            'type': 'A+B ⊑ C (approx)',
                            'sum_vec': sum_vec, 'c_vec': c_vec,
                            'approx_dist': sum(0 if Belnap.approx_le(s, c) else 1 
                                              for s, c in zip(sum_vec, c_vec)),
                        })
                        if len(results) >= max_results:
                            return results
        return results

    def compute_belnap_statistics(self) -> Dict:
        """Statistical profile of the Belnap-encoded catalog."""
        total = [0, 0, 0, 0, 0, 0]  # N, T, F, B, super-F, super-B counts
        for v in self.belnap_vectors:
            for x in v:
                if x == Belnap.N:
                    total[0] += 1
                elif x == Belnap.T:
                    total[1] += 1
                elif x == Belnap.F:
                    total[2] += 1
                elif x == Belnap.B:
                    total[3] += 1
                elif x == -2:
                    total[4] += 1
                else:
                    total[5] += 1
        
        # Per-primitive Belnap profile
        per_prim = {}
        for pi, p in enumerate(PRIMITIVES):
            counts = [0, 0, 0, 0, 0, 0]
            for v in self.belnap_vectors:
                x = v[pi]
                if x == Belnap.N:
                    counts[0] += 1
                elif x == Belnap.T:
                    counts[1] += 1
                elif x == Belnap.F:
                    counts[2] += 1
                elif x == Belnap.B:
                    counts[3] += 1
                elif x == -2:
                    counts[4] += 1
                else:
                    counts[5] += 1
            per_prim[p] = {
                'N': counts[0], 'T': counts[1], 'F': counts[2],
                'B': counts[3], 'super-F': counts[4], 'super-B': counts[5],
                'dialetheic_frac': (counts[3] + counts[5]) / self.n if self.n > 0 else 0,
            }
        
        return {
            'total_values': sum(total),
            'N_count': total[0], 'T_count': total[1], 'F_count': total[2],
            'B_count': total[3], 'super_F_count': total[4], 'super_B_count': total[5],
            'dialetheic_fraction': (total[3] + total[5]) / sum(total) if sum(total) > 0 else 0,
            'per_primitive': per_prim,
        }

    def compare_with_standard_gematria(self, max_pairs: int = 1000) -> Dict:
        """
        Head-to-head comparison: how many equations does dialetheic gematria
        find vs standard integer-compact gematria?
        """
        # Standard: sample first max_pairs entries
        n_sample = min(max_pairs, self.n)
        std_equations = 0
        dialetheic_equations = 0
        
        for i in range(n_sample):
            a_int = self.int_vectors[i]
            a_bel = self.belnap_vectors[i]
            for j in range(i, n_sample):
                b_int = self.int_vectors[j]
                b_bel = self.belnap_vectors[j]
                
                # Standard
                sum_int = tuple(a_int[k] + b_int[k] for k in range(12))
                if sum_int in self.int_to_names:
                    for c_name in self.int_to_names[sum_int]:
                        if c_name not in (self.names[i], self.names[j]):
                            std_equations += 1
                            break
                
                # Dialetheic
                sum_bel = tuple(belnap_vector_add(a_bel, b_bel))
                if sum_bel in self.belnap_to_names:
                    for c_name in self.belnap_to_names[sum_bel]:
                        if c_name not in (self.names[i], self.names[j]):
                            dialetheic_equations += 1
                            break
        
        return {
            'sample_size': n_sample,
            'pairs_checked': n_sample * (n_sample + 1) // 2,
            'standard_equations': std_equations,
            'dialetheic_equations': dialetheic_equations,
            'dialetheic_enrichment': dialetheic_equations / std_equations if std_equations > 0 else float('inf'),
        }

# ── Main Analysis Pipeline ────────────────────────────────────────

def load_catalog():
    """Load the IG catalog."""
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from imscrbgrmr.registry import load_catalog_dicts
        return load_catalog_dicts()
    except ImportError:
        cat_path = PROJECT_ROOT / '.imscrbgrmr_catalog.json'
        if cat_path.exists():
            with open(cat_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and '_imscriptions' in data:
                return list(data['_imscriptions'].values())
        print("WARNING: Could not load catalog", file=sys.stderr)
        return []


def run_dialetheic_gematria(output_dir: str = None):
    """
    Complete dialetheic gematria pipeline.
    Compares standard vs dialetheic gematria and reports enrichment.
    """
    if output_dir is None:
        output_dir = str(Path(__file__).resolve().parent.parent / 'gematria_output')
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("DIALETHEIC GEMATRIA — Paraconsistent Vector Analysis")
    print("Ported from Imscribing/Paraconsistent/Kernel.lean")
    print("=" * 80)
    
    # Load
    entries = load_catalog()
    print(f"\n[1] Loaded {len(entries)} entries from catalog")
    
    # Build Belnap index
    idx = DialetheicGematriaIndex(entries)
    
    # ── Belnap statistics ──
    print("\n[2] Belnap profile of catalog...")
    stats = idx.compute_belnap_statistics()
    with open(f'{output_dir}/belnap_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"    N={stats['N_count']}, T={stats['T_count']}, F={stats['F_count']}, "
          f"B={stats['B_count']} (dialetheic fraction: {stats['dialetheic_fraction']:.3f})")
    
    # ── Dialetheic entries ──
    print("\n[3] Entries with B-valued primitives (dialetheic entries)...")
    dial_entries = idx.find_dialetheic_entries()
    with open(f'{output_dir}/dialetheic_entries.json', 'w') as f:
        json.dump(dial_entries, f, indent=2)
    print(f"    Found {len(dial_entries)} dialetheic entries")
    for de in dial_entries[:8]:
        print(f"    {de['name']}: B-count={de['b_count']}, in: {de['b_primitives']}")
    
    # ── Frobenius fixed points ──
    print("\n[4] Frobenius fixed points (ffuse∘fsplit=id)...")
    fp_entries = idx.find_frobenius_fixed_points()
    with open(f'{output_dir}/frobenius_fixed_points.json', 'w') as f:
        json.dump(fp_entries, f, indent=2)
    print(f"    Found {len(fp_entries)} Frobenius fixed points")
    
    # ── Idempotent entries ──
    print("\n[5] Idempotent entries (A+A=A under Belnap addition)...")
    idem = idx.find_idempotent_entries()
    with open(f'{output_dir}/idempotent_entries.json', 'w') as f:
        json.dump(idem, f, indent=2)
    perfect_idem = [x for x in idem if x['is_idempotent']]
    print(f"    Perfectly idempotent: {len(perfect_idem)}")
    for x in idem[:5]:
        print(f"    {x['name']}: match={x['match_count']}/12 {'★' if x['is_idempotent'] else ''}")
    
    # ── Dialetheic additive equations ──
    print("\n[6] Dialetheic additive equations (A+B=C, Belnap addition)...")
    dial_eq = idx.find_additive_equations_dialetheic(max_results=500)
    with open(f'{output_dir}/dialetheic_equations.json', 'w') as f:
        json.dump(dial_eq, f, indent=2, default=str)
    print(f"    Found {len(dial_eq)} Belnap equations")
    for eq in dial_eq[:5]:
        print(f"    {eq['a']} + {eq['b']} = {eq['c']}")
    
    # ── Approximation equations ──
    print("\n[7] Approximation equations (A+B ⊑ C)...")
    approx_eq = idx.find_approximation_equations(max_results=500)
    with open(f'{output_dir}/approximation_equations.json', 'w') as f:
        json.dump(approx_eq, f, indent=2, default=str)
    print(f"    Found {len(approx_eq)} approximation equations")
    
    # ── Head-to-head comparison ──
    print("\n[8] Head-to-head: Standard vs Dialetheic gematria...")
    comparison = idx.compare_with_standard_gematria(max_pairs=500)
    with open(f'{output_dir}/comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"    Sample: {comparison['sample_size']} entries")
    print(f"    Standard equations: {comparison['standard_equations']}")
    print(f"    Dialetheic equations: {comparison['dialetheic_equations']}")
    print(f"    ENRICHMENT RATIO: {comparison['dialetheic_enrichment']:.1f}x")
    
    print(f"\n{'=' * 80}")
    print(f"Dialetheic gematria complete. Results in: {output_dir}/")
    print(f"{'=' * 80}")
    
    return idx


if __name__ == '__main__':
    run_dialetheic_gematria()
