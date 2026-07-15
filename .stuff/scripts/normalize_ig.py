#!/usr/bin/env python3
"""
normalize_ig.py — IG primitive glyph normalizer
Enforces SYMBOL_REFERENCE.md formatting across all source files.

Usage:
    python normalize_ig.py [file ...]        # normalize specific files
    python normalize_ig.py --check [file ...]  # exit 1 if any changes needed
    python normalize_ig.py --staged            # normalize all staged .md/.tex files

Called automatically by .git/hooks/pre-commit.
"""

import re
import sys
import subprocess
from pathlib import Path

# φ (U+03C6) + U+0302 (combining circumflex) — WRONG glyph for Criticality
PHI_HAT = 'φ' + chr(0x0302)

# Canonical 12 primitive glyphs.  ASCII surrogates that people type by mistake:
#   D→Ð  T→Þ  R→Ř  P→Φ  F/f→ƒ  C→Ç  G→Γ  g→ɢ  ⊙→⊙  H→Ħ  S→Σ  W→Ω
ASCII_TO_PRIM = {
    'D': 'Ð', 'T': 'Þ', 'R': 'Ř', 'P': 'Φ',
    'F': 'ƒ', 'f': 'ƒ', 'C': 'Ç', 'G': 'Γ',
    'g': 'ɢ', 'H': 'Ħ', 'S': 'Σ', 'W': 'Ω',
}

# Non-ASCII subtype chars that uniquely identify a specific primitive.
# Used to safely replace wrong ASCII chars without false positives.
# Only non-ASCII subtypes included — ASCII subtypes (like =, 6, A) are skipped
# because they're too ambiguous to replace confidently in prose.
_PRIM_SAFE_SUBTYPES: dict[str, tuple[str, list[str]]] = {
    # wrong_ascii: (correct_glyph, [non-ASCII subtype chars safe to match on])
    'D': ('Ð', ['ω', 'ß']),
    'T': ('Þ', ['ò', '¨']),
    'R': ('Ř', ['¯', 'ý', 'Ť']),
    'P': ('Φ', ['ɐ', 'υ', '˙']),
    'G': ('Γ', ['β', 'γ', 'ʔ']),
    'H': ('Ħ', ['Ñ', '£']),
    'S': ('Σ', ['ő', 'ï']),
}

# ── \text{{\igprimfont X}} wrong-ASCII fixer ─────────────────────────────────
# Matches the exact manuscript pattern; X must be one of the ASCII surrogates.
_IGPF_WRONG_RE = re.compile(
    r'(\\text\{\{\\igprimfont\s+)([DTRPFfCGgHSW])(\}\})'
)

def fix_igprimfont_wrong_ascii(text: str) -> str:
    """Replace ASCII surrogate in \\text{{\\igprimfont X}} with the canonical glyph."""
    def _repl(m: re.Match) -> str:
        return m.group(1) + ASCII_TO_PRIM[m.group(2)] + m.group(3)
    return _IGPF_WRONG_RE.sub(_repl, text)


# ── Markdown normalizer helpers ───────────────────────────────────────────────
# The igpdf pipeline (pandoc → xelatex + IG_primitives.lua) handles font
# wrapping automatically for correct Unicode glyphs.  normalize_md only needs
# to ensure the right Unicode char is present — not add \text{} wrappers.

def _md_wrong_prim_fixes() -> list[tuple[str, str]]:
    """
    Build (old, new) string-replacement pairs for wrong ASCII primitives in .md.
    Covers three surface forms for each (wrong, subtype) pair:
      $X_{sub}$   $X_{\text{sub}}$   bare X_sub (tuple / prose)
    Only non-ASCII subtypes used — ASCII subtypes are too ambiguous.
    """
    pairs = []
    for wrong, (glyph, subtypes) in _PRIM_SAFE_SUBTYPES.items():
        for sub in subtypes:
            # math mode with \text wrapper: $D_{\text{ω}}$
            pairs.append((f'${wrong}_{{\\text{{{sub}}}}}$', f'${glyph}_{{\\text{{{sub}}}}}$'))
            # math mode bare subscript: $D_{ω}$
            pairs.append((f'${wrong}_{{{sub}}}$', f'${glyph}_{{{sub}}}$'))
            # bare subscript outside math (tuple notation, prose): D_ω
            pairs.append((f'{wrong}_{sub}', f'{glyph}_{sub}'))
    return pairs

