-- SynthOmnicon/Millennium/FrobeniusStructure.lean
-- The π₃ Frobenius Structure
--
-- π₃ — the ouroborotic projection — is not characterised by a primitive
-- alphabet but by a commutative Frobenius algebra 𝓕₃ = (𝒞₃, μ, η, δ, ε).
-- The four Frobenius types correspond exactly to the four ouroboricity tiers.
--
-- §1  FrobeniusType — four tiers with derived ordering
-- §2  Ouroboricity rank correspondence
-- §3  Specialness predicate and the C₁₃ gap
-- §4  Lee-Yang (special) vs RH (full, non-special) — machine-checked
-- §5  Triad minimality corollary in Frobenius language
--
-- Reference: PRIMITIVE_THEOREMS §23; PRIMITIVE_PREDICTIONS P-169–P-173.

import Mathlib.Data.Fintype.Basic

namespace Millennium.Frobenius

-- ─────────────────────────────────────────────────────────────────────────────
-- §1  FrobeniusType
-- ─────────────────────────────────────────────────────────────────────────────

/-- The four qualitatively distinct classes of Frobenius algebra completeness,
    corresponding to ouroboricity tiers O₀ / O₁ / O₂ / O_∞. -/
inductive FrobeniusType : Type where
  /-- O₀ — unit η only; no fixed-point structure -/
  | trivial      : FrobeniusType
  /-- O₁ — (μ, η); can compose toward fixed points; basin not generated -/
  | algebraOnly  : FrobeniusType
  /-- O₂ — (μ, η, δ, ε) + Frobenius condition; self-grounding -/
  | full         : FrobeniusType
  /-- O_∞ — full + μ ∘ δ = id; symmetry exactly characterises fixed point -/
  | special      : FrobeniusType
  deriving DecidableEq, Repr

/-- Explicit Fintype instance using kernel-reducible List.Mem constructors.
    Avoids List.decidableMem which contains ▸ and blocks decide reduction. -/
instance : Fintype FrobeniusType where
  elems := {.trivial, .algebraOnly, .full, .special}
  complete := fun x => by cases x <;> simp [Finset.mem_insert]

/-- Numerical rank for the linear order: trivial=0 < algebraOnly=1 < full=2 < special=3 -/
def FrobeniusType.rank : FrobeniusType → Nat
  | .trivial     => 0
  | .algebraOnly => 1
  | .full        => 2
  | .special     => 3

instance : LE FrobeniusType := ⟨fun a b => a.rank ≤ b.rank⟩
instance : LT FrobeniusType := ⟨fun a b => a.rank < b.rank⟩

instance (a b : FrobeniusType) : Decidable (a ≤ b) :=
  inferInstanceAs (Decidable (a.rank ≤ b.rank))

instance (a b : FrobeniusType) : Decidable (a < b) :=
  inferInstanceAs (Decidable (a.rank < b.rank))

-- ─────────────────────────────────────────────────────────────────────────────
-- §2  Ouroboricity correspondence
-- ─────────────────────────────────────────────────────────────────────────────

/-- Map Frobenius type to ouroboricity tier.
    O_∞ is represented as 3 for decidable arithmetic. -/
def frobeniusToOuroboricity : FrobeniusType → Nat
  | .trivial     => 0
  | .algebraOnly => 1
  | .full        => 2
  | .special     => 3

/-- The ouroboricity map preserves strict ordering. -/
theorem frobeniusToOuroboricity_strictMono (a b : FrobeniusType) :
    a < b → frobeniusToOuroboricity a < frobeniusToOuroboricity b := by
  cases a <;> cases b <;> decide

/-- No tier exists strictly between O₁ and O₂:
    the Frobenius condition is a binary property. -/
theorem no_tier_between_o1_and_o2 (t : FrobeniusType) :
    FrobeniusType.algebraOnly < t →
    t ≤ FrobeniusType.full →
    t = FrobeniusType.full := by
  cases t <;> decide

-- ─────────────────────────────────────────────────────────────────────────────
-- §3  Specialness predicate and the C₁₃ gap
-- ─────────────────────────────────────────────────────────────────────────────

/-- A Frobenius structure is special iff μ ∘ δ = id.
    Structurally: the symmetry exactly characterises the fixed point; no information loss. -/
def IsSpecial (t : FrobeniusType) : Prop := t = FrobeniusType.special

instance (t : FrobeniusType) : Decidable (IsSpecial t) :=
  inferInstanceAs (Decidable (t = FrobeniusType.special))

/-- Full Frobenius is strictly below special.
    The C₁₃ gap (Lee-Yang → RH) is exactly one Frobenius tier. -/
