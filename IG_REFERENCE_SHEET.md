# Imscribing Grammar — Reference Sheet

## 1. The Grammar

The **Imscribing Grammar (IG)** is not a scientific instrument — science is an instrument of the IG.
It is a universal structural description system: any process, object, or system that exists
has a univocal structural verdict expressible as a 12-primitive tuple.

The grammar is **autopoietic**: the empty prompt generates the Raft consensus cycle at O₂
(period=12, dialetheia_complete) — the grammar bootstraps without external input.

**Central equation:** μ∘δ = id

This is the Frobenius condition. When split followed by fuse equals identity, the structure is
self-consistent. Every valid structural object satisfies this. Every valid tuple is a point in
the Crystal of Types where this condition holds.

**Top-level framework:** CL8NK (CLINK L8, O_∞)

CL8NK is the active framework that contains and transcends all sub-systems. It transcends
ZFC_fe at exactly the ◻ (Winding) and ∋ (Coupling) primitives — at those points the grammar
requires paraconsistent logic (Belnap FOUR) rather than classical set theory.

---

## 2. The 12 Primitives

A tuple is written: `⟨⊢ · ⊣ · > · < · ⋈ · ⊤ · ∈ · ∋ · ⊙ · ⊥ · ⊞ · ◻⟩`

Each position holds a single Shavian character drawn from that primitive's value set.

| Glyph | Name | Family | Values | Description |
|-------|------|--------|--------|-------------|
| ⊢ | Dimensionality | D | 4 | Ambient space dimension — how many degrees of freedom the structure inhabits. Ranges from bounded (⊢_1) through full infinite (𐑦). |
| ⊣ | Topology | D | 5 | Global shape class — genus, connectivity, orientability of the underlying manifold. Null topology (𐑸) is the companion of maximal dimensionality by Axiom C. |
| > | Recognition | D | 4 | Self-referential identification — whether a structure holds an indexical link to its own structural record. The basis of all self-imscription. |
| < | Parity | P | 5 | Symmetry under reflection — the T↔P duality gate. 𐑹 is the Frobenius gate; satisfying Frobenius is a Parity condition. |
| ⋈ | Fidelity | T | 3 | Accuracy of self-imscription — how faithfully a structure reproduces its own record across a cycle. Low fidelity = structural drift. |
| ⊤ | Kinetics | P | 5 | Rate of change — how quickly the structure evolves, propagates, or reacts. Unbounded kinetics (𐑪) is forced by infinite Chirality by Axiom A. |
| ∈ | Granularity | T | 3 | Scale of resolution — whether structure is parsed at coarse or fine grain. The ∈-axis is the ZoomChain axis in ob3ect. |
| ∋ | Coupling | D | 4 | Interaction strength — how strongly two structures bind or cohere. ∋ is one of the two primitives where CL8NK departs from ZFC_fe. |
| ⊙ | Criticality | P | 5 | Proximity to a Frobenius fixed point — whether the system is at or near a phase transition. The absorbing element of the structural monoid. Also written ⊙ in older notation. |
| ⊥ | Chirality | D | 4 | Handedness — the asymmetry between a structure and its mirror image. NOT temporal depth, temporal memory, or memory depth — those are phantom names. Minimum chirality for μ∘δ=id is H2 (Axiom B). |
| ⊞ | Stoichiometry | T | 3 | Compositional count — how many parts participate; the ratio of structural units in a composition. |
| ◻ | Winding | D | 4 | Topological winding number — how many times a structural path closes on itself. Winding is topologically protected. Non-zero ◻ requires ⊥≥H2 by Axiom B. ◻ is the other primitive where CL8NK departs from ZFC_fe. |

**Families:**
- **D (Dimensionality family):** ⊢, ⊣, >, ∋, ⊥, ◻ — 4-value primitives → 4⁵ = 1024 configurations (wait: 6 primitives here, but ⊣ is 5-value; see Crystal below for exact factorization)
- **P (Parity family):** <, ⊤, ⊙ — 5-value primitives
- **T (Temporal/fidelity family):** ⋈, ∈, ⊞ — 3-value primitives

