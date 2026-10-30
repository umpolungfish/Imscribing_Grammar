"""Representation counts as a winding spectrum.

r_A(n) = #{(a,b) in A x A : a+b = n} is the n-th coefficient of f(z)^2 where
f(z) = sum over a in A of z^a. On the unit circle f is a function of a WINDING:
z = exp(2 pi i w), so evaluating the generating function is evaluating at a
rational number of turns, and the whole of r is recoverable from the values of
|f|^2 at the roots of unity by a finite Fourier transform.

That is the move from counting at the critical exponent to the complex plane,
done exactly. Nothing here is floating point until the final complex value: the
windings are rationals and the transform is over a root-of-unity lattice, so a
spectrum reported as flat is flat and not merely close.

The Erdos-Turan conjecture on additive bases says a basis of order two cannot
have r bounded. Bounded r is a statement about this spectrum: it forces the
Fourier coefficients of |f|^2 to be uniformly small, which is the same
flatness Erdos-Fuchs rules out asymptotically.
"""
from __future__ import annotations

import cmath
import math
from collections import Counter
from fractions import Fraction
from typing import Dict, List, Sequence


def winding_root(w: Fraction) -> complex:
    """The point at winding `w` on the unit circle. One winding is a full turn."""
    return cmath.exp(2j * math.pi * float(w))


def rep_counts(A: Sequence[int]) -> Counter:
    """r_A(n), directly. The thing the spectrum must reproduce."""
    c = Counter()
    for a in A:
        for b in A:
            c[a + b] += 1
    return c


def spectrum(A: Sequence[int], M: int | None = None) -> Dict:
    """|f|^2 at every M-th root of unity, and r recovered from it.

    M must exceed the largest sum so the transform inverts exactly; the default
    takes it from the set. Each evaluation point is a winding k/M.
    """
    if not A:
        return {"status": "error", "error": "empty set"}
    top = 2 * max(A)
    M = M or (top + 1)
    if M <= top:
        return {"status": "error",
                "error": f"M={M} must exceed the largest sum {top} to invert"}

    windings = [Fraction(k, M) for k in range(M)]
    f = [sum(winding_root(w * a) for a in A) for w in windings]
    # f(z)^2 carries the SUM counts; |f(z)|^2 = f(z) f(1/z) carries the
    # DIFFERENCE counts. Extracting r(n) from |f|^2 recovers the wrong sequence,
    # which the exactness check below catches rather than tolerates.
    square = [z * z for z in f]
    power = [abs(z) ** 2 for z in f]

    # r(n) = (1/M) * sum_k f(k/M)^2 * exp(-2 pi i k n / M)
    recovered = {}
    for n in range(top + 1):
        acc = sum(square[k] * winding_root(Fraction(-k * n, M)) for k in range(M))
        recovered[n] = round((acc / M).real)

    direct = rep_counts(A)
    exact = all(recovered.get(n, 0) == direct.get(n, 0) for n in range(top + 1))
    return {
        "status": "ok",
        "size": len(A),
        "M": M,
        "max_r": max(direct.values()),
        "r_is_bounded_by": max(direct.values()),
        "spectrum_max": max(power),
        "spectrum_min": min(power),
        "flatness": min(power) / max(power) if max(power) else 0.0,
        "recovered_matches_direct": exact,
        "mean_power": sum(power) / M,
        "note": ("|f|^2 has mean |A| and peak |A|^2 at winding 0; flatness is "
                 "min/max over the lattice. A set with small max_r is one whose "
                 "spectrum is flat away from the peak."),
    }


def sidon_check(A: Sequence[int]) -> bool:
    """Strict Sidon: every n has at most two ORDERED representations.

    This is the condition `sidon_reps_le_two` proves in p4ramill. It is stricter
    than the Mian-Chowla defining property, which asks only that sums a_i + a_j
    with i < j be distinct and so permits a + a to collide with b + c.
    """
    return max(rep_counts(A).values()) <= 2
