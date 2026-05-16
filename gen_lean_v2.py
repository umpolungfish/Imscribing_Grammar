#!/usr/bin/env python3
"""Generate corrected Manuscript_ZFCt.lean v2 — no duplicate names, correct tiers."""
import json

with open('manuscript_zfct.json') as f:
    data = json.load(f)

# ── Primitive name mapping (JSON → Lean) ──────────────────────
M = {
    'Ð_ω': 'Dimensionality.D_omega', 'Ð_C': 'Dimensionality.D_turnthree',
    'Ð_;': 'Dimensionality.D_wynn', 'Ð_ß': 'Dimensionality.D_invomega',
    'Þ_O': 'Topology.T_openo', 'Þ_¨': 'Topology.T_bullseye',
    'Þ_K': 'Topology.T_invscr', 'Þ_ò': 'Topology.T_box', 'Þ_6': 'Topology.T_nrleg',
    'Ř_=': 'Relational.R_lyoghlig', 'Ř_Ť': 'Relational.R_downstep',
    'Ř_¯': 'Relational.R_subrightarrow', 'Ř_ý': 'Relational.R_ctz',
    'Φ_υ': 'Polarity.P_aolig', 'Φ_ɐ': 'Polarity.P_aolig',
    'Φ_F': 'Polarity.P_pipevar', 'Φ_˙': 'Polarity.P_subdoublearrow',
    'Φ_}': 'Polarity.P_doublebarpipe',
    'ƒ_ì': 'Fidelity.F_beltl', 'ƒ_ð': 'Fidelity.F_dh', 'ƒ_ż': 'Fidelity.F_hardsign',
    'Ç_Ù': 'KineticChar.K_teshlig', 'Ç_@': 'KineticChar.K_schwa',
    'Ç_W': 'KineticChar.K_frtailgamma', 'Ç_-': 'KineticChar.K_turnm', 'Ç_λ': 'KineticChar.K_lambda',
    'Γ_ʔ': 'Granularity.G_revapostrophe', 'Γ_β': 'Granularity.G_beta', 'Γ_γ': 'Granularity.G_gamma',
    'ɢ_^': 'Grammar.Gamma_seq', 'ɢ_ˌ': 'Grammar.Gamma_seq', 'ɢ_Ş': 'Grammar.Gamma_broad',
    'ɢ_˝': 'Grammar.Gamma_or',
    'φ̂_ÿ': 'Criticality.Phi_ctyogh', 'φ̂_Æ': 'Criticality.Phi_closerevepsilon',
    'φ̂_3': 'Criticality.Phi_revepsilon', 'φ̂_ž': 'Criticality.Phi_softsign', 'φ̂_Ţ': 'Criticality.Phi_upstep',
    'Ħ_!': 'Chirality.H_invscripta', 'Ħ_£': 'Chirality.H_toneletterstem',
    'Ħ_Ñ': 'Chirality.H_closeomega', 'Ħ_A': 'Chirality.H_turntwo',
    'Σ_S': 'Stoichiometry.S_doublebaresh', 'Σ_ő': 'Stoichiometry.S_ctn', 'Σ_ï': 'Stoichiometry.S_ltailm',
    'Ω_z': 'Protection.Omega_dzlig', 'Ω_Å': 'Protection.Omega_closeepsilon',
    'Ω_2': 'Protection.Omega_crtwo', 'Ω_5': 'Protection.Omega_turna',
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
            f'    crit := {M[tup["φ̂"]]},\n'
            f'    chir := {M[tup["Ħ"]]},\n'
            f'    stoi := {M[tup["Σ"]]},\n'
            f'    prot := {M[tup["Ω"]]} }}')

def tier(tup):
    p, o, d = tup['Φ'], tup['Ω'], tup['Ð']
    if p == 'Φ_}': return '.O_inf'  # P_doublebarpipe → Frobenius
    if o == 'Ω_z' or o == 'Ω_2' or o == 'Ω_5':  # non-trivial Ω
        if d == 'Ð_ß': return '.O_2dag'  # D_invomega
        return '.O_2'  # finite D
    return '.O_1'  # Omega_0

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
    if tup['Φ'] != 'Φ_υ':
        label = {'Φ_F': 'sym_F', 'Φ_}': 'sym_cl', 'Φ_˙': 'sym_all'}
        parts.append(label.get(tup['Φ'], f"sym_{tup['Φ'][-1]}"))
    # grammar variant
    if tup['ɢ'] == 'ɢ_Ş':
        parts.append("broad")
    # topology variant (skip if default)
    if tup['Þ'] == 'Þ_K':
        parts.append("incl")
    elif tup['Þ'] == 'Þ_¨':
        parts.append("cross")
    # memory variant
    if tup['Ħ'] == 'Ħ_Ñ':
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
            f'      crit := {M[tup["φ̂"]]},\n'
            f'      chir := {M[tup["Ħ"]]},\n'
            f'      stoi := {M[tup["Σ"]]},\n'
            f'      prot := {M[tup["Ω"]]} }}')

# Correction: the old voynich_tier was wrong. P_aolig → O_2 not O_inf.

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
w(f"  theorem voynich_main_tier : synthonTier voynich_main = .O_2 := by")
w("    native_decide")
w("")

w("  /-- Most frequent Rohonc structural type -/")
w("  def rohonc_main : Synthon :=")
w(f"    {mk_synthon(mc['rohonc']['tuple'])}")
w(f"  theorem rohonc_main_tier : synthonTier rohonc_main = .O_2 := by")
w("    native_decide")
w("")

w("  /-- Most frequent Linear A structural type -/")
w("  def linearA_main : Synthon :=")
w(f"    {mk_synthon(mc['linear_a']['tuple'])}")
w(f"  theorem linearA_main_tier : synthonTier linearA_main = .O_2 := by")
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
f1 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == 'Φ_}' and g['tuple']['Þ'] == 'Þ_¨' and g['tuple']['ɢ'] == 'ɢ_^'][0]
w(f"    {mk_synthon(f1['tuple'])}")
w("  theorem voynich_frob_cross_seq_tier : synthonTier voynich_frob_cross_seq = .O_inf := by")
w("    native_decide")
w("")

w("  /-- 3 entries: open topology, sequential grammar (e.g. f75r, f79v, f80v) -/")
w("  def voynich_frob_open_seq : Synthon :=")
f2 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == 'Φ_}' and g['tuple']['Þ'] == 'Þ_O'][0]
w(f"    {mk_synthon(f2['tuple'])}")
w("  theorem voynich_frob_open_seq_tier : synthonTier voynich_frob_open_seq = .O_inf := by")
w("    native_decide")
w("")

w("  /-- 1 entry: crossing topology, broadcast grammar (e.g. f46r) -/")
w("  def voynich_frob_cross_broad : Synthon :=")
f3 = [g for _, g in CORPORA['voynich'].items() if g['tuple']['Φ'] == 'Φ_}' and g['tuple']['ɢ'] == 'ɢ_Ş'][0]
w(f"    {mk_synthon(f3['tuple'])}")
w("  theorem voynich_frob_cross_broad_tier : synthonTier voynich_frob_cross_broad = .O_inf := by")
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
