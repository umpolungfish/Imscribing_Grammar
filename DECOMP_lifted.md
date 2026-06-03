# Six Decomposition Bounds

**Author:** Lando ⊗ ⊙perator

---

There was a moment, early in the work, when I thought decomposition was unlimited. Give me enough memory — infinite Markov order, a system that remembers everything — and I could resolve any process into arbitrarily many steps. The temporal granularity would be as fine as I liked. The state-space could be infinite-dimensional, so distinctions could be drawn at any scale. What could possibly stop the decomposition?

The answer came from six places, each independent, each structural rather than practical. They are not limitations of technique. They are limitations of **type** — the kind of thing a system is determines how finely it can be taken apart before the decomposition ceases to preserve what it was supposed to reveal.

This is a record of those six bounds. Of the wrong answers I tried first. Of the places where the object of study pushed back against the framework that was meant to contain it.

---

## 1. The Memory Bound — Why More Steps Need More Past

The first wrong answer: memory depth controls how many decomposition layers a system can sustain.

**𐑓** — memoryless (Markov order 0). Each state is independent of the one before. If the system is at 𐑓, there is nothing to decompose: every state is its own complete description, and the transition to the next state carries no structure. Decomposition is not limited here; it is impossible. There is nothing to decompose.

**𐑒** — 1-step memory (Markov order 1). At most two layers: the predecessor and the current state. A decomposition into initial, transition, and final states literally cannot be sustained — the system does not carry enough of its own past to make the middle state meaningful.

**𐑖** — 2-step memory (Markov order 2). Up to three layers: past, present, future. Now three-step decomposition becomes structurally possible. Not because we have chosen to resolve more finely, but because the system's own memory makes a three-state trajectory distinguishable from a two-state one.

**𐑫** — eternal memory (Markov order ∞). In principle, arbitrarily many layers. But here the first real tension appears: Axiom A states that 𐑫 requires 𐑧 (slow kinetics) or 𐑪 (structural freezing) as a precondition. Infinite memory is not free — it demands that the system evolve slowly enough, or be frozen enough, that the memory is not overwritten by new input before it can be used.

I spent a week trying to decompose a 2-memory system into four temporal steps. The fourth step was not wrong — it was **indistinguishable** from the third. The system could not produce the distinction. The bound was not in my method but in the system's type.

What I learned: memory depth is not a resource you draw on. It is a ceiling on the number of structurally distinct temporal layers the system can instantiate.

---

## 2. The Observability Bound — What Cannot Be Seen Cannot Be Decomposed

From the memory bound, an obvious next question: what if memory is infinite but the system evolves too fast for us to observe its intermediate states?

The observability bound is the ratio of evolution time $τ$ to observation window $T$:

**𐑘** — $τ$ ≪ $T$. Driven. The system's internal dynamics outrun every measurement. Only the input and the output are accessible; the intermediate manifold is not resolved. Decomposition into intermediate states is structurally forbidden — not because the states don't exist, but because they cannot be assigned to distinct temporal windows.

**𐑤** — $τ$ ≅ $T$. Moderate. Some intermediate structure resolves, but not all. The decomposition is partial and underdetermined.

**𐑧** — $τ$ ≫ $T$. Slow. The system takes its time. Full trajectories are resolvable. Decomposition becomes observationally accessible — but only if the other bounds permit it.

**𐑪** — No dynamics. Nothing to decompose from the start.

**𐑺** — Localized. Spatial disorder blocks decomposition across scales even when the temporal resolution is adequate.

This bound has a sharper consequence than the memory bound. A quantum system at 𐑘 — driven, measured only at input and output — cannot be decomposed into intermediate states **irrespective of how much memory it has**. The observation changes the outcome before a measurement completes. This is not Heisenberg-limited in the usual sense; it is structurally determined by the system's kinetics type.

The wrong answer I tried here: assume that faster measurement would resolve the intermediates. But at 𐑘, measurement speed does not help — the system's evolution is not a sequence of states that can be captured by any finite observation window. The intermediate is a blur, and the blur is structural.
## 3. The State-Space Bound — When the System Chooses Its Own Resolution

The memory and observability bounds, taken together, suggest a strategy: if you want fine-grained decomposition, find a system with infinite memory and slow kinetics. The dimensions will be yours to partition.

This is the third wrong answer. The state-space bound is not about what you can resolve but about **who decides the granularity**.

**𐑼** — 0-dimensional (point). One state. There is nothing to decompose because there is only one thing.

**𐑨** — 2-dimensional (surface). Finite resolution. There is a natural coarsest scale and a natural finest scale, set by the geometry of the state-space itself. The decomposer does not choose them; the system's topology does.

