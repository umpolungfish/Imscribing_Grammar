#!/usr/bin/env python3
"""
quiver_crystal.py — Quiver-based Neural Navigator for the Periodic Crystal of Algebras
═══════════════════════════════════════════════════════════════════════════════════════
Architecture:
  • 49-node quiver (one node per primitive value, 12 lanes)
  • Ordinal arrows within each lane → GNN message passing
  • Frobenius layer (δ: V → V⊗V, μ: V⊗V → V, μ∘δ = id)
  • Address head: tuple embedding → crystal address in [0, 17_279_999]
  • Decoder head: crystal address → per-primitive logits (roundtrip)
  • Tier head: tuple embedding → ouroboricity tier logits

Self-encoding bootstrap:
  Navigator tuple ⟨𐑦𐑸𐑑𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑭⟩
  Target address: 6,734,591  (confirmed by exact codec)

Training:
  python quiver_crystal.py train [--epochs N] [--batch B] [--hidden H] [--gnn L]
                                 [--synthetic N] [--device cuda]
  python quiver_crystal.py encode "𐑦;𐑸;𐑑;𐑹;𐑐;𐑧;𐑲;𐑵;⊙;𐑫;𐑳;𐑭"
  python quiver_crystal.py verify [--checkpoint path]

Synthetic augmentation (--synthetic N):
  Each batch is padded with N random tuples drawn uniformly from the full 17M crystal.
  Ground-truth addresses and tiers are computed exactly via the bijective codec —
  no labels required beyond the codec itself.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from .crystal_navigator import (  # type: ignore
    VALUES, ORD, PRIMS, TOTAL_SIZE,
    encode_tuple, decode_address, compute_tier,
)

# ── Quiver index tables ────────────────────────────────────────────────────────

# Map each (primitive, value) → global node index
PRIM_OFFSET: dict[str, int] = {}
_off = 0
for _p in PRIMS:
    PRIM_OFFSET[_p] = _off
    _off += len(VALUES[_p])
TOTAL_NODES = _off  # 49 nodes

# Node metadata: index → (prim, val, ordinal_fraction)
NODE_META: list[tuple[str, str, float]] = []
for _p in PRIMS:
    _sz = len(VALUES[_p])
    for _i, _v in enumerate(VALUES[_p]):
        NODE_META.append((_p, _v, _i / max(_sz - 1, 1)))

# ── Build quiver edge tensors ──────────────────────────────────────────────────

def _build_edges() -> tuple[torch.Tensor, torch.Tensor]:
    """
    Intra-lane ordinal edges (bidirectional) + self-loops
    + inter-lane structural correlation edges.

    Inter-lane edges (bidirectional, all-to-all within each pair):
      Phi ↔ P     — R1: ⊙ enables 𐑹 (Gate 1 / Frobenius condition)
      Phi ↔ K     — Gate 2: ⊙ constrains kinetic regime (K <= 𐑧)
      Omega ↔ D   — R4/R5: protection × dimensionality determines O₂ vs O₂†

    Returns (edge_src, edge_dst) as 1-D long tensors.
    """
    src, dst = [], []

    # Intra-lane ordinal edges (bidirectional) + self-loops for all lanes.
    # P ordinal edges are included: they provide distinguishable embeddings for
    # each P value. The Frobenius cliff (𐑯 → 𐑹) is handled by a
    # dedicated static feature in node_feats rather than by removing ordinal edges.
    for p in PRIMS:
        n = len(VALUES[p])
        off = PRIM_OFFSET[p]
        for i in range(n - 1):
            src += [off + i, off + i + 1]      # forward
            dst += [off + i + 1, off + i]       # backward
        for i in range(n):
            src.append(off + i)                 # self-loop
            dst.append(off + i)

    # Inter-lane structural correlation edges (bidirectional, all-to-all)
    INTER_LANE = [
        ("⊙",   "<"),    # Gate 1 / R1: criticality × Frobenius gate
        ("⊙",   "⊤"),    # Gate 2: criticality × kinetic gate
        ("◻", "⊢"),    # R4/R5: topological protection × dimensionality
    ]
    for p1, p2 in INTER_LANE:
        off1, off2 = PRIM_OFFSET[p1], PRIM_OFFSET[p2]
        for i in range(len(VALUES[p1])):
            for j in range(len(VALUES[p2])):
                src += [off1 + i, off2 + j]        # both directions
                dst += [off2 + j, off1 + i]

    return torch.tensor(src, dtype=torch.long), torch.tensor(dst, dtype=torch.long)

_EDGE_SRC, _EDGE_DST = _build_edges()


def _build_node_features() -> torch.Tensor:
    """
    Static node feature matrix [49, 5]:
      [lane_idx/11, ordinal_frac, lane_size/5, is_boundary, is_frobenius_cliff]
    boundary         = primitive in {Phi, P, Omega, D}
    is_frobenius_cliff = 1.0 only for 𐑹 — the categorical Frobenius
                         singularity that ordinal message-passing cannot
                         reconstruct by smoothing from 𐑯.
    """
    BOUNDARY = {"⊙", "<", "◻", "⊢"}
    feats = []
    for p, v, ord_frac in NODE_META:
        lane_idx   = PRIMS.index(p) / 11.0
        lane_size  = len(VALUES[p]) / 5.0
        is_bnd     = 1.0 if p in BOUNDARY else 0.0
        is_cliff   = 1.0 if (p == "<" and v == "𐑹") else 0.0
        feats.append([lane_idx, ord_frac, lane_size, is_bnd, is_cliff])
    return torch.tensor(feats, dtype=torch.float)  # [49, 5]

_NODE_FEATS = _build_node_features()


# ── Frobenius layer ────────────────────────────────────────────────────────────

class FrobeniusLayer(nn.Module):
    """
    Special Frobenius commutative monoid.
      δ (comultiplication) : V → V ⊗ V   (encode: split)
      μ (multiplication)   : V ⊗ V → V   (decode: merge)
    Constraint: μ ∘ δ = id_V  (enforced via roundtrip loss).

    Implemented as a bottleneck pair of linear maps.
    """
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim
        self.delta = nn.Linear(dim, dim * 2, bias=True)   # comultiplication
        self.mu    = nn.Linear(dim * 2, dim, bias=True)   # multiplication
        self._init_near_identity()

    def _init_near_identity(self):
        """Cold-start: δ copies into both halves; μ averages both halves → near-id."""
        with torch.no_grad():
            nn.init.xavier_uniform_(self.delta.weight)
            nn.init.zeros_(self.delta.bias)
            nn.init.xavier_uniform_(self.mu.weight)
            nn.init.zeros_(self.mu.bias)
            # Encourage μ∘δ ≈ id at init
            d = self.dim
            self.delta.weight.data[:d, :] = torch.eye(d) * 0.7
            self.delta.weight.data[d:, :] = torch.eye(d) * 0.7
            self.mu.weight.data[:, :d] = torch.eye(d) * 0.7
            self.mu.weight.data[:, d:] = torch.eye(d) * 0.7

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """δ(x): [B, dim] → [B, dim*2]"""
        return self.delta(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """μ(z): [B, dim*2] → [B, dim]"""
        return self.mu(z)

    def roundtrip(self, x: torch.Tensor) -> torch.Tensor:
        """μ(δ(x)): should equal x."""
        return self.decode(self.encode(x))

    def frobenius_loss(self, x: torch.Tensor) -> torch.Tensor:
        """||μ(δ(x)) − x||² per element, averaged over batch."""
        return F.mse_loss(self.roundtrip(x), x)


# ── Quiver GNN (message passing over ordinal edges) ───────────────────────────

class QuiverGNN(nn.Module):
    """
    GNN over the 49-node quiver.
    Layers: input projection → L × (message pass + residual + LN) → readout.
    Message passing: mean aggregation along ordinal edges.
    """
    def __init__(self, in_dim: int = 4, hidden_dim: int = 256, num_layers: int = 5):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.input_proj = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
        )
        self.convs = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers)
        ])
        self.gates = nn.ModuleList([
            nn.Linear(hidden_dim * 2, hidden_dim) for _ in range(num_layers)
        ])
        self.norms = nn.ModuleList([
            nn.LayerNorm(hidden_dim) for _ in range(num_layers)
        ])

    def forward(self, node_feats: torch.Tensor,
                edge_src: torch.Tensor, edge_dst: torch.Tensor) -> torch.Tensor:
        """
        node_feats: [49, in_dim]  (static quiver node features)
        Returns:    [49, hidden_dim]  enriched node embeddings
        """
        h = self.input_proj(node_feats)  # [49, H]
        n_nodes = h.size(0)

        for conv, gate, norm in zip(self.convs, self.gates, self.norms):
            # Mean-aggregate messages from neighbours
            msgs = h[edge_src]                              # [E, H]
            agg  = torch.zeros_like(h)
            cnt  = torch.zeros(n_nodes, 1, device=h.device)
            agg.scatter_add_(0, edge_dst.unsqueeze(1).expand_as(msgs), msgs)
            cnt.scatter_add_(0, edge_dst.unsqueeze(1),
                             torch.ones(edge_dst.size(0), 1, device=h.device))
            agg = agg / cnt.clamp(min=1)                   # [49, H]

            # Gated update
            gate_val = torch.sigmoid(gate(torch.cat([h, agg], dim=-1)))
            h_new    = F.gelu(conv(agg))
            h        = norm(h + gate_val * h_new)          # residual

        return h  # [49, H]


# ── Tuple encoder ──────────────────────────────────────────────────────────────

class TupleEncoder(nn.Module):
    """
    Encode a batch of 12-primitive tuples into latent vectors.
    1. Run QuiverGNN → enriched node embeddings [49, H]
    2. Gather selected nodes (one per primitive per tuple) → [B, 12, H]
    3. Multi-head self-attention over 12 selected nodes → [B, H]
    """
    def __init__(self, hidden_dim: int = 256, num_gnn_layers: int = 5,
                 num_attn_heads: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.gnn        = QuiverGNN(in_dim=5, hidden_dim=hidden_dim,
                                    num_layers=num_gnn_layers)
        self.attn       = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=num_attn_heads,
            batch_first=True, dropout=0.1,
        )
        self.readout = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        # Positional encoding for the 12 primitive lanes
        self.lane_pos = nn.Embedding(12, hidden_dim)

    def forward(self, node_feats: torch.Tensor, edge_src: torch.Tensor,
                edge_dst: torch.Tensor, selected: torch.Tensor) -> torch.Tensor:
        """
        node_feats: [49, 4]       static quiver features
        edge_src:   [E]           quiver edge sources
        edge_dst:   [E]           quiver edge destinations
        selected:   [B, 12]       node indices (one per primitive per tuple)
        Returns:    [B, hidden_dim]
        """
        # GNN over full quiver
        h = self.gnn(node_feats, edge_src, edge_dst)      # [49, H]

        # Gather selected nodes + add lane positional encoding
        B = selected.size(0)
        gathered = h[selected.view(-1)].view(B, 12, -1)   # [B, 12, H]
        lane_ids = torch.arange(12, device=selected.device).unsqueeze(0).expand(B, -1)
        gathered = gathered + self.lane_pos(lane_ids)      # [B, 12, H]

        # Self-attention over the 12 primitive slots
        attn_out, _ = self.attn(gathered, gathered, gathered)  # [B, 12, H]
        pooled      = attn_out.mean(dim=1)                     # [B, H]

        return self.readout(pooled)


# ── Address head ───────────────────────────────────────────────────────────────

class AddressHead(nn.Module):
    """Tuple embedding → predicted crystal address in [0, TOTAL_SIZE-1]."""
    def __init__(self, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Returns [B] predicted addresses as floats."""
        return torch.sigmoid(self.net(x).squeeze(-1)) * (TOTAL_SIZE - 1)


