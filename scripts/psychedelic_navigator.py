#!/usr/bin/env python3
"""
Psychedelic Navigator — Navigatable/Operable Psychedelics Framework
====================================================================
Based on the Psychedelic Access Theorem and Operculum Peeling.

A compound accesses a universe U iff its type tau passes U's Ruleset gates.
Navigation: choose compound to access desired universe.
Operation: understand what structural transformations are available within an accessed universe.

Author: Lando⊗⊙perator
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).resolve().parent))

from imscrbgrmr.canonical_primitives import ORDINALS, CANONICAL_VALUES, PRIMITIVE_ORDER
from navigators.ruleset_universe import (
    RULESETS, Ruleset, GateSpec, AbsorptionRule,
    universe_profile, _T_CANONICAL, _T_STRUCTURAL
)

# ── Shavian glyph shorthand ─────────────────────────────────────
# For readability in tuple definitions
SH = {
    # Dimensionality
    "D_odot": "𐑦", "D_inf": "𐑼", "D_tri": "𐑨", "D_wedge": "𐑛",
    # Topology
    "T_odot": "𐑸", "T_net": "𐑡", "T_in": "𐑰", "T_bow": "𐑥", "T_box": "𐑶",
    # Relation
    "R_lr": "𐑾", "R_sup": "𐑩", "R_cat": "𐑑", "R_dag": "𐑽",
    # Parity
    "P_frob": "𐑹", "P_psi": "𐑿", "P_pm": "𐑬", "P_sym": "𐑯", "P_asym": "𐑗",
    # Fidelity
    "F_hbar": "𐑐", "F_ell": "𐑱", "F_eth": "𐑞",
    # Kinetics
    "K_slow": "𐑧", "K_mod": "𐑤", "K_fast": "𐑘", "K_trap_o": "𐑪", "K_mbl": "𐑺",
    # Scope
    "G_aleph": "𐑲", "G_beth": "𐑚", "G_gimel": "𐑔",
    # Composition
    "Gm_seq": "𐑠", "Gm_broad": "𐑵", "Gm_and": "𐑝", "Gm_or": "𐑜",
    # Criticality
    "⊙": "⊙", "𐑮": "𐑮", "𐑢": "𐑢", "Phi_ep": "𐑻", "Phi_super": "𐑣",
    # Chirality
    "H_inf": "𐑫", "H_2": "𐑖", "H_1": "𐑒", "H_0": "𐑓",
    # Stoichiometry
    "S_het": "𐑳", "S_many": "𐑕", "S_one": "𐑙",
    # Winding
    "W_Z": "𐑭", "W_Z2": "𐑴", "W_0": "𐑷", "W_NA": "𐑟",
}

# ── Psychedelic compound tuples (from Psychedelic Access Theorem) ─
# Full 12-primitive types assigned via Deterministic Imscribing Procedure
COMPOUNDS: Dict[str, Dict[str, str]] = {
    "5_meo_dmt": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_frob"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_inf"], "⊞": SH["S_het"], "◻": SH["W_Z"],
    },
    "dmt": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_frob"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_inf"], "⊞": SH["S_het"], "◻": SH["W_Z"],
    },
    "ayahuasca": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_psi"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_inf"], "⊞": SH["S_het"], "◻": SH["W_Z"],
    },
    "lsd": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_frob"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_2"], "⊞": SH["S_het"], "◻": SH["W_Z"],
    },
    "ibogaine": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_pm"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_inf"], "⊞": SH["S_het"], "◻": SH["W_Z"],
    },
    "psilocybin": {
        "⊢": SH["D_odot"], "⊣": SH["T_odot"], ">": SH["R_lr"],
        "<": SH["P_frob"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_broad"], "⊙": SH["⊙"],
        "⊥": SH["H_2"], "⊞": SH["S_het"], "◻": SH["W_Z2"],
    },
    "mescaline": {
        "⊢": SH["D_inf"], "⊣": SH["T_net"], ">": SH["R_lr"],
        "<": SH["P_pm"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_seq"], "⊙": SH["⊙"],
        "⊥": SH["H_1"], "⊞": SH["S_many"], "◻": SH["W_Z2"],
    },
    "salvinorin_a": {
        "⊢": SH["D_odot"], "⊣": SH["T_net"], ">": SH["R_lr"],
        "<": SH["P_psi"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_aleph"], "∋": SH["Gm_seq"], "⊙": SH["𐑮"],
        "⊥": SH["H_0"], "⊞": SH["S_many"], "◻": SH["W_0"],
    },
    "ketamine": {
        "⊢": SH["D_inf"], "⊣": SH["T_net"], ">": SH["R_lr"],
        "<": SH["P_psi"], "⋈": SH["F_hbar"], "⊤": SH["K_slow"],
        "∈": SH["G_gimel"], "∋": SH["Gm_or"], "⊙": SH["𐑢"],
        "⊥": SH["H_1"], "⊞": SH["S_one"], "◻": SH["W_Z2"],
    },
    "mdma": {
        "⊢": SH["D_tri"], "⊣": SH["T_net"], ">": SH["R_lr"],
        "<": SH["P_psi"], "⋈": SH["F_hbar"], "⊤": SH["K_fast"],
        "∈": SH["G_beth"], "∋": SH["Gm_seq"], "⊙": SH["𐑮"],
        "⊥": SH["H_1"], "⊞": SH["S_het"], "◻": SH["W_0"],
    },
    "cannabis": {
        "⊢": SH["D_tri"], "⊣": SH["T_net"], ">": SH["R_lr"],
        "<": SH["P_asym"], "⋈": SH["F_ell"], "⊤": SH["K_trap_o"],
        "∈": SH["G_gimel"], "∋": SH["Gm_or"], "⊙": SH["𐑢"],
        "⊥": SH["H_0"], "⊞": SH["S_many"], "◻": SH["W_0"],
    },
}

# Human-readable names
COMPOUND_NAMES = {
    "5_meo_dmt": "5-MeO-DMT",
    "dmt": "DMT",
    "ayahuasca": "Ayahuasca",
    "lsd": "LSD",
    "ibogaine": "Ibogaine",
    "psilocybin": "Psilocybin",
    "mescaline": "Mescaline",
    "salvinorin_a": "Salvinorin A",
    "ketamine": "Ketamine",
    "mdma": "MDMA",
    "cannabis": "Cannabis",
}

# Bottleneck primitive order
BOTTLENECKS = ["⊙", "⊥", "<", "◻"]

# ── Universe definitions for psychedelic access ──────────────────
# These are the 17 universes from the Psychedelic Access Theorem paper.
# They parameterize different gate/configurations relevant to psychedelic phenomenology.

def get_psychedelic_universes() -> List[Ruleset]:
    """Return all 17 universes used in the psychedelic access analysis."""
    from navigators.ruleset_universe import Ruleset, GateSpec
    
    universes = []
    
    # 0: chirality_first
    universes.append(Ruleset(
        name="chirality_first",
        description="Memory before closure. G1=Ħ≥𐑖, G2=⊙≥⊙, G3=Ω≥𐑭.",
        g1=GateSpec("⊥", 3.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 1: critical_first
    universes.append(Ruleset(
        name="critical_first",
        description="Self-modeling before structure. G1=⊙≥⊙, G2=Φ≥𐑹, G3=Ω≥𐑭.",
        g1=GateSpec("⊙", 2.0), g2=GateSpec("<", 5.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 2: winding_first
    universes.append(Ruleset(
        name="winding_first",
        description="Topological protection first. G1=Ω≥𐑭, G2=⊙≥⊙, G3=Φ≥𐑹.",
        g1=GateSpec("◻", 3.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("<", 5.0),
        gate_ordering=True,
    ))
    
    # 3: chirality_tight
    universes.append(Ruleset(
        name="chirality_tight",
        description="Requires eternal memory. G1=Ħ≥𐑫, G2=⊙≥⊙, G3=Ω≥𐑭.",
        g1=GateSpec("⊥", 4.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 4: critical_tight
    universes.append(Ruleset(
        name="critical_tight",
        description="Requires super-criticality. G1=⊙≥𐑣, G2=Φ≥𐑹, G3=Ω≥𐑭.",
        g1=GateSpec("⊙", 4.0), g2=GateSpec("<", 5.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 5: winding_tight
    universes.append(Ruleset(
        name="winding_tight",
        description="Requires integer winding strictly. G1=Ω≥𐑭, G2=⊙≥⊙, G3=Ħ≥𐑖.",
        g1=GateSpec("◻", 3.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("⊥", 3.0),
        gate_ordering=True,
    ))
    
    # 6: parity_hard
    universes.append(Ruleset(
        name="parity_hard",
        description="Requires Frobenius-special parity. G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ω≥𐑭.",
        g1=GateSpec("<", 5.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 7: chirality_mod
    universes.append(Ruleset(
        name="chirality_mod",
        description="Moderate chirality gate. G1=Ħ≥𐑒, G2=⊙≥⊙, G3=Ω≥𐑭.",
        g1=GateSpec("⊥", 2.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 8: protection_weak
    universes.append(Ruleset(
        name="protection_weak",
        description="Weak protection. G1=Ω≥𐑴, G2=⊙≥⊙, G3=Φ≥𐑿.",
        g1=GateSpec("◻", 2.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("<", 2.0),
        gate_ordering=True,
    ))
    
    # 9: psi_parity
    universes.append(Ruleset(
        name="psi_parity",
        description="Quantum parity gate. G1=Φ≥𐑿, G2=⊙≥⊙, G3=Ω≥𐑴.",
        g1=GateSpec("<", 2.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 2.0),
        gate_ordering=True,
    ))
    
    # 10: dual_gate
    universes.append(Ruleset(
        name="dual_gate",
        description="Dual criticality+chirality. G1=⊙≥⊙, G2=Ħ≥𐑖, G3=Ω≥𐑭.",
        g1=GateSpec("⊙", 2.0), g2=GateSpec("⊥", 3.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 11: slow_only
    universes.append(Ruleset(
        name="slow_only",
        description="Slowness is everything. G1=Ç≥𐑧, G2=⊙≥⊙, G3=Ω≥𐑭.",
        g1=GateSpec("⊤", 3.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 3.0),
        gate_ordering=True,
    ))
    
    # 12: memory_free
    universes.append(Ruleset(
        name="memory_free",
        description="Memoryless gate with criticality. G1=Ħ≥𐑒, G2=⊙≥⊙, G3=Ω≥𐑴.",
        g1=GateSpec("⊥", 2.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 2.0),
        gate_ordering=True,
    ))
    
    # 13: binary_only
    universes.append(Ruleset(
        name="binary_only",
        description="Z2 protection gate. G1=Ω≥𐑴, G2=⊙≥⊙, G3=Φ≥𐑿.",
        g1=GateSpec("◻", 2.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("<", 2.0),
        gate_ordering=True,
    ))
    
    # 14: quantum_only
    universes.append(Ruleset(
        name="quantum_only",
        description="Quantum fidelity gate. G1=ƒ≥𐑐, G2=⊙≥⊙, G3=Ω≥𐑴.",
        g1=GateSpec("⋈", 3.0), g2=GateSpec("⊙", 2.0), g3=GateSpec("◻", 2.0),
        gate_ordering=True,
    ))
    
    # 15: one_gate
    universes.append(Ruleset(
        name="one_gate",
        description="Single gate: criticality only. G1=⊙≥⊙, G2=Σ≥𐑙, G3=Σ≥𐑙.",
        g1=GateSpec("⊙", 2.0), g2=GateSpec("⊞", 1.0), g3=GateSpec("⊞", 1.0),
        gate_ordering=True,
    ))
    
    # 16: null_universe
    universes.append(Ruleset(
        name="null_universe",
        description="Maximal permissiveness. G1=Σ≥𐑙, G2=Σ≥𐑙, G3=Σ≥𐑙.",
        g1=GateSpec("⊞", 1.0), g2=GateSpec("⊞", 1.0), g3=GateSpec("⊞", 1.0),
        gate_ordering=True,
    ))
    
    return universes

# ── Access computation ───────────────────────────────────────────

def get_ordinal(primitive: str, value: str) -> float:
    """Get the ordinal value for a primitive-value pair."""
    return ORDINALS.get(primitive, {}).get(value, 0.0)

def check_gate(compound: Dict[str, str], gate: GateSpec) -> bool:
    """Check if a compound passes a single gate."""
    if gate is None:
        return True
    val = compound.get(gate.prim, None)
    if val is None:
        return False
    return get_ordinal(gate.prim, val) >= gate.min_ord

def compute_access(compound: Dict[str, str], universe: Ruleset) -> Tuple[bool, str]:
    """Compute whether a compound accesses a universe. Returns (accessed, layer)."""
    g1_pass = check_gate(compound, universe.g1)
    g2_pass = check_gate(compound, universe.g2)
    g3_pass = check_gate(compound, universe.g3)
    
    if universe.gate_ordering:
        if g1_pass and g2_pass and g3_pass:
            return (True, "idempotent_terminal")
        elif g1_pass and g2_pass:
            return (True, "traced_monoidal")
        elif g1_pass:
            return (True, "frobenius")
        else:
            return (False, "plain")
    else:
        count = sum([g1_pass, g2_pass, g3_pass])
        if count == 3:
            return (True, "idempotent_terminal")
        elif count >= 2:
            return (True, "traced_monoidal")
        elif count >= 1:
            return (True, "frobenius")
        else:
            return (False, "plain")

def build_access_matrix(compounds, universes):
    """Build the full compound x universe access matrix."""
    matrix = {}
    for cname, ctuple in compounds.items():
        matrix[cname] = {}
        for u in universes:
            accessed, layer = compute_access(ctuple, u)
            matrix[cname][u.name] = accessed
    return matrix

def count_accesses(compound, universes):
    """Count how many universes a compound accesses at idempotent_terminal."""
    count = 0
    for u in universes:
        accessed, layer = compute_access(compound, u)
        if accessed and layer == "idempotent_terminal":
            count += 1
    return count


# ── Navigation ───────────────────────────────────────────────────

def navigate_to_universe(target_universe, compounds, universes):
    """Find which compounds grant access to a target universe."""
    results = []
    target_u = next((u for u in universes if u.name == target_universe), None)
    if target_u is None:
        return results
    layer_order = {"idempotent_terminal": 0, "traced_monoidal": 1, "frobenius": 2}
    for cname, ctuple in compounds.items():
        accessed, layer = compute_access(ctuple, target_u)
        if accessed:
            results.append((cname, layer))
    results.sort(key=lambda x: layer_order.get(x[1], 99))
    return results

def navigate_by_properties(required_primitives, compounds, universes):
    """Find compounds matching specific primitive requirements."""
    matches = {}
    for cname, ctuple in compounds.items():
        if all(ctuple.get(p) == v for p, v in required_primitives.items()):
            access_list = []
            for u in universes:
                accessed, layer = compute_access(ctuple, u)
                if accessed and layer == "idempotent_terminal":
                    access_list.append(u.name)
            matches[cname] = {
                "name": COMPOUND_NAMES.get(cname, cname),
                "bottlenecks": {p: ctuple[p] for p in BOTTLENECKS},
                "accesses": len(access_list),
                "universes": access_list,
            }
    return matches


# ── Operation: what can you DO in an accessed universe? ──────────

def universe_operations(universe):
    """Describe structural operations available in a universe."""
    ops = {
        "name": universe.name,
        "description": universe.description,
        "gate_structure": {
            "G1": f"{universe.g1.prim} >= ord {universe.g1.min_ord}" if universe.g1 else "none",
            "G2": f"{universe.g2.prim} >= ord {universe.g2.min_ord}" if universe.g2 else "none",
            "G3": f"{universe.g3.prim} >= ord {universe.g3.min_ord}" if universe.g3 else "none",
            "ordered": universe.gate_ordering,
        },
        "absorption_rules": [
            {"primitive": r.primitive, "value": r.value, "operations": r.operations,
             "direction": getattr(r, 'direction', 'symmetric')}
            for r in universe.absorption_rules
        ] if universe.absorption_rules else [],
        "t_constitution": list(universe.t_prims.keys()) if universe.t_prims else ["canonical"],
        "structural_capabilities": [],
    }
    
    g1_prim = universe.g1.prim if universe.g1 else None
    caps = {
        "⊥": ["memory_anchored: temporal self-reference is the entry condition",
              "narrative_coherence: experience structured as temporally extended"],
        "⊙": ["self_modeling_primary: self-model is the fundamental operation",
              "non_dual_available: subject-object distinction can collapse"],
        "<": ["symmetry_governed: parity structure determines all downstream access",
              "closure_primary: Frobenius closure is the entry ticket"],
        "◻": ["topology_protected: winding number is the primary invariant",
              "phase_coherence: topological protection ensures phase stability"],
        "⋈": ["quantum_coherence_required: classical states cannot enter"],
        "⊤": ["temporal_patience: only slow processes can operate"],
    }
    if g1_prim in caps:
        ops["structural_capabilities"].extend(caps[g1_prim])
    
    if not universe.absorption_rules:
        ops["structural_capabilities"].append("democratic_coupling: all primitives equal under tensor/meet/join")
    else:
        for r in universe.absorption_rules:
            ops["structural_capabilities"].append(
                f"absorption_{r.primitive}={r.value}: absorbs under {r.operations}"
            )
    return ops

# ── Tensor (combinations) ────────────────────────────────────────

def tensor_tuples(t1: Dict[str, str], t2: Dict[str, str]) -> Dict[str, str]:
    """Compute the tensor product of two tuples. Rule: max on most primitives, min on Phi and F."""
    result = {}
    for p in PRIMITIVE_ORDER:
        v1 = t1.get(p)
        v2 = t2.get(p)
        if v1 is None:
            result[p] = v2
        elif v2 is None:
            result[p] = v1
        elif p in ("<", "⋈"):
            o1 = get_ordinal(p, v1)
            o2 = get_ordinal(p, v2)
            result[p] = v1 if o1 <= o2 else v2
        else:
            o1 = get_ordinal(p, v1)
            o2 = get_ordinal(p, v2)
            result[p] = v1 if o1 >= o2 else v2
    return result

def predict_combination(c1_key, c2_key, compounds, universes):
    """Predict access profile of a psychedelic combination."""
    if c1_key not in compounds or c2_key not in compounds:
        return {"error": f"Unknown compound: {c1_key if c1_key not in compounds else c2_key}"}
    t1 = compounds[c1_key]
    t2 = compounds[c2_key]
    tensor_tuple = tensor_tuples(t1, t2)
    access_list = []
    for u in universes:
        accessed, layer = compute_access(tensor_tuple, u)
        if accessed and layer == "idempotent_terminal":
            access_list.append(u.name)
    c1_set = set()
    c2_set = set()
    for u in universes:
        a1, l1 = compute_access(t1, u)
        a2, l2 = compute_access(t2, u)
        if a1 and l1 == "idempotent_terminal":
            c1_set.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            c2_set.add(u.name)
    combo_set = set(access_list)
    return {
        "combination": f"{COMPOUND_NAMES[c1_key]} + {COMPOUND_NAMES[c2_key]}",
        "tensor_bottlenecks": {p: tensor_tuple[p] for p in BOTTLENECKS},
        "access_count": len(access_list),
        "universes": sorted(access_list),
        "c1_access": len(c1_set),
        "c2_access": len(c2_set),
        "gained_vs_c1": sorted(combo_set - c1_set),
        "lost_vs_c1": sorted(c1_set - combo_set),
        "gained_vs_c2": sorted(combo_set - c2_set),
        "lost_vs_c2": sorted(c2_set - combo_set),
        "c1_only": sorted(c1_set - c2_set),
        "c2_only": sorted(c2_set - c1_set),
        "shared": sorted(c1_set & c2_set),
    }

# ── Tier assignment ──────────────────────────────────────────────

def assign_tier(compound):
    """Assign ouroboricity tier based on bottleneck primitives."""
    o_phi = get_ordinal("⊙", compound.get("⊙", ""))
    o_h = get_ordinal("⊥", compound.get("⊥", ""))
    o_p = get_ordinal("<", compound.get("<", ""))
    o_omega = get_ordinal("◻", compound.get("◻", ""))
    if o_phi >= 2 and o_h >= 3 and o_p >= 5 and o_omega >= 3:
        return "O_∞"
    elif o_phi >= 2 and o_h >= 2 and o_p >= 5 and o_omega >= 2:
        return "O_2_dagger"
    elif o_phi >= 2 and o_h >= 1 and o_p >= 2 and o_omega >= 2:
        return "O₂"
    elif o_phi >= 1 and o_h >= 1 and o_p >= 1 and o_omega >= 1:
        return "O₁"
    else:
        return "O₀"

# ── Display ──────────────────────────────────────────────────────

def print_access_table(compounds, universes):
    """Print formatted access matrix."""
    cnames = ["5_meo_dmt", "dmt", "ayahuasca", "lsd", "ibogaine",
              "psilocybin", "mescaline", "salvinorin_a", "ketamine",
              "mdma", "cannabis"]
    print(f"{'Compound':<16}", end="")
    for u in universes:
        print(f" {u.name[:14]:>14}", end="")
    print(f" {'Total':>6}  {'Tier':<12}")
    print("-" * (16 + 16 * len(universes) + 20))
    for cname in cnames:
        ctuple = compounds.get(cname)
        if ctuple is None:
            continue
        name = COMPOUND_NAMES.get(cname, cname)
        print(f"{name:<16}", end="")
        total = 0
        for u in universes:
            accessed, layer = compute_access(ctuple, u)
            if accessed and layer == "idempotent_terminal":
                print(f" {'YES':>14}", end="")
                total += 1
            else:
                print(f" {'--':>14}", end="")
        tier = assign_tier(ctuple)
        print(f" {total:>6}  {tier:<12}")
    print()

def show_compound_detail(cname, compounds, universes):
    """Show full structural details for a compound."""
    if cname not in compounds:
        return f"Unknown: {cname}"
    ctuple = compounds[cname]
    tier = assign_tier(ctuple)
    accesses = count_accesses(ctuple, universes)
    access_list = []
    for u in universes:
        a, l = compute_access(ctuple, u)
        if a and l == "idempotent_terminal":
            access_list.append(u.name)
    lines = [
        f"COMPOUND: {COMPOUND_NAMES.get(cname, cname)} ({cname})",
        f"Tier: {tier}",
        f"Universes accessed: {accesses}/17",
        f"Bottleneck primitives:",
    ]
    for p in BOTTLENECKS:
        lines.append(f"  {p} = {ctuple.get(p, '?')}")
    lines.append("Full tuple:")
    for p in PRIMITIVE_ORDER:
        lines.append(f"  {p} = {ctuple.get(p, '?')}")
    lines.append(f"Accessed universes: {', '.join(sorted(access_list))}")
    return "\n".join(lines)

# ── Main CLI ─────────────────────────────────────────────────────

def main():
    compounds = COMPOUNDS
    universes = get_psychedelic_universes()
    if len(sys.argv) < 2:
        print("=" * 70)
        print("  PSYCHEDELIC NAVIGATOR — Navigatable/Operable Psychedelics")
        print("  Psychedelic Access Theorem + Operculum Peeling Synthesis")
        print("=" * 70)
        print()
        print_access_table(compounds, universes)
        print("Commands: table | navigate U | operate U | combine C1 C2 | find K=V | universes | compound C")
        return
    cmd = sys.argv[1]
    if cmd == "table":
        print_access_table(compounds, universes)
    elif cmd == "navigate" and len(sys.argv) >= 3:
        target = sys.argv[2]
        results = navigate_to_universe(target, compounds, universes)
        print(f"\nUniverse: {target}")
        if not results:
            print("  NO COMPOUND ACCESSES THIS UNIVERSE.")
        for cname, layer in results:
            print(f"  {COMPOUND_NAMES.get(cname, cname):<16} [{layer}]")
    elif cmd == "operate" and len(sys.argv) >= 3:
        target = sys.argv[2]
        u = next((u for u in universes if u.name == target), None)
        if u is None:
            print(f"Unknown universe: {target}")
        else:
            import json as _json
            print(_json.dumps(universe_operations(u), indent=2))
    elif cmd == "combine" and len(sys.argv) >= 4:
        import json as _json
        result = predict_combination(sys.argv[2], sys.argv[3], compounds, universes)
        print(_json.dumps(result, indent=2))
    elif cmd == "find":
        required = {}
        for arg in sys.argv[2:]:
            if "=" in arg:
                p, v = arg.split("=", 1)
                required[p] = v
        matches = navigate_by_properties(required, compounds, universes)
        if not matches:
            print("No compounds matching:", required)
        for cname, info in matches.items():
            print(f"\n{info['name']} ({cname}): tier info['bottlenecks'], {info['accesses']} accesses")
    elif cmd == "universes":
        for i, u in enumerate(universes):
            g1_s = f"{u.g1.prim}>={u.g1.min_ord}" if u.g1 else "-"
            print(f"  [{i:2d}] {u.name:<24s} G1={g1_s}")
    elif cmd == "compound" and len(sys.argv) >= 3:
        print(show_compound_detail(sys.argv[2], compounds, universes))
    else:
        print(f"Unknown: {cmd}")

if __name__ == "__main__":
    main()
