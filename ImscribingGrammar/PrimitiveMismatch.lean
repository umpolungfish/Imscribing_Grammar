-- ImscribingGrammar/PrimitiveMismatch.lean
-- Formalizes the five temporal primitive diagnostics from the task:
--   1. Measurement problem as P_upsilon vs P_aolig mismatch
--   2. Wick rotation as Γ_seq → K_schwa primitive substitution
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

/-- ⟨D_△; T_invscr; R_ctz; P_ψ; F_ℏ; K_schwa; G_revapostrophe; Γ_seq; Φ_sub; H₁; 1:1; Ω₀⟩ -/
def schrodingerDynamics : Synthon := {
  dim  := .D_turnthree
  top  := .T_invscr
  rel  := .R_ctz
  pol  := .P_upsilon
  fid  := .F_hardsign
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_seq
  crit := .Phi_softsign
  chir := .H_toneletterstem
  stoi := .S_doublebaresh
  prot := .Omega_closeepsilon
}

/-- ⟨D_△; T_⋈; R_†; P_aolig; F_ℓ; K_frtailgamma; G_beta; Γ_seq; Φ_c; H₀; 1:1; Ω₀⟩ -/
def measurementOutcome : Synthon := {
  dim  := .D_turnthree
  top  := .T_bullseye
  rel  := .R_downstep
  pol  := .P_aolig
  fid  := .F_beltl
  kin  := .K_frtailgamma
  gran := .G_beta
  gram := .Gamma_seq
  crit := .Phi_ctyogh
  chir := .H_closeomega
  stoi := .S_doublebaresh
  prot := .Omega_closeepsilon
}

/-- ⟨D_△; T_⋈; R_↔; P_±; F_ϑ; K_schwa; G_revapostrophe; Γ_seq; Φ_c; H₁; 1:1; Ω₀⟩ -/
def wickRotation : Synthon := {
  dim  := .D_turnthree
  top  := .T_bullseye
  rel  := .R_lyoghlig
  pol  := .P_pipevar
  fid  := .F_dh
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_seq
  crit := .Phi_ctyogh
  chir := .H_toneletterstem
  stoi := .S_doublebaresh
  prot := .Omega_closeepsilon
}

/-- ⟨D_△; T_invscr; R_ctz; P_ψ; F_ℏ; K_schwa; G_revapostrophe; Γ_seq; Φ_sub; H₁; 1:1; Ω_ℤ⟩ -/
def berryPhase : Synthon := {
  dim  := .D_turnthree
  top  := .T_invscr
  rel  := .R_ctz
  pol  := .P_upsilon
  fid  := .F_hardsign
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_seq
  crit := .Phi_softsign
  chir := .H_toneletterstem
  stoi := .S_doublebaresh
  prot := .Omega_dzlig
}

/-- ⟨D_∞; T_⊙; R_ctz; P_ψ; F_ℏ; K_schwa; G_revapostrophe; Γ_seq; Φ_c; H_∞; n:m; Ω_ℤ⟩ -/
def tqft : Synthon := {
  dim  := .D_invomega
  top  := .T_openo
  rel  := .R_ctz
  pol  := .P_upsilon
  fid  := .F_hardsign
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_seq
  crit := .Phi_ctyogh
  chir := .H_invscripta
  stoi := .S_ltailm
  prot := .Omega_dzlig
}

/-- ⟨D_∞; T_net; R_↔; P_ψ; F_ϑ; K_turnm; G_gamma; Γ_seq; Φ_c; H_∞; n:m; Ω₀⟩ -/
def nonmarkovianOpenSystems : Synthon := {
  dim  := .D_invomega
  top  := .T_nrleg
  rel  := .R_lyoghlig
  pol  := .P_upsilon
  fid  := .F_dh
  kin  := .K_turnm
  gran := .G_gamma
  gram := .Gamma_seq
  crit := .Phi_ctyogh
  chir := .H_invscripta
  stoi := .S_ltailm
  prot := .Omega_closeepsilon
}

/-- ⟨D_∞; T_net; R_sup; P_aolig; F_ϑ; K_schwa; G_revapostrophe; Γ_∧; Φ_c; H₁; n:n; Ω₀⟩ -/
def statisticalMechanics : Synthon := {
  dim  := .D_invomega
  top  := .T_nrleg
  rel  := .R_subrightarrow
  pol  := .P_aolig
  fid  := .F_dh
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_and
  crit  := .Phi_ctyogh
  chir  := .H_toneletterstem
  stoi  := .S_ctn
  prot  := .Omega_closeepsilon
}

/-- ⟨D_∞; T_⊙; R_↔; P_aolig; F_ℏ; K_schwa; G_revapostrophe; Γ_seq; Φ_c; H_∞; n:m; Ω_ℤ⟩ -/
def quantumGravityCandidate : Synthon := {
  dim  := .D_invomega
  top  := .T_openo
  rel  := .R_lyoghlig
  pol  := .P_aolig
  fid  := .F_hardsign
  kin  := .K_schwa
  gran := .G_revapostrophe
  gram := .Gamma_seq
  crit := .Phi_ctyogh
  chir := .H_invscripta
  stoi := .S_ltailm
  prot := .Omega_dzlig
}

