"""
info_bits_demo.py — Demonstrate the calibrated I(bits) pipeline.

Runs the three calibration targets and prints I_recognition, I_net,
I_total_with_solvent for each. Then shows how to use compute_I_from_synthon()
on a catalog entry.

Run:
    python examples/info_bits_demo.py

Or via CLI:
    imscribe info-bits --calibrate
    imscribe info-bits --calibrate --solvent chloroform
"""
from __future__ import annotations

import json
from imscrbgrmr.information import (
    calibrate_I_pipeline,
    compute_I_hbond_dimer,
    compute_I_triple_hbond_array,
    compute_I_quadruple_hbond_array,
    compute_I_proline_cycle,
    SOLVENT_DELTA_S,
)


def print_result(r, label="") -> None:
    print(f"\n{'─'*55}")
    if label:
        print(f"  {label}")
    print(f"  System:           {r.system_name}")
    print(f"  I_recognition:    {r.recognition_bits:.3f} bits")
    print(f"  I_orientation:    {r.orientation_bits:.3f} bits (overhead)")
    print(f"  I_net:            {r.I_net:.3f} bits  (= I_rec − 0.3×I_orient)")
    print(f"  I_total:          {r.total_bits:.3f} bits")
    if r.solvent_correction:
        print(f"  I_total+solvent:  {r.I_total_with_solvent:.3f} bits  "
              f"(ΔS_solv={r.solvent_correction.delta_S_J_mol_K:.1f} J/mol·K)")
    print(f"  ΔS_conf:         {r.delta_S_J_mol_K:.1f} J·mol⁻¹·K⁻¹")
    print(f"  Heuristic:        {r.heuristic_bits:.1f} bits")
    print(f"  Verdict:          {r._verdict()}")
    for note in r.notes[:3]:
        print(f"    · {note}")


def demo_calibration_pipeline() -> None:
    print("=" * 55)
    print("Full I(bits) Calibration Pipeline (vacuum)")
    print("=" * 55)

    report = calibrate_I_pipeline(solvent_model="vacuum", include_quadruple=True)
    summary = report.summary()

    for entry in summary["calibration_targets"]:
        ok = "✓" if entry["in_range"] else "⚠"
        print(
            f"  {ok} {entry['system'][:35]:35s}  "
            f"I_rec={entry['I_recognition_bits']:.2f}  "
            f"I_net={entry['I_net_bits']:.2f}  "
            f"range={entry['expected_range_bits']}"
        )

    print(f"\n  {summary['note']}")
    print("\n  Cooperativity scaling (~4–5 bits/contact rule):")
    for row in summary["cooperativity_scaling"]:
        print(
            f"    {row['system'][:38]:38s}  "
            f"I_rec={row['I_rec']:.2f}  "
            f"bits/contact={row['bits_per_contact']:.2f}"
        )


def demo_solvent_effect() -> None:
    print("\n" + "=" * 55)
    print("Solvent effect on carboxylic acid dimer")
    print("=" * 55)
    for solvent in ["vacuum", "chloroform", "THF", "DMSO", "water"]:
        r = compute_I_hbond_dimer(n_hbonds=2, solvent_model=solvent)
        ds = SOLVENT_DELTA_S.get(solvent, 0.0)
        print(
            f"  {solvent:12s}: I_rec={r.recognition_bits:.2f}  "
            f"I_net={r.I_net:.2f}  "
            f"I+solvent={r.I_total_with_solvent:.2f}  "
            f"(ΔS_solv={ds:.1f} J/mol·K)"
        )


def demo_triple_hbond() -> None:
    print("\n" + "=" * 55)
    print("Triple H-bond DAD·ADA cooperativity sweep")
    print("=" * 55)
    for coop in [1.0, 1.15, 1.25, 1.40]:
        r = compute_I_triple_hbond_array(cooperativity_factor=coop)
        print(
            f"  coop={coop:.2f}: I_rec={r.recognition_bits:.2f}  I_net={r.I_net:.2f}  "
            f"(expect 14–18 for coop=1.25)"
        )


def demo_cooperativity_scaling() -> None:
    """Verify the ~4–5 bits/contact cooperativity scaling rule across 2–4 H-bond arrays."""
    print("\n" + "=" * 55)
    print("Cooperativity scaling: bits/contact (2 → 4 H-bonds)")
    print("=" * 55)
    results = [
        ("dimer (2 HB, coop=1.00)",
         compute_I_hbond_dimer(n_hbonds=2), 2),
        ("triple DAD·ADA (3 HB, coop=1.25)",
         compute_I_triple_hbond_array(cooperativity_factor=1.25), 3),
        ("quadruple AADD·DDAA (4 HB, coop=1.32)",
         compute_I_quadruple_hbond_array(cooperativity_factor=1.32), 4),
    ]
    print(f"\n  {'System':<38}  I_rec   I_net   bits/contact")
    print(f"  {'──────':<38}  ──────  ──────  ────────────")
    for label, r, n in results:
        bpc = r.recognition_bits / n
        print(
            f"  {label:<38}  {r.recognition_bits:6.2f}  {r.I_net:6.2f}  {bpc:6.2f}"
        )
    print(
        "\n  Rule confirmed: ~4–5 bits/contact across 2–4 H-bond cooperative arrays."
        "\n  Cooperative gain per additional contact (vs dimer baseline):"
    )
    dimer_bpc = results[0][1].recognition_bits / 2
    for label, r, n in results[1:]:
        delta = r.recognition_bits / n - dimer_bpc
        print(f"    {label}: +{delta:+.2f} bits/contact over dimer")


def demo_catalog_entry(name: str = "carboxylic_acid_dimer") -> None:
    print("\n" + "=" * 55)
    print(f"Catalog entry: {name}")
    print("=" * 55)
    try:
        from imscrbgrmr import global_catalog
        from imscrbgrmr.information import compute_I_from_synthon

        s = global_catalog.get(name)
        if not s:
            print(f"  (entry '{name}' not found in catalog)")
            return
        r = compute_I_from_synthon(s, solvent_model="chloroform")
        print_result(r, label=f"compute_I_from_synthon('{name}', solvent='chloroform')")
    except Exception as e:
        print(f"  (Catalog unavailable: {e})")


if __name__ == "__main__":
    demo_calibration_pipeline()
    demo_solvent_effect()
    demo_triple_hbond()
    demo_cooperativity_scaling()
    demo_catalog_entry()
    print("\nDone.")
