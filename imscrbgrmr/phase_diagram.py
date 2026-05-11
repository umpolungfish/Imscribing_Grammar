"""
Tuple-Space Phase Diagram — imscrbgrmr/phase_diagram.py  (v0.4.0)

Extracts phase transition signals from tuple distances.

Each imscription is a point in the eleven-dimensional primitive space.
Large jumps in pairwise distance correspond to phase boundaries in that space.
The module computes:

  1. Full N×N distance matrix
  2. Ranked phase-boundary candidates (maximal Δd jumps)
  3. Hierarchical clustering (Ward linkage on distances)
  4. 2-D MDS projection (metric multidimensional scaling)
  5. Annotated visual output:
       - Dendrogram: branch height = tuple distance
       - Phase map (MDS 2-D scatter): Ω color, Factor-8 marker, K_teshlig ring

Interpretation of features:
  - Tall dendrogram branches → large structural discontinuity → phase boundary candidate
  - Factor-8 markers (★) → quantum criticality fingerprint (TFI/heavy-fermion)
  - K_teshlig→K_lambda universal cost (+2.303 nats) appears as parallel trajectory in MDS
  - Ω color encodes topological class:
      grey   = TRIVIAL (Ω₀)
      blue   = Z_CLASS (Ω_Z)
      green  = Z2_CLASS (Ω_Z₂)
      red    = NON_ABELIAN (Ω_NA)
      orange = CHERN (Ω_Ch)

CLI:
  imscribe phase-diagram [NAME [NAME ...]] [--save PATH] [--text-only] [--format text|json]

Python API:
  from imscrbgrmr.phase_diagram import build_phase_map, PhaseDiagram
  pd = build_phase_map(imscription_names)
  pd.print_report()
  pd.plot(save_path="phase_map.png")
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

from .models import Imscription, TopoIndex, KineticCharacter, Granularity, Fidelity, Dimensionality
from .algebra import tuple_distance, mahalanobis_distance
from .registry import global_catalog
from .varma_probe import score_phi_c_candidacy


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_OMEGA_COLOR = {
    None:                  "#888888",   # unset
    TopoIndex.TRIVIAL:     "#999999",   # grey
    TopoIndex.Z_CLASS:     "#3a7eca",   # blue
    TopoIndex.Z2_CLASS:    "#2ca02c",   # green
    TopoIndex.CHERN:       "#ff7f0e",   # orange
    TopoIndex.NON_ABELIAN: "#d62728",   # red
}

_OMEGA_LABEL = {
    None:                  "unset",
    TopoIndex.TRIVIAL:     "Ω₀ TRIVIAL",
    TopoIndex.Z_CLASS:     "Ω_Z ℤ-class",
    TopoIndex.Z2_CLASS:    "Ω_Z₂ ℤ₂-class",
    TopoIndex.CHERN:       "Ω_Ch CHERN",
    TopoIndex.NON_ABELIAN: "Ω_NA NON-ABELIAN",
}


def _is_factor8(s: Imscription) -> bool:
    """Factor 8 trigger: G_ℵ + F_ℏ + K_teshlig + ¬D_∞."""
    return (
        s.granularity == Granularity.GLOBAL
        and s.fidelity == Fidelity.HIGH
        and s.kinetic_character == KineticCharacter.TRAP
        and "infinity" not in s.dimensionality.value
    )


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PhaseCandidate:
    """A pair of imscriptions that defines a phase boundary candidate."""
    name_a: str
    name_b: str
    distance: float
    rank: int
    boundary_type: str          # "major" | "intermediate" | "minor"
    primitives_differ: List[str] = field(default_factory=list)


@dataclass
class PhaseDiagram:
    """
    Full phase-space analysis for a set of imscriptions.

    Attributes:
        imscription_names: Ordered list of names (rows/cols of distance_matrix)
        distance_matrix: N×N numpy array of pairwise tuple distances
        candidates: Ranked phase boundary candidates (largest Δd first)
        linkage_matrix: Ward linkage matrix from scipy
        mds_coords: N×2 MDS coordinates (if computed)
        factor8_flags: bool list — True where Factor 8 fires
        omega_values: list of TopoIndex (or None) for each imscription
        k_trap_flags: bool list — True where kinetic character is K_teshlig
    """
    imscription_names: List[str]
    distance_matrix: np.ndarray
    candidates: List[PhaseCandidate]
    linkage_matrix: np.ndarray
    mds_coords: Optional[np.ndarray]
    factor8_flags: List[bool]
    omega_values: List[Optional[TopoIndex]]
    k_trap_flags: List[bool]
    metric: str = "diagonal"

    # ------------------------------------------------------------------ #
    def print_report(self) -> None:
        """Print a human-readable phase diagram report."""
        n = len(self.imscription_names)
        print("=" * 72)
        print("  TUPLE-SPACE PHASE DIAGRAM REPORT")
        print("=" * 72)
        print()

        # Distance matrix
        print("── Distance Matrix ──")
        header = f"{'':28}" + "".join(f"{s[:7]:>8}" for s in self.imscription_names)
        print(header)
        for i, a in enumerate(self.imscription_names):
            row = f"{a:<28}" + "".join(
                f"{'---':>8}" if i == j else f"{self.distance_matrix[i, j]:>8.2f}"
                for j in range(n)
            )
            print(row)
        print()

        # Phase boundary candidates
        print("── Phase Boundary Candidates (ranked by Δd) ──")
        for c in self.candidates[:10]:
            flag8_a = "★" if self.factor8_flags[self.imscription_names.index(c.name_a)] else " "
            flag8_b = "★" if self.factor8_flags[self.imscription_names.index(c.name_b)] else " "
            print(
                f"  [{c.rank:2d}] {c.boundary_type:>12}  "
                f"{c.name_a}{flag8_a} ↔ {c.name_b}{flag8_b}  "
                f"d={c.distance:.3f}  "
                f"Δ-prims: {', '.join(c.primitives_differ) or '—'}"
            )
        print()

        # Factor 8 summary
        f8 = [n for n, f in zip(self.imscription_names, self.factor8_flags) if f]
        print(f"── Factor 8 (quantum criticality): {len(f8)} imscriptions ──")
        for name in f8:
            print(f"  ★ {name}")
        print()

        # K universality
        k_trap = [n for n, f in zip(self.imscription_names, self.k_trap_flags) if f]
        print(f"── K_teshlig → K_lambda universal cost (+2.303 nats) candidates: {len(k_trap)} ──")
        for name in k_trap:
            print(f"  ○ {name}")
        print()

        # Ω classes
        print("── Topological Class (Ω) ──")
        from collections import defaultdict
        by_omega: Dict[Any, List[str]] = defaultdict(list)
        for name, omega in zip(self.imscription_names, self.omega_values):
            by_omega[omega].append(name)
        omega_order = [None, TopoIndex.TRIVIAL, TopoIndex.Z2_CLASS,
                       TopoIndex.Z_CLASS, TopoIndex.CHERN, TopoIndex.NON_ABELIAN]
        for omega in omega_order:
            if omega in by_omega:
                label = _OMEGA_LABEL.get(omega, str(omega))
                print(f"  {label}: {', '.join(by_omega[omega])}")
        print()
        print("  Legend: ★ = Factor-8 trigger  ○ = K_teshlig (MBL candidate)")
        print("=" * 72)

    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        """Return JSON-serializable representation."""
        return {
            "imscriptions": self.imscription_names,
            "distance_matrix": self.distance_matrix.tolist(),
            "phase_candidates": [
                {
                    "rank": c.rank,
                    "name_a": c.name_a,
                    "name_b": c.name_b,
                    "distance": c.distance,
                    "boundary_type": c.boundary_type,
                    "primitives_differ": c.primitives_differ,
                    "factor8_a": self.factor8_flags[self.imscription_names.index(c.name_a)],
                    "factor8_b": self.factor8_flags[self.imscription_names.index(c.name_b)],
                }
                for c in self.candidates
            ],
            "factor8": [n for n, f in zip(self.imscription_names, self.factor8_flags) if f],
            "k_trap": [n for n, f in zip(self.imscription_names, self.k_trap_flags) if f],
            "omega": {n: (o.value if o else None) for n, o in
                      zip(self.imscription_names, self.omega_values)},
            "mds_coords": self.mds_coords.tolist() if self.mds_coords is not None else None,
        }

    # ------------------------------------------------------------------ #
    def plot(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        Render two-panel phase diagram:
          Left:  Ward dendrogram (branch height = tuple distance)
          Right: MDS 2-D phase map (Ω color, Factor-8 star, K_teshlig ring)
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.lines import Line2D
            from scipy.cluster.hierarchy import dendrogram as scipy_dendrogram
        except ImportError:
            print("[phase_diagram] matplotlib not available — run `pip install matplotlib`")
            return

        fig, axes = plt.subplots(2, 1, figsize=(14, 20))
        fig.suptitle(
            "Imscribing Grammar Tuple-Space Phase Diagram  (v0.4.0)",
            fontsize=20, fontweight="bold", y=1.01
        )

        # ── Panel A: Dendrogram ──────────────────────────────────────────
        ax1 = axes[0]
        scipy_dendrogram(
            self.linkage_matrix,
            labels=self.imscription_names,
            ax=ax1,
            leaf_rotation=40,
            leaf_font_size=13,
            color_threshold=0.7 * max(self.linkage_matrix[:, 2]),
            link_color_func=lambda k: ["#3a7eca", "#d62728", "#e08c00",
                                        "#2ca02c", "#9467bd", "#555555"][k % 6],
        )
        ax1.set_title("Hierarchical Clustering  (Ward linkage on tuple distances)",
                      fontsize=15, pad=12)
        _METRIC_LABEL = {
            "diagonal": "Tuple distance  (weighted Euclidean, §26.1)",
            "mahalanobis": "Mahalanobis distance  (g = Σ⁻¹, §26.2)",
        }
        ax1.set_ylabel(_METRIC_LABEL.get(self.metric, "Distance"), fontsize=12, labelpad=8)
        ax1.set_xlabel("")
        ax1.tick_params(axis="y", labelsize=12)
        for spine in ax1.spines.values():
            spine.set_linewidth(1.4)

        # Annotate Factor-8 leaf labels with ★
        for label in ax1.get_xticklabels():
            name = label.get_text()
            if name in self.imscription_names:
                idx = self.imscription_names.index(name)
                if self.factor8_flags[idx]:
                    label.set_text(f"★ {name}")
                    label.set_color("#d62728")
                    label.set_fontweight("bold")

        # Horizontal line at the largest inter-cluster gap (primary phase boundary)
        if len(self.linkage_matrix) >= 2:
            heights = sorted(self.linkage_matrix[:, 2])
            gaps = [heights[i+1] - heights[i] for i in range(len(heights)-1)]
            if gaps:
                biggest_gap_idx = gaps.index(max(gaps))
                threshold = (heights[biggest_gap_idx] + heights[biggest_gap_idx+1]) / 2
                ax1.axhline(threshold, color="#e05c00", linestyle="--", linewidth=2.2,
                            label=f"Primary phase boundary (d={threshold:.2f})")
                ax1.legend(fontsize=12, loc="upper left", framealpha=0.9)

        # ── Panel B: MDS Phase Map ───────────────────────────────────────
        ax2 = axes[1]
        if self.mds_coords is not None:
            coords = self.mds_coords
            for idx, name in enumerate(self.imscription_names):
                omega = self.omega_values[idx]
                color = _OMEGA_COLOR.get(omega, "#888888")
                is_f8 = self.factor8_flags[idx]
                is_ktrap = self.k_trap_flags[idx]

                # K_teshlig ring (outer circle)
                if is_ktrap:
                    ax2.scatter(coords[idx, 0], coords[idx, 1],
                                s=900, color="none", edgecolors="#e08c00",
                                linewidths=3.5, zorder=3)

                # Main point
                marker = "*" if is_f8 else "o"
                size = 700 if is_f8 else 450
                ax2.scatter(coords[idx, 0], coords[idx, 1],
                            s=size, color=color, marker=marker,
                            edgecolors="white", linewidths=1.5, zorder=4)

                # Label
                ax2.annotate(
                    name.replace("_", "\n"),
                    xy=(coords[idx, 0], coords[idx, 1]),
                    xytext=(10, 10), textcoords="offset points",
                    fontsize=11, fontweight="bold", color="#111111",
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="none"),
                    zorder=5,
                )

            # Draw lines between top-5 phase boundary candidates
            for c in self.candidates[:5]:
                ia = self.imscription_names.index(c.name_a)
                ib = self.imscription_names.index(c.name_b)
                alpha = 0.15 + 0.07 * (5 - c.rank)
                ax2.plot(
                    [coords[ia, 0], coords[ib, 0]],
                    [coords[ia, 1], coords[ib, 1]],
                    color="#555555", linewidth=1.6, alpha=alpha, zorder=2,
                )
                # Label major boundary
                if c.boundary_type == "major":
                    mx = (coords[ia, 0] + coords[ib, 0]) / 2
                    my = (coords[ia, 1] + coords[ib, 1]) / 2
                    ax2.annotate(
                        f"d={c.distance:.1f}",
                        xy=(mx, my), fontsize=11, fontweight="bold", color="#e05c00",
                        ha="center",
                        bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.85,
                                  ec="#e05c00", lw=1.5),
                        zorder=6,
                    )

        ax2.set_title("MDS Phase Map  (2-D metric projection of primitive distance space)",
                      fontsize=15, pad=12)
        _AXIS_LABELS = {
            "diagonal": ("MDS axis 1  (weighted Euclidean)", "MDS axis 2  (weighted Euclidean)"),
            "mahalanobis": (
                "MDS axis 1  [e₁: topological-criticality  Ω vs G+Φ]",
                "MDS axis 2  [e₂: criticality  Φ vs G+D]",
            ),
        }
        xlabel, ylabel = _AXIS_LABELS.get(self.metric, ("MDS axis 1", "MDS axis 2"))
        ax2.set_xlabel(xlabel, fontsize=11, labelpad=8)
        ax2.set_ylabel(ylabel, fontsize=11, labelpad=8)
        ax2.tick_params(axis="both", labelsize=12)
        ax2.grid(True, linestyle=":", linewidth=0.8, alpha=0.55)
        for spine in ax2.spines.values():
            spine.set_linewidth(1.4)

        # Legend
        legend_elements = [
            mpatches.Patch(color=_OMEGA_COLOR[TopoIndex.TRIVIAL],     label="Ω₀  TRIVIAL"),
            mpatches.Patch(color=_OMEGA_COLOR[TopoIndex.Z_CLASS],     label="Ω_Z  ℤ-class"),
            mpatches.Patch(color=_OMEGA_COLOR[TopoIndex.Z2_CLASS],    label="Ω_Z₂ ℤ₂-class"),
            mpatches.Patch(color=_OMEGA_COLOR[TopoIndex.NON_ABELIAN], label="Ω_NA non-Abelian"),
            Line2D([0], [0], marker="*", color="w", markerfacecolor="#555", markersize=18,
                   label="★ Factor-8 (quantum critical)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
                   markeredgecolor="#e08c00", markeredgewidth=3, markersize=16,
                   label="○ K_teshlig (MBL candidate)"),
        ]
        ax2.legend(handles=legend_elements, loc="lower right", fontsize=12,
                   framealpha=0.93, edgecolor="#bbbbbb", borderpad=0.9)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"[phase_diagram] saved → {save_path}")
        if show:
            try:
                plt.show()
            except Exception:
                pass   # headless environment — saved to file if save_path set
        plt.close(fig)


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

def _primitive_diff_labels(a: Imscription, b: Imscription) -> List[str]:
    """Return list of primitive names where a and b differ."""
    diffs = []
    checks = [
        ("D",  a.dimensionality,     b.dimensionality),
        ("T",  a.topology,           b.topology),
        ("R",  a.recognition_mode,   b.recognition_mode),
        ("P",  a.polarity,           b.polarity),
        ("F",  a.fidelity,           b.fidelity),
        ("K",  a.kinetic_character,  b.kinetic_character),
        ("G",  a.granularity,        b.granularity),
        ("Γ",  a.interaction_grammar,b.interaction_grammar),
        ("Φ",  a.criticality_phase,  b.criticality_phase),
        ("Ω",  a.topo_index,         b.topo_index),
    ]
    for label, va, vb in checks:
        if va != vb:
            diffs.append(label)
    return diffs


def _mds_2d(D: np.ndarray) -> np.ndarray:
    """
    Classic (metric) MDS: embed N points into 2-D from distance matrix D.
    Uses eigendecomposition of the double-centered Gram matrix.
    """
    n = D.shape[0]
    D2 = D ** 2
    H = np.eye(n) - np.ones((n, n)) / n   # centering matrix
    B = -0.5 * H @ D2 @ H
    eigenvalues, eigenvectors = np.linalg.eigh(B)
    # Take two largest eigenvalues (MDS keeps highest-variance dimensions)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    # Guard against numerical negatives
    eigenvalues[:2] = np.maximum(eigenvalues[:2], 0)
    coords = eigenvectors[:, :2] * np.sqrt(eigenvalues[:2])
    return coords


def build_phase_map(
    imscription_names: Optional[List[str]] = None,
    catalog: Optional[Any] = None,
    metric: str = "diagonal",
) -> PhaseDiagram:
    """
    Build a PhaseDiagram for the given imscription names.

    Args:
        imscription_names: list of catalog names; defaults to the eight quantum/topological
                       imscriptions registered by register_quantum_imscriptions().
        catalog: ImscriptionCatalog to use; defaults to global_catalog.

    Returns:
        PhaseDiagram instance with all computed fields.
    """
    if catalog is None:
        catalog = global_catalog

    _DEFAULT_QUANTUM = [
        "photon",
        "proton",
        "electron",
        "spin_singlet",
        "qubit_logical",
        "kitaev_chain_majorana",
        "fqh_moore_read",
        "topological_insulator_bi2se3",
    ]
    if imscription_names is None:
        imscription_names = [n for n in _DEFAULT_QUANTUM if n in catalog._imscriptions]

    imscriptions = [catalog._imscriptions[n] for n in imscription_names]
    n = len(imscriptions)

    # 1. Distance matrix
    use_mahalanobis = metric == "mahalanobis"
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if use_mahalanobis:
                d = mahalanobis_distance(imscriptions[i], imscriptions[j])
            else:
                d = tuple_distance(imscriptions[i], imscriptions[j])
            D[i, j] = D[j, i] = d

    # 2. Phase boundary candidates
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((D[i, j], i, j))
    pairs.sort(key=lambda x: -x[0])

    all_dists = [p[0] for p in pairs]
    d_max = all_dists[0] if all_dists else 1.0
    d_p33 = np.percentile(all_dists, 67) if all_dists else d_max * 0.5
    d_p66 = np.percentile(all_dists, 33) if all_dists else d_max * 0.25

    candidates = []
    for rank, (dist, i, j) in enumerate(pairs, start=1):
        if dist >= d_p33:
            btype = "major"
        elif dist >= d_p66:
            btype = "intermediate"
        else:
            btype = "minor"
        candidates.append(PhaseCandidate(
            name_a=imscription_names[i],
            name_b=imscription_names[j],
            distance=dist,
            rank=rank,
            boundary_type=btype,
            primitives_differ=_primitive_diff_labels(imscriptions[i], imscriptions[j]),
        ))

    # 3. Linkage (Ward on condensed distance matrix)
    from scipy.spatial.distance import squareform as sq
    condensed = sq(D)
    Z = linkage(condensed, method="ward")

    # 4. MDS
    mds = _mds_2d(D) if n >= 3 else None

    # 5. Per-imscription annotations
    f8_flags = [_is_factor8(s) for s in imscriptions]
    omega_vals = [s.topo_index for s in imscriptions]
    k_trap_flags = [s.kinetic_character == KineticCharacter.TRAP for s in imscriptions]

    return PhaseDiagram(
        imscription_names=imscription_names,
        distance_matrix=D,
        candidates=candidates,
        linkage_matrix=Z,
        mds_coords=mds,
        factor8_flags=f8_flags,
        omega_values=omega_vals,
        k_trap_flags=k_trap_flags,
        metric=metric,
    )
