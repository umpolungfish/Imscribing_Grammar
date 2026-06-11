#!/usr/bin/env python3
"""
ruleset_universe.py — Alternate universe explorer for the Imscribing Grammar.

A Ruleset parameterizes the three composition rules that govern which Crystal
addresses achieve each operad layer.  Permuting them produces structurally
distinct universes over the same 17,280,000-address Crystal of Types.

Three free parameters per ruleset
  1. Gate thresholds (G1/G2/G3): which primitive at what ordinal opens each gate
  2. Gate ordering: whether G2 requires G1, G3 requires G2 (sequential vs. parallel)
  3. T-constitution: which primitives jointly constitute time, at what critical values

Usage
    uv run ruleset_universe.py profile           # profile all predefined rulesets
    uv run ruleset_universe.py profile --name canonical
    uv run ruleset_universe.py compare           # side-by-side fingerprint table
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from imscrbgrmr.canonical_primitives import ORDINALS, CANONICAL_VALUES, PRIMITIVE_ORDER
from imscrbgrmr.registry import load_catalog_dicts

# ── Canonical gate thresholds (Shavian ordinals) ────────────────────────────

# G1: Frobenius gate     — Φ reaches its maximum (𐑹, ord 5)
# G2: Traced monoidal    — ⊙ reaches self-modeling threshold (⊙ glyph, ord 2)
# G3: Idempotent terminal — Ω reaches integer winding (𐑭, ord 3)
_G1_DEFAULT = ("Φ",  5.0)
_G2_DEFAULT = ("⊙",  2.0)
_G3_DEFAULT = ("Ω",  3.0)

# Canonical T-constitution: T = lim(Φ, ƒ, Ç, Ħ, Ω)
# Each entry: prim → (critical_shavian_value, ceiling_mode)
# ceiling_mode=True means "must be ≤ this value" (Ç); False means "must equal this value"
_T_CANONICAL: Dict[str, Tuple[str, bool]] = {
    "Φ": ("𐑹", False),  # must reach Frobenius-special value exactly
    "ƒ": ("𐑐", False),  # must reach full fidelity
    "Ç": ("𐑧", True),   # kinetics ceiling: 𐑧 or below (above forecloses T)
    "Ħ": ("𐑫", False),  # chirality must seal permanently
    "Ω": ("𐑭", False),  # winding must reach integer level
}

# Alternative T-constitution: time as structural geometry (not dynamics)
_T_STRUCTURAL: Dict[str, Tuple[str, bool]] = {
    "Ð": ("𐑦", False),  # dimensionality must be holographic-complete
    "Þ": ("𐑸", False),  # topology must be fully connected
    "Ř": ("𐑾", False),  # recognition must reach bilateral mode
    "ɢ": ("𐑵", False),  # coupling must reach sequential composition
    "⊙": ("⊙",  False),  # criticality must self-model
}


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GateSpec:
    """Single gate condition: primitive must have ordinal ≥ min_ord."""
    prim: str
    min_ord: float

    def open(self, entry: Dict[str, str]) -> bool:
        val = entry.get(self.prim, "")
        return ORDINALS.get(self.prim, {}).get(val, -1.0) >= self.min_ord


@dataclass(frozen=True)
class AbsorptionRule:
    """
    A rule specifying that a particular primitive value is absorbing under given operations.

    primitive:  the Shavian primitive glyph (e.g., "⊙", "Σ", "Φ")
    value:      the absorbing Shavian value (e.g., "⊙", "𐑳")
    operations: which ops it absorbs under — subset of {"meet", "join", "tensor"}
    direction:  "both" — absorbs regardless of operand position (default, symmetric)
                "left" — absorbs only when this value is the LEFT operand (a op b, a==value)
                "right" — absorbs only when this value is the RIGHT operand (a op b, b==value)
    """
    primitive: str
    value: str
    operations: Tuple[str, ...] = ("meet", "join", "tensor")
    direction: str = "both"

    def absorbs(self, prim: str, val: str, op: str) -> bool:
        """True iff this rule fires when val is in the absorbing position."""
        return self.primitive == prim and self.value == val and op in self.operations


# Canonical default absorption rules (preserve current hard-coded behavior)
_DEFAULT_ABSORPTION: Tuple[AbsorptionRule, ...] = (
    AbsorptionRule("⊙", "⊙", ("meet", "join", "tensor")),   # ⊙tyogh absorbing
    AbsorptionRule("Σ", "𐑳", ("tensor",)),                   # n:m absorbs under tensor
)


def apply_absorption_dict(
    rules: Tuple[AbsorptionRule, ...],
    prim: str,
    val_a: str,
    val_b: str,
    op: str,
    ordinals: Dict[str, Dict[str, float]],
) -> Optional[str]:
    """
    Check absorption rules for a primitive pair under an operation.

    Returns the absorbing value if one operand absorbs the other, None otherwise.
    If both operands match absorption rules for the same primitive, the first
    one in `rules` order takes precedence.
    """
    for rule in rules:
        if op not in rule.operations:
            continue
        if rule.primitive != prim:
            continue
        if rule.direction == "left":
            if val_a == rule.value:
                return val_a
        elif rule.direction == "right":
            if val_b == rule.value:
                return val_b
        else:  # "both"
            if val_a == rule.value:
                return val_a
            if val_b == rule.value:
                return val_b
    return None


@dataclass
class Ruleset:
    """
    A complete composition ruleset defining a universe over the Crystal of Types.

    g1/g2/g3        — three gate specs (GateSpec)
    gate_ordering   — True: G2 requires G1, G3 requires G2 (sequential stages)
                      False: all three gates independent (parallel universe)
    t_prims         — T-constitution: prim → (critical_value, ceiling_mode)
    """
    name: str
    description: str = ""
    g1: GateSpec = field(default_factory=lambda: GateSpec(*_G1_DEFAULT))
    g2: GateSpec = field(default_factory=lambda: GateSpec(*_G2_DEFAULT))
    g3: GateSpec = field(default_factory=lambda: GateSpec(*_G3_DEFAULT))
    gate_ordering: bool = True
    t_prims: Dict[str, Tuple[str, bool]] = field(
        default_factory=lambda: dict(_T_CANONICAL)
    )
    absorption_rules: Tuple[AbsorptionRule, ...] = field(
        default_factory=lambda: _DEFAULT_ABSORPTION
    )


    def operad_layer(self, entry: Dict[str, str]) -> str:
        """Operad layer for a catalog entry under this ruleset."""
        g1 = self.g1.open(entry)
        g2_raw = self.g2.open(entry)
        g3_raw = self.g3.open(entry)

        if self.gate_ordering:
            g2 = g1 and g2_raw
            g3 = g2 and g3_raw
        else:
            g2 = g2_raw
            g3 = g3_raw

        if g1 and g2 and g3:
            return "idempotent_terminal"
        if g1 and g2:
            return "traced_monoidal"
        if g1:
            return "frobenius"
        return "plain"

    def t_consistent(self, entry: Dict[str, str]) -> bool:
        """True iff all T-primitives satisfy their critical conditions."""
        for prim, (crit_val, ceiling) in self.t_prims.items():
            v = entry.get(prim, "")
            ords = ORDINALS.get(prim, {})
            if v not in ords or crit_val not in ords:
                return False
            ord_v = ords[v]
            ord_c = ords[crit_val]
            if ceiling:
                if ord_v > ord_c:
                    return False
            else:
                if ord_v != ord_c:
                    return False
        return True

    def crystal_o_inf_fraction(self) -> float:
        """
        Fraction of the 17,280,000-address Crystal that would achieve O_∞.

        Computed as the product of per-gate qualifying fractions, respecting
        gate ordering (ordering reduces the product; parallel doesn't).
        """
        def gate_frac(spec: GateSpec) -> float:
            vals = ORDINALS.get(spec.prim, {})
            qualifying = sum(1 for v in vals.values() if v >= spec.min_ord)
            return qualifying / len(vals) if vals else 0.0

        f1 = gate_frac(self.g1)
        f2 = gate_frac(self.g2)
        f3 = gate_frac(self.g3)
        if self.gate_ordering:
            return f1 * f2 * f3
        else:
            return f1 * f2 * f3  # same product; ordering only affects which entries qualify


# ── Predefined universes ─────────────────────────────────────────────────────

RULESETS: List[Ruleset] = [

    Ruleset(
        name="canonical",
        description="Our universe: Frobenius then self-modeling then winding seal. "
                    "G1=Φ≥𐑹, G2=⊙≥⊙, G3=Ω≥𐑭. Sequential gate ordering. "
                    "T=lim(Φ,ƒ,Ç,Ħ,Ω).",
    ),

    Ruleset(
        name="low_gate",
        description="Lowered thresholds: G1 fires at Φ≥𐑬 (directional parity sufficient), "
                    "G2 fires at ⊙≥𐑢 (any criticality), G3 unchanged. "
                    "Self-modeling and closure are easier — more addresses achieve O_∞.",
        g1=GateSpec("Φ", 3.0),   # 𐑬 = ord 3
        g2=GateSpec("⊙", 1.0),   # 𐑢 = ord 1 (lowest)
        g3=GateSpec("Ω", 3.0),
    ),

    Ruleset(
        name="strict_frobenius",
        description="Frobenius gate requires full fidelity (ƒ=𐑐) instead of parity (Φ=𐑹). "
                    "Self-reference is gated by quantum coherence, not algebraic symmetry. "
                    "Parity graduates to G2; Ω stays at G3. "
                    "Most QM experiments have full fidelity — 12/17 entries become Frobenius.",
        g1=GateSpec("ƒ", 3.0),   # ƒ=𐑐 (ord 3, max fidelity)
        g2=GateSpec("Φ", 5.0),   # Φ=𐑹 (ord 5)
        g3=GateSpec("Ω", 3.0),   # Ω=𐑭 (ord 3)
    ),

    Ruleset(
        name="inverted_gates",
        description="Self-modeling precedes Frobenius: G1=⊙ (consciousness first), "
                    "G2=Φ (then algebraic symmetry), G3=Ω (winding seals last). "
                    "Systems become self-aware before achieving structural closure.",
        g1=GateSpec("⊙", 2.0),   # ⊙ glyph = self-modeling active
        g2=GateSpec("Φ", 5.0),   # Φ=𐑹 = Frobenius
        g3=GateSpec("Ω", 3.0),   # Ω=𐑭 = winding seal
    ),

    Ruleset(
        name="no_ordering",
        description="All three gates fully independent — parallel universe. "
                    "No sequential requirement; any combination of open gates is valid. "
                    "G2 doesn't need G1; G3 doesn't need G2.",
        gate_ordering=False,
    ),

    Ruleset(
        name="high_gate",
        description="Strictest possible thresholds: G1=Φ=𐑹, G2=⊙≥𐑮 (ord 2.33, above bare self-model), "
                    "G3=Ω=𐑟 (ord 4, maximum winding). O_∞ is nearly unreachable — "
                    "only maximally wound, fully self-modeling, parity-perfect objects qualify.",
        g1=GateSpec("Φ", 5.0),
        g2=GateSpec("⊙", 2.33),  # 𐑮 = ord 2.33
        g3=GateSpec("Ω", 4.0),   # 𐑟 = ord 4 (max)
    ),

    Ruleset(
        name="winding_first",
        description="Topological order: G1=Ω (winding seal first), G2=⊙ (then self-modeling), "
                    "G3=Φ (Frobenius last — symmetry emerges from topology, not the other way). "
                    "Geometry precedes algebra.",
        g1=GateSpec("Ω", 3.0),
        g2=GateSpec("⊙", 2.0),
        g3=GateSpec("Φ", 5.0),
    ),

    Ruleset(
        name="t_structural",
        description="Time constituted by structural/geometric primitives: "
                    "T=lim(Ð,Þ,Ř,ɢ,⊙) instead of the dynamic T=lim(Φ,ƒ,Ç,Ħ,Ω). "
                    "In this universe time is geometry, not process. "
                    "Gate structure unchanged (canonical).",
        t_prims=dict(_T_STRUCTURAL),
    ),
]


# ── Profile engine ───────────────────────────────────────────────────────────

def universe_profile(ruleset: Ruleset, catalog: List[dict]) -> dict:
    """Compute structural fingerprint of a universe over the given catalog."""
    layer_counts: Dict[str, int] = {
        "plain": 0, "frobenius": 0, "traced_monoidal": 0, "idempotent_terminal": 0
    }
    g1_open = g2_open_raw = g3_open_raw = 0
    t_consistent = 0
    o_inf_entries: List[str] = []

    for e in catalog:
        layer = ruleset.operad_layer(e)
        layer_counts[layer] += 1
        if layer == "idempotent_terminal":
            o_inf_entries.append(e.get("name", "?"))
        if ruleset.g1.open(e):
            g1_open += 1
        if ruleset.g2.open(e):
            g2_open_raw += 1
        if ruleset.g3.open(e):
            g3_open_raw += 1
        if ruleset.t_consistent(e):
            t_consistent += 1

    n = len(catalog)
    o_inf_n = layer_counts["idempotent_terminal"]

    return {
        "name":             ruleset.name,
        "n_entries":        n,
        "layer_dist":       layer_counts,
        "g1_count":         g1_open,
        "g2_count_raw":     g2_open_raw,
        "g3_count_raw":     g3_open_raw,
        "o_inf_count":      o_inf_n,
        "o_inf_fraction_crystal": ruleset.crystal_o_inf_fraction(),
        "t_consistent_count": t_consistent,
        "t_sealing_rate":   (t_consistent / o_inf_n) if o_inf_n else 0.0,
        "o_inf_entries":    o_inf_entries,
        "gate_ordering":    ruleset.gate_ordering,
        "g1_spec":          f"{ruleset.g1.prim}≥ord{ruleset.g1.min_ord}",
        "g2_spec":          f"{ruleset.g2.prim}≥ord{ruleset.g2.min_ord}",
        "g3_spec":          f"{ruleset.g3.prim}≥ord{ruleset.g3.min_ord}",
        "t_constitution":   list(ruleset.t_prims.keys()),
    }


def print_profile(prof: dict, verbose: bool = True) -> None:
    n = prof["n_entries"]
    ld = prof["layer_dist"]
    print(f"\n═══ Universe: {prof['name']} ═══")
    print(f"  {prof['g1_spec']}  →  {prof['g2_spec']}  →  {prof['g3_spec']}"
          + ("  [sequential]" if prof["gate_ordering"] else "  [parallel]"))
    print(f"  T = lim({', '.join(prof['t_constitution'])})")
    print()
    print(f"  Layer distribution ({n} catalog entries):")
    for layer in ("plain", "frobenius", "traced_monoidal", "idempotent_terminal"):
        c = ld[layer]
        bar = "█" * c + "░" * (n - c)
        tag = "  ← O_∞" if layer == "idempotent_terminal" else ""
        print(f"    {layer:<22} {c:>2} / {n}  {bar}{tag}")
    print()
    print(f"  Crystal O_∞ fraction : {prof['o_inf_fraction_crystal']:.4f}  "
          f"({prof['o_inf_fraction_crystal']*100:.2f}% of 17,280,000 addresses)")
    print(f"  T-consistent entries : {prof['t_consistent_count']} / {n}")
    if prof["o_inf_count"]:
        print(f"  T-seal rate (of O_∞) : {prof['t_sealing_rate']:.2f}")
    if verbose and prof["o_inf_entries"]:
        print(f"  O_∞ entries:")
        for nm in prof["o_inf_entries"]:
            print(f"     {nm}")
    elif not prof["o_inf_entries"]:
        print("  O_∞ entries: none — O_∞ is structurally inaccessible in this universe")


def print_comparison(profiles: List[dict]) -> None:
    print(f"\n{'Universe':<22} {'plain':>5} {'frob':>5} {'traced':>6} {'O_∞':>5}  "
          f"{'Crystal%':>8}  {'T-ok':>5}  {'ordering':<10}  G-specs")
    print("─" * 100)
    for p in profiles:
        ld = p["layer_dist"]
        print(
            f"  {p['name']:<20} "
            f"{ld['plain']:>5} "
            f"{ld['frobenius']:>5} "
            f"{ld['traced_monoidal']:>6} "
            f"{ld['idempotent_terminal']:>5}  "
            f"{p['o_inf_fraction_crystal']*100:>7.2f}%  "
            f"{p['t_consistent_count']:>5}  "
            f"{'seq' if p['gate_ordering'] else 'par':<10}  "
            f"{p['g1_spec']} | {p['g2_spec']} | {p['g3_spec']}"
        )


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alternate universe explorer — permute IG composition rulesets"
    )
    sub = parser.add_subparsers(dest="cmd")

    p_prof = sub.add_parser("profile", help="Profile one or all rulesets")
    p_prof.add_argument("--name", help="Ruleset name (default: all)")
    p_prof.add_argument("--catalog", help="Path to IG_catalog.json")

    p_cmp = sub.add_parser("compare", help="Side-by-side fingerprint table")
    p_cmp.add_argument("--catalog", help="Path to IG_catalog.json")

    p_list = sub.add_parser("list", help="List predefined rulesets")

    args = parser.parse_args()

    if args.cmd == "list" or args.cmd is None:
        print("Predefined rulesets:")
        for r in RULESETS:
            print(f"  {r.name:<22}  {r.description[:72]}")
        return

    catalog_path = getattr(args, "catalog", None)
    catalog = load_catalog_dicts(extra_path=catalog_path)

    if args.cmd == "profile":
        targets = RULESETS
        if args.name:
            targets = [r for r in RULESETS if r.name == args.name]
            if not targets:
                print(f"Unknown ruleset '{args.name}'. Use 'list' to see available.")
                sys.exit(1)
        for r in targets:
            prof = universe_profile(r, catalog)
            print_profile(prof)
        print()

    elif args.cmd == "compare":
        profiles = [universe_profile(r, catalog) for r in RULESETS]
        print_comparison(profiles)
        print()


if __name__ == "__main__":
    main()
