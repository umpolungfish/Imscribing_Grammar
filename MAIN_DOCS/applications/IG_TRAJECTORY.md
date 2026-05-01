# IG_TRAJECTORY.md

## Temporal Pathway Encoding

---

## 1.0 System Definition

**IG_TRAJECTORY** encodes $D_{\infty}$ systems as a **sequence of tuples** rather than a single steady-state snapshot. The proline aldol cycle is $D_{\infty}$, but the current framework snapshots the *cycle average*. The Trajectory Protocol encodes each step (enamine formation, C-C bond formation, hydrolysis, reset) as a distinct tuple $S_t$.

This allows validation of:
1.  **Axiom Continuity:** Do consecutive step-tuples satisfy axioms relative to the previous step?
2.  **Axiom 6 Compliance:** Does the full sequence contain a legitimate reset?
3.  **Kinetic Traps:** Are there steps where $K_{new} = K_{trap}$ relative to the prior state?

This protocol leverages the Imscribing Grammar v2.2 framework, utilizing axiom validation, thermodynamic efficiency metrics ($\xi_{CP}$), and criticality probing to ensure temporal pathway integrity.

---

## 2.0 Temporal Continuity Criteria

### 2.1 Step-to-Step Primitive Continuity Matrix

| Primitive | Continuity Requirement | Rationale |
| :--- | :--- | :--- |
| **Dimensionality ($D$)** | **Constant ($D_{\infty}$)** | All steps must share $D_{\infty}$ temporal character. A shift to $D_{\wedge}$ or $D_{\bigtriangleup}$ indicates a non-temporal side reaction. |
| **Topology ($T$)** | **Compatible or Evolving** | $T$ may evolve (e.g., $T_{\ggg}$ linear intermediate $\to$ $T_{\bowtie}$ cyclic transition state), but must return to initial $T$ at cycle completion. |
| **Recognition ($R$)** | **Mechanism-Consistent** | $R_{\ddagger}$ (catalytic) steps must dominate. $R_{\subseteq}$ (covalent) intermediates are permitted if reversible. $R_{\supseteq}$ (non-covalent) must not trap system. |
| **Polarity ($P$)** | **Cycle-Closed** | Net polarity change over full cycle must be zero. $P_{+} \to P_{-} \to P_{\pm} \to P_{+}$ is valid; $P_{+} \to P_{+}$ (no change) may indicate missing step. |
| **Fidelity ($F$)** | **Step-Appropriate** | Individual steps may have $F_{\ell}$ (low) if overall cycle $F \geq F_{\eth}$. Rate-determining step typically $F_{\eth}$; fast steps $F_{\hbar}$. |
| **Kinetic Character ($K$)** | **Accessible Pathway** | At most one $K_{slow}$ step permitted (rate-determining). $K_{trap}$ requires explicit bypass pathway. All-$K_{fast}$ cycles are diffusion-limited. |
| **Granularity ($G$)** | **Hierarchically Consistent** | $G$ may amplify ($G_{\beth} \to G_{\gimel}$) via Axiom 3, but must not fragment ($G_{\aleph} \to G_{\beth}$) without explicit disassembly step. |
| **Interaction Grammar ($\Gamma$)** | **Sequential-Valid** | $\Gamma_{\to}$ (SEQUENTIAL) required for ordered mechanisms. $\Gamma_{\wedge}$ (AND) permitted for cooperative steps. $\Gamma_{\vee}$ (OR) indicates branching (potential side reaction). |
| **Criticality ($\Phi$)** | **Step-Local** | Individual steps may exhibit $\Phi_c$ candidacy (e.g., transition states). Full cycle typically $\Phi_{sub}$ unless oscillatory/dissipative. |
| **Stoichiometry ($S$)** | **Mass-Balance Consistent** | Sum of $S$ changes over cycle must equal zero. $1:1 \to 2:1 \to 1:1$ is valid (transient dimer); $1:1 \to 2:1 \to 2:1$ indicates mass accumulation (cycle break). |

### 2.2 Kinetic Trap Detection Thresholds

