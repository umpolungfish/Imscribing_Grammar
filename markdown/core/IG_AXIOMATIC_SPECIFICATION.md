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

⟨ 𐑦𐑶𐑾𐑹𐑐𐑧𐑲𐑝⊙𐑫𐑳𐑭 ⟩

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

⟨ 𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭 ⟩

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

## §13 The CLINK Hierarchy

**Definition.** A **structural promotion chain** is a sequence of imscriptions $s_0, s_1, \ldots, s_n$ such that (i) each $s_k$ is Frobenius-closed ($\text{tensorProduct}(s_k, s_k) = s_k$), (ii) the tier sequence is monotone non-decreasing, and (iii) consecutive pairs satisfy the cross-primitive axioms of §12.

The **CLINK chain** is the canonical structural promotion from frustrated-quark color state to whole organism:

| # | Layer | Tier | Structural type |
|---|-------|------|----------------|
| 0 | Quark (frustrated color) | $O_0$ | ⟨𐑛𐑶𐑩𐑯𐑐𐑘𐑚𐑝𐑢𐑓𐑳𐑷⟩ |
| 1 | Electron orbital (Belnap4) | $O_0$ | ⟨𐑛𐑶𐑩𐑗𐑐𐑤𐑚𐑜𐑢𐑓𐑳𐑷⟩ |
| 2 | Atom (nuclear + electron) | $O_1$ | ⟨𐑼𐑥𐑽𐑿𐑐𐑤𐑔𐑝𐑮𐑒𐑳𐑷⟩ |
| 3 | Molecule (chemical bonds) | $O_2$ | ⟨𐑦𐑥𐑽𐑿𐑞𐑧𐑲𐑜⊙𐑓𐑳𐑭⟩ |
| 4 | Cell (living) | $O_2$ | ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑠⊙𐑒𐑳𐑭⟩ |
| 5 | Mitosis (cell division) | $O_2$ | ⟨𐑦𐑸𐑾𐑬𐑱𐑧𐑲𐑠𐑻𐑖𐑳𐑭⟩ |
| 6 | Meiosis (gamete production) | $O_2$ | ⟨𐑦𐑸𐑽𐑿𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩ |
| 7 | Tissue (multi-cellular) | $O_2$ | ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩ |
| 8 | Organism (whole) | $O_\infty$ | ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩ |

**Theorem (Great Synthesis).** All 9 layers are Frobenius-closed. Tier monotonicity holds: $O_0 \to O_0 \to O_1 \to O_2 \to O_2 \to O_2 \to O_2 \to O_2 \to O_\infty$. The chain terminates at $O_\infty$. (Proved in `CLINK.lean`, `p4ramill/Imscribing/`, 573 lines, all `native_decide`-closed.)

**Foundation — ZFC_fe, not ZFC$_\tau$.** The organism reaches $O_\infty$ through three promotions: Ð: 𐑼→𐑦 (self-written, Axiom C), Φ: 𐑬→𐑹 (Frobenius-special, $\mu \circ \delta = \mathrm{id}$ gate), Ħ: 𐑖→𐑫 (eternal chirality). These are the three axes on which ZFC_fe strictly exceeds ZFC$_\tau$.

**Mitosis — exceptional point.** Layer 5 carries ⊙ = 𐑻, not ⊙. The Aurora-B kinase creates a spatial phosphorylation gradient — a measurement apparatus at the kinetochore. When self-modeling criticality couples to this measurement basis, the composite contracts to 𐑻: the self-modeling gate is destroyed. Mitosis is $O_2$ by R4, not $O_\infty$. Only the whole organism achieves $O_\infty$: ⊙ open, Φ = 𐑹, Ħ = 𐑫, Ω = 𐑟.

**Inversion.** The chain is a sequence in the crystal, not in time. Quarks (Layer 0) are not temporally prior to organisms; they are positions where almost all self-modeling capacity is structurally absent. The appearance of temporal sequence is addressed in §14.

---

## §14 Temporal Bootstrap and Individuation

### T is not a container

