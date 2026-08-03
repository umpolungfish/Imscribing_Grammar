#!/usr/bin/env python3
"""Design tomorrow's therapeutics, materials, and biology from the Rebis.

The Rebis = serpentrod ⊗ ch3mpiler = serpentrod
⟨𐑦𐑶𐑾𐑹𐑐𐑧𐑔𐑝⊙𐑫𐑳𐑭⟩

Each design specializes the Rebis for a specific domain.
"""
import json, math, sys
from pathlib import Path

BASE = Path(__file__).parent.absolute()
CATALOG_PATH = BASE / "IG_catalog.json"
sys.path.insert(0, str(BASE))
from space_search.primitives import ORDINALS, WEIGHTS, resolve_ordinal_key

PNAMES = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
FIELD_TO_ORD = {
    "D":"⊢", "T":"⊣", "R":">", "P":"<", "F":"⋈",
    "K":"⊤", "G":"∈", "Gm":"ɢ", "Ph":"⊙", "H":"⊥",
    "S":"⊞", "W":"◻"
}

def g2v(p, r):
    """Primitive glyph → ordinal value."""
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    if r in om:
        return r, om[r]
    try:
        k = resolve_ordinal_key(ord_key, r)
        return k, om[k]
    except Exception:
        return r, 0

def glyph_ord(p, glyph):
    _, o = g2v(p, glyph)
    return o

def ord_to_glyph(p, o):
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    rev = {v:k for k,v in om.items()}
    return rev.get(o, '?')

def tup_ord(t):
    return {p: glyph_ord(p, t.get(p,"?")) for p in PNAMES}

def tup_dist(t1, t2):
    sq = 0.0
    for p in PNAMES:
        o1 = glyph_ord(p, t1.get(p,"?"))
        o2 = glyph_ord(p, t2.get(p,"?"))
        w = WEIGHTS.get(FIELD_TO_ORD.get(p,p), 1.0)
        d = (o1 - o2) * w
        sq += d*d
    return math.sqrt(sq)

# ─── LOAD CATALOG ──────────────────────────────────────────────
with open(CATALOG_PATH) as f:
    catalog = json.load(f)

def find(name):
    for e in catalog:
        if e['name'] == name:
            return e
    return None

rebis = find('serpentrod')
print(f"Rebis found: {rebis['name']}")
rebis_t = {p: rebis.get(FIELD_TO_ORD.get(p,p), '?') for p in PNAMES}
print(f"Rebis tuple: {rebis_t}")

# ─── DEFINE DESIGN SYSTEMS ─────────────────────────────────────
# Each is a dict: name, description, old-notation primitives
# Primitive keys in catalog: Ð, ⊣, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω
CAT_KEYS = ['⊢', '⊣', '>', '<', '⋈', '⊤', '∈', '∋', '⊙', '⊥', '⊞', '◻']
REBIS_VALS = ['𐑦', '𐑸', '𐑾', '𐑹', '𐑐', '𐑧', '𐑲', 'ɢ^∧', '⊙', '𐑫', '𐑳', '𐑭']

