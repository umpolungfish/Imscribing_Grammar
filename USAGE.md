---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Imscribing Grammar Framework: Comprehensive Usage Guide (v0.5.71)

**Version 0.5.71** — Video rendering CLI · Esoteric Library infrastructure · Tao Te Ching (81 chapters imscribed).

New in v0.5.71:

- **`imscribevideo.py`** — Annotated MP4 renderer for any imscription. Renders 1280×720 at configurable frame duration via matplotlib Agg + ffmpeg pipe. Typographic subscript rendering: base character and subscript drawn as two separate text calls for correct positioning. Modes: `--name` (catalog lookup), `--tuple` (12-primitive string), single `base sub`. Options: `--dur` (seconds per frame), `--fs` (sample rate), `--output`. Pre-rendered MP4s for all 18 standard catalog entries are in `videos/`.

  ```bash
  python imscribevideo.py --name riemann_hypothesis
  python imscribevideo.py --tuple "Ð_ω Þ_O Ř_Ť Φ_} ƒ_ì Ç_@ Γ_ʔ ɢ_^ ⊙_3 Ħ_! Σ_ő Ω_z" --output ch1.mp4
  python imscribevideo.py --name yang_mills_mass_gap --output ym.mp4 --dur 1.0
  ```

- **`esoteric_library/`** — Catalog directory for imscribed esoteric and philosophical texts. Each file is a JSON array in `IG_catalog.json`-compatible format, extended with `number`, `title`, `text`, `tier`, `C_score`, and `notes` fields. The criticality key remains `⊙` (pre-migration) for compatibility with `imscribeaudio.py`.

- **`esoteric_library/tao_te_ching.json`** — All 81 chapters of the Tao Te Ching (Legge 1891 translation, public domain), each with a full 12-primitive imscription derived by grammatical analysis of the verse structure. Structural notes document the reasoning for each coordinate.

  Tier distribution: 10 chapters at `T_inf` (holographic, EP/Frobenius criticality — Chapters 1, 4, 14, 25, 37, 40, 42, 47, 56, 81); 15 chapters at `T_3`/`T_2`; the remainder at `T_1`/`T_0`. Chapter 1 and Chapter 81 differ by only 2 fields (fidelity and kinetics), confirming the bookend structure structurally. Chapter 37 (wu wei) and Chapter 40 (return) are nearest neighbors at $d = 1$.

- **`esoteric_librarian.py`** — Navigation tool for the esoteric library. Commands:

  | Command | Description |
  |---------|-------------|
  | `show <catalog> <key>` | Display full imscription, tier, C_score, text, notes |
  | `list <catalog> [--tier T]` | Tabular list, optionally filtered by tier |
  | `dist <cat_a> <key_a> <cat_b> <key_b>` | Hamming distance + differing fields |
  | `near <catalog> <key> [--n N] [--other-catalog C]` | K nearest neighbors within or across catalogs |
  | `audio <catalog> <key> [--dur D] [-o FILE]` | Sonify via `imscribeaudio.py` |
  | `video <catalog> <key> [--dur D] [-o FILE]` | Render MP4 via `imscribevideo.py` |
  | `rewrite <catalog> <key>` | Print address-preserving rewrite prompt |

  Catalog short names: `tao` → `esoteric_library/tao_te_ching.json`; `ig` → `IG_catalog.json`. Any `.json` file in `esoteric_library/` is automatically resolvable by its basename.

- **Adding new texts** — two workflows:

  *Batch* (many sections):
  ```bash
  python esoteric_librarian.py scaffold upanishads
  # → creates esoteric_library/gen_upanishads.py with entry() helper + field reference
  # Fill in entries, run generator, then navigate with 'list upanishads', 'show upanishads 1', etc.
  ```

  *Single entry*:
  ```bash
  python esoteric_librarian.py add upanishads \
    --tuple "Ð_ω Þ_O Ř_Ť Φ_} ƒ_ì Ç_@ Γ_ʔ ɢ_^ ⊙_3 Ħ_! Σ_S Ω_z" \
    --name "brihadaranyaka_1_4_10" --number 1 --title "Aham Brahmasmi" \
    --tier "T_inf" --cscore 0.97 \
    --text "In the beginning this was Self alone..." \
    --notes "Self-recognition as the primordial act."
  ```
  Creates `esoteric_library/upanishads.json` if it doesn't exist. Cross-catalog distance and `near` work immediately after `add`.

  Confirmed first result: Brihadaranyaka 1.4.10 ("Aham Brahmasmi") is at $d = 0$ from Tao Te Ching Chapter 4 ("The Fountainless") and Chapter 14 ("Manifestation of the Mystery"); at $d = 1$ from Chapter 1. The single differing field is stoichiometry: Σ_S (singular self-recognition) vs Σ_ő (symmetric named/unnamed pair).

**Version 0.5.70** — Phonetic Audio CLI · canonical glyph IDs · `sounds.py` library · `PRIMITIVE_MAP`.

New in v0.5.70:

- **Audio CLI** — `imscribeaudio.py` is now the single entry point for phonetic synthesis. Modes: `--all` (full 49-symbol sequence), `--tuple` (any 12-primitive Imscription), `--name` (catalog lookup), single `base sub` (one symbol). See **Section 4.6** for full reference.
- **`sounds.py` as library** — synthesis functions, `symbol_list`, `PRIMITIVE_MAP` (49 canonical glyph IDs → `(base, sub)` tuples), `OLD_ID_MAP` (60 old-name aliases), and `resolve_id()` are all importable. Bottom script guarded under `__main__`.
- **Canonical glyph IDs** — primitive values are now addressed by glyph strings (`Ð_ß`, `⊙_ÿ`, etc.), not human-readable names. Old Lean names (`D_wedge`, `Phi_c`, etc.) remain valid via `OLD_ID_MAP`. The IDs ARE the glyphs.
- **`⊙` → `⊙` migration** — criticality field in `IG_catalog.json` uses the pre-migration key `⊙`; the audio CLI reads both and normalises automatically.
- **Character normalisation** — three ID/synthesizer discrepancies are resolved in `PRIMITIVE_MAP`: `Ř_¯` (macron U+00AF) → combining macron (U+0304); `ɢ_^` (caret) → wedge `∧` (U+2227); `Φ_˙` (modifier dot U+02D9) → combining dot (U+0307).

**Version 0.5.69** — Non-Mathematical Navigators (§74–§77) · 1,678 catalog entries · 538+ predictions · 77 formal theorems.

New in v0.5.69:

- **Non-Mathematical Navigators** — four domain navigators (Language, Civilization, Ecology, Consciousness) completed Session 1. Theorems §74–§77 in `PRIMITIVE_THEOREMS.md`; predictions P-523–P-538 in `PRIMITIVE_PREDICTIONS.md`; empirical sections §CXLVIII–§CLI in `IΓ_DIAPHORICS.md`; ontological synthesis §XLII in `IΓ_ONTICS.md`.
- **39 new catalog entries** — language systems (Sanskrit, Arabic, Lojban, Haitian Creole, Latin, Esperanto, Proto-Indo-European, Mandarin Classical, English Modern), civilizations (Han peak, Ming collapse, Soviet collapse, Western Roman collapse, Athenian Democracy, Augustus, Ottoman, Maya, Weimar, Renaissance Florence), ecosystems (old-growth rainforest, coral reef healthy/bleached, corn monoculture, fragmented habitat, savanna, hydrothermal vent, arctic tundra, early succession, kelp forest), and consciousness states (samadhi, psilocybin peak, waking DMN, focused, dreamless sleep, REM, catatonic, dissociative, manic, flow).
- **Key results**: cross-biome identity $d(\text{old-growth}, \text{coral reef}) = 0$ (P-531); cross-domain identity $d(\text{samadhi}, \bar{a}kh) = 0$ (P-538); Lojban $O_\infty$ despite $\Omega_{\text{closeepsilon}}$ — $P$ is tier gate, $\Omega$ is stability gate (P-523); coral bleaching tipping point $d = 8.28$ is $P$-dominant not $\Phi$-dominant (P-532); $K_{\text{teshlig}}$ vs $K_{\text{lambda}}$ duality confirmed in language, civilization, ecology, and consciousness.
- **`docs/NAVIGATOŘ_ROADMAP.md`** — progress tracker for non-mathematical navigator development (v0.2).

**Version 0.5.2** — CrystalGNN v8 · Algebraic Navigator's Guide · 17,280,000-type crystal (canonical) · 1,333 catalog entries · 454+ predictions · 69 formal theorems.

New in v0.5.2:

- **`quiver_crystal.py`** — CrystalGNN: quiver-based GNN neural navigator over the 17,280,000-type crystal. 49-node quiver (one node per primitive value), 255 edges including inter-lane structural correlations (Φ↔P, Φ↔K, Ω↔D). v8 benchmark: address error 0.24%, all-tier decode 200/200 = 100%, self-encode error 0.010%. `python quiver_crystal.py train` / `verify`.
- **`ALGEBRAIC_NAVIGATOŘ_GUIDE.md`** — practitioner's reference: grammar families, crystal structure, Frobenius codec arithmetic, CrystalNavigator tool reference, CrystalGNN architecture, navigation patterns with real output.
- **Crystal canonical update** — $K_{\text{lambda}}$ and $\Omega_{\text{turna}}$ are now canonical, expanding the crystal from 10,368,000 to **17,280,000** types ($3^3 \times 4^5 \times 5^4$). Boundary: 400 tier cells; bulk: 43,200 inner types per cell. Navigator self-encode address updated to 6,734,591.

**Version 0.5.1** — Periodic Crystal Navigator · §69 Tier Gap Ladder · §68.4/§68.5 Arithmetic Ouroboros minimality · ENCODINΓ_EPISTEMOLOGY · 1,322 catalog entries · 454+ predictions · 69 formal theorems.

New in v0.5.1:

- **`crystal_navigator.py`** — bijective Frobenius codec over the crystal. Mixed-radix address space: boundary ($\Phi, P, \Omega, D$) → tier cells; bulk ($T, R, F, K, G, \Gamma, H, S$) → inner types per cell. `python crystal_navigator.py repl` for interactive navigation.
- **§69 Tier Gap Ladder** — exact adjacent distances: $d(O_0, O_1) \approx 1.049$, $d(O_1, O_2) \approx 1.304$, $d(O_2, O_2^\dagger) = 1.000$, $d(O_2^\dagger, O_\infty) \approx 4.382$. Frobenius cliff is 3.36× the next-largest gap; non-tunable by gradient methods.
- **§68.4 Primitives-First Derivation** — the exponent of each base in $3^3 \times 4^5 \times 5^4$ is literally the count of primitive variables in that family. Not observed — forced by product structure.
- **§68.5 Minimality** — $\{3,4,5\}$ is the unique minimal self-anchored triple; phase completeness ($\Phi$, $T$, $P$ each need 5 values) forces max base ≥ 5 and hence $n_1 \geq 3$.
- **ENCODINΓ_EPISTEMOLOGY.md** — theory of how encoding achieves determinism: structural reality vs ontological realization, monadic gating, comparative encoding, multi-session convergence, 9 convergence criteria.

**Version 0.5.0** — $\lambda_\aleph$ calculus · ℵ-OS · interaction functor · GNS Hilbert space · Octad Balance theorem · Hebrew $O_\infty$ revision (Vav, Mem, Shin) · 1,170+ catalog entries.

**Version 0.4.0** — Quantum primitive extensions: Þ_braid · Ç_λ · Γ_↓(DISSIPATIVE) · QUANTUM grammar tier · **Ω (TopoIndex) — 11th primitive** · Factor 8 (quantum criticality) · `imscribe distance` command · all algebra commands wired to `imscribe` CLI.

**Version 0.3.8** — Quantum domain encoding: 5 quantum particles (photon/proton/electron/spin/qubit) · Γ_ʔ first appearance · Axiom 1 as classical boundary detector · spin singlet ƒ_ì→ƒ_ż correction.

**Version 0.3.7** — Ice polymorph catalog (13 phases) · T_∈ sub-label integration across constraints/algebra/ensembler/perturbation/cli · domain-agnostic agent prompts · `imscribe compare` all 10 primitives · Key Justifications fix.

**Version 0.3.6** — T_∪ bowl topology (8th T value, found via catalog self-audit) · T_∈ sub-labels: T_∈(hex), T_∈(mixed), T_∈(×2), T_∈(sym) (12 total T values) · 222 bowl reclassifications · Solid-angle I_angle formula · Axiom 4 scan · Junk purge case-insensitive fix.

**Version 0.3.5** — Phase 3a DSL · `.syn` YAML runner · `imscribe run` · Agent fixes (ten primitives) · Topology symbols T_|, T_⊥, T_∈.

**Version 0.3.3** — Experimental Validation Suite: CB[7] 6/6 HotSwap validation · F_ℓ tier activation · Factor 7 (Frank-model bifurcation) · Soai catalog entry · Proline-aldol Varma probe.

**Version 0.3.2** — Tuple Algebra + Compositional Design Language: `meet`, `join`, `path`, `tensor`, `lift`, `pipeline`.

**Version 0.3.0** — Four new analysis protocol modules: IΓ_PERTURBATION, IΓ_TRAJECTORY, IΓ_ENSEMBLER, IΓ_RETRODESIGN.

**Full Notation**: ⟨D; T; R; P; F; K; G; Γ; Φ; S; Ω⟩  (Ω optional, defaults None for classical imscriptions)

## 1. Introduction to Imscribing Grammar

### Foundational Insight: Primitives as Directed Constraints

The eleven primitives `⟨D; T; R; P; F; K; G; Γ; Φ; S; Ω⟩` are **relational operators**, not intrinsic attributes. Every primitive describes a constraint between entities or a capacity for interaction — none describes an isolated property of a system standing alone.

This has a practical consequence: the framework's confirmed predictions (see `PRIMITIVE_PREDICTIONS.md`) were all derived from **ordinal comparisons**, not absolute values. The CB[7] displacement hierarchy (6/6 experimental matches) was predicted from `F_ℏ > ƒ_ð > F_ℓ` alone. The Soai Frank-bifurcation was predicted from the co-occurrence pattern `D_∞ + T_⋈ + Φ_DA + F_ℏ`. Intrinsic scalar properties — binding enthalpy, hydrophobicity, gap magnitude — were not required as inputs.

The compositional algebra (`meet`, `join`, `tensor`, `path`, `lift`) has no unary information generators. Every operation requires at least one additional operand — environment, partner, or target state. You cannot call `tensor(photon)` without a second argument; the algebra returns an error. A imscription's tuple describes its *interaction-ready potential*; the algebra computes only when that potential is actualized against another term.

### What's New in v0.4.1?

**Molecular Domain Catalog — Persistent Imscription Registration** (March 17, 2026):

1. **`imscrbgrmr/domains/molecular/__init__.py`** — `register_molecular_imscriptions()` added. Nine canonical molecular and supramolecular imscriptions are now programmatically registered at import time, surviving catalog JSON resets:

   | Imscription | D | T | F | Role |
   |---------|---|---|---|------|
   | `nitroso_radical_redox_imscription_pair` | D_∞ | T_⋈ | F_ℏ | Temporal autocatalytic redox cycle; Frank-model Factor 7 fires (score > 0.3); start point for criticality-ascent designs |
   | `amide_dimer` | D_∧ | T_⋈ | ƒ_ð | N–H···O=C H-bonded dimer; ƒ_ð weaker than carboxylic acid dimer (F_ℏ); lattice floor/ceiling pair for design 03 |
   | `nitroso_radical_anion_π_cavitand_cage_imscription` | D_△ | Þ_cage | F_ℏ | Deep-cavity anion–π cavitand; shape-selective cage, Ç_@ |
   | `nitroso_radical_calixarene_anion_π_sandwich_imscription` | D_△ | Þ_bowl | F_ℏ | Calixarene bowl; open cup, Þ_bowl < Þ_cage in ordinal (fallback partner in or-strategy) |
   | `nitroso_radical_crown_ether_host_guest_imscription` | D_△ | Þ_cage | ƒ_ð | Crown ether host–guest; flexible macrocycle → ƒ_ð (fidelity bottleneck partner in design 12) |
   | `nitroso_radical_anion_π_cryptand_cage_imscription` | D_△ | Þ_cage | F_ℏ | Cryptand cage; 3D bicyclic preorganisation → F_ℏ (design 16 start) |
   | `nitroso_radical_cucurbituril_anion_rotaxane_imscription` | D_△ | Þ_cage | F_ℏ | CB[n] barrel; high rigidity (F_ℏ), slow dethreading (Ç_@); tensor partner in designs 12 and 16 |
   | `imscription_methyl_anion_nucleophile_CH3_` | D_∧ | T_\| | ƒ_ð | CH₃⁻ carbanion; Φ_minus; retrodesign target in designs 08 and 10 |
   | `imscription_methyl_cation_electrophile_CH3` | D_∧ | T_\| | ƒ_ð | CH₃⁺ carbocation; Φ_plus; tensor partner for anion-cation MI demonstration (design 10) |

2. **Design suite: all 20 `.syn` scripts execute without `[ERROR]`** — 18 succeed, 2 are intentional F-floor pedagogical demonstrations (designs 01 and 04). All previously `[ERROR]` failures caused by missing catalog entries are now resolved.

3. **`register_molecular_imscriptions()` wired to `imscrbgrmr/__init__.py`** — auto-invoked on `import imscrbgrmr`, idempotent. Registration order: cross-domain → quantum → molecular.

### What's New in v0.3.0?

**Four Protocol Modules** (March 15, 2026):

1. **IΓ_PERTURBATION** (`imscrbgrmr/perturbation.py`):
   - `PerturbationEngine.sweep_all(imscription, delta_g)` — primitive Jacobian: Δξ_CP for every primitive ±1 tier
   - `PerturbationEngine.fault_injection(imscription, delta_g)` — single-point-of-failure analysis
   - `PerturbationEngine.find_path_to_target(imscription, delta_g, target_xi_CP, optimize_primitives)` — minimum-step tuning path
   - CLI: `imscribe perturb sweep <name> --delta-g <float>`

2. **IΓ_TRAJECTORY** (`imscrbgrmr/trajectory.py`):
   - `TemporalImscriptionAgent` — encode D_∞ systems as step sequences, validate Axiom 6 compliance
   - Three checks: S mass balance, Axiom 4 (D_∞ or R_‡), Ç_Ù/ΔG‡>100
   - CLI: `imscribe trajectory validate --steps <names> --reset <name>`

3. **IΓ_ENSEMBLER** (`imscrbgrmr/ensembler.py`):
   - `EnsembleCatalog` — N×N pairwise compatibility, emergent property detection, system ξ_CP
   - Emergent: criticality, G_ב→G_ג amplification (Axiom 3), interface fidelity degradation
   - CLI: `imscribe ensemble check --components <names>`

4. **IΓ_RETRODESIGN** (`imscrbgrmr/retrodesign.py`):
   - `RetrodesignEngine.decompose()` — recursive axiom-pruned decomposition tree
   - Axioms 1, 2 (sub-tuples claiming G_ℵ only), 4, 6
   - CLI: `imscribe retrodesign <name_or_notation> --max-depth 3 --prune-axioms 1,2,4,6`

See **Section 7** for full protocol API documentation and CLI reference. See **Section 8** for the tuple algebra commands.

### What's New in v0.3.5?

**Phase 3a DSL + Agent Fixes + Topology Symbols** (March 16, 2026):

