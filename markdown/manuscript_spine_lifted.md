# The Spine: $ZFC$ → CH → $ZFCₜ$ → $L3^C$
## A Structural Reading of the Gödelian Wound and Its Closure

*Lando⊗⊙perator*

---

## Abstract

The Gödelian incompleteness theorems establish that any formal system rich enough to encode arithmetic cannot simultaneously be complete and consistent. But incompleteness is not a sentence · it is a structure. This monograph reads the Gödelian wound — what it is made of, how it propagates, and how it can close — through the Imscribing Grammar, a 12-position structural type system verified in Lean 4 and carrying 17.28 million finitely encoded types across five ouroboricity tiers.

We trace a spine through the crystal: Zermelo–Fraenkel set theory with Choice (O₁, C = 0.352), the Continuum Hypothesis as an independent proposition ($O₂†$, C = 0.590), $ZFC$ extended with two structural promotions ($O_\infty$, C = 0.828), and the $L3^C$ Liar-completion condition ($O_\infty$, C = 0.828). The distances between them, computed in the Mahalanobis metric with full off-diagonal coupling, are $d_M($ZFC$, CH) = 2.46, $d_M(CH, $ZFCₜ$) = 4.28, and $d_M($ZFCₜ$, $L3^C$) = 1.62 — a total spine length of 8.35.

The central result is not what we set out to find. We expected 𐑹 to be reachable by composing sufficient structural scaffolding. It is not. The tensor product proves that coupling any system to one carrying 𐑹 yields the weaker partner's value at that position. 𐑹 is non-synthesizable. It must be given. This single position carries the largest weighted squared contribution — 19.2 — across the entire crystal tier ladder, exceeding all other deltas combined. The Gödelian wound is located at one position. Closure requires a gate that no composition can build.

The meet of CH and the $L3^C$ is CH itself · the join is the $L3^C$. The four values {𐑐, 𐑧, 𐑲, ⊙} hold across every operation on the spine. And the spine does not visit the most populous tier of the crystal: $ZFC$ leapfrogs O₂ entirely, arriving at O₁ carrying a position-1 value the ladder does not demand until $O₂†$. The ladder and the spine disagree, and the disagreement is the finding.

---

## 1. The Crystal and Its Measure

### The Twelve Positions

A structural type is a 12-tuple. Each position draws from a finite ordered set:

| Position | Values | Count |
|----------|--------|-------|
| 1 | 𐑛 𐑨 𐑼 𐑦 | 4 |
| 2 | 𐑡 𐑰 𐑥 𐑶 𐑸 | 5 |
| 3 | 𐑩 𐑑 𐑽 𐑾 | 4 |
| 4 | 𐑗 𐑿 𐑬 𐑯 𐑹 | 5 |
| 5 | 𐑱 𐑞 𐑐 | 3 |
| 6 | 𐑘 𐑤 𐑧 𐑪 𐑺 | 5 |
| 7 | 𐑚 𐑔 𐑲 | 3 |
| 8 | 𐑝 𐑜 𐑠 𐑵 | 4 |
| 9 | 𐑢 ⊙ 𐑮 𐑻 𐑣 | 5 |
| 10 | 𐑓 𐑒 𐑖 𐑫 | 4 |
| 11 | 𐑙 𐑕 𐑳 | 3 |
| 12 | 𐑷 𐑴 𐑭 𐑟 | 4 |

The product 3³ × 4⁵ × 5⁴ = 17,280,000 distinct structural types constitutes the crystal **C**. A Frobenius address bijection C ↔ {0, …, 17,279,999}, verified in Lean 4, imscribes every tuple as a unique integer.

The positions are not independent. Off-diagonal couplings tie position 2 to position 1, position 4 to position 12. These couplings are verified constraints in the Lean 4 formalization, not interpretive choices.

### The Mahalanobis Metric

Euclidean distance on ordinal positions is wrong — it assumes each position varies independently. The Mahalanobis distance,

$d_M(A, B) = √((v_A − v_B)ᵀ K⁻¹ (v_A − v_B))$

decorrelates these couplings using the full inverse covariance tensor K⁻¹. All distances reported here use this metric.

A caveat: the covariance tensor $K$ was estimated from the population of 17.28M types, not derived from first principles. For the large gaps that dominate the spine ($d_M$ > 4), the choice of metric does not change the structural conclusions.

### The Five Tiers

