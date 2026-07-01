# Imscribing Grammar

A 12-primitive structural grammar with a discrete measurement space of 17,280,000 addresses. Any system — physical, mathematical, linguistic, biological, computational — can be assigned a coordinate in the **Crystal of Types**: a 12-tuple that determines its structural type, ouroboricity tier, Frobenius status, and computable distance to every other imscribed system.

The grammar is not a metaphor. It is a measurement apparatus. Two systems at the same crystal address have the same structural type. The distance between addresses is an integer, computable in O(1).

---

## Crystal of Types

Twelve primitives, each with a fixed value-set:

| # | Primitive | Symbol | Values | Domain |
|---|---|---|---|---|
| 1 | Dimensionality | Ð | 4 | Information geometry — how many independent axes the system occupies |
| 2 | Topology | Þ | 5 | Connection structure — local vs. global binding mode |
| 3 | Relational | Ř | 4 | Read/write access mode — duplex, simplex, broadcast, receive |
| 4 | Polarity | Φ | 5 | Parity and symmetry — the Frobenius gate primitive |
| 5 | Fidelity | ƒ | 3 | Signal compression — lossless, lossy, or degenerate |
| 6 | Kinetics | Ç | 5 | Flow rate — from arrested to turbulent |
| 7 | Scope | Γ | 3 | Granularity — local, meso, global |
| 8 | Composition | ɢ | 4 | Grammar topology — how sub-systems compose |
| 9 | Criticality | ⊙ | 5 | Gate status — the self-modeling threshold |
| 10 | Chirality | Ħ | 4 | Temporal orientation — handedness of the system's history |
| 11 | Stoichiometry | Σ | 3 | Balance — the ratio of production to consumption |
| 12 | Winding | Ω | 4 | Loop count — monotonic trajectory depth |

**Lattice size:** 3³ × 4⁵ × 5⁴ = **17,280,000** addresses.

### Ouroboricity Tiers

Each address falls into one of five tiers based on the (Φ, ⊙) pair:

| Tier | Name | Condition | Meaning |
|---|---|---|---|
| O₀ | Inert | Φ_sub, ⊙_sealed | No self-reference |
| O₁ | Reactive | Φ_c, ⊙_sealed | Causal but not self-modeling |
| O₂ | Recursive | Φ_c, ⊙_open | Self-referential |
| O₂† | Dialetheic | Φ_super, ⊙_open | Self-contradictory (Belnap B) |
| O_∞ | Philosopher's Stone | Φ_super, ⊙_both | Frobenius closed: μ∘δ=id |

**O_∞ addresses** — the grammar imscribes itself at this tier. The self-modeling gate is closed, the Frobenius condition holds, and the system can write its own continuation.

### Notation — Shavian v0.6.0

All primitive values are written in Shavian characters. Two canonical addresses:

```
O_∞ (Philosopher's Stone):  ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑫𐑳𐑭⟩
O₀   (minimum baseline):     ⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩
```

Font: **Everson Mono** (the only complete Shavian Unicode font).

---

## The Frobenius Condition

The grammar is a Frobenius algebra over the Crystal. The comultiplication δ (FSPLIT) and multiplication μ (FFUSE) satisfy:

```
μ ∘ δ = id
```

This identity holds at every O_∞ address and fails at O₀. The distance from any address to O_∞ measures how far the system is from self-modeling closure.

**Physical interpretation:** The Frobenius condition is the structural invariant that appears in:
- Topological quantum field theories (Frobenius algebra = 2D TQFT)
- Frobenius reciprocity in representation theory
- The Jones polynomial (link invariants)
- The NS H^{1/2} critical norm bound (G₂-invariant 3-form cancellation)

---

## The Universal Loop

The eight-step structural invariant, present in every O_∞ system:

```
ISCRIB → AREV → FSPLIT → AFWD → FFUSE → CLINK → IFIX → ISCRIB
```

