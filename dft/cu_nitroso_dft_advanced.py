#!/usr/bin/env python3
from pyscf import gto, dft
import numpy as np

print("=== Cu-Nitroso Radical C-N Coupling — Robust DFT ===\n")

mol = gto.M(
    atom = '''
Cu     0.000   0.000   0.000
N      2.050   0.000   0.000
N     -1.025   1.776   0.000
N     -1.025  -1.776   0.000
C      4.500   0.000   0.000
Br     5.900   0.000   0.000
N      3.000   2.500   0.000
O      3.000   3.800   0.000
    ''',
    basis = 'def2-SVP',      # Reliable basis that worked before
    charge = 0,
    spin = 0,
    verbose = 4
)

# Closed-shell resting state
print("=== Closed-shell Cu(I) Resting State ===")
mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.conv_tol = 1e-8
mf.conv_tol_grad = 1e-5
mf.max_cycle = 200
mf.level_shift = 0.3
mf.damp = 0.7
mf.diis_space = 15
mf.kernel()

if mf.converged:
    print("✅ Closed-shell converged")
    pop = mf.mulliken_pop()
    print(f"Cu Mulliken charge: {pop[1][0]:.4f}")
else:
    print("Closed-shell convergence incomplete.")

# Open-shell SET step
print("\n=== Open-shell SET Step (Cu(I) → Cu(II) + R•) ===")
mol_set = mol.copy()
mol_set.charge = 1
mol_set.spin = 1
mol_set.build()

mf_set = dft.UKS(mol_set)
mf_set.xc = 'B3LYP'
mf_set.conv_tol = 1e-7
mf_set.level_shift = 0.4
mf_set.damp = 0.8
mf_set.max_cycle = 200
mf_set.kernel()

if mf_set.converged:
    print("✅ SET step converged")
    spin_density = mf_set.spin_density()
    print("\nSpin Density on key atoms:")
    for i, (sym, _) in enumerate(mol_set.atom):
        print(f"  {sym:2} : {spin_density[0][i]:.4f}")
else:
    print("⚠️ SET step did not fully converge (common for Cu).")

print("\nDone. Checkpoints saved.")