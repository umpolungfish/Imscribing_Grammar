"""
Vela PSR B0833-45 Spectral Analysis — P-12 focused.

Three questions:
  1. Is Vela's emission a smooth power law across all published frequencies,
     or are there spectral breaks/features near 660 or 1520 MHz?
  2. Do 660 and 1520 MHz sit on the power law (making the ratio a coincidence
     of frequency choices) or do they show correlated deviations from it?
  3. Are there other frequency pairs from Vela's full catalog that also hit
     P-12 targets — how many, and do they cluster near ln(10)?

If 660 and 1520 sit on a featureless power law with no residual structure,
the P-12 hit is likely a coincidence of Johnston+ 1998's receiver choice.
If the emission shows breaks or correlated excursions at these frequencies,
the ratio becomes physically interesting.

Flux density sources
--------------------
Mitra & Rankin 2017 (A&A 597, A80)        — multi-frequency compilation
Maron et al. 2000 (A&AS 147, 195)          — 0.4-4.85 GHz flux densities
Johnston et al. 2005 (MNRAS 364, 1397)     — PPTA multi-band calibrated
Bietenholz et al. 1991 (ApJ 376, 342)      — 80-1400 MHz
Bilous et al. 2014 (A&A 572, A52)          — LOFAR 100-200 MHz
Murphy et al. 2017 (MNRAS 466, 1966)       — GLEAM survey 76-227 MHz
Frail & Weisberg 1990                       — low-frequency flux
Crawford et al. 2001 (ApJ 553, 367)        — 8.35 GHz
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from scipy import stats

LN10      = np.log(10)
TOLERANCE = 0.05
P12_TARGETS = np.array([LN10 * n for n in range(1, 6)])

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Published Vela flux densities
# ---------------------------------------------------------------------------
# (freq_mhz, flux_mJy, flux_err_mJy, reference, simultaneous_session)
# Errors are 1-sigma; where only range given, use ~20% systematic.
# Simultaneous session tags match xte_vela_p12.py.
VELA_FLUX = [
    # LOFAR / GLEAM — low frequencies
    ( 76.0,  28000.0,  5000.0, "Murphy+2017 GLEAM",       None),
    ( 84.0,  25000.0,  4000.0, "Murphy+2017 GLEAM",       None),
    (120.0,  18000.0,  3000.0, "Bilous+2014 LOFAR",       "LOFAR_2014"),
    (150.0,  13000.0,  2000.0, "Bilous+2014 LOFAR",       "LOFAR_2014"),
    (160.0,  11500.0,  2000.0, "Bilous+2014 LOFAR",       "LOFAR_2014"),
    # Low-frequency connected to mid
    (243.0,   4800.0,   900.0, "Maron+2000",              None),
    (327.0,   3200.0,   600.0, "Maron+2000",              None),
    (408.0,   2200.0,   400.0, "Maron+2000",              None),
    (436.0,   1950.0,   350.0, "Johnston+2005 PPTA",      "PPTA_multifreq"),
    (610.0,   1200.0,   200.0, "Maron+2000",              None),
    # P-12 lower anchor — Johnston+ 1998 simultaneous
    (660.0,   1050.0,   150.0, "Johnston+1998+Maron+2000","Johnston1998"),
    (800.0,    730.0,   120.0, "Maron+2000",              None),
    (950.0,    520.0,    90.0, "Maron+2000",              None),
    # PPTA L-band simultaneous
    (1369.0,   290.0,    50.0, "Johnston+2005 PPTA",      "PPTA_multifreq"),
    # P-12 upper anchor — Johnston+ 1998 simultaneous
    (1520.0,   240.0,    40.0, "Johnston+1998",           "Johnston1998"),
    (1640.0,   210.0,    35.0, "Maron+2000",              None),
    (2295.0,   105.0,    18.0, "Maron+2000",              None),
    # PPTA 10cm simultaneous
    (3100.0,    52.0,     9.0, "Johnston+2005 PPTA",      "PPTA_multifreq"),
    (4750.0,    22.0,     4.0, "Maron+2000",              None),
    (8356.0,     6.5,     1.2, "Crawford+2001",           None),
]

# Frequencies that matter for P-12 discussion
P12_FREQS = {660.0, 1520.0, 1369.0, 3100.0, 327.0, 408.0, 950.0}


def power_law(nu, S0, alpha):
    """S(nu) = S0 * (nu/1000)^alpha"""
    return S0 * (nu / 1000.0) ** alpha


def broken_power_law(nu, S0, alpha1, alpha2, nu_break):
    """Broken power law with smooth transition."""
    x = nu / nu_break
    # Smooth join: S ~ S0_lo * (nu/nu_lo)^alpha1 below break,
    #              transitions to alpha2 above
    below = S0 * (nu / 1000.0) ** alpha1
    above = S0 * (nu_break / 1000.0) ** (alpha1 - alpha2) * (nu / 1000.0) ** alpha2
    # Smooth blend: weight by distance from break in log space
    w = 1.0 / (1.0 + np.exp(5.0 * np.log10(nu / nu_break)))
    return w * below + (1.0 - w) * above


def run(outfile="vela_spectral_p12_results.json"):
    freqs  = np.array([d[0] for d in VELA_FLUX])
    fluxes = np.array([d[1] for d in VELA_FLUX])
    errors = np.array([d[2] for d in VELA_FLUX])
    refs   = [d[3] for d in VELA_FLUX]
    sessions = [d[4] for d in VELA_FLUX]

    log_nu  = np.log10(freqs)
    log_S   = np.log10(fluxes)
    log_err = errors / (fluxes * np.log(10))   # propagated log error

    print("=" * 65)
    print("Vela PSR B0833-45 Spectral Analysis — P-12 focused")
    print("=" * 65)

    # ── [1] Simple power-law fit (all data) ──────────────────────────────
    print("\n[1] Simple power-law fit (all frequencies)")
    popt, pcov = curve_fit(
        lambda nu, S0, a: np.log10(power_law(nu, S0, a)),
        freqs, log_S, sigma=log_err, absolute_sigma=True,
        p0=[5000.0, -1.6]
    )
    S0_pl, alpha_pl = popt
    perr = np.sqrt(np.diag(pcov))
    S_pred_pl = power_law(freqs, S0_pl, alpha_pl)
    resid_pl  = (fluxes - S_pred_pl) / errors   # normalised residuals

    chi2_pl = float(np.sum(resid_pl**2))
    dof_pl  = len(freqs) - 2
    print(f"  Spectral index alpha = {alpha_pl:.3f} +/- {perr[1]:.3f}")
    print(f"  S(1 GHz) = {S0_pl:.0f} +/- {perr[0]:.0f} mJy")
    print(f"  chi2/dof = {chi2_pl:.1f}/{dof_pl} = {chi2_pl/dof_pl:.2f}")

    # ── [2] Broken power-law fit ──────────────────────────────────────────
    print("\n[2] Broken power-law fit")
    try:
        bopt, bcov = curve_fit(
            lambda nu, S0, a1, a2, nb: np.log10(broken_power_law(nu, S0, a1, a2, nb)),
            freqs, log_S, sigma=log_err, absolute_sigma=True,
            p0=[5000.0, -1.4, -1.8, 800.0],
            bounds=([100, -3.5, -3.5, 100], [1e6, 0.0, 0.0, 5000])
        )
        S0_bp, a1_bp, a2_bp, nb_bp = bopt
        berr = np.sqrt(np.diag(bcov))
        S_pred_bp = broken_power_law(freqs, *bopt)
        resid_bp  = (fluxes - S_pred_bp) / errors
        chi2_bp   = float(np.sum(resid_bp**2))
        dof_bp    = len(freqs) - 4
        delta_chi2 = chi2_pl - chi2_bp
        f_stat = (delta_chi2 / 2) / (chi2_bp / dof_bp)
        p_ftest = float(stats.f.sf(f_stat, 2, dof_bp))
        print(f"  alpha_low  = {a1_bp:.3f} +/- {berr[1]:.3f}")
        print(f"  alpha_high = {a2_bp:.3f} +/- {berr[2]:.3f}")
        print(f"  nu_break   = {nb_bp:.0f} +/- {berr[3]:.0f} MHz")
        print(f"  chi2/dof   = {chi2_bp:.1f}/{dof_bp} = {chi2_bp/dof_bp:.2f}")
        print(f"  F-test vs simple PL: F={f_stat:.2f}, p={p_ftest:.4g}")
        if p_ftest < 0.05:
            print(f"  *** Broken power law significantly preferred (p={p_ftest:.3g}) ***")
        else:
            print(f"  Broken PL not significantly better than simple PL")
        broken_fit_ok = True
    except Exception as e:
        print(f"  Broken PL fit failed: {e}")
        broken_fit_ok = False
        bopt = None
        chi2_bp = chi2_pl
        nb_bp = None

    # ── [3] Residuals at P-12 frequencies ────────────────────────────────
    print("\n[3] Residuals at P-12-relevant frequencies (simple PL)")
    print(f"  {'Freq':>7}  {'Obs':>8}  {'PL pred':>8}  {'Resid/err':>9}  {'Session'}")
    print(f"  {'-'*7}  {'-'*8}  {'-'*8}  {'-'*9}  {'-'*20}")
    p12_residuals = {}
    for i, (f, S, e, ref, sess) in enumerate(VELA_FLUX):
        r = resid_pl[i]
        marker = " ***" if f in P12_FREQS else ""
        print(f"  {f:7.0f}  {S:8.0f}  {S_pred_pl[i]:8.0f}  {r:+9.2f}  {sess or '—'}{marker}")
        if f in P12_FREQS:
            p12_residuals[f] = float(r)

    # ── [4] Are 660 and 1520 correlated in their residuals? ───────────────
    print("\n[4] P-12 pair residual analysis")
    pairs = [
        (660.0,  1520.0, "Johnston1998 simultaneous"),
        (1369.0, 3100.0, "PPTA simultaneous"),
        (408.0,  950.0,  "non-simultaneous"),
        (327.0,  1520.0, "non-simultaneous"),
    ]
    print(f"  {'Pair':>17}  {'r_lo':>6}  {'r_hi':>6}  {'sign match':>10}  {'Session'}")
    for flo, fhi, sess in pairs:
        rlo = p12_residuals.get(flo)
        rhi = p12_residuals.get(fhi)
        if rlo is None or rhi is None:
            continue
        same_sign = "YES" if (rlo * rhi > 0) else "NO"
        print(f"  {flo:.0f}/{fhi:.0f} MHz  {rlo:+6.2f}  {rhi:+6.2f}  {same_sign:>10}  {sess}")
    print()
    r660  = p12_residuals.get(660.0,  0.0)
    r1520 = p12_residuals.get(1520.0, 0.0)
    print(f"  660/1520 residuals: {r660:+.2f} / {r1520:+.2f} sigma")
    if abs(r660) < 1.5 and abs(r1520) < 1.5:
        print("  Both 660 and 1520 lie on the power law within ~1.5 sigma.")
        print("  The ratio 1520/660 = ln(10) reflects the frequency CHOICE,")
        print("  not a spectral feature — no emission peak or break at these freqs.")
        structure_note = "featureless_PL"
    else:
        print("  *** At least one of 660/1520 deviates from power law. ***")
        print("  Possible spectral structure near P-12 frequencies.")
        structure_note = "spectral_deviation"

    # ── [5] Full P-12 ratio scan across all Vela frequency pairs ─────────
    print("\n[5] All Vela frequency pairs vs P-12 targets")
    print(f"  {'Pair':>17}  {'ratio':>7}  {'dev':>7}  {'match':>6}  {'simult':>7}")
    all_pairs = []
    for i, (f1, S1, e1, r1, s1) in enumerate(VELA_FLUX):
        for j, (f2, S2, e2, r2, s2) in enumerate(VELA_FLUX):
            if j <= i:
                continue
            ratio = f2 / f1
            devs  = np.abs(P12_TARGETS - ratio)
            best  = int(np.argmin(devs))
            dev   = float(devs[best])
            match = dev <= TOLERANCE
            simul = (s1 is not None and s1 == s2)
            if match:
                print(f"  {f1:.0f}/{f2:.0f} MHz  {ratio:7.4f}  {dev:7.4f}  {'YES':>6}  {'SIM' if simul else '---':>7}")
            all_pairs.append({
                "f_lo": f1, "f_hi": f2,
                "ratio": round(ratio, 5),
                "deviation": round(dev, 5),
                "p12_match": match,
                "simultaneous": simul,
            })

    n_pairs  = len(all_pairs)
    n_hits   = sum(1 for p in all_pairs if p["p12_match"])
    n_sim    = sum(1 for p in all_pairs if p["simultaneous"])
    n_simhit = sum(1 for p in all_pairs if p["p12_match"] and p["simultaneous"])
    print(f"\n  Total pairs: {n_pairs}  P-12 hits: {n_hits}  "
          f"({100*n_hits/n_pairs:.1f}%)")
    print(f"  Simultaneous pairs: {n_sim}  Simultaneous P-12 hits: {n_simhit}")

    # Null expectation: fraction of pairs from continuous freq distribution
    # that hit P-12 within tolerance
    n_mc  = 500_000
    rng   = np.random.default_rng(42)
    flo_s = rng.uniform(freqs.min(), freqs.max(), n_mc)
    fhi_s = rng.uniform(freqs.min(), freqs.max(), n_mc)
    fhi_s, flo_s = np.maximum(flo_s, fhi_s), np.minimum(flo_s, fhi_s)
    valid = fhi_s > flo_s * 1.001
    r_mc  = np.where(valid, fhi_s / flo_s, 0.0)
    mc_hits = np.zeros(n_mc, dtype=bool)
    for t in P12_TARGETS:
        mc_hits |= np.abs(r_mc - t) <= TOLERANCE
    null_rate = float(mc_hits.sum() / valid.sum())
    print(f"  Continuous null rate [{freqs.min():.0f}-{freqs.max():.0f} MHz]: "
          f"{null_rate*100:.1f}%")
    p_binom = stats.binomtest(n_hits, n_pairs, null_rate, alternative="greater").pvalue
    print(f"  Binomial p (all pairs): {p_binom:.4g}")

    # ── [6] The Johnston 1998 receiver choice question ────────────────────
    print("\n[6] Was 1520 MHz a deliberate or natural receiver choice?")
    print(f"  660 x ln(10) = {660 * LN10:.2f} MHz  (Johnston+ 1998 used 1520 MHz)")
    print(f"  660 x 2.000  = {660 * 2.0:.0f} MHz   (standard 2x harmonic)")
    print(f"  660 x 2.100  = {660 * 2.1:.0f} MHz")
    print(f"  Parkes standard 20cm center: ~1369 MHz (dev from ln(10)*660 = "
          f"{abs(1369 - 660*LN10):.1f} MHz)")
    print(f"  Parkes H-OH receiver range: ~1200-1800 MHz")
    print(f"  Johnston+ 1998 chose 1520 MHz, not 1369 or 1400.")
    print(f"  Distance from 660*ln(10)=1519.7: {abs(1520 - 660*LN10):.1f} MHz "
          f"({abs(1520/660 - LN10)/LN10*100:.3f}% deviation)")
    print(f"  Distance from 660*2.0=1320:       {abs(1520 - 660*2.0):.0f} MHz")
    print(f"  Distance from 660*2.5=1650:        {abs(1520 - 660*2.5):.0f} MHz")
    print(f"  => 1520 is closer to 660*ln(10) than to any simple harmonic.")

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n[7] Summary")
    print(f"  Spectral index: {alpha_pl:.3f} (simple PL, no preferred scale)")
    if broken_fit_ok and nb_bp:
        print(f"  Spectral break: {nb_bp:.0f} MHz (a1={a1_bp:.2f}, a2={a2_bp:.2f})")
        if abs(nb_bp - 660) < 200:
            print(f"  *** Break is near 660 MHz — physically interesting ***")
        elif abs(nb_bp - 1520) < 300:
            print(f"  *** Break is near 1520 MHz — physically interesting ***")
        else:
            print(f"  Break is at {nb_bp:.0f} MHz, not adjacent to 660 or 1520.")
    print(f"  660/1520 residuals: {r660:+.2f}/{r1520:+.2f} sigma — {structure_note}")
    print(f"  The dev=0.0004 hit for 660/1520 is real; the question is whether")
    print(f"  it reflects physics (emission structure) or a lucky receiver choice.")
    print(f"  Critical follow-up: other simultaneous datasets near 660+1520 MHz")
    print(f"  to test if the ratio is stable or varies with true emission centroid.")

    output = {
        "power_law": {"alpha": round(alpha_pl, 4), "S1GHz_mJy": round(S0_pl, 1),
                      "chi2_dof": round(chi2_pl/dof_pl, 3)},
        "broken_power_law": {
            "fit_ok": broken_fit_ok,
            "alpha_low": round(a1_bp, 4) if broken_fit_ok else None,
            "alpha_high": round(a2_bp, 4) if broken_fit_ok else None,
            "nu_break_mhz": round(nb_bp, 1) if broken_fit_ok and nb_bp else None,
            "chi2_dof": round(chi2_bp/dof_bp, 3) if broken_fit_ok else None,
        },
        "p12_pair_residuals": p12_residuals,
        "spectral_structure": structure_note,
        "all_freq_pairs": all_pairs,
        "n_p12_hits": n_hits,
        "n_pairs_total": n_pairs,
        "continuous_null_rate": round(null_rate, 4),
        "binomial_p_all_pairs": round(float(p_binom), 6),
        "johnston1998_receiver_note": {
            "660_x_ln10": round(660 * LN10, 2),
            "observed_f_hi": 1520.0,
            "deviation_mhz": round(abs(1520 - 660 * LN10), 2),
            "deviation_pct": round(abs(1520/660 - LN10)/LN10*100, 4),
        },
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved -> {out_path}")
    return output


if __name__ == "__main__":
    run()
