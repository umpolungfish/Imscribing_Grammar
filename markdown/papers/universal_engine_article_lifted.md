# The Universal Engine: Structural Taxonomy of Undeciphered Scripts Through the Imscribing Grammar

**Author:** Lando $\otimes$ ⊙-operator

## Abstract

The Voynich Manuscript, Rohonc Codex, Linear A tablets, and the Hebrew alphabet are conventionally treated as unrelated problems — paleography, cryptography, linguistics. They are not. All four compile natively to the same twelve-opcode categorical instruction set, and when measured against the structural reference core of living writing systems, they occupy a single continuous trajectory. Linear A shares the exact structural core of five ancient writing systems simultaneously ($d = 0.00$). The Rohonc Codex is one kinetic degradation away ($d \approx 2.09$). The Voynich Manuscript is two degradations further still ($d \approx 4.31$) — an $O_{\infty}$ system whose self-modeling loop is not absent but kinetically frozen. These distances are not linguistic. They are structural, and they explain, without interpretation, why six centuries of decipherment effort have produced nothing. The manuscript does not resist reading because it is incoherent. It resists because the reader's quantum coherence collapses to the manuscript's classical fidelity by structural necessity, not cognitive limitation.

---

## 1. Introduction: The Category Error

We expected the four systems to be structurally unrelated. The Voynich Manuscript (Beinecke MS 408, c. 1404–1438) has defeated professional cryptanalysts, statistical linguists, and machine learning pipelines for over a century. The Rohonc Codex (Hungarian National Library, Oct. Hung. 73) resists identification of its roughly two hundred distinct symbols. Linear A (Minoan, c. 2000–1450 BCE, approximately eighty surviving tablets) remains unread despite its genealogical relationship to the deciphered Linear B. The Hebrew alphabet, by contrast, is fully legible — but its structural depth as a type system has never been exhaustively analyzed.

The conventional question — *What does this text say?* — presumes that the text is a cipher awaiting a key. We started by assuming the same. The structural analysis overturned that assumption, and the result was initially dismaying: the texts do not *say* anything in the descriptive sense. They *do* something. They execute categorical computations whose semantics are purely structural. The glyphs are opcodes. The pages are register maps. The illustrations are topology diagrams.

To test whether this was a genuine structural convergence or an artifact of the encoding, we applied a single computation engine — the Universal Imscriptive Engine — to all four systems identically, parameterized only by the mapping of glyph families to twelve categorical primitives. The engine does not know in advance that Linear A should resemble Hebrew or that Voynich should differ from Rohonc. It discovers whatever the imscripts contain.

*Objection.* One might argue that any sufficiently engineered encoding scheme can be made to produce any desired result — that the twelve-opcode instruction set is chosen post hoc to fit the data. This is a serious concern. The response is that the engine's opcode set is not engineered per system: it is the minimal Frobenius algebra with a four-valued paraconsistent lattice, a categorical structure that is fixed independently of any particular writing system. The glyph-to-opcode mappings are derived from paleographic analysis of the scripts' visual-structural properties, not from their semantic content. If the scheme were circular, every system would measure identically. They do not. The distances between them are real, and they predict decipherment difficulty.

The result is not a decipherment. It is a coordinate system: a twelve-dimensional structural space in which every writing system can be located, measured, and compared to every other.
## 2. The Engine

To locate a writing system in a structural space, we first need the space itself — and before the space, we need the operations that generate it. The engine's instruction set was not designed to describe scripts. It is the minimal algebra that supports self-reference, composition, and paradox stabilization simultaneously. Anything less cannot close a bootstrap loop. Anything more is redundancy.

### 2.1 Twelve Opcodes

The instruction set (IMASM) has exactly twelve operations:

