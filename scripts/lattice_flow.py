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
    # Every field the orbit carries is a candidate, not just the landing. An
    # earlier form checked `final_register` alone and so reported that as the
    # only phase-bearing statistic in words where `restored` swung from full to
    # nothing across the cut. A statistic that moves under rotation is reading
    # the cut, and the point of naming them is to catch exactly that.
    fields = [f for f in rows[0] if f != "k"] if rows else []
    moving = [f for f in fields
              if len({repr(r[f]) for r in rows}) > 1]
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


# ── the ring ────────────────────────────────────────────────────────────────
def transitions(steps) -> Dict:
    """Opcode-to-opcode transitions, counted ON THE RING.

    A word is a cycle and ROTAT is the cyclic shift, so a word of length n has n
    transitions, not n-1. The missing one is the wrap from the last opcode back
    to the first, and it is the edge that makes the word a cycle rather than a
    list. Read linearly, a corpus of k programs loses exactly k transitions, all
    of them closing edges, and in IMASM those are overwhelmingly TANCH -> VINIT:
    the anchor returning to the source. A transition table built without them
    can show a rule as universal that the closing edges break.
    """
    n = len(steps)
    if n == 0:
        return {"status": "ok", "ring": {}, "linear": {}, "dropped": []}
    ring, linear = Counter(), Counter()
    for i in range(n):
        pair = (steps[i], steps[(i + 1) % n])
        ring[pair] += 1
        if i < n - 1:
            linear[pair] += 1
    wrap = (steps[-1], steps[0])
    return {
        "status": "ok",
        "length": n,
        "ring_count": sum(ring.values()),
        "linear_count": sum(linear.values()),
        "wrap": f"{GLYPH.get(wrap[0], '?')} -> {GLYPH.get(wrap[1], '?')}",
        "ring": {f"{GLYPH.get(a,'?')}->{GLYPH.get(b,'?')}": c
                 for (a, b), c in ring.most_common()},
        "note": ("the ring carries one more transition than the linear read: the "
                 "closing edge, here " + f"{GLYPH.get(wrap[0],'?')} -> {GLYPH.get(wrap[1],'?')}"),
    }


def rotation_invariant(steps, stat) -> Dict:
    """Does a statistic survive rotation, or is it reading the cut?

    Anything computed from ABSOLUTE position on a ring measures where the word
    was cut, not the word: rows of a matrix, tiers of a tetraktys, odd against
    even positions. One rotation moves every value into a different row. This
    runs `stat` over the whole orbit and says whether it moved.

    `stat` takes a list of token names and returns anything comparable.
    """
    n = len(steps)
    vals = []
    for k in range(n):
        rot = steps[k:] + steps[:k]
        try:
            vals.append(stat(rot))
        except Exception as exc:
            return {"status": "error", "error": f"stat failed at k={k}: {exc}"}
    distinct = {repr(v) for v in vals}
    return {
        "status": "ok",
        "invariant": len(distinct) == 1,
        "distinct_values": len(distinct),
        "by_cut": {k: vals[k] for k in range(n)} if len(distinct) > 1 else vals[0],
        "verdict": ("survives rotation: a property of the word" if len(distinct) == 1
                    else f"MOVES under rotation ({len(distinct)} values): this reads "
                         f"the cut, not the word"),
    }


# ── hyperdimensional gematria ───────────────────────────────────────────────
_OPCODE_ORDER = ["VINIT", "TANCH", "AFWD", "AREV", "CLINK", "IMSCRIB",
                 "FSPLIT3", "FFUSE3", "EVALT", "EVALF", "EVALI", "IFIX"]
_ORDINAL = {n: i + 1 for i, n in enumerate(_OPCODE_ORDER)}
_REGISTERS = ["N", "T", "F", "TF", "t", "Tt", "Ft", "TFt",
              "f", "Tf", "Ff", "TFf", "tf", "Ttf", "Ftf", "A"]


