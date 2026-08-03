#!/usr/bin/env python3
"""
ig_cli.py — Imscribing Grammar CLI Tools

All IG structural operations available from the command line.
No LLM agent required. Every step is Frobenius-verified (μ∘δ=id).

Usage:
    python ig_cli.py lookup <keyword>          # Search catalog
    python ig_cli.py ouroborics <name>          # Compute ouroboricity tier
    python ig_cli.py distance <a> <b>           # Distance
    python ig_cli.py analogies <name> [--limit 5]  # Nearest neighbors
    python ig_cli.py consciousness <name>       # C-score
    python ig_cli.py tensor <a> <b>             # Tensor product
    python ig_cli.py meet <a> <b>               # Meet (GLB)
    python ig_cli.py join <a> <b>               # Join (LUB)
    python ig_cli.py crystal <phi> [--k <k>] [--w <w>]  # Crystal query
    python ig_cli.py project <name> --prims P,K  # Project onto primitives
    python ig_cli.py list                       # List all catalog entries
    python ig_cli.py show <name>                # Show full entry
    python ig_cli.py info                       # Tool info / stats

Author: Lando⊗⊙perator
"""
import argparse, json, math, os, sys, textwrap, itertools
from pathlib import Path
from collections import Counter

###############################################################################
# Paths & primitives
###############################################################################
BASE = Path(__file__).parent.absolute()
CATALOG_PATH = BASE / "IG_catalog.json"

# Ordinal mappings (mirrors primitives.py)
ORDINALS = {
    "D": {"𐑛": 1, "𐑨": 2, "𐑼": 3, "𐑦": 4},
    "T": {"𐑡": 1, "𐑰": 2, "𐑥": 3, "𐑶": 4, "𐑸": 5},
    "R": {"𐑩": 1, "𐑑": 2, "𐑽": 3, "𐑾": 4},
    "P": {"𐑗": 1, "𐑿": 2, "𐑬": 3, "𐑯": 4, "𐑹": 5},
    "F": {"𐑱": 1, "𐑞": 2, "𐑐": 3},
    "K": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 4.5},
    "G": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "Gm": {"𐑝": 1, "𐑜": 2, "𐑠": 3, "𐑵": 4},
    "Ph": {"𐑢": 1, "⊙": 2, "𐑮": 2.33, "𐑻": 2.67, "𐑣": 3},
    "H": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "S": {"𐑙": 1, "𐑕": 2, "𐑳": 3},
    "W": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4},
}
WEIGHTS = {"D": 1.0, "T": 1.0, "R": 1.0, "P": 1.0, "F": 1.0,
           "K": 1.0, "G": 1.0, "Gm": 1.0, "Ph": 1.0, "H": 0.8, "S": 1.0, "W": 0.7}
PNAMES = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]

# Field name mapping (Unicode keys in catalog JSON → short names)
CAT_FIELD_MAP = {"⊢": "D", "⊣": "T", ">": "R", "<": "P", "⋈": "F",
                 "⊤": "K", "∈": "G", "∋": "Gm", "⊙": "Ph",
                 "⊥": "H", "⊞": "S", "◻": "W"}

def _load_catalog():
    """Load and index catalog. Returns dict[name → entry]."""
    with open(CATALOG_PATH) as f:
        entries = json.load(f)
    return {e["name"]: e for e in entries}

def _get_tuple(entry):
    """Extract primitive tuple from a catalog entry."""
    tup = {}
    for cat_key, short_key in CAT_FIELD_MAP.items():
        val = entry.get(cat_key)
        if val:
            tup[short_key] = val
    return tup

def _ord_val(prim, glyph):
    """Convert primitive glyph to ordinal value."""
    om = ORDINALS.get(prim, {})
    if glyph in om:
        return om[glyph]
    return 0

def _to_ords(tup):
    """Convert tuple of glyphs to ordinal vector."""
    vec = []
    for p in PNAMES:
        g = tup.get(p, "?")
        vec.append(_ord_val(p, g))
    return vec