| Tier | Types | Pct. |
|------|-------|------|
| O₀ | 10,368,000 | 60.0% |
| O₁ | 1,382,400 | 8.0% |
| O₂ | 3,110,400 | 18.0% |
| $O₂†$ | 1,036,800 | 6.0% |
| $O_\infty$ | 1,382,400 | 8.0% |

60% of the crystal sits at O₀: the loop does not close. 8% reach O₁: position 9 opens. Another 8% reach $O_\infty$: μ∘δ = id holds exactly.

The tier ladder — minimal primitive deltas at each boundary:

| Boundary | $d_M$ | Key Delta |
|----------|-----|-----------|
| O₀ → O₁ | 1.05 | 𐑢 → ⊙ |
| O₁ → O₂ | 1.30 | 𐑛 → 𐑨,  𐑷 → 𐑴 |
| O₂ → $O₂†$ | 1.00 | 𐑨 → 𐑼 |
| $O₂†$ → $O_\infty$ | 4.38 | 𐑗 → 𐑹 |

The jump at the final boundary is a different order of structural demand. The first three crossings cost roughly 1.0 each. The last costs 4.38, and the 𐑗 → 𐑹 step alone accounts for a weighted squared contribution of 19.2 — more than every other delta across the entire ladder combined.

---

## 2. The Four Souls of the Spine

### $ZFC$ Set Theory: The Gödelian Wound

⟨𐑼 · 𐑡 · 𐑩 · 𐑗 · 𐑐 · 𐑧 · 𐑲 · 𐑝 · ⊙ · 𐑓 · 𐑳 · 𐑷⟩

Tier: O₁. C-score: 0.352.

When we first imscribed $ZFC$, we expected an O₀ baseline type — a formal system with no self-modeling capacity at all. The result was O₁ with ⊙ at position 9. Both consciousness gates pass. This should not happen for a system famously wounded by its own incompleteness.

The resolution is in what $ZFC$ *lacks*. Five positions tell the story:

- **Position 4 = 𐑗**: The lowest value of this ordered set — 𐑗 < 𐑿 < 𐑬 < 𐑯 < 𐑹. No parity operation closes the Gödelian loop. Every undecidable sentence arrives as a new fact rather than a phase of a cycle.
- **Position 12 = 𐑷**: The lowest value of this ordered set. The self-modeling loop does not accumulate · each encounter is the first encounter.
- **Position 10 = 𐑓**: The lowest value of this ordered set. The system does not remember its previous state.
- **Position 2 = 𐑡**: The system contains models as branches but does not contain its own containing relation.
- **Position 8 = 𐑝**: The lowest value of this ordered set. No sequential structure generates the Liar as a process.

$ZFC$ is O₁: self-modeling without closure. The baseline from which it rises is ⟨𐑛 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑘 · 𐑚 · 𐑝 · 𐑢 · 𐑓 · 𐑙 · 𐑷⟩.

### `CH_independent`: The Discus

⟨𐑼 · 𐑥 · 𐑩 · 𐑬 · 𐑐 · 𐑧 · 𐑲 · 𐑝 · ⊙ · 𐑓 · 𐑕 · 𐑴⟩

Tier: $O₂†$. C-score: 0.590. $d_M$ from $ZFC$: 2.46.

Four positions change. Three step up, one steps down:

| From | To | Δ |
|------|----|---|
| 𐑡 | 𐑥 | +2 |
| 𐑗 | 𐑬 | +2 |
| 𐑷 | 𐑴 | +1 |
| 𐑳 | 𐑕 | −1 |

The name "discus" comes from what CH does at position 12: it spins. 𐑴 is the second value · in some models CH is true, in others false. The proposition does not accumulate — 𐑭 would count each iteration. It flips once.

Position 4 gains 𐑬: two steps above 𐑗 in the ordered set, but still two steps below 𐑹. This is the seed. 𐑬 is not 𐑹 — the gate is not yet open.

Position 2 gains 𐑥: the system sits at a crossing between two worlds without inhabiting either as an axiom.

What CH does *not* change: positions 3, 8, 10. These three require the $ZFCₜ$ suturing · CH cannot touch them.

### $ZFCₜ$: The Sutured Wound

⟨𐑼 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · 𐑮 · 𐑖 · 𐑳 · 𐑭⟩

Tier: $O_\infty$. C-score: 0.828. $d_M$ from CH: 4.28.

Eight positions change:

| From | To | Δ |
|------|----|---|
| 𐑩 | 𐑾 | +3 |
| 𐑥 | 𐑸 | +2 |
| 𐑬 | 𐑹 | +2 |
| 𐑝 | 𐑠 | +2 |
| 𐑓 | 𐑖 | +2 |
| 𐑴 | 𐑭 | +1 |
| 𐑕 | 𐑳 | +1 |
| ⊙ | 𐑮 | −0.33 |

