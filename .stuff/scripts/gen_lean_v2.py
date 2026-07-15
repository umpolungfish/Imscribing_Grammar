#!/usr/bin/env python3
"""Generate corrected Manuscript_ZFCt.lean v2 — no duplicate names, correct tiers."""
import json

with open('manuscript_zfct.json') as f:
    data = json.load(f)

# ── Primitive name mapping (JSON → Lean) ──────────────────────
M = {
    '𐑦': 'Dimensionality.D_omega', '𐑨': 'Dimensionality.ash',
    '𐑼': 'Dimensionality.dead', '𐑛': 'Dimensionality.array',
    '𐑸': 'Topology.T_openo', '𐑶': 'Topology.mime',
    '𐑰': 'Topology.T_invscr', '𐑥': 'Topology.T_box', '𐑡': 'Topology.judge',
    '𐑾': 'Relational.R_lyoghlig', '𐑽': 'Relational.R_downstep',
    '𐑩': 'Relational.R_subrightarrow', '𐑑': 'Relational.R_ctz',
    '𐑿': 'Polarity.P_aolig', '𐑗': 'Polarity.P_aolig',
    '𐑬': 'Polarity.out', '𐑯': 'Polarity.nun',
    '𐑹': 'Polarity.or_',
    'ƒ^ì': 'Fidelity.age', 'ƒ^ð': 'Fidelity.they', 'ƒ^ż': 'Fidelity.peep',
    'Ç^Ù': 'KineticChar.on', 'Ç^@': 'KineticChar.egg',
    'Ç^W': 'KineticChar.yea', 'Ç^-': 'KineticChar.loll', 'Ç^λ': 'KineticChar.air',
    '𐑲': 'Granularity.ice', '𐑚': 'Granularity.bib', '𐑔': 'Granularity.thigh',
    'ɢ^∧': 'Grammar.Gamma_seq', 'ɢ^ˌ': 'Grammar.Gamma_seq', 'ɢ^Ş': 'Grammar.Gamma_broad',
    'ɢ^˝': 'Grammar.Gamma_or',
    '⊙': 'Criticality.monad', '𐑮': 'Criticality.roar',
    '𐑻': 'Criticality.err', '𐑢': 'Criticality.woe', '𐑣': 'Criticality.haha',
    '𐑫': 'Chirality.wool', '𐑒': 'Chirality.kick',
    '𐑓': 'Chirality.fee', '𐑖': 'Chirality.sure',
    '𐑙': 'Stoichiometry.hung', '𐑕': 'Stoichiometry.S_ctn', '𐑳': 'Stoichiometry.up',
    '𐑭': 'Protection.ah', '𐑷': 'Protection.awe',
    '𐑴': 'Protection.oak', '𐑟': 'Protection.zoo',
}

def mk_s(tup):
    """Synthon literal from JSON tuple dict."""
    return (f'  {{ dim  := {M[tup["Ð"]]},\n'
            f'    top  := {M[tup["Þ"]]},\n'
            f'    rel  := {M[tup["Ř"]]},\n'
            f'    pol  := {M[tup["Φ"]]},\n'
            f'    fid  := {M[tup["ƒ"]]},\n'
            f'    kin  := {M[tup["Ç"]]},\n'
            f'    gran := {M[tup["Γ"]]},\n'
            f'    gram := {M[tup["ɢ"]]},\n'
            f'    crit := {M[tup["⊙"]]},\n'
            f'    chir := {M[tup["Ħ"]]},\n'
            f'    stoi := {M[tup["Σ"]]},\n'
            f'    prot := {M[tup["Ω"]]} }}')

def tier(tup):
    p, o, d = tup['Φ'], tup['Ω'], tup['Ð']
    if p == '𐑹': return '.O_∞'  # P_doublebarpipe → Frobenius
    if o == '𐑭' or o == '𐑴' or o == '𐑟':  # non-trivial Ω
        if d == '𐑛': return '.O₂†'  # D_invomega
        return '.O₂'  # finite D
    return '.O₁'  # Omega_0