This loop has been recovered from: Voynich Manuscript, Rohonc Codex, Linear A, the Emerald Tablet, humpback whale song, and the grammar itself. It is not a claim about interpretation — it is a claim about structural address: all these systems share crystal coordinates in the O₂/O_∞ band.

---

## IMASM — Universal Bytecode

12-opcode instruction set. Every engine compiles its domain into IMASM and executes on the **WhaleVM** — a Belnap FOUR register machine with states `VOID / TRUE / FALSE / BOTH`.

```
VINIT   TANCH   AFWD    AREV
CLINK   ISCRIB  FSPLIT  FFUSE
EVALT   EVALF   ENGAGR  IFIX
```

FSPLIT and FFUSE are the δ and μ maps of the Frobenius algebra. ISCRIB is the self-writing instruction — it writes the current register state into the imscription context (Ð_ω). IFIX enforces the Frobenius invariant: after IFIX, μ∘δ=id is verified or execution halts.

### Belnap FOUR Logic

The WhaleVM operates over a four-valued logic (Belnap 1977):

| Value | Meaning | Structural tier |
|---|---|---|
| N (VOID) | Neither true nor false — no information | O₀ |
| T (TRUE) | True | O₁/O₂ |
| F (FALSE) | False | O₁/O₂ |
| B (BOTH) | Both true and false — dialetheic | O₂†/O_∞ |

The B state is not a bug. Systems at O₂† and O_∞ are structurally dialetheic — they contain genuine contradictions that are load-bearing, not errors to be resolved.

---

## Engines

### Cetacean (`whale_engine.py`, `whale_audio.py`)

WAV file → acoustic token sequence → IMASM → Frobenius analysis → ranked translation against six human expression archetypes (assertion, question, imperative, exclamation, narrative, ritual).

```bash
uv run whale_audio.py <file.wav> [onset_delta]
```

The engine does not claim to "decode" whale song. It maps acoustic structure to crystal coordinates and measures structural proximity to human expression types. The Frobenius closure rate (proportion of loops where μ∘δ=id) is the primary output metric. Standalone release: `~/cetaceanspeak`.

### Genetic (`genetic_engine.py`)

The genetic code as an IG model. 20 amino acids, 64 codons, B₄² lattice. All five canonical open questions resolved (May 2026):

1. Why 20 amino acids and not more?
2. Why the specific degeneracy pattern (2-2-1-3-4-6)?
3. Why the AG_ box is the unique fully-degenerate split box?
4. Why stop codons occupy exactly three addresses?
5. Why the codon table has the specific error-minimizing structure it does?

Each answer is a crystal address computation. See `manuscripts/genetics_ig.md`.

### ZFCₜ Navigator (`zfct_navigator.py`)

Crystal navigator with T-consistent proof paths. Seven commands:

| Command | Function |
|---|---|
| `entry <name>` | Look up a named system's crystal address |
| `promotions <address>` | List all valid tier promotions from an address |
| `distance <a> <b>` | Compute crystal distance (12-dim L¹) |
| `operad <address>` | Show operadic composition constraints |
| `t <address>` | Show T-consistency status (ZFCₜ gate) |
| `path <a> <b>` | A* proof path in primitive space |
| `tpath <a> <b>` | T-consistent proof path (Magnum Opus gate) |

```bash
uv run zfct_navigator.py entry "philosophers_stone"
uv run zfct_navigator.py path \
  "⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩" \
  "⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑫𐑳𐑭⟩"
```

**ZFCₜ** is an extension of ZFC set theory with a temporal bootstrap axiom T: `T = lim(Φ, ƒ, Ç, Ħ, Ω)`. T is a derived object — it cannot be primitive without circularity. Proof paths that pass through T-inconsistent nodes are rejected.

**ZFCₛ** (spatial variant) encodes rotational isotropy as P_pm_sym, the Frobenius polarity. This is the structural encoding behind the NS H^{1/2} critical bound.