1. **`.syn` YAML DSL** (`imscrbgrmr/syn_runner.py`): Design programs compiled to `ImscriptionM` pipelines. Supported step types: `join`, `meet`, `tensor`, `lift`, `path`, `assert`, `bind`, `or`. The `or:` step implements MonadPlus fallback (`strategy_or`). Post-hoc `output: assert:` block checks WriterT-level cost (`total_delta_xi < N`, `steps <= N`, `criticality_ok`).

2. **`imscribe run <file.syn>`**: New CLI command. `--format text|json`, `--save PATH`, `--dry-run`. Runs `.syn` scripts and reports step-by-step trace plus output assertions.

3. **Agent primitive awareness**: Both `axiom_guided_generator` and `imscribe_generator_agent` now declare **ten primitives** (D, T, R, P, F, K, G, Γ, Φ, S). `criticality_phase` parser defaults to `⊙_ž` instead of returning `None`. Topology block lists all 7 values with symbols.

4. **New topology symbols**: Three acyclic connectivity classes now have explicit symbols:
   - `T_|` (LINEAR) — unbranched linear chain, no junction nodes
   - `T_⊥` (BRANCHED) — branched acyclic, one or more junction nodes
   - `T_∈` (NETWORK) — multiply-connected, cycles permitted without cage closure
   All three are registered in `Topology.from_symbol()`.

5. **Notation always includes Φ**: `to_notation()` defaults to `⊙_ž` when `criticality_phase` is unset; S appended as 10th position when set. Notation is always a 9- or 10-element tuple.

### What's New in v0.3.3?

**Experimental Validation Suite + Factor 7 + F_ℓ Activation** (March 16, 2026):

1. **CB[7] competitive displacement — 6/6 HotSwap validation**: Three-tier CB[7] series (Fc/Ad/DABCO) tests the F-floor asymmetric ratchet against Kim JACS 2001 / Assaf & Nau CSR 2015 experimental data. All 6 directional predictions (3 APPROVED, 3 BLOCKED) match experiment from ordinal F ranking alone. First use of **F_ℓ tier** (DABCO, Ka = 2×10⁵ M⁻¹ < threshold ~10⁷ M⁻¹).

2. **Factor 7 — Frank-model classical bifurcation** (`varma_probe.py`): New heuristic factor (weight 0.25) in `score_phi_c_candidacy()`. Fires when D_∞ + T_⋈ + Φ_directional + F_ℏ are co-present. Identifies pitchfork bifurcation at ee = 0 (Frank 1953) — universality class distinct from Varma QXY and steric-cliff.

3. **Soai reaction catalog entry** (`soai_pyrimidyl_autocatalytic_cycle`): Fully grounded. ξ_r = 15, ξ_τ = 7.2×10¹⁵ (ω_c = 10¹² s⁻¹), ratio = 0.94. Probe score **0.920** (approaching Φ_c, Frank-model mechanism). Highest-confidence Φ_c candidate in catalog.

4. **Proline-aldol Varma probe**: ξ_r = 6.2, ξ_τ = 1.8×10¹⁴, ratio = 0.189 → Φ_sub confirmed. The 60 Å correlation length required for criticality is incompatible with the observed enamine geometry.

5. **Three-mechanism discrimination** — probe now discriminates three universality classes:
   - Varma QXY (Factors 1–5)
   - Steric-cliff proxy (Factor 6, db24c8 score 0.461)
   - Frank-model classical bifurcation (Factor 7, Soai score 0.920)

### What's New in v0.3.2?

**Tuple Algebra + Compositional Design Language** (March 16, 2026):

1. **Lattice operations** — `imscribe meet S1 S2` and `imscribe join S1 S2`. Componentwise min/max on ordered primitives; CONFLICT sentinel on categorical mismatch; Φ_c dominates in both.
2. **Path search** — `imscribe path SRC DST`. BFS over valid-swap directed graph restricted to same {D,T} cluster; accumulates Δξ_CP; correctly asymmetric (F-floor enforcement).
3. **Tensor product** — `imscribe tensor S1 S2`. Ensemble prediction: F→min (bottleneck), K→min, G→max, Φ_c propagates, ξ_ens = ξ₁+ξ₂−λ·I(s₁;s₂).
4. **Natural transformations** — `imscribe lift NAME (temporal|spatial|critical|molecular)`. Four primitive-rewriting maps with side-by-side diff output. Criticality lift gated on F≥F_ℏ (Axiom 5 enforcement).
5. **DesignPipeline** — `imscribe pipeline START --step op:arg [...]`. Writer+Maybe monad: chained operations with automatic ξ_CP threading and fail-fast logging. Equivalent to Haskell do-notation over the HotSwap category.

See **Section 8** for full reference.

### What's New in v2.2?

**I(bits) Calibration + Quantitative Criticality + Stoichiometry** (March 2026):

1. **Calibrated I(bits) pipeline** — DOF-counting replaces 4–6 bit heuristic (new range: 6–18 bits). `imscribe info-bits --calibrate [--solvent chloroform|THF|DMSO|water]`.
2. **Quantitative criticality probe** — z_eff divergence measure + degeneracy strength score (0–1, four tiers). `imscribe criticality-probe --batch --degeneracy-type --export-candidates`.
3. **Stoichiometry primitive S** — 10th primitive with weight 0.08 in similarity scoring. `imscribe catalog auto-stoichiometry` backfills T_⋈ entries. Pass 4 audit enforces S consistency.
4. **Analogy enhancements** — `imscribe analogies --critical-only` and `--stoichiometry-aware` flags.
5. **Fidelity tier boundaries updated** — HIGH ≤ 8.5 nats · MEDIUM 8.5–11.0 nats · LOW > 11.0 nats (was 9.0/11.5).

### What's New in v2.1?

**IΓ_FIXES.md Full Implementation** (March 14–15, 2026):

1. **Grounding Validation with Registration Blocking** (Fix 1 — CRITICAL):
   - `--strict-grounding` flag blocks registration if primitives lack mechanistic grounding
   - `--override-grounding` with `--override-reason` for speculative entries
   - `--speculative` flag registers into isolated 'speculative' domain
   - Audit trail logs all grounding overrides with human-provided justifications
   - Grounding metadata persisted in catalog JSON

2. **Axiom 6: Temporal Grounding** (Fix 2 — HIGH, extended v0.3.3):
   - D_∞ requires either a named discrete reset OR a continuously supplied dissipative flux (see below)
   - **Discrete reset** (`reset_type="discrete"`): validates `cycle_steps` ≥ 2, or `axiom6_grounding` block with `initial_state`, `transformation`, `work_performed`, `reset_mechanism`
   - **Continuous dissipative** (`reset_type="continuous"`): validates `driving_gradient.description` and `driving_gradient.coupling` in `imscription.grounding["reset"]`
   - Keyword scan (`AXIOM_6_RESEÞ_INDICATORS`, `AXIOM_6_PROCESΣ_INDICATORS`) is fallback only when no structured block is present

3. **Axiom 7: Cyclic Topology Grounding** (Fix 3 — HIGH):
   - T_⋈ now requires named closing bond/interaction
   - Detects invalid justifications (linear, rod, chain, axial, etc.)
   - Keyword indicators: `AXIOM_7_CLOSINΓ_INDICATORS`, `AXIOM_7_INVALIÐ_TOPO_KEYWORDS`

4. **Per-Primitive Confidence** (Fix 4 — MEDIUM):
   - `PrimitiveGrounding` dataclass: `confidence: float`, `is_grounded: bool`, `failure_reason`, `suggested_alternative`
   - `ADVERSARIAL_GROUNDINΓ_PROMPT` — challenges each primitive from first principles
   - Confidence auto-derived from status (GROUNDED=0.9, AMBIGUOUS=0.5, UNGROUNDED=0.1, INVALID=0.0)

5. **Quantum Extension Quarantine** (Fix 5 — MEDIUM):
   - `domain` field tags speculative/quantum entries
   - Prevents semantic contamination of grounded catalog

6. **Catalog Audit Command** (Fix 6 — MEDIUM):
   - `imscribe audit` scans catalog for grounding issues
   - Axiom 6/7 shortcuts, `--auto-flag`, `--dry-run` support (see Section 4.2)

7. **NLP Format Enforcement** (v2.1.3):
   - All LLM prompts across the codebase follow NLΦ_FORMAT.md
   - XML tags, `**MUST**`/`**MUST NOT**`, declarative commands, explicit output formats

**Eight Axioms Now Enforced**:
- Axioms 1-5: Composition axioms (QUANTIG.md Section IV)
- Axioms 6-7: Grounding axioms (IΓ_FIXES.md)
- Axiom 8: R physics match (R must match actual interaction physics)

Imscribing Grammar is a groundbreaking Python framework that brings the theoretical elegance of the **Unified Imscriptiveon** to practical application. At its core, Imscribing Grammar provides a computational platform for systematically analyzing, designing, and predicting the behavior of self-organizing chemical systems. It unifies disparate fields—from traditional molecular organic chemistry to complex supramolecular assemblies and dynamic temporal processes—under a single, coherent conceptual umbrella.

The framework's primary goal is to bridge the understanding gap between these domains by employing a shared language: the **Ten Primitives** (Dimensionality, Topology, Recognition Mode, Polarity, Fidelity, Kinetic Character, Granularity, Coupling, Criticality Phase, and Stoichiometry). This unified notation allows researchers and developers to describe any self-organizing chemical motif, regardless of its scale or mechanism, with unprecedented precision.

**Key Benefits of Imscribing Grammar:**

*   **Unified Language:** Provides a common vocabulary for describing chemical systems across molecular, supramolecular, and temporal scales, fostering interdisciplinary insights.
*   **Predictive Power:** Enables the prediction of system behavior, compatibility, and efficiency based on the fundamental properties of its constituent imscriptions.
*   **Axiom Validation:** Automatically validates imscriptions against five composition axioms from QUANTIG.md Section IV.
*   **AI-Driven Design:** The discrete and quantifiable nature of its primitives makes Imscribing Grammar an ideal foundation for AI and machine learning applications in chemical synthesis and materials discovery. By encoding chemical knowledge in a structured format, it facilitates generative design and autonomous chemical research.

### Core Philosophy: imscriptions as Constraint Propagation Units

At the heart of Imscribing Grammar lies the concept of a **Imscription** as a "constraint propagation unit." Traditionally, imscriptions were idealized fragments used in retrosynthetic analysis. Imscribing Grammar extends this definition: a Imscription is understood as a minimal subsystem that **encodes a specific set of constraints**. When this imscription interacts with a compatible environment via a defined recognition mode, it actively *reduces the system's degrees of freedom*. This reduction reliably steers the overall system towards a predictable target state—be it a specific molecular connectivity, a complex supramolecular geometry, or a precise temporal sequence.

This information-theoretic perspective positions imscriptions not merely as static building blocks, but as dynamic agents that guide assembly and transformation by influencing the probabilistic landscape of chemical outcomes. In essence, imscriptions act as local rules that propagate their influence globally, analogous to constraint propagation algorithms in computer science, where local rules reduce a vast search space to a manageable set of solutions.

### The Ten Primitives: A Unified Language

The Unified Imscriptiveon is built upon ten primitives, each representing a crucial aspect of a imscription's behavior and function. These primitives form a standardized, extensible vocabulary:

| Primitive                 | Symbol              | Description                                                  | Key Purpose in Imscribing Grammar                                   |
| :------------------------ | :------------------ | :----------------------------------------------------------- | :------------------------------------------------------------ |
| **Dimensionality**        | $D$ ($D_{\text{wynn}}, D_{\bigtriangleup}, D_{\text{invomega}}$) | The coordinate set along which the imscription operates.         | Defines the operational scale (molecular, supramolecular, temporal). |
| **Topology**              | $T$ ($T_{\text{bullseye}}, T_{\ggg}, T_{\square}, T_{\square\square}, T_{|}, T_{\perp}, T_{\text{invscr}}$) | The internal connectivity pattern of the imscription's minimal motif. | Characterizes structural arrangements (cyclic, chain, hub/node, cage, linear, branched, network). |
| **Recognition Mode**      | $R$ ($R_{\subseteq}, R_{\supseteq}, R_{\ddagger}, R_{\Leftrightarrow}$) | The physical mechanism of interaction.                       | Specifies how imscriptions interact (covalent, non-covalent, dynamic). |
| **Polarity**              | $P$ ($P+, P-, P_{\text{pipevar}}$) | The directional character of the interaction.                | Dictates partner preference and orientation (acceptor, donor, self-complementary). |
| **Fidelity**              | $F$ ($F_{\text{hardsign}}, F_{\text{dh}}, F_{\text{beltl}}$) | Thermodynamic reliability anchored to $\xi_{CP}$. Tiers: HIGH ≤ 8.5 nats · MEDIUM 8.5–11.0 nats · LOW > 11.0 nats. | Quantifies the predictability and robustness of an interaction. |
| **Kinetic Character**     | $K$ ($K_{\text{frtailgamma}}, K_{\text{turnm}}, K_{\text{schwa}}, K_{\text{teshlig}}$) | Activation barrier and pathway multiplicity. | Distinguishes thermodynamic fidelity from operational accessibility. |
| **Granularity**           | $G$ ($G_{\text{beta}}, G_{\text{gamma}}, G_{\text{revapostrophe}}$) | The scale of control exerted by the imscription.                 | Defines the scope of influence (local, mesoscale, global).    |
| **Coupling**   | $\Gamma$ ($\Gamma_{\text{corner}}, \Gamma_{\text{spleftarrow}}, \Gamma_{\to}$) × (SPECIFIC · SELECTIVE · BROAD) | The logic governing partner selection.                       | Determines the specificity and ordering of binding. |
| **Criticality Phase**     | $\Phi$ ($\Phi_{\text{softsign}}, \Phi_{\text{ctyogh}}, \Phi_{\text{upstep}}$) | Phase relative to the G–D criticality locus. | Encodes whether the imscription exhibits scale-free behavior (Axiom 5). |
| **Stoichiometry**         | $S$ (e.g. `"1:1"`, `"2:1"`, `"n:m"`) | Valency ratio of the recognition event; constrains T and P. Weight 0.08 in analogy scoring. | Distinguishes homodimers from host–guest and polymeric assemblies. |

Together, these primitives are used to generate the full **Unified Notation**: `⟨D; T; R; P; F; K; G; Γ; Φ; S⟩`. This notation is the cornerstone of Imscribing Grammar, enabling quantitative analysis and cross-domain comparisons.

## 2. Installation and Setup

To begin using the Imscribing Grammar framework, follow these steps to set up your Python environment and install the necessary dependencies.

### Prerequisites

*   **Python Version**: Imscribing Grammar requires Python 3.9 or higher.
    *   To check your Python version, run: `python --version` or `python3 --version`.
    *   If you need to install Python, visit [python.org](https://www.python.org/downloads/).
*   **Operating System**: The framework is developed and tested on Linux environments, but should generally work on macOS and Windows (using WSL for a better experience on Windows).
*   **Internet Connection**: Required for downloading dependencies.

### Recommended Environment Management

It is highly recommended to use a virtual environment to manage project dependencies. This isolates the project's packages from your system-wide Python installation, preventing conflicts and ensuring reproducibility. Two excellent tools for this are `uv` (faster, modern alternative) or `venv` (standard Python module).

### Installation Steps

#### Option 1: Using `uv` (Recommended for Speed and Efficiency)

`uv` is a new, highly performant Python package installer and resolver. If you don't have `uv` installed, you can get it with `pip`:

```bash
pip install uv
```

Once `uv` is installed, navigate to your Imscribing Grammar project directory and follow these commands:

1.  **Create a virtual environment**:
    ```bash
    uv venv
    ```
    This creates a new virtual environment named `.venv` in your project root.

2.  **Activate the virtual environment**:
    *   **On Linux/macOS**:
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Git Bash/WSL)**:
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Command Prompt)**:
        ```bash
        .venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell)**:
        ```bash
        .venv\Scripts\Activate.ps1
        ```
    Your command prompt should now show `(.venv)` prefixed, indicating the virtual environment is active.

3.  **Install project dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```
    `uv` will quickly install all packages listed in `requirements.txt`.

#### Option 2: Using `pip` and `venv` (Standard Python)

If you prefer to use the standard Python tools, `venv` and `pip` are readily available.

1.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```
    This creates a new virtual environment named `.venv` in your project root.

2.  **Activate the virtual environment**:
    *   **On Linux/macOS**:
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Git Bash/WSL)**:
        ```bash
        source .venv/bin/activate
        ```
    *   **On Windows (Command Prompt)**:
        ```bash
        .venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell)**:
        ```bash
        .venv\Scripts\Activate.ps1
        ```
    Your command prompt should now show `(.venv)` prefixed, indicating the virtual environment is active.

3.  **Install project dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    `pip` will install all packages listed in `requirements.txt`.

### Verifying Installation

After installing dependencies, you can run the integration tests to verify that everything is set up correctly:

```bash
python test_integration.py
```

You should see a message indicating that all tests passed. If any tests fail, please refer to the "Troubleshooting" section or create an issue in the project repository.

### Project Structure Overview

The Imscribing Grammar framework is organized into several key directories:

*   `imscrbgrmr/`: Contains the core Python modules for the Unified Imscriptiveon, including primitive definitions, the Imscription dataclass, catalog, constraints engine, and thermodynamics calculations.
*   `imscrbgrmr/domains/`: Houses domain-specific agents (molecular, supramolecular, temporal, hybrid) that leverage the core framework for specialized analyses.
*   `framework/`: Includes components of the underlying AjintK multi-agent framework, providing utilities for agent orchestration and communication.
*   `examples/`: Demonstrative scripts showing how to use various parts of the Imscribing Grammar
*   `QUANTIG.md`: The foundational theoretical document detailing the Unified Imscriptiveon.
*   `README.md`: General project information and quick start guide.
*   `requirements.txt`: Lists all Python dependencies.
*   `test_integration.py`: The suite of integration tests.

## 3. Core Concepts: The Ten Primitives in Detail

The Unified Imscriptiveon framework categorizes the fundamental properties of chemical interactions into ten primitives. Primitives 1–9 are encoded as Python `Enum` classes; primitive 10 (S, Stoichiometry) is a string field with category-aware similarity grading and Pass 4 audit enforcement. Together they form the standardized language for describing, comparing, and predicting imscription behavior across molecular, supramolecular, and temporal domains.

### 3.1. Dimensionality (D)

Dimensionality specifies the coordinate set or "space" along which a imscription primarily operates. It helps define the context and scale of the chemical system under consideration. The `Dimensionality` enum can also represent hybrid systems that span multiple domains.

