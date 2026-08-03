#!/usr/bin/env python3
"""
IG_latex.py — Canonical LaTeX for Imscribing Grammar primitives.

Usage:
  python3 IG_latex.py fmt  𐑦           # → \\sh{𐑦}  (no $ delimiters)
  python3 IG_latex.py inline 𐑦         # → $\\sh{𐑦}$
  python3 IG_latex.py tuple "𐑦 𐑸 …"  # display-math crystal address
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
# Every value is written as itself, set in the primitive font. The table this
# replaces rendered each one as a retired axis glyph carrying a subscript —
# a retired axis glyph carrying a subscript, from before the values were
# Shavian, kept alive only
# by this converter.
def PRIM_LATEX_of(value: str) -> str:
    return r"\sh{" + value + "}"


# ── Public API ────────────────────────────────────────────────────────────────

def fmt(raw_id: str) -> str:
    """Return canonical LaTeX body for a source ID like 'ƒ^ż'. No $ delimiters."""
    if raw_id not in PRIM_LATEX:
        raise KeyError(f"Unknown primitive ID: {raw_id!r}")
    return PRIM_LATEX_of(raw_id)


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
        # de-duplicate: ⊙ aliases point to same canonical as ⊙ entries
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

    # Also handle ⊙ prim char → ⊙ canonical (the old key in source documents)
    for raw_id, canonical in PRIM_LATEX.items():
        if not raw_id.startswith('⊙'):
            continue
        _, sub = raw_id.split('_', 1)
        sub_pat = _subtype_pattern(sub)
        pat = (
            re.escape('⊙')
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
    orig_set  = set(re.findall(r'[⊢⊣>ΦƒÇΓɢ⊙Ħ-ΩΣ⊙][_^][^\s;\\$\{]+', original))
    fixed_set = set(re.findall(r'[⊢⊣>ΦƒÇΓɢ⊙Ħ-ΩΣ⊙][_^][^\s;\\$\{]+', fixed))
    print(f"Fixed: {path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cmd_list():
    for raw_id, canon in PRIM_LATEX.items():
        if raw_id.startswith('⊙'):
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
