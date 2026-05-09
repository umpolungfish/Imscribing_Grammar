---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# IΓ_CROSΣ_DOMAIN — Phase 2 Extension Specification

Cross-domain stress testing of the 10-primitive tuple against ecological,
techno-social, and robotic systems surfaced five concrete framework gaps.
This document specifies each extension, its motivation, and its implementation plan.

---

## Background

Three systems were encoded in Phase 1 using the closest available enum values,
with `extensions_required` metadata recording the faithful-encoding gaps:

| Synthon | Domain | Key gaps |
|---|---|---|
| `tide_pool_ecological` | ecological | D∞(open), compound_R, fidelity_distribution |
| `global_supply_chain` | techno_social | D∞(open), stoichiometry_network, fidelity_distribution, compound_T |
| `autonomous_drone_swarm` | robotic | tensor_product_D, compound_R, compound_grammar, fidelity_distribution |

---

## Extension 1 — `D∞(open)`: Open Dissipative Qualifier via `reset_type`

### Problem
Axiom 6 requires D∞ systems to have a specifiable reset mechanism. Open
dissipative systems (tide pools, supply chains, living organisms) have
*directional flows* maintained by external driving gradients — they are
perpetually driven, not discretely cyclic.

### Implemented Change (v0.3.1+)

**`constraints.py`** — `validate_axiom6_temporal_grounding()` reads
`synthon.metadata["grounding"]["reset"]["type"]` and branches:

| `reset_type` | Required fields | Falsification |
|---|---|---|
| `"discrete"` (default) | `cycle_steps` list OR `axiom6_grounding` dict OR keyword scan | No identifiable reset in any grounding source |
| `"continuous"` | `driving_gradient.description` + `driving_gradient.coupling` | Either field absent |

**Grounding metadata schema** (`synthon.metadata["grounding"]["reset"]`):

```python
# Discrete (existing chemistry, closed-cycle systems)
{
    "type": "discrete",
    "cycle_steps": ["step1", "step2", ...],   # OR use axiom6_grounding dict
    "timescale": "microseconds",
    "entropy_export": "heat, waste byproducts",
}

# Continuous (ecological, economic, driven robotic systems)
{
    "type": "continuous",
    "driving_gradient": {
        "description": "Solar flux + tidal exchange drive photosynthesis",
        "physical_quantity": "Solar flux (W m⁻²), tidal volume (m³ cycle⁻¹)",
        "coupling": "Photosynthetic rate ∝ irradiance",
        "timescale": "12.4 h tidal period; 24 h solar cycle",
        "entropy_export": "Heat from respiration; detritus via tidal efflux",
    },
}
```

**No model change required**: `reset_type` lives in metadata, not the `Synthon`
dataclass. This is backward-compatible — all existing chemistry synthons without
a `grounding.reset` block default to `"discrete"` and use the existing keyword
scan / `axiom6_grounding` dict checks.

**`cli.py`** — `imscribe validate` surfaces the `reset_type` branch in verbose
output (future: `--d-qualifier continuous` flag to auto-inject grounding schema).

### Cross-domain synthons updated

| Synthon | `reset_type` | `driving_gradient.physical_quantity` |
|---|---|---|
| `tide_pool_ecological` | `continuous` | Solar flux (W m⁻²) + tidal volume (m³ cycle⁻¹) |
| `global_supply_chain` | `continuous` | Demand signal (units/time) + capital flow (USD/cycle) |
| `autonomous_drone_swarm` | N/A — D is `SUPRAMOLECULAR`, Axiom 6 not triggered | — |

---

## Extension 2 — Compound Primitives: `·` Operator

### Problem
Several cross-domain systems require simultaneous active modes for R and Γ:
- Drone swarm: `R(Ent)·R‡` — consensus protocol AND physical motion, both active
- Tide pool: `R‡·R⊇` — non-equilibrium flows AND sessile attachment, both active
- Supply chain: `Γ∧(SELECTIVE)` is currently the only grammar, but the cyclic
  capital-return loop warrants a `Γ→` component as well

The `·` operator means "simultaneously operative" — distinct from the `{}` set
notation (hybrid D) which means "different domains at different scales."

### Proposed Change

**`models.py`** — add optional list fields to `Synthon`:
```python
compound_recognition_modes: List[RecognitionMode] = field(default_factory=list)
compound_grammars: List[InteractionGrammar] = field(default_factory=list)
```

`recognition_mode` remains the primary (dominant) mode.
`compound_recognition_modes` lists co-active secondary modes.

**`constraints.py`** — update axiom checks to consider compound modes:
- Axiom 4: `Γ_→` satisfied if *any* of `[interaction_grammar] + compound_grammars`
  is SEQ, and *any* of `[recognition_mode] + compound_recognition_modes` is R‡ or D∞.
- Axiom 8: R physics check applies to each mode independently.

**`to_notation()`** — render compound modes with `·`:
```
R = DYNAMIC_CATALYTIC, compound = [NON_COVALENT]  →  "R‡·R⊇"
```

---

## Extension 3 — `R(Ent)`: Consensus/Entanglement Recognition Mode

### Problem
Digital consensus protocols (Raft, PBFT, blockchain) and quantum entanglement
share the same functional signature: partner action is *globally constrained* by
collective agreement. No existing R value captures this.

### Proposed Change

