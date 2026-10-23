#!/usr/bin/env python3
"""ch3mpiler - IG-grounded retrosynthetic compiler using grammar-derived rules
of bond formation — NO named reactions.

Bond formation is modeled as: product_type = join(tensor(FG1, FG2), bond)
  - tensor: max on union primitives (D,T,R,K,G,Gm,Ph,H,S,W), min on P,F
  - join with bond: max on all primitives (bond provides a floor)
Disconnections are ranked by distance between predicted product type and
the molecule's catalog-verified type (or FG-composed type as fallback).

Author: Lando \u2297 \u2299perator
"""
import argparse, json, math, os, re, sys, urllib.request, urllib.error, time
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).parent.absolute()
CATALOG_PATH = BASE / "IG_catalog.json"
CAS_CACHE_PATH = BASE / "CAS_cache.json"
sys.path.insert(0, str(BASE))

from space_search.primitives import ORDINALS, WEIGHTS, resolve_ordinal_key

PNAMES = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
PFIELDS = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
FIELD_TO_ORD = {
    "D":"\u22a2", "T":"\u22a3", "R":"\u227b", "P":"\u227a", "F":"\u22c8",
    "K":"\u22a4", "G":"\u2208", "Gm":"\u220b", "Ph":"\u2299", "H":"\u22a5",
    "S":"\u229e", "W":"\u22a1"
}

def g2v(p, r):
    """Primitive glyph \u2192 ordinal value."""
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

def fmt_tup(t):
    gs = []
    for p in PNAMES:
        v = t.get(p, "?")
        gs.append(v)
    return "<" + "; ".join(gs) + ">"

def tup_to_ords(t):
    """Convert glyph tuple dict to ordinal dict."""
    return {p: glyph_ord(p, t.get(p, "?")) for p in PNAMES}

def tup_dist(t1, t2):
    """Weighted Euclidean distance between two type dictionaries."""
    sq = 0.0; cf = []
    for p in PNAMES:
        v1 = t1.get(p, ""); v2 = t2.get(p, "")
        o1 = glyph_ord(p, v1); o2 = glyph_ord(p, v2)
        w = WEIGHTS.get(FIELD_TO_ORD.get(p, p), 1.0)
        d = (o1 - o2) * w; sq += d * d
        if o1 != o2:
            cf.append({"p": p, "a": v1, "b": v2, "d": o1 - o2})
    return math.sqrt(sq), cf

def tensor_type(t1, t2):
    """Grammar tensor: max on union primitives, min on P and F."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        if p in ("P", "F"):
            r[p] = ord_to_glyph(p, min(o1, o2))
        else:
            r[p] = ord_to_glyph(p, max(o1, o2))
    return r

def join_type(t1, t2):
    """Grammar join: max on all primitives."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        r[p] = ord_to_glyph(p, max(o1, o2))
    return r

def bond_product_type(fg1_type, fg2_type, bond_type):
    """Product type when FG1 and FG2 are connected by bond B.
    Formula: product = join(tensor(FG1, FG2), bond)
    """
    t = tensor_type(fg1_type, fg2_type)
    return join_type(t, bond_type)
# ====================================================================
# GLYPH REFERENCE MAP
# ====================================================================
GLYPH_MAP = {
    "\U0001045B": ("D",1), "\U00010468": ("D",2),
    "\U00010461": ("T",1), "\U00010470": ("T",2), "\U00010465": ("T",3), "\U00010478": ("T",5),
    "\U00010469": ("R",1), "\U00010451": ("R",2), "\U0001047D": ("R",3), "\U0001047E": ("R",4),
    "\U00010457": ("P",1), "\U0001047F": ("P",2), "\U0001046C": ("P",3), "\U0001046F": ("P",4), "\U00010479": ("P",5),
    "\U00010450": ("F",3), "\U0001045E": ("F",2), "\U00010471": ("F",1),
    "\U00010458": ("K",1), "\U00010464": ("K",2), "\U00010467": ("K",3), "\U0001047A": ("K",4), "\U0001046A": ("K",5),
    "\U0001045A": ("G",1), "\U00010454": ("G",2), "\U00010472": ("G",3),
    "\U0001045D": ("Ga",1), "\U0001045C": ("Ga",2), "\U00010460": ("Ga",3), "\U00010475": ("Ga",4),
    "\U00010462": ("Ph",1), "\u2299": ("Ph",2), "\U0001046E": ("Ph",3), "\U0001047B": ("Ph",4), "\U00010463": ("Ph",5),
    "\U00010452": ("H",2), "\U00010456": ("H",3), "\U00010453": ("H",1), "\U0001046B": ("H",4),
    "\U00010459": ("S",1), "\U00010455": ("S",2), "\U00010473": ("S",3),
    "\U00010477": ("W",1), "\U00010474": ("W",2), "\U0001046D": ("W",3), "\U0001045F": ("W",4),
}

# ====================================================================
# GRAMMAR-DERIVED BOND TYPES
# Each bond type encodes a DISTINCTIVE signature.
# The bond provides a FLOOR for the product type via join.
# Higher primitive values = more structural character added by the bond.
# ====================================================================

