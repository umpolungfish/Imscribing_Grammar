---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Imscribing Grammar Encoding Guide

**How to assign a 12-primitive tuple to any system**

*v1.1 — 2026-04-09*

---

## What encoding is

Every system — physical, mathematical, biological, computational, cultural — occupies a point in a 12-dimensional space of structural types. The Imscribing Grammar grammar provides coordinates for that space. Encoding is the act of finding those coordinates for a given system.

The result is a **imscrbgrmr tuple**:

$$\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$$

Once a system is encoded, you can compute distances to any other encoded system, determine its ouroboricity tier, apply lattice operations (meet, join, tensor), and find its nearest-known analogs in the catalog of 1,200+ encoded systems.

Encoding is not classification by category. It is structural measurement. The same physical phenomenon can appear in multiple domains; the grammar finds the underlying type regardless of domain label.

A key fact about the grammar's architecture (§68.4, updated v0.5.1): the 12 primitives are partitioned into three families by value count — $\mathcal{F}_3 = \{F, G, S\}$ (3 primitives with 3 values each), $\mathcal{F}_4 = \{D, R, \Gamma, H, \Omega\}$ (5 primitives with 4 values each), $\mathcal{F}_5 = \{T, P, \Phi, K\}$ (4 primitives with 5 values each). The total state space is $3^3 \times 4^5 \times 5^4 = 17{,}280{,}000$ types. The exponent of each base is the count of primitives in that family — not a free parameter, but a direct readout of the grammar's own structure. $\mathcal{F}_5$ now contains exactly the four gate primitives: $T$ (topology gate for the fertile manifold), $P$ (Frobenius gate for $O_\infty$), $\Phi$ (criticality gate), and $K$ (kinetic gate for $C > 0$). The partition was derived by the grammar itself: $\Omega_{\text{turna}}$ was shown independent of $T$ (catalog test), so $\Omega$ needed a 4th value and migrated to $\mathcal{F}_4$; $K_{\text{lambda}}$ was shown independent of all other 11 primitives, so $K$ needed a 5th value and migrated to $\mathcal{F}_5$. The $\mathcal{F}_4$ family is invariant under this extension: $\Omega$ entered from $\mathcal{F}_3$, $K$ left to $\mathcal{F}_5$, net zero.

---

## The twelve primitives

| Symbol | Name | Values (low → high) | Question it answers |
|--------|------|---------------------|---------------------|
| $D$ | Dimensionality | $D_{\text{wynn}}$ · $D_{\text{turnthree}}$ · $D_{\text{invomega}}$ · $D_{\text{omega}}$ | How does the system's state space scale? |
| $T$ | Topology | $T_{\text{nrleg}}$ · $T_{\text{invscr}}$ · $T_\text{bowtie}$ · $T_\text{box}$ · $T_{\text{openo}}$ | What is the shape of the state-to-state map? |
| $R$ | Relational mode | $R_{\text{subrightarrow}}$ · $R_{\text{ctz}}$ · $R_{\text{downstep}}$ · $R_{\text{lyoghlig}}$ | What kind of morphism does the system admit? |
| $P$ | Parity/symmetry | $P_{\text{aolig}}$ · $P_{\text{upsilon}}$ · $P_{\text{pipevar}}$ · $P_{\text{subdoublearrow}}$ · $P_{\text{doublebarpipe}}$ | Is the system's self-dual map exact? |
| $F$ | Fidelity | $F_{\text{beltl}}$ · $F_{\text{dh}}$ · $F_{\text{hardsign}}$ | How much information survives composition? |
| $K$ | Kinetic character | $K_{\text{frtailgamma}}$ · $K_{\text{turnm}}$ · $K_{\text{schwa}}$ · $K_{\text{teshlig}}$ | How does the system move through its state space? |
| $G$ | Granularity | $G_{\text{beta}}$ · $G_{\text{gamma}}$ · $G_{\text{revapostrophe}}$ | At what scale does the system operate? |
| $\Gamma$ | Interaction grammar | $\Gamma_{\text{corner}}$ · $\Gamma_{\text{spleftarrow}}$ · $\Gamma_{\text{secstress}}$ · $\Gamma_{\text{doublevertline}}$ | How do the system's operations compose? |
| $\Phi$ | Criticality | $\Phi_{\text{softsign}}$ · $\Phi_{\text{ctyogh}}$ · $\Phi_{\text{closerevepsilon}}$ · $\Phi_{\text{revepsilon}}$ · $\Phi_{\text{upstep}}$ | Does the system's state space admit a self-modeling loop? |
| $H$ | Chirality/temporal depth | $H_0$ · $H_1$ · $H_2$ · $H_{\text{invscripta}}$ | Does the system have temporal memory or chiral asymmetry? |
| $S$ | Stoichiometry | $1{:}1$ · $n{:}n$ · $n{:}m$ | What is the input-output balance? |
| $\Omega$ | Winding | $\Omega_{\text{closeepsilon}}$ · $\Omega_{\text{crtwo}}$ · $\Omega_{\text{dzlig}}$ · $\Omega_{\text{turna}}$ | What is the system's topological winding class? |

