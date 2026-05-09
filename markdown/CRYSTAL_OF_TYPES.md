---
title: Crystal of Types
version: 2.0
date: 2026-04-10
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---

# Crystal of Types

The 12-primitive tuple $\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$ is a coordinate chart on the space of structural types. Three ontological layers: **Types** — the 17,280,000 coordinate positions (structural universals, fully determined by their tuple); **Particulars** — concrete systems that instantiate a type (catalog entries: dynasties, ecosystems, consciousness states, algebras, proofs); **Names** — string identifiers for particulars. Two particulars at $d = 0$ are co-typed: the same structural universal, different referents. This document enumerates the type space.

---

## I. The Full Space

The canonical value sets (v0.5.1: $\Omega_{\text{turna}}$ as 4th $\Omega$ value, $K_{\text{lambda}}$ as 5th $K$ value) give:

$$4 \times 5 \times 4 \times 5 \times 3 \times 5 \times 3 \times 4 \times 5 \times 4 \times 3 \times 4 = 17{,}280{,}000 \text{ structural types}$$

The space factors as a **tier crystal** overlaid on an **inner crystal**:

| Layer | Primitives | Values | Count |
|-------|-----------|--------|-------|
| Tier-determining | $\Phi,\ P,\ \Omega,\ D$ | $5 \times 5 \times 4 \times 4$ | 400 tier cells |
| Inner crystal | $T,\ R,\ F,\ K,\ G,\ \Gamma,\ H,\ S$ | $5 \times 4 \times 3 \times 5 \times 3 \times 4 \times 4 \times 3$ | 43,200 types per cell |
| **Total** | all 12 | | **17,280,000** |

The ouroboricity tier — the algebra's capacity for self-referential structure — is determined entirely by $(\Phi, P, \Omega, D)$. The remaining 8 primitives describe the algebra's internal geometry but do not change its tier.

---

## II. The Periodic Table

The crystal organizes naturally as a **5 × 4 periodic table** with $\Phi$ as period (row) and $\Omega$ as group (column). Each cell contains exactly $5(P) \times 4(D) \times 43{,}200(\text{inner}) = 864{,}000$ structural types, uniformly.

| Period ($\Phi$) | $\Omega_{\text{closeepsilon}}$ | $\Omega_{Z_2}$ | $\Ω_z$ | $\Omega_{\text{turna}}$ | Dominant tier | Analogy |
|----------------|-----------|----------------|------------|-------------------|---------------|---------|
| $\Phi_{\text{softsign}}$ — ordered | 864,000 | 864,000 | 864,000 | 864,000 | $O_0$ | alkaline earth — inert, ordered, bonded |
| $\Phi_{\text{ctyogh}}$ — real-axis critical | 864,000 | 864,000 | 864,000 | 864,000 | $O_2$ | transition metal — rich inner structure |
| $\Phi_{\text{closerevepsilon}}$ — complex-axis critical | 864,000 | 864,000 | 864,000 | 864,000 | $O_2$ | transition metal (complex branch) |
| $\Phi_{\text{revepsilon}}$ — exceptional point | 864,000 | 864,000 | 864,000 | 864,000 | $O_0$ | noble gas — closed, non-self-referential |
| $\Phi_{\text{upstep}}$ — disordered | 864,000 | 864,000 | 864,000 | 864,000 | $O_0$ | halogen — disordered, reactive outward |

Every cell has the same total count. What differs between cells is the **tier distribution** — the internal mix of $O_0$, $O_1$, $O_2$, $O_2^\dagger$, $O_\infty$ types within the cell.

---

## III. Tier Census

The five ouroboricity tiers partition the full space:

| Tier | Rule | Tier cells | Types | Share |
|------|------|-----------|-------|-------|
| $O_0$ | $\Phi \in \{\Phi_{\text{softsign}}, \Phi_{\text{upstep}}, \Phi_{\text{revepsilon}}\}$ | 240 | 10,368,000 | 60.0% |
| $O_1$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$, $P \neq P_{\text{doublebarpipe}}$, $\Omega = \Omega_{\text{closeepsilon}}$ | 32 | 1,382,400 | 8.0% |
| $O_2$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$, $P \neq P_{\text{doublebarpipe}}$, $\Omega \neq \Omega_{\text{closeepsilon}}$, $D \in \{D_{\text{wynn}}, D_{\text{turnthree}}, D_{\text{omega}}\}$ | 72 | 3,110,400 | 18.0% |
| $O_2^\dagger$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$, $P \neq P_{\text{doublebarpipe}}$, $\Omega \neq \Omega_{\text{closeepsilon}}$, $D_{\text{invomega}}$ | 24 | 1,036,800 | 6.0% |
| $O_\infty$ | $\Phi \in \{\Phi_{\text{ctyogh}}, \Phi_{\text{closerevepsilon}}\}$, $P = P_{\text{doublebarpipe}}$ | 32 | 1,382,400 | 8.0% |

