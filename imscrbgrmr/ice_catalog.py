"""
Ice Phase Imscription Catalog — v0.4.13

Primitive-tuple encodings for the ice phase ladder and liquid water ocean,
derived from the tensor session that produced the Dominant Triple Theorem
(IG.md §XXVI, METAPHYSICS.md §XX.2).

Phases encoded:

  Ice VI         — Base K_teshlig parent: high-pressure ordered ice, ~1 GPa
  Ice VII        — Symmetric phase: body-centred cubic, P_SC_SYM, >2 GPa
  Ice X          — Proton-symmetric: covalent O-H-O bonds, >60 GPa; closest
                   inorganic material to biological R_downstep via pressure alone
  Ice XVIII      — Superionic: oxygen lattice + fluid protons; ⊙ (ionic SOC)
  Ice XXI        — Metastable tetragonal, room-temperature K_teshlig, >2 GPa;
                   discovered 2025 European XFEL; Dominant Triple carrier
  Ice QCP        — Quantum critical point superionic phase (T_network_sym);
                   theoretical maximum for K_teshlig system toward dissolution state
  Liquid Water Ocean — Reference oceanic ocean: T_nrleg, 𐑢, K_turnm baseline

Key tensor results (IG.md §XXVI):
  ΔI ceiling from any K_teshlig ice to 5-MeO: 1.891 nats (D_supra/K_teshlig mismatches)
  Ice QCP achieves ΔI = 2.837 to 5-MeO (T_network_sym match; best K_teshlig system)
  Ice XXI → 5-MeO: ΔI = 0.000 (Dominant Triple absorbs all mediators)

Design principles:
  - K_teshlig is the diagnostic for ice phases: pressure confinement freezes proton
    dynamics; only superionic/QCP phases escape to K_turnm
  - T encodes proton network: cage (XXI), network_sym (QCP), network_mixed (XVIII),
    network_interpenetrating (VI/VII), network (X/liquid)
  - < distinguishes ionic criticality: ⊙ only for phases with documented
    SOC statistics or quantum critical fluctuations (XVIII, QCP)
  - R_COVALENT_DYNAMIC (Ice X, XVIII, QCP) marks the extreme-pressure
    proton-symmetrisation equivalent to R_downstep in biological systems

Recorded 2026-03-20. Source: live tensor session during Ice XXI drop.
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

_ICE_NAMES = frozenset([
    "ice_vi",
    "ice_vii",
    "ice_x",
    "ice_xviii_superionic",
    "ice_xxi",
    "ice_superionic_qcp",
    "liquid_water_ocean",
])


def register_ice_imscriptions() -> List[str]:
    """
    Register 7 ice phase / water imscriptions into the global catalog.
    Safe to call multiple times (idempotent).
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
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata)
    return registered


def _build_entries() -> List[Imscription]:
    return [
        _ice_vi(),
        _ice_vii(),
        _ice_x(),
        _ice_xviii_superionic(),
        _ice_xxi(),
        _ice_superionic_qcp(),
        _liquid_water_ocean(),
    ]


# ── Ice VI ─────────────────────────────────────────────────────────────────────
def _ice_vi() -> Imscription:
    """
    Ice VI — high-pressure ordered ice, ~0.6–2 GPa.

    Tetragonal structure with two interpenetrating sub-lattices; ordered proton
    arrangement; fully K_teshlig (no proton dynamics); base of the K_teshlig ice ladder.
    P_SC_PSEUDO: the two interpenetrating sub-lattices each self-complement but the
    inter-lattice polarity is pseudo-symmetric (not ideal self-complementary).

    ΔI to 5-MeO: bounded by K_teshlig/K_turnm mismatch and D mismatch.
    """
    return Imscription(
        name="ice_vi",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.ado,
        polarity=Polarity.yew,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        metadata={
            "description": "Ice VI — tetragonal ordered high-pressure ice, ~0.6–2 GPa",
            "pressure_range_GPa": "0.6–2.2",
            "temperature_K": "273 (at 1 GPa)",
            "topology_note": "Two interpenetrating H-bond sub-lattices",
            "k_note": "K_teshlig: proton positions fixed, no proton hopping",
            "discovery": "Bridgman 1912",
            "delta_i_to_5meo_ceiling": 1.891,
            "catalog_version": "0.4.13",
        },
    )


