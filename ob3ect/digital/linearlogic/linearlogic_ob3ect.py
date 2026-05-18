#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


class LinearToken:
    """Resource token — consumed exactly once."""
    def __init__(self, value):
        self.value   = value
        self._used   = False

    def consume(self):
        if self._used:
            raise RuntimeError(f"LinearToken({self.value!r}): double-consume (cloning violation)")
        self._used = True
        return self.value


class LinearLogicOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def _verify_no_cloning(self) -> bool:
        t = LinearToken(42)
        t.consume()
        blocked = False
        try:
            t.consume()
        except RuntimeError:
            blocked = True
        print(f"  No-cloning (double-consume blocked) : {blocked}")
        return blocked

    def _verify_no_weakening(self) -> bool:
        t   = LinearToken("resource")
        val = t.consume()
        ok  = val == "resource"
        print(f"  No-weakening (resource used)        : {ok}")
        return ok

    def _verify_tensor_unit(self) -> bool:
        # (A ⊗ I) ≅ A: consuming unit alongside A leaves A's value intact
        a    = LinearToken(7)
        unit = LinearToken(None)
        val  = a.consume()
        unit.consume()
        ok   = val == 7
        print(f"  Tensor-unit law (A ⊗ I ≅ A)        : {ok}")
        return ok

    def verify(self) -> bool:
        print("=== Linear Logic Ob3ect ===")
        nc      = self._verify_no_cloning()
        nw      = self._verify_no_weakening()
        tu      = self._verify_tensor_unit()
        layer_ok = nc and nw and tu
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if LinearLogicOb3ect().verify() else 1)
