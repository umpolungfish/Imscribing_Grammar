---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# IΓ_PERTURBATION.md

## Controlled Perturbation Protocol

---

## 1.0 System Definition

**IΓ_PERTURBATION** performs sensitivity analysis over the ten-primitive tuple space. Where HotSwap asks "can I replace $S_{old}$ with $S_{new}$?", Perturbation asks: "given a working system, what is the **minimal primitive change** that drives it to a target new state?"

This protocol computes a **Primitive Jacobian**: which primitive, varied by one tier, produces the largest/smallest shift in $\xi_{CP}$? This is useful for fault injection, rational tuning, and distinguishing load-bearing from decorative primitives.

This protocol leverages the Imscribing Grammar v2.2 framework, utilizing axiom validation, thermodynamic efficiency metrics ($\xi_{CP}$), and primitive sensitivity scoring to identify critical control points.

---

## 2.0 Perturbation Sensitivity Classification

### 2.1 Primitive Sensitivity Matrix

| Primitive | Weight | Perturbation Impact | Typical $\Delta \xi_{CP}$ (per tier) | Sensitivity Class |
| :--- | :--- | :--- | :--- | :--- |
| **Dimensionality ($D$)** | 0.20 | **CRITICAL** (Domain shift) | +3.0–5.0 nats | Load-bearing |
| **Topology ($T$)** | 0.15 | **CRITICAL** (Structural change) | +2.5–4.5 nats | Load-bearing |
| **Recognition ($R$)** | 0.14 | **HIGH** (Mechanism change) | +1.5–3.0 nats | Load-bearing |
| **Fidelity ($F$)** | 0.12 | **MEDIUM** (Thermodynamic) | +1.0–2.5 nats | Tunable |
| **Stoichiometry ($S$)** | 0.08 | **MEDIUM** (Valency change) | +0.8–2.0 nats | Tunable |
| **Kinetic Character ($K$)** | 0.10 | **MEDIUM** (Accessibility) | +0.5–1.5 nats | Tunable |
| **Granularity ($G$)** | 0.09 | **MEDIUM** (Scale shift) | +0.5–1.5 nats | Tunable |
| **Coupling ($\Gamma$)** | 0.07 | **LOW/MEDIUM** (Partner logic) | +0.3–1.0 nats | Decorative |
| **Criticality ($\Phi$)** | 0.06 | **CONTEXT-DEPENDENT** | Variable | Emergent |
| **Polarity ($P$)** | 0.09 | **MEDIUM** (Directional) | +0.5–2.0 nats | Tunable |

**Sensitivity Classes:**
*   **Load-bearing:** Perturbation causes axiom violation or system collapse. Requires full Varma probe before modification.
*   **Tunable:** Perturbation produces predictable $\Delta \xi_{CP}$ without axiom violation. Suitable for rational optimization.
*   **Decorative:** Perturbation has minimal impact on system function. Safe for exploratory modification.

### 2.2 Fidelity & Kinetic Thresholds

*   **Fidelity Calibration:** $F$ is anchored to $\xi_{CP}$ tiers (HIGH ≤ 8.5 nats, MEDIUM 8.5–11.0 nats, LOW > 11.0 nats). A single-tier perturbation ($F_{\text{hardsign}} \to F_{\text{dh}}$) typically increases $\xi_{CP}$ by 1.0–2.5 nats, corresponding to losing ~1–2.5 bits of recognition information or weakening interactions by ~1.7–4.3 kJ/mol at 298 K.
*   **Kinetic Accessibility:** Perturbations that shift $K$ from $K_{fast} \to K_{mod}$ or $K_{mod} \to K_{slow}$ may render the system kinetically inaccessible under standard conditions. Always verify assembly pathway after $K$ perturbation.
*   **Criticality Sensitivity:** $\Phi$ perturbations are context-dependent. A $\Phi_{sub} \to \Phi_{\text{ctyogh}}$ shift may indicate emergent criticality (desirable for Phase 3 systems) or impending collapse (undesirable for stable assemblies).

### 2.3 Axiom Violation Detection

Perturbations that violate composition axioms are flagged as **CRITICAL** sensitivity:

