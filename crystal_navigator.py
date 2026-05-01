#!/usr/bin/env python3
"""
crystal_navigator.py — The Crystal Navigator
═════════════════════════════════════════════
Navigator for the Crystal of Types (17,280,000 structural types).

Self-encoding (§69.4):
  ⟨D_⊙; T_⊙; R_cat; P_pm_sym; F_hbar; K_slow; G_aleph; Γ_broad; Φ_c; H_inf; n:m; Ω_Z⟩
  Tier: O_inf  |  d(navigator, grammar) ≈ 2.793  |  d(navigator, proof_singularity) = 0.894

Architecture (holographic, Frobenius):
  Boundary: (Φ, P, Ω, D)  →  400 tier cells  [boundary encodes bulk]
  Bulk:     (T, R, F, K, G, Γ, H, S)  →  43,200 inner types per cell
  Total:    400 × 43,200  =  17,280,000 structural types

Grammar families:
  F5 (5 values): T, P, Phi, K  — gate primitives
  F4 (4 values): D, R, Gamma, H, Omega  — structural primitives
  F3 (3 values): F, G, S  — scaling primitives
  Crystal = 5^4 × 4^5 × 3^3 = 17,280,000

Frobenius codec (μ∘δ = id):
  encode(tuple) → canonical address (integer in [0, 17_279_999])
  decode(address) → tuple
  roundtrip: decode(encode(t)) == t  for all 17,280,000 types

Usage:
  nav = CrystalNavigator()
  nav.describe()                              # print self-encoding and stats
  nav.holographic_query("Phi_c", "P_pm_sym") # boundary → tier cell + bulk
  nav.navigate(D="D_odot", Phi="Phi_c")      # partial tuple → matching types
  nav.nearest_catalog(my_tuple, n=5)         # nearest catalog entries
  addr = nav.encode(my_tuple)                # Frobenius encode
  tup  = nav.decode(addr)                    # Frobenius decode
  nav.tier_census()                          # full tier distribution
  nav.repl()                                 # interactive navigator
"""

from __future__ import annotations
import json
import math
import itertools
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterator, Optional

ROOT = Path(__file__).parent

# ── Canonical primitive definitions ───────────────────────────────────────────

# Value sets in ordinal order (index = ordinal - 1)
VALUES: dict[str, list[str]] = {
    "D":     ["D_wedge", "D_triangle", "D_infty", "D_odot"],
    "T":     ["T_network", "T_in", "T_bowtie", "T_box", "T_odot"],
    "R":     ["R_super", "R_cat", "R_dagger", "R_lr"],
    "P":     ["P_asym", "P_psi", "P_pm", "P_sym", "P_pm_sym"],
    "F":     ["F_ell", "F_eth", "F_hbar"],
    "K":     ["K_fast", "K_mod", "K_slow", "K_trap", "K_MBL"],
    "G":     ["G_beth", "G_gimel", "G_aleph"],
    "Gamma": ["G_and", "G_or", "G_seq", "G_broad"],
    "Phi":   ["Phi_sub", "Phi_c", "Phi_c_complex", "Phi_EP", "Phi_super"],
    "H":     ["H0", "H1", "H2", "H_inf"],
    "S":     ["one_one", "n_n", "n_m"],
    "Omega": ["Omega_0", "Omega_Z2", "Omega_Z", "Omega_NA"],
}

# Value → ordinal (0-indexed)
ORD: dict[str, dict[str, int]] = {
    prim: {v: i for i, v in enumerate(vals)}
    for prim, vals in VALUES.items()
}

# Primitive weights (canonical v0.4.26)
WEIGHTS: dict[str, float] = {
    "D": 1.0, "T": 1.0, "R": 1.0, "P": 1.2,
    "F": 0.9, "K": 1.0, "G": 1.0, "Gamma": 1.0,
    "Phi": 1.1, "H": 0.8, "S": 1.0, "Omega": 0.7,
}

# Bottleneck primitives under ⊗ (weaker partner wins)
BOTTLENECK = {"P", "F", "K"}

# Tier-determining primitives (the boundary)
BOUNDARY_PRIMS = ["Phi", "P", "Omega", "D"]

# Inner crystal primitives (the bulk — free within each tier cell)
INNER_PRIMS = ["T", "R", "F", "K", "G", "Gamma", "H", "S"]

