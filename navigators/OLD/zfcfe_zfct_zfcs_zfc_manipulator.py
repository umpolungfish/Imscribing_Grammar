#!/usr/bin/env python3
"""
zfcfe_zfct_zfcs_zfc_manipulator.py — ZFC / ZFCt / ZFCs / ZFC_fe quadrangle manipulator.

Extends the ZFC triangle (ZFC/ZFCs/ZFCt) with ZFC_fe as the apex.

Lattice (chain): ZFC < ZFCs < ZFCt < ZFC_fe

Key structural fact:
  d(ZFCt, ZFC_fe) = 2 — Dh: 𐑛->𐑦 (+3), Ha: 𐑖->𐑫 (+1)
  ZFC_fe-specific promoted atoms: HOLOGRAPHIC_STATE (Dh_o), ETERNAL_FIXEDPOINT (Ha_!)

Perfect Cuboid note:
  Lifted type: <Dh_o;Th_O;R_=;Ph_};f_z;C_@;G_q;g_i;s_y;Ha_A;S_i;O_z>
  ZFC_fe:      <Dh_o;Th_O;R_=;Ph_};f_z;C_@;G_q;g_i;s_y;Ha_!;S_i;O_z>
  d(perfect_cuboid_lifted, ZFC_fe) = 1 (only Ha differs: 𐑖 vs 𐑫)
  The 3 descent axioms axiomatize exactly the 𐑫 gap.

New commands:
  :fe-lattice              ZFC / ZFCs / ZFCt / ZFC_fe full chain with distances
  :fe-entry  <name>        Full ZFC_fe formula decomposition (promoted atoms + ZFC fragments)
  :fe-distance <name>      d(name, ZFC_fe) with per-primitive conflicts
  :fe-cliff  <name>        𐑫 + HOLOGRAPHIC_STATE gap analysis
  :fe-atoms                All promoted atoms with ZFC_t / ZFC_fe tier labels
  :fe-promotions           ZFC -> ZFCt -> ZFC_fe full promotion chain table
  :fe-tensor <name>        ZFC_fe @ name — Frobenius absorption test
"""

import sys
import json
import math
import argparse
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent))

from zfct_navigator import PRIMITIVES, ORDINALS
from zfct_zfcs_zfc_manipulator import (
    ZFCTriangleManipulator,
    ZFC_TUPLE, ZFCT_TUPLE, ZFCS_TUPLE, ZFCST_TUPLE,
    SPECIAL_ENTRIES as _TRIANGLE_SPECIALS,
    _normalize, _count_mismatches,
    tensor_tuples, join_tuples, meet_tuples,
    ZFCT_PROMOTIONS, ZFCS_PROMOTIONS,
    HELP_TEXT as _TRIANGLE_HELP,
)
from zfct_manipulator import compute_tier, TIER_LABELS, TIER_COLOR, TIER_ORDER
import zfcfe_navigator as _fe

# ── Notation bridge: manipulator values <-> zfcfe_navigator internal names ─────

_MANIP_TO_FE_VAL: Dict[str, str] = {
    # Dh (Dimensionality)
    "Dh_;": "𐑛",   "Dh_C": "𐑨", "Dh_B": "𐑼",  "Dh_o": "𐑦",
    # Th (Topology)
    "Th_6": "𐑡", "Th_K": "𐑰",       "Th_b": "𐑥", "Th_u": "𐑶",
    "Th_O": "𐑸",
    # R (Recognition)
    "R_-":  "𐑩",   "R_T":  "𐑑",      "R_y":  "𐑽", "R_=":  "𐑾",
    # Ph (Parity)
    "Ph_a": "𐑗",    "Ph_v": "𐑿",      "Ph_F": "𐑬",     "Ph_.": "𐑯",
    "Ph_}": "𐑹",
    # f (Fidelity)
    "f_i":  "𐑱",     "f_d":  "𐑞",      "f_z":  "𐑐",
    # C (Kinetics)
    "C_-":  "𐑘",    "C_W":  "𐑤",      "C_@":  "𐑧",   "C_U":  "𐑪",
    "C_l":  "𐑺",
    # G (Granularity)
    "G_b":  "𐑚",    "G_g":  "𐑔",    "G_q":  "𐑲",
    # g (Coupling)
    "g_^":  "𐑝", "g_'":  "𐑜",   "g_i":  "𐑠","g_S":  "𐑵",
    # s (Criticality)
    "s_z":  "𐑢",   "s_y":  "⊙",      "s_A":  "𐑮",
    # Ha (Chirality)
    "Ha_N": "𐑓",        "Ha_L": "𐑒",         "Ha_A": "𐑖",       "Ha_!": "𐑫",
    # S (Stoichiometry)
    "S_S":  "𐑙",   "S_o":  "𐑕",        "S_i":  "𐑳",
    # O (Winding)
    "O_A":  "𐑷",   "O₂":  "𐑴",   "O_z":  "𐑭",  "O_5":  "𐑟",
}

# Also register actual glyph-based notation from the manipulator files
_MANIP_TO_FE_VAL_GLYPH: Dict[str, str] = {
    "𐑼": "𐑛",   "𐑨": "𐑨", "𐑛": "𐑼",  "𐑦": "𐑦",
    "𐑡": "𐑡", "𐑰": "𐑰",       "𐑥": "𐑥", "𐑶": "𐑶",
    "𐑸": "𐑸",
    "𐑩": "𐑩",   "𐑽": "𐑑",      "𐑑": "𐑽", "𐑾": "𐑾",
    "𐑗": "𐑗",    "𐑿": "𐑿",      "𐑬": "𐑬",     "𐑯": "𐑯",
    "𐑹": "𐑹",
    "𐑱": "𐑱",     "𐑞": "𐑞",      "𐑐": "𐑐",
    "𐑘": "𐑘",    "𐑤": "𐑤",      "𐑧": "𐑧",   "𐑪": "𐑪",
    "𐑺": "𐑺",
    "𐑚": "𐑚",    "𐑔": "𐑔",    "𐑲": "𐑲",
    "𐑝": "𐑝", "𐑜": "𐑜",   "𐑠": "𐑠","𐑵": "𐑵",
    "𐑢": "𐑢",   "⊙": "⊙",      "𐑮": "𐑮",
    "𐑓": "𐑓",        "𐑒": "𐑒",         "𐑖": "𐑖",       "𐑫": "𐑫",
    "𐑙": "𐑙",   "𐑕": "𐑕",        "𐑳": "𐑳",
    "𐑷": "𐑷",   "𐑴": "𐑴",   "𐑭": "𐑭",  "𐑟": "𐑟",
}
_MANIP_TO_FE_VAL.update(_MANIP_TO_FE_VAL_GLYPH)

