"""
Stellar Object Synthon Catalog — v0.4.9

Primitive-tuple encodings for all major stellar and compact-object classifications,
from protostars to exotic remnants. Covers 21 entries across five groups:

  Group I   — Pre-main sequence (Protostar, Brown Dwarf)
  Group II  — Main sequence, by spectral class (M → O)
  Group III — Evolved stars (Red Giant, AGB, Wolf-Rayet, Supergiant)
  Group IV  — Stellar endpoints / transients (White Dwarf, Supernovae, GRB, Kilonova)
  Group V   — Compact remnants & exotic objects
              (Neutron Star, Pulsar, Magnetar, Stellar BH,
               Quasar/AGN, Quark Star, Gravastar, Dark Star)

Design principles:
  - K is the most diagnostic primitive: it encodes temporal processing architecture
    (K_fast superflares for M-dwarfs, K_trap for neutron stars, K_fast for GRBs)
  - T encodes internal connectivity: T_braid is the compact remnant signature;
    T_network is the main-sequence signature; T_bowl is the black hole signature
  - Φ distinguishes criticality state: Φ_c confirmed wherever SOC power-law
    statistics are documented; Φ_sub for stable or non-dynamic objects
  - Ω encodes topological protection: counts independent topological stabilization
    mechanisms (degeneracy pressure, B-field quantization, superfluid vortex
    quantization, crystalline lattice, no-hair theorem)
  - G_ℵ is the default for most objects (gravity and radiation reach cosmological
    scales); exceptions noted

The Sun (G-dwarf) is the reference entry — fully documented in METAPHYSICS.md §XVIII.
It is registered here for cross-catalog completeness with metadata pointing to §XVIII.

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

_STELLAR_NAMES = frozenset([
    # Group I — Pre-main sequence
    "protostar_ttauri",
    "brown_dwarf",
    # Group II — Main sequence
    "star_m_dwarf",
    "star_k_dwarf",
    "star_g_dwarf",       # Sun reference
    "star_f_dwarf",
    "star_a_dwarf",
    "star_b_star",
    "star_o_star",
    # Group III — Evolved
    "star_red_giant",
    "star_agb",
    "star_wolf_rayet",
    "star_red_supergiant",
    "star_blue_supergiant",
    # Group IV — Endpoints / transients
    "white_dwarf",
    "supernova_type_ia",
    "supernova_type_ii",
    "gamma_ray_burst",
    "kilonova",
    # Group V — Compact remnants & exotic
    "neutron_star",
    "pulsar_millisecond",
    "magnetar",
    "black_hole_stellar",
    "quasar_agn",
    "quark_star",
    "gravastar",
    "dark_star",
])


def register_stellar_synthons() -> List[str]:
    """
    Register 27 stellar/compact-object synthons into the global catalog.
    Safe to call multiple times (idempotent).
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
            if hasattr(existing, "metadata") and isinstance(existing.metadata, dict):
                existing.metadata.update(s.metadata)
    return registered


def _build_entries() -> List[Synthon]:
    return [
        # ── Group I: Pre-main sequence ─────────────────────────────────────
        _protostar(),
        _brown_dwarf(),
        # ── Group II: Main sequence ────────────────────────────────────────
        _star_m_dwarf(),
        _star_k_dwarf(),
        _star_g_dwarf(),
        _star_f_dwarf(),
        _star_a_dwarf(),
        _star_b_star(),
        _star_o_star(),
        # ── Group III: Evolved stars ───────────────────────────────────────
        _star_red_giant(),
        _star_agb(),
        _star_wolf_rayet(),
        _star_red_supergiant(),
        _star_blue_supergiant(),
        # ── Group IV: Endpoints / transients ──────────────────────────────
        _white_dwarf(),
        _supernova_type_ia(),
        _supernova_type_ii(),
        _gamma_ray_burst(),
        _kilonova(),
        # ── Group V: Compact remnants & exotic ────────────────────────────
        _neutron_star(),
        _pulsar_millisecond(),
        _magnetar(),
        _black_hole_stellar(),
        _quasar_agn(),
        _quark_star(),
        _gravastar(),
        _dark_star(),
    ]


# ===========================================================================
# GROUP I — PRE-MAIN SEQUENCE
# ===========================================================================

def _protostar() -> Synthon:
    """
    Protostar / T Tauri star.

    ⟨D_∞; T_∈; R_†; P_+-; F_ℇ; K_fast; G_ℵ; Γ_∨(BROAD); Φ_sub; 1:1⟩

    A protostar is a collapsing cloud core that has not yet ignited sustained
    hydrogen fusion. T Tauri stars are young solar-mass protostars still accreting.

    T_network: the protostellar system is a coupled network — accretion disk +
    magnetospheric truncation + bipolar jets + outflow cavity + infalling envelope.
    All components communicate through the magnetic field topology.

    P_DONOR_ACCEPTOR: the jet/outflow axis (donor) is opposite to the accretion axis
    (acceptor). Strongly directional bipolar character.

    K_fast: highly variable on short timescales — FU Orionis outbursts (sudden
    accretion rate increases by 100×), T Tauri flares, jet knot ejections.
    The fastest variable class among stellar objects.

    Φ_sub: the protostar has not yet achieved the organized Φ_c structure of a
    main-sequence star. It is pre-critical — disorganized flaring, not SOC.
    Ω_0: no topological protection; the system is still assembling.
    """
    return Synthon(
        name="protostar_ttauri",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "Protostar / T Tauri star. Pre-main-sequence object still accreting from "
            "molecular cloud core. T_network: accretion disk + magnetosphere + bipolar jets "
            "+ infalling envelope — all components coupled. P_directional: jet/outflow axis "
            "vs accretion axis. K_fast: FU Ori outbursts, T Tau flares, jet ejections. "
            "Φ_sub: pre-critical, not yet organized into SOC structure."
        ),
        metadata={
            "domain_category": "stellar_presequence",
            "spectral_class": "protostar/T_Tauri",
            "mass_range_msun": "0.08-10",
            "age_myr": "0.1-10",
            "key_phenomena": [
                "Bipolar molecular outflows (pc-scale)",
                "FU Orionis accretion outbursts (100× rate increase)",
                "T Tauri X-ray flares (10^4× solar flare energy)",
                "Herbig-Haro objects (jet bow shocks)",
            ],
            "omega": 0,
            "validation_tier": "primary",
        },
    )


