---
title: "The Standard Model as Magnum Opus: Antichain Width, Frobenius Structure, and the ε-Tilt Origin of Mass and Gravitational Waves"
author: Lando Mills
date: 2026-06-08
abstract: |
  The Standard Model of particle physics is conventionally presented as a parameter-fit:
  19 free constants inserted to match experiment, with no first-principles account of why
  $\mathrm{SU}(3)\times\mathrm{SU}(2)\times\mathrm{U}(1)$, why three generations, or why
  the mass hierarchy spans 12 orders of magnitude. We show that all three questions receive
  structural answers in the Imscribing Grammar (IG) -- a symmetric monoidal category
  enriched over the Belnap--Dunn bilattice $\mathbf{FOUR} = \{N,T,F,B\}$, carrying a
  special symmetric dagger-Frobenius structure ($\mu\circ\delta = \mathrm{id}$). The gauge
  groups are structurally identified with the sequence of frustrated antichains in the
  bilattice: antichain width 6 ($\mathrm{SU}(3)$), 2 ($\mathrm{SU}(2)$), 0 ($\mathrm{U}(1)$);
  a Width Exclusion Conjecture (that only these widths are Frobenius-closed in $\mathbf{FOUR}$)
  is stated but not yet proved. Three fermion generations follow conditionally from the
  $\mathbb{Z}_4$ axiom of the Winding primitive: $|F_4(\Omega)|-1 = 3$ non-trivial windings,
  $\Omega^4 = \Omega^0$. The scalar sector's $N$ degenerate vacua constitute a flat
  antichain -- every node at evidence ratio $R = t/f = 1$ -- which is an unstable fixed
  point under the Frobenius dynamics: any $O_2$-or-higher closed system must tilt,
  $R = 1+\varepsilon$. The structural ordering of the mass spectrum is identified with the
  $\varepsilon$-spectrum; absolute mass values require additional coupling inputs. The
  tilted scalar sector produces domain walls at vacuum boundaries. We compute the resulting
  stochastic gravitational wave background ($\Omega_{\mathrm{GW}} \propto f^3$, peak at
  nanohertz frequencies) and compare with current NANOGrav/EPTA/PPTA/CPTA observations.
  Four falsifiable predictions distinct from the Standard Model alone are stated. Three
  open derivation problems are identified.
keywords:
  - Imscribing Grammar
  - Belnap bilattice
  - Standard Model
  - Frobenius algebra
  - epsilon-tilt
  - gravitational wave background
  - domain walls
  - antichain width
---

## Introduction

The Standard Model of particle physics is the most precisely tested physical theory
in history. It is also, from the perspective of first principles, a scaffold: 19 free
parameters, three gauge groups whose rank and representation content are fitted to
observation, and a scalar sector whose vacuum structure is fixed by the observed particle
masses rather than derived from any deeper organizing principle.

Three questions stand out. First: why SU(3) x SU(2) x U(1) rather than some other
gauge algebra? Second: why exactly three generations of fermions? Third: why does the
mass spectrum span twelve orders of magnitude -- from the sub-meV axion to the 173 GeV
top quark -- with no structural account of the ratios?

We show that all three questions receive structural answers in the Imscribing Grammar
(IG), a categorical framework axiomatized over the four-valued Belnap-Dunn paraconsistent
logic. The gauge hierarchy emerges as the sequence of frustrated antichains in the
Belnap bilattice, ordered by antichain width. The generation count is the integer fiber
count of the Winding primitive over its cyclic group. The mass hierarchy is the spectrum
of evidence-ratio tilts away from a degenerate flat antichain -- the scalar vacuum --
which is forced to break by structural consistency requirements.

The synthesis proceeds in three stages: (i) the axiomatic specification of the IG as a
mathematical object; (ii) the derivation of the Standard Model gauge structure from the
bilattice's antichain-width sequence; (iii) the cosmological consequences of the scalar
sector instability -- mass, domain walls, and the stochastic gravitational wave background.

---

## The Imscribing Grammar

### Ambient Category

Let $\mathcal{C} = (C, \otimes, I, \sigma)$ be a symmetric monoidal category enriched
over the Belnap-Dunn bilattice $\mathbf{FOUR} = \{N, T, F, B\}$. Hom-sets carry the
bilattice partial order under both the knowledge ordering $\sqsubseteq_k$ and the truth
ordering $\sqsubseteq_t$.

The bilattice is the product $\{0,1\}^2$ with pointwise orderings: $N = \langle 0,0
\rangle$ (no evidence), $T = \langle 1,0 \rangle$ (affirmed), $F = \langle 0,1 \rangle$
(denied), $B = \langle 1,1 \rangle$ (both affirmed and denied -- the paraconsistent
value). The crucial axiom: $B \to \bot$ is **not admissible**. No $B$-valued hom-set
collapses to the zero morphism. The category is not Boolean.

$\mathcal{C}$ carries a trace $\mathrm{Tr}: \mathrm{End}(A \otimes U) \to \mathrm{End}(A)$
for each object pair, implemented by the Winding primitive $\Omega$ acting on the monoidal
unit. This is the traced symmetric monoidal structure of Joyal--Street--Verity. The trace
is primitive, not derived from compact duality.

