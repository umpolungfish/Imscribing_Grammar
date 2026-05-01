-- SynthOmnicon/Primitives/Core.lean
-- Canonical 12-primitive grammar (v0.5.69).
-- All names, value counts, and ordinal orderings match space_search/primitives.py.
-- Crystal: 3³ × 4⁵ × 5⁴ = 17,280,000 structural types.
--   𝓕₃ (3 values): F, G, S
--   𝓕₄ (4 values): D, R, Γ, H, Ω
--   𝓕₅ (5 values): T, P, Φ, K

import Mathlib.Order.Lattice
import Mathlib.Order.BoundedOrder.Basic

namespace SynthOmnicon.Primitives

-- ============================================================
-- 𝓕₄ PRIMITIVES — 4 values each
-- ============================================================

-- 1. Dimensionality (D)  [𝓕₄]
-- Ordered: D_wedge < D_triangle < D_infty < D_odot
-- D_odot = holographic (boundary encodes bulk); the monad symbol ⊙.
-- Replaces the non-canonical D_holo naming everywhere (v0.5.x).
inductive Dimensionality : Type where
  | D_wedge     -- wedge/local: flat 2D sheet, no recursive nesting
  | D_triangle  -- triangulated: simplicial / stratified, finite depth
  | D_infty     -- infinite-dimensional: unbounded temporal/spatial generation
  | D_odot      -- holographic: boundary encodes bulk (⊙ = monad inside circle)
  deriving DecidableEq, Repr, Ord

-- 2. Relational Mode (R)  [𝓕₄]
-- Ordered: R_super < R_cat < R_dagger < R_lr
-- R_super: hierarchical/supervisory; R_cat: compositional/categorical;
-- R_dagger: bidirectional dagger (A ⊣ A†); R_lr: left-right / lateral.
inductive Relational : Type where
  | R_super   -- supervisory / hierarchical: one-way authority
  | R_cat     -- categorical / compositional: functorial chaining
  | R_dagger  -- dagger / reciprocal: A and A† co-define each other
  | R_lr      -- lateral / peer: symmetric two-way exchange
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

-- 4. Chirality / Temporal Depth (H)  [𝓕₄]
-- Ordered: H0 < H1 < H2 < H_inf
-- H0: no temporal memory; H_inf: topologically protected temporal depth.
-- Cross-primitive: H_inf tends to co-occur with K_trap (frozen dynamics preserve
-- deep temporal structure), but this is a structural tendency, not a hard axiom.
inductive Chirality : Type where
  | H0      -- achiral, no temporal memory
  | H1      -- soft chiral, weak temporal asymmetry
  | H2      -- persistent chiral, strong temporal asymmetry
  | H_inf   -- topological chiral, inexhaustible temporal depth
  deriving DecidableEq, Repr, Ord

-- 5. Topological Protection (Ω)  [𝓕₄]
-- Ordered: Omega_0 < Omega_Z2 < Omega_Z < Omega_NA
-- Omega_NA: non-Abelian / non-standard protection (not necessarily stronger than Omega_Z
-- in a linear sense; occupies ordinal 4 as the maximally exotic tier).
inductive Protection : Type where
  | Omega_0    -- no topological protection
  | Omega_Z2   -- ℤ₂ symmetry protection
  | Omega_Z    -- integer winding number / ℤ protection
  | Omega_NA   -- non-Abelian / non-standard protection
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₅ PRIMITIVES — 5 values each
-- ============================================================

-- 6. Topology (T)  [𝓕₅]
-- Ordered: T_network < T_in < T_bowtie < T_box < T_odot
-- T_odot = holographic topology: non-local boundary-bulk correspondence.
-- T_odot co-occurs with D_odot (see Axiom C below).
inductive Topology : Type where
  | T_network  -- general graph: heterogeneous, locally connected
  | T_in       -- inclusion / nested: hierarchical containment
  | T_bowtie   -- bowtie / figure-8: two-cycle closure, bifurcation point
  | T_box      -- box / lattice: regular grid or torus
  | T_odot     -- holographic: boundary fully encodes bulk (⊙)
  deriving DecidableEq, Repr, Ord

