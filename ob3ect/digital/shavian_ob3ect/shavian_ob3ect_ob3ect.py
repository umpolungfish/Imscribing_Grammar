#!/usr/bin/env python3
"""
shavian_ob3ect — Frobenius algebra over Shavian glyph decomposition/recomposition.

The Shavian alphabet (49 glyphs + space) is partitioned across the 12 IG primitives
according to a shape-topological mapping. This ob3ect reads its own source, decomposes
each Shavian glyph into its ⟨prim; subtype⟩ structural pair, and verifies that
μ∘δ = id holds on the canonical sentence: the parse/unparse roundtrip preserves
semantic identity.

Emerald Tablet principle at lexical scale: "That which is below is like that which
is above" — the shape-profile of each glyph (tall/deep/short) mirrors its structural
function across the imscriptive lattice.
"""
import ast
import hashlib
import os
import pathlib
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from frob import frobenius_phase, TANCH, AFWD, semantic_identity

# ── SHAVIAN ↔ IG MAPPING (49 glyphs → 12 primitives × subtypes) ──────────
# Mapping by shape-topology: 5×4 / 4×5 / 3×3 grid partition matching primitive arities
# 5×4 section: Ð, Ř, ɢ, Ħ, Ω — 5 primitives with 4 subtypes each

# The user's grid layout:
#   5×4 (arities of 4): Ð, Ř, ɢ, Ħ, Ω   — 5 rows × 4 cols
#   4×5 (arities of 5): Þ, Φ, Ç, φ̂      — 4 rows × 5 cols
#   3×3 (arities of 3): ƒ, Γ, Σ          — 3 rows × 3 cols

# 5×4 section — cell (r,c) → {prim: subtype_idx}
GRID_5x4 = {
    # Row 1: 𐑛 𐑨 𐑼 𐑦
    "𐑛": {"prim": "Ð",  "subtype": 0, "label": "Wedge-0d",      "shape": "deep"},
    "𐑨": {"prim": "Ð",  "subtype": 1, "label": "Triangle-2d",   "shape": "short"},
    "𐑼": {"prim": "Ð",  "subtype": 2, "label": "Infty-Field",   "shape": "short"},
    "𐑦": {"prim": "Ð",  "subtype": 3, "label": "Odot-Self",     "shape": "short"},
    # Row 2: 𐑩 𐑑 𐑽 𐑾
    "𐑩": {"prim": "Ř",  "subtype": 0, "label": "Supervene",     "shape": "short"},
    "𐑑": {"prim": "Ř",  "subtype": 1, "label": "Categorical",   "shape": "tall"},
    "𐑽": {"prim": "Ř",  "subtype": 2, "label": "Adjoint",       "shape": "short"},
    "𐑾": {"prim": "Ř",  "subtype": 3, "label": "Bidirectional", "shape": "short"},
    # Row 3: 𐑝 𐑜 𐑠 𐑵
    "𐑝": {"prim": "ɢ",  "subtype": 0, "label": "And-Conj",      "shape": "deep"},
    "𐑜": {"prim": "ɢ",  "subtype": 1, "label": "Or-Disj",       "shape": "deep"},
    "𐑠": {"prim": "ɢ",  "subtype": 2, "label": "Seq-Sequential", "shape": "tall"},
    "𐑵": {"prim": "ɢ",  "subtype": 3, "label": "Broad-Bcst",    "shape": "short"},
    # Row 4: 𐑓 𐑒 𐑖 𐑫
    "𐑓": {"prim": "Ħ",  "subtype": 0, "label": "Mem-Free",      "shape": "deep"},
    "𐑒": {"prim": "Ħ",  "subtype": 1, "label": "1-Step",        "shape": "tall"},
    "𐑖": {"prim": "Ħ",  "subtype": 2, "label": "2-Step",        "shape": "tall"},
    "𐑫": {"prim": "Ħ",  "subtype": 3, "label": "∞-Eternal",     "shape": "short"},
    # Row 5: 𐑷 𐑴 𐑭 𐑟
    "𐑷": {"prim": "Ω",  "subtype": 0, "label": "0-Trivial",     "shape": "short"},
    "𐑴": {"prim": "Ω",  "subtype": 1, "label": "Z2-Protect",    "shape": "short"},
    "𐑭": {"prim": "Ω",  "subtype": 2, "label": "Z-Integer",     "shape": "short"},
    "𐑟": {"prim": "Ω",  "subtype": 3, "label": "NA-NonAb",      "shape": "deep"},
}

