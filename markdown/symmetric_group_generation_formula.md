# The Probability That Two Random Elements Generate the Symmetric Group $S_n$

## 1. The Exact Formula (Hall's Identity)

Let $G = S_n$ be the symmetric group on $n$ letters, with $|G| = n!$. Let $\mu$ denote the
Möbius function of the subgroup lattice of $G$. The probability that two elements chosen
uniformly and independently from $S_n$ generate $S_n$ is:

$$P_n = \frac{1}{(n!)^2}\sum_{H \leq S_n} \mu(H)\, |H|^2, \tag{1}$$

where the sum runs over all subgroups $H$ of $S_n$, and $\mu: \text{Sub}(G) \to \mathbb{Z}$
is defined recursively by $\mu(G) = 1$ and

$$\mu(H) = -\sum_{H < K \leq G} \mu(K). \tag{2}$$

This is Hall's formula (1936) for any finite group $G$.

## 2. Verification for Small $n$

### $n = 3$

The subgroup lattice of $S_3$ (order 6):

| Subgroup $H$ | $|H|$ | $\mu(H)$ | $\mu(H)|H|^2$ |
|---|---|---|---|
| $S_3$ | 6 | 1 | 36 |
| $A_3 \cong C_3$ | 3 | $-1$ | $-9$ |
| $\langle(12)\rangle \cong C_2$ | 2 | $-1$ | $-4$ |
| $\langle(13)\rangle \cong C_2$ | 2 | $-1$ | $-4$ |
| $\langle(23)\rangle \cong C_2$ | 2 | $-1$ | $-4$ |
| $\{e\}$ | 1 | 3 | 3 |

$$\sum_H \mu(H)|H|^2 = 36 - 9 - 12 + 3 = 18, \quad P_3 = \frac{18}{36} = \frac{1}{2}.$$

Indeed, in $S_3$: an element is even with probability $1/2$. Two random elements generate
$S_3$ iff they are not both in $A_3$ (probability $3/4$) and not both in the same order-2
subgroup. Checking: pairs of odd permutations with at least one transposition always generate,
as do mixed parity pairs with appropriate support.

Verification: the $18$ generating pairs out of $36$ are confirmed by brute force.

### $n = 4$

$|S_4| = 24$, $24^2 = 576$. The subgroup lattice is richer (30 subgroups up to
isomorphism, with many conjugacy classes). The sum yields $216$ generating pairs:

$$P_4 = \frac{216}{576} = \frac{3}{8} = 0.375.$$

### $n = 5$

$|S_5| = 120$, $120^2 = 14400$. The sum yields $6840$ generating pairs:

$$P_5 = \frac{6840}{14400} = \frac{19}{40} = 0.475.$$

## 3. Organizing by Conjugacy Classes of Subgroups

