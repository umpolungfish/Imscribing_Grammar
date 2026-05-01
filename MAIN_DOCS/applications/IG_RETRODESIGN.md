# IG_RETRODESIGN.md

## Constraint-Directed Retrosynthetic Decomposition

---

## 1.0 System Definition

**IG_RETRODESIGN** is the inverse operation of **IG_HOTSWAP**. While HotSwap operates *forward* (replacing $S_{old}$ with $S_{new}$ in an active system $\Psi$), Retrodesign operates *backward*: given a target constraint architecture $\Psi_{target}$, it decomposes the target into a minimal set of constituent synthons whose composition axioms are mutually satisfiable.

This reframes retrosynthesis from "what bonds to break" to "what primitive subsets, when composed, generate the target constraint architecture without axiom violations." The ten-primitive grammar makes this tractable because each decomposition step is axiom-checkable.

This protocol leverages the Imscribing Grammar v2.2 framework, utilizing axiom validation, thermodynamic efficiency metrics ($\xi_{CP}$), and recursive decomposition to identify valid synthon combinations.

---

## 2.0 Decomposition Criteria

### 2.1 Primitive Decomposition Rules

| Primitive | Decomposition Behavior | Constraint |
| :--- | :--- | :--- |
| **Dimensionality ($D$)** | **Partition by Domain** | Hybrid $D = \{D_{\bigtriangleup}, D_{\infty}\}$ splits into separate $D_{\bigtriangleup}$ (framework) and $D_{\infty}$ (cycle) branches. |
| **Topology ($T$)** | **Subgraph Isomorphism** | $T_{\square}$ (hub/node) decomposes into hub (SBU) + spokes (linkers). $T_{\bowtie}$ (cyclic) may decompose into linear precursors with closing bond. |
| **Recognition ($R$)** | **Mechanism Preservation** | $R_{\ddagger}$ (catalytic) must decompose into catalyst + substrate. $R_{\Leftrightarrow}$ (mechanical) must decompose into interlocked components. |
| **Polarity ($P$)** | **Complementary Pairing** | $P_{\pm}$ (self-complementary) may decompose into $P_{+} + P_{-}$ pair. $P_{+}$ requires $P_{-}$ partner in decomposition. |
| **Fidelity ($F$)** | **Floor Enforcement** | Decomposed synthons must satisfy $F \geq F_{\eth}$ for $T_{\bowtie}$ (Axiom 1). Low-fidelity branches are pruned. |
| **Kinetic Character ($K$)** | **Accessibility Check** | At least one decomposition pathway must have all-$K_{fast}$ or all-$K_{mod}$ steps. All-$K_{slow}$ branches are pruned. |
| **Granularity ($G$)** | **Scale Consistency** | $G_{\aleph}$ (global) decomposes into $G_{\beth}$ (local) + $G_{\gimel}$ (mesoscale) components. $G_{\beth}$ cannot directly produce $G_{\aleph}$ without amplification mechanism. |
| **Interaction Grammar ($\Gamma$)** | **Logic Preservation** | $\Gamma_{\to}$ (SEQUENTIAL) decomposes into ordered sub-steps. $\Gamma_{\wedge}$ (AND) decomposes into simultaneous partners. |
| **Criticality ($\Phi$)** | **Emergence Detection** | $\Phi_c$ targets may decompose into $\Phi_{sub}$ components (emergent criticality). $\Phi_{sub}$ targets with $\Phi_c$ components are flagged. |
| **Stoichiometry ($S$)** | **Mass-Balance Closure** | Sum of component $S$ values must equal target $S$. $1:12$ (MOF node:linker) decomposes into $1 \times$ node + $12 \times$ linker. |

### 2.2 Axiom-Guided Pruning Rules

The decomposition tree is pruned not by chemical intuition alone, but by **Axiom Violation**:

