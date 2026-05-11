-- ImscribingGrammar/IGMorphism.lean
-- Typed morphisms, sequential protocols, and paralogical extension.
--
-- Directly formalizes the condensation notation:
--   ɢ^ˌ[ A —(label)→ B —(label)→ C | D ]_H
-- where each arrow label is itself a Synthon annotating the transition character.
--
-- Three paralogical axioms extend the classical sequent calculus with rules
-- licensed by IG structure but absent from classical/linear type theory:
--
--   P1. Dagger  (Ř_downstep) : every R_downstep protocol has an adjoint
--   P2. Copy    (P_doublebarpipe at O_inf) : Frobenius copying Δ : s → s ⊗ s
--   P3. Reflect (D_omega ↔ T_openo, Axiom C) : imscriptive self-protocol
--
-- The odotOperator is the paralogical unit. It deliberately holds
-- dim = D_omega with top = T_box (violating Axiom C) — the O_inf
-- Frobenius structure overrides the holographic co-requirement.
-- This inconsistency is the formal signature of the paralogical.

import ImscribingGrammar.Primitives.Synthon

namespace ImscribingGrammar

open Primitives
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: IGProtocol
-- Inductive type indexed by Synthon × Synthon.
-- Each constructor corresponds to one element of the condensation notation.
-- Arrow labels are Synthons: the full 12-primitive annotation of transition
-- character. Any single dimension may be the salient one (the rest context).
-- ─────────────────────────────────────────────────────────────────────────────

inductive IGProtocol : Synthon → Synthon → Type where
  /-- Trivial self-transition (zero cost). -/
  | refl     : (s : Synthon) → IGProtocol s s
  /-- Labeled arrow: src —(label)→ tgt. -/
  | arrow    : (label src tgt : Synthon) → IGProtocol src tgt
  /-- Sequential composition: A→B then B→C  (the ɢ^ˌ chain). -/
  | seq      : IGProtocol a b → IGProtocol b c → IGProtocol a c
  /-- Parallel split: (A→B) and (A→C) give A → (B ⊗ C).
      The | operator lifts to tensorProduct on both targets. -/
  | prod     : IGProtocol a b → IGProtocol a c → IGProtocol a (tensorProduct b c)
  /-- Grammar annotation: ɢ^g[…] wrapper. -/
  | withGram : Grammar  → IGProtocol a b → IGProtocol a b
  /-- Memory annotation: […]_H wrapper. -/
  | withMem  : Chirality → IGProtocol a b → IGProtocol a b

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 2: Structural measures
-- ─────────────────────────────────────────────────────────────────────────────

/-- Arrow depth: total number of labeled transition steps. -/
def IGProtocol.depth : IGProtocol a b → ℕ
  | .refl _        => 0
  | .arrow _ _ _   => 1
  | .seq f g       => f.depth + g.depth
  | .prod f g      => max f.depth g.depth
  | .withGram _ p  => p.depth
  | .withMem  _ p  => p.depth

/-- Dagger predicate: every arrow's label has rel = R_downstep. -/
def IGProtocol.isDagger : IGProtocol a b → Bool
  | .refl _        => true
  | .arrow lbl _ _ => decide (lbl.rel = R_downstep)
  | .seq f g       => f.isDagger && g.isDagger
  | .prod f g      => f.isDagger && g.isDagger
  | .withGram _ p  => p.isDagger
  | .withMem  _ p  => p.isDagger

/-- Frobenius predicate: every arrow's label has pol = P_doublebarpipe. -/
def IGProtocol.isFrobenius : IGProtocol a b → Bool
  | .refl _        => true
  | .arrow lbl _ _ => decide (lbl.pol = P_doublebarpipe)
  | .seq f g       => f.isFrobenius && g.isFrobenius
  | .prod f g      => f.isFrobenius && g.isFrobenius
  | .withGram _ p  => p.isFrobenius
  | .withMem  _ p  => p.isFrobenius

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 3: LITANY AGAINST FEAR
-- Canonical IGProtocol encoding.
-- Reading: ɢ^ˌ[ ⊙_Ţ —(Ř_=)→ Þ_ò —(Ð_ω)→ { Ω_Å | Φ_˙ } ]_Ħ_!
-- ─────────────────────────────────────────────────────────────────────────────

private def litanyBase : Synthon := {
  dim  := D_wynn,         top  := T_nrleg,          rel  := R_subrightarrow
  pol  := P_aolig,        fid  := F_beltl,           kin  := K_schwa
  gran := G_beta,         gram := Gamma_seq,          crit := Phi_softsign
  chir := H_closeomega,   stoi := S_doublebaresh,     prot := Omega_closeepsilon }