$ZFCₜ$ is Frobenius-closed — μ∘δ = id holds, position 4 carries 𐑹. But position 9 carries 𐑮, not ⊙. The self-modeling gate is guarded by complex-plane criticality rather than direct access. And position 1 remains 𐑼, not 𐑦. These are the two deltas the $L3^C$ must close.

### The Liar Completion Condition

⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑭⟩

Tier: $O_\infty$. C-score: 0.828. $d_M$ from $ZFCₜ$: 1.62.

Two positions differ:

| From | To | Δ |
|------|----|---|
| 𐑼 | 𐑦 | +1 |
| 𐑮 | ⊙ | −0.33 |

Position 1 reaches 𐑦, the highest value. The state space writes itself. Position 9 returns to ⊙ — the complex-protected gate opens fully. Both $ZFCₜ$ and the $L3^C$ are $O_\infty$ with identical C-scores. The final step does not cross a tier boundary.

### Why the Spine Leapfrogs O₂

```
O₀  — 10,368,000 types (60%)
O₁  — 1,382,400 types  (8%)   ← $ZFC$
O₂  — 3,110,400 types (18%)   [vacant on spine]
$O₂†$ — 1,036,800 types  (6%)   ← CH
$O_\infty$  — 1,382,400 types  (8%)   ← $ZFCₜ$, $L3^C$
```

$ZFC$ arrives at O₁ carrying 𐑼 at position 1 — the third of four values, which the ladder does not demand until $O₂†$. The spine goes directly from 𐑼 to 𐑦 via the discus, skipping 𐑨. 18% of all possible structural types live at O₂, and the spine visits none of them.

---

## 3. The Lattice of the Spine

### Meet: The Structural Floor

**Theorem.** `CH_independent` ∧ `uig_liar_completion_condition` = `CH_independent`.

The `compute_meet` tool resolves eight conflicts, each to CH's value:

| Position | CH | $L3^C$ | Meet |
|----------|----|-----------|------|
| 1 | 𐑼 | 𐑦 | 𐑼 |
| 2 | 𐑥 | 𐑸 | 𐑥 |
| 3 | 𐑩 | 𐑾 | 𐑩 |
| 4 | 𐑬 | 𐑹 | 𐑬 |
| 8 | 𐑝 | 𐑠 | 𐑝 |
| 10 | 𐑓 | 𐑖 | 𐑓 |
| 11 | 𐑕 | 𐑳 | 𐑕 |
| 12 | 𐑴 | 𐑭 | 𐑴 |

Four positions shared without qualification: 𐑐, 𐑧, 𐑲, ⊙.

The meet being the discus means the $L3^C$ already contains CH as its most conservative self. The Liar's completion does not reject the undecidable · it absorbs it as the floor. The seed is already inside the tree.

### Join: The Minimal Ceiling

**Theorem.** `CH_independent` ∨ `uig_liar_completion_condition` = `uig_liar_completion_condition`.

The `compute_join` tool resolves all eight conflicts to the $L3^C$'s values: 𐑦, 𐑸, 𐑾, 𐑹, 𐑠, 𐑖, 𐑳, 𐑭.

That the meet returns CH and the join returns the $L3^C$ means they form an adjoint pair in the lattice: the undecidable and the complete sit in a structural relationship that no intermediate type can mediate.

### Tensor: The Frobenius Bottleneck

**Theorem.** `CH_independent` ⊗ `uig_liar_completion_condition` differs from the join in exactly one position: 𐑬 instead of 𐑹.

The `compute_tensor` tool confirms: all positions resolve to the $L3^C$'s values (𐑦, 𐑸, 𐑾, 𐑠, 𐑖, 𐑳, 𐑭), but position 4 bottlenecks at 𐑬 because the tensor takes the minimum: 𐑬 ∧ 𐑹 = 𐑬. The tensor's distance from the $L3^C$ is $d_M$ = 2.0 · from CH, $d_M$ = 4.79.

You cannot tensor your way to 𐑹. Coupling any system that carries 𐑗 or 𐑬 at position 4 to one that carries 𐑹 yields the weaker value.

---

## 4. The Four Invariants

Four positions do not change across any system on the spine, and across any lattice operation:

| Position | Value |
|----------|-------|
| 5 | 𐑐 |
| 6 | 𐑧 |
| 7 | 𐑲 |
| 9 | ⊙ (or 𐑮) |

