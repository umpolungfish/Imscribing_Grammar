#!/usr/bin/env python3
"""
Imscribing Grammar — Audio CLI

Modes:
  imscribeaudio.py --all
      Full 49-symbol sequence → imscribing_all_symbols.wav

  imscribeaudio.py <base> <sub>
      Single symbol, e.g.:  imscribeaudio.py ⊙ ž

  imscribeaudio.py --tuple "Ð_ß Þ_6 Ř_¯ Φ_F ƒ_ì Ç_- Γ_ʔ ɢ_^ ⊙_ž Ħ_Ñ Σ_S Ω_Å"
      12-primitive Imscription tuple → WAV with each primitive in sequence
      Accepts space- or comma-separated glyph IDs (canonical or old Lean names).

  imscribeaudio.py --name psychedelic_baseline
      Named entry from IG_catalog.json

  imscribeaudio.py --list
      Print all 49 canonical glyph IDs.
"""

import sys
import os
import json
import re
import argparse
import numpy as np
from scipy.io import wavfile

# ---- import library --------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sounds import (
    synthesize_symbol, normalize, symbol_list,
    PRIMITIVE_MAP, OLD_ID_MAP, FIELD_ORDER, resolve_id,
)

# ============================================================================
# Catalog helpers
# ============================================================================
_CATALOG_PATH = os.path.join(_HERE, 'IG_catalog.json')
_CRIT_OLD_KEY = 'φ̂'   # pre-migration criticality field name in catalog

def _load_catalog():
    with open(_CATALOG_PATH, encoding='utf-8') as f:
        return json.load(f)

def _catalog_entry_to_ids(entry):
    """Return list of 12 canonical glyph IDs from a catalog entry dict."""
    ids = []
    for field in FIELD_ORDER:
        if field == '⊙' and '⊙' not in entry:
            raw = entry.get(_CRIT_OLD_KEY, '')
            # φ̂_ž → ⊙_ž
            raw = raw.replace(_CRIT_OLD_KEY + '_', '⊙_')
        else:
            raw = entry.get(field, '')
        ids.append(raw)
    return ids

def _find_catalog_entry(name):
    catalog = _load_catalog()
    for entry in catalog:
        if entry.get('name') == name:
            return entry
    return None

# ============================================================================
# Audio assembly
# ============================================================================
def build_sequence(ids, fs=44100, dur=0.75, gap_s=0.12):
    """ids: list of canonical glyph ID strings → concatenated waveform."""
    gap = np.zeros(int(gap_s * fs))
    sequence = np.array([])
    errors = []
    for gid in ids:
        pair = resolve_id(gid)
        if pair is None:
            errors.append(gid)
            sequence = np.concatenate([sequence, np.zeros(int(dur * fs)), gap])
        else:
            sig = synthesize_symbol(pair[0], pair[1], fs, dur)
            sequence = np.concatenate([sequence, sig, gap])
    return normalize(sequence, peak=0.9), errors

def save_wav(path, sequence, fs=44100):
    wavfile.write(path, fs, (sequence * 32767).astype(np.int16))

def _sanitize(s):
    return re.sub(r'[<>:"/\\|?*]', '_', s) if s else 'unknown'

# ============================================================================
# CLI
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('base', nargs='?', help='Base glyph (single-symbol mode)')
    parser.add_argument('sub',  nargs='?', help='Subscript (single-symbol mode)')

    parser.add_argument('--all',   action='store_true',
                        help='Generate the full 49-symbol sequence')
    parser.add_argument('--tuple', '-t', metavar='IDS',
                        help='12-primitive tuple, space- or comma-separated glyph IDs')
    parser.add_argument('--name', '-n', metavar='NAME',
                        help='Named Imscription from IG_catalog.json')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all 49 canonical glyph IDs and exit')

    parser.add_argument('--dur',  '-d', type=float, default=0.75,
                        help='Duration per symbol in seconds (default: 0.75)')
    parser.add_argument('--fs',         type=int,   default=44100,
                        help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--output', '-o', metavar='FILE',
                        help='Output WAV filename (default: auto)')

    args = parser.parse_args()

    # ---- --list ------------------------------------------------------------
    if args.list:
        print("Canonical glyph IDs (field order: Ð Þ Ř Φ ƒ Ç Γ ɢ ⊙ Ħ Σ Ω)\n")
        for gid in PRIMITIVE_MAP:
            print(f"  {gid}")
        return

    # ---- --all -------------------------------------------------------------
    if args.all:
        if args.base or args.sub or args.tuple or args.name:
            parser.error("--all cannot be combined with other mode flags")
        print("Generating full 49-symbol sequence…")
        fs = args.fs
        gap = np.zeros(int(0.12 * fs))
        sequence = np.array([])
        for base, sub in symbol_list:
            sig = synthesize_symbol(base, sub, fs, dur=args.dur)
            sequence = np.concatenate([sequence, sig, gap])
        sequence = normalize(sequence, peak=0.9)
        out = args.output or 'imscribing_all_symbols.wav'
        save_wav(out, sequence, fs)
        print(f"Saved {out}  ({len(symbol_list)} symbols)")
        return

    # ---- --name ------------------------------------------------------------
    if args.name:
        if args.base or args.sub or args.tuple:
            parser.error("--name cannot be combined with other mode flags")
        entry = _find_catalog_entry(args.name)
        if entry is None:
            sys.exit(f"Error: '{args.name}' not found in IG_catalog.json")
        ids = _catalog_entry_to_ids(entry)
        print(f"Imscription for '{args.name}':")
        print("  " + "  ".join(ids))
        sequence, errors = build_sequence(ids, fs=args.fs, dur=args.dur)
        if errors:
            print(f"Warning: unrecognised IDs skipped: {errors}")
        out = args.output or f"{_sanitize(args.name)}.wav"
        save_wav(out, sequence, args.fs)
        print(f"Saved {out}")
        return

    # ---- --tuple -----------------------------------------------------------
    if args.tuple:
        if args.base or args.sub:
            parser.error("--tuple cannot be combined with positional base/sub")
        raw = args.tuple.replace(',', ' ')
        ids = raw.split()
        if len(ids) != 12:
            sys.exit(f"Error: --tuple requires exactly 12 IDs, got {len(ids)}: {ids}")
        print("Tuple: " + "  ".join(ids))
        sequence, errors = build_sequence(ids, fs=args.fs, dur=args.dur)
        if errors:
            print(f"Warning: unrecognised IDs skipped (silence substituted): {errors}")
        if args.output:
            out = args.output
        else:
            slug = '_'.join(_sanitize(i) for i in ids[:3])
            out = f"tuple_{slug}_etc.wav"
        save_wav(out, sequence, args.fs)
        print(f"Saved {out}  (12 primitives, {args.dur}s each @ {args.fs} Hz)")
        return

    # ---- single symbol -----------------------------------------------------
    if args.base and args.sub:
        # normalize common substitutions
        sub_norm = {'¯': '̄', '^': '∧', '˙': '̇'}
        sub = sub_norm.get(args.sub, args.sub)
        sig = synthesize_symbol(args.base, sub, fs=args.fs, dur=args.dur)
        if args.output:
            out = args.output
        else:
            b = _sanitize(args.base)
            s = _sanitize(args.sub)
            out = f"{b}_{s}.wav"
        save_wav(out, sig, args.fs)
        print(f"Saved {out}  ({args.base}{args.sub}, {args.dur}s @ {args.fs} Hz)")
        return

    parser.print_help()

if __name__ == '__main__':
    main()