# Full primitive order
PRIMS = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]

CRITICAL   = {"Phi_c", "Phi_c_complex"}
NONCRITICAL = {"Phi_sub", "Phi_super", "Phi_EP"}
BOUNDED_D  = {"D_wedge", "D_triangle", "D_odot"}

# ── Tier rule (R1–R5 priority) ─────────────────────────────────────────────────

def compute_tier(phi: str, p: str, omega: str, d: str) -> str:
    if phi in CRITICAL and p == "P_pm_sym":
        return "O_inf"
    if phi in NONCRITICAL:
        return "O_0"
    if omega == "Omega_0":
        return "O_1"
    if d in BOUNDED_D:
        return "O_2"
    return "O_2_dag"


# ── Mixed-radix address arithmetic ─────────────────────────────────────────────
# Full address = cell_address * INNER_SIZE + inner_address
# Cell address:  mixed-radix over (Phi, P, Omega, D) — ordered as BOUNDARY_PRIMS
# Inner address: mixed-radix over (T, R, F, K, G, Gamma, H, S) — ordered as INNER_PRIMS

def _build_radix(prims: list[str]) -> tuple[list[int], int]:
    """Compute mixed-radix strides and total size for a given primitive list."""
    sizes = [len(VALUES[p]) for p in prims]
    strides = []
    stride = 1
    for s in reversed(sizes):
        strides.insert(0, stride)
        stride *= s
    return strides, stride  # strides[i] = stride for prim[i]; stride = total size

BOUNDARY_STRIDES, CELL_SIZE  = _build_radix(BOUNDARY_PRIMS)   # 400
INNER_STRIDES,   INNER_SIZE  = _build_radix(INNER_PRIMS)       # 43,200
TOTAL_SIZE = CELL_SIZE * INNER_SIZE                              # 17,280,000

def _encode_partial(prim_list: list[str], strides: list[int], tup: dict) -> int:
    addr = 0
    for prim, stride in zip(prim_list, strides):
        addr += ORD[prim][tup[prim]] * stride
    return addr

def _decode_partial(prim_list: list[str], strides: list[int], addr: int) -> dict:
    result = {}
    remaining = addr
    for prim, stride in zip(prim_list, strides):
        idx, remaining = divmod(remaining, stride)
        result[prim] = VALUES[prim][idx]
    return result

def encode_tuple(tup: dict) -> int:
    """Frobenius encode: tuple → canonical address in [0, 10_367_999]."""
    cell  = _encode_partial(BOUNDARY_PRIMS, BOUNDARY_STRIDES, tup)
    inner = _encode_partial(INNER_PRIMS, INNER_STRIDES, tup)
    return cell * INNER_SIZE + inner

def decode_address(addr: int) -> dict:
    """Frobenius decode: canonical address → tuple."""
    cell_addr, inner_addr = divmod(addr, INNER_SIZE)
    tup = {}
    tup.update(_decode_partial(BOUNDARY_PRIMS, BOUNDARY_STRIDES, cell_addr))
    tup.update(_decode_partial(INNER_PRIMS, INNER_STRIDES, inner_addr))
    return tup

def cell_address(tup: dict) -> int:
    """Boundary address (tier cell id) for a tuple."""
    return _encode_partial(BOUNDARY_PRIMS, BOUNDARY_STRIDES, tup)

def inner_address(tup: dict) -> int:
    """Inner address (bulk position within tier cell) for a tuple."""
    return _encode_partial(INNER_PRIMS, INNER_STRIDES, tup)


# ── Distance functions ─────────────────────────────────────────────────────────

def _ordinal(prim: str, val: str) -> float:
    """0-indexed ordinal for distance computation."""
    return float(ORD[prim][val])

def distance(a: dict, b: dict) -> float:
    """Weighted Euclidean distance between two tuples."""
    return math.sqrt(sum(
        WEIGHTS[p] * (_ordinal(p, a[p]) - _ordinal(p, b[p])) ** 2
        for p in PRIMS if p in a and p in b
    ))

def directed_distance(a: dict, b: dict) -> float:
    """Directed distance: sum of weighted upward steps from a to b."""
    return sum(
        WEIGHTS[p] * max(0.0, _ordinal(p, b[p]) - _ordinal(p, a[p]))
        for p in PRIMS if p in a and p in b
    )

