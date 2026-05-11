"""
IG_ENSEMBLER — Multi-Imscription Composition Verification

Verifies compatibility of multi-imscription systems. Checks for emergent axiom
violations, computes system-level ξ_CP, and identifies emergent Φ_c candidacy.

Key principle: ξ_CP(Ψ_ensemble) ≠ Σ ξ_CP(S_i).
Interface overhead and cooperative gain must be accounted for separately.

See IG_ENSEMBLER.md for protocol specification.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

from .models import (
    Imscription, Granularity, GrammarOperator, CriticalityPhase, Topology,
)
from .constraints import (
    ConstraintEngine, CompatibilityReport, CompatibilityResult, AxiomValidator,
)
from .thermodynamics import compute_eta_CP
from .varma_probe import degeneracy_strength


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EnsembleCompatibilityEntry:
    """Pairwise compatibility result for two ensemble components."""
    component_a: str
    component_b: str
    result: str              # "Compatible" / "Conditional" / "Incompatible"
    conditions: List[str]
    incompatibilities: List[str]
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pair": f"{self.component_a} ↔ {self.component_b}",
            "result": self.result,
            "conditions": self.conditions,
            "incompatibilities": self.incompatibilities,
            "notes": self.notes,
        }


@dataclass
class EmergentPropertyResult:
    """A single emergent property detected (or not) in the ensemble."""
    property_name: str
    detected: bool
    score: Optional[float] = None
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "property": self.property_name,
            "detected": self.detected,
            "score": round(self.score, 3) if self.score is not None else None,
            "details": self.details,
        }


@dataclass
class EnsembleReport:
    """Full ensemble composition report."""
    component_names: List[str]
    pairwise_matrix: List[EnsembleCompatibilityEntry]
    consistency_score: float    # fraction of compatible pairs
    emergent_properties: List[EmergentPropertyResult]
    ensemble_xi_CP: Optional[float]
    interface_overhead_bits: Optional[float]
    axiom_propagation: Dict[str, str]
    is_consistent: bool
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": self.component_names,
            "consistency_score": round(self.consistency_score, 3),
            "is_consistent": self.is_consistent,
            "pairwise_matrix": [e.to_dict() for e in self.pairwise_matrix],
            "emergent_properties": [e.to_dict() for e in self.emergent_properties],
            "ensemble_xi_CP_nats": (
                round(self.ensemble_xi_CP, 4) if self.ensemble_xi_CP is not None else None
            ),
            "interface_overhead_bits": (
                round(self.interface_overhead_bits, 3)
                if self.interface_overhead_bits is not None else None
            ),
            "axiom_propagation": self.axiom_propagation,
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# EnsembleCatalog
# ---------------------------------------------------------------------------

_COMPAT_LABEL = {
    CompatibilityResult.COMPATIBLE: "Compatible",
    CompatibilityResult.CONDITIONAL: "Conditional",
    CompatibilityResult.INCOMPATIBLE: "Incompatible",
}


class EnsembleCatalog:
    """
    Registry for multi-imscription composition analysis.

    Usage::

        from imscrbgrmr.ensembler import EnsembleCatalog

        ensemble = EnsembleCatalog()
        ensemble.add("rotaxane_axle")     # by catalog name
        ensemble.add("macrocycle_wheel")
        ensemble.add(stopper_imscription)     # or by Imscription object

        report = ensemble.check_pairwise()
        print(report.is_consistent)

        system = ensemble.compute_system_xi_CP(delta_g_assembly=-85.0)
        print(system["xi_CP_system_nats"])
    """

    def __init__(self):
        self._imscriptions: List[Imscription] = []
        self._engine = ConstraintEngine()

    def add(self, imscription_or_name: Union[Imscription, str]) -> "EnsembleCatalog":
        """Add a imscription by object or by name from the global catalog."""
        if isinstance(imscription_or_name, str):
            from .registry import global_catalog
            s = global_catalog.get(imscription_or_name)
            if s is None:
                raise KeyError(
                    f"Imscription '{imscription_or_name}' not found in global catalog."
                )
            self._imscriptions.append(s)
        else:
            self._imscriptions.append(imscription_or_name)
        return self

    def components(self) -> List[Imscription]:
        return list(self._imscriptions)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _pairwise_matrix(self) -> List[EnsembleCompatibilityEntry]:
        entries: List[EnsembleCompatibilityEntry] = []
        n = len(self._imscriptions)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = self._imscriptions[i], self._imscriptions[j]
                report: CompatibilityReport = self._engine.check_pair_compatibility(a, b)
                entries.append(EnsembleCompatibilityEntry(
                    component_a=a.name,
                    component_b=b.name,
                    result=_COMPAT_LABEL.get(report.result, "Unknown"),
                    conditions=report.conditions,
                    incompatibilities=report.details.get("incompatibilities", []),
                    notes=report.details.get("note", ""),
                ))
        return entries

    def _detect_emergent_properties(self) -> List[EmergentPropertyResult]:
        results: List[EmergentPropertyResult] = []

        # 1. Emergent criticality
        individual_scores = [degeneracy_strength(s)[0] for s in self._imscriptions]
        avg_individual = (
            sum(individual_scores) / len(individual_scores) if individual_scores else 0.0
        )
        _NET_TOPOS = {
            Topology.NETWORK, Topology.NETWORK_HEX,
            Topology.NETWORK_MIXED, Topology.NETWORK_INTERPENETRATING,
            Topology.NETWORK_SYM,
        }
        n_network = sum(1 for s in self._imscriptions if s.topology in _NET_TOPOS)
        coop_boost = min(0.30, n_network * 0.10 + len(self._imscriptions) * 0.03)
        ensemble_score = min(1.0, avg_individual + coop_boost)
        emergent_crit = (ensemble_score > avg_individual + 0.10) and ensemble_score >= 0.40

        varma_note = ""
        if ensemble_score >= 0.70:
            varma_note = " Varma probe required to confirm (score ≥ 0.70)."
        results.append(EmergentPropertyResult(
            property_name="Emergent Criticality",
            detected=emergent_crit,
            score=ensemble_score,
            details=(
                f"Ensemble candidacy {ensemble_score:.2f} vs individual avg {avg_individual:.2f}."
                + varma_note
            ),
        ))

        # 2. Granularity amplification G_ב → G_ג (Axiom 3)
        local_count = sum(1 for s in self._imscriptions if s.granularity == Granularity.LOCAL)
        gran_amp = False
        if local_count >= 3:
            ax3 = AxiomValidator.validate_axiom3_cooperative_induction(self._imscriptions)
            gran_amp = ax3.get("should_reclassify_to_mesoscale", False)

        results.append(EmergentPropertyResult(
            property_name="Granularity Amplification (G_ב → G_ג)",
            detected=gran_amp,
            details=(
                f"{local_count} G_ב components. "
                + (
                    "Superlinear induction — reclassify ensemble to G_ג."
                    if gran_amp else "No superlinear induction detected."
                )
            ),
        ))

        # 3. Interface fidelity degradation
        avg_f = sum(s.fidelity.numeric_value for s in self._imscriptions) / len(self._imscriptions)
        matrix = self._pairwise_matrix()
        has_incompat = any(e.result == "Incompatible" for e in matrix)
        iface_lower_f = has_incompat and avg_f > 0.5
        results.append(EmergentPropertyResult(
            property_name="Interface Fidelity Degradation",
            detected=iface_lower_f,
            details=(
                f"Mean F = {avg_f:.2f}. "
                + (
                    "Incompatible pair(s) detected — interface may lower effective F."
                    if iface_lower_f else "No fidelity degradation."
                )
            ),
        ))

        return results

    def _axiom_propagation(self) -> Dict[str, str]:
        props: Dict[str, str] = {}

        # Axiom 1
        cyclic_ok = True
        for s in self._imscriptions:
            r = AxiomValidator.validate_axiom1_cyclic_closure(s)
            if r.get("applies") and r.get("violated"):
                cyclic_ok = False
                break
        props["Axiom 1 (Cyclic Closure)"] = (
            "PASS — cyclic closure holds for all cyclic components."
            if cyclic_ok else
            "FAIL — at least one cyclic component violates F ≥ F_dh."
        )

        # Axiom 2
        has_global_grammar = any(
            s.interaction_grammar.operator == GrammarOperator.OR
            or s.topology in {
                Topology.NETWORK, Topology.NETWORK_HEX,
                Topology.NETWORK_MIXED, Topology.NETWORK_INTERPENETRATING,
                Topology.NETWORK_SYM,
            }
            for s in self._imscriptions
        )
        props["Axiom 2 (Grammar Barrier)"] = (
            "Global propagation (G_ℵ) supported — Γ_∨ or T_nrleg present."
            if has_global_grammar else
            "Local grammar only — ensemble cannot propagate to G_ℵ."
        )

        # Axiom 3
        ax3 = AxiomValidator.validate_axiom3_cooperative_induction(self._imscriptions)
        props["Axiom 3 (Cooperative Induction)"] = (
            "Superlinear induction — reclassify ensemble to G_ג."
            if ax3.get("should_reclassify_to_mesoscale", False) else
            "No superlinear induction — G assignments unchanged."
        )

        # Axiom 5
        max_score = max((degeneracy_strength(s)[0] for s in self._imscriptions), default=0.0)
        if max_score >= 0.70:
            props["Axiom 5 (Criticality)"] = (
                f"Ensemble degeneracy_strength = {max_score:.2f} ≥ 0.70. "
                "Assign Φ_c to ensemble tuple. Run Varma probe to confirm."
            )
        else:
            props["Axiom 5 (Criticality)"] = (
                f"Ensemble degeneracy_strength = {max_score:.2f} < 0.70. Retain Φ_sub."
            )

        return props

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_pairwise(self) -> EnsembleReport:
        """Check all N×N interactions and return a full EnsembleReport."""
        if len(self._imscriptions) < 2:
            return EnsembleReport(
                component_names=[s.name for s in self._imscriptions],
                pairwise_matrix=[],
                consistency_score=1.0,
                emergent_properties=[],
                ensemble_xi_CP=None,
                interface_overhead_bits=None,
                axiom_propagation={},
                is_consistent=True,
                warnings=["Need at least 2 components for pairwise check."],
            )

        matrix = self._pairwise_matrix()
        n_compat = sum(1 for e in matrix if e.result == "Compatible")
        consistency = n_compat / len(matrix) if matrix else 1.0
        is_consistent = all(e.result != "Incompatible" for e in matrix)

        emergent = self._detect_emergent_properties()
        axiom_prop = self._axiom_propagation()

        warnings: List[str] = []
        for e in matrix:
            if e.result == "Incompatible":
                warnings.append(
                    f"Incompatible: {e.component_a} ↔ {e.component_b} "
                    f"(primitives: {', '.join(e.incompatibilities)})"
                )

        return EnsembleReport(
            component_names=[s.name for s in self._imscriptions],
            pairwise_matrix=matrix,
            consistency_score=consistency,
            emergent_properties=emergent,
            ensemble_xi_CP=None,
            interface_overhead_bits=None,
            axiom_propagation=axiom_prop,
            is_consistent=is_consistent,
            warnings=warnings,
        )

    def compute_system_xi_CP(
        self,
        delta_g_assembly: float,
        interface_overhead_bits: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Compute system-level ξ_CP for the assembly event.

        Uses the most constrained (highest F) component as reference.
        Interface overhead adds bits to ξ_CP via the Landauer identity.
        """
        if not self._imscriptions:
            return {"error": "No components registered."}

        # Use the component with highest fidelity as thermodynamic reference
        ref = max(self._imscriptions, key=lambda s: s.fidelity.numeric_value)
        try:
            result = compute_eta_CP(ref, delta_g_assembly)
            xi_system = result.xi_CP + interface_overhead_bits * math.log(2)
            eta_system = math.exp(-xi_system)
        except Exception as exc:
            return {"error": str(exc)}

        tier = (
            "LOW" if xi_system > 9.0 else
            "MEDIUM" if xi_system > 7.0 else
            "HIGH"
        )
        return {
            "num_components": len(self._imscriptions),
            "reference_imscription": ref.name,
            "delta_g_assembly_kJ_mol": delta_g_assembly,
            "eta_CP_system": round(eta_system, 6),
            "xi_CP_system_nats": round(xi_system, 4),
            "interface_overhead_bits": interface_overhead_bits,
            "efficiency_tier": tier,
        }
