-- ImscribingGrammar/Primitives/CLUPrimitives.lean
-- Formal definition of the Criticality-Lift Unit (CLU).
-- CLU = ln(10) = 2.302585... nats.

import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Real.Basic
import ImscribingGrammar.Primitives.Core
import ImscribingGrammar.Primitives.Synthon

namespace ImscribingGrammar.Primitives

open Real

local notation3 (priority := high) "l10" => Real.log (10 : ℝ)

/- One Criticality-Lift Unit: the natural logarithm of 10. -/
noncomputable abbrev CLU : ℝ := l10

theorem CLU_pos : CLU > 0 := by
  unfold CLU l10; apply Real.log_pos; norm_num

theorem CLU_ne_zero : CLU ≠ 0 := ne_of_gt CLU_pos

theorem CLU_eq_one_decade : CLU = Real.log 10 := rfl

noncomputable abbrev CLU_bits : ℝ := Real.log 10 / Real.log 2

-- ============================================================
-- II. CLU OPERATOR AND N-FOLD APPLICATION
-- ============================================================

def CLU_op (x : ℝ) : ℝ := 10 * x

theorem CLU_op_cost (x : ℝ) (hx : x > 0) :
    Real.log (CLU_op x / x) = CLU := by
  unfold CLU_op CLU
  field_simp [hx]
  rfl

def CLU_op_nat (n : ℕ) (x : ℝ) : ℝ := ((10 : ℝ) ^ n) * x

theorem CLU_op_nat_cost (n : ℕ) (x : ℝ) (hx : x > 0) :
    Real.log (CLU_op_nat n x / x) = (n : ℝ) * CLU := by
  unfold CLU_op_nat CLU
  field_simp [hx]
  rw [Real.log_pow]
  rfl

theorem CLU_op_nat_composition (m n : ℕ) (x : ℝ) :
    CLU_op_nat m (CLU_op_nat n x) = CLU_op_nat (m + n) x := by
  unfold CLU_op_nat; ring_nf; rw [pow_add]

-- ============================================================
-- III. K-TIER LADDER STRUCTURE
-- ============================================================

theorem Ktier_gap_is_CLU : Real.log 10 = CLU := rfl

inductive KTier : Type where
  | fast | mod | slow | trap | MBL
  deriving DecidableEq, Repr, Ord

def kineticCharToKTier : KineticChar → KTier
  | .K_fast => .fast
  | .K_mod  => .mod
  | .K_slow => .slow
  | .K_trap => .trap
  | .K_MBL  => .MBL

def kTierLevel : KTier → ℕ
  | .fast => 0
  | .mod  => 1
  | .slow => 2
  | .trap => 3
  | .MBL  => 4

def kTierSteps (from_k to_k : KTier) : ℕ :=
  Int.natAbs ((kTierLevel to_k : ℤ) - kTierLevel from_k)

noncomputable def kTierCrossingCost (from_k to_k : KTier) : ℝ :=
  (kTierSteps from_k to_k : ℝ) * CLU

theorem kTierCrossingCost_self (k : KTier) :
    kTierCrossingCost k k = 0 := by
  simp [kTierCrossingCost, kTierSteps, kTierLevel]

theorem kSlow_to_MBL_cost : kTierCrossingCost .slow .MBL = 2 * CLU := by
  simp [kTierCrossingCost, kTierSteps, kTierLevel]

theorem kTrap_to_MBL_cost : kTierCrossingCost .trap .MBL = CLU := by
  simp [kTierCrossingCost, kTierSteps, kTierLevel]

theorem kFast_to_MBL_cost : kTierCrossingCost .fast .MBL = 4 * CLU := by
  simp [kTierCrossingCost, kTierSteps, kTierLevel]

-- ============================================================
-- IV. CROSS-DOMAIN IDENTITIES
-- ============================================================

noncomputable def pKaCost (n : ℝ) (R : ℝ) (T : ℝ) : ℝ := n * 2.303 * R * T

theorem pKa_one_unit_is_CLU_energy (R T : ℝ) :
    pKaCost 1 R T = 2.303 * R * T := by
  unfold pKaCost; ring

theorem aqueous_range_is_14_CLU (R T : ℝ) :
    pKaCost 14 R T = 14 * (2.303 * R * T) := by
  unfold pKaCost; ring

noncomputable def arrheniusCLU (Ea : ℝ) (RT : ℝ) : ℝ := Ea / (RT * CLU)

theorem arrhenius_integer_CLU (Ea RT : ℝ) (hRT : RT > 0)
    (h : Ea = 3 * RT * CLU) : arrheniusCLU Ea RT = 3 := by
  unfold arrheniusCLU; rw [h]; field_simp [hRT, CLU_ne_zero]; ring

