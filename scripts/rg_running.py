#!/usr/bin/env python3
"""SM one-loop gauge running, from PDG at M_Z outward.

Emits the flow table in ig-docs/rg_running_grammar_sm.md. That table was typed
by hand and its alpha_em and sin^2(theta_W) columns were built from
alpha_em^-1 = alpha_2^-1 + (3/5) alpha_1^-1, with the GUT normalisation factor
inverted. alpha_1 = (5/3) alpha_Y, so alpha_Y^-1 = (5/3) alpha_1^-1, and the
factor in the sum is 5/3. The inverted form put sin^2(theta_W) at 0.455 at M_Z,
where the same document's prose said 0.231 four sections later.

Run it and paste; do not retype the table.
"""

from math import log, pi, sqrt

# PDG 2024 at M_Z. These are the only measured inputs.
MZ      = 91.1876
AEM_INV = 127.952       # alpha_em^-1(M_Z)
S2W     = 0.23122       # sin^2(theta_W)(M_Z), MS-bar
ALPHA_S = 0.1181        # alpha_s(M_Z)
AEM0_INV = 137.035999   # alpha_em^-1(q^2 = 0), the Thomson limit

# One-loop SM coefficients, d(alpha_i^-1)/d(ln mu) = -b_i/(2 pi),
# with alpha_1 in the GUT normalisation.
B1, B2, B3 = 41 / 10, -19 / 6, -7

GEAR = 4  # the Grammar's alpha_s/alpha_em


def couplings_at_mz():
    i2 = AEM_INV * S2W                 # alpha_2^-1
    iY = AEM_INV * (1 - S2W)           # alpha_Y^-1
    i1 = 0.6 * iY                      # alpha_1^-1 = (3/5) alpha_Y^-1
    i3 = 1 / ALPHA_S
    return i1, i2, i3


I1, I2, I3 = couplings_at_mz()


def at(mu):
    """(alpha_1^-1, alpha_2^-1, alpha_3^-1, alpha_em^-1, sin^2 theta_W, alpha_s)."""
    t = log(mu / MZ)
    a1 = I1 - B1 / (2 * pi) * t
    a2 = I2 - B2 / (2 * pi) * t
    a3 = I3 - B3 / (2 * pi) * t
    # alpha_1 is GUT-normalised: alpha_Y^-1 = (5/3) alpha_1^-1. This is the
    # factor the hand-written table inverted.
    iem = a2 + (5 / 3) * a1
    return a1, a2, a3, iem, a2 / iem, 1 / a3


def m_uv_cross():
    """Scale where alpha_s equals gear x alpha_em at zero momentum.

    Pure QCD running, so the inverted factor never touched this one.
    """
    target = AEM0_INV / GEAR
    return MZ * pow(2.718281828459045, (target - I3) * 2 * pi / (-B3))


def m_uv_same():
    """Scale where alpha_s / alpha_em equals gear at that same scale."""
    lo, hi = MZ, 1e19
    for _ in range(300):
        mid = sqrt(lo * hi)
        *_, als = at(mid)
        iem = at(mid)[3]
        if als * iem > GEAR:
            lo = mid
        else:
            hi = mid
    return lo


def table(scales):
    w = "  {:<16}{:>8}{:>9}{:>9}{:>10}{:>11}{:>9}"
    out = [w.format("mu [GeV]", "a1^-1", "a2^-1", "a3^-1", "aem^-1",
                    "sin2thW", "alpha_s"),
           "  " + "-" * 70]
    for mu, label in scales:
        a1, a2, a3, iem, s, als = at(mu)
        out.append("  {:<16}{:>8.2f}{:>9.2f}{:>9.2f}{:>10.2f}{:>11.4f}{:>9.4f}"
                   .format(label, a1, a2, a3, iem, s, als))
    return "\n".join(out)


if __name__ == "__main__":
    muv = m_uv_cross()
    mus = m_uv_same()
    scales = [
        (muv, "{:.2e} (UV)".format(muv).replace("e+", "e")),
        (1e15, "1.00e15"),
        (mus,  "{:.2e} (gear)".format(mus).replace("e+", "e")),
        (1e9,  "1.00e9"),
        (1e6,  "1.00e6"),
        (1e3,  "1.00e3"),
        (MZ,   "91.19 (M_Z)"),
    ]
    scales.sort(key=lambda r: -r[0])
    print(table(scales))
    print()

    a1, a2, a3, iem, s, als = at(muv)
    print("M_UV  (alpha_s = gear x alpha_em(0)) = {:.4e} GeV".format(muv))
    print("   alpha_s = {:.6f}   alpha_em(0) = {:.6f}   ratio = {:.4f}"
          .format(als, 1 / AEM0_INV, als * AEM0_INV))
    print("   at that scale alpha_s/alpha_em(mu) = {:.4f}".format(als * iem))
    print()

    a1, a2, a3, iem, s, als = at(mus)
    print("M_gear (alpha_s = gear x alpha_em at the same scale) = {:.4e} GeV"
          .format(mus))
    print("   alpha_s = {:.6f}   alpha_em = {:.6f}   ratio = {:.4f}"
          .format(als, 1 / iem, als * iem))
    print("   sin^2(theta_W) there = {:.4f}".format(s))
    print()

    *_, s_mz, _ = at(MZ)
    print("sin^2(theta_W): 3/13 = {:.6f}   PDG(M_Z) = {:.5f}   |diff| = {:.3f} pp"
          .format(3 / 13, S2W, abs(3 / 13 - S2W) * 100))
    print("sin^2(theta_W) at M_UV = {:.4f}".format(at(muv)[4]))
    print("alpha_em^-1 at M_UV = {:.2f}   against gear+alpha_s reading {:.2f}"
          .format(at(muv)[3], AEM0_INV))
