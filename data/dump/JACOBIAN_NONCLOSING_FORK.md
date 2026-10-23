# The Jacobian counterexample is a non-closing fork

Alpöge's 2026 counterexample to the Jacobian conjecture in three variables is,
in the Grammar, a δ that admits no μ: a fork opening three alternatives that
never rejoin. Étale everywhere is the well-typing; non-properness is the open
fork. This is the map placed in the crystal.

## The map

With `u = z(1+xy)² + y²(3xy+4)`:

    F₁ = (1+xy)·u                       deg 7
    F₂ = y + 3x·u                       deg 6
    F₃ = -x(x²z + 3xy - 2)              deg 4

`det J_F ≡ -2` — constant and nonzero, so F is étale over all of ℂ³.

## It is 3:1, not injective

Three distinct points share one image:

    (0, 0, -1/4), (1, -3/2, 13/2), (-1, 3/2, 13/2)  ↦  (-1/4, 0, 0)

The generic fibre has degree 3 (Gröbner elimination over random rational
targets; the z-eliminant is the cubic factor with constant leading coefficient
8, so every target carries exactly three z-values). F has no inverse in any
category, polynomial or otherwise. The conjecture failed on injectivity, not on
polynomiality.

## Non-properness, pinned to a curve

The genuine x-eliminant, after dropping the spurious `-c·x¹²` resultant factor,
is the cubic

    P(x) = L·x³ + (4 - 3bc)·x - 2c,   L = 27a²c² - 18abc + 16a + b³c - b².

`L = 0` is the non-properness surface: one sheet escapes to infinity. The image
misses points where the whole cubic collapses — `L = 0` and `4 - 3bc = 0` and
`c ≠ 0`. Solving this leaves a single curve, reached at a double root
(`729t² - 216t + 16 = (27t - 4)²`, `t = ac² = 4/27`):

    M = { ac² = 4/27,  bc = 4/3,  c ≠ 0 },   (a,b,c) = (4/27c², 4/3c, c).

On M two sheets escape to infinity together and the third with them, so the
fibre is empty. Verified: (4/27, 4/3, 1) and (1/27, 2/3, 2) reduce to ⟨1⟩ (no
solution), while the neighbour (4/27, 4/3, 11/10) carries the full fibre of 3.

F is therefore étale, dominant, and generically 3:1, yet neither proper nor
surjective: it drops the entire curve M from its image. Local invertibility at
every point does not assemble into a global inverse.

## The reading in the Grammar

The IMASM engine gives the verdict directly. The map's shape — open a fork, do
work on the arms, never fuse — is the word `⊢∈>⊤<⊣`:

    IMASM check → B (open)
    a δ fork or μ fuse dangles unreconnected: the decision opens alternatives
    it never rejoins.
    μ∘δ: OPEN

The inverse-admitting map the conjecture expected is the same word with the
fuse restored, `⊢∈>⊤<∋⊣`, which returns T with μ∘δ CLOSED. The counterexample
is precisely the difference between those two words: the missing ∋.

Pointwise invertibility holds at every single point of the domain and there is
still no global reconstruction, because closure is not pointwise — closure is
the fuse. A δ that forks and provides no μ reads B, and B is where this map
lives. The counterexample sits at the Composition axis (∋) in its non-closing
value.

## Where it sits in the crystal

Imscribed procedurally (guided generation, one primitive at a time), the map is

    jacobian_counterexample_alpoge = ⟨𐑨𐑰𐑾𐑗𐑞𐑪𐑔𐑜𐑢𐑫𐑕𐑷⟩

registered in IG_catalog.json. Distance run against the δ/μ-family entries
localizes the non-closing fork to a single axis.

Its nearest conceptual sibling is `covering_space_theory`, sharing the
load-bearing slots — Topology 𐑰, Kinetics 𐑪, Scope 𐑔, Criticality 𐑢,
Chirality 𐑫. The decisive difference is Composition ∋:

- `covering_space_theory`: ∋ = 𐑝 (∧, conjunctive — sheets glue, a proper
  covering, μ exists).
- this map: ∋ = 𐑜 (∨, disjunctive — alternative preimages, any one branch
  suffices, sheets never glue).

So the counterexample is covering-space theory with Composition demoted ∧ → ∨.
An étale map is locally a covering; this is the one that carries the covering's
whole criticality/scope/kinetics signature yet fails to close, because its
sheets are alternatives that never fuse. The missing ∋ of the IMASM word
(`⊢∈>⊤<∋⊣` closes to T, `⊢∈>⊤<⊣` opens to B) is exactly this ∧ → ∨ flip.

Against the pure fork archetype `fork_alpha` the map agrees on Topology 𐑰 and
on ∋ = 𐑜 (the shared fork DNA) and parts at Criticality: `fork_alpha` is ⊙
(ramified, with branch points), this map is ⊙ = 𐑢 (no critical points, far from
threshold). A fork with no ramification — which is what étale means: a branching
locally invisible and globally unclosable.

## The survivor

n = 1 is trivial, n ≥ 3 is now dead (M and the collision extend by the identity
to every higher dimension), and the plane n = 2 is the only case left standing.
A distinction that holds at 2 and fails at 3 is the shape already carried in the
crystal: `2ⁿ = n²` only at n = 2 and n = 4.