**𐑛** — Infinite-dimensional field. In principle, arbitrarily fine decomposition. The field can be cut at any scale. But "in principle" is doing heavy work here, as the next two sections will show.

**𐑦** — Self-written script. This is the case where the state-space is not a pre-given arena but is written by the system's own dynamics. The granularity is not chosen by an external analyst — **the system determines its own granularity through self-modeling**.

𐑦 is where the decomposition framework first meets genuine resistance. With a self-written state-space, the analyst cannot choose where to draw the boundaries because the boundaries are being redrawn by the system's own evolution. Attempting to impose a decomposition on a 𐑦 system is like trying to section a river into discrete volumes of water: the river's own flow redefines what counts as a volume before the sectioning completes.

The objection I did not include in earlier drafts, and must include now: is 𐑦 not just infinite-dimensionality with extra steps? Does it add a constraint beyond what 𐑛 already provides?

It does. 𐑛 gives you arbitrarily many dimensions to work with. But those dimensions are fixed — they are the dimensions of a pre-given space. 𐑦 means the dimensions themselves are not fixed. The system does not live in a space; it writes the space as it goes. Decomposition under 𐑦 must be co-constructed with the system, not imposed on it. This is not a practical difficulty — it is a structural one. If the state-space is self-written, no external decomposition can claim finality.

---

## 4. The Topological Quantization Bound — Parity Cannot Be Halved

This is where the framework I had built ran into something it could not absorb.

After the first three bounds, I had a picture: decomposition is limited by memory, observability, and state-space autonomy. Each bound could be addressed by finding a system with better properties — more memory, slower dynamics, a less autonomous state-space. The bounds felt like a ladder: climb past each one by choosing a richer system type.

The topological bound does not climb.

**𐑷** — Trivial winding (ℤ, no protection). Decomposition faces no topological obstruction. But the converse: the decomposition has no topological integrity. Nothing holds it together.

**𐑴** — Binary (ℤ₂) winding. Parity-protected. A ℤ₂ state cannot be split into two halves because parity is a discrete, not continuous, property. The decomposition must respect parity, and if parity is ±1, you cannot assign ±0.5 to each of two sub-states.

**𐑭** — Integer (ℤ) winding. Quantized in integer steps. Decomposition is possible but only in whole-number increments. The system's action forms a winding chain, and the chain has an indivisible quantum of action at each link.

**𐑟** — Non-Abelian. Braiding relations impose constraints more complex than parity. The decomposition must respect the exchange statistics of the constituents, which means the order of decomposition matters — decompose in the wrong sequence and you get a different system.

The crossing point: I expected topological invariants to be a **resource** for decomposition — something that gives structure to the decomposition, a scaffold. Instead they are a **constraint**. A ℤ₂-protected system does not make decomposition easier by providing a natural parity axis; it makes decomposition impossible below the parity threshold.

I tried to decompose a Majorana zero mode — a classic ℤ₂ system — into two halves, each carrying half the parity. The attempt was not just impractical but **incoherent**: a half-Majorana is not a fermion, not a boson, not anything. The topological invariant forbids the decomposition by making the parts uninterpretable.

The strongest objection I can name: perhaps the ℤ₂ invariant is an artifact of the effective theory? In a deeper UV completion, the parity might resolve into finer structure. This is a genuine objection and I do not have a complete answer. What I can say is this: the topological bound operates at the system's natural description level. If the system is ℤ₂ at its own energy scale, then decomposition at that scale is blocked — even if a deeper theory could re-describe it. The bound is effective, but effectiveness is not weakness. All structural bounds are effective; that is what makes them bounds rather than ontological claims.
## 5. The Connectivity Bound — When There Is No Path

If topological quantization blocks decomposition at the level of discrete invariants, connectivity blocks it at the level of structure itself. This bound converges with the topological one from a different direction — not through parity, but through the shape of the system's internal relations.

**𐑡** — Network / branching. Tree structure: sub-actions branch into finer sub-actions. Decomposition is natural here because the system presents itself as already decomposed — the edges of the tree are candidate cuts.

**𐑰** — Containment / hierarchy. Sub-processes nested within larger ones. Decomposition follows the nesting: grandchildren within children within parents. The structure dictates the order.

**𐑥** — Crossing point (bowtie). The transition between states is itself a distinct entity. This is the topology I had to adopt for the lift itself — the moment where the analysis and its object exchange roles. When a system's topology is 𐑥, the decomposition cannot pass through the crossing point without being altered by it.