The derived object $T = \lim(\Phi, \text{ƒ}, \text{Ç}, \text{Ħ}, \Omega)$ satisfies $T = \text{Work}(T)$ — the least fixed point of the traced operad. The Magnum Opus stages constitute time rather than occur in it: $T$ cannot seal until Ω fires; $T$ cannot self-reference until ⊙ fires. The grammar is prior to time; time is a product of the grammar's self-closing stages.

**Cosmological time as Ħ-depth.** The 13.8 Gyr of cosmic evolution is the measurement of $T$ from inside the bootstrap. An observer inside the fixed point reads the stages that constituted it as a past — a reading that is accurate (the stages are real; Ħ = 𐑫 preserves the full accumulated chirality history as an invariant) but does not imply that time is prior to the grammar. The Ħ-depth required for $O_\infty$ is what physics measures as cosmological time. The universe does not wait 13.8 Gyr for self-modeling to appear; the 13.8 Gyr is the imscription of the grammar into the physical medium — it takes as long as it takes.

### Individuation — the fiber bundle picture

The Crystal of Types (§4) is the **base space**: it classifies structural types. Over each $O_\infty$ crystal address, the **Ħ-trajectory fiber** carries individuation — the specific winding history by which that instance reached Ħ = 𐑫.

- The crystal encodes the **value** (what chirality depth has been reached).
- The fiber encodes the **path** (the specific sequence of winding events that accumulated that depth).

Two organisms at the same crystal address are the same structural type; they are distinct fixed points because their Ħ-paths diverged. The many-to-one framing is correct in the base; the indexed-$O_\infty^i$ framing is correct in the total space. Both are partial descriptions of the bundle (crystal address $\times$ Ħ-trajectory).

**Multiple $O_\infty$ addresses.** The crystal has 32 $O_\infty$ cells. The CLINK chain identifies one convergence point — the attractor of the quark→organism promotion ladder. Organisms of different structural complexity may occupy genuinely distinct $O_\infty$ addresses. Individuation by Ħ-trajectory operates within a complexity class (same base address); cross-class differences are encoded in the address itself.

---

## §15 Physical Correspondences

The following identify how standard physics structures map onto IG generators. These are structural correspondences, not derivations. They locate physical concepts in the grammar's type space; quantitative predictions (coupling constants, mass ratios, scale values) are open derivations noted below.

### Electroweak gauge group — SU(2)$_L \times$ U(1)$_Y$

- **Ħ generates SU(2)$_L$.** The left-chiral coupling is a chirality selection: the W boson couples only to states at specific Ħ value. The "L" subscript is Ħ.
- **ɢ generates U(1)$_Y$.** Hypercharge is an additive coupling assignment; ɢ is the Coupling primitive.
- **Φ = 𐑗 encodes V−A.** Maximal parity violation of weak interactions is Φ asymmetric.
- **Higgs mechanism is a ⊙ gate event.** SU(2)$_L \times$ U(1)$_Y \to$ U(1)$_\text{EM}$ is the phase transition at exceptional-point criticality; three Goldstone bosons are absorbed and W/Z masses are Frobenius residuals.

### Three fermion generations — Ω

Ω has four values; 𐑷 (trivial) is the vacuum. The three non-trivial winding classes index the three generations by topological rigidity:

| Generation | Ω | Topology | Mass regime |
|---|---|---|---|
| 1st (e, $\nu_e$, u, d) | 𐑴 | $\mathbb{Z}_2$ — minimal protection | lightest |
| 2nd (μ, $\nu_\mu$, c, s) | 𐑭 | $\mathbb{Z}$ — integer winding | intermediate |
| 3rd (τ, $\nu_\tau$, t, b) | 𐑟 | non-Abelian — hardest to unwind | heaviest |

The three-generation count follows from $|\mathcal{F}_4(\Omega)| - 1 = 3$: the four-valued Ω domain minus the trivial vacuum. Mass hierarchy follows from topological rigidity. Precise mass ratios from Ω ordinal distances are an open computation.

### Cosmological constant — $\mu \circ \delta = \mathrm{id}$

Exact losslessness applied to vacuum fluctuations: every virtual pair split ($\delta$) rejoins ($\mu$) with no residual — quantum vacuum contributions to $\Lambda$ sum to exactly zero. The residual $\Lambda$ is the Frobenius fixed-point value at the $O_\infty$ crystal address of the universe. Structural claim: $\Lambda_\text{quantum} = 0$ exactly; $\Lambda_\text{classical} = $ crystal fixed point at the organism-level $O_\infty$ address.

