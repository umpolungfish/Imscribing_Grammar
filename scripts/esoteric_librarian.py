#!/usr/bin/env python3
"""
esoteric_librarian.py — Navigate the esoteric library by crystal address.

Usage:
  python3 esoteric_librarian.py show tao 1          Show imscription for a chapter
  python3 esoteric_librarian.py list tao [--tier T]  List entries, optionally by tier
  python3 esoteric_librarian.py dist tao 1 tao 81    Hamming distance between two entries
  python3 esoteric_librarian.py near tao 1 [--n 5]   Find nearest neighbors
  python3 esoteric_librarian.py validate tao          Check structural consistency
  python3 esoteric_librarian.py stats tao             Catalog statistics & tier distribution
  python3 esoteric_librarian.py export tao 1          Emit crystal-address notation
  python3 esoteric_librarian.py audio tao 1           Sonify an entry
  python3 esoteric_librarian.py video tao 1           Render annotated video
  python3 esoteric_librarian.py rewrite tao 1         Print structural rewrite prompt
  python3 esoteric_librarian.py scaffold upanishads   Create generator template
  python3 esoteric_librarian.py add tao --tuple ...   Append one entry manually

Optimized v2.0:
  - Robust criticality key normalization (⊙ / ⊙)
  - `validate` command for structural consistency checks
  - `stats` command for catalog-level tier distribution
  - `export` command for crystal-address notation output
"""

import sys, os, json, argparse, unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from sounds import FIELD_ORDER, PRIMITIVE_MAP, OLD_ID_MAP, resolve_id

# ── field keys ───────────────────────────────────────────────────────────────
# Catalog files may use ⊙ (pre-migration key) or ⊙ (post-migration) for criticality.
# We accept BOTH when reading, but normalize to ⊙ for internal tuple storage.
CRIT_LEGACY = '⊙'    # used in all catalog .json files
CRIT_MODERN = '⊙'    # used in sounds.py FIELD_ORDER
_FIELDS = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', CRIT_LEGACY, '⊥', '⊞', '◻']

# ── criticality key normalization ─────────────────────────────────────────────
def _get_crit(entry):
    """Read criticality from entry, accepting ⊙ or ⊙ key. Normalize to ⊙_* form."""
    raw = entry.get(CRIT_LEGACY, entry.get(CRIT_MODERN, ''))
    # If we got ⊙, normalize to ⊙ for internal consistency
    if raw.startswith(CRIT_MODERN + '_'):
        raw = CRIT_LEGACY + raw[len(CRIT_MODERN):]
    return unicodedata.normalize('NFC', raw)

def _norm_glyph(gid):
    """Return NFC-normalized glyph ID with ⊙ form for criticality."""
    gid = unicodedata.normalize('NFC', gid.strip())
    if gid.startswith(CRIT_MODERN + '_'):
        return CRIT_LEGACY + gid[len(CRIT_MODERN):]
    return gid

# ── catalog loading ───────────────────────────────────────────────────────────
def _load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def _tao_path():
    return os.path.join(_HERE, 'esoteric_library', 'tao_te_ching.json')

def _ig_path():
    return os.path.join(_HERE, 'IG_catalog.json')

def load_catalog(name):
    """Load a catalog by short name. Returns list of entry dicts."""
    if name in ('tao', 'tao_te_ching'):
        return _load_json(_tao_path())
    if name in ('ig', 'catalog', 'ig_catalog'):
        return _load_json(_ig_path())
    if os.path.exists(name):
        return _load_json(name)
    slug = name.lower().replace(' ', '_').replace('-', '_')
    candidate = os.path.join(_HERE, 'esoteric_library', f'{slug}.json')
    if os.path.exists(candidate):
        return _load_json(candidate)
    raise FileNotFoundError(
        f"Catalog '{name}' not found. "
        f"Known short names: tao, ig. "
        f"Or place a .json file in esoteric_library/ and use its basename."
    )

def find_entry(catalog, key):
    """Find one entry by name (string) or number (int / str digit)."""
    if isinstance(key, str) and key.isdigit():
        key = int(key)
    if isinstance(key, int):
        for e in catalog:
            if e.get('number') == key:
                return e
        raise KeyError(f"No entry with number {key}")
    for e in catalog:
        if e.get('name') == key:
            return e
    raise KeyError(f"No entry named '{key}'")