_MD_WRONG_PRIM_FIXES = _md_wrong_prim_fixes()


# ── Markdown normalization ───────────────────────────────────────────────────

def normalize_md(text: str) -> str:
    # Criticality primitive is ⊙ (U+2299), not ⊙
    text = text.replace(PHI_HAT, '⊙')

    # All other wrong ASCII primitive surrogates in IG notation contexts
    for old, new in _MD_WRONG_PRIM_FIXES:
        text = text.replace(old, new)

    return text


# ── LaTeX math-mode normalization (no \igprimfont) ──────────────────────────
# Source of truth: SYMBOL_REFERENCE.md
# Primitives using SUPERSCRIPT (^): ƒ Ç ɢ
# All others use SUBSCRIPT (_)

# Complete \texttt{Prim\_subtype} → $math_form$ table
# Order matters: more specific patterns first
TEXTTT_FIXES = [
    # Parity/symmetry (Φ) — most specific first (pandoc mangles 𐑿 → Ph$i_{\upsilon}$)
    (r'\texttt{Ph$i_{\upsilon}$}',   r'$\Phi_{\upsilon}$'),
    (r'\texttt{Φ\_\}}',              r'$\Phi_{\}}$'),
    (r'\texttt{Φ\_ɐ}',              r'$\Phi_{\text{ɐ}}$'),
    (r'\texttt{Φ\_F}',               r'$\Phi_{F}$'),
    (r'\texttt{Φ\_˙}',              r'$\Phi_{\text{˙}}$'),
    # Criticality (⊙) — subscript; pandoc may have left $\odot$
    (r'\texttt{$\odot$\_Æ}',        r'$\odot_{\text{Æ}}$'),
    (r'\texttt{$\odot$\_ÿ}',        r'$\odot_{\text{ÿ}}$'),
    (r'\texttt{$\odot$\_ž}',        r'$\odot_{\text{ž}}$'),
    (r'\texttt{$\odot$\_3}',        r'$\odot_{3}$'),
    (r'\texttt{$\odot$\_Ţ}',        r'$\odot_{\text{Ţ}}$'),
    (r'\texttt{⊙\_Æ}',              r'$\odot_{\text{Æ}}$'),
    (r'\texttt{⊙\_ÿ}',              r'$\odot_{\text{ÿ}}$'),
    # Winding (Ω)
    (r'\texttt{Ω\_z}',               r'$\Omega_{z}$'),
    (r'\texttt{Ω\_2}',               r'$\Omega_{2}$'),
    (r'\texttt{Ω\_5}',               r'$\Omega_{5}$'),
    (r'\texttt{Ω\_Å}',               r'$\Omega_{\text{Å}}$'),
    # Kinetics (Ç) — SUPERSCRIPT
    (r'\texttt{Ç\_@}',               r'$\text{Ç}^{@}$'),
    (r'\texttt{Ç\_W}',               r'$\text{Ç}^{W}$'),
    (r'\texttt{Ç\_-}',               r'$\text{Ç}^{-}$'),
    (r'\texttt{Ç\_Ù}',               r'$\text{Ç}^{\text{Ù}}$'),
    (r'\texttt{Ç\_λ}',               r'$\text{Ç}^{\lambda}$'),
    # Relational mode (Ř) — subscript
    (r'\texttt{Ř\_Ť}',               r'$\text{Ř}_{\text{Ť}}$'),
    (r'\texttt{Ř\_ý}',               r'$\text{Ř}_{\text{ý}}$'),
    (r'\texttt{Ř\_=}',               r'$\text{Ř}_{=}$'),
    (r'\texttt{Ř\_¯}',               r'$\text{Ř}_{\text{¯}}$'),
    # Chirality (Ħ) — subscript
    (r'\texttt{Ħ\_!}',               r'$\text{Ħ}_{!}$'),
    (r'\texttt{Ħ\_A}',               r'$\text{Ħ}_{A}$'),
    (r'\texttt{Ħ\_Ñ}',               r'$\text{Ħ}_{\text{Ñ}}$'),
    (r'\texttt{Ħ\_£}',               r'$\text{Ħ}_{\text{£}}$'),
    # Topology (Þ) — subscript
    (r'\texttt{Þ\_ò}',               r'$\text{Þ}_{\text{ò}}$'),
    (r'\texttt{Þ\_O}',               r'$\text{Þ}_{O}$'),
    (r'\texttt{Þ\_¨}',               r'$\text{Þ}_{\text{¨}}$'),
    (r'\texttt{Þ\_K}',               r'$\text{Þ}_{K}$'),
    (r'\texttt{Þ\_6}',               r'$\text{Þ}_{6}$'),
    # Interaction grammar (ɢ) — SUPERSCRIPT
    (r'\texttt{ɢ\_ˌ}',               r'$\text{ɢ}^{\text{ˌ}}$'),
    (r'\texttt{ɢ\_\^{}}',            r'$\text{ɢ}^{\wedge}$'),
    (r'\texttt{ɢ\_Ş}',               r'$\text{ɢ}^{\text{Ş}}$'),
    (r'\texttt{ɢ\_˝}',               r'$\text{ɢ}^{\text{˝}}$'),
    # Scope/granularity (Γ) — subscript
    (r'\texttt{Γ\_ʔ}',               r'$\Gamma_{\text{ʔ}}$'),
    (r'\texttt{Γ\_β}',               r'$\Gamma_{\beta}$'),
    (r'\texttt{Γ\_γ}',               r'$\Gamma_{\gamma}$'),
    # Fidelity (ƒ) — SUPERSCRIPT
    (r'\texttt{ƒ\_ż}',               r'$\text{ƒ}^{\text{ż}}$'),
    (r'\texttt{ƒ\_ì}',               r'$\text{ƒ}^{\text{ì}}$'),
    (r'\texttt{ƒ\_ð}',               r'$\text{ƒ}^{\text{ð}}$'),
    # Dimensionality (Ð) — subscript
    (r'\texttt{Ð\_;}',               r'$\text{Ð}_{;}$'),
    (r'\texttt{Ð\_\omega}',          r'$\text{Ð}_{\omega}$'),
    (r'\texttt{Ð\_ß}',               r'$\text{Ð}_{\text{ß}}$'),
    (r'\texttt{Ð\_C}',               r'$\text{Ð}_{C}$'),
    # Stoichiometry (Σ) — subscript
    (r'\texttt{Σ\_S}',               r'$\Sigma_{S}$'),
    (r'\texttt{Σ\_ő}',               r'$\Sigma_{\text{ő}}$'),
    (r'\texttt{Σ\_ï}',               r'$\Sigma_{\text{ï}}$'),
]

