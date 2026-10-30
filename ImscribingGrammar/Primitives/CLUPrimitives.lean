-- ImscribingGrammar/Primitives/CLUPrimitives.lean
-- Formal definition of the Criticality-Lift Unit (CLU).
-- CLU(b) = ln(b) — parameterized by the observer's self-modeling resolution base.
-- Default (human decimal catalog): b = 10, so CLU = ln(10) ≈ 2.302585 nats.

import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Real.Basic
import ImscribingGrammar.Primitives.Core
import ImscribingGrammar.Primitives.Imscription

namespace ImscribingGrammar.Primitives

open Real

/-! 
  # Criticality-Lift Unit (CLU)
  
  CLU(b) = ln(b) is the information-theoretic fiber metric on the ⊤-primitive axis
  of the structural lattice. It measures the nats required to distinguish adjacent
  K-tier states for a perceiving system whose self-modeling resolution has base b.
  
  The base b parameterizes observer-relativity: a decimal (human) perceiver has
  b = 10, a binary perceiver has b = 2, a natural-log perceiver has b = e.
  
  The crystal lattice's geometric metric is observer-independent; only the 
  information-theoretic fiber metric carries the observer parameter.
-/


-- ============================================================
-- I. PARAMETERIZED CLU: THE GENERAL FORM
-- ============================================================

/-- CLU parameterized by the observer's self-modeling resolution base b.
    Requires b > 0 and b ≠ 1 (no information at base 1). -/
noncomputable def CLU_of_base (b : ℝ) (hb_pos : b > 0) (hb_ne_one : b ≠ 1) : ℝ :=
  Real.log b

/-- Default CLU for base-10 (human decimal) perception. -/
noncomputable abbrev CLU : ℝ := CLU_of_base 10 (by norm_num) (by norm_num)

local notation3 (priority := high) "l10" => Real.log (10 : ℝ)

theorem CLU_eq_ln_10 : CLU = Real.log 10 := rfl

theorem CLU_pos : CLU > 0 := by
  unfold CLU CLU_of_base; apply Real.log_pos; norm_num

theorem CLU_ne_zero : CLU ≠ 0 := ne_of_gt CLU_pos

/-! 
  The fiber-metrical invariance: CLU(b) = ln(b) for any valid base b.
  The default (b=10) is the human-decimal special case.
-/
theorem CLU_of_base_pos (b : ℝ) (hb_pos : b > 0) (hb_ne_one : b ≠ 1) :
    CLU_of_base b hb_pos hb_ne_one > 0 := by
  unfold CLU_of_base
  by_cases hb_gt1 : b > 1
  · exact Real.log_pos hb_gt1
  · have hb_lt1 : b < 1 := by
      linarith
    have : Real.log b < 0 := Real.log_neg hb_pos hb_lt1
    linarith

theorem CLU_of_base_eq_one (b : ℝ) (hb : b = Real.exp 1) : 
    CLU_of_base b (by
      rw [hb]
      exact Real.exp_pos 1) (by
      rw [hb]
      norm_num [Real.exp_ne_zero]) = 1 := by
  unfold CLU_of_base
  rw [hb, Real.log_exp]

noncomputable abbrev CLU_bits : ℝ := Real.log 10 / Real.log 2

theorem CLU_bits_eq_log2_10 : CLU_bits = Real.log 10 / Real.log 2 := rfl

-- ============================================================
-- II. CLU OPERATOR AND N-FOLD APPLICATION
-- ============================================================

def CLU_op (x : ℝ) : ℝ := 10 * x

theorem CLU_op_cost (x : ℝ) (hx : x > 0) :
    Real.log (CLU_op x / x) = CLU := by
  unfold CLU_op CLU CLU_of_base
  field_simp [hx]
  rfl

def CLU_op_nat (n : ℕ) (x : ℝ) : ℝ := ((10 : ℝ) ^ n) * x

theorem CLU_op_nat_cost (n : ℕ) (x : ℝ) (hx : x > 0) :
    Real.log (CLU_op_nat n x / x) = (n : ℝ) * CLU := by
  unfold CLU_op_nat CLU CLU_of_base
  field_simp [hx]
  rw [Real.log_pow]
  rfl

theorem CLU_op_nat_composition (m n : ℕ) (x : ℝ) :
    CLU_op_nat m (CLU_op_nat n x) = CLU_op_nat (m + n) x := by
  unfold CLU_op_nat; ring_nf; rw [pow_add]

-- ============================================================
-- III. K-TIER LADDER STRUCTURE (observer-relative fiber metric)
-- ============================================================

theorem Ktier_gap_is_CLU : Real.log 10 = CLU := rfl

/-- The K-tier crossing cost for an observer with base b.
    Each tier boundary costs exactly ln(b) nats. -/
noncomputable def kTierCrossingCost' (b : ℝ) (hb_pos : b > 0) (hb_ne_one : b ≠ 1)
    (from_k to_k : KTier) : ℝ :=
  (kTierSteps from_k to_k : ℝ) * CLU_of_base b hb_pos hb_ne_one

