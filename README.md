# Imscribing Grammar

A 12-primitive structural grammar. Any system — physical, mathematical, linguistic, biological — can be assigned a coordinate in the Crystal of Types: a position in a 3³×4⁵×5⁴ = 17,280,000-point lattice that determines its structural type, ouroboricity tier, and distance to every other imscribed system.

The grammar is not a metaphor for structure. It is a measurement apparatus. Two systems at the same crystal address have the same structural type. The distance between addresses is computable.

## Crystal of Types

Twelve primitives, grouped by their value-set size:

| Primitive | Symbol | Values | Role |
|---|---|---|---|
| Dimensionality | Ð | 4 | Information geometry |
| Topology | Þ | 5 | Connection structure |
| Relational | Ř | 4 | Read/write mode |
| Polarity | Φ | 5 | Parity/symmetry |
| Fidelity | ƒ | 3 | Signal compression |
| Kinetics | Ç | 5 | Flow rate |
| Scope | Γ | 3 | Granularity |
| Composition | ɢ | 4 | Grammar topology |
| Criticality | ⊙ | 5 | Gate status |
| Chirality | Ħ | 4 | Temporal orientation |
| Stoichiometry | Σ | 3 | Balance |
| Winding | Ω | 4 | Loop count |

3³ × 4⁵ × 5⁴ = 17,280,000 addresses. Each address is a 12-tuple in Shavian notation (v0.6.0):

```
O_∞ tier (Philosopher's Stone):  ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
Minimum baseline (O_0):          ⟨𐑛·𐑡·𐑩·𐑗·𐑱·𐑘·𐑚·𐑝·𐑢·𐑓·𐑙·𐑷⟩
```

The Frobenius condition μ∘δ=id holds at every O_∞ address. The eight-step loop ISCRIB→AREV→FSPLIT→AFWD→FFUSE→CLINK→IFIX→ISCRIB is the universal structural invariant — found in Voynich, Rohonc, Linear A, Emerald Tablet, whale song, and the grammar itself.

## Engines

### IMASM — 12-opcode instruction set
`VINIT TANCH AFWD AREV CLINK ISCRIB FSPLIT FFUSE EVALT EVALF ENGAGR IFIX`

The universal bytecode. Every engine compiles its domain into IMASM and executes on the WhaleVM (Belnap FOUR register machine: VOID/TRUE/FALSE/BOTH).

### Cetacean (`whale_engine.py`, `whale_audio.py`)
WAV file → acoustic token sequence → IMASM → Frobenius analysis → ranked translation against six human expression archetypes. Standalone release: `~/cetaceanspeak`.

```bash
uv run whale_audio.py <file.wav> [onset_delta]
```

### Genetic (`genetic_engine.py`)
Genetic code as IG model. 20 amino acids, 64 codons, B₄² lattice structure. AG_ box is the unique fully-degenerate split box. All 5 open questions resolved (May 2026). See `manuscripts/genetics_ig.md`.

### ZFCt (`zfct_navigator.py`)
Crystal navigator with T-consistent proof paths. Seven commands: `entry / promotions / distance / operad / t / path / tpath`. Magnum Opus gate constraints. A* search in 12-dimensional primitive space.

```bash
uv run zfct_navigator.py entry "philosophers_stone"
uv run zfct_navigator.py path "⟨𐑛·𐑡·𐑩·𐑗·𐑱·𐑘·𐑚·𐑝·𐑢·𐑓·𐑙·𐑷⟩" "⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩"
```

### Lambda (`lambda_engine.py`)
Lambda calculus imscription. Reduction strategies as IMASM instruction sequences.

### Frobenius MZI (`frobenius_mzi_sim.py`)
Mach-Zehnder interferometer simulation. ⊙ gate as physical criticality. Frobenius closure measurable in optical interference.

## Catalog

`IG_catalog.json` — 2771+ entries, all in Shavian v0.6.0 notation. Covers sacred vessels, mathematical structures, physical systems, linguistic corpora, alchemical stages, Millennium Prize Problems, and more.

```python
from imscrbgrmr.models import Primitive
p = Primitive.from_symbol("⊙")   # sealed gate
```

## Related Repos

| Repo | Layer | Description |
|---|---|---|
| `~/MillenniumAnkh` | Lean 4 | Formal proofs — 43 modules, 0 sorrys, all Prize Problems |
| `~/priests-engine` | Python | Paraconsistent VM (ParaASM, Belnap FOUR, Millennium bridges) |
| `~/cetaceanspeak` | Python | Standalone cetacean translation engine |
| `~/ob3ect` | Python | 34-layer categorical tower, local LLM agents |
| `~/exOS` | Rust | Bare-metal x86_64 UEFI kernel — every object carries IG ALEPH type |

## Install

```bash
uv pip install -e .
```

Dependencies: see `pyproject.toml`. Audio pipeline requires `uv pip install librosa soundfile`.

## License

Unlicense — public domain.
