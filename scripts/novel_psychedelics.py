#!/usr/bin/env python3
"""
Novel Psychedelics Extension — 5 Novel Compounds + Operable Control Methods
============================================================================
Extends psychedelic_navigator.py with structurally novel psychedelic compounds
that lie outside the known parameter space, plus six operable control methods
for active modulation of phenomenological access.

Novel compounds: Verticullum (EP-Lever), Chimerium (Supercritical),
Apertix (Adjoint Corridor), Retiarius (Local-Net Trap), Praxeum (EP-Core Platform).

Control methods: EP Gate Toggle, Chirality Ladder, Winding Modulation,
Scope Focusing, Adjoint Steering, Supercritical Launch.

Author: Lando⊗⊙perator
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

# Import from parent psychedelic_navigator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from psychedelic_navigator import (
    COMPOUNDS, COMPOUND_NAMES, BOTTLENECKS,
    compute_access, get_psychedelic_universes,
    tensor_tuples, get_ordinal, predict_combination,
    ORDINALS, PRIMITIVE_ORDER, check_gate, assign_tier,
)

# ─────────────────────────────────────────────────────────────────
# 1. NOVEL COMPOUNDS
# ─────────────────────────────────────────────────────────────────

NOVEL_COMPOUNDS: Dict[str, Dict[str, str]] = {
    "verticullum": {
        "⊢": "𐑦", "⊣": "𐑥", "≻": "𐑾", "≺": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑠", "⊙": "⊙", "⊥": "𐑫",
        "⊞": "𐑳", "⊡": "𐑟",
    },
    "chimerium": {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑾", "≺": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑵", "⊙": "𐑣", "⊥": "𐑫",
        "⊞": "𐑳", "⊡": "𐑭",
    },
    "apertix": {
        "⊢": "𐑦", "⊣": "𐑥", "≻": "𐑽", "≺": "𐑬", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑠", "⊙": "⊙", "⊥": "𐑖",
        "⊞": "𐑳", "⊡": "𐑴",
    },
    "retiarius": {
        "⊢": "𐑼", "⊣": "𐑡", "≻": "𐑾", "≺": "𐑿", "⋈": "𐑞",
        "⊤": "𐑺", "∈": "𐑚", "∋": "𐑜", "⊙": "𐑮", "⊥": "𐑒",
        "⊞": "𐑕", "⊡": "𐑷",
    },
    "praxeum": {
        "⊢": "𐑦", "⊣": "𐑶", "≻": "𐑾", "≺": "𐑹", "⋈": "𐑐",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑠", "⊙": "𐑻", "⊥": "𐑫",
        "⊞": "𐑳", "⊡": "𐑭",
    },
}

NOVEL_NAMES: Dict[str, str] = {
    "verticullum": "Verticullum (EP-Lever)",
    "chimerium": "Chimerium (Supercritical)",
    "apertix": "Apertix (Adjoint Corridor)",
    "retiarius": "Retiarius (Local-Net Trap)",
    "praxeum": "Praxeum (EP-Core Platform)",
}
# ─────────────────────────────────────────────────────────────────
# Merged compound dicts for unified access
# ─────────────────────────────────────────────────────────────────

def all_compounds() -> Dict[str, Dict[str, str]]:
    """Return the unified compound dictionary (existing + novel)."""
    merged = dict(COMPOUNDS)
    merged.update(NOVEL_COMPOUNDS)
    return merged

def all_names() -> Dict[str, str]:
    """Return the unified name dictionary."""
    merged = dict(COMPOUND_NAMES)
    merged.update(NOVEL_NAMES)
    return merged


# ─────────────────────────────────────────────────────────────────
# 2. OPERABLE CONTROL METHODS
# ─────────────────────────────────────────────────────────────────

# 2.1 EP Gate Toggle — ⊗(⊙, 𐑻) = 𐑻
# When Praxeum (<=𐑻) couples with any ⊙-critical compound,
# the composite falls to EP, closing Gate 1 (self-modeling).

def ep_gate_toggle(compound_key: str, ep_ratio: float = 0.5) -> dict:
    """Compute the tensor of a compound with Praxeum at a given ratio.

    Praxeum (<=𐑻) absorbs ⊙ under tensor: ⊗(⊙, 𐑻) = 𐑻.
    This is a controllable OFF switch for self-modeling.

    Args:
        compound_key: Base compound to couple with Praxeum.
        ep_ratio: Weight of Praxeum in the coupling (0.0–1.0).

    Returns:
        Dict with composite tuple, access change, and Gate 1 status.
    """
    compounds = all_compounds()
    names = all_names()

    if compound_key not in compounds:
        return {"error": f"Unknown compound: {compound_key}"}
    if "praxeum" not in compounds:
        return {"error": "Praxeum not available"}

    base = compounds[compound_key]
    praxeum = compounds["praxeum"]

    # Tensor coupling (EP absorption rule: ⊗(⊙,𐑻) = 𐑻)
    composite = tensor_tuples(base, praxeum)

    # Check Gate 1: ⊙ is self-modeling
    base_phi = base.get("⊙", "")
    comp_phi = composite.get("⊙", "")

    gate1_open_before = get_ordinal("⊙", base_phi) >= get_ordinal("⊙", "⊙")
    gate1_open_after = get_ordinal("⊙", comp_phi) >= get_ordinal("⊙", "⊙")

    universes = get_psychedelic_universes()
    base_access = set()
    comp_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(composite, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            comp_access.add(u.name)

    return {
        "method": "ep_gate_toggle",
        "base_compound": names.get(compound_key, compound_key),
        "ep_coupling": names.get("praxeum", "Praxeum"),
        "ep_ratio": ep_ratio,
        "composite_phi": comp_phi,
        "gate1_open_before": gate1_open_before,
        "gate1_open_after": gate1_open_after,
        "self_modeling_disabled": gate1_open_before and not gate1_open_after,
        "composite_bottlenecks": {p: composite[p] for p in BOTTLENECKS},
        "base_access_count": len(base_access),
        "composite_access_count": len(comp_access),
        "access_lost": sorted(base_access - comp_access),
        "access_gained": sorted(comp_access - base_access),
        "base_universes": sorted(base_access),
        "composite_universes": sorted(comp_access),
    }
# 2.2 Chirality Ladder
# Step through ⊥ values by coupling with compounds at different chirality levels.

CHIRALITY_ANCHORS = {
    "𐑓": {"name": "H0 (memoryless)", "ordinal": 1, "exemplar": "salvinorin_a"},
    "𐑒": {"name": "H1 (one-step)", "ordinal": 2, "exemplar": "mescaline"},
    "𐑖": {"name": "H2 (two-step)", "ordinal": 3, "exemplar": "apertix"},
    "𐑫": {"name": "H_inf (eternal)", "ordinal": 4, "exemplar": "5_meo_dmt"},
}

def chirality_ladder(compound_key: str, target_h: str) -> dict:
    """Compute minimal primitive changes to reach target chirality.

    Target chirality values:
      𐑓 (H0) — memoryless, for transient states
      𐑒 (H1) — one-step, for immediate context
      𐑖 (H2) — two-step, for narrative coherence
      𐑫 (H_inf) — eternal, for full self-reference
    """
    compounds = all_compounds()
    names = all_names()

    if compound_key not in compounds:
        return {"error": f"Unknown compound: {compound_key}"}
    if target_h not in CHIRALITY_ANCHORS:
        return {"error": f"Unknown target chirality: {target_h}. Use: {list(CHIRALITY_ANCHORS.keys())}"}

    base = compounds[compound_key]
    current_h = base.get("⊥", "")
    current_ord = get_ordinal("⊥", current_h)
    target_ord = get_ordinal("⊥", target_h)

    modified = dict(base)
    modified["⊥"] = target_h

    anchor_info = CHIRALITY_ANCHORS[target_h]

    universes = get_psychedelic_universes()
    base_access = set()
    mod_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(modified, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            mod_access.add(u.name)

    return {
        "method": "chirality_ladder",
        "compound": names.get(compound_key, compound_key),
        "current_h": current_h,
        "current_h_name": CHIRALITY_ANCHORS.get(current_h, {}).get("name", "unknown"),
        "target_h": target_h,
        "target_h_name": anchor_info["name"],
        "ordinal_delta": target_ord - current_ord,
        "direction": "up" if target_ord > current_ord else "down" if target_ord < current_ord else "same",
        "modified_bottlenecks": {p: modified[p] for p in BOTTLENECKS},
        "base_tier": assign_tier(base),
        "modified_tier": assign_tier(modified),
        "base_access_count": len(base_access),
        "modified_access_count": len(mod_access),
        "access_lost": sorted(base_access - mod_access),
        "access_gained": sorted(mod_access - base_access),
        "base_universes": sorted(base_access),
        "modified_universes": sorted(mod_access),
    }

WINDING_LEVELS = {
    "𐑷": {"name": "W0 (no protection)", "ordinal": 1, "description": "Fully permeable, no topological barrier"},
    "𐑴": {"name": "W_Z2 (binary protection)", "ordinal": 2, "description": "Z2 parity-protected"},
    "𐑭": {"name": "W_Z (integer winding)", "ordinal": 3, "description": "Full integer winding protection"},
    "𐑟": {"name": "W_NA (non-Abelian)", "ordinal": 4, "description": "Non-Abelian braiding; requires D=𐑦"},
}


# 2.3 Winding Modulation
def winding_modulate(compound_key: str, target_w: str) -> dict:
    """Predict access changes from winding modulation.

    Target winding values:
      𐑷 (W0) — no protection, fully permeable
      𐑴 (W_Z2) — binary protection
      𐑭 (W_Z) — integer winding, full protection
      𐑟 (W_NA) — non-Abelian braiding
    """
    compounds = all_compounds()
    names = all_names()

    if compound_key not in compounds:
        return {"error": f"Unknown compound: {compound_key}"}
    if target_w not in WINDING_LEVELS:
        return {"error": f"Unknown target winding: {target_w}. Use: {list(WINDING_LEVELS.keys())}"}

    base = compounds[compound_key]
    current_w = base.get("⊡", "")
    current_ord = get_ordinal("⊡", current_w)
    target_ord = get_ordinal("⊡", target_w)

    # Non-Abelian requires D=𐑦
    if target_w == "𐑟" and base.get("⊢") != "𐑦":
        return {
            "error": "Non-Abelian winding (𐑟) requires D=𐑦 (self-written dimensionalty).",
            "current_d": base.get("⊢", ""),
            "required_d": "𐑦",
        }

    modified = dict(base)
    modified["⊡"] = target_w

    universes = get_psychedelic_universes()
    base_access = set()
    mod_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(modified, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            mod_access.add(u.name)

    return {
        "method": "winding_modulate",
        "compound": names.get(compound_key, compound_key),
        "current_w": current_w,
        "current_w_name": WINDING_LEVELS.get(current_w, {}).get("name", "unknown"),
        "target_w": target_w,
        "target_w_name": WINDING_LEVELS[target_w]["name"],
        "ordinal_delta": target_ord - current_ord,
        "direction": "up" if target_ord > current_ord else "down" if target_ord < current_ord else "same",
        "modified_bottlenecks": {p: modified[p] for p in BOTTLENECKS},
        "base_tier": assign_tier(base),
        "modified_tier": assign_tier(modified),
        "base_access_count": len(base_access),
        "modified_access_count": len(mod_access),
        "access_lost": sorted(base_access - mod_access),
        "access_gained": sorted(mod_access - base_access),
    }

SCOPE_LEVELS = {
    "𐑚": {"name": "Beth (nearest-neighbor)", "ordinal": 1, "description": "Local interactions only"},
    "𐑔": {"name": "Gimel (mesoscale)", "ordinal": 2, "description": "Intermediate range"},
    "𐑲": {"name": "Aleph (universal)", "ordinal": 3, "description": "Long-range / universal scope"},
}


# 2.4 Scope Focusing
def scope_focus(compound_key: str, target_g: str) -> dict:
    """Predict access changes from scope modulation.

    Target scope values:
      𐑚 (Beth) — nearest-neighbor / local
      𐑔 (Gimel) — mesoscale
      𐑲 (Aleph) — universal / long-range
    """
    compounds = all_compounds()
    names = all_names()

    if compound_key not in compounds:
        return {"error": f"Unknown compound: {compound_key}"}
    if target_g not in SCOPE_LEVELS:
        return {"error": f"Unknown target scope: {target_g}. Use: {list(SCOPE_LEVELS.keys())}"}

    base = compounds[compound_key]
    current_g = base.get("∈", "")
    current_ord = get_ordinal("∈", current_g)
    target_ord = get_ordinal("∈", target_g)

    modified = dict(base)
    modified["∈"] = target_g

    universes = get_psychedelic_universes()
    base_access = set()
    mod_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(modified, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            mod_access.add(u.name)

    return {
        "method": "scope_focus",
        "compound": names.get(compound_key, compound_key),
        "current_scope": current_g,
        "current_scope_name": SCOPE_LEVELS.get(current_g, {}).get("name", "unknown"),
        "target_scope": target_g,
        "target_scope_name": SCOPE_LEVELS[target_g]["name"],
        "ordinal_delta": target_ord - current_ord,
        "direction": "up" if target_ord > current_ord else "down" if target_ord < current_ord else "same",
        "modified_bottlenecks": {p: modified[p] for p in BOTTLENECKS},
        "base_tier": assign_tier(base),
        "modified_tier": assign_tier(modified),
        "base_access_count": len(base_access),
        "modified_access_count": len(mod_access),
        "access_lost": sorted(base_access - mod_access),
        "access_gained": sorted(mod_access - base_access),
    }
# 2.5 Adjoint Steering
# Use R=𐑽 (adjoint/dagger) for directed experience vectors.
# The adjoint maps one-way — a lossy but steerable transformation.

def adjoint_steer(compound_key: str, direction_primitive: str, target_value: str) -> dict:
    """Compute the adjoint-mapped access profile for a directed change.

    The adjoint coupling (>=𐑽) is one-way: it funnels the experience vector
    in a specific direction. This method modifies a single primitive to its
    target value and computes the predicted access shift.

    Args:
        compound_key: Base compound.
        direction_primitive: Which primitive to steer (e.g., "⊙", "⊥", "≺").
        target_value: The target glyph for that primitive.
    """
    compounds = all_compounds()
    names = all_names()

    if compound_key not in compounds:
        return {"error": f"Unknown compound: {compound_key}"}

    base = compounds[compound_key]
    current_value = base.get(direction_primitive, "")

    if direction_primitive not in PRIMITIVE_ORDER:
        return {"error": f"Unknown primitive: {direction_primitive}. Valid: {PRIMITIVE_ORDER}"}

    # Validate target_value is canonical
    from imscrbgrmr.canonical_primitives import CANONICAL_VALUES
    canonical = CANONICAL_VALUES.get(direction_primitive, [])
    if target_value not in canonical:
        return {
            "error": f"Invalid target value '{target_value}' for {direction_primitive}.",
            "canonical_values": canonical,
        }

    modified = dict(base)
    modified[direction_primitive] = target_value
    # Set coupling to adjoint to indicate directed steering
    modified["≻"] = "𐑽"

    universes = get_psychedelic_universes()
    base_access = set()
    mod_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(modified, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            mod_access.add(u.name)

    current_ord = get_ordinal(direction_primitive, current_value)
    target_ord = get_ordinal(direction_primitive, target_value)

    return {
        "method": "adjoint_steer",
        "compound": names.get(compound_key, compound_key),
        "steered_primitive": direction_primitive,
        "current_value": current_value,
        "current_ordinal": current_ord,
        "target_value": target_value,
        "target_ordinal": target_ord,
        "ordinal_delta": target_ord - current_ord,
        "coupling_set_to": "𐑽 (adjoint)",
        "modified_bottlenecks": {p: modified[p] for p in BOTTLENECKS},
        "base_tier": assign_tier(base),
        "modified_tier": assign_tier(modified),
        "base_access_count": len(base_access),
        "modified_access_count": len(mod_access),
        "access_lost": sorted(base_access - mod_access),
        "access_gained": sorted(mod_access - base_access),
        "base_universes": sorted(base_access),
        "modified_universes": sorted(mod_access),
    }
# 2.6 Supercritical Launch
# Compute what happens when Chimerium (⊙=𐑣) is introduced.
# Supercriticality is runaway/chaotic: it amplifies all bottlenecks.

def supercritical_launch(base_compound_key: str) -> dict:
    """Predict the tensor profile of base compound + Chimerium.

    Chimerium (⊙=𐑣, supercritical) amplifies the criticality of any
    compound it couples with. Under tensor (max rule), the composite
    inherits the higher criticality. This can push sub-critical or
    critical compounds into supercritical territory, potentially
    unlocking access to universes gated on ⊙≥𐑣.

    Returns the full access delta and risk assessment.
    """
    compounds = all_compounds()
    names = all_names()

    if base_compound_key not in compounds:
        return {"error": f"Unknown compound: {base_compound_key}"}
    if "chimerium" not in compounds:
        return {"error": "Chimerium not available"}

    base = compounds[base_compound_key]
    chimerium = compounds["chimerium"]

    composite = tensor_tuples(base, chimerium)

    universes = get_psychedelic_universes()
    base_access = set()
    comp_access = set()
    for u in universes:
        a1, l1 = compute_access(base, u)
        a2, l2 = compute_access(composite, u)
        if a1 and l1 == "idempotent_terminal":
            base_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            comp_access.add(u.name)

    # Risk assessment based on composite ⊙ value
    comp_phi = composite.get("⊙", "")
    if comp_phi == "𐑣":
        risk = "HIGH — supercritical launch active; runaway dynamics possible"
    elif comp_phi == "𐑻":
        risk = "MODERATE — EP boundary reached; self-modeling may be unstable"
    elif comp_phi == "⊙":
        risk = "LOW — criticality stabilized at self-modeling"
    else:
        risk = "MINIMAL — below critical threshold"

    return {
        "method": "supercritical_launch",
        "base_compound": names.get(base_compound_key, base_compound_key),
        "catalyst": names.get("chimerium", "Chimerium"),
        "composite_phi": comp_phi,
        "composite_bottlenecks": {p: composite[p] for p in BOTTLENECKS},
        "base_tier": assign_tier(base),
        "composite_tier": assign_tier(composite),
        "risk_assessment": risk,
        "base_access_count": len(base_access),
        "composite_access_count": len(comp_access),
        "access_lost": sorted(base_access - comp_access),
        "access_gained": sorted(comp_access - base_access),
        "base_universes": sorted(base_access),
        "composite_universes": sorted(comp_access),
        "chimerium_profile": {
            "phi": chimerium.get("⊙", ""),
            "h": chimerium.get("⊥", ""),
            "omega": chimerium.get("⊡", ""),
            "tier": assign_tier(chimerium),
        },
    }
# ─────────────────────────────────────────────────────────────────
# 3. EXTENDED TENSOR & REGION SEARCH
# ─────────────────────────────────────────────────────────────────

def tensor_compute(c1_key: str, c2_key: str) -> dict:
    """Extended tensor computation including novel compounds."""
    compounds = all_compounds()
    names = all_names()

    if c1_key not in compounds:
        return {"error": f"Unknown compound: {c1_key}"}
    if c2_key not in compounds:
        return {"error": f"Unknown compound: {c2_key}"}

    t1 = compounds[c1_key]
    t2 = compounds[c2_key]
    composite = tensor_tuples(t1, t2)

    universes = get_psychedelic_universes()
    c1_access = set()
    c2_access = set()
    comp_access = set()
    for u in universes:
        a1, l1 = compute_access(t1, u)
        a2, l2 = compute_access(t2, u)
        ac, lc = compute_access(composite, u)
        if a1 and l1 == "idempotent_terminal":
            c1_access.add(u.name)
        if a2 and l2 == "idempotent_terminal":
            c2_access.add(u.name)
        if ac and lc == "idempotent_terminal":
            comp_access.add(u.name)

    combo_set = comp_access

    return {
        "combination": f"{names[c1_key]} ⊗ {names[c2_key]}",
        "c1": c1_key,
        "c2": c2_key,
        "c1_tier": assign_tier(t1),
        "c2_tier": assign_tier(t2),
        "composite_tier": assign_tier(composite),
        "tensor_bottlenecks": {p: composite[p] for p in BOTTLENECKS},
        "composite_tuple": {p: composite[p] for p in PRIMITIVE_ORDER},
        "access_count": len(comp_access),
        "universes": sorted(comp_access),
        "c1_access_count": len(c1_access),
        "c2_access_count": len(c2_access),
        "gained_vs_c1": sorted(combo_set - c1_access),
        "lost_vs_c1": sorted(c1_access - combo_set),
        "gained_vs_c2": sorted(combo_set - c2_access),
        "lost_vs_c2": sorted(c2_access - combo_set),
    }


def region_search(primitive: str, value: str) -> dict:
    """Find all compounds (novel + existing) matching a primitive=value.

    Supports all 12 primitives. Returns full access profiles for matches.
    """
    compounds = all_compounds()
    names = all_names()

    if primitive not in PRIMITIVE_ORDER:
        return {"error": f"Unknown primitive: {primitive}. Valid: {PRIMITIVE_ORDER}"}

    universes = get_psychedelic_universes()
    matches = []

    for ckey, ctuple in compounds.items():
        if ctuple.get(primitive) == value:
            access_list = []
            for u in universes:
                a, l = compute_access(ctuple, u)
                if a and l == "idempotent_terminal":
                    access_list.append(u.name)
            matches.append({
                "key": ckey,
                "name": names.get(ckey, ckey),
                "tier": assign_tier(ctuple),
                "bottlenecks": {p: ctuple[p] for p in BOTTLENECKS},
                "access_count": len(access_list),
                "universes": sorted(access_list),
                "is_novel": ckey in NOVEL_COMPOUNDS,
            })

    matches.sort(key=lambda m: m["access_count"], reverse=True)

    return {
        "search": f"{primitive}={value}",
        "match_count": len(matches),
        "matches": matches,
    }
# ─────────────────────────────────────────────────────────────────
# 4. DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────

def show_novel_compounds():
    """Display all novel compounds with their structural profiles."""
    compounds = all_compounds()
    names = all_names()
    universes = get_psychedelic_universes()

    lines = ["=" * 78]
    lines.append("  NOVEL PSYCHEDELIC COMPOUNDS — Extended Parameter Space")
    lines.append("=" * 78)
    lines.append("")

    for ckey in NOVEL_COMPOUNDS:
        ctuple = compounds[ckey]
        tier = assign_tier(ctuple)
        accesses = []
        for u in universes:
            a, l = compute_access(ctuple, u)
            if a and l == "idempotent_terminal":
                accesses.append(u.name)

        lines.append(f"  {names.get(ckey, ckey)}")
        lines.append(f"    Tier: {tier}  |  Universes: {len(accesses)}/17")
        lines.append(f"    Bottlenecks: ⊙={ctuple['⊙']}  ⊥={ctuple['⊥']}  <={ctuple['≺']}  ⊡={ctuple['⊡']}")
        lines.append(f"    Full: ⟨{ctuple['⊢']}{ctuple['⊣']}{ctuple['≻']}{ctuple['≺']}{ctuple['⋈']}{ctuple['⊤']}{ctuple['∈']}{ctuple['∋']}{ctuple['⊙']}{ctuple['⊥']}{ctuple['⊞']}{ctuple['⊡']}⟩")
        if accesses:
            lines.append(f"    Accesses: {', '.join(sorted(accesses))}")
        lines.append("")

    # Summary table of novel structural deltas
    lines.append("-" * 78)
    lines.append("  Structural Deltas from Baselines:")
    lines.append("")
    lines.append(f"  {'Compound':<24} {'⊙':>4} {'⊥':>4} {'≺':>4} {'⊡':>4}  Distinguishing Feature")
    lines.append(f"  {'-'*24} {'-'*4} {'-'*4} {'-'*4} {'-'*4}  {'-'*28}")
    lines.append(f"  {'Verticullum':<24} {'⊙':>4} {'𐑫':>4} {'𐑹':>4} {'𐑟':>4}  EP-Lever: non-Abelian winding + ⊙")
    lines.append(f"  {'Chimerium':<24} {'𐑣':>4} {'𐑫':>4} {'𐑹':>4} {'𐑭':>4}  Supercritical catalyst")
    lines.append(f"  {'Apertix':<24} {'⊙':>4} {'𐑖':>4} {'𐑬':>4} {'𐑴':>4}  Adjoint corridor, Z2 gated")
    lines.append(f"  {'Retiarius':<24} {'𐑮':>4} {'𐑒':>4} {'𐑿':>4} {'𐑷':>4}  Local-net trap, memory-limited")
    lines.append(f"  {'Praxeum':<24} {'𐑻':>4} {'𐑫':>4} {'𐑹':>4} {'𐑭':>4}  EP-Core: Gate 1 OFF switch")

    return "\n".join(lines)


def show_extended_compound_detail(ckey: str) -> str:
    """Show full structural details for any compound (novel or existing)."""
    compounds = all_compounds()
    names = all_names()

    if ckey not in compounds:
        return f"Unknown compound: {ckey}"

    ctuple = compounds[ckey]
    tier = assign_tier(ctuple)
    universes = get_psychedelic_universes()
    access_list = []
    for u in universes:
        a, l = compute_access(ctuple, u)
        if a and l == "idempotent_terminal":
            access_list.append(u.name)

    is_novel = ckey in NOVEL_COMPOUNDS
    tag = " [NOVEL]" if is_novel else ""

    lines = [
        f"COMPOUND: {names.get(ckey, ckey)} ({ckey}){tag}",
        f"Tier: {tier}",
        f"Universes accessed: {len(access_list)}/17",
        f"Bottleneck primitives:",
    ]
    for p in BOTTLENECKS:
        lines.append(f"  {p} = {ctuple.get(p, '?')}")
    lines.append("Full tuple:")
    for p in PRIMITIVE_ORDER:
        lines.append(f"  {p} = {ctuple.get(p, '?')}")
    if access_list:
        lines.append(f"Accessed universes: {', '.join(sorted(access_list))}")
    return "\n".join(lines)
# ─────────────────────────────────────────────────────────────────
# 5. MAIN CLI
# ─────────────────────────────────────────────────────────────────

def print_usage():
    """Print usage information."""
    print("""
