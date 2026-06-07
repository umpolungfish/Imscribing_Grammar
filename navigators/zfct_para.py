#!/usr/bin/env python3
"""
zfct_para.py — Belnap FOUR paraconsistent layer over the ZFC/ZFCₜ/ZFCₛ triangle.

Each primitive slot carries a belief set — a frozenset of ordinal value tokens
instead of a single classical value:

  |belief[p]| = 1, v ∈ belief[p]   T  (true: definitely v)
  |belief[p]| > 1, v ∈ belief[p]   B  (both: overdetermined at v)
  |belief[p]| > 0, v ∉ belief[p]   F  (false: v not assigned)
  |belief[p]| = 0                  N  (neither: underdetermined)

Paraconsistent tensor rule (bottleneck preserved):
  para_tensor(A,B)[p] = { min_ord(a,b) | a∈A[p], b∈B[p] }   p ∈ {Φ,ƒ}
  para_tensor(A,B)[p] = { max_ord(a,b) | a∈A[p], b∈B[p] }   otherwise

The Frobenius cliff in paraconsistent setting: forcing Φ to B{v, 𐑹} does NOT
collapse to T after tensor composition — the min-bottleneck preserves the lower
value, leaving the result in B-state. A classical proof of an MPP is exactly a
demonstration that the B-state collapses to T for 𐑹: that the object in question
genuinely carries Frobenius structure rather than merely being consistent with it.

New REPL commands (all prefixed :para-):
  :para-cliff [name]              Frobenius cliff with Φ forced to B{v,𐑹}
  :para-tensor <A> <B>            paraconsistent tensor
  :para-reach <name>              Belnap tier-reachability per tier
  :para-assign <name> <p> <v...>  set belief[p] to the listed values
  :para-compare <A> <B>           Belnap-valued comparison
  :para-help                      this message
"""

import sys
import argparse
from itertools import product as iproduct
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent))
from zfct_navigator import PRIMITIVES, ORDINALS
from zfct_manipulator import (
    compute_tier, TIER_LABELS, TIER_ORDER, TIER_COLOR,
    has_frob, has_fixpt,
)
from zfct_zfcs_zfc_manipulator import (
    ZFCTriangleManipulator, _normalize,
    ZFCT_TUPLE, ZFCS_TUPLE, ZFC_TUPLE,
    _BOTTLENECK_PRIMS, tensor_tuples,
)

_FROB_VAL   = "𐑹"   # 𐑹 — the Frobenius gate value for Φ
_ODOT_CRIT  = "⊙"   # ⊙ critical value (ord ≥ 1)


# ── Belnap four-valued logic ──────────────────────────────────────────────────

class Belnap(Enum):
    T = "Þ"   # true:        all classical realizations satisfy
    F = "ƒ"   # false:       no  classical realization satisfies
    B = "B"   # both:        some satisfy, some do not (overdetermined)
    N = "N"   # neither:     empty belief set (underdetermined)

_SYM   = {Belnap.T: "Þ", Belnap.F: "ƒ", Belnap.B: "B", Belnap.N: "N"}
_COLOR = {Belnap.T: "green", Belnap.F: "red", Belnap.B: "magenta", Belnap.N: "yellow"}

# Belnap truth-order for display sorting: F < N < B < T
_TRUTH_ORD = {Belnap.F: 0, Belnap.N: 1, Belnap.B: 2, Belnap.T: 3}

# Belnap conjunction (truth-order min)
_AND = {
    (Belnap.T, Belnap.T): Belnap.T, (Belnap.T, Belnap.B): Belnap.B,
    (Belnap.T, Belnap.N): Belnap.N, (Belnap.T, Belnap.F): Belnap.F,
    (Belnap.B, Belnap.T): Belnap.B, (Belnap.B, Belnap.B): Belnap.B,
    (Belnap.B, Belnap.N): Belnap.N, (Belnap.B, Belnap.F): Belnap.F,
    (Belnap.N, Belnap.T): Belnap.N, (Belnap.N, Belnap.B): Belnap.N,
    (Belnap.N, Belnap.N): Belnap.N, (Belnap.N, Belnap.F): Belnap.F,
    (Belnap.F, Belnap.T): Belnap.F, (Belnap.F, Belnap.B): Belnap.F,
    (Belnap.F, Belnap.N): Belnap.F, (Belnap.F, Belnap.F): Belnap.F,
}


