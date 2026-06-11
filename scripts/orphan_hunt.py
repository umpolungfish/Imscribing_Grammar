#!/usr/bin/env python3
"""
orphan_hunt.py — find catalog entries that are plain in every known universe,
then hunt the ruleset that promotes each orphan to O_∞.

Usage:
  uv run python3 scripts/orphan_hunt.py               # find orphans + hunt
  uv run python3 scripts/orphan_hunt.py --list-only   # just show the orphans
  uv run python3 scripts/orphan_hunt.py --samples 5000 --seed 7
  uv run python3 scripts/orphan_hunt.py --entry "some name"  # hunt one specific entry
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from navigators.ruleset_universe import (
    RULESETS, universe_profile, GateSpec, AbsorptionRule,
    _DEFAULT_ABSORPTION, _T_CANONICAL,
)
from new_universes import NEW_RULESETS, iter_gate_configs_sampled, iter_t_subsets, build_ruleset
from imscrbgrmr.registry import load_catalog_dicts


ALL_RULESETS = list(RULESETS) + NEW_RULESETS


def find_orphans(catalog):
    """Catalog entries that are plain in every known universe."""
    # layer per entry per ruleset
    plain_in_all = set(e.get("name", str(i)) for i, e in enumerate(catalog))

    for rs in ALL_RULESETS:
        not_plain = set()
        for e in catalog:
            name = e.get("name", "?")
            if rs.operad_layer(e) != "plain":
                not_plain.add(name)
        plain_in_all -= not_plain
        if not plain_in_all:
            break  # short-circuit

    # Return the actual catalog dicts for orphans
    orphan_names = plain_in_all
    return [e for e in catalog if e.get("name", "?") in orphan_names]


def hunt_for_entry(entry, n_samples=2000, seed=42, verbose=True):
    """
    Sample gate configs and T-subsets to find a ruleset that promotes
    this entry above plain. Returns list of (ruleset, layer) that unlock it.
    """
    name = entry.get("name", "?")
    unlocks = []

    for i, (g1, g2, g3, ordering) in enumerate(
        iter_gate_configs_sampled(n_samples, seed=seed)
    ):
        rs = build_ruleset(
            name=f"hunt_{i}",
            description="",
            gate_config=(g1, g2, g3, ordering),
            t_config=dict(_T_CANONICAL),
            abs_config=_DEFAULT_ABSORPTION,
        )
        layer = rs.operad_layer(entry)
        if layer != "plain":
            unlocks.append((rs, layer))
            if verbose:
                print(f"  UNLOCKED [{layer}] under "
                      f"G1={g1.prim}≥ord{g1.min_ord} "
                      f"G2={g2.prim}≥ord{g2.min_ord} "
                      f"G3={g3.prim}≥ord{g3.min_ord} "
                      f"{'seq' if ordering else 'par'}")

    # Also try varying T-constitution with canonical gates
    canonical_gates = (GateSpec("Φ", 5.0), GateSpec("⊙", 2.0), GateSpec("Ω", 3.0), True)
    t_count = 0
    for t_cfg in iter_t_subsets():
        if not t_cfg:
            continue
        rs = build_ruleset(
            name=f"hunt_t_{t_count}",
            description="",
            gate_config=canonical_gates,
            t_config=t_cfg,
            abs_config=_DEFAULT_ABSORPTION,
        )
        layer = rs.operad_layer(entry)
        if layer != "plain":
            unlocks.append((rs, layer))
            if verbose:
                prims = list(t_cfg.keys())
                print(f"  UNLOCKED [{layer}] under T={prims} (canonical gates)")
        t_count += 1

    return unlocks


def summarize_unlocks(unlocks):
    """Which primitives appear most often in gate positions that unlock an orphan."""
    from collections import Counter
    g1_prims = Counter()
    g2_prims = Counter()
    g3_prims = Counter()
    layers = Counter()
    for rs, layer in unlocks:
        g1_prims[rs.g1.prim] += 1
        g2_prims[rs.g2.prim] += 1
        g3_prims[rs.g3.prim] += 1
        layers[layer] += 1

    print(f"\n  Unlock summary ({len(unlocks)} rulesets found):")
    print(f"  Layers:  {dict(layers)}")
    print(f"  G1 prims: {g1_prims.most_common(5)}")
    print(f"  G2 prims: {g2_prims.most_common(5)}")
    print(f"  G3 prims: {g3_prims.most_common(5)}")

    # Find the minimal ruleset: highest layer, most common gate pattern
    o_inf = [(rs, l) for rs, l in unlocks if l == "idempotent_terminal"]
    if o_inf:
        print(f"\n  O_∞ unlocks: {len(o_inf)}")
        # Show first 3
        for rs, _ in o_inf[:3]:
            print(f"    G1={rs.g1.prim}≥ord{rs.g1.min_ord} "
                  f"G2={rs.g2.prim}≥ord{rs.g2.min_ord} "
                  f"G3={rs.g3.prim}≥ord{rs.g3.min_ord} "
                  f"T={list(rs.t_prims.keys())}")
    else:
        print(f"\n  No O_∞ unlocks found in this sample. "
              f"Highest: {layers.most_common(1)}")


def main():
    parser = argparse.ArgumentParser(description="Hunt for orphan catalog entries")
    parser.add_argument("--list-only", action="store_true",
                        help="Just list orphans, don't hunt")
    parser.add_argument("--samples", type=int, default=2000,
                        help="Gate config samples per orphan (default 2000)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--entry", help="Hunt a specific entry by name")
    parser.add_argument("--catalog", help="Path to IG_catalog.json")
    args = parser.parse_args()

    catalog = load_catalog_dicts(extra_path=args.catalog)
    print(f"Catalog: {len(catalog)} entries across {len(ALL_RULESETS)} known universes")

    if args.entry:
        targets = [e for e in catalog if args.entry.lower() in e.get("name", "").lower()]
        if not targets:
            print(f"No entry matching '{args.entry}'")
            sys.exit(1)
        print(f"\nHunting specific entry: {targets[0].get('name')}")
        unlocks = hunt_for_entry(targets[0], n_samples=args.samples, seed=args.seed)
        if unlocks:
            summarize_unlocks(unlocks)
        else:
            print("  No unlock found in this sample.")
        return

    print("\nFinding orphans (plain in ALL known universes)...")
    orphans = find_orphans(catalog)

    if not orphans:
        print("No orphans — every catalog entry promotes in at least one known universe.")
        print("The Hall has no locked rooms. (Or you need more rulesets.)")
        return

    print(f"\nOrphans found: {len(orphans)}")
    for e in orphans:
        name = e.get("name", "?")
        # Show primitive signature
        prims = {k: v for k, v in e.items() if k != "name"}
        print(f"  {name}")
        print(f"    {prims}")

    if args.list_only:
        return

    print(f"\nHunting unlock rulesets ({args.samples} gate samples + all T-subsets)...")
    for e in orphans:
        name = e.get("name", "?")
        print(f"\n── Orphan: {name} ──")
        unlocks = hunt_for_entry(e, n_samples=args.samples, seed=args.seed, verbose=False)
        if unlocks:
            summarize_unlocks(unlocks)
        else:
            print(f"  Truly unreachable in {args.samples} gate samples + 4096 T-subsets.")
            print(f"  This entry may require asymmetric absorption or a novel gate logic.")


if __name__ == "__main__":
    main()
