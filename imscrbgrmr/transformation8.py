"""
Transformation #8 — Mechanical Bond (R_⇔): Rotaxane Dethreading Scan.

From QUANTIG.md Section V (Planned Validation):

A constrained relaxed scan along the N···centroid dethreading coordinate for a
DB24C8/dialkylammonium pseudorotaxane at M06-2X/6-31G(d).

Literature benchmarks:
- Dethreading barriers: 60-125 kJ/mol for ammonium-crown systems
- Characteristic profile: gradual H-bond weakening over ~4-5 Å plateau
  followed by sharp steric cliff as stopper encounters macrocycle

The steric cliff — discontinuous rather than Morse-like — is the topological
control signature distinguishing R_⇔ from any continuously varying non-covalent
interaction (R_⊇).

This module provides utilities for analyzing rotaxane dethreading profiles
and examining them for near-critical behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from imscrbgrmr.models import (
    Imscription,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
    KineticCharacter,
    CriticalityPhase,
)
from imscrbgrmr.thermodynamics import compute_eta_CP, compute_kinetic_fidelity


@dataclass
class DethreadingProfile:
    """Results from rotaxane dethreading scan analysis."""
    imscription_name: str
    dethreading_coordinate: List[float]  # Å
    energy_profile: List[float]  # kJ/mol
    barrier_height: float  # kJ/mol
    plateau_length: float  # Å
    cliff_position: float  # Å
    cliff_steepness: float  # kJ/mol/Å
    is_discontinuous: bool  # Steric cliff detected
    criticality_indicators: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "imscription_name": self.imscription_name,
            "barrier_height": self.barrier_height,
            "plateau_length": self.plateau_length,
            "cliff_position": self.cliff_position,
            "cliff_steepness": self.cliff_steepness,
            "is_discontinuous": self.is_discontinuous,
            "criticality_indicators": self.criticality_indicators,
        }


def analyze_dethreading_profile(
    coordinate: List[float],
    energy: List[float],
    imscription_name: str = "rotaxane_dethreading",
) -> DethreadingProfile:
    """
    Analyze a rotaxane dethreading energy profile.
    
    Args:
        coordinate: Dethreading coordinate (N···centroid distance) in Å
        energy: Energy profile in kJ/mol
        imscription_name: Name for the imscription
    
    Returns:
        DethreadingProfile with analysis results
    """
    coordinate = np.array(coordinate)
    energy = np.array(energy)
    
    # Find barrier height (maximum energy relative to minimum)
    min_energy = np.min(energy)
    max_energy = np.max(energy)
    barrier_height = max_energy - min_energy
    barrier_idx = np.argmax(energy)
    
    # Find plateau region (relatively flat region before cliff)
    # Look for region where dE/dx < threshold
    gradient = np.gradient(energy, coordinate)
    plateau_mask = np.abs(gradient) < 5.0  # kJ/mol/Å threshold
    
    # Find plateau length
    plateau_indices = np.where(plateau_mask)[0]
    if len(plateau_indices) > 1:
        plateau_length = coordinate[plateau_indices[-1]] - coordinate[plateau_indices[0]]
    else:
        plateau_length = 0.0
    
    # Find steric cliff (region of maximum gradient)
    cliff_idx = np.argmax(np.abs(gradient))
    cliff_position = coordinate[cliff_idx]
    cliff_steepness = abs(gradient[cliff_idx])
    
    # Detect discontinuity (steric cliff signature)
    # A true steric cliff has d²E/dx² >> 0 at the cliff position
    second_derivative = np.gradient(gradient, coordinate)
    is_discontinuous = second_derivative[cliff_idx] > 10.0  # kJ/mol/Å² threshold
    
    # Criticality indicators
    criticality_indicators = {
        "barrier_in_range": 60 <= barrier_height <= 125,  # Literature benchmark
        "plateau_detected": plateau_length > 2.0,  # Å
        "cliff_detected": cliff_steepness > 20.0,  # kJ/mol/Å
        "discontinuous_profile": is_discontinuous,
        "near_critical_topology": is_discontinuous and plateau_length > 3.0,
    }
    
    return DethreadingProfile(
        imscription_name=imscription_name,
        dethreading_coordinate=coordinate.tolist(),
        energy_profile=energy.tolist(),
        barrier_height=barrier_height,
        plateau_length=plateau_length,
        cliff_position=cliff_position,
        cliff_steepness=cliff_steepness,
        is_discontinuous=is_discontinuous,
        criticality_indicators=criticality_indicators,
    )


def create_rotaxane_imscription(
    name: str = "db24c8_ammonium_rotaxane",
    barrier_height: Optional[float] = None,
) -> Imscription:
    """
    Create a Imscription representing a mechanical bond rotaxane system.
    
    Args:
        name: Imscription name
        barrier_height: Optional dethreading barrier for K assignment
    
    Returns:
        Imscription with R_⇔ recognition mode
    """
    # Assign kinetic character from barrier
    if barrier_height is not None:
        k_char = KineticCharacter.from_barrier(barrier_height)
    else:
        k_char = KineticCharacter.MODERATE  # Default for rotaxanes
    
    return Imscription(
        name=name,
        dimensionality=Dimensionality.SUPRAMOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,  # Macrocycle
        recognition_mode=RecognitionMode.MECHANICAL,  # R_⇔
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,  # F_ℇ (context-dependent)
        kinetic_character=k_char,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=None,  # To be determined by analysis
        description="Mechanical bond rotaxane (DB24C8/dialkylammonium)",
        metadata={
            "macrocycle": "DB24C8",
            "thread": "dialkylammonium",
            "recognition_type": "mechanical_bond",
            "transformation": "#8",
        },
    )


def compute_rotaxane_efficiency(
    imscription: Imscription,
    barrier_height: float,
    information_gain: float = 5.0,  # bits (estimated)
) -> Dict[str, Any]:
    """
    Compute thermodynamic efficiency for a rotaxane mechanical bond.
    
    Args:
        imscription: Rotaxane imscription
        barrier_height: Dethreading barrier in kJ/mol
        information_gain: Information gain in bits (default: 5.0)
    
    Returns:
        Dict with efficiency metrics
    """
    # Compute η_CP using barrier as energy cost
    result = compute_eta_CP(
        imscription,
        delta_g=barrier_height,
        information_gain=information_gain,
        use_effective_fidelity=True,
    )
    
    # Get kinetic fidelity
    k_char, f_kinetic = compute_kinetic_fidelity(barrier_height)
    
    return {
        "imscription_name": imscription.name,
        "barrier_height": barrier_height,
        "eta_CP": result.eta_CP,
        "xi_CP": result.xi_CP,
        "waste_factor": result.waste_factor,
        "kinetic_character": k_char.value,
        "kinetic_fidelity": f_kinetic,
        "efficiency_description": result.efficiency_description,
        "mechanical_bond_signature": (
            "Steric cliff detected" if imscription.metadata.get("discontinuous_profile")
            else "Continuous profile"
        ),
    }


def check_transformation8_validation(
    profile: DethreadingProfile,
) -> Dict[str, Any]:
    """
    Check if Transformation #8 validation criteria are met.
    
    From QUANTIG.md:
    - Barrier: 60-125 kJ/mol
    - Plateau: ~4-5 Å
    - Steric cliff: discontinuous profile
    
    Args:
        profile: DethreadingProfile from analysis
    
    Returns:
        Validation report
    """
    indicators = profile.criticality_indicators
    
    # Check all criteria
    all_criteria_met = (
        indicators["barrier_in_range"] and
        indicators["plateau_detected"] and
        indicators["cliff_detected"] and
        indicators["discontinuous_profile"]
    )
    
    return {
        "transformation": "#8 (Mechanical Bond)",
        "imscription": profile.imscription_name,
        "barrier_height": profile.barrier_height,
        "barrier_in_range": indicators["barrier_in_range"],
        "plateau_length": profile.plateau_length,
        "plateau_detected": indicators["plateau_detected"],
        "cliff_steepness": profile.cliff_steepness,
        "cliff_detected": indicators["cliff_detected"],
        "discontinuous_profile": indicators["discontinuous_profile"],
        "near_critical_topology": indicators["near_critical_topology"],
        "all_criteria_met": all_criteria_met,
        "validation_status": "PASSED" if all_criteria_met else "PENDING",
        "note": (
            "Mechanical bond (R_⇔) confirmed" if all_criteria_met
            else "Additional characterization needed"
        ),
    }


# Example usage and test data
def generate_test_profile() -> Tuple[List[float], List[float]]:
    """
    Generate a test dethreading profile mimicking DB24C8/ammonium system.
    
    Returns:
        Tuple of (coordinate, energy) lists
    """
    # Simulated dethreading coordinate (3 to 10 Å)
    coordinate = np.linspace(3.0, 10.0, 100)
    
    # Simulated energy profile:
    # - Plateau from 3-7 Å (H-bonding region)
    # - Sharp cliff at 7-8 Å (steric barrier)
    # - Decay beyond 8 Å (thread free)
    
    energy = np.zeros_like(coordinate)
    
    for i, x in enumerate(coordinate):
        if x < 7.0:
            # Plateau region (H-bonding)
            energy[i] = -80 + 2 * (x - 3.0)  # Gradual weakening
        elif x < 7.5:
            # Steric cliff
            energy[i] = -72 + 200 * (x - 7.0)  # Sharp rise
        else:
            # Beyond barrier (decay)
            energy[i] = 28 - 28 * (1 - np.exp(-(x - 7.5) / 0.5))
    
    return coordinate.tolist(), energy.tolist()


if __name__ == "__main__":
    # Test the analysis
    coord, energy = generate_test_profile()
    profile = analyze_dethreading_profile(coord, energy)
    
    print(f"Barrier height: {profile.barrier_height:.1f} kJ/mol")
    print(f"Plateau length: {profile.plateau_length:.1f} Å")
    print(f"Cliff steepness: {profile.cliff_steepness:.1f} kJ/mol/Å")
    print(f"Discontinuous: {profile.is_discontinuous}")
    print(f"Criticality indicators: {profile.criticality_indicators}")
    
    # Create imscription and validate
    imscription = create_rotaxane_imscription(barrier_height=profile.barrier_height)
    validation = check_transformation8_validation(profile)
    
    print(f"\nTransformation #8 Validation: {validation['validation_status']}")
