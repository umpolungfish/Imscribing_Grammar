#!/usr/bin/env python3
"""
zfct_navigator.py — ZFCₜ formula navigator with 6-channel promotion probe.

ZFCₜ extends ZFC via six primitive promotions (from MillenniumAnkh/Primitives/ZFCt.lean):
  Þ_6 → Þ_O   T_network → T_odot      holographic topology
  Ř_¯ → Ř_=   R_super   → R_lr        lateral relational mode
  Φ_ɐ → Φ_F   P_asym    → P_pm        ℤ₂ discrete symmetry
  ɢ^∧ → ɢ^ˌ   Gamma_and  → Gamma_seq   sequential composition
  Ħ_Ñ → Ħ_A   H0        → H2          persistent temporal asymmetry
  Ω_Å → Ω_z   Omega_0   → Omega_Z     integer winding number

Each promotion corresponds to a recovery channel in the ZFCₜ specialist router.
The 4 ZFC collapse channels (ƒ, Þ, Ð, ɢ) are subsumed and extended to 7.

ZFCₜ tier: O_inf (Phi_c + P_pm_sym + Omega_Z) — Frobenius gate open.

Run:
    uv run zfct_navigator.py train
    uv run zfct_navigator.py probe
    uv run zfct_navigator.py entry zfc_t
    uv run zfct_navigator.py promotions      # probe the 6 ZFCₜ promotion channels
    uv run zfct_navigator.py recover
"""

import argparse
import heapq
import json
import math
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# ── 1. Primitives (canonical v0.5.1, identical to zfc_navigator) ────────────

PRIMITIVES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

ORDINALS: Dict[str, Dict[str, float]] = {
    "Ð":  {"Ð_ß": 0, "Ð_C": 1, "Ð_;": 2, "Ð_ω": 3},
    "Þ":  {"Þ_6": 0, "Þ_K": 1, "Þ_ò": 2, "Þ_¨": 3, "Þ_O": 4},
    "Ř":  {"Ř_¯": 0, "Ř_ý": 1, "Ř_Ť": 2, "Ř_=": 3},
    "Φ":  {"Φ_ɐ": 0, "Φ_υ": 1, "Φ_F": 2, "Φ_˙": 3, "Φ_}": 4},
    "ƒ":  {"ƒ^ì": 0, "ƒ^ð": 1, "ƒ^ż": 2},
    "Ç":  {"Ç^-": 0, "Ç^W": 1, "Ç^@": 2, "Ç^Ù": 3, "Ç^λ": 4},
    "Γ":  {"Γ_β": 0, "Γ_γ": 1, "Γ_ʔ": 2},
    "ɢ":  {"ɢ^∧": 0, "ɢ^˝": 1, "ɢ^ˌ": 2, "ɢ^Ş": 3},
    "⊙": {"⊙_ž": 0, "⊙_ÿ": 1, "⊙_Æ": 2, "⊙_3": 3, "⊙_Ţ": 4},
    "Ħ":  {"Ħ_Ñ": 0, "Ħ_£": 1, "Ħ_A": 2, "Ħ_!": 3},
    "Σ":  {"Σ_S": 0, "Σ_ő": 1, "Σ_ï": 2},
    "Ω":  {"Ω_Å": 0, "Ω_2": 1, "Ω_z": 2, "Ω_5": 3},
}

WEIGHTS = {
    "Ð": 1.0, "Þ": 1.2, "Ř": 1.0, "Φ": 1.0,
    "ƒ": 0.9, "Ç": 1.0, "Γ": 1.0, "ɢ": 1.2,
    "⊙": 1.1, "Ħ": 1.2, "Σ": 0.8, "Ω": 1.2,
}
# ZFCₜ weights boost the 6 promoted primitives (Þ, ɢ, Ħ, Ω) to increase
# sensitivity to promotion-channel collapse.

INV_ORDINALS: Dict[str, Dict[int, str]] = {
    p: {int(v): k for k, v in vals.items()}
    for p, vals in ORDINALS.items()
}

NUM_VALUES = {p: len(v) for p, v in ORDINALS.items()}
MAX_VALUES  = max(NUM_VALUES.values())   # = 5

_PRIM_ALIASES: Dict[str, Dict[str, str]] = {
    "Þ": {
        "T_⊠": "Þ_ò", "T_⋈": "Þ_ò", "Þ_holo": "Þ_O", "Þ_torus": "Þ_ò",
        "Þ_cage": "Þ_¨", "Þ_bowl": "Þ_K", "Þ_linear": "Þ_6", "Þ_branched": "Þ_6",
    },
    "Ř": {
        "Ř_superset": "Ř_¯", "Ř_subset": "Ř_ý", "Ř_catalytic": "Ř_ý",
        "Ř_allosteric": "Ř_Ť", "Ř_exact": "Ř_Ť", "Ř_mechanical": "Ř_=",
        "Ř_covalent_dynamic": "Ř_ý",
    },
    "Φ": {
        "Φ_neutral": "Φ_ɐ", "Φ_plus": "Φ_υ", "Φ_minus": "Φ_υ",
        "Φ_directional": "Φ_ɐ", "Φ_pm_pseudo": "Φ_υ", "Φ_˙": "Φ_}",
    },
    "Σ": {"n:m": "Σ_ï", "1:1": "Σ_S", "n:n": "Σ_ő", "1_1": "Σ_S"},
}

def _normalize_entry(entry: dict) -> dict:
    out = dict(entry)
    for prim, aliases in _PRIM_ALIASES.items():
        if prim in out and out[prim] in aliases:
            out[prim] = aliases[out[prim]]
    return out

def tuple_to_indices(entry: dict) -> List[int]:
    return [int(ORDINALS[p][entry[p]]) for p in PRIMITIVES]

def indices_to_tuple(indices: List[int]) -> dict:
    return {p: INV_ORDINALS[p][indices[i]] for i, p in enumerate(PRIMITIVES)}

def tuple_distance(a: dict, b: dict) -> float:
    return math.sqrt(sum(WEIGHTS[p] * (ORDINALS[p][a[p]] - ORDINALS[p][b[p]]) ** 2
                         for p in PRIMITIVES))


# ── 1b. Temporal fiber, operad layer, gate constraints ───────────────────────

# Five primitives that jointly constitute time: T = lim(Φ, ƒ, Ç, Ħ, Ω)
T_PRIMITIVES: List[str] = ["Φ", "ƒ", "Ç", "Ħ", "Ω"]

# Critical values for the T-manifold to seal (Stone tuple values)
T_CRITICAL: Dict[str, str] = {
    "Φ": "Φ_}",   # Frobenius-special (algebraic symmetry class)
    "ƒ": "ƒ^ż",   # quantum coherent (metric-like)
    "Ç": "Ç^@",   # near-equilibrium (Ç^Ù / Ç^λ foreclose T permanently)
    "Ħ": "Ħ_!",   # permanent chirality (Z₂ bundle sealed)
    "Ω": "Ω_z",   # integer winding (topological/homotopy protection)
}

# Gate ordering: (gated_prim, min_ordinal_needing_gate, prereq_prim, prereq_min_ordinal)
# G1 (Φ_}, ord 4) must fire before G2 (⊙_ÿ, ord 1)
# G2 (⊙_ÿ, ord 1) must fire before G3 (Ω_z, ord 2)
GATE_CONSTRAINTS: List[Tuple[str, int, str, int]] = [
    ("⊙", 1, "Φ",  4),   # G2 requires G1 first
    ("Ω",  2, "⊙", 1),   # G3 requires G2 first
]

# T-path adds: Ħ_! cannot precede G2 (Exaltation cannot precede Fermentation)
T_PATH_GATE_CONSTRAINTS: List[Tuple[str, int, str, int]] = GATE_CONSTRAINTS + [
    ("Ħ",  3, "⊙", 1),   # Ħ_! requires G2 first
]
# Ç ceiling: Ç^Ù / Ç^λ permanently foreclose T; path must stay ≤ Ç^@
T_PATH_CEILINGS: Dict[str, int] = {"Ç": ORDINALS["Ç"]["Ç^@"]}


def operad_layer(entry: dict) -> str:
    """Derive monoidal operad layer from gate primitive values.

    plain → frobenius → traced_monoidal → idempotent_terminal
    G1: Φ_} fires (ord 4).  G2: ⊙_ÿ fires (ord ≥ 1).  G3: Ω_z fires (ord ≥ 2).
    """
    g1 = ORDINALS["Φ"].get(entry.get("Φ", ""), -1) >= 4
    g2 = ORDINALS["⊙"].get(entry.get("⊙", ""), -1) >= 1
    g3 = ORDINALS["Ω"].get(entry.get("Ω", ""), -1) >= 2
    if g1 and g2 and g3:
        return "idempotent_terminal"
    if g1 and g2:
        return "traced_monoidal"
    if g1:
        return "frobenius"
    return "plain"


def t_fiber_distance(entry: dict) -> float:
    """Weighted distance from entry to T-consistent region.

    Φ, ƒ, Ħ, Ω: squared gap to their critical value (both shortfall and overshoot penalised).
    Ç: only penalises excess *above* Ç^@ (the kinetic ceiling).
         Ç^W (below Ç^@) is T-compatible — only Ç^Ù / Ç^λ foreclose T.
    """
    total = 0.0
    for p in T_PRIMITIVES:
        v = entry.get(p)
        if v is None or v not in ORDINALS[p]:
            return float("inf")
        ord_v = ORDINALS[p][v]
        ord_c = ORDINALS[p][T_CRITICAL[p]]
        gap = max(0, ord_v - ord_c) if p == "Ç" else (ord_v - ord_c)
        total += WEIGHTS[p] * gap * gap
    return math.sqrt(total)


