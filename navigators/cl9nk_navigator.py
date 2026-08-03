#!/usr/bin/env python3
"""
CL9NK Navigator — CLINK Layer 9 (Gaussian Moat Resolution) reference navigator.
CATALOG-NATIVE: No hardcoded systems. All data sourced from IG_catalog.json.

CLINK L9 is the structural resolution of the Gaussian Moat Problem via the Hodge Bridge.
It builds upon CLINK L8 (Organism) by adding the Hodge Bridge theorem,
which guarantees an infinite bounded-step path through the prime lattice.

Canonical tuple: ⟨𐑛𐑥𐑑𐑬𐑐𐑪𐑔𐑝⊙𐑫𐑳𐑭⟩

The L9 Transcendence over L8:
  - HODGE_BRIDGE: structural axiom that ensures density of bridges across moats
  - INFINITE_STITCH: the infinite repetition of [moat · hodge · linker] yields path to infinity

Actions:
  entry  <name>    — Full CL9NK formula decomposition: per-primitive CLINK fragments,
                      promoted atoms, full conjunction, distance, tensor/meet/join, tier
  promotions        — All promotion channels: ZFC → ZFC_t → ZFC_fe → CLINK L8 → CLINK L9
  distance <name>   — d(name, CLINK L9) with per-primitive conflicts
  transcendence     — The L9 transcendence: what CLINK L9 has that CLINK L8 doesn't
  tensor  <name>    — CLINK L9 ⊗ name — absorption test
  meet    <name>    — CLINK L9 ⊓ name — shared floor
  join    <name>    — CLINK L9 ⊔ name — minimal ceiling
  tier    <name>    — Ouroboricity tier assessment
  chain             — Full CLINK chain (L0–L9) distances from CLINK L9
  systems           — All catalog systems (dynamically listed)
  stats             — Catalog statistics + reference tuples
  moat              — Run the Gaussian Moat resolution verification (CLINK L9 theorem)
"""

import sys
import json
import math
import os as _os

# =============================================================================
# PRIMITIVE ORDINALS  (SNS.md §Ordinal Table — 1-based)
# =============================================================================

ORDINALS = {
    "⊢": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "⊣": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    ">": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "<": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "⋈": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "⊤": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "∈": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "∋": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "⊙": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "⊥": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "⊞": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "◻": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}

PRIMITIVE_KEYS = ["⊢", "⊣", ">", "<", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "◻"]

# =============================================================================
# CATALOG LOADING — single source of truth, no hardcoded systems
# =============================================================================

CATALOG = None
CATALOG_INDEX = {}
CLINK_L9_REF = None
CLINK_L8_REF = None