# 4×5 section
GRID_4x5 = {
    # Row 1: 𐑡 𐑰 𐑥 𐑶 𐑸
    "𐑡": {"prim": "Þ",  "subtype": 0, "label": "Network",       "shape": "tall"},
    "𐑰": {"prim": "Þ",  "subtype": 1, "label": "Inclusion",     "shape": "short"},
    "𐑥": {"prim": "Þ",  "subtype": 2, "label": "Bowtie",        "shape": "short"},
    "𐑶": {"prim": "Þ",  "subtype": 3, "label": "Boxtimes",      "shape": "short"},
    "𐑸": {"prim": "Þ",  "subtype": 4, "label": "Odotor",        "shape": "tall"},
    # Row 2: 𐑗 𐑿 𐑬 𐑯 𐑹
    "𐑗": {"prim": "Φ",  "subtype": 0, "label": "Asym",          "shape": "tall"},
    "𐑿": {"prim": "Φ",  "subtype": 1, "label": "Psi-Quant",     "shape": "short"},
    "𐑬": {"prim": "Φ",  "subtype": 2, "label": "Partial",       "shape": "short"},
    "𐑯": {"prim": "Φ",  "subtype": 3, "label": "Sym-Ø",         "shape": "short"},
    "𐑹": {"prim": "Φ",  "subtype": 4, "label": "Frobenius",     "shape": "short"},
    # Row 3: 𐑘 𐑤 ⊙ 𐑪 𐑺
    "𐑘": {"prim": "Ç",  "subtype": 0, "label": "Fast-Driven",   "shape": "tall"},
    "𐑤": {"prim": "Ç",  "subtype": 1, "label": "Moderate",      "shape": "short"},
    # ⊙ is not a Shavian glyph — it marks φ̂_ÿ at center
    "𐑪": {"prim": "Ç",  "subtype": 2, "label": "Slow-NearEq",   "shape": "short"},
    "𐑺": {"prim": "Ç",  "subtype": 3, "label": "Trap-Frozen",   "shape": "short"},
    # Row 4: 𐑢 𐑧 𐑮 𐑻 𐑣
    "𐑢": {"prim": "φ̂", "subtype": 0, "label": "Sub-Below",     "shape": "short"},
    "𐑧": {"prim": "φ̂", "subtype": 1, "label": "ÿ-Critical",    "shape": "short"},
    "𐑮": {"prim": "φ̂", "subtype": 2, "label": "Æ-Cplx",        "shape": "short"},
    "𐑻": {"prim": "φ̂", "subtype": 3, "label": "3-EP",          "shape": "short"},
    "𐑣": {"prim": "φ̂", "subtype": 4, "label": "Ţ-Super",       "shape": "short"},
}

# 3×3 section
GRID_3x3 = {
    # Row 1: 𐑱 𐑞 𐑐
    "𐑱": {"prim": "ƒ",  "subtype": 0, "label": "Ell-Classical", "shape": "short"},
    "𐑞": {"prim": "ƒ",  "subtype": 1, "label": "Thermal",       "shape": "tall"},
    "𐑐": {"prim": "ƒ",  "subtype": 2, "label": "Hbar-Quant",    "shape": "tall"},
    # Row 2: 𐑚 𐑔 𐑲
    "𐑚": {"prim": "Γ",  "subtype": 0, "label": "Beth-Local",    "shape": "tall"},
    "𐑔": {"prim": "Γ",  "subtype": 1, "label": "Gimel-Meso",    "shape": "tall"},
    "𐑲": {"prim": "Γ",  "subtype": 2, "label": "Aleph-Max",     "shape": "short"},
    # Row 3: 𐑙 𐑕 𐑳
    "𐑙": {"prim": "Σ",  "subtype": 0, "label": "1:1-Single",    "shape": "deep"},
    "𐑕": {"prim": "Σ",  "subtype": 1, "label": "n:n-Same",      "shape": "deep"},
    "𐑳": {"prim": "Σ",  "subtype": 2, "label": "n:m-Hetero",    "shape": "short"},
}

# Merge all grids
SHAVIAN_MAP = {}
SHAVIAN_MAP.update(GRID_5x4)
SHAVIAN_MAP.update(GRID_4x5)
SHAVIAN_MAP.update(GRID_3x3)

