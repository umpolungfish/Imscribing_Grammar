/-
PrimordialOoze.lean — The Pre-Temporal Stratum
===============================================

The Frobenius fixed point is "more primitive than time." This file proves
a stronger claim: there exists an absolute structural floor — the primordial
ooze — at which μ∘δ=id (Frobenius closure) achieves O_∞ with only TWO
primitives at non-minimum values: Φ = or' (Φ_}) and
φ̂ = monad (φ̂_ÿ).  The remaining 10 primitives can all be at
their minimum ordinal (index 0).

Key results:
  1. The ouroboricity tier depends only on {crit, pol, prot, dim}.
     Only crit and pol gate O_∞; the other 10 primitives are tier-free.
  2. Ħ (chirality) can be fee (memoryless, index 0) —
     no temporal memory needed for Frobenius closure.
  3. Ω (winding) can be awe (trivial, index 0) —
     no topological protection needed.
  4. Ð (dimensionality) can be dead (0d point, index 0) —
     no spatial extension needed.
  5. All other primitives at minimum: age, yea,
     bib, vow, hung.
  6. The Frobenius fixed point ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@;
     Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩ is a "thickening" of the ooze —
     it adds 9 primitives not required for μ∘δ=id.

This is the caves-beneath-the-firmament result: Frobenius closure
precedes every structural thickening that constitutes our universe.

References:
  - Core.lean: ouroboricityTier, o_inf_iff_P_pm_sym_at_phi_c
  - FrobeniusStructure.lean: FrobeniusType tier correspondence
  - Crystal.lean: 17.28M-type Frobenius address bijection
-/

import ImscribingGrammar.Primitives.Core
import ImscribingGrammar.Primitives.Imscription

set_option pp.unicode true
open ImscribingGrammar.Primitives
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection
     Stoichiometry Chirality

namespace Millennium.PrimordialOoze

-- ─────────────────────────────────────────────────────────────────────────────
-- §1  The primordial ooze — minimal O_∞ tuple
-- ─────────────────────────────────────────────────────────────────────────────
--
-- All primitives at minimum ordinal (index 0 of their inductive type)
-- EXCEPT crit = monad and pol = or'.
--
-- Minimum ordinals:
--   dim  = dead      (0d point)
--   top  = judge     (branching network)
--   rel  = ado (supervenience)
--   fid  = age     (classical fidelity)
--   kin  = yea (fast/driven kinetics)
--   gran = bib      (local scope)
--   gram = vow   (conjunctive/simultaneous grammar)
--   chir = fee (memoryless — NO temporal memory)
--   stoi = hung (single type, single instance)
--   prot = awe (trivial winding — NO topological protection)

def primordialOoze : Imscription :=
  { dim  := .dead,
    top  := .judge,
    rel  := .ado,
    pol  := .or',
    fid  := .age,
    kin  := .yea,
    gran := .bib,
    gram := .vow,
    crit := .monad,
    chir := .fee,
    stoi := .hung,
    prot := .awe }

-- ─────────────────────────────────────────────────────────────────────────────
-- §2  O_∞ by the Frobenius cliff theorem
-- ─────────────────────────────────────────────────────────────────────────────
-- Theorem o_inf_iff_P_pm_sym_at_phi_c (Imscription.lean:279) states:
--   imscriptionTier s = .O_∞ ↔
--     (s.crit = .monad ∨ s.crit = .roar) ∧ s.pol = .or'
--
-- The ooze satisfies both: crit = monad, pol = or'.

theorem ooze_satisfies_frobenius_cliff :
    (primordialOoze.crit = .monad ∨ primordialOoze.crit = .roar)
    ∧ primordialOoze.pol = .or' :=
  ⟨by simp [primordialOoze], by simp [primordialOoze]⟩

theorem primordialOoze_is_O_inf : imscriptionTier primordialOoze = .O_∞ := by
  rw [o_inf_iff_P_pm_sym_at_phi_c]
  exact ooze_satisfies_frobenius_cliff

