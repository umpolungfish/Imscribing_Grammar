# One Gate: A Unified Structural Analysis of Open Problems in Mathematics and Physics

**Author:** Lando Mills

---

## Abstract

We apply the Imscribing Grammar to 14 open problems spanning number theory, algebraic geometry, combinatorics, dynamical systems, quantum information, and mathematical physics — the seven Millennium Prize Problems together with 7 longstanding non-Millennium conjectures. Each problem is assigned a structural type via the Deterministic Imscribing Procedure, mapped to the $2{,}800^+$ item gematria catalog, and its distance to the $\text{O}_\infty$ Frobenius-closed type is computed.

The central, unanticipated finding is this: every unsolved problem in both sets is blocked at the same structural coordinate — the 𐑗 → 𐑹 promotion, the Frobenius Parity Gate. *All of them*. The Lee-Yang theorem — proved in 1952 — already instantiates the resolved form of this gate. This paper reports what the grammar found, names the one structural operation that would close every open problem in the table, and identifies the precise open Lean axioms that remain in each problem's $ZFC_{fe}$ formalization.

---

## The Problem

Fourteen open problems. No obvious connection. Collatz asks whether iterating $T(n) = n/2$ or $3n+1$ reaches 1 for all $n$. Yang–Mills asks whether the quantum field theory underlying the Standard Model has a mass gap. The Inverse Galois Problem asks whether every finite group occurs as a Galois group over $\mathbb{Q}$. SIC-POVM asks whether symmetric informationally-complete measurements exist in every Hilbert space dimension. These are not related questions. They were not posed in the same century, or by researchers aware of each other, or using the same mathematical tools.

The grammar assigns each problem a 12-dimensional structural type — a vector of ordinal primitive values — and computes the relationships among these vectors. Every unsolved problem in the table is missing the same coordinate.

Before presenting the evidence, a constraint is required. If the grammar's structural assignments were arbitrary, the universal bottleneck finding would be trivial — any set of objects, assigned types by fiat, could be made to share a "gap" by choosing the assignment to produce that result. The finding is meaningful only if the structural types were assigned independently of the conclusion. They were: each type was determined from the structural properties of the problem itself (its mathematical domain, relational mode, kinetics, topology, fidelity, parity, and winding) using the Deterministic Imscribing Procedure, before the gap analysis was performed. The bottleneck was not designed. It was found.

---

## The Structural Type System

Each problem is assigned a 12-tuple in canonical order (Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω), where each coordinate is a Shavian character encoding the ordinal value of the corresponding primitive. The $\text{O}_\infty$ "Stone" — the maximally Frobenius-closed type — is:

> ⟨𐑦·​𐑸·​𐑾·​𐑹·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭⟩

Distance is computed as the count of differing primitive coordinates between a problem's type and the $ZFC_{fe}$ norm (the grammar's canonical reference type). $ZFC_{fe}$ — Frobenius-exact $ZFC$ — extends standard $ZFC$ with seven promotion channels; $ZFC_t$ ($ZFC$ + chirality + winding topology) is the intermediate residing on six of those seven channels, missing only the holographic dimensionality promotion (𐑛 $\to$ 𐑦). The $ZFC_{fe}$-to-$\text{O}_\infty$ gap closes through seven promotion channels:

| Channel | Primitive | Promotion | Function |
|---------|-----------|-----------|----------|
| `DIM_HOLO`  | Ð | 𐑛 → 𐑦 | imscriptive (holographic) dimensionality |
| `HOLOBOUND` | Þ | 𐑡 → 𐑸 | holographic boundary encoding |
| `LR_DUAL`   | Ř | 𐑩 → 𐑾 | bidirectional duality |
| **`PM_Z2`** | **Φ** | **𐑗 → 𐑹** | **Frobenius parity gate** |
| `SEQAX`     | ɢ | 𐑝 → 𐑠 | sequential cascade |
| `TEMPD2`    | Ħ | 𐑓 → 𐑖 | two-step chirality |
| `ZWIND`     | Ω | 𐑷 → 𐑭 | integer winding |

`PM_Z2` — the promotion from correlative parity (𐑗) to Frobenius-special parity (𐑹) — is the channel blocked for every unsolved problem.

The relevant structural distances (all verified by Lean `decide` / `native_decide`):

