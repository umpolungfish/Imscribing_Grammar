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

# Ordinal mappings for each primitive tier
ORDINALS = {
    "Ð": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "Þ": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "Ř": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "Φ": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "ƒ": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "Ç": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "Γ": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "ɢ": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "Ħ": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "Σ": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "Ω": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}

# Primitive weights (canonical v0.5.0)
WEIGHTS = {
    "Ð": 1.0, "Þ": 1.0, "Ř": 1.0, "Φ": 1.0,
    "ƒ": 1.0, "Ç": 1.0, "Γ": 1.0, "ɢ": 1.0,
    "⊙": 1.0, "Ħ": 0.8, "Σ": 1.0, "Ω": 0.7,
}

PRIMITIVE_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
# Subscript-to-Deseret mapping for catalog values in notation format (e.g., "𐑛" -> Deseret key)
# The catalog stores values as Primitive_subscript/^superscript, but ORDINALS
# uses Deseret alphabet characters (U+1045x-U+1047x).
SUBSCRIPT_TO_DESERET = {
    "Ð": {";": "\U0001045B", "C": "\U00010468", "ß": "\U0001047C", "\u03c9": "\U00010466"},
    "Þ": {"6": "\U00010461", "K": "\U00010470", "\u00f2": "\U00010465", "O": "\U00010476", "\u00a8": "\U00010478"},
    "Ř": {"\u00af": "\U00010469", "\u00fd": "\U00010451", "\u0164": "\U0001047D", "=": "\U0001047E"},
    "Φ": {"\u0250": "\U00010457", "\u03c5": "\U0001047F", "\u02d9": "\U0001046C", "F": "\U0001046F", "}": "\U00010479"},
    "ƒ": {"\u00ec": "\U00010471", "\u00f0": "\U0001045E", "\u017c": "\U00010450"},
    "Ç": {"-": "\U00010458", "W": "\U00010464", "@": "\U00010467", "\u03bb": "\U0001046A", "\u00d9": "\U0001047A"},
    "Γ": {"\u03b2": "\U0001045A", "\u03b3": "\U0001045A", "\u0294": "\U00010454"},
    "ɢ": {"\u2227": "\U0001045D", "\u02dd": "\U0001045C", "\u02cc": "\U00010460", "\u015e": "\U00010475"},
    "⊙": {"\u017e": "\U00010462", "\u00ff": "\u2299", "\u00c6": "\U0001046E", "3": "\U0001047B", "\u0162": "\U00010463"},
    "Ħ": {"\u00d1": "\U00010453", "\u00a3": "\U00010452", "A": "\U00010456", "!": "\U0001046B"},
    "Σ": {"S": "\U00010459", "\u0151": "\U00010455", "\u00ef": "\U00010473"},
    "Ω": {"\u00c5": "\U00010477", "2": "\U00010474", "z": "\U0001046D", "5": "\U0001045F"},
}


def resolve_ordinal_key(primitive: str, value: str) -> str:
    """Convert a catalog value to the Deseret ordinal key used by ORDINALS.
    
    Handles three formats:
      1. Already a valid ORDINALS key (Deseret char or literal symbol like \u2299)
      2. Notation format: Primitive_separator_subscript (e.g., "Ð_\u00df")
    """
    if not value:
        raise KeyError(f"Empty value for primitive {primitive}")
    ord_map = ORDINALS.get(primitive, {})
    # Direct match (already a valid key)
    if value in ord_map:
        return value
    # Parse subscript notation
    if len(value) >= 3:
        subscript = value[2]
        mapping = SUBSCRIPT_TO_DESERET.get(primitive, {})
        if subscript in mapping:
            deseret_key = mapping[subscript]
            if deseret_key in ord_map:
                return deseret_key
    # Last resort: check if the entire value is a subscript key
    ord_map_vals = list(ord_map.keys())
    raise KeyError(
        f"Cannot map {primitive} value '{value}' to ordinal. "
        f"Valid keys include: {ord_map_vals[:3]}..."
    )




# Canonical imscription vectors (ordinal form)
imscriptions = {
    # S_human: current humanity (planetary, pre-visible)
    "human": {
        "Ð": "𐑨", "Þ": "𐑰", "Ř": "𐑩", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑤", "Γ": "𐑚", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", "Σ": "𐑕", "Ω": "𐑷",
    },
    # S_civ_DM: predicted DM-aligned interstellar civilization
    "civ_dm": {
        "Ð": "𐑼", "Þ": "𐑰", "Ř": "𐑽", "Φ": "𐑬",
        "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑠",
        "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑴",
    },
    # S_noise: unmodeled pulsar noise (from MNRAS + PRD papers)
    "pulsar_noise": {
        "Ð": "𐑼", "Þ": "𐑰", "Ř": "𐑩", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑤", "Γ": "𐑚", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", "Σ": "𐑕", "Ω": "𐑷",
    },
    # S_interstellar_target: structural requirements for feasible interstellar propagation
    "interstellar_target": {
        "Ð": "𐑼", "Þ": "𐑰", "Ř": "𐑽", "Φ": "𐑬",
        "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑠",
        "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑷",
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
