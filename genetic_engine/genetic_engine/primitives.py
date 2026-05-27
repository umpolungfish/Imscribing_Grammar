"""
primitives.py — Amino Acid → IG Primitive Mapping with Risk Classification.

12 promoted amino acids each activate exactly one IG primitive.
8 ground-layer (exact-box) amino acids activate no primitive.

Promoted AAs (split stratum):
  Met→Ð (Scope),   Trp→Þ (Topology), Cys→Ř (Reversibility),
  Tyr→Φ (Parity),  Phe→ƒ (Force),     Ile→Ç (Kinetics),
  His→Γ (Grammar), Asn→ɢ (Interaction), Gln→φ̂ (Criticality),
  Asp→Ħ (Chirality), Lys→Σ (Entropy), Glu→Ω (Winding)

Ground AAs (exact stratum): Leu, Pro, Arg, Thr, Ala, Ser, Val, Gly
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class IGPrimitive(Enum):
    """The 12 IG primitives as activated by promoted amino acids.

    Each promoted AA activates exactly one primitive that ground-layer
    (exact-box) AAs do not activate.
    """
    SCOPE         = "Ð"     # Met — translation scope (start codon)
    TOPOLOGY      = "Þ"     # Trp — indole ceiling (topological complexity)
    REVERSIBILITY = "Ř"     # Cys — disulfide bonds (reversible crosslinks)
    PARITY        = "Φ"     # Tyr — phosphorylation switch (parity toggle)
    FORCE         = "ƒ"     # Phe — maximum hydrophobicity (force ceiling)
    KINETICS      = "Ç"     # Ile — β-branching (ribosomal coupling)
    GRAMMAR       = "Γ"     # His — imidazole pKa bridge (pH-gated catalysis)
    INTERACTION   = "ɢ"     # Asn — N-glycosylation sequon (recognition gate)
    CRITICALITY   = "φ̂"    # Gln — most regulated biosynthetic node
    CHIRALITY     = "Ħ"     # Asp — chiral substrate selectivity
    ENTROPY       = "Σ"     # Lys — highest variability + acetylation target
    WINDING       = "Ω"     # Glu — α-helix propensity / helix winding


# ── Amino acid → primitive map ─────────────────────────────────────

AA_PRIMITIVE_MAP: Dict[str, Optional[IGPrimitive]] = {
    # ── Promoted (split-stratum) amino acids ──
    "Met": IGPrimitive.SCOPE,
    "Trp": IGPrimitive.TOPOLOGY,
    "Cys": IGPrimitive.REVERSIBILITY,
    "Tyr": IGPrimitive.PARITY,
    "Phe": IGPrimitive.FORCE,
    "Ile": IGPrimitive.KINETICS,
    "His": IGPrimitive.GRAMMAR,
    "Asn": IGPrimitive.INTERACTION,
    "Gln": IGPrimitive.CRITICALITY,
    "Asp": IGPrimitive.CHIRALITY,
    "Lys": IGPrimitive.ENTROPY,
    "Glu": IGPrimitive.WINDING,
    # ── Ground-layer (exact-box) amino acids ──
    "Leu": None, "Pro": None, "Arg": None, "Thr": None,
    "Ala": None, "Ser": None, "Val": None, "Gly": None,
    # ── Special ──
    "Stop": IGPrimitive.WINDING,
}

PRIMITIVE_TO_AAS: Dict[IGPrimitive, List[str]] = defaultdict(list)
for aa, prim in AA_PRIMITIVE_MAP.items():
    if prim is not None:
        PRIMITIVE_TO_AAS[prim].append(aa)

# ── Risk classification ──────────────────────────────────────────

PRIMITIVE_RISK: Dict[Optional[IGPrimitive], str] = {
    IGPrimitive.CHIRALITY:      "critical",     # Ħ — chiral specificity lost
    IGPrimitive.SCOPE:          "critical",     # Ð — translation scope destroyed
    IGPrimitive.WINDING:        "critical",     # Ω — C-terminal boundary removed
    IGPrimitive.REVERSIBILITY:  "high",         # Ř — disulfide partner needed
    IGPrimitive.CRITICALITY:    "high",         # φ̂ — metabolic critical point
    IGPrimitive.TOPOLOGY:       "moderate",     # Þ — indole collapse tolerable
    IGPrimitive.PARITY:         "moderate",     # Φ — phosphorylation site loss
    IGPrimitive.KINETICS:       "moderate",     # Ç — β-branching preservation
    IGPrimitive.GRAMMAR:        "moderate",     # Γ — pH-gated catalysis redesign
    IGPrimitive.INTERACTION:    "moderate",     # ɢ — glycosylation loss pathological
    IGPrimitive.ENTROPY:        "low",          # Σ — Lys↔Arg conserved
    IGPrimitive.FORCE:          "low",          # ƒ — hydrophobic class preserved
    None:                       "low",          # Ground layer — no primitive
}

PRIMITIVE_RISK_SCORE: Dict[str, float] = {
    "critical": 10.0,
    "high":      5.0,
    "moderate":  2.0,
    "low":       0.5,
}

# ── Functions ─────────────────────────────────────────────────────

def get_primitive_delta(orig_aa: str, target_aa: str) -> dict:
    """Compute the primitive delta between two amino acid changes.

    Returns dict with orig_primitive, target_primitive, changed, risk_class, risk_score.
    Tensor amplification applies when both primitives are active and differ.
    """
    orig_prim = AA_PRIMITIVE_MAP.get(orig_aa, None)
    target_prim = AA_PRIMITIVE_MAP.get(target_aa, None)
    changed = orig_prim != target_prim

    risk_order = ["critical", "high", "moderate", "low"]
    orig_risk = PRIMITIVE_RISK.get(orig_prim, "low")
    target_risk = PRIMITIVE_RISK.get(target_prim, "low")
    orig_idx = risk_order.index(orig_risk)
    target_idx = risk_order.index(target_risk)

    if changed and orig_prim is not None and target_prim is not None:
        risk_class = risk_order[min(orig_idx, target_idx)]
        risk_score = PRIMITIVE_RISK_SCORE[risk_class] * 1.5
    else:
        risk_class = risk_order[min(orig_idx, target_idx)]
        risk_score = PRIMITIVE_RISK_SCORE[risk_class]

    return {
        "orig_primitive": orig_prim,
        "target_primitive": target_prim,
        "changed": changed,
        "risk_class": risk_class,
        "risk_score": risk_score,
    }