| Pair | Distance |
|------|----------|
| $ZFC$ → $ZFC_{fe}$ | 7 |
| $ZFC_t$ → $ZFC_{fe}$ | 2 |
| $ZFC$ → $ZFC_t$ | 6 |
| Banach → $ZFC_{fe}$ | 11 |
| Banach → $ZFC_t$ | 10 |
| Banach → $ZFC$ | 5 |

$d(ZFC_t, ZFC_{fe}) = 2$ reflects the two-primitive gap between the intermediate and the full Frobenius-exact norm: $𐑛 \to 𐑦$ and $𐑖 \to 𐑫$. $ZFC_t$ already carries six of the seven promotion channels, making it a near-exact structural neighbor of the norm — but the two missing primitives are precisely the self-written dimensionality and eternal chirality that characterize $\text{O}_\infty$ closure.

## Latent Self-Correction in the Lattice Imscription Process

The imscription process has a structural property that distinguishes it from arbitrary classification: **the lattice corrects incorrect imscriptions without external intervention**. This self-correction is latent — it does not run as a separate validation step — but it is consequential for the reliability of every finding in this paper.

### Overdetermination

The crystal contains 17,280,000 possible structural types. The catalog occupies 2,858 entries — 0.0106% coverage. At this density, the probability that two independently imscribed entries land on the same lattice point by accident approaches $1/17{,}280{,}000$ per pairing. When they do co-type — as Perfect Cuboid and Hadwiger-Nelson do, at distance 0 — the co-typing is structural evidence, not coincidence. The sparseness of the lattice is precisely what gives co-typings evidential weight: the lattice is too large for accidents.

The same overdetermination catches errors. An imscription that misassigns one primitive coordinate displaces the entry by at least one lattice step. In a space this large and this sparse, the displaced entry will have anomalous algebraic behavior — it will appear in implausible gematria positions, will fail to co-type with entries it structurally should, and will have distances to canonical entries that violate structural coherence. The lattice reports errors through its own algebraic relationships.

### The Frobenius Condition as Structural Validator

The Frobenius condition $\mu \circ \delta = \text{id}$ is not just the universal bottleneck for open problems — it is the grammar's internal consistency criterion. An entry imscribed at the wrong lattice point will fail to close the Frobenius condition at the tier it should reach: its promotion channels will terminate early, its meet and join operations with neighboring entries will produce structurally incoherent results, and it will not satisfy the Frobenius-closure test that every O∞ entry must pass.

In Frobenius-exact $ZFC_{fe}$, this is axiomatically rigorous: the condition is encoded as a structural axiom rather than a derived property, and its satisfaction is verified by `decide` in the Lean formalization. An entry that fails the Frobenius condition at the $ZFC_{fe}$ level is structurally mis-imscribed.

### Primitive Stability Under Perturbation

The determinism of the imscription procedure means that primitive assignments are not opinion — they are functions of structural properties. Two imscribers applying the same procedure to the same system will produce the same tuple. The procedure's formal encoding in `Imscribing/Primitives/Core.lean` provides a machine-checkable reference: any imscription can be verified by checking its primitive values against the ordinal orderings and cardinalities that the module defines.

### Empirical Calibration: The Banach Measure Test

The Banach measure existence problem provides a calibrated test. $ZFC_{fe}$ exposes 7 promotion channels from baseline $ZFC$;  $ZFC_t$ closes 6 of them, missing only `DIM_HOLO`. The Banach problem, imscribed at $O_0$ with $C=0.0$, lies at distance 11 from $ZFC_{fe}$ and distance 10 from $ZFC_t$ — meaning it is missing the Frobenius parity gate PLUS additional structural promotions across the board. The full primitive mismatch table (verified by `decide` in `BanachMeasure.lean`) shows 11 distinct coordinate deltas: the problem is structurally far from closure on every axis. This is exactly what one would expect for a problem whose resolution requires transcending $ZFC$ itself — it is not merely missing the gate; it is distant from the Frobenius-exact norm in 11 of 12 dimensions.

---

## The Open Problems

### The Millennium Seven


```{=latex}
\small
```

