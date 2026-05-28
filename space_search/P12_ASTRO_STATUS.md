---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# P-12 Astronomical Probe — Status Report
**Date**: 2026-03-24
**Hypothesis**: ln(10) ≈ 2.303 is a preferred simultaneous emission frequency ratio in radio-transient sources, predicted by the Imscribing Grammar P-12 criticality receipt.

---

## What We Tested

P-12 predicts that any system maintaining Φ_c pays a structural cost of +ln(10) nats per constraint tier. In radio astronomy this should appear as a preferred ratio f_hi/f_lo ≈ ln(10) in **simultaneous** multi-frequency detections of the same physical burst or emission event.

Strict criterion applied throughout: *same burst, same physical event, same time window*. Same-source-different-epoch observations, chromatic activity windows, and different-epoch profiles are excluded.

---

## Methodology

### Band-aware Monte Carlo null
Each instrument pair gets its own null rate, computed by drawing f₁ ~ Uniform(band₁) and f₂ ~ Uniform(band₂) and measuring the fraction of pairs where |f_hi/f_lo − ln(10)| < 0.05. Global uniform nulls (used in the earlier `frb_catalog_p12.py`) are invalid — CHIME internal pairs have max ratio 2.0 and literally cannot reach ln(10), giving null = 0% by physics, not by signal.

### Independence
N independent tests = N physically independent simultaneous events. If all N pulses from a source use the same fixed band centers, N_independent = 1 regardless of pulse count.

### Fisher combination
p-values combined via Fisher's chi² test. Only simultaneous P-12 hits enter the combination.

---

## Results: 3 Confirmed Simultaneous Events

| Source | Frequencies | Ratio | Dev | Band null | p |
|--------|-------------|-------|-----|-----------|---|
| XTE J1810-197 (MeerKAT L+S, Caleb+ 2022) | 1284/2950 MHz | 2.2975 | 0.0051 | 5.3% | 0.053 |
| Vela PSR B0833-45 (PPTA, Johnston+ 2008) | 1369/3100 MHz | 2.2644 | 0.0382 | 14.5% | 0.145 |
| SGR 1935+2154 (CHIME+STARE2, 2020-04-28) | 600/1400 MHz | 2.3333 | 0.0307 | 6.6% | 0.066 |

**Fisher combined: χ²=15.18, df=6, p=0.019, Z=2.35 (marginal)**

---

## Key Corrections Made During This Work

### 1. Johnston+ 1998 citation error (major)
The initial catalog attributed a simultaneous 660+1520 MHz Vela observation to Johnston+ 1998 (MNRAS 297, 108), giving a dev=0.0004 "golden hit" — the closest P-12 measurement in the dataset.

**Finding**: MNRAS 297, 108 is a scintillation parameters paper. The actual Johnston simultaneous Vela paper is Johnston+ 2001 (ApJ 549, L101, astro-ph/0101146), which used **660 + 1413 MHz** — ratio 2.141, dev=0.162, **not a P-12 match**. The 1520 MHz Vela profile is from a different epoch; 660 and 1520 were never observed simultaneously.

**Impact**: Removed the strongest single data point. Fisher Z dropped from 2.53 → 2.35.

