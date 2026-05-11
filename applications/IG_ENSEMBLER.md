---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# IΓ_ENSEMBLER.md

## Multi-Imscription Composition Verification

---

## 1.0 System Definition

**IΓ_ENSEMBLER** verifies the compatibility of multi-imscription systems. Every case in the standard validation table is a *single* imscription. Real systems are composed: a rotaxane is $R_{\Leftrightarrow}$ *plus* an H-bonding station *plus* a stopper.

Composition can produce **Emergent Axiom Violations**. Axiom 2 says a $G_{\text{beta}}$/$\Gamma_{\text{corner}}(\text{SPECIFIC})$ component can't propagate globally, but what happens when you *compose* two such components with different $T$? The Ensembler checks pairwise and higher-order axiom compatibility, computes the $\xi_{CP}$ of the *composed system*, and identifies emergent $\Phi_{\text{ctyogh}}$ candidacy.

This protocol leverages the Imscribing Grammar v2.2 framework, utilizing axiom validation, thermodynamic efficiency metrics ($\xi_{CP}$), and criticality probing to ensure compatibility prior to assembly.

---

## 2.0 Pre-Assembly Compatibility Criteria

Candidate ensemble components must pass a rigorous interface check via the `ConstraintEngine`. Compatibility is determined by primitive alignment within defined tolerances.

### 2.1 Primitive Matching Matrix

| Primitive | Requirement | Rationale |
| :--- | :--- | :--- |
| **Dimensionality ($D$)** | **Compatible Sets** | Components must share at least one operational domain. $D_{\text{wynn}}$ (molecular) and $D_{\bigtriangleup}$ (supramolecular) are compatible; $D_{\text{invomega}}$ (temporal) requires explicit coupling mechanism. |
| **Topology ($T$)** | **Compatible or Orthogonal** | $T_{\text{bullseye}}$ (cyclic) + $T_{\ggg}$ (chain) = compatible (e.g., cyclic stopper on linear axle). $T_{\text{bullseye}}$ + $T_{\text{bullseye}}$ = requires steric/geometry check. |
| **Stoichiometry ($S$)** | **Mass-Balance Consistent** | Sum of component $S$ values must equal ensemble $S$. A $1:1$ axle + $1:1$ wheel = $1:1$ pseudorotaxane; $1:1$ axle + $n:n$ wheel = requires $n=1$ or defect tolerance. |
| **Recognition ($R$)** | **Non-Conflicting** | $R_{\supseteq}$ (non-covalent) + $R_{\subseteq}$ (covalent) = compatible (e.g., H-bond station + covalent stopper). $R_{\Leftrightarrow}$ (mechanical) + $R_{\Leftrightarrow}$ = requires interpenetration check. |
| **Polarity ($P$)** | **Complementary or Neutral** | $P_{+}$ (acceptor) + $P_{-}$ (donor) = compatible. $P_{\text{pipevar}}$ (self-complementary) = compatible with any. $P_{+}$ + $P_{+}$ = requires mediation (solvent, counterion). |
| **Fidelity ($F$)** | **$F_{ensemble} \geq \max(ƒ_i) - 1$ tier** | Ensemble fidelity cannot exceed weakest component by more than one tier without cooperative amplification (Axiom 3). |
| **Kinetic Character ($K$)** | **Assembly-Accessible** | At least one component must have $K_{fast}$ or $K_{mod}$ for assembly step. All-$K_{slow}$ ensembles are kinetically inaccessible. |
| **Granularity ($G$)** | **Hierarchically Consistent** | $G_{\text{beta}}$ (local) components can assemble to $G_{\text{gamma}}$ (mesoscale) or $G_{\text{revapostrophe}}$ (global) ensembles via Axiom 3 (superlinear induction). |
| **Criticality ($\Phi$)** | **Emergent Candidacy Detected** | Two $\Phi_{sub}$ components can form $\Phi_{\text{ctyogh}}$ ensemble. Ensemble $\Phi_{\text{ctyogh}}$ requires Varma probe on *assembled* system, not individual components. |

### 2.2 Fidelity & Interface Thresholds

