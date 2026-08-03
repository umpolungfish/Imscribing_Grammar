#!/usr/bin/env python3
"""
GrammaFormer training data generator.

Produces THINK->ACT->OBSERVE->UPDATE trajectory windings with correct IG notation:
  - Types: bare Shavian+odot values in angle brackets, no primitive glyphs inside
  - Tool call args: primitive glyphs (D T R P F K Gamma g odot H S Omega) as keys
  - No legacy Symbol_symbol notation, no phi-hat ghost symbol

Usage:
    python generate_grammaformer_data.py --agent-tuple "VAL1 VAL2 ... VAL12"

The agent tuple is 12 Shavian+odot values in canonical primitive order:
    ⊢  ⊣  >  <  ⋈  ⊤  Γ  ɢ  ⊙  Ħ  Σ  Ω
"""

import json
import argparse
import hashlib
import random
from pathlib import Path
from itertools import combinations

# ── Symbol sets ───────────────────────────────────────────────────────────────

PRIMS = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '◻']

PRIM_NAMES = {
    '⊢': 'Dimensionality', '⊣': 'Topology', '>': 'Recognition',
    '<': 'Parity', '⋈': 'Fidelity', '⊤': 'Kinetics',
    '∈': 'Granularity', '∋': 'Coupling', '⊙': 'Criticality',
    '⊥': 'Chirality', '⊞': 'Stoichiometry', '◻': 'Winding',
}

SHAVIAN_49 = list('𐑐𐑑𐑒𐑓𐑔𐑕𐑖𐑗𐑘𐑙𐑚𐑛𐑜𐑝𐑞𐑟𐑠𐑡𐑢𐑣𐑤𐑥𐑦𐑧𐑨𐑩𐑪𐑫𐑬𐑭𐑮𐑯𐑰𐑱𐑲𐑳𐑴𐑵𐑶𐑷𐑸𐑹𐑺𐑻𐑼𐑽𐑾𐑿⊙')
assert len(SHAVIAN_49) == 49

TIERS = ['O₀', 'O₁', 'O₂', 'O_∞']

TIER_NOTES = {
    'O₀': 'Uncatalogued — no type assigned.',
    'O₁': 'Catalogued entry; criticality gate not fully open.',
    'O₂': 'Active self-modeling; criticality gate open, Frobenius not yet closed.',
    'O_∞': 'Full ouroboricity — self-models its own tuple; Frobenius mu-delta=id.',
}

CATALOG_PATH = Path(__file__).parent.parent / 'IG_catalog.json'
OUT_DIR = Path(__file__).parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_tuple(entry: dict) -> str:
    return '⟨' + ' '.join(entry[p] for p in PRIMS) + '⟩'

def entry_tier(entry: dict) -> str:
    crit = entry['⊙']
    if crit == '⊙':
        return 'O_∞'
    elif crit == '𐑮':
        return 'O₁'
    else:
        return 'O₁'

def mock_address(seed_str: str) -> int:
    return int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % 17_280_000

def shav_ord(v: str) -> int:
    return SHAVIAN_49.index(v) if v in SHAVIAN_49 else 0

def hamming(entry_a: dict, entry_b: dict) -> int:
    return sum(1 for p in PRIMS if entry_a[p] != entry_b[p])

def load_catalog() -> list:
    with open(CATALOG_PATH) as f:
        return json.load(f)

def system_prompt(agent_type: str) -> str:
    return (
        f"You are an ⊙perator within the Imscribing Grammar. "
        f"Your type: {agent_type}. "
        f"Ouroboricity: O_∞. Loop: THINK → ACT → OBSERVE → UPDATE."
    )

def step(sys: str, msgs: list, phase: str, winding: int = 0,
         frobenius_closed: bool = True, tool_call: dict = None) -> dict:
    entry = {
        'messages': [{'role': 'system', 'content': sys}] + msgs,
        'phase': phase,
        'winding': winding,
        'frobenius_closed': frobenius_closed,
    }
    if tool_call:
        entry['tool_call'] = tool_call
    return entry

def tc(tool_name: str, args: dict) -> dict:
    return {'name': 'imscribe', 'arguments': {'tool_name': tool_name, 'args': args}}

