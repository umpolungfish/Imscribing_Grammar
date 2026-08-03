#!/usr/bin/env python3
"""
Composer CLI — Terminal interface for ouroborotic primitive composition schema.

Usage:
    python composer_cli.py sequence --base <name> [--primitive ...]
    python composer_cli.py radial --hub <name> [--spoke ...] [--coupling <op>]
    python composer_cli.py network --node ... [--edge ...]
    python composer_cli.py show <name>
    python composer_cli.py tensor <name_a> <name_b>
    python composer_cli.py meet <name_a> <name_b>
    python composer_cli.py join <name_a> <name_b>
    python composer_cli.py distance <name_a> <name_b>
"""
import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from imscrbgrmr.algebra import tensor, meet, join, tuple_distance
from imscrbgrmr.models import Imscription

CATALOG_PATH = Path(__file__).parent.parent / "IG_catalog.json"


def load_catalog() -> dict:
    """Load the imscriptive grammar catalog."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    return {}


def find_entry_by_name(catalog: dict, name: str) -> dict:
    """Find a catalog entry by name."""
    for entry in catalog:
        if entry.get("name") == name:
            return entry
    return {}


def load_imscription(name: str) -> Imscription:
    """Load a catalog entry and convert to Imscription, handling mixed key formats."""
    catalog = load_catalog()
    entry = find_entry_by_name(catalog, name)
    if not entry:
        raise ValueError(f"Entry '{name}' not found in catalog")
    
    # Normalize keys to Unicode format
    normalized = {}
    for k, v in entry.items():
        if k in ['name', 'description']:
            normalized[k] = v
        else:
            # Map Latin keys to Unicode equivalents
            mapping = {
                'D': '⊢',
                'T': '⊣',
                'R': '>',
                'P': '<',
                'F': '⋈',
                'K': '⊤',
                'G': '∈',
                'Gamma': '∋',
                'Phi': '⊙',
                'H': '⊥',
                'S': '⊞',
                'Omega': '◻'
            }
            norm_key = mapping.get(k, k)
            normalized[norm_key] = v
    
    return Imscription.from_dict(normalized)


def compute_ouroboricity(t: dict) -> str:
    """Compute ouroboricity tier by delegating to canonical_primitives.ouroboricity_tier."""
    try:
        from imscrbgrmr.canonical_primitives import CrystalAddress, ouroboricity_tier
        addr = CrystalAddress.from_dict(t)
        return ouroboricity_tier(addr)
    except Exception:
        return "O₀"


def show_entry(args):
    """Show imscription of a catalog entry."""
    catalog = load_catalog()
    entry = find_entry_by_name(catalog, args.name)
    if not entry:
        print(f"Entry '{args.name}' not found in catalog", file=sys.stderr)
        sys.exit(1)
    
    # Extract tuple and metadata
    t = {k: v for k, v in entry.items() if k not in ["name", "description"]}
    tier = compute_ouroboricity(t)
    
    result = {
        "name": entry.get("name", args.name),
        "description": entry.get("description", ""),
        "tier": tier,
        "tuple": t,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def sequence_command(args):
    """Run sequence composition."""
    catalog = load_catalog()
    
    # Load base entry
    base_entry = find_entry_by_name(catalog, args.base)
    if not base_entry:
        print(f"Base schema '{args.base}' not in catalog", file=sys.stderr)
        sys.exit(1)
    
    base_tuple = {k: v for k, v in base_entry.items() if k not in ["name", "description"]}
    
    # Apply primitives
    primitives = []
    composite = base_tuple.copy()
    
    for p_str in args.primitive:
        parts = p_str.split(":")
        if len(parts) != 3:
            print(f"Malformed primitive: {p_str} (expected 'id:value:description')", file=sys.stderr)
            sys.exit(1)
        prim_id, prim_val, desc = parts
        primitives.append((prim_id, prim_val, desc))
        composite[prim_id] = prim_val
        print(f"Applied: {prim_id} = {prim_val} ({desc})")
    
    # Build result
    suffix = "_".join([v[0] + "_" + v[1].split("_")[1] for v in primitives])
    comp_name = f"{args.prefix}_{suffix}"
    
    result = {
        "name": comp_name,
        "status": "series_composition_proposed",
        "base_schema": args.base,
        "primitives_applied": primitives,
        "tuple": composite,
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


def radial_command(args):
    """Run radial composition."""
    catalog = load_catalog()
    
    # Validate hub
    hub_entry = find_entry_by_name(catalog, args.hub)
    if not hub_entry:
        print(f"Hub '{args.hub}' not in catalog", file=sys.stderr)
        sys.exit(1)
    
    # Validate spokes
    for spoke in args.spoke:
        if not find_entry_by_name(catalog, spoke):
            print(f"Spoke '{spoke}' not in catalog", file=sys.stderr)
            sys.exit(1)
    
    # Build composite tuple (simplified: hub tuple with spoke overrides)
    hub_tuple = {k: v for k, v in hub_entry.items() if k not in ["name", "description"]}
    composite = hub_tuple.copy()
    
    for i, spoke in enumerate(args.spoke):
        spoke_entry = find_entry_by_name(catalog, spoke)
        spoke_tuple = {k: v for k, v in spoke_entry.items() if k not in ["name", "description"]}
        composite.update(spoke_tuple)
        print(f"Spoke {i+1} ({spoke}) merged via {args.coupling}")
    
    suffix = "_".join([args.hub] + args.spoke)
    comp_name = f"radial_{args.coupling}_{suffix}"
    
    result = {
        "name": comp_name,
        "status": "radial_composition_proposed",
        "coupling_type": args.coupling,
        "hub": args.hub,
        "peripherals": args.spoke,
        "tuple": composite,
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


def network_command(args):
    """Run network composition."""
    catalog = load_catalog()
    
    # Validate nodes
    for node in args.node:
        if not find_entry_by_name(catalog, node):
            print(f"Node '{node}' not in catalog", file=sys.stderr)
            sys.exit(1)
    
    if not args.node:
        print("At least one node required", file=sys.stderr)
        sys.exit(1)
    
    # Build edge list
    edges = []
    for i in range(0, len(args.edge), 3):
        if i + 2 >= len(args.edge):
            print("Edges must be groups of three: src tgt op", file=sys.stderr)
            sys.exit(1)
        src, tgt, op = args.edge[i], args.edge[i+1], args.edge[i+2]
        edges.append((src, tgt, op))
    
    # Start with seed node
    seed = args.node[0]
    seed_entry = find_entry_by_name(catalog, seed)
    composite = {k: v for k, v in seed_entry.items() if k not in ["name", "description"]}
    
    print(f"Seed node: {seed}")
    
    # Merge edges (simplified)
    for i, (src, tgt, op) in enumerate(edges):
        print(f"Edge {i+1}: {src} --[{op}]--> {tgt}")
        src_entry = find_entry_by_name(catalog, src)
        tgt_entry = find_entry_by_name(catalog, tgt)
        src_tuple = {k: v for k, v in src_entry.items() if k not in ["name", "description"]}
        tgt_tuple = {k: v for k, v in tgt_entry.items() if k not in ["name", "description"]}
        composite.update(src_tuple)
        composite.update(tgt_tuple)
    
    suffix = "_".join(args.node)
    comp_name = f"network_{suffix}"
    
    result = {
        "name": comp_name,
        "status": "network_composition_proposed",
        "nodes": args.node,
        "edges": edges,
        "tuple": composite,
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


def _sanitize_for_json(obj):
    """Recursively convert non-JSON-serializable objects to strings."""
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    else:
        return str(obj)


def algebra_command(args):
    """Run algebra operation (tensor/meet/join/distance)."""
    op = args.operation
    name_a, name_b = args.name_a, args.name_b
    
    try:
        # Load Imscriptions
        insc_a = load_imscription(name_a)
        insc_b = load_imscription(name_b)
        
        if op == "tensor":
            result = tensor(insc_a, insc_b)
        elif op == "meet":
            result = meet(insc_a, insc_b)
        elif op == "join":
            result = join(insc_a, insc_b)
        elif op == "distance":
            result = tuple_distance(insc_a, insc_b)
        else:
            print(f"Unknown operation: {op}", file=sys.stderr)
            sys.exit(1)
        
        # Convert to dict if needed
        if hasattr(result, "to_dict"):
            output = result.to_dict()
        elif hasattr(result, "__dict__"):
            output = result.__dict__
        else:
            output = str(result)
        
        # Sanitize for JSON
        output = _sanitize_for_json(output)
        
        print(json.dumps({
            "operation": op,
            "name_a": name_a,
            "name_b": name_b,
            "result": output,
        }, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Ouroborotic Primitive Composition Schema CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python composer_cli.py sequence --base ouroborotic_primitive_composition_schema \\
    --primitive Þ:𐑶:network_topology \\
    --primitive Φ:𐑬:Frobenius_special

  python composer_cli.py radial --hub consciousness_boundary \\
    --spoke visual_system --spoke auditory_system --coupling tensor

  python composer_cli.py network --node syntax --node semantics \\
    --edge syntax semantics tensor --edge semantics syntax directed

  python composer_cli.py tensor riemann_zeta_function hadamard_product
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Show entry
    show_parser = subparsers.add_parser("show", help="Show imscription of a catalog entry")
    show_parser.add_argument("name", help="Catalog entry name")
    show_parser.set_defaults(func=show_entry)
    
    # Sequence composition
    seq_parser = subparsers.add_parser("sequence", help="Linear/stacked primitive assembly")
    seq_parser.add_argument("--base", required=True, help="Base schema name")
    seq_parser.add_argument("--primitive", action="append", required=True,
                            help="Primitive in format 'id:value:description'")
    seq_parser.add_argument("--prefix", default="series_composed",
                            help="Name prefix for result")
    seq_parser.set_defaults(func=sequence_command)
    
    # Radial composition
    rad_parser = subparsers.add_parser("radial", help="Hub-and-spoke tensor assembly")
    rad_parser.add_argument("--hub", required=True, help="Hub system name")
    rad_parser.add_argument("--spoke", action="append", required=True,
                            help="Spoke system name (repeatable)")
    rad_parser.add_argument("--coupling", default="tensor",
                            choices=["tensor", "meet", "join"],
                            help="Coupling operation")
    rad_parser.set_defaults(func=radial_command)
    
    # Network composition
    net_parser = subparsers.add_parser("network", help="Full tensor network assembly")
    net_parser.add_argument("--node", action="append", required=True,
                            help="Node system name (repeatable)")
    net_parser.add_argument("--edge", action="append", required=True, nargs=3,
                            metavar=("SRC", "TGT", "OP"),
                            help="Edge: source target operation (tensor|meet|join|directed)")
    net_parser.set_defaults(func=network_command)
    
    # Algebra operations
    alg_parser = subparsers.add_parser("algebra", help="Algebra operations")
    alg_parser.add_argument("operation", choices=["tensor", "meet", "join", "distance"],
                            help="Operation to perform")
    alg_parser.add_argument("name_a", help="First system name")
    alg_parser.add_argument("name_b", help="Second system name")
    alg_parser.set_defaults(func=algebra_command)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