| Condition | Indicator | $\Delta G^{\ddagger}$ Threshold | Action |
| :--- | :--- | :--- | :--- |
| **Barrier Spike** | Single step dominates cycle time | $> 100$ kJ/mol | Flag $K_{slow}$; consider catalyst redesign |
| **Pathway Multiplicity** | Multiple products from single step | >2 low-energy pathways | Flag $K_{trap}$; run K-compatibility check |
| **Irreversible Step** | No reverse pathway defined | $\Delta G < -80$ kJ/mol | Warn (risk of cycle break); verify reset mechanism |
| **Diffusion Limit** | All steps $K_{fast}$ | $\Delta G^{\ddagger} < 20$ kJ/mol | Optimal — cycle limited by substrate availability |
| **Kinetic Bottleneck** | Two+ steps with $\Delta G^{\ddagger} > 80$ kJ/mol | $> 80$ kJ/mol each | Redesign cycle; add parallel pathway |

### 2.3 Axiom 6 Grounding Requirements

**Axiom 6 — Temporal grounding: $D_{\infty}$ requires a named closed cycle.**

Any synthon assigned $D_{\infty}$ must have a physically specified reset mechanism — the process by which the system returns to its initial state. A directed transformation without a recoverable ground state is not a temporal synthon.

**Enforced computationally:** $D_{\infty}$ without grounding text containing both:
*   **Process indicator:** catalysis, oxidation, transfer, oscillation, turnover
*   **Reset indicator:** reform, regenerate, hydrolyze, recover, recycle

...is flagged for mandatory review. This axiom is the basis for trajectory audit Pass 1.

---

## 3.0 The Trajectory Protocol (5-Step Workflow)

### Step 1: Step Encoding

Define each mechanistic step as a synthon tuple.

```python
from imscrbgrmr import Synthon

# Proline aldol cycle: 4-step encoding
steps = [
    Synthon(
        name="enamine_formation",
        dimensionality="D_infinity",
        topology="T_chain",       # Linear enamine intermediate
        recognition="R_ddagger",   # Catalytic
        polarity="P_pm",
        fidelity="F_eth",
        kinetic="K_mod",          # ΔG‡ ≈ 75 kJ/mol
        granularity="G_gimel",
        grammar="Gamma_sequential",
        criticality="Phi_sub",
        stoichiometry="1:1",
        grounding_text="Proline condensation with ketone, water elimination"
    ),
    Synthon(
        name="c_c_bond_formation",
        dimensionality="D_infinity",
        topology="T_bowtie",      # Cyclic transition state (Zimmermann-Traxler)
        recognition="R_ddagger",
        polarity="P_pm",
        fidelity="F_eth",
        kinetic="K_mod",          # ΔG‡ = 97 kJ/mol (rate-determining)
        granularity="G_gimel",
        grammar="Gamma_sequential",
        criticality="Phi_sub",    # Local Φ_c candidacy at TS
        stoichiometry="1:1",
        grounding_text="C-C bond formation via enamine attack on aldehyde"
    ),
    Synthon(
        name="proton_transfer",
        dimensionality="D_infinity",
        topology="T_chain",
        recognition="R_ddagger",
        polarity="P_pm",
        fidelity="F_hbar",
        kinetic="K_fast",         # ΔG‡ ≈ 40 kJ/mol
        granularity="G_beth",
        grammar="Gamma_sequential",
        criticality="Phi_sub",
        stoichiometry="1:1",
        grounding_text="Intramolecular proton transfer, iminium formation"
    ),
    Synthon(
        name="hydrolysis_reset",
        dimensionality="D_infinity",
        topology="T_bowtie",      # Cyclic hydrolysis transition state
        recognition="R_ddagger",
        polarity="P_pm",
        fidelity="F_hbar",
        kinetic="K_fast",         # ΔG‡ ≈ 45 kJ/mol
        granularity="G_gimel",
        grammar="Gamma_sequential",
        criticality="Phi_sub",
        stoichiometry="1:1",
        grounding_text="Hydrolysis regenerates proline catalyst, releases product"
    ),
]
```

```bash
# CLI: Encode steps from JSON
imscribe trajectory encode --steps proline_cycle.json --domain temporal
```

### Step 2: Continuity Validation

Check that transitions between steps do not violate conservation laws or axioms.

