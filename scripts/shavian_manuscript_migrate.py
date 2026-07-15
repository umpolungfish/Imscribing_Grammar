#!/usr/bin/env python3
"""Migrate old-notation LaTeX primitive values to Shavian v0.6.0 in manuscript files."""
import re
import sys

REPLACEMENTS = [
    # Ð (Dimensionality)
    (r'\text{{\igprimfont Ð}}_{\omega}', r'{\igfont 𐑦}'),
    (r'\text{{\igprimfont Ð}}_{;}', r'{\igfont 𐑼}'),
    (r'\text{{\igprimfont Ð}}_{C}', r'{\igfont 𐑨}'),
    (r'\text{{\igprimfont Ð}}_{\text{{\igfont ß}}}', r'{\igfont 𐑛}'),
    # Þ (Topology)
    (r'\text{{\igprimfont Þ}}_{O}', r'{\igfont 𐑸}'),
    (r'\text{{\igprimfont Þ}}_{K}', r'{\igfont 𐑶}'),
    (r'\text{{\igprimfont Þ}}_{\text{{\igfont ¨}}}', r'{\igfont 𐑶}'),
    (r'\text{{\igprimfont Þ}}_{\text{{\igfont Ý}}}', r'{\igfont 𐑥}'),
    (r'\text{{\igprimfont Þ}}_{\text{{\igfont œ}}}', r'{\igfont 𐑰}'),
    (r'\text{{\igprimfont Þ}}_{\in}', r'{\igfont 𐑰}'),
    (r'\text{{\igprimfont Þ}}_{\bowtie}', r'{\igfont 𐑕}'),
    (r'\text{{\igprimfont Þ}}_{\square}', r'{\igfont 𐑡}'),
    # Ř (Relational)
    (r'\text{{\igprimfont Ř}}_{\text{{\igfont ¯}}}', r'{\igfont 𐑩}'),
    (r'\text{{\igprimfont Ř}}_{\text{{\igfont ý}}}', r'{\igfont 𐑑}'),
    (r'\text{{\igprimfont Ř}}_{\text{{\igfont Ť}}}', r'{\igfont 𐑽}'),
    (r'\text{{\igprimfont Ř}}_{=}', r'{\igfont 𐑾}'),
    (r'\text{{\igprimfont Ř}}_{\dagger}', r'{\igfont 𐑽}'),
    (r'\text{{\igprimfont Ř}}_{\leftrightarrow}', r'{\igfont 𐑾}'),
    # Φ (Polarity)
    (r'\text{{\igprimfont Φ}}_{\text{{\igprimfont ɐ}}}', r'{\igfont 𐑗}'),
    (r'\text{{\igprimfont Φ}}_{\text{{\igfont ˙}}}', r'{\igfont 𐑯}'),
    (r'\text{{\igprimfont Φ}}_{\}}', r'{\igfont 𐑹}'),
    (r'\text{{\igprimfont Φ}}_{+}', r'{\igfont 𐑗}'),
    (r'\text{{\igprimfont Φ}}_{\text{{\igfont ·}}}', r'{\igfont 𐑯}'),
    # ⊙ (Criticality) — ⊙: remove subscript, keep ⊙; others get Shavian
    (r'\text{{\igprimfont ⊙}}_{\text{{\igfont ÿ}}}', r'\text{{\igprimfont ⊙}}'),
    (r'\text{{\igprimfont ⊙}}_{\text{{\igfont Æ}}}', r'{\igfont 𐑮}'),
    (r'\text{{\igprimfont ⊙}}_{\text{{\igfont ž}}}', r'{\igfont 𐑢}'),
    (r'\text{{\igprimfont ⊙}}_{\text{{\igfont Ţ}}}', r'{\igfont 𐑻}'),
    (r'\text{{\igprimfont ⊙}}_{3}', r'{\igfont 𐑣}'),
    # Ω (Protection)
    (r'\text{{\igprimfont Ω}}_{\text{{\igfont Å}}}', r'{\igfont 𐑷}'),
    (r'\Omega_{\text{{\igfont Å}}}', r'{\igfont 𐑷}'),
    (r'\text{{\igprimfont Ω}}_{2}', r'{\igfont 𐑴}'),
    (r'\text{{\igprimfont Ω}}_{z}', r'{\igfont 𐑭}'),
    (r'\text{{\igprimfont Ω}}_{5}', r'{\igfont 𐑟}'),
    (r'\text{{\igprimfont Ω}}_{Z}', r'{\igfont 𐑭}'),
    (r'\text{{\igprimfont Ω}}_{Z_2}', r'{\igfont 𐑴}'),
    # Ħ (Chirality)
    (r'\text{{\igprimfont Ħ}}_0', r'{\igfont 𐑓}'),
    (r'\text{{\igprimfont Ħ}}_1', r'{\igfont 𐑒}'),
    (r'\text{{\igprimfont Ħ}}_2', r'{\igfont 𐑖}'),
    (r'\text{{\igprimfont Ħ}}_{!}', r'{\igfont 𐑫}'),
    (r'\text{{\igprimfont Ħ}}_3', r'{\igfont 𐑖}'),
    # Γ (Granularity)
    (r'\text{{\igprimfont Γ}}_{\beta}', r'{\igfont 𐑚}'),
    (r'\text{{\igprimfont Γ}}_{\gamma}', r'{\igfont 𐑔}'),
    (r'\text{{\igprimfont Γ}}_{\text{{\igprimfont ʔ}}}', r'{\igfont 𐑲}'),
    (r'\text{{\igprimfont Γ}}_{\wedge}', r'{\igfont 𐑚}'),
    (r'\text{{\igprimfont Γ}}_{\vee}', r'{\igfont 𐑔}'),
    # ɢ (Grammar)
    (r'\text{{\igprimfont ɢ}}_{\wedge}', r'{\igfont 𐑝}'),
    (r'\text{{\igprimfont ɢ}}_{\text{{\igprimfont ˝}}}', r'{\igfont 𐑜}'),
    (r'\text{{\igprimfont ɢ}}_{\text{{\igprimfont ˌ}}}', r'{\igfont 𐑠}'),
    (r'\text{{\igprimfont ɢ}}_{\text{{\igfont Ş}}}', r'{\igfont 𐑵}'),
    (r'\text{{\igprimfont ɢ}}_{\vee}', r'{\igfont 𐑜}'),
    (r'\text{{\igprimfont ɢ}}_{|}', r'{\igfont 𐑠}'),
    # ƒ (Fidelity)
    (r'\text{{\igprimfont ƒ}}_{\text{{\igfont ì}}}', r'{\igfont 𐑱}'),
    (r'\text{{\igprimfont ƒ}}_{\text{{\igfont ð}}}', r'{\igfont 𐑞}'),
    (r'\text{{\igprimfont ƒ}}_{\text{{\igfont ż}}}', r'{\igfont 𐑐}'),
    (r'\text{{\igprimfont ƒ}}_{\hbar}', r'{\igfont 𐑱}'),
    (r'\text{{\igprimfont ƒ}}_{\eth}', r'{\igfont 𐑞}'),
    (r'\text{{\igprimfont ƒ}}_{0}', r'{\igfont 𐑐}'),
    # Ç (Kinetic character)
    (r'\text{{\igprimfont Ç}}_{-}', r'{\igfont 𐑘}'),
    (r'\text{{\igprimfont Ç}}_{W}', r'{\igfont 𐑤}'),
    (r'\text{{\igprimfont Ç}}_{@}', r'{\igfont 𐑧}'),
    (r'\text{{\igprimfont Ç}}_{\text{{\igfont Ù}}}', r'{\igfont 𐑪}'),
    (r'\text{{\igprimfont Ç}}_{\lambda}', r'{\igfont 𐑺}'),
    (r'\text{{\igprimfont Ç}}_{trap}', r'{\igfont 𐑘}'),
    (r'\text{{\igprimfont Ç}}_{slow}', r'{\igfont 𐑤}'),
    # Σ (Stoichiometry)
    (r'\text{{\igprimfont Σ}}_{n}', r'{\igfont 𐑕}'),
    (r'\text{{\igprimfont Σ}}_{m}', r'{\igfont 𐑳}'),
    (r'\text{{\igprimfont Σ}}_{1}', r'{\igfont 𐑕}'),
    (r'\text{{\igprimfont Σ}}_{2}', r'{\igfont 𐑳}'),
]

