"""
Constraint Propagation Engine — Core logic for imscription compatibility and propagation.

This module implements:
- Constraint satisfaction checking
- Compatibility matrices for Recognition Modes
- Fidelity propagation calculations
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum

from .models import (
    Imscription,
    Dimensionality,
    Topology,
    Recognition,
    RecognitionMode,   # backward compat alias
    Polarity,
    Grammar,
    Fidelity,
    KineticChar,
    Granularity,
    Criticality,
    CriticalityPhase,  # backward compat alias
    Protection,
    Chirality,
    Stoichiometry,
    _prot_ord,
    _chir_ord,
)


# =============================================================================
# Axiom 6 & 7 Keyword Indicators (IG_FIXES.md)
# =============================================================================

# Axiom 6: D_∞ requires closed cycle with reset mechanism
AXIOM_6_RESET_INDICATORS = [
    "reset", "reform", "regenerat", "hydroly", "return",
    "cycle", "turnover", "re-form", "dissipat", "renew",
    "restore", "recycl", "replenish", "reconstitut",
    # Photoswitch reset mechanisms
    "photoisomeriz", "electrocycliz", "ring clos", "ring open",
    "thermal relax", "thermal revers", "irradiat", "photorevers",
    "photo-induced", "light-driven", "conrotatory", "disrotatory",
    "photochrom", "isomeriz", "z-to-e", "e-to-z", "trans-to-cis",
    "cis-to-trans", "open form", "closed form", "ring-open", "ring-clos",
    "back-react", "back react", "thermal isomeriz",
]

AXIOM_6_PROCESS_INDICATORS = [
    "catalyz", "oxidat", "reduct", "transfer",
    "phosphoryl", "condensat", "oscillat", "periodic",
    "reaction", "transformation", "conversion", "turnover",
    # Photoswitch process indicators
    "switching", "isomeriz", "photostimul", "photo-trigger",
    "photoactivat", "photogenerat", "ring closure", "ring opening",
    "photoinduced", "photorespons", "photoswitchab",
]

# Axiom 7: T_⋈ requires named closing bond/interaction
AXIOM_7_CLOSING_INDICATORS = [
    "hydrogen bond", "h-bond", "hbond", "coordinate", "covalent",
    "close", "ring", "loop", "cycl", "R2_2", "R22", "macrocycle",
    "crown", "cryptand", "rotaxane", "caten", "dimer",
    "base pair", "chelate", "bite-angle",
]

AXIOM_7_INVALID_TOPO_KEYWORDS = [
    "linear", "rod", "chain", "axial", "two-ended", "terminus",
    "extended chain", "polymer chain", "fibrous", "helical",
]

# Axiom 7 extension: T_∪ bowl topology — open concave cavity, single portal
# Mechanistic distinguisher from T_□□: guest exchanges through the open face
# without framework distortion; K_teshlig is exceptional not default.
# Network ring topology sub-labels (T_∈ sub-types)
# Used by catalog repair to upgrade generic T_∈ entries
NETWORK_HEX_KEYWORDS = [
    "hexagonal", "honeycomb", "graphene", "graphitic", "hex net",
    "6-membered ring", "six-membered ring", "ice ih", "ice i_h",
    "ice ic", "ice i_c", "ice xi", "hex-mof", "hkust", "kagome",
    "hex framework", "trigonal network", "hexagonal network",
]
NETWORK_MIXED_KEYWORDS = [
    "ice iii", "ice iv", "ice v", "ice ix",
    "mixed ring", "mixed-ring", "4+5+6", "4+6+8", "5+6+8",
    "amorphous network", "disordered network", "topologically disordered",
    "non-hexagonal", "distorted tetrahedral network",
]
NETWORK_INTERPENETRATING_KEYWORDS = [
    "interpenetrating", "interpenetrated", "self-penetrating",
    "twofold interpenetrating", "two-fold interpenetrating",
    "doubly interpenetrating", "two independent network",
    "two interlocked network", "bcc network", "bcc ice",
    "ice vi", "ice vii", "ice viii", "ice i_vii",
    "catenated network", "entangled network", "polycatenated",
]
NETWORK_SYM_KEYWORDS = [
    "ice x", "ice-x", "symmetric hydrogen bond",
    "centrosymmetric h-bond", "proton-symmetric",
    "symmetric o-h-o", "proton shared", "shared proton",
    "superionic", "proton conductor network",
]

AXIOM_7_BOWL_NAME_KEYWORDS = [
    "calix", "calixarene", "calixpyrrole", "calixpyridine",
    "resorcinarene", "resorcarene", "cavitand",
    "cyclotriveratrylene", "ctv", "corannulene",
    "hemicarceplex", "hemicarcerand", "half-cage",
    "pillar[", "pillarene",
    "deep-cavity", "bowl", "concave", "open cavity",
    "half-sandwich", "open-faced",
]
AXIOM_7_BOWL_DESC_INDICATORS = [
    "cone conformation", "cone conf", "open portal", "upper rim", "lower rim",
    "portal", "aperture", "bowl-shaped", "concave cavity",
    "anion-π", "anion-pi", "cation-π", "cation-pi",
    "guest enter", "guest exit", "exchange through",
]

# Axiom 7 extension: T_□□ cage topology requires a named closing face
AXIOM_7B_CAGE_CLOSING_INDICATORS = [
    "self-assemble", "self-assembly", "cage-close", "cage close",
    "cage formation", "panelling", "face-capped", "face-cap",
    "encapsulate", "encapsulation", "enclose", "enclosure",
    "sequester", "portal", "aperture", "cryptand", "carcerand",
    "cucurbit", "metal-organic polyhedr", "covalent organic cage",
    "condense", "cyclize",
]


@dataclass
class AxiomResult:
    """
    Result of an axiom validation check.
    
    Attributes:
        axiom: Axiom number/name
        satisfied: True if axiom is satisfied, False if violated
        violations: List of violation messages
        warnings: List of warning messages
    """
    axiom: int
    satisfied: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def violated(self) -> bool:
        """Alias for not satisfied."""
        return not self.satisfied


class CompatibilityResult(Enum):
    """Result of a compatibility check."""
    COMPATIBLE = "compatible"
    CONDITIONAL = "conditional"  # Compatible under certain conditions
    INCOMPATIBLE = "incompatible"


@dataclass
class CompatibilityReport:
    """Report on imscription compatibility."""
    result: CompatibilityResult
    imscription_a: str
    imscription_b: str
    details: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    
    @property
    def is_compatible(self) -> bool:
        return self.result in {CompatibilityResult.COMPATIBLE, CompatibilityResult.CONDITIONAL}


class CompatibilityMatrix:
    """
    Matrix defining compatibility rules between recognition modes and polarities.
    
    Based on the physical chemistry principles from QUANTIG.md:
    - Covalent bonds are generally incompatible with mechanical bonds
    - Non-covalent interactions can couple with most other modes
    - Self-complementary polarities only match with themselves
    """
    
    # Recognition mode compatibility
    RECOGNITION_COMPATIBILITY: Dict[Tuple[RecognitionMode, RecognitionMode], CompatibilityResult] = {
        # Same mode always compatible
        (RecognitionMode.tot, RecognitionMode.tot): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ado, RecognitionMode.ado): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ear, RecognitionMode.ear): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ian, RecognitionMode.ian): CompatibilityResult.COMPATIBLE,
        
        # Covalent + Non-covalent: conditional (orthogonal chemistry)
        (RecognitionMode.tot, RecognitionMode.ado): CompatibilityResult.CONDITIONAL,
        (RecognitionMode.ado, RecognitionMode.tot): CompatibilityResult.CONDITIONAL,
        
        # Covalent + Dynamic: compatible (dynamic covalent chemistry)
        (RecognitionMode.tot, RecognitionMode.ear): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ear, RecognitionMode.tot): CompatibilityResult.COMPATIBLE,
        
        # Non-covalent + Dynamic: compatible (supramolecular catalysis)
        (RecognitionMode.ado, RecognitionMode.ear): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ear, RecognitionMode.ado): CompatibilityResult.COMPATIBLE,
        
        # Non-covalent + Mechanical: compatible (supramolecular rotaxanes)
        (RecognitionMode.ado, RecognitionMode.ian): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.ian, RecognitionMode.ado): CompatibilityResult.COMPATIBLE,
        
        # Dynamic + Mechanical: conditional
        (RecognitionMode.ear, RecognitionMode.ian): CompatibilityResult.CONDITIONAL,
        (RecognitionMode.ian, RecognitionMode.ear): CompatibilityResult.CONDITIONAL,
        
        # Covalent + Mechanical: incompatible (typically)
        (RecognitionMode.tot, RecognitionMode.ian): CompatibilityResult.INCOMPATIBLE,
        (RecognitionMode.ian, RecognitionMode.tot): CompatibilityResult.INCOMPATIBLE,
    }
    
    # Polarity compatibility
    POLARITY_COMPATIBILITY: Dict[Tuple[Polarity, Polarity], CompatibilityResult] = {
        # Self-complementary matches itself (both symmetric and pseudosymmetric)
        (Polarity.or_, Polarity.or_): CompatibilityResult.COMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.COMPATIBLE,
        (Polarity.or_, Polarity.yew): CompatibilityResult.COMPATIBLE,
        (Polarity.yew, Polarity.or_): CompatibilityResult.COMPATIBLE,

        # Acceptor + Donor: compatible
        (Polarity.yew, Polarity.yew): CompatibilityResult.COMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.COMPATIBLE,

        # Directional pairs
        (Polarity.church, Polarity.church): CompatibilityResult.COMPATIBLE,
        (Polarity.church, Polarity.yew): CompatibilityResult.COMPATIBLE,
        (Polarity.church, Polarity.yew): CompatibilityResult.COMPATIBLE,
        (Polarity.yew, Polarity.church): CompatibilityResult.COMPATIBLE,
        (Polarity.yew, Polarity.church): CompatibilityResult.COMPATIBLE,

        # Same polarity (non-self-complementary): incompatible
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,

        # Self-complementary + others: incompatible
        (Polarity.or_, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.or_, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.or_, Polarity.church): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.church): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.or_): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.or_): CompatibilityResult.INCOMPATIBLE,
        (Polarity.church, Polarity.or_): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.yew, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
        (Polarity.church, Polarity.yew): CompatibilityResult.INCOMPATIBLE,
    }
    
    @classmethod
    def check_recognition_compatibility(
        cls,
        mode_a: RecognitionMode,
        mode_b: RecognitionMode,
    ) -> CompatibilityResult:
        """Check if two recognition modes are compatible."""
        return cls.RECOGNITION_COMPATIBILITY.get(
            (mode_a, mode_b),
            CompatibilityResult.INCOMPATIBLE,
        )
    
    @classmethod
    def check_polarity_compatibility(
        cls,
        polarity_a: Polarity,
        polarity_b: Polarity,
    ) -> CompatibilityResult:
        """Check if two polarities are compatible."""
        return cls.POLARITY_COMPATIBILITY.get(
            (polarity_a, polarity_b),
            CompatibilityResult.INCOMPATIBLE,
        )
    
    @classmethod
    def get_conditions(
        cls,
        mode_a: RecognitionMode,
        mode_b: RecognitionMode,
    ) -> List[str]:
        """Return conditions for conditional compatibility."""
        result = cls.check_recognition_compatibility(mode_a, mode_b)
        
        if result != CompatibilityResult.CONDITIONAL:
            return []
        
        conditions = []
        
        # Covalent + Non-covalent: need orthogonal reactivity
        if {mode_a, mode_b} == {RecognitionMode.tot, RecognitionMode.ado}:
            conditions.append("Orthogonal reactivity required (no cross-reactivity)")
            conditions.append("Sequential assembly recommended")
        
        # Dynamic + Mechanical: need appropriate topology
        if {mode_a, mode_b} == {RecognitionMode.ear, RecognitionMode.ian}:
            conditions.append("Mechanical bond must not interfere with catalytic cycle")
            conditions.append("Template-directed synthesis may be required")
        
        return conditions


@dataclass
class ConstraintEngine:
    """
    Engine for checking constraint satisfaction in imscription systems.
    
    Implements the constraint propagation principles from QUANTIG.md:
    - imscriptions act as local constraints that reduce degrees of freedom
    - Strong constraints (high F) collapse phase space onto narrow trajectories
    - Constraint efficiency depends on primitive combinations
    """
    
    compatibility_matrix: CompatibilityMatrix = field(default_factory=CompatibilityMatrix)
    
    def check_pair_compatibility(
        self,
        imscription_a: Imscription,
        imscription_b: Imscription,
    ) -> CompatibilityReport:
        """
        Check full compatibility between two imscriptions.
        
        Returns a detailed report with all compatibility checks.
        """
        details = {}
        all_conditions = []
        incompatibilities = []
        
        # Check recognition mode compatibility
        rec_compat = self.compatibility_matrix.check_recognition_compatibility(
            imscription_a.recognition_mode,
            imscription_b.recognition_mode,
        )
        details["recognition_mode"] = rec_compat.value
        if rec_compat == CompatibilityResult.CONDITIONAL:
            conditions = self.compatibility_matrix.get_conditions(
                imscription_a.recognition_mode,
                imscription_b.recognition_mode,
            )
            all_conditions.extend(conditions)
        elif rec_compat == CompatibilityResult.INCOMPATIBLE:
            incompatibilities.append("recognition_mode")
        
        # Check polarity compatibility
        pol_compat = self.compatibility_matrix.check_polarity_compatibility(
            imscription_a.polarity,
            imscription_b.polarity,
        )
        details["polarity"] = pol_compat.value
        if pol_compat == CompatibilityResult.INCOMPATIBLE:
            incompatibilities.append("polarity")
        
        # Check domain overlap (for hybrid systems)
        domain_overlap = imscription_a.dimensionality.domains & imscription_b.dimensionality.domains
        details["domain_overlap"] = bool(domain_overlap)
        details["shared_domains"] = list(domain_overlap)
        if not domain_overlap:
            # No shared domain means they operate on different axes - can coexist
            details["note"] = "No shared domains - imscriptions operate independently"
        
        # Check granularity compatibility
        gran_compat = (
            imscription_a.granularity.can_amplify_to(imscription_b.granularity) or
            imscription_b.granularity.can_amplify_to(imscription_a.granularity)
        )
        details["granularity_compatible"] = gran_compat
        if not gran_compat:
            incompatibilities.append("granularity")
        
        # Determine overall result
        if incompatibilities:
            result = CompatibilityResult.INCOMPATIBLE
            details["incompatibilities"] = incompatibilities
        elif all_conditions:
            result = CompatibilityResult.CONDITIONAL
            details["conditions"] = all_conditions
        else:
            result = CompatibilityResult.COMPATIBLE
        
        return CompatibilityReport(
            result=result,
            imscription_a=imscription_a.name,
            imscription_b=imscription_b.name,
            details=details,
            conditions=all_conditions,
        )
    
    def check_system_consistency(
        self,
        imscriptions: List[Imscription],
    ) -> Dict[str, Any]:
        """
        Check consistency of a system of multiple imscriptions.
        
        Returns a report with:
        - Pairwise compatibility matrix
        - Overall system consistency score
        - Identified conflicts
        """
        n = len(imscriptions)
        compatibility_matrix_result = {}
        conflicts = []
        conditionals = []
        
        for i in range(n):
            for j in range(i + 1, n):
                pair_a = imscriptions[i]
                pair_b = imscriptions[j]
                
                report = self.check_pair_compatibility(pair_a, pair_b)
                pair_key = f"{pair_a.name}::{pair_b.name}"
                compatibility_matrix_result[pair_key] = report.result.value
                
                if report.result == CompatibilityResult.INCOMPATIBLE:
                    conflicts.append({
                        "pair": (pair_a.name, pair_b.name),
                        "reason": report.details.get("incompatibilities", []),
                    })
                elif report.result == CompatibilityResult.CONDITIONAL:
                    conditionals.append({
                        "pair": (pair_a.name, pair_b.name),
                        "conditions": report.conditions,
                    })
        
        # Calculate system consistency score
        total_pairs = n * (n - 1) // 2 if n > 1 else 1
        compatible_pairs = total_pairs - len(conflicts) - len(conditionals)
        consistency_score = compatible_pairs / total_pairs if total_pairs > 0 else 1.0
        
        return {
            "num_imscriptions": n,
            "total_pairs": total_pairs,
            "compatible_pairs": compatible_pairs,
            "conditional_pairs": len(conditionals),
            "conflicts": len(conflicts),
            "consistency_score": consistency_score,
            "compatibility_matrix": compatibility_matrix_result,
            "conflict_details": conflicts,
            "conditional_details": conditionals,
            "is_consistent": len(conflicts) == 0,
        }
    
    def compute_constraint_strength(
        self,
        imscription: Imscription,
        context: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Compute the effective constraint strength of a imscription.
        
        This combines the intrinsic constraint strength with context factors.
        
        Args:
            imscription: The imscription to evaluate
            context: Optional context factors (solvent, temperature, etc.)
        
        Returns:
            Constraint strength (0.0-1.0)
        """
        base_strength = imscription.constraint_strength
        
        if context is None:
            return base_strength
        
        # Apply context modifiers
        modifiers = []
        
        if "solvent_compatibility" in context:
            modifiers.append(context["solvent_compatibility"])
        if "temperature_optimal" in context:
            modifiers.append(1.0 if context["temperature_optimal"] else 0.7)
        if "concentration_sufficient" in context:
            modifiers.append(min(1.0, context["concentration_sufficient"]))
        
        if modifiers:
            avg_modifier = sum(modifiers) / len(modifiers)
            return base_strength * avg_modifier
        
        return base_strength


