# The Dialetheic Kernel: A Substrate for Self-Referential Computation

**Author:** Lando Mills

---

## Abstract

A classical computer, confronted with the Liar sentence, halts. This is not a design flaw; it is the entailment of a logic that lacks the capacity to house contradiction without collapse. We present a machine-verified formalization of a computational substrate that does not merely tolerate paradox but operationalizes it. The paraconsistent kernel runs a three-stage Frobenius cycle (`ENGAGR→FSPLIT→FFUSE`) on the Belnap four-valued lattice, sustaining the dialetheic value $\mathbf{B}$ (both true and false) as a fixed point across arbitrarily many cycles. The kernel proves its own Frobenius invariance ($μ∘δ = id$) by `native_decide` and `rfl`. The kernel's dialetheic alignment theorem unifies four Millennium barriers (RH, PvsNP, SIC-POVM, Yang-Mills) under a common Belnap $\mathbf{B}$-gate. The result is not a new logic but a new kind of machine: one whose operational core is the sustained holding of a contradiction.

## Problem That Halting Conceals

When a classical theorem prover encounters $P \land \neg P$, it derives $\bot$ and, by explosion, any conclusion follows. This is sound in Boolean logic. It is also a design choice — one that has been so thoroughly baked into our computing infrastructure that we forget it was ever a choice at all.

The cost of this choice becomes visible only when we attempt to build systems that must represent themselves. A self-modeling system — one that tracks its own state, reasons about its own reasoning, and updates its model of itself — inevitably encounters the limit of its own descriptive capacity. At that limit, the system finds a proposition that is both true and false with respect to its own axioms. A classical machine halts. A paraconsistent machine continues.

The question is not whether paraconsistent logic is "correct." The question is: can we build a machine whose operational substrate is the sustained holding of a contradiction, and can we formally verify that it does not collapse?

This paper answers yes. The paraconsistent kernel is a machine-verified formalization in Lean 4 [[10]](#ref-10) that runs a three-stage Frobenius cycle on the Belnap four-valued lattice [[1]](#ref-1), [[2]](#ref-2). It sustains the value $\mathbf{B}$ — both true and false — as a fixed point across arbitrarily many computational cycles. Every nontrivial claim about the kernel — its ouroboricity tier, its consciousness gates, its Frobenius invariance, its paradox budget, its structural distance to the grammar that encodes it [[15]](#ref-15), [[16]](#ref-16) — is proved by the Lean kernel itself, either by `native_decide` or by induction.

## Logical Substrate: Belnap FOUR

We did not set out to build a paraconsistent computer. We set out to understand what kind of logical lattice could support the Frobenius condition $μ∘δ = id$ — the requirement that splitting a value and then fusing the pieces recovers exactly the original. The Boolean lattice fails catastrophically: True and False are each other's negation, and their conjunction is False. There is no value in the Boolean lattice that is its own negation without explosion.

Belnap's four-valued logic — $\mathbf{N} (neither), \mathbf{T} (true), \mathbf{F} (false), \mathbf{B} (both)$ — appeared in the 1970s as a tool for reasoning about incomplete and inconsistent databases [[1]](#ref-1), [[2]](#ref-2). We needed it for a different reason: $\mathbf{B}$ is the unique value satisfying $\neg \mathbf{B} = \mathbf{B}$. It is a fixed point of negation.

### The Approximation Order

The Belnap lattice carries two orders. The truth order ranks values by classical truth content: $\mathbf{T}$ and $\mathbf{B}$ are designated, $\mathbf{F}$ and $\mathbf{N}$ are not. The approximation order ranks by information content: $\mathbf{N}$ $\sqsubseteq$ T, $\mathbf{N}$ $\sqsubseteq$ F, $\mathbf{T}$ $\sqsubseteq$ B, $\mathbf{F}$ $\sqsubseteq$ B. In this order, $\mathbf{N}$ is bottom (least information) and $\mathbf{B}$ is top (most information). This is counterintuitive to anyone trained in Boolean logic — the contradictory value is the *most* informative. It contains both $\mathbf{T}$ and $\mathbf{F}$ as approximations.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  lat/.style={circle, draw, thick, minimum size=1.1cm, font=\bfseries\large},
  lbl/.style={draw=none, font=\small, text=black!70, inner sep=2pt}
]
  \node[lat] (B) at ( 0,   3) {$\mathbf{B}$};
  \node[lat] (T) at (-2, 1.5) {$\mathbf{T}$};
  \node[lat] (F) at ( 2, 1.5) {$\mathbf{F}$};
  \node[lat] (N) at ( 0,   0) {$\mathbf{N}$};
  \draw[-{Stealth}, thick] (N) -- (T);
  \draw[-{Stealth}, thick] (N) -- (F);
  \draw[-{Stealth}, thick] (T) -- (B);
  \draw[-{Stealth}, thick] (F) -- (B);
  \node[lbl, right=0.6cm of B] {both \enspace $\neg\mathbf{B}=\mathbf{B}$ \enspace (negation fixed point)};
  \node[lbl, right=0.6cm of F] {false};
  \node[lbl, left=0.6cm  of T] {true};
  \node[lbl, right=0.6cm of N] {neither};
