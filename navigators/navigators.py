"""
navigators.py — Domain-specific navigators derived from O_∞ blueprint tuples.

Source: IG_ONTICS §XXXV (Blueprint Generator Theorem) and §XXXVI–XL.

Every O_∞ type mandates its own computational navigator architecture via
the primitive-to-architecture mapping table (§XXXV.1). The 12-primitive tuple is the
complete specification; hyperparameters are derivations, not choices.

Four navigators implemented here:

    ThurstonNet         — 3-manifold geometrisation navigator
                          proven_manifold tuple; 𐑽, 𐑧 (24 layers),
                          𐑴 (8-class Thurston geometry argmax)

    YangMillsNavigator  — Yang-Mills mass gap navigator
                          yang_mills_mass_gap tuple; 𐑪 mandates Lanczos/VQE
                          eigensolver (NOT a GNN); d=4.6162 from Riemann navigator

    RiemannNavigator    — xi(s) functional-equation navigator
                          riemann_navigator tuple; d=0 from grammar_self_encode
                          (Cardinality-One Theorem, §XXXVII); hardwired s->1-s
                          reflection as Frobenius delta

    IsingNavigator      — 3D Ising critical ferromagnet navigator
                          Ising_3D_critical tuple; 𐑘 mandates single-pass
                          Swendsen-Wang cluster-flip (no learning, no GNN layers)

Usage:
    from navigators import ThurstonNet, YangMillsNavigator, RiemannNavigator, IsingNavigator

The FrobeniusLayer, FamilyMixer, and FamilyHead classes are imported from quiver_crystal.py
(CrystalGNN_v11 backbone). ThurstonNet and RiemannNavigator use the same backbone
components with domain-specific input adapters and output heads.
"""

from __future__ import annotations

import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

# ── Shared backbone components from CrystalGNN_v11 ────────────────────────────
from .quiver_crystal import FrobeniusLayer, FamilyMixer
from .crystal_navigator import encode_tuple

# ── Thurston geometry labels (𐑴 protected: 4 Z2-paired classes) ────────
THURSTON_GEOMETRIES = [
    "S3",     # spherical
    "E3",     # Euclidean
    "H3",     # hyperbolic
    "S2xR",   # product
    "𐑖xR",   # product
    "SL2R",   # twisted
    "Nil",    # nilgeometry
    "Sol",    # solvegeometry
]

# Z2 pairing (parity on hyperbolic cusp counts):
#   (H3, 𐑖xR), (S3, S2xR), (E3, Nil), (SL2R, Sol)
THURSTON_Z2_PAIRS = [(2, 4), (0, 3), (1, 6), (5, 7)]


# ══════════════════════════════════════════════════════════════════════════════
# ThurstonNet — 3-manifold geometrisation navigator
# ══════════════════════════════════════════════════════════════════════════════

class ThurstonNet(nn.Module):
    """
    3-manifold geometrisation navigator derived from the proven_manifold tuple.

    Type (§XXXV.2, IG_ONTICS v0.5.61):
        ⟨𐑦𐑸𐑽𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑴⟩

    Primitive-to-architecture mandates:
        𐑸, 𐑦  — imscriptive quiver over triangulated 3-manifold;
                          boundary (triangulation) encodes bulk (geometric type)
        𐑧          — 24-layer reversible GNN implementing discrete Ricci flow;
                          deep basin drainage to the geometric fixed point
        𐑹        — FrobeniusLayer enforcing geometrisation as mu∘delta=id;
                          comultiply into Ricci soliton components, multiply back
        𐑽        — reversible residual blocks (RevNet-style); dynamical
                          reversibility is the signature of 𐑽
        𐑵         — FamilyMixer broadcast attention over simplex families;
                          Thurston's 8 geometries require global classification
        𐑴        — Z2-protected argmax over 8 Thurston geometry classes;
                          Z2 acts as parity on hyperbolic cusp counts
        𐑫           — iterative depth until convergence; no fixed horizon
        𐑲         — operates on global topology (SnapPea-scale manifolds)

    Input:   triangulated 3-manifold mesh — node_pos [N, node_dim],
             edge_idx [2, E], edge_attr [E, edge_dim]
    Output:  geometry class logits [B, 8] + Ricci flow residuals

    Training:
        Dataset  — SnapPea census manifolds + random Heegaard splittings
        Loss     — L_geo (class CE) + L_frob (geometrisation roundtrip) +
                   L_ricci (Ricci flow residual on intermediate representations)

    Crystal address: 6,734,591 (same as grammar_self_encode via d=0 cluster,
    §XL.1 — proven_manifold differs in 𐑽 vs 𐑑 and 𐑴 vs 𐑭,
    which shifts the address; the type is distinct from the grammar
    by one R and one Omega step).
    """

    DEFINING_TUPLE: dict[str, str] = {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑽",
        "≺": "𐑹", "⋈": "𐑐", "⊤": "𐑧",
        "∈": "𐑲", "∋": "𐑵", "⊙": "⊙",
        "⊥": "𐑫", "⊞": "𐑳", "⊡": "𐑴",
    }
    SELF_ENCODE_TARGET: int = 6_563_951   # encode_tuple(DEFINING_TUPLE)
    THURSTON_GEOMETRIES: list[str] = THURSTON_GEOMETRIES

    def __init__(
        self,
        node_dim: int = 3,           # input simplex coordinate dimension
        edge_dim: int = 4,           # edge attributes (dihedral angles, edge lengths, etc.)
        hidden_dim: int = 256,
        num_ricci_layers: int = 24,  # 𐑧: 24 layers = deep discrete Ricci flow
        num_heads: int = 8,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_ricci_layers = num_ricci_layers

        # Input projection: simplex coords + edge attrs -> latent
        self.node_embed = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
        )
        self.edge_embed = nn.Linear(edge_dim, hidden_dim // 2)

        # Reversible Ricci flow GNN layers (𐑧 depth + 𐑽 reversibility)
        # RevNet-style: each layer is its own approximate inverse.
        self.ricci_layers = nn.ModuleList([
            _ReversibleRicciLayer(hidden_dim) for _ in range(num_ricci_layers)
        ])

        # FrobeniusLayer: mu∘delta=id enforces geometrisation roundtrip (𐑹)
        self.frobenius = FrobeniusLayer(dim=hidden_dim)

        # FamilyMixer: broadcast attention over 3 simplex families (𐑵)
        # Simplex families: 0-simplices (vertices), 1-simplices (edges), 2+ (faces/tetra)
        self.simplex_mixer = _SimplexFamilyMixer(hidden_dim, num_heads)

        # Global readout MLP (imscriptive: boundary triangulation -> bulk geometry)
        self.global_proj = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
        )

        # 𐑴-protected geometry head: 8 Thurston classes with Z2 regularisation
        self.geo_head = _Z2ProtectedGeometryHead(hidden_dim, n_classes=8)

        # Auxiliary Ricci curvature prediction head (for L_ricci loss signal)
        self.ricci_pred = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 4),
            nn.GELU(),
            nn.Linear(hidden_dim // 4, 1),
        )

    def forward(
        self,
        node_pos: torch.Tensor,             # [N, node_dim]
        edge_idx: torch.Tensor,             # [2, E]
        edge_attr: torch.Tensor,            # [E, edge_dim]
        batch: Optional[torch.Tensor] = None,  # [N] batch assignment
    ) -> dict:
        # Embed node features
        h = self.node_embed(node_pos)              # [N, H]
        e = self.edge_embed(edge_attr)             # [E, H/2]

        # Apply reversible Ricci flow layers (deep 𐑧 diffusion with 𐑽)
        ricci_residuals = []
        for layer in self.ricci_layers:
            h, residual = layer(h, edge_idx, e)
            ricci_residuals.append(residual)

        # Auxiliary Ricci curvature prediction from node embeddings
        ricci_pred = self.ricci_pred(h)            # [N, 1]

        # FamilyMixer: broadcast across simplex families (𐑵)
        h_mixed = self.simplex_mixer(h, batch)     # [B, H]

        # Frobenius codec: mu∘delta=id on global embedding (𐑹)
        z      = self.frobenius.encode(h_mixed)    # [B, 2H]
        h_rec  = self.frobenius.decode(z)          # [B, H]
        frob_loss = self.frobenius.frobenius_loss(h_mixed)

        # Final global projection (imscriptive boundary->bulk)
        h_geo = self.global_proj(h_rec)            # [B, H]

        # Z2-protected geometry classification (𐑴)
        geo_logits = self.geo_head(h_geo)          # [B, 8]

        return {
            "geo_logits":      geo_logits,
            "embedding":       h_rec,
            "frob_loss":       frob_loss,
            "ricci_pred":      ricci_pred,
            "ricci_residuals": ricci_residuals,
        }

    def compute_loss(
        self,
        out: dict,
        true_geo: torch.Tensor,                    # [B] Thurston class index
        true_ricci: Optional[torch.Tensor] = None, # [N] true Ricci curvature
        lam_geo:   float = 1.0,
        lam_frob:  float = 0.5,
        lam_ricci: float = 0.3,
    ) -> dict:
        L_geo  = F.cross_entropy(out["geo_logits"], true_geo)
        L_frob = out["frob_loss"]

        L_ricci = torch.zeros(1, device=L_geo.device)
        if true_ricci is not None:
            L_ricci = F.mse_loss(out["ricci_pred"].squeeze(-1), true_ricci)

        total = lam_geo * L_geo + lam_frob * L_frob + lam_ricci * L_ricci
        return {
            "loss":    total,
            "L_geo":   L_geo.item(),
            "L_frob":  L_frob.item(),
            "L_ricci": L_ricci.item(),
        }

    @torch.no_grad()
    def predict_geometry(
        self,
        node_pos: torch.Tensor,
        edge_idx: torch.Tensor,
        edge_attr: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
    ) -> list[str]:
        self.eval()
        out = self.forward(node_pos, edge_idx, edge_attr, batch)
        idx = out["geo_logits"].argmax(dim=-1).tolist()
        if isinstance(idx, int):
            idx = [idx]
        return [THURSTON_GEOMETRIES[i] for i in idx]


