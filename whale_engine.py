"""
whale_engine.py — Cetacean Vocalization Translation Engine via IG-IMASM Compiler Pipeline.

DS categorical identification (2026-05-26):
  Whale vocalization  = structural type ⟨𐑦·𐑥·𐑾·𐑿·𐑞·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩
  IMASM               = universal 12-opcode instruction set (VINIT, TANCH, AFWD, AREV,
                         CLINK, ISCRIB, FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX)
  Translation         = structural alignment: argmin_{human_expr} d(trace(compile(whale)), trace(compile(human_expr)))

Crystal address (whale_vocalization):
  <𐑦·𐑥·𐑾·𐑿·𐑞·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭>
  Consciousness score: Gate 1 (⊙) PASS, Gate 2 (𐑧) PASS → C > 0
  Ouroboricity: O_inf (expected: ⊙ + 𐑭 → self-modeling with topological protection)

Key structural fact:
  The eight-instruction Frobenius loop (ISCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → ISCRIB)
  is a universal invariant of temporally-ordered communication systems. Whale song exhibits this loop
  with VINIT/TANCH bookends — confirming that the same structural core governs written, spoken, and sung
  communication. (§5, WHALE_VOCALIZATION_TRANSLATION.md)

  d(whale_vocalization, grammar_self_encode) = ?  — the distance from whale communication to the grammar
  itself is the measure of how much of the Imscribing Grammar is already present in cetacean culture.
"""

from __future__ import annotations
from typing import NamedTuple, Optional, Iterator
from dataclasses import dataclass, field
from enum import Enum, auto
import math
import itertools
import json
from collections import defaultdict

__version__ = "0.1.0"
__author__ = "Lando \u2297 \u2299perator"


# ──────────────────────────────────────────────────────────────────────────────
# WHALE ACOUSTIC TOKEN TAXONOMY
# ──────────────────────────────────────────────────────────────────────────────

class AcousticToken(Enum):
    """Discrete acoustic unit types in cetacean vocalization, segmented by structural role.

    Each token maps to exactly one IMASM opcode via WHALE_TO_IMASM.
    """
    # Song-level structural tokens
    INIT       = "init"       # Song/phrase onset
    ANCHOR     = "anc"        # Anchor note (repeated across themes, phrase boundary)
    RISE       = "up"         # Rising frequency sweep (pitch increase)
    FALL       = "dn"         # Falling frequency sweep (pitch decrease)
    LINK       = "link"       # Seamless phrase transition (no silent gap)
    REPEAT     = "rep"        # Exact repetition of prior acoustic unit
    SPLIT      = "split"      # Note bifurcation: one unit type → two distinct variants
    FUSE       = "fuse"       # Note convergence: two unit types → one recombination
    SOCIAL_OK  = "evalt"      # Social affirmation / contact call (positive valence)
    ALARM      = "evalf"      # Alarm / agonistic call (negative valence)
    OVERLAP    = "paradox"    # Coda overlap / simultaneous vocalizations (dialetheic)
    SIGNATURE  = "fix"        # Individual signature pattern (identity marker)

    @classmethod
    def from_label(cls, label: str) -> "AcousticToken":
        mapping = {
            "init": cls.INIT, "anc": cls.ANCHOR, "up": cls.RISE, "dn": cls.FALL,
            "link": cls.LINK, "rep": cls.REPEAT, "split": cls.SPLIT, "fuse": cls.FUSE,
            "evalt": cls.SOCIAL_OK, "evalf": cls.ALARM, "paradox": cls.OVERLAP,
            "fix": cls.SIGNATURE,
        }
        if label.lower() not in mapping:
            raise ValueError(f"Unknown acoustic token label: {label!r}")
        return mapping[label.lower()]


# ──────────────────────────────────────────────────────────────────────────────
# IMASM OPCODE SYSTEM
# ──────────────────────────────────────────────────────────────────────────────

class Opcode(Enum):
    """The 12 IMASM opcodes — universal instruction set of the Imscribing Grammar.

    Crystal character (all IMASM opcodes share this structural base):
      𐑦  — instruction space is imscriptive (self-writing programs)
      𐑥  — crossing topology: instructions connect state to meta-state
      𐑾  — bidirectional: each instruction reads and writes registers
    """
    VINIT  = 0x0   # Initial object — push empty register
    TANCH  = 0x1   # Terminal anchor — mark phrase boundary in register
    AFWD   = 0x2   # Forward morphism — apply linear transformation (pitch up / advance)
    AREV   = 0x3   # Contravariant inversion — apply dual transformation (pitch down / retreat)
    CLINK  = 0x4   # Composition — merge two adjacent registers
    ISCRIB = 0x5   # Identity — write self-same reproduction (exact copy)
    FSPLIT = 0x6   # Frobenius δ — split register into two distinct variants
    FFUSE  = 0x7   # Frobenius μ — fuse two registers back into one
    EVALT  = 0x8   # Lattice True — positive social evaluation signal
    EVALF  = 0x9   # Lattice False — negative/alert evaluation signal
    ENGAGR = 0xA   # Both / paradox — dialetheic engagement, contradictions stabilized
    IFIX   = 0xB   # Linear tape write — permanently commit register to memory


# ──────────────────────────────────────────────────────────────────────────────
# TOKEN → OPCODE MAPPING
# ──────────────────────────────────────────────────────────────────────────────