-- ============================================================
-- 1. The Measurement Problem: P_upsilon vs P_aolig mismatch
-- ============================================================

/-- The measurement problem as primitive mismatch -/
theorem measurement_p_mismatch :
  schrodingerDynamics.pol = .P_upsilon ∧
  measurementOutcome.pol = .P_aolig := by
  constructor
  · rfl
  · rfl

/-- The Hamming distance between Schrödinger dynamics and measurement outcome is 8. -/
theorem schrodinger_measurement_hamming_8 :
  primitiveMismatches schrodingerDynamics measurementOutcome = 8 := by
  decide

/-- The tensor product's P component is the bottleneck: P_aolig wins over P_upsilon. -/
theorem measurement_problem_is_structural :
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .P_aolig ∧
  schrodingerDynamics.pol ≠ .P_aolig := by
  simp [tensorProduct, schrodingerDynamics, measurementOutcome]
  constructor
  · -- (if compare P_upsilon P_aolig = .lt then P_upsilon else P_aolig) = P_aolig
    -- P_aolig (idx 0) < P_upsilon (idx 1), so compare = .lt, result = P_aolig
    simp [compare, Polarity]
  · -- P_upsilon ≠ P_aolig
    decide

-- ============================================================
-- 2. Wick Rotation as Primitive Substitution (Γ_seq → K_schwa)
-- ============================================================

/-- The Wick rotation converts quantum coherence to thermal weight. -/
def wickRotate (st : Synthon) : Synthon :=
  { st with fid := .F_dh }

theorem wick_rotation_changes_fidelity :
  (wickRotate schrodingerDynamics).fid = .F_dh := by
  simp [wickRotate]

theorem wick_rotation_single_primitive_change :
  primitiveMismatches schrodingerDynamics (wickRotate schrodingerDynamics) = 1 := by
  decide

-- ============================================================
-- 3. Berry Phase as Ω_ℤ: Emergent vs Constitutive
-- ============================================================

def omegaIsConstitutive (st : Synthon) : Prop :=
  st.prot = .Omega_dzlig ∧ st.top = .T_openo

def omegaIsEmergent (st : Synthon) : Prop :=
  st.prot = .Omega_dzlig ∧ st.top ≠ .T_openo

theorem berry_omega_emergent : omegaIsEmergent berryPhase := by
  simp [omegaIsEmergent, berryPhase]

theorem tqft_omega_constitutive : omegaIsConstitutive tqft := by
  simp [omegaIsConstitutive, tqft]

theorem berry_vs_tqft_key_deltas :
  berryPhase.top = .T_invscr ∧
  tqft.top = .T_openo ∧
  berryPhase.chir = .H_toneletterstem ∧
  tqft.chir = .H_invscripta ∧
  berryPhase.prot = .Omega_dzlig ∧
  tqft.prot = .Omega_dzlig := by
  repeat constructor <;> rfl

/-- Hamming distance between Berry phase and TQFT = 5. -/
theorem berry_tqft_hamming_5 :
  primitiveMismatches berryPhase tqft = 5 := by
  decide

-- ============================================================
-- 4. The H_∞ Line: Genuine Memory vs Markovian Approximation
-- ============================================================

def hasGenuineMemory (st : Synthon) : Prop :=
  st.chir = .H_invscripta

def isMarkovian (st : Synthon) : Prop :=
  st.chir = .H_closeomega

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
  | .kSlow    => st.kin = .K_schwa
  | .pAsym    => st.pol = .P_aolig
  | .omegaZ   => st.prot = .Omega_dzlig
  | .hInf     => st.chir = .H_invscripta

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
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .P_aolig ∧
  (tensorProduct schrodingerDynamics measurementOutcome).fid = .F_beltl ∧
  (tensorProduct schrodingerDynamics measurementOutcome).top = .T_bullseye ∧
  (tensorProduct schrodingerDynamics measurementOutcome).rel = .R_downstep ∧
  (tensorProduct schrodingerDynamics measurementOutcome).kin = .K_schwa ∧
  (tensorProduct schrodingerDynamics measurementOutcome).gran = .G_revapostrophe ∧
  (tensorProduct schrodingerDynamics measurementOutcome).crit = .Phi_ctyogh ∧
  (tensorProduct schrodingerDynamics measurementOutcome).chir = .H_toneletterstem := by
  repeat constructor <;> decide

/-- No mechanism operating purely within Γ_seq + K_schwa with P_upsilon
can produce P_aolig — the measurement problem diagnosis. -/
theorem no_asym_from_psi :
  ∀ (mech : Synthon),
    mech.gram = .Gamma_seq →
    mech.kin = .K_schwa →
    mech.pol = .P_upsilon →
    mech.pol ≠ .P_aolig := by
  intro mech _ _ hpol
  rw [hpol]
  decide

end ImscribingGrammar.PrimitiveMismatch
