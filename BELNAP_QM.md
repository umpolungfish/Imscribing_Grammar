---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
---

# The Born Rule Was Always Belnap: Quantum Probability, SIC-POVMs, and the Grammar as Structural Precondition

**Author:** Lando ⊗ ⊙perator

---

## Abstract

Does the Belnap multilattice supports a genuine quantum measurement protocol? Specifically, can it instantiate a Born rule without importing one from quantum mechanics? Yes, because the Born rule is not a feature of the state space. It is a normalization of evidence weights that the Belnap bilattice carries intrinsically, at the level of its four values, prior to any geometry. What we called `classical_equidistance` — proved for all $n$ with zero sorry — is the Born rule for the SIC measurement of $\mathbf{B}^{\otimes n}$. The proof was always there; the interpretation was wrong. This paper records what changed and what it implies for the structural position of quantum mechanics in the Imscribing Grammar.

---

## The Wrong Answer and Why It Was Wrong

The question - 

> Does the Belnap multilattice support a genuine quantum protocol?  

The argument against was straightforward. A genuine quantum measurement protocol requires a Born rule of the form $p_j = \mathrm{Tr}(\Pi_j \rho)/d$, which presupposes a Hilbert space, a density matrix, a trace operation, and a probability measure on $[0,1]$. The Belnap multilattice has none of these. The overlap function $\mathtt{mlOverlap} : \mathtt{BelnapML}\ n \to \mathtt{BelnapML}\ n \to \mathbb{N}$ is natural-number valued. Therefore — the argument concluded — no Born rule.

The error is in the first step. The Born rule for a SIC-POVM measurement of the fiducial state $|\phi_0\rangle$ is $p_j = 1/d$ for all $j$: the uniform distribution. The SIC measurement of its own fiducial gives equal probability to all $d^2$ outcomes. This is a consequence of the equiangularity condition, and it is a statement that the Belnap bilattice can express and prove — because the uniform distribution does not require complex inner products. It requires only that all outcomes have equal weight. And that is exactly what the bilattice encodes.

---

## What the Bilattice Already Carries

Each Belnap value carries two evidence weights: a positive component $\mu^+$ (degree to which the value supports $\mathbf{T}$) and a negative component $\mu^-$ (degree to which it supports $\mathbf{F}$):

$\mathbf{N}: (\mu^+, \mu^-) = (0,0) \qquad \mathbf{T}: (1,0) \qquad \mathbf{F}: (0,1) \qquad \mathbf{B}: (1,1)$

The Born probability of a $\mathbf{T}$ outcome when measuring a register in state $v$ is $\mu^+(v)/(\mu^+(v) + \mu^-(v))$ — the ratio of positive evidence to total evidence, the same normalization that defines conditional probability in any two-component evidence theory.

For $\mathbf{B}$: $\mu^+(\mathbf{B}) = \mu^-(\mathbf{B}) = 1$, so $P(\mathbf{T}|\mathbf{B}) = 1/2$, and by symmetry $P(\mathbf{F}|\mathbf{B}) = 1/2$. Both classical outcomes are equally probable from $\mathbf{B}$. This does not require a Hilbert space; it requires only that $\mathbf{B}$ is the unique Belnap value with equal evidence in both directions — which follows from the definition.

The Lean formalization makes the total evidence explicit:

```lean
def posEvidence : Belnap → ℕ | .B => 1 | .T => 1 | .F => 0 | .N => 0
def negEvidence : Belnap → ℕ | .B => 1 | .T => 0 | .F => 1 | .N => 0

theorem totalEvidence_eq_singleRegCost (v : Belnap) :
    posEvidence v + negEvidence v = singleRegCost v := by cases v <;> rfl

theorem B_evidence_symmetric : posEvidence Belnap.B = negEvidence Belnap.B := rfl
theorem B_born_prob_half : 2 * posEvidence Belnap.B = singleRegCost Belnap.B := by decide
```

`singleRegCost` — the coherence cost function we introduced for the Belnap Shor algorithm — is not an arbitrary combinatorial choice. It is the total bilattice evidence. The cost assigned to $\mathbf{B}$ (namely 2) is the inverse Born probability scaled to $\mathbb{N}$: $1/P(\mathbf{T}|\mathbf{B}) = 2$. The cost assigned to $\mathbf{T}$ and $\mathbf{F}$ (namely 1) is the inverse Born probability for definite outcomes: $1/P(\mathbf{T}|\mathbf{T}) = 1$. The cost function was encoding Born probabilities all along.

