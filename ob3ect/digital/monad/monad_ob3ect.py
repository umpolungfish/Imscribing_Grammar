#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class MonadOb3ect:
    """Option monad with verified monad laws."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def unit(self, x):  return ("Some", x)
    def bind(self, m, f):
        if m is None:       return None
        tag, val = m
        if tag == "None":   return None
        return f(val)

    def _verify_monad_laws(self) -> bool:
        f = lambda x: self.unit(x * 2) if x < 10 else None
        g = lambda x: self.unit(x + 1)

        xs = [1, 5, 9, 0]
        # Left unit: bind(unit(x), f) = f(x)
        left  = all(self.bind(self.unit(x), f) == f(x) for x in xs)
        # Right unit: bind(m, unit) = m
        ms    = [self.unit(x) for x in xs] + [None]
        right = all(self.bind(m, self.unit) == m for m in ms)
        # Associativity: bind(bind(unit(x),f),g) = bind(unit(x), λx.bind(f(x),g))
        assoc = all(
            self.bind(self.bind(self.unit(x), f), g) ==
            self.bind(self.unit(x), lambda x, f=f, g=g: self.bind(f(x), g))
            for x in xs
        )
        print(f"  Left unit      : {left}")
        print(f"  Right unit     : {right}")
        print(f"  Associativity  : {assoc}")
        return left and right and assoc

    def verify(self) -> bool:
        print("=== Monad Ob3ect ===")
        layer_ok = self._verify_monad_laws()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if MonadOb3ect().verify() else 1)
