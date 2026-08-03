#!/usr/bin/env python3
"""
fix_catalog_encoding.py — normalize all three encoding errors in IG_catalog.json.

  Category 1 — Legacy key names (D,T,R,P,F,K,G,Gamma,Phi,H,S,Omega)
                → rename to canonical glyph keys (⊢,⊣,>,<,⋈,⊤,∋,∈,⊙,Ħ,Σ,Ω)
                  Values are already Shavian; only keys need renaming.

  Category 2 — Tuple notation  (tuple: '𐑼;𐑸;𐑾;...')
                → parse into flat dict using OLD_TO_SHAVIAN, then drop 'tuple' key.

  Category 3 — Symbol_symbol values (𐑗, 𐑭, ⊙, ...)
                → translate each value via OLD_TO_SHAVIAN.

  Category 4 — UNDEFINED tuple  (tuple: 'UNDEFINED;...')
                → cannot fix; left unchanged, flagged in output.

Usage:
  uv run python3 scripts/fix_catalog_encoding.py [--dry-run] [--catalog PATH]
"""
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── Symbol_symbol → Shavian map (from migrate_models_shavian.py) ────────────
OLD_TO_SHAVIAN = {
    "𐑛": "𐑛", "𐑨": "𐑨", "𐑼": "𐑼", "𐑦": "𐑦",
    "𐑡": "𐑡", "𐑰": "𐑰", "𐑥": "𐑥", "𐑶": "𐑶", "𐑸": "𐑸",
    "𐑩": "𐑩", "𐑑": "𐑑", "𐑽": "𐑽", "𐑾": "𐑾",
    "𐑗": "𐑗", "𐑿": "𐑿", "𐑬": "𐑬", "𐑯": "𐑯", "𐑹": "𐑹",
    "⋈^ì": "𐑱", "⋈^ð": "𐑞", "⋈^ż": "𐑐",
    "⊤^-": "𐑘", "⊤^W": "𐑤", "⊤^@": "𐑧", "⊤^Ù": "𐑪", "⊤^λ": "𐑺",
    "𐑚": "𐑚", "𐑔": "𐑔", "𐑲": "𐑲",
    "∋^∧": "𐑝", "∋^˝": "𐑜", "∋^ˌ": "𐑠", "∋^Ş": "𐑵",
    "𐑢": "𐑢", "⊙": "⊙", "𐑮": "𐑮", "𐑻": "𐑻", "𐑣": "𐑣",
    "𐑓": "𐑓", "𐑒": "𐑒", "𐑖": "𐑖", "𐑫": "𐑫",
    "𐑙": "𐑙", "𐑕": "𐑕", "𐑳": "𐑳",
    "𐑷": "𐑷", "𐑴": "𐑴", "𐑭": "𐑭", "𐑟": "𐑟",
}

# Also accept _ separator for primitives that use ^ in OLD_TO_SHAVIAN
_UNIFIED = dict(OLD_TO_SHAVIAN)
for k, v in list(OLD_TO_SHAVIAN.items()):
    if "^" in k:
        prim, val = k.split("^", 1)
        _UNIFIED[f"{prim}_{val}"] = v

# ── Legacy key → canonical glyph key ────────────────────────────────────────
LEGACY_KEY_MAP = {
    "D":     "⊢",
    "T":     "⊣",
    "R":     ">",
    "P":     "<",
    "F":     "⋈",
    "K":     "⊤",
    "G":     "∋",
    "Gamma": "∈",
    "Phi":   "⊙",
    "H":     "⊥",
    "S":     "⊞",
    "Omega": "◻",
}

# Old Criticality glyph → canonical
PRIM_GLYPH_NORM = {"φ̂": "⊙"}

# Canonical prim glyphs for regex split
_PRIMS = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "φ̂", "⊥", "⊞", "◻"]
_PRIM_PAT = "|".join(re.escape(p) for p in sorted(_PRIMS, key=len, reverse=True))
_TUPLE_SPLIT = re.compile(f';(?={_PRIM_PAT})')


def _translate_value(prim_canonical: str, raw_val: str) -> str:
    """Translate a raw (possibly Symbol_symbol) value to a Shavian glyph.
    Returns raw_val unchanged if already canonical or unknown.

    Handles two sub-cases:
      A. raw_val is the full Symbol_symbol form (e.g. '𐑧') — direct lookup
      B. raw_val is just the suffix part (e.g. '@') — prim prefix prepended
    """
    from imscrbgrmr.canonical_primitives import ORDINALS
    # Already Shavian
    if raw_val in ORDINALS.get(prim_canonical, {}):
        return raw_val
    # Case A: raw_val is the full token (e.g. "𐑧", "𐑭")
    if raw_val in _UNIFIED:
        return _UNIFIED[raw_val]
    # Case B: raw_val is the suffix — construct with prim prefix
    key_underscore = f"{prim_canonical}_{raw_val}"
    key_caret = f"{prim_canonical}^{raw_val}"
    if key_underscore in _UNIFIED:
        return _UNIFIED[key_underscore]
    if key_caret in _UNIFIED:
        return _UNIFIED[key_caret]
    return raw_val  # unknown — leave as-is


def fix_legacy_keys(entry: dict) -> tuple[dict, list]:
    """Rename legacy key names to canonical glyph keys."""
    e = deepcopy(entry)
    changes = []
    for old_key, new_key in LEGACY_KEY_MAP.items():
        if old_key in e:
            val = e.pop(old_key)
            e[new_key] = val
            changes.append(f"key {old_key!r} → {new_key!r}")
    return e, changes


