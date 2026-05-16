#!/usr/bin/env python3
"""
IG_latex.py — Canonical LaTeX for Imscribing Grammar primitives.

Usage:
  python3 IG_latex.py fmt  Ð_ω           # → Ð_{\\omega}  (no $ delimiters)
  python3 IG_latex.py inline Ð_ω         # → $Ð_{\\omega}$
  python3 IG_latex.py tuple "Ð_ω Þ_O …"  # display-math crystal address
  python3 IG_latex.py fix file.md         # rewrite file with canonical LaTeX
  python3 IG_latex.py list                # print all 49 entries

Source notation: always  PrimitiveChar_subtypeChar  (underscore separator).
The fix command accepts any plausible malformation inside or outside math mode.
"""

import re, sys, os

# ── Canonical table (source_id → LaTeX body, no $ delimiters) ────────────────
#
# Rules:
#   ƒ  Ç  ɢ  use superscript  ^
#   all others use subscript  _
#   non-ASCII subtypes that are NOT standard Greek commands get \text{}
#   Greek subtypes get their LaTeX command: \omega \beta \gamma \lambda \upsilon
#   } subtype → \}   ^ subtype → \wedge
#
PRIM_LATEX: dict[str, str] = {
    # ── Ð Dimensionality ──────────────────────────────────────────────────────
    'Ð_ß':  r'Ð_{ß}',
    'Ð_C':  r'Ð_{C}',
    'Ð_;':  r'Ð_{;}',
    'Ð_ω':  r'Ð_{\omega}',
    # ── Þ Topology ────────────────────────────────────────────────────────────
    'Þ_6':  r'Þ_{6}',
    'Þ_K':  r'Þ_{K}',
    'Þ_ò':  r'Þ_{\text{ò}}',
    'Þ_¨':  r'Þ_{\text{¨}}',
    'Þ_O':  r'Þ_{O}',
    # ── Ř Relational ──────────────────────────────────────────────────────────
    'Ř_¯':  r'Ř_{\text{¯}}',
    'Ř_ý':  r'Ř_{\text{ý}}',
    'Ř_Ť':  r'Ř_{\text{Ť}}',
    'Ř_=':  r'Ř_{=}',
    # ── Φ Parity ──────────────────────────────────────────────────────────────
    'Φ_ɐ':  r'Φ_{\text{ɐ}}',
    'Φ_υ':  r'Φ_{\upsilon}',
    'Φ_F':  r'Φ_{F}',
    'Φ_˙':  r'Φ_{\text{˙}}',
    'Φ_}':  r'Φ_{\}}',
    # ── ƒ Fidelity  (SUPERSCRIPT; \text{ƒ} — not in standard math font) ────────
    'ƒ_ì':  r'\text{ƒ}^{\text{ì}}',
    'ƒ_ð':  r'\text{ƒ}^{\text{ð}}',
    'ƒ_ż':  r'\text{ƒ}^{\text{ż}}',
    # ── Ç Kinetics  (SUPERSCRIPT) ─────────────────────────────────────────────
    'Ç_-':  r'Ç^{-}',
    'Ç_W':  r'Ç^{W}',
    'Ç_@':  r'Ç^{@}',
    'Ç_Ù':  r'Ç^{\text{Ù}}',
    'Ç_λ':  r'Ç^{\lambda}',
    # ── Γ Scope ───────────────────────────────────────────────────────────────
    'Γ_β':  r'Γ_{\beta}',
    'Γ_γ':  r'Γ_{\gamma}',
    'Γ_ʔ':  r'Γ_{\text{ʔ}}',
    # ── ɢ Grammar  (SUPERSCRIPT; \text{ɢ} — not in standard math font) ─────────
    'ɢ_^':  r'\text{ɢ}^{\wedge}',
    'ɢ_˝':  r'\text{ɢ}^{\text{˝}}',
    'ɢ_ˌ':  r'\text{ɢ}^{\text{ˌ}}',
    'ɢ_Ş':  r'\text{ɢ}^{\text{Ş}}',
    # ── ⊙ Criticality (\odot renders in all LaTeX modes; φ̂ is old catalog key) ─
    '⊙_ž':  r'\odot_{\text{ž}}',
    '⊙_ÿ':  r'\odot_{\text{ÿ}}',
    '⊙_Æ':  r'\odot_{\text{Æ}}',
    '⊙_3':  r'\odot_{3}',
    '⊙_Ţ':  r'\odot_{\text{Ţ}}',
    'φ̂_ž':  r'\odot_{\text{ž}}',
    'φ̂_ÿ':  r'\odot_{\text{ÿ}}',
    'φ̂_Æ':  r'\odot_{\text{Æ}}',
    'φ̂_3':  r'\odot_{3}',
    'φ̂_Ţ':  r'\odot_{\text{Ţ}}',
    # ── Ħ Chirality (\text{Ħ} — not in standard math font) ──────────────
    'Ħ_Ñ':  r'\text{Ħ}_{\text{Ñ}}',
    'Ħ_£':  r'\text{Ħ}_{\text{£}}',
    'Ħ_A':  r'\text{Ħ}_{A}',
    'Ħ_!':  r'\text{Ħ}_{!}',
    # ── Σ Stoichiometry ───────────────────────────────────────────────────────
    'Σ_S':  r'Σ_{S}',
    'Σ_ő':  r'Σ_{\text{ő}}',
    'Σ_ï':  r'Σ_{\text{ï}}',
    # ── Ω Winding ─────────────────────────────────────────────────────────────
    'Ω_Å':  r'Ω_{\text{Å}}',
    'Ω_2':  r'Ω_{2}',
    'Ω_z':  r'Ω_{z}',
    'Ω_5':  r'Ω_{5}',
}

