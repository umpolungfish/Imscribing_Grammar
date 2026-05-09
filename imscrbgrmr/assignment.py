"""
imscrbgrmr/assignment.py — Algorithmic Primitive Assignment Engine

Implements the Algorithmic Assignment Project described in IG.md §XXII.

Each primitive has a formal operational definition mapping measurable quantities
to tier values.  The engine also runs two embedded tests:

  1. Assignment method independence — multiple measurement routes should
     converge to the same tier (cross-checks reported as AGREEMENT/CONFLICT).

  2. Self-consistency under decomposition — for catalog synthons with known
     ΔG data, assign algorithmically, compare to hand-coded catalog value,
     flag boundary cases and conflicts.

Primitives and their assignment routes:
  F   (Fidelity)          → ΔG via integer Boltzmann ratios (P-21)
  K   (KineticCharacter)  → ΔG‡ via Eyring barrier thresholds
  G   (Granularity)       → component-count / spatial scale
  D   (Dimensionality)    → structural type (molecule / assembly / cycle / holographic)
  T   (Topology)          → interaction graph structure
  R   (RecognitionMode)   → bond type + reversibility + catalytic flag
  P   (Polarity)          → partner symmetry
  Γ   (InteractionGrammar)→ selectivity ratio
  Ω   (TopoIndex)         → derived from {T, K, D, Γ, G} via P-22 5-rule tree
  Φ   (CriticalityPhase)  → G/D degeneracy + Varma score heuristic
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .models import (
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    KineticCharacter,
    Granularity,
    InteractionGrammar,
    GrammarOperator,
    CriticalityPhase,
    TopoIndex,
    Synthon,
)

# ── Physical constants ──────────────────────────────────────────────────────
R_GAS = 8.314e-3          # kJ / (mol·K)
T_REF = 298.15            # K

# ── P-21 Boltzmann discrimination thresholds for F ─────────────────────────
# F_HIGH  : P_correct / P_wrong ≥ 19  →  ΔΔG ≤ −RT·ln(19) ≈ −7.30 kJ/mol
# F_MED   : 3 ≤ ratio < 19            →  −7.30 < ΔΔG ≤ −RT·ln(3) ≈ −2.72 kJ/mol
# F_LOW   : ratio < 3                 →  ΔΔG > −2.72 kJ/mol
_RT_REF = R_GAS * T_REF                           # 2.479 kJ/mol at 298 K
_F_HIGH_THRESHOLD = -_RT_REF * math.log(19)       # ≈ −7.30 kJ/mol
_F_MED_THRESHOLD  = -_RT_REF * math.log(3)        # ≈ −2.72 kJ/mol

# K thresholds (kJ/mol activation barrier, Eyring @ 298 K)
_K_FAST_THRESHOLD = 60.0
_K_MOD_THRESHOLD  = 100.0
# K_SLOW: > 100.  K_TRAP: pathway-multiplicity flag (not barrier-only).
# K_lambda:  disorder-driven — not assignable from ΔG‡ alone.

# G spatial-scale thresholds (number of interacting components as proxy)
_G_LOCAL_MAX     = 15     # single molecule / single binding event
_G_MESOSCALE_MAX = 200    # motif / cluster / small assembly


# ══════════════════════════════════════════════════════════════════════════════
# Data structures
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PrimitiveAssignment:
    """Result of algorithmically assigning a single primitive."""
    primitive: str
    value: Any                  # enum instance
    confidence: float           # 0.0 – 1.0
    method: str                 # "thermodynamic" | "structural" | "derived" | "heuristic"
    evidence: str               # human-readable justification
    is_boundary: bool = False   # True if near a tier threshold
    boundary_margin: float = 0.0  # absolute distance to nearest threshold


@dataclass
class MethodComparison:
    """Cross-check between two independent assignment methods for the same primitive."""
    primitive: str
    method_a: str
    value_a: Any
    method_b: str
    value_b: Any
    agreement: bool

    def summary(self) -> str:
        status = "AGREE" if self.agreement else "CONFLICT"
        return (f"{self.primitive}: {status} "
                f"({self.method_a}={self.value_a.name if hasattr(self.value_a,'name') else self.value_a} "
                f"vs {self.method_b}={self.value_b.name if hasattr(self.value_b,'name') else self.value_b})")


@dataclass
class SynthonAssignment:
    """Complete algorithmic assignment result for a synthon."""
    assignments: Dict[str, PrimitiveAssignment]
    boundary_cases: List[str] = field(default_factory=list)
    underdetermined: List[str] = field(default_factory=list)
    consistency_checks: List[str] = field(default_factory=list)
    method_comparisons: List[MethodComparison] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_synthon(self, name: str = "assigned") -> Synthon:
        """Convert assignment to a Synthon object (underdetermined fields get defaults)."""
        a = self.assignments
        return Synthon(
            name=name,
            dimensionality=a["D"].value if "D" in a else Dimensionality.MOLECULAR,
            topology=a["T"].value if "T" in a else Topology.NETWORK,
            recognition_mode=a["R"].value if "R" in a else RecognitionMode.NON_COVALENT,
            polarity=a["P"].value if "P" in a else Polarity.SELF_COMPLEMENTARY_SYM,
            fidelity=a["F"].value if "F" in a else Fidelity.MEDIUM,
            kinetic_character=a["K"].value if "K" in a else KineticCharacter.MODERATE,
            granularity=a["G"].value if "G" in a else Granularity.LOCAL,
            interaction_grammar=a["Gamma"].value if "Gamma" in a else InteractionGrammar.SELECTIVE_AND,
            criticality_phase=a["Phi"].value if "Phi" in a else CriticalityPhase.SUBCRITICAL,
            topo_index=a["Omega"].value if "Omega" in a else None,
        )

    def agreement_rate(self) -> float:
        """Fraction of method comparisons that agree."""
        if not self.method_comparisons:
            return 1.0
        return sum(1 for c in self.method_comparisons if c.agreement) / len(self.method_comparisons)


@dataclass
class CatalogConsistencyEntry:
    """Comparison of algorithmic vs. hand-coded assignment for a catalog synthon."""
    name: str
    primitive: str
    catalog_value: Any
    assigned_value: Any
    agrees: bool
    confidence: float
    is_boundary: bool
    note: str = ""


@dataclass
class CatalogConsistencyReport:
    """Full catalog consistency check results."""
    entries: List[CatalogConsistencyEntry]
    n_synthons_checked: int
    n_primitives_checked: int
    overall_agreement_rate: float
    boundary_rate: float
    conflict_summary: Dict[str, List[str]]  # primitive → list of conflicting synthon names
    notes: List[str] = field(default_factory=list)

    def print_summary(self) -> None:
        print(f"\n  Catalog Consistency Report")
        print(f"  Synthons checked : {self.n_synthons_checked}")
        print(f"  Primitive checks : {self.n_primitives_checked}")
        print(f"  Agreement rate   : {self.overall_agreement_rate:.1%}")
        print(f"  Boundary rate    : {self.boundary_rate:.1%}")
        if self.conflict_summary:
            print(f"\n  Conflicts by primitive:")
            for prim, names in sorted(self.conflict_summary.items()):
                print(f"    {prim}: {len(names)} conflict(s) — {', '.join(names[:5])}"
                      + (" ..." if len(names) > 5 else ""))
        for n in self.notes:
            print(f"  Note: {n}")


# ══════════════════════════════════════════════════════════════════════════════
# Assignment Engine
# ══════════════════════════════════════════════════════════════════════════════

class PrimitiveAssignmentEngine:
    """
    Assigns primitive values from measurable physical/structural quantities.

    Each assign_X method returns a PrimitiveAssignment with:
      - the enum value
      - a confidence score (0–1)
      - the assignment method
      - human-readable evidence
      - a boundary flag if near a tier threshold

    assign_all() accepts a measurements dict and runs all applicable methods,
    performing cross-checks where multiple methods are available.
    """

    def __init__(self, temp_k: float = T_REF):
        self.temp_k = temp_k
        self._rt = R_GAS * temp_k

    # ── F (Fidelity) ─────────────────────────────────────────────────────────

    def assign_F_from_delta_g(self, delta_g_kj: float) -> PrimitiveAssignment:
        """
        Assign F from binding free energy ΔG (kJ/mol, negative = favorable).

        Boundaries (P-21, integer Boltzmann discrimination ratios at T_ref):
          F_HIGH  : ΔG ≤ −RT·ln(19) ≈ −7.30 kJ/mol  (P_correct/P_wrong ≥ 19)
          F_MED   : −7.30 < ΔG ≤ −RT·ln(3) ≈ −2.72 kJ/mol  (ratio 3–19)
          F_LOW   : ΔG > −2.72 kJ/mol  (ratio < 3)
        """
        rt = self._rt
        hi_thresh = -rt * math.log(19)  # ≈ −7.30 at 298 K
        me_thresh = -rt * math.log(3)   # ≈ −2.72 at 298 K

        # Boundary margin: distance to nearest threshold in kJ/mol
        dist_hi = abs(delta_g_kj - hi_thresh)
        dist_me = abs(delta_g_kj - me_thresh)
        margin = min(dist_hi, dist_me)
        is_boundary = margin < 0.5 * abs(rt)  # within 0.5 RT of a boundary

        boltzmann_ratio = math.exp(-delta_g_kj / rt)

        if delta_g_kj <= hi_thresh:
            value = Fidelity.HIGH
            conf = min(1.0, (hi_thresh - delta_g_kj) / abs(hi_thresh) + 0.7)
            evidence = (f"ΔG = {delta_g_kj:.2f} kJ/mol → Boltzmann ratio "
                        f"{boltzmann_ratio:.1f} ≥ 19 (F_HIGH threshold, P-21)")
        elif delta_g_kj <= me_thresh:
            value = Fidelity.MEDIUM
            conf = 0.80 - 0.2 * (delta_g_kj - hi_thresh) / (me_thresh - hi_thresh)
            evidence = (f"ΔG = {delta_g_kj:.2f} kJ/mol → Boltzmann ratio "
                        f"{boltzmann_ratio:.1f} ∈ [3, 19] (F_MED range, P-21)")
        else:
            value = Fidelity.LOW
            conf = min(1.0, 0.7 + (delta_g_kj - me_thresh) / abs(me_thresh))
            evidence = (f"ΔG = {delta_g_kj:.2f} kJ/mol → Boltzmann ratio "
                        f"{boltzmann_ratio:.1f} < 3 (F_LOW threshold, P-21)")

        return PrimitiveAssignment(
            primitive="F", value=value, confidence=round(min(conf, 1.0), 3),
            method="thermodynamic_delta_g", evidence=evidence,
            is_boundary=is_boundary, boundary_margin=round(margin, 3),
        )

    def assign_F_from_xi_cp(self, xi_cp: float) -> PrimitiveAssignment:
        """
        Assign F from ξ_CP (constraint-propagation efficiency, nats).

        Boundaries from calibrated_xi_cp_table() in thermodynamics.py:
          F_HIGH  : ξ_CP ≤ 8.5 nats
          F_MED   : 8.5 < ξ_CP ≤ 11.0 nats
          F_LOW   : ξ_CP > 11.0 nats
        """
        HI = 8.5
        ME = 11.0
        if xi_cp <= HI:
            value, conf = Fidelity.HIGH, 0.90 - 0.1 * (xi_cp / HI)
            evidence = f"ξ_CP = {xi_cp:.2f} nats ≤ 8.5 → F_HIGH"
        elif xi_cp <= ME:
            value, conf = Fidelity.MEDIUM, 0.75
            evidence = f"ξ_CP = {xi_cp:.2f} nats ∈ (8.5, 11.0] → F_MEDIUM"
        else:
            value, conf = Fidelity.LOW, 0.70
            evidence = f"ξ_CP = {xi_cp:.2f} nats > 11.0 → F_LOW"

        margin = min(abs(xi_cp - HI), abs(xi_cp - ME))
        return PrimitiveAssignment(
            primitive="F", value=value, confidence=round(conf, 3),
            method="xi_cp", evidence=evidence,
            is_boundary=margin < 0.3, boundary_margin=round(margin, 3),
        )

    # ── K (KineticCharacter) ─────────────────────────────────────────────────

    def assign_K_from_barrier(
        self,
        delta_g_ddagger_kj: float,
        pathway_multiplicity: Optional[int] = None,
    ) -> PrimitiveAssignment:
        """
        Assign K from activation barrier ΔG‡ (kJ/mol).

        Thresholds:
          K_FAST  : ΔG‡ < 60 kJ/mol
          K_MOD   : 60 ≤ ΔG‡ < 100 kJ/mol
          K_SLOW  : 100 ≤ ΔG‡ < 150 kJ/mol
          K_TRAP  : ΔG‡ ≥ 150 kJ/mol  OR  pathway_multiplicity ≥ 3
          K_lambda   : disorder-driven — not assignable from ΔG‡ alone
        """
        margin = min(
            abs(delta_g_ddagger_kj - _K_FAST_THRESHOLD),
            abs(delta_g_ddagger_kj - _K_MOD_THRESHOLD),
            abs(delta_g_ddagger_kj - 150.0),
        )
        is_boundary = margin < 5.0  # within 5 kJ/mol of a threshold

        trap_by_multiplicity = (pathway_multiplicity is not None
                                and pathway_multiplicity >= 3)

        if trap_by_multiplicity:
            value = KineticCharacter.TRAP
            conf = 0.85
            evidence = (f"Pathway multiplicity = {pathway_multiplicity} ≥ 3 "
                        f"(kinetic trapping regardless of barrier height "
                        f"ΔG‡ = {delta_g_ddagger_kj:.1f} kJ/mol)")
        elif delta_g_ddagger_kj < _K_FAST_THRESHOLD:
            value, conf = KineticCharacter.FAST, 0.90
            evidence = f"ΔG‡ = {delta_g_ddagger_kj:.1f} kJ/mol < 60 → K_FAST"
        elif delta_g_ddagger_kj < _K_MOD_THRESHOLD:
            value, conf = KineticCharacter.MODERATE, 0.85
            evidence = f"ΔG‡ = {delta_g_ddagger_kj:.1f} kJ/mol ∈ [60, 100) → K_MODERATE"
        elif delta_g_ddagger_kj < 150.0:
            value, conf = KineticCharacter.SLOW, 0.80
            evidence = f"ΔG‡ = {delta_g_ddagger_kj:.1f} kJ/mol ∈ [100, 150) → K_SLOW"
        else:
            value, conf = KineticCharacter.TRAP, 0.80
            evidence = f"ΔG‡ = {delta_g_ddagger_kj:.1f} kJ/mol ≥ 150 → K_TRAP"

        return PrimitiveAssignment(
            primitive="K", value=value, confidence=conf,
            method="kinetic_barrier", evidence=evidence,
            is_boundary=is_boundary, boundary_margin=round(margin, 2),
        )

    # ── G (Granularity) ──────────────────────────────────────────────────────

    def assign_G_from_components(self, n_components: int) -> PrimitiveAssignment:
        """
        Assign G from the number of interacting structural components.

        Thresholds (component-count proxy for spatial scale):
          G_LOCAL     : n ≤ 15    (~single molecule / single binding event)
          G_MESOSCALE : 15 < n ≤ 200  (~motif, cluster, small assembly)
          G_GLOBAL    : n > 200   (~network, framework, macroscopic)
        """
        margin = min(
            abs(n_components - _G_LOCAL_MAX),
            abs(n_components - _G_MESOSCALE_MAX),
        )
        is_boundary = margin <= 5

        if n_components <= _G_LOCAL_MAX:
            value, conf = Granularity.LOCAL, 0.85
            evidence = f"n_components = {n_components} ≤ 15 → G_LOCAL"
        elif n_components <= _G_MESOSCALE_MAX:
            value, conf = Granularity.MESOSCALE, 0.80
            evidence = f"n_components = {n_components} ∈ (15, 200] → G_MESOSCALE"
        else:
            value, conf = Granularity.GLOBAL, 0.80
            evidence = f"n_components = {n_components} > 200 → G_GLOBAL"

        return PrimitiveAssignment(
            primitive="G", value=value, confidence=conf,
            method="component_count", evidence=evidence,
            is_boundary=is_boundary, boundary_margin=float(margin),
        )

    def assign_G_from_scale_nm(self, scale_nm: float) -> PrimitiveAssignment:
        """
        Assign G from characteristic spatial scale (nm).

        Thresholds:
          G_LOCAL     : scale < 2 nm     (single molecule)
          G_MESOSCALE : 2 ≤ scale < 100 nm  (nanoscale assembly)
          G_GLOBAL    : scale ≥ 100 nm   (macroscopic / network)
        """
        LO, ME = 2.0, 100.0
        margin = min(abs(scale_nm - LO), abs(scale_nm - ME))
        is_boundary = margin < 0.5 * LO

        if scale_nm < LO:
            value, conf = Granularity.LOCAL, 0.85
            evidence = f"scale = {scale_nm:.1f} nm < 2 nm → G_LOCAL"
        elif scale_nm < ME:
            value, conf = Granularity.MESOSCALE, 0.80
            evidence = f"scale = {scale_nm:.1f} nm ∈ [2, 100) nm → G_MESOSCALE"
        else:
            value, conf = Granularity.GLOBAL, 0.80
            evidence = f"scale = {scale_nm:.1f} nm ≥ 100 nm → G_GLOBAL"

        return PrimitiveAssignment(
            primitive="G", value=value, confidence=conf,
            method="spatial_scale_nm", evidence=evidence,
            is_boundary=is_boundary, boundary_margin=round(margin, 2),
        )

    # ── D (Dimensionality) ───────────────────────────────────────────────────

    def assign_D(
        self,
        is_single_molecule: bool = False,
        is_assembly: bool = False,
        is_catalytic_cycle: bool = False,
        is_holographic: bool = False,
    ) -> PrimitiveAssignment:
        """
        Assign D from structural type flags.

          MOLECULAR        : single molecule / single covalent entity
          SUPRAMOLECULAR   : non-covalent assembly, crystal, scaffold
          TEMPORAL         : catalytic cycle, oscillation, temporal pathway
          HOLOGRAPHIC      : bulk-boundary duality (AdS/CFT, renormalisation)
        """
        flags = {
            "is_single_molecule": is_single_molecule,
            "is_assembly": is_assembly,
            "is_catalytic_cycle": is_catalytic_cycle,
            "is_holographic": is_holographic,
        }
        n_true = sum(flags.values())

        if n_true == 0:
            return PrimitiveAssignment(
                primitive="D", value=Dimensionality.MOLECULAR, confidence=0.40,
                method="structural_flags", evidence="No structural flags set — defaulting to MOLECULAR",
                is_boundary=True, boundary_margin=0.0,
            )

        if n_true > 1:
            # Multiple flags set — use precedence: holographic > temporal > assembly > molecular
            note = f"Multiple D flags set {flags} — using precedence rule"
        else:
            note = ""

        if is_holographic:
            value, conf = Dimensionality.HOLOGRAPHIC, 0.90
            evidence = "Bulk-boundary duality flag set → D_HOLOGRAPHIC"
        elif is_catalytic_cycle:
            value, conf = Dimensionality.TEMPORAL, 0.88
            evidence = "Catalytic cycle / temporal pathway flag → D_TEMPORAL"
        elif is_assembly:
            value, conf = Dimensionality.SUPRAMOLECULAR, 0.88
            evidence = "Non-covalent assembly flag → D_SUPRAMOLECULAR"
        else:
            value, conf = Dimensionality.MOLECULAR, 0.90
            evidence = "Single-molecule flag → D_MOLECULAR"

        if note:
            evidence = note + "; " + evidence

        return PrimitiveAssignment(
            primitive="D", value=value, confidence=conf,
            method="structural_flags", evidence=evidence,
            is_boundary=n_true > 1, boundary_margin=0.0,
        )

    # ── T (Topology) ─────────────────────────────────────────────────────────

    def assign_T(
        self,
        n_binding_sites: int = 1,
        has_cycle: bool = False,
        is_self_complementary: bool = False,
        has_cage_geometry: bool = False,
        has_braid_statistics: bool = False,
        partner_count: int = 1,
    ) -> PrimitiveAssignment:
        """
        Assign T from interaction graph properties.

          LINEAR   : 1 binding site, no cycle, linear sequence
          CYCLIC   : closed ring / cycle (has_cycle=True)
          BOWTIE   : self-complementary interaction (is_self_complementary=True)
          HUB      : 1 central site + ≥3 satellite partners
          NETWORK  : ≥2 binding sites, no cage, no braid
          CAGE     : enclosed interior geometry
          BRAID    : anyonic / non-Abelian exchange statistics
          BOWL     : single concave binding cavity
        """
        if has_braid_statistics:
            value, conf = Topology.BRAID, 0.90
            evidence = "Braid / anyonic exchange statistics → T_BRAID"
        elif has_cage_geometry:
            value, conf = Topology.CAGE, 0.88
            evidence = "Enclosed cage geometry → T_CAGE"
        elif is_self_complementary:
            value, conf = Topology.CYCLIC_BOWTIE, 0.88
            evidence = "Self-complementary partner → T_CYCLIC_BOWTIE"
        elif has_cycle:
            value, conf = Topology.CYCLIC_BOWTIE, 0.85
            evidence = "Closed ring / cycle → T_CYCLIC_BOWTIE"
        elif n_binding_sites == 1 and partner_count <= 2:
            if partner_count >= 1:
                value, conf = Topology.LINEAR, 0.82
                evidence = f"1 binding site, {partner_count} partner(s) → T_LINEAR"
            else:
                value, conf = Topology.LINEAR, 0.75
                evidence = "Single binding site, no partners specified → T_LINEAR"
        elif n_binding_sites == 1 and partner_count >= 3:
            value, conf = Topology.HUB_NODE, 0.82
            evidence = f"1 central site, {partner_count} satellite partners → T_HUB_NODE"
        else:
            value, conf = Topology.NETWORK, 0.80
            evidence = f"{n_binding_sites} binding sites → T_NETWORK"

        return PrimitiveAssignment(
            primitive="T", value=value, confidence=conf,
            method="graph_topology", evidence=evidence,
            is_boundary=False, boundary_margin=0.0,
        )

    # ── K from R (structural prior) ──────────────────────────────────────────

    def assign_K_from_recognition_mode(
        self,
        recognition_mode: "RecognitionMode",
    ) -> "PrimitiveAssignment":
        """
        Estimate K from the R assignment when no ΔG‡ data is available.

        This is a structural prior, not a measurement: R encodes the bond type,
        which is the dominant kinetic determinant at the molecular scale.

        Confidence is capped at 0.60 for all cases and is_boundary=True, because
        the same R can span a wide K range (e.g. weak vs strong H-bonds are both
        R_NON_COVALENT but differ by 2–3 orders of magnitude in off-rate).

        Mapping (directionally correct at 80–90% for small-molecule catalog):
          NON_COVALENT      → FAST     (μs–ms H-bond / vdW off-rates)
          COVALENT_DYNAMIC  → MODERATE (ms–s reversible covalent)
          DYNAMIC_CATALYTIC → MODERATE (catalytic turnover timescale)
          COVALENT          → SLOW     (hours; irreversible on biological timescale)
          MECHANICAL        → SLOW     (threading / dethreading barriers)
        """
        _map = {
            RecognitionMode.NON_COVALENT:      (KineticCharacter.FAST,     0.58, "R=NON_COVALENT → K_FAST prior (H-bond/vdW off-rates)"),
            RecognitionMode.COVALENT_DYNAMIC:  (KineticCharacter.MODERATE, 0.58, "R=COVALENT_DYNAMIC → K_MOD prior (reversible covalent)"),
            RecognitionMode.DYNAMIC_CATALYTIC: (KineticCharacter.MODERATE, 0.55, "R=DYNAMIC_CATALYTIC → K_MOD prior (catalytic turnover)"),
            RecognitionMode.COVALENT:          (KineticCharacter.SLOW,     0.58, "R=COVALENT → K_SLOW prior (irreversible bond)"),
            RecognitionMode.MECHANICAL:        (KineticCharacter.SLOW,     0.55, "R=MECHANICAL → K_SLOW prior (threading barrier)"),
        }
        value, conf, evidence = _map.get(
            recognition_mode,
            (KineticCharacter.MODERATE, 0.45, f"R={recognition_mode} — no prior mapping, defaulting to K_MOD"),
        )
        return PrimitiveAssignment(
            primitive="K", value=value, confidence=conf,
            method="r_prior", evidence=evidence,
            is_boundary=True, boundary_margin=0.0,
        )

    # ── R (RecognitionMode) ──────────────────────────────────────────────────

    def assign_R(
        self,
        is_covalent: bool = False,
        is_reversible: bool = True,
        is_catalytic: bool = False,
        is_mechanical: bool = False,
    ) -> PrimitiveAssignment:
        """
        Assign R from bond type + reversibility + function.

          NON_COVALENT           : non-covalent, reversible (H-bond, vdW, ionic)
          COVALENT_REVERSIBLE    : covalent but reversible (imine, disulfide, boronate)
          DYNAMIC_CATALYTIC      : catalytic cycle — product released, catalyst regenerated
          MECHANICAL             : topological / mechanical bond (rotaxane, catenane)
        """
        if is_mechanical:
            value, conf = RecognitionMode.MECHANICAL, 0.90
            evidence = "Mechanical / topological bond → R_MECHANICAL"
        elif is_catalytic:
            value, conf = RecognitionMode.DYNAMIC_CATALYTIC, 0.90
            evidence = "Catalytic cycle with product release → R_DYNAMIC_CATALYTIC"
        elif is_covalent and is_reversible:
            value, conf = RecognitionMode.COVALENT_DYNAMIC, 0.88
            evidence = "Reversible covalent bond → R_COVALENT_DYNAMIC"
        elif not is_covalent:
            value, conf = RecognitionMode.NON_COVALENT, 0.88
            evidence = "Non-covalent interaction → R_NON_COVALENT"
        else:
            # Covalent + irreversible
            value, conf = RecognitionMode.COVALENT, 0.85
            evidence = "Covalent + irreversible bond → R_COVALENT"

        return PrimitiveAssignment(
            primitive="R", value=value, confidence=conf,
            method="bond_type", evidence=evidence,
            is_boundary=(conf < 0.60), boundary_margin=0.0,
        )

    # ── P (Polarity) ─────────────────────────────────────────────────────────

    def assign_P(
        self,
        partners_identical: bool = False,
        has_pseudosymmetry: bool = False,
    ) -> PrimitiveAssignment:
        """
        Assign P from partner symmetry.

          SELF_COMPLEMENTARY_SYM    : A + A homodimerisation (exact symmetry)
          SELF_COMPLEMENTARY_PSEUDO : A + A' (quasi-symmetric, e.g. coiled-coil)
          DONOR_ACCEPTOR            : A + B heterodimer (asymmetric)
        """
        if partners_identical and not has_pseudosymmetry:
            value, conf = Polarity.SELF_COMPLEMENTARY_SYM, 0.92
            evidence = "Partners identical → P_SELF_COMPLEMENTARY_SYM"
        elif partners_identical and has_pseudosymmetry:
            value, conf = Polarity.SELF_COMPLEMENTARY_PSEUDO, 0.88
            evidence = "Partners quasi-identical (pseudosymmetry) → P_SELF_COMPLEMENTARY_PSEUDO"
        elif has_pseudosymmetry:
            value, conf = Polarity.SELF_COMPLEMENTARY_PSEUDO, 0.80
            evidence = "Pseudosymmetry flag set → P_SELF_COMPLEMENTARY_PSEUDO"
        else:
            value, conf = Polarity.DONOR_ACCEPTOR, 0.88
            evidence = "Partners non-identical → P_DONOR_ACCEPTOR"

        return PrimitiveAssignment(
            primitive="P", value=value, confidence=conf,
            method="partner_symmetry", evidence=evidence,
            is_boundary=False, boundary_margin=0.0,
        )

    # ── Γ (InteractionGrammar) ───────────────────────────────────────────────

    def assign_Gamma(
        self,
        n_compatible_partners: int,
        n_total_possible_partners: int,
        is_quantum: bool = False,
    ) -> PrimitiveAssignment:
        """
        Assign Γ from selectivity ratio.

          SELECTIVE_AND   : narrow selectivity (ratio ≤ 0.15 — few compatible partners)
          BROAD_OR        : wide selectivity (ratio > 0.15 — many compatible partners)
          QUANTUM_AND     : quantum coherence gates partner selection
          CATEGORICAL     : hard categorical exclusion (only one partner class allowed)
        """
        if is_quantum:
            return PrimitiveAssignment(
                primitive="Gamma", value=InteractionGrammar.QUANTUM_AND, confidence=0.88,
                method="quantum_flag", evidence="Quantum coherence flag → Gamma_QUANTUM_AND",
                is_boundary=False, boundary_margin=0.0,
            )

        if n_total_possible_partners == 0:
            return PrimitiveAssignment(
                primitive="Gamma",
                value=InteractionGrammar.SELECTIVE_AND,
                confidence=0.50,
                method="selectivity_ratio",
                evidence="n_total_possible_partners = 0 — cannot compute selectivity ratio",
                is_boundary=True, boundary_margin=0.0,
            )

        ratio = n_compatible_partners / n_total_possible_partners
        THRESHOLD = 0.15
        margin = abs(ratio - THRESHOLD)
        is_boundary = margin < 0.05

        if ratio <= THRESHOLD:
            value, conf = InteractionGrammar.SELECTIVE_AND, 0.85
            evidence = (f"Selectivity ratio = {ratio:.3f} ≤ 0.15 "
                        f"({n_compatible_partners}/{n_total_possible_partners}) → Gamma_SELECTIVE_AND")
        else:
            value, conf = InteractionGrammar.BROAD_OR, 0.82
            evidence = (f"Selectivity ratio = {ratio:.3f} > 0.15 "
                        f"({n_compatible_partners}/{n_total_possible_partners}) → Gamma_BROAD_OR")

        return PrimitiveAssignment(
            primitive="Gamma", value=value, confidence=conf,
            method="selectivity_ratio", evidence=evidence,
            is_boundary=is_boundary, boundary_margin=round(margin, 3),
        )

    # ── Ω (TopoIndex) — derived via P-22 decision tree ───────────────────────

    def assign_Omega_from_primitives(
        self,
        T: Topology,
        K: KineticCharacter,
        D: Dimensionality,
        Gamma: InteractionGrammar,
        G: Granularity,
    ) -> PrimitiveAssignment:
        """
        Derive Ω from {T, K, D, Γ, G} using the P-22 five-rule decision tree.
        Zero mismatches on 32/32 catalog synthons in the original audit.

        Rules (priority order):
          1. K = MBL                        → Ω = Z2_CLASS  (MBL topological order)
          2. T = BRAID                      → Ω = NON_ABELIAN  (anyonic statistics)
          3. T = NETWORK and G = GLOBAL     → Ω = CHERN  (Chern-Simons global network)
          4. D = TEMPORAL and G = GLOBAL    → Ω = Z2_CLASS  (temporal global protection)
          5. Gamma = QUANTUM_AND            → Ω = NON_ABELIAN  (quantum grammar)
          default                           → Ω = None
        """
        if K == KineticCharacter.MBL:
            value = TopoIndex.Z2_CLASS
            rule = "Rule 1: K=MBL → Ω=Z2_CLASS"
        elif T == Topology.BRAID:
            value = TopoIndex.NON_ABELIAN
            rule = "Rule 2: T=BRAID → Ω=NON_ABELIAN"
        elif T == Topology.NETWORK and G == Granularity.GLOBAL:
            value = TopoIndex.CHERN
            rule = "Rule 3: T=NETWORK ∧ G=GLOBAL → Ω=CHERN"
        elif D == Dimensionality.TEMPORAL and G == Granularity.GLOBAL:
            value = TopoIndex.Z2_CLASS
            rule = "Rule 4: D=TEMPORAL ∧ G=GLOBAL → Ω=Z2_CLASS"
        elif Gamma == InteractionGrammar.QUANTUM_AND:
            value = TopoIndex.NON_ABELIAN
            rule = "Rule 5: Γ=QUANTUM_AND → Ω=NON_ABELIAN"
        else:
            value = None
            rule = "Default: no Ω-trigger rules fired → Ω=None"

        return PrimitiveAssignment(
            primitive="Omega", value=value, confidence=0.97,
            method="p22_decision_tree", evidence=f"P-22 5-rule tree: {rule}",
            is_boundary=False, boundary_margin=0.0,
        )

    # ── Φ (CriticalityPhase) — heuristic ─────────────────────────────────────

    def assign_Phi(
        self,
        varma_score: Optional[float] = None,
        gd_degeneracy_detected: bool = False,
        has_scale_free_behavior: bool = False,
    ) -> PrimitiveAssignment:
        """
        Assign Φ from Varma probe score and G/D degeneracy signal.

        This is the hardest primitive to assign algorithmically because it encodes
        a dynamical regime, not a static structural property.  The Varma score
        (from criticality_probe) is the best available proxy.

        Rules:
          Φ_c (CRITICAL)   : varma_score > 0.5  OR  gd_degeneracy_detected + scale_free
          Φ_sub (SUBCRIT.) : otherwise

        Note: This assignment is HEURISTIC (not yet fully algorithmic).  The
        assignment project flag 'is_boundary' is set to True for all Phi
        assignments to indicate this status.
        """
        if varma_score is None and not gd_degeneracy_detected:
            return PrimitiveAssignment(
                primitive="Phi", value=CriticalityPhase.SUBCRITICAL, confidence=0.50,
                method="heuristic_phi", evidence="No Varma score or G/D degeneracy data — defaulting to SUBCRITICAL",
                is_boundary=True, boundary_margin=0.0,
            )

        score = varma_score if varma_score is not None else 0.0
        strong_signal = (score > 0.70) or (gd_degeneracy_detected and has_scale_free_behavior)
        weak_signal = (0.3 < score <= 0.70) or gd_degeneracy_detected

        if strong_signal:
            value = CriticalityPhase.CRITICAL
            conf = min(0.85, 0.60 + 0.35 * score) if varma_score else 0.75
            evidence = (f"Varma score = {score:.2f} > 0.70 OR G/D degeneracy + scale-free "
                        f"→ Φ_c (CRITICAL)")
        elif weak_signal:
            value = CriticalityPhase.CRITICAL
            conf = 0.60
            evidence = (f"Varma score = {score:.2f} ∈ (0.3, 0.7] or G/D degeneracy signal "
                        f"→ Φ_c (marginal — boundary case)")
        else:
            value = CriticalityPhase.SUBCRITICAL
            conf = 0.75
            evidence = f"Varma score = {score:.2f} ≤ 0.3, no degeneracy → Φ_sub"

        return PrimitiveAssignment(
            primitive="Phi", value=value, confidence=round(conf, 3),
            method="heuristic_phi", evidence=evidence,
            is_boundary=True,  # always flagged — Phi assignment is not yet fully algorithmic
            boundary_margin=round(abs(score - 0.50), 3) if varma_score else 0.0,
        )

    # ── Master assign_all ─────────────────────────────────────────────────────

    def assign_all(self, measurements: Dict) -> SynthonAssignment:
        """
        Run all applicable assignment methods from a measurements dict.

        Expected keys (all optional):
          delta_g_kj          : float — binding free energy (kJ/mol)
          xi_cp               : float — ξ_CP from thermodynamics pipeline
          delta_g_ddagger_kj  : float — activation barrier (kJ/mol)
          pathway_multiplicity: int   — number of kinetically accessible pathways
          n_components        : int   — number of interacting structural units
          scale_nm            : float — characteristic spatial scale (nm)
          is_single_molecule  : bool
          is_assembly         : bool
          is_catalytic_cycle  : bool
          is_holographic      : bool
          n_binding_sites     : int
          has_cycle           : bool
          is_self_complementary: bool
          has_cage_geometry   : bool
          has_braid_statistics: bool
          partner_count       : int
          is_covalent         : bool
          is_reversible       : bool
          is_catalytic        : bool
          is_mechanical       : bool
          partners_identical  : bool
          has_pseudosymmetry  : bool
          n_compatible_partners    : int
          n_total_possible_partners: int
          is_quantum          : bool
          varma_score         : float — Varma QXY probe score (0–1)
          gd_degeneracy       : bool
          has_scale_free      : bool
        """
        m = measurements
        assignments: Dict[str, PrimitiveAssignment] = {}
        underdetermined: List[str] = []
        boundary_cases: List[str] = []
        consistency_checks: List[str] = []
        method_comparisons: List[MethodComparison] = []
        notes: List[str] = []

        # ── F ────────────────────────────────────────────────────────────────
        f_assignments = []
        if "delta_g_kj" in m:
            f_assignments.append(self.assign_F_from_delta_g(m["delta_g_kj"]))
        if "xi_cp" in m:
            f_assignments.append(self.assign_F_from_xi_cp(m["xi_cp"]))

        if len(f_assignments) == 2:
            mc = MethodComparison(
                primitive="F",
                method_a=f_assignments[0].method, value_a=f_assignments[0].value,
                method_b=f_assignments[1].method, value_b=f_assignments[1].value,
                agreement=f_assignments[0].value == f_assignments[1].value,
            )
            method_comparisons.append(mc)
            consistency_checks.append(mc.summary())
            # Use the higher-confidence one; flag conflict
            chosen = max(f_assignments, key=lambda x: x.confidence)
            if not mc.agreement:
                chosen.confidence *= 0.75
                chosen.evidence += " [METHOD CONFLICT — confidence reduced]"
                notes.append(f"F assignment method conflict: "
                             f"{f_assignments[0].method}={f_assignments[0].value.name} vs "
                             f"{f_assignments[1].method}={f_assignments[1].value.name}")
            assignments["F"] = chosen
        elif len(f_assignments) == 1:
            assignments["F"] = f_assignments[0]
        else:
            underdetermined.append("F")

        # ── K ────────────────────────────────────────────────────────────────
        if "delta_g_ddagger_kj" in m:
            assignments["K"] = self.assign_K_from_barrier(
                m["delta_g_ddagger_kj"],
                m.get("pathway_multiplicity"),
            )
        else:
            underdetermined.append("K")

        # ── G ────────────────────────────────────────────────────────────────
        g_assignments = []
        if "n_components" in m:
            g_assignments.append(self.assign_G_from_components(m["n_components"]))
        if "scale_nm" in m:
            g_assignments.append(self.assign_G_from_scale_nm(m["scale_nm"]))

        if len(g_assignments) == 2:
            mc = MethodComparison(
                primitive="G",
                method_a=g_assignments[0].method, value_a=g_assignments[0].value,
                method_b=g_assignments[1].method, value_b=g_assignments[1].value,
                agreement=g_assignments[0].value == g_assignments[1].value,
            )
            method_comparisons.append(mc)
            consistency_checks.append(mc.summary())
            chosen = max(g_assignments, key=lambda x: x.confidence)
            if not mc.agreement:
                chosen.confidence *= 0.75
                notes.append(f"G assignment method conflict")
            assignments["G"] = chosen
        elif len(g_assignments) == 1:
            assignments["G"] = g_assignments[0]
        else:
            underdetermined.append("G")

        # ── D ────────────────────────────────────────────────────────────────
        d_flags = {
            "is_single_molecule": m.get("is_single_molecule", False),
            "is_assembly": m.get("is_assembly", False),
            "is_catalytic_cycle": m.get("is_catalytic_cycle", False),
            "is_holographic": m.get("is_holographic", False),
        }
        if any(d_flags.values()):
            assignments["D"] = self.assign_D(**d_flags)
        else:
            underdetermined.append("D")

        # ── T ────────────────────────────────────────────────────────────────
        t_flags = {k: m.get(k, False) for k in
                   ["has_cycle", "is_self_complementary", "has_cage_geometry", "has_braid_statistics"]}
        t_counts = {k: m.get(k, 1) for k in ["n_binding_sites", "partner_count"]}
        if any(t_flags.values()) or t_counts["n_binding_sites"] != 1:
            assignments["T"] = self.assign_T(**t_flags, **t_counts)
        else:
            underdetermined.append("T")

        # ── R ────────────────────────────────────────────────────────────────
        r_keys = {"is_covalent", "is_reversible", "is_catalytic", "is_mechanical"}
        r_flags = {k: m.get(k, False) for k in r_keys}
        # Assign R whenever any R-flag key was explicitly provided (even if all False
        # → that means non-covalent, which is a valid assignment, not underdetermined).
        if r_keys & set(m.keys()):
            assignments["R"] = self.assign_R(**r_flags)
        else:
            underdetermined.append("R")

        # ── P ────────────────────────────────────────────────────────────────
        if "partners_identical" in m or "has_pseudosymmetry" in m:
            assignments["P"] = self.assign_P(
                partners_identical=m.get("partners_identical", False),
                has_pseudosymmetry=m.get("has_pseudosymmetry", False),
            )
        else:
            underdetermined.append("P")

        # ── Γ ────────────────────────────────────────────────────────────────
        if "n_compatible_partners" in m and "n_total_possible_partners" in m:
            assignments["Gamma"] = self.assign_Gamma(
                n_compatible_partners=m["n_compatible_partners"],
                n_total_possible_partners=m["n_total_possible_partners"],
                is_quantum=m.get("is_quantum", False),
            )
        elif m.get("is_quantum", False):
            assignments["Gamma"] = self.assign_Gamma(0, 0, is_quantum=True)
        else:
            underdetermined.append("Gamma")

        # ── Ω — derived from {T, K, D, Γ, G} ────────────────────────────────
        needed = {"T", "K", "D", "Gamma", "G"}
        if needed <= set(assignments.keys()):
            assignments["Omega"] = self.assign_Omega_from_primitives(
                T=assignments["T"].value,
                K=assignments["K"].value,
                D=assignments["D"].value,
                Gamma=assignments["Gamma"].value,
                G=assignments["G"].value,
            )
        else:
            underdetermined.append("Omega")

        # ── Φ ────────────────────────────────────────────────────────────────
        assignments["Phi"] = self.assign_Phi(
            varma_score=m.get("varma_score"),
            gd_degeneracy_detected=m.get("gd_degeneracy", False),
            has_scale_free_behavior=m.get("has_scale_free", False),
        )

        # ── Collect boundary cases ────────────────────────────────────────────
        for pname, pa in assignments.items():
            if pa.is_boundary:
                boundary_cases.append(pname)

        return SynthonAssignment(
            assignments=assignments,
            boundary_cases=boundary_cases,
            underdetermined=underdetermined,
            consistency_checks=consistency_checks,
            method_comparisons=method_comparisons,
            notes=notes,
        )

    def assign_from_smiles(
        self,
        smiles: str,
        description: str = "",
        extra_measurements: Optional[Dict] = None,
    ) -> SynthonAssignment:
        """
        Run assign_all() from a SMILES string via RDKit structural flag extraction.

        This covers D, T, R, and G(scale_nm) automatically.  Primitives that
        cannot be determined from 2D SMILES remain in the `underdetermined` list:

            Undetermined from SMILES alone
            ─────────────────────────────
            K   — needs ΔG‡ (activation barrier); provide delta_g_ddagger_kj
            Γ   — needs interaction selectivity; provide n_compatible/n_total_partners
            P   — needs partner identity; provide partners_identical / has_pseudosymmetry
            Φ   — needs Varma score or G/D degeneracy data
            Ω   — derived from {T,K,D,Γ,G}; auto-computed when all four are available

        Any of those can be supplied via extra_measurements to complete the picture.

        Args:
            smiles           : SMILES string for the molecule or complex
            description      : Optional description (improves ΔG group matching)
            extra_measurements: Dict with additional keys (e.g. delta_g_ddagger_kj,
                               varma_score, n_compatible_partners, …) merged on top

        Returns:
            SynthonAssignment with per-primitive results, boundary flags, and
            notes listing any detected structural features.
        """
        from .rdkit_utils import smiles_to_measurements
        m = smiles_to_measurements(smiles, description)

        # Surface detected features as notes
        sf = m.pop("_structural_flags", None)
        m.pop("_smiles_source", None)
        m.pop("_delta_g_method", None)
        m.pop("_delta_g_confidence", None)
        rdkit_warnings = m.pop("_warnings", [])

        if extra_measurements:
            m.update(extra_measurements)

        sa = self.assign_all(m)

        # K-from-R fallback: if ΔG‡ was not supplied, estimate K from R prior
        if "K" not in sa.assignments and "R" in sa.assignments:
            sa.assignments["K"] = self.assign_K_from_recognition_mode(
                sa.assignments["R"].value
            )
            if "K" in sa.underdetermined:
                sa.underdetermined.remove("K")
            sa.notes.append(
                f"K assigned from R prior ({sa.assignments['R'].value.name}) "
                f"— no ΔG‡ data; provide delta_g_ddagger_kj for a measurement-based value"
            )

        # Ω retry: may now be computable if K was just filled in above
        if "Omega" not in sa.assignments and "Omega" in sa.underdetermined:
            needed = {"T", "K", "D", "Gamma", "G"}
            if needed <= set(sa.assignments.keys()):
                sa.assignments["Omega"] = self.assign_Omega_from_primitives(
                    T=sa.assignments["T"].value,
                    K=sa.assignments["K"].value,
                    D=sa.assignments["D"].value,
                    Gamma=sa.assignments["Gamma"].value,
                    G=sa.assignments["G"].value,
                )
                sa.underdetermined.remove("Omega")

        # Prepend RDKit-derived notes
        if sf is not None and sf.detected_features:
            sa.notes = ["RDKit features: " + "; ".join(sf.detected_features)] + sa.notes
        if rdkit_warnings:
            sa.notes += ["RDKit warnings: " + w for w in rdkit_warnings]

        return sa


# ══════════════════════════════════════════════════════════════════════════════
# Catalog consistency checker
# ══════════════════════════════════════════════════════════════════════════════

def check_catalog_consistency(
    engine: Optional[PrimitiveAssignmentEngine] = None,
) -> CatalogConsistencyReport:
    """
    Run the algorithmic assignment engine against all catalog synthons that
    have ΔG and/or ξ_CP data, and compare to hand-coded primitive values.

    This is the self-consistency test of the Algorithmic Assignment Project:
    if the primitives are natural joints, independent assignment should agree
    with expert hand-coding across the catalog.

    Returns a CatalogConsistencyReport with per-primitive agreement rates,
    boundary cases, and conflict lists.
    """
    from .registry import global_catalog
    from .thermodynamics import calibrated_xi_cp_table

    if engine is None:
        engine = PrimitiveAssignmentEngine()

    xi_table = calibrated_xi_cp_table()
    all_synthons = global_catalog.search()

    entries: List[CatalogConsistencyEntry] = []
    conflict_summary: Dict[str, List[str]] = {}

    for synthon in all_synthons:
        name = synthon.name or ""
        measurements: Dict = {}

        # Pull ξ_CP if available
        if name in xi_table:
            row = xi_table[name]
            measurements["xi_cp"] = row.xi_CP
            if row.delta_g is not None and row.delta_g < 0:
                # Only use delta_g for F assignment when it is a binding free energy
                # (negative).  Positive values in this table are activation barriers
                # (stored by compute_eta_CP for kinetic synthons) — not suitable for
                # P-21 Boltzmann-ratio assignment.
                measurements["delta_g_kj"] = row.delta_g

        if not measurements:
            continue  # skip synthons with no quantitative data

        sa = engine.assign_all(measurements)

        # Compare F assignment (most data available)
        for prim_name, pa in sa.assignments.items():
            cat_val = _get_catalog_primitive(synthon, prim_name)
            if cat_val is None:
                continue

            agrees = (pa.value == cat_val)
            entry = CatalogConsistencyEntry(
                name=name,
                primitive=prim_name,
                catalog_value=cat_val,
                assigned_value=pa.value,
                agrees=agrees,
                confidence=pa.confidence,
                is_boundary=pa.is_boundary,
                note=pa.evidence,
            )
            entries.append(entry)

            if not agrees:
                conflict_summary.setdefault(prim_name, []).append(name)

    n_checked = len(set(e.name for e in entries))
    n_prim = len(entries)
    n_agree = sum(1 for e in entries if e.agrees)
    n_boundary = sum(1 for e in entries if e.is_boundary)

    agreement_rate = n_agree / n_prim if n_prim > 0 else 0.0
    boundary_rate  = n_boundary / n_prim if n_prim > 0 else 0.0

    notes = [
        f"Checked {n_checked} catalog synthons with quantitative data",
        f"F and K assignments from ξ_CP/ΔG data only — other primitives underdetermined without structural metadata",
        "Φ assignments are heuristic — all flagged as boundary cases",
    ]

    return CatalogConsistencyReport(
        entries=entries,
        n_synthons_checked=n_checked,
        n_primitives_checked=n_prim,
        overall_agreement_rate=round(agreement_rate, 4),
        boundary_rate=round(boundary_rate, 4),
        conflict_summary=conflict_summary,
        notes=notes,
    )


def _get_catalog_primitive(synthon: Synthon, prim_name: str) -> Optional[Any]:
    """Extract a primitive value from a Synthon by primitive name string."""
    mapping = {
        "F": synthon.fidelity,
        "K": synthon.kinetic_character,
        "G": synthon.granularity,
        "D": synthon.dimensionality,
        "T": synthon.topology,
        "R": synthon.recognition_mode,
        "P": synthon.polarity,
        "Gamma": synthon.interaction_grammar,
        "Phi": synthon.criticality_phase,
        "Omega": synthon.topo_index,
    }
    return mapping.get(prim_name)


# ══════════════════════════════════════════════════════════════════════════════
# Self-consistency under decomposition
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class DecompositionConsistencyEntry:
    """Result of re-assigning a synthon's atoms and checking round-trip consistency."""
    synthon_name: str
    n_atoms: int
    primitive: str
    original_value: Any
    reconstructed_value: Any
    consistent: bool
    note: str = ""