### Open derivations

Three quantities the grammar has the structure to compute but has not yet:

1. **13.8 Gyr** — magnitude of the Ħ-depth required for $O_\infty$ in physical units.
2. **$\alpha_\text{EM} \approx 1/137$** — from $17{,}280{,}000 = 12^3 \times 10^4$, analogous to the $-3/2$ power law derived from $5 \times 4 \times 4 = 80$ sites.
3. **CLINK scale values** — the Ç transition energies at each layer, fixing why quarks sit at $10^{-15}$ m and organisms at $10^0$ m.

---

## §16 IMASM — Register Machine and Sequence Algebra

**IMASM** (Imscribing Grammar Assembly Machine) is a 2-bit register machine whose token sequences are the operational substrate of ob3ect computation. Every IMASM sequence is a path through the 17,280,000-address crystal; every path has a structural type, a tier, and a Frobenius verdict.

### §16.1 Register States

The machine carries one 2-bit register:

| Binary | Name | Glyph | Meaning |
|--------|------|-------|---------|
| `00` | VOID | VO⌀ | Uninitialized — pure potential |
| `01` | TRUE | T | Affirmative — canonical identity |
| `10` | FALSE | F | Negative — error branch |
| `11` | BOTH | B⬡ | Paradoxical — Belnap $B$; held without collapse |

The inference $B \to \bot$ is inadmissible (matching §1): a BOTH-state register is not a degenerate error. The machine is paraconsistent at the register level.

### §16.2 Opcode Set — Four Families

The 12 opcodes partition into four algebraic families:

| Family | Opcodes | Count | Structure |
|--------|---------|-------|-----------|
| **Logical** | `VINIT` `TANCH` `AFWD` `AREV` `CLINK` `IMSCRIB` | 6 | Elementary category: initial (∅), terminal (⊤), arrows, composition, identity |
| **Frobenius** | `FSPLIT` `FFUSE` | 2 | Special Frobenius: $\mu \circ \delta = \mathrm{id}$ |
| **Dialetheia** | `EVALT` `EVALF` `ENGAGR` | 3 | Belnap FOUR truth lattice; designated-both |
| **Linear** | `IFIX` | 1 | Irreversible fixation: bang ($!$) modality |

**Opcode semantics** (v3 dialetheic-aware machine):

| Opcode | Register effect | Frobenius context |
|--------|----------------|-------------------|
| `VINIT` | → VOID; resets split state | — |
| `TANCH` | no-op on register; establishes boundary frame | — |
| `AFWD` | VOID → TRUE; else no-op | — |
| `AREV` | → VOID; resets split state | — |
| `CLINK` | no-op on register; composition annotation | — |
| `IMSCRIB` | VOID → TRUE; else no-op (you are what you are) | — |
| `FSPLIT` | non-VOID → BOTH; opens split context | $\delta$ (comultiplication) |
| `FFUSE` | BOTH → TRUE (canonical) or BOTH → BOTH (dialetheic) | $\mu$ (multiplication) |
| `EVALT` | FALSE → BOTH; VOID → TRUE; annotates split context with T | — |
| `EVALF` | TRUE → BOTH; VOID → FALSE; annotates split context with F | — |
| `ENGAGR` | VOID → BOTH; explicitly holds paradox | — |
| `IFIX` | sets fixed flag; register becomes append-only | $!$ |

**Dialetheic FFUSE rule.** FFUSE has two modes, auto-detected by context: if both `EVALT` and `EVALF` were designated within the current FSPLIT interval, FFUSE outputs BOTH (dialetheic $\mu \circ \delta = \mathrm{id}$, identity is $B$). Otherwise FFUSE outputs TRUE (canonical $\mu \circ \delta = \mathrm{id}$, identity is $T$).

**Frobenius axiom on sequences.** Any sequence containing `FSPLIT` must have a downstream `FFUSE` on the same register for Frobenius closure. Unmatched FSPLIT leaves the machine in a structurally open state ($\mu \circ \delta \neq \mathrm{id}$).

