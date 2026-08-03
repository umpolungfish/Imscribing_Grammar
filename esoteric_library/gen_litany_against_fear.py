#!/usr/bin/env python3
"""Generate litany_against_fear.json — imscribed catalog for litany_against_fear.
Fill in the entries below, then run:
    python3 esoteric_library/gen_litany_against_fear.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pre-migration criticality key (compatible with imscribeaudio.py)
PHI = '⊙'

# ---------------------------------------------------------------------------
# Available glyph IDs — field order: ⊢ ⊣ > < ƒ Ç Γ ɢ [⊙=crit] Ħ Σ Ω
#
#   ⊢  Dimensionality : 𐑛  𐑨  𐑼  𐑦
#   ⊣  Topology       : 𐑡  𐑰  𐑥  𐑶  𐑸
#   >  Relational     : 𐑩  𐑑  𐑽  𐑾
#   <  Polarity       : 𐑗  𐑿  𐑬  𐑯  𐑹
#   ƒ  Fidelity       : ƒ^ì  ƒ^ð  ƒ^ż
#   Ç  Kinetics       : Ç^-  Ç^W  Ç^@  Ç^Ù  Ç^λ
#   Γ  Scope          : 𐑚  𐑔  𐑲
#   ɢ  Grammar        : ɢ^∧  ɢ^˝  ɢ^ˌ  ɢ^Ş
#   ⊙  Criticality    : 𐑢  ⊙  𐑮  𐑻  𐑣
#   Ħ  Chirality : 𐑓  𐑒  𐑖  𐑫
#   Σ  Stoichiometry  : 𐑙  𐑕  𐑳
#   Ω  Winding        : 𐑷  𐑴  𐑭  𐑟
#
# Tier heuristic (boundary fields: <, D, ⊙, Ω):
#   T_0   : 𐑢, D compact/infty, < not Frobenius
#   T_1   : ⊙, < not Frobenius
#   T_2   : ⊙/𐑮, < not Frobenius, Ω winding
#   T_3   : 𐑮/𐑻, any <, Ω winding
#   T_inf : 𐑻 or (⊙ + 𐑹) — Frobenius + EP
# ---------------------------------------------------------------------------

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"litany_against_fear_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "⊢": D, "⊣": T, ">": R, "<": P, "⋈": F,
        "⊤": K, "∈": G, "∋": Gm, PHI: C,
        "⊥": H, "⊞": S, "◻": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }

# ---------------------------------------------------------------------------
# Fill in one entry per section/verse. Arguments:
#   entry(number, title, description, text,
#         D,    T,    R,    P,    F,    K,    G,    Gm,   Crit, H,    S,    Omega,
#         tier, C_score, notes="...")
# ---------------------------------------------------------------------------

chapters = [
    entry(1, "Section title",
        "One-line description of the claim",
        "Verbatim source text for this section.",
        "𐑦","𐑸","𐑽","𐑹","ƒ^ì","Ç^@","𐑲","ɢ^∧","𐑻","𐑫","𐑙","𐑭",
        "T_inf", 0.95,
        "Why these coordinates: ..."),

    # entry(2, ...),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "litany_against_fear.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries → {out}")