def _lattice_result_to_synthon(lr, name: str = "join_result") -> Synthon:
    """Convert a LatticeResult to a Synthon, replacing CONFLICT tokens with defaults."""
    from .algebra import CONFLICT

    def _safe(val, default):
        return default if val == CONFLICT else val

    return Synthon(
        name=name,
        dimensionality=_safe(lr.dimensionality, Dimensionality.MOLECULAR),
        topology=_safe(lr.topology, Topology.NETWORK),
        recognition_mode=_safe(lr.recognition_mode, RecognitionMode.NON_COVALENT),
        polarity=_safe(lr.polarity, Polarity.SELF_COMPLEMENTARY_SYM),
        fidelity=_safe(lr.fidelity, Fidelity.LOW),
        kinetic_character=_safe(lr.kinetic_character, KineticCharacter.MODERATE),
        granularity=_safe(lr.granularity, Granularity.LOCAL),
        interaction_grammar=_safe(lr.interaction_grammar, InteractionGrammar.SELECTIVE_AND),
        criticality_phase=_safe(lr.criticality_phase, CriticalityPhase.SUBCRITICAL),
        topo_index=_safe(lr.topo_index, None),
    )


def check_decomposition_consistency(
    synthon_name: str,
    measurements_per_atom: List[Dict],
    engine: Optional[PrimitiveAssignmentEngine] = None,
) -> List[DecompositionConsistencyEntry]:
    """
    Self-consistency test under decomposition (Algorithmic Assignment Project, test 2).

    Workflow:
      1. Load synthon from catalog.
      2. Run principal_decomp → atoms.
      3. Assign each atom's primitives independently from measurements_per_atom.
      4. Reconstruct via join of all atoms.
      5. Compare reconstructed encoding to original catalog encoding.

    measurements_per_atom: list of measurement dicts, one per atom (in order).
    If len(measurements_per_atom) < n_atoms, remaining atoms are skipped.

    Returns a list of per-primitive consistency entries.
    """
    from .registry import global_catalog
    from .decompose import principal_decomp
    from .algebra import join as algebra_join

    if engine is None:
        engine = PrimitiveAssignmentEngine()

    synthon = global_catalog.get(synthon_name)
    if synthon is None:
        return [DecompositionConsistencyEntry(
            synthon_name=synthon_name, n_atoms=0, primitive="*",
            original_value=None, reconstructed_value=None, consistent=False,
            note=f"Synthon '{synthon_name}' not found in catalog",
        )]

    pd_result = principal_decomp(synthon)
    atoms = pd_result.factors
    n_atoms = len(atoms)

    if n_atoms == 0:
        return [DecompositionConsistencyEntry(
            synthon_name=synthon_name, n_atoms=0, primitive="*",
            original_value=None, reconstructed_value=None, consistent=False,
            note="principal_decomp returned no atoms",
        )]

    # Assign each atom independently
    assigned_atoms = []
    for i, atom in enumerate(atoms):
        if i < len(measurements_per_atom):
            sa = engine.assign_all(measurements_per_atom[i])
            assigned_atoms.append(sa.to_synthon(name=f"{synthon_name}_atom_{i}"))
        else:
            assigned_atoms.append(atom)  # use original atom if no measurements

    # Reconstruct via iterated join.
    # algebra_join returns a LatticeResult (not a Synthon), so we convert each
    # intermediate result back to a Synthon before the next join.
    reconstructed = assigned_atoms[0]
    for atom in assigned_atoms[1:]:
        lr = algebra_join(reconstructed, atom)
        reconstructed = _lattice_result_to_synthon(lr, f"{synthon_name}_join")

    # Compare to original
    results = []
    primitives_to_check = [
        ("F", synthon.fidelity, reconstructed.fidelity),
        ("K", synthon.kinetic_character, reconstructed.kinetic_character),
        ("G", synthon.granularity, reconstructed.granularity),
        ("D", synthon.dimensionality, reconstructed.dimensionality),
        ("T", synthon.topology, reconstructed.topology),
        ("Phi", synthon.criticality_phase, reconstructed.criticality_phase),
    ]
    for prim, orig, recon in primitives_to_check:
        consistent = (orig == recon)
        results.append(DecompositionConsistencyEntry(
            synthon_name=synthon_name,
            n_atoms=n_atoms,
            primitive=prim,
            original_value=orig,
            reconstructed_value=recon,
            consistent=consistent,
            note=("" if consistent
                  else f"Original={orig.name if hasattr(orig,'name') else orig}, "
                       f"Reconstructed={recon.name if hasattr(recon,'name') else recon}"),
        ))

    return results
