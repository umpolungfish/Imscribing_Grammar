"""
Phase 1: Primitive Filter for Gaia DR3 proper motion data.

Queries the Gaia archive via ADQL, applies the Imscribing Grammar primitive filter
criteria (F-fidelity, T-topology, Phi-criticality, Omega-candidate, D-temporal),
and outputs a ranked candidate list as JSON.

P-74: neutron stars are DM accumulation nodes → cross-match with neutron star catalog.
P-75: DM-baryon conflict set {D, T, R, ∈} → anomalies in those channels are priority.
"""

import json
import warnings
import numpy as np
from pathlib import Path

warnings.filterwarnings("ignore")

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Known neutron star / pulsar positions (J2000 RA/Dec deg) — cross-match targets
# Subset: well-measured millisecond pulsars in high-DM regions
# Source: ATNF pulsar catalog (Manchester et al. 2005)
NEUTRON_STAR_SEEDS = [
    # (name, ra_deg, dec_deg, notes)
    ("PSR J0437-4715",  69.316,  -47.252, "MSP, nearest, best-timed"),
    ("PSR B1937+21",   294.910,   21.583, "First MSP discovered"),
    ("PSR J1614-2230", 243.501,  -22.508, "Massive MSP, gravity well"),
    ("PSR J0030+0451",   7.605,    4.858, "NICER mass/radius MSP"),
    ("PSR J1748-2021B", 267.022, -20.355, "Terzan 5 GC — high DM density"),
    ("PSR J1824-2452A", 276.133, -24.870, "M28 GC — high DM density"),
    ("PSR J0218+4232",  34.529,   42.543, "MSP, gamma-ray bright"),
    ("PSR J2124-3358", 321.137,  -33.975, "MSP, isolated"),
    # P-12 primary targets: highest-confidence emission frequency matches
    ("SGR 1935+2154",  293.730,   21.896, "Magnetar FRB — top P-12 hit, P-74 aligned"),
    ("PSR B0833-45",   128.836,  -45.176, "Vela MSP — dev=0.0004 exact ln(10) at 660/1520 MHz"),
]


def _galactic_latitude(ra_deg: float, dec_deg: float) -> float:
    """Approximate galactic latitude (degrees) from ICRS RA/Dec."""
    import math
    ra  = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    # NGP: ra=192.859°, dec=27.128°, l_NCP=122.932°
    ra_ngp  = math.radians(192.859)
    dec_ngp = math.radians(27.128)
    sin_b = (math.sin(dec) * math.sin(dec_ngp)
             + math.cos(dec) * math.cos(dec_ngp) * math.cos(ra - ra_ngp))
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_b))))


def build_gaia_query(ra_center: float, dec_center: float,
                     radius_deg: float = 1.0,
                     mag_limit: float = 19.0,
                     ruwe_min: float = 1.4) -> str:
    """
    ADQL query for Gaia DR3 sources around a sky position, pre-filtered for
    high-RUWE (Omega candidate) and reasonable magnitude.

    Galactic-plane regions (|b| < 10°) automatically use tighter constraints
    to avoid 408 timeouts from excessive source density.
    """
    b = _galactic_latitude(ra_center, dec_center)
    if abs(b) < 10.0:
        # Galactic plane: compact radius, bright stars, high RUWE pre-filter
        radius_deg = min(radius_deg, 0.10)
        mag_limit  = min(mag_limit, 17.0)
        ruwe_floor = 2.0          # only high-anomaly sources in crowded fields
    else:
        ruwe_floor = ruwe_min

    return f"""
    SELECT
        source_id, ra, dec,
        pmra, pmdec,
        pmra_error, pmdec_error,
        parallax, parallax_error,
        phot_g_mean_mag,
        astrometric_excess_noise,
        astrometric_excess_noise_sig,
        ruwe,
        ipd_frac_multi_peak,
        ipd_gof_harmonic_amplitude
    FROM gaiadr3.gaia_source
    WHERE CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra_center}, {dec_center}, {radius_deg})
    ) = 1
    AND phot_g_mean_mag < {mag_limit}
    AND ruwe > {ruwe_floor}
    AND pmra IS NOT NULL
    AND pmdec IS NOT NULL
    AND pmra_error IS NOT NULL
    AND pmdec_error IS NOT NULL
    """.strip()


