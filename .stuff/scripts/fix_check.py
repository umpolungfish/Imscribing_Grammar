#!/usr/bin/env python3
"""Fix duplicate names and tier claims in generated Lean file."""
import json

with open('manuscript_zfct.json') as f:
    data = json.load(f)

mapping = {
    'Ð_ω': 'Dimensionality.D_omega', 'Ð_C': 'Dimensionality.D_turnthree',
    'Þ_O': 'Topology.T_openo', 'Þ_¨': 'Topology.T_bullseye', 'Þ_K': 'Topology.T_invscr',
    'Ř_=': 'Relational.R_lyoghlig', 'Ř_Ť': 'Relational.R_downstep',
    'Φ_υ': 'Polarity.P_aolig', 'Φ_ɐ': 'Polarity.P_aolig', 'Φ_F': 'Polarity.P_pipevar',
    'Φ_˙': 'Polarity.P_subdoublearrow', 'Φ_}': 'Polarity.P_doublebarpipe',
    'ƒ^ì': 'Fidelity.F_beltl', 'ƒ^ż': 'Fidelity.F_hardsign',
    'Ç^Ù': 'KineticChar.K_teshlig', 'Ç^@': 'KineticChar.K_schwa', 'Ç^W': 'KineticChar.K_frtailgamma',
    'Γ_ʔ': 'Granularity.G_revapostrophe',
    'ɢ^∧': 'Grammar.Gamma_seq', 'ɢ^ˌ': 'Grammar.Gamma_seq', 'ɢ^Ş': 'Grammar.Gamma_broad',
    '⊙_ÿ': 'Criticality.Phi_ctyogh',
    'Ħ_!': 'Chirality.H_invscripta', 'Ħ_£': 'Chirality.H_toneletterstem', 'Ħ_Ñ': 'Chirality.H_closeomega',
    'Σ_S': 'Stoichiometry.S_doublebaresh', 'Σ_ï': 'Stoichiometry.S_ltailm',
    'Ω_z': 'Protection.Omega_dzlig', 'Ω_Å': 'Protection.Omega_closeepsilon',
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
    if p == 'Φ_}': return '.O_∞'
    d = tup['Ð']
    o = tup['Ω']
    if o == 'Ω_z' and d != 'Ð_ß': return '.O₂'
    return '.O₁'

# Fix the CorpusComparison section at the bottom.
# Need to identify the correct P_doublebarpipe tuples for voynich_frobenius variants.
# They differ by (top, gram):
#   (Þ_¨, ɢ^∧) — 6 entries: crossing topology, sequential grammar
#   (Þ_¨, ɢ^Ş) — 1 entry: crossing topology, broadcast grammar
#   (Þ_O, ɢ^∧) — 3 entries: open topology, sequential grammar

frob_tuples = []
for _, g in data['voynich'].items():
    if g['tuple']['Φ'] == 'Φ_}':
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