# Misc: $Prim$\_subtype left over from pandoc math+text mixing
MISC_FIXES = [
    (r'$\Phi$\_\}',  r'$\Phi_{\}}$'),
    (r'$\Phi$\_A',   r'$\Phi_{A}$'),
    (r'$\Phi$\_B',   r'$\Phi_{B}$'),
    (r'$\odot$\_A',  r'$\odot_{A}$'),
    (r'$\odot$\_B',  r'$\odot_{B}$'),
    (r'$\odot$\_Æ',  r'$\odot_{\text{Æ}}$'),
    (r'$\odot$\_ÿ',  r'$\odot_{\text{ÿ}}$'),
]

# phi+combining circumflex in any tex context → $\odot$
PHI_COMBINING_TEX = [
    ('$\\phi$' + chr(0x0302), '$\\odot$'),
    ('\\phi'   + chr(0x0302), '$\\odot$'),
    (PHI_HAT,                 '$\\odot$'),
]

# Primitive glyph → (LaTeX math command, sub/sup indicator)
# sub = uses subscript (_), sup = uses superscript (^) per SYMBOL_REFERENCE.md
PRIM_MATH = {
    'Ð': (r'\text{Ð}',  'sub'),
    'Þ': (r'\text{Þ}',  'sub'),
    'Ř': (r'\text{Ř}',  'sub'),
    'Φ': (r'\Phi',       'sub'),
    'ƒ': (r'\text{ƒ}',  'sup'),
    'Ç': (r'\text{Ç}',  'sup'),
    'Γ': (r'\Gamma',     'sub'),
    'ɢ': (r'\text{ɢ}',  'sup'),
    '⊙': (r'\odot',      'sub'),
    'Ħ': (r'\text{Ħ}',  'sub'),
    'Σ': (r'\Sigma',     'sub'),
    'Ω': (r'\Omega',     'sub'),
}