**The critical subtotal** ($O_1 + O_2 + O_2^\dagger + O_\infty$): 6,912,000 types — exactly 40% of the full space.

The 60/40 split between non-critical and critical is not arbitrary: the grammar has 3 non-critical $\Phi$ values and 2 critical ones, so the ratio traces directly to the $\Phi$ distribution. Adding $\Omega_{\text{turna}}$ (v0.5.1) preserved this split exactly — $\Omega$ does not appear in the critical/non-critical partition, only in the $O_1/O_2/O_2^\dagger$ sub-partition within the critical block.

---

## IV. The P-Axis: Frobenius Collapse

Within each critical period ($\Phi_{\text{ctyogh}}$ or $\Phi_{\text{closerevepsilon}}$), the parity primitive $P$ acts as a **vertical collapse operator**:

| $P$ value | $\Omega_{\text{closeepsilon}}$ | $\Omega \neq \Omega_{\text{closeepsilon}}$, $D$ bounded | $\Omega \neq \Omega_{\text{closeepsilon}}$, $D_{\text{invomega}}$ |
|-----------|------------|--------------------------------------|--------------------------------------|
| $P_{\text{aolig}}$ | $O_1$ | $O_2$ | $O_2^\dagger$ |
| $P_{\text{upsilon}}$ | $O_1$ | $O_2$ | $O_2^\dagger$ |
| $P_{\text{pipevar}}$ | $O_1$ | $O_2$ | $O_2^\dagger$ |
| $P_{\text{subdoublearrow}}$ | $O_1$ | $O_2$ | $O_2^\dagger$ |
| $P_{\text{doublebarpipe}}$ | $\mathbf{O_\infty}$ | $\mathbf{O_\infty}$ | $\mathbf{O_\infty}$ |

$P_{\text{doublebarpipe}}$ **collapses all four $\Omega$ columns and both $D$ branches to $O_\infty$** (R1 overrides R3/R4/R5). The Frobenius condition $\mu \circ \delta = \mathrm{id}$ is the strongest structural constraint in the grammar — it erases all dependence on winding and dimensionality. A Frobenius algebra at criticality needs no external support.

The four non-Frobenius $P$ values ($P_{\text{aolig}}$, $P_{\text{upsilon}}$, $P_{\text{pipevar}}$, $P_{\text{subdoublearrow}}$) are tier-indistinguishable among themselves: all route to the same $O_1/O_2/O_2^\dagger$ tier by the $\Omega/D$ branching rules. The distinction between them lives entirely in the **inner crystal** — in the algebra's symmetry character, not its self-referential capacity.

---

## V. The Inner Crystal

Within each of the 400 tier cells, the 8 free primitives $(T, R, F, K, G, \Gamma, H, S)$ define a sub-crystal of **43,200 types**. This inner crystal factors into four sub-groups:

| Sub-group | Primitives | Combinations | Structural role |
|-----------|-----------|-------------|-----------------|
| Existence tier | $F \times K$ | $3 \times 5 = 15$ | Fidelity of encoding × kinetic regime |
| Scope tier | $G \times \Gamma$ | $3 \times 4 = 12$ | Granularity × interaction grammar |
| Geometric tier | $T \times R$ | $5 \times 4 = 20$ | Topology × relational mode |
| Temporal tier | $H \times S$ | $4 \times 3 = 12$ | Chirality depth × stoichiometry |

$$43{,}200 = 15_{\text{exist}} \times 12_{\text{scope}} \times 20_{\text{geom}} \times 12_{\text{temp}}$$

This factorization is exact. $K_{\text{lambda}}$ (many-body localization, v0.5.1) enlarged the existence tier from $3 \times 4 = 12$ to $3 \times 5 = 15$, reflecting that MBL is a distinct kinetic regime — disorder-frozen like $K_{\text{teshlig}}$ but by a fundamentally different mechanism (Anderson localization rather than potential trapping). The geometric tier remains the largest sub-group (20 vs 12–15 for the others).

The inner crystal is where the conventional distinctions between algebraic structures live: two algebras in the same tier cell but with different $(T, R)$ coordinates differ in how their operations are assembled (network vs. internalized vs. bowtie vs. box vs. imscriptive topology) and in their relational mode (subordinate/categorical/dagger/bidirectional). Same tier, different geometry.

---

## VI. Tier Blocks as Chemical Families

The periodic table analogy runs deeper than aesthetics.

