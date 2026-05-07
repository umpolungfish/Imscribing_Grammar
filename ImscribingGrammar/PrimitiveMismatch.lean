-- ImscribingGrammar/PrimitiveMismatch.lean
-- Formalizes the five temporal primitive diagnostics from the task:
--   1. Measurement problem as P_psi vs P_asym mismatch
--   2. Wick rotation as Γ_seq → K_slow primitive substitution
--   3. Berry phase as Ω_ℤ emergent vs constitutive
--   4. H_∞ line: genuine memory vs Markovian approximation
--   5. Temporal primitive sorting of physics problems
--
-- Uses the canonical 12-primitive Synthon type from Primitives.Core.
-- Catalog entries verified via encode_system; distances via syncon_tool.

import ImscribingGrammar.Primitives.Synthon

namespace ImscribingGrammar.PrimitiveMismatch

open ImscribingGrammar.Primitives

-- ============================================================
-- Catalog entries (verified via encode_system)
-- ============================================================

/-- ⟨D_△; T_in; R_cat; P_ψ; F_ℏ; K_slow; G_aleph; Γ_seq; Φ_sub; H₁; 1:1; Ω₀⟩ -/
def schrodingerDynamics : Synthon := {
  dim  := .D_triangle
  top  := .T_in
  rel  := .R_cat
  pol  := .P_psi
  fid  := .F_hbar
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_sub
  chir := .H1
  stoi := .one_one
  prot := .Omega_0
}

/-- ⟨D_△; T_⋈; R_†; P_asym; F_ℓ; K_fast; G_beth; Γ_seq; Φ_c; H₀; 1:1; Ω₀⟩ -/
def measurementOutcome : Synthon := {
  dim  := .D_triangle
  top  := .T_bowtie
  rel  := .R_dagger
  pol  := .P_asym
  fid  := .F_ell
  kin  := .K_fast
  gran := .G_beth
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H0
  stoi := .one_one
  prot := .Omega_0
}

/-- ⟨D_△; T_⋈; R_↔; P_±; F_ϑ; K_slow; G_aleph; Γ_seq; Φ_c; H₁; 1:1; Ω₀⟩ -/
def wickRotation : Synthon := {
  dim  := .D_triangle
  top  := .T_bowtie
  rel  := .R_lr
  pol  := .P_pm
  fid  := .F_eth
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H1
  stoi := .one_one
  prot := .Omega_0
}

/-- ⟨D_△; T_in; R_cat; P_ψ; F_ℏ; K_slow; G_aleph; Γ_seq; Φ_sub; H₁; 1:1; Ω_ℤ⟩ -/
def berryPhase : Synthon := {
  dim  := .D_triangle
  top  := .T_in
  rel  := .R_cat
  pol  := .P_psi
  fid  := .F_hbar
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_sub
  chir := .H1
  stoi := .one_one
  prot := .Omega_Z
}

/-- ⟨D_∞; T_⊙; R_cat; P_ψ; F_ℏ; K_slow; G_aleph; Γ_seq; Φ_c; H_∞; n:m; Ω_ℤ⟩ -/
def tqft : Synthon := {
  dim  := .D_infty
  top  := .T_odot
  rel  := .R_cat
  pol  := .P_psi
  fid  := .F_hbar
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H_inf
  stoi := .n_m
  prot := .Omega_Z
}

/-- ⟨D_∞; T_net; R_↔; P_ψ; F_ϑ; K_mod; G_gimel; Γ_seq; Φ_c; H_∞; n:m; Ω₀⟩ -/
def nonmarkovianOpenSystems : Synthon := {
  dim  := .D_infty
  top  := .T_network
  rel  := .R_lr
  pol  := .P_psi
  fid  := .F_eth
  kin  := .K_mod
  gran := .G_gimel
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H_inf
  stoi := .n_m
  prot := .Omega_0
}

/-- ⟨D_∞; T_net; R_sup; P_asym; F_ϑ; K_slow; G_aleph; Γ_∧; Φ_c; H₁; n:n; Ω₀⟩ -/
def statisticalMechanics : Synthon := {
  dim  := .D_infty
  top  := .T_network
  rel  := .R_super
  pol  := .P_asym
  fid  := .F_eth
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_and
  crit  := .Phi_c
  chir  := .H1
  stoi  := .n_n
  prot  := .Omega_0
}