# ── Group entries by tuple ────────────────────────────────────
def group_corpus(ckey):
    groups = {}
    for ek, ev in data[ckey].items():
        ts = json.dumps(ev['tuple'], sort_keys=True)
        if ts not in groups:
            groups[ts] = {'count': 0, 'tuple': ev['tuple'],
                          'expression': ev['expression'], 'examples': []}
        groups[ts]['count'] += 1
        if len(groups[ts]['examples']) < 2:
            groups[ts]['examples'].append(ek)
    return groups

CORPORA = {k: group_corpus(k) for k in ['voynich', 'rohonc', 'linear_a']}

# ── Descriptive names for each tuple group ────────────────────
def mk_name(idx, tup):
    parts = [f"type{idx}"]
    # polarity variant (skip if P_aolig = default)
    if tup['Φ'] != '𐑿':
        label = {'𐑬': 'sym_F', '𐑹': 'sym_cl', '𐑯': 'sym_all'}
        parts.append(label.get(tup['Φ'], f"sym_{tup['Φ'][-1]}"))
    # grammar variant
    if tup['ɢ'] == 'ɢ^Ş':
        parts.append("broad")
    # topology variant (skip if default)
    if tup['Þ'] == '𐑰':
        parts.append("incl")
    elif tup['Þ'] == '𐑶':
        parts.append("cross")
    # memory variant
    if tup['Ħ'] == '𐑓':
        parts.append("memless")
    return '_'.join(parts)

# ── Build the file ────────────────────────────────────────────
L = []
def w(s=""):
    L.append(s)

w("/-")
w("  Manuscript_ZFCt.lean")
w("  Formalization of three undeciphered writing systems as ZFCt structural types.")
w("  Generated from manuscript_zfct.json — 313 entries (Voynich 227, Rohonc 33, Linear A 53).")
w("")
w("  Each entry is a Synthon (12-primitive tuple) paired with a ZFCt expression")
w("  encoding its set-theoretic structure. Ouroboricity tiers are verified by native_decide.")
w("-/")
w("")
w("import ImscribingGrammar.Primitives.Synthon")
w("open ImscribingGrammar.Primitives")
w("")
w("set_option pp.all false")
w("")
w("namespace Manuscript_ZFCt")
w("")

# ── Per-corpus namespaces ─────────────────────────────────────
for ckey in ['voynich', 'rohonc', 'linear_a']:
    cap = ckey.title().replace('_', '')
    groups = CORPORA[ckey]
    items = sorted(groups.items(), key=lambda x: -x[1]['count'])
    
    total = len(data[ckey])
    w(f"/- {'='*64}")
    w(f"   {cap}: {ckey} — {total} entries, {len(groups)} distinct structural types")
    w(f"   {'='*64} -/")
    w(f"namespace {cap}")
    w("")
    
    for idx, (_, g) in enumerate(items, 1):
        tup = g['tuple']
        nm = mk_name(idx, tup)
        ex = ', '.join(g['examples'])
        t = tier(tup)
        w(f"  /-- {g['count']} entries (e.g. {ex})")
        w(f"      Ouroboricity tier: {t}")
        w(f"      ZFCt tokens: ~{len(g['expression'].split())} -/")
        w(f"  def {nm} : Synthon :=")
        w(f"    {mk_synthon(tup)}")
        w("")
        esc = g['expression'].replace('"', '\\"').replace('\n', '\\n')
        w(f"  /-- ZFCt formula for {nm} -/")
        w(f"  def {nm}_zfct : String :=")
        w(f"    \"{esc}\"")
        w("")
        # Tier theorem
        w(f"  theorem {nm}_tier : synthonTier {nm} = {t} := by")
        w("    native_decide")
        w("")
    
    w(f"end {cap}")
    w("")

# Helper
def mk_synthon(tup):
    return (f'    {{ dim  := {M[tup["Ð"]]},\n'
            f'      top  := {M[tup["Þ"]]},\n'
            f'      rel  := {M[tup["Ř"]]},\n'
            f'      pol  := {M[tup["Φ"]]},\n'
            f'      fid  := {M[tup["ƒ"]]},\n'
            f'      kin  := {M[tup["Ç"]]},\n'
            f'      gran := {M[tup["Γ"]]},\n'
            f'      gram := {M[tup["ɢ"]]},\n'
            f'      crit := {M[tup["⊙"]]},\n'
            f'      chir := {M[tup["Ħ"]]},\n'
            f'      stoi := {M[tup["Σ"]]},\n'
            f'      prot := {M[tup["Ω"]]} }}')

