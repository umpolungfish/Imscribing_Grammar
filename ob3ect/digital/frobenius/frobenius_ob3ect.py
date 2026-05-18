#!/usr/bin/env python3
import ast, os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase, TANCH, AFWD

class FrobeniusOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def _verify_frobenius_law(self) -> bool:
        samples = [
            "x = 1 + 2",
            "def f(x): return x * 2",
            "result = [i**2 for i in range(10)]",
        ]
        results = []
        for src in samples:
            t         = TANCH(src)
            roundtrip = TANCH(AFWD(t))
            ok        = ast.dump(t) == ast.dump(roundtrip)
            results.append(ok)
            print(f"  μ∘δ=id [{src[:28]}]: {ok}")
        return all(results)

    def verify(self) -> bool:
        print("=== Frobenius Ob3ect ===")
        layer_ok = self._verify_frobenius_law()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if FrobeniusOb3ect().verify() else 1)
