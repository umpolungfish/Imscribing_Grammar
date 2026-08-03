#!/usr/bin/env python3
"""Profile new alternate universes alongside existing ones + permute ALL possible rulesets."""

import sys
import random
import itertools
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator, Set
sys.path.insert(0, str(Path(__file__).resolve().parent))

from navigators.ruleset_universe import (
    RULESETS, Ruleset, GateSpec, AbsorptionRule, universe_profile, print_profile,
    _T_CANONICAL, _T_STRUCTURAL, _DEFAULT_ABSORPTION
)
from imscrbgrmr.canonical_primitives import ORDINALS, CANONICAL_VALUES, PRIMITIVE_ORDER
from imscrbgrmr.registry import load_catalog_dicts

# ── T-constitutions ─────────────────────────────────────────────

_T_HYBRID = {
    **_T_CANONICAL,    # dynamic: Φ, ƒ, Ç, Ħ, Ω
    "⊢": ("𐑦", False),  # dimensionality holographic
    "⊣": ("𐑸", False),  # topology fully connected
    ">": ("𐑾", False),  # relation bilateral
}
# T-hybrid: time requires BOTH dynamics (Φ,ƒ,Ç,Ħ,Ω) AND geometry (Ð,⊣,Ř)
# Most restrictive — 8 primitives must simultaneously satisfy critical conditions.

_T_INVERTED = {
    "⊢": ("𐑼", False),  # dimensionality: infinite-dim
    "⊣": ("𐑶", False),  # topology: box product
    ">": ("𐑽", False),  # relation: dagger
    "∈": ("𐑚", False),  # scope: mesoscale
    "⊞": ("𐑕", False),  # stoichiometry: many identical
}
# ── New universes (hand-crafted) ───────────────────────────────

