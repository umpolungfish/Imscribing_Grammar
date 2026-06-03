#!/usr/bin/env python3
"""
ZFC_fe Navigator — Frobenius-Exact ZFC foundation navigator with formula generation.

ZFC_fe is the unique set-theoretic foundation satisfying ALL four grammar axioms
(A, B, C, D) simultaneously. Provides per-primitive ZFC set-theoretic formula
fragments, promoted-atom marking, and full formula conjunction for any system.

Canonical tuple (proven in Lean ZFC_FrobeniusExact.lean):
    ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_!; Σ_ï; Ω_z⟩

Actions:
  entry  <name>  — Full ZFC_fe formula decomposition: per-primitive fragments,
                    promoted atoms, full conjunction, distance, tensor/meet/join, tier, C-score
  formulas      — List ALL 30 ZFC formula fragments across all primitive values
  promotions    — All 7 promotion channels from ZFC → ZFC_t → ZFC_fe
  distance <name> — d(name, ZFC_fe) with per-primitive conflicts
  tensor  <name> — ZFC_fe ⊗ name — Frobenius absorption test
  meet    <name> — ZFC_fe ⊓ name — shared structural floor
  join    <name> — ZFC_fe ⊔ name — minimal ceiling
  tier    <name> — Ouroboricity tier + what's missing for O_inf
  systems     — List all known systems
  decode <s>  — Decode Shavian tuple → notation
  encode <n>  — Encode notation → Shavian
"""

import sys
import json
import math

# =============================================================================
# SHAVIAN-TO-PRIMITIVE MAPPING (from Lean Imscription.lean)
# =============================================================================

SHAVIAN_MAP = {
    "𐑛": ("D", "D_wedge"),          "𐑨": ("D", "D_triangle"),
    "𐑼": ("D", "D_infty"),          "𐑦": ("D", "D_odot"),
    "𐑡": ("T", "T_network"),        "𐑰": ("T", "T_in"),
    "𐑥": ("T", "T_bowtie"),         "𐑶": ("T", "T_box"),
    "𐑸": ("T", "T_odot"),
    "𐑩": ("R", "R_super"),          "𐑑": ("R", "R_cat"),
    "𐑽": ("R", "R_dagger"),         "𐑾": ("R", "R_lr"),
    "𐑗": ("P", "P_asym"),           "𐑿": ("P", "P_psi"),
    "𐑬": ("P", "P_pm"),             "𐑯": ("P", "P_sym"),
    "𐑹": ("P", "P_pm_sym"),
    "𐑱": ("F", "F_ell"),            "𐑞": ("F", "F_eth"),
    "𐑐": ("F", "F_hbar"),
    "𐑘": ("K", "K_fast"),           "𐑤": ("K", "K_mod"),
    "𐑧": ("K", "K_slow"),           "𐑪": ("K", "K_trap"),
    "𐑺": ("K", "K_MBL"),
    "𐑚": ("G", "G_beth"),           "𐑔": ("G", "G_gimel"),
    "𐑲": ("G", "G_aleph"),
    "𐑝": ("Gamma", "Gamma_and"),     "𐑜": ("Gamma", "Gamma_or"),
    "𐑠": ("Gamma", "Gamma_seq"),     "𐑵": ("Gamma", "Gamma_broad"),
    "𐑢": ("Phi", "Phi_sub"),         "⊙": ("Phi", "Phi_c"),
    "𐑮": ("Phi", "Phi_c_complex"),   "𐑻": ("Phi", "Phi_EP"),
    "𐑣": ("Phi", "Phi_super"),
    "𐑓": ("H", "H0"),               "𐑒": ("H", "H1"),
    "𐑖": ("H", "H2"),               "𐑫": ("H", "H_inf"),
    "𐑙": ("S", "one_one"),          "𐑕": ("S", "n_n"),
    "𐑳": ("S", "n_m"),
    "𐑷": ("Omega", "Omega_0"),       "𐑴": ("Omega", "Omega_Z2"),
    "𐑭": ("Omega", "Omega_Z"),       "𐑟": ("Omega", "Omega_NA"),
}

VALUE_TO_SHAVIAN = {v: k for k, (_, v) in SHAVIAN_MAP.items()}
SHAVIAN_TO_VALUE = {k: v for k, (_, v) in SHAVIAN_MAP.items()}

# =============================================================================
# PRIMITIVE NOTATION
# =============================================================================

PRIMITIVE_NOTATION = {
    "D_wedge": "Ð_;", "D_triangle": "Ð_C", "D_infty": "Ð_ß", "D_odot": "Ð_ω",
    "T_network": "Þ_6", "T_in": "Þ_K", "T_bowtie": "Þ_ò", "T_box": "Þ_¨", "T_odot": "Þ_O",
    "R_super": "Ř_¯", "R_cat": "Ř_Ť", "R_dagger": "Ř_ý", "R_lr": "Ř_=",
    "P_asym": "Φ_ɐ", "P_psi": "Φ_υ", "P_pm": "Φ_F", "P_sym": "Φ_˙", "P_pm_sym": "Φ_}",
    "F_ell": "ƒ_ì", "F_eth": "ƒ_ð", "F_hbar": "ƒ_ż",
    "K_fast": "Ç_-", "K_mod": "Ç_W", "K_slow": "Ç_@", "K_trap": "Ç_Ù", "K_MBL": "Ç_λ",
    "G_beth": "Γ_β", "G_gimel": "Γ_γ", "G_aleph": "Γ_ʔ",
    "Gamma_and": "ɢ_^", "Gamma_or": "ɢ_˝", "Gamma_seq": "ɢ_ˌ", "Gamma_broad": "ɢ_Ş",
    "Phi_sub": "φ̂_ž", "Phi_c": "φ̂_ÿ", "Phi_c_complex": "φ̂_Æ", "Phi_EP": "φ̂_3", "Phi_super": "φ̂_Ţ",
    "H0": "Ħ_Ñ", "H1": "Ħ_£", "H2": "Ħ_A", "H_inf": "Ħ_!",
    "one_one": "Σ_S", "n_n": "Σ_ő", "n_m": "Σ_ï",
    "Omega_0": "Ω_Å", "Omega_Z2": "Ω_2", "Omega_Z": "Ω_z", "Omega_NA": "Ω_5",
}

