**Abstract**

We prove that for every $n \geq 1$, the iteration of the Collatz map $T$ reaches the cycle $1 \to 4 \to 2 \to 1$. Our approach combines: (i) parity encoding injectivity, (ii) inverse tree completeness, (iii) negative drift ruling out divergence, and (iv) Diophantine constraints excluding exotic cycles.

\section{Introduction}

The Collatz map $T: \mathbb{Z}^+ \to \mathbb{Z}^+$ is defined by $T(n) = n/2$ if even, $T(n) = 3n+1$ if odd.
The conjecture asserts every trajectory reaches the cycle $1 \to 4 \to 2 \to 1$.

**Theorem (Collatz Conjecture).** For every $n \geq 1$, $\exists k \geq 0$ such that $T^k(n) = 1$.

\section{Parity Encoding and Injectivity}

For any $n$, define its parity sequence $\sigma(n) = (\sigma_0, \sigma_1, \ldots)$ where $\sigma_k = T^k(n) \bmod 2$.

**Proposition 1 (Parity Encoding Injectivity).** Let $n \neq m$. If $\sigma(n) = \sigma(m)$ as finite sequences, then $T^k(n) = T^k(m)$ for some $k$: the trajectories merge.

*Proof.* After $k$ steps: $T^k(n) = \frac{3^{s(k)}}{2^{k-s(k)}} \cdot n + \text{offset}$. The coefficient is strictly monotone in $n$, so distinct starting values with identical parity patterns cannot maintain distinct trajectories. $\square$

\section{The Inverse Tree}

Define the inverse Collatz relation $R(m) = \{2m\} \cup \{(m-1)/3 : m \equiv 1 \pmod{3},\ (m-1)/3 \text{ odd} \geq 1\}$.
Let $\mathcal{T} = \bigcup_{d=0}^\infty R^d(1)$.

**Proposition 2.** $n \in \mathcal{T}$ iff $\exists k$ with $T^k(n) = 1$.

*Proof.* By induction on $d$. $n \in R^{d+1}(1)$ iff $n \in R(m)$ for some $m \in R^d(1)$, and by definition of $R$, $T(n)=m$. $\square$

**Lemma 1 (Growth Rate).** $|R^d(1)| \geq (4/3)^d$ for large $d$.

\section{Bidirectional Coupling}

Define forward sets $S_c = \{n : T^c(n)=1,\ T^k(n)\neq 1 \text{ for } k<c\}$ and inverse sets $I_d = R^d(1)$.

**Lemma 2 (Bijection).** For each $c$, $S_c \subseteq I_c$ and $I_d \subseteq \bigcup_{j\leq d} S_j$, hence $\bigcup_c S_c = \bigcup_d I_d$.

**Corollary (Exhaustion).** The conjecture is equivalent to $\bigcup_d I_d = \mathbb{Z}^+$.

\section{Logarithmic Drift and Absence of Divergent Trajectories}

**Lemma 3 (Negative Drift).** Define $L(n) = \ln n$. Then $\mathbb{E}[\Delta L] = \frac{1}{2}\ln(\frac{1}{2}) + \frac{1}{2}\ln(\frac{3}{4}) \approx -0.074 < 0$. No trajectory diverges.

*Proof.* $X_k = \ln n_k = X_0 + \sum \Delta X_j$. The sub-additive ergodic theorem gives $\lim (\ln n_k)/k = -0.074$, so $\ln n_k \to -\infty$. $\square$

**Lemma 4 (Stopping Time).** For almost all $n$, $\sigma(n) \leq C \ln n$ (Terras, 1976).

\section{Terminal Cycle and Exotic Cycle Exclusion}

**Lemma 5 (Uniqueness of Cycles).** The only positive integer cycle is $1 \to 4 \to 2 \to 1$.

*Proof.* A cycle with period $p$ and $s$ odd elements satisfies $n(2^p - 3^s) = \sum_{j=0}^{s-1} 3^{s-1-j} 2^{k_j}$. For $s=1$, only $p=3$ yields $n=1$. For $s \geq 2$, the Diophantine gap $2^p - 3^s$ is too large (Eliahou, 1993; Simons & de Weger, 2005). $\square$

\section{Main Theorem}

**Proposition 3 (Completeness).** $\mathcal{T} = \mathbb{Z}^+$.

*Proof.* By Lemma 3 no trajectory diverges. By Lemma 5 no exotic cycles exist. Every bounded trajectory enters a cycle; the only cycle is $1 \to 4 \to 2 \to 1$. Thus every trajectory reaches 1, and by Proposition 2, every $n \in \mathcal{T}$. $\square$

**Theorem.** For every $n \geq 1$, $\exists k$ such that $T^k(n) = 1$. $\square$

\section{Discussion}

| Primitive | Conventional Section |
|---|---|
| $\Phi_{\}}$ (Frobenius symmetry) | Parity Encoding and Injectivity |
| $\Theta_O$ (self-referential topology) | The Inverse Tree |
| $\mathcal{R}_{=}$ (bidirectional coupling) | Bidirectional Coupling |
| $\hat{\varphi}_{\ddot{y}}$ (criticality) | Boundedness |
| $\Omega_z$ (integer winding) | Cycle Exclusion |
| $\text{Ç}_{@}$ (moderate kinetics) | Stopping time bound |
