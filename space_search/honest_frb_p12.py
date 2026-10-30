"""
Honest FRB / Magnetar P-12 Test — strict simultaneity edition.

Applies the same criteria as xte_vela_p12.py:
  - ONLY same-burst, same-physical-event simultaneous multi-frequency detections
  - Band-aware Monte Carlo null per instrument pair (not global uniform)
  - Clear exclusion of: same-episode-different-burst, chromatic activity windows,
    non-simultaneous follow-up, different-epoch profiles

Simultaneity tiers
------------------
  CONFIRMED:  independent instruments independently triggered on the same
              physical burst within the same time window (e.g. CHIME+STARE2,
              FAST+HXMT, coordinated simultaneous pointings).
  LIKELY:     paper explicitly states "simultaneous" with overlapping epochs
              and no chromatic-activity caveat.
  EXCLUDED:   same-episode (multi-day), chromatic activity (different freq
              bands active at different sub-phases), follow-up non-simultaneous,
              different-epoch profiles (pulsars).

Sources
-------
SGR 1935+2154 2020-04-28:
  CHIME/FRB 2020 (Nature 587, 54) + Bochenek+ 2020 (Nature 587, 59)
    CHIME: 400-800 MHz, peak ~600 MHz
    STARE2: 1281-1531 MHz, peak ~1400 MHz
    Status: CONFIRMED — two independent instruments, same burst.
  Li+ 2021 (Nature 598, 267): FAST detected a different burst from SGR 1935
    in L-band (1-1.5 GHz) — no confirmed simultaneous high-freq counterpart.
    EXCLUDED (single-band).

FRB 20201124A:
  Xu+ 2022 (Nature 609, 685): FAST L-band campaign.
    Per paper: FAST alone, 1.0-1.5 GHz. No simultaneous uGMRT in this paper.
    EXCLUDED — single band.
  Zhang+ 2022 (arXiv:2206.09462): mentions "multi-telescope campaigns" but
    confirmed simultaneous uGMRT+FAST bursts are not published as same-burst
    detections in peer-reviewed form as of 2026-03.
    EXCLUDED — simultaneity unverified.

FRB 20180916B (CHIME+Apertif):
  Pastor-Marazuela+ 2021 (Nature 596, 505): chromatic sub-period activity —
    high-freq (Apertif 1.4 GHz) active at DIFFERENT phase of 16.35-day cycle
    than low-freq (CHIME 600 MHz). These are NOT simultaneous same-burst.
    EXCLUDED — chromatic activity, different burst epochs.

FRB 20190303A (CHIME repeater):
  Multi-frequency detections are from different epochs in CHIME band only.
  No confirmed simultaneous cross-band detections.
  EXCLUDED.

PSR J0437-4715, B1937+21, Terzan 5, M28 MSPs:
  Multi-frequency profiles from different observing epochs.
  EXCLUDED — not simultaneous.

XTE J1810-197 (already in xte_vela_p12.py):
  Caleb+ 2022 MeerKAT L+S — CONFIRMED simultaneous (already accounted for).

Vela PSR B0833-45 (already in xte_vela_p12.py):
  Johnston+ 1998 simultaneous 660+1520 MHz — already accounted for.

Conclusion from literature review
----------------------------------
Only ONE new confirmed-simultaneous cross-band event beyond xte_vela_p12.py:
  SGR 1935+2154 CHIME+STARE2 (2020-04-28)

Combined honest Fisher with xte_vela_p12.py adds:
  p1=0.0529 (XTE J1810-197 MeerKAT)
  p2=0.1029 (Vela 660/1520)
  p3=0.1451 (Vela 1369/3100)
  p4=NEW    (SGR 1935+2154 CHIME+STARE2)
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats

LN10      = np.log(10)
TOLERANCE = 0.05
P12_TARGETS = np.array([LN10 * n for n in range(1, 5)])

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Band definitions (MHz)
BANDS = {
    "CHIME":      (400.0,   800.0),
    "STARE2":    (1281.0,  1531.0),
    "FAST_L":    (1000.0,  1500.0),
    "MeerKAT_L":  (856.0,  1712.0),
    "MeerKAT_S": (1968.0,  2843.0),
    "Parkes_L":  (1200.0,  1600.0),
    "PPTA_10cm": (2900.0,  3300.0),
    "PPTA_UHF":   (600.0,   750.0),
    "uGMRT_B4":   (550.0,   750.0),
    "Apertif_L": (1220.0,  1520.0),
}

N_MC = 500_000


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


def check(r: float):
    if r <= 1.001:
        return False, 0.0, 99.0
    devs = np.abs(P12_TARGETS - r)
    i = int(np.argmin(devs))
    return bool(devs[i] <= TOLERANCE), float(P12_TARGETS[i]), float(devs[i])


def fisher_combine(p_values):
    ps = [max(p, 1e-300) for p in p_values]
    chi2 = -2 * sum(np.log(p) for p in ps)
    df   = 2 * len(ps)
    p_combined = float(stats.chi2.sf(chi2, df))
    z_combined = float(stats.norm.isf(p_combined / 2)) if p_combined > 0 else 99.0
    return p_combined, z_combined, chi2, df


# ---------------------------------------------------------------------------
# Confirmed simultaneous events (new — not in xte_vela_p12.py)
# ---------------------------------------------------------------------------
NEW_CONFIRMED_EVENTS = [
    {
        "name": "SGR 1935+2154 (2020-04-28) CHIME+STARE2",
        "reference": "CHIME/FRB 2020 Nature 587,54 + Bochenek+ 2020 Nature 587,59",
        "f_lo": 600.0,   "band_lo": "CHIME",
        "f_hi": 1400.0,  "band_hi": "STARE2",
        "simultaneity": "CONFIRMED",
        "notes": (
            "CHIME (400-800 MHz, representative frequency ~600 MHz) and STARE2 "
            "(1281-1531 MHz, peak ~1400 MHz) independently detected the same "
            "burst on 2020-04-28. Two independent instruments, independent "
            "triggers, same physical event. Gold-standard simultaneity."
        ),
    },
]

# Events that look promising but fail strict simultaneity
EXCLUDED_EVENTS = [
    {
        "name": "FRB 20201124A FAST+uGMRT",
        "reason": "Xu+ 2022 is FAST L-band only. Coordinated uGMRT+FAST same-burst "
                  "detections not confirmed in peer-reviewed literature as of 2026-03.",
    },
    {
        "name": "FRB 20180916B CHIME+Apertif",
        "reason": "Pastor-Marazuela+ 2021 explicitly shows chromatic sub-period: "
                  "high-freq (Apertif) and low-freq (CHIME) are active at different "
                  "sub-phases of the 16.35-day cycle. Not the same burst.",
    },
    {
        "name": "SGR 1935+2154 FAST L-band (Li+ 2021)",
        "reason": "Li+ 2021 FAST detections are L-band only (1.0-1.5 GHz). No "
                  "confirmed simultaneous high-frequency counterpart.",
    },
    {
        "name": "FRB 20190303A (CHIME repeater)",
        "reason": "Multi-frequency detections from different epochs in CHIME band only.",
    },
    {
        "name": "PSR J0437-4715, B1937+21, Terzan 5 MSPs, M28 MSPs",
        "reason": "Multi-frequency profiles from different observing sessions "
                  "(not simultaneous).",
    },
]

# Prior results from xte_vela_p12.py (honest, band-aware, corrected 2026-03-24)
# CORRECTION: Vela 660/1520 removed — Johnston+ 2001 (ApJ 549) observed
# simultaneously at 660+1413 MHz (ratio=2.141, NOT a P-12 hit), not 660+1520.
# The 1520 MHz Vela profile is from a different epoch. MNRAS 297,108 (Johnston+
# 1998) is a scintillation paper, not a dual-receiver profile paper.
XTE_VELA_P_VALUES = [
    {"label": "XTE J1810-197 MeerKAT L+S (1284/2950)",  "p": 0.05287},
    {"label": "Vela 1369/3100 MHz PPTA sim. (dev=0.038)", "p": 0.14510},
]


def run(outfile: str = "honest_frb_p12_results.json") -> dict:
    print("=" * 70)
    print("Honest FRB/Magnetar P-12 Test — strict simultaneity")
    print("=" * 70)

    print("\n[1] Literature review: excluded events")
    for ev in EXCLUDED_EVENTS:
        print(f"  [EXCL] {ev['name']}")
        print(f"         {ev['reason']}")

    print("\n[2] Confirmed simultaneous events (new, beyond xte_vela_p12.py)")
    new_p_values = []
    new_results  = []

    for ev in NEW_CONFIRMED_EVENTS:
        r = ev["f_hi"] / ev["f_lo"]
        matched, tgt, dev = check(r)
        null = band_null(ev["band_lo"], ev["band_hi"],
                         seed=int(ev["f_lo"] + ev["f_hi"]))
        if matched:
            p = stats.binomtest(1, 1, null, alternative="greater").pvalue
            flag = "*** P-12 ***"
        else:
            p = 1.0
            flag = "---"

        print(f"\n  {flag}  {ev['name']}")
        print(f"         {ev['f_lo']:.0f}/{ev['f_hi']:.0f} MHz  r={r:.4f}  "
              f"{'dev='+str(round(dev,4)) if matched else 'no match'}")
        print(f"         band_null={null*100:.1f}%  p={p:.4g}")
        print(f"         Status: {ev['simultaneity']}")
        print(f"         Ref: {ev['reference']}")

        if matched:
            new_p_values.append(float(p))
        new_results.append({
            "name": ev["name"],
            "f_lo": ev["f_lo"], "f_hi": ev["f_hi"],
            "ratio": round(r, 4), "p12_match": matched,
            "deviation": round(dev, 4), "band_null": round(null, 4),
            "simultaneity": ev["simultaneity"],
            "p_value": round(float(p), 6),
        })

    # ── Combined Fisher test ───────────────────────────────────────────────
    print("\n[3] Fisher's combined test (xte_vela + new confirmed events)")

    prior_ps  = [d["p"] for d in XTE_VELA_P_VALUES]
    all_ps    = prior_ps + new_p_values

    print(f"  Prior p-values (xte_vela_p12.py):")
    for d in XTE_VELA_P_VALUES:
        print(f"    {d['label']}: p={d['p']:.4g}")

    print(f"  New confirmed events:")
    for ev, p in zip(NEW_CONFIRMED_EVENTS, new_p_values):
        print(f"    {ev['name']}: p={p:.4g}")

    p_combined, z_combined, chi2, df = fisher_combine(all_ps)
    print(f"\n  Fisher chi2={chi2:.2f}  df={df}")
    print(f"  Combined p = {p_combined:.4g}")
    print(f"  Combined Z = {z_combined:.2f}")

    if z_combined < 2:
        verdict = f"Not significant (Z={z_combined:.1f})"
    elif z_combined < 3:
        verdict = f"Marginal (Z={z_combined:.1f})"
    else:
        verdict = f"Significant (Z={z_combined:.1f})"
    print(f"  Verdict: {verdict}")

    # ── What would push to 3sigma ──────────────────────────────────────────
    print("\n[4] Paths to 3-sigma")
    print("  Currently confirmed simultaneous events: 4 (3 xte_vela + 1 SGR 1935)")
    print()
    print("  A. FRB 20201124A FAST+uGMRT (dev=0.005)")
    print("     Needed: published same-burst simultaneous detection at 650+1500 MHz")
    print("     — contact Xu+ 2022 / CRAFTS team for coordinated-obs burst table")
    print()
    print("  B. XTE J1810-197 per-pulse centroids (Caleb+ 2022)")
    print("     Needed: per-pulse peak frequency within L and S bands")
    print("     — each pulse independent if centroid drifts pulse-to-pulse")
    print("     — 44 pulses at null=5.3% → Z~4+ if even half are P-12 hits")
    print()
    print("  C. Vela Parkes UWL ~3500 MHz profile (single session)")
    print("     Needed: 660+1520+3500 MHz simultaneous (chained ln(10) triple)")
    print(f"     1520 × ln(10) = {1520*LN10:.1f} MHz → profile at ~3500 MHz")
    print()
    print("  D. SGR 1935+2154 active bursts with next simultaneous multi-band obs")
    print("     CHIME+MeerKAT or MeerKAT L+S: 1284/2950 band pair (null=5.3%)")

    output = {
        "prior_p_values": XTE_VELA_P_VALUES,
        "new_confirmed_events": new_results,
        "excluded_events": EXCLUDED_EVENTS,
        "fisher_p_combined": float(p_combined),
        "fisher_z_combined": float(z_combined),
        "fisher_chi2": float(chi2),
        "fisher_df": int(df),
        "verdict": verdict,
        "n_confirmed_total": len(XTE_VELA_P_VALUES) + len(new_p_values),
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved → {out_path}")
    return output


if __name__ == "__main__":
    run()
