"""
Imscribing Grammar Domains — Domain-specific synthon implementations.

Subpackages:
- molecular: Retrosynthetic analysis, bond disconnection
- supramolecular: Crystal packing, non-covalent interactions
- temporal: Oscillatory reactions, catalytic cycles
- hybrid: Multi-dimensional systems (MOFs, programmable matter)
"""

from .molecular import MolecularSynthonAgent
from .supramolecular import SupramolecularSynthonAgent
from .temporal import TemporalSynthonAgent

__all__ = [
    "MolecularSynthonAgent",
    "SupramolecularSynthonAgent",
    "TemporalSynthonAgent",
]
