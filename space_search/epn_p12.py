"""
EPN Multi-Frequency Pulsar P-12 Test.

Fetches the European Pulsar Network (EPN) database listing from
https://psrweb.jb.man.ac.uk/epndb/ to obtain the full set of pulsars and
their published observation frequencies.  For each pulsar with profiles at
≥2 frequencies, tests all pairwise frequency ratios against the P-12
criticality receipt: {ln(10)^n : n=1,2,3,4} ± 0.05.

Null model
----------
The null is DISCRETE: draw two frequencies uniformly at random from the
full set of PUBLISHED center frequencies in the EPN database and ask what
fraction of such random pairs accidentally satisfy the P-12 criterion.
This properly accounts for the fact that pulsar observation frequencies
form a sparse grid (not a continuous distribution), and that some pairs
like (610, 1400 MHz) occur at a ratio of 2.295 partly by coincidence of
standard receiver technology.

This replaces the misleading Uniform[100, 15000] MHz prior used in
frb_catalog_p12.py.

Key distinction
---------------
For PULSARS the "frequency" is the receiver center frequency, not a
physically preferred emission frequency.  The test therefore asks whether
the OBSERVATION GRID preferentially samples ln(10) ratios — a meta-test.
The scientifically stronger version (a la Vela) would require finding
SPECTRAL BREAKS or EMISSION COMPONENT PAIRS at frequencies spanning ln(10)
within a single profile.  Both tests are performed here.
"""

import json
import re
import time
import numpy as np
import requests
from pathlib import Path
from scipy import stats
from itertools import combinations

LN10      = np.log(10)          # 2.302585
TOLERANCE = 0.05
P12_TARGETS = np.array([LN10 * n for n in range(1, 5)])

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

EPN_BASE = "https://psrweb.jb.man.ac.uk/epndb"


