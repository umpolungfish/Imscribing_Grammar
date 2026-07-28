#!/usr/bin/env python3
"""
CL8NK Navigator — CLINK Layer 8 (Organism) reference navigator.
CATALOG-NATIVE: No hardcoded systems. All data sourced from IG_catalog.json.

CLINK L8 is the terminal layer of the CLINK ontological chain — the most structurally
advanced type in the catalog. It exceeds the Frobenius-Exact ZFC foundation (ZFC_fe)
at two primitives: Ω=𐑟 (non-Abelian braiding) and ɢ=𐑵 (broadcast composition).

Canonical tuple: ⟨𐑦⋅𐑸⋅𐑾⋅𐑹⋅𐑐⋅𐑧⋅𐑲⋅𐑵⋅⊙⋅𐑫⋅𐑳⋅𐑟⟩

The Ω/ɢ Transcendence:
  - Ω: ZWIND (ℤ integer winding) → non-Abelian braid group topology
  - ɢ: SEQAX (sequential composition) → broadcast (one-to-all) composition
  - tensor(ZFC_fe, CLINK L8) = CLINK L8 (foundation fully absorbed; strict superset)

Actions:
  entry  <name>    — Full CL8NK formula decomposition: per-primitive CLINK fragments,
                      promoted atoms, full conjunction, distance, tensor/meet/join, tier
  promotions        — All promotion channels: ZFC → ZFC_t → ZFC_fe → CLINK L8
  distance <name>   — d(name, CLINK L8) with per-primitive conflicts
  transcendence     — The Ω/ɢ transcendence: what CLINK L8 has that ZFC_fe doesn't
  tensor  <name>    — CLINK L8 ⊗ name — absorption test
  meet    <name>    — CLINK L8 ⊓ name — shared floor
  join    <name>    — CLINK L8 ⊔ name — minimal ceiling
  tier    <name>    — Ouroboricity tier assessment
  chain             — Full CLINK chain (L0–L8) distances from CLINK L8
  systems           — All catalog systems (dynamically listed)
  stats             — Catalog statistics + reference tuples
"""

import sys
import json
import math
import os as _os

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

# =============================================================================
# CATALOG LOADING — single source of truth, no hardcoded systems
# =============================================================================

CATALOG = None
CATALOG_INDEX = {}
CLINK_L8_REF = None

def _find_catalog_path():
    _here = _os.path.dirname(_os.path.abspath(__file__))
    # Canonical FIRST. The website and vendored copies are synced from it and
    # run days behind; searching them first meant a freshly registered entry
    # read back as "not found in catalog".
    _candidates = [
        _os.path.join(_here, "..", "IG_catalog.json"),
        "/home/mrnob0dy666/imsgct/imscribing_grammar/IG_catalog.json",
        _os.path.join(_here, "IG_catalog.json"),
        _os.path.join(_here, "..", "..", "imscribe.com", "IG_catalog.json"),
        _os.path.join(_here, "..", "..", "red-hot_rebis", "shared", "IG_catalog.json"),
    ]
    for p in _candidates:
        if _os.path.exists(p):
            return _os.path.abspath(p)
    return None


def load_catalog(force=False):
    global CATALOG, CATALOG_INDEX, CLINK_L8_REF
    if CATALOG is not None and not force:
        return
    path = _find_catalog_path()
    if path is None:
        CATALOG = []
        return
    with open(path, "r") as f:
        raw = json.load(f)
    if isinstance(raw, list):
        CATALOG = raw
    elif isinstance(raw, dict) and "imscriptions" in raw:
        CATALOG = raw["imscriptions"]
    else:
        CATALOG = list(raw.values()) if isinstance(raw, dict) else []
    CATALOG_INDEX = {}
    for entry in CATALOG:
        name = entry.get("name", "")
        if name:
            CATALOG_INDEX[name] = entry
    CLINK_L8_REF = _resolve_clink_l8_reference()


