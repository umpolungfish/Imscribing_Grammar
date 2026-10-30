"""
Parkes UWL (704-4032 MHz) FRB Sub-band P-12 Search.

The UWL records the full 704-4032 MHz band simultaneously in a single feed.
Any FRB that shows emission at two non-adjacent sub-band peaks within a
single UWL recording is a genuine simultaneous multi-frequency detection —
same burst, same instrument, no simultaneity ambiguity.

For P-12 (ln(10) = 2.303), accessible pairs within 704-4032 MHz:
  n=1: ratio ~2.303 → e.g. 800/1842, 1000/2303, 1300/2994, 1520/3501
  n=2: ratio ~4.606 → e.g. 704/3244, 800/3685

Method
------
1. Compile all published FRBs with Parkes UWL observations where sub-band
   spectral analysis is reported (peak frequency, emission centroid, or
   sub-burst centre frequencies published).
2. For each event, test all pairs of reported sub-band emission peaks against
   P-12 targets using UWL-specific band-aware null.
3. Fisher combine confirmed simultaneous hits.

Sources
-------
Day+ 2020 (MNRAS 497, 3335)          — FRB 20181112A Parkes UWL sub-band
Cho+ 2020 (ApJ 891, L38)             — FRB 20190611B Parkes UWL
Pilia+ 2020 (ApJ 896, L40)           — FRB 20200428 SGR1935 Parkes UWL
Kumar+ 2021 (MNRAS 500, 2525)        — CRAFT ICS FRBs with Parkes UWL follow-up
Shannon+ 2018 (Nature 562, 386)      — ASKAP-detected FRBs, Parkes follow-up
Farah+ 2018 (MNRAS 478, 1209)        — commensal UWL data
Ravi+ 2023 (ApJ 949, L3)             — FRB 20220912A DSA+follow-up
CHIME/FRB Catalog 1 (2021)           — repeaters with UWL follow-up
Nimmo+ 2022 (NatAs 6, 393)           — FRB 20210807D sub-ms structure
Majid+ 2021                          — DSA-2000 simultaneous

Notes on what counts
--------------------
COUNTS: A burst where two distinct emission peaks separated by >10% of the
        band are reported with measured centre frequencies within a SINGLE
        UWL observation. Both peaks are from the same physical burst.

DOES NOT COUNT:
  - Separate bursts in the same session (different physical events)
  - Single narrowband bursts that happen to touch two sub-bands
  - Follow-up observations at a different epoch than the detection
  - Bursts where only one sub-band shows emission
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

# UWL covers 704-4032 MHz as a single simultaneous receiver
UWL_BAND = (704.0, 4032.0)
N_MC = 500_000


def uwl_null(seed=42):
    """Band-aware null rate for two independent sub-band peaks within UWL."""
    rng = np.random.default_rng(seed)
    f1 = rng.uniform(*UWL_BAND, N_MC)
    f2 = rng.uniform(*UWL_BAND, N_MC)
    fhi = np.maximum(f1, f2)
    flo = np.minimum(f1, f2)
    # Require the two peaks to be well-separated (>10% of geometric mean)
    sep = (fhi - flo) / np.sqrt(fhi * flo)
    valid = sep > 0.10
    r = np.where(valid, fhi / flo, 0.0)
    hits = np.zeros(N_MC, dtype=bool)
    for t in P12_TARGETS:
        hits |= np.abs(r - t) <= TOLERANCE
    return max(float(hits[valid].sum() / valid.sum()), 1e-6)


def check(r):
    if r <= 1.001:
        return False, 0.0, 99.0
    devs = np.abs(P12_TARGETS - r)
    i = int(np.argmin(devs))
    return bool(devs[i] <= TOLERANCE), float(P12_TARGETS[i]), float(devs[i])


# ---------------------------------------------------------------------------
# Catalog of UWL FRBs with reported sub-band spectral structure
# ---------------------------------------------------------------------------
# Format: name, sub-band peak frequencies (MHz), status, reference, notes
#
# "status" codes:
#   CONFIRMED_SUBBAND: Two distinct sub-band peaks measured in single recording
#   SINGLE_BAND:       Only one emission peak / narrowband — no ratio possible
#   ADJACENT:          Two peaks but in adjacent sub-bands (ratio too small)
#   NO_UWL:            Not a UWL observation
#   UNRESOLVED:        Sub-band structure unclear from published data

UWL_CATALOG = [

    # ── FRB 20181112A (ASKAP detect + Parkes UWL follow-up) ─────────────
    {
        "name": "FRB 20181112A",
        "peak_freqs_mhz": [1300.0],
        "status": "SINGLE_BAND",
        "reference": "Prochaska+ 2019 Science 366, 231; Day+ 2020 MNRAS 497, 3335",
        "notes": "Single-band detection at ~1.3 GHz. No second sub-band peak reported.",
    },

    # ── FRB 20190611B (Parkes UWL real-time) ────────────────────────────
    {
        "name": "FRB 20190611B",
        "peak_freqs_mhz": [1632.0],
        "status": "SINGLE_BAND",
        "reference": "Cho+ 2020 ApJ 891 L38",
        "notes": "Detected at ~1.6 GHz. Narrowband; no second peak.",
    },

    # ── SGR 1935+2154 (Parkes UWL 2020-04-28) ───────────────────────────
    # CHIME+STARE2 confirmed simultaneous at 600+1400 MHz (already in honest_frb)
    # Parkes UWL was also observing — did it detect any sub-band structure?
    {
        "name": "SGR 1935+2154 (Parkes UWL 2020-04-28)",
        "peak_freqs_mhz": [1300.0],
        "status": "SINGLE_BAND",
        "reference": "Pilia+ 2020 ApJ 896 L40; Bailes+ 2021",
        "notes": (
            "Parkes UWL detected the burst at ~1.3 GHz during the 2020-04-28 event. "
            "Published spectrum shows single-peaked emission. No confirmed second "
            "sub-band peak at a widely different frequency in the UWL data."
        ),
    },

    # ── FRB 20201124A (FAST + possible UWL follow-up) ────────────────────
    {
        "name": "FRB 20201124A",
        "peak_freqs_mhz": [1250.0],
        "status": "SINGLE_BAND",
        "reference": "Xu+ 2022 Nature 609, 685",
        "notes": (
            "FAST L-band (1.0-1.5 GHz) detections. No confirmed simultaneous "
            "Parkes UWL multi-sub-band detection of the same burst in peer-reviewed form."
        ),
    },

    # ── FRB 20210807D (Nimmo+ 2022 sub-ms structure) ─────────────────────
    {
        "name": "FRB 20210807D",
        "peak_freqs_mhz": [1400.0, 1600.0],
        "status": "ADJACENT",
        "reference": "Nimmo+ 2022 NatAs 6, 393",
        "notes": (
            "Sub-ms sub-burst structure. Two components at ~1400 and ~1600 MHz — "
            "ratio 1.14, far from ln(10). Adjacent sub-bands only."
        ),
    },

    # ── FRB 20220912A (DSA-110, Parkes UWL follow-up) ────────────────────
    {
        "name": "FRB 20220912A",
        "peak_freqs_mhz": [1300.0],
        "status": "SINGLE_BAND",
        "reference": "Ravi+ 2023 ApJ 949 L3; McKinven+ 2023",
        "notes": "High-activity repeater. Most bursts narrowband 1-1.5 GHz. "
                 "No published dual-peak UWL burst.",
    },

    # ── FRB 20121102A (R1, CHIME + Effelsberg + Parkes UWL campaigns) ────
    {
        "name": "FRB 20121102A (R1)",
        "peak_freqs_mhz": [1370.0],
        "status": "SINGLE_BAND",
        "reference": "Michilli+ 2018; Rajwade+ 2020; Cruces+ 2021",
        "notes": (
            "Extensively studied repeater. Burst spectra are narrowband and drift "
            "downward in frequency. No single-burst dual-peak UWL detection reported."
        ),
    },

    # ── FRB 20190520B (FAST + Parkes UWL, 2024) ──────────────────────────
    # arXiv:2507.17696: narrowband burst at ~1632 MHz centre, FAST upper edge + Parkes
    {
        "name": "FRB 20190520B (2024 FAST+UWL)",
        "peak_freqs_mhz": [1632.0],
        "status": "SINGLE_BAND",
        "reference": "arXiv:2507.17696; CPL 41, 109501 (2024)",
        "notes": (
            "FAST (1.05-1.45 GHz upper limit) + Parkes UWL (1.5-1.8 GHz range). "
            "Burst centroid ~1632 MHz, narrowband, no emission below 1200 MHz. "
            "Single emission feature spanning the gap between two adjacent receivers — "
            "not a two-frequency detection."
        ),
    },

    # ── FRB 20240114A (Tianma 2.25 GHz + no 8.6 GHz burst) ──────────────
    {
        "name": "FRB 20240114A",
        "peak_freqs_mhz": [2250.0],
        "status": "SINGLE_BAND",
        "reference": "arXiv:2025 (IOPscience 10.3847/1538-4357/adfece)",
        "notes": (
            "155 bursts at 2.25 GHz (Tianma), 0 at 8.60 GHz. "
            "No dual-peak detection. Ratio 8600/2250=3.82, dev from 4*ln10=0.78 — no match."
        ),
    },

    # ── FRB 20180916B (CHIME + UWL follow-up campaigns) ──────────────────
    {
        "name": "FRB 20180916B",
        "peak_freqs_mhz": [600.0],
        "status": "SINGLE_BAND",
        "reference": "Pastor-Marazuela+ 2021 Nature 596, 505",
        "notes": (
            "Chromatic 16.35-day activity: high-freq active at different sub-phase "
            "than low-freq. No simultaneous dual-peak detection."
        ),
    },

    # ── FRB 20201124A CRAFTS/FAST sub-band analysis ───────────────────────
    # Some papers report drift rates and sub-burst structure
    # Zhang+ 2022 mentions multi-component bursts but within L-band only
    {
        "name": "FRB 20201124A (Zhang+ 2022 sub-burst)",
        "peak_freqs_mhz": [1100.0, 1350.0],
        "status": "ADJACENT",
        "reference": "Zhang+ 2022 arXiv:2206.09462",
        "notes": (
            "Sub-burst components at ~1100 and ~1350 MHz within FAST L-band. "
            "Ratio 1350/1100 = 1.23, far from ln(10). Adjacent sub-bands only."
        ),
    },

]

# ---------------------------------------------------------------------------
# What a positive detection would require
# ---------------------------------------------------------------------------
IDEAL_DETECTION_TARGETS = [
    {
        "f_lo": 800.0, "f_hi": 1842.0,
        "ratio": 1842/800, "dev": abs(1842/800 - LN10),
        "note": "Low UWL sub-band + mid-band, ratio = ln(10)",
    },
    {
        "f_lo": 1000.0, "f_hi": 2303.0,
        "ratio": 2303/1000, "dev": abs(2303/1000 - LN10),
        "note": "1 GHz + 2.3 GHz within UWL, perfect ln(10)",
    },
    {
        "f_lo": 1300.0, "f_hi": 2994.0,
        "ratio": 2994/1300, "dev": abs(2994/1300 - LN10),
        "note": "1.3 + 3.0 GHz within UWL",
    },
    {
        "f_lo": 1520.0, "f_hi": 3500.0,
        "ratio": 3500/1520, "dev": abs(3500/1520 - LN10),
        "note": "Parkes L-band center + 3.5 GHz (Vela gap-analysis target)",
    },
    {
        "f_lo": 704.0, "f_hi": 3244.0,
        "ratio": 3244/704, "dev": abs(3244/704 - 2*LN10),
        "note": "n=2 target: UWL low edge + 3.2 GHz",
    },
]


def run(outfile="uwl_frb_p12_results.json"):
    print("=" * 65)
    print("Parkes UWL FRB Sub-band P-12 Search")
    print("=" * 65)

    null = uwl_null()
    print(f"\nUWL band-aware null rate (separation >10%): {null*100:.1f}%")

    # ── Catalog analysis ─────────────────────────────────────────────────
    print("\n[1] UWL FRB catalog — sub-band structure assessment")
    print(f"  {'Name':35s}  {'Status':20s}  {'Result'}")
    print(f"  {'-'*35}  {'-'*20}  {'-'*30}")

    confirmed_hits = []
    all_results = []

    for ev in UWL_CATALOG:
        freqs = ev["peak_freqs_mhz"]
        status = ev["status"]

        if status != "CONFIRMED_SUBBAND" or len(freqs) < 2:
            result_str = "—"
            p12_match = False
            ratio = None
            dev = None
        else:
            # Check all pairs
            best_dev = 99.0
            best_ratio = None
            for i, f1 in enumerate(sorted(freqs)):
                for f2 in sorted(freqs)[i+1:]:
                    r = f2 / f1
                    matched, tgt, d = check(r)
                    if d < best_dev:
                        best_dev = d
                        best_ratio = r
            p12_match = best_dev <= TOLERANCE
            ratio = best_ratio
            dev = best_dev
            result_str = (f"r={ratio:.4f} dev={dev:.4f} "
                          f"{'*** P-12 ***' if p12_match else 'no match'}")

        print(f"  {ev['name']:35s}  {status:20s}  {result_str}")

        if p12_match:
            p = stats.binomtest(1, 1, null, alternative="greater").pvalue
            confirmed_hits.append({
                "name": ev["name"],
                "ratio": round(ratio, 4),
                "deviation": round(dev, 4),
                "p_value": float(p),
                "reference": ev["reference"],
            })

        all_results.append({
            "name": ev["name"],
            "status": status,
            "peak_freqs_mhz": freqs,
            "p12_match": p12_match,
            "ratio": round(ratio, 4) if ratio else None,
            "deviation": round(dev, 4) if dev else None,
        })

    print(f"\n  Confirmed simultaneous UWL sub-band P-12 hits: {len(confirmed_hits)}")

    if not confirmed_hits:
        print("  None found in published literature.")
        print("  All UWL FRBs with published sub-band analysis show either:")
        print("    (a) single narrowband emission peaks, or")
        print("    (b) adjacent sub-band structure with ratio << ln(10)")

    # ── What a positive detection would look like ─────────────────────────
    print("\n[2] Target frequency pairs within UWL for a P-12 detection")
    print(f"  UWL covers {UWL_BAND[0]:.0f}-{UWL_BAND[1]:.0f} MHz simultaneously.")
    print(f"  For a burst to hit P-12, it needs two peaks at:")
    for t in IDEAL_DETECTION_TARGETS:
        print(f"    {t['f_lo']:.0f} + {t['f_hi']:.0f} MHz  "
              f"(ratio={t['ratio']:.4f}, dev={t['dev']:.4f})  — {t['note']}")

    # ── Why this is hard ─────────────────────────────────────────────────
    print("\n[3] Why UWL FRBs haven't produced P-12 hits yet")
    print("  (a) Most FRBs are narrowband: emission confined to <500 MHz BW,")
    print("      so the two required peaks are within the same sub-band.")
    print("  (b) Drift: repeaters drift downward in frequency; even if two")
    print("      sub-bursts exist, they are temporally separated (not the")
    print("      same burst simultaneously at two frequencies).")
    print("  (c) Publication bias: papers report peak burst frequency, not")
    print("      the full sub-band spectrum. A faint second peak at 2.3x the")
    print("      main peak frequency could exist but be unreported.")
    print("  (d) The two published 2024-2025 'simultaneous' events checked:")
    print("      FRB 20190520B FAST+UWL: single narrowband burst at ~1632 MHz")
    print("      FRB 20240114A: 0 bursts at 8.6 GHz, so no ratio possible")

    print("\n[4] Best available path")
    print("  Request from CRAFT/Parkes teams: full Stokes spectral data for")
    print("  any burst where the dynamic spectrum shows emission at two widely")
    print("  separated sub-bands. The UWL archival data exists — the question")
    print("  is whether any burst has been published with dual-peak sub-band")
    print("  analysis at separations of ~2.3x.")
    print()
    print("  Specific ask: FRB 20190520B, 20201124A, 20220912A dynamic spectra")
    print("  at full UWL resolution — look for any burst where flux is detected")
    print("  in both a low sub-band (e.g. 800-1200 MHz) AND a high sub-band")
    print(f"  (e.g. 1840-2760 MHz, the ln(10) factor range).")

    output = {
        "uwl_null_rate": round(null, 4),
        "n_events_checked": len(UWL_CATALOG),
        "n_confirmed_subband_hits": len(confirmed_hits),
        "confirmed_hits": confirmed_hits,
        "catalog": all_results,
        "ideal_targets": IDEAL_DETECTION_TARGETS,
        "verdict": (
            "No confirmed simultaneous dual-sub-band P-12 hit in published "
            "Parkes UWL FRB data as of 2026-03. Most bursts are narrowband. "
            "Archival analysis of full dynamic spectra is the recommended path."
        ),
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved -> {out_path}")
    return output


if __name__ == "__main__":
    run()
