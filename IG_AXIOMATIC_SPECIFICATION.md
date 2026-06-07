# The Imscribing Grammar — Axiomatic Specification

**Purpose.** This document specifies the Imscribing Grammar (IG) as a mathematical object. All definitions below are to be treated as given. The document provides sufficient specification to compute structural types, distances, tier assignments, and C-scores without further grounding. The IG is a defined formal system — the question is not whether it is "real" but what follows from its axioms.

---

## §1 Ambient Category

Let $\mathbf{C} = (C, \otimes, I, \sigma)$ be a symmetric monoidal category enriched over the Belnap-Dunn bilattice $\mathbf{FOUR} = \{N, T, F, B\}$. Hom-sets carry the bilattice partial order. $B$ ("both") is a paraconsistent state in which a morphism is simultaneously affirmed and denied; $N$ ("neither") is an underdetermined state. The inference $B \to \bot$ is not admissible: no $B$-valued hom-set collapses to the zero morphism. The category is not Boolean.

**Trace.** $C$ carries a trace $\mathrm{Tr}: \mathrm{End}(A \otimes U) \to \mathrm{End}(A)$ for each object pair, implemented by the Ω (Winding) primitive acting on the monoidal unit. This is the traced symmetric monoidal structure of Joyal-Street-Verity. Ω is not compact/dual structure; the trace is primitive, not derived from a duality.

---

## §2 Frobenius Structure

The monoidal unit $I$ carries a special symmetric $\dagger$-Frobenius structure:

- $\mu: I \otimes I \to I$ (multiplication)
- $\delta: I \to I \otimes I$ (comultiplication)
- $\eta = \varepsilon = \mathrm{id}_I$ (unit/counit collapse at scalar level)

satisfying:

1. **Frobenius law**: $(\mu \otimes \mathrm{id}) \circ (\mathrm{id} \otimes \delta) = \delta \circ \mu = (\mathrm{id} \otimes \mu) \circ (\delta \otimes \mathrm{id})$
2. **Special condition**: $\mu \circ \delta = \mathrm{id}_I$
3. **Symmetry**: $\mu \circ \sigma_{I,I} = \mu$
4. **Dagger**: $\mu^\dagger = \delta$, where $(-)^\dagger: C \to C^{\mathrm{op}}$ is the dagger involution

**Commutativity is a theorem.** All 12 generators are endomorphisms of $I$ — scalars of $C$. In any SMC, scalars commute: for $f, g: I \to I$, the coherence isomorphisms give $f \otimes g = g \otimes f$. Condition (3) follows from the scalar structure and need not be assumed independently.

**FOUR-$\dagger$ compatibility.** The dagger functor preserves FOUR-values: if $h$ has value $v \in \{N,T,F,B\}$, then $h^\dagger$ has value $v$. $B$-valued morphisms map to $B$-valued morphisms. This must be imposed explicitly — it is not automatic from either structure alone.

---

## §3 Generators

The grammar is presented by **12 primitive endomorphisms of $I$** subject to the Frobenius relations:

> **Ř** (Recognition) · **Ħ** (Chirality) · **Ω** (Winding) · **Ð** (Dimensionality) · **Σ** (Stoichiometry) · **Φ** (Parity) · **Ç** (Kinetics) · **ƒ** (Fidelity) · **ɢ** (Coupling) · **Γ** (Granularity) · **Þ** (Topology) · **⊙** (Criticality)

"Freely generated" means: take the free SMC on these 12 endomorphisms, then impose the Frobenius relations. The result is the free object in the category of special symmetric $\dagger$-Frobenius algebras — not the free category without relations.

**Operadic structure.** The Γ (Granularity) primitive furnishes a multicategory over $C$: $n$-ary operations are first-class and composition is operadic rather than merely sequential. The grammar is an algebra over the Γ-operad.

---

## §4 Crystal of Types

The free special symmetric $\dagger$-Frobenius algebra on 12 generators has crystal structure:

$$3^3 \times 4^5 \times 5^4 = 17{,}280{,}000 \text{ distinct addresses.}$$