**$O_0$ — the inert block (60%):** Algebras at $\Phi_{\text{softsign}}$, $\Phi_{\text{upstep}}$, or $\Phi_{\text{revepsilon}}$ cannot form self-referential critical loops. $\Phi_{\text{softsign}}$ algebras are over-ordered (too much symmetry); $\Phi_{\text{upstep}}$ are under-constrained (too much disorder); $\Phi_{\text{revepsilon}}$ algebras collapse two eigenstates into one at the exceptional point and lose the $Z_2$ symmetry required for the loop. These are the algebras of *description* — they encode structure but do not self-generate. Ordinary groups, rings, modules, and classical varieties live here.

**$O_1$ — the reactive non-metals (8%):** Critical, no winding. These algebras can form a self-referential loop, but any perturbation can dissolve it. Every deep unproven mathematical conjecture encodes here — the ABC conjecture, Birch–Swinnerton-Dyer, Collatz. The loop exists; it is not locked. $O_1$ is the algebra of *open questions*. The category of $O_1$ algebras is where mathematical research lives — at criticality, before proof closes the Frobenius condition.

**$O_2$ — the transition metals (18%):** Critical, topologically protected, bounded domain. The self-referential loop is stable against continuous deformation (a $Z_2$ or $\mathbb{Z}$-winding prevents it dissolving) but operates within a finite domain. Standard Model gauge algebras, topological quantum field theories, quantum groups away from roots of unity, subfactor standard invariants. The richest diversity of known algebraic structures lives here — 72 tier cells, 18% of the full space. The $\Omega_{\text{turna}}$ column (v0.5.1) adds 24 new $O_2$ cells for non-Abelian winding: algebras of anyonic braiding, Fibonacci categories, and non-Abelian Chern-Simons theories.

**$O_2^\dagger$ — the lanthanides (6%):** Critical, topologically protected, unbounded domain ($D_{\text{invomega}}$). The smallest tier by count but structurally the most generative: the self-referential loop produces further structure without bound. Affine Kac-Moody algebras, affine Hecke algebras, the A2† quantum critical phase transition (Le Chatelier equilibrium of A3). The label $\dagger$ signals that these algebras have a preferred direction of development — they are not merely stable, they *grow*.

**$O_\infty$ — the noble gases (8%):** $P_{\text{doublebarpipe}}$ at criticality. The Frobenius condition $\mu \circ \delta = \mathrm{id}$ is exactly satisfied — the algebra is its own dual and needs no external structure to complete itself. Every proved theorem encodes here (the *proven manifold*). The Moonshine VOA, the Hall algebra of quiver representations, kissing numbers in dimensions 8 and 24, the Ringel-Green theorem. $O_\infty$ algebras do not need $\Omega$ or $D$ to be large — the Frobenius condition overrides all those structural demands. They are complete as they are.

The "noble gas" analogy holds in a precise sense: just as noble gases don't form compounds because their valence shells are full, $O_\infty$ algebras don't need to compose with other structures to achieve their self-referential closure — it is already exact. Tensor product with a non-$O_\infty$ algebra *destroys* $O_\infty$ status (via the $P$ bottleneck rule: $P_{\text{doublebarpipe}} \otimes P < P_{\text{doublebarpipe}}$ → demoted).

---

## VII. Catalog Coverage

The 1,170-entry catalog samples the crystal as follows:

| Tier | Catalog entries | Coverage of 17.3M | Examples |
|------|----------------|-------------------|---------|
| $O_0$ | 575 (49.1%) | $575 / 10{,}368{,}000 = 0.0055\%$ | groups, rings, ordinary metals, dark matter |
| $O_1$ | 152 (13.0%) | $152 / 1{,}382{,}400 = 0.011\%$ | open conjectures, photons, $W/Z$ bosons |
| $O_2$ | 257 (22.0%) | $257 / 3{,}110{,}400 = 0.0083\%$ | Higgs, inflaton, topological insulators |
| $O_2^\dagger$ | 67 (5.7%) | $67 / 1{,}036{,}800 = 0.0065\%$ | affine KM, A2†, Ein Sof |
| $O_\infty$ | 119 (10.2%) | $119 / 1{,}382{,}400 = 0.0086\%$ | proved theorems, Moonshine VOA, Hebrew $O_\infty$ letters |

Sampling density is **remarkably uniform across tiers** (~0.007–0.011% per tier). The catalog is not biased toward any particular structural class — it samples the critical and non-critical regions proportionally to their size.

---

## VIII. Key Structural Identities from the Crystal

**The critical boundary:** The transition $\Phi_{\text{softsign}} \to \Phi_{\text{ctyogh}}$ adds 8% + 18% + 6% + 8% = 40% of all structural types. The critical period is not a refinement of the ordered period — it opens an entirely new 40% of the space.