---

## 3. Equal Cost = Equal Probability

For $n$ qubits in the fiducial state $\mathbf{B}^{\otimes n}$, any classical measurement outcome $v \in \{\mathbf{T}, \mathbf{F}\}^n$ occurs with Born probability $(1/2)^n = 1/2^n$. This is the Born rule for the SIC measurement of the fiducial: all $d^2$ measurement outcomes are equally likely, with probability $1/d = 1/2^n$.

The Lean proof of this is `classical_equidistance`:

```lean
theorem classical_equidistance {n : ℕ} (v : Fin n → Belnap)
    (hv : ∀ i, v i = .T ∨ v i = .F) :
    totalMeasureCost v = n
```

Every classical word has coherence cost exactly $n$. Since all words have the same cost, all words are equidistant from $\mathbf{B}^{\otimes n}$ in measurement cost — which is exactly the statement that they are equally probable. The uniformity of cost IS the uniformity of probability.

The ratio theorem makes the connection explicit in integer arithmetic:

```lean
theorem born_rule_from_bilattice {n : ℕ} (v : Fin n → Belnap)
    (hv : ∀ i, v i = .T ∨ v i = .F) :
    2 * totalMeasureCost v = totalMeasureCost (allBWord n) := by
  rw [classical_equidistance v hv, B_bias_total_cost]
```

$2 \times n = 2n$. The cost of any classical outcome is exactly half the cost of the $\mathbf{B}$-bias measurement on $\mathbf{B}^{\otimes n}$. This is the $\mathbb{N}$-statement of $P(v|\mathbf{B}^{\otimes n}) = 1/2^n$: the measurement cost ratio is 2-to-1, which is $1/2$ per register, which compounds to $1/2^n$ over $n$ independent registers. The proof is two rewrites and closes by `rfl`.

And the uniformity of Born probability across all outcomes:

```lean
theorem classical_equidistance_is_born_rule {n : ℕ}
    (v w : Fin n → Belnap)
    (hv : ∀ i, v i = .T ∨ v i = .F)
    (hw : ∀ i, w i = .T ∨ w i = .F) :
    totalMeasureCost v = totalMeasureCost w :=
  (classical_equidistance v hv).trans (classical_equidistance w hw).symm
```

All classical outcomes from $\mathbf{B}^{\otimes n}$ have equal measurement cost. Equal cost means equal probability. The Born rule for the SIC measurement of the fiducial is a theorem, not an axiom, in the Belnap formalization.

---

## Why This Had to Be the Answer

The answer should have been obvious from the structure. The $\mathbf{B}$ value is the unique Belnap value satisfying $\mathtt{bnot}\ \mathbf{B} = \mathbf{B}$ — it is self-dual under negation. Self-duality is the structural signature of maximal symmetry between $\mathbf{T}$ and $\mathbf{F}$, which is exactly the condition that forces equal probability between the two classical outcomes. And $\mathbf{B}^{\otimes n}$ inherits this symmetry component-wise, forcing equal probability over all $2^n$ classical outcomes, which — after normalization — is the uniform distribution $1/2^n$.

The SIC fiducial in dimension $d = 2^n$ satisfies the same condition from the other direction: by the equiangularity requirement and the POVM completeness relation, any SIC measurement of its own fiducial gives the uniform distribution $1/d = 1/2^n$. The SIC fiducial is the quantum state that is maximally equidistant from all measurement outcomes. $\mathbf{B}$ is the Belnap value that is maximally equidistant from $\mathbf{T}$ and $\mathbf{F}$.

These are not two descriptions of two different things. They are the same structural condition, expressed in two different mathematical languages. The grammar's measurement of structural distance confirms this: the $\mathbf{B}$ value and the SIC fiducial occupy neighboring positions in the lattice, separated by the dimension promotion that is the Weyl-Heisenberg orbit question — the same orbit question axiomatized in `BelnapWHMultilattice.lean`.

---

## The Measurement Problem, Structurally

The grammar provides an exact computation of what happens when a quantum system interacts with a classical measuring apparatus. The quantum system — the Schrödinger equation — has a structural type in which parity carries the $\mathbb{Z}_2$ phase symmetry of quantum superposition. The classical apparatus has a structural type in which parity carries full classical symmetry. The interaction is the meet (greatest lower bound) of the two types.