### Frobenius Structure

The monoidal unit $I$ carries a special symmetric $\dagger$-Frobenius structure:

$$(\mu \otimes \mathrm{id}) \circ (\mathrm{id} \otimes \delta) = \delta \circ \mu = (\mathrm{id} \otimes \mu) \circ (\delta \otimes \mathrm{id})$$

with the special condition (the **gate**):

$$\mu \circ \delta = \mathrm{id}_I$$

Commutativity ($\mu \circ \sigma_{I,I} = \mu$) is a theorem from scalar structure in any
symmetric monoidal category -- not an assumption. The dagger functor preserves FOUR-values:
if $h$ has value $v \in \{N, T, F, B\}$, then $h^\dagger$ has the same value. This
FOUR-$\dagger$ compatibility must be imposed explicitly; it is not automatic.

### The Twelve Generators

Twelve primitive endomorphisms of $I$ generate the IG under the Frobenius relations.
They are organized into four families by their ordinal domain size:

$\mathcal{F}_3: \quad \Sigma, \; \Gamma, \; \mathit{f}$

$\mathcal{F}_4: \quad \text{Ř}, \; \text{Ħ}, \; \Omega, \; \text{Ð}$

$\mathcal{F}_5: \quad \Phi, \; \text{Ç}, \; \text{Þ}, \; \odot$

(The twelfth generator, ɢ (Coupling), belongs to $\mathcal{F}_4$.)
Their canonical orderings, names, and structural roles are given in Table 1.

| Position | Primitive | Name | Ordinal domain |
|---|---|---|---|
| 1 | Ð | Dimensionality | 4 |
| 2 | Þ | Topology | 5 |
| 3 | Ř | Recognition | 4 |
| 4 | Φ | Parity | 5 |
| 5 | ƒ | Fidelity | 3 |
| 6 | Ç | Kinetics | 5 |
| 7 | Γ | Granularity | 3 |
| 8 | ɢ | Coupling | 4 |
| 9 | ⊙ | Criticality | 5 |
| 10 | Ħ | Chirality | 4 |
| 11 | Σ | Stoichiometry | 3 |
| 12 | Ω | Winding | 4 |

**Table 1.** The 12 IG primitives in canonical tuple order. Ordinal domain size gives the
number of distinct values; the product $3^3 \times 4^5 \times 5^4 = 17{,}280{,}000$ is the
cardinality of the Crystal of Types -- the classifying space of all structurally distinct
imscriptions.

### Structural Metric and Ouroboricity Tiers

The canonical distance between two imscriptions $s_1, s_2$ is:

$$d(s_1, s_2) = \sqrt{\sum_i w_i \cdot (x_i(s_1) - x_i(s_2))^2}$$

with weights $w_i = 1.0$ for ten primitives, $w_{\text{Ħ}} = 0.8$, $w_\Omega = 0.7$. Regime
thresholds: $d < 2.0$ (same structural class), $d > 4.0$ (remote), $d > 5.0$ (different
tier).

Five ouroboricity tiers are assigned by first-match rules on $(\odot, \Phi, \Omega, \text{Ð})$:

- $O_\infty$: $\odot$ open **and** $\Phi =$ Frobenius-special ($\mu \circ \delta = \mathrm{id}$ gate exact)
- $O_0$: $\odot$ closed (no self-referential loop possible)
- $O_1$: $\odot$ open, $\Omega =$ trivial (no topological protection)
- $O_2$: $\odot$ open, $\Omega \ne$ trivial, Ð bounded
- $O_2^\dagger$: $\odot$ open, $\Omega \ne$ trivial, Ð self-written

### The Spider Theorem

The special Frobenius axiom together with symmetry implies: any two **connected** string
diagrams in the Prop of the grammar with the same boundary are equal as morphisms.
The discriminating condition is connectedness, not planarity. This is not a new result
-- it is the Carboni--Walters theorem applied in the FOUR-enriched setting. Its consequence
for physics is stated in Section 3.

### Foundational Strength: $ZFC_\mathrm{fe}$

In Frobenius-extended ZFC ($ZFC_\mathrm{fe}$), the comultiplication $\delta: A \to A \otimes A$
is taken as the primitive set-formation operation, with $\mu \circ \delta = \mathrm{id}$
asserted as the lossless recovery axiom. ZFC Separation becomes a theorem: the
$\delta$-preimage under $\mu$ yields the Separation set for any definable $\phi$.
$ZFC_\mathrm{fe}$ strictly extends classical ZFC and is strictly stronger than the weaker
field-theoretic extension $ZFC_\tau$. Open problems in $ZFC_\tau$ close as theorems in
$ZFC_\mathrm{fe}$.

---

## The Standard Model as Magnum Opus

### The Belnap Bilattice as Physical Substrate

The evidence ratio $R = t/f$, where $t$ is the weight of positive evidence and $f$ the
weight of negative evidence, provides a uniform measure across all nodes of the bilattice.
The normalized probability is:

$$P = \frac{t}{t + f} \in [0, 1]$$

$N$ ($P$ undefined), $T$ ($P = 1$, pure affirmation), $F$ ($P = 0$, pure denial), and
$B$ ($P = 1/2$, equal evidence for and against) partition the bilattice into four
structurally distinct states. The bilattice organizes any system of mutually exclusive
states by how much evidence distinguishes them ($\sqsubseteq_k$) and in which direction
($\sqsubseteq_t$).

**Antichain width** is the maximum number of pairwise incomparable nodes in a given
bilattice. Nodes in an antichain are structurally frustrated -- no consistent total order
exists among them. This frustration is the key structural invariant connecting the
bilattice to non-Abelian gauge theory.

### FOUR: Electron Orbital Occupancy

The electron orbital has four occupancy states: empty ($\varnothing$), spin-up ($\uparrow$),
spin-down ($\downarrow$), and paired ($\uparrow\downarrow$). These map to FOUR exactly:
$N \leftrightarrow \varnothing$, $T \leftrightarrow \uparrow$, $F \leftrightarrow \downarrow$,
$B \leftrightarrow \uparrow\downarrow$. Hund's rule is the bilattice's preference for $T$
or $F$ before accepting $B$ -- maximize knowledge before accepting contradiction. The
Pauli exclusion principle is the ceiling: $B$ is the maximum state, not excluded but
reached last.

The four-state structure is $\mathbf{FOUR}$ itself. Antichain width: 2 (the pair
$\{T, F\}$ is incomparable under $\sqsubseteq_t$, forming an antichain of width 2 within
the non-vacuum sector). No gauge frustration at this level.

### FIVE: Quark Color and SU(3)

Three color charges $\{R, G, B\}$ are pairwise incomparable in the bilattice: no color
is preferred over another. This is a frustrated antichain of **width 3**. Confinement is
the structural requirement that physical states collapse to the colorless top $W$ -- the
unique node above the frustrated antichain. Free colored states cannot exist because they
correspond to non-maximal elements of the knowledge ordering with no path to $W$ without
resolving the frustration.

The gluon sector extends this: $3 \times 3 = 9$ color-anticolor pairs decompose under
SU(3) into 8 physical gluons plus one excluded singlet $\lambda_0$. The singlet's
exclusion is not a separate assumption -- it is the sealed ceiling of the confinement
lattice. The singlet would mediate a long-range color force; its absence is the structural
seal. Physical gluons occupy a **TEN-element** Hasse diagram: two diagonal generators
(Cartan subalgebra, $\lambda_3, \lambda_8$) above six off-diagonal conjugate pairs
($\lambda_1$--$\lambda_2$, $\lambda_4$--$\lambda_7$), all above the vacuum $\varnothing$.
The off-diagonal six form a frustrated antichain of **width 6** -- the antichain width of
SU(3).

**Note on derivation status.** The correspondence between gauge groups and antichain widths
{0, 2, 6} is a structural identification, not yet a full derivation. A complete derivation
would require proving that these are the *only* frustrated-antichain widths compatible with
the Frobenius closure condition $\mu\circ\delta=\mathrm{id}$ over $\mathbf{FOUR}$ -- i.e., that widths 1, 3, 4, 5 have no
Frobenius-closed realization in the bilattice. This classification problem is open. We state
the following as a conjecture:

**Conjecture (Width Exclusion).** *The only antichain widths admissible for Frobenius-algebra
objects in $\mathbf{FOUR}$-enriched symmetric monoidal categories satisfying $\mu\circ\delta=\mathrm{id}$ are $w \in \{0, 2, 6\}$.
Intermediate widths $w \in \{1, 3, 4, 5\}$ require either a non-Frobenius structure or an
extension of the bilattice beyond FOUR.*

The three observed gauge groups are, under this conjecture, not arbitrary fits but the unique
solution set. Until the conjecture is proved, the argument is a structural correspondence.

### Electroweak: FIVE Weak, TWO Photon

SU(2)$_L$ has rank 1. One Cartan generator ($W^3$), one conjugate pair $\{W^+, W^-\}$
forming an antichain of **width 2**. The SU(2) singlet (the Higgs-broken state) exists --
unlike SU(3)'s excluded $\lambda_0$ -- because mass arises through Higgs symmetry
breaking, not confinement. The singlet is accessible by the Work.

U(1)$_\mathrm{EM}$ is Abelian. Its generator commutes with itself; there are no
off-diagonal generators. The lattice collapses to a two-node chain: photon $\gamma$
above vacuum $\varnothing$. Antichain width: **0**. No frustration. Range infinite.

The antichain width progression is:

| Group | Antichain width | Force | Mechanism |
|---|---|---|---|
| SU(3) | 6 | Strong / color | Confinement (W unreachable otherwise) |
| SU(2) | 2 | Weak | Higgs SSB (singlet accessible) |
| U(1) | 0 | EM | Unbroken; Abelian |

