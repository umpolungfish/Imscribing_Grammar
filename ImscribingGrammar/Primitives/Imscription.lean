-- ImscribingGrammar/Primitives/Imscription.lean
-- Imscription struct, primitive distance (Hamming + ordinal), and key encodings.
-- Proves P-70 (Higgs = axion = inflaton) by rfl.
-- All primitive names are canonical (v0.5.69).

import ImscribingGrammar.Primitives.Core

namespace ImscribingGrammar.Primitives

open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection
     Stoichiometry Chirality

-- ============================================================
-- IMSCRIPTION STRUCT
-- An Imscription is a 12-tuple ⟨D; T; R; P; F; K; G; Γ; Φ; H; S; Ω⟩.
-- Field name 'rel' used for Relational (R) since 'rec' is reserved in Lean 4.
-- @[ext] generates Imscription.ext for pointwise equality.
-- ============================================================

@[ext]
structure Imscription : Type where
  dim   : Dimensionality   -- D
  top   : Topology         -- T
  rel   : Relational       -- R
  pol   : Polarity         -- P
  fid   : Fidelity         -- F
  kin   : KineticChar      -- K
  gran  : Granularity      -- G
  gram  : Grammar          -- Γ
  crit  : Criticality      -- Φ
  chir  : Chirality        -- H
  stoi  : Stoichiometry    -- S
  prot  : Protection       -- Ω
  deriving DecidableEq, Repr

-- ============================================================
-- HAMMING DISTANCE
-- Count of component mismatches. Zero iff tuples are identical.
-- ============================================================

def primitiveMismatches (a b : Imscription) : Nat :=
  (if a.dim  = b.dim  then 0 else 1) +
  (if a.top  = b.top  then 0 else 1) +
  (if a.rel  = b.rel  then 0 else 1) +
  (if a.pol  = b.pol  then 0 else 1) +
  (if a.fid  = b.fid  then 0 else 1) +
  (if a.kin  = b.kin  then 0 else 1) +
  (if a.gran = b.gran then 0 else 1) +
  (if a.gram = b.gram then 0 else 1) +
  (if a.crit = b.crit then 0 else 1) +
  (if a.chir = b.chir then 0 else 1) +
  (if a.stoi = b.stoi then 0 else 1) +
  (if a.prot = b.prot then 0 else 1)

theorem primitiveMismatches_self (a : Imscription) : primitiveMismatches a a = 0 := by
  simp [primitiveMismatches]

theorem primitiveMismatches_symm (a b : Imscription) :
    primitiveMismatches a b = primitiveMismatches b a := by
  simp only [primitiveMismatches, eq_comm]

private lemma ite_mismatch_le_one (p : Prop) [Decidable p] :
    (if p then 0 else 1) ≤ 1 := by split_ifs <;> omega

theorem primitiveMismatches_le_12 (a b : Imscription) :
    primitiveMismatches a b ≤ 12 := by
  unfold primitiveMismatches
  have h1  := ite_mismatch_le_one (a.dim  = b.dim)
  have h2  := ite_mismatch_le_one (a.top  = b.top)
  have h3  := ite_mismatch_le_one (a.rel  = b.rel)
  have h4  := ite_mismatch_le_one (a.pol  = b.pol)
  have h5  := ite_mismatch_le_one (a.fid  = b.fid)
  have h6  := ite_mismatch_le_one (a.kin  = b.kin)
  have h7  := ite_mismatch_le_one (a.gran = b.gran)
  have h8  := ite_mismatch_le_one (a.gram = b.gram)
  have h9  := ite_mismatch_le_one (a.crit = b.crit)
  have h10 := ite_mismatch_le_one (a.chir = b.chir)
  have h11 := ite_mismatch_le_one (a.stoi = b.stoi)
  have h12 := ite_mismatch_le_one (a.prot = b.prot)
  omega

theorem primitiveMismatches_zero_iff (a b : Imscription) :
    primitiveMismatches a b = 0 ↔ a = b := by
  constructor
  · intro h
    unfold primitiveMismatches at h
    ext
    all_goals {
      by_contra hne
      have hterm : (if _ = _ then 0 else 1) = 1 := if_neg hne
      simp only [hterm] at h; omega
    }
  · rintro rfl; exact primitiveMismatches_self a

-- ============================================================
-- TENSOR PRODUCT (structural composition)
-- Union primitives: max (D, T, R, G, Γ, Φ, H, S, Ω)
-- Bottleneck primitives: min (P, F) — weaker partner wins
-- ============================================================

