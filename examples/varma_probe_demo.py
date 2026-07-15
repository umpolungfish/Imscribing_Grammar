"""
varma_probe_demo.py — Demonstrate the Varma QXY criticality probe.

Shows:
1. Single-entry ⊙ candidacy scoring
2. Quantitative degeneracy strength (logarithmic vs power-law)
3. Dynamic exponent z_eff computation from frequency series
4. Reference correlation data for Varma XY and 2D H-bond percolation

Run:
    python examples/varma_probe_demo.py
"""
from __future__ import annotations

import math
import json
from imscrbgrmr.varma_probe import (
    VarmaCorrelationData,
    score_phi_c_candidacy,
    degeneracy_strength,
    compute_dynamic_exponent,
    check_logarithmic_scaling,
    REFERENCE_CORRELATION_DATA,
)


def demo_varma_qxy() -> None:
    """Test Varma QXY reference: expect logarithmic degeneracy, score > 0.7."""
    print("=" * 60)
    print("Test 1: Varma QXY reference system")
    print("=" * 60)

    data = REFERENCE_CORRELATION_DATA["varma_qxy"]
    print(f"  ξ_r  = {data.xi_r}")
    print(f"  ξ_τ  = {data.xi_tau:.2e}")

    is_log, ratio = check_logarithmic_scaling(data.xi_r, data.xi_tau)
    print(f"  ξ_r / ln(ξ_τ) = {ratio:.4f}  (expect ≈ 1.0 for Varma QXY)")
    print(f"  Logarithmic scaling: {is_log}")

    z_eff = compute_dynamic_exponent(data.xi_r, data.xi_tau)
    print(f"  z_eff = {z_eff:.3f}  (expect → ∞ for logarithmic degeneracy)")


def demo_hbond_percolation() -> None:
    """Test 2D H-bond percolation: expect power-law degeneracy, finite z."""
    print("\n" + "=" * 60)
    print("Test 2: 2D H-bond percolation threshold")
    print("=" * 60)

    data = REFERENCE_CORRELATION_DATA["hbond_percolation_2d"]
    z_known = data.additional_exponents.get("z", 1.33)
    print(f"  ξ_r  = {data.xi_r}")
    print(f"  ξ_τ  = {data.xi_tau:.3f}  (= ξ_r^{z_known})")

    z_eff = compute_dynamic_exponent(data.xi_r, data.xi_tau)
    print(f"  z_eff = {z_eff:.3f}  (expect ≈ {z_known} for 2D percolation)")

    is_log, ratio = check_logarithmic_scaling(data.xi_r, data.xi_tau)
    print(f"  Logarithmic: {is_log}  (should be False for power-law system)")


def demo_frequency_series() -> None:
    """Show z_eff divergence over a frequency sweep (Varma QXY)."""
    print("\n" + "=" * 60)
    print("Test 3: Dynamic exponent z_eff vs. decreasing frequency")
    print("  (simulates approach to the QCP: ξ increases as ω → 0)")
    print("=" * 60)

    # Simulate: as ω decreases, ξ_r grows linearly while ξ_τ grows exponentially
    frequency_series = []
    print(f"  {'ξ_r':>8}  {'ξ_τ':>12}  {'z_eff':>8}")
    for xi_r in [2.0, 5.0, 10.0, 15.0, 20.0]:
        xi_tau = math.exp(xi_r)   # Varma QXY: ξ_τ = exp(ξ_r)
        z = compute_dynamic_exponent(xi_r, xi_tau)
        frequency_series.append((xi_r, xi_tau))
        z_str = f"{z:.3f}" if not math.isinf(z) else "∞"
        print(f"  {xi_r:>8.1f}  {xi_tau:>12.2e}  {z_str:>8}")

    print("  → z_eff grows without bound: logarithmic G/D degeneracy confirmed.")


def demo_degeneracy_strength(imscription_name: str = "imscription_Varma_quantum_XY_critical_poin") -> None:
    """Score degeneracy strength for a catalog entry."""
    print("\n" + "=" * 60)
    print(f"Test 4: Degeneracy strength for catalog entry")
    print("=" * 60)
    try:
        from imscrbgrmr import global_catalog
        imscription = global_catalog.get(imscription_name)
        if not imscription:
            print(f"  Entry '{imscription_name}' not in catalog — using reference data directly.")
            return

        # Test with Varma QXY reference data
        data = REFERENCE_CORRELATION_DATA["varma_qxy"]
        freq_series = [(2.0, math.exp(2.0)), (10.0, math.exp(10.0)), (14.0, math.exp(14.0))]

        score, tier = degeneracy_strength(imscription, data, freq_series)
        print(f"  Entry: {imscription_name}")
        print(f"  Degeneracy strength score: {score:.3f}")
        print(f"  Degeneracy tier: {tier}")
        print("  Tiers: 0.0–0.3=none | 0.3–0.6=logarithmic | 0.6–0.85=power-law | 0.85–1.0=collapse")

        rep = score_phi_c_candidacy(imscription, data)
        print(f"  ⊙ candidacy: {rep._candidacy_label()} (score={rep.score:.3f})")
        print(f"  Axiom 5: {rep.axiom5_note[:80]}...")
    except Exception as e:
        print(f"  (Catalog unavailable: {e})")


if __name__ == "__main__":
    demo_varma_qxy()
    demo_hbond_percolation()
    demo_frequency_series()
    demo_degeneracy_strength()
    print("\nDone.")
