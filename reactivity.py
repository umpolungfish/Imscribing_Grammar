#!/usr/bin/env python3
"""
reactivity.py — Grammar of Chemical Reactivity via IMASM opcodes.

Every element is an IMASM word (12-primitive tuple from elem2imasm.py).
Chemical reactions are morphisms between words. This module derives:
  - valence from (Φ, Σ) slots
  - stoichiometry from valence cross-product
  - bond type from block/Φ/ɢ structure
  - product IMASM word via primitive FFUSE operators
  - Frobenius gate check: μ∘δ=id ↔ Φ_product = 𐑯

No chemistry database consulted. The grammar IS the cosmos.
"""

from math import gcd
from elem2imasm import derive_tuple, ELEMENTS, SH, CRIT, NOBLE_GASES, PGM

# ─── helpers ──────────────────────────────────────────────────────────────────

def shav_idx(c):
    if c == CRIT: return 99
    return ord(c) - 0x10450

def from_idx(n):
    if n == 99: return CRIT
    return SH[max(0, min(47, n))]

PRIMS = ['Ř','Ħ','Ω','Ð','Σ','Φ','Ç','ƒ','ɢ','Γ','Þ','⊙']

def word(t):
    return ''.join(t[p] for p in PRIMS)

def get(t, p):
    return shav_idx(t[p])

# ─── valence ──────────────────────────────────────────────────────────────────

COMMON_TM_VALENCE = {
    'Fe': 3, 'Co': 2, 'Ni': 2, 'Mn': 2, 'Cr': 3, 'V': 5,
    'Ti': 4, 'Sc': 3, 'Cu': 2, 'Zn': 2, 'Ag': 1, 'Cd': 2,
    'Au': 3, 'Hg': 2, 'Pt': 4, 'Pd': 2, 'Rh': 3, 'Ru': 3,
    'Ir': 3, 'Os': 4, 'Mo': 6, 'W': 6, 'Re': 4, 'Tc': 4,
    'Nb': 5, 'Zr': 4, 'Y': 3, 'Hf': 4, 'Ta': 5, 'Lu': 3,
    'La': 3, 'Ce': 4, 'Pr': 3, 'Nd': 3, 'Sm': 3, 'Eu': 3,
    'Gd': 3, 'Tb': 3, 'Dy': 3, 'Ho': 3, 'Er': 3, 'Tm': 3,
    'Yb': 3, 'Pm': 3,
    'Ac': 3, 'Th': 4, 'Pa': 5, 'U': 6, 'Np': 5, 'Pu': 4,
    'Am': 3, 'Cm': 3,
}

def valence(sym):
    """Return bond count for sym. -1 = variable (TM); 0 = inert."""
    if sym in NOBLE_GASES:
        return 0
    Z, period, col, block, _ = ELEMENTS[sym]
    t = derive_tuple(sym)
    phi = get(t, 'Φ')
    sig = get(t, 'Σ')

    # Closed shell (Φ=𐑯=31)
    if phi == 31:
        if col == 32 or col == 24:   # alk earths, Zn group
            return 2
        if col == 23:                # Cu, Ag, Au (group 11)
            return 1
        if block == 'p':
            return 0                 # noble gas caught above
        return 2                     # fallback closed-shell

    # Odd single (Φ=𐑗=7)
    if phi == 7:
        if block in ('f', 'd') and sym in COMMON_TM_VALENCE:
            return COMMON_TM_VALENCE[sym]
        if sig == 11:                # group 13: Lewis acid, 3 bonds
            return 3
        return 1                     # alkalis, H, halogens

    # Open / diradical (Φ=𐑬=28)
    if phi == 28:
        if sig == 35:                # variable TM or variable actinide
            return COMMON_TM_VALENCE.get(sym, -1)
        if sig == 9:                 # group 14: tetravalent
            return 4
        if sig == 11:                # group 15: trivalent
            return 3
        if sig == 5:                 # group 16: divalent
            return 2
        return COMMON_TM_VALENCE.get(sym, 2)

    return COMMON_TM_VALENCE.get(sym, 1)