# ── imscription helpers ───────────────────────────────────────────────────────
def get_ids(entry):
    """Return list of 12 canonical glyph IDs from an entry (normalized to ⊙ form)."""
    ids = []
    for field in _FIELDS:
        if field == CRIT_LEGACY:
            ids.append(_get_crit(entry))
        else:
            ids.append(_norm_glyph(entry.get(field, '')))
    return ids

def entry_tuple(entry):
    """12-tuple of raw glyph ID strings in _FIELDS order."""
    return tuple(get_ids(entry))

def hamming(a, b):
    """Hamming distance between two 12-tuples."""
    return sum(x != y for x, y in zip(a, b))

# ── display ───────────────────────────────────────────────────────────────────
_FIELD_LABELS = {
    '⊢': 'D  Dimensionality',
    '⊣': 'T  Topology      ',
    '>': 'R  Relational    ',
    '<': 'P  Polarity      ',
    '⋈': 'F  Fidelity      ',
    '⊤': 'K  Kinetics      ',
    '∈': 'G  Scope         ',
    '∋': 'Γ  Grammar       ',
    CRIT_LEGACY: 'Φ  Criticality   ',
    '⊥': 'H  Chirality',
    '⊞': 'S  Stoichiometry ',
    '◻': 'Ω  Winding       ',
}

_OLD_NAMES = {v: k for k, v in OLD_ID_MAP.items()}

def _friendly(glyph_id):
    """⊙ → ⊙ (the most readable old name if available)."""
    # Try both ⊙_ and ⊙_ forms for lookup
    lookup = glyph_id.replace(CRIT_LEGACY + '_', CRIT_MODERN + '_')
    return _OLD_NAMES.get(lookup, glyph_id)

def show_entry(entry):
    num = entry.get('number', '')
    title = entry.get('title', entry.get('name', ''))
    print(f"\n{'─'*60}")
    if num:
        print(f"  Chapter {num}: {title}")
    else:
        print(f"  {title}")
    desc = entry.get('description', '')
    if desc:
        print(f"  {desc}")
    tier = entry.get('tier', '')
    cscore = entry.get('C_score', '')
    if tier or cscore != '':
        print(f"  tier: {tier}   C_score: {cscore}")
    print()
    for f in _FIELDS:
        val = entry.get(f, '')
        if f == CRIT_LEGACY and not val:
            val = _get_crit(entry)
        label = _FIELD_LABELS.get(f, f)
        friendly = _friendly(val)
        diff = f" ({friendly})" if friendly != val else ''
        print(f"  {label}  {val}{diff}")
    text = entry.get('text', '')
    if text:
        print(f"\n  \"{text[:120]}{'…' if len(text)>120 else ''}\"")
    notes = entry.get('notes', '')
    if notes:
        print(f"\n  Note: {notes[:200]}")
    print(f"{'─'*60}\n")# ── commands ──────────────────────────────────────────────────────────────────
def cmd_show(args):
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    show_entry(entry)

def cmd_list(args):
    cat = load_catalog(args.catalog)
    tier_filter = getattr(args, 'tier', None)
    print(f"\n{'#':>4}  {'Name':<32}  {'Tier':<8}  {'C':>5}  {'Crit':>10}  Title")
    print('─' * 90)
    for e in cat:
        tier = e.get('tier', '')
        if tier_filter and tier != tier_filter:
            continue
        num = e.get('number', '')
        name = e.get('name', '')[:30]
        cscore = e.get('C_score', 0)
        crit = _get_crit(e)
        title = e.get('title', '')[:35]
        print(f"  {num:>3}  {name:<32}  {tier:<8}  {cscore:>5.2f}  {crit:>10}  {title}")
    print()

def cmd_dist(args):
    cat_a = load_catalog(args.catalog_a)
    cat_b = load_catalog(args.catalog_b)
    a = find_entry(cat_a, args.key_a)
    b = find_entry(cat_b, args.key_b)
    d = hamming(entry_tuple(a), entry_tuple(b))
    name_a = a.get('title', a.get('name', ''))
    name_b = b.get('title', b.get('name', ''))
    print(f"\nHamming distance: {d}/12")
    print(f"  A: {name_a}")
    print(f"  B: {name_b}")
    if d == 0:
        print("  ↳ Identical imscription.")
    elif d <= 2:
        print("  ↳ Structurally adjacent (≤2 field difference).")
    elif d <= 4:
        print("  ↳ Structurally related.")
    elif d <= 8:
        print("  ↳ Same crystal region.")
    else:
        print("  ↳ Structurally distant (>8 fields).")
    ta, tb = entry_tuple(a), entry_tuple(b)
    diffs = [(f, va, vb) for f, va, vb in zip(_FIELDS, ta, tb) if va != vb]
    if diffs:
        print(f"\n  Differing fields ({len(diffs)}):")
        for f, va, vb in diffs:
            print(f"    {_FIELD_LABELS.get(f, f).split()[0]}: {va} → {vb}")
    print()

