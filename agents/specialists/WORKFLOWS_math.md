# Worked chains — quantum surfaces against hard lemmas

Hand-written, not generated. Source of record for the tools themselves is
`ig-docs/QC_TOOLZ.md`; this file is about how to *compose* them, and about the
four traps that make a chain return a confident wrong number.

Every chain below is a real sequence, not an illustration. Run the kernel with
several commands per boot — the QEMU start dominates any single short command:

```
cd ~/imsgct/mOMonadOS && ./run_serial_cmds.sh "<cmd>" "<cmd>" …
```

---

## Trap 1 — three strands is a 1×1 matrix

`fusion_space_dimension(n)` is the **vacuum** sector, dim Hom(τⁿ,1) = F_{n−1}.
At n=3 that is one-dimensional: the braid representation is a scalar, and every
non-Abelian invariant computed from it is a property of a trivial matrix. A
lemma about non-Abelian braiding evaluated at three strands is not weakly
supported, it is vacuous.

**Use n ≥ 4.** The familiar B₃ statement lives in Hom(τ³,τ), which is
two-dimensional and equal in dimension to Hom(τ⁴,1).

Before trusting any braid-derived claim, state the strand count and the sector.

## Trap 2 — glyphs, never opcode names

The kernel's IMASM verbs take glyphs. `cycle ⊢⊙⋈∈>⊤<⊞⊥∋◻⊣` works;
`cycle VINIT IMSCRIB …` returns "no IMASM glyphs in that word". Only the twelve
are tokens — a retired mark is not canonicalised to one, it reads as nothing.
If a ring walk comes back empty, check this before concluding anything about
the word.

## Trap 3 — braid sampling does not search

Universality gives reachability, not findability, and a discrete space has no
gradient. At seven strands against an exact d=8 SIC, three hundred random words
per length peak at 0.75 overlap by length 8 and get *worse* as words lengthen,
because a long random braid word is a near-random state; against Haar states at
equal sample count they lose on best and mean with four times the spread.

So a task of the form "find a braid realising X" is never answered by sampling.
Answer it by compilation (`qc`, which is Solovay–Kitaev), by a closed form, or
by the Gauss-sum route in chain C.

## Trap 4 — a small braid at a large root returns V(1)

A root near 1 sends a short word to something near the value at 1. Reaching a
large level *through a braid* wants a crossing count on the order of the level.
When the level is large, go to the Gauss sum directly.

---

## Chain A — classify a compiled circuit structurally

Lemma shape: *what kind of object is the circuit that realises this gate
sequence, and does it close?*

```
./run_serial_cmds.sh \
  "qc HTSX 8" \
  "bg tuple <word> <strands>" \
  "cycle <glyph-word>" \
  "weight <glyph-word>"
```

`qc` compiles over H T S X to a braid word; gates need no separators and a
trailing digit run is the depth, so `qc HTSX8` and `qc H T S X 8` are the same
circuit. `bg tuple` lifts the word to a 12-primitive tuple — its winding is
`writhe · 2/5 mod 1`, a closed form in the writhe, so it never touches
eigenvalue phases and cannot pick up branch error. Then hand the tuple to the
grammar: `imscribe("ouroborics", …)` for the tier, `compute_distance` against a
reference entry for the gap.

`cycle` reads the whole ring over every cut; `weight` walks it linearly from one
cut. They disagree by construction — a linear read stops at a fixation the ring
does not have — and that disagreement is information, not a bug. Prefer `cycle`
when the question is about the word as a closed object.

Use `bi <gens…> [start:count] [/fold]` or `qc draw` when a crossing pattern
needs eyes on it: the terminal form breaks the under-strand so a crossing and
its inverse are distinguishable rather than merely counted. A compiled circuit
runs to hundreds of generators, so window it (`40:24`) rather than dumping it.

## Chain B — establish a Jones value against two independent engines

Lemma shape: *this link has that invariant.*

