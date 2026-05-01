"""
Quantum Domain Catalog — v0.4.0

Canonical encodings for quantum particles and topological matter synthons.
Eight synthons in two tiers:

  Tier 1 — Quantum Particles (five fundamental particles as recognition synthons):
    photon              D_∞  · T_⋈  · R_sup · P_±  · F_ℏ · K_fast · G_ℵ · Γ⊙(QUANTUM) · Φ_sub · Ω_0
    proton              D_∧  · T_■  · R_†   · P_+  · F_ℏ · K_fast · G_ℵ · Γ⊗          · Φ_sub · Ω_0
    electron            D_∧  · T_■  · R_sub · P_−  · F_ℏ · K_fast · G_ℵ · Γ⊗          · Φ_sub · Ω_0
    spin_singlet        D_∧  · T_⋈  · R_sup · P_±ψ · F_ℏ · K_trap · G_ℵ · Γ∧(QUANTUM) · Φ_sub · Ω_0
    qubit_logical       D_∧  · T_|  · R_sup · P_±ψ · F_ℓ · K_slow · G_ℵ · Γ∧(QUANTUM) · Φ_sub · Ω_0

  Tier 2 — Topological Matter (first catalog entries using T_braid + Ω):
    kitaev_chain_majorana   D_∧  · T_|      · R_sup · P_±  · F_ℏ · K_trap · G_ℵ · Γ∧(QUANTUM) · Φ_sub · Ω_Z
    fqh_moore_read          D_△  · T_braid  · R_sup · P_±ψ · F_ℏ · K_trap · G_ℵ · Γ∧(QUANTUM) · Φ_sub · Ω_NA
    topological_insulator   D_△  · T_∈      · R_sup · P_±  · F_ℏ · K_slow · G_ℵ · Γ⊙          · Φ_sub · Ω_Z₂

Key physics encoded:
  - spin_singlet is the first Factor 8 trigger: G_ℵ + F_ℏ + K_trap + ¬D_∞
    → quantum criticality (TFI/heavy-fermion class), χ(T→0) ~ T^{-γ}
  - kitaev_chain: K_trap (gap-protected) · Ω_Z (ℤ class-D invariant in 1D)
    · non-local Majorana qubit: left-end ⊗ right-end = one logical qubit
  - fqh_moore_read: T_braid (anyonic statistics) · Ω_NA (non-Abelian Ising anyons)
    · GSD = 3 on torus; fusion rules: σ × σ = 1 + ψ
  - topological_insulator: Ω_Z₂ (ℤ₂ class-AII, Kramers-protected)
    · T_network encodes the 2D surface-state network on the 3D bulk
  - MBL note: K_MBL deliberately absent from Tier 1; it belongs to disorder-driven
    phases. The K_trap→K_MBL perturbation (Δξ +2.30 nats, HIGH sensitivity) was
    identified as the largest single-primitive cost in the quantum playground sweep.

Primitive key justifications per synthon are embedded in each _build_* function.
"""
from __future__ import annotations

from typing import List

from ...models import (
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
    TopoIndex,
)
from ...registry import global_catalog


# ---------------------------------------------------------------------------
# Registry names (stable across versions — used as dict keys everywhere)
# ---------------------------------------------------------------------------

QUANTUM_SYNTHON_NAMES = frozenset([
    "photon",
    "proton",
    "electron",
    "spin_singlet",
    "qubit_logical",
    "kitaev_chain_majorana",
    "fqh_moore_read",
    "topological_insulator_bi2se3",
])


def register_quantum_synthons() -> List[str]:
    """
    Register all eight quantum/topological synthons into the global catalog.

    Safe to call multiple times (idempotent). Always refreshes metadata on
    already-present entries so Ω and topo_index fields survive JSON round-trips.

    Returns:
        List of names that were newly registered (empty if all already present).
    """
    entries = _build_all()
    registered = []
    for s in entries:
        if s.name not in global_catalog._synthons:
            global_catalog.register(s, domain="quantum", override_grounding=True,
                                    override_reason="Canonical quantum domain entry (v0.4.0)")
            registered.append(s.name)
        else:
            existing = global_catalog._synthons[s.name]
            # Refresh topo_index and metadata in-place — JSON round-trips lose them
            existing.topo_index = s.topo_index
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata or {})
    return registered


