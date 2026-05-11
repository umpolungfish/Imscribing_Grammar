"""
RDKit-based ΔG estimation, structure validation, and structural flag extraction.

This module provides:
1. SMILES-based ΔG estimation using group additivity
2. Structure validation for imscription chemical descriptions
3. Automatic ΔG justification generation
4. Structural flag extraction for PrimitiveAssignmentEngine (D, T, R, G flags)

Usage:
    from imscrbgrmr.rdkit_utils import estimate_delta_g_from_smiles, smiles_to_structural_flags

    # Estimate ΔG from SMILES
    result = estimate_delta_g_from_smiles("CC(=O)O", "acetic acid dimer")
    print(f"Estimated ΔG: {result.delta_g} kJ/mol")

    # Extract structural flags for assignment engine
    flags = smiles_to_structural_flags("C1C2CC3CC1CC(C2)C3")  # adamantane
    print(flags.has_cage_geometry)  # True

    # Full measurements dict (ΔG + structural flags) for assign_all()
    m = smiles_to_measurements("CC(=O)Nc1ccc(O)cc1")
    from imscrbgrmr.assignment import PrimitiveAssignmentEngine
    result = PrimitiveAssignmentEngine().assign_all(m)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import re

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
    from rdkit.Chem import AllChem
    RDKit_AVAILABLE = True
except ImportError:
    RDKit_AVAILABLE = False


@dataclass
class DeltaGEstimationResult:
    """Result of ΔG estimation."""
    delta_g: float  # Estimated ΔG in kJ/mol
    method: str  # Estimation method used
    justification: str  # Machine-generated justification
    confidence: float  # 0.0-1.0 confidence in estimate
    smiles: Optional[str] = None
    molecular_formula: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


# Group contribution values for ΔG estimation (simplified model)
# Values in kJ/mol, approximate binding/free energies
GROUP_CONTRIBUTIONS = {
    # Hydrogen bonding groups
    "carboxylic_acid": -52.0,  # R₂²(8) dimer
    "amide_primary": -40.0,  # Primary amide dimer
    "amide_secondary": -35.0,  # Secondary amide
    "alcohol": -25.0,  # Alcohol dimer
    "amine_primary": -15.0,  # Primary amine
    "amine_secondary": -12.0,  # Secondary amine
    
    # Halogen bonds
    "iodine_sigma_hole": -28.0,  # I···N halogen bond
    "bromine_sigma_hole": -20.0,  # Br···N
    "chlorine_sigma_hole": -12.0,  # Cl···N
    
    # Chalcogen bonds
    "sulfur_sigma_hole": -15.0,  # S···N
    
    # Base pairs (DNA/RNA)
    "adenine_thymine": -50.0,  # A·T Watson-Crick
    "guanine_cytosine": -80.0,  # G·C Watson-Crick (3 H-bonds)
    
    # Metal coordination
    "zinc_chelate": -90.0,  # Zn²⁺ bidentate
    "zinc_monodentate": -45.0,  # Zn²⁺ monodentate
    
    # Triple H-bond arrays
    "dad_ada_array": -95.0,  # DAD·ADA triple H-bond
    
    # Default for unknown
    "unknown": -30.0,  # Generic non-covalent
}

# SMARTS patterns for group detection
GROUP_SMARTS = {
    "carboxylic_acid": "[CX3](=O)[OX2H1]",
    "amide_primary": "[NX3H2][CX3](=O)",
    "amide_secondary": "[NX3H1][CX3](=O)",
    "alcohol": "[OX2H1][CX4]",
    "amine_primary": "[NX3H2][CX4]",
    "amine_secondary": "[NX3H1][CX4]",
    "iodine": "[I]",
    "bromine": "[Br]",
    "chlorine": "[Cl]",
    "sulfur": "[S]",
    "zinc": "[Zn+2]",
    "pyridine": "n1ccccc1",
    "bipyridine": "n1ccccc1-c2cccnc2",
}


def estimate_delta_g_from_smiles(
    smiles: str,
    description: str = "",
    interaction_type: str = "non-covalent",
) -> DeltaGEstimationResult:
    """
    Estimate ΔG from SMILES using group additivity.
    
    Args:
        smiles: SMILES string of the molecular system
        description: Optional chemical description
        interaction_type: Type of interaction (non-covalent, covalent, etc.)
    
    Returns:
        DeltaGEstimationResult with estimated ΔG and justification
    """
    if not RDKit_AVAILABLE:
        return DeltaGEstimationResult(
            delta_g=-30.0,
            method="fallback",
            justification="RDKit not available, using default estimate",
            confidence=0.3,
            smiles=smiles,
            warnings=["RDKit not available"],
        )
    
    # Parse SMILES
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return DeltaGEstimationResult(
            delta_g=-30.0,
            method="fallback",
            justification=f"Invalid SMILES '{smiles}', using default estimate",
            confidence=0.2,
            smiles=smiles,
            warnings=[f"Invalid SMILES: {smiles}"],
        )
    
    # Detect functional groups
    detected_groups = []
    for group_name, smarts in GROUP_SMARTS.items():
        pattern = Chem.MolFromSmarts(smarts)
        if pattern is None:
            continue
        matches = mol.GetSubstructMatches(pattern)
        if matches:
            detected_groups.append((group_name, len(matches)))
    
    # Estimate ΔG from detected groups
    if detected_groups:
        # Use the strongest interaction group
        best_group = None
        best_energy = 0.0
        for group_name, count in detected_groups:
            energy = GROUP_CONTRIBUTIONS.get(group_name, -30.0)
            if energy < best_energy:  # More negative = stronger
                best_energy = energy
                best_group = (group_name, count)
        
        if best_group:
            group_name, count = best_group
            delta_g = GROUP_CONTRIBUTIONS.get(group_name, -30.0)
            
            # Adjust for multiplicity if applicable
            if count > 1 and group_name in ["carboxylic_acid", "amide_primary"]:
                # Dimerization already accounted for in group value
                pass
            
            justification = (
                f"Group additivity estimate from RDKit structure analysis. "
                f"Detected {count}× {group_name.replace('_', ' ')} "
                f"(SMARTS match in {smiles}). "
                f"Reference value: {delta_g} kJ/mol from QUANTIG.md "
                f"Transformation data."
            )
            
            return DeltaGEstimationResult(
                delta_g=delta_g,
                method="group_additivity",
                justification=justification,
                confidence=0.7 if len(detected_groups) == 1 else 0.6,
                smiles=smiles,
                molecular_formula=Chem.rdMolDescriptors.CalcMolFormula(mol),
            )
    
    # Fallback: estimate from molecular properties
    return _estimate_from_properties(mol, smiles, description)


def _estimate_from_properties(
    mol,
    smiles: str,
    description: str = "",
) -> DeltaGEstimationResult:
    """Estimate ΔG from molecular properties when group detection fails."""
    
    # Calculate molecular descriptors
    mol_wt = Descriptors.MolWt(mol)
    hba = rdMolDescriptors.CalcNumHBA(mol)
    hbd = rdMolDescriptors.CalcNumHBD(mol)
    tpsa = Descriptors.TPSA(mol)
    
    # Simple heuristic based on H-bonding capacity
    hbond_score = hba + hbd
    
    if hbond_score >= 4:
        # Strong H-bonding system
        delta_g = -50.0
        method = "hbond_heuristic_strong"
    elif hbond_score >= 2:
        # Moderate H-bonding
        delta_g = -35.0
        method = "hbond_heuristic_moderate"
    else:
        # Weak interaction
        delta_g = -20.0
        method = "hbond_heuristic_weak"
    
    # Adjust for molecular weight (larger systems typically have stronger interactions)
    if mol_wt > 300:
        delta_g -= 10.0
    elif mol_wt > 150:
        delta_g -= 5.0
    
    justification = (
        f"Property-based estimate from RDKit descriptors. "
        f"Molecular weight: {mol_wt:.1f} Da, "
        f"H-bond acceptors: {hba}, donors: {hbd}, "
        f"TPSA: {tpsa:.1f} Å². "
        f"H-bond score: {hbond_score} → {method}. "
        f"Estimated ΔG = {delta_g} kJ/mol."
    )
    
    return DeltaGEstimationResult(
        delta_g=delta_g,
        method=method,
        justification=justification,
        confidence=0.5,
        smiles=smiles,
        molecular_formula=Chem.rdMolDescriptors.CalcMolFormula(mol),
    )


def validate_imscription_structure(
    imscription_description: str,
    smiles: str,
) -> Tuple[bool, str]:
    """
    Validate that a SMILES structure matches the imscription description.
    
    Args:
        imscription_description: Natural language description
        smiles: SMILES string to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not RDKit_AVAILABLE:
        return True, "RDKit not available, skipping structure validation"
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False, f"Invalid SMILES: {smiles}"
    
    # Check for key features mentioned in description
    description_lower = imscription_description.lower()
    
    # Check for aromatic systems
    if "aromatic" in description_lower or "ring" in description_lower:
        rings = mol.GetRingInfo()
        if rings.NumRings() == 0:
            return False, "Description mentions rings but structure has none"
    
    # Check for specific elements
    element_checks = {
        "chlor": lambda m: any(a.GetAtomicNum() == 17 for a in m.GetAtoms()),
        "brom": lambda m: any(a.GetAtomicNum() == 35 for a in m.GetAtoms()),
        "iod": lambda m: any(a.GetAtomicNum() == 53 for a in m.GetAtoms()),
        "sulfur": lambda m: any(a.GetAtomicNum() == 16 for a in m.GetAtoms()),
        "zinc": lambda m: any(a.GetAtomicNum() == 30 for a in m.GetAtoms()),
    }
    
    for keyword, check in element_checks.items():
        if keyword in description_lower:
            if not check(mol):
                return False, f"Description mentions {keyword} but structure has none"
    
    return True, "Structure validation passed"