def belnap_and(a: Belnap, b: Belnap) -> Belnap:
    return _AND[(a, b)]


# ── Paraconsistent entry ──────────────────────────────────────────────────────

@dataclass
class ParaEntry:
    """A 12-primitive tuple with Belnap belief sets at each slot."""
    name: str
    belief: Dict[str, FrozenSet[str]]   # prim → frozenset of value tokens

    @classmethod
    def from_classical(cls, e: dict, name: str = None) -> "ParaEntry":
        """Wrap a classical entry (all singletons — T state)."""
        return cls(
            name=name or e.get("name", "?"),
            belief={p: frozenset({e[p]}) for p in PRIMITIVES},
        )

    def force_both(self, prim: str, val: str) -> "ParaEntry":
        """Return new entry with belief[prim] augmented by val (B-state if val is new)."""
        new_belief = {p: fs for p, fs in self.belief.items()}
        new_belief[prim] = self.belief.get(prim, frozenset()) | frozenset({val})
        return ParaEntry(
            name=f"B({self.name}; {prim}+{val})",
            belief=new_belief,
        )

    def force_assign(self, prim: str, vals: List[str]) -> "ParaEntry":
        """Return new entry with belief[prim] set to exactly vals."""
        new_belief = {p: fs for p, fs in self.belief.items()}
        new_belief[prim] = frozenset(vals)
        label = "{" + ",".join(sorted(vals)) + "}"
        return ParaEntry(
            name=f"assign({self.name}; {prim}={label})",
            belief=new_belief,
        )

    def belnap_for(self, prim: str, val: str) -> Belnap:
        """Belnap state of the claim 'belief[prim] contains val'."""
        b = self.belief.get(prim, frozenset())
        if not b:
            return Belnap.N
        if val in b:
            return Belnap.T if len(b) == 1 else Belnap.B
        return Belnap.F

    def is_classical(self) -> bool:
        return all(len(v) == 1 for v in self.belief.values())

    def b_primitives(self) -> List[str]:
        """Primitives currently in B-state (|belief| > 1)."""
        return [p for p in PRIMITIVES if len(self.belief.get(p, frozenset())) > 1]

    def n_primitives(self) -> List[str]:
        """Primitives currently in N-state (empty belief)."""
        return [p for p in PRIMITIVES if not self.belief.get(p, frozenset())]

    def classical_realizations(self) -> List[dict]:
        """All classical dicts consistent with this belief (exponential in |B-prims|)."""
        if any(not self.belief.get(p) for p in PRIMITIVES):
            return []
        prims = list(PRIMITIVES)
        val_lists = [
            sorted(self.belief[p], key=lambda v: int(ORDINALS[p][v]))
            for p in prims
        ]
        return [
            {p: v for p, v in zip(prims, combo)} | {"name": self.name}
            for combo in iproduct(*val_lists)
        ]

    def realization_count(self) -> int:
        r = 1
        for p in PRIMITIVES:
            r *= len(self.belief.get(p, frozenset()))
        return r


# ── Paraconsistent algebra ────────────────────────────────────────────────────

def _min_v(p: str, a: str, b: str) -> str:
    return a if int(ORDINALS[p][a]) <= int(ORDINALS[p][b]) else b


def _max_v(p: str, a: str, b: str) -> str:
    return a if int(ORDINALS[p][a]) >= int(ORDINALS[p][b]) else b


def para_tensor(a: ParaEntry, b: ParaEntry) -> ParaEntry:
    """Paraconsistent tensor: min for bottleneck prims, max for rest."""
    result = {}
    for p in PRIMITIVES:
        op = _min_v if p in _BOTTLENECK_PRIMS else _max_v
        result[p] = frozenset(
            op(p, av, bv)
            for av in a.belief.get(p, frozenset())
            for bv in b.belief.get(p, frozenset())
        )
    return ParaEntry(name=f"para⊗({a.name}, {b.name})", belief=result)


