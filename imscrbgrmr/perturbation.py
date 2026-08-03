"""
IG_PERTURBATION — Controlled Perturbation Protocol

Implements the Primitive Jacobian: sensitivity analysis over the 10-primitive
tuple space. For each primitive, computes Δξ_CP when that primitive is shifted
by one tier. Used for fault injection, rational tuning, and identifying
load-bearing vs. decorative primitives.

See IG_PERTURBATION.md for protocol specification.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    Imscription, Dimensionality, Topology, RecognitionMode,
    Polarity, Fidelity, KineticCharacter, Granularity,
    InteractionGrammar, GrammarOperator, CriticalityPhase,
)
from .thermodynamics import compute_eta_CP, ConstraintPropagationEfficiency
from .constraints import AxiomValidator


# ---------------------------------------------------------------------------
# Primitive weights (from CrossDomainAnalogyDetector.PRIMITIVE_WEIGHTS)
# ---------------------------------------------------------------------------

PRIMITIVE_WEIGHTS: Dict[str, float] = {
    "D": 0.20,
    "T": 0.15,
    "R": 0.12,
    "F": 0.12,
    "P": 0.10,
    "<": 0.10,
    "G": 0.10,
    "K": 0.08,
    "S": 0.08,
    "∈": 0.05,
    "◻": 0.08,  # Topological protection index — similar load to K
}

# ---------------------------------------------------------------------------
# Tier orderings — from lowest to highest
# ---------------------------------------------------------------------------

_FIDELITY_TIERS = [Fidelity.age, Fidelity.they, Fidelity.peep]
_KINETIC_TIERS = [
    KineticCharacter.yea, KineticCharacter.loll,
    KineticCharacter.egg, KineticCharacter.on,
    KineticCharacter.air,   # disorder-frozen: most arrested state, beyond energy-barrier trapping
]
_GRANULARITY_TIERS = [Granularity.ice, Granularity.bib, Granularity.thigh]
_TOPOLOGY_TIERS = [
    Topology.eat, Topology.eat, Topology.mime,
    Topology.eat, Topology.judge,
    Topology.judge, Topology.judge, Topology.judge,
    Topology.judge, Topology.judge,
    Topology.oil,
    Topology.mime,  # anyonic topology — orthogonal axis but placed at high complexity
]
_DIM_TIERS = [
    Dimensionality.dead, Dimensionality.ash, Dimensionality.array,
    Dimensionality.ash, Dimensionality.array,
    Dimensionality.array, Dimensionality.ash,
]
_RECOGNITION_TIERS = [
    RecognitionMode.ado, RecognitionMode.ear,
    RecognitionMode.tot, RecognitionMode.tot,
    RecognitionMode.ian,
]
_POLARITY_TIERS = [
    Polarity.yew, Polarity.yew, Polarity.yew,
    Polarity.or_, Polarity.church,
]
_CRITICALITY_TIERS = [
    CriticalityPhase.woe, CriticalityPhase.monad, CriticalityPhase.haha,
]

_PRIM_LABELS: Dict[str, str] = {
    "F": "Fidelity", "K": "Kinetic Character", "T": "Topology",
    "D": "Dimensionality", "R": "Recognition Mode", "P": "Polarity",
    "G": "Granularity", "<": "Criticality Phase", "S": "Stoichiometry",
    "∈": "Coupling", "◻": "Topological Protection Index",
}

_PRIM_ATTR: Dict[str, str] = {
    "F": "fidelity", "K": "kinetic_character", "T": "topology",
    "D": "dimensionality", "R": "recognition_mode", "P": "polarity",
    "G": "granularity", "<": "criticality_phase", "◻": "topo_index",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_tier(value, tiers: list):
    """Return the next value in a tier list, or None if already at maximum."""
    try:
        idx = tiers.index(value)
        if idx + 1 < len(tiers):
            return tiers[idx + 1]
    except ValueError:
        pass
    return None


def _prev_tier(value, tiers: list):
    """Return the previous value in a tier list, or None if already at minimum."""
    try:
        idx = tiers.index(value)
        if idx - 1 >= 0:
            return tiers[idx - 1]
    except ValueError:
        pass
    return None


def _sensitivity_label(delta_xi: float, weight: float) -> str:
    """Map |Δξ_CP| × weight → CRITICAL / HIGH / MEDIUM / LOW."""
    effective = abs(delta_xi) * weight * 10
    if effective >= 3.0:
        return "CRITICAL"
    elif effective >= 1.5:
        return "HIGH"
    elif effective >= 0.5:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PerturbationResult:
    """Result of shifting a single primitive by one tier."""
    primitive: str           # "F", "K", "T", …
    primitive_name: str      # human-readable
    old_value: str
    new_value: str
    baseline_xi_CP: float    # nats
    perturbed_xi_CP: float   # nats
    delta_xi_CP: float       # perturbed − baseline
    sensitivity: str         # CRITICAL / HIGH / MEDIUM / LOW
    direction: str = "up"    # "up" or "down" tier shift
    axiom_violated: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primitive": self.primitive,
            "primitive_name": self.primitive_name,
            "shift": f"{self.old_value} → {self.new_value}",
            "direction": self.direction,
            "delta_xi_CP_nats": round(self.delta_xi_CP, 4),
            "perturbed_xi_CP_nats": round(self.perturbed_xi_CP, 4),
            "sensitivity": self.sensitivity,
            "axiom_violated": self.axiom_violated,
        }


@dataclass
class PrimitiveJacobian:
    """Full Jacobian: Δξ_CP sensitivity for each primitive."""
    imscription_name: str
    baseline_xi_CP: float
    delta_g: float
    results: List[PerturbationResult] = field(default_factory=list)
    fault_primitives: List[str] = field(default_factory=list)

    @property
    def most_sensitive(self) -> Optional[PerturbationResult]:
        if not self.results:
            return None
        return max(self.results, key=lambda r: abs(r.delta_xi_CP))

    @property
    def critical_primitives(self) -> List[PerturbationResult]:
        return [r for r in self.results if r.sensitivity == "CRITICAL"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "imscription": self.imscription_name,
            "baseline_xi_CP_nats": round(self.baseline_xi_CP, 4),
            "delta_g_kJ_mol": self.delta_g,
            "perturbation_results": [r.to_dict() for r in self.results],
            "most_sensitive_primitive": (
                self.most_sensitive.primitive if self.most_sensitive else None
            ),
            "fault_primitives": self.fault_primitives,
        }


# ---------------------------------------------------------------------------
# PerturbationEngine
# ---------------------------------------------------------------------------

class PerturbationEngine:
    """
    Computes the Primitive Jacobian for a imscription.

    For each of the 8 non-stoichiometry primitives, shifts the value by one
    tier (up or down), recomputes ξ_CP, and records Δξ_CP and sensitivity.

    Example::

        engine = PerturbationEngine()
        jacobian = engine.sweep_all(imscription, delta_g=-12.0)
        print(jacobian.most_sensitive.primitive)   # e.g. "T"
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _mutated(self, imscription: Imscription, primitive: str, new_value) -> Imscription:
        """Return a shallow copy of imscription with one primitive changed."""
        s = copy.copy(imscription)
        attr = _PRIM_ATTR.get(primitive)
        if attr:
            setattr(s, attr, new_value)
        return s

    def _axiom_violation(self, imscription: Imscription) -> Optional[str]:
        """Return the first violated axiom key, or None."""
        try:
            report = AxiomValidator.validate_all_axioms(imscription)
            if report["violations"] > 0:
                for key, val in report["detailed_results"].items():
                    violated = (
                        val.get("violated", False)
                        if isinstance(val, dict)
                        else getattr(val, "violated", False)
                    )
                    if violated:
                        return key
        except Exception:
            pass
        return None

    def _perturb_one(
        self,
        imscription: Imscription,
        primitive: str,
        new_value,
        delta_g: float,
        baseline_xi: float,
        direction: str,
    ) -> PerturbationResult:
        """Compute a single perturbation result."""
        mutated = self._mutated(imscription, primitive, new_value)
        try:
            perturbed_xi = compute_eta_CP(mutated, delta_g).xi_CP
        except Exception:
            perturbed_xi = baseline_xi + 99.0  # treat as collapse

        delta_xi = perturbed_xi - baseline_xi
        axiom = self._axiom_violation(mutated)
        weight = PRIMITIVE_WEIGHTS.get(primitive, 0.05)

        old_str = str(getattr(imscription, _PRIM_ATTR.get(primitive, ""), "?")).split(".")[-1]
        new_str = str(new_value).split(".")[-1] if new_value is not None else "N/A"

        return PerturbationResult(
            primitive=primitive,
            primitive_name=_PRIM_LABELS.get(primitive, primitive),
            old_value=old_str,
            new_value=new_str,
            baseline_xi_CP=baseline_xi,
            perturbed_xi_CP=min(perturbed_xi, baseline_xi + 99.0),
            delta_xi_CP=min(delta_xi, 99.0),
            sensitivity=_sensitivity_label(delta_xi, weight),
            direction=direction,
            axiom_violated=axiom,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_baseline(self, imscription: Imscription, delta_g: float) -> ConstraintPropagationEfficiency:
        """Compute baseline η_CP / ξ_CP."""
        return compute_eta_CP(imscription, delta_g)

    def sweep_all(self, imscription: Imscription, delta_g: float) -> PrimitiveJacobian:
        """
        Run a full single-primitive sweep across all perturbable primitives.

        For each primitive, tries both up and down shifts; reports whichever
        produces the largest |Δξ_CP|.
        """
        baseline = self.compute_baseline(imscription, delta_g)
        xi0 = baseline.xi_CP

        perturb_map: List[Tuple[str, Any, list]] = [
            ("F", imscription.fidelity,           _FIDELITY_TIERS),
            ("K", imscription.kinetic_character,  _KINETIC_TIERS),
            ("T", imscription.topology,           _TOPOLOGY_TIERS),
            ("D", imscription.dimensionality,     _DIM_TIERS),
            ("R", imscription.recognition_mode,   _RECOGNITION_TIERS),
            ("P", imscription.polarity,           _POLARITY_TIERS),
            ("G", imscription.granularity,        _GRANULARITY_TIERS),
        ]
        if imscription.criticality_phase is not None:
            perturb_map.append(("<", imscription.criticality_phase, _CRITICALITY_TIERS))

        results: List[PerturbationResult] = []
        fault_prims: List[str] = []

        for prim, current, tiers in perturb_map:
            candidates: List[PerturbationResult] = []
            up = _next_tier(current, tiers)
            down = _prev_tier(current, tiers)
            if up is not None:
                candidates.append(self._perturb_one(imscription, prim, up, delta_g, xi0, "up"))
            if down is not None:
                candidates.append(self._perturb_one(imscription, prim, down, delta_g, xi0, "down"))
            if candidates:
                best = max(candidates, key=lambda r: abs(r.delta_xi_CP))
                results.append(best)
                if best.axiom_violated:
                    fault_prims.append(prim)

        # Sort by |Δξ_CP| descending
        results.sort(key=lambda r: abs(r.delta_xi_CP), reverse=True)

        return PrimitiveJacobian(
            imscription_name=imscription.name,
            baseline_xi_CP=xi0,
            delta_g=delta_g,
            results=results,
            fault_primitives=fault_prims,
        )

    def fault_injection(self, imscription: Imscription, delta_g: float) -> Dict[str, Any]:
        """
        Identify Single Points of Failure (SPOF): primitive changes that
        cause axiom violations or ξ_CP collapse.
        """
        jacobian = self.sweep_all(imscription, delta_g)
        spofs = [
            r for r in jacobian.results
            if r.axiom_violated or r.sensitivity == "CRITICAL"
        ]
        return {
            "imscription": imscription.name,
            "baseline_xi_CP_nats": round(jacobian.baseline_xi_CP, 4),
            "single_points_of_failure": [r.to_dict() for r in spofs],
            "fault_primitives": jacobian.fault_primitives,
            "most_brittle": spofs[0].to_dict() if spofs else None,
            "system_robust": len(spofs) == 0,
        }

    def find_path_to_target(
        self,
        imscription: Imscription,
        delta_g: float,
        target_xi_CP: float,
        optimize_primitives: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Find the minimal sequence of primitive changes to reach target ξ_CP.

        Direction is inferred automatically:
          - target < baseline  → efficiency improvement path  (collect negative Δξ_CP)
          - target > baseline  → degradation / probing path   (collect positive Δξ_CP)
          - target == baseline → no steps needed

        Greedily applies the largest-magnitude steps in the required direction
        until the target is reached or all available steps are exhausted.
        """
        jacobian = self.sweep_all(imscription, delta_g)
        baseline = jacobian.baseline_xi_CP

        if abs(baseline - target_xi_CP) < 1e-6:
            return {
                "imscription": imscription.name,
                "baseline_xi_CP_nats": round(baseline, 4),
                "target_xi_CP_nats": target_xi_CP,
                "achieved_xi_CP_nats": round(baseline, 4),
                "target_reached": True,
                "direction": "none",
                "recommended_steps": [],
                "num_steps": 0,
            }

        lowering = target_xi_CP < baseline  # True → efficiency improvement; False → degradation probe

        pool = jacobian.results
        if optimize_primitives:
            pool = [r for r in pool if r.primitive in optimize_primitives]

        if lowering:
            # Collect steps that decrease ξ_CP; sort most-negative first
            candidates = sorted(
                [r for r in pool if r.delta_xi_CP < 0],
                key=lambda r: r.delta_xi_CP,
            )
        else:
            # Collect steps that increase ξ_CP; sort most-positive first
            candidates = sorted(
                [r for r in pool if r.delta_xi_CP > 0],
                key=lambda r: r.delta_xi_CP,
                reverse=True,
            )

        path: List[PerturbationResult] = []
        current_xi = baseline
        for step in candidates:
            if lowering and current_xi <= target_xi_CP:
                break
            if not lowering and current_xi >= target_xi_CP:
                break
            path.append(step)
            current_xi += step.delta_xi_CP

        reached = (current_xi <= target_xi_CP) if lowering else (current_xi >= target_xi_CP)

        return {
            "imscription": imscription.name,
            "baseline_xi_CP_nats": round(baseline, 4),
            "target_xi_CP_nats": target_xi_CP,
            "achieved_xi_CP_nats": round(current_xi, 4),
            "target_reached": reached,
            "direction": "improvement" if lowering else "degradation",
            "recommended_steps": [r.to_dict() for r in path],
            "num_steps": len(path),
        }