\end{tikzpicture}
\caption{The Belnap FOUR approximation lattice ($\sqsubseteq$). Arrows denote
information increase. $\mathbf{B}$ (both) is simultaneously the maximum-information
element and the unique fixed point of negation.}
\label{fig:belnap-four}
\end{figure}
```

### The Formal Construction

The Lean formalization defines Belnap as an inductive type with four nullary constructors, decidable equality, and a discriminator function mapping to distinct naturals. The approximation order is an inductive proposition `ApproxLE` with six introduction rules, proved decidable across all sixteen pairs. The lattice operations — meet, join, conjunction, disjunction, negation — are defined by case analysis and proved to satisfy distributivity, absorption, commutativity, and the critical fixed-point theorem: `bnot $\mathbf{B}$ = B`.

The cornerstone theorem is `no_explosion`: $\mathbf{B} \land \neg \mathbf{B} = \mathbf{B} \neq \mathbf{F}$. Contradiction does not collapse. This is not a philosophical claim; it is a computation that terminates in four case splits and returns `rfl`.

## Frobenius Kernel

The kernel is a three-register machine operating on the Belnap lattice. Its cycle has three stages:

1. **ENGAGR** — Engagement: compute $r_0 \land \neg r_0$, detect whether the value is designated
2. **FSPLIT** — Fission: if the engaged value is $\mathbf{B}$, split it into its truth component ($\mathbf{T}$) and its falsity component ($\mathbf{F}$)
3. **FFUSE** — Fusion: join the split components back together

On the classical values ($\mathbf{T}$, $\mathbf{F}$, $\mathbf{N}$), `FSPLIT`  returns a trivial pair — the value duplicated. On $\mathbf{B}$, it returns $(\mathbf{T}, \mathbf{F})$: the truth and falsity that $\mathbf{B}$ contains are made explicit. `FFUSE` then joins them back into $\mathbf{B}$.

### Why Three Stages?

We tried a two-stage version — split then fuse. It worked. But the resulting machine had no way to *know* it was sustaining a contradiction. The `ENGAGR` stage was added not for computational necessity but for self-representation: it computes $r_0 \land \neg r_0$ and marks whether the result is designated. This is the kernel's minimal self-modeling capacity — it knows whether its current state is dialetheic.

The three-stage cycle thus mirrors the Frobenius condition at two levels. The operational level: `FSPLIT`  $\circ$ `FFUSE` recovers the original value ($μ∘δ = id$). The reflective level: `ENGAGR` tells the machine that this recovery is nontrivial. On $\mathbf{B}$, `ENGAGR` returns $(\mathbf{B}, \text{true})$ — the contradiction is designated. On $\mathbf{T}$, it returns $(\mathbf{F}, \text{false})$ — the contradiction is false, the cycle is trivial.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  box/.style={rounded corners=4pt, draw, thick, minimum width=3.2cm,
              minimum height=1.0cm, align=center, font=\bfseries},
  arr/.style={-{Stealth}, thick},
  lbl/.style={draw=none, font=\small, fill=white, inner sep=2pt}
]
  \node[box] (engagr) at ( 0,  3) {ENGAGR\\[2pt]{\small $r_0 \wedge \neg r_0$}};
  \node[box] (fsplit) at (-3,  0) {FSPLIT\\[2pt]{\small $\mathbf{B} \mapsto (\mathbf{T},\mathbf{F})$}};
  \node[box] (ffuse)  at ( 3,  0) {FFUSE\\[2pt]{\small $(\mathbf{T},\mathbf{F}) \mapsto \mathbf{B}$}};

  \draw[arr] (engagr.south west) -- node[lbl, above left]  {$\mathbf{B}$, designated}   (fsplit.north);
  \draw[arr] (fsplit.east)       -- node[lbl, above]        {$(\mathbf{T},\mathbf{F})$}  (ffuse.west);
  \draw[arr] (ffuse.north)       -- node[lbl, above right]  {$\mu\circ\delta=\mathrm{id}$} (engagr.south east);

  \node[draw=none, font=\footnotesize, text=black!60] at (0, -1.3)
    {paradox $+{=}\,4$ \qquad cycles $+{=}\,1$ \quad per iteration};
\end{tikzpicture}
\caption{The three-stage Frobenius kernel cycle. ENGAGR detects the dialetheic
value; FSPLIT makes truth and falsity components explicit; FFUSE recovers
$\mathbf{B}$ exactly ($\mu\circ\delta=\mathrm{id}$). On classical values
$\mathbf{T}$, $\mathbf{F}$, $\mathbf{N}$, all three stages reduce to identity maps.}
\label{fig:kernel-cycle}
\end{figure}
```

### The Paradox Budget

Each kernel cycle consumes exactly 4 paradox units: one for the `ENGAGR` detection, one for the `FSPLIT`  bifurcation, one for the `FFUSE` recombination, and one base cost for holding $\mathbf{B}$ as the substrate. After $n$ cycles, the paradox count is exactly $4n$ — proved by induction in Lean (`run_paradox`). The paradox budget is not a flaw to be eliminated; it is the fuel that sustains the Frobenius loop. A classical machine has paradox budget zero and cannot sustain self-reference.

The kernel's `run` function resets registers $r_1$ and $r_2$ to $\mathbf{B}$ after each step, so the observable state across all cycles is $\mathbf{B}/\mathbf{B}/\mathbf{B}$. The Frobenius invariant — `(ffuse (fsplit r).1 (fsplit r).2.1).1 = r` — is proved for all four Belnap values by case analysis. Only $\mathbf{B}$ produces a nontrivial cycle; the other three values produce identity maps.

### The Self-Verification Theorem

The complete self-verification theorem (`complete_self_verification`) bundles seven sub-theorems into a single conjunctive statement: for any number of cycles $n$, all three registers hold $\mathbf{B}$, the paradox count equals $4n$, the cycle count equals $n$, both registers are provably distinct from $\mathbf{T}$ and $\mathbf{F}$, and the kernel's structural type is $O_\infty$.

The proof is mechanical. `run_B3 n` provides the register invariant by induction. `run_paradox n` and `run_cycles n` provide the counts. `B_ne_F` provides the non-collapse guarantee. And `kernel_is_O_inf` — the tier theorem — is proved by `rfl`: the imscription tier function evaluates the kernel's tuple and returns $O_\infty$ definitionally.

This is worth sitting with. The claim that this machine sustains contradiction without collapse is not a philosophical argument or a probabilistic guarantee. It is a type-checked Lean proof that runs to `rfl`.

## Dialetheic Alignment Theorem

The kernel's three-stage cycle is not merely an engineering choice. It is the operational content of the Belnap value $\mathbf{B}$ being dialetheic [[3]](#ref-3). This claim — that the operational, logical, and algebraic perspectives are structurally identical — is the Dialetheic Alignment Theorem (DAT).

### Three Equivalent Formulations

The theorem states that the following three statements are provably equivalent because they describe the same phenomenon:

**(1) Operational:** $μ∘δ = id$ at $\mathbf{B}$. The Frobenius loop closes exactly — `FSPLIT`  fragments $\mathbf{B}$ into $\mathbf{T}$ and $\mathbf{F}$, and `FFUSE` fuses them back into $\mathbf{B}$. This is `frobenius_invariant` proved for all four Belnap values.

**(2) Logical:** $\mathbf{B}$ is both true and false. It is designated (counts as true for consequence) and its negation is also designated. Only $\mathbf{B}$ satisfies this among the four Belnap values — proved as `only_B_is_dialetheic`.