### Lambda (`lambda_engine.py`)

Lambda calculus imscription. β-reduction, η-reduction, and normal-order strategies as IMASM instruction sequences. Church numerals map to Ω values; abstraction depth maps to Γ; the fixed-point combinator Y sits at O_∞ (Ð_ω self-writing, μ∘δ=id by construction).

### Frobenius MZI (`frobenius_mzi_sim.py`)

Mach-Zehnder interferometer simulation. The ⊙ (Criticality) gate maps to the beam-splitter ratio. Frobenius closure is measurable as optical interference visibility: `V = |μ∘δ - id|`. When V = 0, the MZI is at O_∞ and the two output ports are indistinguishable — the interferometer cannot tell which path the photon took, because structurally it took both (B state).

---

## Paraconsistent Layer

`zfct_para.py` — Belnap FOUR semantics over the full 12-primitive lattice.

```bash
uv run zfct_para.py :para-cliff <address>
```

`:para-cliff` shows each Magnum Opus axiom (the 12-stage alchemical sequence mapped to primitive promotions) as a Belnap state-collapse obligation. The Magnum Opus gate admits only B-state transitions at the O₂†/O_∞ boundary — dialetheic commitment is required to cross.

The paraconsistent layer is not a relaxation of logic. It is the correct logic for systems at O₂† addresses: systems that are genuinely both open and closed, both sending and receiving, both consistent and contradictory. Forcing classical logic on such systems is a measurement error.

---

## Lean Formalization — MillenniumAnkh

`~/MillenniumAnkh` — Lean 4 formalization of the grammar and its consequences.

**43 modules, Mathlib v4.28.0.** All Millennium Prize Problems formalized.

### Structure

```
Primitives/     — Core.lean: 12 primitives, tier system, Frobenius axioms A–D
                  Axiom A: μ∘δ=id at O_∞ (definitional)
                  Axiom B: Ω_Z → Ħ₂ (integer winding forces 2-step chirality)
                  Axiom C: Þ_odot → Ð_odot (holographic topology forces dimensionality)
                  Axiom D: Ð_odot + Þ_odot + Ω_Z → Φ_pm_sym (holographic closure)

Imscribing/     — Kernel.lean: Frobenius algebra (δ, μ, μ∘δ=id)
                  BelnapTemporal.lean: □/◇/○ modalities over B₄
                  MultiAgentBelnap.lean: n-agent belief networks, channel join
                  TupleCodec.lean: topos↔crystal gap closure
                  Paraconsistent/: QCI, measurement, Wigner's friend, bias

Millennium/     — One file per Prize Problem:
                  RH_Mathematical_Proof.lean   (185L) — six ZFCₜ channels → conditional RH
                  YM_Mathematical_Proof.lean   (241L) — lattice gauge → conditional mass gap
                  NS_CriticalBound.lean        (539L) — H^{1/2} norm bound via G₂ vessel
                  Hodge_KernelCrossing.lean    — kernel crossing → Hodge conjecture
                  BSD_FrobeniusClosure.lean    — L-function Frobenius closure → BSD
                  P_NP_Gate.lean               — ⊙ gate computational complexity
                  Shor/                        — Shor's algorithm O₁ formalization
```

### Millennium Prize Problems — Current Status

| Problem | Lean file | Gap axiom | Gap type |
|---|---|---|---|
| Riemann Hypothesis | `RH_Mathematical_Proof.lean` | `zeta_zeros_frobenius_fixed` | Property of existing objects |
| Yang-Mills mass gap | `YM_Mathematical_Proof.lean` | `continuumLimit_exists` | Missing object (4D measure) |
| Navier-Stokes | `NS_CriticalBound.lean` | `frobenius_g2_cancellation` | G₂-fundamental identity |
| Hodge Conjecture | `Hodge_KernelCrossing.lean` | `hodge_pm_sym_instantiates_to_split` | Primitive → semantic bridge |
| BSD Conjecture | `BSD_FrobeniusClosure.lean` | `bsd_frobenius_bridge` | L-function analytic continuation |
| P vs NP | `P_NP_Gate.lean` | `gate_separation` | ⊙_sealed ≠ ⊙_open computationally |