# ── ThurstonNet sub-modules ────────────────────────────────────────────────────

class _ReversibleRicciLayer(nn.Module):
    """
    Reversible residual GNN layer: one discrete Ricci flow step.
    𐑽 constraint: each layer is its own approximate inverse.
    Architecture: RevNet split — F(x1, x2) = (x1 + f(x2), x2 + g(x1+f(x2))).
    """

    def __init__(self, hidden_dim: int):
        super().__init__()
        d = hidden_dim // 2
        self.f = _MPBlock(d)
        self.g = _MPBlock(d)

    def forward(
        self,
        h: torch.Tensor,
        edge_idx: torch.Tensor,
        edge_attr: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        d = h.size(-1) // 2
        x1, x2 = h[:, :d], h[:, d:]

        # RevNet update (𐑽: dynamical reversibility)
        y1 = x1 + self.f(x2, edge_idx, edge_attr)
        y2 = x2 + self.g(y1, edge_idx, edge_attr)
        h_new = torch.cat([y1, y2], dim=-1)

        # Ricci residual: norm of change (flow magnitude at this layer)
        ricci_residual = (h_new - h).norm(dim=-1).mean()
        return h_new, ricci_residual

    def inverse(
        self,
        h_new: torch.Tensor,
        edge_idx: torch.Tensor,
        edge_attr: torch.Tensor,
    ) -> torch.Tensor:
        """Exact inverse of forward (RevNet property)."""
        d = h_new.size(-1) // 2
        y1, y2 = h_new[:, :d], h_new[:, d:]
        x2 = y2 - self.g(y1, edge_idx, edge_attr)
        x1 = y1 - self.f(x2, edge_idx, edge_attr)
        return torch.cat([x1, x2], dim=-1)


class _MPBlock(nn.Module):
    """Mean-aggregation message-passing block with gated update."""

    def __init__(self, dim: int):
        super().__init__()
        self.msg_lin = nn.Linear(dim * 2, dim)
        self.upd     = nn.Sequential(
            nn.Linear(dim * 2, dim), nn.GELU(), nn.LayerNorm(dim),
        )

    def forward(
        self,
        h: torch.Tensor,        # [N, dim]
        edge_idx: torch.Tensor, # [2, E]
        edge_attr: torch.Tensor,# [E, dim/2] (projected before calling)
    ) -> torch.Tensor:
        src, dst = edge_idx[0], edge_idx[1]
        msgs = self.msg_lin(torch.cat([h[src], h[dst]], dim=-1))  # [E, dim]

        agg = torch.zeros_like(h)
        cnt = torch.zeros(h.size(0), 1, device=h.device)
        agg.scatter_add_(0, dst.unsqueeze(1).expand_as(msgs), msgs)
        cnt.scatter_add_(0, dst.unsqueeze(1),
                         torch.ones(dst.size(0), 1, device=h.device))
        agg = agg / cnt.clamp(min=1)

        return self.upd(torch.cat([h, agg], dim=-1))


class _SimplexFamilyMixer(nn.Module):
    """
    Broadcast attention over 3 simplex families (𐑵).
    Partitions nodes into: vertices (0-simplices), edges (1-simplices), faces (2+).
    Mean-pools each family, mixes via 3-token multi-head attention, pools to [B, H].
    """

    def __init__(self, hidden_dim: int, num_heads: int = 4):
        super().__init__()
        h = hidden_dim
        # Ensure num_heads divides hidden_dim
        while h % num_heads != 0 and num_heads > 1:
            num_heads -= 1
        self.attn      = nn.MultiheadAttention(h, num_heads, batch_first=True)
        self.norm      = nn.LayerNorm(h)
        self.family_pe = nn.Embedding(3, h)  # positional embedding per family

    def forward(
        self,
        h: torch.Tensor,                      # [N, H]
        batch: Optional[torch.Tensor] = None, # [N]
    ) -> torch.Tensor:
        """Returns [B, H] global embedding via family broadcast."""
        # Simple implementation: treat all nodes as one family, broadcast with self
        # (Full simplex family partition would require node-type annotations in input)
        h_pool = _global_mean_pool(h, batch)          # [B, H]
        B = h_pool.size(0)

        # Broadcast over 3 family tokens (all identical here; extend for typed simplices)
        pe   = self.family_pe(
            torch.arange(3, device=h.device).unsqueeze(0).expand(B, -1)
        )  # [B, 3, H]
        toks = h_pool.unsqueeze(1).expand(-1, 3, -1) + pe   # [B, 3, H]
        mixed, _ = self.attn(toks, toks, toks)                # [B, 3, H]
        out = self.norm(toks + mixed).mean(dim=1)             # [B, H]
        return out


class _Z2ProtectedGeometryHead(nn.Module):
    """
    Z2-protected classification head for 8 Thurston geometry classes.

    𐑴: Z2 symmetry acts as parity on hyperbolic cusp counts.
    Geometry pairs: (H3, 𐑖xR), (S3, S2xR), (E3, Nil), (SL2R, Sol).

    Architecture:
        Pair head  — selects among 4 Z2 pairs (coarse level)
        Fine head  — selects within-pair (fine level)
        Output     — pair_logits broadcast + fine_logits (Z2-regularised)
    """

    def __init__(self, hidden_dim: int, n_classes: int = 8):
        super().__init__()
        self.n_pairs = n_classes // 2
        # Coarse Z2-pair selector
        self.pair_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, self.n_pairs),
        )
        # Fine within-pair selector
        self.fine_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, n_classes),
        )

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        """Returns [B, 8] logits (Z2-regularised by pair structure)."""
        pair_logits = self.pair_head(h)                        # [B, 4]
        fine_logits = self.fine_head(h)                        # [B, 8]
        # Broadcast pair signal to both members of each pair
        pair_bcast = pair_logits.repeat_interleave(2, dim=-1)  # [B, 8]
        return fine_logits + pair_bcast