def tensorProduct (a b : Imscription) : Imscription := {
  dim  := if compare a.dim  b.dim  = .lt then b.dim  else a.dim   -- max
  top  := if compare a.top  b.top  = .lt then b.top  else a.top   -- max
  rel  := if compare a.rel  b.rel  = .lt then b.rel  else a.rel   -- max
  pol  := if compare a.pol  b.pol  = .lt then a.pol  else b.pol   -- min (bottleneck)
  fid  := if compare a.fid  b.fid  = .lt then a.fid  else b.fid   -- min (bottleneck)
  kin  := if compare a.kin  b.kin  = .lt then b.kin  else a.kin   -- max
  gran := if compare a.gran b.gran = .lt then b.gran else a.gran   -- max
  gram := if compare a.gram b.gram = .lt then b.gram else a.gram   -- max
  crit := if compare a.crit b.crit = .lt then b.crit else a.crit   -- max
  chir := if compare a.chir b.chir = .lt then b.chir else a.chir   -- max
  stoi := if compare a.stoi b.stoi = .lt then b.stoi else a.stoi   -- max
  prot := if compare a.prot b.prot = .lt then b.prot else a.prot   -- max
}

-- P-bottleneck: O_∞ ⊗ O₂ → or' ⊗ nun = nun (Frobenius destroyed).
theorem tensor_P_bottleneck (a b : Imscription) :
    (tensorProduct a b).pol =
      if compare a.pol b.pol = .lt then a.pol else b.pol := rfl

-- ============================================================
-- OUROBORICITY OF A SYNTHON
-- ============================================================

def imscriptionTier (s : Imscription) : OuroboricityTier :=
  ouroboricityTier s.crit s.pol s.prot s.dim

-- ============================================================
-- KEY ENCODINGS
-- ============================================================