# ---------------------------------------------------------------------------
# Build all eight synthons
# ---------------------------------------------------------------------------

def _build_all() -> List[Synthon]:
    return [
        _photon(),
        _proton(),
        _electron(),
        _spin_singlet(),
        _qubit_logical(),
        _kitaev_chain_majorana(),
        _fqh_moore_read(),
        _topological_insulator_bi2se3(),
    ]


# ===========================================================================
# TIER 1 — QUANTUM PARTICLES
# ===========================================================================

def _photon() -> Synthon:
    """
    Photon — massless boson, quantum of the electromagnetic field.

    Primitive justifications:
      D = D_∞ (TEMPORAL): photon propagates along the temporal axis of the light
          cone; emission/absorption is a temporal event sequence.
      T = T_⋈ (CYCLIC_BOWTIE): dual circular polarization modes are self-
          complementary — each polarization completes the other. Bowtie topology
          captures the helicity ± degeneracy.
      R = R_⊃ (NON_COVALENT): field–matter coupling (QED vertex); reversible —
          photon can be re-emitted (Rabi oscillations).
      P = P_±^sym (SELF_COMPLEMENTARY_SYM): charge-neutral; ± helicity are
          symmetric under time-reversal. Not a D-A pair.
      F = F_ℏ (HIGH): quantum field with definite frequency — no thermalisation,
          single photon is in a pure Fock state.
      K = K_fast (FAST): propagates at c; no kinetic barrier for absorption.
      G = G_ℵ (GLOBAL): entangled photon pairs exhibit non-local correlations
          across macroscopic distances (Bell tests).
      Γ = SELECTIVE_AND (QUANTUM tier): resonant absorption requires a specific
          frequency match (selective) AND a transition dipole (AND logic).
      Φ = Φ_sub: single photon is below the G–D criticality locus.
      Ω = TRIVIAL: free-space photon has no topological protection.
          (Photonic topological insulators would be a separate synthon.)
    """
    return Synthon(
        name="photon",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.QUANTUM_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry=None,
        topo_index=TopoIndex.TRIVIAL,
        description=(
            "Massless spin-1 boson; quantum of the electromagnetic field. "
            "Carries energy E=hν, momentum p=ℏk, and helicity ±1. "
            "Key quantum resource: entangled photon pairs violate Bell inequalities. "
            "Identified gap: no T_braid needed (photons are bosons; no anyonic statistics). "
            "F_ℏ reflects Fock-state purity, not thermal mixing. "
            "D_∞ reflects the light-cone propagation structure."
        ),
    )


def _proton() -> Synthon:
    """
    Proton — spin-½ baryon, fundamental charge carrier in acid-base chemistry.

    Primitive justifications:
      D = D_∧ (MOLECULAR): point-like nuclear particle; proton transfer operates
          at the molecular scale.
      T = T_■ (HUB_NODE): proton can bridge multiple bases simultaneously in
          Grotthuss relay chains (one proton, multiple acceptor hops).
      R = R_† (DYNAMIC_CATALYTIC): proton transfer is dynamically catalytic —
          the proton moves from acid to base and the event can be reversed (pKa
          dependent). Not a permanent bond.
      P = P_+ (ACCEPTOR): positive charge; electrophilic in all acid-base
          reactions. The proton is always the acceptor of electron density.
      F = F_ℏ (HIGH): quantum tunnelling dominates at low temperatures (KIE
          experiments confirm proton tunnelling); definite charge state.
      K = K_fast (FAST): proton transfer is near-diffusion-limited in water
          (kH⁺ ~ 10¹¹ M⁻¹s⁻¹). Grotthuss mechanism is essentially barrierless.
      G = G_ℵ (GLOBAL): entangled proton states observed in neutron scattering
          experiments on ice; non-local in principle.
      Γ = SPECIFIC_AND: one highly specific protonation site at a time.
      Φ = Φ_sub.
      Ω = TRIVIAL: bare proton, no topological structure.
    """
    return Synthon(
        name="proton",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.HUB_NODE,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        topo_index=TopoIndex.TRIVIAL,
        description=(
            "Bare proton (H⁺); fundamental charge carrier in acid-base chemistry. "
            "Mass ~1.67×10⁻²⁷ kg; charge +e. Quantum tunnelling observed in enzyme "
            "catalysis (large primary KIE). Grotthuss chain mechanism makes "
            "long-range proton transfer near-barrierless in protic media."
        ),
    )


