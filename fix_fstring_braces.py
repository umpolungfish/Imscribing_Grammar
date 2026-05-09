"""
Fix Φ_} → Φ_}} inside f-string literal text after migration.
Uses Python 3.12 FSTRING_START/MIDDLE/END tokens to identify f-string spans.
"""

import ast, pathlib, sys, tokenize, io

SKIP = {
    'migrate_keys.py','migrate_keys2.py','migrate_keys3.py','migrate_all.py',
    'fix_fstring_braces.py','migrate_phonetic.py','migrate_primitive_symbols.py',
    'migrate_to_symbol_ids.py',
}

def line_col_to_offset(lines: list[str], line: int, col: int) -> int:
    """Convert 1-based (line, col) to byte offset in the joined source."""
    return sum(len(lines[i]) for i in range(line - 1)) + col


def fix_phi_in_fstrings(source: str) -> str:
    """Replace Φ_} with Φ_}} only inside f-string literal (MIDDLE) spans."""
    lines = source.splitlines(keepends=True)

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return source

    # Collect (start_offset, end_offset) of FSTRING_MIDDLE tokens
    middle_spans = []
    depth = 0
    for tok in tokens:
        if tok.type == tokenize.FSTRING_START:
            depth += 1
        elif tok.type == tokenize.FSTRING_END:
            depth -= 1
        elif tok.type == tokenize.FSTRING_MIDDLE and depth > 0:
            s = line_col_to_offset(lines, tok.start[0], tok.start[1])
            e = line_col_to_offset(lines, tok.end[0], tok.end[1])
            middle_spans.append((s, e))

    if not middle_spans:
        return source

    # Apply fixes in reverse order
    result = list(source)
    for start, end in reversed(middle_spans):
        seg = ''.join(result[start:end])
        # Replace Φ_} that isn't already Φ_}}
        fixed = seg.replace('Φ_}}', '\x00PLACEHOLDER\x00').replace('Φ_}', 'Φ_}}').replace('\x00PLACEHOLDER\x00', 'Φ_}}')
        result[start:end] = list(fixed)

    return ''.join(result)


files = []
for p in pathlib.Path('.').glob('*.py'):
    if p.name not in SKIP:
        files.append(p)
for sub in ['agents', 'space_search']:
    for p in pathlib.Path(sub).glob('*.py'):
        if p.name not in SKIP:
            files.append(p)

changed = 0
for p in sorted(files):
    text = p.read_text(encoding='utf-8')
    if 'Φ_}' not in text:
        continue
    try:
        ast.parse(text)
        continue  # already valid
    except SyntaxError:
        pass
    fixed = fix_phi_in_fstrings(text)
    try:
        ast.parse(fixed)
        p.write_text(fixed, encoding='utf-8')
        changed += 1
        print(f"fixed: {p}")
    except SyntaxError as e:
        print(f"STILL BROKEN: {p}: {e}")

print(f"Done. {changed} files fixed.")