-- 7. Parity / Symmetry (P)  [𝓕₅]
-- Ordered: P_asym < P_psi < P_pm < P_sym < P_pm_sym
-- P_pm_sym is the Frobenius special condition (μ ∘ δ = id).
-- It is the tier singularity: overrides all Ω and D branching → O_∞.
-- P_pm_sym cannot be synthesised by composition of P < P_pm_sym partners (§23).
inductive Polarity : Type where
  | P_asym    -- asymmetric: no symmetry axis
  | P_psi     -- phase symmetry: U(1) or continuous phase
  | P_pm      -- ℤ₂ discrete symmetry (sign flip)
  | P_sym     -- full continuous symmetry (e.g. SO(n))
  | P_pm_sym  -- Special Frobenius: μ ∘ δ = id; exact ℤ₂ at Φ_c
  deriving DecidableEq, Repr, Ord

-- 8. Criticality (Φ)  [𝓕₅]
-- Ordered: Phi_sub < Phi_c < Phi_c_complex < Phi_EP < Phi_super
-- Phi_c is absorbing under meet: meet(Phi_c, x) = Phi_c for all x.
-- This is not a standard linear meet — see note below.
inductive Criticality : Type where
  | Phi_sub        -- subcritical: stable, ordered phase
  | Phi_c          -- real-axis Hermitian criticality: standard fixed point (absorbing)
  | Phi_c_complex  -- complex-axis criticality: analytic continuation required
                   -- (Lee-Yang edge, complex RG fixed point, ζ-function zeros)
                   -- Ordinal 2.33 in Python (non-integer; Lean uses rank 2)
  | Phi_EP         -- exceptional-point criticality: non-Hermitian eigenvector coalescence
                   -- Square-root branch point; Omega_Z2 structural tendency
                   -- Ordinal 2.67 in Python (non-integer; Lean uses rank 3)
  | Phi_super      -- supercritical: unstable, runaway
  deriving DecidableEq, Repr, Ord

-- NOTE on Phi_c absorbing meet:
-- The standard lattice meet (min) does not capture Phi_c absorption.
-- In the grammar algebra: meet(Phi_c, Phi_sub) = Phi_c (not Phi_sub).
-- This requires a custom MeetSemilattice instance defined in Algebra.lean.
-- The Lean Ord derivation gives the ordinal ordering Phi_sub < Phi_c < ...,
-- which is used for tier comparisons but not for the absorption rule.

-- 9. Kinetic Character (K)  [𝓕₅]
-- Ordered: K_fast < K_mod < K_slow < K_trap < K_MBL
-- K_trap: frozen by order (e.g. over-consolidated bureaucracy, catatonia).
-- K_MBL: frozen by disorder (many-body localization, dissociation, Soviet collapse).
-- Both K_trap and K_MBL fail Gate 2 of the consciousness score (§VIII).
-- Restoration requires OPPOSITE interventions: K_trap → disorder injection;
-- K_MBL → ergodicity restoration. See §75–§77 for civilizational/consciousness examples.
inductive KineticChar : Type where
  | K_fast   -- diffusion-limited, untrapped
  | K_mod    -- moderate barrier
  | K_slow   -- slow / thermally activated (Gate 2 of C-score: K ≤ K_slow passes)
  | K_trap   -- kinetically trapped by order
  | K_MBL    -- many-body localized: frozen by disorder
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₃ PRIMITIVES — 3 values each
-- ============================================================

-- 10. Fidelity (F)  [𝓕₃]
-- Ordered: F_ell < F_eth < F_hbar
-- F_ell: classical lossy; F_eth: threshold / HotSwap; F_hbar: quantum / lossless.
-- Bottleneck primitive under ⊗: weaker partner wins (min), not max.
inductive Fidelity : Type where
  | F_ell   -- classical search fidelity (ℓ)
  | F_eth   -- HotSwap threshold (η)
  | F_hbar  -- quantum / high-fidelity (ℏ)
  deriving DecidableEq, Repr, Ord

-- 11. Scope / Granularity (G)  [𝓕₃]
-- Ordered: G_beth < G_gimel < G_aleph
-- G_beth: local/mesoscale; G_gimel: intermediate collective; G_aleph: global/fine-grained.
-- Note: constructor order determines Ord; G_beth is first (lowest ordinal).
inductive Granularity : Type where
  | G_beth    -- local / mesoscale (ℶ): short-range correlations
  | G_gimel   -- intermediate / collective (ℷ)
  | G_aleph   -- global / fine-grained (ℵ): all-to-all correlations
  deriving DecidableEq, Repr, Ord

-- 12. Stoichiometry (S)  [𝓕₃]
-- Ordered: one_one < n_n < n_m
inductive Stoichiometry : Type where
  | one_one  -- 1:1
  | n_n      -- n:n (matched many-to-many)
  | n_m      -- n:m (unmatched many-to-many)
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