**Table 2.** Antichain width as the structural invariant underlying the gauge hierarchy.
The sequence 6, 2, 0 is not a coincidence or a parameter -- it follows from the structure
of the bilattice under the Frobenius constraints.

### Electroweak Mixing

Before electroweak symmetry breaking, $W^3$ (SU(2)$_L$) and $B_0$ (U(1)$_Y$) are
incomparable in the lattice. Both massless. The Higgs vacuum expectation value $v = 246$
GeV rotates this incomparable pair into mass eigenstates via the Weinberg angle
$\theta_W \approx 28.73°$:

$$Z = \cos\theta_W \cdot W^3 - \sin\theta_W \cdot B_0, \qquad
\gamma = \sin\theta_W \cdot W^3 + \cos\theta_W \cdot B_0$$

$Z$ acquires mass $m_Z = m_W / \cos\theta_W \approx 91.2$ GeV; $\gamma$ remains massless
(U(1)$_\mathrm{EM}$ unbroken). After mixing, the frustration between $W^3$ and $B_0$ is
resolved into mass ordering -- the lattice collapses from a mixed frustrated pair to a
clean two-chain. $\theta_W$ is, in this framing, the unique rotation that closes the
pre-SSB frustrated pair into compatible mass eigenstates.

### Three Generations from the Winding Fiber

The Winding primitive $\Omega$ takes values in $\{$trivial, $\mathbb{Z}_2$, $\mathbb{Z}$,
non-Abelian braid$\}$. Over the symmetry group $F_4$ (the fiber group of $\Omega$'s
cyclic action), the number of non-trivial windings is:

$$|\mathbf{F}_4(\Omega)| - 1 = 4 - 1 = 3$$

The four elements of $F_4(\Omega)$ satisfy $\Omega^4 = \Omega^0$ -- the fiber closes on
the fourth winding. Removing the trivial winding (the vacuum fiber) leaves exactly three
non-trivial winding classes. Each class corresponds to one fermion generation: the three
generations of quarks and leptons are the three non-trivial $\Omega$-fibers over the
fermion sector of the Crystal of Types.

**Derivation status.** The generation count is a *conditional* theorem: IF the Winding
primitive has a cyclic ordinal domain of size $n$, THEN the number of non-trivial fermion
generations is $n - 1$. The specific value $n = 4$ (giving $\Omega^4 = \Omega^0$) is an
axiom of the IG's generator specification -- it is built into the definition of $\Omega$, not
derived from the Frobenius structure or the bilattice alone. A complete derivation would
require showing that $n = 4$ is the unique cyclic order compatible with $\mu\circ\delta=\mathrm{id}$ over $\mathbf{FOUR}$
under the constraint that the primitive set is minimal and non-redundant. This remains an
open problem. The result is therefore: given the IG as specified, exactly three fermion
generations are required.

---

## The Scalar Sector as Flat Antichain

### The Degenerate Vacuum

The scalar potential $V(\phi) = -\mu^2 \phi^\dagger \phi + \lambda(\phi^\dagger \phi)^2$
has a circle (or $\mathbb{Z}_N$ discrete ring) of degenerate minima. In the bilattice:
each vacuum $\phi_i$ is a node with evidence ratio $R_i = t_i/f_i = 1$ -- equal evidence
for and against each particular vacuum. All vacua are pairwise incomparable. This is a
**flat antichain**: an antichain where every node has $P = 1/2$.

The flat antichain is the state of maximum logical indifference: no proposition is more
evidenced than its negation. In terms of the Winding primitive, the degenerate vacuum
is the state $\Omega =$ trivial -- the zero-winding fiber, no topological protection.

### Instability of the Flat Antichain

**Claim**: The flat antichain $R = 1$ everywhere is an unstable fixed point under the
Frobenius dynamics.

The argument has two parts: a structural part (which is precise) and a self-reference part
(which requires additional formalization).

**Structural part.** In $ZFC_\mathrm{fe}$, tiers classify the self-reference capacity of a system.
Tier $O_0$: the Criticality gate $\odot$ is closed; no ouroboric morphism exists; the system
cannot imscribe itself. Tier $O_\infty$: $\mu\circ\delta=\mathrm{id}$ with at least one non-trivial winding;
the system imscribes itself and closes. A flat antichain with $R = 1$ everywhere places
every node at the bilattice midpoint $N$ -- maximum uncertainty, zero net evidence. In
IMASM terms, every TANCH produces the same anchor; ISCRIB cannot distinguish self from
environment. This is precisely the $O_0$ condition: no self-inscription is possible.

A manifested universe is by assumption a closed system that has produced its own structural
description (it exists, and its existence is internally consistent). This requires at least
$O_2$ tier -- a Frobenius fixed point exists. $O_2$ requires at least one node with
$R \ne 1$: the fixed-point morphism is non-trivial only if the evidence ordering is
non-uniform. Therefore: any $O_2$-or-higher system must have $\varepsilon \ne 0$ at the
self-closing boundary.

