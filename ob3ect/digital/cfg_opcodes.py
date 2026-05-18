"""
Animated IMASM opcode flow CFG for the Ob3ect.

Nodes  = IMASM opcodes (VINIT, TANCH, AREV, FSPLIT, AFWD, FFUSE,
         CLINK, IFIX, ISCRIB, EVALT, EVALF, ENGAGR, IMSCRIBE, QUINE)
Edges  = execution flow from the Phase 4 bootstrap sequence + self.o

The Frobenius cycle  FSPLIT → AFWD → FFUSE → ISCRIB  is the μ∘δ = id
loop and is highlighted in gold throughout.

Animation:
  Phase 1 — build: opcodes appear in execution order; Frobenius cycle
             nodes flash gold when the loop is first closed.
  Phase 2 — flow wave: Gaussian pulse travels the execution path;
             Frobenius edges pulse gold; terminal nodes (EVALT/EVALF)
             flash red/green.

Output: docs/cfg_opcodes.gif
"""

from __future__ import annotations
import io
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

OUT = Path(__file__).parent / "docs" / "cfg_opcodes.gif"
BG  = "#0a0a15"

# ── Node families ────────────────────────────────────────────────────────────
_FAMILY: dict[str, str] = {
    "VINIT":    "init",
    "TANCH":    "init",
    "AREV":     "direction",
    "AFWD":     "direction",
    "FSPLIT":   "frobenius",
    "FFUSE":    "frobenius",
    "CLINK":    "link",
    "IFIX":     "self",
    "ISCRIB":   "self",
    "EVALT":    "terminal_ok",
    "EVALF":    "terminal_err",
    "ENGAGR":   "resolve",
    "IMSCRIBE": "output",
    "QUINE":    "output",
}

_FAMILY_COLOR: dict[str, str] = {
    "frobenius":    "#ffd700",   # gold
    "self":         "#cc44ff",   # purple
    "direction":    "#f28e2b",   # orange
    "init":         "#9c9c9c",   # gray
    "link":         "#4e79a7",   # blue
    "terminal_ok":  "#59a14f",   # green
    "terminal_err": "#e15759",   # red
    "resolve":      "#20b2aa",   # teal
    "output":       "#eeeeee",   # white
}

_FROBENIUS_NODES = {"FSPLIT", "FFUSE", "AFWD"}
_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))

# ── Execution graph ──────────────────────────────────────────────────────────
# Directed edges encoding the full bootstrap sequence:
#   Phase 4 loop: VINIT→ISCRIB→AREV→FSPLIT→AFWD→FFUSE→CLINK→IFIX→ISCRIB (cycle)
#   TANCH is called by FSPLIT and FFUSE (parsing/unparsing)
#   EVALT/EVALF are terminal exits
#   self.o sequence adds ENGAGR, IMSCRIBE, QUINE
EDGES: list[tuple[str, str]] = [
    ("VINIT",    "ISCRIB"),
    ("ISCRIB",   "AREV"),
    ("AREV",     "FSPLIT"),
    ("FSPLIT",   "TANCH"),
    ("TANCH",    "AFWD"),
    ("AFWD",     "FFUSE"),
    ("FFUSE",    "TANCH"),      # FFUSE calls TANCH on regenerated source
    ("FFUSE",    "ISCRIB"),     # closure: fused result recognised → ISCRIB again
    ("ISCRIB",   "CLINK"),
    ("CLINK",    "IFIX"),
    ("IFIX",     "IMSCRIBE"),
    ("IMSCRIBE", "ENGAGR"),
    ("ENGAGR",   "EVALT"),
    ("ISCRIB",   "EVALF"),      # ISCRIB can fail → EVALF
    ("FFUSE",    "EVALF"),      # FFUSE mismatch → EVALF
    ("QUINE",    "EVALT"),      # QUINE extraction → EVALT
    ("IFIX",     "QUINE"),      # post-IFIX quine embedding path
]

# Execution order for the animation build phase
EXEC_ORDER = [
    "VINIT", "ISCRIB", "AREV", "FSPLIT", "TANCH",
    "AFWD", "FFUSE", "CLINK", "IFIX", "IMSCRIBE",
    "ENGAGR", "QUINE", "EVALT", "EVALF",
]

_FROBENIUS_EDGES = {
    ("FSPLIT", "TANCH"), ("TANCH", "AFWD"),
    ("AFWD", "FFUSE"), ("FFUSE", "TANCH"), ("FFUSE", "ISCRIB"),
}


def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()
    for n in EXEC_ORDER:
        G.add_node(n, family=_FAMILY[n])
    for u, v in EDGES:
        G.add_edge(u, v)
    return G


