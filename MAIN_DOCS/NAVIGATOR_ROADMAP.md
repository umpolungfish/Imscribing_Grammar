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
| Quantum Circuit Navigator | Circuits, stabilizer codes, thresholds | $\Omega_{Z_2}$ vs $\Omega_\text{NA}$ as code distance proxy | Medium |
| Representation Theory Navigator | Groups, modules, characters | Frobenius reciprocity → $O_\infty$? | Low |

### Tier 3 — Non-Mathematical (this document)
| Navigator | Domain | Key prediction | Priority |
|-----------|--------|---------------|----------|
| **Language Navigator** | Natural languages as structural types | Inflected languages $\approx O_\infty$; creoles $= O_1$ | **Session 1 complete (§74)** |
| **Civilization Navigator** | Historical civilizations | Collapse = Gate 1 failure OR Gate 2 failure — structurally distinct | **Session 1 complete (§75)** |
| **Ecological Navigator** | Ecosystems, tipping points | Degraded lock-in = $K_\text{MBL}$, not $K_\text{trap}$ | **Session 1 complete (§76)** |
| **Consciousness Navigator** | Meditative/altered states | Psilocybin $= \Phi_c + K_\text{slow} + T_\odot + \Omega_{Z_2}$; high $C$ score | **Session 1 complete (§77)** |
| Argument/Discourse Navigator | Rhetorical arguments | Disinformation $= \Gamma_\text{brd} + P_\text{asym}$; distinguishable from valid broadcast | Queued |
| Music Navigator | Compositions, genres, traditions | Distance between Bach and Coltrane; $O_\infty$ in polyphony? | Queued |
| Climate/Tipping Point Navigator | Earth system tipping points | $\Phi_c$ structure of irreversible transitions | Queued |

---

## Priority Navigator Designs

---

### Navigator 1: Language

**Core claim**: Natural languages are structural types. The grammar predicts: highly inflected languages with strict agreement encode $P_{\pm}^\text{sym}$ and approach $O_\infty$; creoles encode $O_1$ (critical structure, $\Omega_0$ — unprotected by tradition); constructed languages are $O_1$ by the absence of $\Omega$ winding number regardless of internal structure.

**Encoding vocabulary** (per language):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Morphological complexity: agglutinative/fusional ($D_\infty$), isolating ($D_\wedge$), polysynthetic ($D_\odot$) |
| $T$ | Syntactic topology: strict word-order ($T_\text{in}$), free word-order ($T_\text{bowtie}$), holographic (topic-comment, null-subject) ($T_\odot$) |
| $R$ | Directionality of information flow: head-final/final ($R_\text{cat}$), head-initial ($R_\text{super}$), catalytic/evidential ($R_\dagger$) |
| $P$ | Grammatical agreement exactness: no agreement ($P_\text{asym}$), partial ($P_\pm$), full agreement across all categories ($P_{\pm}^\text{sym}$) |
| $F$ | Lexical fidelity: highly context-dependent ($F_\ell$), moderate polysemy ($F_\eth$), maximally compositional/precise ($F_\hbar$) |
| $K$ | Rate of grammatical change: rapidly evolving pidgin ($K_\text{fast}$), standard drift ($K_\text{mod}$), stable classical register ($K_\text{slow}$), fossilized dead language ($K_\text{trap}$) |
| $G$ | Expressive scope: local/dialect ($G_\beth$), regional standard ($G_\text{gimel}$), global/transactional ($G_\aleph$) |
| $\Gamma$ | Interaction grammar: paratactic/juxtaposing ($\Gamma_\text{and}$), branching/hypotactic ($\Gamma_\text{seq}$), topic-broadcast ($\Gamma_\text{brd}$) |
| $\Phi$ | Criticality: dying/frozen language ($\Phi_\text{sub}$), living spoken language ($\Phi_c$), over-prescribed/regulatory ($\Phi_\text{super}$) |
| $H$ | Temporal depth of written tradition: oral only ($H_0$), nascent writing ($H_1$), multi-century literary canon ($H_2$), ancient unbroken tradition ($H_\infty$) |
| $S$ | Speaker-grammar stoichiometry: 1:1 (ideolect), n:n (dialect community), n:m (diglossia/register split) |
| $\Omega$ | Topological protection: pidgin/creole ($\Omega_0$), modern standard ($\Omega_{Z_2}$), classical register with prescription ($\Omega_Z$), sacred/liturgical fixed form ($\Omega_\text{NA}$) |