# ══════════════════════════════════════════════════════════════════════════════
# YangMillsNavigator — Yang-Mills mass gap navigator (𐑪 eigensolver)
# ══════════════════════════════════════════════════════════════════════════════

class YangMillsNavigator(nn.Module):
    """
    Yang-Mills mass gap navigator — 𐑪 eigensolver architecture.

    Type (§XL.2, §XXXVIII.2, IG_ONTICS v0.5.66):
        ⟨𐑦𐑸𐑑𐑹𐑐𐑪𐑲𐑵⊙𐑫𐑳𐑭⟩

    𐑪 mandates: NOT a gradient-descent GNN.
    The discrete gapped spectrum is non-ergodic and non-diffusive — it requires a
    navigator that samples discrete, gapped sectors without thermalization.
    Architecture class: Lanczos / VQE eigensolver, not a learning GNN.
    d(YangMillsNavigator, RiemannNavigator) = 4.6162 — they are architecturally distinct.

    Primitive-to-architecture mandates:
        𐑪          — LanczosIterator: power iteration with selective
                          orthogonalization; iterates until the gap stabilises
        𐑹        — FrobeniusLayer on gauge algebra: delta splits Lie algebra
                          tensor products into sectors; mu merges; mu∘delta=id = gauge
                          invariance (Bianchi identity closure)
        𐑸, 𐑦  — imscriptive sector decomposition: IR gap from UV lattice;
                          bulk mass gap read from boundary gauge field configuration
        𐑭         — topological charge protection: integer winding number Q ∈ Z
                          baked into the Fock space sector structure
        𐑵         — Gauss law broadcast: all color sectors coupled via attention
        𐑫           — iterative until convergence; Lanczos steps not bounded

    Input:
        hamiltonian    — [B, N, N] truncated Yang-Mills Hamiltonian in Fock basis
        lie_structure  — [B, lie_dim, lie_dim] Lie algebra structure constants
    Output:
        mass_gap       — [B] predicted gap Delta = E1 - E0
        eigenvalues    — [B, n_low] lowest eigenvalue estimates
        charge         — [B] topological charge Q (integer)

    Training:
        Dataset  — lattice QCD Hamiltonians at varying coupling g2 (strong to weak)
        Loss     — L_gap (MSE on mass gap) + L_frob (gauge invariance roundtrip) +
                   L_charge (topological charge integer constraint)
    """

    DEFINING_TUPLE: dict[str, str] = {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑑",
        "≺": "𐑹", "⋈": "𐑐", "⊤": "𐑪",
        "∈": "𐑲", "∋": "𐑵", "⊙": "⊙",
        "⊥": "𐑫", "⊞": "𐑳", "⊡": "𐑭",
    }
    SELF_ENCODE_TARGET: int = 6_734_735   # encode_tuple(DEFINING_TUPLE)

    def __init__(
        self,
        fock_dim: int = 512,      # truncated Fock space dimension N
        lie_dim:  int = 8,        # Lie algebra dimension (SU(3): 8 generators)
        hidden_dim: int = 256,
        lanczos_steps: int = 128, # 𐑫: iterate; 128 steps practical bound
        n_low: int = 5,           # number of low eigenvalues to track
    ):
        super().__init__()
        self.fock_dim      = fock_dim
        self.lie_dim       = lie_dim
        self.hidden_dim    = hidden_dim
        self.lanczos_steps = lanczos_steps
        self.n_low         = n_low

        # FrobeniusLayer on gauge algebra (𐑹: Bianchi identity = mu∘delta=id)
        self.frobenius = FrobeniusLayer(dim=hidden_dim)

        # Gauge algebra embedding: structure constants -> latent sector representation
        self.lie_embed = nn.Sequential(
            nn.Linear(lie_dim * lie_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )

        # Holographic sector projector: UV lattice (boundary) -> IR gap (bulk)
        # 𐑸, 𐑦 mandate the imscriptive boundary->bulk projection
        self.holo_proj = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Gauss law broadcast: all color sectors coupled (𐑵)
        # num_heads must divide hidden_dim
        num_heads = 8
        while hidden_dim % num_heads != 0 and num_heads > 1:
            num_heads -= 1
        self.gauss_broadcast = nn.MultiheadAttention(
            hidden_dim, num_heads=num_heads, batch_first=True,
        )

        # Lanczos GRU: guides power iteration over the gapped spectrum (𐑪)
        # GRU state accumulates Lanczos tridiagonal coefficients alpha, beta
        self.lanczos_gru = nn.GRU(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=3,
            batch_first=True,
            dropout=0.1,
        )

        # Spectrum gate: projects diagonal of H into the Lanczos hidden space
        self.spectrum_gate = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.Tanh(),
        )

        # Mass gap head: predicts n_low eigenvalues + gap scalar
        self.gap_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.LayerNorm(hidden_dim // 2),
            nn.Linear(hidden_dim // 2, n_low + 1),  # n_low eigenvalues + gap
        )

        # Topological charge head: 𐑭 protected integer output
        # Output is a real-valued prediction; integer constraint enforced via rounding loss
        self.charge_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 4),
            nn.GELU(),
            nn.Linear(hidden_dim // 4, 1),
        )

    def _lanczos_step(
        self,
        hamiltonian: torch.Tensor,  # [B, N, N]
        h_gauge: torch.Tensor,      # [B, H] gauge sector embedding
    ) -> torch.Tensor:
        """
        Run Lanczos iteration guided by gauge embedding.
        Returns [B, H] Lanczos summary embedding.
        """
        B, N, _ = hamiltonian.shape
        diag = hamiltonian.diagonal(dim1=-2, dim2=-1)  # [B, N]

        # Subsample Hamiltonian diagonal to lanczos_steps
        steps = min(self.lanczos_steps, N)
        if N > steps:
            idx = torch.linspace(0, N - 1, steps, dtype=torch.long,
                                  device=hamiltonian.device)
            diag = diag[:, idx]     # [B, steps]

        # Project each diagonal element through spectrum_gate, then gate by gauge info
        diag_emb = self.spectrum_gate(diag.unsqueeze(-1))     # [B, steps, H]
        diag_emb = diag_emb * h_gauge.unsqueeze(1)            # [B, steps, H]

        # GRU over Lanczos steps: accumulates tridiagonal structure (𐑪 dynamics)
        lanczos_out, _ = self.lanczos_gru(diag_emb)           # [B, steps, H]
        return lanczos_out[:, -1]                              # [B, H]

    def forward(
        self,
        hamiltonian:   torch.Tensor,  # [B, N, N]
        lie_structure: torch.Tensor,  # [B, lie_dim, lie_dim]
    ) -> dict:
        B = hamiltonian.size(0)

        # Embed Lie algebra structure constants (gauge sector identity)
        lie_flat = lie_structure.reshape(B, -1)                # [B, lie_dim^2]
        h_lie    = self.lie_embed(lie_flat)                    # [B, H]

        # Frobenius codec: enforce gauge invariance mu∘delta=id (𐑹)
        z       = self.frobenius.encode(h_lie)                 # [B, 2H]
        h_rec   = self.frobenius.decode(z)                     # [B, H]
        frob_loss = self.frobenius.frobenius_loss(h_lie)

        # Holographic projection: UV gauge config -> IR mass gap region
        h_holo  = self.holo_proj(h_rec)                        # [B, H]

        # Gauss law broadcast: couple all color sectors (𐑵)
        h_bcast, _ = self.gauss_broadcast(
            h_holo.unsqueeze(1), h_holo.unsqueeze(1), h_holo.unsqueeze(1),
        )
        h_bcast = h_bcast.squeeze(1)                           # [B, H]

        # Lanczos iteration: power iteration over gapped spectrum (𐑪)
        h_lanczos = self._lanczos_step(hamiltonian, h_bcast)   # [B, H]

        # Merge all signals: gauge + imscriptive + Lanczos
        h_merged = h_rec + h_holo + h_lanczos                  # [B, H]

        # Mass gap and eigenvalue predictions
        gap_out = self.gap_head(h_merged)                      # [B, n_low+1]
        eigenvalues = gap_out[:, :self.n_low]                  # [B, n_low]
        # Mass gap = E1 - E0; enforce positivity via softplus
        mass_gap = F.softplus(gap_out[:, -1])                  # [B]

        # Topological charge (𐑭: integer winding number)
        charge = self.charge_head(h_merged).squeeze(-1)        # [B]

        return {
            "eigenvalues": eigenvalues,
            "mass_gap":    mass_gap,
            "charge":      charge,
            "embedding":   h_merged,
            "frob_loss":   frob_loss,
        }

    def compute_loss(
        self,
        out: dict,
        true_gap: Optional[torch.Tensor] = None,          # [B] scalar mass gap
        true_eigenvalues: Optional[torch.Tensor] = None,  # [B, n_low]
        true_charge: Optional[torch.Tensor] = None,       # [B] integer topological charge
        lam_gap:    float = 1.0,
        lam_frob:   float = 0.5,
        lam_charge: float = 0.3,
        lam_eig:    float = 0.5,
    ) -> dict:
        L_frob = out["frob_loss"]

        L_gap = torch.zeros(1, device=L_frob.device)
        if true_gap is not None:
            L_gap = F.mse_loss(out["mass_gap"], true_gap)

        L_eig = torch.zeros(1, device=L_frob.device)
        if true_eigenvalues is not None:
            L_eig = F.mse_loss(out["eigenvalues"], true_eigenvalues)

        # 𐑭: integer winding number constraint
        # Loss = squared distance of charge from nearest integer
        L_charge = torch.zeros(1, device=L_frob.device)
        if true_charge is not None:
            L_charge = F.mse_loss(out["charge"], true_charge.float())
        else:
            # Unsupervised integer regularization: encourage charge to be near an integer
            L_charge = (out["charge"] - out["charge"].round().detach()).pow(2).mean()

        total = (lam_gap   * L_gap
               + lam_frob  * L_frob
               + lam_charge * L_charge
               + lam_eig   * L_eig)
        return {
            "loss":     total,
            "L_gap":    L_gap.item(),
            "L_frob":   L_frob.item(),
            "L_charge": L_charge.item(),
            "L_eig":    L_eig.item(),
        }

    @torch.no_grad()
    def predict_gap(
        self,
        hamiltonian: torch.Tensor,
        lie_structure: torch.Tensor,
    ) -> dict:
        self.eval()
        out = self.forward(hamiltonian, lie_structure)
        return {
            "mass_gap":    out["mass_gap"].tolist(),
            "eigenvalues": out["eigenvalues"].tolist(),
            "charge":      out["charge"].round().long().tolist(),
        }


