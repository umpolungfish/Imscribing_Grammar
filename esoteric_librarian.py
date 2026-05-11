#!/usr/bin/env python3
"""
esoteric_librarian.py — Navigate the esoteric library by crystal address.

Usage:
  python3 esoteric_librarian.py show tao 1
      Show imscription for Tao Te Ching chapter 1.

  python3 esoteric_librarian.py list tao [--tier T_inf]
      List all chapters, optionally filtered by tier.

  python3 esoteric_librarian.py dist tao 1 tao 81
      Hamming distance between two chapters.

  python3 esoteric_librarian.py near tao 1 [--n 5] [--other-catalog ig]
      Find nearest neighbors within or across catalogs.

  python3 esoteric_librarian.py audio tao 1 [--dur 0.75] [--output FILE]
      Sonify the imscription for a chapter.

  python3 esoteric_librarian.py video tao 1 [--dur 0.75] [--output FILE]
      Render an annotated video for a chapter.

  python3 esoteric_librarian.py rewrite tao 1
      Print a structural rewrite prompt for the chapter.

  python3 esoteric_librarian.py scaffold upanishads
      Create esoteric_library/gen_upanishads.py — a ready-to-fill generator.

  python3 esoteric_librarian.py add tao --tuple "Ð_ω Þ_O ..." --name foo --title "..."
      Append one entry to a catalog from the command line.
"""

import sys, os, json, argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from sounds import FIELD_ORDER, PRIMITIVE_MAP, OLD_ID_MAP, resolve_id

# ── field keys ───────────────────────────────────────────────────────────────
CRIT_KEY = 'φ̂'   # pre-migration criticality key used in all catalog files

# canonical field order for display / distance computation
_FIELDS = ['Ð', 'Þ', 'Ř', 'Φ', 'ƒ', 'Ç', 'Γ', 'ɢ', CRIT_KEY, 'Ħ', 'Σ', 'Ω']

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
    # try as a direct path first
    if os.path.exists(name):
        return _load_json(name)
    # try as a short name in esoteric_library/
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
    """
    Find one entry by name (string) or number (int / str digit).
    Returns the entry dict or raises KeyError.
    """
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
    """Return list of 12 canonical ⊙-based glyph IDs from an entry."""
    ids = []
    for field in FIELD_ORDER:
        if field == '⊙' and '⊙' not in entry:
            raw = entry.get(CRIT_KEY, '')
            raw = raw.replace(CRIT_KEY + '_', '⊙_')
        else:
            raw = entry.get(field, entry.get(CRIT_KEY, '') if field == '⊙' else '')
        ids.append(raw)
    return ids

def entry_tuple(entry):
    """12-tuple of raw glyph ID strings in _FIELDS order."""
    ids = []
    for f in _FIELDS:
        ids.append(entry.get(f, ''))
    return tuple(ids)

def hamming(a, b):
    """Hamming distance between two 12-tuples."""
    return sum(x != y for x, y in zip(a, b))

# ── display ───────────────────────────────────────────────────────────────────

_FIELD_LABELS = {
    'Ð': 'D  Dimensionality',
    'Þ': 'T  Topology      ',
    'Ř': 'R  Relational    ',
    'Φ': 'P  Polarity      ',
    'ƒ': 'F  Fidelity      ',
    'Ç': 'K  Kinetics      ',
    'Γ': 'G  Scope         ',
    'ɢ': 'Γ  Grammar       ',
    CRIT_KEY: 'Φ  Criticality   ',
    'Ħ': 'H  Temporal Depth',
    'Σ': 'S  Stoichiometry ',
    'Ω': 'Ω  Winding       ',
}

_OLD_NAMES = {v: k for k, v in OLD_ID_MAP.items()}  # canonical → first old name

def _friendly(glyph_id):
    """⊙_ÿ → Phi_c (the most readable old name if available)."""
    # convert φ̂_X → ⊙_X for lookup
    lookup = glyph_id.replace(CRIT_KEY + '_', '⊙_')
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
        val = entry.get(f, '─')
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
    print(f"{'─'*60}\n")

# ── commands ──────────────────────────────────────────────────────────────────

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
        crit = e.get(CRIT_KEY, '')
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
    # Show differing fields
    ta, tb = entry_tuple(a), entry_tuple(b)
    diffs = [(f, va, vb) for f, va, vb in zip(_FIELDS, ta, tb) if va != vb]
    if diffs:
        print(f"\n  Differing fields ({len(diffs)}):")
        for f, va, vb in diffs:
            label = _FIELD_LABELS.get(f, f).split()[0]
            print(f"    {label}: {va} → {vb}")
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
    print()