def render_frame(
    ax: plt.Axes,
    pos: dict,
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    revealed: set[str] | None,
    frob_flash: bool,
    pulse_center: int | None,
    pulse_sigma: int,
    N: int,
    title: str,
) -> None:
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.15, 1.15)
    ax.set_title(title, color="white", fontsize=8, pad=6)

    xs = np.array([pos[n][0] for n in EXEC_ORDER])
    ys = np.array([pos[n][1] for n in EXEC_ORDER])
    nidx = {n: i for i, n in enumerate(EXEC_ORDER)}

    if revealed is not None:
        # Phase 1: build
        for u, v in EDGES:
            if u not in revealed or v not in revealed:
                continue
            is_frob = (u, v) in _FROBENIUS_EDGES
            col = "#ffd700" if is_frob else "#3a5f80"
            lw  = 2.5 if is_frob else 1.0
            al  = 0.9 if is_frob else 0.4
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        vis = [nidx[n] for n in EXEC_ORDER if n in revealed]
        if not vis:
            return

        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()

        if frob_flash:
            for i, idx in enumerate(vis):
                if EXEC_ORDER[idx] in _FROBENIUS_NODES:
                    colors[i] = _PULSE_GOLD
                    sizes[i] *= 2.2

        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=0.8, edgecolors="#ffffff44")

        # Label revealed nodes
        for n in EXEC_ORDER:
            if n in revealed:
                fam = _FAMILY[n]
                tc = "#000000" if fam in ("output", "terminal_ok") else "#ffffff"
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=5.5, color=tc, fontweight="bold", zorder=4)

    else:
        # Phase 2: flow wave
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)

        active = {EXEC_ORDER[i] for i in range(N) if weights[i] > 0.3}

        for u, v in EDGES:
            is_frob = (u, v) in _FROBENIUS_EDGES
            near    = u in active or v in active
            if is_frob and near:
                col, lw, al = "#ffd700", 3.0, 0.95
            elif is_frob:
                col, lw, al = "#cc9900", 1.8, 0.55
            elif near:
                col, lw, al = "#cc44ff", 1.8, 0.70
            else:
                col, lw, al = "#3a5f80", 0.7, 0.22
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(EXEC_ORDER):
            w = weights[i]
            target = _PULSE_GOLD if n in _FROBENIUS_NODES else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 2.0 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.8, edgecolors="#ffffff33")

        for n in EXEC_ORDER:
            fam = _FAMILY[n]
            tc = "#000000" if fam in ("output", "terminal_ok") else "#ffffff"
            ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                    fontsize=5.5, color=tc, fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=50, flow_frames=80, fps=15, dpi=110):
    G = build_graph()

    # Hierarchical layout: put EVALT/EVALF at bottom, VINIT at top
    pos = nx.shell_layout(G, nlist=[
        ["VINIT"],
        ["ISCRIB", "AREV"],
        ["FSPLIT", "TANCH", "AFWD"],
        ["FFUSE", "CLINK"],
        ["IFIX", "IMSCRIBE", "QUINE"],
        ["ENGAGR"],
        ["EVALT", "EVALF"],
    ])
    # Normalize to [0,1]
    all_xy = np.array(list(pos.values()))
    mn, mx = all_xy.min(0), all_xy.max(0)
    pos = {n: ((xy - mn) / (mx - mn + 1e-9) * 0.9 + 0.05).tolist()
           for n, xy in pos.items()}
    pos = {n: (v[0], v[1]) for n, v in pos.items()}

    N = len(EXEC_ORDER)

    base_colors = np.array([
        mcolors.to_rgba(_FAMILY_COLOR[_FAMILY[n]]) for n in EXEC_ORDER
    ])
    base_sizes = np.array([
        120 if _FAMILY[n] in ("frobenius", "self") else
        80 if _FAMILY[n] in ("terminal_ok", "terminal_err") else 60
        for n in EXEC_ORDER
    ], dtype=float)

    # Frobenius loop closes at FFUSE (index 6)
    frob_close_idx = EXEC_ORDER.index("FFUSE")

    pulse_sigma   = max(3, N // 5)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    print(f"Rendering cfg_opcodes.gif ({total_frames} frames) …")
    fig, ax = plt.subplots(figsize=(9, 9), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(EXEC_ORDER[:k])
            flash    = k - 1 == frob_close_idx
            center_n = EXEC_ORDER[k - 1]
            title = (
                f"Ob3ect — IMASM Opcode Flow | build: {center_n} | "
                f"{'Frobenius loop closed! μ∘δ = id' if flash else 'μ∘δ = id'}"
            )
            render_frame(ax, pos, base_colors, base_sizes,
                         revealed, flash, None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = EXEC_ORDER[center]
            title  = (
                f"Ob3ect — IMASM Opcode Flow | wave: {n_at} [{_FAMILY[n_at]}] | "
                f"μ∘δ = id"
            )
            render_frame(ax, pos, base_colors, base_sizes,
                         None, False, center, pulse_sigma, N, title)

        frames_pil.append(fig_to_pil(fig, dpi))

    print()
    plt.close(fig)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames_rgb = [fr.convert("RGB") for fr in frames_pil]
    frames_rgb[0].save(str(OUT), save_all=True, append_images=frames_rgb[1:],
                       duration=1000 // fps, loop=0, optimize=False)
    print(f"Done: {OUT}  ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