def cmd_near(args):
    cat = load_catalog(args.catalog)
    other_name = getattr(args, 'other_catalog', None) or args.catalog
    other = load_catalog(other_name)
    entry = find_entry(cat, args.key)
    ta = entry_tuple(entry)
    name_a = entry.get('title', entry.get('name', ''))
    n = getattr(args, 'n', 5)
    scored = []
    for e in other:
        if e.get('name') == entry.get('name') and other_name == args.catalog:
            continue
        d = hamming(ta, entry_tuple(e))
        scored.append((d, e))
    scored.sort(key=lambda x: x[0])
    print(f"\nNearest neighbors to: {name_a}\n")
    for d, e in scored[:n]:
        num = e.get('number', '')
        name = e.get('title', e.get('name', ''))
        tier = e.get('tier', '')
        print(f"  d={d:>2}  {num:>3}  {tier:<8}  {name}")
    print()# ── validate ──────────────────────────────────────────────────────────────────
def cmd_validate(args):
    """Check structural consistency of a catalog: verify all fields are valid."""
    cat = load_catalog(args.catalog)
    total = len(cat)
    errors = []
    warnings = []
    valid_vals = {
        '⊢': {'𐑛', '𐑨', '𐑼', '𐑦'},
        '⊣': {'𐑡', '𐑰', '𐑥', '𐑶', '𐑸'},
        '>': {'𐑩', '𐑑', '𐑽', '𐑾'},
        '<': {'𐑗', '𐑿', '𐑬', '𐑯', '𐑹'},
        '⋈': {'ƒ^ì', 'ƒ^ð', 'ƒ^ż'},
        '⊤': {'Ç^-', 'Ç^W', 'Ç^@', 'Ç^Ù', 'Ç^λ'},
        '∈': {'𐑚', '𐑔', '𐑲'},
        '∋': {'ɢ^∧', 'ɢ^˝', 'ɢ^ˌ', 'ɢ^Ş'},
        CRIT_LEGACY: {'𐑢', '⊙', '𐑮', '𐑻', '𐑣'},
        '⊥': {'𐑓', '𐑒', '𐑖', '𐑫'},
        '⊞': {'𐑙', '𐑕', '𐑳'},
        '◻': {'𐑷', '𐑴', '𐑭', '𐑟'},
    }
    valid_tiers = {'T_0', 'T_1', 'T_2', 'T_3', 'T_inf', 'O₀', 'O₁', 'O₂', 'O₂†', 'O_∞', ''}

    for i, e in enumerate(cat):
        name = e.get('name', f'[index {i}]')
        # Check required fields
        for field in _FIELDS:
            val = e.get(field, '')
            if field == CRIT_LEGACY and not val:
                val = _get_crit(e)
            if not val:
                errors.append(f"{name}: missing field {field}")
                continue
            nfc_val = unicodedata.normalize('NFC', val)
            if nfc_val != val:
                warnings.append(f"{name}: {field} has non-NFC normalization: {repr(val)}")
            if val not in valid_vals.get(field, set()):
                errors.append(f"{name}: invalid {field} value: {repr(val)}")
        # Check tier
        tier = e.get('tier', '')
        if tier not in valid_tiers:
            warnings.append(f"{name}: unrecognized tier: {repr(tier)}")
        # Check C_score range
        cs = e.get('C_score', None)
        if cs is not None:
            try:
                csf = float(cs)
                if csf < 0 or csf > 1:
                    warnings.append(f"{name}: C_score out of [0,1]: {cs}")
            except (ValueError, TypeError):
                warnings.append(f"{name}: C_score not numeric: {cs}")

    print(f"\nCatalog: {args.catalog}  ({total} entries)")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    if errors:
        print("\n  Errors:")
        for e in errors[:20]:
            print(f"    ✗ {e}")
        if len(errors) > 20:
            print(f"    ... and {len(errors)-20} more")
    if warnings:
        print("\n  Warnings:")
        for w in warnings[:20]:
            print(f"    ⚠ {w}")
        if len(warnings) > 20:
            print(f"    ... and {len(warnings)-20} more")
    if not errors and not warnings:
        print("  ✓ All entries are structurally consistent.")
    print()# ── stats ─────────────────────────────────────────────────────────────────────
