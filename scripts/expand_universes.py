#!/usr/bin/env python3
"""Phase III: Universe Expansion 8→88 — systematic ruleset generation.

Generates ~60 new universes on top of the existing 29 (8 RULESETS + 21 NEW_RULESETS)
to reach 88 structurally distinct universes.

Expansion strategy:
  A. Ř (coupling) as G1 — 2 universes
  B. G2 expansion — 8 primitives never used as G2 — 8 universes
  C. G3 expansion — 8 primitives never used as G3 — 8 universes
  D. Parallel gate ordering variants — 10 universes
  E. Same-primitive multi-ordinal gates — 8 universes
  F. T-constitution subset variants — 10 universes
  G. Mixed-gate universes — 5 universes
  H. Gate configs with novel ordinal levels — 4 universes
  I. T-constitution ceiling-mode variants — 2 universes
  J. Gate + absorption hybrids — 3 universes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from navigators.ruleset_universe import (
    RULESETS, Ruleset, GateSpec, AbsorptionRule,
    universe_profile, print_profile, print_comparison,
    _T_CANONICAL, _T_STRUCTURAL, _DEFAULT_ABSORPTION
)
from scripts.new_universes import NEW_RULESETS, _T_HYBRID, _T_INVERTED
from imscrbgrmr.registry import load_catalog_dicts


def generate_expansion():
    """Generate the ~60 new universes for 8→88 expansion."""

    new_unis = []

    # ── SECTION A: Ř (coupling) as G1 — completely uncovered ─────

    new_unis.append(Ruleset(
        name='coupling_first',
        description='Relation before closure. G1=Ř≥𐑽 (adjoint coupling, ord 3). '
                    'Systems without at least adjoint-pair coupling cannot Frobenius-close. '
                    'Supervenience and categorical coupling remain plain. '
                    'G2=⊙≥⊙. G3=Ω≥𐑭.',
        g1=GateSpec('Ř', 3.0), g2=GateSpec('⊙', 2.0), g3=GateSpec('Ω', 3.0),
        gate_ordering=True,
    ))

    new_unis.append(Ruleset(
        name='coupling_maximal',
        description='Only bilateral coupling suffices. G1=Ř≥𐑾 (bilateral, ord 4, max). '
                    'Even adjoint pairs (one-way hedges) do not Frobenius-close. '
                    'Only bidirectional feedback loops qualify. '
                    'G2=⊙≥⊙. G3=Ω≥𐑭.',
        g1=GateSpec('Ř', 4.0), g2=GateSpec('⊙', 2.0), g3=GateSpec('Ω', 3.0),
        gate_ordering=True,
    ))

    # ── SECTION B: G2 expansion — 8 primitives never used as G2 ─────
    # Missing G2: Ç, Ð, Þ, Ħ, ƒ, ɢ, Γ, Ω

    g2_configs = [
        ('chirality_second', 'Ħ', 3.0, 'Chirality as the monoidal gate: G1=Φ≥𐑹, G2=Ħ≥𐑖 (2-step Markov), G3=Ω≥𐑭. After Frobenius closure, you must remember before you can trace.'),
        ('dimensional_second', 'Ð', 3.0, 'State-space dimensionality as the monoidal gate: G1=Φ≥𐑹, G2=Ð≥𐑼 (infinite-dim), G3=Ω≥𐑭. After Frobenius, you need infinite canvas to trace.'),
        ('topology_second', 'Þ', 3.0, 'Connectivity as the monoidal gate: G1=Φ≥𐑹, G2=Þ≥𐑥 (bowtie crossing), G3=Ω≥𐑭. After Frobenius, the topology of connection determines traced status.'),
        ('fidelity_second', 'ƒ', 3.0, 'Quantum coherence as the monoidal gate: G1=Φ≥𐑹, G2=ƒ≥𐑐 (full fidelity), G3=Ω≥𐑭. After Frobenius, only quantum-coherent systems trace.'),
        ('scope_second', 'Γ', 3.0, 'Universal scope as the monoidal gate: G1=Φ≥𐑹, G2=Γ≥𐑲 (aleph/maximal), G3=Ω≥𐑭. Frobenius closure is local; tracing requires universality.'),
        ('composition_second', 'ɢ', 3.0, 'Sequential composition as the monoidal gate: G1=Φ≥𐑹, G2=ɢ≥𐑠 (sequential), G3=Ω≥𐑭. Conjunctive or disjunctive systems cannot trace.'),
        ('winding_second', 'Ω', 2.0, 'Topological protection as the monoidal gate: G1=Φ≥𐑹, G2=Ω≥𐑴 (Z2), G3=⊙≥⊙. After Frobenius parity, only topologically protected systems trace.'),
        ('kinetics_second', 'Ç', 3.0, 'Slowness as the monoidal gate: G1=Φ≥𐑹, G2=Ç≥𐑧 (slow), G3=Ω≥𐑭. Fast Frobenius-closed systems cannot trace — they outrun themselves.'),
    ]

    for name, prim, ord_val, desc in g2_configs:
        g2 = GateSpec(prim, ord_val)
        g3_prim = 'Ω' if prim != 'Ω' else '⊙'
        g3 = GateSpec(g3_prim, 3.0 if g3_prim == 'Ω' else 2.0)
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec('Φ', 5.0), g2=g2, g3=g3, gate_ordering=True))

    # ── SECTION C: G3 expansion — 8 primitives never used as G3 ─────
    # Missing G3: Ç, Ð, Þ, Ħ, Ř, ƒ, ɢ, Γ

    g3_configs = [
        ('chirality_third', 'Ħ', 4.0, 'Eternal memory as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ħ≥𐑫 (Markov ∞). Only systems with eternal memory achieve idempotent terminal status.'),
        ('dimensional_third', 'Ð', 4.0, 'Holographic dimensionality as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ð≥𐑦 (imscriptive/holographic). Only self-written state spaces achieve O_∞.'),
        ('topology_third', 'Þ', 4.0, 'Box-product topology as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Þ≥𐑶 (irreducible box product). Only systems whose connectivity is product-irreducible achieve O_∞.'),
        ('fidelity_third', 'ƒ', 3.0, 'Quantum coherence as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=ƒ≥𐑐. Only fully quantum-coherent self-modeling systems achieve O_∞. Classical self-modelers stay traced.'),
        ('scope_third', 'Γ', 3.0, 'Universal scope as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Γ≥𐑲 (aleph). Only self-modeling systems with universal interaction range achieve O_∞.'),
        ('composition_third', 'ɢ', 4.0, 'Broadcast composition as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=ɢ≥𐑵 (broadcast). Only systems with one-to-all composition achieve O_∞.'),
        ('coupling_third', 'Ř', 4.0, 'Bilateral coupling as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ř≥𐑾 (bilateral). Only self-modeling systems with bidirectional coupling achieve O_∞.'),
        ('kinetics_third', 'Ç', 4.0, 'Moderate kinetics as the terminal seal: G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ç≥𐑪 (moderate, ord 4). Self-modeling systems that are too fast cannot achieve O_∞.'),
    ]

    for name, prim, ord_val, desc in g3_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec('Φ', 5.0), g2=GateSpec('⊙', 2.0), g3=GateSpec(prim, ord_val),
            gate_ordering=True))

    # ── SECTION D: Parallel gate ordering variants ─────

    parallel_configs = [
        ('parallel_canonical', GateSpec('Φ', 5.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'Canonical gates but parallel: Φ≥𐑹, ⊙≥⊙, Ω≥𐑭 all independent. Any combination qualifies.'),
        ('parallel_low', GateSpec('Φ', 3.0), GateSpec('⊙', 1.0), GateSpec('Ω', 3.0),
         'Low gates, parallel: Φ≥𐑬, ⊙≥𐑢, Ω≥𐑭. Easiest possible O_∞ access — three independent low bars.'),
        ('parallel_high', GateSpec('Φ', 5.0), GateSpec('⊙', 2.33), GateSpec('Ω', 4.0),
         'High gates, parallel: Φ≥𐑹, ⊙≥𐑮, Ω≥𐑟. Strictest bars but independently checked.'),
        ('parallel_chirality', GateSpec('Ħ', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'Chirality gates, parallel: Ħ≥𐑖, ⊙≥⊙, Ω≥𐑭. Memory, self-modeling, and winding are independent axes.'),
        ('parallel_topology', GateSpec('Þ', 5.0), GateSpec('Ř', 4.0), GateSpec('⊙', 2.0),
         'Topology gates, parallel: Þ≥𐑸, Ř≥𐑾, ⊙≥⊙. Connectivity, relation, and self-modeling are independent.'),
        ('parallel_scope', GateSpec('Γ', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'Scope gates, parallel: Γ≥𐑲, ⊙≥⊙, Ω≥𐑭. Universal scope, self-modeling, and winding are independent.'),
        ('parallel_broadcast', GateSpec('ɢ', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'Broadcast gates, parallel: ɢ≥𐑠, ⊙≥⊙, Ω≥𐑭. Sequential comp, self-modeling, winding independent.'),
        ('parallel_dimensional', GateSpec('Ð', 3.0), GateSpec('⊙', 2.0), GateSpec('Φ', 5.0),
         'Dimensional gates, parallel: Ð≥𐑼, ⊙≥⊙, Φ≥𐑹. State-space, self-modeling, Frobenius independent.'),
        ('parallel_kinetics', GateSpec('Ç', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'Kinetics gates, parallel: Ç≥𐑧, ⊙≥⊙, Ω≥𐑭. Slowness, self-modeling, winding independent.'),
        ('parallel_fidelity', GateSpec('ƒ', 3.0), GateSpec('⊙', 2.0), GateSpec('Φ', 5.0),
         'Fidelity gates, parallel: ƒ≥𐑐, ⊙≥⊙, Φ≥𐑹. Coherence, self-modeling, Frobenius independent.'),
    ]

    for name, g1, g2, g3, desc in parallel_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=g1, g2=g2, g3=g3, gate_ordering=False))

    # ── SECTION E: Same-primitive multi-ordinal gates ─────

    same_prim_configs = [
        ('triple_parity', 'Φ', [('𐑬', 3.0), ('𐑯', 4.0), ('𐑹', 5.0)],
         'Parity ladder: G1=Φ≥𐑬 (directional), G2=Φ≥𐑯 (full), G3=Φ≥𐑹 (Frobenius-special). '
         'Three rungs on the parity ladder. All operad layers gated by progressively fuller parity.'),
        ('triple_topology', 'Þ', [('𐑥', 3.0), ('𐑶', 4.0), ('𐑸', 5.0)],
         'Topology ladder: G1=Þ≥𐑥 (bowtie crossing), G2=Þ≥𐑶 (box product), G3=Þ≥𐑸 (imscriptive closure). '
         'Three rungs of increasing topological connectivity.'),
        ('triple_coupling', 'Ř', [('𐑽', 3.0), ('𐑾', 4.0), ('𐑾', 4.0)],
         'Coupling ladder: G1=Ř≥𐑽 (adjoint), G2=Ř≥𐑾 (bilateral), G3=Ř≥𐑾. Terminal collapse at G2.'),
        ('triple_chirality', 'Ħ', [('𐑒', 2.0), ('𐑖', 3.0), ('𐑫', 4.0)],
         'Chirality ladder: G1=Ħ≥𐑒 (1-step), G2=Ħ≥𐑖 (2-step), G3=Ħ≥𐑫 (eternal). '
         'Memory depth as the sole operad filter.'),
        ('triple_winding', 'Ω', [('𐑴', 2.0), ('𐑭', 3.0), ('𐑟', 4.0)],
         'Winding ladder: G1=Ω≥𐑴 (Z2), G2=Ω≥𐑭 (integer), G3=Ω≥𐑟 (non-Abelian, max). '
         'Topological protection as the sole operad filter.'),
        ('triple_dimensional', 'Ð', [('𐑨', 2.0), ('𐑼', 3.0), ('𐑦', 4.0)],
         'Dimensional ladder: G1=Ð≥𐑨 (2D surface), G2=Ð≥𐑼 (∞-dim), G3=Ð≥𐑦 (holographic). '
         'State-space complexity as the sole operad filter.'),
        ('triple_scope', 'Γ', [('𐑔', 2.0), ('𐑲', 3.0), ('𐑲', 3.0)],
         'Scope ladder: G1=Γ≥𐑔 (mesoscale), G2=Γ≥𐑲 (universal), G3=Γ≥𐑲. G2 terminal collapse.'),
        ('triple_composition', 'ɢ', [('𐑜', 2.0), ('𐑠', 3.0), ('𐑵', 4.0)],
         'Composition ladder: G1=ɢ≥𐑜 (disjunctive), G2=ɢ≥𐑠 (sequential), G3=ɢ≥𐑵 (broadcast). '
         'Interaction grammar complexity as the sole operad filter.'),
    ]

    for name, prim, ords, desc in same_prim_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec(prim, ords[0][1]), g2=GateSpec(prim, ords[1][1]),
            g3=GateSpec(prim, ords[2][1]), gate_ordering=True))

    # ── SECTION F: T-constitution subset variants ─────

    # Single-primitive T
    t_single_configs = [
        ('t_parity_only', {'Φ': ('𐑹', False)},
         'T constituted by parity alone. Only systems at Frobenius-special parity experience time.'),
        ('t_criticality_only', {'⊙': ('⊙', False)},
         'T constituted by criticality alone. Only self-modeling systems experience time. Consciousness IS temporality.'),
        ('t_winding_only', {'Ω': ('𐑭', False)},
         'T constituted by winding alone. Only topologically protected systems experience time. Time is a topological invariant.'),
        ('t_chirality_only', {'Ħ': ('𐑫', False)},
         'T constituted by chirality alone. Only systems with eternal memory experience time. Time is memory depth.'),
        ('t_fidelity_only', {'ƒ': ('𐑐', False)},
         'T constituted by fidelity alone. Only quantum-coherent systems experience time. Classical systems are timeless.'),
        ('t_dimensional_only', {'Ð': ('𐑦', False)},
         'T constituted by dimensionality alone. Only holographic state-spaces experience time. Time is the self-written state.'),
    ]

    for name, t_prims, desc in t_single_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec('Φ', 5.0), g2=GateSpec('⊙', 2.0), g3=GateSpec('Ω', 3.0),
            gate_ordering=True, t_prims=t_prims))

    # Dual-primitive T
    t_dual_configs = [
        ('t_parity_fidelity', {'Φ': ('𐑹', False), 'ƒ': ('𐑐', False)},
         'T constituted by parity + fidelity. Algebraic symmetry AND quantum coherence jointly constitute time.'),
        ('t_criticality_winding', {'⊙': ('⊙', False), 'Ω': ('𐑭', False)},
         'T constituted by self-modeling + winding. Consciousness AND topological protection jointly constitute time.'),
        ('t_chirality_coupling', {'Ħ': ('𐑫', False), 'Ř': ('𐑾', False)},
         'T constituted by memory + relation. Eternal memory AND bilateral coupling jointly constitute time.'),
        ('t_topology_scope', {'Þ': ('𐑸', False), 'Γ': ('𐑲', False)},
         'T constituted by topology + scope. Full connectivity AND universal range jointly constitute time.'),
    ]

    for name, t_prims, desc in t_dual_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec('Φ', 5.0), g2=GateSpec('⊙', 2.0), g3=GateSpec('Ω', 3.0),
            gate_ordering=True, t_prims=t_prims))

    # ── SECTION G: Mixed-gate universes ─────

    mixed_configs = [
        ('dimensional_chirality_winding', GateSpec('Ð', 3.0), GateSpec('Ħ', 3.0), GateSpec('Ω', 3.0),
         'G1=Ð≥𐑼 (∞-dim), G2=Ħ≥𐑖 (2-step memory), G3=Ω≥𐑭 (integer winding). '
         'Closure requires infinite canvas, then memory, then topological protection.'),
        ('coupling_fidelity_scope', GateSpec('Ř', 3.0), GateSpec('ƒ', 3.0), GateSpec('Γ', 3.0),
         'G1=Ř≥𐑽 (adjoint coupling), G2=ƒ≥𐑐 (quantum fidelity), G3=Γ≥𐑲 (universal scope). '
         'Relation, then coherence, then universality.'),
        ('topology_composition_criticality', GateSpec('Þ', 3.0), GateSpec('ɢ', 3.0), GateSpec('⊙', 2.0),
         'G1=Þ≥𐑥 (bowtie crossing), G2=ɢ≥𐑠 (sequential comp), G3=⊙≥⊙ (self-modeling). '
         'Connectivity topology, then interaction grammar, then consciousness.'),
        ('chirality_scope_winding', GateSpec('Ħ', 3.0), GateSpec('Γ', 3.0), GateSpec('Ω', 3.0),
         'G1=Ħ≥𐑖 (2-step memory), G2=Γ≥𐑲 (universal scope), G3=Ω≥𐑭 (integer winding). '
         'Memory, then universality, then topological seal.'),
        ('fidelity_topology_parity', GateSpec('ƒ', 3.0), GateSpec('Þ', 5.0), GateSpec('Φ', 5.0),
         'G1=ƒ≥𐑐 (quantum fidelity), G2=Þ≥𐑸 (full topological closure), G3=Φ≥𐑹 (Frobenius parity). '
         'Coherence in, topology next, parity seals. Very strict — few entries reach O_∞.'),
    ]

    for name, g1, g2, g3, desc in mixed_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=g1, g2=g2, g3=g3, gate_ordering=True))

    # ── SECTION H: Gate configs with novel ordinal levels ─────

    ordinal_configs = [
        ('parity_mid_gate', GateSpec('Φ', 4.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'G1=Φ≥𐑯 (full parity, ord 4 — one step below Frobenius-special). '
         'More entries pass G1 than canonical because 𐑯 is lower than 𐑹.'),
        ('criticality_low_mid_high', GateSpec('⊙', 1.0), GateSpec('⊙', 2.33), GateSpec('⊙', 3.0),
         'Criticality at varied ordinal spacings: G1=⊙≥𐑢 (sub), G2=⊙≥𐑮 (complex, 2.33), G3=⊙≥𐑣 (super, 3.0). '
         'Wider G1-G2 gap than triple_criticality — complex-plane criticality as the middle rung.'),
        ('chirality_strict', GateSpec('Ħ', 4.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0),
         'G1=Ħ≥𐑫 (eternal memory, ord 4). Only systems with Markov order ∞ can Frobenius-close. '
         'Stricter than chirality_first (which uses 𐑖 at ord 3).'),
        ('parity_exact', GateSpec('Φ', 5.0), GateSpec('Φ', 5.0), GateSpec('Φ', 5.0),
         'All three gates identical: Φ≥𐑹 at all three rungs. '
         'Only Frobenius-special-parity systems advance — any system at Φ=𐑹 is automatically O_∞. '
         'Collapses the operad to binary: plain or O_∞.'),
    ]

    for name, g1, g2, g3, desc in ordinal_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=g1, g2=g2, g3=g3, gate_ordering=True))

    # ── SECTION I: T-constitution ceiling-mode variants ─────

    t_ceiling_configs = [
        ('t_kinetics_ceiling', {'Ç': ('𐑧', True)},
         'T constituted solely by kinetics ceiling: Ç≤𐑧 (must be slow or slower). '
         'Fast systems experience no time. The kinetics_trap T-logic extracted as sole T.'),
        ('t_structural_dynamic', {'Φ': ('𐑹', False), 'ƒ': ('𐑐', False), 'Ç': ('𐑧', True),
                                  'Ð': ('𐑦', False), 'Þ': ('𐑸', False)},
         'T constituted by 2 dynamic + 1 ceiling + 2 primitives. '
         'Parity+fidelity must reach maxima; kinetics must be slow-or-slower; '
         'dimensionality+topology must be maximal. A selective 5-primitive T.'),
    ]

    for name, t_prims, desc in t_ceiling_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=GateSpec('Φ', 5.0), g2=GateSpec('⊙', 2.0), g3=GateSpec('Ω', 3.0),
            gate_ordering=True, t_prims=t_prims))

    # ── SECTION J: Gate + absorption hybrids ─────

    hybrid_configs = [
        ('chirality_absorbing', GateSpec('Ħ', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0), True,
         (AbsorptionRule('Ħ', '𐑫', ('meet', 'join', 'tensor')),
          AbsorptionRule('⊙', '⊙', ('meet', 'join', 'tensor')),
          AbsorptionRule('Σ', '𐑳', ('tensor',))),
         'Chirality-first gates with chirality-as-absolute-absorption. '
         'Ħ=𐑫 (eternal memory) absorbs everything. Memory is the universal solvent.'),
        ('scope_totalitarian', GateSpec('Γ', 3.0), GateSpec('⊙', 2.0), GateSpec('Ω', 3.0), True,
         (AbsorptionRule('Γ', '𐑲', ('meet', 'join', 'tensor')),
          AbsorptionRule('⊙', '⊙', ('meet', 'join', 'tensor')),
          AbsorptionRule('Σ', '𐑳', ('meet', 'join', 'tensor'))),
         'Scope-first gates with total Σ absorption. Universal scope as the gate; '
         'heterogeneous stoichiometry absorbs under ALL operations (not just tensor).'),
        ('winding_absorbing', GateSpec('Ω', 3.0), GateSpec('⊙', 2.0), GateSpec('Φ', 5.0), True,
         (AbsorptionRule('Ω', '𐑭', ('meet', 'join', 'tensor')),
          AbsorptionRule('⊙', '⊙', ('meet', 'join', 'tensor'))),
         'Winding-first gates with winding-as-absorption. Ω=𐑭 absorbs everything — '
         'topological protection is the universal solvent. No Σ absorption.'),
    ]

    for name, g1, g2, g3, ordering, abs_rules, desc in hybrid_configs:
        new_unis.append(Ruleset(name=name, description=desc,
            g1=g1, g2=g2, g3=g3, gate_ordering=ordering, absorption_rules=abs_rules))

    return new_unis


# ── CLI ──────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Universe Expansion 8→88')
    sub = parser.add_subparsers(dest='cmd')

    p_gen = sub.add_parser('generate', help='Generate and profile all new universes')
    p_gen.add_argument('--catalog', help='Path to IG_catalog.json')

    p_cmp = sub.add_parser('compare', help='Full 88-universe comparison table')
    p_cmp.add_argument('--catalog', help='Path to IG_catalog.json')

    p_list = sub.add_parser('list', help='List all universes (existing + new)')

    p_finger = sub.add_parser('fingerprints', help='Count unique fingerprints')

    args = parser.parse_args()
    catalog = load_catalog_dicts(extra_path=getattr(args, 'catalog', None))
    all_rs = list(RULESETS) + NEW_RULESETS
    new_rs = generate_expansion()
    combined = all_rs + new_rs

    if args.cmd == 'list' or args.cmd is None:
        print(f'═══ {len(combined)} Universes ({len(all_rs)} existing + {len(new_rs)} new) ═══')
        for i, r in enumerate(combined):
            gs = f'G1={r.g1.prim}≥{r.g1.min_ord} G2={r.g2.prim}≥{r.g2.min_ord} G3={r.g3.prim}≥{r.g3.min_ord}'
            ab = f' abs={len(r.absorption_rules)}' if len(r.absorption_rules) != 2 else ''
            marker = ' [NEW]' if i >= len(all_rs) else ''
            print(f'  {i+1:>2}. {r.name:<34} {gs} seq={r.gate_ordering}{ab}{marker}')

    elif args.cmd == 'generate':
        print(f'═══ {len(new_rs)} New Universes ═══')
        for r in new_rs:
            prof = universe_profile(r, catalog)
            print_profile(prof, verbose=False)
        print(f'\nTotal: {len(all_rs)} existing + {len(new_rs)} new = {len(combined)} universes')

    elif args.cmd == 'compare':
        profiles = [universe_profile(r, catalog) for r in combined]
        print(f'\n═══ {len(combined)} Universes — Comparison ═══\n')
        print_comparison(profiles)

    elif args.cmd == 'fingerprints':
        from collections import Counter
        fingerprints = []
        for r in combined:
            prof = universe_profile(r, catalog)
            ld = prof['layer_dist']
            fp = (ld['plain'], ld['frobenius'], ld['traced_monoidal'], ld['idempotent_terminal'])
            fingerprints.append((r.name, fp))
        fp_counts = Counter(fp for _, fp in fingerprints)
        print(f'═══ {len(combined)} Universes — {len(fp_counts)} Unique Fingerprints ═══')
        for (p, f, t, o), count in fp_counts.most_common():
            names = [name for name, fp in fingerprints if fp == (p, f, t, o)]
            print(f'  plain={p:>4} frob={f:>4} traced={t:>4} O∞={o:>4}  ×{count}  {", ".join(names[:5])}{"..." if len(names) > 5 else ""}')

if __name__ == '__main__':
    main()