# ── Public API ────────────────────────────────────────────────────────────────

def fmt(raw_id: str) -> str:
    """Return canonical LaTeX body for a source ID like 'ƒ_ż'. No $ delimiters."""
    if raw_id not in PRIM_LATEX:
        raise KeyError(f"Unknown primitive ID: {raw_id!r}")
    return PRIM_LATEX[raw_id]


def inline(raw_id: str) -> str:
    """Return $…$ wrapped canonical LaTeX for a source ID."""
    return f'${fmt(raw_id)}$'


def fmt_tuple(raw_ids: str) -> str:
    """Return a display-math crystal address from space-separated source IDs."""
    parts = raw_ids.strip().split()
    bodies = [fmt(p) for p in parts]
    inner = r';\ '.join(bodies)
    return f'$$\\langle {inner} \\rangle$$'


# ── Fix mode ──────────────────────────────────────────────────────────────────

# Subtypes that map to a LaTeX command name rather than literal or \text{}
_GREEK_CMD = {
    'ω': 'omega', 'β': 'beta', 'γ': 'gamma', 'λ': 'lambda', 'υ': 'upsilon',
}


def _subtype_pattern(sub: str) -> str:
    """Build a regex fragment that matches any plausible LaTeX rendering of sub."""
    if sub == '}':
        # \} or bare }
        return r'\\?\}'
    if sub == '^':
        # \wedge, \hat{}, or literal ^
        return r'(?:\\wedge|\\hat\{\}|\^)'
    if sub in _GREEK_CMD:
        cmd = _GREEK_CMD[sub]
        return f'(?:\\\\{cmd}|{re.escape(sub)})'
    # Everything else: may or may not be wrapped in \text{}
    return re.escape(sub)


