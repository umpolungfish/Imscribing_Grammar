"""
Imscribing Grammar Decomposition Algebra
===================================
Inverse operations that complement the build-up algebra (meet/join/tensor/lift).

Operations
----------
project          — orthogonal projection onto a named primitive subset
primitive_peel   — drop one primitive to its constraint-bottom; track ⊙ / Ω cost
factor           — greatest proper sub-imscription (greedy descent toward constraint-bottom)
principal_decomp — decompose into join-irreducible atomic factors
cofactor         — residual B given composite C and factor A  (inverts tensor)
complement_rel   — relative pseudocomplement w.r.t. context and target
kernel           — largest sub-imscription annihilated by a probe predicate
retrosynthetic_path — find minimal catalog factors whose tensor approximates a target

Algebraic grounding
-------------------
Tensor rules are primitive-aware (see algebra.py):
  • F, K → meet-dominant (tensor takes min)  ← "meet-dominant"
  • G    → join-dominant (tensor takes max)  ← "join-dominant"
  • D    → union (D-components form a set system)
  • T    → promotion (topology lattice)
  • Φ    → join-dominant (⊙ propagates)
  • Ω    → join-dominant (higher topological protection inherits)
  • R, P, Γ → categorical (tensor helper rules)

Cofactor analysis is primitive-aware: for meet-dominant (F, K), cofactor reveals
the bottleneck component; for join-dominant (G, Φ, Ω), it reveals the contributor.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field, replace as _dc_replace
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

from .models import (
    CriticalityPhase,
    Dimensionality,
    Fidelity,
    Granularity,
    InteractionGrammar,
    KineticCharacter,
    Polarity,
    RecognitionMode,
    Imscription,
    TopoIndex,
    Topology,
)

# ---------------------------------------------------------------------------
# Ordinal tables  (mirrors algebra.py)
# ---------------------------------------------------------------------------

_F_ORD: Dict[Fidelity, int] = {Fidelity.age: 0, Fidelity.they: 1, Fidelity.peep: 2}
_F_BY_ORD: Dict[int, Fidelity] = {v: k for k, v in _F_ORD.items()}

_K_ORD: Dict[KineticCharacter, int] = {
    KineticCharacter.air: 0, KineticCharacter.on: 1, KineticCharacter.egg: 2,
    KineticCharacter.loll: 3, KineticCharacter.yea: 4,
}
_K_BY_ORD: Dict[int, KineticCharacter] = {v: k for k, v in _K_ORD.items()}

_G_ORD: Dict[Granularity, int] = {
    Granularity.ice: 0, Granularity.bib: 1, Granularity.thigh: 2,
}
_G_BY_ORD: Dict[int, Granularity] = {v: k for k, v in _G_ORD.items()}

_TOPO_ORD: Dict[TopoIndex, int] = {
    TopoIndex.awe: 0, TopoIndex.oak: 1, TopoIndex.ah: 2,
    TopoIndex.ah: 3, TopoIndex.zoo: 4,
}

# Constraint-bottom values: "removing" the constraint for each ordinal primitive
#   F → LOW   (no fidelity floor)
#   K → FAST  (no kinetic barrier)
#   G → LOCAL (narrowest scope)
_PEEL_BOTTOM: Dict[str, object] = {
    "F": Fidelity.age,
    "K": KineticCharacter.yea,
    "G": Granularity.ice,
}

# For factor: direction to step toward constraint-bottom
#   F: HIGH(2)→MEDIUM(1)→LOW(0)   — decrease ordinal
#   K: MBL(0)→TRAP(1)→...→FAST(4) — increase ordinal (FAST = most accessible)
#   G: GLOBAL(2)→MESOSCALE(1)→LOCAL(0) — decrease ordinal
_FACTOR_STEP_DIR: Dict[str, int] = {"F": -1, "K": +1, "G": -1}

# Dimensionality component sets for cofactor D-analysis
_D_COMPS: Dict[Dimensionality, FrozenSet[str]] = {
    Dimensionality.dead:          frozenset({"M"}),
    Dimensionality.ash:     frozenset({"S"}),
    Dimensionality.array:           frozenset({"T"}),
    Dimensionality.ash:   frozenset({"M", "S"}),
    Dimensionality.array:    frozenset({"M", "T"}),
    Dimensionality.array:  frozenset({"S", "T"}),
    Dimensionality.ash:         frozenset({"M", "S", "T"}),
    Dimensionality.if_:        frozenset({"H"}),
}
_COMPS_TO_D: Dict[FrozenSet[str], Dimensionality] = {v: k for k, v in _D_COMPS.items()}

# ---------------------------------------------------------------------------
# Primitive accessor / mutator helpers
# ---------------------------------------------------------------------------

_PRIM_FIELD: Dict[str, str] = {
    "D": "dimensionality", "T": "topology", "R": "recognition_mode",
    "P": "polarity", "F": "fidelity", "K": "kinetic_character",
    "G": "granularity", "Gamma": "interaction_grammar",
    "Phi": "criticality_phase", "Omega": "topo_index",
}
ALL_PRIMITIVES = list(_PRIM_FIELD.keys())
ORDINAL_PRIMITIVES = {"F", "K", "G"}
CATEGORICAL_PRIMITIVES = {"D", "T", "R", "P", "Gamma", "Phi", "Omega"}


def _get(s: Imscription, prim: str):
    """Return the current value of a named primitive."""
    return getattr(s, _PRIM_FIELD[prim])


def _set(s: Imscription, prim: str, value, suffix: str = "") -> Imscription:
    """Return a copy of s with one primitive replaced."""
    name = s.name + (suffix or f"[{prim}→{value}]")
    return _dc_replace(s, name=name, **{_PRIM_FIELD[prim]: value})


def _has_phi_c(s: Imscription) -> bool:
    return s.criticality_phase is CriticalityPhase.monad


def _has_topo_protection(s: Imscription) -> bool:
    return s.topo_index is not None and s.topo_index != TopoIndex.awe


def _ord_val(prim: str, val) -> int:
    """Ordinal integer for F/K/G value."""
    return {"F": _F_ORD, "K": _K_ORD, "G": _G_ORD}[prim][val]


def _from_ord(prim: str, n: int):
    """Enum value from ordinal integer for F/K/G."""
    return {"F": _F_BY_ORD, "K": _K_BY_ORD, "G": _G_BY_ORD}[prim][n]


def _ordinal_max(prim: str) -> int:
    return {"F": 2, "K": 4, "G": 2}[prim]


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ProjectResult:
    """Result of projecting a imscription onto a subset of primitives."""
    imscription_name: str
    projected: List[str]          # Primitives retained
    zeroed: List[str]             # Primitives set to bottom
    result: Imscription
    notes: List[str] = field(default_factory=list)


@dataclass
class PeelResult:
    """Result of removing one primitive constraint."""
    imscription_name: str
    peeled: str                   # Primitive that was peeled
    result: Optional[Imscription]     # None if axiom-blocked
    phi_c_preserved: bool
    omega_preserved: bool
    peel_cost: float              # |Δξ_CP| from losing ⊙ or Ω (0 if preserved)
    blocked: bool
    block_reason: str
    notes: List[str] = field(default_factory=list)


@dataclass
class FactorResult:
    """Result of computing the greatest proper sub-imscription."""
    imscription_name: str
    result: Imscription               # Greatest proper sub-imscription
    stepped_primitive: str        # Which primitive was stepped down
    from_value: object
    to_value: object
    notes: List[str] = field(default_factory=list)


@dataclass
class PrincipalDecompResult:
    """Result of decomposing a imscription into join-irreducible atomic factors."""
    imscription_name: str
    factors: List[Imscription]        # Ordered list of irreducible components
    n_factors: int
    xi_balance: float             # Std-dev of factor constraint strengths (0 = perfectly balanced)
    notes: List[str] = field(default_factory=list)


@dataclass
class CofactorDimension:
    """Cofactor analysis for one primitive dimension."""
    primitive: str
    composite_val: object
    factor_val: object
    cofactor_val: object          # The residual B value
    role: str                     # "BOTTLENECK" | "CONTRIBUTOR" | "EXPLAINED" | "CONFLICT" | "PASSTHROUGH"
    note: str = ""


@dataclass
class CofactorResult:
    """Result of computing the residual B given composite C and factor A."""
    composite_name: str
    factor_name: str
    result: Optional[Imscription]     # The inferred B; None if globally inconsistent
    dimensions: List[CofactorDimension]
    bottleneck_primitives: List[str]   # Where A is the fidelity/kinetic bottleneck
    contributor_primitives: List[str]  # Where B is the scope/protection contributor
    conflict_primitives: List[str]     # Inconsistencies
    phi_c_source: str                  # "factor" | "cofactor" | "joint" | "none"
    notes: List[str] = field(default_factory=list)


@dataclass
class ComplementResult:
    """Relative pseudocomplement: max x s.t. x ⊓ ctx = ⊥ and x ⊔ ctx ≥ target."""
    imscription_name: str
    context_name: str
    target_name: str
    result: Optional[Imscription]
    satisfied: bool               # Whether the target condition is met
    notes: List[str] = field(default_factory=list)


@dataclass
class KernelResult:
    """Largest sub-imscription annihilated by a probe predicate."""
    imscription_name: str
    probe_name: str
    result: Optional[Imscription]     # None if even the bottom tuple activates the probe
    phi_c_in_kernel: bool         # Whether the kernel still has ⊙
    primitives_trimmed: List[str] # Which primitives were lowered to enter the kernel
    notes: List[str] = field(default_factory=list)


@dataclass
class RetrosynthCandidate:
    factor_names: List[str]
    distance_to_target: float
    xi_balance: float             # How evenly ξ_CP is split among factors


@dataclass
class RetrosynthResult:
    """Minimal catalog factors whose tensor product approximates a target."""
    target_name: str
    candidates: List[RetrosynthCandidate]   # Ranked by distance_to_target
    best: Optional[RetrosynthCandidate]
    n_searched: int               # Total (name-set, distance) pairs evaluated
    notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 1. project
# ---------------------------------------------------------------------------

def project(imscription: Imscription, primitives: Sequence[str]) -> ProjectResult:
    """
    Orthogonal projection: retain only the named primitives; set all others to
    their constraint-bottom value (least restrictive / most permissive).

    Retained primitives keep their exact values.  Projected-out primitives are
    set to:
      F → LOW, K → FAST, G → LOCAL  (ordinal bottoms)
      D → MOLECULAR, T → LINEAR, R → NON_COVALENT, P → SELF_COMPLEMENTARY_SYM
      Gamma → OR(BROAD), Phi → SUBCRITICAL, Omega → TRIVIAL / None

    Cost: zero (lossless for retained dimensions).
    """
    keep = set(primitives)
    bad = keep - set(ALL_PRIMITIVES)
    if bad:
        raise ValueError(f"Unknown primitive(s): {bad}. Valid: {ALL_PRIMITIVES}")

    bottom_map = {
        "D": Dimensionality.dead,
        "T": Topology.eat,
        "R": RecognitionMode.ado,
        "P": Polarity.or_,
        "F": Fidelity.age,
        "K": KineticCharacter.yea,
        "G": Granularity.ice,
        "Gamma": InteractionGrammar.gag,
        "Phi": CriticalityPhase.woe,
        "Omega": None,
    }

    kwargs: Dict[str, object] = {}
    zeroed: List[str] = []
    for prim, field_name in _PRIM_FIELD.items():
        if prim not in keep:
            kwargs[field_name] = bottom_map[prim]
            zeroed.append(prim)

    proj_label = "+".join(sorted(keep))
    result = _dc_replace(imscription, name=f"proj({imscription.name[:20]})[{proj_label}]", **kwargs)
    notes = [f"Projected onto {{{proj_label}}}; zeroed: {{{', '.join(zeroed)}}}"]
    return ProjectResult(
        imscription_name=imscription.name,
        projected=sorted(keep),
        zeroed=zeroed,
        result=result,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# 2. primitive_peel
# ---------------------------------------------------------------------------

def primitive_peel(
    imscription: Imscription,
    primitive: str,
    strict: bool = False,
    phi_c_cost: float = 3.0,
    omega_cost_per_level: float = 1.5,
) -> PeelResult:
    """
    Remove one primitive by setting it to its constraint-bottom value.

    Checks post-peel invariants:
      • ⊙ preserved?  If lost and strict=True → blocked; else → cost += phi_c_cost
      • Ω preserved?    If degraded and strict=True → blocked; else → cost += omega_cost × levels
      • Axiom 2 (G_ב + Γ_∧(SPECIFIC) cannot reach G_ℵ)?  → blocked always

    Returns PeelResult with the peeled imscription, cost, and flags.
    """
    if primitive not in _PRIM_FIELD:
        raise ValueError(f"Unknown primitive: {primitive!r}. Valid: {ALL_PRIMITIVES}")

    original_phi_c = _has_phi_c(imscription)
    original_omega = _G_ORD.get(imscription.granularity, 0)  # proxy for protection
    original_topo = imscription.topo_index

    # --- Determine the bottom value for this primitive ---
    if primitive in ORDINAL_PRIMITIVES:
        new_val = _PEEL_BOTTOM[primitive]
    else:
        bottom_map = {
            "D": Dimensionality.dead,
            "T": Topology.eat,
            "R": RecognitionMode.ado,
            "P": Polarity.or_,
            "Gamma": InteractionGrammar.gag,
            "Phi": CriticalityPhase.woe,
            "Omega": None,
        }
        new_val = bottom_map[primitive]

    peeled = _set(imscription, primitive, new_val, suffix=f"[peel-{primitive}]")

    # --- Invariant checks ---
    notes: List[str] = []
    peel_cost = 0.0

    # ⊙
    new_phi_c = _has_phi_c(peeled)
    phi_c_preserved = (not original_phi_c) or new_phi_c
    if original_phi_c and not new_phi_c:
        notes.append(f"⊙ lost by peeling {primitive} — cost +{phi_c_cost:.1f} nats")
        if strict:
            return PeelResult(
                imscription_name=imscription.name, peeled=primitive, result=None,
                phi_c_preserved=False, omega_preserved=True, peel_cost=0.0,
                blocked=True, block_reason=f"Peeling {primitive} destroys ⊙ (strict mode)",
                notes=notes,
            )
        peel_cost += phi_c_cost

    # Ω topology protection
    new_topo = peeled.topo_index
    orig_str = _TOPO_ORD.get(original_topo, 0) if original_topo else 0
    new_str = _TOPO_ORD.get(new_topo, 0) if new_topo else 0
    omega_preserved = new_str >= orig_str
    if not omega_preserved:
        levels_lost = orig_str - new_str
        oc = omega_cost_per_level * levels_lost
        notes.append(f"Ω degraded {original_topo} → {new_topo} ({levels_lost} level(s)) — cost +{oc:.1f} nats")
        if strict:
            return PeelResult(
                imscription_name=imscription.name, peeled=primitive, result=None,
                phi_c_preserved=phi_c_preserved, omega_preserved=False, peel_cost=0.0,
                blocked=True, block_reason=f"Peeling {primitive} degrades Ω (strict mode)",
                notes=notes,
            )
        peel_cost += oc

    # Axiom 2: G_LOCAL + Gamma_AND(SPECIFIC) cannot propagate to G_GLOBAL
    if (peeled.granularity == Granularity.ice
            and peeled.interaction_grammar == InteractionGrammar.vow
            and imscription.granularity != Granularity.ice):
        reason = "Axiom 2 violation: peeling G to LOCAL with Γ_∧(SPECIFIC) blocks propagation"
        notes.append(reason)
        if strict:
            return PeelResult(
                imscription_name=imscription.name, peeled=primitive, result=None,
                phi_c_preserved=phi_c_preserved, omega_preserved=omega_preserved,
                peel_cost=0.0, blocked=True, block_reason=reason, notes=notes,
            )

    if not notes:
        notes.append(f"Peeled {primitive}: {_get(imscription, primitive)} → {new_val} (cost-free)")

    return PeelResult(
        imscription_name=imscription.name, peeled=primitive, result=peeled,
        phi_c_preserved=phi_c_preserved, omega_preserved=omega_preserved,
        peel_cost=peel_cost, blocked=False, block_reason="", notes=notes,
    )


# ---------------------------------------------------------------------------
# 3. factor
# ---------------------------------------------------------------------------

def factor(imscription: Imscription, prefer: Optional[str] = None) -> FactorResult:
    """
    Compute the greatest proper sub-imscription: step exactly one ordinal primitive
    one notch toward its constraint-bottom.

    Preference order (unless `prefer` is given):
      F first (fidelity floor is the most structurally significant), then K, then G.

    For categorical primitives we do not step (no natural "less" direction);
    use primitive_peel() or project() for those.

    Returns the result of stepping the preferred primitive one level down.
    If all ordinals are already at their constraint-bottom, returns the imscription
    unchanged with a note.
    """
    order = [prefer] if prefer and prefer in ORDINAL_PRIMITIVES else ["F", "K", "G"]

    for prim in order:
        cur_val = _get(imscription, prim)
        cur_ord = _ord_val(prim, cur_val)
        step = _FACTOR_STEP_DIR[prim]
        next_ord = cur_ord + step

        if prim == "K":
            at_bottom = (cur_ord == _ordinal_max(prim))   # FAST = max ord = constraint-bottom
        else:
            at_bottom = (cur_ord == 0)                     # F_LOW / G_LOCAL = min ord = constraint-bottom

        if at_bottom:
            continue   # already at constraint-bottom for this primitive

        next_val = _from_ord(prim, next_ord)
        result = _set(imscription, prim, next_val, suffix=f"[factor:{prim}]")
        return FactorResult(
            imscription_name=imscription.name, result=result,
            stepped_primitive=prim, from_value=cur_val, to_value=next_val,
            notes=[f"Stepped {prim}: {cur_val.value} → {next_val.value} (toward constraint-bottom)"],
        )

    # All ordinals already at bottom
    return FactorResult(
        imscription_name=imscription.name, result=imscription,
        stepped_primitive="none", from_value=None, to_value=None,
        notes=["All ordinal primitives already at constraint-bottom; imscription is join-irreducible"],
    )


# ---------------------------------------------------------------------------
# 4. principal_decomp
# ---------------------------------------------------------------------------

def principal_decomp(imscription: Imscription, max_factors: int = 9) -> PrincipalDecompResult:
    """
    Decompose a imscription into its join-irreducible atomic factors by repeated
    application of factor().

    Each factor step produces a component and a residual.  We collect all the
    "peeled off" contributions (one per ordinal step) as atomic factors,
    plus the categorical skeleton as the final factor.

    A imscription is join-irreducible in the ordinal dimensions when all F/K/G are at
    their constraint-bottoms.  The categorical dimensions (D, T, R, P, Γ, Φ, Ω)
    are each a single atom — they cannot be further decomposed without losing their
    identity.

    Returns factors ordered from most-constraining contribution to least.
    """
    factors: List[Imscription] = []
    notes: List[str] = []
    current = imscription
    steps = 0

    while steps < max_factors:
        fr = factor(current)
        if fr.stepped_primitive == "none":
            break
        # The "peeled off" level is the difference: a 1-primitive atom
        atom = project(imscription, [fr.stepped_primitive]).result
        atom = _dc_replace(
            atom,
            name=f"atom[{fr.stepped_primitive}={fr.from_value.value if hasattr(fr.from_value, 'value') else fr.from_value}]",
        )
        # Override the single primitive to isolate the contribution at that level
        atom = _set(atom, fr.stepped_primitive, fr.from_value, suffix="")
        atom = _dc_replace(atom, name=f"atom[{fr.stepped_primitive}={fr.from_value.value if hasattr(fr.from_value, 'value') else fr.from_value}]")
        factors.append(atom)
        notes.append(f"  Factor {len(factors)}: {fr.stepped_primitive} contribution = {fr.from_value}")
        current = fr.result
        steps += 1

    # The remaining categorical skeleton is the final factor
    skeleton_name = f"skeleton({imscription.name[:20]})"
    skeleton = _dc_replace(current, name=skeleton_name)
    factors.append(skeleton)
    notes.append(f"  Skeleton: categorical primitives of {imscription.name}")

    # Balance metric: std-dev of constraint_strength across factors
    try:
        strengths = [f.constraint_strength() for f in factors]
        mean = sum(strengths) / len(strengths)
        variance = sum((x - mean) ** 2 for x in strengths) / len(strengths)
        xi_balance = variance ** 0.5
    except Exception:
        xi_balance = 0.0

    return PrincipalDecompResult(
        imscription_name=imscription.name, factors=factors, n_factors=len(factors),
        xi_balance=xi_balance, notes=notes,
    )


# ---------------------------------------------------------------------------
# 5. cofactor
# ---------------------------------------------------------------------------

def cofactor(composite: Imscription, factor_a: Imscription) -> CofactorResult:
    """
    Invert the tensor product: given composite C ≈ tensor(A, B), find B.

    Rules per primitive axis (mirroring algebra.tensor()):

    Meet-dominant (F, K):  tensor[p] = min(A[p], B[p])
      • A[p] > C[p]:  B is the bottleneck → cofactor[p] = C[p];  role = BOTTLENECK
      • A[p] = C[p]:  A is bottleneck (or tied) → cofactor[p] = C[p]; role = BOTTLENECK
      • A[p] < C[p]:  CONFLICT (A alone is already below C; impossible)

    Join-dominant (G):  tensor[p] = max(A[p], B[p])
      • A[p] = C[p]:  A explains it → cofactor[p] = LOCAL (B contributes nothing); EXPLAINED
      • A[p] < C[p]:  B is the contributor → cofactor[p] = C[p]; CONTRIBUTOR
      • A[p] > C[p]:  CONFLICT (A alone exceeds C)

    D (union):  cofactor[D] = components(C) − components(A) → CONTRIBUTOR / EXPLAINED
    T (topology promotion): same logic as join-dominant ordinal
    Φ (⊙ join-dominant): if A has ⊙ and C has ⊙ → EXPLAINED; else CONTRIBUTOR / CONFLICT
    Ω (topo protection, join): same as G logic on ordinal strength
    R, P, Γ (categorical, tensor helper):
      • A[p] = C[p] → EXPLAINED (A explains it)
      • A[p] ≠ C[p] → PASSTHROUGH (B must have C[p]; we can't say more without the tensor rule)

    Returns CofactorResult with per-dimension analysis and the inferred B imscription.
    """
    C = composite
    A = factor_a
    dims: List[CofactorDimension] = []
    conflicts: List[str] = []
    bottlenecks: List[str] = []
    contributors: List[str] = []
    cofactor_kwargs: Dict[str, object] = {}

    # ── Meet-dominant: F ────────────────────────────────────────────────────
    for prim in ("F", "K"):
        c_ord = _ord_val(prim, _get(C, prim))
        a_ord = _ord_val(prim, _get(A, prim))
        if prim == "K":
            # K: MBL=0 (most arrested) ... FAST=4 (most accessible)
            # tensor takes min → least accessible = most constraining bottleneck
            # A[K] < C[K] means A is MORE arrested than C → impossible under tensor
            if a_ord < c_ord:
                role, cof_val, note = "CONFLICT", _get(C, prim), f"A[{prim}]={_get(A, prim)} < C[{prim}]={_get(C, prim)}: impossible under tensor-min"
                conflicts.append(prim)
            elif a_ord >= c_ord:
                # A is at least as accessible as C (or more); B is the bottleneck
                role, cof_val, note = "BOTTLENECK", _get(C, prim), f"B sets {prim} floor = {_get(C, prim)}"
                bottlenecks.append(prim)
        else:
            # F: HIGH=2 (most selective) ... LOW=0 (least selective)
            # tensor takes min → least selective = fidelity bottleneck
            # A[F] < C[F] means A is LESS selective than C → impossible under tensor-min
            if a_ord < c_ord:
                role, cof_val, note = "CONFLICT", _get(C, prim), f"A[{prim}]={_get(A, prim)} < C[{prim}]={_get(C, prim)}: impossible under tensor-min"
                conflicts.append(prim)
            else:
                role = "BOTTLENECK" if a_ord > c_ord else "BOTTLENECK"
                cof_val = _get(C, prim)
                note = ("B is fidelity bottleneck" if a_ord > c_ord
                        else f"A is fidelity bottleneck; B ≥ {_get(C, prim)}")
                bottlenecks.append(prim)
        cofactor_kwargs[_PRIM_FIELD[prim]] = cof_val
        dims.append(CofactorDimension(prim, _get(C, prim), _get(A, prim), cof_val, role, note))

    # ── Join-dominant: G ────────────────────────────────────────────────────
    c_g = _G_ORD[C.granularity]
    a_g = _G_ORD[A.granularity]
    if a_g > c_g:
        role, cof_g_val, note = "CONFLICT", C.granularity, f"A[G]={A.granularity} exceeds C[G]={C.granularity}"
        conflicts.append("G")
    elif a_g == c_g:
        role, cof_g_val, note = "EXPLAINED", Granularity.ice, f"A explains G={C.granularity}; B contributes ≥LOCAL"
    else:
        role, cof_g_val, note = "CONTRIBUTOR", C.granularity, f"B is the G={C.granularity} contributor"
        contributors.append("G")
    cofactor_kwargs[_PRIM_FIELD["G"]] = cof_g_val
    dims.append(CofactorDimension("G", C.granularity, A.granularity, cof_g_val, role, note))

    # ── D (union) ────────────────────────────────────────────────────────────
    c_comps = _D_COMPS.get(C.dimensionality, frozenset({"?"}))
    a_comps = _D_COMPS.get(A.dimensionality, frozenset({"?"}))
    if not a_comps.issubset(c_comps):
        role, cof_d, note = "CONFLICT", C.dimensionality, f"A[D] components {a_comps} not ⊆ C[D] components {c_comps}"
        conflicts.append("D")
    else:
        remaining = c_comps - a_comps
        if not remaining:
            role, cof_d, note = "EXPLAINED", Dimensionality.dead, f"A explains D; B needs only D_MOLECULAR"
        else:
            d_val = _COMPS_TO_D.get(frozenset(remaining), C.dimensionality)
            role, cof_d, note = "CONTRIBUTOR", d_val, f"B contributes D components {remaining}"
            contributors.append("D")
    cofactor_kwargs[_PRIM_FIELD["D"]] = cof_d
    dims.append(CofactorDimension("D", C.dimensionality, A.dimensionality, cof_d, role, note))

    # ── Φ (⊙ join-dominant) ────────────────────────────────────────────────
    a_phi = _has_phi_c(A)
    c_phi = _has_phi_c(C)
    if a_phi and not c_phi:
        cof_phi = CriticalityPhase.woe
        phi_role = "CONFLICT"
        note = "A has ⊙ but C does not — impossible under tensor (⊙ propagates)"
        conflicts.append("Phi")
    elif a_phi and c_phi:
        cof_phi = CriticalityPhase.woe
        phi_role = "EXPLAINED"
        note = "A explains ⊙; B need not have it"
    elif not a_phi and c_phi:
        cof_phi = CriticalityPhase.monad
        phi_role = "CONTRIBUTOR"
        note = "B must carry ⊙ (A doesn't have it)"
        contributors.append("Phi")
    else:
        cof_phi = CriticalityPhase.woe
        phi_role = "PASSTHROUGH"
        note = "Neither A nor C has ⊙; B also 𐑢"
    cofactor_kwargs[_PRIM_FIELD["Phi"]] = cof_phi
    dims.append(CofactorDimension("Phi", C.criticality_phase, A.criticality_phase, cof_phi, phi_role, note))

    # ── Ω (topological protection, join-dominant) ────────────────────────────
    c_ome = _TOPO_ORD.get(C.topo_index, 0) if C.topo_index else 0
    a_ome = _TOPO_ORD.get(A.topo_index, 0) if A.topo_index else 0
    if a_ome > c_ome:
        cof_ome_val = None
        ome_role = "CONFLICT"
        note = "A[Ω] stronger than C[Ω] — impossible under tensor (join-dominant)"
        conflicts.append("Omega")
    elif a_ome == c_ome:
        cof_ome_val = TopoIndex.awe if c_ome > 0 else None
        ome_role = "EXPLAINED"
        note = f"A explains Ω={C.topo_index}; B contributes ≥TRIVIAL"
    else:
        cof_ome_val = C.topo_index
        ome_role = "CONTRIBUTOR"
        note = f"B carries Ω={C.topo_index}"
        contributors.append("Omega")
    cofactor_kwargs[_PRIM_FIELD["Omega"]] = cof_ome_val
    dims.append(CofactorDimension("Omega", C.topo_index, A.topo_index, cof_ome_val, ome_role, note))

    # ── Categorical passthrough: T, R, P, Gamma ─────────────────────────────
    for prim in ("T", "R", "P", "Gamma"):
        c_val = _get(C, prim)
        a_val = _get(A, prim)
        if a_val == c_val:
            role, cof_val, note = "EXPLAINED", c_val, f"A explains {prim}={c_val}"
        else:
            role, cof_val, note = "PASSTHROUGH", c_val, f"B contributes {prim}={c_val} (A has {a_val})"
            contributors.append(prim)
        cofactor_kwargs[_PRIM_FIELD[prim]] = cof_val
        dims.append(CofactorDimension(prim, c_val, a_val, cof_val, role, note))

    # ── Stoichiometry ─────────────────────────────────────────────────────────
    cofactor_kwargs["stoichiometry"] = C.stoichiometry

    # ── Determine ⊙ provenance label ───────────────────────────────────────
    if a_phi and c_phi:
        phi_source = "factor"
    elif not a_phi and c_phi:
        phi_source = "cofactor"
    elif a_phi and c_phi:
        phi_source = "joint"
    else:
        phi_source = "none"

    # ── Build the cofactor Imscription ────────────────────────────────────────────
    if conflicts:
        result_imscription = None
        notes = [f"Cofactor({C.name}, {A.name}) has CONFLICT on: {', '.join(conflicts)}"]
    else:
        result_imscription = _dc_replace(
            composite,
            name=f"cofactor({C.name[:16]},{A.name[:16]})",
            **cofactor_kwargs,
        )
        notes = [f"Cofactor({C.name} | {A.name}) computed successfully"]

    notes += [f"  {d.primitive}: {d.role} — {d.note}" for d in dims]

    return CofactorResult(
        composite_name=C.name, factor_name=A.name, result=result_imscription,
        dimensions=dims, bottleneck_primitives=bottlenecks,
        contributor_primitives=contributors, conflict_primitives=conflicts,
        phi_c_source=phi_source, notes=notes,
    )


# ---------------------------------------------------------------------------
# 6. complement_rel
# ---------------------------------------------------------------------------

def complement_rel(imscription: Imscription, context: Imscription, target: Imscription) -> ComplementResult:
    """
    Relative pseudocomplement: find the maximal x ≤ imscription such that:
      (1) x ⊓ context = ⊥   (x and context share no constraint)
      (2) x ⊔ context ≥ target  (together they cover the target)

    For ordinal primitives:
      Condition 1: x[p] + context[p] = bottom → x[p] must be ≤ bottom (i.e., bottom itself)
      Condition 2: max(x[p], context[p]) ≥ target[p]

    For categorical primitives:
      Condition 1: x[p] ≠ context[p]  (no shared constraint)
      Condition 2: either x[p] = target[p] or context[p] = target[p]

    Returns the maximal x satisfying both conditions (join of all valid x).
    """
    from .algebra import meet as _meet, join as _join

    kwargs: Dict[str, object] = {}
    notes: List[str] = []
    satisfied = True

    for prim in ORDINAL_PRIMITIVES:
        ctx_ord = _ord_val(prim, _get(context, prim))
        tgt_ord = _ord_val(prim, _get(target, prim))
        syn_ord = _ord_val(prim, _get(imscription, prim))

        # Condition 1: x ⊓ ctx = ⊥ → for meet-dominant (F, K) and G (join)
        # For G (join): meet is min → min(x, ctx) = 0 → x = 0 (LOCAL) always satisfies if ctx > 0
        # For F, K: meet is min → min(x, ctx) = 0 → x = 0 (F_LOW or K_lambda)
        if prim == "G":
            # Condition 1: for G (join), meet = min. min(x_g, ctx_g) = 0 → x_g = 0 = LOCAL if ctx_g > 0
            # But we want the MAXIMAL x that satisfies this: x_g < ctx_g (strictly less to get min = x_g... no)
            # Actually min(x, ctx) = 0 → x = LOCAL (only if ctx > 0) or anything if ctx = 0
            x_g_max = _G_ORD[Granularity.ice] if ctx_ord > 0 else syn_ord
            # Condition 2: max(x_g, ctx_g) ≥ tgt_g → ctx_g ≥ tgt_g OR x_g ≥ tgt_g
            if ctx_ord >= tgt_ord:
                pass  # ctx alone satisfies condition 2
            elif x_g_max >= tgt_ord:
                pass
            else:
                satisfied = False
                notes.append(f"G: cannot satisfy target G={_get(target, prim)} with context G={_get(context, prim)}")
            new_val = _from_ord(prim, min(x_g_max, syn_ord))
        else:
            # F or K: meet is min. For the complement, meet(x, ctx) = ⊥ means min(x,ctx) = 0
            # → x = 0 (most conservative/bottom value)  OR ctx = 0
            # Maximal x satisfying min(x,ctx) = 0:
            if ctx_ord == 0:
                x_max = syn_ord  # ctx is already bottom; x can be anything
            else:
                x_max = 0  # must be bottom to get min = 0
            # Condition 2: min(x,ctx) ≥ tgt → min(x_max, ctx_ord) ≥ tgt_ord
            # (for F/K, join = max for join operation, but complement uses ⊔ = join = max here)
            # Wait: x ⊔ context for F: join takes max(x,ctx). So x ⊔ ctx ≥ target means max(x,ctx) ≥ tgt.
            if max(x_max, ctx_ord) < tgt_ord:
                satisfied = False
                notes.append(f"{prim}: cannot satisfy target {prim}={_get(target, prim)}")
            new_val = _from_ord(prim, min(x_max, syn_ord))

        kwargs[_PRIM_FIELD[prim]] = new_val
        notes.append(f"  {prim}: complement value = {new_val}")

    # Categorical: set x[p] = target[p] if context[p] ≠ target[p]; else leave None
    for prim in ("D", "T", "R", "P", "Gamma", "Phi", "Omega"):
        ctx_val = _get(context, prim)
        tgt_val = _get(target, prim)
        syn_val = _get(imscription, prim)
        if ctx_val == tgt_val:
            # Context already covers target; x[p] should not match context
            # Maximally: x[p] = syn[p] if syn[p] ≠ ctx[p]; else use None / bottom
            if syn_val != ctx_val:
                kwargs[_PRIM_FIELD[prim]] = syn_val
            else:
                kwargs[_PRIM_FIELD[prim]] = None if prim in ("Phi", "Omega") else ctx_val
            notes.append(f"  {prim}: context covers target; x[{prim}] = {kwargs[_PRIM_FIELD[prim]]}")
        else:
            # x[p] should differ from context and reach target
            kwargs[_PRIM_FIELD[prim]] = tgt_val
            notes.append(f"  {prim}: x[{prim}] = {tgt_val} (complement of context {ctx_val})")

    if not satisfied:
        return ComplementResult(
            imscription_name=imscription.name, context_name=context.name,
            target_name=target.name, result=None, satisfied=False, notes=notes,
        )

    result = _dc_replace(
        imscription,
        name=f"comp_rel({imscription.name[:14]}, {context.name[:14]})",
        **kwargs,
    )
    return ComplementResult(
        imscription_name=imscription.name, context_name=context.name,
        target_name=target.name, result=result, satisfied=True, notes=notes,
    )


# ---------------------------------------------------------------------------
# 7. kernel
# ---------------------------------------------------------------------------

def kernel(
    imscription: Imscription,
    probe: Callable[[Imscription], bool],
    probe_name: str = "probe",
) -> KernelResult:
    """
    Largest sub-imscription annihilated by a probe predicate.

    Starting from the full imscription, greedily lowers each ordinal primitive
    (F → LOW, K → FAST, G → LOCAL) one step at a time until the probe returns
    False.  Returns the largest sub-imscription for which probe(s) = False.

    If probe(full_imscription) = False: the full imscription is already in the kernel.
    If even the bottom tuple activates the probe: returns None.

    Common probe: lambda s: varma_probe(s).phi_c_score > 0.5
    → kernel = largest sub-imscription without ⊙ signal.
    """
    notes: List[str] = []
    trimmed: List[str] = []

    if not probe(imscription):
        notes.append(f"Full imscription already in kernel({probe_name})")
        return KernelResult(
            imscription_name=imscription.name, probe_name=probe_name,
            result=imscription, phi_c_in_kernel=_has_phi_c(imscription),
            primitives_trimmed=[], notes=notes,
        )

    current = imscription
    # Greedy descent through ordinal primitives
    for prim in ("F", "K", "G"):
        max_steps = _ordinal_max(prim) + 1
        for _ in range(max_steps):
            cur_val = _get(current, prim)
            bottom_val = _PEEL_BOTTOM[prim]
            if cur_val == bottom_val:
                break  # Already at constraint-bottom for this primitive
            # Step one notch toward constraint-bottom
            cur_ord = _ord_val(prim, cur_val)
            step = _FACTOR_STEP_DIR[prim]
            next_ord = cur_ord + step
            if next_ord < 0 or next_ord > _ordinal_max(prim):
                break
            next_val = _from_ord(prim, next_ord)
            candidate = _set(current, prim, next_val, suffix=f"[kernel-{prim}]")
            if not probe(candidate):
                notes.append(f"  Probe false after {prim}: {cur_val} → {next_val}")
                if prim not in trimmed:
                    trimmed.append(prim)
                current = candidate
                break
            else:
                notes.append(f"  Probe still true at {prim}={next_val}, continuing")
                current = candidate
                if prim not in trimmed:
                    trimmed.append(prim)

    if probe(current):
        notes.append(f"Probe activates on all sub-imscriptions — no kernel exists above ⊥")
        return KernelResult(
            imscription_name=imscription.name, probe_name=probe_name,
            result=None, phi_c_in_kernel=False,
            primitives_trimmed=trimmed, notes=notes,
        )

    notes.insert(0, f"Kernel({probe_name}) found: {current.name}")
    return KernelResult(
        imscription_name=imscription.name, probe_name=probe_name,
        result=current, phi_c_in_kernel=_has_phi_c(current),
        primitives_trimmed=trimmed, notes=notes,
    )


# ---------------------------------------------------------------------------
# 8. retrosynthetic_path
# ---------------------------------------------------------------------------

def retrosynthetic_path(
    target: Imscription,
    catalog: Sequence[Imscription],
    max_factors: int = 3,
    top_k: int = 5,
    candidate_pool: int = 20,
) -> RetrosynthResult:
    """
    Find the minimal set of catalog imscriptions whose tensor product best approximates
    the target.

    Algorithm:
      1. Rank all catalog imscriptions by distance to target (ascending) → pool of top N.
      2. Try single imscriptions (n=1): each pool member is a candidate.
      3. Try pairs  (n=2): all pairs from the pool; compute tensor; distance to target.
      4. Try triples (n=3) if max_factors ≥ 3: top-M from pool.
      5. Return top-K candidates across all factor counts, ranked by distance.

    Distance is tuple_distance(tensor_result, target).  The tensor result is
    approximated by creating a Imscription from the TensorResult fields.
    """
    from .algebra import tensor as _tensor, tuple_distance as _dist

    def _tensor_to_imscription(tr, base: Imscription) -> Imscription:
        """Convert a TensorResult to a Imscription (inherit missing fields from base)."""
        def _safe(v, fallback):
            return v if v is not None and not isinstance(v, str) else fallback
        return _dc_replace(
            base,
            name=f"~tensor({tr.s1_name[:14]},{tr.s2_name[:14]})",
            dimensionality=_safe(tr.dimensionality, base.dimensionality),
            topology=_safe(tr.topology, base.topology),
            recognition_mode=_safe(tr.recognition_mode, base.recognition_mode),
            polarity=_safe(tr.polarity, base.polarity),
            fidelity=_safe(tr.fidelity, base.fidelity),
            kinetic_character=_safe(tr.kinetic_character, base.kinetic_character),
            granularity=_safe(tr.granularity, base.granularity),
            interaction_grammar=_safe(tr.interaction_grammar, base.interaction_grammar),
            criticality_phase=tr.criticality_phase,
            stoichiometry=tr.stoichiometry,
            topo_index=tr.topo_index,
        )

    notes: List[str] = []
    candidates: List[RetrosynthCandidate] = []
    n_searched = 0

    # Sort catalog by distance to target
    try:
        ranked = sorted(catalog, key=lambda s: _dist(s, target))
    except Exception as e:
        return RetrosynthResult(
            target_name=target.name, candidates=[], best=None,
            n_searched=0, notes=[f"Distance computation failed: {e}"],
        )

    pool = ranked[:candidate_pool]
    notes.append(f"Pool: top-{len(pool)} of {len(catalog)} catalog imscriptions by distance to target")

    # Single factors
    for s in pool:
        d = _dist(s, target)
        candidates.append(RetrosynthCandidate(
            factor_names=[s.name], distance_to_target=d, xi_balance=0.0,
        ))
        n_searched += 1

    # Pairs
    if max_factors >= 2:
        for s1, s2 in itertools.combinations(pool, 2):
            try:
                tr = _tensor(s1, s2)
                composite = _tensor_to_imscription(tr, s1)
                d = _dist(composite, target)
                str1 = s1.constraint_strength()
                str2 = s2.constraint_strength()
                balance = abs(str1 - str2)
                candidates.append(RetrosynthCandidate(
                    factor_names=[s1.name, s2.name],
                    distance_to_target=d,
                    xi_balance=balance,
                ))
                n_searched += 1
            except Exception:
                pass

    # Triples — restrict pool to keep tractable
    if max_factors >= 3:
        triple_pool = pool[:min(10, len(pool))]
        for s1, s2, s3 in itertools.combinations(triple_pool, 3):
            try:
                tr12 = _tensor(s1, s2)
                c12 = _tensor_to_imscription(tr12, s1)
                tr123 = _tensor(c12, s3)
                composite = _tensor_to_imscription(tr123, s1)
                d = _dist(composite, target)
                strs = [s.constraint_strength() for s in (s1, s2, s3)]
                mean = sum(strs) / 3
                balance = (sum((x - mean) ** 2 for x in strs) / 3) ** 0.5
                candidates.append(RetrosynthCandidate(
                    factor_names=[s1.name, s2.name, s3.name],
                    distance_to_target=d,
                    xi_balance=balance,
                ))
                n_searched += 1
            except Exception:
                pass

    # Rank and return top-K
    candidates.sort(key=lambda c: (c.distance_to_target, c.xi_balance))
    top_candidates = candidates[:top_k]
    best = top_candidates[0] if top_candidates else None

    notes.append(f"Searched {n_searched} factor combinations; returning top-{len(top_candidates)}")
    if best:
        notes.append(
            f"Best: {' ⊗ '.join(best.factor_names)} "
            f"→ d={best.distance_to_target:.3f} nats"
        )

    return RetrosynthResult(
        target_name=target.name, candidates=top_candidates,
        best=best, n_searched=n_searched, notes=notes,
    )


# ---------------------------------------------------------------------------
# Convenience: ⊙ probe for kernel()
# ---------------------------------------------------------------------------

def monad_probe(s: Imscription) -> bool:
    """Standard probe: True if the imscription has ⊙ (criticality = CRITICAL)."""
    return _has_phi_c(s)


def topo_protection_probe(s: Imscription) -> bool:
    """Standard probe: True if the imscription has non-trivial topological protection."""
    return _has_topo_protection(s)


# ---------------------------------------------------------------------------
# Monadic wrappers — lift each operation into DesignPipeline style
# ---------------------------------------------------------------------------

def project_m(primitives: Sequence[str]):
    """Return a DesignPipeline-compatible step function for project()."""
    def _step(s: Imscription):
        r = project(s, primitives)
        return r.result, r.notes, [], False, ""
    _step.__name__ = f"project({','.join(primitives)})"
    return _step


def peel_m(primitive: str, strict: bool = False):
    """Return a DesignPipeline-compatible step function for primitive_peel()."""
    def _step(s: Imscription):
        r = primitive_peel(s, primitive, strict=strict)
        return r.result, r.notes, [], r.blocked, r.block_reason
    _step.__name__ = f"peel({primitive})"
    return _step


def factor_m(prefer: Optional[str] = None):
    """Return a DesignPipeline-compatible step function for factor()."""
    def _step(s: Imscription):
        r = factor(s, prefer=prefer)
        return r.result, r.notes, [], False, ""
    _step.__name__ = f"factor(prefer={prefer})"
    return _step


def cofactor_m(factor_a: Imscription):
    """Return a DesignPipeline-compatible step function for cofactor()."""
    def _step(s: Imscription):
        r = cofactor(s, factor_a)
        blocked = r.result is None
        return r.result, r.notes, [], blocked, ("; ".join(r.conflict_primitives) if blocked else "")
    _step.__name__ = f"cofactor({factor_a.name})"
    return _step
