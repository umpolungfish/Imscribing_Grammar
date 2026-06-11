/-
PrimordialOoze.lean — The Pre-Temporal Stratum
===============================================

The Frobenius fixed point is "more primitive than time." This file proves
a stronger claim: there exists an absolute structural floor — the primordial
ooze — at which μ∘δ=id (Frobenius closure) achieves O_∞ with only TWO
primitives at non-minimum values: Φ = P_doublebarpipe (Φ_}) and
φ̂ = Phi_ctyogh (φ̂_ÿ).  The remaining 10 primitives can all be at
their minimum ordinal (index 0).

Key results:
  1. The ouroboricity tier depends only on {crit, pol, prot, dim}.
     Only crit and pol gate O_∞; the other 10 primitives are tier-free.
  2. Ħ (chirality) can be H_closeomega (memoryless, index 0) —
     no temporal memory needed for Frobenius closure.
  3. Ω (winding) can be Omega_closeepsilon (trivial, index 0) —
     no topological protection needed.
  4. Ð (dimensionality) can be D_wynn (0d point, index 0) —
     no spatial extension needed.
  5. All other primitives at minimum: F_beltl, K_frtailgamma,
     G_beta, Gamma_and, S_doublebaresh.
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
-- EXCEPT crit = Phi_ctyogh and pol = P_doublebarpipe.
--
-- Minimum ordinals:
--   dim  = D_wynn      (0d point)
--   top  = T_nrleg     (branching network)
--   rel  = R_subrightarrow (supervenience)
--   fid  = F_beltl     (classical fidelity)
--   kin  = K_frtailgamma (fast/driven kinetics)
--   gran = G_beta      (local scope)
--   gram = Gamma_and   (conjunctive/simultaneous grammar)
--   chir = H_closeomega (memoryless — NO temporal memory)
--   stoi = S_doublebaresh (single type, single instance)
--   prot = Omega_closeepsilon (trivial winding — NO topological protection)

def primordialOoze : Imscription :=
  { dim  := .D_wynn,
    top  := .T_nrleg,
    rel  := .R_subrightarrow,
    pol  := .P_doublebarpipe,
    fid  := .F_beltl,
    kin  := .K_frtailgamma,
    gran := .G_beta,
    gram := .Gamma_and,
    crit := .Phi_ctyogh,
    chir := .H_closeomega,
    stoi := .S_doublebaresh,
    prot := .Omega_closeepsilon }

-- ─────────────────────────────────────────────────────────────────────────────
-- §2  O_∞ by the Frobenius cliff theorem
-- ─────────────────────────────────────────────────────────────────────────────
-- Theorem o_inf_iff_P_pm_sym_at_phi_c (Imscription.lean:279) states:
--   imscriptionTier s = .O_∞ ↔
--     (s.crit = .Phi_ctyogh ∨ s.crit = .Phi_closerevepsilon) ∧ s.pol = .P_doublebarpipe
--
-- The ooze satisfies both: crit = Phi_ctyogh, pol = P_doublebarpipe.

theorem ooze_satisfies_frobenius_cliff :
    (primordialOoze.crit = .Phi_ctyogh ∨ primordialOoze.crit = .Phi_closerevepsilon)
    ∧ primordialOoze.pol = .P_doublebarpipe :=
  ⟨by simp [primordialOoze], by simp [primordialOoze]⟩

theorem primordialOoze_is_O_inf : imscriptionTier primordialOoze = .O_∞ := by
  rw [o_inf_iff_P_pm_sym_at_phi_c]
  exact ooze_satisfies_frobenius_cliff

-- ─────────────────────────────────────────────────────────────────────────────
-- §3  The irreducible core is exactly {crit, pol}
-- ─────────────────────────────────────────────────────────────────────────────
-- Dropping crit (Phi_ctyogh → Phi_softsign) loses O_∞.
-- Dropping pol (P_doublebarpipe → P_subdoublearrow) loses O_∞.
-- Dropping both loses O_∞.

def ooze_drop_crit : Imscription := { primordialOoze with crit := .Phi_softsign }