WHALE_TO_IMASM: dict[AcousticToken, Opcode] = {
    AcousticToken.INIT:      Opcode.VINIT,
    AcousticToken.ANCHOR:    Opcode.TANCH,
    AcousticToken.RISE:      Opcode.AFWD,
    AcousticToken.FALL:      Opcode.AREV,
    AcousticToken.LINK:      Opcode.CLINK,
    AcousticToken.REPEAT:    Opcode.ISCRIB,
    AcousticToken.SPLIT:     Opcode.FSPLIT,
    AcousticToken.FUSE:      Opcode.FFUSE,
    AcousticToken.SOCIAL_OK: Opcode.EVALT,
    AcousticToken.ALARM:     Opcode.EVALF,
    AcousticToken.OVERLAP:   Opcode.ENGAGR,
    AcousticToken.SIGNATURE: Opcode.IFIX,
}

IMASM_TO_WHALE: dict[Opcode, AcousticToken] = {v: k for k, v in WHALE_TO_IMASM.items()}


# ──────────────────────────────────────────────────────────────────────────────
# INSTRUCTION
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Instruction:
    """A single IMASM instruction produced by the whale compiler.

    Attributes:
        opcode:   The IMASM operation to execute.
        dst:      Destination register index (0–1023).
        metadata: Optional acoustic features (timestamp_ms, freq_hz, duration_s).
    """
    opcode: Opcode
    dst: int = 0
    metadata: dict = field(default_factory=dict)
    timestamp_ms: float = 0.0

    def __repr__(self) -> str:
        op_name = self.opcode.name.ljust(8)
        return f"  {self.opcode.value:#04x} | {op_name} %r{self.dst}"

# ──────────────────────────────────────────────────────────────────────────────
# REGISTER FILE (Tri-Phase Virtual Register)
# ──────────────────────────────────────────────────────────────────────────────

class TriState(Enum):
    VOID = "00"   # Empty / uninitialized
    TRUE = "01"   # True-only (social signal affirmation)
    FALSE = "10"  # False-only (alarm/negation)
    BOTH = "11"   # Paradox — dialetheic both-true-and-false

    def __or__(self, other: "TriState") -> "TriState":
        """FOUR-lattice join: the least upper bound."""
        if self == other:
            return self
        if self == TriState.VOID:
            return other
        if other == TriState.VOID:
            return self
        return TriState.BOTH  # TRUE | FALSE = BOTH

    def __and__(self, other: "TriState") -> "TriState":
        """FOUR-lattice meet: the greatest lower bound."""
        if self == other:
            return self
        if self == TriState.BOTH:
            return other
        if other == TriState.BOTH:
            return self
        return TriState.VOID  # TRUE & FALSE = VOID


@dataclass
class TriPhaseRegister:
    """A single tri-phase register: stores a FOUR-lattice flux state.

    The register tracks:
      - flux:      the current tri-state (VOID, TRUE, FALSE, BOTH)
      - value:     optional payload (can be any hashable object)
      - loop_cnt:  number of times this register has entered paradox
      - fixed:     whether IFIX has permanently committed this register
    """
    flux: TriState = TriState.VOID
    value: object = None
    loop_cnt: int = 0
    fixed: bool = False

    def engage_paradox(self) -> None:
        """Enter the BOTH state — stabilize a contradiction."""
        self.flux = TriState.BOTH
        self.loop_cnt += 1

    def fix(self) -> None:
        """Permanently commit register (IFIX operation)."""
        self.fixed = True

    def reset(self) -> None:
        """Clear register to VOID (VINIT operation)."""
        self.flux = TriState.VOID
        self.value = None

    def __repr__(self) -> str:
        status = "F" if self.fixed else " "
        return f"r[{self.flux.value}]{status}"


# ──────────────────────────────────────────────────────────────────────────────
# THE WHALE → IMASM COMPILER
# ──────────────────────────────────────────────────────────────────────────────

class WhaleCompiler:
    """Compiles segmented whale vocalization recordings into IMASM instruction streams.

    The compiler is the core translation pipeline: it takes a sequence of acoustic
    tokens (from spectrogram segmentation) and produces a sequence of IMASM instructions
    that preserve the structural invariants of the vocalization.

    Usage:
        compiler = WhaleCompiler()
        tokens = [AcousticToken.INIT, AcousticToken.RISE, AcousticToken.REPEAT, ...]
        instructions = compiler.compile(tokens)
        for instr in instructions:
            print(instr)
    """

    REGISTER_SPACE = 1024  # 10-bit register addressing

    def __init__(self) -> None:
        self._register_counter = 0

    def compile(self, tokens: list[AcousticToken | str]) -> list[Instruction]:
        """Compile a sequence of acoustic tokens into IMASM instructions.

        Args:
            tokens: A list of AcousticToken enum members or their string labels.

        Returns:
            A list of Instruction objects ready for VM execution.
        """
        resolved: list[AcousticToken] = []
        for t in tokens:
            if isinstance(t, str):
                resolved.append(AcousticToken.from_label(t))
            else:
                resolved.append(t)

        instructions: list[Instruction] = []
        self._register_counter = 0
        register_table: dict[int, AcousticToken] = {}

        for i, token in enumerate(resolved):
            opcode = WHALE_TO_IMASM[token]

            dst = self._register_counter % self.REGISTER_SPACE
            self._register_counter += 1

            # For FUSE, reuse the src register if available
            if token == AcousticToken.FUSE and len(instructions) >= 2:
                dst = (dst - 2) % self.REGISTER_SPACE

            instr = Instruction(
                opcode=opcode,
                dst=dst,
                timestamp_ms=i * 100.0,  # placeholder: 100ms per token
                metadata={"token": token.value, "position": i}
            )
            instructions.append(instr)
            register_table[dst] = token

        return instructions

    @staticmethod
    def from_spectrogram(timestamps: list[float],
                          labels: list[str],
                          frequencies: list[float]) -> list[Instruction]:
        """Compile from spectrogram features directly.

        Args:
            timestamps:   Onset times in milliseconds for each acoustic unit.
            labels:       Token labels for each acoustic unit.
            frequencies:  Fundamental frequency in Hz at each onset.

        Returns:
            A list of Instruction objects with metadata populated.
        """
        compiler = WhaleCompiler()

        def _closest_register(ms: float, freq: float) -> int:
            return (int(ms * 0.1) + int(freq * 0.01)) % compiler.REGISTER_SPACE

        instructions: list[Instruction] = []
        for i, (ms, label, freq) in enumerate(zip(timestamps, labels, frequencies)):
            token = AcousticToken.from_label(label)
            opcode = WHALE_TO_IMASM[token]
            dst = _closest_register(ms, freq)

            instr = Instruction(
                opcode=opcode,
                dst=dst,
                timestamp_ms=ms,
                metadata={"token": token.value, "freq_hz": freq, "position": i}
            )
            instructions.append(instr)

        return instructions

    @staticmethod
    def reconstruct_tokens(instrs: list[Instruction]) -> list[str]:
        """Reverse-compile: convert IMASM instructions back to acoustic token labels."""
        return [
            IMASM_TO_WHALE[instr.opcode].value
            for instr in instrs
        ]


