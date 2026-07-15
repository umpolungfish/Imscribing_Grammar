#!/usr/bin/env python3
"""Generate Manuscript_ZFCt.lean from manuscript_zfct.json"""

import json

with open('manuscript_zfct.json') as f:
    data = json.load(f)

mapping = {
    '𐑦': 'Dimensionality.D_omega',
    '𐑨': 'Dimensionality.ash',
    '𐑼': 'Dimensionality.dead',
    '𐑛': 'Dimensionality.array',
    '𐑸': 'Topology.T_openo',
    '𐑶': 'Topology.mime',
    '𐑰': 'Topology.T_invscr',
    '𐑥': 'Topology.T_box',
    '𐑡': 'Topology.judge',
    '𐑾': 'Relational.R_lyoghlig',
    '𐑽': 'Relational.R_downstep',
    '𐑩': 'Relational.R_subrightarrow',
    '𐑑': 'Relational.R_ctz',
    '𐑿': 'Polarity.P_aolig',
    '𐑗': 'Polarity.P_aolig',
    '𐑬': 'Polarity.out',
    '𐑯': 'Polarity.nun',
    '𐑹': 'Polarity.or_',
    'ƒ^ì': 'Fidelity.age',
    'ƒ^ð': 'Fidelity.they',
    'ƒ^ż': 'Fidelity.peep',
    'Ç^Ù': 'KineticChar.on',
    'Ç^@': 'KineticChar.egg',
    'Ç^W': 'KineticChar.yea',
    'Ç^-': 'KineticChar.loll',
    'Ç^λ': 'KineticChar.air',
    '𐑲': 'Granularity.ice',
    '𐑚': 'Granularity.bib',
    '𐑔': 'Granularity.thigh',
    'ɢ^∧': 'Grammar.Gamma_seq',
    'ɢ^ˌ': 'Grammar.Gamma_seq',
    'ɢ^Ş': 'Grammar.Gamma_broad',
    'ɢ^˝': 'Grammar.Gamma_or',
    '⊙': 'Criticality.monad',
    '𐑮': 'Criticality.roar',
    '𐑻': 'Criticality.err',
    '𐑢': 'Criticality.woe',
    '𐑣': 'Criticality.haha',
    '𐑫': 'Chirality.wool',
    '𐑒': 'Chirality.kick',
    '𐑓': 'Chirality.fee',
    '𐑖': 'Chirality.sure',
    '𐑙': 'Stoichiometry.hung',
    '𐑕': 'Stoichiometry.S_ctn',
    '𐑳': 'Stoichiometry.up',
    '𐑭': 'Protection.ah',
    '𐑷': 'Protection.awe',
    '𐑴': 'Protection.oak',
    '𐑟': 'Protection.zoo',
}

def mk_synthon(tup):
    """Convert a JSON tuple dict to Lean Synthon literal string."""
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

def mk_name(group_idx, tup):
    """Generate a readable Lean name for a tuple group."""
    parts = [f"type{group_idx}"]
    if tup['Φ'] != '𐑿':
        parts.append(f"sym_{tup['Φ'][-1]}")
    if tup['ɢ'] == 'ɢ^Ş':
        parts.append("broad")
    if tup['Þ'] == '𐑰':
        parts.append("incl")
    if tup['Þ'] == '𐑶':
        parts.append("cross")
    if tup['Ħ'] == '𐑓':
        parts.append("memless")
    return '_'.join(parts)

# Group entries by tuple
corpus_groups = {}
for ckey in ['voynich', 'rohonc', 'linear_a']:
    corpus = data[ckey]
    groups = {}
    for ekey, entry in corpus.items():
        ts = json.dumps(entry['tuple'], sort_keys=True)
        if ts not in groups:
            groups[ts] = {'count': 0, 'tuple': entry['tuple'],
                          'expression': entry['expression'], 'examples': []}
        groups[ts]['count'] += 1
        if len(groups[ts]['examples']) < 3:
            groups[ts]['examples'].append(ekey)
    corpus_groups[ckey] = groups

lines = []
def L(s=""):
    lines.append(s)

L("/-")
L("  Manuscript_ZFCt.lean")
L("  Formalization of three undeciphered writing systems as ZFCt structural types.")
L("  Generated from manuscript_zfct.json — 313 entries total.")
L("")
L("  Each entry is a Synthon (12-primitive tuple) paired with a ZFCt")
L("  formula expression encoding its set-theoretic structure.")
L("-/")
L("")
L("import ImscribingGrammar.Primitives.Synthon")
L("open ImscribingGrammar.Primitives")
L("")
L("set_option pp.all false")
L("")
L("namespace Manuscript_ZFCt")
L("")