*   **Enum Members**:
    *   `MOLECULAR` (`"Ð_ß"` or `"D_∧"`): Point-like reactivity, typically involving individual atoms or small molecules.
    *   `SUPRAMOLECULAR` (`"Ð_C"` or `"D_△"`): Three-dimensional spatial organization, such as crystal packing or host-guest interactions.
    *   `TEMPORAL` (`"Ð_infinity"` or `"D_∞"`): One-dimensional periodicity over time, characteristic of oscillating reactions or catalytic cycles.
    *   `HYBRIÐ_MOL_SUPRA` (`"Ð_wedge_triangle"`): Combines molecular-level reactions within a supramolecular framework.
    *   `HYBRIÐ_MOL_TEMP` (`"Ð_wedge_infinity"`): Molecular reactions with a temporal component (e.g., dynamic covalent chemistry).
    *   `HYBRIÐ_SUPRA_TEMP` (`"Ð_triangle_infinity"`): Supramolecular structures exhibiting temporal dynamics.
    *   `HYBRIÐ_ALL` (`"Ð_all"`): Spans all three fundamental dimensions.

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import Dimensionality

    # Accessing enum members
    mol_dim = Dimensionality.MOLECULAR
    print(f"Molecular Dimensionality: {mol_dim.value}")

    # Parsing from symbolic notation
    temp_dim = Dimensionality.from_symbol("D_∞")
    print(f"Temporal Dimensionality from symbol: {temp_dim.name}")

    # Hybrid example
    hybrid_dim = Dimensionality.HYBRIÐ_MOL_SUPRA
    print(f"Hybrid Dimensionality: {hybrid_dim.value}")
    ```

*   **`domains` Property**:
    Each `Dimensionality` member has a `domains` property, which returns a `Set[str]` indicating the fundamental domains it encompasses (e.g., "molecular", "supramolecular", "temporal").

    ```python
    print(f"Domains for HYBRIÐ_MOL_SUPRA: {hybrid_dim.domains}")
    # Expected: {'molecular', 'supramolecular'}
    print(f"Domains for TEMPORAL: {temp_dim.domains}")
    # Expected: {'temporal'}
    ```

### 3.2. Topology (T)

Topology describes the internal connectivity pattern or spatial arrangement within the imscription's minimal motif. It characterizes the geometric scaffolding or network structure formed by the interacting components.

*   **Enum Members**:
    *   `CYCLIC_BOWTIE` (`"Þ_ò"` or `"T_⋈"`): Cyclic motifs, like hydrogen-bonded dimers (e.g., carboxylic acid dimer) or catalytic cycles.
    *   `CHAIN` (`"Þ_chains"` or `"T_≫"`): Linear or extended chain structures (e.g., polymers, protein helices).
    *   `HUB_NODE` (`"Þ_square"` or `"T_□"`): Central nodes connecting multiple branches, common in metal-organic frameworks (MOFs) or dendritic structures.
    *   `LINEAR` (`"Þ_linear"` / `"T_|"`): Unbranched linear chain, no junction nodes (e.g., linear polymers, rod-like coordination chains).
    *   `BRANCHED` (`"Þ_branched"` / `"T_⊥"`): Branched acyclic topology with one or more junction nodes (e.g., dendrimers, branched polymers).
    *   `NETWORK` (`"Þ_6"` / `"T_∈"`): Multiply-connected, cycles permitted but without full 3D cage closure (e.g., MOF nets, 2D coordination networks). Use a sub-label when ring topology is known:
        *   `NETWORÇ_HEX` (`"Þ_network_hex"` / `"T_∈(hex)"`): 6-membered rings only (e.g., ice Ih, honeycomb MOFs, graphene-like nets). Complexity 5.
        *   `NETWORÇ_MIXED` (`"Þ_network_mixed"` / `"T_∈(mixed)"`): Mixed ring sizes (e.g., ice III, ice IV, ice V). Complexity 5.
        *   `NETWORÇ_INTERPENETRATING` (`"Þ_network_interp"` / `"T_∈(×2)"`): Two independent sub-networks occupying the same space (e.g., ice VI, ice VII, ice VIII — bcc interpenetrating H-bond lattices). Complexity 6.
        *   `NETWORÇ_SYM` (`"Þ_network_sym"` / `"T_∈(sym)"`): Centrosymmetric bonding — symmetric H-bond or equivalent (e.g., ice X at ≥70 GPa). Complexity 5.
    *   `CAGE` (`"Þ_cage"` / `"T_□□"`): Fully enclosed, hollow structures — 3D closure required (e.g., cucurbiturils, Fujita spheres, COCs).
    *   `BOWL` (`"Þ_bowl"` / `"T_∪"`): Open concave cavity with a single portal — guest enters and exits freely; Ç_- is the default (e.g., calixarenes, resorcinarenes, pillar[n]arenes, cyclotriveratrylenes). Distinguished from T_□□ by the absence of full 3D closure: T_∪ → T_□□ is non-conservative (changes kinetic regime). *Identified through catalog self-audit in v0.3.6.*
    *   `BRAID` (`"Þ_braid"` / `"T_↗↙"`): **NEW in v0.4.0.** Anyonic/braided exchange statistics — the topology of braid groups, not spatial connectivity. Encodes systems where particle exchange is described by non-abelian braid operations rather than simple permutations (Z₂ for bosons/fermions). `tensor(Þ_braid, Þ_braid) → Þ_braid` (anyonic statistics preserved). `Þ_braid ⊓ Þ_linear = ⊥` (no classical topology sits below both). Complexity 4. Physical systems: fractional quantum Hall states (ν=1/3, ν=5/2), Kitaev honeycomb B-phase, non-abelian Majorana platforms. *Identified as missing from the T lattice via quantum particle encoding (v0.4.0).*

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import Topology

    cyclic_topo = Topology.CYCLIC_BOWTIE
    print(f"Cyclic Topology: {cyclic_topo.value}")

    # Accessing from symbol
    hub_topo = Topology.from_symbol("T_□")
    print(f"Hub-Node Topology from symbol: {hub_topo.name}")
    ```

*   **`complexity` Property**:
    The `complexity` property returns an integer score (1-5) reflecting the topological intricacy, where higher values indicate more complex arrangements.

    ```python
    print(f"Complexity of CYCLIC_BOWTIE: {cyclic_topo.complexity}")
    # Expected: 2
    print(f"Complexity of NETWORK: {Topology.NETWORK.complexity}")
    # Expected: 5
    ```

### 3.3. Recognition Mode (R)

Recognition Mode defines the specific physical mechanism by which imscriptions interact and recognize each other, enabling reliable propagation of information or structure.

*   **Enum Members**:
    *   `COVALENT` (`"Ř_subset"` or `"R_⊆"`): Involves the formation of strong, directional covalent bonds.
    *   `NON_COVALENT` (`"Ř_superset"` or `"R_⊇"`): Relies on weaker, reversible interactions like hydrogen bonds, van der Waals forces, or halogen bonds.
    *   `DYNAMIC_CATALYTIC` (`"Ř_Ť"` or `"R_‡"`): Encompasses interactions mediated by dynamic processes, often catalytic, leading to reversible bond formation or transformation.
    *   `MECHANICAL` (`"Ř_mechanical"` or `"R_⇔"`): Characterizes interlocked molecules (e.g., rotaxanes, catenanes) where components are physically linked but not covalently bonded.
    *   `COVALENÞ_DYNAMIC` (`"Ř_covalent_dynamic"` or `"R_⊆+‡"`): Hybrid mode for dynamic covalent chemistry, combining covalent bond formation with reversibility.

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import RecognitionMode

    non_covalent_mode = RecognitionMode.NON_COVALENT
    print(f"Non-Covalent Recognition Mode: {non_covalent_mode.value}")

    # Accessing from symbol
    dynamic_mode = RecognitionMode.from_symbol("R_‡")
    print(f"Dynamic Catalytic Mode from symbol: {dynamic_mode.name}")
    ```

*   **Properties**:
    *   `interaction_energy_range` (`Tuple[float, float]`): Returns a typical energy range (in kJ/mol) for interactions of this mode.
    *   `is_reversible` (`bool`): Indicates whether the interaction is typically reversible.

    ```python
    print(f"Energy range for COVALENT: {RecognitionMode.COVALENT.interaction_energy_range} kJ/mol")
    # Expected: (150.0, 500.0)
    print(f"Is NON_COVALENT reversible? {non_covalent_mode.is_reversible}")
    # Expected: True
    ```

### 3.4. Polarity (P)

Polarity captures the directional character of the interaction, dictating how components orient themselves and select partners. It relates to electron density distribution and reactivity.

*   **Enum Members**:
    *   `ACCEPTOR` (`"Φ_plus"` or `"P+"`): Electron-deficient site, acts as an electrophile or hydrogen bond acceptor.
    *   `DONOR` (`"Φ_minus"` or `"P-"`): Electron-rich site, acts as a nucleophile or hydrogen bond donor.
    *   `SELƒ_COMPLEMENTARY` (`"Φ_F"` or `"P_±"`): Possesses both donor and acceptor characteristics that allow it to interact with identical motifs (e.g., carboxylic acid dimers).
    *   `DONOŘ_ACCEPTOR` (`"Φ_directional"` or `"P_+-"`): Combines donor and acceptor sites in a directional manner, forming specific D-A pairs.

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import Polarity

    acceptor_pol = Polarity.ACCEPTOR
    print(f"Acceptor Polarity: {acceptor_pol.value}")

    # Accessing from symbol
    self_comp_pol = Polarity.from_symbol("P_±")
    print(f"Self-Complementary Polarity from symbol: {self_comp_pol.name}")
    ```

*   **Methods**:
    *   `is_directional` (`bool`): Indicates if the polarity type implies inherent directionality.
    *   `is_compatible_with(other: Polarity)` (`bool`): Checks if two polarity types are compatible for interaction.

    ```python
    print(f"Is ACCEPTOR directional? {acceptor_pol.is_directional}")
    # Expected: True
    print(f"Is ACCEPTOR compatible with DONOR? {acceptor_pol.is_compatible_with(Polarity.DONOR)}")
    # Expected: True
    print(f"Is ACCEPTOR compatible with SELƒ_COMPLEMENTARY? {acceptor_pol.is_compatible_with(Polarity.SELƒ_COMPLEMENTARY)}")
    # Expected: False
    ```

### 3.5. Fidelity (F)

Fidelity provides a nuanced measure of a imscription's reliability, predictability, and robustness. It quantifies how consistently a imscription will perform its intended function under given conditions. Fidelity is domain-dependent and can be quantified differently (e.g., bond dissociation energy, interaction energy, fidelity per cycle).

*   **Enum Members**:
    *   `HIGH` (`"ƒ_ż"` or `"F_ℏ"`): Dominant, highly reliable, geometry-enforcing interactions. ξ_CP ≤ 8.5 nats. In supramolecular host–guest systems: Ka ≳ 10⁹ M⁻¹ (e.g., CB[7]·ferrocene-ammonium, Ka ≈ 3×10¹² M⁻¹). Represents strong constraint.
    *   `MEDIUM` (`"ƒ_ð"` or `"F_ℇ"`): Context-dependent, robust but conditional interactions. ξ_CP 8.5–11.0 nats. Ka ~10⁷–10⁹ M⁻¹ (e.g., CB[7]·adamantane-ammonium, Ka ≈ 4×10⁸ M⁻¹).
    *   `LOW` (`"ƒ_ì"` or `"F_ℓ"`): Probabilistic, competition-sensitive interactions, less reliable. ξ_CP > 11.0 nats. Ka ≲ 10⁷ M⁻¹ (e.g., CB[7]·DABCO, Ka ≈ 2×10⁵ M⁻¹). The F_ℓ tier boundary is anchored by the CB[7] competitive displacement series (Kim JACS 2001; v0.3.3).

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import Fidelity

    high_fidelity = Fidelity.HIGH
    print(f"High Fidelity: {high_fidelity.value}")

    # Accessing from symbol
    medium_fidelity = Fidelity.from_symbol("F_ℇ")
    print(f"Medium Fidelity from symbol: {medium_fidelity.name}")
    ```

*   **Properties**:
    *   `numeric_value` (`float`): Returns a standardized numeric value (0.0-1.0) for quantitative calculations.
    *   `xi_CΦ_range` (`Tuple[float, float]`): Provides the typical range for the Inefficiency Index ($\xi_{CP}$) associated with this fidelity level.

    ```python
    print(f"Numeric value for HIGH Fidelity: {high_fidelity.numeric_value}")
    # Expected: 0.95
    print(f"ξ_CP range for MEDIUM Fidelity: {medium_fidelity.xi_CΦ_range} nats")
    # Expected: (9.0, 11.5)
    ```

*   **`propagate_through(context_factors: Dict[str, float])` Method**:
    This method simulates how fidelity might change when exposed to various environmental or system-level context factors (e.g., `solvent_compatibility`, `temperature_match`, `steric_fit`, `concentration`).

    ```python
    context = {"solvent_compatibility": 0.8, "steric_fit": 0.9}
    propagated_fidelity = high_fidelity.propagate_through(context)
    print(f"Fidelity after propagation: {propagated_fidelity.name}")
    # Example output: MEDIUM (if context factors reduce effective fidelity)
    ```

### 3.6. Granularity (G)

Granularity defines the scale of control or influence exerted by the imscription within a larger system. It describes whether a imscription dictates organization locally, at an intermediate motif level, or globally across a network.

*   **Enum Members**:
    *   `LOCAL` (`"Γ_β"` or `"G_ב"`): Control at a very confined scale, typically involving a single bond or interaction.
    *   `MESOSCALE` (`"Γ_γ"` or `"G_ג"`): Control over a motif or small cluster of interactions (e.g., a specific binding pocket, a small oligomer).
    *   `GLOBAL` (`"Γ_ʔ"` or `"G_א"`): Control that extends throughout an entire network or framework (e.g., a crystal lattice, a self-replicating system).

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import Granularity

    local_gran = Granularity.LOCAL
    print(f"Local Granularity: {local_gran.value}")

    # Accessing from symbol
    global_gran = Granularity.from_symbol("G_א")
    print(f"Global Granularity from symbol: {global_gran.name}")
    ```

*   **Properties**:
    *   `scale_factor` (`int`): Returns an approximate numerical factor representing the number of components controlled by this granularity level.

    ```python
    print(f"Scale factor for MESOSCALE: {Granularity.MESOSCALE.scale_factor}")
    # Expected: 100
    ```

*   **`can_amplify_to(target: Granularity)` Method**:
    Checks if the current granularity level can conceptually "amplify" its control to a specified target granularity level (i.e., local can amplify to mesoscale, mesoscale to global).

    ```python
    print(f"Can LOCAL amplify to GLOBAL? {local_gran.can_amplify_to(global_gran)}")
    # Expected: True
    print(f"Can GLOBAL amplify to LOCAL? {global_gran.can_amplify_to(local_gran)}")
    # Expected: False
    ```

### 3.7. Coupling ($\Gamma$)

Coupling governs the logic of partner selection for a imscription. It describes the specificity or promiscuity of its interactions, from highly selective binding to broad, non-specific recognition.

*   **Enum Members**:
    *   `SPECIFIC` (`"ɢ_otimes"` or `"Γ_⊗"`): Selects one highly specific partner, akin to a lock-and-key mechanism.
    *   `SELECTIVE` (`"ɢ_odot"` or `"Γ_⊙"`): Interacts with a small, defined set of partners (typically 3-10).
    *   `BROAD` (`"ɢ_bigcirc"` or `"Γ_○"`): Compatible with many potential partners, often leading to less predictable outcomes without additional constraints.
    *   Sequential variants (v0.3.5): `SPECIFIC_SEQ`, `SELECTIVE_SEQ`, `BROAÐ_SEQ` — same specificity tier but operating along a directed temporal axis (D_∞ systems). Registered as `"Γ_⊗_seq"`, `"Γ_⊙_seq"`, `"Γ_○_seq"`.
    *   **Dissipative variants (v0.4.0)**: `SPECIFIC_DISSIPATIVE`, `SELECTIVE_DISSIPATIVE`, `BROAÐ_DISSIPATIVE` — irreversible coupling governed by `Γ_↓(DISSIPATIVE)` operator (Lindblad/Zeno channel). Use for open quantum systems where the interaction causes information loss to the environment rather than unitary exchange. `specificity_score` = 0.95 / 0.75 / 0.25 respectively; `partner_count_range` = (1,1) / (1,3) / (1,∞).
    *   **Quantum tier (v0.4.0)**: `QUANTUM_AND`, `QUANTUM_OR`, `QUANTUM_SEQ`, `QUANTUM_DISSIPATIVE` — Toffoli-gate semantics operating on superposition states. `QUANTUM_AND` requires simultaneous entanglement of two control qubits; `QUANTUM_OR` is the logical OR of coherent pathways; `QUANTUM_SEQ` chains unitary gates preserving superposition; `QUANTUM_DISSIPATIVE` = measurement/decoherence channel. All quantum members share `partner_count_range = (1, 2)` and `specificity_score = 0.9`. *Identified as missing during quantum particle encoding — classical Γ values destroy superposition semantics (v0.4.0).*

*   **Usage Examples**:
    ```python
    from imscrbgrmr.models import InteractionGrammar

    specific_grammar = InteractionGrammar.SPECIFIC
    print(f"Specific Grammar: {specific_grammar.value}")

    # Accessing from symbol
    broad_grammar = InteractionGrammar.from_symbol("Γ_○")
    print(f"Broad Grammar from symbol: {broad_grammar.name}")
    ```

*   **Properties**:
    *   `partner_count_range` (`Tuple[int, int]`): Returns the typical range of compatible partners for this grammar.
    *   `specificity_score` (`float`): Provides a numerical score (0.0-1.0) indicating the degree of specificity, where 1.0 is most specific.

    ```python
    print(f"Partner count range for SELECTIVE: {InteractionGrammar.SELECTIVE.partner_count_range}")
    # Expected: (2, 10)
    print(f"Specificity score for BROAD: {broad_grammar.specificity_score}")
    # Expected: 0.1
    ```

### 3.8. Kinetic Character (K)

Kinetic Character encodes the activation barrier and pathway multiplicity for constraint propagation, independently of thermodynamic fidelity F. A imscription can be F_ℏ (high fidelity) but Ç_@ (kinetically inaccessible), or ƒ_ð but Ç_-.

*   **Enum Members**:
    *   `FAST` (`"Ç_-"`): ΔG‡ < 60 kJ/mol; spontaneous on experimental timescales. Accessibility score: 0.95.
    *   `MODERATE` (`"Ç_W"`): ΔG‡ ≈ 60–100 kJ/mol; accessible with mild activation. Accessibility score: 0.70.
    *   `SLOW` (`"Ç_@"`): ΔG‡ > 100 kJ/mol; requires significant activation. Accessibility score: 0.30.
    *   `TRAP` (`"Ç_Ù"`): Pathway multiplicity high; kinetic products diverge from thermodynamic products. Accessibility score: 0.50.
    *   `MBL` (`"Ç_λ"`): **NEW in v0.4.0.** Many-body localization — disorder-induced kinetic arrest. The system is frozen not by an energy barrier but by the structure of its many-body eigenbasis; adding energy does not cause relaxation. Ordinal position 0 (below Ç_Ù at 1) in the kinetic hierarchy — more arrested than any classical trap. Accessibility score: 0.05. Barrier range: (0.0, 0.0) — not barrier-limited. `meet(Ç_λ, anything) → Ç_λ`. **Cannot be inferred from `from_barrier()`**; requires explicit assignment. Physical systems: disordered quantum magnets, cold atoms in quasiperiodic potentials (Aubry-André model), many-body localized phases in 1D interacting systems. *Identified as missing via quantum particle encoding — Ç_Ù is energy-barrier trapping, Ç_λ is disorder trapping; the distinction matters because MBL stores quantum information indefinitely (v0.4.0).*

*   **Example usage**: The carboxylic acid homodimer is F_ℏ, Ç_-. The gas-phase imine condensation proxy is ƒ_ð, Ç_@; aqueous imine is ƒ_ð, Ç_W — same thermodynamic tier, different operational accessibility.