def fix_symbol_symbol_values(entry: dict) -> tuple[dict, list]:
    """Translate Symbol_symbol values in canonical-glyph-keyed entries."""
    from imscrbgrmr.canonical_primitives import ORDINALS
    e = deepcopy(entry)
    changes = []
    for prim in list(LEGACY_KEY_MAP.values()):  # all 12 canonical keys
        val = e.get(prim)
        if val is None:
            continue
        if val in ORDINALS.get(prim, {}):
            continue  # already Shavian
        # Try to translate
        translated = _translate_value(prim, val)
        if translated != val:
            e[prim] = translated
            changes.append(f"{prim}: {val!r} → {translated!r}")
    return e, changes


def parse_tuple(entry: dict) -> tuple[dict, list, bool]:
    """Parse tuple: '𐑼;𐑸;...' into flat primitive dict.
    Returns (fixed_entry, changes, skipped_undefined)."""
    e = deepcopy(entry)
    raw = e.get("tuple", "")

    if "UNDEFINED" in str(raw):
        return e, [], True  # cannot fix

    # Split on ; only before a known prim glyph
    parts = _TUPLE_SPLIT.split(raw.strip())
    # Filter empty strings
    parts = [p for p in parts if p.strip()]

    changes = []
    parsed = {}
    for part in parts:
        # Split on first _ to get prim and value
        if "_" not in part:
            continue
        idx = part.index("_")
        prim_raw = part[:idx]
        val_raw = part[idx+1:]  # may be empty if value IS the _ char... edge case

        # Normalize prim glyph
        prim = PRIM_GLYPH_NORM.get(prim_raw, prim_raw)

        # The val_raw might be a single special char (like ';'), a Shavian char, or a Symbol_symbol suffix
        shavian = _translate_value(prim, val_raw)
        parsed[prim] = shavian
        changes.append(f"tuple {prim}_{val_raw!r} → {prim}: {shavian!r}")

    if len(parsed) == 12:
        # Successfully parsed all 12 — replace tuple with flat dict
        del e["tuple"]
        e.update(parsed)
    elif parsed:
        # Partial parse — add what we got, keep tuple for inspection
        e.update(parsed)
        changes.append(f"WARNING: only parsed {len(parsed)}/12 primitives from tuple")

    return e, changes, False


# ── Main fix logic ───────────────────────────────────────────────────────────

def fix_entry(entry: dict) -> tuple[dict, list, str]:
    """
    Fix a single catalog entry. Returns (fixed, changes, category).
    category: 'legacy_keys' | 'tuple' | 'symbol_symbol' | 'undefined' | 'ok'
    """
    from imscrbgrmr.canonical_primitives import ORDINALS

    keys = set(entry.keys()) - {"name", "description", "justification", "tuple"}
    legacy_keys = set(LEGACY_KEY_MAP.keys())
    canonical_glyphs = set(LEGACY_KEY_MAP.values())

    if entry.get("tuple"):
        raw = entry["tuple"]
        if "UNDEFINED" in str(raw):
            return entry, [], "undefined"
        fixed, changes, skipped = parse_tuple(entry)
        return fixed, changes, "tuple"

    if keys & legacy_keys:
        fixed, changes = fix_legacy_keys(entry)
        return fixed, changes, "legacy_keys"

    if keys & canonical_glyphs:
        # Check if any values are Symbol_symbol (not in ORDINALS)
        needs_fix = False
        for prim in canonical_glyphs:
            val = entry.get(prim)
            if val and val not in ORDINALS.get(prim, {}):
                needs_fix = True
                break
        if needs_fix:
            fixed, changes = fix_symbol_symbol_values(entry)
            return fixed, changes, "symbol_symbol"

    return entry, [], "ok"


def fix_catalog(entries: list) -> tuple[list, dict]:
    fixed_entries = []
    report = {"legacy_keys": [], "tuple": [], "symbol_symbol": [],
              "undefined": [], "ok": 0}

    for entry in entries:
        fixed, changes, category = fix_entry(entry)
        fixed_entries.append(fixed)
        name = entry.get("name", "?")

        if category == "ok":
            report["ok"] += 1
        elif category == "undefined":
            report["undefined"].append(name)
            print(f"  SKIP (UNDEFINED): {name}")
        else:
            report[category].append((name, changes))
            print(f"  FIX [{category}]: {name}")
            for c in changes[:5]:
                print(f"    {c}")
            if len(changes) > 5:
                print(f"    ... ({len(changes)} total changes)")

    return fixed_entries, report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix catalog encoding errors")
    parser.add_argument("--catalog", default="data/IG_catalog.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    with open(catalog_path) as f:
        data = json.load(f)

    is_list = isinstance(data, list)
    entries = data if is_list else list(data.values())

    print(f"Fixing {len(entries)} catalog entries...\n")
    fixed_entries, report = fix_catalog(entries)

    print(f"\n── Summary ──")
    print(f"  Already canonical:  {report['ok']}")
    print(f"  Legacy keys fixed:  {len(report['legacy_keys'])}")
    print(f"  Tuple parsed:       {len(report['tuple'])}")
    print(f"  Symbol_symbol fixed:{len(report['symbol_symbol'])}")
    print(f"  UNDEFINED (skipped):{len(report['undefined'])} — {report['undefined']}")

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    out_path = Path(args.output) if args.output else catalog_path
    out_data = fixed_entries if is_list else dict(zip(data.keys(), fixed_entries))
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
