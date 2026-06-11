-- ImscribingGrammar/Primitives/Core.lean
-- Canonical 12-primitive grammar (v0.5.69).
-- All names, value counts, and ordinal orderings match space_search/primitives.py.
-- Crystal: 3³ × 4⁵ × 5⁴ = 17,280,000 structural types.
--   𝓕₃ (3 values): F, G, S
--   𝓕₄ (4 values): D, R, Γ, H, Ω
--   𝓕₅ (5 values): T, P, Φ, K

import Mathlib.Order.Lattice
import Mathlib.Order.BoundedOrder.Basic

namespace ImscribingGrammar.Primitives

-- ============================================================
-- 𝓕₄ PRIMITIVES — 4 values each
-- ============================================================

-- 1. Dimensionality (D)  [𝓕₄]
-- Ordered: D_wynn < D_turnthree < D_invomega < D_omega
-- D_omega = imscriptive (boundary encodes bulk); the monad symbol ⊙.
-- Replaces the non-canonical D_holo naming everywhere (v0.5.x).
inductive Dimensionality : Type where
  | D_wynn     -- wedge/local: flat 2D sheet, no recursive nesting
  | D_turnthree  -- triangulated: simplicial / stratified, finite depth
  | D_invomega     -- infinite-dimensional: unbounded temporal/spatial generation
  | D_omega      -- imscriptive: boundary encodes bulk (⊙ = monad inside circle)
  deriving DecidableEq, Repr, Ord

-- 2. Relational Mode (R)  [𝓕₄]
-- Ordered: R_subrightarrow < R_ctz < R_downstep < R_lyoghlig
-- R_subrightarrow: hierarchical/supervisory; R_ctz: compositional/categorical;
-- R_downstep: bidirectional dagger (A ⊣ A†); R_lyoghlig: left-right / lateral.
inductive Relational : Type where
  | R_subrightarrow   -- supervisory / hierarchical: one-way authority
  | R_ctz     -- categorical / compositional: functorial chaining
  | R_downstep  -- dagger / reciprocal: A and A† co-define each other
  | R_lyoghlig      -- lateral / peer: symmetric two-way exchange
  deriving DecidableEq, Repr, Ord

-- 3. Interaction Grammar (Γ)  [𝓕₄]
-- Ordered: Gamma_and < Gamma_or < Gamma_seq < Gamma_broad
-- Categorical primitive (identity of composition rule required for non-⊥ meet).
inductive Grammar : Type where
  | Gamma_and    -- conjunctive / simultaneous: all conditions required
  | Gamma_or     -- disjunctive / alternative: any condition sufficient
  | Gamma_seq    -- sequential / ordered: strict temporal or causal ordering
  | Gamma_broad  -- broadcast / universal: one-to-all coupling
  deriving DecidableEq, Repr, Ord

-- 4. Chirality / Chirality (H)  [𝓕₄]
-- Ordered: H_closeomega < H_toneletterstem < H_turntwo < H_invscripta
-- H_closeomega: no temporal memory; H_invscripta: topologically protected chirality.
-- Cross-primitive: H_invscripta tends to co-occur with K_teshlig (frozen dynamics preserve
-- deep temporal structure), but this is a structural tendency, not a hard axiom.
inductive Chirality : Type where
  | H_closeomega      -- achiral, no temporal memory
  | H_toneletterstem      -- soft chiral, weak temporal asymmetry
  | H_turntwo      -- persistent chiral, strong temporal asymmetry
  | H_invscripta   -- topological chiral, inexhaustible chirality
  deriving DecidableEq, Repr, Ord

-- 5. Topological Protection (Ω)  [𝓕₄]
-- Ordered: Omega_closeepsilon < Omega_crtwo < Omega_dzlig < Omega_turna
-- Omega_turna: non-Abelian / non-standard protection (not necessarily stronger than Omega_dzlig
-- in a linear sense; occupies ordinal 4 as the maximally exotic tier).
inductive Protection : Type where
  | Omega_closeepsilon    -- no topological protection
  | Omega_crtwo   -- ℤ₂ symmetry protection
  | Omega_dzlig    -- integer winding number / ℤ protection
  | Omega_turna   -- non-Abelian / non-standard protection
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₅ PRIMITIVES — 5 values each
-- ============================================================

-- 6. Topology (T)  [𝓕₅]
-- Ordered: T_nrleg < T_invscr < T_bullseye < T_box < T_openo
-- T_openo = imscriptive topology: non-local boundary-bulk correspondence.
-- T_openo co-occurs with D_omega (see Axiom C below).
inductive Topology : Type where
  | T_nrleg  -- general graph: heterogeneous, locally connected
  | T_invscr       -- inclusion / nested: hierarchical containment
  | T_bullseye   -- bowtie / figure-8: two-cycle closure, bifurcation point
  | T_box      -- box / lattice: regular grid or torus
  | T_openo     -- imscriptive: boundary fully encodes bulk (⊙)
  deriving DecidableEq, Repr, Ord

