_CRIT_LEGACY = '\u03c6\u0302'  # φ̂
_CRIT_MODERN = '\u2299'         # ⊙

def _read_crit(entry):
    """Read criticality from entry, accepting ⊙ or φ̂ key. Returns ⊙_* form."""
    import unicodedata
    raw = entry.get(_CRIT_LEGACY, entry.get(_CRIT_MODERN, ''))
    raw = unicodedata.normalize('NFC', raw)
    # Normalize φ̂_* -> ⊙_* (sounds.py uses ⊙ base)
    if raw.startswith(_CRIT_LEGACY + '_'):
        return _CRIT_MODERN + raw[len(_CRIT_LEGACY):]
    return raw

def entry_to_ids(entry):
    """Return 12 glyph IDs from catalog entry (normalized to ⊙ form for sounds.py)."""
    ids = []
    for field in FIELD_ORDER:
        if field == _CRIT_MODERN:
            ids.append(_read_crit(entry))
        else:
            raw = entry.get(field, '')
            import unicodedata
            ids.append(unicodedata.normalize('NFC', raw))
    return ids