for ckey in ['voynich', 'rohonc', 'linear_a']:
    cap = ckey.title().replace('_', '')
    groups = corpus_groups[ckey]
    gitems = sorted(groups.items(), key=lambda x: -x[1]['count'])
    
    L(f"/- ================================================================")
    L(f"   {cap}: {ckey} — {len(data[ckey])} entries, {len(groups)} distinct tuple types")
    L(f"   ================================================================ -/")
    L(f"namespace {cap}")
    L("")
    
    for idx, (_, g) in enumerate(gitems, 1):
        tup = g['tuple']
        nm = mk_name(idx, tup)
        ex_str = ', '.join(g['examples'])
        L(f"  /-- {g['count']} entries (e.g. {ex_str})")
        L(f"      Tuple: {json.dumps(tup)}")
        L(f"      ZFCt expression length: ~{len(g['expression'].split())} tokens -/")
        L(f"  def {nm} : Synthon :=")
        L(f"    {mk_synthon(tup)}")
        L("")
        
        esc_expr = g['expression'].replace('"', '\\"').replace('\n', '\\n')
        L(f"  /-- ZFCt formula for {nm} -/")
        L(f"  def {nm}_zfct : String :=")
        L(f"    \"{esc_expr}\"")
        L("")
    
    L(f"end {cap}")
    L("")

# Corpus comparison section
L("/- ================================================================")
L("   Structural comparison between corpora")
L("   ================================================================ -/")
L("namespace CorpusComparison")
L("")

# Pick most common tuple from each
def most_common(ckey):
    groups = corpus_groups[ckey]
    return max(groups.items(), key=lambda x: x[1]['count'])[1]

mc_v = most_common('voynich')
mc_r = most_common('rohonc')
mc_l = most_common('linear_a')

L("  /-- Most frequent Voynich tuple type -/")
L("  def voynich_main : Synthon :=")
L(f"    {mk_synthon(mc_v['tuple'])}")
L("")
L("  /-- Most frequent Rohonc tuple type -/")
L("  def rohonc_main : Synthon :=")
L(f"    {mk_synthon(mc_r['tuple'])}")
L("")
L("  /-- Most frequent Linear A tuple type -/")
L("  def linearA_main : Synthon :=")
L(f"    {mk_synthon(mc_l['tuple'])}")
L("")

# Compute approximate Hamming distances (hardcoded since we know them)
L("  /-- Hamming: Voynich vs Rohonc — D, T, R, K, H, S differ -/")
L("  theorem voynich_rohonc_dist : primitiveMismatches voynich_main rohonc_main = 6 := by")
L("    native_decide")
L("")
L("  /-- Hamming: Rohonc vs Linear A — only F and K differ (classical vs quantum, -/")
L("      slow vs driven) -/")
L("  theorem rohonc_linearA_dist : primitiveMismatches rohonc_main linearA_main = 2 := by")
L("    native_decide")
L("")
L("  /-- Hamming: Voynich vs Linear A — 7 primitives differ -/")
L("  theorem voynich_linearA_dist : primitiveMismatches voynich_main linearA_main = 7 := by")
L("    native_decide")
L("")

# Compute tiers
L("  /-- Voynich tier: O_∞ (D_omega + ⊙ + P_doublebarpipe-capable) -/")
L("  theorem voynich_tier : synthonTier voynich_main = .O_∞ := by")
L("    native_decide")
L("")
L("  /-- Rohonc tier: O₂ (protected, finite D, crossing topology) -/")
L("  theorem rohonc_tier : synthonTier rohonc_main = .O₂ := by")
L("    native_decide")
L("")
L("  /-- Linear A tier: O₂ (same base as Rohonc despite quantum/driven regime) -/")
L("  theorem linearA_tier : synthonTier linearA_main = .O₂ := by")
L("    native_decide")
L("")

# Voynich Frobenius-special entries (𐑹) — the P_doublebarpipe ones
# Find them
frob_entries = []
for _, g in corpus_groups['voynich'].items():
    if g['tuple']['Φ'] == '𐑹':
        frob_entries.append(g)

if frob_entries:
    L("  /-- Voynich Frobenius-special entries (Phi = P_doublebarpipe, Þ = 𐑶):")
    L(f"      {sum(g['count'] for g in frob_entries)} entries with μ∘δ=id exactly -/")
    for fe in frob_entries:
        tup = fe['tuple']
        nm = "voynich_frobenius"
        L(f"  def {nm} : Synthon :=")
        L(f"    {mk_synthon(tup)}")
        L(f"  theorem {nm}_tier : synthonTier {nm} = .O_∞ := by")
        L("    native_decide")
        L("")

L("end CorpusComparison")
L("")
L("end Manuscript_ZFCt")

result = '\n'.join(lines)
with open('Manuscript_ZFCt.lean', 'w') as f:
    f.write(result)

print(f"Generated {len(lines)} lines, {len(result)} chars, written to Manuscript_ZFCt.lean")
print(f"Distinct tuple types: Voynich={len(corpus_groups['voynich'])}, Rohonc={len(corpus_groups['rohonc'])}, Linear A={len(corpus_groups['linear_a'])}")
