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
    ('φ̂_ž', '𐑢'),
    ('φ̂_ÿ', '⊙'),
    ('φ̂_Æ', '𐑮'),
    ('φ̂_3', '𐑻'),
    ('φ̂_Ţ', '𐑣'),
    ('φ̂',   '⊙'),    # bare: dict keys, display, LaTeX references
    # Ç values
    ('𐑘', 'Ç^-'),
    ('𐑤', 'Ç^W'),
    ('𐑧', 'Ç^@'),
    ('𐑪', 'Ç^Ù'),
    ('𐑺', 'Ç^λ'),
    # ƒ values
    ('𐑱', 'ƒ^ì'),
    ('𐑞', 'ƒ^ð'),
    ('𐑐', 'ƒ^ż'),
    # ɢ values (𐑝 must come before any generic ɢ_ rule)
    ('𐑝', 'ɢ^∧'),
    ('𐑜', 'ɢ^˝'),
    ('𐑠', 'ɢ^ˌ'),
    ('𐑵', 'ɢ^Ş'),
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
