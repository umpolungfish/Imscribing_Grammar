#!/usr/bin/env python3
"""
elem2imasm.py — Exhaustive periodic table → IMASM opcode mapping.

Each element's 12-primitive IG tuple is its 12-slot IMASM word.
Rules derived by pattern-matching the 7 hand-crafted catalog entries
(H, He, Li, O, Fe, Au, U) against their Janet left-step table properties.
"""

import json
from pathlib import Path

# Shavian alphabet U+10450..U+1047F
SH = [chr(0x10450 + i) for i in range(48)]
CRIT = '⊙'  # criticality self-symbol used as a Shavian value

# All 118 elements: sym → (Z, period, janet_col, block, name)
ELEMENTS = {
    # s-block (cols 31-32)
    'H':  (1,  1, 31, 's', 'hydrogen'),      'He': (2,  1, 32, 's', 'helium'),
    'Li': (3,  2, 31, 's', 'lithium'),       'Be': (4,  2, 32, 's', 'beryllium'),
    'Na': (11, 3, 31, 's', 'sodium'),        'Mg': (12, 3, 32, 's', 'magnesium'),
    'K':  (19, 4, 31, 's', 'potassium'),     'Ca': (20, 4, 32, 's', 'calcium'),
    'Rb': (37, 5, 31, 's', 'rubidium'),      'Sr': (38, 5, 32, 's', 'strontium'),
    'Cs': (55, 6, 31, 's', 'cesium'),        'Ba': (56, 6, 32, 's', 'barium'),
    'Fr': (87, 7, 31, 's', 'francium'),      'Ra': (88, 7, 32, 's', 'radium'),
    # p-block (cols 25-30)
    'B':  (5,  2, 25, 'p', 'boron'),         'C':  (6,  2, 26, 'p', 'carbon'),
    'N':  (7,  2, 27, 'p', 'nitrogen'),      'O':  (8,  2, 28, 'p', 'oxygen'),
    'F':  (9,  2, 29, 'p', 'fluorine'),      'Ne': (10, 2, 30, 'p', 'neon'),
    'Al': (13, 3, 25, 'p', 'aluminium'),     'Si': (14, 3, 26, 'p', 'silicon'),
    'P':  (15, 3, 27, 'p', 'phosphorus'),    'S':  (16, 3, 28, 'p', 'sulfur'),
    'Cl': (17, 3, 29, 'p', 'chlorine'),      'Ar': (18, 3, 30, 'p', 'argon'),
    'Ga': (31, 4, 25, 'p', 'gallium'),       'Ge': (32, 4, 26, 'p', 'germanium'),
    'As': (33, 4, 27, 'p', 'arsenic'),       'Se': (34, 4, 28, 'p', 'selenium'),
    'Br': (35, 4, 29, 'p', 'bromine'),       'Kr': (36, 4, 30, 'p', 'krypton'),
    'In': (49, 5, 25, 'p', 'indium'),        'Sn': (50, 5, 26, 'p', 'tin'),
    'Sb': (51, 5, 27, 'p', 'antimony'),      'Te': (52, 5, 28, 'p', 'tellurium'),
    'I':  (53, 5, 29, 'p', 'iodine'),        'Xe': (54, 5, 30, 'p', 'xenon'),
    'Tl': (81, 6, 25, 'p', 'thallium'),      'Pb': (82, 6, 26, 'p', 'lead'),
    'Bi': (83, 6, 27, 'p', 'bismuth'),       'Po': (84, 6, 28, 'p', 'polonium'),
    'At': (85, 6, 29, 'p', 'astatine'),      'Rn': (86, 6, 30, 'p', 'radon'),
    'Nh': (113,7, 25, 'p', 'nihonium'),      'Fl': (114,7, 26, 'p', 'flerovium'),
    'Mc': (115,7, 27, 'p', 'moscovium'),     'Lv': (116,7, 28, 'p', 'livermorium'),
    'Ts': (117,7, 29, 'p', 'tennessine'),    'Og': (118,7, 30, 'p', 'oganesson'),
    # d-block (cols 15-24)
    'Sc': (21, 4, 15, 'd', 'scandium'),      'Ti': (22, 4, 16, 'd', 'titanium'),
    'V':  (23, 4, 17, 'd', 'vanadium'),      'Cr': (24, 4, 18, 'd', 'chromium'),
    'Mn': (25, 4, 19, 'd', 'manganese'),     'Fe': (26, 4, 20, 'd', 'iron'),
    'Co': (27, 4, 21, 'd', 'cobalt'),        'Ni': (28, 4, 22, 'd', 'nickel'),
    'Cu': (29, 4, 23, 'd', 'copper'),        'Zn': (30, 4, 24, 'd', 'zinc'),
    'Y':  (39, 5, 15, 'd', 'yttrium'),       'Zr': (40, 5, 16, 'd', 'zirconium'),
    'Nb': (41, 5, 17, 'd', 'niobium'),       'Mo': (42, 5, 18, 'd', 'molybdenum'),
    'Tc': (43, 5, 19, 'd', 'technetium'),    'Ru': (44, 5, 20, 'd', 'ruthenium'),
    'Rh': (45, 5, 21, 'd', 'rhodium'),       'Pd': (46, 5, 22, 'd', 'palladium'),
    'Ag': (47, 5, 23, 'd', 'silver'),        'Cd': (48, 5, 24, 'd', 'cadmium'),
    'Lu': (71, 6, 15, 'd', 'lutetium'),      'Hf': (72, 6, 16, 'd', 'hafnium'),
    'Ta': (73, 6, 17, 'd', 'tantalum'),      'W':  (74, 6, 18, 'd', 'tungsten'),
    'Re': (75, 6, 19, 'd', 'rhenium'),       'Os': (76, 6, 20, 'd', 'osmium'),
    'Ir': (77, 6, 21, 'd', 'iridium'),       'Pt': (78, 6, 22, 'd', 'platinum'),
    'Au': (79, 6, 23, 'd', 'gold'),          'Hg': (80, 6, 24, 'd', 'mercury'),
    'Lr': (103,7, 15, 'd', 'lawrencium'),    'Rf': (104,7, 16, 'd', 'rutherfordium'),
    'Db': (105,7, 17, 'd', 'dubnium'),       'Sg': (106,7, 18, 'd', 'seaborgium'),
    'Bh': (107,7, 19, 'd', 'bohrium'),       'Hs': (108,7, 20, 'd', 'hassium'),
    'Mt': (109,7, 21, 'd', 'meitnerium'),    'Ds': (110,7, 22, 'd', 'darmstadtium'),
    'Rg': (111,7, 23, 'd', 'roentgenium'),   'Cn': (112,7, 24, 'd', 'copernicium'),
    # f-block lanthanides (cols 1-14, period 6)
    'La': (57, 6,  1, 'f', 'lanthanum'),     'Ce': (58, 6,  2, 'f', 'cerium'),
    'Pr': (59, 6,  3, 'f', 'praseodymium'),  'Nd': (60, 6,  4, 'f', 'neodymium'),
    'Pm': (61, 6,  5, 'f', 'promethium'),    'Sm': (62, 6,  6, 'f', 'samarium'),
    'Eu': (63, 6,  7, 'f', 'europium'),      'Gd': (64, 6,  8, 'f', 'gadolinium'),
    'Tb': (65, 6,  9, 'f', 'terbium'),       'Dy': (66, 6, 10, 'f', 'dysprosium'),
    'Ho': (67, 6, 11, 'f', 'holmium'),       'Er': (68, 6, 12, 'f', 'erbium'),
    'Tm': (69, 6, 13, 'f', 'thulium'),       'Yb': (70, 6, 14, 'f', 'ytterbium'),
    # f-block actinides (cols 1-14, period 7)
    'Ac': (89, 7,  1, 'f', 'actinium'),      'Th': (90, 7,  2, 'f', 'thorium'),
    'Pa': (91, 7,  3, 'f', 'protactinium'),  'U':  (92, 7,  4, 'f', 'uranium'),
    'Np': (93, 7,  5, 'f', 'neptunium'),     'Pu': (94, 7,  6, 'f', 'plutonium'),
    'Am': (95, 7,  7, 'f', 'americium'),     'Cm': (96, 7,  8, 'f', 'curium'),
    'Bk': (97, 7,  9, 'f', 'berkelium'),     'Cf': (98, 7, 10, 'f', 'californium'),
    'Es': (99, 7, 11, 'f', 'einsteinium'),   'Fm': (100,7, 12, 'f', 'fermium'),
    'Md': (101,7, 13, 'f', 'mendelevium'),   'No': (102,7, 14, 'f', 'nobelium'),
}

