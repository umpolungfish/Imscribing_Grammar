"""
para_vm.py — Practical Paraconsistent Universal Engine

Full ParaASM instruction set with Belnap FOUR belief tracking,
control flow, assembler, and I/O.

Instruction set:

  Frobenius core
    ENGAGR  %rN              force %rN to B
    FSPLIT  %rN %rM %rK      δ: co-multiply — all args → B
    FFUSE   %rN %rM %rK      μ: Belnap-join inputs → output (last arg)
    IFIX    %rN              fix %rN to T (linear constraint)

  Register ops
    MOVE    %rN %rM          belief(%rM) ← belief(%rN)
    CLEAR   %rN              belief(%rN) ← N (Void)

  Control flow
    JMP     label            unconditional jump
    JB      %rN label        jump if belief(%rN) == B
    JT      %rN label        jump if belief(%rN) == T
    JF      %rN label        jump if belief(%rN) == F
    JN      %rN label        jump if belief(%rN) == N
    CALL    label            push PC, jump
    RET                      pop and jump (HALT if stack empty)
    HALT                     stop

  Stack
    PUSH    %rN              push belief(%rN)
    POP     %rN              pop into %rN

  I/O
    EMIT    %rN              print belief(%rN)
    READ    %rN              read N/T/F/B from stdin into %rN

Assembly syntax:
  .label:                    label definition (standalone or before instruction)
  ; comment                  rest of line ignored
  %rN                        register N (any non-negative integer)
"""

from __future__ import annotations

import enum
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Belnap FOUR ────────────────────────────────────────────────────────────

class B4(enum.Enum):
    N = 'N'
    T = 'T'
    F = 'F'
    B = 'B'

_JOIN: dict[tuple[B4, B4], B4] = {
    (B4.N, B4.N): B4.N, (B4.N, B4.T): B4.T, (B4.N, B4.F): B4.F, (B4.N, B4.B): B4.B,
    (B4.T, B4.N): B4.T, (B4.T, B4.T): B4.T, (B4.T, B4.F): B4.B, (B4.T, B4.B): B4.B,
    (B4.F, B4.N): B4.F, (B4.F, B4.T): B4.B, (B4.F, B4.F): B4.F, (B4.F, B4.B): B4.B,
    (B4.B, B4.N): B4.B, (B4.B, B4.T): B4.B, (B4.B, B4.F): B4.B, (B4.B, B4.B): B4.B,
}

def b4_join(a: B4, b: B4) -> B4:
    return _JOIN[(a, b)]

_TO_FLUX = {B4.N: '00', B4.T: '01', B4.F: '10', B4.B: '11'}


# ── Register ───────────────────────────────────────────────────────────────

class ParaRegister:
    __slots__ = ('flux', 'value', 'paradox_count')

    def __init__(self) -> None:
        self.flux: str = '00'
        self.value: Optional[str] = None
        self.paradox_count: int = 0

    def engage(self) -> None:
        self.flux = '11'
        self.paradox_count += 1

    @property
    def is_fixed(self) -> bool:
        return self.value == 'FIXED'

    @property
    def is_active(self) -> bool:
        return self.flux != '00' or self.value is not None


# ── Instruction ────────────────────────────────────────────────────────────

@dataclass
class Instr:
    op: str
    args: list[str] = field(default_factory=list)
    source_line: str = ''

    def __str__(self) -> str:
        parts = [self.op] + self.args
        return '  ' + '  '.join(parts)


# ── Assembler ──────────────────────────────────────────────────────────────

_LABEL_RE = re.compile(r'^\s*(\.\w+)\s*:(.*)')

def assemble(text: str) -> tuple[list[Instr], dict[str, int]]:
    """
    Parse ParaASM source text into (program, label_map).
    label_map maps '.label' strings to instruction indices.
    """
    program: list[Instr] = []
    label_map: dict[str, int] = {}

    for raw in text.splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        m = _LABEL_RE.match(line)
        if m:
            label_map[m.group(1)] = len(program)
            line = m.group(2).strip()
            if not line:
                continue
        parts = line.split()
        if not parts:
            continue
        program.append(Instr(op=parts[0].upper(), args=parts[1:], source_line=raw.strip()))

    return program, label_map


# ── VM ─────────────────────────────────────────────────────────────────────

_CTRL_FLOW = frozenset({'JMP', 'JB', 'JT', 'JF', 'JN', 'CALL', 'RET', 'HALT'})