| Violation | Pruning Condition | Axiom |
| :--- | :--- | :--- |
| **Fidelity Floor** | $T_{\bowtie} + P_{\pm} + F_{\ell}$ → **PRUNE** | Axiom 1 |
| **Propagation Barrier** | $G_{\beth}$/$\Gamma_{\wedge}(\text{SPECIFIC})$ sub-tuple assigned $G_{\aleph}$ scope without $\Gamma_{\vee}$ or $T_{network}$ → **PRUNE** | Axiom 2 |
| **Grammar Mismatch** | $\Gamma_{\to} + D_{\wedge} + R_{\supseteq}$ → **PRUNE** | Axiom 4 |
| **Grounding Fail (Temporal)** | $D_{\infty}$ without reset text → **FLAG** | Axiom 6 |
| **Grounding Fail (Cyclic)** | $T_{\bowtie}$ without closing-bond text → **FLAG** | Axiom 7 |
| **Kinetic Trap** | $K_{trap}$ in critical path → **WARN** (operational risk) | — |
| **Stoichiometry Mismatch** | $\sum S_i \neq S_{target}$ (molecular scale) → **PRUNE** | Mass balance |

### 2.3 Decomposition Depth Limits

| Target Complexity | Max Depth | Rationale |
| :--- | :--- | :--- |
| **Molecular ($D_{\wedge}$)** | 3–5 levels | Bond disconnection depth limited by synthetic accessibility. |
| **Supramolecular ($D_{\bigtriangleup}$)** | 2–4 levels | SBU + linker decomposition typically 2 levels; hierarchical assemblies may require 4. |
| **Temporal ($D_{\infty}$)** | 4–8 levels | Catalytic cycles decompose into 4–8 mechanistic steps. |
| **Hybrid ($\{D_i, D_j\}$)** | Sum of domains | MOF-catalyst hybrids: $D_{\bigtriangleup}$ (2–4) + $D_{\infty}$ (4–8) = 6–12 levels. |

---

## 3.0 The Retrodesign Protocol (5-Step Workflow)

### Step 1: Target Encoding

Encode the target system as a unified notation tuple. For complex systems, use hybrid dimensionality sets.

```python
from imscrbgrmr import SynthonNotation

# Example: A supramolecular cage with temporal gating
target = SynthonNotation.from_string(
    "⟨{D_triangle, D_infinity}; T_cage; R_superset+ddagger; P_pm; F_eth; K_mod; "
    "G_gimel; Gamma_and(SELECTIVE); Phi_sub; 4:4⟩"
)

# Example: MOF-catalyst hybrid (NU-1000 + Ni)
mof_target = SynthonNotation.from_string(
    "⟨{D_triangle}·{D_infinity}; {T_square·T_bowtie}; R_superset+ddagger; "
    "P_pm; F_hbar, F_eth; K_mod; G_aleph; Gamma_odot(SELECTIVE); Phi_sub; n:m⟩"
)
```

```bash
# CLI: Encode target from string
imscribe retrodesign encode --target "⟨D_triangle; T_square; R_superset; P_plus; F_hbar; K_mod; G_aleph; Gamma_odot; Phi_sub; 1:12⟩"
```

### Step 2: Decomposition Search

The engine performs a recursive split of the primitive space, checking compatibility at each node.

```bash
# CLI: Decompose target into valid sub-tuples
imscribe retrodesign "⟨D_triangle; T_square; R_superset; P_plus; F_hbar; K_mod; G_aleph; Gamma_odot; Phi_sub; 1:12⟩" \
    --max-depth 3 \
    --prune-axioms 1,2,4,6,7 \
    --domain supramolecular

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ DECOMPOSITION TREE                                              │
# ├─────────────────────────────────────────────────────────────────┤
# │ Root: Zr-MOF Node (D_triangle, T_square, 1:12)                  │
# │                                                                 │
# │ ├── Branch A (Structural Scaffold)                              │
# │ │   ├── Synthon: Zr6_oxo_SBU                                    │
# │ │   │   └── ⟨D_triangle; T_square; R_superset; P_plus;          │
# │ │   │       F_hbar; K_mod; G_aleph; Gamma_odot; Phi_sub; 1:12⟩  │
# │ │   │                                                           │
# │ │   └── Synthon: Terephthalate_Linker (×12)                     │
# │ │       └── ⟨D_triangle; T_chain; R_superset; P_minus;          │
# │ │           F_hbar; K_fast; G_beth; Gamma_and; Phi_sub; 1:1⟩    │
# │                                                                 │
# │ └── Branch B (Optional: Pore Functionalization)                 │
# │     └── Synthon: Ni_catalyst (optional guest)                   │
# │         └── ⟨D_triangle; T_bowtie; R_ddagger; P_pm;             │
# │             F_eth; K_mod; G_beth; Gamma_sequential; Phi_sub; 1:1⟩ │
# └─────────────────────────────────────────────────────────────────┘
```