NOBLE_GASES  = {'He','Ne','Ar','Kr','Xe','Rn','Og'}
PGM          = {'Ru','Rh','Pd','Os','Ir','Pt','Au'}   # FDE=T, always-Frobenius
RADIOACTIVE  = {
    'Tc','Pm','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am',
    'Cm','Bk','Cf','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt',
    'Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og',
}
TRANSACTINIDES = {'Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og'}
# Elements with ⊙=⊙ (self-referential criticality): biologically / structurally
# essential reactive elements (alkalis Li-Cs, key bio p-block, key TMs)
SELF_CRITICAL = {
    'Li','Na','K','Rb','Cs',            # alkali metals
    'Mg','Ca',                           # essential alkaline earths
    'B','C','N','O','P','S','Se','Cl','I', # essential p-block
    'Fe','Co','Ni','Cu','Zn','Mn','Mo',  # essential d-block
    'Si',                                # structural p-block
}

DESCRIPTIONS = {
    's': {
        31: 'Alkali metal with one valence electron, highly reactive',
        32: 'Alkaline earth metal with two valence electrons, divalent',
    },
    'p': {
        25: 'Group 13 element, trivalent, borderline metal/metalloid/nonmetal',
        26: 'Group 14 element, tetravalent, forms covalent network structures',
        27: 'Group 15 element, trivalent, forms pyramidal/tetrahedral compounds',
        28: 'Group 16 chalcogen, divalent, highly electronegative',
        29: 'Halogen, monovalent, highest electronegativity in period',
        30: 'Noble gas, zero valence, chemically inert',
    },
    'd': {
        'general_45': 'Transition metal period 4, variable valence, coordination chemistry',
        'general_5':  'Transition metal period 5, variable valence, 4d-block',
        'general_6':  'Transition metal period 6, relativistic effects, heavy metal',
        'general_7':  'Super-heavy transition metal, period 7, synthetic',
        23: 'Group 11 noble metal, filled d-shell, relatively inert',
        24: 'Group 12 metal, filled d10-shell, fixed divalent',
    },
    'f': {
        6: 'Lanthanide, 4f-electron, strong spin-orbit coupling',
        7: 'Actinide, 5f-electron, radioactive, nuclear instability',
    },
}