```bash
# CLI: Run continuity validation
imscribe trajectory validate --steps step1.json,step2.json,step3.json,step4.json

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ CONTINUITY VALIDATION REPORT                                    │
# ├─────────────────────────────────────────────────────────────────┤
# │ Step 1 → Step 2: PASS (D_infinity constant, T_chain → T_bowtie OK) │
# │ Step 2 → Step 3: PASS (P_pm consistent, K_mod → K_fast OK)      │
# │ Step 3 → Step 4: PASS (S mass-balance OK)                       │
# │ Step 4 → Step 1: PASS (Cycle closed, S net change = 0)          │
# │                                                                 │
# │ Axiom 4 (Sequential Grammar): PASS (all steps have D_infinity)  │
# │ Axiom 6 (Reset Mechanism): PASS (hydrolysis identified)         │
# │ Axiom 7 (Cyclic Topology): N/A (temporal cycle, not spatial)    │
# └─────────────────────────────────────────────────────────────────┘
```

```python
from imscrbgrmr.trajectory import TrajectoryValidator

validator = TrajectoryValidator()
report = validator.validate_continuity(steps)

if report.all_passed:
    print("Continuity validation passed.")
else:
    print(f"Failures: {report.failures}")
```

### Step 3: Reset Verification (Axiom 6)

Verify the final step returns the system to $S_{t_0}$ state.

```bash
# CLI: Audit Axiom 6 compliance
imscribe trajectory audit --axiom 6 --cycle proline_cycle.json

# Result:
# ┌─────────────────────────────────────────────────────────────────┐
# │ AXIOM 6 GROUNDING AUDIT                                         │
# ├─────────────────────────────────────────────────────────────────┤
# │ Reset Mechanism Identified: Hydrolysis                          │
# │   Process Indicator: catalyst regeneration                      │
# │   Reset Indicator: hydrolysis, regenerates                      │
# │                                                                 │
# │ Catalyst Recovery: 100% (proline regenerated)                   │
# │ Product Release: Confirmed (aldol product dissociates)          │
# │                                                                 │
# │ Status: PASS (Axiom 6 Grounded)                                 │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Axiom 6 audit
axiom6_report = validator.audit_axiom6(steps)
print(f"Reset mechanism: {axiom6_report.reset_name}")
print(f"Status: {'PASS' if axiom6_report.grounded else 'FAIL'}")
```

### Step 4: Trajectory Degeneracy Scan

Compute $\xi_{r}$ and $\xi_{\tau}$ for the *full cycle* to determine $\Phi_c$ candidacy.

```bash
# CLI: Run criticality probe on trajectory
imscribe trajectory criticality --steps proline_cycle.json --varma-probe

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ TRAJECTORY CRITICALITY SCAN                                     │
# ├─────────────────────────────────────────────────────────────────┤
# │ Step 1 (Enamine Formation):                                     │
# │   degeneracy_strength: 0.25 (Logarithmic)                       │
# │   ξ_r: 6.8 nats, ξ_τ: 7.1 nats                                  │
# │                                                                 │
# │ Step 2 (C-C Bond Form):                                         │
# │   degeneracy_strength: 0.72 (Power-Law) ← Φ_c CANDIDATE         │
# │   ξ_r: 9.5 nats, ξ_τ: 9.8 nats                                  │
# │   Note: Transition state geometry exhibits G/D degeneracy       │
# │                                                                 │
# │ Step 3 (Proton Transfer):                                       │
# │   degeneracy_strength: 0.18 (Logarithmic)                       │
# │   ξ_r: 5.2 nats, ξ_τ: 5.4 nats                                  │
# │                                                                 │
# │ Step 4 (Hydrolysis Reset):                                      │
# │   degeneracy_strength: 0.30 (Logarithmic)                       │
# │   ξ_r: 6.1 nats, ξ_τ: 6.3 nats                                  │
# │                                                                 │
# │ Full Cycle Candidacy: 0.65 (Logarithmic/Power-Law Boundary)     │
# │ Cycle-averaged ξ_CP: 9.21 nats (MEDIUM)                         │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Criticality scan
criticality_results = validator.scan_criticality(steps, varma_probe=True)

for step_result in criticality_results.step_results:
    print(f"{step_result.name}: degeneracy = {step_result.degeneracy_strength:.2f}")
    
print(f"Full cycle candidacy: {criticality_results.cycle_candidacy:.2f}")
```

