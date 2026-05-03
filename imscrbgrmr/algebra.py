"""
Synthon Algebra — lattice operations, canonical distance, and path search.

Canonical distance: primitive_mismatches(a, b) -> int
  Pure Hamming over all 12 fields. Matches the Lean kernel-verified
  primitiveMismatches in Synthon.lean. Returns 0 iff a == b (as 12-tuples).

Weighted distance: tuple_distance(a, b) -> float
  Per-primitive weights + ordinal gaps for F, K, G. For HotSwap / xi_CP
  scoring where structural proximity matters more than binary identity.

Lattice operations: meet(a, b), join(a, b) -> LatticeResult
  Ordered primitives (F, K, G, Omega, H): take min/max over ordinal.
  Categorical primitives (D, T, R, P, Gamma, Phi, S): require exact match
  or emit CONFLICT.
  Special: Phi_c is absorbing under both meet and join.

Ordinal conventions match Lean Core.lean and the corrected models.py:
  F: F_noise(0) < F_ell(1) < F_eth(2) < F_hbar(3)
  K: K_MBL(0) < K_trap(1) < K_slow(2) < K_mod(3) < K_fast(4)
  G: G_aleph(0) < G_beth(1) < G_gimel(2)   [aleph = finest, gimel = coarsest]
  Omega: Omega_0(0) < Omega_Z2(1) < Omega_Z(2) < Omega_C(3) < Omega_NA(4)
  H: H0(0) < H1(1) < H2(2) < H_inf(3)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

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
    Synthon,
    Topology,
)

# ─────────────────────────────────────────────────────────────────────────────
# Ordinal maps (all aligned with Lean Core.lean)
# ─────────────────────────────────────────────────────────────────────────────

_F_ORD: Dict[Fidelity, int] = {
    Fidelity.F_noise: 0,
    Fidelity.F_ell:   1,
    Fidelity.F_eth:   2,
    Fidelity.F_hbar:  3,
}
_F_BY_ORD = {v: k for k, v in _F_ORD.items()}

_K_ORD: Dict[KineticChar, int] = {
    KineticChar.K_MBL:  0,
    KineticChar.K_trap: 1,
    KineticChar.K_slow: 2,
    KineticChar.K_mod:  3,
    KineticChar.K_fast: 4,
}
_K_BY_ORD = {v: k for k, v in _K_ORD.items()}

# FIXED: G_aleph = finest (0), G_gimel = coarsest (2) — matches ℵ < ℶ < ℷ and Core.lean
_G_ORD: Dict[Granularity, int] = {
    Granularity.G_aleph: 0,
    Granularity.G_beth:  1,
    Granularity.G_gimel: 2,
}
_G_BY_ORD = {v: k for k, v in _G_ORD.items()}

_PROT_ORD: Dict[Protection, int] = {
    Protection.Omega_0:  0,
    Protection.Omega_Z2: 1,
    Protection.Omega_Z:  2,
    Protection.Omega_C:  3,
    Protection.Omega_NA: 4,
}
_PROT_BY_ORD = {v: k for k, v in _PROT_ORD.items()}

_CHIR_ORD: Dict[Chirality, int] = {
    Chirality.H0:    0,
    Chirality.H1:    1,
    Chirality.H2:    2,
    Chirality.H_inf: 3,
}
_CHIR_BY_ORD = {v: k for k, v in _CHIR_ORD.items()}

# ─────────────────────────────────────────────────────────────────────────────
# Canonical distance: primitive_mismatches
# ─────────────────────────────────────────────────────────────────────────────

def primitive_mismatches(a: Synthon, b: Synthon) -> int:
    """
    Canonical Hamming distance over the 12-primitive product.

    Matches the Lean kernel-verified primitiveMismatches in Synthon.lean:
      sum of (0 if a.field == b.field else 1) for each of the 12 fields.

    Returns an integer in [0, 12]. Zero iff the two synthons are identical
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
    s1: Synthon,
    s2: Synthon,
    weights: Optional[Dict[str, float]] = None,
    symmetric: bool = True,
) -> float:
    """
    Weighted quasi-metric between two synthons.

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
    "D": {"D_point": "D_wedge", "D_line": "D_wedge", "D_cube": "D_triangle"},
    "T": {
        "T_linear": "T_in", "T_branched": "T_in",
        "T_bowl": "T_bowtie", "T_cage": "T_bowtie", "T_torus": "T_bowtie",
        "T_braid": "T_boxtimes",
        "T_network_hex": "T_network", "T_network_interp": "T_network",
        "T_network_mixed": "T_network", "T_network_sym": "T_network",
    },
    "R": {
        "R_exact": "R_cat", "R_subset": "R_super", "R_superset": "R_super",
        "R_catalytic": "R_dagger", "R_allosteric": "R_dagger",
        "R_mechanical": "R_dagger", "R_covalent_dynamic": "R_lr",
    },
    "P": {
        "P_directional": "P_asym", "P_minus": "P_psi", "P_plus": "P_psi",
        "P_neutral": "P_sym", "P_pm_pseudo": "P_pm",
    },
    "F": {"F_noise": "F_ell"},
    "K": {"K_MBL": "K_trap"},
    "Gamma": {"G_dissipative": "G_broad", "G_impl": "G_and", "G_xor": "G_or"},
    "Phi": {"Phi_sup": "Phi_super"},
    "S": {"1:1": "one_one", "1:n": "n_n", "n:m": "n_m", "cat": "n_m"},
    "Omega": {"Omega_C": "Omega_Z", "Omega_NA": "Omega_Z"},
}


def _synthon_to_primitives_dict(s: Synthon) -> Optional[Dict[str, str]]:
    """Convert a Synthon to the dict format expected by space_search/primitives.py.

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


