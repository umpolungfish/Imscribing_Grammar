#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class CCCOb3ect:
    """Cartesian closed category: curry/uncurry adjunction."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def curry(self, f):
        return lambda x: lambda y: f(x, y)

    def uncurry(self, g):
        return lambda x, y: g(x)(y)

    def _verify_ccc_adjunction(self) -> bool:
        f = lambda x, y: x * y + 1
        g = lambda x: lambda y: x + y * 2

        pairs = [(1, 2), (3, 4), (0, 0), (5, 5)]

        uc_c = all(self.uncurry(self.curry(f))(x, y) == f(x, y)     for x, y in pairs)
        c_uc = all(self.curry(self.uncurry(g))(x)(y) == g(x)(y)     for x, y in pairs)

        print(f"  uncurry∘curry = id : {uc_c}")
        print(f"  curry∘uncurry = id : {c_uc}")
        return uc_c and c_uc

    def verify(self) -> bool:
        print("=== Cartesian Closed Ob3ect ===")
        layer_ok = self._verify_ccc_adjunction()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if CCCOb3ect().verify() else 1)