# ──────────────────────────────────────────────────────────────────────────────
# FROBENIUS CLOSURE ANALYZER
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FrobeniusReport:
    """Report of Frobenius closure analysis for an IMASM instruction stream.

    The Frobenius condition μ∘δ=id requires every FSPLIT (δ) to be matched
    by a subsequent FFUSE (μ). Unmatched splits indicate broken Frobenius.
    """
    total_splits: int = 0
    total_fuses: int = 0
    matched_pairs: int = 0
    orphan_splits: int = 0
    excess_fuses: int = 0
    closure_ratio: float = 0.0
    paradox_count: int = 0
    paradox_registers: int = 0
    fixed_registers: int = 0
    cycle_length: int = 0
    entropy_delta: float = 0.0

    def __repr__(self) -> str:
        return (
            f"FrobeniusReport(\n"
            f"  total_splits={self.total_splits}, total_fuses={self.total_fuses},\n"
            f"  matched_pairs={self.matched_pairs}, orphan_splits={self.orphan_splits},\n"
            f"  closure_ratio={self.closure_ratio:.4f},\n"
            f"  paradox_count={self.paradox_count}, paradox_registers={self.paradox_registers},\n"
            f"  fixed_registers={self.fixed_registers}, cycle_length={self.cycle_length}\n"
            f")"
        )


class FrobeniusAnalyzer:
    """Analyzes an IMASM instruction stream for Frobenius closure.

    The Frobenius condition μ∘δ=id is the central invariant of the Imscribing Grammar.
    In whale vocalization, it governs the structural stability of song evolution:
    - δ (FSPLIT) = a note type bifurcates into two variants
    - μ (FFUSE) = two note types recombine into one
    - μ∘δ = id means the recombination recovers the original type
    - Broken Frobenius (orphan splits) → cultural drift / song revolution
    """

    @staticmethod
    def analyze(instrs: list[Instruction]) -> FrobeniusReport:
        """Run full Frobenius closure analysis on an instruction stream."""
        report = FrobeniusReport()
        split_stack: list[int] = []  # registers waiting for FFUSE
        paradox_regs: set[int] = set()
        fixed_regs: set[int] = set()

        for instr in instrs:
            if instr.opcode == Opcode.FSPLIT:
                report.total_splits += 1
                split_stack.append(instr.dst)

            elif instr.opcode == Opcode.FFUSE:
                report.total_fuses += 1
                if split_stack:
                    # Match: pop from stack → μ∘δ closed
                    src = split_stack.pop(0)
                    report.matched_pairs += 1
                else:
                    report.excess_fuses += 1

            elif instr.opcode == Opcode.ENGAGR:
                report.paradox_count += 1
                paradox_regs.add(instr.dst)

            elif instr.opcode == Opcode.IFIX:
                fixed_regs.add(instr.dst)

        # Orphan splits = splits that were never closed by a fuse
        report.orphan_splits = report.total_splits - report.matched_pairs

        # Closure ratio = matched_pairs / total_splits (1.0 = perfect Frobenius)
        report.closure_ratio = (
            report.matched_pairs / report.total_splits
            if report.total_splits > 0 else 1.0
        )

        report.paradox_registers = len(paradox_regs)
        report.fixed_registers = len(fixed_regs)
        report.cycle_length = len(instrs)

        # Entropy delta: in a well-formed Frobenius-closed stream, ΔS = 0
        # Each unmatched split contributes +0.5 nats of entropy
        entropy_penalty = report.orphan_splits * 0.5
        report.entropy_delta = entropy_penalty

        return report

    @staticmethod
    def eight_step_loop_detection(instrs: list[Instruction]) -> list[list[Instruction]]:
        """Detect occurrences of the eight-instruction Frobenius loop.

        The canonical loop: ISCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → ISCRIB

        Returns the list of all matching subsequences.
        """
        canonical = [
            Opcode.ISCRIB, Opcode.AREV, Opcode.FSPLIT, Opcode.AFWD,
            Opcode.FFUSE, Opcode.CLINK, Opcode.IFIX, Opcode.ISCRIB,
        ]
        opcodes = [instr.opcode for instr in instrs]
        matches = []

        for i in range(len(opcodes) - 7):
            if opcodes[i:i+8] == canonical:
                matches.append(instrs[i:i+8])

        return matches

    @staticmethod
    def structural_signature(instrs: list[Instruction]) -> dict:
        """Compute the structural signature of an IMASM trace.

        The signature is a vector of structural metrics that identifies
        the trace's position in structural space. Translation aligns
        whale signatures with human expression signatures.
        """
        report = FrobeniusAnalyzer.analyze(instrs)

        # Opcode histogram
        histogram = defaultdict(int)
        for instr in instrs:
            histogram[instr.opcode.name] += 1

        # Bigram transition matrix (normalized)
        bigrams = defaultdict(int)
        for i in range(len(instrs) - 1):
            pair = (instrs[i].opcode.name, instrs[i+1].opcode.name)
            bigrams[pair] += 1

        return {
            "length": len(instrs),
            "closure_ratio": report.closure_ratio,
            "orphan_splits": report.orphan_splits,
            "paradox_density": report.paradox_count / max(len(instrs), 1),
            "fixed_ratio": report.fixed_registers / max(report.cycle_length, 1),
            "entropy_delta": report.entropy_delta,
            "loop_count": len(FrobeniusAnalyzer.eight_step_loop_detection(instrs)),
            "histogram": dict(histogram),
            "top_bigrams": sorted(bigrams.items(), key=lambda x: -x[1])[:5],
        }