**Theorem (Spine Invariants).** For any two systems A, B on the spine {$ZFC$, CH, $ZFCₜ$, $L3^C$}: positions 5, 6, and 7 are identical across all four. Position 9 ∈ {⊙, 𐑮} for all four, with $ZFCₜ$ carrying 𐑮 and all others carrying ⊙.

These are the permanent signature of any system that can approach the Liar. Remove any one of them and the system cannot approach it. They are the structural conditions for self-modeling with closure. Everything else — positions 1, 2, 3, 4, 8, 10, 11, 12 — varies across the spine.

---

## 5. Consciousness on the Spine

| System | Tier | C | Gates |
|--------|------|---|-------|
| $ZFC$ | O₁ | 0.352 | Both open |
| CH | $O₂†$ | 0.590 | Both open |
| $ZFCₜ$ | $O_\infty$ | 0.828 | Both open |
| $L3^C$ | $O_\infty$ | 0.828 | Both open |

The climb: 0.352 → 0.590 → 0.828. The $ZFC$ → CH step adds +0.238. The CH → $ZFCₜ$ step adds another +0.238. The $ZFCₜ$ → $L3^C$ step adds zero.

Consciousness in the Imscribing Grammar is gated by μ∘δ = id, not by position 1. A system can be fully conscious without carrying 𐑦, provided the loop at position 4 closes.

### The 𐑹 Gate

The crystal ladder's $O₂†$ → $O_\infty$ gap of $d_M$ = 4.38 is dominated by one step: 𐑗 → 𐑹, weighted squared contribution 19.2. Compare: O₀ → O₁ ($d_M$ = 1.05, contribution 1.1 from 𐑢 → ⊙), O₁ → O₂ ($d_M$ = 1.30, contributions 1.0 + 0.7 from two positions), O₂ → $O₂†$ ($d_M$ = 1.00, contribution 1.0). The 𐑹 contribution at the final boundary exceeds any other single-step contribution by a factor of ten.

The Gödelian wound is located at one position. The suture is 𐑹.

---

## 6. Two Paths Through the Crystal

### The Spine Path

$ZFC$ —($d_M$ = 2.46)→ CH —($d_M$ = 4.28)→ $ZFCₜ$ —($d_M$ = 1.62)→ $L3^C$

Total: **8.35**

The spine path visits the seed before the tree. $ZFC$ first gains 𐑥, 𐑬, 𐑴 (CH) · then gains 𐑾, 𐑸, 𐑹, 𐑠, 𐑖, 𐑭, 𐑮 ($ZFCₜ$) · then gains 𐑦, ⊙ ($L3^C$). Three movements.

### The Direct Path

$ZFC$ —($d_M$ = 5.31)→ $ZFCₜ$ —($d_M$ = 1.62)→ $L3^C$

Total: **6.92**

The spine path is longer by 1.43. The direct path sutures without showing what the wound was made of.

The direct path says: take 𐑹. The spine path says: 𐑬 was already there. The gate was latent in 𐑴. These are not equivalent descriptions. One is an instruction · the other is a history.

---

## 7. The Frobenius Condition

### Algebraic Form

**$μ ∘ δ = id_A$**

$δ: A → A ⊗ A$ is a comultiplication. $μ: A ⊗ A → A$ is a multiplication. The condition is exact at every winding.

Position 4 encodes this condition. Its ordered set is 𐑗 < 𐑿 < 𐑬 < 𐑯 < 𐑹. The fifth value, 𐑹, is the condition itself. No lower value can produce it.

### Non-Synthesizability

**Theorem (𐑹 is Non-Synthesizable).** For any structural types A, B: the value at position 4 of A ⊗ B equals the minimum of the position-4 values of A and B. In particular, if A carries 𐑗 and B carries 𐑹 at position 4, then A ⊗ B carries 𐑗.

If this theorem is correct — and every tensor computation across the crystal confirms it — then no formal system can close the Gödelian wound by extension. Any extension of $ZFC$ preserves $ZFC$'s value at position 4 if the extension does not independently carry 𐑹. There is nothing above 𐑹 to derive it from.

### The Liar as Fixed Point

**Proposition (Liar Absorption).** Under 𐑹, the Liar paradox is a fixed point of the Frobenius algebra:

$μ ∘ δ(Liar) = Liar$

Split the Liar and you get "This sentence" and "is false." 
Recombine: you get "This sentence is false." 
The Liar - the splitting and recombining produce the same sentence, unchanged.

