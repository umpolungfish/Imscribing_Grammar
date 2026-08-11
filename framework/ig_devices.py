"""Where a local model runs: `IG_DEVICES`, and nothing else.

One spelling for device selection across every repo here — the same string that
`ask --provider local` reads. `IG_DEVICES=0,1` names both cards, `1` pins one,
`cpu` forces the CPU, unset means every card present.

Two cards are two memories, not one pool. What that buys is a partition: a model
too large for either card alone still runs, its layers split between them, and
two cards' worth of KV cache holds a context neither could hold alone. What it
costs is the hidden state crossing the boundary once per forward.
"""

import os
from typing import List

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


def device_plan(logger, reserve_gib: float = 1.0):
    """Decide where a local model loads: one card, several, or the CPU.

    Two cards are not one big card — there is no pooled address space — but a
    model too large for either alone still runs across both, its layers split by
    accelerate with each card holding the part it can. That is what "balanced"
    means here, and `max_memory` is what makes the split honest: each card is
    offered the VRAM it actually has free right now, less a working reserve, so
    a card already busy with a display gets a smaller share instead of OOMing
    halfway through the load.

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