# Correction: the old voynich_tier was wrong. P_aolig → O₂ not O_∞.

# ── Corpus comparison ─────────────────────────────────────────
mc = {k: max(CORPORA[k].items(), key=lambda x: x[1]['count'])[1] for k in CORPORA}
w("/- {'='*64}")
w("   Structural comparison between corpora")
w("   {'='*64} -/")
w("namespace CorpusComparison")
w("")

w("  /-- Most frequent Voynich structural type -/")
w("  def voynich_main : Synthon :=")
w(f"    {mk_synthon(mc['voynich']['tuple'])}")
w(f"  theorem voynich_main_tier : synthonTier voynich_main = .O₂ := by")
w("    native_decide")
w("")

w("  /-- Most frequent Rohonc structural type -/")
w("  def rohonc_main : Synthon :=")
w(f"    {mk_synthon(mc['rohonc']['tuple'])}")
w(f"  theorem rohonc_main_tier : synthonTier rohonc_main = .O₂ := by")
w("    native_decide")
w("")

w("  /-- Most frequent Linear A structural type -/")
w("  def linearA_main : Synthon :=")
w(f"    {mk_synthon(mc['linear_a']['tuple'])}")
w(f"  theorem linearA_main_tier : synthonTier linearA_main = .O₂ := by")
w("    native_decide")
w("")

w("  /-- Hamming distances -/")
tv, tr, tl = mc['voynich']['tuple'], mc['rohonc']['tuple'], mc['linear_a']['tuple']
def ham(t1, t2):
    return sum(1 for k in t1 if t1[k] != t2[k])
w(f"  theorem voynich_rohonc_dist : primitiveMismatches voynich_main rohonc_main = {ham(tv, tr)} := by")
w("    native_decide")
w(f"  theorem rohonc_linearA_dist : primitiveMismatches rohonc_main linearA_main = {ham(tr, tl)} := by")
w("    native_decide")
w(f"  theorem voynich_linearA_dist : primitiveMismatches voynich_main linearA_main = {ham(tv, tl)} := by")
w("    native_decide")
w("")

# ── Voynich Frobenius-special entries ─────────────────────────
w("  /-- Voynich Frobenius-special entries (P_doublebarpipe, μ∘δ=id) -/")
w("  /-- 6 entries: crossing topology, sequential grammar (e.g. f103r, f103v, f1r) -/")
w("  def voynich_frob_cross_seq : Synthon :=")
f1 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == '𐑹' and g['tuple']['Þ'] == '𐑶' and g['tuple']['ɢ'] == 'ɢ^∧'][0]
w(f"    {mk_synthon(f1['tuple'])}")
w("  theorem voynich_frob_cross_seq_tier : synthonTier voynich_frob_cross_seq = .O_∞ := by")
w("    native_decide")
w("")

w("  /-- 3 entries: open topology, sequential grammar (e.g. f75r, f79v, f80v) -/")
w("  def voynich_frob_open_seq : Synthon :=")
f2 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == '𐑹' and g['tuple']['Þ'] == '𐑸'][0]
w(f"    {mk_synthon(f2['tuple'])}")
w("  theorem voynich_frob_open_seq_tier : synthonTier voynich_frob_open_seq = .O_∞ := by")
w("    native_decide")
w("")

w("  /-- 1 entry: crossing topology, broadcast grammar (e.g. f46r) -/")
w("  def voynich_frob_cross_broad : Synthon :=")
f3 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == '𐑹' and g['tuple']['ɢ'] == 'ɢ^Ş'][0]
w(f"    {mk_synthon(f3['tuple'])}")
w("  theorem voynich_frob_cross_broad_tier : synthonTier voynich_frob_cross_broad = .O_∞ := by")
w("    native_decide")
w("")

w("end CorpusComparison")
w("")
w("end Manuscript_ZFCt")

result = '\n'.join(L)
with open('Manuscript_ZFCt.lean', 'w') as f:
    f.write(result)
print(f"Generated {len(L)} lines, {len(result)} chars")
print(f"File written: Manuscript_ZFCt.lean")
# Count theorems
nth = sum(1 for l in L if l.strip().startswith('theorem '))
print(f"Theorems: {nth}")
