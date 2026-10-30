#!/usr/bin/env python3
"""Verify symbol availability and produce final clean assignment table."""
import re

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Build full map
symbol_map = {}
for m in re.finditer(r'(\S)\s+\\(text[a-zA-Z]+)', raw):
    char = m.group(1)
    name = m.group(2)
    short = name[4:]
    if short not in symbol_map:
        symbol_map[short] = (char, name)

# Check specific symbols
needed = ['wynn', 'turnthree', 'invscripta', 'omega', 'nrleg', 'invomega',
          'bullseye', 'commatailz', 'openo', 'subrightarrow', 'ctz', 'downstep',
          'lyoghlig', 'aolig', 'upsilon', 'pipevar', 'subdoublearrow', 'doublebarpipe',
          'beltl', 'hvlig', 'frtailgamma', 'turnm', 'schwa', 'teshlig', 'lambda',
          'beta', 'gamma', 'revapostrophe', 'corner', 'secstress',
          # More needed for remaining primitives
          'invscr', 'doublevertline', 'spleftarrow', 'looptoprevesh',
          'longlegr', 'turnlonglegr', 'doublepipe', 'doublepipevar',
          'doublebaresh', 'softsign', 'hardsign', 'crtwo', 'turntwo',
          'dh', 'flap', 'fishhookr', 'glotstop', 'theta', 'phi',
          'closeomega', 'closeepsilon', 'revepsilon', 'rthook',
          'niomega', 'niphi', 'nisigma', 'turnmrleg',
          'closerevepsilon', 'bktailgamma', 'toneletterstem']

print("=== Symbol availability check ===")
for n in needed:
    if n in symbol_map:
        c, f = symbol_map[n]
        print(f"  OK  \\text{n:25s} '{c}'")
    else:
        # Try partial match
        found = [k for k in symbol_map.keys() if n in k]
        if found:
            print(f"  PART \\text{n:25s} → {found[:2]}")
        else:
            print(f"  MISS \\text{n:25s}")