This is the **Crystal of Types**: the classifying space of all structurally distinct imscriptions. Each address is a point in the 12-dimensional discrete space whose axes are the primitive ordinal domains (§5).

---

## §5 Structural Type — Notation

A **structural type** (imscription) is a 12-tuple of Shavian values, one per primitive, in canonical order:

**⟨ Ð · Þ · Ř · Φ · ƒ · Ç · Γ · ɢ · ⊙ · Ħ · Σ · Ω ⟩**

The value alphabet is the 49-symbol set: {Shavian alphabet (48 letters)} ∪ {⊙}. Each primitive has a finite ordinal domain (ascending rank):

| Pos | Primitive | Name | Values — ascending ordinal rank |
|-----|-----------|------|---------------------------------|
| 1 | Ð | Dimensionality | 𐑛(1) · 𐑨(2) · 𐑼(3) · 𐑦(4) |
| 2 | Þ | Topology | 𐑡(1) · 𐑰(2) · 𐑥(3) · 𐑶(4) · 𐑸(5) |
| 3 | Ř | Recognition | 𐑩(1) · 𐑑(2) · 𐑽(3) · 𐑾(4) |
| 4 | Φ | Parity | 𐑗(1) · 𐑿(2) · 𐑬(3) · 𐑯(4) · 𐑹(5) |
| 5 | ƒ | Fidelity | 𐑱(1) · 𐑞(2) · 𐑐(3) |
| 6 | Ç | Kinetics | 𐑘(1) · 𐑤(2) · 𐑧(3) · 𐑪(4) · 𐑺(4.5) |
| 7 | Γ | Granularity | 𐑚(1) · 𐑔(2) · 𐑲(3) |
| 8 | ɢ | Coupling | 𐑝(1) · 𐑜(2) · 𐑠(3) · 𐑵(4) |
| 9 | ⊙ | Criticality | 𐑢(1) · ⊙(2) · 𐑮(2.33) · 𐑻(2.67) · 𐑣(3) |
| 10 | Ħ | Chirality | 𐑓(1) · 𐑒(2) · 𐑖(3) · 𐑫(4) |
| 11 | Σ | Stoichiometry | 𐑙(1) · 𐑕(2) · 𐑳(3) |
| 12 | Ω | Winding | 𐑷(1) · 𐑴(2) · 𐑭(3) · 𐑟(4) |

**Worked example — the Rebis** ($O_\infty$, C-score 0.755):

⟨ 𐑦 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑝 · ⊙ · 𐑫 · 𐑳 · 𐑭 ⟩

| Primitive | Value | Ordinal | Reading |
|-----------|-------|---------|---------|
| Ð | 𐑦 | 4 | self-written holographic |
| Þ | 𐑶 | 4 | irreducible product |
| Ř | 𐑾 | 4 | bidirectional feedback |
| Φ | 𐑹 | 5 | Frobenius-special ($\mu \circ \delta = \mathrm{id}$ gate) |
| ƒ | 𐑐 | 3 | quantum |
| Ç | 𐑧 | 3 | slow/near-equilibrium |
| Γ | 𐑲 | 3 | universal/long-range |
| ɢ | 𐑝 | 1 | simultaneous conjunction |
| ⊙ | ⊙ | 2 | critical/self-modeling |
| Ħ | 𐑫 | 4 | eternal (no finite Markov order) |
| Σ | 𐑳 | 3 | many heterogeneous |
| Ω | 𐑭 | 3 | integer winding ($\mathbb{Z}$-valued) |

---

## §6 Structural Metric

The **canonical distance** between two imscriptions $s_1, s_2$ is the diagonal weighted Euclidean distance over ordinal ranks:

$$d(s_1, s_2) = \sqrt{\sum_i w_i \cdot (x_i(s_1) - x_i(s_2))^2}$$

where $x_i(s)$ is the ordinal rank of $s$'s value at position $i$. Canonical weights:

| Ð | Þ | Ř | Φ | ƒ | Ç | Γ | ɢ | ⊙ | Ħ | Σ | Ω |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.8 | 1.0 | 0.7 |

The distance is symmetric, satisfies the triangle inequality, and is zero iff $s_1 = s_2$.

Regime thresholds: $d < 2.0$ = same structural regime; $d > 4.0$ = structurally remote; $d > 5.0$ = different tier class.

**Worked distance example.** Between `ouroboric_pill` ($O_\infty$ child of the Rebis) and `plastic_photonic_crystal` ($O_2$, periodic lattice): $d = 5.74$. Largest contributors: Þ (topology, $\Delta = 16.0$), Ð (dimensionality, $\Delta = 4.0$), Ħ (chirality, $\Delta = 3.2$).

---

## §7 Ouroboricity Tiers

**Ouroboricity** measures the degree of self-referential Frobenius closure. Five tiers assigned by rules R1–R5 (first match wins):

| Rule | Condition | Tier | Description |
|------|-----------|------|-------------|
| R1 | ⊙ ∈ {⊙, 𐑣} **and** Φ = 𐑹 | $O_\infty$ | Special Frobenius — $\mu \circ \delta = \mathrm{id}$ holds exactly |
| R2 | ⊙ ∈ {𐑢, 𐑮, 𐑻} | $O_0$ | No self-referential loop possible |
| R3 | ⊙ ∈ {⊙, 𐑣} **and** Ω = 𐑷 | $O_1$ | Critical, no topological protection |
| R4 | ⊙ ∈ {⊙, 𐑣} **and** Ω ≠ 𐑷 **and** Ð ∈ {𐑛, 𐑨, 𐑼} | $O_2$ | Critical + protected, bounded domain |
| R5 | ⊙ ∈ {⊙, 𐑣} **and** Ω ≠ 𐑷 **and** Ð = 𐑦 | $O_2^\dagger$ | Critical + protected, unbounded domain |

Default (no rule matches): $O_0$. The three operative gates are **⊙ (Criticality)**, **Φ (Parity)**, and **Ω (Winding)**. Ð (Dimensionality) determines the $O_2$ / $O_2^\dagger$ split.

---

## §8 C-score

The **C-score** measures proximity to $O_\infty$ along two axes, each a hard gate:

- **Gate 1**: ⊙ ∈ {⊙, 𐑣} (criticality threshold open)
- **Gate 2**: Ç ∈ {𐑘, 𐑤, 𐑧, 𐑪} — kinetics not frozen (Ç ≠ 𐑺 order-frozen)

If either gate is closed: $C = 0$. If both open:

$$C = \sum_i w_i \cdot \frac{x_i}{x_{i,\max}}$$

summed over all 12 primitives with normalized ordinal ranks, yielding $C \in [0, 1]$. C-score and tier are independent: a system can be $O_\infty$ (R1 satisfied) with $C < 1$ if some primitives are below maximum ordinal.

---

## §9 Spider Theorem, Fixpoint, T Object

**Spider theorem.** The special Frobenius axiom ($\mu \circ \delta = \mathrm{id}$) together with symmetry implies: any two connected string diagrams in the Prop of the grammar with the same boundary are equal as morphisms. Discriminating condition: **connectedness**, not planarity. The theorem holds for all connected Frobenius diagrams regardless of planar presentation.

**Fixpoint — $O_\infty$.** The ⊙ gate admits an idempotent scalar $\omega: I \to I$ with $\omega \circ \omega = \omega$. $O_\infty$ is the initial algebra of the endofunctor $(-) \circ (-): \mathrm{End}(I) \to \mathrm{End}(I)$; its carrier is the fixpoint in which the grammar is applied to itself. The Frobenius identity $\mu \circ \delta = \mathrm{id}$ requires **Ħ_A (two-step chirality, 𐑖)** as minimum — one split ($\delta$), one merge ($\mu$). Eternal chirality (Ħ = 𐑫) is what physical systems accumulate through time; it is not required by the identity itself.

**Frobenius fixed-point tuple.** The imscription of the identity $\mu \circ \delta = \mathrm{id}$ as a structural object:

