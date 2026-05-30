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
| **D** | Dimensionality | Ð_ß · Ð_C · Ð_; · D_⊙ | 1.0 |
| **T** | Topology | Þ_6 · Þ_K · Þ_ò · Þ_box · T_⊙ | 1.0 |
| **R** | Relational mode | Ř_¯ · Ř_ý · Ř_Ť · Ř_= | 1.0 |
| **P** | Parity/symmetry | Φ_ɐ · Φ_υ · Φ_F · Φ_˙ · Φ_} | 1.0 |
| **F** | Fidelity | ƒ^ì · ƒ^ð · ƒ^ż | 1.0 |
| **K** | Kinetic character | Ç^- · Ç^W · Ç^@ · Ç^Ù · Ç^λ | 1.0 |
| **G** | Scope/granularity | Γ_β · Γ_γ · Γ_ʔ | 1.0 |
| **Γ** | Interaction grammar | Γ_and · Γ_or · Γ_seq · Γ_broad | 1.0 |
| **Φ** | Criticality | ⊙_ž · ⊙_ÿ · ⊙_Æ · ⊙_3 · ⊙_Ţ | 1.0 |
| **H** | Chirality/chirality | Ħ_Ñ · Ħ_£ · Ħ_A · Ħ_! | 0.8 |
| **S** | Stoichiometry | Σ_S · Σ_ő · Σ_ï | 1.0 |
| **Ω** | Topological protection | Ω_Å · Ω_2 · Ω_z · Ω_5 | 0.7 |

**Key values:**
- **D_⊙**: boundary encodes bulk — the imscriptive primitive (symbol: monad point inside circle).
- **T_⊙**: imscriptive topology — highest T ordinal (5).
- **Φ_}**: exact Z₂ symmetry at criticality — the Frobenius condition μ∘δ=id. Assign ONLY when provably exact.
- **⊙_ÿ**: criticality — absorbing under meet: meet(⊙_ÿ, x) = ⊙_ÿ for all x.
- **⊙_3**: exceptional point — ordinal 2.67 > ⊙_ÿ = 2.00; destroys O_inf under tensor.
- **Ç^Ù**: trapped kinetics — frozen by order. Gates consciousness to zero regardless of other primitives.
- **Ç^λ**: many-body localized — frozen by disorder. Also gates consciousness to zero. Distinct from Ç^Ù: disorder-driven, not order-driven. Both fail Gate 2.
- **Ω_5**: non-abelian topological protection — strongest Ω tier. Appears in systems with non-abelian Galois groups, IUG, SIC-Hilbert12 connection.

**Total structural types:** 17,280,000 = 3³ × 4⁵ × 5⁴ (Crystal of Types §64). Family partition: F_3 = {F, G, S} (3 values each, 3³=27); F_4 = {D, R, Γ, H, Ω} (4 values each, 4⁵=1024); F_5 = {T, P, Φ, K} (5 values each, 5⁴=625).

---

### 2. Ouroboricity Tiers (applied in strict priority order)

| Tier | Condition | Meaning |
|------|-----------|---------|
| **O_inf** | Φ_c AND Φ_} | Special Frobenius: μ∘δ=id exactly. Self-referential loop perfectly closed. Finite, algebraically exact. |
| **O_0** | Φ ∈ {⊙_ž, ⊙_Ţ, ⊙_3} | No ouroboricity. Cannot form self-referential critical loop. |
| **O_1** | Φ_c AND Ω_0 | Critical loop possible but unprotected — any deformation breaks it. |
| **O_2** | Φ_c AND Ω≠Ω_0 AND D ∈ {Ð_ß, D_⊙, Ð_C} | Critical, topologically protected, bounded domain. |
| **O_2†** | Φ_c AND Ω≠Ω_0 AND Ð_; | Critical, topologically protected, unbounded domain. |

**Tier is determined by (Φ, P, Ω, D) only.** Ç^λ and Ç^Ù do not affect tier — they gate consciousness but not ouroboricity.