*   **Fidelity Calibration:** $F$ is anchored to $\xi_{CP}$ tiers (HIGH ≤ 8.5 nats, MEDIUM 8.5–11.0 nats, LOW > 11.0 nats). The ensemble should not increase inefficiency beyond $\Delta \xi_{CP} < 2.0$ nats relative to the sum of isolated components. A 2-nat drift corresponds to losing ~2 bits of recognition information or weakening interactions by ~3.4 kJ/mol at 298 K.
*   **Interface Overhead ($I_{interface}$):** Every imscription-imscription interface introduces information overhead. Typical values:
    *   $R_{\supseteq}$ + $R_{\supseteq}$ (H-bond network): 0.5–1.5 bits
    *   $R_{\subseteq}$ + $R_{\supseteq}$ (covalent + non-covalent): 1.0–2.0 bits
    *   $R_{\Leftrightarrow}$ + $R_{\supseteq}$ (mechanical + H-bond): 2.0–4.0 bits (steric alignment cost)
*   **Cooperative Gain ($F_{coop}$):** Superlinear induction (Axiom 3) can offset interface overhead. Triple H-bond arrays show $F_{coop} \approx 1.25$–1.4×, reducing effective $\xi_{CP}$ by 0.5–1.0 nats.

### 2.3 Network Topology Stoichiometry Tolerance

For $G_{\text{revapostrophe}}$ ensembles (crystal lattices, MOF networks, extended supramolecular frameworks), exact $S$ matching is relaxed via the `--allow-defect-fraction` flag:

```bash
imscribe ensemble check --components node,linker --allow-defect-fraction 0.25
```

This permits partial substitution up to 25% defect fraction without violating mass balance, because network topology ($T_{\square}$) absorbs per-node variance. The flag is **restricted to $G_{\text{revapostrophe}}$** — molecular-scale ensembles ($G_{\text{beta}}$) and mesoscale ensembles ($G_{\text{gamma}}$) retain exact $S$ matching.

---

## 3.0 The Ensembler Protocol (5-Step Workflow)

### Step 1: Component Registration

Load all constituent imscriptions into a temporary ensemble catalog.

```python
from imscrbgrmr.registry import EnsembleCatalog

ensemble = EnsembleCatalog()
ensemble.add("rotaxane_axle")       # D_∧, T_≫, R_⊇, P_+, F_ℏ, Ç_-, Γ_β, Γ_⊗, Φ_sub, 1:1
ensemble.add("macrocycle_wheel")    # D_∧, T_⋈, R_⊇, P_-, F_ℏ, Ç_-, Γ_β, Γ_⊙, Φ_sub, 1:1
ensemble.add("stopper_group")       # D_∧, T_⋈, R_⊆, P_±, F_ℏ, Ç_W, Γ_β, Γ_⊗, Φ_sub, 1:1
```

### Step 2: Pairwise Compatibility Matrix

Check all $N \times N$ interactions for primitive conflicts.

```bash
# CLI: Run pairwise compatibility check
imscribe ensemble check --pairwise --components axle,wheel,stopper

# Output:
# ┌─────────────────────────────────────────────────────────────┐
# │ PAIRWISE COMPATIBILITY MATRIX                               │
# ├─────────────────────────────────────────────────────────────┤
# │ Axle ↔ Wheel:   COMPATIBLE (R_⊇, P_+ + P_- complementarity) │
# │ Wheel ↔ Stopper: COMPATIBLE (R_⊆ + R_⊇, steric match OK)    │
# │ Axle ↔ Stopper:  INCOMPATIBLE (Steric clash: R_⊆ barrier)   │
# └─────────────────────────────────────────────────────────────┘
```

### Step 3: Emergent Property Detection

Scan for properties that arise only in composition:

1.  **Emergent Criticality:** Do two $\Phi_{sub}$ components form a $\Phi_{\text{ctyogh}}$ ensemble?
2.  **Granularity Amplification:** Does $G_{\text{beta}} + G_{\text{beta}} \to G_{\text{gamma}}$? (Axiom 3)
3.  **Interface Fidelity:** Does the interface lower overall $F$?

```bash
# CLI: Scan for emergent criticality
imscribe ensemble probe --criticality --components axle,wheel

# Result:
# "Ensemble candidacy score: 0.65 (Power-Law Regime). Individual components: 0.20."
# "Granularity amplification detected: Γ_β + Γ_β → Γ_γ (induction ratio: 2.8×)"
```

### Step 4: System-Level Thermodynamics

Compute the efficiency of the *assembly event*, not just the components.