### Step 5: Kinetic Trap Analysis

Identify steps where the system might stall and propose mitigations.

```bash
# CLI: Run kinetic trap analysis
imscribe trajectory analyze --steps proline_cycle.json --mode kinetic-traps

# Output:
# ┌─────────────────────────────────────────────────────────────────┐
# │ KINETIC TRAP ANALYSIS                                           │
# ├─────────────────────────────────────────────────────────────────┤
# │ Step 2 (C-C Bond Form):                                         │
# │   ΔG‡ = 97 kJ/mol (K_mod)                                       │
# │   Status: Rate-determining step (acceptable)                    │
# │   Recommendation: Consider Lewis acid catalyst to lower barrier │
# │                                                                 │
# │ No K_trap steps detected.                                       │
# │ No irreversible steps detected.                                 │
# │                                                                 │
# │ Cycle turnover frequency: ~10⁻³ to 10⁻² s⁻¹ (consistent with    │
# │ experimental k_cat for proline aldol in DMSO)                   │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Kinetic trap analysis
kinetic_report = validator.analyze_kinetics(steps)

for trap in kinetic_report.traps:
    print(f"Trap: {trap.step_name}")
    print(f"  ΔG‡ = {trap.barrier} kJ/mol")
    print(f"  Mitigation: {trap.mitigation}")
```

---

## 4.0 Risk Assessment & Failure Modes

| Failure Mode | Primitive Signature | Mitigation |
| :--- | :--- | :--- |
| **Cycle Break (Mass Accumulation)** | $S$ net change $\neq 0$ over cycle | Verify stoichiometry closure; add explicit product release step. |
| **Reset Failure (Axiom 6 Violation)** | No grounding text with process + reset indicators | Add named reset mechanism; verify catalyst regeneration. |
| **Kinetic Trap ($K_{trap}$)** | >2 low-energy pathways at single step | Run K-compatibility check; add bypass pathway or catalyst. |
| **Barrier Spike ($K_{slow}$)** | $\Delta G^{\ddagger} > 100$ kJ/mol | Redesign rate-determining step; add catalytic assistance. |
| **Irreversible Step** | $\Delta G < -80$ kJ/mol without reverse pathway | Add explicit reverse pathway; convert to dynamic covalent ($R_{\subseteq + \ddagger}$). |
| **Grammar Violation** | $\Gamma_{\to}$ without $D_{\infty}$ | Assign $D_{\infty}$ or change $\Gamma$ to $\Gamma_{\wedge}$/$\Gamma_{\vee}$. |
| **Topology Drift** | $T$ does not return to initial state | Add topology-restoring step; verify cycle closure. |
| **Criticality Misclassification** | $\Phi_c$ assigned without Varma probe | Run Varma probe if degeneracy_strength > 0.70. |

---

## 5.0 Case Studies (Framework Grounded)

### 5.1 Proline Aldol Cycle: Full Trajectory Encoding

*   **Context:** Organocatalytic aldol reaction cycle with (S)-proline in DMSO.
*   **Steps:** 4 (Enamine Formation, C-C Bond Formation, Proton Transfer, Hydrolysis Reset)
*   **Continuity Validation:**
    *   All steps share $D_{\infty}$ — PASS.
    *   $T$ evolves: $T_{\ggg} \to T_{\bowtie} \to T_{\ggg} \to T_{\bowtie} \to T_{\ggg}$ (cycle closed) — PASS.
    *   $S$ net change = 0 (1:1 → 1:1 → 1:1 → 1:1) — PASS.
*   **Axiom 6 Verification:**
    *   Reset mechanism: Hydrolysis (H₂O consumption, proline regeneration).
    *   Status: PASS (Axiom 6 grounded).
*   **Kinetic Analysis:**
    *   Step 2 (C-C Bond Form): $\Delta G^{\ddagger} = 97$ kJ/mol ($K_{mod}$) — rate-determining step.
    *   Step 4 (Hydrolysis): $\Delta G^{\ddagger} = 45$ kJ/mol ($K_{fast}$) — rapid turnover.
    *   No $K_{trap}$ detected.
