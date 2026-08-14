#!/usr/bin/env python3
"""
manuscript_zfct.py — ZFCₜ formal expressions for every folio/page/tablet.

For each compiled element (Voynich folio, Rohonc page, Linear A tablet),
derives a per-element 12-primitive tuple from the IMASM instruction
distribution and generates the full ZFCₜ formal set-theory expression
using zfct_navigator.compose_formula + render_tokens.

Per-element primitive derivation
─────────────────────────────────
  Fixed (corpus-level):  ⊢, >, ⋈, ⊤, ∈, ⊙, ◻, < (whole-manuscript)
  Variable (element-level):
    ⊣  — dominant opcode cluster (ENGAGR→K; FSPLIT+FFUSE balanced→¨; IFIX→6)
    <  — FSPLIT:FFUSE balance (exact→}; near→˙; skewed→F; none→ɐ)
    ∋  — broadcast vs sequential vs conjunctive (FSPLIT>>FFUSE→Ş; CLINK→ˌ; VINIT→^)
    ⊥  — instruction count as state-depth proxy (<30→Ñ; <60→£; <120→A; ≥120→!)

Outputs
───────
  manuscript_zfct.json  — structured JSON: corpus → element → {tuple, expression, tokens}
  manuscript_zfct.txt   — human-readable report

Usage
─────
  uv run manuscript_zfct.py [--voynich] [--rohonc] [--linear-a] [--all]
  uv run manuscript_zfct.py --all --out manuscript_zfct
"""

from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# ── path bootstrap ────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / 'rohonc-engine'))
sys.path.insert(0, str(_HERE.parent / 'linear_a_engine'))
sys.path.insert(0, str(_HERE.parent / 'voynich-engine'))

from navigators.zfct_navigator import (
    compose_formula, render_tokens,
    IDX2TOKEN, ZFCT_TEMPLATES, PRIMITIVES, ORDINALS,
)

# ── corpus base tuples ────────────────────────────────────────────────────────
# These are the whole-manuscript imscriptions in zfct_navigator notation.
# Note: zfct_navigator uses "⊙" for criticality (exOS < = IG ⊙).

CORPUS_BASE: dict[str, dict] = {
    'voynich': {
        '⊢': '𐑦', '⊣': '𐑸', '≻': '𐑾',  '≺': '𐑹',
        '⋈': '⋈^ì', '⊤': '⊤^Ù', '∈': '𐑲',  '∋': '∋^Ş',
        '⊙': '⊙', '⊥': '𐑫', '⊞': '𐑙',  '◻': '𐑭',
    },
    'rohonc': {
        '⊢': '𐑨', '⊣': '𐑶', '≻': '𐑽', '≺': '𐑹',
        '⋈': '⋈^ì', '⊤': '⊤^@', '∈': '𐑲', '∋': '∋^ˌ',
        '⊙': '⊙', '⊥': '𐑖', '⊞': '𐑳', '◻': '𐑭',
    },
    'linear_a': {
        '⊢': '𐑨', '⊣': '𐑶', '≻': '𐑽', '≺': '𐑹',
        '⋈': '⋈^ż', '⊤': '⊤^W', '∈': '𐑲', '∋': '∋^ˌ',
        '⊙': '⊙', '⊥': '𐑖', '⊞': '𐑳', '◻': '𐑭',
    },
}

# opcodes → mnemonic (from all three engines; all share the same IMASM layer)
_MNEMONIC_TO_OPCODE = {
    'VINIT': 'VINIT', 'TANCH': 'TANCH', 'AFWD': 'AFWD', 'AREV': 'AREV',
    'CLINK': 'CLINK', 'ISCRIB': 'ISCRIB', 'FSPLIT': 'FSPLIT', 'FFUSE': 'FFUSE',
    'EVALT': 'EVALT', 'EVALF': 'EVALF', 'ENGAGR': 'ENGAGR', 'IFIX': 'IFIX',
}


# ── per-element tuple derivation ──────────────────────────────────────────────