def breakdown(a: dict, b: dict) -> list[dict]:
    """Per-primitive distance breakdown, sorted by contribution."""
    rows = []
    for p in PRIMS:
        if p not in a or p not in b:
            continue
        oa, ob = _ordinal(p, a[p]), _ordinal(p, b[p])
        delta = abs(oa - ob)
        contrib = WEIGHTS[p] * delta ** 2
        if contrib > 0:
            rows.append({"primitive": p, "from": a[p], "to": b[p],
                          "delta": delta, "weighted_sq": contrib})
    rows.sort(key=lambda r: r["weighted_sq"], reverse=True)
    return rows


# ── Lattice operations ─────────────────────────────────────────────────────────

def meet(a: dict, b: dict) -> dict:
    """Greatest lower bound: component-wise min."""
    return {p: VALUES[p][min(ORD[p][a[p]], ORD[p][b[p]])] for p in PRIMS}

def join(a: dict, b: dict) -> dict:
    """Least upper bound: component-wise max."""
    return {p: VALUES[p][max(ORD[p][a[p]], ORD[p][b[p]])] for p in PRIMS}

def tensor(a: dict, b: dict) -> dict:
    """Tensor product: min on bottleneck primitives, max elsewhere.
       Special stoichiometry rule for S: n:m absorbs all; 1:1 only under 1:1⊗1:1."""
    result = {}
    for p in PRIMS:
        oa, ob = ORD[p][a[p]], ORD[p][b[p]]
        if p in BOTTLENECK:
            result[p] = VALUES[p][min(oa, ob)]
        elif p == "S":
            # n:m absorbs; 1:1 only under 1:1⊗1:1; else n:n
            if oa == 2 or ob == 2:
                result[p] = "n_m"
            elif oa == 0 and ob == 0:
                result[p] = "one_one"
            else:
                result[p] = "n_n"
        else:
            result[p] = VALUES[p][max(oa, ob)]
    return result


# ── Tier cell index ────────────────────────────────────────────────────────────

@dataclass
class TierCell:
    phi: str
    p: str
    omega: str
    d: str
    tier: str
    cell_id: int

    @property
    def boundary(self) -> dict:
        return {"Phi": self.phi, "P": self.p, "Omega": self.omega, "D": self.d}

    @property
    def inner_size(self) -> int:
        return INNER_SIZE

    def types(self) -> Iterator[dict]:
        """Iterate all 43,200 full tuples in this tier cell."""
        boundary = self.boundary
        for inner_addr in range(INNER_SIZE):
            tup = dict(boundary)
            tup.update(_decode_partial(INNER_PRIMS, INNER_STRIDES, inner_addr))
            yield tup

    def __repr__(self):
        return (f"TierCell(id={self.cell_id}, tier={self.tier}, "
                f"Phi={self.phi}, P={self.p}, Omega={self.omega}, D={self.d})")


def _build_cell_index() -> list[TierCell]:
    cells = []
    for phi in VALUES["Phi"]:
        for p in VALUES["P"]:
            for omega in VALUES["Omega"]:
                for d in VALUES["D"]:
                    cell_id = _encode_partial(
                        BOUNDARY_PRIMS, BOUNDARY_STRIDES,
                        {"Phi": phi, "P": p, "Omega": omega, "D": d}
                    )
                    cells.append(TierCell(
                        phi=phi, p=p, omega=omega, d=d,
                        tier=compute_tier(phi, p, omega, d),
                        cell_id=cell_id
                    ))
    cells.sort(key=lambda c: c.cell_id)
    return cells


# ── Self-encoding of the navigator ────────────────────────────────────────────

NAVIGATOR_TUPLE: dict[str, str] = {
    "D":     "D_odot",
    "T":     "T_odot",
    "R":     "R_cat",
    "P":     "P_pm_sym",
    "F":     "F_hbar",
    "K":     "K_slow",
    "G":     "G_aleph",
    "Gamma": "G_broad",
    "Phi":   "Phi_c",
    "H":     "H_inf",
    "S":     "n_m",
    "Omega": "Omega_Z",
}