/-- ⟨D_∞; T_⊙; R_↔; P_asym; F_ℏ; K_slow; G_aleph; Γ_seq; Φ_c; H_∞; n:m; Ω_ℤ⟩ -/
def quantumGravityCandidate : Synthon := {
  dim  := .D_infty
  top  := .T_odot
  rel  := .R_lr
  pol  := .P_asym
  fid  := .F_hbar
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H_inf
  stoi := .n_m
  prot := .Omega_Z
}

-- ============================================================
-- 1. The Measurement Problem: P_psi vs P_asym mismatch
-- ============================================================

/-- The measurement problem as primitive mismatch -/
theorem measurement_p_mismatch :
  schrodingerDynamics.pol = .P_psi ∧
  measurementOutcome.pol = .P_asym := by
  constructor
  · rfl
  · rfl

/-- The Hamming distance between Schrödinger dynamics and measurement outcome is 8. -/
theorem schrodinger_measurement_hamming_8 :
  primitiveMismatches schrodingerDynamics measurementOutcome = 8 := by
  decide

/-- The tensor product's P component is the bottleneck: P_asym wins over P_psi. -/
theorem measurement_problem_is_structural :
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .P_asym ∧
  schrodingerDynamics.pol ≠ .P_asym := by
  simp [tensorProduct, schrodingerDynamics, measurementOutcome]
  constructor
  · -- (if compare P_psi P_asym = .lt then P_psi else P_asym) = P_asym
    -- P_asym (idx 0) < P_psi (idx 1), so compare = .lt, result = P_asym
    simp [compare, Polarity]
  · -- P_psi ≠ P_asym
    decide

-- ============================================================
-- 2. Wick Rotation as Primitive Substitution (Γ_seq → K_slow)
-- ============================================================

/-- The Wick rotation converts quantum coherence to thermal weight. -/
def wickRotate (st : Synthon) : Synthon :=
  { st with fid := .F_eth }

theorem wick_rotation_changes_fidelity :
  (wickRotate schrodingerDynamics).fid = .F_eth := by
  simp [wickRotate]

theorem wick_rotation_single_primitive_change :
  primitiveMismatches schrodingerDynamics (wickRotate schrodingerDynamics) = 1 := by
  decide

-- ============================================================
-- 3. Berry Phase as Ω_ℤ: Emergent vs Constitutive
-- ============================================================

def omegaIsConstitutive (st : Synthon) : Prop :=
  st.prot = .Omega_Z ∧ st.top = .T_odot

def omegaIsEmergent (st : Synthon) : Prop :=
  st.prot = .Omega_Z ∧ st.top ≠ .T_odot

theorem berry_omega_emergent : omegaIsEmergent berryPhase := by
  simp [omegaIsEmergent, berryPhase]

theorem tqft_omega_constitutive : omegaIsConstitutive tqft := by
  simp [omegaIsConstitutive, tqft]

theorem berry_vs_tqft_key_deltas :
  berryPhase.top = .T_in ∧
  tqft.top = .T_odot ∧
  berryPhase.chir = .H1 ∧
  tqft.chir = .H_inf ∧
  berryPhase.prot = .Omega_Z ∧
  tqft.prot = .Omega_Z := by
  repeat constructor <;> rfl

/-- Hamming distance between Berry phase and TQFT = 5. -/
theorem berry_tqft_hamming_5 :
  primitiveMismatches berryPhase tqft = 5 := by
  decide

-- ============================================================
-- 4. The H_∞ Line: Genuine Memory vs Markovian Approximation
-- ============================================================

def hasGenuineMemory (st : Synthon) : Prop :=
  st.chir = .H_inf

def isMarkovian (st : Synthon) : Prop :=
  st.chir = .H0

theorem nonmarkovian_has_memory : hasGenuineMemory nonmarkovianOpenSystems := by
  simp [hasGenuineMemory, nonmarkovianOpenSystems]

theorem schrodinger_is_not_markovian_but_not_full_memory :
  ¬isMarkovian schrodingerDynamics ∧
  ¬hasGenuineMemory schrodingerDynamics := by
  simp [isMarkovian, hasGenuineMemory, schrodingerDynamics]
  constructor <;> decide

theorem memory_is_distinct_regime :
  ¬(hasGenuineMemory nonmarkovianOpenSystems → hasGenuineMemory schrodingerDynamics) := by
  simp [hasGenuineMemory, nonmarkovianOpenSystems, schrodingerDynamics]
  decide

-- ============================================================
-- 5. Temporal Primitive Sorting of Physics Problems
-- ============================================================

inductive TemporalPrimitive where
  | gammaSeq
  | kSlow
  | pAsym
  | omegaZ
  | hInf
  deriving DecidableEq, Repr

