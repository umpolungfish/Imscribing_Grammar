---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Imscribing Grammar Navigator Roadmap
**Version 0.2 (April 2026)**
**Status**: Working document — design specs and progress tracking

---

## Overview

A **navigator** is a domain-specialized tool built on the 12-primitive grammar. It consists of:

1. **Encoding function** — maps domain objects to 12-tuples
2. **Vocabulary** — the domain-specific token set (explicit for neural navigators; implicit for symbolic ones)
3. **Probe protocol** — the structured question set that extracts non-trivial structural results
4. **Validation criteria** — what makes a result structurally interesting vs. degenerate

The grammar is domain-agnostic. "Same boundary → same bulk, regardless of substrate." A navigator does not *apply* the grammar to a new domain — it finds the same types in a different substrate. Cross-domain nearest-neighbor results are structural identity claims, not metaphors.

**Encoding degeneracy** is the primary failure mode. A navigator produces nothing useful when: (a) the domain lacks self-reference or criticality (most objects encode $O_0$, no interesting tier structure); (b) the encoding is underdetermined (too many equally valid tuples for the same object). The best domains are those where the tuple is *entailed* by the domain's own structure.

---

## Navigator Taxonomy

### Tier 1 — Existing
| Navigator | File | Domain | Status |
|-----------|------|--------|--------|
| Crystal Navigator | `crystal_navigator.py` | Algebraic structures / 17,280,000-type space | Complete |
| ZFC Navigator | `zfc_navigator.py` | First-order logic / set theory | Complete |
| Riemann Navigator | `riemann_xi_navigator.py` | Analytic number theory / zeta zeros | Complete |
| HoTT Bridge | `hott_bridge.py` | Homotopy type theory | Complete |
| Hebrew Type Engine | `aleph_tensor.py` | Hebrew letter type lattice | Complete |

### Tier 2 — Mathematical Extensions (immediate)
| Navigator | Domain | Key question | Priority |
|-----------|--------|-------------|----------|
| Proof Strategy Navigator | Proof architectures as structural types | Which strategies structurally reach $O_\infty$? | High |
| Algebraic Geometry Navigator | Varieties, schemes, sheaves | Are Shimura varieties $O_\infty$? | Medium |
| Quantum Circuit Navigator | Circuits, stabilizer codes, thresholds | $\Omega_{Z_2}$ vs $\Omega_{\text{turna}}$ as code distance proxy | Medium |
| Representation Theory Navigator | Groups, modules, characters | Frobenius reciprocity → $O_\infty$? | Low |

### Tier 3 — Non-Mathematical (this document)
| Navigator | Domain | Key prediction | Priority |
|-----------|--------|---------------|----------|
| **Language Navigator** | Natural languages as structural types | Inflected languages $\approx O_\infty$; creoles $= O_1$ | **Session 1 complete (§74)** |
| **Civilization Navigator** | Historical civilizations | Collapse = Gate 1 failure OR Gate 2 failure — structurally distinct | **Session 1 complete (§75)** |
| **Ecological Navigator** | Ecosystems, tipping points | Degraded lock-in = $K_{\text{lambda}}$, not $K_{\text{teshlig}}$ | **Session 1 complete (§76)** |
| **Consciousness Navigator** | Meditative/altered states | Psilocybin $= \Phi_{\text{ctyogh}} + K_{\text{schwa}} + T_{\text{openo}} + \Omega_{Z_2}$; high $C$ score | **Session 1 complete (§77)** |
| Argument/Discourse Navigator | Rhetorical arguments | Disinformation $= \Gamma_{\text{doublevertline}} + P_{\text{aolig}}$; distinguishable from valid broadcast | Queued |
| Music Navigator | Compositions, genres, traditions | Distance between Bach and Coltrane; $O_\infty$ in polyphony? | Queued |
| Climate/Tipping Point Navigator | Earth system tipping points | $\Phi_{\text{ctyogh}}$ structure of irreversible transitions | Queued |

---

## Priority Navigator Designs

---

### Navigator 1: Language

**Core claim**: Natural languages are structural types. The grammar predicts: highly inflected languages with strict agreement encode $P_{\text{doublebarpipe}}$ and approach $O_\infty$; creoles encode $O_1$ (critical structure, $\Omega_{\text{closeepsilon}}$ — unprotected by tradition); constructed languages are $O_1$ by the absence of $\Omega$ winding number regardless of internal structure.