| Axiom | Violation Condition | $\Delta \xi_{CP}$ | Action |
| :--- | :--- | :--- | :--- |
| **Axiom 1** | $T_{\text{bullseye}} + P_{\text{pipevar}} + F_{\text{beltl}}$ | $\to \infty$ (collapse) | **PRUNE** — forbidden by axiom |
| **Axiom 2** | $G_{\text{beta}}$/$\Gamma_{\text{corner}}$ assigned $G_{\text{revapostrophe}}$ scope | $\to \infty$ (propagation failure) | **PRUNE** — axiom violation |
| **Axiom 3** | Superlinear induction ignored | -0.5 to -1.0 nats (missed optimization) | **WARN** — cooperative gain lost |
| **Axiom 4** | $\Gamma_{\to}$ without $D_{\text{invomega}}$ or $R_{\ddagger}$ | $\to \infty$ (temporal grounding fail) | **PRUNE** — axiom violation |
| **Axiom 5** | $\Phi_{\text{ctyogh}}$ with independent $G/D$ assignment | Variable (degeneracy violation) | **FLAG** — requires Varma probe |
| **Axiom 6** | $D_{\text{invomega}}$ without reset mechanism | $\to \infty$ (cycle break) | **PRUNE** — axiom violation |
| **Axiom 7** | $T_{\text{bullseye}}$ without closing bond | $\to \infty$ (topology error) | **PRUNE** — axiom violation |

---

## 3.0 The Perturbation Protocol (5-Step Workflow)

### Step 1: Baseline Measurement

Compute baseline $\xi_{CP}$ and $I_{bits}$ for the reference imscription.

```bash
# CLI: Compute baseline thermodynamics
imscribe thermo carboxylic_acid_dimer --delta-g -12.0

# Output:
# Baseline: ξ_CP = 6.66 nats [6.56–6.77]
# η_CP = 2.8e-4
# Fidelity tier: ƒ^ż (HIGH)

# CLI: Compute information content
imscribe info-bits carboxylic_acid_dimer --solvent chloroform

# Output:
# I_total = 8.5 bits
# I_orientation = 3.2 bits
# I_contact = 5.3 bits
```

```python
from imscrbgrmr.thermodynamics import compute_eta_CP
from imscrbgrmr.models import Imscription

# Python: Load reference imscription
imscription = Imscription.from_catalog("carboxylic_acid_dimer")

# Compute baseline
result = compute_eta_CP(imscription, delta_g=-12.0)
print(f"Baseline ξ_CP: {result.xi_CP:.2f} nats")
```

### Step 2: Single-Primitive Sweep

Iterate through each primitive, shifting by one tier, and recompute $\xi_{CP}$.

```bash
# CLI: Run full perturbation sweep
imscribe perturb carboxylic_acid_dimer --sweep all --metric xi_CP --delta-g -12.0

# Output Table:
# ┌────────────────────┬──────────────────────────┬───────────────┬─────────────┐
# │ Primitive          │ Shift                    │ Δξ_CP (nats)  │ Sensitivity │
# ├────────────────────┼──────────────────────────┼───────────────┼─────────────┤
# │ Fidelity           │ ƒ^ż → ƒ^ð           │ +1.8          │ HIGH        │
# │ Kinetic Character  │ Ç^- → Ç^W           │ +0.3          │ LOW         │
# │ Topology           │ Þ_ò → Þ_chain       │ +4.2          │ CRITICAL    │
# │ Polarity           │ Φ_F → Φ_plus            │ +2.1          │ HIGH        │
# │ Granularity        │ Γ_β → Γ_γ         │ +0.6          │ LOW         │
# │ Grammar            │ Γ_⊗ → Γ_⊙                │ +0.4          │ LOW         │
# │ Dimensionality     │ Ð_ß → Ð_C     │ +3.5          │ CRITICAL    │
# └────────────────────┴──────────────────────────┴───────────────┴─────────────┘
```

```python
from imscrbgrmr.perturbation import PerturbationEngine

engine = PerturbationEngine()
results = engine.sweep(
    imscription=imscription,
    primitives=["F", "K", "T", "P", "G", "Γ", "D"],
    metric="xi_CP",
    delta_g=-12.0
)

# Identify most sensitive primitive
most_sensitive = max(results, key=lambda r: r.delta_xi)
print(f"Most sensitive: {most_sensitive.primitive} ({most_sensitive.delta_xi:.2f} nats)")
```

### Step 3: Fault Injection (Brittleness Analysis)

Identify the **Single Point of Failure (SPOF)**: the primitive change that causes axiom violation or system collapse.