# Regex-based: \text{{\igprimfont Ħ}}_(\d) for any digit
CHIRALITY_DIGIT_MAP = {'0': '𐑓', '1': '𐑒', '2': '𐑖', '3': '𐑖'}
CHIRALITY_PAT = re.compile(r'\\text\{\{\\igprimfont Ħ\}\}_(\d)')

def migrate_text(text: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        occurrences = text.count(old)
        if occurrences:
            text = text.replace(old, new)
            count += occurrences

    def chirality_sub(m):
        digit = m.group(1)
        shavian = CHIRALITY_DIGIT_MAP.get(digit, '𐑒')
        return f'{{\\igfont {shavian}}}'

    new_text, n = CHIRALITY_PAT.subn(chirality_sub, text)
    return new_text, count + n


def migrate_file(path: str) -> int:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    migrated, total = migrate_text(original)
    if total == 0:
        print(f"{path}: 0 replacements — already migrated or no patterns found")
        return 0
    with open(path, 'w', encoding='utf-8') as f:
        f.write(migrated)
    print(f"{path}: {total} replacements applied")
    remaining = sum(1 for line in migrated.splitlines()
                    if r'\text{{\igprimfont' in line and r'}}_' in line
                    and r'\text{{\igprimfont ⊙}}' not in line)
    if remaining:
        print(f"  WARNING: {remaining} lines may still contain un-migrated patterns")
        for i, line in enumerate(migrated.splitlines(), 1):
            if r'\text{{\igprimfont' in line and r'}}_' in line and r'\text{{\igprimfont ⊙}}' not in line:
                print(f"    L{i}: {line.strip()[:120]}")
    return total


if __name__ == '__main__':
    files = sys.argv[1:] if len(sys.argv) > 1 else [
        '/home/mrnob0dy666/imscribing_grammar/manuscripts/AS_ABOVE.tex',
        '/home/mrnob0dy666/imscribing_grammar/manuscripts/SO_BELOW.tex',
    ]
    for path in files:
        migrate_file(path)