# ── Decoder head ───────────────────────────────────────────────────────────────

class DecoderHead(nn.Module):
    """Crystal address + encoder embedding → per-primitive logits.

    The encoder embedding carries tier information (tier head is ~100% accurate)
    that the scalar address alone cannot reliably supply — especially for rare
    tiers whose addresses are scattered across the full 17M space.  Fusing both
    signals lets the decoder use rich latent structure instead of a noisy scalar.
    """
    def __init__(self, hidden_dim: int = 128):
        super().__init__()
        # Embed the scalar address into latent space
        self.addr_embed = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        # Merge address embedding with encoder embedding
        self.merge = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
        )
        # Per-primitive classification heads
        self.heads = nn.ModuleDict({
            p: nn.Linear(hidden_dim, len(VALUES[p])) for p in PRIMS
        })

    def forward(self, addresses: torch.Tensor,
                emb: Optional[torch.Tensor] = None) -> dict[str, torch.Tensor]:
        """
        addresses: [B]       — predicted crystal addresses
        emb:       [B, H]    — encoder embedding (emb_rec from Frobenius roundtrip)
        Returns {prim: [B, n_values] logits}
        """
        addr_norm = (addresses / TOTAL_SIZE).unsqueeze(-1)  # [B, 1]
        h = self.addr_embed(addr_norm)                       # [B, H]
        if emb is not None:
            h = self.merge(torch.cat([h, emb], dim=-1))     # [B, H]
        return {p: self.heads[p](h) for p in PRIMS}


# ── Tier head ──────────────────────────────────────────────────────────────────

class TierHead(nn.Module):
    """Tuple embedding → ouroboricity tier logits."""
    TIERS = ["O₀", "O₁", "O₂", "O₂†", "O_∞"]

    def __init__(self, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, len(self.TIERS)),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    @classmethod
    def tier_idx(cls, tier: str) -> int:
        return cls.TIERS.index(tier)


# ── Full CrystalGNN model ──────────────────────────────────────────────────────