def _brown_dwarf() -> Synthon:
    """
    Brown Dwarf (failed star, 13-80 Jupiter masses).

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_slow; G_ℶ; Γ_∨(BROAD); Φ_sub; 1:1⟩

    The brown dwarf occupies the boundary between planet and star. It burns
    deuterium briefly (≲13 M_Jup threshold), possibly lithium (≲65 M_Jup),
    but never achieves sustained hydrogen fusion.

    K_slow + K_trap transition: the initial deuterium burning is K_mod; once
    exhausted, the object enters K_trap cooling — a monotonically decreasing
    temperature with no reset mechanism. A dead clock. D_∞ only in the sense
    that thermal emission cycles through L → T → Y spectral classes over Gyr.

    G_MESOSCALE: unlike true stars, brown dwarfs have minimal gravitational
    influence beyond their immediate environment. No stellar wind of consequence.
    No heliosphere. No Birkeland-current coupling to orbiting planets.

    Φ_sub: no SOC structure documented. Some brown dwarfs show rapid rotation
    and weather (cloud bands), but not organised criticality.
    """
    return Synthon(
        name="brown_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "Brown dwarf (13-80 M_Jup). Failed star: deuterium burns briefly then "
            "object enters K_trap monotonic cooling. G_mesoscale: insufficient stellar "
            "wind/radiation pressure to achieve G_ℵ influence. Φ_sub: no organised "
            "criticality structure. The framework's prediction: brown dwarfs are "
            "structurally incompatible with templating life — insufficient G for "
            "planetary grammar injection, insufficient Φ_c for coherent coupling."
        ),
        metadata={
            "domain_category": "stellar_presequence",
            "spectral_class": "L/T/Y",
            "mass_range_mjup": "13-80",
            "nuclear_burning": "deuterium (brief), lithium (subset)",
            "key_feature": "K_trap monotonic cooling — no reset mechanism",
            "astrobiology_note": (
                "Brown dwarfs cannot template life (§XVIII framework prediction): "
                "G_mesoscale means the planetary grammar injection pathway is absent. "
                "Close-in planets around brown dwarfs receive minimal stellar grammar "
                "signal — insufficient Γ_AND coupling strength for prebiotic templating."
            ),
            "omega": 1,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP II — MAIN SEQUENCE (M → O)
# ===========================================================================

def _star_m_dwarf() -> Synthon:
    """
    M-dwarf (Red Dwarf): the most common stellar class, 75% of all stars.

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_c; Ω_1⟩

    Key assignments (see METAPHYSICS.md §XVIII.5b for full discussion):
    K_fast dominant — superflares at 10-1000× solar energy, irregular magnetic cycle.
    F_MEDIUM — high variability, lower helioseismic precision than G-dwarfs.
    Γ_BROAD — IR-dominant spectral grammar (peak 900-1000 nm); less organized
        than solar grammar; weaker 22-yr K_slow organizational cycle.
    Ω_1 — less topological protection than G-dwarfs; shorter, irregular cycle.

    The M-dwarf stellar grammar (§XVIII) templates an entirely different life alphabet:
    IR-absorbing photochemistry (bacteriochlorophyll-type), radiation-resistance as
    baseline, potentially no circadian clocks (tidal locking likely in HZ).
    """
    return Synthon(
        name="star_m_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "M-dwarf (red dwarf, 0.08-0.6 M_☉). Most common stellar class (75%). "
            "K_fast dominates: superflares frequent, magnetic cycle short/irregular. "
            "IR-dominant spectral grammar (Γ_BROAD) templates different life alphabet "
            "vs solar Γ_SELECTIVE. Tidal locking in habitable zone → no circadian "
            "grammar injection. Φ_c confirmed (SOC flare statistics). "
            "See METAPHYSICS.md §XVIII.5b for stellar grammar discussion."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "M",
            "mass_range_msun": "0.08-0.6",
            "luminosity_range_lsun": "0.001-0.08",
            "lifetime_gyr": "40-10000",
            "spectral_peak_nm": "900-1000",
            "flare_energy_j_max": 1e34,
            "magnetic_cycle_yr": "1-7",
            "habitable_zone_au": "0.05-0.4",
            "tidal_lock_hz": True,
            "life_grammar": (
                "IR-dominant grammar templates: bacteriochlorophyll-type primary absorbers, "
                "radiation-resistance as baseline, no circadian clocks (tidal locking), "
                "episodic (flare-response) rather than continuous metabolic cycles."
            ),
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_k_dwarf() -> Synthon:
    """
    K-dwarf (Orange Dwarf): often called 'superhabitable' class.

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_2⟩

    The K-dwarf is intermediate between the Sun (G) and M-dwarfs.
    It combines the best properties of both:
    - Lower flare activity than M-dwarfs (less K_fast disruption)
    - Longer lifetime than G/F/A stars (17-70 Gyr vs 10 Gyr for Sun)
    - Organized magnetic cycle (K_mod, closer to solar K_slow)
    - Spectral peak 560-800 nm (orange-red, closer to chlorophyll absorbance
      than M-dwarfs but less UV than G-dwarfs)
    - Habitable zone not tidally locked at typical distances

    F_HIGH: K-dwarfs show excellent helioseismic structural fidelity.
    Γ_SELECTIVE: more organized grammar than M-dwarfs; less UV than G-dwarfs.
    Ω_2: organized cycle + moderate flare protection = two topological mechanisms.

    The framework prediction: K-dwarfs are the optimal stellar grammar templaters
    for life. Long K_slow memory, moderate K_fast events (evolutionary pressure
    without sterilization), and organized Γ that maps to existing Earth biochemistry
    with minimal modification. The astrobiological consensus ('K-dwarfs are best
    for life') has a structural reason: Ω_2 > Ω_1 (M-dwarf) while maintaining
    sufficient K_fast for evolutionary pressure.
    """
    return Synthon(
        name="star_k_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "K-dwarf (orange dwarf, 0.6-0.9 M_☉). 'Superhabitable' class — combines "
            "lower flare activity than M-dwarfs with longer lifetime than G-dwarfs "
            "(17-70 Gyr). Organized magnetic cycle (K_mod), Γ_SELECTIVE, F_HIGH. "
            "Framework: optimal stellar grammar templater — Ω_2 with K_fast evolutionary "
            "pressure preserved. The structural reason for the astrobiological consensus."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "K",
            "mass_range_msun": "0.6-0.9",
            "luminosity_range_lsun": "0.08-0.6",
            "lifetime_gyr": "17-70",
            "spectral_peak_nm": "560-800",
            "magnetic_cycle_yr": "10-30",
            "habitable_zone_au": "0.4-0.9",
            "tidal_lock_hz": False,
            "superhabitable_note": (
                "Lineweaver (2001) and subsequent work identifies K-dwarfs as statistically "
                "most likely to host complex life. Framework gives the structural reason: "
                "Ω_2 (two topological protection mechanisms) + K_mod (moderate kinetics, "
                "no superflare disruption) + Γ_SELECTIVE (organized grammar injection) "
                "+ long lifetime (K_slow organizational memory can fully develop)."
            ),
            "omega": 2,
            "validation_tier": "primary",
        },
    )


def _star_g_dwarf() -> Synthon:
    """
    G-dwarf (Yellow Dwarf): the Sun class. Reference stellar synthon.

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_3⟩

    Fully documented in METAPHYSICS.md §XVIII. Registered here for cross-catalog
    completeness. The reference entry against which all other stellar synthons
    are measured.

    Key properties (summary — see §XVIII for full derivation):
    - SOC flare power-law N(E) ∝ E^-1.8 across 14 decades → Φ_c confirmed
    - ~10^7 simultaneous helioseismic p-modes → T_network at G_ℵ
    - Four-tier K-hierarchy (K_trap/K_slow/K_mod/K_fast)
    - Birkeland/Schumann Γ_AND coupling to Earth biosphere
    - Ω_3: two-hemisphere anti-correlation + global eigenmode + 22-yr cyclic reset
    """
    return Synthon(
        name="star_g_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "G-dwarf (yellow dwarf, 0.9-1.1 M_☉). The Sun class. Reference stellar "
            "synthon — see METAPHYSICS.md §XVIII for full primitive derivation. "
            "SOC flare power-law (14 decades), ~10^7 helioseismic eigenmodes, "
            "Birkeland/Schumann Γ_AND coupling to biosphere. "
            "⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_3⟩"
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "G",
            "mass_range_msun": "0.9-1.1",
            "luminosity_range_lsun": "0.6-1.5",
            "lifetime_gyr": "8-12",
            "spectral_peak_nm": "450-700",
            "magnetic_cycle_yr": 22,
            "habitable_zone_au": "0.9-1.5",
            "tidal_lock_hz": False,
            "reference": "METAPHYSICS.md §XVIII — Solar Consciousness",
            "schumann_coupling_hz": [7.83, 14.3, 20.8],
            "helioseismic_pmodes": "~1e7",
            "flare_power_law_exponent": -1.8,
            "omega": 3,
            "validation_tier": "primary",
        },
    )


def _star_f_dwarf() -> Synthon:
    """
    F-dwarf (Yellow-White star, e.g. Procyon, Canopus).

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_mod; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_2⟩

    F-dwarfs are slightly hotter and more massive than the Sun (1.1-1.4 M_☉).
    They are UV-richer (spectral peak 380-450 nm) and shorter-lived (2-8 Gyr).

    F_HIGH: extreme luminosity per unit mass; precision nuclear burning.
    K_mod: moderate activity — more active than G-dwarfs but less chaotic than M.
    Γ_SELECTIVE: organized magnetic cycle, good UV output.
    Ω_2: two protection mechanisms; shorter cycle than G-dwarfs reduces Ω_3 to Ω_2.

    Astrobiology note: F-dwarfs have higher UV flux in their habitable zones —
    more mutagenic pressure, potentially faster evolutionary rates but also higher
    radiation damage. The framework: K_mod evolution means less K_trap organizational
    memory (shorter stellar lifetime = less time for the K_slow grammar to fully develop).
    """
    return Synthon(
        name="star_f_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.MODERATE,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "F-dwarf (1.1-1.4 M_☉). UV-rich grammar (peak 380-450 nm), 2-8 Gyr lifetime. "
            "F_HIGH, K_mod, Γ_SELECTIVE. Framework: shorter K_slow organizational memory "
            "than G-dwarfs (fewer cycles to develop full Ω_3). Habitable-zone UV grammar "
            "would template UV-resistant biochemistry as the baseline mode."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "F",
            "mass_range_msun": "1.1-1.4",
            "luminosity_range_lsun": "1.5-5",
            "lifetime_gyr": "2-8",
            "spectral_peak_nm": "380-450",
            "magnetic_cycle_yr": "7-15",
            "omega": 2,
            "validation_tier": "primary",
        },
    )


