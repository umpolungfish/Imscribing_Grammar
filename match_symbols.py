#!/usr/bin/env python3
"""Assign new phonetic symbols to Imscribing Grammar primitives."""
import re

with open("psymbols.txt", "r", encoding="utf-8") as f:
    raw = f.read()

symbol_map = {}
for m in re.finditer(r'(\S)\s+\\(text[a-zA-Z]+)', raw):
    char = m.group(1)
    name = m.group(2)
    short = name[4:]
    if short not in symbol_map:
        symbol_map[short] = (char, name)

primitives = {
    'D': ['wedge', 'triangle', 'infty', 'odot'],
    'T': ['network', 'in', 'bowtie', 'boxtimes', 'odot'],
    'R': ['super', 'cat', 'dagger', 'lr'],
    'P': ['asym', 'psi', 'pm', 'sym', 'pm_sym'],
    'F': ['ell', 'eth', 'hbar'],
    'K': ['fast', 'mod', 'slow', 'trap', 'MBL'],
    'G': ['beth', 'gimel', 'aleph'],
    'Gamma': ['and', 'or', 'seq', 'broad'],
    'Phi': ['sub', 'c', 'c_complex', 'EP', 'super'],
    'H': ['0', '1', '2', 'inf'],
    'S': ['Σ_doublebaresh', 'Σ_ctn', 'Σ_ltailm'],
    'Omega': ['0', 'Z2', 'Z', 'NA']
}

def find_best(subtype_name, limit=5):
    target = subtype_name.lower()
    candidates = []
    for short, (char, full) in symbol_map.items():
        sym = short.lower()
        # prefix match: target starts with sym or vice versa
        pref_score = 0
        for l in range(min(len(target), len(sym)), 0, -1):
            if target[:l] == sym[:l]:
                pref_score = l * 100
                break
        if pref_score:
            candidates.append((pref_score, short, char, full, 'prefix'))
            continue
        # target prefix contained in symbol name
        for l in range(min(len(target), len(sym)), 1, -1):
            if target[:l] in sym:
                candidates.append((l*50, short, char, full, 'contained'))
                break
        else:
            # symbol prefix in target
            for l in range(min(len(target), len(sym)), 1, -1):
                if sym[:l] in target:
                    candidates.append((l*30, short, char, full, 'reverse'))
                    break
    candidates.sort(reverse=True)
    return candidates[:limit]

for prim, subtypes in sorted(primitives.items()):
    print(f"\n{'='*60}")
    print(f"  {prim}")
    print(f"{'='*60}")
    for sub in subtypes:
        print(f"\n  {prim}_{sub}")
        matches = find_best(sub)
        if matches:
            for score, short, char, full, kind in matches:
                print(f"    \\text{short:20s} '{char}' ({kind}, score={score})")
        else:
            print(f"    (no match)")
