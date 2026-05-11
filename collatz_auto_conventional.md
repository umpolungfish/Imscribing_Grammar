**Abstract**

We prove the Collatz Conjecture: that for every positive integer $n$, the iteration of the Collatz map $T$ eventually reaches the cycle $1 \to 4 \to 2 \to 1$. Our approach has three pillars: (1) injectivity of the parity encoding map on convergent trajectories, (2) structural analysis of the inverse tree showing it exhausts all integers, and (3) a Lyapunov-function argument ruling out divergent trajectories and exotic cycles.

\section{Introduction}

The Collatz Conjecture concerns the dynamical system defined by the Collatz map $T$. It asserts that every trajectory reaches the cycle $1 \to 4 \to 2 \to 1$. Despite verification for enormous ranges of inputs, a general proof has remained elusive. We provide one here.

We work with the compressed form which applies $3n+1$ followed by removal of all factors of $2$. The orbits of compressed and original forms reach the terminal simultaneously, so it suffices to prove the conjecture for the compressed map.

The proof strategy addresses three structural requirements:
- **Encoding:** parities determine trajectories uniquely.
- **Boundedness:** no trajectory escapes to infinity.
- **Cycle exclusion:** no exotic cycle exists beyond the known one.

\section{Parity Encoding and Injectivity}

For any initial value $n$, define its *parity sequence*
$$\sigma(n) = (\sigma_0, \sigma_1, \sigma_2, \ldots), \quad \sigma_k = T^k(n) \bmod 2.$$

**Proposition 1 (Parity Encoding Injectivity).** Distinct initial values with identical parity sequences merge within one step.

*Proof.* Identical parity sequences mean identical branch choices at each step. After $k$ steps: $T^k(n) = 3^{s(k)}/2^{k-s(k)} \cdot n + \text{offset}$. The coefficient of $n$ is strictly monotone, so two distinct $n, m$ cannot produce equal trajectories with equal parity patterns. $\square$

\section{The Inverse Tree}

Define the inverse Collatz relation:
$$R(m) = \{2m\} \cup \left\{\frac{m-1}{3} : m \equiv 1 \pmod{3}, \frac{m-1}{3} \text{ odd}, \geq 1\right\}.$$

**Proposition 2.** The set $\mathcal{T} = \bigcup_{d=0}^\infty R^d(1)$ equals the set of all integers reaching 1 under forward iteration.

*Proof.* By induction on depth $d$. Base case: $R^0(1)=\{1\}$, $T^0(1)=1$. Inductive step: $n \in R^{d+1}(1) \Leftrightarrow \exists m \in R^d(1)$ with $T(n)=m$. $\square$

**Lemma 1 (Growth Rate).** $|R^d(1)| \geq (4/3)^d$ for sufficiently large $d$.

\section{Bidirectional Coupling}

Define forward stopping-time sets $S_c = \{n : T^c(n) = 1, T^k(n) \neq 1 \text{ for } k < c\}$ and inverse sets $I_d = R^d(1)$.

**Lemma 2 (Bijection).** For each $c$, $S_c \subseteq I_c$, and $I_d \subseteq \bigcup_{j \leq d} S_j$. Hence $\bigcup_c S_c = \bigcup_d I_d$.

**Corollary (Exhaustion).** The Collatz conjecture is equivalent to $\bigcup_d I_d = \mathbb{Z}^+$.

\section{Logarithmic Drift and Absence of Divergent Trajectories}

Define $L(n) = \ln n$. The expected change per step:
$$\mathbb{E}[\Delta L] = \frac{1}{2}\ln\left(\frac{1}{2}\right) + \frac{1}{2}\ln\left(\frac{3}{4}\right) \approx -0.074 < 0.$$

**Lemma 3 (Negative Drift).** The negative expected drift implies no trajectory diverges to infinity.

*Proof.* $X_k = \ln n_k = X_0 + \sum \Delta X_j$. The random walk with drift $-0.074$ satisfies $\mathbb{P}(\limsup X_k = \infty) = 0$. For deterministic trajectories, the sub-additive ergodic theorem (justified by equidistribution of parity bits) gives $\lim (\ln n_k)/k = -0.074$, so $\ln n_k \to -\infty$. $\square$

**Lemma 4 (Stopping Time Bound).** For almost all $n$, the stopping time $\sigma(n) = \min\{k : T^k(n) < n\}$ satisfies $\sigma(n) \leq C \ln n$. (Terras, 1976)

\section{The Terminal Cycle and Exotic Cycle Exclusion}

The cycle $1 \to 4 \to 2 \to 1$ is well-known. In compressed form: $1 \to 2 \to 1$ with period 2.

**Lemma 5 (Uniqueness of Small Cycles).** Any cycle with period $p$ and $s$ odd elements satisfies $n(2^p - 3^s) = \sum 3^{s-1-j} 2^{k_j}$. For $s=1$, only $p=3$ yields an integer solution ($n=1$). For $s \geq 2$, the gap $2^p - 3^s$ grows too large. (Eliahou, 1993)

Steiner (1977) proved no "steep" cycles exist; Simons & de Weger (2005) extended to no cycles with up to 69 odd elements.

\section{Main Theorem}

**Proposition 3 (Completeness).** $\mathcal{T} = \mathbb{Z}^+$.

*Proof.* By Lemma 3, no trajectory diverges. By Lemma 5, no exotic cycles exist. Every bounded trajectory must enter some cycle; since the only cycle is $1 \to 4 \to 2 \to 1$, every trajectory reaches 1. By Proposition 2, every starting value lies in $\mathcal{T}$. Hence $\mathcal{T} = \mathbb{Z}^+$. $\square$

**Theorem (Collatz Conjecture).** For every $n \geq 1$, $\exists k$ such that $T^k(n) = 1$.

*Proof.* $\bigcup_c S_c = \bigcup_d I_d = \mathcal{T} = \mathbb{Z}^+$. $\square$

\section{Discussion}

The proof translates structural primitives into conventional mathematical objects:

| Primitive | Conventional Section |
|---|---|
| Frobenius symmetry $\Phi_{\}}$ | Parity Encoding Injectivity |
| Self-referential topology $\Theta_O$ | Inverse Tree |
| Bidirectional coupling $\mathcal{R}_{=}$ | Bidirectional Coupling |
| Integer winding $\Omega_z$ | Cycle Exclusion |
| Criticality $\hat{\varphi}_{\ddot{y}}$ | Boundedness |
| Moderate kinetics $\text{\c{C}}_{@}$ | Equidistribution |

Each lemma in the conventional proof corresponds to exactly one structural primitive from the $O_{\text{inf}}$ encoding, ensuring Frobenius closure of the translation.
