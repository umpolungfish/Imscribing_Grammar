#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class HopfOb3ect:
    """Hopf algebra on Z/2Z (Boolean XOR group)."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def mul(self, a, b): return a ^ b
    def unit(self):      return 0
    def comul(self, a):  return (a, a)
    def counit(self, a): return 0
    def antipode(self, a): return a

    def _verify_antipode_axioms(self) -> bool:
        elements = [0, 1]
        # μ∘(S⊗id)∘δ(a) = η∘ε(a) = unit
        left_ok  = all(self.mul(self.antipode(a), a) == self.unit() for a in elements)
        right_ok = all(self.mul(a, self.antipode(a)) == self.unit() for a in elements)
        # μ∘δ = counit in Z/2Z: a XOR a = 0 = counit(a)
        frob_ok  = all(self.mul(*self.comul(a)) == self.counit(a) for a in elements)
        print(f"  Antipode left    : {left_ok}")
        print(f"  Antipode right   : {right_ok}")
        print(f"  μ∘δ = ε          : {frob_ok}")
        return left_ok and right_ok and frob_ok

    def verify(self) -> bool:
        print("=== Hopf Ob3ect ===")
        layer_ok = self._verify_antipode_axioms()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if HopfOb3ect().verify() else 1)