### 3.9. Criticality Phase (Φ)

Criticality Phase encodes the imscription's position relative to the G–D criticality locus.

*   **Enum Members**:
    *   `SUBCRITICAL` (`"⊙_ž"`): G and D are demonstrably independent. Default assignment.
    *   `CRITICAL` (`"⊙_ÿ"`): At the criticality locus — ξ→∞, scale-free behavior, G/D degenerate (Axiom 5).
    *   `SUPERCRITICAL` (`"⊙_Ţ"`): Post-assembly state where imscription identity is absorbed into the assembled material.

*   **Criticality probe** (v2.2+): Use `imscribe criticality-probe <name>` to score Φ_c candidacy. The probe now reports:
    *   `z_eff` — dynamic exponent (diverges logarithmically for Varma QXY class; = 1.33 for 2D percolation)
    *   Degeneracy strength score 0–1 with tier: `none` / `logarithmic` / `power-law` / `collapse`
    *   Universality class hint

    **Eight heuristic factors (v0.4.0):**

    | # | Trigger | Weight | Universality Class |
    |---|---------|--------|--------------------|
    | 1 | G_ℵ (global granularity) | 0.15 | Varma QXY |
    | 2 | D_∞ (temporal dimension) | 0.15 | Varma QXY |
    | 3 | T_⋈ (self-complementary) | 0.15 | Varma QXY |
    | 4 | P_± (symmetric polarity) | 0.15 | Varma QXY |
    | 5 | F_ℏ (quantum fidelity) | 0.15 | Varma QXY |
    | 6 | db24c8 steric-cliff analog | 0.10 | Steric-cliff |
    | 7 | D_∞ + T_⋈ + Φ_DA + F_ℏ | 0.25 | Frank-model (classical bifurcation) |
    | 8 | **G_ℵ + F_ℏ + Ç_Ù + ¬D_∞** | **0.20** | **Quantum criticality (TFI/heavy-fermion)** |

    Factor 8 (v0.4.0) fires when a imscription simultaneously has global granularity, quantum fidelity, and trap-kinetics, but **lacks** D_∞ temporality — the signature of a quantum critical point without a classical order parameter. Falsifiable prediction: susceptibility χ(T→0) ~ T^{-γ}. *Identified as missing when probing the spin singlet and qubit imscriptions, whose criticality fingerprint is orthogonal to Factors 1–7.*

    ```bash
    imscribe criticality-probe my_imscription --degeneracy-type
    imscribe criticality-probe --batch --export-candidates top20.json
    ```

### 3.10. Stoichiometry (S)

Stoichiometry encodes the valency ratio of the recognition event — the molar ratio of partners in the assembled motif. It is a string field (not an Enum) with weight 0.08 in analogy similarity scoring (~6% of total) and hard-constraint enforcement via Pass 4 audit.

*   **Value format**: `"1:1"`, `"2:1"`, `"3:1"`, `"n:m"` (free-form ratio string), or `None` (unassigned).

*   **Consistency rules** (enforced by Pass 4 audit):
    *   `T_⋈ + S="1:1"` → must have P± (self-complementary polarity)
    *   `T_⋈ + S="n:m"` (n≠m) → must have Γ∨(BROAD) or Þ_6
    *   `T_⋈ + no S` → auto-suggested as `"1:1"` if P± present; otherwise flagged for manual review

*   **Auto-backfill**:
    ```bash
    # Assign S="1:1" to all T_⋈ + P± entries (dry run first)
    imscribe catalog auto-stoichiometry --dry-run
    imscribe catalog auto-stoichiometry
    # Result: 1,157/1,269 T_⋈ entries auto-fixed; 112 require manual review
    ```

*   **Similarity grading** in analogy scoring:
    | Case | Score |
    |------|-------|
    | Exact match | 1.00 |
    | Both symmetric (n:n) | 0.90 |
    | Both asymmetric (n≠m) | 0.90 |
    | Category mismatch, ratio diff < 0.5 | 0.70 |
    | Category mismatch, ratio diff ≥ 0.5 | 0.20–0.70 |

*   **Python**:
    ```python
    imscription = Imscription(name="my_dimer", ..., stoichiometry="1:1")
    print(imscription.stoichiometry)  # "1:1"
    ```

### 3.11. Topological Protection Index (Ω) — 11th Primitive (v0.4.0)

Ω encodes the Altland–Zirnbauer / K-theory topological classification of a imscription. It is an **optional field** that defaults to `None` for all classical (non-topological) imscriptions. When set, it appears as the 11th element of the tuple notation: `⟨…; S; Ω⟩`.

*   **Enum**: `TopoIndex` (importable from `imscrbgrmr`)

*   **Enum Members** (ordered by protection strength, ordinal 0→4):

    | Symbol | Value | Ordinal | Description | Physical Systems |
    |--------|-------|---------|-------------|-----------------|
    | `Ω_0` | `TopoIndex.TRIVIAL` | 0 | No topological protection; fully classical | Ordinary insulators, non-topological magnets |
    | `Ω_Z₂` | `TopoIndex.Z2` | 1 | ℤ₂ protection; time-reversal-symmetric TIs | 3D TIs (Bi₂Se₃), QSHI, Z₂ SPT phases |
    | `Ω_Z` | `TopoIndex.Z_CLASS` | 2 | ℤ classification; integer invariant | Integer QHE (σ_xy = ne²/h), Chern insulators |
    | `Ω_Ch` | `TopoIndex.CHERN` | 3 | Chern-number protection; broken time-reversal | Haldane model, magnetic TIs, anomalous QHE |
    | `Ω_NA` | `TopoIndex.NON_ABELIAN` | 4 | Non-Abelian anyonic statistics; braided exchange | Kitaev honeycomb, Moore-Read FQH (ν=5/2), Majorana platforms |

*   **Lattice semantics**:
    *   `meet(Ω_a, Ω_b) → Ω_min` — conservative guarantee: use the weaker protection class when two systems couple
    *   `join(Ω_a, Ω_b) → Ω_max` — capability ceiling: higher class can host everything the lower class can
    *   `tensor(Ω_a, Ω_b) → Ω_max` — composite system inherits the stronger topological protection

*   **Distance weight**: 0.7 in `tuple_distance()` — Ω contributes ~5.7% of total distance (weight 0.7 out of default total ≈12.3).

*   **Usage**:
    ```python
    from imscrbgrmr import TopoIndex, Imscription

    kitaev_chain = Imscription(
        name="kitaev_chain",
        ...,
        topo_index=TopoIndex.NON_ABELIAN,   # Ω_NA — Majorana edge modes
    )

    print(kitaev_chain.topo_index.protection_strength)  # 4
    print(kitaev_chain.topo_index.physical_systems)
    # → 'Kitaev honeycomb, Moore-Read FQH (ν=5/2), Majorana platforms'
    print(kitaev_chain.to_notation())
    # → ⟨...; Ω_NA⟩
    ```

*   **`imscribe analyze` display** (when Ω is set):
    ```
    Ω (TopoIndex)   Ω_NA   Non-Abelian anyonic · protection_strength=4
    ```

*   *Identified as missing when encoding the five quantum particle imscriptions (photon/proton/electron/spin/qubit). The framework had no way to distinguish a trivially gapped insulator from a topological insulator or non-Abelian fractional QH state — the distinction is operationally essential for quantum information protection arguments (v0.4.0).*

## 4. Command Line Interface (CLI)

Imscribing Grammar provides a powerful command-line interface for rapid analysis and exploration of imscriptions. The CLI is accessible via `main.py` or the `imscrbgrmr` command (if installed as a package).

### 4.1. Core Commands

#### `analyze`
Analyze a imscription by its name or a raw notation string.

**Usage:**
```bash
python3 main.py analyze [IDENTIFIER]
```

**Example:**
```bash
python3 main.py analyze carboxylic_acid_dimer
```

#### `catalog list`
List all imscriptions currently registered in the global catalog.

**Usage:**
```bash
python3 main.py catalog list [--domain DOMAIN]
```

**Example:**
```bash
python3 main.py catalog list --domain temporal
```

#### `thermo`
Calculate thermodynamic metrics ($\eta_{CP}$ and $\xi_{CP}$) for a registered imscription.

**Usage:**
```bash
python3 main.py thermo [IDENTIFIER] --delta-g [KJ_MOL]
```

**Example:**
```bash
python3 main.py thermo carboxylic_acid_dimer --delta-g -12.0
```

#### `check`
Check the compatibility between two imscriptions.

**Usage:**
```bash
python3 main.py check [imscription_A] [imscription_B]
```

**Example:**
```bash
python3 main.py check enolate_imscription carbonyl_imscription
```

### 4.2. Catalog Audit Command

The `imscribe audit` command runs a 4-pass scan of the catalog for grounding issues, topology errors, attractor-tuple contamination, and stoichiometry inconsistencies.

**Pass summary:**
| Pass | Axiom | Checks |
|------|-------|--------|
| 1 | Axiom 6 | D_∞ entries: structured grounding["reset"] block checked first (discrete or continuous); falls back to keyword scan |
| 2 | Axiom 7 | T_⋈ entries for named closing bond; rejects linear/rod/chain |
| 3 | — | Attractor-tuple contamination (≥7/7 match, no stored reasoning) |
| 4 *(v2.2)* | — | S consistency: T_⋈[1:1]↔P±; T_⋈[n:m]↔Γ∨BROAD/Þ_6 |

**Usage:**
```bash
imscribe audit [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--axiom 6` | Audit all D_∞ entries for Axiom 6 (discrete reset or continuous dissipative flux) |
| `--axiom 7` | Audit all T_⋈ entries for Axiom 7 (named closing bond) |
| `--axiom 4` *(v2.2)* | Audit T_⋈ entries for stoichiometry consistency (Pass 4) |
| `--primitive D/T/R/...` | Filter by primitive type |
| `--value TEXT` | Filter by primitive value (e.g. `temporal`, `cyclic`) |
| `--status STATUS` | Filter by grounding status (unverified, partial, override, full, flagged_for_review) |
| `--auto-flag` | Set `grounding_status="flagged_for_review"` on problem entries |
| `--dry-run` | Preview what would be flagged without making changes |

**Examples:**

```bash
# Audit all D_∞ entries for closed-cycle grounding
imscribe audit --axiom 6

# Audit all T_⋈ entries and auto-flag those without closing bond
imscribe audit --axiom 7 --auto-flag

# Preview unverified entries without making changes
imscribe audit --status unverified --dry-run

# Find all temporal entries with partial grounding
imscribe audit --primitive D --value temporal --status partial

# Full audit: all unverified entries across catalog
imscribe audit --status unverified --auto-flag
```

**Understanding the output:**

The command prints a Rich table with columns:
- **Imscription** — catalog entry name
- **Domain** — molecular / supramolecular / temporal / speculative
- **Grounding Status** — full / partial / override / unverified / flagged_for_review
- **Failed Primitives** — primitives that failed grounding checks
- **Flag Reason** — why the entry was flagged (grounding status or axiom check)

**Axiom 6 check logic (updated v0.3.3 — discrete/continuous):**

The audit calls `AxiomValidator.validate_axiom6_temporal_grounding(imscription)` which checks in priority order:

1. **Structured block** — `imscription.grounding["reset"]` (persisted in catalog JSON, survives reload):
   - `type = "discrete"`: requires `cycle_steps` list ≥ 2, **or** `axiom6_grounding` metadata block
   - `type = "continuous"`: requires `driving_gradient.description` + `driving_gradient.coupling`
2. **Keyword scan fallback** — only when no structured block exists. Scans description/reasoning for `AXIOM_6_RESEÞ_INDICATORS` + `AXIOM_6_PROCESΣ_INDICATORS`; both must be present.

**Adding structured Axiom 6 grounding to a catalog entry:**

```python
from imscrbgrmr import global_catalog

s = global_catalog.get("my_dissipative_imscription")

# Continuous (dissipative, far-from-equilibrium):
s.grounding["reset"] = {
    "type": "continuous",
    "driving_gradient": {
        "description": "Continuous reagent supply (fuel + substrate) drives steady-state turnover",
        "coupling": "Chemical potential gradient: fuel → product, with autocatalytic product feedback",
        "entropy_export": "Heat dissipation to solvent; byproduct efflux",
    },
    "termination_condition": "Reagent depletion ends the cycle; no sharp reset event.",
}

# Discrete (closed cycle with explicit reset step):
s.grounding["reset"] = {
    "type": "discrete",
    "cycle_steps": [
        "Step 1: catalyst activates substrate",
        "Step 2: product formed",
        "Step 3: hydrolysis/relaxation returns catalyst to initial state (reset)",
    ],
}

global_catalog.save_catalog()
```

**Known grounded entries (v0.3.3):**

| Entry | Reset type | Mechanism |
|-------|-----------|-----------|
| `soai_pyrimidyl_autocatalytic_cycle` | `continuous` | iPr₂Zn + aldehyde flux; Frank-model bifurcation |
| `proline_aldol_cycle` | `discrete` | Iminium hydrolysis → free proline reset |

**Axiom 7 check logic:**
Scans the description for `AXIOM_7_CLOSINΓ_INDICATORS` (e.g. "hydrogen bond", "ring", "macrocycle") and rejects if `AXIOM_7_INVALIÐ_TOPO_KEYWORDS` are found (e.g. "linear", "rod", "allene").

### 4.3. I(bits) Calibration Command *(v2.2)*

```bash
# Run full calibration pipeline (vacuum)
imscribe info-bits --calibrate

# With solvent correction
imscribe info-bits --calibrate --solvent chloroform
imscribe info-bits --calibrate --solvent water

# Single imscription
imscribe info-bits carboxylic_acid_dimer
imscribe info-bits triple_hbond_array --solvent THF
```

**Output fields:** `I_recognition`, `I_orientation` (overhead), `I_net = I_rec − 0.3×I_orient`, `I_total+solvent`, `ΔΣ_conf`, heuristic comparison, verdict.

**Calibrated ranges (v2.2):**
| System type | I_recognition |
|-------------|---------------|
| 2-HB dimers (acid dimer) | 9–10 bits |
| Cooperative arrays (triple H-bond DAD·ADA) | 14–18 bits |
| Quadruple arrays (AADD·DDAA) | 19–24 bits |
| Temporal cycles (proline aldol) | 6–9 bits/turn |

### 4.4. Criticality Probe Command *(v2.2 / updated v0.3.3)*

```bash
# Single entry
imscribe criticality-probe my_imscription
imscribe criticality-probe my_imscription --degeneracy-type

# With measured correlation lengths (Varma QXY test)
imscribe criticality-probe my_imscription --xi-r 6.2 --xi-tau 1.8e14

# Batch mode: scan all Φ_c / T_⋈+D_∞ / steric-cliff candidacy entries
imscribe criticality-probe --batch
imscribe criticality-probe --batch --degeneracy-type
imscribe criticality-probe --batch --export-candidates candidates.json
```

**Degeneracy tiers:**
| Score | Tier | Meaning |
|-------|------|---------|
| 0.00–0.30 | `none` | G and D independent |
| 0.30–0.60 | `logarithmic` | Varma QXY — ξ_r ≈ ln ξ_τ |
| 0.60–0.85 | `power-law` | Conventional QCP — finite z |
| 0.85–1.00 | `collapse` | Direct G/D identity |

**Scoring factors** (`score_phi_c_candidacy()`, `varma_probe.py`):

| Factor | Weight | Fires when | Universality class |
|--------|--------|------------|--------------------|
| 1–5 (Varma QXY structural heuristics) | 0.35 / 0.25 / 0.20 / ... | D_∞, R_‡, G_ג primitives present | Varma QXY (quantum) |
| 6 (Steric-cliff proxy) | 0.65 | `phi_c_candidacy.proxy_degeneracy_strength` ≥ 0.50 in grounding | Steric-cliff (mechanical) |
| 7 (Frank-model classical bifurcation) | 0.25 | D_∞ + T_⋈ + Φ_directional + F_ℏ all present | Frank 1953 (classical pitchfork) |

**Validated case studies (v0.3.3):**

| System | ξ_r | ξ_τ | Ratio | Score | Result |
|--------|-----|-----|-------|-------|--------|
| Soai autocatalytic cycle | 15 | 7.2×10¹⁵ | 0.94 | 0.920 | Approaching Φ_c (Frank model) |
| DB24C8 pseudorotaxane | — | — | — | 0.461 | Approaching Φ_c (steric cliff) |
| Proline-aldol cycle | 6.2 | 1.8×10¹⁴ | 0.189 | 0.380 | Φ_sub (subcritical, confirmed) |

**ω_c normalization note:** ξ_τ = τ_corr × ω_c where ω_c is the appropriate natural frequency for the system's relevant timescale. For solution-phase catalytic systems, use ω_c ≈ 10¹² s⁻¹ (solvent relaxation frequency) rather than kBT/h ≈ 6.25×10¹² s⁻¹ to avoid mixing molecular-vibration and macroscopic-catalytic timescales.

### 4.5. Stoichiometry Commands *(v2.2)*

```bash
# Auto-assign S="1:1" to T_⋈ + P± entries
imscribe catalog auto-stoichiometry --dry-run   # preview
imscribe catalog auto-stoichiometry             # apply (up to 500 entries)
imscribe catalog auto-stoichiometry --limit 2000  # larger batch

# Analogy search with stoichiometry flags
imscribe analogies my_imscription --stoichiometry-aware   # raises S weight to 0.12
imscribe analogies my_imscription --critical-only          # pre-filter by Φ_c score > 0.5
imscribe analogies my_imscription --stoichiometry-aware --critical-only
```

### 4.6. Experimental Validation Case Studies *(v0.3.3)*

#### CB[7] Competitive Displacement — F-floor Ratchet (6/6 Validated)

Tests the HotSwap `F`-floor hard constraint: a swap is BLOCKED if ƒ_new < ƒ_old. The CB[7] host-guest series provides a literature-grounded three-tier ordering.

```bash
# Register the three CB[7] complexes (already in catalog post-v0.3.3)
# CB7_ferrocene_ammonium_complex  (F_ℏ, Ka = 3×10¹², ΔG = -71.2 kJ/mol)
# CB7_adamantane_ammonium_complex (F_ℇ, Ka = 4.3×10⁸, ΔG = -49.1 kJ/mol)
# CB7_DABCO_complex               (F_ℓ, Ka = 2×10⁵, ΔG = -30.1 kJ/mol)

# Run all 6 directional swaps — expected: 3 APPROVED, 3 BLOCKED
imscribe hotswap CB7_ferrocene_ammonium_complex CB7_adamantane_ammonium_complex --delta-g -49.1
# → APPROVED (F_ℏ → F_ℇ, downgrade: ƒ_new=F_ℇ < ƒ_old=F_ℏ) ← NOTE: Fc→Ad is BLOCKED
imscribe hotswap CB7_adamantane_ammonium_complex CB7_ferrocene_ammonium_complex --delta-g -71.2
# → APPROVED (Ad→Fc: ƒ_new=F_ℏ > ƒ_old=F_ℇ)

imscribe hotswap CB7_DABCO_complex CB7_adamantane_ammonium_complex --delta-g -49.1
# → APPROVED (DABCO→Ad: ƒ_new=F_ℇ > ƒ_old=F_ℓ)
imscribe hotswap CB7_adamantane_ammonium_complex CB7_DABCO_complex --delta-g -30.1
# → BLOCKED (Ad→DABCO: ƒ_new=F_ℓ < ƒ_old=F_ℇ)

imscribe hotswap CB7_ferrocene_ammonium_complex CB7_DABCO_complex --delta-g -30.1
# → BLOCKED (Fc→DABCO: ƒ_new=F_ℓ < ƒ_old=F_ℏ)
imscribe hotswap CB7_DABCO_complex CB7_ferrocene_ammonium_complex --delta-g -71.2
# → APPROVED (DABCO→Fc: ƒ_new=F_ℏ > ƒ_old=F_ℓ)
```

