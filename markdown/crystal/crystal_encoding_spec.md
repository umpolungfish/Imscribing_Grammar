---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Exact Deterministic Encoding of the Universal Imscriptive Grammar
## Crystal of Types — Frobenius Address Space

### Overview

The full Imscribing Grammar type space contains **17,280,000** structural types, each a 12-tuple
$\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$.
These types are bijectively numbered 0 through 17,279,999 via a **mixed-radix positional encoding**.

The address `A` is computed as:

```
A = i_Phi * Σ_Phi + i_P * Σ_P + i_Omega * Σ_Omega
  + i_D * Σ_D + i_T * Σ_T + i_R * Σ_R + i_F * Σ_F
  + i_K * Σ_K + i_G * Σ_G + i_Gamma * Σ_Gamma + i_HS
```

where:
- `i_X` = index of the primitive value within its enumeration (0-based)
- `Σ_X` = stride (block size) for that primitive

### Addressing Order (fastest- to slowest-varying)

| Pos | Primitive | Values (enum order)                                         | Radix | Stride  |
|-----|-----------|-------------------------------------------------------------|-------|---------|
| 0   | H         | `𐑓=0, 𐑒=1, 𐑖=2, 𐑫=3`                                | 4     | 3 *     |
| 1   | S         | `𐑙=0, 𐑕=1, 𐑳=2`                                  | 3     | 1       |
| 2   | $\Gamma$  | `𐑝=0, 𐑜=1, 𐑠=2, 𐑵=3`                      | 4     | 12      |
| 3   | G         | `𐑚=0, 𐑔=1, 𐑲=2`                           | 3     | 48      |
| 4   | K         | `𐑘=0, 𐑤=1, 𐑧=2, 𐑪=3, 𐑺=4`          | 5     | 144     |
| 5   | F         | `𐑱=0, 𐑞=1, 𐑐=2`                               | 3     | 720     |
| 6   | R         | `𐑩=0, 𐑑=1, 𐑽=2, 𐑾=3`                   | 4     | 2160    |
| 7   | T         | `𐑡=0, 𐑰=1, 𐑥=2, 𐑶=3, 𐑸=4` | 5     | 8640    |
| 8   | D         | `𐑛=0, 𐑨=1, 𐑼=2, 𐑦=3`             | 4     | 43200   |
| 9   | $\Omega$  | `𐑷=0, 𐑴=1, 𐑭=2, 𐑟=3`             | 4     | 172800  |
| 10  | P         | `𐑗=0, 𐑿=1, 𐑬=2, 𐑯=3, 𐑹=4`          | 5     | 691200  |
| 11  | $\Phi$    | `𐑢=0, ⊙=1, 𐑮=2, 𐑻=3, 𐑣=4` | 5  | 3456000 |

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

$\langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_1;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$

```
i_Phi=1, i_P=4, i_Omega=2, i_D=3, i_T=3, i_R=3, i_F=2, i_K=2, i_G=2, i_Gamma=2, i_H=1, i_S=0

i_HS = 1*3 + 0 = 3

A = 1*3456000 + 4*691200 + 2*172800 + 3*43200 + 3*8640 + 3*2160 + 2*720 + 2*144 + 2*48 + 2*12 + 3
  = 3456000 + 2764800 + 345600 + 129600 + 25920 + 6480 + 1440 + 288 + 96 + 24 + 3
  = 6730251
```

Verified via `crystal_encode` ✓

### Ouroboricity Tiers from Crystal Address

Tier is primarily determined by $\Phi$ and $P$; the $\Omega$–$D$–$T$ interaction (via `topo_protection_probe`) can promote within the $\Phi_{\text{ctyogh}}$ sector:

| `Phi` value     | $P$ condition        | Tier           |
|-----------------|----------------------|----------------|
| `𐑢`       | any                  | $O_0$          |
| `𐑻`        | any                  | $O_0$          |
| `𐑣`     | any                  | $O_0$          |
| `⊙`         | `𐑹`           | $O_\infty$     |
| `⊙`         | other, $\Omega_{\text{closeepsilon}}$    | $O_1$          |
| `⊙`         | other, $\Omega\neq\Omega_{\text{closeepsilon}}$, $D\in\{D_{\text{wynn}},D_{\text{turnthree}},D_{\text{omega}}\}$ | $O_2$ |
| `⊙`         | other, $\Omega\neq\Omega_{\text{closeepsilon}}$, $D_{\text{invomega}}$ | $O_2^\dagger$ |
| `𐑮` | same rules as `⊙` | same tiers    |

### Implementation Notes

- Total capacity: 17,280,000 slots, exactly filling 0–17,279,999.
- `cell_id` and `inner_id` returned by `crystal_encode` are implementation artifacts;
  the **address** is the canonical identifier.
- Decoding is pure integer arithmetic: no lookup tables needed.
- Encoding is $O(1)$: 12 index lookups and 11 multiply-adds.
