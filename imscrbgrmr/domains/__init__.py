"""
Imscribing Grammar Domains — Domain-specific imscription implementations.

Subpackages:
- molecular: Retrosynthetic analysis, bond disconnection
- supramolecular: Crystal packing, non-covalent interactions
- temporal: Oscillatory reactions, catalytic cycles
- hybrid: Multi-dimensional systems (MOFs, programmable matter)
"""

from .molecular import MolecularImscriptionAgent
from .supramolecular import SupramolecularImscriptionAgent
from .temporal import TemporalImscriptionAgent

__all__ = [
    "MolecularImscriptionAgent",
    "SupramolecularImscriptionAgent",
    "TemporalImscriptionAgent",
]
