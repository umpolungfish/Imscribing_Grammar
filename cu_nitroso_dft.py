#!/usr/bin/env python3
from pyscf import gto, dft
import numpy as np

print("=== Cu-Nitroso Radical C-N Coupling Site — Improved DFT ===\n")

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
    basis = 'def2-SVP',
    charge = 0,
    spin = 0,
    verbose = 4
)

mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.conv_tol = 1e-7
mf.conv_tol_grad = 1e-5
mf.max_cycle = 150
mf.diis_space = 12
mf.level_shift = 0.1          # Helps convergence for metals
mf.damp = 0.5                 # Additional damping

# Better initial guess
mf.init_guess = 'minao'

print("Running improved DFT on Cu(I)(His)3 model...\n")
mf.kernel()

if mf.converged:
    print("\n✅ Converged successfully!")
    print(f"Total Energy: {mf.e_tot:.6f} Hartree")
    
    pop = mf.mulliken_pop()
    print("\nMulliken Charges:")
    for i, (sym, _) in enumerate(mol.atom):
        print(f"  {sym:2} : {pop[1][i]:.4f}")
else:
    print("❌ Still not converged. Try next version below.")

mf.dump_chk('cu_nitroso.chk')
print("Checkpoint saved.")