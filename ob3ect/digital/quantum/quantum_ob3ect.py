#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class QuantumOb3ect:
    """4-state quantum system: Born rule and state normalization."""
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()
        self.basis = [
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ]

    def prepare(self, n: int):
        return self.basis[n]

    def measure(self, state) -> int:
        return max(range(len(state)), key=lambda i: state[i])

    def _verify_born_rule(self) -> bool:
        born_ok = all(self.measure(self.prepare(n)) == n for n in range(4))
        norm_ok = all(
            abs(sum(a**2 for a in self.prepare(n)) - 1.0) < 1e-12
            for n in range(4)
        )
        print(f"  Born rule measure(prepare(n))=n : {born_ok}")
        print(f"  Normalization ‖|n⟩‖² = 1        : {norm_ok}")
        return born_ok and norm_ok

    def verify(self) -> bool:
        print("=== Quantum Ob3ect ===")
        layer_ok = self._verify_born_rule()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if QuantumOb3ect().verify() else 1)