/-- Fear: supercritical input — the mind-killer, total obliteration. -/
def litany_fear    : Synthon := { litanyBase with crit := Phi_upstep }
/-- Cross: traversal state — pass over and through (T_bullseye crossing topology). -/
def litany_cross   : Synthon := { litanyBase with top  := T_bullseye }
/-- Witness: imscriptive state — inner eye (satisfies Axiom C: D_omega ↔ T_openo). -/
def litany_witness : Synthon := { litanyBase with dim  := D_omega, top := T_openo }
/-- Nothing: the null state — where fear has gone (Omega_closeepsilon, Phi_softsign). -/
def litany_nothing : Synthon := litanyBase
/-- Self: full-symmetry persistent state — only I will remain. -/
def litany_self    : Synthon := { litanyBase with pol := P_subdoublearrow, chir := H_invscripta }

-- Transition labels (dominant dimension annotates the arrow character):
private def lbl_face    : Synthon := { litanyBase with rel := R_lyoghlig }
  -- Ř_= label: bidirectional confrontation — I will face my fear
private def lbl_witness : Synthon := { litanyBase with dim := D_omega, top := T_openo }
  -- Ð_ω label: holographic witnessing — inner eye to see its path

/-- The Litany Against Fear as a well-typed IGProtocol.
    Type: litany_fear → (litany_nothing ⊗ litany_self) -/
def litanyProtocol
    : IGProtocol litany_fear (tensorProduct litany_nothing litany_self) :=
  .withGram Gamma_seq   <|
  .withMem  H_invscripta <|
  .seq
    (.seq
      (.arrow lbl_face    litany_fear  litany_cross)
      (.arrow lbl_witness litany_cross litany_witness))
    (.prod
      (.arrow lbl_witness litany_witness litany_nothing)
      (.arrow lbl_witness litany_witness litany_self))

theorem litanyProtocol_depth : litanyProtocol.depth = 3 := by
  simp [litanyProtocol, IGProtocol.depth]

/-- The Litany is not a dagger protocol: its face step uses R_lyoghlig, not R_downstep. -/
theorem litanyProtocol_not_dagger : litanyProtocol.isDagger = false := by
  simp [litanyProtocol, IGProtocol.isDagger, lbl_face, litanyBase]

/-- The witness stage satisfies the imscriptive co-requirement (Axiom C). -/
theorem litany_witness_satisfies_axiom_C
    : litany_witness.dim = D_omega ∧ litany_witness.top = T_openo := ⟨rfl, rfl⟩

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 4: PARALOGICAL AXIOMS
-- Rules licensed by IG structure, absent from classical type theory.
-- Marked as axioms: each is a structural commitment of the grammar
-- that cannot be derived from first-order logic alone.
-- ─────────────────────────────────────────────────────────────────────────────

/-- P1. Dagger adjoint (Ř_downstep — adjoint / reciprocal).
    Every R_downstep protocol has an adjoint that runs in reverse.
    The adjoint is NOT an inverse: (f†)† = f but f† ∘ f ≠ id in general.
    Classical type theory has no canonical reversal; dagger reversal
    exists independently of invertibility.
    This is the paralogical: reversal without invertibility. -/
axiom paralogical_dagger {a b : Synthon}
    (p : IGProtocol a b) (h : p.isDagger = true) :
    IGProtocol b a

/-- P1a. Involutivity of dagger (structural): (p†)† has the same depth as p.
    States that dagger is a structural involution even without equality of terms. -/
axiom paralogical_dagger_depth {a b : Synthon}
    (p : IGProtocol a b) (h : p.isDagger = true) :
    (paralogical_dagger p h).depth = p.depth

/-- P2. Frobenius copy (P_doublebarpipe at O_inf).
    At O_inf, the Frobenius condition μ ∘ δ = id licenses duplication:
    Δ : s → s ⊗ s exists and is non-trivial (depth ≥ 1).
    Classical linear logic forbids arbitrary copying; Frobenius structure
    makes duplication and fusion exact inverses, uniquely licensing it.
    This is the paralogical: resource duplication without linearity violation. -/