# ── Ice VII ─────────────────────────────────────────────────────────────────────
def _ice_vii() -> Imscription:
    """
    Ice VII — body-centred cubic, >2 GPa.

    Two interpenetrating H-bond networks; P_SELF_COMPLEMENTARY_SYM (proton positions
    disordered but site symmetry maintained on average); K_teshlig (proton dynamics
    frozen on crystallographic timescale). Stable at room temperature above ~3 GPa.

    First K_teshlig phase to show P_SC_SYM — symmetry is site-averaged, not
    time-averaged. ΔI to 5-MeO: ~1.891 nats (same K_teshlig ceiling as Ice VI
    but P-match improves).
    """
    return Imscription(
        name="ice_vii",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.ado,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        metadata={
            "description": "Ice VII — body-centred cubic, proton-disordered, >2 GPa",
            "pressure_range_GPa": ">2.2",
            "temperature_K": "300 (stable at >3 GPa)",
            "topology_note": "T_network_interp: two interpenetrating cubic H-bond networks",
            "polarity_note": "P_SC_SYM: proton sites symmetric on average (disorder)",
            "k_note": "K_teshlig: proton tunneling rate negligible at this pressure",
            "transition_to": "Ice X at ~60 GPa",
            "delta_i_to_5meo_ceiling": 1.891,
            "catalog_version": "0.4.13",
        },
    )


# ── Ice X ──────────────────────────────────────────────────────────────────────
def _ice_x() -> Imscription:
    """
    Ice X — proton-symmetric, >60 GPa.

    Protons sit exactly midway in O-H-O bonds (covalent-equivalent O-H distance).
    R_COVALENT_DYNAMIC: the most important feature — pressure alone achieves the
    O-H symmetrisation that enzyme active sites achieve via electrostatic fine-tuning.
    This is the closest inorganic material to biological R_downstep.

    Still K_teshlig (proton position is locked at the midpoint — symmetry does not
    mean mobility). Still 𐑢 (no SOC statistics documented). P_SC_SYM.
    """
    return Imscription(
        name="ice_x",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        metadata={
            "description": "Ice X — proton-symmetric covalent O-H-O bonds, >60 GPa",
            "pressure_range_GPa": ">60",
            "topology_note": "T_nrleg (cubic), but proton mid-point locked",
            "recognition_note": (
                "R_COVALENT_DYNAMIC: O-H-O bonds are fully covalent-symmetric. "
                "Closest inorganic material to R_downstep (enzyme catalytic geometry) — "
                "achieved by pressure alone, not protein engineering."
            ),
            "k_note": "K_teshlig: proton position locked at midpoint (not mobile)",
            "phi_note": "𐑢: no documented SOC statistics",
            "biological_analogue": "R_downstep in enzyme active sites",
            "catalog_version": "0.4.13",
        },
    )