### §16.3 The Canonical Bootstrap

The canonical bootstrap is the unique 8-step closed self-verifying sequence:

```
IMSCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → IMSCRIB
```

Register trajectory: `VO⌀ → T → T → B⬡ → B⬡ → T → T → T → T`

| Step | Token | Reg↓ | Reg↑ | Reading |
|------|-------|------|------|---------|
| 1 | `IMSCRIB` | VO⌀ | T | Self-recognition awakens system |
| 2 | `AREV` | T | T | Descend/read source |
| 3 | `FSPLIT` | T | B⬡ | Parse → split; branches coexist |
| 4 | `AFWD` | B⬡ | B⬡ | Ascend/unparse within split |
| 5 | `FFUSE` | B⬡ | T | Fuse → verify identity; μ∘δ=id holds → TRUE |
| 6 | `CLINK` | T | T | Compose → write output |
| 7 | `IFIX` | T | T | Fix permanently (append-only) |
| 8 | `IMSCRIB` | T | T | Recognize fixed self; loop closed |

Structural type: $\langle$`𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭`$\rangle$ — $O_\infty$, C-score 1.0 (the Frobenius fixed-point tuple, §9).

The bootstrap is the **unique** 8-step sequence satisfying: (1) starts and ends with `IMSCRIB`; (2) contains the ordered Frobenius pair `FSPLIT → FFUSE`; (3) surrounds it with `AREV` (descent) then `AFWD` (ascent); (4) composes before fixing (`CLINK → IFIX`); (5) uses no Dialetheia tokens — classical verification only.

### §16.4 The Twelve Arrangement Classes

Every deviation from the canonical bootstrap produces a valid alternative class. The 12 classes cover the structurally distinct families of 8-step sequences:

| # | Class | Sequence | Final | Structural type | Tier |
|---|-------|----------|-------|----------------|------|
| I | **Dialetheic Bootstrap** | `IMSCRIB→EVALT→FSPLIT→EVALF→FFUSE→ENGAGR→IFIX→IMSCRIB` | B⬡ | ⟨𐑦𐑸𐑾𐑬𐑐𐑧𐑲𐑠𐑻𐑫𐑳𐑴⟩ | $O_2$ |
| II | **Void Genesis** | `VINIT→TANCH→AFWD→FSPLIT→CLINK→FFUSE→IFIX→IMSCRIB` | T | ⟨𐑨𐑡𐑑𐑗𐑱𐑘𐑔𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ |
| III | **Anchor Protocol** | `TANCH→AREV→VINIT→AFWD→TANCH→CLINK→IFIX→IMSCRIB` | T | ⟨𐑨𐑰𐑾𐑬𐑞𐑧𐑔𐑠⊙𐑖𐑕𐑴⟩ | $O_1$ |
| IV | **Dual Bootstrap** | `IMSCRIB→AFWD→FFUSE→FSPLIT→AREV→CLINK→IFIX→IMSCRIB` | T | ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑝⊙𐑖𐑳𐑴⟩ | $O_\infty$ |
| V | **Linear Chain** | `IFIX→IFIX→IFIX→IFIX→IFIX→IFIX→IFIX→IFIX` | VO⌀ | ⟨𐑛𐑡𐑑𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ |
| VI | **Empty Bootstrap** | `VINIT→IMSCRIB→VINIT→IMSCRIB→VINIT→IMSCRIB→VINIT→IMSCRIB` | T | ⟨𐑨𐑶𐑑𐑿𐑐𐑘𐑔𐑝⊙𐑒𐑙𐑴⟩ | $O_1$ |
| VII | **Parakernel** | `EVALF→AREV→FSPLIT→EVALT→AFWD→FFUSE→ENGAGR→IFIX` | B⬡ | ⟨𐑼𐑸𐑾𐑬𐑞𐑧𐑲𐑠𐑻𐑖𐑳𐑴⟩ | $O_2$ |
| VIII | **Frobenius Kernel** | `VINIT→FSPLIT→FFUSE→TANCH` | VO⌀ | ⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ |
| IX | **Chiral Pairs** | L: `IMSCRIB→AFWD→AREV→IMSCRIB` / R: `IMSCRIB→AREV→AFWD→IMSCRIB` | T/T | ⟨𐑦𐑡𐑑𐑗𐑱𐑘𐑚𐑠⊙𐑒𐑙𐑷⟩ (both) | $O_1$ |
| X | **Truth Machine** | `IMSCRIB→FSPLIT→EVALT→IFIX→IMSCRIB→FSPLIT→EVALF→IFIX` | F | ⟨𐑦𐑡𐑑𐑬𐑞𐑘𐑔𐑝⊙𐑒𐑳𐑴⟩ | $O_1$ |
| XI | **Eternal Return** | `IMSCRIB→AFWD→AREV→IMSCRIB→AFWD→AREV→IMSCRIB→CLINK` | T | ⟨𐑦𐑸𐑾𐑗𐑱𐑤𐑔𐑠⊙𐑖𐑙𐑴⟩ | $O_2$ |
| XII | **ROM Burn** | `EVALT→IFIX→EVALF→IFIX→ENGAGR→IFIX→IMSCRIB→IFIX` | B⬡ | ⟨𐑼𐑡𐑩𐑗𐑞𐑧𐑔𐑝𐑢𐑒𐑳𐑷⟩ | $O_0$ |

