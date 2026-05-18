#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys
from dataclasses import dataclass
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


@dataclass
class IGLatticeCoordinate:
    D: str; T: str; R: str; Phi: str; F: str; K: str
    G: str; Gamma: str; Phi_c: str; H: str; S: str; Omega: str

    def to_tuple(self):
        return (self.D, self.T, self.R, self.Phi, self.F, self.K,
                self.G, self.Gamma, self.Phi_c, self.H, self.S, self.Omega)

    def to_json(self):
        return {"D":self.D,"T":self.T,"R":self.R,"Phi":self.Phi,"F":self.F,"K":self.K,
                "G":self.G,"Gamma":self.Gamma,"Phi_c":self.Phi_c,"H":self.H,"S":self.S,"Omega":self.Omega}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


CANONICAL = IGLatticeCoordinate(
    D="Ð_ω", T="Þ_O", R="Ř_=", Phi="Φ_F", F="ƒ_ż", K="Ç_@",
    G="Γ_γ", Gamma="ɢ_ˌ", Phi_c="φ̂_ÿ", H="Ħ_A", S="Σ_S", Omega="Ω_z"
)


class IMASMOb3ect:
    def __init__(self):
        self.source   = pathlib.Path(__file__).read_text()
        self.register : Optional[IGLatticeCoordinate] = None
        self.log      : list = []
        self.state    = "VINIT"

    def VINIT(self):
        self.register = None
        self.state    = "VINIT"

    def TANCH(self):
        if self.register is not None:
            assert len(self.register.to_tuple()) == 12
            self.state = "READY"

    def AFWD(self):
        if self.register is None:
            self.register = CANONICAL
        self.state = "READY"

    def AREV(self):
        self.VINIT()

    def CLINK(self):
        self.AFWD(); self.ISCRIB()

    def ISCRIB(self):
        if self.register is None:
            raise RuntimeError("ISCRIB: no coordinate assigned")
        self.log.append(("ISCRIB", self.register.hash()))
        if self.state != "PARADOX":
            self.state = "VERIFIED"

    def FSPLIT(self):
        src = self.register if self.register else CANONICAL
        self.candidate_A = src
        self.candidate_B = src

    def FFUSE(self):
        if hasattr(self, "candidate_A") and hasattr(self, "candidate_B"):
            if self.candidate_A.to_json() == self.candidate_B.to_json():
                self.register = self.candidate_A
                self.state    = "VERIFIED"
            else:
                self.state = "PARADOX"
        else:
            self.register = CANONICAL
            self.state    = "VERIFIED"

    def EVALT(self):
        if self.register and self.state != "PARADOX":
            self.state = "VERIFIED"

    def EVALF(self):
        if not self.register:
            self.state = "FAILED"

    def IFIX(self):
        if self.register:
            self.log.append(("IFIX", {"coordinate_hash": self.register.hash(), "state": self.state}))

    def _domain_frobenius(self) -> bool:
        if not self.register:
            return False
        return self.register.hash() == IGLatticeCoordinate(**self.register.to_json()).hash()

    def bootstrap(self) -> bool:
        try:
            self.ISCRIB()
        except RuntimeError:
            pass
        self.state = "READY"
        self.AREV(); self.FSPLIT()
        self.AFWD(); self.FFUSE()
        self.CLINK(); self.IFIX()
        self.ISCRIB()
        return self._domain_frobenius()

    def verify(self) -> bool:
        print("=== IMASM Self-Imscription Ob3ect ===")
        domain_ok = self.bootstrap()
        if self.register:
            print(f"  Coordinate : {self.register.to_tuple()[:3]}... (12-tuple)")
            print(f"  Coord hash : {self.register.hash()[:16]}...")
        print(f"  Domain μ∘δ=id (lattice)      : {domain_ok}")
        frob_ok  = frobenius_phase(self.source)
        closure  = domain_ok and frob_ok
        print(f"Closure: {closure}")
        return closure


if __name__ == "__main__":
    sys.exit(0 if IMASMOb3ect().verify() else 1)
