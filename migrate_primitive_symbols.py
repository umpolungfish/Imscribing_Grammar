#!/usr/bin/env python3
"""
Migrate all imscribing_grammar files to the new 12-primitive phonetic symbol notation.

Old → New:
  D     → Ð  (U+00D0  eth)
  T     → Þ  (U+00DE  thorn)
  R     → Ř  (U+0158  caron-r)
  P     → Φ  (U+03A6  phi)
  F     → ƒ  (U+0192  script-f)
  K     → Ç  (U+00C7  cedilla-c)
  G     → Γ  (U+0393  gamma)
  Gamma → ɢ  (U+0262  small-cap G)
  Phi   → φ̂  (U+03C6 + U+0302  phi + combining circumflex)
  H     → Ħ  (U+0126  h-bar)
  S     → Σ  (U+03A3  sigma)
  Omega → Ω  (U+03A9  omega)

Strategy:
  - JSON files: rename field keys + migrate all primitive value strings
  - Python files: migrate quoted string literals only (enum member names stay ASCII)
  - Markdown / TeX / other text: migrate all occurrences of primitive value strings
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Mapping: old JSON field key → new symbol
# Longer / more-specific entries FIRST (Gamma before G, Phi before P, Omega before O)
# ---------------------------------------------------------------------------
JSON_KEY_MAP: list[tuple[str, str]] = [
    ("Gamma", "ɢ"),
    ("Phi",   "φ̂"),
    ("Omega", "Ω"),
    ("D",     "Ð"),
    ("T",     "Þ"),
    ("R",     "Ř"),
    ("P",     "Φ"),
    ("F",     "ƒ"),
    ("K",     "Ç"),
    ("G",     "Γ"),
    ("H",     "Ħ"),
    ("S",     "Σ"),
]

# ---------------------------------------------------------------------------
# Mapping: old primitive value prefix → new symbol prefix
# Longer / more-specific FIRST
# ---------------------------------------------------------------------------
VALUE_PREFIXES: list[tuple[str, str]] = [
    ("Gamma_", "ɢ_"),
    ("Phi_",   "φ̂_"),
    ("Omega_", "Ω_"),
    ("D_",     "Ð_"),
    ("T_",     "Þ_"),
    ("R_",     "Ř_"),
    ("P_",     "Φ_"),
    ("F_",     "ƒ_"),
    ("K_",     "Ç_"),
    ("G_",     "Γ_"),
    ("H_",     "Ħ_"),
    ("S_",     "Σ_"),
]

SKIP_DIRS = {".venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", ".lake"}
# Files where we already use new symbols (skip to avoid double-migration)
SKIP_FILES = {"migrate_primitive_symbols.py", ".llm_cache.json"}

TEXT_EXTENSIONS = {".py", ".md", ".tex", ".json", ".yaml", ".txt", ".rst"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def migrate_value_str(s: str) -> str:
    """Apply prefix mapping to a single primitive value string."""
    for old, new in VALUE_PREFIXES:
        if s.startswith(old):
            return new + s[len(old):]
    return s


def _already_migrated(text: str) -> bool:
    """Quick check: if the new symbols are present and old are absent, skip."""
    has_new = any(new in text for _, new in VALUE_PREFIXES if len(new) > 2)
    has_old = any(f'"{old}' in text or f"'{old}" in text
                  for old, _ in VALUE_PREFIXES)
    return has_new and not has_old


# ---------------------------------------------------------------------------
# JSON catalog migration (handles key rename + value migration)
# ---------------------------------------------------------------------------

def migrate_json_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  SKIP (invalid JSON): {path.name} — {e}")
        return False

    is_list = isinstance(data, list)
    entries = data if is_list else list(data.values())

    changed = False
    new_entries: list[dict] = []
    for entry in entries:
        if not isinstance(entry, dict):
            new_entries.append(entry)
            continue
        new_entry: dict = {}
        for k, v in entry.items():
            # Rename key
            new_k = k
            for old_k, new_k_sym in JSON_KEY_MAP:
                if k == old_k:
                    new_k = new_k_sym
                    if new_k != k:
                        changed = True
                    break
            # Migrate string value
            new_v = v
            if isinstance(v, str):
                new_v = migrate_value_str(v)
                if new_v != v:
                    changed = True
            new_entry[new_k] = new_v
        new_entries.append(new_entry)

    if not changed:
        return False

    with open(path, "w", encoding="utf-8") as f:
        if is_list:
            json.dump(new_entries, f, indent=2, ensure_ascii=False)
        else:
            # Reconstruct dict keyed by name
            out = {e.get("name", i): e for i, e in enumerate(new_entries)}
            json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return True


# ---------------------------------------------------------------------------
# Python file migration (quoted strings only)
# ---------------------------------------------------------------------------

# Match "X_name" or 'X_name' where X_ is an old prefix
_PY_PATTERN = re.compile(
    r'(["\'])('
    + "|".join(re.escape(old) for old, _ in VALUE_PREFIXES)
    + r')([A-Za-z][A-Za-z0-9_]*)(\1)'
)

def _py_replacer(m: re.Match) -> str:
    quote, old_prefix, tail, _ = m.group(1), m.group(2), m.group(3), m.group(4)
    new_prefix = next(new for old, new in VALUE_PREFIXES if old == old_prefix)
    return quote + new_prefix + tail + quote


def migrate_python_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text = _PY_PATTERN.sub(_py_replacer, text)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Generic text file migration (markdown, tex, yaml, txt)
# ---------------------------------------------------------------------------

_BARE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(re.escape(old) + r'([A-Za-z][A-Za-z0-9_]*)'), new)
    for old, new in VALUE_PREFIXES
]

def migrate_text_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text = text
    for pattern, new_prefix in _BARE_PATTERNS:
        new_text = pattern.sub(new_prefix + r'\1', new_text)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def should_skip(path: Path) -> bool:
    return (
        path.name in SKIP_FILES
        or any(part in SKIP_DIRS for part in path.parts)
        or not path.is_file()
    )


def main(dry_run: bool = False) -> None:
    stats = {"json": 0, "python": 0, "text": 0, "skipped": 0}

    for path in sorted(ROOT.rglob("*")):
        if should_skip(path):
            continue
        if path.suffix not in TEXT_EXTENSIONS:
            continue

        rel = path.relative_to(ROOT)

        if path.suffix == ".json":
            if dry_run:
                print(f"  [DRY] json  {rel}")
            else:
                changed = migrate_json_file(path)
                if changed:
                    print(f"  json   {rel}")
                    stats["json"] += 1
        elif path.suffix == ".py":
            if dry_run:
                print(f"  [DRY] py    {rel}")
            else:
                changed = migrate_python_file(path)
                if changed:
                    print(f"  py     {rel}")
                    stats["python"] += 1
        else:
            if dry_run:
                print(f"  [DRY] text  {rel}")
            else:
                changed = migrate_text_file(path)
                if changed:
                    print(f"  text   {rel}")
                    stats["text"] += 1

    if not dry_run:
        print(f"\nDone: {stats['json']} JSON, {stats['python']} Python, {stats['text']} text files updated.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
