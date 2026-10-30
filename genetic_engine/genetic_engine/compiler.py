"""
compiler.py — Full Editing Compiler Pipeline.

Three-stage compilation:
  1. Desired AA change → codon change → nucleotide edit
  2. Frobenius stratum check → B₄ lattice path
  3. Guide design → Frobenius verification → risk score

Architecture follows the whale engine pipeline pattern:
  Desired change → codon space → B₄ lattice → Frobenius stratum
  → Guide design → Template design → Verification → Risk score
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from genetic_engine.codon import CODON_BY_SYMBOL
from genetic_engine.primitives import get_primitive_delta
from genetic_engine.editor import B4EditAnalyzer, EditCostReport
from genetic_engine.stratum import FrobeniusStratumClassifier
from genetic_engine.guide import FrobeniusGuideDesigner, GuideDesign
from genetic_engine.prime import PrimeEditOptimizer, PrimeEditDesign
from genetic_engine.verifier import FrobeniusVerifier, FrobeniusVerification
from genetic_engine.chimera import ChimeraDetector, ChimeraReport


@dataclass
class CompiledEdit:
    """A fully compiled editing protocol.

    Attributes:
        desired_change:        "XaaY → XaaZ" description
        orig_aa:               Original amino acid
        target_aa:             Desired amino acid
        codon_paths:           Optimal (orig, target, cost) paths
        best_path:             Single best path (min cost + risk)
        primitive_delta:       Primitive change analysis
        stratum_analysis:      Stratum crossing analysis
        guide_design:          Frobenius-optimized guide RNA
        prime_edit:            Frobenius-optimized prime design
        frobenius_verification: μ∘δ=id verification
        chimera_risk:          Chimera risk (if multi-edit)
        composite_score:       Overall Frobenius quality
    """
    desired_change: str
    orig_aa: str
    target_aa: str
    codon_paths: List[Tuple[str, str, int]]
    best_path: Tuple[str, str, int]
    primitive_delta: Dict
    stratum_analysis: Dict
    guide_design: Optional[GuideDesign]
    prime_edit: Optional[PrimeEditDesign]
    frobenius_verification: FrobeniusVerification
    chimera_risk: Optional[ChimeraReport]
    composite_score: float


class EditingCompiler:
    """Genetic editing compiler: AA change → Frobenius-optimal protocol."""

    def __init__(self) -> None:
        self.stratum_classifier = FrobeniusStratumClassifier()
        self.b4_analyzer = B4EditAnalyzer()
        self.guide_designer = FrobeniusGuideDesigner()
        self.prime_optimizer = PrimeEditOptimizer()
        self.frobenius_verifier = FrobeniusVerifier()
        self.chimera_detector = ChimeraDetector()

    def compile(self, orig_aa: str, target_aa: str,
                context: Tuple[str, str] = ("", "")) -> CompiledEdit:
        """Compile a desired AA change into a complete editing protocol.

        Args:
            orig_aa:   Original amino acid (e.g., "Met")
            target_aa: Desired amino acid (e.g., "Ile")
            context:   Optional (upstream_codon, downstream_codon)

        Returns:
            CompiledEdit with full protocol.
        """
        # Stage 1: Find optimal codon paths
        codon_edits = self.b4_analyzer.minimal_edit_path(orig_aa, target_aa)
        codon_paths = [(r.orig_codon, r.target_codon, r.total_cost)
                       for r in codon_edits]

        if not codon_paths:
            return CompiledEdit(
                desired_change=f"{orig_aa}→{target_aa}",
                orig_aa=orig_aa, target_aa=target_aa,
                codon_paths=[], best_path=("", "", 99),
                primitive_delta={}, stratum_analysis={},
                guide_design=None, prime_edit=None,
                frobenius_verification=FrobeniusVerification(
                    "", "", 0, 0, False, 0,
                    [f"No valid codon path from {orig_aa} to {target_aa}."]),
                chimera_risk=None, composite_score=0.0)

        best = min(codon_paths, key=lambda x: (x[2], x[0]))

        # Stage 2: Primitive delta & stratum analysis
        prim_delta = get_primitive_delta(orig_aa, target_aa)

        orig_codon_obj = CODON_BY_SYMBOL.get(best[0])
        targ_codon_obj = CODON_BY_SYMBOL.get(best[1])
        crossing = False
        crossing_risk = "?"
        if orig_codon_obj and targ_codon_obj:
            crossing = orig_codon_obj.crosses_stratum(targ_codon_obj)
            crossing_risk = FrobeniusStratumClassifier.stratum_crossing_risk(
                orig_codon_obj.stratum, targ_codon_obj.stratum)

        stratum_analysis = {
            "orig_stratum": orig_codon_obj.stratum.value if orig_codon_obj else "?",
            "target_stratum": targ_codon_obj.stratum.value if targ_codon_obj else "?",
            "crossing": crossing,
            "crossing_risk": crossing_risk,
        }

        # Stage 3: Guide, prime, verification
        try:
            guide = self.guide_designer.design(best[0])
        except Exception:
            guide = None

        try:
            up_context, down_context = context
            prime = self.prime_optimizer.optimize(
                best[0], best[1], up_context, down_context)
        except Exception:
            prime = None

        frob_ver = self.frobenius_verifier.verify(best[0], best[1])

        # Composite score
        score = frob_ver.closure_ratio
        if prim_delta.get("changed", False):
            score -= 0.1 * (PRIMITIVE_RISK_SCORE.get(prim_delta["risk_class"], 0.5) / 10.0)
        if stratum_analysis.get("crossing", False):
            score -= 0.2
        score = max(0.0, min(1.0, score))

        return CompiledEdit(
            desired_change=f"{orig_aa}→{target_aa}",
            orig_aa=orig_aa, target_aa=target_aa,
            codon_paths=codon_paths, best_path=best,
            primitive_delta=prim_delta,
            stratum_analysis=stratum_analysis,
            guide_design=guide, prime_edit=prime,
            frobenius_verification=frob_ver,
            chimera_risk=None, composite_score=score,
        )

    def compile_multi(self, edits: List[Tuple[str, str]]) -> Dict:
        """Compile a multi-edit protocol with chimera risk assessment."""
        compiled_edits = [self.compile(o, t) for o, t in edits]
        chimera = ChimeraDetector.analyze_edit_set(edits)

        min_score = min(c.composite_score for c in compiled_edits)
        tensor_penalty = min(chimera.tensor_risk / 5.0, 1.0) * 0.3
        composite = max(0.0, min_score - tensor_penalty)

        return {
            "edits": compiled_edits,
            "chimera": chimera,
            "composite_score": composite,
            "recommendation": chimera.recommendation,
        }


# Avoid circular import — risk score table needed in compile
from genetic_engine.primitives import PRIMITIVE_RISK_SCORE