def _electron() -> Synthon:
    """
    Electron — spin-½ lepton, fundamental charge carrier in electronics/chemistry.

    Primitive justifications:
      D = D_∧ (MOLECULAR): point-like (r_e < 10⁻²² m per experiment).
      T = T_■ (HUB_NODE): electron can occupy multiple bonding orbitals
          simultaneously (resonance, aromaticity). Hub topology captures
          multi-centre bonding.
      R = R_sub (COVALENT): electron sharing forms σ/π bonds — the canonical
          covalent recognition mode.
      P = P_− (DONOR): negative charge; nucleophile. The electron is the
          electron donor in all Lewis acid-base interactions.
      F = F_ℏ (HIGH): definite charge and spin state (pure quantum state in
          isolation). No thermal mixing of charge eigenstates.
      K = K_fast (FAST): electron transfer at picosecond timescales (Marcus
          theory); Franck-Condon principle.
      G = G_ℵ (GLOBAL): Bell-pair electrons are non-locally correlated (CHSH).
      Γ = SPECIFIC_AND: one target orbital per bonding event.
      Φ = Φ_sub.
      Ω = TRIVIAL: free electron; topological character emerges from band
          structure of hosting material (separate synthon).
    """
    return Synthon(
        name="electron",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.HUB_NODE,
        recognition_mode=RecognitionMode.COVALENT,
        polarity=Polarity.DONOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        topo_index=TopoIndex.TRIVIAL,
        description=(
            "Bare electron; fundamental charge carrier. Mass 9.11×10⁻³¹ kg; "
            "charge −e; spin-½. Marcus-theory electron transfer governs redox "
            "chemistry. Bell-pair entanglement (Aspect 1982). Topological "
            "character (e.g. Dirac surface states) belongs to the material "
            "band-structure, not the bare particle."
        ),
    )


def _spin_singlet() -> Synthon:
    """
    Spin singlet — maximally entangled two-spin Bell state |Ψ⁻⟩ = (|↑↓⟩−|↓↑⟩)/√2.

    FACTOR 8 TRIGGER: G_ℵ + F_ℏ + K_trap + ¬D_∞
      → universality class: quantum criticality (TFI/heavy-fermion)
      → falsifiable prediction: χ(T→0) ~ T^{-γ} with γ > 1

    Primitive justifications:
      D = D_∧ (MOLECULAR): localized two-spin system (e.g., a singlet pair in a
          molecule or a two-qubit Bell pair).
      T = T_⋈ (CYCLIC_BOWTIE): the |↑↓⟩−|↓↑⟩ structure is self-complementary —
          flipping both spins restores the singlet. Bowtie captures the mutual
          completion of the two spin components.
      R = R_⊃ (NON_COVALENT): exchange coupling J is a non-bonded interaction
          (Heisenberg Hamiltonian, not a covalent bond).
      P = P_±^ψ (SELF_COMPLEMENTARY_PSEUDO): geometrically symmetric (looks
          like ±) but electronically asymmetric due to quantum correlations —
          distinguishes singlet from triplet.
      F = F_ℏ (HIGH): pure Bell state; maximal entanglement means F = 1 in
          isolation. The singlet is the most faithful two-spin state.
      K = K_trap (TRAP): kinetically trapped — requires active decoherence or
          perturbation to escape the singlet manifold. The singlet is a local
          free-energy minimum with a barrier to the triplet sector.
      G = G_ℵ (GLOBAL): non-local correlations; spins can be separated
          arbitrarily (EPR-type) while maintaining the singlet structure.
      Γ = QUANTUM_AND: the singlet requires BOTH spins simultaneously — it is
          a joint property of the two-particle system (Toffoli semantics).
      Φ = Φ_sub: Factor 8 fires (G_ℵ + F_ℏ + K_trap + ¬D_∞) but the single
          isolated singlet is not yet at the criticality locus; Factor 8
          scores the criticality candidacy probe, not Φ.
      Ω = TRIVIAL: the singlet is not a topologically protected state per se.
          (A spin singlet in a topological magnet would inherit the material Ω.)
    """
    return Synthon(
        name="spin_singlet",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.QUANTUM_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        topo_index=TopoIndex.TRIVIAL,
        description=(
            "Maximally entangled two-spin Bell state |Ψ⁻⟩ = (|↑↓⟩−|↓↑⟩)/√2. "
            "FACTOR 8 TRIGGER: G_ℵ + F_ℏ + K_trap + ¬D_∞ → quantum criticality "
            "(TFI/heavy-fermion class). Falsifiable: χ(T→0) ~ T^{-γ}. "
            "K_trap: perturbation sweep shows K_trap→K_MBL costs Δξ +2.30 nats "
            "(HIGH sensitivity) — highest single-primitive cost in quantum series. "
            "Contrast with qubit_logical (F_ell) — the singlet is the idealised "
            "entangled pair, the qubit is the practical computational unit."
        ),
    )