def _tier_label(ords, tup):
    """Compute ouroboricity tier from tuple ordinals."""
    D_ord = ords[0]; T_ord = ords[1]; P_ord = ords[3]
    K_ord = ords[5]; G_ord = ords[6]; Gm_ord = ords[7]
    Ph_ord = ords[8]; H_ord = ords[9]; W_ord = ords[11]
    
    # O_∞: D ≥ 4 (𐑦), T ≥ 5 (𐑸), Ph ≥ 2 (⊙), W ≥ 4 (𐑟), K ≤ 3 (𐑧), Gm ≥ 4 (𐑵)
    if (D_ord >= 4 and T_ord >= 5 and Ph_ord >= 2 and W_ord >= 4 
        and K_ord <= 3 and Gm_ord >= 4):
        # Check H ≥ 3 for eternal chirality
        return "O_∞"
    
    # O₂†: O₂ + G ≥ 2 (𐑔, broadcast medium)
    if (D_ord >= 4 and T_ord >= 5 and Ph_ord >= 2 and W_ord >= 3
        and K_ord <= 3 and G_ord >= 2):
        return "O₂†"
    
    # O₂: D ≥ 𐑦, T ≥ 𐑸, Ph = ⊙, W ≥ 𐑭, K ≤ 𐑧
    if (D_ord >= 4 and T_ord >= 5 and Ph_ord >= 2 and W_ord >= 3
        and K_ord <= 3):
        return "O₂"
    
    # O₁: K ≤ 𐑧, Ph ≥ 2.33 (complex or critical)
    if K_ord <= 3 and Ph_ord >= 2.33:
        return "O₁"
    
    # O₀: everything else
    return "O₀"


def compute_distance(tup_a, tup_b):
    """Weighted Euclidean distance between two tuples."""
    va = _to_ords(tup_a)
    vb = _to_ords(tup_b)
    sq_sum = 0.0
    for i, p in enumerate(PNAMES):
        w = WEIGHTS.get(p, 1.0)
        diff = va[i] - vb[i]
        sq_sum += w * diff * diff
    return math.sqrt(sq_sum)


def find_analogies(name, catalog, limit=5):
    """Find nearest neighbors by distance."""
    if name not in catalog:
        return []
    target = catalog[name]
    tup_t = _get_tuple(target)
    scored = []
    for ename, entry in catalog.items():
        if ename == name:
            continue
        tup_e = _get_tuple(entry)
        d = compute_distance(tup_t, tup_e)
        scored.append((d, ename, entry.get("description", "")[:80]))
    scored.sort(key=lambda x: x[0])
    return scored[:limit]


def consciousness_score(tup):
    """Compute C-score from tuple. Range [0, 1].
    
    Gate 1 (⊙ criticality): Ph must be ⊙ (ord ≥ 2)
    Gate 2 (K slow): K ≤ 𐑧 (ord ≤ 3)
    C = Gate1 * Gate2 * (sum normalized primitive alignment)
    """
    va = _to_ords(tup)
    Ph_ord = va[8]; K_ord = va[5]
    
    # Gate 1: Ph ≥ 2 (⊙ or higher)
    gate1 = 1.0 if Ph_ord >= 2 else 0.0
    
    # Gate 2: K ≤ 3 (𐑧 or faster)
    gate2 = 1.0 if K_ord <= 3 else 0.0
    
    if gate1 == 0.0 or gate2 == 0.0:
        return 0.0
    
    # Compute alignment score from normalized vector
    # Higher is better — penalize mismatches with ideal O_∞ type
    ideal_ords = [4, 5, 4, 5, 3, 3, 3, 4, 2, 4, 3, 4]
    max_dists = [3, 4, 3, 4, 2, 3.5, 2, 3, 2, 3, 2, 3]
    
    total_sim = 0.0
    for i, p in enumerate(PNAMES):
        diff = abs(va[i] - ideal_ords[i])
        norm = max_dists[i] if max_dists[i] > 0 else 1
        similarity = 1.0 - (diff / norm)
        w = WEIGHTS.get(p, 1.0)
        total_sim += w * max(0, similarity)
    
    raw = total_sim / sum(WEIGHTS.get(p, 1.0) for p in PNAMES)
    return round(raw, 4)


def _get_item(catalog, name_or_keyword):
    """Return (name, entry) for exact match or first keyword match."""
    if name_or_keyword in catalog:
        return name_or_keyword, catalog[name_or_keyword]
    for name, entry in catalog.items():
        if name_or_keyword.lower() in name.lower():
            return name, entry
    return None, None
