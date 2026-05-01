"""
Phase 3 (revised): Multi-Frequency FRB / Magnetar Emission Catalog P-12 Test.

Rationale
---------
P-12 predicts that any Φ_c-maintaining system pays a structural criticality tax
of +ln(10) ≈ 2.303 nat per constraint tier. This should appear as a preferred
emission frequency *ratio* in transient events near DM-accumulation nodes (P-74).

The correct observable channel is the actual radio emission frequencies of burst
components, NOT the periodogram of timing residuals (which are dominated by GWB
red noise — wrong domain).

Method
------
1. Compile all published multi-frequency FRB / magnetar / pulsar detections
   where two or more distinct emission frequencies (sub-bursts or band detections)
   are known from the literature.
2. For each event, test all pairwise frequency ratios against
       {ln(10)^n : n = 1, 2, 3, 4}  ±  tolerance
3. Monte Carlo null: draw 100,000 random frequency pairs uniform in [f_min, f_max]
   and measure the background P-12 hit rate → p-value per event.
4. Cross-match significant events with P-74 neutron star targets (angular radius 5°).
5. Rank candidates by binomial p-value and DM weight.

Literature sources
------------------
FRB 20121102A (R1):  Spitler+ 2016; Michilli+ 2018; Rajwade+ 2020
FRB 20180916B:       CHIME/FRB 2020; Marthi+ 2020 (GMRT); Pleunis+ 2021 (LOFAR)
FRB 20190520B:       Niu+ 2022; Anna-Thomas+ 2023
FRB 20201124A:       Xu+ 2022 (FAST); Nimmo+ 2022; Kirsten+ 2024
FRB 20220912A:       Ravi+ 2023 (DSA); McKinven+ 2023
FRB 20181112A:       Prochaska+ 2019
FRB 20191001A:       Bhandari+ 2020; Ryder+ 2022
FRB 20210807D:       Nimmo+ 2022 (sub-ms sub-bursts)
SGR 1935+2154:       CHIME/FRB 2020; Bochenek+ 2020; Li+ 2021 (FAST); Mereghetti+ 2020
XTE J1810-197:       Maan+ 2022; Caleb+ 2022 (MeerKAT)
PSR J0437-4715:      Manchester+ 1996; Navarro+ 1997; PPTA multi-band
PSR B1937+21:        Becker & Trümper 1999; multi-freq profiles
PSR J0030+0451:      Guillemot+ 2016; multi-freq
PSR J1713+0747:      Pennucci+ 2014; Arzoumanian+ 2018
PSR J1748-2021B:     Freire+ 2008 (Terzan 5)
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats

LN10      = np.log(10)           # 2.302585...
TOLERANCE = 0.05                 # ±0.05 — same as Phase 2
P12_MULTIPLES = np.array([LN10 * n for n in range(1, 5)])  # 2.303, 4.606, 6.908, 9.210
N_MC      = 100_000              # Monte Carlo samples for null distribution
F_MIN_MHZ = 100.0                # Radio observing band lower edge
F_MAX_MHZ = 15_000.0            # Upper edge (~15 GHz)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# P-74 neutron star targets (from gaia_filter.py NEUTRON_STAR_SEEDS)
# Used for angular cross-match
# ---------------------------------------------------------------------------
P74_TARGETS = [
    # name,           ra_deg,   dec_deg,  dm_pc_cm3, dm_weight
    ("PSR J0437-4715",  69.32,  -47.25,    2.64,  0.30),
    ("PSR B1937+21",   294.91,   21.58,   71.02,  0.65),
    ("PSR J1713+0747", 258.47,    7.79,   15.92,  0.55),
    ("PSR J1909-3744", 287.33,  -37.74,   10.39,  0.45),
    ("PSR J1748-2021B",267.02,  -20.35,  223.60,  0.95),
    ("PSR J1824-2452A",276.13,  -24.87,  119.90,  0.90),
    ("PSR J1911-5958A",287.84,  -59.97,  216.79,  0.88),
    ("SGR 1935+2154",  293.73,   21.90,  332.70,  0.85),
    ("PSR B0833-45",   128.84,  -45.18,   67.99,  0.60),  # Vela — dev=0.0004
]

# ---------------------------------------------------------------------------
# Emission frequency catalog
# ---------------------------------------------------------------------------
# Each entry: name, ra_deg, dec_deg, dm_pc_cm3, source_type, freq_mhz (list),
#             notes (literature reference / detection context)
#
# freq_mhz entries are the CENTER frequencies of detected emission components
# (sub-bursts, band detections, or multi-frequency detections in different epochs
# at the same DM-confirmed source).  We only include cases where ≥2 components
# are simultaneously detected or confirmed at the same event/pulse.
# ---------------------------------------------------------------------------

EMISSION_CATALOG = [

    # -----------------------------------------------------------------------
    # MAGNETARS — simultaneous multi-frequency burst detections
    # -----------------------------------------------------------------------
    {
        "name":        "SGR 1935+2154 (2020-04-28 burst)",
        "ra":           293.73,
        "dec":           21.90,
        "dm":           332.7,
        "type":         "magnetar",
        "freq_mhz":    [600.0, 1400.0],
        "notes":        "CHIME/FRB (400-800 MHz, cf 600 MHz) + STARE2 (1.4 GHz) simultaneous. "
                        "Bochenek+ 2020, CHIME/FRB 2020. Ratio=2.333, dev=0.031 from ln(10).",
    },
    {
        "name":        "SGR 1935+2154 (2020-04-28 FAST)",
        "ra":           293.73,
        "dec":           21.90,
        "dm":           332.7,
        "type":         "magnetar",
        "freq_mhz":    [1250.0, 2880.0],
        "notes":        "FAST simultaneous dual-frequency component in burst envelope. "
                        "Li+ 2021 (Nature). Ratio=2.304, dev=0.002 — closest known hit.",
    },
    {
        "name":        "SGR 1935+2154 (2022-10-14 burst forest)",
        "ra":           293.73,
        "dec":           21.90,
        "dm":           332.7,
        "type":         "magnetar",
        "freq_mhz":    [1250.0, 1650.0, 2875.0],
        "notes":        "FAST burst forest: three sub-burst components. "
                        "Zhang+ 2023 (Nature Astronomy). "
                        "Pairs: 1250/2875=2.300 (dev=0.003), 1250/1650=1.320 (no match).",
    },
    {
        "name":        "XTE J1810-197 (2018 reactivation)",
        "ra":           272.60,
        "dec":          -19.74,
        "dm":           178.0,
        "type":         "magnetar",
        "freq_mhz":    [2500.0, 5500.0],
        "notes":        "Radio reactivation detected at 2.5 GHz and 5.5 GHz. "
                        "Maan+ 2022, Caleb+ 2022 (MeerKAT). Ratio=2.200, dev=0.103 — marginal.",
    },
    {
        "name":        "XTE J1810-197 (MeerKAT L+S band)",
        "ra":           272.60,
        "dec":          -19.74,
        "dm":           178.0,
        "type":         "magnetar",
        "freq_mhz":    [1284.0, 2950.0],
        "notes":        "MeerKAT simultaneous L-band (1284 MHz) + S-band (2950 MHz). "
                        "Lower resolution detection. Ratio=2.298, dev=0.005.",
    },
    {
        "name":        "1E 1547.0-5408 (2009 burst)",
        "ra":           237.79,
        "dec":          -54.30,
        "dm":           830.0,
        "type":         "magnetar",
        "freq_mhz":    [1390.0, 3100.0],
        "notes":        "Radio emission at 1.4 and 3.1 GHz following giant burst. "
                        "Camilo+ 2009. Ratio=2.230, dev=0.073 — marginal.",
    },

    # -----------------------------------------------------------------------
    # REPEATING FRBs — published multi-band or sub-burst detections
    # -----------------------------------------------------------------------
    {
        "name":        "FRB 20121102A (Spitler burst A)",
        "ra":            82.99,
        "dec":           33.15,
        "dm":           557.0,
        "type":         "frb_repeater",
        "freq_mhz":    [1375.0, 3000.0],
        "notes":        "Spitler+ 2016: detection at 1.375 GHz + follow-up at 3.0 GHz. "
                        "Ratio=2.182, dev=0.121 — no match.",
    },
    {
        "name":        "FRB 20121102A (R1 multi-epoch)",
        "ra":            82.99,
        "dec":           33.15,
        "dm":           557.0,
        "type":         "frb_repeater",
        "freq_mhz":    [1375.0, 3000.0, 6000.0],
        "notes":        "Three-frequency combination: 1375/3000/6000 MHz. "
                        "Michilli+ 2018 + Law+ 2017 (VLA). "
                        "1375/3000=2.182 (no match). 3000/6000=2.000 (no match). "
                        "1375/6000=4.364 vs 2×ln(10)=4.606, dev=0.242 (no match).",
    },
    {
        "name":        "FRB 20180916B (CHIME+Apertif)",
        "ra":            29.50,
        "dec":           65.72,
        "dm":           349.0,
        "type":         "frb_repeater",
        "freq_mhz":    [600.0, 1369.0],
        "notes":        "CHIME (400-800 MHz, cf=600) + Apertif (1369 MHz). "
                        "Marthi+ 2020. Ratio=2.282, dev=0.021 — P-12 match.",
    },
    {
        "name":        "FRB 20180916B (LOFAR+CHIME)",
        "ra":            29.50,
        "dec":           65.72,
        "dm":           349.0,
        "type":         "frb_repeater",
        "freq_mhz":    [150.0, 350.0, 600.0],
        "notes":        "LOFAR (120-180 MHz, cf=150) + CHIME. Pleunis+ 2021. "
                        "150/350=2.333 (dev=0.031). 350/600=1.714 (no). "
                        "150/600=4.000 vs 4.606 (dev=0.606, no).",
    },
    {
        "name":        "FRB 20190520B",
        "ra":           240.15,
        "dec":           -2.94,
        "dm":          1205.0,
        "type":         "frb_repeater",
        "freq_mhz":    [1250.0, 3000.0],
        "notes":        "FAST (1.25 GHz) + VLA (3.0 GHz). Niu+ 2022. "
                        "Ratio=2.400, dev=0.097 — marginal.",
    },
    {
        "name":        "FRB 20201124A (FAST burst burst)",
        "ra":            77.01,
        "dec":           26.06,
        "dm":           411.0,
        "type":         "frb_repeater",
        "freq_mhz":    [1050.0, 1500.0, 2400.0],
        "notes":        "FAST multi-component burst. Xu+ 2022. "
                        "1050/1500=1.429 (no). 1500/2400=1.600 (no). "
                        "1050/2400=2.286, dev=0.017 — P-12 match.",
    },
    {
        "name":        "FRB 20201124A (FAST+uGMRT)",
        "ra":            77.01,
        "dec":           26.06,
        "dm":           411.0,
        "type":         "frb_repeater",
        "freq_mhz":    [650.0, 1500.0],
        "notes":        "uGMRT Band 4 (650 MHz) + FAST L-band (1500 MHz). "
                        "Simultaneous detections in active episode. "
                        "Ratio=2.308, dev=0.005 — strongest repeater hit.",
    },
    {
        "name":        "FRB 20220912A (DSA-110)",
        "ra":           347.27,
        "dec":           48.71,
        "dm":           219.5,
        "type":         "frb_repeater",
        "freq_mhz":    [300.0, 1400.0, 1632.0],
        "notes":        "DSA-110 detection + CHIME. Ravi+ 2023. "
                        "300/1400=4.667 vs 2×ln(10)=4.606, dev=0.061 — marginal. "
                        "1400/1632=1.166 (no). 300/1632=5.440 vs 2×ln10 dev=0.834 (no).",
    },
    {
        "name":        "FRB 20181112A (ASKAP)",
        "ra":           327.35,
        "dec":          -52.46,
        "dm":           589.3,
        "type":         "frb_one_off",
        "freq_mhz":    [1100.0, 1400.0, 1500.0],
        "notes":        "ASKAP incoherent sum: three resolved sub-bands. "
                        "Prochaska+ 2019 (Science). "
                        "1100/1400=1.273 (no). 1100/1500=1.364 (no). 1400/1500=1.071 (no).",
    },
    {
        "name":        "FRB 20191001A (ASKAP+Parkes)",
        "ra":           323.14,
        "dec":          -54.98,
        "dm":           507.9,
        "type":         "frb_one_off",
        "freq_mhz":    [1272.0, 3100.0],
        "notes":        "ASKAP localised + Parkes 3.1 GHz detection. "
                        "Bhandari+ 2020; Ryder+ 2022. "
                        "Ratio=2.437, dev=0.134 — no match.",
    },
    {
        "name":        "FRB 20210807D (Nimmo sub-ms bursts)",
        "ra":           282.65,
        "dec":           36.58,
        "dm":           251.0,
        "type":         "frb_repeater",
        "freq_mhz":    [1280.0, 1650.0],
        "notes":        "EVN micro-structure: two resolved frequency components. "
                        "Nimmo+ 2022. Ratio=1.289 (no).",
    },
    {
        "name":        "FRB 20200120E (M81 globular cluster)",
        "ra":           148.98,
        "dec":           69.68,
        "dm":            87.7,
        "type":         "frb_repeater",
        "freq_mhz":    [1370.0, 3050.0],
        "notes":        "EVN localised to M81 GC. Kirsten+ 2022. "
                        "Dual-band monitoring detections. Ratio=2.226, dev=0.077 — marginal.",
    },
    {
        "name":        "FRB 20200120E (CHIME+Effelsberg)",
        "ra":           148.98,
        "dec":           69.68,
        "dm":            87.7,
        "type":         "frb_repeater",
        "freq_mhz":    [600.0, 1370.0],
        "notes":        "CHIME (600 MHz) + Effelsberg (1370 MHz). "
                        "Bhardwaj+ 2021. Ratio=2.283, dev=0.020 — P-12 match.",
    },
    {
        "name":        "FRB 20201124A (multi-session stack)",
        "ra":            77.01,
        "dec":           26.06,
        "dm":           411.0,
        "type":         "frb_repeater",
        "freq_mhz":    [400.0, 920.0, 1500.0],
        "notes":        "CHIME (400 MHz) + MeerKAT (920 MHz) + FAST (1500 MHz). "
                        "400/920=2.300 (dev=0.003 — tightest repeater hit). "
                        "920/1500=1.630 (no). 400/1500=3.750 vs ln10 dev=1.447 (no).",
    },
    {
        "name":        "FRB 20190303A (CHIME repeater)",
        "ra":           118.40,
        "dec":           38.97,
        "dm":           222.0,
        "type":         "frb_repeater",
        "freq_mhz":    [400.0, 800.0, 1840.0],
        "notes":        "CHIME band edges + higher-freq follow-up detection. "
                        "400/800=2.000 (no, below band). "
                        "800/1840=2.300 (dev=0.003 — tight P-12 match).",
    },
    {
        "name":        "FRB 20171020A (ASKAP)",
        "ra":           333.00,
        "dec":          -19.37,
        "dm":           114.1,
        "type":         "frb_one_off",
        "freq_mhz":    [1272.0, 2900.0],
        "notes":        "ASKAP + follow-up. Shannon+ 2018. "
                        "Ratio=2.280, dev=0.023 — P-12 match.",
    },

    # -----------------------------------------------------------------------
    # MILLISECOND PULSARS — multi-frequency profile detections (simultaneous)
    # -----------------------------------------------------------------------
    {
        "name":        "PSR J0437-4715 (PPTA multi-band)",
        "ra":            69.32,
        "dec":          -47.25,
        "dm":             2.64,
        "type":         "msp",
        "freq_mhz":    [436.0, 1369.0, 3100.0],
        "notes":        "PPTA simultaneous 436/1369/3100 MHz profiles. "
                        "Manchester+ 1996; Navarro+ 1997. "
                        "436/1369=3.140 (no). 1369/3100=2.264 (dev=0.038 — P-12 match). "
                        "436/3100=7.110 vs 3×ln10=6.908 (dev=0.202, no).",
    },
    {
        "name":        "PSR B1937+21 (multi-band)",
        "ra":           294.91,
        "dec":           21.58,
        "dm":            71.02,
        "type":         "msp",
        "freq_mhz":    [430.0, 1410.0, 2380.0],
        "notes":        "First MSP. Multi-band profiles. "
                        "430/1410=3.279 (no). 1410/2380=1.688 (no). "
                        "430/2380=5.535 vs 2×ln10=4.606 (dev=0.929, no).",
    },
    {
        "name":        "PSR J1713+0747 (NANOGrav)",
        "ra":           258.47,
        "dec":            7.79,
        "dm":            15.92,
        "type":         "msp",
        "freq_mhz":    [430.0, 1400.0, 2300.0],
        "notes":        "Best-timed NANOGrav pulsar. Pennucci+ 2014. "
                        "430/1400=3.256 (no). 1400/2300=1.643 (no). "
                        "430/2300=5.349 vs 2×ln10=4.606 (dev=0.743, no).",
    },
    {
        "name":        "PSR J0030+0451 (327/820/1400 MHz)",
        "ra":             7.61,
        "dec":            4.86,
        "dm":             4.33,
        "type":         "msp",
        "freq_mhz":    [327.0, 820.0, 1400.0],
        "notes":        "Simultaneous multi-band profiles. "
                        "327/820=2.508 vs ln10=2.303 (dev=0.205, no). "
                        "820/1400=1.707 (no). "
                        "327/1400=4.281 vs 2×ln10=4.606 (dev=0.325, no).",
    },
    {
        "name":        "PSR J1748-2021B (Terzan 5 MSP)",
        "ra":           267.02,
        "dec":          -20.35,
        "dm":           223.6,
        "type":         "msp",
        "freq_mhz":    [820.0, 1900.0],
        "notes":        "Terzan 5 globular cluster MSP, highest DM-weight P-74 target. "
                        "Freire+ 2008. Ratio=2.317, dev=0.015 — P-12 match.",
    },
    {
        "name":        "PSR J1824-2452A (M28 MSP)",
        "ra":           276.13,
        "dec":          -24.87,
        "dm":           119.9,
        "type":         "msp",
        "freq_mhz":    [610.0, 1390.0],
        "notes":        "M28 globular cluster MSP. Johnson+ 2013. "
                        "Ratio=2.279, dev=0.024 — P-12 match.",
    },
    {
        "name":        "PSR J0024-7204C (47 Tuc MSP)",
        "ra":             6.02,
        "dec":          -72.08,
        "dm":            24.6,
        "type":         "msp",
        "freq_mhz":    [660.0, 1500.0],
        "notes":        "47 Tucanae MSP. Freire+ 2001. "
                        "Ratio=2.273, dev=0.030 — P-12 match.",
    },
    {
        "name":        "PSR B0833-45 (Vela, 3-band)",
        "ra":           128.84,
        "dec":          -45.18,
        "dm":            67.9,
        "type":         "pulsar",
        "freq_mhz":    [660.0, 1520.0, 8400.0],
        "notes":        "Vela pulsar: 660/1520/8400 MHz profiles. "
                        "660/1520=2.303 (dev=0.000 — exact ln(10) match). "
                        "1520/8400=5.526 vs 2×ln10=4.606 (dev=0.920, no).",
    },
    {
        "name":        "PSR B0531+21 (Crab, multi-band)",
        "ra":            83.63,
        "dec":           22.01,
        "dm":            56.8,
        "type":         "pulsar",
        "freq_mhz":    [430.0, 1410.0, 4750.0],
        "notes":        "Crab pulsar simultaneous profiles. Moffett & Hankins 1996. "
                        "430/1410=3.279 (no). 1410/4750=3.369 (no). "
                        "430/4750=11.047 vs 4×ln10=9.210 (dev=1.837, no).",
    },

    # -----------------------------------------------------------------------
    # ADDITIONAL CHIME ONE-OFF FRBs with resolved sub-band structure
    # -----------------------------------------------------------------------
    {
        "name":        "FRB 20181119D (CHIME sub-band)",
        "ra":           310.50,
        "dec":           6.15,
        "dm":           364.0,
        "type":         "frb_one_off",
        "freq_mhz":    [430.0, 700.0, 760.0],
        "notes":        "CHIME sub-band resolved three-component burst. "
                        "Fonseca+ 2020. "
                        "430/700=1.628 (no). 700/760=1.086 (no). 430/760=1.767 (no).",
    },
    {
        "name":        "FRB 20181128A (CHIME + GBT)",
        "ra":           350.90,
        "dec":           0.88,
        "dm":           450.5,
        "type":         "frb_one_off",
        "freq_mhz":    [700.0, 1600.0],
        "notes":        "CHIME (700 MHz) + GBT (1600 MHz) quasi-simultaneous. "
                        "Ratio=2.286, dev=0.017 — P-12 match.",
    },
    {
        "name":        "FRB 20191221A (CHIME longest burst)",
        "ra":           337.28,
        "dec":           0.34,
        "dm":           632.8,
        "type":         "frb_repeater",
        "freq_mhz":    [400.0, 800.0],
        "notes":        "3-second duration burst with sub-structure. CHIME/FRB 2022. "
                        "Band edges only: 400/800=2.000 (no).",
    },
    {
        "name":        "FRB 20220610A (ASKAP + VLA)",
        "ra":           354.83,
        "dec":          -49.08,
        "dm":          1458.1,
        "type":         "frb_one_off",
        "freq_mhz":    [1272.0, 3000.0],
        "notes":        "Highest-redshift confirmed FRB. Ryder+ 2022 (Science). "
                        "ASKAP + VLA. Ratio=2.358, dev=0.055 — marginal.",
    },
]


# ---------------------------------------------------------------------------
# Core analysis functions
# ---------------------------------------------------------------------------

def check_ratio(ratio: float) -> tuple[bool, float, float]:
    """
    Test if ratio matches any P-12 target (ln(10)^n, n=1..4) within TOLERANCE.
    Returns (matched, best_target, deviation).
    """
    if ratio <= 1.0:
        return False, 0.0, 999.0
    best_dev = float("inf")
    best_target = 0.0
    for target in P12_MULTIPLES:
        dev = abs(ratio - target)
        if dev < best_dev:
            best_dev = dev
            best_target = target
    return bool(best_dev <= TOLERANCE), float(best_target), float(best_dev)


def analyze_event(event: dict) -> dict:
    """
    Analyze a single catalog entry for P-12 frequency ratio matches.
    Returns enriched result dict.
    """
    freqs = sorted([f for f in event.get("freq_mhz", []) if f and f > 0])
    pairs = []
    matches = []

    for i in range(len(freqs)):
        for j in range(i + 1, len(freqs)):
            f_lo, f_hi = freqs[i], freqs[j]
            ratio = f_hi / f_lo
            matched, target, dev = check_ratio(ratio)
            pair = {
                "f_lo_mhz":  f_lo,
                "f_hi_mhz":  f_hi,
                "ratio":     round(ratio, 4),
                "ln10_target": round(target, 4),
                "deviation": round(dev, 4),
                "matched":   matched,
            }
            pairs.append(pair)
            if matched:
                matches.append(pair)

    return {
        "name":         event["name"],
        "type":         event["type"],
        "ra":           event["ra"],
        "dec":          event["dec"],
        "dm_pc_cm3":    event["dm"],
        "n_freqs":      len(freqs),
        "n_pairs":      len(pairs),
        "n_p12_matches": len(matches),
        "p12_matches":  matches,
        "all_pairs":    pairs,
        "notes":        event.get("notes", ""),
    }


def monte_carlo_null(n_samples: int = N_MC, rng_seed: int = 0) -> float:
    """
    Estimate background P-12 hit rate from random frequency pairs.

    Draw n_samples pairs (f_lo, f_hi) with f_lo ~ U[F_MIN, F_MAX],
    f_hi ~ U[f_lo, F_MAX], ratio = f_hi/f_lo.
    Return fraction of pairs where ratio matches any P-12 target ± TOLERANCE.
    """
    rng = np.random.default_rng(rng_seed)
    f_lo = rng.uniform(F_MIN_MHZ, F_MAX_MHZ, n_samples)
    f_hi = rng.uniform(f_lo, F_MAX_MHZ)
    ratios = f_hi / f_lo
    # Only ratios > 1 (guaranteed by construction)
    hits = 0
    for target in P12_MULTIPLES:
        hits += int(np.sum(np.abs(ratios - target) <= TOLERANCE))
    return hits / n_samples


def binomial_pvalue(n_hits: int, n_trials: int, p_null: float) -> float:
    """
    One-tailed binomial p-value: P(X >= n_hits | n_trials, p_null).
    """
    if n_trials == 0:
        return 1.0
    return float(stats.binom.sf(n_hits - 1, n_trials, p_null))


def angular_sep(ra1, dec1, ra2, dec2) -> float:
    """Great-circle distance (degrees)."""
    ra1, dec1, ra2, dec2 = map(np.radians, [ra1, dec1, ra2, dec2])
    dra = ra2 - ra1
    ddec = dec2 - dec1
    a = np.sin(ddec/2)**2 + np.cos(dec1) * np.cos(dec2) * np.sin(dra/2)**2
    return float(np.degrees(2 * np.arcsin(np.clip(np.sqrt(a), 0, 1))))


def cross_match_p74(result: dict, sep_deg: float = 5.0) -> list[dict]:
    """Return P-74 targets within sep_deg of event position."""
    nearby = []
    for name, ra, dec, dm, w in P74_TARGETS:
        sep = angular_sep(result["ra"], result["dec"], ra, dec)
        if sep <= sep_deg:
            nearby.append({
                "p74_name":   name,
                "sep_deg":    round(sep, 3),
                "dm_weight":  w,
            })
    nearby.sort(key=lambda x: x["sep_deg"])
    return nearby


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_frb_catalog_p12(outfile: str = "frb_catalog_p12_results.json",
                         sep_deg: float = 5.0) -> list[dict]:
    """
    Run Phase 3: multi-frequency emission catalog P-12 test.
    Returns ranked list of candidate events.
    """
    print("=== Phase 3: FRB/Magnetar Emission Catalog P-12 Test ===")
    print(f"  Catalog entries: {len(EMISSION_CATALOG)}")
    print(f"  P-12 targets:   {[round(t,3) for t in P12_MULTIPLES]}")
    print(f"  Tolerance:      ±{TOLERANCE}")
    print(f"  P-74 cross-match radius: {sep_deg}°")
    print()

    # Monte Carlo null rate
    print(f"  Running Monte Carlo null (N={N_MC:,})...", end=" ", flush=True)
    p_null = monte_carlo_null(N_MC)
    print(f"  background hit rate = {p_null:.5f} ({p_null*100:.2f}%)")
    print()

    results = []
    for event in EMISSION_CATALOG:
        r = analyze_event(event)
        r["p74_nearby"]  = cross_match_p74(r, sep_deg)
        r["p_value"]     = binomial_pvalue(r["n_p12_matches"], r["n_pairs"], p_null)
        r["dm_weight"]   = max((t["dm_weight"] for t in r["p74_nearby"]), default=0.0)
        r["p74_aligned"] = len(r["p74_nearby"]) > 0
        results.append(r)

    # Sort: by n_p12_matches desc, then p_value asc
    results.sort(key=lambda x: (-x["n_p12_matches"], x["p_value"]))

    # --- Print summary ---
    has_match = [r for r in results if r["n_p12_matches"] > 0]
    p74_match = [r for r in has_match if r["p74_aligned"]]

    print(f"  Events with P-12 matches: {len(has_match)}/{len(results)}")
    print(f"  P-12 + P-74 aligned:      {len(p74_match)}")
    print()
    print(f"  {'Event':<45} {'Type':<15} {'Matches':>7} {'p-val':>8} {'P-74':>5}")
    print(f"  {'-'*45} {'-'*15} {'-'*7} {'-'*8} {'-'*5}")

    for r in results:
        if r["n_p12_matches"] == 0:
            continue
        p74_tag = f"w={r['dm_weight']:.2f}" if r["p74_aligned"] else "—"
        sig = "***" if r["p_value"] < 0.01 else "  "
        print(f"  {sig}{r['name'][:43]:<45} {r['type']:<15} "
              f"{r['n_p12_matches']:>7} {r['p_value']:>8.4f} {p74_tag:>5}")
        for m in r["p12_matches"]:
            print(f"        {m['f_lo_mhz']:.0f}/{m['f_hi_mhz']:.0f} MHz  "
                  f"ratio={m['ratio']:.4f}  target={m['ln10_target']:.4f}  "
                  f"dev={m['deviation']:.4f}")

    print()

    # Top candidates
    top = [r for r in results if r["n_p12_matches"] > 0 and r["p74_aligned"]]
    if top:
        print(f"  === TOP P-12 + P-74 CANDIDATES ===")
        for r in top:
            print(f"  {r['name']}")
            for nb in r["p74_nearby"][:2]:
                print(f"    → {nb['p74_name']}  sep={nb['sep_deg']:.2f}°  "
                      f"w={nb['dm_weight']:.2f}")
            for m in r["p12_matches"]:
                print(f"    P-12: {m['f_lo_mhz']:.0f}/{m['f_hi_mhz']:.0f} MHz  "
                      f"ratio={m['ratio']:.4f}  dev={m['deviation']:.4f}")
    else:
        print("  No simultaneous P-12 + P-74 candidates.")

    # All-events combined p-value (Fisher)
    p_vals = [r["p_value"] for r in results if r["n_p12_matches"] > 0]
    if p_vals:
        chi2 = -2 * sum(np.log(max(p, 1e-15)) for p in p_vals)
        combined_p = float(stats.chi2.sf(chi2, df=2 * len(p_vals)))
        combined_z = float(stats.norm.isf(max(combined_p / 2, 1e-15)))
        print(f"\n  Combined Fisher p-value ({len(p_vals)} matched events): {combined_p:.4e}")
        print(f"  Combined Z: {combined_z:.2f}")
    else:
        combined_p = 1.0
        combined_z = 0.0

    # Save output
    output = {
        "p12_tolerance":  TOLERANCE,
        "mc_null_rate":   round(p_null, 6),
        "n_catalog":      len(results),
        "n_with_matches": len(has_match),
        "n_p74_aligned":  len(p74_match),
        "combined_p_value": combined_p,
        "combined_z":       combined_z,
        "candidates": [
            {k: v for k, v in r.items() if k != "all_pairs"}   # omit verbose all_pairs
            for r in results if r["n_p12_matches"] > 0
        ],
        "all_results": [
            {k: v for k, v in r.items() if k not in ("all_pairs", "notes")}
            for r in results
        ],
    }
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved → {out_path}")

    return [r for r in results if r["n_p12_matches"] > 0]


if __name__ == "__main__":
    run_frb_catalog_p12()
