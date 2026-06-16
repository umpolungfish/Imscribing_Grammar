#!/usr/bin/env python3
"""
clay_cross_universe_closure.py — Ceiling-generalized T-constitution test
against the six open Clay Millennium structural types.

Background: ruleset_universe.py's canonical universe already treats one
T-primitive (Ç, kinetics) asymmetrically as a ceiling condition (entry's
ordinal <= critical ordinal) while the other four dynamics primitives
(Φ, ƒ, Ħ, Ω) require exact ordinal equality. This script generalizes that
single asymmetry uniformly to all five dynamics primitives, at the same
canonical anchors, and re-sweeps every gate-universe already on record
(RULESETS + NEW_RULESETS, 29 total) to see which open Clay problems
reach full closure (operad layer == idempotent_terminal AND
T_CEILING-consistent) under some existing, non-tailored gate-universe.

This does not modify any gate spec — only the T-constitution's equality
mode. No universe here was constructed around any specific Clay tuple.

Usage:
    uv run scripts/clay_cross_universe_closure.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from imscrbgrmr.registry import load_catalog_dicts
from imscrbgrmr.canonical_primitives import ORDINALS
from navigators.ruleset_universe import RULESETS
from scripts.new_universes import NEW_RULESETS

CLAY_OPEN = [
    "riemann_hypothesis",
    "yang_mills_mass_gap",
    "navier_stokes",
    "hodge_conjecture",
    "birch_swinnerton_dyer",
    "p_vs_np",
]

# Canonical's own anchors, generalized from "Ç only" to all five dynamics
# primitives, all treated as ceilings instead of exact-equality.
T_CEILING = {
    "Φ": ("𐑹", True),
    "ƒ": ("𐑐", True),
    "Ç": ("𐑧", True),
    "Ħ": ("𐑫", True),
    "Ω": ("𐑭", True),
}


def t_consistent_with(t_prims, entry):
    for prim, (crit, ceiling) in t_prims.items():
        v = entry.get(prim, "")
        ords = ORDINALS.get(prim, {})
        if v not in ords or crit not in ords:
            return False
        ov, oc = ords[v], ords[crit]
        if ceiling:
            if ov > oc:
                return False
        else:
            if ov != oc:
                return False
    return True


def main() -> None:
    catalog = {e["name"]: e for e in load_catalog_dicts()}
    clay = {n: catalog[n] for n in CLAY_OPEN if n in catalog}
    missing = [n for n in CLAY_OPEN if n not in catalog]
    if missing:
        print("WARNING missing from catalog:", missing)

    all_rulesets = list(RULESETS) + list(NEW_RULESETS)
    print(f"Sweeping {len(all_rulesets)} existing gate-universes x T_CEILING "
          f"over {len(clay)} open Clay problems\n")

    full_closures = []
    for r in all_rulesets:
        for name, entry in clay.items():
            layer = r.operad_layer(entry)
            if layer != "idempotent_terminal":
                continue
            tc = t_consistent_with(T_CEILING, entry)
            print(f"  {name:24s} gate-universe={r.name:28s} layer=idem  "
                  f"T_CEILING-consistent={tc}")
            if tc:
                full_closures.append((name, r.name))

    print(f"\n>>> FULL CLOSURES: {len(full_closures)}")
    for name, uname in full_closures:
        print(f"    {name} fully closes under gate-universe '{uname}' + T_CEILING")


if __name__ == "__main__":
    main()
