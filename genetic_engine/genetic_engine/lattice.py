"""
lattice.py — B₄ Nucleotide Type System with Covering Relations.

The four nucleotides form a distributive lattice isomorphic to B₄:
           B = Both (G)
          / \
     T = C   N = U  (T/U)
          \\ /
       F = False (A)

  B = ⊤ (top), F = ⊥ (bottom)
  T and N are incomparable (neither covers the other)
  Covering: B⊳T, B⊳N, T⊳F, N⊳F
  Cross-lattice: B↔F (distance 2), T↔N (distance 2)

Nucleotide → B₄ mapping is structural, not arbitrary:
  G→B (Both): purine, keto, 2 H-bonds — topologically unconstrained
  C→T (True): pyrimidine, amino, 3 H-bonds — complementary
  A→F (False): purine, amino, 2 H-bonds — dual to C
  U/T→N (Neither): pyrimidine, keto, 2 H-bonds — dual to A
"""

from __future__ import annotations
from enum import Enum


class B4Element(Enum):
    """The four elements of the B₄ lattice — nucleotide structural types.

    Each element has a fixed position in the lattice with deterministic
    join, meet, covering, and distance operations.
    """
    B = "Both"       # G — purine, keto, 2 H-bonds (⊤)
    T = "True"       # C — pyrimidine, amino, 3 H-bonds
    N = "Neither"    # U/T — pyrimidine, keto, 2 H-bonds
    F = "False"      # A — purine, amino, 2 H-bonds (⊥)

    # ── Lattice operations ───────────────────────────────────────────────

    def join(self, other: B4Element) -> B4Element:
        """Least upper bound: the ∨ (OR) of the lattice.

        B∨x = B for all x; F∨x = x for all x; T∨N = B.
        """
        if self == other or other == B4Element.F:
            return self
        if self == B4Element.F:
            return other
        return B4Element.B  # any two distinct non-F elements → B

    def meet(self, other: B4Element) -> B4Element:
        """Greatest lower bound: the ∧ (AND) of the lattice.

        F∧x = F for all x; B∧x = x for all x; T∧N = F.
        """
        if self == other or other == B4Element.B:
            return self
        if self == B4Element.B:
            return other
        return B4Element.F  # any two distinct non-B elements → F

    def covers(self, other: B4Element) -> bool:
        """Is other covered by self? (other < self with no intermediate)

        Covering relations define structural edit cost = 1:
          B covers T, N   (Both → True, Both → Neither)
          T covers F       (True → False)
          N covers F       (Neither → False)
        """
        return (self == B4Element.B and other in (B4Element.T, B4Element.N)) or \
               (self in (B4Element.T, B4Element.N) and other == B4Element.F)

    def lattice_distance(self, other: B4Element) -> int:
        """Shortest path length in the Hasse diagram.

        0 = same element
        1 = covering relation (direct Hasse edge)
        2 = cross-lattice (B↔F, T↔N)
        """
        if self == other:
            return 0
        if self.covers(other) or other.covers(self):
            return 1
        return 2  # cross-lattice

    @classmethod
    def from_symbol(cls, symbol: str) -> B4Element:
        """Map nucleotide symbol to B₄ element."""
        mapping = {
            'G': cls.B, 'g': cls.B,
            'C': cls.T, 'c': cls.T,
            'A': cls.F, 'a': cls.F,
            'U': cls.N, 'u': cls.N,
            'T': cls.N, 't': cls.N,  # DNA thymine = U equivalent in B₄
        }
        if symbol not in mapping:
            raise ValueError(f"Unknown nucleotide symbol: {symbol!r}")
        return mapping[symbol]

    def to_symbol(self) -> str:
        """Map B₄ element back to RNA nucleotide symbol."""
        return {B4Element.B: 'G', B4Element.T: 'C',
                B4Element.N: 'U', B4Element.F: 'A'}[self]

    def __repr__(self) -> str:
        return f"B₄({self.value})"


# ── Lattice constants ─────────────────────────────────────────────

B4_TOP = B4Element.B
B4_BOTTOM = B4Element.F

# Covering relations as edge pairs
B4_COVERING_EDGES = [
    (B4Element.B, B4Element.T),
    (B4Element.B, B4Element.N),
    (B4Element.T, B4Element.F),
    (B4Element.N, B4Element.F),
]

# Cross-lattice pairs (distance 2)
B4_CROSS_PAIRS = [
    (B4Element.B, B4Element.F),
    (B4Element.T, B4Element.N),
    (B4Element.F, B4Element.B),
    (B4Element.N, B4Element.T),
]