def cmd_stats(args):
    """Catalog-level statistics: tier distribution, C-score range, field diversity."""
    cat = load_catalog(args.catalog)
    total = len(cat)
    if total == 0:
        print(f"\nCatalog '{args.catalog}' is empty.\n")
        return

    # Tier distribution
    tiers = {}
    for e in cat:
        t = e.get('tier', '')
        tiers[t] = tiers.get(t, 0) + 1

    # C-score stats
    cscores = []
    for e in cat:
        cs = e.get('C_score', None)
        if cs is not None:
            try:
                cscores.append(float(cs))
            except (ValueError, TypeError):
                pass

    # Field diversity — count distinct values per field
    field_diversity = {}
    for f in _FIELDS:
        vals = set()
        for e in cat:
            if f == CRIT_LEGACY:
                vals.add(_get_crit(e))
            else:
                v = e.get(f, '')
                if v:
                    vals.add(v)
        field_diversity[f] = len(vals)

    print(f"\n{'='*60}")
    print(f"  Catalog: {args.catalog}")
    print(f"  Entries: {total}")
    print(f"{'='*60}")

    print(f"\n  Tier Distribution:")
    for t in sorted(tiers.keys(), key=lambda x: (
        {'T_0':0,'T_1':1,'T_2':2,'T_3':3,'T_inf':4,'O₀':0,'O₁':1,'O₂':2,'O₂†':3,'O_∞':4,'':-1}.get(x, 99)
    )):
        label = t if t else '(unset)'
        pct = tiers[t] / total * 100
        bar = '█' * int(pct / 2) + '░' * (50 - int(pct / 2))
        print(f"    {label:<8} {tiers[t]:>4} ({pct:5.1f}%) {bar}")

    if cscores:
        print(f"\n  C-Score:  min={min(cscores):.2f}  max={max(cscores):.2f}  "
              f"mean={sum(cscores)/len(cscores):.2f}  median={sorted(cscores)[len(cscores)//2]:.2f}")
        print(f"  Entries with C_score: {len(cscores)}/{total}")

    print(f"\n  Field Diversity (distinct values):")
    for f in _FIELDS:
        label = _FIELD_LABELS.get(f, f).split()[0]
        bar = '█' * field_diversity[f] + '░' * (12 - field_diversity[f])
        print(f"    {label}: {field_diversity[f]:>2} {bar}")
    print()

# ── export ────────────────────────────────────────────────────────────────────
def cmd_export(args):
    """Emit entry as a crystal-address notation string."""
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    ids = get_ids(entry)
    name = entry.get('title', entry.get('name', ''))
    tier = entry.get('tier', '')
    cs = entry.get('C_score', '')
    print(f"\n  {name}")
    if tier or cs:
        print(f"  tier={tier}  C_score={cs}")
    print(f"  ⟨{'  '.join(ids)}⟩")
    print(f"  Address: {' '.join(ids)}")
    print()# ── audio ─────────────────────────────────────────────────────────────────────
def cmd_audio(args):
    import subprocess
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    name = entry.get('name', f"chapter_{args.key}")
    out = getattr(args, 'output', None) or f"{name}.wav"
    dur = getattr(args, 'dur', 0.75)
    ids = get_ids(entry)
    tuple_str = ' '.join(ids)
    script = os.path.join(_HERE, 'imscribeaudio.py')
    cmd = [sys.executable, script, '--tuple', tuple_str, '--output', out, '--dur', str(dur)]
    print(f"Sonifying: {entry.get('title', name)}")
    print(f"Tuple: {tuple_str}")
    subprocess.run(cmd)

# ── video ─────────────────────────────────────────────────────────────────────
def cmd_video(args):
    import subprocess
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    name = entry.get('name', f"chapter_{args.key}")
    out = getattr(args, 'output', None) or f"{name}.mp4"
    dur = getattr(args, 'dur', 0.75)
    ids = get_ids(entry)
    tuple_str = ' '.join(ids)
    script = os.path.join(_HERE, 'imscribevideo.py')
    cmd = [sys.executable, script, '--tuple', tuple_str, '--output', out, '--dur', str(dur)]
    title = entry.get('title', name)
    if title:
        cmd += ['--label', title]
    print(f"Rendering: {title}")
    subprocess.run(cmd)