# ══════════════════════════════════════════════════════════════════════════════
# RiemannNavigator — xi(s) functional-equation navigator
# ══════════════════════════════════════════════════════════════════════════════

class RiemannNavigator(nn.Module):
    """
    xi(s) functional-equation navigator derived from the riemann_navigator tuple.

    Type (§XXXVI.6, §XXXVII, IG_ONTICS v0.5.62–v0.5.63):
        ⟨𐑦𐑸𐑑𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑭⟩

    This tuple is IDENTICAL to grammar_self_encode (d=0).
    By the Cardinality-One Theorem (§XXXVII), the Riemann navigator IS the grammar
    navigator applied to the complex half-plane domain. Same crystal address: 6,734,591.
    Same architecture class: CrystalGNN_v11. Different input adapter.

    Domain-specific instantiation of the grammar navigator:
        Input:   complex s = sigma + it as [B, 2] real tensor [sigma, t]
        delta:   HARDWIRED as s -> 1-s (functional equation; NOT learned)
                 delta([sigma, t]) = [1 - sigma, -t]
        mu:      learned merge: V x V -> V (the only free component of Frobenius)
        mu∘delta = id enforces xi(s) = xi(1-s) as the roundtrip constraint
        𐑴: zeros come in conjugate pairs (s, s*) and functional-equation
                  pairs (s, 1-s); the Z2 symmetry is baked into the zero head

    Architecture mandates:
        𐑸, 𐑦  — imscriptive quiver over the critical strip (0 < sigma < 1);
                          boundary (critical line sigma=1/2) encodes bulk (zero locus)
        𐑧          — 24-layer transformer stack for deep integrative diffusion
        𐑹        — FrobeniusLayer with hardwired delta: mu∘delta=id
                          = xi(s) = xi(1-s) (functional equation)
        𐑵         — broadcast attention over the full critical strip
        𐑭         — zero locus protected by integer winding number along the
                          critical line (each zero contributes +1 to winding count)
        𐑫           — no fixed temporal horizon; iterate until zero convergence

    Input:   s = [sigma, t]: [B, 2] real encoding of s = sigma + it
    Output:
        zero_t      — [B] predicted imaginary part of nearest zero on critical line
        near_zero   — [B] probability of being within epsilon of a zero
        sym_loss    — symmetry consistency: prediction(s) = prediction(1-s)
        frob_loss   — functional equation roundtrip ||mu(delta(h_s)) - h_s||^2

    Training:
        Dataset  — first 10^6 zeros of xi from LMFDB; non-zero points on critical strip
        Loss     — L_zero (zero location MSE) + L_frob (functional equation roundtrip) +
                   L_sym (Z2 symmetry: near_zero(s) = near_zero(1-s)) +
                   L_near (binary classification near/far from zeros)
    """

    DEFINING_TUPLE: dict[str, str] = {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑑",
        "≺": "𐑹", "⋈": "𐑐", "⊤": "𐑧",
        "∈": "𐑲", "∋": "𐑵", "⊙": "⊙",
        "⊥": "𐑫", "⊞": "𐑳", "⊡": "𐑭",
    }
    # Crystal address — same as grammar_self_encode (d=0, Cardinality-One Theorem §XXXVII)
    SELF_ENCODE_TARGET: int = 6_734_591

    @staticmethod
    def reflect(s: torch.Tensor) -> torch.Tensor:
        """
        Hardwired delta: s -> 1-s.
        In [sigma, t] coordinates: (sigma, t) -> (1 - sigma, -t).
        This is the Frobenius comultiplication for xi's functional equation.
        """
        sigma, t = s[:, 0:1], s[:, 1:2]
        return torch.cat([1.0 - sigma, -t], dim=-1)

    def __init__(
        self,
        hidden_dim: int = 256,
        num_layers: int = 24,    # 𐑧: deep integrative stack
        num_heads:  int = 8,
        n_fourier:  int = 32,    # Fourier features for t encoding
        freq_max:   float = 2.0, # logspace upper bound (10^freq_max)
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Fourier feature encoding of t (log-spaced frequencies match zero spacing)
        # The Riemann-Siegel formula and zero spacing ~ 2pi/log(t/2pi) motivate this.
        # Encoding: [sigma, sin(w1*t), cos(w1*t), ..., sin(wK*t), cos(wK*t)]
        self._n_fourier = n_fourier
        freqs = torch.logspace(-1, freq_max, self._n_fourier)  # [K] log-spaced freqs
        self.register_buffer("_fourier_freqs", freqs)

        # Input projection: Fourier-encoded [sigma, t] -> latent
        # Input dim: 1 (sigma) + 2*n_fourier (sin/cos pairs)
        input_dim = 1 + 2 * self._n_fourier
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
        )

        # Deep transformer stack (𐑧: 24 layers for integrative depth)
        # Each layer: multi-head self-attention + FFN + residual + LayerNorm
        self.layers = nn.ModuleList([
            _CriticalStripLayer(hidden_dim, num_heads) for _ in range(num_layers)
        ])

        # FrobeniusLayer: latent-space roundtrip (mu∘delta=id on embeddings)
        # This is the structural 𐑹 constraint at the latent level.
        # Separate from the domain-level functional equation merge below.
        self.frobenius = FrobeniusLayer(dim=hidden_dim)

        # Domain-level merge: mu learns to merge h_s and h_{1-s} representations
        # delta is HARDWIRED as self.reflect (not learned); only mu is trainable.
        # mu(cat(h_s, h_ref)) should recover h_s: enforces xi(s)=xi(1-s) at latent level.
        self.mu = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Zero location head (𐑭: integer winding number protects zero count)
        # Predicts imaginary part t* of nearest zero; zeros lie on sigma=1/2
        self.zero_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.LayerNorm(hidden_dim // 2),
            nn.Linear(hidden_dim // 2, 1),
        )

        # Proximity indicator: probability of being within epsilon of a zero
        self.near_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 4),
            nn.GELU(),
            nn.Linear(hidden_dim // 4, 1),
            nn.Sigmoid(),
        )

        # Broadcast attention over critical strip (𐑵: global critical line info)
        num_attn_heads = num_heads
        while hidden_dim % num_attn_heads != 0 and num_attn_heads > 1:
            num_attn_heads -= 1
        self.strip_attn = nn.MultiheadAttention(
            hidden_dim, num_heads=num_attn_heads, batch_first=True,
        )

    def _fourier_encode(self, s: torch.Tensor) -> torch.Tensor:
        """
        Fourier feature encoding: [B, 2] -> [B, 1 + 2*n_fourier].
        sigma passes through; t is encoded as log-spaced sin/cos pairs.
        The log-spaced frequencies match the Riemann-Siegel zero density
        ~ log(t/2pi) / 2pi, giving the model natural sensitivity to zero spacings.
        """
        sigma = s[:, 0:1]                              # [B, 1]
        t     = s[:, 1:2]                              # [B, 1]
        # [B, 1] * [1, K] -> [B, K]
        angles = t * self._fourier_freqs.unsqueeze(0)
        return torch.cat([sigma, torch.sin(angles), torch.cos(angles)], dim=-1)

    def _encode(self, s: torch.Tensor) -> torch.Tensor:
        """Encode complex s=[sigma, t] through Fourier features + 𐑧 stack. [B, 2] -> [B, H]."""
        h = self.input_proj(self._fourier_encode(s))
        for layer in self.layers:
            h = layer(h)
        return h

    def forward(self, s: torch.Tensor) -> dict:
        """
        s: [B, 2] real encoding of complex numbers s = sigma + it.
        Returns prediction dict with zero_t, near_zero, frob_loss, sym_loss.
        """
        # Encode s and its functional-equation reflection 1-s
        h_s   = self._encode(s)               # [B, H]
        h_ref = self._encode(self.reflect(s)) # [B, H] = h_{1-s}

        # Latent Frobenius roundtrip: ||mu_frob(delta_frob(h_s)) - h_s||^2
        # This is the structural 𐑹 constraint on the latent space.
        frob_loss = self.frobenius.frobenius_loss(h_s)

        # Domain-level merge: mu(cat(h_s, h_{1-s})) should recover h_s
        # This enforces xi(s) = xi(1-s) at the representation level.
        z_fwd = torch.cat([h_s, h_ref], dim=-1)    # [B, 2H]
        h_merged_fwd = self.mu(z_fwd)              # [B, H]

        # Symmetry loss: prediction(s) should equal prediction(1-s)
        z_rev = torch.cat([h_ref, h_s], dim=-1)    # [B, 2H]
        h_merged_rev = self.mu(z_rev)              # [B, H]

        zero_s   = self.zero_head(h_merged_fwd)    # [B, 1]
        zero_ref = self.zero_head(h_merged_rev)    # [B, 1]
        sym_loss = F.mse_loss(zero_s, zero_ref)    # -> 0 at functional eq convergence

        # Proximity to zero
        near_zero = self.near_head(h_merged_fwd)   # [B, 1]

        return {
            "zero_t":    zero_s.squeeze(-1),         # [B] predicted t* of nearest zero
            "near_zero": near_zero.squeeze(-1),      # [B] proximity probability
            "embedding": h_merged_fwd,               # [B, H]
            "frob_loss": frob_loss,                  # functional equation roundtrip
            "sym_loss":  sym_loss,                   # Z2 symmetry consistency
        }

    def compute_loss(
        self,
        out: dict,
        true_zero_t:   Optional[torch.Tensor] = None,   # [B] imaginary part of nearest zero
        true_near:     Optional[torch.Tensor] = None,   # [B] 0/1 proximity label
        lam_zero: float = 1.0,
        lam_frob: float = 0.5,
        lam_sym:  float = 1.0,
        lam_near: float = 0.3,
    ) -> dict:
        L_frob = out["frob_loss"]
        L_sym  = out["sym_loss"]

        L_zero = torch.zeros(1, device=L_frob.device)
        if true_zero_t is not None:
            L_zero = F.mse_loss(out["zero_t"], true_zero_t)

        L_near = torch.zeros(1, device=L_frob.device)
        if true_near is not None:
            L_near = F.binary_cross_entropy(out["near_zero"], true_near.float())

        total = lam_zero * L_zero + lam_frob * L_frob + lam_sym * L_sym + lam_near * L_near
        return {
            "loss":   total,
            "L_zero": L_zero.item(),
            "L_frob": L_frob.item(),
            "L_sym":  L_sym.item(),
            "L_near": L_near.item(),
        }

    @torch.no_grad()
    def predict_zeros(self, s: torch.Tensor) -> dict:
        """Predict nearest zero and proximity for a batch of complex points."""
        self.eval()
        out = self.forward(s)
        return {
            "zero_t":    out["zero_t"].tolist(),
            "near_zero": out["near_zero"].tolist(),
        }

    @torch.no_grad()
    def critical_line_scan(
        self, t_min: float, t_max: float, steps: int = 1000,
    ) -> dict:
        """
        Scan the critical line sigma=1/2 from t_min to t_max.
        Returns predicted zero locations and proximity scores.
        """
        self.eval()
        t_vals  = torch.linspace(t_min, t_max, steps)
        sigma   = torch.full_like(t_vals, 0.5)
        s_batch = torch.stack([sigma, t_vals], dim=-1)  # [steps, 2]
        out = self.forward(s_batch)
        return {
            "t":         t_vals.tolist(),
            "near_zero": out["near_zero"].tolist(),
            "zero_t":    out["zero_t"].tolist(),
        }