**`models.py`** — add to `RecognitionMode`:
```python
CONSENSUS = "Ř_consensus"   # shared distributed-state constraint; R(Ent)
```

**Grounding rule**: `Ř_consensus` requires:
1. A defined consensus protocol or shared-state mechanism
2. A minimum quorum size (e.g., 2/3 of N agents)
3. A conflict-resolution rule

**Axiom 8 extension**: `Ř_consensus` is valid for:
- Digital: consensus protocols (Raft, Paxos, Byzantine fault tolerance)
- Quantum: entangled state preparation (GHZ, cluster states)
- Biological: quorum sensing (Gram-negative bacteria, V. fischeri)

---

## Extension 4 — Fidelity Distribution `⟨F₁, F₂⟩`

### Problem
Heterogeneous systems have different fidelity on different axes or subsystems:
- Supply chain: stochastic demand (F_ð) + hard contractual constraints (F_ℏ)
- Drone swarm: bit-exact digital comms (F_ℏ) + environmental sensor noise (F_ð)
- Tide pool: stochastic on both spatial (F_ð) and temporal (F_ð) axes

A single `Fidelity` tier cannot capture per-axis heterogeneity.

### Proposed Change

**`models.py`** — add optional field to `Synthon`:
```python
fidelity_axes: Optional[Dict[str, Fidelity]] = None
# e.g. {"communication": Fidelity.HIGH, "environment": Fidelity.MEDIUM}
```

`fidelity` remains the *effective* (worst-case) single value for all existing
axiom checks. `fidelity_axes` is supplementary metadata for analysis.

**`perturbation.py`** — `sweep_all()` perturbs `fidelity` (the effective value);
a new `sweep_fidelity_axes()` method perturbs each axis independently.

**`to_notation()`** — if `fidelity_axes` is set, render as `⟨ƒ_x, ƒ_y⟩` in the
compact notation output.

---

## Extension 5 — `D△^⊗n`: Tensor-Product Dimensionality

### Problem
A drone swarm of N agents is not one supramolecular system — it is N identical
systems whose collective state is the tensor product of individual state spaces.
The current hybrid D notation `{D△, D△}` is a set (two different domains) not
a tensor product (N identical agents).

### Proposed Change

**`models.py`** — add optional field to `Synthon`:
```python
dimensionality_multiplicity: Optional[int] = None  # N for D^⊗N; None = single system
```

**`to_notation()`** — render as `D△^⊗3` if `multiplicity = 3`.

**`ensembler.py`** — `EnsembleCatalog.add()` accepts `multiplicity` kwarg:
```python
ensemble.add("autonomous_drone_swarm", multiplicity=50)
```
which instantiates 50 identical copies and computes collective ξ_CP including
Landauer overhead for the N-1 interface connections.

---

## Extension 6 — `stoichiometry_network`: Unbounded S

### Problem
`S = "1:*"` (or `1:∞`) means the system has one "host" entity with an unbounded
number of partners. This is structurally different from `n:m` (fixed asymmetric
ratio) — it signals a network topology where S is better described as a degree
distribution than a ratio.

### Proposed Change

**`models.py`** — add to stoichiometry parsing:
```python
STOICHIOMETRY_NETWORK = "1:*"   # network mode: unbounded partner count
```

**`constraints.py`** — Axiom 3 (cooperative induction):
- `S = "1:*"` with `G = GLOBAL` and `Γ = SELECTIVE_AND` → auto-flag as
  potential scale-free node (hub candidate); recommend Varma probe.

**`audit`** — `catalog auto-stoichiometry` skips `1:*` entries (cannot auto-assign).

---

## Implementation Priority

| Extension | Difficulty | Impact | Priority |
|---|---|---|---|
| D∞(open) qualifier | Low | High — fixes Axiom 6 for all open systems | **P0** |
| Compound primitives `·` | Medium | High — enables faithful cross-domain encoding | **P0** |
| Fidelity distribution | Low | Medium — supplementary metadata | **P1** |
| R(Ent) consensus mode | Medium | Medium — new domain unlocked | **P1** |
| Stoichiometry network | Low | Low — string change + audit update | **P1** |
| D△^⊗n tensor product | High | Medium — requires ensembler update | **P2** |

---

## Catalog Impact

After Phase 2, the three cross-domain synthons should be re-encoded:

```
tide_pool_ecological:
  D: HYBRIÐ_SUPRA_TEMP, qualifier=OPEN
  R: DYNAMIC_CATALYTIC, compound=[NON_COVALENT]
  fidelity_axes: {"spatial": MEDIUM, "temporal": MEDIUM}

global_supply_chain:
  D: TEMPORAL, qualifier=OPEN
  T: NETWORK, compound_topologies=[CYCLIC_BOWTIE]
  stoichiometry: "1:*"
  fidelity_axes: {"demand": MEDIUM, "contract": HIGH}

autonomous_drone_swarm:
  D: SUPRAMOLECULAR, multiplicity=N
  R: DYNAMIC_CATALYTIC, compound=[CONSENSUS]
  Γ: SELECTIVE_SEQ, compound_grammars=[SELECTIVE_AND]
  fidelity_axes: {"digital": HIGH, "environmental": MEDIUM}
```

---

*See also: IΓ_PERTURBATION.md, IΓ_TRAJECTORY.md, IΓ_ENSEMBLER.md*
