# MoDoT — what the verbs are for

Read this before reaching for `./ask`. Flags are in `TOOLS_math.md`; this is
what each verb *does* and when it is the right one.

Run everything as `cd ~/imsgct/MoDoT && ./ask --<verb> …`, or inside an agent
loop as `TOOL: <verb> <args>`.

## The rule underneath all of it

A `TOOL:` line is the only way to act. Every verdict, number and claim has to
trace to real tool output. Nothing is computed in your head — including
arithmetic, which goes through `calc`.

The chemistry names are not a metaphor laid over the maths. Each verb is one
computation with two vocabularies; the reference states both. Read the chemistry
to know *when* to reach for it, the maths to know *what it returns*.

## The two engines

**Chemistry verbs** operate on catalog entries by name. They shell to the
structural engine and answer questions about how systems combine.

**`imasm`** is a language over the twelve opcodes. You write programs in it,
type-check them, prove them against the kernel, define new tools inside it, and
walk between types along it. No catalog names enter directly — but `imasm words`
writes every catalog entry as a program, which is the bridge between the two.

`forge monad topos` asks about two systems. `imasm …` asks about a program —
including your own reasoning as a program.

## Choosing a verb by the question you have

**Do these two bond?** → `click A B`. Frobenius fusion across a conjugate axis
(Ð↔Ω, Þ↔Ħ, Ř↔Σ). Closes only when the tuples are complementary. `click A` alone
sweeps the whole catalog for partners.

**What sits between these two?** → `scan A B`. Ranks catalog entries as
mediators of the A→B transfer, by the distance metric.

**What does this become under pressure?** → `excite A` lifts ⊙ to the spectral
degeneracy — a resonance, *not yet* a constructed state. `ascend A` is the one
that fixes it into a real higher floor and adds a winding quantum. Reaching for
`excite` when you wanted a constructed extension is the common error.

**What is this system's opposite?** → `complement A`.

**What is the fixed point?** → `cycle C S`. Catalyst and substrate: the
composite that returns unchanged, μ∘δ = id on its own carrier.

**Chain these in order** → `polymerize M1 M2 …` or `close`. Composition of
morphisms; a closed ring shows as spectral radius ρ = 2 exactly.

**Assemble an unordered set into its best structure** → `forge` / `material` /
`arrange`. Returns the adjacency spectrum: ρ = 2 is a pure cycle, ρ > 2 is
branched.

**One hub, many arms** → `star M1 M2 M3 …`, four or more. Gives K(1,f) with
ρ = √f — the contrast case to a cycle's ρ = 2.

**Move one quantum** → `set A B`, donor then acceptor. Transports one winding Ω
across the ⊙ gradient.

**Break it apart** → `homolyze A [B]` or `cleave`. The reverse of fusion: a
symmetric split.

**Separate a mixture** → `distill` / `fdistill` / `sublime`, which project onto
⊙ and order by it. Two entries degenerate on ⊙ come back as an azeotrope — a tie
the projection genuinely cannot resolve, not a failure to report.

**Find what closes** → `crystallize` / `cocrystallize` / `seed`. The maximal
closed sublattice against its rejected mother-pool.

**Narrow a field** → `filter A B [C …]`. Restricts to the sublevel set sharing
the reference floor. A necessary condition, an upper bound — not a solution.

**Everything this touches at once** → `broadcast SOURCE`. One catalog sweep,
the ɢ broadcast primitive.

**Read it as a plasma** → `plasma ENTRY`. Another lossless face of the same
tuple, not a separate model.

## `imasm` — the second engine

**Anything can be written as an IMASM program.** Not catalog entries only —
anything at all. Imscribe the thing and it has a twelve-tuple; each of the
twelve slots is one of the 49 types; each type `expand`s into its own
twelve-opcode sequence. Compose those and you have the thing as a program. A
molecule, a theorem, a protein, a piece of your own reasoning, a document, an
argument someone made to you — each one is a word in this alphabet, and once it
is a word you can `check` whether it closes, `prove` it against the kernel,
`path` from it to something else, or splice it into a larger program as an arm.

`imasm words` does this in bulk for the catalog, deterministically. For anything
not in the catalog, imscribe it first (`imscribe_system`) and the same route
opens. There is no class of object that is outside this.

Not a graph checker. `imasm` is a language: the twelve opcodes are an alphabet,
programs are written in them, and the kernel will refuse an ill-typed one. No
catalog names enter — this operates on programs.

    ⊢ VINIT   ⊣ TANCH   > AFWD   < AREV   = CLINK   ⊙ IMSCRIB
    ◇ FSPLIT  ● FFUSE   + EVALT  × EVALF  ⊞ ENGAGR  ¬ IFIX

