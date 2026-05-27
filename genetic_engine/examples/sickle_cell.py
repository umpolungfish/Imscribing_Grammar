#!/usr/bin/env python3
"""example.py — Full pipeline example for sickle cell disease edit (Glu→Val)."""

from genetic_engine import EditingCompiler

def main():
    compiler = EditingCompiler()

    print("=" * 64)
    print("GENETIC ENGINE EXAMPLE: Sickle Cell Anemia Edit")
    print("Target: β-globin codon 6: GAG (Glu) → GUG (Val)")
    print("=" * 64)

    # Compile the edit
    result = compiler.compile("Glu", "Val")

    print(f"\nDesired change: {result.desired_change}")
    print(f"\n=== Stage 1: Codon Path ===")
    for path in result.codon_paths:
        marker = "★ BEST" if path == result.best_path else "  "
        print(f"  {marker} {path[0]} → {path[1]} (B₄ cost = {path[2]}/6)")

    print(f"\n=== Stage 2: Structural Analysis ===")
    print(f"  Original AA: {result.orig_aa}")
    print(f"  Target AA:   {result.target_aa}")
    print(f"  Primitive:   {result.primitive_delta['orig_primitive']} → "
          f"{result.primitive_delta['target_primitive']} "
          f"({'CHANGED' if result.primitive_delta['changed'] else 'preserved'})")
    print(f"  Risk class:  {result.primitive_delta['risk_class']} "
          f"(score={result.primitive_delta['risk_score']})")
    print(f"  Stratum:     {result.stratum_analysis['orig_stratum']} → "
          f"{result.stratum_analysis['target_stratum']}")
    print(f"  Crossing:    {'YES — ' + result.stratum_analysis['crossing_risk'] if result.stratum_analysis['crossing'] else 'NO'}")

    print(f"\n=== Stage 3: Protocol ===")
    if result.guide_design:
        print(f"  Guide:       {result.guide_design.guide_sequence}")
        print(f"  Seed:        {result.guide_design.seed_region}")
        print(f"  Pos3 strat:  {result.guide_design.position3_strategy}")
    if result.prime_edit:
        print(f"  RT template: {result.prime_edit.rt_template}")
        print(f"  Frobenius score: {result.prime_edit.design_score:.3f}")

    print(f"\n=== Frobenius Closure ===")
    v = result.frobenius_verification
    print(f"  μ∘δ: {'CLOSED ✓' if v.frobenius_closed else 'OPEN ✗'}")
    print(f"  Closure ratio: {v.closure_ratio:.3f}")
    print(f"  δ quality:     {v.delta_quality:.3f}")
    print(f"  μ quality:     {v.mu_quality:.3f}")
    for d in v.defects:
        print(f"  • {d}")

    print(f"\n=== Composite Score: {result.composite_score:.3f} ===")

    print("\n" + "=" * 64)
    print("NOTE: Frobenius score < 0.5 suggests the edit is structurally risky.")
    print("The Glu→Val edit crosses from split to exact stratum (GAA→GUA)")
    print("because GAA (Glu) is split and GUA (Val) is exact — a stratum crossing.")
    print("This structural crossing may contribute to sickle cell's variable expressivity.")
    print("=" * 64)


if __name__ == "__main__":
    main()
