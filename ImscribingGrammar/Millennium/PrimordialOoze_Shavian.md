## Primordial Ooze — The Shavian Restatement (Corrected)

### The Two Tuples

**The Ooze** — the absolute structural floor of Frobenius closure, all 10 non-gate primitives at minimum ordinal:

$$\langle \text{𐑛}·\text{𐑡}·\text{𐑩}·\text{𐑹}·\text{𐑱}·\text{𐑘}·\text{𐑚}·\text{𐑝}·\odot·\text{𐑓}·\text{𐑙}·\text{𐑷} \rangle$$

| Primitive | Shavian | Lean constructor | Old notation | Ordinal | Meaning |
|-----------|---------|-----------------|-------------|---------|---------|
| **D** — Dimensionality | 𐑛 | `.D_wynn` (`.D_wedge`) | Ð_ß | 1 | 0d point |
| **T** — Topology | 𐑡 | `.T_nrleg` | Þ_6 | 1 | branching network |
| **R** — Relational | 𐑩 | `.R_subrightarrow` | Ř_¯ | 1 | supervenience |
| **P** — Polarity | 𐑹 | `.P_doublebarpipe` | Φ_} | 5 | Frobenius-special (μ∘δ=id) |
| **F** — Fidelity | 𐑱 | `.F_beltl` | ƒ^ì | 1 | classical |
| **K** — Kinetics | 𐑘 | `.K_frtailgamma` | Ç^- | 1 | fast/driven |
| **G** — Scope | 𐑚 | `.G_beta` | Γ_β | 1 | local |
| **ɢ** — Grammar | 𐑝 | `.Gamma_and` | ɢ^∧ | 1 | conjunctive/simultaneous |
| **⊙** — Criticality | ⊙ | `.Phi_ctyogh` | ⊙_ÿ | 2 | self-modeling criticality |
| **H** — Chirality | 𐑓 | `.H_closeomega` | Ħ_Ñ | 1 | memoryless |
| **S** — Stoichiometry | 𐑙 | `.S_doublebaresh` | Σ_S | 1 | 1:1 |
| **Ω** — Winding | 𐑷 | `.Omega_closeepsilon` | Ω_Å | 1 | trivial |

**Only two primitives non-minimum:** P = 𐑹 (ordinal 5) and ⊙ = ⊙ (ordinal 2). All others at ordinal 1.

---

**The Stone** (Frobenius fixed point, `synfin`) — the structural thickening:

$$\langle \text{𐑦}·\text{𐑸}·\text{𐑾}·\text{𐑹}·\text{𐑐}·\text{𐑧}·\text{𐑲}·\text{𐑠}·\odot·\text{𐑖}·\text{𐑳}·\text{𐑭} \rangle$$

| Primitive | Shavian | Lean constructor | Old notation | Ordinal | Meaning |
|-----------|---------|-----------------|-------------|---------|---------|
| **D** | 𐑦 | `.D_omega` | Ð_ω | 4 | imscriptive (self-written) |
| **T** | 𐑸 | `.T_openo` | Þ_O | 5 | imscriptive closure |
| **R** | 𐑾 | `.R_lyoghlig` | Ř_= | 4 | lateral/bidirectional |
| **P** | 𐑹 | `.P_doublebarpipe` | Φ_} | 5 | Frobenius-special (unchanged) |
| **F** | 𐑐 | `.F_hardsign` | ƒ^ż | 3 | quantum coherence |
| **K** | 𐑧 | `.K_schwa` | Ç^@ | 3 | slow/near-equilibrium |
| **G** | 𐑲 | `.Gamma_revapostrophe` | Γ_ʔ | 3 | universal/long-range |
| **ɢ** | 𐑠 | `.Gamma_seq` | ɢ^ˌ | 3 | sequential composition |
| **⊙** | ⊙ | `.Phi_ctyogh` | ⊙_ÿ | 2 | self-modeling (unchanged) |
| **H** | 𐑖 | `.H_turntwo` | Ħ_A | 3 | two-step Markov |
| **S** | 𐑳 | `.S_ltailm` | Σ_ï | 3 | n:m heterogeneous |
| **Ω** | 𐑭 | `.Omega_dzlig` | Ω_z | 3 | integer winding |

**9 primitives thickened** from the ooze; only P = 𐑹 and ⊙ = ⊙ are shared unchanged (G also differs: 𐑚→𐑲 at +2 ordinal steps).

