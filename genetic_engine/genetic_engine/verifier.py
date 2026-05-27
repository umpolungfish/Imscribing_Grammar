"""
verifier.py — Frobenius Closure Verification (μ∘δ=id).

The Frobenius condition is the central invariant:
  δ (comultiplication) = the edit specification (template, guide)
  μ (multiplication)   = the genetic code table (translation)
  μ∘δ = id means the edit produces the intended amino acid
        AND preserves the Frobenius stratum structure.

Edits that cross strata or change primitives are Frobenius-open.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

from genetic_engine.lattice import B4Element
from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL, FrobeniusStratum
from genetic_engine.primitives import AA_PRIMITIVE_MAP


@dataclass
class FrobeniusVerification:
    """Result of Frobenius closure verification for an editing protocol.

    Attributes:
        target_codon:    Codon being edited
        edit_codon:      Intended edit
        delta_quality:   Quality of the edit template (δ map)
        mu_quality:      Quality of the decoding (μ map)
        frobenius_closed: Whether μ∘δ=id holds
        closure_ratio:   How close to perfect closure (0-1)
        defects:         Frobenius-open defects detected
    """
    target_codon: str
    edit_codon: str
    delta_quality: float
    mu_quality: float
    frobenius_closed: bool
    closure_ratio: float
    defects: List[str]


class FrobeniusVerifier:
    """Verifies that an editing protocol satisfies μ∘δ=id."""

    @staticmethod
    def verify(target_codon: str, edit_codon: str) -> FrobeniusVerification:
        """Verify μ∘δ=id for a codon edit."""
        c_orig = CODON_BY_SYMBOL.get(target_codon)
        c_edit = CODON_BY_SYMBOL.get(edit_codon)
        if c_orig is None or c_edit is None:
            return FrobeniusVerification(
                target_codon=target_codon, edit_codon=edit_codon,
                delta_quality=0.0, mu_quality=0.0,
                frobenius_closed=False, closure_ratio=0.0,
                defects=["Unknown codon(s) — cannot verify."])

        orig_aa = CODON_TABLE.get(target_codon, "X")
        edit_aa = CODON_TABLE.get(edit_codon, "X")
        defects = []

        # δ quality: how well the edit template specifies the target
        delta_quality = 1.0
        if c_orig.stratum != c_edit.stratum:
            delta_quality -= 0.3
            defects.append(
                f"Stratum crossing ({c_orig.stratum.value} → {c_edit.stratum.value}): "
                f"δ must specify extra positional information.")
        b4_cost = c_orig.total_b4_distance(c_edit)
        delta_quality -= min(b4_cost / 6.0, 1.0) * 0.2

        # μ quality: how faithfully the product is read
        mu_quality = 1.0
        if orig_aa != edit_aa:
            orig_prim = AA_PRIMITIVE_MAP.get(orig_aa, None)
            edit_prim = AA_PRIMITIVE_MAP.get(edit_aa, None)
            if orig_prim != edit_prim:
                mu_quality -= 0.2
                defects.append(
                    f"Primitive change ({orig_prim} → {edit_prim}): "
                    f"μ-map reads a different structural class.")
            # Split-stratum wobble check
            if c_edit.stratum == FrobeniusStratum.SPLIT and orig_aa == edit_aa:
                p3_orig_y = c_orig.p3 in (B4Element.T, B4Element.N)
                p3_edit_y = c_edit.p3 in (B4Element.T, B4Element.N)
                if p3_orig_y != p3_edit_y:
                    mu_quality -= 0.15
                    defects.append(
                        f"Wobble violation at split-stratum position 3: "
                        f"Y/R type changed.")

        delta_quality = max(0.0, delta_quality)
        mu_quality = max(0.0, mu_quality)
        closure_ratio = delta_quality * 0.4 + mu_quality * 0.6
        frobenius_closed = closure_ratio >= 0.85

        defects.append(
            f"μ∘δ {'PASSES' if frobenius_closed else 'FAILS'}: "
            f"closure_ratio={closure_ratio:.3f}")

        return FrobeniusVerification(
            target_codon=target_codon, edit_codon=edit_codon,
            delta_quality=delta_quality, mu_quality=mu_quality,
            frobenius_closed=frobenius_closed,
            closure_ratio=closure_ratio, defects=defects)

    @staticmethod
    def verify_protocol(edits: List[Tuple[str, str]]) -> Dict:
        """Verify a multi-step editing protocol for Frobenius closure."""
        verifications = [FrobeniusVerifier.verify(t, e) for t, e in edits]
        all_closed = all(v.frobenius_closed for v in verifications)
        comp_ratio = sum(v.closure_ratio for v in verifications) / max(len(verifications), 1)
        return {
            "per_edit": verifications,
            "composite_closure_ratio": comp_ratio,
            "all_closed": all_closed,
            "protocol_quality": "optimal" if comp_ratio >= 0.95 else
                                "acceptable" if comp_ratio >= 0.85 else
                                "suboptimal" if comp_ratio >= 0.7 else "broken",
            "edit_count": len(edits),
        }