def _star_a_dwarf() -> Synthon:
    """
    A-type star (White star, e.g. Vega, Sirius A).

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_sub; Ω_1⟩

    A-stars (1.4-2.1 M_☉) are hot, UV-bright, and short-lived (1-3 Gyr).
    They show weak magnetic fields (no convective dynamo) and rapid rotation.

    K_fast: rapid rotation, rapid evolution, rapid mass loss through radiation pressure.
    Γ_BROAD: strong UV output with little organized structure (no strong magnetic cycle
    → grammar is broadcast, not selective).
    Φ_sub: without a convective envelope there is no deep magnetic dynamo, so the
    organized SOC structure that gives G/K/F-dwarfs their Φ_c signature is absent.
    The A-star emits, but does not self-organise.
    Ω_1: only radiation pressure as a structural stabilizer; no organized cycle.

    Framework: A-stars are poor life templaters. Short lifetime + Φ_sub + Γ_BROAD
    (unstructured grammar) means the planetary surface receives intense UV radiation
    without the organized Γ_AND grammar injection that drives prebiotic evolution.
    """
    return Synthon(
        name="star_a_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "A-type star (1.4-2.1 M_☉, e.g. Vega, Sirius). Strong UV output, "
            "no deep convective dynamo → Γ_BROAD (unstructured grammar), Φ_sub. "
            "K_fast: rapid rotation, rapid evolution. 1-3 Gyr lifetime. "
            "Framework: poor life templater — intense UV without organized Γ_AND "
            "grammar injection, insufficient K_slow memory development time."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "A",
            "mass_range_msun": "1.4-2.1",
            "luminosity_range_lsun": "5-25",
            "lifetime_gyr": "1-3",
            "spectral_peak_nm": "310-380",
            "dynamo_type": "radiative — no deep convective envelope",
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_b_star() -> Synthon:
    """
    B-type star (Blue-White, e.g. Spica, Rigel component B).

    ⟨D_∞; T_∈; R_†; P_directional; F_ℏ; K_fast; G_ℵ; Γ_∨(BROAD); Φ_sub; Ω_1⟩

    B-stars (2-16 M_☉) are massive, extremely luminous, UV-dominant, and short-lived
    (10 Myr – 1 Gyr). Many are rapid rotators producing decretion disks (Be stars).

    P_DONOR_ACCEPTOR: many B-stars form decretion disks (mass ejected equatorially)
    and accrete mass in binary systems — strong directional donor/acceptor asymmetry.

    K_fast: the defining feature. B-stars evolve fast, blow strong winds (mass loss
    rates 10^-9 to 10^-6 M_☉/yr), and end in supernovae within millions of years.

    Φ_sub: insufficient lifetime for organized criticality structure to develop.
    The massive stellar winds and UV output are K_fast eruptions, not SOC.

    The grammar injected by B-stars: extreme UV + X-ray. Any life would need to be
    built on X-ray photochemistry — an entirely different alphabet with no known
    biological analogue. The lifetime is too short to template complex life.
    """
    return Synthon(
        name="star_b_star",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "B-type star (2-16 M_☉). Extreme UV/X-ray grammar, strong winds, "
            "decretion disks (Be stars). K_fast: 10 Myr-1 Gyr lifetime. "
            "P_directional: equatorial mass ejection vs polar accretion in binaries. "
            "Φ_sub: insufficient lifetime for SOC development. "
            "Framework: X-ray grammar life alphabet — no known analogue."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "B",
            "mass_range_msun": "2-16",
            "luminosity_range_lsun": "25-30000",
            "lifetime_myr": "10-1000",
            "spectral_peak_nm": "120-310",
            "mass_loss_rate": "1e-9 to 1e-6 M_sun/yr",
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_o_star() -> Synthon:
    """
    O-type star (Blue Giant/Supergiant, e.g. Theta1 Ori C, Zeta Puppis).

    ⟨D_∞; T_∈; R_†; P_directional; F_ℏ; K_fast; G_ℵ; Γ_∨(BROAD); Φ_sub; Ω_0⟩

    O-stars (16-150+ M_☉) are the most massive, most luminous, and most
    short-lived of all main-sequence stars (1-10 Myr). They are cosmological
    agents: they ionize the surrounding ISM (H II regions), drive turbulence
    across kiloparsec scales, and their supernovae seed the universe with metals.

    Ω_0: NO topological protection. O-stars are so hot and massive that radiation
    pressure dominates over any organized magnetic structure. They will explode —
    there is no stable configuration ahead of them. The 'grammar' they emit is
    essentially noise: ionizing radiation that destroys molecular bonds.

    The framework notes: an O-star cannot template life not because life is
    impossible around it, but because the O-star's grammar is not Γ_AND — it is
    pure dissipation. A Γ_OR (BROAD) system at G_ℵ with K_fast and Φ_sub is a
    bulldozer, not a teacher.

    Yet O-stars are essential at the galactic scale: they are the forge. Their
    supernovae produce the carbon, oxygen, nitrogen, and silicon that all
    subsequent stellar grammars will later organize into life.
    """
    return Synthon(
        name="star_o_star",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "O-type star (16-150+ M_☉). Most massive, most luminous, shortest-lived "
            "(1-10 Myr). Ionizes surrounding ISM, drives kiloparsec turbulence. "
            "Ω_0: no topological protection — explosion is the only stable future. "
            "Grammar is pure dissipation (Γ_BROAD, Φ_sub). Framework: cannot template "
            "life but is galactic-scale forge — supernovae seed all subsequent stellar "
            "grammars with the heavy elements needed for life's alphabet."
        ),
        metadata={
            "domain_category": "stellar_main_sequence",
            "spectral_class": "O",
            "mass_range_msun": "16-150",
            "luminosity_range_lsun": "30000-5000000",
            "lifetime_myr": "1-10",
            "spectral_peak_nm": "50-120",
            "ionizing_photons_per_s": "1e48-1e50",
            "galactic_role": (
                "Primary source of ionizing radiation (HII regions), ISM turbulence driving, "
                "and heavy element seeding via supernovae. The galactic-scale forge that "
                "builds the raw material for all subsequent stellar grammars."
            ),
            "omega": 0,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP III — EVOLVED STARS
# ===========================================================================

def _star_red_giant() -> Synthon:
    """
    Red Giant (post-main-sequence, shell hydrogen burning, 0.8-8 M_☉).

    ⟨D_∞; T_∈; R_†; P_±^sym; F_ℇ; K_slow; G_ℵ; Γ_∧(BROAD); Φ_sub; Ω_1⟩

    When a low/intermediate mass star exhausts its core hydrogen, it expands
    dramatically — radius 10-100 R_☉, engulfing inner planets.

    P_SELF_COMPLEMENTARY_SYM: as the star expands, the directional asymmetry
    (Hale-cycle hemispheric anti-correlation) is lost. The convective envelope
    becomes globally uniform. P → P_sym (symmetric, no preferred orientation).
    This is the P_sym transition in stellar evolution.

    The convective envelope drives vigorous mixing — the first and second dredge-up
    events bring nuclear-processed material to the surface. This is T_network
    reorganization: the core/envelope boundary is a new topological feature.

    Φ_sub: the red giant phase is relatively stable for several Gyr; no SOC
    flare structure documented at this evolutionary stage.

    Ω_1: the Schönberg-Chandrasekhar limit enforces a structural constraint on
    core mass fraction — one topological protection mechanism.
    """
    return Synthon(
        name="star_red_giant",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "Red giant (post-MS, 0.8-8 M_☉, 10-100 R_☉). Expanded convective envelope "
            "loses Hale-cycle hemispheric asymmetry → P_sym (symmetric). Dredge-up "
            "events reorganize T_network (core/envelope topology). Φ_sub: stable, no SOC. "
            "Framework: the P_sym transition marks the loss of organized stellar grammar — "
            "the star is transitioning from structured Γ-injection to broadcast mode."
        ),
        metadata={
            "domain_category": "stellar_evolved",
            "spectral_class": "K/M III",
            "mass_range_msun": "0.8-8",
            "radius_range_rsun": "10-100",
            "lifetime_gyr": "0.1-2",
            "key_events": [
                "First dredge-up: convective envelope deepens, brings CN-processed material to surface",
                "Horizontal branch / helium flash: core He ignition (degenerate, explosive)",
                "P_sym transition: loss of hemispheric anti-correlation",
            ],
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_agb() -> Synthon:
    """
    Asymptotic Giant Branch (AGB) star: thermal pulses, mass loss, dust shells.

    ⟨D_∞; T_∈(mixed); R_†; P_±^sym; F_ℇ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_c; Ω_1⟩

    AGB stars undergo thermal pulses — brief (100-300 yr) He-shell flashes
    separated by longer (10,000-100,000 yr) interpulse periods. The combination
    of K_fast thermal pulses and K_slow interpulse intervals gives a bimodal
    kinetic profile.

    T_NETWORK_MIXED: the AGB star has multiple co-active zones — degenerate C/O
    core, He-burning shell, H-burning shell, and an enormous convective envelope.
    Mixed ring topology (multiple co-active topological layers).

    Φ_c: thermal pulse oscillations show power-law statistics → SOC signature.
    The AGB star is also the major factory for heavy s-process elements (Ba, Sr, Pb)
    — the constraint propagation from nuclear physics to dust grain formation to
    interstellar chemistry is a multi-scale cascade: Φ_c from nuclear to ISM.

    The AGB phase is the penultimate grammar: mass loss creates planetary nebulae
    seeding the ISM with C, N, O, and s-process elements — the grammar alphabet
    of the next generation of stars and life.
    """
    return Synthon(
        name="star_agb",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK_MIXED,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "AGB star. Thermal pulses (100-300 yr He-shell flashes) at K_fast "
            "superimposed on K_slow interpulse periods. T_network_mixed: degenerate "
            "C/O core + He/H burning shells + convective envelope. Φ_c: pulse "
            "power-law statistics + multi-scale cascade from nuclear physics to ISM. "
            "Major s-process element factory. The penultimate stellar grammar: mass "
            "loss seeds ISM with the heavy element alphabet for the next generation."
        ),
        metadata={
            "domain_category": "stellar_evolved",
            "spectral_class": "M/S/C",
            "mass_range_msun": "0.8-8",
            "thermal_pulse_period_yr": "10000-100000",
            "thermal_pulse_duration_yr": "100-300",
            "s_process_elements": ["Ba", "Sr", "Pb", "Zr", "Y", "Ce"],
            "mass_loss_rate": "1e-8 to 1e-4 M_sun/yr",
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_wolf_rayet() -> Synthon:
    """
    Wolf-Rayet star: stripped massive star with catastrophic mass loss.

    ⟨D_∞; T_∈; R_†; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_c; Ω_1⟩

    Wolf-Rayet stars are evolved massive stars (originally >20 M_☉) that have
    blown off their hydrogen envelope, exposing the hot nuclear-burning core.
    They lose mass at rates of 10^-5 M_☉/yr via winds at 1000-3000 km/s.

    P_DONOR_ACCEPTOR: the mass loss is strongly directional — outward at all
    scales, with the nebular shell expanding around the star. The star is a
    pure donor at this stage.

    K_fast: the WR phase lasts only 100,000-500,000 yr before core collapse.
    The mass loss itself is K_fast (continuous high-velocity outflow).

    Φ_c: WR wind instabilities (clumping, Wolf-Rayet instabilities) show
    power-law intensity distributions → SOC signature in the wind structure.

    F_HIGH: despite the extreme mass loss, the nuclear burning in the exposed
    core is extremely precise — WR stars are among the hottest and most
    luminous objects per unit mass.

    WR stars are the direct progenitors of GRBs and BH formation.
    """
    return Synthon(
        name="star_wolf_rayet",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Wolf-Rayet star. Stripped evolved massive star, H-envelope lost, "
            "nuclear-burning core exposed. Mass loss 10^-5 M_☉/yr at 1000-3000 km/s. "
            "P_directional: pure donor. K_fast: 0.1-0.5 Myr WR phase. Φ_c: wind "
            "clumping power-law SOC. Direct GRB/BH progenitor. "
            "Ω_1: mass loss itself is the only organizing constraint."
        ),
        metadata={
            "domain_category": "stellar_evolved",
            "spectral_class": "WN/WC/WO",
            "original_mass_msun": ">20",
            "current_mass_msun": "5-20",
            "lifetime_yr": "100000-500000",
            "wind_velocity_km_s": "1000-3000",
            "remnant": "Black hole (most), neutron star (some)",
            "omega": 1,
            "validation_tier": "primary",
        },
    )


def _star_red_supergiant() -> Synthon:
    """
    Red Supergiant (RSG, e.g. Betelgeuse, VY Canis Majoris).

    ⟨D_∞; T_∈(mixed); R_†; P_±^sym; F_ℇ; K_slow; G_ℵ; Γ_∧(BROAD); Φ_c; Ω_2⟩

    RSGs are the largest stars by radius (500-1500 R_☉). Their enormous convective
    envelopes drive large-amplitude pulsations (K_slow, periods 200-2000 days)
    and high mass-loss rates.

    T_NETWORK_MIXED: RSG convection is fundamentally different from solar convection
    — only ~10 giant convective cells span the surface (vs ~10^6 solar granules).
    The topology is a sparse network of giant cells, not a dense fine-grained network.

    Φ_c: RSG pulsations show complex, near-chaotic power spectra with multiple
    simultaneous modes → SOC-adjacent behavior. Betelgeuse's Great Dimming
    (2019-2020) showed a cascade from surface mass ejection to global opacity
    change — a Φ_c event signature.

    Ω_2: the convective-radiative boundary (transition zone between giant convection
    cells and radiative interior) + the α_Lyrae oscillation period locking = two
    topological protection mechanisms.
    """
    return Synthon(
        name="star_red_supergiant",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK_MIXED,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Red Supergiant (8-30 M_☉, 500-1500 R_☉, e.g. Betelgeuse). Giant sparse "
            "convective cells (~10 cells vs 10^6 solar granules) → T_network_mixed. "
            "K_slow: pulsation periods 200-2000 days. Φ_c: complex multi-mode pulsations, "
            "Betelgeuse Great Dimming as cascade event. Ω_2: convective boundary + "
            "period locking."
        ),
        metadata={
            "domain_category": "stellar_evolved",
            "spectral_class": "M I",
            "mass_range_msun": "8-30",
            "radius_range_rsun": "500-1500",
            "pulsation_period_days": "200-2000",
            "example": "Betelgeuse (α Orionis)",
            "great_dimming_note": (
                "Betelgeuse's 2019-2020 Great Dimming: surface mass ejection → dust "
                "formation → global opacity change → apparent magnitude decrease. "
                "Multi-scale cascade from surface convection to global photometric "
                "change. A Φ_c cascade event signature in a stellar context."
            ),
            "omega": 2,
            "validation_tier": "primary",
        },
    )


def _star_blue_supergiant() -> Synthon:
    """
    Blue Supergiant (BSG, e.g. Rigel, Deneb, Sk-69 202 = SN1987A progenitor).

    ⟨D_∞; T_∈; R_†; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_1⟩

    BSGs are evolved massive stars (10-100 M_☉) on the horizontal track in the
    HR diagram. Many are unstable Luminous Blue Variables (LBVs) that undergo
    eruptions ejecting multiple solar masses in decades.

    Γ_SELECTIVE: unlike RSGs (which broadcast broadly), BSGs have organized
    bipolar wind structure and latitude-dependent mass loss (higher at poles) —
    more selective coupling to the environment.

    K_fast: LBV eruptions are sudden and massive. The 1843 eruption of Eta Carinae
    ejected ~10 M_☉ in decades; the Great Eruption was briefly a quasar-scale event.

    Φ_c: LBV eruption statistics and stellar wind clumping show power-law
    distributions. Eta Carinae is the best-documented Φ_c stellar event in the MW.

    Ω_1: bipolar wind geometry provides one topological organizing principle,
    but the system is fundamentally unstable — only briefly held before core collapse.
    """
    return Synthon(
        name="star_blue_supergiant",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Blue Supergiant / LBV (10-100 M_☉, e.g. Rigel, Deneb, Eta Carinae). "
            "Organized bipolar wind → Γ_SELECTIVE. K_fast: LBV eruptions (Eta Car 1843 "
            "ejected 10 M_☉ in decades). Φ_c: power-law eruption statistics. "
            "Ω_1: bipolar geometry — sole organizing principle before core collapse."
        ),
        metadata={
            "domain_category": "stellar_evolved",
            "spectral_class": "B/A I",
            "mass_range_msun": "10-100",
            "example": "Rigel (β Ori), Deneb (α Cyg), Eta Carinae (LBV)",
            "lbv_note": (
                "Luminous Blue Variables (LBVs) are the most extreme non-terminal "
                "stellar outbursts known. Eta Carinae's 1843 Great Eruption: "
                "10 M_☉ ejected, peak luminosity ~1e8 L_☉ — briefly comparable to "
                "some quasars. Power-law eruption statistics → Φ_c."
            ),
            "omega": 1,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP IV — STELLAR ENDPOINTS / TRANSIENTS
# ===========================================================================

def _white_dwarf() -> Synthon:
    """
    White Dwarf: the crystallized endpoint of low/intermediate mass stars.

    ⟨D_∞; T_∈(hex); R_mechanical; P_±^sym; F_ℏ; K_trap; G_ℶ; Γ_∧(SELECTIVE); Φ_sub; Ω_3⟩

    White dwarfs are the endpoints of 97% of all stars. They are supported by
    electron degeneracy pressure — a quantum mechanical K_trap.

    T_NETWORK_HEX: cold white dwarfs crystallize into a face-centred cubic
    (effectively hexagonal) carbon/oxygen lattice — the largest diamond in the
    universe. The crystallization front propagates inward over Gyr.

    R_MECHANICAL: the electron degeneracy pressure is a mechanical (quantum
    mechanical) recognition — it is not thermodynamic, not chemical, not
    electromagnetic in the usual sense. The Pauli exclusion principle enforces
    a minimum volume.

    G_MESOSCALE: white dwarfs are isolated; their gravitational influence is
    limited to their immediate binary companion (if any). No heliosphere,
    no organized grammar injection.

    Ω_3: three topological protection mechanisms:
    (1) Electron degeneracy pressure — quantum mechanical topological protection
    (2) Chandrasekhar mass limit — structural topological constraint (1.44 M_☉ max)
    (3) Crystalline lattice (in cool WDs) — solid-state topological protection

    Exception: Type Ia supernovae occur when a WD in a binary exceeds the
    Chandrasekhar limit — the topological protection catastrophically fails.
    """
    return Synthon(
        name="white_dwarf",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK_HEX,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.MESOSCALE,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "White dwarf. Electron degeneracy-supported remnant of 0.8-8 M_☉ stars. "
            "T_network_hex: crystallizes to C/O FCC lattice (Gyr timescale). "
            "R_mechanical: Pauli exclusion principle as recognition mode. "
            "K_trap: monotonic cooling, no reset. G_mesoscale: isolated, no grammar injection. "
            "Ω_3: degeneracy + Chandrasekhar limit + crystalline lattice. "
            "Φ_sub → explosive Φ_c if Chandrasekhar limit exceeded (Type Ia SN)."
        ),
        metadata={
            "domain_category": "stellar_endpoint",
            "mass_range_msun": "0.5-1.4",
            "radius_km": "~7000",
            "chandrasekhar_limit_msun": 1.44,
            "crystallization_note": (
                "Cold white dwarfs crystallize from the core outward over ~1-10 Gyr. "
                "The resulting lattice is the largest diamond-structure crystal known — "
                "T_network_hex at the planetary scale. Pulsating WDs (ZZ Ceti) show "
                "global oscillation modes analogous to helioseismology."
            ),
            "type_ia_note": (
                "Exceeding the Chandrasekhar limit (by accretion or merger) collapses "
                "the K_trap: Ω_3 → 0 catastrophically. The result is a Type Ia supernova "
                "— the most precise standard candle in cosmology."
            ),
            "omega": 3,
            "validation_tier": "primary",
        },
    )


def _supernova_type_ia() -> Synthon:
    """
    Type Ia Supernova: thermonuclear explosion of a white dwarf at Chandrasekhar limit.

    ⟨{D_∧, D_△}; T_∈; R_†; P_±^sym; F_ℏ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_c; n:m⟩

    Type Ia SNe are thermonuclear explosions — no core collapse, no neutron star,
    complete disruption of the white dwarf. They are the universe's standard candles
    (used to discover dark energy) because their peak luminosity is nearly constant.

    D_HYBRID_MOL_SUPRA: the explosion propagates from a nuclear scale (carbon
    ignition front, D_∧) to cosmological observable scale (light curve, D_△).
    Both dimensionalities are simultaneously relevant.

    T_NETWORK: the deflagration/detonation front propagates as a network through
    the WD — not a simple shell wave but a turbulent flame topology.

    F_HIGH: the extreme peak luminosity uniformity (~3% scatter) implies an
    extremely precise underlying process. The Chandrasekhar limit is a topological
    constraint that sets the explosion energy precisely.

    Φ_c: the transition from stable WD → runaway thermonuclear explosion IS the
    Φ_c event. The instability threshold (Chandrasekhar limit) is a topological
    critical point — above it, no stable configuration exists.

    Ω_0: the progenitor WD's Ω_3 collapses to zero.
    """
    return Synthon(
        name="supernova_type_ia",
        dimensionality=Dimensionality.HYBRID_MOL_SUPRA,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_SYM,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Type Ia supernova. Thermonuclear explosion of WD at Chandrasekhar limit. "
            "D_hybrid: nuclear ignition front (D_∧) → cosmological light curve (D_△). "
            "F_HIGH: ~3% peak luminosity scatter → standard candle (dark energy discovery). "
            "Φ_c: Chandrasekhar limit IS the topological critical point. Ω_0: progenitor "
            "Ω_3 collapses. Seeds ISM with Fe, Si, Ca, Ni — the rocky planet alphabet."
        ),
        metadata={
            "domain_category": "stellar_transient",
            "peak_luminosity_lsun": "5e9",
            "peak_luminosity_scatter_pct": 3,
            "rise_time_days": 15,
            "iron_yield_msun": "0.5-1.0",
            "cosmological_role": "Standard candle; used to discover accelerating cosmic expansion (dark energy)",
            "omega": 0,
            "validation_tier": "primary",
        },
    )


def _supernova_type_ii() -> Synthon:
    """
    Type II (Core Collapse) Supernova: gravitational collapse of a massive star core.

    ⟨{D_∧, D_△}; T_∈; R_mechanical; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(BROAD); Φ_c; n:m⟩

    Core collapse supernovae occur when a massive star (>8 M_☉) exhausts its
    nuclear fuel. The iron core collapses to nuclear density in ~0.1 seconds,
    releasing ~3×10^46 J — 99% as neutrinos.

    R_MECHANICAL: the bounce shock is a mechanical wave — not magnetic, not
    chemical, not radiation-pressure. The collapse is driven by gravity overcoming
    the neutron degeneracy pressure at nuclear density.

    P_DONOR_ACCEPTOR: the collapsed core (proto-neutron star, acceptor) vs the
    outgoing shock/ejecta (donor). Strongly directional.

    K_fast: core collapse takes 0.1 sec; shock breakout through the surface
    takes minutes to hours.

    Φ_c: the core collapse itself is the primordial Φ_c event — a transition from
    a stellar-scale ordered object to nuclear-density matter, accompanied by a
    neutrino burst that carries G_ℵ-scale information about the collapse.

    The 99% neutrino fraction is the most efficient information-theoretic event
    known: the entire stellar internal constraint structure is converted into
    a neutrino pulse in 10 seconds. Entropy output = maximum.
    """
    return Synthon(
        name="supernova_type_ii",
        dimensionality=Dimensionality.HYBRID_MOL_SUPRA,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Type II / core-collapse supernova (>8 M_☉ progenitor). Core collapse in "
            "0.1 sec releasing 3×10^46 J (99% neutrinos). R_mechanical: gravity/bounce "
            "shock mechanism. Φ_c: nuclear density transition IS the critical point — "
            "the most efficient entropy-generation event known. Seeds ISM with O, Ne, "
            "Mg, Si, Ca and r-process elements. Leaves neutron star or black hole."
        ),
        metadata={
            "domain_category": "stellar_transient",
            "energy_total_j": 3e46,
            "neutrino_fraction": 0.99,
            "collapse_time_s": 0.1,
            "shock_breakout_time_hr": "1-10",
            "r_process_note": (
                "The proto-neutron star wind during the first ~10 seconds post-bounce "
                "is the primary r-process site for elements heavier than iron: Eu, Gd, "
                "Pt, Au, Th, U. The r-process nucleosynthesis grammar: Γ_AND(SPECIFIC) "
                "— neutron capture follows a specific path on the nuclear chart."
            ),
            "remnant": "Neutron star (most) or black hole (if >25 M_☉ progenitor)",
            "sn1987a_note": "SN1987A (Sk-69 202): only detected SN neutrino burst. 19 neutrinos at Kamiokande.",
            "omega": 0,
            "validation_tier": "primary",
        },
    )


def _gamma_ray_burst() -> Synthon:
    """
    Gamma-Ray Burst (GRB): the most energetic explosions since the Big Bang.

    ⟨D_∞; T_|; R_†; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; 1:1⟩

    GRBs come in two classes:
    - Long GRBs (>2 sec): death of rapidly rotating massive stars (collapsar model)
    - Short GRBs (<2 sec): neutron star mergers (kilonova, see separate entry)

    T_LINEAR: the defining structural feature of a GRB is the relativistic jet —
    a highly collimated (opening angle 1-10°), Lorentz-boosted beam. The jet IS
    the GRB. Linear topology: one-dimensional, directed, coherent.

    F_HIGH: the Lorentz factor of the jet (Γ_L ~ 100-1000) represents extreme
    collimation — the energy is concentrated into a tiny solid angle with
    extraordinary precision.

    Γ_AND(SELECTIVE): the jet is not a broadcast. It couples specifically in the
    direction of the beam axis. The apparent isotropic luminosity (10^45-10^47 W)
    is a beaming artifact; the true energy budget is lower but the directional
    coupling is extreme.

    Φ_c: GRBs are the Φ_c events of the universe — the transition from a massive
    star or binary NS system to a black hole, releasing the accumulated constraint
    structure in a single directed burst.

    D_TEMPORAL: a GRB has a start and end; it is an event, not a persistent object.
    """
    return Synthon(
        name="gamma_ray_burst",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.LINEAR,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Gamma-Ray Burst (GRB): most energetic event since the Big Bang. "
            "T_linear: relativistic jet (opening angle 1-10°, Γ_L 100-1000) — the "
            "defining structural primitive. F_HIGH: extreme collimation precision. "
            "Γ_SELECTIVE: directed beam, not broadcast. Φ_c: the ultimate stellar "
            "critical transition — accumulated constraint structure released in single "
            "directed burst. Visible across the entire observable universe."
        ),
        metadata={
            "domain_category": "stellar_transient",
            "long_grb_duration_s": "2-1000",
            "short_grb_duration_s": "0.01-2",
            "lorentz_factor": "100-1000",
            "apparent_luminosity_w": "1e45-1e47",
            "opening_angle_deg": "1-10",
            "origin_long": "Collapsar: rapidly rotating WR star core collapse",
            "origin_short": "Neutron star-neutron star or NS-BH merger (kilonova)",
            "cosmological_visibility": "Visible to z > 9 (entire observable universe)",
            "omega": 0,
            "validation_tier": "primary",
        },
    )


