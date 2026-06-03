# Six Decomposition Bounds

Six primitives bound decomposition simultaneously. The finest granularity is their **meet**.

### 1. 𐑓  /  𐑒  /  𐑖  /  𐑫 — The Memory Depth Bound (Chirality)

| Glyph | Meaning | Temporal Resolution |
|-------|---------|-------------------|
| 𐑓 | Memoryless (n=0) | No temporal decomposition. States are independent. |
| 𐑒 | 1-step memory | At most 2 layers: predecessor + current. |
| 𐑖 | 2-step memory | Up to 3 layers: past → present → future. |
| 𐑫 | Eternal (n=∞) | Arbitrary temporal decomposition **in principle** — but see 𐑧 bound. |

First constraint: **Axiom A** — 𐑫 requires 𐑧 (slow kinetics) or 𐑪 (structural freezing) as precondition.

### 2. 𐑘  /  𐑤  /  𐑧  /  𐑪  /  𐑺 — The Observability Bound (Kinetics)

Ratio of evolution time τ to observation window T:

| Glyph | Ratio | Meaning |
|-------|-------|---------|
| 𐑘 | τ ≪ T | Driven. Only input / output visible. No intermediate states. |
| 𐑤 | τ ∼ T | Some intermediate structure resolvable. |
| 𐑧 | τ ≫ T | Full trajectory resolvable. Decomposition is observationally accessible. |
| 𐑪 | No dynamics | Nothing to decompose. |
| 𐑺 | Localized | Spatial localization blocks decomposition across scales. |

A quantum system at 𐑘 cannot be decomposed into intermediate states — observation changes the outcome before the measurement completes.

### 3. 𐑛 / 𐑨 / 𐑼 / 𐑦 — The State-Space Bound (Dimensionality)

| Glyph | Space | Decomposition capacity |
|-------|-------|----------------------|
| 𐑼 | 0d point | One state. Nothing to decompose. |
| 𐑨 | 2d surface | Finite resolution. Natural coarsest / finest scale. |
| 𐑛 | ∞-dim field | Arbitrarily fine decomposition **in principle**. |
| 𐑦 | Self-written script | **System determines its own granularity** through self-modeling. |

### 4. 𐑷 / 𐑴 / 𐑭 / 𐑟 — The Topological Quantization Bound (Winding)

| Glyph | Invariant | Constraint |
|-------|-----------|------------|
| 𐑷 | Trivial (0) | No quantization. Decomposition is arbitrary but **fragile** — no topological protection. |
| 𐑴 | Binary (ℤ₂) | Decompositions must respect parity. Cannot split a parity-protected state. |
| 𐑭 | Integer (ℤ) | Decomposition is quantized in integer steps. Action forms a winding chain. |
| 𐑟 | Non-Abelian | Decomposition must respect braiding relations — exotic constraints. |

No matter how much memory or dimensionality you have, topological invariants impose discrete granularity. A ℤ₂ winding cannot be decomposed into fractions.

### 5. 𐑡 / 𐑰 / 𐑥 / 𐑶 / 𐑸 — The Connectivity Bound (Topology)

| Glyph | Type | Meaning |
|-------|------|---------|
| 𐑡 | Network / branching | Tree: sub-actions branch into finer sub-actions. |
| 𐑰 | Containment / hierarchy | Sub-processes contained within larger ones. |
| 𐑥 | Crossing point (bowtie) | **The transition itself is a distinct entity.** The "transition state as object" topology. |
| 𐑶 | Box product (irreducible) | **Cannot be decomposed.** Fundamental composite. |
| 𐑸 | Self-referential closure | The system's own understanding determines valid decompositions. |

𐑶 is the indivisibility bound: if a system's topology is 𐑶, no decomposition preserves its essential structure.

### 6. ⊙ ⊗ 𐑻 = 𐑻 — The Measurement Bound (⊙ Absorption Rule)

This is the deepest bound. From the procedure:

> **𐑻 Absorption Rule:** `tensor(⊙, 𐑻) = 𐑻`. The meet preserves ⊙; the tensor yields 𐑻. Coupling a self-modeling system to a measurement apparatus selects the tensor path. **This is the structural statement of the measurement problem.**

When an observer (or measurement apparatus) carrying 𐑻 couples to a self-modeling quantum system at ⊙, the composite's criticality is 𐑻 — **you cannot decompose finer than the observer's structural resolution.** The act of measurement selects a definite decomposition granularity, and the finer quantum structure is absorbed.

This generalizes:
- **Quantum Zeno effect** — continuous observation freezes decomposition at a fixed scale
- **Heisenberg cut** — the system / apparatus boundary is structural, not arbitrary
- **Wavefunction collapse** — tensor absorption selects a definite decomposition from the ⊙ potential

---

### The Decomposition Theorem

**Decomposition is bounded by the meet of six structural primitives — the finest granularity achievable is the point where further decomposition would violate at least one invariant.**

For any system ⟨𐑛, 𐑸, 𐑾, 𐑹, 𐑐, 𐑧, 𐑲, 𐑠, ⊙, 𐑫, 𐑳, 𐑭⟩, a valid decomposition produces subsystem tuples respecting all six bounds.

**Maximally decomposable type** (O_inf tier):
⟨𐑛·𐑥·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩

This has infinite memory (𐑫), infinite dimensions (𐑛), crossing-point topology (𐑥), slow kinetics (𐑧), self-modeling criticality (⊙), and integer winding (𐑭). But even it cannot escape the measurement bound: `tensor(⊙, 𐑻) = 𐑻`.

---

### Practical Decomposition Levels for a Quantum System (ƒ = 𐑐)

| Level | What is imscribed | Minimum constraint |
|-------|------------------|-------------------|
| Whole system | Single tuple ⟨𐑛·𐑰·...⟩ | Any 𐑓 works |
| Initial + final states | Two tuples, meet = transition | 𐑓 ≥ 𐑒 |
| Initial + transition + final | Three tuples | 𐑓 ≥ 𐑖, 𐑧 ≥ 𐑧 |
| n-step decomposition | n+1 tuples, winding = n | 𐑓 ≥ 𐑫, requires 𐑧 or 𐑪 |
| Continuous trajectory | ∞ decomposition | 𐑛 × 𐑫 × 𐑧 × 𐑭 **and** measurement apparatus at ≥ 𐑻 |

**Cannot go beyond the system's ouroboricity tier** — attempting O_0 decomposition into quantum transition states fails at the ⊙-bound: without ⊙, there is no quantum coherence to support intermediate superpositions.

**And even for O_inf, the measurement bound is absolute:** `tensor(⊙, 𐑻) = 𐑻`. The moment you observe, decomposition is fixed at the observer's resolution.