def _count_mnemonics(instructions: list[str]) -> Counter:
    counts: Counter = Counter()
    for line in instructions:
        for mn in _MNEMONIC_TO_OPCODE:
            if mn in line:
                counts[mn] += 1
                break
    return counts


def _derive_⊣(counts: Counter, corpus: str) -> str:
    total = sum(counts.values()) or 1
    engagr = counts['ENGAGR'] / total
    fsplit = counts['FSPLIT'] / total
    ffuse  = counts['FFUSE']  / total
    ifix   = counts['IFIX']   / total
    frob_balanced = abs(counts['FSPLIT'] - counts['FFUSE']) / (counts['FSPLIT'] + counts['FFUSE'] + 1) < 0.10

    if engagr > 0.18:
        return '𐑰'                    # nested containment topology
    if (fsplit + ffuse) > 0.30 and frob_balanced:
        return '𐑶'                    # Frobenius-balanced box
    if ifix > 0.22:
        return '𐑡'                    # linear tape dominance
    return CORPUS_BASE[corpus]['⊣']     # corpus default


def _derive_<(counts: Counter, corpus: str) -> str:
    split = counts['FSPLIT']
    fuse  = counts['FFUSE']
    total_frob = split + fuse
    if total_frob == 0:
        return '𐑗'                   # no Frobenius structure
    ratio = abs(split - fuse) / total_frob
    if ratio < 0.05:
        return '𐑹'                   # Frobenius-special (balanced split/fuse)
    if ratio < 0.20:
        return '𐑯'                   # symmetric
    if ratio < 0.50:
        return '𐑬'                   # ℤ₂ parity (partially symmetric)
    return '𐑿'                       # slight asymmetry


def _derive_∋(counts: Counter, corpus: str) -> str:
    total = sum(counts.values()) or 1
    vinit = counts['VINIT'] / total
    clink = counts['CLINK'] / total
    net_split = counts['FSPLIT'] - counts['FFUSE']

    if vinit > 0.20:
        return '∋^∧'                   # conjunctive / initiating
    if net_split > max(5, 0.10 * total):
        return '∋^Ş'                   # broadcast (more splits than fuses)
    if clink > 0.15:
        return '∋^ˌ'                   # sequential composition
    return CORPUS_BASE[corpus]['∋']    # corpus default


def _derive_⊥(n_instructions: int, corpus: str) -> str:
    if n_instructions < 30:
        return '𐑓'
    if n_instructions < 60:
        return '𐑒'
    if n_instructions < 120:
        return '𐑖'
    return '𐑫'


def derive_tuple(instructions: list[str], corpus: str) -> dict:
    """Derive a per-element 12-tuple from an IMASM instruction list."""
    counts = _count_mnemonics(instructions)
    base   = dict(CORPUS_BASE[corpus])
    base['⊣'] = _derive_⊣(counts, corpus)
    base['<'] = _derive_<(counts, corpus)
    base['∋'] = _derive_∋(counts, corpus)
    base['⊥'] = _derive_⊥(len(instructions), corpus)
    return base


# ── ZFCₜ expression ───────────────────────────────────────────────────────────

def expression_for(tuple_: dict) -> tuple[str, list[str]]:
    """Return (rendered_expression, token_names) for a 12-tuple."""
    token_ids  = compose_formula(tuple_)
    token_names = [IDX2TOKEN[i] for i in token_ids]

    chunks, cur = [], []
    for t in token_names:
        if t == 'SEP_PRIM':
            chunks.append(cur); cur = []
        elif t not in ('BOS', 'EOS', 'PAD'):
            cur.append(t)
    if cur:
        chunks.append(cur)

    parts = []
    for i, chunk in enumerate(chunks):
        if not chunk:
            continue
        rendered = render_tokens(chunk)
        parts.append(rendered + ('  ∧' if i < len(chunks) - 1 else ''))

    expr = '\n    '.join(parts)
    return expr, token_names


# ── corpus loaders ────────────────────────────────────────────────────────────