_PRIM_CHARS = ''.join(PRIM_MATH.keys())


def subtype_to_math(sub: str) -> str:
    """Render a raw subtype token into its LaTeX math representation."""
    if sub.startswith('\\'):        # already a LaTeX command
        return sub
    if sub == '^':                  # bare caret → logical AND
        return r'\wedge'
    if sub == '}':
        return r'\}'
    if sub == 'ω': return r'\omega'
    if sub == 'β': return r'\beta'
    if sub == 'γ': return r'\gamma'
    if sub == 'λ': return r'\lambda'
    # single ASCII safe to use directly
    if len(sub) == 1 and sub.isascii() and sub not in r'\{}$&%#_^~':
        return sub
    return r'\text{' + sub + '}'


def convert_tuple_element(prim: str, raw_sub: str) -> str:
    """Convert a single Prim_sub element to proper math notation."""
    if prim not in PRIM_MATH:
        return prim + r'\_' + raw_sub  # unknown, leave alone
    math_cmd, pos = PRIM_MATH[prim]
    # Normalize raw_sub: \^{} → ^, \} → }
    sub = raw_sub
    if sub == r'\^{}': sub = '^'
    if sub == r'\}':   sub = '}'
    sub_math = subtype_to_math(sub)
    sep = '^' if pos == 'sup' else '_'
    return math_cmd + sep + '{' + sub_math + '}'


def _fix_tuple_line(line: str) -> str:
    r"""
    Convert a tuple line of the form:
      $\langle$P1\_s1; P2\_s2; ...$\rangle$
    to:
      $\langle P1_{s1};\, P2_{s2};\, ... \rangle$
    Only acts if the content contains \_ (visible underscores).
    """
    m = re.match(r'^(.*?)\$\\langle\$(.*?)\$\\rangle\$(.*)$', line)
    if not m or r'\_' not in m.group(2):
        return line
    prefix, content, suffix = m.group(1), m.group(2), m.group(3)

    converted = []
    for elem in [e.strip() for e in content.split('; ')]:
        # Pattern 1: Prim\_subtype (bare Unicode prim)
        pm = re.match(r'^([' + re.escape(_PRIM_CHARS) + r'])\\_(.+)$', elem)
        if pm:
            converted.append(convert_tuple_element(pm.group(1), pm.group(2)))
            continue
        # Pattern 2: $\odot$\_subtype (odot in math mode with text subscript)
        pm2 = re.match(r'^\$\\odot\$\\_(.+)$', elem)
        if pm2:
            converted.append(convert_tuple_element('⊙', pm2.group(1)))
            continue
        converted.append(elem)

    return prefix + r'$\langle ' + r';\, '.join(converted) + r' \rangle$' + suffix


