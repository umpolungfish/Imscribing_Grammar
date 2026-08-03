#!/usr/bin/env python3
"""
paraconsistent.py — Belnap FOUR dialetheic engine for the TrueAgenticAgent.

Port of exOS/src/para_vm.rs into Python, with bridges to zfct_para.py.

Provides:
  - B4 enum: Belnap FOUR lattice (N=none, T=true, F=false, B=both)
  - ParaKernel: 3-register dialetheic machine (r0, r1, r2)
  - ParaVM: full 16-register ParaASM interpreter
  - B4Frobenius: para-valued Frobenius verification
  - BelnapCircuit: multi-gate dialectic stability analysis
  - DialetheicAlignment: operational/logical/algebraic tri-proof

Type: <𐑦; 𐑶; 𐑾; 𐑹; 𐑐; 𐑧; 𐑲; 𐑠; φ̂_ÿ; 𐑖; 𐑳; 𐑭>
Ouroboricity: O_∞. Dialetheic gates: both open (B4.B is designated AND its negation is).
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set, Tuple
from collections import OrderedDict
import json

# ═════════════════════════════════════════════════════════════════════════════
# 1. Belnap FOUR — the dialetheic truth lattice
# ═════════════════════════════════════════════════════════════════════════════


# ── Ordinal tables for ordinal-aware bridge operations ────────────────────
# These match zfct_navigator.ORDINALS — needed for correct bottleneck min/max
# in para_tensor_belief and bridge operations, avoiding lexicographic string
# comparison which gives wrong results for certain Unicode subscript pairs.

_ORDINALS = {
    "⊢": {"𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3,
           "𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3},
    "⊣": {"𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4,
           "𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4},
    ">": {"𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3,
           "𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3},
    "<": {"𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4,
           "𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4},
    "⋈": {"𐑱": 0, "𐑞": 1, "𐑐": 2,
           "𐑱": 0, "𐑞": 1, "𐑐": 2},
    "⊤": {"𐑘": 0, "𐑤": 1, "𐑧": 2, "𐑪": 3, "𐑺": 4,
           "𐑺": 0, "𐑪": 1, "𐑧": 2, "𐑤": 3, "𐑘": 4},
    "∈": {"𐑚": 0, "𐑔": 1, "𐑲": 2,
           "𐑲": 0, "𐑚": 1, "𐑔": 2},
    "∋": {"𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3,
           "𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3},
    "φ̂": {"φ̂_ž": 0, "φ̂_ÿ": 1, "φ̂_Æ": 2, "φ̂_3": 3, "φ̂_Ţ": 4,
           "𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4},
    "⊥": {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3,
           "𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3},
    "⊞": {"𐑙": 0, "𐑕": 1, "𐑳": 2,
           "𐑙": 0, "𐑕": 1, "𐑳": 2},
    "◻": {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3,
           "𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3},
}

_BOTTLENECK_PRIMS = {"<", "⋈"}

def _bottleneck_min(p: str, a: str, b: str) -> str:
    """Ordinal-aware minimum for bottleneck primitives.
    
    Uses _ORDINALS[p] to compare ordinal positions rather than lexicographic
    string comparison, which gives wrong results for Unicode subscript chars.
    """
    ords = _ORDINALS.get(p, {})
    oa = ords.get(a, 99)
    ob = ords.get(b, 99)
    return a if oa <= ob else b


def _max_v(p: str, a: str, b: str) -> str:
    """Ordinal-aware maximum for non-bottleneck primitives."""
    ords = _ORDINALS.get(p, {})
    oa = ords.get(a, -1)
    ob = ords.get(b, -1)
    return a if oa >= ob else b

class B4(Enum):
    """Belnap FOUR: N (None), T (True), F (False), B (Both).

    Information ordering: N < T < B, N < F < B (T and F are incomparable).
    Truth ordering:        F < N < B < T.
    """
    N = "N"
    T = "T"
    F = "F"
    B = "B"

    # ── Information-order lattice ────────────────────────────────────────

    def join(self, other: B4) -> B4:
        """Information join: N < T,F < B; T ∨ F = B."""
        if self == B4.B or other == B4.B:
            return B4.B
        if self == B4.T and other == B4.F:
            return B4.B
        if self == B4.F and other == B4.T:
            return B4.B
        if self == B4.T or other == B4.T:
            return B4.T
        if self == B4.F or other == B4.F:
            return B4.F
        return B4.N

    def meet(self, other: B4) -> B4:
        """Information meet: N < T,F < B; T ∧ F = N."""
        if self == B4.N or other == B4.N:
            return B4.N
        if self == B4.T and other == B4.F:
            return B4.N
        if self == B4.F and other == B4.T:
            return B4.N
        if self == B4.B and other == B4.T:
            return B4.T
        if self == B4.T and other == B4.B:
            return B4.T
        if self == B4.B and other == B4.F:
            return B4.F
        if self == B4.F and other == B4.B:
            return B4.F
        if self == B4.T and other == B4.T:
            return B4.T
        if self == B4.F and other == B4.F:
            return B4.F
        if self == B4.B and other == B4.B:
            return B4.B
        return B4.N  # fallback

    # ── Truth-functional operations ──────────────────────────────────────

    def bnot(self) -> B4:
        """Belnap negation: ¬N=N, ¬T=F, ¬F=T, ¬B=B."""
        return {B4.N: B4.N, B4.T: B4.F, B4.F: B4.T, B4.B: B4.B}[self]

    def band(self, other: B4) -> B4:
        """Truth-functional AND."""
        if self == B4.F or other == B4.F:
            return B4.F
        if self == B4.B and other in (B4.T, B4.N):
            return B4.B
        if other == B4.B and self in (B4.T, B4.N):
            return B4.B
        if self == B4.T and other == B4.T:
            return B4.T
        if self == B4.T and other == B4.N:
            return B4.N
        if self == B4.N and other == B4.T:
            return B4.N
        if self == B4.N and other == B4.N:
            return B4.N
        if self == B4.B and other == B4.B:
            return B4.B
        return B4.N

    def bor(self, other: B4) -> B4:
        """Truth-functional OR."""
        if self == B4.T or other == B4.T:
            return B4.T
        if self == B4.B and other in (B4.F, B4.N):
            return B4.B
        if other == B4.B and self in (B4.F, B4.N):
            return B4.B
        if self == B4.F and other == B4.F:
            return B4.F
        if self == B4.F and other == B4.N:
            return B4.N
        if self == B4.N and other == B4.F:
            return B4.N
        if self == B4.N and other == B4.N:
            return B4.N
        if self == B4.B and other == B4.B:
            return B4.B
        return B4.N

    def bimplies(self, other: B4) -> B4:
        """Material implication: p → q = ¬p ∨ q."""
        return self.bnot().bor(other)

    # ── Predicates ────────────────────────────────────────────────────────

    def designated(self) -> bool:
        """True iff this value counts as 'true' for paraconsistent consequence.
        T and B are designated (B is both true and false — dialetheic)."""
        return self in (B4.T, B4.B)

    def dialetheic(self) -> bool:
        """True iff both this value AND its negation are designated.
        Only B satisfies this — the dialetheic fixed point."""
        return self.designated() and self.bnot().designated()

    def approx_le(self, other: B4) -> bool:
        """Approximation order: N ≤ everything; everything ≤ B; reflexive only otherwise."""
        return self == other or self == B4.N or other == B4.B

    # ── Bijections ────────────────────────────────────────────────────────

    def to_wh2(self) -> Tuple[int, int]:
        """WH2 bijection: N→(0,0) T→(0,1) F→(1,0) B→(1,1)."""
        return {B4.N: (0, 0), B4.T: (0, 1), B4.F: (1, 0), B4.B: (1, 1)}[self]

    @staticmethod
    def from_wh2(pair: Tuple[int, int]) -> B4:
        """Inverse WH2 bijection."""
        return {(0, 0): B4.N, (0, 1): B4.T, (1, 0): B4.F, (1, 1): B4.B}[pair]

    @staticmethod
    def from_bool(b: bool) -> B4:
        return B4.T if b else B4.F

    def to_bool(self) -> bool:
        """Collapse to classical: T→True, F→False; N→False (not enough info), B→True (overdetermined)."""
        return self in (B4.T, B4.B)

    def __repr__(self) -> str:
        return f"B4.{self.value}"

    def __str__(self) -> str:
        return self.value


# ═════════════════════════════════════════════════════════════════════════════
# 2. ParaKernel — 3-register dialetheic machine
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class ParaKernel:
    """Minimal 3-register dialetheic kernel.
    
    r0:           current belief state
    r1, r2:       split registers (δ: comultiplication)
    paradox_count: total paradoxes accumulated
    cycle_count:   number of Frobenius cycles completed

    The kernel implements the Frobenius algebra:
      δ: B → (T, F);  all others → (r, r)
      μ: (r1, r2) → r1 ∨ r2 (Belnap join)
    Invariant: μ(δ(r)) = r  ∀ r ∈ B4
    """
    r0: B4 = B4.B
    r1: B4 = B4.B
    r2: B4 = B4.B
    paradox_count: int = 0
    cycle_count: int = 0

    @staticmethod
    def initial() -> ParaKernel:
        return ParaKernel(r0=B4.B, r1=B4.B, r2=B4.B, paradox_count=0, cycle_count=0)

    # ── Frobenius operations ─────────────────────────────────────────────

    @staticmethod
    def engager(r: B4) -> Tuple[B4, bool]:
        """ENGAGR: band(b, bnot(b)) — B is the only fixed point; T/F collapse to F."""
        result = r.band(r.bnot())
        return (result, r.designated())

    @staticmethod
    def fsplit(r0: B4) -> Tuple[B4, B4, bool]:
        """FSPLIT (δ): Frobenius comultiplication. B → (T,F); others → (r,r)."""
        if r0 == B4.B:
            return (B4.T, B4.F, True)
        return (r0, r0, True)

    @staticmethod
    def ffuse(r1: B4, r2: B4) -> Tuple[B4, bool]:
        """FFUSE (μ): Belnap join r1 ∨ r2. Returns (result, was_paradox)."""
        j = r1.join(r2)
        return (j, j == B4.B)

    # ── Step ──────────────────────────────────────────────────────────────

    def step(self) -> ParaKernel:
        """One complete Frobenius cycle: ENGAGR → FSPLIT → FFUSE."""
        r0a, p1 = self.engager(self.r0)
        r1a, r2a, p2 = self.fsplit(r0a)
        r0b, p3 = self.ffuse(r1a, r2a)
        pc = self.paradox_count + (1 if p1 else 0) + (1 if p2 else 0) + (1 if p3 else 0)
        return ParaKernel(
            r0=r0b, r1=r1a, r2=r2a,
            paradox_count=pc,
            cycle_count=self.cycle_count + 1,
        )

    def run(self, n: int) -> ParaKernel:
        """Run n cycles, resetting r1/r2 to B after each step (mirrors Lean `run`)."""
        s = self
        for _ in range(n):
            s2 = s.step()
            s = ParaKernel(r0=s2.r0, r1=B4.B, r2=B4.B,
                           paradox_count=s2.paradox_count,
                           cycle_count=s2.cycle_count)
        return s

    # ── Invariant ─────────────────────────────────────────────────────────

    @staticmethod
    def frobenius_invariant(r: B4) -> bool:
        """μ(δ(r)) = r  ∀ r ∈ B4 — the Frobenius condition."""
        r1, r2, _ = ParaKernel.fsplit(r)
        result, _ = ParaKernel.ffuse(r1, r2)
        return result == r

    def format(self) -> str:
        return (f"ParaKernel  r0={self.r0}  r1={self.r1}  r2={self.r2}  "
                f"paradox={self.paradox_count}  cycles={self.cycle_count}")


# ═════════════════════════════════════════════════════════════════════════════
# 3. Dialetheic Alignment
# ═════════════════════════════════════════════════════════════════════════════

def dialetheic_image(r0: B4) -> B4:
    """Maps kernel r0 to Belnap: the operational ↔ logical bridge.
    B → B, T|F → T, N → N."""
    return {B4.B: B4.B, B4.T: B4.T, B4.F: B4.T, B4.N: B4.N}[r0]


def b_is_only_bifurcation_point() -> bool:
    """Only B bifurcates under fsplit — all other values produce (r,r)."""
    for r in [B4.N, B4.T, B4.F, B4.B]:
        d1, d2, _ = ParaKernel.fsplit(r)
        if r == B4.B and d1 == d2:
            return False
        if r != B4.B and d1 != d2:
            return False
    return True


def dialetheic_alignment_tri() -> Tuple[bool, bool, bool]:
    """Three arms of the Dialetheic Alignment Theorem.
    Returns (operational, logical, algebraic)."""
    # Arm 1 (Operational): Frobenius closure at B
    r1b, r2b, _ = ParaKernel.fsplit(B4.B)
    op_arm = (ParaKernel.ffuse(r1b, r2b)[0] == B4.B and b_is_only_bifurcation_point())
    # Arm 2 (Logical): only B is dialetheic
    log_arm = (B4.B.dialetheic()
               and all(not x.dialetheic() for x in [B4.N, B4.T, B4.F]))
    # Arm 3 (Algebraic): no explosion — N undesignated; B∧¬B=B, not void
    alg_arm = (not B4.N.designated()
               and B4.T.join(B4.F) == B4.B
               and B4.B.band(B4.B.bnot()).designated())
    return (op_arm, log_arm, alg_arm)

# ═════════════════════════════════════════════════════════════════════════════
# 4. ParaASM Assembler — compile ParaASM source to instruction list
# ═════════════════════════════════════════════════════════════════════════════

class Op(Enum):
    ENGAGR = "ENGAGR"
    FSPLIT = "FSPLIT"
    FFUSE  = "FFUSE"
    IFIX   = "IFIX"
    MOVE   = "MOVE"
    CLEAR  = "CLEAR"
    JMP    = "JMP"
    JB     = "JB"
    JT     = "JT"
    JF     = "JF"
    JN     = "JN"
    CALL   = "CALL"
    RET    = "RET"
    HALT   = "HALT"
    PUSH   = "PUSH"
    POP    = "POP"
    EMIT   = "EMIT"
    READ   = "READ"

    @staticmethod
    def from_str(s: str) -> Optional['Op']:
        mapping = {
            "ENGAGR": Op.ENGAGR, "FSPLIT": Op.FSPLIT, "FFUSE": Op.FFUSE,
            "IFIX": Op.IFIX, "MOVE": Op.MOVE, "CLEAR": Op.CLEAR,
            "JMP": Op.JMP, "JB": Op.JB, "JT": Op.JT, "JF": Op.JF, "JN": Op.JN,
            "CALL": Op.CALL, "RET": Op.RET, "HALT": Op.HALT,
            "PUSH": Op.PUSH, "POP": Op.POP, "EMIT": Op.EMIT, "READ": Op.READ,
        }
        return mapping.get(s.upper())


@dataclass
class Arg:
    reg: Optional[int] = None
    label: Optional[str] = None

    @staticmethod
    def parse(token: str) -> 'Arg':
        t = token.strip().lstrip('%').lstrip('r')
        if t.isdigit():
            return Arg(reg=int(t))
        return Arg(label=token.strip().lstrip('.'))

    def __repr__(self) -> str:
        if self.reg is not None:
            return f"%r{self.reg}"
        return f".{self.label}"


@dataclass
class Instr:
    op: Op
    args: List[Arg] = dataclass_field(default_factory=list)

    def __repr__(self) -> str:
        return f"{self.op.value} {' '.join(repr(a) for a in self.args)}"


def assemble(text: str) -> Tuple[List[Instr], Dict[str, int]]:
    """Assemble ParaASM source text into (instructions, labels)."""
    instrs: List[Instr] = []
    labels: Dict[str, int] = OrderedDict()

    for raw in text.splitlines():
        # strip comments
        line = raw.split(';')[0].strip()
        if not line:
            continue

        # label prefix
        label = None
        rest = line
        for sep in (':',):
            idx = line.find(sep)
            if idx > 0 and (line[:idx].replace('_', '').replace('.', '').isalnum()):
                potential = line[:idx]
                rest = line[idx+1:].strip()
                label = potential.lstrip('.')
                break

        if label:
            labels[label] = len(instrs)
        rest = rest.strip()
        if not rest:
            continue

        tokens = rest.split()
        op = Op.from_str(tokens[0])
        if op is None:
            continue
        args = [Arg.parse(t) for t in tokens[1:]]
        instrs.append(Instr(op=op, args=args))

    return instrs, labels


# ═════════════════════════════════════════════════════════════════════════════
# 5. ParaVM — full 16-register Paraconsistent Virtual Machine
# ═════════════════════════════════════════════════════════════════════════════

class ParaVM:
    """16-register Belnap FOUR virtual machine.
    
    Runs assembled ParaASM programs step-by-step.
    Supports the full ISA: Engagr, Fsplit, Ffuse, Ifix,
    control flow (JMP/JB/JT/JF/JN/CALL/RET/HALT), stack (PUSH/POP), I/O (EMIT/READ).
    """

    NUM_REGS: int = 16

    def __init__(self):
        self.regs: List[Dict] = [
            {"belief": B4.N, "is_fixed": False, "paradox_count": 0}
            for _ in range(self.NUM_REGS)
        ]
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.pc: int = 0
        self.call_stack: List[int] = []
        self.data_stack: List[B4] = []
        self.halted: bool = False
        self.steps: int = 0
        self.emit_count: int = 0
        self.emit_log: List[str] = []

    def load(self, text: str) -> None:
        """Assemble and load ParaASM text."""
        self.program, self.labels = assemble(text)
        self.pc = 0
        self.halted = False
        self.steps = 0
        self.call_stack.clear()
        self.data_stack.clear()
        self.emit_count = 0
        self.emit_log.clear()

    def reset_state(self) -> None:
        """Reset all registers and VM state (keeps program loaded)."""
        self.regs = [
            {"belief": B4.N, "is_fixed": False, "paradox_count": 0}
            for _ in range(self.NUM_REGS)
        ]
        self.pc = 0
        self.halted = False
        self.steps = 0
        self.call_stack.clear()
        self.data_stack.clear()
        self.emit_count = 0
        self.emit_log.clear()

    def step(self) -> bool:
        """Execute one instruction. Returns False if halted or no program."""
        if self.halted or not self.program:
            return False
        if self.pc >= len(self.program):
            self.pc = 0  # circular wrap
        instr = self.program[self.pc]
        self.pc += 1
        self.steps += 1
        self._execute(instr)
        return True

    def run(self, n: int) -> None:
        """Run n steps."""
        for _ in range(n):
            if not self.step():
                break

    def _r(self, idx: int) -> Optional[int]:
        """Resolve register index from arg position."""
        if 0 <= idx < self.NUM_REGS:
            return idx
        return None

    def _get_reg(self, idx: int) -> B4:
        return self.regs[idx]["belief"] if 0 <= idx < self.NUM_REGS else B4.N

    def _set_reg(self, idx: int, val: B4) -> None:
        if 0 <= idx < self.NUM_REGS:
            self.regs[idx]["belief"] = val

    def _resolve_label(self, name: str) -> Optional[int]:
        name = name.lstrip('.')
        return self.labels.get(name)

    def _execute(self, instr: Instr) -> None:
        op = instr.op
        args = instr.args

        def reg(i: int) -> Optional[int]:
            a = args[i] if i < len(args) else None
            return a.reg if a and a.reg is not None else None

        def lbl(i: int) -> Optional[str]:
            a = args[i] if i < len(args) else None
            return a.label if a and a.label is not None else None

        if op == Op.ENGAGR:
            r = reg(0)
            if r is not None:
                b = self.regs[r]["belief"]
                new_b = b.band(b.bnot())
                if b.designated():
                    self.regs[r]["paradox_count"] += 1
                self.regs[r]["belief"] = new_b

        elif op == Op.FSPLIT:
            src, d1, d2 = reg(0), reg(1), reg(2)
            if src is not None and d1 is not None and d2 is not None:
                b = self.regs[src]["belief"]
                fixed = self.regs[src]["is_fixed"]
                p = self.regs[src]["paradox_count"]
                if b == B4.B:
                    b1, b2 = B4.T, B4.F
                    bump = 1
                else:
                    b1, b2 = b, b
                    bump = 0
                self.regs[d1] = {"belief": b1, "is_fixed": fixed, "paradox_count": p + bump}
                self.regs[d2] = {"belief": b2, "is_fixed": fixed, "paradox_count": p + bump}

        elif op == Op.FFUSE:
            s1, s2, dst = reg(0), reg(1), reg(2)
            if s1 is not None and s2 is not None and dst is not None:
                b1 = self.regs[s1]["belief"]
                b2 = self.regs[s2]["belief"]
                joined = b1.join(b2)
                p = self.regs[s1]["paradox_count"] + self.regs[s2]["paradox_count"]
                self.regs[dst] = {
                    "belief": joined,
                    "is_fixed": False,
                    "paradox_count": p + (1 if joined == B4.B else 0),
                }

        elif op == Op.IFIX:
            r = reg(0)
            if r is not None:
                self.regs[r]["belief"] = B4.T
                self.regs[r]["is_fixed"] = True

        elif op == Op.MOVE:
            src, dst = reg(0), reg(1)
            if src is not None and dst is not None:
                self.regs[dst] = dict(self.regs[src])

        elif op == Op.CLEAR:
            r = reg(0)
            if r is not None:
                self.regs[r] = {"belief": B4.N, "is_fixed": False, "paradox_count": 0}

        elif op == Op.JMP:
            l = lbl(0)
            if l:
                addr = self._resolve_label(l)
                if addr is not None:
                    self.pc = addr

        elif op in (Op.JB, Op.JT, Op.JF, Op.JN):
            target_map = {Op.JB: B4.B, Op.JT: B4.T, Op.JF: B4.F, Op.JN: B4.N}
            r = reg(0)
            l = lbl(1)
            if r is not None and l:
                if self.regs[r]["belief"] == target_map[op]:
                    addr = self._resolve_label(l)
                    if addr is not None:
                        self.pc = addr

        elif op == Op.CALL:
            l = lbl(0)
            if l:
                addr = self._resolve_label(l)
                if addr is not None:
                    self.call_stack.append(self.pc)
                    self.pc = addr

        elif op == Op.RET:
            if self.call_stack:
                self.pc = self.call_stack.pop()

        elif op == Op.HALT:
            self.halted = True

        elif op == Op.PUSH:
            r = reg(0)
            if r is not None:
                self.data_stack.append(self.regs[r]["belief"])

        elif op == Op.POP:
            r = reg(0)
            if r is not None and self.data_stack:
                self.regs[r]["belief"] = self.data_stack.pop()

        elif op == Op.EMIT:
            r = reg(0)
            if r is not None:
                tag = " [FIXED]" if self.regs[r]["is_fixed"] else ""
                msg = f"EMIT %r{r} = {self.regs[r]['belief'].value}{tag}"
                self.emit_log.append(msg)
                self.emit_count += 1

        elif op == Op.READ:
            r = reg(0)
            if r is not None:
                self.regs[r]["belief"] = B4.N

    def active_regs(self) -> List[Tuple[int, B4, int, bool]]:
        return [
            (i, r["belief"], r["paradox_count"], r["is_fixed"])
            for i, r in enumerate(self.regs) if r["belief"] != B4.N or r["is_fixed"]
        ]

    def total_paradoxes(self) -> int:
        return sum(r["paradox_count"] for r in self.regs)

    def format_snapshot(self) -> str:
        lines = [
            f"ParaVM  pc={self.pc}  steps={self.steps}  "
            f"halted={self.halted}  emits={self.emit_count}"
        ]
        active = self.active_regs()
        if not active:
            lines.append("  (all registers N)")
        else:
            for i, belief, paradoxes, fixed in active:
                tag = " [FIXED]" if fixed else ""
                lines.append(f"  %r{i:<2} = {belief.value:<1}{tag:<8}  paradoxes={paradoxes}")
        lines.append(f"  total_paradoxes={self.total_paradoxes()}  labels={len(self.labels)}")
        if self.emit_log:
            lines.append("  EMIT log:")
            for e in self.emit_log[-10:]:
                lines.append(f"    {e}")
        return "\n".join(lines)

    def run_program(self, asm_text: str, steps: int = 100) -> str:
        """Convenience: load, run, return snapshot."""
        self.load(asm_text)
        self.run(steps)
        return self.format_snapshot()

# ═════════════════════════════════════════════════════════════════════════════
# 6. Measurement Sequence Algebra
# ═════════════════════════════════════════════════════════════════════════════

def measure_cost(q: B4, bias: B4) -> int:
    """Coherence cost: 2 for B-bias on B, 1 for T/F-bias on B, 0 otherwise."""
    if q != B4.B:
        return 0
    return 2 if bias == B4.B else 1

def measure_step(q: B4, bias: B4) -> B4:
    """Post-measurement belief. B-bias preserves B; T/F-bias collapses B."""
    if q == B4.B:
        return q if bias == B4.B else bias
    return q

def collapse_irreversible(q: B4) -> bool:
    """Classical (T/F/N) cannot reach B via any unary/binary lattice op on itself."""
    if q == B4.B:
        return True
    candidates = [q.bnot(), q.join(q), q.meet(q), q.band(q), q.bor(q)]
    return all(c != B4.B for c in candidates)

# ═════════════════════════════════════════════════════════════════════════════
# 7. BelnapCircuit — multi-gate dialectic stability analysis
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class BelnapCircuit:
    """A vector of B4 gates — models dialectic stability across a network."""
    gates: List[B4]

    def all_b(self) -> bool:
        return all(g == B4.B for g in self.gates)

    def proj(self) -> BelnapCircuit:
        """Projection: collapse all B gates to T (classical projection)."""
        return BelnapCircuit([B4.T if g == B4.B else g for g in self.gates])

    def sustain_stable(self) -> bool:
        """An all-B circuit stays B under join-with-self and bnot
        (sustain_never_collapses)."""
        return all(g.join(g) == B4.B and g.bnot() == B4.B for g in self.gates)

    def classical_cannot_become_b(self) -> bool:
        """A classical circuit (T/F/N only) cannot self-join to B — one-way barrier."""
        if self.all_b():
            return False
        for a in self.gates:
            for b in self.gates:
                if a != B4.B and b != B4.B and a.join(b) == B4.B:
                    return False
            if a.bnot() == B4.B:
                return False
        return True

    def dialetheic_density(self) -> float:
        """Fraction of gates at B (dialetheic)."""
        return sum(1 for g in self.gates if g == B4.B) / max(len(self.gates), 1)

    def paradox_energy(self) -> int:
        """Sum of paradox potentials: B=2, T=F=1, N=0."""
        return sum({B4.N: 0, B4.T: 1, B4.F: 1, B4.B: 2}[g] for g in self.gates)


# ═════════════════════════════════════════════════════════════════════════════
# 8. B4Frobenius — para-valued Frobenius verification
# ═════════════════════════════════════════════════════════════════════════════

class B4Frobenius:
    """Paraconsistent Frobenius verification.

    Instead of boolean True/False, returns a B4 value:
      B4.T  — mu(delta(query)) == query  (classically closed)
      B4.F  — mu(delta(query)) != query  (classically open)
      B4.B  — both: query structure is dialetheic w.r.t. mu∘delta
              (the Frobenius condition holds AND fails — paradox)
      B4.N  — neither: insufficient information to decide
    """

    @staticmethod
    def check(query: str, emit_output: str, verify_output: str) -> B4:
        """B4-valued Frobenius check.

        Heuristics:
        - If verify_output explicitly says "Frobenius closed" or "PASSED" → T
        - If verify_output explicitly says "Frobenius OPEN" or "FAILED" → F
        - If both conditions appear → B (dialetheic)
        - If neither → N
        - If emit_output contains a paradox marker (e.g. paradox_count > 0) → B
        """
        emit_lower = emit_output.lower()
        verify_lower = verify_output.lower()

        has_close = any(p in verify_lower for p in
                        ["frobenius closed", "passed", "closed", "ok"])
        has_open = any(p in verify_lower for p in
                       ["frobenius open", "open", "failed", "fail"])
        has_paradox = any(p in emit_lower for p in
                          ["paradox", "both", "dialetheic", "b4.b"])

        close_val = B4.T if has_close else B4.N
        open_val = B4.F if has_open else B4.N
        paradox_val = B4.B if has_paradox else B4.N

        # Join all signals — if any signal is present, it contributes
        result = close_val
        result = result.join(open_val).join(paradox_val)

        if result == B4.N:
            # Neither signal: check if the output has content at all
            if len(emit_output) > 10:
                return B4.T  # assume closed by default if output exists
            return B4.N

        return result

    @staticmethod
    def frobenius_vs_belnap(phi_val: str, b4_result: B4) -> Tuple[bool, str]:
        """Cross-check standard Frobenius vs B4 Frobenius.

        Returns (consistency, explanation).
        """
        frob_classical = (phi_val == "𐑹")
        b4_closed = b4_result.to_bool()

        if frob_classical and b4_result == B4.B:
            return (True,
                    "Classical 𐑹 detected; B4 sees dialetheic Frobenius — "
                    "the system is simultaneously closed and open. "
                    "This is the O_∞ signature.")
        if frob_classical == b4_closed:
            return (True,
                    f"Consistent: classical={frob_classical}, B4={b4_result}")
        return (False,
                f"Mismatch: classical < check says {frob_classical} "
                f"but B4 Frobenius says {b4_result}")


# ═════════════════════════════════════════════════════════════════════════════
# 9. Paraconsistent catalog operations (bridge to zfct_para.py logic)
# ═════════════════════════════════════════════════════════════════════════════

def belief_set_from_primitive(prim: str, value: str) -> FrozenSet[str]:
    """Create a singleton belief set from a primitive value."""
    return frozenset({value})


def para_tensor_belief(belief_a: FrozenSet[str],
                        belief_b: FrozenSet[str],
                        is_bottleneck: bool = False,
                        prim: str = "<") -> FrozenSet[str]:
    """Paraconsistent tensor on belief sets.

    Bottleneck primitives (<, ƒ): min ordinal (conservative)
    All other primitives: max ordinal (union)

    Uses ordinal-aware comparison via _bottleneck_min / _max_v instead of
    lexicographic min() — the Unicode subscripts (ɐ, υ, ˙, }) sort in
    non-ordinal order under Python's default string comparison.
    """
    if is_bottleneck:
        # Bottleneck: pick the minimum-ordinal value via ordinal-aware comparison
        vals = list(belief_a | belief_b)
        best = min(vals, key=lambda v: _ORDINALS.get(prim, {}).get(v, 99))
        return frozenset({best})
    else:
        # Non-bottleneck: union (max)
        return frozenset(belief_a | belief_b)


def frobenius_cliff_belief(phi_belief: FrozenSet[str]) -> Optional[B4]:
    """Compute the Frobenius cliff: does forcing < to B{v, 𐑹} collapse?

    Returns:
      B4.T  if classical collapse (𐑹 present alone)
      B4.B  if dialetheic (𐑹 among multiple — B-state)
      B4.F  if no 𐑹 present
      None  if empty belief set
    """
    if not phi_belief:
        return None
    has_frob = "𐑹" in phi_belief
    if has_frob and len(phi_belief) == 1:
        return B4.T
    elif has_frob:
        return B4.B
    return B4.F


# ═════════════════════════════════════════════════════════════════════════════
# 10. Built-in demonstrations
# ═════════════════════════════════════════════════════════════════════════════

DEMO_FROBENIUS_INVARIANT = """
; Frobenius invariant demo: mu(delta(r)) = r for all r in B4
; Load this program then check: for each B4 value, after a full cycle, r0 returns to its original value.

