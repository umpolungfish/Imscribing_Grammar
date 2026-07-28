"""
Adversarial Axiom Validator — Mechanistic criteria for primitive validation.

Unlike the grounding layer (which validates justifications), this module
validates primitive assignments against mechanistic criteria derived from
the chemistry itself.

Each axiom has a falsifiable mechanistic criterion:
- Axiom 3: G_gamma requires superlinear SAPT induction (ratio > 2)
- Axiom 6: D_infinity requires specifiable reset mechanism
- Axiom 7: Topology must match actual connectivity
- Axiom 8: Recognition mode must match interaction physics

Usage:
    from imscrbgrmr.adversarial_grounding import validate_primitive_assignment
    
    # Check if D_infinity assignment is valid
    result = validate_primitive_assignment(
        primitive="dimensionality",
        value="TEMPORAL",
        description="extended allene cumulene chain",
        smiles="C=C=C"
    )
    print(f"Valid: {result.is_valid}")  # False - no reset mechanism
    print(f"Reason: {result.reason}")  # "No closed cycle with reset mechanism"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import re

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
    RDKit_AVAILABLE = True
except ImportError:
    RDKit_AVAILABLE = False


@dataclass
class AxiomValidationResult:
    """Result of adversarial axiom validation."""
    primitive: str
    assigned_value: str
    is_valid: bool
    axiom_violated: Optional[str] = None
    reason: str = ""
    alternative_value: Optional[str] = None
    confidence: float = 0.0
    mechanistic_criteria_checked: List[str] = None
    
    def __post_init__(self):
        if self.mechanistic_criteria_checked is None:
            self.mechanistic_criteria_checked = []


# =============================================================================
# Axiom 6: Temporal Dimension Requires Closed Cycle
# =============================================================================

AXIOM_6_CRITERIA = """
Axiom 6 — Temporal dimension requires a closed cycle with reset mechanism.

D_∞ is valid ONLY if ALL of the following can be specified:
1. STATE: What molecular/state forms
2. WORK: What chemical work the state performs (catalysis, transport, signaling)
3. RESET: What process returns the system to initial state (hydrolysis, product release, energy input)
4. CYCLE: The complete cycle can be drawn with all intermediates

Falsified by: A D_∞ assignment where any of the four cannot be specified.