@dataclass
class FidelityPropagator:
    """
    Computes fidelity propagation through imscription networks.
    
    Based on the cooperativity principles from QUANTIG.md:
    - Triple H-bond arrays show superlinear induction growth
    - Many-body polarization amplifies effective fidelity
    - Granularity transitions (G_beta → G_gamma) couple with F_beltl → F_hardsign
    """
    
    # Cooperativity factors based on topology
    TOPOLOGY_COOPERATIVITY: Dict[Topology, float] = field(default_factory=lambda: {
        Topology.mime: 1.5,  # Cyclic motifs show cooperativity
        Topology.T_linear: 1.0,  # Linear chains: additive
        Topology.judge: 2.0,  # Hub nodes: strong amplification
        Topology.T_linear: 1.0,
        Topology.T_branched: 1.3,
        Topology.judge: 2.5,
        Topology.T_network_hex: 2.5,           # hexagonal rings: same cooperativity as generic network
        Topology.T_network_mixed: 2.3,          # mixed ring sizes: slightly damped long-range cooperativity
        Topology.T_network_interp: 3.0,  # two coupled propagation channels: superlinear
        Topology.T_network_sym: 2.8,            # centrosymmetric bonding: near-isotropic propagation
        Topology.oil: 1.8,
    })
    
    # Granularity amplification factors
    GRANULARITY_AMPLIFICATION: Dict[Granularity, float] = field(default_factory=lambda: {
        Granularity.ice: 1.0,
        Granularity.bib: 1.5,
        Granularity.thigh: 2.0,
    })
    
    def propagate(
        self,
        imscriptions: List[Imscription],
        base_fidelity: Optional[Fidelity] = None,
    ) -> Fidelity:
        """
        Compute propagated fidelity for a system of imscriptions.
        
        Args:
            imscriptions: List of imscriptions in the system
            base_fidelity: Optional base fidelity (uses first imscription's F if not provided)
        
        Returns:
            Effective fidelity after propagation
        """
        if not imscriptions:
            return Fidelity.age
        
        if base_fidelity is None:
            base_fidelity = imscriptions[0].fidelity
        
        base_value = base_fidelity.numeric_value
        
        # Apply cooperativity factors
        total_cooperativity = 0.0
        total_granularity_amp = 0.0
        
        for imscription in imscriptions:
            # Topology cooperativity
            topo_factor = self.TOPOLOGY_COOPERATIVITY.get(
                imscription.topology, 1.0
            )
            total_cooperativity += topo_factor - 1.0
            
            # Granularity amplification
            gran_factor = self.GRANULARITY_AMPLIFICATION.get(
                imscription.granularity, 1.0
            )
            total_granularity_amp = max(total_granularity_amp, gran_factor - 1.0)
        
        # Compute amplified fidelity
        # Cooperativity adds up (superlinear for multiple imscriptions)
        cooperativity_bonus = min(1.0, total_cooperativity * 0.1)
        granularity_bonus = total_granularity_amp * 0.15
        
        amplified_value = min(1.0, base_value + cooperativity_bonus + granularity_bonus)
        
        # Map back to Fidelity enum
        if amplified_value >= 0.90:
            return Fidelity.peep
        elif amplified_value >= 0.60:
            return Fidelity.they
        else:
            return Fidelity.age
    
    def compute_cooperativity_factor(
        self,
        imscriptions: List[Imscription],
    ) -> Dict[str, Any]:
        """
        Compute detailed cooperativity analysis for a imscription system.
        
        Returns:
            Dict with cooperativity breakdown by component
        """
        if not imscriptions:
            return {"error": "No imscriptions provided"}
        
        components = {
            "num_imscriptions": len(imscriptions),
            "topology_factors": [],
            "granularity_factors": [],
            "total_cooperativity": 0.0,
            "total_granularity_amplification": 0.0,
            "estimated_fidelity_gain": 0.0,
        }
        
        for imscription in imscriptions:
            topo_factor = self.TOPOLOGY_COOPERATIVITY.get(imscription.topology, 1.0)
            gran_factor = self.GRANULARITY_AMPLIFICATION.get(imscription.granularity, 1.0)
            
            components["topology_factors"].append({
                "imscription": imscription.name,
                "topology": imscription.topology.value,
                "factor": topo_factor,
            })
            components["granularity_factors"].append({
                "imscription": imscription.name,
                "granularity": imscription.granularity.value,
                "factor": gran_factor,
            })
            
            components["total_cooperativity"] += topo_factor - 1.0
            components["total_granularity_amplification"] = max(
                components["total_granularity_amplification"],
                gran_factor - 1.0,
            )
        
        # Estimate fidelity gain
        coop_bonus = min(1.0, components["total_cooperativity"] * 0.1)
        gran_bonus = components["total_granularity_amplification"] * 0.15
        components["estimated_fidelity_gain"] = coop_bonus + gran_bonus
        
        # Check for superlinear induction (signature of cooperative systems)
        if len(imscriptions) >= 3:
            # Triple arrays should show superlinear behavior
            components["is_superlinear"] = components["total_cooperativity"] > 0.5
            if components["is_superlinear"]:
                components["note"] = (
                    "System exhibits superlinear cooperativity - "
                    "analogous to triple H-bond array (Transformation #5)"
                )
        
        return components


