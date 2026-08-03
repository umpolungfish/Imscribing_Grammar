"""
Molecular Domain — Imscription agents for retrosynthetic analysis.

This module implements agents for analyzing molecular imscriptions
in the context of retrosynthetic bond disconnection.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# Re-export for convenience
from imscrbgrmr.models import (
    Imscription,
    Dimensionality,
    Topology,
    RecognitionMode,
    Polarity,
    Fidelity,
    Granularity,
    InteractionGrammar,
    KineticCharacter,  # NEW
)

__all__ = [
    "MolecularImscriptionAgent",
    "ReactionCenterAnalysis",
]


@dataclass
class ReactionCenterAnalysis:
    """Result of reaction center analysis."""
    bond_index: int
    bond_type: str
    disconnection_feasibility: float  # 0-1
    imscription_polarity: Polarity
    estimated_bde: float  # Bond dissociation energy (kJ/mol)
    metadata: Dict[str, Any]


class MolecularImscriptionAgent:
    """
    Agent for analyzing molecular imscriptions in retrosynthetic contexts.
    
    Molecular imscriptions operate with D_wynn (point-like reactivity)
    and typically involve R_subset (covalent) or R_covalent_dynamic
    recognition modes.
    
    Capabilities:
    - Reaction center identification
    - Bond disconnection feasibility analysis
    - Imscription polarity assignment (P+, P-, P_pipevar)
    - Bond dissociation energy estimation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._last_analysis: Optional[ReactionCenterAnalysis] = None
    
    def analyze_reaction_center(
        self,
        smiles: str,
        bond_index: Optional[int] = None,
    ) -> ReactionCenterAnalysis:
        """
        Analyze a reaction center for imscription disconnection.
        
        Args:
            smiles: SMILES string of the molecule
            bond_index: Optional specific bond to analyze (default: find most labile)
        
        Returns:
            ReactionCenterAnalysis with disconnection feasibility
        """
        # Placeholder implementation
        # In full implementation, this would use RDKit for:
        # 1. Parse SMILES and identify all bonds
        # 2. Score each bond for disconnection feasibility
        # 3. Assign imscription polarity based on electronic properties
        # 4. Estimate BDE from bond type and context
        
        return ReactionCenterAnalysis(
            bond_index=bond_index or 0,
            bond_type="C-C",
            disconnection_feasibility=0.75,
            imscription_polarity=Polarity.yew,
            estimated_bde=350.0,
            metadata={"smiles": smiles},
        )
    
    def get_imscription_polarity(
        self,
        smiles: str,
        functional_groups: Optional[List[str]] = None,
    ) -> Polarity:
        """
        Determine imscription polarity for a molecular fragment.
        
        Args:
            smiles: SMILES of the fragment
            functional_groups: Optional list of functional groups
        
        Returns:
            Polarity enum (ACCEPTOR, DONOR, SELF_COMPLEMENTARY, or DONOR_ACCEPTOR)
        """
        # Common self-complementary motifs
        self_complementary = {
            "carboxylic_acid",
            "amide",
            "urea",
            "alcohol",
        }
        
        if functional_groups:
            for fg in functional_groups:
                if fg.lower() in self_complementary:
                    return Polarity.SELF_COMPLEMENTARY
        
        # Default: analyze electronic properties
        # In full implementation, this would use RDKit to:
        # 1. Compute partial charges
        # 2. Identify electrophilic/nucleophilic sites
        # 3. Assign polarity based on dominant character
        
        return Polarity.yew  # Default
    
    def compute_bond_dissociation_energy(
        self,
        smiles: str,
        bond_index: int,
    ) -> float:
        """
        Estimate bond dissociation energy for a specific bond.
        
        Args:
            smiles: SMILES of the molecule
            bond_index: Index of bond to analyze
        
        Returns:
            Estimated BDE in kJ/mol
        """
        # Typical BDE ranges (kJ/mol):
        # C-C single: 350-380
        # C=C double: 610-680
        # C≡C triple: 810-840
        # C-H: 410-440
        # C-O: 360-380
        # C=O: 710-750
        # O-H: 460-490
        # N-H: 390-420
        
        # Placeholder - in full implementation would use:
        # 1. RDKit to identify bond type
        # 2. Group contribution methods for context effects
        # 3. Optional: DFT single-point for accuracy
        
        return 350.0  # Default C-C single bond
    
    def list_molecular_imscriptions(
        self,
        reaction_type: Optional[str] = None,
    ) -> List[Imscription]:
        """
        List known molecular imscriptions, optionally filtered by reaction type.
        
        Args:
            reaction_type: Optional filter (e.g., "Σ_N2", "Diels-Alder")
        
        Returns:
            List of Imscription objects
        """
        from imscrbgrmr.models import CriticalityPhase
        
        # Common molecular imscriptions from retrosynthesis
        imscriptions = [
            # Carboxylic acid dimer (self-complementary)
            Imscription(
                name="carboxylic_acid_dimer",
                dimensionality=Dimensionality.dead,
                topology=Topology.mime,
                recognition_mode=RecognitionMode.ado,
                polarity=Polarity.yew,
                fidelity=Fidelity.peep,
                kinetic_character=KineticCharacter.yea,
                granularity=Granularity.ice,
                interaction_grammar=InteractionGrammar.vow,
                criticality_phase=CriticalityPhase.woe,
                description="Classic R₂²(8) hydrogen-bonded dimer",
                metadata={"reaction_type": "hydrogen_bonding"},
            ),
            # Enolate imscription (nucleophilic)
            Imscription(
                name="enolate_imscription",
                dimensionality=Dimensionality.dead,
                topology=Topology.eat,
                recognition_mode=RecognitionMode.tot,
                polarity=Polarity.yew,
                fidelity=Fidelity.they,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.ice,
                interaction_grammar=InteractionGrammar.vow,
                criticality_phase=CriticalityPhase.woe,
                description="Nucleophilic enolate for C-C bond formation",
                metadata={"reaction_type": "aldol"},
            ),
            # Carbonyl imscription (electrophilic)
            Imscription(
                name="carbonyl_imscription",
                dimensionality=Dimensionality.dead,
                topology=Topology.eat,
                recognition_mode=RecognitionMode.tot,
                polarity=Polarity.yew,
                fidelity=Fidelity.they,
                kinetic_character=KineticCharacter.loll,
                granularity=Granularity.ice,
                interaction_grammar=InteractionGrammar.vow,
                criticality_phase=CriticalityPhase.woe,
                description="Electrophilic carbonyl for nucleophilic attack",
                metadata={"reaction_type": "aldol"},
            ),
        ]
        
        if reaction_type:
            imscriptions = [
                s for s in imscriptions
                if s.metadata.get("reaction_type") == reaction_type
            ]
        
        return imscriptions
    
    def to_imscription(
        self,
        fragment_smiles: str,
        fragment_name: str = "",
    ) -> Imscription:
        """
        Convert a molecular fragment to a Imscription representation.
        
        Args:
            fragment_smiles: SMILES of the fragment
            fragment_name: Optional name for the imscription
        
        Returns:
            Imscription object representing the fragment
        """
        # Analyze the fragment
        polarity = self.get_imscription_polarity(fragment_smiles)
        
        # Determine interaction grammar based on specificity
        # (In full implementation, would analyze steric/electronic constraints)
        grammar = InteractionGrammar.SELECTIVE

        from imscrbgrmr.models import KineticCharacter, CriticalityPhase
        
        return Imscription(
            name=fragment_name or f"fragment_{fragment_smiles[:10]}",
            dimensionality=Dimensionality.dead,
            topology=Topology.eat,
            recognition_mode=RecognitionMode.tot,
            polarity=polarity,
            fidelity=Fidelity.they,
            kinetic_character=KineticCharacter.loll,
            granularity=Granularity.ice,
            interaction_grammar=grammar,
            criticality_phase=CriticalityPhase.woe,
            description=f"Molecular imscription from {fragment_smiles}",
            metadata={"smiles": fragment_smiles},
        )