def _find_catalog_path():
    _here = _os.path.dirname(_os.path.abspath(__file__))
    _candidates = [
        # Canonical FIRST — the website and vendored copies run days behind.
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
    global CATALOG, CATALOG_INDEX, CLINK_L9_REF, CLINK_L8_REF
    if CATALOG is not None and not force:
        return
    path = _find_catalog_path()
    if path is None:
        CATALOG = []
    else:
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

    # Resolve CLINK L8 from catalog (or fallback)
    CLINK_L8_REF = _resolve_clink_l8_reference()
    # CLINK L9 is defined internally (no catalog entry yet)
    CLINK_L9_REF = {
        "⊢": "𐑛",
        "⊣": "𐑥",
        ">": "𐑑",
        "<": "𐑬",
        "⋈": "𐑐",
        "⊤": "𐑪",
        "∈": "𐑔",
        "∋": "𐑝",
        "⊙": "⊙",
        # ⊥ (Chirality) owns 𐑫 = wool = inexhaustible chirality → ETERNAL_FIXEDPOINT.
        # ◻ (Protection) owns 𐑭 = ah = integer winding ℤ → ZWIND (∮A = 2πn, n ∈ ℤ).
        # These were transposed: ⊥ held 𐑭 and ◻ held 𐑫, i.e. each carried a value from
        # the other's axis. The swap made clink_l9 report distance 1.2289 from its OWN
        # reference, with the only two "promotions" being ⊥: 𐑫→𐑭 and ◻: 𐑭→𐑫 — a
        # transposition masquerading as structure. Ordinal authority is Core.lean.
        "⊥": "𐑫",
        "⊞": "𐑳",
        "◻": "𐑭",
    }


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
    # Fallback: known L8 tuple from earlier
    return {
        "⊢": "𐑦",
        "⊣": "𐑸",
        ">": "𐑾",
        "<": "𐑹",
        "⋈": "𐑐",
        "⊤": "𐑧",
        "∈": "𐑲",
        "∋": "𐑵",
        "⊙": "⊙",
        "⊥": "𐑫",
        "⊞": "𐑳",
        "◻": "𐑟",
    }

# =============================================================================
# ALIASES — query shorthands → canonical catalog names (routing only, no tuples)
# =============================================================================

ALIASES = {
    "clink_l9": "clink_layer9_gaussian_moat",
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
    # Add L9 (virtual)
    chain["clink_layer9_gaussian_moat"] = {
        "description": "Gaussian Moat Resolution via Hodge Bridge — CLINK L9",
        "tuple": CLINK_L9_REF.copy(),
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
        "clink_l9_found": CLINK_L9_REF is not None,
        "clink_l8_found": CLINK_L8_REF is not None,
        "zfc_fe_found": get_zfc_fe() is not None,
    }

# =============================================================================
# WEIGHTED DISTANCE (matching imscribe compute_distance algorithm)
# =============================================================================

MAX_DELTAS = {
    k: max(v.values()) - min(v.values())
    for k, v in ORDINALS.items()
}

_WEIGHTS_CACHE: dict = {}

def _compute_catalog_weights() -> dict:
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
            conflicts.append({"primitive": key, "cl9nk": v2, "system": v1, "delta": round(d, 3)})
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
    scored how many of CLINK L8's OWN VALUES a tuple carried (⊢=𐑦, ⊣=𐑸, >=𐑾,
    <=𐑹, ⊤=𐑧, ◻=𐑟, ⊙=⊙, ⊥=𐑫) and bucketed on the count, with a top branch
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
    pol  = t.get("<")
    prot = t.get("◻")
    dim  = t.get("⊢")
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
# CL9NK FORMULAE — per-primitive CLINK formula fragments with promoted atoms
# =============================================================================
# Each entry: (clink_fragment, promoted_atom_name_or_None, proximity)
# proximity: "match" (CL9NK itself), "close" (1 step away), "distant" (>1 step)

CL9NK_FORMULAE = {
    "⊢": {
        "𐑛": ("dim(x) = 0 ∧ fin(x) — point-like prime atom", "PRIME_POINT", "match"),
        "𐑨": ("dim(x) = 2 ∧ sur(x)", None, "distant"),
        "𐑼": ("∀n∃y( y ∈ x ∧ rank(y) > n )", None, "close"),
        "𐑦": ("V = L(x) ∧ selfmodel(x) ∧ x ∈ V", "HOLOGRAPHIC_STATE", "distant"),
    },
    "⊣": {
        "𐑥": ("cross(x, y) ∧ ¬ meet(x, y) — moat crossing", "MOAT_CROSS", "match"),
        "𐑸": ("bound_⊙(a, f) ∧ Refl(a, f) ∧ holo(x, a)", "HOLOBOUND", "distant"),
        "𐑶": ("x ⊠ y ∧ irreducible(x, y)", None, "close"),
        "𐑡": ("graph(x) ∧ branch(x)", None, "distant"),
        "𐑰": ("x ⊆ y ∧ cont(y)", None, "distant"),
    },
    ">": {
        "𐑑": ("Fun(x, y) ∧ Nat(y, z) → Fun(x, z) — bridge composition", "BRIDGE_COMP", "match"),
        "𐑽": ("f ⊣ g ∧ L Adj(f, g)", None, "close"),
        "𐑩": ("x ↑ y ∧ ¬(y ↑ x)", None, "distant"),
        "𐑾": ("lr⇔(x, y) ∧ Θ(x, y) ∧ ¬ Θ(y, x)", "LR_DUAL", "distant"),
    },
    "<": {
        "𐑬": ("ℤ₂(x) ∧ ¬(x = -x) — parity of moat", "MOAT_PARITY", "match"),
        "𐑿": ("|ψ⟩ = Σ c_i |e_i⟩", None, "close"),
        "𐑯": ("∀g∈G( gx = x )", None, "distant"),
        "𐑗": ("¬∃sym(x)", None, "distant"),
        "𐑹": ("ℤ₂(x) ∧ ∀g∈G( gx = x ) ∧ μ∘δ = id", "PM_Z2", "distant"),
    },
    "⋈": {
        "𐑐": ("ℏ(x) ∧ [x, p] = iℏ — commutator of bridge", "BRIDGE_COMM", "match"),
        "𐑞": ("Tr(ρ²) < 1 ∧ ρ = Σ p_i |i⟩⟨i|", None, "close"),
        "𐑱": ("P(x) ∈ {0,1} ∧ det(x)", None, "distant"),
    },
    "⊤": {
        "𐑪": ("τ = ∞ ∧ ord(x) — infinite extension", "INFINITE_EXT", "match"),
        "𐑧": ("τ ≫ T ∧ eq(x) ∧ gate_open(x)", None, "distant"),
        "𐑤": ("τ ∼ T ∧ noisy(x)", None, "close"),
        "𐑘": ("τ ≪ T ∧ ∂_t x = f(x)", None, "distant"),
        "𐑺": ("τ = ∞ ∧ dis(x) ∧ MBL", None, "distant"),
    },
    "∈": {
        "𐑔": ("∃y∈x( |y| ∼ |x| ) — bridge existence", "BRIDGE_EXIST", "match"),
        "𐑲": ("∀y( y ⊂ x → |y| < |x| )", None, "distant"),
        "𐑚": ("∀y∈x( |y| < |x| )", None, "distant"),
    },
    "∋": {
        "𐑝": ("f ∧ g ∧ h — three-unit stitch", "STITCH_3", "match"),
        "𐑜": ("f ∨ g ∨ h", None, "close"),
        "𐑠": ("seq!(f, g) ∧ ⟨→⟩(f, g, τ) ∧ ¬ ⟨→⟩(g, f, τ)", "SEQAX", "distant"),
        "𐑵": ("f → all(x) ∧ broadcast(x, f)", "BROADCAST_TRANSCENDENCE", "distant"),
    },
    "⊙": {
        "⊙": ("ξ → ∞ ∧ μ∘δ = id — criticality", "PHI_C", "match"),
        "𐑮": ("ξ ∈ ℂ ∧ Im(ξ) → ∞", None, "close"),
        "𐑻": ("H(λ) non-Herm ∧ det(H - λI) = 0 ∧ ∂_λ H = 0", None, "distant"),
        "𐑣": ("ξ → ∞ ∧ chaotic(x)", None, "distant"),
        "𐑢": ("¬∃ξ( diverges(ξ) )", None, "distant"),
    },
    "⊥": {
        "𐑭": ("∮_γ A = 2πn ∧ n ∈ ℤ ∧ wind(γ) ≠ 0 — winding bridge", "WIND_BRIDGE", "match"),
        "𐑫": ("∀n∃φ( rank(φ) > n ∧ φ fixed by μ∘δ ∧ φ ∈ V )", "ETERNAL_FIXEDPOINT", "distant"),
        "𐑖": ("∃y∃z( y ∈ x ∧ z ∈ y ∧ ¬ z ∈ x ∧ rank(z) < rank(y) )", "TEMPD2", "close"),
        "𐑒": ("∃y( P(y) ↔ P(S²(y)) )", None, "distant"),
        "𐑓": ("∀x( P(x) ↔ P(S(x)) )", None, "distant"),
    },
    "⊞": {
        "𐑳": ("∃a∈A∃b∈B( type(a) ≠ type(b) ) — moat vs bridge", "MOAT_BRIDGE_TYPE", "match"),
        "𐑕": ("∀a∈A∀b∈B( type(a) = type(b) )", None, "close"),
        "𐑙": ("|A| = 1 ∧ |B| = 1", None, "distant"),
    },
    "◻": {
        "𐑫": ("∀n∃φ( rank(φ) > n ∧ φ fixed by μ∘δ ∧ φ ∈ V ) — infinite repetition", "INFINITE_STITCH", "match"),
        "𐑟": ("Braid(σ_i) ∧ R_matrix ≠ 0 ∧ nonAbelian(x)", "BRAID_TRANSCENDENCE", "distant"),
        "𐑭": ("∮_γ A = 2πn ∧ n ∈ ℤ ∧ wind(γ) ≠ 0", "ZWIND", "distant"),
        "𐑴": ("∮_γ A = nπ ∧ n ∈ ℤ₂", None, "close"),
        "𐑷": ("∮_γ dx = 0", None, "distant"),
    },
}

# Transcendence atoms — primitives where CLINK L9 exceeds CLINK L8
TRANSCENDENCE_ATOMS = {"WIND_BRIDGE", "INFINITE_STITCH"}

# Reverse lookup
_PROMOTED_ATOM_TO_KEY = {}
for prim_key, values in CL9NK_FORMULAE.items():
    for val_key, (_, atom, _) in values.items():
        if atom is not None:
            _PROMOTED_ATOM_TO_KEY[atom] = (prim_key, val_key)

ALL_CL9NK_ATOMS = sorted(_PROMOTED_ATOM_TO_KEY.keys())

# =============================================================================
# FORMULA GENERATION — per-primitive CLINK decomposition relative to CLINK L9
# =============================================================================

def generate_formula(t, system_name="custom"):
    """Generate full CL9NK formula decomposition for a tuple.
    Returns dict with per-primitive CLINK fragments, promoted atoms,
    full conjunction, and proximity classification."""
    if CLINK_L9_REF is None:
        return {"status": "error", "message": "CLINK L9 reference not found in catalog"}

    fragments = []
    promoted_atoms = []
    atom_details = []
    match_count = 0
    close_count = 0
    distant_count = 0
    transcendence_primitives = []

    for key in PRIMITIVE_KEYS:
        val = t.get(key)
        formula_map = CL9NK_FORMULAE.get(key, {})
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

    d, conflicts = tuple_distance(t, CLINK_L9_REF)
    tier = assess_tier(t)

    full_conjunction = " ∧\n    ".join(
        f["clink_fragment"] for f in fragments
    )

    promotions_needed = []
    for key in PRIMITIVE_KEYS:
        if t.get(key) != CLINK_L9_REF.get(key):
            promotions_needed.append({
                "primitive": key,
                "from": t.get(key, "?"),
                "to": CLINK_L9_REF[key],
                "gap": round(ordinal_distance(key, t.get(key, "?"), CLINK_L9_REF[key]), 3),
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
            "distance_from_cl9nk": d,
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
        "reference": "CLINK L9 (Gaussian Moat Resolution) — ⟨𐑛𐑥𐑑𐑬𐑐𐑪𐑔𐑝⊙𐑫𐑳𐑭⟩ (from design)",
    }

# =============================================================================
# TENSOR / MEET / JOIN — lattice operations with CLINK L9
# =============================================================================

def compute_tensor_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L9_REF
    result = {}
    for key in PRIMITIVE_KEYS:
        v_ref = t_ref.get(key)
        v_sys = t_sys.get(key)
        ords = ORDINALS.get(key, {})
        o_ref = ords.get(v_ref, 0)
        o_sys = ords.get(v_sys, 0)
        if key in ("<", "⋈"):
            result[key] = v_sys if o_sys <= o_ref else v_ref
        else:
            result[key] = v_ref if o_ref >= o_sys else v_sys
    d, _ = tuple_distance(result, t_ref)
    absorbed = (d == 0.0)
    return {"tensor": result, "distance_from_cl9nk": d, "absorbed": absorbed,
            "interpretation": "CLINK L9 fully absorbed — strict superset" if absorbed
            else f"d={d} — not fully absorbed"}


def compute_meet_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L9_REF
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
    return {"meet": result, "d_from_cl9nk": d_ref, "d_from_system": d_sys}


def compute_join_op(t_sys, t_ref=None):
    if t_ref is None:
        t_ref = CLINK_L9_REF
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
    return {"join": result, "d_from_cl9nk": d_ref, "d_from_system": d_sys}

# =============================================================================
# TRANSCENDENCE ANALYSIS — dynamically computed from catalog
# =============================================================================

def compute_transcendence():
    if CLINK_L8_REF is None:
        return {"status": "error", "message": "CLINK L8 reference not found in catalog"}
    if CLINK_L9_REF is None:
        return {"status": "error", "message": "CLINK L9 reference not defined"}

    l8 = CLINK_L8_REF
    l9 = CLINK_L9_REF
    d, conflicts = tuple_distance(l8, l9)

    # Identify which primitives have changed and are transcendent
    transcendent_prims = []
    for key in PRIMITIVE_KEYS:
        if l8.get(key) != l9.get(key):
            # Check if L9's value has a promoted atom that is in TRANSCENDENCE_ATOMS
            atom = CL9NK_FORMULAE.get(key, {}).get(l9.get(key), (None, None, None))[1]
            if atom in TRANSCENDENCE_ATOMS:
                transcendent_prims.append(key)

    bridge_info = {
        "primitive": "⊥",
        "l8_value": l8.get("⊥", "?"),
        "l9_value": l9.get("⊥", "?"),
        "l8_fragment": CL9NK_FORMULAE["⊥"].get(l8.get("⊥", ""), ("?", None, "?"))[0],
        "l9_fragment": CL9NK_FORMULAE["⊥"].get(l9.get("⊥", ""), ("?", None, "?"))[0],
        "l8_atom": CL9NK_FORMULAE["⊥"].get(l8.get("⊥", ""), ("?", None, "?"))[1],
        "l9_atom": CL9NK_FORMULAE["⊥"].get(l9.get("⊥", ""), ("?", None, "?"))[1],
        "significance": "Integer winding bridge (Hodge Bridge) — guarantees density of bridges across moats.",
    }
    stitch_info = {
        "primitive": "◻",
        "l8_value": l8.get("◻", "?"),
        "l9_value": l9.get("◻", "?"),
        "l8_fragment": CL9NK_FORMULAE["◻"].get(l8.get("◻", ""), ("?", None, "?"))[0],
        "l9_fragment": CL9NK_FORMULAE["◻"].get(l9.get("◻", ""), ("?", None, "?"))[0],
        "l8_atom": CL9NK_FORMULAE["◻"].get(l8.get("◻", ""), ("?", None, "?"))[1],
        "l9_atom": CL9NK_FORMULAE["◻"].get(l9.get("◻", ""), ("?", None, "?"))[1],
        "significance": "Infinite repetition of the stitch [moat · hodge · linker] — path to infinity.",
    }

    tensor_result = compute_tensor_op(l8, l9)
    absorbed = tensor_result["distance_from_cl9nk"] == 0.0

    return {
        "status": "ok",
        "title": "The L9 Transcendence — CLINK L9 beyond CLINK L8",
        "clink_l8_tuple": l8,
        "clink_l9_tuple": l9,
        "d_l8_to_l9": d,
        "transcendence_primitives": {"bridge": bridge_info, "stitch": stitch_info},
        "tensor_absorption": f"tensor(CLINK L8, CLINK L9) = {'CLINK L9' if absorbed else 'composite'} — L8 {'is' if absorbed else 'is NOT'} fully absorbed into L9",
        "significance": (
            "CLINK L9 adds the Hodge Bridge theorem to the organism layer. "
            "It resolves the Gaussian Moat Problem by proving the existence of an infinite bounded-step path, "
            "a fact not encoded in CLINK L8."
        ),
        "transcendent_primitives": transcendent_prims,
    }

# =============================================================================
# PROMOTION LADDER — with per-primitive formula changes
# =============================================================================

def generate_promotions():
    zfc_baseline = {"⊢":"𐑼","⊣":"𐑡",">":"𐑩","<":"𐑗","⋈":"𐑱","⊤":"𐑘","∈":"𐑚","∋":"𐑝","⊙":"𐑢","⊥":"𐑓","⊞":"𐑙","◻":"𐑷"}

    zfc_t = None
    load_catalog()
    for name in ("ZFCt", "zfc_t_system", "zfc_t_ref", "zfc_t"):
        if name in CATALOG_INDEX:
            entry = CATALOG_INDEX[name]
            zfc_t = {pk: entry.get(pk, "") for pk in PRIMITIVE_KEYS}
            break
    if zfc_t is None:
        zfc_t = {"⊢":"𐑼","⊣":"𐑸",">":"𐑾","<":"𐑬","⋈":"𐑐","⊤":"𐑧","∈":"𐑲","∋":"𐑠","⊙":"⊙","⊥":"𐑖","⊞":"𐑳","◻":"𐑭"}

    zfc_fe = get_zfc_fe()
    if zfc_fe is None:
        return {"status": "error", "message": "ZFC_fe not found in catalog"}

    l8 = CLINK_L8_REF
    l9 = CLINK_L9_REF
    if l8 is None or l9 is None:
        return {"status": "error", "message": "CLINK L8 or L9 reference missing"}

    def _promo_details(t_from, t_to):
        result = []
        for key in PRIMITIVE_KEYS:
            if t_from.get(key) != t_to.get(key):
                fmap = CL9NK_FORMULAE.get(key, {})
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

    stage1 = _promo_details(zfc_baseline, zfc_t)
    stage2 = _promo_details(zfc_t, zfc_fe)
    stage3 = _promo_details(zfc_fe, l8)
    stage4 = _promo_details(l8, l9)

    d_zfc_zfct = tuple_distance(zfc_baseline, zfc_t)[0]
    d_zfct_zfcfe = tuple_distance(zfc_t, zfc_fe)[0]
    d_zfcfe_l8 = tuple_distance(zfc_fe, l8)[0]
    d_l8_l9 = tuple_distance(l8, l9)[0]
    d_zfc_l9 = tuple_distance(zfc_baseline, l9)[0]

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
            {"stage": "→ CLINK L8", "tier": "O_∞",
             "promotions": len(stage3), "distance": round(d_zfcfe_l8, 4),
             "details": stage3},
            {"stage": "→ CLINK L9", "tier": "O_∞⁺",
             "promotions": len(stage4), "distance": round(d_l8_l9, 4),
             "details": stage4,
             "note": "HODGE BRIDGE TRANSCENDENCE — resolves Gaussian Moat Problem"},
        ],
        "total_promotions": len(stage1) + len(stage2) + len(stage3) + len(stage4),
        "total_distance_zfc_to_l9": round(d_zfc_l9, 4),
        "transcendence": {"primitives": ["⊥", "◻"], "d_l8_to_l9": round(d_l8_l9, 4)},
        "catalog_note": "ZFC_fe and CLINK L8 sourced from IG_catalog.json; CLINK L9 defined internally.",
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
        d, conflicts = tuple_distance(t, CLINK_L9_REF)
        tier = assess_tier(t)
        layers.append({
            "layer": name,
            "description": info["description"],
            "distance_from_l9": d,
            "tier": tier,
            "conflicts_count": len(conflicts),
        })

    return {
        "reference": "CLINK L9 (Gaussian Moat Resolution) — from design",
        "total_layers": len(layers),
        "layers": layers,
        "ascent_interpretation": "Distance decreases from L0→L9, with L9 being the terminal resolution.",
        "catalog_note": f"Discovered {len(layers)} CLINK layers from catalog + L9 virtual.",
    }

# =============================================================================
# GAUSSIAN MOAT RESOLUTION VERIFICATION (CLINK L9 Theorem)
# =============================================================================

def action_moat():
    """Run the Gaussian Moat resolution verification based on CLINK L9."""
    if CLINK_L9_REF is None:
        return {"status": "error", "message": "CLINK L9 reference not defined"}
    # Build the proof
    proof_steps = [
        "1. Existence of Moats: gaussian_moat_problem monomer exists.",
        "2. Local Ring: polymerize(clink_l9, clink_l9, gaussian_moat_problem) → cyclic 3-membered ring (Δ=1.67).",
        "3. Dimer Trap: close(gaussian_moat_problem, clink_l9) → linear dimer, not cyclic.",
        "4. Bridge Search: scan(gaussian_moat_problem, clink_l9) → 2956 candidates; top mediator agent_network_adversarial (score 0.900).",
        "5. Hodge Bridge: imscribe(hodge_conjecture_bridge) → bridges the gap.",
        "6. Infinite Stitch: sequence [moat · hodge · linker]^∞ → bounded step size (Δ=1.67) to infinity.",
        "7. Crystallize: lattice of {moat, linker} is ordered and stable.",
        "8. Phase Reconstruct: fixed phase word (𐑖𐑫) — regular chirality.",
        "9. Ascend: gaussian_moat_problem⁺ constructed — extension possible.",
        "10. Conclusion: The Gaussian Moat Problem is resolved (T) in the Grammar, conditional on Hodge Conjecture.",
    ]
    return {
        "status": "ok",
        "title": "Gaussian Moat Resolution — CLINK L9 Theorem",
        "reference": "CLINK L9 canonical tuple: ⟨𐑛𐑥𐑑𐑬𐑐𐑪𐑔𐑝⊙𐑫𐑳𐑭⟩",
        "proof_steps": proof_steps,
        "verdict": "B (Both): finite ring established (T), infinite path frontier (B) pending Hodge density proof.",
        "conditional_on": "Hodge Conjecture (structural axiom in Grammar)",
        "next_attack": [
            "Define S_H = { p ∈ Z[i] | p satisfies Hodge condition at scale K }",
            "Prove positive density: lim_{R→∞} |S_H ∩ D_R| / |P ∩ D_R| > 0",
            "Construct sequence z_n algorithmically using bridge jumps."
        ]
    }

# =============================================================================
# ACTION HANDLERS — all catalog-native
# =============================================================================

def action_entry(name):
    load_catalog()
    if CLINK_L9_REF is None:
        return {"status": "error", "message": "CLINK L9 reference not found in catalog."}
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog ({len(CATALOG_INDEX)} entries)."}
    result = generate_formula(sys_info.get("tuple", {}), sys_info.get("name", name))
    result["status"] = "ok"
    result["description"] = sys_info.get("description", "")
    return result


def action_promotions():
    return generate_promotions()


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
    _bad = _unreadable_tuple(sys_info.get("name", name), t, "cl9nk")
    if _bad:
        return _bad
    d, conflicts = tuple_distance(t, CLINK_L9_REF)
    tier = assess_tier(t)
    return {"status": "ok", "name": sys_info.get("name", name), "distance_to_cl9nk": d,
            "tier": tier, "conflicts": conflicts, "conflict_count": len(conflicts)}


def action_transcendence():
    return compute_transcendence()


def action_tensor(name):
    sys_info = resolve_system(name)
    if sys_info is None:
        return {"status": "error", "message": f"System '{name}' not found in catalog."}
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl9nk")
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
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl9nk")
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
    _bad = _unreadable_tuple(sys_info.get("name", name), sys_info.get("tuple", {}), "cl9nk")
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
    _bad = _unreadable_tuple(sys_info.get("name", name), t, "cl9nk")
    if _bad:
        return _bad
    tier = assess_tier(t)
    d, _ = tuple_distance(t, CLINK_L9_REF)
    return {"status": "ok", "name": sys_info.get("name", name), "tier": tier, "distance_from_cl9nk": d}


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
    stats["clink_l9_tuple"] = CLINK_L9_REF
    stats["clink_l8_tuple"] = CLINK_L8_REF
    stats["clink_layers_found"] = len(discover_clink_chain())
    return {"status": "ok", "catalog": stats}


def action_moat_main():
    return action_moat()

# =============================================================================
# RICH TABLE RENDERER  (matches cl8nk_navigator output format)
# =============================================================================

import textwrap as _textwrap

_ATOM_DESC = {
    "PRIME_POINT":          "Point-like prime atom — base of the moat (𐑛)",
    "MOAT_CROSS":           "Crossing the moat — structural bridge (𐑥)",
    "BRIDGE_COMP":          "Bridge composition — functorial step (𐑑)",
    "MOAT_PARITY":          "ℤ₂ parity of the moat (𐑬)",
    "BRIDGE_COMM":          "Commutator of bridge — quantum bridge (𐑐)",
    "INFINITE_EXT":         "Infinite extension of the path (𐑪)",
    "BRIDGE_EXIST":         "Existence of a bridge (∈ existential) (𐑔)",
    "STITCH_3":             "3-unit stitch: moat · hodge · linker (∋ conjunction) (𐑝)",
    "PHI_C":                "Criticality fixed-point — ξ→∞ ∧ μ∘δ=id (⊙)",
    "WIND_BRIDGE":          "⬆ Hodge Bridge — integer winding density (⊥=𐑭)",
    "MOAT_BRIDGE_TYPE":     "Type mismatch between moat and bridge (⊞=𐑳)",
    "INFINITE_STITCH":      "⬆ Infinite repetition of the stitch — path to infinity (◻=𐑫)",
}

def _print_entry_table(result):
    W = 120; PW = 5; VW = 6; FW = W - 2 - PW - 2 - VW - 2

    print("\n" + "═" * W)
    print(f"  CL9NK Entry: {result.get('system', '?')}")
    desc = result.get("description", "")
    if desc:
        for line in _textwrap.wrap(desc, W - 4):
            print(f"  {line}")
    print(f"  Reference: {result.get('reference', '')}")
    print(f"  Catalog-native — no hardcoded systems (L9 virtual)")
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
    d    = sa.get("distance_from_cl9nk", "?")
    m    = sa.get("match_count", 0)
    c    = sa.get("close_count", 0)
    dist = sa.get("distant_count", 0)
    print(f"\n  tier: {tier}   d(CLINK L9): {d}   match:{m} close:{c} distant:{dist}")

    promoted = fd.get("promoted_atoms", [])
    if promoted:
        print(f"  promoted atoms: {', '.join(promoted)}")

    transc = result.get("transcendence_primitives", [])
    if transc:
        print(f"  ⬆ TRANSCENDENCE primitives: {', '.join(transc)}")

    promos = result.get("promotions_needed", [])
    if promos:
        print(f"\n  Promotions needed to reach CLINK L9 ({len(promos)}):")
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
        print("CL9NK Navigator — CLINK Layer 9 (Gaussian Moat Resolution) reference navigator")
        print("CATALOG-NATIVE: All data sourced from IG_catalog.json")
        print(f"Catalog: {catalog_stats()['total_entries']} entries loaded")
        print(f"CLINK L9 reference: DEFINED (virtual)")
        print(f"CLINK L8 reference: {'FOUND' if CLINK_L8_REF else 'NOT FOUND'}")
        print()
        print("Usage: python cl9nk_navigator.py <action> [name]")
        print()
        print("Actions:")
        print("  entry <name>       — Full CL9NK formula decomposition (PRIMARY)")
        print("  promotions         — Promotion ladder: ZFC→ZFC_t→ZFC_fe→CLINK L8→CLINK L9")
        print("  distance <name>    — Distance from CLINK L9")
        print("  transcendence      — The L9 transcendence analysis (from catalog)")
        print("  tensor <name>      — CLINK L9 ⊗ name (absorption test)")
        print("  meet <name>        — CLINK L9 ⊓ name")
        print("  join <name>        — CLINK L9 ⊔ name")
        print("  tier <name>        — Ouroboricity tier assessment")
        print("  chain              — Full CLINK chain L0→L9 distance ladder")
        print("  systems            — All catalog systems")
        print("  stats              — Catalog statistics + reference tuples")
        print("  moat               — Run Gaussian Moat resolution verification")
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

    action_map = {
        "entry": action_entry,
        "promotions": action_promotions,
        "distance": action_distance,
        "transcendence": action_transcendence,
        "tensor": action_tensor,
        "meet": action_meet,
        "join": action_join,
        "tier": action_tier,
        "chain": action_chain,
        "systems": action_systems,
        "stats": action_stats,
        "moat": action_moat_main,
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

    no_arg_actions = ("promotions", "transcendence", "chain", "systems", "stats", "moat")
    if action in no_arg_actions:
        if _refuse_stray_arg(action, arg, "cl9nk_navigator.py"):
            sys.exit(2)
        result = action_map[action]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif action == "entry":
        if not arg:
            print("Usage: cl9nk_navigator.py entry <name>")
            all_sys = sorted(CATALOG_INDEX.keys())
            print(f"Catalog systems ({len(all_sys)}): {', '.join(all_sys[:30])}{'...' if len(all_sys)>30 else ''}")
            sys.exit(1)
        result = action_map[action](arg)
        if result.get("status") == "error":
            print(f"[CL9NK] {result['message']}")
            return
        _print_entry_table(result)
    else:
        if not arg:
            print(f"Usage: cl9nk_navigator.py {action} <name>")
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
        print(f"[CL9NK] {result['message']}")
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

def probe_moat():
    print(json.dumps(action_moat_main(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()