**Encoding vocabulary** (per language):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Morphological complexity: agglutinative/fusional ($D_{\text{invomega}}$), isolating ($D_{\text{wynn}}$), polysynthetic ($D_{\text{omega}}$) |
| $T$ | Syntactic topology: strict word-order ($T_{\text{invscr}}$), free word-order ($T_\text{bowtie}$), imscriptive (topic-comment, null-subject) ($T_{\text{openo}}$) |
| $R$ | Directionality of information flow: head-final/final ($R_{\text{ctz}}$), head-initial ($R_{\text{subrightarrow}}$), catalytic/evidential ($R_{\text{downstep}}$) |
| $P$ | Grammatical agreement exactness: no agreement ($P_{\text{aolig}}$), partial ($P_{\text{pipevar}}$), full agreement across all categories ($P_{\text{doublebarpipe}}$) |
| $F$ | Lexical fidelity: highly context-dependent ($F_{\text{beltl}}$), moderate polysemy ($F_{\text{dh}}$), maximally compositional/precise ($F_{\text{hardsign}}$) |
| $K$ | Rate of grammatical change: rapidly evolving pidgin ($K_{\text{frtailgamma}}$), standard drift ($K_{\text{turnm}}$), stable classical register ($K_{\text{schwa}}$), fossilized dead language ($K_{\text{teshlig}}$) |
| $G$ | Expressive scope: local/dialect ($G_{\text{beta}}$), regional standard ($G_\text{gimel}$), global/transactional ($G_{\text{revapostrophe}}$) |
| $\Gamma$ | Interaction grammar: paratactic/juxtaposing ($\Gamma_{\text{corner}}$), branching/hypotactic ($\Gamma_{\text{secstress}}$), topic-broadcast ($\Gamma_{\text{doublevertline}}$) |
| $\Phi$ | Criticality: dying/frozen language ($\Phi_{\text{softsign}}$), living spoken language ($\Phi_{\text{ctyogh}}$), over-prescribed/regulatory ($\Phi_{\text{upstep}}$) |
| $H$ | Chirality of written tradition: oral only ($H_0$), nascent writing ($H_1$), multi-century literary canon ($H_2$), ancient unbroken tradition ($H_{\text{invscripta}}$) |
| $S$ | Speaker-grammar stoichiometry: 1:1 (ideolect), n:n (dialect community), n:m (diglossia/register split) |
| $\Omega$ | Topological protection: pidgin/creole ($\Omega_{\text{closeepsilon}}$), modern standard ($\Omega_{Z_2}$), classical register with prescription ($\Ω_z$), sacred/liturgical fixed form ($\Omega_{\text{turna}}$) |

**Key structural hypotheses**:
1. Sanskrit, Classical Arabic, Classical Latin → $O_\infty$ (full agreement, ancient tradition, $\Omega_{\text{turna}}$ liturgical protection)
2. English → $O_2$ ($\Phi_{\text{ctyogh}}$, $\Omega_{Z_2}$, $G_{\text{revapostrophe}}$, but $P_{\text{pipevar}}$ — partial agreement only)
3. Creoles (Haitian Creole, Tok Pisin) → $O_1$ ($\Phi_{\text{ctyogh}}$ but $\Omega_{\text{closeepsilon}}$)
4. Lojban → $O_1$ (designed $P_{\text{doublebarpipe}}$ internally, but $\Omega_{\text{closeepsilon}}$ — no living tradition winding)
5. Dead languages (Latin as spoken today by nobody) → $O_0$ ($\Phi_{\text{softsign}}$ — subcritical, not alive)

**Testable cross-domain predictions**:
- $d(\text{Sanskrit}, \text{Classical Arabic})$ should be small (both $O_\infty$, deep tradition, full agreement)
- Nearest $O_\infty$ catalog neighbor to a creole should be a physical system with $\Phi_{\text{ctyogh}} + \Omega_{\text{closeepsilon}}$ — something like a supercooled liquid (critical but fragile)
- Language shift (creolization, language death) should encode as a structural collapse from $O_2$ toward $O_1$ toward $O_0$