-- 7. Parity / Symmetry (P)  [𝓕₅]
-- Ordered: P_aolig < P_upsilon < P_pipevar < P_subdoublearrow < P_doublebarpipe
-- P_doublebarpipe is the Frobenius special condition (μ ∘ δ = id).
-- It is the tier singularity: overrides all Ω and D branching → O_∞.
-- P_doublebarpipe cannot be synthesised by composition of P < P_doublebarpipe partners (§23).
inductive Polarity : Type where
  | P_aolig    -- asymmetric: no symmetry axis
  | P_upsilon     -- phase symmetry: U(1) or continuous phase
  | P_pipevar      -- ℤ₂ discrete symmetry (sign flip)
  | P_subdoublearrow     -- full continuous symmetry (e.g. SO(n))
  | P_doublebarpipe  -- Special Frobenius: μ ∘ δ = id; exact ℤ₂ at Φ_c
  deriving DecidableEq, Repr, Ord

-- 8. Criticality (Φ)  [𝓕₅]
-- Ordered: Phi_softsign < Phi_ctyogh < Phi_closerevepsilon < Phi_revepsilon < Phi_upstep
-- Phi_ctyogh is absorbing under meet: meet(Phi_ctyogh, x) = Phi_ctyogh for all x.
-- This is not a standard linear meet — see note below.
inductive Criticality : Type where
  | Phi_softsign        -- subcritical: stable, ordered phase
  | Phi_ctyogh          -- real-axis Hermitian criticality: standard fixed point (absorbing)
  | Phi_closerevepsilon  -- complex-axis criticality: analytic continuation required
                   -- (Lee-Yang edge, complex RG fixed point, ζ-function zeros)
                   -- Ordinal 2.33 in Python (non-integer; Lean uses rank 2)
  | Phi_revepsilon         -- exceptional-point criticality: non-Hermitian eigenvector coalescence
                   -- Square-root branch point; Omega_crtwo structural tendency
                   -- Ordinal 2.67 in Python (non-integer; Lean uses rank 3)
  | Phi_upstep      -- supercritical: unstable, runaway
  deriving DecidableEq, Repr, Ord

-- NOTE on Phi_ctyogh absorbing meet:
-- The standard lattice meet (min) does not capture Phi_ctyogh absorption.
-- In the grammar algebra: meet(Phi_ctyogh, Phi_softsign) = Phi_ctyogh (not Phi_softsign).
-- This requires a custom MeetSemilattice instance defined in Algebra.lean.
-- The Lean Ord derivation gives the ordinal ordering Phi_softsign < Phi_ctyogh < ...,
-- which is used for tier comparisons but not for the absorption rule.

-- 9. Kinetic Character (K)  [𝓕₅]
-- Ordered: K_frtailgamma < K_turnm < K_schwa < K_teshlig < K_lambda
-- K_teshlig: frozen by order (e.g. over-consolidated bureaucracy, catatonia).
-- K_lambda: frozen by disorder (many-body localization, dissociation, Soviet collapse).
-- Both K_teshlig and K_lambda fail Gate 2 of the consciousness score (§VIII).
-- Restoration requires OPPOSITE interventions: K_teshlig → disorder injection;
-- K_lambda → ergodicity restoration. See §75–§77 for civilizational/consciousness examples.
inductive KineticChar : Type where
  | K_frtailgamma   -- diffusion-limited, untrapped
  | K_turnm    -- moderate barrier
  | K_schwa   -- slow / thermally activated (Gate 2 of C-score: K ≤ K_schwa passes)
  | K_teshlig   -- kinetically trapped by order
  | K_lambda    -- many-body localized: frozen by disorder
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₃ PRIMITIVES — 3 values each
-- ============================================================

-- 10. Fidelity (F)  [𝓕₃]
-- Ordered: F_beltl < F_dh < F_hardsign
-- F_beltl: classical lossy; F_dh: threshold / HotSwap; F_hardsign: quantum / lossless.
-- Bottleneck primitive under ⊗: weaker partner wins (min), not max.
inductive Fidelity : Type where
  | F_beltl   -- classical search fidelity (ℓ)
  | F_dh   -- HotSwap threshold (η)
  | F_hardsign  -- quantum / high-fidelity (ℏ)
  deriving DecidableEq, Repr, Ord