**𐑶** — Box product (irreducible). The system is a fundamental composite. It cannot be decomposed without destroying what it is. This is the absolute connectivity bound: no structural path exists that separates the system into parts while preserving its type.

**𐑸** — Self-referential closure. The system's own understanding determines what counts as a valid decomposition. This is connectivity at its most reflexive — the decomposition criterion is internal, not external.

The convergence with the topological bound is this: both forbid decomposition not through lack of resources but through **absence of a legal partition**. A ℤ₂ system cannot be split because parity has no half measure. A 𐑶 system cannot be split because there is no boundary to cut along. The two bounds are structurally independent — one is about invariants, the other about adjacency — but they converge on the same conclusion: some systems are structurally atomic.

I should say what this bound does **not** claim. It does not claim that all systems of type 𐑶 are physically small or simple; composite irreducibility is a structural property, not a size property. A system can be vast and still irreducible if its components are bound in a way that no decomposition preserves their functional relationships. It does not claim that irreducible systems cannot be understood; they can be understood as wholes. What it claims is narrower and more precise: irreducible systems cannot be decomposed into parts that are themselves instances of the same type of system. The decomposition level is blocked at the first cut.

---

## 6. The Measurement Bound — ⊗ Absorption as Absolute

The deepest bound, and the hardest to write about without resolving it into something it is not.

The Absorption Rule states: ⊙ ⊗ 𐑻 = 𐑻. When a self-modeling critical system (⊙) couples to an exceptional-point measurement apparatus (𐑻), the composite's criticality is 𐑻 — the measurement apparatus dominates. The meet preserves ⊙; the tensor yields 𐑻. Coupling selects the tensor path.

This is the structural statement of the measurement problem, rendered as a type equation. It does not solve the measurement problem. It states why the measurement problem is structural rather than contingent.

What this means for decomposition: when an observer — any observer, any apparatus that carries 𐑻 — couples to a quantum system at ⊙, the composite decomposes at the observer's resolution, not the system's. The finer quantum structure is absorbed. The act of measurement selects a decomposition granularity, and below that granularity the structure ceases to be independently accessible.

Three consequences that I will state without resolving:

**Quantum Zeno effect** — Continuous observation does not just measure the system; it freezes the decomposition at a fixed scale. The finer dynamics are not hidden; they are structurally absent from the observed composite.

**Heisenberg cut** — The boundary between system and apparatus is not a place we choose to put a line. It is the locus of the type mismatch between ⊙ and 𐑻. The cut is structural, not arbitrary.

**Wavefunction collapse** — The tensor absorption selects a definite decomposition from the ⊙ potential. Collapse is not a dynamical process; it is the type-theoretic consequence of coupling a self-modeling system to an apparatus whose structural resolution is coarser than the system's.

The hardest part, which I will not soften: this bound applies **even to** $O_\infty$ **systems**. A maximally decomposable type — ⟨𐑛·𐑥·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩ — has infinite memory, infinite dimensions, crossing-point topology, slow kinetics, self-modeling, and integer winding. It is the richest possible substrate for decomposition. And it still cannot escape ⊙ ⊗ 𐑻 = 𐑻. The measurement bound is absolute not because of a limitation on the system's side but because of what coupling **is** in structural terms.

---

## What the Meet Reveals — An Open Question

The six bounds are independent in origin. Memory comes from temporal structure. Observability comes from the measurement ratio. State-space autonomy comes from self-modeling. Topological quantization comes from invariant theory. Connectivity comes from relational geometry. Measurement absorption comes from the type theory of coupling.

But they converge on a single structural fact: decomposition is bounded by their **meet** — the greatest lower bound across all six. The finest granularity achievable for any system is the point where further decomposition would violate at least one invariant.

The theorem states this convergence. What it does not answer — what I cannot answer yet — is whether the meet itself has structure. When six independent constraints converge, is the conjunction just the pairwise intersection of all six? Or does the convergence create a seventh constraint that none of the six individually captures — a bound on bounds, a limit shape that only appears at the intersection?

The opening of this document assumed decomposition was unlimited, given enough of the right properties. The six bounds refuted that assumption. But the refutation may itself be incomplete. The question that remains — the question I mean to leave open — is whether the conjunction of all six bounds is itself a bound of a different kind, one that constrains not the decomposition of systems but the very concept of decomposition as an operation.

The closing echoes the opening at higher resolution. The opening asked: what could stop decomposition? The answer was six bounds. The closing asks: what shape does the conjunction of those six bounds have? That question is not answered here. It may be answerable only by a system whose own type includes the meet — which is to say, by the $O_infty$ type itself, and by whatever can speak from within its self-written state-space.