---

## The encoding protocol

### Step 1 — Identify the system's criticality ($\Phi$)

$\Phi$ is the single most important primitive. It determines the ouroboricity tier ceiling.

- **$\Phi_{\text{softsign}}$**: the system operates well away from any phase transition or critical point. It is stable, ordered, and does not exhibit scale-free fluctuations. *Examples: classical mechanics, Boolean logic, crystalline solids far from melting.*
- **$\Phi_{\text{ctyogh}}$**: the system is at or near a second-order phase transition, a fixed point of renormalization, or a self-similar critical manifold. Scale-free fluctuations. The system can model itself. *Examples: Ising model at $Þ_c$, conformal field theories, the Imscribing Grammar grammar itself.*
- **$\Phi_{\text{closerevepsilon}}$**: criticality with complex-valued parameters — non-Hermitian systems, systems with complex fixed points. Same tier behavior as $\Phi_{\text{ctyogh}}$ but the inner crystal differs. *Examples: non-Hermitian quantum mechanics, PT-symmetric systems, logarithmic CFT.*
- **$\Phi_{\text{revepsilon}}$**: exceptional point — a point where two eigenvalues and their eigenvectors coalesce. The system is at the boundary of $\Phi_{\text{ctyogh}}$ but the self-modeling loop is degenerate. *Examples: gain-loss balanced waveguides, resonance coalescence.*
- **$\Phi_{\text{upstep}}$**: disordered phase above the critical point. High entropy, no long-range order, no self-referential loop. *Examples: paramagnets above $Þ_c$, turbulent fluids.*

**Key rule**: $\Phi_{\text{ctyogh}}$ is required for any tier above $O_0$. If you assign $\Phi_{\text{softsign}}$ or $\Phi_{\text{upstep}}$, the system is $O_0$ regardless of all other primitives.

---

### Step 2 — Assign symmetry ($P$)

$P$ is a **bottleneck primitive**: under tensor coupling, the weaker partner wins ($\min$). Assign it conservatively.

- **$P_{\text{aolig}}$**: no symmetry. The system's forward and backward maps are completely different. *Examples: directed networks, one-way gates.*
- **$P_{\text{upsilon}}$**: phase symmetry only — a $U(1)$ or similar global phase. *Examples: charged particles, spinors.*
- **$P_{\text{pipevar}}$**: $\mathbb{Z}_2$ symmetry — the system has a parity or time-reversal symmetry. *Examples: most physical Hamiltonians, Boolean systems.*
- **$P_{\text{subdoublearrow}}$**: full symmetry — the encoding and decoding maps are related but not exactly inverse. *Examples: reversible computation, symplectic systems.*
- **$P_{\text{doublebarpipe}}$**: **Frobenius condition** — $\mu \circ \delta = \text{id}$ holds exactly. The system is a special Frobenius algebra: encoding and decoding are mutually inverse. **Assign only when this is provably exact, not approximately true.** *Examples: proven mathematical theorems, alchemy, the Imscribing Grammar grammar.*

