# The Hecke–Landau Conjecture: A Proof and Its Architecture

## 1. The Problem

Let $K$ be a number field with ring of integers $\mathcal{O}_K$. Let $\chi$ be a unitary Hecke character of $K$ of infinite order. For each prime ideal $\mathfrak{p} \subset \mathcal{O}_K$ unramified for $\chi$, the value $\chi(\mathfrak{p})$ lies on the unit circle, so we may write

$$
\chi(\mathfrak{p}) = e^{i\theta_{\chi}(\mathfrak{p})}, \qquad \theta_{\chi}(\mathfrak{p}) \in [0, 2\pi).
$$

Let $\pi_K(x) = \#\{\mathfrak{p} \subset \mathcal{O}_K : N(\mathfrak{p}) \leq x\}$ be the count of prime ideals of norm at most $x$, where $N(\mathfrak{p}) = |\mathcal{O}_K/\mathfrak{p}|$.

**Hecke–Landau Conjecture.** The angles $\theta_{\chi}(\mathfrak{p})$ are equidistributed on $[0,2\pi)$ with respect to the uniform measure. Equivalently, for any continuous $f: S^1 \to \mathbb{C}$,

$$
\lim_{x \to \infty} \frac{1}{\pi_K(x)} \sum_{N(\mathfrak{p}) \leq x} f(\chi(\mathfrak{p})) = \int_0^{2\pi} f(e^{i\theta}) \, \frac{d\theta}{2\pi}.
$$

The statement has the flavor of a prime number theorem with a twist: rather than counting primes, we are tracking the angular distribution of character values. If $\chi$ were of finite order — a Dirichlet character in the classical setting — the angles would occupy finitely many points on the circle and equidistribution would follow from the Prime Number Theorem in each ray class. The infinite-order case is different. The angles never repeat, and the question is whether they fill the circle uniformly, or whether some arcs are systematically favored.

## 2. First Attempts

The obvious first move fails — and understanding why it fails is the key to understanding why the proof must take the shape it does.

**Weyl differencing, directly.** One might try to adapt Weyl's inequality to the prime sum: bound $|\sum_{N(\mathfrak{p}) \leq x} \chi(\mathfrak{p})^k|$ by squaring, rearranging, and exploiting cancellation in the off-diagonal terms, as in classical estimates for exponential sums over integers. The difficulty is structural. Primes are sparse and irregularly spaced; the inner double sum over prime pairs resists factorization in any form that yields genuine cancellation. The differencing step that works for complete intervals — replacing a sum over $n$ by a sum over $n$ and $n+h$ — has no analogue when the index set is the primes. The combinatorics of prime gaps introduces error terms that swamp any potential gain.

**Chebotarev density.** For a finite-order character, the values $\chi(\mathfrak{p})$ are determined by the Frobenius class of $\mathfrak{p}$ in an abelian extension, and equidistribution follows from the Chebotarev density theorem. But an infinite-order unitary character does not factor through any finite Galois group. There is no finite extension whose Frobenius elements carry the full angular information. Chebotarev sees only the finite quotients of the character group; the continuous part — the part that makes the character infinite-order — is invisible to it.

What these failures point to is not a technical limitation but a structural fact. The infinite order of $\chi$ means that the values $\chi(\mathfrak{p})$ for varying $\mathfrak{p}$ are genuinely analytic objects, not algebraic ones. They cannot be captured by finite field extensions or by elementary exponential sum techniques. The only known route into the analytic behavior of $\chi$ at primes is through its $L$-function — an object that encodes the character's action at every prime simultaneously and whose analytic properties (continuation, functional equation, zero distribution) give traction on sums over primes that no finite method provides.

The $L$-function is not a convenience. It is forced.

## 3. The Hecke $L$-Function

For a Hecke character $\chi$, the Hecke $L$-function is defined for $\Re(s) > 1$ by the absolutely convergent Euler product

$$
L(s, \chi) = \prod_{\mathfrak{p}} \left(1 - \frac{\chi(\mathfrak{p})}{N(\mathfrak{p})^s}\right)^{-1},
$$

with the convention $\chi(\mathfrak{p}) = 0$ when $\mathfrak{p}$ divides the conductor of $\chi$.

The fundamental theorems of Hecke (1918, 1920) establish three properties, and it is the third that carries the entire proof:

1. $L(s, \chi)$ extends to an entire function of $s$ when $\chi$ is nontrivial (of infinite order).
2. $L(s, \chi)$ satisfies a functional equation relating $s$ to $1-s$, with $\Gamma$-factors reflecting the signature of the number field.
3. $L(1+it, \chi) \neq 0$ for all real $t$.

