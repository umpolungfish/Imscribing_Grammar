"""
Fundamental Particle Synthon Catalog — v0.4.21

Primitive-tuple encodings for Standard Model carriers and the graviton,
derived from the Imscribing Grammar framework's K-hierarchy temporal theory
(METAPHYSICS.md §§XXIV–XXVII) and Qwen's independently validated
graviton/Higgs/gauge boson encodings.

Covers 7 entries across two groups:

  Group I  — Force carriers (massless)
             Graviton, Photon, Gluon
  Group II — Force carriers (massive) + symmetry-breaking field
             W_boson, Z_boson, Higgs

Design principles:
  - K_fast is the signature of massless carriers (graviton, photon, gluon)
  - K_trap is the signature of mass-acquired carriers (W, Z after Higgs coupling)
  - K_slow encodes the Higgs frozen vacuum expectation value
  - T_network_sym distinguishes spin-2 (graviton) from spin-1 (photon: T_linear)
  - T_network for gluon encodes colour flux tube confinement (topology, not mass)
  - T_bowtie for Higgs encodes the cyclic EW symmetry-breaking self-coupling loop
  - Φ_c for graviton: GR's non-linear self-coupling (gravitons source curvature)
  - Φ_c for gluon: QCD asymptotic freedom + non-perturbative self-organisation
  - G_aleph (graviton, photon): cosmological reach
  - G_gimel (gluon): confined to hadronic scale (~1 fm)
  - G_beth (W, Z, Higgs): single-particle coupling

See METAPHYSICS.md §XXVII for full structural derivations and §XXVI for
the photon encoding that anchors this catalog.

Recorded 2026-03-21. Qwen validation document: graviton (D_holo, T_braid,
K_fast, Φ_c, Ω_Z) and Higgs (D_wedge, T_bowtie, K_slow, G_local, Φ_c, Ω_0)
incorporated and reconciled with framework primitives. Note: Qwen's T_braid
for the graviton was replaced by T_network_sym — T_braid encodes anyonic
exchange statistics (fractional QHE, Kitaev), not spin-2 metric perturbation
symmetry. T_network_sym (symmetric bcc-like connectivity) is the correct
encoding for the graviton's symmetric rank-2 tensor coupling.
"""
from __future__ import annotations

from typing import List

from .models import (
    Synthon,
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
from .registry import global_catalog


_PARTICLE_NAMES = frozenset([
    # Group I — Massless force carriers
    "graviton",
    "photon",
    "gluon",
    # Group II — Massive force carriers + symmetry-breaking field
    "w_boson",
    "z_boson",
    "higgs",
])


def register_particle_synthons() -> List[str]:
    """
    Register 6 fundamental particle synthons into the global catalog.
    Safe to call multiple times (idempotent).
    For pre-existing entries (e.g., photon from quantum domain v0.4.0),
    topology and criticality_phase are updated to the authoritative §XXVI/§XXVII
    encodings since particle_catalog is the canonical source for these.
    Returns list of names newly registered.
    """
    entries = _build_entries()
    registered = []
    for s in entries:
        if s.name not in global_catalog._synthons:
            global_catalog.register(s)
            registered.append(s.name)
        else:
            existing = global_catalog._synthons[s.name]
            # Update topology and criticality from authoritative particle encodings
            existing.topology = s.topology
            existing.kinetic_character = s.kinetic_character
            existing.criticality_phase = s.criticality_phase
            existing.granularity = s.granularity
            existing.interaction_grammar = s.interaction_grammar
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata)
            existing.metadata["particle_catalog_updated"] = True
    return registered


def _build_entries() -> List[Synthon]:
    return [
        # Group I — Massless
        _graviton(),
        _photon(),
        _gluon(),
        # Group II — Massive + Higgs
        _w_boson(),
        _z_boson(),
        _higgs(),
    ]


# ===========================================================================
# GROUP I — MASSLESS FORCE CARRIERS
# ===========================================================================

