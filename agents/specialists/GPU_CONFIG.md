
# GPU Configuration Guide — Dual-GPU Inference (3060 + 4070)

## Quick Start

```bash
# Both cards: model splits across them (for models that don't fit one)
export IG_DEVICES=0,1

# Pin to 4070 only (for models that fit on 12 GB — keep 3060 free)
export IG_DEVICES=<4070-ordinal>

# Reserve 3060 for a second process (Rust kernel, embedding, etc.)
export IG_PREFER_DEVICE=<4070-ordinal>
export IG_DEVICES=0,1
```

## Hardware Profile

| Card | VRAM | Compute Capability | Role |
|------|------|--------------------|------|
| RTX 3060 | 12 GB | SM 8.6 (Ampere) | Secondary / KV cache / light models |
| RTX 4070 | 12 GB | SM 8.9 (Ada Lovelace) | Primary / main model layers |
| RAM | 64 GB DDR4 | — | CPU fallback / large context offload |

## Configuration Variables

### `IG_DEVICES` (canonical — used by Rust kernel, Python loader, and all specialists)

```
IG_DEVICES=0        # Pin to card 0 only
IG_DEVICES=1        # Pin to card 1 only
IG_DEVICES=0,1      # Split model across both cards
IG_DEVICES=cpu      # Force CPU (debug / OOM recovery)
(unset)             # Auto-detect: every card present
```

The Rust kernel (`ask --provider local`) reads the same variable. One spelling,
one behavior across the constellation.

### `IG_PREFER_DEVICE` (asymmetric routing)

```
IG_PREFER_DEVICE=1  # Load primary model on card 1 (4070) when it fits
(unset)             # Equal treatment — split when multiple cards available
```

When set AND the model fits the preferred card alone (with working reserve),
`device_plan()` returns a single-device map for that card. The other card
stays free for a second process.

Use this when:
- Qwen3-4B fits on the 4070 with plenty of room for KV cache
- You want to run the Rust kernel (`ask --provider local`) on the 3060
  simultaneously for a different task
- 3060 is driving a display and you want the model on the dedicated card

### `IG_LOCAL_MODEL_DIR`

```bash
export IG_LOCAL_MODEL_DIR=/home/mrnob0dy666/models/Qwen3-4B
```

Default: `/home/mrnob0dy666/models/Qwen3-1.7B`

## Model Sizing: What Fits Where

| Model | bf16 (GB) | 4-bit (GB) | Fits 12 GB? |
|-------|-----------|------------|-------------|
| Qwen3-1.7B | 3.4 | 0.9 | ✓ single card, lots of room |
| Qwen3-4B | 8.0 | 2.0 | ✓ single card |
| Qwen3-8B | 16.0 | 4.0 | ✗ single → split across both |
| Qwen3-14B | 28.0 | 7.0 | ✗ split OR 4-bit on one card |
| Qwen3-32B | 64.0 | 16.0 | ✗ 4-bit split across both |

## Flash Attention

Both GPUs support flash_attention_2 (3060: SM 8.6 Ampere, 4070: SM 8.9 Ada).

### Installation

The system has two CUDA toolkits:
- `/usr/bin/nvcc` → CUDA 11.5 (too old: flash-attn needs ≥ 11.7)
- `/usr/local/cuda-12.4/bin/nvcc` → CUDA 12.4 (compatible with PyTorch 2.9.1+cu128)

Install with the CUDA 12.4 toolkit:

```bash
CUDA_HOME=/usr/local/cuda-12.4 \
  PATH="/usr/local/cuda-12.4/bin:$PATH" \
  uv pip install flash-attn --no-build-isolation
```

This is a large compilation (~5–10 minutes on a 16-core machine). The wheel
is not pre-built for CUDA 12.8 on PyPI as of flash-attn 2.8.3, so building
from source is the current path.

If the build OOMs (gcc can spike to 16+ GB on some translation units), cap
parallelism:

```bash
MAX_JOBS=4 CUDA_HOME=/usr/local/cuda-12.4 \
  PATH="/usr/local/cuda-12.4/bin:$PATH" \
  uv pip install flash-attn --no-build-isolation
```

### Verification

```python
from framework.ig_devices import flash_attention_available, attn_implementation

print(flash_attention_available())  # True
print(attn_implementation())        # 'flash_attention_2'
```