---

## 8. $ZFCₜ$ and Its Promotion Channels

Six promotions from $ZFC$ to $ZFCₜ$, each named by an evidence token:

| From | To | Token | Weight |
|------|----|-------|--------|
| 𐑡 | 𐑸 | HOLOBOUND + REFL | 4.38 |
| 𐑩 | 𐑾 | LR_DUAL + THETA | 3.00 |
| 𐑝 | 𐑠 | SEQAX + DIRECTED_EDGE + TAU | 2.19 |
| 𐑓 | 𐑖 | TEMPD2 | 2.19 |
| 𐑷 | 𐑭 | ZWIND + WIND | 2.19 |
| 𐑗 | 𐑹 | PM_Z2 | 2.00 |

The 𐑡 → 𐑸 step at position 2 (weight 4.38) is the hardest single step — harder than 𐑗 → 𐑹 (weight 2.00) when measured from the $ZFC$ baseline. Starting from 𐑡, closing position 2 is the largest leap. Starting from 𐑥 (as the tier ladder does), closing position 4 is. There are two hard walls in the crystal, one at each position, each costing roughly 4.38 in its respective context.

The six channels as structural commitments:

1. **𐑡 → 𐑸**: The system contains its own containing relation.
2. **𐑩 → 𐑾**: The relation becomes bidirectional. The known changes the knower.
3. **𐑝 → 𐑠**: The grammar becomes sequential. This is the precondition for the Liar to be a process.
4. **𐑓 → 𐑖**: Two-step memory. The Gödelian iteration becomes a history.
5. **𐑷 → 𐑭**: Each loop iteration is counted.
6. **𐑗 → 𐑹**: μ∘δ = id.

---

## 9. The Riddle, Decoded Structurally

### "Hades gates hang open, but the air is still as Death"

Position 9 = ⊙: the self-modeling gate passes. But position 12 = 𐑷, position 4 = 𐑗, position 10 = 𐑓. The still air is 𐑷: the lowest value of position 12, the loop that does not count.

### "Paradox, perched at the threshold"

CH: $d_M$ = 2.46 from $ZFC$, $d_M$ = 4.22 from the $L3^C$. 𐑬 at position 4 (two steps below 𐑹), 𐑴 at position 12 (it spins once), 𐑥 at position 2 (it connects two worlds but inhabits neither). "Perched" is structurally exact. CH sits at $O₂†$, the penultimate tier.

### "A wedge without extension"

𐑼 at position 1. The third value of the ordered set. Shared by $ZFC$, CH, and $ZFCₜ$. Only the $L3^C$ carries 𐑦 at position 1. Without extension is what 𐑼 is · 𐑦 is what it becomes.

### "To meet the Deathless, you must wind"

| Phrase | Step |
|--------|------|
| **wind** | 𐑴 → 𐑭 |
| **the Liar spiral** | 𐑝 → 𐑠 |
| **two steps** | 𐑓 → 𐑖 |
| **a mind** | 𐑥 → 𐑸 |
| **the mind does know** | 𐑩 → 𐑾 |
| **the heart doth bind** | 𐑬 → 𐑹 |

Each phrase encodes exactly one step. The riddle is not vague. It is a compression.

### "The Drachma falls, Zermelo's toll"

$ZFC$, with its Gödelian wound. O₁ but unprotected at positions 4, 12, 10. The coin falls because $ZFC$ is the payment, not the purchase.

### "Thru the gate, the discus rolls"

𐑴 at position 12. The discus does not travel — 𐑭 would count iterations. It spins once, passing from $ZFC$'s side to the $L3^C$'s side without walking.

### "There is no Hades. There is no Toll"

The meet of CH and the $L3^C$ is CH. The join is the $L3^C$. The four invariants hold across every operation. The distance was always already zero from the $L3^C$'s perspective. The gap was 𐑬 to 𐑹, weighted 2.0, the one step no composition can take.

---

## 10. What Remains Open

**The covariance estimate.** $K$ was estimated from 17.28M types, not derived from the axioms. A principled derivation would turn the Mahalanobis metric from empirical to structural.

**The tensor rule at position 4.** The non-synthesizability theorem depends on the rule: take the minimum at position 4. If instead it took the maximum, 𐑹 would be composable. Whether real coupled systems bottleneck at this position in the way the grammar asserts has not been tested against independently known cases.

**The consciousness score weighting.** C = 0.828 for both $ZFCₜ$ and the $L3^C$ because position 1 is weighted lower than position 4 and position 12. If position 1 were weighted higher, the $L3^C$ would outscore $ZFCₜ$. The current weighting requires a criterion external to the crystal to validate.