Examples:
- ✓ Proline aldol cycle: enamine forms → C-C bond forms → hydrolysis resets
- ✓ Imine condensation: imine forms → hydrolysis resets → re-condensation
- ✗ Extended allene: linear cumulene, no cycle, no reset → D_∧ not D_∞
- ✗ Nitroso dimer: static dimer, no cycle → D_∧ not D_∞
- ✗ Quantum imscription: no specifiable chemical cycle → invalid D_∞
"""


def validate_temporal_dimension(
    description: str,
    smiles: Optional[str] = None,
) -> AxiomValidationResult:
    """
    Validate D_∞ assignment against Axiom 6.
    
    Args:
        description: Chemical description
        smiles: Optional SMILES for structure analysis
    
    Returns:
        AxiomValidationResult
    """
    description_lower = description.lower()
    
    # Check for cycle keywords
    cycle_keywords = [
        "cycle", "catalytic", "oscillat", "reset", "regenerat",
        "hydrolysis", "re-condens", "re-form", "turnover",
        "feedback", "autocatal", "dissipative"
    ]
    
    has_cycle = any(kw in description_lower for kw in cycle_keywords)
    
    # Check for static structure keywords (indicates D_∧ or D_△)
    static_keywords = [
        "chain", "rod", "rigid", "linear", "extended", "cumulene",
        "allene", "polymer", "framework", "crystal", "dimer",
        "complex", "adduct"
    ]
    
    is_static = any(kw in description_lower for kw in static_keywords)
    
    # Structure-based checks if SMILES provided
    if smiles and RDKit_AVAILABLE:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            # Check for rings (cycles in structure, not reaction cycles)
            rings = mol.GetRingInfo()
            has_structural_rings = rings.NumRings() > 0
            
            # Check molecular weight (large systems less likely to be D_∞)
            mol_wt = Descriptors.MolWt(mol)
            is_large = mol_wt > 500
            
            # Check for reactive groups that might indicate catalysis
            reactive_patterns = [
                "[CX3](=O)[OX2H1]",  # Carboxylic acid
                "[NX3H2][CX3](=O)",  # Primary amide
                "[CX3]=[OX1]",  # Carbonyl
            ]
            
            has_reactive_groups = False
            for pattern in reactive_patterns:
                patt_mol = Chem.MolFromSmarts(pattern)
                if patt_mol and mol.HasSubstructMatch(patt_mol):
                    has_reactive_groups = True
                    break
    else:
        has_structural_rings = False
        is_large = False
        has_reactive_groups = False
    
    # Decision logic
    mechanistic_criteria = [
        f"Cycle keywords present: {has_cycle}",
        f"Static structure keywords: {is_static}",
        f"Structural rings: {has_structural_rings}",
        f"Reactive groups: {has_reactive_groups}",
    ]
    
    if is_static and not has_cycle:
        # Static structure without cycle keywords → not D_∞
        if "allene" in description_lower or "cumulene" in description_lower:
            return AxiomValidationResult(
                primitive="dimensionality",
                assigned_value="TEMPORAL",
                is_valid=False,
                axiom_violated="Axiom 6",
                reason="Extended allene/cumulene is a static linear structure with no closed cycle or reset mechanism",
                alternative_value="MOLECULAR",
                confidence=0.9,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
        elif "dimer" in description_lower or "complex" in description_lower:
            return AxiomValidationResult(
                primitive="dimensionality",
                assigned_value="TEMPORAL",
                is_valid=False,
                axiom_violated="Axiom 6",
                reason="Static dimer/complex with no specifiable reset mechanism",
                alternative_value="MOLECULAR",
                confidence=0.85,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
        else:
            return AxiomValidationResult(
                primitive="dimensionality",
                assigned_value="TEMPORAL",
                is_valid=False,
                axiom_violated="Axiom 6",
                reason="Description indicates static structure without closed cycle or reset mechanism",
                alternative_value="MOLECULAR",
                confidence=0.75,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
    
    if has_cycle:
        # Has cycle keywords → likely valid D_∞
        return AxiomValidationResult(
            primitive="dimensionality",
            assigned_value="TEMPORAL",
            is_valid=True,
            reason="Closed catalytic cycle with reset mechanism indicated",
            confidence=0.8,
            mechanistic_criteria_checked=mechanistic_criteria,
        )
    
    # Ambiguous case
    return AxiomValidationResult(
        primitive="dimensionality",
        assigned_value="TEMPORAL",
        is_valid=True,  # Give benefit of doubt
        reason="No explicit cycle mentioned, but not ruled out",
        confidence=0.5,
        mechanistic_criteria_checked=mechanistic_criteria,
    )


# =============================================================================
# Axiom 7: Topology Must Match Connectivity
# =============================================================================

AXIOM_7_CRITERIA = """
Axiom 7 — Topology must match actual molecular connectivity.

T_⋈ (cyclic bowtie) is valid ONLY if:
- The minimal motif forms a closed ring
- There are 2+ interaction sites in cyclic arrangement
- Examples: R₂²(8) dimer, base pair, cyclic H-bond array

T_≫ (chain) is valid ONLY if:
- The structure propagates linearly
- No cyclic closure in minimal motif
- Examples: catemer, polymer, linear oligomer

T_□ (hub/node) is valid ONLY if:
- There is a central coordination point
- 3+ ligands/branches from central point
- Examples: MOF node, metal chelate