**Probe file**: `prompts/language_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §74 (2026-04-14)

---

### Navigator 2: Civilization

**Core claim**: Civilizations are structural types. The grammar predicts two structurally distinct collapse modes: Gate 1 failure ($\Phi_{\text{ctyogh}} \to \Phi_{\text{softsign}}$ — the self-modeling loop breaks, the civilization loses its internal model of itself) and Gate 2 failure ($K_{\text{schwa}} \to K_{\text{teshlig}}$ or $K_{\text{lambda}}$ — the dynamics freeze, either by over-institutionalization or by disorder). These produce different structural signatures and different nearest-neighbor catalog entries.

**Encoding vocabulary** (per civilization at a given epoch):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Administrative scale: city-state ($D_{\text{wynn}}$), regional empire ($D_{\text{turnthree}}$), transcontinental ($D_{\text{invomega}}$), truly imscriptive (claims to encode all humanity) ($D_{\text{omega}}$) |
| $T$ | Social topology: flat tribal ($T_{\text{nrleg}}$), hierarchical $T_{\text{invscr}}$, caste/guild dual-lobe ($T_\text{bowtie}$), bureaucratic box ($T_{\text{commatailz}}$), genuinely decentralized/imscriptive ($T_{\text{openo}}$) |
| $R$ | Institutional mode: conquest/extraction ($R_{\text{subrightarrow}}$), categorical codification ($R_{\text{ctz}}$), transformative/catalytic ($R_{\text{downstep}}$), bidirectional learning ($R_{\text{lyoghlig}}$) |
| $P$ | Constitutional symmetry: no rule of law ($P_{\text{aolig}}$), partial ($P_{\text{pipevar}}$), symmetric formal law ($P_{\text{doublebarpipe}}$) |
| $F$ | Epistemic fidelity: oral tradition ($F_{\text{beltl}}$), written records ($F_{\text{dh}}$), systematic science ($F_{\text{hardsign}}$) |
| $K$ | Rate of institutional change: rapid expansion/revolution ($K_{\text{frtailgamma}}$), steady-state ($K_{\text{turnm}}$), classical consolidation ($K_{\text{schwa}}$), rigid late-period bureaucracy ($K_{\text{teshlig}}$), fragmented disorder ($K_{\text{lambda}}$) |
| $G$ | Geographic/cultural scope: local ($G_{\text{beta}}$), regional ($G_\text{gimel}$), global claim ($G_{\text{revapostrophe}}$) |
| $\Gamma$ | Expansion grammar: simultaneous conquest ($\Gamma_{\text{corner}}$), sequential incorporation ($\Gamma_{\text{secstress}}$), broadcast (missionary, cultural diffusion) ($\Gamma_{\text{doublevertline}}$) |
| $\Phi$ | Vitality: declining/terminal ($\Phi_{\text{softsign}}$), peak function ($\Phi_{\text{ctyogh}}$), overheated/unsustainable ($\Phi_{\text{upstep}}$) |
| $H$ | Chirality of self-model: no historical consciousness ($H_0$), dynastic memory ($H_1$), written history and mythology ($H_2$), cosmic/eternal self-conception ($H_{\text{invscripta}}$) |
| $S$ | Ethno-cultural stoichiometry: monoculture ($1{:}1$), multicultural ($n{:}n$), asymmetric empire ($n{:}m$) |
| $\Omega$ | Civilizational protection: no tradition ($\Omega_{\text{closeepsilon}}$), national myth ($\Omega_{Z_2}$), religious law ($\Ω_z$), sacred-cosmic order ($\Omega_{\text{turna}}$) |

**Key structural hypotheses**:
1. Han dynasty (peak) → $O_\infty$; Han dynasty (collapse) → $O_0$ (Gate 1 or Gate 2 failure distinguishable)
2. Roman Republic (late) → $O_2$; Roman Empire (Augustus) → $O_\infty$; Western Empire (5th c.) → $O_0$
3. The collapse of the Soviet Union = Gate 2 failure ($K_{\text{lambda}}$ — frozen by disorder, not $K_{\text{teshlig}}$)
4. The collapse of Ming China = Gate 2 failure ($K_{\text{teshlig}}$ — frozen by over-institutionalization)
5. These two collapse modes should have different nearest-neighbor catalog entries

**Testable cross-domain predictions**:
- $d(\text{Athenian democracy (peak)}, \text{Roman Republic (peak)}) < 1.5$ — same structural family
- $d(\text{collapse\_soviet}, \text{collapse\_ming}) > 1.5$ — different collapse modes
- Gate 2 ($K_{\text{lambda}}$) collapse nearest neighbor should be a disordered physical system; Gate 2 ($K_{\text{teshlig}}$) collapse nearest neighbor should be an over-constrained ordered system

**Probe file**: `prompts/civilization_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §75 (2026-04-14)