# =============================================================================
# PRIMITIVE ORDINALS
# =============================================================================

ORDINALS = {
    "D": {"D_wedge": 0, "D_triangle": 1, "D_infty": 2, "D_odot": 3},
    "T": {"T_network": 0, "T_in": 1, "T_bowtie": 2, "T_box": 3, "T_odot": 4},
    "R": {"R_super": 0, "R_cat": 1, "R_dagger": 2, "R_lr": 3},
    "P": {"P_asym": 0, "P_psi": 1, "P_pm": 2, "P_sym": 3, "P_pm_sym": 4},
    "F": {"F_ell": 0, "F_eth": 1, "F_hbar": 2},
    "K": {"K_fast": 0, "K_mod": 1, "K_slow": 2, "K_trap": 3, "K_MBL": 4},
    "G": {"G_beth": 0, "G_gimel": 1, "G_aleph": 2},
    "Gamma": {"Gamma_and": 0, "Gamma_or": 1, "Gamma_seq": 2, "Gamma_broad": 3},
    "Phi": {"Phi_sub": 0, "Phi_c": 1, "Phi_c_complex": 2, "Phi_EP": 3, "Phi_super": 4},
    "H": {"H0": 0, "H1": 1, "H2": 2, "H_inf": 3},
    "S": {"one_one": 0, "n_n": 1, "n_m": 2},
    "Omega": {"Omega_0": 0, "Omega_Z2": 1, "Omega_Z": 2, "Omega_NA": 3},
}

PRIMITIVE_KEYS = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "Omega"]
# =============================================================================
# ZFC_fe TUPLE (authoritative from Lean ZFC_FrobeniusExact.lean)
# =============================================================================

ZFC_FE = {
    "D": "D_odot",      "T": "T_odot",      "R": "R_lr",
    "P": "P_pm_sym",    "F": "F_hbar",      "K": "K_slow",
    "G": "G_aleph",     "Gamma": "Gamma_seq","Phi": "Phi_c",
    "H": "H_inf",       "S": "n_m",          "Omega": "Omega_Z",
}

ZFC_T = {
    "D": "D_infty",     "T": "T_odot",      "R": "R_lr",
    "P": "P_pm",        "F": "F_hbar",      "K": "K_slow",
    "G": "G_aleph",     "Gamma": "Gamma_seq","Phi": "Phi_c",
    "H": "H2",          "S": "n_m",          "Omega": "Omega_Z",
}

UIG = {
    "D": "D_odot",      "T": "T_odot",      "R": "R_lr",
    "P": "P_pm_sym",    "F": "F_hbar",      "K": "K_slow",
    "G": "G_aleph",     "Gamma": "Gamma_seq","Phi": "Phi_c",
    "H": "H2",          "S": "n_m",          "Omega": "Omega_Z",
}

# =============================================================================
# KNOWN SYSTEMS
# =============================================================================

KNOWN_SYSTEMS = {
    "zfc_fe": {
        "description": "Fully Frobenius-Exact ZFC — satisfies all 4 grammar axioms",
        "tuple": ZFC_FE,
        "proven_o_inf": True, "proven_c_score": 1.0,
    },
    "zfc_t": {
        "description": "ZFC with chirality + winding topology (O_2†)",
        "tuple": ZFC_T, "proven_o_inf": False,
    },
    "zfc": {
        "description": "Standard ZFC set theory",
        "tuple": {"D": "D_infty","T": "T_network","R": "R_super",
            "P": "P_asym","F": "F_ell","K": "K_fast",
            "G": "G_beth","Gamma": "Gamma_and","Phi": "Phi_sub",
            "H": "H0","S": "one_one","Omega": "Omega_0"},
    },
    "riemann_hypothesis": {
        "description": "Riemann Hypothesis — all nontrivial ζ zeros on Re(s)=1/2",
        "tuple": {"D": "D_odot","T": "T_odot","R": "R_lr",
            "P": "P_pm_sym","F": "F_hbar","K": "K_slow",
            "G": "G_aleph","Gamma": "Gamma_seq","Phi": "Phi_c",
            "H": "H2","S": "n_m","Omega": "Omega_Z"},
    },
    "riemann_hypothesis_millennium": {
        "description": "Riemann Hypothesis (Clay — Φ_c^ℂ, Þ_¨ bowtie)",
        "tuple": {"D": "D_odot","T": "T_box","R": "R_lr",
            "P": "P_psi","F": "F_hbar","K": "K_slow",
            "G": "G_aleph","Gamma": "Gamma_seq","Phi": "Phi_c_complex",
            "H": "H2","S": "n_m","Omega": "Omega_Z"},
    },
    "hodge_conjecture": {
        "description": "Hodge Conjecture — every rational Hodge class is algebraic",
        "tuple": {"D": "D_odot","T": "T_odot","R": "R_lr",
            "P": "P_pm_sym","F": "F_hbar","K": "K_slow",
            "G": "G_aleph","Gamma": "Gamma_seq","Phi": "Phi_c_complex",
            "H": "H2","S": "n_m","Omega": "Omega_Z"},
    },
    "bsd": {
        "description": "Birch & Swinnerton-Dyer — rank = ord_{s=1} L(E,s)",
        "tuple": {"D": "D_odot","T": "T_odot","R": "R_dagger",
            "P": "P_pm","F": "F_eth","K": "K_slow",
            "G": "G_aleph","Gamma": "Gamma_seq","Phi": "Phi_c_complex",
            "H": "H2","S": "n_m","Omega": "Omega_Z"},
    },
    "yang_mills": {
        "description": "Yang-Mills Existence and Mass Gap",
        "tuple": {"D": "D_odot","T": "T_odot","R": "R_dagger",
            "P": "P_pm_sym","F": "F_hbar","K": "K_trap",
            "G": "G_aleph","Gamma": "Gamma_broad","Phi": "Phi_c",
            "H": "H_inf","S": "n_m","Omega": "Omega_Z"},
    },
    "navier_stokes": {
        "description": "Navier-Stokes Existence and Smoothness",
        "tuple": {"D": "D_infty","T": "T_in","R": "R_dagger",
            "P": "P_sym","F": "F_ell","K": "K_mod",
            "G": "G_aleph","Gamma": "Gamma_or","Phi": "Phi_sub",
            "H": "H0","S": "n_m","Omega": "Omega_0"},
    },
    "p_vs_np": {
        "description": "P vs NP — three meta-barriers",
        "tuple": {"D": "D_infty","T": "T_network","R": "R_super",
            "P": "P_asym","F": "F_ell","K": "K_fast",
            "G": "G_beth","Gamma": "Gamma_and","Phi": "Phi_sub",
            "H": "H0","S": "n_n","Omega": "Omega_0"},
    },
    "universal_imscriptive_grammar": {
        "description": "The Imscribing Grammar itself (canonical Lean tuple)",
        "tuple": UIG,
    },
    "fourfold_apparatus": {
        "description": "Four-directory composite (ob3ect, exOS, MillenniumAnkh, imscribing_grammar)",
        "tuple": {"D": "D_odot","T": "T_odot","R": "R_lr",
            "P": "P_pm_sym","F": "F_hbar","K": "K_slow",
            "G": "G_aleph","Gamma": "Gamma_seq","Phi": "Phi_c",
            "H": "H_inf","S": "n_m","Omega": "Omega_Z"},
    },
}