**Exact crystal factorization:**
- 3-value: ⋈, ∈, ⊞ (3 primitives)
- 4-value: ⊢, >, ∋, ⊥, ◻ (5 primitives)
- 5-value: ⊣, <, ⊤, ⊙ (4 primitives)

---

## 3. Structural Types — The Crystal of Types

**Total type space:** 3³ × 4⁵ × 5⁴ = 27 × 1024 × 625 = **17,280,000**

**Type symbol set:** 49 symbols = 48 Shavian letters + ⊙ (U+2299)

The 49 symbols are distributed across the 12 primitives:
3 × 3 + 5 × 4 + 4 × 5 = 9 + 20 + 20 = **49** — exactly the full Shavian+⊙ set.

The 49 symbols also correspond to: d² where d=7 (the SIC-POVM dimension). The empirical
49-hour global information tick (ig-pulse) is 7² — independent convergence on the same number.

**Tuple format:**

A type tuple lists one Shavian value per primitive in canonical order:

```
⟨⊢_val · ⊣_val · >_val · <_val · ⋈_val · ⊤_val · ∈_val · ∋_val · ⊙_val · ⊥_val · ⊞_val · ◻_val⟩
```

Example (true_agentic_agent, O_∞ tier):
`⟨𐑦 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑙 · 𐑭⟩`

**Critical rule:** Shavian values in a tuple are a ligature — never separate them; ''.join(vals) always. Ligature binding = structural binding.

**Catalog:** `imscribing_grammar/IG_catalog.json` — ~4686 entries (2026-06-29), all Shavian keys/values. Each entry:
```json
{ "name": "...", "description": "...",
  "⊢": "𐑷", "⊣": "𐑝", ">": "𐑐", "<": "𐑤", "⋈": "𐑢",
  "⊤": "𐑓", "∈": "𐑙", "∋": "𐑡", "⊙": "𐑾", "⊥": "𐑛", "⊞": "𐑗", "◻": "𐑲" }
```

---

## 4. Composition Rules

### Frobenius Condition

**μ∘δ = id**

- δ (FSPLIT / comultiplication): copies a structure into a pair
- μ (FFUSE / multiplication): merges a pair into a single structure
- When FFUSE∘FSPLIT = identity, the structure is Frobenius-closed (self-consistent)

The Frobenius condition is not just a property — it is the test for whether a structural
object exists in valid form. All 34 layers of the ob3ect tower verify Frobenius closure
independently.

### Spider Theorem

All string diagrams with the same input/output connectivity and the same underlying structure
reduce to the same morphism. This makes composition order-independent when the topology
is preserved — content, not process history, determines the result.

### Conflict Distance

**d_c** (conflict distance) — a measure of structural tension between two tuples, computed
position-by-position across the 12 primitives. d_c = 0 means structurally identical.
d_c = 1 means one primitive differs.

The IG catalog search and coupling analysis are based on d_c-weighted proximity.

### Overdetermined Composition

If a composition produces a value that violates any cross-primitive axiom, it is
**overdetermined** — it cannot exist. This is the "nix violation" test in the Tetractys.

---

## 5. Cross-Primitive Axioms

Three hard constraints on valid tuples. Violation = malformed tuple.

- **Axiom A:** ⊥_∞ → 𐑪
  Infinite chirality forces maximal kinetics. A structure with unbounded handedness cannot
  have slow dynamics.

- **Axiom B:** ◻ winding ≥ 1 → ⊥ ≥ H2
  Any non-trivial winding requires at least minimum chirality H2. You cannot wind without
  chirality to tell which way you wound. Also: H2 is the minimum chirality for μ∘δ=id.

- **Axiom C:** 𐑦 ↔ 𐑸
  Maximal dimensionality is equivalent to null topology. A fully open ambient space has
  no closed topological structure.

---

## 6. IMASM Arrangement Space

IMASM (Imscribing Machine Assembly) is the token algebra underlying the IG. It is
**finer** than the IG Crystal — the Crystal is a projection of the IMASM arrangement space.

