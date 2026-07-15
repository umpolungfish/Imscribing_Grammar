#!/usr/bin/env python3
"""Patch IG_inquiry.py: _shavian_to_display → identity, update _classify_frobenius."""
from pathlib import Path

p = Path("/home/mrnob0dy666/imscribing_grammar/IG_inquiry.py")
bak = p.with_suffix(".py.bak2")
orig = p.read_text(encoding="utf-8")
bak.write_text(orig, encoding="utf-8")
print(f"Backup: {bak}")

lines = orig.split('\n')
changes = 0

# ── 1. Find _shavian_to_display and make it identity ──
for i, l in enumerate(lines):
    if 'def _shavian_to_display(val: str, prim: str) -> str:' in l:
        # Find the body and replace everything after docstring with `return val`
        body_start = None
        doc_end = None
        for j in range(i+1, min(i+20, len(lines))):
            if '"""' in lines[j] and doc_end is None:
                doc_end = j
            if doc_end and lines[j].strip() == '"""':
                body_start = j + 1
                break
            # Single-line triple-quote
            if '"""' in lines[j] and '"""' in lines[j].replace('"""', '', 1):
                doc_end = j
                body_start = j + 1
                break
        
        if body_start:
            # Find end of function (next def at indentation 0 or end of scope)
            func_end = body_start
            for j in range(body_start, min(body_start+80, len(lines))):
                if j >= body_start and (lines[j].startswith('    def ') or 
                    (lines[j].startswith('def ') and not lines[j].startswith('    def '))):
                    func_end = j
                    break
                # Also check for class-level def
                if j > body_start and lines[j].startswith('def ') and not lines[j].startswith('    def '):
                    func_end = j
                    break
            func_end = len(lines)  # fallback
            
            # Replace everything from body_start to func_end-1 with just the return
            replacement = ['        return val']
            lines[body_start:func_end] = replacement
            changes += 1
            print(f"  Patched _shavian_to_display (line {i+1})")
            break

# ── 2. Patch _classify_frobenius comparisons ──
for i, l in enumerate(lines):
    if 'def _classify_frobenius(self, s: Dict[str, Any]) -> str:' in l:
        # Find the body after docstring
        doc_end = None
        body_start = None
        for j in range(i+1, min(i+25, len(lines))):
            if '"""' in lines[j] and doc_end is None:
                doc_end = j
            if doc_end and '"""' in lines[j] and j != doc_end:
                body_start = j + 1
                break
        
        # Update comparison strings in the body
        # We replace from body_start to the end of the function
        for j in range(body_start or i+1, min(i+40, len(lines))):
            line = lines[j]
            # Skip non-functional lines and comments
            old = line
            # Update comparison strings: display → Shavian
            line = line.replace('"φ̂_ÿ"', '"⊙"')
            line = line.replace('"φ̂_Æ"', '"𐑮"')
            line = line.replace('"𐑹"', '"𐑹"')
            line = line.replace('"φ̂_ž"', '"𐑢"')
            line = line.replace('"φ̂_Ţ"', '"𐑣"')
            line = line.replace('"φ̂_3"', '"𐑻"')
            line = line.replace('"𐑷"', '"𐑷"')
            line = line.replace('"𐑛"', '"𐑛"')
            line = line.replace('"𐑦"', '"𐑦"')
            line = line.replace('"𐑨"', '"𐑨"')
            line = line.replace('"𐑼"', '"𐑼"')
            # Update docstring text
            line = line.replace('display notation', 'Shavian glyphs')
            line = line.replace('human-readable display', 'Shavian Unicode')
            if line != old:
                lines[j] = line
                changes += 1
                print(f"  [{j+1}] {old.strip()[:60]}")
        
        # Update _FROBENIUS_DESCRIPTIONS
        for j in range(i, min(i+25, len(lines))):
            if '_FROBENIUS_DESCRIPTIONS' in lines[j]:
                for k in range(j, min(j+20, len(lines))):
                    old = lines[k]
                    n = old.replace('(𐑼)', '(𐑼)')
                    if n != old:
                        lines[k] = n
                        changes += 1
                break
        break

# ── 3. Also patch the _frobenius_tier output to remove display notation refs ──
for i, l in enumerate(lines):
    if 'def _frobenius_tier(self, name: str, **kwargs) -> Dict[str, Any]:' in l:
        for j in range(i, min(i+80, len(lines))):
            old = lines[j]
            # The comments and docstrings may still reference display notation
            n = old
            n = n.replace('display notation', 'Shavian glyphs')
            if n != old:
                lines[j] = n
                changes += 1

# ── 4. Also patch _get_o_info which also calls _shavian_to_display ──
# Check if there's an _get_o_info that uses it
for i, l in enumerate(lines):
    if 'def _get_o_info' in l and 'self' in l:
        for j in range(i, min(i+50, len(lines))):
            old = lines[j]
            n = old.replace('self._shavian_to_display(', '')
            # Don't fully remove, just ensure it works (identity already returns val)
            if n != old and 'return' not in old:
                pass  # identity function handles it
        break

# ── Write ──
result = '\n'.join(lines)
p.write_text(result, encoding="utf-8")
shav = sum(1 for c in result if 0x10450 <= ord(c) <= 0x1047F)
print(f"\nWritten: {p}")
print(f"Shavian glyphs: {shav}")
print(f"Changes: {changes}")
