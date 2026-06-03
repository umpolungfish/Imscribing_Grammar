#!/usr/bin/env python3
"""
migrate_models_shavian.py — migrate models.py enum values from Symbol_symbol to Shavian.

Per shavian_notation_spec.md OLD_TO_SHAVIAN table.
Only canonical values with Shavian mappings are replaced.
Non-canonical extensions (Þ_linear, Ω_C, ƒ_noise, Γ_xor, etc.) are left unchanged.
"""
import re
import sys
from pathlib import Path

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

# Build a regex that matches any old symbol inside a Python string literal "..."
# We do a simple quoted-string replacement: "OLD" → "NEW"
# Sorted longest-first to avoid partial matches (e.g. "Ω_5" before "Ω_")
_SORTED = sorted(OLD_TO_SHAVIAN.keys(), key=len, reverse=True)

def replace_quoted(text: str) -> str:
    """Replace 'OLD' → 'NEW' inside double-quoted string literals only."""
    for old in _SORTED:
        new = OLD_TO_SHAVIAN[old]
        # Match the symbol when it appears as the complete content of a double-quoted string
        # e.g.  = "Ð_ß"   or   "Ð_ß":   or   "Ð_ß",   etc.
        text = text.replace(f'"{old}"', f'"{new}"')
    return text

def main():
    path = Path(__file__).parent.parent / "imscrbgrmr" / "models.py"
    if not path.exists():
        print(f"Not found: {path}", file=sys.stderr)
        sys.exit(1)

    original = path.read_text(encoding="utf-8")
    migrated = replace_quoted(original)

    changed = sum(1 for a, b in zip(original.splitlines(), migrated.splitlines()) if a != b)
    if migrated == original:
        print("No changes — already migrated or nothing matched.")
        return

    # Write backup
    backup = path.with_suffix(".py.pre_shavian")
    backup.write_text(original, encoding="utf-8")
    print(f"Backup written: {backup}")

    path.write_text(migrated, encoding="utf-8")
    print(f"Migrated {changed} lines in {path}")

    # Report what changed
    for i, (a, b) in enumerate(zip(original.splitlines(), migrated.splitlines()), 1):
        if a != b:
            print(f"  L{i}: {a.strip()!r}")
            print(f"     → {b.strip()!r}")

if __name__ == "__main__":
    main()
