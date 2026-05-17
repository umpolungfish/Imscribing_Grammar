#!/usr/bin/env python3
"""
zfct_navigator.py — ZFCₜ formula navigator with 6-channel promotion probe.

ZFCₜ extends ZFC via six primitive promotions (from MillenniumAnkh/Primitives/ZFCt.lean):
  Þ_6 → Þ_O   T_network → T_odot      holographic topology
  Ř_¯ → Ř_=   R_super   → R_lr        lateral relational mode
  Φ_ɐ → Φ_F   P_asym    → P_pm        ℤ₂ discrete symmetry
  ɢ_^ → ɢ_ˌ   Gamma_and  → Gamma_seq   sequential composition
  Ħ_Ñ → Ħ_A   H0        → H2          persistent temporal asymmetry
  Ω_Å → Ω_z   Omega_0   → Omega_Z     integer winding number

Each promotion corresponds to a recovery channel in the ZFCₜ specialist router.
The 4 ZFC collapse channels (ƒ, Þ, Ð, ɢ) are subsumed and extended to 7.

ZFCₜ tier: O_2† (Phi_c + Omega_Z + D_infty) — below O_inf (Frobenius cliff).

Run:
    uv run zfct_navigator.py train
    uv run zfct_navigator.py probe
    uv run zfct_navigator.py entry zfc_t
    uv run zfct_navigator.py promotions      # probe the 6 ZFCₜ promotion channels
    uv run zfct_navigator.py recover
"""

import argparse
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

PRIMITIVES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"]

ORDINALS: Dict[str, Dict[str, float]] = {
    "Ð":  {"Ð_ß": 0, "Ð_C": 1, "Ð_;": 2, "Ð_ω": 3},
    "Þ":  {"Þ_6": 0, "Þ_K": 1, "Þ_ò": 2, "Þ_¨": 3, "Þ_O": 4},
    "Ř":  {"Ř_¯": 0, "Ř_ý": 1, "Ř_Ť": 2, "Ř_=": 3},
    "Φ":  {"Φ_ɐ": 0, "Φ_υ": 1, "Φ_F": 2, "Φ_˙": 3, "Φ_}": 4},
    "ƒ":  {"ƒ_ì": 0, "ƒ_ð": 1, "ƒ_ż": 2},
    "Ç":  {"Ç_-": 0, "Ç_W": 1, "Ç_@": 2, "Ç_Ù": 3, "Ç_λ": 4},
    "Γ":  {"Γ_β": 0, "Γ_γ": 1, "Γ_ʔ": 2},
    "ɢ":  {"ɢ_^": 0, "ɢ_˝": 1, "ɢ_ˌ": 2, "ɢ_Ş": 3},
    "φ̂": {"φ̂_ž": 0, "φ̂_ÿ": 1, "φ̂_Æ": 2, "φ̂_3": 3, "φ̂_Ţ": 4},
    "Ħ":  {"Ħ_Ñ": 0, "Ħ_£": 1, "Ħ_A": 2, "Ħ_!": 3},
    "Σ":  {"Σ_S": 0, "Σ_ő": 1, "Σ_ï": 2},
    "Ω":  {"Ω_Å": 0, "Ω_2": 1, "Ω_z": 2, "Ω_5": 3},
}

