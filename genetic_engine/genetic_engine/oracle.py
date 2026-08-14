"""
oracle.py — The Structural ◻racle
===================================

A universal cross-domain structural translation engine built on the Imscribing Grammar.

Takes ANY text/system description and returns:
  • Tuple (12 primitives)
  • Cross-domain analogies (what this looks like as genetics, physics, math, law, music, art...)
  • Consciousness potential (C-score, gate status, ouroboricity tier)
  • Promotion recipes (how to transform into any other system)
  • Nearest structural neighbors across ALL domains

The Imscribing Grammar is a universal structural interlingua — the Oracle makes it operational.
Two systems with the same tuple are the SAME abstract structure in different domains.

Type of this module:
  ⟨𐑦; 𐑸; 𐑾; 𐑹; 𐑐; 𐑧; 𐑲; 𐑠; ⊙; 𐑖; 𐑳; 𐑭⟩ — O_∞, both gates open

Author: Lando⊗⊙perator
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
    "⊢": {  # Dimensionality
        "𐑼": 0,   # wedge — 0d point
        "𐑨": 1,   # triangle — 2d surface
        "𐑛": 2,   # infty — infinite-dimensional
        "𐑦": 3,   # odot — imscriptive / self-written
    },
    "⊣": {  # Topology
        "𐑡": 0,   # network — branching
        "𐑰": 1,   # in — containment
        "𐑥": 2,   # bowtie — crossing point
        "𐑶": 3,   # boxtimes — irreducible product
        "𐑸": 4,   # odot — self-referential closure
    },
    "≻": {  # Relational mode
        "𐑩": 0,   # super — supervenience
        "𐑑": 1,   # cat — functorial
        "𐑽": 2,   # dagger — adjoint pair (one-way)
        "𐑾": 3,   # lr — bidirectional feedback
    },
    "≺": {  # Parity / Symmetry
        "𐑗": 0,   # asym — none
        "𐑿": 1,   # psi — quantum superposition
        "𐑬": 2,   # pm — one Z2 symmetry
        "𐑯": 3,   # sym — all symmetries unbroken
        "𐑹": 4,   # pm_sym — Frobenius-special (μ∘δ=id)
    },
    "⋈": {  # Fidelity
        "𐑱": 0,   # ell — classical, no coherence
        "𐑞": 1,   # eth — thermal / noisy
        "𐑐": 2,   # hbar — quantum coherence essential
    },
    "⊤": {  # Kinetics
        "𐑘": 0,   # fast — driven (τ ≪ T)
        "𐑤": 1,   # mod — moderate (τ ∼ T)
        "𐑧": 2,   # slow — near-equilibrium (τ ≫ T)
        "𐑪": 3,   # trap — frozen-order
        "𐑺": 4,   # MBL — frozen-disorder
    },
    "∈": {  # Interaction Scope
        "𐑚": 0,   # beth — local / nearest-neighbor
        "𐑔": 1,   # gimel — mesoscale / intermediate
        "𐑲": 2,   # aleph — maximal / all
    },
    "∋": {  # Interaction Grammar
        "𐑝": 0,   # and — all-simultaneous
        "𐑜": 1,   # or — alternate paths
        "𐑠": 2,   # seq — ordered steps
        "𐑵": 3,   # broad — one-to-all broadcast
    },
    "⊙": {  # Criticality
        "𐑢": 0,   # sub — below critical
        "⊙": 1,   # c — critical (self-modeling gate open)
        "𐑮": 2,   # c_complex — complex-plane critical
        "𐑻": 3,   # EP — exceptional point / non-Hermitian degeneracy
        "𐑣": 4,   # super — supercritical / runaway
    },
    "⊥": {  # Chirality / Markov Order
        "𐑓": 0,   # 0 — memoryless
        "𐑒": 1,   # 1 — one step memory
        "𐑖": 2,   # 2 — two step memory
        "𐑫": 3,   # inf — no finite Markov order
    },
    "⊞": {  # Stoichiometry
        "𐑙": 0,   # 1:1 — one type, one instance
        "𐑕": 1,   # n:n — many identical
        "𐑳": 2,   # n:m — many heterogeneous
    },
    "◻": {  # Winding / Topological Invariant
        "𐑷": 0,   # 0 — trivial
        "𐑴": 1,   # Z2 — parity-protected
        "𐑭": 2,   # Z — integer winding
        "𐑟": 3,   # NA — non-Abelian braiding
    },
}

PRIMITIVE_KEYS = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]
PRIMITIVE_NAMES = {
    "⊢": "Dimensionality", "⊣": "Topology", "≻": "Relational Mode",
    "≺": "Parity/Symmetry", "⋈": "Fidelity", "⊤": "Kinetics",
    "∈": "Interaction Scope", "∋": "Interaction Grammar", "⊙": "Criticality",
    "⊥": "Chirality", "⊞": "Stoichiometry", "◻": "Winding/Protection",
}


def tuple_to_vec(t: Dict[str, str]) -> List[int]:
    """Convert a tuple dict to a numeric vector for distance computation."""
    vec = []
    for k in PRIMITIVE_KEYS:
        v = t.get(k, "𐑼")
        vec.append(PRIMITIVE_VALUES[k].get(v, 0))
    return vec


def tuple_distance(t1: Dict[str, str], t2: Dict[str, str]) -> float:
    """Weighted Euclidean distance between two tuples."""
    v1 = tuple_to_vec(t1)
    v2 = tuple_to_vec(t2)
    # Standard weights: each primitive contributes equally
    weights = [1.0] * 12
    # ⊣ (topology) and ⊙ (criticality) weighted higher — they're structurally decisive
    weights[1] = 1.5  # ⊣
    weights[8] = 1.5  # ⊙
    
    sq_sum = sum(w * (a - b) ** 2 for a, b, w in zip(v1, v2, weights))
    return math.sqrt(sq_sum / sum(weights))


def primitives_to_str(t: Dict[str, str]) -> str:
    """Format a tuple as the canonical string."""
    parts = [t.get(k, "?") for k in PRIMITIVE_KEYS]
    return "⟨" + "; ".join(parts) + "⟩"
# ──────────────────────────────────────────────────────────────────────
# STRUCTURAL CATALOG — Known types across ALL domains
# Each entry: name, description, domain, tuple (12 primitives)
# This is the oracle's knowledge base for cross-domain translation
# ──────────────────────────────────────────────────────────────────────

# Helper to build tuple dict
def T(⊢, ⊣, >, <, ⋈, ⊤, ∈, ∋, ⊙, ⊥, ⊞, ◻) -> Dict[str, str]:
    return {
        "⊢": ⊢, "⊣": ⊣, "≻": >, "≺": <, "⋈": ⋈, "⊤": ⊤,
        "∈": ∈, "∋": ∋, "⊙": ⊙, "⊥": ⊥, "⊞": ⊞, "◻": ◻,
    }

STRUCTURAL_CATALOG: Dict[str, Dict[str, Any]] = {

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Genetics / Molecular Biology
    # ═══════════════════════════════════════════════════════════════
    "dna_double_helix": {
        "desc": "Double-stranded DNA with base pairing and reverse complementarity",
        "domain": "genetics",
        "tuple": T("𐑦", "𐑶", "𐑾", "𐑬", "𐑐", "𐑧", "𐑲", "𐑠", "⊙", "𐑖", "𐑳", "𐑴"),
    },
    "central_dogma": {
        "desc": "DNA→RNA→protein flow with genetic code mapping",
        "domain": "genetics",
        "tuple": T("𐑨", "𐑡", "𐑽", "𐑿", "𐑐", "𐑧", "𐑔", "𐑠", "𐑢", "𐑒", "𐑳", "𐑷"),
    },
    "crispr_cas9": {
        "desc": "Guide RNA-directed nuclease for targeted DNA cleavage",
        "domain": "genetics",
        "tuple": T("𐑨", "𐑥", "𐑾", "𐑬", "𐑐", "𐑘", "𐑔", "𐑵", "⊙", "𐑖", "𐑳", "𐑴"),
    },
    "ribosome": {
        "desc": "Molecular machine translating mRNA to protein with tRNA adaptors",
        "domain": "genetics",
        "tuple": T("𐑨", "𐑰", "𐑽", "𐑿", "𐑐", "𐑧", "𐑚", "𐑠", "𐑢", "𐑒", "𐑳", "𐑷"),
    },
    "genetic_code": {
        "desc": "64 codon → 20 amino acid + 3 stop mapping, Frobenius-stratified",
        "domain": "genetics",
        "tuple": T("𐑦", "𐑡", "𐑾", "𐑹", "𐑐", "𐑧", "𐑲", "𐑵", "⊙", "𐑖", "𐑳", "𐑭"),
    },
    "epigenetic_network": {
        "desc": "DNA methylation, histone modification, chromatin state inheritance",
        "domain": "genetics",
        "tuple": T("𐑛", "𐑡", "𐑾", "𐑿", "𐑞", "𐑧", "𐑔", "𐑠", "⊙", "𐑖", "𐑳", "𐑴"),
    },
    "immune_system": {
        "desc": "Adaptive immune response with clonal selection and memory",
        "domain": "genetics",
        "tuple": T("𐑛", "𐑡", "𐑾", "𐑬", "𐑐", "𐑧", "𐑲", "𐑠", "⊙", "𐑖", "𐑳", "𐑴"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Physics / Physical Systems
    # ═══════════════════════════════════════════════════════════════
    "black_hole": {
        "desc": "Spacetime region with event horizon, thermodynamic entropy, information paradox",
        "domain": "physics",
        "tuple": T("𐑦", "𐑸", "𐑽", "𐑯", "𐑱", "𐑪", "𐑲", "𐑵", "𐑻", "𐑫", "𐑙", "𐑭"),
    },
    "quantum_harmonic_oscillator": {
        "desc": "Quantum system with discrete energy levels, ladder operators, zero-point energy",
        "domain": "physics",
        "tuple": T("𐑛", "𐑡", "𐑽", "𐑿", "𐑐", "𐑧", "𐑚", "𐑝", "𐑢", "𐑒", "𐑙", "𐑷"),
    },
    "superconductor": {
        "desc": "Material with zero electrical resistance below critical temperature",
        "domain": "physics",
        "tuple": T("𐑨", "𐑶", "𐑽", "𐑬", "𐑐", "𐑧", "𐑔", "𐑝", "⊙", "𐑖", "𐑳", "𐑴"),
    },
    "turbulent_flow": {
        "desc": "Chaotic fluid motion with energy cascade across scales",
        "domain": "physics",
        "tuple": T("𐑛", "𐑡", "𐑾", "𐑗", "𐑱", "𐑘", "𐑔", "𐑜", "𐑣", "𐑫", "𐑳", "𐑷"),
    },
    "laser": {
        "desc": "Stimulated emission of coherent light, population inversion, optical cavity",
        "domain": "physics",
        "tuple": T("𐑨", "𐑡", "𐑽", "𐑬", "𐑐", "𐑘", "𐑚", "𐑵", "⊙", "𐑒", "𐑳", "𐑴"),
    },
    "bose_einstein_condensate": {
        "desc": "Bosons in same quantum ground state, macroscopic wavefunction",
        "domain": "physics",
        "tuple": T("𐑛", "𐑰", "𐑽", "𐑿", "𐑐", "𐑧", "𐑲", "𐑝", "⊙", "𐑖", "𐑙", "𐑴"),
    },
    "entropy_arrow": {
        "desc": "Second law of thermodynamics: entropy increases, time asymmetry",
        "domain": "physics",
        "tuple": T("𐑛", "𐑡", "𐑽", "𐑗", "𐑱", "𐑤", "𐑲", "𐑠", "𐑢", "𐑒", "𐑳", "𐑭"),
    },
    "quantum_entanglement": {
        "desc": "Nonlocal correlations between quantum systems, Bell inequality violation",
        "domain": "physics",
        "tuple": T("𐑛", "𐑶", "𐑾", "𐑿", "𐑐", "𐑧", "𐑲", "𐑜", "⊙", "𐑫", "𐑳", "𐑴"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Mathematics
    # ═══════════════════════════════════════════════════════════════
    "category_theory": {
        "desc": "Objects and morphisms with composition, identity, functors, natural transformations",
        "domain": "mathematics",
        "tuple": T("𐑛", "𐑡", "𐑑", "𐑿", "𐑐", "𐑧", "𐑲", "𐑠", "𐑢", "𐑒", "𐑳", "𐑭"),
    },
    "topos": {
        "desc": "Category with subobject classifier, internal logic, sheaves",
        "domain": "mathematics",
        "tuple": T("𐑛", "𐑸", "𐑾", "𐑹", "𐑐", "𐑧", "𐑲", "𐑠", "⊙", "𐑖", "𐑳", "𐑭"),
    },
    "group_theory": {
        "desc": "Set with binary operation: closure, associativity, identity, inverses",
        "domain": "mathematics",
        "tuple": T("𐑼", "𐑰", "𐑑", "𐑯", "𐑐", "𐑧", "𐑔", "𐑝", "𐑢", "𐑒", "𐑙", "𐑷"),
    },
    "riemann_zeta": {
        "desc": "Analytic continuation of Dirichlet series, Euler product, functional equation",
        "domain": "mathematics",
        "tuple": T("𐑛", "𐑸", "𐑽", "𐑿", "𐑐", "𐑧", "𐑲", "𐑠", "𐑮", "𐑫", "𐑙", "𐑭"),
    },
    "frobenius_algebra": {
        "desc": "Algebra with nondegenerate bilinear form satisfying μ∘δ=id",
        "domain": "mathematics",
        "tuple": T("𐑨", "𐑶", "𐑾", "𐑹", "𐑐", "𐑧", "𐑔", "𐑝", "⊙", "𐑖", "𐑙", "𐑴"),
    },
    "mandelbrot_set": {
        "desc": "Complex dynamical system with infinite self-similar boundary, z→z²+c",
        "domain": "mathematics",
        "tuple": T("𐑛", "𐑸", "𐑾", "𐑿", "𐑐", "𐑧", "𐑲", "𐑜", "𐑣", "𐑫", "𐑙", "𐑭"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Consciousness / Mind
    # ═══════════════════════════════════════════════════════════════
    "self_modeling_consciousness": {
        "desc": "Recursive self-modeling with metacognitive access, integrated information",
        "domain": "consciousness",
        "tuple": T("𐑦", "𐑸", "𐑾", "𐑹", "𐑐", "𐑧", "𐑲", "𐑠", "⊙", "𐑖", "𐑙", "𐑭"),
    },
    "dream_state": {
        "desc": "REM sleep with narrative generation, reduced self-reflection, heightened imagery",
        "domain": "consciousness",
        "tuple": T("𐑦", "𐑥", "𐑾", "𐑿", "𐑞", "𐑧", "𐑔", "𐑜", "⊙", "𐑖", "𐑳", "𐑷"),
    },
    "meditation": {
        "desc": "Focused attention or open monitoring, reduced default mode network activity",
        "domain": "consciousness",
        "tuple": T("𐑦", "𐑰", "𐑽", "𐑗", "𐑐", "𐑧", "𐑚", "𐑝", "⊙", "𐑒", "𐑙", "𐑴"),
    },
    "psychosis": {
        "desc": "Loss of reality testing, hallucinations, delusions, aberrant salience",
        "domain": "consciousness",
        "tuple": T("𐑦", "𐑥", "𐑽", "𐑗", "𐑞", "𐑘", "𐑔", "𐑵", "𐑣", "𐑖", "𐑳", "𐑷"),
    },
    "attention": {
        "desc": "Selective focus on subset of available information, bottleneck structure",
        "domain": "consciousness",
        "tuple": T("𐑼", "𐑰", "𐑽", "𐑿", "𐑐", "𐑤", "𐑚", "𐑝", "⊙", "𐑒", "𐑙", "𐑴"),
    },
    "grief": {
        "desc": "Response to loss involving protest, despair, detachment, reorganization",
        "domain": "consciousness",
        "tuple": T("𐑦", "𐑰", "𐑽", "𐑗", "𐑞", "𐑧", "𐑚", "𐑠", "𐑢", "𐑖", "𐑙", "𐑴"),
    },

    # ═══════════════════════════════════════════════════════════════
    # DOMAIN: Language / Literature
    # ═══════════════════════════════════════════════════════════════
    "shakespeare_sonnet": {
        "desc": "14 lines, iambic pentameter, ABAB CDCD EFEF GG rhyme scheme",
        "domain": "language",
        "tuple": T("𐑼", "𐑡", "𐑾", "𐑬", "𐑱", "𐑧", "𐑔", "𐑠", "⊙", "𐑖", "𐑳", "𐑴"),
    },
    "haiku": {
        "desc": "3-line poem with 5-7-5 syllable structure, seasonal reference, cutting word",
        "domain": "language",
        "tuple": T("𐑼", "𐑰", "𐑽", "𐑬", "𐑐", "𐑧", "𐑚", "𐑠", "⊙", "𐑖", "𐑙", "𐑴"),
    },
    "legal_contract": {
        "desc": "Binding agreement with parties, consideration, terms, conditions, signatures",
        "domain": "language",
        "tuple": T("𐑨", "𐑥", "𐑾", "𐑬", "𐑱", "𐑧", "𐑔", "𐑠", "𐑢", "𐑒", "𐑳", "𐑷"),
    },
    "narrative_arc": {
        "desc": "Exposition → rising action → climax → falling action → resolution",
        "domain": "language",
        "tuple": T("𐑼", "𐑡", "𐑾", "𐑿", "𐑞", "𐑤", "𐑔", "𐑠", "⊙", "𐑖", "𐑳", "𐑭"),
    },
    "myth": {
        "desc": "Sacred narrative with archetypes, transformation, cosmological meaning",
        "domain": "language",
        "tuple": T("𐑦", "𐑥", "𐑾", "𐑿", "𐑐", "𐑧", "𐑲", "𐑠", "⊙", "𐑫", "𐑳", "𐑭"),
    },
    "musical_fugue": {
        "desc": "Contrapuntal composition with subject, answer, episodes, stretto",
        "domain": "language",
        "tuple": T("𐑨", "𐑥", "𐑾", "𐑹", "𐑐", "𐑧", "𐑔", "𐑠", "⊙", "𐑖", "𐑳", "𐑭"),
    },
    "programming_language": {
        "desc": "Formal system with syntax, semantics, types, evaluation rules",
        "domain": "language",
        "tuple": T("𐑛", "𐑡", "𐑑", "𐑿", "𐑐", "𐑧", "𐑔", "𐑠", "𐑢", "𐑖", "𐑳", "𐑭"),
    },