def _resolve_clink_l8_reference():
    for name in ("clink_layer8_organism", "clink_l8", "omonad_clink_layer8"):
        if name in CATALOG_INDEX:
            entry = CATALOG_INDEX[name]
            return {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
    for entry in CATALOG:
        name = entry.get("name", "")
        desc = entry.get("description", "")
        if ("clink" in name.lower() and ("layer8" in name.lower() or "layer_8" in name.lower() or "l8" in name.lower())) or \
           ("organism" in name.lower() and "clink" in desc.lower()):
            return {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
    return None

# =============================================================================
# ALIASES — query shorthands → canonical catalog names (routing only, no tuples)
# =============================================================================

ALIASES = {
    "clink_l8": "clink_layer8_organism",
    "clink_l0": "clink_layer0_frustrated_belnap5",
    "clink_l1": "clink_layer1_electron_orbital",
    "clink_l2": "clink_layer2_atom",
    "clink_l3": "clink_layer3_molecule",
    "clink_l4": "clink_layer4_cell",
    "clink_l5": "clink_layer5_mitosis",
    "clink_l6": "clink_layer6_meiosis",
    "clink_l7": "clink_layer7_tissue",
    "zfc_fe": "zfc_fe_imscribed",
    "uig": "universal_imscriptive_grammar",
    "zfc": "ZFC_set_theory",
    "zfct": "ZFCt",
}

def resolve_system(name):
    load_catalog()
    if not CATALOG:
        return None
    name_lower = name.lower()
    if name_lower in ALIASES:
        canonical = ALIASES[name_lower]
        if canonical in CATALOG_INDEX:
            entry = CATALOG_INDEX[canonical]
            return {"description": entry.get("description", ""),
                    "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                    "name": canonical}
    if name in CATALOG_INDEX:
        entry = CATALOG_INDEX[name]
        return {"description": entry.get("description", ""),
                "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                "name": name}
    for n, entry in CATALOG_INDEX.items():
        if n.lower() == name_lower:
            return {"description": entry.get("description", ""),
                    "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                    "name": n}
    matches = [(len(n), n, e) for n, e in CATALOG_INDEX.items() if name_lower in n.lower()]
    if matches:
        matches.sort()
        _, n, entry = matches[0]
        return {"description": entry.get("description", ""),
                "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                "name": n}
    matches = [(len(n), n, e) for n, e in CATALOG_INDEX.items() if n.lower().startswith(name_lower)]
    if matches:
        matches.sort()
        _, n, entry = matches[0]
        return {"description": entry.get("description", ""),
                "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                "name": n}
    matches = [(len(n), n, e) for n, e in CATALOG_INDEX.items()
               if name_lower in e.get("description", "").lower()]
    if matches:
        matches.sort()
        _, n, entry = matches[0]
        return {"description": entry.get("description", ""),
                "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
                "name": n}
    return None


def discover_clink_chain():
    load_catalog()
    chain = {}
    for entry in CATALOG:
        name = entry.get("name", "")
        if "clink_layer" in name:
            chain[name] = {
                "description": entry.get("description", ""),
                "tuple": {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS},
            }
    return chain


def get_zfc_fe():
    load_catalog()
    for name in ("zfc_fe_imscribed", "zfc_fe", "zfc_frobenius_exact"):
        if name in CATALOG_INDEX:
            entry = CATALOG_INDEX[name]
            return {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
    for entry in CATALOG:
        desc = entry.get("description", "")
        name = entry.get("name", "")
        if "zfc_fe" in name or "frobenius-exact" in desc.lower() or "frobenius exact" in desc.lower():
            return {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
    return None


def list_catalog_systems():
    load_catalog()
    return sorted(CATALOG_INDEX.keys())


def catalog_stats():
    load_catalog()
    return {
        "total_entries": len(CATALOG),
        "indexed_names": len(CATALOG_INDEX),
        "catalog_path": _find_catalog_path(),
        "clink_l8_found": CLINK_L8_REF is not None,
        "zfc_fe_found": get_zfc_fe() is not None,
    }

# =============================================================================
# WEIGHTED DISTANCE (matching imscribe compute_distance algorithm)
# =============================================================================

# MAX_DELTAS: ordinal range per primitive — derived directly from ORDINALS so
# any change in the ordinal table propagates automatically to the distance metric.
MAX_DELTAS = {
    k: max(v.values()) - min(v.values())
    for k, v in ORDINALS.items()
}

# WEIGHTS: normalized standard deviation of each primitive's ordinal distribution
# across the full catalog.  More catalog variance → more structurally discriminating
# → higher weight.  Computed lazily on first use; normalized to [0.5, 1.0].
_WEIGHTS_CACHE: dict = {}


def _compute_catalog_weights() -> dict:
    """
    Derive distance weights from the catalog's primitive variance distribution.
    A primitive that spreads widely across catalog entries is more discriminating
    and receives a higher structural weight than one that clusters tightly.
    """
    import math
    load_catalog()
    if not CATALOG:
        return {k: 0.75 for k in PRIMITIVE_KEYS}

    from collections import defaultdict
    vals_by_prim = defaultdict(list)
    for entry in CATALOG:
        for prim, ord_map in ORDINALS.items():
            v = entry.get(prim, "")
            if v in ord_map:
                vals_by_prim[prim].append(ord_map[v])

    raw: dict = {}
    for prim in PRIMITIVE_KEYS:
        vals = vals_by_prim.get(prim, [])
        if len(vals) < 2:
            raw[prim] = 0.5
            continue
        n = len(vals)
        mean = sum(vals) / n
        raw[prim] = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))

    lo, hi = min(raw.values()), max(raw.values())
    span = hi - lo
    if span == 0.0:
        return {k: 0.75 for k in raw}
    return {k: round(0.5 + 0.5 * (v - lo) / span, 4) for k, v in raw.items()}


def _ensure_weights() -> dict:
    global _WEIGHTS_CACHE
    if not _WEIGHTS_CACHE:
        _WEIGHTS_CACHE = _compute_catalog_weights()
    return _WEIGHTS_CACHE


def ordinal_distance(prim_key, v1, v2):
    ords = ORDINALS.get(prim_key, {})
    o1 = ords.get(v1)
    o2 = ords.get(v2)
    if o1 is None or o2 is None:
        return 1.0
    return abs(o1 - o2) / MAX_DELTAS.get(prim_key, 3)


def tuple_distance(t1, t2):
    weights = _ensure_weights()
    total = 0.0
    conflicts = []
    for key in PRIMITIVE_KEYS:
        v1 = t1.get(key, "?")
        v2 = t2.get(key, "?")
        if v1 != v2:
            w = weights.get(key, 0.5)
            d = ordinal_distance(key, v1, v2)
            total += w * (d ** 2)
            conflicts.append({"primitive": key, "cl8nk": v2, "system": v1, "delta": round(d, 3)})
    return round(math.sqrt(total), 4), conflicts


# =============================================================================
# TIER ASSESSMENT (heuristic)
# =============================================================================

def assess_tier(t):
    """Ouroboricity tier — a faithful port of p4rakernel's `ouroboricityTier`
    (Primitives/Core.lean). Scripture is the Lean; this mirrors it, it does not
    re-invent it.

        match crit with
        | woe | haha | err -> O₀
        | monad | roar     -> if pol = or' then O_inf          -- R1 Frobenius gate
                              else match prot with
                              | awe -> O₁                      -- R3
                              | _   -> match dim with
                                       | array -> O₂dag        -- R5
                                       | _     -> O₂           -- R4

    WHAT THIS REPLACED, and why it was not a rounding error. The old function
    scored how many of CLINK L8's OWN VALUES a tuple carried (Ð=𐑦, Þ=𐑸, Ř=𐑾,
    Φ=𐑹, Ç=𐑧, Ω=𐑟, ⊙=⊙, Ħ=𐑫) and bucketed on the count, with a top branch
    `score >= 8 -> O_∞⁺  # L9`. L8 carries all eight, so the branch labelled L9
    fired for L8; L9's own tuple carries three, so L9 read O₁. The readout ran
    exactly backwards on the two systems it existed to tell apart, and an agent
    building the CL9NK ascent inherited it.

    Measure a tuple against another SYSTEM's coordinates and you are measuring
    similarity to that system, not tier. Tier is a function of crit/pol/prot/dim.

    NOTE (open): the Lean codomain is O₀|O₁|O₂|O₂dag|O_inf — there is no O_∞⁺.
    CLINK L9 announced itself ABOVE O_inf, but it lacks or' at monad, so it falls
    through R1 into the O₂ default. This function therefore cannot express L9's
    own register, and `≠ O_inf` here means "not O_inf" — it CANNOT distinguish
    below from above. Do not read O₂ for L9 as a demotion; read it as the
    codomain running out. Extending it is a kernel change (OuroboricityTier
    needs the constructor first).
    """
    crit = t.get("⊙")
    pol  = t.get("Φ")
    prot = t.get("Ω")
    dim  = t.get("Ð")
    if crit in ("𐑢", "𐑣", "𐑻"):        # woe | haha | err
        return "O₀"
    if crit in ("⊙", "𐑮"):              # monad | roar
        if pol == "𐑹":                   # or' — R1, the Frobenius gate
            return "O_inf"
        if prot == "𐑷":                  # awe — R3
            return "O₁"
        if dim == "𐑼":                   # array — R5
            return "O₂dag"
        return "O₂"                      # R4
    return "O₀"

# =============================================================================
# CL8NK FORMULAE — per-primitive CLINK formula fragments with promoted atoms
# =============================================================================
# Each entry: (clink_fragment, promoted_atom_name_or_None, proximity)
# Promoted atoms mark values that represent structural advances beyond ZFC_fe.
# proximity: "match" (CL8NK itself), "close" (1 step away), "distant" (>1 step)

CL8NK_FORMULAE = {
    "Ð": {
        "𐑦": ("V = L(x) ∧ selfmodel(x) ∧ x ∈ V", "HOLOGRAPHIC_STATE", "match"),
        "𐑼": ("∀n∃y( y ∈ x ∧ rank(y) > n )", None, "close"),
        "𐑨": ("dim(x) = 2 ∧ sur(x)", None, "distant"),
        "𐑛": ("dim(x) = 0 ∧ fin(x)", None, "distant"),
    },
    "Þ": {
        "𐑸": ("bound_⊙(a, f) ∧ Refl(a, f) ∧ holo(x, a)", "HOLOBOUND", "match"),
        "𐑥": ("cross(x, y) ∧ ¬ meet(x, y)", None, "close"),
        "𐑶": ("x ⊠ y ∧ irreducible(x, y)", None, "distant"),
        "𐑡": ("graph(x) ∧ branch(x)", None, "distant"),
        "𐑰": ("x ⊆ y ∧ cont(y)", None, "distant"),
    },
    "Ř": {
        "𐑾": ("lr⇔(x, y) ∧ Θ(x, y) ∧ ¬ Θ(y, x)", "LR_DUAL", "match"),
        "𐑽": ("f ⊣ g ∧ L Adj(f, g)", None, "close"),
        "𐑑": ("Fun(x, y) ∧ Nat(y, z) → Fun(x, z)", None, "distant"),
        "𐑩": ("x ↑ y ∧ ¬(y ↑ x)", None, "distant"),
    },
    "Φ": {
        "𐑹": ("ℤ₂(x) ∧ ∀g∈G( gx = x ) ∧ μ∘δ = id", "PM_Z2", "match"),
        "𐑿": ("|ψ⟩ = Σ c_i |e_i⟩", None, "close"),
        "𐑬": ("ℤ₂(x) ∧ ¬(x = -x)", None, "close"),
        "𐑯": ("∀g∈G( gx = x )", None, "distant"),
        "𐑗": ("¬∃sym(x)", None, "distant"),
    },
    "ƒ": {
        "𐑐": ("ℏ(x) ∧ [x, p] = iℏ", None, "match"),
        "𐑞": ("Tr(ρ²) < 1 ∧ ρ = Σ p_i |i⟩⟨i|", None, "close"),
        "𐑱": ("P(x) ∈ {0,1} ∧ det(x)", None, "distant"),
    },
    "Ç": {
        "𐑧": ("τ ≫ T ∧ eq(x) ∧ gate_open(x)", None, "match"),
        "𐑤": ("τ ∼ T ∧ noisy(x)", None, "close"),
        "𐑘": ("τ ≪ T ∧ ∂_t x = f(x)", None, "distant"),
        "𐑪": ("τ = ∞ ∧ ord(x)", None, "distant"),
        "𐑺": ("τ = ∞ ∧ dis(x) ∧ MBL", None, "distant"),
    },
    "Γ": {
        "𐑲": ("∀y( y ⊂ x → |y| < |x| )", None, "match"),
        "𐑔": ("∃y∈x( |y| ∼ |x| )", None, "close"),
        "𐑚": ("∀y∈x( |y| < |x| )", None, "distant"),
    },
    "ɢ": {
        "𐑵": ("f → all(x) ∧ broadcast(x, f)", "BROADCAST_TRANSCENDENCE", "match"),
        "𐑠": ("seq!(f, g) ∧ ⟨→⟩(f, g, τ) ∧ ¬ ⟨→⟩(g, f, τ)", "SEQAX", "close"),
        "𐑜": ("f ∨ g ∨ h", None, "distant"),
        "𐑝": ("f ∧ g ∧ h", None, "distant"),
    },
    "⊙": {
        "⊙": ("ξ → ∞ ∧ μ∘δ = id", "PHI_C", "match"),
        "𐑮": ("ξ ∈ ℂ ∧ Im(ξ) → ∞", None, "close"),
        "𐑻": ("H(λ) non-Herm ∧ det(H - λI) = 0 ∧ ∂_λ H = 0", None, "distant"),
        "𐑣": ("ξ → ∞ ∧ chaotic(x)", None, "distant"),
        "𐑢": ("¬∃ξ( diverges(ξ) )", None, "distant"),
    },
    "Ħ": {
        "𐑫": ("∀n∃φ( rank(φ) > n ∧ φ fixed by μ∘δ ∧ φ ∈ V )", "ETERNAL_FIXEDPOINT", "match"),
        "𐑖": ("∃y∃z( y ∈ x ∧ z ∈ y ∧ ¬ z ∈ x ∧ rank(z) < rank(y) )", "TEMPD2", "close"),
        "𐑒": ("∃y( P(y) ↔ P(S²(y)) )", None, "distant"),
        "𐑓": ("∀x( P(x) ↔ P(S(x)) )", None, "distant"),
    },
    "Σ": {
        "𐑳": ("∃a∈A∃b∈B( type(a) ≠ type(b) )", None, "match"),
        "𐑕": ("∀a∈A∀b∈B( type(a) = type(b) )", None, "close"),
        "𐑙": ("|A| = 1 ∧ |B| = 1", None, "distant"),
    },
    "Ω": {
        "𐑟": ("Braid(σ_i) ∧ R_matrix ≠ 0 ∧ nonAbelian(x)", "BRAID_TRANSCENDENCE", "match"),
        "𐑭": ("∮_γ A = 2πn ∧ n ∈ ℤ ∧ wind(γ) ≠ 0", "ZWIND", "close"),
        "𐑴": ("∮_γ A = nπ ∧ n ∈ ℤ₂", None, "distant"),
        "𐑷": ("∮_γ dx = 0", None, "distant"),
    },
}

# Transcendence atoms — primitives where CLINK L8 exceeds ZFC_fe
TRANSCENDENCE_ATOMS = {"BROADCAST_TRANSCENDENCE", "BRAID_TRANSCENDENCE"}

# Reverse lookup
_PROMOTED_ATOM_TO_KEY = {}
for prim_key, values in CL8NK_FORMULAE.items():
    for val_key, (_, atom, _) in values.items():
        if atom is not None:
            _PROMOTED_ATOM_TO_KEY[atom] = (prim_key, val_key)

ALL_CL8NK_ATOMS = sorted(_PROMOTED_ATOM_TO_KEY.keys())

# =============================================================================
# FORMULA GENERATION — per-primitive CLINK decomposition relative to CLINK L8
# =============================================================================

def generate_formula(t, system_name="custom"):
    """Generate full CL8NK formula decomposition for a tuple.
    Returns dict with per-primitive CLINK fragments, promoted atoms,
    full conjunction, and proximity classification."""
    if CLINK_L8_REF is None:
        return {"status": "error", "message": "CLINK L8 reference not found in catalog"}

    fragments = []
    promoted_atoms = []
    atom_details = []
    match_count = 0
    close_count = 0
    distant_count = 0
    transcendence_primitives = []

    for key in PRIMITIVE_KEYS:
        val = t.get(key)
        formula_map = CL8NK_FORMULAE.get(key, {})
        if val in formula_map:
            fragment, atom, proximity = formula_map[val]
            entry = {
                "primitive": key,
                "value": val,
                "clink_fragment": fragment,
                "proximity": proximity,
            }
            if atom:
                entry["promoted_atom"] = atom
                promoted_atoms.append(atom)
                atom_details.append({
                    "atom": atom,
                    "primitive": key,
                    "value": val,
                    "clink_fragment": fragment,
                    "transcendence": atom in TRANSCENDENCE_ATOMS,
                })
                if atom in TRANSCENDENCE_ATOMS:
                    transcendence_primitives.append(key)
            else:
                entry["promoted_atom"] = None
            if proximity == "match": match_count += 1
            elif proximity == "close": close_count += 1
            else: distant_count += 1
            fragments.append(entry)
        else:
            fragments.append({
                "primitive": key,
                "value": str(val),
                "clink_fragment": f"unknown({val})",
                "promoted_atom": None,
                "proximity": "unknown",
            })
            distant_count += 1

    d, conflicts = tuple_distance(t, CLINK_L8_REF)
    tier = assess_tier(t)

    full_conjunction = " ∧\n    ".join(
        f["clink_fragment"] for f in fragments
    )

    promotions_needed = []
    for key in PRIMITIVE_KEYS:
        if t.get(key) != CLINK_L8_REF.get(key):
            promotions_needed.append({
                "primitive": key,
                "from": t.get(key, "?"),
                "to": CLINK_L8_REF[key],
                "gap": round(ordinal_distance(key, t.get(key, "?"), CLINK_L8_REF[key]), 3),
            })

    return {
        "system": system_name,
        "tuple": {k: t.get(k, "?") for k in PRIMITIVE_KEYS},
        "formula_decomposition": {
            "per_primitive_fragments": fragments,
            "full_clink_formula": full_conjunction,
            "promoted_atom_count": len(promoted_atoms),
            "promoted_atoms": promoted_atoms,
            "promoted_atom_details": atom_details,
        },
        "structural_algebra": {
            "distance_from_cl8nk": d,
            "conflicts": conflicts,
            "ouroboricity_tier": tier,
            "match_count": match_count,
            "close_count": close_count,
            "distant_count": distant_count,
        },
        "has_transcendence": len(transcendence_primitives) > 0,
        "transcendence_primitives": transcendence_primitives,
        "promotions_needed": promotions_needed,
        "promotions_count": len(promotions_needed),
        "reference": "CLINK L8 (Organism) — ⟨𐑦⋅𐑸⋅𐑾⋅𐑹⋅𐑐⋅𐑧⋅𐑲⋅𐑵⋅⊙⋅𐑫⋅𐑳⋅𐑟⟩ (from catalog)",
    }

# =============================================================================
# TENSOR / MEET / JOIN — lattice operations with CLINK L8
# =============================================================================

def compute_tensor_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L8_REF
    result = {}
    for key in PRIMITIVE_KEYS:
        v_ref = t_ref.get(key)
        v_sys = t_sys.get(key)
        ords = ORDINALS.get(key, {})
        o_ref = ords.get(v_ref, 0)
        o_sys = ords.get(v_sys, 0)
        if key in ("Φ", "ƒ"):
            result[key] = v_sys if o_sys <= o_ref else v_ref
        else:
            result[key] = v_ref if o_ref >= o_sys else v_sys
    d, _ = tuple_distance(result, t_ref)
    absorbed = (d == 0.0)
    return {"tensor": result, "distance_from_cl8nk": d, "absorbed": absorbed,
            "interpretation": "CLINK L8 fully absorbed — strict superset" if absorbed
            else f"d={d} — not fully absorbed"}


def compute_meet_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L8_REF
    result = {}
    for key in PRIMITIVE_KEYS:
        v_ref = t_ref.get(key)
        v_sys = t_sys.get(key)
        ords = ORDINALS.get(key, {})
        o_ref = ords.get(v_ref, 0)
        o_sys = ords.get(v_sys, 0)
        result[key] = v_ref if o_ref <= o_sys else v_sys
    d_ref, _ = tuple_distance(result, t_ref)
    d_sys, _ = tuple_distance(result, t_sys)
    return {"meet": result, "d_from_cl8nk": d_ref, "d_from_system": d_sys}


def compute_join_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L8_REF
    result = {}
    for key in PRIMITIVE_KEYS:
        v_ref = t_ref.get(key)
        v_sys = t_sys.get(key)
        ords = ORDINALS.get(key, {})
        o_ref = ords.get(v_ref, 0)
        o_sys = ords.get(v_sys, 0)
        result[key] = v_ref if o_ref >= o_sys else v_sys
    d_ref, _ = tuple_distance(result, t_ref)
    d_sys, _ = tuple_distance(result, t_sys)
    return {"join": result, "d_from_cl8nk": d_ref, "d_from_system": d_sys}

# =============================================================================
# CONTAINMENT BOUNDARY — S16 ∧ L8 as a verifiable action surface
# =============================================================================
# The SIXTEEN_3 trilattice met against CLINK L8 gives a shared floor —
# ⊙=⊙, Φ=𐑹, Ç=𐑧 plus nine more coordinates — the "paraconsistent observer"
# surface. A system is CONTAINED on a primitive iff its own ordinal there is at
# least as strict as the floor's (meeting it with the floor would not pull the
# floor lower). Mirrors IG_inquiry.py's ToolDispatcher._containment_boundary
# (the general two-name-lattice engine); this is the CL8NK-native form, fixed
# to the S16/L8 reference pair, consistent with how compute_tensor_op/
# compute_meet_op/compute_join_op above are already fixed to CLINK_L8_REF.

_CONTAINMENT_CRITICAL = ("⊙", "Φ", "Ç")


def compute_containment_op(t_sys, t_s16=None, t_l8=None):
    if t_l8 is None:
        t_l8 = CLINK_L8_REF
    if t_s16 is None:
        s16_info = resolve_system("sixteen_3_trilattice")
        t_s16 = s16_info.get("tuple", {}) if s16_info else {}
    weights = _ensure_weights()

    floor = {}
    for key in PRIMITIVE_KEYS:
        ords = ORDINALS.get(key, {})
        o_s16 = ords.get(t_s16.get(key), 0)
        o_l8 = ords.get(t_l8.get(key), 0)
        floor[key] = t_s16.get(key) if o_s16 <= o_l8 else t_l8.get(key)

    breaches, held = [], []
    for key in PRIMITIVE_KEYS:
        ords = ORDINALS.get(key, {})
        fv = floor.get(key)
        tv = t_sys.get(key, "?")
        o_floor = ords.get(fv, 0)
        o_sys = ords.get(tv, 0)
        if o_sys >= o_floor:
            held.append(key)
        else:
            breaches.append({
                "primitive": key, "floor": fv, "system": tv,
                "critical": key in _CONTAINMENT_CRITICAL,
                "weight": weights.get(key, 0.5),
            })

    critical_breach = [b for b in breaches if b["critical"]]
    weighted_breach_total = round(sum(b["weight"] for b in breaches), 4)
    if not breaches:
        verdict, reading = "T", "Fully contained — every primitive holds at or above the S16∧L8 floor."
    elif not critical_breach:
        verdict = "B"
        reading = (
            f"Contained on the observer surface (⊙, Φ, Ç all hold) but breaches "
            f"{len(breaches)} non-critical primitive(s), weighted severity {weighted_breach_total} "
            "(sum of catalog-discriminating weights of the breached primitives, same weight table "
            "tuple_distance uses — a breach on a highly-discriminating primitive counts for more "
            "than one on a primitive that barely varies across the catalog). Held, not refused."
        )
    else:
        names = ", ".join(b["primitive"] for b in critical_breach)
        verdict = "F"
        reading = (
            f"Breaches the defining floor itself ({names}) — erodes the paraconsistent-observer "
            "surface, not just a secondary primitive. Refused."
        )

    return {
        "floor": floor, "verdict": verdict, "held": held, "breaches": breaches,
        "weighted_breach_total": weighted_breach_total,
        "interpretation": reading,
    }


def action_contain(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl8nk")
    if _bad:
        return _bad
    result = compute_containment_op(sys_info.get("tuple", {}))
    result["status"] = "ok"
    result["name"] = sys_info.get("name", name)
    return result

# =============================================================================
# TRANSCENDENCE ANALYSIS — dynamically computed from catalog
# =============================================================================

def compute_transcendence():
    zfc_fe = get_zfc_fe()
    if zfc_fe is None:
        return {"status": "error", "message": "ZFC_fe not found in catalog"}

    cl8 = CLINK_L8_REF
    d, conflicts = tuple_distance(zfc_fe, cl8)

    omega_info = {
        "primitive": "Ω",
        "zfc_fe_value": zfc_fe.get("Ω", "?"),
        "clink_l8_value": cl8.get("Ω", "?"),
        "zfc_fe_fragment": CL8NK_FORMULAE["Ω"].get(zfc_fe.get("Ω", ""), ("?", None, "?"))[0],
        "clink_l8_fragment": CL8NK_FORMULAE["Ω"].get(cl8.get("Ω", ""), ("?", None, "?"))[0],
        "zfc_fe_atom": CL8NK_FORMULAE["Ω"].get(zfc_fe.get("Ω", ""), ("?", None, "?"))[1],
        "clink_l8_atom": CL8NK_FORMULAE["Ω"].get(cl8.get("Ω", ""), ("?", None, "?"))[1],
        "significance": "Integer winding (Abelian anyons) → braid group topology (non-Abelian anyons). This is the topological quantum computing threshold.",
    }
    grammar_info = {
        "primitive": "ɢ",
        "zfc_fe_value": zfc_fe.get("ɢ", "?"),
        "clink_l8_value": cl8.get("ɢ", "?"),
        "zfc_fe_fragment": CL8NK_FORMULAE["ɢ"].get(zfc_fe.get("ɢ", ""), ("?", None, "?"))[0],
        "clink_l8_fragment": CL8NK_FORMULAE["ɢ"].get(cl8.get("ɢ", ""), ("?", None, "?"))[0],
        "zfc_fe_atom": CL8NK_FORMULAE["ɢ"].get(zfc_fe.get("ɢ", ""), ("?", None, "?"))[1],
        "clink_l8_atom": CL8NK_FORMULAE["ɢ"].get(cl8.get("ɢ", ""), ("?", None, "?"))[1],
        "significance": "Sequential stepwise composition → simultaneous broadcast. The organism composes signals to all subsystems simultaneously.",
    }

    tensor_result = compute_tensor_op(zfc_fe, cl8)
    absorbed = tensor_result["distance_from_cl8nk"] == 0.0

    return {
        "status": "ok",
        "title": "The Ω/ɢ Transcendence — CLINK L8 beyond ZFC_fe",
        "zfc_fe_tuple": zfc_fe,
        "clink_l8_tuple": cl8,
        "d_zfcfe_to_cl8nk": d,
        "transcendence_primitives": {"omega": omega_info, "grammar": grammar_info},
        "tensor_absorption": f"tensor(ZFC_fe, CLINK L8) = {'CLINK L8' if absorbed else 'composite'} — foundation {'is' if absorbed else 'is NOT'} fully absorbed",
        "significance": (
            "CLINK L8 is not merely another O_∞ type — it is a strict structural SUPERSET of ZFC_fe. "
            "Non-Abelian braiding (Ω=𐑟) and broadcast composition (ɢ=𐑵) are structural advances "
            "that the Frobenius-exact ZFC foundation itself has not encoded."
        ),
    }

# =============================================================================
# PROMOTION LADDER — with per-primitive formula changes
# =============================================================================

def promo_details(t_from, t_to):
    """Per-primitive promotion ledger carrying t_from -> t_to.

    The general operator behind every promotion ladder: report each primitive
    whose value moves, with its CL8NK formula fragment/atom on both sides and
    the ordinal gap crossed. Primitives that agree are held fixed and omitted.
    """
    result = []
    for key in PRIMITIVE_KEYS:
        if t_from.get(key) != t_to.get(key):
            fmap = CL8NK_FORMULAE.get(key, {})
            f_info = fmap.get(t_from.get(key, ""), ("?", None, "?"))
            t_info = fmap.get(t_to.get(key, ""), ("?", None, "?"))
            result.append({
                "primitive": key,
                "from_value": t_from[key],
                "to_value": t_to[key],
                "from_fragment": f_info[0],
                "to_fragment": t_info[0],
                "from_atom": f_info[1],
                "to_atom": t_info[1],
                "ordinal_gap": round(ordinal_distance(key, t_from[key], t_to[key]), 3),
            })
    return result


def generate_promotion_path(from_name, to_name):
    """Promotions carrying one catalog vessel to another.

    Imscribe both poles of a claim (e.g. `abc_conjecture` and
    `abc_conjecture_proven`), then read off the exact promotions that separate
    them: the vessel and the path come from the Grammar, and this is the path.
    """
    load_catalog()
    a = resolve_system(from_name)
    if a is None:
        return {"status": "error", "message": f"System '{from_name}' not found in catalog."}
    b = resolve_system(to_name)
    if b is None:
        return {"status": "error", "message": f"System '{to_name}' not found in catalog."}

    t_from, t_to = a.get("tuple", {}), b.get("tuple", {})
    details = promo_details(t_from, t_to)
    d, _ = tuple_distance(t_from, t_to)
    held = [k for k in PRIMITIVE_KEYS if t_from.get(k) == t_to.get(k)]

    return {
        "status": "ok",
        "from": {"name": a.get("name", from_name), "description": a.get("description", ""),
                 "tuple": t_from, "tier": assess_tier(t_from)},
        "to": {"name": b.get("name", to_name), "description": b.get("description", ""),
               "tuple": t_to, "tier": assess_tier(t_to)},
        "promotions": details,
        "promotion_count": len(details),
        "held_fixed": held,
        "distance": round(d, 4),
    }


def generate_promotions():
    zfc_baseline = {"Ð":"𐑼","Þ":"𐑡","Ř":"𐑩","Φ":"𐑗","ƒ":"𐑱","Ç":"𐑘","Γ":"𐑚","ɢ":"𐑝","⊙":"𐑢","Ħ":"𐑓","Σ":"𐑙","Ω":"𐑷"}

    zfc_t = None
    load_catalog()
    for name in ("ZFCt", "zfc_t_system", "zfc_t_ref", "zfc_t"):
        if name in CATALOG_INDEX:
            entry = CATALOG_INDEX[name]
            zfc_t = {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
            break
    if zfc_t is None:
        zfc_t = {"Ð":"𐑼","Þ":"𐑸","Ř":"𐑾","Φ":"𐑬","ƒ":"𐑐","Ç":"𐑧","Γ":"𐑲","ɢ":"𐑠","⊙":"⊙","Ħ":"𐑖","Σ":"𐑳","Ω":"𐑭"}

    zfc_fe = get_zfc_fe()
    if zfc_fe is None:
        return {"status": "error", "message": "ZFC_fe not found in catalog"}

    cl8 = CLINK_L8_REF

    stage1 = promo_details(zfc_baseline, zfc_t)
    stage2 = promo_details(zfc_t, zfc_fe)
    stage3 = promo_details(zfc_fe, cl8)

    d_zfc_zfct = tuple_distance(zfc_baseline, zfc_t)[0]
    d_zfct_zfcfe = tuple_distance(zfc_t, zfc_fe)[0]
    d_zfcfe_cl8nk = tuple_distance(zfc_fe, cl8)[0]
    d_zfc_cl8nk = tuple_distance(zfc_baseline, cl8)[0]

    return {
        "status": "ok",
        "ladder": [
            {"stage": "ZFC baseline", "tier": "O₀",
             "promotions": 0,
             "tuple": zfc_baseline},
            {"stage": "→ ZFC_t", "tier": "O₂†",
             "promotions": len(stage1), "distance": round(d_zfc_zfct, 4),
             "details": stage1},
            {"stage": "→ ZFC_fe", "tier": "O_∞",
             "promotions": len(stage2), "distance": round(d_zfct_zfcfe, 4),
             "details": stage2},
            {"stage": "→ CLINK L8", "tier": "O_∞⁺",
             "promotions": len(stage3), "distance": round(d_zfcfe_cl8nk, 4),
             "details": stage3,
             "note": "Ω/ɢ TRANSCENDENCE — exceeds Frobenius-exact foundation"},
        ],
        "total_promotions": len(stage1) + len(stage2) + len(stage3),
        "total_distance_zfc_to_cl8nk": round(d_zfc_cl8nk, 4),
        "transcendence": {"primitives": ["Ω", "ɢ"], "d_zfcfe_to_cl8nk": round(d_zfcfe_cl8nk, 4)},
        "catalog_note": "ZFC_fe and CLINK L8 sourced from IG_catalog.json; ZFC baseline is the absolute minimal O₀ type.",
    }

# =============================================================================
# CHAIN ANALYSIS — dynamically discovered from catalog
# =============================================================================

def chain_analysis():
    clink_chain = discover_clink_chain()
    if not clink_chain:
        return {"status": "error", "message": "No CLINK layers found in catalog"}

    def _layer_num(name):
        import re
        m = re.search(r'layer(\d+)', name)
        return int(m.group(1)) if m else 99

    sorted_names = sorted(clink_chain.keys(), key=_layer_num)
    layers = []
    for name in sorted_names:
        info = clink_chain[name]
        t = info["tuple"]
        d, conflicts = tuple_distance(t, CLINK_L8_REF)
        tier = assess_tier(t)
        layers.append({
            "layer": name,
            "description": info["description"],
            "distance_from_l8": d,
            "tier": tier,
            "conflicts_count": len(conflicts),
        })

    return {
        "reference": "CLINK L8 (Organism) — from catalog",
        "total_layers": len(layers),
        "layers": layers,
        "ascent_interpretation": "Distance decreases monotonically from L0→L8.",
        "catalog_note": f"Discovered {len(layers)} CLINK layers from catalog.",
    }


# =============================================================================
# ACTION HANDLERS — all catalog-native
# =============================================================================

def action_entry(name):
    load_catalog()
    if CLINK_L8_REF is None:
        return {"status": "error", "message": "CLINK L8 reference not found in catalog."}
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog ({len(CATALOG_INDEX)} entries)."}
    result = generate_formula(sys_info.get("tuple", {}), sys_info.get("name", name))
    result["status"] = "ok"
    result["description"] = sys_info.get("description", "")
    return result


def action_promotions():
    return generate_promotions()


def action_promote(from_name, to_name):
    return generate_promotion_path(from_name, to_name)


def _unreadable_tuple(name, t, nav):
    """A tuple whose values did not resolve is not a coordinate — refuse to measure it.

    Six catalog entries (the Navier-Stokes family and zfc_t_system) still carry their tuple in
    a retired notation, so it parses to twelve EMPTY strings. `entry` was honest about this and
    printed `unknown()` twelve times. `distance`/`tier`/`tensor`/`meet`/`join` were not: they
    measured the empty tuple against the reference and returned status "ok" with a precise
    number — 3.0173, BYTE-IDENTICAL for every unreadable entry, because it is the distance from
    NOTHING to the reference, not a property of the entry at all.

    A tool that cannot read its input and answers anyway is worse than one that errors, because
    the answer looks like a measurement. Same fault as a no-arg action silently discarding its
    argument: the model fills the gap with what it was handed, then gets blamed for the
    confabulation the tool invited.
    """
    if not isinstance(t, dict) or not t:
        missing = []
    else:
        missing = [p for p, v in t.items() if not v]
    if not missing:
        return None
    return {
        "status": "error",
        "error": (
            f"'{name}' has an unreadable tuple: {len(missing)} of {len(t)} primitives did not "
            f"resolve ({' '.join(missing)}). Its catalog tuple is written in a retired notation, "
            f"so it parsed to empty. This entry has no coordinate to measure."
        ),
        "why_you_got_an_error_and_not_a_number": (
            "Measuring an empty tuple against the reference returns the distance from NOTHING. "
            "That value is a constant — identical for every unreadable entry — so it would have "
            "told you nothing about this one while looking exactly like a measurement."
        ),
        "fix": f"Re-imscribe it so it has a live coordinate: TOOL: imscribe {name} <description>",
        "navigator": nav,
    }


def action_distance(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    t = sys_info.get("tuple", {})
    _bad = _unreadable_tuple(sys_info.get("name", name), t, "cl8nk")
    if _bad:
        return _bad
    d, conflicts = tuple_distance(t, CLINK_L8_REF)
    tier = assess_tier(t)
    return {"status": "ok", "name": sys_info.get("name", name), "distance_to_cl8nk": d,
            "tier": tier, "conflicts": conflicts, "conflict_count": len(conflicts)}


def action_transcendence():
    return compute_transcendence()


def action_tensor(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl8nk")
    if _bad:
        return _bad
    result = compute_tensor_op(sys_info.get("tuple", {}))
    result["status"] = "ok"
    result["name"] = sys_info.get("name", name)
    return result


def action_meet(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl8nk")
    if _bad:
        return _bad
    result = compute_meet_op(sys_info.get("tuple", {}))
    result["status"] = "ok"
    result["name"] = sys_info.get("name", name)
    return result


def action_join(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl8nk")
    if _bad:
        return _bad
    result = compute_join_op(sys_info.get("tuple", {}))
    result["status"] = "ok"
    result["name"] = sys_info.get("name", name)
    return result


def action_tier(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    t = sys_info.get("tuple", {})
    _bad = _unreadable_tuple(sys_info.get("name", name), t, "cl8nk")
    if _bad:
        return _bad
    tier = assess_tier(t)
    d, _ = tuple_distance(t, CLINK_L8_REF)
    return {"status": "ok", "name": sys_info.get("name", name), "tier": tier, "distance_from_cl8nk": d}


def action_chain():
    result = chain_analysis()
    result["status"] = "ok"
    return result


def action_systems():
    load_catalog()
    systems = sorted(CATALOG_INDEX.keys())
    stats = catalog_stats()
    return {"status": "ok", "systems": systems, "count": len(systems), "catalog": stats}


def action_stats():
    load_catalog()
    stats = catalog_stats()
    stats["clink_l8_tuple"] = CLINK_L8_REF
    stats["zfc_fe_tuple"] = get_zfc_fe()
    stats["clink_layers_found"] = len(discover_clink_chain())
    return {"status": "ok", "catalog": stats}

# =============================================================================
# RICH TABLE RENDERER  (matches zfcfe_navigator / zfct_navigator output format)
# =============================================================================

import textwrap as _textwrap

_ATOM_DESC = {
    "HOLOGRAPHIC_STATE":     "V=L(x) self-writing state-space — Axiom C (𐑦)",
    "HOLOBOUND":             "holographic bound_⊙/bulk encoding — 𐑸",
    "LR_DUAL":               "lateral relational duality — 𐑾",
    "PM_Z2":                 "ℤ₂ parity with Frobenius μ∘δ=id — 𐑹",
    "SEQAX":                 "sequentiality axiom, directed time — 𐑠",
    "PHI_C":                 "criticality fixed-point ξ→∞ ∧ μ∘δ=id — ⊙",
    "TEMPD2":                "chirality-2 asymmetry — 𐑖",
    "ETERNAL_FIXEDPOINT":    "∀n∃φ fixed by μ∘δ — Axiom D (𐑫)",
    "ZWIND":                 "integer winding number — 𐑭",
    "BROADCAST_TRANSCENDENCE": "⬆ broadcast composition — exceeds ZFC_fe SEQAX — ɢ",
    "BRAID_TRANSCENDENCE":    "⬆ non-Abelian braiding — exceeds ZFC_fe ZWIND — Ω",
}

def _print_entry_table(result):
    W = 120; PW = 5; VW = 6; FW = W - 2 - PW - 2 - VW - 2

    print("\n" + "═" * W)
    print(f"  CL8NK Entry: {result.get('system', '?')}")
    desc = result.get("description", "")
    if desc:
        for line in _textwrap.wrap(desc, W - 4):
            print(f"  {line}")
    print(f"  Reference: {result.get('reference', '')}")
    print(f"  Catalog-native — no hardcoded systems")
    print("═" * W)

    fd = result.get("formula_decomposition", {})
    frags = fd.get("per_primitive_fragments", [])
    legend = {}

    print()
    print(f"  {'Prim':<{PW}}  {'Value':<{VW}}  CLINK fragment")
    print(f"  {'─'*PW}  {'─'*VW}  {'─'*FW}")

    for frag in frags:
        p        = frag["primitive"]
        val      = frag["value"]
        formula  = frag["clink_fragment"]
        atom     = frag.get("promoted_atom")
        prox     = frag.get("proximity", "?")

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

    if legend:
        print()
        kw = max(len(k) for k in legend)
        for atom in legend:
            note = _ATOM_DESC.get(atom, "")
            print(f"  [{atom:<{kw}}] {note}")

    # Full CLINK conjunction
    full = fd.get("full_clink_formula", "")
    if full:
        print(f"\n── CLINK expression {'─' * (W - 22)}")
        for i, line in enumerate(full.split(" ∧\n    ")):
            suffix = " ∧" if i < full.count(" ∧\n    ") else ""
            print(f"  {line}{suffix}")

    # Structural summary
    sa = result.get("structural_algebra", {})
    tier = sa.get("ouroboricity_tier", "?")
    d    = sa.get("distance_from_cl8nk", "?")
    m    = sa.get("match_count", 0)
    c    = sa.get("close_count", 0)
    dist = sa.get("distant_count", 0)
    print(f"\n  tier: {tier}   d(CLINK L8): {d}   match:{m} close:{c} distant:{dist}")

    promoted = fd.get("promoted_atoms", [])
    if promoted:
        print(f"  promoted atoms: {', '.join(promoted)}")

    transc = result.get("transcendence_primitives", [])
    if transc:
        print(f"  ⬆ TRANSCENDENCE primitives: {', '.join(transc)}")

    promos = result.get("promotions_needed", [])
    if promos:
        print(f"\n  Promotions needed to reach CLINK L8 ({len(promos)}):")
        for p in promos:
            print(f"    {p['primitive']}: {p['from']} → {p['to']}  (gap: {p['gap']})")

# =============================================================================
# MAIN
# =============================================================================

def _refuse_stray_arg(action: str, arg, nav: str) -> bool:
    """A no-arg action given a name is answering a question nobody asked.

    `moat` is a global theorem about the Gaussian Moat and `promotions` is the fixed
    ZFC→CLINK ladder; neither reads an entry. Silently dropping the argument returned a
    generic result that never mentioned the name, byte-identical no matter what was passed
    — which is worse than an error, because it looks like an answer. A live run asked for
    `moat narrative_field_…`, got the generic theorem back, and the model filled the gap
    itself: it invented a formatted per-entry "Moat Analysis" with a width lifted from an
    unrelated promotion rung. A tool that ignores its argument and answers anyway INVITES
    the confabulation it will then be blamed for.
    """
    if arg is None:
        return False
    print(json.dumps({
        "status": "error",
        "error": f"'{action}' takes no entry — it is a global result, and your argument "
                 f"{arg!r} was being silently discarded.",
        "you_probably_want": {
            "entry <name>":  "the full per-entry decomposition",
            "distance <name>": "that entry's gap to the reference",
            "tier <name>":   "that entry's ouroboricity tier",
            "promote <a> <b>": "the promotions carrying one vessel to another",
        },
        "note": f"{nav} {action} is unchanged and still available with no argument.",
    }, indent=2, ensure_ascii=False))
    return True


def main():
    load_catalog()

    if len(sys.argv) < 2:
        print("CL8NK Navigator — CLINK Layer 8 (Organism) reference navigator")
        print("CATALOG-NATIVE: All data sourced from IG_catalog.json")
        print(f"Catalog: {catalog_stats()['total_entries']} entries loaded")
        print(f"CLINK L8 reference: {'FOUND' if CLINK_L8_REF else 'NOT FOUND'}")
        print()
        print("Usage: python cl8nk_navigator.py <action> [name]")
        print()
        print("Actions:")
        print("  entry <name>       — Full CL8NK formula decomposition (PRIMARY)")
        print("  promotions         — Promotion ladder: ZFC→ZFC_t→ZFC_fe→CLINK L8")
        print("  promote <a> <b>    — Promotions carrying vessel a → vessel b")
        print("  distance <name>    — Distance from CLINK L8")
        print("  transcendence      — The Ω/ɢ transcendence analysis (from catalog)")
        print("  tensor <name>      — CLINK L8 ⊗ name (absorption test)")
        print("  meet <name>        — CLINK L8 ⊓ name")
        print("  join <name>        — CLINK L8 ⊔ name")
        print("  tier <name>        — Ouroboricity tier assessment")
        print("  chain              — Full CLINK chain L0→L8 distance ladder")
        print("  systems            — All catalog systems")
        print("  stats              — Catalog statistics + reference tuples")
        print()
        all_sys = sorted(CATALOG_INDEX.keys())
        print(f"Catalog systems ({len(all_sys)} total):")
        clink_sys = [s for s in all_sys if 'clink' in s.lower()]
        zfc_sys = [s for s in all_sys if 'zfc' in s.lower()]
        print(f"  CLINK: {', '.join(clink_sys) if clink_sys else 'none'}")
        print(f"  ZFC:   {', '.join(zfc_sys[:5]) if zfc_sys else 'none'}")
        print(f"  (use 'systems' for full list)")
        return

    action = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    arg2 = sys.argv[3] if len(sys.argv) > 3 else None

    action_map = {
        "entry": action_entry,
        "promotions": action_promotions,
        "promote": action_promote,
        "distance": action_distance,
        "transcendence": action_transcendence,
        "tensor": action_tensor,
        "meet": action_meet,
        "join": action_join,
        "contain": action_contain,
        "tier": action_tier,
        "chain": action_chain,
        "systems": action_systems,
        "stats": action_stats,
    }

    if action not in action_map:
        # A bare catalog name is an omitted keyword, not a missing entry. Reporting it as
        # unknown sent a live run off to imscribe a reagent already on the shelf.
        if resolve_system(action) is not None:
            print(f"(reading `{action}` as `entry {action}` — action keyword omitted)")
            action, arg = "entry", action
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)

    no_arg_actions = ("promotions", "transcendence", "chain", "systems", "stats")
    if action == "promote":
        if not arg or not arg2:
            print("Usage: cl8nk_navigator.py promote <from> <to>")
            print("  e.g. promote abc_conjecture abc_conjecture_proven")
            sys.exit(1)
        result = action_promote(arg, arg2)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action in no_arg_actions:
        if _refuse_stray_arg(action, arg, "cl8nk_navigator.py"):
            sys.exit(2)
        result = action_map[action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action == "entry":
        if not arg:
            print("Usage: cl8nk_navigator.py entry <name>")
            all_sys = sorted(CATALOG_INDEX.keys())
            print(f"Catalog systems ({len(all_sys)}): {', '.join(all_sys[:30])}{'...' if len(all_sys)>30 else ''}")
            sys.exit(1)
        result = action_map[action](arg)
        if result.get("status") == "error":
            print(f"[CL8NK] {result['message']}")
            return
        _print_entry_table(result)
    else:
        if not arg:
            print(f"Usage: cl8nk_navigator.py {action} <name>")
            sys.exit(1)
        result = action_map[action](arg)
        print(json.dumps(result, indent=2, ensure_ascii=False))


# =============================================================================
# PROGRAMMATIC API (for import by agent harness or other tools)
# =============================================================================

def probe_entry(name):
    """Programmatic entry probe — returns rich text output matching navigator format."""
    result = action_entry(name)
    if result.get("status") == "error":
        print(f"[CL8NK] {result['message']}")
        return
    _print_entry_table(result)

def probe_promotions():
    print(json.dumps(action_promotions(), indent=2, ensure_ascii=False))

def probe_transcendence():
    print(json.dumps(action_transcendence(), indent=2, ensure_ascii=False))

def probe_distance(name):
    print(json.dumps(action_distance(name), indent=2, ensure_ascii=False))

def probe_chain():
    print(json.dumps(action_chain(), indent=2, ensure_ascii=False))

def probe_tensor(name):
    print(json.dumps(action_tensor(name), indent=2, ensure_ascii=False))

def probe_meet(name):
    print(json.dumps(action_meet(name), indent=2, ensure_ascii=False))

def probe_join(name):
    print(json.dumps(action_join(name), indent=2, ensure_ascii=False))

def probe_contain(name):
    print(json.dumps(action_contain(name), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
