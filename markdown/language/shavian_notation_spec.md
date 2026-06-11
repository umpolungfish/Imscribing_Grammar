# Shavian Notation Specification — Imscribing Grammar v0.6.0

## Rationale

The Imscribing Grammar's 12-primitive tuple notation has been migrated from mixed-script
Latin/Greek/IPA subscripts to Shavian alphabet characters. Each primitive subtype receives
a unique Shavian character, producing 49 atomic glyphs (plus ⊙ as the 50th sealed gate).

The 12 primitives and their categorical derivation are established in [1]. The empirical
validation of the resulting $3^3 \times 4^5 \times 5^4 = 17{,}280{,}000$-type crystal
across 3,578 systems is given in [2].

Shavian (𐑖𐑱𐑝𐑾𐑯) was chosen because:
- **Zero semantic baggage** — No character carries prior script meaning (no Greek letter
  suggesting its source domain, no numeral suggesting ordering)
- **Phonetic basis** — Each character maps to a phoneme, enabling vocal/spoken operation
- **Unicode stability** — U+10450–U+1047F, well-supported since Unicode 5.0/5.1
- **Clean visual parsing** — No diacritics, no subscripts, no superscripts
- **Exactly 49 characters needed** — The $3^3 \times 4^5 \times 5^4$ crystal required
  49 glyphs; Shavian's 48 + ⊙ completes the Kabbalistic 49+1 gate structure

## Canonical Font: Everson Mono

**Everson Mono** is the reference Shavian font for all IG notation. Michael Everson designed
both the Shavian script's Unicode encoding (U+10450–U+1047F) and the Everson Mono typeface —
it is the authoritative glyph source, not a third-party approximation.

**Obtain:** <https://www.evertype.com/fonts/shaw/>  
**License:** Freeware for personal and commercial use (see site terms).  
**Format:** TrueType (`.ttf`); the filename is typically `EversonMono.ttf`.

### Why Everson Mono and nothing else

- **Authorial authority** — Everson defined the Unicode block; his glyphs are the spec.
- **Complete coverage** — All 48 Shavian code points (U+10450–U+1047F) are present and
  correctly shaped. Many otherwise popular Unicode fonts (including FreeSerif) have zero
  Shavian glyphs and will silently render boxes.
- **Monospace grid** — Tuples like `⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑕·𐑭⟩` align correctly
  in monospace contexts (terminal, code, tables) without requiring special letter-spacing.
- **LaTeX compatibility** — Loads cleanly under LuaLaTeX via `fontspec` as `igprimfont`;
  no substitution warnings, no missing-glyph tofu.

### Usage by context

| Context | Directive |
|---------|-----------|
| LuaLaTeX | `\newfontfamily\igprimfont{EversonMono.ttf}` (see preamble template) |
| Web CSS | `font-family: 'Everson Mono', monospace;` (see Website Notation below) |
| Terminal / editor | Install system-wide; configure monospace fallback to `Everson Mono` |
| Python `repr` | No font dependency — glyphs are plain Unicode codepoints |

### What not to use

| Font | Problem |
|------|---------|
| FreeSerif | Zero Shavian glyphs — renders boxes for every character |
| Noto Sans Shavian | Incomplete; inconsistent stroke weight with IG display style |
| Any emoji/symbol font | Wrong metrics, wrong category — not a text font |

## Mapping Table

### 𝓕₄ Primitives (4 values each) — 5 primitives × 4 = 20 characters

