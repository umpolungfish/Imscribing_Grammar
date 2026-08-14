"""
Radial Composer — Hub-and-Spoke Tensor Assembly
Schema: ouroborotic_primitive_composition_schema (O₂, ⊙, 𐑬, 𐑭)

Constructs systems where a central core (hub) couples radially to peripheral components.
Models: central limit theorems, symmetry-breaking vortices, attention mechanisms.
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple

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


def compose_primitive_radial(
    hub_name: str,
    peripherals: List[str],
    coupling_type: str = "tensor",
) -> Dict:
    """
    Assemble a radial composite: hub ⊗ peripheral1 ⊗ peripheral2 ⊗ ...
    
    Args:
        hub_name: Catalog entry name for the central (hub) system
        peripherals: List of catalog entry names for spoke systems
        coupling_type: "tensor" | "meet" | "join"
    
    Returns:
        Result dict with composite metadata and verification.
    """
    catalog = load_catalog()
    if hub_name not in catalog:
        raise ValueError(f"Hub '{hub_name}' not in catalog")
    
    for periph in peripherals:
        if periph not in catalog:
            raise ValueError(f"Peripheral '{periph}' not in catalog")
    
    # Start with hub tuple
    hub_entry = catalog[hub_name]
    composite = hub_entry.get("tuple", {}).copy()
    
    # Merge each peripheral via coupling operation
    for i, periph_name in enumerate(peripherals):
        periph_entry = catalog[periph_name]
        periph_tuple = periph_entry.get("tuple", {})
        
        # Compute coupling via imscribe
        if coupling_type == "tensor":
            coupling_result = imscribe(
                "compute_tensor",
                {"name_a": hub_name, "name_b": periph_name}
            )
        elif coupling_type == "meet":
            coupling_result = imscribe(
                "compute_meet",
                {"name_a": hub_name, "name_b": periph_name}
            )
        elif coupling_type == "join":
            coupling_result = imscribe(
                "compute_join",
                {"name_a": hub_name, "name_b": periph_name}
            )
        else:
            raise ValueError(f"Unknown coupling type: {coupling_type}")
        
        # Merge into composite (override hub with coupling result primitives)
        # This is a simplified merge; full version would use coupling_result['tuple']
        composite.update(coupling_result.get("tuple", {}))
        
        print(f"Peripheral {i+1} ({periph_name}) coupled via {coupling_type}")
    
    # Build composite name
    suffix = "_".join([hub_name] + peripherals)
    comp_name = f"radial_{coupling_type}_{suffix}"
    
    # Prepare for imscribe_system
    imscribe_args = {
        "name": comp_name,
        "description": f"Radial {coupling_type} composite: hub={hub_name}, peripherals={peripherals}",
        "⊢": composite.get("D", "𐑼"),
        "⊣": composite.get("T", "𐑡"),
        "≻": composite.get("R", "𐑾"),
        "≺": composite.get("Phi", "𐑗"),
        "⋈": composite.get("F", "⋈^ì"),
        "⊤": composite.get("K", "⊤^-"),
        "∈": composite.get("G", "𐑔"),
        "∋": composite.get("Gamma", "∋^∧"),
        "⊙": composite.get("Phi", "𐑢"),
        "⊥": composite.get("H", "𐑓"),
        "⊞": composite.get("S", "𐑙"),
        "◻": composite.get("Omega", "𐑷"),
    }
    
    # TODO: Replace with actual imscribe_system call (requires direct import)
    # For now, return synthetic result
    result = {
        "name": comp_name,
        "status": "radial_composition_proposed",
        "coupling_type": coupling_type,
        "hub": hub_name,
        "peripherals": peripherals,
        "tuple": composite,
    }
    
    # Verification (run if composite were actually imscribed)
    result["verification"] = imscribe(
        "ouroborics",
        {"name": comp_name}  # will fail until actually imscribed
    )
    
    return result


if __name__ == "__main__":
    print("=== Radial Primitive Composition ===")
    
    # Example: Central consciousness (self-modeling) + sensory modalities
    result = compose_primitive_radial(
        hub_name="-consciousness_boundary",
        peripherals=["visual_system", "auditory_system", "proprioception"],
        coupling_type="tensor"
    )
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