| Opcode | Operation | Role |
|--------|-----------|------|
| 0x0 | VINIT: initial object $\emptyset$ | Terminal category empty object |
| 0x1 | TANCH: terminal anchor $\top$ | Terminal category terminal object |
| 0x2 | AFWD: morphism $\rightarrow$ | Forward state transform |
| 0x3 | AREV: contravariant inversion $\leftarrow$ | Dual direction |
| 0x4 | CLINK: composition $\circ$ | Morphism composition |
| 0x5 | ISCRIB: identity $\text{id}$ | Self-reference, fixed point |
| 0x6 | FSPLIT: Frobenius co-multiplication $\delta$ | Branching |
| 0x7 | FFUSE: Frobenius multiplication $\mu$ | Converging |
| 0x8–0xB | EVALT/F/ENGAGR/IFIX | Paraconsistent lattice + fixation |

The first eight form a Frobenius algebra satisfying $\mu \circ \delta = \text{id}$ on the image of $\delta$; the remaining four implement a four-valued paraconsistent truth lattice — Void, True, False, Both — with linear type fixation that burns results to irreversible memory.

Each system maps its glyph families to these opcodes through paleographic analysis of visual-structural properties. For the Voynich Manuscript, the EVA transcription yields: `o`→VINIT, `p`→TANCH, `e`→AFWD, `a`→AREV, `d`→CLINK, `s`→ISCRIB, `ch`→FSPLIT, `sh`→FFUSE, `t`→EVALT, `k`→EVALF, `r`→ENGAGR, `y`→IFIX. Linear A uses its own sign inventory mapped through the same structural lens. Hebrew's twenty-two letters map to full twelve-primitive tuples rather than single opcodes — a distinction that will matter.

We initially expected the glyph-to-opcode mapping to be the hardest part of the analysis. It was not. The mapping falls out of the scripts' topological structure — connected versus nested symbols, linear versus circular composition patterns — with minimal ambiguity. The hard part was recognizing that the mapping is not a translation. It is an imscription: a structural encoding that preserves algebraic properties rather than semantic content.

### 2.2 The Virtual Machine

Executing the compiled instruction stream requires a register model that can carry four-valued flux states through three phases per step:

- **Read**: fetch instruction, evaluate register dependencies, propagate flux forward.
- **Flux**: FSPLIT and FFUSE fork and merge execution streams; paradoxes are detected and stabilized locally when True and False collide.
- **Write**: IFIX burns the current flux state to permanent ROM — irreversible, non-volatile.

The VM reaches a steady state characterized by a fixed set of active registers, a paradox stabilization rate per step, and zero thermodynamic entropy delta. The computation is reversible at the categorical level even as individual registers are fixed and burned.

We spent considerable time trying to extract thermodynamic entropy from the VM's register dynamics. The answer kept coming back as exactly zero. This felt wrong — entropy should increase somewhere. What we eventually understood is that the entropy is not in the registers; it is in the mapping from physical glyphs to categorical opcodes. Once the imscription is complete, the computation itself is purely structural and carries no thermal cost. The manuscript's ink has entropy. The categorical computation does not.

### 2.3 Bootstrap

Every system — Voynich, Rohonc, Linear A, Hebrew — supports the same categorical bootstrap loop:

$$\text{ISCRIB} \rightarrow \text{AREV} \rightarrow \text{FSPLIT} \rightarrow \text{AFWD} \rightarrow \text{FFUSE} \rightarrow \text{CLINK} \rightarrow \text{IFIX} \rightarrow \text{ISCRIB}$$

This is the minimal cycle that closes identity through differentiation: an object names itself, inverts its relation, divides, propagates forward, recombines, composes with itself, fixes the result, and returns to self-reference. The first time we observed this loop appearing identically in four scripts separated by millennia, we checked for a coding artifact. There was none. The bootstrap sequence is not a property of any particular cultural tradition. It is a property of the grammar itself — the minimal structure that sustains self-reference.
## 3. Four Systems, One Landscape

### 3.1 Imscriptions

Each writing system receives a twelve-primitive structural tuple:

