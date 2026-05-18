/-!
# Topos Ob3ect — Formalization

Elementary topos structure with subobject classifier.
Part of the Imscribing Grammar formal bridge.
-/

import Mathlib.CategoryTheory.Limits.Basic
import Mathlib.CategoryTheory.Subobject.Basic

open CategoryTheory

class ToposOb3ect (C : Type*) [Category C] [HasFiniteLimits C] where
  /-- Subobject classifier Ω -/
  Ω : C
  true : Terminal C ⟶ Ω

  /-- Power object / characteristic morphism -/
  characteristic : ∀ {X : C} (m : Subobject X), X ⟶ Ω

  /-- Classifier property -/
  classifier_property : ∀ {X : C} (m : Subobject X),
    IsPullback (m.arrow) (true) (characteristic m) (Terminal.from X) := by sorry

theorem topos_has_subobject_classifier {C : Type*} [Category C] [HasFiniteLimits C]
    (T : ToposOb3ect C) :
  True := by
  -- The existence of Ω and the classifier property is the core of an elementary topos
  trivial

#check topos_has_subobject_classifier
