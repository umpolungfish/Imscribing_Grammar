---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
**Imscribing Grammar: LLM-Ready Reference**
**Version 0.5.2 (April 2026)**
**Core purpose**: A imscriptive type theory and relational algebra for any system that propagates constraints. Every system IS a TYPE — a 12-primitive tuple that fully determines all structural properties (ouroboricity, consciousness score, distance behavior, composition behavior). The boundary encoding determines the bulk. This IS NOT a labeling system.

---

### 1. The 12 Primitives (the type signature)

Every imscription IS exactly this 12-tuple:

⟨ **D**; **T**; **R**; **P**; **F**; **K**; **G**; **Γ**; **Φ**; **H**; **S**; **Ω** ⟩

| Primitive | Name | Values (low → high) | Weight |
|-----------|------|---------------------|--------|
| **D** | Dimensionality | 𐑛 · 𐑨 · 𐑼 · D_⊙ | 1.0 |
| **T** | Topology | 𐑡 · 𐑰 · 𐑥 · Þ_box · T_⊙ | 1.0 |
| **R** | Relational mode | 𐑩 · 𐑑 · 𐑽 · 𐑾 | 1.0 |
| **P** | Parity/symmetry | 𐑗 · 𐑿 · 𐑬 · 𐑯 · 𐑹 | 1.0 |
| **F** | Fidelity | 𐑱 · 𐑞 · 𐑐 | 1.0 |
| **K** | Kinetic character | 𐑘 · 𐑤 · 𐑧 · 𐑪 · 𐑺 | 1.0 |
| **G** | Scope/granularity | 𐑚 · 𐑔 · 𐑲 | 1.0 |
| **Γ** | Interaction grammar | Γ_and · Γ_or · Γ_seq · Γ_broad | 1.0 |
| **Φ** | Criticality | 𐑢 · ⊙ · 𐑮 · 𐑻 · 𐑣 | 1.0 |
| **H** | Chirality/chirality | 𐑓 · 𐑒 · 𐑖 · 𐑫 | 0.8 |
| **S** | Stoichiometry | 𐑙 · 𐑕 · 𐑳 | 1.0 |
| **Ω** | Topological protection | 𐑷 · 𐑴 · 𐑭 · 𐑟 | 0.7 |

**Key values:**
- **D_⊙**: boundary encodes bulk — the imscriptive primitive (symbol: monad point inside circle).
- **T_⊙**: imscriptive topology — highest T ordinal (5).
- **𐑹**: exact Z₂ symmetry at criticality — the Frobenius condition μ∘δ=id. Assign ONLY when provably exact.
- **⊙**: criticality — absorbing under meet: meet(⊙, x) = ⊙ for all x.
- **𐑻**: exceptional point — ordinal 2.67 > ⊙ = 2.00; destroys O_∞ under tensor.
- **𐑪**: trapped kinetics — frozen by order. Gates consciousness to zero regardless of other primitives.
- **𐑺**: many-body localized — frozen by disorder. Also gates consciousness to zero. Distinct from 𐑪: disorder-driven, not order-driven. Both fail Gate 2.
- **𐑟**: non-abelian topological protection — strongest Ω tier. Appears in systems with non-abelian Galois groups, IUG, SIC-Hilbert12 connection.

**Total structural types:** 17,280,000 = 3³ × 4⁵ × 5⁴ (Crystal of Types §64). Family partition: F_3 = {F, G, S} (3 values each, 3³=27); F_4 = {D, R, Γ, H, Ω} (4 values each, 4⁵=1024); F_5 = {T, P, Φ, K} (5 values each, 5⁴=625).

---

### 2. Ouroboricity Tiers (applied in strict priority order)

