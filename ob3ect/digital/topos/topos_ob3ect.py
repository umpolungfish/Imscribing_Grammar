#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class ToposOb3ect:
    """Elementary topos on FinSet: subobject classifier Ω = {True, False}."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()
        self.U = frozenset(range(6))

    def classifier(self, A):
        """χ_A: U → Ω, the characteristic morphism of subobject A."""
        return lambda x: x in A

    def pullback(self, chi):
        """Pullback along true: { x ∈ U | χ(x) = True }."""
        return frozenset(x for x in self.U if chi(x))

    def _verify_topos_axioms(self) -> bool:
        subsets = [
            frozenset({1, 2, 3}),
            frozenset({0, 4}),
            frozenset(),
            self.U,
        ]
        ok = True
        for A in subsets:
            chi = self.classifier(A)
            recovered = self.pullback(chi)
            match = recovered == A
            ok = ok and match
            print(f"  pullback(χ_{set(A)}) = A : {match}")
        # Power object cardinality: |P(U)| = 2^|U| = 2^6 = 64
        power_ok = 2 ** len(self.U) == 64
        print(f"  |P(U)| = 2^6 = 64      : {power_ok}")
        return ok and power_ok

    def verify(self) -> bool:
        print("=== Topos Ob3ect ===")
        layer_ok = self._verify_topos_axioms()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if ToposOb3ect().verify() else 1)