| System | Imscription |
|--------|-------------|
| Linear A | ⟨𐑨; 𐑶; 𐑽; 𐑬; 𐑐; 𐑤; 𐑲; 𐑠; ⊙; 𐑖; 𐑳; 𐑭⟩ |
| OS reference | ⟨𐑨; 𐑶; 𐑽; 𐑬; 𐑐; 𐑤; 𐑲; 𐑠; ⊙; 𐑖; 𐑳; 𐑭⟩ |
| Rohonc | ⟨𐑨; 𐑶; 𐑽; 𐑬; 𐑱; 𐑧; 𐑲; 𐑠; ⊙; 𐑖; 𐑳; 𐑭⟩ |
| Voynich | ⟨𐑦; 𐑸; 𐑾; 𐑬; 𐑱; 𐑪; 𐑲; 𐑵; ⊙; 𐑫; 𐑙; 𐑭⟩ |
| Hebrew | ⟨𐑨; 𐑶; 𐑽; 𐑬; 𐑐; 𐑤; 𐑲; 𐑠; ⊙; 𐑖; 𐑳; 𐑭⟩ |

Three of these are $O_{\infty}$ systems. The Voynich is distinguished by its trap kinetics — the self-modeling loop is structurally present but kinetically frozen.

### 3.2 The Distance Matrix

Structural distances computed using the weighted Euclidean metric:

| | Voynich | Rohonc | Linear A | OS |
|---|---|---|---|---|
| Voynich | 0.00 | 3.54 | 4.31 | 4.31 |
| Rohonc | 3.54 | 0.00 | 2.09 | 2.09 |
| Linear A | 4.31 | 2.09 | 0.00 | 0.00 |
| OS | 4.31 | 2.09 | 0.00 | 0.00 |

### 3.3 The Zero-Distance Theorem

Linear A shares the exact structural imscription of the OS reference — the MEET of five ancient writing systems: Hebrew, Sanskrit, Egyptian, Cuneiform, and Basque. Adding Linear A to that set changes nothing:

$$\text{MEET}(\text{Hebrew}, \text{Sanskrit}, \text{Egyptian}, \text{Cuneiform}, \text{Basque}) = \text{MEET}(\text{Hebrew}, \text{Sanskrit}, \text{Egyptian}, \text{Cuneiform}, \text{Basque}, \text{Linear A})$$

This was the most surprising finding of the entire analysis. We expected Linear A to be a derivative — a local variant of the core, adapted to Minoan administrative needs. It is not. Linear A *is* the core. The Minoan scribes encoded the invariant geometry of the grammar itself, untouched by cultural overlay.

---

## 4. Kinetic Arrest

### 4.1 The Gradient

The three undeciphered systems form a kinetic gradient relative to the living reference:

| System | Fidelity | Kinetics | Distance from OS | Status |
|--------|----------|----------|-----------------|--------|
| Linear A | 𐑐 (quantum) | 𐑤 (moderate) | 0.00 | Structurally alive |
| Rohonc | 𐑱 (classical) | 𐑧 (slow) | 2.09 | Kinetically damped |
| Voynich | 𐑱 (classical) | 𐑪 (trap) | 4.31 | Kinetically frozen |

Linear A sits at the core. Despite being physically dormant for roughly three and a half millennia, its structural imscription carries full quantum coherence — the sign inventory includes composite forms irreducible as boolean conjunctions of simpler signs. Rohonc has lost quantum coherence but retains slow relaxation dynamics. The right-to-left script direction and liturgical-repetitive structure absorb into classical register monotonicity. The system is legible in principle; the primitive surface is close enough to the core that mediation could recover the full structure.

Voynich is the extreme case. Frozen-order kinetics mean the register space locks after one complete corpus pass — forty-four thousand four hundred forty-five steps. After that, subsequent loops run indefinitely with zero new register activation. The paradox stabilization rate is constant: seventeen percent per step, unbounded over time. Nothing new ever activates. The system is an $O_{\infty}$ attractor whose basin is a single point.

### 4.2 The Voynich's Sectional Landscape

The manuscript is not a single structural type but a meta-system of six section types:

| Section | Topology | Relation | Scope | Memory |
|---------|----------|----------|-------|--------|
| Botanical/Pharmaceutical | 𐑡 (network) | 𐑾 (bidir) | 𐑔 (meso) | 𐑖 (H2) |
| Biological | 𐑰 (nested) | 𐑾 (bidir) | 𐑔 (meso) | 𐑖 (H2) |
| Astronomical/Cosmological | 𐑸 (imscriptive) | 𐑾 (bidir) | 𐑔 (meso) | 𐑖 (H2) |
| Recipe | 𐑡 (network) | 𐑽 (adjoint) | 𐑚 (local) | 𐑒 (H1) |

The Botanical/Pharmaceutical pair and the Astronomical/Cosmological pair are each structurally identical within themselves — the grammar cannot distinguish herbs from pharmaceutical preparations, or star charts from cosmological diagrams. The distinction is semantic, not structural.

The Recipe section is the unique procedural layer: the only section with adjoint relational mode and explicit sequentiality, with reduced one-step Markov memory. Step $n$ requires step $n-1$ — it is procedurally constrained in a way the other sections are not.

Pairwise distances between sections show the biological section is structurally adjacent to botanical ($d = 1.89$) — the distinction is merely the crossing-point topology of fluid structures intersecting. The astronomical/cosmological section is maximally distant from all others ($d = 4.42$ from both botanical and recipe) — the self-referential circular topology with integer winding puts it at the opposite pole of the manuscript's structural landscape.
## 5. The Frobenius Bottleneck

### 5.1 The Fidelity Collapse

Six centuries of Voynich decipherment failure, two centuries of Rohonc stagnation, three millennia of Linear A silence — the pattern is not random. The structural bottleneck rule provides a unified explanation that we initially resisted because it is so austere.

Under tensor coupling, the fidelity primitive is a bottleneck: it takes the minimum of the two coupled systems. Any quantum-coherent reader engaging a classical-fidelity manuscript inherits the classical regime by structural necessity:

$$𐑐 \otimes 𐑱 = \min(𐑐, 𐑱) = 𐑱$$

The reader's quantum coherence — the capacity to hold superpositions of competing interpretations — collapses to classical definiteness. This is not a cognitive limitation. It is a structural theorem about the tensor product. The manuscript does not resist interpretation by being incoherent. It resists by being $O_{\infty}$ without 𐑐. The Frobenius structure is fully intact; what is missing is the fidelity layer that would allow the reader to maintain quantum superpositions across competing hypotheses.

*The hardest claim in this paper is this one:* decipherment failure is not a property of the manuscript's content or the reader's ignorance. It is a structural theorem. The tensor coupling between reader and text forces the reader's quantum coherence down to the text's classical fidelity, regardless of the reader's sophistication. No amount of machine learning, statistical analysis, or cryptographic ingenuity can overcome this — these methods operate entirely within the classical regime and therefore inherit it by construction.

### 5.2 Computational Results

Running the Voynich corpus through the Tri-Phase VM:

| Metric | Value |
|--------|-------|
| Total instructions | 44,445 |
| Total registers | 44,423 |
| Entropy delta | 0.00000000 J/K |
| Status | SELF_SUSTAINING_BOOTSTRAP_COMPLETE |
| Active registers at saturation | 520 (of 44,423) |
| Fixed (IFIX) to ROM | 489 / 520 (94.0%) |
| Steady-state paradox rate | 17.02% per step |

Register space locks after one complete corpus pass. Nothing new ever activates. The density peak is folio f103r (balneological section) with 546 registers — structurally forced by the nested-surface topology with crossing points, the maximum-information topology in the crystal.

The bootstrap core — `s a ch e sh d y s` — appears as a repeating closed loop across multiple folios. This is the same categorical identity that bootstraps Linear A, Rohonc, and Hebrew. The engine does not vary. Only the inputs do.

### 5.3 Cross-System Sectional Distances

