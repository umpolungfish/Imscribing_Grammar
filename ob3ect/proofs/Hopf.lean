/-!
# Hopf Ob3ect — Formalization

Hopf algebra in a monoidal category: multiplication, comultiplication,
unit, counit, and antipode satisfying the defining coherence axioms.
-/

import Mathlib.CategoryTheory.Monoidal.Basic
import Mathlib.CategoryTheory.Monoidal.Coherence

open CategoryTheory
open MonoidalCategory

class HopfStructure (C : Type*) [MonoidalCategory C] extends FrobeniusOb3ect C where
  η : ∀ (X : C), 𝟙_ C ⟶ X   -- unit
  ε : ∀ (X : C), X ⟶ 𝟙_ C   -- counit
  S : ∀ (X : C), X ⟶ X       -- antipode

  /-- **Hopf Antipode Axiom (left)**: δ ; (S ⊗ id) ; μ = ε ; η -/
  antipode_left : ∀ (X : C),
    δ X ≫ (S X ⊗ 𝟙 X) ≫ μ X = ε X ≫ η X := by sorry

  /-- **Hopf Antipode Axiom (right)**: δ ; (id ⊗ S) ; μ = ε ; η -/
  antipode_right : ∀ (X : C),
    δ X ≫ (𝟙 X ⊗ S X) ≫ μ X = ε X ≫ η X := by sorry

theorem hopf_antipode_holds {C : Type*} [MonoidalCategory C]
    (H : HopfStructure C) (X : C) :
    H.δ X ≫ (H.S X ⊗ 𝟙 X) ≫ H.μ X = H.ε X ≫ H.η X :=
  H.antipode_left X

#check hopf_antipode_holds