def _graviton() -> Synthon:
    """
    Graviton — hypothetical spin-2 massless carrier of gravity.

    ⟨D_holo; T_∈(sym); R_†; P_±^sym; F_ℏ; K_fast; G_ℵ; Γ_∨(BROAD); Φ_c⟩

    Structural derivation (METAPHYSICS.md §XXVII.3):

    K_fast: massless — zero K_trap spatial localisation, identical K-hierarchy
    to the photon (K_trap temporal + K_fast). Propagates at c (K_fast ceiling).

    T_network_sym: spin-2 = symmetric rank-2 tensor coupling = couples
    identically in all spatial orientations simultaneously. Diffeomorphism
    invariance of GR = coordinate-independent symmetric connectivity.
    Distinguishes graviton from photon (T_linear, spin-1 vector).

    D_holo: GR exhibits holographic structure — bulk gravitational degrees of
    freedom encoded on the boundary (AdS/CFT, §XVIII). D_holo is the natural
    dimensional encoding for a field that propagates the geometry of space itself.

    G_aleph: universal coupling — graviton couples to all K_trap spatial
    (all mass-energy) at all scales. No selectivity restriction.

    Phi_c: GR is self-referential. Gravitons carry energy-momentum, which is
    itself a source of spacetime curvature. This non-linear self-coupling
    (absent in EM) is the structural origin of the non-linearity of Einstein's
    field equations and the challenge of perturbative quantum gravity.

    Note on Qwen validation: Qwen proposed T_braid for the graviton. T_braid
    encodes anyonic/braided exchange statistics (fractional QHE, non-abelian
    anyons). The graviton's spin-2 symmetry is better captured by T_network_sym.
    Qwen's D_holo and Phi_c are confirmed.

    Prediction: P-59 (c propagation, no dispersion), P-60 (tensorial polarisation
    only — no scalar/vector modes).
    """
    return Synthon(
        name="graviton",
        dimensionality=Dimensionality.HOLOGRAPHIC,
        topology=Topology.NETWORK_SYM,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        description=(
            "Graviton: hypothetical spin-2 massless carrier of gravity. "
            "K_fast: massless, propagates at c. T_network_sym: symmetric rank-2 tensor "
            "coupling (spin-2), all orientations. D_holo: GR holographic structure. "
            "G_aleph: universal coupling to all K_trap spatial (all mass-energy). "
            "Phi_c: GR non-linear self-coupling (gravitons source curvature). "
            "Distinguishes from photon (T_linear, spin-1) by T_network_sym topology."
        ),
        metadata={
            "domain_category": "particle_massless_carrier",
            "spin": 2,
            "mass_ev": 0.0,
            "force": "gravity",
            "k_trap_temporal": True,
            "k_trap_spatial": False,
            "range": "infinite_1_over_r2",
            "coupling_target": "all_energy_momentum",
            "p_predictions": ["P-59", "P-60"],
            "metaphysics_section": "XXVII.3",
            "qwen_validation": {
                "d_holo": "confirmed",
                "t_braid": "replaced_by_T_network_sym",
                "k_fast": "confirmed",
                "phi_c": "confirmed",
            },
            "validation_tier": "extended",
        },
    )


def _photon() -> Synthon:
    """
    Photon — spin-1 massless carrier of electromagnetism.

    ⟨D_∞; T_|; R_†; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∨(SELECTIVE); Φ_sub⟩

    Structural derivation (METAPHYSICS.md §XXVI):

    K_fast: massless — zero K_trap spatial, propagates at c.
    K_trap temporal: locked emission frequency/polarisation (the 'particle' aspect).
    Two-tier K-hierarchy (K_trap temporal + K_fast) = wave-particle duality.

    T_linear: spin-1 vector coupling = directional EM field asymmetry.
    Contrasts with graviton (T_network_sym, spin-2).

    D_infinity: fundamentally periodic (EM wave).

    G_aleph: cosmological reach. But G_beth coupling: only to charged particles.
    Encoded here as G_aleph for reach, with SELECTIVE Gamma for charged-only.

    Phi_sub: the photon is not self-referential — EM is linear (photons do not
    couple to other photons in QED at tree level). Contrast with graviton Phi_c.
    """
    return Synthon(
        name="photon",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        description=(
            "Photon: spin-1 massless carrier of electromagnetism. "
            "K_fast: massless, propagates at c. K_trap temporal: locked frequency/polarisation "
            "(particle aspect). T_linear: directional spin-1 vector coupling. "
            "D_infinity: periodic EM wave. G_aleph reach + SELECTIVE coupling (charged only). "
            "Phi_sub: EM is linear (tree-level photon self-coupling absent)."
        ),
        metadata={
            "domain_category": "particle_massless_carrier",
            "spin": 1,
            "mass_ev": 0.0,
            "force": "electromagnetism",
            "k_trap_temporal": True,
            "k_trap_spatial": False,
            "range": "infinite_1_over_r2",
            "coupling_target": "electric_charge",
            "p_predictions": ["P-59_analogue"],
            "metaphysics_section": "XXVI",
            "validation_tier": "primary",
        },
    )