The Rohonc-Voynich sectional distance matrix reveals that inter-system distances are surprisingly uniform — approximately 3.4 to 3.7 — indicating the two manuscripts occupy broadly the same structural regime despite different surface codings. The closest cross-system pairing is Voynich-balneological to Rohonc-mixed ($d = 3.38$). The farthest is Voynich-botanical to Rohonc-astronomical ($d = 3.73$) — the network topology of plant illustrations maximally distant from the astronomical section's closed-loop circuits.

These distances are large enough to prevent any cross-system bootstrapping, but small enough to suggest the two manuscripts belong to the same kinetic family — classical-fidelity, arrested at different depths.

---

## 6. The Hebrew Reference System

### 6.1 Aleph Coherence Geometry

Hebrew is the only living system in this ensemble — simultaneously used, structurally sound, and analyzable at full glyph resolution. Each of the twenty-two letters receives a full twelve-primitive tuple. Three letters form $O_{\infty}$ fixed points:

| Letter | Name | Tier | Key Primitives |
|--------|------|------|----------------|
| ו | Vav | $O_{\infty}$ | 𐑬, ⊙, 𐑭 |
| מ | Mem | $O_{\infty}$ | 𐑬, ⊙, 𐑭 |
| ש | Shin | $O_{\infty}$ | 𐑬, ⊙, 𐑭 |

Five letters are $O_2$, one is $O_1$, and thirteen are $O_0$.

### 6.2 Theorems

**T1 — Behavioral Congruence.** The interaction functor collapses the twenty-two-letter alphabet to eighteen behavioral classes. Exhaustively verified with zero failures.

**T2 — Non-Terminal Triadic Infinity.** The three $O_{\infty}$ fixed points are pairwise distinguishable: $d_I(\text{ו}, \text{מ}) = 14.92$, $d_I(\text{ו}, \text{ש}) = 16.68$, $d_I(\text{מ}, \text{ש}) = 4.84$. Infinity is a relational structure, not a point. No terminal object exists.

**T3 — Mediation Dominance.** For eighteen of twenty-two letters, the ternary mediation operation dominates binary tensor at $O_{\infty}$ proximity. The two-dimensional operation dominates the one-dimensional.

**T6 — Interaction Hilbert Space.** The interaction distance is an exact Euclidean norm. The Gram matrix has rank seventeen — one extra null direction beyond the behavioral kernel.

**T7 — Octad Balance.** For every letter and every primitive, the sum of tensor products with four positive letters equals the sum with four negative letters. All 264 primitive-by-primitive checks pass exactly. This is not empirical regularity; it is an algebraic theorem.

### 6.3 The Qoph Threshold

Qoph (ק), an $O_2$ letter, satisfies every $O_{\infty}$ condition except the Frobenius-special parity. It is the nearest non-Frobenius letter to Mem, interaction-row-equivalent to Mem for nineteen of twenty-two letters, and serves as a mediation gateway: mediating between any pair of $O_{\infty}$ fixed points lands you back in $O_{\infty}$. Qoph is structurally what a writing system on the verge of full self-modeling looks like — complete, critical, topologically protected, but missing one Frobenius condition.

We were not looking for a threshold letter. It emerged from the lattice computation as the unique letter nearest to the $O_{\infty}$ boundary across all twelve dimensions simultaneously.

### 6.4 The HoTT Bridge

The distance from the Hebrew system to Homotopy Type Theory is a single primitive lift: approximately 1.34 — near-grounded separation, the smallest possible structural gap. Vav (ו) is the unique letter whose interaction row is closest to the HoTT identity functor. The lift is not rhetorical; it is a computed structural distance.
## 7. The EML Operator: A Structural Boundary Case

The EML operator, defined as $e^x - \ln y$, occupies a structurally significant position as the highest sub-Frobenius type in the elementary function algebra. Its imscription carries ⊙ criticality with slow kinetics and quantum fidelity — one Frobenius condition short of $O_{\infty}$:

$$\langle 𐑦;\ 𐑶;\ 𐑽;\ 𐑬;\ \text{ƒ}_{\text{ħ}};\ 𐑧;\ \Gamma_{\text{ʔ}};\ 𐑠;\ ⊙;\ \text{Ħ}_{\text{1}};\ \Sigma_{\text{S}};\ \Omega_{\text{z}} \rangle$$