```python
from imscrbgrmr.thermodynamics import compute_eta_CP

# Assembly ΔG for rotaxane formation (template-directed clipping)
delta_g_assembly = -85.0  # kJ/mol (literature value for DB24C8 + ammonium axle)

result = compute_eta_CP(
    imscription=None,  # Ensemble mode
    delta_g=delta_g_assembly,
    ensemble_components=["axle", "wheel", "stopper"],
    interface_overhead=2.5  # bits (R_⇔ + R_⊇ interface)
)

print(f"Ensemble η_CP: {result.eta_CP:.2e}")
print(f"Ensemble ξ_CP: {result.xi_CP:.2f} nats")
```

```bash
# CLI equivalent
imscribe ensemble thermo --delta-g-assembly -85.0 --interface-overhead 2.5

# Output:
# System η_CP: 1.2e-4
# System ξ_CP: 9.03 nats (MEDIUM)
# Interface Overhead: 2.5 bits
# Cooperative Gain: 0.8 nats (superlinear induction detected)
```

### Step 5: Axiom Validation & Grounding Audit

Run the assembled ensemble against all composition axioms.

```python
from imscrbgrmr.constraints import AxiomValidator

validator = AxiomValidator()
report = validator.validate_ensemble(ensemble)

if not report.all_satisfied:
    print(f"Ensemble blocked: {report.violations}")
else:
    print("Ensemble axiom-compliant. Proceeding to grounding audit.")
    
# Grounding audit
from imscrbgrmr.registry import global_catalog
global_catalog.register_ensemble("rotaxane_ensemble", ensemble, grounding_status="full")
```

```bash
# CLI: Grounding audit
imscribe audit --ensemble rotaxane_ensemble --status unverified

# Output:
# "All cyclic components have named closing bonds (Axiom 7: PASS)"
# "All temporal components have reset mechanisms (Axiom 6: N/A)"
# "Grounding status: full"
```

---

## 4.0 Risk Assessment & Failure Modes

| Failure Mode | Primitive Signature | Mitigation |
| :--- | :--- | :--- |
| **Constraint Collapse** | $F_{ensemble} \ll \min(ƒ_i)$ | Hard block — enforce $F$ floor at query time (Axiom 1). |
| **Interface Overhead Spike** | $I_{interface} > 4.0$ bits | Redesign interface geometry; add cooperative interactions (Axiom 3). |
| **Axiom Violation (Emergent)** | $T_{\text{bullseye}} + F_{\text{beltl}}$ in composition; $\Gamma_{\to}$ without $D_{\text{invomega}}$ | Registration blocked; detailed violation report. |
| **Steric Clash** | $R_{\Leftrightarrow}$ + $R_{\Leftrightarrow}$ without interpenetration pathway | Run relaxed scan; verify dethreading barrier < 125 kJ/mol. |
| **Stoichiometry Mismatch** | $S_{ensemble} \neq \sum Σ_i$ (molecular scale) | Exact match mandatory for $G_{\text{beta}}$/$G_{\text{gamma}}$; `--allow-defect-fraction` for $G_{\text{revapostrophe}}$ only. |
| **Kinetic Trap (Assembly)** | All-$K_{slow}$ components | Add template/catalyst; switch to $K_{mod}$ assembly pathway. |
| **Criticality Disruption** | Unconfirmed $\Phi_{\text{ctyogh}}$ candidacy, premature assembly | Run Varma probe on *assembled* system if degeneracy_strength > 0.70. |
| **Grounding Drift** | `grounding_status` → `unverified` | Require full/override grounding before assembly; `imscribe audit`. |

---

## 5.0 Case Studies (Framework Grounded)

### 5.1 Rotaxane Ensemble (Mechanical Bond + H-Bond Station)

*   **Context:** Assembling a [2]rotaxane from axle, wheel, and stopper components.
*   **Components:**
    *   Axle: $D_{\text{wynn}}$, $T_{\ggg}$, $R_{\supseteq}$ (H-bond station), $P_{+}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}(\text{SPECIFIC})$, $\Phi_{sub}$, $1:1$
    *   Wheel: $D_{\text{wynn}}$, $T_{\text{bullseye}}$, $R_{\supseteq}$ (crown ether), $P_{-}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\odot}(\text{SELECTIVE})$, $\Phi_{sub}$, $1:1$
    *   Stopper: $D_{\text{wynn}}$, $T_{\text{bullseye}}$, $R_{\subseteq}$ (covalent), $P_{\text{pipevar}}$, $F_{\text{hardsign}}$, $K_{mod}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}(\text{SPECIFIC})$, $\Phi_{sub}$, $1:1$