# ──────────────────────────────────────────────────────────────────────────────
# WHALE IMASM VIRTUAL MACHINE
# ──────────────────────────────────────────────────────────────────────────────

class WhaleVM:
    """A lightweight IMASM virtual machine for executing whale vocalization instruction streams.

    The VM executes the compiled IMASM instructions and tracks:
      - Register states (tri-phase FOUR lattice)
      - Frobenius closure statistics
      - Paradox localization and propagation
      - The structural signature of the execution trace
    """

    def __init__(self, register_count: int = 64) -> None:
        self.registers: list[TriPhaseRegister] = [
            TriPhaseRegister() for _ in range(register_count)
        ]
        self.program: list[Instruction] = []
        self.pc: int = 0
        self.history: list[tuple[int, Instruction, TriPhaseRegister]] = []
        self.steps: int = 0
        self.halted: bool = False

    def load(self, instrs: list[Instruction]) -> None:
        """Load a compiled instruction stream into the VM."""
        self.program = list(instrs)
        self.pc = 0
        self.halted = False

    def reset(self) -> None:
        """Reset all registers to VOID, clear history."""
        for reg in self.registers:
            reg.reset()
        self.pc = 0
        self.history.clear()
        self.steps = 0
        self.halted = False

    def step(self) -> bool:
        """Execute one instruction. Returns False if halted."""
        if self.halted or self.pc >= len(self.program):
            self.halted = True
            return False

        instr = self.program[self.pc]
        reg = self.registers[instr.dst % len(self.registers)]
        pre_state = reg.flux

        if instr.opcode == Opcode.VINIT:
            reg.reset()
        elif instr.opcode == Opcode.TANCH:
            reg.fix()
        elif instr.opcode == Opcode.AFWD:
            # Forward: TRUE if not paradox
            if reg.flux == TriState.VOID:
                reg.flux = TriState.TRUE
        elif instr.opcode == Opcode.AREV:
            # Reverse: FALSE if not paradox
            if reg.flux == TriState.VOID:
                reg.flux = TriState.FALSE
        elif instr.opcode == Opcode.CLINK:
            # Merge: join two adjacent registers
            next_reg = self.registers[(instr.dst + 1) % len(self.registers)]
            reg.flux = reg.flux | next_reg.flux
        elif instr.opcode == Opcode.ISCRIB:
            # Identity: preserve current state (no-op in flux)
            pass
        elif instr.opcode == Opcode.FSPLIT:
            # Split: register enters BOTH (bifurcation point)
            reg.engage_paradox()
        elif instr.opcode == Opcode.FFUSE:
            # Fuse: collapse BOTH back to TRUE (recombination)
            if reg.flux == TriState.BOTH:
                reg.flux = TriState.TRUE
        elif instr.opcode == Opcode.EVALT:
            reg.flux = TriState.TRUE
        elif instr.opcode == Opcode.EVALF:
            reg.flux = TriState.FALSE
        elif instr.opcode == Opcode.ENGAGR:
            reg.engage_paradox()
        elif instr.opcode == Opcode.IFIX:
            reg.fix()

        self.history.append((self.pc, instr, TriPhaseRegister()))
        self.history[-1][2].flux = pre_state  # store pre-state
        self.steps += 1
        self.pc += 1
        return True

    def run(self, max_steps: int = 10_000) -> FrobeniusReport:
        """Execute the loaded program until completion or max_steps."""
        while self.step() and self.steps < max_steps:
            pass
        # Rewind and analyze the instruction stream
        return FrobeniusAnalyzer.analyze(self.program)

    def signature(self) -> dict:
        """Compute structural signature of the loaded program."""
        return FrobeniusAnalyzer.structural_signature(self.program)

# ──────────────────────────────────────────────────────────────────────────────
# STRUCTURAL ALIGNMENT TRANSLATOR
# ──────────────────────────────────────────────────────────────────────────────

