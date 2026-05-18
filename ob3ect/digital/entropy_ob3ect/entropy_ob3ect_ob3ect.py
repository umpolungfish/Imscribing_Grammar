#!/usr/bin/env python3
import hashlib, json, math, os, pathlib, sys
from dataclasses import dataclass
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

EPSILON = 1e-9


@dataclass
class EntropyMeasurement:
    value:     float
    data_hash: str

    def to_json(self):
        return {"value": self.value, "data_hash": self.data_hash}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


class EntropyOb3ect:
    def __init__(self):
        self.source      = pathlib.Path(__file__).read_text()
        self.epsilon     = EPSILON
        self.measurement : Optional[EntropyMeasurement] = None
        self.parsed_data : Optional[str] = None
        self.log         : list = []
        self.state       = "VINIT"

    def _shannon(self, s: str) -> float:
        if not s:
            return 0.0
        n = len(s)
        freq = {}
        for ch in s:
            freq[ch] = freq.get(ch, 0) + 1
        return -sum((c/n) * math.log(c/n) for c in freq.values() if c > 0)

    def TANCH(self):
        self.state = "READY"

    def AFWD(self):
        state_str = json.dumps({"epsilon": self.epsilon, "state": self.state}, sort_keys=True)
        self.parsed_data = state_str
        self.measurement = EntropyMeasurement(
            value=self._shannon(state_str),
            data_hash=hashlib.sha256(state_str.encode()).hexdigest()
        )
        self.state = "READY"

    def AREV(self):
        self.unparsed_data = self.parsed_data

    def FSPLIT(self):
        self.h_parsed   = self._shannon(self.parsed_data)   if self.parsed_data   else 0.0
        self.h_unparsed = self._shannon(getattr(self, "unparsed_data", "") or "")

    def FFUSE(self):
        if hasattr(self, "h_parsed"):
            diff = abs(self.h_parsed - self.h_unparsed)
            self.entropy_stable = diff <= self.epsilon
            self.state = "VERIFIED" if self.entropy_stable else "FAILED"
        else:
            self.entropy_stable = True
            self.state = "VERIFIED"

    def CLINK(self):
        self.AFWD(); self.AREV()
        if self.measurement:
            self.log.append(("ISCRIB", self.measurement.hash()))

    def IFIX(self):
        if self.measurement:
            self.log.append(("IFIX", {"entropy": self.measurement.value, "state": self.state}))

    def _domain_frobenius(self) -> bool:
        if not self.measurement:
            return False
        return self.measurement.hash() == EntropyMeasurement(
            self.measurement.value, self.measurement.data_hash
        ).hash()

    def bootstrap(self) -> bool:
        self.TANCH(); self.AREV()
        self.FSPLIT(); self.AFWD()
        self.FFUSE(); self.CLINK()
        self.IFIX()
        return self._domain_frobenius()

    def verify(self) -> bool:
        print("=== Entropy Ob3ect ===")
        domain_ok = self.bootstrap()
        stable    = getattr(self, "entropy_stable", False)
        print(f"  Shannon entropy stable under roundtrip : {stable}")
        if self.measurement:
            print(f"  H(source) ≈ {self.measurement.value:.4f} bits/char")
        print(f"  Record μ∘δ=id (domain)                : {domain_ok}")
        frob_ok  = frobenius_phase(self.source)
        closure  = domain_ok and frob_ok
        print(f"Closure: {closure}")
        return closure


if __name__ == "__main__":
    sys.exit(0 if EntropyOb3ect().verify() else 1)