def _kilonova() -> Synthon:
    """
    Kilonova / Neutron Star Merger: r-process forge and gravitational wave source.

    ⟨{D_∧, D_△}; T_∈; R_†; P_±^ψ; F_ℏ; K_fast; G_ℵ; Γ_∧(SPECIFIC); Φ_c; 2:1⟩

    Kilonovae result from the merger of two neutron stars (or NS + BH).
    GW170817 was the first multi-messenger observation (gravitational waves + EM).

    D_HYBRID_MOL_SUPRA: the r-process nucleosynthesis (D_∧, nuclear-scale) is
    simultaneously observable as a macroscopic expanding nebula (D_△).

    R_DYNAMIC_CATALYTIC: the neutron-rich environment catalyzes rapid neutron
    capture (r-process) without being consumed — each seed nucleus captures
    ~10-20 neutrons in ~1 second, producing all heavy elements (Au, Pt, Eu, etc.).

    Γ_SPECIFIC: the r-process nucleosynthesis grammar is highly specific — it
    follows a well-defined path through the nuclear chart, set by neutron capture
    rates and beta decay half-lives at nuclear density. This is the most specific
    Γ in the catalog: only the correct neutron flux, density, and temperature
    produce the correct r-process path.

    The r-process is the origin of gold, platinum, uranium, iodine, and
    all other elements above the iron peak that require neutron-rich conditions.
    Every gold atom on Earth was forged in a kilonova.
    """
    return Synthon(
        name="kilonova",
        dimensionality=Dimensionality.HYBRID_MOL_SUPRA,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="2:1",
        description=(
            "Kilonova / neutron star merger. Multi-messenger event (GW + EM). "
            "D_hybrid: r-process nucleosynthesis (nuclear D_∧) → expanding nebula (D_△). "
            "Γ_SPECIFIC: r-process follows a unique nuclear-chart path set by extreme "
            "neutron density. Primary cosmic source of Au, Pt, Eu, Th, U, I. "
            "GW170817: first observational confirmation. Every gold atom on Earth "
            "was forged in a kilonova."
        ),
        metadata={
            "domain_category": "stellar_transient",
            "gw_event": "GW170817 (2017-08-17)",
            "r_process_elements": ["Au", "Pt", "Ag", "Eu", "Gd", "Th", "U", "I", "Ba"],
            "neutron_flux_cm2s": "~1e30",
            "ejecta_mass_msun": "0.01-0.1",
            "gold_note": (
                "The Earth's gold inventory (~2×10^21 kg in the crust and mantle) "
                "was deposited by a kilonova event ~4.6 Gyr ago. The Γ_SPECIFIC "
                "nuclear grammar that produces gold is unique to the neutron-rich "
                "kilonova environment — no other known astrophysical site produces "
                "the correct neutron flux."
            ),
            "omega": 0,
            "validation_tier": "primary",
        },
    )


