"""
Fundamental Particle Imscription Catalog — v0.4.21

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
  - K_frtailgamma is the signature of massless carriers (graviton, photon, gluon)
  - K_teshlig is the signature of mass-acquired carriers (W, Z after Higgs coupling)
  - K_schwa encodes the Higgs frozen vacuum expectation value
  - T_network_sym distinguishes spin-2 (graviton) from spin-1 (photon: T_linear)
  - T_nrleg for gluon encodes colour flux tube confinement (topology, not mass)
  - T_bullseye for Higgs encodes the cyclic EW symmetry-breaking self-coupling loop
  - ⊙ for graviton: GR's non-linear self-coupling (gravitons source curvature)
  - ⊙ for gluon: QCD asymptotic freedom + non-perturbative self-organisation
  - G_revapostrophe (graviton, photon): cosmological reach
  - G_gamma (gluon): confined to hadronic scale (~1 fm)
  - G_beta (W, Z, Higgs): single-particle coupling

See METAPHYSICS.md §XXVII for full structural derivations and §XXVI for
the photon encoding that anchors this catalog.

Recorded 2026-03-21. Qwen validation document: graviton (D_holo, T_braid,
K_frtailgamma, ⊙, Ω_Z) and Higgs (D_wynn, T_bullseye, K_schwa, G_local, ⊙, Ω_0)
incorporated and reconciled with framework primitives. Note: Qwen's T_braid
for the graviton was replaced by T_network_sym — T_braid encodes anyonic
exchange statistics (fractional QHE, Kitaev), not spin-2 metric perturbation
symmetry. T_network_sym (symmetric bcc-like connectivity) is the correct
encoding for the graviton's symmetric rank-2 tensor coupling.
"""
from __future__ import annotations

from typing import List