Never rest on one engine. The kernel's `fibqc jones` is pinned at the Fibonacci
root, one fifth of a winding, with values in Q(ζ₅) on the tenths lattice.
`scripts/jones_at_root.py` is independent: it builds the Kauffman bracket as an
exact Laurent polynomial by state sum, converts to Jones in t, and substitutes a
root only at the end.

```
./run_serial_cmds.sh "fibqc knot trefoil" "jp <gens…>"
python3 scripts/jones_at_root.py "<braid>" <strands> <root>
```

Agreement across a pinned-root numeric engine and an exact-polynomial engine is
a real cross-check; agreement of one engine with itself is not.

**These two do not currently agree, and the kernel is the one that is right.**
On the trefoil, closure of `1 1 1` at two strands, the textbook Jones polynomial
V(t) = −t⁻⁴ + t⁻³ + t⁻¹ evaluated at t = e^{2πi/5} is
−0.809017 − 1.314328i, modulus 1.543362. The kernel returns exactly that, both
parts, to six digits. `jones_at_root.py` returns 1.309017 + 0.951057i, modulus
1.618034, and `QC_TOOLZ.md` records that same 1.618034 as the calibration
point. It is not a normalisation difference: the script sends the unknot to 1,
so it is computing normalised Jones, and the ratio 1.0484 is not a quantum
dimension.

So calibrate against the closed form, not against either engine, and treat a
φ appearing where the textbook says 1.543362 as the script's defect rather than
a golden-ratio result. The trefoil is the case to check first when either
engine is touched.

## Chain C — reach a quadratic root the braid cannot reach

Lemma shape: *√m is reachable, and the Stark unit assembled from it is the
recorded one.*

The Fibonacci level supplies the prime 5 and nothing else. For the d=2048
discriminant 4190205 = 3 · 5 · 409 · 683, the other three primes need their own
levels, and by trap 4 a braid will not carry you to 409 or 683.

Take each prime at its own level as a quadratic Gauss sum,
g(p) = Σ_k (k|p) ζ_p^k, which is √p for p ≡ 1 mod 4 and i√p for p ≡ 3 mod 4.
Both primes ≡ 3 contribute a factor of i, so the pair makes the product real and
negative, and its magnitude is √4190205 = 2046.999023. Then
ε = (2047 + |product|)/2 = 2046.9995114801, which is the value the tower's
regulator confirms to ten digits.

The braid route is still worth running where it *is* reachable: √3 lives in
Q(ζ₁₂), and at level 12 both the Hopf link and [1,2,1] give |V| = 1.732051.
That is the check that the Gauss-sum route and the knot route are computing the
same object before you rely on the sums for the primes braids cannot reach.

Cross-check the tower side with `d2048 tower|redei|grammar|pari` and the d=12
side with `d12 tower|existence|duallink`.

## Chain D — land the result as a theorem

A number that agrees is not yet a lemma. Close it in `p4rakernel` as a
`native_decide` fact over the exact integers or rationals, never over floats,
and give the witness rather than an unbounded existential — an `∃ k : ℕ` with no
`Decidable` instance cannot be filtered over and `native_decide` will have
nothing to evaluate.

Register the module in `lakefile.toml` in the same change. A module absent from
the globs is never compiled, so a green whole-project build number says nothing
about it, and "builds clean" claimed for an unregistered file is the most common
false verification in this codebase.

## Chain E — when the surface is wrong

Five surfaces exist and they are not variations on one engine. The kernel is the
canonical path. Reach for `m3iosis` only where the kernel does not expose what
you need — every one of its subcommands has a Rust counterpart. Reach for
`navigators/quantum_tnn.py` when the question is whether a circuit is worth
running at all: it records the crossover plainly, and a circuit whose
`t_gate × n_gates × ε_2q` exceeds 0.1 is one where hardware loses to classical
simulation, which is about ten two-qubit gates on current machines. Reach for
ParaASM when the question is Belnap rather than unitary — `belnap_shor.rs`
carries the finding that the Belnap QFT is not a gate sequence at all, the
period r being carried in the 2:1 coherence cost ratio of B-bias against T-bias.

Choosing the surface is the first move, not an afterthought. State which one the
lemma belongs to before running anything.