ELEM_NAMES_EN = {
    'H':'hydrogen','He':'helium','Li':'lithium','Be':'beryllium','B':'boron',
    'C':'carbon','N':'nitrogen','O':'oxygen','F':'fluorine','Ne':'neon',
    'Na':'sodium','Mg':'magnesium','Al':'aluminium','Si':'silicon','P':'phosphorus',
    'S':'sulfur','Cl':'chlorine','Ar':'argon','K':'potassium','Ca':'calcium',
    'Sc':'scandium','Ti':'titanium','V':'vanadium','Cr':'chromium','Mn':'manganese',
    'Fe':'iron','Co':'cobalt','Ni':'nickel','Cu':'copper','Zn':'zinc',
    'Ga':'gallium','Ge':'germanium','As':'arsenic','Se':'selenium','Br':'bromine',
    'Kr':'krypton','Rb':'rubidium','Sr':'strontium','Y':'yttrium','Zr':'zirconium',
    'Nb':'niobium','Mo':'molybdenum','Tc':'technetium','Ru':'ruthenium','Rh':'rhodium',
    'Pd':'palladium','Ag':'silver','Cd':'cadmium','In':'indium','Sn':'tin',
    'Sb':'antimony','Te':'tellurium','I':'iodine','Xe':'xenon','Cs':'cesium',
    'Ba':'barium','La':'lanthanum','Ce':'cerium','Pr':'praseodymium','Nd':'neodymium',
    'Pm':'promethium','Sm':'samarium','Eu':'europium','Gd':'gadolinium','Tb':'terbium',
    'Dy':'dysprosium','Ho':'holmium','Er':'erbium','Tm':'thulium','Yb':'ytterbium',
    'Lu':'lutetium','Hf':'hafnium','Ta':'tantalum','W':'tungsten','Re':'rhenium',
    'Os':'osmium','Ir':'iridium','Pt':'platinum','Au':'gold','Hg':'mercury',
    'Tl':'thallium','Pb':'lead','Bi':'bismuth','Po':'polonium','At':'astatine',
    'Rn':'radon','Fr':'francium','Ra':'radium','Ac':'actinium','Th':'thorium',
    'Pa':'protactinium','U':'uranium','Np':'neptunium','Pu':'plutonium','Am':'americium',
    'Cm':'curium','Bk':'berkelium','Cf':'californium','Es':'einsteinium','Fm':'fermium',
    'Md':'mendelevium','No':'nobelium','Lr':'lawrencium','Rf':'rutherfordium',
    'Db':'dubnium','Sg':'seaborgium','Bh':'bohrium','Hs':'hassium','Mt':'meitnerium',
    'Ds':'darmstadtium','Rg':'roentgenium','Cn':'copernicium','Nh':'nihonium',
    'Fl':'flerovium','Mc':'moscovium','Lv':'livermorium','Ts':'tennessine',
    'Og':'oganesson',
}


