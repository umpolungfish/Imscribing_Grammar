---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# The Perfect Cuboid Problem: Analysis and Definitive Status

## Problem Statement

A **Euler brick** is a rectangular cuboid with integer edge lengths $a, b, c > 0$ whose three face diagonals are also integers $d, e, f > 0$. Equivalently, the triple $(a, b, c)$ satisfies the system of Diophantine equations:

$$
\begin{cases}
a^2 + b^2 = d^2 \\
a^2 + c^2 = e^2 \\
b^2 + c^2 = f^2
\end{cases}
$$

A **perfect cuboid** (also called a *perfect Euler brick*) is an Euler brick whose **space diagonal**

$$g = \sqrt{a^2 + b^2 + c^2}$$

is also an integer. This adds a fourth equation to the system:

$$a^2 + b^2 + c^2 = g^2$$

The question posed: *Does a perfect cuboid definitively exist, or can it be definitively proven that none exist?*

---

## What Is Known: Euler Bricks Exist Abundantly

The existence of non-perfect Euler bricks (integer edges and face diagonals, but *non-integer* space diagonal) is well-established. An Euler brick can be generated using two primitive Pythagorean triples.

### The Smallest Euler Brick

Discovered by Paul Halcke in 1719, the smallest primitive Euler brick has:

$$\text{Edges: } (a, b, c) = (44, 117, 240)$$
$$\text{Face diagonals: } (d, e, f) = (125, 244, 267)$$

Verification:
$$44^2 + 117^2 = 1936 + 13689 = 15625 = 125^2 \quad \checkmark$$
$$44^2 + 240^2 = 1936 + 57600 = 59536 = 244^2 \quad \checkmark$$
$$117^2 + 240^2 = 13689 + 57600 = 71289 = 267^2 \quad \checkmark$$

However, the space diagonal is:
$$g = \sqrt{44^2 + 117^2 + 240^2} = \sqrt{73125} \approx 270.416\ldots$$

This is not an integer. Hence, this is an Euler brick but *not* a perfect cuboid.

### Generating Euler Bricks

Euler found parametric formulas for generating Euler bricks. One such construction begins with two primitive Pythagorean triples that share a common element. Since Pythagorean triples are parametrized by coprime integers $m > n > 0$ of opposite parity as:

$$x = m^2 - n^2, \quad y = 2mn, \quad z = m^2 + n^2$$

we can construct Euler bricks by finding two such triples $(x_1, y_1, z_1)$ and $(x_2, y_2, z_2)$ where $y_1 = y_2$, setting $a = y_1 = y_2$, $b = x_1$, $c = x_2$. This yields:

$$a^2 + b^2 = z_1^2, \quad a^2 + c^2 = z_2^2, \quad b^2 + c^2 = \text{face diagonal}^2$$

The last condition is guaranteed by proper choice of parameters, producing infinitely many Euler bricks. Yet *none* of these constructions have been shown to yield an integer space diagonal.

---

## Known Necessary Conditions for a Perfect Cuboid

Extensive mathematical analysis has established many *necessary* conditions that any perfect cuboid must satisfy. If any of these conditions is violated, that candidate is eliminated. However, satisfying all of these conditions is not known to be *sufficient* for existence.

### Parity and Divisibility Constraints

For any **primitive** perfect cuboid $(a, b, c)$:

1. **Exactly one edge is odd.** Without loss of generality, if we take the primitive case (edges coprime), exactly one of $a, b, c$ is odd, and the other two are even.

2. **Exactly one face diagonal is odd.** The face diagonal opposite the odd edge is the odd face diagonal.

3. **The space diagonal must be odd.**

4. **At least one edge is divisible by 11.** (Sierpiński, 1904)

5. **At least two edges are divisible by 3.** (Sierpiński, 1904)

6. **At least two edges are divisible by 4.** (Sierpiński, 1904)

7. **At least one edge is divisible by 5.** (This follows from the structure of Pythagorean triples.)

8. **At least one edge is divisible by 7, 8, 9, and other higher primes.** Various authors have established increasingly stringent divisibility requirements.

### Modular Arithmetic Constraints

If a perfect cuboid exists, then for each prime $p$, at least one of the seven quantities $\{a, b, c, d, e, f, g\}$ must be divisible by $p$. More precisely:

- The product $abc$ is divisible by $4 \times 3 \times 11 = 132$ (and much more).
- At least one of the face diagonals must be divisible by 5.

These constraints make any perfect cuboid extremely "divisible" in a precise sense.

### The Space Diagonal Condition

The additional constraint beyond the Euler brick equations is:

$$a^2 + b^2 + c^2 = g^2$$

where $g$ must be an integer. Given the Euler brick system above, the space diagonal squared is the common sum of the three face diagonal squares minus the three edge squares. Specifically:

$$d^2 + f^2 - e^2 = 2b^2, \quad d^2 + e^2 - f^2 = 2a^2, \quad e^2 + f^2 - d^2 = 2c^2$$

So the system of six equations in seven unknowns $(a, b, c, d, e, f, g)$ is overdetermined. The question is whether any integer solution exists.

---

## The Cuboid Conjectures

