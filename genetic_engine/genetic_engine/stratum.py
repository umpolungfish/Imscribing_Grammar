"""
stratum.py — Frobenius Stratum Classifier.

Classifies codons and genomic regions by Frobenius stratum.
Detects stratum boundaries across edit windows.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from genetic_engine.codon import CODON_BY_SYMBOL, FrobeniusStratum


@dataclass
class StratumReport:
    """Report of Frobenius stratum analysis for a codon or edit window.

    Attributes:
        target_window:     List of codon symbols being analyzed
        strata:            Frobenius stratum of each position
        exact_count:       Number of exact-stratum codons
        split_count:       Number of split-stratum codons
        stop_count:        Number of stop codons
        has_boundary:      Whether stratum changes between adjacent codons
        boundary_positions: Indices where stratum changes
    """
    target_window: List[str]
    strata: List[FrobeniusStratum]
    exact_count: int = 0
    split_count: int = 0
    stop_count: int = 0
    has_boundary: bool = False
    boundary_positions: List[int] = field(default_factory=list)


class FrobeniusStratumClassifier:
    """Classifies codons by Frobenius stratum and detects boundaries."""

    @staticmethod
    def classify(codon_symbol: str) -> FrobeniusStratum:
        """Classify a single codon by Frobenius stratum."""
        codon = CODON_BY_SYMBOL.get(codon_symbol)
        if codon is None:
            raise ValueError(f"Unknown codon: {codon_symbol!r}")
        return codon.stratum

    @staticmethod
    def analyze_window(window: List[str]) -> StratumReport:
        """Analyze a list of codon symbols for stratum structure."""
        strata = []
        for sym in window:
            codon = CODON_BY_SYMBOL.get(sym)
            if codon is None:
                raise ValueError(f"Unknown codon: {sym!r}")
            strata.append(codon.stratum)

        exact_count = sum(1 for s in strata if s == FrobeniusStratum.EXACT)
        split_count = sum(1 for s in strata if s == FrobeniusStratum.SPLIT)
        stop_count = sum(1 for s in strata if s == FrobeniusStratum.STOP)

        boundaries = [i for i in range(len(strata) - 1) if strata[i] != strata[i + 1]]

        return StratumReport(
            target_window=window, strata=strata,
            exact_count=exact_count, split_count=split_count,
            stop_count=stop_count,
            has_boundary=len(boundaries) > 0,
            boundary_positions=boundaries,
        )

    @staticmethod
    def position3_strategy(stratum: FrobeniusStratum) -> str:
        """Return the optimal editing strategy for position 3 in this stratum."""
        strategies = {
            FrobeniusStratum.EXACT: "N — degenerate (any base). Position 3 is silent.",
            FrobeniusStratum.SPLIT: "Y or R — must distinguish pyrimidine from purine. "
                                    "Use W (A/U) or S (G/C) wobble pairs.",
            FrobeniusStratum.STOP:  "Exact — stop codons require precise specification.",
        }
        return strategies.get(stratum, "Unknown stratum")

    @staticmethod
    def stratum_crossing_risk(from_stratum: FrobeniusStratum,
                               to_stratum: FrobeniusStratum) -> str:
        """Assess the risk of crossing between Frobenius strata."""
        if from_stratum == to_stratum:
            return "none — same stratum"
        crossings = {
            (FrobeniusStratum.EXACT, FrobeniusStratum.SPLIT):
                "HIGH — position 3 gains information. Silent site becomes meaningful.",
            (FrobeniusStratum.SPLIT, FrobeniusStratum.EXACT):
                "MODERATE — position 3 loses information. Two distinct AAs may collapse.",
            (FrobeniusStratum.EXACT, FrobeniusStratum.STOP):
                "CRITICAL — stop codon created. C-terminal truncation.",
            (FrobeniusStratum.SPLIT, FrobeniusStratum.STOP):
                "CRITICAL — stop codon created. Loss of downstream coding.",
            (FrobeniusStratum.STOP, FrobeniusStratum.EXACT):
                "CRITICAL — Ω winding boundary removed. Readthrough.",
            (FrobeniusStratum.STOP, FrobeniusStratum.SPLIT):
                "CRITICAL — Ω winding boundary removed. Readthrough.",
        }
        return crossings.get((from_stratum, to_stratum),
                             "unknown crossing — assess manually")