# ── rewrite ───────────────────────────────────────────────────────────────────
def cmd_rewrite(args):
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    title = entry.get('title', entry.get('name', ''))
    text = entry.get('text', '')
    notes = entry.get('notes', '')
    ids = get_ids(entry)
    print(f"\nStructural Rewrite Prompt — {title}")
    print('─' * 60)
    print(f"Source text:\n  {text}\n")
    print(f"Crystal address (12-tuple):\n  {' '.join(ids)}\n")
    print("Primitive semantics:")
    for f, gid in zip(_FIELDS, ids):
        friendly = _friendly(gid)
        label = _FIELD_LABELS.get(f, f).strip()
        print(f"  {label}: {friendly}")
    if notes:
        print(f"\nStructural note:\n  {notes}")
    print("""
Rewrite instructions:
  The crystal address above is the type of this passage.
  Rewrite it in a different register or tradition while preserving
  every primitive coordinate exactly. The rewrite is successful when
  the new text imscribes the same 12-tuple and no information is lost —
  only the surface form changes.

  Check each primitive in the rewrite:
    - Does the dimensionality match (scope of ontological claim)?
    - Does the topology match (how concepts connect)?
    - Does the relational mode match (who is speaking to whom)?
    - Does the polarity match (symmetry of the argument)?
    - Does the fidelity match (directness vs. indirection)?
    - Does the kinetics match (pace, stillness, movement)?
    - Does the scope match (narrow vs. full-spectrum)?
    - Does the grammar match (simultaneous vs. sequential)?
    - Does the criticality match (stable, critical, expanding)?
    - Does the chirality match (dry, shallow, deep, infinite)?
    - Does the stoichiometry match (one voice, many, asymmetric)?
    - Does the winding match (open, cyclic, returning)?
""")# ── scaffold ──────────────────────────────────────────────────────────────────
_SCAFFOLD_TEMPLATE = '''\
#!/usr/bin/env python3
"""Generate {name}.json — imscribed catalog for {name}.
Fill in the entries below, then run:
    python3 esoteric_library/gen_{name}.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PHI = '⊙'  # criticality key (pre-migration, compatible with all tools)

# Available glyph IDs — field order: ⊢ ⊣ > Φ ƒ Ç Γ ɢ [⊙=crit] Ħ Σ Ω
#   ⊢: 𐑛 𐑨 𐑼 𐑦
#   ⊣: 𐑡 𐑰 𐑥 𐑶 𐑸
#   >: 𐑩 𐑑 𐑽 𐑾
#   Φ: 𐑗 𐑿 𐑬 𐑯 𐑹}
#   ƒ: ƒ^ì ƒ^ð ƒ^ż
#   Ç: Ç^- Ç^W Ç^@ Ç^Ù Ç^λ
#   Γ: 𐑚 𐑔 𐑲
#   ɢ: ɢ^∧ ɢ^˝ ɢ^ˌ ɢ^Ş
#   ⊙: 𐑢 ⊙ 𐑮 𐑻 𐑣
#   Ħ: 𐑓 𐑒 𐑖 𐑫
#   Σ: 𐑙 𐑕 𐑳
#   Ω: 𐑷 𐑴 𐑭 𐑟

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {{
        "name": f"{name}_{{num:02d}}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "⊢": D, "⊣": T, ">": R, "<": P, "⋈": F,
        "⊤": K, "∈": G, "∋": Gm, PHI: C,
        "⊥": H, "⊞": S, "◻": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }}

chapters = [
    entry(1, "Section title",
        "One-line description",
        "Verbatim source text.",
        "𐑦","𐑸","𐑽","𐑹}","ƒ^ì","Ç^@","𐑲","ɢ^∧","𐑻","𐑫","𐑙","𐑭",
        "T_inf", 0.95,
        "Why these coordinates: ..."),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "{name}.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {{len(chapters)}} entries -> {{out}}")
'''