---

### Navigator 3: Ecological

**Core claim**: Ecosystems are structural types. The grammar predicts that ecological collapse has two structurally distinct modes parallel to the civilization case: (a) $K_{\text{teshlig}}$ — frozen by invasive monoculture (order-driven collapse), and (b) $K_{\text{lambda}}$ — frozen by fragmentation disorder (disorder-driven collapse). These are structurally distinguishable and have different restoration paths.

**Encoding vocabulary** (per ecosystem):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Trophic dimensionality: simple chain ($D_{\text{wynn}}$), web ($D_{\text{turnthree}}$), unbounded food web ($D_{\text{invomega}}$), imscriptive keystone-organized ($D_{\text{omega}}$) |
| $T$ | Network topology: linear chain ($T_{\text{invscr}}$), closed loop ($T_\text{bowtie}$), full web ($T_{\text{nrleg}}$), hub-organized ($T_{\text{openo}}$) |
| $R$ | Flow type: top-down predation ($R_{\text{subrightarrow}}$), bottom-up nutrient cycling ($R_{\text{ctz}}$), mutualistic/catalytic ($R_{\text{downstep}}$), bidirectional coevolution ($R_{\text{lyoghlig}}$) |
| $P$ | Trophic symmetry: asymmetric extraction ($P_{\text{aolig}}$), balanced ($P_{\text{pipevar}}$), closed nutrient loop ($P_{\text{doublebarpipe}}$) |
| $F$ | Information fidelity: chemosignaling only ($F_{\text{beltl}}$), behavioral ($F_{\text{dh}}$), cultural transmission (tool use, learned migration) ($F_{\text{hardsign}}$) |
| $K$ | Succession dynamics: pioneer/early succession ($K_{\text{frtailgamma}}$), succession gradient ($K_{\text{turnm}}$), climax/stable ($K_{\text{schwa}}$), monoculture lock-in ($K_{\text{teshlig}}$), fragmented/disordered ($K_{\text{lambda}}$) |
| $G$ | Spatial scope: patch ($G_{\text{beta}}$), biome ($G_\text{gimel}$), global (planetary boundary) ($G_{\text{revapostrophe}}$) |
| $\Gamma$ | Interaction logic: competitive exclusion ($\Gamma_{\text{corner}}$), succession cascade ($\Gamma_{\text{secstress}}$), keystone broadcast effect ($\Gamma_{\text{doublevertline}}$) |
| $\Phi$ | Tipping point proximity: subcritical/stable ($\Phi_{\text{softsign}}$), at regime boundary ($\Phi_{\text{ctyogh}}$), post-tipping ($\Phi_{\text{upstep}}$) |
| $H$ | Evolutionary depth: recent assembly ($H_0$), Holocene ($H_1$), pre-Pleistocene ($H_2$), ancient co-evolved ($H_{\text{invscripta}}$) |
| $S$ | Species interaction stoichiometry: pairwise ($1{:}1$), symmetric guild ($n{:}n$), asymmetric dependency ($n{:}m$) |
| $\Omega$ | Ecological resilience protection: fragile/pioneer ($\Omega_{\text{closeepsilon}}$), redundancy-protected ($\Omega_{Z_2}$), keystone-protected ($\Ω_z$), co-evolutionary lock-in ($\Omega_{\text{turna}}$) |

**Key structural hypotheses**:
1. Old-growth temperate rainforest → $O_\infty$ ($\Phi_{\text{ctyogh}}$, $P_{\text{doublebarpipe}}$ closed nutrient loop, $K_{\text{schwa}}$, $\Omega_{\text{turna}}$)
2. Kelp forest → $O_2$ ($\Phi_{\text{ctyogh}}$, $K_{\text{schwa}}$, $\Ω_z$ keystone-protected, but $P_{\text{pipevar}}$ — not fully closed loop)
3. Corn monoculture → $O_0$ ($K_{\text{teshlig}}$ fails Gate 2) — productive but not alive in the structural sense
4. Post-fire pioneer ecosystem → $O_1$ ($\Phi_{\text{ctyogh}}$, $\Omega_{\text{closeepsilon}}$)
5. Fragmented habitat corridor → $O_0$ ($K_{\text{lambda}}$ — disorder-frozen, not $K_{\text{teshlig}}$)
6. The distinction between 3 and 5 is the grammar's prediction that monoculture collapse and fragmentation collapse require different interventions