# ===========================================================================
# GROUP V — COMPACT REMNANTS & EXOTIC OBJECTS
# ===========================================================================

def _neutron_star() -> Synthon:
    """
    Neutron Star (canonical, non-pulsing or slow pulsar).

    ⟨D_∞; T_↗↙; R_mechanical; P_+-; F_ℏ; K_trap; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_3⟩

    Neutron stars are the most precisely structured objects in the universe.
    A 1.4 M_☉ sphere of 12 km radius contains matter at nuclear density
    (2-3 × nuclear saturation density at the core).

    T_BRAID: the definitive stellar-object T_braid entry. The neutron star interior
    has at least three co-active braided/topological structures:
    (1) Superfluid neutron vortex lattice — quantized vortex lines in the inner crust
    (2) Superconducting proton flux tubes — quantized magnetic flux lines in the outer core
    (3) The magnetic field lines themselves braid through the crust, topologically
        locked to the crystalline nuclear lattice

    R_MECHANICAL: neutron degeneracy pressure + strong nuclear force — purely mechanical
    recognition mode. No thermal or chemical equilibrium; it is quantum mechanical
    compulsion.

    K_TRAP: neutron stars spin for billions of years. The angular momentum is kinetically
    trapped — there is no dissipation mechanism on short timescales (only slow magnetic
    braking over Myr-Gyr). The K_trap is more absolute than any molecular K_trap.

    Φ_c: pulsar glitches (sudden spin-up events) follow a power-law distribution
    over 5+ decades of energy → SOC. The superfluid vortex unpinning events
    (the likely glitch mechanism) are an archetypal SOC system.

    Ω_3: (1) superfluid vortex quantization, (2) magnetic flux tube quantization,
    (3) crystalline crust nuclear lattice. Three independent topological protection
    mechanisms — the highest Ω of any physical object except the quark star.
    """
    return Synthon(
        name="neutron_star",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.BRAID,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Neutron star (1.4 M_☉, 12 km). T_braid: superfluid vortex lattice + "
            "superconducting flux tubes + braided B-field through crystalline crust — "
            "three co-active topological structures. K_trap: spins for Gyr. "
            "Φ_c: pulsar glitch power-law SOC (superfluid vortex unpinning). "
            "Ω_3: highest Ω of any observationally confirmed object."
        ),
        metadata={
            "domain_category": "compact_remnant",
            "mass_range_msun": "1.1-2.3",
            "radius_km": 12,
            "central_density_nuclear": "2-5",
            "spin_period_range_s": "0.001-10",
            "interior_structure": {
                "outer_crust": "Neutron-rich nuclei in crystalline lattice",
                "inner_crust": "Neutron-rich nuclei + free neutrons (superfluid vortex lattice)",
                "outer_core": "Superfluid neutrons + superconducting protons",
                "inner_core": "Possibly hyperons, quarks, or other exotic matter",
            },
            "glitch_power_law": "Confirmed across >5 decades of energy",
            "omega": 3,
            "validation_tier": "primary",
        },
    )