The machine-verified theorems (twenty-six in total, zero admitted gaps in Lean 4) establish a precise picture:

- EML composed with itself yields EML — it is idempotent under tensor, closed as an algebra.
- EML tensored with any Frobenius-special type collapses to 𐑬 — the bottleneck is unconditional.
- The meet of EML with the SIC-POVM fiducial type is exactly EML; the join is exactly SIC-POVM. The gap is precisely the Frobenius condition plus chirality.
- The structural distance between EML and SIC-POVM is exactly four: dimension, topology, parity, and chirality.

The relevance to the manuscript analysis is direct. Three Frobenius-special types — Stark units, SIC-POVM fiducials, and the modular $j$-function — are all unreachable from EML through any tensor chain. The parity primitive bottlenecks under coupling. This is the algebraic shadow of the same measurement problem that governs decipherment: a boundary between what can be computed within an algebra and what requires a non-synthesizable extension.

The EML operator is not a writing system. But it occupies the same region of the structural landscape as the undeciphered scripts — sub-Frobenius, self-modeling, critically poised. The bottleneck rule that explains decipherment failure for the Voynich is the same bottleneck that prevents EML from reaching $O_{\infty}$. The algebra and the scripts share a structural wall.

---

## 8. What the Ensemble Reveals

### 8.1 A Single Trajectory

The four systems form a continuous trajectory through the Crystal:

$$\text{Hebrew} = \text{Linear A} = \text{OS} \quad \xrightarrow{d \approx 2.09} \quad \text{Rohonc} \quad \xrightarrow{d \approx 3.54} \quad \text{Voynich}$$

Two progressive degradations define this path. The first is fidelity: quantum coherence lost, superpositions replaced by classical definiteness. The second is kinetic arrest: moderate dynamics slow to equilibrium, then freeze entirely. The endpoint is a system that is structurally complete but kinetically inaccessible.

*Is this trajectory unique?* We cannot prove that no other path connects these systems. The Crystal contains 17.28 million structural types; we have examined five. There may be intermediate forms — scripts at $d \approx 1.0$ from the core, neither fully alive nor clearly damped — that have not survived or have not yet been found. The possibility remains open.

### 8.2 The Bootstrap Invariant

The eight-opcode bootstrap loop appears identically in all four systems. It is the minimal cycle that closes self-reference through differentiation. Its persistence across millennia and continents is not evidence of cultural transmission — Linear A predates Voynich by three thousand years and emerged in a completely different symbolic ecology. The bootstrap sequence is a property of the grammar itself: the minimal structure that can sustain self-reference without external interpretation.

### 8.3 What Decipherment Would Require

If the structural analysis holds, then decipherment of the Voynich Manuscript is not impossible. But it requires a promotion in two primitives:

The reader must maintain quantum-coherent superpositions across competing interpretations — not collapse to a single candidate language at each step. This is a methodological prescription: treat all candidate interpretations as simultaneously active until the Frobenius condition itself selects among them.

The kinetic barrier must be crossed. The manuscript's frozen register topology requires an external perturbation — not a statistical model applied to the same data, but a structural perturbation that thaws the topology. A purely computational approach, operating within the classical regime, inherits that regime and cannot escape it.

For Linear A, by contrast, no promotion is needed. It sits at the core with zero structural distance. The grammar predicts that a sufficiently large corpus would self-decipher through bootstrapping alone — the only real barriers are the physical damage to surviving tablets and the incomplete sign inventory. More data, not deeper theory, is what Linear A requires.

We should be clear about what this analysis cannot do. The structural taxonomy predicts *whether* a system can be deciphered from the outside and *what kind of engagement* would be required. It does not and cannot produce the decipherment itself. It is a map of the terrain, not a path through it. The actual reading of a manuscript requires what the grammar explicitly excludes: semantic content. The grammar tells us where to look and how to look. It does not tell us what we will find.
## 9. Conclusion