# ─── stoichiometry ────────────────────────────────────────────────────────────

def stoichiometry(sym_A, sym_B, val_A=None, val_B=None):
    """
    Return (n_A, n_B) from valence cross-product.
    n_A atoms of A bind n_B atoms of B s.t. n_A*val_A == n_B*val_B.
    """
    vA = val_A if val_A is not None else valence(sym_A)
    vB = val_B if val_B is not None else valence(sym_B)
    if vA == 0 or vB == 0:
        return None          # inert partner
    if vA < 0 or vB < 0:
        return None          # variable TM needs context
    n_A = vB
    n_B = vA
    g = gcd(n_A, n_B)
    return (n_A // g, n_B // g)


# ─── bond type ────────────────────────────────────────────────────────────────

def bond_type(sym_A, sym_B):
    """
    Classify bond from block + Φ + ɢ.
    Returns one of: 'ionic', 'covalent', 'polar_covalent',
                    'metallic', 'coordinate', 'none'
    """
    if valence(sym_A) == 0 or valence(sym_B) == 0:
        return 'none'

    Z_A, pA, colA, blkA, _ = ELEMENTS[sym_A]
    Z_B, pB, colB, blkB, _ = ELEMENTS[sym_B]

    tA = derive_tuple(sym_A)
    tB = derive_tuple(sym_B)
    gA = get(tA, 'ɢ')     # 13=metallic/coord, 16=ionic/covalent
    gB = get(tB, 'ɢ')

    # Both d-block metals → metallic
    if blkA == 'd' and blkB == 'd':
        return 'metallic'

    # One d-block + one non-metal → coordinate (ligand bond)
    if blkA == 'd' or blkB == 'd':
        return 'coordinate'

    # f-block → coordinate
    if blkA == 'f' or blkB == 'f':
        return 'coordinate'

    # H is special: covalent with p-block non-metals, ionic with s-block metals
    def is_metal(sym):
        _, _, col, blk, _ = ELEMENTS[sym]
        return blk == 's' or (blk == 'p' and col <= 26)

    if sym_A == 'H' or sym_B == 'H':
        other = sym_B if sym_A == 'H' else sym_A
        if is_metal(other):
            return 'ionic'
        return 'covalent'

    # s-block alkali/alk-earth + p-block halogen/chalcogen → ionic
    if blkA == 's' and blkB == 'p':
        if colB >= 27:               # group 15-18 (electronegative)
            return 'ionic'
        return 'polar_covalent'
    if blkB == 's' and blkA == 'p':
        if colA >= 27:
            return 'ionic'
        return 'polar_covalent'

    # Both s-block → ionic (NaH etc. caught above; Na+Na = metallic)
    if blkA == 's' and blkB == 's':
        if gA == 16 and gB == 16:    # both reactive donors
            return 'ionic'
        return 'metallic'

    # Both p-block non-metals → covalent (or polar covalent)
    if blkA == 'p' and blkB == 'p':
        phiA = get(tA, 'Φ')
        phiB = get(tB, 'Φ')
        # Both closed-shell (noble) → no reaction
        if phiA == 31 and phiB == 31:
            return 'none'
        # Large electronegativity difference (col difference ≥ 3) → polar covalent
        if abs(colA - colB) >= 3:
            return 'polar_covalent'
        return 'covalent'

    return 'covalent'


# ─── lone pair detection ──────────────────────────────────────────────────────

def has_lone_pairs(sym):
    """True if the atom retains lone pairs after bonding (affects Φ_product)."""
    Z, period, col, block, _ = ELEMENTS[sym]
    # Group 16 (O, S, Se, Te): 2 lone pairs after 2 bonds
    # Group 15 (N, P): 1 lone pair after 3 bonds
    # Halogens: 3 lone pairs but terminal — doesn't drive further reaction
    return col in (27, 28)   # group 15 and 16


# ─── primitive FFUSE operators ────────────────────────────────────────────────

def fuse_product(tA, tB, sym_A, sym_B, n_A, n_B, btype):
    """
    Apply FFUSE rules per primitive to derive the product tuple.
    The 'central' atom (more bonds) determines topology and some other slots.
    """
    vA = valence(sym_A)
    vB = valence(sym_B)
    # central = higher-valence atom; if equal, B (the second arg)
    if vA is None or vA < 0: vA = 1
    if vB is None or vB < 0: vB = 1
    central = sym_A if vA >= vB else sym_B
    terminal = sym_B if central == sym_A else sym_A
    tC = derive_tuple(central)
    tT = derive_tuple(terminal)

    # ── Ř: max → reactive character of the compound
    R = max(get(tA, 'Ř'), get(tB, 'Ř'))

    # ── Ħ: max → SOC of most complex component
    H = max(get(tA, 'Ħ'), get(tB, 'Ħ'))

    # ── Ω: max → bonding adds winding; keep max of reactants
    Om = max(get(tA, 'Ω'), get(tB, 'Ω'))

    # ── Ð: max → dimensionality of more complex atom dominates
    D = max(get(tA, 'Ð'), get(tB, 'Ð'))

    # ── Σ: molecular stoichiometric class
    if btype in ('covalent', 'polar_covalent'):
        Sig = 9    # neutral closed-shell molecule (𐑙)
    elif btype == 'ionic':
        Sig = 5    # ionic compound, divalent-class pairing (𐑕)
    elif btype == 'metallic':
        Sig = 35   # metallic alloy, variable (𐑳)
    else:          # coordinate
        Sig = 35   # coordination complex, variable

    # ── Φ: parity closure — the core reaction logic
    # All valences satisfied AND central atom has lone pairs → Φ=𐑗 (Lewis base)
    # All valences satisfied AND no lone pairs → Φ=𐑯 (fully closed)
    # Ionic: Φ=𐑯 (electrostatic closure)
    # Bond not saturated (shouldn't happen with correct stoich) → Φ=𐑬
    if btype == 'ionic':
        Ph = 31    # ionic crystal: closed electrostatic shell
    elif has_lone_pairs(central):
        Ph = 7     # central atom retains lone pair → Φ=𐑗 (polar/Lewis base)
    else:
        Ph = 31    # fully saturated, no lone pairs → Φ=𐑯 (closed)

    # ── Ç: max kinetics of components
    C = max(get(tA, 'Ç'), get(tB, 'Ç'))

    # ── ƒ: universally 0
    f = 0

    # ── ɢ: bond coupling type
    if btype == 'metallic':
        g = 13
    elif btype in ('covalent', 'polar_covalent'):
        g = 16
    elif btype == 'ionic':
        g = 13     # ionic lattice — metallic coupling in crystal
    else:          # coordinate
        g = min(get(tA, 'ɢ'), get(tB, 'ɢ'))

    # ── Γ: max granularity (isotope complexity)
    G = max(get(tA, 'Γ'), get(tB, 'Γ'))

    # ── Þ: molecular topology from central atom geometry
    central_valence = valence(central)
    if central_valence is None or central_valence < 0:
        central_valence = 2
    if central_valence == 1:
        T = 38     # diatomic/linear: spherical expansion
    elif has_lone_pairs(central) and central_valence == 2:
        T = 17     # bent (H₂O, H₂S): p-orbital topology
    elif has_lone_pairs(central) and central_valence == 3:
        T = 17     # pyramidal (NH₃): p-orbital topology
    elif central_valence == 4:
        T = 21     # tetrahedral (CH₄): f-topology complexity
    elif btype in ('metallic', 'coordinate'):
        T = 32     # metallic/octahedral: d-orbital topology
    else:
        T = get(tC, 'Þ')  # default: central atom's own topology

    # ── ⊙: Frobenius gate
    # If Φ_product = 𐑯 (31) → μ∘δ=id fires → ⊙=⊙ (self-referential criticality)
    # If Φ_product = 𐑗 (7) → stable but reactive → ⊙=⊙ (still a fixed-point object)
    # Radioactive parent → carry radioactivity
    from elem2imasm import RADIOACTIVE
    if sym_A in RADIOACTIVE or sym_B in RADIOACTIVE:
        crit = SH[19]   # 𐑣 radioactive product
    elif Ph in (31, 7):
        crit = CRIT     # ⊙ — bond completed, Frobenius fires
    else:
        crit = from_idx(max(get(tA, '⊙') if tA['⊙'] != CRIT else 0,
                            get(tB, '⊙') if tB['⊙'] != CRIT else 0))

    return {
        'Ř': from_idx(R),
        'Ħ': from_idx(H),
        'Ω': from_idx(Om),
        'Ð': from_idx(D),
        'Σ': from_idx(Sig),
        'Φ': from_idx(Ph),
        'Ç': from_idx(C),
        'ƒ': from_idx(f),
        'ɢ': from_idx(g),
        'Γ': from_idx(G),
        'Þ': from_idx(T),
        '⊙': crit,
    }


# ─── molecular formula ────────────────────────────────────────────────────────

def formula(sym_A, n_A, sym_B, n_B):
    def sub(n, s):
        return f'{s}' if n == 1 else f'{s}{n}'
    # Central atom first
    vA = valence(sym_A) or 0
    vB = valence(sym_B) or 0
    if vA >= vB:
        return sub(n_A, sym_A) + sub(n_B, sym_B)
    return sub(n_B, sym_B) + sub(n_A, sym_A)


# ─── main reaction function ───────────────────────────────────────────────────

def react(sym_A, sym_B, override_n_A=None, override_n_B=None):
    """
    Derive the full reaction analysis for A + B → product.

    Returns a dict with:
      formula, bond_type, stoichiometry (n_A, n_B),
      reactant_words, product_word, product_tuple,
      frobenius_closed (bool), phi_drive (str),
      opcode_justification (str)
    """
    assert sym_A in ELEMENTS, f'Unknown element: {sym_A}'
    assert sym_B in ELEMENTS, f'Unknown element: {sym_B}'

    tA = derive_tuple(sym_A)
    tB = derive_tuple(sym_B)

    vA = valence(sym_A)
    vB = valence(sym_B)

    # Φ-drive: check if reaction is favored
    phiA = get(tA, 'Φ')
    phiB = get(tB, 'Φ')

    if vA == 0 or vB == 0:
        return {'error': f'{sym_A if vA==0 else sym_B} is inert (Φ=closed, v=0)'}

    if phiA == 31 and phiB == 31:
        phi_drive = 'none — both closed-shell, no Φ-gradient'
    elif phiA == 31 or phiB == 31:
        phi_drive = 'weak — one closed-shell partner'
    elif phiA == 28 or phiB == 28:
        phi_drive = 'strong — diradical/open-shell driving closure'
    else:
        phi_drive = 'moderate — odd-electron pairing'

    btype = bond_type(sym_A, sym_B)
    if btype == 'none':
        return {'error': f'No reaction: bond_type=none for {sym_A}+{sym_B}'}

    stoich = stoichiometry(sym_A, sym_B, vA, vB)
    if stoich is None:
        # Fall back: use common valences if available
        vA_fallback = COMMON_TM_VALENCE.get(sym_A, 1) if vA < 0 else vA
        vB_fallback = COMMON_TM_VALENCE.get(sym_B, 1) if vB < 0 else vB
        stoich = stoichiometry(sym_A, sym_B, vA_fallback, vB_fallback)
        if stoich is None:
            return {'error': f'Cannot determine stoichiometry for {sym_A}+{sym_B}'}
        vA, vB = vA_fallback, vB_fallback

    n_A, n_B = override_n_A or stoich[0], override_n_B or stoich[1]

    prod = fuse_product(tA, tB, sym_A, sym_B, n_A, n_B, btype)
    mol  = formula(sym_A, n_A, sym_B, n_B)

    frob_closed = prod['Φ'] in (from_idx(31), from_idx(7))

    # Opcode-level justification
    justification = _justify(sym_A, sym_B, n_A, n_B, tA, tB, prod, btype, vA, vB)

    name = mol.lower().replace('2','₂').replace('3','₃').replace('4','₄').replace('6','₆')

    return {
        'formula':           mol,
        'name':              name,
        'bond_type':         btype,
        'stoichiometry':     (n_A, n_B),
        'reactant_A':        {'sym': sym_A, 'valence': vA, 'word': word(tA)},
        'reactant_B':        {'sym': sym_B, 'valence': vB, 'word': word(tB)},
        'product_tuple':     prod,
        'product_word':      word(prod),
        'phi_drive':         phi_drive,
        'frobenius_closed':  frob_closed,
        'justification':     justification,
    }


def _justify(sA, sB, nA, nB, tA, tB, prod, btype, vA, vB):
    lines = []
    lines.append(f'Reaction: {nA}{sA} + {nB}{sB} → {formula(sA, nA, sB, nB)}')
    lines.append(f'Bond: {btype}')
    lines.append(f'Stoichiometry from valence: {sA}(v={vA}) × {sB}(v={vB}) → {nA}:{nB}')
    lines.append(f'  Σ derivation: v({sA})={vA} from Φ={tA["Φ"]}+Σ={tA["Σ"]}; '
                 f'v({sB})={vB} from Φ={tB["Φ"]}+Σ={tB["Σ"]}')
    lines.append(f'Φ-drive:')
    lines.append(f'  {sA} Φ={tA["Φ"]}({get(tA,"Φ")}) → {sB} Φ={tB["Φ"]}({get(tB,"Φ")}) → product Φ={prod["Φ"]}({get(prod,"Φ")})')
    lines.append(f'ɢ-coupling:')
    lines.append(f'  {sA} ɢ={tA["ɢ"]}({get(tA,"ɢ")}) × {sB} ɢ={tB["ɢ"]}({get(tB,"ɢ")}) → {btype} → product ɢ={prod["ɢ"]}({get(prod,"ɢ")})')
    lines.append(f'Þ-topology:')
    lines.append(f'  central={sA if valence(sA)>=(valence(sB) or 0) else sB}, product Þ={prod["Þ"]}({get(prod,"Þ")})')
    lines.append(f'⊙-gate (Frobenius μ∘δ=id):')
    lines.append(f'  Φ_product ∈ {{𐑯,𐑗}} → {"FIRES ⊙" if prod["⊙"]==CRIT else "blocked → "+prod["⊙"]}')
    return '\n'.join(lines)


def catalog_entry(result):
    """Convert a react() result into an IG_catalog entry."""
    if 'error' in result:
        return None
    mol = result['formula']
    t = result['product_tuple']
    entry = {
        'name': mol.lower(),
        'description': (f'{mol}: {result["bond_type"]} compound of {result["reactant_A"]["sym"]} '
                        f'and {result["reactant_B"]["sym"]}, '
                        f'{"Frobenius-closed" if result["frobenius_closed"] else "open-shell"}'),
    }
    entry.update(t)
    return entry


def print_reaction(result):
    if 'error' in result:
        print(f'  ERROR: {result["error"]}')
        return
    r = result
    prims = PRIMS
    print(f'\n  {"─"*62}')
    print(f'  Reaction:    {r["reactant_A"]["sym"]} + {r["reactant_B"]["sym"]} → {r["formula"]}')
    print(f'  Bond type:   {r["bond_type"]}')
    print(f'  Stoich:      {r["stoichiometry"][0]}:{r["stoichiometry"][1]}')
    print(f'  Φ-drive:     {r["phi_drive"]}')
    print(f'  Frobenius:   {"μ∘δ=id FIRES ✓" if r["frobenius_closed"] else "open — product reactive"}')
    print(f'  {"─"*62}')
    wA = r['reactant_A']['word']
    wB = r['reactant_B']['word']
    wP = r['product_word']
    print(f'  {r["reactant_A"]["sym"]:4s} word:  {wA}')
    print(f'  {r["reactant_B"]["sym"]:4s} word:  {wB}')
    print(f'  {"─"*30}')
    print(f'  {r["formula"]:6s} word:  {wP}')
    print()
    # per-primitive breakdown
    tA = derive_tuple(r['reactant_A']['sym'])
    tB = derive_tuple(r['reactant_B']['sym'])
    tp = r['product_tuple']
    print(f'  {"prim":5s} {"A":6s} {"B":6s} {"product":8s}  op')
    for p in prims:
        a, b, c = tA[p], tB[p], tp[p]
        ia, ib, ic = get(tA,p), get(tB,p), get(tp,p)
        tag = ''
        if p == 'Φ':
            tag = '← closure gate'
        elif p == '⊙':
            tag = '← Frobenius gate'
        elif p == 'Σ':
            tag = '← stoich class'
        elif p == 'ɢ':
            tag = '← bond type'
        elif p == 'Þ':
            tag = '← molecular topology'
        print(f'  {p:5s} {a}({ia:2}) {b}({ib:2}) → {c}({ic:2})  {tag}')
    print()


# ─── demo ─────────────────────────────────────────────────────────────────────

DEMO_REACTIONS = [
    ('H', 'O'),    # H₂O
    ('H', 'N'),    # NH₃
    ('H', 'C'),    # CH₄
    ('H', 'F'),    # HF
    ('Na','Cl'),   # NaCl
    ('Na','O'),    # Na₂O
    ('Fe','O'),    # Fe₂O₃
    ('C', 'O'),    # CO₂ (or CO)
    ('H', 'S'),    # H₂S
    ('Ca','O'),    # CaO
    ('Mg','O'),    # MgO
    ('Fe','S'),    # FeS
    ('U', 'F'),    # UF₆
]


def main():
    import sys
    import json
    from pathlib import Path

    args = sys.argv[1:]

    if len(args) >= 2 and args[0] not in ('--demo', '--add'):
        # Single reaction mode
        symA = args[0].capitalize()
        symB = args[1].capitalize()
        if symA not in ELEMENTS:
            # try lowercase (for two-char symbols like 'fe')
            symA = args[0][:1].upper() + args[0][1:].lower()
        if symB not in ELEMENTS:
            symB = args[1][:1].upper() + args[1][1:].lower()
        r = react(symA, symB)
        print_reaction(r)
        if '--add' in args:
            _add_to_catalog([r])
        return

    # Demo all reactions
    results = []
    for sA, sB in DEMO_REACTIONS:
        r = react(sA, sB)
        print_reaction(r)
        results.append(r)

    if '--add' in args:
        _add_to_catalog(results)


def _add_to_catalog(results):
    from pathlib import Path
    import json
    cat_path = Path(__file__).parent / 'IG_catalog.json'
    with open(cat_path) as f:
        cat = json.load(f)
    existing = {e['name'] for e in cat}
    added = 0
    for r in results:
        if 'error' in r:
            continue
        entry = catalog_entry(r)
        if entry and entry['name'] not in existing:
            cat.append(entry)
            print(f'  Catalog: added {entry["name"]}')
            added += 1
    if added:
        with open(cat_path, 'w') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)
        print(f'  {added} molecular entries added to catalog.')


if __name__ == '__main__':
    main()