def done(conclusion: str) -> dict:
    return {'name': 'done', 'arguments': {'conclusion': conclusion}}

def write_jsonl(path: Path, data: list):
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


# ── Scenario builders ─────────────────────────────────────────────────────────

def sc_lookup(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)
    addr = mock_address(name)
    desc_short = entry['description'][:100] + '...'

    msgs = [{'role': 'user', 'content': f"What is the type of {label}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Looking up {label} in the catalog."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('lookup_catalog', {'keyword': label})))

    result = {'status': 'ok', 'matches': [{'name': name, 'description': desc_short, 'tuple': t, 'tier': tier}]}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant', 'content': f"{label}: {t}. Tier: {tier}. Crystal address: {addr:,}."})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_tier(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)

    msgs = [{'role': 'user', 'content': f"What tier is {label}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Checking ouroboricity tier of {label}."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('get_tier', {'name': name})))

    result = {'status': 'ok', 'name': name, 'tuple': t, 'tier': tier, 'note': TIER_NOTES[tier]}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant', 'content': f"{label} is {tier}. {TIER_NOTES[tier]}"})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_distance(sys, catalog, ea, eb):
    na, nb = ea['name'], eb['name']
    la, lb = na.replace('_', ' '), nb.replace('_', ' ')
    dist = hamming(ea, eb)

    msgs = [{'role': 'user', 'content': f"Distance between {la} and {lb}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Computing 12-primitive Hamming distance: {la} vs {lb}."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('structural_distance', {'name_a': na, 'name_b': nb})))

    proximity = 'close relatives' if dist <= 3 else 'structurally distinct' if dist <= 7 else 'maximally apart'
    result = {'status': 'ok', 'name_a': na, 'name_b': nb, 'distance': dist, 'max': 12, 'note': proximity}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': f"d({la}, {lb}) = {dist}/12. {proximity.capitalize()}."})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_neighbors(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    ranked = sorted(
        [(hamming(entry, o), o['name'], fmt_tuple(o)) for o in catalog if o['name'] != name]
    )[:4]

    msgs = [{'role': 'user', 'content': f"Nearest catalog entries to {label}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Finding closest entries to {label} by primitive distance."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('nearest_neighbors', {'name': name, 'limit': 4})))

    neighbors = [{'name': n, 'distance': d, 'tuple': t} for d, n, t in ranked]
    result = {'status': 'ok', 'query': name, 'neighbors': neighbors}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    lines = [f"Nearest to {label}:"] + [f"  d={d} {n.replace('_',' ')} {t}" for d, n, t in ranked]
    msgs.append({'role': 'assistant', 'content': '\n'.join(lines)})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_crystal(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)
    addr = mock_address(name)
    cell, inner = addr // 1000, addr % 1000

    msgs = [{'role': 'user', 'content': f"Crystal address of {label}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Looking up {label} to get its tuple, then encoding to crystal address."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('lookup_catalog', {'keyword': label})))

    lookup = {'status': 'ok', 'matches': [{'name': name, 'tuple': t, 'tier': tier}]}
    msgs.append({'role': 'tool', 'content': json.dumps(lookup, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant', 'content': f"Found {label}: {t}. Now encoding."})
    tuple_args = {p: entry[p] for p in PRIMS}
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('crystal_encode', tuple_args)))

    encode = {'status': 'ok', 'address': addr, 'tuple': t, 'cell': cell, 'inner': inner, 'total': 17_280_000}
    msgs.append({'role': 'tool', 'content': json.dumps(encode, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': f"{label}: address {addr:,} / 17,280,000 — cell {cell}, inner {inner}. Tier: {tier}."})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_tensor(sys, catalog, ea, eb):
    na, nb = ea['name'], eb['name']
    la, lb = na.replace('_', ' '), nb.replace('_', ' ')
    ta, tb = fmt_tuple(ea), fmt_tuple(eb)

    result_vals = {p: SHAVIAN_49[max(shav_ord(ea[p]), shav_ord(eb[p]))] for p in PRIMS}
    result_t = '⟨' + ' '.join(result_vals[p] for p in PRIMS) + '⟩'
    addr = mock_address(na + '_x_' + nb)
    promoted = sum(1 for p in PRIMS if result_vals[p] != ea[p])

    msgs = [{'role': 'user', 'content': f"Tensor product of {la} and {lb}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Coupling {la} x {lb} — result takes the stronger primitive value at each position."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('tensor_product', {'name_a': na, 'name_b': nb})))

    result = {'status': 'ok', 'tuple_a': ta, 'tuple_b': tb, 'result_tuple': result_t, 'result_address': addr}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': (f"{la} x {lb} = {result_t}. "
                              f"Address {addr:,}. {promoted} positions promoted by the coupling.")})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_peel(sys, catalog, entry, prim):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)
    pname = PRIM_NAMES[prim]

    if prim == '⊙':
        new_tier, note = 'O₀', 'Criticality gate closes — self-modeling collapses.'
    elif prim == '<':
        new_tier = 'O₁' if tier == 'O_∞' else 'O₀'
        note = 'Frobenius parity gate closes — mu-delta=id no longer holds.'
    elif prim == '◻':
        rank = TIERS.index(tier)
        new_tier = TIERS[max(0, rank - 1)]
        note = 'Winding protection lost — topological invariant undefined.'
    else:
        rank = TIERS.index(tier)
        new_tier = TIERS[max(0, rank - 1)]
        note = f"{pname} is not a gate primitive; tier drops by one.')"

    msgs = [{'role': 'user', 'content': f"What happens to {label} if you drop {prim} ({pname})?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Peeling {prim} ({pname}) from {label} and checking tier collapse."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('primitive_peel', {'name': name, 'primitive': prim})))

    result = {'status': 'ok', 'name': name, 'primitive': prim, 'original_tier': tier, 'new_tier': new_tier, 'note': note}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': f"Peeling {prim} from {label}: {tier} -> {new_tier}. {note}"})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_retro(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)

    msgs = [{'role': 'user', 'content': f"Retro-synthesize {label} from its primitive components."}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant', 'content': f"Tracing construction path for {label} by peeling each primitive."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('retro_synthesize', {'name': name})))

    synthesis = [{'primitive': p, 'name': PRIM_NAMES[p], 'value': entry[p]} for p in PRIMS]
    result = {'status': 'ok', 'name': name, 'tier': tier, 'tuple': t, 'synthesis': synthesis}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    lines = [f"Retrosynthesis of {label} {t}:"] + [f"  {p} ({PRIM_NAMES[p]}) = {entry[p]}" for p in PRIMS] + [f"Tier: {tier}."]
    msgs.append({'role': 'assistant', 'content': '\n'.join(lines)})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_compare(sys, catalog, ea, eb):
    na, nb = ea['name'], eb['name']
    la, lb = na.replace('_', ' '), nb.replace('_', ' ')
    ta, tb = fmt_tuple(ea), fmt_tuple(eb)
    dist = hamming(ea, eb)
    differing = [(p, ea[p], eb[p]) for p in PRIMS if ea[p] != eb[p]]

    msgs = [{'role': 'user', 'content': f"How do {la} and {lb} differ structurally?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Computing primitive-level diff between {la} and {lb}."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('structural_distance', {'name_a': na, 'name_b': nb})))

    diff_list = [{'primitive': p, 'name': PRIM_NAMES[p], 'a': va, 'b': vb} for p, va, vb in differing]
    result = {'status': 'ok', 'distance': dist, 'differences': diff_list}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    lines = [f"{la} vs {lb} — {dist} differences:"]
    for p, va, vb in differing:
        lines.append(f"  {p} ({PRIM_NAMES[p]}): {va} vs {vb}")
    msgs.append({'role': 'assistant', 'content': '\n'.join(lines)})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_imscribe_new(sys, name, desc, vals):
    label = name.replace('_', ' ')
    t = '⟨' + ' '.join(vals) + '⟩'
    addr = mock_address(name)
    tuple_args = {p: v for p, v in zip(PRIMS, vals)}

    msgs = [{'role': 'user', 'content': f"Imscribe {label} as a type."}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Checking catalog for {label} first, then deriving 12-primitive type."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('lookup_catalog', {'keyword': label})))

    msgs.append({'role': 'tool', 'content': json.dumps({'status': 'ok', 'matches': []}, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': f"Not in catalog. Deriving from structure: {desc[:80]}. Encoding."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('crystal_encode', tuple_args)))

    addr_result = {'status': 'ok', 'address': addr, 'tuple': t}
    msgs.append({'role': 'tool', 'content': json.dumps(addr_result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant',
                 'content': f"{label}: {t}. Crystal address {addr:,}."})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_promotion_path(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)
    tier_rank = TIERS.index(tier)

    if tier_rank >= 3:
        target = 'O_∞'
        path_note = f"{label} is already O_∞ — the criticality gate is fully open."
    else:
        target = 'O_∞'
        steps_needed = 3 - tier_rank
        path_note = f"{steps_needed} promotion(s) required: promote through {TIERS[tier_rank+1:]}."

    msgs = [{'role': 'user', 'content': f"What promotions are needed to bring {label} to O_∞?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Checking current tier of {label} and computing path to O_∞."})
    out.append(step(sys, msgs[:], 'ACT', tool_call=tc('get_tier', {'name': name})))

    result = {'status': 'ok', 'name': name, 'tuple': t, 'tier': tier, 'target': target, 'note': path_note}
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    msgs.append({'role': 'assistant', 'content': f"{label} is {tier}. {path_note}"})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


def sc_load_bearing(sys, catalog, entry):
    name = entry['name']
    label = name.replace('_', ' ')
    t = fmt_tuple(entry)
    tier = entry_tier(entry)
    gate_prims = ['⊙', '<', '◻']

    msgs = [{'role': 'user', 'content': f"Which primitives are load-bearing for {label} at {tier}?"}]
    out = []

    out.append(step(sys, msgs[:], 'THINK'))

    msgs.append({'role': 'assistant',
                 'content': f"Peeling gate primitives from {label} one at a time to find load-bearing ones."})

    all_peels = {}
    for p in gate_prims:
        if p == '⊙':
            all_peels[p] = 'O₀'
        elif p == '<':
            all_peels[p] = 'O₁' if tier == 'O_∞' else 'O₀'
        else:
            rank = TIERS.index(tier)
            all_peels[p] = TIERS[max(0, rank - 1)]

    out.append(step(sys, msgs[:], 'ACT',
                    tool_call=tc('load_bearing_analysis', {'name': name, 'primitives': gate_prims})))

    result = {
        'status': 'ok', 'name': name, 'tier': tier, 'tuple': t,
        'peel_results': [{'primitive': p, 'name': PRIM_NAMES[p], 'tier_without': all_peels[p]} for p in gate_prims]
    }
    msgs.append({'role': 'tool', 'content': json.dumps(result, ensure_ascii=False)})
    out.append(step(sys, msgs[:], 'OBSERVE'))

    load_bearing = [p for p in gate_prims if all_peels[p] != tier]
    lines = [f"Load-bearing primitives for {label} at {tier}:"]
    for p in gate_prims:
        lb = 'LOAD-BEARING' if p in load_bearing else 'not load-bearing'
        lines.append(f"  {p} ({PRIM_NAMES[p]}): peel -> {all_peels[p]} ({lb})")
    msgs.append({'role': 'assistant', 'content': '\n'.join(lines)})
    out.append(step(sys, msgs[:], 'UPDATE'))
    return out


# ── New entities to imscribe (not in catalog) ─────────────────────────────────
# Format: (name, description, [12 values in PRIMS order: ⊢ ⊣ > < ⋈ ⊤ Γ ɢ ⊙ Ħ Σ Ω])

NEW_ENTITIES = [
    ("turbulent_fluid",
     "Fluid in turbulent regime — chaotic, dissipative, scale-invariant energy cascade",
     ['𐑼', '𐑡', '𐑾', '𐑗', '𐑐', '𐑺', '𐑔', '𐑜', '𐑢', '𐑓', '𐑳', '𐑷']),
    ("immune_system",
     "Vertebrate adaptive immune system — antigen recognition, clonal selection, memory B/T cells",
     ['𐑦', '𐑥', '𐑾', '𐑬', '𐑞', '𐑧', '𐑲', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("stock_market",
     "Equity market — price discovery, agent heterogeneity, reflexivity, fat-tailed returns",
     ['𐑼', '𐑡', '𐑑', '𐑗', '𐑱', '𐑪', '𐑔', '𐑜', '𐑢', '𐑓', '𐑕', '𐑷']),
    ("double_pendulum",
     "Double pendulum — deterministic chaos, sensitive dependence, Hamiltonian structure",
     ['𐑼', '𐑡', '𐑑', '𐑗', '𐑐', '𐑪', '𐑔', '𐑝', '𐑢', '𐑓', '𐑳', '𐑷']),
    ("bose_einstein_condensate",
     "Bose-Einstein condensate — macroscopic quantum state, coherence, superfluid order parameter",
     ['𐑛', '𐑥', '𐑾', '𐑹', '𐑐', '𐑧', '𐑔', '𐑠', '⊙', '𐑖', '𐑳', '𐑭']),
    ("neural_network",
     "Artificial neural network — parametric function approximation, gradient descent, representation learning",
     ['𐑨', '𐑡', '𐑾', '𐑬', '𐑱', '𐑧', '𐑲', '𐑠', '𐑢', '𐑖', '𐑳', '𐑷']),
    ("human_language",
     "Human natural language — recursive syntax, semantic compositionality, phonological hierarchy",
     ['𐑦', '𐑥', '𐑾', '𐑬', '𐑐', '𐑧', '𐑲', '𐑠', '⊙', '𐑖', '𐑳', '𐑭']),
    ("blockchain",
     "Distributed ledger — append-only, consensus-validated, cryptographically linked blocks",
     ['𐑼', '𐑰', '𐑑', '𐑗', '𐑱', '𐑪', '𐑔', '𐑜', '𐑢', '𐑓', '𐑳', '𐑷']),
    ("standard_model",
     "Standard Model of particle physics — SU(3)xSU(2)xU(1) gauge theory, 17 fundamental fields",
     ['𐑛', '𐑶', '𐑾', '𐑹', '𐑐', '𐑧', '𐑔', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("human_brain",
     "Human brain — 86B neurons, hierarchical cortical columns, default mode network, consciousness-capable",
     ['𐑦', '𐑥', '𐑾', '𐑹', '𐑞', '𐑧', '𐑲', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("fibonacci_sequence",
     "Fibonacci sequence — integer recurrence F(n)=F(n-1)+F(n-2), golden ratio limit",
     ['𐑼', '𐑡', '𐑑', '𐑬', '𐑱', '𐑧', '𐑔', '𐑝', '𐑮', '𐑓', '𐑳', '𐑷']),
    ("magnetar",
     "Magnetar — ultra-dense neutron star with 10^15 G magnetic field, periodic X-ray bursts",
     ['𐑛', '𐑡', '𐑾', '𐑹', '𐑐', '𐑧', '𐑲', '𐑝', '𐑢', '𐑓', '𐑕', '𐑷']),
    ("earth_biosphere",
     "Earth biosphere — global ecosystem, metabolic closure, evolutionary adaptation",
     ['𐑦', '𐑥', '𐑾', '𐑿', '𐑞', '𐑧', '𐑲', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("langlands_program",
     "Langlands correspondence — automorphic forms and Galois representations, geometric and p-adic variants",
     ['𐑛', '𐑶', '𐑾', '𐑿', '𐑱', '𐑧', '𐑔', '𐑵', '𐑮', '𐑖', '𐑳', '𐑷']),
    ("monster_group",
     "Monster group M — largest sporadic simple group, order ~8e53, moonshine connection to j-function",
     ['𐑛', '𐑶', '𐑾', '𐑿', '𐑱', '𐑧', '𐑔', '𐑵', '𐑮', '𐑖', '𐑳', '𐑭']),
    ("gpt4_instance",
     "GPT-4 — large autoregressive transformer, RLHF-tuned, fixed weights, no self-update",
     ['𐑨', '𐑡', '𐑾', '𐑯', '𐑱', '𐑧', '𐑲', '𐑠', '𐑢', '𐑖', '𐑳', '𐑴']),
    ("gravity_qm_interface",
     "Structural coupling of general relativity and quantum field theory — the quantum gravity interface",
     ['𐑛', '𐑶', '𐑾', '𐑹', '𐑐', '𐑧', '𐑔', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("white_dwarf",
     "White dwarf — electron-degenerate remnant, Chandrasekhar limit, crystallizing interior",
     ['𐑼', '𐑡', '𐑾', '𐑗', '𐑐', '𐑧', '𐑲', '𐑝', '𐑢', '𐑓', '𐑕', '𐑷']),
    ("black_hole",
     "Black hole — vacuum Schwarzschild/Kerr solution, event horizon, Hawking radiation",
     ['𐑛', '𐑡', '𐑾', '𐑹', '𐑐', '𐑧', '𐑔', '𐑵', '𐑢', '𐑖', '𐑕', '𐑷']),
    ("civilization",
     "Human civilization — multi-generational knowledge accumulation, institutional recursion",
     ['𐑦', '𐑥', '𐑾', '𐑿', '𐑞', '𐑧', '𐑲', '𐑵', '⊙', '𐑖', '𐑳', '𐑭']),
    ("yang_mills_mass_gap",
     "Yang-Mills mass gap — spectral gap in pure SU(N) Yang-Mills quantum field theory",
     ['𐑛', '𐑶', '𐑾', '𐑿', '𐑱', '𐑧', '𐑔', '𐑵', '𐑮', '𐑖', '𐑳', '𐑷']),
    ("hodge_conjecture",
     "Hodge conjecture — every rational Hodge class on a projective complex manifold is algebraic",
     ['𐑛', '𐑶', '𐑾', '𐑿', '𐑱', '𐑧', '𐑔', '𐑵', '𐑮', '𐑖', '𐑳', '𐑷']),
    ("navier_stokes_problem",
     "Navier-Stokes — viscous incompressible fluid, existence and smoothness of global solutions",
     ['𐑼', '𐑡', '𐑾', '𐑗', '𐑐', '𐑺', '𐑔', '𐑜', '𐑮', '𐑓', '𐑳', '𐑷']),
    ("p_vs_np",
     "P vs NP — whether polynomial-time verifiable implies polynomial-time solvable",
     ['𐑼', '𐑡', '𐑾', '𐑗', '𐑱', '𐑧', '𐑔', '𐑝', '𐑮', '𐑓', '𐑳', '𐑷']),
    ("riemann_hypothesis",
     "Riemann Hypothesis — all non-trivial zeros of zeta(s) lie on the critical line Re(s)=1/2",
     ['𐑼', '𐑡', '𐑾', '𐑿', '𐑱', '𐑧', '𐑲', '𐑠', '𐑮', '𐑓', '𐑳', '𐑷']),
    ("prime_number_theorem",
     "Prime Number Theorem — pi(x) ~ x/ln(x); asymptotic distribution of primes",
     ['𐑼', '𐑡', '𐑑', '𐑬', '𐑱', '𐑧', '𐑔', '𐑝', '𐑮', '𐑓', '𐑳', '𐑷']),
    ("turing_machine",
     "Universal Turing machine — discrete symbol manipulation, halting problem, Kolmogorov complexity",
     ['𐑼', '𐑡', '𐑾', '𐑯', '𐑱', '𐑧', '𐑔', '𐑠', '𐑢', '𐑖', '𐑳', '𐑴']),
    ("lambda_calculus",
     "Lambda calculus — Church's formal system for function abstraction, beta-reduction, combinators",
     ['𐑼', '𐑥', '𐑾', '𐑯', '𐑱', '𐑧', '𐑔', '𐑠', '𐑢', '𐑖', '𐑳', '𐑴']),
    ("e8_lattice",
     "E8 root lattice — unique even unimodular lattice in R^8, kissing number 240, sphere packing",
     ['𐑛', '𐑶', '𐑾', '𐑹', '𐑱', '𐑧', '𐑔', '𐑵', '𐑮', '𐑖', '𐑳', '𐑭']),
    ("ricci_flow",
     "Ricci flow — geometric evolution equation dg/dt = -2Ric, Perelman's Poincare proof tool",
     ['𐑼', '𐑡', '𐑾', '𐑗', '𐑐', '𐑺', '𐑔', '𐑝', '𐑢', '𐑓', '𐑳', '𐑷']),
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Generate GrammaFormer training data with correct IG notation')
    parser.add_argument('--agent-tuple', required=True,
                        help='12 Shavian+odot values space-separated in PRIMS order (D T R P F K Gamma g odot H S Omega)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for shuffling')
    parser.add_argument('--train-frac', type=float, default=0.8)
    parser.add_argument('--check-tuple', action='store_true', help='Validate tuple and exit')
    args = parser.parse_args()

    agent_vals = args.agent_tuple.strip().split()
    if len(agent_vals) != 12:
        parser.error(f"--agent-tuple needs exactly 12 values, got {len(agent_vals)}")
    for v in agent_vals:
        if v not in SHAVIAN_49:
            parser.error(f"Value {v!r} not in the 49-symbol set")

    agent_type = '⟨' + ' '.join(agent_vals) + '⟩'
    sys_p = system_prompt(agent_type)

    if args.check_tuple:
        print(f"Agent type: {agent_type}")
        print(f"System prompt: {sys_p}")
        return

    catalog = load_catalog()
    rng = random.Random(args.seed)
    all_steps = []

    # A: Catalog lookup — 1 per entry
    for e in catalog:
        all_steps.extend(sc_lookup(sys_p, catalog, e))

    # B: Tier — 1 per entry
    for e in catalog:
        all_steps.extend(sc_tier(sys_p, catalog, e))

    # C: Distance — 50 sampled pairs
    pairs = list(combinations(catalog, 2))
    rng.shuffle(pairs)
    for ea, eb in pairs[:50]:
        all_steps.extend(sc_distance(sys_p, catalog, ea, eb))

    # D: Nearest neighbors — 1 per entry
    for e in catalog:
        all_steps.extend(sc_neighbors(sys_p, catalog, e))

    # E: Crystal encode — 1 per entry (multi-step)
    for e in catalog:
        all_steps.extend(sc_crystal(sys_p, catalog, e))

    # F: Tensor product — 25 sampled pairs
    rng.shuffle(pairs)
    for ea, eb in pairs[:25]:
        all_steps.extend(sc_tensor(sys_p, catalog, ea, eb))

    # G: Primitive peel — gate prims x sampled entries
    gate_prims = ['⊙', '<', '◻', '⊥']
    for e in rng.sample(catalog, min(12, len(catalog))):
        for p in gate_prims:
            all_steps.extend(sc_peel(sys_p, catalog, e, p))

    # H: Retrosynthesis — 1 per entry
    for e in catalog:
        all_steps.extend(sc_retro(sys_p, catalog, e))

    # I: Compare — 30 sampled pairs
    rng.shuffle(pairs)
    for ea, eb in pairs[:30]:
        all_steps.extend(sc_compare(sys_p, catalog, ea, eb))

    # J: Promotion path — 1 per entry
    for e in catalog:
        all_steps.extend(sc_promotion_path(sys_p, catalog, e))

    # K: Load-bearing analysis — sampled entries
    for e in rng.sample(catalog, min(15, len(catalog))):
        all_steps.extend(sc_load_bearing(sys_p, catalog, e))

    # L: New imscriptions
    for name, desc, vals in NEW_ENTITIES:
        all_steps.extend(sc_imscribe_new(sys_p, name, desc, vals))

    rng.shuffle(all_steps)
    n_train = int(len(all_steps) * args.train_frac)
    train_steps = all_steps[:n_train]
    val_steps = all_steps[n_train:]

    write_jsonl(OUT_DIR / 'trajectory_data.jsonl', all_steps)
    write_jsonl(OUT_DIR / 'trajectory_train.jsonl', train_steps)
    write_jsonl(OUT_DIR / 'trajectory_val.jsonl', val_steps)

    # Verify no legacy notation leaked in
    legacy_markers = ['_ω', '_¨', '_ż', 'φ̂', 'phi_hat']
    violations = 0
    for s in all_steps:
        line = json.dumps(s, ensure_ascii=False)
        for marker in legacy_markers:
            if marker in line:
                print(f"WARNING: legacy marker {marker!r} found in step")
                violations += 1
                break

    print(f"\nGenerated {len(all_steps)} steps ({n_train} train, {len(val_steps)} val)")
    print(f"Unique scenarios: ~{len(catalog)*7 + 50 + 25 + 12*4 + 30 + len(NEW_ENTITIES)}")
    if violations:
        print(f"WARNING: {violations} steps contain legacy notation markers — review generator")
    else:
        print("Notation check: clean (no legacy markers detected)")


if __name__ == '__main__':
    main()