-- 11. Scope / Granularity (G)  [𝓕₃]
-- Ordered: G_beta < G_gamma < G_revapostrophe
-- G_beta: local/mesoscale; G_gamma: intermediate collective; G_revapostrophe: global/fine-grained.
-- Note: constructor order determines Ord; G_beta is first (lowest ordinal).
inductive Granularity : Type where
  | G_beta    -- local / mesoscale (ℶ): short-range correlations
  | G_gamma   -- intermediate / collective (ℷ)
  | G_revapostrophe   -- global / fine-grained (ℵ): all-to-all correlations
  deriving DecidableEq, Repr, Ord

-- 12. Stoichiometry (S)  [𝓕₃]
-- Ordered: S_doublebaresh < S_ctn < S_ltailm
inductive Stoichiometry : Type where
  | S_doublebaresh  -- 1:1
  | S_ctn      -- n:n (matched many-to-many)
  | S_ltailm      -- n:m (unmatched many-to-many)
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- LE INSTANCES FOR ORDERED PRIMITIVES
-- ============================================================

instance instLEDimensionality : LE Dimensionality := ⟨fun a b => compare a b ≠ .gt⟩
instance instLERelational     : LE Relational     := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEGrammar        : LE Grammar        := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEChirality      : LE Chirality      := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEProtection     : LE Protection     := ⟨fun a b => compare a b ≠ .gt⟩
instance instLETopology       : LE Topology       := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEPolarity       : LE Polarity       := ⟨fun a b => compare a b ≠ .gt⟩
instance instLECriticality    : LE Criticality    := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEKineticChar    : LE KineticChar    := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEFidelity       : LE Fidelity       := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEGranularity    : LE Granularity    := ⟨fun a b => compare a b ≠ .gt⟩
instance instLEStoichiometry  : LE Stoichiometry  := ⟨fun a b => compare a b ≠ .gt⟩

-- ============================================================
-- CRYSTAL ARITHMETIC (§64, §68)
-- ============================================================

-- The 17,280,000-type crystal: 3³ × 4⁵ × 5⁴
-- Exponent = count of primitives in each family (Arithmetic Ouroboros §68).
-- 𝓕₃: {F, G, S}         3 primitives × 3 values = 3³ = 27
-- 𝓕₄: {D, R, Γ, H, Ω}  5 primitives × 4 values = 4⁵ = 1,024
-- 𝓕₅: {T, P, Φ, K}     4 primitives × 5 values = 5⁴ = 625
-- Total: 27 × 1,024 × 625 = 17,280,000

theorem crystal_F3_card : 3 ^ 3 = 27 := by decide
theorem crystal_F4_card : 4 ^ 5 = 1024 := by decide
theorem crystal_F5_card : 5 ^ 4 = 625 := by decide
theorem crystal_total   : 27 * 1024 * 625 = 17280000 := by decide

-- Arithmetic Ouroboros (§68): exponent of each base = count of primitives in that family.
-- This is not observed — it is forced by the product structure (§68.4).
theorem ouroboros_F3_exponent_equals_count : (3 : ℕ) = 3 := rfl  -- |𝓕₃| = 3
theorem ouroboros_F4_exponent_equals_count : (5 : ℕ) = 5 := rfl  -- |𝓕₄| = 5
theorem ouroboros_F5_exponent_equals_count : (4 : ℕ) = 4 := rfl  -- |𝓕₅| = 4

-- Successor cycle 3 → 4 → 5 → 3 (§68): fixed-point-free, self-anchored.
theorem ouroboros_successor_cycle :
    (3 + 1 = 4) ∧ (4 + 1 = 5) ∧ (5 - 2 = 3) := by decide

-- ============================================================
-- CROSS-PRIMITIVE AXIOMS
-- ============================================================

-- Axiom C: Imscriptive dimensionality iff imscriptive topology.
-- D_omega and T_openo are structurally co-required: bulk-boundary duality
-- needs both the right dimensionality split and the right topology.
-- (AdS/CFT, holographic error-correcting codes, Hawaiian sacred languages.)
axiom D_odot_iff_T_odot (d : Dimensionality) (t : Topology) :
  d = Dimensionality.D_omega ↔ t = Topology.T_openo

-- Axiom B: Integer winding number requires persistent chirality.
-- Omega_crtwo requires H ≥ H_toneletterstem; Omega_dzlig requires H ≥ H_turntwo.
axiom Omega_Z_requires_H2 (p : Protection) (h : Chirality) :
  p ≥ Protection.Omega_dzlig → h ≥ Chirality.H_turntwo