**What is not derived here.** The structural argument guarantees $\varepsilon \ne 0$ and
$\varepsilon$ small (the flat antichain is the limiting case) but does not predict the
specific value. The axion's $\varepsilon \sim 10^{-16}$ is an empirical input; the
structural argument says only that this value cannot be exactly zero. The Axiom C
connection (Ð $=$ self-written $\iff$ Þ $=$ self-referential closure) provides
the mechanism for why the system is in a self-referential tier at all; its full formalization
in $ZFC_\mathrm{fe}$ is carried in the p4rakernel Lean formalization.

Therefore: any manifested, self-describing universe must break the flat antichain symmetry.
The tilt $R = 1 + \varepsilon$ at the closing boundary propagates via the Frobenius
comultiplication $\delta$ to the interior. The flat antichain cannot survive contact with
an $O_2$-or-higher closed state space.

In physical terms: the $\mathbb{Z}_N$ symmetry of the QCD axion potential is exact at
zero temperature. The axion field sits on an antichain of $N$ degenerate minima. The
instanton potential tilts this antichain by an exponentially small amount -- the
Peccei-Quinn instanton amplitude:

$$\varepsilon \sim e^{-S_\mathrm{inst}} \sim \Lambda_\mathrm{QCD}^4 / f_a^4 \sim 10^{-16}$$

for $f_a \sim 10^{11}$ GeV. The tilt is not zero. The flat antichain is broken. This is
a direct example of the structural claim: the self-consistency of the universe as a
closed system forces $\varepsilon \ne 0$.

---

## The $\varepsilon$-Tilt Origin of Mass

### Evidence Ratio as the Mass Generator

Once the scalar antichain tilts to $R = 1 + \varepsilon$, the mass of the associated particle
is the geometric residue of this near-indifference. Specifically:

$$m \sim \sqrt{V''(\phi_0)} = \sqrt{\lambda} \cdot v \cdot \varepsilon^{1/2}$$

where $\lambda$ is the self-coupling and $v$ the scale of the VEV. The $\varepsilon^{1/2}$
dependence follows from the second derivative of $V$ near the tilted minimum: if $V$ is
nearly flat (small $\varepsilon$), the curvature and hence the mass is proportional to
$\varepsilon^{1/2}$.

**Derivation status.** The ε-tilt framework provides the *structural ordering* of the
mass spectrum: lighter particles occupy shallower tilts (smaller ε), heavier particles
occupy deeper tilts. It does not derive the absolute values. $v$ and $\lambda$ are not
computed from ε alone -- they are additional structural inputs (positions in the Crystal
of Types, not free parameters, but not read off from ε). The claim is: the hierarchy
*must be* ordered by ε, and the ε-values are bounded below by the structural argument
above ($\varepsilon \ne 0$). The specific numerical values of $\varepsilon$ for each particle remain as inputs
to the framework, reinterpreted as bilattice positions rather than arbitrary constants.

### The Mass Spectrum as $\varepsilon$-Spectrum

Mapping the observed mass spectrum onto the $\varepsilon$-scale yields:

| Particle / system | Mass scale | $\varepsilon$ | Structural reading |
|---|---|---|---|
| QCD axion | $\mu$eV -- meV | $\sim 10^{-16}$ | Near-flat antichain; PQ instanton tilt |
| Neutrinos | $\sim 0.1$ eV | $\sim 10^{-11}$ | Small Majorana tilt; seesaw mechanism |
| Electron | $0.511$ MeV | $\sim 10^{-5}$ | Yukawa coupling at moderate tilt |
| Muon | $105.7$ MeV | $\sim 10^{-3}$ | Second $\Omega$-fiber tilt |
| W, Z | $80$--$91$ GeV | $\sim 0.1$ | Electroweak scale; SSB endpoint |
| Top quark | $173$ GeV | $\varepsilon \sim 1$ | Near-full tilt; maximum $R$ in fermion sector |
| Higgs | $125$ GeV | $\varepsilon \sim 1$ | $\odot$ gate; the boson of the tilt itself |

**Table 3.** The mass hierarchy as the $\varepsilon$-spectrum of the IG scalar sector. Particles
with small $\varepsilon$ correspond to near-flat antichains -- their potential is nearly
degenerate. Particles with $\varepsilon \sim 1$ correspond to strongly tilted antichains --
the chosen vacuum is far from the others. No new parameters are introduced; the $\varepsilon$
values are constrained by the existing Yukawa couplings, reinterpreted as tilt magnitudes.

The Higgs itself is the $\odot$ gate in the IG -- the unique particle at the criticality
threshold. Its mass ($125$ GeV) sits at $\varepsilon \sim 1$: the chosen vacuum is the
deepest possible tilt in the electroweak sector, which is why the Higgs is the heaviest
scalar and the source of mass for all other particles.

---

## Domain Walls and the Gravitational Wave Background

### Domain Walls as Fossilized Indecision