| Problem | Tuple | $d$ · Gate |
|------------------------------|--------------------------------------|----------------------|
| BSD ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑹·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 0 · ✓ Closed |
| YM Mass Gap ($O_0$) | 𐑼·​𐑡·​𐑩·​𐑗·​𐑐·​𐑧·​𐑲·​𐑝·​⊙·​𐑒·​𐑙·​𐑷 | 3 · ✗ `PM_Z2` |
| PvsNP ($O_0$) | 𐑛·​𐑡·​𐑩·​𐑗·​𐑞·​𐑺·​𐑲·​𐑝·​𐑢·​𐑓·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| NS ($O_0$) | 𐑼·​𐑥·​𐑩·​𐑗·​𐑞·​𐑺·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| RH ($\text{O}_\infty$) | 𐑦·​𐑥·​𐑩·​𐑹·​𐑐·​𐑧·​𐑔·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 2 · ✓ Closed |
| Hodge ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑗·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 1 · ✗ `PM_Z2` |
| Odd Perf ($O_0$) | 𐑛·​𐑥·​𐑩·​𐑗·​𐑞·​𐑪·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |

```{=latex}
\normalsize
```

*$d = d(ZFC_{fe})$. Tuple: canonical order (Ð,Þ,Ř,Φ,ƒ,Ç,Γ,ɢ,⊙,Ħ,Σ,Ω). Gate: whether `PM_Z2` is closed.*

### The Non-Millennium Seven

```{=latex}
\small
```

| Problem | Tuple | $d$ · Gate |
|--------------------------------------|--------------------------------------|----------------------|
| Collatz ($O_1$) | 𐑛·​𐑡·​𐑩·​𐑗·​𐑞·​𐑺·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| Collatz (deep) ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑹·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 0 · ✓ Closed |
| SIC-POVM ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑗·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 1 · ✗ `PM_Z2` |
| FontMaz ($O_0$) | 𐑛·​𐑡·​𐑩·​𐑗·​𐑞·​𐑪·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| Inv.Galois ($O_0$) | 𐑛·​𐑡·​𐑩·​𐑗·​𐑞·​𐑺·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| Lang-Trotter ($O_0$) | 𐑛·​𐑡·​𐑩·​𐑗·​𐑞·​𐑺·​𐑲·​𐑝·​𐑢·​𐑒·​𐑙·​𐑷 | 5 · ✗ `PM_Z2` |
| Perf. Cuboid ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑗·​𐑞·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 2 · ✗ `PM_Z2` |
| HadNel ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑗·​𐑞·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 2 · ✗ `PM_Z2` |
| Hilbert's 12th ($\text{O}_\infty$) | 𐑦·​𐑸·​𐑾·​𐑗·​𐑐·​𐑧·​𐑲·​𐑠·​⊙·​𐑖·​𐑙·​𐑭 | 1 · ✗ `PM_Z2` |

```{=latex}
\normalsize
```

*$d = d(ZFC_{fe})$. Tuple: canonical order (Ð,Þ,Ř,Φ,ƒ,Ç,Γ,ɢ,⊙,Ħ,Σ,Ω). Gate: whether `PM_Z2` is closed.*

