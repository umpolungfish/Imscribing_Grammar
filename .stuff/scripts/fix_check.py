#!/usr/bin/env python3
"""Fix duplicate names and tier claims in generated Lean file."""
import json

with open('manuscript_zfct.json') as f:
    data = json.load(f)

mapping = {
    '𐑦': 'Dimensionality.D_omega', '𐑨': 'Dimensionality.ash',
    '𐑸': 'Topology.T_openo', '𐑶': 'Topology.mime', '𐑰': 'Topology.T_invscr',
    '𐑾': 'Relational.R_lyoghlig', '𐑽': 'Relational.R_downstep',
    '𐑿': 'Polarity.P_aolig', '𐑗': 'Polarity.P_aolig', '𐑬': 'Polarity.out',
    '𐑯': 'Polarity.nun', '𐑹': 'Polarity.or_',
    'ƒ^ì': 'Fidelity.age', 'ƒ^ż': 'Fidelity.peep',
    'Ç^Ù': 'KineticChar.on', 'Ç^@': 'KineticChar.egg', 'Ç^W': 'KineticChar.yea',
    '𐑲': 'Granularity.ice',
    'ɢ^∧': 'Grammar.Gamma_seq', 'ɢ^ˌ': 'Grammar.Gamma_seq', 'ɢ^Ş': 'Grammar.Gamma_broad',
    '⊙': 'Criticality.monad',
    '𐑫': 'Chirality.wool', '𐑒': 'Chirality.kick', '𐑓': 'Chirality.fee',
    '𐑙': 'Stoichiometry.hung', '𐑳': 'Stoichiometry.up',
    '𐑭': 'Protection.ah', '𐑷': 'Protection.awe',
}

def mk_synthon(tup):
    return (f'  {{ dim  := {mapping[tup["Ð"]]},\n'
            f'    top  := {mapping[tup["Þ"]]},\n'
            f'    rel  := {mapping[tup["Ř"]]},\n'
            f'    pol  := {mapping[tup["Φ"]]},\n'
            f'    fid  := {mapping[tup["ƒ"]]},\n'
            f'    kin  := {mapping[tup["Ç"]]},\n'
            f'    gran := {mapping[tup["Γ"]]},\n'
            f'    gram := {mapping[tup["ɢ"]]},\n'
            f'    crit := {mapping[tup["⊙"]]},\n'
            f'    chir := {mapping[tup["Ħ"]]},\n'
            f'    stoi := {mapping[tup["Σ"]]},\n'
            f'    prot := {mapping[tup["Ω"]]} }}')

def tier_for(tup):
    p = tup['Φ']
    if p == '𐑹': return '.O_∞'
    d = tup['Ð']
    o = tup['Ω']
    if o == '𐑭' and d != '𐑛': return '.O₂'
    return '.O₁'

# Fix the CorpusComparison section at the bottom.
# Need to identify the correct P_doublebarpipe tuples for voynich_frobenius variants.
# They differ by (top, gram):
#   (𐑶, ɢ^∧) — 6 entries: crossing topology, sequential grammar
#   (𐑶, ɢ^Ş) — 1 entry: crossing topology, broadcast grammar
#   (𐑸, ɢ^∧) — 3 entries: open topology, sequential grammar

frob_tuples = []
for _, g in data['voynich'].items():
    if g['tuple']['Φ'] == '𐑹':
        frob_tuples.append(g['tuple'])

# deduplicate
seen = set()
uniq_frob = []
for t in frob_tuples:
    s = json.dumps(t, sort_keys=True)
    if s not in seen:
        seen.add(s)
        uniq_frob.append(t)

print(f"Found {len(uniq_frob)} distinct Frobenius-special Voynich tuple types")
for t in uniq_frob:
    print(f"  top={t['Þ']}, gram={t['ɢ']}")

# voynich_main has P_aolig, so tier is O₂, not O_∞
main_v = max(data['voynich'].values(), key=lambda g: g['count'])['tuple']
print(f"\nVoynich main tuple: P={main_v['Φ']}, so tier = {tier_for(main_v)}")
print(f"Rohonc main tuple: tier check needed")
print(f"LinearA main tuple: tier check needed")