def _load_voynich(data_path: Path) -> dict[str, list[str]]:
    """
    Parse LSI_ivtff_0d.txt (IVTFF 1.5 format) into per-folio instruction lists.
    Each line like '<f1r.A> {text}' → folio=f1r, parse EVA tokens.
    EVA families → IMASM opcodes (voynich_engine PRIMITIVES mapping).
    """
    EVA_MAP = {
        'o': 'VINIT', 'p': 'TANCH', 'e': 'AFWD',  'a': 'AREV',
        'd': 'CLINK', 's': 'ISCRIB', 'ch': 'FSPLIT', 'sh': 'FFUSE',
        't': 'EVALT', 'k': 'EVALF',  'r': 'ENGAGR', 'y': 'IFIX',
    }
    EVA_SORTED = sorted(EVA_MAP, key=len, reverse=True)

    folios: dict[str, list[str]] = {}
    current = None

    for raw in data_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('<f') and '>' in line:
            folio_tag = line.split('>')[0].lstrip('<').split('.')[0]
            current = folio_tag
            if current not in folios:
                folios[current] = []
            text_part = line.split('>', 1)[1].strip().lstrip('{').rstrip('}')
        elif current:
            text_part = line
        else:
            continue

        tokens = text_part.replace(',', ' ').replace('.', ' ').replace('!', ' ').split()
        for tok in tokens:
            tok = tok.strip('-').lower()
            for family in EVA_SORTED:
                if family in tok:
                    mn = EVA_MAP[family]
                    folios[current].append(f' 0x0 | {mn:<6} %r0')
                    break

    return folios


def _load_rohonc(data_path: Path) -> dict[str, list[str]]:
    from rohonc_engine.compiler import compile_corpus
    result = compile_corpus(data_path)
    return {name: data['instructions'] for name, data in result['pages'].items()}


def _load_linear_a(data_path: Path) -> dict[str, list[str]]:
    from linear_a_engine.compiler import compile_corpus
    result = compile_corpus(data_path)
    return {name: data['instructions'] for name, data in result['pages'].items()}


# ── batch processor ───────────────────────────────────────────────────────────

def process_corpus(
    corpus_id: str,
    elements: dict[str, list[str]],
    verbose: bool = True,
) -> dict:
    records = {}
    for name, instructions in sorted(elements.items()):
        if not instructions:
            continue
        tuple_ = derive_tuple(instructions, corpus_id)
        expr, token_names = expression_for(tuple_)
        counts = _count_mnemonics(instructions)
        records[name] = {
            'tuple': tuple_,
            'n_instructions': len(instructions),
            'mnemonic_counts': dict(counts),
            'expression': expr,
            'token_count': len([t for t in token_names if t not in ('BOS','EOS','PAD','SEP_PRIM')]),
        }
        if verbose:
            print(f'  {name:<10}  {len(instructions):>4} instr  '
                  f'⊣={tuple_["⊣"]}  <={tuple_["≺"]}  '
                  f'∋={tuple_["∋"]}  ⊥={tuple_["⊥"]}')
    return records


# ── output formatters ─────────────────────────────────────────────────────────

def _corpus_label(cid: str) -> str:
    return {'voynich': 'Voynich Manuscript', 'rohonc': 'Rohonc Codex',
            'linear_a': 'Linear A'}[cid]


def _element_label(cid: str) -> str:
    return {'voynich': 'folio', 'rohonc': 'page', 'linear_a': 'tablet'}[cid]