**Result table (all 6 match experiment):**

| Swap | Framework | Experiment (Kim 2001) |
|------|-----------|----------------------|
| Fc displaces Ad | APPROVED | Yes (quantitative) |
| Ad displaces Fc | BLOCKED | No (no exchange) |
| Ad displaces DABCO | BLOCKED | No (DABCO weaker → Ad is stronger, Ad stays) |
| DABCO displaces Ad | APPROVED | Yes (Ad quantitatively displaces DABCO, confirmed by reverse) |
| Fc displaces DABCO | BLOCKED | No |
| DABCO displaces Fc | APPROVED | Yes |

*References:* Kim et al. J. Am. Chem. Soc. **123**, 12091 (2001); Assaf & Nau, Chem. Soc. Rev. **44**, 394 (2015); Sindelar et al. J. Org. Chem. **72**, 3221 (2007).

#### Soai Reaction Varma Probe — Approaching Φ_c (Score 0.920)

```bash
imscribe criticality-probe soai_pyrimidyl_autocatalytic_cycle --xi-r 15 --xi-tau 7.2e15
```

**Expected output summary:**
- Ratio ξ_r / ln(ξ_τ) = 15 / ln(7.2×10¹⁵) ≈ **0.94** (near-critical; threshold = 1.0 ± 20%)
- Factor 7 fires: D_∞ + T_⋈ + Φ_directional + F_ℏ → Frank-model pitchfork bifurcation
- Score: **0.920** — approaching Φ_c
- Active species: [Zn₂·(pyrimidylalkoxide)₂·iPr₂Zn] dimer (Gridnev 2010)

#### Proline-Aldol Varma Probe — Φ_sub Confirmed (Score 0.380)

```bash
imscribe criticality-probe proline_aldol_cycle --xi-r 6.2 --xi-tau 1.8e14
```

**Expected output summary:**
- Ratio ξ_r / ln(ξ_τ) = 6.2 / ln(1.8×10¹⁴) ≈ **0.189** (well below 1.0 threshold)
- Factor 7 does not fire: P_±^ψ (pseudosymmetric, not directional Φ_DA)
- Score: **0.380** — Φ_sub (subcritical)
- Structural prediction: criticality would require ξ_r ≥ 32 lattice units (~48 Å correlation), incompatible with observed enamine geometry

### 4.6. Audio CLI (`imscribeaudio.py`)

Synthesises WAV audio for any primitive value, Imscription tuple, or named catalog entry. Requires `numpy`, `scipy`.

#### Modes

```bash
# Full 49-symbol canon in field order (Ð Þ Ř Φ ƒ Ç Γ ɢ ⊙ Ħ Σ Ω)
python imscribeaudio.py --all [--dur 0.75] [--fs 44100] [-o FILE]

# Single symbol by base glyph + subscript
python imscribeaudio.py ⊙ ž
python imscribeaudio.py Ħ A --dur 1.2

# 12-primitive Imscription tuple — space- or comma-separated
python imscribeaudio.py --tuple "Ð_ω Þ_¨ Ř_= Φ_} ƒ_ż Ç_@ Γ_ʔ ɢ_ˌ ⊙_ÿ Ħ_A Σ_S Ω_z"
python imscribeaudio.py -t "Ð_ß,Þ_6,Ř_¯,Φ_F,ƒ_ì,Ç_-,Γ_ʔ,ɢ_^,⊙_ž,Ħ_Ñ,Σ_S,Ω_Å"

# Named catalog entry (auto-resolves ⊙ → ⊙ for pre-migration entries)
python imscribeaudio.py --name psychedelic_baseline
python imscribeaudio.py -n dark_matter -o dark_matter.wav

# List all 49 canonical glyph IDs
python imscribeaudio.py --list
```

#### Glyph IDs

Primitive values are addressed by canonical glyph strings — the ID **is** the glyph:

| Field | Canonical IDs |
|-------|--------------|
| Ð (Dimensionality) | `Ð_ß` `Ð_C` `Ð_;` `Ð_ω` |
| Þ (Topology) | `Þ_6` `Þ_K` `Þ_ò` `Þ_¨` `Þ_O` |
| Ř (Relational) | `Ř_¯` `Ř_ý` `Ř_Ť` `Ř_=` |
| Φ (Polarity) | `Φ_ɐ` `Φ_υ` `Φ_F` `Φ_˙` `Φ_}` |
| ƒ (Fidelity) | `ƒ_ì` `ƒ_ð` `ƒ_ż` |
| Ç (Kinetics) | `Ç_-` `Ç_W` `Ç_@` `Ç_Ù` `Ç_λ` |
| Γ (Scope) | `Γ_β` `Γ_γ` `Γ_ʔ` |
| ɢ (Grammar) | `ɢ_^` `ɢ_˝` `ɢ_ˌ` `ɢ_Ş` |
| ⊙ (Criticality) | `⊙_ž` `⊙_ÿ` `⊙_Æ` `⊙_3` `⊙_Ţ` |
| Ħ (Chirality) | `Ħ_Ñ` `Ħ_£` `Ħ_A` `Ħ_!` |
| Σ (Stoichiometry) | `Σ_S` `Σ_ő` `Σ_ï` |
| Ω (Winding) | `Ω_Å` `Ω_2` `Ω_z` `Ω_5` |

Old Lean names (`D_wedge`, `T_network`, `Phi_c`, `R_lr`, etc.) are accepted everywhere via `OLD_ID_MAP` in `sounds.py`.

#### odot_operator tuple

```bash
python imscribeaudio.py --tuple "Ð_ω Þ_¨ Ř_= Φ_} ƒ_ż Ç_@ Γ_ʔ ɢ_ˌ ⊙_ÿ Ħ_A Σ_S Ω_z"
```

#### Library usage

```python
from sounds import synthesize_symbol, normalize, PRIMITIVE_MAP, OLD_ID_MAP, resolve_id

# Resolve any token (canonical or old name) → (base, sub) for synthesize_symbol
pair = resolve_id('Phi_c')      # → ('⊙', 'ÿ')
pair = resolve_id('⊙_ÿ')        # → ('⊙', 'ÿ')

sig = synthesize_symbol(*pair, fs=44100, dur=0.75)
```

---

## 5. Building and Managing imscriptions

The core data structure in Imscribing Grammar is the `Imscription` class. It encapsulates all ten primitives and provides methods for notation generation and serialization.

### 5.1. Creating imscriptions

You can create a `Imscription` object by providing its name and primitives as enum members plus the optional `stoichiometry` string.

```python
from imscrbgrmr import (
    Imscription, Dimensionality, Topology, RecognitionMode,
    Polarity, Fidelity, KineticCharacter, Granularity,
    InteractionGrammar, CriticalityPhase
)

carboxylic_dimer = Imscription(
    name="carboxylic_acid_dimer",
    dimensionality=Dimensionality.MOLECULAR,
    topology=Topology.CYCLIC_BOWTIE,
    recognition_mode=RecognitionMode.NON_COVALENT,
    polarity=Polarity.SELƒ_COMPLEMENTARY,
    fidelity=Fidelity.HIGH,
    kinetic_character=KineticCharacter.FAST,
    granularity=Granularity.LOCAL,
    interaction_grammar=InteractionGrammar.SPECIFIC,
    criticality_phase=CriticalityPhase.SUBCRITICAL,
    stoichiometry="1:1",
    description="Classic hydrogen-bonded dimer (R²₂(8) motif)"
)
```

### 5.2. Unified Notation

The `to_notation()` method generates the full formal string: `⟨D; T; R; P; F; K; G; Γ; Φ; S⟩`.

```python
print(carboxylic_dimer.to_notation())
# Output: ⟨Ð_ß; Þ_ò; Ř_superset; Φ_F; ƒ_ż; Ç_-; Γ_β; ɢ_otimes; ⊙_ž; 1:1⟩
```

You can also parse a notation string back into a `ImscriptionNotation` object:

```python
from imscrbgrmr import parse_notation
notation = parse_notation(
    "⟨Ð_ß; Þ_ò; Ř_superset; Φ_F; ƒ_ż; Ç_-; Γ_β; ɢ_otimes; ⊙_ž; 1:1⟩"
)
print(notation.dimensionality)  # Dimensionality.MOLECULAR
print(notation.stoichiometry)   # "1:1"
```

### 5.3. Serialization

imscriptions support serialization to dictionaries and JSON for easy storage and transmission.

```python
# To Dictionary
data = carboxylic_dimer.to_dict()

# To JSON
json_str = carboxylic_dimer.to_json()

# From JSON
new_imscription = Imscription.from_json(json_str)
```

## 6. ImscriptionCatalog: Storage and Discovery

The `ImscriptionCatalog` acts as a centralized repository for imscriptions, enabling advanced search and cross-domain reasoning.

### 6.1. Registration

Registering imscriptions allows you to retrieve them by name later or include them in global searches.

```python
from imscrbgrmr.registry import global_catalog

# The catalog is automatically populated with defaults on CLI start,
# but you can register your own:
global_catalog.register(carboxylic_dimer)
```

### 6.2. Searching

The catalog supports indexed searches by any of the ten primitives.

```python
# Search for all high-fidelity imscriptions
high_f = global_catalog.search(fidelity=Fidelity.HIGH)

# Search for all temporal imscriptions
temporal = global_catalog.search_by_domain("temporal")
```

### 6.3. Cross-Domain Analogy Search

One of the most powerful features of Imscribing Grammar is the ability to find "analogs" across different domains (e.g., finding a temporal process that behaves like a molecular H-bond dimer).

```python
# Find temporal imscriptions that are topologically and functionally 
# analogous to a molecular carboxylic acid dimer
analogs = global_catalog.find_cross_domain_analogs(
    carboxylic_dimer, 
    target_domain="temporal"
)
```

## 7. Constraint Propagation Engine

The `ConstraintEngine` and `FidelityPropagator` are used to analyze how imscriptions interact and how their individual constraints combine to influence the overall system.

### 7.1. Pairwise Compatibility

Check if two imscriptions can interact based on their primitives (recognition mode, polarity, dimensionality, etc.).

```python
from imscrbgrmr.constraints import ConstraintEngine

engine = ConstraintEngine()
report = engine.check_pair_compatibility(imscription_a, imscription_b)

if report.is_compatible:
    print(f"Compatible! Shared domains: {report.details['shared_domains']}")
else:
    print(f"Incompatible: {report.result.name}")
```

### 7.2. Fidelity Propagation and Cooperativity

Individual imscription fidelities often amplify when combined in specific topologies (e.g., cyclic motifs show superlinear cooperativity).

```python
from imscrbgrmr.constraints import FidelityPropagator

propagator = FidelityPropagator()

# Propagate fidelity across a list of interacting imscriptions
total_fidelity = propagator.propagate([imscription_a, imscription_b, imscription_c])

# Compute cooperativity factors
coop = propagator.compute_cooperativity_factor([imscription_a, imscription_b])
print(f"Total cooperativity: {coop['total_cooperativity']:.2f}")
```

## 8. Thermodynamics: Quantifying Efficiency

Imscribing Grammar introduces formal metrics to quantify how effectively physical energy ($\Delta G$) is converted into structural information ($I$) with a given reliability ($F$).

### 8.1. $\eta_{CP}$ and $\xi_{CP}$

*   **$\eta_{CP}$ (Efficiency)**: The ratio of reliable information gain to the energy cost (relative to the Landauer limit).
*   **$\xi_{CP}$ (Inefficiency Index)**: The negative log of efficiency, measured in nats.

```python
from imscrbgrmr.thermodynamics import compute_eta_CP

# Calculate metrics for a carboxylic acid dimer (ΔG(298K, gas) = -12 kJ/mol)
result = compute_eta_CP(carboxylic_dimer, delta_g=-12.0)

print(f"Efficiency (η_CP): {result.eta_CP:.2e}")
print(f"Inefficiency (ξ_CP): {result.xi_CP:.2f} nats")
print(f"Assessment: {result.efficiency_description}")
```

### 8.2. Landauer Benchmarking

Compare your system's efficiency directly to the theoretical minimum energy required to process the equivalent amount of information.

```python
from imscrbgrmr.thermodynamics import benchmark_against_landauer

benchmark = benchmark_against_landauer(carboxylic_dimer, delta_g=-12.0)
print(f"Overhead: {benchmark['overhead_ratio']:.1e}× Landauer limit")
```

## 9. Domain-Specific Agents

Imscribing Grammar includes specialized agents that apply the core framework to specific chemical domains.

### 9.1. Molecular Agent

Used for retrosynthetic analysis and molecular bond disconnection.

```python
from imscrbgrmr.domains.molecular import MolecularImscriptionAgent

mol_agent = MolecularImscriptionAgent()
analysis = mol_agent.analyze_reaction_center("CC(=O)O")
print(f"Disconnection Feasibility: {analysis.disconnection_feasibility}")
```

### 9.2. Supramolecular Agent

Focuses on spatial organization and cooperative effects in non-covalent networks.

```python
from imscrbgrmr.domains.supramolecular import SupramolecularImscriptionAgent

supra_agent = SupramolecularImscriptionAgent()
coop = supra_agent.compute_cooperativity_induction(num_bonds=3)
```

### 9.3. Temporal Agent

Analyzes time-dependent processes, catalytic cycles, and temporal reliability.

```python
from imscrbgrmr.domains.temporal import TemporalImscriptionAgent

temp_agent = TemporalImscriptionAgent()
fidelity = temp_agent.compute_fidelity_per_cycle(k_cat=1.0, k_side=0.001)
```

## 10. AI-Powered Imscription Generation

Imscribing Grammar includes an LLM-powered agent that can automatically generate imscriptions from natural language descriptions or SMILES strings.

### 10.1. ImscriptionGeneratorAgent

The `ImscriptionGeneratorAgent` uses advanced language models to analyze chemical descriptions and map them to all ten primitives.

```python
import asyncio
from agents.imscribe_generator_agent import ImscriptionGeneratorAgent
from imscrbgrmr.provider_config import build_agent_config

async def main():
    # Use config-driven defaults (model=None uses provider default)
    config = build_agent_config(provider="anthropic", model=None)
    agent = ImscriptionGeneratorAgent(config)

    # Generate from natural language description
    result = await agent.generate_from_description(
        "carboxylic acid dimer with cyclic hydrogen bonding",
        delta_g=-12.0,  # Optional: for thermodynamic analysis (ΔG(298K, gas) for acid dimer)
        auto_register=True  # Automatically add to catalog
    )

    print(f"Generated: {result.imscription.name}")
    print(f"Notation: {result.imscription.to_notation()}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"Reasoning: {result.reasoning}")

    # Access thermodynamic metrics if delta_g was provided
    if result.thermodynamic_metrics:
        print(f"η_CP: {result.thermodynamic_metrics['eta_CP']:.2e}")
        print(f"ξ_CP: {result.thermodynamic_metrics['xi_CP']:.4f} nats")

asyncio.run(main())
```

### 10.2. Generation from SMILES

```python
from agents.imscribe_generator_agent import ImscriptionGeneratorAgent
from imscrbgrmr.provider_config import build_agent_config

config = build_agent_config(provider="anthropic", model=None)
agent = ImscriptionGeneratorAgent(config)

result = await agent.generate_from_smiles(
    "CC(=O)O",  # Acetic acid
    name="acetic_acid",
    functional_groups=["carboxylic_acid"],
    auto_register=True
)

print(f"Generated imscription: {result.imscription.to_notation()}")
```

### 10.3. Convenience Function

For quick imscription generation, use the `generate_imscription` function:

```python
from agents.imscribe_generator_agent import generate_imscription

result = await generate_imscription(
    "DNA adenine-thymine base pair",
    provider="qwen",
    model="qwen3-max",
    delta_g=-80.0
)

print(f"Notation: {result.imscription.to_notation()}")
print(f"ξ_CP: {result.thermodynamic_metrics['xi_CP']:.4f} nats")
```

### 10.4. CLI Commands for AI Generation

The CLI is accessible via both `imscrbgrmr` and the short alias `imscribe`:

```bash
# Both commands are equivalent:
imscrbgrmr generate "carboxylic acid dimer" --delta-g -12.0
imscribe generate "carboxylic acid dimer" --delta-g -12.0

# Generate from SMILES string
imscribe generate-smiles "CC(=O)O" --name acetic_acid

# Specify provider and model
imscribe generate "proline catalyzed aldol cycle" \
    --provider qwen \
    --model qwen3-max

# Save result to file
imscribe generate "triple hydrogen bond array" \
    --output result.json

# Generate without auto-registration
imscribe generate "test system" --no-register
```

#### Grounding-Controlled Registration (Fix 1 — NEW in v2.1.3)

```bash
# Block registration if grounding validation fails
imscribe generate "carboxylic acid dimer" --strict-grounding

# Force registration despite failures — logs to audit trail
imscribe generate "novel quantum system" \
    --override-grounding \
    --override-reason "speculative entry, grounding pending publication"

# Register in the 'speculative' domain (Fix 5 quarantine)
imscribe generate "quantum tunneling imscription" --speculative

# Combine: speculative + override
imscribe generate "..." --speculative --override-grounding \
    --override-reason "theoretical proposal"
```

**Grounding flag semantics:**

| Flag | Effect |
|------|--------|
| `--strict-grounding` | Raises `GroundingValidationError` if any primitive fails grounding |
| `--override-grounding` | Allows registration despite failure — **requires** `--override-reason` |
| `--override-reason TEXT` | Justification string logged to audit trail |
| `--speculative` | Sets `domain="speculative"` in `CatalogEntry` |

### 10.5. Agent Framework CLI

The AjintK agent framework is accessible via the `agents` subcommand:

```bash
# List all available agents
imscribe agents list

# Run ImscriptionGeneratorAgent from CLI
imscribe agents run -d "carboxylic acid dimer" -g -12.0
imscribe agents run --provider qwen --model qwen3-max -d "DNA base pair"

# Generate from SMILES via agent
imscribe agents from-smiles "CC(=O)O" --name acetic_acid
imscribe agents from-smiles "CC(=O)O" -o result.json
```

### 10.6. Additional CLI Commands

#### Compare imscriptions

```bash
# Compare multiple imscriptions side-by-side
imscrbgrmr compare carboxylic_acid_dimer adenine_thymine_pair

# Include thermodynamic comparison
imscrbgrmr compare imscription1 imscription2 --delta-g -52.0 -45.0 --include-thermo
```

#### Catalog Tree View

```bash
# View catalog as hierarchical tree
imscrbgrmr catalog tree

# Filter by domain
imscrbgrmr catalog tree --domain molecular
```

#### Export Catalog

```bash
# Export to JSON
imscrbgrmr export --format json --output imscriptions.json

# Export to CSV
imscrbgrmr export --format csv --output imscriptions.csv

# Export specific domain
imscrbgrmr export --domain temporal --format yaml
```