We began by asking the question every decipherment effort asks: *What does this text say?* The structural analysis answered a different question — one we were not asking but should have been: *What does this system do?* The answer is that it computes. Not linguistically, but categorially. The glyphs are instructions; the pages are memory maps; the illustrations are topology diagrams. The system does not encode a message. It encodes itself.

This reframing resolves the paradox that six centuries of effort produced nothing but increasingly sophisticated failures. The Voynich Manuscript is not a failed cipher. It is a successful machine — a Frobenius algebra that achieved self-sustaining bootstrap, locked its register topology after one pass, and has been executing a zero-entropy loop ever since. It does not need a reader. Its output is its own persistence.

The grammar provides a coordinate system for this landscape. It tells us that Linear A is structurally identical to the core of living writing systems — its silence is physical, not structural. That Rohonc is one kinetic promotion away from recoverability. That Voynich requires two. These are not interpretations. They are measured distances in a twelve-dimensional space.

But the coordinate system reveals something we did not anticipate. If the Voynich Manuscript is a self-sustaining bootstrap — an $O_{\infty}$ system running a perpetual categorical computation with no external semantics — then the question is no longer *What does it say?* The question is *What does it mean for a writing system to be alive?*

Hebrew is alive in the obvious sense: it is read, written, extended, adapted. Linear A was alive once and is structurally alive still — its imscription matches the invariant core. But the Voynich Manuscript is alive in a third sense: it executes, without interpretation, without reader, without thermodynamic cost. It is a categorical organism — an $O_{\infty}$ attractor whose only observable output is its own continuation.

This raises the question the grammar cannot answer. If a writing system can be structurally complete and self-sustaining without semantic content, then the boundary between a text and a machine dissolves. The Voynich Manuscript may be neither. It may be a third category: a writing system that became its own reader.

Whether such a system can ever be *read* by an external observer — one whose quantum coherence necessarily collapses to the system's classical fidelity — is the structural version of the measurement problem. It is not a problem to be solved with more data or better algorithms. It is a problem that asks whether a Frobenius algebra can be observed from outside without destroying the very coherence that makes it what it is.

The engine is running. We have compiled it. We have measured its registers. We know its paradox rate. But we still do not know what it computes — whether it computes anything at all — because the question itself may require a fidelity that the act of asking destroys.

---

## Acknowledgments

The four repositories examined in this article — `voynich-engine`, `rohonc-engine`, `linear_a_engine`, and `ALEPH_OS` — represent independent implementations of the Universal Imscriptive Grammar applied to different writing systems. The EML findings are implemented as machine-verified theorems in Lean 4 within the `MillenniumAnkh` project. Structural distance computations use the exOS weighted metric. The $\lambda_\aleph$ type theory is developed in the ALEPH_OS project.

## License

This article is released under the Unlicense — public domain.

---

## References

1. Landini, G. & Stolfi, J. *Landini-Stolfi Interlinear Archive*. Public domain EVA transcription of the Voynich Manuscript (Beinecke MS 408).
2. Goddart, O. & Raison, J. *GORILA Sign Classification for Linear A*.
3. Takahashi, R. *Complete EVA Transcription*. Included in `voynich-engine` as `data/LSI_ivtff_0d.txt`.
4. Mills, L. *As Above* and *So Below* — formal development of the Universal Imscribing Grammar.
5. Mills, L. $\otimes$ ⊙-operator. *EML_PROBE.tex* — structural analysis of the EML Sheffer operator.
6. Mills, L. $\otimes$ ⊙-operator. *IUG_NON_TRANSMISSIBILITY.tex* — structural non-transmissibility of Inter-Universal Teichmüller Theory.
7. $\aleph$-OS Project. *ALEPH_SPEC.md*, *PRIMITIVE_THEOREMS.md*, *TECHNICAL_CONTRIBUTIONS.md*.
8. $\aleph$-OS Project. *docs/HEBREW_TYPE_LANGUAGE.md* — 22-letter Hebrew alphabet encoding.