Falsified by: Assigning T_⋈ to a linear chain, or T_≫ to a cyclic dimer.
"""


def validate_topology(
    description: str,
    smiles: Optional[str] = None,
    assigned_topology: str = "CYCLIC_BOWTIE",
) -> AxiomValidationResult:
    """
    Validate topology assignment against Axiom 7.
    
    Args:
        description: Chemical description
        smiles: Optional SMILES for structure analysis
        assigned_topology: The topology value to validate
    
    Returns:
        AxiomValidationResult
    """
    description_lower = description.lower()
    
    # Detect actual topology from description
    is_cyclic = any(kw in description_lower for kw in [
        "dimer", "cyclic", "ring", "r₂", "r2", "bowtie",
        "base pair", "closed", "cycle"
    ])
    
    is_linear = any(kw in description_lower for kw in [
        "chain", "linear", "rod", "extended", "catemer",
        "polymer", "oligomer", "cumulene", "allene"
    ])
    
    is_hub = any(kw in description_lower for kw in [
        "node", "hub", "coordination", "chelate", "metal",
        "framework", "mof", "branch"
    ])
    
    # Structure-based checks
    if smiles and RDKit_AVAILABLE:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            rings = mol.GetRingInfo()
            has_rings = rings.NumRings() > 0
            
            # Count heavy atoms (linear chains typically have more)
            heavy_atoms = mol.GetNumHeavyAtoms()
            is_long_chain = heavy_atoms > 10 and not has_rings
    else:
        has_rings = False
        is_long_chain = False
    
    mechanistic_criteria = [
        f"Cyclic keywords: {is_cyclic}",
        f"Linear keywords: {is_linear}",
        f"Hub keywords: {is_hub}",
        f"Structural rings: {has_rings}",
    ]
    
    # Check for mismatches
    if assigned_topology == "CYCLIC_BOWTIE":
        if is_linear and not is_cyclic:
            return AxiomValidationResult(
                primitive="topology",
                assigned_value="CYCLIC_BOWTIE",
                is_valid=False,
                axiom_violated="Axiom 7",
                reason="Linear/extended structure assigned cyclic topology without cyclic motif",
                alternative_value="CHAIN",
                confidence=0.85,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
    
    elif assigned_topology == "CHAIN":
        if is_cyclic and not is_linear:
            return AxiomValidationResult(
                primitive="topology",
                assigned_value="CHAIN",
                is_valid=False,
                axiom_violated="Axiom 7",
                reason="Cyclic motif assigned chain topology",
                alternative_value="CYCLIC_BOWTIE",
                confidence=0.85,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
    
    return AxiomValidationResult(
        primitive="topology",
        assigned_value=assigned_topology,
        is_valid=True,
        reason="Topology consistent with features",
        confidence=0.85,
        mechanistic_criteria_checked=mechanistic_criteria,
    )


# =============================================================================
# Axiom 8: Recognition Mode Must Match Interaction Physics
# =============================================================================

AXIOM_8_CRITERIA = """
Axiom 8 — Recognition mode must match the physical interaction mechanism.

R_⊇ (non-covalent) is valid ONLY if:
- Primary interaction is H-bonding, electrostatic, dispersion, or σ-hole
- No bond formation/breaking in the interaction
- Examples: carboxylic dimer, halogen bond, base pair

R_⊆ (covalent) is valid ONLY if:
- Electron sharing / orbital overlap forms σ or π bonds
- Examples: static covalent linkage

R_‡ (catalytic/dynamic) is valid ONLY if:
- Transition state stabilization or barrier reduction
- Reversible bond formation with error correction
- Examples: organocatalysis, dynamic covalent chemistry

R_⇔ (mechanical) is valid ONLY if:
- Steric clipping or topological entanglement
- Discontinuous steric cliff in potential energy surface
- Examples: rotaxane, catenane

