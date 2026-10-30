#!/usr/bin/env python3
"""
ZFC_fe Navigator — Frobenius-Exact ZFC foundation navigator with formula generation.

ZFC_fe is the unique set-theoretic foundation satisfying ALL four grammar axioms
(A, B, C, D) simultaneously. Provides per-primitive ZFC set-theoretic formula
fragments, promoted-atom marking, and full formula conjunction for any system.

Canonical tuple (proven in Lean ZFC_FrobeniusExact.lean):
    ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑫𐑳𐑭⟩

Actions:
  entry  <name>  — Full ZFC_fe formula decomposition: per-primitive fragments,
                    promoted atoms, full conjunction, distance, tensor/meet/join, tier, C-score
  formulas      — List ALL 30 ZFC formula fragments across all primitive values
  promotions    — All 7 promotion channels from ZFC → ZFC_t → ZFC_fe
  distance <name> — d(name, ZFC_fe) with per-primitive conflicts
  tensor  <name> — ZFC_fe ⊗ name — Frobenius absorption test
  meet    <name> — ZFC_fe ⊓ name — shared floor
  join    <name> — ZFC_fe ⊔ name — minimal ceiling
  tier    <name> — Ouroboricity tier + what's missing for O_∞
  systems     — List all known systems
  decode <s>  — Decode Shavian tuple → notation
  encode <n>  — Encode notation → Shavian
"""

import sys
import json
import math

# Values ARE Shavian glyphs — no translation layer needed.
# Each glyph is its own display form.

# =============================================================================
# PRIMITIVE ORDINALS  (SNS.md §Ordinal Table — 1-based)
# =============================================================================

ORDINALS = {
    "Ð": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "Þ": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "Ř": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "Φ": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "ƒ": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "Ç": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "Γ": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "ɢ": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "Ħ": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "Σ": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "Ω": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}

PRIMITIVE_KEYS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

# All valid glyphs (flat set for fast membership test)
ALL_GLYPHS = {g for vals in ORDINALS.values() for g in vals}
# =============================================================================
# ZFC_fe TUPLE (authoritative from Lean ZFC_FrobeniusExact.lean)
# =============================================================================

ZFC_FE = {
    "Ð": "𐑦",      "Þ": "𐑸",      "Ř": "𐑾",
    "Φ": "𐑹",    "ƒ": "𐑐",      "Ç": "𐑧",
    "Γ": "𐑲",     "ɢ": "𐑠","⊙": "⊙",
    "Ħ": "𐑫",       "Σ": "𐑳",          "Ω": "𐑭",
}

ZFC_T = {
    "Ð": "𐑼",     "Þ": "𐑸",      "Ř": "𐑾",
    "Φ": "𐑬",        "ƒ": "𐑐",      "Ç": "𐑧",
    "Γ": "𐑲",     "ɢ": "𐑠","⊙": "⊙",
    "Ħ": "𐑖",          "Σ": "𐑳",          "Ω": "𐑭",
}