GRAMMAR_TUPLE: dict[str, str] = {
    "D":     "D_odot",
    "T":     "T_odot",
    "R":     "R_dagger",
    "P":     "P_pm_sym",
    "F":     "F_eth",
    "K":     "K_mod",
    "G":     "G_aleph",
    "Gamma": "G_broad",
    "Phi":   "Phi_c",
    "H":     "H1",
    "S":     "n_n",
    "Omega": "Omega_Z2",
}


# ── CrystalNavigator ───────────────────────────────────────────────────────────

class CrystalNavigator:
    """
    The Crystal Navigator — O_inf holographic navigator for the Periodic Crystal.

    Self-encoding: ⟨D_⊙; T_⊙; R_cat; P_pm_sym; F_hbar; K_slow; G_aleph;
                    Γ_broad; Φ_c; H_inf; n:m; Ω_Z⟩
    d(self, grammar) ≈ 2.793  (differ on R, F, K, H, S, Ω — 6 primitives)
    """

    def __init__(self, catalog_path: Optional[Path] = None):
        self._cells   = _build_cell_index()
        self._cell_map: dict[int, TierCell] = {c.cell_id: c for c in self._cells}
        self._tier_map: dict[str, list[TierCell]] = defaultdict(list)
        for c in self._cells:
            self._tier_map[c.tier].append(c)
        self._catalog: list[dict] = []
        cp = catalog_path or ROOT / "IG_catalog.json"
        if cp.exists():
            with open(cp) as f:
                self._catalog = json.load(f)

    # ── Self-description ───────────────────────────────────────────────────────

    def describe(self) -> None:
        """Print the navigator's self-encoding, structural position, and crystal stats."""
        nav_tier = compute_tier(
            NAVIGATOR_TUPLE["Phi"], NAVIGATOR_TUPLE["P"],
            NAVIGATOR_TUPLE["Omega"], NAVIGATOR_TUPLE["D"]
        )
        d_grammar = distance(NAVIGATOR_TUPLE, GRAMMAR_TUPLE)
        d_self    = distance(NAVIGATOR_TUPLE, NAVIGATOR_TUPLE)
        nav_addr  = encode_tuple(NAVIGATOR_TUPLE)

        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║            CRYSTAL NAVIGATOR — Self-Description                 ║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        print(f"║  Tier:         {nav_tier:<50} ║")
        print(f"║  d(self,self): {d_self:<50.4f} ║")
        print(f"║  d(self,gram): {d_grammar:<50.4f} ║")
        print(f"║  Address:      {nav_addr:<50,} ║")
        print("╠══════════════════════════════════════════════════════════════════╣")
        print("║  Encoding:")
        for p in PRIMS:
            v = NAVIGATOR_TUPLE[p]
            g = GRAMMAR_TUPLE[p]
            diff = " ←differs" if v != g else ""
            print(f"║    {p:6s}: {v:<20s}{diff}")
        print("╠══════════════════════════════════════════════════════════════════╣")
        print("║  Crystal structure:")
        print(f"║    Total types:    {TOTAL_SIZE:>12,}")
        print(f"║    Tier cells:     {CELL_SIZE:>12,}  (Φ×P×Ω×D = 5×5×4×4)")
        print(f"║    Inner types:    {INNER_SIZE:>12,}  per cell")
        print("║    Tier census:")
        for tier_name in ["O_inf", "O_2_dag", "O_2", "O_1", "O_0"]:
            cells = self._tier_map[tier_name]
            types = len(cells) * INNER_SIZE
            pct   = 100 * types / TOTAL_SIZE
            print(f"║      {tier_name:<10} {len(cells):3d} cells  {types:>10,} types  ({pct:.1f}%)")
        print(f"║    Catalog:        {len(self._catalog):>12,} entries")
        print("╚══════════════════════════════════════════════════════════════════╝")

    # ── Frobenius codec ────────────────────────────────────────────────────────

    def encode(self, tup: dict) -> int:
        """Frobenius encode (δ): tuple → canonical address."""
        return encode_tuple(tup)

    def decode(self, addr: int) -> dict:
        """Frobenius decode (μ): canonical address → tuple."""
        return decode_address(addr)

    def roundtrip(self, tup: dict) -> bool:
        """Verify Frobenius condition: decode(encode(tup)) == tup."""
        return decode_address(encode_tuple(tup)) == tup

    def codec_address(self, tup: dict) -> tuple[int, int, int]:
        """Return (cell_id, inner_id, full_address) for a tuple."""
        c = cell_address(tup)
        i = inner_address(tup)
        return c, i, c * INNER_SIZE + i

    # ── Holographic queries (boundary → bulk) ──────────────────────────────────

    def holographic_query(self, phi: str = None, p: str = None,
                           omega: str = None, d: str = None,
                           tier: str = None) -> list[TierCell]:
        """
        Boundary query: given any subset of (Φ, P, Ω, D, tier), return
        matching tier cells. The boundary encodes the bulk — each cell
        contains 43,200 inner types retrievable via cell.types().

        With no arguments: returns all 400 cells.
        """
        results = self._cells
        if phi   is not None: results = [c for c in results if c.phi   == phi]
        if p     is not None: results = [c for c in results if c.p     == p]
        if omega is not None: results = [c for c in results if c.omega == omega]
        if d     is not None: results = [c for c in results if c.d     == d]
        if tier  is not None: results = [c for c in results if c.tier  == tier]
        return results

    def cell_for(self, tup: dict) -> TierCell:
        """Return the tier cell containing a given tuple."""
        cid = cell_address(tup)
        return self._cell_map[cid]

    # ── Navigation (partial tuple → matching types) ────────────────────────────

    def navigate(self, limit: int = 20, **constraints: str) -> list[dict]:
        """
        Navigate the crystal: given any subset of the 12 primitives as keyword
        arguments, return up to `limit` matching complete tuples.

        Example:
            nav.navigate(Phi="Phi_c", P="P_pm_sym", limit=5)

        Broadcasts across all free coordinates (Γ_broad semantics).
        """
        inn_constraints = {k: v for k, v in constraints.items() if k in INNER_PRIMS}

        cells = self._cells
        if "Phi" in constraints:
            cells = [c for c in cells if c.phi == constraints["Phi"]]
        if "P" in constraints:
            cells = [c for c in cells if c.p == constraints["P"]]
        if "Omega" in constraints:
            cells = [c for c in cells if c.omega == constraints["Omega"]]
        if "D" in constraints:
            cells = [c for c in cells if c.d == constraints["D"]]

        count = 0
        results = []
        for cell in cells:
            for tup in cell.types():
                # Check inner constraints
                if all(tup.get(k) == v for k, v in inn_constraints.items()):
                    results.append(tup)
                    count += 1
                    if count >= limit:
                        return results
        return results

    def count(self, **constraints: str) -> int:
        """Count matching types without materializing them."""
        cells = self._cells
        if "Phi" in constraints:
            cells = [c for c in cells if c.phi == constraints["Phi"]]
        if "P" in constraints:
            cells = [c for c in cells if c.p == constraints["P"]]
        if "Omega" in constraints:
            cells = [c for c in cells if c.omega == constraints["Omega"]]
        if "D" in constraints:
            cells = [c for c in cells if c.d == constraints["D"]]

        inner_constraints = {k: v for k, v in constraints.items() if k in INNER_PRIMS}
        if not inner_constraints:
            return len(cells) * INNER_SIZE

        # Must count inner matches
        inner_free = 1
        for prim in INNER_PRIMS:
            if prim in inner_constraints:
                inner_free *= 1
            else:
                inner_free *= len(VALUES[prim])
        return len(cells) * inner_free

    # ── Tier queries ───────────────────────────────────────────────────────────

    def tier_census(self) -> dict[str, dict]:
        """Return full tier census with cell count, type count, percentage."""
        census = {}
        for tier_name in ["O_inf", "O_2_dag", "O_2", "O_1", "O_0"]:
            cells = self._tier_map[tier_name]
            types = len(cells) * INNER_SIZE
            census[tier_name] = {
                "cells": len(cells),
                "types": types,
                "pct":   100 * types / TOTAL_SIZE,
            }
        return census

    def tier_of(self, tup: dict) -> str:
        """Return the ouroboricity tier of a tuple."""
        return compute_tier(tup["Phi"], tup["P"], tup["Omega"], tup["D"])

    # ── Catalog nearest-neighbor ───────────────────────────────────────────────

    def nearest_catalog(self, tup: dict, n: int = 10,
                         same_tier: bool = False) -> list[dict]:
        """
        Return the n nearest catalog entries to a given tuple.
        Sorted by weighted Euclidean distance.
        If same_tier=True, restrict to entries with the same ouroboricity tier.
        """
        target_tier = self.tier_of(tup)
        results = []
        for entry in self._catalog:
            if same_tier and self.tier_of(entry) != target_tier:
                continue
            d = distance(tup, entry)
            results.append({"name": entry.get("name", "?"), "distance": d,
                             "tier": self.tier_of(entry), "entry": entry})
        results.sort(key=lambda r: r["distance"])
        return results[:n]

    def catalog_entry(self, name: str) -> Optional[dict]:
        """Look up a catalog entry by name."""
        for e in self._catalog:
            if e.get("name") == name:
                return e
        return None

    # ── Lattice operations (broadcast semantics) ───────────────────────────────

    def meet(self, a: dict, b: dict) -> dict:
        return meet(a, b)

    def join(self, a: dict, b: dict) -> dict:
        return join(a, b)

    def tensor(self, a: dict, b: dict) -> dict:
        return tensor(a, b)

    def distance(self, a: dict, b: dict) -> float:
        return distance(a, b)

    def directed_distance(self, a: dict, b: dict) -> float:
        return directed_distance(a, b)

    def breakdown(self, a: dict, b: dict) -> list[dict]:
        return breakdown(a, b)

    # ── Tier gap ladder (§69.1) ────────────────────────────────────────────────

    def tier_gap_ladder(self) -> dict[str, dict]:
        """
        Compute the tier gap ladder from §69.1:
        d(O_0,O_1), d(O_1,O_2), d(O_2,O_2†), d(O_2†,O_inf).
        Uses minimal representative tuples (canonical inner primitives).
        """
        canon_inner = {
            "T": "T_network", "R": "R_cat", "F": "F_ell",
            "K": "K_fast", "G": "G_beth", "Gamma": "G_and",
            "H": "H0", "S": "one_one",
        }
        reps = {
            "O_0":     {**canon_inner, "Phi": "Phi_sub",  "P": "P_asym",    "Omega": "Omega_0",  "D": "D_wedge"},
            "O_1":     {**canon_inner, "Phi": "Phi_c",    "P": "P_asym",    "Omega": "Omega_0",  "D": "D_wedge"},
            "O_2":     {**canon_inner, "Phi": "Phi_c",    "P": "P_asym",    "Omega": "Omega_Z2", "D": "D_triangle"},
            "O_2_dag": {**canon_inner, "Phi": "Phi_c",    "P": "P_asym",    "Omega": "Omega_Z2", "D": "D_infty"},
            "O_inf":   {**canon_inner, "Phi": "Phi_c",    "P": "P_pm_sym",  "Omega": "Omega_Z2", "D": "D_infty"},
        }
        ladder = {}
        pairs = [("O_0","O_1"), ("O_1","O_2"), ("O_2","O_2_dag"), ("O_2_dag","O_inf")]
        for lo, hi in pairs:
            d = distance(reps[lo], reps[hi])
            bd = breakdown(reps[lo], reps[hi])
            ladder[f"{lo}→{hi}"] = {
                "distance": d,
                "driver": bd[0]["primitive"] if bd else None,
                "breakdown": bd,
            }
        return ladder

    def print_tier_gap_ladder(self) -> None:
        """Print the tier gap ladder (§69.1)."""
        print("\nTIER GAP LADDER (§69.1)")
        print("─" * 60)
        ladder = self.tier_gap_ladder()
        for transition, data in ladder.items():
            d     = data["distance"]
            drv   = data["driver"]
            parts = ", ".join(
                f"{r['primitive']}({r['from']}→{r['to']})"
                for r in data["breakdown"]
            )
            print(f"  {transition:<18}  d = {d:.4f}  [{parts}]")
        print()
        gaps = [v["distance"] for v in ladder.values()]
        frobenius_gap = gaps[-1]
        others_sum    = sum(gaps[:-1])
        print(f"  Frobenius cliff:  {frobenius_gap:.4f}  (vs others combined: {others_sum:.4f})")
        print(f"  Cliff ratio:      {frobenius_gap/max(gaps[:-1]):.3f}×  the next-largest gap")

    # ── Frobenius roundtrip verification ──────────────────────────────────────

    def verify_codec(self, sample_size: int = 1000) -> bool:
        """
        Verify the Frobenius codec (μ∘δ = id) on a sample of addresses.
        Tests decode(encode(decode(addr))) == decode(addr) for sample_size addresses.
        """
        import random
        errors = 0
        for _ in range(sample_size):
            addr = random.randint(0, TOTAL_SIZE - 1)
            tup  = decode_address(addr)
            recovered = encode_tuple(tup)
            if recovered != addr:
                errors += 1
        print(f"Frobenius codec verification: {sample_size} samples, {errors} errors")
        return errors == 0

    # ── Interactive REPL ───────────────────────────────────────────────────────

    def repl(self) -> None:
        """Interactive crystal navigation REPL."""
        print("\nCRYSTAL NAVIGATOR — Interactive Mode")
        print("Commands: describe | tier <name> | cell <Phi> <P> <Omega> <D> |")
        print("          encode <k=v ...> | decode <addr> | nearest <k=v ...> |")
        print("          gap | verify | count <k=v ...> | quit")
        print()
        while True:
            try:
                line = input("nav> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting navigator.")
                break
            if not line:
                continue
            parts = line.split()
            cmd   = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                break

            elif cmd == "describe":
                self.describe()

            elif cmd == "gap":
                self.print_tier_gap_ladder()

            elif cmd == "verify":
                n = int(parts[1]) if len(parts) > 1 else 1000
                self.verify_codec(n)

            elif cmd == "tier":
                name = parts[1] if len(parts) > 1 else None
                if name:
                    cells = self._tier_map.get(name, [])
                    print(f"  {name}: {len(cells)} tier cells, {len(cells)*INNER_SIZE:,} types")
                    for c in cells[:10]:
                        print(f"    {c}")
                    if len(cells) > 10:
                        print(f"    ... and {len(cells)-10} more")
                else:
                    for tier_name, data in self.tier_census().items():
                        print(f"  {tier_name:<12} {data['cells']:3d} cells  "
                              f"{data['types']:>10,} types  ({data['pct']:.1f}%)")

            elif cmd == "cell":
                if len(parts) >= 5:
                    phi, p, omega, d = parts[1], parts[2], parts[3], parts[4]
                    cells = self.holographic_query(phi=phi, p=p, omega=omega, d=d)
                    if cells:
                        c = cells[0]
                        print(f"  {c}")
                        print(f"  Tier: {c.tier}  |  Cell ID: {c.cell_id}  |  Inner types: {INNER_SIZE:,}")
                        print(f"  First 3 inner types:")
                        for i, t in enumerate(c.types()):
                            if i >= 3:
                                break
                            print(f"    addr={c.cell_id*INNER_SIZE+i}  {t}")
                    else:
                        print("  No matching cell.")

            elif cmd == "encode":
                kwargs = dict(kv.split("=") for kv in parts[1:] if "=" in kv)
                # Fill missing with navigator defaults
                tup = {**NAVIGATOR_TUPLE, **kwargs}
                if all(p in tup for p in PRIMS):
                    addr = self.encode(tup)
                    tier = self.tier_of(tup)
                    cell_id, inner_id, _ = self.codec_address(tup)
                    print(f"  Address:  {addr:,}")
                    print(f"  Cell:     {cell_id}  (boundary: Phi={tup['Phi']}, P={tup['P']}, "
                          f"Omega={tup['Omega']}, D={tup['D']})")
                    print(f"  Inner:    {inner_id}")
                    print(f"  Tier:     {tier}")
                    rt = self.roundtrip(tup)
                    print(f"  Roundtrip: {'✓ VALID' if rt else '✗ FAIL'}")
                else:
                    print("  Incomplete tuple. Provide all 12 primitives as k=v pairs.")

            elif cmd == "decode":
                if len(parts) > 1:
                    addr = int(parts[1].replace(",", ""))
                    if 0 <= addr < TOTAL_SIZE:
                        tup = self.decode(addr)
                        tier = self.tier_of(tup)
                        print(f"  Address {addr:,} → tier {tier}")
                        for p in PRIMS:
                            print(f"    {p:6s}: {tup[p]}")
                    else:
                        print(f"  Address out of range [0, {TOTAL_SIZE-1:,}]")

            elif cmd == "nearest":
                kwargs = dict(kv.split("=") for kv in parts[1:] if "=" in kv)
                tup = {**NAVIGATOR_TUPLE, **kwargs}
                n = int(kwargs.get("n", 5))
                results = self.nearest_catalog(tup, n=n)
                tier = self.tier_of(tup)
                print(f"  Query tier: {tier}")
                for r in results:
                    print(f"    d={r['distance']:.4f}  [{r['tier']}]  {r['name']}")

            elif cmd == "count":
                kwargs = dict(kv.split("=") for kv in parts[1:] if "=" in kv)
                n = self.count(**kwargs)
                print(f"  {n:,} matching types")

            else:
                print(f"  Unknown command: {cmd}")


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Crystal Navigator — Crystal of Types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("describe",  help="Print navigator self-description and crystal stats")
    sub.add_parser("gap",       help="Print tier gap ladder (§69.1)")
    sub.add_parser("verify",    help="Verify Frobenius codec roundtrip")
    sub.add_parser("repl",      help="Interactive navigation REPL")
    sub.add_parser("census",    help="Full tier census")

    enc = sub.add_parser("encode", help="Encode a tuple to canonical address")
    enc.add_argument("kvs", nargs="*", help="primitive=value pairs")

    dec = sub.add_parser("decode", help="Decode canonical address to tuple")
    dec.add_argument("address", type=int)

    nrst = sub.add_parser("nearest", help="Nearest catalog entries to a tuple")
    nrst.add_argument("kvs", nargs="*", help="primitive=value pairs")
    nrst.add_argument("-n", type=int, default=10)

    cnt = sub.add_parser("count", help="Count matching types")
    cnt.add_argument("kvs", nargs="*", help="primitive=value pairs")

    args = parser.parse_args()
    nav  = CrystalNavigator()

    if args.command == "describe" or args.command is None:
        nav.describe()

    elif args.command == "gap":
        nav.print_tier_gap_ladder()

    elif args.command == "verify":
        nav.verify_codec(10000)

    elif args.command == "repl":
        nav.describe()
        nav.repl()

    elif args.command == "census":
        print("\nFULL TIER CENSUS")
        print("─" * 50)
        for tier_name, data in nav.tier_census().items():
            print(f"  {tier_name:<12} {data['cells']:3d} cells  "
                  f"{data['types']:>10,} types  ({data['pct']:.1f}%)")

    elif args.command == "encode":
        kwargs = dict(kv.split("=") for kv in args.kvs if "=" in kv)
        tup = {**NAVIGATOR_TUPLE, **kwargs}
        addr = nav.encode(tup)
        tier = nav.tier_of(tup)
        cell_id, inner_id, _ = nav.codec_address(tup)
        print(f"Address:  {addr:,}")
        print(f"Cell:     {cell_id}  (Phi={tup['Phi']}, P={tup['P']}, "
              f"Omega={tup['Omega']}, D={tup['D']})")
        print(f"Inner:    {inner_id}")
        print(f"Tier:     {tier}")
        print(f"Roundtrip: {'✓' if nav.roundtrip(tup) else '✗'}")

    elif args.command == "decode":
        tup = nav.decode(args.address)
        tier = nav.tier_of(tup)
        print(f"Address {args.address:,} → tier {tier}")
        for p in PRIMS:
            print(f"  {p:6s}: {tup[p]}")

    elif args.command == "nearest":
        kwargs = dict(kv.split("=") for kv in args.kvs if "=" in kv)
        tup = {**NAVIGATOR_TUPLE, **kwargs}
        results = nav.nearest_catalog(tup, n=args.n)
        tier = nav.tier_of(tup)
        print(f"Query tier: {tier}")
        for r in results:
            print(f"  d={r['distance']:.4f}  [{r['tier']}]  {r['name']}")

    elif args.command == "count":
        kwargs = dict(kv.split("=") for kv in args.kvs if "=" in kv)
        print(f"{nav.count(**kwargs):,} matching types")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "repl":
        main()
    else:
        # Default: describe + REPL
        nav = CrystalNavigator()
        nav.describe()
        nav.print_tier_gap_ladder()
        nav.repl()