def autoEnhancement (nT : ℕ) : ℝ := (10 : ℝ) ^ nT

theorem autoEnhancement_one_CLU_per_loop (nT : ℕ) :
    Real.log (autoEnhancement nT) = (nT : ℝ) * CLU := by
  unfold autoEnhancement CLU; rw [Real.log_pow]; rfl

theorem soai_tBuPym_2_CLU : autoEnhancement 2 = 100 := by
  unfold autoEnhancement; norm_num

theorem soai_TMS_1_CLU : autoEnhancement 1 = 10 := by
  unfold autoEnhancement; norm_num

def grokkingRatio (nK : ℕ) : ℝ := (10 : ℝ) ^ nK

theorem grokking_n_cost (nK : ℕ) :
    Real.log (grokkingRatio nK) = (nK : ℝ) * CLU := by
  unfold grokkingRatio CLU; rw [Real.log_pow]; rfl

theorem grokking_modular_arith : grokkingRatio 2 = 100 := by
  unfold grokkingRatio; norm_num

theorem grokking_natural_language : grokkingRatio 3 = 1000 := by
  unfold grokkingRatio; norm_num

noncomputable def logNormalDecadeWidth (sigma : ℝ) : ℝ := sigma / CLU

theorem logNormal_width_decades (w : ℝ) :
    logNormalDecadeWidth (w * CLU) = w := by
  unfold logNormalDecadeWidth; field_simp [CLU_ne_zero]

-- ============================================================
-- V. CLU OPERATOR ALGEBRA
-- ============================================================

def isCLUInteger (c : ℝ) : Prop := ∃ n : ℕ, c = (n : ℝ) * CLU

theorem CLU_is_CLU_Integer : isCLUInteger CLU := ⟨1, by simp [CLU]⟩

theorem zero_is_CLU_Integer : isCLUInteger 0 := ⟨0, by simp [CLU]⟩

theorem CLU_int_closed_add {a b : ℝ}
    (ha : isCLUInteger a) (hb : isCLUInteger b) :
    isCLUInteger (a + b) := by
  obtain ⟨n, hn⟩ := ha
  obtain ⟨m, hm⟩ := hb
  use n + m
  rw [hn, hm]
  rfl

theorem CLU_int_closed_mul_nat {a : ℝ} (n : ℕ)
    (ha : isCLUInteger a) : isCLUInteger ((n : ℝ) * a) := by
  obtain ⟨k, hk⟩ := ha
  use n * k
  rw [hk]
  rfl

-- ============================================================
-- VI. RECOGNITION HEURISTIC AND SCALE-INDEPENDENCE
-- ============================================================

def isCLUEvent (n : ℕ) (r : ℝ) : Prop := Real.log r = (n : ℝ) * CLU

theorem CLU_event_iff_ratio (n : ℕ) (r : ℝ) (hr : r > 0) :
    isCLUEvent n r ↔ r = (10 : ℝ) ^ n := by
  unfold isCLUEvent CLU
  constructor
  · intro h
    apply_fun Real.exp at h
    simp [Real.exp_log hr] at h
    simp [Real.exp_mul, Real.exp_log (by norm_num)] at h
    exact h
  · intro h
    rw [h]
    rw [Real.log_pow]
    rfl

theorem CLU_scale_independence (x c : ℝ) (hx : x > 0) (hc : c > 0) :
    Real.log ((10 * c * x) / (c * x)) = CLU := by
  field_simp [hx, hc]
  unfold CLU
  rfl

noncomputable def synthonKDistance (a b : Synthon) : ℝ :=
  kTierCrossingCost (kineticCharToKTier a.kin) (kineticCharToKTier b.kin)

theorem higgs_axion_K_distance_zero :
    synthonKDistance higgs axion = 0 := by
  simp [synthonKDistance, kTierCrossingCost, kineticCharToKTier,
        higgs, axion, scalarField_Kslow, kTierLevel, kTierSteps]

theorem qg_higgs_K_distance_one_CLU :
    synthonKDistance quantum_gravity higgs = CLU := by
  simp [synthonKDistance, kTierCrossingCost, kineticCharToKTier,
        quantum_gravity, higgs, scalarField_Kslow, kTierLevel, kTierSteps, CLU]

theorem CLU_universality (n : ℕ) :
    Real.log ((10 : ℝ) ^ n) = (n : ℝ) * CLU := by
  unfold CLU; rw [Real.log_pow]; rfl

end ImscribingGrammar.Primitives
