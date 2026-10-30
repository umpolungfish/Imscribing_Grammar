#!/usr/bin/env python3
"""
Migrate Imscribing Grammar notation from mixed-script subscripts to Shavian.
v0.5.69 → v0.6.0

Old: 𐑛, 𐑨, 𐑼, 𐑦, 𐑡, ... etc.
New: 𐑛, 𐑨, 𐑼, 𐑦, 𐑡, ... etc.

This script transforms IG_catalog.json and all Python/Lua/JS sources.
"""

import json
import os
import re
import shutil

# ── Full Old → Shavian mapping ─────────────────────────────────────
OLD_TO_SHAVIAN = {
    # D — Dimensionality (F4)
    "𐑛": "𐑛",
    "𐑨": "𐑨",
    "𐑼": "𐑼",
    "𐑦": "𐑦",
    # T — Topology (F5)
    "𐑡": "𐑡",
    "𐑰": "𐑰",
    "𐑥": "𐑥",
    "𐑶": "𐑶",
    "𐑸": "𐑸",
    # R — Relational (F4)
    "𐑩": "𐑩",
    "𐑑": "𐑑",
    "𐑽": "𐑽",
    "𐑾": "𐑾",
    # P — Polarity/Symmetry (F5)
    "𐑗": "𐑗",
    "𐑿": "𐑿",
    "𐑬": "𐑬",
    "𐑯": "𐑯",
    "𐑹": "𐑹",
    # F — Fidelity (F3)
    "ƒ^ì": "𐑱",
    "ƒ^ð": "𐑞",
    "ƒ^ż": "𐑐",
    # K — Kinetics (F5)
    "Ç^-": "𐑘",
    "Ç^W": "𐑤",
    "Ç^@": "𐑧",
    "Ç^Ù": "𐑪",
    "Ç^λ": "𐑺",
    # G — Scope (F3)
    "𐑚": "𐑚",
    "𐑔": "𐑔",
    "𐑲": "𐑲",
    # Gamma — Coupling Grammar (F4)
    "ɢ^∧": "𐑝",
    "ɢ^˝": "𐑜",
    "ɢ^ˌ": "𐑠",
    "ɢ^Ş": "𐑵",
    # Phi — Criticality (F5)
    "𐑢": "𐑢",
    "⊙": "⊙",
    "𐑮": "𐑮",
    "𐑻": "𐑻",
    "𐑣": "𐑣",
    # H — Chirality (F4)
    "𐑓": "𐑓",
    "𐑒": "𐑒",
    "𐑖": "𐑖",
    "𐑫": "𐑫",
    # S — Stoichiometry (F3)
    "𐑙": "𐑙",
    "𐑕": "𐑕",
    "𐑳": "𐑳",
    # Omega — Winding (F4)
    "𐑷": "𐑷",
    "𐑴": "𐑴",
    "𐑭": "𐑭",
    "𐑟": "𐑟",
}

# Reverse mapping
SHAVIAN_TO_OLD = {v: k for k, v in OLD_TO_SHAVIAN.items()}

# The 12 primitive keys in catalog JSON
PRIMITIVE_KEYS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]


def migrate_catalog(input_path, output_path=None):
    """Rewrite IG_catalog.json with Shavian characters."""
    if output_path is None:
        output_path = input_path

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for entry in data:
        migrated = False
        for key in PRIMITIVE_KEYS:
            if key in entry and entry[key] in OLD_TO_SHAVIAN:
                entry[key] = OLD_TO_SHAVIAN[entry[key]]
                migrated = True
        if migrated:
            count += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Catalog migration: {count}/{len(data)} entries updated → {output_path}")
    return count


def migrate_primitives_py(input_path, output_path=None):
    """Rewrite primitives.py ORDINALS dict with Shavian keys."""
    if output_path is None:
        output_path = input_path

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build old-to-new ORDINALS block as Python code
    ordinals_new = '''ORDINALS = {
    "Ð": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "Þ": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "Ř": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "Φ": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "ƒ": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "Ç": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "Γ": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "ɢ": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "Ħ": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "Σ": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "Ω": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}'''

    # Replace the ORDINALS block (from "ORDINALS = {" to the matching "}")
    # Use regex to find the block
    pattern = r'ORDINALS\s*=\s*\{.*?\n\}'
    replacement = ordinals_new
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Also replace the imscriptions dict values (old notation)
    for old_val, shavian_val in OLD_TO_SHAVIAN.items():
        # Replace string values in the imscriptions dict
        content = content.replace(f'"{old_val}"', f'"{shavian_val}"')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"primitives.py migrated → {output_path}")
    return True


def check_site_files():
    """Check website files for Shavian rendering support."""
    sites = [
        "/home/mrnob0dy666/imscribing_grammar/index/index.html",
        "/home/mrnob0dy666/personal_site/index.html",
    ]
    for path in sites:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            has_shavian_font = "Shavian" in content
            print(f"  {path}: {'has Shavian font' if has_shavian_font else 'NEEDS Shavian font'}")


def translate_tuple_str(old_tuple_str):
    """Translate a tuple string from old notation to Shavian.
    E.g. '⟨𐑦; 𐑸; 𐑾; 𐑹; 𐑐; 𐑧; 𐑲; 𐑠; ⊙; 𐑫; 𐑳; 𐑭⟩'
    →   '⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑫𐑳𐑭⟩'
    """
    result = old_tuple_str
    # Replace separators: semicolons become middot
    result = result.replace("; ", "·")
    for old, shavian in OLD_TO_SHAVIAN.items():
        result = result.replace(old, shavian)
    return result


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "all"

    if action in ("catalog", "all"):
        catalog = "/home/mrnob0dy666/imscribing_grammar/IG_catalog.json"
        if os.path.exists(catalog):
            backup = catalog + ".bak"
            if not os.path.exists(backup):
                shutil.copy2(catalog, backup)
                print(f"Backup saved: {backup}")
            migrate_catalog(catalog)
        else:
            print(f"Catalog not found: {catalog}")

    if action in ("primitives", "all"):
        py_path = "/home/mrnob0dy666/imscribing_grammar/space_search/primitives.py"
        if os.path.exists(py_path):
            migrate_primitives_py(py_path)

    if action in ("check", "all"):
        check_site_files()

    if action == "translate":
        # Test tuple translation
        test = "⟨𐑦; 𐑸; 𐑾; 𐑹; 𐑐; 𐑧; 𐑲; 𐑠; ⊙; 𐑫; 𐑳; 𐑭⟩"
        print(f"Old:   {test}")
        print(f"Shavian: {translate_tuple_str(test)}")

    print("Migration complete.")