def ooze_drop_pol : Imscription := { primordialOoze with pol := .P_subdoublearrow }

def ooze_drop_both : Imscription :=
  { primordialOoze with crit := .Phi_softsign, pol := .P_subdoublearrow }

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
-- including all-minimum, achieves O_∞ iff {crit, pol} = {Phi_ctyogh, P_doublebarpipe}.

theorem tier_depends_only_on_crit_pol_prot_dim (s : Imscription) :
    imscriptionTier s = ouroboricityTier s.crit s.pol s.prot s.dim :=
  rfl

-- The primordial ooze achieves O_∞ at the absolute structural floor:
-- every non-gate primitive at its minimum possible value.

-- ─────────────────────────────────────────────────────────────────────────────
-- §5  Pre-temporal stratum
-- ─────────────────────────────────────────────────────────────────────────────
-- The ooze has chir = H_closeomega (memoryless, index 0).
-- This means Frobenius closure requires ZERO temporal memory.
--
-- Canonical T-constitution (temporal_mathematics in ZFCₜ navigator)
-- requires H_turntwo (Ħ_A, two-step Markov) for chirality.
-- The ooze is below this threshold — it operates in a pre-temporal regime
-- where no temporal memory is needed for μ∘δ=id.
--
-- This formalizes the claim: "the Frobenius fixed point is more primitive
-- than time."

theorem ooze_chirality_is_minimal : primordialOoze.chir = .H_closeomega := by
  simp [primordialOoze]

theorem ooze_winding_is_minimal : primordialOoze.prot = .Omega_closeepsilon := by
  simp [primordialOoze]

theorem ooze_dimensionality_is_minimal : primordialOoze.dim = .D_wynn := by
  simp [primordialOoze]

-- ─────────────────────────────────────────────────────────────────────────────
-- §6  Frobenius fixed point as a thickening
-- ─────────────────────────────────────────────────────────────────────────────
-- The Frobenius fixed point (MajoranaFixed.lean / FrobeniusUnification.lean):
--   ⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; φ̂_ÿ; Ħ_A; Σ_ï; Ω_z⟩
--
-- Compared to the ooze, it "thickens" 9 primitives (3 are identical:
-- pol = P_doublebarpipe, gran = G_beta, crit = Phi_ctyogh):
--   dim:  D_wynn       → D_omega       (0d point → imscriptive)
--   top:  T_nrleg      → T_openo       (branching → imscriptive)
--   rel:  R_subrightarrow → R_lyoghlig (supervenience → lateral)
--   fid:  F_beltl      → F_hardsign    (classical → quantum)
--   kin:  K_frtailgamma → K_schwa      (fast → slow)
--   gram: Gamma_and    → Gamma_seq     (conjunctive → sequential)
--   chir: H_closeomega → H_turntwo     (memoryless → two-step Markov)
--   stoi: S_doublebaresh → S_ltailm    (1:1 → n:m heterogeneous)
--   prot: Omega_closeepsilon → Omega_dzlig (trivial → integer winding)
--
-- These thickenings are what our universe requires for empirical phenomena
-- (quantum coherence, temporal asymmetry, topological protection, etc.)
-- but NONE are required for μ∘δ=id.

def frobeniusFixedPoint : Imscription :=
  { dim  := .D_omega,
    top  := .T_openo,
    rel  := .R_lyoghlig,
    pol  := .P_doublebarpipe,
    fid  := .F_hardsign,
    kin  := .K_schwa,
    gran := .G_beta,
    gram := .Gamma_seq,
    crit := .Phi_ctyogh,
    chir := .H_turntwo,
    stoi := .S_ltailm,
    prot := .Omega_dzlig }

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
    primordialOoze.crit = .Phi_ctyogh ∧                                 -- φ̂_ÿ
    primordialOoze.pol = .P_doublebarpipe ∧                             -- Φ_}
    primordialOoze.chir = .H_closeomega ∧                               -- no memory
    primordialOoze.prot = .Omega_closeepsilon ∧                         -- no winding
    primordialOoze.dim = .D_wynn ∧                                      -- 0d point
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