from .models import (
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


def register_particle_imscriptions() -> List[str]:
    """
    Register 6 fundamental particle imscriptions into the global catalog.
    Safe to call multiple times (idempotent).
    For pre-existing entries (e.g., photon from quantum domain v0.4.0),
    topology and criticality_phase are updated to the authoritative §XXVI/§XXVII
    encodings since particle_catalog is the canonical source for these.
    Returns list of names newly registered.
    """
    entries = _build_entries()
    registered = []
    for s in entries:
        if s.name not in global_catalog._imscriptions:
            global_catalog.register(s)
            registered.append(s.name)
        else:
            existing = global_catalog._imscriptions[s.name]
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


def _build_entries() -> List[Imscription]:
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

def _graviton() -> Imscription:
    """
    Graviton — hypothetical spin-2 massless carrier of gravity.

    ⟨D_holo; T_∈(sym); R_†; P_±^sym; F_ℏ; K_frtailgamma; G_ℵ; Γ_∨(BROAD); ⊙⟩

    Structural derivation (METAPHYSICS.md §XXVII.3):

    K_frtailgamma: massless — zero K_teshlig spatial localisation, identical K-hierarchy
    to the photon (K_teshlig temporal + K_frtailgamma). Propagates at c (K_frtailgamma ceiling).

    T_network_sym: spin-2 = symmetric rank-2 tensor coupling = couples
    identically in all spatial orientations simultaneously. Diffeomorphism
    invariance of GR = coordinate-independent symmetric connectivity.
    Distinguishes graviton from photon (T_linear, spin-1 vector).

    D_holo: GR exhibits holographic structure — bulk gravitational degrees of
    freedom encoded on the boundary (AdS/CFT, §XVIII). D_holo is the natural
    dimensional encoding for a field that propagates the geometry of space itself.

    G_revapostrophe: universal coupling — graviton couples to all K_teshlig spatial
    (all mass-energy) at all scales. No selectivity restriction.

    ⊙: GR is self-referential. Gravitons carry energy-momentum, which is
    itself a source of spacetime curvature. This non-linear self-coupling
    (absent in EM) is the structural origin of the non-linearity of Einstein's
    field equations and the challenge of perturbative quantum gravity.

    Note on Qwen validation: Qwen proposed T_braid for the graviton. T_braid
    encodes anyonic/braided exchange statistics (fractional QHE, non-abelian
    anyons). The graviton's spin-2 symmetry is better captured by T_network_sym.
    Qwen's D_holo and ⊙ are confirmed.

    Prediction: P-59 (c propagation, no dispersion), P-60 (tensorial polarisation
    only — no scalar/vector modes).
    """
    return Imscription(
        name="graviton",
        dimensionality=Dimensionality.if_,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.yea,
        granularity=Granularity.thigh,
        interaction_grammar=InteractionGrammar.gag,
        criticality_phase=CriticalityPhase.monad,
        description=(
            "Graviton: hypothetical spin-2 massless carrier of gravity. "
            "K_frtailgamma: massless, propagates at c. T_network_sym: symmetric rank-2 tensor "
            "coupling (spin-2), all orientations. D_holo: GR holographic structure. "
            "G_revapostrophe: universal coupling to all K_teshlig spatial (all mass-energy). "
            "⊙: GR non-linear self-coupling (gravitons source curvature). "
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


def _photon() -> Imscription:
    """
    Photon — spin-1 massless carrier of electromagnetism.

    ⟨D_∞; T_|; R_†; P_+-; F_ℏ; K_frtailgamma; G_ℵ; Γ_∨(SELECTIVE); 𐑢⟩

    Structural derivation (METAPHYSICS.md §XXVI):

    K_frtailgamma: massless — zero K_teshlig spatial, propagates at c.
    K_teshlig temporal: locked emission frequency/polarisation (the 'particle' aspect).
    Two-tier K-hierarchy (K_teshlig temporal + K_frtailgamma) = wave-particle duality.

    T_linear: spin-1 vector coupling = directional EM field asymmetry.
    Contrasts with graviton (T_network_sym, spin-2).

    D_infinity: fundamentally periodic (EM wave).

    G_revapostrophe: cosmological reach. But G_beta coupling: only to charged particles.
    Encoded here as G_revapostrophe for reach, with SELECTIVE Gamma for charged-only.

    Phi_softsign: the photon is not self-referential — EM is linear (photons do not
    couple to other photons in QED at tree level). Contrast with graviton ⊙.
    """
    return Imscription(
        name="photon",
        dimensionality=Dimensionality.array,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.church,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.yea,
        granularity=Granularity.thigh,
        interaction_grammar=InteractionGrammar.gag,
        criticality_phase=CriticalityPhase.woe,
        description=(
            "Photon: spin-1 massless carrier of electromagnetism. "
            "K_frtailgamma: massless, propagates at c. K_teshlig temporal: locked frequency/polarisation "
            "(particle aspect). T_linear: directional spin-1 vector coupling. "
            "D_infinity: periodic EM wave. G_revapostrophe reach + SELECTIVE coupling (charged only). "
            "Phi_softsign: EM is linear (tree-level photon self-coupling absent)."
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


def _gluon() -> Imscription:
    """
    Gluon — spin-1 massless carrier of the strong force (QCD).

    ⟨D_△; T_∈; R_†; P_±^sym; F_ℏ; K_frtailgamma; G_ג; Γ_∨(BROAD); ⊙⟩

    Structural derivation (METAPHYSICS.md §§XXVI.3, XXVII.8):

    K_frtailgamma: massless — zero K_teshlig spatial. But short-range despite masslessness.

    Short range NOT from K_teshlig mass (like W/Z) but from T_nrleg confinement:
    colour flux tubes (T_nrleg topology) form between colour charges. The T-topology
    itself confines quarks — gluons cannot escape the colour-connected network.
    The range mechanism is T-topological, not kinetic. (§XXVI.3 force range table.)

    T_nrleg: colour flux tubes form networks between quarks in hadrons.
    Gluons themselves carry colour charge — they are part of the T_nrleg they create.

    G_gamma (mesoscale): confined to hadronic scale (~1 fm). Contrast with
    graviton and photon (G_revapostrophe = cosmological reach).

    ⊙: QCD exhibits asymptotic freedom (coupling → 0 at high energy) and
    confinement (coupling → ∞ at low energy). The transition between these regimes
    involves genuine self-organisation and non-perturbative structure. The
    SU(3) gauge group's non-abelian structure (8 gluons carrying colour) makes
    QCD self-referential in a way QED (abelian U(1)) is not.
    """
    return Imscription(
        name="gluon",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.yea,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.gag,
        criticality_phase=CriticalityPhase.monad,
        description=(
            "Gluon: spin-1 massless carrier of the strong force (QCD). "
            "K_frtailgamma: massless. Short-range NOT from K_teshlig mass but from T_nrleg "
            "confinement — colour flux tubes confine quarks topologically. "
            "G_gamma: confined to hadronic scale. T_nrleg: 8 gluons form colour flux "
            "tube networks. ⊙: QCD asymptotic freedom + non-perturbative confinement; "
            "non-abelian SU(3) makes QCD self-referential."
        ),
        metadata={
            "domain_category": "particle_massless_carrier",
            "spin": 1,
            "mass_ev": 0.0,
            "force": "strong_QCD",
            "k_trap_spatial": False,
            "range": "confined_1fm_T_topology",
            "range_mechanism": "𐑡_confinement_not_K_trap_mass",
            "colour_charges": 8,
            "coupling_target": "colour_charge",
            "metaphysics_section": "XXVI.3",
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP II — MASSIVE FORCE CARRIERS + SYMMETRY-BREAKING FIELD
# ===========================================================================

def _w_boson() -> Imscription:
    """
    W± boson — charged massive carrier of the weak force.

    ⟨D_∧; T_|; R_†; P_+-; F_ℏ; K_teshlig; G_ב; Γ_∧(SELECTIVE); 𐑢⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    K_teshlig: massive (m_W ≈ 80.4 GeV) — acquired K_teshlig spatial from Higgs coupling
    after electroweak symmetry breaking (§XXVI.2). K_teshlig spatial → Yukawa range
    (~1/m_W ≈ 0.002 fm). Short-range from kinetic trapping, not T-topology.

    T_linear: spin-1 vector boson — charged current coupling (W+: u→d+e+ν;
    W-: d→u+e+ν). Directional charge transfer.

    P_directional (donor-acceptor): W boson couples asymmetrically — W+ carries
    positive charge from quark to lepton vertex; W- carries negative charge.

    G_beta (local): couples to individual particles (quark doublets, lepton doublets)
    at the single-vertex level.

    Phi_softsign: the massive W is in its post-symmetry-breaking (frozen) phase.
    The EW phase transition (⊙) has already completed.
    """
    return Imscription(
        name="w_boson",
        dimensionality=Dimensionality.dead,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.church,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        description=(
            "W± boson: charged massive carrier of the weak force. "
            "K_teshlig: massive (80.4 GeV), K_teshlig spatial installed by Higgs coupling. "
            "Short range (~0.002 fm) from K_teshlig mass (Yukawa suppression). "
            "T_linear: charged current coupling, directional charge transfer. "
            "G_beta: single-particle coupling. Phi_softsign: post-EW-symmetry-breaking phase."
        ),
        metadata={
            "domain_category": "particle_massive_carrier",
            "spin": 1,
            "mass_ev": 80.4e9,
            "force": "weak",
            "k_trap_spatial": True,
            "range_fm": 0.002,
            "range_mechanism": "⊤_trap_mass_Yukawa",
            "coupling_target": "weak_isospin_doublets",
            "higgs_coupling": True,
            "metaphysics_section": "XXVII.8",
            "validation_tier": "primary",
        },
    )


def _z_boson() -> Imscription:
    """
    Z⁰ boson — neutral massive carrier of the weak force.

    ⟨D_∧; T_|; R_†; P_±^sym; F_ℏ; K_teshlig; G_ב; Γ_∧(SELECTIVE); 𐑢⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    Identical to W± in K-hierarchy (K_teshlig, Higgs-acquired mass), T-topology
    (T_linear, spin-1), and G-scope (G_beta). Differs in polarity:

    P_doublebarpipe (self-complementary symmetric): Z⁰ is neutral — it couples
    symmetrically to both particles and antiparticles without charge transfer.
    The neutral current has no preferred direction, unlike the charged current
    of the W.

    G_beta: single-particle coupling. Short range via K_teshlig mass (m_Z ≈ 91.2 GeV,
    shorter range than W: ~0.002 fm).
    """
    return Imscription(
        name="z_boson",
        dimensionality=Dimensionality.dead,
        topology=Topology.eat,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        description=(
            "Z⁰ boson: neutral massive carrier of the weak force. "
            "K_teshlig: massive (91.2 GeV), K_teshlig spatial from Higgs. "
            "T_linear: spin-1 neutral current (no charge transfer). "
            "P_doublebarpipe: symmetric neutral coupling (particles + antiparticles equally). "
            "G_beta: single-particle. Phi_softsign: post-EW-breaking."
        ),
        metadata={
            "domain_category": "particle_massive_carrier",
            "spin": 1,
            "mass_ev": 91.2e9,
            "force": "weak",
            "k_trap_spatial": True,
            "range_fm": 0.002,
            "range_mechanism": "⊤_trap_mass_Yukawa",
            "coupling_target": "weak_neutral_current_all_fermions",
            "higgs_coupling": True,
            "metaphysics_section": "XXVII.8",
            "validation_tier": "primary",
        },
    )


def _higgs() -> Imscription:
    """
    Higgs boson / Higgs field — K_teshlig spatial localisation installer.

    ⟨D_∧; T_⋈; R_†; P_±^sym; F_ℏ; K_schwa; G_ב; Γ_∧(SELECTIVE); 𐑢⟩

    Structural derivation (METAPHYSICS.md §§XXVI.2, XXVII.8):

    K_schwa: the Higgs vacuum expectation value (VEV = 246 GeV) is quasi-static
    below the electroweak phase transition temperature (~100 GeV). The Higgs
    field is a frozen landscape — it does not oscillate on particle timescales.
    K_schwa = the dominant kinetic character: a frozen high-barrier state
    (the EW symmetry-broken vacuum). K_teshlig would encode the excitation (Higgs
    boson at 125 GeV); K_schwa encodes the VEV substrate.

    T_bullseye: cyclic self-coupling loop. The Higgs mechanism is a self-consistent
    cycle: (1) EW symmetry breaking occurs → (2) W/Z acquire K_teshlig spatial →
    (3) W/Z couple back to the Higgs to maintain the broken vacuum → (4) the
    broken vacuum maintains the Higgs mass. T_bullseye encodes this cyclic
    back-coupling (the Mexican hat potential's self-referential ground state).

    D_wynn (molecular): couples at the individual particle level.

    G_beta: local coupling — Higgs couples to individual particles via Yukawa terms.
    Does NOT couple to photon (U(1) unbroken) or gluon (SU(3) unbroken).
    SELECTIVE: couples to W, Z, and all massive fermions; not to massless carriers.

    Phi_softsign: the low-temperature broken phase is below criticality. The EW phase
    transition itself (T ~ 100 GeV, where EW symmetry breaks) is the ⊙ event.
    Below it, the Higgs VEV is frozen (Phi_softsign = post-critical frozen state).

    Note: Qwen proposed ⊙ for the Higgs. This is correct at the EW transition
    but the ground-state Higgs is Phi_softsign (frozen condensate). The distinction
    matters: the Higgs *creates* a ⊙ event (symmetry breaking) but *lives* in
    Phi_softsign (the broken phase).
    """
    return Imscription(
        name="higgs",
        dimensionality=Dimensionality.dead,
        topology=Topology.mime,
        recognition_mode=RecognitionMode.ear,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.egg,
        granularity=Granularity.ice,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        description=(
            "Higgs boson/field: K_teshlig spatial localisation installer. "
            "K_schwa: frozen VEV (246 GeV) below EW phase transition. "
            "T_bullseye: cyclic self-coupling — EW symmetry breaking self-consistent loop. "
            "D_wynn + G_beta: particle-level local coupling. "
            "SELECTIVE: couples to W, Z, massive fermions; NOT to photon or gluon. "
            "Phi_softsign: broken-phase frozen condensate (⊙ was the EW transition)."
        ),
        metadata={
            "domain_category": "particle_scalar_field",
            "spin": 0,
            "mass_ev": 125.1e9,
            "force": "electroweak_symmetry_breaking",
            "k_trap_spatial": False,
            "k_slow_vev_gev": 246.0,
            "higgs_mechanism": "⊤_trap_spatial_installer_for_W_Z_fermions",
            "does_not_couple": ["photon", "gluon"],
            "metaphysics_section": "XXVI.2, XXVII.8",
            "qwen_validation": {
                "d_wedge": "confirmed",
                "t_bowtie": "confirmed",
                "k_slow": "confirmed",
                "g_local_as_G_beth": "confirmed",
                "phi_c_clarified": "⊙ at EW transition; Phi_softsign in broken phase",
            },
            "validation_tier": "primary",
        },
    )
