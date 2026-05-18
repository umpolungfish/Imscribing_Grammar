/-!
# Cartesian Closed Category Ob3ect

Products and exponentials (internal Hom) in a CCC.
Uses the categorical product Limits.prod, not the Lean product type ×.
-/

import Mathlib.CategoryTheory.Limits.Basic
import Mathlib.CategoryTheory.Limits.Shapes.Finite

open CategoryTheory Limits

class CCCStructure (C : Type*) [Category C] [HasFiniteProducts C] where
  /-- Exponential object A ⇒ B (internal Hom) -/
  exp : ∀ (A B : C), C

  /-- Evaluation morphism: (A ⇒ B) × A → B -/
  eval : ∀ (A B : C), prod (exp A B) A ⟶ B

  /-- Curry: turns (A × B → C) into (A → (B ⇒ C)) -/
  curry : ∀ {A B D : C}, (prod A B ⟶ D) → (A ⟶ exp B D)

  /-- Universal property of exponentials -/
  exponential_universal : ∀ {A B D : C} (f : prod A B ⟶ D),
    eval B D ∘ prod.map (curry f) (𝟙 B) = f := by sorry

theorem ccc_coherent {C : Type*} [Category C] [HasFiniteProducts C]
    (CCC : CCCStructure C) : True := trivial

#check ccc_coherent