def _qubit_logical() -> Synthon:
    """
    Qubit (logical, unprotected) — idealized two-level quantum system for computation.

    Primitive justifications:
      D = D_∧ (MOLECULAR): localized in physical hardware (superconducting island,
          ion trap, quantum dot, etc.).
      T = T_| (LINEAR): computational basis {|0⟩, |1⟩} spans a line in Hilbert
          space; the Bloch sphere is S² but the tensor-product structure of a
          register is T_|^⊗n (chain of qubits).
      R = R_⊃ (NON_COVALENT): controlled via external fields (microwave, laser,
          RF pulses); not a covalent bonding event.
      P = P_±^ψ (SELF_COMPLEMENTARY_PSEUDO): |0⟩ and |1⟩ are pseudosymmetric
          (they look like ± but quantum interference breaks the symmetry).
      F = F_ℓ (LOW): coherence times T₁, T₂ are finite; gate error rates
          10⁻² to 10⁻³ in current hardware — well below F_ℏ threshold.
          This is the critical gap between this synthon and spin_singlet.
      K = K_slow (SLOW): gate operation speeds (ns–μs) are slow relative to
          environmental decoherence; threshold error correction overhead is large.
      G = G_ℵ (GLOBAL): entanglement non-local across entire quantum register.
      Γ = QUANTUM_AND: CNOT / Toffoli gates require joint operation on two qubits.
      Φ = Φ_sub: sub-threshold fidelity prevents criticality lift (Axiom 5).
      Ω = TRIVIAL: unprotected qubit. Topological qubit (Ω_NA) is a separate
          synthon — it would have F_ℏ and K_trap instead.
    """
    return Synthon(
        name="qubit_logical",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.LOW,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.QUANTUM_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry=None,
        topo_index=TopoIndex.TRIVIAL,
        description=(
            "Idealized logical qubit — two-level quantum system for gate-based "
            "quantum computation. F_ell reflects current hardware reality "
            "(decoherence limits T₂ to μs–ms range). K_slow captures that gate "
            "operations are slow relative to decoherence. Compare: spin_singlet "
            "(F_ℏ, K_trap) is the idealised entangled state; qubit_logical "
            "(F_ell, K_slow) is the practical computational unit. "
            "Topological qubit (Ω_NA) would flip both: F_ℏ, K_trap, Ω_NA."
        ),
    )


# ===========================================================================
# TIER 2 — TOPOLOGICAL MATTER
# ===========================================================================