**$O_\infty$ as the universal upper bound:** $O_\infty$ is closed under lattice join with anything — $O_\infty \vee x = O_\infty$ only if $x$ itself is $O_\infty$ (otherwise join produces something in $[O_1, O_2^\dagger]$ depending on the primitive merge). $O_\infty$ is NOT closed under tensor: $O_\infty \otimes O_1 \to O_1$ (P bottleneck destroys Frobenius). The proven manifold is fragile under composition but stable as a lattice ceiling.

**$\Phi_{\text{revepsilon}}$ as a structural anomaly:** Exceptional-point algebras ($\Phi_{\text{revepsilon}}$) have the highest ordinal of any non-critical $\Phi$ value (ordinal 2.67, above $\Phi_{\text{ctyogh}} = 2.00$). They absorb $O_\infty$ under tensor — any system composed with a $\Phi_{\text{revepsilon}}$ system loses its Frobenius exactness and reverts to $O_0$. $\Phi_{\text{revepsilon}}$ is the one $\Phi$ value that is both *above* the critical surface in ordinal and *below* it in self-referential capacity. This is the grammar's encoding of non-Hermitian criticality: higher energy, no self-reference.

**The 240:160 ratio:** Non-critical tier cells (240) vs critical tier cells (160) in a 3:2 ratio, matching exactly the 3:2 ratio of non-critical to critical $\Phi$ values. The periodic table is symmetric in this sense — criticality is neither dominant nor marginal; it is the minority by count but the majority of structural richness. This ratio is preserved under any expansion of $\Omega$ or $D$ (which affect both sides equally) and changes only if new $\Phi$ values are added.

**$D_{\text{invomega}}$ as a splitter:** Among the 4 values of $D$, exactly one ($D_{\text{invomega}}$) separates $O_2$ from $O_2^\dagger$. The other three ($D_{\text{wynn}}$, $D_{\text{turnthree}}$, $D_{\text{omega}}$) are structurally equivalent for tier purposes. This means $O_2^\dagger$ is 1/3 the size of $O_2$ (1,036,800 vs 3,110,400 = exactly 1:3). Unbounded-domain algebras are the rarest protected-critical type.

**$\Omega_{\text{turna}}$ as a new column:** Non-Abelian winding ($\Omega_{\text{turna}}$) adds an entire new $\Omega$ column to the periodic table. Within the critical periods it creates 24 new $O_2$ cells and 8 new $O_2^\dagger$ cells — the algebras of non-Abelian anyons, Fibonacci topological order, and Haagerup subfactors all fall here. The tier rules are unchanged; $\Omega_{\text{turna}}$ simply satisfies $\Omega \neq \Omega_{\text{closeepsilon}}$ and gets routed by $D$ as before.

---

## IX. Navigating the Crystal

The five grammar moves from PRIMITIVE_THEOREMS §55 map directly onto crystal coordinates:

| Move | Crystal action |
|------|---------------|
| **Le Chatelier inversion** | Find the $O_\infty$ or $O_2^\dagger$ point that a driven system flows toward |
| **Tensor coupling** | Move to the $(\min_P, \min_F)$ intersection of two cells' coordinates |
| **Lattice meet** | Find the lower-left corner of two cells' bounding box |
| **Directed distance** | Count ordinal steps upward from one cell to another |
| **Nearest-neighbor search** | Sample the catalog for the closest inhabited point |

The crystal is not a static taxonomy — it is a dynamical space. Systems flow between cells under renormalization, phase transitions, and compositional coupling. The ouroboricity tier is the invariant that classifies which fixed points a system can reach.

---

## X. The 400-Cell Tier Lattice

The full tier structure is encoded in 400 cells:

$$(\Phi_5) \times (P_5) \times (\Omega_4) \times (D_4) = 400 \text{ tier cells}$$

These 400 cells form a sub-lattice of the full 17.3M-type space. Within this sub-lattice:
- 240 cells are $O_0$ (inert)
- 32 cells are $O_\infty$ (complete)
- 32 cells are $O_1$ (self-referential, unprotected)
- 72 cells are $O_2$ (protected, bounded)
- 24 cells are $O_2^\dagger$ (protected, unbounded)

The lattice has a natural total order under the ouroboricity tier: $O_0 < O_1 < O_2 \approx O_2^\dagger < O_\infty$ (with $O_2$ and $O_2^\dagger$ on different branches rather than ordered relative to each other). This is not a linear order — the crystal has a genuine branching at the $O_2/O_2^\dagger$ split determined by $D$.

---

*Generated by `crystal_enumeration.py` · v2.0 · 2026-04-10*
*Catalog: 1,170 entries · Grammar: 12-primitive tuple v0.5.1 ($\Omega_{\text{turna}}$ + $K_{\text{lambda}}$ canonical)*