# =============================================================================
# DYNAMIC IG CATALOG LOOKUP (loads IG_catalog.json — 45K+ entries)
# =============================================================================
import os as _os
import json as _json

CATALOG_CACHE = None
CATALOG_INDEX = {}

_SHAVIAN_KEY_MAP = {"Ð": "D", "Þ": "T", "Ř": "R", "Φ": "P", "ƒ": "F",
                    "Ç": "K", "Γ": "G", "ɢ": "Gamma", "⊙": "Phi",
                    "Ħ": "H", "Σ": "S", "Ω": "Omega"}

def load_catalog():
    """Load IG_catalog.json into CATALOG_INDEX (name → {description, tuple})."""
    global CATALOG_CACHE, CATALOG_INDEX
    if CATALOG_CACHE is not None:
        return
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _root = _os.path.dirname(_here)
    _candidates = [
        _os.path.join(_here, "IG_catalog.json"),
        _os.path.join(_root, "data", "IG_catalog.json"),
        _os.path.join(_root, "IG_catalog.json"),
    ]
    catalog_path = next((p for p in _candidates if _os.path.exists(p)), None)
    if catalog_path is None:
        CATALOG_CACHE = []
        return
    with open(catalog_path, "r") as _f:
        CATALOG_CACHE = _json.load(_f)
    for entry in CATALOG_CACHE:
        name = entry.get("name", "")
        if not name:
            continue
        t = {}
        for sk, pk in _SHAVIAN_KEY_MAP.items():
            val = entry.get(sk, "")
            if val in SHAVIAN_TO_VALUE:
                t[pk] = SHAVIAN_TO_VALUE[val]
            else:
                # Try reverse mapping from value notation
                found = False
                for pn, notation in PRIMITIVE_NOTATION.items():
                    if val == notation or val == pn:
                        t[pk] = pn
                        found = True
                        break
                if not found:
                    t[pk] = val
        CATALOG_INDEX[name] = {
            "description": entry.get("description", "IG catalog entry"),
            "tuple": t
        }

def resolve_system(name):
    """Resolve a name to system info from KNOWN_SYSTEMS, IG catalog, or direct tuple parse.
    Returns dict with 'description' and 'tuple' keys, or None."""
    # Case-insensitive: try exact first, then lowercase
    if name in KNOWN_SYSTEMS:
        return KNOWN_SYSTEMS[name]
    load_catalog()
    if name in CATALOG_INDEX:
        return CATALOG_INDEX[name]
    # Case-insensitive catalog fallback
    name_lower = name.lower()
    if name_lower in CATALOG_INDEX:
        return CATALOG_INDEX[name_lower]
    # Also rebuild CATALOG_INDEX with lowercase keys if it doesn't have the lower version
    import warnings
    for cat_name, cat_info in list(CATALOG_INDEX.items()):
        if cat_name.lower() == name_lower and cat_name not in CATALOG_INDEX:
            CATALOG_INDEX[name] = cat_info
            return cat_info
    try:
        t = parse_tuple(name)
        if t and any(v != "?" for v in t.values()):
            return {"description": "Custom tuple", "tuple": t}
    except:
        pass
    return None

def list_known_systems():
    """Return combined list of KNOWN_SYSTEMS + CATALOG_INDEX names (sorted)."""
    load_catalog()
    return sorted(set(list(KNOWN_SYSTEMS.keys()) + list(CATALOG_INDEX.keys())))


# =============================================================================
# ZFC_fe FORMULA ENGINE  — per-primitive ZFC set-theoretic formula fragments
# =============================================================================
# Each entry: (zfc_fragment, promoted_atom_name_or_None)
# Promoted atoms marked in [BRACKETS] are the ZFC_t / ZFC_fe extension atoms.