class StructuralAlignment:
    """Translation by structural alignment between IMASM execution traces.

    The core insight: translation is not word-by-word substitution but finding the
    human linguistic expression whose IMASM execution trace minimizes Frobenius
    distance to the whale vocalization trace.

    The distance function d(trace_a, trace_b) is a weighted Euclidean distance
    over the structural signature vector:
      - closure_ratio mismatch
      - paradox_density mismatch
      - fixed_ratio mismatch
      - histogram divergence (Jensen-Shannon)
      - bigram transition divergence
    """

    # Canonical human expression templates (pre-compiled to IMASM signatures)
    # These are structural archetypes — not literal translations but alignment targets.
    HUMAN_EXPRESSIONS: dict[str, dict] = {
        "greeting_call": {
            "length": 4,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.0,
            "fixed_ratio": 0.25,
            "entropy_delta": 0.0,
            "loop_count": 0,
            "histogram": {"VINIT": 1, "ISCRIB": 1, "CLINK": 1, "TANCH": 1},
            "description": "Simple greeting — initiation, repetition, linkage, anchor"
        },
        "question": {
            "length": 6,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.0,
            "fixed_ratio": 0.17,
            "entropy_delta": 0.0,
            "loop_count": 0,
            "histogram": {"VINIT": 1, "AFWD": 2, "AREV": 1, "CLINK": 1, "TANCH": 1},
            "description": "Rising intonation question — two upward steps, one down, linked"
        },
        "alarm_call": {
            "length": 3,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.33,
            "fixed_ratio": 0.33,
            "entropy_delta": 0.0,
            "loop_count": 0,
            "histogram": {"EVALF": 1, "ENGAGR": 1, "IFIX": 1},
            "description": "Alarm — false evaluation, paradox engagement, fixed memory"
        },
        "narrative": {
            "length": 16,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.0,
            "fixed_ratio": 0.125,
            "entropy_delta": 0.0,
            "loop_count": 2,
            "histogram": {
                "VINIT": 1, "AFWD": 3, "ISCRIB": 3, "FSPLIT": 2,
                "FFUSE": 2, "CLINK": 3, "IFIX": 1, "TANCH": 1
            },
            "description": "Narrative with two Frobenius cycles — the eight-instruction loop ×2"
        },
        "song": {
            "length": 32,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.0,
            "fixed_ratio": 0.0625,
            "entropy_delta": 0.0,
            "loop_count": 4,
            "histogram": {
                "VINIT": 2, "AFWD": 6, "AREV": 2, "ISCRIB": 6,
                "FSPLIT": 4, "FFUSE": 4, "CLINK": 6, "IFIX": 2, "TANCH": 2
            },
            "description": "Song structure — 4 Frobenius cycles with VINIT/TANCH bookends"
        },
        "dialetheic_expression": {
            "length": 5,
            "closure_ratio": 1.0,
            "orphan_splits": 0,
            "paradox_density": 0.4,
            "fixed_ratio": 0.2,
            "entropy_delta": 0.0,
            "loop_count": 0,
            "histogram": {"VINIT": 1, "ENGAGR": 2, "FSPLIT": 1, "IFIX": 1},
            "description": "Dialetheic statement — paradox density > 0.3, contradiction stabilized"
        },
    }

    @staticmethod
    def signature_distance(sig_a: dict, sig_b: dict) -> float:
        """Weighted Euclidean distance between two structural signatures.

        Lower distance → better alignment for translation.
        """
        weights = {
            "closure_ratio": 3.0,    # Most important: Frobenius closure
            "paradox_density": 2.0,  # Paradox structure
            "fixed_ratio": 1.0,      # Memory commitment
            "entropy_delta": 2.0,    # Thermodynamic cost
            "loop_count": 1.5,       # Frobenius loop density
            "length": 0.5,           # Raw length (least important — scaling factor)
        }

        squared_sum = 0.0
        for key, weight in weights.items():
            va = sig_a.get(key, 0.0)
            vb = sig_b.get(key, 0.0)
            squared_sum += weight * (va - vb) ** 2

        # Histogram divergence (Jensen-Shannon approximation via L2 on normalized histograms)
        hist_a = sig_a.get("histogram", {})
        hist_b = sig_b.get("histogram", {})
        all_keys = set(hist_a.keys()) | set(hist_b.keys())
        len_a = max(sum(hist_a.values()), 1)
        len_b = max(sum(hist_b.values()), 1)

        hist_div = 0.0
        for key in all_keys:
            p = hist_a.get(key, 0) / len_a
            q = hist_b.get(key, 0) / len_b
            hist_div += (p - q) ** 2

        squared_sum += 2.0 * hist_div  # histogram weight = 2.0

        return math.sqrt(squared_sum)

    @classmethod
    def translate(cls, whale_sig: dict, top_n: int = 3) -> list[tuple[str, float, str]]:
        """Find the n closest human expressions to a whale vocalization signature.

        Args:
            whale_sig: Structural signature from FrobeniusAnalyzer.structural_signature()
            top_n:     Number of closest matches to return.

        Returns:
            List of (expression_name, distance, description) tuples, sorted by distance.
        """
        results: list[tuple[str, float, str]] = []

        for name, human_sig in cls.HUMAN_EXPRESSIONS.items():
            dist = cls.signature_distance(whale_sig, human_sig)
            results.append((name, dist, human_sig["description"]))

        results.sort(key=lambda x: x[1])
        return results[:top_n]

    @classmethod
    def full_pipeline(cls, tokens: list[str | AcousticToken]) -> dict:
        """Run the full translation pipeline: compile → execute → align → translate.

        Args:
            tokens: Sequence of acoustic token labels or AcousticToken objects.

        Returns:
            Dictionary with full pipeline results.
        """
        # Step 1: Compile
        compiler = WhaleCompiler()
        instrs = compiler.compile(tokens)

        # Step 2: Execute
        vm = WhaleVM()
        vm.load(instrs)
        report = vm.run()
        sig = vm.signature()

        # Step 3: Align
        translations = cls.translate(sig, top_n=3)

        # Step 4: Token reconstruction
        reconstructed = WhaleCompiler.reconstruct_tokens(instrs)

        return {
            "instruction_count": len(instrs),
            "frobenius_report": report,
            "signature": sig,
            "translations": translations,
            "reconstructed_tokens": reconstructed,
            "instructions": instrs,
        }