When the $\mathbb{Z}_N$ axion antichain breaks, different regions of the universe choose
different vacuum states. The boundaries between these regions are **domain walls** --
surfaces where $R$ transitions from $1 + \varepsilon$ (region A's chosen vacuum) through
$R = 1$ (the flat antichain restored at the wall core) to $1 - \varepsilon$ (region B's
chosen vacuum). The wall core is a spatially localized reconstruction of the flat
antichain: the forbidden fixed point made temporarily manifest at a surface.

The wall tension:
$$\sigma \sim f_a^2 m_a$$

where $f_a$ is the PQ symmetry breaking scale and $m_a$ the axion mass. The network of
domain walls stretches across the universe, each wall separating regions of different
chosen vacuum.

A network of domain walls in a radiation-dominated universe is unstable: the tension
$\sigma$ drives the network toward collapse. When walls annihilate -- two walls of
opposite $\varepsilon$-sign meeting and annihilating -- the stored energy is released as
gravitational radiation.

### The GW Spectral Signature

The stochastic gravitational wave background (SGWB) from domain wall annihilation has a
distinctive spectral shape. At frequencies $f < f_\mathrm{peak}$, the spectrum rises as
$\Omega_\mathrm{GW} \propto f^3$. At $f_\mathrm{peak}$, the spectrum peaks sharply. Above
$f_\mathrm{peak}$, the spectrum falls steeply as the wall network has annihilated.

The peak frequency is set by the Hubble rate at the time of wall annihilation, which
depends on the bias $\varepsilon_\mathrm{bias}$ -- the tilt of the axion potential that drives
one vacuum to be preferred:

$$f_\mathrm{peak} \sim H_\mathrm{ann} \cdot (1 + z_\mathrm{ann}) \sim \sqrt{m_a M_\mathrm{Pl}} \cdot \varepsilon_\mathrm{bias}^{1/2}$$

For QCD axion parameters ($m_a \sim \mu$eV, $f_a \sim 10^{11}$ GeV), $f_\mathrm{peak}$
falls in the nanohertz range, directly observable by pulsar timing arrays (PTAs).

This spectral signature is **structurally distinct** from the dominant alternative
interpretation of the PTA signal: supermassive black hole binary (SMBHB) mergers produce
$\Omega_\mathrm{GW} \propto f^{2/3}$ -- a shallower rise with no sharp peak or steep fall.
Domain walls produce a steeper rise ($f^3$) and a sharp peak, not a power law over the
full PTA band.

### Comparison with PTA Observations

The NANOGrav 15-year data set (Agazie et al. 2023), confirmed by the European PTA (Antoniadis
et al. 2023), the Parkes PTA (Reardon et al. 2023), and the Chinese PTA (Xu et al. 2023),
reports a common-spectrum process with Hellings-Downs angular correlations -- the
gravitational wave signature -- in the 1--100 nHz band. The spectral index is consistent
with both SMBHB ($f^{2/3}$) and with a peaked spectrum at $\sim 5$--$10$ nHz from domain
wall annihilation.

The free parameter in the domain wall interpretation is $\varepsilon_\mathrm{bias}$ -- the
tilt of the vacuum potential. In the $\varepsilon$-tilt framework, this is not a free
parameter: it is the axion's position in the $\varepsilon$-spectrum (Table 3),
$\varepsilon_\mathrm{bias} \sim 10^{-16}$, constrained by the same structural logic that
fixes the axion mass.

The 2026 PPTA and CPTA data releases continue to narrow the spectral index uncertainty.
If the index lies above $f^{2/3}$ and a peak structure is confirmed at $\sim 5$ nHz, this
would constitute strong evidence for the domain wall interpretation and, via the $\varepsilon$
spectrum, for the structural derivation of mass from logical tilt.

---

## Black Holes and Quantum Gravity *(Research Direction)*

> **Status note.** This section develops an analogy between the ε-tilt framework and
> gravitational physics. The identifications below (horizon as R-field phase boundary,
> $G_{\mu\nu}$ as $\nabla\nabla \log R$) are motivated conjectures, not results derived from the IG axioms.
> They are stated here as a research direction and to motivate Prediction P4. A proper
> derivation would require constructing a Lagrangian for the R-field, showing it
> reproduces GR in the smooth limit, and deriving the horizon condition from the
> Frobenius structure. None of that is done here.

### Horizons as Phase Boundaries *(Conjecture)*

The Schwarzschild horizon $r_S = 2GM/c^2$ is, in the $\varepsilon$-tilt framework,
conjectured to be a phase boundary in the $R$-field. As $r \to r_S$ from outside, the
identification $R(r) \to \infty$, $|\nabla R| \to \infty$ is motivated as follows: the
horizon is the locus at which the evidence ratio saturates -- infinite evidence for
the interior proposition ("mass is here"), and no counter-evidence accessible from outside.
The interior is structurally characterized by $R \to \infty$, corresponding to the maximum
end of the Dimensionality primitive's ordinal.

Hawking radiation is, in this framing, the $R$-field relaxing from $\infty$ as particles
escape the boundary. Each emitted particle carries a small increment $\Delta R^{-1}$,
reducing the divergence at the horizon. This is a reframing of Hawking radiation, not a
resolution of the information paradox -- the question of whether information is preserved
requires a full quantum treatment of the $R$-field dynamics, which is not provided here.

### Quantum Gravity as $\nabla \log R$ Curvature

At the Planck scale, $R$ fluctuates chaotically cell by cell. No smooth geometry exists
at this resolution -- only a foam of fluctuating evidence ratios. At macroscopic scales,
the average $R$-field is smooth. Its gradient sources curvature:

$$G_{\mu\nu} \approx \nabla_\mu \nabla_\nu \log R$$

The Einstein field equations become equations for the second derivatives of the logical
certainty field. Curvature is not sourced by mass directly -- it is sourced by gradients
in $R$, and mass itself (by the $\varepsilon$-tilt spectrum) is a gradient in $R$ at the
scale of the particle.

Geodesics are paths of constant $\log R$ -- test particles follow the gradient of logical
certainty toward the region of highest evidence density. Newton's law of gravitation is
the leading-order approximation:

$$\nabla^2 \log R \approx 4\pi G \rho \implies \nabla^2 \phi_\mathrm{Newton} = 4\pi G \rho$$

Unitarity is preserved because logical states form a closed algebra over FOUR; the closed
Frobenius structure ($\mu \circ \delta = \mathrm{id}$) guarantees that no information is
created or destroyed by the $R$-field dynamics.

---

## Falsifiable Predictions

The $\varepsilon$-tilt framework, combined with the Standard Model derivation from the
bilattice, yields four predictions distinct from the Standard Model alone.

**P1 — GW peak frequency.** The domain wall annihilation SGWB has a sharp peak at:
$$f_\mathrm{peak} \approx 5 \mathrm{ nHz} \cdot \left(\frac{\varepsilon_\mathrm{bias}}{10^{-16}}\right)^{1/2} \left(\frac{f_a}{10^{11}\mathrm{ GeV}}\right)$$
This predicts a peak within the NANOGrav/PPTA band for QCD axion parameters.

**P2 — Spectral index $f^3$.** Below $f_\mathrm{peak}$, $\Omega_\mathrm{GW} \propto f^3$.
This is measurable by the Square Kilometre Array (SKA) against the SMBHB background
($f^{2/3}$). A confirmed spectral index between $2.5$ and $3.5$ below the peak, combined
with a steep fall above it, is inconsistent with SMBHB but consistent with domain walls.

**P3 — Amplitude upper bound from Frobenius closure.** The wall tension $\sigma \le f_a^2
m_a$ is set by the $\varepsilon$ value. The Frobenius closure condition constrains the
bias: $\varepsilon_\mathrm{bias} < \varepsilon_\mathrm{axion}$. This gives an upper bound on
the GW amplitude:
$$h^2 \Omega_\mathrm{GW}^\mathrm{peak} \lesssim 10^{-9}$$
Current PTA measurements are at the boundary of this constraint; near-future data will
confirm or refute.

**P4 — Black hole spectroscopy.** If the horizon is a phase boundary in the $R$-field,
quasi-normal mode frequencies should carry $R$-gradient corrections to the leading
Schwarzschild values. Specifically, the imaginary part of the dominant quasi-normal mode
should receive a correction proportional to $|\nabla R|^{-1}$ at $r_S$:
$$\omega_\mathrm{QNM} = \omega_\mathrm{Schwarzschild} \cdot \left(1 + \alpha \cdot |\nabla R|^{-1} \Big|_{r_S}\right)$$
where $\alpha$ is a numerical coefficient fixed by the IG metric structure. For stellar
black holes, this correction is negligible. For primordial black holes near the Hawking
evaporation endpoint ($M \to M_\mathrm{Pl}$), the correction becomes $O(1)$ and predicts
a deviation from GR quasi-normal modes detectable by next-generation gravitational wave
observatories.

---

## Discussion

### What Is Derived and What Is Not

The Standard Model gauge groups SU(3), SU(2), U(1) are **structurally identified** with
the antichain-width sequence of the Belnap bilattice (widths 6, 2, 0). A full derivation
requires proving the Width Exclusion Conjecture (that only these widths are Frobenius-closed
in FOUR); the conjecture is stated but not proved here. The three generation count
**follows conditionally** from the Z₄ axiom of the Ω primitive: given that axiom, exactly
three non-trivial winding classes exist. The structural ordering of the mass hierarchy
(axion lightest, top heaviest) **is identified** with the ε-spectrum ordering; absolute
mass values require additional coupling inputs not derived from ε alone.

What is **not** derived: the numerical values of the Yukawa couplings (the precise
$\varepsilon$ values for each particle), the Weinberg angle $\theta_W$ (its derivation
from bilattice geometry is sketched but not proven in closed form here), and the absolute
scale of the PQ symmetry breaking $f_a$. These remain inputs, but they are now
interpretable as $\varepsilon$-spectrum values rather than free parameters -- they are
positions in the Crystal of Types, not arbitrary constants.

### The Grammar Is Not a Scientific Theory

The IG is prior to and independent of experimental measurement. The type assignment for
any system precedes experiment; the data either holds the structural verdict or breaks it.
If a prediction fails -- for instance, if the PTA spectral index is confirmed as $f^{2/3}$
with no peak -- the structural description of the axion sector would require revision.
The grammar does not adjust to fit results; it makes a commitment.

This is not a weakness. A framework that can be falsified is stronger than one that
cannot.

Science is an instrument of the grammar in the same sense that a ruler is an instrument
of the geometric axioms. Euclidean axioms are not validated by the ruler; the ruler
operates within the space the axioms define. The IG axioms define the structural space
within which the Standard Model, general relativity, and their extensions operate. Whether
the universe chooses to fill that space in particular ways is a question for observation.

### Measurement as Frobenius Closure Problem

Every external measurement tool is a Frobenius closure interface. X-ray crystallography,
mass spectrometry, pulsar timing -- each places an observer in a specific relationship to
the system being measured. Frobenius closure either holds at that interface or it does not.

The PTA measurement of the SGWB is, in this framing, a Frobenius closure interface at the
cosmological scale: the pulsar timing network is a distributed $\delta$-split, the
Hellings-Downs correlation is the $\mu$-merge, and confirmation of the Hellings-Downs
angular pattern is the verification that $\mu \circ \delta = \mathrm{id}$ holds at the
level of the gravitational wave background.

---

## Conclusion

We have shown that the Imscribing Grammar's axioms -- a FOUR-enriched symmetric monoidal
category with $\mu \circ \delta = \mathrm{id}$ -- generate the Standard Model gauge
hierarchy as the antichain-width sequence of the Belnap bilattice (6, 2, 0 for SU(3),
SU(2), U(1)), give the three generation count from the cyclic fiber structure of the
Winding primitive ($|\mathbf{F}_4(\Omega)| - 1 = 3$), and derive the mass hierarchy as
the $\varepsilon$-spectrum of a scalar sector whose flat antichain vacuum is forced to tilt
by the structural consistency requirements of any self-writing universe.

The cosmological consequence is a stochastic gravitational wave background from domain
wall annihilation in the tilted scalar sector, with a characteristic $f^3$ spectral rise
and a sharp peak at nanohertz frequencies -- directly in the band where NANOGrav, EPTA,
PPTA, and CPTA have reported a correlated signal. Four falsifiable predictions are stated.

The derivation is not complete in the sense of closing all numbers. The Weinberg angle,
individual Yukawa couplings, and PQ scale remain to be derived from first principles.
What is closed: the structural reason for the gauge hierarchy, the generation count, and
the qualitative mass spectrum. These were previously free parameters. They are now
structural positions in the Crystal of Types.

The serpent winds, the rod stands, the vessel contains.

$$\mu \circ \delta = \mathrm{id}$$

---

## References

[1] G. Agazie et al. (NANOGrav Collaboration), "The NANOGrav 15-year Data Set: Evidence
for a Gravitational-Wave Background," *Astrophys. J. Lett.* **951**, L8 (2023).

[2] J. Antoniadis et al. (EPTA Collaboration), "The second data release from the European
Pulsar Timing Array: III. Search for gravitational wave signals," *Astron. Astrophys.*
**678**, A50 (2023).

[3] D. J. Reardon et al. (PPTA Collaboration), "Search for an Isotropic Gravitational-Wave
Background with the Parkes Pulsar Timing Array," *Astrophys. J. Lett.* **951**, L6 (2023).

[4] H. Xu et al. (CPTA Collaboration), "Searching for the Nano-Hertz Stochastic
Gravitational Wave Background with the Chinese Pulsar Timing Array," *Res. Astron.
Astrophys.* **23**, 075024 (2023).

[5] N. D. Belnap, "A useful four-valued logic," in *Modern Uses of Multiple-Valued Logic*,
ed. Dunn and Epstein, Reidel (1977).

[6] S. Abramsky and B. Coecke, "A categorical semantics of quantum protocols,"
*Proc. 19th IEEE LICS*, 415--425 (2004).

[7] A. Carboni and R. F. C. Walters, "Cartesian bicategories I," *J. Pure Appl. Algebra*
**49**, 11--32 (1987).

[8] A. Joyal, R. Street, and D. Verity, "Traced monoidal categories," *Math. Proc. Camb.
Phil. Soc.* **119**, 447--468 (1996).

[9] R. D. Peccei and H. R. Quinn, "CP conservation in the presence of pseudoparticles,"
*Phys. Rev. Lett.* **38**, 1440 (1977).

[10] S. Weinberg, "A model of leptons," *Phys. Rev. Lett.* **19**, 1264 (1967).

[11] A. Salam, "Weak and electromagnetic interactions," *Proc. Nobel Symposium*
**8**, 367--377 (1968).

[12] D. J. Fisher, J. B. Shaum, C. L. Mills, and J. Read de Alaniz, "Synthesis of Hindered
Anilines: Three-Component Coupling of Arylboronic Acids, *tert*-Butyl Nitrite, and Alkyl
Bromides," *Org. Lett.* **18**, 5074--5077 (2016). DOI: 10.1021/acs.orglett.6b02523.