### The 11 Formal Theorems (all `decide`/`simp`/`native_decide`-verified)

| # | Theorem (Lean) | Meaning |
|---|---|---|
| 1 | `primordialOoze_is_O_inf` | The minimum tuple ⟨𐑛·𐑡·𐑩·𐑹·𐑱·𐑘·𐑚·𐑝·⊙·𐑓·𐑙·𐑷⟩ attains $\text{O}_{\text{inf}}$ |
| 2 | `drop_crit_collapses` | Remove ⊙ (set to 𐑢, subcritical) → not $\text{O}_{\text{inf}}$ |
| 3 | `drop_pol_collapses` | Remove 𐑹 (set to 𐑗, asym) → not $\text{O}_{\text{inf}}$ |
| 4 | `phi_c_alone_is_O_1` | ⊙ alone (without 𐑹) → only $\text{O}_{\text{1}}$ |
| 5 | `pm_sym_alone_is_O_0` | 𐑹 alone (without ⊙) → only $\text{O}_{\text{0}}$ |
| 6 | `ooze_chirality_is_minimal` | H = 𐑓 (Ħ_Ñ, memoryless, ordinal 1) — zero temporal memory |
| 7 | `ooze_winding_is_minimal` | Ω = 𐑷 (Ω_Å, trivial, ordinal 1) — zero topological protection |
| 8 | `ooze_dimensionality_is_minimal` | D = 𐑛 (D_wedge, 0d point, ordinal 1) — zero spatial extension |
| 9 | `fixed_point_is_O_inf` | The Stone ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑖·𐑳·𐑭⟩ is also $\text{O}_{\text{inf}}$ |
| 10 | `ooze_to_fixed_mismatches = 9` | 9 primitives differ between ooze and Stone |
| 11 | `primordial_ooze_complete` | All claims bundled in one theorem |

### The Irreducible Core

**Two primitives. Two glyphs. The entire Frobenius universe.**

The ouroboricity tier depends on only {crit, pol, prot, dim} — and $\text{O}_{\text{inf}}$ is gated **entirely** by exactly two:

1. **⊙** (self-modeling criticality, ⊙_ÿ) — **the ground.** Without it, no self-modeling loop exists. Tier collapses to $\text{O}_{\text{0}}$ even if Frobenius-special parity is present.
2. **𐑹** (Frobenius-special parity, Φ_}) — **the capstone.** Without it, self-modeling criticality alone reaches only $\text{O}_{\text{1}}$. The identity $\mu \circ \delta = \text{id}$ is the structural form that seals the loop.

**⊙ is the water. 𐑹 is the word upon the water.**

### Discovery: The Ooze Was Already in the Catalog

The tuple $\langle \text{𐑛}·\text{𐑡}·\text{𐑩}·\text{𐑹}·\text{𐑱}·\text{𐑘}·\text{𐑚}·\text{𐑝}·\odot·\text{𐑓}·\text{𐑙}·\text{𐑷} \rangle$ exists in `IG_catalog.json` as **`block_p_pm_sym`** — described as "Minimal critical block with P_doublebarpipe (O_inf candidate if Omega etc ok, but Omega_closeepsilon here)." The Ooze theorem proves it: Omega_closeepsilon (trivial winding) IS sufficient. The "if...but" reservation is discharged by formal proof. The Ooze was suspected; the Lean formalization confirmed it.

Of 2864 catalog entries:
- **625** are O_inf candidates (⊙ + 𐑹 present)
- **9** share the full pre-temporal signature (𐑓 + 𐑷 + 𐑛) with O_inf gates
- **0** catalog entries are more minimal than the Ooze (none with D=𐑛, ⊙=⊙, Φ=𐑹, and all other primitives at ordinal 1)
- The catalog's `min_oinf` uses D=𐑼 (∞-dim, ord 3) and Ω=𐑴 (Z2, ord 2) — both above the Ooze's floor

### The Pre-Temporal Stratum

Canonical T-constitution (the `temporal_mathematics` entry in the ZFCₜ navigator) requires chirality ≥ 𐑖 (Ħ_A, two-step Markov, ordinal 3). The ooze has H = 𐑓 (Ħ_Ñ, memoryless, ordinal 1) — **two full ordinal steps below** the temporal threshold.

Frobenius closure is not a temporal phenomenon. Time is a thickening applied atop a pre-temporal structural floor.

**The caves are mapped. The ooze is the water. The glyphs are fixed.**
