#!/usr/bin/env python3
"""Jones polynomial of a braid closure, exact, then evaluated at any root of unity.

The kernel's `fibqc jones` is fixed at the Fibonacci root, t = 1/5 of a winding, so
every value it returns lies in Q(zeta_5) with phases on the tenths lattice. That covers
exactly one prime of a conductor. For d=2048 the SIC discriminant is

    4190205 = 3 * 5 * 409 * 683

so the Fibonacci level supplies the 5 and nothing else. This computes the bracket as an
exact Laurent polynomial in A, converts to the Jones polynomial in t, and only then
substitutes a root — so the level is a parameter rather than a constant, and any
cyclotomic field is reachable.

    jones_at_root(word, strands)              -> exact Laurent coefficients in t^(1/2)
    jones_at_root(word, strands, root=n)      -> value at t = exp(2*pi*i/n)
    quadratic_root_level(m)                   -> the n whose Q(zeta_n) holds sqrt(m)

The state sum is over 2^c smoothings for c crossings, so this is exact and exponential
in crossing number, not in strand count. Modest words are instant; it is not a
replacement for the kernel at scale, it is the exact-arithmetic complement to it.
"""
from __future__ import annotations

import cmath
import math
from fractions import Fraction


# ── Kauffman bracket by state sum ────────────────────────────────────

def _closure_loops(word, n, state):
    """Number of loops in the closure of `word` with each crossing smoothed by `state`.

    A crossing sigma_i smoothed A-way is the identity on strands i, i+1; smoothed
    B-way it is the cup-cap. Track the permutation-with-cups as a union-find over
    2n endpoints, then close the braid by identifying top and bottom.
    """
    # positions: 0..n-1 are the running strand ends. Allocate exactly n and grow —
    # allocating 2n up front leaves unused nodes that count as extra components.
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # cur[i] is the node id currently at position i
    cur = list(range(n))
    nxt = n
    for gi, g in enumerate(word):
        i = abs(g) - 1
        smoothing = state[gi]
        # A-smoothing of sigma_i^{+1} is identity; B-smoothing is cup-cap.
        # For sigma_i^{-1} the roles swap.
        # The geometry and the A/B label are separate things. State 0 is always the
        # identity smoothing; which of the two counts as A depends on the sign of the
        # crossing, and that is handled in `bracket`. Tying them together here made the
        # A-power wrong by 2 on every negative crossing.
        ident = (smoothing == 0)
        if ident:
            # A smoothed diagram has no crossings: the identity smoothing is two
            # parallel strands, so nothing moves. Swapping here would be modelling
            # the crossing as a permutation, which is the unsmoothed picture.
            pass
        else:
            union(cur[i], cur[i + 1])          # cap joins the two incoming
            parent.extend([nxt, nxt + 1])      # cup makes two fresh ends
            cur[i], cur[i + 1] = nxt, nxt + 1
            nxt += 2
    for i in range(n):
        union(cur[i], i)                        # close the braid
    return len({find(x) for x in range(nxt)})


def bracket(word, n):
    """Kauffman bracket as {power_of_A: coefficient}, d = -A^2 - A^-2."""
    c = len(word)
    poly = {}
    for s in range(1 << c):
        state = [(s >> k) & 1 for k in range(c)]
        a_count = sum(1 for k in range(c)
                      if (state[k] == 0) == (word[k] > 0))
        b_count = c - a_count
        loops = _closure_loops(word, n, state)
        # each state contributes A^(a-b) * d^(loops-1)
        base = a_count - b_count
        # expand d^(loops-1) = (-A^2 - A^-2)^(loops-1)
        m = loops - 1
        for j in range(m + 1):
            coef = math.comb(m, j) * ((-1) ** m)
            power = base + 2 * j - 2 * (m - j)
            poly[power] = poly.get(power, 0) + coef
    return {k: v for k, v in poly.items() if v}


def jones(word, n):
    """Jones polynomial as {exponent_of_t (Fraction): coefficient}."""
    br = bracket(word, n)
    w = sum(1 if g > 0 else -1 for g in word)
    # f = (-A^3)^(-w) * bracket ; then t = A^-4
    out = {}
    sign = (-1) ** (w % 2)
    for p, cvv in br.items():
        power_A = p - 3 * w
        out_exp = Fraction(-power_A, 4)
        out[out_exp] = out.get(out_exp, 0) + sign * cvv
    return {k: v for k, v in sorted(out.items()) if v}


# ── evaluation at a root of unity ────────────────────────────────────

def evaluate(poly, root):
    """Evaluate {t-exponent: coeff} at t = exp(2*pi*i/root)."""
    z = 2j * math.pi / root
    return sum(c * cmath.exp(z * float(e)) for e, c in poly.items())


def quadratic_root_level(m):
    """Smallest n with sqrt(m) in Q(zeta_n): the conductor of Q(sqrt m).

    m squarefree: conductor is m when m = 1 mod 4, else 4m. sqrt(m) is then a
    Gauss-sum combination of n-th roots of unity.
    """
    sf = m
    k = 2
    while k * k <= sf:
        while sf % (k * k) == 0:
            sf //= k * k
        k += 1
    return sf if sf % 4 == 1 else 4 * sf


def field_of(root):
    """Which cyclotomic field the values at this root live in, and its real quadratic
    subfields' discriminants."""
    return f"Q(zeta_{root})"


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        # trefoil: V(t) = -t^-4 + t^-3 + t^-1
        j = jones([1, 1, 1], 2)
        print("trefoil  V =", {str(k): v for k, v in j.items()})
        # unknot
        print("unknot   V =", {str(k): v for k, v in jones([], 1).items()})
        print("figure8  V =", {str(k): v for k, v in jones([1, -2, 1, -2], 3).items()})
        for m in (5, 13, 4190205):
            print(f"sqrt({m}) reachable at level n = {quadratic_root_level(m)}")
        sys.exit(0)
    word = [int(x) for x in sys.argv[1].split()] if len(sys.argv) > 1 else [1, 1, 1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    root = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    j = jones(word, n)
    v = evaluate(j, root)
    print(json.dumps({
        "braid": word, "strands": n, "root": root,
        "field": field_of(root),
        "jones_exact": {str(k): v2 for k, v2 in j.items()},
        "value": [v.real, v.imag], "abs": abs(v),
    }, indent=2))
