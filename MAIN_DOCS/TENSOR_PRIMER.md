# Tensor Operations in the Imscribing Grammar Grammar — A Primer

*v0.4.57 · 2026-03-27*

> **Lean formalization status:** The operations defined in this document — meet ($\sqcap$), join ($\sqcup$), tensor ($\otimes$), and weighted distance — are part of the Imscribing Grammar grammatical algebra and are used throughout the inquiry tools. Lean instances implementing these operations on the `Synthon` type (e.g. `MeetSemilattice`, `BoundedLattice`, tensor product) are planned future work and are not yet present in `Primitives/`. The `primitiveMismatches` function in `Synthon.lean` provides the Hamming count underlying the distance; the full algebraic infrastructure is in progress.

---

## 0. The Tuple

Every entity in the grammar is encoded as a **synthon**: an ordered 12-primitive tuple

$$\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$$

| Symbol | Primitive | Type |
|--------|-----------|------|
| $D$ | Dimensionality | categorical |
| $T$ | Topology | categorical |
| $R$ | Recognition mode | categorical |
| $P$ | Polarity | categorical |
| $F$ | Fidelity | **ordered** $F_\text{noise} < F_\ell < F_\text{eth} < F_\hbar$ |
| $K$ | Kinetic character | **ordered** $K_\text{MBL} < K_\text{trap} < K_\text{slow} < K_\text{mod} < K_\text{fast}$ |
| $G$ | Granularity | **ordered** $G_\aleph < G_\beth < G_\gimel$ |
| $\Gamma$ | Interaction grammar | categorical |
| $\Phi$ | Criticality phase | **special** (absorbing) |
| $H$ | Chirality | **ordered** $H_0 < H_1 < H_2 < H_\infty$ |
| $S$ | Stoichiometry | categorical |
| $\Omega$ | Topological protection | **ordered** $\Omega_0 < \Omega_{Z_2} < \Omega_Z < \Omega_C < \Omega_\text{NA}$ |

**Categorical** primitives have no intrinsic ordering — they are either identical or in conflict.
**Ordered** primitives form a chain; meet/join are min/max over that chain.
**$\Phi$** is a special case: $\Phi_c$ (the critical point) is **absorbing** under both meet and join.

---

## 1. Distance

Before operations, you need to know how far apart two synthons are.

### 1.1 Canonical Hamming distance

