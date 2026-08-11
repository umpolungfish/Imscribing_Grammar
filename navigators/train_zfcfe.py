#!/usr/bin/env python3
"""
train_zfcfe.py — Training loop for ZFC_fe encoder.

Trains a transformer-based encoder on the IG catalog (2,861+ entries)
to predict the 12 primitive values from ZFC_fe formula token sequences.

ZFC_fe encodes 7 promotion channels from ZFC baseline:
  HOLOGRAPHIC_STATE  (𐑦)     — Axiom C: self-written state space
  HOLOBOUND          (𐑸)     — holographic topology  
  LR_DUAL            (𐑾)       — lateral relational duality
  PM_Z2              (𐑹)   — Frobenius-special ℤ₂ with μ∘δ=id
  SEQAX              (𐑠)  — sequential composition
  PHI_C              (⊙)      — critical self-modeling gate
  ETERNAL_FIXEDPOINT (𐑫)      — transfinite fixed-point induction
  ZWIND              (𐑭)    — integer winding number

Usage:
    python train_zfcfe.py                    # train with defaults
    python train_zfcfe.py --epochs 500       # more epochs
    python train_zfcfe.py --no-catalog       # train on built-in systems only
    python train_zfcfe.py --save zfcfe_encoder_v2.pt
"""

from __future__ import annotations
import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Path bootstrap
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

from zfcfe_navigator import (
    ZFC_FE_FORMULAE, ZFC_FE as ZFC_FE_TUPLE, PRIMITIVE_KEYS, ORDINALS,
    PRIMITIVE_NOTATION, KNOWN_SYSTEMS, CATALOG_INDEX, load_catalog,
    resolve_system, generate_formula, tuple_to_notation,
)

# Which card this run owns comes from IG_DEVICES, the one spelling for device
# selection across every repo here (see framework/ig_devices.py).
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent.parent))
from framework.ig_devices import torch_device as _ig_torch_device

DEVICE = _ig_torch_device()

# ══════════════════════════════════════════════════════════════════════════════
# ZFC_fe TOKEN VOCABULARY
# ══════════════════════════════════════════════════════════════════════════════

# Extract all unique formula tokens from ZFC_FE_FORMULAE
def build_vocabulary() -> Dict[str, int]:
    """Build token→idx vocabulary from all ZFC_fe formula fragments."""
    tokens: List[str] = []
    # Collect all tokens from formula fragments
    raw_tokens: set = set()
    for prim_key in PRIMITIVE_KEYS:
        formula_map = ZFC_FE_FORMULAE.get(prim_key, {})
        for val_key, (fragment, atom) in formula_map.items():
            toks = re.split(r'[\s(),{}]+', fragment)
            for t in toks:
                t = t.strip()
                if t:
                    raw_tokens.add(t)
            if atom:
                raw_tokens.add(atom)

    # Sort for determinism
    sorted_tokens = sorted(raw_tokens)

    # Build vocabulary with special tokens
    vocab: Dict[str, int] = {
        '<PAD>': 0,
        '<BOS>': 1,
        '<EOS>': 2,
        '<SEP>': 3,
    }
    for i, t in enumerate(sorted_tokens, start=4):
        vocab[t] = i

    return vocab

VOCAB = build_vocabulary()
VOCAB_SIZE = len(VOCAB)
IDX2TOKEN = {v: k for k, v in VOCAB.items()}
PAD_IDX = VOCAB['<PAD>']
BOS_IDX = VOCAB['<BOS>']
EOS_IDX = VOCAB['<EOS>']
SEP_IDX = VOCAB['<SEP>']

# Promoted atoms for the 7 ZFC_fe channels
ZFC_FE_PROMOTED_ATOMS = [
    "HOLOGRAPHIC_STATE",  # 𐑦
    "HOLOBOUND",          # 𐑸
    "LR_DUAL",            # 𐑾
    "PM_Z2",              # 𐑹
    "SEQAX",              # 𐑠
    "PHI_C",              # ⊙
    "ETERNAL_FIXEDPOINT", # 𐑫
    "ZWIND",              # 𐑭
]