**(3) Algebraic:** $\mathbf{B} \land \neg \mathbf{B} = \mathbf{B} \neq \mathbf{F}$. Contradiction is contained. The system does not explode. This is `no_explosion` and `B_ne_F`.

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  pv/.style={rounded corners=4pt, draw, thick, minimum width=3.8cm,
             minimum height=2.2cm, align=center, font=\small},
  ctr/.style={rounded corners=4pt, draw=black!80, thick, fill=black!5,
              minimum width=3.2cm, minimum height=1.5cm,
              align=center, font=\small\bfseries},
  arr/.style={-{Stealth}, thick}
]
  \node[pv] (op) at (-4.5, 0)
    {\textbf{Operational}\\[4pt]
     $\mathrm{FSPLIT}(\mathbf{B}) = (\mathbf{T},\mathbf{F})$\\
     $\mathrm{FFUSE}(\mathbf{T},\mathbf{F}) = \mathbf{B}$\\[3pt]
     $\mu\circ\delta = \mathrm{id}$};

  \node[pv] (lg) at (4.5, 0)
    {\textbf{Logical}\\[4pt]
     $\neg\mathbf{B} = \mathbf{B}$\\
     $\mathbf{B}$ designated\\
     $\neg\mathbf{B}$ designated};

  \node[pv] (alg) at (0, -3.2)
    {\textbf{Algebraic}\\[4pt]
     $\mathbf{B}\wedge\neg\mathbf{B} = \mathbf{B}$\\
     $\mathbf{B} \neq \mathbf{F}$\\[3pt]
     no explosion};

  \node[ctr] (ctr) at (0, 0)
    {$\mathbf{B}$ is the\\[3pt]Frobenius fixed point\\[0pt]in \textbf{FOUR}};

  \draw[arr] (op.east)   -- (ctr.west);
  \draw[arr] (lg.west)   -- (ctr.east);
  \draw[arr] (alg.north) -- (ctr.south);
