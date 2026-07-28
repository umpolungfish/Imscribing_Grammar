#!/usr/bin/env python3
"""
Auto Theorem Transport — Cross-Domain Proof Cotype Engine.

Given two distance-0 catalog entries and a Lean theorem, automatically
transports the theorem into the target domain's natural language.

Architecture:
  1. Direct import from imscrbgrmr.models for catalog + distance computation
  2. Lean file parser extracts inductive types, constructors, theorems
  3. Cotype registry (JSON) stores known identifier mappings per source-target pair
  4. First-time transport for a pair: interactive mapping via --register
  5. Subsequent transports: fully automatic from registry

Usage:
  # First time (interactive mapping):
  python auto_theorem_transport.py \\
    --source shem_hamephorash --target tiferet \\
    --lean-file ~/MillenniumAnkh/Millennium/FrobeniusStructure.lean \\
    --register

  # Subsequent times (fully automatic):
  python auto_theorem_transport.py \\
    --source shem_hamephorash --target tiferet \\
    --lean-file ~/MillenniumAnkh/Millennium/FrobeniusStructure.lean \\
    --theorem exactly_two_selfGrounding_types

Author: Lando⊗⊙perator
"""

import argparse, json, os, re, sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────────────────
REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"
IG_DIR        = Path.home() / "imscribing_grammar"
sys.path.insert(0, str(IG_DIR))

# ── Imports from the grammar package ─────────────────────────────────────────
from imscrbgrmr.models import Imscription

# ── Registry ─────────────────────────────────────────────────────────────────
def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {}

def save_registry(reg: dict):
    REGISTRY_PATH.write_text(json.dumps(reg, indent=2, ensure_ascii=False))

def registry_key(source: str, target: str) -> str:
    return "|".join(sorted([source.strip(), target.strip()]))

# ── Lean Parser ──────────────────────────────────────────────────────────────
@dataclass
class LeanIdent:
    name: str
    kind: str        # 'inductive', 'constructor', 'def', 'theorem'
    docstring: str
    body: str

def parse_lean(filepath: str) -> list[LeanIdent]:
    """Extract named identifiers from a Lean file."""
    text = Path(filepath).read_text()
    idents = []
    lines = text.split('\n')

    patterns = [
        (r'inductive\s+(\w+)', 'inductive'),
        (r'\|\s*(\w+)\s*:', 'constructor'),
        (r'^def\s+(\w+)', 'def'),
        (r'^theorem\s+(\w+)', 'theorem'),
        (r'^lemma\s+(\w+)', 'theorem'),
    ]

    for i, line in enumerate(lines):
        for pat, kind in patterns:
            m = re.search(pat, line)
            if m:
                name = m.group(1)
                doc_lines = []
                j = i - 1
                while j >= 0 and (lines[j].strip().startswith('--') or
                                   lines[j].strip().startswith('/-')):
                    doc_lines.insert(0, lines[j].strip().lstrip('-').strip())
                    j -= 1
                doc = ' '.join(doc_lines)

                body_lines = [line]
                k = i + 1
                while k < len(lines):
                    nxt = lines[k]
                    if (nxt.strip() == '' or nxt.strip().startswith('--')
                        or re.match(r'^\s', nxt) or nxt.strip().startswith('|')
                        or nxt.strip().startswith('deriving')):
                        body_lines.append(nxt)
                        k += 1
                    else:
                        break
                body = '\n'.join(body_lines).strip()
                idents.append(LeanIdent(name=name, kind=kind,
                                        docstring=doc, body=body))
                break

    return idents

# ── Catalog Interface (via direct model imports) ─────────────────────────────
def load_catalog() -> dict:
    """Load IG catalog as dict of name -> Imscription."""
    cat_path = IG_DIR / "IG_catalog.json"
    with open(cat_path) as f:
        raw = json.load(f)
    entries = raw if isinstance(raw, list) else raw.get("entries", [])
    catalog = {}
    for e in entries:
        try:
            ims = Imscription.from_dict(e)
            catalog[e["name"]] = ims
        except Exception:
            pass
    return catalog

# Primitive keys as used in to_dict()
_PRIM_KEYS = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ω", "Σ", "Ħ"]