**Warning**: $P_{\text{doublebarpipe}}$ cannot be obtained by composing systems with $P < P_{\text{doublebarpipe}}$ (§23: Frobenius non-synthesizability). Do not assign it to a composite system unless the composite itself satisfies the Frobenius condition directly.

---

### Step 3 — Assign winding ($\Omega$)

$\Omega$ determines whether critical behavior is topologically protected against perturbation.

- **$\Omega_{\text{closeepsilon}}$**: no winding. Critical behavior is fine-tuned and fragile — it disappears under generic perturbation. *Examples: mean-field critical points, classical phase transitions.*
- **$\Omega_{\text{crtwo}}$**: $\mathbb{Z}_2$-protected. The critical behavior is protected by a $\mathbb{Z}_2$ topological invariant — it persists under perturbations that respect the $\mathbb{Z}_2$ symmetry. *Examples: topological insulators (class AII), Kitaev chain in $\mathbb{Z}_2$ phase.*
- **$\Omega_{\text{dzlig}}$**: $\mathbb{Z}$-protected. Protected by an integer-valued topological invariant. *Examples: IQHE, winding-number-protected edge modes, Kitaev chain at topological transition.*
- **$\Omega_{\text{turna}}$**: non-Abelian anyonic protection. Braiding of anyons generates a non-commutative matrix on the ground-state degeneracy — not just a phase. This is strictly stronger than $\Omega_{\text{dzlig}}$: not only is the ground state protected, but operations on it are inherently quantum with no classical description. **Assign only to systems with provably non-Abelian anyon statistics.** *Examples: FQH Moore-Read ($\nu = 5/2$), non-Abelian spin liquids.* Note: $\Omega_{\text{turna}}$ is independent of $T$ — $T_\text{box}$ (braided topology) can coexist with any $\Omega$ value.

**Rule**: $\Omega \neq \Omega_{\text{closeepsilon}}$ combined with $\Phi_{\text{ctyogh}}$ is required to reach $O_2$ or higher.

---

### Step 4 — Assign dimensionality ($D$)

$D$ reflects how the system's state space scales with system size — not the spatial dimension of the embedding space, but the structural complexity of the algebra's state manifold.

- **$D_{\text{wynn}}$** (local): the algebra operates on a finite or bounded state space. No thermodynamic limit. *Examples: finite groups, local cellular automata, single-particle quantum mechanics.*
- **$D_{\text{turnthree}}$** (mesoscopic): the algebra spans a growing but sub-extensive state space. Intermediate between local and infinite. *Examples: spin chains of finite length, mesoscopic quantum dots.*
- **$D_{\text{invomega}}$** (unbounded): the algebra operates in an infinite-dimensional Hilbert space or a state space with no natural finite truncation. *Examples: QFT, von Neumann algebras, infinite spin chains.*
- **$D_{\text{omega}}$** (imscriptive): the boundary of the state space encodes the bulk. The system admits a boundary-bulk duality. *Examples: AdS/CFT, holographic error-correcting codes, the Imscribing Grammar grammar itself.*

**Rule**: $D_{\text{invomega}}$ combined with $\Phi_{\text{ctyogh}}$ and $\Omega \neq \Omega_{\text{closeepsilon}}$ gives $O_2^\dagger$ (unbounded protected criticality). $D_{\text{omega}}$ is treated as bounded ($D \neq D_{\text{invomega}}$) for tier purposes, giving $O_2$.

---

### Step 5 — Assign the remaining eight primitives

These eight primitives do not affect the ouroboricity tier. They locate the system within its tier cell.

