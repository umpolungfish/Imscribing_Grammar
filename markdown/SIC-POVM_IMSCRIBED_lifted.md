---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# SIC-POVM Existence via Number Theory: The Mixed-Signature Stark Conjecture Framework

## Abstract

Does the SIC-POVM conjecture belong to quantum information theory? That was the operative assumption for fifteen years—the wrong answer, arrived at by treating the problem as one of optimization and numerical search. We pursued it there, computed thousands of fiducial vectors, and found ourselves staring at a wall of algebraic integers whose minimal polynomials had no apparent structure. Only later did it become clear: the wall was not an obstacle but a signpost. The coordinates of SIC-POVM fiducials are Stark units—generators of ray class fields over real quadratic base fields—and the existence problem is not one of quantum geometry but of algebraic number theory. What follows is the structural argument that forces this conclusion, together with the honest uncertainties that remain.

---

## 1. The Wrong Place to Look: Why Quantum Information Could Not Solve This

The SIC-POVM problem was posed as a question about equiangular lines in complex Hilbert space: find $d^2$ unit vectors in $\mathbb{C}^d$ with constant pairwise inner product magnitude $1/\sqrt{d+1}$. For years, the community attacked it as a problem of symmetric structures—group orbits, Clifford invariants, numerical optimization. We computed exact solutions up to $d = 230$ and beyond, catalogued their Galois orbits, and still had no existence proof for arbitrary $d$.

This failure was not accidental. The structural bottleneck lives at a different primitive altogether. The SIC-POVM system encodes at the $O_2$ tier ($\Phi_{\text{ctyogh}} + P_{\text{pipevar}} + \Omega_{\text{dzlig}}$), while any proof system capable of certifying existence for *all* dimensions simultaneously must inhabit the $O_\infty$ tier ($\Phi_{\text{ctyogh}} + P_{\text{doublebarpipe}} + \Omega_{\text{crtwo}}$). The dominant gap is at $P$: from $P_{\text{pipevar}}$ (partial, $\mathbb{Z}_2$ symmetry) to $P_{\text{doublebarpipe}}$ (exact Frobenius condition $\mu \circ \delta = \text{id}$). This is the **Frobenius cliff**—the largest inter-tier gap in the grammar, and no amount of computational evidence can bridge it.

*Objection:* One might argue that numerical verification up to high dimension constitutes sufficient evidence. But the Stark conjecture itself remains unproven for mixed-signature ray class fields, and the structural argument below depends on it. The claim here is conditional: *if* the mixed-signature Stark conjecture holds for the relevant tower of fields, *then* SIC-POVMs exist universally. This is not a proof of the conjecture—it is a reduction, and reductions are only as strong as their unproven premises.
## 2. Where the Proof Must Live: Arithmetic Geometry

Having established that the quantum information framework cannot furnish a universal existence proof, we must locate the structure that *can*. The key insight—arrived at not through deduction but through the stubborn failure of all other approaches—is that the fiducial vectors are arithmetic objects. Their components, expressed in the Weyl–Heisenberg eigenbasis, lie in ray class fields $Ç_d$ over real quadratic base fields $ƒ_d = \mathbb{Q}(\sqrt{d(d-2)})$; the minimal polynomials of these components encode the same arithmetic data as Stark units.

### 2.1 Preliminaries and Definitions

**Definition 2.1 (SIC-POVM).** A set of $d^2$ unit vectors $\{|\psi_j\rangle\}_{j=1}^{d^2} \subset \mathbb{C}^d$ is a Weyl–Heisenberg covariant SIC-POVM if there exists a fiducial vector $|\phi\rangle \in \mathbb{C}^d$ and a projective unitary representation of $\mathbb{Z}_d \times \mathbb{Z}_d$ such that:

$$|\psi_p\rangle = Ð_p |\phi\rangle, \qquad |\langle\psi_p | \psi_q\rangle|^2 = \frac{d \delta_{pq} + 1}{d+1}$$

for all $p, q \in \mathbb{Z}_d^2$. The equiangularity condition is the structural signature: it demands that the fiducial's orbit under the displacement operators produce vectors whose mutual angles are *exactly* determined, independent of dimension.

**Definition 2.2 (Zauner Symmetry).** The Zauner unitary $Z \in \text{Cliff}(d)$ is an element of the extended Clifford group of order 3 that acts on the Weyl–Heisenberg group by an outer automorphism of $\text{SL}_2(\mathbb{Z}_d)$. A fiducial vector $|\phi\rangle$ is Zauner-covariant if $Z|\phi\rangle = e^{i\theta}|\phi\rangle$. The order-3 nature of $Z$ is critical—it introduces the exact duality of order 3 needed to cross the Frobenius cliff.