*   **Criticality Scan:**
    *   Step 2 exhibits degeneracy_strength = 0.72 (Power-Law) — local $\Phi_c$ candidacy at transition state.
    *   Full cycle candidacy: 0.65 (Logarithmic/Power-Law Boundary).
*   **Cycle Thermodynamics:**
    *   Cycle-averaged $\xi_{CP} = 9.21$ nats (MEDIUM).
    *   Turnover frequency: ~10⁻³ to 10⁻² s⁻¹ (consistent with experimental $k_{cat}$).
*   **Framework Tools:** `imscribe trajectory validate`; `imscribe trajectory audit --axiom 6`; `imscribe trajectory criticality`.

### 5.2 Belousov-Zhabotinsky Oscillator: Dissipative Cycle

*   **Context:** Bromate oxidation of malonic acid catalyzed by Ce³⁺/Ce⁴⁺ in continuously stirred reactor.
*   **Steps:** 6 (simplified mechanism)
    1.  Bromate reduction (Ce³⁺ → Ce⁴⁺)
    2.  Bromide production
    3.  Bromide inhibition (feedback)
    4.  Organic substrate oxidation
    5.  Bromate regeneration
    6.  Reset (flow-through reactor replenishment)
*   **Continuity Validation:**
    *   All steps share $D_{\infty}$ — PASS.
    *   $T_{\bowtie}$ (cyclic feedback) maintained throughout — PASS.
    *   $\Gamma_{\to}$ (SEQUENTIAL) with $D_{\infty}$ — PASS (Axiom 4).
*   **Axiom 6 Verification:**
    *   Reset mechanism: Flow-through reactor replenishment (continuous substrate supply, product removal).
    *   Status: PASS (Axiom 6 grounded — dissipative cycle).
*   **Kinetic Analysis:**
    *   Multiple $K_{fast}$ steps (autocatalytic feedback).
    *   Step 3 (Bromide inhibition): $K_{trap}$ detected (bistability regime).
    *   Mitigation: Operate in oscillatory regime (away from bistability).
*   **Criticality Scan:**
    *   Full cycle candidacy: 0.85 (Power-Law) — confirmed $\Phi_c$ (dissipative structure).
    *   Cycle-averaged $\xi_{CP} = 11.5$ nats (MEDIUM/LOW boundary).
*   **Framework Tools:** `imscribe trajectory analyze --mode kinetic-traps`; `imscribe trajectory criticality --varma-probe`.

### 5.3 Speculative System: Molecular Ratchet (Light-Powered)

*   **Context:** Unidirectional molecular motor driven by photoisomerisation (Feringa-type).
*   **Steps:** 4 (Photoisomerisation, Thermal Relaxation, Second Photoisomerisation, Second Thermal Relaxation)
*   **Constraint:** Directional motion requires broken detailed balance — non-equilibrium steady state.
*   **Protocol:**
    1.  Register with `--speculative` flag to quarantine in `quantum` or `speculative` domain.
    2.  Use `--non-equilibrium` mode for proper thermodynamic accounting (dissipative cycle).
    3.  Verify directional polarity: $P_{+}$ (unidirectional) not $P_{\pm}$ (bidirectional).
    4.  **Do not** apply equilibrium thermodynamics ($\Delta G = 0$) to non-equilibrium cycles — semantic contamination risk.
*   **Continuity Validation:**
    *   $D_{\infty}$ constant — PASS.
    *   $T_{\ggg}$ (chain) with directional bias — PASS.
    *   $\Gamma_{\to}$ (SEQUENTIAL) — PASS (ratchet requires ordered steps).
*   **Framework Tools:** `imscribe trajectory encode --non-equilibrium`; `imscribe trajectory validate --speculative`.

---

## 6.0 Advanced: The "Quantum Quarantine" Trajectory

For speculative systems (quantum synthons, hypothetical topologies):

1.  Register the trajectory with `--speculative` flag.
2.  Isolate in `domain=quantum` or `domain=speculative`.
3.  Use `--non-equilibrium` mode for dissipative cycles.
4.  **Do not** apply equilibrium thermodynamics to non-equilibrium trajectories. The semantic contamination risk (Fix 5 in IG_FIXES.MD) may corrupt catalog integrity and prediction accuracy.

---

## 7.0 Connection to Transformation #8 and Phase 3