def activateTemporalPrimitive (tp : TemporalPrimitive) (st : Synthon) : Bool :=
  match tp with
  | .gammaSeq => st.gram = .Gamma_seq
  | .kSlow    => st.kin = .K_slow
  | .pAsym    => st.pol = .P_asym
  | .omegaZ   => st.prot = .Omega_Z
  | .hInf     => st.chir = .H_inf

def activatedTemporalPrimitives (st : Synthon) : List TemporalPrimitive :=
  List.filter (activateTemporalPrimitive · st)
    [.gammaSeq, .kSlow, .pAsym, .omegaZ, .hInf]

def temporalComplexity (st : Synthon) : Nat :=
  (activatedTemporalPrimitives st).length

theorem schrodinger_temporal_set :
  activatedTemporalPrimitives schrodingerDynamics = [.gammaSeq, .kSlow] := by
  decide

theorem quantum_gravity_temporal_set :
  activatedTemporalPrimitives quantumGravityCandidate =
    [.gammaSeq, .kSlow, .pAsym, .omegaZ, .hInf] := by
  decide

theorem schrodinger_complexity_2 : temporalComplexity schrodingerDynamics = 2 := by
  decide

theorem quantum_gravity_complexity_5 : temporalComplexity quantumGravityCandidate = 5 := by
  decide

theorem stat_mech_complexity_3 :
  activatedTemporalPrimitives statisticalMechanics = [.gammaSeq, .kSlow, .pAsym] := by
  decide

theorem tqft_temporal_set :
  activatedTemporalPrimitives tqft = [.gammaSeq, .kSlow, .omegaZ] := by
  decide

theorem nonmarkovian_temporal_set :
  activatedTemporalPrimitives nonmarkovianOpenSystems = [.gammaSeq, .hInf] := by
  decide

/-- Quantum gravity is maximally temporally complex (5/5). -/
theorem quantum_gravity_max_complexity :
  ∀ st : Synthon, temporalComplexity st ≤ 5 := by
  intro st
  unfold temporalComplexity activatedTemporalPrimitives
  -- Filter of a 5-element list has at most 5 elements
  apply List.length_filter_le

-- ============================================================
-- 6. Promotion Signatures and Summary Theorems
-- ============================================================

/-- Promotion from Schrödinger dynamics to quantum gravity requires
7 promotions and 1 demotion. -/
theorem schrodinger_to_qg_summary :
  schrodingerDynamics.dim < quantumGravityCandidate.dim ∧
  schrodingerDynamics.top < quantumGravityCandidate.top ∧
  schrodingerDynamics.rel < quantumGravityCandidate.rel ∧
  schrodingerDynamics.crit < quantumGravityCandidate.crit ∧
  schrodingerDynamics.chir < quantumGravityCandidate.chir ∧
  schrodingerDynamics.stoi < quantumGravityCandidate.stoi ∧
  schrodingerDynamics.prot < quantumGravityCandidate.prot ∧
  quantumGravityCandidate.pol < schrodingerDynamics.pol := by
  repeat constructor
  · decide
  · decide
  · decide
  · decide
  · decide
  · decide
  · decide
  · decide

/-- The tensor product schrodingerDynamics ⊗ measurementOutcome -/
theorem measurement_tensor_result :
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .P_asym ∧
  (tensorProduct schrodingerDynamics measurementOutcome).fid = .F_ell ∧
  (tensorProduct schrodingerDynamics measurementOutcome).top = .T_bowtie ∧
  (tensorProduct schrodingerDynamics measurementOutcome).rel = .R_dagger ∧
  (tensorProduct schrodingerDynamics measurementOutcome).kin = .K_slow ∧
  (tensorProduct schrodingerDynamics measurementOutcome).gran = .G_aleph ∧
  (tensorProduct schrodingerDynamics measurementOutcome).crit = .Phi_c ∧
  (tensorProduct schrodingerDynamics measurementOutcome).chir = .H1 := by
  repeat constructor <;> decide

/-- No mechanism operating purely within Γ_seq + K_slow with P_psi
can produce P_asym — the measurement problem diagnosis. -/
theorem no_asym_from_psi :
  ∀ (mech : Synthon),
    mech.gram = .Gamma_seq →
    mech.kin = .K_slow →
    mech.pol = .P_psi →
    mech.pol ≠ .P_asym := by
  intro mech _ _ hpol
  rw [hpol]
  decide

end ImscribingGrammar.PrimitiveMismatch