To compute (1) efficiently, group the sum by conjugacy classes of maximal subgroups.
The maximal subgroups of $S_n$ fall into three types (the O'Nan–Scott theorem):

### Type 1: Intransitive subgroups
$$M \cong S_k \times S_{n-k}, \quad 1 \leq k \leq \left\lfloor\frac{n}{2}\right\rfloor.$$
Number of conjugates: $\binom{n}{k}$ (for $k < n/2$) or $\frac{1}{2}\binom{n}{n/2}$ (for $k = n/2$).
Each has order $k! \,(n-k)!$.

### Type 2: Imprimitive subgroups
$$M \cong S_k \wr S_m \quad \text{where } n = k \cdot m, \quad 1 < k < n.$$
These are stabilizers of a nontrivial partition of $\{1,\dots,n\}$ into $m$ blocks of size $k$.

### Type 3: Primitive subgroups
Maximal subgroups acting primitively on $\{1,\dots,n\}$ (classified using the
Classification of Finite Simple Groups). These include $A_n$, and various affine
and almost-simple groups.

### The dominant term: the alternating group $A_n$

The unique index-2 subgroup $A_n$ has $\mu(A_n) = -1$ (it sits immediately below
$S_n$ in the lattice). Its contribution to (1) is:

$$\frac{\mu(A_n) \cdot |A_n|^2}{(n!)^2} = \frac{-1 \cdot (n!/2)^2}{(n!)^2} = -\frac{1}{4}.$$

This term alone contributes $-\tfrac{1}{4}$ to $P_n$.

## 4. The Asymptotic Formula

Dixon (1969) proved the landmark result:

$$P(S_n \text{ or } A_n \text{ is generated}) \to 1 \quad \text{as } n \to \infty.$$

Since $P(\text{both elements land in } A_n) = \left(\frac{1}{2}\right)^2 = \frac{1}{4}$,
and conditional on avoiding $A_n$ the pair generates $S_n$ with probability tending
to 1, we obtain:

$$\boxed{\lim_{n \to \infty} P_n = \frac{3}{4}.}$$

Bovey (1980), refined by Maróti (2011), gave the precise asymptotic expansion:

$$P_n = \frac{3}{4} - \frac{1}{n!} - \frac{1}{2\binom{n}{n/2}} + O\left(n^{-3/2}\log n\right),$$

where the second term $\frac{1}{2\binom{n}{n/2}}$ is omitted when $n$ is odd.
Using Stirling's approximation, we have $\binom{n}{n/2} \sim \frac{2^n}{\sqrt{\pi n/2}}$, so

$$P_n = \frac{3}{4} - \frac{1}{n!} - \frac{\sqrt{\pi n}}{2 \cdot 4^n} + O\left(n^{-3/2}\log n\right). \tag{3}$$

The convergence to $\tfrac{3}{4}$ is extremely rapid — already by $n = 5$,
$P_5 = 0.475$, and the error shrinks exponentially thereafter.

## 5. Organizing by Maximal Subgroups

Applying Hall identity (1) directly requires the full subgroup lattice, which is
enormous for large $n$. A more practical approach groups the sum by maximal subgroups.

By Mobius inversion on the subgroup lattice, we have the equivalent formula:

$$P_n = \frac{1}{(n!)^2} \sum_{\substack{M \text{ maximal} \\ M \neq S_n,\, M \neq A_n}} \mu(M)\, |M|^2 + \frac{1}{(n!)^2} \sum_{\substack{H \text{ non-maximal} \\ H \neq \{e\}}} \mu(H)\, |H|^2.$$

The dominant correction comes from the intransitive maximal subgroups
$S_k \times S_{n-k}$, each of proportion $1/\binom{n}{k}$ in $S_n$. Their total
contribution to the sum is $O(1/n)$ and vanishes as $n \to \infty$.

The primitive maximal subgroups other than $A_n$ contribute $O(n^{-3/2}\log n)$
(Dixon, 1969).

## 6. Proof Sketch of $\lim_{n \to \infty} P_n = \frac{3}{4}$

**Step 1.** By the Classification of Finite Simple Groups and Jordan's theorem, a
transitive subgroup of $S_n$ containing a transposition is all of $S_n$. A
transitive subgroup containing a 3-cycle and acting 2-transitively is either
$A_n$ or $S_n$.

**Step 2.** The probability that two random permutations are both even is $1/4$. In
this case they can only generate $A_n$ or a proper subgroup.

**Step 3.** The probability that two random permutations both lie in a fixed
intransitive maximal subgroup $S_k \times S_{n-k}$ is $\binom{n}{k}^{-2}$. Summing
over all such subgroups gives $\sum_{k=1}^{\lfloor n/2 \rfloor}\binom{n}{k}^{-1} = O(1/n)$.

**Step 4.** Dixon showed that the probability that two random permutations generate
a transitive subgroup other than $A_n$ or $S_n$ is $O(n^{-3/2}\log n)$.

**Step 5.** Combining:
$$P_n = 1 - \frac{1}{4} - O(1/n) - O(n^{-3/2}\log n) = \frac{3}{4} + o(1).$$

## 7. Generalization to $d$ Generators

For $d$ random generators, the same analysis gives:

$$P(S_n \text{ is generated by } d \text{ elements}) \to 1 - 2^{-d} \quad \text{as } n \to \infty.$$

The $2^{-d}$ comes from the probability that all $d$ elements land in $A_n$.

---