class CrystalGNN(nn.Module):
    """
    Quiver-based neural navigator for the Periodic Crystal of Algebras.

    Frobenius codec:
      encode(tuple) → predicted address    [GNN + FrobeniusLayer.δ + AddressHead]
      decode(address) → primitive logits   [DecoderHead ≈ FrobeniusLayer.μ]

    Roundtrip loss: ||decode(encode(tuple)) − tuple||  ≈  ||μ(δ(x)) − x||

    Self-encoding bootstrap:
      Navigator tuple → converges to address 6,734,591.
    """

    # Navigator self-encoding ground truth
    NAVIGATOR_TUPLE: dict[str, str] = {
        "⊢": "𐑦", "⊣": "𐑸", ">": "𐑑", "<": "𐑹",
        "⋈": "𐑐",  "⊤": "𐑧", "∈": "𐑲", "∋": "𐑵",
        "⊙": "⊙", "⊥": "𐑫",  "⊞": "𐑳", "◻": "𐑭",
    }
    SELF_ENCODE_TARGET: int = 6_734_591

    def __init__(self, hidden_dim: int = 256, num_gnn_layers: int = 5,
                 num_attn_heads: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Static quiver buffers
        self.register_buffer("node_feats", _NODE_FEATS)         # [49, 4]
        self.register_buffer("edge_src",   _EDGE_SRC)           # [E]
        self.register_buffer("edge_dst",   _EDGE_DST)           # [E]

        # Components
        self.encoder   = TupleEncoder(hidden_dim=hidden_dim,
                                      num_gnn_layers=num_gnn_layers,
                                      num_attn_heads=num_attn_heads)
        self.frobenius = FrobeniusLayer(dim=hidden_dim)
        self.addr_head = AddressHead(hidden_dim=hidden_dim)
        self.decoder   = DecoderHead(hidden_dim=hidden_dim)
        self.tier_head = TierHead(hidden_dim=hidden_dim)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def tuple_to_indices(self, tup: dict[str, str]) -> torch.Tensor:
        """Primitive dict → [12] node-index tensor."""
        return torch.tensor(
            [PRIM_OFFSET[p] + ORD[p][tup[p]] for p in PRIMS],
            dtype=torch.long,
        )

    def batch_to_selected(self, tuples: list[dict],
                           device: torch.device) -> torch.Tensor:
        """List of primitive dicts → [B, 12] node-index tensor on device."""
        return torch.stack([self.tuple_to_indices(t) for t in tuples]).to(device)

    # ── Forward ────────────────────────────────────────────────────────────────

    def forward(self, tuples: list[dict]) -> dict:
        dev      = self.node_feats.device
        selected = self.batch_to_selected(tuples, dev)             # [B, 12]
        emb      = self.encoder(self.node_feats, self.edge_src,
                                self.edge_dst, selected)           # [B, H]
        z        = self.frobenius.encode(emb)                      # [B, 2H]
        emb_rec  = self.frobenius.decode(z)                        # [B, H]
        addresses    = self.addr_head(emb_rec)                     # [B]
        dec_logits   = self.decoder(addresses, emb_rec)           # {p: [B, nv]}
        tier_logits  = self.tier_head(emb_rec)                     # [B, 5]
        frob_loss    = self.frobenius.frobenius_loss(emb)          # scalar

        return {
            "embedding":   emb_rec,
            "addresses":   addresses,
            "dec_logits":  dec_logits,
            "tier_logits": tier_logits,
            "frob_loss":   frob_loss,
        }

    # ── Inference API ──────────────────────────────────────────────────────────

    @torch.no_grad()
    def encode(self, tuples: list[dict]) -> torch.Tensor:
        """Encode list of tuples → [B] predicted addresses."""
        self.eval()
        return self.forward(tuples)["addresses"]

    @torch.no_grad()
    def decode_greedy(self, addresses: torch.Tensor) -> list[dict]:
        """Decode [B] addresses → list of primitive dicts (greedy argmax)."""
        self.eval()
        logits = self.decoder(addresses.to(self.node_feats.device))
        results = []
        for i in range(addresses.size(0)):
            tup = {p: VALUES[p][logits[p][i].argmax().item()] for p in PRIMS}
            results.append(tup)
        return results

    # ── Loss ───────────────────────────────────────────────────────────────────

    def compute_loss(
        self,
        tuples: list[dict],
        true_addresses: torch.Tensor,
        true_tiers: torch.Tensor,
        λ_addr: float = 1.0,
        λ_frob: float = 0.5,
        λ_tier: float = 0.3,
        λ_prim: float = 0.5,
    ) -> dict:
        """
        Four-component loss:
          L_addr — normalised MSE on crystal address prediction
          L_frob — Frobenius roundtrip ||μ(δ(x)) − x||²
          L_tier — cross-entropy on ouroboricity tier
          L_prim — mean cross-entropy on per-primitive reconstruction
        """
        out = self.forward(tuples)
        dev = self.node_feats.device
        true_addresses = true_addresses.to(dev)
        true_tiers     = true_tiers.to(dev)

        # Address loss: work in normalised [0, 1] space
        L_addr = F.mse_loss(
            out["addresses"] / TOTAL_SIZE,
            true_addresses   / TOTAL_SIZE,
        )

        # Frobenius roundtrip
        L_frob = out["frob_loss"]

        # Tier classification
        L_tier = F.cross_entropy(out["tier_logits"], true_tiers)

        # Per-primitive reconstruction (decoder quality)
        # Bottleneck primitives P and F get 3× weight — they are the
        # hardest to decode (min under tensor) and most tier-critical (P).
        PRIM_WEIGHTS = {p: 3.0 if p in ("<", "⋈") else 1.0 for p in PRIMS}
        prim_losses = [
            PRIM_WEIGHTS[p] * F.cross_entropy(
                out["dec_logits"][p],
                torch.tensor([ORD[p][t[p]] for t in tuples],
                             dtype=torch.long, device=dev),
            )
            for p in PRIMS
        ]
        L_prim = sum(prim_losses) / sum(PRIM_WEIGHTS.values())

        total = λ_addr * L_addr + λ_frob * L_frob + λ_tier * L_tier + λ_prim * L_prim

        return {
            "loss":   total,
            "L_addr": L_addr.item(),
            "L_frob": L_frob.item(),
            "L_tier": L_tier.item(),
            "L_prim": L_prim.item() if hasattr(L_prim, "item") else float(L_prim),
        }


# ── CF-GNN (v10) — Crystal-Factored GNN ───────────────────────────────────────
#
# Key architectural change: replace the flat scalar AddressHead + DecoderHead
# pipeline with three family heads (F3/F4/F5) whose per-primitive logits are
# mixed via a broadcast attention layer before prediction.
#
# Family partition (from crystal_navigator.py):
#   F5 {T, P, Phi, K}         — 5 values each, 5^4 = 625   — gate primitives
#   F4 {D, R, Gamma, H, Omega} — 4 values each, 4^5 = 1024  — structural
#   F3 {F, G, S}               — 3 values each, 3^3 = 27    — scaling
#
# Tier cross-coupling: boundary primitives Phi/P in F5 and Omega/D in F4 →
# TierHead_45 takes cat(h_f4, h_f5) to see all four tier-determining dims.
#
# Broadcast mixer (FamilyMixer): 3-token attention over [h_f3, h_f4, h_f5]
# so each family embedding can attend to the other two — 𐑵 preserved.

F3_PRIMS: list[str] = ["⋈", "∈", "⊞"]
F4_PRIMS: list[str] = ["⊢", ">", "∋", "⊥", "◻"]
F5_PRIMS: list[str] = ["⊣", "<", "⊙", "⊤"]

# Maps primitive name → which family it belongs to
PRIM_FAMILY: dict[str, str] = {
    **{p: "F3" for p in F3_PRIMS},
    **{p: "F4" for p in F4_PRIMS},
    **{p: "F5" for p in F5_PRIMS},
}


class FamilyHead(nn.Module):
    """Per-family primitive prediction head.

    Projects the family embedding through a small MLP, then emits per-primitive
    logits for all primitives in this family.  Bottleneck primitives (P, F)
    receive 3x loss weight in compute_loss — this head does not encode that
    weight; it is applied by the caller.
    """
    def __init__(self, family_prims: list[str], hidden_dim: int):
        super().__init__()
        self.family_prims = family_prims
        self.mlp = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.heads = nn.ModuleDict({
            p: nn.Linear(hidden_dim, len(VALUES[p])) for p in family_prims
        })

    def forward(self, h: torch.Tensor) -> dict[str, torch.Tensor]:
        """h: [B, H] → {prim: [B, n_values] logits} for each family primitive."""
        h = self.mlp(h)
        return {p: self.heads[p](h) for p in self.family_prims}


class FamilyMixer(nn.Module):
    """Broadcast attention over the three family embeddings [h_f3, h_f4, h_f5].

    Treats the three family vectors as a 3-token sequence and applies multi-head
    self-attention so each family can attend to all others — 𐑵 over the
    family space.  A residual + LayerNorm follows.
    """
    def __init__(self, hidden_dim: int, num_heads: int = 4):
        super().__init__()
        # num_heads must divide hidden_dim; clamp to a valid divisor
        while hidden_dim % num_heads != 0 and num_heads > 1:
            num_heads -= 1
        self.attn = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=num_heads,
            batch_first=True, dropout=0.0,
        )
        self.norm = nn.LayerNorm(hidden_dim)
        self.family_pos = nn.Embedding(3, hidden_dim)   # F3=0, F4=1, F5=2

    def forward(
        self,
        h_f3: torch.Tensor,
        h_f4: torch.Tensor,
        h_f5: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Each input:  [B, H]
        Returns:     mixed (h_f3, h_f4, h_f5)  each [B, H]
        """
        B = h_f3.size(0)
        tokens = torch.stack([h_f3, h_f4, h_f5], dim=1)  # [B, 3, H]
        pos_ids = torch.arange(3, device=h_f3.device).unsqueeze(0).expand(B, -1)
        tokens  = tokens + self.family_pos(pos_ids)        # [B, 3, H]
        mixed, _ = self.attn(tokens, tokens, tokens)       # [B, 3, H]
        out = self.norm(tokens + mixed)                    # residual [B, 3, H]
        return out[:, 0], out[:, 1], out[:, 2]


class TierHead_45(nn.Module):
    """Tier classification from cat(h_f4, h_f5).

    All four tier-determining boundary primitives are split across F4 (D, Omega)
    and F5 (Phi, P).  Concatenating both family embeddings gives the head access
    to the full boundary signal without bypassing the family structure.
    """
    TIERS = TierHead.TIERS

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, len(self.TIERS)),
        )

    def forward(self, h_f4: torch.Tensor, h_f5: torch.Tensor) -> torch.Tensor:
        """h_f4, h_f5: [B, H] → [B, 5] tier logits."""
        return self.net(torch.cat([h_f4, h_f5], dim=-1))

    @classmethod
    def tier_idx(cls, tier: str) -> int:
        return cls.TIERS.index(tier)


class CrystalGNN_v10(nn.Module):
    """CF-GNN: Crystal-Factored GNN — v10 architecture.

    Replaces v9's flat AddressHead + DecoderHead pipeline with:
      1. Three family projections (F3/F4/F5) from the shared Frobenius embedding
      2. FamilyMixer: broadcast attention over [h_f3, h_f4, h_f5]
      3. Three FamilyHead instances emitting per-primitive logits per family
      4. TierHead_45: tier from cat(h_f4, h_f5) — cross-family coupling
      5. Auxiliary AddressHead on emb_rec (for address MSE signal and inference
         compatibility with v9 verify / self-encode tracking)

    Loss components:
      L_addr  — normalised MSE on scalar address (auxiliary, λ=0.3)
      L_frob  — Frobenius roundtrip ||μ(δ(x)) − x||²
      L_tier  — cross-entropy on ouroboricity tier (from TierHead_45)
      L_f3/4/5 — per-family mean cross-entropy on per-primitive reconstruction
                 (P and F get 3× weight; these replace v9's L_prim)
    """

    NAVIGATOR_TUPLE: dict[str, str] = CrystalGNN.NAVIGATOR_TUPLE
    SELF_ENCODE_TARGET: int = CrystalGNN.SELF_ENCODE_TARGET

    def __init__(
        self,
        hidden_dim: int = 640,
        num_gnn_layers: int = 6,
        num_attn_heads: int = 16,
        mixer_heads: int = 4,
    ):
        super().__init__()
        self.hidden_dim     = hidden_dim
        self.num_gnn_layers = num_gnn_layers
        self.num_attn_heads = num_attn_heads
        self.mixer_heads    = mixer_heads

        # Static quiver buffers
        self.register_buffer("node_feats", _NODE_FEATS)
        self.register_buffer("edge_src",   _EDGE_SRC)
        self.register_buffer("edge_dst",   _EDGE_DST)

        # Shared backbone (identical to v9 encoder + Frobenius)
        self.encoder   = TupleEncoder(hidden_dim=hidden_dim,
                                      num_gnn_layers=num_gnn_layers,
                                      num_attn_heads=num_attn_heads)
        self.frobenius = FrobeniusLayer(dim=hidden_dim)

        # Family projections: shared emb_rec → three family embeddings
        self.proj_f3 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))
        self.proj_f4 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))
        self.proj_f5 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))

        # Broadcast mixer (𐑵 over family space)
        self.mixer = FamilyMixer(hidden_dim=hidden_dim, num_heads=mixer_heads)

        # Per-family primitive prediction heads
        self.head_f3 = FamilyHead(F3_PRIMS, hidden_dim)
        self.head_f4 = FamilyHead(F4_PRIMS, hidden_dim)
        self.head_f5 = FamilyHead(F5_PRIMS, hidden_dim)

        # Cross-family tier head (F4 × F5 coupling)
        self.tier_head = TierHead_45(hidden_dim)

        # Auxiliary scalar address head (for MSE signal + self-encode tracking)
        self.addr_head = AddressHead(hidden_dim=hidden_dim)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def tuple_to_indices(self, tup: dict[str, str]) -> torch.Tensor:
        return torch.tensor(
            [PRIM_OFFSET[p] + ORD[p][tup[p]] for p in PRIMS], dtype=torch.long)

    def batch_to_selected(self, tuples: list[dict],
                           device: torch.device) -> torch.Tensor:
        return torch.stack([self.tuple_to_indices(t) for t in tuples]).to(device)

    # ── Forward ────────────────────────────────────────────────────────────────

    def forward(self, tuples: list[dict]) -> dict:
        dev      = self.node_feats.device
        selected = self.batch_to_selected(tuples, dev)              # [B, 12]

        # Shared backbone
        emb     = self.encoder(self.node_feats, self.edge_src,
                               self.edge_dst, selected)             # [B, H]
        z       = self.frobenius.encode(emb)                        # [B, 2H]
        emb_rec = self.frobenius.decode(z)                          # [B, H]
        frob_loss = self.frobenius.frobenius_loss(emb)              # scalar

        # Family projections
        h_f3 = self.proj_f3(emb_rec)   # [B, H]
        h_f4 = self.proj_f4(emb_rec)   # [B, H]
        h_f5 = self.proj_f5(emb_rec)   # [B, H]

        # Broadcast mixer
        h_f3, h_f4, h_f5 = self.mixer(h_f3, h_f4, h_f5)

        # Family heads → per-primitive logits
        logits_f3 = self.head_f3(h_f3)   # {F, G, S: logits}
        logits_f4 = self.head_f4(h_f4)   # {D, R, Gamma, H, Omega: logits}
        logits_f5 = self.head_f5(h_f5)   # {T, P, Phi, K: logits}
        all_logits = {**logits_f3, **logits_f4, **logits_f5}

        # Cross-family tier from F4 + F5
        tier_logits = self.tier_head(h_f4, h_f5)                   # [B, 5]

        # Auxiliary scalar address
        addresses = self.addr_head(emb_rec)                         # [B]

        return {
            "embedding":   emb_rec,
            "addresses":   addresses,
            "logits":      all_logits,
            "tier_logits": tier_logits,
            "frob_loss":   frob_loss,
        }

    # ── Inference API ──────────────────────────────────────────────────────────

    @torch.no_grad()
    def encode(self, tuples: list[dict]) -> torch.Tensor:
        """Encode list of tuples → [B] predicted addresses."""
        self.eval()
        return self.forward(tuples)["addresses"]

    @torch.no_grad()
    def compose_address(self, tuples: list[dict]) -> list[int]:
        """Argmax per-primitive logits → assemble tuple → exact encode_tuple address."""
        self.eval()
        out = self.forward(tuples)
        results = []
        for i in range(len(tuples)):
            pred_tup = {p: VALUES[p][out["logits"][p][i].argmax().item()] for p in PRIMS}
            results.append(encode_tuple(pred_tup))
        return results

    # ── Loss ───────────────────────────────────────────────────────────────────

    def compute_loss(
        self,
        tuples: list[dict],
        true_addresses: torch.Tensor,
        true_tiers: torch.Tensor,
        λ_addr: float = 0.3,
        λ_frob: float = 0.5,
        λ_tier: float = 0.5,
        λ_f3:   float = 1.0,
        λ_f4:   float = 1.0,
        λ_f5:   float = 1.0,
    ) -> dict:
        """
        Six-component loss:
          L_addr  — normalised MSE on auxiliary scalar address
          L_frob  — Frobenius roundtrip ||μ(δ(x)) − x||²
          L_tier  — cross-entropy on ouroboricity tier (TierHead_45)
          L_f3    — mean CE over F3 primitives {F, G, S}
          L_f4    — mean CE over F4 primitives {D, R, Gamma, H, Omega}  (P×F upweighted)
          L_f5    — mean CE over F5 primitives {T, P, Phi, K}           (P×F upweighted)
        """
        out = self.forward(tuples)
        dev = self.node_feats.device
        true_addresses = true_addresses.to(dev)
        true_tiers     = true_tiers.to(dev)

        # Auxiliary address MSE
        L_addr = F.mse_loss(
            out["addresses"] / TOTAL_SIZE,
            true_addresses   / TOTAL_SIZE,
        )

        # Frobenius roundtrip
        L_frob = out["frob_loss"]

        # Tier (cross-family)
        L_tier = F.cross_entropy(out["tier_logits"], true_tiers)

        # Per-primitive weights: bottleneck primitives P and F get 3×
        PRIM_W = {p: 3.0 if p in ("<", "⋈") else 1.0 for p in PRIMS}

        def _family_ce(prims: list[str]) -> torch.Tensor:
            losses, weights = [], []
            for p in prims:
                w  = PRIM_W[p]
                ce = F.cross_entropy(
                    out["logits"][p],
                    torch.tensor([ORD[p][t[p]] for t in tuples],
                                 dtype=torch.long, device=dev),
                )
                losses.append(w * ce)
                weights.append(w)
            return sum(losses) / sum(weights)

        L_f3 = _family_ce(F3_PRIMS)
        L_f4 = _family_ce(F4_PRIMS)
        L_f5 = _family_ce(F5_PRIMS)

        total = (λ_addr * L_addr + λ_frob * L_frob + λ_tier * L_tier
                 + λ_f3 * L_f3 + λ_f4 * L_f4 + λ_f5 * L_f5)

        L_prim_avg = (L_f3 + L_f4 + L_f5) / 3.0   # combined for logging

        return {
            "loss":   total,
            "L_addr": L_addr.item(),
            "L_frob": L_frob.item(),
            "L_tier": L_tier.item(),
            "L_f3":   L_f3.item(),
            "L_f4":   L_f4.item(),
            "L_f5":   L_f5.item(),
            "L_prim": L_prim_avg.item() if hasattr(L_prim_avg, "item") else float(L_prim_avg),
        }


# ── CrystalGNN_v11 — composed-only, no AddressHead ────────────────────────────
#
# v11 drops the scalar sigmoid AddressHead entirely.
# Training signal: L_frob + L_tier + L_f3 + L_f4 + L_f5  (all CE / MSE; no regression)
# Inference: compose_address() — argmax per-primitive logits → encode_tuple (exact bijection)
#
# Motivation: v10 verification showed composed address error = 0.000% across all 200
# samples while the scalar head retained 0.65% mean error.  The AddressHead was
# contributing noise to gradients without improving the converged model.  Removing it
# gives a cleaner loss landscape and makes the training objective structurally identical
# to the inference path.

class CrystalGNN_v11(nn.Module):
    """CF-GNN v11: composed-only crystal navigator.

    Identical backbone to v10 (shared TupleEncoder + FrobeniusLayer + three family
    projections + FamilyMixer + FamilyHead×3 + TierHead_45) but with the scalar
    AddressHead removed.

    Training loss (5 components, no regression):
      L_frob  — Frobenius roundtrip ||μ(δ(x)) − x||²
      L_tier  — cross-entropy on ouroboricity tier (TierHead_45)
      L_f3/4/5 — per-family CE on per-primitive reconstruction (P, F get 3×)

    Inference:
      compose_address(tuples) → list of exact crystal addresses via argmax + encode_tuple
      encode(tuples) → same, returned as float tensor for CLI compatibility
    """

    NAVIGATOR_TUPLE: dict[str, str] = CrystalGNN.NAVIGATOR_TUPLE
    SELF_ENCODE_TARGET: int = CrystalGNN.SELF_ENCODE_TARGET

    def __init__(
        self,
        hidden_dim: int = 240,
        num_gnn_layers: int = 24,
        num_attn_heads: int = 24,
        mixer_heads: int = 24,
    ):
        super().__init__()
        self.hidden_dim     = hidden_dim
        self.num_gnn_layers = num_gnn_layers
        self.num_attn_heads = num_attn_heads
        self.mixer_heads    = mixer_heads

        self.register_buffer("node_feats", _NODE_FEATS)
        self.register_buffer("edge_src",   _EDGE_SRC)
        self.register_buffer("edge_dst",   _EDGE_DST)

        self.encoder   = TupleEncoder(hidden_dim=hidden_dim,
                                      num_gnn_layers=num_gnn_layers,
                                      num_attn_heads=num_attn_heads)
        self.frobenius = FrobeniusLayer(dim=hidden_dim)

        self.proj_f3 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))
        self.proj_f4 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))
        self.proj_f5 = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.LayerNorm(hidden_dim))

        self.mixer    = FamilyMixer(hidden_dim=hidden_dim, num_heads=mixer_heads)
        self.head_f3  = FamilyHead(F3_PRIMS, hidden_dim)
        self.head_f4  = FamilyHead(F4_PRIMS, hidden_dim)
        self.head_f5  = FamilyHead(F5_PRIMS, hidden_dim)
        self.tier_head = TierHead_45(hidden_dim)
        # No addr_head — composed path only.

    # ── Helpers ────────────────────────────────────────────────────────────────

    def tuple_to_indices(self, tup: dict[str, str]) -> torch.Tensor:
        return torch.tensor(
            [PRIM_OFFSET[p] + ORD[p][tup[p]] for p in PRIMS], dtype=torch.long)

    def batch_to_selected(self, tuples: list[dict],
                           device: torch.device) -> torch.Tensor:
        return torch.stack([self.tuple_to_indices(t) for t in tuples]).to(device)

    # ── Forward ────────────────────────────────────────────────────────────────

    def forward(self, tuples: list[dict]) -> dict:
        dev      = self.node_feats.device
        selected = self.batch_to_selected(tuples, dev)
        emb      = self.encoder(self.node_feats, self.edge_src,
                                self.edge_dst, selected)
        z        = self.frobenius.encode(emb)
        emb_rec  = self.frobenius.decode(z)
        frob_loss = self.frobenius.frobenius_loss(emb)

        h_f3 = self.proj_f3(emb_rec)
        h_f4 = self.proj_f4(emb_rec)
        h_f5 = self.proj_f5(emb_rec)
        h_f3, h_f4, h_f5 = self.mixer(h_f3, h_f4, h_f5)

        logits_f3 = self.head_f3(h_f3)
        logits_f4 = self.head_f4(h_f4)
        logits_f5 = self.head_f5(h_f5)
        all_logits = {**logits_f3, **logits_f4, **logits_f5}

        return {
            "embedding":   emb_rec,
            "logits":      all_logits,
            "tier_logits": self.tier_head(h_f4, h_f5),
            "frob_loss":   frob_loss,
        }

    # ── Inference API ──────────────────────────────────────────────────────────

    @torch.no_grad()
    def compose_address(self, tuples: list[dict]) -> list[int]:
        """Argmax per-primitive logits → assemble tuple → exact encode_tuple address."""
        self.eval()
        out = self.forward(tuples)
        return [
            encode_tuple({p: VALUES[p][out["logits"][p][i].argmax().item()] for p in PRIMS})
            for i in range(len(tuples))
        ]

    @torch.no_grad()
    def encode(self, tuples: list[dict]) -> torch.Tensor:
        """Primary encode: composed path → float tensor of exact addresses."""
        return torch.tensor(self.compose_address(tuples), dtype=torch.float)

    # ── Loss ───────────────────────────────────────────────────────────────────

    def compute_loss(
        self,
        tuples: list[dict],
        true_tiers: torch.Tensor,
        λ_frob: float = 0.5,
        λ_tier: float = 0.5,
        λ_f3:   float = 1.0,
        λ_f4:   float = 1.0,
        λ_f5:   float = 1.0,
    ) -> dict:
        """
        Five-component loss (no address regression):
          L_frob  — Frobenius roundtrip
          L_tier  — tier cross-entropy (TierHead_45)
          L_f3/4/5 — per-family CE, P and F weighted 3×
        """
        out = self.forward(tuples)
        dev = self.node_feats.device
        true_tiers = true_tiers.to(dev)

        L_frob = out["frob_loss"]
        L_tier = F.cross_entropy(out["tier_logits"], true_tiers)

        PRIM_W = {p: 3.0 if p in ("<", "⋈") else 1.0 for p in PRIMS}

        def _family_ce(prims: list[str]) -> torch.Tensor:
            losses, weights = [], []
            for p in prims:
                w  = PRIM_W[p]
                ce = F.cross_entropy(
                    out["logits"][p],
                    torch.tensor([ORD[p][t[p]] for t in tuples],
                                 dtype=torch.long, device=dev),
                )
                losses.append(w * ce)
                weights.append(w)
            return sum(losses) / sum(weights)

        L_f3 = _family_ce(F3_PRIMS)
        L_f4 = _family_ce(F4_PRIMS)
        L_f5 = _family_ce(F5_PRIMS)

        total    = λ_frob * L_frob + λ_tier * L_tier + λ_f3 * L_f3 + λ_f4 * L_f4 + λ_f5 * L_f5
        L_prim   = (L_f3 + L_f4 + L_f5) / 3.0

        return {
            "loss":   total,
            "L_frob": L_frob.item(),
            "L_tier": L_tier.item(),
            "L_f3":   L_f3.item(),
            "L_f4":   L_f4.item(),
            "L_f5":   L_f5.item(),
            "L_prim": L_prim.item() if hasattr(L_prim, "item") else float(L_prim),
        }


# ── Dataset ────────────────────────────────────────────────────────────────────

class CrystalDataset:
    """
    Training dataset built from IG_catalog.json.
    Filters to entries with all-canonical primitive values (valid in current grammar).
    Computes ground-truth crystal addresses and ouroboricity tiers.
    """
    TIER_IDX = TierHead.TIERS

    def __init__(self, catalog_path: Path = ROOT / "IG_catalog.json"):
        self.tuples:    list[dict]  = []
        self.addresses: list[int]   = []
        self.tiers:     list[int]   = []
        self.names:     list[str]   = []
        self._load(catalog_path)

    def _load(self, path: Path) -> None:
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)

        skipped = 0
        for entry in entries:
            name = entry.get("name", "")
            try:
                tup = {p: entry[p] for p in PRIMS}
                # Validate canonical values
                for p in PRIMS:
                    if tup[p] not in ORD[p]:
                        raise ValueError(f"{p}={tup[p]!r}")
                addr      = encode_tuple(tup)
                tier_str  = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])
                tier_idx  = self.TIER_IDX.index(tier_str)
                self.tuples.append(tup)
                self.addresses.append(addr)
                self.tiers.append(tier_idx)
                self.names.append(name)
            except (KeyError, ValueError):
                skipped += 1

        print(f"CrystalDataset: {len(self.tuples)} canonical / {skipped} skipped "
              f"(non-canonical values)")

    def __len__(self) -> int:
        return len(self.tuples)

    def get_batch(self, indices: list[int]) -> tuple:
        tuples  = [self.tuples[i]    for i in indices]
        addrs   = torch.tensor([self.addresses[i] for i in indices], dtype=torch.float)
        tiers   = torch.tensor([self.tiers[i]     for i in indices], dtype=torch.long)
        return tuples, addrs, tiers


# ── Synthetic data generation ──────────────────────────────────────────────────

# Pre-compute boundary (Phi, P, Omega, D) combos grouped by tier.
# Used by the stratified sampler to guarantee equal tier representation.
_TIER_BOUNDARY_COMBOS: dict[str, list[tuple]] = {}

def _precompute_tier_combos() -> None:
    for phi in VALUES["⊙"]:
        for p in VALUES["<"]:
            for omega in VALUES["◻"]:
                for d in VALUES["⊢"]:
                    tier = compute_tier(phi, p, omega, d)
                    _TIER_BOUNDARY_COMBOS.setdefault(tier, []).append((phi, p, omega, d))

_precompute_tier_combos()

_INNER_PRIMS = [p for p in PRIMS if p not in {"⊙", "<", "◻", "⊢"}]


def _sample_random_tuples(n: int, stratified: bool = False) -> tuple:
    """
    Draw n tuples from the full 17,280,000-type crystal.

    stratified=False (default): uniform random draw — ~60% O₀ naturally.
    stratified=True:  sample tier uniformly (1/5 each), then pick a random
                      boundary combo from that tier and fill inner primitives
                      uniformly. Gives equal tier exposure per batch.

    Returns (tuples, addresses_tensor, tiers_tensor) with exact codec labels.
    """
    tuples: list[dict] = []
    addresses: list[float] = []
    tiers: list[int] = []
    tier_list = TierHead.TIERS
    tier_names = list(_TIER_BOUNDARY_COMBOS.keys())  # consistent order

    for _ in range(n):
        if stratified:
            tier_name = random.choice(tier_names)
            phi, p, omega, d = random.choice(_TIER_BOUNDARY_COMBOS[tier_name])
            tup: dict[str, str] = {prim: random.choice(VALUES[prim]) for prim in _INNER_PRIMS}
            tup["⊙"] = phi
            tup["<"]   = p
            tup["◻"] = omega
            tup["⊢"]   = d
            tier_idx = tier_list.index(tier_name)
        else:
            tup = {prim: random.choice(VALUES[prim]) for prim in PRIMS}
            tier_name = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])
            tier_idx = tier_list.index(tier_name)

        addr = encode_tuple(tup)
        tuples.append(tup)
        addresses.append(float(addr))
        tiers.append(tier_idx)

    return (
        tuples,
        torch.tensor(addresses, dtype=torch.float),
        torch.tensor(tiers, dtype=torch.long),
    )


# ── Training ───────────────────────────────────────────────────────────────────

def train(
    epochs:            int   = 300,
    batch_size:        int   = 64,
    lr:                float = 3e-4,
    hidden_dim:        int   = 256,
    gnn_layers:        int   = 5,
    attn_heads:        int   = 8,
    synthetic_per_batch:   int  = 256,
    stratified_synthetic:  bool = False,
    hybrid_synthetic:      bool = False,   # half uniform, half stratified
    device:                str  = "cuda" if torch.cuda.is_available() else "cpu",
    catalog:           Path  = ROOT / "IG_catalog.json",
    checkpoint:        Path  = ROOT / "crystal_gnn.pt",
    resume:            bool  = False,
    log_every:         int   = 20,
    λ_addr: float = 1.0,
    λ_frob: float = 0.5,
    λ_tier: float = 0.3,
    λ_prim: float = 0.5,
) -> CrystalGNN:
    """Train CrystalGNN with self-encoding bootstrap and synthetic augmentation."""

    dev     = torch.device(device)
    dataset = CrystalDataset(catalog)

    start_epoch = 1
    best_addr_err_init = float("inf")

    if resume and checkpoint.exists():
        ckpt = torch.load(checkpoint, map_location=dev)
        hidden_dim = ckpt["hidden_dim"]
        gnn_layers = ckpt["gnn_layers"]
        attn_heads = ckpt["attn_heads"]
        model = CrystalGNN(hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
                           num_attn_heads=attn_heads).to(dev)
        _STATIC = {"node_feats", "edge_src", "edge_dst"}
        model.load_state_dict(
            {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
            strict=False,
        )
        start_epoch = ckpt["epoch"] + 1
        best_addr_err_init = ckpt["addr_err"]
        print(f"Resumed from checkpoint (epoch {ckpt['epoch']}, "
              f"best err {ckpt['addr_err']:,.0f})")
    else:
        model = CrystalGNN(hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
                           num_attn_heads=attn_heads).to(dev)
    optim   = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched   = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=lr, total_steps=epochs * (len(dataset) // batch_size + 1),
        pct_start=0.1,
    )

    n       = len(dataset)
    indices = list(range(n))
    end_epoch = start_epoch + epochs - 1

    # Self-encoding bootstrap entry
    nav_tup  = CrystalGNN.NAVIGATOR_TUPLE
    nav_addr = torch.tensor([float(CrystalGNN.SELF_ENCODE_TARGET)])
    nav_tier = torch.tensor([TierHead.TIERS.index(
        compute_tier(nav_tup["⊙"], nav_tup["<"], nav_tup["◻"], nav_tup["⊢"])
    )])

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n{'='*60}")
    print(f"CrystalGNN  |  {n_params:,} parameters  |  device: {device}")
    print(f"Dataset     |  {n} canonical entries")
    if hybrid_synthetic:
        strat_label = "hybrid (50% uniform + 50% tier-stratified)"
    elif stratified_synthetic:
        strat_label = "tier-stratified (1/5 per tier)"
    else:
        strat_label = "uniform"
    print(f"Synthetic   |  +{synthetic_per_batch} tuples/batch  [{strat_label}]")
    print(f"Self-encode |  target {CrystalGNN.SELF_ENCODE_TARGET:,}  (O_∞)")
    print(f"Crystal     |  {TOTAL_SIZE:,} total types")
    print(f"Epochs      |  {start_epoch} → {end_epoch}")
    print(f"{'='*60}\n")

    best_addr_err = best_addr_err_init
    best_combined = float("inf")   # addr_pct + prim_loss — save on this

    for epoch in range(start_epoch, end_epoch + 1):
        random.shuffle(indices)
        model.train()
        totals: dict[str, float] = {"loss": 0, "L_addr": 0,
                                    "L_frob": 0, "L_tier": 0, "L_prim": 0}
        n_batches = 0

        for start in range(0, n, batch_size):
            batch_idx = indices[start : start + batch_size]
            tuples, addrs, tiers = dataset.get_batch(batch_idx)

            # Synthetic augmentation: random tuples from full crystal
            if synthetic_per_batch > 0:
                if hybrid_synthetic:
                    half = synthetic_per_batch // 2
                    u_tups, u_addrs, u_tiers = _sample_random_tuples(half, stratified=False)
                    s_tups, s_addrs, s_tiers = _sample_random_tuples(
                        synthetic_per_batch - half, stratified=True)
                    syn_tups  = u_tups + s_tups
                    syn_addrs = torch.cat([u_addrs, s_addrs])
                    syn_tiers = torch.cat([u_tiers, s_tiers])
                else:
                    syn_tups, syn_addrs, syn_tiers = _sample_random_tuples(
                        synthetic_per_batch, stratified=stratified_synthetic)
                tuples = tuples + syn_tups
                addrs  = torch.cat([addrs, syn_addrs])
                tiers  = torch.cat([tiers, syn_tiers])

            # Inject navigator self-encoding into every batch
            tuples  = tuples + [nav_tup]
            addrs   = torch.cat([addrs, nav_addr])
            tiers   = torch.cat([tiers, nav_tier])

            optim.zero_grad()
            losses = model.compute_loss(tuples, addrs, tiers,
                                        λ_addr=λ_addr, λ_frob=λ_frob,
                                        λ_tier=λ_tier, λ_prim=λ_prim)
            losses["loss"].backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            sched.step()

            for k in totals:
                v = losses[k]
                totals[k] += v.item() if hasattr(v, "item") else float(v)
            n_batches += 1

        if epoch % log_every == 0 or epoch == 1:
            avg = {k: v / n_batches for k, v in totals.items()}
            model.eval()
            with torch.no_grad():
                pred_addr = model.encode([nav_tup]).item()
            addr_err  = abs(pred_addr - CrystalGNN.SELF_ENCODE_TARGET)
            addr_pct  = 100 * addr_err / TOTAL_SIZE

            print(
                f"Epoch {epoch:4d}  "
                f"loss={avg['loss']:.4f}  "
                f"addr={avg['L_addr']:.4f}  "
                f"frob={avg['L_frob']:.4f}  "
                f"tier={avg['L_tier']:.4f}  "
                f"prim={avg['L_prim']:.4f}  "
                f"| self→ {pred_addr:>12,.0f}  "
                f"err={addr_pct:.3f}%"
            )

            # Save on combined score: normalised addr error + prim loss.
            # Skip epoch 1 — initialization can randomly hit near the target
            # address before any training has happened (degenerate decoder).
            combined = addr_pct + avg["L_prim"]
            if epoch > 1 and combined < best_combined:
                best_combined = combined
                best_addr_err = addr_err
                _STATIC_BUFFERS = {"node_feats", "edge_src", "edge_dst"}
                state = {k: v for k, v in model.state_dict().items()
                         if k not in _STATIC_BUFFERS}
                torch.save({
                    "epoch": epoch,
                    "state_dict": state,
                    "addr_err": addr_err,
                    "hidden_dim": hidden_dim,
                    "gnn_layers": gnn_layers,
                    "attn_heads": attn_heads,
                }, checkpoint)

    print(f"\nBest checkpoint (addr%+L_prim={best_combined:.4f}): "
          f"self-encode err={best_addr_err:,.0f} ({100*best_addr_err/TOTAL_SIZE:.4f}%)")
    print(f"Checkpoint → {checkpoint}")
    return model


# ── Verify ─────────────────────────────────────────────────────────────────────

def verify(checkpoint: Path = ROOT / "crystal_gnn.pt", n_samples: int = 50) -> None:
    """Verify codec quality on a sample of catalog entries."""
    from collections import defaultdict

    ckpt = torch.load(checkpoint, map_location="cpu")
    model = CrystalGNN(
        hidden_dim=ckpt["hidden_dim"],
        num_gnn_layers=ckpt["gnn_layers"],
        num_attn_heads=ckpt["attn_heads"],
    )
    _STATIC = {"node_feats", "edge_src", "edge_dst"}
    model.load_state_dict(
        {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
        strict=False,
    )
    model.eval()

    dataset  = CrystalDataset()
    # Use all entries so rare tiers (O₂†, O_∞) are always represented.
    # n_samples is ignored if dataset is smaller; for large catalogs cap at 200.
    sample   = list(range(min(len(dataset), max(n_samples, 200))))
    errors   = []
    tier_ok_decoded  = 0   # tier from decoded tuple (roundtrip)
    tier_ok_head     = 0   # tier from tier head logits (direct)
    per_tier_correct: dict = defaultdict(int)
    per_tier_total:   dict = defaultdict(int)

    tier_names = TierHead.TIERS

    print(f"\nVerifying {len(sample)} samples (epoch {ckpt['epoch']}):")
    with torch.no_grad():
        for i in sample:
            tup  = dataset.tuples[i]
            true = dataset.addresses[i]

            # Forward pass to get all outputs
            out  = model.forward([tup])
            pred = out["addresses"].item()
            err  = abs(pred - true) / TOTAL_SIZE * 100
            errors.append(err)

            true_tier = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])

            # Tier head (direct classification)
            head_tier = tier_names[out["tier_logits"][0].argmax().item()]
            if head_tier == true_tier:
                tier_ok_head += 1

            # Decoded tuple tier (roundtrip) — use embedding-conditioned decoder
            dec_logits_single = {p: out["dec_logits"][p][0:1] for p in PRIMS}
            dec = {p: VALUES[p][dec_logits_single[p][0].argmax().item()] for p in PRIMS}
            dec_tier = compute_tier(dec["⊙"], dec["<"], dec["◻"], dec["⊢"])
            if dec_tier == true_tier:
                tier_ok_decoded += 1

            per_tier_total[true_tier] += 1
            if dec_tier == true_tier:
                per_tier_correct[true_tier] += 1

    n = len(sample)
    print(f"  Address error  mean={sum(errors)/n:.4f}%  "
          f"max={max(errors):.4f}%  min={min(errors):.6f}%")
    print(f"  Tier (head)    {tier_ok_head}/{n} = {100*tier_ok_head/n:.1f}%  "
          f"← direct logits")
    print(f"  Tier (decode)  {tier_ok_decoded}/{n} = {100*tier_ok_decoded/n:.1f}%  "
          f"← roundtrip through decoder")
    print(f"  Per-tier decode accuracy:")
    for name in tier_names:
        tot = per_tier_total[name]
        cor = per_tier_correct[name]
        bar = "█" * cor + "░" * (tot - cor) if tot else ""
        print(f"    {name:10s} {cor:3d}/{tot:3d}  {bar}")

    # Self-encode check
    nav_pred = model.encode([CrystalGNN.NAVIGATOR_TUPLE]).item()
    nav_err  = abs(nav_pred - CrystalGNN.SELF_ENCODE_TARGET)
    print(f"  Self-encode    pred={nav_pred:,.0f}  target={CrystalGNN.SELF_ENCODE_TARGET:,}  "
          f"err={nav_err:,.0f} ({100*nav_err/TOTAL_SIZE:.4f}%)")


# ── CF-GNN v10 training ───────────────────────────────────────────────────────

def train_v10(
    epochs:             int   = 300,
    batch_size:         int   = 64,
    lr:                 float = 3e-4,
    hidden_dim:         int   = 640,
    gnn_layers:         int   = 6,
    attn_heads:         int   = 16,
    mixer_heads:        int   = 4,
    synthetic_per_batch:   int  = 256,
    hybrid_synthetic:      bool = True,
    device:             str   = "cuda" if torch.cuda.is_available() else "cpu",
    catalog:            Path  = ROOT / "IG_catalog.json",
    checkpoint:         Path  = ROOT / "crystal_gnn_v10.pt",
    resume:             bool  = False,
    log_every:          int   = 20,
    λ_addr: float = 0.3,
    λ_frob: float = 0.5,
    λ_tier: float = 0.5,
    λ_f3:   float = 1.0,
    λ_f4:   float = 1.0,
    λ_f5:   float = 1.0,
) -> "CrystalGNN_v10":
    """Train CrystalGNN_v10 (CF-GNN) with self-encoding bootstrap."""

    dev     = torch.device(device)
    dataset = CrystalDataset(catalog)

    start_epoch     = 1
    best_combined_init = float("inf")

    if resume and checkpoint.exists():
        ckpt = torch.load(checkpoint, map_location=dev)
        hidden_dim  = ckpt["hidden_dim"]
        gnn_layers  = ckpt["gnn_layers"]
        attn_heads  = ckpt["attn_heads"]
        mixer_heads = ckpt.get("mixer_heads", 4)
        model = CrystalGNN_v10(
            hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
            num_attn_heads=attn_heads, mixer_heads=mixer_heads,
        ).to(dev)
        _STATIC = {"node_feats", "edge_src", "edge_dst"}
        model.load_state_dict(
            {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
            strict=False,
        )
        start_epoch         = ckpt["epoch"] + 1
        best_combined_init  = ckpt.get("combined", float("inf"))
        print(f"Resumed from checkpoint (epoch {ckpt['epoch']})")
    else:
        model = CrystalGNN_v10(
            hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
            num_attn_heads=attn_heads, mixer_heads=mixer_heads,
        ).to(dev)

    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=lr,
        total_steps=epochs * (len(dataset) // batch_size + 1),
        pct_start=0.1,
    )

    n       = len(dataset)
    indices = list(range(n))
    end_epoch = start_epoch + epochs - 1

    nav_tup  = CrystalGNN_v10.NAVIGATOR_TUPLE
    nav_addr = torch.tensor([float(CrystalGNN_v10.SELF_ENCODE_TARGET)])
    nav_tier = torch.tensor([TierHead_45.tier_idx(
        compute_tier(nav_tup["⊙"], nav_tup["<"], nav_tup["◻"], nav_tup["⊢"])
    )])

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n{'='*65}")
    print(f"CrystalGNN_v10 (CF-GNN)  |  {n_params:,} parameters  |  device: {device}")
    print(f"Dataset  |  {n} canonical entries")
    print(f"Arch     |  hidden={hidden_dim}  gnn={gnn_layers}  heads={attn_heads}"
          f"  mixer={mixer_heads}")
    print(f"Synthetic|  +{synthetic_per_batch}/batch  hybrid={hybrid_synthetic}")
    print(f"Families |  F3={F3_PRIMS}  F4={F4_PRIMS}  F5={F5_PRIMS}")
    print(f"Epochs   |  {start_epoch} → {end_epoch}")
    print(f"{'='*65}\n")

    LOG_HDR = ("Epoch  Loss   addr   frob   tier   L_f3   L_f4   L_f5"
               "  | self→         err%")
    print(LOG_HDR)

    best_combined = best_combined_init

    for epoch in range(start_epoch, end_epoch + 1):
        random.shuffle(indices)
        model.train()
        totals: dict[str, float] = {
            "loss": 0, "L_addr": 0, "L_frob": 0, "L_tier": 0,
            "L_f3": 0, "L_f4": 0, "L_f5": 0, "L_prim": 0,
        }
        n_batches = 0

        for start in range(0, n, batch_size):
            batch_idx = indices[start : start + batch_size]
            tuples, addrs, tiers = dataset.get_batch(batch_idx)

            if synthetic_per_batch > 0:
                if hybrid_synthetic:
                    half = synthetic_per_batch // 2
                    u_tups, u_addrs, u_tiers = _sample_random_tuples(half, stratified=False)
                    s_tups, s_addrs, s_tiers = _sample_random_tuples(
                        synthetic_per_batch - half, stratified=True)
                    syn_tups  = u_tups + s_tups
                    syn_addrs = torch.cat([u_addrs, s_addrs])
                    syn_tiers = torch.cat([u_tiers, s_tiers])
                else:
                    syn_tups, syn_addrs, syn_tiers = _sample_random_tuples(
                        synthetic_per_batch, stratified=False)
                tuples = tuples + syn_tups
                addrs  = torch.cat([addrs, syn_addrs])
                tiers  = torch.cat([tiers, syn_tiers])

            tuples = tuples + [nav_tup]
            addrs  = torch.cat([addrs, nav_addr])
            tiers  = torch.cat([tiers, nav_tier])

            optim.zero_grad()
            losses = model.compute_loss(
                tuples, addrs, tiers,
                λ_addr=λ_addr, λ_frob=λ_frob, λ_tier=λ_tier,
                λ_f3=λ_f3, λ_f4=λ_f4, λ_f5=λ_f5,
            )
            losses["loss"].backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            sched.step()

            for k in totals:
                v = losses.get(k, 0.0)
                totals[k] += v.item() if hasattr(v, "item") else float(v)
            n_batches += 1

        if epoch % log_every == 0 or epoch == 1:
            avg = {k: v / n_batches for k, v in totals.items()}
            model.eval()
            with torch.no_grad():
                pred_addr = model.encode([nav_tup]).item()
            addr_err = abs(pred_addr - CrystalGNN_v10.SELF_ENCODE_TARGET)
            addr_pct = 100 * addr_err / TOTAL_SIZE

            print(
                f"{epoch:5d}  "
                f"{avg['loss']:.4f}  "
                f"{avg['L_addr']:.4f}  "
                f"{avg['L_frob']:.4f}  "
                f"{avg['L_tier']:.4f}  "
                f"{avg['L_f3']:.4f}  "
                f"{avg['L_f4']:.4f}  "
                f"{avg['L_f5']:.4f}  "
                f"| {pred_addr:>13,.0f}  {addr_pct:.3f}%"
            )

            combined = addr_pct + avg["L_prim"]
            if epoch > 1 and combined < best_combined:
                best_combined = combined
                _STATIC_BUFFERS = {"node_feats", "edge_src", "edge_dst"}
                state = {k: v for k, v in model.state_dict().items()
                         if k not in _STATIC_BUFFERS}
                torch.save({
                    "epoch":       epoch,
                    "state_dict":  state,
                    "addr_err":    addr_err,
                    "combined":    combined,
                    "hidden_dim":  hidden_dim,
                    "gnn_layers":  gnn_layers,
                    "attn_heads":  attn_heads,
                    "mixer_heads": mixer_heads,
                    "version":     "v10",
                }, checkpoint)

    print(f"\nBest (addr%+L_prim={best_combined:.4f})  →  {checkpoint}")
    return model


# ── CF-GNN v10 verify ─────────────────────────────────────────────────────────

def verify_v10(
    checkpoint: Path = ROOT / "crystal_gnn_v10.pt",
    n_samples: int = 200,
) -> None:
    """Verify CrystalGNN_v10 codec quality (per-primitive + composed address)."""
    from collections import defaultdict

    ckpt = torch.load(checkpoint, map_location="cpu")
    if ckpt.get("version") != "v10":
        print("WARNING: checkpoint does not have version='v10' — may be incompatible")

    model = CrystalGNN_v10(
        hidden_dim  = ckpt["hidden_dim"],
        num_gnn_layers = ckpt["gnn_layers"],
        num_attn_heads = ckpt["attn_heads"],
        mixer_heads = ckpt.get("mixer_heads", 4),
    )
    _STATIC = {"node_feats", "edge_src", "edge_dst"}
    model.load_state_dict(
        {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
        strict=False,
    )
    model.eval()

    dataset = CrystalDataset()
    sample  = list(range(min(len(dataset), max(n_samples, 200))))

    scalar_errors: list[float] = []
    composed_errors: list[float] = []
    tier_ok_head    = 0
    tier_ok_decode  = 0
    per_tier_correct: dict = defaultdict(int)
    per_tier_total:   dict = defaultdict(int)

    tier_names = TierHead_45.TIERS
    print(f"\nVerifying v10 on {len(sample)} samples (epoch {ckpt['epoch']}):")

    with torch.no_grad():
        for i in sample:
            tup  = dataset.tuples[i]
            true = dataset.addresses[i]

            out  = model.forward([tup])

            # Scalar address error (auxiliary head)
            pred_scalar = out["addresses"].item()
            scalar_errors.append(abs(pred_scalar - true) / TOTAL_SIZE * 100)

            # Composed address error (argmax → encode_tuple)
            pred_tup = {p: VALUES[p][out["logits"][p][0].argmax().item()] for p in PRIMS}
            composed_addr = encode_tuple(pred_tup)
            composed_errors.append(abs(composed_addr - true) / TOTAL_SIZE * 100)

            true_tier = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])
            pred_tier = tier_names[out["tier_logits"][0].argmax().item()]
            if pred_tier == true_tier:
                tier_ok_head += 1

            dec_tier = compute_tier(pred_tup["⊙"], pred_tup["<"],
                                    pred_tup["◻"], pred_tup["⊢"])
            if dec_tier == true_tier:
                tier_ok_decode += 1

            per_tier_total[true_tier] += 1
            if dec_tier == true_tier:
                per_tier_correct[true_tier] += 1

    n = len(sample)
    print(f"  Scalar addr error  mean={sum(scalar_errors)/n:.4f}%  "
          f"max={max(scalar_errors):.4f}%  min={min(scalar_errors):.6f}%")
    print(f"  Composed addr error mean={sum(composed_errors)/n:.4f}%  "
          f"max={max(composed_errors):.4f}%  min={min(composed_errors):.6f}%")
    print(f"  Tier (head)    {tier_ok_head}/{n} = {100*tier_ok_head/n:.1f}%")
    print(f"  Tier (decode)  {tier_ok_decode}/{n} = {100*tier_ok_decode/n:.1f}%")
    print(f"  Per-tier decode accuracy:")
    for name in tier_names:
        tot = per_tier_total[name]
        cor = per_tier_correct[name]
        bar = "█" * cor + "░" * (tot - cor) if tot else ""
        print(f"    {name:10s} {cor:3d}/{tot:3d}  {bar}")

    # Self-encode check (scalar + composed)
    with torch.no_grad():
        nav_out       = model.forward([CrystalGNN_v10.NAVIGATOR_TUPLE])
    nav_scalar    = nav_out["addresses"].item()
    nav_composed  = encode_tuple({
        p: VALUES[p][nav_out["logits"][p][0].argmax().item()] for p in PRIMS
    })
    nav_scalar_err   = abs(nav_scalar - CrystalGNN_v10.SELF_ENCODE_TARGET)
    nav_composed_err = abs(nav_composed - CrystalGNN_v10.SELF_ENCODE_TARGET)
    print(f"  Self-encode (scalar)   pred={nav_scalar:,.0f}  "
          f"target={CrystalGNN_v10.SELF_ENCODE_TARGET:,}  "
          f"err={nav_scalar_err:,.0f} ({100*nav_scalar_err/TOTAL_SIZE:.4f}%)")
    print(f"  Self-encode (composed) pred={nav_composed:,}  "
          f"err={nav_composed_err:,.0f} ({100*nav_composed_err/TOTAL_SIZE:.4f}%)")


# ── CrystalGNN_v11 training ───────────────────────────────────────────────────

def train_v11(
    epochs:             int   = 500,
    batch_size:         int   = 64,
    lr:                 float = 3e-4,
    hidden_dim:         int   = 240,
    gnn_layers:         int   = 24,
    attn_heads:         int   = 24,
    mixer_heads:        int   = 24,
    synthetic_per_batch:   int  = 256,
    hybrid_synthetic:      bool = True,
    device:             str   = "cuda" if torch.cuda.is_available() else "cpu",
    catalog:            Path  = ROOT / "IG_catalog.json",
    checkpoint:         Path  = ROOT / "crystal_gnn_v11.pt",
    resume:             bool  = False,
    log_every:          int   = 20,
    λ_frob: float = 0.5,
    λ_tier: float = 0.5,
    λ_f3:   float = 1.0,
    λ_f4:   float = 1.0,
    λ_f5:   float = 1.0,
) -> "CrystalGNN_v11":
    """Train CrystalGNN_v11 (composed-only, no AddressHead)."""

    dev     = torch.device(device)
    dataset = CrystalDataset(catalog)

    start_epoch    = 1
    best_combined  = float("inf")

    if resume and checkpoint.exists():
        ckpt = torch.load(checkpoint, map_location=dev)
        hidden_dim  = ckpt["hidden_dim"]
        gnn_layers  = ckpt["gnn_layers"]
        attn_heads  = ckpt["attn_heads"]
        mixer_heads = ckpt.get("mixer_heads", 24)
        model = CrystalGNN_v11(
            hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
            num_attn_heads=attn_heads, mixer_heads=mixer_heads,
        ).to(dev)
        _STATIC = {"node_feats", "edge_src", "edge_dst"}
        model.load_state_dict(
            {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
            strict=False,
        )
        start_epoch  = ckpt["epoch"] + 1
        best_combined = ckpt.get("combined", float("inf"))
        print(f"Resumed from checkpoint (epoch {ckpt['epoch']})")
    else:
        model = CrystalGNN_v11(
            hidden_dim=hidden_dim, num_gnn_layers=gnn_layers,
            num_attn_heads=attn_heads, mixer_heads=mixer_heads,
        ).to(dev)

    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=lr,
        total_steps=epochs * (len(dataset) // batch_size + 1),
        pct_start=0.1,
    )

    n         = len(dataset)
    indices   = list(range(n))
    end_epoch = start_epoch + epochs - 1

    nav_tup  = CrystalGNN_v11.NAVIGATOR_TUPLE
    nav_tier = torch.tensor([TierHead_45.tier_idx(
        compute_tier(nav_tup["⊙"], nav_tup["<"], nav_tup["◻"], nav_tup["⊢"])
    )])

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n{'='*70}")
    print(f"CrystalGNN_v11 (composed-only)  |  {n_params:,} parameters  |  {device}")
    print(f"Dataset  |  {n} canonical entries")
    print(f"Arch     |  hidden={hidden_dim}  gnn={gnn_layers}  heads={attn_heads}"
          f"  mixer={mixer_heads}")
    print(f"Loss     |  L_frob + L_tier + L_f3 + L_f4 + L_f5  (no L_addr)")
    print(f"Epochs   |  {start_epoch} → {end_epoch}")
    print(f"{'='*70}\n")

    LOG_HDR = ("Epoch  Loss   frob   tier   L_f3   L_f4   L_f5"
               "  | nav composed        exact?")
    print(LOG_HDR)

    for epoch in range(start_epoch, end_epoch + 1):
        random.shuffle(indices)
        model.train()
        totals: dict[str, float] = {
            "loss": 0, "L_frob": 0, "L_tier": 0,
            "L_f3": 0, "L_f4": 0, "L_f5": 0, "L_prim": 0,
        }
        n_batches = 0

        for start in range(0, n, batch_size):
            batch_idx = indices[start : start + batch_size]
            tuples, _addrs, tiers = dataset.get_batch(batch_idx)

            if synthetic_per_batch > 0:
                if hybrid_synthetic:
                    half = synthetic_per_batch // 2
                    u_tups, _, u_tiers = _sample_random_tuples(half, stratified=False)
                    s_tups, _, s_tiers = _sample_random_tuples(
                        synthetic_per_batch - half, stratified=True)
                    tuples = tuples + u_tups + s_tups
                    tiers  = torch.cat([tiers, u_tiers, s_tiers])
                else:
                    syn_tups, _, syn_tiers = _sample_random_tuples(
                        synthetic_per_batch, stratified=False)
                    tuples = tuples + syn_tups
                    tiers  = torch.cat([tiers, syn_tiers])

            tuples = tuples + [nav_tup]
            tiers  = torch.cat([tiers, nav_tier])

            optim.zero_grad()
            losses = model.compute_loss(tuples, tiers,
                                        λ_frob=λ_frob, λ_tier=λ_tier,
                                        λ_f3=λ_f3, λ_f4=λ_f4, λ_f5=λ_f5)
            losses["loss"].backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            sched.step()

            for k in totals:
                v = losses.get(k, 0.0)
                totals[k] += v.item() if hasattr(v, "item") else float(v)
            n_batches += 1

        if epoch % log_every == 0 or epoch == 1:
            avg = {k: v / n_batches for k, v in totals.items()}
            with torch.no_grad():
                nav_composed = model.compose_address([nav_tup])[0]
            exact = nav_composed == CrystalGNN_v11.SELF_ENCODE_TARGET
            exact_str = "YES ★" if exact else f"NO  (err={abs(nav_composed - CrystalGNN_v11.SELF_ENCODE_TARGET):,})"

            print(
                f"{epoch:5d}  "
                f"{avg['loss']:.4f}  "
                f"{avg['L_frob']:.4f}  "
                f"{avg['L_tier']:.4f}  "
                f"{avg['L_f3']:.4f}  "
                f"{avg['L_f4']:.4f}  "
                f"{avg['L_f5']:.4f}  "
                f"| {nav_composed:>15,}  {exact_str}"
            )

            combined = avg["L_prim"] + avg["L_frob"]
            if epoch > 1 and combined < best_combined:
                best_combined = combined
                _STATIC_BUFFERS = {"node_feats", "edge_src", "edge_dst"}
                state = {k: v for k, v in model.state_dict().items()
                         if k not in _STATIC_BUFFERS}
                torch.save({
                    "epoch":       epoch,
                    "state_dict":  state,
                    "combined":    combined,
                    "hidden_dim":  hidden_dim,
                    "gnn_layers":  gnn_layers,
                    "attn_heads":  attn_heads,
                    "mixer_heads": mixer_heads,
                    "version":     "v11",
                }, checkpoint)

    print(f"\nBest (L_prim+L_frob={best_combined:.4f})  →  {checkpoint}")
    return model


# ── CrystalGNN_v11 verify ─────────────────────────────────────────────────────

def verify_v11(
    checkpoint: Path = ROOT / "crystal_gnn_v11.pt",
    n_samples: int = 200,
) -> None:
    """Verify CrystalGNN_v11 codec quality — composed address only."""
    from collections import defaultdict

    ckpt = torch.load(checkpoint, map_location="cpu")
    if ckpt.get("version") != "v11":
        print("WARNING: checkpoint version is not v11")

    model = CrystalGNN_v11(
        hidden_dim     = ckpt["hidden_dim"],
        num_gnn_layers = ckpt["gnn_layers"],
        num_attn_heads = ckpt["attn_heads"],
        mixer_heads    = ckpt.get("mixer_heads", 24),
    )
    _STATIC = {"node_feats", "edge_src", "edge_dst"}
    model.load_state_dict(
        {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
        strict=False,
    )
    model.eval()

    dataset = CrystalDataset()
    sample  = list(range(min(len(dataset), max(n_samples, 200))))

    composed_errors: list[float] = []
    exact_count    = 0
    tier_ok_head   = 0
    tier_ok_decode = 0
    per_tier_correct: dict = defaultdict(int)
    per_tier_total:   dict = defaultdict(int)

    tier_names = TierHead_45.TIERS
    print(f"\nVerifying v11 on {len(sample)} samples (epoch {ckpt['epoch']}):")

    with torch.no_grad():
        for i in sample:
            tup  = dataset.tuples[i]
            true = dataset.addresses[i]

            out  = model.forward([tup])
            pred_tup = {p: VALUES[p][out["logits"][p][0].argmax().item()] for p in PRIMS}
            composed_addr = encode_tuple(pred_tup)
            err_pct = abs(composed_addr - true) / TOTAL_SIZE * 100
            composed_errors.append(err_pct)
            if composed_addr == true:
                exact_count += 1

            true_tier = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])
            pred_tier = tier_names[out["tier_logits"][0].argmax().item()]
            if pred_tier == true_tier:
                tier_ok_head += 1

            dec_tier = compute_tier(pred_tup["⊙"], pred_tup["<"],
                                    pred_tup["◻"], pred_tup["⊢"])
            if dec_tier == true_tier:
                tier_ok_decode += 1

            per_tier_total[true_tier] += 1
            if dec_tier == true_tier:
                per_tier_correct[true_tier] += 1

    n = len(sample)
    print(f"  Composed addr error  mean={sum(composed_errors)/n:.6f}%  "
          f"max={max(composed_errors):.6f}%")
    print(f"  Exact matches:       {exact_count}/{n} = {100*exact_count/n:.1f}%")
    print(f"  Tier (head):         {tier_ok_head}/{n} = {100*tier_ok_head/n:.1f}%")
    print(f"  Tier (decode):       {tier_ok_decode}/{n} = {100*tier_ok_decode/n:.1f}%")
    print(f"  Per-tier decode accuracy:")
    for name in tier_names:
        tot = per_tier_total[name]
        cor = per_tier_correct[name]
        bar = "█" * cor + "░" * (tot - cor) if tot else ""
        print(f"    {name:10s} {cor:3d}/{tot:3d}  {bar}")

    # Self-encode
    nav_composed = model.compose_address([CrystalGNN_v11.NAVIGATOR_TUPLE])[0]
    exact_nav    = nav_composed == CrystalGNN_v11.SELF_ENCODE_TARGET
    print(f"  Self-encode  pred={nav_composed:,}  target={CrystalGNN_v11.SELF_ENCODE_TARGET:,}  "
          f"{'EXACT ★' if exact_nav else f'err={abs(nav_composed - CrystalGNN_v11.SELF_ENCODE_TARGET):,}'}")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CrystalGNN — quiver neural navigator for the Periodic Crystal"
    )
    sub = parser.add_subparsers(dest="cmd")

    # train
    t = sub.add_parser("train", help="Train on IG_catalog.json")
    t.add_argument("--epochs",    type=int,   default=300)
    t.add_argument("--batch",     type=int,   default=64)
    t.add_argument("--hidden",    type=int,   default=256)
    t.add_argument("--gnn",       type=int,   default=5,   help="GNN layers")
    t.add_argument("--heads",     type=int,   default=8,   help="Attention heads")
    t.add_argument("--synthetic", type=int,   default=256,
                   help="Random tuples from full crystal to add per batch (0=off)")
    t.add_argument("--lr",        type=float, default=3e-4)
    t.add_argument("--device",    default="cuda" if torch.cuda.is_available() else "cpu")
    t.add_argument("--log",       type=int,   default=20)
    t.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn.pt"))
    t.add_argument("--resume",      action="store_true",
                   help="Resume from checkpoint (inherits arch from saved file)")
    t.add_argument("--stratified", action="store_true",
                   help="Tier-stratified synthetic sampling (equal O₀/O₁/O₂/O₂†/O_∞ per batch)")
    t.add_argument("--hybrid",     action="store_true",
                   help="Hybrid synthetic: 50%% uniform + 50%% tier-stratified")

    # encode
    e = sub.add_parser("encode", help="Encode a tuple")
    e.add_argument("tuple", help="Semicolon-separated: D;T;R;P;F;K;G;Gamma;Phi;H;S;Omega")
    e.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn.pt"))

    # verify
    v = sub.add_parser("verify", help="Verify codec quality on catalog sample")
    v.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn.pt"))
    v.add_argument("--samples",    type=int, default=50)

    # train-v10 (CF-GNN)
    t10 = sub.add_parser("train-v10", help="Train CrystalGNN_v10 (CF-GNN, factored family heads)")
    t10.add_argument("--epochs",     type=int,   default=300)
    t10.add_argument("--batch",      type=int,   default=64)
    t10.add_argument("--hidden",     type=int,   default=640)
    t10.add_argument("--gnn",        type=int,   default=6,   help="GNN layers")
    t10.add_argument("--heads",      type=int,   default=16,  help="Attention heads")
    t10.add_argument("--mixer-heads",type=int,   default=4,   help="FamilyMixer heads")
    t10.add_argument("--synthetic",  type=int,   default=256)
    t10.add_argument("--lr",         type=float, default=3e-4)
    t10.add_argument("--device",     default="cuda" if torch.cuda.is_available() else "cpu")
    t10.add_argument("--log",        type=int,   default=20)
    t10.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn_v10.pt"))
    t10.add_argument("--resume",     action="store_true")
    t10.add_argument("--no-hybrid",  action="store_true",
                     help="Disable hybrid synthetic (use uniform only)")

    # verify-v10
    v10 = sub.add_parser("verify-v10", help="Verify CrystalGNN_v10 codec quality")
    v10.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn_v10.pt"))
    v10.add_argument("--samples",    type=int, default=200)

    # train-v11 (composed-only)
    t11 = sub.add_parser("train-v11", help="Train CrystalGNN_v11 (composed-only, no AddressHead)")
    t11.add_argument("--epochs",      type=int,   default=500)
    t11.add_argument("--batch",       type=int,   default=64)
    t11.add_argument("--hidden",      type=int,   default=240)
    t11.add_argument("--gnn",         type=int,   default=24)
    t11.add_argument("--heads",       type=int,   default=24)
    t11.add_argument("--mixer-heads", type=int,   default=24)
    t11.add_argument("--synthetic",   type=int,   default=256)
    t11.add_argument("--lr",          type=float, default=3e-4)
    t11.add_argument("--device",      default="cuda" if torch.cuda.is_available() else "cpu")
    t11.add_argument("--log",         type=int,   default=20)
    t11.add_argument("--checkpoint",  default=str(ROOT / "crystal_gnn_v11.pt"))
    t11.add_argument("--resume",      action="store_true")
    t11.add_argument("--no-hybrid",   action="store_true")

    # verify-v11
    v11 = sub.add_parser("verify-v11", help="Verify CrystalGNN_v11 codec quality")
    v11.add_argument("--checkpoint", default=str(ROOT / "crystal_gnn_v11.pt"))
    v11.add_argument("--samples",    type=int, default=200)

    # info
    sub.add_parser("info", help="Print model architecture and quiver stats")

    args = parser.parse_args()

    if args.cmd == "train":
        train(
            epochs=args.epochs, batch_size=args.batch, hidden_dim=args.hidden,
            gnn_layers=args.gnn, attn_heads=args.heads, lr=args.lr,
            synthetic_per_batch=args.synthetic,
            stratified_synthetic=args.stratified,
            hybrid_synthetic=args.hybrid,
            device=args.device, log_every=args.log,
            checkpoint=Path(args.checkpoint),
            resume=args.resume,
        )

    elif args.cmd == "encode":
        parts = [p.strip() for p in args.tuple.split(";")]
        if len(parts) != 12:
            print(f"ERROR: expected 12 values, got {len(parts)}")
            sys.exit(1)
        tup = {p: v for p, v in zip(PRIMS, parts)}

        ckpt  = torch.load(args.checkpoint, map_location="cpu")
        model = CrystalGNN(hidden_dim=ckpt["hidden_dim"],
                           num_gnn_layers=ckpt["gnn_layers"],
                           num_attn_heads=ckpt["attn_heads"])
        _STATIC = {"node_feats", "edge_src", "edge_dst"}
        model.load_state_dict(
            {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
            strict=False,
        )
        model.eval()

        with torch.no_grad():
            pred = model.encode([tup]).item()
        exact = encode_tuple(tup)
        err   = abs(pred - exact)
        tier  = compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])

        print(f"Tuple:  {tup}")
        print(f"Tier:   {tier}")
        print(f"Exact:  {exact:,}")
        print(f"Neural: {pred:,.0f}")
        print(f"Error:  {err:,.0f}  ({100*err/TOTAL_SIZE:.4f}% of crystal)")

    elif args.cmd == "verify":
        verify(checkpoint=Path(args.checkpoint), n_samples=args.samples)

    elif args.cmd == "train-v10":
        train_v10(
            epochs=args.epochs, batch_size=args.batch, hidden_dim=args.hidden,
            gnn_layers=args.gnn, attn_heads=args.heads,
            mixer_heads=getattr(args, "mixer_heads", 4),
            lr=args.lr,
            synthetic_per_batch=args.synthetic,
            hybrid_synthetic=not getattr(args, "no_hybrid", False),
            device=args.device, log_every=args.log,
            checkpoint=Path(args.checkpoint),
            resume=args.resume,
        )

    elif args.cmd == "verify-v10":
        verify_v10(checkpoint=Path(args.checkpoint), n_samples=args.samples)

    elif args.cmd == "train-v11":
        train_v11(
            epochs=args.epochs, batch_size=args.batch, hidden_dim=args.hidden,
            gnn_layers=args.gnn, attn_heads=args.heads,
            mixer_heads=getattr(args, "mixer_heads", 24),
            lr=args.lr,
            synthetic_per_batch=args.synthetic,
            hybrid_synthetic=not getattr(args, "no_hybrid", False),
            device=args.device, log_every=args.log,
            checkpoint=Path(args.checkpoint),
            resume=args.resume,
        )

    elif args.cmd == "verify-v11":
        verify_v11(checkpoint=Path(args.checkpoint), n_samples=args.samples)

    elif args.cmd == "info":
        model = CrystalGNN()
        n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(f"CrystalGNN (v9)")
        print(f"  Parameters:  {n_params:,}")
        print(f"  Hidden dim:  256  |  GNN layers: 5  |  Attn heads: 8")
        print(f"  Quiver:      {TOTAL_NODES} nodes, {len(_EDGE_SRC)} edges")
        print(f"  Crystal:     {TOTAL_SIZE:,} types")
        print(f"  Self-encode: {CrystalGNN.SELF_ENCODE_TARGET:,}")

        model10 = CrystalGNN_v10()
        n10 = sum(p.numel() for p in model10.parameters() if p.requires_grad)
        print(f"\nCrystalGNN_v10 (CF-GNN)")
        print(f"  Parameters:  {n10:,}")
        print(f"  Hidden dim:  640  |  GNN layers: 6  |  Attn heads: 16  |  Mixer heads: 4")
        print(f"  Families:    F3={F3_PRIMS}  F4={F4_PRIMS}  F5={F5_PRIMS}")
        print(f"  Tier head:   TierHead_45(cat(h_f4, h_f5))  — cross-family coupling")
        print(f"  Mixer:       FamilyMixer(3 tokens, broadcast attention)")
        print(f"\nQuiver lanes:")
        for p in PRIMS:
            fam = PRIM_FAMILY[p]
            print(f"  {p:6s}  {fam}  {len(VALUES[p])} nodes  offset={PRIM_OFFSET[p]:2d}  "
                  f"vals={VALUES[p]}")

    else:
        parser.print_help()