UIG = {
    "Ð": "𐑦",      "Þ": "𐑸",      "Ř": "𐑾",
    "Φ": "𐑹",    "ƒ": "𐑐",      "Ç": "𐑧",
    "Γ": "𐑲",     "ɢ": "𐑠","⊙": "⊙",
    "Ħ": "𐑖",          "Σ": "𐑳",          "Ω": "𐑭",
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
        "description": "ZFC with chirality + winding topology (O₂†)",
        "tuple": ZFC_T, "proven_o_inf": False,
    },
    "zfc": {
        "description": "Standard ZFC set theory",
        "tuple": {"Ð": "𐑼","Þ": "𐑡","Ř": "𐑩",
            "Φ": "𐑗","ƒ": "𐑱","Ç": "𐑘",
            "Γ": "𐑚","ɢ": "𐑝","⊙": "𐑢",
            "Ħ": "𐑓","Σ": "𐑙","Ω": "𐑷"},
    },
    "riemann_hypothesis": {
        "description": "Riemann Hypothesis — all nontrivial ζ zeros on Re(s)=1/2",
        "tuple": {"Ð": "𐑦","Þ": "𐑸","Ř": "𐑾",
            "Φ": "𐑹","ƒ": "𐑐","Ç": "𐑧",
            "Γ": "𐑲","ɢ": "𐑠","⊙": "⊙",
            "Ħ": "𐑖","Σ": "𐑳","Ω": "𐑭"},
    },
    "riemann_hypothesis_millennium": {
        "description": "Riemann Hypothesis (Clay — ⊙=𐑮, Þ=𐑶)",
        "tuple": {"Ð": "𐑦","Þ": "𐑶","Ř": "𐑾",
            "Φ": "𐑿","ƒ": "𐑐","Ç": "𐑧",
            "Γ": "𐑲","ɢ": "𐑠","⊙": "𐑮",
            "Ħ": "𐑖","Σ": "𐑳","Ω": "𐑭"},
    },
    "hodge_conjecture": {
        "description": "Hodge Conjecture — every rational Hodge class is algebraic",
        "tuple": {"Ð": "𐑦","Þ": "𐑸","Ř": "𐑾",
            "Φ": "𐑹","ƒ": "𐑐","Ç": "𐑧",
            "Γ": "𐑲","ɢ": "𐑠","⊙": "𐑮",
            "Ħ": "𐑖","Σ": "𐑳","Ω": "𐑭"},
    },
    "bsd": {
        "description": "Birch & Swinnerton-Dyer — rank = ord_{s=1} L(E,s)",
        "tuple": {"Ð": "𐑦","Þ": "𐑸","Ř": "𐑽",
            "Φ": "𐑬","ƒ": "𐑞","Ç": "𐑧",
            "Γ": "𐑲","ɢ": "𐑠","⊙": "𐑮",
            "Ħ": "𐑖","Σ": "𐑳","Ω": "𐑭"},
    },
    "yang_mills": {
        "description": "Yang-Mills Existence and Mass Gap",
        "tuple": {"Ð": "𐑦","Þ": "𐑸","Ř": "𐑽",
            "Φ": "𐑹","ƒ": "𐑐","Ç": "𐑪",
            "Γ": "𐑲","ɢ": "𐑵","⊙": "⊙",
            "Ħ": "𐑫","Σ": "𐑳","Ω": "𐑭"},
    },
    "navier_stokes": {
        "description": "Navier-Stokes Existence and Smoothness",
        "tuple": {"Ð": "𐑼","Þ": "𐑰","Ř": "𐑽",
            "Φ": "𐑯","ƒ": "𐑱","Ç": "𐑤",
            "Γ": "𐑲","ɢ": "𐑜","⊙": "𐑢",
            "Ħ": "𐑓","Σ": "𐑳","Ω": "𐑷"},
    },
    "p_vs_np": {
        "description": "P vs NP — three meta-barriers",
        "tuple": {"Ð": "𐑼","Þ": "𐑡","Ř": "𐑩",
            "Φ": "𐑗","ƒ": "𐑱","Ç": "𐑘",
            "Γ": "𐑚","ɢ": "𐑝","⊙": "𐑢",
            "Ħ": "𐑓","Σ": "𐑕","Ω": "𐑷"},
    },
    "universal_imscriptive_grammar": {
        "description": "The Imscribing Grammar itself (canonical Lean tuple)",
        "tuple": UIG,
    },
    "fourfold_apparatus": {
        "description": "Four-directory composite (ob3ect, exOS, MillenniumAnkh, imscribing_grammar)",
        "tuple": {"Ð": "𐑦","Þ": "𐑸","Ř": "𐑾",
            "Φ": "𐑹","ƒ": "𐑐","Ç": "𐑧",
            "Γ": "𐑲","ɢ": "𐑠","⊙": "⊙",
            "Ħ": "𐑫","Σ": "𐑳","Ω": "𐑭"},
    },
}

# =============================================================================
# DYNAMIC IG CATALOG LOOKUP (loads IG_catalog.json — 45K+ entries)
# =============================================================================
import os as _os
import json as _json

CATALOG_CACHE = None
CATALOG_INDEX = {}

