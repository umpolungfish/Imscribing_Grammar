"""
Primitive Series Composer — Linear/Stacked Assembly
Schema: ouroborotic_primitive_composition_schema (O₂, ⊙, 𐑬, 𐑭)
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# Use absolute path to catalog
CATALOG_PATH = Path("/home/mrnob0dy666/imscribing_grammar/IG_catalog.json")


def load_catalog() -> List[Dict]:
    """Load the imscriptive grammar catalog (list format)."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    return []


def find_entry_by_name(catalog: List[Dict], name: str) -> Dict:
    """Find a catalog entry by name."""
    for entry in catalog:
        if entry.get("name") == name:
            return entry
    return {}


def compose_primitive_series(
    base_schema_name: str,
    primitives: List[Tuple[str, str, str]],
    name_prefix: str = "series_composed",
) -> Dict:
    """
    Compose a linear series of primitives: p1 → p2 → p3 → ...
    Each primitive is (primitive_id, value, description).
    
    Returns catalog metadata for the new composite.
    """
    catalog = load_catalog()
    base_entry = find_entry_by_name(catalog, base_schema_name)
    if not base_entry:
        raise ValueError(f"Base schema '{base_schema_name}' not in catalog")
    
    base_tuple = {k: v for k, v in base_entry.items() if k not in ["name", "description"]}
    
    composite = base_tuple.copy()
    
    for i, (prim_id, prim_val, desc) in enumerate(primitives):
        composite[prim_id] = prim_val
        print(f"Primitive {i+1}: {prim_id} = {prim_val} ({desc})")
    
    suffix = "_".join([v[0] + "_" + v[1].split("_")[1] for v in primitives])
    comp_name = f"{name_prefix}_{suffix}"
    
    result = {
        "name": comp_name,
        "status": "series_composition_proposed",
        "base_schema": base_schema_name,
        "primitives_applied": primitives,
        "tuple": composite,
    }
    
    return result


if __name__ == "__main__":
    # Example primitives for ascent to O₂
    primitives = [
        ("Þ", "𐑶", "network topology → self-referential"),
        ("Φ", "𐑬", "partial symmetry → Frobenius-special"),
        ("Ç", "Ç^@", "moderate kinetics → slow/near-equilibrium"),
        ("⊙", "⊙", "subcritical → self-modeling criticality"),
        ("Ħ", "𐑖", "memoryless → two-step chirality"),
        ("Ω", "𐑭", "trivial winding → integer-wound"),
    ]
    
    print("=== Primitive Series Composition ===")
    result = compose_primitive_series(
        "ouroborotic_primitive_composition_schema",
        primitives,
        name_prefix="ascension_series"
    )
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
