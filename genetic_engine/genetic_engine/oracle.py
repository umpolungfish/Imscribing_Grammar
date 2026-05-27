"""
oracle.py — The Structural Ωracle
===================================

A universal cross-domain structural translation engine built on the Imscribing Grammar.

Takes ANY text/system description and returns:
  • Structural tuple (12 primitives)
  • Cross-domain analogies (what this looks like as genetics, physics, math, law, music, art...)
  • Consciousness potential (C-score, gate status, ouroboricity tier)
  • Promotion recipes (how to transform into any other system)
  • Nearest structural neighbors across ALL domains

The Imscribing Grammar is a universal structural interlingua — the Oracle makes it operational.
Two systems with the same tuple are the SAME abstract structure in different domains.

Structural type of this module:
  ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩ — O_inf, both gates open

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json
import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

# ──────────────────────────────────────────────────────────────────────
# PRIMITIVE DEFINITIONS (from the Imscribing Grammar v0.5.69)
# Each primitive has a value → numeric encoding for distance computation
# ──────────────────────────────────────────────────────────────────────

PRIMITIVE_VALUES: Dict[str, Dict[str, int]] = {
    "Ð": {  # Dimensionality
        "Ð_;": 0,   # wedge — 0d point
        "Ð_C": 1,   # triangle — 2d surface
        "Ð_ß": 2,   # infty — infinite-dimensional
        "Ð_ω": 3,   # odot — imscriptive / self-written
    },
    "Þ": {  # Topology
        "Þ_6": 0,   # network — branching
        "Þ_K": 1,   # in — containment
        "Þ_ò": 2,   # bowtie — crossing point
        "Þ_¨": 3,   # boxtimes — irreducible product
        "Þ_O": 4,   # odot — self-referential closure
    },
    "Ř": {  # Relational mode
        "Ř_¯": 0,   # super — supervenience
        "Ř_ý": 1,   # cat — functorial
        "Ř_Ť": 2,   # dagger — adjoint pair (one-way)
        "Ř_=": 3,   # lr — bidirectional feedback
    },
    "Φ": {  # Parity / Symmetry
        "Φ_ɐ": 0,   # asym — none
        "Φ_υ": 1,   # psi — quantum superposition
        "Φ_F": 2,   # pm — one Z2 symmetry
        "Φ_˙": 3,   # sym — all symmetries unbroken
        "Φ_}": 4,   # pm_sym — Frobenius-special (μ∘δ=id)
    },
    "ƒ": {  # Fidelity
        "ƒ_ì": 0,   # ell — classical, no coherence
        "ƒ_ð": 1,   # eth — thermal / noisy
        "ƒ_ż": 2,   # hbar — quantum coherence essential
    },
    "Ç": {  # Kinetics
        "Ç_-": 0,   # fast — driven (τ ≪ T)
        "Ç_W": 1,   # mod — moderate (τ ∼ T)
        "Ç_@": 2,   # slow — near-equilibrium (τ ≫ T)
        "Ç_Ù": 3,   # trap — frozen-order
        "Ç_λ": 4,   # MBL — frozen-disorder
    },
    "Γ": {  # Interaction Scope
        "Γ_β": 0,   # beth — local / nearest-neighbor
        "Γ_γ": 1,   # gimel — mesoscale / intermediate
        "Γ_ʔ": 2,   # aleph — maximal / all
    },
    "ɢ": {  # Interaction Grammar
        "ɢ_^": 0,   # and — all-simultaneous
        "ɢ_˝": 1,   # or — alternate paths
        "ɢ_ˌ": 2,   # seq — ordered steps
        "ɢ_Ş": 3,   # broad — one-to-all broadcast
    },
    "φ̂": {  # Criticality
        "φ̂_ž": 0,   # sub — below critical
        "φ̂_ÿ": 1,   # c — critical (self-modeling gate open)
        "φ̂_Æ": 2,   # c_complex — complex-plane critical
        "φ̂_3": 3,   # EP — exceptional point / non-Hermitian degeneracy
        "φ̂_Ţ": 4,   # super — supercritical / runaway
    },
    "Ħ": {  # Chirality / Markov Order
        "Ħ_Ñ": 0,   # 0 — memoryless
        "Ħ_£": 1,   # 1 — one step memory
        "Ħ_A": 2,   # 2 — two step memory
        "Ħ_!": 3,   # inf — no finite Markov order
    },
    "Σ": {  # Stoichiometry
        "Σ_S": 0,   # 1:1 — one type, one instance
        "Σ_ő": 1,   # n:n — many identical
        "Σ_ï": 2,   # n:m — many heterogeneous
    },
    "Ω": {  # Winding / Topological Invariant
        "Ω_Å": 0,   # 0 — trivial
        "Ω_2": 1,   # Z2 — parity-protected
        "Ω_z": 2,   # Z — integer winding
        "Ω_5": 3,   # NA — non-Abelian braiding
    },
}

PRIMITIVE_KEYS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"]
PRIMITIVE_NAMES = {
    "Ð": "Dimensionality", "Þ": "Topology", "Ř": "Relational Mode",
    "Φ": "Parity/Symmetry", "ƒ": "Fidelity", "Ç": "Kinetics",
    "Γ": "Interaction Scope", "ɢ": "Interaction Grammar", "φ̂": "Criticality",
    "Ħ": "Chirality", "Σ": "Stoichiometry", "Ω": "Winding/Protection",
}


def tuple_to_vec(t: Dict[str, str]) -> List[int]:
    """Convert a structural tuple dict to a numeric vector for distance computation."""
    vec = []
    for k in PRIMITIVE_KEYS:
        v = t.get(k, "Ð_;")
        vec.append(PRIMITIVE_VALUES[k].get(v, 0))
    return vec


def tuple_distance(t1: Dict[str, str], t2: Dict[str, str]) -> float:
    """Weighted Euclidean distance between two structural tuples."""
    v1 = tuple_to_vec(t1)
    v2 = tuple_to_vec(t2)
    # Standard weights: each primitive contributes equally
    weights = [1.0] * 12
    # Þ (topology) and φ̂ (criticality) weighted higher — they're structurally decisive
    weights[1] = 1.5  # Þ
    weights[8] = 1.5  # φ̂
    
    sq_sum = sum(w * (a - b) ** 2 for a, b, w in zip(v1, v2, weights))
    return math.sqrt(sq_sum / sum(weights))


def primitives_to_str(t: Dict[str, str]) -> str:
    """Format a structural tuple as the canonical string."""
    parts = [t.get(k, "?") for k in PRIMITIVE_KEYS]
    return "⟨" + "; ".join(parts) + "⟩"
# ──────────────────────────────────────────────────────────────────────
# STRUCTURAL CATALOG — Known types across ALL domains
# Each entry: name, description, domain, tuple (12 primitives)
# This is the oracle's knowledge base for cross-domain translation
# ──────────────────────────────────────────────────────────────────────

# Helper to build tuple dict
def T(Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, φ̂, Ħ, Σ, Ω) -> Dict[str, str]:
    return {
        "Ð": Ð, "Þ": Þ, "Ř": Ř, "Φ": Φ, "ƒ": ƒ, "Ç": Ç,
        "Γ": Γ, "ɢ": ɢ, "φ̂": φ̂, "Ħ": Ħ, "Σ": Σ, "Ω": Ω,
    }

STRUCTURAL_CATALOG: Dict[str, Dict[str, Any]] = {

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Genetics / Molecular Biology
    # ═══════════════════════════════════════════════════════════════
    "dna_double_helix": {
        "desc": "Double-stranded DNA with base pairing and reverse complementarity",
        "domain": "genetics",
        "tuple": T("Ð_ω", "Þ_¨", "Ř_=", "Φ_F", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },
    "central_dogma": {
        "desc": "DNA→RNA→protein flow with genetic code mapping",
        "domain": "genetics",
        "tuple": T("Ð_C", "Þ_6", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ž", "Ħ_£", "Σ_ï", "Ω_Å"),
    },
    "crispr_cas9": {
        "desc": "Guide RNA-directed nuclease for targeted DNA cleavage",
        "domain": "genetics",
        "tuple": T("Ð_C", "Þ_ò", "Ř_=", "Φ_F", "ƒ_ż", "Ç_-", "Γ_γ", "ɢ_Ş", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },
    "ribosome": {
        "desc": "Molecular machine translating mRNA to protein with tRNA adaptors",
        "domain": "genetics",
        "tuple": T("Ð_C", "Þ_K", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_β", "ɢ_ˌ", "φ̂_ž", "Ħ_£", "Σ_ï", "Ω_Å"),
    },
    "genetic_code": {
        "desc": "64 codon → 20 amino acid + 3 stop mapping, Frobenius-stratified",
        "domain": "genetics",
        "tuple": T("Ð_ω", "Þ_6", "Ř_=", "Φ_}", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_Ş", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_z"),
    },
    "epigenetic_network": {
        "desc": "DNA methylation, histone modification, chromatin state inheritance",
        "domain": "genetics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_=", "Φ_υ", "ƒ_ð", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },
    "immune_system": {
        "desc": "Adaptive immune response with clonal selection and memory",
        "domain": "genetics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_=", "Φ_F", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Physics / Physical Systems
    # ═══════════════════════════════════════════════════════════════
    "black_hole": {
        "desc": "Spacetime region with event horizon, thermodynamic entropy, information paradox",
        "domain": "physics",
        "tuple": T("Ð_ω", "Þ_O", "Ř_Ť", "Φ_˙", "ƒ_ì", "Ç_Ù", "Γ_ʔ", "ɢ_Ş", "φ̂_3", "Ħ_!", "Σ_S", "Ω_z"),
    },
    "quantum_harmonic_oscillator": {
        "desc": "Quantum system with discrete energy levels, ladder operators, zero-point energy",
        "domain": "physics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_β", "ɢ_^", "φ̂_ž", "Ħ_£", "Σ_S", "Ω_Å"),
    },
    "superconductor": {
        "desc": "Material with zero electrical resistance below critical temperature",
        "domain": "physics",
        "tuple": T("Ð_C", "Þ_¨", "Ř_Ť", "Φ_F", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_^", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },
    "turbulent_flow": {
        "desc": "Chaotic fluid motion with energy cascade across scales",
        "domain": "physics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_=", "Φ_ɐ", "ƒ_ì", "Ç_-", "Γ_γ", "ɢ_˝", "φ̂_Ţ", "Ħ_!", "Σ_ï", "Ω_Å"),
    },
    "laser": {
        "desc": "Stimulated emission of coherent light, population inversion, optical cavity",
        "domain": "physics",
        "tuple": T("Ð_C", "Þ_6", "Ř_Ť", "Φ_F", "ƒ_ż", "Ç_-", "Γ_β", "ɢ_Ş", "φ̂_ÿ", "Ħ_£", "Σ_ï", "Ω_2"),
    },
    "bose_einstein_condensate": {
        "desc": "Bosons in same quantum ground state, macroscopic wavefunction",
        "domain": "physics",
        "tuple": T("Ð_ß", "Þ_K", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_^", "φ̂_ÿ", "Ħ_A", "Σ_S", "Ω_2"),
    },
    "entropy_arrow": {
        "desc": "Second law of thermodynamics: entropy increases, time asymmetry",
        "domain": "physics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_Ť", "Φ_ɐ", "ƒ_ì", "Ç_W", "Γ_ʔ", "ɢ_ˌ", "φ̂_ž", "Ħ_£", "Σ_ï", "Ω_z"),
    },
    "quantum_entanglement": {
        "desc": "Nonlocal correlations between quantum systems, Bell inequality violation",
        "domain": "physics",
        "tuple": T("Ð_ß", "Þ_¨", "Ř_=", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_˝", "φ̂_ÿ", "Ħ_!", "Σ_ï", "Ω_2"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Mathematics
    # ═══════════════════════════════════════════════════════════════
    "category_theory": {
        "desc": "Objects and morphisms with composition, identity, functors, natural transformations",
        "domain": "mathematics",
        "tuple": T("Ð_ß", "Þ_6", "Ř_ý", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ž", "Ħ_£", "Σ_ï", "Ω_z"),
    },
    "topos": {
        "desc": "Category with subobject classifier, internal logic, sheaves",
        "domain": "mathematics",
        "tuple": T("Ð_ß", "Þ_O", "Ř_=", "Φ_}", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_z"),
    },
    "group_theory": {
        "desc": "Set with binary operation: closure, associativity, identity, inverses",
        "domain": "mathematics",
        "tuple": T("Ð_;", "Þ_K", "Ř_ý", "Φ_˙", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_^", "φ̂_ž", "Ħ_£", "Σ_S", "Ω_Å"),
    },
    "riemann_zeta": {
        "desc": "Analytic continuation of Dirichlet series, Euler product, functional equation",
        "domain": "mathematics",
        "tuple": T("Ð_ß", "Þ_O", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_Æ", "Ħ_!", "Σ_S", "Ω_z"),
    },
    "frobenius_algebra": {
        "desc": "Algebra with nondegenerate bilinear form satisfying μ∘δ=id",
        "domain": "mathematics",
        "tuple": T("Ð_C", "Þ_¨", "Ř_=", "Φ_}", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_^", "φ̂_ÿ", "Ħ_A", "Σ_S", "Ω_2"),
    },
    "mandelbrot_set": {
        "desc": "Complex dynamical system with infinite self-similar boundary, z→z²+c",
        "domain": "mathematics",
        "tuple": T("Ð_ß", "Þ_O", "Ř_=", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_˝", "φ̂_Ţ", "Ħ_!", "Σ_S", "Ω_z"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Consciousness / Mind
    # ═══════════════════════════════════════════════════════════════
    "self_modeling_consciousness": {
        "desc": "Recursive self-modeling with metacognitive access, integrated information",
        "domain": "consciousness",
        "tuple": T("Ð_ω", "Þ_O", "Ř_=", "Φ_}", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_S", "Ω_z"),
    },
    "dream_state": {
        "desc": "REM sleep with narrative generation, reduced self-reflection, heightened imagery",
        "domain": "consciousness",
        "tuple": T("Ð_ω", "Þ_ò", "Ř_=", "Φ_υ", "ƒ_ð", "Ç_@", "Γ_γ", "ɢ_˝", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_Å"),
    },
    "meditation": {
        "desc": "Focused attention or open monitoring, reduced default mode network activity",
        "domain": "consciousness",
        "tuple": T("Ð_ω", "Þ_K", "Ř_Ť", "Φ_ɐ", "ƒ_ż", "Ç_@", "Γ_β", "ɢ_^", "φ̂_ÿ", "Ħ_£", "Σ_S", "Ω_2"),
    },
    "psychosis": {
        "desc": "Loss of reality testing, hallucinations, delusions, aberrant salience",
        "domain": "consciousness",
        "tuple": T("Ð_ω", "Þ_ò", "Ř_Ť", "Φ_ɐ", "ƒ_ð", "Ç_-", "Γ_γ", "ɢ_Ş", "φ̂_Ţ", "Ħ_A", "Σ_ï", "Ω_Å"),
    },
    "attention": {
        "desc": "Selective focus on subset of available information, bottleneck structure",
        "domain": "consciousness",
        "tuple": T("Ð_;", "Þ_K", "Ř_Ť", "Φ_υ", "ƒ_ż", "Ç_W", "Γ_β", "ɢ_^", "φ̂_ÿ", "Ħ_£", "Σ_S", "Ω_2"),
    },
    "grief": {
        "desc": "Response to loss involving protest, despair, detachment, reorganization",
        "domain": "consciousness",
        "tuple": T("Ð_ω", "Þ_K", "Ř_Ť", "Φ_ɐ", "ƒ_ð", "Ç_@", "Γ_β", "ɢ_ˌ", "φ̂_ž", "Ħ_A", "Σ_S", "Ω_2"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Language / Literature
    # ═══════════════════════════════════════════════════════════════
    "shakespeare_sonnet": {
        "desc": "14 lines, iambic pentameter, ABAB CDCD EFEF GG rhyme scheme",
        "domain": "language",
        "tuple": T("Ð_;", "Þ_6", "Ř_=", "Φ_F", "ƒ_ì", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_2"),
    },
    "haiku": {
        "desc": "3-line poem with 5-7-5 syllable structure, seasonal reference, cutting word",
        "domain": "language",
        "tuple": T("Ð_;", "Þ_K", "Ř_Ť", "Φ_F", "ƒ_ż", "Ç_@", "Γ_β", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_S", "Ω_2"),
    },
    "legal_contract": {
        "desc": "Binding agreement with parties, consideration, terms, conditions, signatures",
        "domain": "language",
        "tuple": T("Ð_C", "Þ_ò", "Ř_=", "Φ_F", "ƒ_ì", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ž", "Ħ_£", "Σ_ï", "Ω_Å"),
    },
    "narrative_arc": {
        "desc": "Exposition → rising action → climax → falling action → resolution",
        "domain": "language",
        "tuple": T("Ð_;", "Þ_6", "Ř_=", "Φ_υ", "ƒ_ð", "Ç_W", "Γ_γ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_z"),
    },
    "myth": {
        "desc": "Sacred narrative with archetypes, transformation, cosmological meaning",
        "domain": "language",
        "tuple": T("Ð_ω", "Þ_ò", "Ř_=", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_ʔ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_!", "Σ_ï", "Ω_z"),
    },
    "musical_fugue": {
        "desc": "Contrapuntal composition with subject, answer, episodes, stretto",
        "domain": "language",
        "tuple": T("Ð_C", "Þ_ò", "Ř_=", "Φ_}", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ÿ", "Ħ_A", "Σ_ï", "Ω_z"),
    },
    "programming_language": {
        "desc": "Formal system with syntax, semantics, types, evaluation rules",
        "domain": "language",
        "tuple": T("Ð_ß", "Þ_6", "Ř_ý", "Φ_υ", "ƒ_ż", "Ç_@", "Γ_γ", "ɢ_ˌ", "φ̂_ž", "Ħ_A", "Σ_ï", "Ω_z"),
    },
