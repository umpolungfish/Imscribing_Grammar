"""
Cross-Domain Imscription Catalog — Phase 1 Implementation

Registers the first non-chemical imscription entries: ecological, techno-social,
and robotic systems encoded in the 10-primitive tuple framework.

Each entry uses the closest available enum values for the current primitive set,
with `metadata["extensions_required"]` recording exactly which Phase 2 primitive
extensions are needed for a fully faithful encoding.

Domain categories added:
    ecological       — open dissipative bio-physical systems
    techno_social    — human-machine network systems
    robotic          — autonomous multi-agent systems

Phase 2 extensions flagged here (see IG_CROSS_DOMAIN.md):
    D∞(open)              — open dissipative qualifier for Axiom 6
    compound_R            — simultaneous multi-mode recognition (R·R notation)
    compound_grammar      — simultaneous multi-grammar (Γ·Γ notation)
    fidelity_distribution — ⟨F₁, F₂⟩ per-axis field pairs
    stoichiometry_network — 1:* (unbounded) stoichiometry
    tensor_product_D      — D△^⊗n for N-agent tensor-product dimensionality
"""
from __future__ import annotations

from typing import List

from .models import (
    Imscription, Dimensionality, Topology, RecognitionMode, Polarity,
    Fidelity, KineticCharacter, Granularity, InteractionGrammar, CriticalityPhase,
)
from .registry import global_catalog

_CROSS_DOMAIN_NAMES = frozenset([
    "tide_pool_ecological",
    "global_supply_chain",
    "autonomous_drone_swarm",
    "db24c8_dialkylammonium_pseudorotaxane",
])


def register_cross_domain_imscriptions() -> List[str]:
    """
    Register the three Phase-1 cross-domain imscriptions into the global catalog.

    Safe to call multiple times. Always refreshes metadata on already-present
    entries so that `extensions_required` and other Phase 1 annotations are
    current even after a catalog JSON round-trip strips them.

    Returns:
        List of names that were newly registered (empty if all already present).
    """
    entries: List[Imscription] = _build_entries()
    registered = []
    for s in entries:
        if s.name not in global_catalog._imscriptions:
            global_catalog.register(s)
            registered.append(s.name)
        else:
            # Refresh metadata in-place — persisted JSON may have dropped it
            existing = global_catalog._imscriptions[s.name]
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata)
    return registered


# ---------------------------------------------------------------------------
# Imscription definitions
# ---------------------------------------------------------------------------

def _build_entries() -> List[Imscription]:
    return [
        _tide_pool(),
        _global_supply_chain(),
        _autonomous_drone_swarm(),
        _db24c8_pseudorotaxane(),
    ]


