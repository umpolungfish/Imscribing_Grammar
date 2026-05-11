"""
IG_TRAJECTORY — Temporal Pathway Encoding

Encodes D_∞ systems as sequences of step-tuples rather than steady-state
snapshots. Validates:
  1. Axiom Continuity — consecutive steps satisfy axioms relative to prior step
  2. Axiom 6 Compliance — the full sequence contains a legitimate reset
  3. Kinetic Traps — steps where K_new = K_teshlig relative to prior state

See IG_TRAJECTORY.md for protocol specification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    Imscription, KineticCharacter, Dimensionality, RecognitionMode,
)
from .constraints import AxiomValidator, AxiomResult
from .varma_probe import degeneracy_strength, VarmaCorrelationData


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TrajectoryStep:
    """A single mechanistic step in a D_∞ cycle."""
    imscription: Imscription
    step_name: str
    delta_g: Optional[float] = None          # kJ/mol (reaction ΔG, signed)
    delta_g_ddagger: Optional[float] = None  # kJ/mol (activation barrier ΔG‡)
    is_reset_step: bool = False              # True for the step returning to S_t0
    notes: str = ""

    @property
    def kinetic_character(self) -> KineticCharacter:
        return self.imscription.kinetic_character


@dataclass
class ContinuityCheckResult:
    """Axiom-continuity check between two consecutive steps."""
    step_a: str
    step_b: str
    mass_balance_ok: bool     # S primitive consistency
    axiom4_ok: bool           # Sequential grammar: D_∞ or R_‡ present
    kinetic_accessible: bool  # No K_teshlig without noted bypass
    issues: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.mass_balance_ok and self.axiom4_ok and self.kinetic_accessible

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition": f"{self.step_a} → {self.step_b}",
            "passed": self.passed,
            "mass_balance_ok": self.mass_balance_ok,
            "axiom4_ok": self.axiom4_ok,
            "kinetic_accessible": self.kinetic_accessible,
            "issues": self.issues,
        }


@dataclass
class StepCriticalityResult:
    """G/D degeneracy score for a single trajectory step."""
    step_name: str
    degeneracy_score: float
    tier: str               # "none" / "logarithmic" / "power-law" / "collapse"
    is_phi_c_candidate: bool  # score ≥ 0.70

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_name,
            "degeneracy_score": round(self.degeneracy_score, 3),
            "tier": self.tier,
            "phi_c_candidate": self.is_phi_c_candidate,
        }


@dataclass
class TrajectoryValidationResult:
    """Full trajectory validation report."""
    cycle_name: str
    num_steps: int
    continuity_results: List[ContinuityCheckResult]
    reset_verified: bool
    reset_step: Optional[str]
    kinetic_traps: List[str]           # step names with K_teshlig or barrier > 100 kJ/mol
    criticality_per_step: List[StepCriticalityResult]
    axiom6_satisfied: bool
    overall_valid: bool
    warnings: List[str] = field(default_factory=list)

    @property
    def full_cycle_candidacy(self) -> float:
        """Average degeneracy score across all steps."""
        if not self.criticality_per_step:
            return 0.0
        return (
            sum(s.degeneracy_score for s in self.criticality_per_step)
            / len(self.criticality_per_step)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cycle": self.cycle_name,
            "num_steps": self.num_steps,
            "overall_valid": self.overall_valid,
            "axiom6_satisfied": self.axiom6_satisfied,
            "reset_verified": self.reset_verified,
            "reset_step": self.reset_step,
            "kinetic_traps": self.kinetic_traps,
            "full_cycle_candidacy_score": round(self.full_cycle_candidacy, 3),
            "continuity_checks": [c.to_dict() for c in self.continuity_results],
            "criticality_per_step": [s.to_dict() for s in self.criticality_per_step],
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------------------
# TemporalImscriptionAgent
# ---------------------------------------------------------------------------

_RESET_KEYWORDS = [
    "reset", "reform", "regenerat", "hydroly", "return",
    "cycle", "turnover", "re-form", "dissipat", "renew",
    "restore", "recycl", "replenish", "reconstitut",
]


class TemporalImscriptionAgent:
    """
    Validates D_∞ systems as step sequences.

    Protocol::

        agent = TemporalImscriptionAgent("proline_aldol")
        agent.add_step(enamine_imscription, "enamine_formation", delta_g=-15.0)
        agent.add_step(ts_imscription,      "c_c_bond_form",     delta_g_ddagger=97.0)
        agent.add_step(hydrolysis_syn,  "hydrolysis_reset",  delta_g=-25.0, is_reset=True)
        result = agent.validate_all()
        print(result.overall_valid)
    """

    def __init__(self, cycle_name: str = "unnamed_cycle"):
        self.cycle_name = cycle_name
        self._steps: List[TrajectoryStep] = []

    def add_step(
        self,
        imscription: Imscription,
        step_name: Optional[str] = None,
        delta_g: Optional[float] = None,
        delta_g_ddagger: Optional[float] = None,
        is_reset: bool = False,
        notes: str = "",
    ) -> "TemporalImscriptionAgent":
        """Register a mechanistic step. Returns self for chaining."""
        name = step_name or f"step_{len(self._steps) + 1}"
        self._steps.append(TrajectoryStep(
            imscription=imscription,
            step_name=name,
            delta_g=delta_g,
            delta_g_ddagger=delta_g_ddagger,
            is_reset_step=is_reset,
            notes=notes,
        ))
        return self

    # ------------------------------------------------------------------
    # Check 1: Continuity
    # ------------------------------------------------------------------

    def validate_continuity(self) -> List[ContinuityCheckResult]:
        """
        Check axiom continuity between consecutive steps.

        Per IG_TRAJECTORY.md §3.2:
          1. Mass Balance — S primitive must be consistent across steps
          2. Axiom 4 — every step must have D_∞ or R_‡ (sequential grammar)
          3. Kinetic Accessibility — K_teshlig or ΔG‡ > 100 kJ/mol flagged
        """
        results: List[ContinuityCheckResult] = []
        for i in range(len(self._steps) - 1):
            a = self._steps[i]
            b = self._steps[i + 1]
            issues: List[str] = []

            # 1. Mass balance via S primitive
            s_a = getattr(a.imscription, "stoichiometry", None)
            s_b = getattr(b.imscription, "stoichiometry", None)
            if s_a and s_b and s_a != s_b:
                mass_balance_ok = False
                issues.append(
                    f"S mismatch: '{s_a}' → '{s_b}' — mass balance violation"
                )
            else:
                mass_balance_ok = True

            # 2. Axiom 4: D_∞ or R_‡ required for every sequential step
            has_temporal = "temporal" in b.imscription.dimensionality.domains
            has_catalytic = b.imscription.recognition_mode in {
                RecognitionMode.DYNAMIC_CATALYTIC,
                RecognitionMode.COVALENT_DYNAMIC,
            }
            axiom4_ok = has_temporal or has_catalytic
            if not axiom4_ok:
                issues.append(
                    f"Axiom 4 violation at '{b.step_name}': "
                    "sequential step requires D_∞ or R_‡"
                )

            # 3. Kinetic accessibility
            if b.imscription.kinetic_character == KineticCharacter.TRAP:
                kinetic_accessible = False
                issues.append(
                    f"K_teshlig at '{b.step_name}': pathway multiplicity — "
                    "run K-compatibility check (IG_HOTSWAP.md §2.2)"
                )
            elif b.delta_g_ddagger is not None and b.delta_g_ddagger > 100.0:
                kinetic_accessible = False
                issues.append(
                    f"Barrier spike at '{b.step_name}': "
                    f"ΔG‡ = {b.delta_g_ddagger:.1f} kJ/mol > 100 → K_schwa flag"
                )
            else:
                kinetic_accessible = True

            results.append(ContinuityCheckResult(
                step_a=a.step_name,
                step_b=b.step_name,
                mass_balance_ok=mass_balance_ok,
                axiom4_ok=axiom4_ok,
                kinetic_accessible=kinetic_accessible,
                issues=issues,
            ))
        return results

    # ------------------------------------------------------------------
    # Check 2: Axiom 6 reset verification
    # ------------------------------------------------------------------

    def verify_reset(self) -> Tuple[bool, Optional[str]]:
        """
        Axiom 6: verify the cycle contains a step that returns to S_t0.

        Checks:
          - Explicit is_reset=True flag, OR
          - Final step description contains reset/regeneration keywords
        """
        if not self._steps:
            return False, None

        # Explicit flag
        reset_steps = [s for s in self._steps if s.is_reset_step]
        if reset_steps:
            return True, reset_steps[-1].step_name

        # Keyword fallback in last step description
        last = self._steps[-1]
        desc = (last.imscription.description or "").lower()
        if any(kw in desc for kw in _RESET_KEYWORDS):
            return True, last.step_name

        return False, None

    # ------------------------------------------------------------------
    # Check 3: Criticality scan
    # ------------------------------------------------------------------

    def scan_criticality(
        self,
        correlation_data: Optional[Dict[str, VarmaCorrelationData]] = None,
    ) -> List[StepCriticalityResult]:
        """
        Compute G/D degeneracy score for each step via Varma probe.

        Args:
            correlation_data: optional dict mapping step_name → VarmaCorrelationData
        """
        results: List[StepCriticalityResult] = []
        for step in self._steps:
            cd = correlation_data.get(step.step_name) if correlation_data else None
            score, tier = degeneracy_strength(step.imscription, cd)
            results.append(StepCriticalityResult(
                step_name=step.step_name,
                degeneracy_score=score,
                tier=tier,
                is_phi_c_candidate=score >= 0.70,
            ))
        return results

    # ------------------------------------------------------------------
    # Main: validate_all
    # ------------------------------------------------------------------

    def validate_all(
        self,
        correlation_data: Optional[Dict[str, VarmaCorrelationData]] = None,
    ) -> TrajectoryValidationResult:
        """Run all validation checks and return a full trajectory report."""
        if not self._steps:
            return TrajectoryValidationResult(
                cycle_name=self.cycle_name,
                num_steps=0,
                continuity_results=[],
                reset_verified=False,
                reset_step=None,
                kinetic_traps=[],
                criticality_per_step=[],
                axiom6_satisfied=False,
                overall_valid=False,
                warnings=["No steps registered."],
            )

        continuity = self.validate_continuity()
        reset_verified, reset_step = self.verify_reset()
        criticality = self.scan_criticality(correlation_data)

        # Collect kinetic traps
        kinetic_traps: List[str] = []
        for step in self._steps:
            if step.imscription.kinetic_character == KineticCharacter.TRAP:
                kinetic_traps.append(step.step_name)
            elif step.delta_g_ddagger is not None and step.delta_g_ddagger > 100.0:
                kinetic_traps.append(step.step_name)

        # Axiom 6
        axiom6_result = AxiomValidator.validate_axiom6_temporal_grounding(
            self._steps[0].imscription
        )
        axiom6_base = (
            axiom6_result.satisfied
            if isinstance(axiom6_result, AxiomResult)
            else bool(axiom6_result.get("satisfied", True))
        )
        axiom6_satisfied = reset_verified and axiom6_base

        continuity_ok = all(c.passed for c in continuity)
        overall_valid = continuity_ok and axiom6_satisfied

        warnings: List[str] = []
        if not reset_verified:
            warnings.append(
                "No reset step found. Mark the regeneration step with is_reset=True "
                "or include 'reset'/'regenerate'/'hydrolysis' in the step description."
            )

        # Varma probe warnings for high-degeneracy steps
        for crit in criticality:
            if crit.degeneracy_score >= 0.70:
                warnings.append(
                    f"Step '{crit.step_name}': degeneracy_strength = {crit.degeneracy_score:.2f} ≥ 0.70 — "
                    "run full Varma probe to confirm Φ_c before HotSwap screening."
                )

        return TrajectoryValidationResult(
            cycle_name=self.cycle_name,
            num_steps=len(self._steps),
            continuity_results=continuity,
            reset_verified=reset_verified,
            reset_step=reset_step,
            kinetic_traps=kinetic_traps,
            criticality_per_step=criticality,
            axiom6_satisfied=axiom6_satisfied,
            overall_valid=overall_valid,
            warnings=warnings,
        )