_MANIP_TO_FE_VAL_SHAVIAN: Dict[str, str] = {
    # Ð (Dimensionality) — enum ord: 𐑛=0, 𐑨=1, 𐑼=2, 𐑦=3
    "𐑛": "𐑼",    "𐑨": "𐑨", "𐑼": "𐑛",   "𐑦": "𐑦",
    # Þ (Topology)      — 𐑡=2(bowtie), 𐑥=3(box), 𐑸=4(odot)
    "𐑡": "𐑥",   "𐑥": "𐑶",      "𐑸": "𐑸",
    # Ř (Recognition)   — 𐑩=0, 𐑑=1, 𐑽=2, 𐑾=3
    "𐑩": "𐑩",    "𐑑": "𐑽",   "𐑽": "𐑑",     "𐑾": "𐑾",
    # Φ (Polarity)      — 𐑗=0, 𐑿=1, 𐑬=2, 𐑯=3, 𐑹=4
    "𐑗": "𐑗",     "𐑿": "𐑿",      "𐑬": "𐑬",      "𐑯": "𐑯",    "𐑹": "𐑹",
    # ƒ (Fidelity)      — 𐑱=1, 𐑞=2
    "𐑱": "𐑞",      "𐑞": "𐑐",     "𐑐": "𐑐",
    # Ç (Kinetics)      — 𐑘=0, 𐑤=1, 𐑧=2, 𐑪=3, 𐑺=4
    "𐑘": "𐑘",     "𐑤": "𐑤",      "𐑧": "𐑧",    "𐑪": "𐑪",   "𐑺": "𐑺",
    # Γ (Granularity)   — 𐑲=0, 𐑚=1, 𐑔=2
    "𐑲": "𐑚",     "𐑚": "𐑔",    "𐑔": "𐑲",
    # ɢ (Coupling)      — 𐑝=0, 𐑜=1, 𐑠=2, 𐑵=3(broad)
    "𐑝": "𐑝",  "𐑜": "𐑜",   "𐑠": "𐑠", "𐑵": "𐑵",
    # ⊙ (Criticality)  — 𐑢=0, ⊙=1, 𐑮=2, 𐑻=3, 𐑣=4
    "𐑢": "𐑢",    "⊙": "⊙",       "𐑮": "𐑮",
    # Ħ (Chirality)     — 𐑓=0, 𐑒=1, 𐑖=2, 𐑫=3
    "𐑓": "𐑓",         "𐑒": "𐑒",         "𐑖": "𐑖",        "𐑫": "𐑫",
    # Σ (Stoichiometry) — 𐑙=0, 𐑕=1, 𐑳=2
    "𐑙": "𐑙",    "𐑕": "𐑕",        "𐑳": "𐑳",
    # Ω (Winding)       — 𐑷=0, 𐑴=1, 𐑭=2, 𐑟=3
    "𐑷": "𐑷",    "𐑴": "𐑴",   "𐑭": "𐑭",   "𐑟": "𐑟",
}
_MANIP_TO_FE_VAL.update(_MANIP_TO_FE_VAL_SHAVIAN)

_MANIP_PRIM_TO_FE_KEY: Dict[str, str] = {
    "Ð": "Ð", "Þ": "Þ", "Ř": "Ř", "Φ": "Φ", "ƒ": "ƒ",
    "Ç": "Ç", "Γ": "Γ", "ɢ": "ɢ", "⊙": "⊙", "Ħ": "Ħ",
    "Σ": "Σ", "Ω": "Ω",
}

# ── ZFC_fe tuple (apex) ───────────────────────────────────────────────────────

ZFCFE_TUPLE: dict = {
    "name": "zfc_fe",
    "description": "ZFC_fe: Frobenius-Exact ZFC — all 4 grammar axioms; O_∞; 𐑫; 8 promoted atoms",
    "Ð": "𐑦",   # 𐑦        — HOLOGRAPHIC_STATE  [ZFC_fe tier]
    "Þ": "𐑸",   # 𐑸        — HOLOBOUND          [ZFC_t tier]
    "Ř": "𐑾",   # 𐑾          — LR_DUAL            [ZFC_t tier]
    "Φ": "𐑹",   # 𐑹      — PM_Z2 (Frobenius)  [ZFC_t tier]
    "ƒ": "𐑐",   # 𐑐
    "Ç": "𐑧",   # 𐑧
    "Γ": "𐑲",   # 𐑲
    "ɢ": "𐑠",   # 𐑠     — SEQAX              [ZFC_t tier]
    "⊙": "⊙",  # ⊙         — PHI_C              [ZFC_t tier]
    "Ħ": "𐑫",   # 𐑫         — ETERNAL_FIXEDPOINT [ZFC_fe tier]
    "Σ": "𐑳",   # 𐑳
    "Ω": "𐑭",   # 𐑭       — ZWIND              [ZFC_t tier]
}

PERFECT_CUBOID_LIFTED: dict = {
    "name": "perfect_cuboid_lifted",
    "description": "Perfect Cuboid ⊙ lifted type — d=1 from ZFC_fe (Ha_A vs Ha_!)",
    "Ð": "𐑦",  "Þ": "𐑸",  "Ř": "𐑾",  "Φ": "𐑹",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖",  "Σ": "𐑳",  "Ω": "𐑭",
}