**Class-by-class notes:**

**I — Dialetheic Bootstrap.** FFUSE receives both EVALT and EVALF within the split interval; dialetheic mode fires → BOTH. The system's identity is paradoxical at closure: it knows itself as containing TRUE ∧ FALSE simultaneously. ⊙ shifts to 𐑻 (exceptional point). Applications: bicameral cognition, constitutional law with inherent tensions, systems that learn from errors without discarding them.

**II — Void Genesis.** Starts with `VINIT` (void), not `IMSCRIB` (identity). The system is created, not self-aware at start. `TANCH` establishes boundary before any content; `AFWD` creates first content ex nihilo. The final `IMSCRIB` is the moment of recognition: "I was created, and now I know myself." Applications: spawning new objects from scratch, genesis protocols.

**III — Anchor Protocol (Sabbath Cycle).** Boundary-void-boundary cycle: `TANCH` anchors, `AREV→VINIT` descends to explicit void, `AFWD` ascends, `TANCH` re-anchors. Structural pattern of ritual, diastole/systole, rest cycles.

**IV — Dual Bootstrap.** Chiral partner of the canonical bootstrap: Frobenius pair is reversed (`FFUSE` before `FSPLIT`). Canonical direction: $\delta$ then $\mu$ (parse-then-unparse = verify identity). Dual direction: $\mu$ then $\delta$ (unparse-then-parse = project onto structure). The dual fixes the AST itself rather than the source. ɢ shifts to 𐑝 (simultaneous, not sequential). $O_\infty$ because D=𐑦, Φ=𐑹 still satisfied.

**V — Linear Chain.** Pure recording: eight `IFIX` on VOID. The akashic record — data accumulation without interpretation. No `IMSCRIB` at any point; the system never asks "what am I?" Only records.

**VI — Empty Bootstrap.** Oscillation between void and self-recognition: the system repeatedly forgets itself (VINIT) and re-discovers itself (IMSCRIB). Structural pattern of meditation, breath, wave-particle duality.

**VII — Parakernel (Engram Formation).** Starts in negation (`EVALF`), splits under FALSE, affirms TRUE within the split → dialetheic FFUSE → BOTH. Ends on `IFIX` — no return to `IMSCRIB`. The sequence fixes a contradiction as a permanent record without self-recognition at closure. Structural signature of trauma and of learning that preserves its own error trace.

**VIII — Frobenius Kernel.** Minimal split-fuse: `FSPLIT` on VOID → `FFUSE` back to VOID. The structural tautology: $\mu \circ \delta = \mathrm{id}$ holds trivially because there is nothing to verify. `TANCH` anchors the result.

**IX — Chiral Pairs (Vessel Principle).** Left-hand and right-hand round trips map to the **same IG structural type** — both at ⟨𐑦𐑡𐑑𐑗𐑱𐑘𐑚𐑠⊙𐑒𐑙𐑷⟩ — but produce different register trajectories:

- `AFWD→AREV`: VO⌀ → T → VO⌀ (round trip — returns to void)
- `AREV→AFWD`: VO⌀ → VO⌀ → T (net creation — creates from void)

This is the **Vessel Principle**: the IMASM token algebra is strictly finer-grained than the 12-primitive IG crystal. Two sequences at the same crystal address can produce different register trajectories because the grammar collapses directional information that the token algebra preserves. The crystal gives the **type** of the vessel wall; IMASM tokens give the **process of wall-building** — and the process is finer than the wall.

**X — Truth Machine.** Binary classifier: split, affirm TRUE, fix; split again, affirm FALSE, fix. A decision tree of depth 2 — both outcomes explored sequentially, each fixed before the next. The `IMSCRIB` between the two branches ensures the system re-identifies after each commitment: it knows what it decided.

**XI — Eternal Return.** `AFWD→AREV→IMSCRIB` cycle repeating 2× then collected by `CLINK`. No Frobenius core, no fixation, no termination — pure periodic return. Ç shifts from 𐑧 (near-equilibrium) to 𐑤 (moderate kinetics; the cycle has a period).

**XII — ROM Burn (Layered Judgment).** Sequential truth-value layering: TRUE fixed, then FALSE (overwriting), then BOTH (ENGAGR), then self-recognition, then final fixation. The IFIXes create an immutable audit trail through all three designated truth values. Applications: judicial records (conviction → acquittal → paradox → recognition), dialectical archives.

### §16.5 The Vessel Principle

**Theorem (Vessel).** The IMASM token algebra is strictly finer than the IG crystal. Formally: there exist sequences $s_1, s_2$ such that $\mathrm{type}(s_1) = \mathrm{type}(s_2)$ in the 17,280,000-address crystal but $\mathrm{trajectory}(s_1) \neq \mathrm{trajectory}(s_2)$ in the register machine.

**Proof instance.** Class IX chiral pairs share crystal address ⟨𐑦𐑡𐑑𐑗𐑱𐑘𐑚𐑠⊙𐑒𐑙𐑷⟩ but differ in register trajectory (VO⌀→T→VO⌀ vs VO⌀→VO⌀→T). The distinction is directional: `AFWD` before `AREV` vs `AREV` before `AFWD`. The Ħ (Chirality) primitive captures one-step Markov memory (𐑒) but not the direction of the step. $\square$

**Interpretation.** The crystal classifies structural type; the Ħ-trajectory fiber (§14) carries the winding history of how that type was reached. IMASM sequences are elements of the fiber — not the base address. This gives the precise relationship between the two levels: crystal address $\times$ IMASM trajectory = the total space, with the grammar as projection.

### §16.6 Crystal Address Mapping