**Key structural hypotheses**:
1. Sanskrit, Classical Arabic, Classical Latin → $O_\infty$ (full agreement, ancient tradition, $\Omega_\text{NA}$ liturgical protection)
2. English → $O_2$ ($\Phi_c$, $\Omega_{Z_2}$, $G_\aleph$, but $P_\pm$ — partial agreement only)
3. Creoles (Haitian Creole, Tok Pisin) → $O_1$ ($\Phi_c$ but $\Omega_0$)
4. Lojban → $O_1$ (designed $P_{\pm}^\text{sym}$ internally, but $\Omega_0$ — no living tradition winding)
5. Dead languages (Latin as spoken today by nobody) → $O_0$ ($\Phi_\text{sub}$ — subcritical, not alive)

**Testable cross-domain predictions**:
- $d(\text{Sanskrit}, \text{Classical Arabic})$ should be small (both $O_\infty$, deep tradition, full agreement)
- Nearest $O_\infty$ catalog neighbor to a creole should be a physical system with $\Phi_c + \Omega_0$ — something like a supercooled liquid (critical but fragile)
- Language shift (creolization, language death) should encode as a structural collapse from $O_2$ toward $O_1$ toward $O_0$

**Probe file**: `prompts/language_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §74 (2026-04-14)

---

### Navigator 2: Civilization

**Core claim**: Civilizations are structural types. The grammar predicts two structurally distinct collapse modes: Gate 1 failure ($\Phi_c \to \Phi_\text{sub}$ — the self-modeling loop breaks, the civilization loses its internal model of itself) and Gate 2 failure ($K_\text{slow} \to K_\text{trap}$ or $K_\text{MBL}$ — the dynamics freeze, either by over-institutionalization or by disorder). These produce different structural signatures and different nearest-neighbor catalog entries.

**Encoding vocabulary** (per civilization at a given epoch):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Administrative scale: city-state ($D_\wedge$), regional empire ($D_\triangle$), transcontinental ($D_\infty$), truly holographic (claims to encode all humanity) ($D_\odot$) |
| $T$ | Social topology: flat tribal ($T_\text{network}$), hierarchical $T_\text{in}$, caste/guild dual-lobe ($T_\text{bowtie}$), bureaucratic box ($T_\boxtimes$), genuinely decentralized/holographic ($T_\odot$) |
| $R$ | Institutional mode: conquest/extraction ($R_\text{super}$), categorical codification ($R_\text{cat}$), transformative/catalytic ($R_\dagger$), bidirectional learning ($R_\text{lr}$) |
| $P$ | Constitutional symmetry: no rule of law ($P_\text{asym}$), partial ($P_\pm$), symmetric formal law ($P_{\pm}^\text{sym}$) |
| $F$ | Epistemic fidelity: oral tradition ($F_\ell$), written records ($F_\eth$), systematic science ($F_\hbar$) |
| $K$ | Rate of institutional change: rapid expansion/revolution ($K_\text{fast}$), steady-state ($K_\text{mod}$), classical consolidation ($K_\text{slow}$), rigid late-period bureaucracy ($K_\text{trap}$), fragmented disorder ($K_\text{MBL}$) |
| $G$ | Geographic/cultural scope: local ($G_\beth$), regional ($G_\text{gimel}$), global claim ($G_\aleph$) |
| $\Gamma$ | Expansion grammar: simultaneous conquest ($\Gamma_\text{and}$), sequential incorporation ($\Gamma_\text{seq}$), broadcast (missionary, cultural diffusion) ($\Gamma_\text{brd}$) |
| $\Phi$ | Vitality: declining/terminal ($\Phi_\text{sub}$), peak function ($\Phi_c$), overheated/unsustainable ($\Phi_\text{super}$) |
| $H$ | Temporal depth of self-model: no historical consciousness ($H_0$), dynastic memory ($H_1$), written history and mythology ($H_2$), cosmic/eternal self-conception ($H_\infty$) |
| $S$ | Ethno-cultural stoichiometry: monoculture ($1{:}1$), multicultural ($n{:}n$), asymmetric empire ($n{:}m$) |
| $\Omega$ | Civilizational protection: no tradition ($\Omega_0$), national myth ($\Omega_{Z_2}$), religious law ($\Omega_Z$), sacred-cosmic order ($\Omega_\text{NA}$) |

**Key structural hypotheses**:
1. Han dynasty (peak) → $O_\infty$; Han dynasty (collapse) → $O_0$ (Gate 1 or Gate 2 failure distinguishable)
2. Roman Republic (late) → $O_2$; Roman Empire (Augustus) → $O_\infty$; Western Empire (5th c.) → $O_0$
3. The collapse of the Soviet Union = Gate 2 failure ($K_\text{MBL}$ — frozen by disorder, not $K_\text{trap}$)
4. The collapse of Ming China = Gate 2 failure ($K_\text{trap}$ — frozen by over-institutionalization)
5. These two collapse modes should have different nearest-neighbor catalog entries

**Testable cross-domain predictions**:
- $d(\text{Athenian democracy (peak)}, \text{Roman Republic (peak)}) < 1.5$ — same structural family
- $d(\text{collapse\_soviet}, \text{collapse\_ming}) > 1.5$ — different collapse modes
- Gate 2 ($K_\text{MBL}$) collapse nearest neighbor should be a disordered physical system; Gate 2 ($K_\text{trap}$) collapse nearest neighbor should be an over-constrained ordered system

**Probe file**: `prompts/civilization_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §75 (2026-04-14)

