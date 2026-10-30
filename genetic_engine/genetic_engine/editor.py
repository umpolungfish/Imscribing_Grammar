"""
editor.py — B₄ Lattice Edit Cost Analysis.

Every nucleotide edit is characterized by:
  - Per-position B₄ lattice distance (0, 1, or 2)
  - Covering vs cross-lattice classification
  - Frobenius stratum crossing
  - Silent/missense status

Structural rule: edits along covering relations are structurally minimal;
cross-lattice edits (B↔F, T↔N) are maximal jumps.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from genetic_engine.lattice import B4Element
from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL, AA_TO_CODONS


@dataclass
class EditCostReport:
    """Structural cost report for a nucleotide-level edit.

    Attributes:
        orig_codon:      Source codon symbol (e.g. "AUG")
        target_codon:    Target codon symbol (e.g. "AUU")
        per_position:    B₄ distances at each position (d1, d2, d3)
        total_cost:      Sum of per-position distances
        lattice_type:    covering, cross-lattice, or multi-nt
        stratum_crossing: Whether Frobenius stratum changes
        silent:          Whether amino acid is unchanged
        aa_change:       (orig_aa, target_aa) tuple
    """
    orig_codon: str
    target_codon: str
    per_position: Tuple[int, int, int]
    total_cost: int
    lattice_type: str = "multi"
    stratum_crossing: bool = False
    silent: bool = True
    aa_change: Tuple[str, str] = ("", "")

    @property
    def normalized_cost(self) -> float:
        return self.total_cost / 6.0

    @property
    def risk_level(self) -> str:
        if self.stratum_crossing:
            return "CRITICAL — stratum crossing"
        if self.total_cost >= 4:
            return "HIGH — cross-lattice distance"
        if self.total_cost >= 2:
            return "MODERATE"
        return "LOW — covering relation"


class B4EditAnalyzer:
    """Analyzes structural cost of nucleotide edits using the B₄ lattice."""

    @staticmethod
    def analyze(orig: str, target: str) -> EditCostReport:
        """Analyze the structural cost of editing orig → target."""
        c_orig = CODON_BY_SYMBOL.get(orig)
        c_targ = CODON_BY_SYMBOL.get(target)
        if c_orig is None or c_targ is None:
            raise ValueError(f"Unknown codon: {orig} or {target}")

        per_pos = c_orig.b4_distance(c_targ)
        total = sum(per_pos)
        changed_positions = sum(1 for d in per_pos if d > 0)

        if changed_positions == 1:
            max_dist = max(per_pos)
            lattice_type = "covering" if max_dist == 1 else "cross-lattice"
        else:
            lattice_type = f"multi-{changed_positions}nt"

        orig_aa = CODON_TABLE.get(orig, "X")
        targ_aa = CODON_TABLE.get(target, "X")

        return EditCostReport(
            orig_codon=orig, target_codon=target,
            per_position=per_pos, total_cost=total,
            lattice_type=lattice_type,
            stratum_crossing=c_orig.crosses_stratum(c_targ),
            silent=(orig_aa == targ_aa),
            aa_change=(orig_aa, targ_aa),
        )

    @staticmethod
    def base_editor_cost(edit_type: str) -> dict:
        """Analyze structural cost of a base editor type.

        Types: CBE (C→T), ABE (A→G), C→A, G→U, U→C, G→A.
        """
        mapping = {
            "CBE": ("C", "U"), "ABE": ("A", "G"),
            "C→A": ("C", "A"), "G→U": ("G", "U"),
            "U→C": ("U", "C"), "G→A": ("G", "A"),
        }
        if edit_type not in mapping:
            raise ValueError(f"Unknown base editor type: {edit_type}")
        orig_nuc, targ_nuc = mapping[edit_type]
        orig_b4 = B4Element.from_symbol(orig_nuc)
        targ_b4 = B4Element.from_symbol(targ_nuc)
        dist = orig_b4.lattice_distance(targ_b4)
        covering = orig_b4.covers(targ_b4) or targ_b4.covers(orig_b4)
        return {
            "edit_type": edit_type,
            "orig_nucleotide": orig_nuc, "target_nucleotide": targ_nuc,
            "orig_b4": orig_b4, "target_b4": targ_b4,
            "lattice_distance": dist,
            "is_covering": covering,
            "structural_quality": "optimal" if covering and dist == 1 else
                                   "suboptimal" if dist == 2 else "maximal_jump",
        }

    @staticmethod
    def minimal_edit_path(orig_aa: str, target_aa: str) -> List[EditCostReport]:
        """Find minimal-B₄-distance codon edit(s) from orig_aa to target_aa."""
        orig_codons = AA_TO_CODONS.get(orig_aa, [])
        targ_codons = AA_TO_CODONS.get(target_aa, [])
        if not orig_codons or not targ_codons:
            return []
        paths = [B4EditAnalyzer.analyze(oc.symbol, tc.symbol)
                 for oc in orig_codons for tc in targ_codons]
        if not paths:
            return []
        min_cost = min(p.total_cost for p in paths)
        return [p for p in paths if p.total_cost == min_cost]