def _ring_pairs_and_depth(steps):
    """Pair count and greatest depth, read as a LOOP.

    A linear scan starts wherever the word was cut, so a region the cut passes
    through is counted as an unmatched fuse followed by an unmatched split, and
    both the pair count and the depth move with the rotation. By the cycle
    lemma, when splits and fuses balance there is a start from which the stack
    never underflows; read from there, both are properties of the word.
    """
    n = len(steps)
    if n == 0:
        return 0, 0
    splits = [i for i, t in enumerate(steps) if t == FSPLIT3]
    starts = [0] + splits
    best = None
    for st in starts:
        d = mx = pr = 0
        ok = True
        for j in range(n):
            t = steps[(st + j) % n]
            if t == FSPLIT3:
                d += 1
                mx = max(mx, d)
            elif t == FFUSE3:
                if d == 0:
                    ok = False
                else:
                    d -= 1
                    pr += 1
        if ok and (best is None or pr > best[0]):
            best = (pr, mx)
    if best is None:
        # genuinely unbalanced: real structure, reported as the linear read sees it
        d = mx = pr = 0
        for t in steps:
            if t == FSPLIT3:
                d += 1; mx = max(mx, d)
            elif t == FFUSE3 and d > 0:
                d -= 1; pr += 1
        return pr, mx
    return best


def hyper_gematria(word_steps) -> Dict:
    """A high-dimensional signature of an IMASM word, every coordinate of which
    survives rotation.

    A word is a ring. Any coordinate read from absolute position measures where
    the word was cut and not the word, so a signature built from rows, tiers or
    odd-against-even positions describes the cut. Every coordinate here is
    either a multiset over the whole word, a count on the ring, or an aggregate
    over the entire orbit, and each one is CHECKED with `rotation_invariant`
    rather than assumed.

    The coordinates:

      opcode census      12  how many of each opcode, order discarded
      ring transitions  144  ordered pairs counted with the closing edge, so
                             the wrap from the last opcode to the first is in
      landing spectrum   16  how many of the n cuts land in each register.
                             Aggregating over every cut is what makes this one
                             invariant: the landing of any SINGLE cut is the
                             phase-bearing quantity, and the distribution of
                             all of them is not.
      scalars                length, delta/mu pairs, greatest depth, deposits,
                             total ordinal, verdict, closed walk

    The landing spectrum is the part that is genuinely of the ring rather than
    of a word: two words with the same census and the same transitions can put
    their cuts in different registers.
    """
    n = len(word_steps)
    if n == 0:
        return {"status": "error", "error": "empty word"}

    census = Counter(word_steps)
    ring = Counter((word_steps[i], word_steps[(i + 1) % n]) for i in range(n))

    landings = Counter()
    for k in range(n):
        rot = word_steps[k:] + word_steps[:k]
        landings[reg_name(run_weighted(rot).reg)] += 1

    m = run_weighted(word_steps)
    pairs, maxdepth = _ring_pairs_and_depth(word_steps)

    scalars = {
        "length": n,
        "pairs": pairs,
        "max_depth": maxdepth,
        "total_ordinal": sum(_ORDINAL.get(t, 0) for t in word_steps),
        "distinct_landings": len(landings),
    }
    # Deposits are NOT invariant and are reported apart from the signature: a
    # rotation moves the IFIX, and every opcode after a fixation is inert, so
    # how much a word deposits depends on where it was cut.
    deposits_here = sum(1 for _, _, k, _ in m.ledger if k == "DEPOSIT")

    # Every coordinate is checked, not asserted. A coordinate that moves under
    # rotation is reading the cut and does not belong in a signature of a ring.
    def _census(w): return tuple(sorted(Counter(w).items()))
    def _ring(w):
        L = len(w)
        return tuple(sorted(Counter((w[i], w[(i + 1) % L]) for i in range(L)).items()))
    def _land(w):
        L = len(w)
        c = Counter()
        for k in range(L):
            c[reg_name(run_weighted(w[k:] + w[:k]).reg)] += 1
        return tuple(sorted(c.items()))
    def _scal(w):
        pr, mx = _ring_pairs_and_depth(w)
        return (len(w), pr, mx, sum(_ORDINAL.get(t, 0) for t in w))

    checks = {name: rotation_invariant(word_steps, fn)["invariant"]
              for name, fn in (("opcode_census", _census),
                               ("ring_transitions", _ring),
                               ("landing_spectrum", _land),
                               ("scalars", _scal))}

    return {
        "status": "ok",
        "word": render(word_steps),
        "dimension": 12 + 144 + 16 + len(scalars),
        "opcode_census": {GLYPH.get(k, k): v for k, v in census.items()},
        "ring_transitions": {f"{GLYPH.get(a,'?')}{GLYPH.get(b,'?')}": c
                             for (a, b), c in ring.most_common()},
        "landing_spectrum": {r: landings.get(r, 0) for r in _REGISTERS
                             if landings.get(r, 0)},
        "scalars": scalars,
        "phase_bearing_not_in_signature": {
            "deposits_at_this_cut": deposits_here,
            "why": "a rotation moves the IFIX and everything after a fixation is "
                   "inert, so the deposit count belongs to the cut, not the word",
        },
        "every_coordinate_rotation_invariant": all(checks.values()),
        "invariance_by_block": checks,
        "note": ("built on the ring: the closing edge is counted and the landing "
                 "spectrum aggregates every cut, so no coordinate reads absolute "
                 "position"),
    }