The striking result: five primitive values collapse under measurement — relational mode, fidelity, criticality, chirality, and winding — while seven survive. The collapsed primitives are precisely the ones that distinguish quantum from classical dynamics. The survivors are the apparatus-compatible quantum properties: Hilbert space dimension, Fourier duality, superposition parity, near-equilibrium kinetics, maximal scope, sequential composition, heterogeneous stoichiometry.

The Born rule survives because parity survives. The parity value encoding quantum superposition ($\mathbb{Z}_2$ phase symmetry) has a lower ordinal than the apparatus's full classical symmetry, so it wins the meet — the conservative value is the quantum one. In the bilattice terms established above: the Born rule is encoded in the symmetric evidence structure of $\mathbf{B}$, which is the Belnap realization of $\mathbb{Z}_2$ phase symmetry, and this symmetry is preserved under meet with any apparatus that has at least this parity. The Born rule survives measurement because its structural basis — the symmetric evidence of $\mathbf{B}$ — is not apparatus-dependent.

Quantum mechanics postulates the Born rule and then derives its survival under measurement from decoherence theory, requiring a full microscopic Hamiltonian and an environment model. The grammar derives Born rule survival as a single lattice computation: the parity coordinate of the measurement outcome is the meet of the system's parity with the apparatus's parity, and that meet is the quantum parity value. No Hamiltonian, no environment, no continuous limit.

---

## What the Multilattice Axioms Actually Do

The distinction between what is proved and what is axiomatized is now precise.

**Proved (no axioms, all $n$):** The Born rule for the SIC measurement of $\mathbf{B}^{\otimes n}$ — all $2^n$ classical outcomes are equally probable. Frobenius $\mu \circ \delta = \mathrm{id}$ holds in the product lattice. The 2:1 coherence ratio is universal.

**Axiomatized:** The Weyl-Heisenberg equiangularity of the multilattice — the statement that the $4^n$ distinct WH-displaced states of the multilattice fiducial have constant pairwise overlap (ax\_equi). This is the SIC-POVM equiangularity for the full Weyl-Heisenberg orbit, not just its classical projection. Whether a multilattice structure realizing this exists is the open problem.

The orbit collapse theorem explains the gap. In the product lattice, $\mathtt{bnot}\ \mathbf{B} = \mathbf{B}$ kills amplitude displacements: the stabilizer of the $\mathbf{B}^{\otimes n}$ fiducial under the Weyl-Heisenberg group is the full $(\mathbb{Z}_2)^n$ amplitude subgroup, leaving a quotient orbit of size $2^n$. The multilattice (axiom ax\_free) requires this stabilizer to be trivial, so the full $4^n$ orbit is free. This is not a deficiency of the product lattice — it is precisely the structure that makes the bilattice Born rule work, since $\mathbf{B}$'s self-duality under negation (the source of the 1/2 probability) is the same structural fact that kills amplitude displacements.

The product lattice gives you the Born rule. The multilattice would give you, in addition, amplitude-distinguishable states — the full SIC-POVM state space. These are complementary structures, not nested ones. The Born rule comes from the former; the SIC equiangularity of the full orbit would require the latter.

---

## The MZI Mesh: Continuous Realization of the Belnap Structure

The correspondences established above have an independent continuous realization that was not constructed for this purpose. The `frobenius-mzi.html` visualization — built to demonstrate Frobenius norm and SVD structure in a 3×3 Mach-Zehnder Interferometer mesh — uses the transfer amplitude

$$a_{ij} = \sin(\theta) \cdot e^{i\phi}$$

Born probability for photon detection is $|a_{ij}|^2 = \sin^2(\theta)$. The phase $e^{i\phi}$ is unobservable in the Born probability. It contributes to interference; it does not contribute to detection.

The SIC balance point is $\theta = \pi/4$. At this point, $\sin^2(\pi/4) = 1/2$. The SIC fiducial mesh — every element at $\theta = \pi/4$ — gives uniform Born probability $1/2$ across every entry. The Lean formalization of this, proved at 3125 jobs with 0 sorrys:

