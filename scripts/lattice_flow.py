"""Lattice cycling and weight flow over an IMASM word.

One implementation, several consumers: the grammar tools in `IG_inquiry.py`,
the ob3ect CLIs, and the MoDoT verbs all call in here rather than each carrying
their own copy of the rules.

Two questions are answered.

CYCLING. A word is a ring and ROTAT is the cyclic shift, so every rotation is
the same object. The verdict, the closed-walk flag and the topology class hold
across the whole orbit; the FINAL REGISTER does not. That makes the phase the
only handle on where a word comes to rest, and this prints the map from cut to
landing register so the handle can be read instead of guessed.

WEIGHT. The machine holds each open fork as a set and closes it with a union.
Union is idempotent, so a finished walk knows WHICH base values were touched
and nothing else: not how many times, not by which arm, not whether a value
reached the end or was destroyed and restored on the way. This records the
movement. Weight banked in a frame survives a clear that empties the register;
weight left in the open does not. The lift of OR to weights is MAX, not sum, so
at weights zero and one the accounting reduces to the set semantics exactly.

Two movements are recorded that carry no weight at all, because both are
otherwise invisible in a final register:

  SEED    AFWD and IMSCRIB assign `frozenset('T')` to an empty register
          directly, so a walk can land in T having carried nothing
  INERT   after IFIX the machine returns early for every token but IFIX and
          IMSCRIB, so a word can be almost entirely no-ops

Deterministic. No model, no network.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

_OB3ECT = Path(__file__).resolve().parent.parent.parent / "ob3ect" / "digital"
if str(_OB3ECT) not in sys.path:
    sys.path.insert(0, str(_OB3ECT))

from imasm16_3_core import (  # noqa: E402
    GLYPH, NAME_FROM_GLYPH, IMASM16_3_Machine,
    VINIT, AREV, AFWD, IMSCRIB, IFIX, FSPLIT3, FFUSE3, reg_name,
)

# The 12-op alphabet writes split and fuse as ◇ and ●; the trilattice core
# writes them ∈ and ∋. A word copied out of a bootstrap report is in the first,
# the machine reads the second. Silently dropping the unrecognised character is
# what a tool built to find that must not do.
ALIAS = {"◇": "∈", "●": "∋", "⊗": "∈", "⊕": "∋"}


def parse_word(text: str) -> Tuple[List[str], List[str]]:
    """Glyphs to token names. Anything outside the alphabet is returned, not eaten."""
    out, unknown = [], []
    for ch in text:
        if ch.isspace():
            continue
        tok = NAME_FROM_GLYPH.get(ALIAS.get(ch, ch))
        (out if tok else unknown).append(tok or ch)
    return out, unknown


def render(steps) -> str:
    return "".join(GLYPH.get(t, "?") for t in steps)


# ── the weighted machine ────────────────────────────────────────────────────
class WeightedMachine(IMASM16_3_Machine):
    """The machine, plus a ledger of every movement of weight.

    Subclassed rather than reimplemented so the transition rules stay the ones
    the pipeline uses and only the bookkeeping is added.
    """

    def __init__(self):
        super().__init__()
        self.ledger: List[Tuple[int, str, str, Dict]] = []
        self.reg_weight: Counter = Counter()
        self.frame_weight: List[Counter] = []
        self._step = 0

    def _touch(self, values):
        depth = len(self.split_stack)
        super()._touch(values)
        for v in values:
            self.reg_weight[v] += 1
            if self.frame_weight:
                self.frame_weight[-1][v] += 1
        self.ledger.append((self._step, None, "DEPOSIT",
                            {"values": sorted(values), "depth": depth}))

    def transition(self, token):
        self._step += 1
        before = Counter(self.reg_weight)

        if self.fixed and token not in (IFIX, IMSCRIB):
            self.ledger.append((self._step, GLYPH.get(token), "INERT", {}))
            return super().transition(token)

        if token == FSPLIT3:
            self.frame_weight.append(Counter())
            self.ledger.append((self._step, GLYPH.get(token), "OPEN",
                                {"depth": len(self.frame_weight)}))
        elif token == FFUSE3 and self.frame_weight:
            closed = self.frame_weight.pop()
            restored = {}
            for v, w in closed.items():
                if w > self.reg_weight[v]:
                    restored[v] = w - self.reg_weight[v]
                    self.reg_weight[v] = w
                if self.frame_weight:
                    self.frame_weight[-1][v] = max(self.frame_weight[-1][v], w)
            self.ledger.append((self._step, GLYPH.get(token), "FUSE",
                                {"held": dict(closed), "restored": restored,
                                 "into_depth": len(self.frame_weight)}))
        elif token in (AFWD, IMSCRIB) and not self.reg:
            self.ledger.append((self._step, GLYPH.get(token), "SEED",
                                {"value": "T"}))
        elif token in (AREV, VINIT):
            banked = sum(sum(f.values()) for f in self.frame_weight)
            self.ledger.append((self._step, GLYPH.get(token), "CLEAR",
                                {"lost": dict(before), "banked": banked}))
            self.reg_weight = Counter()
            if token == VINIT:
                self.frame_weight = []

        return super().transition(token)


def run_weighted(steps) -> WeightedMachine:
    m = WeightedMachine()
    m.reset()
    m.reg_weight, m.frame_weight, m.ledger, m._step = Counter(), [], [], 0
    for tok in steps:
        m.transition(tok)
    return m


# ── the two readouts ────────────────────────────────────────────────────────
def cycle(steps) -> Dict:
    """Every rotation, with its readouts and the map from cut to landing."""
    n = len(steps)
    rows = []
    for k in range(n):
        rot = steps[k:] + steps[:k]
        m = run_weighted(rot)
        rows.append({
            "k": k,
            "word": render(rot),
            "final_register": reg_name(m.reg),
            "restored": sum(sum(d["restored"].values())
                            for _, _, kind, d in m.ledger if kind == "FUSE"),
            "cleared": sum(sum(d["lost"].values())
                           for _, _, kind, d in m.ledger if kind == "CLEAR"),
            "deposits": sum(1 for _, _, kind, _ in m.ledger if kind == "DEPOSIT"),
            "inert": sum(1 for _, _, kind, _ in m.ledger if kind == "INERT"),
            "seeded": sum(1 for _, _, kind, _ in m.ledger if kind == "SEED"),
            "surviving": {v: w for v, w in sorted(m.reg_weight.items())},
        })
    landings: Dict[str, List[int]] = {}
    for r in rows:
        landings.setdefault(r["final_register"], []).append(r["k"])
    moving = [f for f in ("final_register",)
              if len({r[f] for r in rows}) > 1]
    return {"status": "ok", "word": render(steps), "period": n,
            "orbit": rows, "landing_by_cut": landings,
            "phase_bearing": moving or ["nothing"]}


def weight(steps) -> Dict:
    """Where the weight moves through one word."""
    m = run_weighted(steps)
    moves = []
    for step, glyph, kind, d in m.ledger:
        g = glyph or GLYPH.get(steps[step - 1], "?")
        moves.append({"step": step, "glyph": g, "kind": kind, **d})
    return {
        "status": "ok",
        "word": render(steps),
        "final_register": reg_name(m.reg),
        "movement": moves,
        "surviving": {v: w for v, w in sorted(m.reg_weight.items())},
        "stranded": sum(sum(f.values()) for f in m.frame_weight),
        "deposits": sum(1 for x in moves if x["kind"] == "DEPOSIT"),
        "cleared": sum(sum(x["lost"].values()) for x in moves if x["kind"] == "CLEAR"),
        "restored": sum(sum(x["restored"].values()) for x in moves if x["kind"] == "FUSE"),
        "seeded": sum(1 for x in moves if x["kind"] == "SEED"),
        "inert": sum(1 for x in moves if x["kind"] == "INERT"),
    }


def insertion_grid(steps, glyph: str) -> Dict:
    """One token placed at every index of every rotation.

    Appending is insertion at the seam, so the seam is a column here and not a
    separate operation. A constant row means the index does not matter at that
    cut; a constant column means the cut does not matter at that index.
    """
    tok = NAME_FROM_GLYPH.get(ALIAS.get(glyph, glyph))
    if tok is None:
        return {"status": "error", "error": f"'{glyph}' is not in the alphabet",
                "alphabet": list(GLYPH.values())}
    n = len(steps)
    grid = []
    for k in range(n):
        rot = steps[k:] + steps[:k]
        grid.append([reg_name(run_weighted(rot[:i] + [tok] + rot[i:]).reg)
                     for i in range(len(rot) + 1)])
    cols = list(zip(*grid))
    return {
        "status": "ok", "glyph": glyph, "token": tok, "grid": grid,
        "rotations_where_index_is_irrelevant":
            [k for k, row in enumerate(grid) if len(set(row)) == 1],
        "indices_where_rotation_is_irrelevant":
            [i for i, col in enumerate(cols) if len(set(col)) == 1],
        "reachable": sorted({c for row in grid for c in row}),
    }


def banked_count_check(steps) -> Dict:
    """Was anything counted, then destroyed by a clear that a frame would have held?

    AREV empties the register and leaves open frames alone, so a count fused
    back to depth zero is exposed to the next reversal while the same count held
    one level up survives it. A proof that counts, reverses, then bounds must
    bank the count in an enclosing region before the reversal.

    The signature is a CLEAR losing weight with nothing banked behind it. What
    the fix costs is one nesting: open the region that will hold the result
    before opening the region that computes it, and close them in that order.
    """
    m = run_weighted(steps)
    exposed, live_clears = [], 0
    for step, glyph, kind, d in m.ledger:
        if kind == "CLEAR" and d["lost"]:
            live_clears += 1
            if d["banked"] == 0:
                exposed.append({"step": step, "glyph": glyph,
                                "lost": dict(d["lost"]),
                                "weight": sum(d["lost"].values())})
    total_lost = sum(e["weight"] for e in exposed)
    # THE SECOND FACT. Banking and surplus are independent, proved in
    # p4ramill Imscribing/IMASM/BankedWeight.lean. Whether ANYTHING is banked
    # depends on a frame being open when the clear fires; whether the SURPLUS
    # is kept depends on where the splits fall between deposits of the same
    # value. Deposits inside one region accumulate, the fold between regions
    # takes a maximum, so a value deposited in two sibling regions comes back
    # as one. A word can bank correctly and still discard a surplus.
    surplus = {}
    for step, glyph, kind, d in m.ledger:
        if kind == "CLEAR" and d["lost"] and d["banked"]:
            lost_here = d["lost"]
            back = {}
            for _, _, k2, d2 in m.ledger:
                if k2 == "FUSE":
                    for v, w in d2.get("restored", {}).items():
                        back[v] = max(back.get(v, 0), w)
            for v, w in lost_here.items():
                short = w - back.get(v, 0)
                if short > 0:
                    surplus[v] = surplus.get(v, 0) + short
    total_surplus = sum(surplus.values())
    inert = sum(1 for _, _, k, _ in m.ledger if k == "INERT")
    deposits = sum(1 for _, _, k, _ in m.ledger if k == "DEPOSIT")
    restored = sum(sum(d["restored"].values())
                   for _, _, k, d in m.ledger if k == "FUSE")
    # Passing because nothing was ever at risk is not the same as passing
    # because the frame held. A word whose clears never fire reads identically
    # to one that banked correctly, and the difference is the whole content of
    # the check.
    vacuous = not exposed and live_clears == 0
    return {
        "status": "ok",
        "word": render(steps),
        "exposed_clears": exposed,
        "weight_lost_in_the_open": total_lost,
        "banked_ok": not exposed,
        "vacuous": vacuous,
        "surplus_discarded": surplus,
        "surplus_total": total_surplus,
        "live_clears": live_clears,
        "restored": restored,
        "deposits": deposits,
        "inert": inert,
        "verdict": (
            f"{total_lost} unit(s) of weight cleared with nothing banked behind "
            f"them: the count was in the open when the reversal came"
            if exposed else
            (f"nothing was at risk: no clear ever fired against a live register"
             + (f" ({inert} step(s) inert after a fixation)" if inert else "")
             + (f", {deposits} deposit(s) made" if deposits else ", nothing deposited"))
            if vacuous else
            f"{restored} unit(s) survived a clear by being banked in a frame "
            f"({live_clears} live clear(s))"
            + (f"; {total_surplus} further unit(s) flattened by a fold between "
               f"sibling regions and not restored" if total_surplus else "")),
        "surplus_note": None if not total_surplus else
                        "a split between two deposits of the same value puts them "
                        "in sibling regions; the fold keeps the larger rather than "
                        "the sum. Put them in one region to keep both.",
        "remedy": None if not exposed else
                  "open the region that holds the result BEFORE the region that "
                  "computes it, and close them in that order, so the inner fuse "
                  "folds into the enclosing frame rather than into the register",
    }