def para_join(a: ParaEntry, b: ParaEntry) -> ParaEntry:
    """Lattice join: pure max, no bottleneck."""
    result = {
        p: frozenset(_max_v(p, av, bv) for av in a.belief[p] for bv in b.belief[p])
        for p in PRIMITIVES
    }
    return ParaEntry(name=f"para∨({a.name}, {b.name})", belief=result)


def para_meet(a: ParaEntry, b: ParaEntry) -> ParaEntry:
    """Lattice meet: pure min."""
    result = {
        p: frozenset(_min_v(p, av, bv) for av in a.belief[p] for bv in b.belief[p])
        for p in PRIMITIVES
    }
    return ParaEntry(name=f"para∧({a.name}, {b.name})", belief=result)


# ── Paraconsistent tier ───────────────────────────────────────────────────────

_MAX_REALIZATIONS = 256   # cap to avoid exponential blow-up


def para_tier(e: ParaEntry) -> Dict[str, Belnap]:
    """
    For each tier key, return its Belnap truth value.

    T: every realization achieves this tier
    F: no  realization achieves this tier
    B: some realizations achieve it, others don't
    N: empty belief set — no realizations possible
    """
    if e.realization_count() > _MAX_REALIZATIONS:
        return {t: Belnap.N for t in TIER_ORDER}

    realizations = e.classical_realizations()
    if not realizations:
        return {t: Belnap.N for t in TIER_ORDER}

    tier_counts: Dict[str, int] = {}
    total = len(realizations)
    for r in realizations:
        t = compute_tier(r)
        tier_counts[t] = tier_counts.get(t, 0) + 1

    result = {}
    for t in TIER_ORDER:
        count = tier_counts.get(t, 0)
        if count == 0:
            result[t] = Belnap.F
        elif count == total:
            result[t] = Belnap.T
        else:
            result[t] = Belnap.B
    return result


def para_tier_compact(e: ParaEntry) -> str:
    """Compact string: 'T:O_inf  B:O_2dag  F:...' (non-F tiers only)."""
    pt = para_tier(e)
    parts = [
        f"{_SYM[v]}:{t}"
        for t in sorted(TIER_ORDER, key=lambda x: TIER_ORDER[x])
        if (v := pt[t]) != Belnap.F
    ]
    return "  ".join(parts) if parts else "all-F"


# ── Tier condition Belnap breakdown ───────────────────────────────────────────

def _tier_conditions(e: ParaEntry) -> Dict[str, Belnap]:
    """
    Return Belnap values for the four primitive conditions that determine tier:

      crit:  ⊙ ≥ ord 1       (required for O_1, O_2, O_2dag, O_inf)
      frob:  Φ = 𐑹          (required for O_inf)
      wind:  Ω ≥ ord 1        (distinguishes O_1 from O_2/O_2dag)
      dinf:  Ð ≥ ord 2        (distinguishes O_2 from O_2dag)
    """
    def belnap_threshold(prim: str, threshold: int) -> Belnap:
        vals = e.belief.get(prim, frozenset())
        if not vals:
            return Belnap.N
        above = sum(1 for v in vals if int(ORDINALS[prim][v]) >= threshold)
        if above == len(vals):
            return Belnap.T
        if above == 0:
            return Belnap.F
        return Belnap.B

    frob_vals = e.belief.get("Φ", frozenset())
    if not frob_vals:
        frob = Belnap.N
    else:
        frob_count = sum(1 for v in frob_vals if v == _FROB_VAL)
        if frob_count == len(frob_vals):
            frob = Belnap.T
        elif frob_count == 0:
            frob = Belnap.F
        else:
            frob = Belnap.B

    return {
        "crit": belnap_threshold("⊙", 1),
        "frob": frob,
        "wind": belnap_threshold("Ω", 1),
        "dinf": belnap_threshold("Ð", 2),
    }


# ── Display helpers ───────────────────────────────────────────────────────────

