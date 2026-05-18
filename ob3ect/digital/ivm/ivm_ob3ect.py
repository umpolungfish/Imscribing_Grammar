#!/usr/bin/env python3
import hashlib, os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


class IVM:
    """Stack-based Imscription Virtual Machine."""
    def __init__(self):
        self.stack = []

    def run(self, program):
        self.stack = []
        for instr in program:
            op, *args = instr
            if   op == "PUSH": self.stack.append(args[0])
            elif op == "DUP":  self.stack.append(self.stack[-1])
            elif op == "POP":  self.stack.pop()
            elif op == "SWAP": self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
            elif op == "ADD":  b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a + b)
            elif op == "XOR":  b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a ^ b)
            elif op == "HASH":
                v = self.stack.pop()
                h = int(hashlib.sha256(str(v).encode()).hexdigest()[:8], 16)
                self.stack.append(h)
        return list(self.stack)


class IVMOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()
        self.vm     = IVM()

    def _verify_vm_laws(self) -> bool:
        vm = self.vm

        # a XOR a = 0 (self-annihilation)
        xor_ok = vm.run([("PUSH", 42), ("DUP",), ("XOR",)]) == [0]
        print(f"  a XOR a = 0       : {xor_ok}")

        # 3 + 3 = 6 (additive composition)
        add_ok = vm.run([("PUSH", 3), ("DUP",), ("ADD",)]) == [6]
        print(f"  3 + 3 = 6         : {add_ok}")

        # Determinism: same program gives same result
        r1     = vm.run([("PUSH", 99), ("HASH",)])
        r2     = vm.run([("PUSH", 99), ("HASH",)])
        det_ok = r1 == r2
        print(f"  Determinism       : {det_ok}")

        # Categorical composition: (g∘f)(x) computed via stack
        # f = DUP ADD (x→2x), g = PUSH 1 ADD (x→x+1)
        # (g∘f)(3) = g(6) = 7
        f_then_g = vm.run([("PUSH", 3), ("DUP",), ("ADD",), ("PUSH", 1), ("ADD",)])
        comp_ok  = f_then_g == [7]
        print(f"  (g∘f)(3) = 7      : {comp_ok}")

        return xor_ok and add_ok and det_ok and comp_ok

    def verify(self) -> bool:
        print("=== Imscription VM Ob3ect ===")
        layer_ok = self._verify_vm_laws()
        frob_ok  = frobenius_phase(self.source)
        closure  = layer_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if IVMOb3ect().verify() else 1)