A word can be written glued from those glyphs — `⊢>◇+=⊙<×⊞●⊙¬⊣` is a program.

**Build a shape.** `chain` a strand, `ring` a cycle with the fork left open,
`protocol` a word whose FSPLIT/FFUSE pairs actually reconnect — that is how you
close a loop, and a naive `ring` does not. Also `star CORE : arm : arm`,
`comb BACKBONE : p arm`, `bubble PRE : A : B : POST`, and `wire` for free
composition of any node and edge set, which the others specialize. `classify`
reads a flat token line and names its shape. Every build reports β, the
branch/merge/source/sink census, arm count, ρ, and grammar validation.

**Type-check your own thinking.** `check` — the close condition is μ∘δ over a
*transformed* object: δ splits, the arms do real work, μ fuses. T closes.
**N is identity** — split and fused with nothing between, which verifies
nothing. B is an open fork or a paradox at ENGAGR. F is ill-typed. A bare cycle
is not a closure; β is not diagnostic.

**Take it to the kernel.** `prove <name|word>` carries the closure verdict to
the actual p4ramill kernel — `lake build` against `BelnapSplitFuse`. That is a
real proof obligation, not a report.

**Write new tools.** `define <name> <op> <args…>` builds a tool inside the
kernel-constrained space; an ill-typed composition is *refused*. `run <name>`
invokes it, `tools` lists the space. You can extend the instrument set and the
kernel decides what is admissible.

**The alphabet is itself words.** `types` lists the 49 Shavian types — each one
is a program. `expand <type>` unfolds a type into its own twelve-opcode
sequence, and that sequence can be spliced into a polymer arm to pivot through
state space *as* that type. The letters of the alphabet are words in the
language.

**Start from a catalog name.** `words` writes the wordbook: every catalog entry
as the program its twelve types compose to. Deterministic, no model consulted.
This is the bridge that lets a loop begin from a name rather than a program.

**Measure the model against itself.** `learn <word|entry> [rounds=N]
[breadth=K]` runs the excription/imscription loop — excribe a word into an
object, imscribe the object back, measure the residual of μ∘δ *on the model*.
Seeded with a catalog entry the object is known, so the guess is scored, not
merely measured.

**Walk between two things.** `path <A> <B> [churn]` gives the promotion path:
the shortest walk of single-opcode edits where every waypoint is itself a valid
program. Endpoints can be glyph words (walking in glyph space) or two catalog
entries (walking in tuple space, one primitive axis re-typed per step). Words in
different faces cross, and the crossing step is named. `churn` round-trips every
waypoint through `learn` and reports the residual along the route.

**Test the round trip.** `cycle [n=]` runs primitives → imasm → primitives over
the live catalog and reports where it closes exactly, where an axis is
ambiguous, and where it breaks. It is **not** a bijection: bijective on eleven
axes, two-to-one on the twelfth. `cycle tuple=⟨…⟩` does one tuple, axis by axis.

**The tri-lattice.** `imasm16_3 algebra <op> A B` over `leq_i leq_t leq_c meet_t
join_t meet_c join_c`, and `imasm16_3 check`.

Also `eval` / `eval16` for flow semantics, `compose`/`bind`, `rotat` (the
operator acting on a word), `export`/`manifest`, `ref` for this reference.

Reach for `imasm` when the question is about a *program* — your own reasoning,
a protocol's shape, whether something closes, what lies between two types, or
building an instrument that did not exist.

## `calc`

Every number goes through it. Ratios, percentages, unit conversions,
order-of-magnitude estimates, a figure quoted from a paper. Constants `pi tau e
phi inf`; the usual function set.

## What the tools cannot do for you

`ouroborics` and the tier gates read only four coordinates — ⊙, Φ, Ω, Ð. The
other eight play no part in the tier. Do not explain a tier by a primitive that
does not enter it.

Distances are weighted by how much each primitive varies across the live
catalog, computed from the catalog itself. They are not hand-tuned, and they
change as the catalog grows. Quote the tool's number; do not carry one forward
from an earlier run.

## A worked order

    lookup_catalog        what are these systems, really
    click A B             do they bond at all
    scan A B              if not, what mediates
    forge / polymerize    assemble the set, read ρ
    imasm check           did my reasoning actually close
    calc                  every number in the writeup