PARA_HELP = """
Paraconsistent commands — Belnap FOUR over the 12-primitive crystal lattice

  :para-cliff [name]              Frobenius cliff: force Φ → B{v,𐑹}, trace propagation
  :para-tensor <A> <B>            paraconsistent tensor (belief cross-products)
  :para-reach <name>              Belnap tier-reachability (T/F/B/N per tier)
  :para-assign <name> <p> <v...>  set belief[p] = {v1, v2, ...}
  :para-compare <A> <B>           belief-set comparison per primitive
  :para-help                      this message

Belnap states:
  T = true    all classical realizations satisfy this property
  F = false   no  classical realization satisfies this property
  B = both    some satisfy, some do not (overdetermined — the interesting case)
  N = neither empty belief set (underdetermined — no classical realization)

Interpretation:
  A B-state at Φ means the entry is simultaneously ZFC-level (𐑗) and
  ZFCₜ-level (𐑹). The Frobenius min-bottleneck preserves this B-state through
  tensor composition — it does NOT collapse to T automatically.

  A classical proof of an MPP axiom is a demonstration that the B-state collapses
  to T for 𐑹: the mathematical object (zeta zeros, YM measure, NS cascade) is
  shown to genuinely carry Frobenius structure. The B-state is not a shortcut —
  it is a precise statement of what the proof must accomplish.
""".strip()