def derive_tuple(sym):
    """Return 12-primitive Shavian tuple for an element symbol."""
    Z, period, col, block, _ = ELEMENTS[sym]

    # ─── > (Recognition) idx ─────────────────────────────────────
    # Noble gases, H, and PGM catalysts (always return to ground state): minimal
    R = 1 if (sym in NOBLE_GASES or sym == 'H' or sym in PGM) else 45

    # ─── ⊥ (Chirality) idx ───────────────────────────────────────
    # f-block (strong SOC, H2): 27; d-block periods 4-5 (H1 coord): 2
    # d-block period 6 relativistic collapse → 3 (like s-block); else 3
    if block == 'f':
        H = 27
    elif block == 'd' and period in (4, 5):
        H = 2
    else:
        H = 3

    # ─── Ω (Winding) idx ─────────────────────────────────────────
    # f-block strong winding: 29; d-block 4-5 integer: 36
    # everything else (s, p, d period 6 relativistic): 39
    if block == 'f':
        Om = 29
    elif block == 'd' and period in (4, 5):
        Om = 36
    else:
        Om = 39

    # ─── ⊢ (Dimensionality) idx ──────────────────────────────────
    # Janet left-step depth: s-block rightmost (11), f-block leftmost (44)
    if block == 's':
        D = 11
    elif block == 'f':
        D = 44
    else:
        D = 24   # p and d block

    # ─── Σ (Stoichiometry) idx ───────────────────────────────────
    # By Janet column (= group position):
    # Monovalent (col 31, 29, 30, 26, col-23 noble d10s1): 9
    # Divalent (col 32 non-noble, col 28, col 24 zinc-group, col 27): 5
    # Trivalent (col 25): 11
    # Variable (d cols 15-22, f-block): 35
    if block == 'f' or (block == 'd' and col in range(15, 23)):
        Sig = 35   # variable valence
    elif col in (31, 30, 26, 29) or (col == 23 and block == 'd') or sym == 'H':
        Sig = 9    # monovalent / fixed tetravalent / inert
    elif col in (32, 28, 24):
        if col == 32 and sym in NOBLE_GASES:
            Sig = 9    # He special case: noble at col 32
        else:
            Sig = 5    # divalent (alk earths, chalcogens, zinc group)
    elif col == 27:
        Sig = 11   # trivalent pnictogen (N, P, As, Sb, Bi): distinct from chalcogen
    elif col == 25:
        Sig = 11   # trivalent boron-group
    else:
        Sig = 9    # fallback

    # ─── < (Parity) idx ──────────────────────────────────────────
    # Closed shell / noble-like: 31; open diradical / paramagnetic: 28
    # Odd single unpaired: 7
    if sym in NOBLE_GASES:
        Ph = 31   # closed shell noble
    elif col == 32:
        Ph = 31   # alkaline earths s2 closed
    elif col == 24:
        Ph = 31   # zinc group d10s2 closed
    elif col == 23 and period == 6:
        Ph = 31   # Au/Rg relativistic d10 closed
    elif block == 'f' and period == 7:
        Ph = 7    # actinides: complex odd-unpaired
    elif block in ('d', 'f') or col in (26, 27, 28):
        Ph = 28   # open d/f shell or O-like diradical
    else:
        Ph = 7    # odd-valence open shell (alkalis, H, halogens, group 13)

    # ─── ⊤ (Kinetics) idx ────────────────────────────────────────
    # PGM + Fe-like TM catalysts: 20; radioactive/nuclear: 23; rest: 8
    CATALYTIC = {'Fe','Co','Ru','Rh','Pd','Os','Ir','Pt','Mn','Ni'}
    if sym in (RADIOACTIVE - TRANSACTINIDES) or sym in TRANSACTINIDES:
        C = 23
    elif sym in CATALYTIC:
        C = 20
    else:
        C = 8

    # ─── ⋈ (Fidelity) idx ────────────────────────────────────────
    # Universally 0 across all 7 existing entries
    f = 0

    # ─── ∋ (Coupling) idx ────────────────────────────────────────
    # d-block metals + noble gases + H: 13 (coordinate/metallic/none)
    # s-block, p-block reactive, f-block: 16 (ionic/covalent)
    if sym in NOBLE_GASES or sym == 'H' or block == 'd':
        g = 13
    else:
        g = 16

    # ─── ∈ (Granularity) idx ─────────────────────────────────────
    # s-block (all periods): 10; d-block period 6 relativistic: 10
    # p/d periods 2-6 and f-block lanthanides: 4
    # f-block actinides + p/d period 7: 34
    if block == 's':
        G = 10
    elif block == 'd' and period == 6:
        G = 10   # relativistic noble metals — simple granularity
    elif period == 7:
        G = 34   # super-heavy / actinide era
    else:
        G = 4    # active chemistry zone (periods 2-6, d4-5, f lans)

    # ─── ⊣ (Topology) idx ────────────────────────────────────────
    # s-block spherical: 38; d-block period 6 relativistic collapse: 38
    # d-block periods 4-5 (and 7): 32; f-block: 21
    # p-block noble (col 30): 38; p-block active: 17
    if block == 's':
        T = 38
    elif block == 'd' and period == 6:
        T = 38   # relativistic d→s collapse
    elif block == 'd':
        T = 32   # d-orbital cloverleaf topology
    elif block == 'f':
        T = 21   # f-orbital complex topology
    elif col == 30:
        T = 38   # noble gas: spherical
    else:
        T = 17   # p-block active: dumbbell/bent topology

    # ─── ⊙ (Criticality) ─────────────────────────────────────────
    # Inert stable (noble + H + PGM): 18 (𐑢); bio-critical reactive: ⊙
    # Radioactive simple: 19 (𐑣); transactinides: 23 (𐑧)
    if sym in TRANSACTINIDES:
        crit = SH[23]  # 𐑧 — synthetic, maximally indeterminate
    elif sym in (RADIOACTIVE - TRANSACTINIDES):
        crit = SH[19]  # 𐑣
    elif sym in NOBLE_GASES or sym == 'H' or sym in PGM:
        crit = SH[18]  # 𐑢 — subcritical stable
    elif sym in SELF_CRITICAL:
        crit = CRIT    # ⊙ self-referential
    else:
        crit = CRIT    # default: reactive elements are critical

    return {
        '>': SH[R],
        '⊥': SH[H],
        '◻': SH[Om],
        '⊢': SH[D],
        '⊞': SH[Sig],
        '<': SH[Ph],
        '⊤': SH[C],
        '⋈': SH[f],
        '∋': SH[g],
        '∈': SH[G],
        '⊣': SH[T],
        '⊙': crit,
    }