def mahalanobis_distance(s1: Synthon, s2: Synthon) -> Optional[float]:
    """Riemannian distance d = sqrt((v1-v2)^T g (v1-v2)) with g = Sigma^{-1}.

    Returns None if either synthon contains values outside the catalog ordinals
    or if the catalog cannot be located.
    """
    global _ALGEBRA_METRIC_G
    d1 = _synthon_to_primitives_dict(s1)
    d2 = _synthon_to_primitives_dict(s2)
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

    def to_notation(self) -> str:
        bot = "\u22a5" if self.operation == "meet" else "\u22a4"
        def _v(x):
            if x == CONFLICT:
                return bot
            return x.value if hasattr(x, "value") else (str(x) if x else "\u2014")
        return (
            f"\u27e8{_v(self.dimensionality)}; {_v(self.topology)}; "
            f"{_v(self.recognition_mode)}; {_v(self.polarity)}; "
            f"{_v(self.fidelity)}; {_v(self.kinetic_character)}; "
            f"{_v(self.granularity)}; {_v(self.grammar)}; "
            f"{_v(self.criticality_phase)}; {_v(self.protection)}; "
            f"{_v(self.stoichiometry)}; {_v(self.chirality)}\u27e9"
        )

    # Backward compat
    @property
    def interaction_grammar(self): return self.grammar
    @property
    def topo_index(self): return self.protection


def _phi_absorb(p1: Criticality, p2: Criticality, notes: List[str], op: str) -> Criticality:
    """Phi_c is absorbing under both meet and join."""
    if p1 == p2:
        return p1
    if p1.is_degenerate:
        notes.append(f"\u03a6: {p1.value} {op} {p2.value} \u2192 {p1.value} (\u03a6_c absorbing)")
        return p1
    if p2.is_degenerate:
        notes.append(f"\u03a6: {p1.value} {op} {p2.value} \u2192 {p2.value} (\u03a6_c absorbing)")
        return p2
    # Neither critical — meet takes lower, join takes higher in the linear order
    phi_ord = {Criticality.Phi_sub: 0, Criticality.Phi_c: 1, Criticality.Phi_sup: 2}
    result = min if op == "\u2293" else max
    idx = result(phi_ord[p1], phi_ord[p2])
    return [Criticality.Phi_sub, Criticality.Phi_c, Criticality.Phi_sup][idx]