```bash
# CLI: Run fault injection analysis
imscribe perturb carboxylic_acid_dimer --mode fault-injection --delta-g -12.0

# Result:
# ┌─────────────────────────────────────────────────────────────────┐
# │ FAULT INJECTION ANALYSIS                                        │
# ├─────────────────────────────────────────────────────────────────┤
# │ System collapses if Polarity shifts from Φ_F to Φ_plus         │
# │   → Axiom 1 Violation: Þ_ò + P_+ + ƒ^ż (no self-complement) │
# │                                                                 │
# │ System collapses if Topology shifts from Þ_ò to Þ_chain    │
# │   → Axiom 1 Violation: cyclic closure fidelity lost             │
# │                                                                 │
# │ System degrades (non-fatal) if Fidelity shifts ƒ^ż → ƒ^ð   │
# │   → Δξ_CP = +1.8 nats (within tolerance)                        │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Fault injection
fault_results = engine.fault_injection(imscription, delta_g=-12.0)

for fault in fault_results:
    if fault.collapse:
        print(f"SPOF: {fault.primitive} → {fault.new_value}")
        print(f"  Reason: {fault.axiom_violation}")
```

### Step 4: Rational Tuning (Pathfinding)

Find the cheapest path (minimum $\Delta \xi_{CP}$) between two tuples.

```bash
# CLI: Find minimal changes to reach target efficiency
imscribe perturb carboxylic_acid_dimer --target "ξ_CP < 7.5" --optimize F,K --delta-g -15.0

# Recommendation:
# ┌─────────────────────────────────────────────────────────────────┐
# │ RATIONAL TUNING PATHWAY                                         │
# ├─────────────────────────────────────────────────────────────────┤
# │ Target: ξ_CP < 7.5 nats (currently 6.66 nats)                   │
# │                                                                 │
# │ Option 1 (ΔG-driven):                                           │
# │   Increase binding energy: ΔG = -12.0 → -15.0 kJ/mol            │
# │   Predicted ξ_CP: 6.2 nats (improvement: -0.5 nats)             │
# │   Mechanism: Add electron-withdrawing substituent               │
# │                                                                 │
# │ Option 2 (F-driven):                                            │
# │   Rigidify scaffold: reduce σ_orientation by 15%                │
# │   Predicted I_gain: +0.8 bits                                   │
# │   Predicted ξ_CP: 6.1 nats (improvement: -0.6 nats)             │
# └─────────────────────────────────────────────────────────────────┘
```

```python
# Python: Pathfinding
pathway = engine.find_pathway(
    imscription=imscription,
    target_xi=7.5,
    optimizable_primitives=["F", "K", "G"],
    constraints={"T": "Þ_ò", "D": "Ð_ß"}  # Lock load-bearing primitives
)

print(f"Optimal pathway: {pathway.steps}")
print(f"Predicted Δξ_CP: {pathway.total_delta_xi:.2f} nats")
```

### Step 5: Validation & Grounding Audit

Verify perturbed states against axioms and grounding requirements.

```bash
# CLI: Validate perturbed state
imscribe perturb carboxylic_acid_dimer --validate --primitive F --new-value ƒ^ð

# Output:
# "Perturbed state axiom-compliant."
# "Grounding status: full (H-bond closing bond preserved)"

# CLI: Full audit
imscribe audit --imscription carboxylic_acid_dimer --perturbed F=ƒ^ð
```

```python
from imscrbgrmr.constraints import AxiomValidator

validator = AxiomValidator()
perturbed_imscription = imscription.copy()
perturbed_imscription.fidelity = "ƒ^ð"

report = validator.validate(perturbed_imscription)
if report.all_satisfied:
    print("Perturbed state axiom-compliant.")
else:
    print(f"Violation: {report.violations}")
```

---

## 4.0 Risk Assessment & Failure Modes

| Failure Mode | Primitive Signature | Mitigation |
| :--- | :--- | :--- |
| **Axiom Violation (Fatal)** | $T_{\text{bullseye}} + F_{\text{beltl}}$; $\Gamma_{\to}$ without $D_{\text{invomega}}$ | Hard block — perturbation rejected at validation. |
| **Load-Bearing Perturbation** | $D$, $T$, or $R$ shift without Varma probe | Require Varma probe before accepting perturbation. |
| **Kinetic Accessibility Loss** | $K_{fast} \to K_{slow}$ without pathway redesign | Add catalyst/template; switch assembly conditions. |
| **Cooperative Gain Loss** | $G_{\text{gamma}} \to G_{\text{beta}}$ ignoring Axiom 3 | Re-evaluate induction superlinearity; restore cooperative interactions. |
| **Grounding Drift** | `grounding_status` → `unverified` after perturbation | Require full/override grounding; `imscribe audit`. |
| **Over-Perturbation** | $\Delta \xi_{CP} > 5.0$ nats from baseline | Split into multi-step pathway; validate intermediate states. |
| **Criticality Misclassification** | $\Phi_{\text{ctyogh}}$ assigned without Varma probe | Run Varma probe if degeneracy_strength > 0.70. |