⟨ 𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑔 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑭 ⟩

$O_\infty$, C-score $= 1.0$. Proved in `MajoranaFixed.lean`: Belnap $B$ (`bnot B = B`), SIC-POVM fiducial (`meet B x = x`), and Majorana mode (`pair(depair s).1(depair s).2 = s`) are the same computation under $\mu \circ \delta = \mathrm{id}$, each proved by definitional equality (`rfl`).

**Derived object — T.** $T = \lim(\Phi, \text{ƒ}, \text{Ç}, \text{Ħ}, \Omega)$ is a categorical limit over the five primitives Parity, Fidelity, Kinetics, Chirality, Winding. $T$ is not a generator; it is the temporal bootstrap fixed point derived from the free algebra.

---

## §10 Foundational Strength — ZFC_fe

In **ZFC_fe** (Frobenius-Extended ZFC), $\mu \circ \delta = \mathrm{id}$ is taken as a set-formation axiom. The comultiplication $\delta: A \to A \otimes A$ is the primitive set-formation operation; the condition asserts lossless recovery — every set is faithfully recoverable from its copy. ZFC Separation ($\forall \varphi: \{x \in A \mid \varphi(x)\}$ exists) becomes a theorem: the $\delta$-preimage under $\mu$ yields the Separation set for any definable $\varphi$. ZFC_fe strictly extends ZFC and is strictly stronger than ZFC$_\tau$. Open problems in ZFC$_\tau$ close as theorems in ZFC_fe.

---

## §11 Distinctions — Categorical QM and Holography

### Distinction from Abramsky-Coecke categorical QM

In Abramsky-Coecke $\dagger$-compact categories, hom-sets are Bool-valued. In $C$, hom-sets are FOUR-valued. A $B$-valued morphism — simultaneously affirmed and denied — is a legitimate element of $\mathrm{hom}(A,B)$, not a degenerate case. Two incompatible imscriptions of the same boundary coexist in a $B$-valued hom-set without collapse. FOUR has no bottom element below $B$ playing the role of the trivial morphism. Classical QM is recovered as the $T$-valued sub-category. The grammar is intrinsically paraconsistent at the level of its hom-sets; this is not relaxation of rigor but a strictly stronger structure.

### Distinction from holography

**Holography is static isomorphism up to redundancy. Imscription is dynamic identity up to the trace.**

The holographic principle (AdS/CFT, holographic error-correcting codes) asserts that a $d$-dimensional bulk is isomorphic to its $(d-1)$-dimensional boundary. The isomorphism is:

- **Static** — a correspondence between states, not a process; the map exists timelessly between configurations
- **Up to redundancy** — the encoding is overcomplete by design; bulk content can be recovered from partial boundary data via entanglement wedge reconstruction; the redundancy is the gauge group acting on encoding choices

The imscriptive identity $\mu \circ \delta = \mathrm{id}$ is:

- **Dynamic** — a process, not a state equivalence; the system reconstitutes itself through the operation
- **Up to the trace** — equivalence is defined by connected diagrams with the same boundary (Spider theorem); this is topological, not a symmetry of an encoding

The structural consequence is exact: **holography requires a boundary**. The isomorphism lives between bulk and boundary, so the boundary must exist as a distinct object. The Rebis has Ř = 𐑾 (bidirectional — no outside). There is nowhere to put the boundary. Holography can describe $O_2$ systems — bounded domain, topological protection, a surface you can project onto — but it structurally cannot describe $O_\infty$, because $O_\infty$ is the tier at which the distinction between system and boundary collapses.

The redundancy distinguishes them further. In holography, you can lose parts of the boundary and reconstruct the bulk — the encoding is overcomplete, and recovery from partial data is the point. In imscription there is nothing to recover because nothing was ever encoded away from the system. $\mu \circ \delta = \mathrm{id}$ does not preserve information across a gap; it collapses the gap. The system reconstitutes itself through the operation, not from a separate store.