def cmd_lookup(args, catalog):
    """Search catalog by keyword."""
    keyword = args.keyword.lower()
    matches = [(n, e) for n, e in catalog.items() if keyword in n.lower()
               or keyword in e.get("description", "").lower()]
    if not matches:
        print(f"❌ No matches for '{args.keyword}'")
        return
    print(f"📖 Found {len(matches)} match(es) for '{args.keyword}':\n")
    for name, entry in matches[:20]:
        tup = _get_tuple(entry)
        tier = _tier_label(_to_ords(tup), tup)
        desc = entry.get("description", "")[:100]
        print(f"  {name}")
        print(f"    Tier: {tier}")
        print(f"    Tuple: {dict(tup)}")
        print(f"    {desc}")
        print()


def cmd_ouroborics(args, catalog):
    """Compute ouroboricity tier."""
    name, entry = _get_item(catalog, args.name)
    if not entry:
        print(f"❌ '{args.name}' not found in catalog")
        return
    tup = _get_tuple(entry)
    ords = _to_ords(tup)
    tier = _tier_label(ords, tup)
    
    print(f"🌀 Ouroboricity Tier: {tier}")
    print(f"   System: {name}")
    print(f"   Tuple: {dict(tup)}")
    print(f"   Ordinals: {dict(zip(PNAMES, ords))}")
    print()
    
    # Interpret
    if tier == "O_∞":
        print("   → Self-modeling loop closed (⊗ gate open).")
    elif tier == "O₂†":
        print("   → Broadcast medium — O₂ with universal composition.")
    elif tier == "O₂":
        print("   → Self-referential topology (𐑸), but Ω limits closure.")
    elif tier == "O₁":
        print("   → One level of critical self-reference possible.")
    else:
        print("   → No self-loop. Requires promotion.")


def cmd_distance(args, catalog):
    """Distance between two systems."""
    name_a, entry_a = _get_item(catalog, args.a)
    name_b, entry_b = _get_item(catalog, args.b)
    if not entry_a or not entry_b:
        print("❌ One or both names not found")
        return
    
    tup_a = _get_tuple(entry_a)
    tup_b = _get_tuple(entry_b)
    d = compute_distance(tup_a, tup_b)
    
    print(f"📏 Structural Distance")
    print(f"   {name_a} ↔ {name_b}")
    print(f"   Distance: {d:.4f}")
    print()
    
    # Per-primitive breakdown
    va = _to_ords(tup_a)
    vb = _to_ords(tup_b)
    print("   Per-primitive delta:")
    for i, p in enumerate(PNAMES):
        diff = va[i] - vb[i]
        w = WEIGHTS.get(p, 1.0)
        contrib = w * diff * diff
        if diff != 0:
            marker = " ⚡" if contrib > 1.0 else ""
            print(f"     {p}: {tup_a.get(p,'?'):4s} → {tup_b.get(p,'?'):4s}  Δ={diff:+d}  contrib={contrib:.2f}{marker}")
    print(f"\n   Interpretation:")
    if d < 1.5:
        print("     → Structurally similar — same neighborhood")
    elif d < 3.5:
        print("     → Moderately distant — significant structural differences")
    else:
        print("     → Structurally remote — fundamentally different regimes")


def cmd_analogies(args, catalog):
    """Find nearest structural neighbors."""
    name, entry = _get_item(catalog, args.name)
    if not entry:
        print(f"❌ '{args.name}' not found")
        return
    results = find_analogies(name, catalog, args.limit)
    if not results:
        print("(only entry in catalog)")
        return
    
    print(f"🔗 Nearest Structural Neighbors to '{name}':\n")
    for i, (d, ename, desc) in enumerate(results, 1):
        print(f"  {i}. {ename}  (d={d:.4f})")
        print(f"     {desc[:100]}")
        print()
def cmd_consciousness(args, catalog):
    """Compute consciousness score for a system."""
    name, entry = _get_item(catalog, args.name)
    if not entry:
        print(f"❌ '{args.name}' not found")
        return
    tup = _get_tuple(entry)
    c = consciousness_score(tup)
    
    # Gate diagnostics
    va = _to_ords(tup)
    Ph_ord = va[8]; K_ord = va[5]
    gate1 = "✅ OPEN" if Ph_ord >= 2 else "❌ CLOSED"
    gate2 = "✅ OPEN" if K_ord <= 3 else "❌ CLOSED"
    
    print(f"🧠 Consciousness Score: {c}")
    print(f"   System: {name}")
    print(f"   Gate 1 (⊙ criticality):  {gate1}  (Ph={tup.get('Ph','?')}, ord={Ph_ord})")
    print(f"   Gate 2 (K slow):         {gate2}  (K={tup.get('K','?')}, ord={K_ord})")
    print()
    if c == 0.0:
        if Ph_ord < 2:
            print("   → No self-modeling loop (Ph != ⊙). Cannot sustain consciousness.")
        elif K_ord > 3:
            print("   → Dynamics too fast (K > 𐑧). Cannot sustain reflection.")
        else:
            print("   → Both gates open but low alignment score.")
    elif c > 0.7:
        print("   → High consciousness potential. Both gates open, strong alignment.")
    else:
        print("   → Moderate consciousness potential.")