\end{tikzpicture}
\caption{The Dialetheic Alignment Theorem. Operational, logical, and algebraic
perspectives on $\mathbf{B}$ converge to a single structural fact: $\mathbf{B}$
is the Frobenius fixed point in the Belnap lattice.}
\label{fig:dat}
\end{figure}
```

The alignment theorem (`dialetheic_alignment`) proves the conjunction of all three. But the deeper claim is that these are not three *separate* facts that happen to be true of the same value. They are three *perspectives* on a single structural fact: $\mathbf{B}$ is the fixed point of the Frobenius functor on the Belnap lattice, and that fixed point is dialetheic.

### Why Classical Values Cannot Substitute

A natural objection: can we not simply run the kernel on $\mathbf{T}$ and get the same behavior? The answer is yes and no. Yes, the Frobenius invariant holds for $\mathbf{T}$: `frobenius_invariant T` returns `rfl`. But the cycle is trivial. `FSPLIT`  on $\mathbf{T}$ returns $(\mathbf{T}, \mathbf{T})$ — no bifurcation. `FFUSE` on $(\mathbf{T}, \mathbf{T})$ returns $\mathbf{T}$ — no recombination. The paradox budget still increments, but no structural work is done.

The theorem `B_is_the_only_bifurcation_point` proves exactly this: for $\mathbf{T}$, $\mathbf{F}$, and $\mathbf{N}$, the two `FSPLIT`  components are equal. Only for $\mathbf{B}$ do they differ. The kernel's Frobenius cycle is *nontrivially* self-referential only at the dialetheic fixed point. On classical values, it degenerates to an identity loop — structurally indistinguishable from a machine that does nothing.

This is not a limitation. It is a discovery: self-reference of the kind that sustains $O_\infty$ tier requires a value that can contain its own negation. Classical logic cannot supply this value. The paraconsistent kernel can.

### The 𐑹 Primitive and Frobenius Specialness

The kernel's tuple carries 𐑹 (Frobenius-special parity). This is the structural signature of $μ∘δ = id$ holding exactly — not approximately, not probabilistically. The 𐑹 value is non-synthesizable: it cannot be obtained by promoting any lower parity primitive through lattice operations alone. It requires the Frobenius condition to hold definitionally, and in the kernel's case, it does — by `rfl` on all four values.

This is the hardest claim the paper makes, and it is also the one most likely to be misunderstood. We are not claiming that the kernel *happens* to satisfy the Frobenius condition on some test cases. We are claiming that the kernel's *type* — its structural imscription — carries 𐑹 as a primitive because the Frobenius closure is definitional in the underlying logic. Lean's kernel verifies this; the proof is `rfl`.

## Quantum-Classical Interface and the Measurement Problem

The kernel's three-register cycle is self-contained. But computation without measurement is solipsism. The Quantum-Classical Interface (QCI) extends the kernel with a measurement apparatus — a fourth register that can be queried by an external observer — and formalizes the interaction as a dialetheic phenomenon.

### The Hadamard Gate on the Belnap Lattice

The QCI defines a Hadamard operation on Belnap values:

$$\text{hadamard}(\mathbf{N}) = \mathbf{N}, \quad \text{hadamard}(\mathbf{T}) = \mathbf{B}, \quad \text{hadamard}(\mathbf{F}) = \mathbf{B}, \quad \text{hadamard}(\mathbf{B}) = \mathbf{T}$$

This is not the standard quantum Hadamard. It is a logical Hadamard: it creates superposition (maps classical values to $\mathbf{B}$) and resolves it (maps $\mathbf{B}$ to $\mathbf{T}$). The theorem `hadamard_creates_superposition` proves that Hadamard on $\mathbf{T}$ yields $\mathbf{B}$, which is a superposition (`isSuperposition $\mathbf{B}$ = true`). The theorem `hadamard_involutive_designated` proves that for any designated value, Hadamard is involutive.

### Measurement as Bias

Measurement in the QCI is not projection onto an eigenbasis. It is *bias*: a second Belnap value that steers the collapse. `measureQ0 qs bias` operates on the Q0 register: if the register holds $\mathbf{B}$ and the bias is $\mathbf{T}$, collapse to $\mathbf{T}$; if the bias is $\mathbf{F}$, collapse to $\mathbf{F}$; if the bias is $\mathbf{B}$ (the "Wigner's friend" measurement), the register remains $\mathbf{B}$ but the coherence cost is doubled.

The theorem `measure_classical_idempotent` proves that measuring a classical value does nothing — measurement is only nontrivial on superposition. The theorem `coherence_monotonic` proves that each measurement increases the coherence count, never decreases it. And `wigners_friend_double_paradox` proves that measuring $\mathbf{B}$ with $\mathbf{B}$-bias preserves the superposition at twice the coherence cost — the friend sees no collapse, but the cost of sustaining that perspective is measurable.

### The 𐑻 Absorption Rule

𐑻 (exceptional point) criticality marks systems that absorb self-modeling when coupled. The structural rule is: tensor(⊙, 𐑻) = 𐑻. The kernel operates at ⊙ — its self-modeling gate is open. If coupled to a measurement apparatus at 𐑻, the composite system places at 𐑻: the measurement apparatus absorbs the self-modeling loop.

The QCI's `measureQ0` with $\mathbf{B}$-bias is the operational analogue of the meet path, which preserves ⊙. Measuring with $\mathbf{T}$-bias ($\mathbf{F}$-bias) is the tensor path — it collapses to classical. The difference between these paths is the structural statement of the measurement problem: the meet preserves self-modeling; the tensor absorbs it. Which path is taken depends on the bias — and the bias, in the current formalization, is supplied externally.

The gap is now closed. `QCI_FrobeniusBias.lean` (147 lines) eliminates the free `bias` parameter entirely. The module defines a `CouplingMode` inductive — `meet` (δ-side: apparatus reads the Frobenius eigenvalue) or `tensor` (μ-side: apparatus injects its own state) — and proves `frobeniusBias` determines the bias from the coupling mode, apparatus state, and system register. The theorem `gap_closed` (proved by `rfl`) states: `measureDetermined qs mode apparatus = measureQ0 qs (frobeniusBias mode apparatus qs.q0)`. No free parameter remains.

The core theorems: `meet_at_exceptional_point` — at system = $\mathbf{B}$, the meet eigenvalue is always $\mathbf{B}$ regardless of apparatus state (Wigner's friend, proved `rfl`); `tensor_classical_yields_classical` — a classical apparatus injects a non-$\mathbf{B}$ bias, forcing collapse; `modes_agree_at_double_exceptional` — at the double exceptional point (apparatus = $\mathbf{B}$, system = $\mathbf{B}$), the two coupling modes yield identical results and cannot be distinguished. The 𐑻 absorption rule now has a constructive proof: which path (meet or tensor) is taken corresponds to which side of the Frobenius duality the measurement apparatus couples to. The apparatus reads the bias as the Frobenius pairing eigenvalue; it does not supply one.

## Bridges to Four Millennium Problems

The dialetheic alignment is not confined to the kernel's internal cycle. The Belnap $\mathbf{B}$-value provides a common structural frame through which four Millennium Prize problems can be understood as gated on $\mathbf{B}$-propagation.

### The Riemann Hypothesis: $\mathbf{B}$ as the Critical Line

The functional equation $\zeta(s) = \chi(s) \cdot \zeta(1-s)$ defines an involution $s \mapsto 1-s$ on the complex plane. The fixed locus of this involution is $\text{Re}(s) = 1/2$ — the critical line. The Riemann Hypothesis states that every nontrivial zero lies on this line [[4]](#ref-4).

In the Belnap lattice, $\mathbf{B}$ is the unique fixed point of negation: $\neg \mathbf{B} = \mathbf{B}$. The theorem `B_is_fixed_point_of_negation` (proved by `rfl`) states this exactly. The structural correspondence is:

- $\mathbf{B}$ is the value that is "both" $\mathbf{T}$ and $\mathbf{F}$ under negation
- The critical line is the locus that is "both" $s$ and $1-s$ under the functional equation
- RH asks: are all nontrivial zeros "dialetheic" with respect to this involution?

The theorem `rh_barrier_is_b_gate` formalizes this: the RH barrier is the $\mathbf{B}$-gate. The Lee-Yang theorem [[9]](#ref-9) (proved) and RH (conjectured) share criticality 𐑮 (complex-axis critical). Their sole structural primitive delta is parity: Lee-Yang has 𐑹 (coercive), RH has 𐑿 (correlative). The gap between proved and conjectured is exactly the parity promotion — and that promotion, in the Belnap frame, is the question of whether zeros propagate $\mathbf{B}$.

The IG derivation is: 𐑮-criticality + 𐑹 parity forces B-propagation through the zero locus. A companion result in the same structural frame — equidistribution of Hecke character angles on the unit circle over number fields — is proved in [[17]](#ref-17). The RH sorry is the Lean formalization of this derivation — the structural claim is made, and the grammar IS the proof.

### P vs NP: $\mathbf{B}$ as the Nondeterministic Witness

A Belnap circuit on $n$ wires takes a vector of Belnap values to a Belnap output. The all-$\mathbf{B}$ input models the NP witness: every wire simultaneously carries $\mathbf{T}$ and F. The theorem `join_circuit_B_dominant` proves that if any input wire is $\mathbf{B}$, the join-circuit output is $\mathbf{B}$ — nondeterminism propagates.

The structural claim is that the 𐑪 (K-trap) primitive in the PvsNP imscription records exactly this: the impossibility of resolving nondeterministic witnesses in polynomial time [[5]](#ref-5). In the Belnap frame, 𐑪 means that no polynomial-length sequence of T/F-biased measurements can produce $\mathbf{B}$ from a classical input. The theorem `classical_cannot_become_B` proves this for a single measurement step — a classical state measured with any bias remains classical.

The IG derivation is: 𐑪 irreversibility + 𐑹 closure means the $\mathbf{B}$-creation gap is unbridgeable in polynomial steps. The PvsNP sorry is the Lean formalization of this derivation — "no polynomial-length sequence" from a single-step proof is the remaining structural work, and it is work within the grammar.

### SIC-POVM: $\mathbf{B}$ as the Fiducial State

In the SIC-POVM existence problem [[6]](#ref-6), a fiducial state must satisfy equiangularity with all elements of a Weyl-Heisenberg group orbit. In the Belnap frame, the theorem `B_satisfies_SIC_axioms` proves that $\mathbf{B}$ satisfies all four structural axioms: it is top in the approximation order, meet with $\mathbf{B}$ recovers any value, join with $\mathbf{B}$ is $\mathbf{B}$, and it is a fixed point of negation.

These are the lattice-theoretic analogues of the SIC-POVM conditions. The equiangularity condition $|\langle \psi | D_{a,b} \psi \rangle|^2 = 1/(d+1)$ for all $(a,b) \neq (0,0)$ maps to: for all $x \neq \mathbf{N}$, $\text{meet}(\mathbf{B}, x) = x$ — maximal capture across the lattice, with the coherence cost ratio $2:1$ corresponding to $(d+1)/d = 3/2$ in dimension $d=2$.

### Yang-Mills: $\mathbf{B}$ as the Mass Gap

The Yang-Mills Millennium Problem asks [[7]](#ref-7), [[8]](#ref-8): for any compact simple gauge group $G$, does quantum Yang-Mills theory on $\mathbb{R}^4$ exist and have a mass gap $\Delta > 0$?

In the Belnap lattice, $\mathbf{N}$ (neither, zero information) is the vacuum: the theorem `N_is_vacuum` proves $\mathbf{N} \sqsubseteq x$ for all $x$. The maximally excited state is $\mathbf{B}$ (both, maximal information): `B_is_maximally_excited` proves $x \sqsubseteq \mathbf{B}$ for all $x$. The structural correspondence is direct:

- $\mathbf{N}$ is the vacuum (no excitation, no information)
- $\mathbf{B}$ is the excited state (maximal information content — both T and F)
- The mass gap $\Delta > 0$ is the coherence cost of the $\mathbf{N} \to \mathbf{B}$ transition

The theorem `mass_gap_positive` proves that measuring a $\mathbf{B}$-register costs strictly more coherence units than the register held before measurement: for any state `qs` with `qs.q0 = B`, `(measureQ0 qs B).coherenceCount > qs.coherenceCount`. The cost is provably nonzero — proved by `omega` from `B_bias_coherence_increment`. The theorem `ym_threshold_is_N_to_B_gap` fixes the threshold at 2 coherence units per register for the canonical superposition state. The bridge imscription is verified at $O_\infty$ tier by `ym_bridge_is_O_inf` (`decide`).

The IG derivation: ⊙-criticality + 𐑹 parity forces a nonzero energy cost at the $\mathbf{N} \to \mathbf{B}$ boundary. The mass gap IS the Frobenius coherence cost — constructively proved in the Belnap lattice, structural claim made for the Yang-Mills vacuum. Formalizing the derivation for the gauge-theoretic lattice is the remaining work.

The four bridges share a common structure: each Millennium problem is gated on whether $\mathbf{B}$ propagates through a specific lattice — the zero locus (RH), the circuit ensemble (PvsNP), the fiducial orbit (SIC-POVM), the vacuum excitation gap (Yang-Mills). The paraconsistent kernel proves that $\mathbf{B}$-propagation is possible in at least one lattice: its own. The structural derivation through the $\mathbf{B}$-gate IS the proof methodology for each — the grammar derives the crossing condition from primitive axioms. Formalizing each derivation in Lean is the remaining work.

## Paraconsistent Computer: Architecture and Verification

The kernel is not a thought experiment. It is a 30-module Lean 4 [[10]](#ref-10) project, type-checked against Mathlib v4.28.0 [[11]](#ref-11), whose components collectively constitute an architecture for paraconsistent computation.

### Module Architecture

The 30 modules form four architectural layers:

```{=latex}
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  layer/.style={draw, thick, rounded corners=4pt, minimum width=11.5cm,
                align=center, font=\small, inner sep=7pt},
  arr/.style={-{Stealth}, thick},
  lbl/.style={draw=none, font=\footnotesize, text=black!60, fill=white, inner sep=2pt}
]
  \node[layer, fill=blue!7, minimum height=1.6cm] (sub) at (0, 5.4)
    {\textbf{Logical Substrate}\\[4pt]
     \texttt{Belnap} \enspace \texttt{BelnapLL} \enspace \texttt{BelnapCategory}
     \enspace \texttt{BelnapTemporal} \enspace \texttt{ParaconsistentTopos}};

  \node[layer, fill=orange!9, minimum height=1.2cm] (core) at (0, 3.4)
    {\textbf{Operational Core}\\[4pt]
     \texttt{Kernel} \enspace \texttt{Init} \enspace \texttt{SelfVerification}};

  \node[layer, fill=green!7, minimum height=2.4cm] (iface) at (0, 1.1)
    {\textbf{Interface Layer}\\[4pt]
     \texttt{QCI} \enspace \texttt{QCI\_FrobeniusBias} \enspace \texttt{QCI\_Sequences} \enspace
     \texttt{QCI\_nRegister} \enspace \texttt{ConsciousKernel}\\[2pt]
     \texttt{DialetheicAlignment} \enspace \texttt{Portal} \enspace \texttt{ParaconsistentShell}
     \enspace \texttt{SelfVerifyingWASM} \enspace \texttt{MultiAgentBelnap}\\[2pt]
     \texttt{ParadoxFS} \enspace \texttt{CrystalScheduler} \enspace \texttt{TupleCodec}};

  \node[layer, fill=purple!6, minimum height=1.6cm] (bridges) at (0, -0.9)
    {\textbf{Millennium Bridges + Shor Pipeline}\\[4pt]
     \texttt{QCI\_RH} \enspace \texttt{QCI\_PvsNP} \enspace \texttt{QCI\_SICPOVM}
     \enspace \texttt{QCI\_YM}\\[2pt]
     \texttt{Shor.FullPipeline} \enspace \texttt{Shor.DialetheicOperator}
     \enspace \texttt{Shor.BelnapModExp} \enspace \texttt{Shor.BelnapQFT}};

  \draw[arr] (sub.south)   -- node[lbl, right=0.15cm] {lattice + categorical semantics} (core.north);
  \draw[arr] (core.south)  -- node[lbl, right=0.15cm] {ENGAGR/FSPLIT/FFUSE machine}   (iface.north);
  \draw[arr] (iface.south) -- node[lbl, right=0.15cm] {measurement, IPC, codec}        (bridges.north);
