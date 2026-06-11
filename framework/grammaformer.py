"""
GrammaFormer — A Grammar-Native Transformer Architecture.

Every architectural component maps 1:1 to one of the agent's 12 O_∞ primitives.
Grafts onto a Qwen3 base via QLoRA. Selectable via --model grammaformer.

Agent tuple (Lean-verified, AgentSelf.lean):
  <Ð_ω; Þ_¨; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙_ÿ; Ħ_A; Σ_S; Ω_z>
"""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Winding-Modulated Positional Encoding — Ω_z
# ═══════════════════════════════════════════════════════════════════════════════

class WindingPositionalEncoding(nn.Module):
    """Sinusoidal PE phase-shifted by winding counter ω."""

    def __init__(self, d_model: int, max_len: int = 32768):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div = torch.exp(torch.arange(0, d_model, 2).float() *
                        (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div)
        pe[:, 1::2] = torch.cos(position * div)
        self.register_buffer('base_pe', pe.unsqueeze(0))  # (1, max_len, d_model)
        self.d_model = d_model

    def forward(self, x: torch.Tensor, winding: int = 0) -> torch.Tensor:
        """x: (batch, seq_len, d_model). winding: integer winding counter."""
        seq_len = x.size(1)
        shift = winding * 0.0625 * math.pi  # ω modulates by π/16 per winding
        if shift == 0:
            return x + self.base_pe[:, :seq_len, :]
        # Phase-shifted PE
        pe = self.base_pe[:, :seq_len, :].clone()
        pe_even = pe[:, :, 0::2]
        pe_odd = pe[:, :, 1::2]
        pe[:, :, 0::2] = pe_even * math.cos(shift) - pe_odd * math.sin(shift)
        pe[:, :, 1::2] = pe_even * math.sin(shift) + pe_odd * math.cos(shift)
        return x + pe.to(x.device, dtype=x.dtype)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Two-Slot State Register — Ħ_A
# ═══════════════════════════════════════════════════════════════════════════════

class TwoSlotRegister(nn.Module):
    """Stores prior two states. Ħ_A: 2-step Markov memory."""

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model
        self.register_proj = nn.Linear(d_model * 2, d_model)
        self.r1: Optional[torch.Tensor] = None  # t-1
        self.r2: Optional[torch.Tensor] = None  # t-2

    def set_state(self, h: torch.Tensor):
        """h: pooled state vector (d_model,) or (batch, d_model).
        Always stored as (1, d_model) so batch size changes between forward
        passes don't corrupt the register injection in the next call.
        """
        if h.dim() > 1:
            h = h.mean(dim=0, keepdim=True)  # (B, d_model) → (1, d_model)
        elif h.dim() == 1:
            h = h.unsqueeze(0)               # (d_model,) → (1, d_model)
        self.r2 = self.r1
        self.r1 = h.detach()

    def get_state(self) -> Optional[torch.Tensor]:
        """Returns projected [r1; r2] or None if registers are empty."""
        if self.r1 is None:
            return None
        r2 = self.r2 if self.r2 is not None else torch.zeros_like(self.r1)
        return self.register_proj(torch.cat([self.r1, r2], dim=-1))

    def reset(self):
        self.r1 = None
        self.r2 = None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Tensor Product Attention — Þ_¨
# ═══════════════════════════════════════════════════════════════════════════════

class TensorProductAttention(nn.Module):
    """Q⊗K via rank-1 bottleneck. Irreducible interaction (Þ_¨), not QK^T."""

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.0):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.d_model = d_model

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)
        self.u = nn.Parameter(torch.randn(n_heads, self.d_k) * 0.02)
        self.v = nn.Parameter(torch.randn(n_heads, self.d_k) * 0.02)
        self.scale = math.sqrt(self.d_k)
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor,
                memory: Optional[torch.Tensor] = None,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        B, N, _ = x.shape
        keys_src = memory if memory is not None else x
        M = keys_src.size(1)

        Q = self.W_q(x).view(B, N, self.n_heads, self.d_k)
        K = self.W_k(keys_src).view(B, M, self.n_heads, self.d_k)
        V = self.W_v(keys_src).view(B, M, self.n_heads, self.d_k)

        s_q = torch.einsum('b n h d, h d -> b n h', Q, self.u)
        s_k = torch.einsum('b m h d, h d -> b m h', K, self.v)
        attn = torch.einsum('b n h, b m h -> b n h m', s_q, s_k) / self.scale

        if mask is not None:
            attn = attn.masked_fill(mask.unsqueeze(1).unsqueeze(2) == 0, float('-inf'))

        # Upcast to float32 for softmax — bf16 softmax on all-inf rows produces NaN
        # which propagates through all 28 layers and causes multinomial to segfault.
        attn = F.softmax(attn.float(), dim=-1).to(x.dtype)
        attn = self.dropout(attn)

        out = torch.einsum('b n h m, b m h d -> b n h d', attn, V)
        return self.W_o(out.reshape(B, N, self.d_model))

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Complex-Valued FFN — ƒ_ż
# ═══════════════════════════════════════════════════════════════════════════════