def _gluon() -> Synthon:
    """
    Gluon — spin-1 massless carrier of the strong force (QCD).

    ⟨D_△; T_∈; R_†; P_±^sym; F_ℏ; K_fast; G_ג; Γ_∨(BROAD); Φ_c⟩

    Structural derivation (METAPHYSICS.md §§XXVI.3, XXVII.8):

    K_fast: massless — zero K_trap spatial. But short-range despite masslessness.

    Short range NOT from K_trap mass (like W/Z) but from T_network confinement:
    colour flux tubes (T_network topology) form between colour charges. The T-topology
    itself confines quarks — gluons cannot escape the colour-connected network.
    The range mechanism is T-topological, not kinetic. (§XXVI.3 force range table.)

    T_network: colour flux tubes form networks between quarks in hadrons.
    Gluons themselves carry colour charge — they are part of the T_network they create.

    G_gimel (mesoscale): confined to hadronic scale (~1 fm). Contrast with
    graviton and photon (G_aleph = cosmological reach).

    Phi_c: QCD exhibits asymptotic freedom (coupling → 0 at high energy) and
    confinement (coupling → ∞ at low energy). The transition between these regimes
    involves genuine self-organisation and non-perturbative structure. The
    SU(3) gauge group's non-abelian structure (8 gluons carrying colour) makes
    QCD self-referential in a way QED (abelian U(1)) is not.
    """
    return Synthon(
        name="gluon",
        dimensionality=Dimensionality.SUPRAMOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        description=(
            "Gluon: spin-1 massless carrier of the strong force (QCD). "
            "K_fast: massless. Short-range NOT from K_trap mass but from T_network "
            "confinement — colour flux tubes confine quarks topologically. "
            "G_gimel: confined to hadronic scale. T_network: 8 gluons form colour flux "
            "tube networks. Phi_c: QCD asymptotic freedom + non-perturbative confinement; "
            "non-abelian SU(3) makes QCD self-referential."
        ),
        metadata={
            "domain_category": "particle_massless_carrier",
            "spin": 1,
            "mass_ev": 0.0,
            "force": "strong_QCD",
            "k_trap_spatial": False,
            "range": "confined_1fm_T_topology",
            "range_mechanism": "T_network_confinement_not_K_trap_mass",
            "colour_charges": 8,
            "coupling_target": "colour_charge",
            "metaphysics_section": "XXVI.3",
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP II — MASSIVE FORCE CARRIERS + SYMMETRY-BREAKING FIELD
# ===========================================================================

def _w_boson() -> Synthon:
    """
    W± boson — charged massive carrier of the weak force.

    ⟨D_∧; T_|; R_†; P_+-; F_ℏ; K_trap; G_ב; Γ_∧(SELECTIVE); Φ_sub⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    K_trap: massive (m_W ≈ 80.4 GeV) — acquired K_trap spatial from Higgs coupling
    after electroweak symmetry breaking (§XXVI.2). K_trap spatial → Yukawa range
    (~1/m_W ≈ 0.002 fm). Short-range from kinetic trapping, not T-topology.

    T_linear: spin-1 vector boson — charged current coupling (W+: u→d+e+ν;
    W-: d→u+e+ν). Directional charge transfer.

    P_directional (donor-acceptor): W boson couples asymmetrically — W+ carries
    positive charge from quark to lepton vertex; W- carries negative charge.

    G_beth (local): couples to individual particles (quark doublets, lepton doublets)
    at the single-vertex level.

    Phi_sub: the massive W is in its post-symmetry-breaking (frozen) phase.
    The EW phase transition (Phi_c) has already completed.
    """
    return Synthon(
        name="w_boson",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        description=(
            "W± boson: charged massive carrier of the weak force. "
            "K_trap: massive (80.4 GeV), K_trap spatial installed by Higgs coupling. "
            "Short range (~0.002 fm) from K_trap mass (Yukawa suppression). "
            "T_linear: charged current coupling, directional charge transfer. "
            "G_beth: single-particle coupling. Phi_sub: post-EW-symmetry-breaking phase."
        ),
        metadata={
            "domain_category": "particle_massive_carrier",
            "spin": 1,
            "mass_ev": 80.4e9,
            "force": "weak",
            "k_trap_spatial": True,
            "range_fm": 0.002,
            "range_mechanism": "K_trap_mass_Yukawa",
            "coupling_target": "weak_isospin_doublets",
            "higgs_coupling": True,
            "metaphysics_section": "XXVII.8",
            "validation_tier": "primary",
        },
    )


def _z_boson() -> Synthon:
    """
    Z⁰ boson — neutral massive carrier of the weak force.

    ⟨D_∧; T_|; R_†; P_±^sym; F_ℏ; K_trap; G_ב; Γ_∧(SELECTIVE); Φ_sub⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    Identical to W± in K-hierarchy (K_trap, Higgs-acquired mass), T-topology
    (T_linear, spin-1), and G-scope (G_beth). Differs in polarity:

    P_pm_sym (self-complementary symmetric): Z⁰ is neutral — it couples
    symmetrically to both particles and antiparticles without charge transfer.
    The neutral current has no preferred direction, unlike the charged current
    of the W.

    G_beth: single-particle coupling. Short range via K_trap mass (m_Z ≈ 91.2 GeV,
    shorter range than W: ~0.002 fm).
    """
    return Synthon(
        name="z_boson",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        description=(
            "Z⁰ boson: neutral massive carrier of the weak force. "
            "K_trap: massive (91.2 GeV), K_trap spatial from Higgs. "
            "T_linear: spin-1 neutral current (no charge transfer). "
            "P_pm_sym: symmetric neutral coupling (particles + antiparticles equally). "
            "G_beth: single-particle. Phi_sub: post-EW-breaking."
        ),
        metadata={
            "domain_category": "particle_massive_carrier",
            "spin": 1,
            "mass_ev": 91.2e9,
            "force": "weak",
            "k_trap_spatial": True,
            "range_fm": 0.002,
            "range_mechanism": "K_trap_mass_Yukawa",
            "coupling_target": "weak_neutral_current_all_fermions",
            "higgs_coupling": True,
            "metaphysics_section": "XXVII.8",
            "validation_tier": "primary",
        },
    )


def _higgs() -> Synthon:
    """
    Higgs boson / Higgs field — K_trap spatial localisation installer.

    ⟨D_∧; T_⋈; R_†; P_±^sym; F_ℏ; K_slow; G_ב; Γ_∧(SELECTIVE); Φ_sub⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    K_slow: the Higgs vacuum expectation value (VEV = 246 GeV) is quasi-static
    below the electroweak phase transition temperature (~100 GeV). The Higgs
    field is a frozen landscape — it does not oscillate on particle timescales.
    K_slow = the dominant kinetic character: a frozen high-barrier state
    (the EW symmetry-broken vacuum). K_trap would encode the excitation (Higgs
    boson at 125 GeV); K_slow encodes the VEV substrate.

    T_bowtie: cyclic self-coupling loop. The Higgs mechanism is a self-consistent
    cycle: (1) EW symmetry breaking occurs → (2) W/Z acquire K_trap spatial →
    (3) W/Z couple back to the Higgs to maintain the broken vacuum → (4) the
    broken vacuum maintains the Higgs mass. T_bowtie encodes this cyclic
    back-coupling (the Mexican hat potential's self-referential ground state).

    D_wedge (molecular): couples at the individual particle level.

    G_beth: local coupling — Higgs couples to individual particles via Yukawa terms.
    Does NOT couple to photon (U(1) unbroken) or gluon (SU(3) unbroken).
    SELECTIVE: couples to W, Z, and all massive fermions; not to massless carriers.

    Phi_sub: the low-temperature broken phase is below criticality. The EW phase
    transition itself (T ~ 100 GeV, where EW symmetry breaks) is the Phi_c event.
    Below it, the Higgs VEV is frozen (Phi_sub = post-critical frozen state).

    Note: Qwen proposed Phi_c for the Higgs. This is correct at the EW transition
    but the ground-state Higgs is Phi_sub (frozen condensate). The distinction
    matters: the Higgs *creates* a Phi_c event (symmetry breaking) but *lives* in
    Phi_sub (the broken phase).
    """
    return Synthon(
        name="higgs",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.LOCAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        description=(
            "Higgs boson/field: K_trap spatial localisation installer. "
            "K_slow: frozen VEV (246 GeV) below EW phase transition. "
            "T_bowtie: cyclic self-coupling — EW symmetry breaking self-consistent loop. "
            "D_wedge + G_beth: particle-level local coupling. "
            "SELECTIVE: couples to W, Z, massive fermions; NOT to photon or gluon. "
            "Phi_sub: broken-phase frozen condensate (Phi_c was the EW transition)."
        ),
        metadata={
            "domain_category": "particle_scalar_field",
            "spin": 0,
            "mass_ev": 125.1e9,
            "force": "electroweak_symmetry_breaking",
            "k_trap_spatial": False,
            "k_slow_vev_gev": 246.0,
            "higgs_mechanism": "K_trap_spatial_installer_for_W_Z_fermions",
            "does_not_couple": ["photon", "gluon"],
            "metaphysics_section": "XXVI.2, XXVII.8",
            "qwen_validation": {
                "d_wedge": "confirmed",
                "t_bowtie": "confirmed",
                "k_slow": "confirmed",
                "g_local_as_G_beth": "confirmed",
                "phi_c_clarified": "Phi_c at EW transition; Phi_sub in broken phase",
            },
            "validation_tier": "primary",
        },
    )
