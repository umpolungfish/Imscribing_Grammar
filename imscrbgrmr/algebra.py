"""
Imscription Algebra — lattice operations, canonical distance, and path search.

Canonical distance: primitive_mismatches(a, b) -> int
  Pure Hamming over all 12 fields. Matches the Lean kernel-verified
  primitiveMismatches in Imscription.lean. Returns 0 iff a == b (as 12-tuples).

Weighted distance: tuple_distance(a, b) -> float
  Per-primitive weights + ordinal gaps for F, K, G. For HotSwap / xi_CP
  scoring where structural proximity matters more than binary identity.

Lattice operations: meet(a, b), join(a, b) -> LatticeResult
  Ordered primitives (F, K, G, Omega, H): take min/max over ordinal.
  Categorical primitives (D, T, R, P, Gamma, S): require exact match
  or emit CONFLICT.
  Criticality is ordered too, but with an absorbing element: ⊙ absorbs under
  both meet and join, and the rest of the axis takes min/max like the others.
  A value off that axis emits CONFLICT, the way a categorical mismatch does.

Ordinal conventions match Lean Core.lean and the corrected models.py:
  F: F_noise(0) < F_beltl(1) < F_dh(2) < F_hardsign(3)
  K: K_lambda(0) < K_teshlig(1) < K_schwa(2) < K_turnm(3) < K_frtailgamma(4)
  G: G_revapostrophe(0) < G_beta(1) < G_gamma(2)   [aleph = finest, gimel = coarsest]
  Omega: Omega_closeepsilon(0) < Omega_crtwo(1) < Omega_dzlig(2) < Omega_C(3) < Omega_turna(4)
  H: H_closeomega(0) < H_toneletterstem(1) < H_turntwo(2) < H_invscripta(3)
  Criticality: woe(1) < monad(2) < roar(2.33) < err(2.67) < haha(3), the ranks
    read from the canonical table. Lean carries the same order at integer ranks;
    the fractional two are where the complex and exceptional-point criticalities
    sit between the real critical point and the supercritical phase.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .canonical_primitives import ORDINALS as _CANON_ORDINALS
from .models import (
    CONFLICT,
    Chirality,
    Criticality,
    Dimensionality,
    Fidelity,
    Grammar,
    Granularity,
    KineticChar,
    Polarity,
    Protection,
    Recognition,
    Stoichiometry,
    Imscription,
    Topology,
)

# ─────────────────────────────────────────────────────────────────────────────
# Ordinal maps (all aligned with Lean Core.lean)
# ─────────────────────────────────────────────────────────────────────────────

# Three values, not four. The retired below-threshold value sat under age and was
# rekeyed onto age itself, leaving a duplicate key whose second binding happened
# to give the right spacing. Written out so it is right on purpose, not by luck.
_F_ORD: Dict[Fidelity, int] = {
    Fidelity.age:  1,
    Fidelity.they: 2,
    Fidelity.peep: 3,
}
_F_BY_ORD = {v: k for k, v in _F_ORD.items()}

_K_ORD: Dict[KineticChar, int] = {
    KineticChar.air:  0,
    KineticChar.on: 1,
    KineticChar.egg: 2,
    KineticChar.loll:  3,
    KineticChar.yea: 4,
}
_K_BY_ORD = {v: k for k, v in _K_ORD.items()}

# FIXED: G_revapostrophe = finest (0), G_gamma = coarsest (2) — matches ℵ < ℶ < ℷ and Core.lean
_G_ORD: Dict[Granularity, int] = {
    Granularity.ice: 0,
    Granularity.bib:  1,
    Granularity.thigh: 2,
}
_G_BY_ORD = {v: k for k, v in _G_ORD.items()}

_PROT_ORD: Dict[Protection, int] = {
    Protection.awe:  0,
    Protection.oak: 1,
    Protection.ah:  2,
    Protection.ah:  3,
    Protection.zoo: 4,
}
_PROT_BY_ORD = {v: k for k, v in _PROT_ORD.items()}

_CHIR_ORD: Dict[Chirality, int] = {
    Chirality.fee:    0,
    Chirality.kick:    1,
    Chirality.sure:    2,
    Chirality.wool: 3,
}
_CHIR_BY_ORD = {v: k for k, v in _CHIR_ORD.items()}

# Criticality is the one ordered axis whose ranks are not consecutive integers:
# complex criticality and the exceptional point sit between the real critical
# point and the supercritical phase, at 2.33 and 2.67. Read from the canonical
# table rather than restated here, since restating it is how the map this
# replaces came to hold three of the five values and raise KeyError on a tuple
# carrying either of the others. 𐑧 is deliberately absent: the canonical order
# is five values, and the sixth is not on it.
_PHI_ORD: Dict[Criticality, float] = {
    c: _CANON_ORDINALS["⊙"][c.value]
    for c in Criticality if c.value in _CANON_ORDINALS["⊙"]
}

# ─────────────────────────────────────────────────────────────────────────────
# Canonical distance: primitive_mismatches
# ─────────────────────────────────────────────────────────────────────────────

def primitive_mismatches(a: Imscription, b: Imscription) -> int:
    """
    Canonical Hamming distance over the 12-primitive product.

    Matches the Lean kernel-verified primitiveMismatches in Imscription.lean:
      sum of (0 if a.field == b.field else 1) for each of the 12 fields.

    Returns an integer in [0, 12]. Zero iff the two imscriptions are identical
    as 12-tuples (name and metadata are ignored).
    """
    return int(
        (a.dimensionality    != b.dimensionality)   +
        (a.topology          != b.topology)          +
        (a.recognition_mode  != b.recognition_mode)  +
        (a.polarity          != b.polarity)          +
        (a.grammar           != b.grammar)           +
        (a.fidelity          != b.fidelity)          +
        (a.kinetic_character != b.kinetic_character) +
        (a.granularity       != b.granularity)       +
        (a.criticality_phase != b.criticality_phase) +
        (a.protection        != b.protection)        +
        (a.stoichiometry     != b.stoichiometry)     +
        (a.chirality         != b.chirality)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Weighted distance: tuple_distance
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "D":     2.0,   # dimensionality mismatch most penalised
    "T":     1.5,
    "R":     1.0,
    "P":     0.8,
    "Gamma": 0.6,
    "F":     0.6,   # per ordinal step
    "K":     0.5,   # per ordinal step
    "G":     0.4,   # per ordinal step
    "Phi":   0.3,
    "Omega": 0.7,   # ordinal gap × weight
    "S":     0.5,
    "H":     0.4,   # ordinal gap × weight
}


def tuple_distance(
    s1: Imscription,
    s2: Imscription,
    weights: Optional[Dict[str, float]] = None,
    symmetric: bool = True,
) -> float:
    """
    Weighted quasi-metric between two imscriptions.

    Uses ordinal gaps for F, K, G, Omega, H; binary mismatch for
    the categorical primitives D, T, R, P, Gamma, Phi, S.

    When symmetric=True: standard symmetric distance.
    When symmetric=False: directed distance d(s1→s2) — gives 0 for F/K
    components where s2 >= s1 (valid HotSwap upgrade direction).

    For the algebraically canonical unweighted distance use primitive_mismatches().
    """
    w = weights or _DEFAULT_WEIGHTS
    d = 0.0

    # Categorical — binary mismatch
    for key, v1, v2 in [
        ("D",     s1.dimensionality,   s2.dimensionality),
        ("T",     s1.topology,         s2.topology),
        ("R",     s1.recognition_mode, s2.recognition_mode),
        ("P",     s1.polarity,         s2.polarity),
        ("Gamma", s1.grammar,          s2.grammar),
        ("Phi",   s1.criticality_phase, s2.criticality_phase),
        ("S",     s1.stoichiometry,    s2.stoichiometry),
    ]:
        d += w.get(key, 1.0) * float(v1 != v2)

    # Fidelity — ordinal
    f_gap = _F_ORD[s2.fidelity] - _F_ORD[s1.fidelity]
    d += w.get("F", 0.6) * (abs(f_gap) if symmetric else max(0, -f_gap))

    # Kinetics — ordinal (directed: penalise only downgrade)
    k_gap = _K_ORD[s2.kinetic_character] - _K_ORD[s1.kinetic_character]
    d += w.get("K", 0.5) * (abs(k_gap) if symmetric else max(0, -k_gap))

    # Granularity — ordinal (always symmetric)
    g_gap = _G_ORD[s2.granularity] - _G_ORD[s1.granularity]
    d += w.get("G", 0.4) * abs(g_gap)

    # Topological protection — ordinal
    o_gap = _PROT_ORD[s2.protection] - _PROT_ORD[s1.protection]
    d += w.get("Omega", 0.7) * abs(o_gap)

    # Chirality — ordinal
    h_gap = _CHIR_ORD[s2.chirality] - _CHIR_ORD[s1.chirality]
    d += w.get("H", 0.4) * abs(h_gap)

    return d


# ─────────────────────────────────────────────────────────────────────────────
# Mahalanobis metric (full g_ij = Sigma^{-1} from catalog)
# ─────────────────────────────────────────────────────────────────────────────

_PRIMITIVES_FALLBACK: Dict[str, Dict[str, str]] = {
    # Values present in models.py but not in primitives.py ORDINALS.
    # Mapped to the nearest canonical primitives.py value.
    "D": {"𐑛": "𐑛", "𐑛": "𐑛", "𐑨": "𐑨"},
    # ⊣ Topology needs no fallback: all five values are in ORDINALS.
    "R": {
        "𐑑": "𐑑", "𐑩": "𐑩", "𐑩": "𐑩",
        "𐑽": "𐑽", "𐑽": "𐑽",
        "𐑾": "𐑽", "𐑾": "𐑾",
    },
    "P": {
        "𐑗": "𐑗", "𐑬": "𐑿", "𐑬": "𐑿",
        "𐑯": "Φ_subdoublearrow", "𐑬": "𐑬",
    },
    "F": {"𐑱": "𐑱"},
    "K": {"𐑺": "𐑪"},
    "Gamma": {"𐑵": "𐑵", "𐑠": "𐑠", "𐑜": "𐑜"},
    "Phi": {"⊙_upstep": "⊙_upstep"},
    "S": {"1:1": "Σ_doublebaresh", "1:n": "Σ_ctn", "n:m": "Σ_ltailm", "cat": "Σ_ltailm"},
    "Omega": {"Ω_C": "Ω_dzlig", "Ω_turna": "Ω_dzlig"},
}


def _imscription_to_primitives_dict(s: Imscription) -> Optional[Dict[str, str]]:
    """Convert a Imscription to the dict format expected by space_search/primitives.py.

    Extended enum values that postdate the catalog encoding are mapped to their
    nearest canonical equivalent via _PRIMITIVES_FALLBACK.  Returns None only
    if a value cannot be resolved even with the fallback table.
    """
    import os, sys
    _sp = os.path.join(os.path.dirname(__file__), "..", "space_search")
    if _sp not in sys.path:
        sys.path.insert(0, _sp)
    try:
        from primitives import ORDINALS  # type: ignore
    except ImportError:
        return None

    raw = {
        "D":     s.dimensionality.value,
        "T":     s.topology.value,
        "R":     s.recognition_mode.value,
        "P":     s.polarity.value,
        "F":     s.fidelity.value,
        "K":     s.kinetic_character.value,
        "G":     s.granularity.value,
        "Gamma": s.grammar.value,
        "Phi":   s.criticality_phase.value,
        "H":     s.chirality.value,
        "S":     s.stoichiometry.value,
        "Omega": s.protection.value,
    }
    resolved = {}
    for prim, val in raw.items():
        if val in ORDINALS.get(prim, {}):
            resolved[prim] = val
        elif val in _PRIMITIVES_FALLBACK.get(prim, {}):
            resolved[prim] = _PRIMITIVES_FALLBACK[prim][val]
        else:
            return None  # unresolvable — caller handles gracefully
    return resolved


_ALGEBRA_METRIC_G = None  # lazy-loaded


def mahalanobis_distance(s1: Imscription, s2: Imscription) -> Optional[float]:
    """Riemannian distance d = sqrt((v1-v2)^T g (v1-v2)) with g = Sigma^{-1}.

    Returns None if either imscription contains values outside the catalog ordinals
    or if the catalog cannot be located.
    """
    global _ALGEBRA_METRIC_G
    d1 = _imscription_to_primitives_dict(s1)
    d2 = _imscription_to_primitives_dict(s2)
    if d1 is None or d2 is None:
        return None

    import os, sys
    _sp = os.path.join(os.path.dirname(__file__), "..", "space_search")
    if _sp not in sys.path:
        sys.path.insert(0, _sp)
    try:
        from primitives import mahalanobis_distance as _maha, build_metric_tensor  # type: ignore
    except ImportError:
        return None

    if _ALGEBRA_METRIC_G is None:
        try:
            _ALGEBRA_METRIC_G = build_metric_tensor()
        except Exception:
            return None

    try:
        return _maha(d1, d2, _ALGEBRA_METRIC_G)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Lattice operations
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LatticeResult:
    """Result of a meet or join operation. CONFLICT marks categorical clashes."""
    operation:        str   # "meet" or "join"
    s1_name:          str
    s2_name:          str
    dimensionality:   Any   # Dimensionality or CONFLICT
    topology:         Any
    recognition_mode: Any
    polarity:         Any
    grammar:          Any
    fidelity:         Any   # Fidelity (always resolves — ordered)
    kinetic_character: Any
    granularity:      Any
    criticality_phase: Any  # Criticality or CONFLICT
    protection:       Any   # Protection (always resolves — ordered)
    stoichiometry:    Any   # Stoichiometry or CONFLICT
    chirality:        Any   # Chirality (always resolves — ordered)
    conflicts: List[str] = field(default_factory=list)
    notes:     List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.conflicts) == 0

    def to_dict(self) -> dict:
        def _val(x):
            if x == CONFLICT:
                return "CONFLICT"
            return x.value if hasattr(x, "value") else str(x)
        return {
            "operation":        self.operation,
            "s1_name":          self.s1_name,
            "s2_name":          self.s2_name,
            "dimensionality":   _val(self.dimensionality),
            "topology":         _val(self.topology),
            "recognition_mode": _val(self.recognition_mode),
            "polarity":         _val(self.polarity),
            "grammar":          _val(self.grammar),
            "fidelity":         _val(self.fidelity),
            "kinetic_character":_val(self.kinetic_character),
            "granularity":      _val(self.granularity),
            "criticality_phase":_val(self.criticality_phase),
            "protection":       _val(self.protection),
            "stoichiometry":    _val(self.stoichiometry),
            "chirality":        _val(self.chirality),
            "conflicts":        self.conflicts,
            "notes":            self.notes,
        }

    def to_notation(self) -> str:
        bot = "\u22a5" if self.operation == "meet" else "\u22a4"
        def _v(x):
            if x == CONFLICT:
                return bot
            return x.value if hasattr(x, "value") else (str(x) if x else "\u2014")
        vals = [
            _v(self.dimensionality), _v(self.topology),
            _v(self.recognition_mode), _v(self.polarity),
            _v(self.fidelity), _v(self.kinetic_character),
            _v(self.granularity), _v(self.grammar),
            _v(self.criticality_phase), _v(self.chirality),
            _v(self.stoichiometry), _v(self.protection),
        ]
        return f"\u27e8{''.join(vals)}\u27e9"

    # Backward compat
    @property
    def interaction_grammar(self): return self.grammar
    @property
    def topo_index(self): return self.protection


def _absorb_check(
    absorption_rules,
    prim_shavian: str,
    p1_val: Any,
    p2_val: Any,
    notes: List[str],
    op_symbol: str,
    op_name: str,
) -> Optional[Any]:
    """
    Check whether either operand is absorbing under the given operation.

    absorption_rules: iterable of (primitive, value, operations) tuples,
                      or None to use canonical defaults.
    prim_shavian:   Shavian glyph for this primitive (e.g., "⊙", "⊞")
    p1_val, p2_val: enum values with .value attribute giving the Shavian glyph
    op_name:        "meet", "join", or "tensor"

    Returns the absorbing value if applicable, else None.
    """
    if absorption_rules is None:
        return None
    for rule in absorption_rules:
        prim, val, ops = rule if isinstance(rule, tuple) else (rule.primitive, rule.value, rule.operations)
        if prim != prim_shavian:
            continue
        if op_name not in ops:
            continue
        v1 = p1_val.value if hasattr(p1_val, 'value') else str(p1_val)
        v2 = p2_val.value if hasattr(p2_val, 'value') else str(p2_val)
        if v1 == val:
            notes.append(f"{prim_shavian}: {v1} {op_symbol} {v2} → {v1} (absorbing)")
            return p1_val
        if v2 == val:
            notes.append(f"{prim_shavian}: {v1} {op_symbol} {v2} → {v2} (absorbing)")
            return p2_val
    return None


def _phi_absorb(p1: Criticality, p2: Criticality, notes: List[str], op: str,
                absorption=None, conflicts: Optional[List[str]] = None) -> Any:
    """Criticality absorption (generalized). ⊙ is absorbing under meet and join."""
    # Which operation this is, by the symbol the callers actually pass: ⊓ and ⊔,
    # the square cap and cup. Testing for ∩, the set intersection, matched
    # neither, so every call took the join branch and a meet of two criticalities
    # returned the higher of them.
    is_meet = op in ("⊓", "∩")
    # Check configurable absorption first
    if absorption is not None:
        absorbed = _absorb_check(absorption, "⊙", p1, p2, notes, op,
                                 "meet" if is_meet else "join")
        if absorbed is not None:
            return absorbed
    # Fall through to canonical behavior
    if p1 == p2:
        return p1
    if p1.is_degenerate:
        notes.append(f"<: {p1.value} {op} {p2.value} → {p1.value} (⊙ absorbing)")
        return p1
    if p2.is_degenerate:
        notes.append(f"<: {p1.value} {op} {p2.value} → {p2.value} (⊙ absorbing)")
        return p2
    # 𐑧 is a sixth value the canonical five-value order does not rank, so neither
    # the lower nor the higher of the pair means anything when it is one of them.
    # Report it the way a categorical mismatch is reported rather than invent a
    # rank to put it at one end of an axis it is not on.
    if p1 not in _PHI_ORD or p2 not in _PHI_ORD:
        off = p1 if p1 not in _PHI_ORD else p2
        notes.append(f"<: {off.value} is off the criticality order, "
                     f"so {p1.value} {op} {p2.value} does not resolve")
        if conflicts is not None:
            conflicts.append("Phi")
        return CONFLICT
    # Neither critical — meet takes lower, join takes higher in the linear order
    o1, o2 = _PHI_ORD[p1], _PHI_ORD[p2]
    lower, higher = (p1, p2) if o1 <= o2 else (p2, p1)
    return lower if is_meet else higher
def meet(s1: Imscription, s2: Imscription, absorption=None) -> LatticeResult:
    """
    Lattice meet (sqcap): greatest lower bound.

    Ordered primitives (F, K, G, Omega, H): take minimum (more conservative).
    Categorical (D, T, R, P, Gamma, S): exact match required; mismatch -> CONFLICT.
    ⊙ is absorbing: meet(⊙, x) = ⊙ for all x.
    absorption: optional iterable of (prim, val, ops) tuples for configurable absorption.
    """
    conflicts: List[str] = []
    notes: List[str] = []

    def _cat(key: str, v1: Any, v2: Any) -> Any:
        if v1 == v2:
            return v1
        conflicts.append(key)
        return CONFLICT

    def _ord(key: str, v1: Any, v2: Any, ord_map: dict, by_ord: dict) -> Any:
        o1, o2 = ord_map[v1], ord_map[v2]
        result = by_ord[min(o1, o2)]
        if o1 != o2:
            notes.append(f"{key}: {v1.value} \u2293 {v2.value} \u2192 {result.value}")
        return result

    return LatticeResult(
        operation="meet",
        s1_name=s1.name, s2_name=s2.name,
        dimensionality   = _cat("D",     s1.dimensionality,    s2.dimensionality),
        topology         = _cat("T",     s1.topology,          s2.topology),
        recognition_mode = _cat("R",     s1.recognition_mode,  s2.recognition_mode),
        polarity         = _cat("P",     s1.polarity,          s2.polarity),
        grammar          = _cat("Gamma", s1.grammar,           s2.grammar),
        fidelity         = _ord("F",     s1.fidelity,          s2.fidelity,          _F_ORD,    _F_BY_ORD),
        kinetic_character= _ord("K",     s1.kinetic_character, s2.kinetic_character, _K_ORD,    _K_BY_ORD),
        granularity      = _ord("G",     s1.granularity,       s2.granularity,       _G_ORD,    _G_BY_ORD),
        criticality_phase= _phi_absorb(s1.criticality_phase, s2.criticality_phase, notes, "\u2293", absorption, conflicts),
        protection       = _ord("Omega", s1.protection,        s2.protection,        _PROT_ORD, _PROT_BY_ORD),
        stoichiometry    = _cat("S",     s1.stoichiometry,     s2.stoichiometry),
        chirality        = _ord("H",     s1.chirality,         s2.chirality,         _CHIR_ORD, _CHIR_BY_ORD),
        conflicts=conflicts, notes=notes,
    )


def join(s1: Imscription, s2: Imscription, absorption=None) -> LatticeResult:
    """
    Lattice join (sqcup): least upper bound.

    Ordered primitives: take maximum (more permissive / demanding).
    Categorical: exact match or CONFLICT.
    ⊙ is absorbing: join(⊙, x) = ⊙ for all x.
    absorption: optional iterable of (prim, val, ops) tuples for configurable absorption.
    """
    conflicts: List[str] = []
    notes: List[str] = []

    def _cat(key: str, v1: Any, v2: Any) -> Any:
        if v1 == v2:
            return v1
        conflicts.append(key)
        return CONFLICT

    def _ord(key: str, v1: Any, v2: Any, ord_map: dict, by_ord: dict) -> Any:
        o1, o2 = ord_map[v1], ord_map[v2]
        result = by_ord[max(o1, o2)]
        if o1 != o2:
            notes.append(f"{key}: {v1.value} \u2294 {v2.value} \u2192 {result.value}")
        return result

    return LatticeResult(
        operation="join",
        s1_name=s1.name, s2_name=s2.name,
        dimensionality   = _cat("D",     s1.dimensionality,    s2.dimensionality),
        topology         = _cat("T",     s1.topology,          s2.topology),
        recognition_mode = _cat("R",     s1.recognition_mode,  s2.recognition_mode),
        polarity         = _cat("P",     s1.polarity,          s2.polarity),
        grammar          = _cat("Gamma", s1.grammar,           s2.grammar),
        fidelity         = _ord("F",     s1.fidelity,          s2.fidelity,          _F_ORD,    _F_BY_ORD),
        kinetic_character= _ord("K",     s1.kinetic_character, s2.kinetic_character, _K_ORD,    _K_BY_ORD),
        granularity      = _ord("G",     s1.granularity,       s2.granularity,       _G_ORD,    _G_BY_ORD),
        criticality_phase= _phi_absorb(s1.criticality_phase, s2.criticality_phase, notes, "\u2294", absorption, conflicts),
        protection       = _ord("Omega", s1.protection,        s2.protection,        _PROT_ORD, _PROT_BY_ORD),
        stoichiometry    = _cat("S",     s1.stoichiometry,     s2.stoichiometry),
        chirality        = _ord("H",     s1.chirality,         s2.chirality,         _CHIR_ORD, _CHIR_BY_ORD),
        conflicts=conflicts, notes=notes,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Path search (HotSwap)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PathResult:
    found:       bool
    src_name:    str
    dst_name:    str
    path:        List[str]
    hop_deltas:  List[float]
    total_delta: float
    notes:       List[str] = field(default_factory=list)

    @property
    def n_hops(self) -> int:
        return len(self.path) - 1


def find_path(
    src: Imscription,
    dst: Imscription,
    catalog: Sequence[Imscription],
    max_hops: int = 6,
    xi_tolerance: float = 1.0,
    ignore_grounding: bool = True,
) -> PathResult:
    """
    Shortest valid HotSwap path from src to dst through the catalog.

    Uses directed tuple_distance (symmetric=False) as the hop cost so that
    upward moves in F/K are free. Restricts to imscriptions sharing src.dim and
    src.top (HotSwap hard constraint: D and T cannot change mid-path).
    """
    try:
        from .thermodynamics import compute_xi_CP
    except ImportError:
        compute_xi_CP = lambda s, delta_g=0.0: 0.0  # noqa: E731

    # Filter catalog to same D/T cluster
    candidates = [
        s for s in catalog
        if s.dimensionality == src.dimensionality
        and s.topology == src.topology
        and (ignore_grounding or s.is_grounded)
    ]

    # BFS / greedy hop via directed distance
    visited = {src.name}
    current = src
    path = [src.name]
    hop_deltas: List[float] = []

    for _ in range(max_hops):
        if current.name == dst.name or primitive_mismatches(current, dst) == 0:
            break
        # Find best next hop (min directed distance to dst)
        best: Optional[Imscription] = None
        best_d = float("inf")
        for cand in candidates:
            if cand.name in visited:
                continue
            d = tuple_distance(current, cand, symmetric=False)
            if d < best_d:
                best_d = d
                best = cand
        if best is None:
            break
        xi1 = compute_xi_CP(current, delta_g=0.0)
        xi2 = compute_xi_CP(best, delta_g=0.0)
        hop_deltas.append(abs(xi2 - xi1))
        path.append(best.name)
        visited.add(best.name)
        current = best

    found = primitive_mismatches(current, dst) == 0
    return PathResult(
        found=found,
        src_name=src.name,
        dst_name=dst.name,
        path=path,
        hop_deltas=hop_deltas,
        total_delta=sum(hop_deltas),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tensor product
# ─────────────────────────────────────────────────────────────────────────────

def tensor(s1: Imscription, s2: Imscription, name: Optional[str] = None, absorption=None) -> Imscription:
    """
    Tensor product of two imscriptions (co-assembly / ensemble encoding).

    Uses join for ordered primitives (F, K, G, Omega, H — take the more demanding)
    and requires exact match for categorical primitives (conflict raises ValueError).
    ⊙ absorbs in both operands.
    absorption: optional iterable of (prim, val, ops) tuples for configurable absorption
                (e.g., Σ n:m absorbs under tensor).
    """
    import imscrbgrmr.models as _m
    result = join(s1, s2, absorption=absorption)
    if not result.is_valid:
        raise ValueError(
            f"tensor({s1.name}, {s2.name}): categorical conflicts on "
            f"{result.conflicts} — tensor product undefined"
        )

    # Σ absorption under tensor: if either operand has the absorbing Σ value, it dominates
    stoi = result.stoichiometry
    if absorption is not None:
        absorbed_stoi = _absorb_check(absorption, "⊞", s1.stoichiometry, s2.stoichiometry,
                                      [], "⊗", "tensor")
        if absorbed_stoi is not None:
            stoi = absorbed_stoi

    old_enforce = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        t = Imscription(
            name             = name or f"tensor({s1.name},{s2.name})",
            dimensionality   = result.dimensionality,
            topology         = result.topology,
            recognition_mode = result.recognition_mode,
            polarity         = result.polarity,
            grammar          = result.grammar,
            fidelity         = result.fidelity,
            kinetic_character= result.kinetic_character,
            granularity      = result.granularity,
            criticality_phase= result.criticality_phase,
            protection       = result.protection,
            stoichiometry    = stoi,
            chirality        = result.chirality,
        )
    finally:
        _m._ENFORCE_AXIOMS = old_enforce
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Lift operations + _LIFT_MAP
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LiftResult:
    applicable: bool
    imscription: Optional[Imscription]
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _lift_temporal(s: Imscription) -> LiftResult:
    """D_* → D_invomega: inject temporal/iterative dimension."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality == Dimensionality.array:
        return LiftResult(True, s, notes=["Already D_invomega — no change"])
    if s.dimensionality == Dimensionality.if_:
        return LiftResult(False, None, notes=["D_omega subsumes D_invomega; lift not applicable"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.array,
                         name=f"{s.name}[+temporal]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result, notes=[f"D {s.dimensionality.value} → D_invomega"])


def _lift_spatial(s: Imscription) -> LiftResult:
    """D_wynn → D_cube: molecular → supramolecular spatial array."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality not in (Dimensionality.dead, Dimensionality.dead, Dimensionality.dead):
        return LiftResult(False, None,
                          notes=[f"Spatial lift requires D_wynn or lower; got {s.dimensionality.value}"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.ash,
                         name=f"{s.name}[+spatial]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result, notes=[f"D {s.dimensionality.value} → D_cube"])


def _lift_critical(s: Imscription, strength: float = 1.0) -> LiftResult:
    """𐑢 → ⊙: inject criticality. Requires F ≥ F_hardsign."""
    import imscrbgrmr.models as _m
    from .models import Criticality, Fidelity
    warnings = []
    if s.fidelity not in (Fidelity.peep,):
        warnings.append(f"F={s.fidelity.value} < F_hardsign — criticality injection is fragile")
    if s.criticality_phase == Criticality.monad:
        return LiftResult(True, s, notes=["Already ⊙ — no change"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, criticality_phase=Criticality.monad,
                         name=f"{s.name}[+critical]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result,
                      notes=[f"< {s.criticality_phase.value} → ⊙ (strength={strength:.2f})"],
                      warnings=warnings)


def _lift_molecular(s: Imscription) -> LiftResult:
    """Forgetful projection → D_wynn (loses spatial/temporal)."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality == Dimensionality.dead:
        return LiftResult(True, s, notes=["Already D_wynn — no change"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.dead,
                         name=f"{s.name}[->molecular]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result,
                      notes=[f"D {s.dimensionality.value} → D_wynn (forgetful)"],
                      warnings=["Forgetful projection — spatial/temporal structure lost"])


def _imscription_from_lattice(r: "LatticeResult", s1: Imscription, s2: Imscription, op: str) -> Imscription:
    """Extract a Imscription from a LatticeResult, substituting s1 values for conflicts."""
    import imscrbgrmr.models as _m
    CONFLICT = object.__class__  # sentinel check
    def _resolve(val, fallback):
        # CONFLICT sentinel is a string "CONFLICT" in the result
        if val is None or str(val) == "CONFLICT":
            return fallback
        return val
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from .models import Dimensionality, Topology, Recognition, Polarity, Grammar
        t = Imscription(
            name             = f"{op}({s1.name},{s2.name})",
            dimensionality   = _resolve(r.dimensionality,    s1.dimensionality),
            topology         = _resolve(r.topology,          s1.topology),
            recognition_mode = _resolve(r.recognition_mode,  s1.recognition_mode),
            polarity         = _resolve(r.polarity,           s1.polarity),
            grammar          = _resolve(r.grammar,            s1.grammar),
            fidelity         = _resolve(r.fidelity,           s1.fidelity),
            kinetic_character= _resolve(r.kinetic_character,  s1.kinetic_character),
            granularity      = _resolve(r.granularity,        s1.granularity),
            criticality_phase= _resolve(r.criticality_phase,  s1.criticality_phase),
            protection       = _resolve(r.protection,         s1.protection),
            stoichiometry    = _resolve(r.stoichiometry,      s1.stoichiometry),
            chirality        = _resolve(r.chirality,          s1.chirality),
        )
    finally:
        _m._ENFORCE_AXIOMS = old
    return t


_LIFT_MAP: Dict[str, Any] = {
    "temporal":    _lift_temporal,
    "spatial":     _lift_spatial,
    "critical":    _lift_critical,
    "criticality": _lift_critical,
    "molecular":   _lift_molecular,
}


# ─────────────────────────────────────────────────────────────────────────────
# DesignPipeline — fluent builder over algebra operations
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PipelineStep:
    op:          str
    input_name:  str
    output_name: str
    delta_xi:    Optional[float] = None
    notes:       str = ""
    warnings:    str = ""
    blocked:     bool = False
    block_reason: Optional[str] = None


@dataclass
class PipelineResult:
    value:         Optional[Imscription]
    steps:         List[PipelineStep]
    total_xi_delta: float
    failed:        bool
    failed_at:     Optional[str] = None
    failure_reason: Optional[str] = None

    def print_trace(self) -> None:
        status = "[FAILED]" if self.failed else "[OK]"
        print(f"\nPipeline result: {status}")
        if self.value:
            print(f"  Final imscription : {self.value.name}")
            print(f"  Notation      : {self.value.to_notation()}")
        print(f"  Total Δξ_CP   : {self.total_xi_delta:.4f} nats")
        print()
        for i, s in enumerate(self.steps, 1):
            tag = "BLOCKED" if s.blocked else "OK"
            print(f"  Step {i}: [{tag}] {s.op}({s.input_name}) → {s.output_name}")
            if s.notes:
                print(f"          {s.notes}")
            if s.warnings:
                print(f"          ⚠ {s.warnings}")
            if s.block_reason:
                print(f"          ✗ {s.block_reason}")
        if self.failed_at:
            print(f"\n  Failed at: {self.failed_at}")
            print(f"  Reason   : {self.failure_reason}")


class DesignPipeline:
    """Fluent builder for chained imscription algebra operations."""

    def __init__(self, imscription: Optional[Imscription], steps: List[PipelineStep],
                 xi_total: float, failed: bool,
                 failed_at: Optional[str] = None,
                 failure_reason: Optional[str] = None):
        self._imscription = imscription
        self._steps = steps
        self._xi_total = xi_total
        self._failed = failed
        self._failed_at = failed_at
        self._failure_reason = failure_reason

    @classmethod
    def start(cls, imscription: Imscription) -> "DesignPipeline":
        return cls(imscription, [], 0.0, False)

    def _fail(self, op: str, input_name: str, reason: str) -> "DesignPipeline":
        step = PipelineStep(op=op, input_name=input_name, output_name="—",
                            blocked=True, block_reason=reason)
        return DesignPipeline(None, self._steps + [step], self._xi_total,
                              True, failed_at=op, failure_reason=reason)

    def meet(self, other: Imscription) -> "DesignPipeline":
        if self._failed or self._imscription is None:
            return self
        try:
            r = meet(self._imscription, other)
            out = _imscription_from_lattice(r, self._imscription, other, "meet")
            notes = "; ".join(r.notes) if r.notes else ""
            warnings = f"conflicts on {r.conflicts}" if r.conflicts else ""
            step = PipelineStep("meet", other.name, out.name, notes=notes, warnings=warnings)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("meet", other.name, str(e))

    def join(self, other: Imscription) -> "DesignPipeline":
        if self._failed or self._imscription is None:
            return self
        try:
            r = join(self._imscription, other)
            out = _imscription_from_lattice(r, self._imscription, other, "join")
            notes = "; ".join(r.notes) if r.notes else ""
            warnings = f"conflicts on {r.conflicts}" if r.conflicts else ""
            step = PipelineStep("join", other.name, out.name, notes=notes, warnings=warnings)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("join", other.name, str(e))

    def tensor(self, other: Imscription, lambda_: float = 0.3) -> "DesignPipeline":
        if self._failed or self._imscription is None:
            return self
        try:
            out = tensor(self._imscription, other)
            step = PipelineStep("tensor", other.name, out.name)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except ValueError as e:
            return self._fail("tensor", other.name, str(e))

    def lift(self, target: str, **kw) -> "DesignPipeline":
        if self._failed or self._imscription is None:
            return self
        fn = _LIFT_MAP.get(target)
        if fn is None:
            return self._fail("lift", target,
                              f"Unknown lift target '{target}'. Valid: {list(_LIFT_MAP)}")
        try:
            r = fn(self._imscription, **kw)
            if not r.applicable:
                step = PipelineStep("lift", target, "—", blocked=True,
                                    block_reason="; ".join(r.notes))
                return DesignPipeline(None, self._steps + [step], self._xi_total,
                                      True, "lift", "; ".join(r.notes))
            out = r.imscription or self._imscription
            step = PipelineStep("lift", target, out.name,
                                notes="; ".join(r.notes),
                                warnings="; ".join(r.warnings))
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("lift", target, str(e))

    def path(self, target: Imscription, catalog: Any,
             max_hops: int = 6, xi_tolerance: float = 1.0) -> "DesignPipeline":
        if self._failed or self._imscription is None:
            return self
        try:
            r = find_path(self._imscription, target,
                          list(catalog) if not isinstance(catalog, list) else catalog,
                          max_hops=max_hops)
            if not r.found:
                return self._fail("path", target.name, "No valid path found")
            out = r.path[-1] if r.path else self._imscription
            step = PipelineStep("path", target.name, out.name,
                                delta_xi=r.total_delta,
                                notes=f"{len(r.path)} hops, Δξ={r.total_delta:.3f}")
            return DesignPipeline(out, self._steps + [step],
                                  self._xi_total + (r.total_delta or 0.0), False)
        except Exception as e:
            return self._fail("path", target.name, str(e))

    def result(self) -> PipelineResult:
        return PipelineResult(
            value=self._imscription,
            steps=self._steps,
            total_xi_delta=self._xi_total,
            failed=self._failed,
            failed_at=self._failed_at,
            failure_reason=self._failure_reason,
        )
