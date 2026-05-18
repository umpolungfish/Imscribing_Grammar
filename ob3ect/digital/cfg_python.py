"""
Animated Python call-graph CFG for the Ob3ect.

Statically analyses frob.py and ob3ect-imscriber.py via AST to extract
the real function-call graph. Nodes = functions; edges = calls.

Node color by file:
  frob.py           → purple (#9c59d1)
  ob3ect-imscriber  → orange (#f28e2b)

Special highlight:
  Frobenius functions (FSPLIT, FFUSE, frobenius_phase) → gold
  Terminal functions  (EVALT, EVALF)                   → green/red
  Bootstrap entry     (bootstrap_compiler, bootstrap_ob3ect) → cyan

Animation:
  Phase 1 — build: functions appear in definition order;
             cross-file call edges flash purple.
  Phase 2 — flow wave: Gaussian pulse travels the call graph.

Output: docs/cfg_python.gif
"""

from __future__ import annotations
import ast
import io
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

DIGITAL = Path(__file__).parent
OUT     = DIGITAL / "docs" / "cfg_python.gif"
BG      = "#0a0a15"

_FILE_COLOR = {
    "frob":       "#9c59d1",
    "imscriber":  "#f28e2b",
}

_SPECIAL_COLOR = {
    "FSPLIT":            "#ffd700",
    "FFUSE":             "#ffd700",
    "frobenius_phase":   "#ffd700",
    "EVALT":             "#59a14f",
    "EVALF":             "#e15759",
    "bootstrap_compiler":"#00ced1",
    "bootstrap_ob3ect":  "#00ced1",
    "bootstrap_minimal": "#00ced1",
    "ISCRIB":            "#cc44ff",
}

_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))
_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))


# ── AST-based call graph extractor ──────────────────────────────────────────

def extract_calls(source: str, file_tag: str) -> tuple[
    list[str],                          # functions defined (in order)
    list[tuple[str, str]],              # (caller, callee) edges
]:
    tree = ast.parse(source)
    defined: list[str] = []
    calls:   list[tuple[str, str]] = []

    # Collect all top-level function defs
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined.append(node.name)

    # For each function, find calls to other defined functions
    func_nodes = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

    for fname, fnode in func_nodes.items():
        for node in ast.walk(fnode):
            if isinstance(node, ast.Call):
                callee = None
                if isinstance(node.func, ast.Name):
                    callee = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    callee = node.func.attr
                if callee and callee in func_nodes and callee != fname:
                    calls.append((fname, callee))

    return defined, calls


def build_graph() -> tuple[nx.DiGraph, dict[str, str], list[str]]:
    G    = nx.DiGraph()
    file_of: dict[str, str] = {}
    def_order: list[str] = []

    for fname, tag in [
        ("frob.py",            "frob"),
        ("ob3ect-imscriber.py","imscriber"),
    ]:
        path = DIGITAL / fname
        if not path.exists():
            print(f"  Warning: {fname} not found, skipping.")
            continue
        source = path.read_text(encoding="utf-8")
        defined, calls = extract_calls(source, tag)
        for fn in defined:
            if fn not in G.nodes():
                G.add_node(fn, file=tag)
                file_of[fn] = tag
                def_order.append(fn)
        for u, v in calls:
            if u in G and v in G:
                G.add_edge(u, v)

    return G, file_of, def_order


def _node_color(name: str, file_of: dict[str, str]) -> str:
    if name in _SPECIAL_COLOR:
        return _SPECIAL_COLOR[name]
    return _FILE_COLOR.get(file_of.get(name, "frob"), "#cccccc")