# ══════════════════════════════════════════════════════════════════════════════
# FORMULA → TOKEN SEQUENCE
# ══════════════════════════════════════════════════════════════════════════════

def formula_to_tokens(entry_tuple: dict, max_len: int = 256) -> List[int]:
    """Convert a 12-tuple to a ZFC_fe token sequence."""
    tokens = [BOS_IDX]
    for prim_key in PRIMITIVE_KEYS:
        val = entry_tuple.get(prim_key)
        formula_map = ZFC_FE_FORMULAE.get(prim_key, {})
        if val in formula_map:
            fragment, atom = formula_map[val]
            # Tokenize fragment
            frag_toks = []
            for t in re.split(r'[\s(),{}]+', fragment):
                t = t.strip()
                if t and t in VOCAB:
                    frag_toks.append(VOCAB[t])
            tokens.extend(frag_toks)
        tokens.append(SEP_IDX)
    tokens.append(EOS_IDX)

    # Pad or truncate
    if len(tokens) >= max_len:
        return tokens[:max_len - 1] + [EOS_IDX]
    return tokens + [PAD_IDX] * (max_len - len(tokens))


def formula_to_token_ids(formula_result: dict, max_len: int = 256) -> List[int]:
    """Convert a formula decomposition result to token IDs."""
    tokens = [BOS_IDX]
    for frag in formula_result.get("per_primitive_fragments", []):
        fragment = frag.get("zfc_fragment", "")
        for t in re.split(r'[\s(),{}]+', fragment):
            t = t.strip()
            if t and t in VOCAB:
                tokens.append(VOCAB[t])
        atom = frag.get("promoted_atom")
        if atom and atom in VOCAB:
            tokens.append(VOCAB[atom])
        tokens.append(SEP_IDX)
    tokens.append(EOS_IDX)

    if len(tokens) >= max_len:
        return tokens[:max_len - 1] + [EOS_IDX]
    return tokens + [PAD_IDX] * (max_len - len(tokens))


# ══════════════════════════════════════════════════════════════════════════════
# ZFC_fe ENCODER MODEL
# ══════════════════════════════════════════════════════════════════════════════

NUM_VALUES = {p: len(v) for p, v in ORDINALS.items()}