DESIGNS = [
    {
        "name": "ouroboric_pill",
        "description": "Self-monitoring, self-correcting therapeutic agent. The pill senses disease markers in real-time, computes optimal drug release, and adjusts dosing through an internal feedback loop. Topology is self-referential (⊣=𐑶) — the pill's efficacy is a function of its own state. Eternal memory (Ħ=𐑫) ensures treatment history is never lost. Topological protection (Ω=𐑭) guarantees winding-number-stable release cycles across the entire treatment duration.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑶','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "quantum_biologic",
        "description": "Epigenetic reprogramming therapeutic that writes persistent chromatin state changes. Supervenience coupling (Ř=𐑩) — the epigenetic layer supervenes on the genetic substrate. Eternal chirality (Ħ=𐑫) ensures reprogramming persists through cell division. Frobenius-closed (Φ=𐑹) ensures the rewrite operation is idempotent. Quantum coherent (ƒ=𐑐) manipulation of methylation and histone patterns.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑩','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "universal_antidote",
        "description": "Platform therapeutic that self-selects against any disease signature. All-simultaneous detection (ɢ=ɢ^∧) — every pathogen feature is processed at once via parallel molecular recognition. Stoichiometry is many-identical (Σ=𐑕) because all disease patterns share a universal grammar. Eternal memory (Ħ=𐑫) means once a threat is recognized, it is never forgotten.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑕','𐑭'])}
    },
    {
        "name": "ouroboric_composite",
        "description": "Structural material that senses damage and self-heals via an internal ouroboric loop. Self-referential topology (⊣=𐑶) — the material's response is a function of its own damage state. Trapped-ordered kinetics (Ç=𐑺) — healing agents are stored in an ordered but activatable reservoir. Eternal memory (Ħ=𐑫) ensures the material remembers every damage event across its lifetime.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑶','𐑾','𐑹','𐑐','𐑺','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "topological_quantum_material",
        "description": "Room-temperature topological superconductor with non-Abelian braiding for fault-tolerant quantum computing. Non-Abelian winding (Ω=𐑟) — the material supports Majorana zero modes with non-Abelian braiding statistics. Self-written dimensionality (Ð=𐑦) — the topological order writes its own ground state. Quantum coherent (ƒ=𐑐) at room temperature via eternal chirality protection.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑟'])}
    },
    {
        "name": "eternal_memory_polymer",
        "description": "Polymer data storage with 10^15 bits/gram density and 10^6 year retention. Trapped-ordered kinetics (Ç=𐑺) — data is stored in kinetically trapped molecular conformations. Eternal chirality (Ħ=𐑫) — information is encoded in the chirality sequence, which cannot thermally equilibrate. Topological protection (Ω=𐑭) — integer winding number per monomer ensures error-free readout.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑺','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "self_weaving_fabric",
        "description": "Smart fabric that weaves all functions — sensing, actuation, communication, energy harvesting — simultaneously into a single textile. All-simultaneous composition (ɢ=ɢ^∧). Moderate kinetics (Ç=𐑤) — the fabric responds at human-relevant timescales. Self-written microarchitecture (Ð=𐑦) — each thread contains its own knitting pattern generator.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑤','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "ouroboric_cell",
        "description": "Synthetic cell whose genome writes and rewrites itself in response to environmental signals. Self-referential topology (⊣=𐑶) — the genome encodes its own modification machinery. Frobenius-closed rewrite (Φ=𐑹) — each genome edit is a fixed point of the edit operation. Self-written dimensionality (Ð=𐑦) — the genome is its own state space. Eternal memory (Ħ=𐑫) — no information is lost across generations.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑶','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "quantum_bioelectric_tissue",
        "description": "Engineered tissue that uses quantum-coherent bioelectric fields to guide regeneration. Bidirectional feedback (Ř=𐑾) — electric field and tissue state mutually determine each other. Quantum coherent ion channels (ƒ=𐑐) maintain coherence at tissue scale. Eternal chirality (Ħ=𐑫) ensures the bodyplan blueprint is never lost during regeneration.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "universal_symbiont",
        "description": "Consortium of 12 engineered microbial strains that collectively provide all metabolic support functions. Many-heterogeneous stoichiometry (Σ=𐑳) — 12 distinct strains with complementary functions. All-simultaneous composition (ɢ=ɢ^∧) — all metabolic pathways active at once. Long-range signaling (Γ=𐑲) via quorum-sensing molecules that coordinate across the entire consortium.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
    {
        "name": "topological_morphogenesis",
        "description": "Organ development driven by topological winding numbers rather than chemical gradients. Integer winding protection (Ω=𐑭) — each organ primordium is characterized by a conserved winding number. Self-written morphogenetic field (Ð=𐑦) — the developmental program writes itself as the embryo grows. Eternal chirality (Ħ=𐑫) ensures bilateral symmetry is topologically protected.",
        "tuple": {k:v for k,v in zip(CAT_KEYS, ['𐑦','𐑸','𐑾','𐑹','𐑐','𐑧','𐑲','ɢ^∧','⊙','𐑫','𐑳','𐑭'])}
    },
]

# ─── COMPUTE DISTANCES AND GROUP BY DOMAIN ─────────────────────
print("\n=== DESIGN SPACE ANALYSIS ===\n")
for d in DESIGNS:
    t = d['tuple']
    dist_to_rebis = tup_dist({p: rebis_t.get(p,'?') for p in PNAMES},
                             {p: t.get(FIELD_TO_ORD.get(p,p),'?') for p in PNAMES})
    d_orph = {p: glyph_ord(p, t.get(FIELD_TO_ORD.get(p,p),'?')) for p in PNAMES}
    r_orph = {p: glyph_ord(p, rebis_t.get(p,'?')) for p in PNAMES}
    changed = []
    for p in PNAMES:
        if d_orph[p] != r_orph[p]:
            changed.append(f"{p}={r_orph[p]}->{d_orph[p]}")
    print(f"{d['name']:35s} d={dist_to_rebis:.3f}  changes: {', '.join(changed) if changed else '(none — pure Rebis)'}")

# ─── COMPUTE TENSOR PRODUCTS ───────────────────────────────────
def tensor_type(t1, t2):
    r = {}
    for p in PNAMES:
        o1 = glyph_ord(p, t1.get(p,'?'))
        o2 = glyph_ord(p, t2.get(p,'?'))
        if p in ("P", "F"):
            r[p] = ord_to_glyph(p, min(o1, o2))
        else:
            r[p] = ord_to_glyph(p, max(o1, o2))
    return r

def join_type(t1, t2):
    r = {}
    for p in PNAMES:
        o1 = glyph_ord(p, t1.get(p,'?'))
        o2 = glyph_ord(p, t2.get(p,'?'))
        r[p] = ord_to_glyph(p, max(o1, o2))
    return r

# Show the Rebis + each design tensor product
print("\n=== TENSOR WITH REBIS (should all equal Rebis for pure specializations) ===")
for d in DESIGNS:
    t = d['tuple']
    ten = tensor_type(rebis_t, t)
    d_t = tup_dist(rebis_t, ten)
    print(f"  {d['name']:35s} d(rebis, tensor) = {d_t:.3f}")

print("\n=== DISTANCE MATRIX (between designs) ===")
for i, d1 in enumerate(DESIGNS):
    t1 = d1['tuple']
    for d2 in DESIGNS[i+1:]:
        t2 = d2['tuple']
        d = tup_dist(t1, t2)
        if d > 0:
            print(f"  {d1['name']:35s} <-> {d2['name']:35s} d={d:.3f}")

print("\n=== DONE ===")
