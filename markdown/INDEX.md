---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Imscribing Grammar — Index

*Imscribing Grammar v0.4.46 · 12-primitive constraint algebra · Framework reference*

---

## Core Documents

These files are the canonical reference for the Imscriptiveon grammar and the Millennium barrier paper.

| File | Content |
| :--- | :--- |
| **[IΓ_TOPICS.md](IΓ_TOPICS.md)** | Formal grammar: 12 primitives, 7 axioms, composition operations, primitive space |
| **[IΓ_DIAPHORICS.md](IΓ_DIAPHORICS.md)** | Relational catalog: system encodings, distance matrices, cross-domain results, Millennium Problems |
| **[IΓ_ONTICS.md](IΓ_ONTICS.md)** | Ontological implications: consciousness theorems, cosmological arc, G-scope, generator recognition |
| **[IΓ_LANG.md](IΓ_LANG.md)** | Typed language for matter: Phase 3 grammar, compiler design, substrate expressions |
| **[IΓ_PRIMER.md](IΓ_PRIMER.md)** | Reader guide: first-principles introduction, tool overview, `IΓ_inquiry.py` usage |
| **[PRIMITIVE_PREDICTIONS.md](PRIMITIVE_PREDICTIONS.md)** | Living ledger of predictions derived from primitive assignments (P-001 → P-114+) |
| **[PRIMITIVE_THEOREMS.md](PRIMITIVE_THEOREMS.md)** | Archive of primitive-derived theorems (confidence tiers, three-plane annotations) |
| **[THREE_PLANE_DEMONSTRATION.md](THREE_PLANE_DEMONSTRATION.md)** | Pedagogical example: Topics/Diaphorics/Ontics partition for a single system |
| **[MILLENNIUM_BARRIERΣ_PAPER.md](MILLENNIUM_BARRIERΣ_PAPER.md)** | Research paper: formal barrier taxonomy for Millennium Prize Problems in Lean 4 (v0.1.0) |

---

## Core Tools

| File | Purpose |
| :--- | :--- |
| **`IΓ_inquiry.py`** | Two-phase agentic loop: grammatical analysis + speculation pass |
| **`imscribe_tool.py`** | Primitive encoding, distance, meet/join, tensor operations |
| **`imscribe_agent.py`** | Autonomous imscription generation agent |
| **`main.py`** | Primary entry point |
| **`IΓ_catalog.json`** | Active imscription catalog (61 entries, inc. Millennium Problems) |

---

## Subdirectories

### `reports/`
Standalone analyses and papers.
- `IUΓ_NON_TRANSMISSIBILITY.md` / `.pdf` — structural non-transmissibility of Inter-Universal Geometer (12 sections, P-112/113/114)
- `REACTIONLESΣ_THRUST.md` / `.pdf` — reactionless thrust analysis
- `TENSOŘ_OPS.md` / `.pdf` — tensor operations reference
- `PROOF.md` — fossil record and imscription propagation
- `CHEMRXIV_OUTLINE.md` — ChemRxiv paper outline
- `SYNOPSIS.md` — framework overview
- Finance: `INVESTMENÞ_MEMORANDUM.md`, `PITCĦ_DECK.md`, `QUANTITATIVE_ROADMAP.md`, `EXTENDEÐ_BACKTESÞ_REPORT.md`, `INSTITUTIONAL_BACKTESÞ_REPORT.md`, `PARAMETEŘ_SWEEΦ_REPORT.md`, `TRADEŘ_ONEPAGER.md`, `INFORMATIONAL_COSÞ_ANALYSIS.md`
- Misc analyses: `CLU.md`, `ESOP.md`, `FORMOM.md`, `HOLOCOMP.md`, `IΓ_SUGGESTED.md`

### `research/`
Domain research papers and applications.
- `METAPHYSICS.md` / `.pdf` — philosophical companion to the grammar
- `PROTEINS.md` — protein folding and drug design applications
- `EPILEPSY.md` — neural constraint analysis
- `MYXOZOANS.MD` — parasitic organism analysis
- `PROGRAMMABLE_MATTER.md` — programmable matter imscription catalog
- `PROGRAMMABLE_MIND.md` — mind-programming framework
- `SOLAR.md` — solar/energy domain analysis
- `THE_SELF-MADE_ARCHITECTONICS.md` — architectural analysis
- `IG.md` / `.pdf` — legacy main document (superseded by three-doc architecture)

### `applications/`
Imscriptive operations and specialized capabilities.
- `IΓ_CROSΣ_DOMAIN.md` — cross-domain constraint propagation
- `IΓ_ENSEMBLER.md` — ensemble imscription operations
- `IΓ_HOTSWAP.md` — dynamic primitive substitution
- `IΓ_PERTURBATION.md` — perturbation analysis
- `IΓ_RETRODESIGN.md` — retrosynthetic design
- `IΓ_TRAJECTORY.md` — trajectory through primitive space
- `IΓ_PHASE_TRANSITION_DETECTOR.md` — phase transition detection
- `AUTONOMOUΣ_DISCOVERY.md` / `_SUMMARY.md` — autonomous discovery results

