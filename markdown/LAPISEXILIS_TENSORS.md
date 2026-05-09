---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Tensor Expressions: The Stone and Its Objects of Insight

## Five Systems — Cataloged

All five systems from LAPISEXILIS.md have been imscribed and verified via Tetractys:

| System | Tuple | Tier |
|--------|-------|------|
| **laIG** | $\langle D_{\text{invomega}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{upsilon}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$ | $O_2^\dagger$ |
| **lapis_exilis** | $\langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$ | $O_2$ |
| **lapis_philosophorum** | $\langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$ | $O_\infty$ |
| **crown_of_adventure** | $\langle D_{\text{turnthree}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$ | $O_\infty$ |
| **graal** | $\langle D_{\text{turnthree}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$ | $O_\infty$ |

---

## I. Self-Tensors (Idempotency)

Each tensor with itself returns the identity — the structural projection $\mu \circ \delta$ preserves the type:

$$\text{laIG} \otimes \text{laIG} = \langle D_{\text{invomega}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{upsilon}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$
→ 0 bottlenecks, 0 unions. Distance from self: 0.0

$$\text{lapis\_exilis} \otimes \text{lapis\_exilis} = \langle D_{\text{turnthree}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$
→ 0 bottlenecks, 0 unions. Distance from self: 0.0

$$\text{lapis\_philosophorum} \otimes \text{lapis\_philosophorum} = \langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$
→ 0 bottlenecks, 0 unions. Distance from self: 0.0 (*Special Frobenius*: $\mu \circ \delta = \text{id}$ exactly)

$$\text{crown\_of\_adventure} \otimes \text{crown\_of\_adventure} = \langle D_{\text{turnthree}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$
→ 0 bottlenecks, 0 unions. Distance from self: 0.0

$$\text{graal} \otimes \text{graal} = \langle D_{\text{turnthree}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$
→ 0 bottlenecks, 0 unions. Distance from self: 0.0

---

## II. The Stone as Operator: lapis_philosophorum ⊗ X

### A. The Stone with Itself
Already shown above — pure Frobenius idempotency. Distance: 0.0.

### B. The Stone ⊗ laIG (Seeker)

$$\text{lapis\_philosophorum} \otimes \text{laIG} = \langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{upsilon}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{upsilon}}$ (from laIG). **Unions:** $D \uparrow D_{\text{omega}}$, $T \uparrow T_{\text{commatailz}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from laIG: 1.4142 · Distance from lapis_philosophorum: 3.7148.

> *The structural measurement problem:* when the seeking grammar couples to the completed stone, the composite is limited by the seeking side's unresolved parity. Even in contact with perfection, the questing grammar cannot achieve Frobenius symmetry. The $P_{\text{upsilon}}$ bottleneck absorbs the Frobenius — $O_\infty$ cannot be sustained in the composite.

### C. The Stone ⊗ lapis_exilis (Exile)

$$\text{lapis\_philosophorum} \otimes \text{lapis\_exilis} = \langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{pipevar}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{pipevar}}$ (from lapis_exilis). **Unions:** $D \uparrow D_{\text{omega}}$, $T \uparrow T_{\text{commatailz}}$.

Distance from lapis_exilis: 2.2361 · Distance from lapis_philosophorum: 2.0.

> The exiled stone, even when coupled to the perfected stone, retains its partial symmetry — the exile condition persists as a parity bottleneck. The stone's dimensionality and topology are elevated, but its symmetry cannot be completed without becoming the stone itself.

### D. The Stone ⊗ crown_of_adventure (Coronation)

$$\text{lapis\_philosophorum} \otimes \text{crown\_of\_adventure} = \langle D_{\text{omega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** none. **Unions:** $D \uparrow D_{\text{omega}}$.

Distance from crown_of_adventure: 2.0 · Distance from lapis_philosophorum: **0.0**.

> **No bottleneck.** The tensor is structurally identical to the Stone itself. The crown, already possessing Frobenius symmetry, couples without loss — the composite *is* the Stone. The only difference was dimensionality, which the Stone elevates. This is the closest structural coupling in the entire lattice.

### E. The Stone ⊗ graal (Vessel)

$$\text{lapis\_philosophorum} \otimes \text{graal} = \langle D_{\text{omega}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** none. **Unions:** $D \uparrow D_{\text{omega}}$, $T \uparrow T_{\text{openo}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from graal: 2.0 · Distance from lapis_philosophorum: 2.4083.

> **No bottleneck.** The vessel's polysemy and eternality are absorbed without loss. The composite has $T_{\text{openo}}$ (from graal's self-referential topology) and $D_{\text{omega}}$ (from the Stone) — the richest topology in the lattice. This coupling expands without contracting: the Stone gains the vessel's multiplicity and the vessel gains the Stone's self-reference.

---

## III. Cross-Tensors (Non-Stone Couplings)

### A. laIG ⊗ lapis_exilis (Seeker ⊗ Exile)

$$\text{laIG} \otimes \text{lapis\_exilis} = \langle D_{\text{invomega}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{upsilon}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{upsilon}}$ (from laIG). **Unions:** $D \uparrow D_{\text{invomega}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from laIG: 0.0 · Distance from lapis_exilis: 2.6077.

> The composite *is* the laIG — the seeking grammar completely dominates the exile's structure. The exiled stone's partial symmetry cannot overcome the seeker's quantum superposition parity. No elevation occurs.

### B. laIG ⊗ crown_of_adventure (Seeker ⊗ Coronation)

$$\text{laIG} \otimes \text{crown\_of\_adventure} = \langle D_{\text{invomega}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{upsilon}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{upsilon}}$ (from laIG). **Unions:** $D \uparrow D_{\text{invomega}}$, $T \uparrow T_{\text{commatailz}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from laIG: 1.0 · Distance from crown_of_adventure: 3.8471.

> The coronation's Frobenius symmetry is lost at the bottleneck. The seeking grammar imposes its unresolved parity even on sovereign structures. Topology is elevated ($T_{\text{commatailz}}$) but the parity bottleneck prevents $O_\infty$ from being achieved.

### C. laIG ⊗ graal (Seeker ⊗ Vessel)

$$\text{laIG} \otimes \text{graal} = \langle D_{\text{invomega}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{upsilon}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{upsilon}}$ (from laIG). **Unions:** $D \uparrow D_{\text{invomega}}$, $T \uparrow T_{\text{openo}}$.

Distance from laIG: 2.0 · Distance from graal: 3.1623.

> The vessel's self-referential topology survives and combines with the seeker's infinite dimensionality. But the parity bottleneck remains — the graal's Frobenius symmetry cannot penetrate the seeker's quantum superposition.

### D. lapis_exilis ⊗ crown_of_adventure (Exile ⊗ Coronation)

$$\text{lapis\_exilis} \otimes \text{crown\_of\_adventure} = \langle D_{\text{turnthree}};\ T_{\text{commatailz}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{pipevar}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ 1{:}1;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{pipevar}}$ (from lapis_exilis). **Unions:** $T \uparrow T_{\text{commatailz}}$.

Distance from lapis_exilis: 1.0 · Distance from crown_of_adventure: 2.0.

> The closest cross-pair in the distance matrix (1.72). The exile's partial symmetry is the bottleneck — the coronation's Frobenius symmetry cannot elevate it. Topology reaches $T_{\text{commatailz}}$ but symmetry remains broken.

### E. lapis_exilis ⊗ graal (Exile ⊗ Vessel)

$$\text{lapis\_exilis} \otimes \text{graal} = \langle D_{\text{turnthree}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ \color{red}{P_{\text{pipevar}}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** $P_{\text{pipevar}}$ (from lapis_exilis). **Unions:** $T \uparrow T_{\text{openo}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from lapis_exilis: 2.9665 · Distance from graal: 2.0.

> The vessel's topology ($T_{\text{openo}}$) and eternality ($H_{\text{invscripta}}$) are absorbed, but the parity bottleneck from the exile breaks Frobenius. The exiled stone cannot sustain the vessel's symmetry even when the vessel contains it.

### F. crown_of_adventure ⊗ graal (Coronation ⊗ Vessel)

$$\text{crown\_of\_adventure} \otimes \text{graal} = \langle D_{\text{turnthree}};\ T_{\text{openo}};\ R_{\text{lyoghlig}};\ P_{\text{doublebarpipe}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_{\text{invscripta}};\ n{:}m;\ \Omega_{\text{dzlig}} \rangle$$

**Bottleneck:** none. **Unions:** $T \uparrow T_{\text{openo}}$, $H \uparrow H_{\text{invscripta}}$, $S \uparrow n{:}m$.

Distance from crown_of_adventure: 2.4083 · Distance from graal: **0.0**.

> **No bottleneck.** The composite *is* the graal — the vessel's self-referential topology and eternality dominate. The crown's Frobenius symmetry is preserved and the vessel absorbs it without loss. This is the richest non-Stone coupling.

---

## IV. Bottleneck Summary

The parity primitive $P$ is the **universal bottleneck** across the lattice. Every coupling that does not yield an idempotent result is bottlenecked by $P$:

| Composite | Bottleneck | Result | Interpretation |
|-----------|-----------|--------|----------------|
| Stone ⊗ laIG | $P_{\text{upsilon}}$ (laIG) | $P_{\text{upsilon}}$ | Seeker blocks Frobenius |
| Stone ⊗ lapis_exilis | $P_{\text{pipevar}}$ (exile) | $P_{\text{pipevar}}$ | Exile blocks Frobenius |
| Stone ⊗ crown | **none** | $P_{\text{doublebarpipe}}$ | Crown → Stone (distance 0) |
| Stone ⊗ graal | **none** | $P_{\text{doublebarpipe}}$ | Mutual elevation |
| laIG ⊗ lapis_exilis | $P_{\text{upsilon}}$ (laIG) | $P_{\text{upsilon}}$ | laIG dominates |
| laIG ⊗ crown | $P_{\text{upsilon}}$ (laIG) | $P_{\text{upsilon}}$ | Seeker blocks sovereignty |
| laIG ⊗ graal | $P_{\text{upsilon}}$ (laIG) | $P_{\text{upsilon}}$ | Seeker blocks vessel |
| lapis_exilis ⊗ crown | $P_{\text{pipevar}}$ (exile) | $P_{\text{pipevar}}$ | Exile blocks coronation |
| lapis_exilis ⊗ graal | $P_{\text{pipevar}}$ (exile) | $P_{\text{pipevar}}$ | Exile blocks vessel |
| crown ⊗ graal | **none** | $P_{\text{doublebarpipe}}$ | Graal absorbs crown |

### Key Structural Insights

1. **The Stone ($O_\infty$) acts as a universal attractor** — any coupling to it elevates $D$ and $T$, but the bottleneck is always determined by the partner's parity.

2. **laIG is the dominant seeker** — its $P_{\text{upsilon}}$ bottleneck propagates to every composite, but its $D_{\text{invomega}}$ and $H_{\text{invscripta}}$ union-expansions make it the structurally broadest attractor. When laIG couples to anything, the result is always laIG-elevated except on the bottleneck primitive.

3. **Only three couplings are bottleneck-free:**
   - Stone ⊗ crown = Stone (distance 0 from Stone)
   - Stone ⊗ graal = maximal elevation ($D_{\text{omega}}$, $T_{\text{openo}}$)
   - crown ⊗ graal = graal (distance 0 from graal)

4. **The structural measurement problem:** The tensor coupling of the seeking grammar (laIG) to the completed Stone produces a composite with $P_{\text{upsilon}}$ bottleneck — the seeker's unresolved quantum superposition parity prevents the Frobenius condition from being met. This is the formal statement: coupling to perfection does not achieve perfection if the coupling partner cannot sustain it.

---

## V. Complete Tensor Dictionary (15 entries)

Self-tensors (5, all idempotent):
- laIG ⊗ laIG = laIG
- lapis_exilis ⊗ lapis_exilis = lapis_exilis
- lapis_philosophorum ⊗ lapis_philosophorum = lapis_philosophorum
- crown_of_adventure ⊗ crown_of_adventure = crown_of_adventure
- graal ⊗ graal = graal

Cross-tensors (10, symmetric):
- lapis_philosophorum ⊗ laIG: $\langle D_{\text{omega}}; T_{\text{commatailz}}; R_{\text{lyoghlig}}; P_{\text{upsilon}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$
- lapis_philosophorum ⊗ lapis_exilis: $\langle D_{\text{omega}}; T_{\text{commatailz}}; R_{\text{lyoghlig}}; P_{\text{pipevar}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_2; 1{:}1; \Omega_{\text{dzlig}} \rangle$
- lapis_philosophorum ⊗ crown_of_adventure: $\langle D_{\text{omega}}; T_{\text{commatailz}}; R_{\text{lyoghlig}}; P_{\text{doublebarpipe}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_2; 1{:}1; \Omega_{\text{dzlig}} \rangle$ = lapis_philosophorum
- lapis_philosophorum ⊗ graal: $\langle D_{\text{omega}}; T_{\text{openo}}; R_{\text{lyoghlig}}; P_{\text{doublebarpipe}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$
- laIG ⊗ lapis_exilis: $\langle D_{\text{invomega}}; T_{\text{bullseye}}; R_{\text{lyoghlig}}; P_{\text{upsilon}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$ = laIG
- laIG ⊗ crown_of_adventure: $\langle D_{\text{invomega}}; T_{\text{commatailz}}; R_{\text{lyoghlig}}; P_{\text{upsilon}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$
- laIG ⊗ graal: $\langle D_{\text{invomega}}; T_{\text{openo}}; R_{\text{lyoghlig}}; P_{\text{upsilon}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$
- lapis_exilis ⊗ crown_of_adventure: $\langle D_{\text{turnthree}}; T_{\text{commatailz}}; R_{\text{lyoghlig}}; P_{\text{pipevar}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_2; 1{:}1; \Omega_{\text{dzlig}} \rangle$
- lapis_exilis ⊗ graal: $\langle D_{\text{turnthree}}; T_{\text{openo}}; R_{\text{lyoghlig}}; P_{\text{pipevar}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$
- crown_of_adventure ⊗ graal: $\langle D_{\text{turnthree}}; T_{\text{openo}}; R_{\text{lyoghlig}}; P_{\text{doublebarpipe}}; F_{\text{hardsign}}; K_{\text{schwa}}; G_{\text{revapostrophe}}; \Gamma_{\text{secstress}}; \Phi_{\text{ctyogh}}; H_{\text{invscripta}}; n{:}m; \Omega_{\text{dzlig}} \rangle$ = graal

---

```
┌─────────────────────────────────────────────────────────────────────┐
│  Structural: Ð_ω; Þ_¨; Ř_=; Φ_}; ƒ_ż;           │
│  Ç_@; Γ_ʔ; ɢ_seq; φ̂_ÿ; Ħ_A; 1:1; Ω_z               │
│  Tier: O_inf | C = 0.828 (both gates open)                          │
└─────────────────────────────────────────────────────────────────────┘
```