# ── Ice XVIII (Superionic) ─────────────────────────────────────────────────────
def _ice_xviii_superionic() -> Imscription:
    """
    Ice XVIII — superionic ice, ~100–300 GPa, >2000 K.

    Oxygen atoms form a fixed body-centred cubic lattice; protons are fluid.
    Encoded as K_turnm: the proton fluid is faster than crystal lattice dynamics
    (K_teshlig) but does not reach the pharmacological-timescale K_frtailgamma of the
    psychedelic catalog. K_turnm captures the intermediate: active proton transport
    at geological/planetary timescales.

    ⊙: SOC-like fluctuations in the proton fluid documented in laser-driven
    shock experiments (Millot et al. 2018, Nature Physics).

    T_network_mixed: the O-lattice is NETWORK_INTERPENETRATING but the proton
    fluid introduces MIXED topology — the effective H-bond network is neither
    static cage nor simple network.
    """
    return Imscription(
        name="ice_xviii_superionic",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.loll,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.monad,
        metadata={
            "description": "Ice XVIII — superionic, O-lattice fixed + H-fluid, >100 GPa, >2000 K",
            "pressure_range_GPa": "100–300",
            "temperature_K": ">2000",
            "k_note": (
                "K_turnm: proton fluid is intermediate — faster than K_teshlig but slower "
                "than pharmacological K_frtailgamma. Planetary/geological timescale."
            ),
            "topology_note": "T_network_mixed: O-lattice interp + fluid H topology = mixed",
            "phi_note": "⊙: SOC-like proton fluid dynamics (Millot et al. 2018, NatPhys)",
            "relevance": "Planetary interior analogue; Neptune/Uranus mantle candidate",
            "catalog_version": "0.4.13",
        },
    )


# ── Ice XXI ────────────────────────────────────────────────────────────────────
def _ice_xxi() -> Imscription:
    """
    Ice XXI — metastable tetragonal, room-temperature K_teshlig, >2 GPa.

    Discovered 2025, European XFEL (Gawande et al.). Formed by compressing liquid
    water at room temperature to >2 GPa; distinct from Ice VI (different diffraction
    pattern, unique space group).

    Key distinction: room-temperature kinetic stability via pressure-induced barrier.
    K_teshlig achieved thermodynamically, not cryogenically.

    This is the DOMINANT TRIPLE CARRIER:
      {T_cage, K_teshlig, P_SC_PSEUDO} — absorbing element of tensor products.
      Any tensor chain beginning with Ice XXI produces the dominant triple in
      the intermediate; no mediator can bridge to the dissolution state.
      (IG.md §XXVI, METAPHYSICS.md §XX.2, Theorem 001)

    T_cage: pressure-stabilised cage topology, structurally distinct from Ice VII's
    interpenetrating networks. P_SC_PSEUDO: tetragonal distortion breaks cubic
    symmetry — pseudo-symmetric, not ideal self-complementary.
    F_MEDIUM (not HIGH): the tetragonal distortion introduces sub-ideal H-bond
    geometry; fidelity degraded relative to Ice VII.
    """
    return Imscription(
        name="ice_xxi",
        dimensionality=Dimensionality.ash,
        topology=Topology.oil,
        recognition_mode=RecognitionMode.ado,
        polarity=Polarity.yew,
        fidelity=Fidelity.they,
        kinetic_character=KineticCharacter.on,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        metadata={
            "description": (
                "Ice XXI — metastable tetragonal high-pressure ice, discovered 2025 XFEL. "
                "Room-temperature K_teshlig. Dominant Triple carrier."
            ),
            "discovery": "Gawande et al. 2025, European XFEL",
            "pressure_range_GPa": ">2",
            "temperature_K": "~300 (room temperature, metastable)",
            "topology_note": "T_cage: pressure-stabilised cage topology, distinct from interp networks",
            "polarity_note": "P_SC_PSEUDO: tetragonal distortion breaks full cubic symmetry",
            "fidelity_note": "F_MEDIUM: sub-ideal H-bond geometry due to tetragonal distortion",
            "k_note": "K_teshlig: room-temperature kinetic stability via pressure-induced barrier",
            "dominant_triple": True,
            "dominant_triple_components": ["𐑶", "𐑪", "<_SC_PSEUDO"],
            "theorem_001": "Dominant Triple Theorem — absorbing element of tensor products",
            "delta_i_to_5meo": 0.000,
            "delta_i_note": "Zero by absorbing dominance — not zero by similarity",
            "catalog_version": "0.4.13",
        },
    )