def cmd_scaffold(args):
    name = args.name.lower().replace(' ', '_').replace('-', '_')
    lib_dir = os.path.join(_HERE, 'esoteric_library')
    os.makedirs(lib_dir, exist_ok=True)
    gen_path = os.path.join(lib_dir, f'gen_{name}.py')
    if os.path.exists(gen_path) and not getattr(args, 'force', False):
        sys.exit(f"Error: {gen_path} already exists. Use --force to overwrite.")
    content = _SCAFFOLD_TEMPLATE.format(name=name)
    with open(gen_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {gen_path}")
    print()
    print("Next steps:")
    print(f"  1. Open {gen_path} and fill in entries using the entry() helper.")
    print(f"  2. Run:  python3 esoteric_library/gen_{name}.py")
    print(f"  3. Navigate:  python3 esoteric_librarian.py list {name}")
    print()
    print("The catalog short name will be the filename without .json:")
    print(f"  python3 esoteric_librarian.py show {name} 1")# ── imscribe (auto-assign via LLM loop) ──────────────────────────────────────
def cmd_imscribe(args):
    """Auto-assign all 12 primitives via IGInquiryLoop, then save to catalog."""
    try:
        from IG_inquiry import IGInquiryLoop
    except ImportError as e:
        sys.exit(f"Error: could not import IGInquiryLoop from IG_inquiry.py: {e}")

    name        = args.name
    title       = getattr(args, 'title', '') or name
    description = getattr(args, 'description', '') or ''
    text        = getattr(args, 'text', '') or ''
    if not text and getattr(args, 'file', None):
        with open(args.file, encoding='utf-8') as fh:
            text = fh.read()
    provider    = getattr(args, 'provider', None) or os.environ.get('IG_PROVIDER', 'anthropic')
    model       = getattr(args, 'model', None)   or os.environ.get('IG_MODEL', None)

    sections = [s.strip() for s in text.split('\n\n') if s.strip()] if text else []
    multi = len(sections) > 1

    cat_slug = args.catalog.lower().replace(' ', '_').replace('-', '_')
    lib_dir  = os.path.join(_HERE, 'esoteric_library')
    if args.catalog in ('tao', 'tao_te_ching'):
        cat_path = _tao_path()
    elif args.catalog in ('ig', 'catalog', 'ig_catalog'):
        cat_path = _ig_path()
    else:
        os.makedirs(lib_dir, exist_ok=True)
        cat_path = os.path.join(lib_dir, f'{cat_slug}.json')
        if not os.path.exists(cat_path):
            with open(cat_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print(f"Created new catalog: {cat_path}")

    def _run_loop(seed_text):
        kw = dict(seed=seed_text, provider=provider, verbose=True)
        if model:
            kw['model'] = model
        loop = IGInquiryLoop(**kw)
        loop.run()
        return loop

    def _load_catalog():
        with open(cat_path, encoding='utf-8') as f:
            return json.load(f)

    def _save_catalog(cat):
        with open(cat_path, 'w', encoding='utf-8') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)

    if multi:
        print(f"\nImscribing {len(sections)} sections one at a time…\n")
        total_saved = 0
        for i, sec_text in enumerate(sections):
            sec_name = f"{name}_{i+1:02d}"
            catalog = _load_catalog()
            if sec_name in {e.get('name') for e in catalog}:
                print(f"  §{i+1} ({sec_name}) already imscribed — skipping.")
                continue
            print(f"\n{'='*60}")
            print(f"  Imscribing §{i+1}/{len(sections)}: {sec_name}")
            print(f"{'='*60}\n")
            seed = (
                f"Imscribe the following section for the esoteric library catalog.\n\n"
                f"Name: {sec_name}\n"
                f"Parent work: {title}\n"
                f"Section: {i+1} of {len(sections)}\n"
                + (f"Description: {description}\n" if description else "")
                + f"\nSource text:\n{sec_text}\n\n"
                f"Reason through all 12 primitives carefully for this specific passage, "
                f"then call encode_system(name='{sec_name}', description='...', ...) "
                f"with all 12 values explicitly set. Once imscribed, CONCLUDE."
            )
            loop = _run_loop(seed)
            imscription = loop.dispatcher.catalog._entries.get(sec_name)
            if not imscription:
                for k, v in loop.dispatcher.catalog._entries.items():
                    if k not in {e.get('name') for e in _load_catalog()} and name in k:
                        imscription = v
                        break
            if not imscription:
                print(f"  Warning: §{i+1} ({sec_name}) was not imscribed — skipping.")
                continue
            entry = {
                'name': sec_name, 'number': i + 1,
                'title': f"{title} — §{i+1}",
                'text': sec_text,
            }
            if description:
                entry['description'] = description
            for field in _FIELDS:
                entry[field] = imscription.get(field, '')
            catalog = _load_catalog()
            catalog.append(entry)
            _save_catalog(catalog)
            total_saved += 1
            print(f"\n  ✓ Saved §{i+1} ({sec_name})  [{total_saved} saved so far]")
            show_entry(entry)
        print(f"\nDone. Imscribed {total_saved}/{len(sections)} sections → {cat_path}")
    else:
        seed = (
            f"Imscribe the following object for the esoteric library catalog.\n\n"
            f"Name: {name}\n"
            + (f"Title: {title}\n" if title and title != name else "")
            + (f"Description: {description}\n" if description else "")
            + (f"\nSource text:\n{text}\n" if text else "")
            + f"\nReason through all 12 primitives carefully, then call "
            f"encode_system(name='{name}', description='{description or title}', ...) "
            f"with all 12 values explicitly set. Once imscribed, CONCLUDE."
        )
        loop = _run_loop(seed)
        catalog = _load_catalog()
        existing_names = {e.get('name') for e in catalog}
        imscription = loop.dispatcher.catalog._entries.get(name)
        if not imscription:
            for k, v in loop.dispatcher.catalog._entries.items():
                if k.lower() == name.lower() and k not in existing_names:
                    imscription, name = v, k
                    break
        if not imscription:
            sys.exit(f"\nError: '{name}' was not imscribed by the loop. Check output above.")
        if name in existing_names:
            sys.exit(f"Error: '{name}' already exists in {cat_path}. Use a different --name.")
        entry = {'name': name}
        if args.number is not None:
            entry['number'] = args.number
        if title:
            entry['title'] = title
        if description:
            entry['description'] = description
        if text:
            entry['text'] = text
        for field in _FIELDS:
            entry[field] = imscription.get(field, '')
        if getattr(args, 'tier', ''):
            entry['tier'] = args.tier
        if getattr(args, 'notes', ''):
            entry['notes'] = args.notes
        catalog.append(entry)
        _save_catalog(catalog)
        print(f"\nSaved '{name}' to {cat_path}  ({len(catalog)} entries total)")
        show_entry(entry)# ── add ───────────────────────────────────────────────────────────────────────
def cmd_add(args):
    name = args.catalog.lower().replace(' ', '_').replace('-', '_')
    lib_dir = os.path.join(_HERE, 'esoteric_library')
    cat_path = os.path.join(lib_dir, f'{name}.json')
    if not os.path.exists(cat_path):
        with open(cat_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print(f"Created new catalog: {cat_path}")
    with open(cat_path, encoding='utf-8') as f:
        catalog = json.load(f)

    raw = args.tuple.replace(',', ' ').split()
    if len(raw) != 12:
        sys.exit(f"Error: --tuple requires exactly 12 glyph IDs, got {len(raw)}")

    field_keys = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', CRIT_LEGACY, '⊥', '⊞', '◻']
    entry = {}
    entry['name'] = args.name
    if args.number is not None:
        entry['number'] = args.number
    if args.title:
        entry['title'] = args.title
    if args.description:
        entry['description'] = args.description
    if args.text:
        entry['text'] = args.text
    for key, val in zip(field_keys, raw):
        entry[key] = _norm_glyph(val)
    if args.tier:
        entry['tier'] = args.tier
    if args.cscore is not None:
        entry['C_score'] = args.cscore
    if args.notes:
        entry['notes'] = args.notes

    existing_names = {e.get('name') for e in catalog}
    if entry['name'] in existing_names:
        sys.exit(f"Error: entry '{entry['name']}' already exists in {cat_path}. "
                 "Use a different --name or edit the file directly.")
    catalog.append(entry)
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"Added '{entry['name']}' to {cat_path}  ({len(catalog)} entries total)")
    show_entry(entry)

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest='cmd')

    # show
    s = sub.add_parser('show', help='Show imscription for one entry')
    s.add_argument('catalog', help='Catalog name: tao, ig, or basename in esoteric_library/')
    s.add_argument('key', help='Chapter number or entry name')

    # list
    s = sub.add_parser('list', help='List all entries in a catalog')
    s.add_argument('catalog')
    s.add_argument('--tier', help='Filter by tier (e.g. T_inf)')

    # dist
    s = sub.add_parser('dist', help='Hamming distance between two entries')
    s.add_argument('catalog_a')
    s.add_argument('key_a')
    s.add_argument('catalog_b')
    s.add_argument('key_b')

    # near
    s = sub.add_parser('near', help='Nearest neighbors')
    s.add_argument('catalog')
    s.add_argument('key')
    s.add_argument('--n', type=int, default=5, help='Number of neighbors')
    s.add_argument('--other-catalog', dest='other_catalog', default=None,
                   help='Search in a different catalog (default: same)')

    # validate
    s = sub.add_parser('validate', help='Check structural consistency of a catalog')
    s.add_argument('catalog')

    # stats
    s = sub.add_parser('stats', help='Catalog-level statistics and tier distribution')
    s.add_argument('catalog')

    # export
    s = sub.add_parser('export', help='Emit entry as crystal-address notation')
    s.add_argument('catalog')
    s.add_argument('key')

    # audio
    s = sub.add_parser('audio', help='Sonify an entry')
    s.add_argument('catalog')
    s.add_argument('key')
    s.add_argument('--dur', type=float, default=0.75)
    s.add_argument('--output', '-o')

    # video
    s = sub.add_parser('video', help='Render video for an entry')
    s.add_argument('catalog')
    s.add_argument('key')
    s.add_argument('--dur', type=float, default=0.75)
    s.add_argument('--output', '-o')

    # rewrite
    s = sub.add_parser('rewrite', help='Print structural rewrite prompt')
    s.add_argument('catalog')
    s.add_argument('key')

    # scaffold
    s = sub.add_parser('scaffold', help='Create a generator template for a new text')
    s.add_argument('name', help='Short name for the new catalog (e.g. upanishads)')
    s.add_argument('--force', action='store_true', help='Overwrite if file exists')

    # imscribe
    s = sub.add_parser('imscribe',
        help='Auto-assign all 12 primitives via the IG_inquiry LLM loop and save to catalog')
    s.add_argument('catalog', help='Target catalog name')
    s.add_argument('--name', '-n', required=True, help='Unique entry name')
    s.add_argument('--number', type=int, default=None, help='Section/chapter number')
    s.add_argument('--title', default='', help='Section title')
    s.add_argument('--description', '--desc', default='', help='One-line description')
    s.add_argument('--text', default='', help='Verbatim source text to imscribe')
    s.add_argument('--file', '-f', default=None, help='Path to text file (alternative to --text)')
    s.add_argument('--tier', default='', help='Tier override (optional)')
    s.add_argument('--notes', default='', help='Structural notes override (optional)')
    s.add_argument('--provider', default='anthropic',
                   help='LLM provider: anthropic, openai, deepseek, gemini, … (default: anthropic)')
    s.add_argument('--model', default=None, help='Model ID override')

    # add
    s = sub.add_parser('add', help='Append one entry to a catalog (manual --tuple required)')
    s.add_argument('catalog', help='Target catalog name')
    s.add_argument('--tuple', '-t', required=True, metavar='IDS',
                   help='12 glyph IDs in field order (space- or comma-separated)')
    s.add_argument('--name', '-n', required=True, help='Unique entry name')
    s.add_argument('--number', type=int, default=None, help='Section/chapter number')
    s.add_argument('--title', default='', help='Section title')
    s.add_argument('--description', '--desc', default='', help='One-line description')
    s.add_argument('--text', default='', help='Verbatim source text')
    s.add_argument('--tier', default='', help='Tier label (e.g. T_inf, T_2)')
    s.add_argument('--cscore', type=float, default=None, help='C_score 0.0–1.0')
    s.add_argument('--notes', default='', help='Structural reasoning notes')

    args = p.parse_args()
    if args.cmd is None:
        p.print_help()
        return

    dispatch = {
        'show':     cmd_show,
        'list':     cmd_list,
        'dist':     cmd_dist,
        'near':     cmd_near,
        'validate': cmd_validate,
        'stats':    cmd_stats,
        'export':   cmd_export,
        'audio':    cmd_audio,
        'video':    cmd_video,
        'rewrite':  cmd_rewrite,
        'scaffold': cmd_scaffold,
        'add':      cmd_add,
        'imscribe': cmd_imscribe,
    }
    dispatch[args.cmd](args)

if __name__ == '__main__':
    main()