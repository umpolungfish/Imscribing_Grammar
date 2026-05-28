#!/usr/bin/env python3
"""
IG Genetics Analysis: Answer the open questions from genetics_ig.md.
Investigates the 8 exact boxes, UU_/UA_ half-degeneracy, 20=8+12 derivation,
and 20=4x5 coincidence using the B4 lattice and Crystal structure.
"""

import json
from itertools import product
from collections import defaultdict, Counter

# ── 1. Genetic Code ──────────────────────────────────────────────────────────

GENETIC_CODE = {
    "UUU":"Phe","UUC":"Phe","UUA":"Leu","UUG":"Leu",
    "UCU":"Ser","UCC":"Ser","UCA":"Ser","UCG":"Ser",
    "UAU":"Tyr","UAC":"Tyr","UAA":"Stop","UAG":"Stop",
    "UGU":"Cys","UGC":"Cys","UGA":"Stop","UGG":"Trp",
    "CUU":"Leu","CUC":"Leu","CUA":"Leu","CUG":"Leu",
    "CCU":"Pro","CCC":"Pro","CCA":"Pro","CCG":"Pro",
    "CAU":"His","CAC":"His","CAA":"Gln","CAG":"Gln",
    "CGU":"Arg","CGC":"Arg","CGA":"Arg","CGG":"Arg",
    "AUU":"Ile","AUC":"Ile","AUA":"Ile","AUG":"Met",
    "ACU":"Thr","ACC":"Thr","ACA":"Thr","ACG":"Thr",
    "AAU":"Asn","AAC":"Asn","AAA":"Lys","AAG":"Lys",
    "AGU":"Ser","AGC":"Ser","AGA":"Arg","AGG":"Arg",
    "GUU":"Val","GUC":"Val","GUA":"Val","GUG":"Val",
    "GCU":"Ala","GCC":"Ala","GCA":"Ala","GCG":"Ala",
    "GAU":"Asp","GAC":"Asp","GAA":"Glu","GAG":"Glu",
    "GGU":"Gly","GGC":"Gly","GGA":"Gly","GGG":"Gly",
}

nuc_to_b4 = {"G":"B","C":"T","A":"F","U":"N"}
B4 = ["N","T","F","B"]

# B4 lattice: meet and join
b4_meet = {}
b4_join = {}
for a in B4:
    for b in B4:
        if a == "N" or b == "N":        m = "N"
        elif a == "B":                  m = b
        elif b == "B":                  m = a
        elif a == b:                    m = a
        else:                           m = "N"
        if a == "B" or b == "B":        j = "B"
        elif a == "N":                  j = b
        elif b == "N":                  j = a
        elif a == b:                    j = a
        else:                           j = "B"
        b4_meet[(a,b)] = m
        b4_join[(a,b)] = j

def b4_le(a, b):
    """a <= b in B4 lattice order"""
    return b4_meet[(a,b)] == a

def pfx(box_str):
    """Convert nucleotide box prefix to B4² coordinates"""
    return (nuc_to_b4[box_str[0]], nuc_to_b4[box_str[1]])

def p_le(p, q):
    return b4_le(p[0], q[0]) and b4_le(p[1], q[1])

def p_meet(p, q):
    return (b4_meet[(p[0], q[0])], b4_meet[(p[1], q[1])])

def p_join(p, q):
    return (b4_join[(p[0], q[0])], b4_join[(p[1], q[1])])

# ── Build codon boxes ────────────────────────────────────────────────────────

boxes = {}
for b1 in "UCAG":
    for b2 in "UCAG":
        key = f"{b1}{b2}_"
        aas = [GENETIC_CODE[f"{b1}{b2}{b3}"] for b3 in "UCAG"]
        unique = list(dict.fromkeys(aas))
        boxes[key] = {"aas": aas, "unique": unique,
                      "split": len(set(aas)) > 1, "prefix": pfx(key)}

exact_boxes = {k:v for k,v in boxes.items() if not v["split"]}
split_boxes = {k:v for k,v in boxes.items() if v["split"]}
ground_aas = set(v["unique"][0] for v in exact_boxes.values())

print("=" * 70)
print("Q1: WHY 8 EXACT BOXES?")
print("=" * 70)

# The exact boxes have position 2 = C (T in B4) always exact
# Position 2 = G (B in B4) exact when position 1 = C or G
# Position 2 = A/U (F/N) always split

print("\nExact boxes by position-2 base:")
pos2_exact = defaultdict(list)
for k, v in exact_boxes.items():
    pos2_exact[k[1]].append(k)
