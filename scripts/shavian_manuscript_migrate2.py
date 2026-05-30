#!/usr/bin/env python3
"""Second-pass Shavian migration: fix wrong Þ_K→𐑶 substitutions, add missing patterns, update SO_BELOW macros."""
import sys

AS_ABOVE = '/home/mrnob0dy666/imscribing_grammar/manuscripts/AS_ABOVE.tex'
SO_BELOW = '/home/mrnob0dy666/imscribing_grammar/manuscripts/SO_BELOW.tex'

# ============================================================
# TARGETED FIXES — AS_ABOVE only
# Þ_K (T_bowl) was wrongly mapped to 𐑶 (T_cage); correct is 𐑰.
# Use enough context to uniquely identify each wrong occurrence.
# ============================================================
AS_ABOVE_TARGETED = [
    # L1024: table row with all 5 Þ values (· separator)
    (
        r'\cdot {\igfont 𐑶} \cdot \text{{\igprimfont Þ}}_{\text{{\igfont ò}}} \cdot {\igfont 𐑶} \cdot {\igfont 𐑸}',
        r'\cdot {\igfont 𐑰} \cdot \text{{\igprimfont Þ}}_{\text{{\igfont ò}}} \cdot {\igfont 𐑶} \cdot {\igfont 𐑸}',
    ),
    # L1485: "exactly 5 values" list (comma separator)
    (
        r'_{6}$, ${\igfont 𐑶}$, $\text{{\igprimfont Þ}}_{\text{{\igfont ò}}}$, ${\igfont 𐑶}$, ${\igfont 𐑸}$',
        r'_{6}$, ${\igfont 𐑰}$, $\text{{\igprimfont Þ}}_{\text{{\igfont ò}}}$, ${\igfont 𐑶}$, ${\igfont 𐑸}$',
    ),
    # L1695: tikz node with \\ separator
    (
        '_{6}$\\\\${\igfont 𐑶}$\\\\$\\text{{\\igprimfont Þ}}_{{\\text{{\\igfont ò}}}}$\\\\${\\igfont 𐑶}$',
        '_{6}$\\\\${\igfont 𐑰}$\\\\$\\text{{\\igprimfont Þ}}_{{\\text{{\\igfont ò}}}}$\\\\${\\igfont 𐑶}$',
    ),
    # L1366: "simultaneously injective" (𐑶 here is Þ_K = T_bowl, not T_cage)
    (
        'simultaneously injective (${\igfont 𐑶}$)',
        'simultaneously injective (${\igfont 𐑰}$)',
    ),
]

# ============================================================
# GENERAL MISSING PATTERNS — apply to BOTH files
# ============================================================
MISSING = [
    # Þ (Topology) — missing values
    (r'\text{{\igprimfont Þ}}_{6}',               r'{\igfont 𐑡}'),   # T_nrleg
    (r'\text{{\igprimfont Þ}}_{\text{{\igfont ò}}}', r'{\igfont 𐑥}'),  # T_bullseye
    (r'\text{{\igprimfont Þ}}_O',                  r'{\igfont 𐑸}'),   # T_holo, bare subscript

    # Φ (Polarity) — missing values
    (r'\text{{\igprimfont Φ}}_{\upsilon}',         r'{\igfont 𐑿}'),   # P_plus / P_psi
    (r'\text{{\igprimfont Φ}}_{F}',               r'{\igfont 𐑬}'),   # P_pipevar / P_pm

    # Ħ (Chirality) — actual notation uses £ and A, not digit subscripts
    (r'\text{{\igprimfont Ħ}}_{\text{{\igfont £}}}', r'{\igfont 𐑒}'),  # H1 = toneletterstem
    (r'\text{{\igprimfont Ħ}}_{A}',               r'{\igfont 𐑖}'),   # H2 = turntwo
    (r'\text{{\igprimfont Ħ}}_!',                 r'{\igfont 𐑫}'),   # H_inf, bare subscript
    (r'\text{{\igprimfont Ħ}}_{!}',               r'{\igfont 𐑫}'),   # H_inf, with braces (deduplicate)

    # Σ (Stoichiometry) — all three values
    (r'\text{{\igprimfont Σ}}_{S}',               r'{\igfont 𐑙}'),   # one:one = S_doublebaresh
    (r'\text{{\igprimfont Σ}}_{\text{{\igfont ő}}}', r'{\igfont 𐑕}'),  # one:n = S_ctn
    (r'\text{{\igprimfont Σ}}_{\text{{\igfont ï}}}', r'{\igfont 𐑳}'),  # n:m = S_ltailm

    # ɢ (Grammar) — sequential in various notation forms
    (r'\text{{\igprimfont ɢ}}_{\to}',             r'{\igfont 𐑠}'),   # G_seq, arrow subscript
    (r'\text{{\igprimfont ɢ}}_{\gg}',             r'{\igfont 𐑵}'),   # G_broad, double-arrow
    (r'\text{{\igprimfont ɢ}}_{\text{seq}}',      r'{\igfont 𐑠}'),   # G_seq, text subscript

    # Ω (Protection) — varnothing variant = Omega_0 = "not applicable"
    (r'\text{{\igprimfont Ω}}_{\varnothing}',     r'{\igfont 𐑷}'),   # Omega_0 / NA

    # Bare subscript variants (no curly braces around subscript)
    (r'\text{{\igprimfont Ð}}_\omega',            r'{\igfont 𐑦}'),   # D_odot, bare
    (r'\text{{\igprimfont Ç}}_W',                 r'{\igfont 𐑤}'),   # K_mod, bare
    (r'\text{{\igprimfont Ω}}_z',                 r'{\igfont 𐑭}'),   # Omega_Z, bare
    (r'\text{{\igprimfont Ç}}_{\text{{\igfont @}}}', r'{\igfont 𐑧}'), # K_slow, font-wrapped @
]