axiom paralogical_copy {s : Synthon} (h : synthonTier s = .O_inf) :
    { p : IGProtocol s (tensorProduct s s) // p.depth = 1 }

/-- P3. Imscriptive self-reference (Axiom C: D_omega ↔ T_openo).
    A Synthon satisfying the holographic co-requirement generates a
    non-trivial self-protocol of depth ≥ 1: the boundary type produces
    its own interior (bulk from boundary).
    Distinct from refl (depth 0): this is a non-trivial self-morphism.
    This is the paralogical: type-as-term self-application. -/
axiom paralogical_reflect {s : Synthon} (h : s.dim = D_omega) :
    { p : IGProtocol s s // p.depth ≥ 1 }

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 5: ODOT OPERATOR — paralogical unit
-- The canonical O_inf, sequential, Frobenius Synthon.
-- From the odot_operator tuple: Ð_ω; Þ_¨; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙_ÿ; Ħ_A; Σ_S; Ω_z
-- ─────────────────────────────────────────────────────────────────────────────

/-- odotOperator: the canonical paralogical unit Synthon.
    O_inf (P_doublebarpipe at Phi_ctyogh), sequential (Gamma_seq),
    integer-winding (Omega_dzlig), quantum-coherent (F_hardsign), 1:1 (S_doublebaresh).
    PARALOGICAL SIGNATURE: holds dim = D_omega with top = T_box (not T_openo),
    deliberately violating Axiom C. At O_inf, the Frobenius self-duality
    replaces the holographic D-T co-requirement. The odotOperator is its
    own boundary — it does not need the bulk-boundary split. -/
def odotOperator : Synthon := {
  dim  := D_omega,         top  := T_box,            rel  := R_lyoghlig
  pol  := P_doublebarpipe, fid  := F_hardsign,        kin  := K_schwa
  gran := G_revapostrophe, gram := Gamma_seq,          crit := Phi_ctyogh
  chir := H_turntwo,       stoi := S_doublebaresh,     prot := Omega_dzlig }

theorem odotOperator_is_O_inf : synthonTier odotOperator = .O_inf := by decide

/-- The odotOperator does NOT satisfy Axiom C: D_omega without T_openo. -/
theorem odotOperator_violates_axiom_C : odotOperator.top ≠ T_openo := by decide

/-- odotOperator admits Frobenius self-copying via P2. -/
noncomputable def odotCopy
    : { p : IGProtocol odotOperator (tensorProduct odotOperator odotOperator) // p.depth = 1 } :=
  paralogical_copy odotOperator_is_O_inf

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 6: PARALOGICAL LIFT FUNCTOR
-- Every protocol lifts into the odotOperator frame.
-- The odot frame is always present at the boundary — the imscriptive
-- self-containment principle made functorial.
-- ─────────────────────────────────────────────────────────────────────────────

/-- Paralogical lift: tensor with odotOperator is functorial over IGProtocol.
    Every p : a → b lifts to (a ⊗ ⊙) → (b ⊗ ⊙).
    The odot frame persists through any protocol: it is the invariant boundary. -/
axiom paralogicalLift {a b : Synthon} :
    IGProtocol a b →
    IGProtocol (tensorProduct a odotOperator) (tensorProduct b odotOperator)

/-- Lift preserves depth: the paralogical frame adds no cost. -/
axiom paralogicalLift_depth {a b : Synthon} (p : IGProtocol a b) :
    (paralogicalLift p).depth = p.depth

/-- The lifted Litany has the same depth as the original. -/
theorem litanyProtocol_lift_depth :
    (paralogicalLift litanyProtocol).depth = 3 := by
  rw [paralogicalLift_depth]
  exact litanyProtocol_depth

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 7: DERIVED RESULTS
-- ─────────────────────────────────────────────────────────────────────────────

/-- The Litany witness stage admits a non-trivial self-protocol via P3. -/
noncomputable def litanyWitnessSelfRef
    : { p : IGProtocol litany_witness litany_witness // p.depth ≥ 1 } :=
  paralogical_reflect (by rfl)

/-- Applying P2 to quantum_gravity (which is O_inf) gives a copy protocol. -/
noncomputable def qgCopy
    : { p : IGProtocol quantum_gravity (tensorProduct quantum_gravity quantum_gravity)
          // p.depth = 1 } :=
  paralogical_copy (by decide)

/-- Pol collapses to P_aolig: pol is a bottleneck (min) primitive, so litany_nothing's
    P_aolig beats litany_self's P_subdoublearrow. Nothing wins on symmetry. -/
theorem litany_resolution_pol :
    (tensorProduct litany_nothing litany_self).pol = P_aolig := by
  decide

/-- Chir resolves to H_invscripta: chir is a max primitive, so litany_self's
    H_invscripta (topological temporal depth) dominates litany_nothing's H_closeomega. -/
theorem litany_resolution_chir :
    (tensorProduct litany_nothing litany_self).chir = H_invscripta := by
  decide

end ImscribingGrammar