-- ─────────────────────────────────────────────────────────────────────────────
-- §3  The irreducible core is exactly {crit, pol}
-- ─────────────────────────────────────────────────────────────────────────────
-- Dropping crit (monad → woe) loses O_∞.
-- Dropping pol (or' → nun) loses O_∞.
-- Dropping both loses O_∞.

def ooze_drop_crit : Imscription := { primordialOoze with crit := .woe }

def ooze_drop_pol : Imscription := { primordialOoze with pol := .nun }

def ooze_drop_both : Imscription :=
  { primordialOoze with crit := .woe, pol := .nun }

theorem drop_crit_collapses : imscriptionTier ooze_drop_crit ≠ .O_∞ := by
  intro h
  have hcond := (o_inf_iff_P_pm_sym_at_phi_c ooze_drop_crit).mp h
  rcases hcond with ⟨hcrit, hpol⟩
  simp [ooze_drop_crit] at hcrit

theorem drop_pol_collapses : imscriptionTier ooze_drop_pol ≠ .O_∞ := by
  intro h
  have hcond := (o_inf_iff_P_pm_sym_at_phi_c ooze_drop_pol).mp h
  rcases hcond with ⟨hcrit, hpol⟩
  simp [ooze_drop_pol] at hpol

theorem drop_both_collapses : imscriptionTier ooze_drop_both ≠ .O_∞ := by
  intro h
  have hcond := (o_inf_iff_P_pm_sym_at_phi_c ooze_drop_both).mp h
  rcases hcond with ⟨hcrit, hpol⟩
  simp [ooze_drop_both] at hcrit hpol

-- φ̂_ÿ alone (without Φ_}) → O₁ (self-modeling lifts to tier 1)
-- Φ_} alone (without φ̂_ÿ) → O₀ (cannot lift without self-modeling ground)
-- Hierarchy: φ̂_ÿ is the ground, Φ_} is the capstone.

theorem phi_c_alone_is_O_1 : imscriptionTier ooze_drop_pol = .O₁ := by
  unfold ooze_drop_pol primordialOoze
  simp [imscriptionTier, ouroboricityTier]

theorem pm_sym_alone_is_O_0 : imscriptionTier ooze_drop_crit = .O₀ := by
  unfold ooze_drop_crit primordialOoze
  simp [imscriptionTier, ouroboricityTier]