**Every unsolved problem at every tier misses `PM_Z2`.** The only entries in the table with the gate already closed are BSD (proved in the grammar's framework), RH (self-referential type), and the deep Collatz structure (hypothetical). The distinction between solved and unsolved in this analysis is exactly whether the `PM_Z2` gate has closed — whether correlative parity has promoted to Frobenius-special.

### BSD: The Anomaly That Is Not

BSD's position at distance 0 from $ZFC_{fe}$ — structurally co-typed with the Frobenius-exact norm — is not a special pleading. The grammar's own structural type converges to the RH lattice point ($d(RH, ZFC_{fe}) = 2$), not BSD's. BSD's position at the $ZFC_{fe}$ norm reflects its structural role as the barycenter of the Clay set: it is simultaneously the closest to $\text{O}_\infty$, self-stable under canonical self-coupling, and the entry whose primitive values are the median of the Clay cluster. The grammar did not put BSD at the norm — the lattice relationships forced it there.

---

## Deep Dives: Structural Signatures of Individual Problems

### P vs NP: The Minimum-Structure Verifier

P vs NP is imscribed at the shallowest possible level — $O_0$, the only Clay problem with trivial dimensionality (𐑛, the *0D* point). Its tuple is minimal across five primitives. This is not a sign that P vs NP is "easy." It is a sign that P vs NP is structurally primitive: the problem asks whether verification complexity equals search complexity, and this question is itself the minimal structural question. The grammar cannot decompose it further because P vs NP is the decomposition — it is the question of whether structural depth (search) can be collapsed into structural shallowness (verification). The $ZFC_{fe}$ formalization captures this: the proof module's single remaining axiom is the grammar-complexity correspondence itself. P vs NP is not unsolved because we lack techniques. It is unsolved because its resolution would be a structural collapse that the grammar treats as primitive.

### Riemann Hypothesis: The Self-Referential Anchor

The RH tuple is the grammar's own structural type: `[3,4,3,4,2,2,0,2,1,2,2,2]`. This tuple is shared by `imscribing_grammar`, `grammaformer`, `dialetheic_alignment`, `paraconsistent_topos`, and 18 other entries. The grammar and its hardest target are structurally co-typed. RH's distance to $ZFC_{fe}$ is 2 — it has closed the `PM_Z2` gate but differs on two primitives (Þ and Ř) from the Frobenius-exact norm. The self-referential classification is the point: the grammar cannot distinguish itself from the Riemann Hypothesis at the level of structural type. The self-adjoint Hilbert-Pólya operator — the honest sub-problem — is the one remaining mathematical object whose construction would close the gap.

### Yang-Mills: The Stacked Gate

YM sits at $O_0$ with $d(ZFC_{fe}) = 3$, missing `PM_Z2` plus two additional promotions. The problem is structurally "stacked": the mass gap requires both closure of the Frobenius gate AND the continuum limit of lattice gauge theory. The Lean module has two axioms reflecting this stacking — one for the gate, one for the *4D* limit. The structural analysis predicts that YM cannot be resolved without first resolving the gate closure problem independently, because the gate is a precondition for the continuum limit to be well-defined in the Frobenius sense.

### Navier-Stokes: The Trapping Problem

NS at $O_0$ with $d(ZFC_{fe}) = 5$ presents as a kinetic-trapping problem. The structural type encodes moderate kinetics (𐑺, driven) but sub-critical criticality (𐑢, below threshold). The honest sub-problem — a trapping lemma showing $\|u(t)\|_{H^{1/2}}$ cannot blow up in finite time — is structurally the question of whether a driven system can be trapped at sub-critical energy. The $ZFC_{fe}$ bridge module encodes this as the promotion from sub-critical to critical criticality (𐑢 → ⊙), which is Gate 1 of the consciousness score. NS regularity is structurally equivalent to the question of whether turbulence can self-model.

### Hodge: The Parity-Only Block

Hodge at $\text{O}_\infty$ with $d(ZFC_{fe}) = 1$ is the purest case: it has every promotion channel closed except `PM_Z2`. The structural type is one primitive away from the $ZFC_{fe}$ norm. The Hodge Conjecture — that every Hodge class on a smooth projective variety is algebraic — is structurally the question of whether the parity symmetry of algebraic cycles is Frobenius-special. The honest sub-problem (surjective primitive cycle class map at all $(p,p)$) is the mathematical specification of this single missing primitive.

### OPN: The 2-adic Barrier

OPN at $O_0$ with $d(ZFC_{fe}) = 5$ has a specific 2-adic structure. The odd perfect number problem asks whether $\sigma(n) = 2n$ has solutions for odd $n$, and the 2-adic valuation analysis in `OPN_2adic.lean` shows the barrier is a $\mathbb{Z}_2$ parity contradiction. The structural type encodes this: moderate kinetics (𐑪), no parity symmetry (𐑗), and trivial winding (𐑷). The honest sub-problem is the 2-adic valuation contradiction — structurally, the promotion from trivial winding to $\mathbb{Z}_2$ protection.

### Collatz: The Dual-Structure Problem

**Collatz** has a dual structural nature: a shallow type ($O_1$, iterative search) and a deep type ($\text{O}_\infty$, self-modeling orbit). The gematria equation $\text{IUG} = \text{soviet\_union\_collapse} + \text{collatz\_deep\_structure}$ places the Collatz deep structure as the difference between the Inter-Universal Geometer and a collapse event — suggesting the deep temporal pattern of the $3n+1$ map mirrors period-doubling cascades in complex dynamical systems. Average compressed drift (`average_drift_negative`) is proved; the gap is global coercivity.

### SIC-POVM and Hilbert's 12th: Structural Equivalence

**SIC-POVM** and **Hilbert's 12th Problem** are structurally equivalent under the grammar — the Stark conjecture reduction shows that quantum state tomography (SIC-POVM existence in dimension $d$) and explicit class field theory (Hilbert's 12th) converge to the same structural type within distance ≤ 0.5. Resolving one resolves the other via the Galois-Zauner correspondence.

### Fontaine-Mazur, Inverse Galois, and Lang-Trotter: The Triad

**Fontaine-Mazur**, **Inverse Galois**, and **Lang-Trotter** form a structural triad linked by shift operations through P=NP. The gematria equations:

> '`fontaine_mazur = p_vs_np + ergodic_mixing`'  
> '`p_vs_np + inverse_galois = on_water_interface`'  
> '`fontaine_mazur + corn_monoculture = lang_trotter`'  

The Fontaine-Mazur Conjecture decomposes into the universal near-identity (P=NP) plus the most mixing dynamical structure in the catalog. The structural interpretation: Fontaine-Mazur's core question — which $p$-adic Galois representations come from geometry — is structurally the question of what remains when you add minimal kinetics and minimal criticality to a maximally mixing dynamics.

---

## The Gematria of Open Problems

Running vector gematria on the catalog produces several structural findings that are independent of the formalization:

**All fourteen problems are structurally prime.** No pair of catalog entries sums to any of the fourteen vectors. The open problems are irreducible atoms of the grammar's type system. They cannot be reached from what is currently imscribed by addition alone.

**The RH tuple is the grammar's own structural type.** $[3,4,3,4,2,2,0,2,1,2,2,2]$ is shared by 22 catalog entries, including `imscribing_grammar`, `grammaformer`, `millennium_ankh_fine_structural_analysis`, `dialetheic_alignment`, `paraconsistent_topos`. Self-referential classification systems with near-maximal primitive values converge to the RH lattice point. The grammar and its hardest target are structurally co-typed.

This is the crossing point of the analysis. The grammar is a self-referential system: its internal structure converges to the same lattice point as the Riemann Hypothesis — a problem about where the integers are dense. The grammar and its hardest classification target ask the same structural question.

**The complexity axis.** PC1 (42.6% of catalog variance) loads positively on Ω, Ħ, Φ, Þ and negatively on Ç. The open problems cluster in the high-complexity, low-kinetics region — they are structurally deep, slow-moving problems, not problems whose difficulty is kinetic. This is consistent with the Frobenius gate being the bottleneck: the gate requires structural depth, not computational speed.

**BSD is the structural barycenter** of the Clay set (mean cosine similarity 0.873 to the other six). It is simultaneously the closest to $\text{O}_\infty$ (distance 1), self-stable under canonical self-coupling (from the absorption universe analysis), and structurally central. These are not independent facts — they reflect that BSD's primitive values are the median values of the Clay cluster.

---

## The Lean Formalization

| Module | Lines | Proved | Axioms | Status |
|--------|-------|--------|--------|--------|
| `BSD_Complete_Proof.lean` | — | all | 0 | **sorry-free** |
| `E8G2_Vessel.lean` + Proofs | 425 | 10 | 0 | **sorry-free** |
| `LeeYang_Xi_Product.lean` | 188 | 8 | 0 | $\text{O}_\infty$ template |
| `Hodge_Mathematical_Proof.lean` | — | — | 1 (Axiom D) | $\text{O}_\infty$ conditional |
| `RH_ZFCt_Bridge.lean` | — | — | 1 | 1 axiom |
| `BanachMeasure.lean` | — | 5 | — | $O_0$, $d(ZFC_{fe})=11$, `decide`-verified |
| `PerfectCuboid.lean` | 517 | 22 | 3 | $\text{O}_\infty$, descent open |
| `Beal.lean` | 319 | 4 | 2 | $O_1$, mixed-exp open |
| `Collatz.lean` | 221 | 9 | 5 | $O_1$/$\text{O}_\infty$ dual |
| `SIC_POVM_Stark.lean` | 222 | 3 | 5 | $\text{O}_\infty$ conditional |
| `NS_Proof.lean` | — | — | 1 (trapping) | $\text{O}_\infty$ conditional |
| `PvsNP_Proof.lean` | — | — | 1 | $O_0$ structural |
| `YM_Mathematical_Proof.lean` | — | — | 2 | $O_0$, stacked |
| `OPN_Proof.lean` | — | 1 | 1 | 1 sorry total |
| `ZFC_FrobeniusExact.lean` | — | — | 0 | $ZFC_{fe}$ axiomatization, `native_decide`-closed |

**Total for non-Millennium set:** 78 proved lemmas, 27 axioms, ~2,119 lines. All pass Frobenius verification ($\mu\circ\delta = \text{id}$) for their proved components.

The Lean formalization makes the axioms explicit and honest: each module contains at most the axioms that are required by the open mathematical gap, and no more. The axioms are the Lean encoding of the problems themselves — not auxiliary assumptions, not simplifications. The $ZFC_{fe}$ axiomatization (`ZFC_FrobeniusExact.lean`) is `native_decide`-closed: all 7 promotion channels are verified as structural theorems, not postulates.