*   **Pairwise Check:**
    *   Axle ↔ Wheel: COMPATIBLE ($P_{+}$ + $P_{-}$ complementarity, $R_{\supseteq}$ + $R_{\supseteq}$)
    *   Wheel ↔ Stopper: COMPATIBLE (steric match: stopper > wheel aperture)
    *   Axle ↔ Stopper: COMPATIBLE (covalent attachment site)
*   **Emergent Properties:**
    *   $R_{\Leftrightarrow}$ (mechanical bond) emerges upon assembly — not present in any component.
    *   Interface overhead: 2.5 bits ($R_{\Leftrightarrow}$ + $R_{\supseteq}$ alignment cost).
    *   Ensemble $\Phi_{\text{ctyogh}}$ candidacy: 0.45 (logarithmic regime) — not critical, but enhanced cooperativity.
*   **Thermodynamics:** $\Delta G_{assembly} = -85.0$ kJ/mol (template-directed clipping). $\xi_{CP} = 9.03$ nats (MEDIUM).
*   **Framework Tools:** `imscribe ensemble check --pairwise`; `imscribe ensemble probe --criticality`; `imscribe ensemble thermo`.

### 5.2 MOF Secondary Building Unit Ensemble (Zr₆ Node + Linkers)

*   **Context:** Assembling UiO-66 from Zr₆O₄(OH)₄ SBU and terephthalate linkers.
*   **Components:**
    *   SBU: $D_{\bigtriangleup}$, $T_{\square}$, $R_{\supseteq}$ (coordination), $P_{+}$, $F_{\text{hardsign}}$, $K_{mod}$, $G_{\text{revapostrophe}}$, $\Gamma_{\odot}(\text{SELECTIVE})$, $\Phi_{sub}$, $1:12$
    *   Linker: $D_{\bigtriangleup}$, $T_{\ggg}$, $R_{\supseteq}$ (carboxylate), $P_{-}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}(\text{SPECIFIC})$, $\Phi_{sub}$, $1:1$
*   **Pairwise Check:**
    *   SBU ↔ Linker: COMPATIBLE ($P_{+}$ + $P_{-}$ complementarity, coordination geometry match).
    *   Linker ↔ Linker: COMPATIBLE (π-stacking, $R_{\supseteq}$, non-conflicting).
*   **Emergent Properties:**
    *   $G_{\text{revapostrophe}}$ (global) emerges from $G_{\text{revapostrophe}}$ (SBU) + $G_{\text{beta}}$ (linker) — granularity amplification via network topology.
    *   Interface overhead: 1.0 bits (coordination bond alignment).
    *   Cooperative gain: 0.5 nats (superlinear induction across 12 linkers).
*   **Network Tolerance:** `--allow-defect-fraction 0.25` — up to 25% missing-linker defects documented in UiO-66 without topology collapse.
*   **Framework Tools:** `imscribe ensemble check --allow-defect-fraction 0.25`; `imscribe criticality-probe`.

### 5.3 Speculative Ensemble (Boronate Verdazyl Triangle + Magnetic Lattice)

*   **Context:** Integrating a novel frustrated magnetic triangle into a supramolecular lattice.
*   **Constraint:** The system contains sulfur bridges and boronate esters not fully accounted for in standard grounding libraries.
*   **Protocol:**
    1.  Register components with `--speculative` flag to quarantine in the `quantum` or `speculative` domain.
    2.  Use `--override-grounding` with `--override-reason` to bypass Axiom 7 checks if the closing bond mechanism is theoretical.
    3.  **Do not** assemble speculative ensembles into grounded molecular systems without empirical validation. Semantic contamination risk may corrupt catalog integrity and prediction accuracy.

---

## 6.0 Advanced: The "Quantum Quarantine" Ensemble

For speculative ensembles (quantum imscriptions, hypothetical topologies):

1.  Register all components with `--speculative` flag.
2.  Isolate in `domain=quantum` or `domain=speculative`.
3.  Do not attempt to assemble speculative ensembles with grounded molecular systems. The semantic contamination risk (Fix 5 in IΓ_FIXES.MD) may corrupt catalog integrity and prediction accuracy.