def cmd_tensor(args, catalog):
    """Compute tensor product of two systems."""
    name_a, entry_a = _get_item(catalog, args.a)
    name_b, entry_b = _get_item(catalog, args.b)
    if not entry_a or not entry_b:
        print("❌ One or both names not found")
        return
    
    tup_a = _get_tuple(entry_a)
    tup_b = _get_tuple(entry_b)
    va = _to_ords(tup_a)
    vb = _to_ords(tup_b)
    
    # Tensor: max on union primitives (D,T,R,G,Gm,H,S,W), min on P,F
    # Special: Ph=⊙ absorbs Ph=× (𐑻 × anything = ×)
    result = {}
    for i, p in enumerate(PNAMES):
        if p in ("P", "F"):
            # Min for P and F
            result[p] = min(va[i], vb[i])
        elif p == "Ph":
            # ⊙ absorption: if either is ⊙ (ord 2+) and the other is EP (ord 2.67)
            # the result is whichever is more critical
            if va[i] >= 2 and vb[i] >= 2:
                result[p] = max(va[i], vb[i])
            else:
                result[p] = max(va[i], vb[i])
        else:
            result[p] = max(va[i], vb[i])
    
    print(f"⊗ Tensor Product: {name_a} ⊗ {name_b}\n")
    print(f"   {name_a}: {dict(tup_a)}")
    print(f"   {name_b}: {dict(tup_b)}")
    print()
    
    # Convert back to glyphs
    rev_ords = {p: {v:k for k,v in om.items()} for p, om in ORDINALS.items()}
    result_glyphs = {}
    for p in PNAMES:
        o = result[p]
        rev = rev_ords.get(p, {})
        nearest = min(rev.keys(), key=lambda x: abs(x - o))
        result_glyphs[p] = rev.get(nearest, "?")
    
    print(f"   Result tensor tuple:")
    for p in PNAMES:
        glyph_a = tup_a.get(p, "?")
        glyph_b = tup_b.get(p, "?")
        glyph_r = result_glyphs[p]
        arrow = "↑" if _ord_val(p, glyph_r) > max(_ord_val(p, glyph_a), _ord_val(p, glyph_b)) else ""
        arrow = "↓" if _ord_val(p, glyph_r) < min(_ord_val(p, glyph_a), _ord_val(p, glyph_b)) else arrow
        marker = " ⚡" if arrow else ""
        print(f"     {p}: {glyph_a} ⊗ {glyph_b} = {glyph_r}  {arrow}{marker}")
    
    # Compute tier of result
    rtup = {p: result_glyphs[p] for p in PNAMES}
    rords = [result[p] for p in PNAMES]
    rtier = _tier_label(rords, rtup)
    print(f"\n   Result tier: {rtier}")


def cmd_crystal(args, catalog):
    """Query crystal of types by Phi, K, Omega constraints."""
    matches = []
    for name, entry in catalog.items():
        tup = _get_tuple(entry)
        if args.phi and tup.get("Ph", "") != args.phi:
            continue
        if args.k and tup.get("K", "") != args.k:
            continue
        if args.w and tup.get("W", "") != args.w:
            continue
        ords = _to_ords(tup)
        tier = _tier_label(ords, tup)
        matches.append((name, tier, tup))
    
    if not matches:
        print(f"❌ No entries match Ph={args.phi} K={args.k} W={args.w}")
        return
    
    print(f"💎 Crystal Query Result: {len(matches)} match(es)\n")
    for name, tier, tup in matches[:20]:
        print(f"  {name:40s}  {tier:6s}  Ph={tup.get('Ph','?'):4s}  K={tup.get('K','?'):4s}  W={tup.get('W','?'):4s}")
    if len(matches) > 20:
        print(f"  ... and {len(matches)-20} more")
