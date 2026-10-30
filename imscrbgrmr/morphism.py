"""
Imscription Morphisms — Phase Transitions as Kleisli Arrows

Encodes phase transitions as morphisms in the Kleisli category over the
HotSwap monad.  A transition A → B is:

  • 2nd order  — direct path through ⊙ intermediates exists (continuous,
                 order parameter vanishes at the critical point)
  • 1st order  — no HotSwap path (D/T or F conflict), transition requires
                 an external driver; represented as a *virtual* morphism
                 with infinite forward cost and asymmetric reverse cost

Asymmetry metric:
  forward_cost  = sum of hop Δξ_CP on the forward path (or ∞ if no path)
  reverse_cost  = sum of hop Δξ_CP on the reverse path (or ∞ if no path)
  asymmetry     = |forward_cost − reverse_cost| / max(forward_cost, 1e-9)

The asymmetry encodes the thermodynamic irreversibility of the transition.

A second-order transition has a 2-way path and low asymmetry.
A first-order transition has no path and asymmetry = 1.0 (maximally
irreversible from a primitive standpoint — the driver must supply the
missing structural information).

Reference: IG_LANG.md §Phase 3e stress tests.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence

from .models import Imscription, CriticalityPhase
from .algebra import find_path, tuple_distance, PathResult


# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

class TransitionOrder(str, Enum):
    SECOND   = "2nd_order"   # continuous; path through ⊙ intermediates
    FIRST    = "1st_order"   # discontinuous; no HotSwap path (T/D conflict)
    UNKNOWN  = "unknown"     # insufficient catalog coverage to determine


@dataclass
class QuantumCriticalPoint:
    """
    A quantum critical point (QCP) detected in a transition morphism.

    A QCP is *not* a property of either endpoint imscription — it is a property
    of the morphism between them.  Specifically: the transition is 2nd-order
    AND the forward path passes through at least one ⊙ intermediate.

    The ⊙ intermediate is the QCP imscription — the system is tuned *through*
    it, not to it.  This is the representational gap closed by the morphism
    infrastructure: Factor 8 in the Varma probe fires on an endpoint that
    *looks like* a QCP; the morphism QCP fires on the actual transition.

    Attributes
    ----------
    transition_src, transition_dst : endpoint names
    qcp_imscription_names : names of the ⊙ imscriptions on the path (the QCPs)
    path_cost : total Δξ_CP to traverse the QCP from src to dst
    universality_hints : list of primitive-derived universality class hints
    """
    transition_src: str
    transition_dst: str
    qcp_imscription_names: List[str]
    path_cost: float
    universality_hints: List[str] = field(default_factory=list)


@dataclass
class TransitionMorphism:
    """
    A Kleisli arrow  A ──(transition)──▶ B

    Attributes
    ----------
    src_name, dst_name : names of the endpoint imscriptions
    order       : SECOND | FIRST | UNKNOWN
    forward_path : BFS PathResult for A→B (may be not found)
    reverse_path : BFS PathResult for B→A (may be not found)
    phi_c_intermediates : names of ⊙ imscriptions on the forward path (if any)
    forward_cost  : total Δξ_CP on forward path  (math.inf if no path)
    reverse_cost  : total Δξ_CP on reverse path  (math.inf if no path)
    asymmetry     : |fwd − rev| / max(fwd, 1e-9)  ∈ [0, 1]
    notes         : human-readable rationale
    """
    src_name: str
    dst_name: str
    order: TransitionOrder
    forward_path: PathResult
    reverse_path: PathResult
    phi_c_intermediates: List[str] = field(default_factory=list)
    forward_cost: float = math.inf
    reverse_cost: float = math.inf
    asymmetry: float = 1.0
    quantum_critical_point: Optional[QuantumCriticalPoint] = None
    notes: List[str] = field(default_factory=list)

    @property
    def is_reversible(self) -> bool:
        """Both paths exist and asymmetry < 0.20."""
        return (
            self.forward_path.found
            and self.reverse_path.found
            and self.asymmetry < 0.20
        )

    @property
    def is_quantum_critical(self) -> bool:
        """True when the morphism passes through a ⊙ intermediate.

        A quantum critical point is a property of the *transition*, not of
        either endpoint.  The endpoint Varma probe (Factor 8) is a heuristic;
        this is the exact morphism-level predicate.
        """
        return self.quantum_critical_point is not None

    def summary(self) -> str:
        order_str = {
            TransitionOrder.SECOND:  "2nd-order (continuous)",
            TransitionOrder.FIRST:   "1st-order (discontinuous)",
            TransitionOrder.UNKNOWN: "order unknown",
        }[self.order]

        fwd = f"{self.forward_cost:.2f}" if math.isfinite(self.forward_cost) else "∞"
        rev = f"{self.reverse_cost:.2f}" if math.isfinite(self.reverse_cost) else "∞"
        asym = f"{self.asymmetry:.2f}"
        phi_str = (
            f"  ⊙ intermediates: {', '.join(self.phi_c_intermediates)}"
            if self.phi_c_intermediates else ""
        )
        rev_str = "reversible" if self.is_reversible else "irreversible"

        lines = [
            f"{self.src_name} → {self.dst_name}",
            f"  Order: {order_str}",
            f"  Forward cost: {fwd} nat   Reverse cost: {rev} nat",
            f"  Asymmetry: {asym}   ({rev_str})",
        ]
        if phi_str:
            lines.append(phi_str)
        if self.notes:
            lines.append("  Notes:")
            for n in self.notes:
                lines.append(f"    • {n}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Core function
# ─────────────────────────────────────────────────────────────────────────────

def find_qcp_path(
    src: Imscription,
    dst: Imscription,
    catalog: Sequence[Imscription],
    max_hops: int = 6,
    xi_tolerance: float = 1.0,
) -> Optional["TransitionMorphism"]:
    """
    Search specifically for a path from src to dst that passes through a
    ⊙ intermediate — the morphism-level quantum critical point.

    Unlike `find_transition()`, which takes the cheapest BFS path (which may
    bypass a ⊙ intermediate), this function enumerates all ⊙ imscriptions
    in the D/T cluster and checks for two-segment paths:
        src → Φ_c_intermediate → dst

    If any such path exists, returns a TransitionMorphism with
    is_quantum_critical = True and quantum_critical_point populated.
    Returns None if no ⊙-mediated path exists.
    """
    phi_c_candidates = [
        s for s in catalog
        if s.criticality_phase == CriticalityPhase.monad
        and s.dimensionality == src.dimensionality
        and s.topology == src.topology
        and s.name not in (src.name, dst.name)
    ]

    if not phi_c_candidates:
        return None

    from .algebra import find_path as _find_path

    best: Optional[TransitionMorphism] = None

    for qcp_s in phi_c_candidates:
        seg1 = _find_path(src, qcp_s, list(catalog),
                          max_hops=max_hops, xi_tolerance=xi_tolerance)
        seg2 = _find_path(qcp_s, dst, list(catalog),
                          max_hops=max_hops, xi_tolerance=xi_tolerance)

        if not (seg1.found and seg2.found):
            continue

        # Valid 2-segment QCP path found
        total_fwd = seg1.total_delta + seg2.total_delta
        combined_path_names = seg1.path + seg2.path[1:]  # merge without duplicating QCP

        # Build a synthetic PathResult for the combined path
        from .algebra import PathResult
        combined_fwd = PathResult(
            found=True,
            src_name=src.name,
            dst_name=dst.name,
            path=combined_path_names,
            hop_deltas=seg1.hop_deltas + seg2.hop_deltas,
            total_delta=total_fwd,
            notes=[f"QCP-mediated path via {qcp_s.name}"],
        )

        # Reverse path
        rev_seg1 = _find_path(dst, qcp_s, list(catalog),
                              max_hops=max_hops, xi_tolerance=xi_tolerance)
        rev_seg2 = _find_path(qcp_s, src, list(catalog),
                              max_hops=max_hops, xi_tolerance=xi_tolerance)
        if rev_seg1.found and rev_seg2.found:
            rev_path_names = rev_seg1.path + rev_seg2.path[1:]
            combined_rev = PathResult(
                found=True,
                src_name=dst.name,
                dst_name=src.name,
                path=rev_path_names,
                hop_deltas=rev_seg1.hop_deltas + rev_seg2.hop_deltas,
                total_delta=rev_seg1.total_delta + rev_seg2.total_delta,
                notes=[f"Reverse QCP path via {qcp_s.name}"],
            )
            rev_cost = rev_seg1.total_delta + rev_seg2.total_delta
        else:
            combined_rev = PathResult(
                found=False, src_name=dst.name, dst_name=src.name,
                path=[], hop_deltas=[], total_delta=0.0,
                notes=["No reverse QCP path"],
            )
            rev_cost = math.inf

        asym = abs(total_fwd - rev_cost) / max(max(total_fwd, rev_cost), 1e-9)
        if not math.isfinite(asym):
            asym = 1.0

        # Universality hints
        from .models import Granularity, Fidelity, KineticCharacter
        hints = []
        has_galeph = qcp_s.granularity == Granularity.thigh
        has_fhigh  = qcp_s.fidelity == Fidelity.peep
        has_ktrap  = qcp_s.kinetic_character == KineticCharacter.on
        no_temp    = "temporal" not in qcp_s.dimensionality.domains
        if has_galeph and has_fhigh and has_ktrap and no_temp:
            hints.append(
                f"{qcp_s.name}: G_revapostrophe + F_hardsign + K_teshlig + ¬D_∞ → "
                "TFI/heavy-fermion quantum criticality class"
            )
        else:
            hints.append(f"{qcp_s.name}: ⊙ intermediate (universality class unresolved)")

        qcp_obj = QuantumCriticalPoint(
            transition_src=src.name,
            transition_dst=dst.name,
            qcp_imscription_names=[qcp_s.name],
            path_cost=total_fwd,
            universality_hints=hints,
        )

        morph = TransitionMorphism(
            src_name=src.name,
            dst_name=dst.name,
            order=TransitionOrder.SECOND,
            forward_path=combined_fwd,
            reverse_path=combined_rev,
            phi_c_intermediates=[qcp_s.name],
            forward_cost=total_fwd,
            reverse_cost=rev_cost,
            asymmetry=asym,
            quantum_critical_point=qcp_obj,
            notes=[
                f"QCP-mediated path: {src.name} → {qcp_s.name} → {dst.name}",
                f"Segment 1: Δξ={seg1.total_delta:.3f} nat  "
                f"Segment 2: Δξ={seg2.total_delta:.3f} nat",
                f"⊙ intermediate confirms 2nd-order quantum critical transition.",
            ],
        )

        if best is None or total_fwd < best.forward_cost:
            best = morph

    return best


def find_transition(
    src: Imscription,
    dst: Imscription,
    catalog: Sequence[Imscription],
    max_hops: int = 6,
    xi_tolerance: float = 1.0,
) -> TransitionMorphism:
    """
    Determine the transition morphism between two imscriptions.

    Algorithm
    ---------
    1. Run BFS forward  (src → dst) and backward (dst → src).
    2. Classify order:
       - SECOND if forward path exists AND at least one intermediate is ⊙
       - SECOND (degenerate) if forward path exists but no ⊙ intermediate
         (near-critical pair — flag in notes)
       - FIRST  if no forward path (structural conflict blocks HotSwap)
       - UNKNOWN if catalog is empty / both imscriptions absent
    3. Compute costs and asymmetry.
    """
    # --- QCP-first search ---
    # Before the generic BFS, check if there is a ⊙-mediated path.
    # BFS may route around a QCP intermediate when costs are equal; this
    # ensures QCPs are never missed due to tie-breaking order.
    qcp_morph = find_qcp_path(src, dst, catalog, max_hops=max_hops,
                               xi_tolerance=xi_tolerance)
    if qcp_morph is not None:
        return qcp_morph

    fwd = find_path(src, dst, list(catalog),
                    max_hops=max_hops, xi_tolerance=xi_tolerance)
    rev = find_path(dst, src, list(catalog),
                    max_hops=max_hops, xi_tolerance=xi_tolerance)

    # Extract ⊙ intermediates from forward path (exclude endpoints)
    phi_c_names: List[str] = []
    if fwd.found and len(fwd.path) > 2:
        # path is a list of imscription names
        interior = fwd.path[1:-1]
        catalog_map = {s.name: s for s in catalog}
        for name in interior:
            s = catalog_map.get(name)
            if s and s.criticality_phase == CriticalityPhase.monad:
                phi_c_names.append(name)

    # Costs
    fwd_cost = fwd.total_delta if fwd.found else math.inf
    rev_cost = rev.total_delta if rev.found else math.inf

    # Asymmetry ∈ [0, 1]
    denom = max(max(fwd_cost, rev_cost), 1e-9)
    if not math.isfinite(denom):
        asym = 1.0
    else:
        asym = abs(fwd_cost - rev_cost) / denom

    # Order classification
    notes: List[str] = []
    if fwd.found:
        if phi_c_names:
            order = TransitionOrder.SECOND
            notes.append(
                f"⊙ intermediate(s) confirm continuous critical point: "
                f"{', '.join(phi_c_names)}"
            )
        else:
            order = TransitionOrder.SECOND
            notes.append(
                "Forward path exists but no ⊙ intermediates found — "
                "transition may be weakly 2nd-order or sub-critical crossover; "
                "verify Varma score of intermediates"
            )
    elif not fwd.found:
        # Check why — D/T mismatch = structural 1st order
        d_match = src.dimensionality == dst.dimensionality
        t_match = src.topology == dst.topology
        if not d_match or not t_match:
            conflict_dims = []
            if not d_match:
                conflict_dims.append(
                    f"D: {src.dimensionality.value} ≠ {dst.dimensionality.value}"
                )
            if not t_match:
                conflict_dims.append(
                    f"T: {src.topology.value} ≠ {dst.topology.value}"
                )
            order = TransitionOrder.FIRST
            notes.append(
                "Structural conflict blocks HotSwap path — "
                "1st-order transition requires external driver: "
                + "; ".join(conflict_dims)
            )
            notes.append(
                "Virtual Kleisli arrow: morphism exists categorically but "
                "has infinite primitive cost; latent heat ≈ barrier height "
                "between D/T classes"
            )
        else:
            # Same D/T but no path — fidelity or ξ budget exhausted
            order = TransitionOrder.FIRST
            notes.append(
                "No HotSwap path within same D/T class — "
                "fidelity floor or Δξ budget exceeded; "
                "effective 1st-order (nucleation required)"
            )

    # Symmetric distance for reference
    d_sym = tuple_distance(src, dst)
    notes.append(f"Symmetric tuple distance d(src,dst) = {d_sym:.2f}")

    # Quantum critical point detection
    # A QCP is a morphism-level property: 2nd order AND path through ⊙ intermediate.
    # This is the closure of Factor 8: the QCP is the transition, not either endpoint.
    qcp: Optional[QuantumCriticalPoint] = None
    if order == TransitionOrder.SECOND and phi_c_names:
        catalog_map = {s.name: s for s in catalog}
        hints: List[str] = []
        for name in phi_c_names:
            s = catalog_map.get(name)
            if s:
                from .models import Granularity, Fidelity, KineticCharacter
                has_galeph = s.granularity == Granularity.thigh
                has_fhigh  = s.fidelity == Fidelity.peep
                has_ktrap  = s.kinetic_character == KineticCharacter.on
                no_temp    = "temporal" not in s.dimensionality.domains
                if has_galeph and has_fhigh and has_ktrap and no_temp:
                    hints.append(
                        f"{name}: G_revapostrophe + F_hardsign + K_teshlig + ¬D_∞ → "
                        "TFI/heavy-fermion quantum criticality class"
                    )
                elif has_galeph:
                    hints.append(f"{name}: G_revapostrophe → non-local QCP")
                else:
                    hints.append(f"{name}: ⊙ intermediate (universality class unresolved)")
        qcp = QuantumCriticalPoint(
            transition_src=src.name,
            transition_dst=dst.name,
            qcp_imscription_names=phi_c_names,
            path_cost=fwd_cost,
            universality_hints=hints,
        )
        notes.append(
            f"Quantum critical point detected in transition morphism: "
            f"{', '.join(phi_c_names)}. "
            "This is the exact morphism-level QCP predicate (cf. Varma probe "
            "Factor 8, which fires on endpoints — this fires on the path)."
        )

    return TransitionMorphism(
        src_name=src.name,
        dst_name=dst.name,
        order=order,
        forward_path=fwd,
        reverse_path=rev,
        phi_c_intermediates=phi_c_names,
        forward_cost=fwd_cost,
        reverse_cost=rev_cost,
        asymmetry=asym,
        quantum_critical_point=qcp,
        notes=notes,
    )
