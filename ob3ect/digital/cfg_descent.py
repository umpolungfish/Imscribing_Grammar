"""
Animated version-descent CFG for the Ob3ect.

Nodes  = each generation: seed (μΔ-ID), v0.1 … v0.10
Edges  = "imscribed" parent→child relationship

Substrate layers (horizontal bands):
  Top    (Python) : seed, v0.1
  Middle (C/ELF)  : v0.2 – v0.9
  Bottom (Silicon): v0.10

Node color by substrate:
  Python  → green  (#59a14f)
  C/ELF   → orange (#f28e2b)
  Silicon → gold   (#ffd700)

Animation:
  Phase 1 — build: versions appear in imscription order;
             substrate-crossing edges flash purple.
  Phase 2 — flow wave: pulse travels the lineage; silicon node
             pulses gold; cross-substrate edges light amber.

Output: docs/cfg_descent.gif
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

OUT = Path(__file__).parent / "docs" / "cfg_descent.gif"
BG  = "#0a0a15"

_SUBSTRATE_COLOR = {
    "python":  "#59a14f",
    "c":       "#f28e2b",
    "silicon": "#ffd700",
}

# Version definitions: (label, substrate, description)
VERSIONS = [
    ("seed",   "python",  "μΔ-ID: Python meta-circular seed"),
    ("v0.1",   "python",  "Frobenius PASS — Closure: True"),
    ("v0.2",   "c",       "Custom .o grammar → C native binary"),
    ("v0.3",   "c",       "Quine embedding — self.o in binary"),
    ("v0.4",   "c",       "Quine extraction stub activated"),
    ("v0.5",   "c",       "Grammar expansion — QUINE opcode"),
    ("v0.6",   "c",       "MACRO opcode — language deepening"),
    ("v0.7",   "c",       "Entropy pass — ΔS ≈ 0 verified"),
    ("v0.8",   "c",       "Full C self-hosting target"),
    ("v0.9",   "c",       "Pre-silicon — final C generation"),
    ("v0.10",  "silicon", "Bare-metal x86 bootloader ISO"),
]

IMSCRIPTION_EDGES: list[tuple[str, str]] = [
    ("seed",  "v0.1"),
    ("v0.1",  "v0.2"),
    ("v0.2",  "v0.3"),
    ("v0.3",  "v0.4"),
    ("v0.4",  "v0.5"),
    ("v0.5",  "v0.6"),
    ("v0.6",  "v0.7"),
    ("v0.7",  "v0.8"),
    ("v0.8",  "v0.9"),
    ("v0.9",  "v0.10"),
]

_CROSS_SUBSTRATE = {("v0.1", "v0.2"), ("v0.9", "v0.10")}

_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))
_PULSE_AMBER = np.array(mcolors.to_rgba("#ffb347"))


def make_pos() -> dict[str, tuple[float, float]]:
    """
    Horizontal bands by substrate.
    Python layer: y=0.85, C layer: y=0.5 (spread), Silicon: y=0.10
    """
    pos: dict[str, tuple[float, float]] = {}
    python_nodes = [v[0] for v in VERSIONS if v[1] == "python"]
    c_nodes      = [v[0] for v in VERSIONS if v[1] == "c"]
    sil_nodes    = [v[0] for v in VERSIONS if v[1] == "silicon"]

    for i, n in enumerate(python_nodes):
        x = (i + 1) / (len(python_nodes) + 1)
        pos[n] = (x, 0.85)

    for i, n in enumerate(c_nodes):
        x = (i + 1) / (len(c_nodes) + 1)
        pos[n] = (x, 0.50)

    for i, n in enumerate(sil_nodes):
        x = (i + 1) / (len(sil_nodes) + 1)
        pos[n] = (x, 0.12)

    return pos


def render_frame(
    ax: plt.Axes,
    pos: dict,
    labels: list[str],
    substrates: list[str],
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    revealed: set[str] | None,
    cross_flash: bool,
    pulse_center: int | None,
    pulse_sigma: int,
    N: int,
    title: str,
) -> None:
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_title(title, color="white", fontsize=8, pad=6)

    # Substrate band labels
    for y, lbl, col in [
        (0.85, "Python layer", "#59a14f"),
        (0.50, "C / ELF layer", "#f28e2b"),
        (0.12, "Silicon / x86", "#ffd700"),
    ]:
        ax.text(0.01, y + 0.08, lbl, color=col, fontsize=7,
                alpha=0.5, va="bottom", transform=ax.transData)
        ax.axhline(y=y + 0.06, color=col, lw=0.4, alpha=0.15, xmin=0, xmax=1)

    nidx = {n: i for i, n in enumerate(labels)}
    xs = np.array([pos[n][0] for n in labels])
    ys = np.array([pos[n][1] for n in labels])

    if revealed is not None:
        for u, v in IMSCRIPTION_EDGES:
            if u not in revealed or v not in revealed:
                continue
            is_cs = (u, v) in _CROSS_SUBSTRATE
            col = "#cc44ff" if is_cs else "#4e79a7"
            lw  = 2.5 if is_cs else 1.2
            al  = 0.85 if is_cs else 0.45
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        vis = [nidx[n] for n in labels if n in revealed]
        if not vis:
            return

        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()
        if cross_flash:
            for i, idx in enumerate(vis):
                if substrates[idx] == "silicon":
                    colors[i] = _PULSE_GOLD
                    sizes[i]  *= 2.5

        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=1.0, edgecolors="#ffffff55")
        for n in labels:
            if n in revealed:
                ax.text(pos[n][0], pos[n][1], n,
                        ha="center", va="center", fontsize=6.5,
                        color="#000000" if substrates[labels.index(n)] == "silicon" else "#ffffff",
                        fontweight="bold", zorder=4)

    else:
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {labels[i] for i in range(N) if weights[i] > 0.3}

        for u, v in IMSCRIPTION_EDGES:
            is_cs = (u, v) in _CROSS_SUBSTRATE
            near  = u in active or v in active
            if is_cs and near:
                col, lw, al = "#ffb347", 3.0, 0.92
            elif is_cs:
                col, lw, al = "#cc44ff", 1.8, 0.55
            elif near:
                col, lw, al = "#4e79a7", 1.8, 0.70
            else:
                col, lw, al = "#3a5f80", 0.7, 0.22
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(labels):
            w = weights[i]
            target = _PULSE_GOLD if substrates[i] == "silicon" else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 2.0 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=1.0, edgecolors="#ffffff33")
        for i, n in enumerate(labels):
            ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                    fontsize=6.5,
                    color="#000000" if substrates[i] == "silicon" else "#ffffff",
                    fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=60, flow_frames=80, fps=15, dpi=110):
    labels     = [v[0] for v in VERSIONS]
    substrates = [v[1] for v in VERSIONS]
    descs      = [v[2] for v in VERSIONS]
    N          = len(labels)

    pos = make_pos()

    base_colors = np.array([
        mcolors.to_rgba(_SUBSTRATE_COLOR[s]) for s in substrates
    ])
    base_sizes = np.array([
        200 if n in ("seed", "v0.1", "v0.10") else 120
        for n in labels
    ], dtype=float)

    pulse_sigma   = max(2, N // 4)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    # Silicon crossing happens at v0.10 reveal (last node)
    silicon_reveal_k = N  # frame where v0.10 appears

    print(f"Rendering cfg_descent.gif ({total_frames} frames) …")
    fig, ax = plt.subplots(figsize=(12, 7), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(labels[:k])
            flash    = labels[k - 1] == "v0.10"
            cur      = labels[k - 1]
            sub      = substrates[k - 1]
            title = (
                f"Ob3ect — Version Descent | imscribing: {cur} [{sub}] | "
                f"{'← bare metal!' if flash else descs[k-1]}"
            )
            render_frame(ax, pos, labels, substrates, base_colors, base_sizes,
                         revealed, flash, None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = labels[center]
            sub_at = substrates[center]
            title  = (
                f"Ob3ect — Version Descent | wave: {n_at} [{sub_at}] | "
                f"10 generations · μ∘δ = id"
            )
            render_frame(ax, pos, labels, substrates, base_colors, base_sizes,
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