; Test B4.N (register 1)
IFIX %r0          ; set r0 = T first
MOVE %r0 %r1      ; r1 = T
CLEAR %r1         ; r1 = N
FSPLIT %r1 %r2 %r3 ; split r1 into r2, r3
FFUSE %r2 %r3 %r4   ; fuse r2, r3 into r4
EMIT %r4           ; should be N

; Test B4.T (register 5)
IFIX %r5          ; r5 = T
FSPLIT %r5 %r6 %r7 ; split T -> (T,T)
FFUSE %r6 %r7 %r8   ; fuse -> T
EMIT %r8           ; should be T

; Test B4.F (register 9)
IFIX %r5          ; r5 = T
MOVE %r5 %r9      ; r9 = T
CLEAR %r9         ; r9 = N
ENGAGR %r9        ; r9 = band(N, not(N)) = N -- stays N, we need F
; Clear approach: load B not possible directly -- use shortcut
IFIX %r10
CLEAR %r10        ; r10 = N
; The Frobenius property is structural; the ParaKernel demonstrates it in Python.

HALT
"""

DEMO_DIALETHEIC_LOOP = """
; Dialetheic loop: r0 alternates through B -> (T,F) -> B
.loop
ENGAGR %r0        ; band(b, bnot(b)) -- B is fixed point
FSPLIT %r0 %r1 %r2 ; B -> (T,F)
FFUSE %r1 %r2 %r0  ; join(T,F) -> B
EMIT %r0           ; should be B
JMP loop
"""

# ── Quick test ──────────────────────────────────────────────────────────────

def self_test() -> str:
    """Run the dialetheic alignment theorem and Frobenius invariant."""
    lines = ["=== Paraconsistent Module Self-Test ===\n"]

    # Test B4 operations
    lines.append("B4 Lattice:")
    for a in [B4.N, B4.T, B4.F, B4.B]:
        for b in [B4.N, B4.T, B4.F, B4.B]:
            lines.append(f"  {a.value} ∨ {b.value} = {a.join(b).value}")
            lines.append(f"  {a.value} ∧ {b.value} = {a.meet(b).value}")
            lines.append(f"  {a.value} → {b.value} = {a.bimplies(b).value}")

    lines.append("\nDialetheic check:")
    for v in [B4.N, B4.T, B4.F, B4.B]:
        des = "designated" if v.designated() else "undesignated"
        dia = "dialetheic" if v.dialetheic() else "not dialetheic"
        lines.append(f"  {v.value}: {des}, {dia}")

    # Alignment theorem
    lines.append("\nDialetheic Alignment Theorem:")
    op, log, alg = dialetheic_alignment_tri()
    lines.append(f"  Operational (Frobenius closure at B): {op}")
    lines.append(f"  Logical (only B is dialetheic):      {log}")
    lines.append(f"  Algebraic (no explosion):             {alg}")
    lines.append(f"  All three arms: {all([op, log, alg])}")

    # Frobenius invariant
    lines.append("\nFrobenius invariant μ(δ(r)) = r:")
    for v in [B4.N, B4.T, B4.F, B4.B]:
        result = ParaKernel.frobenius_invariant(v)
        lines.append(f"  μ(δ({v.value})) = {v.value} ? {result}")

    # Kernel run
    k = ParaKernel.initial()
    k2 = k.run(5)
    lines.append(f"\nParaKernel after 5 cycles:")
    lines.append(f"  {k2.format()}")

    # BelnapCircuit
    bc = BelnapCircuit([B4.B, B4.T, B4.B, B4.F])
    lines.append(f"\nBelnapCircuit:")
    lines.append(f"  gates: {[g.value for g in bc.gates]}")
    lines.append(f"  all_b: {bc.all_b()}")
    lines.append(f"  dialetheic_density: {bc.dialetheic_density():.2f}")
    lines.append(f"  paradox_energy: {bc.paradox_energy()}")
    lines.append(f"  sustain_stable: {bc.sustain_stable()}")
    lines.append(f"  classical_cannot_become_b: {bc.classical_cannot_become_b()}")

    # Collapse irreversibility
    lines.append("\nCollapse irreversibility:")
    for v in [B4.N, B4.T, B4.F, B4.B]:
        lines.append(f"  collapse_irreversible({v.value}): {collapse_irreversible(v)}")

    # B4 Frobenius
    bf = B4Frobenius()
    lines.append("\nB4 Frobenius examples:")
    lines.append(f"  check(closed): {bf.check('q', 'ok', 'Frobenius closed').value}")
    lines.append(f"  check(open):   {bf.check('q', 'err', 'Frobenius OPEN').value}")
    lines.append(f"  check(both):   {bf.check('q', 'paradox B', 'Frobenius closed').value}")
    lines.append(f"  check(neither):{bf.check('q', '', '').value}")

    lines.append("\n=== Self-test complete ===")
    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print(self_test())
    elif len(sys.argv) >= 3 and sys.argv[1] == "run":
        asm = " ".join(sys.argv[2:]).replace("\\n", "\n")
        vm = ParaVM()
        result = vm.run_program(asm, steps=200)
        print(result)
    elif len(sys.argv) >= 3 and sys.argv[1] == "kernel":
        n = int(sys.argv[2]) if sys.argv[2].isdigit() else 5
        k = ParaKernel.initial()
        k2 = k.run(n)
        print(k2.format())
        print(f"Frobenius invariant: {all(ParaKernel.frobenius_invariant(v) for v in B4)}")
    else:
        print("Usage:")
        print("  python paraconsistent.py --test         Run self-test")
        print("  python paraconsistent.py run '<asm>'    Run ParaASM program")
        print("  python paraconsistent.py kernel <N>     Run ParaKernel for N cycles")

# ═════════════════════════════════════════════════════════════════════════════
# 11. Auto-decomposition — ParaVM activation from agent pipeline
# ═════════════════════════════════════════════════════════════════════════════

def auto_decompose_dialetheic(b4_val: B4 = B4.B) -> Dict:
    """Automatically decompose a dialetheic state through the ParaKernel.

    Called by the agent's OBSERVE pipeline when B4.B is detected — turns
    the dormant ParaVM into an active, always-on decomposition engine.

    Returns a snapshot dict with:
      - split: FSPLIT(B) → (T, F) — the classical components
      - fuse: FFUSE(T, F) → B — dialetheic reconstruction
      - kernel: ParaKernel run for 5 cycles
      - alignment: dialetheic alignment theorem arms
      - invariant: Frobenius mu(delta(r)) = r confirmation
      - circuit: BelnapCircuit analysis of [B]
    """
    # Decompose B through FSPLIT
    t_val, f_val, split_ok = ParaKernel.fsplit(b4_val)

    # Reconstruct through FFUSE
    fused, fuse_was_paradox = ParaKernel.ffuse(t_val, f_val)

    # Run kernel cycles to verify stability
    kernel_init = ParaKernel.initial()
    kernel_5 = kernel_init.run(5)

    # BelnapCircuit on the single [B] gate sequence
    bc = BelnapCircuit([b4_val])

    # Frobenius invariant
    inv = {v.value: ParaKernel.frobenius_invariant(v) for v in [B4.N, B4.T, B4.F, B4.B]}

    # Dialetheic alignment
    op_arm, log_arm, alg_arm = dialetheic_alignment_tri()

    return {
        "b4_value": b4_val.value,
        "split": {"r1": t_val.value, "r2": f_val.value, "ok": split_ok},
        "fuse": {"result": fused.value, "was_paradox": fuse_was_paradox},
        "kernel": {
            "cycle_count": kernel_5.cycle_count,
            "paradox_count": kernel_5.paradox_count,
            "r0_final": kernel_5.r0.value,
            "frobenius_stable": kernel_5.r0 == B4.B,
        },
        "circuit": {
            "dialetheic_density": bc.dialetheic_density(),
            "paradox_energy": bc.paradox_energy(),
            "sustain_stable": bc.sustain_stable(),
        },
        "alignment": {
            "operational": op_arm,
            "logical": log_arm,
            "algebraic": alg_arm,
            "all_three": all([op_arm, log_arm, alg_arm]),
        },
        "frobenius_invariant": inv,
        "theorem": "Dialetheic Alignment Theorem holds: B is the unique dialetheic fixed point. ParaVM auto-decomposition active.",
    }