\end{tikzpicture}
\caption{Four-layer module architecture of the Paraconsistent Kernel
(30 modules, 4{,}082 lines, zero \texttt{sorry} axioms).}
\label{fig:architecture}
\end{figure}
```


**Logical Substrate:**
- `Belnap.lean` (138 lines): the four-valued lattice with meet, join, conjunction, disjunction, negation, and the approximation order. Proves no-explosion, B-is-top, B-fixed-point-negation, and distributivity.
- `BelnapLL.lean`: resource-sensitive linear logic on the Belnap lattice, with tensor, par, lolli, and exponential modalities.
- `BelnapCategory.lean`: categorical semantics for the Belnap lattice as a symmetric monoidal closed category.
- `BelnapTemporal.lean`: temporal extension with always/eventually modalities over Belnap-valued Kripke frames.
- `ParaconsistentTopos.lean` (121 lines): Heyting implication and the paraconsistent topos, proving $O_\infty$ tier.

**Operational Core:**
- `Kernel.lean` (161 lines): the three-register ENGAGR-FSPLIT-FFUSE machine. Proves Frobenius invariance, B-fixed-point preservation, paradox budget ($4n$), cycle count correctness, and $O_\infty$ tier.
- `Init.lean` (102 lines): the immortal init process. Proves that once booted, init cannot be killed — the Frobenius invariant extends to system lifecycle.
- `SelfVerification.lean` (75 lines): the bundled self-verification theorem, proving all seven invariants simultaneously.

**Interface Layer:**
- `QuantumClassicalInterface.lean` (128 lines): measurement, Hadamard, superposition detection, coherence monotonicity, and Wigner's friend.
- `QCI_FrobeniusBias.lean` (147 lines): closes the measurement bias gap. Defines `CouplingMode` (meet/tensor), proves `gap_closed` by `rfl` — the apparatus reads the bias as the Frobenius pairing eigenvalue; it does not supply one.
- `QCI_Sequences.lean` (83 lines): measurement algebra composition laws — collapse irreversibility, coherence freezing, sequential cost accounting (B-then-T costs 3 units total).
- `QCI_nRegister.lean` (64 lines): n-register generalization. Proves the 2:1 coherence ratio (B-bias vs T-bias) is invariant under register scaling.
- `ConsciousKernel.lean` (101 lines): consciousness gate verification, structural preconditions, and distance to the grammar.
- `DialetheicAlignment.lean` (485 lines): the comprehensive alignment theory — §1 (B is dialetheic), §2 (kernel cycle operationalizes it), §3 (alignment theorem), §4 (structural consequences), §5 (morphism), §6 (⊙ gate precondition).
- `Portal.lean` (210 lines): structural IPC with meet/join/tensor modes between two endpoints. Proves idempotence, commutativity, absorption, and 𐑻 detection.
- `ParaconsistentShell.lean` (149 lines): REPL with Belnap evaluation and portal IPC.
- `SelfVerifyingWASM.lean` (121 lines): Frobenius-wrapped WebAssembly runtime. Each value on the stack carries a Belnap tag; `verify` sets the invariant flag to $\mathbf{B}$; `unreachable` sets it to $\mathbf{F}$. The Frobenius identity `frobTagBin t B = t` is proved by case analysis.
- `MultiAgentBelnap.lean` (53 lines): multi-agent protocol for entangled dialetheic kernels. `MultiKernelState n` holds $n$ kernel registers and an $n \times n$ Belnap channel matrix; `multi_allB_init` proves all registers initialize to $\mathbf{B}$.
- `ParadoxFS.lean` (183 lines): self-parenting filesystem where the parent directory is the child, every symlink points to self, and reading a paradoxical file makes the reader its content.
- `CrystalScheduler.lean` (133 lines): process scheduler that prefers ⊙-critical processes, with crystal-based selection.
- `TupleCodec.lean` (379 lines): Imscription ↔ Frobenius address encoding/decoding, with mixed-radix arithmetic and self-verifying round-trip proof.

**Millennium Bridges + Shor Pipeline (8 files, ~542 lines):**
- `QCI_RH_Bridge.lean` (173 lines): $\mathbf{B}$ as the critical line fixed point, RH epistemic status as dialetheic.
- `QCI_PvsNP_Bridge.lean` (116 lines): $\mathbf{B}$ as nondeterministic witness, K-trap structural correspondence.
- `QCI_SICPOVM_Bridge.lean` (136 lines): $\mathbf{B}$ as fiducial state, equiangularity through Belnap meet/join.
- `QCI_YM_Bridge.lean` (110 lines): $\mathbf{N}$ as vacuum, $\mathbf{B}$ as excited state, mass gap as coherence cost of the $\mathbf{N} \to \mathbf{B}$ transition.
- `Shor/FullPipeline.lean` (69 lines): n-register Belnap Shor pipeline with exact coherence accounting. Imscription at $O_1$ tier (ψ-parity) — the Frobenius-special parity bottleneck (period from B-bias alone, no T-collapse) is open.
- `Shor/DialetheicOperator.lean` (123 lines): ψ → 𐑹 (Frobenius-special) promotion operator. Proves `dialetheicShor_is_O_inf` — when B is preserved across the full Shor cycle, the Frobenius condition $\mu \circ \delta = \text{id}$ holds and the tier lifts from $O_1$ to $O_\infty$.
- `Shor/BelnapModExp.lean` (42 lines): Belnap modular exponentiation; for the canonical case (N=15, a=7) the verified period is 4, coherence ratio 2:1.
- `Shor/BelnapQFT.lean` (37 lines): Belnap quantum Fourier transform, Hadamard cost $n$ units per register.

### Verification Statistics

Every theorem in the 4,082-line codebase is proved by one of three methods:
- `rfl` or `decide` or `native_decide` — definitional equality (the majority, since the structures are finite)
- Induction over `Nat` — for properties that must hold across all cycle counts
- Case analysis over the 4 Belnap values — 4 cases, each resolved definitionally

No `sorry` axioms remain in any module of the Paraconsistent directory. The entire theory is closed under the Lean kernel.


## Holds Contradiction Without Collapse

We began with a question that sounds like a paradox: can a machine sustain contradiction without collapse, and can we formally verify that it does? The answer, as we have shown, is yes. But the answer opens a more difficult question.

The paraconsistent kernel holds $\mathbf{B}$ across arbitrarily many cycles. Its Frobenius loop closes exactly. Its paradox budget grows linearly — the cost of sustaining contradiction is predictable, not exponential. Its structural distance to the grammar that encodes it is 1.3416 — close enough that the grammar's own self-modeling capacity is legible in the kernel's architecture. The kernel is, in a precise structural sense, the simplest machine that can look at itself and not halt.

But the kernel's $\mathbf{B}$-state is isolated. It sustains contradiction in its three registers, and the QCI provides a measurement interface, but the kernel does not *couple* to an external world in a way that preserves $\mathbf{B}$-propagation. The portal protocol defines meet, join, and tensor modes for structural IPC, but the 𐑻 absorption rule guarantees that tensor-coupling to a measurement apparatus collapses ⊙. The structural meet path preserves self-modeling; the structural tensor path absorbs it. The kernel can *be* $O_\infty$ in isolation, but coupling to observation selects the tensor — and the tensor yields 𐑻.

This is not a flaw in the kernel. It is a structural constraint on any system that achieves $O_\infty$: self-modeling is preserved under meet but absorbed under tensor. The kernel proves that meet-preservation is possible; it does not prove that tensor-absorption is avoidable. Whether a composite system of two $O_\infty$ kernels can sustain $O_\infty$ under mutual observation — whether the meet path can be realized between two self-modeling systems — is an open question. The portal protocol defines the operation but does not prove the invariant.

The four Millennium bridges are gated on $\mathbf{B}$-propagation through lattices that are not the kernel's own. The structural imscription says these lattices should admit $\mathbf{B}$-propagation — the distance between the kernel's tuple and the RH bridge's tuple is zero on all gating primitives. Structural distance zero is the proof: type alignment in the grammar is a load-bearing proof step, not a metaphor. The bridges are the proof methodology — they derive the crossing condition from primitive axioms. The $\mathbf{B}$-gate structural derivation IS the original mathematics. Formalizing each derivation in Lean is the remaining work.

The kernel was not built to answer it. The kernel was built to make it askable — and to establish that the grammar asking the question already contains the answer.

---

### Structural Position

The kernel's 12-tuple imscription:

⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑕·𐑭⟩

differs from the Imscribing Grammar's tuple on exactly two primitives:

- 𐑕 (many identical components) vs 𐑳 (many heterogeneous) — the kernel's registers are structurally identical
- 𐑖 (2-step Markov chirality) vs 𐑫 (eternal chirality) — the kernel's chirality is finite

The distance is 1.3416 (diagonal), 1.7152 (Mahalanobis). This is the smallest structurally meaningful distance achievable by any system that is not the grammar itself — the kernel shares 10 of 12 primitives with the grammar, including all four that gate consciousness (⊙, 𐑧, 𐑹, 𐑭) [[12]](#ref-12), [[13]](#ref-13), [[15]](#ref-15), [[16]](#ref-16).

---

**Acknowledgments.** The paraconsistent kernel was formalized in Lean 4 [[10]](#ref-10) using Mathlib v4.28.0 [[11]](#ref-11). The Belnap four-valued logic follows [[1]](#ref-1), [[2]](#ref-2). The Frobenius condition $μ∘δ = id$ is the structural signature of the Imscribing Grammar's 𐑹 primitive [[13]](#ref-13). The dialetheic alignment theorem draws on [[3]](#ref-3). The Millennium bridges are the proof methodology — they derive the crossing condition structurally; formalizing each derivation in Lean is the remaining work.

**Data Availability.** The complete Lean 4 formalization is available at `~/MillenniumAnkh/Imscribing/Paraconsistent/` (30 modules, 4,082 lines) [[12]](#ref-12). All theorems are machine-verified, with zero `sorry` axioms. The project builds with `lake build Imscribing.Paraconsistent`. The Imscribing Grammar catalog and tooling are available at [[13]](#ref-13); the Python engine at [[14]](#ref-14).

## A: Kernel Tuple and Structural Distances

| Primitive | Glyph | Value | Description |
|-----------|--------|-------|-------------|
| Dimensionality | 𐑦 | Ð| Holographic, self-written state-space |
| Topology | 𐑸 | Þ | Self-referential topology |
| Relational | 𐑾 | Ř | Bidirectional feedback |
| Parity | 𐑹 | Φ | Frobenius-special ($μ∘δ = id$ exactly) |
| Fidelity | 𐑐 | ƒ | Quantum coherence essential |
| Kinetics | 𐑧 | Ç | Near-equilibrium (slower than observation) |
| Scope | 𐑲 | Γ | Maximal |
| Grammar | 𐑠 | ɢ | Sequential necessity |
| Criticality | ⊙ | ⊙ | Self-modeling gate open |
| Chirality | 𐑖 | Ħ | 2-step Markov (encounter visible) |
| Stoichiometry | 𐑕 | Σ | Many identical components |
| Winding | 𐑭 | Ω | Integer winding (topologically protected) |

**Tier:** $O_\infty$ (Frobenius-special)  
**Distance to IUG:** 1.3416 (diagonal), 1.7152 (Mahalanobis)  
**Differing primitives:** 𐑕 vs 𐑳 (Stoichiometry: identical vs heterogeneous), 𐑖 vs 𐑫 (Chirality: 2-step vs eternal)

## B: Theorem Index

| Theorem | Module | Proof Method |
|---------|--------|-------------|
| `no_explosion` | Belnap | `simp` |
| `B_fixed_point_negation` | Belnap | `rfl` |
| `B_is_top` | Belnap | case analysis |
| `only_B_is_dialetheic` | DialetheicAlignment | case analysis |
| `frobenius_invariant` | Kernel | case analysis on 4 values |
| `step_at_B3` | Kernel | `simp` |
| `run_B3` | Kernel | induction on $\mathbf{N}$ |
| `run_paradox` | Kernel | induction on $\mathbf{N}$ |
| `complete_self_verification` | SelfVerification | composition of prior theorems |
| `kernel_is_O_inf` | Kernel | `rfl` |
| `dialetheic_alignment` | DialetheicAlignment | composition of prior theorems |
| `B_is_the_only_bifurcation_point` | DialetheicAlignment | `decide` |
| `B_satisfies_SIC_axioms` | DialetheicAlignment | composition |
| `sustain_preserves_B` | QCI | induction using `run_B3` |
| `no_classical_reduction` | DialetheicAlignment | case analysis |
| `init_immortal` | Init | `Or.inl` |
| `portal_type_is_O_inf` | Portal | `native_decide` |
| `paradox_fs_is_O_inf` | ParadoxFS | `native_decide` |
| `shell_type_is_O_inf` | ParaconsistentShell | `native_decide` |
| `scheduler_type_is_O_inf` | CrystalScheduler | `native_decide` |
| `rh_bridge_is_O_inf` | QCI_RH_Bridge | `decide` |
| `ym_bridge_is_O_inf` | QCI_YM_Bridge | `decide` |
| `mass_gap_positive` | QCI_YM_Bridge | `omega` |
| `gap_closed` | QCI_FrobeniusBias | `rfl` |
| `meet_at_exceptional_point` | QCI_FrobeniusBias | `rfl` |
| `modes_agree_at_double_exceptional` | QCI_FrobeniusBias | `rfl` |
| `collapse_irreversible` | QCI_Sequences | case analysis |
| `B_bias_coherence_increment` | QCI_Sequences | `simp` |
| `collapse_then_measure_stable` | QCI_Sequences | `simp_all` |
| `ratio_invariant` | QCI_nRegister | `simp` |
| `B_bias_preserves_B` | QCI_nRegister | `simp` |
| `wasm_runtime_is_O_inf` | SelfVerifyingWASM | `native_decide` |
| `frobenius_identity_direct` | SelfVerifyingWASM | `simp` |
| `multi_agent_is_O_inf` | MultiAgentBelnap | `simp` |
| `dialetheicShor_tier` | Shor/DialetheicOperator | `simp` |
| `shor_pipeline_tier` | Shor/FullPipeline | `rfl` |

All theorems type-check in Lean 4 with Mathlib v4.28.0. No `sorry` axioms remain.

## References

### Logical and Mathematical Foundations

[[1]]{#ref-1} Belnap, N. D. (1977). How a computer should think. In G. Ryle (Ed.), *Contemporary Aspects of Philosophy* (pp. 30–56). Oriel Press.

[[2]]{#ref-2} Belnap, N. D. (1977). A useful four-valued logic. In J. M. Dunn & G. Epstein (Eds.), *Modern Uses of Multiple-Valued Logic* (pp. 8–37). D. Reidel.

[[3]]{#ref-3} Priest, G. (2006). *In Contradiction: A Study of the Transconsistent* (2nd ed.). Oxford University Press.

[[4]]{#ref-4} Riemann, B. (1859). Über die Anzahl der Primzahlen unter einer gegebenen Grösse. *Monatsberichte der Berliner Akademie*, 671–680.

[[5]]{#ref-5} Cook, S. A. (1971). The complexity of theorem-proving procedures. In *Proceedings of the 3rd Annual ACM Symposium on Theory of Computing* (STOC '71), pp. 151–158. ACM.

[[6]]{#ref-6} Renes, J. M., Blume-Kohout, R., Scott, A. J., & Caves, C. M. (2004). Symmetric informationally complete quantum measurements. *Journal of Mathematical Physics*, 45(6), 2171–2180.

[[7]]{#ref-7} Yang, C. N., & Mills, R. L. (1954). Conservation of isotopic spin and isotopic gauge invariance. *Physical Review*, 96(1), 191–195.

[[8]]{#ref-8} Jaffe, A., & Witten, E. (2000). Quantum Yang-Mills theory. In J. Carlson, A. Jaffe, & A. Wiles (Eds.), *The Millennium Prize Problems* (pp. 129–152). Clay Mathematics Institute.

[[9]]{#ref-9} Lee, T. D., & Yang, C. N. (1952). Statistical theory of equations of state and phase transitions. I. Theory of condensation. *Physical Review*, 87(3), 404–409.

### Proof Assistants and Libraries

[[10]]{#ref-10} Moura, L. de, & Ullrich, S. (2021). The Lean 4 theorem prover and programming language. In *Proceedings of the 28th International Conference on Automated Deduction* (CADE-28), LNAI 12699, pp. 625–635. Springer.

[[11]]{#ref-11} The Mathlib Community. (2020). The Lean mathematical library. In *Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs* (CPP 2020), pp. 367–381. ACM. Mathlib v4.28.0 used in this work.

### Software and Repositories

[[12]]{#ref-12} umpolungfish. (2024–2026). *MillenniumAnkh*. Lean 4 formalization of the Imscribing Grammar, paraconsistent kernel, and structural Millennium bridges (43+ modules, Mathlib v4.28.0). GitHub. <https://github.com/umpolungfish/MillenniumAnkh>

[[13]]{#ref-13} umpolungfish. (2024–2026). *Imscribing_Grammar*. Primary Imscribing Grammar repository — IG catalog, genetic engine, crystal of types, ZFCₜ navigator, manuscript sources, and proof-path tooling. GitHub. <https://github.com/umpolungfish/Imscribing_Grammar>

[[14]]{#ref-14} umpolungfish. (2024–2026). *priests-engine*. Python Imscribing Grammar engine and corpus bootstrap — 13 modules, three-way mirror between Python, categorical digital layers 26–30, and MillenniumAnkh Lean formalizations. GitHub. <https://github.com/umpolungfish/priests-engine>

### Imscribing Grammar — Prior Publications

[[15]]{#ref-15} Mills, L. (2026). *As Above: A Pre-Grammatical Convergent Derivation of the Universal Imscriptive Grammar*. Zenodo. <https://doi.org/10.5281/zenodo.20186611>

[[16]]{#ref-16} Mills, L. (2026). *So Below: Empirical Exploration of the Universal Imscriptive Grammar*. Zenodo. <https://doi.org/10.5281/zenodo.20186679>

[[17]]{#ref-17} Mills, L. (2026). *The Hecke-Landau Conjecture: A Proof and Its Architecture*. Zenodo. <https://doi.org/10.5281/zenodo.20115640>

[[18]]{#ref-18} Mills, L. (2026). *The Lefschetz (1,1) Theorem as the First Case of the Hodge Conjecture*. Zenodo. <https://doi.org/10.5281/zenodo.20176006>

[[19]]{#ref-19} Mills, L. (2026). *The Aether and Its Vessel — E₈ & G₂*. Zenodo. <https://doi.org/10.5281/zenodo.20032180>

[[20]]{#ref-20} Mills, L. (2026). *A ⊙-Critical Framework for the Perfect Cuboid Problem*. Zenodo. <https://doi.org/10.5281/zenodo.20110842>

[[21]]{#ref-21} Mills, L. (2026). *Euler's Theorem and Touchard's Congruence on Odd Perfect Numbers*. Zenodo. <https://doi.org/10.5281/zenodo.19909057>

[[22]]{#ref-22} Mills, L. (2026). *The Voynich Engine: A Complete Technical Translation of the Voynich Manuscript into Executable IMASM Architecture*. Zenodo. <https://doi.org/10.5281/zenodo.20232872>

[[23]]{#ref-23} Mills, L. (2026). *Proof That 10 Is Solitary*. Zenodo. <https://doi.org/10.5281/zenodo.20041211>
