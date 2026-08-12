"""Where a local model runs: `IG_DEVICES`, and nothing else.

One spelling for device selection across every repo here — the same string that
`ask --provider local` reads. `IG_DEVICES=0,1` names both cards, `1` pins one,
`cpu` forces the CPU, unset means every card present.

Two cards are two memories, not one pool. What that buys is a partition: a model
too large for either card alone still runs, its layers split between them, and
two cards' worth of KV cache holds a context neither could hold alone. What it
costs is the hidden state crossing the boundary once per forward.

ASYMMETRIC SETUP (3060 + 4070): IG_DEVICES=0,1 splits the model across both cards
by default. For a model that fits the 4070 alone, use IG_DEVICES=<4070-ordinal>
to pin it to the larger card and keep the 3060 free for a second process (Rust
kernel, embedding model, etc.). Set IG_PREFER_DEVICE=<ordinal> to route the PRIMARY
model to the larger card while still using both for memory when splitting.
"""

import os
from typing import Dict, List, Optional, Tuple

def cpu_forced() -> bool:
    """CPU is forced by IG_DEVICES=cpu, or by the legacy FORCE_CPU flag."""
    if os.getenv("IG_DEVICES", "").strip().lower() == "cpu":
        return True
    return os.getenv("IG_LOCAL_CPU", os.getenv("FORCE_CPU", "")).strip() not in ("", "0")


def devices() -> List[int]:
    """CUDA ordinals this process may use, from IG_DEVICES ("0,1", "1", "auto").

    An empty list means "every card present" — the caller decides what that
    implies. IG_DEVICES is the one spelling across every repo here; it means the
    same thing to `ask --provider local` as it does to this loader.
    """
    spec = os.getenv("IG_DEVICES", "").strip().lower()
    if spec in ("", "auto", "all", "cpu"):
        return []
    out: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if part.isdigit() and int(part) not in out:
            out.append(int(part))
    return out


def prefer_device() -> Optional[int]:
    """The GPU ordinal to prefer for the PRIMARY model, from IG_PREFER_DEVICE.

    In an asymmetric setup (3060 + 4070), set IG_PREFER_DEVICE to the larger
    card's ordinal. The model will favour that card when it fits, while still
    splitting across both when it does not.

    Returns None when unset (the default — every card is equal).
    """
    spec = os.getenv("IG_PREFER_DEVICE", "").strip()
    if spec.isdigit():
        return int(spec)
    return None


def flash_attention_available() -> bool:
    """Whether flash_attention_2 is installed and usable on at least one GPU.

    Qwen3 models on Ampere (3060: SM 8.6, 4070: SM 8.9) see ~2× throughput
    improvement with flash_attention_2 over sdpa at long context lengths.
    Returns True when `pip install flash-attn` has been run and the package
    imports successfully.
    """
    try:
        import flash_attn
        return True
    except ImportError:
        pass
    # Also check for the v2 variant packaging
    try:
        import flash_attn_2_cuda
        return True
    except ImportError:
        pass
    return False


def attn_implementation() -> str:
    """The best available attention implementation for the current hardware.

    Priority: flash_attention_2 > sdpa > eager.
    sdpa is the transformers default on torch >= 2.0 and is memory-efficient
    but not as fast as flash_attention_2 for Ampere+ cards.
    """
    if flash_attention_available():
        return "flash_attention_2"
    try:
        import torch
        if hasattr(torch.backends.cuda, "flash_sdp_enabled"):
            return "sdpa"
    except ImportError:
        pass
    return "sdpa"


def warmup_devices(indices: List[int], logger=None) -> List[int]:
    """Warm up every CUDA device in `indices` before model loading.

    A matmul + synchronize per card kicks each device out of the suspended
    state that produces "device not ready" on the first generate() under
    WSL2 and after an OOM. Returns the list of indices that survived warm-up.

    Call this BEFORE from_pretrained, not inside generate(). The model load
    itself keeps the device awake; this is for the gap between process start
    and the first forward pass.
    """
    try:
        import torch
    except Exception:
        return []
    if not indices:
        return []
    ok: List[int] = []
    for i in indices:
        if i >= torch.cuda.device_count():
            continue
        try:
            _t = torch.randn(1000, 1000, device=f"cuda:{i}", dtype=torch.float16)
            torch.matmul(_t, _t)
            torch.cuda.synchronize(i)
            del _t
            ok.append(i)
        except Exception as err:
            if logger:
                logger.warning(f"GPU {i} warm-up failed ({err}); leaving it out.")
    return ok


def gpu_info(indices: Optional[List[int]] = None) -> Dict[int, Dict[str, object]]:
    """Return per-GPU metadata: name, total VRAM, free VRAM, compute capability.

    Call for diagnostics and for deciding which model size fits which card.
    """
    try:
        import torch
    except Exception:
        return {}
    if indices is None:
        indices = list(range(torch.cuda.device_count()))
    info: Dict[int, Dict[str, object]] = {}
    for i in indices:
        if i >= torch.cuda.device_count():
            continue
        try:
            free, total = torch.cuda.mem_get_info(i)
            props = torch.cuda.get_device_properties(i)
            info[i] = {
                "name": props.name,
                "total_gib": round(total / 1024**3, 1),
                "free_gib": round(free / 1024**3, 1),
                "compute_capability": f"{props.major}.{props.minor}",
                "multi_processor_count": props.multi_processor_count,
            }
        except Exception:
            continue
    return info