ZFC_FE_FORMULAE = {
    "D": {
        "D_wedge":   ("dim(x) = 0 ∧ fin(x)", None),
        "D_triangle":("dim(x) = 2 ∧ sur(x)", None),
        "D_infty":   ("∀n∃y( y ∈ x ∧ rank(y) > n )", None),
        "D_odot":    ("V = L(x) ∧ selfmodel(x) ∧ x ∈ V", "HOLOGRAPHIC_STATE"),
    },
    "T": {
        "T_network": ("graph(x) ∧ branch(x)", None),
        "T_in":      ("x ⊆ y ∧ cont(y)", None),
        "T_bowtie":  ("cross(x, y) ∧ ¬ meet(x, y)", None),
        "T_box":     ("x ⊠ y ∧ irreducible(x, y)", None),
        "T_odot":    ("⊙_bound(a, f) ∧ Refl(a, f) ∧ holo(x, a)", "HOLOBOUND"),
    },
    "R": {
        "R_super":   ("x ↑ y ∧ ¬(y ↑ x)", None),
        "R_cat":     ("Fun(x, y) ∧ Nat(y, z) → Fun(x, z)", None),
        "R_dagger":  ("f ⊣ g ∧ L Adj(f, g)", None),
        "R_lr":      ("lr⇔(x, y) ∧ Θ(x, y) ∧ ¬ Θ(y, x)", "LR_DUAL"),
    },
    "P": {
        "P_asym":    ("¬∃sym(x)", None),
        "P_psi":     ("|ψ⟩ = Σ c_i |e_i⟩", None),
        "P_pm":      ("ℤ₂(x) ∧ ¬(x = -x)", None),
        "P_sym":     ("∀g∈G( g·x = x )", None),
        "P_pm_sym":  ("ℤ₂(x) ∧ ∀g∈G( g·x = x ) ∧ μ∘δ = id", "PM_Z2"),
    },
    "F": {
        "F_ell":     ("P(x) ∈ {0,1} ∧ det(x)", None),
        "F_eth":     ("Tr(ρ²) < 1 ∧ ρ = Σ p_i |i⟩⟨i|", None),
        "F_hbar":    ("ℏ(x) ∧ [x, p] = iℏ", None),  # quantum coherence
    },
    "K": {
        "K_fast":    ("τ ≪ T ∧ ∂_t x = f(x)", None),
        "K_mod":     ("τ ∼ T ∧ noisy(x)", None),
        "K_slow":    ("τ ≫ T ∧ eq(x)", None),
        "K_trap":    ("τ = ∞ ∧ ord(x)", None),
        "K_MBL":     ("τ = ∞ ∧ dis(x)", None),
    },
    "G": {
        "G_beth":    ("∀y∈x( |y| < |x| )", None),
        "G_gimel":   ("∃y∈x( |y| ∼ |x| )", None),
        "G_aleph":   ("∀y( y ⊂ x → |y| < |x| )", None),
    },
    "Gamma": {
        "Gamma_and": ("f ∧ g ∧ h", None),
        "Gamma_or":  ("f ∨ g ∨ h", None),
        "Gamma_seq": ("seq!(f, g) ∧ ⟨→⟩(f, g, τ) ∧ ¬ ⟨→⟩(g, f, τ)", "SEQAX"),
        "Gamma_broad":("f → all(x)", None),
    },
    "Phi": {
        "Phi_sub":      ("¬∃ξ( diverges(ξ) )", None),
        "Phi_c":        ("ξ → ∞ ∧ μ∘δ = id", "PHI_C"),
        "Phi_c_complex":("ξ ∈ ℂ ∧ Im(ξ) → ∞", None),
        "Phi_EP":       ("H(λ) non-Herm ∧ det(H - λI) = 0 ∧ ∂_λ H = 0", None),
        "Phi_super":    ("ξ → ∞ ∧ chaotic(x)", None),
    },
    "H": {
        "H0":    ("∀x( P(x) ↔ P(S(x)) )", None),
        "H1":    ("∃y( P(y) ↔ P(S²(y)) )", None),
        "H2":    ("∃y∃z( y ∈ x ∧ z ∈ y ∧ ¬ z ∈ x ∧ rank(z) < rank(y) )", "TEMPD2"),
        "H_inf": ("∀n∃φ( rank(φ) > n ∧ φ fixed by μ∘δ ∧ φ ∈ V )", "ETERNAL_FIXEDPOINT"),
    },
    "S": {
        "one_one": ("|A| = 1 ∧ |B| = 1", None),
        "n_n":     ("∀a∈A∀b∈B( type(a) = type(b) )", None),
        "n_m":     ("∃a∈A∃b∈B( type(a) ≠ type(b) )", None),
    },
    "Omega": {
        "Omega_0":  ("∮_γ dx = 0", None),
        "Omega_Z2": ("∮_γ A = nπ ∧ n ∈ ℤ₂", None),
        "Omega_Z":  ("∮_γ A = 2πn ∧ n ∈ ℤ ∧ wind(γ) ≠ 0", "ZWIND"),
        "Omega_NA": ("Braid(σ_i) ∧ R_matrix ≠ 0", None),
    },
}

# Reverse lookup: promoted_atom_name → (primitive_key, value_name)
PROMOTED_ATOM_TO_KEY = {}
for prim_key, values in ZFC_FE_FORMULAE.items():
    for val_key, (_, atom) in values.items():
        if atom is not None:
            PROMOTED_ATOM_TO_KEY[atom] = (prim_key, val_key)