def _kitaev_chain_majorana() -> Synthon:
    """
    Kitaev chain (1D p-wave superconductor) — topological phase with Majorana zero modes.

    Model: H = -μ Σ c†c - t Σ(c†c + h.c.) + Δ Σ(c†c† + h.c.)
    Topological phase: |μ| < 2t. Hosts two Majorana zero modes γ_L, γ_R at chain ends.
    AZ class: D (no time-reversal, no spin rotation). Topological invariant: ℤ.

    Primitive justifications:
      D = D_∧ (MOLECULAR): the *recognition event* is the non-local Majorana qubit —
          it is defined by the pair of end modes, which are spatially localized.
          The chain length is irrelevant to the recognition motif.
      T = T_| (LINEAR): 1D quantum wire — the chain topology is the defining
          geometric constraint. T_braid reserved for 2D systems where actual
          braiding can occur.
      R = R_⊃ (NON_COVALENT): Cooper-pair tunnelling via proximity effect (not a
          covalent chemical bond; the superconducting pairing is a non-bonded
          coherent channel).
      P = P_±^sym (SELF_COMPLEMENTARY_SYM): particle-hole symmetry (PHS) is the
          defining symmetry of class D — the Nambu space relates ψ and ψ†
          symmetrically (true symmetry, not pseudosymmetric).
      F = F_ℏ (HIGH): topological gap Δ_topo protects the Majorana modes from
          local perturbations — the highest available fidelity tier.
      K = K_trap (TRAP): the topological gap acts as a kinetic barrier; thermal
          excitations above the gap are exponentially suppressed. The Majorana
          modes are gap-protected (contrast K_MBL which requires disorder).
      G = G_ℵ (GLOBAL): the logical qubit is non-locally encoded — γ_L and γ_R
          are at opposite ends of the chain; no local operator can distinguish
          |0_L⟩ from |1_L⟩.
      Γ = QUANTUM_AND: the non-local qubit requires both end modes simultaneously;
          a single Majorana is not a qubit.
      Φ = Φ_sub: stable topological phase (not at the phase transition).
      Ω = Z_CLASS (Ω_Z): ℤ topological invariant, AZ class D, 1D.
          The winding number W ∈ ℤ; topological phase has W = 1.
      S = "1:1": one Majorana zero mode per end (γ_L : γ_R = 1:1).
    """
    return Synthon(
        name="kitaev_chain_majorana",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.QUANTUM_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        topo_index=TopoIndex.Z_CLASS,
        description=(
            "Kitaev chain: 1D spinless p-wave superconductor in its topological phase "
            "(|μ| < 2t). Majorana zero modes γ_L, γ_R at chain ends encode a "
            "single non-local logical qubit. AZ class D, ℤ invariant (W=1). "
            "Gap-protected (K_trap); no disorder required (contrast K_MBL). "
            "Ω_Z: first topological synthon in the quantum catalog. "
            "Prediction: tensor(kitaev_chain, qubit_logical) → Ω_Z (dominant "
            "protection propagates); meet(kitaev_chain, spin_singlet) → Ω_0 "
            "(conservative guarantee)."
        ),
    )


def _fqh_moore_read() -> Synthon:
    """
    FQH ν=5/2 Moore-Read state — non-Abelian fractional quantum Hall state.

    The Moore-Read (Pfaffian) state at Landau level filling ν=5/2 in GaAs
    is the paradigmatic experimental non-Abelian topological phase.
    Quasiparticles are Ising anyons: fusion rule σ × σ = 1 + ψ (quantum
    dimension √2). Groundstate degeneracy 3 on torus.

    Primitive justifications:
      D = D_△ (SUPRAMOLECULAR): 2D electron gas in GaAs/AlGaAs heterojunction;
          the recognition motif spans the sample scale.
      T = T_braid (BRAID): anyonic braiding statistics — the first use of T_braid
          in a catalog entry. The world-lines of Ising anyons literally form braids
          in 2+1 dimensions, implementing non-Abelian unitary gates.
      R = R_⊃ (NON_COVALENT): Coulomb electron-electron interactions (non-bonded).
          The pairing is not covalent; it is a collective quantum condensate.
      P = P_±^ψ (SELF_COMPLEMENTARY_PSEUDO): particle-hole pseudosymmetry at
          ν=5/2 — the Moore-Read state and its conjugate at ν=7/2 are related
          by PHS but differ in microscopic details (anti-Pfaffian debate).
      F = F_ℏ (HIGH): topological gap Δ_5/2 ≈ 0.5 K protects the state.
          Fragile in practice but protected in principle (high F tier).
      K = K_trap (TRAP): topological gap prevents thermal escape; the system is
          pinned in the ν=5/2 plateau.
      G = G_ℵ (GLOBAL): non-local topological order — groundstate degeneracy
          (GSD = 3 on torus) is a global property inaccessible to local probes.
      Γ = QUANTUM_AND: non-Abelian fusion requires simultaneous manipulation of
          two or more anyons — inherently a multi-particle (QUANTUM AND) operation.
      Φ = Φ_sub: stable FQH plateau (the phase transition to ν=2 or ν=3 is a
          separate synthon).
      Ω = NON_ABELIAN (Ω_NA): non-Abelian Ising anyons. First Ω_NA entry in the
          catalog. Protection_strength = 4 (maximum).
      S = None: filling fraction ν=5/2 is a material property, not a pairwise
          stoichiometric ratio.
    """
    return Synthon(
        name="fqh_moore_read",
        dimensionality=Dimensionality.SUPRAMOLECULAR,
        topology=Topology.BRAID,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.QUANTUM_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry=None,
        topo_index=TopoIndex.NON_ABELIAN,
        description=(
            "FQH ν=5/2 Moore-Read (Pfaffian) state. Non-Abelian Ising anyons: "
            "σ × σ = 1 + ψ, quantum dimension d_σ = √2. GSD = 3 on torus. "
            "First T_braid entry in the quantum catalog. Ω_NA (protection_strength=4). "
            "Experimental platform: GaAs/AlGaAs at T ~ 10 mK, B ~ 5 T. "
            "Tension: anti-Pfaffian debate unresolved (PH-symmetric partner). "
            "Prediction: tensor(fqh_moore_read, kitaev_chain) → Ω_NA (dominates). "
            "Prediction: meet(fqh_moore_read, topological_insulator_bi2se3) → Ω_Z₂ "
            "(conservative guarantee falls to weaker protection)."
        ),
    )