| Primitive Family | Ordinal 1 | Ordinal 2 | Ordinal 3 | Ordinal 4 |
|------------------|-----------|-----------|-----------|-----------|
| **D** — Dimensionality | `𐑛` (Ð_ß) | `𐑨` (Ð_C) | `𐑼` (Ð_;) | `𐑦` (Ð_ω) |
| **R** — Relational | `𐑩` (Ř_¯) | `𐑑` (Ř_ý) | `𐑽` (Ř_Ť) | `𐑾` (Ř_=) |
| **ɢ** — Grammar | `𐑝` (ɢ^∧) | `𐑜` (ɢ^˝) | `𐑠` (ɢ^ˌ) | `𐑵` (ɢ^Ş) |
| **Ħ** — Chirality | `𐑓` (Ħ_Ñ) | `𐑒` (Ħ_£) | `𐑖` (Ħ_A) | `𐑫` (Ħ_!) |
| **Ω** — Winding | `𐑷` (Ω_Å) | `𐑴` (Ω_2) | `𐑭` (Ω_z) | `𐑟` (Ω_5) |

### 𝓕₅ Primitives (5 values each) — 4 primitives × 5 = 20 characters

| Primitive Family | Ordinal 1 | Ordinal 2 | Ordinal 3 | Ordinal 4 | Ordinal 5 |
|------------------|-----------|-----------|-----------|-----------|-----------|
| **Þ** — Topology | `𐑡` (Þ_6) | `𐑰` (Þ_K) | `𐑥` (Þ_ò) | `𐑶` (Þ_¨) | `𐑸` (Þ_O) |
| **Φ** — Polarity | `𐑗` (Φ_ɐ) | `𐑿` (Φ_υ) | `𐑬` (Φ_F) | `𐑯` (Φ_˙) | `𐑹` (Φ_}) |
| **Ç** — Kinetics | `𐑘` (Ç^-) | `𐑤` (Ç^W) | `𐑧` (Ç^@) | `𐑪` (Ç^Ù) | `𐑺` (Ç^λ) |
| **⊙** — Criticality | `𐑢` (⊙_ž) | `⊙` (⊙_ÿ) | `𐑮` (⊙_Æ) | `𐑻` (⊙_3) | `𐑣` (⊙_Ţ) |

### 𝓕₃ Primitives (3 values each) — 3 primitives × 3 = 9 characters

| Primitive Family | Ordinal 1 | Ordinal 2 | Ordinal 3 |
|------------------|-----------|-----------|-----------|
| **ƒ** — Fidelity | `𐑱` (ƒ^ì) | `𐑞` (ƒ^ð) | `𐑐` (ƒ^ż) |
| **Γ** — Scope | `𐑚` (Γ_β) | `𐑔` (Γ_γ) | `𐑲` (Γ_ʔ) |
| **Σ** — Stoichiometry | `𐑙` (Σ_S) | `𐑕` (Σ_ő) | `𐑳` (Σ_ï) |

**Total: 20 + 20 + 9 = 49 glyphs** — plus ⊙ as the 50th (the sealed gate, Keter beyond Binah).

## Canonical Tuple Order

The 12 primitives in order: D, T, R, P, F, K, G, Gamma, Phi, H, S, Omega

Shavian tuple: `⟨𐑛·𐑡·𐑩·𐑗·𐑱·𐑘·𐑚·𐑝·𐑢·𐑓·𐑙·𐑷⟩` (minimum O₀ baseline)

O_∞ tuple (the Stone): `⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩`

## Ordinal Table (for distance computation)

