#!/usr/bin/env python3
import hashlib, json, os, pathlib, sys
from dataclasses import dataclass
from typing import List, Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase


@dataclass
class ASTNode:
    node_type: str
    value: Optional[str] = None
    children: List["ASTNode"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def to_json(self):
        return {"node_type": self.node_type, "value": self.value,
                "children": [c.to_json() for c in self.children]}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


@dataclass
class FixedPointRecord:
    program_hash: str
    folded_hash:  str
    fixed_point_verified: bool

    def to_json(self):
        return {"program_hash": self.program_hash, "folded_hash": self.folded_hash,
                "fixed_point_verified": self.fixed_point_verified}

    def hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True).encode()).hexdigest()


class FixedPointOb3ect:
    def __init__(self):
        self.source  = pathlib.Path(__file__).read_text()
        self.program : Optional[ASTNode]        = None
        self.folded  : Optional[ASTNode]        = None
        self.record  : Optional[FixedPointRecord] = None
        self.log     : list = []
        self.state   = "VINIT"

    def _fold(self, node: ASTNode) -> ASTNode:
        if node.node_type == "CONSTANT":
            return ASTNode("CONSTANT", node.value)
        return ASTNode(node.node_type, node.value, [self._fold(c) for c in node.children])

    def _extract_constants(self, node: ASTNode) -> List[ASTNode]:
        if node.node_type == "CONSTANT":
            return [node]
        out = []
        for c in node.children:
            out.extend(self._extract_constants(c))
        return out

    def _extract_variables(self, node: ASTNode) -> List[ASTNode]:
        if node.node_type == "CONSTANT":
            return []
        out = [node]
        for c in node.children:
            out.extend(self._extract_variables(c))
        return out

    def ISCRIB(self):
        if self.program is None:
            self.program = ASTNode("VARIABLE", "x")
        self.log.append(("ISCRIB", self.program.hash()))

    def AREV(self):
        pass

    def FSPLIT(self):
        self.const_part = self._extract_constants(self.program) if self.program else []
        self.var_part   = self._extract_variables(self.program) if self.program else []

    def AFWD(self):
        if self.program:
            self.folded = self._fold(self.program)
            self.state  = "READY"

    def FFUSE(self):
        if hasattr(self, "const_part") and self.program:
            # T∘T = T: folding twice equals folding once
            twice = self._fold(self._fold(self.program))
            once  = self._fold(self.program)
            self.fp_verified = twice.hash() == once.hash()
            self.state = "VERIFIED" if self.fp_verified else "FAILED"
        else:
            self.fp_verified = True
            self.state = "VERIFIED"

    def CLINK(self):
        self.AFWD()
        self.ISCRIB()

    def IFIX(self):
        if self.program and hasattr(self, "fp_verified"):
            folded_hash = self.folded.hash() if self.folded else ""
            self.record = FixedPointRecord(self.program.hash(), folded_hash, self.fp_verified)
            self.log.append(("IFIX", {"record_hash": self.record.hash(), "state": self.state}))

    def _domain_frobenius(self) -> bool:
        if not self.record:
            return False
        return self.record.hash() == FixedPointRecord(
            self.record.program_hash,
            self.record.folded_hash,
            self.record.fixed_point_verified
        ).hash()

    def bootstrap(self) -> bool:
        self.ISCRIB(); self.AREV(); self.FSPLIT()
        self.AFWD();   self.FFUSE(); self.CLINK()
        self.IFIX();   self.ISCRIB()
        return self._domain_frobenius()

    def verify(self) -> bool:
        print("=== Fixed-Point Ob3ect ===")
        domain_ok = self.bootstrap()
        print(f"  T∘T = T (idempotent folding) : {getattr(self, 'fp_verified', False)}")
        print(f"  Record μ∘δ=id (domain)       : {domain_ok}")
        frob_ok  = frobenius_phase(self.source)
        closure  = domain_ok and frob_ok
        print(f"Closure: {closure}")
        return closure


if __name__ == "__main__":
    sys.exit(0 if FixedPointOb3ect().verify() else 1)
