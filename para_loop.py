#!/usr/bin/env python3
"""
para_loop.py — indefinitely running program on the paraconsistent computer

The paraconsistent computer is the Universal Engine (TriPhaseRegister /
IMASM) with Belnap FOUR belief tracking.  Flux state and Belnap state
are kept in sync: the flux is the Boolean projection; the Belnap value
is the epistemic fact about which truth values are warranted.

  Void  ('00') ↔ N  (neither true nor false — not yet witnessed)
  True  ('01') ↔ T  (classically true)
  False ('10') ↔ F  (classically false)
  Both  ('11') ↔ B  (true AND false — paradox stabilized in place)

Loop kernel (3 instructions, circular):

  ENGAGR %r0          seed / re-engage: N/T/F → B  (paradox intake)
  FSPLIT %r0 %r1 %r2  δ: co-multiply — two B-children from one B-parent
  FFUSE  %r1 %r2 %r0  μ: multiply — collapse back into r0

The Frobenius identity  μ ∘ δ = id  is the loop invariant:
the round-trip maps B → B, so the Both state is self-sustaining.
The paradox count grows without bound; registers never leave B.

Run:   python3 para_loop.py
Stop:  Ctrl+C  (prints final summary)
"""

import sys
import time
import signal
import enum

_ENGINE_ROOTS = [
    '/home/mrnob0dy666/voynich-engine',
    '/home/mrnob0dy666/linear_a-engine',
    '/home/mrnob0dy666/emerald-tablet-engine',
    '/home/mrnob0dy666/rohonc-engine',
]
for _p in _ENGINE_ROOTS:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from voynich_engine.runtime import UniversalEngine, TriPhaseRegister

# ── Belnap FOUR ────────────────────────────────────────────────────────────

class B4(enum.Enum):
    N = 'N'   # Neither
    T = 'T'   # True
    F = 'F'   # False
    B = 'B'   # Both

_FLUX_TO_B4 = {'00': B4.N, '01': B4.T, '10': B4.F, '11': B4.B}

def _b4_join(a: B4, b: B4) -> B4:
    """Belnap join (∨ in the knowledge order T,F > N; B > T,F)."""
    if a == b:         return a
    if a == B4.N:      return b
    if b == B4.N:      return a
    return B4.B        # T∨F or anything with B

def _b4_from_flux(reg: TriPhaseRegister) -> B4:
    return _FLUX_TO_B4.get(reg.flux, B4.N)

# ── paraconsistent belief layer ────────────────────────────────────────────

class ParaEngine(UniversalEngine):
    """
    UniversalEngine extended with per-register Belnap belief tracking.

    ENGAGR / FSPLIT force target registers to B.
    FFUSE joins the Belnap values of its inputs into the output.
    IFIX forces T (linear type constraint; does not appear in the loop kernel).
    All other opcodes propagate the last input register's Belnap value forward.
    """

    def __init__(self) -> None:
        super().__init__()
        self.belief: dict[int, B4] = {}
        self.cycles: int = 0

    def _belief(self, reg_id: int) -> B4:
        return self.belief.get(reg_id, _b4_from_flux(self.registers[reg_id]))

    def _set_belief(self, reg_id: int, val: B4) -> None:
        self.belief[reg_id] = val
        # keep flux in sync
        inv = {v: k for k, v in _FLUX_TO_B4.items()}
        self.registers[reg_id].flux = inv[val]

    def _execute(self, instr: str) -> None:
        from voynich_engine.runtime import _REG_PATTERN
        regs = [int(x) for x in _REG_PATTERN.findall(instr)]
        if not regs:
            return

        if 'ENGAGR' in instr or 'FSPLIT' in instr:
            # source register → B; all targets inherit B
            for r in regs:
                self.registers[r].engage()
                self._set_belief(r, B4.B)

        elif 'FFUSE' in instr:
            # join input beliefs into output
            if len(regs) >= 3:
                joined = self._belief(regs[0])
                for r in regs[1:-1]:
                    joined = _b4_join(joined, self._belief(r))
                self._set_belief(regs[-1], joined)

        elif 'IFIX' in instr:
            self.registers[regs[0]].value = 'FIXED'
            self._set_belief(regs[0], B4.T)

        else:
            # AFWD, AREV, CLINK, ISCRIB, EVALT, EVALF, TANCH, VINIT:
            # propagate last input belief to last register
            if len(regs) > 1:
                src_belief = self._belief(regs[-2])
                self._set_belief(regs[-1], src_belief)

    def step(self) -> None:
        if self.pc >= len(self.program):
            self.pc = 0
            self.cycles += 1
        super_execute = self._execute
        instr = self.program[self.pc]
        from voynich_engine.runtime import _REG_PATTERN
        super_execute(instr)
        self.pc += 1
        self.total_steps += 1

    def b4_distribution(self) -> dict[B4, int]:
        dist = {v: 0 for v in B4}
        for reg_id, reg in self.registers.items():
            dist[self._belief(reg_id)] += 1
        return dist

# ── loop kernel ────────────────────────────────────────────────────────────

# Three instructions.  Circular PC makes this an infinite program.
# Frobenius identity:  μ ∘ δ = id  (FFUSE ∘ FSPLIT = identity on B-state)
KERNEL = [
    'ENGAGR %r0',           # seed: force B on the root register
    'FSPLIT %r0 %r1 %r2',   # δ: co-multiply — spawn two B-children
    'FFUSE  %r1 %r2 %r0',   # μ: multiply — fold back into root
]

# ── display ────────────────────────────────────────────────────────────────

