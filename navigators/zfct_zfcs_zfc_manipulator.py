#!/usr/bin/env python3
"""
zfct_zfcs_zfc_manipulator.py — ZFC / ZFCₜ / ZFCₛ triangle manipulator.

Extends the ZFCₜ manipulator with:
  • Corrected tensorProduct: min for Φ and ƒ, max for all others (matches Lean)
  • join_tuples: pure component-wise max (lattice join, no pol/fid bottleneck)
  • Corrected ZFC entry: 𐑼 (𐑼), ⊙ (⊙)  — navigator had 𐑨, 𐑢
  • Corrected ZFCₜ entry: 𐑹 (𐑹, O_inf)        — navigator had 𐑬 (O_2†)
  • ZFCₛ (spatial extension of ZFC, 5 promotions, O_inf)
  • ZFCₛₜ = ZFCₛ ⊗ ZFCₜ = ZFCₜ (temporal dominates)
  • Imaginary numbers: imaginary_unit (O_2), complex_time_path_integral (O_inf),
    planck_imaginary_time (O_2†)

Lattice structure (chain, not diamond): ZFC < ZFCₛ < ZFCₜ = ZFCₛₜ

New commands:
  :join <A> <B>        lattice join — pure max, no pol/fid bottleneck
  :lattice             ZFC / ZFCₛ / ZFCₜ / ZFCₛₜ chain with tiers and distances
  :promotions-dual     ZFC→ZFCₜ vs ZFC→ZFCₛ side-by-side
  :cliff [name]        Frobenius cliff analysis
"""

import sys
import math
import random
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))
from zfct_navigator import (
    PRIMITIVES, ORDINALS, INV_ORDINALS, WEIGHTS,
    ZFCT_TEMPLATES, TOKEN2IDX, IDX2TOKEN,
    tuple_distance, compose_formula, _normalize_entry, render_tokens,
    load_catalog, _PROMOTION_ATOMS, ZFCT_REFERENCE_ENTRIES,
    _PRIM_ALIASES,
)

# The navigator aliases 𐑯 → 𐑹 (𐑿 → 𐑹), which is incorrect:
# 𐑿 (U(1) phase) is ord 3, 𐑹 (Frobenius) is ord 4 — they are distinct.
_SAFE_ALIASES = {
    p: {k: v for k, v in aliases.items() if not (p == "Φ" and k == "𐑯")}
    for p, aliases in _PRIM_ALIASES.items()
}

def _normalize(entry: dict) -> dict:
    out = dict(entry)
    for prim, aliases in _SAFE_ALIASES.items():
        if prim in out and out[prim] in aliases:
            out[prim] = aliases[out[prim]]
    return out
from zfct_manipulator import (
    TIER_LABELS, TIER_ORDER, TIER_COLOR, compute_tier,
    meet_tuples, lift_tuple,
    all_tokens, promotion_atoms_present, has_frob, has_fixpt,
    RuleExtractor,
)


# ── Corrected entries ─────────────────────────────────────────────────────────
# All values verified against ~/MillenniumAnkh/Primitives/ZFCt.lean and ZFCs.lean.

ZFC_TUPLE = {
    "name": "ZFC_foundations",
    "description": "Zermelo-Fraenkel set theory with Choice (corrected: 𐑼, ⊙)",
    "Ð": "𐑼",  "Þ": "𐑰",  "Ř": "𐑩",  "Φ": "𐑗",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑝",
    "⊙": "⊙", "Ħ": "𐑓",  "Σ": "𐑳",  "Ω": "𐑷",
}

ZFCT_TUPLE = {
    "name": "zfc_t",
    "description": "ZFCₜ: ZFC + sequential + chirality + winding (O_inf, Frobenius)",
    "Ð": "𐑼",  "Þ": "𐑸",  "Ř": "𐑾",  "Φ": "𐑹",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖",  "Σ": "𐑳",  "Ω": "𐑭",
}

ZFCS_TUPLE = {
    "name": "zfc_s",
    "description": "ZFCₛ: ZFC + spatial topology + Frobenius (𐑰, 𐑽, 5 promotions)",
    "Ð": "𐑼",  "Þ": "𐑶",  "Ř": "𐑽",  "Φ": "𐑹",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑜",
    "⊙": "⊙", "Ħ": "𐑓",  "Σ": "𐑳",  "Ω": "𐑭",
}

# ZFCₛₜ = ZFCₛ ⊗ ZFCₜ = ZFCₜ (temporal max-primitives dominate; pol no bottleneck)
ZFCST_TUPLE = {
    "name": "zfc_st",
    "description": "ZFCₛₜ = ZFCₛ ⊗ ZFCₜ = ZFCₜ (spacetime: temporal dominates spatial)",
    **{k: v for k, v in ZFCT_TUPLE.items() if k not in ("name", "description")},
}

IMAGINARY_UNIT_TUPLE = {
    "name": "imaginary_unit",
    "description": "i — U(1) phase rotation; O_2 (𐑨, 𐑿); Frobenius cliff dist=5 from ZFCₜ",
    "Ð": "𐑨",   "Þ": "𐑥",  "Ř": "𐑾",  "Φ": "𐑿",
    "ƒ": "𐑱",   "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "⊙",  "Ħ": "𐑖",  "Σ": "𐑙",  "Ω": "𐑭",
}

COMPLEX_TIME_PATH_INTEGRAL_TUPLE = {
    "name": "complex_time_path_integral",
    "description": "Euclidean path integral (Wick-rotated t→iτ); O_inf; 1 step from ZFCₜ (𐑥 vs 𐑸)",
    "Ð": "𐑼",  "Þ": "𐑥",  "Ř": "𐑾",  "Φ": "𐑹",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖",  "Σ": "𐑳",  "Ω": "𐑭",
}

PLANCK_IMAGINARY_TIME_TUPLE = {
    "name": "planck_imaginary_time",
    "description": "Imaginary time in QG (t→iτ); O_2; shares 𐑰+𐑽 spatial skeleton with ZFCₛ",
    "Ð": "𐑼",  "Þ": "𐑶",  "Ř": "𐑽",  "Φ": "𐑿",
    "ƒ": "𐑐",  "Ç": "𐑧",  "Γ": "𐑲",  "ɢ": "𐑠",
    "⊙": "𐑮", "Ħ": "𐑫",  "Σ": "𐑳",  "Ω": "𐑴",
}