class ParaVM:
    """
    Practical Paraconsistent Universal Engine.
    Full ParaASM ISA with control flow, assembler, and I/O.
    """

    def __init__(self) -> None:
        self.registers: defaultdict[int, ParaRegister] = defaultdict(ParaRegister)
        self.belief: dict[int, B4] = {}
        self.program: list[Instr] = []
        self.label_map: dict[str, int] = {}
        self.pc: int = 0
        self.total_steps: int = 0
        self.cycles: int = 0
        self.call_stack: list[int] = []
        self.data_stack: list[B4] = []
        self.halted: bool = False

    # ── belief helpers ─────────────────────────────────────────────────────

    def belief_of(self, reg_id: int) -> B4:
        return self.belief.get(reg_id, B4.N)

    def set_belief(self, reg_id: int, val: B4) -> None:
        self.belief[reg_id] = val
        self.registers[reg_id].flux = _TO_FLUX[val]

    def engage(self, reg_id: int) -> None:
        self.registers[reg_id].engage()
        self.belief[reg_id] = B4.B

    # ── arg helpers ────────────────────────────────────────────────────────

    @staticmethod
    def parse_reg(arg: str) -> int:
        if arg.startswith('%r') and arg[2:].isdigit():
            return int(arg[2:])
        raise ValueError(f'expected %rN, got: {arg!r}')

    def resolve(self, label: str) -> int:
        if label not in self.label_map:
            raise KeyError(f'undefined label: {label!r}')
        return self.label_map[label]

    # ── load ───────────────────────────────────────────────────────────────

    def load(self, text: str) -> None:
        self.program, self.label_map = assemble(text)
        self.pc = 0
        self.halted = False

    def load_file(self, path: str | Path) -> None:
        self.load(Path(path).read_text())

    def append_instr(self, instr: Instr) -> None:
        """Append a single instruction without resetting PC."""
        self.program.append(instr)

    def add_label(self, label: str) -> None:
        """Define a label at the current end of program."""
        self.label_map[label] = len(self.program)

    # ── execution ──────────────────────────────────────────────────────────

    def step(self) -> bool:
        """Execute one instruction. Returns False when halted."""
        if self.halted or not self.program:
            return False
        if self.pc >= len(self.program):
            self.pc = 0
            self.cycles += 1
        instr = self.program[self.pc]
        self.pc += 1
        self.total_steps += 1
        self._exec(instr)
        return not self.halted

    def run(self, steps: Optional[int] = None) -> None:
        """Run until halted, KeyboardInterrupt, or steps exhausted."""
        n = 0
        try:
            while not self.halted:
                if steps is not None and n >= steps:
                    break
                if not self.step():
                    break
                n += 1
        except KeyboardInterrupt:
            pass

    def exec_one(self, instr: Instr) -> None:
        """Execute a single instruction directly (REPL interactive mode)."""
        self.total_steps += 1
        self._exec(instr)

    def _exec(self, instr: Instr) -> None:
        op = instr.op
        a  = instr.args

        def R(i: int) -> int:
            return self.parse_reg(a[i])

        def L(i: int) -> int:
            return self.resolve(a[i])

        if op == 'ENGAGR':
            self.engage(R(0))

        elif op == 'FSPLIT':
            for arg in a:
                self.engage(self.parse_reg(arg))

        elif op == 'FFUSE':
            if len(a) < 2:
                return
            joined = self.belief_of(self.parse_reg(a[0]))
            for arg in a[1:-1]:
                joined = b4_join(joined, self.belief_of(self.parse_reg(arg)))
            self.set_belief(self.parse_reg(a[-1]), joined)

        elif op == 'IFIX':
            r = R(0)
            self.registers[r].value = 'FIXED'
            self.set_belief(r, B4.T)

        elif op == 'MOVE':
            self.set_belief(R(1), self.belief_of(R(0)))

        elif op == 'CLEAR':
            r = R(0)
            self.registers[r].flux = '00'
            self.registers[r].value = None
            self.belief[r] = B4.N

        elif op == 'JMP':
            self.pc = L(0)

        elif op == 'JB':
            if self.belief_of(R(0)) == B4.B:
                self.pc = L(1)

        elif op == 'JT':
            if self.belief_of(R(0)) == B4.T:
                self.pc = L(1)

        elif op == 'JF':
            if self.belief_of(R(0)) == B4.F:
                self.pc = L(1)

        elif op == 'JN':
            if self.belief_of(R(0)) == B4.N:
                self.pc = L(1)

        elif op == 'CALL':
            self.call_stack.append(self.pc)
            self.pc = L(0)

        elif op == 'RET':
            if self.call_stack:
                self.pc = self.call_stack.pop()
            else:
                self.halted = True

        elif op == 'HALT':
            self.halted = True

        elif op == 'PUSH':
            self.data_stack.append(self.belief_of(R(0)))

        elif op == 'POP':
            val = self.data_stack.pop() if self.data_stack else B4.N
            self.set_belief(R(0), val)

        elif op == 'EMIT':
            r = R(0)
            b = self.belief_of(r).value
            fixed = ' [FIXED]' if self.registers[r].is_fixed else ''
            print(f'  %r{r} = {b}{fixed}')

        elif op == 'READ':
            r = R(0)
            try:
                raw = input(f'  read %r{r} (N/T/F/B): ').strip().upper()
                val = B4(raw) if raw in ('N', 'T', 'F', 'B') else B4.N
            except (EOFError, ValueError):
                val = B4.N
            self.set_belief(r, val)

        # Unknown ops: structural presence, no effect.

    # ── introspection ──────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        dist    = {v: 0 for v in B4}
        paradox = 0
        active  = 0
        fixed   = 0
        for rid in self.registers:
            r = self.registers[rid]
            dist[self.belief_of(rid)] += 1
            paradox += r.paradox_count
            if r.is_active:
                active += 1
            if r.is_fixed:
                fixed += 1
        return {
            'steps': self.total_steps, 'cycles': self.cycles,
            'pc': self.pc, 'active': active, 'fixed': fixed,
            'paradox': paradox, 'dist': dist, 'halted': self.halted,
        }

    def active_regs(self) -> list[tuple[int, B4, int, bool]]:
        """All registers that have been touched: (id, belief, paradox, is_fixed)."""
        rows = []
        seen = set(self.registers.keys()) | set(self.belief.keys())
        for rid in sorted(seen):
            r = self.registers[rid]
            if r.is_active or rid in self.belief:
                rows.append((rid, self.belief_of(rid), r.paradox_count, r.is_fixed))
        return rows

    def reset(self) -> None:
        self.__init__()