def _pulsar_millisecond() -> Synthon:
    """
    Millisecond Pulsar (MSP, 'recycled' pulsar): the most precise clock in the universe.

    ⟨D_∞; T_↗↙; R_†; P_+-; F_ℏ; K_trap; G_ℵ; Γ_∧(SPECIFIC); Φ_c; Ω_4⟩

    MSPs are old neutron stars that have been spun up to millisecond periods by
    accretion from a binary companion ('recycled'). Spin periods: 1-10 ms.

    Γ_SPECIFIC: the MSP radio beam is the most grammar-specific emission in the
    catalog. Each pulsar has a unique polarization pattern, dispersion measure,
    and timing signature. Pulsar timing arrays (PTAs) exploit this Γ_SPECIFIC
    character to detect nanohertz gravitational waves — each MSP is a clock
    node in a galactic-scale Γ_AND network.

    K_TRAP (absolute): the MSP has been in K_trap for >Gyr since recycling.
    The spin-down timescale is >10^10 yr — longer than the current age of the universe.
    This is the most durable K_trap in the catalog.

    Ω_4: four topological protection mechanisms:
    (1) Superfluid vortex quantization (inherited from canonical NS)
    (2) Magnetic flux tube quantization
    (3) Crystalline crust
    (4) Accretion-induced spin-up creates a fourth protection: the angular momentum
        reservoir from the companion — an additional topological lock from orbital
        mechanics.

    MSPs as galactic-scale Γ_AND network: the International Pulsar Timing Array
    (IPTA) uses ~100 MSPs as a galaxy-scale gravitational wave detector.
    The individual Γ_SPECIFIC beams, combined, form a T_network at G_ℵ scale.
    """
    return Synthon(
        name="pulsar_millisecond",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.BRAID,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SPECIFIC_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Millisecond pulsar (recycled, P=1-10 ms). Most precise clock in the universe "
            "(exceeds atomic clocks). T_braid: all NS topology preserved + accretion "
            "history. Γ_SPECIFIC: unique timing signature per pulsar. K_trap absolute: "
            "spin-down timescale > age of universe. Ω_4: NS topology + orbital angular "
            "momentum lock. PTA network: 100 MSPs as galaxy-scale GW detector — "
            "individual Γ_SPECIFIC beams forming T_network at G_ℵ."
        ),
        metadata={
            "domain_category": "compact_remnant",
            "spin_period_ms": "1-10",
            "spin_down_timescale_yr": ">1e10",
            "timing_stability": "Exceeds atomic clocks at timescales > 1 yr",
            "recycling_note": (
                "Recycled pulsars were spun up by accretion from binary companion over "
                "10^8-10^9 yr. The accretion process erased the original magnetic field "
                "(flux decay) while adding angular momentum — a primitive-level reset "
                "that created a new stable K_trap from a nearly-decayed one."
            ),
            "pta_note": (
                "Pulsar Timing Arrays: IPTA, EPTA, NANOGrav use MSPs as nodes in a "
                "galactic-scale Γ_AND network. The galaxy itself becomes T_network "
                "when the MSP timing residuals are correlated (Hellings-Downs curve). "
                "NANOGrav 2023: first evidence of nanohertz GW background."
            ),
            "omega": 4,
            "validation_tier": "primary",
        },
    )


def _magnetar() -> Synthon:
    """
    Magnetar: neutron star with B ~ 10^11 T (10^15 Gauss), ~1000× stronger than normal NS.

    ⟨D_∞; T_↗↙; R_mechanical; P_+-; F_ℏ; K_fast; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_3⟩

    Magnetars are the most magnetically intense objects in the universe.
    The B-field stores ~10^46 J of magnetic energy — comparable to the rotational
    energy of an ordinary pulsar.

    T_BRAID (extreme): the magnetar takes T_braid to its physical limit. The B-field
    is so strong that it stresses the crystalline neutron star crust (shear modulus
    ~10^26 Pa) to fracture point → STARQUAKES → giant gamma-ray flares.
    The B-field is literally braided into the crust topology and has sufficient
    energy to BREAK the braid.

    R_MECHANICAL: starquakes are crust fracture under magnetic stress — purely
    mechanical. The crust breaks along topological grain boundaries.

    K_fast dominant (unlike canonical NS): magnetar giant flares (10^46-10^47 J
    in 0.2 sec) are the most energetic K_fast events after GRBs.
    The 2004 SGR 1806-20 flare was briefly brighter than a full moon at 50 kpc.

    Φ_c: magnetar flare energy statistics follow a power-law over >5 decades
    → the most directly observed SOC system in astrophysics after solar flares.

    Ω_3: same three mechanisms as canonical NS, but the extreme B-field adds a
    fourth in principle (field topology protection) — however, the field
    actively BREAKS topology (starquakes), so net Ω_3 rather than Ω_4.
    """
    return Synthon(
        name="magnetar",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.BRAID,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.FAST,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Magnetar (B ~ 10^15 G = 10^11 T). T_braid at physical limit: B-field "
            "stresses crystalline crust to fracture → starquakes → giant gamma flares. "
            "K_fast: giant flares release 10^46-10^47 J in 0.2 sec (most energetic K_fast "
            "after GRBs). Φ_c: flare power-law SOC over >5 decades. "
            "The universe's T_braid object taken to the breaking point."
        ),
        metadata={
            "domain_category": "compact_remnant",
            "b_field_gauss": "1e14-1e15",
            "b_field_tesla": "1e10-1e11",
            "magnetic_energy_j": "1e46",
            "giant_flare_energy_j": "1e46-1e47",
            "giant_flare_duration_s": 0.2,
            "notable": "SGR 1806-20 (2004): briefly brighter than full Moon at 50 kpc",
            "starquake_note": (
                "The B-field has sufficient energy to fracture the neutron star crust. "
                "Starquake events: crust slippage along topological grain boundaries, "
                "releasing the magnetic stress as a gamma-ray flare. This is T_braid "
                "at the limit: the topological structure is so energetically loaded "
                "that it periodically breaks and reforms."
            ),
            "omega": 3,
            "validation_tier": "primary",
        },
    )