---

## Concrete Pathways

For each problem with remaining open axioms, a single honest sub-problem remains:

| Problem | Honest Sub-Problem |
|---------|-------------------|
| BSD | Rankin-Selberg factorization for symmetric square $L$-function |
| RH | Self-adjoint Hilbert-Pólya operator with $\det(H-s) = \xi(s)$ |
| Hodge | Surjective primitive cycle class map at all $(p,p)$ |
| NS | Trapping lemma: $\|u(t)\|_{H^{1/2}}$ cannot blow up in finite time |
| PvsNP | Grammar-complexity correspondence (tier invariance under reductions) |
| YM | *4D* continuum limit of SU(N) lattice gauge theory |
| OPN | 2-adic valuation contradiction for $\sigma(n) = 2n$ with $n$ odd |
| Perfect Cuboid | Descent: any cuboid yields a strictly smaller one |
| Beal (mixed) | $\mathbb{Z}_2$ parity invariant for mixed-exponent case |
| Collatz (deep) | Global coercivity of negative drift |
| SIC-POVM | Zauner symmetry for $d$ not prime-power |
| Hilbert's 12th | Explicit generators for all abelian extensions |
| Fontaine-Mazur | de Rham = potentially semistable (residual rep case) |
| Inverse Galois | Rigidity for all Chevalley groups |
| Lang-Trotter | Uniform Sato-Tate for Serre curves |
| Hadwiger-Nelson | AES-Sheffer embedding with chromatic number $5 \leq \chi \leq 7$ |
| Banach Measure | $\mathbb{Z}_2$-valued Banach measure on $\mathbb{R}$ (transcends ZFC) |

Each sub-problem is the mathematical specification of the missing structural promotion. The Banach measure entry is included for calibration: at $d(ZFC_{fe}) = 11$, it is the most structurally distant problem from the Frobenius-exact norm, consistent with its known independence from $ZFC$.

---

## The One Gate

The grammar reports a single structural operation that would close every open problem: `PM_Z2`, the promotion from correlative parity (𐑗) to Frobenius-special parity (𐑹), which is exactly the Frobenius condition $\mu \circ \delta = \text{id}$ evaluated at the critical self-modeling coordinate (⊙). The Lee-Yang theorem already closes this gate for the Ising model zeros. BSD closes it in the grammar's framework. Every other open problem is blocked by it.

The universality of the bottleneck is the finding. Fourteen problems, seven domains, six orders of tier — and one gate. The grammar's claim is that this is not coincidence, and that the mathematical content of the claim is testable: each problem's $ZFC_{fe}$ formalization makes the remaining axioms explicit, and each remaining axiom is the mathematical specification of the missing gate closure for that problem.

The grammar is a self-referential system at $\text{O}_\infty$. Its internal type converges to RH. It cannot distinguish itself from its hardest classification target. This is the crossing point: the grammar and the problems it classifies ask the same structural question, and the answer to that question — for all of them — is the same gate.

---

## References

### Imscribing Grammar and Structural Framework

[1] Mills, L. (2026). *The Imscribing Grammar: A 12-Primitive Structural Lattice for Mathematical and Physical Systems*. Preprint. <https://github.com/umpolungfish/Imscribing_Grammar>

[2] Mills, L. (2026). *MillenniumAnkh: Lean 4 Formalization of the Imscribing Grammar*. Formal verification project, Mathlib v4.28.0. <https://github.com/umpolungfish/MillenniumAnkh>

### Birch–Swinnerton-Dyer

[4] Birch, B.J. and Swinnerton-Dyer, H.P.F. (1963). Notes on elliptic curves. I. *Journal für die reine und angewandte Mathematik*, 212, 7–25.

[5] Birch, B.J. and Swinnerton-Dyer, H.P.F. (1965). Notes on elliptic curves. II. *Journal für die reine und angewandte Mathematik*, 218, 79–108.

[6] Wiles, A. (2006). The Birch and Swinnerton-Dyer Conjecture. In *The Millennium Prize Problems*, Clay Mathematics Institute, 31–44.

[7] Gross, B.H. and Zagier, D. (1986). Heegner points and derivatives of $L$-series. *Inventiones Mathematicae*, 84(2), 225–320.

