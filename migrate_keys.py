"""
Rename all primitive KEY names from old ASCII letters to glyph family characters.

Replacements (multi-char first, then single-char):
  "Gamma"  -> "ɢ"
  "Omega"  -> "Ω"
  "Phi"    -> "φ̂"
  "D"      -> "Ð"
  "T"      -> "Þ"
  "R"      -> "Ř"
  "P"      -> "Φ"
  "F"      -> "ƒ"
  "K"      -> "Ç"
  "G"      -> "Γ"
  "H"      -> "Ħ"
  "S"      -> "Σ"
"""

import ast, sys, pathlib

FILES = [
    "space_search/primitives.py",
    "crystal_navigator.py",
    "domain_navigators.py",
    "crystal_enumeration.py",
    "zfc_navigator.py",
    "IG_inquiry.py",
    "agents/true_agentic_agent.py",
]

# (old, new) — multi-char FIRST so "Gamma" is done before "G" etc.
KEY_PAIRS = [
    # multi-char
    ("Gamma",  "ɢ"),
    ("Omega",  "Ω"),
    ("Phi",    "φ̂"),
    # single-char
    ("D",      "Ð"),
    ("T",      "Þ"),
    ("R",      "Ř"),
    ("P",      "Φ"),
    ("F",      "ƒ"),
    ("K",      "Ç"),
    ("G",      "Γ"),
    ("H",      "Ħ"),
    ("S",      "Σ"),
]

def migrate(text: str) -> str:
    for old, new in KEY_PAIRS:
        q_old = f'"{old}"'
        q_new = f'"{new}"'
        # 1. Quoted string literal: "KEY" (covers dict keys, list items, comparisons, lookups)
        text = text.replace(q_old, q_new)
        # 2. Keyword-arg / label in example strings with equals: KEY='  or KEY=
        text = text.replace(f"{old}='", f"{new}='")
        text = text.replace(f'{old}="', f'{new}="')
        # 3. Label in display strings with colon: "KEY: "
        text = text.replace(f'"{old}: ', f'"{new}: ')
        # 4. Unquoted label in repr/format strings: KEY=self. / KEY={
        text = text.replace(f"{old}={{self.", f"{new}={{self.")
        text = text.replace(f", {old}=self.", f", {new}=self.")
        text = text.replace(f"({old}=self.", f"({new}=self.")
        # 5. C_WEIGHTS/C_MAXORD style dicts with unquoted key: "KEY":
        #    (already covered by q_old)
    return text

total_changed = 0
for fname in FILES:
    p = pathlib.Path(fname)
    if not p.exists():
        print(f"SKIP (not found): {fname}")
        continue
    original = p.read_text(encoding="utf-8")
    migrated = migrate(original)
    if migrated == original:
        print(f"NO CHANGE: {fname}")
        continue
    # Verify Python syntax
    try:
        ast.parse(migrated)
    except SyntaxError as e:
        print(f"SYNTAX ERROR in {fname}: {e}")
        sys.exit(1)
    n = sum(1 for a, b in zip(original.splitlines(), migrated.splitlines()) if a != b)
    p.write_text(migrated, encoding="utf-8")
    total_changed += 1
    print(f"OK ({n} lines changed): {fname}")

print(f"\nDone. {total_changed}/{len(FILES)} files modified.")
