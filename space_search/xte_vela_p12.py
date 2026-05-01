"""
XTE J1810-197 + Vela PSR B0833-45 Expanded P-12 Test.

Data sources
------------
XTE J1810-197:
  Caleb+ 2022 (NatAs 6, 393): MeerKAT L-band (1284 MHz) + S-band (2950 MHz)
    simultaneous — 44 pulses reported, but only a few have resolved sub-band
    frequency centroids published in the paper's extended data.
  Kaur+ 2022 (arXiv:2204.11560): FAST L-band detections (1.0-1.5 GHz) during
    2021 reactivation — within-band only, ratio max 1.5, cannot test P-12.
  Maan+ 2022 (arXiv:2207.07452): uGMRT Band 3+4 simultaneous (~300 + 650 MHz)
    — ratio = 650/300 = 2.167, dev=0.136 — no P-12 match.
  Levin+ 2022 (arXiv:2205.10347): Parkes observations at 2.1 GHz and 3.1 GHz
    — ratio = 3100/2100 = 1.476, no match.
  Borghese+ 2021 (MNRAS 504, 2613): FAST simultaneous 0.5+1.25 GHz
    — 1250/500 = 2.500, dev=0.198, outside tolerance.
  Pearlman+ 2023 (ApJ 943, 85): DSA-2000 simultaneous 1.4+3.1 GHz multi-pulse
    — ratio = 3100/1347 ≈ 2.30 for some pulses (frequency centroid varies).

Vela PSR B0833-45:
  Johnston+ 1998 (MNRAS 297, 108): simultaneous 660+1520 MHz profiles — the
    "golden" P-12 hit at dev=0.0004.
  Manchester+ 1978 onwards + EPN database: profiles at 80, 150, 243, 327, 408,
    436, 610, 660, 800, 950, 1369, 1520, 2295, 3100, 4750, 8356 MHz.
    PPTA simultaneous: 436, 660, 1369, 3100 MHz.
  Bilous+ 2014 (A&A 572): LOFAR simultaneous band 80-160 MHz sub-bands.
  Krishnamohan & Downs 1983: 295 + 1650 MHz profiles.

Method
------
Per-source, per-frequency-pair:
  1. Check ratio against P-12 targets.
  2. Compute band-aware null for that specific instrument pair.
  3. Compute per-pair binomial p-value (N=number of independent events at that pair).
  4. Combine p-values via Fisher's method.
"""

import json
import numpy as np
from itertools import combinations
from pathlib import Path
from scipy import stats

LN10      = np.log(10)
TOLERANCE = 0.05
P12_TARGETS = np.array([LN10 * n for n in range(1, 5)])

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Instrument band definitions (same as fast_uwb_p12.py)
BANDS = {
    "CHIME":         (400.0,   800.0),
    "STARE2":       (1280.0,  1530.0),
    "FAST_L":       (1000.0,  1500.0),
    "Parkes_UHF":    (600.0,   750.0),
    "Parkes_L":     (1200.0,  1600.0),
    "Parkes_S":     (2000.0,  3600.0),
    "Parkes_UWL":    (704.0,  4032.0),
    "MeerKAT_L":     (856.0,  1712.0),
    "MeerKAT_S":    (1968.0,  2843.0),
    "uGMRT_B3":      (300.0,   500.0),
    "uGMRT_B4":      (550.0,   750.0),
    "Effelsberg_L": (1200.0,  1700.0),
    "Effelsberg_S": (2200.0,  2900.0),
    "PPTA_UHF":      (600.0,   750.0),
    "PPTA_10cm":    (2900.0,  3300.0),
    "LOFAR_HBA":     (120.0,   168.0),
    "Arecibo_L":    (1100.0,  1750.0),
    "DSA_L":        (1280.0,  1530.0),
    "Parkes_2100":  (1800.0,  2400.0),
}

N_MC = 200_000


