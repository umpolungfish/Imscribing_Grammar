#!/usr/bin/env python3
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

KERNEL_MODULES = {
    "scheduler": "def schedule(tasks):\n    return [t() for t in tasks]",
    "allocator": "def alloc(n):\n    return bytearray(n)",
    "imscriber": "import ast\ndef imscribe(src):\n    return ast.unparse(ast.parse(src))",
    "verifier":  "def verify(ok):\n    return bool(ok)",
}


class ImscriptionOperatingSystem:
    def __init__(self):
        self.source   = pathlib.Path(__file__).read_text()
        self.pids     = {}

    def _boot_all(self) -> bool:
        all_ok = True
        for name, body in KERNEL_MODULES.items():
            ok = frobenius_phase(body)
            self.pids[name] = "RUNNING" if ok else "FAILED"
            print(f"  [{self.pids[name]:8s}] {name}")
            all_ok = all_ok and ok
        return all_ok

    def verify(self) -> bool:
        print("=== Imscription Operating System ===")
        print(f"  Kernel modules : {len(KERNEL_MODULES)}")
        boot_ok = self._boot_all()
        frob_ok = frobenius_phase(self.source)
        closure  = boot_ok and frob_ok
        print(f"Closure: {closure}")
        return closure

if __name__ == "__main__":
    sys.exit(0 if ImscriptionOperatingSystem().verify() else 1)