The loader auto-detects: `attn_implementation()` returns `"flash_attention_2"`
when installed, otherwise falls back to `"sdpa"` (PyTorch native, 3–5× faster
than eager). No flag needed.

## Toroidal Attention — FFT Circulant (Zero-Dependency Fallback)

When flash-attn won't build (CUDA version mismatch, nvcc absent, the usual),
toroidal attention steps in: O(N log N) FFT-based circulant convolution, pure
NumPy, no CUDA dependency, exact at ~2e-16. Integrated directly into the local
model loader — all agents and specialists get it automatically.

### Quick Start

```bash
# Enable toroidal attention for all local model inference
export IG_TOROIDAL_ATTENTION=1

# Optional tuning
export IG_TOROIDAL_SIGMA=0.15    # kernel width (0.05=tight, 0.15=default, 0.5=uniform)
export IG_TOROIDAL_MODE=1d       # 1d (Z_N cycle) or 2d (Z_m×Z_n torus)

# Then run any specialist — toroidal replaces flash_attn/sdpa:
uv run agents/specialists/math_operator.py "Derive the SIC-POVM functor"
```

### Shell Aliases

```bash
toroidal-on       # Enable toroidal (IG_TOROIDAL_ATTENTION=1)
toroidal-off      # Disable toroidal
toroidal-status   # Show current config
toroidal-2d       # Switch to 2D torus mode
toroidal-1d       # Switch to 1D cycle mode
toroidal-wide     # Sigma=0.30 (more context mixing)
toroidal-tight    # Sigma=0.08 (more local)
toroidal-mid      # Sigma=0.15 (default)
```

### How It Works

Standard attention operates on a line with a causal mask — token N can't see token N+1.
Toroidal attention wraps the sequence onto a circle Z_N (or a torus S¹×S¹ for 2D grids).
The attention matrix becomes circulant (translation-invariant kernel + softmax commuting
with cyclic shifts), diagonalized exactly by the FFT. No approximation, no kernel trick,
no low-rank assumption.

**Integration point:** `LocalProvider._ensure_loaded()` in `framework/enhanced_llm_provider.py`.
After `AutoModelForCausalLM.from_pretrained()`, when `IG_TOROIDAL_ATTENTION=1`, the model's
attention layers are patched via `framework.ig_toroidal_attention.patch_with_toroidal()`.
This replaces QK^T softmax with FFT convolution while keeping all learned Q/K/V/O projections.

### Geometry: 1D vs 2D

| Mode | Geometry | Use Case | Imscription |
|------|----------|----------|-------------|
| 1d | Z_N (single cycle) | Standard transformer sequences | ⟨𐑨𐑥𐑾𐑯𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩ |
| 2d | Z_m × Z_n (torus) | Grid-structured data, daydr33m | ⟨𐑨𐑶𐑾𐑯𐑐𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩ |

The 1D variant is default. The 2D variant auto-factorises sequence length into a near-square
torus grid via `torus_from_seqlen()`.

### CUDA Kernels (daydr33m)

GPU-native toroidal attention kernels compiled for SM 8.6 + 8.9:

```bash
# Already compiled and tested on both GPUs:
/home/mrnob0dy666/imsgct/daydr33m/libtoroidal_attn.so       # cuFFT-based (104 KB)
/home/mrnob0dy666/imsgct/daydr33m/libtoroidal_attn_cu12.so  # CUDA 12 native (64 KB)
```

Faster than the NumPy path (~0.008ms vs ~0.5ms for seq≤1024). Integration
of the CUDA path into the patch function is the next step (currently NumPy only).

### Config Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IG_TOROIDAL_ATTENTION` | (unset) | Set to `1` to enable |
| `IG_TOROIDAL_SIGMA` | `0.15` | Kernel width in windings |
| `IG_TOROIDAL_MODE` | `1d` | `1d` (Z_N cycle) or `2d` (Z_m×Z_n torus) |
| `IG_TOROIDAL_LAYERS` | (unset) | Comma-separated layer indices to patch (default: all) |

### Sigma Tuning Guide