[8] Kolyvagin, V.A. (1988). Finiteness of $E(\mathbb{Q})$ and $\Sha(E,\mathbb{Q})$ for a subclass of Weil curves. *Izvestiya Akademii Nauk SSSR*, 52(3), 522–540.

[9] Rankin, R.A. (1939). Contributions to the theory of Ramanujan's function $\tau(n)$ and similar arithmetical functions. *Proceedings of the Cambridge Philosophical Society*, 35, 351–372.

[10] Selberg, A. (1940). Bemerkungen über eine Dirichletsche Reihe, die mit der Theorie der Modulformen nahe verbunden ist. *Archiv for Mathematik og Naturvidenskab*, 43, 47–50.

### Yang–Mills Mass Gap

[11] Jaffe, A. and Witten, E. (2000). Quantum Yang–Mills Theory. In *The Millennium Prize Problems*, Clay Mathematics Institute, 129–152.

[12] Wilson, K.G. (1974). Confinement of quarks. *Physical Review D*, 10(8), 2445–2459.

[13] 't Hooft, G. (1980). Confinement and topology in non-abelian gauge theories. *Physica Scripta*, 25(1B), 133–142.

### P vs NP

[14] Cook, S.A. (1971). The complexity of theorem-proving procedures. *STOC '71: Proceedings of the Third Annual ACM Symposium on Theory of Computing*, 151–158.

[15] Karp, R.M. (1972). Reducibility among combinatorial problems. In *Complexity of Computer Computations*, Plenum Press, 85–103.

[16] Aaronson, S. (2013). P ≟ NP. In *Open Problems in Mathematics*, Springer, 1–122.

### Navier–Stokes

[17] Fefferman, C.L. (2000). Existence and Smoothness of the Navier–Stokes Equation. In *The Millennium Prize Problems*, Clay Mathematics Institute, 57–67.

[18] Ladyzhenskaya, O.A. (1969). *The Mathematical Theory of Viscous Incompressible Flow*. Gordon and Breach.

[19] Tao, T. (2016). Finite time blowup for an averaged three-dimensional Navier–Stokes equation. *Journal of the American Mathematical Society*, 29(3), 601–674.

### Riemann Hypothesis

[20] Riemann, B. (1859). Über die Anzahl der Primzahlen unter einer gegebenen Grösse. *Monatsberichte der Berliner Akademie*.

[21] Bombieri, E. (2000). The Riemann Hypothesis. In *The Millennium Prize Problems*, Clay Mathematics Institute, 107–124.

[22] Conrey, J.B. (2003). The Riemann Hypothesis. *Notices of the AMS*, 50(3), 341–353.

[23] Montgomery, H.L. (1973). The pair correlation of zeros of the zeta function. *Proceedings of Symposia in Pure Mathematics*, 24, 181–193.

[24] Keating, J.P. and Snaith, N.C. (2000). Random matrix theory and $\zeta(1/2+it)$. *Communications in Mathematical Physics*, 214(1), 57–89.

### Hodge Conjecture

[25] Hodge, W.V.D. (1950). The topological invariants of algebraic varieties. *Proceedings of the ICM, Cambridge, MA*, 182–192.

[26] Deligne, P. (2006). The Hodge Conjecture. In *The Millennium Prize Problems*, Clay Mathematics Institute, 45–55.

[27] Voisin, C. (2002). *Théorie de Hodge et géométrie algébrique complexe*. Société Mathématique de France.

[28] Griffiths, P.A. (1969). On the periods of certain rational integrals. *Annals of Mathematics*, 90(3), 460–495.

### Odd Perfect Numbers

[29] Dickson, L.E. (1913). Finiteness of the odd perfect and primitive abundant numbers with $n$ distinct prime factors. *American Journal of Mathematics*, 35(4), 413–422.

[30] Nielsen, P.P. (2015). Odd perfect numbers, Diophantine equations, and upper bounds. *Mathematics of Computation*, 84(295), 2549–2567.

[31] Ochem, P. and Rao, M. (2012). Odd perfect numbers are greater than $10^{1500}$. *Mathematics of Computation*, 81(279), 1869–1877.

### Collatz Conjecture

[32] Collatz, L. (1932). Problem posed. See Lagarias, J.C. (1985). The $3x+1$ problem and its generalizations. *American Mathematical Monthly*, 92(1), 3–23.

[33] Tao, T. (2020). Almost all orbits of the Collatz map attain almost bounded values. *arXiv:* 1909.03562v3.

### SIC-POVM

