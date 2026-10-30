"""
Canonical algebra over the 17,280,000-address Crystal.

All operations are defined strictly on CrystalAddress (the 12-tuple of Shavian glyphs).
Distance uses the exact ordinals from canonical_primitives.ORDINALS.
"""

from __future__ import annotations

from typing import Dict
import math

from .canonical_primitives import (
    CrystalAddress,
    ORDINALS,
    WEIGHTS,
    PRIMITIVE_ORDER,
    ouroboricity_tier,
)


def to_vector(addr: CrystalAddress) -> list[float]:
    """Ordinal vector in canonical PRIMITIVE_ORDER."""
    return addr.to_vector()


def distance(a: CrystalAddress, b: CrystalAddress) -> float:
    """
    Weighted Euclidean distance in the crystal.
    Uses the exact canonical weights and ordinals.
    O(1).
    """
    va = a.to_vector()
    vb = b.to_vector()
    w = [WEIGHTS[p] for p in PRIMITIVE_ORDER]
    return math.sqrt(sum(w[i] * (va[i] - vb[i]) ** 2 for i in range(12)))


def directed_distance(a: CrystalAddress, b: CrystalAddress) -> float:
    """Sum of weighted upward steps only (asymmetric lattice cost)."""
    va = a.to_vector()
    vb = b.to_vector()
    w = [WEIGHTS[p] for p in PRIMITIVE_ORDER]
    return sum(w[i] * max(0.0, vb[i] - va[i]) for i in range(12))


def breakdown(a: CrystalAddress, b: CrystalAddress) -> list[dict]:
    """Per-primitive contribution to distance, sorted descending."""
    va = a.to_vector()
    vb = b.to_vector()
    w = [WEIGHTS[p] for p in PRIMITIVE_ORDER]
    rows = []
    for i, prim in enumerate(PRIMITIVE_ORDER):
        delta = abs(va[i] - vb[i])
        contrib = w[i] * delta ** 2
        rows.append({
            "primitive": prim,
            "glyph_a": getattr(a, prim),
            "glyph_b": getattr(b, prim),
            "delta": delta,
            "weighted_sq": contrib,
        })
    rows.sort(key=lambda r: r["weighted_sq"], reverse=True)
    return rows


def meet(a: CrystalAddress, b: CrystalAddress) -> CrystalAddress:
    """
    Componentwise min (bottleneck) in ordinal space.
    Returns the greatest lower bound address.
    """
    va = a.to_vector()
    vb = b.to_vector()
    glyphs = []
    for i, prim in enumerate(PRIMITIVE_ORDER):
        vmin = min(va[i], vb[i])
        candidates = [(g, ORDINALS[prim][g]) for g in ORDINALS[prim]]
        best = min((g for g, v in candidates if v <= vmin + 1e-9),
                   key=lambda g: abs(ORDINALS[prim][g] - vmin),
                   default=min(candidates, key=lambda x: x[1])[0])
        glyphs.append(best)
    return CrystalAddress.from_tuple(tuple(glyphs))


def join(a: CrystalAddress, b: CrystalAddress) -> CrystalAddress:
    """Componentwise max (lub) in ordinal space."""
    va = a.to_vector()
    vb = b.to_vector()
    glyphs = []
    for i, prim in enumerate(PRIMITIVE_ORDER):
        vmax = max(va[i], vb[i])
        candidates = [(g, ORDINALS[prim][g]) for g in ORDINALS[prim]]
        best = min(candidates, key=lambda x: abs(x[1] - vmax))[0]
        glyphs.append(best)
    return CrystalAddress.from_tuple(tuple(glyphs))


def tensor(a: CrystalAddress, b: CrystalAddress) -> CrystalAddress:
    """
    Tensor product = componentwise bottleneck (min) under the grammar's
    "weakest link" rule for most primitives (Fidelity, Polarity, etc.).
    This is the current canonical interpretation.
    """
    return meet(a, b)


def is_frobenius_closed(addr: CrystalAddress) -> bool:
    """
    True only at O_∞ (the single tier where μ∘δ = id holds by definition).
    """
    return ouroboricity_tier(addr) == "O_∞"


__all__ = [
    "to_vector",
    "distance",
    "directed_distance",
    "breakdown",
    "meet",
    "join",
    "tensor",
    "is_frobenius_closed",
]