# ============================================================
# SO_BELOW MACRO DEFINITIONS — update 6 macros in preamble
# ============================================================
SO_BELOW_MACROS = [
    # \Phic: remove old-notation subscript from sealed gate
    (
        r'\newcommand{\Phic}{\mathord{\text{{\igprimfont ⊙}}}_{\text{{\igfont ÿ}}}}',
        r'\newcommand{\Phic}{\mathord{\text{{\igprimfont ⊙}}}}',
    ),
    # \Ppm: P_pipevar (Φ_F) → 𐑬
    (
        r'\newcommand{\Ppm}{{\text{{\igprimfont Φ}}_{F}}}',
        r'\newcommand{\Ppm}{{\igfont 𐑬}}',
    ),
    # \GamSeq: G_seq → 𐑠
    (
        r'\newcommand{\GamSeq}{\text{{\igprimfont ɢ}}_{\to}}',
        r'\newcommand{\GamSeq}{{\igfont 𐑠}}',
    ),
    # \Tbw: T_bullseye (bowtie) → 𐑥
    (
        r'\newcommand{\Tbw}{\text{{\igprimfont Þ}}_{{\mathord{{\bowtie}}}}}',
        r'\newcommand{\Tbw}{{\igfont 𐑥}}',
    ),
    # \Tin: T_bowl (∈ / subset) → 𐑰
    (
        r'\newcommand{\Tin}{\text{{\igprimfont Þ}}_{{\mathord{{\subset}}}}}',
        r'\newcommand{\Tin}{{\igfont 𐑰}}',
    ),
    # \Tbox: T_cage (boxtimes) → 𐑶
    (
        r'\newcommand{\Tbox}{\text{{\igprimfont Þ}}_{{\mathord{{\boxtimes}}}}}',
        r'\newcommand{\Tbox}{{\igfont 𐑶}}',
    ),
]


def apply_replacements(text, pairs, label):
    count = 0
    for old, new in pairs:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            count += n
            print(f"  {label}: {n}× {repr(old[:50])} → {repr(new[:30])}")
    return text, count


def migrate_file(path, targeted=None, general=None, macros=None):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    total = 0

    if targeted:
        text, n = apply_replacements(text, targeted, 'targeted-fix')
        total += n

    if macros:
        text, n = apply_replacements(text, macros, 'macro-def')
        total += n

    if general:
        text, n = apply_replacements(text, general, 'general')
        total += n

    if total == 0:
        print(f"{path}: 0 changes")
        return

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"{path}: {total} total replacements")

    remaining = sum(
        1 for line in text.splitlines()
        if r'\text{{\igprimfont' in line and r'}}_' in line
        and r'\text{{\igprimfont ⊙}}' not in line
        and r'\text{{\igprimfont' + ' ' not in line.split(r'\text{{\igprimfont')[1][:3]
    )
    # Simple check: lines with }}_{ that aren't just bare primitive labels
    flagged = []
    for i, line in enumerate(text.splitlines(), 1):
        if r'\text{{\igprimfont' in line:
            parts = line.split(r'\text{{\igprimfont')
            for part in parts[1:]:
                # Check if there's a subscript after the closing }}
                after = part[part.find('}}')+2:] if '}}' in part else ''
                if after.startswith('_') and not after.startswith('_\n'):
                    # Skip positional indices (pure digits like _1, _2 ... _12) and variable _n
                    subscript = after[1:].lstrip('{').rstrip('}').split('}')[0].split(';')[0][:20]
                    if not subscript.isdigit() and subscript not in ('n', 'm', 'k', 'i', 'j',
                                                                      'alpha', 'mathcal', 'cdot'):
                        flagged.append((i, line.strip()[:100]))
                        break
    if flagged:
        print(f"  {len(flagged)} lines may still have unmigrated value patterns:")
        for lineno, content in flagged[:20]:
            print(f"    L{lineno}: {content}")


if __name__ == '__main__':
    print("=== AS_ABOVE.tex ===")
    migrate_file(AS_ABOVE, targeted=AS_ABOVE_TARGETED, general=MISSING)

    print("\n=== SO_BELOW.tex ===")
    migrate_file(SO_BELOW, general=MISSING, macros=SO_BELOW_MACROS)
