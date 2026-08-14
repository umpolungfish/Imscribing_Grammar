"""
primitives.py — Amino Acid → IG Primitive Mapping with Risk Classification.

13 promoted entries (12 amino acids + Stop) each activate exactly one IG primitive.
8 ground-layer (exact-box) amino acids activate no primitive.

REVISED MAPPING (2026-06-03 v0.6.0):
  His→⊙ (Criticality) — imidazole pKa≈6 is the only sidechain pKa near physiological pH,
    making His the natural carrier of criticality (protonation equilibrium = pH sensing gate).
    Histidine is the Swiss Army knife of protein function: catalytic triads, metal binding,
    pH-dependent conformational switching. Its criticality is biochemical, not metabolic.

  Gln→∈ (Grammar) — glutamine's long amide side chain enables extended hydrogen bonding
    networks that structure interaction patterns (grammar of H-bond recognition). Maps to
    Granularity/Scope because Gln's length positions H-bond donors at structural range.

  Rationale: The original mapping (His→∈, Gln→⊙) was structurally correct at the metabolic
    level (Gln synthetase is the most regulated biosynthetic node) but biochemically incorrect
    at the protein function level. His IS the critical residue — its imidazole ring titrates
    at the crossover between acid and base catalysis (protonated/deprotonated equilibrium),
    which is the definition of ⊙ criticality in the protein context.

  Previous mapping (preserved for reference):
    His→∈ (Grammar), Gln→⊙ (Criticality) — original assignment

Promoted AAs (split stratum):
  Met→⊢ (Scope),     Trp→⊣ (Topology),     Cys→> (Reversibility),
  Tyr→< (Parity),    Phe→⋈ (Force),        Ile→⊤ (Kinetics),
  His→⊙ (Criticality), Asn→∋ (Interaction), Gln→∈ (Grammar/Scope),
  Asp→⊥ (Chirality), Lys→Σ (Entropy),     Glu→◻ (Winding)

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
    SCOPE         = "⊢"     # Met — translation scope (start codon)
    TOPOLOGY      = "⊣"     # Trp — indole ceiling (topological complexity)
    REVERSIBILITY = "≻"     # Cys — disulfide bonds (reversible crosslinks)
    PARITY        = "≺"     # Tyr — phosphorylation switch (parity toggle)
    FORCE         = "⋈"     # Phe — maximum hydrophobicity (force ceiling)
    KINETICS      = "⊤"     # Ile — β-branching (ribosomal coupling)
    GRAMMAR       = "∈"     # Gln — long amide H-bond network (interaction grammar)
    INTERACTION   = "∋"     # Asn — N-glycosylation sequon (recognition gate)
    CRITICALITY   = "⊙"     # His — imidazole pKa≈6 (pH-critical protonation gate)
    CHIRALITY     = "⊥"     # Asp — chiral substrate selectivity
    ENTROPY       = "⊞"     # Lys — highest variability + acetylation target
    WINDING       = "◻"     # Glu — α-helix propensity / helix winding


# ── Amino acid → primitive map ─────────────────────────────────────

AA_PRIMITIVE_MAP: Dict[str, Optional[IGPrimitive]] = {
    # ── Promoted (split-stratum) amino acids ──
    "Met": IGPrimitive.SCOPE,
    "Trp": IGPrimitive.TOPOLOGY,
    "Cys": IGPrimitive.REVERSIBILITY,
    "Tyr": IGPrimitive.PARITY,
    "Phe": IGPrimitive.FORCE,
    "Ile": IGPrimitive.KINETICS,
    "His": IGPrimitive.CRITICALITY,    # REVISED: His→⊙ (criticality)
    "Asn": IGPrimitive.INTERACTION,
    "Gln": IGPrimitive.GRAMMAR,        # REVISED: Gln→∈ (grammar)
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
    IGPrimitive.CHIRALITY:      "critical",     # ⊥ — chiral specificity lost
    IGPrimitive.SCOPE:          "critical",     # ⊢ — translation scope destroyed
    IGPrimitive.WINDING:        "critical",     # ◻ — C-terminal boundary removed
    IGPrimitive.REVERSIBILITY:  "high",         # > — disulfide partner needed
    IGPrimitive.CRITICALITY:    "high",         # ⊙ — pH-critical catalysis gate
    IGPrimitive.TOPOLOGY:       "moderate",     # ⊣ — indole collapse tolerable
    IGPrimitive.PARITY:         "moderate",     # < — phosphorylation site loss
    IGPrimitive.KINETICS:       "moderate",     # ⊤ — β-branching preservation
    IGPrimitive.GRAMMAR:        "moderate",     # ∈ — H-bond grammar redesign
    IGPrimitive.INTERACTION:    "moderate",     # ∋ — glycosylation loss pathological
    IGPrimitive.ENTROPY:        "low",          # Σ — Lys↔Arg conserved
    IGPrimitive.FORCE:          "low",          # ⋈ — hydrophobic class preserved
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

def get_mapping_version() -> str:
    """Return the current mapping version with revision notes."""
    return ("v0.6.0: His→⊙ (Criticality), Gln→∈ (Grammar). "
            "His imidazole pKa≈6 is the natural carrier of protein criticality; "
            "Gln H-bond networks structure interaction grammar.")

def get_aa_primitive_description(aa: str) -> str:
    """Return a description of what primitive an amino acid activates."""
    descriptions = {
        "His": "⊙ (Criticality) — imidazole pKa≈6, pH-gated protonation equilibrium",
        "Gln": "∈ (Grammar) — long amide side chain H-bond network structuring",
        "Met": "⊢ (Scope) — translation initiation, start codon",
        "Trp": "⊣ (Topology) — largest indole ring system, structural complexity ceiling",
        "Cys": "> (Reversibility) — disulfide bond, only reversible covalent crosslink",
        "Tyr": "< (Parity) — phosphorylation switch, aromatic OH toggle",
        "Phe": "⋈ (Force) — maximally hydrophobic aromatic, no heteroatoms",
        "Ile": "⊤ (Kinetics) — β-branched, tightest ribosomal coupling",
        "Asn": "∋ (Interaction) — N-glycosylation sequon, extracellular recognition",
        "Asp": "⊥ (Chirality) — chiral selectivity in active site catalysis",
        "Lys": "Σ (Entropy) — most variable charged residue, acetylation target",
        "Glu": "◻ (Winding) — highest helix propensity, helix dipole stabilizer",
    }
    return descriptions.get(aa, "Ground-layer AA: no primitive activation")

def get_primitive_aa(prim: IGPrimitive) -> List[str]:
    """Return amino acid(s) that activate a given primitive."""
    return PRIMITIVE_TO_AAS.get(prim, [])