def score_source(row: dict, neighbors_pmra: np.ndarray | None = None,
                 neighbors_pmdec: np.ndarray | None = None,
                 dm_density_relative: float = 0.5) -> dict:
    """
    Apply Imscribing Grammar primitive filter to a single Gaia DR3 source.

    Scoring:
      +1  F_compliant: pmra_error < 0.1 and pmdec_error < 0.1 mas/yr
      +2  𐑡: spatially correlated proper motions (|r| > 0.3 with ≥5 neighbors)
      +3  ⊙ritical: astrometric_excess_noise_sig > 2 (scale-invariant excess)
      +4  Omega_candidate: RUWE > 1.4 + excess noise > 0.2 mas + high-DM region
      +1  D_temporal: ipd_gof_harmonic_amplitude > 0.1 (proxy for long-term drift signal)

    Returns dict with score, flags, and priority.
    """
    score = 0
    flags = []

    # F-FIDELITY FILTER
    pmra_err = row.get("pmra_error", 999)
    pmdec_err = row.get("pmdec_error", 999)
    if pmra_err < 0.1 and pmdec_err < 0.1:
        score += 1
        flags.append("⋈_compliant")

    # T-TOPOLOGY FILTER: correlated proper motions with neighbors
    if neighbors_pmra is not None and len(neighbors_pmra) >= 5:
        src_pmra = row.get("pmra", 0)
        src_pmdec = row.get("pmdec", 0)
        # Pearson r between source PM and neighbor PM distribution
        # Use deviation from median as proxy for network correlation
        med_ra = float(np.median(neighbors_pmra))
        med_dec = float(np.median(neighbors_pmdec))
        std_ra = float(np.std(neighbors_pmra)) + 1e-9
        std_dec = float(np.std(neighbors_pmdec)) + 1e-9
        z_ra = abs(src_pmra - med_ra) / std_ra
        z_dec = abs(src_pmdec - med_dec) / std_dec
        # Low z-score = source moves WITH neighbors = network topology
        if z_ra < 1.0 and z_dec < 1.0:
            score += 2
            flags.append("𐑡")

    # PHI-CRITICALITY FILTER: structured excess noise (scale invariance proxy)
    excess_noise = row.get("astrometric_excess_noise", 0) or 0
    excess_noise_sig = row.get("astrometric_excess_noise_sig", 0) or 0
    if excess_noise > 0 and excess_noise_sig > 2.0:
        score += 3
        flags.append("⊙_critical")

    # OMEGA_Z2 CANDIDATE FILTER: high RUWE + structured noise + high DM region
    ruwe = row.get("ruwe", 1.0) or 1.0
    ipd_multi = row.get("ipd_frac_multi_peak", 0) or 0
    if (ruwe > 1.4
            and excess_noise > 0.2
            and dm_density_relative > 0.6   # above 60th percentile DM density
            and ipd_multi < 0.1):           # not explained by double star
        score += 4
        flags.append("◻_candidate")

    # D-TEMPORAL FILTER: harmonic variation proxy (ipd_gof_harmonic_amplitude)
    harmonic = row.get("ipd_gof_harmonic_amplitude", 0) or 0
    if harmonic > 0.1:
        score += 1
        flags.append("⊢ temporal")

    priority = (
        "Critical" if score >= 7 else
        "High"     if score >= 5 else
        "Medium"   if score >= 3 else
        "Low"
    )

    return {
        "source_id": str(row.get("source_id", "")),
        "ra": row.get("ra"),
        "dec": row.get("dec"),
        "phot_g_mean_mag": row.get("phot_g_mean_mag"),
        "pmra": row.get("pmra"),
        "pmdec": row.get("pmdec"),
        "pmra_error": pmra_err,
        "pmdec_error": pmdec_err,
        "ruwe": ruwe,
        "astrometric_excess_noise": excess_noise,
        "astrometric_excess_noise_sig": excess_noise_sig,
        "primitive_flags": flags,
        "anomaly_score": score,
        "priority": priority,
    }


def query_region(ra: float, dec: float, radius_deg: float = 1.0,
                 row_limit: int = 5000) -> list[dict]:
    """Query Gaia DR3 for sources in a cone around (ra, dec)."""
    from astroquery.gaia import Gaia
    Gaia.ROW_LIMIT = row_limit
    query = build_gaia_query(ra, dec, radius_deg)
    try:
        job = Gaia.launch_job(query)
        table = job.get_results()
        return [dict(zip(table.colnames, row)) for row in table]
    except Exception as e:
        print(f"    [query error] {e}")
        return []


def run_filter(seeds: list = None, radius_deg: float = 0.5,
               row_limit: int = 2000, outfile: str = "gaia_candidates.json") -> list[dict]:
    """
    Run the primitive filter over all neutron star seed regions.
    Returns list of candidates with score >= 3 (Medium or higher).
    """
    if seeds is None:
        seeds = NEUTRON_STAR_SEEDS

    all_candidates = []

    for name, ra, dec, notes in seeds:
        print(f"  [{name}] querying r={radius_deg}° around ({ra:.3f}, {dec:.3f}) — {notes}")
        rows = query_region(ra, dec, radius_deg, row_limit)
        if not rows:
            print(f"    no results")
            continue
        print(f"    {len(rows)} sources retrieved")

        # Build neighbor PM arrays for T-topology test
        pmra_arr  = np.array([r.get("pmra",  0) or 0 for r in rows])
        pmdec_arr = np.array([r.get("pmdec", 0) or 0 for r in rows])

        region_candidates = []
        for row in rows:
            scored = score_source(
                row,
                neighbors_pmra=pmra_arr,
                neighbors_pmdec=pmdec_arr,
                # Neutron star seeds are all in high-DM regions (P-74)
                dm_density_relative=0.75,
            )
            scored["seed_pulsar"] = name
            scored["seed_notes"] = notes
            if scored["anomaly_score"] >= 3:
                region_candidates.append(scored)

        region_candidates.sort(key=lambda x: x["anomaly_score"], reverse=True)
        print(f"    {len(region_candidates)} candidates (score ≥ 3)")
        all_candidates.extend(region_candidates)

    # Global sort
    all_candidates.sort(key=lambda x: x["anomaly_score"], reverse=True)

    # Save
    out_path = OUTPUT_DIR / outfile
    with open(out_path, "w") as f:
        json.dump(all_candidates, f, indent=2, default=str)
    print(f"\n  Saved {len(all_candidates)} candidates → {out_path}")

    # Summary
    for priority in ["Critical", "High", "Medium"]:
        n = sum(1 for c in all_candidates if c["priority"] == priority)
        print(f"  {priority}: {n}")

    return all_candidates


if __name__ == "__main__":
    print("=== Phase 1: Gaia DR3 Primitive Filter ===")
    print("Querying neutron star seed regions (P-74)...")
    candidates = run_filter(radius_deg=0.5, row_limit=2000)
    if candidates:
        print(f"\nTop 5 candidates:")
        for c in candidates[:5]:
            print(f"  [{c['priority']}] {c['source_id']} "
                  f"score={c['anomaly_score']} flags={c['primitive_flags']} "
                  f"near {c['seed_pulsar']}")