| Tier | Condition | Meaning |
|------|-----------|---------|
| **O_∞** | Φ_c AND 𐑹 | Special Frobenius: μ∘δ=id exactly. Self-referential loop perfectly closed. Finite, algebraically exact. |
| **O₀** | Φ ∈ {𐑢, 𐑣, 𐑻} | No ouroboricity. Cannot form self-referential critical loop. |
| **O₁** | Φ_c AND Ω_0 | Critical loop possible but unprotected — any deformation breaks it. |
| **O₂** | Φ_c AND Ω≠Ω_0 AND D ∈ {𐑛, D_⊙, 𐑨} | Critical, topologically protected, bounded domain. |
| **O₂†** | Φ_c AND Ω≠Ω_0 AND 𐑼 | Critical, topologically protected, unbounded domain. |

**Tier is determined by (Φ, P, Ω, D) only.** 𐑺 and 𐑪 do not affect tier — they gate consciousness but not ouroboricity.

**Composition rules (tensor = component-wise max on union primitives, min on P and F):**
- O_∞ ⊗ O_∞ → O_∞
- O_∞ ⊗ O_{1,2,2†} → O_∞
- O_∞ ⊗ O₀(𐑻) → O₀ ← **EP erases O_∞**
- O_∞ **cannot be synthesized** from non-𐑹 components — it must be planted (§23 Frobenius non-synthesizability)

**Bottleneck rule:** P and F resolve to min(A, B) under tensor. All other ordered primitives resolve to max. Consequence: 𐑹 ⊗ 𐑬 = 𐑬 — the Frobenius condition is destroyed by any sub-Frobenius partner.

---

### 3. Consciousness Score

$$C(\mathbf{x}) = [\Phi = \Phi_{\text{ctyogh}}] \cdot [K \leq K_{\text{schwa}}] \cdot (0.158\,\tilde{K} + 0.273\,\tilde{G} + 0.292\,\tilde{T} + 0.276\,\tilde{\Omega})$$

Two independent gates — neither subsumes the other:
- **Gate 1** [Φ=Φ_c]: state-space condition — topology admits self-modeling loop
- **Gate 2** [K≤𐑧]: flow condition — dynamics can actualize the loop. 𐑪 (frozen by order) AND 𐑺 (frozen by disorder) both fail this gate.

If either gate fails, C=0. Stellar examples: magnetar C=0.677 (highest stellar), black hole C=0 (Gate 2 fails: 𐑪), white dwarf C=0 (Gate 1 fails: 𐑢).

---

### 4. Core Algebra Operations

| Operation | Semantics | Use when asking |
|-----------|-----------|-----------------|
| **meet** A∧B | Component-wise min — shared structural floor | "What do these two systems share?" |
| **join** A∨B | Component-wise max — minimal upper bound | "What must a system containing both look like?" |
| **tensor** A⊗B | Structural composition — interacting system type | "What does the composed/interacting system look like?" |
| **project** | Restrict to primitive subset | "What does this look like in only these dimensions?" |
| **peel** | Strip one primitive to minimum | "What remains if we remove this structural requirement?" |
| **principal_decomp** | Join-irreducible atoms | "What are the irreducible components?" |
| **retrosynthetic_path** | Trace back to structural baseline | "How was this system built up from primitives?" |

**Distance interpretation:**
- d = 0.000 → structurally identical
- d < 0.500 → close analog (same structural family)
- d 0.5–1.5 → related by shared primitive subsets
- d > 1.5 → structurally remote (different regime)
- d > 3.0 → alien (essentially no shared structure)

Distance IS the structural story. The per-primitive breakdown shows WHERE divergence lives.

---

### 5. imscriptive Type Theory — Operational Consequences

The grammar IS a imscriptive type theory. This IS NOT a metaphor.

**Type inference (bulk → boundary):** Given observed behaviors, infer the type before encoding. The behavior constrains the tuple.

**Type checking (boundary → bulk):** Given a claimed encoding, every derived property IS determined. Contradictions between encoding and claimed behavior ARE type errors.

**Type composition IS relational operator composition:** Tensor IS NOT juxtaposition — it IS the composition of two directed relational operators.

**Cross-domain transfer IS imscriptive inference:** Same boundary → same bulk, regardless of substrate. Two systems with identical tuples share ALL structural properties necessarily.