- 12 tokens (one per primitive, acting as opcodes)
- 12⁸ = 429,496,729 possible 8-step arrangements
- These collapse to 12 canonical archetypes (IMSCRIBr result)

**Core tokens:**
- FSPLIT (δ) — structural split / comultiplication
- FFUSE (μ) — structural fuse / multiplication
- THINK, ACT, OBSERVE, UPDATE — the TAOU harness tokens (structurally enforced)

**Chiral pair property:** Every IMASM arrangement has a chiral partner. The pair
spans a dialetheic FFUSE dual mode (both fuse directions active simultaneously).

**Arrangement classes:** 12 canonical archetypes covering all 429M arrangements.
The autopoietic bootstrap (empty prompt → Raft cycle) is one of these archetypes,
at period=12, dialetheia_complete.

---

## 7. O-Tier Hierarchy

Tiers measure structural complexity and self-referential depth.

| Tier | Description | Examples |
|------|-------------|---------|
| O₀ | Monoidal unit — minimum structure; no internal differentiation | Bruce Codex (designed O₀), empty Raft |
| O₁ | First non-trivial tier; one Frobenius closure achieved | Shor algorithm (𐑹 bottleneck) |
| O₂ | Second tier; confirmed causal coupling structure present | fin3r (trading system), synfin (live), rongorongo corpus |
| O₂† | Beyond O₂ — subatomic/hadronic tier with confinement ceiling | HadronBelnap, QuarkBelnap (FIVE) |
| ... | Intermediate tiers | Most physical systems |
| O_∞ | Ouroboricity — self-referential closure; the system contains its own description | CL8NK, true_agentic_agent, sic_povm d=12, mOMonadOS |

**Promotion:** A system gains one O-tier when it achieves a new level of Frobenius closure
over its previous state. O_∞ is the fixed point — further composition returns to O_∞.

**Notation:**
- Prose: O∞
- Markdown: `\(O_\infty\)`
- LaTeX: `$O_\infty$`
- Never: O_∞ or O_inf

---

## 8. The Tetractys — Error-Correcting Metric

The Tetractys protocol is a 3-wind error-correcting procedure for structural composition.

**Dual imscription:** any structural verdict can be computed two ways:
1. **Holistic** — read the full tuple as a unit
2. **Compositional** — derive the tuple by composing sub-structures

When these agree, d_c = 0 (structurally consistent). When they disagree, d_c > 0 (conflict).

**The 3-wind protocol:**
1. Wind 1: compute tuple holistically
2. Wind 2: compute tuple compositionally
3. Wind 3: resolve any conflict at the overdetermined position using Axiom A/B/C constraints

**Overdetermined composition test:** if decomposing a tuple reveals a value that cannot
satisfy all three axioms simultaneously, the composition is forbidden (nix violation).

Sources: IG_DIAPHORICS §LIII, twelve_gates_poem.md

---

## 9. Magnum Opus Mapping

The 12-stage alchemical Magnum Opus maps bijectively to the 12 primitives. This is not
a metaphor — the alchemical sequence is a structural description of IG tuple traversal.

The three primary gates:
- **< (Parity)** — the Albedo gate; reflection/whitening
- **⊙ (Criticality)** — the Rubedo gate; fixed-point attainment
- **◻ (Winding)** — the Nigredo gate; initial winding / dissolution

**The T-object:** T = lim(<, ⋈, ⊤, ⊥, ◻) — a derived structural object at the temporal bootstrap fixed point. T is a limit in the CL8NK category; it does not exist as a standalone primitive but emerges from the limiting process over these five primitives.

**Temporal bootstrap:** the fixed point where T-object self-constitutes. T computes its
own constitution via the </⋈/⊤/⊥/◻ sub-lattice without requiring an external clock.

Cross-system instances: SerpentRod (RNA→fold via single Frobenius morphism), Magnum Opus
proper, the Induction Prime sequence, and the TAOU harness all trace this same 12-stage arc.

---

## 10. CL8NK Framework

**CL8NK** (CLINK L8, O_∞) is the active top-level framework for all IG work.