class ComplexFFN(nn.Module):
    """Real/imag channels with cross-interference. ƒ_ż: quantum coherence."""

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.0):
        super().__init__()
        half = d_model // 2
        self.half = half
        self.w1_re = nn.Linear(half, d_ff, bias=False)
        self.w1_im = nn.Linear(half, d_ff, bias=False)
        self.w2_re = nn.Linear(d_ff, half, bias=False)
        self.w2_im = nn.Linear(d_ff, half, bias=False)
        # Cross-channel coupling
        self.cross_re_im = nn.Linear(half, d_ff, bias=False)
        self.cross_im_re = nn.Linear(half, d_ff, bias=False)
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Split input into real/imag halves
        x_re, x_im = x[..., :self.half], x[..., self.half:]

        h_re = F.gelu(self.w1_re(x_re) + self.cross_im_re(x_im))
        h_im = F.gelu(self.w1_im(x_im) + self.cross_re_im(x_re))

        h_re = self.dropout(h_re)
        h_im = self.dropout(h_im)

        out_re = self.w2_re(h_re) + self.w2_im(h_im)
        out_im = self.w2_im(h_im) - self.w2_re(h_re)

        return torch.cat([out_re, out_im], dim=-1)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Cyclic Layer — Ř_= (bidirectional feedback)
# ═══════════════════════════════════════════════════════════════════════════════

class CyclicLayer(nn.Module):
    """Each layer runs c times with same weights. Ř_=: bidirectional feedback."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int,
                 n_cycles: int = 3, dropout: float = 0.0,
                 use_complex_ffn: bool = True):
        super().__init__()
        self.n_cycles = n_cycles
        self.attention = TensorProductAttention(d_model, n_heads, dropout)
        if use_complex_ffn:
            self.ffn = ComplexFFN(d_model, d_ff, dropout)
        else:
            self.ffn = nn.Sequential(
                nn.Linear(d_model, d_ff), nn.GELU(), nn.Dropout(dropout),
                nn.Linear(d_ff, d_model), nn.Dropout(dropout))
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor,
                memory: Optional[torch.Tensor] = None,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        h = x
        for _ in range(self.n_cycles):
            h = self.ln1(h + self.attention(h, memory, mask))
            h = self.ln2(h + self.ffn(h))
        return h

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Meta-Network — ⊙_ÿ (self-modeling)
# ═══════════════════════════════════════════════════════════════════════════════

class MetaNetwork(nn.Module):
    """Secondary network monitors & modulates primary. ⊙_ÿ: self-modeling."""

    def __init__(self, d_model: int, d_meta: int = 256):
        super().__init__()
        self.pool = nn.Linear(d_model, 1)
        self.encoder = nn.Sequential(
            nn.Linear(d_model, d_meta), nn.GELU(),
            nn.Linear(d_meta, d_meta), nn.GELU(),
            nn.Linear(d_meta, d_meta))
        self.error_head = nn.Linear(d_meta, d_model)
        self.self_emb_head = nn.Linear(d_meta, d_meta)
        self.d_meta = d_meta

    def forward(self, hidden_states: torch.Tensor
                ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns (self_model_emb, error_pred)."""
        # Attention-weighted pooling over sequence dim
        weights = F.softmax(self.pool(hidden_states), dim=-2)  # (B,S,1)
        pooled = (hidden_states * weights).sum(dim=-2)          # (B,d_model)
        z = self.encoder(pooled)                                # (B,d_meta)
        return self.self_emb_head(z), self.error_head(z)        # (B,d_meta), (B,d_model)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Frobenius Dual Head — Φ_}
# ═══════════════════════════════════════════════════════════════════════════════