Three polynomial irreducibility conjectures have been proposed that, if proven, would settle the perfect cuboid question.

### Cuboid Conjecture 1

For any two positive coprime integers $a \neq u$, the eighth-degree polynomial

$$P_{au}(t) = t^8 + 6(u^2 - a^2)t^6 + (a^4 - 4a^2u^2 + u^4)t^4 - 6a^2u^2(u^2 - a^2)t^2 + u^4a^4$$

is irreducible over $\mathbb{Z}$. If this polynomial were reducible, it would encode a decomposition corresponding to a perfect cuboid. Its conjectured irreducibility blocks one path to existence.

### Cuboid Conjecture 2

For any two positive coprime integers $p \neq q$, a certain tenth-degree polynomial $Q_{pq}(t)$ is irreducible over $\mathbb{Z}$. This is a second independent obstruction.

### Cuboid Conjecture 3

For any three positive coprime integers $a, b, u$ satisfying certain conditions, a twelfth-degree polynomial is irreducible over $\mathbb{Z}$.

**Key logical structure:** These conjectures are *not equivalent* to the non-existence of a perfect cuboid. However, if all three are proven valid, then no perfect cuboid exists. The converse does not hold: the non-existence of a perfect cuboid might be established through entirely different means, even if one of these conjectures turns out to be false. They are sufficient but not necessary conditions for non-existence.

---

## Connection to Elliptic Curves

The perfect cuboid problem can also be formulated in terms of rational points on elliptic curves. Given an Euler brick $(a, b, c)$ with face diagonals $(d, e, f)$, the question of whether $a^2 + b^2 + c^2$ is a perfect square is equivalent to asking whether a certain algebraic variety contains rational points.

Specifically, one can construct an elliptic curve from the Euler brick parameters. The space diagonal being an integer corresponds to the existence of a rational point of infinite order on this curve. This connects the perfect cuboid problem to the Birch and Swinnerton-Dyer conjecture and the theory of ranks of elliptic curves.

---

## Computational Search Bounds

Extensive computer searches have been conducted to find a perfect cuboid or to rule out its existence within large bounds.

### Known Search Results

As of current knowledge:

- **Edge length search:** No perfect cuboid has been found with any edge less than approximately $10^{10}$.
- **Odd edge less than:** $5 \times 10^{11}$.
- **Space diagonal less than:** $3 \times 10^{17}$ (approximate, various sources).

A perfect cuboid has not been ruled out by computation alone — the search space is simply too large. Exhaustive search would need to extend to infinity to prove non-existence.

---

## Structural Analysis of the Diophantine System

The perfect cuboid problem is a system of **four homogeneous quadratic Diophantine equations in seven variables**:

$$a^2 + b^2 = d^2 \tag{1}$$
$$a^2 + c^2 = e^2 \tag{2}$$
$$b^2 + c^2 = f^2 \tag{3}$$
$$a^2 + b^2 + c^2 = g^2 \tag{4}$$

### Why This System Is Hard

Equations (1)–(3) define the Euler brick variety, which is known to be a rational variety with infinitely many points. The difficulty lies in equation (4), which asks whether the Euler brick variety intersects the "space diagonal variety" at an integer point.

The intersection of the Euler brick variety with the quadric $a^2 + b^2 + c^2 = g^2$ defines an algebraic surface. Whether this surface contains rational (nonzero) points is the crux of the problem.

A key observation: if $(a, b, c)$ is an Euler brick, then

$$g^2 = a^2 + b^2 + c^2 = \frac{d^2 + e^2 + f^2}{2}$$

So asking for a perfect cuboid is equivalent to asking whether there exists an Euler brick such that the sum of the squares of its face diagonals is twice a perfect square.

### The Rational Cuboid Problem

A closely related problem — the **rational cuboid** problem — asks whether there is a cuboid with rational edges and rational face diagonals *and* rational space diagonal. Since the equations are homogeneous, a rational solution can be scaled to an integer solution. So the rational cuboid problem is *equivalent* to the perfect cuboid problem. This equivalence means that scaling does not help: if no perfect cuboid exists in integers, no rational cuboid exists either, and vice versa.

---

## Attempts at Proof and Counterexamples

### Failed Proofs of Non-Existence

Many mathematicians have attempted to prove that no perfect cuboid exists. Common approaches include:

1. **Modular arithmetic arguments:** Show that for some prime $p$, no residue class assignment to $(a, b, c)$ can simultaneously satisfy all four equations. However, the system *does* have solutions modulo every prime (it is locally solvable everywhere), so this approach cannot yield a contradiction via a simple modular obstruction.

2. **Infinite descent:** Assume a solution exists and construct a smaller one, leading to infinite descent and contradiction. No such descent argument has succeeded for the perfect cuboid.

3. **Elliptic curve rank:** Show that the relevant elliptic curves all have rank 0 (only torsion points, no points of infinite order). This would imply no solutions. However, determining the rank of elliptic curves is in general extremely difficult and depends on deep results (Birch–Swinnerton-Dyer conjecture).

