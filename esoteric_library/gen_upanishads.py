#!/usr/bin/env python3
"""Generate upanishads.json — imscribed catalog for upanishads.
Fill in the entries below, then run:
    python3 esoteric_library/gen_upanishads.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pre-migration criticality key (compatible with imscribeaudio.py)
PHI = 'φ̂'

# ---------------------------------------------------------------------------
# Available glyph IDs — field order: Ð Þ Ř Φ ƒ Ç Γ ɢ [φ̂=crit] Ħ Σ Ω
#
#   Ð  Dimensionality : Ð_ß  Ð_C  Ð_;  Ð_ω
#   Þ  Topology       : Þ_6  Þ_K  Þ_ò  Þ_¨  Þ_O
#   Ř  Relational     : Ř_¯  Ř_ý  Ř_Ť  Ř_=
#   Φ  Polarity       : Φ_ɐ  Φ_υ  Φ_F  Φ_˙  Φ_}
#   ƒ  Fidelity       : ƒ_ì  ƒ_ð  ƒ_ż
#   Ç  Kinetics       : Ç_-  Ç_W  Ç_@  Ç_Ù  Ç_λ
#   Γ  Scope          : Γ_β  Γ_γ  Γ_ʔ
#   ɢ  Grammar        : ɢ_^  ɢ_˝  ɢ_ˌ  ɢ_Ş
#   φ̂  Criticality    : φ̂_ž  φ̂_ÿ  φ̂_Æ  φ̂_3  φ̂_Ţ
#   Ħ  Temporal Depth : Ħ_Ñ  Ħ_£  Ħ_A  Ħ_!
#   Σ  Stoichiometry  : Σ_S  Σ_ő  Σ_ï
#   Ω  Winding        : Ω_Å  Ω_2  Ω_z  Ω_5
#
# Tier heuristic (boundary fields: Φ, D, φ̂, Ω):
#   T_0   : φ̂_ž, D compact/infty, Φ not Frobenius
#   T_1   : φ̂_ÿ, Φ not Frobenius
#   T_2   : φ̂_ÿ/φ̂_Æ, Φ not Frobenius, Ω winding
#   T_3   : φ̂_Æ/φ̂_3, any Φ, Ω winding
#   T_inf : φ̂_3 or (φ̂_ÿ + Φ_}) — Frobenius + EP
# ---------------------------------------------------------------------------

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {
        "name": f"upanishads_{num:02d}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "Ð": D, "Þ": T, "Ř": R, "Φ": P, "ƒ": F,
        "Ç": K, "Γ": G, "ɢ": Gm, PHI: C,
        "Ħ": H, "Σ": S, "Ω": Om,
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
        "One-line description of the structural claim",
        "Verbatim source text for this section.",
        "Ð_ω","Þ_O","Ř_Ť","Φ_}","ƒ_ì","Ç_@","Γ_ʔ","ɢ_^","φ̂_3","Ħ_!","Σ_S","Ω_z",
        "T_inf", 0.95,
        "Why these coordinates: ..."),

    # entry(2, ...),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upanishads.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(chapters)} entries → {out}")
