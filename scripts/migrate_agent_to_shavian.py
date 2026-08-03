#!/usr/bin/env python3
"""Migrate true_agentic_agent.py to Shavian Unicode glyphs."""
import re, sys
from pathlib import Path

# Display→Shavian (from IG_inquiry.py _shavian_to_display, inverted)
D2S = {
    "𐑛": "𐑛", "𐑨": "𐑨", "𐑼": "𐑼", "𐑦": "𐑦",
    "𐑡": "𐑡", "𐑰": "𐑰", "𐑥": "𐑥", "𐑶": "𐑶", "𐑸": "𐑸",
    "𐑩": "𐑩", "𐑑": "𐑑", "𐑽": "𐑽", "𐑾": "𐑾",
    "𐑗": "𐑗", "𐑿": "𐑿", "𐑬": "𐑬", "𐑯": "𐑯", "𐑹": "𐑹",
    "𐑱": "𐑱", "𐑞": "𐑞", "𐑐": "𐑐",
    "𐑘": "𐑺", "𐑤": "𐑪", "𐑧": "𐑧", "𐑪": "𐑤", "𐑺": "𐑘",
    "𐑚": "𐑲", "𐑔": "𐑚", "𐑲": "𐑔",
    "𐑝": "𐑝", "𐑜": "𐑜", "𐑠": "𐑠", "𐑵": "𐑵",
    "𐑢": "𐑢", "⊙": "⊙", "𐑮": "𐑮", "𐑻": "𐑻", "𐑣": "𐑣",
    "𐑓": "𐑓", "𐑒": "𐑒", "𐑖": "𐑖", "𐑫": "𐑫",
    "𐑙": "𐑙", "𐑕": "𐑕", "𐑳": "𐑳",
    "𐑷": "𐑷", "𐑴": "𐑴", "𐑭": "𐑭", "𐑟": "𐑟",
}

def replace_display(text):
    """Replace display notation with Shavian, sorted longest-first to avoid partials."""
    for d in sorted(D2S, key=len, reverse=True):
        text = text.replace(d, D2S[d])
    return text

def main():
    ap = Path("/home/mrnob0dy666/imscribing_grammar/agents/true_agentic_agent.py")
    bak = ap.with_suffix(".py.bak")
    orig = ap.read_text(encoding="utf-8")
    bak.write_text(orig, encoding="utf-8")
    print(f"Backup: {bak}")
    
    lines = orig.split('\n')
    total_repl = 0
    
    # ── Phase 1: Docstring (lines before 'from __future__') ──
    doc_end = next(i for i, l in enumerate(lines) if l.strip().startswith("from __future__"))
    for i in range(doc_end):
        n = replace_display(lines[i])
        if n != lines[i]:
            total_repl += 1
            lines[i] = n
    print(f"Docstring: {total_repl} replacements")
    
    # ── Phase 2: _SYSTEM_PROMPT content ──
    sp_start = next(i for i, l in enumerate(lines) if "_SYSTEM_PROMPT" in l and "textwrap" in l)
    # Find closing triple-quote (first '"""' on its own line after sp_start)
    sp_end = next(i for i in range(sp_start+1, len(lines)) if lines[i].strip() == '"""')
    
    sp_repl = 0
    for i in range(sp_start, sp_end + 1):
        old = lines[i]
        n = replace_display(old)
        if n != old:
            sp_repl += 1
            lines[i] = n
    print(f"System prompt: {sp_repl} replacements (lines {sp_start+1}-{sp_end+1})")
    total_repl += sp_repl

    # ── Phase 3: PRIMITIVE_DISPLAY dict keys ──
    pd_start = next(i for i, l in enumerate(lines) if 'PRIMITIVE_DISPLAY: Dict[str, str] = {' in l)
    pd_end = next(i for i in range(pd_start, len(lines)) if lines[i].strip() == '}')
    pd_repl = 0
    for i in range(pd_start, pd_end + 1):
        old = lines[i]
        n = old
        for disp, shav in D2S.items():
            key_old = f'"{disp}"'
            if key_old in n:
                n = n.replace(key_old, f'"{shav}"')
        if n != old:
            pd_repl += 1
            lines[i] = n
    print(f"PRIMITIVE_DISPLAY: {pd_repl} key replacements")
    total_repl += pd_repl
    
    # ── Phase 4: Tool schema descriptions (prose only, NOT enum values) ──
    # Find TOOL_SCHEMAS start
    ts_start = next(i for i, l in enumerate(lines) if 'TOOL_SCHEMAS = [' in l)
    # Only replace in description strings, not in enum arrays
    # Descriptions are in parentheses: ("text...") after _fn(
    # We'll do a careful line-by-line approach: skip lines containing "enum"
    ts_repl = 0
    in_enum = False
    for i in range(ts_start, sp_start):
        l = lines[i]
        # Track if we're in an enum array
        if '"enum"' in l or '"type": "string", "enum"' in l:
            in_enum = True
        if in_enum and ']' in l and '[' not in l.split(']')[0]:
            in_enum = False
        if in_enum:
            continue  # Skip enum value lines
        n = replace_display(l)
        if n != l:
            ts_repl += 1
            lines[i] = n
    print(f"Tool schemas: {ts_repl} prose replacements")
    total_repl += ts_repl

    # ── Phase 5: _run_single_imscription normalization & _PRIM_VALID ──
    # These have display notation in code logic — DO NOT REPLACE.
    # They are internal identifiers that match tool enum values.
    # Only replace in prose comments.
    for i in range(len(lines)):
        l = lines[i]
        if l.strip().startswith('#') and not l.strip().startswith('#!'):
            n = replace_display(l)
            if n != l:
                lines[i] = n
                total_repl += 1
    
    # ── Write result ──
    result = '\n'.join(lines)
    ap.write_text(result, encoding="utf-8")
    
    # Count Shavian glyphs
    shav = sum(1 for c in result if 0x10450 <= ord(c) <= 0x1047F)
    print(f"\n{'='*60}")
    print(f"Written: {ap}")
    print(f"Shavian glyphs: {shav}")
    print(f"Total replacements: {total_repl}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