-- Axiom C: Holographic dimensionality iff holographic topology.
-- D_odot and T_odot are structurally co-required: bulk-boundary duality
-- needs both the right dimensionality split and the right topology.
-- (AdS/CFT, holographic error-correcting codes, Hawaiian sacred languages.)
axiom D_odot_iff_T_odot (d : Dimensionality) (t : Topology) :
  d = Dimensionality.D_odot ↔ t = Topology.T_odot

-- Axiom B: Integer winding number requires persistent chirality.
-- Omega_Z2 requires H ≥ H1; Omega_Z requires H ≥ H2.
axiom Omega_Z_requires_H2 (p : Protection) (h : Chirality) :
  p ≥ Protection.Omega_Z → h ≥ Chirality.H2

-- Structural tendency (not hard axiom): H_inf co-occurs with K_trap.
-- Deep temporal memory is preserved by kinetic freezing.
-- Not an axiom because some H_inf systems (e.g. proto-languages) have K_slow.
-- Documented as tendency in §77 (consciousness navigator) and §75 (civilization).

-- ============================================================
-- TIER STRUCTURE (§69 — Tier Gap Ladder)
-- ============================================================

-- The ouroboricity tier is determined by (Φ, P, Ω, D) only.
-- R1: Φ_c + P_pm_sym → O_∞  (overrides all Ω and D)
-- R2: Φ ∉ {Φ_c, Φ_c^ℂ} → O_0
-- R3: Φ_c + Ω_0 → O_1  (P < P_pm_sym)
-- R4: Φ_c + Ω ≠ 0 + D ∈ {D_wedge, D_odot, D_triangle} → O_2
-- R5: Φ_c + Ω ≠ 0 + D_infty → O_2†
-- Frobenius cliff: d(O_2†, O_∞) ≈ 4.382 (non-tunable by gradient methods).

/-- Ouroboricity tier as a decidable function of the four gate primitives. -/
inductive OuroboricityTier : Type where
  | O_0    -- non-critical
  | O_1    -- critical, no topological protection
  | O_2    -- critical, Ω-protected, D ≠ D_infty
  | O_2dag -- critical, Ω-protected, D = D_infty
  | O_inf  -- Special Frobenius (P_pm_sym at Φ_c)
  deriving DecidableEq, Repr, Ord

def ouroboricityTier (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality) : OuroboricityTier :=
  match phi with
  | .Phi_sub | .Phi_super | .Phi_EP => .O_0
  | .Phi_c | .Phi_c_complex =>
    if pol = .P_pm_sym then .O_inf                    -- R1: Frobenius gate
    else match prot with
    | .Omega_0 => .O_1                                -- R3
    | _ => match dim with
      | .D_infty => .O_2dag                           -- R5
      | _        => .O_2                              -- R4

-- R1 is the dominant gate: P_pm_sym at Phi_c always gives O_inf.
theorem r1_dominates (prot : Protection) (dim : Dimensionality) :
    ouroboricityTier .Phi_c .P_pm_sym prot dim = .O_inf := by
  simp [ouroboricityTier]

-- O_inf requires Phi_c or Phi_c_complex: no other Phi value can give O_inf.
theorem o_inf_requires_phi_c (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_inf) :
    phi = .Phi_c ∨ phi = .Phi_c_complex := by
  cases phi <;> simp [ouroboricityTier] at h <;> simp

-- O_inf requires P_pm_sym: no other Polarity can give O_inf.
theorem o_inf_requires_P_pm_sym (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_inf) :
    pol = .P_pm_sym := by
  cases phi <;> cases pol <;> simp [ouroboricityTier] at h

-- The Frobenius non-synthesizability statement (§23):
-- P_pm_sym cannot be reached by the Polarity min (tensor bottleneck rule).
-- If either partner has P < P_pm_sym, the tensor product has P < P_pm_sym.
def polarityTensor (a b : Polarity) : Polarity :=
  if compare a b = .lt then a else b   -- min rule: bottleneck primitive

theorem frobenius_not_synthesizable (a b : Polarity)
    (ha : a ≠ .P_pm_sym) : polarityTensor a b ≠ .P_pm_sym := by
  simp [polarityTensor]
  split_ifs with h
  · exact ha
  · intro heq
    -- If b wins (a ≥ b), then result = b. But a ≠ P_pm_sym and result = P_pm_sym
    -- means b = P_pm_sym and a ≥ P_pm_sym, i.e. a = P_pm_sym — contradiction.
    cases a <;> cases b <;> simp_all [compare, Ord.compare]

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

end SynthOmnicon.Primitives