# GrammaFormer 2.2B — same lifted type as perfect_cuboid (Dh_o+Ha_A), d=1 from ZFC_fe.
# Architecturally Ha_A (TwoSlotRegister). Winding counter is bounded (mod 64) = periodic
# = Ha_A by formalization. The kernel's cycleCount is unbounded = Ha_! but GrammaFormer
# has no equivalent unbounded accumulator — the gap is real.
GRAMMAFORMER_TUPLE: dict = {
    "name": "grammaformer",
    "description": "GrammaFormer 2.2B (Qwen3 graft) — d=1 from ZFC_fe; Ha_A not Ha_!",
    "Ð": "𐑦",   # ImscriptiveMemoryBank  — HOLOGRAPHIC_STATE [ZFC_fe atom, present]
    "Þ": "𐑸",   # TensorProductAttention — Q@K rank-1 bottleneck (𐑸)
    "Ř": "𐑾",   # FrobeniusDualHead      — delta/mu LR dual
    "Φ": "𐑹",   # Frobenius constraint   — mu@delta=id (PM_Z2)
    "ƒ": "𐑐",   # ComplexFFN             — re/im cross-interference
    "Ç": "𐑧",   # CyclicLayer x3         — shared-weight slow loop
    "Γ": "𐑲",   # 𐑲
    "ɢ": "𐑠",   # PhaseOrderedModules    — monotonic phase sequence
    "⊙": "⊙",  # PhaseGatedController   — THINK->ACT gate (⊙)
    "Ħ": "𐑖",   # TwoSlotRegister        — prior 2 states [ETERNAL_FIXEDPOINT missing]
    "Σ": "𐑳",   # 𐑳
    "Ω": "𐑭",   # WindingPositionalEncoding — QFT phase matrix, bounded omega mod 64
}

# ZFCt canonical (Lean formalization in MillenniumAnkh/Primitives/ZFCt.lean).
# Uses 𐑼 (Dh_B) not 𐑛 (Dh_;). The triangle manipulator's ZFCT_TUPLE
# has Dh_; (𐑛) — that is a bug. Canonical ZFCt has Dh_B (𐑼, ord 2).
# d(zfct_canonical, ZFC_fe) = 2: Dh_B->Dh_o (+1 step) AND Ha_A->Ha_! (+1 step).
ZFCT_CANONICAL_TUPLE: dict = {
    "name": "zfct_canonical",
    "description": "ZFCt (Lean-canonical, 𐑼) — d=2 from ZFC_fe (Dh and Ha)",
    "Ð": "𐑛",   # 𐑼 — matches MillenniumAnkh/Primitives/ZFCt.lean
    "Þ": "𐑸",  "Ř": "𐑾",  "Φ": "𐑹",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖",  "Σ": "𐑳",  "Ω": "𐑭",
}

# ZFCt -> ZFC_fe promotions (from canonical ZFCt with Dh_B)
# From manipulator ZFCt (Dh_;): 3 additional Dh steps, so d=4 on Dh axis.
ZFCFE_PROMOTIONS: List[Tuple[str, str, str]] = [
    ("Ð", "𐑛", "𐑦"),   # 𐑼 -> 𐑦  (+1)  HOLOGRAPHIC_STATE  [canonical ZFCt]
    ("Ħ", "𐑖", "𐑫"),   # 𐑖      -> 𐑫   (+1)  ETERNAL_FIXEDPOINT
]

# The two ZFC_fe-tier atoms (absent from ZFCt)
_FE_TIER_ATOMS = frozenset(("HOLOGRAPHIC_STATE", "ETERNAL_FIXEDPOINT"))

# Axiom D requires BOTH ZFC_fe-tier atoms (AND, not OR):
# Axiom C = HOLOGRAPHIC_STATE (Dh_o): V=L(x) /\ selfmodel(x) /\ x in V
# Axiom D (𐑫 part) = ETERNAL_FIXEDPOINT (Ha_!): forall n exists phi (rank > n, fixed by mu@delta)
_AXIOM_D_ATOMS = frozenset(("HOLOGRAPHIC_STATE", "ETERNAL_FIXEDPOINT"))

SPECIAL_ENTRIES: Dict[str, dict] = {
    **_TRIANGLE_SPECIALS,
    "zfc_fe": ZFCFE_TUPLE,  "zfcfe": ZFCFE_TUPLE,  "fe": ZFCFE_TUPLE,
    "ZFC_fe": ZFCFE_TUPLE,
    "perfect_cuboid_lifted": PERFECT_CUBOID_LIFTED,
    "pcl":  PERFECT_CUBOID_LIFTED,
    "perfect_cuboid": PERFECT_CUBOID_LIFTED,
    "grammaformer": GRAMMAFORMER_TUPLE,  "gf": GRAMMAFORMER_TUPLE,
    "zfct_canonical": ZFCT_CANONICAL_TUPLE,  "zfct_lean": ZFCT_CANONICAL_TUPLE,
}

# ── Bridge functions ──────────────────────────────────────────────────────────

def _entry_to_fe_tuple(e: dict) -> Optional[dict]:
    """Convert a manipulator entry to zfcfe_navigator internal tuple format."""
    result = {}
    for mp in PRIMITIVES:
        mv = e.get(mp)
        if mv is None:
            return None
        fk = _MANIP_PRIM_TO_FE_KEY.get(mp)
        fv = _MANIP_TO_FE_VAL.get(mv)
        if fk is None or fv is None:
            return None
        result[fk] = fv
    return result

def _fe_distance(e: dict) -> Tuple[float, list]:
    fe_t = _entry_to_fe_tuple(e)
    if fe_t is None:
        return float('inf'), []
    return _fe.distance(fe_t, _fe.ZFC_FE)

