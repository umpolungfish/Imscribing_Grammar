"""
Canonical Imscribing Grammar Primitives — 3³ × 4⁵ × 5⁴ = 17,280,000 addresses.

This module is the single source of truth for the 12-primitive system.
It uses the exact Shavian glyphs and ordinal mappings from space_search/primitives.py
and ImscribingGrammar/Primitives/Core.lean.

DO NOT expand cardinalities. DO NOT rename values. This is the grammar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Literal

# =============================================================================
# The 12 Primitives with their exact canonical Shavian value sets
# (sourced from space_search/primitives.py ORDINALS + README + Core.lean)
# =============================================================================

PRIMITIVE_ORDER: List[str] = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

# Exact glyphs per primitive (the only legal values)
CANONICAL_VALUES: Dict[str, List[str]] = {
    "⊢": ["𐑛", "𐑨", "𐑼", "𐑦"],                    # Dimensionality — 4 values
    "⊣": ["𐑡", "𐑰", "𐑥", "𐑶", "𐑸"],                # Topology — 5
    ">": ["𐑩", "𐑑", "𐑽", "𐑾"],                    # Relational — 4
    "<": ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"],                # Polarity (Frobenius gate) — 5
    "⋈": ["𐑱", "𐑞", "𐑐"],                         # Fidelity — 3
    "⊤": ["𐑘", "𐑤", "𐑧", "𐑪", "𐑺"],                # Kinetics — 5
    "∈": ["𐑚", "𐑔", "𐑲"],                         # Scope / Granularity — 3
    "∋": ["𐑝", "𐑜", "𐑠", "𐑵"],                    # Composition — 4
    "⊙": ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"],               # Criticality — 5 (note: ⊙ glyph is a legal value)
    "⊥": ["𐑓", "𐑒", "𐑖", "𐑫"],                    # Chirality — 4
    "⊞": ["𐑙", "𐑕", "𐑳"],                         # Stoichiometry — 3
    "◻": ["𐑷", "𐑴", "𐑭", "𐑟"],                    # Winding — 4
}

# Ordinal ranks (1-based where possible; non-integer only for the two transitional ⊙ values)
# These are the authoritative ordinals used for all distance / tier calculations.
ORDINALS: Dict[str, Dict[str, float]] = {
    "⊢": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "⊣": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    ">": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "<": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "⋈": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "⊤": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "∈": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "∋": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "⊥": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "⊞": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "◻": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}

# Canonical weights for distance calculations (from space_search/primitives.py v0.5.0)
WEIGHTS: Dict[str, float] = {
    "⊢": 1.0, "⊣": 1.0, ">": 1.0, "<": 1.0,
    "⋈": 1.0, "⊤": 1.0, "∈": 1.0, "∋": 1.0,
    "⊙": 1.0, "⊥": 0.8, "⊞": 1.0, "◻": 0.7,
}

# Human-readable names (for docs / errors only — the glyphs are the identity)
PRIMITIVE_NAMES: Dict[str, str] = {
    "⊢": "Dimensionality",
    "⊣": "Topology",
    ">": "Relational",
    "<": "Polarity",
    "⋈": "Fidelity",
    "⊤": "Kinetics",
    "∈": "Scope",
    "∋": "Composition",
    "⊙": "Criticality",
    "⊥": "Chirality",
    "⊞": "Stoichiometry",
    "◻": "Winding",
}

# =============================================================================
# CrystalAddress — the fundamental 12-tuple type
# =============================================================================

@dataclass(frozen=True, order=True)
class CrystalAddress:
    """
    A point in the 17,280,000-address Crystal of Types.

    Represented internally as the exact 12-tuple of canonical Shavian glyphs.
    Two addresses are identical iff their 12 glyphs match.
    Distance is integer (or float with the non-integer ⊙ ranks) and O(1).
    """
    D: str   # ⊢ Dimensionality
    T: str   # ⊣ Topology
    R: str   # > Relational
    P: str   # < Polarity
    F: str   # ⋈ Fidelity
    K: str   # ⊤ Kinetics
    G: str   # ∈ Scope/Granularity
    C: str   # ∋ Composition
    Crit: str  # ⊙ Criticality (the field name is Crit; the *value* can be the glyph ⊙)
    H: str   # ⊥ Chirality
    S: str   # ⊞ Stoichiometry
    O: str   # ◻ Winding

    def __post_init__(self):
        glyph_map = self._glyph_map()
        for prim, val in glyph_map.items():
            if val not in CANONICAL_VALUES[prim]:
                raise ValueError(f"Invalid glyph for {prim}: {val!r} not in {CANONICAL_VALUES[prim]}")

    def _glyph_map(self) -> Dict[str, str]:
        return {
            "⊢": self.D, "⊣": self.T, ">": self.R, "<": self.P,
            "⋈": self.F, "⊤": self.K, "∈": self.G, "∋": self.C,
            "⊙": self.Crit, "⊥": self.H, "⊞": self.S, "◻": self.O,
        }

    @classmethod
    def from_tuple(cls, glyphs: Tuple[str, ...]) -> "CrystalAddress":
        if len(glyphs) != 12:
            raise ValueError("CrystalAddress requires exactly 12 glyphs")
        # Map positionally to the internal fields using PRIMITIVE_ORDER
        d = dict(zip(PRIMITIVE_ORDER, glyphs))
        return cls(
            D=d["⊢"], T=d["⊣"], R=d[">"], P=d["<"],
            F=d["⋈"], K=d["⊤"], G=d["∈"], C=d["∋"],
            Crit=d["⊙"], H=d["⊥"], S=d["⊞"], O=d["◻"],
        )

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "CrystalAddress":
        return cls(
            D=d["⊢"], T=d["⊣"], R=d[">"], P=d["<"],
            F=d["⋈"], K=d["⊤"], G=d["∈"], C=d["∋"],
            Crit=d["⊙"], H=d["⊥"], S=d["⊞"], O=d["◻"],
        )

    def as_tuple(self) -> Tuple[str, ...]:
        m = self._glyph_map()
        return tuple(m[p] for p in PRIMITIVE_ORDER)

    def as_dict(self) -> Dict[str, str]:
        return self._glyph_map()

    def as_notation(self) -> str:
        """Shavian notation: ⟨g1g2...g12⟩"""
        return "⟨" + "".join(self.as_tuple()) + "⟩"

    def to_vector(self) -> List[float]:
        """Ordinal vector in canonical PRIMITIVE_ORDER."""
        m = self._glyph_map()
        return [ORDINALS[p][m[p]] for p in PRIMITIVE_ORDER]

    def __str__(self) -> str:
        return self.as_notation()

    def __repr__(self) -> str:
        return f"CrystalAddress({self.as_notation()})"


# =============================================================================
# Tier calculation (O₀ ... O_∞) — canonical rules from Core.lean + README
# =============================================================================

OuroboricityTier = Literal["O₀", "O₁", "O₂", "O₂†", "O_∞"]

def ouroboricity_tier(addr: CrystalAddress) -> OuroboricityTier:
    """
    Compute the canonical ouroboricity tier from the (<, ⊙) pair (with ◻/D context).
    Matches the rules in Core.lean and the README table.
    """
    phi = addr.P
    crit = addr.Crit
    omega = addr.O
    dim = addr.D

    # R1: 𐑣er (𐑹) + ⊙_both (⊙ glyph) → O_∞ (Philosopher's Stone)
    if phi == "𐑹" and crit == "⊙":
        return "O_∞"

    # 𐑢 or sealed criticality → O₀
    if phi in ("𐑗", "𐑿"):  # the two lowest <
        return "O₀"

    # ⊙ (𐑬) family
    if phi in ("𐑬", "𐑯"):
        if crit == "𐑢":  # sealed
            if omega in ("𐑷", "𐑴"):
                return "O₁"
            return "O₂"
        if crit in ("𐑮", "𐑻"):  # open / transitional
            if dim == "𐑦":  # D_omega / D_invomega family
                return "O₂†"
            return "O₂"
        if crit == "𐑣":  # both / high
            return "O_∞"

    # Default high-criticality non-Frobenius
    if crit in ("𐑮", "𐑻", "𐑣"):
        return "O₂†" if dim == "𐑦" else "O₂"

    return "O₀"


# Convenience: the two famous addresses from the README (exact glyphs)
PHILOSOPHERS_STONE: CrystalAddress = CrystalAddress.from_dict({
    "⊢": "𐑦", "⊣": "𐑸", ">": "𐑾", "<": "𐑹",
    "⋈": "𐑐", "⊤": "𐑧", "∈": "𐑲", "∋": "𐑠",
    "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭",
})

MINIMUM_BASELINE: CrystalAddress = CrystalAddress.from_dict({
    "⊢": "𐑛", "⊣": "𐑡", ">": "𐑩", "<": "𐑗",
    "⋈": "𐑱", "⊤": "𐑘", "∈": "𐑚", "∋": "𐑝",
    "⊙": "𐑢", "⊥": "𐑓", "⊞": "𐑙", "◻": "𐑷",
})


__all__ = [
    "PRIMITIVE_ORDER", "CANONICAL_VALUES", "ORDINALS", "WEIGHTS",
    "PRIMITIVE_NAMES", "CrystalAddress",
    "ouroboricity_tier", "OuroboricityTier",
    "PHILOSOPHERS_STONE", "MINIMUM_BASELINE",
]