WEIGHTS = {
    "Ð": 1.0, "Þ": 1.2, "Ř": 1.0, "Φ": 1.0,
    "ƒ": 0.9, "Ç": 1.0, "Γ": 1.0, "ɢ": 1.2,
    "φ̂": 1.1, "Ħ": 1.2, "Σ": 0.8, "Ω": 1.2,
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


# ── 2. ZFCₜ Token Vocabulary ─────────────────────────────────────────────────
#
# ZFC_VOCAB from zfc_navigator + 6 ZFCₜ-specific atoms:
#   HOLOBOUND  holographic boundary/bulk encoding  → Þ_O  (stronger than HOLO)
#   LR_DUAL    lateral relational duality          → Ř_=
#   PM_Z2      ℤ₂ parity marker                   → Φ_F
#   SEQAX      sequentiality axiom                 → ɢ_ˌ
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
    "SEQAX",        # sequentiality axiom — ɢ_ˌ (Gamma_seq)
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
        "ƒ_ì":  ["CLASSIC", "VX"],
        "ƒ_ð":  ["EXISTS", "VY", "LPAREN",
                 "VY", "EQ", "VX", "AND", "VY", "IN", "OMEGA", "RPAREN"],
        # ⚠ TOTAL COLLAPSE: ƒ_ż → identical CLASSIC token as ƒ_ì
        "ƒ_ż":  ["CLASSIC", "VX"],
    },
    "Ç": {
        "Ç_-":  ["EXISTS", "VY", "LPAREN", "SUCC", "VY", "EQ", "VX", "RPAREN"],
        "Ç_W":  ["EXISTS", "VY", "EXISTS", "VZ", "LPAREN",
                 "VY", "IN", "VX", "AND", "VZ", "IN", "VX", "AND", "VY", "SUBSETEQ", "VZ", "RPAREN"],
        "Ç_@":  ["FORALL", "VY", "LPAREN",
                 "VY", "SUBSETEQ", "VX", "IMPLIES",
                 "EXISTS", "VZ", "LPAREN", "VZ", "IN", "VX", "AND", "VY", "SUBSETEQ", "VZ",
                 "RPAREN", "RPAREN"],
        "Ç_Ù":  ["FIXPT", "VF"],
        "Ç_λ":  ["FORALL", "VY", "FORALL", "VZ", "LPAREN",
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
        "ɢ_^":  ["AND"],
        "ɢ_˝":  ["OR"],
        # ZFCₜ promotion: SEQAX prefix + DIRECTED_EDGE+TAU (ZFCₜ axiom for causal ordering)
        "ɢ_ˌ":  ["SEQAX", "VF", "VG", "AND",
                 "DIRECTED_EDGE", "VF", "VG", "TAU",
                 "AND", "NOT", "DIRECTED_EDGE", "VG", "VF", "TAU"],
        "ɢ_Ş":  ["FORALL", "VY", "LPAREN", "VF", "VY", "RPAREN"],
    },
    "φ̂": {
        "φ̂_ž":  ["EXISTS", "VY", "LPAREN",
                 "VY", "IN", "VX", "AND", "RANK", "VY", "SUBSET", "RANK", "VX", "RPAREN"],
        "φ̂_ÿ":  ["FIXPT", "VF"],
        "φ̂_Æ":  ["GUE", "VX", "AND", "FIXPT", "VF"],
        "φ̂_3":  ["LCARD", "VA", "AND", "FIXPT", "VF"],
        "φ̂_Ţ":  ["FORALL", "VY", "LPAREN",
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
    "description": "Zermelo-Fraenkel set theory with Choice (ZFC baseline)",
    "Ð": "Ð_C", "Þ": "Þ_K", "Ř": "Ř_¯", "Φ": "Φ_˙",
    "ƒ": "ƒ_ì", "Ç": "Ç_@", "Γ": "Γ_β", "ɢ": "ɢ_^",
    "φ̂": "φ̂_ž", "Ħ": "Ħ_Ñ", "Σ": "Σ_S", "Ω": "Ω_Å",
}

ZFCT_TUPLE = {
    "name": "zfc_t",
    "description": "ZFCₜ: ZFC + sequential + chirality + winding (ZFCt.lean)",
    "Ð": "Ð_;",   # D_infty
    "Þ": "Þ_O",   # T_odot   ← ZFCₜ promotion
    "Ř": "Ř_=",   # R_lr     ← ZFCₜ promotion
    "Φ": "Φ_F",   # P_pm     ← ZFCₜ promotion
    "ƒ": "ƒ_ż",   # F_hbar
    "Ç": "Ç_@",   # K_slow
    "Γ": "Γ_ʔ",   # G_aleph
    "ɢ": "ɢ_ˌ",   # Gamma_seq  ← ZFCₜ promotion
    "φ̂": "φ̂_ÿ",  # Phi_c
    "Ħ": "Ħ_A",   # H2       ← ZFCₜ promotion
    "Σ": "Σ_ï",   # n_m
    "Ω": "Ω_z",   # Omega_Z  ← ZFCₜ promotion
}

TEMPORAL_MATHEMATICS_TUPLE = {
    "name": "temporal_mathematics",
    "description": "Temporal mathematics (ZFCt.lean: temporal_mathematics)",
    "Ð": "Ð_;",  "Þ": "Þ_O",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ_ż",  "Ç": "Ç_@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_ÿ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

SCHRODINGER_TUPLE = {
    "name": "schrodinger_equation",
    "description": "Schrödinger equation (ZFCt.lean: schrodinger_equation)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_=",  "Φ": "Φ_υ",
    "ƒ": "ƒ_ż",  "Ç": "Ç_@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_Æ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

HEAT_DIFFUSION_TUPLE = {
    "name": "heat_diffusion_equation",
    "description": "Heat diffusion equation (ZFCt.lean: heat_diffusion_equation)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_Ť",  "Φ": "Φ_ɐ",
    "ƒ": "ƒ_ð",  "Ç": "Ç_@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_ž", "Ħ": "Ħ_£",  "Σ": "Σ_ï",  "Ω": "Ω_Å",
}

NAVIER_STOKES_TUPLE = {
    "name": "navier_stokes_equations",
    "description": "Navier-Stokes equations (ZFCt.lean: navier_stokes_equations)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_=",  "Φ": "Φ_F",
    "ƒ": "ƒ_ì",  "Ç": "Ç_W",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_ÿ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

WAVE_EQUATION_TUPLE = {
    "name": "wave_equation_temporal",
    "description": "Wave equation (ZFCt.lean: wave_equation_temporal)",
    "Ð": "Ð_;",  "Þ": "Þ_ò",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ_ì",  "Ç": "Ç_W",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_ž", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_Å",
}

EINSTEIN_TUPLE = {
    "name": "einstein_field_equations_dynamic",
    "description": "Einstein field equations dynamic (ZFCt.lean)",
    "Ð": "Ð_;",  "Þ": "Þ_O",  "Ř": "Ř_Ť",  "Φ": "Φ_˙",
    "ƒ": "ƒ_ì",  "Ç": "Ç_@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_Æ", "Ħ": "Ħ_A",  "Σ": "Σ_ï",  "Ω": "Ω_z",
}

IUG_TUPLE = {
    "name": "IUG_mochizuki",
    "description": "Inter-Universal Teichmüller Theory (Mochizuki)",
    "Ð": "Ð_ω",  "Þ": "Þ_O",  "Ř": "Ř_=",  "Φ": "Φ_}",
    "ƒ": "ƒ_ż",  "Ç": "Ç_@",  "Γ": "Γ_ʔ",  "ɢ": "ɢ_ˌ",
    "φ̂": "φ̂_ÿ", "Ħ": "Ħ_!",  "Σ": "Σ_ï",  "Ω": "Ω_z",
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
    ("ɢ", "ɢ_^", "ɢ_ˌ"),   # Gamma_and → Gamma_seq
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
    # ɢ-channel: sequential composition — SEQAX+DIRECTED_EDGE+TAU → ɢ_ˌ
    ZFCtSlot("ɢ_recovery",  "ɢ",  ["SEQAX", "DIRECTED_EDGE", "TAU"],      "ɢ_^",  "ɢ_ˌ",  1),
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
    ZFCtSlot("ƒ_recovery",  "ƒ",  ["CLASSIC", "FROB", "FIXPT", "HOLO"],   "ƒ_ì",  "ƒ_ż",  6),
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
    print(f"  ZFCₜ tier:   O_2†  (Phi_c + Omega_Z + D_infty — below Frobenius cliff)")

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


# ── 12. Main ──────────────────────────────────────────────────────────────────

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
    else:
        parser.print_help()
        print("\nQuick start:")
        print("  uv run zfct_navigator.py train")
        print("  uv run zfct_navigator.py promotions  --no-model  # formula analysis without training")
        print("  uv run zfct_navigator.py entry zfc_t --no-model")
        print("  uv run zfct_navigator.py entry navier_stokes --no-model")
        print("\nZFCₜ special entries:", ", ".join(sorted(_SPECIAL_ENTRIES)))