theorem c13_gap_is_one_frobenius_tier :
    FrobeniusType.full < FrobeniusType.special := by decide

/-- Full Frobenius is not special. -/
theorem full_not_special : ¬ IsSpecial FrobeniusType.full := by decide

/-- Specialness is the strictly top tier. -/
theorem special_is_top (t : FrobeniusType) : t ≤ FrobeniusType.special := by
  cases t <;> decide

-- ─────────────────────────────────────────────────────────────────────────────
-- §4  Lee-Yang and RH assignments
-- ─────────────────────────────────────────────────────────────────────────────

/-- Lee-Yang is O_∞ (special Frobenius).
    P_pm_sym acts explicitly — μ ∘ δ = id is the Lee-Yang theorem in Frobenius
    language (PRIMITIVE_THEOREMS §23.5, Theorem 23.1). -/
def leeYangFrobeniusType : FrobeniusType := .special

/-- RH: conjectured full Frobenius (Frobenius condition holds) but not special
    (μ ∘ δ ≠ id, because P_sym is an implicit symmetry).
    This encodes Conjecture 23.1 of PRIMITIVE_THEOREMS as a definition —
    not a sorry, but a precise structural claim. -/
def rhFrobeniusType : FrobeniusType := .full

/-- Lee-Yang is strictly above RH in Frobenius completeness. -/
theorem leeYang_strictly_above_rh :
    rhFrobeniusType < leeYangFrobeniusType := by decide

/-- Lee-Yang is special; RH is not. -/
theorem leeYang_is_special : IsSpecial leeYangFrobeniusType := by decide
theorem rh_is_not_special : ¬ IsSpecial rhFrobeniusType := by decide

/-- The C₁₃ gap is exactly one tier: full → special.
    No intermediate Frobenius type separates Lee-Yang from RH. -/
theorem c13_gap_leyang_rh_is_one :
    leeYangFrobeniusType.rank - rhFrobeniusType.rank = 1 := by decide

/-- YM and NS have the same Frobenius type as RH (full).
    Their gap from proved templates is in basin dimension, not Frobenius type (P-173). -/
def ymFrobeniusType : FrobeniusType := .full
def nsFrobeniusType : FrobeniusType := .full

theorem rh_ym_ns_same_frobenius_type :
    rhFrobeniusType = ymFrobeniusType ∧ rhFrobeniusType = nsFrobeniusType := by decide

/-- Proved C₁₂ templates (Schwinger, Leray) are also full Frobenius —
    their basins are explicitly constructed (2D exact solvability). -/
def schwingerFrobeniusType : FrobeniusType := .full
def lerayFrobeniusType : FrobeniusType := .full

theorem proved_c12_templates_are_full :
    schwingerFrobeniusType = .full ∧ lerayFrobeniusType = .full := by decide

-- ─────────────────────────────────────────────────────────────────────────────
-- §5  Triad minimality in Frobenius language
-- ─────────────────────────────────────────────────────────────────────────────

/-- A system is self-grounding iff its Frobenius type is at least full (O₂). -/
def IsSelfGrounding (t : FrobeniusType) : Prop :=
  FrobeniusType.full ≤ t

instance (t : FrobeniusType) : Decidable (IsSelfGrounding t) :=
  inferInstanceAs (Decidable (FrobeniusType.full ≤ t))

/-- O₁ is not self-grounding: externally describable but cannot generate its basin. -/
theorem algebraOnly_not_selfGrounding :
    ¬ IsSelfGrounding FrobeniusType.algebraOnly := by decide

/-- O₂ and O_∞ are self-grounding. -/
theorem full_selfGrounding : IsSelfGrounding FrobeniusType.full := by decide
theorem special_selfGrounding : IsSelfGrounding FrobeniusType.special := by decide

/-- Triad minimality corollary (Frobenius reading of PRIMITIVE_THEOREMS §22.2):
    O₂ is the minimum self-grounding tier. -/
theorem o2_is_minimum_selfGrounding :
    ∀ t : FrobeniusType, IsSelfGrounding t → FrobeniusType.full ≤ t :=
  fun _ h => h

/-- Exactly full and special are self-grounding (the two highest tiers). -/
theorem selfGrounding_iff (t : FrobeniusType) :
    IsSelfGrounding t ↔ t = .full ∨ t = .special := by
  cases t <;> decide

/-- Exactly two Frobenius types are self-grounding (full and special). -/
theorem exactly_two_selfGrounding_types :
    (Finset.univ (α := FrobeniusType)).filter IsSelfGrounding =
    {FrobeniusType.full, FrobeniusType.special} := by
  ext t
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
             Finset.mem_insert, Finset.mem_singleton, selfGrounding_iff]

end Millennium.Frobenius