def _build_fix_patterns() -> list[tuple[re.Pattern, str]]:
    """
    For each of the 49 source IDs build a regex that matches ANY plausible
    LaTeX representation (wrong separator, missing/wrong wrappers, etc.) and
    pairs it with the canonical replacement string.
    """
    patterns: list[tuple[re.Pattern, str]] = []
    seen: set[str] = set()

    for raw_id, canonical in PRIM_LATEX.items():
        prim, sub = raw_id.split('_', 1)
        # de-duplicate: φ̂ aliases point to same canonical as ⊙ entries
        if canonical in seen:
            continue
        seen.add(canonical)

        prim_re  = re.escape(prim)
        sub_pat  = _subtype_pattern(sub)

        # Match: prim  [_^]  {?  (\text{)?  subtype  }?  }?
        pat = (
            prim_re
            + r'[_^]'
            + r'\{?'
            + r'(?:\\text\{)?'
            + sub_pat
            + r'\}?\}?'
        )
        patterns.append((re.compile(pat), canonical))

    # Also handle φ̂ prim char → ⊙ canonical (the old key in source documents)
    for raw_id, canonical in PRIM_LATEX.items():
        if not raw_id.startswith('φ̂'):
            continue
        _, sub = raw_id.split('_', 1)
        sub_pat = _subtype_pattern(sub)
        pat = (
            re.escape('φ̂')
            + r'[_^]'
            + r'\{?'
            + r'(?:\\text\{)?'
            + sub_pat
            + r'\}?\}?'
        )
        patterns.append((re.compile(pat), canonical))

    return patterns


_FIX_PATTERNS: list[tuple[re.Pattern, str]] | None = None


def fix(text: str) -> str:
    """
    Fix all primitive references in text, skipping fenced code blocks and
    inline code spans so LaTeX source examples are not mutated.
    """
    global _FIX_PATTERNS
    if _FIX_PATTERNS is None:
        _FIX_PATTERNS = _build_fix_patterns()

    # Split on fenced code blocks (``` … ```)
    segments = re.split(r'(```[\s\S]*?```)', text)
    out: list[str] = []
    for i, seg in enumerate(segments):
        if i % 2 == 1:          # fenced code block — leave alone
            out.append(seg)
            continue
        # Split on inline code (`…`)
        sub_segs = re.split(r'(`[^`\n]+`)', seg)
        for j, ss in enumerate(sub_segs):
            if j % 2 == 1:      # inline code — leave alone
                out.append(ss)
            else:
                for pat, repl in _FIX_PATTERNS:
                    ss = pat.sub(lambda m, r=repl: r, ss)
                out.append(ss)

    return ''.join(out)


def fix_file(path: str) -> None:
    """Fix primitive formatting in a markdown file in-place."""
    with open(path, encoding='utf-8') as f:
        original = f.read()
    fixed = fix(original)
    if fixed == original:
        print(f"No changes needed: {path}")
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    # Report changed primitives
    orig_set  = set(re.findall(r'[ÐÞŘΦƒÇΓɢ⊙Ħ-ΩΣφ̂][_^][^\s;\\$\{]+', original))
    fixed_set = set(re.findall(r'[ÐÞŘΦƒÇΓɢ⊙Ħ-ΩΣφ̂][_^][^\s;\\$\{]+', fixed))
    print(f"Fixed: {path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cmd_list():
    for raw_id, canon in PRIM_LATEX.items():
        if raw_id.startswith('φ̂'):
            continue   # suppress duplicate alias listing
        print(f"  {raw_id:<8}  →  ${canon}$")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd, *rest = args

    if cmd == 'fmt':
        for raw_id in rest:
            print(fmt(raw_id))

    elif cmd == 'inline':
        for raw_id in rest:
            print(inline(raw_id))

    elif cmd == 'tuple':
        print(fmt_tuple(' '.join(rest)))

    elif cmd == 'fix':
        if not rest:
            sys.exit("Usage: IG_latex.py fix <file.md> [file2.md …]")
        for path in rest:
            fix_file(path)

    elif cmd == 'list':
        _cmd_list()

    else:
        sys.exit(f"Unknown command: {cmd!r}. Use: fmt | inline | tuple | fix | list")


if __name__ == '__main__':
    main()