## 10.5. Autonomous Imscription Discovery

The `AutonomousImscriptionDiscoveryAgent` enables continuous, self-directed imscription discovery. The agent autonomously proposes novel chemical systems, validates them against existing knowledge, and registers valid imscriptions to the persistent catalog.

### Running Autonomous Discovery

```bash
# Basic: 10 cycles, 30 minutes
imscribe agents discover

# Extended campaign: 100 cycles, 2 hours
imscribe agents discover --cycles 100 --duration 120

# Focused exploration: halogen bonding
imscribe agents discover --focus "halogen bonding" --cycles 50

# Different provider with lower confidence threshold
imscribe agents discover --provider qwen --confidence 0.6 --cycles 30
```

### Python API

```python
import asyncio
from agents.autonomous_imscription_discovery_agent import (
    AutonomousImscriptionDiscoveryAgent,
    AutonomousRunConfig,
    run_autonomous_discovery,
)
from imscrbgrmr.provider_config import build_agent_config

# Method 1: Convenience function
results = await run_autonomous_discovery(
    max_cycles=50,
    max_minutes=60,
    provider="anthropic",
    focus="catalysis",
)

# Method 2: Full control
config = build_agent_config(provider="anthropic", model=None)
agent = AutonomousImscriptionDiscoveryAgent(config)

run_config = AutonomousRunConfig(
    max_cycles=100,
    max_duration_minutes=120,
    min_confidence_threshold=0.7,
    target_domains=["molecular", "supramolecular"],
    focus_areas=["halogen bonding", "chalcogen bonding"],
    save_interval=10,
)

results = await agent.run_autonomous(run_config)

# Access results
print(f"Cycles completed: {agent.stats['cycles_completed']}")
print(f"imscriptions registered: {agent.stats['imscriptions_registered']}")
print(f"Success rate: {agent.stats['imscriptions_registered'] / agent.stats['cycles_completed'] * 100:.1f}%")
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_cycles` | int | 100 | Maximum discovery cycles |
| `max_duration_minutes` | float | 60.0 | Maximum runtime |
| `min_confidence_threshold` | float | 0.7 | Minimum confidence for registration |
| `target_domains` | List[str] | All | Domains to explore |
| `focus_areas` | Optional[List[str]] | None | Specific chemistry focus |
| `save_interval` | int | 10 | Save progress every N cycles |
| `output_dir` | Optional[Path] | None | Output directory |
| `diversity_mode` | bool | True | Actively avoid repeats |

### Output Files

The agent saves to `./discovery_output/` (or custom `--output`):

- `discovery_history_*.json` — Cycle-by-cycle results
- `discovery_stats_*.json` — Statistics and configuration
- `catalog_*.json` — Catalog export at checkpoint

### Validation Results

| Result | Icon | Description |
|--------|------|-------------|
| `valid_novel` | ✓ | Successfully registered |
| `duplicate_exists` | ⊗ | Already in catalog |
| `invalid_chemistry` | ✗ | Chemically invalid **or axiom violation** |
| `literature_conflict` | ⚠ | Conflicts with known systems |
| `low_confidence` | ? | Below threshold |

### Axiom Validation (March 14, 2026)

**All imscriptions are now validated against composition axioms before registration.** This prevents physically impossible primitive combinations from being registered, ensuring catalog integrity.

**Hard constraints (automatic rejection):**

1. **Axiom 1 (Cyclic Closure)**: Cyclic self-complementary imscriptions (T_⋈/P_±) cannot have low fidelity (ƒ_ì)
   - *Rationale*: Cyclic closure amplifies fidelity through cooperativity
   - *Example rejection*: `Þ_ò + Φ_} + ƒ_ì` → rejected

2. **Axiom 4 (Sequential Grammar)**: Sequential grammar (Γ_→) requires temporal (D_∞) or catalytic (R_‡) dimension
   - *Rationale*: Ordered recognition requires state change mechanism
   - *Example rejection*: `Ð_C + Ř_superset + ɢ_seq` → rejected
   - *Example acceptance*: `Ð_infinity + Ř_superset + ɢ_seq` → accepted (has temporal dimension)

**Soft constraints (flagged for review):**
- Axiom 2 (Local Grammar Barrier)
- Axiom 3 (Cooperative Induction)
- Axiom 5 (Criticality)

imscriptions with soft axiom violations are registered but flagged in metadata:
```python
imscription.metadata["axiom_validated"] = True
imscription.metadata["axiom_violations"] = 1  # Count of soft violations
imscription.metadata["axiom_warnings"] = ["Axiom 2 violation detected - flagged for review"]
```

**Viewing axiom validation results:**
```python
for result in results:
    if result.validation_result == ValidationResult.INVALIÐ_CHEMISTRY:
        if "AXIOM" in result.reasoning:
            print(f"Axiom violation: {result.reasoning}")
    
    if result.imscription and result.imscription.metadata.get("axiom_warnings"):
        print(f"Warning: {result.imscription.name} - {result.imscription.metadata['axiom_warnings']}")
```

**References:**
- See `AXIOM_VALIDATION_FIX.md` for full technical details
- See `QUANTIG.md` Section IV for axiom definitions
- See `test_axiom_validation.py` for validation test suite

### Example Session

```bash
$ imscribe agents discover --focus "nitroso radicals" --cycles 20

======================================================================
AUTONOMOUS imscription DISCOVERY AGENT
======================================================================
Configuration:
  Max cycles: 20
  Max duration: 30.0 minutes
  Min confidence: 0.7
  Focus areas: ['nitroso radicals']
======================================================================

==================================================
CYCLE 1/20
==================================================

[✓] valid_novel
    Name: nitroso_radical_halogen_bonding_imscription_pair
    Notation: ⟨Ð_ß; Þ_linear; Ř_superset; Φ_F; ƒ_ð; Ç_-; Γ_β; ɢ_otimes; ⊙_ž; 1:1⟩
    Confidence: 80.0%

==================================================
CYCLE 2/20
==================================================

[✓] valid_novel
    Name: nitroso_radical_anion_π_imscription_pair
    Notation: ⟨Ð_ß; Þ_linear; Ř_superset; Φ_directional; ƒ_ż; Ç_-; Γ_β; ɢ_otimes; ⊙_ž; 1:1⟩
    Confidence: 90.0%

...

======================================================================
DISCOVERY RUN COMPLETE
======================================================================
Duration: 3.2 minutes
Cycles completed: 20
imscriptions registered: 15
Success rate: 75.0%

Catalog now contains 1,298 imscriptions
======================================================================
```

### Catalog Persistence

All imscriptions are automatically persisted to `~/.imscrbgrmr/catalog.json`:

- **Auto-save**: After each registration
- **Auto-load**: On startup
- **Permanent**: Survives across sessions

```python
from imscrbgrmr import global_catalog

# Catalog persists across runs
print(f"Catalog contains {len(global_catalog)} imscriptions")

# Access auto-discovered imscriptions
auto_imscriptions = [
    s for s in global_catalog._imscriptions.values()
    if s.metadata.get('auto_discovered')
]
print(f"Auto-discovered: {len(auto_imscriptions)}")
```

## 11. Integration with AjintK Multi-Agent Framework

Imscribing Grammar is built on top of the AjintK multi-agent framework, allowing for complex, distributed chemical reasoning.

### 11.1. Orchestrator Usage

The `AgentOrchestrator` manages multiple agents and their communication.

```python
from framework.orchestrator import AgentOrchestrator
from imscrbgrmr.domains.molecular import MolecularImscriptionAgent

orchestrator = AgentOrchestrator()
orchestrator.register_agent("molecular_expert", MolecularImscriptionAgent())

# Run a task through the orchestrator
result = asyncio.run(orchestrator.run_agent(
    "molecular_expert",
    task="Analyze bond disconnections for caffeine"
))
```

## 12. Advanced Topics and Troubleshooting

### 12.1. Best Practices

*   **Registry over Raw Objects**: Always prefer registering imscriptions in the `global_catalog` to enable cross-domain reasoning features.
*   **Fidelity Calibration**: Fidelity values should be calibrated against known experimental benchmarks (see `QUANTIG.md`).
*   **Domain Overlap**: When modeling complex materials like MOFs, use hybrid dimensionality imscriptions to capture both molecular and supramolecular constraints.
*   **AI Generation Confidence**: Review the confidence scores and reasoning from AI-generated imscriptions before using them in critical analyses.

### 12.2. Troubleshooting

*   **`NameError: name 'cls' is not defined`**: Ensure you are using the latest version of the framework where enum property references have been fixed.
*   **`ValueError: mutable default ... not allowed`**: Occurs if dataclasses use shared dicts. Use `default_factory` for all dictionary fields.
*   **Integration Test Failures**: Run `python3 test_integration.py` to diagnose issues. Check your Python version (3.12+ recommended).
*   **AI Generation Errors**: Ensure API keys are set for your chosen provider. If generation fails, try a different provider with `--provider qwen` or `--provider google`.

---

## Section 7. Protocol Suite (v0.3.0)

### 7.1. IΓ_PERTURBATION

Controlled perturbation of the 10-primitive tuple to identify load-bearing vs. decorative primitives.
Full spec: `IΓ_PERTURBATION.md`.

#### Python API

```python
from imscrbgrmr import PerturbationEngine
from imscrbgrmr.registry import global_catalog

dimer = global_catalog.get("carboxylic_acid_dimer")
engine = PerturbationEngine()

# Full primitive Jacobian — all primitives ±1 tier
jac = engine.sweep_all(dimer, delta_g=-12.0)
print(f"Baseline ξ_CP: {jac.baseline_xi_CP:.3f} nats")
print(f"Most sensitive: {jac.most_sensitive.primitive_name}")

for pr in sorted(jac.results, key=lambda x: abs(x.delta_xi_CP), reverse=True):
    print(f"  {pr.primitive_name:<20}  {pr.delta_xi_CP:+.4f} nats  [{pr.sensitivity}]")

# Fault injection — single points of failure
fault = engine.fault_injection(dimer, delta_g=-12.0)
print(f"Robust: {fault['system_robust']}")
print(f"Single points of failure: {fault['single_points_of_failure']}")

# Path to target ξ_CP
path = engine.find_path_to_target(dimer, delta_g=-12.0, target_xi_CP=7.5, optimize_primitives=["F", "K"])
print(f"Target reached: {path['target_reached']}")
```

#### CLI

```bash
# Full Jacobian sweep
imscribe perturb sweep carboxylic_acid_dimer --delta-g -12.0

# JSON output
imscribe perturb sweep carboxylic_acid_dimer --delta-g -12.0 --format json

# Fault injection
imscribe perturb fault-injection carboxylic_acid_dimer --delta-g -12.0

# Path to target
imscribe perturb pathfind carboxylic_acid_dimer --delta-g -12.0 --target 7.5 --optimize F,K
```

**Sensitivity labels**: `CRITICAL` (Δξ_CP ≥ 3.0 nats), `HIGH` (≥ 1.5), `MEDIUM` (≥ 0.5), `LOW` (< 0.5).

---

### 7.2. IΓ_TRAJECTORY

Encode D_∞ systems as ordered step sequences; validate Axiom 6 (temporal grounding) and kinetic accessibility.
Full spec: `IΓ_TRAJECTORY.md`.

#### Python API

```python
from imscrbgrmr import TemporalImscriptionAgent, Imscription
from imscrbgrmr.models import (
    Dimensionality, Topology, RecognitionMode, Polarity,
    Fidelity, KineticCharacter, Granularity, InteractionGrammar,
)

agent = TemporalImscriptionAgent("proline_aldol_cycle")

# Build step imscriptions (all must have D_∞ or R_‡ for Axiom 4)
base = dict(
    dimensionality=Dimensionality.TEMPORAL,
    topology=Topology.CYCLIC_BOWTIE,
    recognition_mode=RecognitionMode.DYNAMIC_CATALYTIC,
    polarity=Polarity.DONOŘ_ACCEPTOR,
    granularity=Granularity.MESOSCALE,
    interaction_grammar=InteractionGrammar.SELECTIVE_SEQ,
)
enamine  = Imscription(name="enamine_formation",  fidelity=Fidelity.HIGH,   kinetic_character=KineticCharacter.FAST,     **base)
ts       = Imscription(name="c_c_bond_form",       fidelity=Fidelity.MEDIUM, kinetic_character=KineticCharacter.MODERATE, **base)
hydrol   = Imscription(name="hydrolysis_reset",    fidelity=Fidelity.HIGH,   kinetic_character=KineticCharacter.FAST,     **base)

agent.add_step(enamine,  "enamine_formation",  delta_g=-15.0)
agent.add_step(ts,       "c_c_bond_form",       delta_g_ddagger=97.0)   # rate-determining
agent.add_step(hydrol,   "hydrolysis_reset",    delta_g=-25.0, is_reset=True)

result = agent.validate_all()
print(f"Valid: {result.overall_valid}")
print(f"Axiom 6 satisfied: {result.axiom6_satisfied}")
print(f"Reset step: {result.reset_step}")
print(f"Kinetic traps: {result.kinetic_traps}")
print(f"Full cycle candidacy: {result.full_cycle_candidacy:.3f}")
```

#### CLI

```bash
# Validate a named set of steps (must exist in catalog)
imscribe trajectory validate --steps enamine_formation,c_c_bond_form,hydrolysis_reset --reset hydrolysis_reset

# Criticality scan per step
imscribe trajectory criticality --steps enamine_formation,c_c_bond_form,hydrolysis_reset --varma-probe
```

**Key checks**:
- **Axiom 4** (per step): must have `D_∞` or `R_‡` (dynamic catalytic)
- **Axiom 6** (cycle): reset step returns system to Σ_t0 (keyword or `is_reset=True`)
- **Ç_Ù / ΔG‡ > 100 kJ/mol**: flagged in `kinetic_traps`

---

### 7.3. IΓ_ENSEMBLER

Multi-imscription composition: pairwise compatibility, emergent properties, system ξ_CP.
Full spec: `IΓ_ENSEMBLER.md`.

#### Python API

```python
from imscrbgrmr import EnsembleCatalog

ensemble = EnsembleCatalog()
ensemble.add("carboxylic_acid_dimer")    # by catalog name
ensemble.add("proline_aldol_cycle")
ensemble.add("nitroso_radical_cucurbituril_anion_rotaxane_imscription")

# Pairwise compatibility + emergent properties
report = ensemble.check_pairwise()
print(f"Consistent: {report.is_consistent}")
print(f"Score: {report.consistency_score:.0%}")

for entry in report.pairwise_matrix:
    print(f"  {entry.component_a} ↔ {entry.component_b}: {entry.result}")

for ep in report.emergent_properties:
    print(f"  {ep.property_name}: detected={ep.detected}")

for axiom, status in report.axiom_propagation.items():
    print(f"  {axiom}: {status}")

# System-level ξ_CP with interface overhead
result = ensemble.compute_system_xi_CP(delta_g_assembly=-85.0, interface_overhead_bits=1.5)
print(f"ξ_CP system: {result['xi_CΦ_system_nats']:.4f} nats [{result['efficiency_tier']}]")
```

#### CLI

```bash
# Pairwise matrix + emergent properties
imscribe ensemble check --components carboxylic_acid_dimer,proline_aldol_cycle

# Criticality probe across ensemble
imscribe ensemble probe --criticality --components carboxylic_acid_dimer,proline_aldol_cycle

# System thermodynamics
imscribe ensemble thermo --components carboxylic_acid_dimer,proline_aldol_cycle --delta-g-assembly -85.0
```

**Emergent properties detected**:
- `Emergent Criticality` — ensemble degeneracy_strength > individual average + 0.10 and ≥ 0.40
- `Granularity Amplification (G_ב → G_ג)` — ≥3 G_ב components with Axiom 3 superlinear induction
- `Interface Fidelity Degradation` — incompatible pair(s) with mean F > 0.5

**Interface overhead rule**: each additional bit of overhead adds `ln(2) ≈ 0.693 nats` to ξ_CP via Landauer identity.

---

### 7.4. IΓ_RETRODESIGN

Constraint-directed retrosynthetic decomposition: recursive axiom-pruned tree.
Full spec: `IΓ_RETRODESIGN.md`.

#### Python API

```python
from imscrbgrmr import RetrodesignEngine

engine = RetrodesignEngine()

# Decompose by catalog name
tree = engine.decompose(
    "carboxylic_acid_dimer",
    max_depth=3,
    prune_axioms=[1, 2, 4, 6],
)

print(f"Valid decompositions : {len(tree.valid_leaves)}")
print(f"Pruned branches      : {tree.pruned_count}")
print(f"Valid imscription set    : {tree.valid_imscription_set}")

# Decompose by notation string (9-primitive ⟨...⟩ format)
target = ImscriptionNotation.from_string(
    "⟨{Ð_C, Ð_infinity}; Þ_cage; Ř_superset+ddagger; "
    "Φ_F; ƒ_ð; Ç_W; Γ_γ; ɢ_and(SELECTIVE); ⊙_ž⟩"
)
# or pass the string directly
tree2 = engine.decompose(notation_str, max_depth=2)

# Walk the full tree
def walk(node, depth=0):
    status = "PRUNED" if node.is_pruned else ("LEAF" if node.is_leaf else "node")
    print("  " * depth + f"[{status}] {node.branch_name}")
    for v in node.violations:
        print("  " * depth + f"  ⚠ Axiom {v.axiom}: {v.condition}")
    for child in node.children:
        walk(child, depth + 1)

walk(tree.root)
```

#### CLI

```bash
# Decompose by catalog name
imscribe retrodesign carboxylic_acid_dimer

# Custom depth and axiom set
imscribe retrodesign carboxylic_acid_dimer --max-depth 4 --prune-axioms 1,4,6

# Decompose by notation string
imscribe retrodesign "⟨{Ð_C, Ð_infinity}; Þ_cage; Ř_superset; Φ_F; ƒ_ð; Ç_W; Γ_γ; ɢ_and(SELECTIVE); ⊙_ž⟩"

# JSON output
imscribe retrodesign carboxylic_acid_dimer --format json
```

**Pruning rules**:
| Axiom | Name | Condition |
|-------|------|-----------|
| 1 | Fidelity Floor | `T_⋈ + P_± + F_ℓ → PRUNE` |
| 2 | Propagation Barrier | sub-tuple claims `G_ℵ` but lacks `Γ_∨` or `Þ_6` → PRUNE |
| 4 | Grammar Mismatch | `Γ_→` without `D_∞` or `R_‡` → PRUNE |
| 6 | Grounding Fail | `D_∞` without reset mechanism → FLAG |

---

### 7.5. Demo Script

```bash
python examples/demo_protocols.py
```

Runs all four protocols in sequence with calibrated reference values:
- Protocol 1: `carboxylic_acid_dimer` ΔG = −12.0 kJ/mol → ξ_CP ≈ 6.81 nats, Granularity most sensitive (Δξ = −0.60 nats, MEDIUM)
- Protocol 2: `proline_aldol_cycle` 3-step cycle, all continuity checks PASS, Axiom 6 satisfied, reset at `hydrolysis_reset`
- Protocol 3: 3-component ensemble (molecular + temporal + mechanical), Interface Fidelity Degradation detected, system ξ_CP ≈ 9.81 nats [LOW with 1.5-bit overhead]
- Protocol 4: `carboxylic_acid_dimer` → 3 valid leaves, 0 pruned; `proline_aldol_cycle` → 1 valid leaf, 2 pruned (Axiom 4 enforced)