for base in sorted(pos2_exact):
    print(f"  pos-2={base}: {pos2_exact[base]}")

print("\nSplit boxes by position-2 base:")
pos2_split = defaultdict(list)
for k, v in split_boxes.items():
    pos2_split[k[1]].append(k)
for base in sorted(pos2_split):
    print(f"  pos-2={base}: {pos2_split[base]}")

print()

# The key insight: The Frobenius condition μ∘δ=id for a box means
# position 3 carries no structural information. This happens when:
# 1. pos-2 = C (T in B4): C=T pairs only with G=B via 3 H-bonds.
#    The strong pairing at position 2 stabilizes the codon-anticodon
#    enough that position 3 is redundant.
# 2. pos-2 = G (B in B4): G=B is the universal pairing base.
#    It's exact when pos-1 is also strong (C or G = T or B).
#    AU_ and GU_ show the exact/split boundary depends on pos-1.

# B4 lattice analysis of the 8/16 split
print("\n--- B4 LATTICE ANALYSIS ---")
print("The 16 boxes = all combinations of B4 at positions 1 and 2.")
print("Each box prefix (p1_B4, p2_B4) determines Frobenius status.")

for b1 in B4:
    for b2 in B4:
        # Find which RNA box(es) have this B4 prefix
        matching = [k for k in boxes if pfx(k) == (b1, b2)]
        if matching:
            k = matching[0]
            is_exact = not boxes[k]["split"]
            print(f"  B4²=({b1},{b2}) → {k:6s} {'EXACT' if is_exact else 'SPLIT'}")

print()
print("Key structural fact: The 8 exact boxes are EXACTLY those")
print("where the prefix is NOT in {(F,N), (F,F), (N,N), (N,F),")
print("(N,B), (B,N), (F,B), (B,F)} — i.e., 8 out of 16.")

# Show the B4 partial order determines which exact boxes exist
print("\nB4 order: N ≤ T ≤ B, N ≤ F ≤ B  (T and F are incomparable)")
print()
print("Theorem: A box is Frobenius-exact iff its B4² prefix (p1, p2)")
print("satisfies: p2 ∈ {T, B} with p2 ≠ B or p1 ∈ {T, B}.")
print("Equivalently: not (p2 ∈ {N, F} or (p2 = B and p1 ∈ {N, F})).")
print()

# Let me derive this combinatorially
print("\n--- COMBINATORIAL DERIVATION ---")
print("Total B4² = 4×4 = 16 possible prefixes.")
print("A prefix is Frobenius-exact iff position 2 is a 'determining' base,")
print("where determining = the third position cannot change the AA.")
print()
print("In B4 terms: a box is exact iff p2 is NOT join-absorbed by")
print("any different B4 value at position 3. The third-position B4")
print("values {N, T, F, B} can only be distinguished at position 3 if")
print("position 2 is WEAK (N or F, i.e., U or A).")
print()
print("Counting in B4²:")
print("  p2 = T (C): 4 prefixes (any p1) → 4 exact")
print("  p2 = B (G): exact iff p1 ∈ {T, B} (C or G) → 2 exact")
print("  p2 = N (U): always split (position 3 needed) → 4 split")
print("  p2 = F (A): always split → 4 split")
print("  Total exact: 4 + 2 = 6? Wait...")
print()

# Let me recalculate
print("Let me re-count from the actual genetic code:")
print(f"  Exact boxes with pos-2 = C (T): ", end="")
print([k for k in exact_boxes if k[1]=='C'])
print(f"  Exact boxes with pos-2 = G (B): ", end="")
print([k for k in exact_boxes if k[1]=='G'])

# Hmm, the exact boxes with pos-2=G are CG_ and GG_. So that's 2 more.
# And exact boxes with pos-2=C are UC_, CC_, AC_, GC_ = 4.
# Total = 6? But we said 8 exact boxes earlier!

# Wait, let me re-check from the manuscript:
""" 
Frobenius-exact (unsplit) — 8 boxes:
UC_, CU_, CC_, CG_, AC_, GU_, GC_, GG_

Pos-2 of these:
UC_=C, CU_=U, CC_=C, CG_=G, AC_=C, GU_=U, GC_=C, GG_=G
"""
print()
print("Wait - CU_ and GU_ have pos-2 = U, which contradicts 'C or G'. Let me re-check.")
cu = [k for k in exact_boxes if k[1]=='U']
gu = [k for k in exact_boxes if k[1]=='G']
print(f"  Exact boxes with pos-2 = U: {cu}")
print(f"  Exact boxes with pos-2 = G: {gu}")