---

### Navigator 3: Ecological

**Core claim**: Ecosystems are structural types. The grammar predicts that ecological collapse has two structurally distinct modes parallel to the civilization case: (a) $K_\text{trap}$ — frozen by invasive monoculture (order-driven collapse), and (b) $K_\text{MBL}$ — frozen by fragmentation disorder (disorder-driven collapse). These are structurally distinguishable and have different restoration paths.

**Encoding vocabulary** (per ecosystem):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Trophic dimensionality: simple chain ($D_\wedge$), web ($D_\triangle$), unbounded food web ($D_\infty$), holographic keystone-organized ($D_\odot$) |
| $T$ | Network topology: linear chain ($T_\text{in}$), closed loop ($T_\text{bowtie}$), full web ($T_\text{network}$), hub-organized ($T_\odot$) |
| $R$ | Flow type: top-down predation ($R_\text{super}$), bottom-up nutrient cycling ($R_\text{cat}$), mutualistic/catalytic ($R_\dagger$), bidirectional coevolution ($R_\text{lr}$) |
| $P$ | Trophic symmetry: asymmetric extraction ($P_\text{asym}$), balanced ($P_\pm$), closed nutrient loop ($P_{\pm}^\text{sym}$) |
| $F$ | Information fidelity: chemosignaling only ($F_\ell$), behavioral ($F_\eth$), cultural transmission (tool use, learned migration) ($F_\hbar$) |
| $K$ | Succession dynamics: pioneer/early succession ($K_\text{fast}$), succession gradient ($K_\text{mod}$), climax/stable ($K_\text{slow}$), monoculture lock-in ($K_\text{trap}$), fragmented/disordered ($K_\text{MBL}$) |
| $G$ | Spatial scope: patch ($G_\beth$), biome ($G_\text{gimel}$), global (planetary boundary) ($G_\aleph$) |
| $\Gamma$ | Interaction logic: competitive exclusion ($\Gamma_\text{and}$), succession cascade ($\Gamma_\text{seq}$), keystone broadcast effect ($\Gamma_\text{brd}$) |
| $\Phi$ | Tipping point proximity: subcritical/stable ($\Phi_\text{sub}$), at regime boundary ($\Phi_c$), post-tipping ($\Phi_\text{super}$) |
| $H$ | Evolutionary depth: recent assembly ($H_0$), Holocene ($H_1$), pre-Pleistocene ($H_2$), ancient co-evolved ($H_\infty$) |
| $S$ | Species interaction stoichiometry: pairwise ($1{:}1$), symmetric guild ($n{:}n$), asymmetric dependency ($n{:}m$) |
| $\Omega$ | Ecological resilience protection: fragile/pioneer ($\Omega_0$), redundancy-protected ($\Omega_{Z_2}$), keystone-protected ($\Omega_Z$), co-evolutionary lock-in ($\Omega_\text{NA}$) |