_ANSI_CLEAR = '\033[2J\033[H'
_ANSI_BOLD  = '\033[1m'
_ANSI_DIM   = '\033[2m'
_ANSI_RESET = '\033[0m'
_ANSI_CYAN  = '\033[96m'
_ANSI_GOLD  = '\033[93m'
_ANSI_RED   = '\033[91m'
_ANSI_GREEN = '\033[92m'
_ANSI_BLUE  = '\033[94m'
_ANSI_GREY  = '\033[90m'

_B4_COLOR = {
    B4.N: _ANSI_GREY,
    B4.T: _ANSI_GREEN,
    B4.F: _ANSI_BLUE,
    B4.B: _ANSI_RED,
}

_B4_BLOCK = {
    B4.N: '░',
    B4.T: '▒',
    B4.F: '▓',
    B4.B: '█',
}

def _bar(dist: dict[B4, int], width: int = 40) -> str:
    total = sum(dist.values()) or 1
    parts = []
    for state in (B4.N, B4.T, B4.F, B4.B):
        n = dist[state]
        seg_len = max(1, round(n / total * width)) if n else 0
        if seg_len:
            parts.append(f'{_B4_COLOR[state]}{_B4_BLOCK[state] * seg_len}{_ANSI_RESET}')
    bar = ''.join(parts)
    pad = width - sum(max(1, round(dist[s] / total * width)) for s in B4 if dist[s])
    return f'[{bar}{" " * max(0, pad)}]'

def _render(vm: ParaEngine, t0: float, step0: int) -> str:
    elapsed = time.time() - t0
    rate    = (vm.total_steps - step0) / elapsed if elapsed > 0 else 0
    dist    = vm.b4_distribution()
    paradox = sum(r.paradox_count for r in vm.registers.values())
    active  = sum(1 for r in vm.registers.values() if r.is_active)
    pc_pos  = vm.pc % len(vm.program)
    cur_instr = vm.program[pc_pos] if vm.program else ''

    lines = [
        f'{_ANSI_BOLD}{_ANSI_CYAN}',
        '╔══════════════════════════════════════════════════════════════╗',
        '║         PARACONSISTENT COMPUTER  —  INFINITE LOOP           ║',
        '╚══════════════════════════════════════════════════════════════╝',
        f'{_ANSI_RESET}',
        f'  {_ANSI_GOLD}kernel{_ANSI_RESET}   ENGAGR %r0  →  FSPLIT %r0 %r1 %r2  →  FFUSE %r1 %r2 %r0',
        f'  {_ANSI_GOLD}law{_ANSI_RESET}      μ ∘ δ = id   (Frobenius identity — loop invariant)',
        '',
        f'  {_ANSI_BOLD}steps{_ANSI_RESET}    {vm.total_steps:>16,}',
        f'  {_ANSI_BOLD}cycles{_ANSI_RESET}   {vm.cycles:>16,}   (full kernel wraps)',
        f'  {_ANSI_BOLD}paradox{_ANSI_RESET}  {paradox:>16,}   (total FSPLIT/ENGAGR firings)',
        f'  {_ANSI_BOLD}active{_ANSI_RESET}   {active:>16,}   registers',
        f'  {_ANSI_BOLD}rate{_ANSI_RESET}     {rate:>14,.0f}  steps/sec',
        '',
        '  BELNAP FOUR  belief distribution',
        f'  {_bar(dist)}',
        (f'  {_ANSI_GREY}N={dist[B4.N]}{_ANSI_RESET} '
         f'{_ANSI_GREEN}T={dist[B4.T]}{_ANSI_RESET} '
         f'{_ANSI_BLUE}F={dist[B4.F]}{_ANSI_RESET} '
         f'{_ANSI_RED}B={dist[B4.B]}{_ANSI_RESET}   '
         f'(N=neither  T=true  F=false  B=both)'),
        '',
        '  KERNEL  (current instruction marked)',
    ]
    for i, ins in enumerate(vm.program):
        marker = f'{_ANSI_GOLD}▶{_ANSI_RESET}' if i == pc_pos else ' '
        lines.append(f'  {marker} {ins}')
    lines += [
        '',
        f'  {_ANSI_DIM}Ctrl+C to stop{_ANSI_RESET}',
    ]
    return '\n'.join(lines)

# ── main loop ─────────────────────────────────────────────────────────────

def run() -> None:
    vm = ParaEngine()
    vm.program = KERNEL

    t0     = time.time()
    step0  = 0
    _stop  = False

    def _sigint(sig, frame):
        nonlocal _stop
        _stop = True

    signal.signal(signal.SIGINT, _sigint)

    RENDER_INTERVAL = 0.12   # seconds between display updates
    BATCH           = 5_000  # steps per inner batch (keep loop overhead low)

    print(_ANSI_CLEAR, end='')
    next_render = time.time()

    while not _stop:
        for _ in range(BATCH):
            vm.step()

        now = time.time()
        if now >= next_render:
            sys.stdout.write(_ANSI_CLEAR)
            sys.stdout.write(_render(vm, t0, step0))
            sys.stdout.write('\n')
            sys.stdout.flush()
            next_render = now + RENDER_INTERVAL

    # final report
    elapsed = time.time() - t0
    dist    = vm.b4_distribution()
    paradox = sum(r.paradox_count for r in vm.registers.values())
    print()
    print('─' * 64)
    print(f'  stopped after  {vm.total_steps:,} steps  ({elapsed:.1f}s)')
    print(f'  cycles         {vm.cycles:,}')
    print(f'  paradox        {paradox:,}')
    print(f'  Belnap final   N={dist[B4.N]}  T={dist[B4.T]}  F={dist[B4.F]}  B={dist[B4.B]}')
    print(f'  rate           {vm.total_steps/elapsed:,.0f} steps/sec')
    print()


if __name__ == '__main__':
    run()