def generate_rdkit_grounding(
    smiles: str,
    description: str = "",
) -> Dict[str, Any]:
    """
    Generate complete RDKit-based grounding for a imscription.
    
    Args:
        smiles: SMILES string
        description: Chemical description
    
    Returns:
        Dict with ΔG value, justification, and structure validation
    """
    # Estimate ΔG
    delta_g_result = estimate_delta_g_from_smiles(smiles, description)
    
    # Validate structure
    is_valid, validation_msg = validate_imscription_structure(description, smiles)
    
    return {
        "delta_g_value": delta_g_result.delta_g,
        "delta_g_justification": delta_g_result.justification,
        "delta_g_method": delta_g_result.method,
        "delta_g_confidence": delta_g_result.confidence,
        "structure_valid": is_valid,
        "structure_message": validation_msg,
        "smiles": smiles,
        "molecular_formula": delta_g_result.molecular_formula,
        "warnings": delta_g_result.warnings,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Structural flag extraction  (feeds PrimitiveAssignmentEngine.assign_all)
# ══════════════════════════════════════════════════════════════════════════════

# SMARTS for covalent warheads (electrophilic, form covalent bonds with nucleophiles)
_COVALENT_WARHEAD_SMARTS = {
    "acrylamide":        "C=CC(=O)[NX3]",
    "vinyl_sulfone":     "C=C[SX4](=O)(=O)",
    "epoxide":           "[C;R1]1[O;R1][C;R1]1",
    "chloroacetamide":   "ClCC(=O)[NX3]",
    "aldehyde":          "[CH1X3](=O)",   # also reversible
    "alpha_beta_enone":  "[CX3](=O)[CX3]=[CX3]",
    "maleimide":         "N1C(=O)C=CC1=O",
}

# SMARTS for *reversible* covalent warheads (subset of above + others)
_REVERSIBLE_WARHEAD_SMARTS = {
    "aldehyde":          "[CH1X3](=O)",
    "boronic_acid":      "[BX3](O)O",
    "disulfide":         "[SX2][SX2]",
    "nitrile":           "C#N",
    "cyanamide":         "N[CX2]#N",
}

# SMARTS for self-complementary H-bond arrays (DAD or ADA patterns)
# Split into "specific" (triggers gamma_specific_smarts → SELECTIVE_AND regardless of
# binding-site count) and "moderate" (is_self_complementary only; Γ uses site-count rule).
_SELF_COMPLEMENTARY_SMARTS = {
    # Carboxylic acid — forms R2^2(8) DAD···ADA dimer with itself
    # Moderate: COOH alone is selective, but other groups on the same molecule can make it broad.
    "carboxylic_acid":   "[CX3](=O)[OX2H1]",
    # Barbiturate / uracil-like DAD array (NH–C=O–NH, both aromatic and aliphatic)
    "barbiturate_dad":   "[#7H][#6](=O)[#7H]",
    # Cyanuric acid ADA (aromatic tautomer) — hydroxytriazine
    "cyanurate_ada":     "c1nc(O)nc(O)n1",
    # Melamine DAD (amino-triazine)
    "melamine_dad":      "c1nc(N)nc(N)n1",
    # Isocyanuric acid / barbiturate aliphatic variant
    "isocyanurate":      "[NH]C(=O)NC(=O)N",
    # Uracil/thymine
    "uracil":            "O=C1CC(=O)[NH]C([NH]1)",
}

# Subset of the above for which matching guarantees SELECTIVE Γ regardless of
# total binding-site count.  Carboxylic acid is excluded because it appears on
# multifunctional molecules (amino acids, peptides) that are NOT selective.
_SPECIFIC_COMPLEMENTARY_SMARTS = {
    k: v for k, v in _SELF_COMPLEMENTARY_SMARTS.items()
    if k != "carboxylic_acid"
}


@dataclass
class StructuralFlags:
    """
    Structural flags extracted from SMILES for use with PrimitiveAssignmentEngine.

    D flags
    -------
    is_single_molecule : True when SMILES is a single connected fragment
    is_assembly        : True when SMILES has multiple disconnected fragments (complex, salt, etc.)
    is_catalytic_cycle : Always False from 2D SMILES — requires functional annotation
    is_holographic     : Always False from 2D SMILES — requires scale-collapse annotation

    T flags
    -------
    has_cycle          : True when a macrocyclic ring (≥ 12 atoms) is present
    is_self_complementary : True when a known DAD/ADA H-bond array is detected
    has_cage_geometry  : True when ≥ 2 bridgehead atoms AND ≥ 3 rings (adamantane, cubane, etc.)
    has_braid_statistics: Always False from 2D SMILES — requires catenane/rotaxane topology
    n_binding_sites    : Estimated from H-bond donors + acceptors + metal centers + aromatic rings
    partner_count      : Set to 1 (unknown from single-component SMILES)

    R flags
    -------
    is_covalent        : True when an electrophilic warhead is detected
    is_reversible      : True when the warhead is known to be reversible

    G
    --
    scale_nm           : Estimated molecular diameter from heavy-atom count (rough)

    Metadata
    --------
    n_heavy_atoms, n_rings, n_macrocycles, detected_features
    """
    # D
    is_single_molecule: bool = True
    is_assembly: bool = False
    is_catalytic_cycle: bool = False
    is_holographic: bool = False
    # T
    has_cycle: bool = False
    is_self_complementary: bool = False
    has_cage_geometry: bool = False
    has_braid_statistics: bool = False
    n_binding_sites: int = 1
    partner_count: int = 1
    # R
    is_covalent: bool = False
    is_reversible: bool = False
    is_mechanical: bool = False
    is_catalytic: bool = False
    # P  (partner symmetry)
    partners_identical: bool = False
    has_pseudosymmetry: bool = False
    # Γ  (selectivity proxy — None means insufficient evidence, don't assign)
    n_compatible_partners: Optional[int] = None
    n_total_possible_partners: Optional[int] = None
    gamma_specific_smarts: bool = False   # True when a named DAD/ADA pattern matched
    # G
    scale_nm: float = 0.5
    # metadata
    n_heavy_atoms: int = 0
    n_rings: int = 0
    n_macrocycles: int = 0
    n_hbd: int = 0
    n_hba: int = 0
    detected_features: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def smiles_to_structural_flags(smiles: str) -> StructuralFlags:
    """
    Extract structural flags from a SMILES string using RDKit.

    What RDKit can determine
    ------------------------
    ✅ Fragment count → is_single_molecule / is_assembly
    ✅ Macrocyclic rings (≥12 atoms) → has_cycle
    ✅ Bridgehead atoms + ring count → has_cage_geometry
    ✅ Known DAD/ADA SMARTS → is_self_complementary
    ✅ Electrophilic warheads → is_covalent / is_reversible
    ✅ HBD + HBA + aromatic rings → n_binding_sites
    ✅ Heavy-atom diameter estimate → scale_nm
    ✅ Canonical fragment identity → partners_identical / has_pseudosymmetry (P)
    ✅ Selectivity proxy from binding-site count → n_compatible/n_total (Γ heuristic)

    What cannot be determined from 2D SMILES
    -----------------------------------------
    ✗ is_catalytic_cycle — requires mechanistic annotation
    ✗ is_holographic — requires scale annotation
    ✗ has_braid_statistics — requires catenane/rotaxane topology graph
    ✗ partner_count — requires interaction database
    ✗ is_mechanical / is_catalytic — requires mechanistic annotation
    ✗ K (activation barrier) — estimated post-hoc from R via assign_K_from_recognition_mode

    Returns a StructuralFlags dataclass with is_boundary-aware defaults
    for anything that cannot be determined.
    """
    if not RDKit_AVAILABLE:
        f = StructuralFlags()
        f.warnings.append("RDKit not available — all flags set to defaults")
        return f

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        f = StructuralFlags()
        f.warnings.append(f"Invalid SMILES '{smiles}' — all flags set to defaults")
        return f

    features: List[str] = []
    warnings: List[str] = []

    # ── Fragment count → D flags ──────────────────────────────────────────────
    frags = Chem.GetMolFrags(mol)
    n_frags = len(frags)
    is_single_molecule = (n_frags == 1)
    is_assembly = (n_frags > 1)
    if is_assembly:
        features.append(f"multi-fragment SMILES ({n_frags} components) → is_assembly")

    # ── Macrocyclic rings → T has_cycle ──────────────────────────────────────
    ring_info = mol.GetRingInfo()
    atom_rings = ring_info.AtomRings()
    n_rings = ring_info.NumRings()
    macrocycles = [r for r in atom_rings if len(r) >= 12]
    n_macrocycles = len(macrocycles)
    has_cycle = n_macrocycles > 0
    if has_cycle:
        sizes = [len(r) for r in macrocycles]
        features.append(f"macrocycle(s) detected: ring sizes {sizes} → has_cycle")

    # ── Cage geometry → T has_cage_geometry ──────────────────────────────────
    n_bridgeheads = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
    has_cage_geometry = (n_bridgeheads >= 2 and n_rings >= 3)
    if has_cage_geometry:
        features.append(
            f"{n_bridgeheads} bridgehead atoms, {n_rings} rings → has_cage_geometry"
        )

    # ── Self-complementary H-bond arrays ─────────────────────────────────────
    is_self_complementary = False
    for name, smarts in _SELF_COMPLEMENTARY_SMARTS.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat is not None and mol.HasSubstructMatch(pat):
            is_self_complementary = True
            features.append(f"self-complementary pattern '{name}' → is_self_complementary")
            break

    # Fallback: perfectly symmetric HBD == HBA >= 2 (conservative proxy)
    if not is_self_complementary:
        n_hbd_check = rdMolDescriptors.CalcNumHBD(mol)
        n_hba_check = rdMolDescriptors.CalcNumHBA(mol)
        if n_hbd_check >= 2 and n_hbd_check == n_hba_check:
            is_self_complementary = True
            features.append(
                f"symmetric HBD=HBA={n_hbd_check} ≥ 2 → is_self_complementary (proxy)"
            )

    # Inter-fragment complementarity: for multi-component SMILES, check whether
    # each fragment carries both H-bond donors and acceptors — the signature of a
    # complementary pair (e.g. A:T base pair, melamine:cyanuric acid, DAD:ADA arrays).
    if not is_self_complementary and n_frags >= 2:
        frag_parsed = Chem.GetMolFrags(mol, asMols=True)
        if len(frag_parsed) >= 2:
            each_has_donor    = all(rdMolDescriptors.CalcNumHBD(f) >= 1 for f in frag_parsed)
            each_has_acceptor = all(rdMolDescriptors.CalcNumHBA(f) >= 1 for f in frag_parsed)
            if each_has_donor and each_has_acceptor:
                is_self_complementary = True
                features.append(
                    "inter-fragment: each component has ≥1 HBD and ≥1 HBA → complementary pair"
                )

    # ── P: partner symmetry ───────────────────────────────────────────────────
    # Re-use frag_parsed computed above if available (multi-fragment case).
    # For single molecules, self-complementary pattern means the molecule dimerises
    # with an identical copy of itself → partners_identical.
    partners_identical = False
    has_pseudosymmetry = False

    if n_frags >= 2:
        # Get per-fragment mols (may have been computed above; recompute safely)
        _frags_parsed = Chem.GetMolFrags(mol, asMols=True)
        canonical_smiles = [Chem.MolToSmiles(f) for f in _frags_parsed]
        if len(set(canonical_smiles)) == 1:
            partners_identical = True
            features.append("identical fragments detected → partners_identical")
        else:
            # Pseudosymmetry: different SMILES but same (HBD, HBA) fingerprint
            hbdhba = [
                (rdMolDescriptors.CalcNumHBD(f), rdMolDescriptors.CalcNumHBA(f))
                for f in _frags_parsed
            ]
            if len(set(hbdhba)) == 1 and hbdhba[0] != (0, 0):
                has_pseudosymmetry = True
                features.append(
                    f"fragments differ in SMILES but share HBD/HBA={hbdhba[0]} → has_pseudosymmetry"
                )
    else:
        # Single molecule: self-complementary → it dimerises with an identical copy
        if is_self_complementary:
            partners_identical = True
            features.append("self-complementary single molecule → partners_identical (homodimer)")

    # ── Γ: selectivity proxy ─────────────────────────────────────────────────
    # Only assign when structural evidence is strong enough.
    # Rule: specific DAD/ADA SMARTS match (not just HBD==HBA proxy) AND
    #       n_binding_sites ≤ 5 → SELECTIVE_AND (ratio 0.05–0.10)
    # Rule: n_binding_sites ≥ 7 OR (assembly, not self-complementary) → BROAD_OR (ratio ~0.30)
    # Otherwise: leave None → undetermined in assign_all.
    # gamma_specific: True when a high-specificity DAD/ADA SMARTS matches
    # (carboxylic acid excluded — too promiscuous on multifunctional molecules)
    gamma_specific_smarts = False
    if is_self_complementary:
        for sm in _SPECIFIC_COMPLEMENTARY_SMARTS.values():
            p = Chem.MolFromSmarts(sm)
            if p is not None and mol.HasSubstructMatch(p):
                gamma_specific_smarts = True
                break
    n_compatible_partners: Optional[int] = None
    n_total_possible_partners: Optional[int] = None
    _gamma_specific = gamma_specific_smarts

    # ── Covalent warhead detection → R flags ─────────────────────────────────
    is_covalent = False
    is_reversible = False
    for name, smarts in _COVALENT_WARHEAD_SMARTS.items():
        pat = Chem.MolFromSmarts(smarts)
        if pat is not None and mol.HasSubstructMatch(pat):
            is_covalent = True
            features.append(f"covalent warhead '{name}' → is_covalent")
            # Check if this warhead is also reversible
            if name in _REVERSIBLE_WARHEAD_SMARTS:
                is_reversible = True
                features.append(f"  warhead '{name}' is reversible → is_reversible")
            break

    if not is_covalent:
        # Check reversible-only warheads (boronic acid, disulfide) not in covalent list
        for name, smarts in _REVERSIBLE_WARHEAD_SMARTS.items():
            if name in _COVALENT_WARHEAD_SMARTS:
                continue  # already checked
            pat = Chem.MolFromSmarts(smarts)
            if pat is not None and mol.HasSubstructMatch(pat):
                is_covalent = True
                is_reversible = True
                features.append(
                    f"reversible covalent group '{name}' → is_covalent + is_reversible"
                )
                break

    # ── n_binding_sites estimate ──────────────────────────────────────────────
    # Count distinct pharmacophore contributions:
    #   H-bond sites (donors + acceptors, capped at 5 each to avoid double-counting),
    #   aromatic ring faces, metal centres
    n_hbd = rdMolDescriptors.CalcNumHBD(mol)
    n_hba = rdMolDescriptors.CalcNumHBA(mol)
    n_aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    n_metals = sum(
        1 for a in mol.GetAtoms()
        if a.GetAtomicNum() in {26, 27, 28, 29, 30, 46, 47, 78, 79}  # Fe Co Ni Cu Zn Pd Ag Pt Au
    )
    # Each H-bond donor and acceptor counts as one site; aromatic rings and metals add to it.
    # Cap individual contributions to avoid runaway counts on large molecules.
    n_binding_sites = min(n_hbd, 5) + min(n_hba, 5) + min(n_aromatic_rings, 3) + n_metals
    n_binding_sites = max(1, n_binding_sites)  # floor at 1

    # ── Γ finalisation (now that n_binding_sites is known) ────────────────────
    # Selective (ratio ≤ 0.10): specific named DAD/ADA pattern AND few binding sites
    # Broad    (ratio ≥ 0.30): many binding sites OR non-specific multi-fragment
    # None: insufficient evidence → left undetermined in assign_all
    TOTAL = 20   # synthetic denominator — large enough to give stable ratios
    if _gamma_specific:
        # High-specificity DAD/ADA SMARTS matched: the binding sites ARE the
        # complementary array → SELECTIVE_AND regardless of total binding-site count.
        n_compatible_partners = 2       # ratio = 0.10 → SELECTIVE_AND
        n_total_possible_partners = TOTAL
        features.append(
            f"named complementary array matched → Γ SELECTIVE_AND (ratio~0.10)"
        )
    elif is_self_complementary and not _gamma_specific and n_hbd <= 1:
        # Carboxylic acid (or similar) is the sole H-bond donor → COOH-driven selectivity.
        # Even with additional acceptors/rings (aspirin, benzoic acid), the recognition
        # is dominated by the COOH DAD array.
        n_compatible_partners = 2       # ratio = 0.10 → SELECTIVE_AND
        n_total_possible_partners = TOTAL
        features.append(
            f"COOH as sole donor (HBD={n_hbd}) → Γ estimated SELECTIVE_AND (ratio~0.10)"
        )
    elif (n_binding_sites >= 7
          or (is_assembly and not is_self_complementary)
          or (is_self_complementary and not _gamma_specific and n_hbd >= 2)):
        n_compatible_partners = 7       # ratio = 0.35 → BROAD_OR
        n_total_possible_partners = TOTAL
        features.append(
            f"n_binding_sites={n_binding_sites} or broad assembly "
            f"→ Γ estimated BROAD_OR (ratio~0.35)"
        )
    # else: None / None → undetermined

    # ── Scale estimate (nm) ───────────────────────────────────────────────────
    n_heavy_atoms = mol.GetNumHeavyAtoms()
    # Rough molecular diameter assuming spherical, density ≈ 1.3 g/cm³:
    #   V = MW / (ρ·NA) → r = (3V/4π)^(1/3)
    # Simpler empirical: d(nm) ≈ 0.12 * n_heavy_atoms^(1/3) + 0.05
    scale_nm = round(0.12 * (n_heavy_atoms ** (1 / 3)) + 0.05, 3)

    # Flag if assembly — use fragment-weighted scale
    if is_assembly:
        n_atoms_per_frag = n_heavy_atoms / n_frags
        scale_nm = round(0.12 * (n_atoms_per_frag ** (1 / 3)) + 0.05, 3)
        warnings.append(
            "Multi-fragment SMILES: scale_nm computed per fragment; "
            "assembly scale may be much larger — provide scale_nm manually if known"
        )

    return StructuralFlags(
        is_single_molecule=is_single_molecule,
        is_assembly=is_assembly,
        is_catalytic_cycle=False,
        is_holographic=False,
        has_cycle=has_cycle,
        is_self_complementary=is_self_complementary,
        has_cage_geometry=has_cage_geometry,
        has_braid_statistics=False,
        n_binding_sites=n_binding_sites,
        partner_count=1,
        is_covalent=is_covalent,
        is_reversible=is_reversible,
        is_mechanical=False,
        is_catalytic=False,
        partners_identical=partners_identical,
        has_pseudosymmetry=has_pseudosymmetry,
        n_compatible_partners=n_compatible_partners,
        n_total_possible_partners=n_total_possible_partners,
        gamma_specific_smarts=gamma_specific_smarts,
        scale_nm=scale_nm,
        n_heavy_atoms=n_heavy_atoms,
        n_rings=n_rings,
        n_macrocycles=n_macrocycles,
        n_hbd=n_hbd,
        n_hba=n_hba,
        detected_features=features,
        warnings=warnings,
    )


def smiles_to_measurements(smiles: str, description: str = "") -> Dict[str, Any]:
    """
    Combine ΔG estimation + structural flag extraction into a single
    measurements dict ready for PrimitiveAssignmentEngine.assign_all().

    Keys returned (all optional in assign_all):
        delta_g_kj              — from group additivity / property heuristic
        scale_nm                — estimated molecular diameter
        is_single_molecule, is_assembly, is_catalytic_cycle, is_holographic
        has_cycle, is_self_complementary, has_cage_geometry, has_braid_statistics
        n_binding_sites, partner_count
        is_covalent, is_reversible, is_mechanical, is_catalytic
        partners_identical, has_pseudosymmetry    (P — from fragment identity)
        n_compatible_partners, n_total_possible_partners  (Γ — structural proxy;
            only present when evidence is sufficient, otherwise absent → undetermined)
        _smiles_source          — passthrough metadata

    Keys NOT populated (require external data):
        delta_g_ddagger_kj  — activation barrier (K assigned post-hoc from R)
        pathway_multiplicity
        n_components        — use for G if molecular-count is known
        varma_score, gd_degeneracy, has_scale_free
        is_quantum
    """
    dg = estimate_delta_g_from_smiles(smiles, description)
    sf = smiles_to_structural_flags(smiles)

    m: Dict[str, Any] = {
        "delta_g_kj":           dg.delta_g,
        "scale_nm":             sf.scale_nm,
        # D
        "is_single_molecule":   sf.is_single_molecule,
        "is_assembly":          sf.is_assembly,
        "is_catalytic_cycle":   sf.is_catalytic_cycle,
        "is_holographic":       sf.is_holographic,
        # T
        "has_cycle":            sf.has_cycle,
        "is_self_complementary": sf.is_self_complementary,
        "has_cage_geometry":    sf.has_cage_geometry,
        "has_braid_statistics": sf.has_braid_statistics,
        "n_binding_sites":      sf.n_binding_sites,
        "partner_count":        sf.partner_count,
        # R
        "is_covalent":          sf.is_covalent,
        "is_reversible":        sf.is_reversible,
        "is_mechanical":        sf.is_mechanical,
        "is_catalytic":         sf.is_catalytic,
        # P
        "partners_identical":   sf.partners_identical,
        "has_pseudosymmetry":   sf.has_pseudosymmetry,
        # metadata
        "_smiles_source":       smiles,
        "_structural_flags":    sf,
        "_delta_g_method":      dg.method,
        "_delta_g_confidence":  dg.confidence,
        "_warnings":            dg.warnings + sf.warnings,
    }
    # Γ — only include when structural evidence is sufficient
    if sf.n_compatible_partners is not None and sf.n_total_possible_partners is not None:
        m["n_compatible_partners"]     = sf.n_compatible_partners
        m["n_total_possible_partners"] = sf.n_total_possible_partners
    return m
