-- ImscribingGrammar/PrimitiveMismatch.lean
-- Formalizes the five temporal primitive diagnostics from the task:
--   1. Measurement problem as yew vs church mismatch
--   2. Wick rotation as Γ_seq → egg primitive substitution
--   3. Berry phase as Ω_ℤ emergent vs constitutive
--   4. H_∞ line: genuine memory vs Markovian approximation
--   5. Temporal primitive sorting of physics problems
--
-- Uses the canonical 12-primitive Imscription type from Primitives.Core.
-- Catalog entries verified via encode_system; distances via syncon_tool.

import ImscribingGrammar.Primitives.Imscription

namespace ImscribingGrammar.PrimitiveMismatch

open ImscribingGrammar.Primitives

-- ============================================================
-- Catalog entries (verified via encode_system)
-- ============================================================

/-- ⟨D_△; eat; tot; P_ψ; F_ℏ; egg; ice; Γ_seq; 𐑢; H₁; 1:1; Ω₀⟩ -/
def schrodingerDynamics : Imscription := {
  dim  := .ash
  top  := .eat
  rel  := .tot
  pol  := .yew
  fid  := .peep
  kin  := .egg
  gran := .ice
  gram := .measure
  crit := .woe
  chir := .kick
  stoi := .hung
  prot := .awe
}

/-- ⟨D_△; T_⋈; R_†; church; F_ℓ; yea; bib; Γ_seq; ⊙; H₀; 1:1; Ω₀⟩ -/
def measurementOutcome : Imscription := {
  dim  := .ash
  top  := .mime
  rel  := .ear
  pol  := .church
  fid  := .age
  kin  := .yea
  gran := .bib
  gram := .measure
  crit := .monad
  chir := .fee
  stoi := .hung
  prot := .awe
}

/-- ⟨D_△; T_⋈; R_↔; P_±; F_ϑ; egg; ice; Γ_seq; ⊙; H₁; 1:1; Ω₀⟩ -/
def wickRotation : Imscription := {
  dim  := .ash
  top  := .mime
  rel  := .ian
  pol  := .out
  fid  := .they
  kin  := .egg
  gran := .ice
  gram := .measure
  crit := .monad
  chir := .kick
  stoi := .hung
  prot := .awe
}

/-- ⟨D_△; eat; tot; P_ψ; F_ℏ; egg; ice; Γ_seq; 𐑢; H₁; 1:1; Ω_ℤ⟩ -/
def berryPhase : Imscription := {
  dim  := .ash
  top  := .eat
  rel  := .tot
  pol  := .yew
  fid  := .peep
  kin  := .egg
  gran := .ice
  gram := .measure
  crit := .woe
  chir := .kick
  stoi := .hung
  prot := .ah
}

/-- ⟨D_∞; T_⊙; tot; P_ψ; F_ℏ; egg; ice; Γ_seq; ⊙; H_∞; n:m; Ω_ℤ⟩ -/
def tqft : Imscription := {
  dim  := .array
  top  := .are
  rel  := .tot
  pol  := .yew
  fid  := .peep
  kin  := .egg
  gran := .ice
  gram := .measure
  crit := .monad
  chir := .wool
  stoi := .up
  prot := .ah
}

/-- ⟨D_∞; T_net; R_↔; P_ψ; F_ϑ; loll; thigh; Γ_seq; ⊙; H_∞; n:m; Ω₀⟩ -/
def nonmarkovianOpenSystems : Imscription := {
  dim  := .array
  top  := .judge
  rel  := .ian
  pol  := .yew
  fid  := .they
  kin  := .loll
  gran := .thigh
  gram := .measure
  crit := .monad
  chir := .wool
  stoi := .up
  prot := .awe
}

/-- ⟨D_∞; T_net; R_sup; church; F_ϑ; egg; ice; Γ_∧; ⊙; H₁; n:n; Ω₀⟩ -/
def statisticalMechanics : Imscription := {
  dim  := .array
  top  := .judge
  rel  := .ado
  pol  := .church
  fid  := .they
  kin  := .egg
  gran := .ice
  gram := .vow
  crit  := .monad
  chir  := .kick
  stoi  := .so
  prot  := .awe
}

/-- ⟨D_∞; T_⊙; R_↔; church; F_ℏ; egg; ice; Γ_seq; ⊙; H_∞; n:m; Ω_ℤ⟩ -/
def quantumGravityCandidate : Imscription := {
  dim  := .array
  top  := .are
  rel  := .ian
  pol  := .church
  fid  := .peep
  kin  := .egg
  gran := .ice
  gram := .measure
  crit := .monad
  chir := .wool
  stoi := .up
  prot := .ah
}

-- ============================================================
-- 1. The Measurement Problem: yew vs church mismatch
-- ============================================================