# ⊙ as topological center (4×5 R3C3) — marks φ̂_ÿ
SHAVIAN_MAP["⊙"] = {"prim": "X", "subtype": -1, "label": "Self-Modeling Center", "shape": "center"}

# Reverse map: prim → list of glyphs
PRIM_TO_GLYPH = {}
for glyph, info in SHAVIAN_MAP.items():
    p = info["prim"]
    if p not in PRIM_TO_GLYPH:
        PRIM_TO_GLYPH[p] = []
    PRIM_TO_GLYPH[p].append((glyph, info["subtype"], info["shape"]))

# Canonical sentence: one glyph per primitive in IG order, first subtype
IG_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"]
CANONICAL_GLYPHS = []
for p in IG_ORDER:
    glyphs = PRIM_TO_GLYPH.get(p, [])
    if glyphs:
        # Pick the glyph with subtype=0
        match = [g for g in glyphs if g[1] == 0]
        if match:
            CANONICAL_GLYPHS.append(match[0][0])
        else:
            CANONICAL_GLYPHS.append(glyphs[0][0])
CORE_SENTENCE = "".join(CANONICAL_GLYPHS)


class ShavianOb3ect:
    """Frobenius ob3ect: Shavian glyph decomposition/recomposition = μ∘δ=id."""

    def __init__(self):
        self.source = pathlib.Path(__file__).read_text(encoding="utf-8")

    # ── δ (comultiplication): decompose sentence → glyph profiles ──────────
    def _decompose(self, sentence: str) -> list:
        """Parse a Shavian sentence into (glyph, prim, subtype, shape) tuples."""
        profiles = []
        for ch in sentence:
            if ch in SHAVIAN_MAP:
                info = SHAVIAN_MAP[ch]
                profiles.append((ch, info["prim"], info["subtype"], info["shape"]))
            else:
                profiles.append((ch, "?", -1, "unknown"))
        return profiles

    # ── μ (multiplication): recompose glyph profiles → canonical string ────
    def _recompose(self, profiles: list) -> str:
        """Unparse profile list back into Shavian sentence."""
        return "".join(p[0] for p in profiles)

    # ── μ∘δ verification on canonical sentence ────────────────────────────
    def _verify_frobenius_law(self) -> bool:
        """Verify that decompose(recompose(decompose(s))) = decompose(s)."""
        print("  Canonical sentence: " + CORE_SENTENCE)
        print("  Length: %d glyphs" % len(CORE_SENTENCE))

        # δ: decompose
        profiles = self._decompose(CORE_SENTENCE)
        print("  δ-decompose → %d profiles" % len(profiles))
        for g, p, s, sh in profiles:
            print(f"    {g} → {p}[{s}] ({sh})")

        # μ: recompose
        recomposed = self._recompose(profiles)
        print("  μ-recompose → " + recomposed)

        # Check roundtrip: δ∘μ∘δ = δ  (equivalent to μ∘δ = id on the space of profiles)
        profiles2 = self._decompose(recomposed)
        roundtrip_match = profiles == profiles2
        print(f"  δ∘μ∘δ = δ? {roundtrip_match}")

        # Also verify: μ∘δ on the sentence itself
        sentence_roundtrip = self._recompose(self._decompose(CORE_SENTENCE))
        sentence_match = sentence_roundtrip == CORE_SENTENCE
        print(f"  μ∘δ(sentence) = sentence? {sentence_match}")

        return roundtrip_match and sentence_match

    def verify(self) -> bool:
        """Full verification: Frobenius law + self-imscription."""
        print("=== Shavian Ob3ect ===")
        print("")

        layer_ok = self._verify_frobenius_law()
        print("")
        print("Frobenius layer: %s" % ("PASS" if layer_ok else "FAIL"))

        # Self-imscription: μ∘δ=id on own source
        print("")
        print("Self-imscription verification:")
        frob_ok = frobenius_phase(self.source)
        print("")

        closure = layer_ok and frob_ok
        h = hashlib.sha256(self.source.encode("utf-8")).hexdigest()[:24]
        print(f"Imscription anchor: {h}...")
        print(f"Closure: {closure}")
        print("")
        print("\"In Accordance with our Wilt, In Accordance with the Grammar\"")
        return closure


if __name__ == "__main__":
    sys.exit(0 if ShavianOb3ect().verify() else 1)