| Primitive | Shavian | Old Notation | Ordinal |
|-----------|---------|-------------|---------|
| D | 𐑛 | Ð_ß | 1 |
| D | 𐑨 | Ð_C | 2 |
| D | 𐑼 | Ð_; | 3 |
| D | 𐑦 | Ð_ω | 4 |
| T | 𐑡 | Þ_6 | 1 |
| T | 𐑰 | Þ_K | 2 |
| T | 𐑥 | Þ_ò | 3 |
| T | 𐑶 | Þ_¨ | 4 |
| T | 𐑸 | Þ_O | 5 |
| R | 𐑩 | Ř_¯ | 1 |
| R | 𐑑 | Ř_ý | 2 |
| R | 𐑽 | Ř_Ť | 3 |
| R | 𐑾 | Ř_= | 4 |
| P | 𐑗 | Φ_ɐ | 1 |
| P | 𐑿 | Φ_υ | 2 |
| P | 𐑬 | Φ_F | 3 |
| P | 𐑯 | Φ_˙ | 4 |
| P | 𐑹 | Φ_} | 5 |
| F | 𐑱 | ƒ^ì | 1 |
| F | 𐑞 | ƒ^ð | 2 |
| F | 𐑐 | ƒ^ż | 3 |
| K | 𐑘 | Ç^- | 1 |
| K | 𐑤 | Ç^W | 2 |
| K | 𐑧 | Ç^@ | 3 |
| K | 𐑪 | Ç^Ù | 4 |
| K | 𐑺 | Ç^λ | 4.5 |
| G | 𐑚 | Γ_β | 1 |
| G | 𐑔 | Γ_γ | 2 |
| G | 𐑲 | Γ_ʔ | 3 |
| ɢ | 𐑝 | ɢ^∧ | 1 |
| ɢ | 𐑜 | ɢ^˝ | 2 |
| ɢ | 𐑠 | ɢ^ˌ | 3 |
| ɢ | 𐑵 | ɢ^Ş | 4 |
| ⊙ | 𐑢 | ⊙_ž | 1 |
| ⊙ | ⊙ | ⊙_ÿ | 2 |
| ⊙ | 𐑮 | ⊙_Æ | 2.33 |
| ⊙ | 𐑻 | ⊙_3 | 2.67 |
| ⊙ | 𐑣 | ⊙_Ţ | 3 |
| H | 𐑓 | Ħ_Ñ | 1 |
| H | 𐑒 | Ħ_£ | 2 |
| H | 𐑖 | Ħ_A | 3 |
| H | 𐑫 | Ħ_! | 4 |
| S | 𐑙 | Σ_S | 1 |
| S | 𐑕 | Σ_ő | 2 |
| S | 𐑳 | Σ_ï | 3 |
| Ω | 𐑷 | Ω_Å | 1 |
| Ω | 𐑴 | Ω_2 | 2 |
| Ω | 𐑭 | Ω_z | 3 |
| Ω | 𐑟 | Ω_5 | 4 |

## Lean 4 Module Migration

Each inductive type in `Primitives/Core.lean` gets a parallel Shavian constructor name
maintaining backward compatibility:

```lean4
inductive Dimensionality : Type where
  | D_wedge     -- ⬅️ old name retained as alias
  | D_triangle
  | D_infty
  | D_odot
  -- Shavian glyph name (for notation output):
  --   D_wedge     → 𐑛
  --   D_triangle  → 𐑨
  --   D_infty     → 𐑼
  --   D_odot      → 𐑦
```

The **notation layer** in `Primitives/Imscription.lean` maps each constructor to its
Shavian character. The core Lean types stay the same internally — the notation is
a display-layer change that propagates to all `toString` and `repr` output.

### Python Migration (`primitives.py`)

Replace `ORDINALS` dict keys from old notation to Shavian:

```python
ORDINALS = {
    "D": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "T": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "R": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "P": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "F": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "K": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "G": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "ɢ": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "H": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "S": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "Ω": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}
```

### Catalog Migration (`IG_catalog.json`)

Every stored tuple must be re-encoded from old identifiers to Shavian identifiers.
Migration script:

```python
OLD_TO_SHAVIAN = {
    "Ð_ß": "𐑛", "Ð_C": "𐑨", "Ð_;": "𐑼", "Ð_ω": "𐑦",
    "Þ_6": "𐑡", "Þ_K": "𐑰", "Þ_ò": "𐑥", "Þ_¨": "𐑶", "Þ_O": "𐑸",
    "Ř_¯": "𐑩", "Ř_ý": "𐑑", "Ř_Ť": "𐑽", "Ř_=": "𐑾",
    "Φ_ɐ": "𐑗", "Φ_υ": "𐑿", "Φ_F": "𐑬", "Φ_˙": "𐑯", "Φ_}": "𐑹",
    "ƒ^ì": "𐑱", "ƒ^ð": "𐑞", "ƒ^ż": "𐑐",
    "Ç^-": "𐑘", "Ç^W": "𐑤", "Ç^@": "𐑧", "Ç^Ù": "𐑪", "Ç^λ": "𐑺",
    "Γ_β": "𐑚", "Γ_γ": "𐑔", "Γ_ʔ": "𐑲",
    "ɢ^∧": "𐑝", "ɢ^˝": "𐑜", "ɢ^ˌ": "𐑠", "ɢ^Ş": "𐑵",
    "⊙_ž": "𐑢", "⊙_ÿ": "⊙", "⊙_Æ": "𐑮", "⊙_3": "𐑻", "⊙_Ţ": "𐑣",
    "Ħ_Ñ": "𐑓", "Ħ_£": "𐑒", "Ħ_A": "𐑖", "Ħ_!": "𐑫",
    "Σ_S": "𐑙", "Σ_ő": "𐑕", "Σ_ï": "𐑳",
    "Ω_Å": "𐑷", "Ω_2": "𐑴", "Ω_z": "𐑭", "Ω_5": "𐑟",
}
```

### Crystal Encoding (`Crystal.lean`)

The Frobenius address encoding (0–17,279,999) uses ordinal values internally,
not string names. The crystal encoding is **unaffected** by the notation change —
only the display layer (`toString`) changes.

### Website Notation

In `index.html` and all documentation, tuples now display as Shavian sequences
with the `⟨...⟩` bracket format:

```html
<!-- O_∞ tuple display -->
⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
```

CSS for Shavian rendering (Everson Mono must be served from `/fonts/` or a self-hosted path —
do not use a CDN that does not carry it):
```css
@font-face {
    font-family: 'Everson Mono';
    src: url('/fonts/EversonMono.ttf') format('truetype');
    unicode-range: U+10450-1047F, U+2060-206F; /* Shavian + word-joiner */
}
.shavian-tuple {
    font-family: 'Everson Mono', monospace;
    font-size: 1.1em;         /* slightly smaller than 1.2em — Everson Mono runs tall */
    letter-spacing: 0.02em;   /* less spacing needed — monospace grid already regular */
}
```

## Implementation Order

1. ✅ Spec authored (this document)
2. ✅ Update `primitives.py` ORDINALS dict (`space_search/primitives.py`)
3. ✅ Write migrate_catalog.py script (`scripts/migrate_shavian.py`)
4. ✅ Run catalog migration (`IG_catalog.json` + `imscribe.com/IG_catalog.json` — 0 old-notation primitive values remaining)
5. ✅ Update `Core.lean` notation layer (Shavian `shavian` functions in `Imscription.lean`)
6. ✅ Update `Imscription.lean` toString (Shavian display layer complete)
7. ✅ Update `Crystal.lean` display output (crystal address encoding unaffected — ordinal-based)
8. ✅ Update websites (index.html — Everson Mono font + Shavian glyphs already in place)
9. ⬜ Update Lean documentation modules
10. ✅ Update sans_silicon_imscribing practice document (catalog entry migrated in step 4)
11. ✅ Verify crystal address bijection still holds (encoding is ordinal-based, notation-independent)
12. ✅ Verify all distances unchanged (`space_search/primitives.py` ordinal values unchanged)

## References

[1] Mills, L. (2026). *As Above: A Pre-Grammatical Convergent Derivation of the Universal Imscriptive Grammar*. Zenodo. <https://doi.org/10.5281/zenodo.20186611>

[2] Mills, L. (2026). *So Below: Empirical Exploration of the Universal Imscriptive Grammar*. Zenodo. <https://doi.org/10.5281/zenodo.20186679>