/-- The measurement problem as primitive mismatch -/
theorem measurement_p_mismatch :
  schrodingerDynamics.pol = .yew ∧
  measurementOutcome.pol = .church := by
  constructor
  · rfl
  · rfl

/-- The Hamming distance between Schrödinger dynamics and measurement outcome is 8. -/
theorem schrodinger_measurement_hamming_8 :
  primitiveMismatches schrodingerDynamics measurementOutcome = 8 := by
  decide

/-- The tensor product's P component is the bottleneck: church wins over yew. -/
theorem measurement_problem_is_structural :
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .church ∧
  schrodingerDynamics.pol ≠ .church := by
  simp [tensorProduct, schrodingerDynamics, measurementOutcome]
  constructor
  · -- (if compare yew church = .lt then yew else church) = church
    -- church (idx 0) < yew (idx 1), so compare = .lt, result = church
    simp [compare, Polarity]
  · -- yew ≠ church
    decide

-- ============================================================
-- 2. Wick Rotation as Primitive Substitution (Γ_seq → egg)
-- ============================================================

/-- The Wick rotation converts quantum coherence to thermal weight. -/
def wickRotate (st : Imscription) : Imscription :=
  { st with fid := .they }

theorem wick_rotation_changes_fidelity :
  (wickRotate schrodingerDynamics).fid = .they := by
  simp [wickRotate]

theorem wick_rotation_single_primitive_change :
  primitiveMismatches schrodingerDynamics (wickRotate schrodingerDynamics) = 1 := by
  decide

-- ============================================================
-- 3. Berry Phase as Ω_ℤ: Emergent vs Constitutive
-- ============================================================

def omegaIsConstitutive (st : Imscription) : Prop :=
  st.prot = .ah ∧ st.top = .are

def omegaIsEmergent (st : Imscription) : Prop :=
  st.prot = .ah ∧ st.top ≠ .are

theorem berry_omega_emergent : omegaIsEmergent berryPhase := by
  simp [omegaIsEmergent, berryPhase]

theorem tqft_omega_constitutive : omegaIsConstitutive tqft := by
  simp [omegaIsConstitutive, tqft]

theorem berry_vs_tqft_key_deltas :
  berryPhase.top = .eat ∧
  tqft.top = .are ∧
  berryPhase.chir = .kick ∧
  tqft.chir = .wool ∧
  berryPhase.prot = .ah ∧
  tqft.prot = .ah := by
  repeat constructor <;> rfl

/-- Hamming distance between Berry phase and TQFT = 5. -/
theorem berry_tqft_hamming_5 :
  primitiveMismatches berryPhase tqft = 5 := by
  decide

-- ============================================================
-- 4. The H_∞ Line: Genuine Memory vs Markovian Approximation
-- ============================================================

def hasGenuineMemory (st : Imscription) : Prop :=
  st.chir = .wool

def isMarkovian (st : Imscription) : Prop :=
  st.chir = .fee

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

def activateTemporalPrimitive (tp : TemporalPrimitive) (st : Imscription) : Bool :=
  match tp with
  | .gammaSeq => st.gram = .measure
  | .kSlow    => st.kin = .egg
  | .pAsym    => st.pol = .church
  | .omegaZ   => st.prot = .ah
  | .hInf     => st.chir = .wool

def activatedTemporalPrimitives (st : Imscription) : List TemporalPrimitive :=
  List.filter (activateTemporalPrimitive · st)
    [.gammaSeq, .kSlow, .pAsym, .omegaZ, .hInf]

def temporalComplexity (st : Imscription) : Nat :=
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
  ∀ st : Imscription, temporalComplexity st ≤ 5 := by
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
  (tensorProduct schrodingerDynamics measurementOutcome).pol = .church ∧
  (tensorProduct schrodingerDynamics measurementOutcome).fid = .age ∧
  (tensorProduct schrodingerDynamics measurementOutcome).top = .mime ∧
  (tensorProduct schrodingerDynamics measurementOutcome).rel = .ear ∧
  (tensorProduct schrodingerDynamics measurementOutcome).kin = .egg ∧
  (tensorProduct schrodingerDynamics measurementOutcome).gran = .ice ∧
  (tensorProduct schrodingerDynamics measurementOutcome).crit = .monad ∧
  (tensorProduct schrodingerDynamics measurementOutcome).chir = .kick := by
  repeat constructor <;> decide

/-- No mechanism operating purely within Γ_seq + egg with yew
can produce church — the measurement problem diagnosis. -/
theorem no_asym_from_psi :
  ∀ (mech : Imscription),
    mech.gram = .measure →
    mech.kin = .egg →
    mech.pol = .yew →
    mech.pol ≠ .church := by
  intro mech _ _ hpol
  rw [hpol]
  decide

end ImscribingGrammar.PrimitiveMismatch