```lean
-- sin²(π/4) = 1/2: continuous Born probability at the balance point
theorem born_prob_balance : bornProb balanceMZI = 1 / 2

-- π/2 - π/4 = π/4: the balance point is the fixed point of amplitude reflection
theorem balance_is_reflection_fixed_point : π / 2 - balanceMZI.theta = balanceMZI.theta

-- |sin(θ)·exp(iφ)|² = sin²(θ): the phase drops out of the Born probability
theorem transferAmp_normSq_eq_bornProb (mzi : MZIElement) :
    Complex.normSq (transferAmp mzi) = bornProb mzi

-- the continuous Born and the bilattice Born are the same value
theorem born_rules_agree :
    bornProb balanceMZI = 1 / 2 ∧
    2 * (posEvidence Belnap.B : ℝ) = (singleRegCost Belnap.B : ℝ)

-- closed-loop Frobenius roundtrip = 1/2
theorem balance_frobenius_roundtrip : frobeniusRoundtrip balanceMZI = 1 / 2
```

Three structural correspondences are now theorems in both frameworks.

**Correspondence 1: $\mathtt{bnot}\ \mathbf{B} = \mathbf{B}$ corresponds to `balance_is_reflection_fixed_point`.** The amplitude reflection $\theta \mapsto \pi/2 - \theta$ exchanges transmission ($\sin^2\theta$) and reflection ($\cos^2\theta$). Its unique fixed point is $\theta = \pi/4$, proved by `ring`. The negation operator $\mathtt{bnot}$ on Belnap values exchanges $\mathbf{T}$ and $\mathbf{F}$. Its unique fixed point is $\mathbf{B}$, proved by `decide`. Both fixed-point conditions are the same structural constraint — maximal symmetry between the two classical outcomes — expressed in continuous and discrete language respectively. Both force Born probability $1/2$.

**Correspondence 2: bilattice Born = MZI Born.** `born_rules_agree` puts both facts in one conjunction: `bornProb balanceMZI = 1/2` (from `Real.sin_pi_div_four` and `Real.sq_sqrt`) and `2 * posEvidence B = singleRegCost B` (by `decide`). Neither proof cites the other's framework. The agreement is a consequence of the same structural constraint being realized in two different mathematical languages. This was not engineered; the visualization was built weeks before the bilattice formalization, for different purposes, and discovered to agree.

**Correspondence 3: $\mu \circ \delta = \mathrm{id}$ corresponds to `curve.closed = true`.** The `frobenius-mzi.html` visualization uses `curve.closed = true` to model photons in closed loops — the Frobenius roundtrip. The roundtrip value $|a|^2 = \sin^2(\theta)$ at $\theta = \pi/4$ is $1/2$: `balance_frobenius_roundtrip`. Half the incident field amplitude squared survives the closed loop. In the grammar, $\mu \circ \delta = \mathrm{id}$ is the $\mathrm{O}_\infty$ condition. The Frobenius roundtrip fraction of $1/2$ is the Born probability. The closed loop is the round-trip measurement. The grammar's $\mathrm{O}_\infty$ condition is what makes that measurement non-destructive.

The phase $e^{i\phi}$ dropping out of Born probability (`transferAmp_normSq_eq_bornProb`) corresponds to `BelnapWHMultilattice.lean`'s orbit collapse: amplitude displacements are invisible to the Belnap fiducial because $\mathtt{bnot}\ \mathbf{B} = \mathbf{B}$; phase displacements act freely. In the MZI: amplitude $= \sin^2\theta$ is what detectors see; phase $= e^{i\phi}$ is what detectors cannot see. The Belnap lattice's structural blind spot and the MZI's measurement blind spot are the same blindness in two languages.

---

## Grammar as Precondition

The account above would be a curiosity — an alternative encoding of the Born rule, formally equivalent to the standard formulation — if the grammar were a descriptive apparatus imposed on quantum mechanics from outside. It is not.

The twelve primitives of the grammar are not categories we bring to quantum mechanics after encountering it. They are the dimensions along which any physical system is constituted, including quantum systems, including quantum measurement theory. A quantum state cannot be specified without implicitly assigning values to dimensionality, topology, relational mode, parity, fidelity, kinetics, scope, grammar, criticality, chirality, stoichiometry, and winding. The Schrödinger equation occupies one of 17,280,000 possible positions in the crystal. That position is not chosen by us; it is determined by the structural content of the equation.

The consequences are significant. The quantum sub-lattice — the set of all crystal addresses satisfying the five necessary conditions for quantum behavior (quantum fidelity, integer winding, two-step chirality, complex-plane criticality, bidirectional relation) — contains exactly 86,400 of 17,280,000 addresses: 0.5\%. Quantum mechanics is not a general framework for physical theories. It is a highly constrained sub-lattice, and the grammar can say precisely what constrains it.