def load_catalog():
    """Load IG_catalog.json into CATALOG_INDEX (name → {description, tuple})."""
    global CATALOG_CACHE, CATALOG_INDEX
    if CATALOG_CACHE is not None:
        return
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _root = _os.path.dirname(_here)
    _candidates = [
        _os.path.join(_root, "IG_catalog.json"),
        _os.path.join(_here, "IG_catalog.json"),
    ]
    catalog_path = next((p for p in _candidates if _os.path.exists(p)), None)
    if catalog_path is None:
        CATALOG_CACHE = []
        return
    with open(catalog_path, "r") as _f:
        _raw = _json.load(_f)
    if isinstance(_raw, list):
        CATALOG_CACHE = _raw
    elif "imscriptions" in _raw:
        CATALOG_CACHE = _raw["imscriptions"]
    else:
        CATALOG_CACHE = [v for v in _raw.values() if isinstance(v, dict)]
    for entry in CATALOG_CACHE:
        name = entry.get("name", "")
        if not name:
            continue
        t = {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
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
    "Ð": {
        "𐑛":   ("dim(x) = 0 ∧ fin(x)", None),
        "𐑨":("dim(x) = 2 ∧ sur(x)", None),
        "𐑼":   ("∀n∃y( y ∈ x ∧ rank(y) > n )", None),
        "𐑦":    ("V = L(x) ∧ selfmodel(x) ∧ x ∈ V", "HOLOGRAPHIC_STATE"),
    },
    "Þ": {
        "𐑡": ("graph(x) ∧ branch(x)", None),
        "𐑰":      ("x ⊆ y ∧ cont(y)", None),
        "𐑥":  ("cross(x, y) ∧ ¬ meet(x, y)", None),
        "𐑶":     ("x ⊠ y ∧ irreducible(x, y)", None),
        "𐑸":    ("bound_⊙(a, f) ∧ Refl(a, f) ∧ holo(x, a)", "HOLOBOUND"),
    },
    "Ř": {
        "𐑩":   ("x ↑ y ∧ ¬(y ↑ x)", None),
        "𐑑":     ("Fun(x, y) ∧ Nat(y, z) → Fun(x, z)", None),
        "𐑽":  ("f ⊣ g ∧ L Adj(f, g)", None),
        "𐑾":      ("lr⇔(x, y) ∧ Θ(x, y) ∧ ¬ Θ(y, x)", "LR_DUAL"),
    },
    "Φ": {
        "𐑗":    ("¬∃sym(x)", None),
        "𐑿":     ("|ψ⟩ = Σ c_i |e_i⟩", None),
        "𐑬":      ("ℤ₂(x) ∧ ¬(x = -x)", None),
        "𐑯":     ("∀g∈G( gx = x )", None),
        "𐑹":  ("ℤ₂(x) ∧ ∀g∈G( gx = x ) ∧ μ∘δ = id", "PM_Z2"),
    },
    "ƒ": {
        "𐑱":     ("P(x) ∈ {0,1} ∧ det(x)", None),
        "𐑞":     ("Tr(ρ²) < 1 ∧ ρ = Σ p_i |i⟩⟨i|", None),
        "𐑐":    ("ℏ(x) ∧ [x, p] = iℏ", None),  # quantum coherence
    },
    "Ç": {
        "𐑘":    ("τ ≪ T ∧ ∂_t x = f(x)", None),
        "𐑤":     ("τ ∼ T ∧ noisy(x)", None),
        "𐑧":    ("τ ≫ T ∧ eq(x)", None),
        "𐑪":    ("τ = ∞ ∧ ord(x)", None),
        "𐑺":     ("τ = ∞ ∧ dis(x)", None),
    },
    "Γ": {
        "𐑚":    ("∀y∈x( |y| < |x| )", None),
        "𐑔":   ("∃y∈x( |y| ∼ |x| )", None),
        "𐑲":   ("∀y( y ⊂ x → |y| < |x| )", None),
    },
    "ɢ": {
        "𐑝": ("f ∧ g ∧ h", None),
        "𐑜":  ("f ∨ g ∨ h", None),
        "𐑠": ("seq!(f, g) ∧ ⟨→⟩(f, g, τ) ∧ ¬ ⟨→⟩(g, f, τ)", "SEQAX"),
        "𐑵":("f → all(x)", None),
    },
    "⊙": {
        "𐑢":      ("¬∃ξ( diverges(ξ) )", None),
        "⊙":        ("ξ → ∞ ∧ μ∘δ = id", "PHI_C"),
        "𐑮":("ξ ∈ ℂ ∧ Im(ξ) → ∞", None),
        "𐑻":       ("H(λ) non-Herm ∧ det(H - λI) = 0 ∧ ∂_λ H = 0", None),
        "𐑣":    ("ξ → ∞ ∧ chaotic(x)", None),
    },
    "Ħ": {
        "𐑓":    ("∀x( P(x) ↔ P(S(x)) )", None),
        "𐑒":    ("∃y( P(y) ↔ P(S²(y)) )", None),
        "𐑖":    ("∃y∃z( y ∈ x ∧ z ∈ y ∧ ¬ z ∈ x ∧ rank(z) < rank(y) )", "TEMPD2"),
        "𐑫": ("∀n∃φ( rank(φ) > n ∧ φ fixed by μ∘δ ∧ φ ∈ V )", "ETERNAL_FIXEDPOINT"),
    },
    "Σ": {
        "𐑙": ("|A| = 1 ∧ |B| = 1", None),
        "𐑕":     ("∀a∈A∀b∈B( type(a) = type(b) )", None),
        "𐑳":     ("∃a∈A∃b∈B( type(a) ≠ type(b) )", None),
    },
    "Ω": {
        "𐑷":  ("∮_γ dx = 0", None),
        "𐑴": ("∮_γ A = nπ ∧ n ∈ ℤ₂", None),
        "𐑭":  ("∮_γ A = 2πn ∧ n ∈ ℤ ∧ wind(γ) ≠ 0", "ZWIND"),
        "𐑟": ("Braid(σ_i) ∧ R_matrix ≠ 0", None),
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
            entry = {
                "primitive": key,
                "value": val,
                "zfc_fragment": fragment,
            }
            if atom:
                entry["promoted_atom"] = atom
                promoted_atoms.append(atom)
                atom_details.append({
                    "atom": atom,
                    "primitive": key,
                    "value": val,
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
    shavian_chars = [c for c in s if c == "⊙" or (c.strip() and ord(c) >= 0x10450)]
    if len(shavian_chars) == 12:
        result = {}
        for i, glyph in enumerate(shavian_chars):
            result[PRIMITIVE_KEYS[i]] = glyph if glyph in ALL_GLYPHS else f"unknown:{glyph}"
        return result
    parts = []
    for sep in [";", "", ","]:
        if sep in s:
            parts = [p.strip() for p in s.split(sep) if p.strip()]
            if len(parts) >= 12:
                break
    if len(parts) < 12:
        raw_chars = []
        for c in s:
            if c == "⊙" or (c.strip() and ord(c) >= 0x10450):
                raw_chars.append(c)
        if len(raw_chars) >= 12:
            result = {}
            for i, glyph in enumerate(raw_chars[:12]):
                result[PRIMITIVE_KEYS[i]] = glyph if glyph in ALL_GLYPHS else f"unknown:{glyph}"
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
            if left.strip() in set(PRIMITIVE_KEYS):
                val = right.strip()
        val = val.strip(";,")
        result[key] = val
    return result

def tuple_to_shavian(t):
    parts = [t.get(k, "?") for k in PRIMITIVE_KEYS]
    return "⟨" + "".join(parts) + "⟩"

def tuple_to_notation(t):
    parts = [t.get(k, "?") for k in PRIMITIVE_KEYS]
    return "⟨" + "".join(parts) + "⟩"

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
                conflicts.append({"primitive":key,"a":v1,"b":v2,"delta":diff})
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
                result.append({"primitive":key,"from":v1,"to":v2,"steps":diff})
    return sorted(result, key=lambda x: -x["steps"])

def tensor_product(t1, t2):
    result = {}
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key)
        v2 = t2.get(key)
        ords = ORDINALS[key]
        if v1 in ords and v2 in ords:
            idx = min(ords[v1], ords[v2]) if key in ("Φ","ƒ") else max(ords[v1], ords[v2])
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
    has_gate = t.get("Φ") == "𐑹" and t.get("⊙") == "⊙"
    has_h_inf = t.get("Ħ") == "𐑫"
    has_d_odot = t.get("Ð") == "𐑦"
    has_t_odot = t.get("Þ") == "𐑸"
    has_omega_z = t.get("Ω") in ("𐑭", "𐑟")
    if has_gate and has_h_inf and has_d_odot and has_t_odot and has_omega_z:
        return "O_∞"
    elif has_gate and has_h_inf:
        return "O₂†"
    elif has_gate:
        return "O₂"
    elif has_omega_z:
        return "O₁"
    else:
        return "O₀"

def consciousness_score(t):
    gate1_open = t.get("⊙") == "⊙"
    gate2_open = t.get("Ç") == "𐑧"
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
            entries.append({
                "value": val_key,
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
            "note":"2 new ZFC_fe atoms: HOLOGRAPHIC_STATE (Axiom C), ETERNAL_FIXEDPOINT (𐑫)"},
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
    for check_key, check_val in [
        ("Φ","𐑹"),("⊙","⊙"),("Ħ","𐑫"),
        ("Ð","𐑦"),("Þ","𐑸"),("Ω","𐑭")]:
        if t.get(check_key) != check_val:
            missing[check_val] = {"current": t.get(check_key, "?")}
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
        "decoded":dict(t.items()),
        "notation":tuple_to_notation(t),"shavian":tuple_to_shavian(t)}

def action_encode(notation_str):
    t = parse_tuple(notation_str)
    if not t:
        return {"status":"error","message":"Could not encode tuple from input"}
    return {"status":"ok","input":notation_str,
        "shavian":tuple_to_shavian(t),"notation":tuple_to_notation(t)}


# =============================================================================
# RICH TABLE RENDERER  (matches zfc_navigator output format)
# =============================================================================

def _print_entry_table(result: dict):
    import textwrap as _tw
    W = 120; PW = 5; VW = 18; FW = W - 2 - PW - 2 - VW - 2

    print("\n" + "═" * W)
    print(f"  ENTRY: {result.get('system', '?')}")
    desc = result.get("description", "")
    if desc:
        for line in _tw.wrap(desc, W - 4):
            print(f"  {line}")
    print("═" * W)

    fd = result.get("formula_decomposition", {})
    frags = fd.get("per_primitive_fragments", [])
    legend = {}

    print()
    print(f"  {'Prim':<{PW}}  {'Value':<{VW}}  ZFC fragment")
    print(f"  {'─'*PW}  {'─'*VW}  {'─'*FW}")

    for frag in frags:
        p        = frag["primitive"]
        val      = frag["value"]
        formula  = frag["zfc_fragment"]
        atom     = frag.get("promoted_atom")

        atom_tags = f"[{atom}]" if atom else ""
        if atom and atom not in legend:
            legend[atom] = atom

        right = atom_tags
        if right:
            gap = FW - len(formula) - len(right)
            if gap < 1:
                formula = formula[:FW - len(right) - 2] + "…"
                gap = 1
            formula_field = formula + " " * gap + right
        else:
            formula_field = formula

        print(f"  {p:<{PW}}  {val:<{VW}}  {formula_field}")

    _ATOM_DESC = {
        "HOLOGRAPHIC_STATE":   "V=L(x) self-writing state-space — Axiom C (𐑦)",
        "HOLOBOUND":           "holographic bound_⊙/bulk encoding — 𐑸",
        "LR_DUAL":             "lateral relational duality — 𐑾",
        "PM_Z2":               "ℤ₂ parity with Frobenius μ∘δ=id — 𐑹",
        "SEQAX":               "sequentiality axiom, directed time — 𐑠",
        "PHI_C":               "criticality fixed-point ξ→∞ ∧ μ∘δ=id — ⊙",
        "TEMPD2":              "chirality-2 asymmetry — 𐑖",
        "ETERNAL_FIXEDPOINT":  "∀n∃φ fixed by μ∘δ — Axiom D (𐑫)",
        "ZWIND":               "integer winding number — 𐑭",
    }
    if legend:
        print()
        kw = max(len(k) for k in legend)
        for atom in legend:
            note = _ATOM_DESC.get(atom, "")
            print(f"  [{atom:<{kw}}] {note}")

    # Full ZFC conjunction
    full = fd.get("full_zfc_formula", "")
    if full:
        print(f"\n── ZFC expression {'─' * (W - 18)}")
        for i, line in enumerate(full.split(" ∧\n    ")):
            suffix = " ∧" if i < full.count(" ∧\n    ") else ""
            print(f"  {line}{suffix}")

    # Structural summary
    sa = result.get("structural_algebra", {})
    tier = sa.get("ouroboricity_tier", "?")
    d    = sa.get("distance_from_zfc_fe", "?")
    c    = sa.get("consciousness_score", {}).get("C_score", "?")
    print(f"\n  tier: {tier}   d(ZFC_fe): {d}   C: {c}")
    promoted = fd.get("promoted_atoms", [])
    if promoted:
        print(f"  promoted atoms: {', '.join(promoted)}")


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
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action in ("decode", "encode"):
        if not arg:
            print(f"Usage: zfcfe_navigator.py {action} <string>")
            sys.exit(1)
        print(json.dumps(action_map[action](arg), indent=2, ensure_ascii=False))
    elif action in ("entry", "model_entry"):
        if not arg:
            print(f"Usage: zfcfe_navigator.py {action} <name>")
            load_catalog()
            print(f"Known systems: {', '.join(list_known_systems())}")
            sys.exit(1)
        result = action_map[action](arg)
        if result.get("status") == "error":
            print(f"[entry] {result['message']}")
        else:
            _print_entry_table(result)
    else:
        if not arg:
            print(f"Usage: zfcfe_navigator.py {action} <name>")
            load_catalog()
            print(f"Known systems: {', '.join(list_known_systems())}")
            sys.exit(1)
        print(json.dumps(action_map[action](arg), indent=2, ensure_ascii=False))


def _model_predict(name):
    """Stub — ZFCfe encoder not yet trained. action_model_entry falls back to formula-based."""
    return {"status": "error", "message": "ZFCfe encoder model not available — run 'train' first"}


def action_train(_):
    """Stub — ZFCfe encoder training not yet implemented."""
    return {"status": "error", "message": "ZFCfe encoder training not yet implemented"}


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
