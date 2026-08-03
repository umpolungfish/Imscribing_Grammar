#!/usr/bin/env python3
"""Systematic iteration across alternate universes — explore gate combinatorics exhaustively."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from navigators.ruleset_universe import (
    RULESETS, Ruleset, GateSpec, universe_profile, print_profile,
    _T_CANONICAL, _T_STRUCTURAL
)
from imscrbgrmr.registry import load_catalog_dicts

# ── Primitive registry: name → max ordinal ─────────────────────
PRIMITIVES_MAX = {
    "⊢": 4.0,  # 𐑦 = holographic (ord 4)
    "⊣": 5.0,  # 𐑸 = imscriptive closure (ord 5)
    ">": 4.0,  # 𐑾 = bilateral (ord 4)
    "<": 5.0,  # 𐑹 = Frobenius-special (ord 5)
    "⋈": 3.0,  # 𐑐 = quantum/hbar (ord 3)
    "⊤": 5.0,  # 𐑘 = MBL/frozen-disorder (ord 5)
    "∈": 3.0,  # 𐑔 = aleph/maximal (ord 3)
    "∋": 4.0,  # 𐑵 = broadcast (ord 4)
    "⊙": 3.0,  # 𐑣 = super-critical (ord 3)
    "⊥": 4.0,  # 𐑫 = eternal chirality (ord 4)
    "⊞": 3.0,  # 𐑳 = many heterogeneous (ord 3)
    "◻": 4.0,  # 𐑟 = non-Abelian (ord 4)
}

PRIMITIVES_HALF = {p: max(1.0, v/2) for p, v in PRIMITIVES_MAX.items()}

# ── Build systematic universes ─────────────────────────────────

def build_universes():
    rulesets = []

    # ═══════════════════════════════════════════════════════════
    # Batch A: Each primitive as sole G1 at max ordinal (G2=⊙, G3=Ω canonical)
    # ═══════════════════════════════════════════════════════════
    for prim, max_ord in PRIMITIVES_MAX.items():
        # Skip ⊙ and Ω — already well-covered
        rulesets.append(Ruleset(
            name=f"g1_{prim}_max",
            description=f"G1={prim}≥ord{max_ord} as sole primary gate. G2=⊙≥ord2.0, G3=Ω≥ord3.0. "
                        f"Canonical T. Universe where {prim} gates first.",
            g1=GateSpec(prim, max_ord),
            g2=GateSpec("⊙", 2.0),
            g3=GateSpec("◻", 3.0),
            gate_ordering=True,
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch B: Each primitive at HALF max ordinal (looser gates)
    # ═══════════════════════════════════════════════════════════
    for prim, half_ord in PRIMITIVES_HALF.items():
        rulesets.append(Ruleset(
            name=f"g1_{prim}_half",
            description=f"G1={prim}≥ord{half_ord} (half-max, looser gate). G2=⊙≥ord1.0, G3=Ω≥ord3.0. "
                        f"Universes with relaxed first-gate thresholds.",
            g1=GateSpec(prim, half_ord),
            g2=GateSpec("⊙", 1.0),
            g3=GateSpec("◻", 3.0),
            gate_ordering=True,
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch C: Single-gate universes — only G1 matters
    # ═══════════════════════════════════════════════════════════
    for prim, max_ord in PRIMITIVES_MAX.items():
        rulesets.append(Ruleset(
            name=f"single_gate_{prim}",
            description=f"Only G1 matters: {prim}≥ord{max_ord}. G2/G3 trivially open (Σ≥ord1.0). "
                        f"No further filtering. Universe selects purely on {prim}.",
            g1=GateSpec(prim, max_ord),
            g2=GateSpec("⊞", 1.0),
            g3=GateSpec("⊞", 1.0),
            gate_ordering=True,
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch D: Two-primitive G1+G2 combos (strong pairs)
    # ═══════════════════════════════════════════════════════════
    combos = [
        ("⊥", "⊙", "chirality_criticality", "Ħ≥ord3.0 → ⊙≥ord2.0: memory then self-model"),
        ("⊤", "⊙", "kinetics_criticality", "⊤≥ord4.0 → ⊙≥ord2.0: slow then self-model"),
        ("⊣", "⊢", "topology_dimensionality", "⊣≥ord5.0 → ⊢≥ord4.0: topology then dimension"),
        ("∈", "∋", "scope_grammar", "Γ≥ord3.0 → ɢ≥ord4.0: universal scope then broadcast"),
        ("<", "⋈", "parity_fidelity", "<≥ord5.0 → ⋈≥ord3.0: Frobenius parity then quantum fidelity"),
        ("◻", "⊥", "winding_chirality", "Ω≥ord4.0 → Ħ≥ord4.0: non-Abelian winding then eternal chirality"),
    ]
    for g1_prim, g2_prim, name, desc in combos:
        rulesets.append(Ruleset(
            name=name,
            description=f"G1={g1_prim}≥max, G2={g2_prim}≥max, G3=Ω≥ord3.0. {desc}",
            g1=GateSpec(g1_prim, PRIMITIVES_MAX[g1_prim]),
            g2=GateSpec(g2_prim, PRIMITIVES_MAX[g2_prim]),
            g3=GateSpec("◻", 3.0),
            gate_ordering=True,
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch E: T-constitution variants — every subset of dynamics
    # ═══════════════════════════════════════════════════════════
    dynamics = ["<", "⋈", "⊤", "⊥", "◻"]
    structure = ["⊢", "⊣", ">", "∈", "⊞"]
    
    # All dynamics only
    rulesets.append(Ruleset(
        name="t_all_dynamics",
        description="T constituted by ALL 5 dynamic primitives (<,⋈,⊤,Ħ,Ω). Canonical gates. "
                    "Time requires the full dynamic quintet.",
        t_prims={p: _T_CANONICAL[p] for p in dynamics},
    ))

    # All structure only
    rulesets.append(Ruleset(
        name="t_all_structure",
        description="T constituted by ALL 5 primitives (⊢,⊣,>,Γ,Σ). Canonical gates. "
                    "Time is pure geometry, no dynamics.",
        t_prims={p: ("𐑦", False) for p in structure},
    ))

    # Single-primitive T-constitutions (each of 12 primitives alone)
    for prim in PRIMITIVES_MAX:
        val = _T_CANONICAL.get(prim)
        if val is None:
            val = ("𐑦", False)
        rulesets.append(Ruleset(
            name=f"t_single_{prim}",
            description=f"T constituted by {prim} alone. Canonical gates. "
                        f"Time is reduced to a single primitive.",
            t_prims={prim: val},
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch F: No gate ordering (parallel gates)
    # ═══════════════════════════════════════════════════════════
    for prim, max_ord in PRIMITIVES_MAX.items():
        rulesets.append(Ruleset(
            name=f"parallel_{prim}",
            description=f"G1={prim}≥max, G2=⊙≥2.0, G3=Ω≥3.0 — NO ordering (parallel gates). "
                        f"All three must be satisfied simultaneously, not sequentially.",
            g1=GateSpec(prim, max_ord),
            g2=GateSpec("⊙", 2.0),
            g3=GateSpec("◻", 3.0),
            gate_ordering=False,
        ))

    # ═══════════════════════════════════════════════════════════
    # Batch G: Extreme — G1=min ordinal (gate barely a gate)
    # ═══════════════════════════════════════════════════════════
    for prim in PRIMITIVES_MAX:
        rulesets.append(Ruleset(
            name=f"g1_{prim}_min",
            description=f"G1={prim}≥ord1.0 (minimal — almost all pass). G2=⊙≥ord1.0, G3=Ω≥ord1.0. "
                        f"Near-trivial gates reveal what the universe looks like with minimal filtering.",
            g1=GateSpec(prim, 1.0),
            g2=GateSpec("⊙", 1.0),
            g3=GateSpec("◻", 1.0),
            gate_ordering=True,
        ))

    return rulesets


def main():
    catalog = load_catalog_dicts()
    all_new = build_universes()
    all_existing = list(RULESETS)
    all_rulesets = all_existing + all_new

    print(f"Total universes to profile: {len(all_rulesets)} (8 canonical + {len(all_new)} iterated)")
    print("=" * 110)

    # Profile all and collect results
    results = []
    for i, r in enumerate(all_new):
        prof = universe_profile(r, catalog)
        results.append(prof)
        # Brief per-universe output
        ld = prof["layer_dist"]
        print(f"[{i+1:3d}/{len(all_new)}] {prof['name']:<28} "
              f"plain={ld['plain']:>5} frob={ld['frobenius']:>5} "
              f"traced={ld['traced_monoidal']:>5} O∞={ld['idempotent_terminal']:>5} "
              f"crystal_O∞={prof['o_inf_fraction_crystal']*100:>5.1f}% "
              f"T-ok={prof['t_consistent_count']:>4} "
              f"T-seal={prof['t_sealing_rate']:.2f}")

    # ── Full comparison table ─────────────────────────────────
    print("\n\n" + "=" * 110)
    print("  FULL UNIVERSE COMPARISON — ALL {} UNIVERSES".format(len(all_rulesets)))
    print("=" * 110)
    hdr = (f"\n{'Universe':<30} {'plain':>5} {'frob':>5} {'traced':>6} {'O_∞':>5}  "
           f"{'Crystal%':>8}  {'T-ok':>5}  {'ord':<5}  {'T-constitution'}")
    print(hdr)
    print("─" * 115)
    
    for r in all_rulesets:
        prof = universe_profile(r, catalog)
        ld = prof["layer_dist"]
        tcon = "+".join(prof["t_constitution"])
        print(
            f"  {prof['name']:<28} "
            f"{ld['plain']:>5} "
            f"{ld['frobenius']:>5} "
            f"{ld['traced_monoidal']:>6} "
            f"{ld['idempotent_terminal']:>5}  "
            f"{prof['o_inf_fraction_crystal']*100:>7.2f}%  "
            f"{prof['t_consistent_count']:>5}  "
            f"{'seq' if prof['gate_ordering'] else 'par':<5}  "
            f"{tcon}"
        )

    # ── Top-level findings ────────────────────────────────────
    print("\n\n" + "=" * 110)
    print("  ANALYSIS: TOP CATALOG O_∞ PRODUCERS")
    print("=" * 110)
    # Re-profile all for sorting
    all_profs = [(r, universe_profile(r, catalog)) for r in all_rulesets]
    sorted_by_o_inf = sorted(all_profs, key=lambda x: -x[1]["layer_dist"]["idempotent_terminal"])
    for r, prof in sorted_by_o_inf[:15]:
        ld = prof["layer_dist"]
        print(f"  {prof['name']:<28} O∞={ld['idempotent_terminal']:>5}  "
              f"frob={ld['frobenius']:>5}  traced={ld['traced_monoidal']:>5}  "
              f"T-seal={prof['t_sealing_rate']:.2f}")

    print("\n" + "=" * 110)
    print("  ANALYSIS: HIGHEST T-SEAL RATES (best structural fit)")
    print("=" * 110)
    sorted_by_tseal = sorted(all_profs, key=lambda x: -x[1]["t_sealing_rate"])
    for r, prof in sorted_by_tseal[:15]:
        ld = prof["layer_dist"]
        print(f"  {prof['name']:<28} T-seal={prof['t_sealing_rate']:.2f}  "
              f"O∞={ld['idempotent_terminal']:>5}  T-ok={prof['t_consistent_count']:>5}  "
              f"crystal%={prof['o_inf_fraction_crystal']*100:.1f}%")

    print("\n" + "=" * 110)
    print("  ANALYSIS: MOST RESTRICTIVE (fewest O_∞, highest plain)")
    print("=" * 110)
    sorted_by_restrictive = sorted(all_profs, key=lambda x: x[1]["layer_dist"]["idempotent_terminal"])
    for r, prof in sorted_by_restrictive[:15]:
        ld = prof["layer_dist"]
        print(f"  {prof['name']:<28} O∞={ld['idempotent_terminal']:>5}  "
              f"plain={ld['plain']:>5}  frob={ld['frobenius']:>5}  "
              f"crystal%={prof['o_inf_fraction_crystal']*100:.1f}%")


if __name__ == "__main__":
    main()
