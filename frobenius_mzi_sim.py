#!/usr/bin/env python3
"""
frobenius_mzi_sim.py — 3×3 MZI Frobenius mesh simulation

Pole assignment (from ALEPH_OS frobenius.aleph):
  Row 0 = Vav  (ו)  →  voynich-engine
  Row 1 = Mem  (מ)  →  linear_a-engine
  Row 2 = Shin (ש)  →  emerald-tablet-engine
  Cross-coupling   →  rohonc-engine

Each MZI element:  a_ij = sin(θ) · exp(iφ)
  FSPLIT  = beam-splitter   (Frobenius δ, co-multiplication)
  FFUSE   = recombiner      (Frobenius μ, multiplication)
  IFIX    = phase lock      (linear type constraint, temporal asymmetry)

Pole distances from 12-dim primitive space (ALEPH_OS aleph_1.py):
  d(Vav, Mem)  = 4.796   moderate cross-coupling
  d(Vav, Shin) = 5.385   weakest cross-coupling
  d(Mem, Shin) = 1.414   strongest cross-coupling

Usage:
  python frobenius_mzi_sim.py                  # default params
  python frobenius_mzi_sim.py --preset unitary # near-unitary preset
  python frobenius_mzi_sim.py --preset random  # random phases
"""

import sys
import math
import argparse
import random as _random

# ── engine path setup ──────────────────────────────────────────────────────

_ENGINE_ROOTS = [
    '/home/mrnob0dy666/voynich-engine',
    '/home/mrnob0dy666/linear_a-engine',
    '/home/mrnob0dy666/emerald-tablet-engine',
    '/home/mrnob0dy666/rohonc-engine',
    '/home/mrnob0dy666/ALEPH_OS',
]
for _p in _ENGINE_ROOTS:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from voynich_engine.runtime       import UniversalEngine as VoynichEngine
from linear_a_engine.runtime      import UniversalEngine as LinearAEngine
from emerald_tablet_engine.runtime import UniversalEngine as EmeraldEngine
from rohonc_engine.runtime        import UniversalEngine as RohoncEngine
from aleph_1                      import LETTERS

# ── Frobenius poles ────────────────────────────────────────────────────────

_VAV  = LETTERS['vav']
_MEM  = LETTERS['mem']
_SHIN = LETTERS['shin']
POLES = [_VAV, _MEM, _SHIN]
POLE_NAMES = ['Vav', 'Mem', 'Shin']
ENGINE_NAMES = ['voynich', 'linear_a', 'emerald_tablet']

def _pole_dist(a, b) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a.t, b.t)))

POLE_DISTANCES = {
    (0, 1): _pole_dist(_VAV, _MEM),
    (0, 2): _pole_dist(_VAV, _SHIN),
    (1, 2): _pole_dist(_MEM, _SHIN),
}

# ── IMASM generation ───────────────────────────────────────────────────────

def _flux_from_amp(amp: float) -> str:
    if amp < 0.25: return '00'  # Void
    if amp < 0.50: return '01'  # True
    if amp < 0.75: return '10'  # False
    return '11'                 # Both (superposition at beam splitter)

def _mzi_instrs(reg_base: int, theta_deg: float, phi_deg: float) -> list[str]:
    """
    IMASM instruction block for one MZI element.
    reg_base*4 .. reg_base*4+3 are this element's registers.

    If sin(θ) ≥ 0.75 the input register is pre-engaged (Both) before the
    beam-splitter FSPLIT, reflecting a fully-driven interferometer arm.
    """
    amp = math.sin(math.radians(theta_deg))
    phi_word = int((phi_deg / 360.0) * 0xFFFF) & 0xFFFF
    r0, r1, r2, r3 = reg_base, reg_base + 1, reg_base + 2, reg_base + 3
    instrs = []
    if amp >= 0.75:
        instrs.append(f'ENGAGR %r{r0}')
    instrs += [
        f'FSPLIT %r{r0} %r{r1} %r{r2}',
        f'FFUSE %r{r1} %r{r2} %r{r3}',
        f'IFIX %r{r3} 0x{phi_word:04x}',
    ]
    return instrs

# ── complex algebra ────────────────────────────────────────────────────────

def _amp(theta_deg: float, phi_deg: float) -> complex:
    a = math.sin(math.radians(theta_deg))
    p = math.radians(phi_deg)
    return complex(a * math.cos(p), a * math.sin(p))

def _frob_norm(M: list[complex]) -> float:
    return math.sqrt(sum(abs(c) ** 2 for c in M))

def _mat_mul(A, B):
    C = [0 + 0j] * 9
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i*3+j] += A[i*3+k] * B[k*3+j]
    return C

