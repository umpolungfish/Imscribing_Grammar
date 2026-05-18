#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class StringDiagramOb3ect:
    """String diagrams: spider law (fuse∘split = id) and composition associativity."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def split(self, x):
        """δ: X → X⊗X  (copy)."""
        return (x, x)

    def fuse(self, pair):
        """μ: X⊗X → X  (merge; requires equal legs)."""
        a, b = pair
        if a != b:
            raise ValueError(f"fuse: legs {a!r} ≠ {b!r}")
        return a

    def compose(self, f, g):
        return lambda x: g(f(x))

    def _verify_spider_law(self) -> bool:
        values = [0, 1, "α", 3.14, (1, 2)]
        ok = all(self.fuse(self.split(v)) == v for v in values)
        print(f"  fuse∘split = id  : {ok}")
        return ok

    def _verify_composition(self) -> bool:
        f = lambda x: x + 1
        g = lambda x: x * 2
        h = lambda x: x - 3
        xs = [0, 1, 5, 10]
        assoc = all(
            self.compose(self.compose(f, g), h)(x) ==
            self.compose(f, self.compose(g, h))(x)
            for x in xs
        )
        print(f"  Composition assoc: {assoc}")
        return assoc

    def _verify_frobenius_spider(self) -> bool:
        # Frobenius spider: split then fuse = identity (already above)
        # Also: (μ⊗id)∘(id⊗δ) = δ∘μ = (id⊗μ)∘(δ⊗id)
        # Concretely: for a pair (a,a), split left leg and fuse with right gives (a,a)
        def frob_left(pair):
            a, b = pair
            la, lb = self.split(a)
            return (la, self.fuse((lb, b)))
        def frob_right(pair):
            a, b = pair
            ra, rb = self.split(b)
            return (self.fuse((a, ra)), rb)
        pairs  = [(x, x) for x in [0, 1, 7]]
        l_ok   = all(frob_left(p) == p for p in pairs)
        r_ok   = all(frob_right(p) == p for p in pairs)
        print(f"  Frobenius spider L: {l_ok}")
        print(f"  Frobenius spider R: {r_ok}")
        return l_ok and r_ok

    def verify(self) -> bool:
        print("=== String Diagram Ob3ect ===")
        sp_ok  = self._verify_spider_law()
        co_ok  = self._verify_composition()
        fr_ok  = self._verify_frobenius_spider()
        layer_ok = sp_ok and co_ok and fr_ok
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if StringDiagramOb3ect().verify() else 1)