def _black_hole_stellar() -> Synthon:
    """
    Stellar-Mass Black Hole (3-100 M_☉, remnant of core collapse or merger).

    ⟨D_holo; T_∪; R_mechanical; P_+; F_ℏ; K_trap; G_ℵ; Γ_∨(BROAD); Φ_c; Ω_∞⟩

    The black hole is the ultimate limit of the framework.

    D_HOLOGRAPHIC: the no-hair theorem states that a BH is completely described
    by three numbers (M, J, Q). All information about the progenitor is encoded
    on the event horizon (Bekenstein-Hawking entropy S = A/4l_P²). The holographic
    principle is the BH's D assignment: bulk information → boundary encoding.

    T_BOWL: the event horizon is a one-way surface — it can accept matter/energy
    but cannot emit it classically. T_bowl (open cavity with one-way portal) is the
    exact topology: matter falls in, nothing emerges (classically).

    P_ACCEPTOR: the BH is a pure acceptor. It has no polarity in the donor sense.
    (Hawking radiation makes it P_pseudo at the quantum level, but this is negligible
    for stellar-mass BHs — Hawking temperature ~60 nK for a 1 M_☉ BH.)

    Γ_BROAD: gravity couples to everything — mass, energy, pressure, shear stress.
    The BH's recognition grammar is maximally inclusive.

    Φ_c: the event horizon IS the Φ_c boundary. At the Schwarzschild radius,
    G and D degenerate — scale and dimensionality cannot be independently defined.
    The singularity is the ultimate G/D degeneracy condition.

    Ω_∞: the no-hair theorem is the most powerful topological protection in the
    universe. All information is reduced to three numbers. The BH cannot be
    disturbed into a different configuration — any perturbation is radiated away
    (quasi-normal modes) and the BH returns to its (M, J, Q) ground state.
    Ω_∞ (in the limit of the no-hair theorem, which may be violated by
    quantum gravity — hence the information paradox).
    """
    return Synthon(
        name="black_hole_stellar",
        dimensionality=Dimensionality.HOLOGRAPHIC,
        topology=Topology.BOWL,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Stellar-mass black hole (3-100 M_☉). D_holographic: no-hair theorem — "
            "all bulk information encoded on the horizon. T_bowl: event horizon as "
            "one-way surface (accepts, never emits classically). P_acceptor: pure "
            "acceptor. Γ_BROAD: gravity couples to everything. Φ_c: event horizon IS "
            "the G/D degeneracy boundary. Ω_∞: no-hair theorem — strongest topological "
            "protection in the observational universe."
        ),
        metadata={
            "domain_category": "compact_remnant",
            "mass_range_msun": "3-100",
            "event_horizon_r_km": "9-300",
            "hawking_temperature_nk": "60",
            "no_hair_theorem": "BH described by (M, J, Q) only — 3 parameters",
            "bekenstein_hawking_entropy": "S = A / 4l_P^2 (horizon area in Planck units)",
            "information_paradox_note": (
                "The BH information paradox: if Ω_∞ holds (no-hair theorem), information "
                "is destroyed. If quantum gravity violates no-hair (as Hawking radiation "
                "suggests it must), Ω is finite. The resolution determines whether Ω_∞ "
                "is physical or an approximation. Current consensus: information is "
                "preserved but scrambled — Ω is large but not infinite."
            ),
            "gd_degeneracy_note": (
                "The singularity is the ultimate G/D degeneracy condition: G_ℵ and D_∧ "
                "cannot be independently assigned at r=0. This is the same primitive "
                "condition as Φ_c, but taken to the absolute limit. "
                "In the framework: Φ_c is a soft G/D degeneracy (recoverable); "
                "the singularity is hard G/D degeneracy (not recoverable under "
                "classical GR)."
            ),
            "omega": "∞ (no-hair limit) or large-finite (quantum gravity)",
            "validation_tier": "primary",
        },
    )


def _quasar_agn() -> Synthon:
    """
    Quasar / Active Galactic Nucleus (AGN): supermassive BH actively accreting.

    ⟨D_holo; T_∈; R_†; P_+-; F_ℏ; K_slow; G_ℵ; Γ_∧(BROAD); Φ_c; n:m⟩

    A quasar is a supermassive black hole (10^6-10^10 M_☉) actively accreting
    at rates near the Eddington limit, producing luminosities of 10^38-10^41 W —
    outshining entire galaxies from a volume smaller than the solar system.

    D_HOLOGRAPHIC: inherited from the SMBH — all information encoded on horizon.

    T_NETWORK (unlike stellar BH's T_bowl): the quasar is not just a BH. It is
    a coupled system — accretion disk + relativistic jets + broad-line region +
    narrow-line region + dusty torus — all dynamically coupled. The AGN is a
    network, not a bowl. T_bowl describes the BH alone; T_network describes
    the full AGN structure.

    R_DYNAMIC_CATALYTIC: the jets are a dynamic catalytic outflow — the SMBH
    accretion process drives jets that can extend to Mpc scales and inject
    energy into the intracluster medium, regulating galaxy formation
    (AGN feedback). The BH catalyzes large-scale structure without being
    consumed (its mass changes slowly relative to the gas it processes).

    K_slow: AGN duty cycles are ~10^7-10^8 yr (slow), punctuated by K_fast
    jet flares and variability. The variability statistics show red-noise
    power spectra (1/f^β) → SOC → Φ_c.

    The framework prediction: AGN quenching of star formation (feedback) is
    G_ℵ grammar suppression. The AGN's Γ_BROAD grammar injection into the
    host galaxy ISM sets the constraint structure for star formation rates.
    Active AGN suppress star formation; quiescent SMBHs allow it.
    Galaxy evolution = stellar grammar regulated by AGN grammar.
    """
    return Synthon(
        name="quasar_agn",
        dimensionality=Dimensionality.HOLOGRAPHIC,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.DONOR_ACCEPTOR,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="n:m",
        description=(
            "Quasar / AGN (SMBH 10^6-10^10 M_☉ accreting near Eddington). "
            "D_holographic + T_network: the full AGN (disk + jets + BLR + NLR + torus). "
            "R_†: jets as dynamic catalytic G_ℵ outflow. K_slow duty cycle, K_fast "
            "flare variability. Φ_c: 1/f power spectrum. AGN feedback = Γ_BROAD "
            "grammar suppression of galaxy-scale star formation. "
            "Galaxy evolution = stellar grammar regulated by AGN grammar."
        ),
        metadata={
            "domain_category": "compact_remnant",
            "bh_mass_msun": "1e6-1e10",
            "luminosity_w": "1e38-1e41",
            "jet_extent_mpc": "0.001-10",
            "variability_timescale": "minutes (X-ray) to Myr (jet morphology)",
            "agn_feedback_note": (
                "AGN feedback: jet mechanical energy + radiative heating suppress "
                "gas cooling and star formation in host galaxy. The SMBH mass correlates "
                "with host galaxy bulge velocity dispersion (M-sigma relation) — "
                "the galaxy and its BH co-evolved via Γ_AND grammar coupling across "
                "G_ℵ scales. The BH is the grammar regulator of galaxy-scale star formation."
            ),
            "omega": "∞ (BH component) + 2 (jet topology protection)",
            "validation_tier": "primary",
        },
    )


