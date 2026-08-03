"""
chimera.py — Tensor Product Risk for Multi-Primitive Edits.

The Chimera Theorem: composite risk of multi-primitive edits is TENSORIAL,
not additive. Two independently tolerable edits at different primitive classes
can produce a trap state (𐑪) when combined.

Key dangerous pairs:
  Ħ⊗⊢, Ħ⊗Ω, ⊢⊗Ω → ALWAYS trap (critical×critical)
  >⊗Ħ, >⊗⊢, >⊗Ω, φ̂⊗Ħ, φ̂⊗> → trap (high×critical/high)
  ⊣⊗>, <⊗φ̂, ⊤⊗Ħ, ∈⊗> → semi-trap (moderate×critical/high)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from genetic_engine.primitives import (
    IGPrimitive, AA_PRIMITIVE_MAP, PRIMITIVE_RISK,
    PRIMITIVE_RISK_SCORE, get_primitive_delta,
)


@dataclass
class ChimeraReport:
    """Report of tensor risk for multi-primitive edits.

    Attributes:
        edits:              Primitive changes being made
        individual_risks:   Risk of each edit individually
        tensor_risk:        Tensor product risk multiplier
        tensor_class:       Risk classification after tensor
        is_trap_state:      Whether combination creates frozen-order trap
        trap_description:   Trap state mechanism
        recommendation:     Clinical recommendation
    """
    edits: List[str]
    individual_risks: List[str]
    tensor_risk: float
    tensor_class: str
    is_trap_state: bool
    trap_description: str
    recommendation: str


class ChimeraDetector:
    """Detects dangerous tensor-product interactions between primitive edits."""

    _TENSOR_TABLE: Dict[Tuple[Optional[IGPrimitive], Optional[IGPrimitive]],
                        Tuple[float, bool, str]] = {}

    @classmethod
    def _init_tensor_table(cls) -> None:
        if cls._TENSOR_TABLE:
            return
        P = IGPrimitive
        pairs = [
            # Critical × Critical → ALWAYS trap
            (P.CHIRALITY, P.SCOPE, 4.0, True,
             "Chiral scope collapsed: editing both chirality and translation scope "
             "creates a protein that cannot fold correctly in any chiral form."),
            (P.CHIRALITY, P.WINDING, 4.0, True,
             "Chiral winding break: removing both chiral specificity and C-terminal "
             "winding produces a topologically uncontrolled peptide."),
            (P.SCOPE, P.WINDING, 4.0, True,
             "Scope/winding annihilation: editing both start and stop destroys "
             "the entire translation boundary structure."),
            # High × Critical/High → TRAP
            (P.REVERSIBILITY, P.CHIRALITY, 3.5, True,
             "Irreversible chiral loss: editing a disulfide Cys AND an Asp active-site "
             "enforcer creates a structurally frozen active site."),
            (P.REVERSIBILITY, P.SCOPE, 3.5, True,
             "Reversibility/scope trap: editing Cys and Met locks the translational "
             "start into a disulfide-bridged conformation."),
            (P.REVERSIBILITY, P.WINDING, 3.5, True,
             "Disulfide readthrough: editing a disulfide Cys near a stop codon "
             "creates an orphan half-cystine at the C-terminus."),
            (P.CRITICALITY, P.CHIRALITY, 3.5, True,
             "Critical chiral node: editing Gln at a regulatory node AND Asp at "
             "an active site creates metabolic runaway with no chiral correction."),
            (P.CRITICALITY, P.REVERSIBILITY, 3.5, True,
             "Critical irreversibility: editing Gln AND Cys in the same pathway "
             "produces a metabolic bottleneck that cannot be reversed."),
            # Moderate × Critical/High → semi-trap
            (P.TOPOLOGY, P.REVERSIBILITY, 2.5, False,
             "Topological irreversibility: editing Trp AND Cys reduces both "
             "structural complexity and flexibility."),
            (P.PARITY, P.CRITICALITY, 2.5, False,
             "Parity-critical coupling: editing Tyr AND Gln removes both "
             "the signaling switch and its control node."),
            (P.KINETICS, P.CHIRALITY, 2.5, False,
             "Kinetic-chiral bottleneck: editing Ile AND Asp slows translation "
             "and mis-folds the product."),
            (P.GRAMMAR, P.REVERSIBILITY, 2.5, False,
             "Grammatical irreversibility: editing His AND Cys at the same "
             "active site creates a pH-locked irreversible bond."),
            # Low-risk pairs
            (P.ENTROPY, P.FORCE, 1.2, False,
             "Low-risk: Lys (charge/entropy) + Phe (hydrophobicity) edits "
             "affect orthogonal structural dimensions."),
            (P.ENTROPY, P.INTERACTION, 1.2, False,
             "Low-risk: Lys (acetylation) + Asn (glycosylation) edits "
             "affect orthogonal post-translational modifications."),
            (P.FORCE, P.INTERACTION, 1.2, False,
             "Low-risk: hydrophobic packing + glycosylation are orthogonal."),
        ]
        for a, b, mult, trap, desc in pairs:
            cls._TENSOR_TABLE[(a, b)] = (mult, trap, desc)
            cls._TENSOR_TABLE[(b, a)] = (mult, trap, desc)

    @classmethod
    def tensor_product(cls, prim_a: Optional[IGPrimitive],
                       prim_b: Optional[IGPrimitive]) -> Tuple[float, bool, str]:
        """Compute the tensor risk of editing two primitives together."""
        cls._init_tensor_table()
        if prim_a is None or prim_b is None:
            return (1.0, False, "No tensor: ground-layer primitive.")
        key = (prim_a, prim_b)
        if key in cls._TENSOR_TABLE:
            return cls._TENSOR_TABLE[key]
        # Default: product of risks normalized
        risk_a = PRIMITIVE_RISK_SCORE.get(PRIMITIVE_RISK.get(prim_a, "low"), 0.5)
        risk_b = PRIMITIVE_RISK_SCORE.get(PRIMITIVE_RISK.get(prim_b, "low"), 0.5)
        mult = risk_a * risk_b / 5.0
        trap = mult >= 3.0
        return (mult, trap,
                f"Default tensor: {prim_a.value} ⊗ {prim_b.value} = {mult:.1f}x")

    @classmethod
    def analyze_edit_set(cls, edits: List[Tuple[str, str]]) -> ChimeraReport:
        """Analyze a set of edits for tensor risk.

        Args:
            edits: List of (orig_aa, target_aa) pairs.
        """
        cls._init_tensor_table()
        primitives_changed = []
        individual_risks = []
        for orig_aa, target_aa in edits:
            delta = get_primitive_delta(orig_aa, target_aa)
            primitives_changed.append((delta["orig_primitive"],
                                       delta["target_primitive"]))
            individual_risks.append(delta["risk_class"])

        max_tensor_mult = 1.0
        is_trap = False
        trap_desc = "No trap state detected."
        worst_pair = ""

        for i in range(len(primitives_changed)):
            for j in range(i + 1, len(primitives_changed)):
                p_orig_i, p_targ_i = primitives_changed[i]
                p_orig_j, p_targ_j = primitives_changed[j]
                mult, trap, desc = cls.tensor_product(p_targ_i, p_targ_j)
                if mult > max_tensor_mult:
                    max_tensor_mult = mult
                    is_trap = trap
                    trap_desc = desc
                    worst_pair = f"{p_targ_i}⊗{p_targ_j}"

        if max_tensor_mult >= 3.0:
            tensor_class = "CRITICAL — trap state"
        elif max_tensor_mult >= 2.0:
            tensor_class = "HIGH — significant tensor amplification"
        elif max_tensor_mult >= 1.5:
            tensor_class = "MODERATE — elevated risk"
        else:
            tensor_class = "LOW — near-additive"

        recommendation = ("SAFE — proceed with standard protocol."
                          if not is_trap else
                          f"⚠ DANGER: Trap state detected ({worst_pair}). "
                          f"Do NOT apply both edits simultaneously.")

        return ChimeraReport(
            edits=[f"{o}→{t}" for o, t in edits],
            individual_risks=individual_risks,
            tensor_risk=max_tensor_mult,
            tensor_class=tensor_class,
            is_trap_state=is_trap,
            trap_description=trap_desc,
            recommendation=recommendation,
        )