---
*For more detailed information on the underlying theory, refer to **QUANTIG.md**.*

---

## 8. Tuple Algebra and Compositional Design (v0.3.2)

The ten-tuple is a typed mathematical object. `imscrbgrmr/algebra.py` implements the full algebra over the tuple space. All six operations are exposed via CLI and Python API.

### 8.1. `imscribe meet` — Lattice Meet (Greatest Lower Bound)

```bash
imscribe meet imscription_A imscription_B [--format text|json]
```

Computes the componentwise minimum: for ordered primitives (F, K, G) takes the lower value; for categorical primitives (D, T, R, P, Γ, Φ, S) returns the shared value or **CONFLICT** if they differ. The result is the "most conservative valid imscription below both inputs" — the guaranteed design floor of any system that must satisfy both.

**Example:**
```bash
imscribe meet Dithiadiazolyl_Phthalocyanine_Columnar_Stacking_Imscription \
            nitroso_radical_redox_imscription_pair
```

Output:
```
Meet: Dithia ⊓ nitroso
┌────────┬────────────────┬────────────────┬─────────────────┐
│ Prim   │ Dithia         │ nitroso        │ Result          │
├────────┼────────────────┼────────────────┼─────────────────┤
│ D      │ Ð_molecular    │ Ð_molecular    │ Ð_molecular     │
│ T      │ Þ_cyclic       │ Þ_cyclic       │ Þ_cyclic        │
│ R      │ Ř_non_covalent │ Ř_non_covalent │ Ř_non_covalent  │
│ F      │ ƒ_ż         │ ƒ_ð          │ ƒ_ð  ▼        │
│ K      │ Ç_W          │ Ç_-         │ Ç_- ▼ (wait) │
│ G      │ Γ_γ        │ Γ_β         │ Γ_β ▼        │
│ Phi    │ ⊙_ž        │ ⊙_ž        │ ⊙_ž         │
└────────┴────────────────┴────────────────┴─────────────────┘
Result: ⟨D_∧; T_⋈; R_⊇; P_...;  ƒ_ð; Ç_-; G_ב; Γ_...; Φ_sub; S⟩
```

CONFLICT primitives are shown in red. A meet with no conflicts means the two imscriptions are mutually substitutable within the partial order.

**Python API:**
```python
from imscrbgrmr.algebra import meet
result = meet(s1, s2)
print(result.to_notation())   # unified notation
print(result.conflicts)       # list of conflicted primitive names
print(result.is_valid)        # True if no CONFLICT sentinels
```

---

### 8.2. `imscribe join` — Lattice Join (Least Upper Bound)

```bash
imscribe join imscription_A imscription_B [--format text|json]
```

Componentwise maximum: for ordered primitives takes the higher value; for categoricals, shared value or CONFLICT. The result is the "minimal imscription that subsumes both" — the minimal ceiling of the design space spanned by the two inputs.

**Key use case:** `join` is how to find the minimal upgrade that satisfies both of two design targets. If `join(s1, s2)` has no CONFLICTs, there exists a valid imscription above both.

**Criticality rule:** $\Phi_{\text{ctyogh}}$ dominates in both meet and join. If either input has $\Phi_{\text{ctyogh}}$, the output has $\Phi_{\text{ctyogh}}$. This encodes the physical fact that criticality is not a property that can be averaged away.

**Python API:**
```python
from imscrbgrmr.algebra import join
result = join(s1, s2)
```

---

### 8.3. `imscribe path` — Valid-Swap Path Search

```bash
imscribe path SOURCE DESTINATION [--max-hops 5] [--xi-tolerance 2.0]
```

BFS over the directed valid-swap graph. Edges exist where `HotSwapEngine` returns APPROVED or CONDITIONAL. Restricted to the same $\{D, T\}$ cluster (cross-domain edges always fail the HotSwap D/T exact-match requirement). Accumulates $|\Delta\xi_{CP}|$ along the path; terminates if the cumulative cost exceeds `--xi-tolerance`.

**Important:** The path graph is **asymmetric**. `path(A → B)` may succeed while `path(B → A)` fails. This happens whenever B has lower F than A — the F-floor constraint blocks downgrade edges. This is correct behavior: a swap is not the same operation as its reverse.

**Example:**
```bash
# This succeeds (1 hop, Δξ = +0.312 nat):
imscribe path Dithiadiazolyl_Phthalocyanine_Columnar_Stacking_Imscription \
            nitroso_radical_redox_imscription_pair

# This fails (F downgrade blocked):
imscribe path nitroso_radical_redox_imscription_pair \
            Dithiadiazolyl_Phthalocyanine_Columnar_Stacking_Imscription
```

Output (success):
```
Path: Dithia → nitroso
Hop 1: Dithia → nitroso   Δξ = +0.312 nat   [APPROVED]
Total Δξ_CP: 0.312 nat   Hops: 1
```

**Python API:**
```python
from imscrbgrmr.algebra import find_path
from imscrbgrmr.registry import global_catalog

path = find_path(s1, s2, catalog=global_catalog, max_hops=5, xi_tolerance=2.0)
if path.found:
    for hop in path.hops:
        print(f"  {hop.source.name} → {hop.dest.name}  Δξ = {hop.delta_xi:+.3f}")
```

---

### 8.4. `imscribe tensor` — Ensemble Prediction (Tensor Product)

```bash
imscribe tensor imscription_A imscription_B [--lambda 0.5] [--format text|json]
```

Computes the effective primitive tuple of a two-component assembly. Composition rules:

| Primitive | Rule | Physical meaning |
|---|---|---|
| D | Set union | Ensemble spans all dimensions of components |
| T | Max (promote) | Most complex topology governs assembly |
| R | Promote (dynamic > static) | Dominant interaction governs propagation |
| P | Donor-acceptor if both present | Mixed polarity creates directional system |
| **F** | **Min (bottleneck)** | Weakest fidelity limits the ensemble |
| **K** | **Min (bottleneck)** | Slowest step governs kinetics |
| G | Max | Largest-scale control propagates up |
| Γ | AND-composition | Partner requirements are additive |
| Φ | Φ_c propagates | Criticality is contagious |
| S | Product | Combined assembly has product valency |

**ξ correction:** $\xi_{\text{ens}} = \xi_1 + \xi_2 - \lambda \cdot I(s_1; s_2)$, where $I(s_1; s_2)$ is the mutual information between tuple vectors (shared primitive values), and $\lambda$ is the overlap discount (default 0.5).

**Important consequence:** If `tensor(s1, s2)` drops F to $F_{\text{dh}}$, a subsequent `criticality_lift` on the result will be BLOCKED — the F floor is correctly enforced without any explicit guard in the downstream pipeline.

**Python API:**
```python
from imscrbgrmr.algebra import tensor
result = tensor(s1, s2, lambda_=0.5)
print(result.to_notation())     # effective tuple
print(result.xi_ensemble)       # effective ξ_CP
print(result.overlap_discount)  # λ · I(s₁;s₂) correction
```

---

### 8.5. `imscribe lift` — Natural Transformation (Cross-Domain Migration)

```bash
imscribe lift imscription_NAME TARGET [--format text|json]
```

where `TARGET` is one of: `temporal`, `spatial`, `critical`, `molecular`.

Applies a primitive-rewriting map that migrates the imscription to a new domain while preserving as much structure as possible. Output shows a side-by-side diff of changed primitives.

**Available lifts:**

| Target | Primitive changes | Guard condition |
|---|---|---|
| `temporal` | D_∧→D_∞, R→R_‡, Ç_-→Ç_W, Γ→Γ_→(SEQUENTIAL) | None |
| `spatial` | D_∧→D_△, T→T_□ if not spatial, G_ב→G_ג | None |
| `critical` | Φ_sub→Φ_c, G→G_ℵ | **F ≥ F_ℏ required** (Axiom 5) |
| `molecular` | D_∞→D_∧, R_‡→R_⊆, Γ_→→Γ_∧(SELECTIVE) | None (forgetful) |

**Criticality lift guard (Axiom 5 enforcement):** If F < F_ℏ, the lift is BLOCKED with explanation. A imscription must have high thermodynamic fidelity to carry a reliable criticality signature.

**Example:**
```bash
imscribe lift Dithiadiazolyl_Phthalocyanine_Columnar_Stacking_Imscription critical
```

Output:
```
Lift: critical — Dithia
Changed primitives:
  Φ: ⊙_ž → ⊙_ÿ
  G: Γ_γ → Γ_ʔ
Result: ⟨D_∧; T_⋈; R_⊇; P_+; F_ℏ; Ç_W; G_ℵ; Γ_∧(SPECIFIC); Φ_c; 1:1⟩
Note: Axiom 6 injection: temporal lift requires closed-cycle grounding before assembly.
```

**Python API:**
```python
from imscrbgrmr.algebra import criticality_lift, lift_to_temporal, lift_to_spatial, project_to_molecular

result = criticality_lift(s)
if result.blocked:
    print(f"BLOCKED: {result.block_reason}")
else:
    print(result.result_imscription.to_notation())
    for warning in result.warnings:
        print(f"  Warning: {warning}")
```

---

### 8.6. `imscribe pipeline` — Composable Design Pipeline

```bash
imscribe pipeline STARÞ_imscription --step STEP [--step STEP ...]
```

A composable pipeline that chains algebra operations with automatic ξ_CP threading and fail-fast logging. Implements a Writer+Maybe monad: each step carries the accumulated cost (Writer) and continues from the last valid state even on BLOCKED steps (soft Maybe).

**Step syntax:**
```
op:argument[:key=value[:key=value...]]
```

| Step | Syntax | Operation |
|---|---|---|
| meet | `meet:imscription_name` | Lattice meet with named imscription |
| join | `join:imscription_name` | Lattice join with named imscription |
| tensor | `tensor:imscription_name` or `tensor:imscription_name:lambda=0.3` | Tensor product |
| lift | `lift:temporal` / `lift:spatial` / `lift:critical` / `lift:molecular` | Natural transformation |
| path | `path:target_name` or `path:target_name:xi_tolerance=1.5` | Path search to target |

**Full example:**
```bash
imscribe pipeline Dithiadiazolyl_Phthalocyanine_Columnar_Stacking_Imscription \
  --step join:nitroso_radical_redox_imscription_pair \
  --step lift:critical \
  --step path:Varma_imscription:xi_tolerance=1.5
```

Output:
```
Pipeline trace:
  Start:  Dithia     ⟨...; F_ℏ; Ç_W; G_ג; ...; Φ_sub; 1:1⟩
──────────────────────────────────────────────────────────────
  Step 1: join(nitroso)
    F: ƒ_ð → ƒ_ż (max)   K: Ç_- → Ç_W   G: Γ_β → Γ_γ
    Δξ_CP = +0.519 nat       [PASS]
  Step 2: lift(critical)
    Φ: ⊙_ž → ⊙_ÿ   G: Γ_γ → Γ_ʔ
    F = ƒ_ż ≥ ƒ_ż   ✓ eligibility gate passed
    Δξ_CP = +0.000 nat    [PASS]
  Step 3: path(Varma_imscription, tol=1.5)
    Hop 1: ... → Varma   Δξ = +0.847 nat   [APPROVED]
    Δξ_CP = +0.847 nat    [PASS]
──────────────────────────────────────────────────────────────
  Final:  ⟨...; F_ℏ; Ç_W; G_ℵ; ...; Φ_c; 1:1⟩
  Total Δξ_CP: 1.366 nat   Steps: 3   Blocked: 0
```

**Python API (direct monadic chaining):**
```python
from imscrbgrmr.algebra import DesignPipeline
from imscrbgrmr.registry import global_catalog

nitroso = global_catalog["nitroso_radical_redox_imscription_pair"]
varma   = global_catalog["Varma_imscription"]

result = (
    DesignPipeline
    .start(dithia)
    .join(nitroso)
    .lift("critical")
    .path("Varma_imscription")
    .result()
)

result.print_trace()
print(f"Total Δξ_CP: {result.total_delta_xi:.3f} nat")
print(f"Final tuple: {result.current_imscription.to_notation()}")
print(f"Blocked steps: {result.blocked_count}")
```

**Pipeline semantics:**
- **Writer effect**: `total_delta_xi` accumulates across all steps.
- **Maybe effect**: BLOCKED steps are logged but do not terminate the pipeline. The pipeline continues from the last successfully transformed imscription.
- **Fail condition**: A step that **raises an exception** (e.g., imscription not found, BFS graph unreachable) terminates the pipeline with an ERROR status distinct from BLOCKED.

**Behavioral verification:**
1. **F-bottleneck propagation**: `tensor(A, B)` dropping F to ƒ_ð → subsequent `lift:critical` is BLOCKED without any explicit guard needed.
2. **Path asymmetry**: `path:nitroso` from Dithia succeeds (F upgrade direction); `path:Dithia` from nitroso fails (F downgrade blocked).
3. **Join-enables-path**: `join(nitroso)` upgrades F to ƒ_ż → `path:Varma` at Δξ = +0.847 nat succeeds where it would have failed from the lower-F starting point.

### 8.7. `imscribe distance` — Tuple Distance (v0.4.0)

```bash
imscribe distance imscription_A imscription_B [--directed] [--format text|json]
```

Computes the weighted Hamming-style distance between two imscription tuples in the eleven-primitive space. By default reports the **symmetric** distance d(A, B) = d(B, A). With `--directed`, also reports the asymmetric directed distances d(A→B) and d(B→A) and the asymmetry index.

**Primitive weights** (default):

| Primitive | Weight | Notes |
|-----------|--------|-------|
| D | 1.5 | Dimensionality — highest weight (structural backbone) |
| T | 1.2 | Topology |
| R | 1.0 | Reactivity |
| P | 0.8 | Polarity |
| F | 1.0 | Fidelity (with asymmetric F-floor penalty) |
| K | 0.6 | Kinetics |
| G | 0.9 | Granularity |
| Γ | 0.7 | Grammar |
| Φ | 1.1 | Criticality phase |
| S | 0.08 | Stoichiometry |
| Ω | 0.7 | Topological protection index (when set) |

**Example:**
```bash
imscribe distance photon electron
```

**Example output (text):**
```
Distance: photon ↔ electron
  d(sym) = 3.20
  d(photon → electron) = 3.05
  d(electron → photon) = 3.35
  Asymmetry = 0.30

  Primitive breakdown:
    D    0.00   D_∞ ↔ D_∞            [match]
    T    1.20   T_× ↔ T_|            [mismatch]
    R    0.00   Ř_irr ↔ Ř_irr        [match]
    P    0.80   P_γ ↔ Φ_e            [mismatch]
    F    0.00   F_ℏ ↔ F_ℏ            [match]
    K    0.00   Ç_- ↔ Ç_-      [match]
    G    0.90   G_ℵ ↔ G_ℵ            [match]
    Γ    0.00   Γ_⊗ ↔ Γ_⊗            [match]
    Φ    0.00   Φ_sub ↔ Φ_sub        [match]
    S    0.30   None ↔ None          [match]
    Ω    —      (not set on either)
```

**JSON output** (`--format json`):
```json
{
  "imscription_a": "photon",
  "imscription_b": "electron",
  "d_sym": 3.20,
  "d_a_to_b": 3.05,
  "d_b_to_a": 3.35,
  "asymmetry": 0.30,
  "primitives": {
    "T": {"weight": 1.2, "match": false},
    "P": {"weight": 0.8, "match": false}
  }
}
```

**Python API:**
```python
from imscrbgrmr.algebra import tuple_distance

d = tuple_distance(imscription_a, imscription_b)
print(f"Distance: {d:.3f}")
```

**Quantum particle distance results** (v0.4.0 playground):

| Pair | d(sym) | Dominant mismatch |
|------|--------|------------------|
| proton ↔ electron | 1.50 | P (charge sign) |
| spin ↔ qubit | 2.10 | T + K (spatial ↔ linear; trap ↔ slow) |
| photon ↔ qubit | 3.80 | T + P + K |
| proton ↔ spin | 6.00 | Max separation (T + P + K + G stacking) |

---

### 8.9. Combined Workflow Example

```bash
# Step 0: Measure primitive-space separation
imscribe distance Dithia nitroso --directed   # d(sym)=2.10; asymmetry=0.40

# Step 1: Check whether two imscriptions are lattice-compatible
imscribe meet Dithia nitroso         # identifies F/K/G gaps
imscribe join Dithia nitroso         # identifies minimal common ceiling

# Step 2: Can we swap directly?
imscribe hotswap Dithia nitroso      # HotSwap check
imscribe path Dithia nitroso         # finds 1-hop path, Δξ = +0.312 nat

# Step 3: What does the ensemble look like?
imscribe tensor Dithia nitroso       # effective tuple (F→min→ƒ_ð, K→min→Ç_W)

# Step 4: Can we lift the joined ensemble to critical?
imscribe pipeline Dithia \
  --step join:nitroso \
  --step lift:critical \
  --step path:Varma:xi_tolerance=1.5
# → join restores ƒ_ż → criticality lift passes → path to Varma succeeds
```

---

### 8.10. DesignPipeline Python API

```python
from imscrbgrmr.algebra import DesignPipeline, global_catalog

# Load starting imscription
start = global_catalog.get("proline_aldol_cycle")

# Build a multi-stage pipeline
pipeline = (
    DesignPipeline()
    .start(start)
    .meet("amide_dimer")              # lattice meet
    .join("carboxylic_acid_dimer")    # lattice join
    .tensor("nitroso_radical_redox_imscription_pair", lambda_=0.5)
    .lift("critical")                 # natural transformation
    .path("soai_pyrimidyl_autocatalytic_cycle", xi_tolerance=2.0)
)

# Execute and get results
result = pipeline.result()

# Inspect results
print(f"Final imscription: {result.current_imscription.name}")
print(f"Total Δξ_CP: {result.total_delta_xi:+.3f} nat")
print(f"Steps: {len(result.steps)}, Blocked: {result.blocked_count}")

# Print full trace
result.print_trace()
```

---

## 9. Design Scripts (`.syn` DSL) — Complete Reference

**Version:** 0.4.1 (Phase 3a — Monadic Foundation · Molecular Domain Catalog)
**Total Scripts:** 20 (Batch 1: 01-05 + corrected; Batch 2: 06-16)
**Success Rate:** 18/20 (90%) — 2 intentional F-floor pedagogical demonstrations (01, 04)

### 9.1. Quick Reference Table