# ── Steering: reach a target register by rotation and insertion ───────────────


# ── What an insertion costs ─────────────────────────────────────────────────
# Measured, not stipulated: each opcode was inserted at every third position of
# 120 randomly generated LIVE words (words that had weight to lose), and the
# change in restored weight and the rate of vacating recorded.
#
# The result is categorical rather than graded. IFIX vacates a live word about
# half the time; every other opcode vacates zero. A fixation makes everything
# after it inert, so it is the only insertion that can end a run rather than
# merely shift it. The productive ordering that falls out is the banking
# discipline arrived at from the other direction: open a region, clear against
# it, deposit inside it.
OP_COST: Dict[str, Dict[str, float]] = {
    "FSPLIT3": {"delta": +0.019, "vacates": 0.000},   # open a region — best
    "AREV":    {"delta": +0.011, "vacates": 0.000},   # the clear that banks
    "EVALI":   {"delta": +0.008, "vacates": 0.000},
    "EVALT":   {"delta": +0.004, "vacates": 0.000},
    "EVALF":   {"delta": +0.004, "vacates": 0.000},
    "AFWD":    {"delta":  0.000, "vacates": 0.000},
    "CLINK":   {"delta":  0.000, "vacates": 0.000},
    "IMSCRIB": {"delta":  0.000, "vacates": 0.000},
    "TANCH":   {"delta":  0.000, "vacates": 0.000},
    "FFUSE3":  {"delta": -0.019, "vacates": 0.000},   # closing early costs
    "VINIT":   {"delta": -0.044, "vacates": 0.000},   # clears, banks nothing
    "IFIX":    {"delta": -0.069, "vacates": 0.494},   # the only one that ends a run
}


def op_cost(tokens) -> Dict:
    """The measured cost of a set of insertions, and whether any can vacate."""
    d = sum(OP_COST.get(t, {}).get("delta", 0.0) for t in tokens)
    risk = max([OP_COST.get(t, {}).get("vacates", 0.0) for t in tokens] or [0.0])
    return {"delta": round(d, 4), "vacate_risk": risk,
            "carries_fixation": any(t == "IFIX" for t in tokens)}

# Ordered by measured productivity so the search meets the useful insertions
# first; the set is unchanged, only the order.
_STEER_TOKENS = ["FSPLIT3", "AREV", "EVALI", "EVALT", "EVALF", "AFWD",
                 "CLINK", "IMSCRIB", "TANCH", "FFUSE3", "VINIT", "IFIX"]


def _inserted(base, cand) -> List[str]:
    """Which tokens `cand` has that `base` does not, as a multiset difference."""
    c = Counter(cand) - Counter(base)
    return [t for t, n in c.items() for _ in range(n)]