def make_description(sym):
    Z, period, col, block, _ = ELEMENTS[sym]
    if sym in ELEM_NAMES_EN:
        name = ELEM_NAMES_EN[sym].capitalize()
    else:
        name = sym
    if block == 's':
        base = DESCRIPTIONS['s'].get(col, f's-block element, period {period}')
    elif block == 'p':
        base = DESCRIPTIONS['p'].get(col, f'p-block element, period {period}')
    elif block == 'd':
        if col == 23:
            base = DESCRIPTIONS['d'][23]
        elif col == 24:
            base = DESCRIPTIONS['d'][24]
        elif period == 4:
            base = DESCRIPTIONS['d']['general_45']
        elif period == 5:
            base = DESCRIPTIONS['d']['general_5']
        elif period == 6:
            base = DESCRIPTIONS['d']['general_6']
        else:
            base = DESCRIPTIONS['d']['general_7']
    else:  # f
        base = DESCRIPTIONS['f'][period]
    suffix = ', radioactive' if sym in RADIOACTIVE else ''
    return f'{name} (Z={Z}, {block}-block, period {period}): {base}{suffix}'


def build_catalog_entry(sym):
    Z, period, col, block, name = ELEMENTS[sym]
    t = derive_tuple(sym)
    entry = {'name': name, 'description': make_description(sym)}
    entry.update(t)
    return entry


def imasm_word(sym):
    """Return the 12-token IMASM word string for an element."""
    t = derive_tuple(sym)
    prims = ['>','⊥','◻','⊢','⊞','<','⊤','⋈','∋','∈','⊣','⊙']
    return ''.join(t[p] for p in prims)


