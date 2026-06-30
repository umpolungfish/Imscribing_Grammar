"""catalog_cleaner.py — continuous janitor for ~/.imscrbgrmr/catalog.json

Watches the live catalog for dirty entries (trailing commas, editorial
parentheticals, paren suffixes) and removes them on every write.
Runs until killed.
"""
import json, re, sys, time, os
from pathlib import Path

LIVE   = Path.home() / ".imscrbgrmr" / "catalog.json"
IG     = Path(__file__).parent / "IG_catalog.json"

EDITORIAL = re.compile(
    r'\b(?:already|not[_\s]+standard|not[_\s]+a[_\s]+paradox|not[_\s]+always|'
    r'paradox[_\s]+like|paradox-like|fable|variant[_\s]+of[_\s]+barber|'
    r'not[_\s]+strictly|already[_\s]+listed|skip)\b'
    r'|[—–][_\s]*already|\(goodman[^)]*already'
    r'|\(conjecture\)',
    re.IGNORECASE,
)
PAREN_SUFFIX = re.compile(r'_\([^)]*\)$')

def strip_name(name: str) -> str:
    n = name.rstrip(',').rstrip()
    while PAREN_SUFFIX.search(n):
        n = PAREN_SUFFIX.sub('', n)
    return n

def clean(path: Path) -> tuple[int, int, int]:
    """Return (removed, renamed, kept). Returns (0,0,0) if nothing to do."""
    try:
        with open(path) as f:
            raw = json.load(f)
    except Exception:
        return 0, 0, 0

    is_dict = isinstance(raw, dict) and 'imscriptions' in raw
    entries = raw['imscriptions'] if is_dict else raw

    # Load IG names for dedup
    try:
        with open(IG) as f:
            ig_entries = json.load(f)
        ig_names = {e.get('name','') for e in ig_entries if isinstance(e, dict)}
    except Exception:
        ig_names = set()

    seen: set[str] = set()
    result = []
    removed = renamed = kept = 0

    for e in entries:
        if not isinstance(e, dict):
            result.append(e)
            continue
        name = e.get('name', '')
        base = name.rstrip(',').rstrip()

        if EDITORIAL.search(base):
            removed += 1
            continue

        new_name = strip_name(base)

        if new_name in seen or new_name in ig_names:
            removed += 1
            continue

        seen.add(new_name)
        if new_name != name:
            e = dict(e)
            e['name'] = new_name
            renamed += 1
        else:
            kept += 1
        result.append(e)

    if removed == 0 and renamed == 0:
        return 0, 0, kept

    out = dict(raw, imscriptions=result) if is_dict else result
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"[cleaner] write error: {exc}", flush=True)
        return 0, 0, 0

    return removed, renamed, kept


def watch(path: Path, interval: float = 2.0):
    last_mtime = 0.0
    last_size  = 0
    print(f"[cleaner] watching {path} (interval={interval}s)", flush=True)
    while True:
        try:
            st = path.stat()
            mtime, size = st.st_mtime, st.st_size
        except FileNotFoundError:
            time.sleep(interval)
            continue

        if mtime != last_mtime or size != last_size:
            last_mtime, last_size = mtime, size
            removed, renamed, kept = clean(path)
            if removed or renamed:
                print(
                    f"[cleaner] cleaned: -{removed} editorial/dup, "
                    f"~{renamed} renamed, {kept} clean | "
                    f"total {kept + renamed}",
                    flush=True,
                )

        time.sleep(interval)


if __name__ == "__main__":
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
    watch(LIVE, interval)