def steer(steps, target=None, rotate=True, insert=True, depth=1,
          require_live=False, min_restored=0):
    """Reach a target register AND a target state, by rotation and insertion.

    A landing is a property of the cut, not of the word, so asking for a
    register is asking which cut to read from and what to add. But a register
    alone is not a result: inserting IFIX makes everything after it inert, so
    almost any target is reachable on a run where nothing was ever at risk.
    `require_live` and `min_restored` are how the caller asks for the landing
    to have been earned, which is the half of the request a register cannot
    express.

    `depth` allows more than one insertion. With no target, the reachable set is
    returned — the refusal stated positively, as what this word CAN land on.

    Cost prunes NOTHING here, deliberately. The obvious optimisation is to stop
    expanding intermediates that have gone vacuous, and it is maximally lossy:
    measured on the Frobenius kernel, every live depth-2 solution is reached
    through a vacuous depth-1 intermediate and none through a live one, because
    no single insertion makes that word live at all. From a word carrying
    nothing, the path to carrying something passes through carrying nothing —
    so a search that refuses to walk through vacuity finds no way out of it.
    The measured costs order the frontier and are reported per solution; they do
    not gate it.

    """
    n = len(steps)
    rots = list(range(n)) if rotate else [0]

    def variants(w):
        """All words reachable from w by up to `depth` insertions, w included."""
        seen = {render(w): w}
        frontier = [w]
        for _ in range(max(0, depth) if insert else 0):
            nxt = []
            for cur in frontier:
                for g in _STEER_TOKENS:
                    for i in range(len(cur) + 1):
                        cand = cur[:i] + [g] + cur[i:]
                        key = render(cand)
                        if key not in seen:
                            seen[key] = cand
                            nxt.append(cand)
            frontier = nxt
        return seen

    hits, reachable, examined = [], {}, 0
    for k in rots:
        rot = steps[k:] + steps[:k]
        for key, cand in variants(rot).items():
            examined += 1
            reg = weight(cand)["final_register"]
            reachable[reg] = reachable.get(reg, 0) + 1
            if target is not None and reg != target:
                continue
            b = banked_count_check(cand)
            live = not b.get("vacuous")
            rest = b.get("restored", 0)
            if require_live and not live:
                continue
            if rest < min_restored:
                continue
            if target is not None:
                added_toks = _inserted(rot, cand)
                hits.append({"word": key, "cut": k, "added": len(cand) - n,
                             "register": reg, "restored": rest,
                             "vacuous": b.get("vacuous"),
                             "deposits": b.get("deposits", 0),
                             "cost": op_cost(added_toks)})
    # Liveness leads, then weight: a landing bought with a vacuous run is free,
    # and ranking by the target alone manufactures exactly those.
    hits.sort(key=lambda h: (not h["vacuous"], h["restored"], -h["added"]),
              reverse=True)
    out = {"status": "ok", "word": render(steps), "target": target,
           "depth": depth, "examined": examined,
           "constraints": {"require_live": require_live,
                           "min_restored": min_restored},
           "reachable": dict(sorted(reachable.items(), key=lambda t: -t[1]))}
    if target is None:
        out["note"] = ("no target given; reachable registers counted over every "
                       "cut and insertion")
        return out
    out["solutions"] = len(hits)
    out["best"] = hits[:5]
    if not hits:
        why = "with nothing at risk excluded" if require_live else ""
        out["refusal"] = (f"{target} is not reachable from this word by rotation "
                          f"and {depth} insertion(s) {why}".strip())
    return out


def steer_spectrum(steps, target=None, depth=1):
    """Steer the landing SPECTRUM, which is a property of the word not the cut.

    Rotation moves the landing and cannot move the spectrum — the spectrum is
    rotation-invariant by construction, so this searches insertions only. That
    asymmetry is the point: to change where a word rests you turn it, to change
    what it IS you add to it.

    Scored by the target's share across every cut, so the answer is a word that
    lands on the target from MOST readings rather than from a lucky one, and by
    the weight it still carries after the change.
    """
    def spectrum(w):
        n = len(w)
        c = Counter(weight(w[k:] + w[:k])["final_register"] for k in range(n))
        return c, n

    base_c, base_n = spectrum(steps)
    base = {"word": render(steps), "spectrum": dict(base_c),
            "share": round(base_c.get(target, 0) / base_n, 4) if target else None}
    if target is None:
        return {"status": "ok", "base": base,
                "note": "no target; the spectrum above is the word's invariant landing profile"}

    seen, frontier = {render(steps): steps}, [steps]
    for _ in range(max(1, depth)):
        nxt = []
        for w in frontier:
            for g in _STEER_TOKENS:
                for i in range(len(w) + 1):
                    cand = w[:i] + [g] + w[i:]
                    key = render(cand)
                    if key not in seen:
                        seen[key] = cand
                        nxt.append(cand)
        frontier = nxt
    rows = []
    for key, cand in seen.items():
        c, n = spectrum(cand)
        b = banked_count_check(cand)
        rows.append({"word": key, "added": len(cand) - len(steps),
                     "share": round(c.get(target, 0) / n, 4),
                     "spectrum": dict(c), "restored": b.get("restored", 0),
                     "vacuous": b.get("vacuous")})
    # Ranking share first manufactures the free landing: inserting IFIX makes
    # everything after it inert, so the word lands on the target from EVERY cut
    # while nothing is ever at risk. A perfect spectrum bought with a vacuous
    # run is not a better word, so liveness leads, then weight, then share.
    rows.sort(key=lambda r: (not r["vacuous"], r["restored"], r["share"]), reverse=True)
    best_share = rows[0]["share"] if rows else 0.0
    return {"status": "ok", "target": target, "base": base,
            "searched": len(seen), "best_share": best_share,
            "best": rows[:5],
            "invariant_note": "rotation is absent from this search because it cannot change a spectrum"}