def meet(s1: Synthon, s2: Synthon) -> LatticeResult:
    """
    Lattice meet (sqcap): greatest lower bound.

    Ordered primitives (F, K, G, Omega, H): take minimum (more conservative).
    Categorical (D, T, R, P, Gamma, S): exact match required; mismatch -> CONFLICT.
    Phi_c is absorbing: meet(Phi_c, x) = Phi_c for all x.
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
        criticality_phase= _phi_absorb(s1.criticality_phase, s2.criticality_phase, notes, "\u2293"),
        protection       = _ord("Omega", s1.protection,        s2.protection,        _PROT_ORD, _PROT_BY_ORD),
        stoichiometry    = _cat("S",     s1.stoichiometry,     s2.stoichiometry),
        chirality        = _ord("H",     s1.chirality,         s2.chirality,         _CHIR_ORD, _CHIR_BY_ORD),
        conflicts=conflicts, notes=notes,
    )


def join(s1: Synthon, s2: Synthon) -> LatticeResult:
    """
    Lattice join (sqcup): least upper bound.

    Ordered primitives: take maximum (more permissive / demanding).
    Categorical: exact match or CONFLICT.
    Phi_c is absorbing: join(Phi_c, x) = Phi_c for all x.
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
        criticality_phase= _phi_absorb(s1.criticality_phase, s2.criticality_phase, notes, "\u2294"),
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
    src: Synthon,
    dst: Synthon,
    catalog: Sequence[Synthon],
    max_hops: int = 6,
    xi_tolerance: float = 1.0,
    ignore_grounding: bool = True,
) -> PathResult:
    """
    Shortest valid HotSwap path from src to dst through the catalog.

    Uses directed tuple_distance (symmetric=False) as the hop cost so that
    upward moves in F/K are free. Restricts to synthons sharing src.dim and
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
        best: Optional[Synthon] = None
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

def tensor(s1: Synthon, s2: Synthon, name: Optional[str] = None) -> Synthon:
    """
    Tensor product of two synthons (co-assembly / ensemble encoding).

    Uses join for ordered primitives (F, K, G, Omega, H — take the more demanding)
    and requires exact match for categorical primitives (conflict raises ValueError).
    Phi_c absorbs in both operands.
    """
    import imscrbgrmr.models as _m
    result = join(s1, s2)
    if not result.is_valid:
        raise ValueError(
            f"tensor({s1.name}, {s2.name}): categorical conflicts on "
            f"{result.conflicts} — tensor product undefined"
        )

    old_enforce = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        t = Synthon(
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
            stoichiometry    = result.stoichiometry,
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
    synthon: Optional[Synthon]
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _lift_temporal(s: Synthon) -> LiftResult:
    """D_* → D_infty: inject temporal/iterative dimension."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality == Dimensionality.D_infty:
        return LiftResult(True, s, notes=["Already D_infty — no change"])
    if s.dimensionality == Dimensionality.D_holo:
        return LiftResult(False, None, notes=["D_odot subsumes D_infty; lift not applicable"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.D_infty,
                         name=f"{s.name}[+temporal]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result, notes=[f"D {s.dimensionality.value} → D_infty"])


def _lift_spatial(s: Synthon) -> LiftResult:
    """D_wedge → D_cube: molecular → supramolecular spatial array."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality not in (Dimensionality.D_wedge, Dimensionality.D_point, Dimensionality.D_line):
        return LiftResult(False, None,
                          notes=[f"Spatial lift requires D_wedge or lower; got {s.dimensionality.value}"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.D_cube,
                         name=f"{s.name}[+spatial]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result, notes=[f"D {s.dimensionality.value} → D_cube"])


def _lift_critical(s: Synthon, strength: float = 1.0) -> LiftResult:
    """Φ_sub → Φ_c: inject criticality. Requires F ≥ F_hbar."""
    import imscrbgrmr.models as _m
    from .models import Criticality, Fidelity
    warnings = []
    if s.fidelity not in (Fidelity.F_hbar,):
        warnings.append(f"F={s.fidelity.value} < F_hbar — criticality injection is fragile")
    if s.criticality_phase == Criticality.Phi_c:
        return LiftResult(True, s, notes=["Already Phi_c — no change"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, criticality_phase=Criticality.Phi_c,
                         name=f"{s.name}[+critical]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result,
                      notes=[f"Φ {s.criticality_phase.value} → Phi_c (strength={strength:.2f})"],
                      warnings=warnings)


def _lift_molecular(s: Synthon) -> LiftResult:
    """Forgetful projection → D_wedge (loses spatial/temporal)."""
    import imscrbgrmr.models as _m
    from .models import Dimensionality
    if s.dimensionality == Dimensionality.D_wedge:
        return LiftResult(True, s, notes=["Already D_wedge — no change"])
    old = _m._ENFORCE_AXIOMS
    _m._ENFORCE_AXIOMS = False
    try:
        from dataclasses import replace
        result = replace(s, dimensionality=Dimensionality.D_wedge,
                         name=f"{s.name}[->molecular]")
    finally:
        _m._ENFORCE_AXIOMS = old
    return LiftResult(True, result,
                      notes=[f"D {s.dimensionality.value} → D_wedge (forgetful)"],
                      warnings=["Forgetful projection — spatial/temporal structure lost"])


def _synthon_from_lattice(r: "LatticeResult", s1: Synthon, s2: Synthon, op: str) -> Synthon:
    """Extract a Synthon from a LatticeResult, substituting s1 values for conflicts."""
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
        t = Synthon(
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
    value:         Optional[Synthon]
    steps:         List[PipelineStep]
    total_xi_delta: float
    failed:        bool
    failed_at:     Optional[str] = None
    failure_reason: Optional[str] = None

    def print_trace(self) -> None:
        status = "[FAILED]" if self.failed else "[OK]"
        print(f"\nPipeline result: {status}")
        if self.value:
            print(f"  Final synthon : {self.value.name}")
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
    """Fluent builder for chained synthon algebra operations."""

    def __init__(self, synthon: Optional[Synthon], steps: List[PipelineStep],
                 xi_total: float, failed: bool,
                 failed_at: Optional[str] = None,
                 failure_reason: Optional[str] = None):
        self._synthon = synthon
        self._steps = steps
        self._xi_total = xi_total
        self._failed = failed
        self._failed_at = failed_at
        self._failure_reason = failure_reason

    @classmethod
    def start(cls, synthon: Synthon) -> "DesignPipeline":
        return cls(synthon, [], 0.0, False)

    def _fail(self, op: str, input_name: str, reason: str) -> "DesignPipeline":
        step = PipelineStep(op=op, input_name=input_name, output_name="—",
                            blocked=True, block_reason=reason)
        return DesignPipeline(None, self._steps + [step], self._xi_total,
                              True, failed_at=op, failure_reason=reason)

    def meet(self, other: Synthon) -> "DesignPipeline":
        if self._failed or self._synthon is None:
            return self
        try:
            r = meet(self._synthon, other)
            out = _synthon_from_lattice(r, self._synthon, other, "meet")
            notes = "; ".join(r.notes) if r.notes else ""
            warnings = f"conflicts on {r.conflicts}" if r.conflicts else ""
            step = PipelineStep("meet", other.name, out.name, notes=notes, warnings=warnings)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("meet", other.name, str(e))

    def join(self, other: Synthon) -> "DesignPipeline":
        if self._failed or self._synthon is None:
            return self
        try:
            r = join(self._synthon, other)
            out = _synthon_from_lattice(r, self._synthon, other, "join")
            notes = "; ".join(r.notes) if r.notes else ""
            warnings = f"conflicts on {r.conflicts}" if r.conflicts else ""
            step = PipelineStep("join", other.name, out.name, notes=notes, warnings=warnings)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("join", other.name, str(e))

    def tensor(self, other: Synthon, lambda_: float = 0.3) -> "DesignPipeline":
        if self._failed or self._synthon is None:
            return self
        try:
            out = tensor(self._synthon, other)
            step = PipelineStep("tensor", other.name, out.name)
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except ValueError as e:
            return self._fail("tensor", other.name, str(e))

    def lift(self, target: str, **kw) -> "DesignPipeline":
        if self._failed or self._synthon is None:
            return self
        fn = _LIFT_MAP.get(target)
        if fn is None:
            return self._fail("lift", target,
                              f"Unknown lift target '{target}'. Valid: {list(_LIFT_MAP)}")
        try:
            r = fn(self._synthon, **kw)
            if not r.applicable:
                step = PipelineStep("lift", target, "—", blocked=True,
                                    block_reason="; ".join(r.notes))
                return DesignPipeline(None, self._steps + [step], self._xi_total,
                                      True, "lift", "; ".join(r.notes))
            out = r.synthon or self._synthon
            step = PipelineStep("lift", target, out.name,
                                notes="; ".join(r.notes),
                                warnings="; ".join(r.warnings))
            return DesignPipeline(out, self._steps + [step], self._xi_total, False)
        except Exception as e:
            return self._fail("lift", target, str(e))

    def path(self, target: Synthon, catalog: Any,
             max_hops: int = 6, xi_tolerance: float = 1.0) -> "DesignPipeline":
        if self._failed or self._synthon is None:
            return self
        try:
            r = find_path(self._synthon, target,
                          list(catalog) if not isinstance(catalog, list) else catalog,
                          max_hops=max_hops)
            if not r.found:
                return self._fail("path", target.name, "No valid path found")
            out = r.path[-1] if r.path else self._synthon
            step = PipelineStep("path", target.name, out.name,
                                delta_xi=r.total_delta,
                                notes=f"{len(r.path)} hops, Δξ={r.total_delta:.3f}")
            return DesignPipeline(out, self._steps + [step],
                                  self._xi_total + (r.total_delta or 0.0), False)
        except Exception as e:
            return self._fail("path", target.name, str(e))

    def result(self) -> PipelineResult:
        return PipelineResult(
            value=self._synthon,
            steps=self._steps,
            total_xi_delta=self._xi_total,
            failed=self._failed,
            failed_at=self._failed_at,
            failure_reason=self._failure_reason,
        )