def _show_para_entry(e: ParaEntry, console=None):
    """Display ParaEntry with Belnap state per primitive."""
    tier_str  = para_tier_compact(e)
    conds     = _tier_conditions(e)
    b_prims   = e.b_primitives()
    cond_line = ("  ".join(f"{k}:{_SYM[v]}" for k, v in conds.items()))

    title = f"{e.name}  |  tier: {tier_str}  |  cond: {cond_line}"

    if console:
        from rich.table import Table
        tbl = Table(title=title, show_header=True, header_style="bold cyan")
        tbl.add_column("Prim", width=5, style="bold")
        tbl.add_column("Belief set", width=36)
        tbl.add_column("State", width=6)
        tbl.add_column("Ords", width=14)
        for p in PRIMITIVES:
            vals = sorted(e.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
            state = (Belnap.N if not vals else
                     Belnap.T if len(vals) == 1 else Belnap.B)
            col   = _COLOR[state]
            ords  = " ".join(str(int(ORDINALS[p][v])) for v in vals)
            tbl.add_row(
                p,
                "{ " + ", ".join(vals) + " }",
                f"[{col}]{_SYM[state]}[/{col}]",
                ords,
            )
        console.print(tbl)
        if b_prims:
            console.print(f"  [magenta]B-state primitives: {', '.join(b_prims)}[/magenta]  "
                          f"({e.realization_count()} realizations)")
    else:
        print(f"\n{title}")
        print(f"  {'Prim':<5}  {'Belief set':<36}  State  Ords")
        print(f"  {'─'*5}  {'─'*36}  {'─'*5}  {'─'*14}")
        for p in PRIMITIVES:
            vals = sorted(e.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
            state = (Belnap.N if not vals else
                     Belnap.T if len(vals) == 1 else Belnap.B)
            ords  = " ".join(str(int(ORDINALS[p][v])) for v in vals)
            bset  = "{ " + ", ".join(vals) + " }"
            print(f"  {p:<5}  {bset:<36}  {_SYM[state]:<5}  {ords}")
        if b_prims:
            print(f"\n  B-state primitives: {', '.join(b_prims)}"
                  f"  ({e.realization_count()} realizations)")


# ── ParaManipulator ───────────────────────────────────────────────────────────

class ParaManipulator(ZFCTriangleManipulator):
    """Extends ZFCTriangleManipulator with Belnap paraconsistent analysis."""

    def _resolve_para(self, name: str) -> Optional[ParaEntry]:
        """Resolve name to a ParaEntry (classical singleton belief sets)."""
        e = self.resolve(name)
        if e is None:
            return None
        return ParaEntry.from_classical(_normalize(e), name=e.get("name", name))

    # ── :para-cliff ───────────────────────────────────────────────────────────

    def cmd_para_cliff(self, name: str = "imaginary_unit", console=None):
        """
        Force Φ from its current value to B{current, 𐑹}, then trace what
        happens when para_tensor is applied with ZFCₜ.

        Shows:
          - Classical entry (T-state) and its tier
          - B-forced entry (Φ in B-state) and its para-tier
          - para_tensor(B-forced, ZFCₜ) — does 𐑹 survive?
          - Whether the B-state collapses, propagates, or is blocked
        """
        pe = self._resolve_para(name)
        if pe is None:
            print(f"  [not found] '{name}'"); return

        zfct_classical = _normalize(ZFCT_TUPLE)
        pe_zfct = ParaEntry.from_classical(zfct_classical, name="ZFCₜ")

        # classical baseline
        classical_dict = {p: list(pe.belief[p])[0] for p in PRIMITIVES}
        classical_tier = compute_tier(classical_dict | {"name": pe.name})

        phi_current = list(pe.belief["Φ"])[0] if len(pe.belief["Φ"]) == 1 else None

        if phi_current == _FROB_VAL:
            msg = (f"  {pe.name}: Φ already = 𐑹 (Frobenius) — no cliff for this entry.\n"
                   f"  tier = {classical_tier}  (T:O_inf)")
            if console:
                console.print(f"[green]{msg}[/green]")
            else:
                print(msg)
            return

        # force Φ to B{current, 𐑹}
        pe_b = pe.force_both("Φ", _FROB_VAL)

        # para-tensor of B-forced entry with ZFCₜ
        pe_tensored = para_tensor(pe_b, pe_zfct)

        # tier analyses
        tier_orig    = para_tier(pe)
        tier_b       = para_tier(pe_b)
        tier_tensored = para_tier(pe_tensored)

        cond_orig     = _tier_conditions(pe)
        cond_b        = _tier_conditions(pe_b)
        cond_tensored = _tier_conditions(pe_tensored)

        # Φ-state in tensored result
        phi_tensored   = pe_tensored.belief.get("Φ", frozenset())
        frob_in_result = _FROB_VAL in phi_tensored
        b_after        = len(phi_tensored) > 1

        # interpretation
        if len(phi_tensored) == 1 and _FROB_VAL in phi_tensored:
            interpretation = ("COLLAPSE TO T: para_tensor collapsed Φ to 𐑹 alone.\n"
                              "  This means ZFCₜ dominates at Φ — the Frobenius gate is "
                              "fully open in the result.\n"
                              "  In practice this cannot happen for entries below 𐑹: "
                              "the min-bottleneck blocks it.")
        elif b_after:
            phi_ords = sorted(phi_tensored, key=lambda v: int(ORDINALS["Φ"][v]))
            interpretation = (
                f"B-STATE PROPAGATES: Φ remains overdetermined = {{{', '.join(phi_ords)}}}.\n"
                f"  The min-bottleneck preserved the lower value ({phi_ords[0]}) alongside 𐑹.\n"
                f"  The tier is B:{tier_tensored.get('O_inf', Belnap.F).value} for O_inf.\n"
                f"  A classical proof must show 𐑗 is NOT a valid assignment — i.e., that\n"
                f"  the mathematical object in question genuinely has Frobenius structure.\n"
                f"  The B-state is the proof obligation, not a proof.")
        else:
            interpretation = (
                f"CLIFF HOLDS: Φ = {list(phi_tensored)[0]} — Frobenius was not reached.\n"
                f"  The min-bottleneck completely blocked 𐑹.\n"
                f"  No composition with ZFCₜ can synthesize 𐑹 from this starting point.")

        lines = [
            f"Frobenius cliff (paraconsistent):  {pe.name}",
            "",
            f"  Classical:   Φ = {phi_current}  (ord {int(ORDINALS['Φ'][phi_current])})  "
            f"tier = {classical_tier}",
            f"  B-forced:    Φ ∈ {{{phi_current}, {_FROB_VAL}}}  "
            f"para-tier: {para_tier_compact(pe_b)}",
            f"  ⊗ ZFCₜ:      Φ ∈ {{{', '.join(sorted(phi_tensored, key=lambda v: int(ORDINALS['Φ'][v])))}}}  "
            f"para-tier: {para_tier_compact(pe_tensored)}",
            "",
            "  Tier conditions (crit / frob / wind / dinf):",
            f"    original:  {cond_line(cond_orig)}",
            f"    B-forced:  {cond_line(cond_b)}",
            f"    tensored:  {cond_line(cond_tensored)}",
            "",
            "  Interpretation:",
        ] + [f"    {l}" for l in interpretation.split("\n")]

        if console:
            from rich.panel import Panel
            bstyle = ("green" if len(phi_tensored) == 1 and frob_in_result
                      else "magenta" if b_after else "red")
            console.print(Panel("\n".join(lines),
                                title="[bold]Para-Cliff Analysis[/bold]",
                                border_style=bstyle))
        else:
            for line in lines:
                print(line)

    # ── :para-tensor ──────────────────────────────────────────────────────────

    def cmd_para_tensor(self, name_a: str, name_b: str, console=None):
        pa = self._resolve_para(name_a)
        pb = self._resolve_para(name_b)
        if pa is None:
            print(f"  [not found] '{name_a}'"); return
        if pb is None:
            print(f"  [not found] '{name_b}'"); return

        result = para_tensor(pa, pb)
        _show_para_entry(result, console=console)

        # extra: compare to classical tensor
        ca = {p: list(pa.belief[p])[0] for p in PRIMITIVES if len(pa.belief[p]) == 1}
        cb = {p: list(pb.belief[p])[0] for p in PRIMITIVES if len(pb.belief[p]) == 1}
        if len(ca) == 12 and len(cb) == 12:
            classical_r = tensor_tuples(ca | {"name": pa.name}, cb | {"name": pb.name})
            classical_tier = compute_tier(classical_r | {"name": "classical"})
            msg = f"\n  (classical tensor tier: {classical_tier})"
            if console:
                console.print(msg)
            else:
                print(msg)

    # ── :para-reach ───────────────────────────────────────────────────────────

    def cmd_para_reach(self, name: str, console=None):
        """
        Show Belnap tier-reachability and the four tier conditions for this entry.
        """
        pe = self._resolve_para(name)
        if pe is None:
            print(f"  [not found] '{name}'"); return

        pt    = para_tier(pe)
        conds = _tier_conditions(pe)
        n_r   = pe.realization_count()
        b_ps  = pe.b_primitives()

        lines = [
            f"Para-reach:  {pe.name}  ({n_r} realization(s))",
            "",
            "  Tier          Belnap  Description",
            "  " + "─"*65,
        ]
        for t in sorted(TIER_ORDER, key=lambda x: TIER_ORDER[x]):
            v   = pt[t]
            sym = _SYM[v]
            lbl = TIER_LABELS.get(t, t)
            lines.append(f"  {t:<10}    {sym}       {lbl}")

        lines += [
            "",
            "  Tier conditions:",
            f"    crit  (⊙ ≥ 1):   {_SYM[conds['crit']]}",
            f"    frob  (Φ = 𐑹): {_SYM[conds['frob']]}",
            f"    wind  (Ω ≥ 1):   {_SYM[conds['wind']]}",
            f"    dinf  (Ð ≥ 2):   {_SYM[conds['dinf']]}",
        ]

        if b_ps:
            lines += ["", f"  B-state primitives: {', '.join(b_ps)}"]

        o_inf_state = pt.get("O_inf", Belnap.F)
        if o_inf_state == Belnap.T:
            lines += ["", "  ✓ O_inf is T: entry definitly carries Frobenius structure."]
        elif o_inf_state == Belnap.B:
            lines += [
                "",
                "  ◈ O_inf is B: entry is consistent with Frobenius but not confirmed.",
                "    Proof obligation: show Φ = 𐑹 is the only valid assignment.",
            ]
        elif o_inf_state == Belnap.F:
            lines += [
                "",
                f"  ✗ O_inf is F: Frobenius not reached. Gap: {4 - int(ORDINALS['Φ'][list(pe.belief['Φ'])[0] if pe.belief['Φ'] else '𐑗'])} step(s) in Φ.",
            ]

        if console:
            from rich.panel import Panel
            bstyle = (_COLOR[o_inf_state])
            console.print(Panel("\n".join(lines),
                                title="[bold cyan]Para-Reach[/bold cyan]",
                                border_style=bstyle))
        else:
            for line in lines:
                print(line)

    # ── :para-assign ──────────────────────────────────────────────────────────

    def cmd_para_assign(self, name: str, prim: str, vals: List[str], console=None):
        pe = self._resolve_para(name)
        if pe is None:
            print(f"  [not found] '{name}'"); return
        if prim not in ORDINALS:
            print(f"  [error] unknown primitive '{prim}'. Valid: {', '.join(PRIMITIVES)}"); return
        for v in vals:
            if v not in ORDINALS[prim]:
                print(f"  [error] unknown value '{v}' for {prim}."); return

        result = pe.force_assign(prim, vals)
        _show_para_entry(result, console=console)

    # ── :para-compare ─────────────────────────────────────────────────────────

    def cmd_para_compare(self, name_a: str, name_b: str, console=None):
        pa = self._resolve_para(name_a)
        pb = self._resolve_para(name_b)
        if pa is None:
            print(f"  [not found] '{name_a}'"); return
        if pb is None:
            print(f"  [not found] '{name_b}'"); return

        tier_a = para_tier_compact(pa)
        tier_b = para_tier_compact(pb)

        if console:
            from rich.table import Table
            tbl = Table(
                title=f"para-compare: {pa.name}  vs  {pb.name}",
                show_header=True, header_style="bold cyan",
            )
            tbl.add_column("Prim", width=5, style="bold")
            tbl.add_column(f"A: {pa.name[:18]}", width=28)
            tbl.add_column(f"B: {pb.name[:18]}", width=28)
            tbl.add_column("Same?", width=6)
            for p in PRIMITIVES:
                va = sorted(pa.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
                vb = sorted(pb.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
                same = "=" if va == vb else ""
                sa = Belnap.T if len(va) == 1 else (Belnap.B if va else Belnap.N)
                sb = Belnap.T if len(vb) == 1 else (Belnap.B if vb else Belnap.N)
                ca = _COLOR[sa]; cb = _COLOR[sb]
                tbl.add_row(
                    p,
                    f"[{ca}]{{" + ", ".join(va) + f"}}[/{ca}]",
                    f"[{cb}]{{" + ", ".join(vb) + f"}}[/{cb}]",
                    same,
                )
            console.print(tbl)
            console.print(f"  A para-tier: {tier_a}")
            console.print(f"  B para-tier: {tier_b}")
        else:
            print(f"\npara-compare: {pa.name}  vs  {pb.name}")
            print(f"  {'Prim':<5}  {'A belief':<28}  {'B belief':<28}  Same")
            print(f"  {'─'*5}  {'─'*28}  {'─'*28}  {'─'*4}")
            for p in PRIMITIVES:
                va = sorted(pa.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
                vb = sorted(pb.belief.get(p, frozenset()), key=lambda v: int(ORDINALS[p][v]))
                sa = "{" + ", ".join(va) + "}"
                sb = "{" + ", ".join(vb) + "}"
                same = "=" if va == vb else ""
                print(f"  {p:<5}  {sa:<28}  {sb:<28}  {same}")
            print(f"\n  A para-tier: {tier_a}")
            print(f"  B para-tier: {tier_b}")

    # ── Extended REPL ─────────────────────────────────────────────────────────

    def run_repl(self):
        try:
            from rich.console import Console
            from rich.prompt import Prompt
            console = Console()
        except ImportError:
            console = None

        if console:
            console.print(
                "[bold cyan]ZFC/ZFCₜ/ZFCₛ Para-Manipulator[/bold cyan]"
                "  —  Belnap FOUR paraconsistent layer  —  :help / :para-help"
            )
            console.print(
                f"  catalog: {len(self.catalog)} entries  "
                "| para commands: :para-cliff  :para-tensor  :para-reach  :para-assign  :para-compare"
            )
        else:
            print("ZFC/ZFCₜ/ZFCₛ Para-Manipulator — :help / :para-help for commands")
            print(f"  catalog: {len(self.catalog)} entries")

        while True:
            try:
                if console:
                    raw = Prompt.ask("\n[bold magenta]⟨IG∥⟩[/bold magenta]")
                else:
                    raw = input("\n⟨IG∥⟩ ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                break

            parts = raw.strip().split()
            if not parts:
                continue
            cmd  = parts[0].lower()
            args = parts[1:]

            if cmd in (":quit", ":exit", ":q"):
                print("bye."); break

            elif cmd == ":para-help":
                if console:
                    from rich.panel import Panel
                    console.print(Panel(PARA_HELP, title="Para-Help", border_style="magenta"))
                else:
                    print(PARA_HELP)

            elif cmd == ":para-cliff":
                self.cmd_para_cliff(args[0] if args else "imaginary_unit", console)

            elif cmd == ":para-tensor":
                if len(args) < 2:
                    print("  usage: :para-tensor <A> <B>")
                else:
                    self.cmd_para_tensor(args[0], " ".join(args[1:]), console)

            elif cmd == ":para-reach":
                if not args:
                    print("  usage: :para-reach <name>")
                else:
                    self.cmd_para_reach(" ".join(args), console)

            elif cmd == ":para-assign":
                if len(args) < 3:
                    print("  usage: :para-assign <name> <prim> <val1> [<val2> ...]")
                else:
                    self.cmd_para_assign(args[0], args[1], args[2:], console)

            elif cmd == ":para-compare":
                if len(args) < 2:
                    print("  usage: :para-compare <A> <B>")
                else:
                    self.cmd_para_compare(args[0], " ".join(args[1:]), console)

            # fall through to parent REPL commands
            else:
                self._dispatch_parent(cmd, args, raw, console)

    def _dispatch_parent(self, cmd: str, args: list, raw: str, console=None):
        """Route non-para commands to the parent manipulator's handlers."""
        from zfct_manipulator import HELP_TEXT as _MHELP
        parts = raw.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in (":help",):
            from zfct_zfcs_zfc_manipulator import HELP_TEXT
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
            if args:
                self.cmd_clauses(" ".join(args), console)
        elif cmd == ":tier":
            if args:
                self.cmd_tier(" ".join(args), console)
        elif cmd in (":tensor", ":join", ":meet"):
            if len(args) >= 2:
                self.cmd_binary(cmd[1:], args[0], " ".join(args[1:]), console)
        elif cmd == ":compare":
            if len(args) >= 2:
                self.cmd_compare(args[0], " ".join(args[1:]), console)
        elif cmd == ":barrier":
            if len(args) >= 2:
                self.cmd_barrier(args[0], " ".join(args[1:]), console)
        elif cmd == ":distance":
            if len(args) >= 2:
                self.cmd_distance(args[0], " ".join(args[1:]), console)
        elif cmd == ":lift":
            if len(args) >= 3:
                self.cmd_lift(args[0], args[1], args[2], console)
        elif cmd == ":lattice":
            self.cmd_lattice(console)
        elif cmd in (":promotions-dual", ":promos", ":dual"):
            self.cmd_promotions_dual(console)
        elif cmd == ":cliff":
            self.cmd_cliff(args[0] if args else "imaginary_unit", console)
        elif cmd == ":rules":
            self.cmd_rules(console)
        elif cmd == ":scan":
            n = int(args[0]) if args else 100
            self.cmd_scan(n, console)
        else:
            msg = f"  unknown command '{cmd}' — try :help or :para-help"
            if console:
                console.print(f"[red]{msg}[/red]")
            else:
                print(msg)


# ── Helper used in para-cliff output ─────────────────────────────────────────

def cond_line(conds: Dict[str, Belnap]) -> str:
    return "  ".join(f"{k}:{_SYM[v]}" for k, v in conds.items())


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Belnap FOUR paraconsistent layer over the ZFC/ZFCₜ triangle"
    )
    parser.add_argument("--catalog", type=str, default=None)
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("repl",  help="interactive REPL (default)")

    pc = sub.add_parser("cliff",  help="para-cliff analysis for one entry")
    pc.add_argument("name", nargs="?", default="imaginary_unit")

    pr = sub.add_parser("reach",  help="para-reach for one entry")
    pr.add_argument("name")

    args = parser.parse_args()
    manip = ParaManipulator(catalog_path=args.catalog)

    if args.cmd == "cliff":
        manip.cmd_para_cliff(args.name)
    elif args.cmd == "reach":
        manip.cmd_para_reach(args.name)
    else:
        manip.run_repl()