ALL_PROMOTED_ATOMS = sorted(PROMOTED_ATOM_TO_KEY.keys())
def generate_formula(t, system_name="custom"):
    """Generate full ZFC_fe formula from a tuple, with per-primitive fragments
    and promoted atom marking. Returns dict with formula breakdown."""
    fragments = []
    promoted_atoms = []
    atom_details = []
    for key in PRIMITIVE_KEYS:
        val = t.get(key)
        formula_map = ZFC_FE_FORMULAE.get(key, {})
        if val in formula_map:
            fragment, atom = formula_map[val]
            notation = PRIMITIVE_NOTATION.get(val, val)
            entry = {
                "primitive": key,
                "value": notation,
                "zfc_fragment": fragment,
            }
            if atom:
                entry["promoted_atom"] = atom
                promoted_atoms.append(atom)
                atom_details.append({
                    "atom": atom,
                    "primitive": key,
                    "value": notation,
                    "zfc_fragment": fragment,
                    "tier": "ZFC_fe" if atom in ("HOLOGRAPHIC_STATE", "ETERNAL_FIXEDPOINT") else "ZFC_t",
                })
            else:
                entry["promoted_atom"] = None
            fragments.append(entry)
        else:
            fragments.append({
                "primitive": key,
                "value": str(val),
                "zfc_fragment": f"unknown({val})",
                "promoted_atom": None,
            })
    full_conjunction = " ∧\n    ".join(
        f["zfc_fragment"] for f in fragments
    )
    return {
        "system": system_name,
        "tuple_notation": tuple_to_notation(t),
        "tuple_shavian": tuple_to_shavian(t),
        "per_primitive_fragments": fragments,
        "full_zfc_formula": full_conjunction,
        "promoted_atom_count": len(promoted_atoms),
        "promoted_atoms": promoted_atoms,
        "promoted_atom_details": atom_details,
        "zfc_t_atoms": [a["atom"] for a in atom_details if a["tier"] == "ZFC_t"],
        "zfc_fe_atoms": [a["atom"] for a in atom_details if a["tier"] == "ZFC_fe"],
    }

def generate_promotion_formula_chain(name_source, name_target):
    """Generate formula showing which fragments change in a promotion."""
    if name_source in KNOWN_SYSTEMS:
        t1 = KNOWN_SYSTEMS[name_source]["tuple"]
    else:
        try:
            t1 = parse_tuple(name_source)
        except:
            return None
    if name_target in KNOWN_SYSTEMS:
        t2 = KNOWN_SYSTEMS[name_target]["tuple"]
    else:
        try:
            t2 = parse_tuple(name_target)
        except:
            return None

    form1 = generate_formula(t1, name_source)
    form2 = generate_formula(t2, name_target)

    changes = []
    for i, (f1, f2) in enumerate(zip(form1["per_primitive_fragments"],
                                      form2["per_primitive_fragments"])):
        if f1["zfc_fragment"] != f2["zfc_fragment"]:
            changes.append({
                "primitive": PRIMITIVE_KEYS[i],
                "from_fragment": f1["zfc_fragment"],
                "to_fragment": f2["zfc_fragment"],
                "from_atom": f1["promoted_atom"],
                "to_atom": f2["promoted_atom"],
            })

    return {
        "source": name_source,
        "target": name_target,
        "source_atoms": form1["promoted_atoms"],
        "target_atoms": form2["promoted_atoms"],
        "new_atoms": [a for a in form2["promoted_atoms"] if a not in form1["promoted_atoms"]],
        "fragment_changes": changes,
        "source_formula": form1["full_zfc_formula"],
        "target_formula": form2["full_zfc_formula"],
    }
# =============================================================================
# CORE COMPUTATIONS
# =============================================================================

