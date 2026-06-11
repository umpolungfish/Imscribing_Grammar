"""
Network Composer — Full Tensor/Graph Assembly
Schema: ouroborotic_primitive_composition_schema (O₂, ⊙_ÿ, Φ_F, Ω_z)

Constructs arbitrary tensor networks: G = (V, E) where vertices are systems,
edges are coupling operations (tensor, meet, join, directed).
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from IG_inquiry import ToolDispatcher as _Dispatcher
_d = _Dispatcher()
def imscribe(tool_name: str, args: dict) -> dict:
    return _d.dispatch(tool_name, args, 0)


SCHEMA_PATH = Path(__file__).parent
CATALOG_PATH = Path(__file__).parent.parent / "IG_catalog.json"


def load_catalog() -> Dict:
    """Load the imscriptive grammar catalog."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    return {}


def build_network_composite(
    nodes: List[str],
    edges: List[Tuple[str, str, str]],
) -> Dict:
    """
    Assemble a tensor network from nodes and edges.
    
    Args:
        nodes: List of catalog entry names
        edges: List of (source, target, operation) tuples
    
    Returns:
        Result dict with composite metadata.
    
    Algorithm:
        1. Start with first node as seed
        2. For each edge, compute coupling (tensor/meet/join/directed)
        3. Merge result into accumulator
        4. Final tuple is candidate for new catalog entry
    """
    catalog = load_catalog()
    
    # Validate all nodes exist
    for node in nodes:
        if node not in catalog:
            raise ValueError(f"Node '{node}' not in catalog")
    
    if not nodes:
        raise ValueError("At least one node required")
    
    # Start with first node
    seed = nodes[0]
    composite = catalog[seed].get("tuple", {}).copy()
    
    print(f"Seed node: {seed}")
    
    # Process edges (BFS-style, but edges define the exact coupling order)
    for i, (src, tgt, op) in enumerate(edges):
        if src not in catalog or tgt not in catalog:
            raise ValueError(f"Edge {i}: source '{src}' or target '{tgt}' not in catalog")
        
        # Compute coupling via imscribe
        if op == "tensor":
            result = imscribe("compute_tensor", {"name_a": src, "name_b": tgt})
        elif op == "meet":
            result = imscribe("compute_meet", {"name_a": src, "name_b": tgt})
        elif op == "join":
            result = imscribe("compute_join", {"name_a": src, "name_b": tgt})
        elif op == "directed":
            result = imscribe(
                "compute_conflict_distance",
                {"name_a": src, "name_b": tgt}
            )
        else:
            raise ValueError(f"Unknown operation: {op}")
        
        # Merge primitives into composite
        composite.update(result.get("tuple", {}))
        
        print(f"Edge {i+1}: {src} --[{op}]--> {tgt}")
    
    # Build name
    suffix = "_".join(nodes)
    comp_name = f"network_{suffix}"
    
    # Prepare for imscribe_system
    imscribe_args = {
        "name": comp_name,
        "description": f"Network composite: nodes={nodes}, edges={edges}",
        "Ð": composite.get("D", "Ð_;"),
        "Þ": composite.get("T", "Þ_6"),
        "Ř": composite.get("R", "Ř_="),
        "Φ": composite.get("Phi", "Φ_ɐ"),
        "ƒ": composite.get("F", "ƒ^ì"),
        "Ç": composite.get("K", "Ç^-"),
        "Γ": composite.get("G", "Γ_γ"),
        "ɢ": composite.get("Gamma", "ɢ^∧"),
        "⊙": composite.get("Phi", "⊙_ž"),
        "Ħ": composite.get("H", "Ħ_Ñ"),
        "Σ": composite.get("S", "Σ_S"),
        "Ω": composite.get("Omega", "Ω_Å"),
    }
    
    # TODO: Replace with actual imscribe_system call
    result = {
        "name": comp_name,
        "status": "network_composition_proposed",
        "nodes": nodes,
        "edges": edges,
        "tuple": composite,
    }
    
    # Verification (run if composite were actually imscribed)
    result["verification"] = imscribe(
        "ouroborics",
        {"name": comp_name}  # will fail until actually imscribed
    )
    
    return result


if __name__ == "__main__":
    print("=== Network Primitive Composition ===")
    
    # Example: Language grammar network
    # nodes = ["syntax", "semantics", "pragmatics", "phonology"]
    # edges = [
    #     ("syntax", "semantics", "tensor"),
    #     ("semantics", "pragmatics", "meet"),
    #     ("pragmatics", "phonology", "join"),
    #     ("phonology", "syntax", "directed"),
    # ]
    
    # result = build_network_composite(nodes, edges)
    # print("\nResult:")
    # print(json.dumps(result, indent=2))
    
    # For now, demonstrate with simpler case
    print("Sample network definition available; uncomment to run.")
