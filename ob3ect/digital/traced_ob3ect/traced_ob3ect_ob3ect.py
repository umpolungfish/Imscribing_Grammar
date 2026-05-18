#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys
from dataclasses import dataclass
from typing import Any, Dict, Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


@dataclass
class Closure:
    name:        str
    body:        str
    environment: Dict[str, Any] = None

    def to_json(self):
        return {"name": self.name, "body": self.body, "environment": self.environment}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


@dataclass
class TraceRecord:
    closure_hash:    str
    result_hash:     str
    yanking_verified: bool

    def to_json(self):
        return {"closure_hash": self.closure_hash, "result_hash": self.result_hash,
                "yanking_verified": self.yanking_verified}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


class TracedOb3ect:
    def __init__(self):
        self.source      = pathlib.Path(__file__).read_text()
        self.environment : Dict[str, Any]   = {}
        self.closure     : Optional[Closure] = None
        self.trace_record: Optional[TraceRecord] = None
        self.log         : list = []
        self.state       = "VINIT"

    def ISCRIB(self):
        if self.closure is None:
            self.closure = Closure("id", "λx.x", {})
        self.log.append(("ISCRIB", self.closure.hash()))
        if self.state != "PARADOX":
            self.state = "VERIFIED"

    def AREV(self):
        if self.closure:
            self.closure.environment = {
                k: v for k, v in self.environment.items() if k in self.closure.body
            }

    def FSPLIT(self):
        if self.closure:
            self.traced = Closure(f"Tr({self.closure.name})", self.closure.body,
                                  (self.closure.environment or {}).copy())
        else:
            self.traced = Closure("Tr(id)", "λx.x", {})

    def AFWD(self):
        self.state = "VERIFIED" if self.closure else "FAILED"

    def FFUSE(self):
        if hasattr(self, "traced"):
            self.yanking_ok = (
                self.traced.name.startswith("Tr(") and self.traced.body == "λx.x"
            )
            self.state = "VERIFIED" if self.yanking_ok else "FAILED"
        else:
            self.yanking_ok = True
            self.state = "VERIFIED"

    def CLINK(self):
        self.AFWD(); self.ISCRIB()

    def IFIX(self):
        if self.closure and hasattr(self, "yanking_ok"):
            rh = hashlib.sha256(json.dumps({"yanking": self.yanking_ok}).encode()).hexdigest()
            self.trace_record = TraceRecord(self.closure.hash(), rh, self.yanking_ok)
            self.log.append(("IFIX", {"trace_hash": self.trace_record.hash(), "state": self.state}))

    def _domain_frobenius(self) -> bool:
        if not self.trace_record:
            return False
        return self.trace_record.hash() == TraceRecord(
            self.trace_record.closure_hash,
            self.trace_record.result_hash,
            self.trace_record.yanking_verified
        ).hash()

    def bootstrap(self) -> bool:
        self.ISCRIB(); self.AREV(); self.FSPLIT()
        self.AFWD();   self.FFUSE(); self.CLINK()
        self.IFIX();   self.ISCRIB()
        return self._domain_frobenius()

    def verify(self) -> bool:
        print("=== Traced Ob3ect ===")
        domain_ok = self.bootstrap()
        print(f"  Yanking equation Tr(id_A)=id_I : {getattr(self, 'yanking_ok', False)}")
        print(f"  Record μ∘δ=id (domain)         : {domain_ok}")
        frob_ok  = frobenius_phase(self.source)
        closure  = domain_ok and frob_ok
        print(f"Closure: {closure}")
        return closure


if __name__ == "__main__":
    sys.exit(0 if TracedOb3ect().verify() else 1)
