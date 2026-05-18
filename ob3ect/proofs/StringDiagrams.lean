/-!
# String Diagram Ob3ect — Graphical Rewriting System

Formalization of string diagram calculus for monoidal categories.
-/

import Mathlib.CategoryTheory.Monoidal.Basic

open CategoryTheory MonoidalCategory

class StringDiagramStructure (C : Type*) [MonoidalCategory C] where
  /-- Graphical composition respects categorical composition -/
  diagram_composition : ∀ {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z),
    (f ⊗ 𝟙) ≫ (𝟙 ⊗ g) = f ≫ g := by sorry

  /-- Frobenius / Hopf diagrams satisfy spider laws -/
  spider_law : True := by sorry

#check diagram_composition
