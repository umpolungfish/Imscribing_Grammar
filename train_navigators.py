"""
train_navigators.py — Training loops for the three O_inf navigators.

Each section is self-contained and generates its own synthetic / ground-truth data.
Run a specific navigator with:

    python train_navigators.py riemann    [--epochs N] [--lr F] [--hidden-dim N]
    python train_navigators.py yangmills  [--epochs N] [--lr F] [--hidden-dim N]
    python train_navigators.py thurston   [--epochs N] [--lr F] [--hidden-dim N]
    python train_navigators.py all        (runs all three sequentially)

Riemann:    trains on the first 100 known zeros of xi(s) (critical line sigma=1/2)
            → near_zero probability + zero_t prediction
            → scans critical line t ∈ [10, 60] after training

YangMills:  trains on random SU(2) Hamiltonians with planted mass gaps
            → mass_gap MSE + topological charge integer constraint

ThurstonNet: trains on synthetic simplicial complexes with planted Thurston geometry labels
             → 8-class geometry classification
"""

from __future__ import annotations

import argparse
import math
import random

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from navigators import (
    ThurstonNet,
    YangMillsNavigator,
    RiemannNavigator,
    train_frobenius_bootstrap,
    THURSTON_GEOMETRIES,
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Riemann zeros (first 100 non-trivial zeros of zeta on critical line) ────────
# Source: standard tables; imaginary parts t where zeta(1/2 + it) = 0
RIEMANN_ZEROS_T = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446247, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
    79.337375, 82.910381, 84.735493, 87.425274, 88.809111,
    92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    103.725538, 105.446623, 107.168611, 111.029535, 111.874659,
    114.320220, 116.226680, 118.790782, 121.370125, 122.946829,
    124.256819, 127.516683, 129.578704, 131.087688, 133.497737,
    134.756510, 138.116042, 139.736208, 141.123707, 143.111845,
    146.000982, 147.422765, 150.053521, 150.925257, 153.024693,
    156.112909, 157.597591, 158.849988, 161.188964, 163.030709,
    165.537069, 167.184439, 169.094515, 169.911976, 173.411536,
    174.754191, 176.441434, 178.377407, 179.916484, 182.207078,
    184.874467, 185.598783, 187.228922, 189.416159, 192.026656,
    193.079726, 195.265396, 196.876481, 198.015309, 201.264751,
    202.493594, 204.189671, 205.394697, 207.906258, 209.576509,
    211.690862, 213.347919, 214.547044, 216.169538, 219.067596,
    220.714918, 221.430705, 224.007000, 224.983324, 227.421444,
    229.337413, 231.250188, 232.498503, 233.693404, 236.524229,
]


# ══════════════════════════════════════════════════════════════════════════════
# Riemann navigator training
# ══════════════════════════════════════════════════════════════════════════════

ZERO_T_SCALE = 250.0   # normalise zero_t targets to [0, 1] to balance L_zero vs L_near