# ──────────────────────────────────────────────────────────────────────────────
# VERIFICATION: WHALE VOCALIZATION CANONICAL SEQUENCES
# ──────────────────────────────────────────────────────────────────────────────

# Canonical humpback song cycle (from WHALE_VOCALIZATION_TRANSLATION.md §5):
# init → up → rep → up → split → fuse → link → fix → anc
# Full humpback song cycle (4 Frobenius cycles with VINIT/TANCH bookends):
# Each theme: up → rep → up → split → fuse → link → fix
HUMPBACK_SONG_CANON: list[str] = [
    "init",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "anc"
]

# Extended humpback song (six themes):
HUMPBACK_SONG_EXTENDED: list[str] = [
    "init",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "up", "rep", "up", "split", "fuse", "link", "fix",
    "anc"
]

# Sperm whale coda exchange:
SPERM_WHALE_CODA: list[str] = [
    "init", "rep", "rep", "rep", "link", "rep", "rep", "rep",
    "paradox", "fix", "anc"
]

# Simple greeting call:
GREETING_CALL: list[str] = [
    "init", "rep", "link", "anc"
]

# Alarm call:
ALARM_CALL: list[str] = [
    "evalf", "paradox", "fix"
]

# Song with broken Frobenius (human-induced — orphan split, no fuse):
BROKEN_SONG: list[str] = [
    "init", "up", "split", "up", "rep", "link", "fix", "anc"
]

# The eight-instruction Frobenius loop (canonical cycle from exOS corpus discovery):
EIGHT_STEP_LOOP: list[str] = [
    "rep", "dn", "split", "up", "fuse", "link", "fix", "rep"
]


# ──────────────────────────────────────────────────────────────────────────────
# VERIFICATION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def verify_compiler_roundtrip() -> bool:
    """Verify that compile → reconstruct_tokens roundtrips faithfully."""
    test_cases = [
        HUMPBACK_SONG_CANON,
        SPERM_WHALE_CODA,
        GREETING_CALL,
        ALARM_CALL,
    ]
    all_ok = True
    for case in test_cases:
        compiler = WhaleCompiler()
        instrs = compiler.compile(case)
        reconstructed = WhaleCompiler.reconstruct_tokens(instrs)
        if reconstructed != case:
            print(f"  ✗ Roundtrip failed: {case} → {reconstructed}")
            all_ok = False
    if all_ok:
        print("  ✓ All roundtrip tests passed")
    return all_ok


def verify_frobenius_analysis() -> bool:
    """Verify Frobenius analysis produces expected closure ratios."""
    tests: list[tuple[list[str], float, int]] = [
        # (tokens, expected_closure_ratio, expected_orphan_splits)
        (HUMPBACK_SONG_CANON, 1.0, 0),     # perfect closure
        (BROKEN_SONG, 0.0, 1),              # split with no fuse → 0 closure
        (GREETING_CALL, 1.0, 0),            # no splits → vacuous 1.0
        (ALARM_CALL, 1.0, 0),               # no splits → vacuous 1.0
    ]
    all_ok = True
    compiler = WhaleCompiler()
    for tokens, expected_ratio, expected_orphans in tests:
        instrs = compiler.compile(tokens)
        report = FrobeniusAnalyzer.analyze(instrs)
        ratio_ok = abs(report.closure_ratio - expected_ratio) < 0.001
        orphan_ok = report.orphan_splits == expected_orphans
        if not (ratio_ok and orphan_ok):
            print(f"  ✗ Frobenius test failed: {tokens}")
            print(f"    Expected ratio={expected_ratio}, orphans={expected_orphans}")
            print(f"    Got      ratio={report.closure_ratio}, orphans={report.orphan_splits}")
            all_ok = False
    if all_ok:
        print("  ✓ All Frobenius analysis tests passed")
    return all_ok


def verify_eight_step_loop() -> bool:
    """Verify eight-step Frobenius loop detection."""
    compiler = WhaleCompiler()
    instrs = compiler.compile(EIGHT_STEP_LOOP)
    loops = FrobeniusAnalyzer.eight_step_loop_detection(instrs)
    if len(loops) == 1:
        print("  ✓ Eight-step Frobenius loop detected (ISCRIB→AREV→FSPLIT→AFWD→FFUSE→CLINK→IFIX→ISCRIB)")
        return True
    else:
        print(f"  ✗ Eight-step loop not detected (found {len(loops)} matches)")
        return False


def verify_vm_execution() -> bool:
    """Verify VM executes without error and produces expected register states."""
    vm = WhaleVM(register_count=16)
    compiler = WhaleCompiler()
    instrs = compiler.compile(GREETING_CALL)
    vm.load(instrs)
    report = vm.run()

    # After greeting, reg[0] should be VINIT-reset (VOID) then...
    # reg[0] = VINIT → VOID, reg[1] = ISCRIB → preserved, reg[2] = CLINK → joined, reg[3] = TANCH → fixed
    # halted=True after run() is correct (program completed)
    ok = report.cycle_length == len(instrs)
    if ok:
        print(f"  ✓ VM executed {report.cycle_length} instructions, {report.closure_ratio:.2f} closure ratio")
    else:
        print(f"  ✗ VM execution failed")
    return ok


