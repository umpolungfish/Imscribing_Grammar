"""
Constraint Propagation Engine — Core logic for synthon compatibility and propagation.

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
    Synthon,
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
    """Report on synthon compatibility."""
    result: CompatibilityResult
    synthon_a: str
    synthon_b: str
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
        (RecognitionMode.COVALENT, RecognitionMode.COVALENT): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.NON_COVALENT, RecognitionMode.NON_COVALENT): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.DYNAMIC_CATALYTIC): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.MECHANICAL, RecognitionMode.MECHANICAL): CompatibilityResult.COMPATIBLE,
        
        # Covalent + Non-covalent: conditional (orthogonal chemistry)
        (RecognitionMode.COVALENT, RecognitionMode.NON_COVALENT): CompatibilityResult.CONDITIONAL,
        (RecognitionMode.NON_COVALENT, RecognitionMode.COVALENT): CompatibilityResult.CONDITIONAL,
        
        # Covalent + Dynamic: compatible (dynamic covalent chemistry)
        (RecognitionMode.COVALENT, RecognitionMode.DYNAMIC_CATALYTIC): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.COVALENT): CompatibilityResult.COMPATIBLE,
        
        # Non-covalent + Dynamic: compatible (supramolecular catalysis)
        (RecognitionMode.NON_COVALENT, RecognitionMode.DYNAMIC_CATALYTIC): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.NON_COVALENT): CompatibilityResult.COMPATIBLE,
        
        # Non-covalent + Mechanical: compatible (supramolecular rotaxanes)
        (RecognitionMode.NON_COVALENT, RecognitionMode.MECHANICAL): CompatibilityResult.COMPATIBLE,
        (RecognitionMode.MECHANICAL, RecognitionMode.NON_COVALENT): CompatibilityResult.COMPATIBLE,
        
        # Dynamic + Mechanical: conditional
        (RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.MECHANICAL): CompatibilityResult.CONDITIONAL,
        (RecognitionMode.MECHANICAL, RecognitionMode.DYNAMIC_CATALYTIC): CompatibilityResult.CONDITIONAL,
        
        # Covalent + Mechanical: incompatible (typically)
        (RecognitionMode.COVALENT, RecognitionMode.MECHANICAL): CompatibilityResult.INCOMPATIBLE,
        (RecognitionMode.MECHANICAL, RecognitionMode.COVALENT): CompatibilityResult.INCOMPATIBLE,
    }
    
    # Polarity compatibility
    POLARITY_COMPATIBILITY: Dict[Tuple[Polarity, Polarity], CompatibilityResult] = {
        # Self-complementary matches itself (both symmetric and pseudosymmetric)
        (Polarity.SELF_COMPLEMENTARY_SYM, Polarity.SELF_COMPLEMENTARY_SYM): CompatibilityResult.COMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_PSEUDO, Polarity.SELF_COMPLEMENTARY_PSEUDO): CompatibilityResult.COMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_SYM, Polarity.SELF_COMPLEMENTARY_PSEUDO): CompatibilityResult.COMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_PSEUDO, Polarity.SELF_COMPLEMENTARY_SYM): CompatibilityResult.COMPATIBLE,

        # Acceptor + Donor: compatible
        (Polarity.ACCEPTOR, Polarity.DONOR): CompatibilityResult.COMPATIBLE,
        (Polarity.DONOR, Polarity.ACCEPTOR): CompatibilityResult.COMPATIBLE,

        # Directional pairs
        (Polarity.DONOR_ACCEPTOR, Polarity.DONOR_ACCEPTOR): CompatibilityResult.COMPATIBLE,
        (Polarity.DONOR_ACCEPTOR, Polarity.ACCEPTOR): CompatibilityResult.COMPATIBLE,
        (Polarity.DONOR_ACCEPTOR, Polarity.DONOR): CompatibilityResult.COMPATIBLE,
        (Polarity.ACCEPTOR, Polarity.DONOR_ACCEPTOR): CompatibilityResult.COMPATIBLE,
        (Polarity.DONOR, Polarity.DONOR_ACCEPTOR): CompatibilityResult.COMPATIBLE,

        # Same polarity (non-self-complementary): incompatible
        (Polarity.ACCEPTOR, Polarity.ACCEPTOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.DONOR, Polarity.DONOR): CompatibilityResult.INCOMPATIBLE,

        # Self-complementary + others: incompatible
        (Polarity.SELF_COMPLEMENTARY_SYM, Polarity.ACCEPTOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_SYM, Polarity.DONOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_SYM, Polarity.DONOR_ACCEPTOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_PSEUDO, Polarity.ACCEPTOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_PSEUDO, Polarity.DONOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.SELF_COMPLEMENTARY_PSEUDO, Polarity.DONOR_ACCEPTOR): CompatibilityResult.INCOMPATIBLE,
        (Polarity.ACCEPTOR, Polarity.SELF_COMPLEMENTARY_SYM): CompatibilityResult.INCOMPATIBLE,
        (Polarity.DONOR, Polarity.SELF_COMPLEMENTARY_SYM): CompatibilityResult.INCOMPATIBLE,
        (Polarity.DONOR_ACCEPTOR, Polarity.SELF_COMPLEMENTARY_SYM): CompatibilityResult.INCOMPATIBLE,
        (Polarity.ACCEPTOR, Polarity.SELF_COMPLEMENTARY_PSEUDO): CompatibilityResult.INCOMPATIBLE,
        (Polarity.DONOR, Polarity.SELF_COMPLEMENTARY_PSEUDO): CompatibilityResult.INCOMPATIBLE,
        (Polarity.DONOR_ACCEPTOR, Polarity.SELF_COMPLEMENTARY_PSEUDO): CompatibilityResult.INCOMPATIBLE,
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
        if {mode_a, mode_b} == {RecognitionMode.COVALENT, RecognitionMode.NON_COVALENT}:
            conditions.append("Orthogonal reactivity required (no cross-reactivity)")
            conditions.append("Sequential assembly recommended")
        
        # Dynamic + Mechanical: need appropriate topology
        if {mode_a, mode_b} == {RecognitionMode.DYNAMIC_CATALYTIC, RecognitionMode.MECHANICAL}:
            conditions.append("Mechanical bond must not interfere with catalytic cycle")
            conditions.append("Template-directed synthesis may be required")
        
        return conditions


@dataclass
class ConstraintEngine:
    """
    Engine for checking constraint satisfaction in synthon systems.
    
    Implements the constraint propagation principles from QUANTIG.md:
    - Synthons act as local constraints that reduce degrees of freedom
    - Strong constraints (high F) collapse phase space onto narrow trajectories
    - Constraint efficiency depends on primitive combinations
    """
    
    compatibility_matrix: CompatibilityMatrix = field(default_factory=CompatibilityMatrix)
    
    def check_pair_compatibility(
        self,
        synthon_a: Synthon,
        synthon_b: Synthon,
    ) -> CompatibilityReport:
        """
        Check full compatibility between two synthons.
        
        Returns a detailed report with all compatibility checks.
        """
        details = {}
        all_conditions = []
        incompatibilities = []
        
        # Check recognition mode compatibility
        rec_compat = self.compatibility_matrix.check_recognition_compatibility(
            synthon_a.recognition_mode,
            synthon_b.recognition_mode,
        )
        details["recognition_mode"] = rec_compat.value
        if rec_compat == CompatibilityResult.CONDITIONAL:
            conditions = self.compatibility_matrix.get_conditions(
                synthon_a.recognition_mode,
                synthon_b.recognition_mode,
            )
            all_conditions.extend(conditions)
        elif rec_compat == CompatibilityResult.INCOMPATIBLE:
            incompatibilities.append("recognition_mode")
        
        # Check polarity compatibility
        pol_compat = self.compatibility_matrix.check_polarity_compatibility(
            synthon_a.polarity,
            synthon_b.polarity,
        )
        details["polarity"] = pol_compat.value
        if pol_compat == CompatibilityResult.INCOMPATIBLE:
            incompatibilities.append("polarity")
        
        # Check domain overlap (for hybrid systems)
        domain_overlap = synthon_a.dimensionality.domains & synthon_b.dimensionality.domains
        details["domain_overlap"] = bool(domain_overlap)
        details["shared_domains"] = list(domain_overlap)
        if not domain_overlap:
            # No shared domain means they operate on different axes - can coexist
            details["note"] = "No shared domains - synthons operate independently"
        
        # Check granularity compatibility
        gran_compat = (
            synthon_a.granularity.can_amplify_to(synthon_b.granularity) or
            synthon_b.granularity.can_amplify_to(synthon_a.granularity)
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
            synthon_a=synthon_a.name,
            synthon_b=synthon_b.name,
            details=details,
            conditions=all_conditions,
        )
    
    def check_system_consistency(
        self,
        synthons: List[Synthon],
    ) -> Dict[str, Any]:
        """
        Check consistency of a system of multiple synthons.
        
        Returns a report with:
        - Pairwise compatibility matrix
        - Overall system consistency score
        - Identified conflicts
        """
        n = len(synthons)
        compatibility_matrix_result = {}
        conflicts = []
        conditionals = []
        
        for i in range(n):
            for j in range(i + 1, n):
                pair_a = synthons[i]
                pair_b = synthons[j]
                
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
            "num_synthons": n,
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
        synthon: Synthon,
        context: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Compute the effective constraint strength of a synthon.
        
        This combines the intrinsic constraint strength with context factors.
        
        Args:
            synthon: The synthon to evaluate
            context: Optional context factors (solvent, temperature, etc.)
        
        Returns:
            Constraint strength (0.0-1.0)
        """
        base_strength = synthon.constraint_strength
        
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
    Computes fidelity propagation through synthon networks.
    
    Based on the cooperativity principles from QUANTIG.md:
    - Triple H-bond arrays show superlinear induction growth
    - Many-body polarization amplifies effective fidelity
    - Granularity transitions (G_beta → G_gamma) couple with F_beltl → F_hardsign
    """
    
    # Cooperativity factors based on topology
    TOPOLOGY_COOPERATIVITY: Dict[Topology, float] = field(default_factory=lambda: {
        Topology.CYCLIC_BOWTIE: 1.5,  # Cyclic motifs show cooperativity
        Topology.CHAIN: 1.0,  # Linear chains: additive
        Topology.HUB_NODE: 2.0,  # Hub nodes: strong amplification
        Topology.LINEAR: 1.0,
        Topology.BRANCHED: 1.3,
        Topology.NETWORK: 2.5,
        Topology.NETWORK_HEX: 2.5,           # hexagonal rings: same cooperativity as generic network
        Topology.NETWORK_MIXED: 2.3,          # mixed ring sizes: slightly damped long-range cooperativity
        Topology.NETWORK_INTERPENETRATING: 3.0,  # two coupled propagation channels: superlinear
        Topology.NETWORK_SYM: 2.8,            # centrosymmetric bonding: near-isotropic propagation
        Topology.CAGE: 1.8,
    })
    
    # Granularity amplification factors
    GRANULARITY_AMPLIFICATION: Dict[Granularity, float] = field(default_factory=lambda: {
        Granularity.LOCAL: 1.0,
        Granularity.MESOSCALE: 1.5,
        Granularity.GLOBAL: 2.0,
    })
    
    def propagate(
        self,
        synthons: List[Synthon],
        base_fidelity: Optional[Fidelity] = None,
    ) -> Fidelity:
        """
        Compute propagated fidelity for a system of synthons.
        
        Args:
            synthons: List of synthons in the system
            base_fidelity: Optional base fidelity (uses first synthon's F if not provided)
        
        Returns:
            Effective fidelity after propagation
        """
        if not synthons:
            return Fidelity.LOW
        
        if base_fidelity is None:
            base_fidelity = synthons[0].fidelity
        
        base_value = base_fidelity.numeric_value
        
        # Apply cooperativity factors
        total_cooperativity = 0.0
        total_granularity_amp = 0.0
        
        for synthon in synthons:
            # Topology cooperativity
            topo_factor = self.TOPOLOGY_COOPERATIVITY.get(
                synthon.topology, 1.0
            )
            total_cooperativity += topo_factor - 1.0
            
            # Granularity amplification
            gran_factor = self.GRANULARITY_AMPLIFICATION.get(
                synthon.granularity, 1.0
            )
            total_granularity_amp = max(total_granularity_amp, gran_factor - 1.0)
        
        # Compute amplified fidelity
        # Cooperativity adds up (superlinear for multiple synthons)
        cooperativity_bonus = min(1.0, total_cooperativity * 0.1)
        granularity_bonus = total_granularity_amp * 0.15
        
        amplified_value = min(1.0, base_value + cooperativity_bonus + granularity_bonus)
        
        # Map back to Fidelity enum
        if amplified_value >= 0.90:
            return Fidelity.HIGH
        elif amplified_value >= 0.60:
            return Fidelity.MEDIUM
        else:
            return Fidelity.LOW
    
    def compute_cooperativity_factor(
        self,
        synthons: List[Synthon],
    ) -> Dict[str, Any]:
        """
        Compute detailed cooperativity analysis for a synthon system.
        
        Returns:
            Dict with cooperativity breakdown by component
        """
        if not synthons:
            return {"error": "No synthons provided"}
        
        components = {
            "num_synthons": len(synthons),
            "topology_factors": [],
            "granularity_factors": [],
            "total_cooperativity": 0.0,
            "total_granularity_amplification": 0.0,
            "estimated_fidelity_gain": 0.0,
        }
        
        for synthon in synthons:
            topo_factor = self.TOPOLOGY_COOPERATIVITY.get(synthon.topology, 1.0)
            gran_factor = self.GRANULARITY_AMPLIFICATION.get(synthon.granularity, 1.0)
            
            components["topology_factors"].append({
                "synthon": synthon.name,
                "topology": synthon.topology.value,
                "factor": topo_factor,
            })
            components["granularity_factors"].append({
                "synthon": synthon.name,
                "granularity": synthon.granularity.value,
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
        if len(synthons) >= 3:
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
    def validate_axiom1_cyclic_closure(cls, synthon: Synthon) -> Dict[str, Any]:
        """
        Axiom 1: Cyclic closure amplifies fidelity (T_⋈–F rule).
        
        A synthon with T_⋈ and P_± necessarily achieves F ≥ F_dh,
        provided R_⊇ or R_⊆.
        
        Prediction: no T_⋈/P_± synthon will be assigned F_beltl.
        Falsified by: cyclic self-complementary motif with xi_CP > 10.5 nats.
        """
        is_cyclic = synthon.topology == Topology.CYCLIC_BOWTIE
        is_self_comp = synthon.polarity.is_self_complementary
        is_valid_recognition = synthon.recognition_mode in {
            RecognitionMode.NON_COVALENT,
            RecognitionMode.COVALENT,
            RecognitionMode.COVALENT_DYNAMIC,
        }
        
        # Check if axiom applies
        axiom_applies = is_cyclic and is_self_comp and is_valid_recognition
        
        if not axiom_applies:
            return {
                "axiom": "Axiom 1 (Cyclic Closure)",
                "applies": False,
                "reason": "Not a cyclic self-complementary synthon with valid R",
            }
        
        # Check prediction
        fidelity_violated = synthon.fidelity == Fidelity.LOW
        
        return {
            "axiom": "Axiom 1 (Cyclic Closure)",
            "applies": True,
            "cyclic": is_cyclic,
            "self_complementary": is_self_comp,
            "recognition_valid": is_valid_recognition,
            "fidelity": synthon.fidelity.value,
            "prediction_satisfied": not fidelity_violated,
            "violated": fidelity_violated,
            "falsification_note": (
                "AXIOM FALSIFIED" if fidelity_violated else "Axiom satisfied"
            ),
        }
    
    @classmethod
    def validate_axiom2_local_grammar_barrier(
        cls,
        synthon: Synthon,
        target_granularity: Optional[Granularity] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 2: Local grammar blocks network propagation (G_ב–Γ barrier rule).
        
        A synthon with G_ב and Γ_⊗ cannot propagate constraint beyond
        its immediate recognition pair.
        
        Prediction: no single G_ב/Γ_⊗ synthon will be found as the sole
        organizing element of a MOF, polymer, or oscillatory network.
        """
        is_local = synthon.granularity == Granularity.LOCAL
        is_specific = (
            synthon.grammar == Grammar.Gamma_corner and
            synthon.fidelity == Fidelity.HIGH
        )
        
        axiom_applies = is_local and is_specific
        
        if not axiom_applies:
            return {
                "axiom": "Axiom 2 (Local Grammar Barrier)",
                "applies": False,
                "reason": "Not a local specific synthon",
            }
        
        # Check if target granularity is achievable
        if target_granularity is None:
            can_propagate = False
        else:
            can_propagate = synthon.granularity.can_amplify_to(target_granularity)
        
        # Axiom predicts NO propagation to global
        prediction_satisfied = not can_propagate or target_granularity != Granularity.GLOBAL
        
        return {
            "axiom": "Axiom 2 (Local Grammar Barrier)",
            "applies": True,
            "local": is_local,
            "specific_grammar": is_specific,
            "can_propagate_to_global": can_propagate and target_granularity == Granularity.GLOBAL,
            "prediction_satisfied": prediction_satisfied,
            "violated": not prediction_satisfied,
        }
    
    @classmethod
    def validate_axiom3_cooperative_induction(
        cls,
        synthons: List[Synthon],
        induction_ratio: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 3: Cooperative induction superlinearity signals G_ב → G_ג transition.
        
        When induction component of E_int grows faster than linearly with
        number of recognition contacts, system has crossed from G_ב to G_ג.
        
        Prediction: any synthon array showing superlinear SAPT induction
        should be reclassified from G_ב to G_ג.
        """
        if len(synthons) < 2:
            return {
                "axiom": "Axiom 3 (Cooperative Induction)",
                "applies": False,
                "reason": "Need at least 2 synthons for cooperativity analysis",
            }
        
        # Check if all are local (candidate for transition)
        all_local = all(s.granularity == Granularity.LOCAL for s in synthons)
        
        if induction_ratio is None:
            # Estimate from synthon properties
            # Triple H-bond arrays typically have induction_ratio ~2.5-3.5
            induction_ratio = len(synthons) * 0.8  # Rough estimate
        
        # Superlinear threshold
        is_superlinear = induction_ratio > len(synthons) * 1.2
        
        # Check current granularity assignments
        granularities = set(s.granularity for s in synthons)
        
        # Axiom predicts reclassification if superlinear
        should_reclassify = is_superlinear and Granularity.LOCAL in granularities
        
        return {
            "axiom": "Axiom 3 (Cooperative Induction)",
            "applies": all_local,
            "num_synthons": len(synthons),
            "induction_ratio": induction_ratio,
            "is_superlinear": is_superlinear,
            "superlinear_threshold": len(synthons) * 1.2,
            "should_reclassify_to_mesoscale": should_reclassify,
            "current_granularities": [g.value for g in granularities],
        }
    
    @classmethod
    def validate_axiom4_sequential_grammar(
        cls,
        synthon: Synthon,
    ) -> Dict[str, Any]:
        """
        Axiom 4: Sequential grammar requires temporal or catalytic dimension.
        
        Γ_→ (ordered sequential recognition) is only physically realizable
        if the synthon possesses D_∞ or R_‡, or both.
        
        Prediction: all documented allosteric systems with ordered binding
        will contain either a conformational change (R_‡-like) or temporal component.
        """
        is_sequential = synthon.grammar == Grammar.Gamma_secstress
        
        if not is_sequential:
            return {
                "axiom": "Axiom 4 (Sequential Grammar)",
                "applies": False,
                "reason": "Not a sequential grammar",
            }
        
        has_temporal = synthon.dimensionality in (Dimensionality.D_invomega, Dimensionality.TEMPORAL)
        has_catalytic = synthon.recognition_mode in {
            RecognitionMode.DYNAMIC_CATALYTIC,
            RecognitionMode.COVALENT_DYNAMIC,
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
        synthon: Synthon,
        correlation_length: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Axiom 5: Criticality contracts the primitive basis.
        
        At criticality (G-D degeneracy, ξ → ∞), G becomes redundant given D.
        
        Prediction: a critical synthon's behavior at molecular scale fully
        predicts its behavior at supramolecular and temporal scales.
        """
        is_critical = synthon.criticality_phase == CriticalityPhase.CRITICAL
        
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
        synthon: Synthon,
        grounding_result: Optional[Any] = None,
    ) -> AxiomResult:
        """
        Axiom 6: D_∞ requires a physically grounded reset mechanism.

        Supports two reset types via ``synthon.metadata["grounding"]["reset"]["type"]``:

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
        has_temporal = Dimensionality.TEMPORAL in (
            synthon.dimensionality if isinstance(synthon.dimensionality, (list, set, tuple))
            else [synthon.dimensionality]
        )

        if not has_temporal:
            return AxiomResult(axiom=6, satisfied=True, violations=[], warnings=[])

        # ── 2. Read reset_type from structured grounding block ────────────────
        # Primary source: synthon.grounding["reset"] (persisted in catalog JSON)
        # Fallback: synthon.metadata["grounding"]["reset"] (legacy in-memory path)
        sg = getattr(synthon, "grounding", None) or {}
        reset_block = sg.get("reset", {})
        if not reset_block:
            # fallback to metadata-nested path (not persisted, but accepted in tests)
            meta_grounding = synthon.metadata.get("grounding", {}) if hasattr(synthon, "metadata") and synthon.metadata else {}
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
        ax6 = synthon.metadata.get("axiom6_grounding", {}) if hasattr(synthon, "metadata") and synthon.metadata else {}
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
        synthon: Synthon,
        grounding_result: Optional[Any] = None,
    ) -> AxiomResult:
        """
        Axiom 7: T_⋈ requires a named closing bond or interaction.
        
        A synthon assigned T_⋈ must identify the specific interaction
        or bond that closes the loop. If no closing interaction can be
        named, T_⋈ is invalid and the correct assignment is T_≫ (chain)
        or T_□ (hub/node).
        
        Falsified by: a documented T_⋈ synthon where no closing bond
        or interaction can be identified.
        
        Args:
            synthon: The synthon to validate
            grounding_result: Optional GroundingResult with justifications
            
        Returns:
            AxiomResult with violations if T_⋈ assigned without closing bond
        """
        violations = []
        warnings = []
        
        is_bowtie = synthon.topology == Topology.CYCLIC_BOWTIE
        is_cage = synthon.topology == Topology.CAGE

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
        synthon_or_synthons: Union[Synthon, List[Synthon]],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate all seven axioms for a synthon or system.
        
        Includes Axioms 1-5 (composition axioms) and Axioms 6-7 (grounding axioms).

        Returns comprehensive axiom validation report.
        """
        if isinstance(synthon_or_synthons, Synthon):
            synthons = [synthon_or_synthons]
            synthon = synthon_or_synthons
        else:
            synthons = synthon_or_synthons
            synthon = synthons[0] if synthons else None

        results = {}
        grounding_result = kwargs.get("grounding_result")

        if synthon:
            results["axiom1"] = cls.validate_axiom1_cyclic_closure(synthon)
            results["axiom2"] = cls.validate_axiom2_local_grammar_barrier(
                synthon,
                target_granularity=kwargs.get("target_granularity"),
            )
            results["axiom4"] = cls.validate_axiom4_sequential_grammar(synthon)
            results["axiom5"] = cls.validate_axiom5_criticality(
                synthon,
                correlation_length=kwargs.get("correlation_length"),
            )
            # Fix 2: Axiom 6 (temporal grounding)
            results["axiom6"] = cls.validate_axiom6_temporal_grounding(
                synthon,
                grounding_result=grounding_result,
            )
            # Fix 3: Axiom 7 (cyclic topology grounding)
            results["axiom7"] = cls.validate_axiom7_cyclic_grounding(
                synthon,
                grounding_result=grounding_result,
            )

        if len(synthons) >= 2:
            results["axiom3"] = cls.validate_axiom3_cooperative_induction(
                synthons,
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
    synthon: str


class CoreAxioms:
    """
    Cross-primitive axioms from Core.lean, enforced on Python Synthon objects.

    These are the same four axioms that are stated as `axiom` declarations in
    Imscribing Grammar/Primitives/Core.lean and enforced in Synthon.__post_init__.
    This class provides a soft-check path (returns violations rather than raising)
    useful for auditing existing catalog entries.

    Axiom A: H_invscripta -> K_teshlig
        Topological chirality implies kinetic trapping. A topology-protected
        chiral object cannot exchange without breaking a topological bond,
        so it is by definition kinetically trapped.

    Axiom B: prot >= Omega_dzlig -> chir >= H_turntwo
        Integer winding number (or stronger) requires persistent chirality.
        Omega_crtwo does NOT require H_turntwo; only Omega_dzlig and above do.

    Axiom C: D_omega <-> T_openo
        Imscriptive dimensionality and imscriptive topology are co-required.
        You cannot have one without the other (AdS/CFT, imscriptive error codes).

    Axiom D: Omega_turna -> D_omega
        Non-Abelian anyonic protection requires a imscriptive substrate.
        Anyonic braiding statistics are only topologically protected in a
        bulk-boundary encoded system.
    """

    @staticmethod
    def check(synthon: Synthon) -> List[AxiomViolation]:
        """
        Return all axiom violations for the given synthon.
        Empty list means the synthon is axiom-consistent.
        """
        v: List[AxiomViolation] = []
        name = synthon.name

        # Axiom A
        if synthon.chirality == Chirality.H_invscripta and synthon.kinetic_character != KineticChar.K_teshlig:
            v.append(AxiomViolation(
                axiom="A",
                message=(f"H_invscripta requires K_teshlig (got {synthon.kinetic_character.value})"),
                synthon=name,
            ))

        # Axiom B
        if _prot_ord(synthon.protection) >= _prot_ord(Protection.Omega_dzlig) \
                and _chir_ord(synthon.chirality) < _chir_ord(Chirality.H_turntwo):
            v.append(AxiomViolation(
                axiom="B",
                message=(
                    f"protection {synthon.protection.value} requires chirality >= H_turntwo "
                    f"(got {synthon.chirality.value})"
                ),
                synthon=name,
            ))

        # Axiom C
        d_holo = synthon.dimensionality == Dimensionality.D_holo
        t_holo = synthon.topology == Topology.T_holo
        if d_holo and not t_holo:
            v.append(AxiomViolation(
                axiom="C",
                message=f"D_omega requires T_openo (got {synthon.topology.value})",
                synthon=name,
            ))
        elif t_holo and not d_holo:
            v.append(AxiomViolation(
                axiom="C",
                message=f"T_openo requires D_omega (got {synthon.dimensionality.value})",
                synthon=name,
            ))

        # Axiom D
        if synthon.protection == Protection.Omega_turna \
                and synthon.dimensionality != Dimensionality.D_holo:
            v.append(AxiomViolation(
                axiom="D",
                message=f"Omega_turna requires D_omega (got {synthon.dimensionality.value})",
                synthon=name,
            ))

        return v

    @staticmethod
    def check_all(synthons) -> Dict[str, List[AxiomViolation]]:
        """Check a collection of synthons. Returns {name: [violations]}."""
        return {s.name: CoreAxioms.check(s) for s in synthons}

    @staticmethod
    def audit_catalog(synthons) -> Dict[str, Any]:
        """Audit report: counts, violation breakdown by axiom, offending names."""
        all_violations = CoreAxioms.check_all(synthons)
        by_axiom: Dict[str, List[str]] = {"A": [], "B": [], "C": [], "D": []}
        total = 0
        for name, viols in all_violations.items():
            for v in viols:
                by_axiom[v.axiom].append(name)
                total += 1
        return {
            "total_synthons": len(synthons),
            "total_violations": total,
            "clean": total == 0,
            "by_axiom": {k: {"count": len(v), "synthons": v} for k, v in by_axiom.items()},
        }