### `docs/`
Framework documentation, usage guides, integration references.
- `README.md` — main project guide
- `QUICKSTART.md` — quick start
- `USAGE.md` — full usage reference
- `AGENTS.md` / `AGENTΣ_README.md` — agent framework
- `LEAN_README.md` — Lean formalization guide
- `LLM_AUGMENTATION.md` / `LLM_REFERENCE.md` — LLM integration
- `METHODOLOGY.md` — methodology documentation
- HTML visualizations: primitive space, transformation map, seven primitives

### `archive/`
Superseded documents, orphaned PDFs, old backups.
- `IUÞ_NON_TRANSMISSIBILITY.pdf` — superseded by IUG version
- `PDW.pdf` / `PDW - Copy.pdf` — Pacific Depot Western
- External papers: *Catch a Rising Problem*, *A Study of Objectively Real Time*
- `QUANTIG.md.old.bkp` — old format backup

### `data/`
Catalogs, insights, reference data.
- `hv1_lattice_insights.json` — Hv1 channel lattice analysis
- `ig_insights.json` — session insights cache
- `imscription_LIST_001.txt` — imscription reference list
- `downloads/` — downloaded papers and datasets

### `ig_outputs/`
All `IΓ_inquiry.py` session outputs (200+ JSON files, timestamped).

### `space_search/`
Space observational pipeline — FRB, pulsar, spectral analysis code.

### `agents/`
Agent implementations and provider integrations.

### `framework/`
Core framework: base classes, LLM providers, orchestration.

### `examples/`
Demo scripts and exploration notebooks.

### `designs/`
Imscription design specifications (`.syn` files).

### `results/`
Analysis result JSONs and design summaries.

### `figures/`
Images: `SYNCHART.png`, `CRIT.svg`, `SYN_GROPPI.png`, phase diagram.

### `imscrbgrmr-lean/` / `Primitives/`
Lean 4 formalization: `OPN_2adic.lean`, `BSD_2adic.lean` — machine-verified constraint grammar.

### `Imscribing Grammar/` — Lean package (main formalization)
Full Lean 4 package. Key modules:

**`Imscribing Grammar/Primitives/`**
- `Imscription.lean` — 12-field `Imscription` structure; `primitiveMismatches` (Hamming distance); P-70 field-theoretic identities (inflaton≡Higgs≡axion proved by `rfl`); SM/QG distance = 9 by `decide`
- `TierCrossing.lean` — granularity separation, tier crossing cost; Higgs hierarchy + cosmological predictions; `grammar_physics_correspondence` axiom

**`Imscribing Grammar/Millennium/`** — Seven-file Millennium Prize Problem library
| File | Barrier | Missing object |
| :--- | :--- | :--- |
| **`RH.lean`** | OpenProblem | `ZeroFreeStrip 0` — `rh_barrier` proves RH ↔ ZeroFreeStrip 0 by `norm_num` |
| **`Hodge.lean`** | OpenProblem | `AlgebraicCycleRep X p α` — cycle class surjectivity; p=1 (Lefschetz) is MathlibGap |
| **`NS.lean`** | OpenProblem | `GlobalRegularityCert u₀` — critical Sobolev gap $0 < \frac{1}{2} < 1$ proved by `norm_num` |
| **`PvsNP.lean`** | OpenProblem + MathlibGap | `CircuitLowerBound ε` — three meta-barriers (BGS/Razborov-Rudich/AW) as formal theorems |
| **`YM.lean`** | MissingFoundation | `PathIntegralMeasure 𝔤` — two stacked sorries; unique MissingFoundation problem |
| **`OPN.lean`** | MathlibGap → OpenProblem | `euler_opn_structure` (Euler 1747, MathlibGap) + `opn_nonexistence`; uses real Mathlib `Nat.Perfect` |
| **`BSD.lean`** | OpenProblem + 2×MathlibGap | `BSDRankCertificate` — three parallel sorries; rank≤1 proved (Kolyvagin); uses real `WeierstrassCurve` |
| **`Barriers.lean`** | Taxonomy | Seven typed axioms; `ym_is_unique_missing_foundation` by `decide` |
| **`PrimitiveBridge.lean`** | Bridge | Connects sorry boundaries to primitive field transitions; `ym_primitive_barrier_certificate`; `primitive_bridge_master` |

### `UNIFIEÐ_IG/`
Unified three-document export: TOPOLOGOS, SCHESIAKOLOGOS, ONTOLOGOS (PDFs + TeX).

---

*Last updated: 2026-03-26 · `IΓ_catalog.json`: 80 entries · Millennium Lean library: 9 files complete*