SPECIAL_ENTRIES: Dict[str, dict] = {
    "zfc":  ZFC_TUPLE,  "ZFC": ZFC_TUPLE, "zfc_foundations": ZFC_TUPLE,
    "zfc_t": ZFCT_TUPLE, "zfct": ZFCT_TUPLE, "ZFCt": ZFCT_TUPLE,
    "zfc_s": ZFCS_TUPLE, "zfcs": ZFCS_TUPLE, "ZFCs": ZFCS_TUPLE,
    "zfc_st": ZFCST_TUPLE, "zfcst": ZFCST_TUPLE,
    "imaginary_unit": IMAGINARY_UNIT_TUPLE, "i": IMAGINARY_UNIT_TUPLE,
    "complex_time": COMPLEX_TIME_PATH_INTEGRAL_TUPLE,
    "ctpi": COMPLEX_TIME_PATH_INTEGRAL_TUPLE,
    "planck_imaginary_time": PLANCK_IMAGINARY_TIME_TUPLE,
    "pit": PLANCK_IMAGINARY_TIME_TUPLE,
}

REFERENCE_ENTRIES = [
    ZFC_TUPLE, ZFCT_TUPLE, ZFCS_TUPLE, ZFCST_TUPLE,
    IMAGINARY_UNIT_TUPLE, COMPLEX_TIME_PATH_INTEGRAL_TUPLE, PLANCK_IMAGINARY_TIME_TUPLE,
] + [e for e in ZFCT_REFERENCE_ENTRIES
     if e.get("name") not in {e["name"] for e in [ZFC_TUPLE, ZFCT_TUPLE]}]


# ── Promotion channels ────────────────────────────────────────────────────────

ZFCT_PROMOTIONS: List[Tuple[str, str, str]] = [
    ("Þ", "𐑰", "𐑸"),   # 𐑡 → 𐑸
    ("Ř", "𐑩", "𐑾"),   # 𐑩   → 𐑾
    ("Φ", "𐑗", "𐑹"),   # 𐑗    → 𐑹   ← corrected
    ("ɢ", "𐑝", "𐑠"),   # 𐑝 → 𐑠
    ("Ħ", "𐑓", "𐑖"),   # 𐑓        → 𐑖
    ("Ω", "𐑷", "𐑭"),   # 𐑷   → 𐑭
]

ZFCS_PROMOTIONS: List[Tuple[str, str, str]] = [
    ("Þ", "𐑰", "𐑶"),   # 𐑡 → 𐑰
    ("Ř", "𐑩", "𐑽"),   # 𐑩   → 𐑽
    ("Φ", "𐑗", "𐑹"),   # 𐑗    → 𐑹
    ("ɢ", "𐑝", "𐑜"),   # 𐑝 → 𐑜
    ("Ω", "𐑷", "𐑭"),   # 𐑷   → 𐑭
]

_BOTTLENECK_PRIMS = {"Φ", "ƒ"}


# ── Corrected algebra ─────────────────────────────────────────────────────────

def tensor_tuples(a: dict, b: dict) -> dict:
    """Correct tensorProduct: min for Φ/ƒ (pol/fid bottleneck), max for all others.

    Matches Lean: tensorProduct takes min on pol and fid so that classical fidelity
    and non-Frobenius polarity cannot be upgraded by composition alone.
    """
    result = {}
    for p in PRIMITIVES:
        ao = ORDINALS[p][a[p]]
        bo = ORDINALS[p][b[p]]
        if p in _BOTTLENECK_PRIMS:
            result[p] = a[p] if ao <= bo else b[p]
        else:
            result[p] = a[p] if ao >= bo else b[p]
    return result


def join_tuples(a: dict, b: dict) -> dict:
    """Lattice join: pure component-wise max for all primitives (no bottleneck)."""
    return {p: (a[p] if ORDINALS[p][a[p]] >= ORDINALS[p][b[p]] else b[p])
            for p in PRIMITIVES}


def _count_mismatches(a: dict, b: dict) -> int:
    return sum(1 for p in PRIMITIVES if a[p] != b[p])


# ── Display helpers ────────────────────────────────────────────────────────────

HELP_TEXT = """
ZFC/ZFCₜ/ZFCₛ Manipulator — commands

  :lookup <name>              clause breakdown and tier
  :tier <name>                compute OuroboricityTier
  :tensor <A> <B>             corrected tensorProduct (min Φ/ƒ, max rest)
  :join <A> <B>               lattice join (pure max, no pol/fid bottleneck)
  :meet <A> <B>               lattice meet (pure min)
  :lift <name> <prim> <val>   set one primitive to val
  :compare <A> <B>            side-by-side comparison with Δ ordinal
  :barrier <A> <B>            Frobenius barrier analysis
  :distance <A> <B>           primitive mismatch count and weighted distance
  :lattice                    ZFC / ZFCₛ / ZFCₜ / ZFCₛₜ chain structure
  :promotions-dual            ZFC→ZFCₜ vs ZFC→ZFCₛ side-by-side
  :cliff [name]               Frobenius cliff analysis
  :scan <N>                   scan N random catalog pairs
  :rules                      composition rule set
  :special                    list special entries with tiers
  :list [pattern]             list catalog entries
  :help                       this message
  :quit                       exit

Special entries: zfc  zfc_t  zfc_s  zfc_st  imaginary_unit  complex_time  planck_imaginary_time
Aliases:         ZFC  zfct   zfcs   zfcst   i               ctpi           pit
Inline tuple:    𐑼,𐑸,𐑾,𐑹,𐑐,𐑧,𐑲,𐑠,⊙,𐑖,𐑳,𐑭  (12 comma-separated)
""".strip()


# ── Main manipulator class ────────────────────────────────────────────────────