def _tide_pool() -> Imscription:
    """
    Intertidal rock-pool ecological imscription.

    Formal tuple (Phase 2 target):
        ⟨ {D∞(open), D△} ; T⋈ ; R‡·R⊇ ; P±ψ ; ⟨F_ð, F_ð⟩ ; K_schwa ; G_ℶ ;
          Γ∨(BROAD) ; Φ_sub ; n:m ⟩

    Phase 1 encoding (current enum limits):
        D  → HYBRID_SUPRA_TEMP  (supramolecular spatial structure + open dissipative dynamics)
        T  → CYCLIC_BOWTIE      (closed trophic cycle: algae→grazer→predator→detritus→nutrients)
        R  → DYNAMIC_CATALYTIC  (non-equilibrium predator-prey flows; R⊇ flagged in metadata)
        P  → SELF_COMPLEMENTARY_PSEUDO  (each species is both consumer and resource)
        F  → MEDIUM             (stochastic, F_ð on both axes; field-pair in metadata)
        K  → SLOW               (diurnal/tidal period > 12 h; seasonal reproduction)
        G  → MESOSCALE          (bounded locality; coastline influence → G_ℶ not G_ℵ)
        Γ  → BROAD_OR           (promiscuous: grazer eats many prey; Γ∨(BROAD))
        Φ  → SUBCRITICAL        (no documented scale-free transition)
        S  → "n:m"              (many species, no fixed ratio)

    Axiom grounding:
        Axiom 6 — D∞(open) flagged; reset = tidal flushing + nutrient cycling
        Axiom 7 — T⋈ closing bond = nutrient-uptake step closes trophic loop
    """
    return Imscription(
        name="tide_pool_ecological",
        dimensionality=Dimensionality.HYBRID_SUPRA_TEMP,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="n:m",
        description=(
            "Intertidal rock-pool ecosystem: open dissipative system with "
            "diurnal tidal flushing, solar energy input, and closed trophic cycle "
            "(algae → grazers → predators → detritus → nutrients → algae). "
            "Closing bond: detritivore nutrient-release step returns system to initial state."
        ),
        metadata={
            "domain_category": "ecological",
            "cross_domain": True,
            "validation_tier": "extended",
            "phase1_encoding": True,
            "extensions_required": [
                "D∞(open) — Axiom 6 relaxed to directional-flow grounding (not closed-cycle reset)",
                "compound_R — R‡·R⊇ simultaneous non-equilibrium flow + sessile attachment",
                "fidelity_distribution — ⟨F_ð, F_ð⟩ stochastic on both spatial and temporal axes",
            ],
            "grounding": {
                "reset": {
                    "type": "continuous",
                    "driving_gradient": {
                        "description": "Solar irradiance + tidal flushing continuously drive photosynthesis and nutrient import",
                        "physical_quantity": "Solar flux (W m⁻²) + tidal volume exchange (m³ cycle⁻¹)",
                        "coupling": "Photosynthetic rate ∝ irradiance; nutrient import ∝ tidal amplitude",
                        "timescale": "12.4 h tidal period; 24 h diurnal solar cycle",
                        "entropy_export": "Heat dissipation from respiration; detritus export via tidal efflux",
                    },
                },
            },
            "axiom6_grounding": {
                "initial_state": "Nutrient-rich water, established species assemblage",
                "transformation": "Trophic energy cascade: photosynthesis → herbivory → predation",
                "work_performed": "Biomass accumulation; organismal growth and reproduction",
                "reset_mechanism": "Tidal flushing + detritivore mineralisation returns nutrients to water column",
            },
            "axiom7_closing_bond": "Detritivore mineralisation step closes the trophic loop",
            "cross_domain_analog": {
                "molecular": "proline_aldol_cycle (closed catalytic cycle, periodic reset)",
                "supramolecular": "MOF framework (spatial organisation, mesoscale granularity)",
            },
            "phase2_target_tuple": "⟨ {D∞(open), D△} ; T⋈ ; R‡·R⊇ ; P±ψ ; ⟨F_ð,F_ð⟩ ; K_schwa ; G_ℶ ; Γ∨(BROAD) ; Φ_sub ; n:m ⟩",
        },
    )


def _global_supply_chain() -> Imscription:
    """
    Planetary logistics network imscription (techno-social).

    Formal tuple (Phase 2 target):
        ⟨ D∞(open) ; T⋈·T_nrleg ; R‡ ; P− ; ⟨F_ð, F_ℏ⟩ ; K_turnm ; G_ℵ ;
          Γ∧(SELECTIVE) ; Φ_sub ; 1:* ⟩

    Phase 1 encoding:
        D  → TEMPORAL           (open dissipative; D∞(open) flagged in metadata)
        T  → NETWORK            (hub-and-spoke ports + mesh redundancy; T⋈ cyclic flows in metadata)
        R  → DYNAMIC_CATALYTIC  (supply/demand non-equilibrium; R‡)
        P  → DONOR              (P− asymmetric: producer → consumer directionality)
        F  → MEDIUM             (composite; F_ð demand stochastic + F_ℏ contractual hard constraints)
        K  → MODERATE           (ships ~20 kn; infrastructure rebuild months-to-years)
        G  → GLOBAL             (G_ℵ: planetary graph, every node addressable)
        Γ  → SELECTIVE_AND      (all required inputs must arrive simultaneously for production)
        Φ  → SUBCRITICAL        (bullwhip oscillations exist but no confirmed Φ_c transition)
        S  → "1:*"              (one planetary system, unbounded node count; stoichiometry_network flagged)

    Axiom grounding:
        Axiom 6 — D∞(open) flagged; directional flow = production→distribution→consumption
        Axiom 7 — T⋈ component closes via payment/consumption loop returning capital to producers
    """
    return Imscription(
        name="global_supply_chain",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:*",
        description=(
            "Planetary production-distribution-consumption network: open dissipative "
            "techno-social system with hub-and-spoke port topology, non-equilibrium "
            "supply/demand flows, and mixed stochastic/contractual fidelity. "
            "Asymmetric polarity (producers → consumers). Infinite graph (G_ℵ). "
            "Cyclic component: capital-return loop closes trade cycle."
        ),
        metadata={
            "domain_category": "techno_social",
            "cross_domain": True,
            "validation_tier": "extended",
            "phase1_encoding": True,
            "extensions_required": [
                "D∞(open) — open dissipative qualifier; Axiom 6 directional-flow grounding not closed-cycle",
                "stoichiometry_network — 1:* unbounded node count; S primitive needs network mode",
                "fidelity_distribution — ⟨F_ð, F_ℏ⟩ stochastic demand + hard contractual constraints",
                "compound_T — T_nrleg·T⋈ simultaneous network topology + cyclic trade flows",
            ],
            "grounding": {
                "reset": {
                    "type": "continuous",
                    "driving_gradient": {
                        "description": "Global consumer demand continuously drives production, distribution, and capital circulation",
                        "physical_quantity": "Demand signal (units/time) + capital flow (USD/cycle)",
                        "coupling": "Production rate ∝ demand forecast; capital reinvestment ∝ margin",
                        "timescale": "Hours (logistics) to years (infrastructure rebuild)",
                        "entropy_export": "Waste products, heat from manufacturing, depreciation of physical capital",
                    },
                },
            },
            "axiom6_grounding": {
                "initial_state": "Production capacity available; inventory levels at baseline",
                "transformation": "Raw materials → manufactured goods → distribution → consumption",
                "work_performed": "Economic value creation; consumer needs satisfied",
                "directional_flow": "Capital returns from consumption → investment → production capacity",
                "note": "D∞(open): flow is directional, not a discrete reset — Phase 2 qualifier required",
            },
            "axiom7_closing_bond": "Capital-return loop: consumer payment → producer revenue closes cycle",
            "known_emergent_phenomena": [
                "Bullwhip effect (demand amplification upstream)",
                "Just-in-time fragility under single-node failures",
                "Phase transition during pandemic/geopolitical shocks",
            ],
            "cross_domain_analog": {
                "temporal": "proline_aldol_cycle (catalytic flow with continuous throughput)",
                "supramolecular": "MOF framework (G_ℵ global network, selective AND grammar)",
            },
            "phase2_target_tuple": "⟨ D∞(open) ; T⋈·T_nrleg ; R‡ ; P− ; ⟨F_ð,F_ℏ⟩ ; K_turnm ; G_ℵ ; Γ∧(SELECTIVE) ; Φ_sub ; 1:* ⟩",
        },
    )


