#!/usr/bin/env python3
"""Patch IG_inquiry.py: _shavian_to_display → identity (surgical)."""
from pathlib import Path

p = Path("/home/mrnob0dy666/imscribing_grammar/IG_inquiry.py")
bak = p.with_suffix(".py.bak3")
orig = p.read_text(encoding="utf-8")
bak.write_text(orig, encoding="utf-8")
print(f"Backup: {bak}")

lines = orig.split('\n')
changes = 0

# ── 1. _shavian_to_display: replace dict body with `return val` ──
# Find the function
for i, l in enumerate(lines):
    if 'def _shavian_to_display(val: str, prim: str) -> str:' in l:
        # Find start of _SHAVIAN_TO_DISPLAY = {
        dict_start = None
        doc_end = None
        for j in range(i+1, min(i+20, len(lines))):
            if '_SHAVIAN_TO_DISPLAY = {' in lines[j]:
                dict_start = j
            # End of docstring (triple quote)
            if '"""' in lines[j] and doc_end is None:
                if '"""' in lines[j] and lines[j].strip() == '"""':
                    doc_end = j
                elif '"""' in lines[j].strip():  # may have """ on same line
                    doc_end = j
        
        # Replace from dict_start to the closing brace of the dict
        if dict_start:
            # Find closing '}' of the dict
            brace_depth = 1
            dict_end = dict_start
            for j in range(dict_start + 1, len(lines)):
                dict_end = j
                brace_depth += lines[j].count('{') - lines[j].count('}')
                if brace_depth <= 0:
                    break
            
            # Replace all lines from dict_start to dict_end with just '        return val'
            indent = '        '
            replacement = [indent + 'return val']
            lines[dict_start:dict_end+1] = replacement
            changes += 1
            print(f"  _shavian_to_display: replaced dict body (lines {dict_start+1}–{dict_end+1})")
        
        # Also update the docstring text
        for j in range(i+1, dict_start or i+10):
            lines[j] = lines[j].replace('to display notation', 'as Shavian glyphs (identity)')
            lines[j] = lines[j].replace('human-readable display', 'Shavian Unicode (identity)')
        break

# ── 2. _classify_frobenius: update comparison strings ──
for i, l in enumerate(lines):
    if 'def _classify_frobenius(self, s: Dict[str, Any]) -> str:' in l:
        # Find function body after docstring
        body_start = None
        for j in range(i+1, min(i+25, len(lines))):
            if '"""' in lines[j] and body_start is None:
                # end of docstring
                pass
            if body_start is None and lines[j].strip().endswith('"""'):
                body_start = j + 1
                break
            if body_start is None and '"""' in lines[j].strip() and lines[j-1].strip().endswith('"""'):
                body_start = j + 1
                break
        
        if body_start:
            # Update lines in the function body
            replacements = {
                '"φ̂_ÿ"': '"⊙"',
                '"φ̂_Æ"': '"𐑮"',
                '"𐑹"': '"𐑹"',
                '"φ̂_ž"': '"𐑢"',
                '"φ̂_Ţ"': '"𐑣"',
                '"φ̂_3"': '"𐑻"',
                '"𐑷"': '"𐑷"',
                '"𐑛"': '"𐑛"',
                '"𐑦"': '"𐑦"',
                '"𐑨"': '"𐑨"',
                '"𐑼"': '"𐑼"',
            }
            # Find end of function (next def at same indentation, or _FROBENIUS_DESCRIPTIONS)
            func_end = body_start
            for j in range(body_start, min(body_start+100, len(lines))):
                if lines[j].startswith('def ') or (j > body_start and lines[j].startswith('    def ')):
                    func_end = j
                    break
                if lines[j].startswith('_FROBENIUS_DESCRIPTIONS'):
                    func_end = j
                    break
            
            for j in range(body_start, func_end):
                old = lines[j]
                n = old
                for disp, shav in replacements.items():
                    n = n.replace(disp, shav)
                n = n.replace('display notation', 'Shavian glyphs')
                if n != old:
                    lines[j] = n
                    changes += 1
            
            print(f"  _classify_frobenius: {changes} replacements in function body")
        break

# ── 3. Update _FROBENIUS_DESCRIPTIONS ──
for i, l in enumerate(lines):
    if '_FROBENIUS_DESCRIPTIONS = {' in l:
        for j in range(i, min(i+15, len(lines))):
            old = lines[j]
            n = old.replace('(𐑼)', '(𐑼)')
            if n != old:
                lines[j] = n
                changes += 1
                print(f"  _FROBENIUS_DESCRIPTIONS: [{j+1}] updated")
        break

# ── Write ──
result = '\n'.join(lines)
p.write_text(result, encoding="utf-8")
shav = sum(1 for c in result if 0x10450 <= ord(c) <= 0x1047F)
print(f"\nWritten: {p}")
print(f"Shavian glyphs: {shav}")
print(f"Changes: {changes}")
wc = len(result.split('\n'))
print(f"Lines: {wc}")