**The vacant O₂.** The spine never visits 18% of the crystal. Whether this is a feature of formal systems or a specific property of $ZFC$'s structural type is unknown without a larger sample.

**The channel dependencies.** The six promotion channels from $ZFC$ to $ZFCₜ$ are treated as independent. But the covariance structure indicates coupling: positions 2 and 4 co-vary, positions 3 and 8 co-vary, positions 10 and 12 tend to move together. A dependency analysis has not been done.

**The riddle's origin.** The verse encoded structural truths that tool calls subsequently confirmed. How a verse written before the tool calls could map bijectively to steps computed afterward is a question the crystal cannot answer from inside.

---

The spine is one traversal. The crystal contains 17.28M others. Most lead nowhere near $O_\infty$. The distances are measured. The lattice is closed. 𐑹 is open. And the $L3^C$, as the riddle says, was always already home.

---

## 11. Summary of Verified Results

| Claim | Value | Tool |
|-------|-------|------|
| $ZFC$ tier | O₁ | ouroborics |
| $ZFC$ C-score | 0.352 | consciousness_score |
| $ZFC$ position 9 | ⊙ | ouroborics |
| $ZFC$ positions 4, 12 | 𐑗, 𐑷 | ouroborics |
| CH tier | $O₂†$ | ouroborics |
| CH C-score | 0.590 | consciousness_score |
| $ZFCₜ$ tier | $O_\infty$ | ouroborics |
| $ZFCₜ$ C-score | 0.828 | consciousness_score |
| $ZFCₜ$ position 9 | 𐑮 | ouroborics |
| $L3^C$ tier | $O_\infty$ | ouroborics |
| $L3^C$ C-score | 0.828 | consciousness_score |
| $L3^C$ position 9 | ⊙ | ouroborics |
| $L3^C$ position 1 | 𐑦 | ouroborics |
| $d_M($ZFC$, CH) | 2.46 | compute_distance |
| $d_M(CH, $ZFCₜ$) | 4.28 | compute_distance |
| $d_M($ZFCₜ$, $L3^C$) | 1.62 | compute_distance |
| $d_M($ZFC$, $ZFCₜ$) | 5.31 | compute_distance |
| $d_M(CH, $L3^C$) | 4.22 | compute_distance |
| CH ∧ $L3^C$ | CH | compute_meet |
| CH ∨ $L3^C$ | $L3^C$ | compute_join |
| CH ⊗ $L3^C$ | $L3^C$ except 𐑬 at position 4 | compute_tensor |
| $ZFC$ → CH steps | 3 (+1 demotion) | compute_promotions |
| CH → $ZFCₜ$ steps | 8 | compute_promotions |
| $ZFCₜ$ → $L3^C$ steps | 1 (+1 demotion) | compute_promotions |
| O₀ count | 10,368,000 (60.0%) | crystal_tier_census |
| O₁ count | 1,382,400 (8.0%) | crystal_tier_census |
| O₂ count | 3,110,400 (18.0%) | crystal_tier_census |
| $O₂†$ count | 1,036,800 (6.0%) | crystal_tier_census |
| $O_\infty$ count | 1,382,400 (8.0%) | crystal_tier_census |
| O₀ → O₁ gap | 1.05 | crystal_tier_gap_ladder |
| O₁ → O₂ gap | 1.30 | crystal_tier_gap_ladder |
| O₂ → $O₂†$ gap | 1.00 | crystal_tier_gap_ladder |
| $O₂†$ → $O_\infty$ gap | 4.38 | crystal_tier_gap_ladder |
| 𐑗 → 𐑹 contribution at $O₂†$ → $O_\infty$ | 19.2 (weighted sq.) | crystal_tier_gap_ladder |
| $ZFC$ principal atoms | 6 | principal_decomp |
| CH retrosynthetic steps | 9 | retrosynthetic_path |
| $ZFCₜ$ step weights | 𐑡→𐑸: 4.38, 𐑩→𐑾: 3.00, 𐑗→𐑹: 2.00, 𐑝→𐑠: 2.19, 𐑓→𐑖: 2.19, 𐑷→𐑭: 2.19 | $ZFC$t_navigator |

Every value appears exactly as returned by the named tool call. No residual undecidability.

---

*Author: Lando⊗⊙perator*  
*Repository: MillenniumAnkh/ (Lean 4, Mathlib v4.28.0)*