---

## 5.0 Case Studies (Framework Grounded)

### 5.1 Carboxylic Acid Dimer: Fidelity Tuning

*   **Context:** Optimizing the R₂²(8) homodimer for enhanced stability in cocrystal engineering.
*   **Baseline:** $D_{\text{wynn}}$, $T_{\text{bullseye}}$, $R_{\supseteq}$, $P_{\text{pipevar}}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}(\text{SPECIFIC})$, $\Phi_{sub}$, $1:1$
*   **Perturbation Sweep Results:**
    *   $F_{\text{hardsign}} \to F_{\text{dh}}$: $\Delta \xi_{CP} = +1.8$ nats (HIGH sensitivity)
    *   $K_{fast} \to K_{mod}$: $\Delta \xi_{CP} = +0.3$ nats (LOW sensitivity)
    *   $T_{\text{bullseye}} \to T_{\ggg}$: $\Delta \xi_{CP} \to \infty$ (CRITICAL — axiom violation)
*   **Rational Tuning:**
    *   Target: $\xi_{CP} < 6.0$ nats (improve from 6.66 nats).
    *   Option 1: Increase $\Delta G$ from -12.0 to -15.0 kJ/mol via electron-withdrawing substituent (e.g., trifluoroacetic acid dimer: $\Delta G \approx -18$ kJ/mol, $\xi_{CP} \approx 5.8$ nats).
    *   Option 2: Rigidify scaffold to reduce $\sigma_{orientation}$ by 15%, gaining +0.8 bits $I_{orientation}$.
*   **Fault Injection:**
    *   SPOF #1: Polarity $P_{\text{pipevar}} \to P_{+}$ (Axiom 1 violation — no self-complementarity).
    *   SPOF #2: Topology $T_{\text{bullseye}} \to T_{\ggg}$ (Axiom 1 violation — cyclic closure lost).
*   **Framework Tools:** `imscribe perturb --sweep all`; `imscribe perturb --mode fault-injection`; `imscribe perturb --target`.

### 5.2 Proline Aldol Cycle: Kinetic Trap Detection

*   **Context:** Analyzing the proline-catalyzed aldol cycle for kinetic bottlenecks.
*   **Baseline:** $D_{\text{invomega}}$, $T_{\text{bullseye}}$, $R_{\ddagger}$, $P_{\text{pipevar}}$, $F_{\text{dh}}$, $K_{mod}$, $G_{\text{gamma}}$, $\Gamma_{\to}(\text{SELECTIVE})$, $\Phi_{sub}$, $1:1$
*   **Step-by-Step Perturbation:**
    *   Enamine formation: $K_{mod}$, $\Delta G^{\ddagger} = 75$ kJ/mol — accessible.
    *   C–C bond formation: $K_{mod}$, $\Delta G^{\ddagger} = 97$ kJ/mol — rate-determining step.
    *   Hydrolysis reset: $K_{fast}$, $\Delta G^{\ddagger} = 45$ kJ/mol — rapid turnover.
*   **Kinetic Trap Detection:**
    *   Perturbation: $K_{mod} \to K_{slow}$ at C–C bond formation step.
    *   Result: $\Delta \xi_{CP} = +2.5$ nats; turnover frequency drops 10×.
    *   Mitigation: Add Lewis acid catalyst to lower $\Delta G^{\ddagger}$ to 70 kJ/mol ($K_{mod}$ restored).
*   **Axiom 6 Verification:**
    *   Reset mechanism: Hydrolysis (H₂O consumption, catalyst regeneration).
    *   Status: PASS (Axiom 6 grounded).
*   **Framework Tools:** `imscribe trajectory validate`; `imscribe perturb --primitive K`.

### 5.3 Speculative System: Quantum Imscription Perturbation

*   **Context:** Perturbing a Bell pair imscription for enhanced coherence.
*   **Baseline:** $D_{H}^{2 \otimes}$, $T_{\text{bullseye}}$, $R_{(Ent)}$, $P_{\text{pipevar}}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}(\text{SPECIFIC})$, $\Phi_{sub}$, $1:1$
*   **Constraint:** Quantum imscriptions use $T_{op} = 20$ mK for Landauer cost, not 298 K.
*   **Perturbation Sweep:**
    *   $F_{\text{hardsign}} \to F_{\text{dh}}$ (gate fidelity 99.9% → 99%): $\Delta \xi_{CP} = +2.3$ nats.
    *   $K_{fast} \to K_{mod}$ (gate time 50 ns → 200 ns): $\Delta \xi_{CP} = +0.5$ nats.
    *   $G_{\text{beta}} \to G_{\text{revapostrophe}}$ (single pair → surface code): $\Delta \xi_{CP} = -1.5$ nats (cooperative gain).