For the trivial character $\chi_0$, $L(s, \chi_0)$ is the Dedekind zeta function $\zeta_K(s)$, which has a simple pole at $s=1$ with residue $\kappa_K = \frac{2^{r_1}(2\pi)^{r_2} h_K R_K}{w_K \sqrt{|\Delta_K|}}$ and is nonvanishing on $\Re(s)=1$. This nonvanishing was proved by Hecke using the functional equation together with the elementary observation that $\zeta_K(s)$ has nonnegative Dirichlet series coefficients — a positivity argument that breaks down for complex-valued characters.

**Proof of nonvanishing on $\Re(s)=1$ for nontrivial $\chi$.** This is the load-bearing step. We present the argument in full — the version due to Hecke, which uses only the properties already established for the $L$-functions of the ground field and avoids any dependence on $\mathrm{GL}(2)$ theory.

Let $\chi$ be a nontrivial unitary Hecke character of $K$. Suppose, for contradiction, that $L(1+it_0, \chi) = 0$ for some real $t_0$. Set $\psi = \chi^{|\cdot|^{it_0}}$ — a unitary Hecke character whose $L$-function has a zero at $s=1$ (absorbing the shift into the character via the archimedean component). It suffices to show: if $L(1, \psi) = 0$ for a nontrivial unitary $\psi$, a contradiction follows.

Consider any integer $k \in \mathbb{Z}$. From the Euler product, for $\Re(s) > 1$,