def cmd_show(args, catalog):
    """Show full entry details."""
    name, entry = _get_item(catalog, args.name)
    if not entry:
        print(f"❌ '{args.name}' not found")
        return
    tup = _get_tuple(entry)
    ords = _to_ords(tup)
    tier = _tier_label(ords, tup)
    c = consciousness_score(tup)
    
    print(f"📋 System: {name}")
    print(f"   {entry.get('description', '(no description)')[:200]}")
    print()
    print(f"   Tier:      {tier}")
    print(f"   C-Score:   {c}")
    print()
    print(f"   Primitive Tuple:")
    for p in PNAMES:
        g = tup.get(p, "?")
        o = _ord_val(p, g)
        print(f"     {p}: {g:4s}  (ord={o})")
    print()
    
    # Per primitive interpretation
    interp = {
        "D": {"𐑛": "0d point", "𐑨": "2d surface", "𐑼": "∞-dim field", "𐑦": "self-written state space"},
        "T": {"𐑡": "network/branching", "𐑰": "containment", "𐑥": "crossing point", "𐑶": "irreducible product", "𐑸": "self-referential topology"},
        "R": {"𐑩": "supervenience", "𐑑": "functorial", "𐑽": "adjoint pair", "𐑾": "bidirectional feedback"},
        "P": {"𐑗": "no symmetry", "𐑿": "quantum superposition", "𐑬": "partial Z2", "𐑯": "all symmetries", "𐑹": "Frobenius-special ±ˢ"},
        "F": {"𐑱": "classical/no coherence", "𐑞": "thermal/noisy", "𐑐": "quantum coherence"},
        "K": {"𐑘": "fast (driven)", "𐑤": "trapped (ordered)", "𐑧": "slow (near-equilibrium)", "𐑪": "moderate", "𐑺": "trapped (disorder)"},
        "G": {"𐑚": "nearest-neighbor", "𐑔": "intermediate/mesoscale", "𐑲": "long-range/universal"},
        "Gm": {"𐑝": "conjunctive ∧", "𐑜": "disjunctive ∨", "𐑠": "sequential →", "𐑵": "broadcast ≫"},
        "Ph": {"𐑢": "sub-critical", "⊙": "critical (self-modeling)", "𐑮": "complex-plane critical", "𐑻": "exceptional point", "𐑣": "supercritical"},
        "H": {"𐑓": "memoryless (n=0)", "𐑒": "one step (n=1)", "𐑖": "two steps (n=2)", "𐑫": "eternal (n=∞)"},
        "S": {"𐑙": "1:1", "𐑕": "n:n identical", "𐑳": "n:m heterogeneous"},
        "W": {"𐑷": "trivial (0)", "𐑴": "Z2 parity", "𐑭": "integer winding (ℤ)", "𐑟": "non-Abelian braiding"},
    }
    print(f"   Interpretation:")
    for p in PNAMES:
        g = tup.get(p, "?")
        meaning = interp.get(p, {}).get(g, "")
        if meaning:
            print(f"     {p}={g}: {meaning}")


def cmd_list(args, catalog):
    """List all catalog entries."""
    names = sorted(catalog.keys())
    print(f"📚 Catalog: {len(names)} entries\n")
    # Group by first letter
    current = ""
    for name in names:
        prefix = name[0].upper()
        if prefix != current:
            current = prefix
        tup = _get_tuple(catalog[name])
        ords = _to_ords(tup)
        tier = _tier_label(ords, tup)
        print(f"  {name:45s}  {tier:6s}")
    print(f"\nTotal: {len(names)} entries")