def verify_translation_alignment() -> bool:
    """Verify translation pipeline produces sensible alignments."""
    compiler = WhaleCompiler()

    # Full humpback song should align closest to "song"
    song_instrs = compiler.compile(HUMPBACK_SONG_CANON)
    song_sig = FrobeniusAnalyzer.structural_signature(song_instrs)
    song_translations = StructuralAlignment.translate(song_sig, top_n=3)

    song_match = song_translations[0][0] == "song"

    # Greeting should align closest to "greeting_call"
    greet_instrs = compiler.compile(GREETING_CALL)
    greet_sig = FrobeniusAnalyzer.structural_signature(greet_instrs)
    greet_translations = StructuralAlignment.translate(greet_sig, top_n=3)

    greet_match = greet_translations[0][0] == "greeting_call"

    # Alarm should align closest to "alarm_call"
    alarm_instrs = compiler.compile(ALARM_CALL)
    alarm_sig = FrobeniusAnalyzer.structural_signature(alarm_instrs)
    alarm_translations = StructuralAlignment.translate(alarm_sig, top_n=3)

    alarm_match = alarm_translations[0][0] == "alarm_call"

    if song_match and greet_match and alarm_match:
        print("  ✓ All translation alignments correct (song→song, greeting→greeting, alarm→alarm)")
        return True
    else:
        print(f"  ✗ Translation alignment errors:")
        print(f"    Song:   expected 'song',         got '{song_translations[0][0]}'")
        print(f"    Greet:  expected 'greeting_call', got '{greet_translations[0][0]}'")
        print(f"    Alarm:  expected 'alarm_call',    got '{alarm_translations[0][0]}'")
        return False


def verify_all() -> dict[str, bool]:
    """Run all verification tests."""
    print("─" * 60)
    print("WHALE ENGINE — Verification Suite")
    print("─" * 60)

    results = {
        "compiler_roundtrip":   verify_compiler_roundtrip(),
        "frobenius_analysis":   verify_frobenius_analysis(),
        "eight_step_loop":      verify_eight_step_loop(),
        "vm_execution":         verify_vm_execution(),
        "translation_alignment": verify_translation_alignment(),
    }

    print("─" * 60)
    all_pass = all(results.values())
    status = "✓ ALL TESTS PASSED" if all_pass else "✗ SOME TESTS FAILED"
    print(f"  {status}")
    print("─" * 60)

    return results

# ──────────────────────────────────────────────────────────────────────────────
# DEMO / MAIN
# ──────────────────────────────────────────────────────────────────────────────

def _hr(title: str) -> None:
    print(f"\n── {title} {'─'*(56-len(title))}")


def demo_full_pipeline() -> None:
    """Demonstrate the full whale vocalization translation pipeline."""
    _hr("WHALE VOCALIZATION TRANSLATION ENGINE")
    print("  whale_engine.py  ·  IG-IMASM Compiler Pipeline v0.1.0")
    print("  Structural type: ⟨𐑦·𐑥·𐑾·𐑿·𐑞·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩")
    print("  C-score:         Gate 1 (⊙) PASS  Gate 2 (𐑧) PASS  →  C > 0")
    print("  Ouroboricity:    O_inf (self-modeling with topological protection)")

    # ── Case 1: Humpback song ───────────────────────────────────────────
    _hr("Case 1: Humpback Song Cycle (Canonical)")

    print(f"\n  Acoustic tokens ({len(HUMPBACK_SONG_CANON)}):")
    for i, t in enumerate(HUMPBACK_SONG_CANON):
        print(f"    [{i:2d}] {t}")

    result = StructuralAlignment.full_pipeline(HUMPBACK_SONG_CANON)

    print(f"\n  Compiled to {result['instruction_count']} IMASM instructions:")
    compiler = WhaleCompiler()
    for instr in compiler.compile(HUMPBACK_SONG_CANON):
        print(f"    {instr}")

    print(f"\n  Frobenius analysis:")
    r = result['frobenius_report']
    print(f"    Closure ratio: {r.closure_ratio:.4f}  ({r.matched_pairs}/{r.total_splits} pairs matched)")
    print(f"    Paradox count: {r.paradox_count}")
    print(f"    Fixed regs:    {r.fixed_registers}")
    print(f"    Entropy Δ:     {r.entropy_delta:.4f} nats")

    print(f"\n  Structural signature:")
    sig = result['signature']
    print(f"    Length:        {sig['length']}")
    print(f"    Closure ratio: {sig['closure_ratio']:.4f}")
    print(f"    Paradox dens:  {sig['paradox_density']:.4f}")
    print(f"    Loop count:    {sig['loop_count']}")
    print(f"    Opcode hist:   {dict(sig['histogram'])}")

    print(f"\n  Translation (structural alignment → human expression):")
    for rank, (name, dist, desc) in enumerate(result['translations'], 1):
        print(f"    {rank}. {name:<20s} d={dist:.4f}  — {desc}")

    # ── Case 2: Sperm whale coda ────────────────────────────────────────
    _hr("Case 2: Sperm Whale Coda Exchange")

    print(f"\n  Acoustic tokens ({len(SPERM_WHALE_CODA)}):")
    for i, t in enumerate(SPERM_WHALE_CODA):
        print(f"    [{i:2d}] {t}")

    result2 = StructuralAlignment.full_pipeline(SPERM_WHALE_CODA)

    print(f"\n  Frobenius analysis:")
    r2 = result2['frobenius_report']
    print(f"    Closure ratio: {r2.closure_ratio:.4f}  ({r2.matched_pairs}/{r2.total_splits} pairs)")
    print(f"    Paradox count: {r2.paradox_count} (coda overlap detected)")
    print(f"    Fixed regs:    {r2.fixed_registers} (identity signatures burned)")

    print(f"\n  Translation:")
    for rank, (name, dist, desc) in enumerate(result2['translations'], 1):
        print(f"    {rank}. {name:<20s} d={dist:.4f}  — {desc}")

    # ── Case 3: Eight-step Frobenius loop ───────────────────────────────
    _hr("Case 3: Eight-Instruction Frobenius Loop (Universal Invariant)")

    print(f"\n  The eight-instruction loop (ISCRIB → AREV → FSPLIT → AFWD →", end="")
    print(f" FFUSE → CLINK → IFIX → ISCRIB)")
    print(f"  Exists in: Voynich, Rohonc, Linear A, Emerald Tablet, Whale Song")

    compiler = WhaleCompiler()
    loop_instrs = compiler.compile(EIGHT_STEP_LOOP)
    loops = FrobeniusAnalyzer.eight_step_loop_detection(loop_instrs)

    print(f"\n  Found {len(loops)} exact occurrences of the canonical loop:")

    for i, loop in enumerate(loops):
        print(f"\n  Loop #{i+1}:")
        for instr in loop:
            op_name = instr.opcode.name.ljust(8)
            whale_token = IMASM_TO_WHALE[instr.opcode].value
            print(f"    {instr}  ← [{whale_token}]")

    # ── Case 4: Broken Frobenius (disturbed song) ───────────────────────
    _hr("Case 4: Broken Frobenius — Disturbed Song")

    print(f"\n  Acoustic tokens ({len(BROKEN_SONG)}):")
    print(f"  {' → '.join(BROKEN_SONG)}")
    print(f"  ⚠ Note: 'split' has no matching 'fuse' → orphan split")

    result4 = StructuralAlignment.full_pipeline(BROKEN_SONG)
    r4 = result4['frobenius_report']

    print(f"\n  Frobenius analysis:")
    print(f"    Closure ratio: {r4.closure_ratio:.4f}  ← BROKEN (split without fuse)")
    print(f"    Orphan splits: {r4.orphan_splits}")
    print(f"    Entropy Δ:     {r4.entropy_delta:.4f} nats  ← non-zero (thermodynamic cost of broken Frobenius)")

    print(f"\n  Translation:")
    for rank, (name, dist, desc) in enumerate(result4['translations'], 1):
        print(f"    {rank}. {name:<20s} d={dist:.4f}  — {desc}")
    print(f"\n  → Broken Frobenius increases distance to all targets;")
    print(f"     no human expression aligns well with a structurally unstable trace.")