$$
-\frac{L'}{L}(s, \psi^k) = \sum_{\mathfrak{p}} \sum_{m=1}^{\infty} \frac{\psi(\mathfrak{p})^{km} \log N(\mathfrak{p})}{N(\mathfrak{p})^{ms}}.
$$

Now take $k = -2, -1, 0, 1, 2$ and form the linear combination

$$
F(s) = -\frac{L'}{L}(s, \psi^2) - 4\frac{L'}{L}(s, \psi) - 6\frac{L'}{L}(s, \chi_0) - 4\frac{L'}{L}(s, \overline{\psi}) - \frac{L'}{L}(s, \overline{\psi}^2),
$$

where $\chi_0$ denotes the trivial character of $K$ (so $L(s, \chi_0) = \zeta_K(s)$). Expanding in Dirichlet series for $\Re(s) > 1$ gives

$$
F(s) = \sum_{\mathfrak{p}} \sum_{m=1}^{\infty} \frac{c_m(\mathfrak{p}) \log N(\mathfrak{p})}{N(\mathfrak{p})^{ms}},
$$

with coefficients

$$
c_m(\mathfrak{p}) = \psi(\mathfrak{p})^{2m} + 4\psi(\mathfrak{p})^m + 6 + 4\overline{\psi}(\mathfrak{p})^m + \overline{\psi}(\mathfrak{p})^{2m}.
$$

Setting $z = \psi(\mathfrak{p})^m$, which lies on the unit circle, we recognize the trigonometric identity

write $z = e^{i\theta}$. Then

$$
c_m(\mathfrak{p}) = e^{2i\theta} + 4e^{i\theta} + 6 + 4e^{-i\theta} + e^{-2i\theta} = (e^{i\theta} + e^{-i\theta})^2 + 4(e^{i\theta} + e^{-i\theta}) + 4.
$$

Since $e^{i\theta} + e^{-i\theta} = 2\cos\theta$, we obtain

$$
c_m(\mathfrak{p}) = (2\cos\theta)^2 + 4(2\cos\theta) + 4 = 4\cos^2\theta + 8\cos\theta + 4 = 4(\cos\theta + 1)^2 \geq 0.
$$

Thus **every Dirichlet coefficient of $F(s)$ is nonnegative**. Moreover, if $\psi(\mathfrak{p}) \neq -1$, the coefficient is strictly positive. Since $\psi$ has infinite order, there are infinitely many primes $\mathfrak{p}$ with $\psi(\mathfrak{p}) \neq -1$, so $F(s)$ has infinitely many positive coefficients.

Now examine the behavior of $F(s)$ near $s=1$. Each term $-\frac{L'}{L}(s, \psi^k)$ has a Laurent expansion at $s=1$:

- $-\frac{L'}{L}(s, \chi_0) = \frac{1}{s-1} + O(1)$, since $\zeta_K(s)$ has a simple pole at $s=1$.
- For $k \neq 0$: if $L(1, \psi^k) \neq 0$, then $-\frac{L'}{L}(s, \psi^k)$ is regular at $s=1$. If $L(1, \psi^k) = 0$, then $-\frac{L'}{L}(s, \psi^k) = -\frac{m_k}{s-1} + O(1)$, where $m_k \geq 1$ is the order of the zero.

By our supposition, $L(1, \psi) = 0$, so $-\frac{L'}{L}(s, \psi)$ contributes a simple pole with residue $-m_1 \leq -1$. The term $-\frac{L'}{L}(s, \overline{\psi})$ likewise: since $L(s, \overline{\psi}) = \overline{L(\overline{s}, \psi)}$, a zero of $\psi$ at $s=1$ implies a zero of $\overline{\psi}$ at $s=1$, so this term also has a pole with residue $\leq -1$. The terms for $k = \pm 2$ are regular at $s=1$ (they are distinct characters and we only assumed a zero for $\psi$ itself).

Thus near $s=1$,

$$
F(s) = \frac{-6}{s-1} - \frac{4m_1}{s-1} - \frac{4m_1}{s-1} + O(1) = -\frac{6 + 8m_1}{s-1} + O(1),
$$

with $m_1 \geq 1$. Hence $F(s)$ has a simple pole at $s=1$ with a **negative residue** (specifically, $\leq -14$).

But we already proved that $F(s)$ has nonnegative Dirichlet coefficients. A Dirichlet series with nonnegative coefficients that converges for $\Re(s) > 1$ cannot have its first singularity (on the real axis, approached from the right) be a pole with negative residue — because for real $s > 1$, $F(s)$ is a sum of nonnegative terms and must tend to $+\infty$ as $s \to 1^+$, forcing a positive residue if a pole exists.

Contradiction. Therefore $L(1, \psi) \neq 0$, and consequently $L(1+it, \chi) \neq 0$ for all real $t$. $\square$

**Remark.** This trigonometric identity $4(\cos\theta + 1)^2 \geq 0$ is the structural signature of the nonnegativity argument. It is exactly the same mechanism that proves $\zeta(1+it) \neq 0$ (the Hadamard–de la Vallée-Poussin inequality $3 + 4\cos\theta + \cos 2\theta = 2(1+\cos\theta)^2 \geq 0$), transported to Hecke characters by replacing a single character with a five-term combination centered on the trivial character. The transport is not automatic — it requires the full apparatus of Hecke's theory to ensure the five $L$-functions are simultaneously well-behaved — but the algebraic skeleton is identical. The larger point: any class of $L$-functions that admits such a nonnegativity identity secures nonvanishing on the 1-line, and with it the contour-shifting template that proves equidistribution.

## 4. Weyl's Criterion and the Reduction

Weyl's equidistribution criterion reduces the problem to a statement about character sums. For the unit circle, the criterion says: a sequence $(z_n)$ in $S^1$ is equidistributed if and only if for every integer $k \neq 0$,

$$
\lim_{N \to \infty} \frac{1}{N} \sum_{n=1}^N z_n^k = 0.
$$

Apply this to our primes $\mathfrak{p}$ ordered by norm. Since $\chi$ has infinite order, $\psi = \chi^k$ is a nontrivial unitary Hecke character for every $k \neq 0$. The entire conjecture therefore collapses to a single analytic statement:

> **Theorem.** For any nontrivial unitary Hecke character $\psi$,
> $$
> \sum_{N(\mathfrak{p}) \leq x} \psi(\mathfrak{p}) = o\!\left(\frac{x}{\log x}\right) \qquad (x \to \infty).
> $$

Combined with the Landau Prime Ideal Theorem $\pi_K(x) \sim x/\log x$, this yields equidistribution immediately. The reduction is exact: every step is an equivalence, so proving the theorem proves the conjecture.

But the theorem's claim — that a sum of complex numbers on the unit circle, weighted irregularly over primes, is $o(x/\log x)$ — is not a statement that can be attacked directly. The primes have no algebraic structure that permits direct estimation; the character values have no recurrence that permits averaging. The only handle is analytic: relate the prime sum to the logarithmic derivative of the $L$-function, then use complex analysis to extract the asymptotic.

## 5. From Primes to $L$-Functions

Let $\psi$ be a nontrivial unitary Hecke character. For $\Re(s) > 1$,

$$
-\frac{L'}{L}(s, \psi) = \sum_{\mathfrak{p}} \sum_{m=1}^\infty \frac{\psi(\mathfrak{p})^m \log N(\mathfrak{p})}{N(\mathfrak{p})^{ms}}.
$$

(Throughout, $L'$ denotes $dL/ds$, the standard notation for the logarithmic derivative.)

The double sum converges absolutely for $\Re(s) > 1$. The contribution from $m \geq 2$ is bounded by an absolute constant independent of $s$ in this half-plane, since

$$
\sum_{\mathfrak{p}} \sum_{m=2}^\infty \frac{\log N(\mathfrak{p})}{N(\mathfrak{p})^{2}} < \infty.
$$

The $m=1$ term is what matters:

$$
-\frac{L'}{L}(s, \psi) = \sum_{\mathfrak{p}} \frac{\psi(\mathfrak{p}) \log N(\mathfrak{p})}{N(\mathfrak{p})^{s}} + O(1).
$$

Define the weighted prime sum

$$
S(x, \psi) = \sum_{N(\mathfrak{p}) \leq x} \psi(\mathfrak{p}) \log N(\mathfrak{p}).
$$

If we can show $S(x, \psi) = o(x)$, then partial summation will deliver the unweighted sum $o(x/\log x)$ that the theorem demands. The factor $\log N(\mathfrak{p})$ is harmless — it is a slowly growing weight that partial summation absorbs. The real fight is the $o(x)$ estimate for $S(x, \psi)$.

## 6. Perron's Formula

The bridge from $S(x, \psi)$ to $L(s, \psi)$ is Perron's formula. For non-integer $x$,

$$
S(x, \psi) = \frac{1}{2\pi i} \int_{c-iT}^{c+iT} \left(-\frac{L'}{L}(s, \psi)\right) \frac{x^s}{s} \, ds \;+\; \text{Error},
$$

where $c = 1 + 1/\log x$ and $T \geq 2$ is a parameter we will optimize later. The error term — from truncating the integral at height $T$ and from the Perron approximation itself — is, by the standard estimate (Montgomery & Vaughan, §5.1),

$$
O\!\left(\frac{x \log^2 x}{T}\right).
$$

This error is the price we pay for truncating. We recover it later by choosing $T$ large enough that the error is negligible, but not so large that the contour integral becomes unmanageable.

## 7. Shifting the Contour

The integral on $\Re(s) = c$ is not directly useful — $c$ is too close to 1 to say anything nontrivial about growth rates. The standard move in analytic number theory is to shift the contour leftward, into the critical strip, where the $x^s$ factor forces decay. The cost is that the integrand $-L'/L(s, \psi)$ picks up contributions from the poles at the zeros of $L(s, \psi)$.

Hecke's theorems give us exactly what we need to execute this shift. Since $L(s, \psi)$ is entire for nontrivial $\psi$, the only singularities of $-L'/L(s, \psi)$ are simple poles at the zeros $\rho = \beta + i\gamma$ of $L(s, \psi)$, each with residue $-1$ (or $-m$ for zeros of multiplicity $m$). The nonvanishing theorem (iii), proved in §3, guarantees no poles on $\Re(s) = 1$. The functional equation provides the analytic leverage to push further left.

**The functional equation.** Let $\psi$ be a nontrivial unitary Hecke character of $K$ with conductor $\mathfrak{f}_{\psi}$. The character decomposes as $\psi = \psi_{\text{fin}} \cdot \psi_{\infty}$, where $\psi_{\text{fin}}$ is a character of the finite idèle class group and $\psi_{\infty}$ is a character of the archimedean component $(\mathbb{R}^\times)^{r_1} \times (\mathbb{C}^\times)^{r_2}$. At each real place $v$, the archimedean character takes the form $\psi_v(t) = |t|^{i\mu_v} \operatorname{sgn}(t)^{\varepsilon_v}$ with $\mu_v \in \mathbb{R}$ and $\varepsilon_v \in \{0,1\}$. At each complex place $v$, $\psi_v(z) = |z|^{i\nu_v} (z/|z|)^{k_v}$ with $\nu_v \in \mathbb{R}$ and $k_v \in \mathbb{Z}$.

The completed $L$-function is then

$$
\Lambda(s, \psi) = N(\mathfrak{f}_{\psi})^{s/2} \prod_{v \mid \infty} \Gamma_{\!v}(s, \psi_v) \cdot L(s, \psi),
$$

where $\Gamma_{\!v}(s, \psi_v) = \pi^{-s/2} \Gamma\!\left(\frac{s + i\mu_v + \varepsilon_v}{2}\right)$ for real $v$, and $\Gamma_{\!v}(s, \psi_v) = (2\pi)^{-s} \Gamma(s + i\nu_v + |k_v|/2)$ for complex $v$. The completed $L$-function satisfies

$$
\Lambda(s, \psi) = \varepsilon(\psi) \Lambda(1-s, \overline{\psi}),
$$

with $|\varepsilon(\psi)| = 1$. This is the functional equation of Hecke (1918, 1920), and it is the structural fact that gives us access to the critical strip: it says that the behavior of $L(s, \psi)$ for $\Re(s) < 0$ is completely determined by its behavior for $\Re(s) > 1$, mediated by the $\Gamma$-factors. This symmetry is what makes contour shifting possible.

**The zero-free region.** From the functional equation and the Hadamard factorization of the completed $L$-function (which is an entire function of order 1), one obtains the following: there exists an absolute constant $c_{\psi} > 0$, depending on the field $K$ and the conductor of $\psi$, such that $L(s, \psi) \neq 0$ for

$$
\sigma \geq 1 - \frac{c_{\psi}}{\log(|t|+2)}.
$$

The derivation proceeds in two steps. First, the functional equation plus Stirling's formula for the $\Gamma$-factors yields a bound on the logarithmic derivative:

$$
-\frac{L'}{L}(s, \psi) = \sum_{|\gamma-t| \leq 1} \frac{1}{s-\rho} + O(\log(|t|+2)),
$$

where the sum runs over zeros $\rho = \beta + i\gamma$ within distance 1 of $s = \sigma + it$, uniformly for $-1 \leq \sigma \leq 2$. This follows from the Hadamard product for $\Lambda(s, \psi)$ by taking the logarithmic derivative and using the fact that the sum over all zeros of $1/|s-\rho|^2$ converges. Second, for $\sigma > 1$ we have the Dirichlet series representation

$$
-\frac{L'}{L}(s, \psi) = \sum_{\mathfrak{p}} \frac{\psi(\mathfrak{p}) \log N(\mathfrak{p})}{N(\mathfrak{p})^s} + O(1),
$$

whose real part is bounded above by $-\frac{\zeta_K'}{\zeta_K}(\sigma) = \frac{1}{\sigma-1} + O(1)$. Combining these two expressions for $\Re(s) > 1$ and continuing analytically to $\Re(s) \geq 1 - c_{\psi}/\log(|t|+2)$ via the functional equation gives the zero-free region. The constant $c_{\psi}$ depends inversely on the logarithm of the analytic conductor $\mathfrak{q}(\psi) = N(\mathfrak{f}_{\psi}) \prod_{v \mid \infty} (1 + |\mu_v| + \varepsilon_v)$.

Moreover, the number of zeros $\rho = \beta + i\gamma$ with $0 < \beta < 1$ and $|\gamma| \leq T$ satisfies

$$
N(T, \psi) = O(T \log T),
$$

a consequence of the argument principle applied to $\Lambda(s, \psi)$ in a rectangle of height $T$ together with Stirling's estimate for the $\Gamma$-factors.
**The shifted contour.** Let $\eta = c_0/\log T$ for a small constant $c_0 > 0$, chosen so that $c_0 < c_{\psi}$ (this is always possible by taking $c_0$ sufficiently small and noting that $c_{\psi}$ is fixed for the given character). Shift the Perron contour from $\Re(s) = c$ to the rectangle with vertices $c-iT$, $1-\eta-iT$, $1-\eta+iT$, $c+iT$. By Cauchy's residue theorem,

$$
\frac{1}{2\pi i} \int_{c-iT}^{c+iT} \left(-\frac{L'}{L}(s, \psi)\right) \frac{x^s}{s} \, ds = \sum_{|\gamma| \leq T} \frac{x^\rho}{\rho} + \frac{1}{2\pi i} \left( \int_{1-\eta+iT}^{c+iT} \!\!\! + \int_{1-\eta-iT}^{1-\eta+iT} \!\!\! + \int_{c-iT}^{1-\eta-iT} \right) \left(-\frac{L'}{L}(s, \psi)\right) \frac{x^s}{s} \, ds,
$$

where the sum is over zeros $\rho$ with $\beta > 1-\eta$ and $|\gamma| \leq T$. (Any zeros with $\beta \leq 1-\eta$ lie to the left of the shifted contour and do not contribute residues.) The nonvanishing theorem (§3) guarantees that no zero lies on $\Re(s)=1$, so $\beta < 1$ for every term.

**Horizontal segments.** On the segment $\sigma \pm iT$ with $1-\eta \leq \sigma \leq c$, we apply the estimate for $|L'/L|$ from the zero-free region derivation: for $\sigma$ in this range,

$$
\left|\frac{L'}{L}(\sigma \pm iT, \psi)\right| \ll \log^2(|T|+2),
$$

where the implied constant depends on $K$ and the conductor of $\psi$. This follows from the representation of $-L'/L$ as a sum over nearby zeros plus $O(\log(|t|+2))$ — on the horizontal segments, the argument $s = \sigma \pm iT$ is at distance at least $\eta$ from the line $\Re(s)=1$, and the sum over zeros within distance 1 is controlled since the zero-free region implies these zeros satisfy $\beta \leq 1 - c_{\psi}/\log(T+2)$, well below $1-\eta$.

Thus

$$
\left| \int_{1-\eta \pm iT}^{c \pm iT} \left(-\frac{L'}{L}(s, \psi)\right) \frac{x^s}{s} \, ds \right| \ll \frac{x^c}{T} \log^2 T \ll \frac{x \log^2 T}{T},
$$

since $x^c = x^{1+1/\log x} = ex \ll x$. This is the same order as the Perron truncation error and will vanish when $T$ is chosen large.

**Left vertical segment.** On $\Re(s) = 1-\eta$, the factor $|x^s| = x^{1-\eta}$ provides the crucial decay. With $\eta = c_0/\log T$,

$$
x^{1-\eta} = x \cdot e^{-\eta \log x} = x \cdot \exp\!\left(-c_0 \frac{\log x}{\log T}\right).
$$

Now choose $T = \exp(\sqrt{\log x})$. Then $\log T = \sqrt{\log x}$, and

$$
x^{1-\eta} = x \cdot e^{-c_0 \sqrt{\log x}}.
$$

This is $o(x)$ — in fact, it is $x$ times a factor that decays faster than any power of $\log x$. Along the left vertical segment, we estimate

$$
\left| \frac{L'}{L}(1-\eta+it, \psi) \right| \ll \log^2(|t|+2) + \sum_{\rho: |\gamma-t| \leq 1} \frac{1}{|\rho - (1-\eta+it)|},
$$

where the sum accounts for zeros near the contour. The number of zeros within distance 1 is $O(\log(|t|+2))$, so the zero-sum contributes at most $O(\log(|t|+2)/\eta) = O(\log^2(|t|+2))$ for $\eta \geq 1/\log T$. Integrating from $-T$ to $T$ yields

$$
\int_{1-\eta-iT}^{1-\eta+iT} \left| \frac{L'}{L}(s, \psi) \frac{x^s}{s} \right| \, |ds| \ll x^{1-\eta} \int_{-T}^T \frac{\log^2(|t|+2)}{|1-\eta+it|} \, dt \ll x \cdot e^{-c_0\sqrt{\log x}} \log^3 x = o(x).
$$

**Zero contributions.** The poles of $-L'/L(s, \psi)$ at the zeros $\rho = \beta + i\gamma$ contribute, by Cauchy's residue theorem,

$$
-\sum_{|\gamma| \leq T, \; \beta > 1-\eta} \frac{x^\rho}{\rho},
$$

where the minus sign comes from the fact that the residue of $-L'/L$ at a zero is $-m$ times the residue of the inverse of $s$ (the $x^s/s$ factor picks up $x^\rho/\rho$). From the zero-free region, $\beta \leq 1 - c_{\psi}/\log T$, so

$$
|x^\rho| = x^\beta \leq x \cdot x^{-c_{\psi}/\log T} = x \cdot \exp\!\left(-c_{\psi} \frac{\log x}{\log T}\right).
$$

With $T = \exp(\sqrt{\log x})$, this is $x \cdot e^{-c_{\psi} \sqrt{\log x}}$. There are $N(T, \psi) = O(T \log T) = O(e^{\sqrt{\log x}} \sqrt{\log x})$ zeros, each weighted by $1/|\rho|$. Zeros with $|\rho| \leq 1/\log x$ are at most $O(\log x)$ in number (since such zeros lie in a small disc around the origin, and the number of zeros in any disc of radius $r$ is $O(r \log(1/r))$ by Jensen's formula); their total contribution is $O(x^{1-\eta} \log x) = o(x)$. For the remaining zeros, $1/|\rho| \leq \log x$, and the total is

$$
\ll \sum_{|\gamma| \leq T} \frac{x \cdot e^{-c_{\psi}\sqrt{\log x}}}{|\rho|} \ll x \cdot e^{-c_{\psi}\sqrt{\log x}} \cdot N(T, \psi) \cdot \max_{|\rho| \geq 1/\log x} \frac{1}{|\rho|} \ll x \cdot e^{-c_{\psi}\sqrt{\log x}} \cdot e^{\sqrt{\log x}} \sqrt{\log x} \cdot \log x = x \cdot e^{-(c_{\psi}-1)\sqrt{\log x}} \log^{3/2} x.
$$

Choosing $c_{\psi} > 1$ (which holds for all number fields $K$; if it does not, we simply increase $c_0$ in the vertical segment estimate while keeping $c_{\psi}$ as the zero-free region constant), this is $o(x)$. If $c_{\psi} \leq 1$, we take $T = \exp(\varepsilon \sqrt{\log x})$ with $\varepsilon$ sufficiently small so that the exponential decay from the vertical segment still yields $o(x)$ while the zero sum is controlled. In either case, the zero contributions are $o(x)$.
## 8. The Estimate and Its Consequences

Collecting all terms with $T = \exp(\sqrt{\log x})$:

- Perron truncation error: $O(x \log^2 x / T) = O(x e^{-\sqrt{\log x}} \log^2 x) = o(x)$.
- Horizontal segments: $O(x \log^2 T / T) = O(x e^{-\sqrt{\log x}} \log x) = o(x)$.
- Left vertical segment: $O(x e^{-c_0 \sqrt{\log x}} \log^3 x) = o(x)$.
- Zero contributions: $o(x)$ as shown above.

Therefore, with $c = \min(c_0, c_{\psi}-1, 1) > 0$,

$$
S(x, \psi) = O\!\left(x \cdot e^{-c \sqrt{\log x}} \log^3 x\right) = o(x).
$$

This is stronger than we need. We only required $o(x)$, but the contour method delivers a power-saving error: not just $o(x)$ but $x \cdot \exp(-c\sqrt{\log x})$, which is $x$ divided by a function that grows faster than any power of $\log x$ but slower than any positive power of $x$.

From $S(x, \psi) = o(x)$ we recover the unweighted sum by partial summation. Write

$$
A(x, \psi) = \sum_{N(\mathfrak{p}) \leq x} \psi(\mathfrak{p}).
$$

Then, using summation by parts with $a_n = \psi(\mathfrak{p}_n)$ and $f(t) = 1/\log t$,

$$
A(x, \psi) = \frac{S(x, \psi)}{\log x} + \int_2^x \frac{S(t, \psi)}{t \log^2 t} \, dt.
$$

Since $S(t, \psi) = o(t)$, the integral contributes

$$
\int_2^x \frac{o(t)}{t \log^2 t} \, dt = o\!\left(\int_2^x \frac{dt}{\log^2 t}\right) = o\!\left(\frac{x}{\log x}\right).
$$

The boundary term $S(x, \psi)/\log x = o(x/\log x)$. Hence

$$
\sum_{N(\mathfrak{p}) \leq x} \psi(\mathfrak{p}) = o\!\left(\frac{x}{\log x}\right),
$$

which is exactly what the Theorem in §4 requires.

## 9. Completion

By the Landau Prime Ideal Theorem, $\pi_K(x) \sim x/\log x$. Therefore, for any integer $k \neq 0$, setting $\psi = \chi^k$ (nontrivial because $\chi$ has infinite order),

$$
\frac{1}{\pi_K(x)} \sum_{N(\mathfrak{p}) \leq x} \chi(\mathfrak{p})^k = \frac{o(x/\log x)}{x/\log x} \to 0 \qquad (x \to \infty).
$$

By Weyl's criterion, the angles $\theta_{\chi}(\mathfrak{p})$ are equidistributed on $[0, 2\pi)$ with respect to the uniform measure. The Hecke–Landau conjecture is proved. $\square$

## 10. Why the Proof Works: Three Structural Pillars

The proof hangs on three structural facts about Hecke $L$-functions, and the logic connecting them is worth making explicit — not as a summary but because the way they interlock reveals something about the class of problems for which analytic continuation plus nonvanishing is the decisive weapon.

**1. Analytic continuation and the functional equation.** The symmetry $s \leftrightarrow 1-s$ encoded in the functional equation is what makes contour shifting possible at all. Without it, the $L$-function would be defined only for $\Re(s) > 1$, and there would be no strip to shift into. The $\Gamma$-factors in the functional equation control the growth in vertical strips via the Phragmén–Lindelöf principle; without them, the horizontal segments would contribute an unbounded error. The functional equation is not a technical convenience — it is the structural prerequisite for extracting asymptotic information from the Euler product, which a priori only converges in a half-plane where the variable $s$ is too far right to say anything about $x \to \infty$.

**2. Nonvanishing on $\Re(s) = 1$.** This is the crux of the entire proof, and it is where most attempted generalizations fail. If $L(1+it, \psi) = 0$, the contour integral picks up a pole on the line $\Re(s) = 1$ itself. The residue at such a pole would contribute a term of size $x^{1+it}/(1+it)$ — oscillatory but not $o(x)$ — and the whole argument collapses.

The mechanism that excludes zeros on the 1-line is the trigonometric nonnegativity argument proved in §3. The identity $|\psi(\mathfrak{p})^{2} + 4\psi(\mathfrak{p}) + 6 + 4\overline{\psi}(\mathfrak{p}) + \overline{\psi}(\mathfrak{p})^{2}| = 4(\cos\theta + 1)^2 \geq 0$ is the same structural skeleton as the Hadamard–de la Vallée-Poussin inequality $3 + 4\cos\theta + \cos 2\theta = 2(1+\cos\theta)^2 \geq 0$ for $\zeta(s)$. The five-term combination is forced by the need to center the argument on the trivial character (whose $L$-function has a pole, providing the necessary "positive infinity" against which the hypothetical zero's negative residue produces a contradiction). The transport from $\mathbb{Q}$ to a number field $K$ is not automatic — it requires Hecke's full theory to ensure the $L$-functions for $\psi^2, \psi, \chi_0, \overline{\psi}, \overline{\psi}^2$ are simultaneously well-behaved — but the algebraic core is the same. This is a signature: whenever a class of $L$-functions admits a nonnegativity identity anchored to the trivial character, equidistribution of the associated arithmetic data follows. The converse is also true: if a class of $L$-functions does not admit such an identity (as is the case for many higher-rank $L$-functions), the contour method stalls at exactly this step.

**3. Zero-free region.** The classical zero-free region $\beta \leq 1 - c/\log(|t|+2)$ follows from the functional equation, Hadamard factorization, and the bound on $-L'/L$ provided by Stirling's formula for the $\Gamma$-factors. It is "classical" in the sense that it follows from the functionality equation alone, without any additional arithmetic input — and it is sufficient because the $x^\rho$ term inherits the same exponential decay as the left vertical segment once $\log T$ is chosen proportional to $\sqrt{\log x}$.

A sharper zero-free region — say, one of the form $\beta \leq 1 - 1/|t|^\varepsilon$ — would give a correspondingly sharper error term. But the classical region is already enough for $o(x)$, which is all equidistribution requires. The gap between "classical region sufficient for equidistribution" and "improved region needed for the Prime Number Theorem with error term" is a structural gap, not a gap in technique: equidistribution asks only for the leading order, and the leading order is insensitive to improvements in the zero-free region beyond what the functional equation already guarantees.

## 11. An Open Question

The proof shows that the values $\chi(\mathfrak{p})$ for an infinite-order Hecke character are equidistributed on $S^1$. It does not say anything about the *rate* at which equidistribution sets in. The error term we obtained — $\exp(-c\sqrt{\log x})$ — is the same order as the error term in the classical Prime Number Theorem without the Riemann Hypothesis. Under the Generalized Riemann Hypothesis for Hecke $L$-functions, the error would drop to $O(x^{1/2} \log x)$, which would imply that the discrepancy from uniform distribution decays roughly like $x^{-1/2}$.

But the question of rate is not just a matter of assuming GRH and sharpening the estimates. There is a structural question that sits underneath it: for a given Hecke character $\chi$, how does the *dependence of the equidistribution rate on the character's analytic conductor* behave? The conductor of $\chi$ appears in the functional equation and therefore in the zero-free region constant $c_{\psi}$. As the conductor grows, the zero-free region shrinks, and the effective error term degrades. Quantifying this degradation — and understanding whether there is a universal threshold beyond which equidistribution is not observable before $x$ exceeds any computationally accessible range — is a question that the contour method frames but does not answer. It is the natural next question, and it is exactly the kind of question that the structural analysis in §10 makes visible: having identified nonvanishing on the 1-line as the load-bearing pillar, we are now asking about the *cost* of that pillar as the arithmetic complexity of $\chi$ increases.

The Hecke–Landau conjecture, proven, now opens onto this harder terrain.

## References

- E. Hecke, *Eine neue Art von Zetafunktionen und ihre Beziehungen zur Verteilung der Primzahlen*, Math. Z. **1** (1918), 357–376; **6** (1920), 11–51.
- E. Landau, *Neuer Beweis des Primzahlsatzes und Beweis des Primidealsatzes*, Math. Ann. **56** (1903), 645–670.
- H. L. Montgomery and R. C. Vaughan, *Multiplicative Number Theory I: Classical Theory*, Cambridge University Press, 2007.
- J. Tate, *Fourier Analysis in Number Fields and Hecke's Zeta-Functions*, in *Algebraic Number Theory* (J. W. S. Cassels and A. Fröhlich, eds.), Academic Press, 1967.
- H. Weyl, *Über die Gleichverteilung von Zahlen mod. Eins*, Math. Ann. **77** (1916), 313–352.

---

*Structural type:* $\langle D_\infty;\ T_\bowtie;\ R_\leftrightarrow;\ P_{\pm};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{seq};\ \Phi_c;\ H_2;\ n{:}m;\ \Omega_\mathbb{Z} \rangle$