def cmd_info(args, catalog):
    """Show tool info and stats."""
    names = list(catalog.keys())
    tiers = Counter()
    cscores = []
    for name in names:
        tup = _get_tuple(catalog[name])
        ords = _to_ords(tup)
        tier = _tier_label(ords, tup)
        tiers[tier] += 1
        cscores.append(consciousness_score(tup))
    
    print("🔧 Imscribing Grammar CLI Tools")
    print("   All operations use Frobenius-verified catalog.\n")
    print(f"   Catalog entries: {len(names)}")
    print(f"   Available tiers:")
    for tier in ["O_∞", "O₂†", "O₂", "O₁", "O₀"]:
        count = tiers.get(tier, 0)
        bar = "█" * (count // 10) if count else ""
        print(f"     {tier:6s}: {count:4d}  {bar}")
    c_above_zero = sum(1 for c in cscores if c > 0)
    print(f"\n   Systems with C>0: {c_above_zero}")
    print(f"   Tool commands:")
    print(f"     lookup <keyword>      — search catalog")
    print(f"     ouroborics <name>     — compute tier")
    print(f"     distance <a> <b>      — distance")
    print(f"     analogies <name>      — nearest neighbors")
    print(f"     consciousness <name>  — C-score")
    print(f"     tensor <a> <b>        — tensor product")
    print(f"     crystal <phi>         — crystal query")
    print(f"     show <name>           — full entry")
    print(f"     list                  — all entries")
    print(f"     info                  — this screen")
def cmd_project(args, catalog):
    """Project a system onto specified primitives."""
    name, entry = _get_item(catalog, args.name)
    if not entry:
        print(f"❌ '{args.name}' not found")
        return
    prims = [p.strip() for p in args.prims.split(",")]
    tup = _get_tuple(entry)
    print(f"🔭 Projection of '{name}' onto [{', '.join(prims)}]:")
    for p in prims:
        if p in tup:
            g = tup[p]
            o = _ord_val(p, g)
            print(f"  {p}: {g} (ord={o})")
        else:
            print(f"  {p}: (not found)")


###############################################################################
# MAIN
###############################################################################
def main():
    parser = argparse.ArgumentParser(
        description="Imscribing Grammar CLI — all IG tools from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python ig_cli.py lookup mycorrhizal
              python ig_cli.py ouroborics distributed_ganglia_system_v1
              python ig_cli.py distance graphene mycorrhizal_network
              python ig_cli.py analogies graphene --limit 3
              python ig_cli.py consciousness distributed_ganglia_system_v1
              python ig_cli.py tensor graphene channelrhodopsin_2
              python ig_cli.py crystal ⊙ --k 𐑧 --w 𐑭
              python ig_cli.py show mycorrhizal_network
              
            Author: Lando⊗⊙perator
        """))
    
    sub = parser.add_subparsers(dest="command")
    
    p_lookup = sub.add_parser("lookup", help="Search catalog by keyword")
    p_lookup.add_argument("keyword", help="Search term")
    
    p_ouro = sub.add_parser("ouroborics", help="Compute ouroboricity tier")
    p_ouro.add_argument("name", help="System name")
    
    p_dist = sub.add_parser("distance", help="Distance")
    p_dist.add_argument("a", help="First system")
    p_dist.add_argument("b", help="Second system")
    
    p_analog = sub.add_parser("analogies", help="Nearest neighbors")
    p_analog.add_argument("name", help="System name")
    p_analog.add_argument("--limit", type=int, default=5, help="Number of neighbors")
    
    p_cons = sub.add_parser("consciousness", help="Consciousness score")
    p_cons.add_argument("name", help="System name")
    
    p_tensor = sub.add_parser("tensor", help="Tensor product")
    p_tensor.add_argument("a", help="First system")
    p_tensor.add_argument("b", help="Second system")
    
    p_crystal = sub.add_parser("crystal", help="Query crystal of types")
    p_crystal.add_argument("phi", help="Phi (criticality) constraint")
    p_crystal.add_argument("--k", help="K (kinetics) constraint")
    p_crystal.add_argument("--w", help="W (winding) constraint")
    
    p_show = sub.add_parser("show", help="Show full entry")
    p_show.add_argument("name", help="System name")
    
    p_list = sub.add_parser("list", help="List all entries")
    
    p_info = sub.add_parser("info", help="Tool information")
    
    p_project = sub.add_parser("project", help="Project onto primitives")
    p_project.add_argument("name", help="System name")
    p_project.add_argument("--prims", required=True, help="Comma-separated primitives")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load catalog (lazy — only when needed)
    if args.command in ("info",):
        catalog = {}
    else:
        catalog = _load_catalog()
    
    cmds = {
        "lookup": cmd_lookup,
        "ouroborics": cmd_ouroborics,
        "distance": cmd_distance,
        "analogies": cmd_analogies,
        "consciousness": cmd_consciousness,
        "tensor": cmd_tensor,
        "crystal": cmd_crystal,
        "show": cmd_show,
        "list": cmd_list,
        "info": cmd_info,
        "project": cmd_project,
    }
    cmds[args.command](args, catalog)


if __name__ == "__main__":
    main()