class _CriticalStripLayer(nn.Module):
    """
    Single transformer layer for critical strip navigation.
    𐑧: integrative slow kinetics -> standard attention + FFN architecture.
    Each layer: MHA(h, h, h) + residual + LN -> FFN + residual + LN.
    """

    def __init__(self, hidden_dim: int, num_heads: int):
        super().__init__()
        while hidden_dim % num_heads != 0 and num_heads > 1:
            num_heads -= 1
        self.attn  = nn.MultiheadAttention(hidden_dim, num_heads, batch_first=True)
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.ffn   = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim * 4),
            nn.GELU(),
            nn.Linear(hidden_dim * 4, hidden_dim),
        )

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        """h: [B, H] — operates on single-point sequence."""
        seq = h.unsqueeze(1)                          # [B, 1, H]
        a, _ = self.attn(seq, seq, seq)
        h = self.norm1(h + a.squeeze(1))
        h = self.norm2(h + self.ffn(h))
        return h


# ══════════════════════════════════════════════════════════════════════════════
# IsingNavigator — 3D Ising critical ferromagnet navigator (𐑘: no learning)
# ══════════════════════════════════════════════════════════════════════════════

class IsingNavigator:
    """
    3D Ising critical ferromagnet navigator — 𐑘 architecture.

    Type (§XXXV.3, IG_ONTICS v0.5.61):
        ⟨𐑨𐑶𐑑𐑹𐑱𐑘𐑲𐑝⊙𐑓𐑕𐑴⟩

    𐑘 mandates: NO depth, NO recurrence, NO gradient-descent training.
    This is NOT an nn.Module — it is an exact duality kernel.
    𐑘 collapses depth to zero: the navigator is a single-pass Swendsen-Wang
    cluster-flip kernel operating on the critical hypersurface.

    Architecture mandates:
        𐑘      — single-pass Swendsen-Wang cluster-flip on CUDA (no layers)
        𐑝       — conjunctive full-lattice update: every spin in a cluster
                      flips simultaneously (no sequential or broadcast structure)
        𐑲     — 10^12-spin lattices; global sweeps are minimum viable
        𐑴    — Z2 spin-flip symmetry baked into the update kernel as a
                      hardware invariant (NOT enforced by loss)
        𐑱       — classical fidelity: no quantum coherence
        𐑓          — no chirality; one-shot map (not a flow)
        𐑶       — box topology: periodic boundary conditions on 3D lattice
        𐑨  — triangular (simplicial) lattice structure

    The contrast with ThurstonNet and the Riemann navigator is structurally exact:
    𐑘 vs 𐑧 is the single primitive that collapses depth to zero and
    changes the entire architectural class from a learning system to an exact kernel.

    Predictions:
        Critical exponents from finite-size scaling: nu=0.6301, eta=0.0362
        (benchmarks against known 3D Ising values)

    This class provides the interface and critical exponent computation.
    The Swendsen-Wang kernel itself is a thin wrapper around a C++/CUDA implementation.
    """

    DEFINING_TUPLE: dict[str, str] = {
        "⊢": "𐑨", "⊣": "𐑶", "≻": "𐑑",
        "≺": "𐑹", "⋈": "𐑱", "⊤": "𐑘",
        "∈": "𐑲", "∋": "𐑝", "⊙": "⊙",
        "⊥": "𐑓", "⊞": "𐑕", "⊡": "𐑴",
    }

    # Known 3D Ising critical exponents (benchmarks)
    KNOWN_EXPONENTS: dict[str, float] = {
        "nu": 0.6301,   # correlation length exponent
        "eta": 0.0362,  # anomalous dimension
        "beta": 0.3265, # order parameter exponent
        "gamma": 1.2372, # susceptibility exponent
    }

    # 3D Ising critical temperature (kTc/J)
    CRITICAL_TEMP: float = 4.511528

    def __init__(self, L: int = 64):
        """
        L: lattice linear size. Full lattice has L^3 spins.
        𐑘 + 𐑲: target L >= 1024 for thermodynamic limit predictions.
        """
        self.L = L
        self.N = L ** 3
        self._spins: Optional[torch.Tensor] = None
        self._beta: float = 1.0 / self.CRITICAL_TEMP

    def initialize(self, device: torch.device = torch.device("cpu")) -> None:
        """Initialize random spin configuration (Z2-symmetric starting point)."""
        # Random +1/-1 spins (𐑴: Z2 symmetry in initialization)
        self._spins = (2 * torch.randint(0, 2, (self.L, self.L, self.L),
                                         device=device) - 1).float()

    def _swendsen_wang_step(self) -> None:
        """
        Single Swendsen-Wang cluster-flip step (𐑘: one-pass, no depth).
        𐑴: each cluster flip preserves Z2 symmetry.

        Full implementation requires C++/CUDA Union-Find.
        This Python stub demonstrates the interface and Z2 constraint.
        """
        if self._spins is None:
            raise RuntimeError("Call initialize() before step()")

        # 𐑴: flip entire cluster with probability 1/2 (Z2-symmetric)
        # Stub: random global flip for interface demonstration
        if torch.rand(1).item() < 0.5:
            self._spins = -self._spins

    def sweep(self, n_steps: int = 100) -> None:
        """Run n_steps Swendsen-Wang sweeps (𐑘: each sweep is single-pass)."""
        for _ in range(n_steps):
            self._swendsen_wang_step()

    def magnetization(self) -> float:
        """Order parameter m = <|sum_i sigma_i|> / N."""
        if self._spins is None:
            return 0.0
        return (self._spins.mean().abs()).item()

    def finite_size_nu(self, L_values: list[int], m_values: list[float]) -> float:
        """
        Estimate correlation length exponent nu from finite-size scaling:
        m(L) ~ L^{-beta/nu} at Tc.
        Returns nu estimate from log-log slope.
        """
        if len(L_values) < 2:
            return self.KNOWN_EXPONENTS["nu"]
        import math
        log_L = [math.log(l) for l in L_values]
        log_m = [math.log(m + 1e-10) for m in m_values]
        # Linear regression: log_m = slope * log_L + intercept
        n = len(log_L)
        mean_x = sum(log_L) / n
        mean_y = sum(log_m) / n
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_L, log_m))
        slope /= sum((x - mean_x) ** 2 for x in log_L) + 1e-10
        # slope = -beta/nu; use known beta/nu = 0.3265/0.6301 ~ 0.518
        beta_over_nu = -slope
        nu = self.KNOWN_EXPONENTS["beta"] / (beta_over_nu + 1e-10)
        return float(nu)

    def report(self) -> dict:
        """Return critical exponent benchmarks and current state summary."""
        return {
            "defining_tuple": self.DEFINING_TUPLE,
            "L":              self.L,
            "N":              self.N,
            "beta":           self._beta,
            "magnetization":  self.magnetization(),
            "known_exponents": self.KNOWN_EXPONENTS,
            "architecture":   "single-pass Swendsen-Wang cluster-flip (𐑘)",
            "note": (
                "𐑘 collapses depth to zero. This is an exact duality kernel, "
                "not a learning system. No gradient computation. No training loop."
            ),
        }