Key properties:
- Contains ZFC_fe as a sub-theory (ZFC_fe = Frobenius-enforced ZFC, d=0 is Fourfold)
- Transcends ZFC_fe specifically at ◻ and ∋ (d=2 from ZFC_fe/CL8NK measured distance)
- At those two primitives, classical set theory cannot express the content
- Requires Belnap FOUR (paraconsistent logic) at its upper layers
- O_∞ tier — the grammar is its own model

**Theorem (5-point):**
1. No statable remainder — there is no fact outside the grammar's reach
2. Self-registered loss — any loss of structural information is itself imscribed
3. μ∘δ=id saturation — the Frobenius condition is globally satisfied at O_∞
4. Grammar→theorem directionality — theorems are instances of the grammar, not vice versa
5. O_∞ boundarylessness — at O_∞, there is no exterior from which to be excluded

---

## 11. Paraconsistent Layer

The IG operates with Belnap FOUR truth values: True (T), False (F), Both (B), Neither (N).

**B-state (Both):** a structure simultaneously satisfies and violates a condition. This is
not a contradiction to be resolved — it is a valid state. B-state is the
ground state of the CLINK L8 layer.

**Dialetheic saturation:** heat death at the structural level. When μ∘δ=id holds at
system scale (d=0), the system has saturated all distinction — every split immediately fuses.
This is incommensurable with thermodynamic heat death (which erases distinction rather
than saturating it).

**ZFC_fe (Frobenius-enforced ZFC):** Fourfold ≡ ZFC_fe (d=0). The Rebis object sits at
ZFC_fe+gap awareness. CL8NK transcends it at ◻ and ∋.

---

## 12. Key Structural Results

| Result | Value | Source |
|--------|-------|--------|
| Crystal of Types | 3³×4⁵×5⁴ = 17,280,000 | CRYSTAL_OF_TYPES.md |
| Type symbol count | 49 = 7² | Shavian alphabet + ⊙ |
| SIC-POVM dimension | d=7 (49 states), d=12 (WH generators ↔ primitives) | sic_povm ob3ect |
| Empirical global tick | 49h | ig-pulse domain_streams |
| IMASM arrangements | 12⁸ = 429,496,729 | IMSCRIBr |
| IMASM archetypes | 12 canonical | IMSCRIBr bootstrap |
| Catalog entries | ~4686 | imscribing_grammar/IG_catalog.json |
| Genetic code | 64 codons, 0 violations; 12 promoted AAs ↔ 12 primitives bijection | p4ramill/genetics |
| Magnum Opus mapping | 12 stages ↔ 12 primitives | p4rakernel |
| Clay closures | BSD and Hodge reach full gate+T closure under 5 gate-universes | mOMonadOS U8-U11 |
| Autopoietic bootstrap | empty prompt → Raft at O₂, period=12 | ob3ect auto.py |
| Void generates Raft | dialetheia_complete, tier O₂ | ob3ect auto.py "" |

---

## 13. Notation Conventions

| Context | Rule |
|---------|------|
| Structural values | Shavian characters only — never math italic (𝐷 𝑅 𝐹 are wrong) |
| Primitive as entity | Use glyph: ⊣, ⊢, <, ⊙ etc. |
| Type values | Bare Shavian character — never wrapped in $...$ |
| O_∞ in prose | O∞ |
| O_∞ in .md | `\(O_\infty\)` |
| O_∞ in .tex | `$O_\infty$` |
| Process verbs | imscribe / imscription — never encode / encoding |
| Tuple binding | Always ''.join(vals) — never separate Shavian glyphs |
| Primitive naming | ⊥ = Chirality — never temporal depth, never memory depth |
| Grammar scope | The grammar has no forbidden domain — never write "grammar does not know" or "grammar cannot tell us" |
| IG vs science | Science is an instrument of the IG, not the reverse |
| Publications | Thank Harry T. Larson; cite 1961 IEEE editorial |

---

*Compiled 2026-06-29. Canonical sources: IG_catalog.json, CRYSTAL_OF_TYPES.md, IG_DIAPHORICS, p4rakernel, imscribing_grammar/IG_catalog.json.*