BOND_TYPES = {
    # σ single bond: simple localized connection between sp³ centers
    # Low values — doesn't add structure beyond connectivity
    "sigma_single": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
        "desc":"σ single bond (localized, sp³-sp³)"
    },
    # π bond: p-orbital overlap, adds 2D character and quantum coherence
    "pi_bond": {
        "D":"\U00010468","T":"\U00010470","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010471","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"π bond (p-orbital overlap, quantum coherent)"
    },
    # C=C double bond: σ+π, adds planarity and restricted rotation
    "double_bond": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047E",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C=C double bond (planar, σ+π)"
    },
    # C≡C triple bond: σ+2π, linear geometry
    "triple_bond": {
        "D":"\U00010468","T":"\U00010470","R":"\U0001047E",
        "P":"\U0001046F","F":"\U00010471","K":"\U00010458",
        "G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C≡C triple bond (linear, σ+2π)"
    },
    # Carbonyl C=O: polarized, reaction hub, critical
    "carbonyl": {
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C=O carbonyl (polarized, reaction hub)"
    },
    # C-O single bond: polar, lower symmetry
    "co_sigma": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"C-O σ bond (polar, ether/alcohol)"
    },
    # C-N single bond: polar, nitrogen lone pair
    "cn_sigma": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010458",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
        "desc":"C-N σ bond (polar, amine)"
    },
    # Amide: conjugated, planar, high chirality
    "amide_link": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047E",
        "P":"\U0001046C","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U00010474",
        "desc":"Amide C(=O)-N (conjugated, planar)"
    },
    # Ester: polarized, resonance-stabilized
    "ester_link": {
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010474",
        "desc":"Ester C(=O)-O (resonance-stabilized)"
    },
    # Aromatic: delocalized, high symmetry, topological
    "aromatic": {
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E",
        "P":"\U00010479","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
        "desc":"Aromatic delocalized (cyclic π, Z₃)"
    },
    # Hydrogen bond: intermolecular, weak
    "hydrogen_bond": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010458",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"H-bond (intermolecular, electrostatic)"
    },
    # Ether C-O-C: bent, polar
    "ether_link": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"C-O-C ether (bent, polar)"
    },
}
# ====================================================================
# FUNCTIONAL GROUP TYPES (IG structural encodings)
# ====================================================================
FG = {
    "alcohol": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "carbonyl": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "aldehyde": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "ketone": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "carboxylic_acid": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010452","S":"\U00010473","W":"\U00010477"},
    "ester": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010452","S":"\U00010473","W":"\U00010477"},
    "amide": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046C","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U00010474"},
        "alkane": {"D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑒","S":"𐑳","W":"𐑷"},
    "amine": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "aniline": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "ether": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010453","S":"\U00010459","W":"\U00010477"},
    "nitrile": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "halide": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010453","S":"\U00010459","W":"\U00010477"},
    "alkene": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "alkyne": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "aromatic_ring": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "phenol": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "epoxide": {"D":"\U00010468","T":"\U00010470","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "thiol": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U0001045E","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
}

FG_TOKENS = {
    "alcohol":"alcohol","ol":"alcohol","hydroxy":"alcohol","hydroxyl":"alcohol",
    "carbonyl":"carbonyl","oxo":"carbonyl",
    "aldehyde":"aldehyde","al":"aldehyde",
    "ketone":"ketone","one":"ketone","keto":"ketone",
    "acid":"carboxylic_acid","carboxy":"carboxylic_acid","oic":"carboxylic_acid","oate":"carboxylic_acid",
    "ester":"ester",
    "amide":"amide","amido":"amide",
    "amine":"amine","amino":"amine","aza":"amine",
    "ether":"ether","oxy":"ether","methoxy":"ether","ethoxy":"ether",
    "nitrile":"nitrile","cyano":"nitrile",
    "halide":"halide","chloro":"halide","bromo":"halide","fluoro":"halide","iodo":"halide",
    "alkene":"alkene","ene":"alkene","vinyl":"alkene",
    "alkane":"alkane","ane":"alkane",
    "alkyne":"alkyne","yne":"alkyne","acetylene":"alkyne",
    "benz":"aromatic_ring","phenyl":"aromatic_ring","aryl":"aromatic_ring",
    "phenol":"phenol","hydroxybenz":"phenol",
    "diazonium":"diazonium","diazo":"diazonium",
    "nitro":"nitro","nitroso":"nitro",
    "epoxide":"epoxide","oxirane":"epoxide",
    "thio":"thiol","thiol":"thiol","sulfanyl":"thiol",
    "cyclo":"cyclic","cyclohex":"cyclic","cyclopent":"cyclic",
}

# ====================================================================
# GRAMMAR-DERIVED DISCONNECTION ENGINE
# Product type = join(tensor(FG1, FG2), bond_type)
# Disconnection delta = distance(molecule_type, product_type)
# ====================================================================

def compose_molecule_type(fg_names):
    """Compose molecule type from its functional groups via tensor product."""
    result = None
    for fg in sorted(fg_names):
        fg_t = FG.get(fg, {})
        if not fg_t:
            continue
        if result is None:
            result = dict(fg_t)
        else:
            result = tensor_type(result, fg_t)
    return result if result else {}

def get_molecule_type(name, catalog):
    """Get molecule type: from catalog if available, else compose from FGs."""
    for e in catalog:
        if e.get("name", "").lower() == name.lower():
            t = {}
            for pn, pf in zip(PNAMES, PFIELDS):
                v = e.get(pf, "")
                if v:
                    t[pn] = v
            if len(t) == 12:
                return t, "catalog"
    # Fallback: use find_fgs which checks MOLECULE_FG_DB first, then FG_TOKENS
    fgs_found = find_fgs(name)
    if fgs_found:
        return compose_molecule_type(fgs_found), "composed"
    return {}, "none"

# Name-to-FG lookup from molecule database (built from local CAS DB + catalog)
# Name-to-FG lookup — direct mapping from molecule names to functional groups
MOLECULE_FG_DB = {
    "aspirin": ["ester", "carboxylic_acid", "aromatic_ring"],
    "paracetamol": ["amide", "phenol", "aromatic_ring"],
    "acetaminophen": ["amide", "phenol", "aromatic_ring"],
    "thc": ["phenol", "alkene", "ether", "cyclic", "aromatic_ring"],
    "cannabidiol": ["phenol", "alkene", "cyclic", "aromatic_ring"],
    "caffeine": ["amine", "amide", "alkene", "cyclic"],
    "ibuprofen": ["carboxylic_acid", "aromatic_ring"],
    "naproxen": ["carboxylic_acid", "ether", "aromatic_ring"],
    "morphine": ["amine", "alcohol", "ether", "aromatic_ring"],
    "codeine": ["amine", "alcohol", "ether", "aromatic_ring"],
    "nicotine": ["amine", "cyclic", "aromatic_ring"],
    "glucose": ["alcohol", "ether", "aldehyde"],
    "fructose": ["alcohol", "ether", "ketone"],
    "sucrose": ["alcohol", "ether"],
    "benzaldehyde": ["aldehyde", "aromatic_ring"],
    "aniline": ["aniline", "aromatic_ring"],
    "toluene": ["aromatic_ring"],
    "nitrobenzene": ["nitro", "aromatic_ring"],
    "chlorobenzene": ["halide", "aromatic_ring"],
    "acetophenone": ["ketone", "aromatic_ring"],
    "benzonitrile": ["nitrile", "aromatic_ring"],
    "anisole": ["ether", "aromatic_ring"],
    "styrene": ["alkene", "aromatic_ring"],
    "acrylonitrile": ["alkene", "nitrile"],
    "ethylene": ["alkene"],
    "acetylene": ["alkyne"],
    "cyclohexane": ["alkane"],
    "phenol": ["phenol", "aromatic_ring"],
    "benzene": ["aromatic_ring"],
    "ethylbenzene": ["aromatic_ring"],
    "triethylamine": ["amine"],
    "propionic acid": ["carboxylic_acid"],
    "acetic acid": ["carboxylic_acid"],
    "salicylic acid": ["carboxylic_acid", "phenol", "aromatic_ring"],
    "picric acid": ["phenol", "nitro", "aromatic_ring"],
    "2-acetoxybenzoic acid": ["ester", "carboxylic_acid", "aromatic_ring"],
    "11-hydroxy-δ9-tetrahydrocannabinol": ["phenol", "alcohol", "alkene", "ether", "cyclic", "aromatic_ring"],
    "4-methyl-5-phenyl-4,5-dihydro-1,3-oxazol-2-amine": ["amine", "aromatic_ring", "ether", "cyclic"],
        "cubane": ["cyclic", "alkane"],
    "pentacyclo": ["cyclic", "alkane"],
    "p-phenylenediamine": ["amine", "aromatic_ring"],
    "3,4-dichloroaniline": ["halide", "amine", "aromatic_ring"],
    "purine": ["aromatic_ring", "amine", "cyclic"],
    "adenine": ["amine", "aromatic_ring", "cyclic"],
    "guanine": ["amide", "amine", "aromatic_ring", "cyclic"],
    "theophylline": ["amide", "amine", "alkene", "cyclic"],
    "theobromine": ["amide", "amine", "alkene", "cyclic"],
    "isoprene": ["alkene"],
    "limonene": ["alkene", "cyclic"],
    "pinene": ["alkene", "cyclic"],
    "penicillin": ["amide", "carboxylic_acid", "cyclic", "thiol"],
    "morphine": ["phenol", "alcohol", "ether", "amine", "alkene", "cyclic", "aromatic_ring"],
    "codeine": ["phenol", "ether", "amine", "alkene", "cyclic", "aromatic_ring"],
    "diazepam": ["amide", "amine", "aromatic_ring", "halide", "cyclic"],
    "warfarin": ["alcohol", "ketone", "ester", "aromatic_ring"],
    "cholesterol": ["alcohol", "alkene", "cyclic"],
    "testosterone": ["alcohol", "ketone", "alkene", "cyclic"],
    "estradiol": ["phenol", "alcohol", "cyclic", "aromatic_ring"],
    "cortisol": ["alcohol", "ketone", "alkene", "cyclic"],
}

# SMARTS for every functional group the FG table types. A molecule given as SMILES
# is read here rather than by name, so the same nineteen groups are recognised
# whichever way the target arrives.
FG_SMARTS = {
    "carboxylic_acid": "[CX3](=O)[OX2H1]",
    "ester":           "[CX3](=O)[OX2H0][#6]",
    "amide":           "[NX3][CX3](=[OX1])",
    "aldehyde":        "[CX3H1](=O)[#6]",
    "ketone":          "[#6][CX3](=O)[#6]",
    "alcohol":         "[#6;!$(C=O)][OX2H]",
    "phenol":          "[c][OX2H]",
    "ether":           "[OD2]([#6])[#6]",
    "epoxide":         "[OX2r3]1[#6r3][#6r3]1",
    "amine":           "[NX3;H2,H1,H0;!$(N[C,S]=[O,S,N]);!$(N=*)]",
    "aniline":         "[c][NX3;H2,H1,H0;!$(N[C,S]=[O,S,N])]",
    "nitrile":         "[NX1]#[CX2]",
    "thiol":           "[#6][SX2H]",
    "halide":          "[#6][F,Cl,Br,I]",
    "aromatic_ring":   "c1ccccc1",
    "alkene":          "[CX3;!$(C=O)]=[CX3]",
    "alkyne":          "[CX2]#[CX2]",
    "carbonyl":        "[CX3]=[OX1]",
    "alkane":          "[CX4;!$(C~[!#6;!#1])]",
}

def _looks_like_smiles(text):
    """A target string is read as SMILES when RDKit parses it and the string is
    not a molecule name already known to the database."""
    if text.lower().replace("_", " ").strip() in MOLECULE_FG_DB:
        return False
    try:
        from rdkit import Chem
        from rdkit import RDLogger
        RDLogger.DisableLog("rdApp.*")
    except Exception:
        return False
    if not any(ch in text for ch in "()[]=#12345") and text.isalpha() and len(text) > 3:
        return False
    return Chem.MolFromSmiles(text) is not None

def find_fgs_smiles(smiles):
    """Functional groups of a SMILES string, by substructure match.

    A larger group contains smaller ones, and counting both counts the same
    atoms twice. Containment is decided on the atoms actually matched, so a
    molecule carrying a phenol in one ring and an alcohol elsewhere keeps both,
    while the hydroxyl of a carboxylic acid is not reported a second time.
    """
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    matches = {}
    for name, sma in FG_SMARTS.items():
        patt = Chem.MolFromSmarts(sma)
        if patt is None:
            continue
        hits = [frozenset(h) for h in mol.GetSubstructMatches(patt)]
        if hits:
            matches[name] = hits

    implied = {
        "carboxylic_acid": {"carbonyl", "alcohol", "ether", "ketone", "aldehyde"},
        "ester":           {"carbonyl", "ether", "alcohol", "ketone"},
        "amide":           {"carbonyl", "amine", "aniline", "ketone"},
        "aldehyde":        {"carbonyl"},
        "ketone":          {"carbonyl"},
        "phenol":          {"alcohol"},
        "aniline":         {"amine"},
        "epoxide":         {"ether"},
        "aromatic_ring":   {"alkene"},
    }
    for big, smalls in implied.items():
        if big not in matches:
            continue
        big_atoms = set().union(*matches[big])
        for small in smalls:
            if small not in matches:
                continue
            kept = [h for h in matches[small] if not h <= big_atoms]
            if kept:
                matches[small] = kept
            else:
                del matches[small]

    if set(matches) - {"alkane"}:
        matches.pop("alkane", None)
    return sorted(matches)

def find_fgs(name):
    """Extract functional groups from molecule name.
    
    Priority order:
    1. Molecule name lookup (MOLECULE_FG_DB) — exact
    2. Molecule name substring (MOLECULE_FG_DB) — best match
    3. Word-boundary token matching (FG_TOKENS) — avoids false positives
       like 'ene' matching 'caffeine' or 'one' matching 'ketone'
    """
    import re as _re
    name_lower = name.lower().replace("_", " ").replace("-", " ").strip()

    if _looks_like_smiles(name):
        smiles_fgs = find_fgs_smiles(name)
        if smiles_fgs:
            return smiles_fgs

    if name_lower in MOLECULE_FG_DB:
        return sorted(g for g in MOLECULE_FG_DB[name_lower] if g in FG)

    for db_name in sorted(MOLECULE_FG_DB.keys(), key=len, reverse=True):
        if db_name in name_lower:
            return sorted(g for g in MOLECULE_FG_DB[db_name] if g in FG)
    
    words = _re.split(r'[\s\d,;()\[\]{}]+', name_lower)
    found = set()
    
    for token in sorted(FG_TOKENS.keys(), key=len, reverse=True):
        for word in words:
            if word == token or word.endswith(token):
                if len(token) >= 4 or word == token or (
                    len(word) > len(token) and word[-len(token):] == token
                    and word[-len(token)-1] not in 'aeiou'
                ):
                    found.add(FG_TOKENS[token])
                    break
            elif word.startswith(token) and len(token) >= 4:
                found.add(FG_TOKENS[token])
                break
    
    if not found:
        for token in sorted(FG_TOKENS.keys(), key=len, reverse=True):
            if len(token) >= 4 and token in name_lower:
                found.add(FG_TOKENS[token])
    
    return sorted(found) if found else []
def get_fg_type(fg_name):
    return FG.get(fg_name, {})

def meet_type(t1, t2):
    """Meet: min on all primitives — shared floor."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        r[p] = ord_to_glyph(p, min(o1, o2))
    return r

def is_bond_compatible(bond, fg1, fg2):
    """Check if bond type is structurally compatible with FGs.
    For union primitives: bond value <= max(FG1, FG2)
    For intersection primitives (P, F): bond value <= min(FG1, FG2)
    """
    reasons = []
    for p in PNAMES:
        bo = glyph_ord(p, bond.get(p,"?"))
        if p in ("P", "F"):
            fo = min(glyph_ord(p, fg1.get(p,"?")), glyph_ord(p, fg2.get(p,"?")))
        else:
            fo = max(glyph_ord(p, fg1.get(p,"?")), glyph_ord(p, fg2.get(p,"?")))
        if bo > fo:
            reasons.append(f"{p}: bond={bo} > FG={fo}")
    return len(reasons) == 0, reasons

def evaluate_disconnection(fg1_name, fg2_name, bond_name, molecule_type):
    """Evaluate a disconnection using grammar-derived rules.
    
    Delta = distance(bond_type, meet(FG1, FG2)) — lower = bond fits FG interface better.
    Compatibility = whether bond primitives are within FG capacity.
    """
    fg1 = FG.get(fg1_name, {}); fg2 = FG.get(fg2_name, {})
    bond = BOND_TYPES.get(bond_name, {})
    if not fg1 or not fg2 or not bond:
        return None
    
    interface = meet_type(fg1, fg2)
    delta, conflicts = tup_dist(bond, interface)
    compatible, reasons = is_bond_compatible(bond, fg1, fg2)
    
    product = bond_product_type(fg1, fg2, bond)
    
    return {
        "fg1": fg1_name, "fg2": fg2_name,
        "bond": bond_name,
        "bond_desc": bond.get("desc", bond_name),
        "delta": round(delta, 3),
        "compatible": compatible,
        "incompatible_reasons": reasons,
        "conflicts": len(conflicts),
        "product_type": fmt_tup(product),
    }

def find_disconnections(fg_names, molecule_type, max_results=10):
    """Find all viable disconnections via grammar-derived rules.
    
    Ranking: bond specificity (amide>ester>carbonyl>...>sigma>H-bond),
    then structural delta. Incompatible bonds are filtered out.
    """
    BOND_SPECIFICITY = {
        "amide_link": 10, "ester_link": 9, "carbonyl": 8,
        "aromatic": 7, "double_bond": 6, "triple_bond": 5,
        "co_sigma": 3, "cn_sigma": 3, "ether_link": 2,
        "sigma_single": 1, "pi_bond": 1, "hydrogen_bond": 0,
    }
    
    results = []
    for i, fg1 in enumerate(fg_names):
        for fg2 in fg_names[i:]:
            for bname in BOND_TYPES:
                ev = evaluate_disconnection(fg1, fg2, bname, molecule_type)
                if ev and ev["compatible"]:
                    ev["specificity"] = BOND_SPECIFICITY.get(bname, 0)
                    results.append(ev)
    results.sort(key=lambda x: (-x.get("specificity", 0), x["delta"]))
    return results[:max_results]

# CAS RESOLVER
# ====================================================================
class CASResolver:
    def __init__(self):
        self._cache = self._load_cache()
        self._local = self._load_local()

    def _load_cache(self):
        try:
            with open(CAS_CACHE_PATH) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self):
        try:
            with open(CAS_CACHE_PATH, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def _load_local(self):
        return {
            "50-78-2": {"name": "2-acetoxybenzoic acid", "formula": "C9H8O4", "type_hint": "ester carboxylic_acid aromatic_ring"},
            "103-90-2": {"name": "acetaminophen", "formula": "C8H9NO2", "type_hint": "amide phenol"},
            "69-72-7": {"name": "salicylic acid", "formula": "C7H6O3", "type_hint": "carboxylic_acid phenol"},
            "79-09-4": {"name": "propionic acid", "formula": "C3H6O2", "type_hint": "carboxylic_acid"},
            "64-19-7": {"name": "acetic acid", "formula": "C2H4O2", "type_hint": "carboxylic_acid"},
            "67-64-1": {"name": "acetone", "formula": "C3H6O", "type_hint": "ketone"},
            "67-56-1": {"name": "methanol", "formula": "CH4O", "type_hint": "alcohol"},
            "64-17-5": {"name": "ethanol", "formula": "C2H6O", "type_hint": "alcohol"},
            "71-23-8": {"name": "propanol", "formula": "C3H8O", "type_hint": "alcohol"},
            "75-07-0": {"name": "acetaldehyde", "formula": "C2H4O", "type_hint": "aldehyde"},
            "100-52-7": {"name": "benzaldehyde", "formula": "C7H6O", "type_hint": "aldehyde aromatic_ring"},
            "100-66-3": {"name": "anisole", "formula": "C7H8O", "type_hint": "ether aromatic_ring"},
            "108-95-2": {"name": "phenol", "formula": "C6H6O", "type_hint": "phenol"},
            "71-43-2": {"name": "benzene", "formula": "C6H6", "type_hint": "aromatic_ring"},
            "100-42-5": {"name": "styrene", "formula": "C8H8", "type_hint": "alkene aromatic_ring"},
            "121-44-8": {"name": "triethylamine", "formula": "C6H15N", "type_hint": "amine"},
            "62-53-3": {"name": "aniline", "formula": "C6H7N", "type_hint": "aniline"},
            "75-05-8": {"name": "acetonitrile", "formula": "C2H3N", "type_hint": "nitrile"},
            "67-66-3": {"name": "chloroform", "formula": "CHCl3", "type_hint": "halide"},
            "75-09-2": {"name": "dichloromethane", "formula": "CH2Cl2", "type_hint": "halide"},
            "107-13-1": {"name": "acrylonitrile", "formula": "C3H3N", "type_hint": "alkene nitrile"},
            "74-85-1": {"name": "ethylene", "formula": "C2H4", "type_hint": "alkene"},
            "74-86-2": {"name": "acetylene", "formula": "C2H2", "type_hint": "alkyne"},
            "106-97-8": {"name": "butane", "formula": "C4H10", "type_hint": "alkene"},
            "110-82-7": {"name": "cyclohexane", "formula": "C6H12", "type_hint": "cyclic"},
            "108-88-3": {"name": "toluene", "formula": "C7H8", "type_hint": "aromatic_ring"},
            "100-41-4": {"name": "ethylbenzene", "formula": "C8H10", "type_hint": "aromatic_ring"},
            "98-86-2": {"name": "acetophenone", "formula": "C8H8O", "type_hint": "ketone aromatic_ring"},
            "98-95-3": {"name": "nitrobenzene", "formula": "C6H5NO2", "type_hint": "nitro aromatic_ring"},
            "100-47-0": {"name": "benzonitrile", "formula": "C7H5N", "type_hint": "nitrile aromatic_ring"},
            "88-89-1": {"name": "picric acid", "formula": "C6H3N3O7", "type_hint": "phenol nitro"},
            "106-50-3": {"name": "p-phenylenediamine", "formula": "C6H8N2", "type_hint": "amine aromatic_ring"},
            "95-76-1": {"name": "3,4-dichloroaniline", "formula": "C6H5Cl2N", "type_hint": "halide aniline"},
            "3568-94-3": {"name": "4-methyl-5-phenyl-4,5-dihydro-1,3-oxazol-2-amine", "formula": "C10H12N2O", "type_hint": "amine aromatic_ring ether cyclic"},
            "1972-08-3": {"name": "11-hydroxy-Δ9-tetrahydrocannabinol", "formula": "C21H30O3", "type_hint": "phenol alcohol alkene ether cyclic"},
            "7704-34-9": {"name": "sulfur", "formula": "S8", "type_hint": "thiol"},
        }

    def resolve(self, cas_number):
        cas = cas_number.strip()
        if cas in self._local:
            entry = dict(self._local[cas])
            entry["cas"] = cas; entry["source"] = "local_db"
            return entry
        if cas in self._cache:
            entry = dict(self._cache[cas])
            entry["cas"] = cas; entry["source"] = "cache"
            return entry
        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/JSON"
            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            props = {}
            if "PC_Compounds" in data and data["PC_Compounds"]:
                for prop in data["PC_Compounds"][0].get("props", []):
                    urn = prop.get("urn", {}).get("label", "")
                    val = prop.get("value", {}).get("sval", "")
                    props[urn] = val
            name = props.get("IUPAC Name", props.get("Molecular Formula", cas))
            formula = props.get("Molecular Formula", "")
            entry = {"cas": cas, "name": name, "formula": formula, "source": "pubchem", "type_hint": ""}
            self._cache[cas] = entry
            self._save_cache()
            return entry
        except Exception as e:
            return {"cas": cas, "name": f"CAS-{cas}", "formula": "", "source": "unresolved", "type_hint": "", "error": str(e)}


# ====================================================================
# CH3MPILER - Main Class
# ====================================================================
class Ch3mpiler:
    def __init__(self):
        self.catalog = self._load_catalog()
        self.cas_resolver = CASResolver()

    def _load_catalog(self):
        try:
            with open(CATALOG_PATH) as f:
                return json.load(f)
        except Exception:
            return []

    def analyze(self, target):
        """Analyze molecule: type, FGs, grammar-derived disconnections."""
        mol_type, source = get_molecule_type(target, self.catalog)
        fgs = find_fgs(target)
        
        cuts = []
        if fgs and mol_type:
            cuts = find_disconnections(fgs, mol_type, max_results=10)
        
        # Find analogs from catalog
        analogs = []
        for e in self.catalog[:500]:
            et = {}
            for pn, pf in zip(PNAMES, PFIELDS):
                v = e.get(pf, ""); 
                if v: et[pn] = v
            if len(et) == 12:
                d, _ = tup_dist(mol_type, et)
                if d < 3.5 and d > 0:
                    analogs.append({"n": e.get("name",""), "d": round(d, 3)})
        analogs.sort(key=lambda x: x["d"])
        
        return {"target": target, "type": fmt_tup(mol_type),
                "type_source": source, "fgs": fgs,
                "cuts": cuts, "analogs": analogs[:8]}

    def retrosynthesis(self, target, depth=2):
        """Full retrosynthetic tree using grammar-derived rules."""
        base = self.analyze(target)
        tree = {"target": target, "type": base["type"],
                "fgs": base["fgs"], "cuts": base["cuts"],
                "analogs": base["analogs"], "steps": []}
        
        if depth > 0:
            for idx, cut in enumerate(base["cuts"][:3]):
                sname1 = f"{cut['fg1']}_precursor"
                sname2 = f"{cut['fg2']}_precursor"
                sub1 = self.retrosynthesis(sname1, depth-1)
                sub2 = self.retrosynthesis(sname2, depth-1)
                tree["steps"].append({
                    "bond": cut["bond"],
                    "bond_desc": cut["bond_desc"],
                    "delta": cut["delta"],
                    "fg1": cut["fg1"], "fg2": cut["fg2"],
                    "product_type": cut["product_type"],
                    "precursors": [
                        {"name": sname1, "fg_hint": cut["fg1"], "type": sub1["type"],
                         "further": sub1["cuts"][:2] if depth > 1 else []},
                        {"name": sname2, "fg_hint": cut["fg2"], "type": sub2["type"],
                         "further": sub2["cuts"][:2] if depth > 1 else []},
                    ]
                })
        return tree

    def forward(self, reagents):
        """Predict forward reaction: find most compatible bond between reagent FGs.
        
        Ranking: specificity then delta (more specific bonds preferred).
        """
        BOND_SPECIFICITY = {
            "amide_link": 10, "ester_link": 9, "carbonyl": 8,
            "aromatic": 7, "double_bond": 6, "triple_bond": 5,
            "co_sigma": 3, "cn_sigma": 3, "ether_link": 2,
            "sigma_single": 1, "pi_bond": 1, "hydrogen_bond": 0,
        }
        all_fgs = set()
        for r in reagents:
            all_fgs.update(find_fgs(r))
        if not all_fgs:
            return {"reagents": reagents, "error": "no FGs identified"}
        
        best = None
        best_score = (-1, 999)
        for fg1 in sorted(all_fgs):
            for fg2 in sorted(all_fgs):
                for bname in BOND_TYPES:
                    fg1_t = FG.get(fg1, {}); fg2_t = FG.get(fg2, {})
                    bond = BOND_TYPES.get(bname, {})
                    if fg1_t and fg2_t and bond:
                        product = bond_product_type(fg1_t, fg2_t, bond)
                        tensor = tensor_type(fg1_t, fg2_t)
                        d, _ = tup_dist(product, tensor)
                        spec = BOND_SPECIFICITY.get(bname, 0)
                        score = (spec, -d)
                        if score > best_score:
                            best_score = score
                            best = {"fg1": fg1, "fg2": fg2, "bond": bname,
                                    "bond_desc": bond.get("desc",""),
                                    "structuring_delta": round(d, 3),
                                    "product_type": fmt_tup(product)}
        return {"reagents": reagents, "fgs": sorted(all_fgs),
                "prediction": best} if best else {"reagents": reagents, "fgs": sorted(all_fgs), "error": "no compatible bond"}
    def resolve_cas(self, cas_number):
        return self.cas_resolver.resolve(cas_number)

    def resolve_and_analyze(self, cas_number, do_retrosynthesis=False, depth=2):
        info = self.resolve_cas(cas_number)
        name = info.get("name", cas_number)
        if do_retrosynthesis:
            tree = self.retrosynthesis(name, depth=depth)
            tree["cas_info"] = info
            return tree
        result = self.analyze(name)
        result["cas_info"] = info
        return result
# ====================================================================
# OUTPUT FORMATTERS
# ====================================================================
def print_retrosynthesis(tree, indent=0):
    pad = "  " * indent
    target = tree["target"]
    ttype = tree["type"]
    
    if "cas_info" in tree:
        ci = tree["cas_info"]
        src = ci.get("source", "")
        cas = ci.get("cas", "")
        formula = ci.get("formula", "")
        if src != "unresolved":
            print(f"{pad}CAS: {cas}  ({src})")
            if formula:
                print(f"{pad}Formula: {formula}")
    
    print(f"{pad}{target}")
    print(f"{pad}  Type: {ttype}")
    
    fgs = tree.get("fgs", [])
    if fgs:
        print(f"{pad}  FGs: {', '.join(fgs)}")
    
    print(f"{pad}  Grammar-derived disconnections (no named reactions):")
    steps = tree.get("steps", [])
    if not steps:
        print(f"{pad}  (terminal)")
        return
    
    for idx, step in enumerate(steps):
        print(f"{pad}  ── Cut {idx+1}: {step['bond']} (δ={step['delta']}) ──")
        print(f"{pad}     {step['bond_desc']}")
        print(f"{pad}     Between: {step['fg1']} + {step['fg2']}")
        print(f"{pad}     Product type: {step['product_type']}")
        
        for pidx, prec in enumerate(step.get("precursors", [])):
            print(f"{pad}     Precursor {pidx+1}: {prec['name']}  [{prec['fg_hint']}]")
            f_list = prec.get("further", [])
            if f_list:
                for fc in f_list[:2]:
                    print(f"{pad}       \u2514 {fc['bond']} (δ={fc['delta']})")

def print_analysis(result):
    print(f"Target: {result['target']}")
    print(f"Type: {result['type']}  [{result.get('type_source','?')}]")
    fgs = result.get("fgs", [])
    if fgs:
        print(f"FGs: {', '.join(fgs)}")
    
    cuts = result.get("cuts", [])
    if cuts:
        print(f"\nGrammar-derived disconnections (ranked by δ, lower=better):")
        print(f"  {'Bond':20s} {'δ':8s} {'Between':30s} {'Product Type':40s}")
        print(f"  {'-'*20} {'-'*8} {'-'*30} {'-'*40}")
        for c in cuts[:8]:
            between = f"{c['fg1']}+{c['fg2']}"
            print(f"  {c['bond']:20s} {c['delta']:<8.3f} {between:30s} {c['product_type']:40s}")
    else:
        print(f"\n  No disconnections found.")
    
    analogs = result.get("analogs", [])
    if analogs:
        print(f"\nStructural analogs:")
        for a in analogs[:5]:
            print(f"  {a['n']:40s} d={a['d']:.3f}")


# ====================================================================
# MAIN CLI
# ====================================================================
def main():
    _dash_map = str.maketrans({chr(c): '-' for c in [0x2212, 0x2013, 0x2014, 0x2015, 0xff0d, 0xfe63]})
    sys.argv = [s.translate(_dash_map) for s in sys.argv]
    
    parser = argparse.ArgumentParser(
        description="ch3mpiler - Grammar-derived retrosynthetic compiler (no named reactions)")
    parser.add_argument("--target", help="Molecule name")
    parser.add_argument("--retrosynthesis", action="store_true", help="Full retrosynthetic tree")
    parser.add_argument("--cas", help="CAS Registry Number")
    parser.add_argument("--depth", type=int, default=2, help="Retrosynthetic depth")
    parser.add_argument("--forward", nargs="+", help="Reagents for forward prediction")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--fg", help="Analyze functional group")
    parser.add_argument("--list-fgs", action="store_true", help="List FGs")
    parser.add_argument("--list-bonds", action="store_true", help="List bond types")
    parser.add_argument("--show-cas-cache", action="store_true", help="Show CAS cache")
    
    args = parser.parse_args()
    ch = Ch3mpiler()
    
    if args.cas:
        if args.retrosynthesis:
            tree = ch.resolve_and_analyze(args.cas, do_retrosynthesis=True, depth=args.depth)
            print("=" * 66)
            print("  ch3mpiler — Retrosynthetic Analysis (grammar-derived)")
            print("=" * 66)
            print_retrosynthesis(tree)
        else:
            r = ch.resolve_and_analyze(args.cas)
            info = r.get("cas_info", {})
            print(f"CAS: {info.get('cas', args.cas)}")
            print(f"Name: {info.get('name', 'unknown')}  ({info.get('source', '')})")
            if info.get("formula"): print(f"Formula: {info['formula']}")
            if info.get("smiles"): print(f"SMILES: {info['smiles']}")
            print_analysis(r)
        return
    
    if args.list_fgs:
        print("Functional Groups:")
        for fg_name in sorted(FG.keys()):
            t = {p: FG[fg_name].get(p, "?") for p in PNAMES}
            print(f"  {fg_name:30s}  {fmt_tup(t)}")
        return
    
    if args.list_bonds:
        print("Grammar-derived bond types:")
        for bname in sorted(BOND_TYPES.keys()):
            b = BOND_TYPES[bname]
            t = {p: b.get(p, "?") for p in PNAMES}
            print(f"  {bname:20s}  {b.get('desc',''):45s}  {fmt_tup(t)}")
        return
    
    if args.show_cas_cache:
        cache = ch.cas_resolver._cache
        if not cache:
            print("CAS cache is empty.")
        else:
            print(f"Cached CAS ({len(cache)}):")
            for cas, entry in sorted(cache.items()):
                print(f"  {cas:15s}  {entry.get('name','?'):40s}  [{entry.get('source','?')}]")
        return
    
    if args.fg:
        if args.fg in FG:
            t = {p: FG[args.fg].get(p, "?") for p in PNAMES}
            print(f"FG: {args.fg}")
            print(f"Type: {fmt_tup(t)}")
        else:
            print(f"Unknown FG: {args.fg}")
            print(f"Known: {', '.join(sorted(FG.keys()))}")
        return
    
    if args.target:
        if args.retrosynthesis:
            tree = ch.retrosynthesis(args.target, depth=args.depth)
            print("=" * 66)
            print("  ch3mpiler — Retrosynthetic Analysis (grammar-derived)")
            print("=" * 66)
            print_retrosynthesis(tree)
        else:
            r = ch.analyze(args.target)
            print_analysis(r)
        return
    
    if args.forward:
        r = ch.forward(args.forward)
        print(f"Reagents: {', '.join(r['reagents'])}")
        if "error" in r:
            print(f"  {r['error']}")
        else:
            p = r.get("prediction", {})
            print(f"FGs: {', '.join(r.get('fgs',[]))}")
            print(f"Best bond: {p.get('bond','?')} ({p.get('bond_desc','')})")
            print(f"  Between: {p.get('fg1','?')} + {p.get('fg2','?')}")
            print(f"  Structuring Δ: {p.get('structuring_delta','?')}")
            print(f"  Product: {p.get('product_type','?')}")
        return
    
    if args.interactive:
        print("ch3mpiler interactive — grammar-derived bond rules")
        print("Commands: <name>, retro:<name>, cas:<n>, cas-retro:<n>,")
        print("          fwd:r1,r2, fg:<n>, fgs, bonds, quit")
        while True:
            try:
                c = input(">>> ").strip()
                if c in ("quit","q","exit"): break
                if c == "fgs":
                    for f in sorted(FG.keys()): print(f"  {f}")
                elif c == "bonds":
                    for b in sorted(BOND_TYPES.keys()):
                        print(f"  {b:20s}  {BOND_TYPES[b].get('desc','')}")
                elif c.startswith("fg:"):
                    fg = c[3:]
                    if fg in FG:
                        t = {p: FG[fg].get(p,"?") for p in PNAMES}
                        print(f"FG {fg}: {fmt_tup(t)}")
                    else: print(f"Unknown FG: {fg}")
                elif c.startswith("retro:"):
                    print_retrosynthesis(ch.retrosynthesis(c[6:], depth=2))
                elif c.startswith("cas:"):
                    r = ch.resolve_and_analyze(c[4:])
                    info = r.get("cas_info",{})
                    print(f"CAS: {info.get('cas','')} Name: {info.get('name','')}")
                    print_analysis(r)
                elif c.startswith("cas-retro:"):
                    print_retrosynthesis(ch.resolve_and_analyze(c[10:], do_retrosynthesis=True, depth=2))
                elif c.startswith("fwd:"):
                    r = ch.forward(c[4:].split(","))
                    print(f"Reagents: {', '.join(r['reagents'])}")
                    if "error" not in r:
                        p = r.get("prediction",{})
                        print(f"  -> {p.get('bond','?')} ({p.get('bond_desc','')})")
                    else: print(f"  {r['error']}")
                else:
                    r = ch.analyze(c)
                    print_analysis(r)
            except (EOFError, KeyboardInterrupt): break
        return
    
    # Default demo
    print("=" * 66)
    print("  ch3mpiler — Grammar-Derived Retrosynthetic Engine")
    print("  No named reactions — disconnections from 12-primitive rules")
    print("=" * 66)
    print()
    print("Demo: benzaldehyde")
    r = ch.analyze("benzaldehyde")
    print_analysis(r)
    print()
    print("Try: ch3mpiler --cas 3568-94-3 --retrosynthesis")

if __name__ == "__main__":
    main()
