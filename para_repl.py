#!/usr/bin/env python3
"""
para_repl.py — REPL for the Paraconsistent Universal Engine

Interactive mode:
  Type ParaASM instructions directly — non-control-flow ops execute
  immediately and show changed registers.  Labels and control-flow
  ops are appended to the program buffer for :step / :run.

Commands (prefix :):
  :help                show this list
  :regs                dump all active registers
  :prog                show program buffer with PC marker
  :step [N]            execute N steps (default 1)
  :run  [N]            run fast N steps (default: until HALT or Ctrl+C)
  :load <file>         assemble and load a .asm file (resets PC, keeps registers)
  :reset               clear everything (registers + program)
  :save <file>         write current program buffer to file
  :snap                print snapshot (steps, cycles, paradox, Belnap dist)
  :q / :quit           exit
"""

import sys
import signal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from para_vm import ParaVM, B4, Instr, assemble, b4_join, _CTRL_FLOW

try:
    import readline  # noqa: F401
except ImportError:
    pass


# ── ANSI ───────────────────────────────────────────────────────────────────

R  = '\033[0m'
BD = '\033[1m'
DM = '\033[2m'
CY = '\033[96m'
GD = '\033[93m'
GN = '\033[92m'
BL = '\033[94m'
RD = '\033[91m'
GR = '\033[90m'

_B4_COLOR = {B4.N: GR, B4.T: GN, B4.F: BL, B4.B: RD}
_B4_BLOCK = {B4.N: '░', B4.T: '▒', B4.F: '▓', B4.B: '█'}


def _b4_color(b: B4) -> str:
    return f'{_B4_COLOR[b]}{b.value}{R}'


def _reg_line(rid: int, belief: B4, paradox: int, is_fixed: bool) -> str:
    c  = _B4_COLOR[belief]
    fx = f' {GR}[FIXED]{R}' if is_fixed else ''
    return f'  %r{rid:<3d} {c}{belief.value}{R}  paradox={paradox}{fx}'


def _dist_bar(dist: dict[B4, int], width: int = 32) -> str:
    total = sum(dist.values()) or 1
    parts = []
    for s in (B4.N, B4.T, B4.F, B4.B):
        n = dist[s]
        seg = max(1, round(n / total * width)) if n else 0
        if seg:
            parts.append(f'{_B4_COLOR[s]}{_B4_BLOCK[s] * seg}{R}')
    return '[' + ''.join(parts) + ']'


def _snap_line(vm: ParaVM) -> str:
    s = vm.snapshot()
    d = s['dist']
    dist_str = '  '.join(f'{_b4_color(v)}={d[v]}{R}' for v in B4)
    return (f'{GR}steps={s["steps"]}  pc={s["pc"]}  '
            f'paradox={s["paradox"]}  {dist_str}{R}')


# ── display helpers ────────────────────────────────────────────────────────

def show_regs(vm: ParaVM) -> None:
    rows = vm.active_regs()
    if not rows:
        print(f'  {GR}(no active registers){R}')
        return
    print(f'  {BD}{"reg":<6} {"bel":^5} {"paradox":>8} {"fixed":>6}{R}')
    print('  ' + '─' * 30)
    for rid, bel, paradox, is_fixed in rows:
        c  = _B4_COLOR[bel]
        fx = f'{GR}yes{R}' if is_fixed else 'no'
        print(f'  %r{rid:<4d} {c}{bel.value:^5}{R} {paradox:>8}  {fx:>6}')


def show_prog(vm: ParaVM) -> None:
    if not vm.program:
        print(f'  {GR}(program buffer empty){R}')
        return
    for i, instr in enumerate(vm.program):
        marker = f'{GD}▶{R}' if i == vm.pc else ' '
        label_here = [k for k, v in vm.label_map.items() if v == i]
        if label_here:
            for lbl in label_here:
                print(f'  {GR}{lbl}:{R}')
        print(f'  {marker} {i:3d}  {instr}')
    if vm.pc >= len(vm.program):
        print(f'  {GD}▶{R} {len(vm.program):3d}  (end of program)')


def show_snap(vm: ParaVM) -> None:
    s = vm.snapshot()
    d = s['dist']
    print(f'  steps    {s["steps"]:,}')
    print(f'  cycles   {s["cycles"]:,}')
    print(f'  pc       {s["pc"]} / {len(vm.program)}')
    print(f'  paradox  {s["paradox"]:,}')
    print(f'  active   {s["active"]}   fixed {s["fixed"]}')
    print(f'  halted   {s["halted"]}')
    print(f'  Belnap   {_dist_bar(d)}')
    print(f'           ' + '  '.join(f'{_b4_color(v)}={d[v]}{R}' for v in B4))


# ── command dispatch ───────────────────────────────────────────────────────