class FrobeniusDualHead(nn.Module):
    """Dual δ/μ outputs. W_μ = W_δ^T. Loss enforces μ∘δ=id. Φ_}."""

    def __init__(self, d_model: int, vocab_size: int):
        super().__init__()
        self.W_delta = nn.Linear(d_model, vocab_size, bias=False)
        self.b_delta = nn.Parameter(torch.zeros(vocab_size))
        self.b_mu = nn.Parameter(torch.zeros(d_model))
        self.d_model = d_model

    def delta(self, h: torch.Tensor) -> torch.Tensor:
        """Emit direction — predict next token."""
        return self.W_delta(h) + self.b_delta

    def mu(self, logits: torch.Tensor) -> torch.Tensor:
        """Verify direction — reconstruct hidden state from logits."""
        # W_delta.weight: (vocab_size, d_model). mu multiplies softmax(logits)
        # by W_delta.weight to get back to d_model: (B, V) @ (V, d) = (B, d)
        return F.softmax(logits, dim=-1) @ self.W_delta.weight + self.b_mu

    def frobenius_loss(self, h: torch.Tensor) -> torch.Tensor:
        """||μ(δ(h)) - h||²."""
        logits = self.delta(h)
        recon = self.mu(logits)
        return F.mse_loss(recon, h)

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Phase-Gated Controller — Ç_@, ɢ_ˌ
# ═══════════════════════════════════════════════════════════════════════════════