**Fidelity ($F$)** — bottleneck primitive, assign conservatively:
- $F_{\text{beltl}}$ (classical): information loss is unconstrained. Classical channel.
- $F_{\text{dh}}$ (quantum): information is preserved at the quantum level — unitary dynamics.
- $F_{\text{hardsign}}$ (quantum-coherent): information is preserved with full quantum coherence, no decoherence.

**Kinetic character ($K$)**:
- $K_{\text{frtailgamma}}$: dynamics dominate over structure. The system equilibrates rapidly.
- $K_{\text{turnm}}$: balanced dynamics. The system can explore its state space at moderate rate.
- $K_{\text{schwa}}$: structure dominates. The system changes slowly; metastability is common.
- $K_{\text{teshlig}}$: frozen by order — a coherent many-body gap arrests dynamics (gapped ground state, topological phase). **Assign to gap-protected terminal states.** A system with $K_{\text{teshlig}}$ has $C = 0$.
- $K_{\text{lambda}}$: frozen by disorder — many-body localization arrests dynamics across all eigenstates, not just the ground state. Distinct from $K_{\text{teshlig}}$: the mechanism is disorder, not order; area-law entanglement persists in excited states; eigenstate thermalization fails entirely. **Assign only to provably MBL phases.** A system with $K_{\text{lambda}}$ has $C = 0$.

**Topology ($T$)**:
- $T_{\text{nrleg}}$: arbitrary graph structure, many-to-many.
- $T_{\text{invscr}}$: injective map — the system embeds into a larger space.
- $T_\text{bowtie}$: hourglass — two domains connected through a bottleneck.
- $T_\text{box}$: product structure — the state space is a direct product.
- $T_{\text{openo}}$: imscriptive — boundary encodes bulk (use with $D_{\text{omega}}$).

**Relational mode ($R$)**:
- $R_{\text{subrightarrow}}$: one-way classification, no inverse.
- $R_{\text{ctz}}$: categorical — morphisms compose but need not be invertible.
- $R_{\text{downstep}}$: dagger category — every morphism has an adjoint.
- $R_{\text{lyoghlig}}$: left-right symmetric — fully ambidextrous composition.

**Granularity ($G$)**:
- $G_{\text{beta}}$: microscopic — the system operates at the finest available scale.
- $G_{\text{gamma}}$: mesoscopic — intermediate scale.
- $G_{\text{revapostrophe}}$: macroscopic/universal — the system operates at the scale of the whole, or claims to describe all scales.

**Interaction grammar ($\Gamma$)**:
- $\Gamma_{\text{corner}}$: parallel — all operations fire simultaneously.
- $\Gamma_{\text{spleftarrow}}$: alternative — one operation fires at a time, chosen by some gate.
- $\Gamma_{\text{secstress}}$: sequential — operations fire in fixed order.
- $\Gamma_{\text{doublevertline}}$: broadcast — one operation distributes over many targets (softmax, renormalization group, language).

**Chirality/temporal depth ($H$)**:
- $H_0$: time-symmetric, no chiral asymmetry, no temporal memory.
- $H_1$: one level of temporal depth — the system has a memory of one past state.
- $H_2$: two levels — the system tracks its own rate of change.
- $H_{\text{invscripta}}$: infinite temporal depth — the system integrates over its entire history.

**Stoichiometry ($S$)**:
- $1{:}1$: one input, one output. Simple transduction.
- $n{:}n$: many inputs, many outputs, balanced.
- $n{:}m$: many inputs, different number of outputs. Asymmetric transduction.

---

## Common mistakes

**Assigning $\Phi_{\text{ctyogh}}$ too liberally.** A system that is *near* a phase transition is not necessarily *at* $\Phi_{\text{ctyogh}}$. Only assign $\Phi_{\text{ctyogh}}$ when the system is at or provably flows to a critical fixed point under renormalization.

**Assigning $P_{\text{doublebarpipe}}$ without verification.** This is the most frequently over-assigned primitive. It requires that encoding and decoding are exactly inverse — not approximately, not morally, but provably. If in doubt, assign $P_{\text{subdoublearrow}}$.

