"""
Imscribing Grammar primitive ordinals and distance computation for the space search pipeline.
All weights and ordinals are canonical as of v0.4.27 (12-primitive tuple, Mahalanobis metric).

Distance functions
------------------
tuple_distance(s1, s2)
    Diagonal weighted Euclidean: d = sqrt(sum w_i * (xi_A - xi_B)^2).
    Fast, interpretable, backward-compatible.

mahalanobis_distance(s1, s2, G=None)
    Full Riemannian metric: d = sqrt((v1-v2)^T G (v1-v2)) where G = Sigma^{-1}
    estimated from the catalog.  Accounts for off-diagonal couplings; canonical
    for any analysis that requires geometric correctness.
    G defaults to METRIC_TENSOR (lazy-loaded from IG_catalog.json on first use).

build_metric_tensor(catalog_path)
    Compute and return the 12x12 inverse-covariance matrix G from a catalog file.
"""

import json
import os
import numpy as np

# Ordinal mappings for each primitive tier
ORDINALS = {
    "D": {"D_wedge": 1, "D_triangle": 2, "D_infty": 3, "D_odot": 4},
    "T": {"T_network": 1, "T_in": 2, "T_bowtie": 3, "T_boxtimes": 4, "T_odot": 5},
    "R": {"R_super": 1, "R_cat": 2, "R_dagger": 3, "R_lr": 4},
    "P": {"P_asym": 1, "P_psi": 2, "P_pm": 3, "P_sym": 4, "P_pm_sym": 5},
    "F": {"F_ell": 1, "F_eth": 2, "F_hbar": 3},
    "K": {"K_fast": 1, "K_mod": 2, "K_slow": 3, "K_trap": 4},
    "G": {"G_beth": 1, "G_gimel": 2, "G_aleph": 3},
    "Gamma": {"G_and": 1, "G_or": 2, "G_seq": 3, "G_broad": 4},
    "Phi": {"Phi_sub": 1, "Phi_c": 2, "Phi_c_complex": 2.33, "Phi_EP": 2.67, "Phi_super": 3},
    "H": {"H0": 1, "H1": 2, "H2": 3, "H_inf": 4},
    "S": {"one_one": 1, "n_n": 2, "n_m": 3},
    "Omega": {"Omega_0": 1, "Omega_Z2": 2, "Omega_Z": 3},
}

# Primitive weights (canonical v0.4.26)
WEIGHTS = {
    "D": 1.0, "T": 1.0, "R": 1.0, "P": 1.0,
    "F": 1.0, "K": 1.0, "G": 1.0, "Gamma": 1.0,
    "Phi": 1.0, "H": 0.8, "S": 1.0, "Omega": 0.7,
}

PRIMITIVE_ORDER = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

# Canonical synthon vectors (ordinal form)
SYNTHONS = {
    # S_human: current humanity (planetary, pre-visible)
    "human": {
        "D": "D_triangle", "T": "T_in", "R": "R_super", "P": "P_pm",
        "F": "F_eth", "K": "K_mod", "G": "G_beth", "Gamma": "G_or",
        "Phi": "Phi_sub", "H": "H1", "S": "n_n", "Omega": "Omega_0",
    },
    # S_civ_DM: predicted DM-aligned interstellar civilization
    "civ_dm": {
        "D": "D_infty", "T": "T_in", "R": "R_dagger", "P": "P_pm",
        "F": "F_hbar", "K": "K_trap", "G": "G_aleph", "Gamma": "G_seq",
        "Phi": "Phi_c", "H": "H2", "S": "n_m", "Omega": "Omega_Z2",
    },
    # S_noise: unmodeled pulsar noise (from MNRAS + PRD papers)
    "pulsar_noise": {
        "D": "D_infty", "T": "T_in", "R": "R_super", "P": "P_pm",
        "F": "F_eth", "K": "K_mod", "G": "G_beth", "Gamma": "G_or",
        "Phi": "Phi_sub", "H": "H1", "S": "n_n", "Omega": "Omega_0",
    },
    # S_interstellar_target: structural requirements for feasible interstellar propagation
    "interstellar_target": {
        "D": "D_infty", "T": "T_in", "R": "R_dagger", "P": "P_pm",
        "F": "F_hbar", "K": "K_trap", "G": "G_aleph", "Gamma": "G_seq",
        "Phi": "Phi_c", "H": "H2", "S": "n_m", "Omega": "Omega_0",
    },
}