# =============================================================================
# Composition Axiom Validation — NEW
# =============================================================================

class AxiomValidator:
    """
    Validates the five composition axioms from QUANTIG.md Section IV.
    
    Each axiom is a falsifiable proposition about primitive combinations.
    """
    
    @classmethod
    def validate_axiom1_cyclic_closure(cls, imscription: Imscription) -> Dict[str, Any]:
        """
        Axiom 1: Cyclic closure amplifies fidelity (T_⋈–F rule).
        
        A imscription with T_⋈ and P_± necessarily achieves F ≥ F_dh,
        provided R_⊇ or R_⊆.
        
        Prediction: no T_⋈/P_± imscription will be assigned F_beltl.
        Falsified by: cyclic self-complementary motif with xi_CP > 10.5 nats.
        """
        is_cyclic = imscription.topology == Topology.mime
        is_self_comp = imscription.polarity.is_self_complementary
        is_valid_recognition = imscription.recognition_mode in {
            RecognitionMode.ado,
            RecognitionMode.tot,
            RecognitionMode.tot,
        }
        
        # Check if axiom applies
        axiom_applies = is_cyclic and is_self_comp and is_valid_recognition
        
        if not axiom_applies:
            return {
                "axiom": "Axiom 1 (Cyclic Closure)",
                "applies": False,
                "reason": "Not a cyclic self-complementary imscription with valid R",
            }
        
        # Check prediction
        fidelity_violated = imscription.fidelity == Fidelity.age
        
        return {
            "axiom": "Axiom 1 (Cyclic Closure)",
            "applies": True,
            "cyclic": is_cyclic,
            "self_complementary": is_self_comp,
            "recognition_valid": is_valid_recognition,
            "fidelity": imscription.fidelity.value,
            "prediction_satisfied": not fidelity_violated,
            "violated": fidelity_violated,
            "falsification_note": (
                "AXIOM FALSIFIED" if fidelity_violated else "Axiom satisfied"
            ),
        }
    
    @classmethod
    def validate_axiom2_local_grammar_barrier(
        cls,
        imscription: Imscription,
        target_granularity: Optional[Granularity] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 2: Local grammar blocks network propagation (G_ב–Γ barrier rule).
        
        A imscription with G_ב and Γ_⊗ cannot propagate constraint beyond
        its immediate recognition pair.
        
        Prediction: no single G_ב/Γ_⊗ imscription will be found as the sole
        organizing element of a MOF, polymer, or oscillatory network.
        """
        is_local = imscription.granularity == Granularity.ice
        is_specific = (
            imscription.grammar == Grammar.vow and
            imscription.fidelity == Fidelity.peep
        )
        
        axiom_applies = is_local and is_specific
        
        if not axiom_applies:
            return {
                "axiom": "Axiom 2 (Local Grammar Barrier)",
                "applies": False,
                "reason": "Not a local specific imscription",
            }
        
        # Check if target granularity is achievable
        if target_granularity is None:
            can_propagate = False
        else:
            can_propagate = imscription.granularity.can_amplify_to(target_granularity)
        
        # Axiom predicts NO propagation to global
        prediction_satisfied = not can_propagate or target_granularity != Granularity.thigh
        
        return {
            "axiom": "Axiom 2 (Local Grammar Barrier)",
            "applies": True,
            "local": is_local,
            "specific_grammar": is_specific,
            "can_propagate_to_global": can_propagate and target_granularity == Granularity.thigh,
            "prediction_satisfied": prediction_satisfied,
            "violated": not prediction_satisfied,
        }
    
    @classmethod
    def validate_axiom3_cooperative_induction(
        cls,
        imscriptions: List[Imscription],
        induction_ratio: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 3: Cooperative induction superlinearity signals G_ב → G_ג transition.
        
        When induction component of E_int grows faster than linearly with
        number of recognition contacts, system has crossed from G_ב to G_ג.
        
        Prediction: any imscription array showing superlinear SAPT induction
        should be reclassified from G_ב to G_ג.
        """
        if len(imscriptions) < 2:
            return {
                "axiom": "Axiom 3 (Cooperative Induction)",
                "applies": False,
                "reason": "Need at least 2 imscriptions for cooperativity analysis",
            }
        
        # Check if all are local (candidate for transition)
        all_local = all(s.granularity == Granularity.ice for s in imscriptions)
        
        if induction_ratio is None:
            # Estimate from imscription properties
            # Triple H-bond arrays typically have induction_ratio ~2.5-3.5
            induction_ratio = len(imscriptions) * 0.8  # Rough estimate
        
        # Superlinear threshold
        is_superlinear = induction_ratio > len(imscriptions) * 1.2
        
        # Check current granularity assignments
        granularities = set(s.granularity for s in imscriptions)
        
        # Axiom predicts reclassification if superlinear
        should_reclassify = is_superlinear and Granularity.ice in granularities
        
        return {
            "axiom": "Axiom 3 (Cooperative Induction)",
            "applies": all_local,
            "num_imscriptions": len(imscriptions),
            "induction_ratio": induction_ratio,
            "is_superlinear": is_superlinear,
            "superlinear_threshold": len(imscriptions) * 1.2,
            "should_reclassify_to_mesoscale": should_reclassify,
            "current_granularities": [g.value for g in granularities],
        }
    
    @classmethod
    def validate_axiom4_sequential_grammar(
        cls,
        imscription: Imscription,
    ) -> Dict[str, Any]:
        """
        Axiom 4: Sequential grammar requires temporal or catalytic dimension.
        
        Γ_→ (ordered sequential recognition) is only physically realizable
        if the imscription possesses D_∞ or R_‡, or both.
        
        Prediction: all documented allosteric systems with ordered binding
        will contain either a conformational change (R_‡-like) or temporal component.
        """
        is_sequential = imscription.grammar == Grammar.measure
        
        if not is_sequential:
            return {
                "axiom": "Axiom 4 (Sequential Grammar)",
                "applies": False,
                "reason": "Not a sequential grammar",
            }
        
        # Reads as a copy-paste slip and is not one. This was
        # `(D_invomega, TEMPORAL)`, and those were two names for the same glyph
        # 𐑼 — the Shavian rename collapsed both onto `array`, which is
        # behaviourally identical. The test is Ð = 𐑼, the D_∞ the docstring
        # names. Left as a single member so it stops inviting a "fix".
        has_temporal = imscription.dimensionality is Dimensionality.array
        has_catalytic = imscription.recognition_mode in {
            RecognitionMode.ear,
            RecognitionMode.tot,
        }
        
        # Axiom requires at least one
        axiom_satisfied = has_temporal or has_catalytic
        
        return {
            "axiom": "Axiom 4 (Sequential Grammar)",
            "applies": True,
            "sequential_grammar": is_sequential,
            "has_temporal_dimension": has_temporal,
            "has_catalytic_mode": has_catalytic,
            "axiom_satisfied": axiom_satisfied,
            "violated": not axiom_satisfied,
            "falsification_note": (
                "AXIOM FALSIFIED" if not axiom_satisfied else "Axiom satisfied"
            ),
        }
    
    @classmethod
    def validate_axiom5_criticality(
        cls,
        imscription: Imscription,
        correlation_length: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 5: Criticality contracts the primitive basis.
        
        At criticality (G-D degeneracy, ξ → ∞), G becomes redundant given D.
        
        Prediction: a critical imscription's behavior at molecular scale fully
        predicts its behavior at supramolecular and temporal scales.
        """
        is_critical = imscription.criticality_phase == CriticalityPhase.monad
        
        if not is_critical:
            # Check if approaching criticality
            if correlation_length is not None and correlation_length > 500:
                approaching = True
            else:
                approaching = False
            
            return {
                "axiom": "Axiom 5 (Criticality)",
                "applies": False,
                "is_critical": False,
                "approaching_criticality": approaching,
                "reason": "Not at criticality",
            }
        
        # At criticality, check if G and D are truly degenerate
        # This requires domain knowledge about scale-free behavior
        # For now, flag for manual verification
        return {
            "axiom": "Axiom 5 (Criticality)",
            "applies": True,
            "is_critical": True,
            "correlation_length": correlation_length,
            "g_d_degenerate": True,  # By definition at criticality
            "requires_verification": True,
            "verification_note": (
                "Verify that molecular-scale behavior predicts supramolecular "
                "and temporal behavior without additional primitive information"
            ),
        }

    @classmethod
    def validate_axiom6_temporal_grounding(
        cls,
        imscription: Imscription,
        grounding_result: Optional[Any] = None,
    ) -> AxiomResult:
        """
        Axiom 6: D_∞ requires a physically grounded reset mechanism.

        Supports two reset types via ``imscription.metadata["grounding"]["reset"]["type"]``:

        * ``"discrete"`` (default / backward-compat): closed cycle with a named
          reset step.  Requires: initial state, transformation, work performed,
          and a reset mechanism.  Validated against AXIOM_6_RESET_INDICATORS +
          AXIOM_6_PROCESS_INDICATORS keyword sets (or the structured
          ``cycle_steps`` list when present).

        * ``"continuous"``: open dissipative / driven system with a sustained
          driving gradient and no sharp reset event.  Requires a
          ``driving_gradient`` block with at minimum ``description`` and
          ``coupling`` fields.

        Falsified by:
          - ``"discrete"``: no identifiable reset mechanism in grounding
          - ``"continuous"``: no ``driving_gradient`` block, or ``description``
            / ``coupling`` fields missing
        """
        violations = []
        warnings = []

        # ── 1. Check whether D_∞ (TEMPORAL) is assigned ──────────────────────
        has_temporal = Dimensionality.array in (
            imscription.dimensionality if isinstance(imscription.dimensionality, (list, set, tuple))
            else [imscription.dimensionality]
        )

        if not has_temporal:
            return AxiomResult(axiom=6, satisfied=True, violations=[], warnings=[])

        # ── 2. Read reset_type from structured grounding block ────────────────
        # Primary source: imscription.grounding["reset"] (persisted in catalog JSON)
        # Fallback: imscription.metadata["grounding"]["reset"] (legacy in-memory path)
        sg = getattr(imscription, "grounding", None) or {}
        reset_block = sg.get("reset", {})
        if not reset_block:
            # fallback to metadata-nested path (not persisted, but accepted in tests)
            meta_grounding = imscription.metadata.get("grounding", {}) if hasattr(imscription, "metadata") and imscription.metadata else {}
            reset_block = meta_grounding.get("reset", {})
        reset_type = reset_block.get("type", "discrete")  # default: discrete (backward-compat)

        # ── 3. Continuous-reset path ──────────────────────────────────────────
        if reset_type == "continuous":
            dg = reset_block.get("driving_gradient", {})
            missing = [f for f in ("description", "coupling") if not dg.get(f)]
            if missing:
                violations.append(
                    f"D_∞ with reset_type='continuous' requires a driving_gradient block "
                    f"with 'description' and 'coupling' fields. Missing: {missing}. "
                    "If the system has a discrete cycle, set reset_type='discrete'."
                )
            else:
                # Soft check: entropy export recommended for completeness
                if not dg.get("entropy_export") and not reset_block.get("entropy_export"):
                    warnings.append(
                        "D_∞ continuous reset: 'entropy_export' not specified. "
                        "Recommended for full Axiom 6 grounding (e.g., heat dissipation, "
                        "waste product efflux)."
                    )
            return AxiomResult(
                axiom=6,
                satisfied=len(violations) == 0,
                violations=violations,
                warnings=warnings,
            )

        # ── 4. Discrete-reset path (default) ─────────────────────────────────
        # First try structured cycle_steps list (takes priority over keyword scan)
        cycle_steps = reset_block.get("cycle_steps", [])
        if cycle_steps:
            if len(cycle_steps) < 2:
                violations.append(
                    "D_∞ discrete reset: cycle_steps list has fewer than 2 entries. "
                    "Specify at minimum: initial state and reset/closing step."
                )
            # cycle_steps present and sufficient → satisfied
            return AxiomResult(
                axiom=6,
                satisfied=len(violations) == 0,
                violations=violations,
                warnings=warnings,
            )

        # Fallback: keyword scan on axiom6_grounding metadata dict
        ax6 = imscription.metadata.get("axiom6_grounding", {}) if hasattr(imscription, "metadata") and imscription.metadata else {}
        if ax6:
            required_keys = {"initial_state", "transformation", "work_performed", "reset_mechanism"}
            present_keys = {k for k in required_keys if ax6.get(k)}
            missing_keys = required_keys - present_keys
            if missing_keys:
                violations.append(
                    f"D_∞ discrete reset: axiom6_grounding block missing required fields: "
                    f"{sorted(missing_keys)}. Must specify initial_state, transformation, "
                    "work_performed, and reset_mechanism."
                )
            return AxiomResult(
                axiom=6,
                satisfied=len(violations) == 0,
                violations=violations,
                warnings=warnings,
            )

        # Fallback: keyword scan on LLM grounding result justification text
        if grounding_result is not None:
            justifications: dict = {}
            if hasattr(grounding_result, 'justifications'):
                jj = grounding_result.justifications
                justifications = jj() if callable(jj) else jj
            elif hasattr(grounding_result, 'primitive_results'):
                for prim_name, prim_result in grounding_result.primitive_results.items():
                    if hasattr(prim_result, 'justification_text'):
                        justifications[prim_name] = prim_result.justification_text
                    elif hasattr(prim_result, 'justification'):
                        justifications[prim_name] = prim_result.justification

            dim_just_lower = (justifications.get("dimensionality") or "").lower()
            has_reset = any(kw in dim_just_lower for kw in AXIOM_6_RESET_INDICATORS)
            has_process = any(kw in dim_just_lower for kw in AXIOM_6_PROCESS_INDICATORS)

            if not (has_reset and has_process):
                violations.append(
                    "D_∞ assigned but no closed cycle specified in grounding justification. "
                    "Must name: initial state, transformation, work performed, and reset "
                    "mechanism. Alternatively set metadata['grounding']['reset']['type'] to "
                    "'continuous' for open dissipative systems."
                )
        else:
            warnings.append(
                "D_∞ assigned without grounding check. Cannot verify reset mechanism. "
                "Run with --use-llm-grounding or add metadata['grounding']['reset'] block "
                "to validate."
            )

        return AxiomResult(
            axiom=6,
            satisfied=len(violations) == 0,
            violations=violations,
            warnings=warnings,
        )

    @classmethod
    def validate_axiom7_cyclic_grounding(
        cls,
        imscription: Imscription,
        grounding_result: Optional[Any] = None,
    ) -> AxiomResult:
        """
        Axiom 7: T_⋈ requires a named closing bond or interaction.
        
        A imscription assigned T_⋈ must identify the specific interaction
        or bond that closes the loop. If no closing interaction can be
        named, T_⋈ is invalid and the correct assignment is T_≫ (chain)
        or T_□ (hub/node).
        
        Falsified by: a documented T_⋈ imscription where no closing bond
        or interaction can be identified.
        
        Args:
            imscription: The imscription to validate
            grounding_result: Optional GroundingResult with justifications
            
        Returns:
            AxiomResult with violations if T_⋈ assigned without closing bond
        """
        violations = []
        warnings = []
        
        is_bowtie = imscription.topology == Topology.mime
        is_cage = imscription.topology == Topology.oil

        if not is_bowtie and not is_cage:
            return AxiomResult(axiom=7, satisfied=True, violations=[], warnings=[])

        if grounding_result is not None:
            justifications = {}
            if hasattr(grounding_result, 'justifications'):
                if callable(grounding_result.justifications):
                    justifications = grounding_result.justifications()
                else:
                    justifications = grounding_result.justifications
            elif hasattr(grounding_result, 'primitive_results'):
                for prim_name, prim_result in grounding_result.primitive_results.items():
                    if hasattr(prim_result, 'justification_text'):
                        justifications[prim_name] = prim_result.justification_text
                    elif hasattr(prim_result, 'justification'):
                        justifications[prim_name] = prim_result.justification

            topo_justification = justifications.get("topology", "")
            topo_just_lower = topo_justification.lower() if topo_justification else ""

            # Check for invalid justifications (linear, chain, etc.)
            has_invalid = any(
                kw in topo_just_lower for kw in AXIOM_7_INVALID_TOPO_KEYWORDS
            )

            if is_bowtie:
                # Check for closing bond indicators (T_⋈)
                has_closing = any(
                    kw in topo_just_lower for kw in AXIOM_7_CLOSING_INDICATORS
                )
                if has_invalid:
                    violations.append(
                        "T_⋈ assigned but justification describes a linear/chain topology. "
                        "T_⋈ requires a closed loop. Assign T_≫ for chains or T_□ for hub topologies."
                    )
                elif not has_closing:
                    warnings.append(
                        "T_⋈ assigned but no closing bond/interaction named in justification. "
                        "Specify the interaction that closes the ring (e.g., 'two O-H···O hydrogen "
                        "bonds completing the R²₂(8) motif')."
                    )
            else:
                # T_□□ cage: require a closing face indicator
                has_closing_face = any(
                    kw in topo_just_lower for kw in AXIOM_7B_CAGE_CLOSING_INDICATORS
                )
                if has_invalid:
                    violations.append(
                        "T_□□ assigned but justification describes a linear/chain topology. "
                        "T_□□ requires 3D closure. Assign T_□ for hub/node topologies."
                    )
                elif not has_closing_face:
                    warnings.append(
                        "T_□□ (cage) assigned but no closing face/assembly event named in "
                        "justification. Specify the event that seals the third dimension "
                        "(e.g., 'self-assembly into a Pd₁₂L₂₄ sphere', 'face-capping', "
                        "'encapsulates guest via portal closure')."
                    )
        else:
            # No grounding result — warning only
            if is_bowtie:
                warnings.append(
                    "T_⋈ assigned without grounding check. Cannot verify closing interaction. "
                    "Run with --use-llm-grounding to validate."
                )
            else:
                warnings.append(
                    "T_□□ (cage) assigned without grounding check. Cannot verify closing face. "
                    "Run with --use-llm-grounding to validate."
                )
        
        return AxiomResult(
            axiom=7,
            satisfied=len(violations) == 0,
            violations=violations,
            warnings=warnings,
        )

    @classmethod
    def validate_all_axioms(
        cls,
        imscription_or_imscriptions: Union[Imscription, List[Imscription]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate all seven axioms for a imscription or system.
        
        Includes Axioms 1-5 (composition axioms) and Axioms 6-7 (grounding axioms).

        Returns comprehensive axiom validation report.
        """
        if isinstance(imscription_or_imscriptions, Imscription):
            imscriptions = [imscription_or_imscriptions]
            imscription = imscription_or_imscriptions
        else:
            imscriptions = imscription_or_imscriptions
            imscription = imscriptions[0] if imscriptions else None

        results = {}
        grounding_result = kwargs.get("grounding_result")

        if imscription:
            results["axiom1"] = cls.validate_axiom1_cyclic_closure(imscription)
            results["axiom2"] = cls.validate_axiom2_local_grammar_barrier(
                imscription,
                target_granularity=kwargs.get("target_granularity"),
            )
            results["axiom4"] = cls.validate_axiom4_sequential_grammar(imscription)
            results["axiom5"] = cls.validate_axiom5_criticality(
                imscription,
                correlation_length=kwargs.get("correlation_length"),
            )
            # Fix 2: Axiom 6 (temporal grounding)
            results["axiom6"] = cls.validate_axiom6_temporal_grounding(
                imscription,
                grounding_result=grounding_result,
            )
            # Fix 3: Axiom 7 (cyclic topology grounding)
            results["axiom7"] = cls.validate_axiom7_cyclic_grounding(
                imscription,
                grounding_result=grounding_result,
            )

        if len(imscriptions) >= 2:
            results["axiom3"] = cls.validate_axiom3_cooperative_induction(
                imscriptions,
                induction_ratio=kwargs.get("induction_ratio"),
            )

        # Summary — count hard violations (not warnings)
        violations = 0
        for r in results.values():
            # Handle both dict results (Axioms 1-5) and AxiomResult objects (Axioms 6-7)
            if isinstance(r, AxiomResult):
                if r.violated:
                    violations += 1
            elif isinstance(r, dict):
                if r.get("violated", False):
                    violations += 1

        serializable_results = {}
        for k, r in results.items():
            if isinstance(r, AxiomResult):
                serializable_results[k] = {
                    "axiom": r.axiom,
                    "satisfied": r.satisfied,
                    "violated": r.violated,
                    "violations": r.violations,
                    "warnings": r.warnings,
                }
            else:
                serializable_results[k] = r

        return {
            "num_axioms_tested": len(results),
            "violations": violations,
            "all_satisfied": violations == 0,
            "detailed_results": serializable_results,
        }


# =============================================================================
# CoreAxioms — Lean-aligned cross-primitive axioms A–D
# =============================================================================

@dataclass
class AxiomViolation:
    axiom:   str
    message: str
    imscription: str


class CoreAxioms:
    """
    The four axioms of the Grammar, in their correct formulation.

    Each axiom is a CLOSURE CONDITION on a named δ/μ dyad — not a co-occurrence
    rule between coordinates. An axiom asserts: for its split, μ∘δ = id with
    ΔS ≈ 0, EVALT being the affirmative arm and EVALF the failure arm. The split
    it names IS its content:

        A   Bulk → (Boundary projection, Bulk remainder) → Bulk
            T: the boundary accurately encodes the bulk.
            F: the encoding fails to represent the bulk.
        B   Topological-State → (Persistent-Chiral arm, Achiral arm) → same
            T: integer winding number conserved.
            F: broken symmetry without topological protection.
            Dialetheia-complete: both arms run, held at ENGAGR through transition.
        C   Bulk → (Boundary-Projection, Bulk-Residual) → Bulk
            T: the boundary-bulk correspondence is exact.
            F: the encoding fails to preserve bulk information.
        D   Bulk → (Boundary-encoding, Bulk-decoding) → Bulk
            T: μ∘δ = id is satisfied.
            F: the encoding is incomplete or symmetry is broken.

    Truth is established by RUNNING the dyad — see closure_verdict(). The twelve
    coordinates cannot decide it, so check() emits no coordinate violations.

    Why no coordinate form survives, on two independent grounds:

      Self-application. The correct formulation of A imscribes with Ħ=𐑫 ∧ Ç=𐑧 —
      the exact pair old-A forbade. The correct formulation of D imscribes with
      Ð=𐑛 ∧ Ω=𐑟 (old-D demanded Ð=𐑦) and Þ=𐑸 at Ð=𐑛 (violating one-way C).
      Each correct formulation violates the coordinate form of its own axiom.

      Catalog. Every shadow has counterexamples across several dimensionalities,
      including genuine non-Abelian anyons and SIC existence entries at Ω=𐑟
      without Ð=𐑦. Axiom C's biconditional was already revised to one-way on this
      kind of evidence (2026-05-03); the one-way form falls to it equally.

    A coordinate co-occurrence was never the rule. It was the shadow a closure
    condition casts on its own maximally-collapsed case, which is why each shadow
    looked exact for AdS/CFT-like systems and failed everywhere else.
    """

    # The named split of each axiom, from the correct_formulation_of_axiom_* ob3ects.
    SPLITS: Dict[str, Dict[str, str]] = {
        "A": {"input": "Bulk state",       "arms": "Boundary projection | Bulk remainder"},
        "B": {"input": "Topological-State", "arms": "Persistent-Chiral arm | Achiral arm"},
        "C": {"input": "Bulk-State",       "arms": "Boundary-Projection | Bulk-Residual"},
        "D": {"input": "Bulk-state",       "arms": "Boundary-encoding | Bulk-decoding"},
    }

    @staticmethod
    def check(imscription: Imscription) -> List[AxiomViolation]:
        """
        Coordinate-level check. Always empty: the axioms are closure conditions and
        cannot be decided from the twelve coordinates (see the class docstring —
        every coordinate form is refuted by self-application and by the catalog).

        Kept so existing callers keep working and so that auditing a tuple never
        reports a violation the Grammar does not actually hold. To establish an
        axiom, run its dyad: closure_verdict().
        """
        return []

    @staticmethod
    def closure_verdict(ob3ect: Dict[str, Any], axiom: str = "") -> Dict[str, Any]:
        """
        Establish an axiom by RUNNING its dyad, from a designed ob3ect.

        Reads the object's split/fuse phase and its entropy assertion, and returns
        the Belnap verdict:
            T  the dyad closes: μ∘δ = id, fuse returns the split input, ΔS ≈ 0
            F  the dyad is named but does not close (lossy / symmetry broken)
            B  both arms run and are held together (dialetheia-complete, ENGAGR)
            N  no dyad present to run — nothing is asserted

        This is the whole content of an axiom. A tuple cannot supply it.
        """
        phases = (ob3ect or {}).get("phases") or {}
        p2, p3, p4 = phases.get("phase_2") or {}, phases.get("phase_3") or {}, phases.get("phase_4") or {}
        p6 = phases.get("phase_6") or {}

        if not p2.get("split_element") or not p2.get("fuse_element"):
            return {"verdict": "N", "axiom": axiom, "reason": "no δ/μ dyad present — nothing asserted"}

        closes = p2.get("frobenius_verdict") == "PASS"
        # μ∘δ = id: the fuse must return exactly what the split consumed.
        restores = bool(p2.get("fuse_result")) and p2.get("fuse_result") == p2.get("split_input")
        lossless = "≈ 0" in str(p3.get("entropy_assertion", "")) or "≈ 0" in str(p6.get("delta_s_verdict", ""))
        verified = bool(p4.get("closure_verified"))

        steps = {s.get("opcode") for s in (p4.get("steps") or [])}
        both_arms = {"EVALT", "EVALF"} <= steps

        if closes and restores and lossless and verified:
            verdict = "B" if both_arms else "T"
        else:
            verdict = "F"
        return {
            "verdict": verdict,
            "axiom": axiom,
            "split": f"{p2.get('split_input')} → {p2.get('split_outputs')}",
            "fuse": p2.get("fuse_result"),
            "mu_delta_id": restores,
            "lossless": lossless,
            "dialetheia_complete": both_arms,
            "affirmative": p3.get("true_description", ""),
            "failure": p3.get("false_description", ""),
        }

    @staticmethod
    def check_all(imscriptions) -> Dict[str, List[AxiomViolation]]:
        """Check a collection of imscriptions. Returns {name: [violations]}."""
        return {s.name: CoreAxioms.check(s) for s in imscriptions}

    @staticmethod
    def audit_catalog(imscriptions) -> Dict[str, Any]:
        """Audit report: counts, violation breakdown by axiom, offending names."""
        all_violations = CoreAxioms.check_all(imscriptions)
        by_axiom: Dict[str, List[str]] = {"A": [], "B": [], "C": [], "D": []}
        total = 0
        for name, viols in all_violations.items():
            for v in viols:
                by_axiom[v.axiom].append(name)
                total += 1
        return {
            "total_imscriptions": len(imscriptions),
            "total_violations": total,
            "clean": total == 0,
            "by_axiom": {k: {"count": len(v), "imscriptions": v} for k, v in by_axiom.items()},
        }