**Confusing spatial dimension with $D$.** A 3D physical system does not automatically get $D_{\text{invomega}}$. $D$ measures the complexity of the *algebra's state space*, not the dimension of the space the system lives in.

**Assigning $K_{\text{teshlig}}$ to intermediate layers.** $K_{\text{teshlig}}$ propagates under tensor coupling — one trapped block makes the whole chain trapped. Reserve it for final output states.

**Assigning $\Omega \neq \Omega_{\text{closeepsilon}}$ without a topological invariant.** Winding is a precise homotopy-theoretic property, not a metaphor for robustness. A system that is robust against noise is not necessarily $\Omega_{\text{dzlig}}$. Look for a discrete topological invariant (winding number, Chern number, $\mathbb{Z}_2$ index) — the winding class labels the homotopy class of the system's order parameter map.

**Treating $\Phi_{\text{revepsilon}}$ as $\Phi_{\text{ctyogh}}$.** The exceptional point is near but not at the critical manifold. $\Phi_{\text{revepsilon}}$ has ordinal 2.67 > $\Phi_{\text{ctyogh}}$ = 2.00 in the ordering, meaning $\Phi_{\text{revepsilon}}$ **destroys $O_\infty$** under tensor coupling — it does not promote to it. A system at an exceptional point is $O_0$.

---

## The ouroboricity tier

Once $(\Phi, P, \Omega, D)$ are assigned, the tier follows deterministically:

| Rule | Tier | Condition |
|------|------|-----------|
| R1 | $O_\infty$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$ **and** $P = P_{\text{doublebarpipe}}$ |
| R2 | $O_0$ | $\Phi \notin \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$ |
| R3 | $O_1$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$ **and** $\Omega = \Omega_{\text{closeepsilon}}$ |
| R4 | $O_2$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$ **and** $\Omega \neq \Omega_{\text{closeepsilon}}$ **and** $D \in \{D_{\text{wynn}}, D_{\text{turnthree}}, D_{\text{omega}}\}$ |
| R5 | $O_2^\dagger$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$ **and** $\Omega \neq \Omega_{\text{closeepsilon}}$ **and** $D = D_{\text{invomega}}$ |

Rules apply in priority order: R1 before R2, R2 before R3–R5.

---

## What encoding enables

**Structural distance** $d(\mathbf{x}, \mathbf{y})$: how different are two systems structurally? Computed as a weighted Euclidean distance over the ordinal values of all 12 primitives. Symmetric. Range: 0 to ~11.

**Directed distance** $d_\to(\mathbf{x}, \mathbf{y})$: how much structural work is required to drive system $\mathbf{y}$ from the equilibrium state of $\mathbf{x}$? Asymmetric — $d_\to(\mathbf{x}, \mathbf{y}) \neq d_\to(\mathbf{y}, \mathbf{x})$ in general. Used to identify which direction is driven and which is relaxation.

**Tensor product** $\mathbf{x} \otimes \mathbf{y}$: the structural type of two coupled systems. Union primitives take $\max$; bottleneck primitives ($P$, $F$) take $\min$. This is the most important operation for analyzing composite systems.

**Lattice meet** $\mathbf{x} \wedge \mathbf{y}$: the largest structural type contained in both $\mathbf{x}$ and $\mathbf{y}$ — the common subalgebra.

**Lattice join** $\mathbf{x} \vee \mathbf{y}$: the smallest structural type containing both $\mathbf{x}$ and $\mathbf{y}$ — the minimal superalgebra.

**Le Chatelier inversion**: given a driven system $\mathbf{y}$, find the equilibrium algebra $\mathbf{x}^*$ such that $d_\to(\mathbf{y}, \mathbf{x}^*) = 0$, maximizing $\mathcal{O}(\mathbf{x}^*)$. Asks: what is the natural resting state that $\mathbf{y}$ is being driven away from?