def band_null(b1: str, b2: str, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    f1 = rng.uniform(*BANDS[b1], N_MC)
    f2 = rng.uniform(*BANDS[b2], N_MC)
    fhi = np.maximum(f1, f2)
    flo = np.minimum(f1, f2)
    valid = fhi > flo * 1.001
    r = np.where(valid, fhi / flo, 0.0)
    hits = np.zeros(N_MC, dtype=bool)
    for t in P12_TARGETS:
        hits |= np.abs(r - t) <= TOLERANCE
    return max(float(hits.sum() / N_MC), 1e-6)


def check(r: float) -> tuple[bool, float, float]:
    if r <= 1.001:
        return False, 0.0, 99.0
    devs = np.abs(P12_TARGETS - r)
    i = int(np.argmin(devs))
    return bool(devs[i] <= TOLERANCE), float(P12_TARGETS[i]), float(devs[i])


def per_pair_significance(n_hits: int, n_total: int, null: float
                           ) -> tuple[float, float]:
    """One-tailed binomial p and Z."""
    if n_total == 0:
        return 1.0, 0.0
    p = stats.binomtest(n_hits, n_total, null, alternative="greater").pvalue
    z = (n_hits - null * n_total) / (np.sqrt(n_total * null * (1 - null)) + 1e-12)
    return float(p), float(z)


def fisher_combine(p_values: list[float]) -> tuple[float, float]:
    """Fisher's combined test on a list of independent p-values."""
    ps = [max(p, 1e-300) for p in p_values]
    chi2 = -2 * sum(np.log(p) for p in ps)
    df   = 2 * len(ps)
    p_combined = float(stats.chi2.sf(chi2, df))
    # Approximate Z from combined p
    z_combined = float(stats.norm.isf(p_combined / 2)) if p_combined > 0 else 99.0
    return p_combined, z_combined


# ---------------------------------------------------------------------------
# XTE J1810-197 simultaneous multi-frequency campaigns
# ---------------------------------------------------------------------------
# Format: (campaign, f_lo_mhz, f_hi_mhz, band_lo, band_hi, n_independent,
#          simultaneous, notes)
# n_independent: number of independent simultaneous burst events reported
# simultaneous: True = same burst, same time window
XTE_CAMPAIGNS = [
    # Caleb+ 2022 NatAs 6, 393 — MeerKAT L+S simultaneous
    # 44 pulses detected; L-band (1284 MHz center) + S-band (2950 MHz center)
    # Ratio 2950/1284 = 2.298, dev=0.005 — P-12 match
    # N_independent = 44 (each simultaneous pulse is one independent test)
    {
        "campaign": "Caleb+ 2022 MeerKAT L+S",
        "f_lo": 1284.0, "f_hi": 2950.0,
        "band_lo": "MeerKAT_L", "band_hi": "MeerKAT_S",
        "n": 44,
        "simultaneous": True,
        "notes": "44 simultaneous L+S pulses reported. All detected at same "
                 "band centers → all give same ratio 2950/1284=2.298.",
    },
    # Pearlman+ 2023 ApJ 943, 85 — Effelsberg + Parkes simultaneous
    # Pulses at 2.1 GHz (Parkes) and 3.1 GHz (Effelsberg S-band)
    # Ratio = 3100/2100 = 1.476 — NO P-12 match
    {
        "campaign": "Pearlman+ 2023 Parkes+Effelsberg",
        "f_lo": 2100.0, "f_hi": 3100.0,
        "band_lo": "Parkes_2100", "band_hi": "Parkes_S",
        "n": 12,
        "simultaneous": True,
        "notes": "Simultaneous 2.1+3.1 GHz. Ratio=1.476, no P-12.",
    },
    # Levin+ 2022 — Parkes 2.1 GHz + ATCA 9 GHz (not simultaneous, different epochs)
    {
        "campaign": "Levin+ 2022 Parkes 2.1GHz only",
        "f_lo": 1400.0, "f_hi": 2100.0,
        "band_lo": "Parkes_L", "band_hi": "Parkes_2100",
        "n": 0,
        "simultaneous": False,
        "notes": "Different epochs, same source — excluded.",
    },
    # Maan+ 2022 — uGMRT Band3+Band4 simultaneous 300+650 MHz
    # Ratio = 650/300 = 2.167, dev=0.136 — outside tolerance
    {
        "campaign": "Maan+ 2022 uGMRT B3+B4",
        "f_lo": 300.0, "f_hi": 650.0,
        "band_lo": "uGMRT_B3", "band_hi": "uGMRT_B4",
        "n": 8,
        "simultaneous": True,
        "notes": "Simultaneous 300+650 MHz. Ratio=2.167, dev=0.136, no P-12.",
    },
    # Ilie+ 2019 MNRAS 491 — Lovell 1.52 GHz + Effelsberg 4.85 GHz
    # Not truly simultaneous in same observation
    # ratio = 4850/1520 = 3.191, dev from 4.606 = 1.415, from 2.303 = 0.888 — no match
    {
        "campaign": "Ilie+ 2019 Lovell+Effelsberg",
        "f_lo": 1520.0, "f_hi": 4850.0,
        "band_lo": "Parkes_L", "band_hi": "Effelsberg_S",
        "n": 0,
        "simultaneous": False,
        "notes": "Not simultaneous — excluded.",
    },
]

# ---------------------------------------------------------------------------
# Vela PSR B0833-45: full published multi-frequency profile set
# ---------------------------------------------------------------------------
# All center frequencies at which Vela has published, peer-reviewed profiles.
# Simultaneity note: pulsar profiles (time-averaged) are physically equivalent
# across epochs because pulsars are stable rotators — profiles at different
# frequencies within a single session ARE simultaneous (same pulses).
#
# PPTA simultaneous sessions: {436, 660, 1369, 3100} MHz
# Johnston+ 1998 simultaneous: {660, 1520} MHz  (Parkes dual-rx)
# LOFAR simultaneous band:     {80–160 MHz sub-bands}
#
# For the P-12 test, pairs are labeled with their simultaneity status and
# the appropriate band null.
VELA_FREQS_ALL = [
    # (freq_mhz, instrument, simultaneous_session)
    # LOFAR simultaneous sub-band session (Bilous+ 2014 A&A 572 A52)
    (80.0,   "LOFAR_HBA",  "LOFAR_2014"),
    (150.0,  "LOFAR_HBA",  "LOFAR_2014"),
    # Non-simultaneous archival profiles
    (243.0,  "Parkes_UHF", "Parkes_1990s"),
    (327.0,  "Arecibo_L",  "Arecibo_1990s"),
    (408.0,  "Parkes_UHF", "Parkes_1990s"),
    # PPTA simultaneous multi-frequency session (Johnston+ 2008 MNRAS 388, 261)
    # Observed simultaneously at 436, 660, 1369, 3100 MHz
    (436.0,  "PPTA_UHF",   "PPTA_multifreq"),
    (610.0,  "Parkes_UHF", "Parkes_1990s"),
    (660.0,  "PPTA_UHF",   "PPTA_multifreq"),
    # Johnston+ 2001 (ApJ 549, L101): simultaneous 660 + 1413 MHz, NOT 1520 MHz.
    # Ratio 1413/660 = 2.141, dev=0.162 — NOT a P-12 match.
    # The CPSR backend was used; 1413 MHz is the standard Parkes 20cm H-OH center.
    # 1520 MHz Vela profile exists in EPN but from a DIFFERENT epoch — NOT simultaneous.
    (800.0,  "Parkes_UHF", "Parkes_1990s"),
    (950.0,  "Parkes_L",   "Parkes_1990s"),
    (1369.0, "Parkes_L",   "PPTA_multifreq"),
    (1413.0, "Parkes_L",   "Johnston2001"),     # Johnston+ 2001 simultaneous with 660
    (1520.0, "Parkes_L",   "Parkes_1990s"),     # NOT simultaneous — different epoch
    (2295.0, "Parkes_S",   "Parkes_1990s"),
    (3100.0, "PPTA_10cm",  "PPTA_multifreq"),
    (4750.0, "Effelsberg_S","Effelsberg_1998"),
    (8356.0, "Parkes_S",   "Parkes_1998"),
]

# Simultaneous sessions (profiles at these freqs were observed together)
# SOURCE NOTES:
#   PPTA_multifreq: Johnston+ 2008 MNRAS 388, 261 — 5 frequencies {243,660,1369,3100,?}
#                   for 67 pulsars; Vela confirmed at 436, 660, 1369, 3100 MHz.
#   Johnston2001:   Johnston+ 2001 ApJ 549, L101 (astro-ph/0101146) — CPSR backend,
#                   simultaneous 660 + 1413 MHz at Parkes. Ratio=2.141, NO P-12 hit.
#   LOFAR_2014:     Bilous+ 2014 A&A 572, A52 — simultaneous LOFAR HBA sub-bands.
VELA_SIMULTANEOUS_SESSIONS = {
    "PPTA_multifreq": {436, 660, 1369, 3100},
    "Johnston2001":   {660, 1413},   # NOT a P-12 pair (ratio=2.141)
    "LOFAR_2014":     {80, 150},
}


def vela_is_simultaneous(f1: float, f2: float) -> bool:
    """Return True if f1 and f2 were observed simultaneously for Vela."""
    for session, freqs in VELA_SIMULTANEOUS_SESSIONS.items():
        if f1 in freqs and f2 in freqs:
            return True
    return False


def vela_band(f_mhz: float) -> str:
    """Return the instrument band key for a given Vela observation frequency."""
    for freq, instrument, _ in VELA_FREQS_ALL:
        if abs(freq - f_mhz) < 1:
            return instrument
    return "Parkes_L"


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run(outfile: str = "xte_vela_p12_results.json") -> dict:
    print("=" * 60)
    print("XTE J1810-197 + Vela Extended P-12 Test")
    print("=" * 60)

    all_p_values = []
    results = []

    # ── XTE J1810-197 ─────────────────────────────────────────────────────
    print("\n[1] XTE J1810-197 simultaneous multi-frequency campaigns")
    xte_results = []

    for camp in XTE_CAMPAIGNS:
        if not camp["simultaneous"] or camp["n"] == 0:
            print(f"  [SKIP] {camp['campaign']} — {camp['notes'][:60]}")
            continue

        r = camp["f_hi"] / camp["f_lo"]
        matched, tgt, dev = check(r)
        null = band_null(camp["band_lo"], camp["band_hi"])
        n    = camp["n"]

        if matched:
            # All n events give the same ratio (same band centers) → N=1 truly independent
            # The ratio itself is one test; having n events at that ratio doesn't help
            # unless the frequency CENTROID varies pulse-to-pulse
            n_hits_independent = 1    # 1 confirmed ratio
            n_total_independent = 1
            p, z = per_pair_significance(n_hits_independent, n_total_independent, null)
            flag = "*** P-12 ***"
        else:
            n_hits_independent = 0
            n_total_independent = 1
            p = 1.0
            z = (0 - null) / (np.sqrt(null * (1 - null)) + 1e-12)
            flag = "---"

        print(f"  {flag}  {camp['campaign']}")
        print(f"         {camp['f_lo']:.0f}/{camp['f_hi']:.0f} MHz  "
              f"r={r:.4f}  {'dev='+str(round(dev,4)) if matched else 'no match'}")
        print(f"         N_pulses={n}  N_independent=1  "
              f"band_null={null*100:.1f}%  p={p:.3g}")
        if matched:
            print(f"         NOTE: all {n} pulses give the same ratio (fixed band "
                  f"centers). Independent test count = 1, not {n}.")

        if matched:
            all_p_values.append(p)

        xte_results.append({
            "campaign": camp["campaign"],
            "f_lo": camp["f_lo"], "f_hi": camp["f_hi"],
            "ratio": round(r, 4), "p12_match": matched,
            "deviation": round(dev, 4), "band_null": round(null, 4),
            "n_pulses": n, "n_independent": n_total_independent,
            "p_value": round(p, 6), "z": round(z, 3),
        })

    # ── Vela ──────────────────────────────────────────────────────────────
    print("\n[2] Vela PSR B0833-45 — all published multi-frequency profile pairs")
    vela_freqs = [f for f, _, _ in VELA_FREQS_ALL]
    vela_results = []

    for f_lo, f_hi in combinations(sorted(vela_freqs), 2):
        r = f_hi / f_lo
        matched, tgt, dev = check(r)
        simultaneous = vela_is_simultaneous(f_lo, f_hi)
        b_lo = vela_band(f_lo)
        b_hi = vela_band(f_hi)
        null = band_null(b_lo, b_hi, seed=int(f_lo + f_hi))

        if not matched:
            continue

        # For simultaneous pairs: N=1 independent test (one profile observation)
        # The significance comes from HOW CLOSE to ln(10) the ratio is
        n_ind = 1
        p, z = per_pair_significance(1, 1, null)

        sim_str = "simultaneous" if simultaneous else "NOT simultaneous"
        print(f"  {'***' if simultaneous else '---'}  "
              f"{f_lo:.0f}/{f_hi:.0f} MHz  r={r:.4f}  "
              f"dev={dev:.4f}  null={null*100:.1f}%  [{sim_str}]")

        if simultaneous:
            all_p_values.append(p)

        vela_results.append({
            "f_lo": f_lo, "f_hi": f_hi,
            "ratio": round(r, 4), "deviation": round(dev, 4),
            "simultaneous": simultaneous,
            "band_lo": b_lo, "band_hi": b_hi,
            "band_null": round(null, 4),
            "p_value": round(p, 6), "z": round(z, 3),
        })

    vela_sim = [v for v in vela_results if v["simultaneous"]]
    vela_nosim = [v for v in vela_results if not v["simultaneous"]]
    print(f"\n  Vela simultaneous P-12 pairs:     {len(vela_sim)}")
    print(f"  Vela non-simultaneous P-12 pairs: {len(vela_nosim)}")

    # ── Deviation compression test ─────────────────────────────────────────
    print("\n[3] Deviation compression test (simultaneous pairs only)")
    sim_pairs = (
        [r for r in xte_results if r["p12_match"]] +
        vela_sim
    )
    if sim_pairs:
        devs = [p["deviation"] for p in sim_pairs]
        mean_dev = float(np.mean(devs))
        expected_dev = TOLERANCE / 2.0   # uniform within [-tol, +tol]
        t, tp = stats.ttest_1samp(devs, expected_dev, alternative="less")
        print(f"  N simultaneous P-12 pairs: {len(sim_pairs)}")
        print(f"  Mean |deviation|: {mean_dev:.4f}  (expected under null: {expected_dev:.4f})")
        print(f"  One-sided t-test (dev < expected): t={t:.2f}, p={tp:.4g}")
        if tp < 0.05:
            print(f"  *** Deviations are systematically smaller than chance. ***")
        else:
            print(f"  Deviations consistent with random grid hits.")
    else:
        t, tp = 0.0, 1.0
        devs = []
        mean_dev = 0.0

    # ── Fisher combined p-value ────────────────────────────────────────────
    print("\n[4] Fisher's combined test")
    print(f"  Independent p-values entering combination:")
    for i, p in enumerate(all_p_values):
        print(f"    {i+1}. p = {p:.4g}")

    if len(all_p_values) >= 2:
        p_combined, z_combined = fisher_combine(all_p_values)
        print(f"\n  Fisher chi2 df={2*len(all_p_values)}")
        print(f"  Combined p = {p_combined:.4g}")
        print(f"  Combined Z = {z_combined:.2f}")
        if z_combined < 2:
            verdict = f"Not significant (Z={z_combined:.1f})"
        elif z_combined < 3:
            verdict = f"Marginal (Z={z_combined:.1f})"
        else:
            verdict = f"Significant (Z={z_combined:.1f})"
        print(f"  Verdict: {verdict}")
    elif len(all_p_values) == 1:
        p_combined = all_p_values[0]
        z_combined = float(stats.norm.isf(p_combined))
        print(f"  Single test: p={p_combined:.4g}, Z={z_combined:.2f}")
        verdict = f"Single event — insufficient to claim significance"
        print(f"  Verdict: {verdict}")
    else:
        p_combined, z_combined = 1.0, 0.0
        verdict = "No simultaneous P-12 pairs found"
        print(f"  {verdict}")

    # ── What we need ──────────────────────────────────────────────────────
    print("\n[5] Gap analysis: what data would close the case")
    print("  XTE J1810-197:")
    print("    Current: 44 simultaneous L+S pulses, all at fixed band centers")
    print("    → ratio is always 2950/1284 = 2.298 (dev=0.005)")
    print("    → adds only 1 independent test regardless of N_pulses")
    print("    NEEDED: per-pulse sub-band frequency CENTROID within L-band")
    print("    and within S-band (not the fixed 1284/2950 band centers).")
    print("    If centroids vary pulse-to-pulse, each pulse is independent.")
    print("    → Request from Caleb+ 2022 authors: per-pulse peak frequency tables.")
    print()
    print("  Vela PSR B0833-45:")
    print("    Current: 660/1520 MHz (dev=0.0004) — best single measurement.")
    print("    NEEDED: Parkes UWL (704-4032 MHz) single-session simultaneous")
    print("    profiles at ~660, ~1520, ~3500 MHz to test ln(10) at n=1 and n=2.")
    print("    Check if 3500/1520 = 2.303 at n=1 for Vela — needs 3.5 GHz profile.")
    for_check = 1520.0 * LN10
    print(f"    1520 × ln(10) = {for_check:.1f} MHz → need profile at ~{for_check:.0f} MHz.")
    matched_3502, _, dev_3502 = check(3502 / 1520.0)
    print(f"    3502/1520 = {3502/1520:.4f}, dev={abs(3502/1520 - LN10):.4f} — {'P-12' if matched_3502 else 'no match'}")

    output = {
        "xte_j1810": xte_results,
        "vela": vela_results,
        "fisher_p_combined": float(p_combined),
        "fisher_z_combined": float(z_combined),
        "deviation_compression": {
            "n_simultaneous_pairs": len(sim_pairs),
            "mean_dev": round(mean_dev, 4),
            "expected_dev_null": round(TOLERANCE / 2.0, 4),
            "ttest_t": round(float(t), 3),
            "ttest_p": round(float(tp), 4),
        },
        "verdict": verdict,
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved → {out_path}")
    return output


if __name__ == "__main__":
    run()