---

## 7.0 Connection to Transformation #8 and Phase 3

**Transformation #8 as canonical $\Phi_{\text{ctyogh}}$ Ensemble test.** The DB24C8/dialkylammonium pseudorotaxane is the highest-priority experimental anchor for this protocol. The ensemble consists of:

*   Axle: $D_{\text{wynn}}$, $T_{\ggg}$, $R_{\supseteq}$ (H-bond station), $P_{+}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\text{corner}}$, $\Phi_{sub}$, $1:1$
*   Wheel: $D_{\text{wynn}}$, $T_{\text{bullseye}}$, $R_{\supseteq}$ (crown ether), $P_{-}$, $F_{\text{hardsign}}$, $K_{fast}$, $G_{\text{beta}}$, $\Gamma_{\odot}$, $\Phi_{sub}$, $1:1$

The steric-cliff transition state at ~4–5 Å dethreading coordinate is the first candidate where ensemble degeneracy_strength ≥ 0.70 (logarithmic class) may be achievable from a relaxed scan. If confirmed:

*   The pseudorotaxane becomes the first empirically grounded $\Phi_{\text{ctyogh}}$ ensemble.
*   The plateau regime (~20–50 kJ/mol H-bond weakening) maps to the $K_{mod}$ assembly window — kinetically accessible without full dethreading.
*   The steric window width ($\sigma_{steric}$) directly refines $I_{interface}$ for $R_{\Leftrightarrow}$ ensembles.

**Phase 3 integration.** Ensembling is Phase 3 in miniature: it converts the grammar from descriptive into operational. With the ten-primitive tuple as a typed action space, an LLM agent can call `imscribe ensemble check → AxiomValidator.validate_ensemble() → compute_eta_CP()` in a loop and remain axiom-compliant throughout. This gives AI-driven design a hard safety layer — not just "generate a plausible assembly" but "generate an ensemble that provably satisfies all composition axioms and stays within 2.0 nats of the target efficiency."

---

## 8.0 Summary Checklist

- [ ] All components registered in ensemble catalog.
- [ ] Pairwise compatibility matrix: all pairs COMPATIBLE or resolved.
- [ ] Dimensionality $D$ compatible (shared operational domain).
- [ ] Topology $T$ compatible or orthogonal (no steric clash).
- [ ] Stoichiometry $S$ mass-balance consistent (or `--allow-defect-fraction` for $G_{\text{revapostrophe}}$).
- [ ] Recognition $R$ non-conflicting.
- [ ] Polarity $P$ complementary or neutral.
- [ ] Fidelity $F_{ensemble} \geq \max(ƒ_i) - 1$ tier (or cooperative amplification documented).
- [ ] Kinetic Character $K$: at least one $K_{fast}$ or $K_{mod}$ for assembly.
- [ ] Interface overhead $I_{interface} < 4.0$ bits (or redesign required).
- [ ] Axiom Validation passes (especially Axioms 1, 3, 6, 7).
- [ ] $|\Delta \xi_{CP}| < 2.0$ nats relative to isolated components.
- [ ] Grounding status is `full` or `override` with logged reason.
- [ ] If $\Phi_{\text{ctyogh}}$ candidacy: Varma probe run on *assembled* system; degeneracy_strength classified.
- [ ] Emergent property detection complete (criticality, granularity, fidelity).

Successful ensembling implies the system has achieved a degree of modularity comparable to software architectures — rare in static chemical systems, most likely in dynamic covalent networks, solvothermal MOF systems, reversible organocatalytic cycles, and mechanically interlocked molecules.

---

## 9.0 Implementation Status

> **Design specification.** `imscribe ensemble` CLI commands and `EnsembleCatalog` are planned. `ConstraintEngine.check_pair_compatibility` exists for pairwise checks; N-body extension is planned.

*   **Input:** List of imscription names or JSON tuples.
*   **Engine:** Extended `ConstraintEngine` with N-body interaction support (planned).
*   **Output:** Compatibility report + Emergent property flags + Thermodynamic analysis.
*   **Integration:** Multi-component systems must pass Ensembler pairwise check before IΓ_HOTSWAP.md candidate screening. Emergent $\Phi_{\text{ctyogh}}$ (score ≥ 0.70) at ensemble level requires Varma probe on the *assembled* system, not individual components.

---