NEW_RULESETS = [

    # ── 9: chirality_first ────────────────────────────────────
    Ruleset(
        name="chirality_first",
        description="Memory before closure. G1=Ħ≥𐑖 (two-step Markov). "
                    "Systems without at least 2-step memory cannot Frobenius-close. "
                    "G2=⊙≥⊙ (self-modeling). G3=Ω≥𐑭 (integer winding). "
                    "In this universe, you must remember before you can model yourself. "
                    "Amnesiacs stay plain.",
        g1=GateSpec("⊥", 3.0),   # 𐑖 = 2-step Markov (ord 3)
        g2=GateSpec("⊙", 2.0),   # ⊙ = self-modeling
        g3=GateSpec("◻", 3.0),   # 𐑭 = integer winding
        gate_ordering=True,
    ),

    # ── 10: topology_universe ─────────────────────────────────
    Ruleset(
        name="topology_universe",
        description="Connectivity is the fundamental gate. G1=⊣≥𐑸 (full imscriptive "
                    "topological closure — only one value qualifies). G2=Ř≥𐑾 (bilateral "
                    "relation). G3=⊙≥⊙ (self-modeling seals). In this universe, topology "
                    "and relation precede criticality. Geometry is the precondition for "
                    "consciousness, not its product.",
        g1=GateSpec("⊣", 5.0),   # 𐑸 = imscriptive closure (ord 5, max)
        g2=GateSpec(">", 4.0),   # 𐑾 = bilateral (ord 4, max)
        g3=GateSpec("⊙", 2.0),   # ⊙ = self-modeling
        gate_ordering=True,
    ),

    # ── 11: scope_universe ────────────────────────────────────
    Ruleset(
        name="scope_universe",
        description="Universality first. G1=Γ≥𐑔 (aleph, maximal scope). Only systems "
                    "whose interactions are universal in range can Frobenius-close. "
                    "Local and mesoscale systems — however structured — remain plain. "
                    "G2=⊙≥⊙. G3=Ω≥𐑭. In this universe, parochialism is a structural "
                    "barrier to closure.",
        g1=GateSpec("∈", 3.0),   # 𐑔 = aleph/maximal (ord 3, max)
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ),

    # ── 12: dimensional_gate ──────────────────────────────────
    Ruleset(
        name="dimensional_gate",
        description="State-space is the first gate. G1=Ð≥𐑼 (infinite-dimensional or "
                    "higher). 0D points and 2D surfaces are structurally precluded from "
                    "Frobenius closure — they lack sufficient degrees of freedom. "
                    "G2=⊙≥⊙. G3=Φ≥𐑹 (Frobenius-special parity). In this universe, "
                    "you need an infinite canvas before you can paint yourself.",
        g1=GateSpec("⊢", 3.0),   # 𐑼 = infinite-dim (ord 3); 𐑦=holographic (ord 4) also passes
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("<", 5.0),   # 𐑹 = Frobenius-special
        gate_ordering=True,
    ),

    # ── 13: kinetics_trap ─────────────────────────────────────
    Ruleset(
        name="kinetics_trap",
        description="Slowness is a structural requirement. G1=Ç≥𐑧 (slow/near-equilibrium "
                    "kinetics). Fast processes (Ç=𐑺) and moderately-paced processes "
                    "(Ç=𐑪) cannot Frobenius-close — they outrun their own structure. "
                    "Only systems that move slowly enough to track themselves qualify. "
                    "G2=⊙≥⊙. G3=Ω≥𐑭. In this universe, haste structurally precludes "
                    "closure.",
        g1=GateSpec("⊤", 3.0),   # 𐑧 = slow (ord 3); 𐑤=trap-ordered (ord 4); 𐑘=MBL (ord 5) all pass
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ),

    # ── 14: triple_criticality ────────────────────────────────
    Ruleset(
        name="triple_criticality",
        description="Criticality is everything — three rungs of a single ladder. "
                    "G1=⊙≥𐑢 (any criticality), G2=⊙≥⊙ (self-modeling active), "
                    "G3=⊙≥𐑣 (super-critical, ord 3). All three operad layers are "
                    "gated by the same primitive at escalating ordinals. In this "
                    "universe, Φ, Ω, and the other primitives are descriptive, not "
                    "gating. Consciousness depth is the only structural filter.",
        g1=GateSpec("⊙", 1.0),   # 𐑢 = sub-critical (lowest)
        g2=GateSpec("⊙", 2.0),   # ⊙ = self-modeling
        g3=GateSpec("⊙", 3.0),   # 𐑣 = super-critical (max)
        gate_ordering=True,
    ),

    # ── 15: t_hybrid ──────────────────────────────────────────
    Ruleset(
        name="t_hybrid",
        description="Time requires both dynamics AND geometry. T constituted by all "
                    "five dynamic primitives (Φ,ƒ,Ç,Ħ,Ω) AND three primitives "
                    "(Ð,⊣,Ř). Eight primitives must simultaneously satisfy their critical "
                    "conditions for T-sealing. Canonical gates. In this universe, time "
                    "is the most demanding structural alignment — process and space must "
                    "co-constitute, or time does not seal.",
        t_prims=dict(_T_HYBRID),
    ),

    # ── 16: broadcast_universe ────────────────────────────────
    Ruleset(
        name="broadcast_universe",
        description="Interaction grammar as the fundamental gate. G1=ɢ≥𐑠 (sequential "
                    "composition or broadcast). Systems with only conjunctive (𐑝) or "
                    "disjunctive (𐑜) interaction grammar cannot Frobenius-close — they "
                    "lack the sequential structure necessary for self-reference. "
                    "G2=⊙≥⊙. G3=Ω≥𐑭. In this universe, how you interact determines "
                    "whether you can close.",
        g1=GateSpec("∋", 3.0),   # 𐑠 = sequential (ord 3); 𐑵 = broadcast (ord 4) passes
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ),

    # ── 17: t_inverted ────────────────────────────────────────
    Ruleset(
        name="t_inverted",
        description="Time constituted by the primitives canonically NOT in T: "
                    "dimensionality, topology, relation, scope, and stoichiometry. "
                    "In this universe, time is not dynamics — it is structure. "
                    "Canonical gates. The inversion reveals what 'time as geometry' "
                    "selects for when decoupled from process primitives.",
        t_prims=dict(_T_INVERTED),
    ),

    # ── 18: single_gate ───────────────────────────────────────
    Ruleset(
        name="single_gate",
        description="Only G1 matters. G2 and G3 are set to trivially open (any Σ value "
                    "passes at ord 1.0). G1=Φ≥𐑹 (Frobenius parity). All entries that "
                    "pass G1 are automatically idempotent_terminal — traced_monoidal "
                    "collapses. This universe reveals what the Frobenius gate alone "
                    "selects for, with no further filtering.",
        g1=GateSpec("<", 5.0),   # 𐑹 = Frobenius-special
        g2=GateSpec("⊞", 1.0),   # trivial — all pass
        g3=GateSpec("⊞", 1.0),   # trivial — all pass
        gate_ordering=True,
    ),

    # ── 19: fidelity_universe ─────────────────────────────────
    Ruleset(
        name="fidelity_universe",
        description="Quantum coherence is the fundamental gate. G1=ƒ≥𐑐 (full fidelity, "
                    "hbar regime). Classical (ℓ) and thermal (ð) systems cannot "
                    "Frobenius-close — they lack the coherence required for self-modeling. "
                    "G2=⊙≥⊙. G3=Φ≥𐑹. In this universe, only quantum-coherent systems "
                    "can achieve closure. Classical systems stay plain "
                    "regardless of their other primitives.",
        g1=GateSpec("⋈", 3.0),   # 𐑐 = quantum/hbar (ord 3, max)
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("<", 5.0),   # 𐑹 = Frobenius-special
        gate_ordering=True,
    ),

    # ── 20: stoichiometry_universe ────────────────────────────
    Ruleset(
        name="stoichiometry_universe",
        description="Component heterogeneity is the first gate. G1=Σ≥𐑳 (many "
                    "heterogeneous components). Systems with 1:1 or n:n stoichiometry "
                    "cannot Frobenius-close — uniformity precludes the internal "
                    "differentiation needed for self-reference. G2=⊙≥⊙. G3=Ω≥𐑭. "
                    "In this universe, you must be internally diverse before you can "
                    "model yourself.",
        g1=GateSpec("⊞", 3.0),   # 𐑳 = many heterogeneous (ord 3, max)
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ),
    # ── 22: absorption_democracy ───────────────────────────────
    Ruleset(
        name="absorption_democracy",
        description="No absorptions. Every primitive fights on its own terms. "
                    "No ⊙ dominance; no Σ n:m monopoly. Meet, join, and tensor "
                    "are pure lattice operations — the ordinary-weighted sum of "
                    "every primitive. In this universe, nothing is special. "
                    "Systems that rely on absorption for closure are plain.",
        absorption_rules=(),  # empty — no absorption at all
    ),

    # ── 23: absorption_monarchy ───────────────────────────────
    Ruleset(
        name="absorption_monarchy",
        description="⊙ (⊙ criticality) absorbs EVERYTHING. Under meet, join, "
                    "AND tensor, any system touching self-modeling criticality is "
                    "completely dominated by it. In this universe, self-modeling is "
                    "totalitarian — you cannot couple to a self-modeling system without "
                    "becoming it. The monadic absorption empire.",
        absorption_rules=(
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("meet", "join", "tensor")),  # Σ n:m also totalitarian
            AbsorptionRule("<", "𐑹", ("meet", "join", "tensor")),  # Frobenius parity absorbs
            AbsorptionRule("◻", "𐑭", ("meet", "join", "tensor")),  # integer winding absorbs
        ),
    ),

    # ── 24: absorption_inverted ───────────────────────────────
    Ruleset(
        name="absorption_inverted",
        description="The antimonarchy: sub-critical (𐑢) and trivial winding (𐑷) "
                    "are the absorbing values. Coupling to the simplest, most trivial "
                    "values dominates. In this universe, complexity is fragile — the "
                    "ground state always wins. Meet, join, and tensor all collapse "
                    "toward the baseline. O_∞ is structurally impossible because "
                    "every attempt at self-modeling gets absorbed by triviality.",
        absorption_rules=(
            AbsorptionRule("⊙", "𐑢", ("meet", "join", "tensor")),  # sub-critical absorbs
            AbsorptionRule("◻", "𐑷", ("meet", "join", "tensor")),  # trivial winding absorbs
            AbsorptionRule("⊞", "𐑙", ("meet", "join", "tensor")),  # 1:1 stoichiometry absorbs
        ),
        g1=GateSpec("<", 5.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),

    # ── 25: absorption_tensor_only ────────────────────────────
    Ruleset(
        name="absorption_tensor_only",
        description="Absorption applies ONLY under tensor, not meet or join. "
                    "⊙ and Σ n:m absorb under tensor as in the canonical "
                    "universe, but meet and join are pure lattice operations. "
                    "In this universe, coupling (tensor) is destructive to self-modeling, "
                    "but comparison (meet/join) preserves structure. You can compare "
                    "without collapsing.",
        absorption_rules=(
            AbsorptionRule("⊙", "⊙", ("tensor",)),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
    ),

    # ── 26: absorption_chirality_first ─────────────────────────
    Ruleset(
        name="absorption_chirality_first",
        description="Chirality is the fundamental absorbing primitive. Ħ=𐑫 (eternal "
                    "memory / Markov order ∞) absorbs everything under all operations. "
                    "In this universe, memory is dominant — any system that remembers "
                    "forever cannot be coupled to without inheriting its memory. "
                    "Forgetfulness is structurally precluded. G1=Ħ≥𐑖. "
                    "G2=⊙≥⊙. G3=Ω≥𐑭.",
        absorption_rules=(
            AbsorptionRule("⊥", "𐑫", ("meet", "join", "tensor")),
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
        g1=GateSpec("⊥", 3.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),

    # ── 27: absorption_scope_empire ───────────────────────────
    Ruleset(
        name="absorption_scope_empire",
        description="Maximal scope (Γ=𐑔) is absorbing under all operations. "
                    "Any system with universal interaction range dominates every "
                    "coupling. Local and mesoscale systems are absorbed into "
                    "universality. In this universe, you cannot be parochial — "
                    "the universal swallows the particular.",
        absorption_rules=(
            AbsorptionRule("∈", "𐑔", ("meet", "join", "tensor")),
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
        g1=GateSpec("∈", 3.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),

    # ── 28: absorption_topology_seal ──────────────────────────
    Ruleset(
        name="absorption_topology_seal",
        description="Topological closure (⊣=𐑸) is absorbing under all operations. "
                    "Any system with fully imscriptive topology dominates every "
                    "coupling. In this universe, topology is destiny — the most "
                    "connected structure absorbs everything it touches. "
                    "G1=⊣≥𐑸. G2=⊙≥⊙. G3=Ω≥𐑭.",
        absorption_rules=(
            AbsorptionRule("⊣", "𐑸", ("meet", "join", "tensor")),
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
        g1=GateSpec("⊣", 5.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),

    # ── 29: predator_universe ─────────────────────────────────
    Ruleset(
        name="predator_universe",
        description="Asymmetric tensor absorption: Frobenius-special parity (Φ=𐑹) "
                    "absorbs under tensor ONLY when it is the LEFT operand — the "
                    "actor, not the acted-upon. A Frobenius-special system that is "
                    "tensored into absorbs nothing; one that acts on another absorbs "
                    "everything. Being acted on by self-modeling criticality (⊙, "
                    "symmetric) still absorbs as usual. In this universe, agency is "
                    "structural: what you do to others is not what others do to you. "
                    "G1=Φ≥𐑹. G2=⊙≥⊙. G3=Ω≥𐑭.",
        absorption_rules=(
            AbsorptionRule("<", "𐑹", ("tensor",), direction="left"),
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
        g1=GateSpec("<", 5.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),

    # ── 30: prey_universe ─────────────────────────────────────
    Ruleset(
        name="prey_universe",
        description="Asymmetric tensor absorption: Frobenius-special parity (Φ=𐑹) "
                    "absorbs under tensor ONLY when it is the RIGHT operand — the "
                    "system being acted upon. A Frobenius-special system that acts "
                    "absorbs nothing; one that is acted on absorbs everything. The "
                    "dual of predator_universe: passivity is the structural power. "
                    "G1=Φ≥𐑹. G2=⊙≥⊙. G3=Ω≥𐑭.",
        absorption_rules=(
            AbsorptionRule("<", "𐑹", ("tensor",), direction="right"),
            AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),
            AbsorptionRule("⊞", "𐑳", ("tensor",)),
        ),
        g1=GateSpec("<", 5.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("◻", 3.0),
    ),
]

# =============================================================================
# RULESET PERMUTATION GENERATOR
# Systematically iterates over ALL possible combinations of:
#   (a) gate configs:  (G1_prim, G1_ord, G2_prim, G2_ord, G3_prim, G3_ord, ordering)
#   (b) T-constitutions: which primitives constitute time, at what critical values
#   (c) absorption rules: which (primitive, value) pairs are absorbing under which ops
# =============================================================================

def _available_ordinals(prim: str) -> List[float]:
    """Return all valid ordinal thresholds for a primitive (sorted ascending)."""
    return sorted(set(ORDINALS.get(prim, {}).values()))


def _value_at_ordinal(prim: str, ord_val: float) -> str:
    """Return the Shavian glyph whose ordinal equals ord_val (inverse of ORDINALS)."""
    for glyph, o in ORDINALS.get(prim, {}).items():
        if o == ord_val:
            return glyph
    raise ValueError(f"No value for {prim} at ordinal {ord_val}")


def _all_gate_primitive_pairs() -> List[Tuple[str, float, str]]:
    """Return list of (primitive, ordinal, glyph) for all possible gate specs."""
    pairs = []
    for prim in PRIMITIVE_ORDER:
        for o in _available_ordinals(prim):
            glyph = _value_at_ordinal(prim, o)
            pairs.append((prim, o, glyph))
    return pairs


# ── Gate permutation generators ──────────────────────────────────

def iter_gate_configs(
    max_per_prim: Optional[int] = None,
    allow_duplicate_primitives: bool = True,
    orderings: Tuple[bool, ...] = (True, False),
) -> Iterator[Tuple[GateSpec, GateSpec, GateSpec, bool]]:
    """
    Yield ALL (G1, G2, G3, ordering) gate configurations.

    Total unique configurations:
      - 12 primitives × avg ~4 ordinals ≈ 49 gate-primitive pairs
      - 49³ = 117,649 ordered triples (with duplicates allowed)
      - × 2 orderings = 235,298 configs
      - Without duplicate primitives: C(12,3)×3! × 4³ ≈ 220×6×64 = 84,480 configs

    Set max_per_prim=N to only use the top N ordinal thresholds per primitive.
    Set allow_duplicate_primitives=False to require G1, G2, G3 be distinct primitives.
    """
    pairs = _all_gate_primitive_pairs()
    if max_per_prim is not None:
        # Keep only the highest max_per_prim ordinals per primitive
        prim_groups: Dict[str, List[Tuple[str, float, str]]] = {}
        for prim, o, glyph in pairs:
            prim_groups.setdefault(prim, []).append((prim, o, glyph))
        filtered = []
        for prim, grp in prim_groups.items():
            grp.sort(key=lambda x: -x[1])  # descending ordinal
            filtered.extend(grp[:max_per_prim])
        pairs = filtered

    for (p1, o1, g1), (p2, o2, g2), (p3, o3, g3) in itertools.product(pairs, repeat=3):
        if not allow_duplicate_primitives:
            if len({p1, p2, p3}) < 3:
                continue
        for ordering in orderings:
            yield (
                GateSpec(p1, o1),
                GateSpec(p2, o2),
                GateSpec(p3, o3),
                ordering,
            )


def iter_gate_configs_sampled(
    n: int, seed: int = 42, allow_duplicate_primitives: bool = True
) -> Iterator[Tuple[GateSpec, GateSpec, GateSpec, bool]]:
    """
    Yield n random samples from the gate configuration space.
    """
    pairs = _all_gate_primitive_pairs()
    rng = random.Random(seed)
    for _ in range(n):
        p1, o1, g1 = rng.choice(pairs)
        p2, o2, g2 = rng.choice(pairs)
        p3, o3, g3 = rng.choice(pairs)
        ordering = rng.choice([True, False])
        yield (
            GateSpec(p1, o1),
            GateSpec(p2, o2),
            GateSpec(p3, o3),
            ordering,
        )


def count_gate_configs(
    allow_duplicate_primitives: bool = True,
    max_per_prim: Optional[int] = None,
) -> int:
    """Total number of gate configurations in the space."""
    pairs = _all_gate_primitive_pairs()
    if max_per_prim is not None:
        prim_groups: Dict[str, list] = {}
        for prim, o, glyph in pairs:
            prim_groups.setdefault(prim, []).append((prim, o, glyph))
        filtered = []
        for prim, grp in prim_groups.items():
            grp.sort(key=lambda x: -x[1])
            filtered.extend(grp[:max_per_prim])
        pairs = filtered
    n = len(pairs)
    if allow_duplicate_primitives:
        return n ** 3 * 2  # ×2 for orderings
    else:
        # Choose 3 distinct primitives, then assign ordinals to each
        n_prim = len(PRIMITIVE_ORDER)
        pair_counts = {p: sum(1 for x in pairs if x[0] == p) for p in PRIMITIVE_ORDER}
        total = 0
        for p1, p2, p3 in itertools.permutations(PRIMITIVE_ORDER, 3):
            total += pair_counts[p1] * pair_counts[p2] * pair_counts[p3]
        return total * 2


# ── T-constitution permutation generators ───────────────────────

def _default_critical_value(prim: str) -> Tuple[str, bool]:
    """Default critical value for a primitive: its max ordinal, with ceiling=False."""
    ords = _available_ordinals(prim)
    max_ord = max(ords)
    val = _value_at_ordinal(prim, max_ord)
    return (val, False)


def iter_t_subsets(
    fixed_prims: Optional[Dict[str, Tuple[str, bool]]] = None,
) -> Iterator[Dict[str, Tuple[str, bool]]]:
    """
    Yield ALL T-constitution subsets of the 12 primitives.

    Total: 2^12 = 4,096 subsets. Each primitive either included at its
    default critical value, or excluded.

    fixed_prims: primitives that are always included (with their critical values).
    """
    fixed = fixed_prims or {}
    variable = [p for p in PRIMITIVE_ORDER if p not in fixed]

    for mask in range(1 << len(variable)):
        t_prims = dict(fixed)
        for i, prim in enumerate(variable):
            if mask & (1 << i):
                t_prims[prim] = _default_critical_value(prim)
        yield t_prims


def iter_t_constitutions_with_varied_critical_values(
    include_prims: Optional[List[str]] = None,
) -> Iterator[Dict[str, Tuple[str, bool]]]:
    """
    Yield T-constitutions where each included primitive is tested at ALL
    possible critical value assignments (value × ceiling_mode).

    For a set of k primitives, total = prod over prims of (n_values × 2).
    This is large (e.g., 5 prims can be ~10K+), so use sparingly.
    """
    include = include_prims or PRIMITIVE_ORDER
    all_options = []
    for prim in include:
        options = []
        vals = ORDINALS.get(prim, {})
        for glyph, o in vals.items():
            options.append((glyph, False))  # exact match
            options.append((glyph, True))   # ceiling mode
        all_options.append((prim, options))

    prims, opts = zip(*all_options)
    for combo in itertools.product(*opts):
        yield dict(zip(prims, combo))


# ── Absorption rule permutation generators ──────────────────────

def iter_single_absorption_rules() -> Iterator[Tuple[AbsorptionRule, ...]]:
    """
    Yield absorption rule configs with exactly ONE absorption rule active.
    Useful for understanding each primitive-value's individual effect.

    Total: sum over prims of n_values(prim) × 7 (non-empty subsets of {meet,join,tensor})
    = ~47 × 7 = 329 single-rule configs.
    """
    ops_list = [("meet",), ("join",), ("tensor",),
                ("meet", "join"), ("meet", "tensor"), ("join", "tensor"),
                ("meet", "join", "tensor")]
    for prim in PRIMITIVE_ORDER:
        vals = CANONICAL_VALUES.get(prim, [])
        for val in vals:
            for ops in ops_list:
                yield (AbsorptionRule(prim, val, ops),)


def iter_absorption_configs(
    max_rules: int = 2,
    include_baseline: bool = True,
) -> Iterator[Tuple[AbsorptionRule, ...]]:
    """
    Yield absorption configurations with up to max_rules active rules.

    At max_rules=2: total = sum_{k=0}^{2} C(329_single, k) ≈ 54K configs
    At max_rules=3: total = sum_{k=0}^{3} C(329, k) ≈ 5.9M — too large for catalog
    """
    all_single = list(iter_single_absorption_rules())
    # Each single is a 1-tuple. Flatten to individual rules.
    all_rules = [r[0] for r in all_single]

    # Yield baseline (canonical absorption)
    if include_baseline:
        yield _DEFAULT_ABSORPTION

    # Yield empty
    yield ()

    # Yield single rules
    for r in all_rules:
        yield (r,)

    # Yield pairs
    if max_rules >= 2:
        for r1, r2 in itertools.combinations(all_rules, 2):
            yield (r1, r2)


# ── Composite generator: full rulesets from parameter combinations ──

def build_ruleset(
    name: str,
    description: str,
    gate_config: Tuple[GateSpec, GateSpec, GateSpec, bool],
    t_config: Dict[str, Tuple[str, bool]],
    abs_config: Tuple[AbsorptionRule, ...],
) -> Ruleset:
    """Build a complete Ruleset from parameter choices."""
    g1, g2, g3, ordering = gate_config
    return Ruleset(
        name=name,
        description=description,
        g1=g1, g2=g2, g3=g3,
        gate_ordering=ordering,
        t_prims=t_config,
        absorption_rules=abs_config,
    )


def iter_rulesets(
    gates: str = "canonical",
    t_subsets: str = "canonical",
    absorptions: str = "canonical",
    max_count: Optional[int] = None,
    sample_seed: int = 42,
) -> Iterator[Ruleset]:
    """
    Composite iterator over the full ruleset parameter space.

    gates: 'canonical' | 'all' | 'random:N' | gate spec
    t_subsets: 'canonical' | 'all' | 'varied' | t-spec
    absorptions: 'canonical' | 'all' | 'single' | 'none'

    Controls combinatorial explosion:
      - 'canonical' = fixed canonical value for the parameter
      - 'all' = full permutation of that parameter
      - 'random:N' = N random samples
      - direct spec = fixed value
    """
    # Resolve gate configs
    if gates == "canonical":
        gate_list = [(GateSpec("<", 5.0), GateSpec("⊙", 2.0), GateSpec("◻", 3.0), True)]
    elif gates == "all":
        # Limit to avoid explosion: top 2 ordinals per prim, no duplicate prims
        gate_list = list(iter_gate_configs(max_per_prim=2, allow_duplicate_primitives=False))
    elif gates.startswith("random:"):
        n = int(gates.split(":")[1])
        gate_list = list(iter_gate_configs_sampled(n, seed=sample_seed))
    else:
        raise ValueError(f"Unknown gate spec: {gates}")

    # Resolve T-constitutions
    if t_subsets == "canonical":
        t_list = [dict(_T_CANONICAL)]
    elif t_subsets == "all":
        t_list = list(iter_t_subsets())
    elif t_subsets == "structural":
        t_list = [dict(_T_STRUCTURAL)]
    elif t_subsets == "hybrid":
        t_list = [dict(_T_HYBRID)]
    elif t_subsets == "inverted":
        t_list = [dict(_T_INVERTED)]
    elif t_subsets.startswith("varied:"):
        prims = t_subsets.split(":")[1].split(",")
        t_list = list(iter_t_constitutions_with_varied_critical_values(include_prims=prims))
    else:
        raise ValueError(f"Unknown T-subsets spec: {t_subsets}")

    # Resolve absorptions
    if absorptions == "canonical":
        abs_list = [_DEFAULT_ABSORPTION]
    elif absorptions == "none":
        abs_list = [()]
    elif absorptions == "single":
        abs_list = list(iter_single_absorption_rules())
    elif absorptions == "all_pairs":
        abs_list = list(iter_absorption_configs(max_rules=2, include_baseline=True))
    else:
        raise ValueError(f"Unknown absorptions spec: {absorptions}")

    # Generate outer product
    count = 0
    for gc in gate_list:
        for tc in t_list:
            for ac in abs_list:
                tag_g = f"G1={gc[0].prim}≥ord{gc[0].min_ord}"
                tag_g += f"_G2={gc[1].prim}≥ord{gc[1].min_ord}"
                tag_g += f"_G3={gc[2].prim}≥ord{gc[2].min_ord}"
                tag_g += "_seq" if gc[3] else "_par"
                tag_t = f"T_{'_'.join(sorted(tc.keys()))}" if tc else "T_empty"
                tag_a = f"abs{len(ac)}" if ac else "abs0"
                tag = f"gen_{tag_g}_{tag_t}_{tag_a}"

                desc = (f"Generated: gates=({gc[0].prim}≥ord{gc[0].min_ord}, "
                        f"{gc[1].prim}≥ord{gc[1].min_ord}, "
                        f"{gc[2].prim}≥ord{gc[2].min_ord}, "
                        f"{'seq' if gc[3] else 'par'}), "
                        f"T={list(tc.keys())}, abs_rules={len(ac)}")

                yield build_ruleset(tag, desc, gc, tc, ac)
                count += 1
                if max_count is not None and count >= max_count:
                    return

# ── CLI ──────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="New universes — profile hand-crafted rulesets + permute ALL possible gates/T/absorptions"
    )
    sub = parser.add_subparsers(dest="cmd")

    # Existing: profile hand-crafted rulesets
    p_prof = sub.add_parser("profile", help="Profile one or all hand-crafted new rulesets")
    p_prof.add_argument("--name", help="Ruleset name (default: all)")
    p_prof.add_argument("--catalog", help="Path to IG_catalog.json")

    p_cmp = sub.add_parser("compare", help="Side-by-side fingerprint table (all 28 rulesets)")
    p_cmp.add_argument("--catalog", help="Path to IG_catalog.json")

    p_list = sub.add_parser("list", help="List predefined rulesets")

    # NEW: permute subcommand — systematic ruleset generation
    p_perm = sub.add_parser("permute", help="Generate and profile rulesets from parameter permutations")
    p_perm.add_argument("--gates", default="canonical",
                        help="Gate config: 'canonical' | 'all' | 'random:N'")
    p_perm.add_argument("--t-subsets", default="canonical",
                        help="T-constitution: 'canonical' | 'all' | 'structural' | 'hybrid' | 'inverted' | 'none'")
    p_perm.add_argument("--absorptions", default="canonical",
                        help="Absorption: 'canonical' | 'none' | 'single' | 'all_pairs'")
    p_perm.add_argument("--max", type=int, default=None,
                        help="Max rulesets to generate (default: no limit)")
    p_perm.add_argument("--seed", type=int, default=42,
                        help="Random seed for sampling (default: 42)")
    p_perm.add_argument("--catalog", help="Path to IG_catalog.json")
    p_perm.add_argument("--count-only", action="store_true",
                        help="Only print combinatorial counts, don't profile")

    # NEW: count subcommand — show combinatorial scale
    p_cnt = sub.add_parser("count", help="Count configurations in the permutation space")
    p_cnt.add_argument("--gates", action="store_true", help="Show gate config count")
    p_cnt.add_argument("--t-subsets", action="store_true", help="Show T-subset count")
    p_cnt.add_argument("--absorptions", action="store_true", help="Show absorption config count")
    p_cnt.add_argument("--all", action="store_true", help="Show all counts")

    args = parser.parse_args()

    # ── list ──────────────────────────────────────────────────
    if args.cmd == "list" or args.cmd is None:
        print("═══ Hand-crafted rulesets (RULESETS + NEW_RULESETS) ═══")
        all_rs = list(RULESETS) + NEW_RULESETS
        for r in all_rs:
            gs = f"G1={r.g1.prim}≥ord{r.g1.min_ord}, G2={r.g2.prim}≥ord{r.g2.min_ord}, G3={r.g3.prim}≥ord{r.g3.min_ord}"
            ab = f", abs={len(r.absorption_rules)}" if r.absorption_rules else ""
            print(f"  {r.name:<26}  {gs}{ab}")
        print(f"\nTotal: {len(all_rs)} rulesets")
        return

    # ── count ─────────────────────────────────────────────────
    if args.cmd == "count":
        show_all = args.all or not (args.gates or args.t_subsets or args.absorptions)
        if show_all or args.gates:
            n_gates_full = count_gate_configs()
            n_gates_distinct = count_gate_configs(allow_duplicate_primitives=False)
            n_gates_top2 = count_gate_configs(allow_duplicate_primitives=False, max_per_prim=2)
            print("═══ Gate configuration counts ═══")
            print(f"  Full (duplicate prims allowed):     {n_gates_full:>12,}")
            print(f"  Distinct prims (all ordinals):       {n_gates_distinct:>12,}")
            print(f"  Distinct prims (top 2 ordinals):     {n_gates_top2:>12,}")
        if show_all or args.t_subsets:
            print("\n═══ T-constitution counts ═══")
            print(f"  All subsets (2^12):                  4,096")
            print(f"  With ceiling variations per prim:    varies (up to ~10^10)")
        if show_all or args.absorptions:
            n_single = sum(1 for _ in iter_single_absorption_rules())
            print("\n═══ Absorption rule counts ═══")
            print(f"  Single-rule configurations:          {n_single:>12,}")
            print(f"  Pairs (k=2):                         ~{n_single * (n_single - 1) // 2:>12,}")
            print(f"  Full combinatorial (k=0..47):        cannot enumerate")
        return

    catalog_path = getattr(args, "catalog", None)
    catalog = load_catalog_dicts(extra_path=catalog_path)

    # ── profile (hand-crafted) ────────────────────────────────
    if args.cmd == "profile":
        targets = NEW_RULESETS
        if getattr(args, "name", None):
            candidates = [r for r in NEW_RULESETS + list(RULESETS) if r.name == args.name]
            if candidates:
                targets = candidates
            else:
                print(f"Unknown ruleset '{args.name}'")
                sys.exit(1)
        for r in targets:
            prof = universe_profile(r, catalog)
            print_profile(prof)
        return

    # ── compare ────────────────────────────────────────────────
    if args.cmd == "compare":
        from navigators.ruleset_universe import print_comparison
        all_rs = list(RULESETS) + NEW_RULESETS
        profiles = [universe_profile(r, catalog) for r in all_rs]
        print_comparison(profiles)
        return

    # ── permute ────────────────────────────────────────────────
    if args.cmd == "permute":
        if args.count_only:
            # Count what we'd generate
            gate_count = 1
            if args.gates == "all":
                gc_list = list(iter_gate_configs(max_per_prim=2, allow_duplicate_primitives=False))
                gate_count = len(gc_list)
            elif args.gates.startswith("random:"):
                gate_count = int(args.gates.split(":")[1])

            if args.t_subsets == "all":
                t_count = 4096
            elif args.t_subsets == "varied":
                t_count = "varies"
            else:
                t_count = 1

            if args.absorptions == "single":
                a_count = sum(1 for _ in iter_single_absorption_rules())
            elif args.absorptions == "all_pairs":
                s = sum(1 for _ in iter_single_absorption_rules())
                a_count = 1 + 1 + s + s * (s - 1) // 2  # baseline + empty + singles + pairs
            else:
                a_count = 1

            total = f"{gate_count} × {t_count} × {a_count}"
            print(f"Rulesets to generate: {total}")
            if args.max:
                print(f"  (capped at {args.max})")
            return

        gen = iter_rulesets(
            gates=args.gates,
            t_subsets=args.t_subsets,
            absorptions=args.absorptions,
            max_count=args.max,
            sample_seed=args.seed,
        )
        count = 0
        from navigators.ruleset_universe import print_comparison
        profiles = []
        for ruleset in gen:
            if args.max and count >= args.max:
                break
            prof = universe_profile(ruleset, catalog)
            profiles.append(prof)
            print_profile(prof, verbose=False)
            count += 1
        print(f"\n=== Generated {count} rulesets ===")
        if len(profiles) > 1:
            print("\n── Comparison ──")
            print_comparison(profiles)
        return


if __name__ == "__main__":
    main()