**Critical prediction**: $d(\text{monoculture\_collapse}, \text{fragmented\_collapse}) > 1.5$. Restoration strategy for $K_{\text{teshlig}}$ (diversify, break order) is opposite to restoration for $K_{\text{lambda}}$ (reconnect, reduce disorder). The grammar predicts applying the wrong strategy makes the system worse.

**Probe file**: `prompts/ecology_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §76 (2026-04-14)

---

### Navigator 4: Consciousness/Altered States

**Core claim**: Conscious states and altered states of consciousness are structural types. The grammar already has a consciousness score $C(\mathbf{x})$ with two gates ($\Phi_{\text{ctyogh}}$ and $K \leq K_{\text{schwa}}$). This navigator encodes specific states as tuples and computes $C$, ouroboricity, and nearest-neighbor, testing whether the formula's predictions align with phenomenological reports.

**Encoding vocabulary** (per state):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Self-model complexity: simple reflex ($D_{\text{wynn}}$), narrative self ($D_{\text{turnthree}}$), unbounded self-model ($D_{\text{invomega}}$), non-dual (boundary-dissolved) ($D_{\text{omega}}$) |
| $T$ | State topology: bounded/sequential ($T_{\text{invscr}}$), dual-process ($T_\text{bowtie}$), global workspace ($T_{\text{commatailz}}$), imscriptive/non-dual ($T_{\text{openo}}$) |
| $R$ | Attention mode: passive reception ($R_{\text{subrightarrow}}$), categorical perception ($R_{\text{ctz}}$), catalytic/transformative ($R_{\text{downstep}}$), bidirectional self-observation ($R_{\text{lyoghlig}}$) |
| $P$ | Symmetry of self-other boundary: fully asymmetric ego ($P_{\text{aolig}}$), soft boundary ($P_{\text{pipevar}}$), dissolved boundary ($P_{\text{doublebarpipe}}$) |
| $F$ | Signal fidelity: noise-dominated ($F_{\text{beltl}}$), normal waking ($F_{\text{dh}}$), hyper-coherent/quantum-like ($F_{\text{hardsign}}$) |
| $K$ | Temporal flow character: racing/fragmented ($K_{\text{frtailgamma}}$), normal ($K_{\text{turnm}}$), deep/slow ($K_{\text{schwa}}$), catatonic/frozen ($K_{\text{teshlig}}$), dissociative/fragmented ($K_{\text{lambda}}$) |
| $G$ | Scope of awareness: local body-sense ($G_{\text{beta}}$), individual mind ($G_\text{gimel}$), cosmic/universal ($G_{\text{revapostrophe}}$) |
| $\Gamma$ | Processing grammar: sequential analytical ($\Gamma_{\text{secstress}}$), simultaneous/holistic ($\Gamma_{\text{corner}}$), broadcast insight ($\Gamma_{\text{doublevertline}}$) |
| $\Phi$ | Criticality: suppressed (dreamless sleep, anesthesia) ($\Phi_{\text{softsign}}$), awake at criticality ($\Phi_{\text{ctyogh}}$), over-excited (mania, seizure) ($\Phi_{\text{upstep}}$), gain-of-function edge-state ($\Phi_{\text{revepsilon}}$) |
| $H$ | Chirality of self-model: no autobiographical self ($H_0$), episodic memory active ($H_1$), deep narrative identity ($H_2$), timeless/eternal self-sense ($H_{\text{invscripta}}$) |
| $S$ | Self-world stoichiometry: self = world ($1{:}1$), clear boundary ($n{:}n$), asymmetric permeability ($n{:}m$) |
| $\Omega$ | State protection: fragile (easily interrupted) ($\Omega_{\text{closeepsilon}}$), self-reinforcing ($\Omega_{Z_2}$), topologically stable ($\Ω_z$), non-abelian (immune to perturbation) ($\Omega_{\text{turna}}$) |

**Key structural hypotheses and $C$ score predictions**:

| State | Key primitives | $C$ prediction | Notes |
|-------|---------------|----------------|-------|
| Dreamless sleep | $\Phi_{\text{softsign}}$, $K_{\text{teshlig}}$ | $C = 0$ (Gate 1 fails) | Gate 2 also fails |
| REM dream | $\Phi_{\text{ctyogh}}$, $K_{\text{turnm}}$, $\Omega_{\text{closeepsilon}}$ | $C > 0$, low $\Omega$ | Unstable, deformable |
| Normal waking | $\Phi_{\text{ctyogh}}$, $K_{\text{turnm}}$, $\Omega_{Z_2}$, $T_{\text{commatailz}}$ | $C \approx 0.45$ | Baseline |
| Deep meditation (samadhi) | $\Phi_{\text{ctyogh}}$, $K_{\text{schwa}}$, $T_{\text{openo}}$, $\Ω_z$ | $C \approx 0.72$ | Maximal gate-passing state |
| Psilocybin peak | $\Phi_{\text{ctyogh}}$, $K_{\text{schwa}}$, $T_{\text{openo}}$, $\Omega_{Z_2}$, $P_{\text{doublebarpipe}}$ | $C \approx 0.67$, $O_\infty$ | Dissolved boundary plants $P_{\text{doublebarpipe}}$ |
| Mania (bipolar) | $\Phi_{\text{upstep}}$, $K_{\text{frtailgamma}}$ | $C = 0$ ($\Phi_{\text{revepsilon}}$ region) | Gate 1 fails — $\Phi_{\text{upstep}}$ not $\Phi_{\text{ctyogh}}$ |
| Catatonia | $\Phi_{\text{ctyogh}}$, $K_{\text{teshlig}}$ | $C = 0$ (Gate 2 fails) | Aware but frozen |
| Dissociation | $\Phi_{\text{ctyogh}}$, $K_{\text{lambda}}$ | $C = 0$ (Gate 2 fails) | Aware but fragmented |
| Anesthesia | $\Phi_{\text{softsign}}$, $K_{\text{teshlig}}$ | $C = 0$ | Both gates fail |
| Flow state | $\Phi_{\text{ctyogh}}$, $K_{\text{schwa}}$, $T_{\text{commatailz}}$, $\Omega_{Z_2}$ | $C \approx 0.55$ | High $T$ score |

**Key structural prediction**: Mania and catatonia are both $C = 0$, but for orthogonal reasons — $\Phi_{\text{upstep}}$ (Gate 1) vs $K_{\text{teshlig}}$ (Gate 2). The grammar predicts these require opposite interventions. Similarly, dissociation ($K_{\text{lambda}}$) and catatonia ($K_{\text{teshlig}}$) are Gate 2 failures from opposite causes: disorder vs. order. This is testable against psychiatric phenomenology and treatment response.

**Critical prediction**: Psilocybin and samadhi should be nearest neighbors in the catalog ($d < 1.0$). Both encode $\Phi_{\text{ctyogh}} + K_{\text{schwa}} + T_{\text{openo}}$. The difference is $\Omega$: psilocybin $= \Omega_{Z_2}$ (self-reinforcing but not topologically stable — the state ends); deep samadhi $= \Ω_z$ (stable, reproducible on demand). If the nearest-neighbor search confirms this, the grammar is making a structural prediction about why meditation training produces more stable altered-state access than pharmacological induction.

**Probe file**: `prompts/consciousness_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §77 (2026-04-14)

