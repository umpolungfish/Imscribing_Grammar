"""
Null test for P-12 criticality receipt.

Problem: the ±0.05 tolerance window is wide enough that random peaks in red
noise produce spurious ln(10) ratio matches. We need to know the background rate.

Method (shuffle test):
  1. Take real (or simulated) residuals for each pulsar.
  2. Randomly shuffle the time labels N=1000 times, breaking any real structure.
  3. Run the same P-12 test on each shuffle.
  4. Background rate = mean P-12 hits per shuffle ± std.
  5. Z-score = (real_hits - background_mean) / background_std.

A real P-12 signal should give Z > 3 on at least one pulsar.

Also computes Monte Carlo p-value for the stacked ln(10) peak count.
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

from pulsar_stack import (
    NANOGRAV_15YR, DM_DENSITY_WEIGHTS,
    simulate_residuals, load_real_residuals, power_spectrum, test_ln10_periodicity,
)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

N_SHUFFLES = 1000
RNG = np.random.default_rng(0)


def shuffle_test_pulsar(name: str, rms: float, n_toas: int,
                         timespan: float, n_shuffles: int = N_SHUFFLES) -> dict:
    """
    Run shuffle null test for a single pulsar.
    Uses real NANOGrav residuals if available, otherwise simulated.
    Returns real hit count, background distribution, and Z-score.
    """
    real = load_real_residuals(name)
    if real is not None:
        times, resids = real
        source = "REAL"
    else:
        times, resids = simulate_residuals(rms, n_toas, timespan, seed=hash(name) % (2**31))
        source = "sim"
    freqs, power = power_spectrum(times, resids)
    real_hits = len(test_ln10_periodicity(freqs, power))

    # Shuffle distribution
    null_hits = []
    for _ in range(n_shuffles):
        shuffled = RNG.permutation(resids)
        freqs_s, power_s = power_spectrum(times, shuffled)
        null_hits.append(len(test_ln10_periodicity(freqs_s, power_s)))

    null_arr = np.array(null_hits)
    bg_mean = float(np.mean(null_arr))
    bg_std  = float(np.std(null_arr)) + 1e-9
    z_score = (real_hits - bg_mean) / bg_std
    p_value = float(np.mean(null_arr >= real_hits))

    return {
        "name": name,
        "source": source,
        "real_hits": real_hits,
        "bg_mean": round(bg_mean, 2),
        "bg_std":  round(bg_std, 3),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "significant": z_score > 2.5 and p_value < 0.02,
        "null_distribution": null_hits,
    }


def run_null_tests(outfile: str = "p12_null_test.json") -> list[dict]:
    """Run shuffle null tests across all NANOGrav 15yr pulsars."""
    print("=== P-12 Null Test (Shuffle Method) ===")
    print(f"  N_SHUFFLES = {N_SHUFFLES} per pulsar")
    print(f"  Significance threshold: Z > 2.5, p < 0.02")
    print()

    results = []
    for name, ra, dec, dm, n_toas, rms, timespan in NANOGRAV_15YR:
        w = DM_DENSITY_WEIGHTS.get(name, 0.5)
        print(f"  {name:20s}  DM={dm:7.1f}  w={w:.2f} ...", end=" ", flush=True)
        r = shuffle_test_pulsar(name, rms, n_toas, timespan)
        results.append({**r, "dm_pc_cm3": dm, "dm_weight": w})
        sig = "*** SIGNIFICANT ***" if r["significant"] else ""
        print(f"[{r['source']}] real={r['real_hits']:3d}  bg={r['bg_mean']:.1f}±{r['bg_std']:.1f}  "
              f"Z={r['z_score']:+.2f}  p={r['p_value']:.3f}  {sig}")

    # Summary
    n_sig = sum(1 for r in results if r["significant"])
    high_dm_sig = [r for r in results if r["significant"] and r["dm_weight"] >= 0.7]
    print(f"\n  Significant pulsars: {n_sig}/{len(results)}")
    print(f"  High-DM significant (w≥0.7): {len(high_dm_sig)}")
    for r in high_dm_sig:
        print(f"    {r['name']}  Z={r['z_score']:+.2f}  DM={r['dm_pc_cm3']:.1f}  w={r['dm_weight']:.2f}")

    # Combined p-value across pulsars (Fisher's method)
    p_vals = [r["p_value"] for r in results]
    chi2_stat = -2 * sum(np.log(max(p, 1e-10)) for p in p_vals)
    combined_p = float(stats.chi2.sf(chi2_stat, df=2 * len(p_vals)))
    print(f"\n  Combined p-value (Fisher): {combined_p:.4e}")
    print(f"  Combined Z (approx): {stats.norm.isf(combined_p / 2):.2f}")

    output = {
        "n_shuffles": N_SHUFFLES,
        "n_pulsars": len(results),
        "n_significant": n_sig,
        "high_dm_significant": [r["name"] for r in high_dm_sig],
        "combined_p_value": combined_p,
        "combined_z": float(stats.norm.isf(max(combined_p / 2, 1e-15))),
        "per_pulsar": [{k: v for k, v in r.items() if k != "null_distribution"}
                       for r in results],
    }

    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved → {out_path}")
    return results


if __name__ == "__main__":
    run_null_tests()