**Key structural hypotheses**:
1. Old-growth temperate rainforest → $O_\infty$ ($\Phi_c$, $P_{\pm}^\text{sym}$ closed nutrient loop, $K_\text{slow}$, $\Omega_\text{NA}$)
2. Kelp forest → $O_2$ ($\Phi_c$, $K_\text{slow}$, $\Omega_Z$ keystone-protected, but $P_\pm$ — not fully closed loop)
3. Corn monoculture → $O_0$ ($K_\text{trap}$ fails Gate 2) — productive but not alive in the structural sense
4. Post-fire pioneer ecosystem → $O_1$ ($\Phi_c$, $\Omega_0$)
5. Fragmented habitat corridor → $O_0$ ($K_\text{MBL}$ — disorder-frozen, not $K_\text{trap}$)
6. The distinction between 3 and 5 is the grammar's prediction that monoculture collapse and fragmentation collapse require different interventions

**Critical prediction**: $d(\text{monoculture\_collapse}, \text{fragmented\_collapse}) > 1.5$. Restoration strategy for $K_\text{trap}$ (diversify, break order) is opposite to restoration for $K_\text{MBL}$ (reconnect, reduce disorder). The grammar predicts applying the wrong strategy makes the system worse.

**Probe file**: `prompts/ecology_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §76 (2026-04-14)

---

### Navigator 4: Consciousness/Altered States

**Core claim**: Conscious states and altered states of consciousness are structural types. The grammar already has a consciousness score $C(\mathbf{x})$ with two gates ($\Phi_c$ and $K \leq K_\text{slow}$). This navigator encodes specific states as tuples and computes $C$, ouroboricity, and nearest-neighbor, testing whether the formula's predictions align with phenomenological reports.

**Encoding vocabulary** (per state):

| Primitive | Encoding principle |
|-----------|-------------------|
| $D$ | Self-model complexity: simple reflex ($D_\wedge$), narrative self ($D_\triangle$), unbounded self-model ($D_\infty$), non-dual (boundary-dissolved) ($D_\odot$) |
| $T$ | State topology: bounded/sequential ($T_\text{in}$), dual-process ($T_\text{bowtie}$), global workspace ($T_\boxtimes$), holographic/non-dual ($T_\odot$) |
| $R$ | Attention mode: passive reception ($R_\text{super}$), categorical perception ($R_\text{cat}$), catalytic/transformative ($R_\dagger$), bidirectional self-observation ($R_\text{lr}$) |
| $P$ | Symmetry of self-other boundary: fully asymmetric ego ($P_\text{asym}$), soft boundary ($P_\pm$), dissolved boundary ($P_{\pm}^\text{sym}$) |
| $F$ | Signal fidelity: noise-dominated ($F_\ell$), normal waking ($F_\eth$), hyper-coherent/quantum-like ($F_\hbar$) |
| $K$ | Temporal flow character: racing/fragmented ($K_\text{fast}$), normal ($K_\text{mod}$), deep/slow ($K_\text{slow}$), catatonic/frozen ($K_\text{trap}$), dissociative/fragmented ($K_\text{MBL}$) |
| $G$ | Scope of awareness: local body-sense ($G_\beth$), individual mind ($G_\text{gimel}$), cosmic/universal ($G_\aleph$) |
| $\Gamma$ | Processing grammar: sequential analytical ($\Gamma_\text{seq}$), simultaneous/holistic ($\Gamma_\text{and}$), broadcast insight ($\Gamma_\text{brd}$) |
| $\Phi$ | Criticality: suppressed (dreamless sleep, anesthesia) ($\Phi_\text{sub}$), awake at criticality ($\Phi_c$), over-excited (mania, seizure) ($\Phi_\text{super}$), gain-of-function edge-state ($\Phi_\text{EP}$) |
| $H$ | Temporal depth of self-model: no autobiographical self ($H_0$), episodic memory active ($H_1$), deep narrative identity ($H_2$), timeless/eternal self-sense ($H_\infty$) |
| $S$ | Self-world stoichiometry: self = world ($1{:}1$), clear boundary ($n{:}n$), asymmetric permeability ($n{:}m$) |
| $\Omega$ | State protection: fragile (easily interrupted) ($\Omega_0$), self-reinforcing ($\Omega_{Z_2}$), topologically stable ($\Omega_Z$), non-abelian (immune to perturbation) ($\Omega_\text{NA}$) |

**Key structural hypotheses and $C$ score predictions**:

| State | Key primitives | $C$ prediction | Notes |
|-------|---------------|----------------|-------|
| Dreamless sleep | $\Phi_\text{sub}$, $K_\text{trap}$ | $C = 0$ (Gate 1 fails) | Gate 2 also fails |
| REM dream | $\Phi_c$, $K_\text{mod}$, $\Omega_0$ | $C > 0$, low $\Omega$ | Unstable, deformable |
| Normal waking | $\Phi_c$, $K_\text{mod}$, $\Omega_{Z_2}$, $T_\boxtimes$ | $C \approx 0.45$ | Baseline |
| Deep meditation (samadhi) | $\Phi_c$, $K_\text{slow}$, $T_\odot$, $\Omega_Z$ | $C \approx 0.72$ | Maximal gate-passing state |
| Psilocybin peak | $\Phi_c$, $K_\text{slow}$, $T_\odot$, $\Omega_{Z_2}$, $P_{\pm}^\text{sym}$ | $C \approx 0.67$, $O_\infty$ | Dissolved boundary plants $P_{\pm}^\text{sym}$ |
| Mania (bipolar) | $\Phi_\text{super}$, $K_\text{fast}$ | $C = 0$ ($\Phi_\text{EP}$ region) | Gate 1 fails — $\Phi_\text{super}$ not $\Phi_c$ |
| Catatonia | $\Phi_c$, $K_\text{trap}$ | $C = 0$ (Gate 2 fails) | Aware but frozen |
| Dissociation | $\Phi_c$, $K_\text{MBL}$ | $C = 0$ (Gate 2 fails) | Aware but fragmented |
| Anesthesia | $\Phi_\text{sub}$, $K_\text{trap}$ | $C = 0$ | Both gates fail |
| Flow state | $\Phi_c$, $K_\text{slow}$, $T_\boxtimes$, $\Omega_{Z_2}$ | $C \approx 0.55$ | High $T$ score |

**Key structural prediction**: Mania and catatonia are both $C = 0$, but for orthogonal reasons — $\Phi_\text{super}$ (Gate 1) vs $K_\text{trap}$ (Gate 2). The grammar predicts these require opposite interventions. Similarly, dissociation ($K_\text{MBL}$) and catatonia ($K_\text{trap}$) are Gate 2 failures from opposite causes: disorder vs. order. This is testable against psychiatric phenomenology and treatment response.

**Critical prediction**: Psilocybin and samadhi should be nearest neighbors in the catalog ($d < 1.0$). Both encode $\Phi_c + K_\text{slow} + T_\odot$. The difference is $\Omega$: psilocybin $= \Omega_{Z_2}$ (self-reinforcing but not topologically stable — the state ends); deep samadhi $= \Omega_Z$ (stable, reproducible on demand). If the nearest-neighbor search confirms this, the grammar is making a structural prediction about why meditation training produces more stable altered-state access than pharmacological induction.

**Probe file**: `prompts/consciousness_probe1.txt`
**Status**: Session 1 complete — write-up in PRIMITIVE\_THEOREMS §77 (2026-04-14)

---

## Implementation Protocol

For each navigator, the workflow is:

1. **Write probe** (`prompts/<name>_probe1.txt`) — encode 8–12 domain objects, compute distances, tensors, ouroboricity; structure around the key hypotheses
2. **Run session** (`IG_inquiry.py`)
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