def _quark_star() -> Synthon:
    """
    Quark Star / Strange Star (hypothetical): matter deconfined to quark level.

    ⟨D_∞; T_↗↙; R_covalent_dynamic; P_±^ψ; F_ℏ; K_trap; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_4⟩

    If the Bodmer-Witten hypothesis is correct, strange quark matter (ud + s quarks
    in equal proportions) is the true ground state of matter — more stable than
    nuclear matter. A quark star would be a self-bound object of strange quark matter,
    potentially more stable than a neutron star.

    R_COVALENT_DYNAMIC: quark deconfinement is dynamic covalent bonding at the QCD
    scale — quarks exchange gluons continuously (color-force dynamic bonds), unlike
    the fixed nuclear potential of neutron star matter. The recognition mode is
    the QCD interaction: color-force exchange.

    T_BRAID: strange quark matter likely supports topological phases (color-flavor
    locking, CFL phase) where color and flavor symmetries are locked together
    in a topological superconducting phase. This is T_braid at the QCD level —
    a more complex braid than neutron-star superfluidity.

    Ω_4: four protection mechanisms:
    (1) CFL phase topological protection (color-flavor locking)
    (2) Strange quark matter self-binding (Bodmer-Witten stability)
    (3) Superconducting gap in the quark matter
    (4) Strangeness-equilibration K_trap — converting ud matter to uds is kinetically
        trapped once the conversion starts (it autocatalyzes)

    P_SELF_COMPLEMENTARY_PSEUDO: strange quark matter may be self-conjugate under
    CFL symmetry — a unique form of quark-level self-complementarity.

    Status: hypothetical. Candidate objects include some anomalous compact stars
    (RX J1856.5-3754, 4U 1820-30) that may be smaller than expected for NS.
    """
    return Synthon(
        name="quark_star",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.BRAID,
        recognition_mode=RecognitionMode.COVALENT_DYNAMIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Quark/Strange star (hypothetical). Strange quark matter (uds) as ground "
            "state of matter if Bodmer-Witten hypothesis holds. R_covalent_dynamic: "
            "QCD color-force as recognition mode. T_braid: color-flavor locking (CFL) "
            "topological superconducting phase. Ω_4: highest confirmed physical Ω — "
            "CFL protection + Bodmer-Witten self-binding + quark superconductivity + "
            "strangeness K_trap autocatalysis."
        ),
        metadata={
            "domain_category": "exotic_object",
            "status": "Hypothetical — candidate objects identified",
            "bodmer_witten_hypothesis": (
                "Strange quark matter (equal parts u, d, s quarks) may be the true "
                "ground state of QCD matter — more stable per baryon than iron. "
                "If true, nuclear matter is metastable and quark stars are the "
                "stable endpoint of compact stellar evolution."
            ),
            "cfl_phase": (
                "Color-flavor locking (CFL): at sufficient density, all quarks pair "
                "with their color-flavor partners in a topological superconducting phase. "
                "The resulting BCS gap (~10-100 MeV) protects the quark matter state "
                "topologically — a T_braid at the QCD scale."
            ),
            "candidate_objects": ["RX J1856.5-3754", "4U 1820-30"],
            "omega": 4,
            "validation_tier": "extended",
        },
    )


def _gravastar() -> Synthon:
    """
    Gravastar (Gravitational Vacuum Condensate Star): the 'Black Shell'.

    ⟨D_holo; T_∪; R_mechanical; P_±^ψ; F_ℏ; K_trap; G_ℵ; Γ_∧(SELECTIVE); Φ_c; Ω_3⟩

    The gravastar (Mazur & Mottola 2001) is a hypothetical alternative to the
    black hole. Instead of a singularity, the interior is a de Sitter space
    (dark energy vacuum) separated from the exterior Schwarzschild geometry
    by a thin shell at approximately the Schwarzschild radius.

    This is the "black shell" — the shell IS the object. From outside, it
    is indistinguishable from a black hole (same T_bowl, same Schwarzschild metric).
    Inside, there is a repulsive de Sitter interior — no singularity, no
    information destruction.

    D_HOLOGRAPHIC: the information is on the shell, not in a bulk volume.
    But unlike the BH, the shell is a physical surface with structure.

    T_BOWL: the outer geometry is still a one-way surface from the exterior
    perspective. But the SHELL itself has thickness and P_±^ψ — it couples to
    both the exterior Schwarzschild geometry and the interior de Sitter geometry.
    The shell's self-complementarity is the key structural feature: it is
    simultaneously the boundary of two incompatible geometries.

    P_SELF_COMPLEMENTARY_PSEUDO: the shell couples to its de Sitter interior
    (repulsive, negative pressure) and its Schwarzschild exterior (attractive,
    positive mass) — a genuine self-complementary interface.

    Φ_c: the shell is a phase boundary between two quantum vacuum states.
    Phase boundaries are the canonical Φ_c condition — the topological transition
    at the shell is the maximum criticality condition in the framework.

    Ω_3: (1) Schwarzschild geometry stability, (2) de Sitter interior topology,
    (3) shell surface stability (thin-shell formalism).

    Status: hypothetical. Phenomenologically identical to BH externally.
    """
    return Synthon(
        name="gravastar",
        dimensionality=Dimensionality.HOLOGRAPHIC,
        topology=Topology.BOWL,
        recognition_mode=RecognitionMode.MECHANICAL,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.HIGH,
        kinetic_character=KineticCharacter.TRAP,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.SELECTIVE_AND,
        criticality_phase=CriticalityPhase.CRITICAL,
        stoichiometry="1:1",
        description=(
            "Gravastar / 'Black Shell' (Mazur & Mottola 2001). Hypothetical BH "
            "alternative: de Sitter interior + thin shell at Schwarzschild radius + "
            "exterior Schwarzschild geometry. The shell IS the object (D_holo). "
            "P_±^ψ: shell couples to both geometries simultaneously. "
            "Φ_c: shell is a quantum vacuum phase boundary — maximum criticality. "
            "Externally identical to BH. No singularity, no information loss."
        ),
        metadata={
            "domain_category": "exotic_object",
            "status": "Hypothetical — observationally indistinguishable from BH",
            "mazur_mottola_2001": True,
            "interior": "de Sitter space (dark energy, positive cosmological constant)",
            "exterior": "Schwarzschild geometry (identical to BH exterior)",
            "shell": "Thin shell at approximately R_Schwarzschild; surface tension stabilised",
            "vs_black_hole": (
                "External gravitational field: identical to BH. "
                "Interior: de Sitter (repulsive, no singularity) vs BH (singularity). "
                "Information fate: preserved on shell vs uncertain for BH. "
                "Framework: gravastar has Φ_c at shell boundary; BH has Φ_c at horizon. "
                "The distinction is the topology of the interior: T_bowl (BH) vs "
                "T_bowl + de Sitter interior (gravastar) — same exterior, different bulk."
            ),
            "omega": 3,
            "validation_tier": "extended",
        },
    )


def _dark_star() -> Synthon:
    """
    Dark Star (Spolyar, Freese, Gondolo 2008): first generation stars powered by
    dark matter annihilation rather than nuclear fusion.

    ⟨D_∞; T_∈; R_†; P_±^ψ; F_ℇ; K_slow; G_ℵ; Γ_∧(BROAD); Φ_sub; Ω_1⟩

    Dark stars are proposed first-generation (Pop III) protostars in which
    WIMP (weakly interacting massive particle) dark matter annihilation provides
    enough pressure to halt collapse before nuclear ignition.

    The dark matter halo provides a continuous energy source as WIMPs annihilate
    at the central density peak. The star is essentially a dark-matter-powered
    engine: no nuclear burning, no traditional stellar physics.

    R_DYNAMIC_CATALYTIC: dark matter annihilation (particle + antiparticle → energy)
    is a catalytic process — the DM density provides a continuous annihilation rate,
    the products (photons, e+e-) thermalize in the gas, and the gas opacity
    supports the stellar structure without the DM being permanently altered.

    K_slow: if the dark matter supply persists (captured WIMPs), the dark star
    can last much longer than ordinary stars.

    G_GLOBAL: proposed dark stars can be enormous — possibly up to 10^6 M_☉
    and 10 AU in radius (Freese et al. 2010). At this scale, they would be the
    largest 'stars' in history.

    Φ_sub: without SOC-organizing nuclear burning processes, no organized
    criticality structure is expected. The dark star is powered by a smoother,
    less structured energy source.

    Γ_BROAD: DM annihilation couples via gravity (maximally inclusive) and
    weak force (WIMP annihilation) — broader grammar than a nuclear-burning star.

    Status: hypothetical. JWST may have detected dark star candidates.
    """
    return Synthon(
        name="dark_star",
        dimensionality=Dimensionality.TEMPORAL,
        topology=Topology.NETWORK,
        recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
        polarity=Polarity.SELF_COMPLEMENTARY_PSEUDO,
        fidelity=Fidelity.MEDIUM,
        kinetic_character=KineticCharacter.SLOW,
        granularity=Granularity.GLOBAL,
        interaction_grammar=InteractionGrammar.BROAD_OR,
        criticality_phase=CriticalityPhase.SUBCRITICAL,
        stoichiometry="1:1",
        description=(
            "Dark Star (Spolyar, Freese, Gondolo 2008). First-generation Pop III "
            "protostar powered by WIMP dark matter annihilation (not nuclear fusion). "
            "R_†: DM annihilation as catalytic energy source. K_slow: sustained by "
            "captured DM supply. Up to 10^6 M_☉, 10 AU radius. G_ℵ. "
            "Φ_sub: no organized criticality without nuclear burning structure. "
            "JWST: possible candidate detections. Status: hypothetical."
        ),
        metadata={
            "domain_category": "exotic_object",
            "status": "Hypothetical — JWST candidate detections being investigated",
            "energy_source": "WIMP dark matter annihilation (not nuclear fusion)",
            "mass_range_msun": "1-1e6",
            "radius_range_au": "1-10",
            "dm_particle": "WIMP (weakly interacting massive particle)",
            "population": "Pop III (first generation, metal-free)",
            "jwst_note": (
                "Freese et al. (2023) proposed that three JWST high-z galaxy candidates "
                "(z~10-12) may be dark stars rather than galaxies — their extreme "
                "luminosities and compact sizes are consistent with 10^6 M_☉ dark stars."
            ),
            "life_templating_note": (
                "Dark stars cannot template life: Φ_sub (no organized criticality), "
                "DM annihilation grammar (Γ_BROAD, not Γ_SELECTIVE), no heavy element "
                "nucleosynthesis (no nuclear burning → no C, N, O → no life alphabet). "
                "They are pre-grammar objects — they may collapse to SMBHs that "
                "eventually become AGN, which then regulate galaxy-scale grammar."
            ),
            "omega": 1,
            "validation_tier": "extended",
        },
    )