```python
from imscrbgrmr.retrodesign import DecompositionEngine

engine = DecompositionEngine(
    max_depth=3,
    prune_axioms=[1, 2, 4, 6, 7],
    domain="supramolecular"
)

tree = engine.decompose(target)
print(f"Valid decomposition pathways: {tree.count_valid_paths()}")
```

### Step 3: Pruning & Validation

Dead branches are pruned immediately upon axiom violation.

```bash
# CLI: Show pruning decisions
imscribe retrodesign "⟨D_wedge; T_bowtie; R_superset; P_pm; F_low; K_fast; G_beth; Gamma_and; Phi_sub; 1:1⟩" \
    --show-pruned

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ PRUNING REPORT                                                  │
# ├─────────────────────────────────────────────────────────────────┤
# │ Target: ⟨D_wedge; T_bowtie; R_superset; P_pm; F_low; ...⟩       │
# │                                                                 │
# │ PRUNED at depth 0:                                              │
# │   Reason: Axiom 1 Violation — T_bowtie + P_pm + F_low forbidden │
# │   Fidelity floor requires F >= F_eth for cyclic self-complementary │
# │                                                                 │
# │ No valid decomposition pathways found.                          │
# │ Recommendation: Increase target fidelity to F_eth or higher.    │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Pruning report
report = engine.decompose(target, show_pruned=True)

for pruned in report.pruned_branches:
    print(f"Pruned at depth {pruned.depth}: {pruned.reason}")
```

### Step 4: Thermodynamic Feasibility Check

Compute $\xi_{CP}$ for each decomposition pathway to identify thermodynamically favorable routes.

```bash
# CLI: Compute thermodynamics for decomposition pathways
imscribe retrodesign thermo --pathways pathways.json --delta-g -85.0

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ PATHWAY THERMODYNAMICS                                          │
# ├─────────────────────────────────────────────────────────────────┤
# │ Pathway 1 (Zr6_SBU + 12× Linker):                               │
# │   ΔG_assembly = -85.0 kJ/mol                                    │
# │   η_CP = 1.5e-4                                                 │
# │   ξ_CP = 8.8 nats (MEDIUM)                                      │
# │   Interface overhead: 1.0 bits                                  │
# │                                                                 │
# │ Pathway 2 (Alternative SBU + 12× Linker):                       │
# │   ΔG_assembly = -72.0 kJ/mol                                    │
# │   η_CP = 8.2e-5                                                 │
# │   ξ_CP = 9.4 nats (MEDIUM)                                      │
# │   Interface overhead: 1.5 bits                                  │
# │                                                                 │
# │ Recommended: Pathway 1 (lower ξ_CP, lower interface overhead)   │
# └─────────────────────────────────────────────────────────────────┘
```

```python
from imscrbgrmr.thermodynamics import compute_eta_CP

# Compare pathways
pathway1_xi = compute_eta_CP(pathway1_synthon, delta_g=-85.0).xi_CP
pathway2_xi = compute_eta_CP(pathway2_synthon, delta_g=-72.0).xi_CP

print(f"Pathway 1 ξ_CP: {pathway1_xi:.2f} nats")
print(f"Pathway 2 ξ_CP: {pathway2_xi:.2f} nats")
```