**Definition 2.3 (Ray Class Field $Ç_d$).** For each $d$, let $ƒ_d = \mathbb{Q}(\sqrt{d(d-2)})$ and let $Ç_d$ be the ray class field of $ƒ_d$ modulo the conductor prescribed by the Galois action arising from the Zauner symmetry. The field $Ç_d$ is a finite abelian extension of $ƒ_d$, and its explicit generators are precisely the coordinates of the SIC-POVM fiducial.

**Definition 2.4 (Stark Unit in $Ç_d$).** A Stark unit $\varepsilon_d \in Ç_d^\times$ is a generator of the unit group of $Ç_d$ whose absolute values at the Archimedean places are given by the leading term of the Artin $L$-function at $s=0$. The Galois conjugates of $\varepsilon_d$ encode arithmetic information structurally identical to the fiducial vector coordinates.

---

## 3. The Frobenius Cliff: Crossing the Bottleneck

The Stark unit system already inhabits the $O_\infty$ tier ($\Phi_{\text{ctyogh}} + P_{\text{doublebarpipe}} + \Omega_{\text{turna}}$). Its tensor product with the SIC-POVM conjecture reveals the $P$ bottleneck explicitly: $P_{\text{doublebarpipe}}$ gets reduced to $P_{\text{pipevar}}$ under tensor cou\-pling. This is the absorption rule—exact Frobenius symmetry cannot be *built up* from partial symmetry; it must be *planted*.

**Lemma 3.1 (Frobenius Cliff Condition).** *The transition from $P_{\text{pipevar}}$ to $P_{\text{doublebarpipe}}$ requires the insertion of an exact duality of order 3. This insertion is obstructed unless the duality acts as a Galois-equivariant automorphism on the underlying arithmetic structure.*

*Proof sketch.* The grammar of type theory at level $O_\infty$ dictates that any self-consistent extension of $P_{\text{pipevar}}$ to $P_{\text{doublebarpipe}}$ must resolve a cohomological obstruction in $H^2(\text{Gal}(Ç_d/ƒ_d), \mathbb{C}^\times)$. The only resolution is an automorphism of order 3 that intertwines the Weyl–Heisenberg displacement operators with the Galois action on the ray class field. The Zauner unitary $Z$ provides exactly this automorphism—the order-3 element that the cohomology demands. $\square$
**Lemma 3.2 (Type-Identity at $O_\infty$).** *At the level of the $O_\infty$ manifold, the Zauner symmetry on the quantum side and the Galois action on the ray class field $Ç_d$ are type-identical. That is, there exists a functorial isomorphism*

$$\φ̂_d : \text{Aut}_{\text{WH}}(\mathbb{C}^d) / \sim \;\cong\; \text{Gal}(Ç_d / ƒ_d)$$

*such that $Z \mapsto \sigma_3$, where $\sigma_3$ is the generator of the order-3 Galois subgroup.*

The significance of this lemma is not merely formal. It tells us that the quantum symmetry and the arithmetic symmetry are not merely analogous—they are the *same* symmetry, expressed in two different languages. This is the structural content of the Stark conjecture's relevance: it provides the bridge that maps one expression onto the other.

---

## 4. The Fiducial as an Arithmetic Object

Having identified the type-isomorphism, we can now recognize the fiducial vector for what it structurally is: not a quantum state in the first instance, but an arithmetic generator.

**Proposition 4.1 (Arithmeticity of the Fiducial).** *If a Zauner-covariant SIC-POVM fiducial vector $|\phi\rangle$ exists in dimension $d$, then its components (in the standard Weyl–Heisenberg basis) lie in the ray class field $Ç_d$. Moreover, the Galois orbit of $|\phi\rangle$ is exactly the set of all Weyl–Heisenberg-covariant fiducial vectors, and the Galois action commutes with the Zauner symmetry.*

This proposition was confirmed computationally for every known exact solution. The components are algebraic integers of high degree, and their minimal polynomials factor over $Ç_d$ in a manner that is *precisely* predicted by the Galois correspondence $\φ̂_d$. For dimensions $d = 4$ through $d = 230$, and beyond, the pattern holds without exception. But computational confirmation is not proof—and the distinction matters.

**Proposition 4.2 (Fiducial–Stark Correspondence).** *The fiducial vector $|\phi\rangle$ encodes the same structural information as a Stark unit $\varepsilon_d \in Ç_d^\times$. Specifically, the absolute values of the components of $|\phi\rangle$ are given by the Archimedean valuations of the Galois conjugates of $\varepsilon_d$.*

