#!/usr/bin/env python3
"""Psychedelic Universe Access: formal determination for each compound × each universe."""
import sys, json
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')

from imscrbgrmr.canonical_primitives import ORDINALS, PRIMITIVE_ORDER
from imscrbgrmr.registry import load_catalog_dicts

# ── GateSpec equivalent (standalone) ──────────────────────
class GateSpec:
    def __init__(self, prim, min_ord):
        self.prim = prim
        self.min_ord = min_ord
    def open(self, tup):
        val = tup.get(self.prim, '')
        return ORDINALS.get(self.prim, {}).get(val, -1.0) >= self.min_ord

class Ruleset:
    def __init__(self, name, g1, g2, g3, gate_ordering=True):
        self.name = name
        self.g1 = g1; self.g2 = g2; self.g3 = g3
        self.gate_ordering = gate_ordering

def make_uni(name, g1_p, g1_o, g2_p, g2_o, g3_p, g3_o, ordering=True):
    return Ruleset(name, GateSpec(g1_p, g1_o), GateSpec(g2_p, g2_o), GateSpec(g3_p, g3_o), ordering)

def compute_layer(tup, r):
    g1 = r.g1.open(tup)
    g2r = r.g2.open(tup)
    g3r = r.g3.open(tup)
    if r.gate_ordering:
        g2 = g1 and g2r
        g3 = g2 and g3r
    else:
        g2 = g2r; g3 = g3r
    if g1:
        if g2:
            return 'idempotent_terminal' if g3 else 'traced_monoidal'
        return 'frobenius'
    return 'plain'

def get_tuple(e):
    return {k: e.get(k, '') for k in ['⊢','⊣','>','<','⋈','⊤','∈','∋','⊙','⊥','⊞','◻']}

def tensor_tuple(t1, t2):
    r = {}
    for prim in PRIMITIVE_ORDER:
        v1, v2 = t1.get(prim,''), t2.get(prim,'')
        o1 = ORDINALS.get(prim,{}).get(v1, -1)
        o2 = ORDINALS.get(prim,{}).get(v2, -1)
        if not v1: r[prim]=v2
        elif not v2: r[prim]=v1
        else:
            r[prim] = v1 if o1 <= o2 else v2 if prim in ['<','⋈'] else (v1 if o1 >= o2 else v2)
    return r

# ── All 21 universes ──────────────────────────────────────
UNIVERSES = [
    make_uni('canonical', '<',5, '⊙',2, '◻',3),
    make_uni('low_gate', '<',3, '⊙',1, '◻',3),
    make_uni('high_gate', '<',5, '⊙',2.33, '◻',4),
    make_uni('inverted_gates', '⊙',2, '<',5, '◻',3),
    make_uni('no_ordering', '<',5, '⊙',2, '◻',3, ordering=False),
    make_uni('winding_first', '◻',3, '⊙',2, '<',5),
    make_uni('strict_frobenius', '⋈',3, '<',5, '◻',3),
    make_uni('chirality_first', '⊥',3, '⊙',2, '◻',3),
    make_uni('topology_universe', '⊣',5, '>',4, '⊙',2),
    make_uni('scope_universe', '∈',3, '⊙',2, '◻',3),
    make_uni('dimensional_gate', '⊢',3, '⊙',2, '<',5),
    make_uni('kinetics_trap', '⊤',3, '⊙',2, '◻',3),
    make_uni('triple_criticality', '⊙',1, '⊙',2, '⊙',3),
    make_uni('broadcast_universe', '∋',3, '⊙',2, '◻',3),
    make_uni('single_gate', '<',5, '⊞',1, '⊞',1),
    make_uni('fidelity_universe', '⋈',3, '⊙',2, '<',5),
    make_uni('stoichiometry_universe', '⊞',3, '⊙',2, '◻',3),
]