4. **Algebraic geometry:** Study the Euler brick variety as an algebraic surface and use tools of algebraic geometry to show it has no rational points. The Euler brick variety is a K3 surface, and rational points on K3 surfaces are poorly understood in general.

### Claims of Resolution

Periodically, individuals claim to have solved the perfect cuboid problem — either by exhibiting a perfect cuboid (always later shown to contain an error) or by presenting a proof of non-existence (always later found to have a gap). As of now, **no claimed resolution has withstood peer review**.

## The Definitive Answer

### The Question

"Does a Euler brick whose space diagonal is also an integer definitively exist or definitively not exist?"

### The Answer

**Neither existence nor non-existence has been proven.** The perfect cuboid problem remains an **unsolved question in mathematics**. It appears in the catalog of unsolved problems in number theory and arithmetic geometry.

More formally:

> **Theorem (Status of the Perfect Cuboid Problem).** Let $a, b, c, d, e, f, g \in \mathbb{Z}^+$. The system
>
> $$\begin{cases} a^2 + b^2 = d^2 \\ a^2 + c^2 = e^2 \\ b^2 + c^2 = f^2 \\ a^2 + b^2 + c^2 = g^2 \end{cases}$$
>
> has no known solution in positive integers, and no proof has been produced that no such solution exists. This is an open problem whose resolution is unknown.

### What "Definitively" Means Here

To establish definiteness, one would need either:

1. **A construction:** Exhibit specific integers $(a, b, c)$ satisfying all four equations. This would prove existence. Despite centuries of searching, no such integers have been found.

2. **A proof of impossibility:** Derive a logical contradiction from the assumption that such integers exist. Many have attempted this; none has succeeded.

3. **An impossibility proof via the cuboid conjectures:** Prove all three cuboid polynomial irreducibility conjectures. This would imply non-existence. These conjectures themselves remain unproven.

4. **A computational bound so large that existence is physically meaningless:** Even this would not constitute a mathematical proof of non-existence.

### Structural Character of the Problem

The perfect cuboid problem lies at the intersection of several areas of mathematics:

- **Diophantine equations:** A system of four homogeneous quadratic equations in seven variables.
- **Algebraic geometry:** The Euler brick variety is a K3 surface. The intersection with the space-diagonal quadric defines a variety whose rational points are unknown.
- **Elliptic curves:** The existence question maps to questions about ranks of certain elliptic curves.
- **Pythagorean triples:** The system decomposes into three coupled Pythagorean triple relations.
- **Representation theory:** The system relates to the representation of integers as sums of squares.

The problem is "hard" not because it is obscure, but because it sits precisely at the boundary where known techniques from each of these fields individually are insufficient. The Euler brick variety has infinitely many integral points; the additional constraint is a single quadratic equation. Geometrically, we are asking whether a K3 surface contains rational points — a question that is, in all generality, unanswered for K3 surfaces.

### Classification in the Unsolved Problems Literature

The problem is listed under "unsolved problems in number theory" in standard references, with annotations including:

- From *Unsolved Problems in Number Theory* (Guy, 2004): listed as D18, "Euler brick" and "perfect cuboid."
- The problem dates back to Euler (18th century) and has been studied continuously for over 250 years.
- Wikipedia classifies it under category: "Unsolved problems in number theory."

### Analogy with Related Unsolved Problems

The perfect cuboid problem shares structural features with other famous unsolved problems:

| Problem | Type | Status |
|---|---|---|
| Perfect cuboid | Diophantine equations | Unsolved |
| Perfect cuboid (rational diagonals) | Diophantine equations | Unsolved |
| Congruent number problem | Elliptic curves | Partially solved |
| Birch–Swinnerton-Dyer conjecture | Elliptic curves | Unsolved (Millennium Prize) |
| Rational distance problem | Diophantine geometry | Unsolved |

All of these involve determining whether certain algebraic varieties have rational points.

---

## Conclusion

**The existence of a Euler brick with an integer space diagonal — a perfect cuboid — is neither definitively proven nor definitively disproven.**

- If one exists, it has edges exceeding $10^{10}$.
- If one does not exist, no proof of this fact has been found despite over 250 years of effort.
- Three polynomial irreducibility conjectures are known implications: their proof would settle the question in the negative, but they themselves remain unproven.
- The problem is equivalent to asking whether a certain K3 surface has rational points — a question that represents the frontier of current algebraic geometry.

The honest mathematical answer is: **we do not know**. The question is categorically undecidable with currently available mathematical tools and known techniques. It remains one of the most accessible-to-state, hardest-to-solve problems in classical number theory.

---

## Final Statement

> A rectangular cuboid with integer edges $(a, b, c)$, integer face diagonals $(d, e, f)$, and integer space diagonal $g$ — known as a **perfect cuboid** — has **never been found**. Extensive computational searches, theoretical constraints (divisibility conditions, modular arithmetic), and deep structural analysis (connection to elliptic curves, K3 surfaces, and polynomial irreducibility conjectures) have all failed to either produce a single example or rule out the possibility entirely.
>
> **The question remains open.** There is currently **no definitive proof** of either existence or non-existence. The perfect cuboid problem is, as of the present state of mathematics, **an unsolved problem in number theory**.