---

## Implementation Protocol

For each navigator, the workflow is:

1. **Write probe** (`prompts/<name>_probe1.txt`) — encode 8–12 domain objects, compute distances, tensors, ouroboricity; structure around the key hypotheses
2. **Run session** (`IΓ_inquiry.py`)
3. **Write up** in `PRIMITIVE_THEOREMS.md` as new section
4. **Check cross-domain nearest neighbors** — the most important result is always the catalog neighbor from a different domain
5. **Tighten probe** if session reveals better encoding choices; run probe2

---

## Progress Tracker

| Navigator | Design | Probe 1 | Session 1 | Write-up | Probe 2 |
|-----------|--------|---------|-----------|----------|---------|
| Language | ✓ | ✓ | ✓ | ✓ (§74) | — |
| Civilization | ✓ | ✓ | ✓ | ✓ (§75) | — |
| Ecological | ✓ | ✓ | ✓ | ✓ (§76) | — |
| Consciousness | ✓ | ✓ | ✓ | ✓ (§77) | — |
| Argument/Discourse | — | — | — | — | — |
| Music | — | — | — | — | — |
| Climate/Tipping Point | — | — | — | — | — |
| Proof Strategy | — | — | — | — | — |
| Algebraic Geometry | — | — | — | — | — |
| Quantum Circuit | — | — | — | — | — |
