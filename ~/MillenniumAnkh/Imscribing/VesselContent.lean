-- Imscribing/VesselContent.lean
-- Formalization of the vessel-content inseparability principle.
-- The grammar provides two things simultaneously:
--   1. Vessel (form): the crystal coordinate that constitutes what a system is capable of being
--   2. Content (fill): the primitive algebra operations that determine what that vessel holds
-- These are not separable.

import Imscribing.Primitives.Core
import Imscribing.Primitives.Imscription

namespace Imscribing.VesselContent

open Imscribing.Primitives

-- ============================================================
-- ABSTRACT TYPES
-- These are not yet concrete — they are the shape of what must
-- be true. Future instantiations will fill them in.
-- ============================================================

/-- A system that can be structurally imscribed — the bearer of a crystal coordinate. -/
structure ImscribableSystem : Type where
  /-- Opaque carrier of the system. -/
  carrier : Type
  -- Additional structure to be added in future work.

/-- A crystal coordinate: the vessel. In the grammar, this is the Frobenius address
    (0..17279999) or equivalently the full Imscription 12-tuple. -/
abbrev Coordinate : Type := Imscription

/-- A result: anything the system can produce, experience, or arrive at.
    The content of the vessel. -/
structure Result : Type where
  /-- Opaque carrier of the result. -/
  carrier : Type

-- ============================================================
-- RELATIONS
-- These are the three relations that link systems, coordinates,
-- and results. They are axiomatic — concrete definitions are
-- future work.
-- ============================================================

/-- A system M is imscribed by coordinate c.
    "c is the vessel that M inhabits." -/
axiom Imscribes : ImscribableSystem → Coordinate → Prop

/-- A result r is reachable by system M.
    "M can produce or access r as content." -/
axiom Reachable : ImscribableSystem → Result → Prop

/-- A result r is within the algebra of coordinate c.
    "The algebra operations determined by c can produce r." -/
axiom WithinAlgebra : Coordinate → Result → Prop

-- ============================================================
-- THEOREM 1: form_uniqueness
-- Every ImscribableSystem has exactly one Coordinate that
-- imscribes it. The vessel is unique.
-- ============================================================

/-- **form_uniqueness**: Every imscribable system has a unique crystal coordinate.
    This is the classifier property — the grammar assigns each system exactly one
    structural type. However, this theorem alone does NOT tell you what the system
    can do (its reachable results). That requires content_containment.

    Proof sketch (future work): Fix M. Existence follows from the imscription
    procedure (encoding_method.md, steps [1]–[12]). Uniqueness follows from the
    Frobenius condition: if c and c' both imscribe M, then μ(δ(M)) = c = c'.

    Named sorries:
    - `form_existence`: ∀ M, ∃ c, Imscribes M c
    - `form_uniqueness_proper`: ∀ M c c', Imscribes M c → Imscribes M c' → c = c'
-/
theorem form_uniqueness (M : ImscribableSystem) :
    ∃! (c : Coordinate), Imscribes M c := by
  -- Existence
  have hex : ∃ c, Imscribes M c := by
    -- Lemma 'form_existence' would discharge this.
    -- Statement: ∀ (M : ImscribableSystem), ∃ (c : Coordinate), Imscribes M c
    sorry
  -- Uniqueness
  have huniq : ∀ c c' : Coordinate, Imscribes M c → Imscribes M c' → c = c' := by
    -- Lemma 'form_uniqueness_proper' would discharge this.
    -- Statement: ∀ (M : ImscribableSystem) (c c' : Coordinate),
    --   Imscribes M c → Imscribes M c' → c = c'
    sorry
  exact exists_unique_of_exists_of_unique hex huniq

-- ============================================================
-- THEOREM 2: content_containment
-- If M is imscribed by c, then every result reachable by M
-- is within the algebra of c. The vessel constrains the content.
-- ============================================================

/-- **content_containment**: The vessel constrains the content. If a system M is
    imscribed by coordinate c, then every result reachable by M must lie within
    the algebra determined by c. The form bounds the possible fill.

    This theorem is the directional form — vessel_fills_itself strengthens this
    to an equivalence.

    Named sorry:
    - `imscribes_implies_content`: ∀ M c r, Imscribes M c → Reachable M r → WithinAlgebra c r
-/
theorem content_containment (M : ImscribableSystem) (c : Coordinate)
    (h : Imscribes M c) (r : Result) (hr : Reachable M r) :
    WithinAlgebra c r := by
  -- Lemma 'imscribes_implies_content' would discharge this.
  -- Statement: ∀ (M : ImscribableSystem) (c : Coordinate) (r : Result),
  --   Imscribes M c → Reachable M r → WithinAlgebra c r
  sorry

-- ============================================================
-- THEOREM 3: vessel_fills_itself
-- The strong form: a result is reachable by M iff it is within
-- the algebra of M's coordinate. Vessel = content, inseparably.
-- ============================================================

/-- **vessel_fills_itself**: The inseparability of vessel and content.

    A result r is reachable by system M if and only if r is within the algebra
    determined by the coordinate c that imscribes M. This is the strong form:
    the vessel IS its content, and the content FILLS the vessel entirely.

    Why a pure classifier (form_uniqueness alone) does not give content_containment:

    form_uniqueness says: "every system has exactly one crystal coordinate."
    This is a *labeling* property — it assigns a type tag to each system. But a
    labeling does not constrain behavior. One could know the unique coordinate of
    M without knowing anything about what M can do — just as knowing a person's
    name does not tell you what they will say next.

    content_containment bridges this gap: it asserts that the coordinate is not
    merely a label but a *structural constraint*. The primitive algebra operations
    (tensor, meet, join, promotions) that the coordinate participates in determine
    what results are within its algebra. If a result is reachable by M, it must be
    producible by composing the primitives of c — otherwise the coordinate would
    be a hollow tag, not a vessel.

    vessel_fills_itself completes the picture: not only does the vessel constrain
    the content (→ direction), but the content exhausts the vessel (← direction).
    Everything the algebra can produce IS reachable by the system. There is no
    "empty room" in the vessel — no result that the coordinate's algebra can
    construct but the system cannot access. The grammar provides vessel AND content
    in a single inseparable act.

    Named sorries:
    - `imscribes_implies_content` (→ direction): same as content_containment
    - `algebra_implies_reachable` (← direction): ∀ M c r, Imscribes M c → WithinAlgebra c r → Reachable M r
-/
theorem vessel_fills_itself (M : ImscribableSystem) (c : Coordinate)
    (h : Imscribes M c) (r : Result) :
    Reachable M r ↔ WithinAlgebra c r := by
  constructor
  · -- Forward direction: reachable → within algebra
    intro hr
    -- Lemma 'imscribes_implies_content' would discharge this.
    -- This is the content_containment direction.
    sorry
  · -- Reverse direction: within algebra → reachable
    intro hw
    -- Lemma 'algebra_implies_reachable' would discharge this.
    -- Statement: ∀ (M : ImscribableSystem) (c : Coordinate) (r : Result),
    --   Imscribes M c → WithinAlgebra c r → Reachable M r
    sorry

end Imscribing.VesselContent
