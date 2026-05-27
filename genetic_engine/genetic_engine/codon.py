"""
codon.py — Codon Table with Frobenius Stratum Classification.

The 64 codons partition into 16 boxes, which split 8/8 into:
  - Exact stratum (8 boxes, 32 codons): position 3 is silent.
    μ∘δ=id holds exactly on this stratum.
  - Split stratum (8 boxes, 29 codons + 3 stops): position 3
    distinguishes pyrimidine (Y) from purine (R). ℤ₂ wobble symmetry.
  - Stop stratum (3 codons): Ω winding boundary.

Exact boxes (p2=C, or p2∈{U,G} with p1∈{C,G}):
  CU_, CC_, CG_, CA_, AC_, GC_, UC_, GU_, GG_
  Wait — CG_ has p2=G not C. Let me recompute.
  
  Exact iff p2=C (T), OR (p2∈{U,G} (N,B) AND p1∈{C,G} (T,B))
  p2=C: UC_, CC_, AC_, GC_ (4 boxes)
  p2∈{U,G} AND p1∈{C,G}: CU_, CG_, GU_, GG_ (4 boxes)
  Total: 8 exact boxes ✓
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from genetic_engine.lattice import B4Element


class FrobeniusStratum(Enum):
    """The three Frobenius strata of the genetic code.

    EXACT — position 3 is silent (no information). 8 boxes, 32 codons.
            μ∘δ=id holds exactly on this stratum.
    SPLIT — position 3 distinguishes pyrimidine (Y) from purine (R).
            8 boxes, 29 codons (2 are stop). ℤ₂ wobble symmetry.
    STOP  — termination codons with Ω boundary. 3 codons.
    """
    EXACT = "exact"
    SPLIT = "split"
    STOP = "stop"


@dataclass(frozen=True)
class Codon:
    """A single codon: three B₄ elements with Frobenius stratum.

    Attributes:
        p1, p2, p3: Three nucleotide positions as B₄ elements.
    """
    p1: B4Element
    p2: B4Element
    p3: B4Element

    def __post_init__(self) -> None:
        assert isinstance(self.p1, B4Element)
        assert isinstance(self.p2, B4Element)
        assert isinstance(self.p3, B4Element)

    @property
    def symbol(self) -> str:
        return self.p1.to_symbol() + self.p2.to_symbol() + self.p3.to_symbol()

    @property
    def box_name(self) -> str:
        """First two positions with underscore, e.g. 'CU_'."""
        return self.p1.to_symbol() + self.p2.to_symbol() + "_"

    @property
    def is_exact_stratum(self) -> bool:
        """Exact iff p2=C, or p2∈{U,G} with p1∈{C,G}."""
        if self.p2 == B4Element.T:  # C at position 2
            return True
        if self.p2 in (B4Element.B, B4Element.N) and \
           self.p1 in (B4Element.T, B4Element.B):  # C/G at pos1, G/U at pos2
            return True
        return False

    @property
    def is_split_stratum(self) -> bool:
        return not self.is_exact_stratum and not self.is_stop

    @property
    def is_stop(self) -> bool:
        return self.symbol in ("UAA", "UAG", "UGA")

    @property
    def is_start(self) -> bool:
        return self.symbol == "AUG"

    @property
    def stratum(self) -> FrobeniusStratum:
        if self.is_stop:
            return FrobeniusStratum.STOP
        if self.is_exact_stratum:
            return FrobeniusStratum.EXACT
        return FrobeniusStratum.SPLIT

    @property
    def amino_acid(self) -> str:
        return CODON_TABLE.get(self.symbol, "Xaa")

    def b4_distance(self, other: Codon) -> Tuple[int, int, int]:
        """Per-position B₄ lattice distance to another codon."""
        return (
            self.p1.lattice_distance(other.p1),
            self.p2.lattice_distance(other.p2),
            self.p3.lattice_distance(other.p3),
        )

    def total_b4_distance(self, other: Codon) -> int:
        """Sum of per-position B₄ distances."""
        return sum(self.b4_distance(other))

    def crosses_stratum(self, other: Codon) -> bool:
        """Does editing this codon to the other cross Frobenius strata?"""
        return self.stratum != other.stratum

    def __repr__(self) -> str:
        return f"Codon({self.symbol} → {self.amino_acid}, {self.stratum.value})"


# ── Build codon table ──────────────────────────────────────────────────

def _build_codon_table() -> Tuple[Dict[str, str], List[Codon]]:
    """Build complete codon table algorithmically.

    Returns (aa_map, codon_list) where aa_map maps symbol→amino acid.
    """
    b4_map = {'G': B4Element.B, 'C': B4Element.T,
              'A': B4Element.F, 'U': B4Element.N}

    std_code = {
        "UUU": "Phe", "UUC": "Phe",
        "UUA": "Leu", "UUG": "Leu",
        "CUU": "Leu", "CUC": "Leu", "CUA": "Leu", "CUG": "Leu",
        "AUU": "Ile", "AUC": "Ile", "AUA": "Ile",
        "AUG": "Met",
        "GUU": "Val", "GUC": "Val", "GUA": "Val", "GUG": "Val",
        "UCU": "Ser", "UCC": "Ser", "UCA": "Ser", "UCG": "Ser",
        "AGU": "Ser", "AGC": "Ser",
        "CCU": "Pro", "CCC": "Pro", "CCA": "Pro", "CCG": "Pro",
        "ACU": "Thr", "ACC": "Thr", "ACA": "Thr", "ACG": "Thr",
        "GCU": "Ala", "GCC": "Ala", "GCA": "Ala", "GCG": "Ala",
        "UAU": "Tyr", "UAC": "Tyr",
        "UAA": "Stop", "UAG": "Stop", "UGA": "Stop",
        "CAU": "His", "CAC": "His",
        "CAA": "Gln", "CAG": "Gln",
        "AAU": "Asn", "AAC": "Asn",
        "AAA": "Lys", "AAG": "Lys",
        "GAU": "Asp", "GAC": "Asp",
        "GAA": "Glu", "GAG": "Glu",
        "UGU": "Cys", "UGC": "Cys",
        "UGG": "Trp",
        "CGU": "Arg", "CGC": "Arg", "CGA": "Arg", "CGG": "Arg",
        "AGA": "Arg", "AGG": "Arg",
        "GGU": "Gly", "GGC": "Gly", "GGA": "Gly", "GGG": "Gly",
    }

    aa_map: Dict[str, str] = {}
    codons: List[Codon] = []
    for sym, aa in std_code.items():
        p1 = b4_map[sym[0]]
        p2 = b4_map[sym[1]]
        p3 = b4_map[sym[2]]
        codon = Codon(p1=p1, p2=p2, p3=p3)
        aa_map[sym] = aa
        codons.append(codon)
    return aa_map, codons


CODON_TABLE, ALL_CODONS = _build_codon_table()

# Cached lookups
CODON_BY_SYMBOL: Dict[str, Codon] = {c.symbol: c for c in ALL_CODONS}

AA_TO_CODONS: Dict[str, List[Codon]] = defaultdict(list)
for c in ALL_CODONS:
    AA_TO_CODONS[CODON_TABLE[c.symbol]].append(c)

# Box grouping
BOX_TO_CODONS: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
for sym, aa in CODON_TABLE.items():
    box = sym[:2] + "_"
    BOX_TO_CODONS[box].append((sym, aa))
