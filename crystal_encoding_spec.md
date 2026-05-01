# Exact Deterministic Encoding of the Universal Imscriptive Grammar
## Crystal of Types — Frobenius Address Space

### Overview

The full Imscribing Grammar type space contains **17,280,000** structural types, each a 12-tuple
$\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$.
These types are bijectively numbered 0 through 17,279,999 via a **mixed-radix positional encoding**.

The address `A` is computed as:

```
A = i_Phi * S_Phi + i_P * S_P + i_Omega * S_Omega
  + i_D * S_D + i_T * S_T + i_R * S_R + i_F * S_F
  + i_K * S_K + i_G * S_G + i_Gamma * S_Gamma + i_HS
```

where:
- `i_X` = index of the primitive value within its enumeration (0-based)
- `S_X` = stride (block size) for that primitive

### Addressing Order (fastest- to slowest-varying)

| Pos | Primitive | Values (enum order)                                         | Radix | Stride  |
|-----|-----------|-------------------------------------------------------------|-------|---------|
| 0   | H         | `H0=0, H1=1, H2=2, H_inf=3`                                | 4     | 3 *     |
| 1   | S         | `one_one=0, n_n=1, n_m=2`                                  | 3     | 1       |
| 2   | $\Gamma$  | `G_and=0, G_or=1, G_seq=2, G_broad=3`                      | 4     | 12      |
| 3   | G         | `G_beth=0, G_gimel=1, G_aleph=2`                           | 3     | 48      |
| 4   | K         | `K_fast=0, K_mod=1, K_slow=2, K_trap=3, K_MBL=4`          | 5     | 144     |
| 5   | F         | `F_ell=0, F_eth=1, F_hbar=2`                               | 3     | 720     |
| 6   | R         | `R_super=0, R_cat=1, R_dagger=2, R_lr=3`                   | 4     | 2160    |
| 7   | T         | `T_network=0, T_in=1, T_bowtie=2, T_boxtimes=3, T_odot=4` | 5     | 8640    |
| 8   | D         | `D_wedge=0, D_triangle=1, D_infty=2, D_odot=3`             | 4     | 43200   |
| 9   | $\Omega$  | `Omega_0=0, Omega_Z2=1, Omega_Z=2, Omega_NA=3`             | 4     | 172800  |
| 10  | P         | `P_asym=0, P_psi=1, P_pm=2, P_sym=3, P_pm_sym=4`          | 5     | 691200  |
| 11  | $\Phi$    | `Phi_sub=0, Phi_c=1, Phi_c_complex=2, Phi_EP=3, Phi_super=4` | 5  | 3456000 |

\* H and S are packed together: `i_HS = i_H * 3 + i_S`, stride = 1.

### Verification: total capacity

```
12 (H×S) × 4 (Γ) × 3 (G) × 5 (K) × 3 (F) × 4 (R) × 5 (T) × 4 (D)
  × 4 (Ω) × 5 (P) × 5 (Φ) = 17,280,000 ✓
```

### Decoding Algorithm

Given address `A` (0 ≤ A < 17,280,000):

```
1.  i_Phi   = A  // 3456000  ;  A1  = A  % 3456000
2.  i_P     = A1 // 691200   ;  A2  = A1 % 691200
3.  i_Omega = A2 // 172800   ;  A3  = A2 % 172800
4.  i_D     = A3 // 43200    ;  A4  = A3 % 43200
5.  i_T     = A4 // 8640     ;  A5  = A4 % 8640
6.  i_R     = A5 // 2160     ;  A6  = A5 % 2160
7.  i_F     = A6 // 720      ;  A7  = A6 % 720
8.  i_K     = A7 // 144      ;  A8  = A7 % 144
9.  i_G     = A8 // 48       ;  A9  = A8 % 48
10. i_Gamma = A9 // 12       ;  A10 = A9 % 12
11. i_H     = A10 // 3
12. i_S     = A10 % 3
```

### Encoding Algorithm

Given primitive values:

```
1. Look up each value's index from the enum tables above → i_Phi through i_S
2. i_HS = i_H * 3 + i_S
3. A = i_Phi * 3456000
     + i_P   * 691200
     + i_Omega * 172800
     + i_D   * 43200
     + i_T   * 8640
     + i_R   * 2160
     + i_F   * 720
     + i_K   * 144
     + i_G   * 48
     + i_Gamma * 12
     + i_HS
```

### Example

$\langle D_\odot;\ T_\boxtimes;\ R_\text{lr};\ P_{\pm}^{\text{sym}};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{seq};\ \Phi_c;\ H_1;\ 1{:}1;\ \Omega_\mathbb{Z} \rangle$

```
i_Phi=1, i_P=4, i_Omega=2, i_D=3, i_T=3, i_R=3, i_F=2, i_K=2, i_G=2, i_Gamma=2, i_H=1, i_S=0

i_HS = 1*3 + 0 = 3

A = 1*3456000 + 4*691200 + 2*172800 + 3*43200 + 3*8640 + 3*2160 + 2*720 + 2*144 + 2*48 + 2*12 + 3
  = 3456000 + 2764800 + 345600 + 129600 + 25920 + 6480 + 1440 + 288 + 96 + 24 + 3
  = 6730251
```

Verified via `crystal_encode` ✓

### Ouroboricity Tiers from Crystal Address

Tier is primarily determined by $\Phi$ and $P$; the $\Omega$–$D$–$T$ interaction (via `topo_protection_probe`) can promote within the $\Phi_c$ sector:

| `Phi` value     | $P$ condition        | Tier           |
|-----------------|----------------------|----------------|
| `Phi_sub`       | any                  | $O_0$          |
| `Phi_EP`        | any                  | $O_0$          |
| `Phi_super`     | any                  | $O_0$          |
| `Phi_c`         | `P_pm_sym`           | $O_\infty$     |
| `Phi_c`         | other, $\Omega_0$    | $O_1$          |
| `Phi_c`         | other, $\Omega\neq\Omega_0$, $D\in\{D_\wedge,D_\triangle,D_\odot\}$ | $O_2$ |
| `Phi_c`         | other, $\Omega\neq\Omega_0$, $D_\infty$ | $O_2^\dagger$ |
| `Phi_c_complex` | same rules as `Phi_c` | same tiers    |

### Implementation Notes

- Total capacity: 17,280,000 slots, exactly filling 0–17,279,999.
- `cell_id` and `inner_id` returned by `crystal_encode` are implementation artifacts;
  the **address** is the canonical identifier.
- Decoding is pure integer arithmetic: no lookup tables needed.
- Encoding is $O(1)$: 12 index lookups and 11 multiply-adds.