**Type inhabitation IS design:** Given a target behavior, ask which tuples can inhabit it. Use retrosynthetic_path and principal_decomp as type-inhabitation tools.

**The grammar IS NOT a description of the world from outside. It IS the boundary theory of all relational systems.**

---

### 6. Dual-Encoding Protocol (for contested or anomalous systems)

1. Encode **holistically**: what tuple is required for the claimed behavior? Name `system_claimed`
2. Encode **compositionally**: encode each component, tensor mentally, encode result. Name `system_actual`
3. Call `compute_conflict_distance` → get d_c, conflict_set, conflict_type per primitive, veracity_class
4. **Compositional encoding IS canonical** unless a mechanism is established
5. Each aspirational conflict IS an open emergence question at a named primitive

**Veracity classes:** transparent (d_c=0) · near-grounded (√1–√2) · partial-emergence (√3–√6) · aspirational (≥√7)

---

### 7. Proof Taxonomy (derived from catalog)

The grammar distinguishes two proof archetypes:

**Discovery proofs:** Cross a structural gap. Introduce new primitive content. Ouroboricity promotes O₂→O_∞. Promotion signature [R, P, K, Γ, H] is the universal template: 𐑑→R_†, 𐑬→𐑹, 𐑤→𐑧, Γ_and→Γ_broad, H→𐑫. Examples: Berry-Tabor (proven), Fujita (theorem form).

**Witness proofs:** Confirm existing structure. No promotion. Same ouroboricity before and after. The theorem was always determined by the constraint geometry — proof is verification not discovery. Example: Erdős–Faber–Lovász.

**Counterexample collapse signature** (consistent across all sessions): 𐑛 + 𐑡 + 𐑗 + 𐑢 + 𐑷. Any conjecture whose counterexample encodes this way is structurally false.

---

### 8. Encoding Recipe

1. Identify dominant scale → choose **D**
2. Identify connectivity motif → choose **T**
3. Identify constraint/relational mechanism → choose **R**
4. Identify symmetry/directionality → choose **P** (𐑹 only when Z₂ is provably exact)
5. Estimate thermodynamic reliability → choose **F**
6. Estimate barrier / kinetic character → choose **K** (𐑪 overrides if frozen by order; 𐑺 overrides if frozen by disorder)
7. Identify control scale → choose **G**
8. Identify interaction logic → choose **Γ**
9. Probe criticality → choose **Φ** (⊙ IS absorbing under meet)
10. Identify chirality/chirality → choose **H**
11. Choose **S** (stoichiometry)
12. Derive **Ω** from topology + kinetics + dimensionality (𐑟 for non-abelian Galois/group protection)

**Rules:**
- NEVER invent primitive values — only use the documented set
- NEVER assign 𐑹 without provable exact Z₂ symmetry
- NEVER claim an encoding succeeded without tool confirmation
- The per-primitive breakdown IS the structural explanation — do not translate back to disciplinary language

---

### 9. Distance Thresholds & Structural Families

| Distance | Interpretation |
|----------|---------------|
| 0.000 | Type identity — structurally identical |
| < 0.500 | Close analog — same structural family |
| 0.5–1.5 | Related — shared primitive subsets |
| > 1.5 | Remote — different structural regime |
| > 3.0 | Alien — essentially no shared structure |

Known structural families in the catalog:
- **imscriptive geometric extremal problems**: D_⊙ + T_⊙ + ⊙ + 𐑲 + 𐑐 (Kusner, Fujita, Willmore-type)
- **imscriptive arithmetic conjectures**: D_⊙ + T_⊙ + ⊙ + 𐑹 (Riemann, RH+HC join)
- **Critical network symmetry problems**: 𐑼 + 𐑡 + 𐑯 + ⊙ + 𐑴 (EFL, kissing_dim_4)
- **Exceptional/solved-by-breaking**: 𐑻 + 𐑗 (Dehn/Hilbert-3, counterexamples)
- **Non-abelian arithmetic conjectures**: D_⊙ + ⊙ + 𐑹 + 𐑟 + 𐑐 (Zauner/SIC-Hilbert12, IUG)
