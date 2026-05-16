#!/usr/bin/env python3
"""
migrate_to_symbol_ids.py — Replace all phonetic-name subtype IDs with Symbol_symbol IDs.

Canonical mapping: each primitive key + TeX name → primitive key + rendered phonetic char.
Handles both the old gen_final.py names and the current catalog phonetic names.

Run:   uv run migrate_to_symbol_ids.py [--dry-run]
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DRY_RUN = "--dry-run" in sys.argv

# ── Canonical rename table (old → new).  Longer keys must precede shorter
# prefixes to prevent partial matches (e.g. Ω_dzlig before Ω_dz if both existed).
RENAME: list[tuple[str, str]] = [
    # D — Dimensionality
    ("Ð_wynn",               "Ð_ß"),
    ("Ð_turnthree",          "Ð_C"),
    ("Ð_invomega",           "Ð_;"),
    ("Ð_omega",              "Ð_ω"),
    # T — Topology
    ("Þ_nrleg",              "Þ_6"),
    ("Þ_invscr",             "Þ_K"),
    ("Þ_bullseye",           "Þ_ò"),
    ("Þ_commatailz",         "Þ_¨"),
    ("Þ_openo",              "Þ_O"),
    # R — Relational mode
    ("Ř_subrightarrow",      "Ř_¯"),
    ("Ř_ctz",                "Ř_ý"),
    ("Ř_downstep",           "Ř_Ť"),
    ("Ř_lyoghlig",           "Ř_="),
    # P — Parity/Symmetry (pm_sym before pm to avoid partial match)
    ("Φ_doublebarpipe",      "Φ_}"),
    ("Φ_aolig",              "Φ_ɐ"),
    ("Φ_upsilon",            "Φ_υ"),
    ("Φ_pipevar",            "Φ_F"),
    ("Φ_subdoublearrow",     "Φ_˙"),
    # F — Fidelity
    ("ƒ_beltl",              "ƒ_ì"),
    ("ƒ_dh",                 "ƒ_ð"),
    ("ƒ_hardsign",           "ƒ_ż"),
    ("ƒ_hvlig",              "ƒ_ż"),   # old gen_final.py name, same target
    # K — Kinetics
    ("Ç_frtailgamma",        "Ç_-"),
    ("Ç_turnm",              "Ç_W"),
    ("Ç_schwa",              "Ç_@"),
    ("Ç_teshlig",            "Ç_Ù"),
    ("Ç_lambda",             "Ç_λ"),
    # G — Scope/Granularity
    ("Γ_beta",               "Γ_β"),
    ("Γ_gamma",              "Γ_γ"),
    ("Γ_revapostrophe",      "Γ_ʔ"),
    # Gamma — Interaction grammar
    ("ɢ_corner",             "ɢ_^"),
    ("ɢ_spleftarrow",        "ɢ_˝"),
    ("ɢ_secstress",          "ɢ_ˌ"),
    ("ɢ_doublevertline",     "ɢ_Ş"),
    # Phi — Criticality (c_complex before c to avoid partial match)
    ("φ̂_closerevepsilon",   "φ̂_Æ"),
    ("φ̂_softsign",          "φ̂_ž"),
    ("φ̂_ctyogh",            "φ̂_ÿ"),
    ("φ̂_ctc",               "φ̂_ÿ"),   # old gen_final.py name, same target
    ("φ̂_revepsilon",        "φ̂_3"),
    ("φ̂_upstep",            "φ̂_Ţ"),
    # H — Chirality
    ("Ħ_closeomega",         "Ħ_Ñ"),
    ("Ħ_toneletterstem",     "Ħ_£"),
    ("Ħ_turntwo",            "Ħ_A"),
    ("Ħ_invscripta",         "Ħ_!"),
    # S — Stoichiometry
    ("Σ_doublebaresh",       "Σ_S"),
    ("Σ_ctn",                "Σ_ő"),
    ("Σ_ltailm",             "Σ_ï"),
    ("Σ_scn",                "Σ_ï"),   # old gen_final.py name, same target
    # Omega — Topological invariant
    ("Ω_closeepsilon",       "Ω_Å"),
    ("Ω_crtwo",              "Ω_2"),
    ("Ω_dzlig",              "Ω_z"),
    ("Ω_turna",              "Ω_5"),
]

RENAME_DICT = dict(RENAME)


# ── JSON catalog migration ────────────────────────────────────────────────────
def migrate_catalog(path: Path) -> int:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    changes = 0
    for entry in data:
        for key in list(entry.keys()):
            val = entry[key]
            if isinstance(val, str) and val in RENAME_DICT:
                entry[key] = RENAME_DICT[val]
                changes += 1

    if not DRY_RUN:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return changes


# ── Python file migration ────────────────────────────────────────────────────
def migrate_py(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0
    for old, new in sorted(RENAME, key=lambda p: len(p[0]), reverse=True):
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            changes += count
    if not DRY_RUN and text != original:
        path.write_text(text, encoding="utf-8")
    return changes


# ── Targets ──────────────────────────────────────────────────────────────────
CATALOG = ROOT / "IG_catalog.json"
PY_FILES = [
    ROOT / "space_search" / "primitives.py",
    ROOT / "IG_primitive_map.py",
    ROOT / "IG_inquiry.py",
]
DOC_EXTENSIONS = {".md", ".tex", ".txt", ".yaml", ".toml"}
EXCLUDE_DIRS = {ROOT / "space_search" / "data"}  # NANOGrav data: _lambda/_beta are astro params

def find_doc_files() -> list[Path]:
    results = []
    for p in sorted(ROOT.rglob("*")):
        if p.suffix not in DOC_EXTENSIONS:
            continue
        if any(p.is_relative_to(ex) for ex in EXCLUDE_DIRS):
            continue
        if p in PY_FILES:
            continue  # already handled
        results.append(p)
    return results

print(f"{'DRY RUN — ' if DRY_RUN else ''}Migrating to Symbol_symbol IDs")
print(f"  {len(RENAME)} rename pairs")
print()

total = 0

n = migrate_catalog(CATALOG)
print(f"  IG_catalog.json          {n:4d} values replaced")
total += n

for p in PY_FILES:
    if p.exists():
        n = migrate_py(p)
        print(f"  {p.name:30s} {n:4d} occurrences replaced")
        total += n
    else:
        print(f"  {p.name:30s} NOT FOUND")

print()
doc_files = find_doc_files()
doc_total = 0
doc_changed = 0
for p in doc_files:
    n = migrate_py(p)  # same simple str.replace logic works for all text files
    if n:
        rel = p.relative_to(ROOT)
        print(f"  {str(rel):50s} {n:4d}")
        doc_total += n
        doc_changed += 1

print()
print(f"Doc files changed: {doc_changed} / {len(doc_files)}  ({doc_total} replacements)")
total += doc_total
print(f"Total replacements: {total}")
if DRY_RUN:
    print("(dry run — no files written)")