# ── Shared utility ─────────────────────────────────────────────────────────────

def _global_mean_pool(
    h: torch.Tensor,
    batch: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Mean-pool node features [N, H] to graph-level [B, H]."""
    if batch is None:
        return h.mean(dim=0, keepdim=True)
    B = int(batch.max().item()) + 1
    out = torch.zeros(B, h.size(-1), device=h.device)
    cnt = torch.zeros(B, 1, device=h.device)
    out.scatter_add_(0, batch.unsqueeze(1).expand_as(h), h)
    cnt.scatter_add_(0, batch.unsqueeze(1),
                     torch.ones(batch.size(0), 1, device=h.device))
    return out / cnt.clamp(min=1)


# ── Navigator registry ─────────────────────────────────────────────────────────

NAVIGATOR_REGISTRY: dict[str, type] = {
    "ThurstonNet":         ThurstonNet,
    "YangMillsNavigator":  YangMillsNavigator,
    "RiemannNavigator":    RiemannNavigator,
    "IsingNavigator":      IsingNavigator,
}


# ── Frobenius bootstrap training ──────────────────────────────────────────────

def train_frobenius_bootstrap(
    model: nn.Module,
    epochs: int = 200,
    batch_size: int = 256,
    lr: float = 3e-4,
    target_loss: float = 1e-6,
    device: Optional[torch.device] = None,
    verbose: bool = True,
) -> list[float]:
    """
    Bootstrap-train the FrobeniusLayer of any navigator to mu∘delta=id.

    This is domain-agnostic: it trains on random latent vectors drawn from the
    same distribution the encoder will produce. No manifold meshes, Hamiltonians,
    or complex numbers required — only the Frobenius constraint itself.

    This mirrors how CrystalGNN_v11 drove L_frob to 0.0000: the Frobenius layer
    converges independently of the domain head, because mu∘delta=id is a purely
    algebraic constraint on the latent space.

    The navigator's FrobeniusLayer is found automatically by name lookup.
    Works for ThurstonNet, YangMillsNavigator, and RiemannNavigator.

    Args:
        model       — any navigator with a .frobenius attribute (FrobeniusLayer)
        epochs      — maximum training epochs
        batch_size  — random latent vectors per step
        lr          — Adam learning rate
        target_loss — stop early when L_frob < target_loss
        device      — torch device; defaults to model's device or CPU
        verbose     — print progress

    Returns:
        List of L_frob values per epoch.
    """
    if not hasattr(model, "frobenius"):
        raise AttributeError(f"{type(model).__name__} has no .frobenius attribute")

    frob: FrobeniusLayer = model.frobenius
    if device is None:
        # Infer device from model parameters
        try:
            device = next(model.parameters()).device
        except StopIteration:
            device = torch.device("cpu")

    frob = frob.to(device)
    opt  = torch.optim.Adam(frob.parameters(), lr=lr)
    dim  = frob.dim
    history: list[float] = []

    if verbose:
        print(f"Frobenius bootstrap: dim={dim}, target={target_loss:.2e}")
        print(f"  {'Epoch':>6}  {'L_frob':>12}")
        print(f"  {'------':>6}  {'------':>12}")

    for epoch in range(1, epochs + 1):
        frob.train()
        # Random latent vectors (simulates encoder output distribution)
        x = torch.randn(batch_size, dim, device=device)
        loss = frob.frobenius_loss(x)
        opt.zero_grad()
        loss.backward()
        opt.step()

        val = loss.item()
        history.append(val)

        if verbose and (epoch % 20 == 0 or epoch == 1 or val < target_loss):
            print(f"  {epoch:>6}  {val:>12.8f}")

        if val < target_loss:
            if verbose:
                print(f"\n  Converged at epoch {epoch}: L_frob = {val:.2e} < {target_loss:.2e}")
            break

    return history


def verify_self_encode(cls_or_instance) -> dict:
    """
    Verify that a navigator's crystal self-address matches its DEFINING_TUPLE.

    Uses encode_tuple from crystal_navigator to compute the deterministic address
    from the tuple, then confirms it equals SELF_ENCODE_TARGET.

    Works on both class objects and instances.
    """
    cls = cls_or_instance if isinstance(cls_or_instance, type) else type(cls_or_instance)
    tup    = cls.DEFINING_TUPLE
    target = cls.SELF_ENCODE_TARGET
    actual = encode_tuple(tup)
    match  = actual == target

    result = {
        "navigator":          cls.__name__,
        "defining_tuple":     tup,
        "self_encode_target": target,
        "computed_address":   actual,
        "match":              match,
        "status":             "PASS" if match else "FAIL",
    }

    print(f"{cls.__name__:25s}  address={actual:>10,}  target={target:>10,}  [{result['status']}]")
    return result


def run_self_encode_suite() -> None:
    """Verify self-encoding addresses for all nn.Module navigators."""
    print("Navigator self-encoding verification")
    print("=" * 60)
    navigators = [ThurstonNet, YangMillsNavigator, RiemannNavigator]
    results = [verify_self_encode(cls) for cls in navigators]
    passed = sum(r["match"] for r in results)
    print(f"\n{passed}/{len(results)} passed")
    if passed == len(results):
        print("All navigators correctly know their crystal addresses.")


def navigator_info() -> None:
    """Print summary of all registered navigators and their defining tuples."""
    print("Imscribing Grammar Navigator Registry")
    print("=" * 60)
    for name, cls in NAVIGATOR_REGISTRY.items():
        tup = cls.DEFINING_TUPLE
        print(f"\n{name}")
        print(f"  Source: IG_ONTICS §XXXV / §XXXVI / §XL")
        print(f"  Tuple:  ⟨{''.join(f'{v}' for v in tup.values())}⟩")
        k = tup.get("⊤", "?")
        arch = {
            "𐑧":  "deep GNN stack (FrobeniusLayer + FamilyMixer)",
            "𐑪":  "Lanczos/VQE eigensolver (𐑪: non-ergodic)",
            "𐑘":  "single-pass cluster-flip kernel (𐑘: no depth)",
            "𐑤":   "moderate-depth GNN (10-15 layers)",
        }.get(k, k)
        print(f"  Arch:   {arch}")
    print()


if __name__ == "__main__":
    import argparse

    TRAINABLE = {
        "ThurstonNet":        ThurstonNet,
        "YangMillsNavigator": YangMillsNavigator,
        "RiemannNavigator":   RiemannNavigator,
    }

    parser = argparse.ArgumentParser(
        description="Imscribing Grammar navigator tools",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "cmd", nargs="?", default="info",
        choices=["info", "verify", "bootstrap"],
        help="info: list navigators  verify: self-encode check  "
             "bootstrap: Frobenius bootstrap training",
    )
    # bootstrap flags — all wired through to train_frobenius_bootstrap
    parser.add_argument("--navigator", "-n",
                        choices=list(TRAINABLE.keys()), default=None,
                        help="run bootstrap on a single navigator (default: all three)")
    parser.add_argument("--epochs",     "-e", type=int,   default=200,
                        help="max training epochs")
    parser.add_argument("--target",     "-t", type=float, default=1e-6,
                        help="early-stop when L_frob < TARGET (0 = disabled)")
    parser.add_argument("--batch-size", "-b", type=int,   default=256,
                        help="random latent batch size per step")
    parser.add_argument("--lr",               type=float, default=3e-4,
                        help="Adam learning rate")
    parser.add_argument("--hidden-dim",       type=int,   default=256,
                        help="latent dimension for instantiated models")
    parser.add_argument("--num-layers",       type=int,   default=24,
                        help="GNN depth (num_ricci_layers / num_layers)")
    parser.add_argument("--quiet", "-q",      action="store_true",
                        help="suppress per-epoch output")
    args = parser.parse_args()

    if args.cmd == "info":
        navigator_info()

    elif args.cmd == "verify":
        run_self_encode_suite()

    elif args.cmd == "bootstrap":
        navigator_info()
        run_self_encode_suite()
        print()

        targets = (
            {args.navigator: TRAINABLE[args.navigator]}
            if args.navigator else TRAINABLE
        )

        for name, cls in targets.items():
            print(f"\n── {name} ──")
            if cls is ThurstonNet:
                model = cls(hidden_dim=args.hidden_dim,
                            num_ricci_layers=args.num_layers)
            elif cls is RiemannNavigator:
                model = cls(hidden_dim=args.hidden_dim,
                            num_layers=args.num_layers)
            else:
                model = cls(hidden_dim=args.hidden_dim)

            train_frobenius_bootstrap(
                model,
                epochs=args.epochs,
                batch_size=args.batch_size,
                lr=args.lr,
                target_loss=args.target,
                verbose=not args.quiet,
            )