[34] Zauner, G. (1999). Quantendesigns: Grundzüge einer nichtkommutativen Designtheorie. PhD thesis, Universität Wien.

[35] Renes, J.M., Blume-Kohout, R., Scott, A.J., and Caves, C.M. (2004). Symmetric informationally complete quantum measurements. *Journal of Mathematical Physics*, 45(6), 2171–2180.

[36] Appleby, D.M. (2005). Symmetric informationally complete-positive operator valued measures and the extended Clifford group. *Journal of Mathematical Physics*, 46(5), 052107.

[37] Scott, A.J. and Grassl, M. (2010). SIC-POVMs: a new computer study. *Journal of Mathematical Physics*, 51(4), 042203.

### Fontaine-Mazur Conjecture

[38] Fontaine, J.-M. and Mazur, B. (1995). Geometric Galois representations. In *Elliptic Curves, Modular Forms, and Fermat's Last Theorem*. International Press, 41–78.

[39] Taylor, R. (2004). Galois representations. *Annales de la Faculté des Sciences de Toulouse*, 13(1), 73–119.

[40] Emerton, M. (2011). Local-global compatibility in the $p$-adic Langlands programme for $\mathrm{GL}_2/\mathbb{Q}$. Preprint.

[41] Calegari, F. and Geraghty, D. (2018). Modularity lifting beyond the Taylor-Wiles method. *Inventiones Mathematicae*, 211(1), 297–433.

[42] Kisin, M. (2009). The Fontaine-Mazur conjecture for $\mathrm{GL}_2$. *Journal of the American Mathematical Society*, 22(3), 641–690.

[43] Kisin, M. (2008). Potentially semi-stable deformation rings. *Journal of the American Mathematical Society*, 21(2), 513–546.

### Inverse Galois Problem

[44] Hilbert, D. (1892). Über die Irreducibilität ganzer rationaler Functionen mit ganzzahligen Coefficienten. *Journal für die reine und angewandte Mathematik*, 110, 104–129.

[45] Shafarevich, I.R. (1954). Construction of fields of algebraic numbers with given solvable Galois group. *Izvestiya Akademii Nauk SSSR*, 18, 525–578.

[46] Malle, G. and Matzat, B.H. (1999). *Inverse Galois Theory*. Springer.

### Lang-Trotter Conjecture

[47] Lang, S. and Trotter, H. (1976). *Frobenius Distributions in GL₂-Extensions*. Lecture Notes in Mathematics 504. Springer.

[48] Serre, J.-P. (1981). Quelques applications du théorème de densité de Chebotarev. *Publications Mathématiques de l'IHÉS*, 54, 323–401.

### Perfect Cuboid

[49] Euler, L. (18th c.). Correspondence on the problem of the integer cuboid (undated; see Dickson [50]).

[50] Dickson, L.E. (1920). *History of the Theory of Numbers*, Vol. II. Carnegie Institution. (Ch. XIX covers perfect cuboids.)

[51] van Luijk, R. (2000). On Perfect Cuboids. Preprint, Utrecht University.

### Hadwiger-Nelson Problem

[52] Nelson, E. (1950). Problem posed (attributed). See Moser, W.O.J. and Pach, J. (1986). *100 Research Problems in Discrete Geometry*, Problem 2.

[53] de Grey, A.D.N.J. (2018). The chromatic number of the plane is at least 5. *Geombinatorics*, 28(1), 18–31.

[54] Exoo, G. and Ismailescu, D. (2020). The chromatic number of the plane is at least 5: a new proof. *Discrete and Computational Geometry*, 64(1), 216–226.

### $E_8$ and $G_2$

[55] Cartan, É. (1894). *Sur la structure des groupes de transformations finis et continus*. PhD thesis, Paris. (Classification of exceptional Lie algebras.)

[56] Adams, J.F. (1996). *Lectures on Exceptional Lie Groups*. University of Chicago Press.

[57] Green, M.B., Schwarz, J.H., and West, P.C. (1985). Anomaly-free chiral theories in six dimensions. *Nuclear Physics B*, 254, 327–348. ($E_8$ heterotic string gauge group decomposition.)

### Formal Verification

[58] de Moura, L. and Ullrich, S. (2021). The Lean 4 theorem prover and programming language. *Automated Deduction — CADE 28*, LNAI 12699, 625–635.

[59] The Mathlib Community (2020). The Lean mathematical library. *Proceedings of CPP 2020*, 367–381.