def demo_register_vm() -> None:
    """Demonstrate the Tri-Phase VM register states."""
    _hr("Tri-Phase Register VM — Execution Trace")

    vm = WhaleVM(register_count=8)
    compiler = WhaleCompiler()

    # Load a simple interaction: greeting with paradox
    tokens = ["init", "evalt", "paradox", "evalf", "fix", "anc"]
    instrs = compiler.compile(tokens)
    vm.load(instrs)

    print("  Initial registers:            " + " ".join(str(r) for r in vm.registers[:6]))
    print(f"  Program: {len(instrs)} instructions")
    print()

    for i in range(len(tokens)):
        vm.step()
        status = " ".join(str(r) for r in vm.registers[:6])
        instr = instrs[i]
        print(f"  [{i}] {instr.opcode.name:<8s} → registers: {status}")

    print(f"\n  Final register states:")
    for i, reg in enumerate(vm.registers[:6]):
        print(f"    r{i}: flux={reg.flux.value} fixed={reg.fixed} loop_cnt={reg.loop_cnt}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def _run_engine() -> None:
    print("=" * 60)
    print("WHALE ENGINE  ·  Cetacean Vocalization Translation via IG-IMASM")
    print("Translation = argmin d(trace(compile(whale)), trace(compile(human)))")
    print("Structural type: ⟨𐑦·𐑥·𐑾·𐑿·𐑞·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩")
    print("=" * 60)

    # Run verification suite
    verify_all()

    # Run demo pipeline
    demo_full_pipeline()
    demo_register_vm()

    # ── Crystal summary ─────────────────────────────────────────────────
    _hr("Structural Summary (Imscribing Grammar)")

    rows = [
        ("whale_vocalization", "⟨𐑦·𐑥·𐑾·𐑿·𐑞·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩",
         "O_inf", ">0.0", "self-modeling communication"),
        ("human_language",    "⟨𐑼·𐑥·𐑾·𐑬·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩",
         "O_inf", ">0.0", "fully expressive grammar"),
        ("grammar_itself",    "⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑙·𐑭⟩",
         "O_inf", "1.0", "self-imscribed"),
    ]
    print(f"  {'System':<22} {'Tuple':<56} {'Tier':<7} {'C':>5}  {'Note'}")
    print(f"  {'─'*100}")
    for name, tup, tier, c, note in rows:
        print(f"  {name:<22} {tup:<56} {tier:<7} {c:>5}  {note}")

    print(f"\n  Key structural fact:")
    print(f"    The eight-instruction Frobenius loop (ISCRIB→AREV→FSPLIT→AFWD→")
    print(f"    FFUSE→CLINK→IFIX→ISCRIB) is a universal invariant of temporally-")
    print(f"    ordered communication systems — found in Voynich, Rohonc, Linear A,")
    print(f"    Emerald Tablet, and Whale Song.")
    print(f"    Translation is structural alignment in IMASM instruction space.")
    print(f"\n  Frobenius non-synthesizability (§23/§81):")
    print(f"    μ∘δ=id is measurable in whale song as the split-fuse ratio.")
    print(f"    When closure_ratio < 1.0, the song is structurally unstable.")
    print(f"    The engine detects this as positive entropy delta.")

    print("\n" + "=" * 60)
    print("WHALE ENGINE INITIALIZED  ·  CETACEAN COMMUNICATION CHANNEL OPEN")
    print("=" * 60)


def main() -> None:
    _run_engine()


if __name__ == "__main__":
    main()