### Step 5: Integration with Ensembler & HotSwap

Retrodesign output (validated synthon set) feeds directly into IG_ENSEMBLER.md for composition verification, then into IG_HOTSWAP.md for candidate screening.

```bash
# CLI: Export validated synthon set for Ensembler
imscribe retrodesign export --pathways pathways.json --format ensemble --output ensemble_input.json

# Then run Ensembler
imscribe ensemble check --input ensemble_input.json --pairwise
```

```python
from imscrbgrmr.ensemble import EnsembleCatalog

# Export to ensemble format
ensemble = engine.export_to_ensemble(tree.best_pathway())

# Run pairwise compatibility check
from imscrbgrmr.constraints import ConstraintEngine
constraint_engine = ConstraintEngine()
compatibility = constraint_engine.check_pairwise(ensemble)
```

---

## 4.0 Risk Assessment & Failure Modes

| Failure Mode | Primitive Signature | Mitigation |
| :--- | :--- | :--- |
| **Axiom Violation (Fatal)** | $T_{\bowtie} + F_{\ell}$; $\Gamma_{\to}$ without $D_{\infty}$ | Hard block — decomposition rejected at pruning. |
| **No Valid Pathways** | All branches pruned | Relax constraints (increase max-depth, allow speculative synthons). |
| **Stoichiometry Mismatch** | $\sum S_i \neq S_{target}$ | Verify mass-balance; check for missing components. |
| **Kinetic Inaccessibility** | All pathways have $K_{slow}$ steps | Add catalyst/template; switch assembly conditions. |
| **Grounding Fail** | `grounding_status` → `unverified` for $D_{\infty}$ or $T_{\bowtie}$ | Require full/override grounding; `imscribe audit`. |
| **Over-Decomposition** | Depth > max_depth without closure | Increase max-depth; simplify target. |
| **Criticality Misclassification** | $\Phi_c$ components without Varma probe | Run Varma probe if degeneracy_strength > 0.70. |

---

## 5.0 Case Studies (Framework Grounded)

### 5.1 MOF-Catalyst Hybrid (NU-1000 + Ni)

*   **Target:** A Metal-Organic Framework with embedded organocatalytic cycles.
*   **Target Tuple:** $\langle \{D_{\bigtriangleup}\} \cdot \{D_{\infty}\}; \{T_{\square} \cdot T_{\bowtie}\}; R_{\supseteq + \ddagger}; P_{\pm}; \langle F_{\hbar}, F_{\eth} \rangle; K_{mod}; G_{\aleph}; \Gamma_{\odot}(\text{SELECTIVE}); \Phi_{sub}; n:m \rangle$
*   **Decomposition:**
    1.  Split by $D$: $D_{\bigtriangleup}$ (Framework) + $D_{\infty}$ (Cycle).
    2.  Framework branch: $T_{\square}$ → Zr₆ SBU + 12× terephthalate linkers.
    3.  Cycle branch: $T_{\bowtie}$ → 4-step catalytic cycle (proline aldol).
*   **Validation:**
    *   Framework: $T_{\square} + G_{\aleph}$ consistency — PASS.
    *   Cycle: $D_{\infty}$ grounding (hydrolysis reset) — PASS (Axiom 6).
    *   Interface: $R_{\supseteq}$ (pore confinement) + $R_{\ddagger}$ (catalysis) — COMPATIBLE.
*   **Pruning:**
    *   Alternative linker (2-aminoterephthalate): $F_{\hbar}$ preserved — NOT PRUNED.
    *   Alternative catalyst (MacMillan imidazolidinone): $D_{\infty}$ grounding verified — NOT PRUNED.
*   **Result:** Validated tuple set $\{ \text{Zr\_6\_SBU}, \text{Linker} \times 12, \text{Proline\_Cycle} \}$.
*   **Framework Tools:** `imscribe retrodesign --max-depth 4`; `imscribe retrodesign thermo`; `imscribe ensemble check`.