class ZFCfeEncoder(nn.Module):
    """Transformer encoder over ZFC_fe formula vocabulary.

    Input: token sequence representing ZFC_fe formula fragments
    Output: 12 primitive classification heads (one per primitive)
    """

    def __init__(
        self,
        vocab_size: int = VOCAB_SIZE,
        max_len: int = 256,
        hidden_dim: int = 256,
        n_heads: int = 4,
        n_layers: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.tok_emb = nn.Embedding(vocab_size, hidden_dim, padding_idx=PAD_IDX)
        self.pos_emb = nn.Embedding(max_len, hidden_dim)

        enc_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, nhead=n_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout, batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.heads = nn.ModuleList([
            nn.Linear(hidden_dim, NUM_VALUES[p]) for p in PRIMITIVE_KEYS
        ])
        self.dropout = nn.Dropout(dropout)
        self._init_weights()

    def _init_weights(self):
        nn.init.normal_(self.tok_emb.weight, std=0.02)
        nn.init.normal_(self.pos_emb.weight, std=0.02)
        for h in self.heads:
            nn.init.xavier_uniform_(h.weight)

    def forward(self, token_ids: torch.Tensor) -> List[torch.Tensor]:
        if token_ids.dim() == 1:
            token_ids = token_ids.unsqueeze(0)
        B, L = token_ids.shape
        positions = torch.arange(L, device=token_ids.device).unsqueeze(0).expand(B, -1)
        pad_mask = (token_ids == PAD_IDX)
        x = self.dropout(self.tok_emb(token_ids) + self.pos_emb(positions))
        x = self.transformer(x, src_key_padding_mask=pad_mask)
        lens = (~pad_mask).float().sum(dim=1, keepdim=True).clamp(min=1)
        x_mean = (x * (~pad_mask).float().unsqueeze(-1)).sum(1) / lens
        return [head(x_mean) for head in self.heads]


# ══════════════════════════════════════════════════════════════════════════════
# FROBENIUS LOSS
# ══════════════════════════════════════════════════════════════════════════════

WEIGHTS = {
    "⊢": 1.0, "⊣": 1.2, ">": 1.0, "<": 1.0,
    "⋈": 0.9, "⊤": 1.0, "∈": 1.0, "∋": 1.2,
    "⊙": 1.1, "⊥": 1.2, "⊞": 0.8, "◻": 1.2,
}


def frobenius_loss(
    predictions: List[torch.Tensor],
    targets: torch.Tensor,  # [B, 12]
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Weighted cross-entropy loss with per-primitive breakdown."""
    B = targets.shape[0]
    total_loss = torch.tensor(0.0, device=targets.device)
    per_prim = torch.zeros(12, device=targets.device)

    for i in range(12):
        w = WEIGHTS.get(PRIMITIVE_KEYS[i], 1.0)
        loss_i = F.cross_entropy(predictions[i], targets[:, i])
        total_loss = total_loss + w * loss_i
        per_prim[i] = loss_i.detach()

    return total_loss, per_prim


# ══════════════════════════════════════════════════════════════════════════════
# DATASET BUILDING
# ══════════════════════════════════════════════════════════════════════════════

def build_dataset(
    catalog_entries: List[dict],
    max_len: int = 256,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Build (token_seqs, target_indices) from catalog entries."""
    token_seqs = []
    targets = []

    for entry in catalog_entries:
        t = entry.get("tuple", {})
        if not t or len(t) < 12:
            continue

        # Verify all 12 primitives present with valid values
        valid = True
        target_idx = []
        for p in PRIMITIVE_KEYS:
            v = t.get(p)
            if v is None or v not in ORDINALS[p]:
                valid = False
                break
            target_idx.append(int(ORDINALS[p][v]))
        if not valid:
            continue

        tokens = formula_to_tokens(t, max_len)
        token_seqs.append(tokens)
        targets.append(target_idx)

    if not token_seqs:
        return torch.empty(0, max_len, dtype=torch.long), torch.empty(0, 12, dtype=torch.long)

    return (
        torch.tensor(token_seqs, dtype=torch.long),
        torch.tensor(targets, dtype=torch.long),
    )


def load_all_entries(catalog_path: Optional[str] = None) -> List[dict]:
    """Load all entries: built-in KNOWN_SYSTEMS + IG_catalog.json entries."""
    entries = []

    # Built-in systems
    for name, info in KNOWN_SYSTEMS.items():
        t = info.get("tuple", {})
        if t and len(t) == 12:
            entries.append({"name": name, "description": info.get("description", ""), "tuple": t})

    # IG catalog
    load_catalog()
    for name, info in sorted(CATALOG_INDEX.items()):
        t = info.get("tuple", {})
        if t and len(t) == 12:
            entries.append({"name": name, "description": info.get("description", ""), "tuple": t})

    # Deduplicate by name
    seen = set()
    unique = []
    for e in entries:
        if e["name"] not in seen:
            seen.add(e["name"])
            unique.append(e)
    return unique


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def train(
    catalog_path: Optional[str] = None,
    n_epochs: int = 300,
    batch_size: int = 64,
    lr: float = 3e-4,
    hidden_dim: int = 256,
    n_layers: int = 4,
    max_len: int = 256,
    seed: int = 17280000,
    save_path: str = "zfcfe_encoder.pt",
):
    """Train the ZFC_fe encoder on catalog entries."""
    torch.manual_seed(seed)
    print(f"[ZFCfe train] device={DEVICE}  vocab={VOCAB_SIZE}  max_len={max_len}")

    # Load all entries
    all_entries = load_all_entries(catalog_path)
    print(f"[ZFCfe train] loaded {len(all_entries)} entries")

    # Build dataset
    token_seqs, targets = build_dataset(all_entries, max_len)
    print(f"[ZFCfe train] dataset: {len(token_seqs)} valid entries")

    if len(token_seqs) == 0:
        print("[ZFCfe train] ERROR: no valid entries — check catalog")
        return None

    # Report ZFC_fe promotion instances
    for atom in ZFC_FE_PROMOTED_ATOMS:
        n = sum(1 for e in all_entries
                if any(atom in str(ZFC_FE_FORMULAE.get(p, {}).get(e.get("tuple", {}).get(p), ("", None))[1] or "")
                       for p in PRIMITIVE_KEYS))
        print(f"  {atom}: {n} entries with this atom")

    # Create DataLoader
    dataset = TensorDataset(token_seqs, targets)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Build model
    model = ZFCfeEncoder(
        vocab_size=VOCAB_SIZE, max_len=max_len,
        hidden_dim=hidden_dim, n_layers=n_layers,
    ).to(DEVICE)

    optimiser = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimiser, T_max=n_epochs)

    print(f"[ZFCfe train] parameters: {sum(p.numel() for p in model.parameters()):,}")

    best_loss = float("inf")
    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss, epoch_prim, n_batches = 0.0, torch.zeros(12), 0

        for toks, tgts in loader:
            toks, tgts = toks.to(DEVICE), tgts.to(DEVICE)
            optimiser.zero_grad()
            loss, pp = frobenius_loss(model(toks), tgts)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            epoch_loss += loss.item()
            epoch_prim += pp.cpu()
            n_batches += 1

        scheduler.step()
        avg_loss = epoch_loss / n_batches

        if epoch % 50 == 0 or epoch == 1:
            top2 = (epoch_prim / n_batches).topk(2)
            print(f"  ep {epoch:4d}  loss={avg_loss:.4f}  "
                  f"top: {PRIMITIVE_KEYS[top2.indices[0]]}={top2.values[0]:.3f}  "
                  f"{PRIMITIVE_KEYS[top2.indices[1]]}={top2.values[1]:.3f}")

        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), str(_HERE / save_path))

    print(f"[ZFCfe train] done. best loss={best_loss:.4f}  saved → {save_path}")
    return model


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATION
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_entry(
    model: ZFCfeEncoder,
    entry_name: str,
    max_len: int = 256,
) -> dict:
    """Evaluate a single entry through the trained model."""
    sys_info = resolve_system(entry_name)
    if sys_info is None:
        return {"status": "error", "message": f"Unknown system: {entry_name}"}

    t = sys_info["tuple"]
    tokens = formula_to_tokens(t, max_len)
    token_tensor = torch.tensor([tokens], dtype=torch.long).to(DEVICE)

    model.eval()
    with torch.no_grad():
        predictions = model(token_tensor)

    predicted_values = {}
    predicted_notation = {}
    for i, p in enumerate(PRIMITIVE_KEYS):
        pred_idx = predictions[i][0].argmax().item()
        inv = {int(v): k for k, v in ORDINALS[p].items()}
        predicted_values[p] = inv.get(pred_idx, f"unk:{pred_idx}")
        predicted_notation[p] = PRIMITIVE_NOTATION.get(predicted_values[p], str(predicted_values[p]))

    correct = sum(1 for p in PRIMITIVE_KEYS if predicted_values[p] == t.get(p))
    accuracy = correct / 12

    formula = generate_formula(t, entry_name)

    return {
        "status": "ok",
        "system": entry_name,
        "accuracy": accuracy,
        "correct_primitives": correct,
        "predicted_tuple": predicted_values,
        "predicted_notation": tuple_to_notation(predicted_values),
        "actual_notation": tuple_to_notation(t),
        "formula": formula,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZFC_fe Encoder Training")
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--hidden", type=int, default=256)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--catalog", type=str, default=None)
    parser.add_argument("--save", type=str, default="zfcfe_encoder.pt")
    parser.add_argument("--no-catalog", action="store_true", help="Skip IG catalog, use built-ins only")
    parser.add_argument("--eval", type=str, default=None, help="Evaluate a specific entry after training")

    args = parser.parse_args()

    model = train(
        catalog_path=None if args.no_catalog else args.catalog,
        n_epochs=args.epochs,
        batch_size=args.batch,
        lr=args.lr,
        hidden_dim=args.hidden,
        n_layers=args.layers,
        save_path=args.save,
    )

    if model is not None and args.eval:
        result = evaluate_entry(model, args.eval)
        print(json.dumps(result, indent=2, ensure_ascii=False))