Holographic redundancy is a symmetry of the map. Imscriptive trace is a property of the winding. These are different equivalence relations: one defined by a group action on encoding choices, one defined by the connected topology of the string diagram.

**Holography is the information-theoretic analogue of crystallography.** Both impose an external observer, both achieve their result by projecting onto a lower-dimensional or lower-tier representation, and both destroy the properties of $O_\infty$ systems in the act of representing them. Crystallography freezes Ω (winding collapses 𐑭→𐑷) to produce a static coordinate map. Holography projects Ř (bidirectionality collapses 𐑾→𐑩) to produce a static boundary encoding. In both cases, the representation is faithful to the $O_2$ content and blind to the $O_\infty$ structure.

---

## §12 The Imscription Procedure — Deterministic, Self-Correcting, Falsifiable

An imscription is produced by a **12-step decision procedure** applied to a system's structural description, following canonical primitive order: Ð → Þ → Ř → Φ → ƒ → Ç → Γ → ɢ → ⊙ → Ħ → Σ → Ω. Each step assigns one primitive value from structural facts — mechanism, geometry, stoichiometry, coordination chemistry. No computed observable is an input. Data tests structural predictions after the imscription is fixed.

### Cross-primitive axioms

Inter-primitive consistency is enforced by three named axioms. A tuple that violates any axiom is malformed. All three are proved in `ParadoxBoot.lean` (0 sorrys) and enforced at runtime in `genetic_tuples.py`.

**Axiom A**: Ħ = 𐑫 (eternal, $H_\infty$) $\Rightarrow$ Ç = 𐑺 (order-frozen)

If a system has eternal chirality, it must have order-frozen kinetics. The depth of chirality memory and the kinetic regime are coupled. The Frobenius identity itself lives at $H_A$ (two-step, 𐑖), not $H_\infty$ — Axiom A applies only to structures that accumulate chirality through time beyond what the identity minimally requires.

**Axiom B**: Ω $\in \{$𐑭 $(\mathbb{Z})$, 𐑴 $(\mathbb{Z}_2)\} \Rightarrow$ Ħ $\geq$ ordinal 2 (𐑒 or above)

Topological winding protection requires at least two-step chirality memory to sustain it. A system cannot have topological protection without sufficient memory depth.

**Axiom C**: Ð = 𐑦 (self-written) $\Leftrightarrow$ Þ = 𐑸 (self-referential closure)

Both must be present or neither. A physical system with a state space embedded in external degrees of freedom (Ð = 𐑼, infinite-dim) cannot carry self-referential topology (Þ $\neq$ 𐑸). This is the most commonly violated axiom in practice.

**Additional structural constraints** (unnamed, but checked):
- Ω = 𐑭 ($\mathbb{Z}$ winding) typically requires Ð $\geq$ 𐑼 (infinite-dim)
- ⊙ at criticality + Ç = slow/near-eq → deep critical structure, stable
- ⊙ at criticality + Ç fast/frozen → structural warning

### Falsifiability structure

The type assignment is **prior to and independent of experimental data**. The type carries structural predictions — observable consequences derivable from the primitive assignments:

| Type assignment | Structural prediction | How to test |
|---|---|---|
| ⊙ at criticality | Geometry and electronic structure co-evolve through a divergent region | Plot $\langle S^2 \rangle$ vs bond distance across optimization trajectory |
| Ω = 𐑭 (integer winding) | System returns to origin state after exactly $n$ windings; no half-integer paths | Stoichiometric closure analysis |
| Ħ = 𐑖 (two-step chirality) | Outcome depends on two prior states; stereospecificity is precursor-dependent | Isotopic labeling; chiral substrate series |
| Þ = 𐑰 (crossing point) | Two potential energy surfaces cross; transition state at the crossing | CASSCF scan along reaction coordinate |

Data confirms or falsifies the **structural description**, not the grammar. If a prediction fails: the structural description was wrong; revise the mechanism and re-imscribe. The grammar does not adjust to fit results. It makes a commitment; the data either holds it or breaks it.

---

$\mu \circ \delta = \mathrm{id}$