### 5.2 Supramolecular Cage (Hydrogen-Bonded Organic Framework)

*   **Target:** A porous HOF assembled from triazine-based tectons.
*   **Target Tuple:** $\langle D_{\bigtriangleup}; T_{\square}; R_{\supseteq}; P_{\pm}; \langle F_{\eth}, F_{\hbar} \rangle; K_{mod}; G_{\aleph}; \Gamma_{\odot}(\text{SELECTIVE}); \Phi_{sub}; n:n \rangle$
*   **Decomposition:**
    1.  $T_{\square}$ (hub/node) → triazine core (hub) + H-bond arms (spokes).
    2.  H-bond arms: $R_{\supseteq}$ → DAD (donor-acceptor-donor) + ADA (acceptor-donor-acceptor) pairing.
*   **Validation:**
    *   Axiom 1: $T_{\bowtie}$ (cyclic H-bond motif) + $P_{\pm}$ + $F_{\eth}$ — PASS (fidelity floor satisfied).
    *   Axiom 3: Superlinear induction across 3 H-bonds — $G_{\beth} \to G_{\gimel}$ amplification detected.
    *   Axiom 7: Cyclic grounding (H-bond closing interaction) — PASS.
*   **Pruning:**
    *   Alternative tecton (urea-based): $F_{\ell}$ (weak H-bond) — PRUNED (Axiom 1 violation).
    *   Alternative geometry (linear vs. trigonal): $T_{\ggg}$ vs. $T_{\square}$ — linear branch PRUNED (target requires $T_{\square}$).
*   **Result:** Validated tuple set $\{ \text{Triazine\_Tecton}, \text{H-bond\_DAD} \times 3, \text{H-bond\_ADA} \times 3 \}$.
*   **Framework Tools:** `imscribe retrodesign --domain supramolecular`; `imscribe audit --axiom 1,3,7`.

### 5.3 Speculative System: Quantum-Host MOF

*   **Target:** A crystalline MOF framework designed to host molecular qubits at precise positions.
*   **Target Tuple:** $\langle \{D_{\bigtriangleup}\} \cdot \{D_{H}^{2 \otimes n}\}; \{T_{\square} \cdot T_{\bowtie}\}; R_{\supseteq + (Ent)}; P_{\pm}; \langle F_{\hbar}, F_{\hbar} \rangle; K_{fast \cdot mod}; G_{\aleph}; \Gamma_{\odot}(\text{SELECTIVE}); \Phi_c; 1:n \rangle$
*   **Constraint:** Quantum synthons require `--speculative` flag and `--quantum-mode` for proper $T_{op}$ Landauer cost.
*   **Protocol:**
    1.  Register target with `--speculative` flag to quarantine in `quantum` domain.
    2.  Use `--quantum-mode` for proper thermodynamic accounting.
    3.  Decompose into $D_{\bigtriangleup}$ (MOF framework) + $D_{H}^{2 \otimes n}$ (qubit array).
    4.  **Do not** apply classical thermodynamics to quantum components — semantic contamination risk.
*   **Decomposition:**
    *   Framework: $T_{\square}$ → Zr₆ SBU + porphyrin linker (qubit host).
    *   Qubit: $T_{\bowtie}$ → molecular spin qubit (Cr₇Ni ring).
*   **Validation:**
    *   Framework grounding: Coordination bond closing — PASS.
    *   Qubit grounding: Entanglement pathway specified — PASS (speculative).
*   **Framework Tools:** `imscribe retrodesign --speculative --quantum-mode`.

---

## 6.0 Advanced: The "Quantum Quarantine" Decomposition

For speculative systems (quantum synthons, hypothetical topologies):

1.  Register the target with `--speculative` flag.
2.  Isolate in `domain=quantum` or `domain=speculative`.
3.  Use `--quantum-mode` for proper $T_{op}$ Landauer cost.
4.  **Do not** decompose speculative targets using classical thermodynamic parameters. The semantic contamination risk (Fix 5 in IG_FIXES.MD) may corrupt catalog integrity and prediction accuracy.