# ---------------------------------------------------------------------------
# Canonical Molecular Catalog — design-file imscriptions
# ---------------------------------------------------------------------------
# These imscriptions are referenced by .syn design scripts and must be present in
# the global catalog at import time. They encode nine canonical systems not
# already covered by registry.py's populate_defaults().
#
# Naming convention for nitroso_radical_* entries: these encode nitrosobenzene-
# derived host–guest and redox systems used in supramolecular design studies.
# The "nitroso_radical" prefix marks the radical-anion binding motif that
# drives the anion–π recognition in cavity systems.
# ---------------------------------------------------------------------------

MOLECULAR_imscription_NAMES = frozenset([
    "nitroso_radical_redox_imscription_pair",
    "amide_dimer",
    "nitroso_radical_anion_π_cavitand_cage_imscription",
    "nitroso_radical_calixarene_anion_π_sandwich_imscription",
    "nitroso_radical_crown_ether_host_guest_imscription",
    "nitroso_radical_anion_π_cryptand_cage_imscription",
    "nitroso_radical_cucurbituril_anion_rotaxane_imscription",
    "methyl_anion_nucleophile_CH3",
    "methyl_cation_electrophile_CH3",
])


def register_molecular_imscriptions() -> list:
    """
    Register nine canonical molecular/supramolecular imscriptions used by
    .syn design scripts into the global catalog.

    Safe to call multiple times (idempotent).

    Returns:
        List of names newly registered (empty if all already present).
    """
    from ...models import (
        Imscription,
        Dimensionality,
        Topology,
        RecognitionMode,
        Polarity,
        Fidelity,
        KineticCharacter,
        Granularity,
        InteractionGrammar,
        CriticalityPhase,
    )
    from ...registry import global_catalog

    D = Dimensionality
    T = Topology
    R = RecognitionMode
    P = Polarity
    F = Fidelity
    K = KineticCharacter
    G = Granularity
    Gr = InteractionGrammar
    Ph = CriticalityPhase

    entries = [
        # ------------------------------------------------------------------
        # nitroso_radical_redox_imscription_pair
        # A high-fidelity temporal autocatalytic redox cycle encoding the
        # Frank-model bifurcation pattern (D_∞ + T_⋈ + P_directional + F_ℏ).
        # Intended role: start point for criticality-ascent design scripts;
        # the four Frank co-requisites mean Factor 7 fires (score 0.25) and
        # Factor 3 contributes ~0.10, giving phi_c_score > 0.3.
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_redox_imscription_pair",
            dimensionality=D.TEMPORAL,
            topology=T.CYCLIC_BOWTIE,
            recognition_mode=R.DYNAMIC_CATALYTIC,
            polarity=P.DONOR_ACCEPTOR,
            fidelity=F.HIGH,
            kinetic_character=K.MODERATE,
            granularity=G.MESOSCALE,
            interaction_grammar=Gr.SELECTIVE_SEQ,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Nitroso-radical redox pair: enantiospecific closed autocatalytic cycle "
                "(D_∞, T_⋈, P_directional, F_ℏ). Frank-model bifurcation candidate; "
                "φ_c score >0.3 via Factor 7 (classical pitchfork criticality)."
            ),
            metadata={"domain": "molecular", "class": "redox_autocatalytic"},
        ),

        # ------------------------------------------------------------------
        # amide_dimer
        # Self-complementary N–H···O=C hydrogen-bonded dimer.
        # Similar topology to carboxylic_acid_dimer (both T_⋈) but lower
        # fidelity (F_dh): amide NH is a weaker H-bond donor than OH.
        # meet(carboxylic_acid_dimer [F_ℏ], amide_dimer [F_dh]) → F_dh ✓
        # join(amide_dimer [F_dh], carboxylic_acid_dimer [F_ℏ]) → F_ℏ ✓
        # ------------------------------------------------------------------
        Imscription(
            name="amide_dimer",
            dimensionality=D.MOLECULAR,
            topology=T.CYCLIC_BOWTIE,
            recognition_mode=R.NON_COVALENT,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.MEDIUM,
            kinetic_character=K.MODERATE,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SELECTIVE_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Amide N–H···O=C hydrogen-bonded dimer (R₂²(8) motif). "
                "F_dh: weaker H-bond donor than carboxylic acid. "
                "T_⋈: closed self-complementary loop."
            ),
            metadata={"domain": "molecular", "class": "H-bond_dimer"},
        ),

        # ------------------------------------------------------------------
        # nitroso_radical_anion_π_cavitand_cage_imscription
        # Deep-cavity cavitand host with anion–π recognition.
        # D_△ (supramolecular), T_cage (closed three-dimensional enclosure),
        # R_mechanical (shape-selective mechanical capture), F_ℏ (rigid cavity,
        # high fidelity), K_schwa (slow guest exchange kinetics).
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_anion_π_cavitand_cage_imscription",
            dimensionality=D.SUPRAMOLECULAR,
            topology=T.CAGE,
            recognition_mode=R.MECHANICAL,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.HIGH,
            kinetic_character=K.SLOW,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SPECIFIC_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Cavitand cage with nitroso-radical anion–π recognition motif. "
                "Deep-cavity enclosure (T_cage), high rigidity (F_ℏ), slow guest "
                "exchange (K_schwa), shape-selective (R_mechanical)."
            ),
            metadata={"domain": "supramolecular", "class": "anion_pi_cage"},
        ),

        # ------------------------------------------------------------------
        # nitroso_radical_calixarene_anion_π_sandwich_imscription
        # Calixarene bowl — open cup topology (T_bowl) providing anion–π
        # sandwich geometry. Fallback partner to cavitand in hybrid designs.
        # T_bowl < T_cage in topology ordinal (3 vs 5), so serves as the
        # lower-complexity fallback in tensor or-patterns.
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_calixarene_anion_π_sandwich_imscription",
            dimensionality=D.SUPRAMOLECULAR,
            topology=T.BOWL,
            recognition_mode=R.MECHANICAL,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.HIGH,
            kinetic_character=K.SLOW,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SPECIFIC_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Calixarene bowl with anion–π sandwich recognition. "
                "T_bowl: open cup geometry; guest access from one face. "
                "Fallback to cavitand cage in hybrid design strategies."
            ),
            metadata={"domain": "supramolecular", "class": "anion_pi_bowl"},
        ),

        # ------------------------------------------------------------------
        # nitroso_radical_crown_ether_host_guest_imscription
        # Crown ether host–guest complex. F_dh (lower than rigid cage
        # systems): crown ether binding is enthalpy-driven but the flexible
        # macrocycle has conformational entropy cost that limits fidelity.
        # Tensor with cucurbituril gives F_dh (min bottleneck) — used to
        # demonstrate thermodynamic efficiency tuning in design 12.
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_crown_ether_host_guest_imscription",
            dimensionality=D.SUPRAMOLECULAR,
            topology=T.CAGE,
            recognition_mode=R.MECHANICAL,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.MEDIUM,
            kinetic_character=K.MODERATE,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SPECIFIC_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Crown ether host–guest complex with nitroso-radical recognition. "
                "F_dh: flexible macrocycle conformational entropy limits fidelity "
                "vs rigid cage systems. K_turnm: fast host–guest exchange."
            ),
            metadata={"domain": "supramolecular", "class": "crown_ether"},
        ),

        # ------------------------------------------------------------------
        # nitroso_radical_anion_π_cryptand_cage_imscription
        # Cryptand cage — 3D bicyclic host with high encapsulation fidelity.
        # F_ℏ: cryptand preorganisation gives high binding affinity.
        # Tensor with cucurbituril gives F_ℏ (min of F_ℏ, F_ℏ = F_ℏ) — used
        # in design 16 MOF-inspired network assembly.
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_anion_π_cryptand_cage_imscription",
            dimensionality=D.SUPRAMOLECULAR,
            topology=T.CAGE,
            recognition_mode=R.MECHANICAL,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.HIGH,
            kinetic_character=K.SLOW,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SPECIFIC_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Cryptand cage host with nitroso-radical anion–π recognition. "
                "3D bicyclic preorganisation → F_ℏ (high binding affinity). "
                "K_schwa: slow guest decomplexation kinetics."
            ),
            metadata={"domain": "supramolecular", "class": "cryptand_cage"},
        ),

        # ------------------------------------------------------------------
        # nitroso_radical_cucurbituril_anion_rotaxane_imscription
        # Cucurbit[n]uril barrel — high-fidelity mechanical cage.
        # Used as a tensor partner in both design 12 (with crown ether,
        # giving F_dh via bottleneck) and design 16 (with cryptand,
        # giving F_ℏ). The cucurbituril itself is F_ℏ in both cases.
        # ------------------------------------------------------------------
        Imscription(
            name="nitroso_radical_cucurbituril_anion_rotaxane_imscription",
            dimensionality=D.SUPRAMOLECULAR,
            topology=T.CAGE,
            recognition_mode=R.MECHANICAL,
            polarity=P.SELF_COMPLEMENTARY_PSEUDO,
            fidelity=F.HIGH,
            kinetic_character=K.SLOW,
            granularity=G.LOCAL,
            interaction_grammar=Gr.SPECIFIC_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Cucurbit[n]uril barrel encapsulating nitroso-radical anion via "
                "ion–dipole and hydrophobic interactions. High rigidity (F_ℏ), "
                "slow rotaxane dethreading kinetics (K_schwa)."
            ),
            metadata={"domain": "supramolecular", "class": "cucurbituril_rotaxane"},
        ),

        # ------------------------------------------------------------------
        # imscription_methyl_anion_nucleophile_CH3_
        # Carbanion (methyl anion) — the archetypal anionic nucleophile.
        # D_∧ (point reactant), T_| (linear: one reactive site), R_subset
        # (forms one covalent bond), P_minus (donates electron pair),
        # F_dh, K_turnm. Used in retrodesign/path searches within the D_∧/T_|
        # cluster of molecular imscriptions.
        # ------------------------------------------------------------------
        Imscription(
            name="methyl_anion_nucleophile_CH3",
            dimensionality=D.MOLECULAR,
            topology=T.LINEAR,
            recognition_mode=R.COVALENT,
            polarity=P.DONOR,
            fidelity=F.MEDIUM,
            kinetic_character=K.MODERATE,
            granularity=G.LOCAL,
            interaction_grammar=Gr.BROAD_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Methyl carbanion (CH₃⁻): archetypal anionic nucleophile. "
                "P_minus: electron-pair donor. T_linear: single reactive carbon centre. "
                "Retrosynthetic pair to carbonyl_imscription and methyl cation."
            ),
            metadata={"domain": "molecular", "class": "carbanion_nucleophile"},
        ),

        # ------------------------------------------------------------------
        # imscription_methyl_cation_electrophile_CH3
        # Carbocation (methyl cation) — archetypal cationic electrophile.
        # Retrosynthetic partner to methyl anion; tensor(anion, cation) →
        # pseudo-zwitterionic P (P_pm_pseudo) encoding C–C bond formation.
        # ------------------------------------------------------------------
        Imscription(
            name="methyl_cation_electrophile_CH3",
            dimensionality=D.MOLECULAR,
            topology=T.LINEAR,
            recognition_mode=R.COVALENT,
            polarity=P.ACCEPTOR,
            fidelity=F.MEDIUM,
            kinetic_character=K.MODERATE,
            granularity=G.LOCAL,
            interaction_grammar=Gr.BROAD_AND,
            criticality_phase=Ph.SUBCRITICAL,
            stoichiometry="1:1",
            description=(
                "Methyl carbocation (CH₃⁺): archetypal cationic electrophile. "
                "P_plus: electron-pair acceptor. T_linear: single reactive carbon centre. "
                "Retrosynthetic partner to imscription_methyl_anion_nucleophile_CH3_."
            ),
            metadata={"domain": "molecular", "class": "carbocation_electrophile"},
        ),
    ]

    registered = []
    for s in entries:
        if s.name not in global_catalog._imscriptions:
            global_catalog.register(
                s,
                domain="molecular",
                override_grounding=True,
                override_reason="Canonical molecular domain catalog entry (v0.4.0)",
            )
            registered.append(s.name)
    return registered