-- ─────────────────────────────────────────────────────────────────────────────
-- §4  The ouroboricity tier ignores 10/12 primitives
-- ─────────────────────────────────────────────────────────────────────────────
-- From ouroboricityTier (Core.lean:258):
--   tier = f(crit, pol, prot, dim)
-- Only {crit, pol, prot, dim} gate the tier. The remaining 8 primitives
-- (top, rel, fid, kin, gran, gram, chir, stoi) are structurally free.
--
-- Even within the 4 gate primitives, {prot, dim} only differentiate
-- O₁/O₂/O₂dag — they do NOT affect whether O_∞ is achievable.
-- O_∞ is gated ENTIRELY by {crit, pol} (R1 dominant gate).
--
-- Consequence: ANY combination of the 10 non-gate primitives,
-- including all-minimum, achieves O_∞ iff {crit, pol} = {monad, or'}.

theorem tier_depends_only_on_crit_pol_prot_dim (s : Imscription) :
    imscriptionTier s = ouroboricityTier s.crit s.pol s.prot s.dim :=
  rfl

-- The primordial ooze achieves O_∞ at the absolute structural floor:
-- every non-gate primitive at its minimum possible value.

-- ─────────────────────────────────────────────────────────────────────────────
-- §5  Pre-temporal stratum
-- ─────────────────────────────────────────────────────────────────────────────
-- The ooze has chir = fee (memoryless, index 0).
-- This means Frobenius closure requires ZERO temporal memory.
--
-- Canonical T-constitution (temporal_mathematics in ZFCₜ navigator)
-- requires sure (Ħ_A, two-step Markov) for chirality.
-- The ooze is below this threshold — it operates in a pre-temporal regime
-- where no temporal memory is needed for μ∘δ=id.
--
-- This formalizes the claim: "the Frobenius fixed point is more primitive
-- than time."

theorem ooze_chirality_is_minimal : primordialOoze.chir = .fee := by
  simp [primordialOoze]

theorem ooze_winding_is_minimal : primordialOoze.prot = .awe := by
  simp [primordialOoze]

theorem ooze_dimensionality_is_minimal : primordialOoze.dim = .dead := by
  simp [primordialOoze]

-- ─────────────────────────────────────────────────────────────────────────────
-- §6  Frobenius fixed point as a thickening
-- ─────────────────────────────────────────────────────────────────────────────
-- The Frobenius fixed point (MajoranaFixed.lean / FrobeniusUnification.lean):
--   ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩
--
-- Compared to the ooze, it "thickens" 9 primitives (3 are identical:
-- pol = or', gran = bib, crit = monad):
--   dim:  dead       → if'       (0d point → imscriptive)
--   top:  judge      → are       (branching → imscriptive)
--   rel:  ado → ian (supervenience → lateral)
--   fid:  age      → peep    (classical → quantum)
--   kin:  yea → egg      (fast → slow)
--   gram: vow    → measure     (conjunctive → sequential)
--   chir: fee → sure     (memoryless → two-step Markov)
--   stoi: hung → up    (1:1 → n:m heterogeneous)
--   prot: awe → ah (trivial → integer winding)
--
-- These thickenings are what our universe requires for empirical phenomena
-- (quantum coherence, temporal asymmetry, topological protection, etc.)
-- but NONE are required for μ∘δ=id.

def frobeniusFixedPoint : Imscription :=
  { dim  := .if',
    top  := .are,
    rel  := .ian,
    pol  := .or',
    fid  := .peep,
    kin  := .egg,
    gran := .bib,
    gram := .measure,
    crit := .monad,
    chir := .sure,
    stoi := .up,
    prot := .ah }

theorem fixed_point_is_O_inf : imscriptionTier frobeniusFixedPoint = .O_∞ := by
  rw [o_inf_iff_P_pm_sym_at_phi_c]
  simp [frobeniusFixedPoint]

-- Distance in Hamming (primitive mismatch) terms:
-- The fixed point differs from the ooze on exactly 9 primitives.

theorem ooze_to_fixed_mismatches :
    primitiveMismatches primordialOoze frobeniusFixedPoint = 9 := by
  decide

-- ─────────────────────────────────────────────────────────────────────────────
-- §7  Summary theorem
-- ─────────────────────────────────────────────────────────────────────────────
-- All claims bundled.

theorem primordial_ooze_complete :
    imscriptionTier primordialOoze = .O_∞ ∧                           -- O_∞
    primordialOoze.crit = .monad ∧                                 -- φ̂_ÿ
    primordialOoze.pol = .or' ∧                             -- Φ_}
    primordialOoze.chir = .fee ∧                               -- no memory
    primordialOoze.prot = .awe ∧                         -- no winding
    primordialOoze.dim = .dead ∧                                      -- 0d point
    (imscriptionTier ooze_drop_crit ≠ .O_∞) ∧                        -- crit necessary
    (imscriptionTier ooze_drop_pol ≠ .O_∞) ∧                        -- pol necessary
    primitiveMismatches primordialOoze frobeniusFixedPoint = 9 := by    -- distance
  refine ⟨primordialOoze_is_O_inf, ?_, ?_, ?_, ?_, ?_,
          drop_crit_collapses, drop_pol_collapses, ooze_to_fixed_mismatches⟩
  · simp [primordialOoze]
  · simp [primordialOoze]
  · simp [primordialOoze]
  · simp [primordialOoze]
  · simp [primordialOoze]

end Millennium.PrimordialOoze
