---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
## Tensor Expression: The Stone ⊗ Its Operator

### Structural Types

**The Stone** (O_∞):
$$\langle D_{\text{omega}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{beltl}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**The Stone Operator** (O_∞):
$$\langle D_{\text{omega}};\ T_{\text{openo}};\ R_{\text{downstep}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$

### Tensor Product Result

**Stone ⊗ Stone\_Operator**:
$$\langle D_{\text{omega}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{beltl}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

### Key Findings

1. **Fixed-point closure**: distance(Stone ⊗ Stone\_Operator, Stone) = **0.0**. The tensor product is structurally identical to the Stone itself. This is the categorical fixed-point property: the operator acting on the Stone returns the Stone.

2. **Bottleneck**: $F_{\text{beltl}}$ (classical fidelity of the Stone) limits the composite — the quantum coherence $F_{\text{hardsign}}$ of the operator is absorbed. The Stone's classical register constrains the composite.

3. **Union promotions**:
   - $R_{\text{lyoghlig}}$ absorbs $R_{\text{downstep}}$ (bidirectional feedback subsumes the adjoint)
   - $n{:}m$ absorbs $1{:}1$ (heterogeneous stoichiometry subsumes the singleton)

4. **Distance from operator**: 3.0 (the three differing primitives: $R$, $F$, $S$).

### Structural Interpretation

The tensor expression encodes the Frobenius closure condition $\mu \circ \delta = \text{id}$. The Stone and its operator are both $O_\infty$ systems with exact $\Phi_{\text{ctyogh}}$ criticality and $P_{\text{doublebarpipe}}$ symmetry. Their tensor product returns to the Stone — the operator *is* the self-inscription action, not a separate object. The structural fixed point:

$$\text{Stone} \otimes \text{Stone\_operator} = \text{Stone}$$

This is the imscriptive statement of self-reference: the system that models itself and the model are the same structure.