def do_command(cmd: str, vm: ParaVM) -> bool:
    """Handle a :command. Returns False to quit."""
    parts = cmd.split(None, 1)
    verb  = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ''

    if verb in (':q', ':quit'):
        return False

    elif verb == ':help':
        print(__doc__)

    elif verb == ':regs':
        show_regs(vm)

    elif verb == ':prog':
        show_prog(vm)

    elif verb == ':snap':
        show_snap(vm)

    elif verb == ':step':
        n = int(arg) if arg.isdigit() else 1
        changed = set(vm.belief.keys())
        for _ in range(n):
            if not vm.step():
                print(f'  {GR}HALTED{R}')
                break
        show_regs(vm)
        print(_snap_line(vm))

    elif verb == ':run':
        n = int(arg) if arg.isdigit() else None
        print(f'  {GR}running… Ctrl+C to pause{R}')
        try:
            vm.run(steps=n)
        except KeyboardInterrupt:
            pass
        show_regs(vm)
        print(_snap_line(vm))
        if vm.halted:
            print(f'  {GR}HALTED{R}')

    elif verb == ':load':
        if not arg:
            print(f'  {RD}usage: :load <file>{R}')
        else:
            path = Path(arg)
            if not path.exists():
                path = Path(__file__).parent / arg
            if not path.exists():
                print(f'  {RD}file not found: {arg}{R}')
            else:
                vm.load_file(path)
                print(f'  {GN}loaded {path} — {len(vm.program)} instructions, '
                      f'{len(vm.label_map)} labels{R}')
                show_prog(vm)

    elif verb == ':save':
        if not arg:
            print(f'  {RD}usage: :save <file>{R}')
        else:
            lines = []
            label_by_idx = {}
            for lbl, idx in vm.label_map.items():
                label_by_idx.setdefault(idx, []).append(lbl)
            for i, instr in enumerate(vm.program):
                for lbl in label_by_idx.get(i, []):
                    lines.append(f'{lbl}:')
                lines.append(f'    {instr.op}  {" ".join(instr.args)}'.rstrip())
            Path(arg).write_text('\n'.join(lines) + '\n')
            print(f'  {GN}saved {len(lines)} lines → {arg}{R}')

    elif verb == ':reset':
        vm.reset()
        print(f'  {GN}VM reset{R}')

    else:
        print(f'  {RD}unknown command: {verb}  (try :help){R}')

    return True


# ── interactive instruction entry ──────────────────────────────────────────

def do_instruction(line: str, vm: ParaVM) -> None:
    """
    Parse a line as ParaASM.  Non-control-flow ops execute immediately
    and print changed registers.  Labels and control-flow ops are appended
    to the program buffer only.
    """
    from para_vm import _LABEL_RE

    line = line.split(';', 1)[0].strip()
    if not line:
        return

    # label definition
    m = _LABEL_RE.match(line)
    if m:
        label = m.group(1)
        vm.add_label(label)
        rest = m.group(2).strip()
        print(f'  {GR}label {label} → instruction {vm.label_map[label]}{R}')
        if not rest:
            return
        line = rest

    parts = line.split()
    op    = parts[0].upper()
    args  = parts[1:]
    instr = Instr(op=op, args=args, source_line=line)

    if op in _CTRL_FLOW:
        vm.append_instr(instr)
        print(f'  {GR}appended to program buffer at {len(vm.program)-1}'
              f'  (use :step or :run to execute){R}')
        return

    # snapshot belief state before execution
    before = {rid: vm.belief_of(rid) for rid in vm.registers}
    before.update({rid: B4.N for rid in vm.belief if rid not in before})

    vm.append_instr(instr)
    vm.exec_one(instr)

    # show registers whose belief changed or are newly active
    changed = []
    all_ids = set(vm.registers.keys()) | set(vm.belief.keys())
    for rid in sorted(all_ids):
        new_b = vm.belief_of(rid)
        if new_b != before.get(rid, B4.N):
            r     = vm.registers[rid]
            c     = _B4_COLOR[new_b]
            fx    = f' {GR}[FIXED]{R}' if r.is_fixed else ''
            changed.append(f'%r{rid}={c}{new_b.value}{R}  π={r.paradox_count}{fx}')
    if changed:
        print('  ' + '   '.join(changed))


# ── main REPL ──────────────────────────────────────────────────────────────

BANNER = f"""
{BD}{CY}Para∥ REPL{R}  — Paraconsistent Universal Engine
{GR}type ParaASM instructions, or :help for commands, Ctrl-D / :q to quit{R}
"""

def repl(init_file: str | None = None) -> None:
    vm = ParaVM()
    print(BANNER)

    if init_file:
        try:
            vm.load_file(init_file)
            print(f'  {GN}loaded {init_file}{R}')
            show_prog(vm)
        except Exception as e:
            print(f'  {RD}load error: {e}{R}')

    while True:
        s = vm.snapshot()
        b_dist = s['dist']
        bar    = ''.join(f'{_B4_COLOR[v]}{b_dist[v]}{R}' for v in B4)
        prompt = f'{CY}(∥){R} '

        try:
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.startswith(':'):
            if not do_command(line, vm):
                break
        else:
            try:
                do_instruction(line, vm)
            except Exception as e:
                print(f'  {RD}error: {e}{R}')

    print(f'{GR}bye{R}')


if __name__ == '__main__':
    init = sys.argv[1] if len(sys.argv) > 1 else None
    repl(init)