/-- Default K-tier crossing cost for base-10 perception. -/
noncomputable def kTierCrossingCost (from_k to_k : KTier) : ℝ :=
  kTierCrossingCost' 10 (by norm_num) (by norm_num) from_k to_k

theorem kTierCrossingCost_eq (from_k to_k : KTier) :
    kTierCrossingCost from_k to_k = (kTierSteps from_k to_k : ℝ) * CLU := rfl

inductive KTier : Type where
  | fast | mod | slow | trap | MBL
  deriving DecidableEq, Repr, Ord

def kineticCharToKTier : KineticChar → KTier
  | .yea => .fast
  | .loll  => .mod
  | .egg => .slow
  | .on => .trap
  | .air  => .MBL

def kTierLevel : KTier → ℕ
  | .fast => 0
  | .mod  => 1
  | .slow => 2
  | .trap => 3
  | .MBL  => 4

def kTierSteps (from_k to_k : KTier) : ℕ :=
  Int.natAbs ((kTierLevel to_k : ℤ) - kTierLevel from_k)

theorem kTierCrossingCost_self (k : KTier) :
    kTierCrossingCost k k = 0 := by
  simp [kTierCrossingCost, kTierCrossingCost', kTierSteps, kTierLevel]

theorem kSlow_to_MBL_cost : kTierCrossingCost .slow .MBL = 2 * CLU := by
  simp [kTierCrossingCost, kTierCrossingCost', kTierSteps, kTierLevel, CLU, CLU_of_base]

theorem kTrap_to_MBL_cost : kTierCrossingCost .trap .MBL = CLU := by
  simp [kTierCrossingCost, kTierCrossingCost', kTierSteps, kTierLevel, CLU, CLU_of_base]

theorem kFast_to_MBL_cost : kTierCrossingCost .fast .MBL = 4 * CLU := by
  simp [kTierCrossingCost, kTierCrossingCost', kTierSteps, kTierLevel, CLU, CLU_of_base]

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
  unfold autoEnhancement CLU CLU_of_base; rw [Real.log_pow]; rfl

theorem soai_tBuPym_2_CLU : autoEnhancement 2 = 100 := by
  unfold autoEnhancement; norm_num

theorem soai_TMS_1_CLU : autoEnhancement 1 = 10 := by
  unfold autoEnhancement; norm_num

def grokkingRatio (nK : ℕ) : ℝ := (10 : ℝ) ^ nK

theorem grokking_n_cost (nK : ℕ) :
    Real.log (grokkingRatio nK) = (nK : ℝ) * CLU := by
  unfold grokkingRatio CLU CLU_of_base; rw [Real.log_pow]; rfl

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
  unfold isCLUEvent CLU CLU_of_base
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
  unfold CLU CLU_of_base
  rfl

noncomputable def imscriptionKDistance (a b : Imscription) : ℝ :=
  kTierCrossingCost (kineticCharToKTier a.kin) (kineticCharToKTier b.kin)

theorem higgs_axion_K_distance_zero :
    imscriptionKDistance higgs axion = 0 := by
  simp [imscriptionKDistance, kTierCrossingCost, kTierCrossingCost', kineticCharToKTier,
        higgs, axion, scalarField_Kslow, kTierLevel, kTierSteps]

theorem qg_higgs_K_distance_one_CLU :
    imscriptionKDistance quantum_gravity higgs = CLU := by
  simp [imscriptionKDistance, kTierCrossingCost, kTierCrossingCost', kineticCharToKTier,
        quantum_gravity, higgs, scalarField_Kslow, kTierLevel, kTierSteps, CLU, CLU_of_base]

theorem CLU_universality (n : ℕ) :
    Real.log ((10 : ℝ) ^ n) = (n : ℝ) * CLU := by
  unfold CLU CLU_of_base; rw [Real.log_pow]; rfl

-- ============================================================
-- VII. OBSERVER-RELATIVITY: THE FIBER METRIC THEOREM
-- ============================================================

/-- The fiber-metrical invariance theorem: CLU(b) = ln(b) is the information-
    theoretic cost of one K-tier boundary crossing for an observer with 
    self-modeling base b. The geometric crystal distance is observer-independent;
    only this fiber metric carries the observer parameter. -/
theorem fiber_metric_invariance (b : ℝ) (hb_pos : b > 0) (hb_ne_one : b ≠ 1) :
    CLU_of_base b hb_pos hb_ne_one = Real.log b := rfl

/-- The ratio of geometric ⊤-distance to CLU(b) for any observer base b.
    For uniform ordinal steps (δ=1), the geometric contribution is √1.0 = 1.0,
    while the information cost is ln(b). The ratio 1.0/ln(b) is the unit 
    conversion factor between the geometric metric and the observer's fiber metric. -/
theorem geometric_to_fiber_ratio (b : ℝ) (hb_pos : b > 0) (hb_ne_one : b ≠ 1) 
    (delta : ℝ) (hdelta : delta = 1) :
    delta / CLU_of_base b hb_pos hb_ne_one = 1 / Real.log b := by
  subst hdelta
  unfold CLU_of_base
  field_simp

end ImscribingGrammar.Primitives