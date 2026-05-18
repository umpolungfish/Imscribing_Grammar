#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class HomotopyTypeTheoryOb3ect:
    """HoTT: type equivalence witness between two isomorphic record types."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def _verify_type_equivalence(self) -> bool:
        from collections import namedtuple
        Point2D  = namedtuple("Point2D",  ["x", "y"])
        Complex2 = namedtuple("Complex2", ["re", "im"])

        phi     = lambda p: Complex2(p.x, p.y)
        phi_inv = lambda c: Point2D(c.re, c.im)

        points   = [Point2D(1.0, 2.0), Point2D(-3.0, 0.5), Point2D(0.0, 0.0)]
        complexes = [Complex2(1.0, 2.0), Complex2(-3.0, 0.5), Complex2(0.0, 0.0)]

        retraction = all(phi_inv(phi(p)) == p for p in points)
        section    = all(phi(phi_inv(c)) == c for c in complexes)
        # refl: identity path is trivial (φ⁻¹∘φ on the unit element)
        refl_ok    = phi_inv(phi(Point2D(0.0, 0.0))) == Point2D(0.0, 0.0)

        print(f"  φ⁻¹∘φ = id_Point2D   : {retraction}")
        print(f"  φ∘φ⁻¹ = id_Complex2  : {section}")
        print(f"  refl path trivial     : {refl_ok}")
        return retraction and section and refl_ok

    def verify(self) -> bool:
        print("=== Homotopy Type Theory Ob3ect ===")
        layer_ok = self._verify_type_equivalence()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if HomotopyTypeTheoryOb3ect().verify() else 1)