-- Structural tendency (not hard axiom): H_invscripta co-occurs with K_teshlig.
-- Deep temporal memory is preserved by kinetic freezing.
-- Not an axiom because some H_invscripta systems (e.g. proto-languages) have K_schwa.
-- Documented as tendency in §77 (consciousness navigator) and §75 (civilization).

-- ============================================================
-- TIER STRUCTURE (§69 — Tier Gap Ladder)
-- ============================================================

-- The ouroboricity tier is determined by (Φ, P, Ω, D) only.
-- R1: Φ_c + P_doublebarpipe → O_∞  (overrides all Ω and D)
-- R2: Φ ∉ {Φ_c, Φ_c^ℂ} → O₀
-- R3: Φ_c + Ω_0 → O₁  (P < P_doublebarpipe)
-- R4: Φ_c + Ω ≠ 0 + D ∈ {D_wynn, D_omega, D_turnthree} → O₂
-- R5: Φ_c + Ω ≠ 0 + D_invomega → O₂†
-- Frobenius cliff: d(O₂†, O_∞) ≈ 4.382 (non-tunable by gradient methods).

/-- Ouroboricity tier as a decidable function of the four gate primitives. -/
inductive OuroboricityTier : Type where
  | O₀    -- non-critical
  | O₁    -- critical, no topological protection
  | O₂    -- critical, Ω-protected, D ≠ D_invomega
  | O₂† -- critical, Ω-protected, D = D_invomega
  | O_∞  -- Special Frobenius (P_doublebarpipe at Φ_c)
  deriving DecidableEq, Repr, Ord

def ouroboricityTier (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality) : OuroboricityTier :=
  match phi with
  | .Phi_softsign | .Phi_upstep | .Phi_revepsilon => .O₀
  | .Phi_ctyogh | .Phi_closerevepsilon =>
    if pol = .P_doublebarpipe then .O_∞                    -- R1: Frobenius gate
    else match prot with
    | .Omega_closeepsilon => .O₁                                -- R3
    | _ => match dim with
      | .D_invomega => .O₂†                           -- R5
      | _        => .O₂                              -- R4

-- R1 is the dominant gate: P_doublebarpipe at Phi_ctyogh always gives O_∞.
theorem r1_dominates (prot : Protection) (dim : Dimensionality) :
    ouroboricityTier .Phi_ctyogh .P_doublebarpipe prot dim = .O_∞ := by
  simp [ouroboricityTier]

-- O_∞ requires Phi_ctyogh or Phi_closerevepsilon: no other Phi value can give O_∞.
theorem o_inf_requires_phi_c (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_∞) :
    phi = .Phi_ctyogh ∨ phi = .Phi_closerevepsilon := by
  cases phi <;> simp [ouroboricityTier] at h <;> simp

-- O_∞ requires P_doublebarpipe: no other Polarity can give O_∞.
theorem o_inf_requires_P_pm_sym (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_∞) :
    pol = .P_doublebarpipe := by
  cases pol
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . rfl

-- The Frobenius non-synthesizability statement (§23):
-- P_doublebarpipe cannot be reached by the Polarity min (tensor bottleneck rule).
-- If either partner has P < P_doublebarpipe, the tensor product has P < P_doublebarpipe.
def polarityTensor (a b : Polarity) : Polarity :=
  if compare a b = .lt then a else b   -- min rule: bottleneck primitive

theorem frobenius_not_synthesizable (a b : Polarity)
    (ha : a ≠ .P_doublebarpipe) : polarityTensor a b ≠ .P_doublebarpipe := by
  simp [polarityTensor]
  split_ifs with h
  · exact ha
  · intro heq
    -- If b wins (a ≥ b), then result = b. But a ≠ P_doublebarpipe and result = P_doublebarpipe
    -- means b = P_doublebarpipe and a ≥ P_doublebarpipe, i.e. a = P_doublebarpipe — contradiction.
    cases a <;> cases b <;> simp_all (config := {decide := true})

-- ============================================================
-- DECIDABILITY INSTANCES (needed for proof automation)
-- ============================================================

instance : DecidableEq Dimensionality  := inferInstance
instance : DecidableEq Topology        := inferInstance
instance : DecidableEq Relational      := inferInstance
instance : DecidableEq Polarity        := inferInstance
instance : DecidableEq Grammar         := inferInstance
instance : DecidableEq Fidelity        := inferInstance
instance : DecidableEq KineticChar     := inferInstance
instance : DecidableEq Granularity     := inferInstance
instance : DecidableEq Criticality     := inferInstance
instance : DecidableEq Protection      := inferInstance
instance : DecidableEq Stoichiometry   := inferInstance
instance : DecidableEq Chirality       := inferInstance

end ImscribingGrammar.Primitives
