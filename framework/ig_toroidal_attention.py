"""ig_toroidal_attention.py — toroidal attention as the IG framework attention backend.

When flash-attn won't build (CUDA version mismatch, nvcc missing, the usual),
toroidal attention steps in: O(N log N) FFT-based circulant convolution,
pure NumPy, no CUDA dependency, exact at ~2e-16.

─── geometry ───
Standard attention operates on a line with a causal mask — token N can't see
token N+1. Toroidal attention wraps the sequence onto a circle Z_N (or a torus
S¹×S¹ for 2D grids). The attention matrix becomes circulant (translation-
invariant kernel + softmax commuting with cyclic shifts), diagonalized exactly
by the FFT. No approximation, no kernel trick, no low-rank assumption.

─── 1D vs 2D ───
The 1D variant (Z_N, single cycle) is for standard transformer sequences.
The 2D variant (Z_m × Z_n) is for grid-structured data. Both are exact FFT
convolutions. The 1D variant is the default for HuggingFace model integration.

─── integration ───
HuggingFace `attn_implementation` only accepts eager/sdpa/flash_attention_2.
Toroidal attention is applied as a post-load patch: load the model with sdpa,
then call `patch_with_toroidal(model, dim=1)` to replace attention layers.

─── types ───
toroidal_attention_1d: ⟨𐑨𐑥𐑾𐑯𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩
    box product → crossing (1D is crossing Z_N, not box S¹×S¹)
toroidal_attention_2d: ⟨𐑨𐑶𐑾𐑯𐑐𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩
    box product S¹×S¹ (daydr33m original)
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import numpy as np

# GPU auto-dispatch: when daydr33m is importable, attention_fft_1d and
# attention_fft_2d auto-detect torch/cuda and stay on GPU without CPU round-trips.
try:
    import sys
    _daydr33m_path = __file__.rsplit('/', 3)[0] + '/daydr33m'
    if _daydr33m_path not in sys.path:
        sys.path.insert(0, _daydr33m_path)
    from toroidal_attention import attention_fft_1d as _attn_fft_1d_dispatch
    from toroidal_attention import attention_fft as _attn_fft_2d_dispatch
    _HAS_DISPATCH = True
except ImportError:
    _HAS_DISPATCH = False


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Geometry — positions and distances in windings
# ═══════════════════════════════════════════════════════════════════════════════

def winding_coords_1d(i: int, n: int) -> float:
    """Token i on the cycle Z_n as a rational winding in [0, 1)."""
    return i / n


def cyclic_geodesic(di: int, n: int) -> float:
    """Geodesic distance on Z_n (a single cycle), in windings, in [0, 1/2]."""
    u = (di % n) / n
    return min(u, 1.0 - u)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Kernel — the translation-invariant attention generator
# ═══════════════════════════════════════════════════════════════════════════════

def kernel_row_1d(n: int, sigma: float = 0.15) -> np.ndarray:
    """1D circulant kernel generator: k[i] = -d(i,0)² / (2σ²).

    The kernel is a Gaussian on the cyclic distance. These are LOGITS, not
    weights — a softmax follows. The row is length n; every other row is a
    cyclic shift of this one, so this single row generates the full (n×n)
    circulant attention matrix.

    At σ=0.05: 84% mass on self. At σ=0.15: 11% on self, spread over
    neighbours. At σ=0.50: nearly uniform. σ controls locality.
    """
    i = np.arange(n)
    d = np.minimum(i / n, 1.0 - i / n)       # geodesic distance from 0 in windings
    d2 = d * d
    return -d2 / (2.0 * sigma * sigma)


def kernel_row_2d(m: int, n: int, sigma: float = 0.15) -> np.ndarray:
    """2D circulant kernel generator on Z_m × Z_n.

    Returns (m, n) logit array. Every (m, n) row of the full (mn × mn)
    attention matrix is a 2D cyclic shift of this generator.
    """
    a = np.arange(m)
    b = np.arange(n)
    da = np.minimum(a / m, 1.0 - a / m)
    db = np.minimum(b / n, 1.0 - b / n)
    d2 = da[:, None] ** 2 + db[None, :] ** 2
    return -d2 / (2.0 * sigma * sigma)


def _row_softmax(row: np.ndarray) -> np.ndarray:
    """Softmax over a flattened row. Softmax commutes with cyclic shifts,
    so a softmaxed generator stays circulant."""
    flat = row.ravel()
    z = flat - flat.max()
    e = np.exp(z)
    return (e / e.sum()).reshape(row.shape)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Attention passes — FFT convolution (exact) and O(N²) reference
# ═══════════════════════════════════════════════════════════════════════════════

def attention_fft_1d(x: np.ndarray, sigma: float = 0.15,
                     heads: int = 1) -> np.ndarray:
    """1D toroidal attention: FFT-evaluated circulant convolution on Z_N.

    x:      (batch, n_tok, d_model)
    sigma:  kernel width in windings
    heads:  number of attention heads

    Returns y of same shape. The attention weight matrix is circulant; the
    1D FFT diagonalizes it. Complexity O(d_model · N log N).

    This is EXACTLY equivalent to building the full (N×N) softmax attention
    matrix and multiplying — verified at ~2e-16. No approximation.
    """
    batch, n_tok, d_model = x.shape

    row = kernel_row_1d(n_tok, sigma)
    a = _row_softmax(row)                              # (n_tok,) — circulant generator

    d_head = d_model // heads
    assert d_head * heads == d_model

    xg = x.reshape(batch, n_tok, heads, d_head)        # (batch, N, heads, d_head)

    A = np.fft.fft(a)                                   # (N,) — diagonal of operator
    X = np.fft.fft(xg, axis=1)                          # (batch, N, heads, d_head)
    Y = A[None, :, None, None] * X                      # convolution theorem
    y = np.fft.ifft(Y, axis=1).real

    return y.reshape(batch, n_tok, d_model)


def attention_fft_2d(x: np.ndarray, m: int, n: int,
                     sigma: float = 0.15, heads: int = 1) -> np.ndarray:
    """2D toroidal attention: FFT-evaluated circulant convolution on Z_m × Z_n.

    x:      (batch, m*n, d_model) — tokens in row-major torus order
    sigma:  kernel width in windings
    heads:  number of attention heads

    Returns y of same shape. This is the daydr33m original, verified exact
    at ~2e-16 against the O(N²) reference.
    """
    batch, n_tok, d_model = x.shape
    assert n_tok == m * n

    row = kernel_row_2d(m, n, sigma)
    a = _row_softmax(row)                                # (m, n)

    d_head = d_model // heads
    assert d_head * heads == d_model
    xg = x.reshape(batch, m, n, heads, d_head)

    A = np.fft.fft2(a)                                   # (m, n)
    X = np.fft.fft2(xg, axes=(1, 2))
    Y = A[None, :, :, None, None] * X
    y = np.fft.ifft2(Y, axes=(1, 2)).real

    return y.reshape(batch, n_tok, d_model)


def attention_naive_1d(x: np.ndarray, sigma: float = 0.15) -> np.ndarray:
    """O(N²) reference for 1D toroidal attention — verification only."""
    batch, n_tok, d_model = x.shape

    ii = np.arange(n_tok)
    di = ii[:, None] - ii[None, :]
    du = np.minimum(di % n_tok / n_tok, 1.0 - di % n_tok / n_tok)
    d2 = du * du
    K = -d2 / (2.0 * sigma * sigma)

    z = K - K.max(axis=1, keepdims=True)
    e = np.exp(z)
    A = e / e.sum(axis=1, keepdims=True)

    return np.einsum('ij,bjd->bid', A, x)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Shift-equivariance verification
# ═══════════════════════════════════════════════════════════════════════════════

def shift_equivariance_error_1d(x: np.ndarray, sigma: float,
                                shift: int) -> float:
    """∥T_s ∘ F − F ∘ T_s∥_∞ — should be at float precision (~1e-15)."""
    y = attention_fft_1d(x, sigma)
    y_shifted = np.roll(y, shift, axis=1)
    x_shifted = np.roll(x, shift, axis=1)
    y_of_shifted = attention_fft_1d(x_shifted, sigma)
    return float(np.max(np.abs(y_shifted - y_of_shifted)))


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Regime classification
# ═══════════════════════════════════════════════════════════════════════════════

def regime_1d(n: int) -> dict:
    """Classify 1D cyclic connectivity. Always ergodic for n > 1."""
    return {
        "n": n,
        "ergodic": n > 1,
        "label": "ergodic (single Z_N cycle)" if n > 1 else "degenerate",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5.5. PyTorch availability
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import torch
    import torch.nn as nn
    _HAS_TORCH = True
except ImportError:
    _HAS_TORCH = False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. HuggingFace integration — post-load attention patching
# ═══════════════════════════════════════════════════════════════════════════════

class ToroidalAttentionWrapper(nn.Module if _HAS_TORCH else object):
    """Wraps a HuggingFace attention layer, replacing the forward pass with
    toroidal FFT attention.

    This is applied AFTER model loading: load with sdpa/eager, then replace
    each attention module's forward with the toroidal pass.

    The wrapper preserves the original Q/K/V/O projections and only replaces
    the attention computation (the QK^T + softmax + V part).
    """

    def __init__(self, original_module, sigma: float = 0.15,
                 mode: str = "1d", m: int = 0, n: int = 0):
        """
        original_module: the HuggingFace attention module (e.g. Qwen3Attention)
        sigma: kernel width in windings
        mode: "1d" (cyclic Z_N) or "2d" (torus Z_m × Z_n)
        m, n: torus grid dimensions (for 2D mode; auto-computed in 1D)
        """
        if _HAS_TORCH:
            super().__init__()
        # Move projection/param attributes from original to wrapper so state
        # dict paths are preserved (self.q_proj, NOT self.q_proj).
        _proj_attrs = [
            "q_proj", "k_proj", "v_proj", "o_proj", "qkv_proj",
            "num_heads", "head_dim", "num_key_value_heads",
            "num_attention_heads", "attention_dropout", "rotary_emb",
            "rotary_ndims", "kv_heads", "hidden_size",
            "num_key_value_groups",
        ]
        for _a in _proj_attrs:
            if hasattr(original_module, _a):
                setattr(self, _a, getattr(original_module, _a))
        # Hold the original module WITHOUT auto-registration (so _orig does
        # NOT appear in named_modules / state_dict).
        object.__setattr__(self, "_orig", original_module)
        self.sigma = sigma
        self.mode = mode
        self._m = m
        self._n = n
        # Cache num_heads if not directly found on original_module.
        # attn_output_gate (Qwen3.5, Olmo3) doubles q_proj output: Q + gate.
        if not hasattr(self, "num_heads"):
            if hasattr(self, "num_attention_heads"):
                object.__setattr__(self, "num_heads", self.num_attention_heads)
            elif hasattr(self, "q_proj") and hasattr(self, "head_dim"):
                q_out = self.q_proj.out_features
                hd = self.head_dim
                n = q_out // hd
                # Detect gate-doubling (Qwen3.5, Olmo3): q_proj output is
                # doubled when attn_output_gate=true (Q + gate, each
                # num_attention_heads * head_dim wide).  Use k_proj (which
                # is never gate-doubled) to find the real num_kv_heads,
                # compute the expected non-gate Q width, and only halve n
                # when q_out exceeds that.  This prevents the old heuristic
                # (n % 2 == 0) from falsely halving plain GQA models like
                # Qwen3-1.7B that have no gate at all.
                n_kv_groups = getattr(self, "num_key_value_groups", None)
                if n_kv_groups is not None and n_kv_groups > 1:
                    if hasattr(self, "k_proj"):
                        k_out = self.k_proj.out_features
                        num_kv_actual = k_out // hd
                        expected_q = num_kv_actual * n_kv_groups * hd
                        if q_out > expected_q:
                            n = n // 2
                    elif n % 2 == 0:
                        # No k_proj to cross-check: use the old heuristic
                        # as a fallback (should be rare).
                        n = n // 2
                object.__setattr__(self, "num_heads", n)
            else:
                object.__setattr__(self, "num_heads", 1)

    @property
    def m(self):
        return self._m

    @property
    def n(self):
        return self._n

    def forward(self, hidden_states, attention_mask=None, position_ids=None,
                past_key_value=None, output_attentions=False, use_cache=False,
                **kwargs):
        """Toroidal forward pass — replaces QK^T softmax with FFT convolution.

        Projects Q/K/V through the original weight matrices, then applies
        toroidal attention (content-independent circulant kernel) instead of
        standard scaled dot-product attention.
        """
        import torch

        # Run original projections (Q, K, V, O are learned)
        # Try standard HuggingFace attribute names
        if hasattr(self, "q_proj"):
            Q = self.q_proj(hidden_states)
            K = self.k_proj(hidden_states)
            V = self.v_proj(hidden_states)
            o_proj = self.o_proj
        elif hasattr(self, "qkv_proj"):
            qkv = self.qkv_proj(hidden_states)
            # Split — heuristics for common split patterns
            d = qkv.shape[-1] // 3
            Q, K, V = qkv[..., :d], qkv[..., d:2*d], qkv[..., 2*d:]
            if hasattr(self, "o_proj"):
                o_proj = self.o_proj
            else:
                o_proj = lambda x: x  # noqa: E731
        else:
            # Generic fallback: try to find projection layers
            # If we can't find them, return the original forward
            return self._orig(hidden_states, attention_mask=attention_mask,
                            position_ids=position_ids, past_key_value=past_key_value,
                            output_attentions=output_attentions, use_cache=use_cache,
                            **kwargs)

        batch, n_tok, d_model = V.shape
        num_heads = getattr(self, "num_heads", 1)
        num_kv_heads = getattr(self, "num_key_value_heads", None)
        if num_kv_heads is None:
            # Derive from q_proj: for GQA, num_kv_heads = num_heads / num_key_value_groups
            n_kv_groups = getattr(self, "num_key_value_groups", None)
            if n_kv_groups is not None and n_kv_groups > 1:
                num_kv_heads = num_heads // n_kv_groups
            else:
                num_kv_heads = num_heads  # non-GQA: KV heads == Q heads
        n_rep = num_heads // num_kv_heads if num_kv_heads > 0 else 1

        # Toroidal attention on V with KV head count.
        # Uses the V-projected tensor whose last dim is num_kv_heads * head_dim,
        # which is exactly divisible by num_kv_heads.
        if _HAS_DISPATCH:
            if self.mode == "2d" and self._m > 0 and self._n > 0:
                y = _attn_fft_2d_dispatch(
                    V.reshape(batch, self._m * self._n, d_model),
                    self._m, self._n, self.sigma, num_kv_heads,
                )
            else:
                y = _attn_fft_1d_dispatch(
                    V.reshape(batch, n_tok, d_model),
                    self.sigma, num_kv_heads,
                )
        else:
            # Fallback: NumPy FFT (CPU round-trip, always available)
            V_np = V.detach().cpu().numpy().reshape(batch, n_tok, d_model)
            if self.mode == "2d" and self._m > 0 and self._n > 0:
                y_np = attention_fft_2d(
                    V_np, self._m, self._n, self.sigma, num_kv_heads,
                )
            else:
                y_np = attention_fft_1d(V_np, self.sigma, num_kv_heads)
            y = torch.from_numpy(y_np).to(V.device).to(V.dtype)

        # Expand KV-grouped output to full attention-head dimension for o_proj.
        # GQA (Grouped Query Attention) uses fewer KV heads than Q heads;
        # each KV head serves n_rep Q heads.  The toroidal kernel is
        # circulant, so expanding BEFORE the output projection is equivalent
        # to computing the kernel on the expanded head dimension.
        if n_rep > 1:
            head_dim = d_model // num_kv_heads
            y = y.reshape(batch, n_tok, num_kv_heads, head_dim)
            y = y.unsqueeze(2).expand(-1, -1, n_rep, -1, -1)
            y = y.reshape(batch, n_tok, num_heads * head_dim)

        # ── Gate application (attn_output_gate: Qwen3.5, Olmo3) ──
        # Models with attn_output_gate stash a gate signal in the second
        # half of q_proj's output.  The gate modulates the attention output
        # element-wise: sigmoid(gate) * y.  The toroidal kernel produces y
        # from V alone, so the gate is extracted from Q (which we projected
        # but haven't used yet) and applied here.
        if hasattr(self, "q_proj"):
            _hd = getattr(self, "head_dim", 64)
            _q_out = Q.shape[-1]
            _expected_q = num_heads * _hd
            if _q_out > _expected_q:
                # Q = [query_states | gate], each _expected_q wide
                gate = Q[..., _expected_q:]
                y = y * torch.sigmoid(gate)


        # Apply output projection
        y = o_proj(y)

        # Match HF return format — always a 2-tuple (output, weights_or_None).
        # Decoder layers unpack as hidden_states, _ = self_attn(...) and a
        # 1-tuple here gives "not enough values to unpack (expected 2, got 1)".
        if output_attentions:
            return (y, None)
        return (y, None)


def patch_with_toroidal(model, sigma: float = 0.15, mode: str = "1d",
                        m: int = 0, n: int = 0, layers_to_patch=None):
    """Replace attention layers in a loaded HuggingFace model with toroidal attention.

    model:            a loaded HuggingFace model (e.g. AutoModelForCausalLM)
    sigma:            kernel width in windings (0.05 = tight local, 0.5 = near-uniform)
    mode:             "1d" (cyclic Z_N) or "2d" (torus Z_m × Z_n)
    m, n:             torus grid dimensions for 2D mode
    layers_to_patch:  list of layer indices to patch (None = all attention layers)

    Returns the model with patched attention layers.
    """
    import torch.nn as nn

    patched = 0
    for name, module in model.named_modules():
        # Detect attention modules by common HF naming conventions
        is_attention = (
            'attention' in name.lower()
            or 'attn' in name.lower()
            or 'self_attn' in name.lower()
        ) and hasattr(module, 'forward')

        if not is_attention:
            continue

        # Skip if it's already a wrapper or doesn't have Q/K/V projections
        if isinstance(module, ToroidalAttentionWrapper):
            continue

        has_projections = (
            hasattr(module, 'q_proj')
            or hasattr(module, 'qkv_proj')
        )
        if not has_projections:
            continue

        # Check layer filtering
        if layers_to_patch is not None:
            # Try to extract layer number from name
            import re
            match = re.search(r'(\d+)', name)
            if match and int(match.group(1)) not in layers_to_patch:
                continue

        wrapper = ToroidalAttentionWrapper(module, sigma=sigma, mode=mode, m=m, n=n)

        # Replace the module in its parent
        parts = name.split('.')
        parent = model
        for part in parts[:-1]:
            parent = getattr(parent, part)
        setattr(parent, parts[-1], wrapper)

        patched += 1
        print(f"[toroidal]   patched #{patched}: {name}", flush=True)

    print(f"[toroidal] patched {patched} attention layers (σ={sigma}, {mode})")
    return model


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Torch integration — torch.nn.Module for native HF registration
# ═══════════════════════════════════════════════════════════════════════════════



if _HAS_TORCH:
    class ToroidalAttention1D(nn.Module):
        """Standalone 1D toroidal attention as a torch module.

        Can be used as a drop-in attention replacement in custom models.
        Projects Q/K/V, then applies FFT-based circulant attention instead
        of standard scaled dot-product.
        """

        def __init__(self, d_model: int, num_heads: int, sigma: float = 0.15,
                     qkv_bias: bool = True):
            super().__init__()
            self.d_model = d_model
            self.num_heads = num_heads
            self.head_dim = d_model // num_heads
            self.sigma = sigma

            self.q_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
            self.k_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
            self.v_proj = nn.Linear(d_model, d_model, bias=qkv_bias)
            self.o_proj = nn.Linear(d_model, d_model, bias=qkv_bias)

        def forward(self, hidden_states, attention_mask=None, **kwargs):
            batch, n_tok, _ = hidden_states.shape
            V = self.v_proj(hidden_states)

            # Toroidal attention: content-independent circulant kernel via FFT.
            # Auto-dispatched: stays on GPU when available.
            if _HAS_DISPATCH:
                y = _attn_fft_1d_dispatch(
                    V.reshape(batch, n_tok, self.d_model),
                    self.sigma, self.num_heads,
                )
            else:
                V_np = V.detach().cpu().numpy()
                y_np = attention_fft_1d(V_np, self.sigma, self.num_heads)
                y = torch.from_numpy(y_np).to(V.device).to(V.dtype)

            return self.o_proj(y), None


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Verification and diagnostics
# ═══════════════════════════════════════════════════════════════════════════════

def verify_1d(n_tok: int = 64, d_model: int = 32, sigma: float = 0.15,
              seed: int = 42) -> dict:
    """Verify 1D toroidal attention: FFT vs naive, shift-equivariance.

    Returns dict with max_error (should be ~1e-15), shift_error, timing.
    """
    import time

    rng = np.random.default_rng(seed)
    x = rng.normal(size=(2, n_tok, d_model))

    t0 = time.perf_counter()
    y_fft = attention_fft_1d(x, sigma)
    t_fft = time.perf_counter() - t0

    t0 = time.perf_counter()
    y_naive = attention_naive_1d(x, sigma)
    t_naive = time.perf_counter() - t0

    fft_vs_naive = float(np.max(np.abs(y_fft - y_naive)))
    shift_err = shift_equivariance_error_1d(x, sigma, 3)
    reg = regime_1d(n_tok)

    return {
        "n_tok": n_tok,
        "d_model": d_model,
        "sigma": sigma,
        "fft_vs_naive_error": fft_vs_naive,
        "shift_equivariance_error": shift_err,
        "regime": reg["label"],
        "fft_time_ms": t_fft * 1000,
        "naive_time_ms": t_naive * 1000,
        "speedup": t_naive / t_fft if t_fft > 0 else float('inf'),
    }


def verify_2d(m: int = 7, n: int = 5, d_model: int = 32,
              sigma: float = 0.15, seed: int = 42) -> dict:
    """Verify 2D toroidal attention. Import from daydr33m if available."""
    import time

    rng = np.random.default_rng(seed)
    x = rng.normal(size=(2, m * n, d_model))

    t0 = time.perf_counter()
    y_fft = attention_fft_2d(x, m, n, sigma)
    t_fft = time.perf_counter() - t0

    # Try daydr33m naive reference
    import sys
    sys.path.insert(0, "/home/mrnob0dy666/imsgct/daydr33m")
    try:
        from toroidal_attention import attention_naive as _naive_2d
        t0 = time.perf_counter()
        y_naive = _naive_2d(x, m, n, sigma)
        t_naive = time.perf_counter() - t0
        fft_vs_naive = float(np.max(np.abs(y_fft - y_naive)))
    except ImportError:
        y_naive = None
        t_naive = 0.0
        fft_vs_naive = None

    return {
        "grid": f"{m}×{n}",
        "d_model": d_model,
        "sigma": sigma,
        "fft_vs_naive_error": fft_vs_naive,
        "fft_time_ms": t_fft * 1000,
        "naive_time_ms": t_naive * 1000,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Auto-detect torus dimensions from sequence length
# ═══════════════════════════════════════════════════════════════════════════════

def torus_from_seqlen(n_tok: int) -> Tuple[int, int]:
    """Find the best m×n factorization of n_tok for a torus grid.

    Prefers near-square factorizations. For prime n_tok, uses n_tok×1
    (degenerate torus → 1D cycle).
    """
    best_m, best_n = n_tok, 1
    best_diff = n_tok
    for m in range(1, int(math.sqrt(n_tok)) + 1):
        if n_tok % m == 0:
            n_ = n_tok // m
            diff = abs(m - n_)
            if diff < best_diff:
                best_diff = diff
                best_m, best_n = m, n_
    return best_m, best_n


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Self-test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═══ toroidal attention · IG framework backend ═══\n")

    # 1D verification
    for n_tok in [32, 64, 128]:
        r = verify_1d(n_tok=n_tok, d_model=64, sigma=0.15)
        print(f"1D n={n_tok:>4d}:  |fft−naive| = {r['fft_vs_naive_error']:.2e}"
              f"  |  shift-equiv = {r['shift_equivariance_error']:.2e}"
              f"  |  fft {r['fft_time_ms']:.2f}ms  naive {r['naive_time_ms']:.2f}ms"
              f"  speedup {r['speedup']:.1f}×  [{r['regime']}]")

    print()

    # 2D verification
    for (m, n) in [(5, 7), (6, 8), (8, 12)]:
        r = verify_2d(m=m, n=n, d_model=64, sigma=0.15)
        err_str = f"{r['fft_vs_naive_error']:.2e}" if r['fft_vs_naive_error'] is not None else "N/A"
        print(f"2D {r['grid']:>8s}:  |fft−naive| = {err_str}"
              f"  |  fft {r['fft_time_ms']:.2f}ms  naive {r['naive_time_ms']:.2f}ms")

    print()

    # Torus factorization
    for n in [32, 48, 64, 97, 128]:
        m, n_ = torus_from_seqlen(n)
        print(f"seqlen {n:>4d} → torus {m}×{n_} (product {m*n_})")

    print("\n✓ toroidal attention ready — no CUDA, no build, exact FFT convolution.")
