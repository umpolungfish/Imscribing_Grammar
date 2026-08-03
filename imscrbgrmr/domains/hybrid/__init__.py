"""
Hybrid Domain — Multi-dimensional imscription agents.

This module implements agents for analyzing hybrid systems
that span multiple domains (e.g., MOF-embedded catalytic cycles).
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional

from imscrbgrmr.models import (
    Imscription,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
)

__all__ = ["HybridImscriptionAgent"]


class HybridImscriptionAgent:
    """
    Agent for analyzing multi-dimensional hybrid imscriptions.
    
    Hybrid systems combine multiple dimensionalities:
    - D_wedge_triangle: Molecular + Supramolecular (e.g., crystal engineering)
    - D_wedge_infinity: Molecular + Temporal (e.g., dynamic covalent chemistry)
    - D_triangle_infinity: Supramolecular + Temporal (e.g., MOF-embedded catalysis)
    - D_all: All three domains (programmable matter)
    
    Capabilities:
    - Spatial framework analysis (MOF topology)
    - Temporal cycle analysis (embedded catalysis)
    - Granularity amplification detection
    - R_hyb coupling evaluation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def analyze_spatial_framework(
        self,
        framework_type: str,
        topology: str = "pcu",
    ) -> Dict[str, Any]:
        """
        Analyze the spatial framework of a hybrid system.
        
        Args:
            framework_type: Type of framework (e.g., "MOF", "COF", "zeolite")
            topology: Net topology (e.g., "pcu", "dia", "rht")
        
        Returns:
            Framework analysis with topology and granularity
        """
        # Common MOF topologies
        topology_info = {
            "pcu": {"name": "Primitive cubic", "coordination": 6},
            "dia": {"name": "Diamond", "coordination": 4},
            "rht": {"name": "Rhombohedral", "coordination": 8},
            "ftw": {"name": "Frank-Kasper", "coordination": 12},
        }
        
        return {
            "framework_type": framework_type,
            "topology": topology,
            "topology_name": topology_info.get(topology, {}).get("name", "Unknown"),
            "dimensionality": "𐑨",
            "granularity": Granularity.thigh.value,
            "notes": (
                f"{framework_type} with {topology} topology provides "
                f"global (G_revapostrophe) constraint propagation"
            ),
        }
    
    def analyze_temporal_cycle(
        self,
        cycle_type: str,
        confinement: str = "pore",
    ) -> Dict[str, Any]:
        """
        Analyze the temporal cycle embedded in a hybrid system.
        
        Args:
            cycle_type: Type of catalytic cycle
            confinement: Confinement environment ("pore", "cage", "channel")
        
        Returns:
            Cycle analysis with confinement effects
        """
        # Confinement effects on catalysis
        confinement_effects = {
            "pore": {
                "selectivity_enhancement": "high",
                "rate_effect": "variable",
                "mechanism": "Size/shape selectivity",
            },
            "cage": {
                "selectivity_enhancement": "very_high",
                "rate_effect": "often_enhanced",
                "mechanism": "Concentration + preorganization",
            },
            "channel": {
                "selectivity_enhancement": "medium",
                "rate_effect": "diffusion_limited",
                "mechanism": "1D transport constraints",
            },
        }
        
        effect = confinement_effects.get(confinement, confinement_effects["pore"])
        
        return {
            "cycle_type": cycle_type,
            "confinement": confinement,
            "dimensionality": "𐑼",
            "recognition_mode": "𐑽",
            "confinement_effects": effect,
            "notes": (
                f"Temporal imscription (D_infinity) coupled with "
                f"{confinement} confinement"
            ),
        }
    
    def compute_granularity_amplification(
        self,
        spatial_granularity: Granularity,
        temporal_granularity: Granularity,
    ) -> Dict[str, Any]:
        """
        Compute granularity amplification in hybrid systems.
        
        Based on Transformation #3 from QUANTIG.md:
        - Chelate effect: G_beta → G_revapostrophe (local to global)
        - Single binding event enforces entire coordination sphere
        
        Args:
            spatial_granularity: Granularity of spatial framework
            temporal_granularity: Granularity of temporal cycle
        
        Returns:
            Amplification analysis
        """
        # Determine effective granularity
        granularities = [spatial_granularity, temporal_granularity]
        
        # Hierarchy: GLOBAL > MESOSCALE > LOCAL
        if Granularity.thigh in granularities:
            effective_granularity = Granularity.thigh
        elif Granularity.bib in granularities:
            effective_granularity = Granularity.bib
        else:
            effective_granularity = Granularity.ice
        
        # Compute amplification factor
        base_gran = Granularity.ice
        amplification_map = {
            Granularity.ice: 1,
            Granularity.bib: 10,
            Granularity.thigh: 100,
        }
        
        amplification = (
            amplification_map[effective_granularity] /
            amplification_map[base_gran]
        )
        
        return {
            "spatial_granularity": spatial_granularity.value,
            "temporal_granularity": temporal_granularity.value,
            "effective_granularity": effective_granularity.value,
            "amplification_factor": amplification,
            "transition": f"G_{base_gran.name} → G_{effective_granularity.name}",
            "notes": (
                f"Granularity amplification by {amplification}× "
                f"through hybrid coupling"
            ),
        }
    
    def evaluate_r_hyb_coupling(
        self,
        recognition_modes: List[RecognitionMode],
    ) -> Dict[str, Any]:
        """
        Evaluate hybrid recognition mode coupling.
        
        Args:
            recognition_modes: List of recognition modes in the system
        
        Returns:
            Coupling analysis with compatibility and effects
        """
        if len(recognition_modes) < 2:
            return {"error": "Need at least 2 recognition modes for hybrid coupling"}
        
        # Known hybrid recognition combinations
        hyb_combinations = {
            frozenset({RecognitionMode.ado, RecognitionMode.ear}): {
                "name": "Supramolecular catalysis",
                "example": "MOF-embedded organocatalyst",
                "coupling_strength": "strong",
                "effect": "Enhanced selectivity via confinement",
            },
            frozenset({RecognitionMode.tot, RecognitionMode.ear}): {
                "name": "Dynamic covalent chemistry",
                "example": "Imine exchange networks",
                "coupling_strength": "strong",
                "effect": "Error correction + self-healing",
            },
            frozenset({RecognitionMode.ado, RecognitionMode.ian}): {
                "name": "Supramolecular rotaxanes",
                "example": "Hydrogen-bonded template assembly",
                "coupling_strength": "medium",
                "effect": "Template-directed synthesis",
            },
        }
        
        mode_set = frozenset(recognition_modes)
        combo_data = hyb_combinations.get(mode_set, {
            "name": "Unknown hybrid",
            "coupling_strength": "unknown",
            "effect": "To be determined",
        })
        
        return {
            "recognition_modes": [r.value for r in recognition_modes],
            "hybrid_notation": f"R_hyb({'+'.join(r.value.split('_')[1] for r in recognition_modes)})",
            **combo_data,
        }
    
    def to_imscription(
        self,
        name: str,
        domains: List[str],
        description: str = "",
    ) -> Imscription:
        """
        Create a hybrid imscription from domain specifications.
        
        Args:
            name: Name for the imscription
            domains: List of domains ("molecular", "supramolecular", "temporal")
            description: Optional description
        
        Returns:
            Imscription object with hybrid dimensionality
        """
        # Map domains to Dimensionality
        domain_set = set(domains)
        
        if domain_set == {"molecular"}:
            dim = Dimensionality.dead
        elif domain_set == {"supramolecular"}:
            dim = Dimensionality.ash
        elif domain_set == {"temporal"}:
            dim = Dimensionality.array
        elif domain_set == {"molecular", "supramolecular"}:
            dim = Dimensionality.ash
        elif domain_set == {"molecular", "temporal"}:
            dim = Dimensionality.array
        elif domain_set == {"supramolecular", "temporal"}:
            dim = Dimensionality.array
        else:
            dim = Dimensionality.ash

        from imscrbgrmr.models import KineticCharacter, CriticalityPhase
        
        return Imscription(
            name=name,
            dimensionality=dim,
            topology=Topology.judge,  # Default for hybrid systems
            recognition_mode=RecognitionMode.ado,  # Default
            polarity=Polarity.church,
            fidelity=Fidelity.they,
            kinetic_character=KineticCharacter.loll,
            granularity=Granularity.thigh,
            interaction_grammar=InteractionGrammar.SELECTIVE,
            criticality_phase=CriticalityPhase.woe,
            description=description or f"Hybrid imscription: {', '.join(domains)}",
            metadata={"domains": domains},
        )