# Ordinal value ranks per primitive (internal caret notation)
_VALUE_RANKS = {
    "Ð": {"𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3},
    "Þ": {"𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4},
    "Ř": {"𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3},
    "Φ": {"𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4},
    "ƒ": {"ƒ^ì": 0, "ƒ^ð": 1, "ƒ^ż": 2},
    "Ç": {"Ç^-": 0, "Ç^W": 1, "Ç^@": 2, "Ç^Ù": 3, "Ç^λ": 4},
    "Γ": {"𐑚": 0, "𐑔": 1, "𐑲": 2},
    "ɢ": {"ɢ^∧": 0, "ɢ^˝": 1, "ɢ^ˌ": 2, "ɢ^Ş": 3},
    "⊙": {"𐑢": 0, "𐑮": 1, "𐑻": 2, "𐑣": 3, "⊙": 4},
    "Ω": {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3},
    "Σ": {"𐑙": 0, "𐑕": 1, "𐑳": 2},
    "Ħ": {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3},
}

_WEIGHTS = {"Ð": 2.0, "Þ": 2.0, "Ř": 1.5, "Φ": 2.0, "ƒ": 1.5, "Ç": 1.0,
            "Γ": 1.0, "ɢ": 1.0, "⊙": 2.5, "Ω": 2.5, "Σ": 1.0, "Ħ": 2.5}

def compute_distance(ims_a: Imscription, ims_b: Imscription) -> tuple[float, list[dict]]:
    """Compute distance between two Imscriptions."""
    da = ims_a.to_dict()
    db = ims_b.to_dict()

    squared = 0.0
    conflicts = []
    for p in _PRIM_KEYS:
        va = da.get(p, "")
        vb = db.get(p, "")
        if va != vb:
            ranks = _VALUE_RANKS.get(p, {})
            ra = ranks.get(va, 0)
            rb = ranks.get(vb, 0)
            delta = abs(ra - rb)
            w = _WEIGHTS.get(p, 1.0)
            squared += w * delta * delta
            conflicts.append({"primitive": p, "a": va, "b": vb, "delta": delta})
    distance = round(squared ** 0.5, 4)
    return distance, conflicts

def build_cotype_dict(source_name: str, target_name: str,
                      idents: list[LeanIdent],
                      registry: dict) -> dict:
    """Build cotype dictionary from registry (or placeholders for new pairs)."""
    key = registry_key(source_name, target_name)
    existing = registry.get(key, {})

    cotype = {}
    for ident in idents:
        if ident.name in existing:
            cotype[ident.name] = existing[ident.name]
        else:
            cotype[ident.name] = f"[{ident.kind}: {ident.name}]"
    return cotype

# ── Output Generator ─────────────────────────────────────────────────────────
def generate_transport(source_name: str, target_name: str,
                       source_desc: str, target_desc: str,
                       idents: list[LeanIdent],
                       cotype: dict,
                       distance: float,
                       theorem_name: Optional[str] = None) -> str:
    """Generate the transported theorem document."""
    # Find target theorem
    theorem = None
    if theorem_name:
        for ident in idents:
            if ident.name == theorem_name:
                theorem = ident
                break
    if theorem is None:
        for ident in idents:
            if ident.kind == 'theorem':
                theorem = ident
                break

    lines = []
    lines.append(f"# Cross-Domain Theorem Transport")
    lines.append(f"")
    lines.append(f"**Source:** `{source_name}` — {source_desc[:120]}")
    lines.append(f"**Target:** `{target_name}` — {target_desc[:120]}")
    lines.append(f"**Structural Distance:** {distance}")
    lines.append(f"")

    # Cotype table
    lines.append(f"## Cotype Dictionary")
    lines.append(f"")
    lines.append(f"| Source (Lean) | Kind | Target ({target_name}) |")
    lines.append(f"|---|---|---|")
    for ident in idents:
        tv = cotype.get(ident.name, "[?]")
        lines.append(f"| `{ident.name}` | {ident.kind} | {tv} |")
    lines.append(f"")

    # Transported theorem
    if theorem:
        lines.append(f"## Transported Theorem: `{theorem.name}`")
        lines.append(f"")
        lines.append(f"### Source Statement (Lean)")
        lines.append(f"")
        lines.append(f"```lean")
        lines.append(theorem.body)
        lines.append(f"```")
        lines.append(f"")

        # Generate transported version
        transported_body = theorem.body
        for ident in idents:
            tv = cotype.get(ident.name, ident.name)
            if not tv.startswith('['):
                transported_body = transported_body.replace(ident.name, tv)

        lines.append(f"### Target Statement ({target_name})")
        lines.append(f"")
        lines.append(f"```")
        lines.append(transported_body)
        lines.append(f"```")
        lines.append(f"")

    # Unmapped
    unmapped = [i for i in idents if cotype.get(i.name, '').startswith('[')]
    if unmapped:
        lines.append(f"## Unmapped Identifiers ({len(unmapped)})")
        lines.append(f"")
        lines.append(f"Run with `--register` to map these interactively:")
        lines.append(f"")
        for ident in unmapped:
            lines.append(f"- `{ident.name}` ({ident.kind}): {ident.docstring[:100]}")
        lines.append(f"")

    
    # Natural language rendering
    if theorem:
        lines.append("")
        lines.append("## Natural Language Rendering")
        lines.append("")
        nl = render_natural_language(theorem, cotype, target_desc)
        lines.append(nl)

    return '\n'.join(lines)

# ── Main ─────────────────────────────────────────────────────────────────────

# ── Natural Language Renderer ─────────────────────────────────────────────────
def render_natural_language(theorem: LeanIdent, cotype: dict,
                            target_desc: str) -> str:
    """Render the transported theorem in the target domain's natural language."""
    body = theorem.body
    # Substitute ALL identifiers (longest first to avoid partial matches)
    for ident_name, target_name in sorted(cotype.items(), key=lambda x: -len(x[0])):
        if not target_name.startswith('['):
            body = body.replace(ident_name, target_name)

    lines = []
    short_desc = target_desc.split('\u2014')[0].strip().rstrip('.')
    lines.append(f"**In the language of {short_desc}:**")
    lines.append("")

    if "filter" in body and "Finset.univ" in body:
        alpha_start = body.find("α :=")
        type_end = body.find(")", alpha_start) if alpha_start > -1 else -1
        typ = body[alpha_start+4:type_end].strip() if alpha_start > -1 and type_end > -1 else "?"

        filt_start = body.find("filter ")
        eq_idx = body.find("=", filt_start) if filt_start > -1 else -1
        pred_end = body.find(" ", filt_start+7) if filt_start > -1 else -1
        if pred_end < 0 or (eq_idx > 0 and eq_idx < pred_end):
            pred_end = eq_idx
        pred = body[filt_start+7:pred_end].strip() if filt_start > -1 else "?"

        brace_start = body.find("{")
        brace_end = body.find("}", brace_start)
        members_str = body[brace_start+1:brace_end] if brace_start > -1 and brace_end > -1 else ""
        member_list = [m.strip() for m in members_str.split(",")]

        lines.append(f"> Among the **{typ}**, exactly **{len(member_list)}** are **{pred}**:")
        for m in member_list:
            lines.append(f"> - **{m}**")
        lines.append("")
        lines.append(f"> The Lean proof (`cases t <;> decide`) becomes an examination of each "
                     f"{typ.lower()}. The proof tree is invariant; only the leaves are renamed.")

    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Auto Theorem Transport — Cross-Domain Proof Cotype Engine")
    parser.add_argument("--source", required=True, help="Source catalog entry name")
    parser.add_argument("--target", required=True, help="Target catalog entry name")
    parser.add_argument("--lean-file", required=True, help="Path to Lean theorem file")
    parser.add_argument("--theorem", default=None, help="Theorem name to transport")
    parser.add_argument("--register", action="store_true",
                        help="Register new cotype mappings interactively")
    parser.add_argument("--output", "-o", default=None, help="Output file path")
    args = parser.parse_args()

    # Load catalog
    print(f"Loading catalog...")
    catalog = load_catalog()
    print(f"  {len(catalog)} entries loaded.")

    source_ims = catalog.get(args.source)
    target_ims = catalog.get(args.target)

    if not source_ims:
        print(f"ERROR: Source '{args.source}' not found.")
        # fuzzy match
        matches = [n for n in catalog if args.source.lower() in n.lower()]
        if matches:
            print(f"  Did you mean: {matches[:5]}")
        sys.exit(1)

    if not target_ims:
        print(f"ERROR: Target '{args.target}' not found.")
        matches = [n for n in catalog if args.target.lower() in n.lower()]
        if matches:
            print(f"  Did you mean: {matches[:5]}")
        sys.exit(1)

    # Compute distance
    distance, conflicts = compute_distance(source_ims, target_ims)
    print(f"Distance({args.source}, {args.target}) = {distance}")
    if distance != 0.0:
        print(f"  WARNING: Nonzero distance! Cotype transport assumes structural identity.")
        for c in conflicts:
            print(f"    {c['primitive']}: {c['a']} vs {c['b']} (delta={c['delta']})")

    # Parse Lean
    print(f"Parsing {args.lean_file}...")
    idents = parse_lean(args.lean_file)
    print(f"  {len(idents)} identifiers:")
    for ident in idents:
        print(f"    {ident.kind:12s} {ident.name}")

    # Registry
    registry = load_registry()

    # Build cotype
    cotype = build_cotype_dict(args.source, args.target, idents, registry)

    # Generate
    output = generate_transport(
        args.source, args.target,
        source_ims.description or args.source,
        target_ims.description or args.target,
        idents, cotype, distance,
        theorem_name=args.theorem)

    # Interactive registration
    if args.register:
        print("\n── Interactive Cotype Registration ──")
        print("For each unmapped identifier, enter the target-domain equivalent.")
        print("Press Enter to skip; type 'quit' to finish.\n")

        unmapped = [i for i in idents if cotype.get(i.name, '').startswith('[')]
        new_mappings = {}
        for ident in unmapped:
            print(f"\n  Source ID: {ident.name} ({ident.kind})")
            print(f"  Docstring: {ident.docstring[:150]}")
            val = input(f"  Target [{args.target}]: ").strip()
            if val.lower() == 'quit':
                break
            if val:
                new_mappings[ident.name] = val

        if new_mappings:
            key = registry_key(args.source, args.target)
            if key not in registry:
                registry[key] = {}
            registry[key].update(new_mappings)
            save_registry(registry)
            print(f"\n  ✓ Registered {len(new_mappings)} mappings to {REGISTRY_PATH}")

            # Regenerate
            cotype = build_cotype_dict(args.source, args.target, idents, registry)
            output = generate_transport(
                args.source, args.target,
                source_ims.description or args.source,
                target_ims.description or args.target,
                idents, cotype, distance,
                theorem_name=args.theorem)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"\n✓ Transport written to {args.output}")
    else:
        print(f"\n{output}")

if __name__ == "__main__":
    main()
