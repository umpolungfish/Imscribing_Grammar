#!/usr/bin/env python3
"""
space_search/encoding_invariance.py — Encoding invariance test suite

Tests the core invariance claim: independent encodings of the same physical
system must produce tuples that are metrically close (d_g < CLOSE), while
clearly distinct universality classes remain well-separated (d_g > FAR).

Five batteries
--------------
A  Alias detection      — catalog pairs with d_g = 0 (exact duplicate tuples)
B  Known proximity      — curated pairs that should be close; hard assertions
C  Known separation     — curated pairs that should be far;  hard assertions
D  Primitive sensitivity — per-primitive d_g for a one-step ordinal error;
                           reveals which primitives are high-risk miscodings
E  Metric consistency   — d_diagonal vs d_mahalanobis on 200 random pairs;
                           large ratio flags entries where off-diagonal
                           couplings dominate

Exit 0 = all hard assertions (B, C) passed.
Exit 1 = one or more hard failures.

Usage
-----
    python3 space_search/encoding_invariance.py
    python3 space_search/encoding_invariance.py --verbose
    python3 space_search/encoding_invariance.py --catalog path/to/IG_catalog.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# Allow running from repo root or as module
sys.path.insert(0, str(Path(__file__).parent.parent))

from space_search.primitives import (
    SYNTHONS, PRIMITIVE_ORDER,
    tuple_distance, mahalanobis_distance,
    build_metric_tensor, to_vector,
)

# ── Thresholds ────────────────────────────────────────────────────────────────
CLOSE = 2.5    # Battery B: d_g must be < CLOSE  (proximity assertion)
FAR   = 4.0    # Battery C: d_g must be > FAR    (separation assertion)

# ── Curated pair registry ─────────────────────────────────────────────────────
# Each entry: (name_a, source_a, name_b, source_b, note)
# source = "catalog" | "synthons"
#
# Battery B — pairs that should be close (same system, different encoding angle
# or structurally identical tuple confirmed in prior sessions)
PROXIMITY_PAIRS = [
    (
        "AtHv1_primed",      "catalog",
        "PsHv1_constitutive", "catalog",
        "Hv1 proton channels: AtHv1 primed vs PsHv1 constitutive — identical tuple, d=0 (P-55)",
    ),
    (
        "human",       "synthons",
        "pulsar_noise", "synthons",
        "Human vs unmodeled pulsar noise: differ only in D (D_triangle vs D_infty)",
    ),
]

# Battery C — pairs that should be far (distinct universality classes)
SEPARATION_PAIRS = [
    (
        "human",     "synthons",
        "civ_dm",    "synthons",
        "Pre-visible humanity vs DM-aligned interstellar civilisation",
    ),
    (
        "human",               "synthons",
        "interstellar_target", "synthons",
        "Human encoding vs structural requirements for interstellar propagation",
    ),
    (
        "pulsar_noise", "synthons",
        "civ_dm",       "synthons",
        "Pulsar noise vs DM-aligned civilisation",
    ),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_catalog(path: str) -> dict[str, dict]:
    with open(path) as f:
        data = json.load(f)
    entries = data if isinstance(data, list) else list(data.values())
    return {e["name"]: e for e in entries if "name" in e}


def safe_to_vector(entry: dict) -> np.ndarray | None:
    """to_vector with KeyError guard for extended/non-canonical ordinal values."""
    try:
        return to_vector(entry)
    except (KeyError, TypeError):
        return None


def safe_mahalanobis(a: dict, b: dict, G: np.ndarray) -> float | None:
    try:
        return mahalanobis_distance(a, b, G)
    except (KeyError, TypeError):
        return None


def safe_tuple_dist(a: dict, b: dict) -> float | None:
    try:
        return tuple_distance(a, b)
    except (KeyError, TypeError):
        return None


def resolve(name: str, source: str, catalog: dict) -> dict | None:
    if source == "synthons":
        return SYNTHONS.get(name)
    return catalog.get(name)


def bar(title: str):
    w = 64
    print(f"\n{'─' * w}")
    print(f"  {title}")
    print(f"{'─' * w}")


# ── Battery A ─────────────────────────────────────────────────────────────────

def battery_a(catalog: dict, G: np.ndarray) -> list[tuple[str, str]]:
    bar("Battery A — Alias detection  (d_g = 0 in full catalog)")
    entries = list(catalog.values())
    vecs = []
    names = []
    for e in entries:
        v = safe_to_vector(e)
        if v is not None:
            vecs.append(v)
            names.append(e["name"])

    n = len(vecs)
    V = np.stack(vecs)          # (n, 12)
    # Compute all pairwise Mahalanobis squared distances efficiently
    # d^2 = (v_i - v_j)^T G (v_i - v_j)
    # Expand: v^T G v - 2 v_i^T G v_j + v_j^T G v_j
    GV = V @ G                  # (n, 12)
    diag = np.einsum("ij,ij->i", V, GV)   # v_i^T G v_i  shape (n,)
    D2 = diag[:, None] + diag[None, :] - 2 * (V @ G @ V.T)
    D2 = np.maximum(D2, 0.0)

    zeros = []
    for i in range(n):
        for j in range(i + 1, n):
            if D2[i, j] < 1e-9:
                zeros.append((names[i], names[j]))
                print(f"  d_g = 0.000   {names[i]}  ≡  {names[j]}")

    if not zeros:
        print("  (no exact duplicate tuples found in catalog)")
    print(f"\n  Scanned {n} canonical entries.  Aliases found: {len(zeros)}")
    return zeros


# ── Battery B ─────────────────────────────────────────────────────────────────

def battery_b(catalog: dict, G: np.ndarray, verbose: bool) -> bool:
    bar(f"Battery B — Known proximity  (assert d_g < {CLOSE})")
    passed = True
    for name_a, src_a, name_b, src_b, note in PROXIMITY_PAIRS:
        sa = resolve(name_a, src_a, catalog)
        sb = resolve(name_b, src_b, catalog)
        if sa is None or sb is None:
            missing = name_a if sa is None else name_b
            print(f"  SKIP   {name_a} / {name_b}  —  '{missing}' not in {src_a if sa is None else src_b}")
            continue
        d = safe_mahalanobis(sa, sb, G)
        if d is None:
            print(f"  SKIP   {name_a} / {name_b}  —  vector conversion failed")
            continue
        ok = d < CLOSE
        tag = "PASS" if ok else "FAIL"
        print(f"  {tag}   d_g = {d:.4f}   ({name_a},  {name_b})")
        if verbose:
            print(f"         {note}")
        if not ok:
            passed = False
    return passed


# ── Battery C ─────────────────────────────────────────────────────────────────

def battery_c(catalog: dict, G: np.ndarray, verbose: bool) -> bool:
    bar(f"Battery C — Known separation  (assert d_g > {FAR})")
    passed = True
    for name_a, src_a, name_b, src_b, note in SEPARATION_PAIRS:
        sa = resolve(name_a, src_a, catalog)
        sb = resolve(name_b, src_b, catalog)
        if sa is None or sb is None:
            missing = name_a if sa is None else name_b
            print(f"  SKIP   {name_a} / {name_b}  —  '{missing}' not in {src_a if sa is None else src_b}")
            continue
        d = safe_mahalanobis(sa, sb, G)
        if d is None:
            print(f"  SKIP   {name_a} / {name_b}  —  vector conversion failed")
            continue
        ok = d > FAR
        tag = "PASS" if ok else "FAIL"
        print(f"  {tag}   d_g = {d:.4f}   ({name_a},  {name_b})")
        if verbose:
            print(f"         {note}")
        if not ok:
            passed = False
    return passed


# ── Battery D ─────────────────────────────────────────────────────────────────

def battery_d(G: np.ndarray):
    bar("Battery D — Primitive sensitivity  (d_g per single-step ordinal error)")
    print(f"  A one-step miscoding of primitive p produces d_g = sqrt(G[p,p]).\n")
    print(f"  {'Primitive':<10}  {'G[p,p]':>10}  {'d_g/step':>10}  {'vs CLOSE':>10}  {'risk':<6}")
    print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*6}")

    rows = []
    for i, p in enumerate(PRIMITIVE_ORDER):
        gpp = float(G[i, i])
        d_per_step = float(np.sqrt(max(gpp, 0.0)))
        frac = d_per_step / CLOSE
        risk = "HIGH" if frac > 1.0 else ("MED" if frac > 0.5 else "low")
        rows.append((p, gpp, d_per_step, frac, risk))

    rows.sort(key=lambda r: r[2], reverse=True)
    for p, gpp, dps, frac, risk in rows:
        print(f"  {p:<10}  {gpp:>10.4f}  {dps:>10.4f}  {frac:>9.1%}  {risk:<6}")

    high = [r[0] for r in rows if r[4] == "HIGH"]
    med  = [r[0] for r in rows if r[4] == "MED"]
    print()
    if high:
        print(f"  HIGH-risk (1-step error > CLOSE):  {', '.join(high)}")
    if med:
        print(f"  MED-risk  (1-step error > CLOSE/2): {', '.join(med)}")
    if not high and not med:
        print("  No primitive exceeds 50% of CLOSE per step — low miscoding risk overall.")


# ── Battery E ─────────────────────────────────────────────────────────────────

def battery_e(catalog: dict, G: np.ndarray, verbose: bool):
    bar("Battery E — Metric consistency  (d_mahalanobis / d_diagonal, 200 random pairs)")
    entries = [e for e in catalog.values() if safe_to_vector(e) is not None]
    n = len(entries)
    rng = np.random.default_rng(42)
    sample_size = min(200, n * (n - 1) // 2)

    seen = set()
    pairs = []
    attempts = 0
    while len(pairs) < sample_size and attempts < sample_size * 20:
        attempts += 1
        i, j = int(rng.integers(0, n)), int(rng.integers(0, n))
        if i == j:
            continue
        key = (min(i, j), max(i, j))
        if key in seen:
            continue
        seen.add(key)
        pairs.append(key)

    ratios = []
    outliers = []
    for i, j in pairs:
        d_diag = safe_tuple_dist(entries[i], entries[j])
        d_maha = safe_mahalanobis(entries[i], entries[j], G)
        if d_diag is None or d_maha is None or d_diag < 1e-9:
            continue
        r = d_maha / d_diag
        ratios.append(r)
        if r > 2.0 or r < 0.5:
            outliers.append((entries[i]["name"], entries[j]["name"], d_diag, d_maha, r))

    ratios = np.array(ratios)
    print(f"  Sampled pairs: {len(ratios)}")
    print(f"  d_maha / d_diagonal:")
    print(f"    mean   = {ratios.mean():.4f}")
    print(f"    median = {np.median(ratios):.4f}")
    print(f"    std    = {ratios.std():.4f}")
    print(f"    range  = [{ratios.min():.4f}, {ratios.max():.4f}]")
    print(f"  Pairs with ratio > 2.0 or < 0.5: {len(outliers)}")

    if verbose and outliers:
        outliers.sort(key=lambda r: abs(np.log(r[4])), reverse=True)
        print(f"\n  Top outliers (off-diagonal couplings dominate):")
        for a, b, dd, dm, r in outliers[:8]:
            print(f"    ratio={r:.3f}  d_diag={dd:.3f}  d_maha={dm:.3f}  ({a}, {b})")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Imscribing Grammar encoding invariance test suite (§26 metric)"
    )
    parser.add_argument(
        "--catalog", default=None,
        help="Path to IG_catalog.json (default: auto-detect from repo root)"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    catalog_path = args.catalog or str(root / "IG_catalog.json")

    print(f"Imscribing Grammar — Encoding Invariance Suite")
    print(f"Catalog : {catalog_path}")
    catalog = load_catalog(catalog_path)
    print(f"Entries : {len(catalog)}")

    G = build_metric_tensor(catalog_path)
    cond = float(np.linalg.cond(G))
    print(f"Metric  : G = Sigma^{{-1}}  shape={G.shape}  cond={cond:.2f}")

    battery_a(catalog, G)
    b_ok = battery_b(catalog, G, args.verbose)
    c_ok = battery_c(catalog, G, args.verbose)
    battery_d(G)
    battery_e(catalog, G, args.verbose)

    bar("Summary")
    print(f"  Battery B (proximity):   {'PASS' if b_ok else 'FAIL'}")
    print(f"  Battery C (separation):  {'PASS' if c_ok else 'FAIL'}")
    all_ok = b_ok and c_ok
    print(f"\n  {'ALL HARD ASSERTIONS PASSED' if all_ok else 'HARD ASSERTION FAILURES DETECTED'}")
    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
