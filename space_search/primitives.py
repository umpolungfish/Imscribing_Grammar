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
    "Ð": {"Ð_ß": 1, "Ð_C": 2, "Ð_;": 3, "Ð_ω": 4},
    "Þ": {"Þ_6": 1, "Þ_K": 2, "Þ_ò": 3, "Þ_¨": 4, "Þ_O": 5},
    "Ř": {"Ř_¯": 1, "Ř_ý": 2, "Ř_Ť": 3, "Ř_=": 4},
    "Φ": {"Φ_ɐ": 1, "Φ_υ": 2, "Φ_F": 3, "Φ_˙": 4, "Φ_}": 5},
    "ƒ": {"ƒ^ì": 1, "ƒ^ð": 2, "ƒ^ż": 3},
    "Ç": {"Ç^-": 1, "Ç^W": 2, "Ç^@": 3, "Ç^Ù": 4, "Ç^λ": 4.5},
    "Γ": {"Γ_β": 1, "Γ_γ": 2, "Γ_ʔ": 3},
    "ɢ": {"ɢ^∧": 1, "ɢ^˝": 2, "ɢ^ˌ": 3, "ɢ^Ş": 4},
    "⊙": {"⊙_ž": 1, "⊙_ÿ": 2, "⊙_Æ": 2.33, "⊙_3": 2.67, "⊙_Ţ": 3},
    "Ħ": {"Ħ_Ñ": 1, "Ħ_£": 2, "Ħ_A": 3, "Ħ_!": 4},
    "Σ": {"Σ_S": 1, "Σ_ő": 2, "Σ_ï": 3},
    "Ω": {"Ω_Å": 1, "Ω_2": 2, "Ω_z": 3, "Ω_5": 4},
}

# Primitive weights (canonical v0.4.26)
WEIGHTS = {
    "Ð": 1.0, "Þ": 1.0, "Ř": 1.0, "Φ": 1.0,
    "ƒ": 1.0, "Ç": 1.0, "Γ": 1.0, "ɢ": 1.0,
    "⊙": 1.0, "Ħ": 0.8, "Σ": 1.0, "Ω": 0.7,
}

PRIMITIVE_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

# Canonical imscription vectors (ordinal form)
imscriptions = {
    # S_human: current humanity (planetary, pre-visible)
    "human": {
        "Ð": "Ð_C", "Þ": "Þ_K", "Ř": "Ř_¯", "Φ": "Φ_F",
        "ƒ": "ƒ^ð", "Ç": "Ç^W", "Γ": "Γ_β", "ɢ": "ɢ^˝",
        "⊙": "⊙_ž", "Ħ": "Ħ_£", "Σ": "Σ_ő", "Ω": "Ω_Å",
    },
    # S_civ_DM: predicted DM-aligned interstellar civilization
    "civ_dm": {
        "Ð": "Ð_;", "Þ": "Þ_K", "Ř": "Ř_Ť", "Φ": "Φ_F",
        "ƒ": "ƒ^ż", "Ç": "Ç^Ù", "Γ": "Γ_ʔ", "ɢ": "ɢ^ˌ",
        "⊙": "⊙_ÿ", "Ħ": "Ħ_A", "Σ": "Σ_ï", "Ω": "Ω_2",
    },
    # S_noise: unmodeled pulsar noise (from MNRAS + PRD papers)
    "pulsar_noise": {
        "Ð": "Ð_;", "Þ": "Þ_K", "Ř": "Ř_¯", "Φ": "Φ_F",
        "ƒ": "ƒ^ð", "Ç": "Ç^W", "Γ": "Γ_β", "ɢ": "ɢ^˝",
        "⊙": "⊙_ž", "Ħ": "Ħ_£", "Σ": "Σ_ő", "Ω": "Ω_Å",
    },
    # S_interstellar_target: structural requirements for feasible interstellar propagation
    "interstellar_target": {
        "Ð": "Ð_;", "Þ": "Þ_K", "Ř": "Ř_Ť", "Φ": "Φ_F",
        "ƒ": "ƒ^ż", "Ç": "Ç^Ù", "Γ": "Γ_ʔ", "ɢ": "ɢ^ˌ",
        "⊙": "⊙_ÿ", "Ħ": "Ħ_A", "Σ": "Σ_ï", "Ω": "Ω_Å",
    },
}


def to_vector(imscription: dict) -> np.ndarray:
    """Convert a imscription dict to an ordinal vector in canonical primitive order."""
    vec = []
    for prim in PRIMITIVE_ORDER:
        val = imscription[prim]
        vec.append(ORDINALS[prim][val])
    return np.array(vec, dtype=float)


def weight_vector() -> np.ndarray:
    return np.array([WEIGHTS[p] for p in PRIMITIVE_ORDER])


def tuple_distance(s1: dict, s2: dict) -> float:
    """Weighted Euclidean distance between two imscription dicts."""
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

    Each imscription is converted to its ordinal vector; the sample covariance
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
    imscriptions = data if isinstance(data, list) else list(data.values())

    rows = []
    for s in imscriptions:
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
    s1, s2 : dict   Imscription dicts (same format as tuple_distance).
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
        d_diag = tuple_distance(imscriptions[a], imscriptions[b])
        d_maha = mahalanobis_distance(imscriptions[a], imscriptions[b], G)
        print(f"  d_diag({a}, {b}) = {d_diag:.3f}")
        print(f"  d_maha({a}, {b}) = {d_maha:.3f}")
        for row in breakdown(imscriptions[a], imscriptions[b])[:4]:
            if row["weighted_sq"] > 0:
                print(f"    {row['primitive']}: Δ={row['delta']:.0f}  contrib={row['weighted_sq']:.2f}")
        print()