def to_vector(synthon: dict) -> np.ndarray:
    """Convert a synthon dict to an ordinal vector in canonical primitive order."""
    vec = []
    for prim in PRIMITIVE_ORDER:
        val = synthon[prim]
        vec.append(ORDINALS[prim][val])
    return np.array(vec, dtype=float)


def weight_vector() -> np.ndarray:
    return np.array([WEIGHTS[p] for p in PRIMITIVE_ORDER])


def tuple_distance(s1: dict, s2: dict) -> float:
    """Weighted Euclidean distance between two synthon dicts."""
    v1 = to_vector(s1)
    v2 = to_vector(s2)
    w = weight_vector()
    return float(np.sqrt(np.sum(w * (v1 - v2) ** 2)))


def directed_distance(s_from: dict, s_to: dict) -> float:
    """
    Directed distance: sum of weighted upward steps (lattice cost from → to).
    Asymmetric when one primitive is higher in the other direction.
    Uses max(0, v_to - v_from) per primitive (cost only for upward moves).
    """
    v_from = to_vector(s_from)
    v_to = to_vector(s_to)
    w = weight_vector()
    upward = np.maximum(0.0, v_to - v_from)
    return float(np.sum(w * upward))


def breakdown(s1: dict, s2: dict) -> list[dict]:
    """Return per-primitive distance breakdown sorted by contribution (descending)."""
    v1 = to_vector(s1)
    v2 = to_vector(s2)
    w = weight_vector()
    rows = []
    for i, prim in enumerate(PRIMITIVE_ORDER):
        delta = abs(v1[i] - v2[i])
        contrib = w[i] * delta ** 2
        rows.append({
            "primitive": prim,
            "v1": int(v1[i]),
            "v2": int(v2[i]),
            "delta": delta,
            "weighted_sq": contrib,
        })
    rows.sort(key=lambda r: r["weighted_sq"], reverse=True)
    return rows


# ---------------------------------------------------------------------------
# Mahalanobis metric
# ---------------------------------------------------------------------------

# Module-level cache; populated lazily on first call to mahalanobis_distance()
# or explicitly by calling build_metric_tensor().
METRIC_TENSOR: np.ndarray | None = None

_CATALOG_SEARCH_PATHS = [
    # Relative to this file's directory
    os.path.join(os.path.dirname(__file__), "..", "IG_catalog.json"),
    # Relative to cwd (common when running from repo root)
    "IG_catalog.json",
]


def build_metric_tensor(catalog_path: str | None = None) -> np.ndarray:
    """Compute G = Sigma^{-1} from the catalog and cache it in METRIC_TENSOR.

    Each synthon is converted to its ordinal vector; the sample covariance
    matrix Sigma is estimated, then inverted.  The result is stored in the
    module-level METRIC_TENSOR and also returned.

    Parameters
    ----------
    catalog_path : str or None
        Path to IG_catalog.json.  If None, the module searches the default
        locations (_CATALOG_SEARCH_PATHS).

    Returns
    -------
    np.ndarray  shape (12, 12), the inverse-covariance metric tensor G.
    """
    global METRIC_TENSOR

    if catalog_path is None:
        for p in _CATALOG_SEARCH_PATHS:
            if os.path.exists(p):
                catalog_path = p
                break
        if catalog_path is None:
            raise FileNotFoundError(
                "IG_catalog.json not found; pass catalog_path explicitly."
            )

    with open(catalog_path) as f:
        data = json.load(f)
    synthons = data if isinstance(data, list) else list(data.values())

    rows = []
    for s in synthons:
        try:
            rows.append(to_vector(s))
        except (KeyError, TypeError):
            pass  # skip entries with missing primitives

    X = np.array(rows, dtype=float)  # shape (N, 12)
    cov = np.cov(X.T)                # shape (12, 12)

    try:
        G = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        G = np.linalg.pinv(cov)      # fallback for near-singular covariance

    METRIC_TENSOR = G
    return G