NOVEL PSYCHEDELICS — Extended Navigator + Control Methods
===========================================================
Commands:
  novel                              List all novel compounds
  table                              Show access matrix (existing + novel)
  compound <C>                       Show compound detail (any)
  navigate <U>                       Find compounds accessing universe U
  operate <U>                        Show operations in universe U
  tensor <C1> <C2>                   Compute tensor product (novel + existing)
  region <P>=<V>                     Find compounds matching primitive=value
  universes                          List all 17 universes

Control Methods:
  control ep <compound> [ratio]      EP Gate Toggle — couple with Praxeum
  control chirality <compound> <H>   Chirality Ladder — step to target ⊥
  control winding <compound> <W>     Winding Modulate — adjust ⊡ protection
  control scope <compound> <G>       Scope Focus — adjust ∈ range
  control adjoint <compound> <P> <V> Adjoint Steer — directed primitive change
  control launch <compound>          Supercritical Launch — couple with Chimerium

Control target values:
  Chirality:  𐑓=H0  𐑒=H1  𐑖=H2  𐑫=H_inf
  Winding:    𐑷=W0  𐑴=W_Z2  𐑭=W_Z  𐑟=W_NA
  Scope:      𐑚=Beth  𐑔=Gimel  𐑲=Aleph
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    args = sys.argv[1:]
    cmd = args[0]

    if cmd == "novel":
        print(show_novel_compounds())

    elif cmd == "table":
        from psychedelic_navigator import print_access_table, COMPOUNDS as _orig
        compounds = all_compounds()
        universes = get_psychedelic_universes()
        print("=" * 78)
        print("  EXTENDED ACCESS MATRIX (existing + 5 novel)")
        print("=" * 78)
        print_access_table(compounds, universes)

    elif cmd == "compound" and len(args) >= 2:
        print(show_extended_compound_detail(args[1]))

    elif cmd == "navigate" and len(args) >= 2:
        from psychedelic_navigator import navigate_to_universe
        compounds = all_compounds()
        universes = get_psychedelic_universes()
        target = args[1]
        results = navigate_to_universe(target, compounds, universes)
        names = all_names()
        print(f"\nUniverse: {target}")
        if not results:
            print("  NO COMPOUND ACCESSES THIS UNIVERSE.")
        for cname, layer in results:
            novel_tag = " [NOVEL]" if cname in NOVEL_COMPOUNDS else ""
            print(f"  {names.get(cname, cname):<24} [{layer}]{novel_tag}")

    elif cmd == "operate" and len(args) >= 2:
        from psychedelic_navigator import universe_operations
        universes = get_psychedelic_universes()
        target = args[1]
        u = next((u for u in universes if u.name == target), None)
        if u is None:
            print(f"Unknown universe: {target}")
        else:
            print(json.dumps(universe_operations(u), indent=2))

    elif cmd == "tensor" and len(args) >= 3:
        result = tensor_compute(args[1], args[2])
        print(json.dumps(result, indent=2))

    elif cmd == "region" and len(args) >= 2:
        for arg in args[1:]:
            if "=" in arg:
                p, v = arg.split("=", 1)
                result = region_search(p, v)
                print(json.dumps(result, indent=2))
            else:
                print(f"Invalid region spec: {arg} (use P=V)")

    elif cmd == "universes":
        universes = get_psychedelic_universes()
        for i, u in enumerate(universes):
            g1_s = f"{u.g1.prim}>={u.g1.min_ord}" if u.g1 else "-"
            print(f"  [{i:2d}] {u.name:<24s} G1={g1_s}")

    elif cmd == "control" and len(args) >= 3:
        method = args[1]
        compound = args[2]
        result = None

        if method == "ep":
            ratio = float(args[3]) if len(args) >= 4 else 0.5
            result = ep_gate_toggle(compound, ratio)
        elif method == "chirality":
            if len(args) < 4:
                print("Usage: control chirality <compound> <H>")
                print(f"Valid H values: {list(CHIRALITY_ANCHORS.keys())}")
                return
            result = chirality_ladder(compound, args[3])
        elif method == "winding":
            if len(args) < 4:
                print("Usage: control winding <compound> <W>")
                print(f"Valid W values: {list(WINDING_LEVELS.keys())}")
                return
            result = winding_modulate(compound, args[3])
        elif method == "scope":
            if len(args) < 4:
                print("Usage: control scope <compound> <G>")
                print(f"Valid G values: {list(SCOPE_LEVELS.keys())}")
                return
            result = scope_focus(compound, args[3])
        elif method == "adjoint":
            if len(args) < 5:
                print("Usage: control adjoint <compound> <P> <V>")
                print(f"Valid primitives: {PRIMITIVE_ORDER}")
                return
            result = adjoint_steer(compound, args[3], args[4])
        elif method == "launch":
            result = supercritical_launch(compound)
        else:
            print(f"Unknown control method: {method}")
            print("Valid: ep, chirality, winding, scope, adjoint, launch")
            return

        if result:
            print(json.dumps(result, indent=2))

    elif cmd == "combine" and len(args) >= 3:
        # Legacy combine from psychedelic_navigator, extended
        compounds = all_compounds()
        universes = get_psychedelic_universes()
        result = predict_combination(args[1], args[2], compounds, universes)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        print_usage()


if __name__ == "__main__":
    main()