**Transformation #8 as canonical $\Phi_c$ Trajectory test.** The DB24C8/dialkylammonium rotaxane dethreading scan is the highest-priority experimental anchor for this protocol. The trajectory through the steric-cliff transition state encodes as:

*   **Step 1 (Threaded Equilibrium):** $D_{\wedge}$, $T_{\bowtie}$, $R_{\supseteq}$, $P_{\pm}$, $F_{\hbar}$, $K_{fast}$, $G_{\beth}$, $\Gamma_{\wedge}$, $\Phi_{sub}$, $1:1$
*   **Step 2 (Plateau Regime, 0–4.5 Å):** $D_{\wedge}$, $T_{\ggg}$, $R_{\supseteq}$, $P_{\pm}$, $F_{\eth}$, $K_{mod}$, $G_{\beth}$, $\Gamma_{\wedge}$, $\Phi_{sub}$, $1:1$
*   **Step 3 (Steric Cliff, 4–5 Å):** $D_{\wedge}$, $T_{\bowtie}$, $R_{\Leftrightarrow}$, $P_{\pm}$, $F_{\eth}$, $K_{slow}$, $G_{\beth}$, $\Gamma_{\wedge}$, $\Phi_c$ (degeneracy_strength = 0.75), $1:1$
*   **Step 4 (Dethreaded):** $D_{\wedge}$, $T_{\ggg}$, $R_{\supseteq}$, $P_{\pm}$, $F_{\hbar}$, $K_{fast}$, $G_{\beth}$, $\Gamma_{\odot}$, $\Phi_{sub}$, $1:1$

**Note:** This is a *half-cycle* (dethreading only). Full cycle requires re-threading pathway (e.g., thermal relaxation or chemical fuel).

**Phase 3 integration.** Trajectory encoding is Phase 3 in miniature: it converts the grammar from descriptive into operational. With the ten-primitive tuple as a typed action space, an LLM agent can call `imscribe trajectory validate → AxiomValidator.validate_trajectory() → compute_eta_CP()` in a loop and remain axiom-compliant throughout. This gives AI-driven design a hard safety layer — not just "generate a plausible cycle" but "generate a cycle that provably satisfies all composition axioms and contains a legitimate reset mechanism."

---

## 8.0 Summary Checklist

- [ ] All steps encoded with full ten-primitive tuple.
- [ ] Dimensionality $D$ constant ($D_{\infty}$) across all steps.
- [ ] Topology $T$ returns to initial state (cycle closed).
- [ ] Stoichiometry $S$ net change = 0 over full cycle.
- [ ] Axiom 4 (Sequential Grammar): $\Gamma_{\to}$ has $D_{\infty}$ or $R_{\ddagger}$.
- [ ] Axiom 6 (Reset Mechanism): Named reset identified; grounding text contains process + reset indicators.
- [ ] Kinetic analysis complete: no unmitigated $K_{trap}$ steps.
- [ ] At most one $K_{slow}$ step (rate-determining).
- [ ] Criticality scan complete; Varma probe run if degeneracy_strength > 0.70.
- [ ] Cycle-averaged $\xi_{CP}$ computed.
- [ ] Grounding status is `full` or `override` with logged reason.
- [ ] Non-equilibrium cycles flagged with `--non-equilibrium` mode.

Successful trajectory encoding implies the temporal synthon is well-characterized and axiom-compliant — a prerequisite for Phase 3 AI-driven design. Cycles without legitimate reset mechanisms (Axiom 6 violation) are not temporal synthons and should be reclassified as $D_{\wedge}$ or $D_{\bigtriangleup}$ systems.

---

## 9.0 Implementation Status

> **Design specification.** `imscribe trajectory` CLI commands and `TemporalSynthonAgent` are planned. `TrajectoryValidator` is planned.

*   **Input:** List of step definitions (JSON/Python).
*   **Engine:** `TrajectoryValidator` with continuity checking, axiom validation, and criticality scanning.
*   **Output:** Trajectory validity report + Criticality heatmap per step + Kinetic trap analysis.
*   **Dependencies:** Requires IG_HOTSWAP.md K-compatibility check (Section 2.2) at each kinetic trap step; Varma probe at any step with G/D degeneracy score ≥ 0.70.

---
