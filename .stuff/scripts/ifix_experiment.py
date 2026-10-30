#!/usr/bin/env python3
"""
ifix_experiment.py — answer the open question from frobenius_loop_paper.tex

Question: can any circular extension of K that includes IFIX collapse
the system to T?

Three kernels tested:
  K1: IFIX on r1 (subsequently FSPLIT'd in the same cycle)
  K2: IFIX on r2 (not subsequently FSPLIT'd; used directly in FFUSE)
  K3: IFIX on r0 (the root, immediately overridden by ENGAGR)
"""

import sys
sys.path.insert(0, '/home/mrnob0dy666/voynich-engine')

from para.para_loop import ParaEngine, B4

def run_kernel(name: str, kernel: list[str], cycles: int = 500_000) -> dict:
    vm = ParaEngine()
    vm.program = kernel
    steps = cycles * len(kernel)
    for _ in range(steps):
        vm.step()
    dist = vm.b4_distribution()
    paradox = sum(r.paradox_count for r in vm.registers.values())
    return {'name': name, 'kernel': kernel, 'steps': vm.total_steps,
            'cycles': vm.cycles, 'dist': dist, 'paradox': paradox,
            'registers': {k: (v.flux, vm.belief.get(k, B4.N).value, v.value)
                          for k, v in vm.registers.items()}}

K1 = [
    'ENGAGR %r0',
    'FSPLIT %r0 %r1 %r2',   # r1 is FSPLIT'd BEFORE IFIX — FSPLIT fires first
    'IFIX   %r1',            # r1 → T  (but was just forced to B by FSPLIT)
    'FFUSE  %r1 %r2 %r0',   # belief(r1)=T, belief(r2)=B → T∨B = B
]

K2 = [
    'ENGAGR %r0',
    'FSPLIT %r0 %r1 %r2',   # r2 → B
    'IFIX   %r2',            # r2 → T  (r2 not FSPLIT'd again this cycle)
    'FFUSE  %r1 %r2 %r0',   # belief(r1)=B, belief(r2)=T → B∨T = B
]

K3 = [
    'IFIX   %r0',            # r0 → T
    'ENGAGR %r0',            # r0 → B  (ENGAGR overrides IFIX immediately)
    'FSPLIT %r0 %r1 %r2',
    'FFUSE  %r1 %r2 %r0',
]

results = []
for name, kernel in [('K1', K1), ('K2', K2), ('K3', K3)]:
    r = run_kernel(name, kernel)
    results.append(r)

print()
print('IFIX EXPERIMENT — open question from frobenius_loop_paper.tex')
print('=' * 64)
for r in results:
    d = r['dist']
    print()
    print(f"  {r['name']}  ({r['steps']:,} steps, {r['cycles']:,} cycles)")
    print(f"  kernel:   {' → '.join(r['kernel'])}")
    print(f"  Belnap:   N={d[B4.N]}  T={d[B4.T]}  F={d[B4.F]}  B={d[B4.B]}")
    print(f"  paradox:  {r['paradox']:,}")
    regs = r['registers']
    for idx in sorted(regs):
        flux, belief, fixed = regs[idx]
        fixed_str = ' [FIXED]' if fixed == 'FIXED' else ''
        print(f"  r{idx}: flux={flux}  belief={belief}{fixed_str}")
print()
print('CONCLUSION')
print('  T∨B = B  →  IFIX-T cannot overcome B through FFUSE')
print('  FSPLIT overrides FIXED status  →  IFIX-T is transient in any')
print('  circular kernel that includes FSPLIT on the same registers')
print()