def _autonomous_drone_swarm() -> Imscription:
    """
    Autonomous UAV swarm imscription (robotic multi-agent).

    Formal tuple (Phase 2 target):
        ⟨ D△^⊗n ; T□ ; R(Ent)·R‡ ; P± ; ⟨F_ℏ, F_ð⟩ ; K_frtailgamma ; G_ℵ ;
          Γ∧(SELECTIVE)·Γ→(SELECTIVE) ; Φ_c ; n:m ⟩

    Phase 1 encoding:
        D  → SUPRAMOLECULAR     (D△ discrete spatial assembly; ^⊗n tensor flagged in metadata)
        T  → HUB_NODE           (T□ lattice/mesh communication graph)
        R  → DYNAMIC_CATALYTIC  (R‡ non-equilibrium motion + R(Ent) consensus; compound in metadata)
        P  → SELF_COMPLEMENTARY_PSEUDO  (P± — symmetric units, asymmetric roles leader/follower)
        F  → HIGH               (F_ℏ digital protocol determinism; F_ð env noise in metadata)
        K  → FAST               (millisecond control loops, GHz processors)
        G  → GLOBAL             (G_ℵ unlimited swarm scalability)
        Γ  → SELECTIVE_SEQ      (formation agreement AND then sequential command execution)
        Φ  → CRITICAL           (Φ_c — flocking is documented scale-free phase transition)
        S  → "n:m"              (flexible drone-to-task ratio)

    Axiom grounding:
        Axiom 4 — Γ_→ (SEQ) satisfied: R‡ (non-equilibrium motion) present
        Axiom 5 — Φ_c assigned: flocking correlation length ξ_r ~ N^(ν) (scale-free)
    """
    return Imscription(
        name="autonomous_drone_swarm",
        dimensionality=Dimensionality.SUPRAMOLECULAR,
        topology=Topology.HUB_NODE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Autonomous UAV swarm: N-agent robotic system with consensus-protocol "
            "recognition, non-equilibrium physical dynamics, and emergent flocking "
            "phase transition (Φ_c). Digital communication is F_ℏ (bit-exact); "
            "environmental coupling introduces F_ð noise. Sequential grammar: "
            "formation consensus precedes ordered manoeuvre execution."
        ),
        metadata={
            "domain_category": "robotic",
            "cross_domain": True,
            "validation_tier": "extended",
            "phase1_encoding": True,
            "extensions_required": [
                "tensor_product_D — D△^⊗n for N independent agents; collective state is tensor product",
                "compound_R — R(Ent)·R‡ consensus protocol + physical motion simultaneously active",
                "compound_grammar — Γ∧·Γ→ formation AND then sequential command execution",
                "fidelity_distribution — ⟨F_ℏ, F_ð⟩ digital precision + environmental stochasticity",
            ],
            "axiom4_grounding": {
                "sequential_grammar_present": True,
                "satisfying_primitive": "R‡ (DYNAMIC_CATALYTIC) — non-equilibrium physical motion",
            },
            "axiom5_grounding": {
                "criticality_evidence": "Vicsek model flocking transition; ξ_r ~ N^0.5 at Φ_c",
                "universality_class": "Active matter / Vicsek universality",
                "gd_degeneracy": "At flocking transition, local (G_ב) and global (G_ℵ) become degenerate",
            },
            "r_ent_definition": (
                "R(Ent): Consensus-protocol recognition — shared distributed state "
                "where each agent's action is constrained by collective agreement. "
                "Functionally isomorphic to quantum entanglement: no agent can act "
                "independently once consensus is reached."
            ),
            "cross_domain_analog": {
                "molecular": "adenine_thymine_pair (specific AND grammar, high fidelity)",
                "temporal": "proline_aldol_cycle (sequential grammar, reset mechanism)",
            },
            "phi_c_test": {
                "method": "Measure ξ_r vs N at varying alignment noise η",
                "expected": "Power-law divergence of ξ_r at η_c (critical noise)",
                "reference": "Vicsek et al. (1995) PRL 75:1226",
            },
            "phase2_target_tuple": "⟨ D△^⊗n ; T□ ; R(Ent)·R‡ ; P± ; ⟨F_ℏ,F_ð⟩ ; K_frtailgamma ; G_ℵ ; Γ∧(SELECTIVE)·Γ→(SELECTIVE) ; Φ_c ; n:m ⟩",
        },
    )


