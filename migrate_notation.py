#!/usr/bin/env python3
"""
Migrate IG notation project-wide to SYMBOL_REFERENCE.md standard:
  φ̂  → ⊙   (criticality primitive rename + all φ̂_X → ⊙_X)
  Ç_X → Ç^X  (kinetics: underscore → superscript)
  ƒ_X → ƒ^X  (fidelity: underscore → superscript)
  ɢ_X → ɢ^X  (interaction grammar: underscore → superscript, ^ → ∧)
"""

import os, re, sys
from pathlib import Path

ROOT = Path(__file__).parent

EXTENSIONS = {'.json', '.py', '.md', '.tex'}

# Order matters: most specific first
SUBSTITUTIONS = [
    # φ̂ values
    ('φ̂_ž', '⊙_ž'),
    ('φ̂_ÿ', '⊙_ÿ'),
    ('φ̂_Æ', '⊙_Æ'),
    ('φ̂_3', '⊙_3'),
    ('φ̂_Ţ', '⊙_Ţ'),
    ('φ̂',   '⊙'),    # bare: dict keys, display, LaTeX references
    # Ç values
    ('Ç_-', 'Ç^-'),
    ('Ç_W', 'Ç^W'),
    ('Ç_@', 'Ç^@'),
    ('Ç_Ù', 'Ç^Ù'),
    ('Ç_λ', 'Ç^λ'),
    # ƒ values
    ('ƒ_ì', 'ƒ^ì'),
    ('ƒ_ð', 'ƒ^ð'),
    ('ƒ_ż', 'ƒ^ż'),
    # ɢ values (ɢ_^ must come before any generic ɢ_ rule)
    ('ɢ_^', 'ɢ^∧'),
    ('ɢ_˝', 'ɢ^˝'),
    ('ɢ_ˌ', 'ɢ^ˌ'),
    ('ɢ_Ş', 'ɢ^Ş'),
]

SKIP = {
    'migrate_notation.py',   # this file
    'SYMBOL_REFERENCE.md',   # ground truth, already correct
}

def migrate_file(path: Path, dry_run=False) -> int:
    if path.name in SKIP:
        return 0
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return 0
    original = text
    for old, new in SUBSTITUTIONS:
        text = text.replace(old, new)
    if text == original:
        return 0
    if not dry_run:
        path.write_text(text, encoding='utf-8')
    return 1

def main():
    dry_run = '--dry-run' in sys.argv
    changed = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and path.suffix in EXTENSIONS:
            # skip hidden dirs other than .cosmology (which has content)
            parts = path.relative_to(ROOT).parts
            if any(p.startswith('.') and p != '.cosmology' for p in parts[:-1]):
                continue
            n = migrate_file(path, dry_run=dry_run)
            if n:
                changed.append(path.relative_to(ROOT))
    label = '[DRY RUN] ' if dry_run else ''
    print(f'{label}Modified {len(changed)} files:')
    for p in changed:
        print(f'  {p}')

if __name__ == '__main__':
    main()