def make_riemann_batch(
    zeros_t: list[float],
    batch_size: int = 64,
    t_range: tuple[float, float] = (10.0, 250.0),
    eps: float = 0.5,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Build a batch of (s, near_zero, zero_t) triples.

    Positive examples (near_zero=1): s = (0.5 + noise, t_k + noise) at known zeros.
    Negative examples (near_zero=0): random points on the critical strip, away from zeros.

    Returns:
        s         [B, 2]   complex points as (sigma, t)
        near_zero [B]      0/1 float
        zero_t    [B]      imaginary part of nearest zero (training target for zero_head)
    """
    half = batch_size // 2

    # Positive: perturbed points near known zeros
    pos_t = [random.choice(zeros_t) + random.gauss(0, 0.1) for _ in range(half)]
    pos_s = [random.gauss(0.5, 0.02) for _ in range(half)]
    pos   = torch.tensor(list(zip(pos_s, pos_t)), dtype=torch.float32)
    pos_label  = torch.ones(half)
    pos_zero_t = torch.tensor(
        [min(zeros_t, key=lambda z: abs(z - t)) for t in pos_t], dtype=torch.float32
    )

    # Negative: random points on critical strip, gap >= eps from any zero
    neg_s_vals, neg_t_vals = [], []
    while len(neg_t_vals) < half:
        t = random.uniform(*t_range)
        if all(abs(t - z) > eps for z in zeros_t):
            neg_t_vals.append(t)
            neg_s_vals.append(random.uniform(0.1, 0.9))
    neg   = torch.tensor(list(zip(neg_s_vals, neg_t_vals)), dtype=torch.float32)
    neg_label  = torch.zeros(half)
    neg_zero_t = torch.tensor(
        [min(zeros_t, key=lambda z: abs(z - t)) for t in neg_t_vals], dtype=torch.float32
    )

    s         = torch.cat([pos, neg], dim=0)
    near_zero = torch.cat([pos_label, neg_label], dim=0)
    zero_t    = torch.cat([pos_zero_t, neg_zero_t], dim=0) / ZERO_T_SCALE

    # Shuffle
    perm = torch.randperm(batch_size)
    return s[perm], near_zero[perm], zero_t[perm]


def train_riemann(
    epochs: int = 300,
    lr: float = 3e-4,
    hidden_dim: int = 256,
    num_layers: int = 8,
    batch_size: int = 128,
    scan_after: bool = True,
) -> RiemannNavigator:
    model = RiemannNavigator(hidden_dim=hidden_dim, num_layers=num_layers).to(DEVICE)
    opt   = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    print(f"RiemannNavigator — hidden={hidden_dim}, layers={num_layers}, device={DEVICE}")
    print(f"Training on {len(RIEMANN_ZEROS_T)} known zeros, {epochs} epochs\n")
    print(f"  {'Epoch':>6}  {'Loss':>10}  {'L_frob':>10}  {'L_sym':>10}"
          f"  {'L_zero':>10}  {'L_near':>10}  {'Acc':>7}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*7}")

    for epoch in range(1, epochs + 1):
        model.train()
        s, near, zero_t = make_riemann_batch(
            RIEMANN_ZEROS_T, batch_size=batch_size,
        )
        s      = s.to(DEVICE)
        near   = near.to(DEVICE)
        zero_t = zero_t.to(DEVICE)

        out = model(s)
        losses = model.compute_loss(
            out,
            true_zero_t=zero_t,
            true_near=near,
            lam_zero=1.0, lam_frob=0.5, lam_sym=1.0, lam_near=0.5,
        )
        losses["loss"].backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        opt.zero_grad()
        sched.step()

        if epoch % 25 == 0 or epoch == 1:
            model.eval()
            with torch.no_grad():
                pred_near = (out["near_zero"] > 0.5).float()
                acc = (pred_near == near).float().mean().item()
            print(f"  {epoch:>6}  {losses['loss'].item():>10.6f}"
                  f"  {losses['L_frob']:>10.6f}  {losses['L_sym']:>10.6f}"
                  f"  {losses['L_zero']:>10.6f}  {losses['L_near']:>10.6f}"
                  f"  {acc:>6.1%}")

    if scan_after:
        _riemann_scan(model)

    return model


def _riemann_scan(model: RiemannNavigator, t_min: float = 10.0, t_max: float = 60.0):
    """Scan the critical line and print peaks (predicted zero locations)."""
    model.eval()
    dev = next(model.parameters()).device

    t_vals_raw = torch.linspace(t_min, t_max, 500)
    sigma      = torch.full_like(t_vals_raw, 0.5)
    s_batch    = torch.stack([sigma, t_vals_raw], dim=-1).to(dev)

    with torch.no_grad():
        out = model(s_batch)

    t_vals = t_vals_raw.tolist()
    near   = out["near_zero"].cpu().tolist()
    # zero_t predictions are normalised; denormalise for display
    zero_t_pred = [v * ZERO_T_SCALE for v in out["zero_t"].cpu().tolist()]

    # Find local maxima in near_zero (predicted zero locations)
    peaks = []
    for i in range(1, len(near) - 1):
        if near[i] > near[i-1] and near[i] > near[i+1] and near[i] > 0.3:
            peaks.append((t_vals[i], near[i], zero_t_pred[i]))

    known_in_range = [z for z in RIEMANN_ZEROS_T if t_min <= z <= t_max]

    print(f"\n── Critical line scan  sigma=1/2,  t ∈ [{t_min}, {t_max}] ──")
    print(f"  Known zeros in range: {len(known_in_range)}")
    print(f"  Predicted peaks:      {len(peaks)}")
    print(f"\n  {'t (scan)':>12}  {'P(near)':>9}  {'zero_t pred':>12}  {'Nearest known':>14}  {'|Δ|':>8}")
    for t, p, zt in peaks[:20]:
        nearest = min(known_in_range, key=lambda z: abs(z - t))
        print(f"  {t:>12.4f}  {p:>9.4f}  {zt:>12.4f}  {nearest:>14.6f}  {abs(t-nearest):>8.4f}")


# ══════════════════════════════════════════════════════════════════════════════
# Yang-Mills navigator training
# ══════════════════════════════════════════════════════════════════════════════

def make_su2_hamiltonian(
    N: int = 64,
    coupling: float = 1.0,
    mass_gap: float = None,
) -> tuple[torch.Tensor, torch.Tensor, float]:
    """
    Generate a random SU(2) Hamiltonian in truncated Fock space.
    Planted mass gap: lowest eigenvalue = 0 (vacuum), next = planted_gap.

    Returns: (H [N, N], lie_structure [3, 3], true_gap)
    """
    # SU(2) structure constants f_abc (fully antisymmetric, f_123=1)
    lie = torch.zeros(3, 3)
    lie[0, 1] = coupling; lie[1, 0] = -coupling  # [T1, T2] = i T3 sector

    # Random symmetric positive semi-definite H with planted gap
    A = torch.randn(N, N) * 0.1
    H = A @ A.T  # PSD baseline
    H = (H + H.T) / 2

    # Plant gap: shift so E0=0, E1=planted_gap
    eigs = torch.linalg.eigvalsh(H)
    H = H - eigs[0] * torch.eye(N)   # shift vacuum to 0
    gap = eigs[1] - eigs[0]
    if mass_gap is not None:
        # Scale to hit the planted gap
        H = H * (mass_gap / (gap + 1e-8))
        gap = mass_gap

    return H, lie, gap.item() if isinstance(gap, torch.Tensor) else gap


def train_yangmills(
    epochs: int = 300,
    lr: float = 3e-4,
    hidden_dim: int = 256,
    batch_size: int = 32,
    fock_dim: int = 64,
    lanczos_steps: int = 32,
) -> YangMillsNavigator:
    model = YangMillsNavigator(
        fock_dim=fock_dim, lie_dim=3, hidden_dim=hidden_dim,
        lanczos_steps=lanczos_steps, n_low=3,
    ).to(DEVICE)
    opt   = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    print(f"YangMillsNavigator — hidden={hidden_dim}, fock={fock_dim}, device={DEVICE}")
    print(f"Training on synthetic SU(2) Hamiltonians, {epochs} epochs\n")
    print(f"  {'Epoch':>6}  {'Loss':>10}  {'L_frob':>10}  {'L_gap':>10}"
          f"  {'Gap_pred':>10}  {'Gap_true':>10}  {'|Delta|':>8}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}")

    for epoch in range(1, epochs + 1):
        model.train()

        # Build batch
        Hs, lies, gaps = [], [], []
        for _ in range(batch_size):
            g = random.uniform(0.1, 3.0)   # random planted gap
            H, lie, gap = make_su2_hamiltonian(N=fock_dim, mass_gap=g)
            Hs.append(H); lies.append(lie); gaps.append(gap)

        H_batch   = torch.stack(Hs).to(DEVICE)
        lie_batch = torch.stack(lies).to(DEVICE)
        gap_batch = torch.tensor(gaps, dtype=torch.float32).to(DEVICE)

        out = model(H_batch, lie_batch)
        losses = model.compute_loss(
            out, true_gap=gap_batch, lam_gap=1.0, lam_frob=0.5, lam_charge=0.2,
        )
        losses["loss"].backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        opt.zero_grad()
        sched.step()

        if epoch % 25 == 0 or epoch == 1:
            pred_gap = out["mass_gap"].mean().item()
            true_gap = gap_batch.mean().item()
            print(f"  {epoch:>6}  {losses['loss'].item():>10.6f}"
                  f"  {losses['L_frob']:>10.6f}  {losses['L_gap']:>10.6f}"
                  f"  {pred_gap:>10.4f}  {true_gap:>10.4f}"
                  f"  {abs(pred_gap - true_gap):>8.4f}")

    return model


# ══════════════════════════════════════════════════════════════════════════════
# ThurstonNet training
# ══════════════════════════════════════════════════════════════════════════════

def make_synthetic_manifold(
    geo_class: int,
    n_nodes: int = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Generate a synthetic simplicial complex with geometry-class-dependent structure.

    The planted signal:
        S3  (0) — high clustering, positive Ricci curvature, even degree
        E3  (1) — flat, uniform degree, zero curvature
        H3  (2) — negative curvature, tree-like branching, high diameter
        S2xR (3) — layered: two high-curvature components
        H2xR (4) — layered: one negative, one flat component
        SL2R (5) — twisted: asymmetric degree distribution
        Nil  (6) — nilpotent structure: linear chain + dense hub
        Sol  (7) — solvegeometry: bipartite-like, alternating curvature
    """
    if n_nodes is None:
        n_nodes = random.randint(20, 60)

    # Node positions: encoded as (x, y, z) with geometry-class-specific distribution
    if geo_class == 0:   # S3: spherical — nodes on unit sphere
        pos = F.normalize(torch.randn(n_nodes, 3), dim=-1)
    elif geo_class == 1: # E3: flat — uniform in cube
        pos = torch.rand(n_nodes, 3) * 2 - 1
    elif geo_class == 2: # H3: hyperbolic — exponential radial
        r   = torch.distributions.Exponential(0.5).sample((n_nodes,))
        phi = torch.rand(n_nodes) * 2 * math.pi
        th  = torch.rand(n_nodes) * math.pi
        pos = torch.stack([
            r * torch.sin(th) * torch.cos(phi),
            r * torch.sin(th) * torch.sin(phi),
            r * torch.cos(th),
        ], dim=-1)
    elif geo_class in (3, 4):  # product geometries: layered
        half = n_nodes // 2
        p1 = F.normalize(torch.randn(half, 3), dim=-1)
        p2 = torch.rand(n_nodes - half, 3)
        if geo_class == 4:
            r = torch.distributions.Exponential(0.5).sample((n_nodes - half,))
            p2 = p2 * r.unsqueeze(-1)
        pos = torch.cat([p1, p2], dim=0)
    elif geo_class == 5:  # SL2R: twisted
        t   = torch.linspace(0, 4 * math.pi, n_nodes)
        pos = torch.stack([torch.cos(t), torch.sin(t), t / (4 * math.pi)], dim=-1)
        pos = pos + torch.randn_like(pos) * 0.1
    elif geo_class == 6:  # Nil: nilpotent chain + hub
        chain = torch.stack([torch.linspace(0, 1, n_nodes - 1),
                              torch.zeros(n_nodes - 1),
                              torch.zeros(n_nodes - 1)], dim=-1)
        hub   = torch.zeros(1, 3)
        pos   = torch.cat([chain, hub], dim=0)
    else:                 # Sol: bipartite curvature alternation
        pos = torch.randn(n_nodes, 3)
        pos[::2] *= 0.3    # compact subgroup
        pos[1::2] *= 1.7   # expansive subgroup

    # Build k-NN edges (k=6)
    k = min(6, n_nodes - 1)
    dists = torch.cdist(pos, pos)
    dists.fill_diagonal_(float('inf'))
    knn = dists.topk(k, largest=False).indices  # [N, k]
    src = torch.arange(n_nodes).unsqueeze(1).expand(-1, k).reshape(-1)
    dst = knn.reshape(-1)
    edge_idx = torch.stack([src, dst], dim=0)

    # Edge attributes: (length, angle_to_centroid, curvature_proxy, class_signal)
    edge_vec  = pos[dst] - pos[src]
    edge_len  = edge_vec.norm(dim=-1, keepdim=True)
    centroid  = pos.mean(dim=0)
    to_c      = (pos[src] - centroid)
    angle     = (edge_vec * to_c).sum(dim=-1, keepdim=True) / (
        edge_len * to_c.norm(dim=-1, keepdim=True) + 1e-8
    )
    # Curvature proxy: negative = hyperbolic, positive = spherical
    curv_sign = torch.tensor([[1.0 if geo_class in (0,3) else
                               -1.0 if geo_class in (2,4) else 0.0]])
    curv      = curv_sign.expand(edge_len.size(0), 1) * (1.0 / (edge_len + 1e-8))
    # Weak class signal (makes learning feasible in a few epochs)
    signal    = torch.full((edge_len.size(0), 1), geo_class / 7.0)
    edge_attr = torch.cat([edge_len, angle, curv, signal], dim=-1)   # [E, 4]

    return pos, edge_idx, edge_attr


def train_thurston(
    epochs: int = 300,
    lr: float = 3e-4,
    hidden_dim: int = 256,
    num_ricci_layers: int = 4,   # use 4 for speed; 24 for full architecture
    batch_size: int = 16,
) -> ThurstonNet:
    model = ThurstonNet(
        node_dim=3, edge_dim=4, hidden_dim=hidden_dim,
        num_ricci_layers=num_ricci_layers,
    ).to(DEVICE)
    opt   = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    print(f"ThurstonNet — hidden={hidden_dim}, ricci_layers={num_ricci_layers}, device={DEVICE}")
    print(f"Training on synthetic simplicial complexes (8 Thurston geometries), {epochs} epochs\n")
    print(f"  {'Epoch':>6}  {'Loss':>10}  {'L_geo':>10}  {'L_frob':>10}  {'Acc':>7}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*7}")

    for epoch in range(1, epochs + 1):
        model.train()

        # Build batch manually (variable-size graphs — process one at a time)
        epoch_loss, epoch_geo, epoch_frob, correct, total = 0., 0., 0., 0, 0
        for _ in range(batch_size):
            geo = random.randint(0, 7)
            pos, edge_idx, edge_attr = make_synthetic_manifold(geo)
            pos       = pos.to(DEVICE)
            edge_idx  = edge_idx.to(DEVICE)
            edge_attr = edge_attr.to(DEVICE)
            label     = torch.tensor([geo], dtype=torch.long, device=DEVICE)

            out = model(pos, edge_idx, edge_attr)
            losses = model.compute_loss(out, true_geo=label,
                                        lam_geo=1.0, lam_frob=0.5, lam_ricci=0.0)
            losses["loss"].backward()
            epoch_loss += losses["loss"].item()
            epoch_geo  += losses["L_geo"]
            epoch_frob += losses["L_frob"]
            pred = out["geo_logits"].argmax(dim=-1).item()
            correct += int(pred == geo)
            total   += 1

        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        opt.zero_grad()
        sched.step()

        if epoch % 25 == 0 or epoch == 1:
            print(f"  {epoch:>6}  {epoch_loss/batch_size:>10.6f}"
                  f"  {epoch_geo/batch_size:>10.6f}  {epoch_frob/batch_size:>10.6f}"
                  f"  {correct/total:>6.1%}")

    # Per-class accuracy
    _thurston_eval(model)
    return model


def _thurston_eval(model: ThurstonNet, n_per_class: int = 20):
    model.eval()
    print("\n── Thurston geometry classification accuracy ──")
    print(f"  {'Geometry':>10}  {'Acc':>7}")
    for geo_idx, name in enumerate(THURSTON_GEOMETRIES):
        correct = 0
        for _ in range(n_per_class):
            pos, edge_idx, edge_attr = make_synthetic_manifold(geo_idx)
            with torch.no_grad():
                out = model(pos.to(DEVICE), edge_idx.to(DEVICE), edge_attr.to(DEVICE))
            pred = out["geo_logits"].argmax(dim=-1).item()
            correct += int(pred == geo_idx)
        print(f"  {name:>10}  {correct/n_per_class:>6.1%}")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train O_inf domain navigators",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("navigator", choices=["riemann", "yangmills", "thurston", "all"])
    parser.add_argument("--epochs",     "-e", type=int,   default=300)
    parser.add_argument("--lr",               type=float, default=3e-4)
    parser.add_argument("--hidden-dim",       type=int,   default=256)
    parser.add_argument("--batch-size", "-b", type=int,   default=None,
                        help="batch size (navigator-specific default if omitted)")
    parser.add_argument("--num-layers",       type=int,   default=None,
                        help="GNN depth (navigator-specific default if omitted)")
    args = parser.parse_args()

    def run_riemann():
        train_riemann(
            epochs=args.epochs, lr=args.lr, hidden_dim=args.hidden_dim,
            num_layers=args.num_layers or 8,
            batch_size=args.batch_size or 128,
        )

    def run_yangmills():
        train_yangmills(
            epochs=args.epochs, lr=args.lr, hidden_dim=args.hidden_dim,
            batch_size=args.batch_size or 32,
        )

    def run_thurston():
        train_thurston(
            epochs=args.epochs, lr=args.lr, hidden_dim=args.hidden_dim,
            num_ricci_layers=args.num_layers or 4,
            batch_size=args.batch_size or 16,
        )

    if args.navigator == "riemann":
        run_riemann()
    elif args.navigator == "yangmills":
        run_yangmills()
    elif args.navigator == "thurston":
        run_thurston()
    elif args.navigator == "all":
        print("=" * 70)
        print("RIEMANN NAVIGATOR")
        print("=" * 70)
        run_riemann()
        print("\n" + "=" * 70)
        print("YANG-MILLS NAVIGATOR")
        print("=" * 70)
        run_yangmills()
        print("\n" + "=" * 70)
        print("THURSTON NET")
        print("=" * 70)
        run_thurston()