def render_frame(
    ax: plt.Axes,
    all_nodes: list[str],
    pos: dict,
    edges: list[tuple[str, str]],
    file_of: dict[str, str],
    base_colors: np.ndarray,
    base_sizes: np.ndarray,
    cross_file_edges: set[tuple[str, str]],
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
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_title(title, color="white", fontsize=7.5, pad=6)

    nidx = {n: i for i, n in enumerate(all_nodes)}
    xs = np.array([pos[n][0] for n in all_nodes])
    ys = np.array([pos[n][1] for n in all_nodes])

    frob_nodes = {"FSPLIT", "FFUSE", "frobenius_phase"}

    if revealed is not None:
        for u, v in edges:
            if u not in revealed or v not in revealed:
                continue
            is_cf   = (u, v) in cross_file_edges
            is_frob = u in frob_nodes or v in frob_nodes
            col = "#ffd700" if is_frob else ("#cc44ff" if is_cf else "#3a5f80")
            lw  = 2.5 if is_frob else (2.0 if is_cf else 0.8)
            al  = 0.90 if is_frob else (0.75 if is_cf else 0.30)
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        vis = [nidx[n] for n in all_nodes if n in revealed]
        if not vis:
            return

        colors = base_colors[vis].copy()
        sizes  = base_sizes[vis].copy()
        if cross_flash:
            colors = np.tile(_PULSE_GOLD, (len(vis), 1)) * 0.7 + colors * 0.3

        ax.scatter(xs[vis], ys[vis], c=colors, s=sizes,
                   zorder=3, linewidths=0.5, edgecolors="#ffffff33")
        for n in all_nodes:
            if n in revealed:
                ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                        fontsize=4.5, color="#ffffff", fontweight="bold", zorder=4)

    else:
        dists   = np.abs(np.arange(N) - pulse_center)
        dists   = np.minimum(dists, N - dists)
        weights = np.exp(-0.5 * (dists / pulse_sigma) ** 2)
        active  = {all_nodes[i] for i in range(N) if weights[i] > 0.3}

        for u, v in edges:
            is_cf   = (u, v) in cross_file_edges
            is_frob = u in frob_nodes or v in frob_nodes
            near    = u in active or v in active
            if is_frob and near:
                col, lw, al = "#ffd700", 3.0, 0.95
            elif is_frob:
                col, lw, al = "#cc9900", 1.8, 0.55
            elif is_cf and near:
                col, lw, al = "#ffb347", 2.5, 0.85
            elif is_cf:
                col, lw, al = "#cc44ff", 1.5, 0.50
            elif near:
                col, lw, al = "#9c59d1", 1.5, 0.60
            else:
                col, lw, al = "#3a5f80", 0.6, 0.18
            ax.annotate("", xy=(pos[v][0], pos[v][1]),
                        xytext=(pos[u][0], pos[u][1]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                        zorder=1)

        blended = np.empty_like(base_colors)
        for i, n in enumerate(all_nodes):
            w = weights[i]
            target = _PULSE_GOLD if n in frob_nodes else _PULSE_WHITE
            blended[i] = base_colors[i] * (1 - w) + target * w
        blended = np.clip(blended, 0, 1)
        sizes = base_sizes + base_sizes * 2.0 * weights

        ax.scatter(xs, ys, c=blended, s=sizes, zorder=3,
                   linewidths=0.5, edgecolors="#ffffff22")
        for n in all_nodes:
            ax.text(pos[n][0], pos[n][1], n, ha="center", va="center",
                    fontsize=4.5, color="#ffffff", fontweight="bold", zorder=4)


def fig_to_pil(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def main(build_frames=55, flow_frames=85, fps=15, dpi=110):
    G, file_of, def_order = build_graph()

    # Keep only nodes in the largest weakly-connected component
    if G.number_of_nodes() == 0:
        print("No functions found — check file paths.")
        return

    wcc = max(nx.weakly_connected_components(G), key=len)
    C   = G.subgraph(wcc).copy()
    all_nodes = [n for n in def_order if n in C.nodes()]
    N = len(all_nodes)

    print(f"  {N} functions, {C.number_of_edges()} calls")

    # Cross-file edges
    cross_file_edges: set[tuple[str, str]] = {
        (u, v) for u, v in C.edges()
        if file_of.get(u) != file_of.get(v)
    }
    print(f"  Cross-file edges: {len(cross_file_edges)}")

    pos = nx.spring_layout(C, k=0.3, iterations=300, seed=42)

    degrees = dict(C.degree())
    max_deg = max(degrees.values()) if degrees else 1

    base_colors = np.array([
        mcolors.to_rgba(_node_color(n, file_of)) for n in all_nodes
    ])
    base_sizes = np.array([
        60 + 80 * (np.log1p(degrees.get(n, 1)) / np.log1p(max_deg)) ** 1.5
        for n in all_nodes
    ])

    edges = list(C.edges())
    pulse_sigma   = max(4, N // 6)
    pulse_centers = np.linspace(0, N - 1, flow_frames).astype(int)
    total_frames  = build_frames + flow_frames

    print(f"  Rendering cfg_python.gif ({total_frames} frames) …")
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=BG)
    frames_pil = []

    for f in range(total_frames):
        print(f"\r  {(f+1)/total_frames*100:5.1f}%", end="", flush=True)

        if f < build_frames:
            frac     = (f + 1) / build_frames
            k        = max(1, int(frac * N))
            revealed = set(all_nodes[:k])
            cur      = all_nodes[k - 1]
            src      = file_of.get(cur, "?")
            cross_flash = any(
                (u, v) in cross_file_edges
                for u, v in C.edges()
                if u in revealed and v in revealed
            )
            title = (
                f"Ob3ect — Python Call Graph | revealing: {cur} [{src}] | "
                f"{C.number_of_edges()} calls · {len(cross_file_edges)} cross-file"
            )
            render_frame(ax, all_nodes, pos, edges, file_of, base_colors, base_sizes,
                         cross_file_edges, revealed, cross_flash,
                         None, pulse_sigma, N, title)
        else:
            fi     = f - build_frames
            center = pulse_centers[fi]
            n_at   = all_nodes[center]
            src    = file_of.get(n_at, "?")
            title  = (
                f"Ob3ect — Python Call Graph | wave: {n_at} [{src}] | "
                f"μ∘δ = id"
            )
            render_frame(ax, all_nodes, pos, edges, file_of, base_colors, base_sizes,
                         cross_file_edges, None, False,
                         center, pulse_sigma, N, title)

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