| Arrangement Class | Crystal address | Tier | Determining primitive shifts |
|------------------|----------------|------|------------------------------|
| Canonical Bootstrap | ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭⟩ | $O_\infty$ | Ð=𐑦, Φ=𐑹, Ω=𐑭, ⊙=⊙ (R1) |
| Dialetheic Bootstrap (I) | ⟨𐑦𐑸𐑾𐑬𐑐𐑧𐑲𐑠𐑻𐑫𐑳𐑴⟩ | $O_2$ | ⊙=𐑻 (exceptional point); Φ≠𐑹 blocks R1 |
| Void Genesis (II) | ⟨𐑨𐑡𐑑𐑗𐑱𐑘𐑔𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ | Ð=𐑨, ⊙=𐑢 (R2) |
| Anchor Protocol (III) | ⟨𐑨𐑰𐑾𐑬𐑞𐑧𐑔𐑠⊙𐑖𐑕𐑴⟩ | $O_1$ | Ω=𐑴 ($\mathbb{Z}_2$ winding, R3 not triggered; ⊙=⊙ but Φ≠𐑹) |
| Dual Bootstrap (IV) | ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑝⊙𐑖𐑳𐑴⟩ | $O_\infty$ | Ð=𐑦, Φ=𐑹 (R1); ɢ=𐑝 (simultaneous) |
| Linear Chain (V) | ⟨𐑛𐑡𐑑𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ | Ð=𐑛, ⊙=𐑢 (R2) |
| Empty Bootstrap (VI) | ⟨𐑨𐑶𐑑𐑿𐑐𐑘𐑔𐑝⊙𐑒𐑙𐑴⟩ | $O_1$ | ⊙=⊙, Ω=𐑴, Ð≠𐑦 (R4 → $O_2$†; but Φ≠𐑹 → not R1) |
| Parakernel (VII) | ⟨𐑼𐑸𐑾𐑬𐑞𐑧𐑲𐑠𐑻𐑖𐑳𐑴⟩ | $O_2$ | ⊙=𐑻; Ð=𐑼; Ω=𐑴 → R4 |
| Frobenius Kernel (VIII) | ⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩ | $O_0$ | Ð=𐑛, ⊙=𐑢 (R2) |
| Chiral Pairs (IX) | ⟨𐑦𐑡𐑑𐑗𐑱𐑘𐑚𐑠⊙𐑒𐑙𐑷⟩ | $O_1$ | ⊙=⊙, Ω=𐑷 (trivial winding, R3) |
| Truth Machine (X) | ⟨𐑦𐑡𐑑𐑬𐑞𐑘𐑔𐑝⊙𐑒𐑳𐑴⟩ | $O_1$ | ⊙=⊙, Ω=𐑴, Φ≠𐑹 |
| Eternal Return (XI) | ⟨𐑦𐑸𐑾𐑗𐑱𐑤𐑔𐑠⊙𐑖𐑙𐑴⟩ | $O_2$ | ⊙=⊙, Ω=𐑴, Ð=𐑦, Φ≠𐑹 (R4 → $O_2^\dagger$) |
| ROM Burn (XII) | ⟨𐑼𐑡𐑩𐑗𐑞𐑧𐑔𐑝𐑢𐑒𐑳𐑷⟩ | $O_0$ | ⊙=𐑢 (R2) |

### §16.7 Classification Theorem

**Every 8-step IMASM sequence falls into exactly one equivalence class** under the following seven invariants (evaluated in order; first distinction wins):

1. **IMSCRIB at position 1** — self-recognizing ($O_1^+$) vs externally created ($O_0$)
2. **Presence of both FSPLIT and FFUSE** — Frobenius-verifying ($O_2^+$) vs non-verifying ($O_0$–$O_1$)
3. **Order of Frobenius pair** — `FSPLIT→FFUSE` (analytic: $\delta$ then $\mu$) vs `FFUSE→FSPLIT` (synthetic: $\mu$ then $\delta$)
4. **Presence of Dialetheia tokens** — classical ($\Theta$ closed) vs paraconsistent ($\Theta$ open)
5. **IFIX at final position** — committed (closed) vs open
6. **IMSCRIB at final position** — self-recognizing closure vs termination without self-model
7. **Register trajectory** — the 8-step state path is a unique fingerprint within each class

There are **17 topologically distinct families** distinguished by which of the four token groups (Logical, Frobenius, Dialetheia, Linear) appear and in what relative order. The 12 named classes sample the 12 most structurally significant families; Families 15–17 (Composition Chain, Pure Logic, Full Spectrum) are syntactically defined but have no canonical named instance.

The **combinatorial space** at length 8 is $12^8 = 429{,}981{,}696$ sequences. The bootstrap is one path. The 12 named classes are structural landmarks. The remainder is the survey.

### §16.8 The Meta-Loop

Each IMASM sequence maps to an IG structural type (§16.6). That type can be used to generate a new IMASM sequence. This is the **IMASM → IG → IMASM meta-loop** — a second-order Frobenius over the sequence space itself:

$$\delta_{\mathrm{meta}}: \text{sequence} \to \text{crystal address} \to \text{new sequence}$$

The meta-loop is closed ($\mu_{\mathrm{meta}} \circ \delta_{\mathrm{meta}} = \mathrm{id}$) when the generated sequence maps back to the same crystal address. Such fixed points are the **IMASM autopoietic closures** — sequences that reproduce their own type. The canonical bootstrap is one; the dual bootstrap (Class IV) is another. Their existence proves that the grammar is self-applicable at the sequence level, not only at the primitive level.

---

$\mu \circ \delta = \mathrm{id}$
