"""
prime.py — Prime Editing Optimization via the Frobenius Template Rule.

The Frobenius template rule: prime editing succeeds when μ∘δ=id for
the edited locus. Three conditions:
  1. Stratum preservation
  2. Primitive invariance
  3. Ω boundary respect

Optimization criteria beyond sequence homology:
  - Frobenius stratum checking
  - B₄ lattice distance minimization
  - Primitive load matching
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

from genetic_engine.codon import CODON_TABLE, CODON_BY_SYMBOL, FrobeniusStratum
from genetic_engine.primitives import AA_PRIMITIVE_MAP, get_primitive_delta
from genetic_engine.editor import B4EditAnalyzer
from genetic_engine.stratum import FrobeniusStratumClassifier


@dataclass
class PrimeEditDesign:
    """A Frobenius-optimized prime editing design.

    Attributes:
        target_codon:        Original codon
        edit_codon:          Desired edited codon
        rt_template:         Reverse transcriptase template
        pbs:                 Primer binding site
        stratum_preserved:   Frobenius stratum unchanged?
        primitive_invariant: IG primitive class preserved?
        b4_lattice_cost:     Total B₄ lattice distance
        frobenius_conditions: Which conditions pass
        design_score:        Overall Frobenius quality (0-1)
        notes:               Design rationale
    """
    target_codon: str
    edit_codon: str
    rt_template: str
    pbs: str
    stratum_preserved: bool
    primitive_invariant: bool
    b4_lattice_cost: int
    frobenius_conditions: Dict[str, bool]
    design_score: float
    notes: str


class PrimeEditOptimizer:
    """Optimizes prime editing (pegRNA) using the Frobenius template rule."""

    @staticmethod
    def optimize(target_codon: str, edit_codon: str,
                 upstream_context: str = "",
                 downstream_context: str = "") -> PrimeEditDesign:
        """Design a Frobenius-optimal prime editing protocol."""
        c_orig = CODON_BY_SYMBOL.get(target_codon)
        c_edit = CODON_BY_SYMBOL.get(edit_codon)
        if c_orig is None or c_edit is None:
            raise ValueError(f"Unknown codon: {target_codon} or {edit_codon}")

        orig_aa = CODON_TABLE.get(target_codon, "X")
        edit_aa = CODON_TABLE.get(edit_codon, "X")

        # Condition 1: Stratum preservation
        stratum_preserved = c_orig.stratum == c_edit.stratum

        # Condition 2: Primitive invariance
        orig_prim = AA_PRIMITIVE_MAP.get(orig_aa, None)
        edit_prim = AA_PRIMITIVE_MAP.get(edit_aa, None)
        primitive_invariant = (orig_prim == edit_prim)

        # Condition 3: Ω boundary respect
        if c_orig.is_stop:
            omega_respected = c_edit.is_stop or (edit_aa == "Sel")
        else:
            omega_respected = not c_edit.is_stop

        # B₄ lattice cost
        cost_report = B4EditAnalyzer.analyze(target_codon, edit_codon)
        b4_cost = cost_report.total_cost

        # RT template design
        rt_template = edit_codon
        pbs = target_codon
        if stratum_preserved and c_edit.stratum == FrobeniusStratum.EXACT:
            rt_template = edit_codon[:2] + "N"
        if upstream_context:
            rt_template = upstream_context[-1:] + rt_template
        if not stratum_preserved:
            if upstream_context:
                rt_template = upstream_context[-2:] + rt_template
            if downstream_context:
                rt_template = rt_template + downstream_context[:2]

        # Frobenius conditions
        frobenius_conditions = {
            "stratum_preservation": stratum_preserved,
            "primitive_invariance": primitive_invariant,
            "omega_boundary_respect": omega_respected,
        }
        conditions_passed = sum(1 for v in frobenius_conditions.values() if v)

        # Design score
        base_score = conditions_passed / 3.0
        b4_penalty = min(b4_cost / 6.0, 1.0) * 0.3
        bonus = 0.1 if (cost_report.silent and stratum_preserved) else 0.0
        design_score = max(0.0, min(1.0, base_score - b4_penalty + bonus))

        # Notes
        notes_parts = []
        if stratum_preserved:
            notes_parts.append(f"✓ Stratum preserved ({c_orig.stratum.value} → {c_edit.stratum.value})")
        else:
            notes_parts.append(f"✗ Stratum CROSSING ({c_orig.stratum.value} → {c_edit.stratum.value})")
            notes_parts.append(f"  Risk: {FrobeniusStratumClassifier.stratum_crossing_risk(c_orig.stratum, c_edit.stratum)}")
        if primitive_invariant:
            notes_parts.append(f"✓ Primitive invariant ({orig_aa}→{edit_aa}, same class)")
        else:
            delta = get_primitive_delta(orig_aa, edit_aa)
            notes_parts.append(f"✗ Primitive CHANGE: {orig_prim} → {edit_prim} (risk: {delta['risk_class']})")
        if omega_respected:
            notes_parts.append("✓ Ω boundary respected")
        else:
            notes_parts.append("✗ Ω BOUNDARY VIOLATED")
        notes_parts.append(f"B₄ lattice cost: {b4_cost}/6")
        notes_parts.append(f"Frobenius design score: {design_score:.3f}")

        return PrimeEditDesign(
            target_codon=target_codon, edit_codon=edit_codon,
            rt_template=rt_template, pbs=pbs,
            stratum_preserved=stratum_preserved,
            primitive_invariant=primitive_invariant,
            b4_lattice_cost=b4_cost,
            frobenius_conditions=frobenius_conditions,
            design_score=design_score,
            notes="\n  ".join(notes_parts),
        )