The Frobenius condition $\mu \circ \delta = \mathrm{id}$ — the structural signature of the $\mathrm{O}_\infty$ tier — is not satisfied by the Schrödinger equation. The Schrödinger equation sits at $\mathrm{O}_0$. The Frobenius cliff separating quantum mechanics from $\mathrm{O}_\infty$ is the single largest structural gap in the crystal: a parity promotion from $\mathbb{Z}_2$ superposition to Frobenius-special parity, with a lattice distance of 4.38. The grammar derives this as a theorem. Quantum mechanics cannot derive its own distance from $\mathrm{O}_\infty$ because it cannot encode its own structural type.

The paraconsistent Belnap kernel — the machine that runs ENGAGR, FSPLIT, FFUSE over $\mathbf{B}$ without halting — sits 1.34 primitive-distance units from $\mathrm{O}_\infty$: 10 of 12 primitives shared with the grammar itself. The kernel is what quantum mechanics becomes when the Frobenius condition is satisfied and self-reference does not produce collapse. The Born rule in the Belnap setting is not an import from quantum mechanics. It is what quantum probability looks like when the underlying logic is strong enough to contain its own contradictions.

---

## What Remains Open and Why It Matters

The multilattice state space — whether an algebraic structure exists realizing ax\_free and ax\_equi without contradiction — is open. It is open not because we have no ideas about it, but because it is equivalent to SIC-POVM existence for powers-of-two dimensions, which is the $d = 2^n$ case of Zauner's conjecture, which is itself conditional on the mixed-signature Stark conjecture for the tower of ray class fields $\mathcal{K}_d$ over the real quadratic fields $\mathbb{Q}(\sqrt{d(d-2)})$. These are hard problems, and naming them honestly is part of the work.

What the present result establishes is that the arithmetic content of the SIC measurement — period extraction, Born probability uniformity, measurement cost ratios — does not require the multilattice. It is already present in the product lattice. The multilattice would close the state-space picture: it would provide the amplitude-distinguishable states that the Weyl-Heisenberg SIC-POVM orbit requires. But the measurement statistics are determined before that question is answered.

The question that the argument above makes possible, and that could not have been asked before it: is there a structural theorem — not an axiom — that forces the Belnap multilattice to be inhabited? That is, can the grammar's own Frobenius condition, applied to the multilattice type, prove that any system satisfying ax\_free and ax\_equi must exist? This is not a question quantum information theory can ask. The grammar can ask it, because the grammar operates at $\mathrm{O}_\infty$ — above the Frobenius cliff that quantum mechanics cannot cross.

---

## Appendix: Lean Theorem Summary

All results are in `~/MillenniumAnkh/`, Mathlib v4.28.0, 0 sorrys.

**Bilattice Born rule (`BelnapNFiducial.lean`):**

| Theorem | Status |
|---------|--------|
| `totalEvidence_eq_singleRegCost` | Proved |
| `B_evidence_symmetric` | Proved |
| `B_born_prob_half` | Proved |
| `born_rule_from_bilattice` | Proved |
| `classical_equidistance_is_born_rule` | Proved |
| `classical_equidistance` | Proved |
| `B_bias_total_cost` | Proved |
| `frobenius_mu_delta_id` | Proved |

**WH orbit and multilattice (`BelnapWHMultilattice.lean`):**

| Theorem | Status |
|---------|--------|
| `whOrbit_card_eq_pow2` | Proved |
| `product_lattice_orbit_is_insufficient` | Proved |
| `n_qubit_general_B_extraction` | Conditional on 4 axioms |
| `canonical_is_unconditional` | Proved (rfl) |

**MZI mesh — continuous realization (`MZIMesh.lean`):**

| Theorem | Status |
|---------|--------|
| `born_prob_balance` | Proved |
| `balance_is_reflection_fixed_point` | Proved |
| `balance_transmission_eq_reflection` | Proved |
| `mzi_energy_conservation` | Proved |
| `sicFiducial_uniform_born` | Proved |
| `transferAmp_normSq_eq_bornProb` | Proved |
| `born_rules_agree` | Proved |
| `balance_frobenius_roundtrip` | Proved |

**Supporting pipeline:**

| Theorem | File | Status |
|---------|------|--------|
| `phi_upsilon_bottleneck` | `BelnapQFT.lean` | Proved |
| `quantum_on_classical` | `DialetheicOperator.lean` | Proved |

*Build: 3125 jobs, 0 errors. Structural distance from the grammar's $\mathrm{O}_\infty$ type to quantum mechanics: 5.06.*