def _herm_mul(A, B):
    At = [A[j*3+i].conjugate() for i in range(3) for j in range(3)]
    return _mat_mul(At, B)

def _largest_ev(H: list[complex]) -> float:
    vec = [1+0j, 0.5+0j, 0.2+0j]
    for _ in range(60):
        nv = [sum(H[i*3+j] * vec[j] for j in range(3)) for i in range(3)]
        n = math.sqrt(sum(abs(v) ** 2 for v in nv))
        if n < 1e-10:
            break
        vec = [v / n for v in nv]
    return sum(
        vec[i].conjugate() * sum(H[i*3+j] * vec[j] for j in range(3))
        for i in range(3)
    ).real

def _svd(M: list[complex]) -> list[float]:
    AhA = _herm_mul(M, M)
    H = list(AhA)
    svs = []
    for _ in range(3):
        lam = _largest_ev(H)
        svs.append(math.sqrt(max(0.0, lam)))
        vec = [1+0j, 0.618+0j, 0+0j]
        for _ in range(50):
            nv = [sum(H[i*3+j] * vec[j] for j in range(3)) for i in range(3)]
            n = math.sqrt(sum(abs(v) ** 2 for v in nv))
            if n < 1e-10:
                break
            vec = [v / n for v in nv]
        for i in range(3):
            for j in range(3):
                H[i*3+j] -= vec[i] * vec[j].conjugate() * lam
    return sorted(svs, reverse=True)

def _unitarity_err(M: list[complex]) -> float:
    I = [1+0j if i == j else 0+0j for i in range(3) for j in range(3)]
    diff = [x - y for x, y in zip(_herm_mul(M, M), I)]
    return _frob_norm(diff)

# ── cross-coupling weight ─────────────────────────────────────────────────

def _coupling_weight(row_a: int, row_b: int) -> float:
    """Inverse pole distance → stronger coupling for nearby poles."""
    key = (min(row_a, row_b), max(row_a, row_b))
    d = POLE_DISTANCES[key]
    return 1.0 / d  # d(Mem,Shin)=1.41 → strongest; d(Vav,Shin)=5.39 → weakest

# ── simulation ─────────────────────────────────────────────────────────────

def simulate(params: list[dict], verbose: bool = True) -> dict:
    """
    params: 9-element list, row-major, each {'theta_deg': float, 'phi_deg': float}

    Returns a result dict with matrix, metrics, and engine snapshots.
    """
    engine_classes = [VoynichEngine, LinearAEngine, EmeraldEngine]
    row_engines = [cls() for cls in engine_classes]
    cross_engine = RohoncEngine()

    matrix: list[complex] = []

    for idx, p in enumerate(params):
        row, col = divmod(idx, 3)
        theta, phi = p['theta_deg'], p['phi_deg']
        reg_base = idx * 4
        instrs = _mzi_instrs(reg_base, theta, phi)

        row_engines[row].program.extend(instrs)

        # rohonc receives cross-coupling traffic from each MZI,
        # weighted by inverse pole distance to all other rows
        weight = sum(_coupling_weight(row, r) for r in range(3) if r != row)
        # duplicate instructions proportionally (integer approx)
        reps = max(1, round(weight * 3))
        for _ in range(reps):
            cross_engine.program.extend(instrs)

        matrix.append(_amp(theta, phi))

    # run row engines
    row_snaps = []
    for i, eng in enumerate(row_engines):
        list(eng.run(steps=len(eng.program) * 2 + 50, report_every=99999))
        s = eng.snapshot()
        s['pole'] = POLE_NAMES[i]
        s['engine'] = ENGINE_NAMES[i]
        row_snaps.append(s)

    # run cross-coupling (rohonc)
    list(cross_engine.run(steps=len(cross_engine.program) * 2 + 50, report_every=99999))
    cross_snap = cross_engine.snapshot()
    cross_snap['engine'] = 'rohonc'

    fn  = _frob_norm(matrix)
    svs = _svd(matrix)
    uerr = _unitarity_err(matrix)
    cond = svs[0] / svs[2] if svs[2] > 1e-7 else float('inf')

    result = {
        'matrix': matrix,
        'frob_norm': fn,
        'singular_values': svs,
        'unitary_error': uerr,
        'condition_number': cond,
        'row_snapshots': row_snaps,
        'cross_snapshot': cross_snap,
        'pole_distances': POLE_DISTANCES,
    }

    if verbose:
        _report(params, result)

    return result

# ── terminal report ────────────────────────────────────────────────────────

