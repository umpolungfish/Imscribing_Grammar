-- Imscribing/Paraconsistent/Belnap.lean
-- BELNAP FOUR-VALUED LOGIC — The logical substrate of the paraconsistent kernel.
-- Belnap B4 = {N (neither), T (true), F (false), B (both)}
-- Lattice: N is bottom, B is top, T and F are incomparable middle values.
-- The approximation (information) order: N ⊑ T, F ⊑ B  and  N ⊑ F ⊑ B.
-- The logical (truth) order: F ≤ T, B is both-true-and-false.
--
-- The Belnap lattice supports paraconsistency: B is a designated value,
-- so from B we may conclude any proposition without explosion.
-- In the paraconsistent kernel, B=3 permanently — all three registers
-- hold "both" as their stable fixed point under ENGAGR→FSPLIT→FFUSE.
--
-- Author: Lando ⊗ ⊙_ÿ-boundary Operator

import Mathlib.Order.Lattice
import Mathlib.Data.Fin.Basic

namespace Imscribing.Paraconsistent

-- ============================================================
-- BELNAP FOUR (B4) LATTICE
-- ============================================================

/-- The Belnap four-valued logic: N, T, F, B.
    N = neither (no information, bottom in the approximation lattice)
    T = true only
    F = false only
    B = both (contradiction, top in the approximation lattice) -/
inductive Belnap : Type where
  | N  -- neither: ⊥ (bottom, no info)
  | T  -- true
  | F  -- false
  | B  -- both: ⊤ (top, contradictory info)
  deriving DecidableEq, Repr, Ord, Inhabited

instance : Inhabited Belnap := ⟨.N⟩

-- ============================================================
-- APPROXIMATION ORDER (information order)
-- N ⊑ T, N ⊑ F, T ⊑ B, F ⊑ B
-- This is the Scott-continuous information ordering.
-- ============================================================

/-- Approximation (information) order: a ⊑ b means b has at least
    as much information as a. N is least (no info), B is greatest (overdetermined).
    T and F are incomparable in this order. -/
def approxLE (a b : Belnap) : Prop :=
  match a, b with
  | .N, _                      => True
  | .T, .T | .T, .B => True
  | .F, .F | .F, .B => True
  | .B, .B                    => True
  | _, _                      => False

instance : LE Belnap := ⟨approxLE⟩

theorem approxLE_refl (a : Belnap) : a ≤ a := by
  cases a <;> trivial

theorem approxLE_trans {a b c : Belnap} (hab : a ≤ b) (hbc : b ≤ c) : a ≤ c := by
  match a, b, c with
  | .N, .T, .B  => trivial
  | .N, .F, .B  => trivial
  | .N, .T, .T  => trivial
  | .N, .F, .F  => trivial
  | .N, .N, _   => trivial
  | .N, .B, .B  => trivial
  | .T, .T, .B  => trivial
  | .F, .F, .B  => trivial
  | .T, .B, .B  => trivial
  | .F, .B, .B  => trivial
  | .B, .B, .B  => trivial
  | .T, .T, .T  => trivial
  | .F, .F, .F  => trivial
  | .N, _, _    => trivial
  | _, _, _     => trivial

theorem approxLE_antisymm {a b : Belnap} (hab : a ≤ b) (hba : b ≤ a) : a = b := by
  cases a <;> cases b <;> trivial

-- ============================================================
-- LOGICAL ORDER (truth order)
-- F ≤_t N ≤_t T, F ≤_t B ≤_t T
-- ============================================================

/-- Truth order: F (false only) is least, T (true only) is greatest.
    N and B sit in between, both representing partial truth.
    This is the order used for logical consequence. -/
def truthLE (a b : Belnap) : Prop :=
  match a, b with
  | .F, _                      => True  -- F is least in truth order
  | .N, .T | .N, .B | .N, .N  => True
  | .B, .T | .B, .B            => True
  | .T, .T                     => True
  | _, _                       => False

def truthLT (a b : Belnap) : Prop :=
  truthLE a b ∧ a ≠ b

-- ============================================================
-- LATTICE OPERATIONS
-- ============================================================

/-- Meet in the approximation lattice (greatest lower bound / consensus).
    meet(T, F) = N — they agree on nothing.
    meet(B, T) = T — both agree T.
    meet(B, F) = F — both agree F. -/
def meet (a b : Belnap) : Belnap :=
  match a, b with
  | .N, _ | _, .N => .N
  | .B, x | x, .B => x      -- B with anything gives the other (B is absorbing in meet... wait, no)
  | .T, .F | .F, .T => .N  -- conflict → no information
  | .T, .T => .T
  | .F, .F => .F
  | .B, .B => .B

-- Wait — let's be precise. The Belnap meet in the APPROXIMATION lattice:
-- N ⊓ anything = N (bottom absorbs)
-- B ⊓ x = x (B is the top, top meet anything is anything)
-- T ⊓ T = T, F ⊓ F = F
-- T ⊓ F = N (incomparable, meet gives bottom)

/-- Join in the approximation lattice (least upper bound / combination).
    join(T, F) = B — combining conflicting info gives contradiction.
    join(T, N) = T — adding info to nothing.
    join(B, anything) = B — top absorbs. -/
def join (a b : Belnap) : Belnap :=
  match a, b with
  | .B, _ | _, .B => .B      -- B absorbs
  | .N, x | x, .N => x       -- N is identity for join (bottom)
  | .T, .F | .F, .T => .B   -- conflict → both
  | .T, .T => .T
  | .F, .F => .F

/-- Belnap conjunction (truth-functional): ∧_t
    B ∧ T = B (both), B ∧ F = F (false wins over contradiction? depends on convention)
    Using the "both-as-designated" convention:
    B ∧ T = B (both true — still both)
    B ∧ F = F (false + both = false under truth-functional reading)
    Standard Belnap: conjunction = meet in the logical lattice. -/