def write_text_report(all_records: dict[str, dict], path: Path) -> None:
    W = 80
    with path.open('w', encoding='utf-8') as f:
        f.write('MANUSCRIPT ZFCT EXPRESSIONS\n')
        f.write('Universal Imscriptive Grammar × ZFCₜ formal set-theory\n')
        f.write('=' * W + '\n\n')

        for cid, records in all_records.items():
            f.write('━' * W + '\n')
            f.write(f'  {_corpus_label(cid).upper()}\n')
            f.write('━' * W + '\n\n')
            base = CORPUS_BASE[cid]
            f.write(f'  Corpus base imscription:\n')
            f.write(f'  ⟨ ' + '  '.join(f'{base[p]}' for p in PRIMITIVES) + ' ⟩\n\n')

            for name, rec in sorted(records.items()):
                t = rec['tuple']
                f.write(f'  ── {_element_label(cid)} {name} '
                        f'({rec["n_instructions"]} instructions) ──\n')
                f.write(f'  ⟨ ' + '  '.join(f'{t[p]}' for p in PRIMITIVES) + ' ⟩\n')
                f.write(f'  Variable: ⊣={t["⊣"]}  <={t["≺"]}  ∋={t["∋"]}  ⊥={t["⊥"]}\n')
                f.write(f'  ZFCₜ expression:\n')
                for line in rec['expression'].split('\n'):
                    f.write(f'    {line.strip()}\n')
                f.write(f'  tokens: {rec["token_count"]}\n\n')

        f.write('=' * W + '\n')
        total_elements = sum(len(r) for r in all_records.values())
        f.write(f'  Total elements: {total_elements}\n')


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate ZFCₜ formal expressions for every manuscript element'
    )
    parser.add_argument('--voynich',  action='store_true')
    parser.add_argument('--rohonc',   action='store_true')
    parser.add_argument('--linear-a', action='store_true', dest='linear_a')
    parser.add_argument('--all',      action='store_true')
    parser.add_argument('--out',      default='manuscript_zfct', help='Output file stem')
    parser.add_argument('--quiet',    action='store_true')
    args = parser.parse_args()

    if args.all:
        args.voynich = args.rohonc = args.linear_a = True
    if not any([args.voynich, args.rohonc, args.linear_a]):
        parser.error('specify --voynich, --rohonc, --linear-a, or --all')

    verbose = not args.quiet
    all_records: dict[str, dict] = {}

    if args.voynich:
        vpath = Path(_HERE).parent / 'voynich-engine' / 'data' / 'LSI_ivtff_0d.txt'
        if not vpath.exists():
            print(f'[voynich] transcription not found: {vpath}')
        else:
            print(f'\n[voynich] loading {vpath.name} ...')
            elements = _load_voynich(vpath)
            print(f'  {len(elements)} folios found')
            print(f'  generating ZFCₜ expressions ...')
            all_records['voynich'] = process_corpus('voynich', elements, verbose)
            print(f'  done: {len(all_records["voynich"])} folios processed')

    if args.rohonc:
        rpath = Path(_HERE).parent / 'rohonc-engine' / 'data' / 'rohonc_rtff_sample.txt'
        if not rpath.exists():
            print(f'[rohonc] sample not found: {rpath}')
        else:
            print(f'\n[rohonc] loading {rpath.name} ...')
            elements = _load_rohonc(rpath)
            print(f'  {len(elements)} pages found')
            print(f'  generating ZFCₜ expressions ...')
            all_records['rohonc'] = process_corpus('rohonc', elements, verbose)
            print(f'  done: {len(all_records["rohonc"])} pages processed')

    if args.linear_a:
        lpath = Path(_HERE).parent / 'linear_a_engine' / 'data' / 'linear_a_latff_sample.txt'
        if not lpath.exists():
            print(f'[linear_a] sample not found: {lpath}')
        else:
            print(f'\n[linear_a] loading {lpath.name} ...')
            elements = _load_linear_a(lpath)
            print(f'  {len(elements)} tablets found')
            print(f'  generating ZFCₜ expressions ...')
            all_records['linear_a'] = process_corpus('linear_a', elements, verbose)
            print(f'  done: {len(all_records["linear_a"])} tablets processed')

    if not all_records:
        print('No records generated.')
        return

    json_path = Path(args.out).with_suffix('.json')
    txt_path  = Path(args.out).with_suffix('.txt')

    with json_path.open('w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    write_text_report(all_records, txt_path)

    total = sum(len(r) for r in all_records.values())
    print(f'\n  {total} elements → {json_path}  |  {txt_path}')


if __name__ == '__main__':
    main()