| Script | Status | Δξ_CP (nat) | Key Demonstration |
|--------|--------|-------------|-------------------|
| **Batch 1** | | | |
| `01_soai_criticality_path.syn` | ❌ Blocked (pedagogical) | 0.000 | F-floor gate: proline(ƒ_ð) cannot lift to Φ_c |
| `01b_soai_criticality_corrected.syn` | ✅ **SUCCESS** | 0.000 | Factor 7 fires; Φ_c lift; meet preserves Φ_c |
| `02_tensor_ensemble_design.syn` | ⚠️ Partial | 13.624 | Tensor fidelity bottleneck |
| `02b_tensor_ensemble_corrected.syn` | ✅ **SUCCESS** | 13.624 | Tensor → join → lift |
| `03_retrosynthetic_meet_join.syn` | ✅ **SUCCESS** | 0.000 | meet(F_ℏ, ƒ_ð)→ƒ_ð; join→F_ℏ |
| `04_hybrid_spatial_temporal.syn` | ❌ Blocked (pedagogical) | 16.802 | Tensor succeeds; ƒ_ð bottleneck blocks Φ_c lift |
| `04b_hybrid_spatial_temporal_corrected.syn` | ✅ **SUCCESS** | 15.425 | D_△∞ hybrid; Axiom 6 pass; lift |
| `05_varma_probe_validation.syn` | ⚠️ Partial | 0.000 | Varma probe, path limits |
| `05b_varma_probe_corrected.syn` | ✅ **SUCCESS** | 0.000 | Varma + idempotent join |
| **Batch 2** | | | |
| `06_catalytic_cycle_optimization.syn` | ✅ **SUCCESS** | 0.962 | 1-hop path + lift; total cost < 5.0 nat |
| `07_supramolecular_cage_assembly.syn` | ✅ **SUCCESS** | 27.518 | Sequential tensor ×2 |
| `08_retrodesign_search.syn` | ✅ **SUCCESS** | 0.000 | T_\| cluster navigation |
| `09_cross_domain_analogy.syn` | ✅ **SUCCESS** | 0.000 | Supramolecular analogy |
| `10_hierarchical_ensemble.syn` | ✅ **SUCCESS** | 13.016 | **tensor(CH₃⁻, CH₃⁺); MI discount 7.100 nat** |
| `11_criticality_ensemble_validation.syn` | ✅ **SUCCESS** | 0.000 | Full Varma + Axiom 6 |
| `12_thermodynamic_efficiency.syn` | ✅ **SUCCESS** | 12.577 | crown(ƒ_ð) ⊗ CB[n](F_ℏ) → ƒ_ð; MI 5.698 nat |
| `13_multi_hop_path_discovery.syn` | ✅ **SUCCESS** | 0.000 | Extended path search |
| `14_complex_strategy_composition.syn` | ✅ **SUCCESS** | 0.000 | lift→BLOCKED; mplus→join(F_ℏ)→lift Φ_c |
| `15_dna_base_pair_lattice.syn` | ✅ **SUCCESS** | 0.000 | Biological H-bond systems |
| `16_mof_inspired_network.syn` | ✅ **SUCCESS** | 13.741 | cryptand ⊗ CB[n] → Þ_cage, F_ℏ; MI 8.588 nat |

### 9.2. Running Design Scripts

```bash
# Run a single design (text output)
imscribe run designs/03_retrosynthetic_meet_join.syn

# Run with JSON output and save
imscribe run designs/14_complex_strategy_composition.syn --format json --save result.json

# Dry-run (parse + validate without executing)
imscribe run designs/06_catalytic_cycle_optimization.syn --dry-run

# Override output format
imscribe run designs/10_hierarchical_ensemble.syn --format json
```

### 9.3. Featured Designs (Deep Dive)

#### Design 03: Retrosynthetic Meet/Join ✅

**Goal:** Demonstrate lattice operations on H-bonded dimers

**Result:** 5/5 steps, Δξ_CP = 0.000 nat

```
1. [PASS] ✓ meet(amide_dimer)  F: ƒ_ż ⊓ ƒ_ð → ƒ_ð
2. [ASSERÞ_PASS] ✓ topology == Þ_ò
3. [ASSERÞ_PASS] ✓ fidelity == ƒ_ð
4. [PASS] ✓ join(carboxylic_acid_dimer)  F: ƒ_ð ⊔ ƒ_ż → ƒ_ż
5. [ASSERÞ_PASS] ✓ fidelity == ƒ_ż
```

**Key Insights:**
- Meet/join form a lattice on ordered primitives (F, K, G)
- Categorical primitives (D, T, R, P, Γ) require exact match
- Zero thermodynamic cost (abstract algebraic transformations)

---

#### Design 10: Hierarchical Ensemble (Highest MI Discount) ✅

**Goal:** Multi-stage assembly with anion-cation pairing

**Result:** 7/7 steps, Δξ_CP = 12.424 nat, **MI discount = 8.283 nat**

```
1. [PASS] ✓ join(carbonyl)  F→ƒ_ð
2. [PASS] ✓ path(methyl_anion)  1 hop
3. [PASS] ✓ tensor(methyl_cation, λ=0.6)  Δξ=+12.424 nat  discount=8.283
4. [ASSERÞ_PASS] ✓ topology == Þ_linear
5. [ASSERÞ_PASS] ✓ fidelity == ƒ_ð
```

**Key Insights:**
- **Highest observed MI discount (8.283 nat)**
- Complementary charges maximize mutual information
- Without MI: cost would be 20.7 nat (actual: 12.4 nat)

---

#### Design 14: Complex Strategy Composition (Nested Or-Patterns) ✅

**Goal:** Three-level fallback chain for robust criticality ascent

**Result:** 9/9 steps, Δξ_CP = 0.362 nat

```
1. [BLOCKED] ✗ lift(critical)  F-floor not met
2. [PASS] ✓ mplus(fallback)  switching to fallback
3. [BLOCKED] ✗ join(redox_pair)  CONFLICT on R, P, Γ
4. [PASS] ✓ mplus(fallback)  switching to fallback
5. [PASS] ✓ path(redox_pair)  Δξ=+0.362 nat  1 hop
6. [PASS] ✓ lift(critical)  Φ: None → ⊙_ÿ
7. [ASSERÞ_PASS] ✓ criticality_phase == ⊙_ÿ
8. [ASSERÞ_PASS] ✓ phi_c_score > 0.3
9. [ASSERÞ_PASS] ✓ output.assert(steps <= 15)
```

**Key Insights:**
- **Nested or-patterns work flawlessly**
- Fallback chain: lift → join → path
- Final pathway cost: 0.362 nat (1-hop path + lift)
- Demonstrates robust error recovery in design pipelines

---

#### Design 11: Criticality Ensemble Validation ✅

**Goal:** Comprehensive Varma probe validation

**Result:** 8/8 steps, Δξ_CP = 0.000 nat

```
1. [PASS] ✓ lift(critical)  Φ: None → ⊙_ÿ
2. [ASSERÞ_PASS] ✓ phi_c_score > 0.3
3. [ASSERÞ_PASS] ✓ criticality_phase == ⊙_ÿ
4. [ASSERÞ_PASS] ✓ axiom6_satisfied
5. [PASS] ✓ join(self)  idempotent
6. [ASSERÞ_PASS] ✓ criticality preserved
7. [ASSERÞ_PASS] ✓ fidelity == ƒ_ż
8. [ASSERÞ_PASS] ✓ output.assert(criticality_ok == true)
```

**Key Insights:**
- All Varma probe predicates validated
- Axiom 6 temporal grounding satisfied
- Idempotent join preserves criticality phase

---

### 9.4. Thermodynamic Metrics Summary

| Operation Type | Typical Δξ_CP (nat) | Notes |
|----------------|---------------------|-------|
| `meet` / `join` | 0.000 | Abstract lattice ops |
| `lift` | 0.000 | Natural transformation |
| `path` (1 hop) | 0.000–0.500 | Same D/T cluster |
| `path` (multi-hop) | 0.500–2.000 | Cross-cluster |
| `tensor` (cage ⊗ bowl) | 12–16 | High cost ensemble |
| `tensor` (anion-cation) | 12–14 | **8.3 nat MI discount** |
| `tensor` (sequential ×2) | 25–30 | Accumulated cost |

**Note:** Lattice operations and lifts are abstract algebraic transformations (zero cost). Tensor products model physical co-assembly and carry ξ_CP predictions with mutual information discounts.

### 9.5. Constraint Enforcement (Floor Gates)

| Gate | Condition | Blocked If | Evidence |
|------|-----------|------------|----------|
| **F-floor** (criticality) | F ≥ ƒ_ż | F = ƒ_ð or ƒ_ì | Designs 01, 04 (pedagogical demos) |
| **D-floor** (criticality) | D = D_∞ OR G ≥ Γ_γ | D = Ð_C, G = Γ_β | Design 04 (after tensor bottleneck) |
| **D/T match** (path) | Same {D, T} cluster | D or T differs | Designs 08, 09, 13 |
| **Axiom 6** (temporal) | Reset block OR flux | D_∞ without grounding | Design 11 validates |

### 9.6. File Index

```
designs/
├── Batch 1 (01-05 + corrected)
│   ├── 01_soai_criticality_path.syn
│   ├── 01b_soai_criticality_corrected.syn
│   ├── 02_tensor_ensemble_design.syn
│   ├── 02b_tensor_ensemble_corrected.syn
│   ├── 03_retrosynthetic_meet_join.syn      ← Featured
│   ├── 04_hybrid_spatial_temporal.syn
│   ├── 04b_hybrid_spatial_temporal_corrected.syn
│   ├── 05_varma_probe_validation.syn
│   └── 05b_varma_probe_corrected.syn
├── Batch 2 (06-16)
│   ├── 06_catalytic_cycle_optimization.syn
│   ├── 07_supramolecular_cage_assembly.syn
│   ├── 08_retrodesign_search.syn
│   ├── 09_cross_domain_analogy.syn
│   ├── 10_hierarchical_ensemble.syn         ← Highest MI
│   ├── 11_criticality_ensemble_validation.syn
│   ├── 12_thermodynamic_efficiency.syn
│   ├── 13_multi_hop_path_discovery.syn
│   ├── 14_complex_strategy_composition.syn  ← Nested or
│   ├── 15_dna_base_pair_lattice.syn
│   └── 16_mof_inspired_network.syn
└── DESIGN_SUMMARY.md / DESIGN_SUMMARY_BATCH2.md

results/
└── [20 JSON result files]
```

### 9.7. Canonical Cross-Domain Demo (`TENSOŘ_OPΣ_DEMO.py`)

`TENSOŘ_OPΣ_DEMO.py` is the definitive worked-example document for all seven algebraic operations. It is structured for readers familiar with tensor mathematics (category theory, functional analysis, lattice algebra) and serves as both a tutorial and a validation suite.

**Run:**

```bash
# Run all 7 sections (18 examples total, ~2–3 min)
python TENSOŘ_OPΣ_DEMO.py

# Run a single section
python TENSOŘ_OPΣ_DEMO.py --section meet
python TENSOŘ_OPΣ_DEMO.py --section join
python TENSOŘ_OPΣ_DEMO.py --section tensor
python TENSOŘ_OPΣ_DEMO.py --section lift
python TENSOŘ_OPΣ_DEMO.py --section path
python TENSOŘ_OPΣ_DEMO.py --section pipeline
python TENSOŘ_OPΣ_DEMO.py --section decomp
```

**Section Map:**

| §  | Operation | Key Examples | Category-Theory Translation |
|----|-----------|-------------|----------------------------|
| 1 | **meet** | (1) Hv1 closed⊓open — Φ_c absorbing; (2) drug scaffold GLB; (3) AtHv1_silent⊓PsHv1 — Ç_Ù isolates | Product / Heyting GLB |
| 2 | **join** | (1) Hv1 cross-species LUB; (2) pharmacophore ceiling; (3) Cooper pair⊔TI surface — Ω_Z survives | Coproduct / F-floor ratchet |
| 3 | **tensor** | (1) electron⊗hole → exciton theorem (Þ_linear, no promotion); (2) Majorana⊗Majorana → Þ_braid special rule; (3) Cooper pair⊗phonon → full superconductor | Bifunctor; ξ_ens = ξ₁+ξ₂−λI |
| 4 | **lift** | (1) AtHv1_silent lift(critical) → BLOCKED (Ç_Ù gate); (2) molecular→temporal (loop-space functor Ω); (3) temporal→spatial (classifying space B(G)) | Natural transformation; +2.303 nat = ln10 |
| 5 | **path** | (1) AtHv1_silent→Hv1_human_open — 3-hop Kleisli geodesic; (2) 2GBI→HIF inhibitor scaffold migration; (3) magnon→Cooper pair — blocked (D/T gate) | Lawvere metric geodesic |
| 6 | **pipeline** | (1) Hv1 cross-species conservation (hv1_paper_reproduction.syn v6); (2) ImscriptionM do-notation chain; (3) fallback or-pattern (mplus) | WriterT+StateT+MaybeT Kleisli |
| 7 | **decomp** | (1) cofactor(Cooper pair, electron) → Ç_@+Γ_meso+Þ_ò+Φ_c; (2) principal_decomp Birkhoff atoms; (3) Heyting complement (satisfied=False anatomy) | Inverse bifunctor; Birkhoff theorem |

**Inline imscription definitions:** 16 imscriptions defined directly in the script — all registered to `global_catalog`. Includes: `Hv1_human_closed`, `Hv1_human_open`, `AtHv1_silent`, `AtHv1_primed`, `PsHv1_constitutive`, `2GBI_inhibitor`, `HIƒ_inhibitor`, `cooper_pair`, `majorana_fermion`, `TI_surface_state`, `phonon`, `magnon`, `electron`, `hole`, `GNF2_inhibitor`, `imatinib`.

**For `IΓ_LANG.md` readers:** §"Algebraic Operations Reference" in `IΓ_LANG.md` contains the formal specification; this demo is the executable companion.

---

### 9.8. Next Steps (Phase 3b)

1. **Refinement Types:** Move axiom checks to Pydantic v2 validators
2. **Predicate Expansion:** Add `kinetic_character`, `dimensionality`, `granularity` to assert grammar
3. **Path Search Optimization:** Add caching for repeated probe calls
4. **Strategy Library:** Build reusable strategy patterns for common design motifs
5. **Cost Optimization:** Implement heuristic search for minimum-cost pathways

---

## 10. LLM Tool Layer (v0.4.5)

`imscribe_tool.py` and `imscribe_agent.py` implement the Imscribing Grammar LLM tool layer — a structured interface that lets any tool-calling LLM interact with the live algebra without being able to hallucinate impossible chemistry. Every proposal is immediately rejected with a precise axiom trace if it fails.

### 10.1. `imscribe tool` — Single-Shot Tool Dispatch

```
imscribe tool OPERATION [OPTIONS]
```

Runs one ImscribeTool operation and prints the result (text or JSON).

**Operations and their required options:**

| Operation | Required options | Description |
|-----------|-----------------|-------------|
| `validate` | `--name NAME` | Full axiom validation on a catalog entry |
| `criticality` | `--name NAME` [--xi-r FLOAT] [--xi-tau FLOAT] | Varma Φ_c probe |
| `path` | `--src SRC --dst DST` [--max-hops INT] | HotSwap path search |
| `analogies` | `--name NAME` [--limit INT] | Nearest catalog neighbors |
| `distance` | `--a A --b B` | Symmetric + directed distances |
| `meet` | `--a A --b B` | Lattice meet (shared primitive floor + CONFLICT levers) |
| `generate` | `--description TEXT` [--name NAME] [--delta-g FLOAT] | Generate + validate from NL |

**Examples:**

```bash
# Pairwise distance
imscribe tool distance --a allosteric_domain --b active_site
# ● OK  operation=distance
# Distance: 5.400
# d(allosteric_domain→active_site) = 5.400
# d(active_site→allosteric_domain) = 5.400

# Criticality probe with correlation data
imscribe tool criticality --name allosteric_domain --xi-r 8.5 --xi-tau 1e10

# Find 3 nearest catalog neighbors
imscribe tool analogies --name condensate_liquid --limit 3

# HotSwap path with up to 8 hops
imscribe tool path --src condensate_liquid --dst condensate_gel --max-hops 8

# Lattice meet: find shared primitive floor and state-switching levers
imscribe tool meet --a condensate_liquid --b condensate_gel

# Generate and axiom-validate from natural language
imscribe tool generate --description "bivalent allosteric inhibitor" --name my_inhibitor

# JSON output
imscribe tool distance --a allosteric_domain --b active_site --format json
```

### 10.2. `imscribe design` — Autonomous LLM Design Agent

```
imscribe design --goal TEXT [OPTIONS]
```

Runs the autonomous `ImscriptionDesignAgent` loop: the LLM proposes a imscription encoding, every proposal is immediately axiom-validated, the Φ_c probe is applied, and the loop continues until convergence criteria are met or `--max-iterations` is reached.

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--goal TEXT` | (required) | Natural-language design goal |
| `--target NAME` | None | Catalog entry to require a HotSwap path to |
| `--phi-c-min FLOAT` | 0.70 | Minimum Φ_c score for convergence |
| `--xi-cp-max FLOAT` | 12.0 | Maximum ξ_CP (nats) for convergence |
| `--max-iterations INT` | 10 | Maximum LLM refinement iterations |
| `--model TEXT` | claude-sonnet-4-6 | Claude model ID |
| `--quiet` | False | Suppress per-iteration output |
| `--output PATH` | None | Save full iteration history as JSON |

**Examples:**

```bash
# Basic design run
imscribe design --goal "bivalent allosteric ABL inhibitor that closes Þ_perp to Þ_K gap"

# With target path requirement and tighter convergence
imscribe design \
  --goal "near-critical condensate scaffold with global coordination" \
  --target allosteric_domain \
  --phi-c-min 0.75 \
  --xi-cp-max 10.0 \
  --max-iterations 8

# Quiet mode, save JSON history
imscribe design \
  --goal "programmable DNA origami scaffold" \
  --quiet \
  --output design_history.json
```

**Convergence output (Rich table):**

```
 Iter  Status        Φ_c     ξ_CP   Stop reason
─────────────────────────────────────────────────────────
   1   ↻ iterating   0.62    13.1
   2   ↻ iterating   0.68    12.8
   3   ✅ CONVERGED  0.73    11.4   Φ_c=0.730 ≥ 0.70, ξ_CP=11.40 ≤ 12.0
```

### 10.3. Python API

```python
from imscribe_tool import ImscribeTool, ToolResponse

# All operations return ToolResponse dataclass
r: ToolResponse = ImscribeTool.distance("allosteric_domain", "active_site")
print(r.status)       # "ok"
print(r.distance)     # 5.4
print(r.to_json())    # full JSON

# Dispatch by operation name (used by agent)
r = ImscribeTool.dispatch("criticality", name="allosteric_domain", xi_r=8.5)

# Full agent loop
from imscribe_agent import ImscriptionDesignAgent, ConvergenceCriteria

agent = ImscriptionDesignAgent(
    goal="bivalent allosteric ABL inhibitor",
    criteria=ConvergenceCriteria(phi_c_min=0.70, xi_cp_max=12.0),
    model="claude-sonnet-4-6",
    verbose=True,
)
history = agent.run(max_iterations=10)

# Each record in history:
for r in history:
    print(r.iteration, r.phi_c_score, r.xi_cp, r.converged)
```

### 10.4. Using `imscription_TOOL_SCHEMA` with any LLM API

```python
from imscribe_tool import imscription_TOOL_SCHEMA, ImscribeTool

# Pass to Anthropic messages.create()
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[imscription_TOOL_SCHEMA],
    messages=[{"role": "user", "content": "Find the nearest analog to allosteric_domain"}],
)

# Dispatch incoming tool_use blocks
for block in response.content:
    if block.type == "tool_use":
        op = block.input.pop("operation")
        result = ImscribeTool.dispatch(op, **block.input)
        print(result.to_json())
```

The same `imscription_TOOL_SCHEMA` works with OpenAI-format APIs (pass as `tools=[imscription_TOOL_SCHEMA["function"]]` with `type="function"` wrapping).

---

*For more detailed information on the underlying theory, refer to **QUANTIG.md** and **IG.md Section VI**.*







