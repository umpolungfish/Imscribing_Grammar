"""
Imscribing Grammar Space Search Pipeline — Orchestrator

Runs all three phases in sequence:
  Phase 1: Gaia DR3 primitive filter (neutron star seed regions)
  Phase 2: P-12 criticality receipt test (short FRB/pulsar hardcoded catalog)
  Phase 3: Multi-frequency FRB/magnetar emission catalog P-12 test (full catalog)

Then cross-correlates results to identify candidates satisfying all three
detection criteria simultaneously (the "triple conjunction"):
  (1) Gaia Critical candidate (score ≥ 5) near a P-74 neutron star
  (2) Phase 2 P-12 spectral match within 5° of same P-74 target
  (3) Phase 3 emission catalog P-12 match aligned with same P-74 target

A triple conjunction reduces d(S_noise, S_civ_DM) from ~4.18 → estimated < 2.5.

Usage:
    python pipeline.py [--skip-gaia] [--verbose]

    --skip-gaia: Skip the Gaia query (requires network; use for offline testing)
    --verbose:   Print full per-candidate details
"""

import argparse
import json
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def angular_separation(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Great-circle distance in degrees (haversine)."""
    import numpy as np
    ra1, dec1, ra2, dec2 = map(np.radians, [ra1, dec1, ra2, dec2])
    dra = ra2 - ra1
    ddec = dec2 - dec1
    a = np.sin(ddec/2)**2 + np.cos(dec1) * np.cos(dec2) * np.sin(dra/2)**2
    return float(np.degrees(2 * np.arcsin(np.sqrt(a))))


def cross_correlate(gaia_candidates: list[dict],
                    p12_phase2: list[dict],
                    frb_phase3: list[dict],
                    sep_deg: float = 5.0) -> list[dict]:
    """
    Find P-74 targets simultaneously covered by all three detection criteria:
      (1) Gaia Critical candidate (score ≥ 5) within sep_deg
      (2) Phase 2 P-12 spectral match (FRB/pulsar short catalog) within sep_deg
      (3) Phase 3 emission catalog P-12 match (full FRB catalog) within sep_deg

    Works P-74-centric: iterate over P-74 targets, check each criterion radius.
    Returns list of conjunction events sorted by score.
    """
    from frb_catalog_p12 import P74_TARGETS

    conjunctions = []

    for p74_name, p74_ra, p74_dec, p74_dm, p74_w in P74_TARGETS:

        # Criterion 1: Gaia Critical nearby
        gaia_near = [
            g for g in gaia_candidates
            if g.get("anomaly_score", 0) >= 5
            and g.get("ra") is not None
            and angular_separation(p74_ra, p74_dec, g["ra"], g["dec"]) < sep_deg
        ]
        gaia_near.sort(key=lambda x: -x["anomaly_score"])

        # Criterion 2: Phase 2 P-12 match nearby
        p2_near = [
            m for m in p12_phase2
            if m.get("ra") is not None
            and angular_separation(p74_ra, p74_dec, m["ra"], m["dec"]) < sep_deg
        ]

        # Criterion 3: Phase 3 emission catalog P-12 match at this P-74 target
        # frb_phase3 entries already have p74_nearby cross-match; use it
        p3_near = [
            r for r in frb_phase3
            if any(nb["p74_name"] == p74_name for nb in r.get("p74_nearby", []))
        ]
        # Also accept any entry whose ra/dec falls within sep_deg
        p3_near_extra = [
            r for r in frb_phase3
            if r not in p3_near
            and angular_separation(p74_ra, p74_dec, r["ra"], r["dec"]) < sep_deg
        ]
        p3_near = p3_near + p3_near_extra

        # Score = number of criteria met
        score = (
            (1 if gaia_near else 0) +
            (1 if p2_near  else 0) +
            (1 if p3_near  else 0)
        )

        if score == 0:
            continue

        # Best Phase 3 match: tightest deviation
        best_p3_dev = None
        best_p3_match = None
        for r in p3_near:
            for m in r.get("p12_matches", []):
                if best_p3_dev is None or m["deviation"] < best_p3_dev:
                    best_p3_dev  = m["deviation"]
                    best_p3_match = {"event": r["name"],
                                     "ratio": m["ratio"],
                                     "dev":   m["deviation"],
                                     "f_lo":  m["f_lo_mhz"],
                                     "f_hi":  m["f_hi_mhz"]}

        conjunctions.append({
            "p74_target":        p74_name,
            "p74_ra":            p74_ra,
            "p74_dec":           p74_dec,
            "p74_dm_weight":     p74_w,
            "conjunction_score": score,
            "criteria_met":      {
                "gaia_critical": bool(gaia_near),
                "p12_phase2":    bool(p2_near),
                "p12_phase3":    bool(p3_near),
            },
            "gaia_top": gaia_near[0] if gaia_near else None,
            "p12_phase2_events": [m.get("event_name") for m in p2_near],
            "p12_phase3_best": best_p3_match,
            "estimated_d_effective": max(0.5, 4.18 - score * 0.56),
        })

    conjunctions.sort(key=lambda x: (-x["conjunction_score"], -x["p74_dm_weight"]))
    return conjunctions


def print_summary(gaia_candidates, p12_phase2, frb_phase3, conjunctions, verbose=False):
    print("\n" + "="*60)
    print("IG SPACE SEARCH — RESULTS SUMMARY")
    print("="*60)

    # Phase 1: Gaia
    n_crit = sum(1 for c in gaia_candidates if c.get("priority") == "Critical")
    n_high = sum(1 for c in gaia_candidates if c.get("priority") == "High")
    print(f"\nPhase 1 — Gaia DR3 Filter:")
    print(f"  Candidates: {len(gaia_candidates)} total  "
          f"(Critical: {n_crit}  High: {n_high})")

    # Phase 2: P-12 short catalog
    print(f"\nPhase 2 — P-12 Spectral Test (short catalog):")
    print(f"  Events with ln(10) matches: {len(p12_phase2)}")
    for m in p12_phase2[:5]:
        print(f"    {m['event_name']}: {m['n_matches']} match(es)  "
              f"dev_min={min(x['deviation'] for x in m['p12_matches']):.4f}")

    # Phase 3: FRB emission catalog
    n_p3_match = len(frb_phase3)
    n_p3_p74   = sum(1 for r in frb_phase3 if r["p74_aligned"])
    print(f"\nPhase 3 — FRB Emission Catalog P-12 Test:")
    print(f"  Events with P-12 matches: {n_p3_match}")
    print(f"  P-74 aligned (w/in 5°):   {n_p3_p74}")
    for r in frb_phase3[:8]:
        p74tag = f"[P74 w={r['dm_weight']:.2f}]" if r["p74_aligned"] else ""
        devs = [m["deviation"] for m in r["p12_matches"]]
        print(f"    {r['name'][:50]}  dev={min(devs):.4f}  {p74tag}")

    # Cross-correlation
    print(f"\nCross-correlation (P-74-centric conjunctions, sep < 5°):")
    if conjunctions:
        for c in conjunctions[:10]:
            crit = "+".join(k for k, v in c["criteria_met"].items() if v)
            print(f"  [score={c['conjunction_score']}] {c['p74_target']:<25} "
                  f"w={c['p74_dm_weight']:.2f}  d_eff≈{c['estimated_d_effective']:.2f}  "
                  f"[{crit}]")
            if c["p12_phase3_best"]:
                b = c["p12_phase3_best"]
                print(f"    Phase3 best: {b['event']}  "
                      f"{b['f_lo']:.0f}/{b['f_hi']:.0f} MHz  ratio={b['ratio']:.4f}  "
                      f"dev={b['dev']:.4f}")
    else:
        print("  No conjunctions found in current dataset.")

    # Interpretation
    print("\n--- Imscribing Grammar Interpretation ---")
    triple = [c for c in conjunctions if c["conjunction_score"] == 3]
    double = [c for c in conjunctions if c["conjunction_score"] == 2]
    single = [c for c in conjunctions if c["conjunction_score"] == 1]
    if triple:
        print("  TRIPLE CONJUNCTION DETECTED — d_eff < 2.5")
        print("  → meet(S_noise, S_civ_DM) structurally reachable")
        print("  → Recommended: Omega_Z2 lensing test + MeerKAT follow-up")
        for c in triple:
            print(f"    {c['p74_target']}  d_eff≈{c['estimated_d_effective']:.2f}")
    elif double:
        print("  DOUBLE CONJUNCTION — d_eff ≈ 2.6–3.6 (adjacent basins zone)")
        print("  → Amplification strategy viable; P-12 signal present in emission domain")
        print("  → Recommended: deeper Gaia cone + TRAPUM/MeerKAT GC timing")
        for c in double[:3]:
            print(f"    {c['p74_target']}  d_eff≈{c['estimated_d_effective']:.2f}")
    elif single:
        print("  SINGLE CRITERION — Phase 3 emission P-12 detections only")
        print("  → No Gaia convergence; expand photometric filter or add EHT/VLBI baseline")
    else:
        print("  NO MATCH in current dataset.")
        print("  → Recommended: expand to CHIME FRB Catalog 1 full dataset + DSA-110")

    print("="*60)


def run(skip_gaia: bool = False, verbose: bool = False):
    """Run the full three-phase pipeline."""
    import sys, os
    sys.path.insert(0, str(Path(__file__).parent))

    from p12_spectral_test import run_p12_test
    from frb_catalog_p12 import run_frb_catalog_p12
    from primitives import tuple_distance, SYNTHONS, breakdown

    # Print canonical distances
    print("=== Canonical Tuple Distances ===")
    pairs = [
        ("human", "civ_dm"),
        ("pulsar_noise", "civ_dm"),
        ("human", "interstellar_target"),
    ]
    for a, b in pairs:
        d = tuple_distance(SYNTHONS[a], SYNTHONS[b])
        print(f"  d({a}, {b}) = {d:.3f}")
    print()

    # Phase 1: Gaia
    gaia_cache = OUTPUT_DIR / "gaia_candidates.json"
    if skip_gaia:
        print("=== Phase 1: Gaia DR3 Filter [SKIPPED] ===")
        gaia_candidates = []
    elif gaia_cache.exists():
        print("=== Phase 1: Gaia DR3 Filter [loading from cache] ===")
        with open(gaia_cache) as f:
            gaia_candidates = json.load(f)
        n_crit = sum(1 for c in gaia_candidates if c["priority"] == "Critical")
        n_high = sum(1 for c in gaia_candidates if c["priority"] == "High")
        print(f"  Loaded {len(gaia_candidates)} candidates "
              f"(Critical: {n_crit}  High: {n_high})")
    else:
        from gaia_filter import run_filter
        gaia_candidates = run_filter(radius_deg=0.5, row_limit=2000)

    print()

    # Phase 2: P-12 short catalog
    p12_phase2 = run_p12_test()
    print()

    # Phase 3: FRB/magnetar emission catalog P-12 test
    frb_phase3 = run_frb_catalog_p12()
    print()

    # Cross-correlation
    print("=== Cross-Correlation ===")
    conjunctions = cross_correlate(gaia_candidates, p12_phase2, frb_phase3)

    # Summary
    print_summary(gaia_candidates, p12_phase2, frb_phase3, conjunctions, verbose)

    # Save full results
    out = {
        "n_gaia_candidates": len(gaia_candidates),
        "n_p12_phase2_matches": len(p12_phase2),
        "n_p12_phase3_matches": len(frb_phase3),
        "conjunctions": conjunctions,
    }
    out_path = OUTPUT_DIR / "pipeline_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFull results saved → {out_path}")
    return conjunctions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Imscribing Grammar Space Search Pipeline")
    parser.add_argument("--skip-gaia", action="store_true",
                        help="Skip Gaia DR3 query (network not required)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full candidate details")
    args = parser.parse_args()
    run(skip_gaia=args.skip_gaia, verbose=args.verbose)