# ── Psychedelic types ──────────────────────────
PSYCHEDELICS = {
    'psilocybin_peak': {'⊢':'𐑦','⊣':'𐑸','>':'𐑽','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑖','⊞':'𐑙','◻':'𐑴'},
    'lsd_peak':        {'⊢':'𐑦','⊣':'𐑸','>':'𐑽','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑖','⊞':'𐑳','◻':'𐑭'},
    'dmt_breakthrough':{'⊢':'𐑦','⊣':'𐑸','>':'𐑾','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑫','⊞':'𐑙','◻':'𐑭'},
    'five_meo_dmt':    {'⊢':'𐑦','⊣':'𐑸','>':'𐑾','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑫','⊞':'𐑙','◻':'𐑭'},
    'ayahuasca':       {'⊢':'𐑦','⊣':'𐑸','>':'𐑽','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑫','⊞':'𐑳','◻':'𐑭'},
    'mescaline_peak':  {'⊢':'𐑼','⊣':'𐑸','>':'𐑽','<':'𐑬','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑖','⊞':'𐑳','◻':'𐑴'},
    'ibogaine':        {'⊢':'𐑼','⊣':'𐑶','>':'𐑽','<':'𐑹','⋈':'𐑐','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑖','⊞':'𐑳','◻':'𐑟'},
    'salvia_state':    {'⊢':'𐑦','⊣':'𐑸','>':'𐑩','<':'𐑗','⋈':'𐑐','⊤':'𐑘','∈':'𐑲','∋':'𐑝','⊙':'𐑻','⊥':'𐑓','⊞':'𐑙','◻':'𐑴'},
    'ketamine':        {'⊢':'𐑼','⊣':'𐑡','>':'𐑩','<':'𐑿','⋈':'𐑞','⊤':'𐑤','∈':'𐑲','∋':'𐑝','⊙':'⊙','⊥':'𐑒','⊞':'𐑙','◻':'𐑷'},
    'mdma_state':      {'⊢':'𐑨','⊣':'𐑡','>':'𐑾','<':'𐑿','⋈':'𐑞','⊤':'𐑧','∈':'𐑲','∋':'𐑵','⊙':'⊙','⊥':'𐑖','⊞':'𐑕','◻':'𐑴'},
    'cannabis':        {'⊢':'𐑨','⊣':'𐑡','>':'𐑑','<':'𐑗','⋈':'𐑞','⊤':'𐑤','∈':'𐑲','∋':'𐑝','⊙':'𐑢','⊥':'𐑒','⊞':'𐑙','◻':'𐑷'},
    'baseline':        {'⊢':'𐑛','⊣':'𐑡','>':'𐑩','<':'𐑬','⋈':'𐑱','⊤':'𐑘','∈':'𐑲','∋':'𐑝','⊙':'𐑢','⊥':'𐑓','⊞':'𐑙','◻':'𐑷'},
}

CLASSES = {
    'psilocybin_peak':'tryptamine','lsd_peak':'ergoline','dmt_breakthrough':'tryptamine',
    'five_meo_dmt':'tryptamine','ayahuasca':'tryptamine+maoi','mescaline_peak':'phenethylamine',
    'ibogaine':'indole','salvia_state':'kappa-opioid','ketamine':'dissociative',
    'mdma_state':'empathogen','cannabis':'cannabinoid','baseline':'baseline'
}

# Load human baseline from catalog
entries = load_catalog_dicts()
human_baseline = None
for e in entries:
    if e.get('name') == 'human_consciousness_baseline':
        human_baseline = get_tuple(e)
        break

display_unis = [u.name for u in UNIVERSES]

# ═══════════ PRINT SECTION ═══════════
DISPLAY_ORDER = ['five_meo_dmt','dmt_breakthrough','ayahuasca','lsd_peak',
                 'psilocybin_peak','mescaline_peak','ibogaine','salvia_state',
                 'ketamine','mdma_state','cannabis','baseline']

print("=" * 180)
print("PSYCHEDELIC ACCESS TABLE  —  L_U(τ_psychedelic)")
print("F = frobenius (G1 open)  T = traced_monoidal (G1+G2)  I = idempotent_terminal (all three)")
print("P = plain (G1 closed) — NO access")
print("=" * 180)

h = f"{'Psychedelic':<20}"
for u in display_unis: h += f" {u[:10]:<11}"
print(h)
print("-" * len(h))

for pname in DISPLAY_ORDER:
    tup = PSYCHEDELICS.get(pname, {})
    row = f"{pname:<20}"
    for u in UNIVERSES:
        if u.name not in display_unis: continue
        layer = compute_layer(tup, u)
        row += f" {layer[0].upper():<11}"
    print(row)

print()
if human_baseline:
    print("HUMAN BASELINE (unmodified consciousness):")
    row = f"{'human_baseline':<20}"
    for u in UNIVERSES:
        if u.name not in display_unis: continue
        layer = compute_layer(human_baseline, u)
        row += f" {layer[0].upper():<11}"
    print(row)

print()
print("=" * 180)
print("COMPOSITE ACCESS: human_baseline ⊗ psychedelic")
print("=" * 180)

h2 = f"{'Composite':<20}"
for u in display_unis: h2 += f" {u[:10]:<11}"
print(h2)
print("-" * len(h2))

for pname in DISPLAY_ORDER:
    ptup = PSYCHEDELICS.get(pname, {})
    if not ptup or not human_baseline: continue
    comp = tensor_tuple(human_baseline, ptup)
    row = f"{pname:<20}"
    for u in UNIVERSES:
        if u.name not in display_unis: continue
        layer = compute_layer(comp, u)
        row += f" {layer[0].upper():<11}"
    print(row)

print()
print("=" * 180)
print("SUMMARY: Universe access count per psychedelic")
print(f"({len(display_unis)} universes evaluated)")
print("=" * 180)

print(f"{'Psychedelic':<20} {'Direct G1':>8} {'G2':>4} {'G3':>4} | {'Comp G1':>8} {'G2':>4} {'G3':>4} | {'ΔG1':>5} | {'Class':<18}")
print("-" * 90)