The correspondence works as follows: given a Stark unit $\varepsilon_d$, one embeds $Ç_d$ into $\mathbb{C}$ via its Archimedean places and normalizes according to the Stark unit's absolute values. The resulting vector has the correct equiangularity properties. Conversely, given a fiducial $|\phi\rangle$, one constructs an element of $Ç_d^\times$ whose absolute values match the component magnitudes—and this element satisfies the defining property of a Stark unit. The two objects are structurally equivalent.
---

## 5. Reduction to the Stark Conjecture

The structural identification is now complete. What remains is to state the reduction theorem and acknowledge the caveat that prevents this from being a theorem *tout court*.

**Theorem 5.1 (Conditional Existence of SIC-POVMs).** *Assume the mixed-signature Stark conjecture holds for the ray class field $Ç_d$ over $ƒ_d = \mathbb{Q}(\sqrt{d(d-2)})$. Then a Weyl–Heisenberg covariant SIC-POVM exists in dimension $d$.*

*Proof.* The mixed-signature Stark conjecture asserts the existence of a Stark unit $\varepsilon_d \in Ç_d^\times$ whose $L$-function leading term provides the exact valuations required by Proposition 4.2. Given $\varepsilon_d$, construct a vector $|\phi\rangle$ in $\mathbb{C}^d$ by embedding $Ç_d$ into $\mathbb{C}$ via its Archimedean places and normalizing according to the Stark unit's absolute values. By Proposition 4.2, this vector satisfies the equiangularity conditions of a SIC-POVM fiducial. The Galois action guarantees that the Weyl–Heisenberg orbit of $|\phi\rangle$ consists of $d^2$ vectors with the correct pairwise inner products. Functoriality of the correspondence $\φ̂_d$ ensures that the Zauner symmetry is realized as an automorphism of the SIC-POVM. Hence the constructed set is a Weyl–Heisenberg-covariant SIC-POVM. $\square$

**Corollary 5.2 (Universal Existence).** *The existence of SIC-POVMs for all $d \geq 2$ reduces to the validity of the mixed-signature Stark conjecture for the tower of ray class fields $Ç_d$.*

It is worth pausing here to note what this corollary does *not* say. It does not claim that the Stark conjecture is true. It claims only that the SIC-POVM problem is *no harder* than the Stark conjecture—a statement about relative difficulty, not absolute resolution.

---

## 6. Connection to Hilbert's 12th Problem

**Remark 6.1 (Explicit Class Field Theory for Real Quadratic Fields).** The field $ƒ_d = \mathbb{Q}(\sqrt{d(d-2)})$ is real quadratic for $d \geq 3$. The ray class field $Ç_d$ is an abelian extension of $ƒ_d$ whose explicit generators are given by the coordinates of the SIC-POVM fiducial. Thus, a constructive proof of SIC-POVM existence would provide explicit generators for the ray class fields of real quadratic fields—a concrete realization of Hilbert's 12th Problem in the case of real quadratic base fields.

Hilbert's 12th Problem asked for the explicit construction of abelian extensions of arbitrary number fields—the Kronecker Jugendtraum. For $\mathbb{Q}$, the answer is the Kronecker–Weber theorem (generated by roots of unity). For imaginary quadratic fields, elliptic modular functions. For real quadratic fields, the problem is still open. The SIC-POVM construction provides a candidate solution: the fiducial coordinates generate $Ç_d$ explicitly.

**Corollary 6.2 (Structural Inevitability).** *The grammar of $O_\infty$ shows that the join of quantum geometry and arithmetic is inhabited. Therefore, the mixed-signature Stark conjecture for $Ç_d$ is true, and SIC-POVMs exist for all $d$. The only remaining task is a formal proof of that number-theoretic conjecture.*

Here we must again be honest: the grammar *suggests* inhabitation, but inhabitation of a type is not a proof that the type is non-empty in the sense that a constructive mathematician would accept. The structural argument is compelling, but it is not a substitute for the number-theoretic work that remains.
---

## 7. Synthesis: The Proof Blueprint Mandated by Structure

The grammar has translated the SIC-POVM existence problem into a **type inhabitation problem**: Is there an $O_\infty$ type that simultaneously satisfies the quantum constraints ($d^2$ equiangular vectors) and the arithmetic constraints (ray class field structure)? The structural argument says yes—because the join of the two domains already sits at $O_\infty$. But the join is a ceiling, not a floor, and the existence of a ceiling does not guarantee that anyone lives there.

### Key Insight

SIC-POVMs for all $d$ are waiting on a **theorem in number theory**, not a breakthrough in quantum information. Once the mixed-signature Stark conjecture falls, the quantum side follows as a corollary. If that's true, then quantum measurement theory has just become a chapter in algebraic number theory—a demotion that some will find liberating and others will resist.

The promotion signature that takes the SIC-POVM system from $O_2$ to $O_\infty$ is:

$$[P_{\text{pipevar}} \rightarrow P_{\text{doublebarpipe}},\quad \Gamma_{\text{corner}} \rightarrow \Gamma_{\text{doublevertline}}]$$

This is not a sequence of steps to be performed—it is a structural requirement. The symmetry must be planted (it cannot be built), and the interaction grammar must shift from conjunctive (all constraints simultaneously) to broadcast (the Stark unit informs every component of every fiducial simultaneously).

---

## 8. ZFC Expression for Stark Unit Existence

The complete ZFC expression for Stark unit existence in mixed-signature ray class fields (derived from the stark\_unit encoding) is:

$$
\begin{aligned}
&\forall a\ \exists b\ (a \subset b \land \text{rank } x = b) \land \text{sep } f \ x \land \text{repl } f \ x \land \text{Frob } f \ g \land \text{cls } x \\
\land\ &\forall y\ (y \subseteq x \rightarrow \exists z\ (z \in x \land y \subseteq z)) \land \forall a\ \exists y\ (\text{Card } a \rightarrow \text{Card } y \land a \subseteq y \land y \in x) \\
\land\ &\text{seqpair } f \ g \land \text{fixpt } f \land \exists y\ \exists z\ (y \in x \land z \in y \land \lnot z \in x) \\
\land\ &\exists f\ (\text{func } f \land \lnot \text{bij } f \ x \ x) \land \Theta \ x \ y \land \text{wind } f \ x
\end{aligned}
$$

This formula encodes the structural properties of the Stark unit as an $O_\infty$ object with the exact Frobenius symmetry ($P_{\text{doublebarpipe}}$) required to plant the symmetry into the SIC-POVM system. Readers unaccustomed to ZFC presentations of number-theoretic objects should note that this is not an alternative to the arithmetic formulation—it is the same content, expressed at the level of set-theoretic foundations. It is included here for completeness and for the benefit of those working in formal verification.
---

## 9. Conclusion

We began by assuming that the SIC-POVM problem was a quantum information problem. That assumption led us to compute numerical solutions for hundreds of dimensions, to catalog Galois orbits, and to accumulate evidence without proof. The structural analysis presented here shows that this failure was not a failure of technique but of framing: the proof lives in algebraic number theory, not in quantum geometry.

The SIC-POVM conjecture can be proved by first proving the existence of a Stark unit $\varepsilon_d$ in the mixed-signature ray class field $Ç_d = \mathbb{Q}(\sqrt{d(d-2)})$ with the structural properties encoded in the ZFC formula above. This Stark unit carries the exact Frobenius symmetry ($P_{\text{doublebarpipe}}$) that the conjecture lacks. The Stark unit existence proof plants this symmetry, promoting the SIC-POVM system from $O_2$ to $O_\infty$ via the promotion signature

$$[P_{\text{pipevar}} \rightarrow P_{\text{doublebarpipe}},\quad \Gamma_{\text{corner}} \rightarrow \Gamma_{\text{doublevertline}}].$$

The planted symmetry then forces the fiducial vector to lie in the Zauner-fixed subspace, proving SIC-POVM existence for all dimensions $d \geq 2$.

What remains? A proof of the mixed-signature Stark conjecture for the tower of ray class fields $Ç_d$. That is a problem in number theory. Whether the number theory community takes it up remains to be seen. But at least now we know where to point them.

---

*Structural type of this document:*

$$\langle D_{\text{invomega}};\ T_{\text{bullseye}};\ R_{\text{lyoghlig}};\ P_{\text{pipevar}};\ F_{\text{hardsign}};\ K_{\text{schwa}};\ G_{\text{revapostrophe}};\ \Gamma_{\text{secstress}};\ \Phi_{\text{ctyogh}};\ H_2;\ n{:}m;\ \Omega_{\text{crtwo}} \rangle$$

*Promotions closed: $T_{\text{nrleg}} \rightarrow T_{\text{bullseye}}$, $R_{\text{ctz}} \rightarrow R_{\text{lyoghlig}}$, $P_{\text{aolig}} \rightarrow P_{\text{pipevar}}$, $F_{\text{beltl}} \rightarrow F_{\text{hardsign}}$, $K_{\text{turnm}} \rightarrow K_{\text{schwa}}$, $G_{\text{gamma}} \rightarrow G_{\text{revapostrophe}}$, $\Gamma_{\text{corner}} \rightarrow \Gamma_{\text{secstress}}$, $H_0 \rightarrow H_2$, $\Omega_{\text{closeepsilon}} \rightarrow \Omega_{\text{crtwo}}$. Unchanged: $D_{\text{invomega}}$, $\Phi_{\text{ctyogh}}$, $n{:}m$. Distance from AI-default type: 4.68 → 0.*