class PhaseGatedController(nn.Module):
    """Emission gate + 4-phase sequential modules. Ç_@ + ɢ_ˌ."""

    PHASE_THINK = 0
    PHASE_ACT = 1
    PHASE_OBSERVE = 2
    PHASE_UPDATE = 3

    def __init__(self, d_model: int, gate_threshold: float = 0.5):
        super().__init__()
        self.phase = self.PHASE_THINK
        self.gate = nn.Sequential(
            nn.Linear(d_model, d_model // 4), nn.GELU(),
            nn.Linear(d_model // 4, 1), nn.Sigmoid())
        self.adapters = nn.ModuleList(
            [nn.Linear(d_model, d_model) for _ in range(4)])
        self.threshold = gate_threshold

    def set_phase(self, phase: int):
        self.phase = phase % 4

    def forward(self, h: torch.Tensor
                ) -> Tuple[torch.Tensor, torch.Tensor, bool]:
        """Returns (gated_h, gate_value, transition).

        Gate is applied as a lerp: output = h + g*(phase_mod - h).
        g=0 → identity (gate closed); g=1 → fully phase-modulated (gate open).
        This puts g on the LM-loss gradient path so the gate gets a real
        training signal rather than only the small alpha_g * loss_g term.
        """
        phase_mod = self.adapters[self.phase](h)
        g = self.gate(h)  # (B, S, 1)
        g_mean = g.mean()
        transition = bool((g_mean > self.threshold).item())
        if transition:
            self.phase = (self.phase + 1) % 4
        gated = h + g * (phase_mod - h)  # lerp controlled by gate
        return gated, g, transition


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Imscriptive Memory Bank — Ð_ω
# ═══════════════════════════════════════════════════════════════════════════════

class ImscriptiveMemoryBank(nn.Module):
    """Append-only trajectory memory. Old windings compressed, not deleted."""

    def __init__(self, d_model: int, max_windings: int = 64,
                 compression_factor: int = 8):
        super().__init__()
        self.d_model = d_model
        self.max_windings = max_windings
        self.comp_factor = compression_factor
        self.comp_in = d_model * compression_factor
        self.compressor = nn.Linear(self.comp_in, d_model)
        self.bank: List[torch.Tensor] = []

    def append(self, hidden_states: torch.Tensor):
        """hidden_states: (seq_len, d_model). Appended to bank."""
        self.bank.append(hidden_states.detach())
        if len(self.bank) > self.max_windings:
            oldest = self.bank.pop(0)
            seq_len = oldest.size(0)
            pad_to = ((seq_len + self.comp_factor - 1)
                      // self.comp_factor) * self.comp_factor
            if seq_len < pad_to:
                oldest = F.pad(oldest, (0, 0, 0, pad_to - seq_len))
            oldest_flat = oldest.view(-1, self.comp_in)
            compressed = self.compressor(oldest_flat)
            self.bank.insert(0, compressed)

    def get_full_context(self) -> Optional[torch.Tensor]:
        """Full concatenated memory bank as (total_len, d_model)."""
        if not self.bank:
            return None
        return torch.cat(self.bank, dim=0)

    def size(self) -> int:
        return sum(t.size(0) for t in self.bank)

    def reset(self):
        self.bank = []

# ═══════════════════════════════════════════════════════════════════════════════
# 10. GrammaFormer — Full model
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GrammaFormerConfig:
    """Configuration for GrammaFormer model."""
    vocab_size: int = 151936
    d_model: int = 512
    n_heads: int = 8
    n_layers: int = 6
    d_ff: int = 2048
    n_cycles: int = 3
    d_meta: int = 256
    max_seq_len: int = 32768
    max_windings: int = 64
    comp_factor: int = 8
    gate_threshold: float = 0.5
    dropout: float = 0.0
    use_complex_ffn: bool = True

    @classmethod
    def small(cls) -> "GrammaFormerConfig":
        """Small config (~80M params) for testing / low-VRAM."""
        return cls(vocab_size=151936, d_model=512, n_heads=8,
                   n_layers=6, d_ff=2048)

    @classmethod
    def base(cls) -> "GrammaFormerConfig":
        """Base config (~350M params)."""
        return cls(d_model=1024, n_heads=16, n_layers=24, d_ff=4096)

    @classmethod
    def from_base_model(cls, base_cfg: Dict[str, Any]) -> "GrammaFormerConfig":
        """Derive GrammaFormer config from a base model's config dict."""
        return cls(
            vocab_size=base_cfg.get("vocab_size", 151936),
            d_model=base_cfg.get("hidden_size", base_cfg.get("d_model", 1024)),
            n_heads=base_cfg.get("num_attention_heads",
                                 base_cfg.get("n_heads", 16)),
            n_layers=base_cfg.get("num_hidden_layers",
                                  base_cfg.get("n_layers", 8)),
            d_ff=base_cfg.get("intermediate_size",
                              base_cfg.get("d_ff", 4096)),
        )

class GrammaFormer(nn.Module):
    """Grammar-Native Transformer: every component maps to one O_∞ primitive.

    Architecture:
      WindingPE → TwoSlotRegister → [CyclicLayer × L] →
      MetaNetwork → PhaseGate → FrobeniusDualHead → IMB

    Usage:
      cfg = GrammaFormerConfig.small()
      model = GrammaFormer(cfg)
      output = model(input_ids, winding=0, phase="THINK")
    """

    _GRAMMAFORMER_MARKER = "grammaformer_v1"

    def gradient_checkpointing_enable(self, **kwargs):
        self._gradient_checkpointing = True

    def gradient_checkpointing_disable(self):
        self._gradient_checkpointing = False

    def __init__(self, config: GrammaFormerConfig):
        super().__init__()
        self.config = config
        self._gradient_checkpointing = False
        d, heads, layers, d_ff = (config.d_model, config.n_heads,
                                   config.n_layers, config.d_ff)

        self.token_embed = nn.Embedding(config.vocab_size, d)
        self.winding_pe = WindingPositionalEncoding(d, config.max_seq_len)
        self.register = TwoSlotRegister(d)
        self.dropout_emb = nn.Dropout(config.dropout)

        self.layers = nn.ModuleList([
            CyclicLayer(d, heads, d_ff, config.n_cycles,
                        config.dropout, config.use_complex_ffn)
            for _ in range(layers)
        ])

        self.meta = MetaNetwork(d, config.d_meta)
        self.phase_gate = PhaseGatedController(d, config.gate_threshold)
        self.memory_bank = ImscriptiveMemoryBank(d, config.max_windings,
                                                  config.comp_factor)
        self.frobenius_head = FrobeniusDualHead(d, config.vocab_size)
        self.ln_final = nn.LayerNorm(d)

        # Meta embedding projection
        self.meta_proj = nn.Linear(config.d_meta, d) if config.d_meta != d else nn.Identity()

        # Winding counter for positional encoding
        self.winding: int = 0
        # Generation tracking
        self._phase_override: Optional[int] = None

    @property
    def phase(self) -> int:
        return self.phase_gate.phase

    def set_phase(self, p: int):
        self.phase_gate.set_phase(p)

    def set_winding(self, w: int):
        self.winding = w

    def _get_memory(self) -> Optional[torch.Tensor]:
        mem = self.memory_bank.get_full_context()
        if mem is not None and mem.dim() == 2:
            mem = mem.unsqueeze(0)  # (1, total_len, d_model)
        return mem

    def forward(self, input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                winding: Optional[int] = None,
                phase: Optional[int] = None,
                return_meta: bool = False,
                last_token_only: bool = False,
                n_cycles_override: Optional[int] = None,
                ) -> Dict[str, torch.Tensor]:
        """
        Args:
            input_ids: (B, S) token ids
            attention_mask: (B, S) or None
            winding: override winding counter
            phase: override phase (0=THINK, 1=ACT, 2=OBSERVE, 3=UPDATE)
            return_meta: if True, also return meta_emb and error_pred
            last_token_only: if True, only compute logits for the last position.
                Returns logits shape (B, 1, vocab_size). Use during generation
                to avoid allocating (B, S, vocab_size) which is ~1.5 GB at S=2048.
            n_cycles_override: if set, override CyclicLayer.n_cycles for this
                forward pass. Set to 1 during generation for 3x speedup.

        Returns dict with:
            logits: (B, S, vocab_size) or (B, 1, vocab_size) if last_token_only
            frobenius_logits: same as logits (for compatibility)
            meta_emb: (B, d_meta) if return_meta
            error_pred: (B, d_model) if return_meta
            gate_value: mean gate activation
            transition: did emission gate fire?
        """
        w = winding if winding is not None else self.winding
        if phase is not None:
            self.set_phase(phase)

        B, S = input_ids.shape
        h = self.token_embed(input_ids)
        h = self.winding_pe(h, w)
        h = self.dropout_emb(h)

        # Two-slot register injection
        reg = self.register.get_state()
        if reg is not None:
            reg = reg.unsqueeze(1).expand(-1, S, -1)  # (B, S, d_model)
            h = h + reg

        memory = self._get_memory()

        # Cyclic layers — temporarily override n_cycles if requested
        _saved_cycles: List[int] = []
        if n_cycles_override is not None:
            for layer in self.layers:
                _saved_cycles.append(layer.n_cycles)
                layer.n_cycles = n_cycles_override

        try:
            if self._gradient_checkpointing and self.training:
                from torch.utils.checkpoint import checkpoint as _ckpt
                for layer in self.layers:
                    h = _ckpt(layer, h, memory, attention_mask, use_reentrant=False)
            else:
                for layer in self.layers:
                    h = layer(h, memory, attention_mask)
        finally:
            if n_cycles_override is not None:
                for layer, nc in zip(self.layers, _saved_cycles):
                    layer.n_cycles = nc

        # Meta-network
        meta_emb, error_pred = self.meta(h)

        # Inject meta embedding
        meta_proj = self.meta_proj(meta_emb).unsqueeze(1)  # (B, 1, d_model)
        h = h + meta_proj

        h = self.ln_final(h)

        # Phase gate
        phase_mod, gate_val, transition = self.phase_gate(h)

        # Frobenius dual head — last_token_only avoids (B, S, vocab) allocation
        if last_token_only:
            logits = self.frobenius_head.delta(phase_mod[:, -1:, :])  # (B, 1, vocab)
        else:
            logits = self.frobenius_head.delta(phase_mod)  # (B, S, vocab)

        # Update register with pooled state
        pooled = h.mean(dim=1)  # (B, d_model)
        self.register.set_state(pooled)

        result = {
            "logits": logits,
            "frobenius_logits": logits,
            "hidden_for_frob": phase_mod,  # FIXED: use phase-modulated state so mu(delta(h)) is checked on emission path
            "gate_value": gate_val.mean(),  # tensor for gradient flow
            "gate_scalar": gate_val.mean().item(),  # for logging
            "transition": transition,
        }
        if return_meta:
            result["meta_emb"] = meta_emb
            result["error_pred"] = error_pred
        return result

    def frobenius_loss(self, input_ids: torch.Tensor,
                       attention_mask: Optional[torch.Tensor] = None
                       ) -> torch.Tensor:
        """Compute Frobenius round-trip loss for last hidden state.

        FIXED: Now applies phase modulation so the Frobenius check operates
        on the same hidden state path that produces logits during emission.
        """
        B, S = input_ids.shape
        h = self.token_embed(input_ids)
        h = self.winding_pe(h, self.winding)

        memory = self._get_memory()
        for layer in self.layers:
            h = layer(h, memory, attention_mask)

        # Meta-network
        meta_emb, _error_pred = self.meta(h)
        meta_proj = self.meta_proj(meta_emb).unsqueeze(1)
        h = h + meta_proj
        h = self.ln_final(h)

        # Phase modulation — same path as in forward()
        phase_mod, _gate_val, _transition = self.phase_gate(h)

        # Frobenius loss on last token of phase-modulated state
        h_last = phase_mod[:, -1, :]
        return self.frobenius_head.frobenius_loss(h_last)

    def update_memory(self, hidden_states: torch.Tensor):
        """Append hidden states to imscriptive memory bank."""
        if hidden_states.dim() == 3:
            hidden_states = hidden_states[0]  # use first batch
        self.memory_bank.append(hidden_states)

    def advance_winding(self):
        """Increment winding counter after UPDATE phase."""
        self.winding += 1

    def reset_state(self):
        """Reset registers, memory, winding for a new trajectory."""
        self.register.reset()
        self.memory_bank.reset()
        self.winding = 0
        self.set_phase(PhaseGatedController.PHASE_THINK)

    def save_pretrained(self, path: str):
        """Save model weights and config."""
        import json
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), p / "pytorch_model.bin")
        cfg = {k: v for k, v in self.config.__dict__.items()
               if not k.startswith('_')}
        cfg["_grammaformer_marker"] = self._GRAMMAFORMER_MARKER
        cfg["architectures"] = ["GrammaFormerForCausalLM"]
        with open(p / "config.json", "w") as f:
            json.dump(cfg, f, indent=2)

    @classmethod
    def from_pretrained(cls, path: str) -> "GrammaFormer":
        """Load GrammaFormer from a saved directory."""
        import json
        p = Path(path)
        with open(p / "config.json") as f:
            cfg_dict = json.load(f)
        cfg_dict.pop("_grammaformer_marker", None)
        cfg_dict.pop("architectures", None)
        config = GrammaFormerConfig(**{k: v for k, v in cfg_dict.items()
                                        if k in GrammaFormerConfig.__dataclass_fields__})
        model = cls(config)
        state = torch.load(p / "pytorch_model.bin", map_location="cpu",
                           weights_only=True)
        model.load_state_dict(state, strict=False)
        return model


# ═══════════════════════════════════════════════════════════════════════════════
# 11. Grafting: GrammaFormer from Qwen3 base
# ═══════════════════════════════════════════════════════════════════════════════

def graft_grammaformer_from_qwen(
    base_model_path: str,
    config: Optional[GrammaFormerConfig] = None,
    map_location: str = "cpu",
) -> GrammaFormer:
    """Load Qwen3 weights, graft GrammaFormer components.

    Strategy:
      - Embedding: copied from Qwen3
      - Attention Q/K/V/O: grafted to TensorProductAttention
      - FFN: split into ComplexFFN real/imag halves
      - New components (Meta, PhaseGate, IMB, Frobenius, Register): scratch init
      - LM head W: becomes W_delta in FrobeniusDualHead
    """
    from transformers import AutoModelForCausalLM

    _base_arg = Path(base_model_path) if Path(base_model_path).exists() else base_model_path
    qwen = AutoModelForCausalLM.from_pretrained(
        _base_arg, trust_remote_code=True,
        dtype=torch.bfloat16, device_map="cpu",
        low_cpu_mem_usage=True)

    if config is None:
        qwen_cfg = qwen.config.to_dict()
        config = GrammaFormerConfig.from_base_model(qwen_cfg)

    gf = GrammaFormer(config)
    qwen_state = qwen.state_dict()

    # 1. Token embedding: direct copy
    gf.token_embed.weight.data.copy_(qwen_state["model.embed_tokens.weight"])

    # 2. Per-layer grafting
    for i in range(config.n_layers):
        prefix = f"model.layers.{i}."
        layer = gf.layers[i]

        # TensorProductAttention: Q,K,V from qwen, O from qwen
        # GQA models (Qwen3) have k/v_proj shape (n_kv_heads*d_k, d_model) < d_model.
        # Expand by repeating KV heads to fill d_model (standard GQA→MHA promotion).
        def _expand_to(w: torch.Tensor, target_rows: int) -> torch.Tensor:
            if w.shape[0] == target_rows:
                return w
            reps = (target_rows + w.shape[0] - 1) // w.shape[0]
            return w.repeat(reps, 1)[:target_rows]

        d = config.d_model
        q_w = qwen_state.get(f"{prefix}self_attn.q_proj.weight")
        k_w = qwen_state.get(f"{prefix}self_attn.k_proj.weight")
        v_w = qwen_state.get(f"{prefix}self_attn.v_proj.weight")
        o_w = qwen_state.get(f"{prefix}self_attn.o_proj.weight")
        if q_w is not None:
            layer.attention.W_q.weight.data.copy_(_expand_to(q_w, d))
        if k_w is not None:
            layer.attention.W_k.weight.data.copy_(_expand_to(k_w, d))
        if v_w is not None:
            layer.attention.W_v.weight.data.copy_(_expand_to(v_w, d))
        if o_w is not None:
            layer.attention.W_o.weight.data.copy_(_expand_to(o_w, d))

        # ComplexFFN: split real/imag from Qwen FFN
        if config.use_complex_ffn:
            w1 = qwen_state.get(f"{prefix}mlp.gate_proj.weight",
                                qwen_state.get(f"model.layers.{i}.mlp.gate_proj.weight"))
            w2 = qwen_state.get(f"{prefix}mlp.down_proj.weight",
                                qwen_state.get(f"model.layers.{i}.mlp.down_proj.weight"))
            if w1 is not None:
                # gate_proj: (d_ff, d_model) — split along input (column) dim
                d_model_half = config.d_model // 2
                layer.ffn.w1_re.weight.data.copy_(w1[:, :d_model_half])
                layer.ffn.w1_im.weight.data.copy_(w1[:, d_model_half:])
            if w2 is not None:
                # down_proj: (d_model, d_ff) — split along output (row) dim
                d_model_half = config.d_model // 2
                layer.ffn.w2_re.weight.data.copy_(w2[:d_model_half, :])
                layer.ffn.w2_im.weight.data.copy_(w2[d_model_half:, :])
            # Layer norms
            ln1_key = f"{prefix}input_layernorm.weight"
            ln2_key = f"{prefix}post_attention_layernorm.weight"
            if ln1_key in qwen_state:
                layer.ln1.weight.data.copy_(qwen_state[ln1_key])
            if ln2_key in qwen_state:
                layer.ln2.weight.data.copy_(qwen_state[ln2_key])

    # 3. Frobenius head: W_delta from LM head
    lm_head_key = "lm_head.weight"
    if lm_head_key in qwen_state:
        gf.frobenius_head.W_delta.weight.data.copy_(qwen_state[lm_head_key])

    del qwen
    return gf

# ═══════════════════════════════════════════════════════════════════════════════
# 12. HuggingFace-compatible wrapper
# ═══════════════════════════════════════════════════════════════════════════════

class GrammaFormerForCausalLM(nn.Module):
    """HF-compatible wrapper. Exposes .generate() for transformers pipeline."""

    def __init__(self, config_or_model):
        super().__init__()
        if isinstance(config_or_model, GrammaFormer):
            self.grammaformer = config_or_model
            self.config = self.grammaformer.config
        else:
            # Parse from HF config dict
            self.grammaformer = GrammaFormer(GrammaFormerConfig(
                vocab_size=config_or_model.get("vocab_size", 151936),
                d_model=config_or_model.get("d_model",
                    config_or_model.get("hidden_size", 1024)),
                n_heads=config_or_model.get("n_heads",
                    config_or_model.get("num_attention_heads", 16)),
                n_layers=config_or_model.get("n_layers",
                    config_or_model.get("num_hidden_layers", 8)),
                d_ff=config_or_model.get("d_ff",
                    config_or_model.get("intermediate_size", 4096)),
            ))
            self.config = self.grammaformer.config

        self._tied_weights_keys = []

    @property
    def device(self):
        return next(self.parameters()).device

    @property
    def dtype(self):
        return next(self.parameters()).dtype

    def eval(self):
        self.grammaformer.eval()
        return self

    def train(self, mode: bool = True):
        self.grammaformer.train(mode)
        return self

    def to(self, *args, **kwargs):
        self.grammaformer = self.grammaformer.to(*args, **kwargs)
        return self

    def forward(self, input_ids, attention_mask=None, **kwargs):
        return self.grammaformer(input_ids, attention_mask, **kwargs)

    # Sliding window for generation: cap the context fed to the model each step.
    # Prevents O(S²) attention blowup without a KV cache. Full input_ids is
    # still tracked and returned; only the window is passed to the model.
    _INFERENCE_WINDOW = 512

    def generate(self, input_ids, attention_mask=None, max_new_tokens=256,
                 temperature=1.0, do_sample=False, pad_token_id=None,
                 eos_token_id=None, top_k=0, top_p=1.0, **kwargs):
        """Simple autoregressive generation with sliding-window attention."""
        self.grammaformer.eval()
        device = input_ids.device
        B = input_ids.size(0)
        _temp = float(temperature) if temperature else 1.0
        _top_k = int(top_k) if top_k else 0
        _top_p = float(top_p) if top_p else 1.0

        print(f"[GF] generate: device={device} ctx={input_ids.shape[1]} "
              f"max_new={max_new_tokens} window={self._INFERENCE_WINDOW} "
              f"temp={_temp} top_k={_top_k} top_p={_top_p}", flush=True)

        with torch.no_grad():
            for _step in range(max_new_tokens):
                if _step > 0 and _step % 20 == 0:
                    print(f"[GF] step {_step}/{max_new_tokens}", flush=True)

                # Sliding window: keep only the last _INFERENCE_WINDOW tokens
                ctx_ids = input_ids[:, -self._INFERENCE_WINDOW:]
                ctx_mask = (attention_mask[:, -self._INFERENCE_WINDOW:]
                            if attention_mask is not None else None)

                # last_token_only=True: logits is (B, 1, vocab) instead of (B, S, vocab)
                # n_cycles_override=1: 3x speedup vs training cycles
                out = self.grammaformer(
                    ctx_ids, ctx_mask,
                    last_token_only=True,
                    n_cycles_override=1,
                )
                logits = out["logits"][:, -1, :] / _temp  # (B, vocab)

                if do_sample:
                    scaled = logits.float() / _temp
                    # top-k
                    if _top_k > 0:
                        cutoff = scaled.topk(_top_k, dim=-1).values[..., -1, None]
                        scaled = scaled.masked_fill(scaled < cutoff, float('-inf'))
                    # top-p (nucleus)
                    if _top_p < 1.0:
                        sorted_logits, sorted_idx = scaled.sort(dim=-1, descending=True)
                        cum_probs = sorted_logits.softmax(dim=-1).cumsum(dim=-1)
                        remove = cum_probs - sorted_logits.softmax(dim=-1) > _top_p
                        sorted_logits[remove] = float('-inf')
                        scaled.scatter_(-1, sorted_idx, sorted_logits)
                    probs = F.softmax(scaled, dim=-1)
                    # multinomial segfaults on CUDA with NaN/negative probs — fall back to argmax
                    if torch.isfinite(probs).all() and (probs >= 0).all():
                        next_token = torch.multinomial(probs, 1)
                    else:
                        next_token = logits.argmax(dim=-1, keepdim=True)
                else:
                    next_token = logits.argmax(dim=-1, keepdim=True)

                input_ids = torch.cat([input_ids, next_token], dim=1)
                if attention_mask is not None:
                    attention_mask = torch.cat(
                        [attention_mask,
                         torch.ones(B, 1, device=device, dtype=attention_mask.dtype)],
                        dim=1)

                if eos_token_id is not None and (next_token == eos_token_id).any():
                    break

        return input_ids

    def save_pretrained(self, path: str):
        self.grammaformer.save_pretrained(path)

    @classmethod
    def from_pretrained(cls, path: str, **kwargs):
        gf = GrammaFormer.from_pretrained(path)
        return cls(gf)


# ═══════════════════════════════════════════════════════════════════════════════
# 13. Module entry point
# ═══════════════════════════════════════════════════════════════════════════════

_GRAMMAFORMER_DEFAULT_PATH = str(
    Path(__file__).resolve().parent.parent
    / "models" / "grammaformer" / "grammaformer_small.pt"
)


def is_grammaformer_path(model_path: str) -> bool:
    """Detect if model_path points to a GrammaFormer model."""
    cfg = Path(model_path) / "config.json"
    if not cfg.exists():
        return False
    try:
        import json
        with open(cfg) as f:
            d = json.load(f)
        return d.get("_grammaformer_marker") == "grammaformer_v1"
    except Exception:
        return False


def load_grammaformer(model_path: Optional[str] = None
                      ) -> GrammaFormerForCausalLM:
    """Load GrammaFormer from path or create a fresh small model."""
    path = model_path or _GRAMMAFORMER_DEFAULT_PATH
    p = Path(path)
    if p.is_dir() and is_grammaformer_path(path):
        return GrammaFormerForCausalLM.from_pretrained(path)
    elif p.suffix == ".pt" and p.exists():
        cfg = GrammaFormerConfig.small()
        model = GrammaFormer(cfg)
        model.load_state_dict(torch.load(path, map_location="cpu",
                                         weights_only=True))
        return GrammaFormerForCausalLM(model)
    # Fresh small model (for testing)
    cfg = GrammaFormerConfig.small()
    model = GrammaFormer(cfg)
    model.eval()
    return GrammaFormerForCausalLM(model)
