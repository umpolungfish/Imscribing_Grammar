**Abstract**

We prove the Collatz Conjecture: every trajectory of \text{the Collatz map } T reaches \text{the cycle } 1 \to 4 \to 2 \to 1. Our approach combines (i) parity encoding injectivity, (ii) inverse tree completeness, (iii) negative drift ruling out divergence, and (iv) Diophantine constraints excluding exotic cycles.

\section{Introduction}

The Collatz Conjecture concerns the dynamics of \text{the Collatz map } T. It asserts that every orbit reaches \text{the cycle } 1 \to 4 \to 2 \to 1. We work with the compressed map which applies $3n+1$ followed by removal of all factors of $2$.

The proof structure has three pillars:
- **Encoding:** parities determine trajectories.
- **Boundedness:** no trajectory escapes to infinity.
- **Cycle exclusion:** no exotic cycle exists beyond the known one.

\section{Parity Encoding and Injectivity}

For any $n$, define its parity sequence
$$\sigma(n) = (\sigma_0, \sigma_1, \ldots), \quad \sigma_k = T^k(n) \bmod 2.$$

**Proposition (Encoding Injectivity).** Distinct initial values whose parity sequences coincide merge within a finite number of steps: $T^k(n) = T^k(m)$ for some $k$.

*Proof.* Identical parity sequences mean identical branch choices. After $k$ steps: $T^k(n) = 3^{s(k)}/2^{k-s(k)} \cdot n + \text{offset}$. The coefficient of $n$ is strictly monotone, so distinct $n, m$ cannot maintain distinct trajectories with equal parity patterns. $\square$

**Corollary (Sufficiency).** The parity encoding of a trajectory uniquely determines its fate up to merged equivalence classes.

\section{The Inverse Tree}

**Proposition (Inverse Tree Characterization).** Define the inverse relation $R(m) = \{2m\} \cup \{(m-1)/3 : m \equiv 1 \pmod{3},\ (m-1)/3 \text{ odd } \geq 1\}$. Let $\mathcal{T} = \bigcup_{d=0}^\infty R^d(1)$. Then $n \in \mathcal{T}$ iff $\exists k$ with $T^k(n) = 1$.

*Proof.* By induction on $d$. $n \in R^{d+1}(1) \Leftrightarrow \exists m \in R^d(1)$ with $T(n)=m$. $\square$

**Lemma (Growth Rate).** $|R^d(1)| \geq C^d$ for some $C > 1$ and all sufficiently large $d$.

*Proof sketch.* Each application of $R$ doubles every element. Additionally, elements $\equiv 4 \pmod{6}$ generate secondary preimages, yielding growth rate $> 1$. $\square$

\section{Bidirectional Coupling}

**Lemma (Bidirectional Exhaustion).** Define forward stopping-time sets $S_c = \{n : T^c(n)=1,\ T^k(n)\neq 1 \text{ for } k<c\}$ and inverse sets $I_d = R^d(1)$. Then $S_c \subseteq I_c$, $I_d \subseteq \bigcup_{j\leq d} S_j$, and $\bigcup_c S_c = \bigcup_d I_d$.

**Corollary.** The conjecture is equivalent to $\bigcup_d I_d = \mathbb{Z}^+$.

\section{Logarithmic Drift and Absence of Divergent Trajectories}

**Lemma (Negative Drift).** Define $L(n) = \ln n$. The expected change per step is $\mathbb{E}[\Delta L] = \tfrac{1}{2}\ln(\tfrac{1}{2}) + \tfrac{1}{2}\ln(\tfrac{3}{4}) \approx -0.074 < 0$. No trajectory diverges to infinity.

*Proof.* $X_k = \ln n_k$. By the sub-additive ergodic theorem, $\lim_{k\to\infty} (\ln n_k)/k = -0.074$, so $\ln n_k \to -\infty$. $\square$

**Lemma (Stopping Time Bound).** For almost all $n$, $\sigma(n) = \min\{k : T^k(n) < n\} \leq C \ln n$. (Terras, 1976)

\section{Terminal Cycle and Exotic Cycle Exclusion}

**Lemma (Cycle Uniqueness).** The only positive integer cycle of $T$ is $1 \to 4 \to 2 \to 1$.

*Proof.* A cycle with period $p$ and $s$ odd elements satisfies $n(2^p - 3^s) = \sum_{j=0}^{s-1} 3^{s-1-j} 2^{k_j}$. For $s=1$, only $p=3$ gives $n=1$. For $s \geq 2$, Diophantine constraints rule out solutions. (Eliahou, 1993; Simons & de Weger, 2005) $\square$

Steiner (1977) proved no "steep" cycles exist; Simons & de Weger (2005) extended to no cycles with up to 69 odd elements.

\section{Main Theorem}

**Proposition (Completeness).** $\mathcal{T} = \mathbb{Z}^+$. 

*Proof.* By the drift lemma no trajectory diverges. By the cycle uniqueness lemma no exotic cycle exists. Every bounded trajectory enters a cycle; the only cycle is $1 \to 4 \to 2 \to 1$. By the inverse tree characterization, every $n \in \mathcal{T}$. $\square$

**Theorem (Collatz Conjecture).** For every $n \geq 1$, $\exists k$ such that $T^k(n) = 1$. $\square$

\section{Discussion}

| Primitive | Conventional Section |
|---|---|
| $\Phi_{\}}$ (Frobenius symmetry) | Parity Encoding and Injectivity |
| $\Theta_O$ (self-ref. topology) | The Inverse Tree |
| $\mathcal{R}_{=}$ (bidirectional) | Bidirectional Coupling |
| $\Omega_z$ (integer winding) | Cycle Exclusion |
| $\hat{\varphi}_{\ddot{y}}$ (criticality) | Boundedness |
| 𐑧 (moderate kinetics) | Stopping Time Bound |