| Sigma | Self-mass | Behavior |
|-------|-----------|----------|
| 0.05 | 84% | Tightly local — mostly self-attention |
| 0.08 | 60% | Tight — near-neighbor focused |
| 0.15 | 11% | Default — balanced local + global mixing |
| 0.30 | 3% | Wide — strong long-range mixing |
| 0.50 | ~1% | Near-uniform — almost mean pooling |

Sigma controls the length scale of the Gaussian kernel on the cyclic distance.
At sigma=0.05, 84% of attention mass is on the token itself. At sigma=0.50,
attention is nearly uniform across the sequence.

### Verification

```python
from framework.ig_toroidal_attention import verify_1d

# FFT vs O(N²) naive reference — should be ~2e-16
r = verify_1d(n_tok=64, d_model=32, sigma=0.15)
print(f"FFT vs naive error: {r['fft_vs_naive_error']:.2e}")
print(f"Shift-equivariance:  {r['shift_equivariance_error']:.2e}")
print(f"Speedup: {r['speedup']:.1f}×")
```

## Two Models at Once

The 3060 and 4070 have identical VRAM (12 GB) but the 4070 is faster
(Ada Lovelace vs Ampere, higher clock, more SMs). Strategy:

### Option A: Split one model (no room for two large ones)
```bash
export IG_DEVICES=0,1
# Qwen3-8B splits across both; 4B fits one with room for context
```

### Option B: Two processes, one per card
```bash
# Terminal 1: Python specialist on 4070
IG_DEVICES=1 uv run agents/specialists/math_operator.py "..."

# Terminal 2: Rust kernel on 3060
IG_DEVICES=0 ask --provider local --raw --ask "..."
```

### Option C: Python specialist on 4070, small model on 3060
```bash
IG_PREFER_DEVICE=1 IG_DEVICES=0,1 \
  uv run agents/specialists/quantum_operator.py "..."
# Primary: 4070 (via IG_PREFER_DEVICE)
# 3060: kept free for a second process
```

## Diagnostics

```python
from framework.ig_devices import gpu_info, flash_attention_available, attn_implementation

# What cards are detected?
print(gpu_info())
# {0: {'name': 'NVIDIA GeForce RTX 3060', 'total_gib': 12.0, 'free_gib': 10.2, ...},
#  1: {'name': 'NVIDIA GeForce RTX 4070', 'total_gib': 12.0, 'free_gib': 11.1, ...}}

# Is flash attention installed?
print(flash_attention_available())  # True/False

# Which attention implementation will be used?
print(attn_implementation())  # 'flash_attention_2' or 'sdpa'
```

Or from the shell:
```bash
# Check GPU free memory
nvidia-smi --query-gpu=index,name,memory.free --format=csv

# Check CUDA availability
python3 -c "import torch; print(torch.cuda.device_count(), 'GPUs')"

# Verify CUDA 12.4 nvcc is reachable
/usr/local/cuda-12.4/bin/nvcc --version
```

## Troubleshooting

### "device not ready" on first generate()
→ Fixed: `warmup_devices()` runs a matmul on every card before model load.
The Rust kernel does the same in `open_devices()`.

### OOM during load
→ Set `LOAD_IN_4BIT=1` for 4-bit quantization.
→ Or pin to the larger card: `IG_DEVICES=1` (use the 4070).

### Model loads but generation hangs
→ The model fell back to CPU. Check stderr for the banner:
  `!! LOCAL MODEL FELL BACK TO CPU`
→ Use a smaller checkpoint or enable 4-bit quantization.

### "CUDA out of memory" during generation
→ Context too large. The KV cache is sized from free VRAM.
→ Reduce context length or split across both cards.

### "FlashAttention is only supported on CUDA 11.7 and above"
→ You're using the system nvcc (CUDA 11.5) instead of CUDA 12.4.
→ Set `CUDA_HOME=/usr/local/cuda-12.4` and put `/usr/local/cuda-12.4/bin` first in PATH.
→ Verify: `which nvcc` should show `/usr/local/cuda-12.4/bin/nvcc`.

### "Toroidal attention patch failed"
→ Check the log — the loader falls back to flash_attn/sdpa automatically.
→ Verify the import: `python3 -c "from framework.ig_toroidal_attention import patch_with_toroidal; print('OK')"`
→ The NumPy FFT path requires no CUDA, no build, and works on CPU.