def _db24c8_pseudorotaxane() -> Imscription:
    """
    DB24C8/dialkylammonium pseudorotaxane — Transformation #8 Φ_c probe system.

    Formal tuple:
        ⟨ D_∧ ; T_⋈ ; R_⇔ ; P_+ ; F_ℏ ; K_turnm ; G_ב ; Γ_∧(SPECIFIC) ; Φ_sub→Φ_c ; 1:1 ⟩

    This is the primary-tier molecular system used as the Transformation #8
    literature-grounded partial Φ_c anchor.

    Grounding source: Groppi et al. Angew. Chem. Int. Ed. 2020, 59, 14825–14834.
    DOI: 10.1002/anie.202003064

    Key data:
      - Guest 6⁺ (good axle): ΔG‡ = 19.8 kcal mol⁻¹ (metadynamics, PBE-D2,
        explicit CH₂Cl₂ solvent); experimental ΔG‡_out = 23.1 kcal mol⁻¹.
        Ring distortions < 200 cm⁻¹ (thermally accessible). K_turnm.
      - Guest 8⁺ (bad axle): ΔG‡ > 100 kcal mol⁻¹. Blocked modes at 614 and
        809 cm⁻¹. Effective K_teshlig.
      - Sub-Å methyl repositioning switches K_turnm ↔ K_teshlig without disrupting
        R_⇔ or T_⋈. All-or-nothing steric cliff.

    Provisional degeneracy_strength ≈ 0.71 (proxy estimate; not computed).
    Triggers Varma probe requirement in HotSwapEngine (score ≥ 0.70 threshold).

    grounding_status: "partial" — literature proxy, full relaxed scan pending.
    validation_tier: "primary" — molecular domain, explicit literature ΔG data.
    """
    return Imscription(
        name="db24c8_dialkylammonium_pseudorotaxane",
        description=(
            "DB24C8 / dialkylammonium pseudorotaxane: steric-cliff dethreading system. "
            "Transformation #8 literature-grounded partial Φ_c anchor. "
            "Guest 6⁺ (good axle): ΔG‡ = 19.8 kcal mol⁻¹ (K_turnm). "
            "Guest 8⁺ (bad axle): ΔG‡ > 100 kcal mol⁻¹ (K_teshlig). "
            "All-or-nothing steric cliff on sub-Å methyl repositioning. "
            "Provisional degeneracy_strength ≈ 0.71. "
            "Source: Groppi et al. Angew. Chem. Int. Ed. 2020, 59, 14825. "
            "DOI: 10.1002/anie.202003064"
        ),
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        metadata={
            "validation_tier": "primary",
            "grounding_status": "partial",
            "grounding_status_note": (
                "Literature proxy from Groppi et al. 2020 metadynamics. "
                "Full relaxed-scan validation at ωB97X-D/def2-TZVPP pending."
            ),
            "phi_c_candidacy": {
                "proxy_degeneracy_strength": 0.71,
                "classification": "power-law / low-logarithmic boundary",
                "proxy_source": "Groppi, J. et al. Angew. Chem. Int. Ed. 2020, 59, 14825–14834. DOI: 10.1002/anie.202003064",
                "basis": (
                    "Barrier amplification >5× on sub-Å methyl repositioning "
                    "(19.8 → >100 kcal mol⁻¹) + inaccessible high-frequency ring modes "
                    "(614/809 cm⁻¹) in bad axle 8⁺ vs. accessible <200 cm⁻¹ modes in "
                    "good axle 6⁺. Matches K selectivity explosion at constant/improved F."
                ),
                "status": "literature_proxy",
                "requires_full_scan": True,
                "notes": (
                    "Matches predicted all-or-nothing steric cliff; K selectivity explosion "
                    "at constant/improved F. Sub-Å methyl repositioning flips K_turnm → K_teshlig "
                    "without disrupting R_⇔ or T_⋈ — precisely the primitive contraction "
                    "Axiom 5 predicts near the criticality locus. "
                    "HotSwap code relaxations (F floor, K multiplicity, S defect) deferred "
                    "until degeneracy_strength ≥ 0.70 is confirmed computationally."
                ),
                "varma_required": True,
            },
            "transformation_number": 8,
            "dethreading_data": {
                "guest_6_plus": {
                    "barrier_kcal_mol": 19.8,
                    "method": "ab initio metadynamics, PBE-D2, explicit CH₂Cl₂, 300 K",
                    "barrier_experimental_kcal_mol": 23.1,
                    "kinetic_character": "Ç_turnm",
                    "ring_distortion_modes_cm1": "<200 (thermally accessible)",
                    "h_bonds_in_ts": "persist and shift",
                },
                "guest_8_plus": {
                    "barrier_kcal_mol": ">100",
                    "method": "ab initio metadynamics, PBE-D2, explicit CH₂Cl₂, 300 K",
                    "kinetic_character": "Ç_teshlig",
                    "blocked_modes_cm1": [614, 809],
                    "reason": "high-frequency ring-elongation modes inaccessible at 300 K",
                },
                "collective_variable": (
                    "Displacement of 9 phenyl carbons (including methyls and methylene) "
                    "relative to the 8 crown oxygens of DB24C8"
                ),
                "steric_cliff_regime_angstrom": "4–5",
            },
            "reference": {
                "citation": "Groppi, J. et al. Angew. Chem. Int. Ed. 2020, 59, 14825–14834",
                "doi": "10.1002/anie.202003064",
                "type": "literature_proxy",
            },
            "axiom6_grounding": {
                "initial_state": "DB24C8 threaded on ammonium axle; 2–4 N⁺-H···O hydrogen bonds",
                "transformation": "Steric-cliff dethreading: sequential H-bond weakening then abrupt steric clash",
                "work_performed": "ΔG‡ = 19.8 kcal mol⁻¹ (83 kJ mol⁻¹) for slippage-permissive 6⁺ axle",
                "reset_mechanism": "Re-threading: ammonium axle re-enters crown cavity driven by H-bond formation",
            },
            "grounding": {
                "reset": {
                    "type": "discrete",
                    "cycle_steps": [
                        "ammonium_axle_insertion",
                        "h_bond_formation_2_to_4_contacts",
                        "plateau_traversal_20_to_50_kJ_mol",
                        "steric_cliff_crossing_at_4_to_5_angstrom",
                        "dethreading_complete",
                    ],
                },
            },
            "axiom7_closing_bond": "Crown ether O···H-N⁺ hydrogen bonds (2–4 contacts); mechanical interlocking at threaded state",
            "next_steps": [
                "Full relaxed scan at ωB97X-D/def2-TZVPP with 0.1–0.2 Å step density around 4–5 Å",
                "DLPNO-CCSD(T)/CBS single-point refinement at TS geometry",
                "Run varma_probe.degeneracy_strength() on MD trajectory near TS",
                "If degeneracy_strength ≥ 0.70 confirmed computationally: upgrade grounding_status to 'full'",
                "First empirically grounded Φ_c HotSwap candidate upon confirmation",
            ],
            "cross_domain_analog": {
                "ecological": "tide_pool_ecological (open dissipative cycle with reset; R‡ analog to R_⇔ kinetic gating)",
                "temporal": "proline_aldol_cycle (reset mechanism, cyclic topology, K_turnm)",
            },
        },
    )