def _topological_insulator_bi2se3() -> Synthon:
    """
    3D Strong Topological Insulator (Bi₂Se₃ archetype) — ℤ₂ protected surface states.

    Bi₂Se₃ is the archetypal strong 3D TI (Kane-Mele-Fu model). Has ℤ₂ topological
    invariant ν₀ = 1 (class AII — time-reversal symmetric, spin-orbit coupled).
    Hosts a single Dirac cone on each surface protected by Kramers' theorem.

    Primitive justifications:
      D = D_△ (SUPRAMOLECULAR): 3D van-der-Waals layered crystal; the recognition
          motif (surface Dirac cone) spans the bulk-boundary interface at the
          supramolecular scale.
      T = T_∈ (NETWORK): the Dirac surface states form a multiply-connected 2D
          network on the 3D surface — an open network topology, not a cage or chain.
      R = R_⊃ (NON_COVALENT): spin-orbit coupling is an effective non-bonded
          interaction; the surface state transport is non-covalent.
      P = P_±^sym (SELF_COMPLEMENTARY_SYM): time-reversal symmetry (TRS) is the
          key protecting symmetry — T² = -1 for fermions ensures Kramers degeneracy.
          The system is symmetric under TRS (true symmetry, not pseudo).
      F = F_ℏ (HIGH): TRS + Kramers' theorem makes the surface states topologically
          protected — a single magnetic impurity at the Dirac point would gap the
          surface state, but that requires explicitly breaking TRS.
      K = K_slow (SLOW): surface state mobility is lower than bulk carrier mobility
          in typical Bi₂Se₃ (bulk conduction still dominant below ~100 K);
          the surface states are slow compared to bulk.
      G = G_ℵ (GLOBAL): bulk-boundary correspondence is a non-local relationship —
          the number of surface Dirac cones is determined by the bulk ℤ₂ invariant.
      Γ = SELECTIVE_AND: the surface states selectively couple to magnetic
          perturbations (gap-opening) vs. non-magnetic (no gap); selective.
      Φ = Φ_sub: stable topological insulating phase.
      Ω = Z2_CLASS (Ω_Z₂): strong ℤ₂ TI, class AII (ν₀ = 1).
      S = None: bulk material, not a pairwise recognition event.
    """
    return Synthon(
        name="topological_insulator_bi2se3",
        dimensionality=Dimensionality.SUPRAMOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry=None,
        topo_index=TopoIndex.Z2_CLASS,
        description=(
            "Bi₂Se₃-type 3D strong topological insulator. ℤ₂ invariant ν₀=1, "
            "AZ class AII (time-reversal symmetric). Single Dirac cone per surface, "
            "Kramers-protected. Bulk gap ~0.35 eV; surface state velocity "
            "v_F ~ 5×10⁵ m/s. K_slow: surface carrier mobility < bulk. "
            "Ω_Z₂ (protection_strength=1). "
            "Prediction: tensor(topological_insulator, spin_singlet) → Ω_Z₂ "
            "(dominates TRIVIAL). "
            "meet(topological_insulator, fqh_moore_read) → Ω_Z₂ "
            "(conservative: Z₂ < non-Abelian)."
        ),
    )