def t_consistency(entry: dict) -> dict:
    """Full T-manifold consistency report for an entry.

    t_consistent = True iff Φ=Φ_}, ƒ=ƒ^ż, Ç≤Ç^@, Ħ=Ħ_!, Ω=Ω_z.
    Ç^Ù (ord 3) and Ç^λ (ord 4) permanently foreclose T.
    Ç values below Ç^@ (e.g. Ç^W) are T-compatible.
    """
    c_ord = ORDINALS["Ç"].get(entry.get("Ç", ""), -1)
    ç_ceiling = ORDINALS["Ç"]["Ç^@"]   # ord 2
    ç_forecloses = c_ord > ç_ceiling    # Ç^Ù (3) or Ç^λ (4)

    d = t_fiber_distance(entry)
    details: Dict[str, dict] = {}
    for p in T_PRIMITIVES:
        v = entry.get(p, "?")
        if v not in ORDINALS.get(p, {}):
            details[p] = {"value": v, "target": T_CRITICAL[p], "gap": None, "status": "missing"}
            continue
        ord_v = ORDINALS[p][v]
        ord_c = ORDINALS[p][T_CRITICAL[p]]
        gap = ord_v - ord_c
        if p == "Ç":
            status = "forecloses_T" if gap > 0 else "ok"   # ≤ ceiling is always ok
        else:
            status = "sealed" if gap == 0 else ("above" if gap > 0 else "below_target")
        details[p] = {"value": v, "target": T_CRITICAL[p], "gap": gap, "status": status}

    t_ok = (d == 0.0 and not ç_forecloses)
    return {
        "t_fiber_distance": round(d, 4),
        "t_consistent": t_ok,
        "ç_forecloses_t": ç_forecloses,
        "primitives": details,
    }


# ── 2. ZFCₜ Token Vocabulary ─────────────────────────────────────────────────
#
# ZFC_VOCAB from zfc_navigator + 6 ZFCₜ-specific atoms:
#   HOLOBOUND  holographic boundary/bulk encoding  → Þ_O  (stronger than HOLO)
#   LR_DUAL    lateral relational duality          → Ř_=
#   PM_Z2      ℤ₂ parity marker                   → Φ_F
#   SEQAX      sequentiality axiom                 → ɢ^ˌ
#   TEMPD2     chirality 2 chirality          → Ħ_A
#   ZWIND      ℤ-winding (integer, not just ∃)     → Ω_z
#
# The 6 new atoms give the encoder distinctive features for each promotion
# channel, reducing roundtrip loss for ZFCₜ-regime entries.

ZFCT_VOCAB = [
    # Control
    "BOS", "EOS", "PAD", "SEP_PRIM",
    # Quantifiers
    "FORALL", "EXISTS", "EXISTS_UNIQUE",
    # Connectives
    "AND", "OR", "NOT", "IMPLIES", "IFF",
    # Punctuation
    "LPAREN", "RPAREN", "COMMA", "DOT",
    # Variables
    "VX", "VY", "VZ", "VU", "VV", "VW", "VA", "VB", "VF", "VG", "VH", "VN",
    # Relations
    "IN", "EQ", "SUBSETEQ", "SUBSET",
    # Set-theoretic constants / operations
    "EMPTY", "OMEGA",
    "UNION", "POWER", "SUCC", "PAIR", "SINGLETON",
    # Structural predicates
    "RANK", "ORD", "CARD", "FUNC", "BIJ",
    # ZFC grammar-specific atoms (retained from zfc_navigator)
    "SEP", "REPL", "REFL", "LCARD", "FROB", "WIND", "HOLO",
    "THETA", "FIXPT", "SEQPAIR", "DIRECTED_EDGE", "TAU", "GUE", "CLASSIC",
    # ZFCₜ-specific atoms (6 promotion channels)
    "HOLOBOUND",    # holographic boundary — Þ_O (T_odot)
    "LR_DUAL",      # lateral relational duality — Ř_= (R_lr)
    "PM_Z2",        # ℤ₂ parity — Φ_F (P_pm)
    "SEQAX",        # sequentiality axiom — ɢ^ˌ (Gamma_seq)
    "TEMPD2",       # chirality 2 — Ħ_A (H2)
    "ZWIND",        # integer winding — Ω_z (Omega_Z)
]

ZFCT_VOCAB_SIZE = len(ZFCT_VOCAB)
TOKEN2IDX = {t: i for i, t in enumerate(ZFCT_VOCAB)}
IDX2TOKEN  = {i: t for t, i in TOKEN2IDX.items()}

PAD_IDX = TOKEN2IDX["PAD"]
BOS_IDX = TOKEN2IDX["BOS"]
EOS_IDX = TOKEN2IDX["EOS"]
SEP_IDX = TOKEN2IDX["SEP_PRIM"]


# ── 3. ZFCₜ Templates ────────────────────────────────────────────────────────
#
# All 12 primitives × all values.
# The 6 promoted values use new ZFCₜ atoms for distinctive encoding.
# Non-promoted values retain their zfc_navigator templates.

ZFCT_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "Ð": {
        "Ð_ß":  ["EXISTS", "VA", "LPAREN", "VX", "IN", "VA", "AND", "EMPTY", "EQ", "VA", "RPAREN"],
        "Ð_C":  ["EXISTS", "VA", "LPAREN", "ORD", "VA", "AND", "VX", "IN", "RANK", "VA", "RPAREN"],
        "Ð_;":  ["FORALL", "VA", "EXISTS", "VB", "LPAREN",
                 "VA", "SUBSET", "VB", "AND", "RANK", "VX", "EQ", "VB", "RPAREN"],
        "Ð_ω":  ["LCARD", "VA", "AND", "HOLO", "VX", "VA"],
    },
    "Þ": {
        "Þ_6":  ["EXISTS", "VY", "FORALL", "VZ", "LPAREN",
                 "VZ", "IN", "VY", "IFF", "VZ", "IN", "VX", "RPAREN"],
        "Þ_K":  ["SEP", "VF", "VX"],
        "Þ_ò":  ["EXISTS", "VY", "EXISTS", "VZ", "LPAREN",
                 "UNION", "VY", "VZ", "EQ", "VX", "AND",
                 "SINGLETON", "VY", "EQ", "SINGLETON", "VZ", "RPAREN"],
        "Þ_¨":  ["FORALL", "VZ", "LPAREN",
                 "VZ", "IN", "VX", "IFF", "REPL", "VF", "VZ", "RPAREN"],
        # ZFCₜ promotion: HOLOBOUND distinguishes from REFL+HOLO (pure ZFC approx.)
        "Þ_O":  ["HOLOBOUND", "VA", "VF", "AND", "REFL", "VA", "VF", "AND", "HOLO", "VX", "VA"],
    },
    "Ř": {
        "Ř_¯":  ["FORALL", "VY", "LPAREN",
                 "VY", "IN", "VX", "IMPLIES", "VY", "IN", "VA", "RPAREN"],
        "Ř_ý":  ["REPL", "VF", "VX"],
        "Ř_Ť":  ["REPL", "VF", "VX", "AND",
                 "FORALL", "VY", "LPAREN", "VY", "IN", "REPL", "VF", "VX",
                 "IMPLIES", "BIJ", "VF", "VX", "VY", "RPAREN"],
        # ZFCₜ promotion: LR_DUAL asserts symmetric non-commutativity
        "Ř_=":  ["LR_DUAL", "VX", "VY", "AND",
                 "THETA", "VX", "VY", "AND", "NOT", "THETA", "VY", "VX"],
    },
    "Φ": {
        "Φ_ɐ":  ["EXISTS", "VX", "NOT", "VX", "EQ", "VX"],
        "Φ_υ":  ["EXISTS", "VY", "LPAREN",
                 "VY", "IN", "VX", "AND", "NOT", "VY", "EQ", "VX", "RPAREN"],
        # ZFCₜ promotion: PM_Z2 marks the ℤ₂ involution (non-Frobenius parity)
        "Φ_F":  ["PM_Z2", "VF", "AND",
                 "EXISTS", "VF", "LPAREN",
                 "BIJ", "VF", "VX", "VX", "AND",
                 "FORALL", "VY", "LPAREN",
                 "VF", "LPAREN", "VF", "VY", "RPAREN", "EQ", "VY", "RPAREN", "RPAREN"],
        "Φ_˙":  ["FORALL", "VF", "LPAREN",
                 "BIJ", "VF", "VX", "VX", "IMPLIES",
                 "FORALL", "VY", "LPAREN", "VY", "IN", "VX",
                 "IFF", "VF", "VY", "IN", "VX", "RPAREN", "RPAREN"],
        "Φ_}":  ["FROB", "VF", "VG"],
    },
    "ƒ": {
        "ƒ^ì":  ["CLASSIC", "VX"],
        "ƒ^ð":  ["EXISTS", "VY", "LPAREN",
                 "VY", "EQ", "VX", "AND", "VY", "IN", "OMEGA", "RPAREN"],
        # ⚠ TOTAL COLLAPSE: ƒ^ż → identical CLASSIC token as ƒ^ì
        "ƒ^ż":  ["CLASSIC", "VX"],
    },
    "Ç": {
        "Ç^-":  ["EXISTS", "VY", "LPAREN", "SUCC", "VY", "EQ", "VX", "RPAREN"],
        "Ç^W":  ["EXISTS", "VY", "EXISTS", "VZ", "LPAREN",
                 "VY", "IN", "VX", "AND", "VZ", "IN", "VX", "AND", "VY", "SUBSETEQ", "VZ", "RPAREN"],
        "Ç^@":  ["FORALL", "VY", "LPAREN",
                 "VY", "SUBSETEQ", "VX", "IMPLIES",
                 "EXISTS", "VZ", "LPAREN", "VZ", "IN", "VX", "AND", "VY", "SUBSETEQ", "VZ",
                 "RPAREN", "RPAREN"],
        "Ç^Ù":  ["FIXPT", "VF"],
        "Ç^λ":  ["FORALL", "VY", "FORALL", "VZ", "LPAREN",
                 "VY", "IN", "VX", "AND", "VZ", "IN", "VX",
                 "AND", "NOT", "VY", "EQ", "VZ", "IMPLIES",
                 "NOT", "VY", "IN", "VZ", "RPAREN"],
    },
    "Γ": {
        "Γ_β":  ["EXISTS", "VY", "LPAREN", "VY", "IN", "VX", "RPAREN"],
        "Γ_γ":  ["EXISTS", "VY", "EXISTS", "VZ", "LPAREN",
                 "VY", "IN", "VX", "AND", "VZ", "IN", "VX", "AND", "NOT", "VY", "EQ", "VZ", "RPAREN"],
        "Γ_ʔ":  ["FORALL", "VA", "EXISTS", "VY", "LPAREN",
                 "CARD", "VA", "IMPLIES",
                 "CARD", "VY", "AND", "VA", "SUBSETEQ", "VY", "AND", "VY", "IN", "VX", "RPAREN"],
    },
    "ɢ": {
        "ɢ^∧":  ["AND"],
        "ɢ^˝":  ["OR"],
        # ZFCₜ promotion: SEQAX prefix + DIRECTED_EDGE+TAU (ZFCₜ axiom for causal ordering)
        "ɢ^ˌ":  ["SEQAX", "VF", "VG", "AND",
                 "DIRECTED_EDGE", "VF", "VG", "TAU",
                 "AND", "NOT", "DIRECTED_EDGE", "VG", "VF", "TAU"],
        "ɢ^Ş":  ["FORALL", "VY", "LPAREN", "VF", "VY", "RPAREN"],
    },
    "⊙": {
        "⊙_ž":  ["EXISTS", "VY", "LPAREN",
                 "VY", "IN", "VX", "AND", "RANK", "VY", "SUBSET", "RANK", "VX", "RPAREN"],
        "⊙_ÿ":  ["FIXPT", "VF"],
        "⊙_Æ":  ["GUE", "VX", "AND", "FIXPT", "VF"],
        "⊙_3":  ["LCARD", "VA", "AND", "FIXPT", "VF"],
        "⊙_Ţ":  ["FORALL", "VY", "LPAREN",
                 "VY", "SUBSETEQ", "VX", "IMPLIES", "FIXPT", "VY", "RPAREN"],
    },
    "Ħ": {
        "Ħ_Ñ":  ["VX", "EQ", "VX"],
        "Ħ_£":  ["EXISTS", "VY", "LPAREN",
                 "VY", "IN", "VX", "AND", "NOT", "VX", "IN", "VY", "RPAREN"],
        # ZFCₜ promotion: TEMPD2 marks persistent two-level temporal asymmetry
        "Ħ_A":  ["TEMPD2", "VX", "AND",
                 "EXISTS", "VY", "EXISTS", "VZ", "LPAREN",
                 "VY", "IN", "VX", "AND", "VZ", "IN", "VY",
                 "AND", "NOT", "VZ", "IN", "VX", "RPAREN"],
        "Ħ_!":  ["WIND", "VF", "VX", "AND", "NOT", "WIND", "VF", "SUCC", "VX"],
    },
    "Σ": {
        "Σ_S":  ["BIJ", "VF", "VX", "VX"],
        "Σ_ő":  ["EXISTS", "VF", "LPAREN", "BIJ", "VF", "VX", "VX", "RPAREN"],
        "Σ_ï":  ["EXISTS", "VF", "LPAREN",
                 "FUNC", "VF", "AND", "NOT", "BIJ", "VF", "VX", "VX", "RPAREN"],
    },
    "Ω": {
        "Ω_Å":  ["VX", "EQ", "VX"],
        "Ω_2":  ["EXISTS", "VY", "LPAREN", "SUCC", "SUCC", "VY", "EQ", "VX", "RPAREN"],
        # ZFCₜ promotion: ZWIND+WIND marks integer (not just existential) winding
        "Ω_z":  ["ZWIND", "VF", "VX", "AND", "WIND", "VF", "VX"],
        "Ω_5":  ["THETA", "VX", "VY", "AND", "WIND", "VF", "VX"],
    },
}