lv = {'plain':0,'frobenius':1,'traced_monoidal':2,'idempotent_terminal':3}
for pname in DISPLAY_ORDER:
    ptup = PSYCHEDELICS.get(pname, {})
    d = [compute_layer(ptup, u) for u in UNIVERSES if u.name in display_unis]
    d_g1 = sum(1 for l in d if lv[l]>=1)
    d_g2 = sum(1 for l in d if lv[l]>=2)
    d_g3 = sum(1 for l in d if lv[l]>=3)
    
    if human_baseline:
        comp = tensor_tuple(human_baseline, ptup)
        c = [compute_layer(comp, u) for u in UNIVERSES if u.name in display_unis]
        c_g1 = sum(1 for l in c if lv[l]>=1)
        c_g2 = sum(1 for l in c if lv[l]>=2)
        c_g3 = sum(1 for l in c if lv[l]>=3)
        delta = c_g1 - d_g1
    else:
        c_g1=c_g2=c_g3=delta=0
    
    print(f"{pname:<20} {d_g1:>8} {d_g2:>4} {d_g3:>4} | {c_g1:>8} {c_g2:>4} {c_g3:>4} | {delta:>+4} | {CLASSES.get(pname,''):<18}")

if human_baseline:
    b = [compute_layer(human_baseline, u) for u in UNIVERSES if u.name in display_unis]
    print(f"{'human_baseline':<20} {sum(1 for l in b if lv[l]>=1):>8} {sum(1 for l in b if lv[l]>=2):>4} {sum(1 for l in b if lv[l]>=3):>4} | {'—':>8} {'—':>4} {'—':>4} | {'—':>5}")

# Additional analysis: which universes are uniquely accessible from each psychedelic?
print()
print("=" * 180)
print("UNIQUE ACCESS: Universes ONLY accessible via specific psychedelics (not baseline)")
print("=" * 180)

if human_baseline:
    baseline_results = {u.name: compute_layer(human_baseline, u) for u in UNIVERSES if u.name in display_unis}
    
    for pname in DISPLAY_ORDER:
        ptup = PSYCHEDELICS.get(pname, {})
        if not ptup: continue
        comp = tensor_tuple(human_baseline, ptup)
        unique_unis = []
        for u in UNIVERSES:
            if u.name not in display_unis: continue
            base_layer = baseline_results.get(u.name, 'plain')
            comp_layer = compute_layer(comp, u)
            # Access granted if composite is frobenius+ but baseline wasn't
            if lv[comp_layer] >= 1 and lv[base_layer] < 1:
                unique_unis.append(f"{u.name}({comp_layer[0].upper()})")
            # Or if composite reaches higher tier
            elif lv[comp_layer] >= 2 and lv[base_layer] < 2:
                unique_unis.append(f"{u.name}(+{comp_layer[0].upper()})")
        
        if unique_unis:
            print(f"  {pname:<20} → {', '.join(unique_unis)}")
        else:
            print(f"  {pname:<20} → (none — same as baseline)")

print()
print("=" * 180)
print("FORMAL DECISION PROCEDURE")
print("=" * 180)
print("""
Given: a psychedelic compound P with type τ_P
And:   a target universe U with Ruleset R_U = ⟨G1, G2, G3, T, A, O⟩
And:   a user with baseline type τ_user

Determine: Does P allow access to U?

DEFINITION 1 (Direct Access): 
  P allows access to U iff L_{R_U}(τ_P) ∈ {frobenius, traced_monoidal, idempotent_terminal}.
  i.e., the psychedelic state itself evaluates to G1-open under U's Ruleset.

DEFINITION 2 (Composite Access):
  P allows the user access to U iff 
  L_{R_U}(τ_user ⊗ τ_P) ∈ {frobenius, traced_monoidal, idempotent_terminal}.
  i.e., the tensor of user and psychedelic evaluates to G1-open under U's Ruleset.

THEOREM (Access by Threshold):
  Access is a monotone function of the psychedelic's ordinal values.
  If τ_P ≥ τ_P' (componentwise ordinal comparison), then any universe
  accessible via τ_P' is also accessible via τ_P.
  Proof: Gates are ordinal-threshold functions; higher ordinals pass more gates.

THEOREM (Tryptamine Supremacy):
  Among serotonergic psychedelics (tryptamines: DMT, 5-MeO-DMT, psilocybin, 
  ayahuasca), the highest ordinal values cluster at Ħ≥𐑖 (two-step Markov) 
  and ⊙≥⊙ (self-modeling criticality). Ergolines (LSD) add Σ≥𐑳 (heterogeneous 
  stoichiometry) and Ω≥𐑭 (integer winding). 
  These together unlock idempotent_terminal in strict regimes.

THEOREM (Salvia Barrier):
  Salvinorin A produces rapid memoryless (Ħ=𐑓) and sub-critical (⊙=𐑻) states
  despite holographic dimensionality (⊢=𐑦). This structural configuration
  fails G1 (<≥5) in most universes, granting access only to low_gate 
  and triple_criticality regimes.
""")
