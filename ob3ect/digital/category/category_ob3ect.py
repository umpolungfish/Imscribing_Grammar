#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class CategoryOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def _verify_category_laws(self) -> bool:
        compose  = lambda f, g: lambda x: g(f(x))
        identity = lambda x: x
        f = lambda x: (x + 1) % 4
        g = lambda x: (x * 2) % 4
        h = lambda x: (x + 3) % 4
        xs = list(range(4))

        id_left  = all(compose(identity, f)(x) == f(x) for x in xs)
        id_right = all(compose(f, identity)(x) == f(x) for x in xs)
        assoc    = all(compose(compose(f, g), h)(x) == compose(f, compose(g, h))(x) for x in xs)

        print(f"  Identity left   : {id_left}")
        print(f"  Identity right  : {id_right}")
        print(f"  Associativity   : {assoc}")
        return id_left and id_right and assoc

    def verify(self) -> bool:
        print("=== Category Ob3ect ===")
        layer_ok = self._verify_category_laws()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if CategoryOb3ect().verify() else 1)