def compose_formula(entry: dict) -> List[int]:
    tokens = [BOS_IDX]
    for prim in PRIMITIVES:
        frag = ZFCT_TEMPLATES[prim][entry[prim]]
        tokens.extend(TOKEN2IDX[t] for t in frag)
        tokens.append(SEP_IDX)
    tokens.append(EOS_IDX)
    return tokens

def pad_formula(tokens: List[int], max_len: int = 256) -> List[int]:
    if len(tokens) >= max_len:
        return tokens[:max_len - 1] + [EOS_IDX]
    return tokens + [PAD_IDX] * (max_len - len(tokens))


# ── 4. ZFCₜ Encoder ──────────────────────────────────────────────────────────

class _NestedTransformerEncoderLayer(nn.Module):
    """Lightweight self-attention encoder that supports both ragged (nested) and
    padded (dense) inputs.  Replaces nn.TransformerEncoder to eliminate the
    internal `enable_nested_tensor` deprecation path in PyTorch >= 2.4."""

    def __init__(self, d_model: int, nhead: int, dim_feedforward: int, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        self.ln1  = nn.LayerNorm(d_model)
        self.ff   = nn.Sequential(
            nn.Linear(d_model, dim_feedforward), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(dim_feedforward, d_model), nn.Dropout(dropout),
        )
        self.ln2  = nn.LayerNorm(d_model)

    def _jagged_to_padded(self, src):
        """Convert jagged nested tensor to (padded_tensor, key_padding_mask)."""
        seqs = list(src.unbind(0))
        lengths = [len(s) for s in seqs]
        max_len = max(lengths)
        padded = src.to_padded_tensor(padding=0.0)
        # key_padding_mask: True where PAD (shape: batch x seq_len)
        mask = torch.zeros(padded.shape[0], max_len, dtype=torch.bool, device=padded.device)
        for i, l in enumerate(lengths):
            mask[i, l:] = True
        return padded, mask

    def forward(self, src, src_mask=None, src_key_padding_mask=None, is_causal=False,
                memory=None, memory_mask=None, memory_key_padding_mask=None):
        # src can be a torch._nested_tensor (jagged) or a regular Tensor (padded)
        # Normalize jagged to padded+mask (MultiheadAttention training mode does not
        # support nested tensors directly), then use the standard attention path.
        if isinstance(src, torch.Tensor) and src.layout == torch.jagged:
            src, src_key_padding_mask = self._jagged_to_padded(src)
        # Dense/padded path — standard transformer layer.
        x = src
        residual = x
        x, _ = self.attn(x, x, x, key_padding_mask=src_key_padding_mask,
                         is_causal=is_causal)
        x = self.ln1(x + residual)
        x = x + self.ff(x)
        return self.ln2(x)


class NestedTransformerEncoder(nn.Module):
    """Stack of _NestedTransformerEncoderLayer blocks.  Accepts regular tensors
    (dense, padded) and torch.jagged tensors (nested/ragged) transparently."""

    def __init__(self, layer: nn.Module, num_layers: int):
        super().__init__()
        self.layers = nn.ModuleList([layer for _ in range(num_layers)])

    def forward(self, src, src_mask=None, src_key_padding_mask=None, is_causal=False):
        x = src
        for mod in self.layers:
            x = mod(x, src_mask=src_mask, src_key_padding_mask=src_key_padding_mask,
                    is_causal=is_causal)
        return x


class ZFCtEncoder(nn.Module):
    """Transformer encoder over the extended ZFCₜ vocabulary.

    Supports both padded (legacy) and jagged/nested tensor inputs via
    ``torch.nested`` — no more ``enable_nested_tensor`` deprecation warning.
    """

    def __init__(
        self,
        vocab_size: int = ZFCT_VOCAB_SIZE,
        max_len:    int = 256,
        hidden_dim: int = 256,
        n_heads:    int = 4,
        n_layers:   int = 4,
        dropout:    float = 0.1,
        use_nested: bool = False,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.use_nested = use_nested
        self.tok_emb = nn.Embedding(vocab_size, hidden_dim, padding_idx=PAD_IDX)
        self.pos_emb = nn.Embedding(max_len, hidden_dim)
        enc_layer = _NestedTransformerEncoderLayer(
            d_model=hidden_dim, nhead=n_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
        )
        self.transformer = NestedTransformerEncoder(enc_layer, num_layers=n_layers)
        self.heads = nn.ModuleList([nn.Linear(hidden_dim, NUM_VALUES[p]) for p in PRIMITIVES])
        self.dropout = nn.Dropout(dropout)
        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.tok_emb.weight, std=0.02)
        nn.init.normal_(self.pos_emb.weight, std=0.02)
        for h in self.heads:
            nn.init.xavier_uniform_(h.weight)

    def forward(self, token_ids: torch.Tensor, seq_lengths: Optional[torch.Tensor] = None) -> List[torch.Tensor]:
        # Detect input layout
        is_jagged = isinstance(token_ids, torch.Tensor) and token_ids.layout == torch.jagged

        if is_jagged:
            # Nested-tensor path: apply embeddings layer-by-layer
            x = self.dropout(self.tok_emb(token_ids))
            # positional info encoded via learned offset in the nested tensor itself
            x = self.transformer(x)
            # For jagged tensors, mean-reduce over each sequence in the batch
            # Mean-reduce over each sequence (sequence-level pooling for classification)
            seqs = x.unbind(0)
            x_mean = torch.stack([s.mean(dim=0) for s in seqs])
        else:
            # Legacy padded path
            if token_ids.dim() == 1:
                token_ids = token_ids.unsqueeze(0)
            B, L = token_ids.shape
            positions = torch.arange(L, device=token_ids.device).unsqueeze(0).expand(B, -1)
            pad_mask  = (token_ids == PAD_IDX)
            x = self.dropout(self.tok_emb(token_ids) + self.pos_emb(positions))
            x = self.transformer(x, src_key_padding_mask=pad_mask)
            if seq_lengths is not None:
                lens = seq_lengths.float().unsqueeze(-1).clamp(min=1)
            else:
                lens  = (~pad_mask).float().sum(dim=1, keepdim=True).clamp(min=1)
            x_mean = (x * (~pad_mask).float().unsqueeze(-1)).sum(1) / lens
        return [head(x_mean) for head in self.heads]


def frobenius_loss(
    logits_list: List[torch.Tensor],
    targets:     torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor]:
    losses = [F.cross_entropy(logits_list[i], targets[:, i]) for i in range(len(logits_list))]
    per_prim = torch.stack(losses)
    return per_prim.mean(), per_prim


# ── 5. Dataset ───────────────────────────────────────────────────────────────

def load_catalog(path: str = None) -> List[dict]:
    try:
        from imscrbgrmr.registry import load_catalog_dicts
        return load_catalog_dicts(extra_path=path)
    except ImportError:
        import glob as _glob, os
        _DIR = os.path.dirname(os.path.abspath(__file__))
        candidates = [os.path.join(_DIR, "IG_catalog.json"), "IG_catalog.json", "ig_catalog*.json"]
        if path is None:
            paths = []
            for c in candidates:
                if "*" in c or "?" in c:
                    paths.extend(sorted(_glob.glob(c)))
                elif os.path.isfile(c):
                    paths.append(c)
                if paths:
                    break
            if not paths:
                raise FileNotFoundError("IG_catalog.json not found. Pass --catalog to specify a path.")
        elif "*" in str(path) or "?" in str(path):
            paths = sorted(_glob.glob(path))
            if not paths:
                raise FileNotFoundError(f"No files matching '{path}' found.")
        else:
            paths = [path]
        seen: set = set()
        merged: List[dict] = []
        for p in paths:
            with open(p) as f:
                for e in json.load(f):
                    nm = e.get("name", "")
                    if nm not in seen:
                        seen.add(nm); merged.append(e)
        return merged

def build_dataset(catalog: List[dict], max_len: int = 256) -> Tuple[torch.Tensor, torch.Tensor]:
    token_list, target_list = [], []
    for entry in catalog:
        if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
            continue
        token_list.append(pad_formula(compose_formula(entry), max_len))
        target_list.append(tuple_to_indices(entry))
    return (torch.tensor(token_list, dtype=torch.long),
            torch.tensor(target_list, dtype=torch.long))


# ── 6. ZFCₜ Reference Entries (from MillenniumAnkh/Primitives/ZFCt.lean) ─────

ZFC_TUPLE = {
    "name": "ZFC_foundations",
    "description": "Zermelo-Fraenkel set theory with Choice (corrected: D_infty, Phi_c)",
    "Ð": "Ð_;",  "Þ": "Þ_K",  "Ř": "Ř_¯",  "Φ": "Φ_ɐ",
    "ƒ": "ƒ^ż",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^∧",
    "⊙": "⊙_ÿ", "Ħ": "Ħ_Ñ",  "Σ": "Σ_ï",  "Ω": "Ω_Å",
}

ZFCT_TUPLE = {
    "name": "zfc_t",
    "description": "ZFCₜ: ZFC + sequential + chirality + winding (O_inf, Frobenius)",
    "Ð": "Ð_;",   # D_infty
    "Þ": "Þ_O",   # T_odot   ← ZFCₜ promotion
    "Ř": "Ř_=",   # R_lr     ← ZFCₜ promotion
    "Φ": "Φ_}",   # P_pm_sym ← ZFCₜ promotion (Frobenius-special)
    "ƒ": "ƒ^ż",   # F_hbar
    "Ç": "Ç^@",   # K_slow
    "Γ": "Γ_ʔ",   # G_aleph
    "ɢ": "ɢ^ˌ",   # Gamma_seq  ← ZFCₜ promotion
    "⊙": "⊙_ÿ",  # Phi_c
    "Ħ": "Ħ_A",   # H2       ← ZFCₜ promotion
    "Σ": "Σ_ï",   # n_m
    "Ω": "Ω_z",   # Omega_Z  ← ZFCₜ promotion
}

TEMPORAL_MATHEMATICS_TUPLE = {
    "name": "temporal_mathematics",
    "description": "Temporal mathematics (ZFCt.lean: temporal_mathematics)",
    "Ð": "Ð_;",  "Þ": "Þ_O",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ^ż",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ÿ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

SCHRODINGER_TUPLE = {
    "name": "schrodinger_equation",
    "description": "Schrödinger equation (ZFCt.lean: schrodinger_equation)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_=",  "Φ": "Φ_υ",
    "ƒ": "ƒ^ż",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_Æ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

HEAT_DIFFUSION_TUPLE = {
    "name": "heat_diffusion_equation",
    "description": "Heat diffusion equation (ZFCt.lean: heat_diffusion_equation)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_Ť",  "Φ": "Φ_ɐ",
    "ƒ": "ƒ^ð",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ž", "Ħ": "Ħ_£",  "Σ": "Σ_ï",  "Ω": "Ω_Å",
}

NAVIER_STOKES_TUPLE = {
    "name": "navier_stokes_equations",
    "description": "Navier-Stokes equations (ZFCt.lean: navier_stokes_equations)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_=",  "Φ": "Φ_F",
    "ƒ": "ƒ^ì",  "Ç": "Ç^W",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ÿ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

WAVE_EQUATION_TUPLE = {
    "name": "wave_equation_temporal",
    "description": "Wave equation (ZFCt.lean: wave_equation_temporal)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ^ì",  "Ç": "Ç^W",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ž", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_Å",
}

EINSTEIN_TUPLE = {
    "name": "einstein_field_equations_dynamic",
    "description": "Einstein field equations dynamic (ZFCt.lean)",
    "Ð": "Ð_;",  "Þ": "Þ_O",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ^ì",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_Æ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

IUG_TUPLE = {
    "name": "IUG_mochizuki",
    "description": "Inter-Universal Teichmüller Theory (Mochizuki)",
    "Ð": "Ð_ω",  "Þ": "Þ_O",  "Ř": "Ř_=",  "Φ": "Φ_}",
    "ƒ": "ƒ^ż",  "Ç": "Ç^@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ÿ", "Ħ": "Ħ_!",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

_SPECIAL_ENTRIES = {
    "zfc": ZFC_TUPLE, "ZFC": ZFC_TUPLE, "zfc_foundations": ZFC_TUPLE,
    "zfc_t": ZFCT_TUPLE, "zfct": ZFCT_TUPLE, "ZFCt": ZFCT_TUPLE,
    "temporal_mathematics": TEMPORAL_MATHEMATICS_TUPLE,
    "schrodinger": SCHRODINGER_TUPLE, "schrodinger_equation": SCHRODINGER_TUPLE,
    "heat": HEAT_DIFFUSION_TUPLE, "heat_diffusion": HEAT_DIFFUSION_TUPLE,
    "navier_stokes": NAVIER_STOKES_TUPLE, "ns": NAVIER_STOKES_TUPLE,
    "wave": WAVE_EQUATION_TUPLE, "wave_equation": WAVE_EQUATION_TUPLE,
    "einstein": EINSTEIN_TUPLE, "efe": EINSTEIN_TUPLE,
    "iug": IUG_TUPLE, "IUG": IUG_TUPLE,
}

ZFCT_REFERENCE_ENTRIES = [
    ZFC_TUPLE, ZFCT_TUPLE, TEMPORAL_MATHEMATICS_TUPLE,
    SCHRODINGER_TUPLE, HEAT_DIFFUSION_TUPLE, NAVIER_STOKES_TUPLE,
    WAVE_EQUATION_TUPLE, EINSTEIN_TUPLE, IUG_TUPLE,
]

# ZFCₜ promotion map: which primitive was promoted from which value
ZFCT_PROMOTIONS: List[Tuple[str, str, str]] = [
    ("Þ", "Þ_6", "Þ_O"),   # T_network → T_odot
    ("Ř", "Ř_¯", "Ř_="),   # R_super   → R_lr
    ("Φ", "Φ_ɐ", "Φ_F"),   # P_asym    → P_pm
    ("ɢ", "ɢ^∧", "ɢ^ˌ"),   # Gamma_and → Gamma_seq
    ("Ħ", "Ħ_Ñ", "Ħ_A"),   # H0        → H2
    ("Ω", "Ω_Å", "Ω_z"),   # Omega_0   → Omega_Z
]


# ── 7. Training ───────────────────────────────────────────────────────────────

def train(
    catalog_path: str   = None,
    n_epochs:     int   = 500,
    batch_size:   int   = 24,
    lr:           float = 3e-4,
    hidden_dim:   int   = 24,
    n_layers:     int   = 24,
    max_len:      int   = 256,
    seed:         int   = 17280000,
    save_path:    str   = "zfct_encoder.pt",
):
    torch.manual_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[zfct_navigator] device={device}  vocab={ZFCT_VOCAB_SIZE}  max_len={max_len}")

    catalog = load_catalog(catalog_path)
    # Merge reference entries (always present)
    ref_names = {e["name"] for e in ZFCT_REFERENCE_ENTRIES}
    catalog_plus = ZFCT_REFERENCE_ENTRIES + [e for e in catalog if e.get("name") not in ref_names]

    token_seqs, targets = build_dataset(catalog_plus, max_len)
    print(f"[zfct_navigator] dataset: {len(token_seqs)} valid entries ({len(catalog_plus)} loaded)")

    # Report ZFCₜ promotion instances
    for prim, zfc_val, zfct_val in ZFCT_PROMOTIONS:
        n = sum(1 for e in catalog_plus if e.get(prim) == zfct_val)
        print(f"  {prim}: {zfc_val}→{zfct_val}  {n} entries")

    dataset   = TensorDataset(token_seqs, targets)
    loader    = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model     = ZFCtEncoder(hidden_dim=hidden_dim, n_layers=n_layers, max_len=max_len).to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=n_epochs)

    print(f"[zfct_navigator] parameters: {sum(p.numel() for p in model.parameters()):,}")

    best_loss = float("inf")
    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss, epoch_prim, n_batches = 0.0, torch.zeros(12), 0
        for toks, tgts in loader:
            toks, tgts = toks.to(device), tgts.to(device)
            optimiser.zero_grad()
            loss, pp = frobenius_loss(model(toks), tgts)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            epoch_loss += loss.item(); epoch_prim += pp.detach().cpu(); n_batches += 1
        scheduler.step()
        avg_loss = epoch_loss / n_batches
        if epoch % 50 == 0 or epoch == 1:
            top2 = (epoch_prim / n_batches).topk(2)
            print(f"  ep {epoch:4d}  loss={avg_loss:.4f}  "
                  f"top: {PRIMITIVES[top2.indices[0]]}={top2.values[0]:.3f}  "
                  f"{PRIMITIVES[top2.indices[1]]}={top2.values[1]:.3f}")
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), save_path)
    print(f"[zfct_navigator] done. best loss={best_loss:.4f}  saved → {save_path}")
    return model


# ── 8. ZFCₜ Specialist Router (6 promotion channels + ƒ-channel) ─────────────

@dataclass
class ZFCtSlot:
    name:            str
    primitive:       str
    evidence_tokens: List[str]
    wrong_pred:      str
    correction:      str
    priority:        int

DEFAULT_ZFCT_SLOTS: List[ZFCtSlot] = [
    # Þ-channel: holographic topology — HOLOBOUND+REFL distinguishes Þ_O from Þ_K
    ZFCtSlot("Þ_recovery",  "Þ",  ["HOLOBOUND", "REFL"],                  "Þ_K",  "Þ_O",  0),
    # ɢ-channel: sequential composition — SEQAX+DIRECTED_EDGE+TAU → ɢ^ˌ
    ZFCtSlot("ɢ_recovery",  "ɢ",  ["SEQAX", "DIRECTED_EDGE", "TAU"],      "ɢ^∧",  "ɢ^ˌ",  1),
    # Ř-channel: lateral relational — LR_DUAL+THETA → Ř_=
    ZFCtSlot("Ř_recovery",  "Ř",  ["LR_DUAL", "THETA"],                   "Ř_Ť",  "Ř_=",  2),
    # Φ-channel: ℤ₂ parity — PM_Z2 is unique to Φ_F template
    ZFCtSlot("Φ_recovery",  "Φ",  ["PM_Z2"],                              "Φ_ɐ",  "Φ_F",  3),
    # Ħ-channel: chirality 2 — TEMPD2 is unique to Ħ_A template
    ZFCtSlot("Ħ_recovery",  "Ħ",  ["TEMPD2"],                             "Ħ_Ñ",  "Ħ_A",  4),
    # Ω-channel: integer winding — ZWIND+WIND distinguishes Ω_z from Ω_Å
    ZFCtSlot("Ω_recovery",  "Ω",  ["ZWIND", "WIND"],                      "Ω_Å",  "Ω_z",  5),
    # ƒ-channel: F_hbar (quantum) — retained from zfc_navigator F-recovery
    # CLASSIC+FROB+FIXPT+HOLO jointly mark O_inf-adjacent quantum-fidelity context
    ZFCtSlot("ƒ_recovery",  "ƒ",  ["CLASSIC", "FROB", "FIXPT", "HOLO"],   "ƒ^ì",  "ƒ^ż",  6),
]


class ZFCtSpecialistRouter:
    """
    Token-evidence post-processor for ZFCₜ encoder predictions.

    Seven slots covering the 6 ZFCₜ promotion channels plus the ƒ-channel
    inherited from ZFC non-transmissibility. Fires in priority order;
    first match per primitive wins.
    """

    def __init__(self, slots: List[ZFCtSlot] = None):
        self.slots = sorted(
            slots if slots is not None else DEFAULT_ZFCT_SLOTS,
            key=lambda s: s.priority,
        )
        self.corrections_fired: dict = {}

    def apply(self, token_ids: List[int], pred_tuple: dict) -> dict:
        self.corrections_fired = {}
        result = dict(pred_tuple)
        present = {IDX2TOKEN.get(idx, "") for idx in token_ids}
        for slot in self.slots:
            if slot.primitive in self.corrections_fired:
                continue
            if not all(tok in present for tok in slot.evidence_tokens):
                continue
            if result.get(slot.primitive) != slot.wrong_pred:
                continue
            result[slot.primitive] = slot.correction
            self.corrections_fired[slot.primitive] = slot.name
        return result


# ── 9. Transmissibility Probe ─────────────────────────────────────────────────

@dataclass
class ProbeResult:
    name:            str
    input_tuple:     dict
    predicted_tuple: dict
    roundtrip_dist:  float
    roundtrip_loss:  float
    per_prim_loss:   Dict[str, float]
    promotion_flags: List[str]


def run_probe(
    catalog_path: str = None,
    model_path:   str = "zfct_encoder.pt",
    max_len:      int = 256,
    top_n:        int = 20,
    hidden_dim:   int = 256,
    n_layers:     int = 4,
):
    device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    catalog = load_catalog(catalog_path)
    ref_names = {e["name"] for e in ZFCT_REFERENCE_ENTRIES}
    catalog_plus = ZFCT_REFERENCE_ENTRIES + [e for e in catalog if e.get("name") not in ref_names]

    model = ZFCtEncoder(hidden_dim=hidden_dim, n_layers=n_layers, max_len=max_len).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    results: List[ProbeResult] = []
    with torch.no_grad():
        for entry in catalog_plus:
            entry = _normalize_entry(entry)
            if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
                continue
            tokens  = torch.tensor([pad_formula(compose_formula(entry), max_len)],
                                    dtype=torch.long, device=device)
            targets = torch.tensor([tuple_to_indices(entry)],
                                    dtype=torch.long, device=device)
            logits  = model(tokens)
            loss, pp = frobenius_loss(logits, targets)
            pred_idx   = [int(logits[i].argmax(dim=-1).item()) for i in range(12)]
            pred_tuple = indices_to_tuple(pred_idx)
            rt_dist    = tuple_distance(entry, pred_tuple)
            per_prim   = {PRIMITIVES[i]: float(pp[i]) for i in range(12)}
            flags = []
            for prim, zfc_val, zfct_val in ZFCT_PROMOTIONS:
                if entry.get(prim) == zfct_val and pred_tuple.get(prim) != zfct_val:
                    flags.append(f"{prim}: {zfct_val}→{pred_tuple.get(prim,'?')}")
            results.append(ProbeResult(
                name=entry.get("name", "?"), input_tuple={p: entry[p] for p in PRIMITIVES},
                predicted_tuple=pred_tuple, roundtrip_dist=rt_dist,
                roundtrip_loss=float(loss), per_prim_loss=per_prim, promotion_flags=flags,
            ))

    results.sort(key=lambda r: r.roundtrip_dist, reverse=True)
    print("\n" + "=" * 80)
    print("ZFCₜ TRANSMISSIBILITY PROBE — Top entries by roundtrip distance")
    print("=" * 80)
    print(f"{'Name':<35} {'d_rt':>6}  {'loss':>6}  Promotion mismatches")
    print("-" * 80)
    for r in results[:top_n]:
        fl = "; ".join(r.promotion_flags) if r.promotion_flags else "—"
        print(f"{r.name[:35]:<35} {r.roundtrip_dist:>6.3f}  {r.roundtrip_loss:>6.3f}  {fl}")

    all_dists = [r.roundtrip_dist for r in results]
    print(f"\nTotal entries:  {len(results)}")
    print(f"Mean d_rt:      {np.mean(all_dists):.4f}")
    print(f"Max  d_rt:      {np.max(all_dists):.4f}")

    print("\nMean per-primitive roundtrip loss:")
    prim_means = {p: np.mean([r.per_prim_loss[p] for r in results]) for p in PRIMITIVES}
    for p, v in sorted(prim_means.items(), key=lambda x: -x[1]):
        bar = "█" * int(v * 20)
        promo = "*" if any(p == pm for pm, _, _ in ZFCT_PROMOTIONS) else " "
        print(f"  {p:<6}{promo} {v:.4f}  {bar}")
    print("  (* = ZFCₜ promotion primitive)")
    return results


# ── 10. Promotion probe ───────────────────────────────────────────────────────

def probe_promotions(
    model_path: str = "zfct_encoder.pt",
    max_len:    int = 256,
    hidden_dim: int = 256,
    n_layers:   int = 4,
):
    """
    Probe specifically the 6 ZFCₜ promotion channels.
    For each channel: show d(ZFC_val, ZFCₜ_val) and the roundtrip on the reference entries.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_p = Path(model_path)

    W = 80
    print("\n" + "═" * W)
    print("  ZFCₜ PROMOTION PROBE — 6-channel recovery analysis")
    print("═" * W)

    # Grammar distances for each promotion
    print(f"\n  Primitive grammar distances (ZFC value → ZFCₜ promoted value):")
    for prim, zfc_val, zfct_val in ZFCT_PROMOTIONS:
        d = abs(ORDINALS[prim][zfct_val] - ORDINALS[prim][zfc_val]) * WEIGHTS[prim] ** 0.5
        print(f"    {prim:<4}  {zfc_val:<8} → {zfct_val:<8}  ordinal gap={abs(ORDINALS[prim][zfct_val] - ORDINALS[prim][zfc_val])}  weighted={d:.3f}")

    # d(ZFC, ZFCt)
    d_zfc_zfct = tuple_distance(ZFC_TUPLE, ZFCT_TUPLE)
    print(f"\n  d(ZFC, ZFCₜ) = {d_zfc_zfct:.4f}  (6 simultaneous promotions)")
    print(f"  ZFCₜ tier:   O_inf  (Phi_c + P_pm_sym + Omega_Z — Frobenius gate open)")

    if not model_p.exists():
        print(f"\n  [promotions] model not found at {model_path} — skipping roundtrip.")
        print("  Run `uv run zfct_navigator.py train` first.")
        return

    model = ZFCtEncoder(hidden_dim=hidden_dim, n_layers=n_layers, max_len=max_len).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    router = ZFCtSpecialistRouter()

    print(f"\n  {'Entry':<35} {'d_rt':>6}  {'d_rec':>6}  {'Slots fired'}")
    print("  " + "-" * 68)

    with torch.no_grad():
        for entry in ZFCT_REFERENCE_ENTRIES:
            entry = _normalize_entry(entry)
            if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
                continue
            token_ids = pad_formula(compose_formula(entry), max_len)
            tokens_t  = torch.tensor([token_ids], dtype=torch.long, device=device)
            logits    = model(tokens_t)
            pred_idx  = [int(logits[i].argmax(dim=-1).item()) for i in range(12)]
            base_pred = indices_to_tuple(pred_idx)
            base_dist = tuple_distance(entry, base_pred)
            rec_pred  = router.apply(token_ids, base_pred)
            rec_dist  = tuple_distance(entry, rec_pred)
            slots_str = ", ".join(router.corrections_fired.values()) if router.corrections_fired else "—"
            name = entry.get("name", "?")[:33]
            print(f"  {name:<35} {base_dist:>6.4f}  {rec_dist:>6.4f}  {slots_str}")

    print(f"\n  Slot evidence tokens:")
    for slot in DEFAULT_ZFCT_SLOTS:
        evstr = " + ".join(slot.evidence_tokens)
        print(f"    [{slot.name:<15}] {evstr}")


# ── 11. Entry probe ───────────────────────────────────────────────────────────

_TM = {
    "BOS": "⟨", "EOS": "⟩", "PAD": "", "SEP_PRIM": " ║ ",
    "FORALL": "∀", "EXISTS": "∃", "EXISTS_UNIQUE": "∃!",
    "AND": "∧", "OR": "∨", "NOT": "¬", "IMPLIES": "→", "IFF": "↔",
    "LPAREN": "(", "RPAREN": ")", "COMMA": ",", "DOT": ".",
    "VX": "x", "VY": "y", "VZ": "z", "VU": "u", "VV": "v", "VW": "w",
    "VA": "a", "VB": "b", "VF": "f", "VG": "g", "VH": "h", "VN": "n",
    "IN": "∈", "EQ": "=", "SUBSETEQ": "⊆", "SUBSET": "⊂",
    "EMPTY": "∅", "OMEGA": "ω",
    "UNION": "⋃", "POWER": "𝒫", "SUCC": "σ",
    "PAIR": "pair", "SINGLETON": "{}",
    "RANK": "rank", "ORD": "Ord", "CARD": "Card", "FUNC": "func", "BIJ": "bij",
    "SEP": "sep", "REPL": "repl", "REFL": "Refl", "LCARD": "LCard",
    "FROB": "Frob", "WIND": "wind", "HOLO": "holo", "THETA": "Θ",
    "FIXPT": "fixpt", "SEQPAIR": "seqpair", "DIRECTED_EDGE": "⟨→⟩", "TAU": "τ",
    "GUE": "GUE", "CLASSIC": "cls",
    "HOLOBOUND": "⊙bound", "LR_DUAL": "lr⇔", "PM_Z2": "ℤ₂",
    "SEQAX": "seq!", "TEMPD2": "H₂", "ZWIND": "ℤwind",
}

_PROMOTION_ATOMS = {"HOLOBOUND", "LR_DUAL", "PM_Z2", "SEQAX", "TEMPD2", "ZWIND"}

def render_tokens(token_names: List[str]) -> str:
    import re
    parts = []
    for t in token_names:
        sym = _TM.get(t, t)
        if not sym:
            continue
        parts.append(sym if t in ("LPAREN", "RPAREN", "COMMA", "DOT") else f" {sym}")
    return re.sub(r"  +", " ", "".join(parts).strip())

def probe_entry(
    name:         str,
    model_path:   str  = "zfct_encoder.pt",
    catalog_path: str  = None,
    max_len:      int  = 256,
    hidden_dim:   int  = 256,
    n_layers:     int  = 4,
    no_model:     bool = False,
):
    if name in _SPECIAL_ENTRIES:
        entry = _SPECIAL_ENTRIES[name]
    else:
        catalog = load_catalog(catalog_path)
        matches = [e for e in catalog if e.get("name") == name]
        if not matches:
            matches = [e for e in catalog if name.lower() in e.get("name", "").lower()]
        if not matches:
            print(f"[entry] no entry found for '{name}'.")
            print("  Special names: " + ", ".join(sorted(_SPECIAL_ENTRIES)))
            return
        if len(matches) > 1:
            print(f"[entry] {len(matches)} fuzzy matches — using '{matches[0]['name']}'")
        entry = matches[0]

    entry = _normalize_entry(entry)
    if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
        print(f"[entry] '{entry.get('name')}' has missing or invalid primitives.")
        return

    import textwrap as _tw
    W = 80
    print("\n" + "═" * W)
    print(f"  ENTRY: {entry.get('name', '?')}")
    if desc := entry.get("description", ""):
        for line in _tw.wrap(desc, W - 4):
            print(f"  {line}")

    # Is this entry ZFCₜ-promoted?
    promoted = [(p, zv, ztv) for p, zv, ztv in ZFCT_PROMOTIONS if entry.get(p) == ztv]
    if promoted:
        print(f"  ZFCₜ promotions active: {', '.join(p + ':' + ztv for p, _, ztv in promoted)}")
    print("═" * W)

    token_ids = compose_formula(entry)

    print(f"\n  {'Prim':<5}  {'Value':<18}  ZFC fragment")
    print(f"  {'─'*5}  {'─'*18}  {'─'*51}")
    for p in PRIMITIVES:
        val  = entry[p]
        frag = ZFCT_TEMPLATES[p][val]
        rendered = render_tokens(frag)
        promo_atoms = [t for t in frag if t in _PROMOTION_ATOMS]
        tag = "  [" + "+".join(promo_atoms) + "]" if promo_atoms else ""
        print(f"  {p:<5}  {val:<18}  {rendered[:50 - len(tag)]:50}{tag}")

    # Full ZFCₜ expression
    token_names = [IDX2TOKEN[i] for i in token_ids]
    chunks, cur = [], []
    for t in token_names:
        if t == "SEP_PRIM":
            chunks.append(cur); cur = []
        elif t not in ("BOS", "EOS", "PAD"):
            cur.append(t)
    if cur:
        chunks.append(cur)
    rendered_chunks = [render_tokens(c) for c in chunks if c]
    print(f"\n── ZFCₜ expression {'─' * (W - 19)}")
    for i, frag in enumerate(rendered_chunks):
        print(f"  {frag}{' ∧' if i < len(rendered_chunks) - 1 else ''}")
    print(f"\n  tokens: {len(token_ids)}")

    if no_model:
        return

    model_p = Path(model_path)
    if not model_p.exists():
        print(f"\n[entry] model not found at {model_path} — skipping roundtrip.")
        print("  Run `uv run zfct_navigator.py train` first.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model  = ZFCtEncoder(hidden_dim=hidden_dim, n_layers=n_layers, max_len=max_len).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    with torch.no_grad():
        tokens_t  = torch.tensor([pad_formula(token_ids, max_len)],
                                  dtype=torch.long, device=device)
        targets_t = torch.tensor([tuple_to_indices(entry)],
                                  dtype=torch.long, device=device)
        logits    = model(tokens_t)
        loss, pp  = frobenius_loss(logits, targets_t)
        pred_tuple = indices_to_tuple([int(logits[i].argmax(-1).item()) for i in range(12)])
        rt_dist   = tuple_distance(entry, pred_tuple)

    print(f"\n── Roundtrip {'─' * (W - 13)}")
    mismatches = [(i, p) for i, p in enumerate(PRIMITIVES) if entry[p] != pred_tuple[p]]
    if not mismatches:
        print(f"  ✓  d_rt = {rt_dist:.4f}   loss = {float(loss):.4f}   all 12 recovered")
    else:
        print(f"  ✗  d_rt = {rt_dist:.4f}   loss = {float(loss):.4f}")
        for i, p in mismatches:
            inp  = entry[p]
            pred = pred_tuple[p]
            ppl  = float(pp[i])
            is_promo = any(p == pm and inp == ztv for pm, _, ztv in ZFCT_PROMOTIONS)
            tag = "  ← promotion collapse" if is_promo else "  ← mismatch"
            print(f"  {p:<5}  {inp:<18}  →  {pred:<18}  ✗{tag}  ({ppl:.4f})")


# ── 12. Gate-ordered A* proof path ───────────────────────────────────────────

_LAPIS_TUPLE: dict = {   # O∞ Stone — default A* target
    "name": "lapis_philosophorum",
    "Ð": "Ð_ω", "Þ": "Þ_O", "Ř": "Ř_=", "Φ": "Φ_}",
    "ƒ": "ƒ^ż", "Ç": "Ç^W", "Γ": "Γ_ʔ", "ɢ": "ɢ^Ş",
    "⊙": "⊙_ÿ", "Ħ": "Ħ_!", "Σ": "Σ_ï", "Ω": "Ω_z",
}

_GATE_ANNOTATIONS: Dict[Tuple[str, str], str] = {
    ("Φ",  "Φ_}" ): "◀ G1 fires (Frobenius gate)",
    ("⊙", "⊙_ÿ"): "◀ G2 fires (traced monoidal gate)",
    ("Ω",  "Ω_z" ): "◀ G3 fires (idempotent terminal gate)",
}


def _gate_blocked(prim: str, new_ord: int, state: dict,
                  constraints: Optional[List[Tuple[str, int, str, int]]] = None,
                  ceilings: Optional[Dict[str, int]] = None) -> bool:
    if ceilings and prim in ceilings and new_ord > ceilings[prim]:
        return True
    for gated, min_ord, prereq, prereq_min in (constraints if constraints is not None else GATE_CONSTRAINTS):
        if prim == gated and new_ord >= min_ord:
            if ORDINALS[prereq].get(state.get(prereq, ""), -1) < prereq_min:
                return True
    return False


def _path_successors(state: dict,
                     constraints: Optional[List[Tuple[str, int, str, int]]] = None,
                     ceilings: Optional[Dict[str, int]] = None,
                     ) -> List[Tuple[dict, str, float]]:
    result = []
    for p in PRIMITIVES:
        curr_ord = ORDINALS[p][state[p]]
        for new_ord in (curr_ord - 1, curr_ord + 1):
            if new_ord < 0 or new_ord >= len(ORDINALS[p]):
                continue
            if _gate_blocked(p, new_ord, state, constraints, ceilings):
                continue
            ns = dict(state)
            ns[p] = INV_ORDINALS[p][new_ord]
            direction = "↑" if new_ord > curr_ord else "↓"
            label = f"{p}: {state[p]} → {ns[p]} {direction}"
            result.append((ns, label, WEIGHTS[p]))
    return result


def _path_h(state: dict, target: dict) -> float:
    return sum(WEIGHTS[p] * abs(ORDINALS[p][state[p]] - ORDINALS[p][target[p]])
               for p in PRIMITIVES)


def astar_path(
    source: dict,
    target: dict,
    constraints: Optional[List[Tuple[str, int, str, int]]] = None,
    ceilings: Optional[Dict[str, int]] = None,
) -> Optional[Tuple[List[dict], List[str], float]]:
    """Gate-ordered A* from source to target.

    Returns (state_sequence, step_labels, total_cost) or None if unreachable.
    Gate constraints enforce G1→G2→G3 operad layer ordering by default.
    Pass constraints=[] to disable. ceilings hard-blocks any move past a primitive ceiling.
    """
    def key(s: dict) -> tuple:
        return tuple(s[p] for p in PRIMITIVES)

    sk, gk = key(source), key(target)
    if sk == gk:
        return ([dict(source)], [], 0.0)

    _ctr = [0]
    def ctr() -> int:
        _ctr[0] += 1
        return _ctr[0]

    h0 = _path_h(source, target)
    heap: list = [(h0, 0.0, ctr(), source)]
    g_score: Dict[tuple, float] = {sk: 0.0}
    parent: Dict[tuple, Tuple[Optional[tuple], Optional[str]]] = {sk: (None, None)}

    while heap:
        _, g, _, state = heapq.heappop(heap)
        cur = key(state)
        if cur == gk:
            labels: List[str] = []
            k = cur
            while parent[k][0] is not None:
                labels.append(parent[k][1])   # type: ignore[arg-type]
                k = parent[k][0]              # type: ignore[assignment]
            labels.reverse()
            states = [dict(source)]
            cur_s = dict(source)
            for lbl in labels:
                prim, rest = lbl.split(": ", 1)
                _, new_v = rest.split(" → ", 1)
                new_v = new_v.rstrip(" ↑↓")
                cur_s = dict(cur_s)
                cur_s[prim] = new_v
                states.append(cur_s)
            return (states, labels, g)
        if g > g_score.get(cur, float("inf")) + 1e-9:
            continue
        for ns, label, cost in _path_successors(state, constraints, ceilings):
            nk = key(ns)
            ng = g + cost
            if ng < g_score.get(nk, float("inf")):
                g_score[nk] = ng
                parent[nk] = (cur, label)
                nh = ng + _path_h(ns, target)
                heapq.heappush(heap, (nh, ng, ctr(), ns))
    return None


def cmd_path(
    source_name: str,
    target_name: str = "lapis",
    catalog_path: Optional[str] = None,
    no_gate: bool = False,
) -> None:
    """Display gate-ordered A* proof path from source to target."""
    special = dict(_SPECIAL_ENTRIES)
    special["lapis"] = _LAPIS_TUPLE

    catalog = load_catalog(catalog_path)

    def resolve(name: str) -> Optional[dict]:
        if name in special:
            return special[name]
        matches = [e for e in catalog if e.get("name") == name]
        if not matches:
            matches = [e for e in catalog if name.lower() in e.get("name", "").lower()]
        return matches[0] if matches else None

    src = resolve(source_name)
    tgt = resolve(target_name)
    if src is None:
        print(f"[path] source '{source_name}' not found.")
        return
    if tgt is None:
        print(f"[path] target '{target_name}' not found.")
        return

    src = _normalize_entry(src)
    tgt = _normalize_entry(tgt)
    if not all(p in src and src[p] in ORDINALS[p] for p in PRIMITIVES):
        print("[path] source has missing/invalid primitives.")
        return
    if not all(p in tgt and tgt[p] in ORDINALS[p] for p in PRIMITIVES):
        print("[path] target has missing/invalid primitives.")
        return

    constraints: Optional[List[Tuple[str, int, str, int]]] = [] if no_gate else None

    W = 80
    print(f"\n{'═'*W}")
    print(f"  GATE-ORDERED PROOF PATH")
    print(f"  source: {src.get('name', source_name)}")
    print(f"  target: {tgt.get('name', target_name)}")
    print(f"  d_start = {tuple_distance(src, tgt):.4f}"
          + ("   [gate constraints disabled]" if no_gate else ""))
    print(f"{'═'*W}")

    result = astar_path(src, tgt, constraints)
    if result is None:
        print("  No path found (gate constraints may block; try --no-gate).")
        return

    states, labels, cost = result
    print(f"  Steps: {len(labels)}   Total cost: {cost:.4f}\n")
    print(f"  {'Step':<5} {'Move':<42} {'Operad layer':<22} {'T-dist':>8}")
    print(f"  {'─'*5} {'─'*42} {'─'*22} {'─'*8}")

    prev_layer = operad_layer(states[0])
    td0 = t_fiber_distance(states[0])
    td0_str = f"{td0:.4f}" if td0 != float("inf") else "     ∞"
    print(f"  {'[src]':<5} {'—':<42} {prev_layer:<22} {td0_str:>8}")

    for i, (label, state) in enumerate(zip(labels, states[1:]), 1):
        layer = operad_layer(state)
        td = t_fiber_distance(state)
        td_str = f"{td:.4f}" if td != float("inf") else "     ∞"

        prim = label.split(": ", 1)[0]
        new_v = label.split(" → ", 1)[1].rstrip(" ↑↓")
        gate_ann = _GATE_ANNOTATIONS.get((prim, new_v), "")

        layer_str = f"→ {layer}" if layer != prev_layer else layer
        prev_layer = layer
        move_col = label[:42]
        print(f"  {i:<5} {move_col:<42} {layer_str:<22} {td_str:>8}  {gate_ann}")

    print()
    final = states[-1]
    tc = t_consistency(final)
    print(f"  Final operad layer:   {operad_layer(final)}")
    print(f"  Final T-fiber dist:   {tc['t_fiber_distance']}")
    print(f"  T-consistent:         {tc['t_consistent']}")
    if tc["ç_forecloses_t"]:
        print(f"  ⚠  Ç forecloses T (frozen kinetics — T cannot seal)")


def cmd_operad(
    catalog_path: Optional[str] = None,
    layer_filter: Optional[str] = None,
) -> None:
    """Census catalog by operad layer; list entries at a specific layer."""
    catalog = load_catalog(catalog_path)
    counts: Dict[str, int] = {
        "plain": 0, "frobenius": 0, "traced_monoidal": 0, "idempotent_terminal": 0
    }
    rows: List[Tuple[str, str, float]] = []
    for entry in catalog:
        entry = _normalize_entry(entry)
        if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
            continue
        layer = operad_layer(entry)
        counts[layer] = counts.get(layer, 0) + 1
        if layer_filter is None or layer == layer_filter:
            rows.append((entry.get("name", "?"), layer, t_fiber_distance(entry)))

    W = 80
    print(f"\n{'═'*W}")
    print("  OPERAD LAYER CENSUS")
    print(f"{'═'*W}")
    print(f"  plain:               {counts['plain']:>6}")
    print(f"  frobenius:           {counts['frobenius']:>6}")
    print(f"  traced_monoidal:     {counts['traced_monoidal']:>6}")
    print(f"  idempotent_terminal: {counts['idempotent_terminal']:>6}")
    if layer_filter and rows:
        print(f"\n  Entries at layer '{layer_filter}'  (sorted by T-fiber dist):")
        print(f"  {'─'*W}")
        print(f"  {'Name':<46} {'T-dist':>8}")
        print(f"  {'─'*46} {'─'*8}")
        for name, _, td in sorted(rows, key=lambda x: x[2]):
            td_str = f"{td:.4f}" if td != float("inf") else "     ∞"
            print(f"  {name[:46]:<46} {td_str:>8}")


def cmd_t(
    catalog_path: Optional[str] = None,
    name: Optional[str] = None,
    top_n: int = 20,
) -> None:
    """T-fiber consistency: single-entry analysis or full catalog census."""
    catalog = load_catalog(catalog_path)
    ref_names = {e.get("name") for e in _SPECIAL_ENTRIES.values()}
    all_entries = list(_SPECIAL_ENTRIES.values()) + [
        e for e in catalog if e.get("name") not in ref_names
    ]

    W = 80

    if name:
        matches = [e for e in all_entries if e.get("name") == name]
        if not matches:
            matches = [e for e in all_entries if name.lower() in e.get("name", "").lower()]
        if not matches:
            print(f"[t] '{name}' not found.")
            return
        entry = _normalize_entry(matches[0])
        tc = t_consistency(entry)
        print(f"\n{'═'*W}")
        print(f"  T-MANIFOLD ANALYSIS: {entry.get('name', '?')}")
        print(f"  operad layer: {operad_layer(entry)}")
        print(f"{'═'*W}")
        print(f"  T-fiber distance:  {tc['t_fiber_distance']}")
        print(f"  T-consistent:      {tc['t_consistent']}")
        if tc["ç_forecloses_t"]:
            print(f"  ⚠  Ç forecloses T — kinetics frozen, T cannot seal")
        print(f"\n  {'Prim':<6} {'Value':<12} {'Target':<12} {'Gap':>5}  Status")
        print(f"  {'─'*6} {'─'*12} {'─'*12} {'─'*5}  {'─'*20}")
        for p, info in tc["primitives"].items():
            gap_str = f"{info['gap']:+d}" if info["gap"] is not None else "?"
            sym = "✓" if info["status"] == "sealed" else (
                "✗" if "forecloses" in info.get("status", "") else "·")
            print(f"  {p:<6} {info['value']:<12} {info['target']:<12} {gap_str:>5}  {sym} {info['status']}")
        return

    rows: List[Tuple[str, dict]] = []
    for entry in all_entries:
        entry = _normalize_entry(entry)
        if not all(p in entry and entry[p] in ORDINALS[p] for p in PRIMITIVES):
            continue
        rows.append((entry.get("name", "?"), t_consistency(entry)))

    consistent = sum(1 for _, tc in rows if tc["t_consistent"])
    forecloses  = sum(1 for _, tc in rows if tc["ç_forecloses_t"])
    rows_sorted = sorted(rows, key=lambda r: r[1]["t_fiber_distance"])

    print(f"\n{'═'*W}")
    print(f"  T-FIBER CENSUS   ({len(rows)} entries)")
    print(f"{'═'*W}")
    print(f"  T-consistent (d=0, Ç ok):  {consistent}")
    print(f"  Ç forecloses T:            {forecloses}")
    print(f"\n  {'Name':<42} {'T-dist':>8}  {'Ç-ok':>5}  {'T-ok':>5}")
    print(f"  {'─'*42} {'─'*8}  {'─'*5}  {'─'*5}")
    for n, tc in rows_sorted[:top_n]:
        td = tc["t_fiber_distance"]
        td_str = f"{td:.4f}" if td != float("inf") else "     ∞"
        c_ok = "✓" if not tc["ç_forecloses_t"] else "✗"
        t_ok = "✓" if tc["t_consistent"] else "·"
        print(f"  {n[:42]:<42} {td_str:>8}  {c_ok:>5}  {t_ok:>5}")


def t_sealed_prims(entry: dict) -> List[str]:
    """Return list of T-primitives that have reached their critical value in entry."""
    sealed = []
    for p in T_PRIMITIVES:
        v = entry.get(p, "")
        if p == "Ç":
            ord_v = ORDINALS[p].get(v, -1)
            ord_c = ORDINALS[p][T_CRITICAL[p]]
            if 0 <= ord_v <= ord_c:
                sealed.append(p)
        else:
            if v == T_CRITICAL[p]:
                sealed.append(p)
    return sealed


def cmd_tpath(
    source_name: str,
    target_name: str = "lapis",
    catalog_path: Optional[str] = None,
) -> None:
    """T-consistent proof path: gate-ordered A* + Ħ_! after G2 + Ç ceiling at Ç^@."""
    special = dict(_SPECIAL_ENTRIES)
    special["lapis"] = _LAPIS_TUPLE

    catalog = load_catalog(catalog_path)

    def resolve(name: str) -> Optional[dict]:
        if name in special:
            return special[name]
        matches = [e for e in catalog if e.get("name") == name]
        if not matches:
            matches = [e for e in catalog if name.lower() in e.get("name", "").lower()]
        return matches[0] if matches else None

    src = resolve(source_name)
    tgt = resolve(target_name)
    if src is None:
        print(f"[tpath] source '{source_name}' not found.")
        return
    if tgt is None:
        print(f"[tpath] target '{target_name}' not found.")
        return

    src = _normalize_entry(src)
    tgt = _normalize_entry(tgt)
    if not all(p in src and src[p] in ORDINALS[p] for p in PRIMITIVES):
        print("[tpath] source has missing/invalid primitives.")
        return
    if not all(p in tgt and tgt[p] in ORDINALS[p] for p in PRIMITIVES):
        print("[tpath] target has missing/invalid primitives.")
        return

    W = 80
    print(f"\n{'═'*W}")
    print(f"  T-CONSISTENT PROOF PATH  (T = Work(T) temporal bootstrap)")
    print(f"  source: {src.get('name', source_name)}")
    print(f"  target: {tgt.get('name', target_name)}")
    print(f"  constraints: G1→G2→G3 ordering  +  Ħ_! after G2  +  Ç ≤ Ç^@ ceiling")
    print(f"  d_start = {tuple_distance(src, tgt):.4f}")
    print(f"{'═'*W}")

    result = astar_path(src, tgt, T_PATH_GATE_CONSTRAINTS, T_PATH_CEILINGS)
    if result is None:
        print("  No T-consistent path found.")
        print("  Possible causes: source has Ç > Ç^@ (forecloses T), or target requires")
        print("  Ħ_! before G2 can fire. Try 'path' for unconstrained gate ordering.")
        return

    states, labels, cost = result
    print(f"  Steps: {len(labels)}   Total cost: {cost:.4f}\n")

    header = f"  {'Step':<5} {'Move':<38} {'Operad layer':<22} {'T-sealed':>10}"
    print(header)
    print(f"  {'─'*5} {'─'*38} {'─'*22} {'─'*10}")

    prev_layer = operad_layer(states[0])
    sealed0 = t_sealed_prims(states[0])
    sealed0_str = ",".join(sealed0) if sealed0 else "—"
    print(f"  {'[src]':<5} {'—':<38} {prev_layer:<22} {sealed0_str:>10}")

    t_seal_step: Optional[int] = None
    prev_sealed = set(sealed0)

    for i, (label, state) in enumerate(zip(labels, states[1:]), 1):
        layer = operad_layer(state)
        sealed = t_sealed_prims(state)
        sealed_set = set(sealed)
        sealed_str = ",".join(sealed) if sealed else "—"

        prim = label.split(": ", 1)[0]
        new_v = label.split(" → ", 1)[1].rstrip(" ↑↓")
        gate_ann = _GATE_ANNOTATIONS.get((prim, new_v), "")

        layer_str = f"→ {layer}" if layer != prev_layer else layer
        prev_layer = layer

        # Track T-seal moment: first step where all 5 T-prims are sealed
        newly_sealed = sealed_set - prev_sealed
        is_t_seal = (len(sealed_set) == len(T_PRIMITIVES) and
                     len(prev_sealed) < len(T_PRIMITIVES))
        prev_sealed = sealed_set
        if is_t_seal and t_seal_step is None:
            t_seal_step = i
            gate_ann = "◀ T = Work(T) — temporal bootstrap complete"

        move_col = label[:38]
        print(f"  {i:<5} {move_col:<38} {layer_str:<22} {sealed_str:>10}  {gate_ann}")

    print()
    final = states[-1]
    tc = t_consistency(final)
    print(f"  Final operad layer:    {operad_layer(final)}")
    print(f"  Final T-fiber dist:    {tc['t_fiber_distance']}")
    print(f"  T-consistent:          {tc['t_consistent']}")
    if t_seal_step is not None:
        print(f"  T-seal moment:         step {t_seal_step}  (T = Work(T) first satisfied)")
    else:
        final_sealed = t_sealed_prims(final)
        missing = [p for p in T_PRIMITIVES if p not in final_sealed]
        print(f"  T-seal moment:         not reached  (missing: {', '.join(missing)})")
    if tc["ç_forecloses_t"]:
        print(f"  ⚠  Ç forecloses T (frozen kinetics — path is T-inconsistent)")


# ── 13. Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ZFCₜ Navigator — 6-channel promotion probe for ZFCₜ-regime entries"
    )
    sub = parser.add_subparsers(dest="cmd")

    tr = sub.add_parser("train")
    tr.add_argument("--epochs",  type=int,   default=300)
    tr.add_argument("--batch",   type=int,   default=64)
    tr.add_argument("--lr",      type=float, default=3e-4)
    tr.add_argument("--hidden",  type=int,   default=256)
    tr.add_argument("--layers",  type=int,   default=4)
    tr.add_argument("--catalog", type=str,   default=None)
    tr.add_argument("--save",    type=str,   default="zfct_encoder.pt")

    pr = sub.add_parser("probe")
    pr.add_argument("--model",   type=str, default="zfct_encoder.pt")
    pr.add_argument("--catalog", type=str, default=None)
    pr.add_argument("--top",     type=int, default=20)
    pr.add_argument("--hidden",  type=int, default=256)
    pr.add_argument("--layers",  type=int, default=4)

    pm = sub.add_parser("promotions")
    pm.add_argument("--model",   type=str, default="zfct_encoder.pt")
    pm.add_argument("--hidden",  type=int, default=256)
    pm.add_argument("--layers",  type=int, default=4)

    en = sub.add_parser("entry")
    en.add_argument("name",       type=str)
    en.add_argument("--model",    type=str, default="zfct_encoder.pt")
    en.add_argument("--catalog",  type=str, default=None)
    en.add_argument("--hidden",   type=int, default=256)
    en.add_argument("--layers",   type=int, default=4)
    en.add_argument("--no-model", action="store_true")

    pa = sub.add_parser("path", help="Gate-ordered A* proof path between two crystal addresses")
    pa.add_argument("source",    type=str, help="Source entry name (or special key)")
    pa.add_argument("--target",  type=str, default="lapis",
                    help="Target entry name (default: lapis_philosophorum / O∞ Stone)")
    pa.add_argument("--catalog", type=str, default=None)
    pa.add_argument("--no-gate", action="store_true",
                    help="Disable G1→G2→G3 gate ordering constraints")

    op = sub.add_parser("operad", help="Census catalog by monoidal operad layer")
    op.add_argument("--catalog", type=str, default=None)
    op.add_argument("--layer",   type=str, default=None,
                    choices=["plain", "frobenius", "traced_monoidal", "idempotent_terminal"],
                    help="Filter to a specific operad layer")

    tf = sub.add_parser("t", help="T-fiber consistency analysis (T = lim(Φ,ƒ,Ç,Ħ,Ω))")
    tf.add_argument("--name",    type=str, default=None, help="Analyse a specific entry")
    tf.add_argument("--catalog", type=str, default=None)
    tf.add_argument("--top",     type=int, default=20, help="Show top N entries by T-dist")

    tp = sub.add_parser("tpath", help="T-consistent proof path (gate-ordered + Ħ after G2 + Ç ceiling)")
    tp.add_argument("source",    type=str, help="Source entry name (or special key)")
    tp.add_argument("--target",  type=str, default="lapis",
                    help="Target entry name (default: lapis_philosophorum / O∞ Stone)")
    tp.add_argument("--catalog", type=str, default=None)

    args = parser.parse_args()

    if args.cmd == "train":
        train(catalog_path=args.catalog, n_epochs=args.epochs, batch_size=args.batch,
              lr=args.lr, hidden_dim=args.hidden, n_layers=args.layers, save_path=args.save)
    elif args.cmd == "probe":
        run_probe(catalog_path=args.catalog, model_path=args.model,
                  top_n=args.top, hidden_dim=args.hidden, n_layers=args.layers)
    elif args.cmd == "promotions":
        probe_promotions(model_path=args.model, hidden_dim=args.hidden, n_layers=args.layers)
    elif args.cmd == "entry":
        probe_entry(name=args.name, model_path=args.model, catalog_path=args.catalog,
                    hidden_dim=args.hidden, n_layers=args.layers, no_model=args.no_model)
    elif args.cmd == "path":
        cmd_path(args.source, args.target, args.catalog, args.no_gate)
    elif args.cmd == "operad":
        cmd_operad(args.catalog, args.layer)
    elif args.cmd == "t":
        cmd_t(args.catalog, args.name, args.top)
    elif args.cmd == "tpath":
        cmd_tpath(args.source, args.target, args.catalog)
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  uv run zfct_navigator.py train")
        print("  uv run zfct_navigator.py promotions  --no-model  # formula analysis without training")
        print("  uv run zfct_navigator.py entry zfc_t --no-model")
        print("  uv run zfct_navigator.py entry navier_stokes --no-model")
        print("  uv run zfct_navigator.py path zfc_t            # gate-ordered path to O∞ Stone")
        print("  uv run zfct_navigator.py operad --layer frobenius")
        print("  uv run zfct_navigator.py t --name voynich_manuscript")
        print("  uv run zfct_navigator.py tpath zfc_t           # T-consistent path (Ħ after G2, Ç ceiling)")
        print("\nZFCₜ special entries:", ", ".join(sorted(_SPECIAL_ENTRIES)))