### 2. Band assignment error (XTE J1810-197 Vela 1369 MHz)
Initial code assigned 1369 MHz to `PPTA_10cm` (2900–3300 MHz), making the null for the 1369/3100 pair effectively 0% (band doesn't contain 1369 MHz). Fixed to `Parkes_L` (1200–1600 MHz), giving correct null = 14.5%.

**Impact**: Fisher Z dropped from 36.87 → 2.22 on the xte_vela dataset (the 36.87 was entirely spurious).

### 3. EPN survey design contamination
The initial `epn_p12.py` found Z=13.46 across 55 pulsars. The Rankin 1993 atlas uses fixed survey frequencies {408, 610, 925, 1408 MHz} — the pairs 408/925 (r=2.267) and 610/1408 (r=2.308) are near ln(10) by coincidence of those frequency choices, and all 28 pulsars in the atlas share the same two coincidences. Independent test count = 2, not 74. The EPN result is spurious.

### 4. frb_catalog Z=7.48 spurious
`frb_catalog_p12.py` used a uniform null over [100, 15000] MHz for all sources (null=1.77%) regardless of actual instrument bands, and included non-simultaneous multi-epoch profiles. The 18/35 "hits" are primarily from same-frequency-grid coincidences. Discarded.

### 5. FRB 20180916B excluded
CHIME+Apertif detections of FRB 20180916B are at different sub-phases of the 16.35-day chromatic activity cycle (Pastor-Marazuela+ 2021). Not the same burst.

---

## Vela Spectral Analysis

Full spectral fit across 20 published flux densities (76–8356 MHz):

- **Simple power law**: α = −1.756 ± 0.030, χ²/dof = 1.60 (adequate but not great)
- **Broken power law**: α_low = −1.63, α_high = −2.09, ν_break ≈ 1221 MHz
  F-test vs simple PL: F=44.6, **p=2.9×10⁻⁷** — break is real and significant

The spectral break at ~1221 MHz sits between the 660 and 1520 MHz frequencies, which is physically interesting but does not by itself imply P-12. Both 660 and 1520 lie within ~1σ of the power law — no emission peak or break is located *at* either frequency.

The Vela Parkes UWL gap analysis remains: `1520 × ln(10) = 3499.7 MHz`. A single UWL session simultaneously covering ~660, ~1520, and ~3500 MHz would give a chained ln(10) triple test (660→1520→3500) from one instrument in one observation.

---

## FRB / UWL Search Results

### 2024–2025 simultaneous events checked
- **FRB 20190520B (FAST+Parkes UWL, arXiv:2507.17696)**: Single narrowband burst at ~1632 MHz, spanning the gap between adjacent FAST and UWL bands. Not a two-frequency detection.
- **FRB 20240114A (Tianma, 2025)**: 155 bursts at 2.25 GHz, 0 at 8.60 GHz. Single-band; ratio 3.82, no match.

### UWL catalog scan (11 published events)
Zero confirmed simultaneous dual-sub-band P-12 hits. All published UWL FRBs show either single narrowband emission or adjacent-sub-band structure (ratios ≪ ln(10)). FRBs are intrinsically narrowband — typical emission bandwidth is 200–500 MHz, too narrow for a simultaneous 2.3× frequency separation.

---

## What Would Push to 3σ

| Path | Required | Z estimate |
|------|----------|------------|
| XTE J1810-197 per-pulse centroids | Caleb+ 2022 authors release per-pulse peak frequency within L and S bands; if emission centroids vary, N=44 independent tests | ~4σ if even half match |
| Vela Parkes UWL single session | New ~2h observation at {660, 1520, 3500} MHz simultaneously | adds 1–2 clean tests |
| FRB 20201124A confirmed FAST+uGMRT | Xu+ 2022 / CRAFTS team confirm same-burst simultaneous detection at 650+1500 MHz (dev=0.005) | Z → 2.8σ |
| SGR 1935+2154 next active period | CHIME+MeerKAT L+S simultaneous monitoring: 1284/2950 MHz pair, null=5.3% | adds clean event |

---

## Honest Summary

Z = 2.35 across 3 independently confirmed simultaneous events from 3 distinct sources (a magnetar, a pulsar, and a magnetar FRB). This is suggestive but below the 3σ threshold for a claim of evidence.

The main unresolved confound is **instrument band center coincidence**: the MeerKAT L/S ratio (1284/2950 = 2.298) is a fixed property of MeerKAT's receiver design, not necessarily of the emission physics. Unless per-pulse centroids vary and still track ln(10), the XTE J1810 result could reflect telescope design rather than a physical signal. The SGR 1935 CHIME peak frequency (~600 MHz) is approximate (center of a 400–800 MHz band), introducing similar ambiguity.

The cleanest test remains the Vela UWL observation, which would use one instrument in one session and could in principle measure actual spectral peak positions rather than fixed band centers.

---

## Updated Canonical Primitive Distances (v0.5.0, post Ç/Γ ordinal fix)

Two ordinal errors corrected in `primitives.py` (v0.4.27 → v0.5.0):

**Ç (Kinetics)** was fully inverted. Canonical order is K_lambda(𐑺)=1 (MBL, disorder-frozen) through K_frtailgamma(𐑘)=5 (diffusion-limited, no barrier). Old code had 𐑘=1, 𐑺=4.5.

**Γ (Granularity)** had 𐑲 (G_revapostrophe, fine/atomic) at ordinal 3 instead of 1. Canonical: 𐑲(fine)=1 < 𐑚(meso)=2 < 𐑔(coarse)=3, matching ℵ < ℶ < ℷ.

| Pair | d_tuple (old) | d_tuple (new) | d_maha (new) |
|------|:---:|:---:|:---:|
| human ↔ civ_dm | 4.301 | **3.937** | 3.414 |
| pulsar_noise ↔ civ_dm | ~4.15 | **3.808** | 3.847 |
| human ↔ interstellar_target | ~4.14 | **3.847** | 3.759 |
| pulsar_noise ↔ interstellar_target | — | **3.715** | 4.106 |

Breakdown for human→civ_dm (post-fix): dominant contributions are Ř (Δ=2, 4.000) and Ç (Δ=2, 4.000); all other primitives contribute Δ=1. The Γ contribution dropped from 4.000 (was Δ=2) to 1.000 (now Δ=1) due to the ordinal correction.

---

## Null Test — NANOGrav 15yr Residuals (Shuffle Method)

Tested whether P-12 (ln10 periodicity) appears in timing residuals above shuffle background.

**Result: 0/13 significant. All Z-scores negative.**

Every pulsar tested has *fewer* Lomb-Scargle peaks near ln(10) in real data than in shuffled controls. Combined Fisher: p=1.00, Z=0.00. P-12 is not detectable in NANOGrav timing residuals at any power above the noise floor.

This is consistent with the honest simultaneity result: P-12, if real, is an *emission* signature visible in simultaneous multi-frequency radio bursts, not a timing residual periodicity.

---

## Ω₂ Lensing Test (Simulated Shear Catalog)

Tested for parity-odd B-mode excess near P-74 neutron star positions.

**Real test**: 0/10 Ω₂ candidates (B-mode SNR < threshold at all targets).
**Validation** (injected signal=0.005): 2/10 detected (PSR B1937+21, Vela) — confirms the detection pipeline functions.

No Ω₂ lensing signal in existing simulated shear catalogs. Requires KiDS-1000 or Euclid DR1 real shear data for a meaningful test.

---

## Files

| File | Description |
|------|-------------|
| `xte_vela_p12.py` | XTE J1810-197 + Vela simultaneous P-12 test (corrected) |
| `honest_frb_p12.py` | Strict simultaneity FRB catalog (SGR 1935+2154 only new event) |
| `vela_spectral_p12.py` | Vela flux density spectral fit and P-12 residual analysis |
| `uwl_frb_p12.py` | Parkes UWL FRB sub-band scan |
| `epn_p12.py` | EPN pulsar catalog (Z=13.46 identified as spurious) |
| `output/*.json` | All numerical results |
