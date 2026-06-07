#!/usr/bin/env python3
"""
zfct_manipulator.py — ZFCₜ functor discovery machine.

Performs algebraic operations on imscription tuples, displays per-primitive
ZFCₜ clause transformations, and extracts composition rules — including
cross-clause emergent phenomena (Frobenius cliff, tier emergence).
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
    _SPECIAL_ENTRIES, ZFCT_REFERENCE_ENTRIES, ZFCT_PROMOTIONS,
    load_catalog, _PROMOTION_ATOMS,
)


# ── Tier computation ──────────────────────────────────────────────────────────

TIER_LABELS = {
    "O_0":    "O₀  (semasiographic baseline — non-critical ⊙)",
    "O_1":    "O₁  (critical, Omega-bound — ⊙≥1, Ω=0)",
    "O_2":    "O₂  (recursive, finite dim — ⊙≥1, Ω≥1, Ð<2)",
    "O_2dag": "O₂† (recursive, 𐑼 — ⊙≥1, Ω≥1, Ð≥2)",
    "O_inf":  "O_∞ (Frobenius round-trip — ⊙≥1 ∧ Φ=𐑹)",
}

TIER_ORDER = {"O_0": 0, "O_1": 1, "O_2": 2, "O_2dag": 3, "O_inf": 4}

TIER_COLOR = {
    "O_0":    "dim white",
    "O_1":    "blue",
    "O_2":    "cyan",
    "O_2dag": "yellow",
    "O_inf":  "bold magenta",
}


def compute_tier(t: dict) -> str:
    """
    OuroboricityTier rules (from Imscribing.Primitives.Imscription):
      R1: ⊙ ≥ ord 1 (critical)  ∧  Φ = 𐑹 (𐑹)  →  O_inf
      R2: ⊙ = ord 0 (𐑢)                               →  O_0
      R3: ⊙ ≥ 1  ∧  Ω = ord 0 (𐑷)                    →  O_1
      R4: ⊙ ≥ 1  ∧  Ω ≥ 1  ∧  Ð < ord 2                →  O_2
      R5: ⊙ ≥ 1  ∧  Ω ≥ 1  ∧  Ð ≥ ord 2 (𐑼)      →  O_2†
    """
    phi_c_ord = ORDINALS["⊙"][t["⊙"]]
    phi_frob  = t["Φ"] == "𐑹"
    omega_ord = ORDINALS["Ω"][t["Ω"]]
    dim_ord   = ORDINALS["Ð"][t["Ð"]]
    if phi_c_ord >= 1 and phi_frob:
        return "O_inf"
    if phi_c_ord == 0:
        return "O_0"
    if omega_ord == 0:
        return "O_1"
    if dim_ord >= 2:
        return "O_2dag"
    return "O_2"


# ── Tuple algebra ─────────────────────────────────────────────────────────────

def tensor_tuples(a: dict, b: dict) -> dict:
    """Per-primitive supremum (max ordinal). Categorical join ⊗."""
    return {p: (a[p] if ORDINALS[p][a[p]] >= ORDINALS[p][b[p]] else b[p])
            for p in PRIMITIVES}


def meet_tuples(a: dict, b: dict) -> dict:
    """Per-primitive infimum (min ordinal). Categorical meet ⊓."""
    return {p: (a[p] if ORDINALS[p][a[p]] <= ORDINALS[p][b[p]] else b[p])
            for p in PRIMITIVES}


def lift_tuple(a: dict, prim: str, val: str) -> dict:
    """Set one primitive to val (any ordinal, up or down)."""
    if prim not in ORDINALS:
        raise ValueError(f"unknown primitive: {prim}")
    if val not in ORDINALS[prim]:
        raise ValueError(f"unknown value {val!r} for {prim}")
    result = dict(a)
    result[prim] = val
    return result


# ── ZFCₜ clause algebra ────────────────────────────────────────────────────────

def get_clauses(t: dict) -> Dict[str, List[str]]:
    return {p: ZFCT_TEMPLATES[p][t[p]] for p in PRIMITIVES}


def all_tokens(t: dict) -> set:
    tokens: set = set()
    for p in PRIMITIVES:
        tokens.update(ZFCT_TEMPLATES[p][t[p]])
    return tokens


def promotion_atoms_present(t: dict) -> List[str]:
    present = all_tokens(t)
    return [a for a in sorted(_PROMOTION_ATOMS) if a in present]


def has_frob(t: dict) -> bool:
    return "FROB" in all_tokens(t)


def has_fixpt(t: dict) -> bool:
    return "FIXPT" in all_tokens(t)


# ── Rule induction ─────────────────────────────────────────────────────────────

@dataclass
class Observation:
    a_name: str
    b_name: str
    op: str
    a_tier: str
    b_tier: str
    result_tier: str
    tier_emerged: bool
    frob_emerged: bool
    new_promo_atoms: List[str]


class RuleExtractor:
    def __init__(self):
        self.observations: List[Observation] = []

    def observe(self, a: dict, b: dict, op: str = "tensor") -> Tuple[dict, Observation]:
        if op == "tensor":
            result = tensor_tuples(a, b)
        elif op == "meet":
            result = meet_tuples(a, b)
        else:
            raise ValueError(f"unknown op: {op}")

        a_tier = compute_tier(a)
        b_tier = compute_tier(b)
        r_tier = compute_tier(result)

        a_atoms = all_tokens(a)
        b_atoms = all_tokens(b)
        r_atoms = all_tokens(result)

        max_in_ord = max(TIER_ORDER[a_tier], TIER_ORDER[b_tier])
        obs = Observation(
            a_name=a.get("name", "?"),
            b_name=b.get("name", "?"),
            op=op,
            a_tier=a_tier,
            b_tier=b_tier,
            result_tier=r_tier,
            tier_emerged=TIER_ORDER[r_tier] > max_in_ord,
            frob_emerged=has_frob(result) and not has_frob(a) and not has_frob(b),
            new_promo_atoms=sorted(r_atoms - (a_atoms | b_atoms) & set(_PROMOTION_ATOMS)),
        )
        self.observations.append(obs)
        return result, obs

    def summary(self) -> dict:
        total = len(self.observations)
        if not total:
            return {}
        tensor_obs = [o for o in self.observations if o.op == "tensor"]
        emergences = [o for o in tensor_obs if o.tier_emerged]
        frob_synths = [o for o in self.observations if o.frob_emerged]
        return {
            "total": total,
            "tensor": len(tensor_obs),
            "tier_emergences": len(emergences),
            "frob_syntheses": len(frob_synths),
            "emergence_rate": len(emergences) / max(len(tensor_obs), 1),
        }

    def emergent_cases(self, limit: int = 20) -> List[Observation]:
        return [o for o in self.observations if o.tier_emerged][:limit]

    def print_rules(self, console=None):
        stats = self.summary()
        lines = [
            f"Observations: {stats.get('total', 0)} total  "
            f"({stats.get('tensor', 0)} tensor ops)",
            f"Tier emergences (result tier > max(A,B)):  "
            f"{stats.get('tier_emergences', 0)}  "
            f"({stats.get('emergence_rate', 0):.1%})",
            f"FROB synthesized from non-FROB inputs:     "
            f"{stats.get('frob_syntheses', 0)}",
            "",
            "─── Per-primitive composition rules (trivial) ───────────────────────",
            "",
            "  R-CLAUS-T   clauses(tensor(A,B))[p] = ZFCT_TEMPLATES[p][max_ord(A[p], B[p])]",
            "              true by construction — per-primitive independence",
            "",
            "  R-CLAUS-M   clauses(meet(A,B))[p]   = ZFCT_TEMPLATES[p][min_ord(A[p], B[p])]",
            "              true by construction",
            "",
            "─── Cross-primitive emergence rules (non-trivial) ───────────────────",
            "",
            "  R-FROB-BARR FROB ∈ clauses(tensor(A,B))  iff  A[Φ]=𐑹 OR B[Φ]=𐑹",
            "              𐑹 = 𐑹, ordinal 4 = unique maximum",
            "              → FROBENIUS CLIFF: 𐑹 is non-synthesizable by tensor",
            "                from any pair where neither input has 𐑹",
            "",
            "  R-FIXPT-T   FIXPT ∈ clauses(tensor(A,B))  iff  A[⊙] ord≥1 OR B[⊙] ord≥1",
            "              ⊙ (⊙) is ordinal 1 — reached by any critical input",
            "",
            "  R-TIER-EMRG tier(tensor(A,B)) can exceed tier(A) and tier(B)",
            "              mechanism: FROB ∧ FIXPT cross-clause conjunction",
            "              example:   A = O_2† with 𐑹 but 𐑢  (has FROB, no FIXPT)",
            "                         B = O_2† with ⊙ but 𐑬  (has FIXPT, no FROB)",
            "                         tensor(A,B) has BOTH → O_inf",
            "",
            "  R-ZFCT-ABS  For all 6 ZFCₜ promotion channels c:",
            "              tensor(any, ZFCt)[c] = ZFCt_promoted_value(c)",
            "              ZFCt is the absorption element for each promotion channel",
            "",
            "  R-FROB-CONT Once FROB ∈ clauses, it is preserved under all tensor ops:",
            "              FROB ∈ clauses(A)  →  FROB ∈ clauses(tensor(A, X))  ∀X",
            "",
            "─── ZFCₜ promotion summary ───────────────────────────────────────────",
            "",
        ]
        for prim, zfc_val, zfct_val in ZFCT_PROMOTIONS:
            zfc_ord  = ORDINALS[prim][zfc_val]
            zfct_ord = ORDINALS[prim][zfct_val]
            gap = zfct_ord - zfc_ord
            lines.append(
                f"  {prim:<4}  {zfc_val:<8} ord={zfc_ord}  →  "
                f"{zfct_val:<8} ord={zfct_ord}  gap={gap:+d}"
            )

        if console:
            from rich.panel import Panel
            console.print(Panel(
                "\n".join(lines),
                title="[bold cyan]ZFCₜ Composition Rules[/bold cyan]",
                border_style="cyan",
            ))
        else:
            for line in lines:
                print(line)


# ── Display helpers ────────────────────────────────────────────────────────────

HELP_TEXT = """
ZFCₜ Manipulator — commands

  :lookup <name>              show clause breakdown for entry
  :clauses <name>             alias for :lookup
  :tier <name>                compute OuroboricityTier
  :tensor <A> <B>             per-primitive supremum (categorical join)
  :meet <A> <B>               per-primitive infimum (categorical meet)
  :lift <name> <prim> <val>   set one primitive to val
  :compare <A> <B>            side-by-side clause comparison with Δ ordinal
  :barrier <A> <B>            Frobenius barrier analysis
  :distance <A> <B>           weighted tuple distance
  :scan <N>                   scan N random catalog pairs (tensor + meet)
  :rules                      print ZFCₜ composition rule set
  :emergent                   list tier-emergent observations
  :special                    list special named entries with tiers
  :list [pattern]             list catalog entries (optional name filter)
  :help                       this message
  :quit                       exit