def metric_eigendecomposition(G: np.ndarray | None = None) -> dict:
    """Eigendecompose the metric tensor G = V Λ V^T.

    Returns a dict with:
      eigenvalues  : np.ndarray shape (12,) descending
      eigenvectors : np.ndarray shape (12,12) columns = modes
      effective_dim: int — number of modes capturing >= 90% of eigenweight
      named_modes  : list of dicts, one per top-6 mode
      condition_number: float = λ_max / λ_min
    """
    if G is None:
        global METRIC_TENSOR
        if METRIC_TENSOR is None:
            build_metric_tensor()
        G = METRIC_TENSOR

    vals, vecs = np.linalg.eigh(G)
    idx = np.argsort(vals)[::-1]
    vals = vals[idx]
    vecs = vecs[:, idx]

    total = float(np.sum(np.abs(vals)))
    cumulative = 0.0
    eff_dim = len(vals)
    for i, v in enumerate(vals):
        cumulative += abs(v)
        if cumulative / total >= 0.90:
            eff_dim = i + 1
            break

    named_modes = []
    for i in range(min(6, len(vals))):
        top4 = sorted(range(12), key=lambda j: abs(vecs[j, i]), reverse=True)[:4]
        named_modes.append({
            "index": i + 1,
            "eigenvalue": float(vals[i]),
            "cumulative_weight": float(np.sum(np.abs(vals[:i+1])) / total),
            "loadings": {PRIMITIVE_ORDER[j]: float(vecs[j, i]) for j in top4},
            "participation_ratio": float(
                (np.sum(np.abs(vecs[:, i]))**2) / np.sum(vecs[:, i]**2)
            ),
        })

    return {
        "eigenvalues": vals,
        "eigenvectors": vecs,
        "effective_dim": eff_dim,
        "condition_number": float(vals[0] / vals[-1]),
        "named_modes": named_modes,
    }


def mahalanobis_distance(s1: dict, s2: dict, G: np.ndarray | None = None) -> float:
    """Riemannian distance d = sqrt((v1-v2)^T G (v1-v2)).

    Parameters
    ----------
    s1, s2 : dict   Synthon dicts (same format as tuple_distance).
    G : np.ndarray or None
        The 12x12 metric tensor (inverse covariance).  If None, uses the
        module-level METRIC_TENSOR, loading it from the catalog if necessary.

    Returns
    -------
    float  Non-negative distance.
    """
    if G is None:
        global METRIC_TENSOR
        if METRIC_TENSOR is None:
            build_metric_tensor()
        G = METRIC_TENSOR

    delta = to_vector(s1) - to_vector(s2)
    sq = float(delta @ G @ delta)
    return float(np.sqrt(max(sq, 0.0)))


if __name__ == "__main__":
    print("=== Canonical distances: diagonal vs Mahalanobis ===")
    G = build_metric_tensor()

    eig = metric_eigendecomposition(G)
    print(f"\n=== Metric eigendecomposition (§26.6) ===")
    print(f"  Effective dimension: {eig['effective_dim']} of 12  (90% eigenweight)")
    print(f"  Condition number:    {eig['condition_number']:.2f}")
    for m in eig["named_modes"]:
        top = sorted(m["loadings"].items(), key=lambda x: abs(x[1]), reverse=True)
        top_str = "  ".join(f"{p}({v:+.3f})" for p, v in top)
        print(f"  e{m['index']} λ={m['eigenvalue']:.3f}  cum={m['cumulative_weight']*100:.1f}%  PR={m['participation_ratio']:.1f}  |  {top_str}")
    print()
    pairs = [
        ("human", "civ_dm"),
        ("pulsar_noise", "civ_dm"),
        ("human", "interstellar_target"),
    ]
    for a, b in pairs:
        d_diag = tuple_distance(SYNTHONS[a], SYNTHONS[b])
        d_maha = mahalanobis_distance(SYNTHONS[a], SYNTHONS[b], G)
        print(f"  d_diag({a}, {b}) = {d_diag:.3f}")
        print(f"  d_maha({a}, {b}) = {d_maha:.3f}")
        for row in breakdown(SYNTHONS[a], SYNTHONS[b])[:4]:
            if row["weighted_sq"] > 0:
                print(f"    {row['primitive']}: Δ={row['delta']:.0f}  contrib={row['weighted_sq']:.2f}")
        print()