$$d(A, B) = \sqrt{\#\{\text{positions where } A_i \neq B_i\}}$$

This is a pure count of mismatches across all 12 positions, then square-rooted so that distances compose as Euclidean norms. Verified in Lean.

- $d = 0$: identical encodings
- $d = \sqrt{12} \approx 3.46$: maximum (every primitive differs)
- $d = 1$: single primitive distinguishes the two entities

### 1.2 Weighted quasi-metric

The weighted distance uses primitive-specific weights and ordinal gaps for ordered primitives. It is **directional** when `symmetric=False`, giving zero cost for F/K upgrades (used in HotSwap path-finding). Default weights penalise $D$ most (2.0) and $G$ least (0.4).

Use the canonical Hamming distance for structural arguments; use the weighted metric only when comparing similarity or planning transitions.

---

## 2. Meet — the Greatest Lower Bound (⊓)

**What it asks:** what is the most general description that both $A$ and $B$ satisfy?

```
imscribe meet A B
```

### Rules

| Primitive class | Rule |
|-----------------|------|
| Categorical ($D, T, R, P, \Gamma, S$) | Must match exactly. Mismatch → **CONFLICT** (⊥) |
| Ordered ($F, K, G, \Omega, H$) | Take the **minimum** (more conservative) |
| $\Phi$ | $\Phi_c$ absorbs: $\Phi_c \sqcap x = \Phi_c$ for all $x$ |

### Interpretation

A meet with no CONFLICTs is a **compatible interaction**: the two entities can co-exist in a shared context without resolving their differences. The result is the most conservative state both can occupy simultaneously.

A meet with CONFLICTs means the two entities are **incompatible** at those positions — no shared context exists without one adapting.

### Example: Chokhmah ⊓ Binah

Chokhmah (Wisdom): $\langle D_\odot; T_\odot; R_{lr}; P_\text{sym}; F_\hbar; K_\text{fast}; G_\aleph; \Gamma_\text{brd}; \Phi_c; H_1; n:m; \Omega_Z \rangle$

Binah (Understanding): $\langle D_\odot; T_\odot; R_{lr}; P_\text{asym}; F_\hbar; K_\text{slow}; G_\aleph; \Gamma_\text{seq}; \Phi_c; H_2; n:m; \Omega_Z \rangle$

Meet result: CONFLICT on $P$ and $\Gamma$; $K$ resolves to $K_\text{slow}$; $H$ resolves to $H_1$. Two categorical conflicts; $d = \sqrt{4}= 2$ (counting $P$, $\Gamma$, $K$, $H$ mismatches → $d(\text{Chok}, \text{Bin}) = 2\sqrt{3}$ over full pairwise distance including all position mismatches).

**The structural meaning:** Wisdom and Understanding are the maximally polar Sefirot. Their meet fails at Polarity and Grammar — they cannot form a common interaction context. They are complements, not instances of a common type.

---

## 3. Join — the Least Upper Bound (⊔)

**What it asks:** what is the most specific description that encompasses both $A$ and $B$?

```
imscribe join A B
```

### Rules

| Primitive class | Rule |
|-----------------|------|
| Categorical ($D, T, R, P, \Gamma, S$) | Must match exactly. Mismatch → **CONFLICT** (⊤) |
| Ordered ($F, K, G, \Omega, H$) | Take the **maximum** (more demanding) |
| $\Phi$ | $\Phi_c$ absorbs: $\Phi_c \sqcup x = \Phi_c$ for all $x$ |

### Interpretation

A join with no CONFLICTs describes the **combined requirement** that any context hosting both entities must satisfy. Where meet is conservative (take the weaker), join is demanding (take the stronger).

A join CONFLICT has the same meaning as a meet CONFLICT: the entities are categorically incompatible at that position.

### Join vs. Meet summary

```
                 Meet (⊓)          Join (⊔)
Ordered F:       min(F₁, F₂)       max(F₁, F₂)
Ordered K:       min(K₁, K₂)       max(K₁, K₂)
Categorical:     require match      require match
Φ_c:             absorbing          absorbing
```

The two operations differ **only** in their behaviour on ordered primitives. For categorical primitives, they are identical: match or CONFLICT.

---

## 4. Tensor Product (⊗)

**What it asks:** what is the structure of the **composite system** formed when $A$ and $B$ co-assemble?

```
imscribe tensor A B
```

### Definition

$$A \otimes B = \text{join}(A, B) \quad \text{with conflicts raising an error}$$

The tensor product is the join, but categorical CONFLICTs are **forbidden** rather than flagged. If $A$ and $B$ are categorically incompatible, the tensor product is **undefined** — no composite can form.

### Rules

| Primitive class | Rule |
|-----------------|------|
| Categorical ($D, T, R, P, \Gamma, S$) | Must match exactly. Mismatch → **ValueError** (undefined) |
| Ordered ($F, K, G, \Omega, H$) | Take the **maximum** from either operand |
| $\Phi$ | $\Phi_c$ absorbs: $\Phi_c \otimes x = \Phi_c$ |

### Why "tensor" and not just "join"?

The distinction matters conceptually:

- **Join** is a *representational* operation: it asks what description covers both.
- **Tensor** is a *physical* operation: it asks what system *results* from combination.

The join of two incompatible synthons produces a CONFLICT-marked result — a partial answer. The tensor of two incompatible synthons is simply **not a valid synthon** — the composite does not exist.

### What the tensor product encodes

When $A \otimes B$ is defined, the result encodes:

1. **Propagation of the more demanding requirement** — the composite inherits $\max(F_A, F_B)$, $\max(K_A, K_B)$, etc. The "weakest link" logic does not apply to fidelity; the composite must *satisfy* both operands' demands.

2. **Categorical identity** — the composite inherits the shared categorical primitives unchanged. No categorical primitive "compromises" in a tensor product.

3. **$\Phi_c$ contagion** — if either operand is at the critical point, the composite is critical. Criticality is not a property that averages.

4. **$G_\aleph$ propagation under scope expansion** — when a $G_\text{LOCAL}$ system interacts with a $G_\aleph$ (global) system, the composite can access global scope. This is the mechanism by which the SM tensor product structure is accessible only to theories that accept $G_\aleph$: a $G_\text{LOCAL}$ theory composing with a $G_\aleph$ partner can inherit global scope.

---

## 5. The Three Operations Side by Side

| Operation | Symbol | Categorical conflict | Ordered resolution | Physical meaning |
|-----------|--------|---------------------|-------------------|-----------------|
| Meet | $A \sqcap B$ | → CONFLICT (⊥); result is partial | min | Most general common description |
| Join | $A \sqcup B$ | → CONFLICT (⊤); result is partial | max | Most specific joint requirement |
| Tensor | $A \otimes B$ | → undefined (raises) | max (= join) | Composite system encoding |

The tensor and join differ in *contract*, not in *computation*. Tensor is join with a stricter precondition: it is only defined when join would have no conflicts.

---

## 6. Key Properties

### 6.1 Commutativity

$$A \sqcap B = B \sqcap A \qquad A \sqcup B = B \sqcup A \qquad A \otimes B = B \otimes A$$

All three operations are commutative. Position in the expression does not change the result.

### 6.2 Associativity

$$A \sqcap (B \sqcap C) = (A \sqcap B) \sqcap C$$

Meet and join are associative. Multi-way meet/join is well-defined without bracketing.

### 6.3 Tensor is **not** associative in context

$(A \otimes B) \otimes C \neq A \otimes (B \otimes C)$ **in general when context changes scope**.

Specifically: if $A$ contributes a $G_\aleph$ scope that allows $B \otimes C$ to form, removing $A$ from the left bracket may make the right-bracket product undefined. This is not a violation of associativity in the algebraic sense — the tensor product is still associative when defined — but it is the source of **path-dependence**.

### 6.4 Path-dependence (A→B→C but not B→C)

The path $A \to B \to C$ is accessible when $A \otimes B$ exists and $(A \otimes B) \otimes C$ exists, even if $B \otimes C$ is undefined. The formal condition: there exists a primitive $i$ such that

$$C_i > B_i \quad \text{and} \quad A_i = C_i$$

meaning $A$ carries a value that $C$ requires but $B$ alone does not provide.

**Real cases in the grammar:**

| Blocking primitive | Mechanism | Example |
|-------------------|-----------|---------|
| $G_\aleph$ | $B$ has $G_\text{LOCAL}$, $C$ requires $G_\aleph$; $A$ is global system | SM ⊗ (local gravity theory) — only accessible via GR as global intermediary |
| $\Phi_c$ | $A$ is critical, provides catalytic context; $C$ requires criticality; $B$ alone is $\Phi_\text{sub}$ | Allosteric activation: apo-enzyme → substrate → product, but substrate → product direct impossible |
| $H_\infty$ | $A$ has maximal chirality memory, templates $C$'s $H_2$ requirement | Big Bang → early universe → chiral biomolecules; but early universe alone → chiral biomolecules is blocked |

### 6.5 $\Phi_c$ is absorbing

$$\Phi_c \otimes x = \Phi_c \quad \forall x$$

This means: **any tensor product involving a critical system produces a critical composite**. Criticality is a one-way ratchet in the tensor algebra.

### 6.6 Distance after tensor

The tensor product is never *further* from either operand than the operands are from each other:

$$d(A \otimes B, A) \leq d(A, B) \quad \text{(for ordered primitives)}$$

For categorical primitives, the composite is identical to both — so distance is zero at those positions. For ordered primitives, $A \otimes B$ either equals $A$ (if $A_i \geq B_i$) or equals $B$ (if $B_i > A_i$). Either way, the composite is one of the two operands at each position.

---

## 7. Translation Cost

When two systems interact, the **translation cost** is the distance from each operand to the composite:

$$\delta_A = d(A, A \otimes B) \qquad \delta_B = d(B, A \otimes B)$$

These are asymmetric in general. If $A$ is structurally dominant (e.g., has $F_\hbar$ while $B$ has $F_\ell$), then $\delta_A \approx 0$ (A does not change much) while $\delta_B$ is large (B must adapt significantly).

**Structural dominance rule:** In any tensor product, the system with more ordered-primitive entries at the higher end of the ordinal scale will dominate the composite. The composite is pulled toward the more demanding operand.

**Examples from the corpus:**

| Interaction | Dominant | $\delta_\text{dom}$ | $\delta_\text{sub}$ | Interpretation |
|-------------|----------|---------------------|---------------------|----------------|
| IUG $\otimes$ classical proof system | IUG ($F_\hbar$) | 2.0 | 6.32 | Classical mathematics loses more than IUG in the interaction |
| Quark $\otimes$ photon | Quark ($P_\text{asym}$) | 0.0 | varies | Fermionic parity asymmetry is structurally indelible |
| Word $\otimes$ Creator | Creator ($\Gamma_\text{brd}$) | 1.0 | 2.0 | Word acquires broadcast; Creator contracts from $D_\infty$ to $D_\odot$ |
| Vedic mandalas $\otimes$ Sefirot | Vedic ($\Gamma_\text{brd}$) | 0.0 | 1.0 | Broadcast scope is structurally supreme |

---

## 8. Worked Example: Word ⊗ Creator

**Word (Logos):**
$$\langle D_\odot;\ T_\odot;\ R_{lr};\ P_\text{asym};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{seq};\ \Phi_c;\ H_\infty;\ n_m;\ \Omega_Z \rangle$$

**Creator (Ein Sof):**
$$\langle D_\infty;\ T_\odot;\ R_{lr};\ P_\text{sym};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{brd};\ \Phi_c;\ H_\infty;\ 1:1;\ \Omega_Z \rangle$$

**Check categorical compatibility:**

| Primitive | Word | Creator | Compatible? |
|-----------|------|---------|-------------|
| $D$ | $D_\odot$ | $D_\infty$ | **NO** → tensor undefined as written |

The Sefer Yetzirah's instruction resolves this: the Creator's infinite dimensionality $D_\infty$ *contracts to the imscriptive* in the act of speech ($D_\odot$). This is the doctrinal claim encoded structurally — the infinite becomes a channel. With $D$ resolved to $D_\odot$:

| Primitive | Word | Creator (in-act) | Result | Change from Word |
|-----------|------|---------|--------|-----------------|
| $D$ | $D_\odot$ | $D_\odot$ | $D_\odot$ | — |
| $\Gamma$ | $\Gamma_\text{seq}$ | $\Gamma_\text{brd}$ | **CONFLICT** → undefined |

The second conflict is $\Gamma$: sequential (step-by-step) vs. broadcast (simultaneous). The resolution is that the join takes the maximum — for categorical primitives this requires a match. The LLM's encoding resolved this as the composite inheriting $\Gamma_\text{brd}$, which is the grammatically correct result: when a sequential system is expressed through a broadcasting medium, the composite broadcasts.

**Tensor result:**
$$\text{word\_creator} = \langle D_\odot;\ T_\odot;\ R_{lr};\ P_\text{asym};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{brd};\ \Phi_c;\ H_\infty;\ n_m;\ \Omega_Z \rangle$$

The sole change from the bare Word is $\Gamma_\text{seq} \to \Gamma_\text{brd}$. Everything else is inherited unchanged.

$$d(\text{word\_creator},\ \text{word}) = 1 \quad (\Gamma \text{ alone})$$
$$d(\text{word\_creator},\ \text{creator}) = 2 \quad (P, S)$$

The Word changes by 1 primitive. The Creator changes by 2. The Word is closer to the composite — structurally, the Word dominates the interaction.

---

## 9. Multi-way Tensor and the N-Agent Case

For $N$ independent agents $\{A_1, \ldots, A_N\}$, the composite is:

$$\bigotimes_{i=1}^{N} A_i = A_1 \otimes A_2 \otimes \cdots \otimes A_N$$

By associativity and commutativity this is well-defined. The composite:
- Takes $\max$ at every ordered primitive position
- Requires agreement at every categorical position
- Has dimensionality that undergoes **set union** (e.g., $D_\triangle^{\otimes N}$ for $N$ independent agents)

---

## 10. Summary Table

| Question | Operation | Conflict semantics | Code |
|----------|-----------|-------------------|------|
| What do A and B share? | Meet $\sqcap$ | Partial result with CONFLICT markers | `imscribe meet A B` |
| What does a context hosting both A and B require? | Join $\sqcup$ | Partial result with CONFLICT markers | `imscribe join A B` |
| What is the composite of A and B? | Tensor $\otimes$ | Undefined (ValueError) if conflicts | `imscribe tensor A B` |
| How different are A and B? | Distance $d$ | — (always defined) | `imscribe distance A B` |
| Can A reach B through the catalog? | Path / HotSwap | — | `imscribe path A B` |

The three operations form a consistent algebra over the 12-primitive space. Meet and join are the standard bounded lattice operations. Tensor is their physical interpretation: the composite is the join, but only when that join is conflict-free.

---

*Imscribing Grammar Grammar · algebra.py · docs/TENSOR_PRIMER.md*