Entry names:
  special:   zfc  zfct  schrodinger  navier_stokes  einstein  iug  wave  heat
  catalog:   exact name or fuzzy substring match
  inline:    𐑼,𐑸,𐑾,𐑬,𐑐,𐑧,𐑲,𐑠,⊙,𐑖,𐑳,𐑭  (12 comma-separated)
""".strip()


# ── Manipulator ────────────────────────────────────────────────────────────────

class ZFCtManipulator:
    def __init__(self, catalog_path: str = None):
        self.catalog_path = catalog_path
        self.catalog: List[dict] = []
        self._name_index: Dict[str, dict] = {}
        self.extractor = RuleExtractor()
        self._load()

    def _load(self):
        raw = load_catalog(self.catalog_path)
        ref_names = {e["name"] for e in ZFCT_REFERENCE_ENTRIES}
        self.catalog = ZFCT_REFERENCE_ENTRIES + [
            e for e in raw if e.get("name") not in ref_names
        ]
        for e in self.catalog:
            n = e.get("name", "")
            if n:
                self._name_index[n.lower()] = e

    def _validate(self, t: dict) -> bool:
        return all(p in t and t[p] in ORDINALS[p] for p in PRIMITIVES)

    def resolve(self, name: str) -> Optional[dict]:
        # special
        if name in _SPECIAL_ENTRIES:
            return _normalize_entry(_SPECIAL_ENTRIES[name])
        # inline tuple: 12 comma-separated prim_val entries
        if name.count(",") == 11 and "_" in name:
            parts = name.split(",")
            try:
                t: dict = {}
                for i, p in enumerate(PRIMITIVES):
                    t[p] = parts[i].strip()
                    if t[p] not in ORDINALS[p]:
                        raise ValueError(f"bad value {t[p]!r} for {p}")
                t["name"] = "inline"
                return t
            except (ValueError, IndexError):
                pass
        # exact (case-insensitive)
        low = name.lower()
        if low in self._name_index:
            return _normalize_entry(self._name_index[low])
        # fuzzy substring
        matches = [e for e in self.catalog if low in e.get("name", "").lower()]
        if matches:
            if len(matches) > 1:
                print(f"  [fuzzy] {len(matches)} matches — using '{matches[0]['name']}'")
            return _normalize_entry(matches[0])
        return None

    def _not_found(self, name: str, console=None):
        msg = f"  [not found] '{name}' — try :special or :list"
        if console:
            console.print(f"[red]{msg}[/red]")
        else:
            print(msg)

    # ── command implementations ──────────────────────────────────────────────

    def cmd_clauses(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console)
            return
        if not self._validate(e):
            print(f"  [error] '{name}' has missing/invalid primitives.")
            return
        self._show_clauses(e, console)

    def _show_clauses(self, e: dict, console=None):
        tier = compute_tier(e)
        title = f"{e.get('name', '?')}  tier={tier}"

        if console:
            from rich.table import Table
            tbl = Table(title=title, show_header=True, header_style="bold cyan")
            tbl.add_column("Prim",  width=5,  style="bold")
            tbl.add_column("Value", width=18)
            tbl.add_column("ZFCₜ clause")
            tbl.add_column("Promo atoms", style="magenta", width=14)
            for p in PRIMITIVES:
                val   = e[p]
                frag  = ZFCT_TEMPLATES[p][val]
                rendered = render_tokens(frag)
                promo = [tok for tok in frag if tok in _PROMOTION_ATOMS]
                tbl.add_row(p, val, rendered, " ".join(promo) or "—")
            console.print(tbl)
            style = TIER_COLOR.get(tier, "white")
            console.print(
                f"  tier: [{style}]{TIER_LABELS.get(tier, tier)}[/{style}]"
            )
        else:
            print(f"\n{title}")
            print(f"  {'Prim':<5}  {'Value':<18}  ZFCₜ clause")
            print(f"  {'─'*5}  {'─'*18}  {'─'*50}")
            for p in PRIMITIVES:
                val  = e[p]
                frag = ZFCT_TEMPLATES[p][val]
                rendered = render_tokens(frag)
                promo = [tok for tok in frag if tok in _PROMOTION_ATOMS]
                tag = "  [" + "+".join(promo) + "]" if promo else ""
                print(f"  {p:<5}  {val:<18}  {rendered[:50-len(tag)]:50}{tag}")
            print(f"  tier: {TIER_LABELS.get(tier, tier)}")

    def cmd_tier(self, name: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console)
            return
        if not self._validate(e):
            print(f"  [error] '{name}' has missing/invalid primitives.")
            return
        tier  = compute_tier(e)
        style = TIER_COLOR.get(tier, "white")
        label = TIER_LABELS.get(tier, tier)
        msg   = f"tier({e.get('name','?')}) = {label}"
        if console:
            console.print(f"  [{style}]{msg}[/{style}]")
        else:
            print(f"  {msg}")

    def cmd_binary(self, op: str, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a:
            self._not_found(name_a, console)
            return
        if not b:
            self._not_found(name_b, console)
            return
        if not (self._validate(a) and self._validate(b)):
            print("  [error] invalid primitives in one of the entries.")
            return
        result, obs = self.extractor.observe(a, b, op)
        result["name"] = f"{op}({a.get('name','A')},{b.get('name','B')})"
        self._show_binary(a, b, result, obs, op, console)

    def _show_binary(self, a, b, result, obs, op, console=None):
        dist_ab = tuple_distance(a, b)
        dist_ar = tuple_distance(a, result)
        dist_br = tuple_distance(b, result)

        if console:
            from rich.table import Table
            an = a.get("name", "A")[:16]
            bn = b.get("name", "B")[:16]
            tbl = Table(
                title=f"{op}({an}, {bn})",
                show_header=True, header_style="bold",
            )
            tbl.add_column("Prim",   width=5,  style="bold")
            tbl.add_column(f"A: {an}", width=20)
            tbl.add_column(f"B: {bn}", width=20)
            tbl.add_column("Result",  width=20, style="green")
            tbl.add_column("Src",     width=5)
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]; rv = result[p]
                if av == bv:
                    src = "="
                elif rv == av:
                    src = "←A"
                else:
                    src = "←B"
                style = "dim" if av == bv else ""
                tbl.add_row(p, av, bv, rv, src)
            console.print(tbl)

            # tier line
            as_ = TIER_COLOR.get(obs.a_tier, "white")
            bs_ = TIER_COLOR.get(obs.b_tier, "white")
            rs_ = TIER_COLOR.get(obs.result_tier, "white")
            console.print(
                f"  tier(A)=[{as_}]{obs.a_tier}[/{as_}]  "
                f"tier(B)=[{bs_}]{obs.b_tier}[/{bs_}]  "
                f"→  tier(result)=[{rs_}]{obs.result_tier}[/{rs_}]"
            )
            console.print(
                f"  d(A,B)={dist_ab:.3f}  "
                f"d(A,result)={dist_ar:.3f}  "
                f"d(B,result)={dist_br:.3f}"
            )
            if obs.tier_emerged:
                console.print(
                    "[bold magenta]  ★ TIER EMERGENCE: "
                    "result tier exceeds both inputs[/bold magenta]"
                )
            if obs.frob_emerged:
                console.print(
                    "[bold red]  !! FROB VIOLATION: FROB appeared without either input having it[/bold red]"
                )
            if promotion_atoms_present(result):
                pa = ", ".join(promotion_atoms_present(result))
                console.print(f"  promo atoms in result: [magenta]{pa}[/magenta]")
        else:
            an = a.get("name", "A"); bn = b.get("name", "B")
            print(f"\n{op}({an}, {bn})")
            print(f"  {'Prim':<5}  {'A':<20}  {'B':<20}  {'Result':<20}  Src")
            print(f"  {'─'*5}  {'─'*20}  {'─'*20}  {'─'*20}  {'─'*3}")
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]; rv = result[p]
                src = "=" if av == bv else ("←A" if rv == av else "←B")
                print(f"  {p:<5}  {av:<20}  {bv:<20}  {rv:<20}  {src}")
            print(f"\n  tier(A)={obs.a_tier}  tier(B)={obs.b_tier}  → tier(result)={obs.result_tier}")
            print(f"  d(A,B)={dist_ab:.3f}  d(A,result)={dist_ar:.3f}  d(B,result)={dist_br:.3f}")
            if obs.tier_emerged:
                print("  *** TIER EMERGENCE: result tier exceeds both inputs! ***")
            if obs.frob_emerged:
                print("  *** FROB VIOLATION: FROB appeared without either input having it ***")
            pa = promotion_atoms_present(result)
            if pa:
                print(f"  promo atoms: {', '.join(pa)}")

    def cmd_compare(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a:
            self._not_found(name_a, console)
            return
        if not b:
            self._not_found(name_b, console)
            return
        if not (self._validate(a) and self._validate(b)):
            print("  [error] invalid primitives in one of the entries.")
            return

        dist    = tuple_distance(a, b)
        a_tier  = compute_tier(a)
        b_tier  = compute_tier(b)
        n_diffs = sum(1 for p in PRIMITIVES if a[p] != b[p])

        if console:
            from rich.table import Table
            an = a.get("name", "A")[:20]
            bn = b.get("name", "B")[:20]
            tbl = Table(
                title=f"compare: {an}  vs  {bn}  (d={dist:.4f}, {n_diffs}/12 differ)",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim",    width=5)
            tbl.add_column("A value", width=18)
            tbl.add_column("A clause")
            tbl.add_column("B value", width=18)
            tbl.add_column("B clause")
            tbl.add_column("Δ ord",   width=6)
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]
                af = render_tokens(ZFCT_TEMPLATES[p][av])[:32]
                bf = render_tokens(ZFCT_TEMPLATES[p][bv])[:32]
                delta = int(ORDINALS[p][bv]) - int(ORDINALS[p][av])
                ds    = f"{delta:+d}" if delta != 0 else "—"
                style = "green" if delta > 0 else ("red" if delta < 0 else "dim")
                avs   = f"[bold]{av}[/bold]" if delta != 0 else av
                bvs   = f"[bold]{bv}[/bold]" if delta != 0 else bv
                tbl.add_row(p, avs, af, bvs, bf, f"[{style}]{ds}[/{style}]")
            console.print(tbl)
            as_ = TIER_COLOR.get(a_tier, "white")
            bs_ = TIER_COLOR.get(b_tier, "white")
            console.print(
                f"  tier(A)=[{as_}]{a_tier}[/{as_}]  "
                f"tier(B)=[{bs_}]{b_tier}[/{bs_}]  "
                f"d={dist:.4f}  primitives differing: {n_diffs}/12"
            )
        else:
            an = a.get("name", "A"); bn = b.get("name", "B")
            print(f"\ncompare: {an}  vs  {bn}  (d={dist:.4f})")
            print(f"  {'Prim':<5}  {'A value':<18}  {'B value':<18}  Δ ord")
            print(f"  {'─'*5}  {'─'*18}  {'─'*18}  {'─'*5}")
            for p in PRIMITIVES:
                av = a[p]; bv = b[p]
                delta = int(ORDINALS[p][bv]) - int(ORDINALS[p][av])
                ds = f"{delta:+d}" if delta != 0 else "—"
                marker = " *" if delta != 0 else ""
                print(f"  {p:<5}  {av:<18}  {bv:<18}  {ds}{marker}")
            print(f"\n  tier(A)={a_tier}  tier(B)={b_tier}  d={dist:.4f}  diffs={n_diffs}/12")

    def cmd_barrier(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a:
            self._not_found(name_a, console)
            return
        if not b:
            self._not_found(name_b, console)
            return
        if not (self._validate(a) and self._validate(b)):
            print("  [error] invalid primitives in one of the entries.")
            return

        tensor_r = tensor_tuples(a, b)
        meet_r   = meet_tuples(a, b)
        tensor_r["name"] = f"tensor({a.get('name','A')},{b.get('name','B')})"
        meet_r["name"]   = f"meet({a.get('name','A')},{b.get('name','B')})"

        a_frob   = has_frob(a);      b_frob   = has_frob(b)
        t_frob   = has_frob(tensor_r)
        a_fixpt  = has_fixpt(a);     b_fixpt  = has_fixpt(b)
        t_fixpt  = has_fixpt(tensor_r)
        a_tier   = compute_tier(a);  b_tier   = compute_tier(b)
        t_tier   = compute_tier(tensor_r)
        m_tier   = compute_tier(meet_r)

        phi_a_ord = int(ORDINALS["Φ"][a["Φ"]])
        phi_b_ord = int(ORDINALS["Φ"][b["Φ"]])
        frob_gap  = 4 - max(phi_a_ord, phi_b_ord)

        lines = [
            f"Frobenius barrier:  {a.get('name','A')}  ×  {b.get('name','B')}",
            "",
            f"  A    FROB={str(a_frob):<5}  FIXPT={str(a_fixpt):<5}  Φ={a['Φ']}  ⊙={a['⊙']}  tier={a_tier}",
            f"  B    FROB={str(b_frob):<5}  FIXPT={str(b_fixpt):<5}  Φ={b['Φ']}  ⊙={b['⊙']}  tier={b_tier}",
            f"  ─────────────────────────────────────────────────────────────",
            f"  ⊗    FROB={str(t_frob):<5}  FIXPT={str(t_fixpt):<5}  Φ={tensor_r['Φ']}  ⊙={tensor_r['⊙']}  tier={t_tier}",
            f"  ⊓    tier={m_tier}  Φ={meet_r['Φ']}",
            "",
        ]

        if t_frob and not (a_frob or b_frob):
            lines += [
                "  !! BARRIER VIOLATION: FROB appeared in tensor without being in either input.",
                "     This contradicts R-FROB-BARR — check primitive data integrity.",
            ]
        elif t_frob:
            src = "A" if a_frob else "B"
            lines += [
                f"  Barrier holds: FROB inherited from {src}, not synthesized.",
                f"  R-FROB-BARR satisfied: 𐑹 propagates forward under ⊗.",
            ]
        else:
            lines += [
                "  Barrier holds: neither input has FROB, tensor has none.",
                f"  Gap to Frobenius: {frob_gap} ordinal step(s) in Φ from current max "
                f"(Φ ord={max(phi_a_ord, phi_b_ord)}, need ord=5 for 𐑹).",
            ]

        if t_tier == "O_inf" and a_tier != "O_inf" and b_tier != "O_inf":
            lines += [
                "",
                "  ★ TIER EMERGENCE to O_inf!",
                f"    A: FROB={a_frob}, FIXPT={a_fixpt}   B: FROB={b_frob}, FIXPT={b_fixpt}",
                "    Tensor supplies both FROB and FIXPT across the two inputs.",
                "    Neither alone satisfies R1 — together they unlock Frobenius round-trip.",
            ]
        elif t_tier == "O_inf":
            lines += [
                "",
                "  O_inf result: at least one input already has both FROB and FIXPT.",
            ]

        if console:
            from rich.panel import Panel
            bstyle = "bold magenta" if t_tier == "O_inf" else (
                     "red" if (t_frob and not a_frob and not b_frob) else "cyan")
            console.print(Panel(
                "\n".join(lines),
                title="[bold]Frobenius Barrier Analysis[/bold]",
                border_style=bstyle,
            ))
        else:
            for line in lines:
                print(line)

    def cmd_distance(self, name_a: str, name_b: str, console=None):
        a = self.resolve(name_a)
        b = self.resolve(name_b)
        if not a:
            self._not_found(name_a, console)
            return
        if not b:
            self._not_found(name_b, console)
            return
        if not (self._validate(a) and self._validate(b)):
            print("  [error] invalid primitives in one of the entries.")
            return
        d = tuple_distance(a, b)
        n = sum(1 for p in PRIMITIVES if a[p] != b[p])
        msg = f"d({a.get('name','A')}, {b.get('name','B')}) = {d:.4f}  ({n}/12 primitives differ)"
        if console:
            console.print(f"  {msg}")
        else:
            print(f"  {msg}")

    def cmd_lift(self, name: str, prim: str, val: str, console=None):
        e = self.resolve(name)
        if not e:
            self._not_found(name, console)
            return
        if prim not in ORDINALS:
            valids = ", ".join(PRIMITIVES)
            print(f"  [error] unknown primitive '{prim}'.  Valid: {valids}")
            return
        if val not in ORDINALS[prim]:
            valids = ", ".join(ORDINALS[prim].keys())
            print(f"  [error] unknown value '{val}' for {prim}.  Valid: {valids}")
            return
        old_tier  = compute_tier(e)
        old_val   = e[prim]
        result    = lift_tuple(e, prim, val)
        new_tier  = compute_tier(result)
        result["name"] = f"lift({e.get('name','?')}, {prim}→{val})"

        delta = int(ORDINALS[prim][val]) - int(ORDINALS[prim][old_val])
        direction = "lift" if delta > 0 else ("degrade" if delta < 0 else "identity")
        msg = (
            f"  {direction}: {prim}: {old_val} (ord {int(ORDINALS[prim][old_val])}) "
            f"→ {val} (ord {int(ORDINALS[prim][val])})  Δ={delta:+d}"
        )
        if old_tier != new_tier:
            msg += f"   tier: {old_tier} → {new_tier}"
        if console:
            console.print(msg)
        else:
            print(msg)
        self._show_clauses(result, console)

    def cmd_scan(self, n: int, console=None):
        valid = [_normalize_entry(e) for e in self.catalog if self._validate(_normalize_entry(e))]
        max_pairs = len(valid) * (len(valid) - 1) // 2
        n = min(n, max_pairs)
        all_pairs = [(i, j) for i in range(len(valid)) for j in range(i+1, len(valid))]
        pairs = random.sample(all_pairs, n) if n < len(all_pairs) else all_pairs

        if console:
            from rich.progress import Progress
            emergences = 0
            with Progress(console=console) as prog:
                task = prog.add_task("Scanning pairs...", total=len(pairs))
                for i, j in pairs:
                    a, b = valid[i], valid[j]
                    _, obs_t = self.extractor.observe(a, b, "tensor")
                    _, _     = self.extractor.observe(a, b, "meet")
                    if obs_t.tier_emerged:
                        emergences += 1
                    prog.advance(task)
        else:
            emergences = 0
            for i, j in pairs:
                a, b = valid[i], valid[j]
                _, obs_t = self.extractor.observe(a, b, "tensor")
                _, _     = self.extractor.observe(a, b, "meet")
                if obs_t.tier_emerged:
                    emergences += 1

        stats = self.extractor.summary()
        msg = (
            f"Scan complete: {len(pairs)} pairs  ({len(valid)} valid catalog entries)\n"
            f"  Tensor tier emergences: {emergences}/{len(pairs)}  ({emergences/max(len(pairs),1):.1%})\n"
            f"  Total observations: {stats['total']}\n"
        )
        if console:
            from rich.panel import Panel
            console.print(Panel(msg, title="Scan Results", border_style="green"))
        else:
            print(msg)

    def cmd_emergent(self, console=None):
        cases = self.extractor.emergent_cases(limit=30)
        if not cases:
            msg = "No emergent observations yet. Run :scan N first."
            if console:
                console.print(f"  [dim]{msg}[/dim]")
            else:
                print(f"  {msg}")
            return
        if console:
            from rich.table import Table
            tbl = Table(
                title=f"Tier-emergent tensor operations ({len(cases)} shown)",
                show_header=True, header_style="bold magenta",
            )
            tbl.add_column("A", width=26)
            tbl.add_column("tier(A)", width=8)
            tbl.add_column("B", width=26)
            tbl.add_column("tier(B)", width=8)
            tbl.add_column("tier(⊗)", width=8)
            for o in cases:
                as_ = TIER_COLOR.get(o.a_tier, "white")
                bs_ = TIER_COLOR.get(o.b_tier, "white")
                rs_ = TIER_COLOR.get(o.result_tier, "white")
                tbl.add_row(
                    o.a_name[:24], f"[{as_}]{o.a_tier}[/{as_}]",
                    o.b_name[:24], f"[{bs_}]{o.b_tier}[/{bs_}]",
                    f"[{rs_}]{o.result_tier}[/{rs_}]",
                )
            console.print(tbl)
        else:
            print(f"\nTier-emergent tensor observations: {len(cases)}")
            print(f"  {'A':<28}  {'tier(A)':<8}  {'B':<28}  {'tier(B)':<8}  tier(⊗)")
            for o in cases:
                print(f"  {o.a_name[:26]:<28}  {o.a_tier:<8}  {o.b_name[:26]:<28}  {o.b_tier:<8}  {o.result_tier}")

    def cmd_special(self, console=None):
        unique_keys = sorted(set(v.get("name","?") for v in _SPECIAL_ENTRIES.values()))
        rows = []
        for k in unique_keys:
            e = next(v for v in _SPECIAL_ENTRIES.values() if v.get("name","") == k)
            e2 = _normalize_entry(e)
            tier = compute_tier(e2) if self._validate(e2) else "?"
            aliases = [a for a, v in _SPECIAL_ENTRIES.items() if v is e]
            rows.append((k, tier, aliases))

        if console:
            from rich.table import Table
            tbl = Table(title="Special entries", show_header=True, header_style="bold cyan")
            tbl.add_column("Name",    width=34)
            tbl.add_column("Tier",    width=8)
            tbl.add_column("Aliases")
            for name, tier, aliases in rows:
                style = TIER_COLOR.get(tier, "white")
                tbl.add_row(name, f"[{style}]{tier}[/{style}]",
                            ", ".join(a for a in aliases if a != name))
            console.print(tbl)
        else:
            print("\nSpecial entries:")
            for name, tier, aliases in rows:
                als = ", ".join(a for a in aliases if a != name)
                print(f"  {name:<34}  tier={tier:<8}  aliases: {als}")

    def cmd_list(self, pattern: str = "", console=None):
        matches = [e for e in self.catalog
                   if pattern.lower() in e.get("name", "").lower()]
        print(f"  {len(matches)} entries" + (f" matching '{pattern}'" if pattern else ""))
        for e in matches[:50]:
            e2   = _normalize_entry(e)
            tier = compute_tier(e2) if self._validate(e2) else "?"
            print(f"  {e.get('name','?'):<42}  tier={tier}")
        if len(matches) > 50:
            print(f"  ... ({len(matches)-50} more — narrow with :list <pattern>)")

    # ── REPL ─────────────────────────────────────────────────────────────────

    def run_repl(self):
        try:
            from rich.console import Console
            from rich.prompt import Prompt
            console = Console()
        except ImportError:
            console = None

        if console:
            console.print(
                "[bold cyan]ZFCₜ Manipulator[/bold cyan]"
                "  —  functor discovery machine  —  :help for commands"
            )
            console.print(
                f"  catalog: {len(self.catalog)} entries  "
                f"| specials: {len(set(v.get('name') for v in _SPECIAL_ENTRIES.values()))}"
            )
        else:
            print("ZFCₜ Manipulator — :help for commands")
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
            cmd  = parts[0].lower()
            args = parts[1:]

            if cmd in (":quit", ":exit", ":q"):
                print("bye.")
                break
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
            elif cmd in (":tensor", ":meet"):
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
            elif cmd == ":scan":
                n = 100
                if args:
                    try:
                        n = int(args[0])
                    except ValueError:
                        print("  usage: :scan <N>")
                        continue
                self.cmd_scan(n, console)
            elif cmd == ":rules":
                self.extractor.print_rules(console)
            elif cmd == ":emergent":
                self.cmd_emergent(console)
            else:
                msg = f"  unknown command '{cmd}' — try :help"
                if console:
                    console.print(f"[red]{msg}[/red]")
                else:
                    print(msg)


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ZFCₜ Manipulator — functor discovery machine"
    )
    parser.add_argument("--catalog", type=str, default=None)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("repl",  help="interactive REPL (default)")
    sub.add_parser("rules", help="print composition rules and exit")

    sc = sub.add_parser("scan", help="scan N random catalog pairs")
    sc.add_argument("--n", type=int, default=200)

    args = parser.parse_args()
    manip = ZFCtManipulator(catalog_path=args.catalog)

    if args.cmd == "rules":
        manip.extractor.print_rules()
    elif args.cmd == "scan":
        manip.cmd_scan(args.n)
        manip.extractor.print_rules()
    else:
        manip.run_repl()