def device_plan(logger, reserve_gib: float = 1.0):
    """Decide where a local model loads: one card, several, or the CPU.

    Two cards are not one big card — there is no pooled address space — but a
    model too large for either alone still runs across both, its layers split by
    accelerate with each card holding the part it can. That is what "balanced"
    means here, and `max_memory` is what makes the split honest: each card is
    offered the VRAM it actually has free right now, less a working reserve, so
    a card already busy with a display gets a smaller share instead of OOMing
    halfway through the load.

    ASYMMETRIC PREFERENCE: When IG_PREFER_DEVICE is set, and the model fits that
    card alone (with reserve), the plan returns a single-device map for that card.
    The other card is kept free for a second process (kernel, embedding, etc.).

    Returns (device_map, max_memory) ready to pass to `from_pretrained`.
    """
    try:
        import torch
    except Exception:
        return "cpu", None
    if cpu_forced() or not torch.cuda.is_available():
        return "cpu", None

    wanted = devices() or list(range(torch.cuda.device_count()))
    usable = []
    for i in wanted:
        try:
            free = torch.cuda.mem_get_info(i)[0]
        except Exception:
            continue
        if free > 2 * 1024 ** 3:
            usable.append((i, free))
    if not usable:
        logger.warning("No GPU has >2 GB free; loading on CPU.")
        return "cpu", None

    # Warm up each card before the weights land on it: a matmul + synchronize
    # kicks the device out of the suspended state that produces "device not
    # ready" on the first generate() under WSL2 and after an OOM.
    warm = []
    for i, free in usable:
        try:
            _t = torch.randn(1000, 1000, device=f"cuda:{i}", dtype=torch.float16)
            torch.matmul(_t, _t)
            torch.cuda.synchronize(i)
            del _t
            warm.append((i, free))
        except Exception as err:
            logger.warning(f"GPU {i} warm-up failed ({err}); leaving it out.")
    if not warm:
        logger.warning("No GPU survived warm-up; loading on CPU.")
        return "cpu", None

    # ── Asymmetric preference: pin to the preferred card when it fits ──
    pref = prefer_device()
    if pref is not None and len(warm) > 1:
        pref_entry = next(((i, f) for i, f in warm if i == pref), None)
        if pref_entry is not None:
            i, free = pref_entry
            logger.info(
                f"IG_PREFER_DEVICE={pref}: pinning primary model to GPU {i} "
                f"({free // 1024**3} GB free). Other card(s) kept free."
            )
            return {"": i}, None

    if len(warm) == 1:
        i, free = warm[0]
        logger.info(f"Selected GPU {i} ({free // 1024**3} GB free).")
        return {"": i}, None

    max_memory = {i: f"{max(free / 1024**3 - reserve_gib, 0.5):.1f}GiB" for i, free in warm}
    logger.info(
        "Splitting the model across GPUs "
        + ", ".join(f"{i}:{max_memory[i]}" for i, _ in warm)
    )
    return "balanced", max_memory



def torch_device(logger=None):
    """The single torch device this run should use — the first card named by
    IG_DEVICES that opens, else the one with the most free VRAM, else the CPU.

    Training a model that fits one card does not want it split: the way both
    cards work at once here is two runs, `IG_DEVICES=0` and `IG_DEVICES=1`, one
    model each with the whole card to itself. This returns the card THIS run owns.
    """
    try:
        import torch
    except Exception:
        return "cpu"
    if cpu_forced() or not torch.cuda.is_available():
        return torch.device("cpu")
    wanted = devices()
    if wanted:
        for i in wanted:
            if i < torch.cuda.device_count():
                return torch.device(f"cuda:{i}")
        if logger:
            logger.warning(f"IG_DEVICES={wanted} names no present card; falling back.")
    best = max(range(torch.cuda.device_count()), key=lambda i: torch.cuda.mem_get_info(i)[0])
    return torch.device(f"cuda:{best}")


def data_parallel(model, logger=None):
    """Wrap `model` so a training batch is split across every card IG_DEVICES
    names, when there is more than one and the model fits on each.

    This is the other kind of splitting: the model is replicated, the BATCH is
    divided, and the gradients are summed back. It is what to reach for when the
    model fits a single card and the throughput is the constraint — the opposite
    case from the layer split, which is for a model that does not fit at all.
    Returns the model unchanged when a single card is in play.
    """
    try:
        import torch
    except Exception:
        return model
    if cpu_forced() or not torch.cuda.is_available():
        return model
    ids = devices() or list(range(torch.cuda.device_count()))
    ids = [i for i in ids if i < torch.cuda.device_count()]
    if len(ids) < 2:
        return model
    if logger:
        logger.info(f"Splitting each batch across GPUs {ids}.")
    return torch.nn.DataParallel(model, device_ids=ids)