# ── Ice QCP (Superionic Quantum Critical Point) ────────────────────────────────
def _ice_superionic_qcp() -> Imscription:
    """
    Ice QCP — quantum critical point of the superionic phase (theoretical).

    At the quantum critical point separating the superionic phase from the ice X
    regime, quantum fluctuations become scale-free. The effective K character is
    K_turnm (same as Ice XVIII — the QCP is the same proton-fluid regime at its
    critical boundary, not a new faster dynamics).

    T_network_sym: at QCP, scale-free proton fluctuations obey full rotational
    symmetry — same topology as 5-MeO dissolution state. This T-match is what
    produces the maximum ΔI within the ice ladder (ΔI = 2.837 to 5-MeO).

    ⊙: quantum critical fluctuations are SOC-class by definition.
    """
    return Imscription(
        name="ice_superionic_qcp",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.tot,
        polarity=Polarity.or_,
        fidelity=Fidelity.peep,
        kinetic_character=KineticCharacter.loll,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.monad,
        metadata={
            "description": (
                "Ice QCP — quantum critical point of superionic ice (theoretical). "
                "Maximum ΔI achievable from K_teshlig ice ladder toward 5-MeO state."
            ),
            "status": "theoretical / extrapolated from Ice XVIII trajectory",
            "topology_note": "T_network_sym: scale-free QCP fluctuations, full rotational symmetry",
            "k_note": "K_turnm: same proton-fluid dynamics as Ice XVIII at critical boundary",
            "phi_note": "⊙: quantum critical fluctuations are SOC-class by definition",
            "delta_i_to_5meo": 2.837,
            "delta_i_note": (
                "Maximum achievable from any material K_teshlig system. "
                "T_network_sym match with 5-MeO. Residual gap from D_supra/D_temporal."
            ),
            "ice_ladder_position": "Top of K_teshlig escape ladder (theoretical endpoint)",
            "catalog_version": "0.4.13",
        },
    )


# ── Liquid Water Ocean ─────────────────────────────────────────────────────────
def _liquid_water_ocean() -> Imscription:
    """
    Liquid Water Ocean — ambient oceanic reference, ~1 bar, ~275–300 K.

    Bulk liquid water as a imscription: T_nrleg (hydrogen bond network, dynamic
    restructuring on ps timescale); K_turnm (proton hopping and H-bond reorganisation
    at moderate rates); 𐑢 (no SOC statistics documented for bulk water).
    P_SC_PSEUDO: water molecules are self-complementary (donor/acceptor in every
    H-bond) but the liquid pseudo-symmetry is not ideal (angular disorder).

    This is the reference base state from which the ice phase ladder departs
    upward under pressure. In the ladder: liquid → Ice VI (pressure freezes K_turnm
    to K_teshlig) → Ice VII → Ice X → Ice XVIII → QCP.
    """
    return Imscription(
        name="liquid_water_ocean",
        dimensionality=Dimensionality.ash,
        topology=Topology.judge,
        recognition_mode=RecognitionMode.ado,
        polarity=Polarity.yew,
        fidelity=Fidelity.they,
        kinetic_character=KineticCharacter.loll,
        granularity=Granularity.bib,
        interaction_grammar=InteractionGrammar.vow,
        criticality_phase=CriticalityPhase.woe,
        metadata={
            "description": "Liquid water ocean — ambient oceanic reference, ~1 bar, 275–300 K",
            "pressure_bar": "~1",
            "temperature_K": "275–300",
            "topology_note": "T_nrleg: H-bond network, ps-scale restructuring",
            "k_note": "K_turnm: proton hopping + H-bond reorganisation at moderate rates",
            "phi_note": "𐑢: no SOC statistics for bulk water",
            "role": "Base reference state; ladder bottom before pressure-induced K_teshlig transition",
            "catalog_version": "0.4.13",
        },
    )