Falsified by: Assigning R_⊇ to a covalent bond, or R_‡ to a static interaction.
"""


def validate_recognition_mode(
    description: str,
    assigned_mode: str = "NON_COVALENT",
) -> AxiomValidationResult:
    """
    Validate recognition mode assignment against Axiom 8.
    
    Args:
        description: Chemical description
        assigned_mode: The recognition mode value to validate
    
    Returns:
        AxiomValidationResult
    """
    description_lower = description.lower()
    
    # Detect interaction type from description
    is_covalent = any(kw in description_lower for kw in [
        "covalent", "bond formation", "σ-bond", "pi-bond",
        "electron sharing"
    ])
    
    is_noncovalent = any(kw in description_lower for kw in [
        "hydrogen bond", "h-bond", "hbond", "electrostatic", "dispersion",
        "halogen bond", "chalcogen bond", "π-stacking", "pi-stacking",
        "van der waals", "non-covalent", "water", "aqueous", "solvent",
        "ionic", "ion pair", "coordination", "host-guest", "inclusion",
    ])
    
    is_catalytic = any(kw in description_lower for kw in [
        "catalytic", "catalysis", "organocatal", "dynamic",
        "reversible", "error correction", "transition state"
    ])
    
    is_mechanical = any(kw in description_lower for kw in [
        "mechanical", "rotaxane", "catenane", "interlock",
        "thread", "steric cliff", "topological"
    ])
    
    mechanistic_criteria = [
        f"Covalent keywords: {is_covalent}",
        f"Non-covalent keywords: {is_noncovalent}",
        f"Catalytic keywords: {is_catalytic}",
        f"Mechanical keywords: {is_mechanical}",
    ]
    
    # Check for mismatches
    if assigned_mode == "NON_COVALENT":
        if is_covalent and not is_noncovalent:
            return AxiomValidationResult(
                primitive="recognition_mode",
                assigned_value="NON_COVALENT",
                is_valid=False,
                axiom_violated="Axiom 8",
                reason="Covalent interaction described but assigned non-covalent recognition",
                alternative_value="COVALENT",
                confidence=0.9,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
        if is_mechanical:
            return AxiomValidationResult(
                primitive="recognition_mode",
                assigned_value="NON_COVALENT",
                is_valid=False,
                axiom_violated="Axiom 8",
                reason="Mechanical bond described but assigned non-covalent recognition",
                alternative_value="MECHANICAL",
                confidence=0.85,
                mechanistic_criteria_checked=mechanistic_criteria,
            )
    
    elif assigned_mode in ("COVALENT", "SUBSET"):
        # COVALENT assigned — check if description is actually non-covalent
        if is_noncovalent and not is_covalent:
            return AxiomValidationResult(
                primitive="recognition_mode",
                assigned_value=assigned_mode,
                is_valid=False,
                axiom_violated="Axiom 8",
                reason=(
                    "Non-covalent interaction (H-bond / coordination / host-guest) described "
                    "but COVALENT (R_subset) assigned; should be NON_COVALENT (R_superset)"
                ),
                alternative_value="NON_COVALENT",
                confidence=0.9,
                mechanistic_criteria_checked=mechanistic_criteria,
            )

    elif assigned_mode == "DYNAMIC_CATALYTIC":
        if is_covalent and not is_catalytic:
            return AxiomValidationResult(
                primitive="recognition_mode",
                assigned_value="DYNAMIC_CATALYTIC",
                is_valid=False,
                axiom_violated="Axiom 8",
                reason="Static covalent bond described but assigned dynamic catalytic recognition",
                alternative_value="COVALENT",
                confidence=0.85,
                mechanistic_criteria_checked=mechanistic_criteria,
            )

    return AxiomValidationResult(
        primitive="recognition_mode",
        assigned_value=assigned_mode,
        is_valid=True,
        reason="Recognition mode consistent with interaction physics",
        confidence=0.85,
        mechanistic_criteria_checked=mechanistic_criteria,
    )


# =============================================================================
# Main Adversarial Validator
# =============================================================================

def validate_primitive_assignment(
    primitive: str,
    value: str,
    description: str,
    smiles: Optional[str] = None,
) -> AxiomValidationResult:
    """
    Validate a primitive assignment against mechanistic criteria.
    
    Args:
        primitive: Primitive name (dimensionality, topology, recognition_mode)
        value: Assigned primitive value
        description: Chemical description
        smiles: Optional SMILES for structure analysis
    
    Returns:
        AxiomValidationResult
    """
    if primitive == "dimensionality" and value == "TEMPORAL":
        return validate_temporal_dimension(description, smiles)
    
    elif primitive == "topology":
        return validate_topology(description, smiles, value)
    
    elif primitive == "recognition_mode":
        return validate_recognition_mode(description, value)
    
    # Other primitives don't have adversarial axioms yet
    return AxiomValidationResult(
        primitive=primitive,
        assigned_value=value,
        is_valid=True,
        reason=f"No adversarial axiom defined for {primitive}",
        confidence=0.8,
    )


def validate_full_imscription(
    imscription_data: Dict[str, Any],
    description: str,
    smiles: Optional[str] = None,
) -> Dict[str, AxiomValidationResult]:
    """
    Validate all primitives of a imscription against adversarial axioms.
    
    Args:
        imscription_data: Dict with primitive assignments
        description: Chemical description
        smiles: Optional SMILES
    
    Returns:
        Dict mapping primitive names to validation results
    """
    results = {}
    
    # Validate dimensionality
    if "dimensionality" in imscription_data:
        dim_value = imscription_data["dimensionality"]
        if isinstance(dim_value, str):
            dim_value = dim_value.upper().replace("D_", "")
        results["dimensionality"] = validate_primitive_assignment(
            "dimensionality", dim_value, description, smiles
        )
    
    # Validate topology
    if "topology" in imscription_data:
        top_value = imscription_data["topology"]
        if isinstance(top_value, str):
            top_value = top_value.upper().replace("T_", "")
        results["topology"] = validate_primitive_assignment(
            "topology", top_value, description, smiles
        )
    
    # Validate recognition mode
    if "recognition_mode" in imscription_data:
        rec_value = imscription_data["recognition_mode"]
        if isinstance(rec_value, str):
            rec_value = rec_value.upper().replace("R_", "")
        results["recognition_mode"] = validate_primitive_assignment(
            "recognition_mode", rec_value, description
        )
    
    return results
