"""
Imscribing Grammar primitive ordinals and distance computation for the space search pipeline.
All weights and ordinals are canonical as of v0.5.0 (12-primitive tuple, Mahalanobis metric).

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

# Ordinal mappings for each primitive tier.
#
# Derived from imscrbgrmr.canonical_primitives, not restated. This file used to
# carry its own copy, and a second copy of a table is a second thing to move: the
# two would have to be renamed in the same commit forever, and the version that
# was missed would go on answering.
try:  # pragma: no cover - the package is the authority when it is importable
    from imscrbgrmr.canonical_primitives import (
        ORDINALS, WEIGHTS, PRIMITIVE_ORDER,
    )
    _DERIVED = True
except Exception:  # standalone use, no package on the path
    _DERIVED = False

_FALLBACK_ORDINALS = {
    "⊢": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "⊣": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "≻": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "≺": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "⋈": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "⊤": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "∈": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "∋": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "⊥": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "⊞": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "◻": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}

_FALLBACK_WEIGHTS = {
    "⊢": 1.0, "⊣": 1.0, "≻": 1.0, "≺": 1.0,
    "⋈": 1.0, "⊤": 1.0, "∈": 1.0, "∋": 1.0,
    "⊙": 1.0, "⊥": 0.8, "⊞": 1.0, "◻": 0.7,
}

_FALLBACK_ORDER = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

if not _DERIVED:
    ORDINALS = _FALLBACK_ORDINALS
    WEIGHTS = _FALLBACK_WEIGHTS
    PRIMITIVE_ORDER = _FALLBACK_ORDER


def resolve_ordinal_key(primitive: str, value: str) -> str:
    """The value IS the ordinal key. A value that is not one is an error.

    This used to fall back to parsing a subscript notation, which is how a value
    that had stopped being legal went on resolving to something anyway. There is
    one spelling now; anything else is data that was missed, not data to rescue.
    """
    if not value:
        raise KeyError(f"Empty value for primitive {primitive}")
    ord_map = ORDINALS.get(primitive, {})
    if value in ord_map:
        return value
    raise KeyError(
        f"Cannot map {primitive} value {value!r} to ordinal. "
        f"Valid keys: {list(ord_map)}"
    )




# Canonical imscription vectors (ordinal form)
imscriptions = {
    # S_human: current humanity (planetary, pre-visible)
    "human": {
        "⊢": "𐑨", "⊣": "𐑰", "≻": "𐑩", "≺": "𐑬",
        "⋈": "𐑞", "⊤": "𐑤", "∈": "𐑚", "∋": "𐑜",
        "⊙": "𐑢", "⊥": "𐑒", "⊞": "𐑕", "◻": "𐑷",
    },
    # S_civ_DM: predicted DM-aligned interstellar civilization
    "civ_dm": {
        "⊢": "𐑼", "⊣": "𐑰", "≻": "𐑽", "≺": "𐑬",
        "⋈": "𐑐", "⊤": "𐑪", "∈": "𐑲", "∋": "𐑠",
        "⊙": "⊙", "⊥": "𐑖", "⊞": "𐑳", "◻": "𐑴",
    },
    # S_noise: unmodeled pulsar noise (from MNRAS + PRD papers)
    "pulsar_noise": {
        "⊢": "𐑼", "⊣": "𐑰", "≻": "𐑩", "≺": "𐑬",
        "⋈": "𐑞", "⊤": "𐑤", "∈": "𐑚", "∋": "𐑜",
        "⊙": "𐑢", "⊥": "𐑒", "⊞": "𐑕", "◻": "𐑷",
    },
    # S_interstellar_target: structural requirements for feasible interstellar propagation
    "interstellar_target": {
        "⊢": "𐑼", "⊣": "𐑰", "≻": "𐑽", "≺": "𐑬",
        "⋈": "𐑐", "⊤": "𐑪", "∈": "𐑲", "∋": "𐑠",
        "⊙": "⊙", "⊥": "𐑖", "⊞": "𐑳", "◻": "𐑷",
    },
}


def to_vector(imscription: dict) -> np.ndarray:
    """Convert a imscription dict to an ordinal vector in canonical primitive order."""
    vec = []
    for prim in PRIMITIVE_ORDER:
        raw_val = imscription[prim]
        key = resolve_ordinal_key(prim, raw_val)
        vec.append(ORDINALS[prim][key])
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