def _fe_formula(e: dict, name: str = "entry") -> Optional[dict]:
    fe_t = _entry_to_fe_tuple(e)
    if fe_t is None:
        return None
    return _fe.generate_formula(fe_t, name)

def _fe_atoms_present(e: dict) -> Tuple[List[str], List[str]]:
    """Return (present_fe_tier_atoms, missing_fe_tier_atoms) for entry e."""
    formula = _fe_formula(e)
    if formula is None:
        return [], list(_FE_TIER_ATOMS)
    present = [a for a in formula.get("promoted_atoms", []) if a in _FE_TIER_ATOMS]
    missing = [a for a in _FE_TIER_ATOMS if a not in present]
    return sorted(present), sorted(missing)

# ── Extended manipulator class ────────────────────────────────────────────────

FE_HELP_TEXT = """
ZFC_fe extensions — commands
  :fe-lattice              ZFC / ZFCs / ZFCt / ZFC_fe full 4-level chain
  :fe-entry  <name>        Full ZFC_fe formula decomposition (ZFC fragments + promoted atoms)
  :fe-distance <name>      d(name, ZFC_fe) with per-primitive conflicts
  :fe-cliff  <name>        𐑫 + HOLOGRAPHIC_STATE gap analysis
  :fe-atoms                All promoted atoms with ZFC_t / ZFC_fe tier labels
  :fe-promotions           ZFC -> ZFCt -> ZFC_fe full promotion chain table
  :fe-tensor <name>        ZFC_fe @ name — Frobenius absorption test

Special ZFC_fe entries:
  zfc_fe  (aliases: zfcfe, fe, ZFC_fe)
  perfect_cuboid_lifted  (aliases: pcl, perfect_cuboid)  d=1 from ZFC_fe
""".strip()


