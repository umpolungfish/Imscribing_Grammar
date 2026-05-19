"""
Composer Core — Core algebraic operations for ouroborotic primitive composition
Schema: ouroborotic_primitive_composition_schema (O_2, ⊙_ÿ, Φ_F, Ω_z)

Provides: tensor, meet, join, distance wrappers using imscrbgrmr.algebra
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from imscrbgrmr.algebra import tensor, meet, join, tuple_distance


def compute_tensor(name_a: str, name_b: str) -> dict:
    """Wrap algebra.tensor for Frobenius-compatible output."""
    try:
        result = tensor(name_a, name_b)
        return {
            "name_a": name_a,
            "name_b": name_b,
            "status": "tensor_result",
            "tuple": result.to_dict() if hasattr(result, "to_dict") else str(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def compute_meet(name_a: str, name_b: str) -> dict:
    """Wrap algebra.meet for Frobenius-compatible output."""
    try:
        result = meet(name_a, name_b)
        return {
            "name_a": name_a,
            "name_b": name_b,
            "status": "meet_result",
            "tuple": result.lattice.to_dict() if hasattr(result, "lattice") else str(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def compute_join(name_a: str, name_b: str) -> dict:
    """Wrap algebra.join for Frobenius-compatible output."""
    try:
        result = join(name_a, name_b)
        return {
            "name_a": name_a,
            "name_b": name_b,
            "status": "join_result",
            "tuple": result.lattice.to_dict() if hasattr(result, "lattice") else str(result),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def compute_distance(name_a: str, name_b: str) -> dict:
    """Wrap algebra.distance for Frobenius-compatible output."""
    try:
        dist = tuple_distance(name_a, name_b)
        return {
            "name_a": name_a,
            "name_b": name_b,
            "distance": dist,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    print("Composer core utilities imported.")
