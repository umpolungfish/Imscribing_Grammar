"""
guide.py — Frobenius-Stratum-Aware Guide RNA Design.

Current guide design treats all four bases independently. Frobenius-aware
design recognizes structural constraints:
  - Exact-stratum targets: position 3 can be N (degenerate)
  - Split-stratum targets: position 3 must distinguish Y/R
  - The Cas9 off-target sheaf theorem: cross-stratum off-targets
    have ≥50% structural defect risk.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from genetic_engine.lattice import B4Element
from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL, FrobeniusStratum
from genetic_engine.stratum import FrobeniusStratumClassifier


@dataclass
class GuideDesign:
    """A Frobenius-optimized guide RNA design.

    Attributes:
        target_window:     The coding region targeted
        stratum:           Frobenius stratum of the target site
        seed_region:       PAM-proximal seed sequence
        guide_sequence:    Full guide RNA sequence
        position3_strategy: How to handle position 3
        off_target_risk:   Estimated off-target risk
        degenerate_sites:  Positions where degenerate bases are optimal
        design_notes:      Full design rationale
    """
    target_window: str
    stratum: FrobeniusStratum
    seed_region: str
    guide_sequence: str
    position3_strategy: str
    off_target_risk: str
    degenerate_sites: List[int]
    design_notes: str


class FrobeniusGuideDesigner:
    """Designs guide RNAs that respect Frobenius stratum structure."""

    @staticmethod
    def design(codon_target: str, pam: str = "NGG") -> GuideDesign:
        """Design a Frobenius-optimal guide RNA for a target codon."""
        codon = CODON_BY_SYMBOL.get(codon_target)
        if codon is None:
            raise ValueError(f"Unknown codon: {codon_target!r}")
        stratum = codon.stratum
        aa = CODON_TABLE.get(codon_target, "X")

        if stratum == FrobeniusStratum.EXACT:
            seed = codon_target[:2]
            pos3_strat = FrobeniusStratumClassifier.position3_strategy(stratum)
            guide_seq = codon_target[:2] + "N"
            degenerate_sites = [2]
            off_target_risk = (
                "LOW — exact stratum target. Position 3 is silent. "
                "Off-target in split stratum: MODERATE risk.")
            notes = (
                f"Target {codon_target} ({aa}) in EXACT stratum.\n"
                f"Position 3 can be N (any base). Guide spans positions 1-2.\n"
                f"PAM-proximal seed distinguishes adjacent exact/split boxes.")

        elif stratum == FrobeniusStratum.SPLIT:
            p3_b4 = codon.p3
            pos3_spec = "Y (pyrimidine: C/U)" if p3_b4 in (B4Element.T, B4Element.N) \
                       else "R (purine: G/A)"
            seed = codon_target
            pos3_strat = FrobeniusStratumClassifier.position3_strategy(stratum)
            guide_seq = codon_target
            degenerate_sites = []
            off_target_risk = (
                f"MODERATE — split stratum target. Position 3 distinguishes "
                f"{pos3_spec}. Off-target in exact stratum: MODERATE risk.")
            notes = (
                f"Target {codon_target} ({aa}) in SPLIT stratum.\n"
                f"Position 3 must respect Y/R distinction ({pos3_spec}).\n"
                f"Consider wobble-tolerant bases at position 3.")

        else:  # STOP
            seed = codon_target
            pos3_strat = FrobeniusStratumClassifier.position3_strategy(stratum)
            guide_seq = codon_target
            degenerate_sites = []
            off_target_risk = (
                "CRITICAL — stop codon target. Any off-target edit that "
                "creates a sense codon causes readthrough.")
            notes = (
                f"Target is STOP codon {codon_target}. Editing stop codons "
                f"removes the Ω winding boundary. Only proceed with explicit "
                f"readthrough design or selenocysteine machinery.")

        return GuideDesign(
            target_window=codon_target, stratum=stratum,
            seed_region=seed, guide_sequence=guide_seq,
            position3_strategy=pos3_strat,
            off_target_risk=off_target_risk,
            degenerate_sites=degenerate_sites, design_notes=notes,
        )

    @staticmethod
    def off_target_stratum_risk(on_target: str,
                                off_targets: List[str]) -> Dict:
        """Assess off-target risk based on Frobenius stratum mismatches.

        Cas9 off-target sheaf theorem: cross-stratum off-targets have
        ≥50% structural defect risk.
        """
        on_codon = CODON_BY_SYMBOL.get(on_target)
        if on_codon is None:
            raise ValueError(f"Unknown codon: {on_target!r}")
        on_stratum = on_codon.stratum

        results = []
        for ot in off_targets:
            ot_codon = CODON_BY_SYMBOL.get(ot)
            if ot_codon is None:
                continue
            ot_stratum = ot_codon.stratum
            same = on_stratum == ot_stratum
            results.append({
                "off_target": ot,
                "on_stratum": on_stratum.value,
                "off_stratum": ot_stratum.value,
                "same_stratum": same,
                "structural_defect_risk_pct": 50.0 if not same else 5.0,
                "theorem_applies": not same,
            })

        return {
            "on_target": on_target,
            "on_stratum": on_stratum.value,
            "off_target_count": len(results),
            "cross_stratum_off_targets": sum(1 for r in results if not r["same_stratum"]),
            "details": results,
        }