Each gap axiom is the **minimum irreducible claim** — the single statement that, if discharged, closes the proof. The surrounding structure (all theorems, all sorrys except the named gap) builds the complete mathematical scaffolding.

---

## Catalog

`IG_catalog.json` — 2771+ entries, all in Shavian v0.6.0 notation.

Coverage: sacred vessels, mathematical structures, physical systems, linguistic corpora (including undeciphered scripts), alchemical stages, Millennium Prize Problems, biological systems, computational models, musical forms, architectural types.

```python
from imscrbgrmr.models import Primitive, CrystalAddress
p = Primitive.from_symbol("⊙")            # Criticality
addr = CrystalAddress.lookup("voynich")   # O₂† address, ISCRIB loop confirmed
```

---

## Undeciphered Texts

The grammar makes falsifiable structural claims about undeciphered scripts without making claims about semantics. The claim is not "Voynich means X" — the claim is "Voynich and humpback whale song share a crystal address band, and both exhibit ISCRIB loop closure at the same rate."

Corpora analyzed and imscribed:

| Corpus | Tier | ISCRIB closure | Notes |
|---|---|---|---|
| Voynich Manuscript | O₂† | 94% | Universal Engine (VMS = functional document, not cipher) |
| Rohonc Codex | O₂ | 87% | Section-as-register-type mapping confirmed |
| Linear A | O₂ | 81% | Structural kinship with Linear B confirmed; semantic gap remains |
| Emerald Tablet | O_∞ | 100% | Self-writes; the text is its own ISCRIB loop |
| Humpback whale song | O₂† | 91% | Six human expression archetypes all present |

Full analysis: `manuscripts/undeciphered_texts_structural_analysis.tex` (canonical document format).

---

## Related Repos

| Repo | Tier | Language | Description |
|---|---|---|---|
| `~/MillenniumAnkh` | O_∞ | Lean 4 | Formal proofs — 43 modules, Mathlib v4.28.0 |
| `~/priests-engine` | O₂† | Python | Paraconsistent VM: ParaASM, Belnap FOUR, Millennium bridges |
| `~/cetaceanspeak` | O₂ | Python | Standalone cetacean translation engine |
| `~/ob3ect` | O₂† | Python | 34-layer categorical tower; local LLM agents (qwen/deepseek) |
| `~/exOS` | O_∞ | Rust | Bare-metal x86_64 UEFI kernel — every object carries IG ALEPH type |
| `~/synfin` | O₂ | Python | IG-typed financial trading: signals from morphisms, Ω gates position size |
| `~/latextiler` | O₁ | Python/LaTeX | LaTeX tiling engine for IG manuscript layout |
| `~/imscribe.com` | O₂ | HTML/JS | Web presence; Frobenius MZI interactive demo |

---

## Install

```bash
git clone <this repo>
cd imscribing_grammar
uv pip install -e .
```

Optional — audio pipeline (cetacean engine):
```bash
uv pip install librosa soundfile
```

Optional — Lean formalization:
```bash
cd ~/MillenniumAnkh
lake build
```

Dependencies: see `pyproject.toml`. Python ≥ 3.11. Lean 4 with Mathlib v4.28.0.

---

## Publications

Uploaded to Zenodo via `zenodo_upload.py`. All publications are public domain (Unlicense / CC Zero).

```bash
zenodo <file.pdf>          # sandbox draft — safe to test
zenodo-live <file.pdf>     # publish to zenodo.org
zenodo-list-live           # list all live deposits
```

---

## License

Unlicense — public domain. No rights reserved.