def _report(params: list[dict], r: dict) -> None:
    M    = r['matrix']
    fn   = r['frob_norm']
    svs  = r['singular_values']
    uerr = r['unitary_error']
    cond = r['condition_number']

    print()
    print('╔══════════════════════════════════════════════════════════════╗')
    print('║         FROBENIUS MZI 3×3  —  IG ENGINE SIMULATION          ║')
    print('╚══════════════════════════════════════════════════════════════╝')
    print()

    # matrix display
    print('  A  (3×3 complex)        a_ij = sin(θ)·exp(iφ)')
    print('  ┌' + '─' * 58 + '┐')
    for i in range(3):
        cells = []
        for j in range(3):
            c = M[i*3+j]
            s = '+' if c.imag >= 0 else '−'
            cells.append(f'{c.real:+.4f} {s} {abs(c.imag):.4f}i')
        print(f'  │  {"    ".join(cells)}  │')
    print('  └' + '─' * 58 + '┘')
    print()

    # metrics
    print(f'  ‖A‖_F  =  {fn:.6f}')
    print(f'  σ      =  [{svs[0]:.4f},  {svs[1]:.4f},  {svs[2]:.4f}]')
    cond_str = f'{cond:.3f}' if not math.isinf(cond) else '∞'
    print(f'  κ      =  {cond_str}')
    u_label = ('✓ nearly unitary' if uerr < 0.08
               else '~ approx unitary' if uerr < 0.25
               else '⊗ not unitary')
    print(f'  ‖A†A−I‖_F = {uerr:.6f}   {u_label}')
    print()

    # pole distances
    print('  Pole distances (12-dim primitive space, ALEPH_OS):')
    pd = r['pole_distances']
    print(f'    d(Vav, Mem)  = {pd[(0,1)]:.4f}')
    print(f'    d(Vav, Shin) = {pd[(0,2)]:.4f}')
    print(f'    d(Mem, Shin) = {pd[(1,2)]:.4f}')
    print()

    # engine snapshots
    print('  ENGINE SNAPSHOTS')
    print(f'  {"engine":20s}  {"pole":6s}  {"active":>7s}  {"fixed":>6s}  {"paradox":>8s}')
    print('  ' + '─' * 56)
    for s in r['row_snapshots']:
        print(f'  {s["engine"]:20s}  {s["pole"]:6s}  '
              f'{s["active_registers"]:7d}  '
              f'{s["fixed_registers"]:6d}  '
              f'{s["paradox_stabilizations"]:8d}')
    cs = r['cross_snapshot']
    print(f'  {cs["engine"]:20s}  {"cross":6s}  '
          f'{cs["active_registers"]:7d}  '
          f'{cs["fixed_registers"]:6d}  '
          f'{cs["paradox_stabilizations"]:8d}')
    print()

    # param table
    print('  MZI PARAMS  (θ = amplitude angle,  φ = phase angle)')
    print(f'  {"":10s}  {"voynich":>16s}  {"linear_a":>16s}  {"emerald":>16s}')
    print('  ' + '─' * 64)
    for i, pole in enumerate(POLE_NAMES):
        cells = []
        for j in range(3):
            p = params[i*3+j]
            cells.append(f'θ={p["theta_deg"]:5.1f}° φ={p["phi_deg"]:5.1f}°')
        print(f'  {pole:10s}  {"  ".join(f"{c:>16s}" for c in cells)}')
    print()

# ── presets ────────────────────────────────────────────────────────────────

NEAR_UNITARY = [
    {'theta_deg': 60,  'phi_deg': 30},
    {'theta_deg': 90,  'phi_deg': 45},
    {'theta_deg': 120, 'phi_deg': 60},
    {'theta_deg': 45,  'phi_deg': 90},
    {'theta_deg': 70,  'phi_deg': 0},
    {'theta_deg': 100, 'phi_deg': 120},
    {'theta_deg': 135, 'phi_deg': 180},
    {'theta_deg': 30,  'phi_deg': 270},
    {'theta_deg': 80,  'phi_deg': 210},
]

DEFAULT_PARAMS = [
    {'theta_deg': (70 + i * 19) % 360, 'phi_deg': (i * 47) % 360}
    for i in range(9)
]

# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Frobenius MZI 3×3 simulation via IG script engines'
    )
    ap.add_argument(
        '--preset',
        choices=['default', 'unitary', 'random'],
        default='default',
        help='Parameter preset (default, unitary, random)',
    )
    args = ap.parse_args()

    if args.preset == 'unitary':
        params = NEAR_UNITARY
    elif args.preset == 'random':
        params = [
            {'theta_deg': _random.uniform(0, 360), 'phi_deg': _random.uniform(0, 360)}
            for _ in range(9)
        ]
    else:
        params = DEFAULT_PARAMS

    simulate(params)