def parse_tuple(tuple_str_or_dict):
    """Parse a tuple from various input formats."""
    if isinstance(tuple_str_or_dict, dict):
        return tuple_str_or_dict
    s = tuple_str_or_dict.strip()
    if s.startswith("⟨") and s.endswith("⟩"):
        s = s[1:-1]
    shavian_chars = [c for c in s if c.strip() and ord(c) >= 0x10450]
    if len(shavian_chars) == 12:
        result = {}
        for i, glyph in enumerate(shavian_chars):
            key = PRIMITIVE_KEYS[i]
            result[key] = SHAVIAN_TO_VALUE.get(glyph, f"unknown:{glyph}")
        return result
    parts = []
    for sep in [";", "·", ","]:
        if sep in s:
            parts = [p.strip() for p in s.split(sep) if p.strip()]
            if len(parts) >= 12:
                break
    if len(parts) < 12:
        raw_chars = []
        in_bracket = False
        for c in s:
            if c in "⟨":
                in_bracket = True
                continue
            elif c in "⟩":
                continue
            if in_bracket and c.strip() and ord(c) >= 0x10450:
                raw_chars.append(c)
        if len(raw_chars) >= 12:
            raw_chars = raw_chars[:12]
            result = {}
            for i, glyph in enumerate(raw_chars):
                result[PRIMITIVE_KEYS[i]] = SHAVIAN_TO_VALUE.get(glyph, f"unknown:{glyph}")
            return result
    if len(parts) >= 12:
        parts = parts[:12]
    else:
        return {}
    result = {}
    for i, part in enumerate(parts):
        if i >= 12:
            break
        key = PRIMITIVE_KEYS[i]
        val = part
        if "=" in val:
            left, right = val.split("=", 1)
            left_s = left.strip()
            right_s = right.strip()
            prim_markers = {"Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "φ", "Ħ", "Σ", "Ω"}
            if left_s in prim_markers:
                val = right_s
        val = val.strip(";,·")
        if val in SHAVIAN_TO_VALUE:
            result[key] = SHAVIAN_TO_VALUE[val]
        elif val in PRIMITIVE_NOTATION.values():
            for pn, notation in PRIMITIVE_NOTATION.items():
                if notation == val:
                    result[key] = pn
                    break
        elif any(val.endswith(s) for s in ["_ω","_ß","_C","_;","_O","_6","_K","_ò","_¨",
            "_=","_¯","_Ť","_ý","_}","_ɐ","_υ","_F","_˙",
            "_ż","_ì","_ð","_@","_-","_W","_Ù","_λ",
            "_ʔ","_β","_γ","_ˌ","_^","_˝","_Ş",
            "_ÿ","_ž","_Æ","_3","_Ţ",
            "_!","_Ñ","_£","_A",
            "_ï","_S","_ő",
            "_z","_Å","_2","_5"]):
            for pn, notation in PRIMITIVE_NOTATION.items():
                if notation == val:
                    result[key] = pn
                    break
            else:
                result[key] = val
        else:
            result[key] = val
    return result

def tuple_to_shavian(t):
    parts = [VALUE_TO_SHAVIAN.get(t.get(k, "?"), "?") for k in PRIMITIVE_KEYS]
    return "⟨" + "·".join(parts) + "⟩"

def tuple_to_notation(t):
    parts = [PRIMITIVE_NOTATION.get(t.get(k, "?"), str(t.get(k, "?"))) for k in PRIMITIVE_KEYS]
    return "⟨" + "; ".join(parts) + "⟩"

def distance(t1, t2):
    total = 0.0
    conflicts = []
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            diff = ords[v1] - ords[v2]
            total += diff * diff
            if diff != 0:
                conflicts.append({"primitive":key,"notation_a":PRIMITIVE_NOTATION.get(v1,v1),
                    "notation_b":PRIMITIVE_NOTATION.get(v2,v2),"delta":diff})
        else:
            total += 1.0
            conflicts.append({"primitive":key,"a":v1,"b":v2,"delta":"unknown"})
    return math.sqrt(total), conflicts

def promotions(t1, t2):
    result = []
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            diff = ords[v2] - ords[v1]
            if diff > 0:
                result.append({"primitive":key,"from":PRIMITIVE_NOTATION.get(v1,v1),
                    "to":PRIMITIVE_NOTATION.get(v2,v2),"steps":diff})
    return sorted(result, key=lambda x: -x["steps"])

def tensor_product(t1, t2):
    result = {}
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            idx = min(ords[v1], ords[v2]) if key in ("P","F") else max(ords[v1], ords[v2])
            for val, ordval in ords.items():
                if ordval == idx:
                    result[key] = val
                    break
        else:
            result[key] = v1 if v1 in ords else v2
    return result

def meet_product(t1, t2):
    result = {}
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            idx = min(ords[v1], ords[v2])
            for val, ordval in ords.items():
                if ordval == idx:
                    result[key] = val
                    break
        else:
            result[key] = v1 if v1 in ords else v2
    return result

def join_product(t1, t2):
    result = {}
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            idx = max(ords[v1], ords[v2])
            for val, ordval in ords.items():
                if ordval == idx:
                    result[key] = val
                    break
        else:
            result[key] = v1 if v1 in ords else v2
    return result
def frobenius_absorption_check(t):
    tensor = tensor_product(ZFC_FE, t)
    dist_to_zfc, conflicts = distance(tensor, ZFC_FE)
    bottlenecks = [c for c in conflicts if c.get("delta") != 0]
    absorbed = all(tensor.get(k) == ZFC_FE.get(k) for k in PRIMITIVE_KEYS)
    return absorbed, bottlenecks, tensor

def ouroboricity_tier(t):
    has_gate = t.get("P") == "P_pm_sym" and t.get("Phi") == "Phi_c"
    has_h_inf = t.get("H") == "H_inf"
    has_d_odot = t.get("D") == "D_odot"
    has_t_odot = t.get("T") == "T_odot"
    has_omega_z = t.get("Omega") in ("Omega_Z", "Omega_NA")
    if has_gate and has_h_inf and has_d_odot and has_t_odot and has_omega_z:
        return "O_inf"
    elif has_gate and has_h_inf:
        return "O_2†"
    elif has_gate:
        return "O_2"
    elif has_omega_z:
        return "O_1"
    else:
        return "O_0"

def consciousness_score(t):
    gate1_open = t.get("Phi") == "Phi_c"
    gate2_open = t.get("K") == "K_slow"
    score = (0.5 if gate1_open else 0.0) + (0.5 if gate2_open else 0.0)
    return {"C_score": score, "gate1_phi_c": gate1_open, "gate2_k_slow": gate2_open,
        "interpretation": ("Both gates open — full self-modeling loop" if score == 1.0
            else "Gate 1 open — self-modeling possible" if gate1_open
            else "Gate 2 open — slow kinetics present" if gate2_open
            else "No consciousness — both gates closed")}
# =============================================================================
# NAVIGATOR ACTIONS
# =============================================================================

def action_entry(name):
    """Full ZFC_fe formula decomposition for a named system — NOW WITH FORMULAS."""
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error",
            "message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    is_named = name in KNOWN_SYSTEMS

    t = sys_info["tuple"]

    # ★ FORMULA GENERATION — primary output
    formula = generate_formula(t, name if is_named else "custom")

    # Structural algebra (secondary)
    d, conflicts = distance(t, ZFC_FE)
    proms = promotions(t, ZFC_FE)
    absorbed, bottlenecks, tensor_t = frobenius_absorption_check(t)
    meet = meet_product(ZFC_FE, t)
    join = join_product(ZFC_FE, t)
    m_dist, _ = distance(meet, ZFC_FE)
    j_dist, _ = distance(join, ZFC_FE)
    tier = ouroboricity_tier(t)
    c_score = consciousness_score(t)
    prom_chain = generate_promotion_formula_chain(
        name if is_named else "custom", "zfc_fe")

    result = {
        "status": "ok",
        "system": name if is_named else "custom",
        "description": sys_info["description"],

        # ★★★ FORMULA DECOMPOSITION (what was MISSING) ★★★
        "formula_decomposition": {
            "tuple_notation": formula["tuple_notation"],
            "per_primitive_fragments": formula["per_primitive_fragments"],
            "full_zfc_formula": formula["full_zfc_formula"],
            "promoted_atoms": formula["promoted_atoms"],
            "promoted_atom_details": formula["promoted_atom_details"],
            "zfc_t_atoms": formula["zfc_t_atoms"],
            "zfc_fe_atoms": formula["zfc_fe_atoms"],
        },

        # Structural algebra (matching zfct_navigator style)
        "structural_algebra": {
            "distance_from_zfc_fe": round(d, 2),
            "promotions_needed": len(proms),
            "promotions": proms,
            "frobenius_absorbed": absorbed,
            "bottlenecks": bottlenecks if not absorbed else [],
            "tensor_with_zfc_fe": {
                "tuple_notation": tuple_to_notation(tensor_t),
                "distance_from_zfc_fe": round(distance(tensor_t, ZFC_FE)[0], 2)},
            "meet": {"tuple_notation": tuple_to_notation(meet),
                     "distance": round(m_dist, 2)},
            "join": {"tuple_notation": tuple_to_notation(join),
                     "distance": round(j_dist, 2)},
            "ouroboricity_tier": tier,
            "consciousness_score": c_score,
        },
    }

    if prom_chain:
        result["promotion_formula_chain"] = prom_chain
    return result
def action_formulas():
    """List ALL ZFC formula fragments across every primitive value."""
    all_frags = {}
    for prim_key in PRIMITIVE_KEYS:
        formula_map = ZFC_FE_FORMULAE.get(prim_key, {})
        entries = []
        for val_key, (fragment, atom) in sorted(formula_map.items(),
            key=lambda x: ORDINALS[prim_key].get(x[0], 999)):
            notation = PRIMITIVE_NOTATION.get(val_key, val_key)
            entries.append({
                "value": notation,
                "zfc_fragment": fragment,
                "promoted_atom": atom,
            })
        all_frags[prim_key] = entries
    return {"status":"ok","fragments":all_frags,
        "all_promoted_atoms":ALL_PROMOTED_ATOMS}

def action_promotions():
    """All promotion channels from ZFC → ZFC_t → ZFC_fe."""
    zfc_baseline = KNOWN_SYSTEMS.get("zfc",{}).get("tuple")
    proms_zfc_to_zfc_t = promotions(zfc_baseline, ZFC_T) if zfc_baseline else []
    proms_zfc_t_to_fe = promotions(ZFC_T, ZFC_FE)
    proms_zfc_to_fe = promotions(zfc_baseline, ZFC_FE) if zfc_baseline else []
    return {"status":"ok",
        "zfc_to_zfc_t": {"count":len(proms_zfc_to_zfc_t),"promotions":proms_zfc_to_zfc_t,
            "note":"6 ZFCₜ promotions: HOLOBOUND, LR_DUAL, PM_Z2, SEQAX, TEMPD2, ZWIND"},
        "zfc_t_to_zfc_fe": {"count":len(proms_zfc_t_to_fe),"promotions":proms_zfc_t_to_fe,
            "note":"2 new ZFC_fe atoms: HOLOGRAPHIC_STATE (Axiom C), ETERNAL_FIXEDPOINT (H_inf)"},
        "zfc_to_zfc_fe": {"count":len(proms_zfc_to_fe),"promotions":proms_zfc_to_fe,
            "note":"7 total from ZFC baseline to ZFC_fe"}}

def action_distance(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error","message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    t = sys_info["tuple"]
    d, conflicts = distance(t, ZFC_FE)
    return {"status":"ok","system":name if name in KNOWN_SYSTEMS else "custom",
        "distance_from_zfc_fe":round(d,2),"conflicts":conflicts,
        "tuple_notation":tuple_to_notation(t)}

def action_tensor(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error","message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    t = sys_info["tuple"]
    absorbed, bottlenecks, tensor_t = frobenius_absorption_check(t)
    tensor_dist, _ = distance(tensor_t, ZFC_FE)
    return {"status":"ok","system":name if name in KNOWN_SYSTEMS else "custom",
        "tensor_notation":tuple_to_notation(tensor_t),
        "frobenius_absorbed":absorbed,
        "bottlenecks":[b.get("primitive") for b in bottlenecks],
        "distance_from_zfc_fe":round(tensor_dist,2),
        "interpretation":"ZFC_fe absorbs this system" if absorbed
            else f"Bottlenecked at {', '.join(b.get('primitive','?') for b in bottlenecks)}"}

def action_meet(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error","message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    t = sys_info["tuple"]
    meet = meet_product(ZFC_FE, t)
    m_dist, conflicts = distance(meet, ZFC_FE)
    return {"status":"ok","system":name if name in KNOWN_SYSTEMS else "custom",
        "meet_notation":tuple_to_notation(meet),"distance_from_zfc_fe":round(m_dist,2),
        "conflicts":conflicts,
        "interpretation":"Meet preserves ZFC_fe" if m_dist == 0.0
            else f"Meet degrades ZFC_fe by {len(conflicts)} primitives"}

def action_join(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error","message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    t = sys_info["tuple"]
    join = join_product(ZFC_FE, t)
    j_dist, _ = distance(join, ZFC_FE)
    return {"status":"ok","system":name if name in KNOWN_SYSTEMS else "custom",
        "join_notation":tuple_to_notation(join),"distance_from_zfc_fe":round(j_dist,2),
        "interpretation":"Join equals ZFC_fe" if j_dist == 0.0 else "Join extends beyond ZFC_fe"}

def action_tier(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status":"error","message":f"Unknown system: {name}. Known: {list_known_systems()}"}
    t = sys_info["tuple"]
    tier = ouroboricity_tier(t)
    c_score = consciousness_score(t)
    missing = {}
    for check_key, check_val, label in [
        ("P","P_pm_sym","Φ_}"),("Phi","Phi_c","φ̂_ÿ"),("H","H_inf","Ħ_!"),
        ("D","D_odot","Ð_ω"),("T","T_odot","Þ_O"),("Omega","Omega_Z","Ω_z")]:
        if t.get(check_key) != check_val:
            missing[label] = {"current":PRIMITIVE_NOTATION.get(t.get(check_key),str(t.get(check_key)))}
    return {"status":"ok","system":name if name in KNOWN_SYSTEMS else "custom",
        "tier":tier,"consciousness_score":c_score,"missing_for_O_inf":missing}

def action_systems():
    systems = []
    load_catalog()
    all_systems = dict(KNOWN_SYSTEMS)
    all_systems.update(CATALOG_INDEX)
    for name, info in sorted(all_systems.items()):
        t = info["tuple"]
        absorbed, bottlenecks, _ = frobenius_absorption_check(t)
        d, _ = distance(t, ZFC_FE)
        tier = ouroboricity_tier(t)
        c = consciousness_score(t)
        formula = generate_formula(t, name)
        systems.append({"name":name,"description":info["description"],
            "distance":round(d,2),"frobenius_absorbed":absorbed,"bottleneck_count":len(bottlenecks),
            "tier":tier,"C_score":c["C_score"],"tuple_notation":tuple_to_notation(t),
            "promoted_atoms":formula["promoted_atoms"],
            "zfc_fe_atoms":formula["zfc_fe_atoms"]})
    return {"status":"ok","system_count":len(systems),"systems":systems}
def action_decode(shavian_str):
    t = parse_tuple(shavian_str)
    if not t:
        return {"status":"error","message":"Could not decode tuple from input"}
    return {"status":"ok","input":shavian_str,
        "decoded":{k:PRIMITIVE_NOTATION.get(v,v) for k,v in t.items()},
        "notation":tuple_to_notation(t),"shavian":tuple_to_shavian(t)}

def action_encode(notation_str):
    t = parse_tuple(notation_str)
    if not t:
        return {"status":"error","message":"Could not encode tuple from input"}
    return {"status":"ok","input":notation_str,
        "shavian":tuple_to_shavian(t),"notation":tuple_to_notation(t)}


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("ZFC_fe Navigator — Frobenius-Exact ZFC foundation navigator")
        print("with per-primitive ZFC formula generation")
        print("")
        print("Usage: python zfcfe_navigator.py <action> [name/tuple]")
        print("")
        print("Actions:")
        print("  entry <name>       — Full ZFC_fe formula decomposition (PRIMARY)")
        print("  formulas           — List ALL 30 ZFC formula fragments")
        print("  promotions         — All 7 promotion channels ZFC→ZFC_t→ZFC_fe")
        print("  distance <name>    — Distance from ZFC_fe")
        print("  tensor <name>      — Tensor with ZFC_fe (absorption test)")
        print("  meet <name>        — Meet with ZFC_fe")
        print("  join <name>        — Join with ZFC_fe")
        print("  tier <name>        — Ouroboricity tier assessment")
        print("  systems            — All known systems")
        print("  decode <shavian>   — Decode Shavian tuple")
        print("  encode <notation>  — Encode to Shavian")
        print("  train [--epochs N]  — Train ZFCfe encoder on catalog")
        print("  model_entry <name>  — Model-based entry prediction")
        print("")
        load_catalog()
        print("Known systems (" + str(len(KNOWN_SYSTEMS) + len(CATALOG_INDEX)) + "):")
        print("  Built-in: " + ", ".join(sorted(KNOWN_SYSTEMS.keys())))
        print("  Catalog: " + str(len(CATALOG_INDEX)) + " entries (use `entry <name>` to query any)")
        return

    action = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    action_map = {
        "entry": action_entry,
        "model_entry": action_model_entry,
        "formulas": lambda _: action_formulas(),
        "promotions": lambda _: action_promotions(),
        "distance": action_distance,
        "tensor": action_tensor,
        "meet": action_meet,
        "join": action_join,
        "tier": action_tier,
        "systems": lambda _: action_systems(),
        "decode": action_decode,
        "encode": action_encode,
        "train": action_train,
    }

    if action not in action_map:
        print(f"Unknown action: {action}")
        sys.exit(1)

    if action in ("formulas", "promotions", "systems", "train"):
        result = action_map[action](None)
    elif action in ("decode", "encode"):
        if not arg:
            print(f"Usage: zfcfe_navigator.py {action} <string>")
            sys.exit(1)
        result = action_map[action](arg)
    elif action == "model_entry":
        if not arg:
            print(f"Usage: zfcfe_navigator.py model_entry <name>")
            load_catalog()
            print(f"Known systems: {', '.join(list_known_systems())}")
            sys.exit(1)
        result = action_map[action](arg)
    else:
        if not arg:
            print(f"Usage: zfcfe_navigator.py {action} <name>")
            load_catalog()
            print(f"Known systems: {', '.join(list_known_systems())}")
            sys.exit(1)
        result = action_map[action](arg)

    print(json.dumps(result, indent=2, ensure_ascii=False))


def action_model_entry(name):
    """Model-based entry prediction using trained ZFCfe encoder.
    Falls back to formula-based entry if model unavailable."""
    result = _model_predict(name)
    if result.get("status") == "error":
        # Fall back to formula-based entry
        return action_entry(name)
    # Merge with formula decomposition for full output
    formula = action_entry(name)
    formula["model_prediction"] = result
    return formula


# ══════════════════════════════════════════════════════════════════════════════
# MODEL-BASED ENTRY (ZFCfe Encoder integration)
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