def cmd_audio(args):
    import subprocess
    cat = load_catalog(args.catalog)
    entry = find_entry(cat, args.key)
    name = entry.get('name', f"chapter_{args.key}")
    out = getattr(args, 'output', None) or f"{name}.wav"
    dur = getattr(args, 'dur', 0.75)
    ids = get_ids(entry)
    # write a temp catalog entry-like call to imscribeaudio
    tuple_str = ' '.join(ids)
    script = os.path.join(_HERE, 'imscribeaudio.py')
    cmd = [sys.executable, script, '--tuple', tuple_str, '--output', out, '--dur', str(dur)]
    print(f"Sonifying: {entry.get('title', name)}")
    print(f"Tuple: {tuple_str}")
    subprocess.run(cmd)

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
    for f, gid in zip(_FIELDS, [entry.get(f,'') for f in _FIELDS]):
        friendly = _friendly(gid)
        label = _FIELD_LABELS.get(f, f).strip()
        print(f"  {label}: {friendly}")
    if notes:
        print(f"\nStructural note:\n  {notes}")
    print("""
Rewrite instructions:
  The crystal address above is the structural type of this passage.
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
    - Does the temporal depth match (dry, shallow, deep, infinite)?
    - Does the stoichiometry match (one voice, many, asymmetric)?
    - Does the winding match (open, cyclic, returning)?
""")

# ── scaffold ──────────────────────────────────────────────────────────────────