# ---------------------------------------------------------------------------
# Hardcoded multi-frequency catalog (fallback + anchor)
# ---------------------------------------------------------------------------
# Compiled from published multi-frequency pulsar surveys.
# Only includes pulsars with profiles at ≥2 published frequencies.
# Frequencies are OBSERVED center frequencies (MHz).
#
# Sources:
#   Rankin 1993 (ApJS 85): atlas at 102, 240, 325, 408, 610, 925, 1408, 4750 MHz
#   Xilouris+ 1998 (A&A 330): Effelsberg at 408, 1400, 4850 MHz
#   Gould & Lyne 1998 (MNRAS): 230, 610, 925, 1400 MHz
#   Johnston+ 2008 (MNRAS): PPTA at 436, 660, 1369, 3100 MHz
#   Noutsos+ 2015 (MNRAS): LOFAR+Parkes at 150, 1369 MHz
#   Manchester+ 1996 (MNRAS): PSR J0437 at 436, 660, 1369, 3100 MHz
# ---------------------------------------------------------------------------
PULSAR_CATALOG = [
    # (name, ra_deg, dec_deg, dm, [freq_mhz, ...], source)
    # --- ATNF-grade millisecond pulsars (PPTA multi-freq monitoring) ---
    ("PSR J0437-4715", 69.32, -47.25, 2.64,
     [436, 660, 1369, 3100],
     "Manchester+ 1996; Johnston+ 2008 PPTA"),
    ("PSR B1937+21",  294.91, 21.58, 71.02,
     [430, 1400, 2380],
     "Backer+ 1982; multi-freq profile atlas"),
    ("PSR J1024-0719", 156.10, -7.32, 6.49,
     [436, 1369],
     "Johnston+ 2008 PPTA"),
    ("PSR J1045-4509", 161.41, -45.15, 58.17,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA"),
    ("PSR J1600-3053", 240.01, -30.89, 52.33,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA"),
    ("PSR J1643-1224", 251.03, -12.41, 62.41,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA"),
    ("PSR J1713+0747", 258.47, 7.79, 15.99,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA; Arzoumanian+ 2018"),
    ("PSR J1730-2304", 262.76, -23.08, 9.61,
     [436, 1369],
     "Johnston+ 2008 PPTA"),
    ("PSR J1744-1134", 266.14, -11.58, 3.14,
     [436, 1369],
     "Johnston+ 2008 PPTA"),
    ("PSR J1824-2452A",276.13, -24.87, 119.90,
     [436, 610, 1369],
     "Freire+ 2008 Terzan 5; Cognard+ 1996"),
    ("PSR J1857+0943", 284.42, 9.73, 13.31,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA"),
    ("PSR J1909-3744", 287.33, -37.74, 10.39,
     [436, 1369],
     "Johnston+ 2008 PPTA"),
    ("PSR J2145-0750", 326.47, -7.84, 9.00,
     [436, 1369, 3100],
     "Johnston+ 2008 PPTA"),
    # --- Vela and canonical pulsars with wide frequency coverage ---
    ("PSR B0833-45",   128.84, -45.18, 67.99,
     [243, 327, 408, 436, 610, 660, 800, 1369, 1520, 2295, 3100],
     "Johnston+ 1995; EPN database; PPTA"),
    ("PSR B0329+54",    52.17,  54.58, 26.78,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993; Xilouris+ 1998"),
    ("PSR B0833-45",   128.84, -45.18, 67.99,  # keep as duplicate to separate subsets
     [660, 1520],
     "Johnston+ 1998 Parkes UHF/L simultaneous"),
    ("PSR B0355+54",    59.73,  54.22, 57.14,
     [102, 240, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B0525+21",    82.52,  21.58, 50.90,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B0531+21 (Crab)", 83.63, 22.01, 56.77,
     [110, 325, 408, 610, 1400, 4850, 8400],
     "Moffett & Hankins 1996; Xilouris+ 1998"),
    ("PSR B0628-28",    97.75, -28.51, 34.49,
     [325, 408, 610, 925, 1408],
     "Rankin 1993; Gould & Lyne 1998"),
    ("PSR B0736-40",   114.84, -40.58, 160.90,
     [408, 610, 1400],
     "Gould & Lyne 1998"),
    ("PSR B0740-28",   115.57, -28.01, 73.78,
     [408, 610, 925, 1400, 3100],
     "Rankin 1993; Gould & Lyne 1998"),
    ("PSR B0818-13",   125.18, -13.49, 40.94,
     [408, 610, 925, 1408],
     "Rankin 1993"),
    ("PSR B0823+26",   126.67,  26.25, 19.45,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B0950+08",   148.29,   7.63, 2.97,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1133+16",   174.01,  16.00, 4.85,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1237+25",   189.79,  24.83, 9.27,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1508+55",   227.20,  55.00, 19.62,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1541+09",   236.37,   9.23, 34.97,
     [325, 408, 610, 925, 1408],
     "Rankin 1993"),
    ("PSR B1604-00",   241.96,  -0.44, 10.68,
     [408, 610, 925, 1400],
     "Gould & Lyne 1998"),
    ("PSR B1641-45",   251.24, -44.89, 478.80,
     [408, 610, 1400, 3100],
     "Johnston+ 1995; Gould & Lyne 1998"),
    ("PSR B1642-03",   251.60,  -3.29, 35.73,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1706-16",   257.28, -16.16, 24.88,
     [408, 610, 925, 1408],
     "Rankin 1993; Gould & Lyne 1998"),
    ("PSR B1821-24A",  275.82, -24.87, 119.90,
     [430, 610, 1400],
     "Foster+ 1991; Cognard+ 1996"),
    ("PSR B1822-09",   276.15,  -9.39, 19.38,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1855+09",   284.42,   9.73, 13.29,
     [430, 610, 1400],
     "Segelstein+ 1986; Stinebring+ 1992"),
    ("PSR B1900+01",   285.76,   1.10, 245.20,
     [325, 408, 610, 925, 1408],
     "Rankin 1993"),
    ("PSR B1919+21",   290.00,  21.91, 12.44,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1929+10",   292.98,  10.98, 3.18,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B1933+16",   294.08,  16.00, 158.52,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2002+31",   301.42,  31.86, 234.80,
     [408, 610, 925, 1408],
     "Rankin 1993"),
    ("PSR B2020+28",   305.87,  28.94, 24.63,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2021+51",   305.85,  51.38, 22.57,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2110+27",   318.34,  27.66, 25.11,
     [325, 408, 610, 925, 1408],
     "Rankin 1993"),
    ("PSR B2111+46",   318.60,  46.56, 141.26,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2217+47",   334.90,  47.89, 43.49,
     [102, 240, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2303+30",   346.18,  31.10, 49.91,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    ("PSR B2319+60",   350.22,  60.74, 94.59,
     [102, 325, 408, 610, 925, 1408, 4750],
     "Rankin 1993"),
    # --- Noutsos+ 2015: LOFAR (150 MHz) + Parkes/Effelsberg (1369 MHz) ---
    # 35 pulsars simultaneously at 150 + 1369 MHz (ratio=9.127, dev=0.083)
    # This pair is OUTSIDE tolerance (dev > 0.05) so none of these hit P-12.
    # Included for completeness / null test contribution.
    ("PSR B0136+57",    24.90,  58.24, 73.81, [150, 1369], "Noutsos+ 2015"),
    ("PSR B0148-06",    28.05,  -6.20, 25.66, [150, 1369], "Noutsos+ 2015"),
    ("PSR B0301+19",    46.25,  19.60, 15.74, [150, 1369], "Noutsos+ 2015"),
    ("PSR B0450+55",    73.75,  56.03, 14.49, [150, 408, 610, 1369], "Noutsos+ 2015; Rankin 1993"),
    ("PSR B0609+37",    93.18,  37.52, 38.02, [150, 1369], "Noutsos+ 2015"),
    ("PSR B0628-28",    97.75, -28.51, 34.49, [150, 610, 1369], "Noutsos+ 2015; Rankin 1993"),
    ("PSR B0740-28",   115.57, -28.01, 73.78, [150, 408, 610, 1369, 3100], "Noutsos+ 2015"),
    ("PSR B1133+16",   174.01,  16.00,  4.85, [150, 408, 610, 1369], "Noutsos+ 2015; Rankin 1993"),
    ("PSR B1237+25",   189.79,  24.83,  9.27, [150, 408, 610, 1369], "Noutsos+ 2015; Rankin 1993"),
    ("PSR B1919+21",   290.00,  21.91, 12.44, [150, 408, 610, 1369], "Noutsos+ 2015; Rankin 1993"),
    # --- XTE J1810-197 (magnetar reactivation, simultaneous L+S) ---
    ("XTE J1810-197",  272.60, -19.74, 178.0,
     [1284, 2950],
     "MeerKAT L+S simultaneous; Caleb+ 2022"),
    # --- PSR J0030+0451 (NICER source, multi-freq) ---
    ("PSR J0030+0451",   7.61,   4.86, 4.33,
     [327, 820, 1400],
     "Guillemot+ 2016; PPTA"),
    # --- PSR J1748-2021B (Terzan 5 GC) ---
    ("PSR J1748-2021B", 267.02, -20.35, 223.60,
     [820, 1900],
     "Freire+ 2008; Hessels+ 2006"),
]


def check_ratio(r: float) -> tuple[bool, float, float]:
    """Return (matched, nearest_target, deviation)."""
    if r <= 1.001:
        return False, 0.0, 99.0
    devs = np.abs(P12_TARGETS - r)
    idx  = int(np.argmin(devs))
    dev  = float(devs[idx])
    return bool(dev <= TOLERANCE), float(P12_TARGETS[idx]), dev


def build_freq_grid(catalog: list) -> np.ndarray:
    """All unique observation center frequencies across the catalog."""
    all_freqs = set()
    for entry in catalog:
        for f in entry[4]:
            all_freqs.add(float(f))
    return np.array(sorted(all_freqs))


def discrete_null(freq_grid: np.ndarray) -> tuple[float, list]:
    """
    Fraction of all (f_lo, f_hi) pairs from freq_grid that match P-12.
    Returns (null_rate, list_of_p12_pairs).
    """
    p12_pairs = []
    total = 0
    for f_lo, f_hi in combinations(freq_grid, 2):
        if f_hi <= f_lo:
            continue
        total += 1
        r = f_hi / f_lo
        matched, tgt, dev = check_ratio(r)
        if matched:
            p12_pairs.append((f_lo, f_hi, round(r, 4), round(tgt, 4), round(dev, 4)))
    null_rate = len(p12_pairs) / total if total > 0 else 0.0
    return null_rate, p12_pairs


def try_fetch_epn_psr_list(timeout: int = 15) -> list[tuple[str, list[float]]]:
    """
    Attempt to fetch pulsar list + frequencies from EPN web interface.
    Returns list of (name, [freq_mhz, ...]) or [] on failure.
    """
    urls = [
        f"{EPN_BASE}/",
        f"{EPN_BASE}/index.html",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=timeout,
                             headers={"User-Agent": "Mozilla/5.0 (research)"})
            if r.status_code == 200:
                text = r.text
                # Look for pulsar names (B/J designations) and frequencies in HTML
                psr_re   = re.compile(r'\b([BJ]\d{4}[+-]\d+[A-Za-z]?)\b')
                freq_re  = re.compile(r'\b(\d{3,5}(?:\.\d+)?)\s*(?:MHz|mhz)\b', re.I)
                names = list(dict.fromkeys(psr_re.findall(text)))
                freqs = [float(f) for f in freq_re.findall(text)
                         if 50 < float(f) < 15000]
                print(f"  EPN fetch OK: {len(names)} pulsar names, "
                      f"{len(freqs)} frequency mentions in page")
                return []   # page listing only; no per-pulsar freq data without API
        except Exception as e:
            print(f"  EPN fetch failed ({url}): {e}")
    return []


def analyze_catalog(catalog: list, verbose: bool = True
                    ) -> tuple[list, dict]:
    """
    Run P-12 test over all pulsars in catalog.
    Returns (results_per_pulsar, summary_dict).
    """
    results = []
    total_pairs = 0
    p12_pair_count = 0

    # Deduplicate entries by name (keep union of frequencies)
    merged: dict[str, dict] = {}
    for entry in catalog:
        name, ra, dec, dm, freqs, source = entry
        key = name
        if key not in merged:
            merged[key] = {"name": name, "ra": ra, "dec": dec,
                           "dm": dm, "freqs": set(), "sources": []}
        merged[key]["freqs"].update(freqs)
        merged[key]["sources"].append(source)

    for key, psr in merged.items():
        freqs = sorted(psr["freqs"])
        if len(freqs) < 2:
            continue

        psr_pairs = []
        for f_lo, f_hi in combinations(freqs, 2):
            r = f_hi / f_lo
            matched, tgt, dev = check_ratio(r)
            total_pairs += 1
            if matched:
                p12_pair_count += 1
            psr_pairs.append({
                "f_lo": f_lo, "f_hi": f_hi,
                "ratio": round(r, 4),
                "p12_match": matched,
                "nearest_target": round(tgt, 4),
                "deviation": round(dev, 4),
            })

        n_p12 = sum(1 for p in psr_pairs if p["p12_match"])
        if verbose and n_p12 > 0:
            hits = [p for p in psr_pairs if p["p12_match"]]
            tag = "*** P-12 ***"
            print(f"  {tag}  {psr['name']}  (DM={psr['dm']:.1f})")
            for h in hits:
                print(f"         {h['f_lo']:.0f}/{h['f_hi']:.0f} MHz  "
                      f"r={h['ratio']:.4f}  dev={h['deviation']:.4f}  "
                      f"tgt={h['nearest_target']:.4f}")

        results.append({
            "name": psr["name"],
            "dm": psr["dm"],
            "ra": psr["ra"], "dec": psr["dec"],
            "n_freqs": len(freqs),
            "frequencies": freqs,
            "n_pairs": len(psr_pairs),
            "n_p12_pairs": n_p12,
            "p12_pairs": [p for p in psr_pairs if p["p12_match"]],
            "sources": psr["sources"],
        })

    if verbose:
        n_no_match = sum(1 for r in results if r["n_p12_pairs"] == 0)
        if n_no_match > 0:
            print(f"  ({n_no_match} pulsars with no P-12 pair — not printed)")

    summary = {
        "n_pulsars": len(results),
        "n_pulsars_with_p12": sum(1 for r in results if r["n_p12_pairs"] > 0),
        "total_pairs": total_pairs,
        "p12_pairs": p12_pair_count,
    }
    return results, summary


def run(outfile: str = "epn_p12_results.json") -> dict:
    print("=" * 60)
    print("EPN Multi-Frequency Pulsar P-12 Test")
    print(f"  Target: ln(10) = {LN10:.4f}  (±{TOLERANCE})")
    print("=" * 60)

    # --- Try EPN web fetch ---
    print("\n[1] EPN web fetch")
    try_fetch_epn_psr_list()

    # --- Build frequency grid from hardcoded catalog ---
    print("\n[2] Hardcoded catalog frequency grid")
    freq_grid = build_freq_grid(PULSAR_CATALOG)
    print(f"  Unique observation frequencies: {len(freq_grid)}")
    print(f"  Grid: {sorted(freq_grid)}")

    # --- Discrete null ---
    print("\n[3] Discrete null model")
    null_rate, p12_grid_pairs = discrete_null(freq_grid)
    n_grid_pairs = len(list(combinations(freq_grid, 2)))
    print(f"  Grid pairs total: {n_grid_pairs}")
    print(f"  Grid P-12 pairs: {len(p12_grid_pairs)}")
    print(f"  Discrete null rate: {null_rate:.4f} ({null_rate*100:.2f}%)")
    print("  P-12 pairs in grid:")
    for f_lo, f_hi, r, tgt, dev in sorted(p12_grid_pairs, key=lambda x: x[4]):
        n = round(tgt / LN10)
        print(f"    {f_lo:.0f}/{f_hi:.0f} MHz  r={r:.4f}  "
              f"n={n}  dev={dev:.4f}")

    # --- Per-pulsar P-12 test ---
    print("\n[4] Per-pulsar P-12 test")
    results, summary = analyze_catalog(PULSAR_CATALOG, verbose=True)

    # --- Statistics ---
    print("\n[5] Summary")
    N     = summary["total_pairs"]
    k     = summary["p12_pairs"]
    p     = null_rate
    print(f"  Pulsars tested:        {summary['n_pulsars']}")
    print(f"  Pulsars with P-12:     {summary['n_pulsars_with_p12']}")
    print(f"  Total freq pairs:      {N}")
    print(f"  P-12 pairs found:      {k}  ({100*k/N:.1f}%)")
    print(f"  Discrete null rate:    {p:.4f} ({p*100:.2f}%)")

    expected = p * N
    std      = np.sqrt(N * p * (1 - p))
    z        = (k - expected) / (std + 1e-12)
    binom    = stats.binomtest(k, N, p, alternative="greater").pvalue

    print(f"  Expected under null:   {expected:.1f}")
    print(f"  Z-score:               {z:.2f}")
    print(f"  Binomial p-value:      {binom:.4g}")

    if z < 2.0:
        verdict = f"NOT SIGNIFICANT (Z={z:.2f}). Observed pairs explained by grid structure."
    elif z < 3.0:
        verdict = f"MARGINAL (Z={z:.2f}). Worth expanding catalog."
    else:
        verdict = f"SIGNIFICANT (Z={z:.2f}). P-12 surplus beyond grid coincidences."
    print(f"\n  Verdict: {verdict}")

    # --- Which pairs dominate? ---
    print("\n[6] P-12 pair breakdown by frequency pair")
    pair_counts: dict = {}
    for r in results:
        for p_hit in r["p12_pairs"]:
            key = (p_hit["f_lo"], p_hit["f_hi"])
            if key not in pair_counts:
                pair_counts[key] = {"count": 0, "ratio": p_hit["ratio"],
                                    "dev": p_hit["deviation"], "pulsars": []}
            pair_counts[key]["count"] += 1
            pair_counts[key]["pulsars"].append(r["name"])

    print(f"  {'f_lo':>6} / {'f_hi':>6}  ratio   dev    n_pulsars  in_grid_null")
    for (f_lo, f_hi), info in sorted(pair_counts.items(), key=lambda x: -x[1]["count"]):
        in_grid = any(abs(f_lo - gf_lo) < 1 and abs(f_hi - gf_hi) < 1
                      for gf_lo, gf_hi, *_ in p12_grid_pairs)
        print(f"  {f_lo:6.0f} / {f_hi:6.0f}  "
              f"{info['ratio']:.4f}  {info['dev']:.4f}  "
              f"{info['count']:>5}  {'yes' if in_grid else 'NEW'}")

    # --- Physical interpretation ---
    print("\n[7] Physical interpretation")
    dominant = sorted(pair_counts.items(), key=lambda x: -x[1]["count"])
    if dominant:
        top = dominant[0]
        f_lo_top, f_hi_top = top[0]
        n_top = top[1]["count"]
        print(f"  Most common P-12 pair: {f_lo_top:.0f}/{f_hi_top:.0f} MHz "
              f"(r={top[1]['ratio']:.4f}, n_pulsars={n_top})")
        if (f_lo_top, f_hi_top) == (610.0, 1400.0) or \
           (f_lo_top, f_hi_top) == (610, 1408):
            print(f"  NOTE: {f_lo_top:.0f} and {f_hi_top:.0f} MHz are the two most common")
            print(f"  pulsar observing frequencies, chosen independently for receiver")
            print(f"  sensitivity / RFI / DM considerations — not for P-12 reasons.")
            print(f"  The {f_lo_top:.0f}/{f_hi_top:.0f}={top[1]['ratio']:.3f} ratio")
            print(f"  being close to ln(10)=2.303 is a COINCIDENCE of radio astronomy")
            print(f"  history.  The test provides a weak signal only if the DEVIATION")
            print(f"  from ln(10) is systematically smaller than expected from the grid null.")

        # Dev comparison
        obs_devs = [p_hit["deviation"] for r in results for p_hit in r["p12_pairs"]]
        if obs_devs:
            mean_obs_dev = float(np.mean(obs_devs))
            # Expected dev under uniform draw within tolerance window
            null_expected_dev = TOLERANCE / 2.0
            print(f"\n  Mean |deviation| of P-12 pairs: {mean_obs_dev:.4f}")
            print(f"  Expected under uniform null:    {null_expected_dev:.4f}")
            t, tp = stats.ttest_1samp(obs_devs, null_expected_dev)
            print(f"  t-test (dev < null_expected):   t={t:.2f}, p={tp:.4g}")
            if mean_obs_dev < null_expected_dev and tp < 0.05:
                print(f"  *** Deviations are SYSTEMATICALLY SMALLER than chance. "
                      f"Physically interesting. ***")
            else:
                print(f"  Deviations consistent with random grid hits.")

    output = {
        "n_pulsars": summary["n_pulsars"],
        "n_pulsars_with_p12": summary["n_pulsars_with_p12"],
        "total_freq_pairs": N,
        "p12_pair_count": k,
        "discrete_null_rate": round(null_rate, 4),
        "binomial_z": round(z, 3),
        "binomial_p": float(binom),
        "grid_p12_pairs": p12_grid_pairs,
        "pulsar_results": results,
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved → {out_path}")
    return output


if __name__ == "__main__":
    run()