def normalize_tex_math(text: str) -> str:
    """Normalize primitive notation in non-igprimfont LaTeX documents."""
    # 1. Fix phi+combining circumflex variants
    for old, new in PHI_COMBINING_TEX:
        text = text.replace(old, new)

    # 2. Fix \texttt{Prim\_subtype} → $math_form$
    for old, new in TEXTTT_FIXES:
        text = text.replace(old, new)

    # 3. Fix $Prim$\_subtype hybrid patterns
    for old, new in MISC_FIXES:
        text = text.replace(old, new)

    # 4. Fix $\langle$...$\rangle$ tuple lines with visible underscores
    # Only outside lstlisting environments
    lines = text.split('\n')
    in_lst = False
    out = []
    for line in lines:
        if r'\begin{lstlisting}' in line:
            in_lst = True
        if r'\end{lstlisting}' in line:
            in_lst = False
        if not in_lst and r'$\langle$' in line and r'\_' in line:
            line = _fix_tuple_line(line)
        out.append(line)
    return '\n'.join(out)


# ── igprimfont manuscript normalization — delegate to fix_ig_glyphs.py ───────

def _load_fix_ig_glyphs():
    import importlib.util
    script = Path(__file__).with_name('fix_ig_glyphs.py')
    spec = importlib.util.spec_from_file_location('fix_ig_glyphs', script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_tex_igprimfont(text: str, path: Path) -> str:
    mod = _load_fix_ig_glyphs()
    text = mod.process(text)
    if 'SO_BELOW' in path.name or path.name.startswith('SB'):
        text = mod.process_macros(text)
    # Catch ASCII surrogates left inside \text{{\igprimfont X}}
    text = fix_igprimfont_wrong_ascii(text)
    return text


# ── Entry point ───────────────────────────────────────────────────────────────

def normalize_file(path: Path) -> bool:
    """Normalize path in-place. Returns True if the file was changed."""
    original = path.read_text(encoding='utf-8')

    suffix = path.suffix.lower()
    if suffix == '.md':
        fixed = normalize_md(original)
    elif suffix == '.tex':
        if r'\igprimfont' in original or r'\igprim{' in original:
            fixed = normalize_tex_igprimfont(original, path)
        else:
            fixed = normalize_tex_math(original)
    else:
        return False

    if fixed != original:
        path.write_text(fixed, encoding='utf-8')
        return True
    return False


def staged_files() -> list[Path]:
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True, text=True
    )
    root = Path(subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        capture_output=True, text=True
    ).stdout.strip())
    paths = []
    for rel in result.stdout.splitlines():
        if rel.endswith('.md') or rel.endswith('.tex'):
            p = root / rel
            if p.exists():
                paths.append(p)
    return paths


if __name__ == '__main__':
    args = sys.argv[1:]
    check_only = '--check' in args
    use_staged = '--staged' in args
    paths_args = [a for a in args if not a.startswith('--')]

    if use_staged:
        files = staged_files()
    elif paths_args:
        files = [Path(p) for p in paths_args]
    else:
        print(__doc__)
        sys.exit(0)

    any_changed = False
    for p in files:
        changed = normalize_file(p) if not check_only else False
        if check_only:
            original = p.read_text(encoding='utf-8')
            suffix = p.suffix.lower()
            if suffix == '.md':
                fixed = normalize_md(original)
            elif suffix == '.tex':
                if r'\igprimfont' in original:
                    fixed = normalize_tex_igprimfont(original, p)
                else:
                    fixed = normalize_tex_math(original)
            else:
                continue
            changed = fixed != original

        if changed:
            any_changed = True
            if check_only:
                print(f'NEEDS FIX: {p}')
            else:
                # Re-stage if called from pre-commit hook context
                print(f'Fixed: {p}')
        else:
            print(f'Clean: {p}')

    sys.exit(1 if (check_only and any_changed) else 0)