-- ── P-70: Scalar egg template (Higgs / axion / inflaton) ──
-- All three are spin-0 fields with double-well potential, slow-roll /
-- SSB relaxation (egg), symmetric potential (or' at monad).
-- They differ in energy scale only — not in primitive structure.
def scalarField_Kslow : Imscription := {
  dim  := ash   -- local simplicial field (not imscriptive)
  top  := mime     -- double-well / figure-8 potential landscape
  rel  := ear     -- field ↔ vacuum bidirectional (SSB is reciprocal)
  pol  := or'     -- exact Z_2 symmetry at monad (μ ∘ δ = id)
  fid  := peep       -- quantum coherent
  kin  := egg       -- slow-roll / thermally activated SSB (THE defining feature)
  gran := bib       -- mesoscale local description
  gram := vow    -- all SSB conditions required simultaneously
  crit := monad        -- SSB is a phase transition
  chir := kick           -- soft temporal asymmetry (vacuum selection)
  stoi := so          -- field-to-excitation: matched coupling
  prot := awe      -- no topological protection of the vacuum
}

def higgs    : Imscription := scalarField_Kslow
def axion    : Imscription := scalarField_Kslow
def inflaton : Imscription := scalarField_Kslow

/-- P-70a: Higgs and axion are structurally identical. -/
theorem P70a_higgs_axion_identity : higgs = axion := rfl

/-- P-70b: Axion and inflaton are structurally identical. -/
theorem P70b_axion_inflaton_identity : axion = inflaton := rfl

/-- P-70 (full): Three-scale egg symmetry. -/
theorem P70_three_scale_Kslow :
    higgs = axion ∧ axion = inflaton ∧ higgs = inflaton :=
  ⟨rfl, rfl, rfl⟩

/-- All three scalar egg fields are O_∞. -/
theorem scalar_Kslow_is_O_inf : imscriptionTier scalarField_Kslow = .O_∞ := by decide

-- ── Standard Model ──────────────────────────────────────────
def standard_model : Imscription := {
  dim  := array      -- 4D spacetime (unbounded temporal generation)
  top  := judge    -- gauge group connections: general graph
  rel  := tot        -- compositional: gauge group × matter sector
  pol  := out         -- Z_2 discrete symmetry (CP)
  fid  := they        -- threshold: classical field theory with quantum corrections
  kin  := loll        -- perturbative (no confinement at this level)
  gran := ice      -- all-scale: renormalization group runs to all scales
  gram := vow    -- gauge + matter + Higgs all simultaneously required
  crit := monad        -- electroweak phase transition is a critical phenomenon
  chir := sure           -- persistent chirality (CKM matrix, neutrino mixing)
  stoi := up          -- many particles, unmatched coupling strengths
  prot := ah      -- instanton winding numbers (integer)
}

-- ── Quantum Gravity ─────────────────────────────────────────
-- if' and are are co-required (Axiom C).
def quantum_gravity : Imscription := {
  dim  := if'       -- imscriptive: boundary encodes bulk
  top  := are       -- imscriptive topology (co-required with if')
  rel  := ear     -- bulk ↔ boundary reciprocal
  pol  := or'     -- diffeomorphism invariance at criticality: Special Frobenius
  fid  := peep       -- quantum
  kin  := on       -- Planck-scale dynamics are frozen at low energy
  gran := ice      -- Planck-scale: all-to-all correlations
  gram := ooze  -- graviton couples universally (broadcast)
  crit := monad        -- quantum criticality at Planck scale
  chir := wool        -- topological chirality (CPT asymmetry at Planck scale)
  stoi := up          -- many gravitational sources, unmatched
  prot := zoo     -- non-Abelian topological protection
}

/-- Quantum gravity is O_∞ (imscriptive Frobenius). -/
theorem qg_is_O_inf : imscriptionTier quantum_gravity = .O_∞ := by decide

-- ── General Relativity ──────────────────────────────────────
def general_relativity : Imscription := {
  dim  := array      -- 4D spacetime (not imscriptive — classical GR is local)
  top  := judge    -- causal structure: general graph of events
  rel  := ear     -- metric ↔ matter bidirectional (Einstein equations)
  pol  := nun        -- full diffeomorphism invariance
  fid  := peep       -- classical limit of a quantum theory
  kin  := egg       -- geodesic motion is slow compared to Planck scale
  gran := thigh      -- collective: macroscopic description
  gram := vow    -- all matter + metric conditions simultaneously
  crit := woe      -- no quantum criticality in classical GR
  chir := kick           -- soft temporal asymmetry (arrow of time via initial conditions)
  stoi := so          -- matched: one metric for all matter
  prot := awe      -- no topological protection
}

-- ── Yang-Mills (classical, pre-quantization) ────────────────
def yang_mills_classical : Imscription := {
  dim  := array      -- 4D Minkowski spacetime
  top  := judge    -- gauge group connections
  rel  := tot        -- compositional: gauge covariant derivative
  pol  := out         -- Z_2 discrete parity
  fid  := they        -- classical field theory
  kin  := loll        -- perturbative regime
  gran := bib       -- local: Lagrangian density at each point
  gram := vow    -- gauge invariance requires all conditions
  crit := woe      -- no mass gap yet
  chir := kick           -- weak temporal asymmetry
  stoi := so          -- gauge field ↔ matter: matched
  prot := ah      -- instanton winding numbers
}

-- ── Yang-Mills (quantum target) ─────────────────────────────
-- The target tuple if the path integral measure existed.
-- Gap from classical: F(eth→hbar), K(mod→trap), G(beth→aleph), Φ(sub→c) = 4 mismatches.
def yang_mills_quantum_target : Imscription := {
  dim  := array
  top  := judge
  rel  := tot
  pol  := out
  fid  := peep       -- quantum coherence
  kin  := on       -- confinement = kinetic trapping
  gran := ice      -- fine-grained: requires path integral measure
  gram := vow
  crit := monad        -- mass gap is a critical phenomenon
  chir := kick
  stoi := so
  prot := ah
}

/-- The YM barrier is exactly 4 primitive mismatches. -/
theorem ym_barrier_4_primitives :
    primitiveMismatches yang_mills_classical yang_mills_quantum_target = 4 := by decide

-- ── SM ↔ QG distance ────────────────────────────────────────
/-- Standard Model and Quantum Gravity differ on 9 primitives. -/
theorem sm_qg_distance :
    primitiveMismatches standard_model quantum_gravity = 9 := by decide

-- ── GR → Asymptotic Safety: 3 primitive changes ─────────────
def asymptotic_safety : Imscription := { general_relativity with
  kin  := loll    -- UV fixed point has moderate kinetics
  gran := ice  -- Planck-scale fine-grained
  crit := monad    -- UV fixed point IS a quantum critical point
}

theorem gr_as_morphism_cost :
    primitiveMismatches general_relativity asymptotic_safety = 3 := by decide

-- ============================================================
-- STRUCTURAL THEOREMS
-- ============================================================

/-- Frobenius cliff: O_∞ requires or'. No other Polarity gives O_∞
    regardless of Φ, Ω, D. (Lean-verified statement of §23 / §69.) -/
theorem o_inf_iff_P_pm_sym_at_phi_c (s : Imscription) :
    imscriptionTier s = .O_∞ ↔
    (s.crit = .monad ∨ s.crit = .roar) ∧ s.pol = .or' := by
  constructor
  · intro h
    constructor
    · exact o_inf_requires_phi_c s.crit s.pol s.prot s.dim h
    · exact o_inf_requires_P_pm_sym s.crit s.pol s.prot s.dim h
  · intro ⟨hphi, hpol⟩
    simp [imscriptionTier, ouroboricityTier]
    cases hphi with
    | inl h => simp [h, hpol]
    | inr h => simp [h, hpol]

/-- Higgs is O_∞ (P-70 claim). -/
theorem higgs_is_O_inf : imscriptionTier higgs = .O_∞ := by decide

/-- Tensor of O_∞ with any O₂ system (nun) gives nun — Frobenius destroyed. -/
theorem tensor_O_inf_O2_destroys_frobenius (s_inf s_two : Imscription)
    (h_inf : s_inf.pol = .or') (h_two : s_two.pol = .nun) :
    (tensorProduct s_inf s_two).pol = .nun := by
  simp [tensorProduct, h_inf, h_two]
  -- Need to prove ¬compare or' nun = .lt
  intro h
  -- compare is Ord.compare; for Polarity derived Ord, or' (idx 4) vs nun (idx 3)
  have : Ord.compare or' nun = .gt := by decide
  simp [this] at h

end ImscribingGrammar.Primitives
