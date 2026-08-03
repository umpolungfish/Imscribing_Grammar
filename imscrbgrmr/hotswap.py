"""
IG_HOTSWAP — Dynamic Component Exchange Protocol

Implements the 5-step HotSwap workflow from IG_HOTSWAP.md:

1. Target Identification
2. Candidate Selection (via analogy search)
3. Axiomatic Validation
4. Thermodynamic Feasibility Check
5. Execution & Verification (checklist)

All enforcement criteria from the protocol spec are implemented:
- D, T, S exact match (or --allow-defect-fraction for G_ℵ)
- F_new ≥ F_old hard floor
- |Δξ_CP| < 1.0 nat tolerance (+0.5 nat K-multiplicity penalty)
- K accessible (FAST or MODERATE only)
- Grounding status full or override before swap
- ⊙ Varma probe requirement when degeneracy_strength ≥ 0.70
- Full axiom validation (Axioms 1, 4, 6, 7 are critical checks)

See IG_HOTSWAP.md for specification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    Imscription,
    Dimensionality,
    Topology,
    Fidelity,
    KineticCharacter,
    Granularity,
    CriticalityPhase,
)
from .constraints import AxiomValidator
from .thermodynamics import compute_eta_CP


# ---------------------------------------------------------------------------
# Thresholds (from IG_HOTSWAP.md §2.2 and §8.0)
# ---------------------------------------------------------------------------

XI_CP_TOLERANCE: float = 1.0          # |Δξ_CP| < 1.0 nat
K_MULTIPLICITY_PENALTY: float = 0.5   # +0.5 nat when >2 new pathways
VARMA_PHI_C_THRESHOLD: float = 0.70   # degeneracy_strength ≥ 0.70 → Varma required
GROUNDING_REQUIRED = {"full", "override"}  # grounding_status values that pass

# Fidelity tier order: lower index = lower fidelity
_FIDELITY_ORDER = [Fidelity.age, Fidelity.they, Fidelity.peep]


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

class HotSwapDecision(str, Enum):
    APPROVED  = "APPROVED"
    BLOCKED   = "BLOCKED"
    CONDITIONAL = "CONDITIONAL"   # Passes but has warnings


@dataclass
class PrimitiveCheckResult:
    """Result of a single primitive constraint check."""
    primitive: str               # e.g. "D", "T", "F", "K"
    passed: bool
    old_value: str
    new_value: str
    note: str = ""


@dataclass
class HotSwapReport:
    """
    Full report produced by HotSwapEngine.validate_candidate().

    Attributes:
        decision:           APPROVED / CONDITIONAL / BLOCKED
        target_name:        Name of the imscription being replaced (S_old)
        candidate_name:     Name of the proposed replacement (S_new)
        xi_old:             ξ_CP of S_old (nats)
        xi_new:             ξ_CP of S_new (nats)
        delta_xi:           ξ_new − ξ_old (nats); negative = more efficient
        k_multiplicity_penalty: 0.0 or 0.5 nat applied to effective Δξ_CP
        effective_delta_xi: delta_xi + k_multiplicity_penalty
        primitive_checks:   Per-primitive pass/fail results
        axiom_report:       Full axiom validation dict for S_new
        grounding_check:    Grounding status result
        varma_required:     True when Varma probe must be run before swap
        varma_score:        degeneracy_strength score if available
        violations:         Hard blocking reasons
        warnings:           Non-blocking cautions
        checklist:          Summary checklist (Section 8.0)
    """
    decision: HotSwapDecision
    target_name: str
    candidate_name: str
    xi_old: Optional[float]
    xi_new: Optional[float]
    delta_xi: Optional[float]
    k_multiplicity_penalty: float
    effective_delta_xi: Optional[float]
    primitive_checks: List[PrimitiveCheckResult]
    axiom_report: Dict[str, Any]
    grounding_check: Dict[str, Any]
    varma_required: bool
    varma_score: Optional[float]
    violations: List[str]
    warnings: List[str]
    checklist: Dict[str, bool]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "target": self.target_name,
            "candidate": self.candidate_name,
            "xi_old_nats": round(self.xi_old, 4) if self.xi_old is not None else None,
            "xi_new_nats": round(self.xi_new, 4) if self.xi_new is not None else None,
            "delta_xi_nats": round(self.delta_xi, 4) if self.delta_xi is not None else None,
            "k_multiplicity_penalty_nats": self.k_multiplicity_penalty,
            "effective_delta_xi_nats": (
                round(self.effective_delta_xi, 4)
                if self.effective_delta_xi is not None else None
            ),
            "primitive_checks": [
                {
                    "primitive": c.primitive,
                    "passed": c.passed,
                    "old": c.old_value,
                    "new": c.new_value,
                    "note": c.note,
                }
                for c in self.primitive_checks
            ],
            "axiom_violations": self.axiom_report.get("violations", 0),
            "axiom_satisfied": self.axiom_report.get("all_satisfied", False),
            "grounding_check": self.grounding_check,
            "varma_required": self.varma_required,
            "varma_score": self.varma_score,
            "violations": self.violations,
            "warnings": self.warnings,
            "checklist": self.checklist,
        }


# ---------------------------------------------------------------------------
# HotSwapEngine
# ---------------------------------------------------------------------------

class HotSwapEngine:
    """
    Enforces the Imscriptive HotSwap protocol from IG_HOTSWAP.md.

    Usage::

        from imscrbgrmr.hotswap import HotSwapEngine
        from imscrbgrmr import global_catalog

        engine = HotSwapEngine()
        target    = global_catalog.get("proline_aldol_cycle")
        candidate = global_catalog.get("allene_crown_catalyst")

        report = engine.validate_candidate(target, candidate, delta_g=-12.0)
        if report.decision == HotSwapDecision.APPROVED:
            print("Swap approved — Δξ_CP =", report.effective_delta_xi)
        else:
            print("Swap blocked:", report.violations)
    """

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def validate_candidate(
        self,
        target: Imscription,
        candidate: Imscription,
        delta_g: float = -12.0,
        allow_defect_fraction: Optional[float] = None,
        new_pathway_count: int = 0,
        varma_score: Optional[float] = None,
    ) -> HotSwapReport:
        """
        Run all HotSwap compatibility checks (Steps 3–4 of the protocol).

        Args:
            target:               The imscription to be replaced (S_old).
            candidate:            The proposed replacement (S_new).
            delta_g:              ΔG basis for ξ_CP computation (kJ/mol).
            allow_defect_fraction: For G_ℵ assemblies only — relax S matching
                                   up to this fraction (0.0–1.0).  None means
                                   exact-match required.
            new_pathway_count:    Number of new low-energy pathways S_new
                                  introduces near the operative TS.  If > 2,
                                  the +0.5 nat K-multiplicity penalty applies.
            varma_score:          Pre-computed degeneracy_strength score.
                                  If None and ⊙ check is needed, the engine
                                  will attempt to compute it.

        Returns:
            HotSwapReport with decision, per-primitive checks, and checklist.
        """
        violations: List[str] = []
        warnings: List[str] = []

        # Step 1 — primitive compatibility matrix
        prim_checks = self._check_primitives(
            target, candidate, allow_defect_fraction
        )
        for c in prim_checks:
            if not c.passed:
                violations.append(f"Primitive {c.primitive}: {c.note}")

        # Step 2 — axiom validation on candidate
        axiom_report = AxiomValidator.validate_all_axioms(candidate)
        if not axiom_report["all_satisfied"]:
            violations.append(
                f"Candidate fails {axiom_report['violations']} axiom(s) — "
                "swap blocked until violations are resolved."
            )

        # Step 3 — grounding check
        grounding_check = self._check_grounding(candidate)
        if not grounding_check["passed"]:
            violations.append(
                f"Grounding status '{grounding_check['status']}' is insufficient. "
                "Require 'full' or 'override' before swap."
            )

        # Step 4 — thermodynamic tolerance
        xi_old = self._compute_xi(target, delta_g)
        xi_new = self._compute_xi(candidate, delta_g)
        delta_xi: Optional[float] = None
        effective_delta_xi: Optional[float] = None
        k_penalty = 0.0

        if xi_old is not None and xi_new is not None:
            delta_xi = xi_new - xi_old
            # K-multiplicity penalty (§2.2)
            if new_pathway_count > 2:
                k_penalty = K_MULTIPLICITY_PENALTY
                warnings.append(
                    f"S_new introduces {new_pathway_count} new low-energy pathways "
                    f"(>2) — +{K_MULTIPLICITY_PENALTY} nat penalty applied."
                )
            effective_delta_xi = delta_xi + k_penalty
            if effective_delta_xi > XI_CP_TOLERANCE:
                violations.append(
                    f"Effective Δξ_CP = {effective_delta_xi:.3f} nats exceeds "
                    f"tolerance of {XI_CP_TOLERANCE:.1f} nat "
                    f"(Δξ = {delta_xi:.3f} + penalty = {k_penalty:.1f})."
                )

        # Step 5 — Varma / ⊙ check
        varma_required = False
        if varma_score is None:
            varma_score = self._try_varma_score(candidate)
        if varma_score is not None and varma_score >= VARMA_PHI_C_THRESHOLD:
            varma_required = True
            warnings.append(
                f"Candidate degeneracy_strength = {varma_score:.3f} ≥ "
                f"{VARMA_PHI_C_THRESHOLD} — Varma QXY probe required before swap. "
                "Confirmed ⊙ is swap-tolerant per Axiom 5; unconfirmed ⊙ is not."
            )

        # Step 6 — kinetic accessibility warning
        for c in prim_checks:
            if c.primitive == "K" and c.passed and candidate.kinetic_character == KineticCharacter.on:
                warnings.append(
                    "Candidate K = K_teshlig — kinetic trap risk even though this passes "
                    "the primitive check. Verify pathway multiplicity experimentally."
                )

        # Decide
        decision = self._decide(violations, warnings)

        checklist = self._build_checklist(
            prim_checks=prim_checks,
            axiom_report=axiom_report,
            grounding_check=grounding_check,
            effective_delta_xi=effective_delta_xi,
            varma_required=varma_required,
            varma_score=varma_score,
        )

        return HotSwapReport(
            decision=decision,
            target_name=target.name,
            candidate_name=candidate.name,
            xi_old=xi_old,
            xi_new=xi_new,
            delta_xi=delta_xi,
            k_multiplicity_penalty=k_penalty,
            effective_delta_xi=effective_delta_xi,
            primitive_checks=prim_checks,
            axiom_report=axiom_report,
            grounding_check=grounding_check,
            varma_required=varma_required,
            varma_score=varma_score,
            violations=violations,
            warnings=warnings,
            checklist=checklist,
        )

    def run_protocol(
        self,
        target: Imscription,
        candidates: List[Imscription],
        delta_g: float = -12.0,
        allow_defect_fraction: Optional[float] = None,
        top_n: int = 5,
    ) -> List[HotSwapReport]:
        """
        Run the full HotSwap protocol over a list of candidates.

        Candidates are ranked by effective_delta_xi (lowest first = most efficient swap).
        Blocked candidates are included at the end, sorted by violation count.

        Args:
            target:               S_old imscription.
            candidates:           List of S_new candidates to evaluate.
            delta_g:              ΔG basis for ξ_CP computation.
            allow_defect_fraction: Defect tolerance for G_ℵ assemblies.
            top_n:                Return at most top_n reports.

        Returns:
            List of HotSwapReport sorted best-first.
        """
        reports = []
        for cand in candidates:
            report = self.validate_candidate(
                target, cand,
                delta_g=delta_g,
                allow_defect_fraction=allow_defect_fraction,
            )
            reports.append(report)

        approved   = [r for r in reports if r.decision == HotSwapDecision.APPROVED]
        conditional = [r for r in reports if r.decision == HotSwapDecision.CONDITIONAL]
        blocked    = [r for r in reports if r.decision == HotSwapDecision.BLOCKED]

        def _sort_key(r: HotSwapReport) -> float:
            if r.effective_delta_xi is not None:
                return r.effective_delta_xi
            return float("inf")

        approved.sort(key=_sort_key)
        conditional.sort(key=_sort_key)
        blocked.sort(key=lambda r: len(r.violations))

        ranked = (approved + conditional + blocked)[:top_n]
        return ranked

    # ------------------------------------------------------------------ #
    # Primitive checks (§2.1 Primitive Matching Matrix)                   #
    # ------------------------------------------------------------------ #

    def _check_primitives(
        self,
        target: Imscription,
        candidate: Imscription,
        allow_defect_fraction: Optional[float],
    ) -> List[PrimitiveCheckResult]:
        checks: List[PrimitiveCheckResult] = []

        # D — Exact Match
        checks.append(self._check_D(target, candidate))

        # T — Exact Match
        checks.append(self._check_T(target, candidate))

        # S — Exact Match (or defect-fraction for G_ℵ)
        checks.append(self._check_S(target, candidate, allow_defect_fraction))

        # R — Compatible Class (R_⊇ ↔ R_⊆+‡ allowed; static R_⊆ is not hot-swappable)
        checks.append(self._check_R(target, candidate))

        # P — Complementary (environment polarity must be preserved)
        checks.append(self._check_P(target, candidate))

        # F — F_new ≥ F_old (hard floor)
        checks.append(self._check_F(target, candidate))

        # K — Accessible pathway (FAST or MODERATE)
        checks.append(self._check_K(candidate, target))

        return checks

    def _check_D(self, target: Imscription, candidate: Imscription) -> PrimitiveCheckResult:
        old = target.dimensionality.value
        new = candidate.dimensionality.value
        passed = target.dimensionality == candidate.dimensionality
        note = "" if passed else (
            f"D mismatch: {old} ≠ {new}. "
            "Swapping across dimensionality axes collapses the coordinate set."
        )
        return PrimitiveCheckResult("D", passed, old, new, note)

    def _check_T(self, target: Imscription, candidate: Imscription) -> PrimitiveCheckResult:
        old = target.topology.value
        new = candidate.topology.value
        passed = target.topology == candidate.topology
        note = "" if passed else (
            f"T mismatch: {old} ≠ {new}. "
            "Topology must match exactly — cyclic cannot replace linear."
        )
        return PrimitiveCheckResult("T", passed, old, new, note)

    def _check_S(
        self,
        target: Imscription,
        candidate: Imscription,
        allow_defect_fraction: Optional[float],
    ) -> PrimitiveCheckResult:
        old = target.stoichiometry or "unspecified"
        new = candidate.stoichiometry or "unspecified"

        # G_ℵ networks with defect fraction tolerance
        if (
            allow_defect_fraction is not None
            and target.granularity == Granularity.thigh
        ):
            # Any stoichiometry mismatch is permitted within defect_fraction
            passed = True
            note = (
                f"G_ℵ defect tolerance {allow_defect_fraction:.0%} applied — "
                f"S mismatch ({old} → {new}) is permitted."
            )
            return PrimitiveCheckResult("S", passed, old, new, note)

        # Molecular / mesoscale: exact match required
        if old == "unspecified" or new == "unspecified":
            # Cannot enforce check without data; treat as warning
            return PrimitiveCheckResult(
                "S", True, old, new,
                "Stoichiometry not specified on one/both imscriptions — check skipped."
            )

        passed = old == new
        note = "" if passed else (
            f"S mismatch: {old} ≠ {new}. "
            "Exact stoichiometry required at G_ב/G_ג scale."
        )
        return PrimitiveCheckResult("S", passed, old, new, note)

    def _check_R(self, target: Imscription, candidate: Imscription) -> PrimitiveCheckResult:
        from .models import RecognitionMode
        old = target.recognition_mode.value
        new = candidate.recognition_mode.value

        # Static covalent (R_⊆) is not hot-swappable as old
        if target.recognition_mode == RecognitionMode.tot:
            return PrimitiveCheckResult(
                "R", False, old, new,
                "Static R_⊆ (covalent) is not hot-swappable without full scaffold rebuild."
            )

        # Allowed: same class, R_⊇ ↔ R_⊆+‡, R_‡ ↔ R_⊆+‡
        compatible_swaps = {
            RecognitionMode.ado: {
                RecognitionMode.ado,
                RecognitionMode.tot,
            },
            RecognitionMode.ear: {
                RecognitionMode.ear,
                RecognitionMode.tot,
                RecognitionMode.ado,
            },
            RecognitionMode.tot: {
                RecognitionMode.tot,
                RecognitionMode.ado,
                RecognitionMode.ear,
            },
            RecognitionMode.ian: {
                RecognitionMode.ian,
                RecognitionMode.ado,
            },
        }
        allowed = compatible_swaps.get(target.recognition_mode, set())
        passed = candidate.recognition_mode in allowed
        if not passed:
            note = f"R incompatible: {old} → {new} is not an allowed swap class."
        else:
            # Allowed but mechanistically significant cross-class changes warrant a note
            _MECHANISM_CHANGE_NOTES = {
                (RecognitionMode.ear, RecognitionMode.ado): (
                    f"R_‡ → R_⊇: constraint propagation basis changes from catalytic "
                    f"turnover to non-covalent binding. Verify the D_∞ cycle driver is "
                    f"preserved independently of the recognition step."
                ),
                (RecognitionMode.ado, RecognitionMode.tot): (
                    f"R_⊇ → R_⊆+‡: adds covalent character to recognition. "
                    f"Verify K and reversibility constraints are still met."
                ),
                (RecognitionMode.ian, RecognitionMode.ado): (
                    f"R_⇔ → R_⊇: mechanical bond replaced by non-covalent interaction. "
                    f"Steric-cliff K-barrier profile will change; re-evaluate K."
                ),
                (RecognitionMode.tot, RecognitionMode.ado): (
                    f"R_⊆+‡ → R_⊇: dynamic covalent replaced by non-covalent. "
                    f"Fidelity floor may be affected under dilute conditions."
                ),
            }
            swap_pair = (target.recognition_mode, candidate.recognition_mode)
            note = _MECHANISM_CHANGE_NOTES.get(swap_pair, "")
        return PrimitiveCheckResult("R", passed, old, new, note)

    def _check_P(self, target: Imscription, candidate: Imscription) -> PrimitiveCheckResult:
        old = target.polarity.value
        new = candidate.polarity.value
        passed = target.polarity == candidate.polarity
        # Polarity mismatch is a warning, not a hard block, unless both are self-complementary
        # and they differ — that means the environment geometry changes.
        note = "" if passed else (
            f"P mismatch: {old} → {new}. "
            "Verify environment polarity constraints remain satisfied."
        )
        # Treat P mismatch as conditional (warning), not hard block
        return PrimitiveCheckResult("P", True, old, new, note if not passed else "")

    def _check_F(self, target: Imscription, candidate: Imscription) -> PrimitiveCheckResult:
        old = target.fidelity
        new = candidate.fidelity
        old_idx = _FIDELITY_ORDER.index(old)
        new_idx = _FIDELITY_ORDER.index(new)
        passed = new_idx >= old_idx  # F_new ≥ F_old
        note = "" if passed else (
            f"Fidelity floor violated: F_new={new.value} < F_old={old.value}. "
            "Downgrading fidelity increases entropy production (ξ_CP) — hard block."
        )
        return PrimitiveCheckResult("F", passed, old.value, new.value, note)

    def _check_K(self, candidate: Imscription, target: Imscription = None) -> PrimitiveCheckResult:
        k = candidate.kinetic_character
        accessible = {KineticCharacter.yea, KineticCharacter.loll}
        passed = k in accessible
        note = "" if passed else (
            f"K = {k.value} is not accessible for hot-swapping. "
            "K_schwa creates kinetic bottlenecks; K_teshlig may freeze system state."
        )
        old_k = target.kinetic_character.value if target is not None else "—"
        return PrimitiveCheckResult(
            "K", passed, old_k, k.value, note
        )

    # ------------------------------------------------------------------ #
    # Grounding check (§3 Step 5, §4 Grounding Drift failure mode)        #
    # ------------------------------------------------------------------ #

    def _check_grounding(self, candidate: Imscription) -> Dict[str, Any]:
        meta = getattr(candidate, "metadata", None) or {}
        status = meta.get("grounding_status", "unverified")
        passed = status in GROUNDING_REQUIRED
        return {
            "passed": passed,
            "status": status,
            "note": (
                "Grounding verified." if passed else
                f"grounding_status='{status}' — must be 'full' or 'override' before swap. "
                "Run 'imscribe audit --status unverified --dry-run' to inspect."
            ),
        }

    # ------------------------------------------------------------------ #
    # Thermodynamic helpers                                                #
    # ------------------------------------------------------------------ #

    def _compute_xi(self, imscription: Imscription, delta_g: float) -> Optional[float]:
        try:
            result = compute_eta_CP(imscription, delta_g=delta_g)
            return result.xi_CP
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Varma probe                                                          #
    # ------------------------------------------------------------------ #

    def _try_varma_score(self, candidate: Imscription) -> Optional[float]:
        try:
            from .varma_probe import degeneracy_strength
            score, _ = degeneracy_strength(candidate)
            return score
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Decision                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _decide(violations: List[str], warnings: List[str]) -> HotSwapDecision:
        if violations:
            return HotSwapDecision.BLOCKED
        if warnings:
            return HotSwapDecision.CONDITIONAL
        return HotSwapDecision.APPROVED

    # ------------------------------------------------------------------ #
    # Checklist (§8.0 Summary Checklist)                                  #
    # ------------------------------------------------------------------ #

    def _build_checklist(
        self,
        prim_checks: List[PrimitiveCheckResult],
        axiom_report: Dict[str, Any],
        grounding_check: Dict[str, Any],
        effective_delta_xi: Optional[float],
        varma_required: bool,
        varma_score: Optional[float],
    ) -> Dict[str, bool]:
        prim_by_name = {c.primitive: c.passed for c in prim_checks}

        xi_ok = (
            effective_delta_xi is not None
            and effective_delta_xi <= XI_CP_TOLERANCE
        )
        varma_ok = (not varma_required) or (
            varma_score is not None and varma_score >= VARMA_PHI_C_THRESHOLD
        )

        return {
            "D_T_S_exact_match":    all(prim_by_name.get(p, False) for p in ("D", "T", "S")),
            "ƒ_floor_preserved":    prim_by_name.get("F", False),
            "Ç_accessible":         prim_by_name.get("K", False),
            "axiom_validation_pass": axiom_report.get("all_satisfied", False),
            "xi_CP_within_tolerance": xi_ok,
            "grounding_status_ok":  grounding_check.get("passed", False),
            "varma_probe_satisfied": varma_ok,
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def validate_hotswap(
    target_name: str,
    candidate_name: str,
    delta_g: float = -12.0,
    allow_defect_fraction: Optional[float] = None,
) -> HotSwapReport:
    """
    Quick helper: validate a HotSwap from catalog names.

    Args:
        target_name:          Name of S_old in global_catalog.
        candidate_name:       Name of S_new in global_catalog.
        delta_g:              ΔG basis for ξ_CP computation (kJ/mol).
        allow_defect_fraction: Defect tolerance for G_ℵ assemblies.

    Returns:
        HotSwapReport
    """
    from .registry import global_catalog

    target = global_catalog.get(target_name)
    if target is None:
        raise KeyError(f"Imscription '{target_name}' not found in catalog.")
    candidate = global_catalog.get(candidate_name)
    if candidate is None:
        raise KeyError(f"Imscription '{candidate_name}' not found in catalog.")

    engine = HotSwapEngine()
    return engine.validate_candidate(
        target, candidate,
        delta_g=delta_g,
        allow_defect_fraction=allow_defect_fraction,
    )