class ZFCTriangleManipulator:
    def __init__(self, catalog_path: str = None):
        self.catalog_path = catalog_path
        self.catalog: List[dict] = []
        self._name_index: Dict[str, dict] = {}
        self.extractor = RuleExtractor()
        self._load()

    def _load(self):
        raw = load_catalog(self.catalog_path)
        ref_names = {e["name"] for e in REFERENCE_ENTRIES}
        self.catalog = REFERENCE_ENTRIES + [e for e in raw if e.get("name") not in ref_names]
        for e in self.catalog:
            n = e.get("name", "")
            if n:
                self._name_index[n.lower()] = e

    def _validate(self, t: dict) -> bool:
        return all(p in t and t[p] in ORDINALS[p] for p in PRIMITIVES)

    def resolve(self, name: str) -> Optional[dict]:
        if name in SPECIAL_ENTRIES:
            return _normalize(SPECIAL_ENTRIES[name])
        if name.count(",") == 11 and "_" in name:
            parts = name.split(",")
            try:
                t: dict = {}
                for i, p in enumerate(PRIMITIVES):
                    t[p] = parts[i].strip()
                    if t[p] not in ORDINALS[p]:
                        raise ValueError
                t["name"] = "inline"
                return t
            except (ValueError, IndexError):
                pass
        low = name.lower()
        if low in self._name_index:
            return _normalize(self._name_index[low])
        matches = [e for e in self.catalog if low in e.get("name", "").lower()]
        if matches:
            if len(matches) > 1:
                print(f"  [fuzzy] {len(matches)} matches — using '{matches[0]['name']}'")
            return _normalize(matches[0])
        return None

    def _not_found(self, name: str, console=None):
        msg = f"  [not found] '{name}' — try :special or :list"
        if console:
            console.print(f"[red]{msg}[/red]")
        else:
            print(msg)

    # ── command: lookup ───────────────────────────────────────────────────────

    def cmd_clauses(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return
        if not self._validate(e):
            print(f"  [error] '{name}' has missing/invalid primitives."); return
        tier = compute_tier(e)
        title = f"{e.get('name', '?')}  tier={tier}"
        if console:
            from rich.table import Table
            tbl = Table(title=title, show_header=True, header_style="bold cyan")
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column("Value", width=18)
            tbl.add_column("ZFCₜ clause")
            tbl.add_column("Promo atoms", style="magenta", width=14)
            for p in PRIMITIVES:
                val = e[p]
                frag = ZFCT_TEMPLATES[p][val]
                rendered = render_tokens(frag)
                promo = [t for t in frag if t in _PROMOTION_ATOMS]
                tbl.add_row(p, val, rendered, " ".join(promo) or "—")
            console.print(tbl)
            style = TIER_COLOR.get(tier, "white")
            console.print(f"  tier: [{style}]{TIER_LABELS.get(tier, tier)}[/{style}]")
        else:
            print(f"\n{title}")
            print(f"  {'Prim':<5}  {'Value':<18}  ZFCₜ clause")
            print(f"  {'─'*5}  {'─'*18}  {'─'*50}")
            for p in PRIMITIVES:
                val = e[p]
                frag = ZFCT_TEMPLATES[p][val]
                rendered = render_tokens(frag)
                promo = [t for t in frag if t in _PROMOTION_ATOMS]
                tag = "  [" + "+".join(promo) + "]" if promo else ""
                print(f"  {p:<5}  {val:<18}  {rendered[:50-len(tag)]:50}{tag}")
            print(f"  tier: {TIER_LABELS.get(tier, tier)}")

    # ── command: tier ─────────────────────────────────────────────────────────

    def cmd_tier(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return
        tier = compute_tier(e)
        style = TIER_COLOR.get(tier, "white")
        msg = f"tier({e.get('name','?')}) = {TIER_LABELS.get(tier, tier)}"
        if console:
            console.print(f"  [{style}]{msg}[/{style}]")
        else:
            print(f"  {msg}")

    # ── command: binary op (tensor / join / meet) ─────────────────────────────

    def cmd_binary(self, op: str, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a: self._not_found(name_a, console); return
        if not b: self._not_found(name_b, console); return
        if not (self._validate(a) and self._validate(b)):
            print("  [error] invalid primitives in one of the entries."); return

        if op == "tensor":
            result = tensor_tuples(a, b)
        elif op == "join":
            result = join_tuples(a, b)
        elif op == "meet":
            result = meet_tuples(a, b)
        else:
            raise ValueError(f"unknown op: {op}")

        result["name"] = f"{op}({a.get('name','A')},{b.get('name','B')})"
        a_tier = compute_tier(a)
        b_tier = compute_tier(b)
        r_tier = compute_tier(result)

        dist_ab = tuple_distance(a, b)
        dist_ar = tuple_distance(a, result)
        dist_br = tuple_distance(b, result)
        tier_emerged = TIER_ORDER[r_tier] > max(TIER_ORDER[a_tier], TIER_ORDER[b_tier])

        an = a.get("name","A"); bn = b.get("name","B")

        if console:
            from rich.table import Table
            tbl = Table(
                title=f"{op}({an[:16]}, {bn[:16]})",
                show_header=True, header_style="bold",
            )
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column(f"A: {an[:14]}", width=18)
            tbl.add_column(f"B: {bn[:14]}", width=18)
            tbl.add_column("Result", width=18, style="green")
            tbl.add_column("Src", width=5)
            tbl.add_column("Btlnk?", width=7)
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]; rv = result[p]
                src = "=" if av == bv else ("←A" if rv == av else "←B")
                bottleneck = (op == "tensor" and p in _BOTTLENECK_PRIMS
                              and ORDINALS[p][rv] < max(ORDINALS[p][av], ORDINALS[p][bv]))
                tbl.add_row(p, av, bv, rv, src, "[red]⊥[/red]" if bottleneck else "")
            console.print(tbl)
            as_ = TIER_COLOR.get(a_tier, "white")
            bs_ = TIER_COLOR.get(b_tier, "white")
            rs_ = TIER_COLOR.get(r_tier, "white")
            console.print(
                f"  tier(A)=[{as_}]{a_tier}[/{as_}]  "
                f"tier(B)=[{bs_}]{b_tier}[/{bs_}]  "
                f"→  tier(result)=[{rs_}]{r_tier}[/{rs_}]"
            )
            console.print(
                f"  d(A,B)={dist_ab:.3f}  d(A,result)={dist_ar:.3f}  d(B,result)={dist_br:.3f}"
            )
            if tier_emerged:
                console.print("[bold magenta]  ★ TIER EMERGENCE: result exceeds both inputs[/bold magenta]")
        else:
            print(f"\n{op}({an}, {bn})")
            print(f"  {'Prim':<5}  {'A':<18}  {'B':<18}  {'Result':<18}  Src  Btlnk")
            print(f"  {'─'*5}  {'─'*18}  {'─'*18}  {'─'*18}  {'─'*3}  {'─'*5}")
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]; rv = result[p]
                src = "=" if av == bv else ("←A" if rv == av else "←B")
                bottleneck = (op == "tensor" and p in _BOTTLENECK_PRIMS
                              and ORDINALS[p][rv] < max(ORDINALS[p][av], ORDINALS[p][bv]))
                print(f"  {p:<5}  {av:<18}  {bv:<18}  {rv:<18}  {src:<3}  {'⊥' if bottleneck else ''}")
            print(f"\n  tier(A)={a_tier}  tier(B)={b_tier}  → tier(result)={r_tier}")
            print(f"  d(A,B)={dist_ab:.3f}  d(A,result)={dist_ar:.3f}  d(B,result)={dist_br:.3f}")
            if tier_emerged:
                print("  *** TIER EMERGENCE: result tier exceeds both inputs! ***")

    # ── command: compare ──────────────────────────────────────────────────────

    def cmd_compare(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a: self._not_found(name_a, console); return
        if not b: self._not_found(name_b, console); return
        d = tuple_distance(a, b)
        n = _count_mismatches(a, b)
        a_tier = compute_tier(a); b_tier = compute_tier(b)
        an = a.get("name","A"); bn = b.get("name","B")
        if console:
            from rich.table import Table
            tbl = Table(
                title=f"compare: {an}  vs  {bn}  (d={d:.4f}, {n}/12 differ)",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim", width=5)
            tbl.add_column("A value", width=18)
            tbl.add_column("B value", width=18)
            tbl.add_column("Δ ord", width=6)
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]
                delta = int(ORDINALS[p][bv]) - int(ORDINALS[p][av])
                ds = f"{delta:+d}" if delta != 0 else "—"
                style = "green" if delta > 0 else ("red" if delta < 0 else "dim")
                avs = f"[bold]{av}[/bold]" if delta != 0 else av
                bvs = f"[bold]{bv}[/bold]" if delta != 0 else bv
                tbl.add_row(p, avs, bvs, f"[{style}]{ds}[/{style}]")
            console.print(tbl)
            as_ = TIER_COLOR.get(a_tier, "white")
            bs_ = TIER_COLOR.get(b_tier, "white")
            console.print(
                f"  tier(A)=[{as_}]{a_tier}[/{as_}]  "
                f"tier(B)=[{bs_}]{b_tier}[/{bs_}]  "
                f"d={d:.4f}  mismatches={n}/12"
            )
        else:
            print(f"\ncompare: {an}  vs  {bn}  (d={d:.4f}, {n}/12 differ)")
            print(f"  {'Prim':<5}  {'A value':<18}  {'B value':<18}  Δ ord")
            print(f"  {'─'*5}  {'─'*18}  {'─'*18}  {'─'*5}")
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]
                delta = int(ORDINALS[p][bv]) - int(ORDINALS[p][av])
                ds = f"{delta:+d}" if delta != 0 else "—"
                marker = " *" if delta != 0 else ""
                print(f"  {p:<5}  {av:<18}  {bv:<18}  {ds}{marker}")
            print(f"\n  tier(A)={a_tier}  tier(B)={b_tier}  d={d:.4f}  diffs={n}/12")

    # ── command: distance ─────────────────────────────────────────────────────

    def cmd_distance(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a: self._not_found(name_a, console); return
        if not b: self._not_found(name_b, console); return
        d = tuple_distance(a, b)
        n = _count_mismatches(a, b)
        msg = f"d({a.get('name','A')}, {b.get('name','B')}) = {d:.4f}  ({n}/12 primitives differ)"
        if console:
            console.print(f"  {msg}")
        else:
            print(f"  {msg}")

    # ── command: barrier ──────────────────────────────────────────────────────

    def cmd_barrier(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a: self._not_found(name_a, console); return
        if not b: self._not_found(name_b, console); return
        t_r = tensor_tuples(a, b)
        m_r = meet_tuples(a, b)
        a_frob = has_frob(a); b_frob = has_frob(b); t_frob = has_frob(t_r)
        a_fixpt = has_fixpt(a); b_fixpt = has_fixpt(b); t_fixpt = has_fixpt(t_r)
        a_tier = compute_tier(a); b_tier = compute_tier(b)
        t_tier = compute_tier(t_r); m_tier = compute_tier(m_r)
        phi_a = int(ORDINALS["Φ"][a["Φ"]]); phi_b = int(ORDINALS["Φ"][b["Φ"]])
        frob_gap = 4 - max(phi_a, phi_b)

        lines = [
            f"Frobenius barrier:  {a.get('name','A')}  ×  {b.get('name','B')}",
            "",
            f"  A    FROB={str(a_frob):<5}  FIXPT={str(a_fixpt):<5}  Φ={a['Φ']}  ⊙={a['⊙']}  tier={a_tier}",
            f"  B    FROB={str(b_frob):<5}  FIXPT={str(b_fixpt):<5}  Φ={b['Φ']}  ⊙={b['⊙']}  tier={b_tier}",
            f"  {'─'*60}",
            f"  ⊗    FROB={str(t_frob):<5}  FIXPT={str(t_fixpt):<5}  Φ={t_r['Φ']}  ⊙={t_r['⊙']}  tier={t_tier}",
            f"  ⊓    tier={m_tier}  Φ={m_r['Φ']}",
            "",
        ]
        if t_frob and not (a_frob or b_frob):
            lines += ["  !! BARRIER VIOLATION: FROB appeared in tensor without either input having it."]
        elif t_frob:
            src = "A" if a_frob else "B"
            lines += [
                f"  Barrier holds: FROB inherited from {src}.",
                f"  R-FROB-BARR satisfied: 𐑹 propagates forward under ⊗.",
            ]
        else:
            lines += [
                "  Barrier holds: neither input has FROB, tensor has none.",
                f"  Gap to Frobenius: {frob_gap} step(s) in Φ from current max (ord={max(phi_a,phi_b)}, need ord=4).",
            ]
        if t_tier == "O_inf" and a_tier != "O_inf" and b_tier != "O_inf":
            lines += [
                "",
                "  ★ TIER EMERGENCE to O_inf via FROB+FIXPT cross-clause conjunction.",
            ]
        if console:
            from rich.panel import Panel
            bstyle = ("bold magenta" if t_tier == "O_inf" else
                      "red" if (t_frob and not a_frob and not b_frob) else "cyan")
            console.print(Panel("\n".join(lines), title="[bold]Frobenius Barrier[/bold]", border_style=bstyle))
        else:
            for line in lines:
                print(line)

    # ── command: lift ─────────────────────────────────────────────────────────

    def cmd_lift(self, name: str, prim: str, val: str, console=None):
        e = self.resolve(name)
        if not e: self._not_found(name, console); return
        if prim not in ORDINALS:
            print(f"  [error] unknown primitive '{prim}'.  Valid: {', '.join(PRIMITIVES)}"); return
        if val not in ORDINALS[prim]:
            print(f"  [error] unknown value '{val}' for {prim}.  Valid: {', '.join(ORDINALS[prim])}"); return
        old_val = e[prim]; old_tier = compute_tier(e)
        result = lift_tuple(e, prim, val)
        new_tier = compute_tier(result)
        result["name"] = f"lift({e.get('name','?')},{prim}→{val})"
        delta = int(ORDINALS[prim][val]) - int(ORDINALS[prim][old_val])
        direction = "lift" if delta > 0 else ("degrade" if delta < 0 else "identity")
        msg = (f"  {direction}: {prim}: {old_val} (ord {int(ORDINALS[prim][old_val])}) "
               f"→ {val} (ord {int(ORDINALS[prim][val])})  Δ={delta:+d}")
        if old_tier != new_tier:
            msg += f"   tier: {old_tier} → {new_tier}"
        if console:
            console.print(msg)
        else:
            print(msg)
        self.cmd_clauses(result["name"] if result["name"] in SPECIAL_ENTRIES else "", console)
        self._show_clauses_dict(result, console)

    def _show_clauses_dict(self, e: dict, console=None):
        tier = compute_tier(e)
        if console:
            from rich.table import Table
            tbl = Table(title=f"{e.get('name','?')}  tier={tier}", show_header=True, header_style="bold cyan")
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column("Value", width=18)
            tbl.add_column("ZFCₜ clause")
            for p in PRIMITIVES:
                val = e[p]; frag = ZFCT_TEMPLATES[p][val]
                tbl.add_row(p, val, render_tokens(frag))
            console.print(tbl)
        else:
            print(f"\n  {'Prim':<5}  {'Value':<18}  ZFCₜ clause")
            for p in PRIMITIVES:
                val = e[p]; frag = ZFCT_TEMPLATES[p][val]
                print(f"  {p:<5}  {val:<18}  {render_tokens(frag)[:60]}")

    # ── command: lattice ──────────────────────────────────────────────────────

    def cmd_lattice(self, console=None):
        zfc  = _normalize(ZFC_TUPLE)
        zfcs = _normalize(ZFCS_TUPLE)
        zfct = _normalize(ZFCT_TUPLE)
        zfcst = _normalize(ZFCST_TUPLE)

        t_zfc   = compute_tier(zfc)
        t_zfcs  = compute_tier(zfcs)
        t_zfct  = compute_tier(zfct)
        t_zfcst = compute_tier(zfcst)

        d_zfc_zfcs  = _count_mismatches(zfc, zfcs)
        d_zfc_zfct  = _count_mismatches(zfc, zfct)
        d_zfcs_zfct = _count_mismatches(zfcs, zfct)
        d_zfct_zfcst = _count_mismatches(zfct, zfcst)

        tensor_result = tensor_tuples(zfcs, zfct)
        join_result   = join_tuples(zfcs, zfct)
        meet_result   = meet_tuples(zfcs, zfct)
        t_tensor = compute_tier(tensor_result)
        t_meet   = compute_tier(meet_result)

        tensor_is_zfct = _count_mismatches(tensor_result, zfct) == 0
        join_is_zfct   = _count_mismatches(join_result, zfct) == 0
        meet_is_zfcs   = _count_mismatches(meet_result, zfcs) == 0

        lines = [
            "ZFC / ZFCₛ / ZFCₜ / ZFCₛₜ  Lattice",
            "",
            "  ZFCₛₜ = ZFCₜ  [O_inf]",
            "  ║",
            f"  ║  ← ZFCₛ ⊗ ZFCₜ = ZFCₛₜ? {'yes ✓' if tensor_is_zfct else 'no'}",
            f"  ║  ← ZFCₛ ∨ ZFCₜ = ZFCₛₜ? {'yes ✓' if join_is_zfct else 'no'}",
            "  ║",
            f"  ZFCₜ  [O_inf]  (tier={t_zfct})",
            "  ║",
            f"  ║  d(ZFCₛ, ZFCₜ) = {d_zfcs_zfct}/12 primitives",
            f"  ║  ZFCₛ ∧ ZFCₜ = ZFCₛ? {'yes ✓' if meet_is_zfcs else 'no'}",
            "  ║",
            f"  ZFCₛ  [O_inf]  (tier={t_zfcs})",
            "  ║",
            f"  ║  d(ZFC, ZFCₛ) = {d_zfc_zfcs}/12   d(ZFC, ZFCₜ) = {d_zfc_zfct}/12",
            "  ║",
            f"  ZFC  [O_1]  (tier={t_zfc})",
            "",
            "  Ordering:  ZFC < ZFCₛ < ZFCₜ = ZFCₛₜ  (a chain, not a diamond)",
            "  Both ZFCₛ and ZFCₜ reach O_inf independently — ZFCₛ is the spatial",
            "  stepping-stone between ZFC and ZFCₜ in the primitive lattice.",
            "",
            "  Key structural facts:",
            f"   ZFC  → ZFCₛ:  {d_zfc_zfcs} promotions  {', '.join(p+'→'+t for p,_,t in ZFCS_PROMOTIONS)}",
            f"   ZFC  → ZFCₜ:  {d_zfc_zfct} promotions  {', '.join(p+'→'+t for p,_,t in ZFCT_PROMOTIONS)}",
            f"   ZFCₛ → ZFCₜ:  {d_zfcs_zfct} promotions  Þ Ř ɢ Ħ  (spatial→temporal upgrades; Φ already shared)",
            "",
            "  Frobenius gate: ZFCₛ and ZFCₜ both carry 𐑹 (𐑹) independently.",
            "  Neither inherits Frobenius from the other — both open it via distinct",
            "  structural routes (spatial topology vs temporal chirality).",
        ]
        if console:
            from rich.panel import Panel
            console.print(Panel(
                "\n".join(lines),
                title="[bold cyan]ZFC Triangle Lattice[/bold cyan]",
                border_style="cyan",
            ))
        else:
            for line in lines:
                print(line)

    # ── command: promotions-dual ──────────────────────────────────────────────

    def cmd_promotions_dual(self, console=None):
        zfc = _normalize(ZFC_TUPLE)
        t_promotions = {p: (zv, tv) for p, zv, tv in ZFCT_PROMOTIONS}
        s_promotions = {p: (zv, sv) for p, zv, sv in ZFCS_PROMOTIONS}
        all_prims = sorted(set(t_promotions) | set(s_promotions),
                           key=lambda p: PRIMITIVES.index(p))

        if console:
            from rich.table import Table
            tbl = Table(
                title="ZFC → ZFCₜ vs ZFC → ZFCₛ promotion channels",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column("ZFC value", width=18)
            tbl.add_column("→ ZFCₜ", width=18, style="blue")
            tbl.add_column("Δₜ", width=5)
            tbl.add_column("→ ZFCₛ", width=18, style="green")
            tbl.add_column("Δₛ", width=5)
            tbl.add_column("Shared?", width=8)
            for p in all_prims:
                zv = zfc[p]
                tv = t_promotions[p][1] if p in t_promotions else "—"
                sv = s_promotions[p][1] if p in s_promotions else "—"
                dt = (f"+{int(ORDINALS[p][tv]) - int(ORDINALS[p][zv])}"
                      if tv != "—" else "—")
                ds = (f"+{int(ORDINALS[p][sv]) - int(ORDINALS[p][zv])}"
                      if sv != "—" else "—")
                shared = "✓" if tv == sv and tv != "—" else ""
                tbl.add_row(p, zv, tv if tv != "—" else "[dim]unchanged[/dim]",
                            dt, sv if sv != "—" else "[dim]unchanged[/dim]", ds, shared)
            console.print(tbl)
            console.print(
                "  [bold]Shared promotions[/bold] (Φ, Ω): ZFCₛ and ZFCₜ both open the same gates independently.\n"
                "  [blue]ZFCₜ-only[/blue] (Ħ): temporal chirality 𐑓→𐑖 — no spatial analogue.\n"
                "  [green]ZFCₛ-only[/green] (none, Ħ stays 𐑓 in ZFCₛ).\n"
                "  Þ and Ř diverge: ZFCₜ takes 𐑸+𐑾, ZFCₛ takes 𐑰+𐑽."
            )
        else:
            print("\nZFC → ZFCₜ vs ZFC → ZFCₛ promotion channels")
            print(f"  {'Prim':<5}  {'ZFC':<12}  {'→ ZFCₜ':<18}  Δₜ   {'→ ZFCₛ':<18}  Δₛ   Shared")
            print(f"  {'─'*5}  {'─'*12}  {'─'*18}  {'─'*4}  {'─'*18}  {'─'*4}  {'─'*6}")
            for p in all_prims:
                zv = zfc[p]
                tv = t_promotions[p][1] if p in t_promotions else "(same)"
                sv = s_promotions[p][1] if p in s_promotions else "(same)"
                dt = (f"+{int(ORDINALS[p][tv]) - int(ORDINALS[p][zv])}"
                      if tv != "(same)" else "—")
                ds = (f"+{int(ORDINALS[p][sv]) - int(ORDINALS[p][zv])}"
                      if sv != "(same)" else "—")
                shared = "✓" if tv == sv and tv != "(same)" else ""
                print(f"  {p:<5}  {zv:<12}  {tv:<18}  {dt:<4}  {sv:<18}  {ds:<4}  {shared}")
            print()
            print("  Shared (Φ, Ω): both extensions open the Frobenius gate and integer winding.")
            print("  Diverge  (Þ, Ř): topology and relation mode differ per extension.")
            print("  ZFCₜ-only (Ħ): temporal chirality 𐑓→𐑖 has no spatial parallel in ZFCₛ.")

    # ── command: cliff ────────────────────────────────────────────────────────

    def cmd_cliff(self, name: str = "imaginary_unit", console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console); return
        zfct = _normalize(ZFCT_TUPLE)
        zfcs = _normalize(ZFCS_TUPLE)

        phi_val = e["Φ"]
        phi_ord = int(ORDINALS["Φ"][phi_val])
        is_frob = phi_val == "𐑹"
        tier = compute_tier(e)

        d_zfct = _count_mismatches(e, zfct)
        d_zfcs = _count_mismatches(e, zfcs)

        tensor_zfct = tensor_tuples(e, zfct)
        tensor_result_pol = tensor_zfct["Φ"]
        cliff_holds = tensor_result_pol != "𐑹"

        lines = [
            f"Frobenius cliff analysis: {e.get('name','?')}",
            "",
            f"  Φ = {phi_val}  (ord={phi_ord})  {'= Frobenius ✓' if is_frob else '≠ Frobenius — below the cliff'}",
            f"  tier = {tier}",
            f"  d(entry, ZFCₜ) = {d_zfct}/12    d(entry, ZFCₛ) = {d_zfcs}/12",
            "",
            "  Frobenius cliff (R-FROB-BARR with corrected tensor):",
            f"  tensor(entry, ZFCₜ).Φ = {tensor_result_pol}  {'= 𐑹 ✓' if tensor_result_pol=='𐑹' else '≠ 𐑹  — cliff holds'}",
        ]

        if cliff_holds:
            gap = 4 - phi_ord
            lines += [
                "",
                f"  The cliff holds: Φ = {phi_val} (ord={phi_ord}) ≤ ord 3 < ord 5 = 𐑹.",
                f"  Tensor min-bottleneck on Φ: min({phi_val}, 𐑹) = {phi_val}  (Frobenius cannot propagate).",
                f"  To reach 𐑹 directly requires an independent promotion of {gap} step(s).",
                "  No sequence of tensor compositions with any partner can synthesize 𐑹",
                "  from a starting Φ strictly below 𐑹 — this is the Frobenius cliff.",
            ]
        else:
            lines += [
                "",
                "  Entry already carries Frobenius (𐑹): no cliff for this entry.",
            ]

        for other_name, other_entry in [("ZFCₜ", zfct), ("ZFCₛ", zfcs)]:
            t = tensor_tuples(e, other_entry)
            t_tier = compute_tier(t)
            lines.append(f"  tensor(entry, {other_name}) → tier={t_tier}  Φ={t['Φ']}")

        if console:
            from rich.panel import Panel
            bstyle = "red" if cliff_holds else "green"
            console.print(Panel("\n".join(lines), title="[bold]Frobenius Cliff[/bold]", border_style=bstyle))
        else:
            for line in lines:
                print(line)

    # ── command: special ──────────────────────────────────────────────────────

    def cmd_special(self, console=None):
        seen = set()
        rows = []
        for k, e in SPECIAL_ENTRIES.items():
            n = e.get("name", k)
            if n in seen:
                continue
            seen.add(n)
            e2 = _normalize(e)
            tier = compute_tier(e2) if self._validate(e2) else "?"
            aliases = [a for a, v in SPECIAL_ENTRIES.items() if v is e and a != n]
            rows.append((n, tier, aliases))

        if console:
            from rich.table import Table
            tbl = Table(title="Special entries", show_header=True, header_style="bold cyan")
            tbl.add_column("Name", width=36)
            tbl.add_column("Tier", width=8)
            tbl.add_column("Aliases")
            for name, tier, aliases in rows:
                style = TIER_COLOR.get(tier, "white")
                tbl.add_row(name, f"[{style}]{tier}[/{style}]", ", ".join(aliases))
            console.print(tbl)
        else:
            print("\nSpecial entries:")
            for name, tier, aliases in rows:
                als = ", ".join(aliases)
                print(f"  {name:<38}  tier={tier:<8}  aliases: {als}")

    # ── command: scan ─────────────────────────────────────────────────────────

    def cmd_scan(self, n: int, console=None):
        valid = [_normalize(e) for e in self.catalog if self._validate(_normalize(e))]
        all_pairs = [(i, j) for i in range(len(valid)) for j in range(i+1, len(valid))]
        pairs = random.sample(all_pairs, min(n, len(all_pairs)))
        emergences = 0
        for i, j in pairs:
            a, b = valid[i], valid[j]
            t_r = tensor_tuples(a, b)
            a_tier = compute_tier(a); b_tier = compute_tier(b); r_tier = compute_tier(t_r)
            if TIER_ORDER[r_tier] > max(TIER_ORDER[a_tier], TIER_ORDER[b_tier]):
                emergences += 1
        msg = (
            f"Scan: {len(pairs)} pairs  ({len(valid)} valid entries)\n"
            f"  Tensor tier emergences: {emergences}/{len(pairs)} ({emergences/max(len(pairs),1):.1%})"
        )
        if console:
            from rich.panel import Panel
            console.print(Panel(msg, title="Scan Results", border_style="green"))
        else:
            print(msg)

    # ── command: list ─────────────────────────────────────────────────────────

    def cmd_list(self, pattern: str = "", console=None):
        matches = [e for e in self.catalog if pattern.lower() in e.get("name", "").lower()]
        print(f"  {len(matches)} entries" + (f" matching '{pattern}'" if pattern else ""))
        for e in matches[:50]:
            e2 = _normalize(e)
            tier = compute_tier(e2) if self._validate(e2) else "?"
            print(f"  {e.get('name','?'):<42}  tier={tier}")
        if len(matches) > 50:
            print(f"  ... ({len(matches)-50} more — narrow with :list <pattern>)")

    # ── command: rules ────────────────────────────────────────────────────────

    def cmd_rules(self, console=None):
        lines = [
            "─── Corrected tensor (pol/fid bottleneck) ──────────────────────────",
            "",
            "  tensor(A,B)[p] = max_ord(A[p],B[p])  for all p except Φ, ƒ",
            "  tensor(A,B)[Φ] = min_ord(A[Φ],B[Φ])  Frobenius cliff — 𐑹 cannot be synthesized",
            "  tensor(A,B)[ƒ] = min_ord(A[ƒ],B[ƒ])  fidelity cliff — 𐑐 cannot be synthesized",
            "",
            "  join(A,B)[p]   = max_ord(A[p],B[p])  for all p — pure lattice join",
            "  meet(A,B)[p]   = min_ord(A[p],B[p])  for all p — pure lattice meet",
            "",
            "─── Key structural results ──────────────────────────────────────────",
            "",
            "  ZFC < ZFCₛ < ZFCₜ = ZFCₛₜ  (lattice chain)",
            "  ZFCₛ ⊗ ZFCₜ = ZFCₛₜ = ZFCₜ   (pol min-min = 𐑹, no bottleneck)",
            "  ZFC  ⊗ ZFCₜ = hybrid (O_2†)  pol bottleneck: min(𐑗,𐑹) = 𐑗",
            "  ZFC  ∧ ZFCₜ = ZFC             ZFC  ∨ ZFCₜ = ZFCₜ",
            "  ZFC  ∧ ZFCₛ = ZFC             ZFC  ∨ ZFCₛ = ZFCₛ",
            "  ZFCₛ ∧ ZFCₜ = ZFCₛ            ZFCₛ ∨ ZFCₜ = ZFCₜ",
            "",
            "─── Imaginary numbers Frobenius cliff ──────────────────────────────",
            "",
            "  imaginary_unit: Φ = 𐑿 (ord 1)  →  O_2  (not Frobenius)",
            "    tensor(i, X).Φ = min(𐑿, X.Φ) ≤ 𐑿 < 𐑹  — cliff holds ∀X",
            "    dist(i, ZFCₜ) = 5   dist(i, ZFCₛ) = 8",
            "",
            "  complex_time_path_integral: O_inf, 𐑹  — 1 step from ZFCₜ (𐑥 vs 𐑸)",
            "    Wick rotation t→iτ is a single Þ-promotion: 𐑥→𐑸",
            "",
            "  planck_imaginary_time: Φ = 𐑿 (O_2) — shares 𐑶+𐑽 with ZFCₛ",
            "    tensor(pit, X).Φ = min(𐑿, X.Φ) ≤ 𐑿 — cliff holds ∀X",
            "",
            "─── ZFCₜ promotion channels ────────────────────────────────────────",
            "",
        ]
        for prim, zv, tv in ZFCT_PROMOTIONS:
            gap = int(ORDINALS[prim][tv]) - int(ORDINALS[prim][zv])
            lines.append(f"  {prim:<4}  {zv:<8} ord={int(ORDINALS[prim][zv])}  →  {tv:<8} ord={int(ORDINALS[prim][tv])}  gap={gap:+d}")
        lines += ["", "─── ZFCₛ promotion channels ────────────────────────────────────────", ""]
        for prim, zv, sv in ZFCS_PROMOTIONS:
            gap = int(ORDINALS[prim][sv]) - int(ORDINALS[prim][zv])
            lines.append(f"  {prim:<4}  {zv:<8} ord={int(ORDINALS[prim][zv])}  →  {sv:<8} ord={int(ORDINALS[prim][sv])}  gap={gap:+d}")

        if console:
            from rich.panel import Panel
            console.print(Panel("\n".join(lines), title="[bold cyan]ZFC Triangle Rules[/bold cyan]", border_style="cyan"))
        else:
            for line in lines:
                print(line)

    # ── REPL ──────────────────────────────────────────────────────────────────

    def run_repl(self):
        try:
            from rich.console import Console
            from rich.prompt import Prompt
            console = Console()
        except ImportError:
            console = None

        if console:
            console.print(
                "[bold cyan]ZFC/ZFCₜ/ZFCₛ Manipulator[/bold cyan]"
                "  —  triangle machine  —  :help for commands"
            )
            console.print(
                f"  catalog: {len(self.catalog)} entries  "
                f"| specials: zfc  zfc_t  zfc_s  zfc_st  imaginary_unit  complex_time  planck_imaginary_time"
            )
        else:
            print("ZFC/ZFCₜ/ZFCₛ Manipulator — :help for commands")
            print(f"  catalog: {len(self.catalog)} entries")

        while True:
            try:
                if console:
                    raw = Prompt.ask("\n[bold green]⟨IG⟩[/bold green]")
                else:
                    raw = input("\n⟨IG⟩ ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                break

            parts = raw.strip().split()
            if not parts:
                continue
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in (":quit", ":exit", ":q"):
                print("bye."); break
            elif cmd == ":help":
                if console:
                    from rich.panel import Panel
                    console.print(Panel(HELP_TEXT, title="Help", border_style="dim"))
                else:
                    print(HELP_TEXT)
            elif cmd == ":special":
                self.cmd_special(console)
            elif cmd == ":list":
                self.cmd_list(args[0] if args else "", console)
            elif cmd in (":lookup", ":clauses"):
                if not args:
                    print(f"  usage: {cmd} <name>")
                else:
                    self.cmd_clauses(" ".join(args), console)
            elif cmd == ":tier":
                if not args:
                    print("  usage: :tier <name>")
                else:
                    self.cmd_tier(" ".join(args), console)
            elif cmd in (":tensor", ":join", ":meet"):
                op = cmd[1:]
                if len(args) < 2:
                    print(f"  usage: {cmd} <A> <B>")
                else:
                    self.cmd_binary(op, args[0], " ".join(args[1:]), console)
            elif cmd == ":compare":
                if len(args) < 2:
                    print("  usage: :compare <A> <B>")
                else:
                    self.cmd_compare(args[0], " ".join(args[1:]), console)
            elif cmd == ":barrier":
                if len(args) < 2:
                    print("  usage: :barrier <A> <B>")
                else:
                    self.cmd_barrier(args[0], " ".join(args[1:]), console)
            elif cmd == ":distance":
                if len(args) < 2:
                    print("  usage: :distance <A> <B>")
                else:
                    self.cmd_distance(args[0], " ".join(args[1:]), console)
            elif cmd == ":lift":
                if len(args) < 3:
                    print("  usage: :lift <name> <prim> <val>")
                else:
                    self.cmd_lift(args[0], args[1], args[2], console)
            elif cmd == ":lattice":
                self.cmd_lattice(console)
            elif cmd in (":promotions-dual", ":promos", ":dual"):
                self.cmd_promotions_dual(console)
            elif cmd == ":cliff":
                name = args[0] if args else "imaginary_unit"
                self.cmd_cliff(name, console)
            elif cmd == ":rules":
                self.cmd_rules(console)
            elif cmd == ":scan":
                n = 100
                if args:
                    try:
                        n = int(args[0])
                    except ValueError:
                        print("  usage: :scan <N>"); continue
                self.cmd_scan(n, console)
            else:
                msg = f"  unknown command '{cmd}' — try :help"
                if console:
                    console.print(f"[red]{msg}[/red]")
                else:
                    print(msg)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ZFC/ZFCₜ/ZFCₛ triangle manipulator"
    )
    parser.add_argument("--catalog", type=str, default=None)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("repl",     help="interactive REPL (default)")
    sub.add_parser("rules",    help="print composition rules and exit")
    sub.add_parser("lattice",  help="print ZFC/ZFCₛ/ZFCₜ lattice and exit")
    sub.add_parser("dual",     help="print promotions-dual table and exit")
    sc = sub.add_parser("scan", help="scan N random catalog pairs")
    sc.add_argument("--n", type=int, default=200)

    args = parser.parse_args()
    manip = ZFCTriangleManipulator(catalog_path=args.catalog)

    if args.cmd == "rules":
        manip.cmd_rules()
    elif args.cmd == "lattice":
        manip.cmd_lattice()
    elif args.cmd == "dual":
        manip.cmd_promotions_dual()
    elif args.cmd == "scan":
        manip.cmd_scan(args.n)
    else:
        manip.run_repl()
