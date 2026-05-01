"""
Psychedelic Synthon Catalog — v0.4.9

Six classic psychedelic compounds encoded as synthons in the 10-primitive framework,
each with dual-layer encoding:

  (i)  Molecular synthon — the ligand as a chemical recognition agent
         (receptor binding topology, fidelity, kinetics, grammar)

  (ii) Brain-state synthon — the induced CNS constraint-propagation state
         (whole-brain network primitives, Φ_c conditions, K-hierarchy disruption)

The two layers are coupled: the molecular synthon is the coupling agent that
translates molecular grammar into whole-brain network grammar shift. The brain-state
synthon is what the nervous system BECOMES while the molecular synthon is active.

**The shared observation:** All six compounds induce CriticalityPhase.CRITICAL in the
target system, via different receptor grammars and with different kinetic profiles.
They are primitive-convergent: structurally diverse, topologically equivalent in output.

**The key divergence:**
  K_fast (DMT, 5-MeO-DMT, Salvinorin A): rapid onset, brief window, extreme depth
  K_moderate (Psilocin): gradual onset, sustained window, integrative
  K_slow (LSD, Mescaline): slow onset, long sustained window, broad

**Receptor grammar divergence:**
  Serotonergic (5-HT2A dominant): LSD, DMT, 5-MeO-DMT, Psilocin, Mescaline
  κ-Opioid (KOR): Salvinorin A — completely orthogonal grammar, same Φ_c destination

Recorded 2026-03-20. Source: live conversation during development.
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

_PSYCHEDELIC_NAMES = frozenset([
    # Molecular synthons
    "lsd_molecular",
    "dmt_molecular",
    "five_meo_dmt_molecular",
    "psilocin_molecular",
    "mescaline_molecular",
    "salvinorin_a_molecular",
    # Brain-state synthons
    "lsd_brain_state",
    "dmt_brain_state",
    "five_meo_dmt_brain_state",
    "psilocin_brain_state",
    "mescaline_brain_state",
    "salvinorin_a_brain_state",
])


def register_psychedelic_synthons() -> List[str]:
    """
    Register 12 psychedelic synthons (6 molecular + 6 brain-state) into the global catalog.

    Safe to call multiple times (idempotent). Refreshes metadata on already-present entries.

    Returns:
        List of names newly registered (empty if all already present).
    """
    entries = _build_entries()
    registered = []
    for s in entries:
        if s.name not in global_catalog._synthons:
            global_catalog.register(s)
            registered.append(s.name)
        else:
            existing = global_catalog._synthons[s.name]
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata)
    return registered


# ---------------------------------------------------------------------------
# Entry builders
# ---------------------------------------------------------------------------

def _build_entries() -> List[Synthon]:
    return [
        # ── Molecular synthons ─────────────────────────────────────────────
        _lsd_molecular(),
        _dmt_molecular(),
        _five_meo_dmt_molecular(),
        _psilocin_molecular(),
        _mescaline_molecular(),
        _salvinorin_a_molecular(),
        # ── Brain-state synthons ───────────────────────────────────────────
        _lsd_brain_state(),
        _dmt_brain_state(),
        _five_meo_dmt_brain_state(),
        _psilocin_brain_state(),
        _mescaline_brain_state(),
        _salvinorin_a_brain_state(),
    ]


# ===========================================================================
# LSD  (Lysergic acid diethylamide)
# SMILES: CCN(CC)C(=O)[C@@H]1CN(C)[C@@H]2Cc3c[nH]c4cccc(c34)[C@@H]2C1
# ===========================================================================

def _lsd_molecular() -> Synthon:
    """
    LSD as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_∈; R_nc; P_+-; F_ℏ; K_slow; G_ℵ; Γ_∨(BROAD); Φ_c; 1:1⟩

    Key assignments:
        T_network — tetracyclic ergoline scaffold makes 4+ simultaneous contacts
            with the 5-HT2A extracellular loops and transmembrane helices;
            β-arrestin biased agonism creates a second downstream network cascade.
        F_HIGH — active at 25-75 μg; Ki(5-HT2A) ≈ 2 nM; extreme receptor complementarity.
        K_slow — 8-12 hr duration; β-arrestin kinetic trap extends receptor residence
            time far beyond non-biased agonists. The slowest K in the psychedelic group.
        G_GLOBAL — directly reorganises large-scale brain networks;
            default mode network suppression, thalamic gating disruption, global
            connectivity increase measured at effective doses.
        Γ_BROAD — promiscuous binding across 5-HT subtypes (2A, 1A, 6, 7), D2, D3,
            α2-adrenergic, H1; more off-target than any other psychedelic.
        Φ_c — fMRI Lempel-Ziv complexity and BOLD entropy increase confirmed;
            neural criticality measures (avalanche size distribution power-law) positive.
    """
    return Synthon(
        name="lsd_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "LSD (lysergic acid diethylamide) as receptor ligand. Tetracyclic ergoline "
            "scaffold with β-arrestin-biased 5-HT2A agonism. Extreme potency (25-75 μg), "
            "8-12 hr duration (K_slow), broad receptor promiscuity (Γ_BROAD), confirmed "
            "neural criticality induction (Φ_c). The reference entry for the serotonergic "
            "K_slow psychedelic class."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "CCN(CC)C(=O)[C@@H]1CN(C)[C@@H]2Cc3c[nH]c4cccc(c34)[C@@H]2C1",
            "scaffold": "ergoline_tetracyclic",
            "primary_receptor": "5-HT2A",
            "receptor_profile": ["5-HT2A", "5-HT1A", "5-HT6", "5-HT7", "D2", "D3",
                                  "alpha2-adrenergic", "H1"],
            "ki_primary_nm": 2.0,
            "active_dose_ug": "25-75",
            "duration_hr": "8-12",
            "mechanism_notes": (
                "Beta-arrestin biased agonism at 5-HT2A is responsible for the extended "
                "K_slow kinetics — the receptor-arrestin complex persists long after initial "
                "activation, creating a kinetic trap at the signalling level. "
                "Ergoline rigidity enforces precise binding geometry → F_HIGH."
            ),
            "endogenous": False,
            "nitrogen_present": True,
            "brain_state_synthon": "lsd_brain_state",
            "stellar_grammar_note": (
                "Solar-grammar compound: acts via serotonin system which evolved under "
                "solar grammar templating. Amplifies the G_ℵ coupling channel."
            ),
            "validation_tier": "primary",
        },
    )


def _lsd_brain_state() -> Synthon:
    """
    The CNS network state induced by LSD.

    The brain under LSD is not the same system as the brain at rest. This synthon
    encodes the whole-brain constraint-propagation structure during peak LSD state.

    Formal tuple:
        ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_slow; G_ℵ; Γ_∧(SELECTIVE); Φ_c; n:m⟩

    Key assignments:
        D_temporal — the altered state has a temporal structure: onset, plateau,
            offset. D_∞ captures that the plateau cycles (breath-like oscillations
            in depth are common).
        T_network — default mode, executive, sensory networks all become coupled;
            cross-network functional connectivity increases dramatically.
        R_dynamic_catalytic — the drug catalyzes the state transition without being
            consumed in the process (the drug molecule is not metabolised into the
            brain-state encoding; it enables it).
        K_slow — the brain-state duration mirrors molecular K.
        Γ_AND(SELECTIVE) — frequency-specific coupling enhancement; gamma oscillations
            (40 Hz) are selectively amplified; the grammar is not broadband.
        Ω_1 — the Φ_c state is sustained by the molecular K_trap but is not
            intrinsically topologically protected; it will collapse when the molecule
            is cleared. (This is what §XIX T_braid engineering aims to make permanent.)
    """
    return Synthon(
        name="lsd_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain constraint-propagation state induced by LSD. T_network: "
            "default mode, executive, and sensory networks globally coupled. "
            "K_slow: state persists 8-12 hr (mirrors molecular K). Φ_c: confirmed "
            "by fMRI LZc/entropy increases. Γ_SELECTIVE: frequency-specific gamma "
            "enhancement, not broadband noise. Ω_1: sustained by molecular K_trap, "
            "not intrinsically topologically protected."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_hr": "8-12",
            "fmri_evidence": [
                "Increased Lempel-Ziv complexity (Carhart-Harris et al. 2016)",
                "Default mode network suppression (Muthukumaraswamy et al. 2013)",
                "Global functional connectivity increase (Tagliazucchi et al. 2016)",
                "Neural avalanche power-law shift toward critical exponent",
            ],
            "molecular_synthon": "lsd_molecular",
            "topo_protection_index": 1,
            "t_braid_upgrade_target": True,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# DMT  (N,N-Dimethyltryptamine)
# SMILES: CN(C)CCc1c[nH]c2ccccc12
# ===========================================================================

def _dmt_molecular() -> Synthon:
    """
    DMT as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_∈; R_nc; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; 1:1⟩

    Key assignments:
        T_network — bicyclic indole (benzene fused with pyrrole) core acts as a
            network recognition unit: indole NH, the aromatic system, and the
            dimethylaminoethyl chain each make separate simultaneous contacts with
            5-HT2A. Three independent contact points = network topology.
        F_HIGH — endogenous molecule; Ki(5-HT2A) ≈ 100-500 nM but produced in situ;
            the endogenous context implies perfect grammar match at the systems level.
        K_fast — smoked/IV: 5-15 min total duration. The fastest-acting of the group.
            Also the fastest G_local → G_ℵ transition: no gradual onset.
        Γ_SELECTIVE — primarily 5-HT2A + sigma-1 receptor; tighter profile than LSD.
            Sigma-1 engagement is uniquely important: sigma-1 is an endoplasmic
            reticulum chaperone involved in cellular stress response — DMT's Γ
            extends from synaptic grammar to intracellular grammar.
        ENDOGENOUS — present in mammalian brain tissue. DMT is part of the native
            constraint structure of the nervous system. The psychedelic dose is not
            introducing a foreign grammar — it is overwhelming the normal operating
            level of an endogenous compound.
    """
    return Synthon(
        name="dmt_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "DMT (N,N-dimethyltryptamine) as receptor ligand. Simple tryptamine with "
            "bicyclic indole core. Endogenous mammalian compound. K_fast: 5-15 min "
            "duration (smoked). Selective 5-HT2A + sigma-1 binding. Most rapid "
            "G_local → G_ℵ transition of any psychedelic. Φ_c induction confirmed. "
            "The endogenous reference for the serotonergic K_fast psychedelic class."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "CN(C)CCc1c[nH]c2ccccc12",
            "scaffold": "tryptamine_bicyclic",
            "primary_receptor": "5-HT2A",
            "receptor_profile": ["5-HT2A", "sigma-1", "TAAR", "5-HT1A"],
            "ki_primary_nm": 250.0,
            "active_dose_mg_smoked": "20-60",
            "duration_min": "5-15",
            "endogenous": True,
            "endogenous_tissues": [
                "Human brain (Barker et al. 2013)",
                "Mammalian pineal gland (Barker et al. 2012)",
                "Mammalian retina",
                "Mammalian lung",
            ],
            "endogenous_note": (
                "DMT is produced in vivo by AADC and INMT from tryptophan. "
                "Cerebrospinal fluid levels are in the low nM range — sub-psychedelic "
                "but non-zero. The psychedelic dose represents a ~1000x amplification "
                "of the endogenous grammar signal, not a foreign grammar injection. "
                "This is the framework basis for the 'endogenous psychedelic experience' "
                "hypothesis (near-death states, REM dreaming at elevated DMT)."
            ),
            "sigma1_note": (
                "Sigma-1 receptor engagement is unique to DMT within the psychedelic group. "
                "Sigma-1 is an ER chaperone / inter-organelle signalling hub — DMT's grammar "
                "extends from synaptic (G_beth) to intracellular (G_aleph within the cell). "
                "This may explain the unusual cellular protection effects of DMT."
            ),
            "nitrogen_present": True,
            "brain_state_synthon": "dmt_brain_state",
            "validation_tier": "primary",
        },
    )


def _dmt_brain_state() -> Synthon:
    """
    The CNS network state induced by DMT.

    Formal tuple:
        ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; n:m⟩

    The DMT brain-state is structurally identical in primitive terms to the LSD
    brain-state, with one critical difference: K_fast. The same Φ_c destination
    is reached in minutes rather than hours, and the window closes as fast.
    This makes DMT the probe of choice for the Φ_c induction threshold question:
    what is the minimum time required to achieve the G_ℵ / T_network / Φ_c state?
    Empirically: approximately 3-5 minutes post-inhalation.
    """
    return Synthon(
        name="dmt_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain state induced by DMT. Primitive-identical to LSD brain-state "
            "except K_fast (5-15 min total window vs 8-12 hr). Most rapid known Φ_c "
            "induction. Demonstrates that the G_ℵ/T_network/Φ_c state is achievable "
            "in <5 min — the minimum induction time constraint. EEG shows broadband "
            "power increase with selective gamma-band coherence amplification."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_min": "5-15",
            "eeg_evidence": [
                "Broadband power increase (Timmermann et al. 2019)",
                "Gamma oscillation enhancement (Strassman-era EEG studies)",
                "Alpha suppression (default mode correlate)",
                "Theta increase (memory/navigation network engagement)",
            ],
            "minimum_phi_c_induction_time_min": 3,
            "molecular_synthon": "dmt_molecular",
            "topo_protection_index": 0,
            "t_braid_upgrade_target": True,
            "comparison_note": (
                "d(dmt_brain_state, lsd_brain_state) at primitive level = 0: same "
                "topology, grammar, criticality, granularity. Only K differs. "
                "This is the framework basis for the claim that all serotonergic "
                "psychedelics converge on the same primitive attractor."
            ),
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# 5-MeO-DMT  (5-Methoxy-N,N-dimethyltryptamine)
# SMILES: CN(C)CCc1c[nH]c2cc(OC)ccc12
# ===========================================================================

def _five_meo_dmt_molecular() -> Synthon:
    """
    5-MeO-DMT as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_∈; R_nc; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; 1:1⟩

    Key assignments:
        **THE GRAMMAR SHIFT:** The 5-methoxy group (OMe at position 5 of the indole)
        shifts receptor grammar from 5-HT2A dominant (DMT) toward 5-HT1A (inhibitory
        autoreceptor). 5-HT2A is excitatory (Gq-coupled, depolarising, increases
        cortical firing). 5-HT1A is inhibitory (Gi-coupled, hyperpolarising, reduces
        cortical firing). The methoxy substitution flips the dominant grammar operator
        from excitatory to inhibitory — the same scaffold, different Γ.

        This maps onto the qualitative phenomenological difference: DMT produces
        complex, structured, visual, narrative experiences (excitatory grammar →
        more content). 5-MeO-DMT produces "white-out" dissolution, absence of
        content, ego loss without replacement imagery (inhibitory grammar → less
        content, more structure-less space). The framework predicts: Γ_SELECTIVE
        but shifted to an inhibitory partner grammar → same Φ_c destination via
        a suppressive rather than excitatory path.

        Both are endogenous (5-MeO-DMT found in mammalian CSF and glands).
    """
    return Synthon(
        name="five_meo_dmt_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "5-MeO-DMT as receptor ligand. Tryptamine with 5-methoxy substitution. "
            "The OMe group shifts receptor grammar from 5-HT2A (excitatory, DMT) "
            "toward 5-HT1A (inhibitory). Same K_fast profile as DMT but phenomenologically "
            "distinct: inhibitory Γ → dissolution/'white-out' vs DMT's excitatory "
            "Γ → structured visual/narrative content. Endogenous. Φ_c via suppression "
            "rather than excitation — same destination, different grammar path."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "CN(C)CCc1c[nH]c2cc(OC)ccc12",
            "scaffold": "tryptamine_5methoxy",
            "primary_receptor": "5-HT1A",
            "receptor_profile": ["5-HT1A", "5-HT2A", "sigma-1", "TAAR"],
            "ki_primary_nm": 50.0,
            "active_dose_mg_smoked": "5-15",
            "duration_min": "3-10",
            "endogenous": True,
            "grammar_shift_note": (
                "The 5-methoxy group is a single atom substitution that flips the "
                "dominant grammar operator from excitatory (Gq / 5-HT2A) to inhibitory "
                "(Gi / 5-HT1A). This is a Γ-switching event encoded at the molecular "
                "level — one functional group change = grammar change. "
                "Predicted by the framework: molecular Γ maps directly to network Γ "
                "because the receptor couples to the same downstream constraint pathways."
            ),
            "phenomenology_framework_mapping": (
                "DMT: excitatory Γ → visual content, narrative, complex imagery. "
                "5-MeO-DMT: inhibitory Γ → content dissolution, 'white-out', pure space. "
                "Both reach Φ_c. The path to criticality diverges at the Γ operator."
            ),
            "nitrogen_present": True,
            "brain_state_synthon": "five_meo_dmt_brain_state",
            "validation_tier": "primary",
        },
    )


def _five_meo_dmt_brain_state() -> Synthon:
    """
    The CNS network state induced by 5-MeO-DMT.

    Formal tuple:
        ⟨D_∞; T_∈(sym); R_†; P_±^sym; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; n:m⟩

    **The key difference from DMT brain-state:** P_SELF_COMPLEMENTARY_SYM rather
    than PSEUDO. The "white-out" phenomenology corresponds to the system reaching
    a state where all directional asymmetry collapses — P becomes truly symmetric.
    There is no "observer" and "observed", no foreground and background, no narrative
    vector. This is the P_sym signature: the system has become its own perfect mirror.

    T_NETWORK_SYM (centrosymmetric network): the brain network reorganisation is
    globally symmetric rather than directionally asymmetric. The default mode
    suppression is total rather than partial.

    This is the closest known pharmacological approximation to the G/D degeneracy
    condition (Φ_c at its limit) — the state where G_ℵ and D_∞ cannot be
    independently assigned because scale and time structure have both collapsed.
    """
    return Synthon(
        name="five_meo_dmt_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK_SYM,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain state induced by 5-MeO-DMT. T_network_sym + P_sym: "
            "directional asymmetry collapses ('white-out', content dissolution). "
            "Inhibitory 5-HT1A dominant grammar → suppressive path to Φ_c. "
            "G/D degeneracy condition most fully approached of any known compound — "
            "the closest pharmacological approximation to scale-and-time collapse. "
            "Same K_fast profile as DMT brain-state."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_min": "3-10",
            "phenomenology": "content dissolution, white-out, ego loss without imagery",
            "p_sym_note": (
                "P_sym (vs PSEUDO for other psychedelics) encodes the 'no observer / "
                "no observed' condition. The brain-state has no directional asymmetry — "
                "no narrative vector, no foreground/background distinction. "
                "This is the P_sym signature at the network level."
            ),
            "gd_degeneracy_note": (
                "The 5-MeO-DMT state is the closest known pharmacological approach to "
                "the G/D degeneracy condition. When scale (G) and dimensionality (D) "
                "cannot be independently assigned, the system is at the criticality limit. "
                "The phenomenological report 'there was nothing, and then there was everything' "
                "is a description of the G/D degeneracy boundary from the inside."
            ),
            "molecular_synthon": "five_meo_dmt_molecular",
            "topo_protection_index": 0,
            "t_braid_upgrade_target": True,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# Psilocin  (4-Hydroxy-N,N-dimethyltryptamine; active form of psilocybin)
# SMILES: CN(C)CCc1c[nH]c2cc(O)ccc12
# Psilocybin SMILES (prodrug): CN(C)CCc1c[nH]c2cc(OP(=O)(O)O)ccc12
# ===========================================================================

def _psilocin_molecular() -> Synthon:
    """
    Psilocin (active form of psilocybin) as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_∈; R_nc; P_±^ψ; F_ℇ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; 1:1⟩

    Key assignments:
        F_MEDIUM (F_eth) — active at mg doses (10-40 mg psilocybin); significantly
            less potent than LSD (μg) or DMT. Ki(5-HT2A) ≈ 100-200 nM. The 4-OH
            group adds a hydrogen bond donor but the overall receptor affinity is
            lower than LSD's ergoline preorganization.
        K_MODERATE — 4-6 hr duration. The prodrug dephosphorylation step (alkaline
            phosphatase converts psilocybin → psilocin) adds a ~30-60 min kinetic
            delay at onset. This is functionally K_mod rather than K_fast despite
            being a simple tryptamine structurally. The prodrug layer is a kinetic
            modifier that the structure alone does not predict.
        Γ_SELECTIVE — most receptor-selective of the tryptamine psychedelics.
            Primarily 5-HT2A, minimal off-target compared to LSD's breadth.
            The 4-OH group provides a precise hydrogen bond geometry that
            tightens selectivity.
        The prodrug architecture (psilocybin) is encodable as a separate
        kinetic-modifier synthon: psilocybin = psilocin + K_mod_phosphate_gate.
    """
    return Synthon(
        name="psilocin_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Psilocin (4-OH-DMT, active form of psilocybin) as receptor ligand. "
            "Most selective tryptamine for 5-HT2A. F_MEDIUM: active at mg doses. "
            "K_mod: 4-6 hr duration, shaped by prodrug dephosphorylation kinetics. "
            "Φ_c induction confirmed (fMRI, MEG); considered the most 'integrative' "
            "psychedelic — sustained window without extremity of DMT or length of LSD."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "CN(C)CCc1c[nH]c2cc(O)ccc12",
            "smiles_prodrug": "CN(C)CCc1c[nH]c2cc(OP(=O)(O)O)ccc12",
            "scaffold": "tryptamine_4hydroxy",
            "primary_receptor": "5-HT2A",
            "receptor_profile": ["5-HT2A", "5-HT1A", "5-HT2C"],
            "ki_primary_nm": 150.0,
            "active_dose_mg_psilocybin": "10-40",
            "duration_hr": "4-6",
            "prodrug_note": (
                "Psilocybin (4-phosphoryloxy-DMT) is the naturally occurring form. "
                "Alkaline phosphatase (gut, blood, brain) cleaves the phosphate → psilocin. "
                "The phosphate group adds ~30-60 min onset delay (kinetic gate). "
                "Psilocybin is K_slow at onset, K_mod at steady-state. "
                "Encoding: psilocybin_molecular = psilocin_molecular with K_mod_gate "
                "in the prodrug position."
            ),
            "endogenous": False,
            "nitrogen_present": True,
            "brain_state_synthon": "psilocin_brain_state",
            "clinical_note": (
                "Most studied psychedelic in clinical trials (depression, addiction). "
                "The K_mod window (sustained, not overwhelming) is a clinical asset — "
                "long enough for therapeutic processing, short enough for controllability."
            ),
            "validation_tier": "primary",
        },
    )


def _psilocin_brain_state() -> Synthon:
    """
    The CNS network state induced by psilocin/psilocybin.

    Formal tuple:
        ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; n:m⟩

    F_MEDIUM at the brain-state level: the Φ_c state achieved by psilocin is
    less extreme than LSD or DMT. fMRI studies show robust criticality measures
    but lower LZc increases than LSD at equivalent subjective intensity ratings.
    The 4-6 hr K_mod window is the therapeutic sweet spot — long enough for
    memory reconsolidation processes (K_slow memory encoding requires ~4 hr),
    short enough to avoid the fatigue of LSD's 12-hr K_slow.
    """
    return Synthon(
        name="psilocin_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain state induced by psilocin. Primitive-identical to LSD brain-state "
            "except F_MEDIUM and K_mod. The 4-6 hr moderate-kinetics window is the "
            "therapeutic sweet spot for memory reconsolidation. Confirmed by fMRI "
            "default mode suppression, increased entropy, maintained global integration. "
            "The reference state for psychedelic-assisted therapy research."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_hr": "4-6",
            "fmri_evidence": [
                "Default mode network suppression (Carhart-Harris et al. 2012)",
                "Increased BOLD signal entropy (Carhart-Harris et al. 2013)",
                "Decreased coupling within DMN; increased coupling between DMN and TPN",
                "Neural avalanche exponent shift toward critical point",
            ],
            "therapeutic_window_note": (
                "K_mod window aligns with memory reconsolidation timescale (~4 hr). "
                "This is the framework basis for the clinical efficacy of psilocybin: "
                "the Φ_c state coincides with a kinetically accessible window for "
                "re-encoding long-term memory traces (K_slow memory = K_trap → K_slow "
                "requires prior K_mod unlocking). The drug opens the window; the therapy "
                "determines what is written into it."
            ),
            "molecular_synthon": "psilocin_molecular",
            "topo_protection_index": 0,
            "t_braid_upgrade_target": True,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# Mescaline  (3,4,5-Trimethoxyphenethylamine)
# SMILES: COc1cc(CCN)cc(OC)c1OC
# ===========================================================================

def _mescaline_molecular() -> Synthon:
    """
    Mescaline as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_|; R_nc; P_±^ψ; F_ℇ; K_slow; G_ℵ; Γ_∨(BROAD); Φ_c; 1:1⟩

    Key assignments:
        T_LINEAR — phenethylamine scaffold: a phenyl ring with a flexible ethylamine
            chain. The three methoxy groups modulate electron density but do not
            create additional ring systems or cage topology. Recognition is through
            a single aromatic face + flexible chain — fundamentally linear vs the
            tryptamines' bicyclic network topology.
        F_MEDIUM — active at 200-500 mg; 100-1000x less potent than LSD.
            The simple phenethylamine scaffold lacks the preorganised binding
            geometry of the ergoline or the indole NH contact — lower fidelity
            of receptor fit, compensated by higher dose.
        K_slow — 8-12 hr duration. This is surprising for such a simple scaffold
            and suggests MAO-mediated slow clearance (the methoxy groups protect
            against rapid MAO-A deamination).
        Γ_BROAD — phenethylamine scaffold hits 5-HT2A but also catecholamine
            receptors (trace amine-associated receptors, TAAR), dopaminergic sites,
            and sigma receptors. Broader receptor grammar than any tryptamine.
        SCAFFOLD NOTE — mescaline is a phenethylamine, not a tryptamine. It shares
            5-HT2A affinity with the tryptamines but via a completely different
            molecular grammar. This is a Γ-convergent result: different scaffolds,
            different molecular topologies, same Φ_c destination at the brain level.
    """
    return Synthon(
        name="mescaline_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Mescaline (3,4,5-trimethoxyphenethylamine) as receptor ligand. "
            "Phenethylamine scaffold — T_linear (vs tryptamines' T_network). "
            "F_MEDIUM: active at 200-500 mg (100-1000x less potent than LSD). "
            "K_slow: 8-12 hr (methoxy groups protect against MAO deamination). "
            "Γ_BROAD: 5-HT2A + catecholamine/TAAR receptors. "
            "Scaffold-diverse but Φ_c-convergent with tryptamines — different "
            "molecular grammar, same brain-state destination."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "COc1cc(CCN)cc(OC)c1OC",
            "scaffold": "phenethylamine_trimethoxy",
            "primary_receptor": "5-HT2A",
            "receptor_profile": ["5-HT2A", "TAAR1", "D2", "alpha2-adrenergic"],
            "ki_primary_nm": 500.0,
            "active_dose_mg": "200-500",
            "duration_hr": "8-12",
            "endogenous": False,
            "scaffold_convergence_note": (
                "Mescaline demonstrates scaffold-independent convergence on Φ_c: "
                "phenethylamine T_linear → same Φ_c as tryptamine T_network. "
                "The molecular topology differs fundamentally but the receptor-level "
                "Γ overlap (5-HT2A) is sufficient to drive the same brain-state. "
                "This is the framework's prediction for grammar-convergent systems: "
                "primitive-level similarity at the grammar layer overrides "
                "structural dissimilarity at the scaffold layer."
            ),
            "cultural_note": (
                "Mescaline is the active compound in peyote (Lophophora williamsii) "
                "and San Pedro cactus. Oldest documented psychedelic use (~5700 BP). "
                "The framework notes: the ancient grammar (ritual context, solar "
                "symbolism, communal setting) provides the Γ structure within which "
                "the molecular Γ operates. The compound opens the Φ_c window; "
                "the cultural grammar determines what is encoded."
            ),
            "nitrogen_present": True,
            "brain_state_synthon": "mescaline_brain_state",
            "validation_tier": "primary",
        },
    )


def _mescaline_brain_state() -> Synthon:
    """
    The CNS network state induced by mescaline.

    Formal tuple:
        ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_slow; G_ℵ; Γ_∨(BROAD); Φ_c; n:m⟩

    Γ_BROAD is preserved into the brain-state: mescaline's broader receptor grammar
    produces a qualitatively different Φ_c state compared to the tryptamines.
    The subjective phenomenology reflects this — mescaline is described as more
    visually rich, more 'earthy', more textured with complex geometry and colour,
    less dissociative than DMT or 5-MeO-DMT. In framework terms: Γ_BROAD → more
    constraint-propagation channels active simultaneously → richer content but
    less extreme depth. The geometry of Φ_c is the same; the dimensionality of
    the content within it is higher.
    """
    return Synthon(
        name="mescaline_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain state induced by mescaline. Γ_BROAD preserved from molecular "
            "level — broader receptor grammar → more simultaneous constraint-propagation "
            "channels → richer visual/sensory content, less dissociation than tryptamines. "
            "K_slow: 8-12 hr. F_MEDIUM: less extreme depth than LSD. "
            "Framework interpretation: broader Γ = wider content-space within Φ_c "
            "rather than deeper access to the G/D degeneracy condition."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_hr": "8-12",
            "phenomenology": (
                "Rich visual geometry, colour enhancement, tactile amplification, "
                "earthen/organic quality, less ego dissolution than tryptamines, "
                "maintained narrative coherence even at high doses"
            ),
            "gamma_broad_interpretation": (
                "Γ_BROAD at the brain-state level means more receptor subtypes "
                "simultaneously engaged, driving more concurrent constraint-propagation "
                "pathways. This produces a 'wider' rather than 'deeper' Φ_c state — "
                "more sensory channels open, but each individual channel less pushed "
                "toward G/D degeneracy."
            ),
            "molecular_synthon": "mescaline_molecular",
            "topo_protection_index": 0,
            "t_braid_upgrade_target": True,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# Salvinorin A  (Neoclerodane diterpene)
# SMILES: [C@@H]1([C@H](OC(C)=O)[C@H]2CC(=O)O[C@@H]([C@@H]3[C@@H]([C@@H]12)C(=O)OC)OC(c4ccoc4)=O)
# ===========================================================================

def _salvinorin_a_molecular() -> Synthon:
    """
    Salvinorin A as a molecular receptor-binding synthon.

    Formal tuple:
        ⟨D_∧; T_⋈; R_nc; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(SPECIFIC); Φ_c; 1:1⟩

    **THE OUTLIER.** Salvinorin A is structurally and mechanistically orthogonal
    to every other psychedelic in this catalog:

    1. NO NITROGEN. Every other classic psychedelic contains a basic amine nitrogen.
       Salvinorin A is a pure terpenoid with no nitrogen at all. The 5-HT2A binding
       motif (protonatable amine) is absent. This alone is enough to mark it as
       a completely different grammar class.

    2. κ-OPIOID RECEPTOR (KOR), NOT 5-HT2A. The primary target is the kappa-opioid
       receptor, not any serotonin receptor. KOR modulates dopamine release
       (inhibitory), acetylcholine, and the dynorphin/endorphin system — entirely
       different constraint-propagation pathways from the serotonergic psychedelics.

    3. T_CYCLIC_BOWTIE — bicyclic diterpene with a lactone and multiple ester groups
       creating a bowtie-like two-directional binding geometry. The furanylmethyl
       ester and acetate groups contact different KOR transmembrane helices
       simultaneously, creating a topological self-complementarity unusual for
       a terpenoid ligand.

    4. P_DONOR_ACCEPTOR — multiple stereocenters enforce highly directional binding.
       The KOR binding requires a specific 3D conformation available only to the
       correct absolute configuration. DIRECTIONAL in both axes.

    5. Γ_SPECIFIC (not SELECTIVE) — uniquely specific for KOR among all known
       psychoactive compounds. Essentially no off-target binding at psychedelic doses.
       This is the most grammar-specific psychedelic.

    The framework interpretation: Salvinorin A proves that Φ_c is accessible via
    orthogonal receptor grammar. The KOR path to criticality is as valid as the
    5-HT2A path. There is no single grammar that owns the Φ_c state.
    """
    return Synthon(
        name="salvinorin_a_molecular",
        dimensionality=Dimensionality.MOLECULAR,
        topology=Topology.CYCLIC_BOWTIE,
        recognition_mode=RecognitionMode.NON_COVALENT,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Salvinorin A (neoclerodane diterpene) as receptor ligand. "
            "THE OUTLIER: no nitrogen, κ-opioid receptor (KOR) agonist — "
            "completely orthogonal grammar to all serotonergic psychedelics. "
            "T_cyclic_bowtie: bicyclic two-directional ester binding geometry. "
            "F_HIGH: Ki(KOR) ≈ 1.9 nM, extremely potent. "
            "K_fast: 3-8 min (smoked). Γ_SPECIFIC: essentially no off-target binding. "
            "Proves Φ_c is grammar-independent — accessible via KOR pathway."
        ),
        metadata={
            "domain_category": "psychedelic_molecular",
            "smiles": "[C@@H]1([C@H](OC(C)=O)[C@H]2CC(=O)O[C@@H]([C@@H]3[C@@H]([C@@H]12)C(=O)OC)OC(c4ccoc4)=O)",
            "scaffold": "neoclerodane_diterpene",
            "primary_receptor": "KOR",
            "receptor_profile": ["KOR"],
            "ki_primary_nm": 1.9,
            "active_dose_mg_smoked": "0.2-1.0",
            "duration_min": "3-8",
            "endogenous": False,
            "nitrogen_present": False,
            "orthogonality_note": (
                "Salvinorin A is the only known psychedelic compound without nitrogen. "
                "The protonatable amine that all other psychedelics use for receptor "
                "binding (the 'pharmacophore nitrogen') is absent. KOR binding is "
                "achieved through ester oxygen contacts — a completely different "
                "recognition chemistry. "
                "Framework: same Φ_c destination, completely different Γ path. "
                "This is the strongest evidence that Φ_c is a topological attractor "
                "accessible from multiple grammar starting points."
            ),
            "kor_grammar_note": (
                "KOR activation: inhibits dopamine release (vs 5-HT2A which increases "
                "cortical glutamate). The Φ_c path via KOR is inhibitory/dopaminergic "
                "suppression rather than excitatory/glutamatergic amplification. "
                "Different grammar operator, same critical topology."
            ),
            "cultural_note": (
                "Active compound in Salvia divinorum, used by Mazatec shamans (Oaxaca). "
                "Traditional use: divinatory states, regarded as qualitatively different "
                "from peyote/mushroom experiences. Framework confirms: orthogonal Γ "
                "produces orthogonal content character, despite same Φ_c topology."
            ),
            "brain_state_synthon": "salvinorin_a_brain_state",
            "validation_tier": "primary",
        },
    )


def _salvinorin_a_brain_state() -> Synthon:
    """
    The CNS network state induced by Salvinorin A.

    Formal tuple:
        ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(SPECIFIC); Φ_c; n:m⟩

    The KOR-mediated brain state converges on the same T_network / G_ℵ / Φ_c
    primitive signature as the serotonergic states, but with Γ_SPECIFIC preserved
    into the brain-state. The phenomenology reflects this: the Salvinorin A state
    is qualitatively unlike serotonergic psychedelics — less visual geometry,
    more reality-distortion and dimensional folding, described as 'being pulled
    through reality rather than expanding within it.' The framework maps this:
    Γ_SPECIFIC → a single high-precision constraint-propagation path rather than
    the broad simultaneous multi-channel activation of serotonergic states.
    High precision, narrow channel, extreme depth.
    """
    return Synthon(
        name="salvinorin_a_brain_state",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Whole-brain state induced by Salvinorin A (KOR). Γ_SPECIFIC preserved: "
            "single high-precision constraint-propagation channel (vs serotonergic "
            "multi-channel). Phenomenology: reality distortion, dimensional folding, "
            "'being pulled through' rather than 'expanding within'. K_fast: 3-8 min. "
            "Same T_network/G_ℵ/Φ_c as serotonergic states — grammar-convergent. "
            "Demonstrates Φ_c is a topological attractor accessible from orthogonal grammar."
        ),
        metadata={
            "domain_category": "psychedelic_brain_state",
            "duration_min": "3-8",
            "phenomenology": (
                "Reality distortion, spatial folding, dimensional alteration, "
                "merging with environment, 'becoming' objects/spaces, "
                "minimal geometric imagery (vs DMT's rich visual grammar), "
                "qualitatively unlike serotonergic states"
            ),
            "gamma_specific_note": (
                "Γ_SPECIFIC at the brain-state level: KOR drives a single "
                "high-precision dopamine-suppression pathway rather than the "
                "simultaneous multi-receptor activation of serotonergic states. "
                "This produces a 'narrower' but extremely deep Φ_c state — "
                "one channel, maximal amplitude. Compare: mescaline (Γ_BROAD → "
                "wide/shallow), LSD (Γ_BROAD → wide/deep), DMT (Γ_SELECTIVE → "
                "moderate/very deep), salvinorin A (Γ_SPECIFIC → narrow/extremely deep)."
            ),
            "molecular_synthon": "salvinorin_a_molecular",
            "topo_protection_index": 0,
            "t_braid_upgrade_target": True,
            "validation_tier": "primary",
        },
    )
