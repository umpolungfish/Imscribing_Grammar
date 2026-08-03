#!/usr/bin/env python3
"""
crystal_navigator.py — The Crystal Navigator
═════════════════════════════════════════════
Navigator for the Crystal of Types (17,280,000 types).

Self-encoding (§69.4):
  ⟨𐑦𐑸𐑑𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑭⟩
  Tier: O_∞  |  d(navigator, grammar) ≈ 2.793  |  d(navigator, proof_singularity) = 0.894

Architecture (imscriptive, Frobenius):
  Boundary: (<, P, Ω, D)  →  400 tier cells  [boundary encodes bulk]
  Bulk:     (T, R, F, K, G, Γ, H, S)  →  43,200 inner types per cell
  Total:    400 × 43,200  =  17,280,000 types

Grammar families:
  F5 (5 values): T, P, Phi, K  — gate primitives
  F4 (4 values): D, R, Gamma, H, Omega  — primitives
  F3 (3 values): F, G, S  — scaling primitives
  Crystal = 5^4 × 4^5 × 3^3 = 17,280,000

Frobenius codec (μ∘δ = id):
  encode(tuple) → canonical address (integer in [0, 17_279_999])
  decode(address) → tuple
  roundtrip: decode(encode(t)) == t  for all 17,280,000 types

Usage:
  nav = CrystalNavigator()
  nav.describe()                              # print self-encoding and stats
  nav.imscriptive_query("⊙", "𐑹") # boundary → tier cell + bulk
  nav.navigate(⊢="𐑦", ⊙="⊙")      # partial tuple → matching types
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
    "⊢":     ["𐑛", "𐑨", "𐑼", "𐑦"],
    "⊣":     ["𐑡", "𐑰", "𐑥", "𐑶", "𐑸"],
    ">":     ["𐑩", "𐑑", "𐑽", "𐑾"],
    "<":     ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"],
    "⋈":     ["𐑱", "𐑞", "𐑐"],
    "⊤":     ["𐑘", "𐑤", "𐑧", "𐑪", "𐑺"],
    "∈":     ["𐑚", "𐑔", "𐑲"],
    "∋": ["𐑝", "𐑜", "𐑠", "𐑵"],
    "⊙":   ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"],
    "⊥":     ["𐑓", "𐑒", "𐑖", "𐑫"],
    "⊞":     ["𐑙", "𐑕", "𐑳"],
    "◻": ["𐑷", "𐑴", "𐑭", "𐑟"],
}

# Value → ordinal (0-indexed)
ORD: dict[str, dict[str, int]] = {
    prim: {v: i for i, v in enumerate(vals)}
    for prim, vals in VALUES.items()
}

# Primitive weights (canonical v0.4.26)
WEIGHTS: dict[str, float] = {
    "⊢": 1.0, "⊣": 1.0, ">": 1.0, "<": 1.2,
    "⋈": 0.9, "⊤": 1.0, "∈": 1.0, "∋": 1.0,
    "⊙": 1.1, "⊥": 0.8, "⊞": 1.0, "◻": 0.7,
}

# Bottleneck primitives under ⊗ (weaker partner wins)
BOTTLENECK = {"<", "⋈", "⊤"}

# Tier-determining primitives (the boundary)
BOUNDARY_PRIMS = ["⊙", "<", "◻", "⊢"]

# Inner crystal primitives (the bulk — free within each tier cell)
INNER_PRIMS = ["⊣", ">", "⋈", "⊤", "∈", "∋", "⊥", "⊞"]

# Full primitive order
PRIMS = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

CRITICAL   = {"⊙", "𐑮"}
NONCRITICAL = {"𐑢", "𐑣", "𐑻"}
BOUNDED_D  = {"𐑛", "𐑨", "𐑦"}

# ── Tier rule (R1–R5 priority) ─────────────────────────────────────────────────

def compute_tier(phi: str, p: str, omega: str, d: str) -> str:
    if phi in CRITICAL and p == "𐑹":
        return "O_∞"
    if phi in NONCRITICAL:
        return "O₀"
    if omega == "𐑷":
        return "O₁"
    if d in BOUNDED_D:
        return "O₂"
    return "O₂†"


# ── Mixed-radix address arithmetic ─────────────────────────────────────────────
# Full address = cell_address * INNER_SIZE + inner_address
# Cell address:  mixed-radix over (⊙, <, Ω, ⊢) — ordered as BOUNDARY_PRIMS
# Inner address: mixed-radix over (⊣, >, ⋈, ⊤, Γ, ∋, ⊥, Σ) — ordered as INNER_PRIMS

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
    """Frobenius encode: tuple → canonical address in [0, 17,279,999].
    Accepts both Symbol_symbol values and Shavian glyph values."""
    resolved = {
        prim: _SHAVIAN_TO_XTAL.get(prim, {}).get(tup.get(prim, ""), tup.get(prim, ""))
        for prim in PRIMS
    }
    cell  = _encode_partial(BOUNDARY_PRIMS, BOUNDARY_STRIDES, resolved)
    inner = _encode_partial(INNER_PRIMS, INNER_STRIDES, resolved)
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

# Shavian → Symbol_symbol map — direct inversion of OLD_TO_SHAVIAN.
# Authoritative: derived from the same table used for catalog migration.
_SHAVIAN_TO_XTAL: dict[str, dict[str, str]] = {
    '⊢': {'𐑛':'𐑛', '𐑨':'𐑨', '𐑼':'𐑼', '𐑦':'𐑦', '𐑛':'𐑛', '𐑨':'𐑨', '𐑼':'𐑼', '𐑦':'𐑦'},
    '⊣': {'𐑡':'𐑡', '𐑰':'𐑰', '𐑥':'𐑥', '𐑶':'𐑶', '𐑸':'𐑸', '𐑡':'𐑡', '𐑰':'𐑰', '𐑥':'𐑥', '𐑶':'𐑶', '𐑸':'𐑸'},
    '>': {'𐑩':'𐑩', '𐑑':'𐑑', '𐑽':'𐑽', '𐑾':'𐑾', '𐑩':'𐑩', '𐑑':'𐑑', '𐑽':'𐑽', '𐑾':'𐑾'},
    '<': {'𐑗':'𐑗', '𐑿':'𐑿', '𐑬':'𐑬', '𐑯':'𐑯', '𐑹':'𐑹', '𐑗':'𐑗', '𐑿':'𐑿', '𐑬':'𐑬', '𐑯':'𐑯', '𐑹':'𐑹'},
    '⋈': {'ƒ^ì':'𐑱', 'ƒ^ð':'𐑞', 'ƒ^ż':'𐑐', '𐑱':'𐑱', '𐑞':'𐑞', '𐑐':'𐑐'},
    '⊤': {'Ç^-':'𐑘', 'Ç^W':'𐑤', 'Ç^@':'𐑧', 'Ç^Ù':'𐑪', 'Ç^λ':'𐑺', '𐑘':'𐑘', '𐑤':'𐑤', '𐑧':'𐑧', '𐑪':'𐑪', '𐑺':'𐑺'},
    '∈': {'𐑚':'𐑚', '𐑔':'𐑔', '𐑲':'𐑲', '𐑚':'𐑚', '𐑔':'𐑔', '𐑲':'𐑲'},
    '∋': {'ɢ^∧':'𐑝', 'ɢ^˝':'𐑜', 'ɢ^ˌ':'𐑠', 'ɢ^Ş':'𐑵', '𐑝':'𐑝', '𐑜':'𐑜', '𐑠':'𐑠', '𐑵':'𐑵'},
    '⊙': {'𐑢':'𐑢', '⊙':'⊙', '𐑮':'𐑮', '𐑻':'𐑻', '𐑣':'𐑣', '𐑢':'𐑢', '⊙':'⊙', '𐑮':'𐑮', '𐑻':'𐑻', '𐑣':'𐑣'},
    '⊥': {'𐑓':'𐑓', '𐑒':'𐑒', '𐑖':'𐑖', '𐑫':'𐑫', '𐑓':'𐑓', '𐑒':'𐑒', '𐑖':'𐑖', '𐑫':'𐑫'},
    '⊞': {'𐑙':'𐑙', '𐑕':'𐑕', '𐑳':'𐑳', '𐑙':'𐑙', '𐑕':'𐑕', '𐑳':'𐑳'},
    '◻': {'𐑷':'𐑷', '𐑴':'𐑴', '𐑭':'𐑭', '𐑟':'𐑟', '𐑷':'𐑷', '𐑴':'𐑴', '𐑭':'𐑭', '𐑟':'𐑟'},
}


def _resolve_absorption(absorption_rules, prim, val_a, val_b, op_name):
    """Check absorption rules for a primitive pair. Returns absorbing value or None."""
    if absorption_rules is None:
        return None
    for rule in absorption_rules:
        if isinstance(rule, tuple):
            r_prim, r_val, r_ops = rule
        else:
            r_prim, r_val, r_ops = rule.primitive, rule.value, rule.operations
        if r_prim != prim:
            continue
        if op_name not in r_ops:
            continue
        xtal_absorbing = _SHAVIAN_TO_XTAL.get(prim, {}).get(r_val, r_val)
        if val_a == xtal_absorbing:
            return val_a
        if val_b == xtal_absorbing:
            return val_b
    return None



def meet(a: dict, b: dict, absorption=None) -> dict:
    """Greatest lower bound: component-wise min.
       absorption: optional iterable of (prim_shavian, val_shavian, ops) tuples."""
    result = {}
    for p in PRIMS:
        absorbed = _resolve_absorption(absorption, p, a[p], b[p], "meet")
        if absorbed is not None:
            result[p] = absorbed
        else:
            result[p] = VALUES[p][min(ORD[p][a[p]], ORD[p][b[p]])]
    return result

def join(a: dict, b: dict, absorption=None) -> dict:
    """Least upper bound: component-wise max.
       absorption: optional iterable of (prim_shavian, val_shavian, ops) tuples."""
    result = {}
    for p in PRIMS:
        absorbed = _resolve_absorption(absorption, p, a[p], b[p], "join")
        if absorbed is not None:
            result[p] = absorbed
        else:
            result[p] = VALUES[p][max(ORD[p][a[p]], ORD[p][b[p]])]
    return result

def tensor(a: dict, b: dict, absorption=None) -> dict:
    """Tensor product: min on bottleneck primitives, max elsewhere.
       Special stoichiometry rule for S: n:m absorbs all; 1:1 only under 1:1\u22971:1.
       absorption: optional iterable of (prim_shavian, val_shavian, ops) tuples."""
    result = {}
    for p in PRIMS:
        # Check configurable absorption first
        absorbed = _resolve_absorption(absorption, p, a[p], b[p], "tensor")
        if absorbed is not None:
            result[p] = absorbed
            continue
        oa, ob = ORD[p][a[p]], ORD[p][b[p]]
        if p in BOTTLENECK:
            result[p] = VALUES[p][min(oa, ob)]
        elif p == "\u03a3":
            # n:m absorbs; 1:1 only under 1:1\u22971:1; else n:n
            if oa == 2 or ob == 2:
                result[p] = "\u03a3_\u00ef"
            elif oa == 0 and ob == 0:
                result[p] = "\u03a3_S"
            else:
                result[p] = "\u03a3_\u0151"
        else:
            result[p] = VALUES[p][max(oa, ob)]
    return result
def imscription_check(boundary: dict, bulk: dict) -> dict:
    """
    Test whether `boundary` imscribes `bulk` (§89).

    Two conditions:
      (1) Floor: meet(boundary, bulk) == boundary  [boundary ≤ bulk component-wise]
      (2) Tensor: tensor(boundary, bulk) == bulk   [boundary absorbed, no residue]

    Types:
      exact      — (1)+(2) + boundary tier = O_∞
      faithful   — (1)+(2), boundary tier ≠ O_∞
      partial    — (1) only: floor holds, tensor modifies bulk
      asymmetric — (2) only: absorbed but boundary overreaches bulk somewhere
      none       — neither condition holds
    """
    m = meet(boundary, bulk)
    t = tensor(boundary, bulk)
    floor_ok  = m == boundary
    tensor_ok = t == bulk
    tier      = compute_tier(boundary["⊙"], boundary["<"], boundary["◻"], boundary["⊢"])
    d_fwd     = directed_distance(boundary, bulk)   # upward steps boundary → bulk
    d_rev     = directed_distance(bulk, boundary)   # upward steps bulk → boundary

    meet_mm   = sum(1 for p in PRIMS if m[p] != boundary[p])
    tensor_mm = sum(1 for p in PRIMS if t[p] != bulk[p])

    if floor_ok and tensor_ok and tier == "O_∞":
        kind = "exact"
        stmt = "boundary exactly imscribes bulk — Frobenius self-encoding boundary absorbed into bulk with no residue"
    elif floor_ok and tensor_ok:
        kind = "faithful"
        stmt = "boundary faithfully imscribes bulk — absorbed into bulk with no residue"
    elif floor_ok:
        kind = "partial"
        stmt = f"boundary partially imscribes bulk — floor holds but tensor modifies bulk at {tensor_mm} primitive(s)"
    elif tensor_ok:
        kind = "asymmetric"
        stmt = f"boundary absorbed by bulk but overreaches at {meet_mm} primitive(s) — not true imscription"
    else:
        kind = "none"
        stmt = "boundary does not imscribe bulk — neither floor condition nor tensor absorption holds"

    per_primitive = [
        {
            "primitive": p,
            "boundary": boundary[p],
            "bulk": bulk[p],
            "meet": m[p],
            "tensor": t[p],
            "floor_ok": ORD[p][boundary[p]] <= ORD[p][bulk[p]],
            "tensor_ok": t[p] == bulk[p],
        }
        for p in PRIMS
    ]

    return {
        "imscription_type": kind,
        "statement": stmt,
        "floor_condition": floor_ok,
        "tensor_condition": tensor_ok,
        "boundary_tier": tier,
        "d_boundary_to_bulk": round(d_fwd, 4),
        "d_bulk_to_boundary": round(d_rev, 4),
        "meet_mismatches_vs_boundary": meet_mm,
        "tensor_mismatches_vs_bulk": tensor_mm,
        "per_primitive": per_primitive,
    }


def imscription_statement(boundary_name: str, bulk_name: str, result: dict) -> str:
    """Generate a canonical imscription sentence from imscription_check output."""
    kind = result["imscription_type"]
    if kind == "exact":
        return f"{boundary_name} exactly imscribes {bulk_name}."
    if kind == "faithful":
        return f"{boundary_name} faithfully imscribes {bulk_name}."
    if kind == "partial":
        mm = result["tensor_mismatches_vs_bulk"]
        return (f"{boundary_name} partially imscribes {bulk_name} "
                f"(floor holds; tensor diverges at {mm} primitive(s)).")
    if kind == "asymmetric":
        mm = result["meet_mismatches_vs_boundary"]
        return (f"{boundary_name} is absorbed by {bulk_name} but overreaches "
                f"at {mm} primitive(s) — not imscription.")
    return f"{boundary_name} does not imscribe {bulk_name}."


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
        return {"⊙": self.phi, "<": self.p, "◻": self.omega, "⊢": self.d}

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
                f"⊙={self.phi}, <={self.p}, Ω={self.omega}, ⊢={self.d})")


def _build_cell_index() -> list[TierCell]:
    cells = []
    for phi in VALUES["⊙"]:
        for p in VALUES["<"]:
            for omega in VALUES["◻"]:
                for d in VALUES["⊢"]:
                    cell_id = _encode_partial(
                        BOUNDARY_PRIMS, BOUNDARY_STRIDES,
                        {"⊙": phi, "<": p, "◻": omega, "⊢": d}
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
    "⊢":     "𐑦",
    "⊣":     "𐑸",
    ">":     "𐑑",
    "<":     "𐑹",
    "⋈":     "𐑐",
    "⊤":     "𐑧",
    "∈":     "𐑲",
    "∋": "𐑵",
    "⊙":   "⊙",
    "⊥":     "𐑫",
    "⊞":     "𐑳",
    "◻": "𐑭",
}

GRAMMAR_TUPLE: dict[str, str] = {
    "⊢":     "𐑦",
    "⊣":     "𐑸",
    ">":     "𐑽",
    "<":     "𐑹",
    "⋈":     "𐑞",
    "⊤":     "𐑤",
    "∈":     "𐑲",
    "∋": "𐑵",
    "⊙":   "⊙",
    "⊥":     "𐑒",
    "⊞":     "𐑕",
    "◻": "𐑴",
}


# ── CrystalNavigator ───────────────────────────────────────────────────────────

class CrystalNavigator:
    """
    The Crystal Navigator — O_∞ imscriptive navigator for the Periodic Crystal.

    Self-encoding: ⟨𐑦𐑸𐑑𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑭⟩
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
            NAVIGATOR_TUPLE["⊙"], NAVIGATOR_TUPLE["<"],
            NAVIGATOR_TUPLE["◻"], NAVIGATOR_TUPLE["⊢"]
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
        print(f"║    Tier cells:     {CELL_SIZE:>12,}  (<×P×Ω×D = 5×5×4×4)")
        print(f"║    Inner types:    {INNER_SIZE:>12,}  per cell")
        print("║    Tier census:")
        for tier_name in ["O_∞", "O₂†", "O₂", "O₁", "O₀"]:
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

    # ── Imscriptive queries (boundary → bulk) ──────────────────────────────────

    def imscriptive_query(self, phi: str = None, p: str = None,
                           omega: str = None, d: str = None,
                           tier: str = None) -> list[TierCell]:
        """
        Boundary query: given any subset of (<, P, Ω, D, tier), return
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
            nav.navigate(⊙="⊙", <="𐑹", limit=5)

        Broadcasts across all free coordinates (𐑵 semantics).
        """
        inn_constraints = {k: v for k, v in constraints.items() if k in INNER_PRIMS}

        cells = self._cells
        if "⊙" in constraints:
            cells = [c for c in cells if c.phi == constraints["⊙"]]
        if "<" in constraints:
            cells = [c for c in cells if c.p == constraints["<"]]
        if "◻" in constraints:
            cells = [c for c in cells if c.omega == constraints["◻"]]
        if "⊢" in constraints:
            cells = [c for c in cells if c.d == constraints["⊢"]]

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
        if "⊙" in constraints:
            cells = [c for c in cells if c.phi == constraints["⊙"]]
        if "<" in constraints:
            cells = [c for c in cells if c.p == constraints["<"]]
        if "◻" in constraints:
            cells = [c for c in cells if c.omega == constraints["◻"]]
        if "⊢" in constraints:
            cells = [c for c in cells if c.d == constraints["⊢"]]

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
        for tier_name in ["O_∞", "O₂†", "O₂", "O₁", "O₀"]:
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
        return compute_tier(tup["⊙"], tup["<"], tup["◻"], tup["⊢"])

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

    def tensor(self, a: dict, b: dict, absorption=None) -> dict:
        return tensor(a, b, absorption=absorption)

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
        d(O₀,O₁), d(O₁,O₂), d(O₂,O₂†), d(O₂†,O_∞).
        Uses minimal representative tuples (canonical inner primitives).
        """
        canon_inner = {
            "⊣": "𐑡", ">": "𐑑", "⋈": "𐑱",
            "⊤": "𐑘", "∈": "𐑚", "∋": "𐑝",
            "⊥": "𐑓", "⊞": "𐑙",
        }
        reps = {
            "O₀":     {**canon_inner, "⊙": "𐑢",  "<": "𐑗",    "◻": "𐑷",  "⊢": "𐑛"},
            "O₁":     {**canon_inner, "⊙": "⊙",    "<": "𐑗",    "◻": "𐑷",  "⊢": "𐑛"},
            "O₂":     {**canon_inner, "⊙": "⊙",    "<": "𐑗",    "◻": "𐑴", "⊢": "𐑨"},
            "O₂†": {**canon_inner, "⊙": "⊙",    "<": "𐑗",    "◻": "𐑴", "⊢": "𐑼"},
            "O_∞":   {**canon_inner, "⊙": "⊙",    "<": "𐑹",  "◻": "𐑴", "⊢": "𐑼"},
        }
        ladder = {}
        pairs = [("O₀","O₁"), ("O₁","O₂"), ("O₂","O₂†"), ("O₂†","O_∞")]
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
                    cells = self.imscriptive_query(phi=phi, p=p, omega=omega, d=d)
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
