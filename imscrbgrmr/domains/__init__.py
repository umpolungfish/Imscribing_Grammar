"""
Imscribing Grammar Domains — Domain-specific imscription implementations.

Subpackages:
- quantum: Quantum particles and topological matter

The molecular, supramolecular, temporal and hybrid domains were chemistry:
retrosynthesis, crystal packing, catalytic cycles, MOFs. That work lives in
red-hot_rebis, which supersedes it. What the Grammar keeps here is the
domain-agnostic algebra — tensor, meet, join, distance, ouroborics.
"""

from .quantum import *  # noqa: F401,F403

__all__ = []