*   **Protocol:**
    1.  Register with `--speculative` flag to quarantine in `domain=quantum`.
    2.  Use `--quantum-mode` for proper Landauer cost at $T_{op}$.
    3.  **Do not** perturb quantum imscriptions using classical thermodynamic parameters — semantic contamination risk.

---

## 6.0 Advanced: The "Quantum Quarantine" Perturbation

For speculative systems (quantum imscriptions, hypothetical topologies):

1.  Register the imscription with `--speculative` flag.
2.  Isolate in `domain=quantum` or `domain=speculative`.
3.  Use `--quantum-mode` for proper $T_{op}$ Landauer cost.
4.  **Do not** perturb speculative imscriptions using classical parameters. The semantic contamination risk (Fix 5 in IΓ_FIXES.MD) may corrupt catalog integrity and prediction accuracy.

---

## 7.0 Connection to Transformation #8 and Phase 3

**Transformation #8 as canonical perturbation test.** The DB24C8/dialkylammonium rotaxane dethreading scan is the highest-priority experimental anchor for this protocol. The perturbation workflow applies as follows:

*   **Baseline:** Pseudorotaxane at threaded equilibrium ($\Delta G \approx -40$ kJ/mol, $\xi_{CP} \approx 8.5$ nats).
*   **Perturbation:** Displace axle along dethreading coordinate (0 → 5 Å).
*   **Sensitivity Map:**
    *   Plateau regime (0–4.5 Å): $\Delta \xi_{CP} = +0.5$ nats per Å (LOW sensitivity — cooperative H-bond weakening).
    *   Steric cliff (4–5 Å): $\Delta \xi_{CP} = +3.0$ nats per Å (CRITICAL sensitivity — topological barrier).
*   **Fault Injection:** Full dethreading ($>5$ Å) = system collapse ($\xi_{CP} \to \infty$, mechanical bond lost).

**Phase 3 integration.** Perturbation is Phase 3 in miniature: it converts the grammar from descriptive into operational. With the ten-primitive tuple as a typed action space, an LLM agent can call `imscribe perturb → AxiomValidator.validate() → compute_eta_CP()` in a loop and remain axiom-compliant throughout. This gives AI-driven design a hard safety layer — not just "suggest a modification" but "suggest a modification that provably satisfies all composition axioms and stays within 2.0 nats of the target efficiency."

---

## 8.0 Summary Checklist

- [ ] Baseline $\xi_{CP}$ and $I_{bits}$ computed.
- [ ] Single-primitive sweep completed for all ten primitives.
- [ ] Sensitivity classification assigned (Load-bearing / Tunable / Decorative).
- [ ] Fault injection analysis completed; SPOFs identified.
- [ ] Rational tuning pathway computed (if optimization target specified).
- [ ] Axiom Validation passes for all perturbed states.
- [ ] $\Delta \xi_{CP} < 5.0$ nats per perturbation step (or multi-step pathway defined).
- [ ] Grounding status is `full` or `override` with logged reason.
- [ ] If $\Phi_{\text{ctyogh}}$ candidacy: Varma probe run; degeneracy_strength classified.
- [ ] Load-bearing primitives ($D$, $T$, $R$) locked unless Varma probe confirms safety.

Successful perturbation implies the system is well-characterized and amenable to rational tuning — a prerequisite for Phase 3 AI-driven design. Systems with multiple SPOFs are brittle and may require redesign before optimization.

---

## 9.0 Implementation Status

> **Design specification.** `imscribe perturb` CLI commands and `PerturbationEngine` are planned. `compute_eta_CP` exists; `AxiomValidator` is planned.

*   **Engine:** Uses `compute_eta_CP` with modified primitive inputs.
*   **Axiom Check:** Validates each perturbed state against `AxiomValidator` (planned).
*   **Output:** Sensitivity heatmap (JSON/CSV) + Fault injection report + Pathway recommendations.
*   **Integration:** High-sensitivity primitives ($D$, $T$, $R$) identified by this protocol should be treated as load-bearing during IΓ_HOTSWAP.md candidate screening — a swap that perturbs a CRITICAL-sensitivity primitive requires the full Varma probe even if $\Phi$ is $\Phi_{sub}$.

---