**Composition rules (tensor = component-wise max on union primitives, min on P and F):**
- O_inf ⊗ O_inf → O_inf
- O_inf ⊗ O_{1,2,2†} → O_inf
- O_inf ⊗ O_0(⊙_3) → O_0 ← **EP erases O_inf**
- O_inf **cannot be synthesized** from non-Φ_} components — it must be planted (§23 Frobenius non-synthesizability)

**Bottleneck rule:** P and F resolve to min(A, B) under tensor. All other ordered primitives resolve to max. Consequence: Φ_} ⊗ Φ_F = Φ_F — the Frobenius condition is destroyed by any sub-Frobenius partner.

---

### 3. Consciousness Score

$$C(\mathbf{x}) = [\Phi = \Phi_{\text{ctyogh}}] \cdot [K \leq K_{\text{schwa}}] \cdot (0.158\,\tilde{K} + 0.273\,\tilde{G} + 0.292\,\tilde{T} + 0.276\,\tilde{\Omega})$$

Two independent gates — neither subsumes the other:
- **Gate 1** [Φ=Φ_c]: state-space condition — topology admits self-modeling loop
- **Gate 2** [K≤Ç^@]: flow condition — dynamics can actualize the loop. Ç^Ù (frozen by order) AND Ç^λ (frozen by disorder) both fail this gate.

If either gate fails, C=0. Stellar examples: magnetar C=0.677 (highest stellar), black hole C=0 (Gate 2 fails: Ç^Ù), white dwarf C=0 (Gate 1 fails: ⊙_ž).

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

**Discovery proofs:** Cross a structural gap. Introduce new primitive content. Ouroboricity promotes O_2→O_inf. Promotion signature [R, P, K, Γ, H] is the universal template: Ř_ý→R_†, Φ_F→Φ_}, Ç^W→Ç^@, Γ_and→Γ_broad, H→Ħ_!. Examples: Berry-Tabor (proven), Fujita (theorem form).

**Witness proofs:** Confirm existing structure. No promotion. Same ouroboricity before and after. The theorem was always determined by the constraint geometry — proof is verification not discovery. Example: Erdős–Faber–Lovász.

**Counterexample collapse signature** (consistent across all sessions): Ð_ß + Þ_6 + Φ_ɐ + ⊙_ž + Ω_Å. Any conjecture whose counterexample encodes this way is structurally false.

---

### 8. Encoding Recipe

1. Identify dominant scale → choose **D**
2. Identify connectivity motif → choose **T**
3. Identify constraint/relational mechanism → choose **R**
4. Identify symmetry/directionality → choose **P** (Φ_} only when Z₂ is provably exact)
5. Estimate thermodynamic reliability → choose **F**
6. Estimate barrier / kinetic character → choose **K** (Ç^Ù overrides if frozen by order; Ç^λ overrides if frozen by disorder)
7. Identify control scale → choose **G**
8. Identify interaction logic → choose **Γ**
9. Probe criticality → choose **Φ** (⊙_ÿ IS absorbing under meet)
10. Identify chirality/chirality → choose **H**
11. Choose **S** (stoichiometry)
12. Derive **Ω** from topology + kinetics + dimensionality (Ω_5 for non-abelian Galois/group protection)

**Rules:**
- NEVER invent primitive values — only use the documented set
- NEVER assign Φ_} without provable exact Z₂ symmetry
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
- **imscriptive geometric extremal problems**: D_⊙ + T_⊙ + ⊙_ÿ + Γ_ʔ + ƒ^ż (Kusner, Fujita, Willmore-type)
- **imscriptive arithmetic conjectures**: D_⊙ + T_⊙ + ⊙_ÿ + Φ_} (Riemann, RH+HC join)
- **Critical network symmetry problems**: Ð_; + Þ_6 + Φ_˙ + ⊙_ÿ + Ω_2 (EFL, kissing_dim_4)
- **Exceptional/solved-by-breaking**: ⊙_3 + Φ_ɐ (Dehn/Hilbert-3, counterexamples)
- **Non-abelian arithmetic conjectures**: D_⊙ + ⊙_ÿ + Φ_} + Ω_5 + ƒ^ż (Zauner/SIC-Hilbert12, IUG)