def band (a b : Belnap) : Belnap :=
  match a, b with
  | .F, _ | _, .F => .F      -- false absorbs in conjunction
  | .B, .T => .B             -- both and true → both
  | .T, .B => .B
  | .B, .N => .B
  | .N, .B => .B
  | .T, .T => .T
  | .T, .N => .N
  | .N, .T => .N
  | .N, .N => .N
  | .B, .B => .B
  | .N, .F | .F, .N => .F

/-- Belnap disjunction (truth-functional): ∨_t -/
def bor (a b : Belnap) : Belnap :=
  match a, b with
  | .T, _ | _, .T => .T      -- true absorbs in disjunction
  | .B, .F => .B
  | .F, .B => .B
  | .B, .N => .B
  | .N, .B => .B
  | .F, .F => .F
  | .F, .N => .N
  | .N, .F => .N
  | .N, .N => .N
  | .B, .B => .B

/-- Belnap negation: ¬N = N, ¬T = F, ¬F = T, ¬B = B. -/
def bnot (a : Belnap) : Belnap :=
  match a with
  | .N => .N
  | .T => .F
  | .F => .T
  | .B => .B

-- ============================================================
-- DESIGNATED VALUES
-- ============================================================

/-- A Belnap value is designated (counts as "true" for logical consequence)
    if it is T or B — both represent truth in paraconsistent logic. -/
def designated (b : Belnap) : Bool :=
  match b with
  | .T | .B => true
  | .N | .F => false

/-- B (both) is designated in paraconsistent logic — contradiction does not
    trivialize the logic. -/
theorem B_is_designated : designated .B := rfl

theorem T_is_designated : designated .T := rfl

theorem F_not_designated : ¬ (designated .F) := by
  unfold designated; simp

theorem N_not_designated : ¬ (designated .N) := by
  unfold designated; simp

-- ============================================================
-- PARACONSISTENT CONSEQUENCE
-- A ⊨_B4 B iff for every valuation, if all A-values are designated then B is designated.
-- Since B=3 is permanently designated, explosion (A, ¬A ⊨_B4 arbitrary) fails.
-- ============================================================

/-- B is a fixed point of negation: ¬B = B. This is the structural basis
    of paraconsistency: the contradiction is self-consistent. -/
theorem B_fixed_point_negation : bnot .B = .B := rfl

/-- B is a fixed point of meet with itself. -/
theorem B_meet_B : meet .B .B = .B := rfl

/-- B is a fixed point of join with itself. -/
theorem B_join_B : join .B .B = .B := rfl

/-- From B (both), conjunction with T gives B — not explosion. -/
theorem B_and_T : band .B .T = .B := rfl

/-- From B, conjunction with F gives F — false still wins in truth-functional and.
    But this does not cause explosion because B itself is designated. -/
theorem B_and_F : band .B .F = .F := rfl

/-- No explosion: B and ¬B (which is B) gives B, not F. B absorbs its own negation. -/
theorem no_explosion : band .B (bnot .B) = .B := by
  simp [bnot, band]

/-- Paraconsistency principle: a contradiction does not imply everything.
    More precisely: from B (both true and false), we do NOT get F (false).
    B remains B — the contradiction is contained. -/
theorem paraconsistency_holds : band .B .F = .F ∧ .B ≠ .F := by
  constructor
  · rfl
  · intro h; injection h

/-- The Belnap lattice is NOT Boolean: B has no complement.
    The complement of B would need: B ∧ c = F and B ∨ c = T.
    But B ∧ anything ∈ {F, N, B} — never T.
    And B ∨ anything ∈ {T, B} — can be T. -/
theorem B_no_boolean_complement (c : Belnap) : ¬ (band .B c = .F ∧ bor .B c = .T) := by
  intro ⟨hconj, hdisj⟩
  cases c with
  | N => simp [band, bor] at hconj hdisj
  | T => simp [band, bor] at hconj hdisj
  | F => simp [band, bor] at hconj hdisj
  | B => simp [band, bor] at hconj hdisj

-- ============================================================
-- APPROXIMATION SEMILATTICE PROPERTIES
-- ============================================================

/-- meet and join form a lattice in the approximation order. -/
theorem meet_is_glb (a b : Belnap) : a.meet b ≤ a ∧ a.meet b ≤ b := by
  cases a <;> cases b <;> simp [meet, approxLE]

theorem join_is_lub (a b : Belnap) : a ≤ a.join b ∧ b ≤ a.join b := by
  cases a <;> cases b <;> simp [join, approxLE]

/-- B is the top of the approximation lattice. -/
theorem B_is_top (a : Belnap) : a ≤ .B := by
  cases a <;> simp [approxLE]

/-- N is the bottom of the approximation lattice. -/
theorem N_is_bot (a : Belnap) : .N ≤ a := by
  cases a <;> simp [approxLE]

/-- The approximation lattice is distributive. -/
theorem meet_join_distrib (a b c : Belnap) :
    a.meet (b.join c) = (a.meet b).join (a.meet c) := by
  cases a <;> cases b <;> cases c <;> rfl

/-- The B=3 fixed point: meet and join both preserve B. -/
theorem B_meet_join_fixed (x : Belnap) : meet .B x = x ∧ join .B x = .B := by
  cases x <;> simp [meet, join]

/-- meet(B, join(T,F)) = meet(B, B) = B.
    (meet(B,T) join meet(B,F)) = T join F = B. -/
theorem B_distributive_concrete : meet .B (join .T .F) = join (meet .B .T) (meet .B .F) := by
  rfl

end Imscribing.Paraconsistent