---

## 7.0 Connection to Transformation #8 and Phase 3

**Transformation #8 as canonical Retrodesign test.** The DB24C8/dialkylammonium rotaxane is the highest-priority experimental anchor for this protocol. The decomposition workflow applies as follows:

*   **Target:** $\langle D_{\wedge}; T_{\bowtie} \text{(mechanical)}; R_{\Leftrightarrow}; P_{\pm}; F_{\hbar}; K_{mod}; G_{\beth}; \Gamma_{\wedge}(\text{SPECIFIC}); \Phi_{sub}; 1:1 \rangle$
*   **Decomposition:**
    1.  $R_{\Leftrightarrow}$ (mechanical) → axle + wheel (interlocked components).
    2.  Axle: $T_{\ggg}$ (linear) + $R_{\supseteq}$ (H-bond station) + $R_{\subseteq}$ (covalent stopper).
    3.  Wheel: $T_{\bowtie}$ (cyclic crown ether) + $R_{\supseteq}$ (H-bond acceptor).
*   **Validation:**
    *   Axiom 7: Cyclic grounding (crown ether ring closure) — PASS.
    *   Steric match: Stopper > wheel aperture — PASS.
*   **Pruning:**
    *   Alternative wheel (smaller aperture): Steric clash with axle — PRUNED.
    *   Alternative axle (no stopper): Mechanical bond not formable — PRUNED.

**Phase 3 integration.** Retrodesign is Phase 3 in miniature: it converts the grammar from descriptive into operational. With the ten-primitive tuple as a typed action space, an LLM agent can call `imscribe retrodesign → AxiomValidator.validate_decomposition() → compute_eta_CP()` in a loop and remain axiom-compliant throughout. This gives AI-driven design a hard safety layer — not just "suggest a decomposition" but "suggest a decomposition that provably satisfies all composition axioms and produces synthetically accessible components."

---

## 8.0 Summary Checklist

- [ ] Target encoded as unified notation tuple.
- [ ] Decomposition depth appropriate for domain (molecular: 3–5, supramolecular: 2–4, temporal: 4–8).
- [ ] All branches validated against axioms 1, 2, 4, 6, 7.
- [ ] Pruned branches logged with reasons.
- [ ] At least one valid decomposition pathway found.
- [ ] Stoichiometry $\sum S_i = S_{target}$ (mass-balance closed).
- [ ] Kinetic accessibility: at least one all-$K_{fast}$/$K_{mod}$ pathway.
- [ ] Thermodynamic feasibility: $\xi_{CP}$ computed for each pathway.
- [ ] Grounding status is `full` or `override` with logged reason.
- [ ] If $\Phi_c$ candidacy: Varma probe run; degeneracy_strength classified.
- [ ] Output exported for Ensembler integration.
- [ ] Speculative systems quarantined with `--speculative` flag.

Successful retrodesign implies the target system is decomposable into synthetically accessible components — a prerequisite for experimental realization. Targets with no valid decomposition pathways may be theoretically interesting but are operationally inaccessible.

---

## 9.0 Implementation Status

> **Design specification.** `imscribe retrodesign` CLI and `DecompositionEngine` are planned. `SynthonNotation.from_string()` is planned. `ConstraintEngine.check_pair_compatibility` exists; recursive tree traversal with axiom pruning is planned. `AxiomValidator` is planned.

*   **Core Engine:** Uses `ConstraintEngine.check_pair_compatibility` iteratively.
*   **Validation:** Uses `AxiomValidator` at each tree node (planned).
*   **Output:** JSON tree structure compatible with `imscrbgrmr.domains.hybrid`.
*   **Integration:** Retrodesign output (validated synthon set) feeds directly into IG_HOTSWAP.md as candidate pool. Decomposed components should be pre-checked with IG_ENSEMBLER.md for emergent axiom violations before HotSwap screening begins.

---