def validate_against_existing(cat):
    """Check how our derivations compare to the 7 hand-crafted entries."""
    prims = ['>','⊥','◻','⊢','⊞','<','⊤','⋈','∋','∈','⊣','⊙']
    existing = {e['name']: e for e in cat if e['name'] in set(ELEM_NAMES_EN.values())}
    sym_map = {v: k for k, v in ELEM_NAMES_EN.items()}
    info_line('\nValidation against 7 existing hand-crafted entries:')
    info_line(f'{"elem":12s} {"prim":5s} derived  existing  match')
    for name, entry in existing.items():
        sym = sym_map.get(name)
        if sym not in ELEMENTS:
            continue
        derived = derive_tuple(sym)
        mismatches = []
        for p in prims:
            d = derived.get(p, '?')
            e = entry.get(p, '?')
            if d != e:
                mismatches.append(f'{p}:{d}≠{e}')
        status = 'OK' if not mismatches else f'DIFF: {" ".join(mismatches)}'
        info_line(f'  {name:12s} {status}')


from shared.rich_output import *

def main():
    import sys
    cat_path = Path(__file__).parent / 'IG_catalog.json'
    with open(cat_path) as f:
        cat = json.load(f)

    existing_names = {e['name'] for e in cat}

    # Validation
    validate_against_existing(cat)

    # Generate entries
    new_entries = []
    updated = 0
    added = 0
    for sym in sorted(ELEMENTS, key=lambda s: ELEMENTS[s][0]):
        Z, period, col, block, name = ELEMENTS[sym]
        entry = build_catalog_entry(sym)
        if name not in existing_names:
            new_entries.append(entry)
            added += 1

    info_line(f'\nNew entries to add: {added}')
    info_line(f'Already in catalog: {len(ELEMENTS) - added}')

    if '--add' in sys.argv:
        # Also update existing element entries that have wrong values
        all_elem_names = {ELEMENTS[s][4] for s in ELEMENTS}
        for i, entry in enumerate(cat):
            if entry['name'] in all_elem_names:
                sym = next(s for s, v in ELEMENTS.items() if v[4] == entry['name'])
                correct = build_catalog_entry(sym)
                if any(entry.get(p) != correct[p] for p in ['>','⊥','◻','⊢','⊞','<','⊤','⋈','∋','∈','⊣','⊙']):
                    cat[i] = correct
                    info_line(f'  Updated stale entry: {entry["name"]}')
                    updated += 1
        cat.extend(new_entries)
        with open(cat_path, 'w') as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)
        info_line(f'Added {added} new + updated {updated} stale element entries in catalog.')

    if '--table' in sys.argv or '--add' not in sys.argv:
        prims = ['>','⊥','◻','⊢','⊞','<','⊤','⋈','∋','∈','⊣','⊙']
        info_line(f'\n{"Sym":4s} {"Z":3s} P B {"IMASM word (12 tokens)":50s}  {"> ⊥ Ω ⊢ Σ < ⊤ ⋈ ∋ ∈ ⊣ ⊙"}')
        info_line('-'*110)
        for sym in sorted(ELEMENTS, key=lambda s: ELEMENTS[s][0]):
            Z, period, col, block, name = ELEMENTS[sym]
            t = derive_tuple(sym)
            word = ''.join(t[p] for p in prims)
            vals = ' '.join(t[p] for p in prims)
            info_line(f'{sym:4s} {Z:3d} {period} {block} {word}  {vals}')

    if '--imasm' in sys.argv:
        # Output IMASM opcode index table (ordinal values 0-47 or S for ⊙)
        prims = ['>','⊥','◻','⊢','⊞','<','⊤','⋈','∋','∈','⊣','⊙']
        info_line(f'\n{"Sym":4s} {"Z":3s} | >  ⊥  Ω  ⊢  Σ  <  ⊤  ⋈  ∋  ∈  ⊣  ⊙')
        info_line('-'*60)
        for sym in sorted(ELEMENTS, key=lambda s: ELEMENTS[s][0]):
            Z = ELEMENTS[sym][0]
            t = derive_tuple(sym)
            def idx(c):
                if c == CRIT: return ' S'
                return f'{ord(c)-0x10450:2d}'
            ords = '  '.join(idx(t[p]) for p in prims)
            info_line(f'{sym:4s} {Z:3d} | {ords}')


if __name__ == '__main__':
    main()