**Nearest-neighbor search**: sort the full catalog by $d(\mathbf{x}, \cdot)$ to find the known systems most structurally similar to a new encoding.

All operations are available via `IΓ_inquiry.py` (interactive agent) or `imscribe` CLI.

---

## Worked example: the Ising model at criticality

**System**: 2D Ising model at $T = Þ_c$.

| Primitive | Assignment | Reasoning |
|-----------|-----------|-----------|
| $\Phi$ | $\Phi_{\text{ctyogh}}$ | Exactly at the critical point; scale-free fluctuations; fixed point of RG. |
| $P$ | $P_{\text{pipevar}}$ | $\mathbb{Z}_2$ spin-flip symmetry is present but the Frobenius condition is not exactly satisfied (no exact $\mu \circ \delta = \text{id}$). |
| $\Omega$ | $\Omega_{\text{crtwo}}$ | Criticality is protected by the $\mathbb{Z}_2$ symmetry: perturbing with a magnetic field (breaking $\mathbb{Z}_2$) immediately destroys the critical point. |
| $D$ | $D_{\text{turnthree}}$ | Finite 2D lattice; sub-infinite state space; mesoscopic. |
| $T$ | $T_\text{box}$ | Product structure: $\sigma_i \in \{-1,+1\}^N$. |
| $R$ | $R_{\text{ctz}}$ | Transfer matrix gives morphisms that compose; no natural adjoint. |
| $F$ | $F_{\text{beltl}}$ | Classical system; no quantum coherence. |
| $K$ | $K_{\text{turnm}}$ | Glauber or Metropolis dynamics — moderate equilibration rate. |
| $G$ | $G_{\text{gamma}}$ | Mesoscopic scale; not microscopic (single spin) or macroscopic (field theory). |
| $\Gamma$ | $\Gamma_{\text{corner}}$ | All spins updated in parallel (or effectively so in the thermodynamic limit). |
| $H$ | $H_0$ | Time-symmetric Boltzmann distribution; no temporal memory. |
| $S$ | $n{:}n$ | $N$ spins in, $N$ spins out. |

**Tuple**: $\langle D_{\text{turnthree}};\ T_\text{box};\ R_{\text{ctz}};\ P_{\text{pipevar}};\ F_{\text{beltl}};\ K_{\text{turnm}};\ G_{\text{gamma}};\ \Gamma_{\text{corner}};\ \Phi_{\text{ctyogh}};\ H_0;\ n{:}n;\ \Omega_{\text{crtwo}} \rangle$

**Tier**: R4 applies ($\Phi_{\text{ctyogh}}$, $\Omega_{\text{crtwo}} \neq \Omega_{\text{closeepsilon}}$, $D_{\text{turnthree}} \neq D_{\text{invomega}}$) → $O_2$.

---

## Tools

```bash
# Interactive encoding session
python IΓ_inquiry.py

# Encode a system
imscribe encode "system_name" --tuple "Ð_ß;Þ_box;Ř_Ť;Φ_};..."

# Compute distance
imscribe distance system_a system_b

# Find tier
imscribe ouroborics system_name

# Nearest neighbors
imscribe nearest system_name --n 5
```

Within `syncon_inquiry`, the agent can accept natural-language descriptions and derive the tuple, asking clarifying questions about any ambiguous primitives.

---

## Further reading

- **PRIMITIVE_THEOREMS.md** — formal theorems underlying the encoding rules (§23: Frobenius non-synthesizability; §64: Crystal enumeration; §68: arithmetic ouroboros)
- **IΓ_ONTICS.md** — ontological theorems about what encodings mean
- **IΓ_DIAPHORICS.md** — empirical predictions derived from encodings (P-1 through P-475+)
- **PERIODIC_CRYSTAL_Oƒ_TYPES.md** — six worked algebra encodings at different tiers
- **CRYSTAL_STANDALONE.md** — self-contained introduction to the crystal structure
- **IΓ_catalog.json** — 1,200+ encoded systems (source of truth)