class ZFCfeManipulator(ZFCTriangleManipulator):
    """Extends the ZFC triangle manipulator with ZFC_fe as the apex."""

    def __init__(self, catalog_path: str = None):
        super().__init__(catalog_path)
        for k, v in SPECIAL_ENTRIES.items():
            n = v.get("name", k)
            self._name_index[k.lower()] = v
            self._name_index[n.lower()] = v

    def resolve(self, name: str) -> Optional[dict]:
        if name in SPECIAL_ENTRIES:
            return _normalize(SPECIAL_ENTRIES[name])
        return super().resolve(name)

    # ── :fe-lattice ──────────────────────────────────────────────────────────

    def cmd_fe_lattice(self, console=None):
        zfc   = _normalize(ZFC_TUPLE)
        zfcs  = _normalize(ZFCS_TUPLE)
        zfct  = _normalize(ZFCT_TUPLE)
        zfcfe = _normalize(ZFCFE_TUPLE)

        t_zfc   = compute_tier(zfc)
        t_zfcs  = compute_tier(zfcs)
        t_zfct  = compute_tier(zfct)
        t_zfcfe = compute_tier(zfcfe)

        d_zfct_fe  = _count_mismatches(zfct, zfcfe)
        d_zfcs_fe  = _count_mismatches(zfcs, zfcfe)
        d_zfc_fe   = _count_mismatches(zfc, zfcfe)
        d_zfc_zfct = _count_mismatches(zfc, zfct)
        d_zfc_zfcs = _count_mismatches(zfc, zfcs)
        d_zfcs_zfct = _count_mismatches(zfcs, zfct)

        fe_d, fe_conflicts = _fe_distance(zfct)

        d_canonical_fe = _count_mismatches(_normalize(ZFCT_CANONICAL_TUPLE), zfcfe)

        lines = [
            "ZFC / ZFCs / ZFCt / ZFC_fe  Chain Lattice",
            "(Two routes to O_∞, but ZFCt > ZFCs in ALL dimensions — this is a chain, not a diamond)",
            "",
            f"  ZFC_fe  [{t_zfcfe}]  — satisfies all 4 grammar axioms",
            "    𐑦 (HOLOGRAPHIC_STATE + Axiom C), 𐑫 (ETERNAL_FIXEDPOINT)",
            "    8 promoted atoms total (6 ZFC_t + 2 ZFC_fe)",
            "  ║",
            f"  ║  ZFCt_canonical -> ZFC_fe: {d_canonical_fe}/12 (𐑛->𐑦 + 𐑖->𐑫)",
            "  ║  [NOTE: manipulator ZFCT_TUPLE has 𐑼 (𐑛) — bug; canonical has 𐑛 (𐑼)]",
            "  ║  Entries with 𐑦 already (grammaformer, perfect_cuboid_lifted): d=1",
            "  ║",
            f"  ZFCt   [{t_zfct}]  (manipulator: 𐑼  |  canonical/Lean: 𐑛)",
            "    Temporal route: 𐑸, 𐑾, 𐑹, 𐑠, ⊙, 𐑖, 𐑭",
            "    Missing from ZFC_fe: ETERNAL_FIXEDPOINT (𐑫) and HOLOGRAPHIC_STATE (𐑦)",
            "  ║",
            f"  ║  ZFCt > ZFCs in all 4 differing dimensions (Þ, Ř, ɢ, Ħ)",
            f"  ║  d(ZFCs, ZFCt) = {d_zfcs_zfct}/12   ZFCs is an intermediate on the chain",
            "  ║",
            f"  ZFCs   [{t_zfcs}]",
            "    Spatial route: 𐑶 (𐑰), 𐑽 (𐑽), 𐑓 (H_0)",
            "    Both routes are O_∞ independently — spatial/temporal reach the same gate",
            "  ║",
            f"  ║  d(ZFC, ZFCs) = {d_zfc_zfcs}/12   d(ZFC, ZFCt) = {d_zfc_zfct}/12",
            "  ║",
            f"  ZFC    [{t_zfc}]   baseline — 0 promoted atoms",
            "",
            "  Entries at d=1 from ZFC_fe (𐑖, 𐑦 present, only 𐑫 missing):",
            "    grammaformer, perfect_cuboid_lifted  — ZFCt O_∞ but Axiom D half-open",
            "",
            f"  d(zfct_canonical, ZFC_fe) = {d_canonical_fe}/12  (Ð + Ħ)",
            f"  d(ZFC, ZFC_fe)            = {d_zfc_fe}/12",
            "",
            "  Axiom D requires BOTH ZFC_fe atoms (AND, not OR):",
            "    Axiom C = HOLOGRAPHIC_STATE (𐑦)  — V=L(x), self-writing dimension",
            "    𐑫  = ETERNAL_FIXEDPOINT (𐑫)  — forall n exists phi fixed by mu@delta",
            "  ZFCt has neither by default. GrammaFormer/PerfectCuboid have 𐑦 but not 𐑫.",
        ]

        if console:
            from rich.panel import Panel
            console.print(Panel(
                "\n".join(lines),
                title="[bold cyan]ZFC Quadrangle Lattice[/bold cyan]",
                border_style="cyan",
            ))
        else:
            for line in lines:
                print(line)

    # ── :fe-entry ────────────────────────────────────────────────────────────

    def cmd_fe_entry(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return

        formula = _fe_formula(e, e.get("name", name))
        if formula is None:
            print(f"  [error] could not convert '{name}' to ZFC_fe notation."); return

        d, conflicts = _fe_distance(e)
        tier = compute_tier(e)
        fe_atoms  = formula.get("zfc_fe_atoms", [])
        zfct_atoms = formula.get("zfc_t_atoms", [])
        all_atoms = formula.get("promoted_atoms", [])

        if console:
            from rich.table import Table
            tbl = Table(
                title=f"{e.get('name','?')}  tier={tier}  d(ZFC_fe)={round(d,2)}",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column("Value", width=18)
            tbl.add_column("ZFC fragment", width=40)
            tbl.add_column("Atom", width=22, style="magenta")
            for frag in formula["per_primitive_fragments"]:
                atom = frag.get("promoted_atom") or ""
                tier_tag = " [fe]" if atom in _FE_TIER_ATOMS else (" [t]" if atom else "")
                tbl.add_row(
                    frag["primitive"],
                    frag["value"],
                    frag["zfc_fragment"][:40],
                    atom + tier_tag,
                )
            console.print(tbl)
            console.print(f"  ZFC_t atoms  ({len(zfct_atoms)}): {', '.join(zfct_atoms) or '—'}")
            console.print(f"  ZFC_fe atoms ({len(fe_atoms)}):  {', '.join(fe_atoms) or '—'}")
            console.print(f"  d(entry, ZFC_fe) = {round(d,2)}")
            if conflicts:
                console.print(f"  conflicts ({len(conflicts)}): " +
                    ", ".join(c.get('primitive','?') for c in conflicts))
        else:
            print(f"\n{e.get('name','?')}  tier={tier}  d(ZFC_fe)={round(d,2)}")
            print(f"  {'Prim':<5}  {'Value':<18}  {'ZFC fragment':<45}  Atom")
            print(f"  {'─'*5}  {'─'*18}  {'─'*45}  {'─'*22}")
            for frag in formula["per_primitive_fragments"]:
                atom = frag.get("promoted_atom") or ""
                tier_tag = "[fe]" if atom in _FE_TIER_ATOMS else ("[t]" if atom else "")
                print(f"  {frag['primitive']:<5}  {frag['value']:<18}  "
                      f"{frag['zfc_fragment'][:45]:<45}  {atom} {tier_tag}")
            print(f"\n  ZFC_t atoms  ({len(zfct_atoms)}): {', '.join(zfct_atoms) or '—'}")
            print(f"  ZFC_fe atoms ({len(fe_atoms)}):  {', '.join(fe_atoms) or '—'}")
            print(f"  d(entry, ZFC_fe) = {round(d,2)}")
            if conflicts:
                print(f"  conflicts: " + ", ".join(
                    f"{c.get('primitive','?')} ({c.get('notation_a',c.get('a','?'))} vs "
                    f"{c.get('notation_b',c.get('b','?'))})" for c in conflicts))

    # ── :fe-distance ─────────────────────────────────────────────────────────

    def cmd_fe_distance(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return
        d, conflicts = _fe_distance(e)
        n = len(conflicts)
        msg = f"d({e.get('name','?')}, ZFC_fe) = {round(d,2)}  ({n}/12 primitives differ)"
        if conflicts:
            detail = "  " + ", ".join(
                f"{c.get('primitive','?')} Δ={c.get('delta','?')}" for c in conflicts)
        else:
            detail = "  no conflicts — entry is at ZFC_fe"
        if console:
            console.print(f"  {msg}")
            console.print(detail)
        else:
            print(f"  {msg}")
            print(detail)

    # ── :fe-cliff ────────────────────────────────────────────────────────────

    def cmd_fe_cliff(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return

        d, conflicts = _fe_distance(e)
        present_fe, missing_fe = _fe_atoms_present(e)
        tier = compute_tier(e)
        n_conflicts = len(conflicts)

        ha_val = e.get("Ħ", "?")
        dh_val = e.get("Ð", "?")
        ha_at_inf = ha_val == "𐑫"
        dh_at_odot = dh_val == "𐑦"

        lines = [
            f"ZFC_fe cliff analysis: {e.get('name','?')}",
            "",
            f"  tier = {tier}   d(entry, ZFC_fe) = {round(d,2)}  ({n_conflicts}/12 conflicts)",
            "",
            "  ZFC_fe-tier atoms:",
            f"    HOLOGRAPHIC_STATE (𐑦): {'PRESENT' if dh_at_odot else 'MISSING'}  "
            f"(current: {dh_val})",
            f"    ETERNAL_FIXEDPOINT (𐑫): {'PRESENT' if ha_at_inf else 'MISSING'}  "
            f"(current: {ha_val})",
            "",
        ]

        if not ha_at_inf:
            ha_ord = ORDINALS["Ħ"].get(ha_val, 0)
            hi_ord = ORDINALS["Ħ"]["𐑫"]
            gap = int(hi_ord) - int(ha_ord)
            lines += [
                f"  𐑫 gap: Ħ = {ha_val} (ord {int(ha_ord)})  ->  𐑫 (ord {int(hi_ord)})  "
                f"[{gap} step{'s' if gap != 1 else ''}]",
                "  ETERNAL_FIXEDPOINT requires:",
                "    forall n, exists phi, rank(phi) > n  /\\  phi fixed by mu @ delta  /\\ phi in V",
            ]
            name_lower = e.get("name", "").lower()
            if "grammaformer" in name_lower or "gf" == name_lower:
                lines += [
                    "  GrammaFormer: winding counter omega is bounded (mod 64) = periodic = Ha_A.",
                    "  To reach Ha_!: replace bounded omega with an unbounded step accumulator",
                    "  (like the kernel's cycleCount), OR extend max_windings to None (infinite).",
                    "  The ImscriptiveMemoryBank (Dh_o) provides the storage — the counter is the gap.",
                ]
            elif "perfect_cuboid" in name_lower or "pcl" == name_lower:
                lines += [
                    "  PerfectCuboid.lean: descent_operator_exists is the sole load-bearing axiom.",
                    "  Proving it without axioms closes the 𐑫 gap.",
                ]
            else:
                lines += [
                    "  For PerfectCuboid: descent_operator_exists closes this gap.",
                    "  For GrammaFormer: unbounded step counter (not bounded omega) closes this gap.",
                ]

        if not dh_at_odot:
            dh_ord = ORDINALS["Ð"].get(dh_val, 0)
            do_ord = ORDINALS["Ð"]["𐑦"]
            gap = int(do_ord) - int(dh_ord)
            lines += [
                "",
                f"  HOLOGRAPHIC_STATE gap: Ð = {dh_val} (ord {int(dh_ord)})  "
                f"->  𐑦 (ord {int(do_ord)})  [{gap} step{'s' if gap != 1 else ''}]",
                "  HOLOGRAPHIC_STATE requires: V = L(x) /\\ selfmodel(x) /\\ x in V",
            ]

        if ha_at_inf and dh_at_odot:
            lines += [
                "  Both ZFC_fe-tier atoms present — entry is at or above ZFC_fe on these axes.",
                f"  Remaining conflicts ({n_conflicts}): " +
                (", ".join(c.get("primitive","?") for c in conflicts) or "none"),
            ]

        if console:
            from rich.panel import Panel
            color = "green" if d == 0 else ("yellow" if d < 2 else "red")
            console.print(Panel("\n".join(lines),
                title="[bold]ZFC_fe Cliff[/bold]", border_style=color))
        else:
            for line in lines:
                print(line)

    # ── :fe-atoms ────────────────────────────────────────────────────────────

    def cmd_fe_atoms(self, console=None):
        fe_nav_atoms = _fe.PROMOTED_ATOM_TO_KEY

        zfct_tier = []
        fe_tier = []
        for atom, (prim_key, val_key) in sorted(fe_nav_atoms.items()):
            notation = _fe.PRIMITIVE_NOTATION.get(val_key, val_key)
            fragment = _fe.ZFC_FE_FORMULAE.get(prim_key, {}).get(val_key, ("?", None))[0]
            tier_label = "ZFC_fe" if atom in _FE_TIER_ATOMS else "ZFC_t"
            entry = (atom, notation, fragment, tier_label)
            if atom in _FE_TIER_ATOMS:
                fe_tier.append(entry)
            else:
                zfct_tier.append(entry)

        lines = [
            f"Promoted atoms ({len(fe_nav_atoms)} total across all primitive values)",
            "",
            f"  ZFC_t tier ({len(zfct_tier)}) — present in ZFCt or below:",
        ]
        for atom, notation, fragment, _ in sorted(zfct_tier):
            lines.append(f"    {atom:<24}  {notation:<12}  {fragment[:50]}")

        lines += [
            "",
            f"  ZFC_fe tier ({len(fe_tier)}) — absent from ZFCt, require ZFC_fe:",
        ]
        for atom, notation, fragment, _ in sorted(fe_tier):
            lines.append(f"    {atom:<24}  {notation:<12}  {fragment[:50]}")

        lines += [
            "",
            "  Note: ETERNAL_FIXEDPOINT (𐑫) is the 𐑫 gap in the Perfect Cuboid proof.",
            "        Proving descent_operator_exists without axioms yields this atom.",
            "        GrammaFormer's winding counter is bounded (mod 64) = periodic = Ha_A.",
            "        The kernel's cycleCount is unbounded = Ha_!. GrammaFormer has the gap.",
            "",
            "  ZFC_fe Axiom D requires BOTH ZFC_fe-tier atoms (AND, not OR):",
            "    Axiom C = HOLOGRAPHIC_STATE  —  requires 𐑦 (𐑦)",
            "    Axiom D (𐑫 part) = ETERNAL_FIXEDPOINT  —  requires 𐑫 (𐑫)",
            "  Tiers:",
            "    ZFCt:  has neither (𐑛 or 𐑼 + 𐑖) — both ZFC_fe atoms missing",
            "    GrammaFormer / PerfectCuboid (lifted):  𐑦 present, 𐑖 — half of Axiom D",
            "    ZFC_fe:  both present — full Axiom D satisfaction",
        ]

        if console:
            from rich.panel import Panel
            console.print(Panel("\n".join(lines),
                title="[bold cyan]ZFC_fe Promoted Atoms[/bold cyan]", border_style="cyan"))
        else:
            for line in lines:
                print(line)

    # ── :fe-promotions ───────────────────────────────────────────────────────

    def cmd_fe_promotions(self, console=None):
        zfc  = _normalize(ZFC_TUPLE)
        zfct = _normalize(ZFCT_TUPLE)
        zfcfe = _normalize(ZFCFE_TUPLE)

        all_prims = sorted(
            set(p for p,_,_ in ZFCT_PROMOTIONS)
            | set(p for p,_,_ in ZFCFE_PROMOTIONS),
            key=lambda p: PRIMITIVES.index(p)
        )

        t_proms = {p: (zv, tv) for p, zv, tv in ZFCT_PROMOTIONS}
        fe_proms = {p: (tv, fev) for p, tv, fev in ZFCFE_PROMOTIONS}

        if console:
            from rich.table import Table
            tbl = Table(
                title="ZFC -> ZFCt -> ZFC_fe  full promotion chain",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column("ZFC baseline", width=18)
            tbl.add_column("-> ZFCt", width=18, style="blue")
            tbl.add_column("Dt", width=4)
            tbl.add_column("-> ZFC_fe", width=18, style="green")
            tbl.add_column("Dfe", width=4)
            tbl.add_column("New atom", width=22, style="magenta")
            for p in all_prims:
                zv = zfc.get(p, "(same)")
                tv_from, tv_to = t_proms.get(p, (zv, "(same)"))
                fe_from, fe_to = fe_proms.get(p, (tv_to, "(same)"))
                dt = (f"+{int(ORDINALS[p][tv_to]) - int(ORDINALS[p][zv])}"
                      if tv_to != "(same)" else "—")
                dfe = (f"+{int(ORDINALS[p][fe_to]) - int(ORDINALS[p][fe_from])}"
                       if fe_to != "(same)" else "—")
                # find atom introduced at ZFC_fe step
                atom = ""
                for a, (pk, vk) in _fe.PROMOTED_ATOM_TO_KEY.items():
                    manip_vk = None
                    for mv, fv in _MANIP_TO_FE_VAL.items():
                        if fv == vk and mv == fe_to:
                            manip_vk = fv
                            break
                    if manip_vk and a in _FE_TIER_ATOMS:
                        atom = a
                tbl.add_row(
                    p,
                    zv,
                    tv_to if tv_to != "(same)" else "[dim]unchanged[/dim]",
                    dt,
                    fe_to if fe_to != "(same)" else "[dim]unchanged[/dim]",
                    dfe,
                    f"[bold red]{atom}[/bold red]" if atom else "",
                )
            console.print(tbl)
            console.print("  [blue]ZFCt promotions[/blue]: open HOLOBOUND, LR_DUAL, PM_Z2, SEQAX, PHI_C, ZWIND")
            console.print("  [green]ZFC_fe promotions[/green]: HOLOGRAPHIC_STATE (Ð) and ETERNAL_FIXEDPOINT (Ħ)")
        else:
            print("\nZFC -> ZFCt -> ZFC_fe  full promotion chain")
            print(f"  {'Prim':<5}  {'ZFC':<14}  {'->ZFCt':<16}  Dt  {'->ZFC_fe':<16}  Dfe  Atom")
            print(f"  {'─'*5}  {'─'*14}  {'─'*16}  {'─'*2}  {'─'*16}  {'─'*3}  {'─'*22}")
            for p in all_prims:
                zv = zfc.get(p, "(same)")
                tv_from, tv_to = t_proms.get(p, (zv, "(same)"))
                fe_from, fe_to = fe_proms.get(p, (tv_to, "(same)"))
                dt = (f"+{int(ORDINALS[p][tv_to]) - int(ORDINALS[p][zv])}"
                      if tv_to != "(same)" else "—")
                dfe = (f"+{int(ORDINALS[p][fe_to]) - int(ORDINALS[p][fe_from])}"
                       if fe_to != "(same)" else "—")
                atom = ""
                for a, (pk, vk) in _fe.PROMOTED_ATOM_TO_KEY.items():
                    for mv, fv in _MANIP_TO_FE_VAL.items():
                        if fv == vk and mv == fe_to and a in _FE_TIER_ATOMS:
                            atom = a
                            break
                tv_s = tv_to if tv_to != "(same)" else "(same)"
                fe_s = fe_to if fe_to != "(same)" else "(same)"
                print(f"  {p:<5}  {zv:<14}  {tv_s:<16}  {dt:<2}  {fe_s:<16}  {dfe:<3}  {atom}")
            print()
            print("  ZFCt promotions: HOLOBOUND + LR_DUAL + PM_Z2 + SEQAX + PHI_C + ZWIND")
            print("  ZFC_fe promotions: HOLOGRAPHIC_STATE (Ð) + ETERNAL_FIXEDPOINT (Ħ)")

    # ── :fe-tensor ───────────────────────────────────────────────────────────

    def cmd_fe_tensor(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return
        zfcfe = _normalize(ZFCFE_TUPLE)
        result = tensor_tuples(zfcfe, e)
        d_result, _ = _fe_distance(result)
        absorbed = d_result == 0.0
        bottlenecks = [p for p in PRIMITIVES
                       if ORDINALS[p].get(result[p], 0) < ORDINALS[p].get(zfcfe[p], 0)]

        result["name"] = f"ZFC_fe@{e.get('name','?')}"
        t_r = compute_tier(result)

        msg = (
            f"ZFC_fe @ {e.get('name','?')}: d(result, ZFC_fe)={round(d_result,2)}  "
            f"tier={t_r}  absorbed={'yes' if absorbed else 'no'}"
        )
        detail = (
            "  ZFC_fe absorbs this entry — tensor returns to ZFC_fe."
            if absorbed else
            f"  Bottlenecked at: {', '.join(bottlenecks)}  "
            f"(Frobenius cliff — those primitives pull below ZFC_fe)"
        )
        if console:
            console.print(f"  {msg}")
            console.print(detail)
        else:
            print(f"  {msg}")
            print(detail)

    # ── extended REPL ────────────────────────────────────────────────────────

    def run_repl(self):
        try:
            from rich.console import Console
            from rich.prompt import Prompt
            console = Console()
        except ImportError:
            console = None

        if console:
            console.print(
                "[bold cyan]ZFC/ZFCt/ZFCs/ZFC_fe Quadrangle Manipulator[/bold cyan]"
                "  —  :help for commands  |  :fe-lattice to see the chain"
            )
            console.print(
                f"  catalog: {len(self.catalog)} entries  "
                f"| apex: zfc_fe (𐑫, ETERNAL_FIXEDPOINT)  "
                f"| d(ZFCt,ZFC_fe)=2"
            )
        else:
            print("ZFC/ZFCt/ZFCs/ZFC_fe Quadrangle Manipulator — :help for commands")
            print(f"  catalog: {len(self.catalog)} entries")

        while True:
            try:
                raw = (Prompt.ask("\n[bold green]<ZFC_fe>[/bold green]")
                       if console else input("\n<ZFC_fe> ").strip())
            except (EOFError, KeyboardInterrupt):
                print("\nbye."); break

            parts = raw.strip().split()
            if not parts:
                continue
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in (":quit", ":exit", ":q"):
                print("bye."); break
            elif cmd == ":help":
                txt = _TRIANGLE_HELP + "\n\n" + FE_HELP_TEXT
                if console:
                    from rich.panel import Panel
                    console.print(Panel(txt, title="Help", border_style="dim"))
                else:
                    print(txt)
            elif cmd == ":fe-lattice":
                self.cmd_fe_lattice(console)
            elif cmd == ":fe-entry":
                if not args:
                    print("  usage: :fe-entry <name>")
                else:
                    self.cmd_fe_entry(" ".join(args), console)
            elif cmd == ":fe-distance":
                if not args:
                    print("  usage: :fe-distance <name>")
                else:
                    self.cmd_fe_distance(" ".join(args), console)
            elif cmd == ":fe-cliff":
                if not args:
                    print("  usage: :fe-cliff <name>")
                else:
                    self.cmd_fe_cliff(" ".join(args), console)
            elif cmd == ":fe-atoms":
                self.cmd_fe_atoms(console)
            elif cmd == ":fe-promotions":
                self.cmd_fe_promotions(console)
            elif cmd == ":fe-tensor":
                if not args:
                    print("  usage: :fe-tensor <name>")
                else:
                    self.cmd_fe_tensor(" ".join(args), console)
            else:
                # delegate to parent REPL by re-running its logic
                self._dispatch_parent(cmd, args, console)

    def _dispatch_parent(self, cmd: str, args: list, console=None):
        """Dispatch unknown commands to triangle manipulator."""
        if cmd == ":special":
            self.cmd_special(console)
        elif cmd == ":list":
            self.cmd_list(args[0] if args else "", console)
        elif cmd in (":lookup", ":clauses"):
            if not args:
                print(f"  usage: {cmd} <name>")
            else:
                self.cmd_clauses(" ".join(args), console)
        elif cmd == ":tier":
            if not args:
                print("  usage: :tier <name>")
            else:
                self.cmd_tier(" ".join(args), console)
        elif cmd in (":tensor", ":join", ":meet"):
            op = cmd[1:]
            if len(args) < 2:
                print(f"  usage: {cmd} <A> <B>")
            else:
                self.cmd_binary(op, args[0], " ".join(args[1:]), console)
        elif cmd == ":compare":
            if len(args) < 2:
                print("  usage: :compare <A> <B>")
            else:
                self.cmd_compare(args[0], " ".join(args[1:]), console)
        elif cmd == ":barrier":
            if len(args) < 2:
                print("  usage: :barrier <A> <B>")
            else:
                self.cmd_barrier(args[0], " ".join(args[1:]), console)
        elif cmd == ":distance":
            if len(args) < 2:
                print("  usage: :distance <A> <B>")
            else:
                self.cmd_distance(args[0], " ".join(args[1:]), console)
        elif cmd == ":lift":
            if len(args) < 3:
                print("  usage: :lift <name> <prim> <val>")
            else:
                self.cmd_lift(args[0], args[1], args[2], console)
        elif cmd == ":lattice":
            self.cmd_lattice(console)
        elif cmd in (":promotions-dual", ":promos", ":dual"):
            self.cmd_promotions_dual(console)
        elif cmd == ":cliff":
            self.cmd_cliff(args[0] if args else "imaginary_unit", console)
        elif cmd == ":rules":
            self.cmd_rules(console)
        elif cmd == ":scan":
            n = 100
            if args:
                try:
                    n = int(args[0])
                except ValueError:
                    print("  usage: :scan <N>"); return
            self.cmd_scan(n, console)
        else:
            msg = f"  unknown command '{cmd}' — try :help"
            if console:
                console.print(f"[red]{msg}[/red]")
            else:
                print(msg)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ZFC/ZFCt/ZFCs/ZFC_fe quadrangle manipulator"
    )
    parser.add_argument("--catalog", type=str, default=None)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("repl",        help="interactive REPL (default)")
    sub.add_parser("fe-lattice",  help="print ZFC/ZFCs/ZFCt/ZFC_fe lattice and exit")
    sub.add_parser("fe-atoms",    help="print promoted atoms table and exit")
    sub.add_parser("fe-promotions", help="print full promotion chain and exit")
    sc = sub.add_parser("fe-cliff", help="ZFC_fe cliff for a named entry")
    sc.add_argument("name", nargs="?", default="perfect_cuboid_lifted")
    se = sub.add_parser("fe-entry", help="full ZFC_fe formula decomposition")
    se.add_argument("name")

    args = parser.parse_args()
    manip = ZFCfeManipulator(catalog_path=args.catalog)

    if args.cmd == "fe-lattice":
        manip.cmd_fe_lattice()
    elif args.cmd == "fe-atoms":
        manip.cmd_fe_atoms()
    elif args.cmd == "fe-promotions":
        manip.cmd_fe_promotions()
    elif args.cmd == "fe-cliff":
        manip.cmd_fe_cliff(args.name)
    elif args.cmd == "fe-entry":
        manip.cmd_fe_entry(args.name)
    else:
        manip.run_repl()
