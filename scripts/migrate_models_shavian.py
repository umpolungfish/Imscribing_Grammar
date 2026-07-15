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
    "𐑛": "𐑛", "𐑨": "𐑨", "𐑼": "𐑼", "𐑦": "𐑦",
    "𐑡": "𐑡", "𐑰": "𐑰", "𐑥": "𐑥", "𐑶": "𐑶", "𐑸": "𐑸",
    "𐑩": "𐑩", "𐑑": "𐑑", "𐑽": "𐑽", "𐑾": "𐑾",
    "𐑗": "𐑗", "𐑿": "𐑿", "𐑬": "𐑬", "𐑯": "𐑯", "𐑹": "𐑹",
    "ƒ^ì": "𐑱", "ƒ^ð": "𐑞", "ƒ^ż": "𐑐",
    "Ç^-": "𐑘", "Ç^W": "𐑤", "Ç^@": "𐑧", "Ç^Ù": "𐑪", "Ç^λ": "𐑺",
    "𐑚": "𐑚", "𐑔": "𐑔", "𐑲": "𐑲",
    "ɢ^∧": "𐑝", "ɢ^˝": "𐑜", "ɢ^ˌ": "𐑠", "ɢ^Ş": "𐑵",
    "𐑢": "𐑢", "⊙": "⊙", "𐑮": "𐑮", "𐑻": "𐑻", "𐑣": "𐑣",
    "𐑓": "𐑓", "𐑒": "𐑒", "𐑖": "𐑖", "𐑫": "𐑫",
    "𐑙": "𐑙", "𐑕": "𐑕", "𐑳": "𐑳",
    "𐑷": "𐑷", "𐑴": "𐑴", "𐑭": "𐑭", "𐑟": "𐑟",
}

# Build a regex that matches any old symbol inside a Python string literal "..."
# We do a simple quoted-string replacement: "OLD" → "NEW"
# Sorted longest-first to avoid partial matches (e.g. "𐑟" before "Ω_")
_SORTED = sorted(OLD_TO_SHAVIAN.keys(), key=len, reverse=True)

def replace_quoted(text: str) -> str:
    """Replace 'OLD' → 'NEW' inside double-quoted string literals only."""
    for old in _SORTED:
        new = OLD_TO_SHAVIAN[old]
        # Match the symbol when it appears as the complete content of a double-quoted string
        # e.g.  = "𐑛"   or   "𐑛":   or   "𐑛",   etc.
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