_SCAFFOLD_TEMPLATE = '''\
#!/usr/bin/env python3
"""Generate {name}.json — imscribed catalog for {name}.
Fill in the entries below, then run:
    python3 esoteric_library/gen_{name}.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pre-migration criticality key (compatible with imscribeaudio.py)
PHI = 'φ̂'

# ---------------------------------------------------------------------------
# Available glyph IDs — field order: Ð Þ Ř Φ ƒ Ç Γ ɢ [φ̂=crit] Ħ Σ Ω
#
#   Ð  Dimensionality : Ð_ß  Ð_C  Ð_;  Ð_ω
#   Þ  Topology       : Þ_6  Þ_K  Þ_ò  Þ_¨  Þ_O
#   Ř  Relational     : Ř_¯  Ř_ý  Ř_Ť  Ř_=
#   Φ  Polarity       : Φ_ɐ  Φ_υ  Φ_F  Φ_˙  Φ_}}
#   ƒ  Fidelity       : ƒ_ì  ƒ_ð  ƒ_ż
#   Ç  Kinetics       : Ç_-  Ç_W  Ç_@  Ç_Ù  Ç_λ
#   Γ  Scope          : Γ_β  Γ_γ  Γ_ʔ
#   ɢ  Grammar        : ɢ_^  ɢ_˝  ɢ_ˌ  ɢ_Ş
#   φ̂  Criticality    : φ̂_ž  φ̂_ÿ  φ̂_Æ  φ̂_3  φ̂_Ţ
#   Ħ  Temporal Depth : Ħ_Ñ  Ħ_£  Ħ_A  Ħ_!
#   Σ  Stoichiometry  : Σ_S  Σ_ő  Σ_ï
#   Ω  Winding        : Ω_Å  Ω_2  Ω_z  Ω_5
#
# Tier heuristic (boundary fields: Φ, D, φ̂, Ω):
#   T_0   : φ̂_ž, D compact/infty, Φ not Frobenius
#   T_1   : φ̂_ÿ, Φ not Frobenius
#   T_2   : φ̂_ÿ/φ̂_Æ, Φ not Frobenius, Ω winding
#   T_3   : φ̂_Æ/φ̂_3, any Φ, Ω winding
#   T_inf : φ̂_3 or (φ̂_ÿ + Φ_}}) — Frobenius + EP
# ---------------------------------------------------------------------------

def entry(num, title, desc, text,
          D, T, R, P, F, K, G, Gm, C, H, S, Om,
          tier, cscore, notes=""):
    return {{
        "name": f"{name}_{{num:02d}}",
        "number": num,
        "title": title,
        "description": desc,
        "text": text,
        "Ð": D, "Þ": T, "Ř": R, "Φ": P, "ƒ": F,
        "Ç": K, "Γ": G, "ɢ": Gm, PHI: C,
        "Ħ": H, "Σ": S, "Ω": Om,
        "tier": tier, "C_score": cscore, "notes": notes,
    }}

# ---------------------------------------------------------------------------
# Fill in one entry per section/verse. Arguments:
#   entry(number, title, description, text,
#         D,    T,    R,    P,    F,    K,    G,    Gm,   Crit, H,    S,    Omega,
#         tier, C_score, notes="...")
# ---------------------------------------------------------------------------

chapters = [
    entry(1, "Section title",
        "One-line description of the structural claim",
        "Verbatim source text for this section.",
        "Ð_ω","Þ_O","Ř_Ť","Φ_}}","ƒ_ì","Ç_@","Γ_ʔ","ɢ_^","φ̂_3","Ħ_!","Σ_S","Ω_z",
        "T_inf", 0.95,
        "Why these coordinates: ..."),

    # entry(2, ...),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "{name}.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Wrote {{len(chapters)}} entries → {{out}}")
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
    print(f"  python3 esoteric_librarian.py show {name} 1")

# ── imscribe (auto-assign via LLM loop) ──────────────────────────────────────

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

    # Split text into sections (blank-line separated paragraphs)
    sections = [s.strip() for s in text.split('\n\n') if s.strip()] if text else []
    multi = len(sections) > 1

    # Resolve writable catalog path
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
        # One focused loop per section — saves results incrementally
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
                # fuzzy match
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
        if getattr(args, 'tier',  ''):
            entry['tier']  = args.tier
        if getattr(args, 'notes', ''):
            entry['notes'] = args.notes

        catalog.append(entry)
        _save_catalog(catalog)
        print(f"\nSaved '{name}' to {cat_path}  ({len(catalog)} entries total)")
        show_entry(entry)


# ── add ───────────────────────────────────────────────────────────────────────

def cmd_add(args):
    # resolve catalog path (only esoteric_library files are writable)
    name = args.catalog.lower().replace(' ', '_').replace('-', '_')
    lib_dir = os.path.join(_HERE, 'esoteric_library')
    cat_path = os.path.join(lib_dir, f'{name}.json')

    if not os.path.exists(cat_path):
        # create an empty catalog if it doesn't exist
        with open(cat_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        print(f"Created new catalog: {cat_path}")

    with open(cat_path, encoding='utf-8') as f:
        catalog = json.load(f)

    # parse the tuple
    raw = args.tuple.replace(',', ' ').split()
    if len(raw) != 12:
        sys.exit(f"Error: --tuple requires exactly 12 glyph IDs, got {len(raw)}")

    # map positional fields to keys
    field_keys = ['Ð', 'Þ', 'Ř', 'Φ', 'ƒ', 'Ç', 'Γ', 'ɢ', CRIT_KEY, 'Ħ', 'Σ', 'Ω']
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
        entry[key] = val
    if args.tier:
        entry['tier'] = args.tier
    if args.cscore is not None:
        entry['C_score'] = args.cscore
    if args.notes:
        entry['notes'] = args.notes

    # check for duplicate name
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
    s.add_argument('catalog', help='Catalog name: tao, ig')
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
    s.add_argument('catalog', help='Target catalog name (e.g. tao, upanishads)')
    s.add_argument('--name', '-n', required=True, help='Unique entry name')
    s.add_argument('--number', type=int, default=None, help='Section/chapter number')
    s.add_argument('--title', default='', help='Section title')
    s.add_argument('--description', '--desc', default='', help='One-line description')
    s.add_argument('--text', default='', help='Verbatim source text to imscribe')
    s.add_argument('--file', '-f', default=None, help='Path to text file to imscribe (alternative to --text)')
    s.add_argument('--tier', default='', help='Tier override (optional)')
    s.add_argument('--notes', default='', help='Structural notes override (optional)')
    s.add_argument('--provider', default='anthropic',
                   help='LLM provider: anthropic, openai, deepseek, gemini, … (default: anthropic)')
    s.add_argument('--model', default=None, help='Model ID override')

    # add
    s = sub.add_parser('add', help='Append one entry to a catalog (manual --tuple required)')
    s.add_argument('catalog', help='Target catalog name (e.g. tao, upanishads)')
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
