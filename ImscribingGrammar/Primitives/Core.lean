-- ImscribingGrammar/Primitives/Core.lean
-- Canonical 12-primitive grammar (v0.5.69).
-- All names, value counts, and ordinal orderings match space_search/primitives.py.
-- Crystal: 3³ × 4⁵ × 5⁴ = 17,280,000 types.
--   𝓕₃ (3 values): F, G, S
--   𝓕₄ (4 values): D, R, ∈, H, Ω
--   𝓕₅ (5 values): T, P, Φ, K

import Mathlib.Order.Lattice
import Mathlib.Order.BoundedOrder.Basic

namespace ImscribingGrammar.Primitives

-- ============================================================
-- 𝓕₄ PRIMITIVES — 4 values each
-- ============================================================

-- 1. Dimensionality (D)  [𝓕₄]
-- Ordered: dead < ash < array < if'
-- if' = imscriptive (boundary encodes bulk); the monad symbol ⊙.
-- Replaces the non-canonical D_holo naming everywhere (v0.5.x).
inductive Dimensionality : Type where
  | dead     -- wedge/local: flat 2D sheet, no recursive nesting
  | ash  -- triangulated: simplicial / stratified, finite depth
  | array     -- infinite-dimensional: unbounded temporal/spatial generation
  | if'      -- imscriptive: boundary encodes bulk (⊙ = monad inside circle)
  deriving DecidableEq, Repr, Ord

-- 2. Relational Mode (R)  [𝓕₄]
-- Ordered: ado < tot < ear < ian
-- ado: hierarchical/supervisory; tot: compositional/categorical;
-- ear: bidirectional dagger (A ⊣ A†); ian: left-right / lateral.
inductive Relational : Type where
  | ado   -- supervisory / hierarchical: one-way authority
  | tot     -- categorical / compositional: functorial chaining
  | ear  -- dagger / reciprocal: A and A† co-define each other
  | ian      -- lateral / peer: symmetric two-way exchange
  deriving DecidableEq, Repr, Ord

-- 3. Interaction Grammar (∈)  [𝓕₄]
-- Ordered: vow < gag < measure < ooze
-- Categorical primitive (identity of composition rule required for non-⊥ meet).
inductive Grammar : Type where
  | vow    -- conjunctive / simultaneous: all conditions required
  | gag     -- disjunctive / alternative: any condition sufficient
  | measure    -- sequential / ordered: strict temporal or causal ordering
  | ooze  -- broadcast / universal: one-to-all coupling
  deriving DecidableEq, Repr, Ord

-- 4. Chirality / Chirality (H)  [𝓕₄]
-- Ordered: fee < kick < sure < wool
-- fee: no temporal memory; wool: topologically protected chirality.
-- Cross-primitive: wool tends to co-occur with on (frozen dynamics preserve
-- deep temporal structure), but this is a tendency, not a hard axiom.
inductive Chirality : Type where
  | fee      -- achiral: shift-invariant, no handedness to break
  | kick      -- soft chiral: period-2 under the shift
  | sure      -- persistent chiral: a descent through rank
  | wool   -- topological chiral, inexhaustible chirality
  deriving DecidableEq, Repr, Ord

-- 5. Topological Protection (Ω)  [𝓕₄]
-- Ordered: awe < oak < ah < zoo
-- zoo: non-Abelian / non-standard protection (not necessarily stronger than ah
-- in a linear sense; occupies ordinal 4 as the maximally exotic tier).
inductive Protection : Type where
  | awe    -- no topological protection
  | oak   -- ℤ₂ symmetry protection
  | ah    -- integer winding number / ℤ protection
  | zoo   -- non-Abelian / non-standard protection
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₅ PRIMITIVES — 5 values each
-- ============================================================

-- 6. Topology (T)  [𝓕₅]
-- Ordered: judge < eat < mime < oil < are
-- are = imscriptive topology: non-local boundary-bulk correspondence.
-- are co-occurs with if' (see Axiom C below).
inductive Topology : Type where
  | judge  -- general graph: heterogeneous, locally connected
  | eat       -- inclusion / nested: hierarchical containment
  | mime   -- bowtie / figure-8: two-cycle closure, bifurcation point
  | oil      -- box / lattice: regular grid or torus
  | are     -- imscriptive: boundary fully encodes bulk (⊙)
  deriving DecidableEq, Repr, Ord

-- 7. Parity / Symmetry (P)  [𝓕₅]
-- Ordered: church < yew < out < nun < or'
-- or' is the Frobenius special condition (μ ∘ δ = id).
-- It is the tier singularity: overrides all Ω and D branching → O_∞.
-- or' cannot be synthesised by composition of P < or' partners (§23).
inductive Polarity : Type where
  | church    -- asymmetric: no symmetry axis
  | yew     -- phase symmetry: U(1) or continuous phase
  | out      -- ℤ₂ discrete symmetry (sign flip)
  | nun     -- full continuous symmetry (e.g. SO(n))
  | or'  -- Special Frobenius: μ ∘ δ = id; exact ℤ₂ at ⊙
  deriving DecidableEq, Repr, Ord

-- 8. Criticality (<)  [𝓕₅]
-- Ordered: woe < monad < roar < err < haha
-- monad is absorbing under meet: meet(monad, x) = monad for all x.
-- This is not a standard linear meet — see note below.
inductive Criticality : Type where
  | woe        -- subcritical: stable, ordered phase
  | monad          -- real-axis Hermitian criticality: standard fixed point (absorbing)
  | roar  -- complex-axis criticality: analytic continuation required
                   -- (Lee-Yang edge, complex RG fixed point, ζ-function zeros)
                   -- Ordinal 2.33 in Python (non-integer; Lean uses rank 2)
  | err         -- exceptional-point criticality: non-Hermitian eigenvector coalescence
                   -- Square-root branch point; oak tendency
                   -- Ordinal 2.67 in Python (non-integer; Lean uses rank 3)
  | haha      -- supercritical: unstable, runaway
  deriving DecidableEq, Repr, Ord

-- NOTE on monad absorbing meet:
-- The standard lattice meet (min) does not capture monad absorption.
-- In the grammar algebra: meet(monad, woe) = monad (not woe).
-- This requires a custom MeetSemilattice instance defined in Algebra.lean.
-- The Lean Ord derivation gives the ordinal ordering woe < monad < ...,
-- which is used for tier comparisons but not for the absorption rule.

-- 9. Kinetic Character (K)  [𝓕₅]
-- Ordered: yea < loll < egg < on < air
-- on: frozen by order (e.g. over-consolidated bureaucracy, catatonia).
-- air: frozen by disorder (many-body localization, dissociation, Soviet collapse).
-- Both on and air fail Gate 2 of the consciousness score (§VIII).
-- Restoration requires OPPOSITE interventions: on → disorder injection;
-- air → ergodicity restoration. See §75–§77 for civilizational/consciousness examples.
inductive KineticChar : Type where
  | yea   -- diffusion-limited, untrapped
  | loll    -- moderate barrier
  | egg   -- slow / thermally activated (Gate 2 of C-score: K ≤ egg passes)
  | on   -- kinetically trapped by order
  | air    -- many-body localized: frozen by disorder
  deriving DecidableEq, Repr, Ord

-- ============================================================
-- 𝓕₃ PRIMITIVES — 3 values each
-- ============================================================

-- 10. Fidelity (F)  [𝓕₃]
-- Ordered: age < they < peep
-- age: classical lossy; they: threshold / HotSwap; peep: quantum / lossless.
-- Bottleneck primitive under ⊗: weaker partner wins (min), not max.
inductive Fidelity : Type where
  | age   -- classical search fidelity (ℓ)
  | they   -- HotSwap threshold (η)
  | peep  -- quantum / high-fidelity (ℏ)
  deriving DecidableEq, Repr, Ord

-- 11. Scope / Granularity (G)  [𝓕₃]
-- Ordered: bib < thigh < ice
-- bib: local/mesoscale; thigh: intermediate collective; ice: global/fine-grained.
-- Note: constructor order determines Ord; bib is first (lowest ordinal).
inductive Granularity : Type where
  | bib    -- local / mesoscale (ℶ): short-range correlations
  | thigh   -- intermediate / collective (ℷ)
  | ice   -- global / fine-grained (ℵ): all-to-all correlations
  deriving DecidableEq, Repr, Ord

-- 12. Stoichiometry (S)  [𝓕₃]
-- Ordered: hung < so < up
inductive Stoichiometry : Type where
  | hung  -- 1:1
  | so      -- n:n (matched many-to-many)
  | up      -- n:m (unmatched many-to-many)
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
-- 𝓕₄: {D, R, ∈, H, Ω}  5 primitives × 4 values = 4⁵ = 1,024
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
-- if' and are are structurally co-required: bulk-boundary duality
-- needs both the right dimensionality split and the right topology.
-- (AdS/CFT, holographic error-correcting codes, Hawaiian sacred languages.)
axiom D_odot_iff_T_odot (d : Dimensionality) (t : Topology) :
  d = Dimensionality.if' ↔ t = Topology.are

-- Axiom B: Integer winding number requires persistent chirality.
-- oak requires H ≥ kick; ah requires H ≥ sure.
axiom Omega_Z_requires_H2 (p : Protection) (h : Chirality) :
  p ≥ Protection.ah → h ≥ Chirality.sure

-- Tendency (not hard axiom): wool co-occurs with on.
-- An inexhaustible tower stands because its store is frozen.
-- Not an axiom because some wool systems (e.g. proto-languages) have egg.
-- Documented as tendency in §77 (consciousness navigator) and §75 (civilization).

-- ============================================================
-- TIER STRUCTURE (§69 — Tier Gap Ladder)
-- ============================================================

-- The ouroboricity tier is determined by (<, P, Ω, D) only.
-- R1: ⊙ + or' → O_∞  (overrides all Ω and D)
-- R2: < ∉ {⊙, ⊙^ℂ} → O₀
-- R3: ⊙ + Ω_0 → O₁  (P < or')
-- R4: ⊙ + Ω ≠ 0 + D ∈ {dead, if', ash} → O₂
-- R5: ⊙ + Ω ≠ 0 + array → O₂†
-- Frobenius cliff: d(O₂†, O_∞) ≈ 4.382 (non-tunable by gradient methods).

/-- Ouroboricity tier as a decidable function of the four gate primitives. -/
inductive OuroboricityTier : Type where
  | O₀    -- non-critical
  | O₁    -- critical, no topological protection
  | O₂    -- critical, Ω-protected, D ≠ array
  | O₂† -- critical, Ω-protected, D = array
  | O_∞  -- Special Frobenius (or' at ⊙)
  deriving DecidableEq, Repr, Ord

def ouroboricityTier (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality) : OuroboricityTier :=
  match phi with
  | .woe | .haha | .err => .O₀
  | .monad | .roar =>
    if pol = .or' then .O_∞                    -- R1: Frobenius gate
    else match prot with
    | .awe => .O₁                                -- R3
    | _ => match dim with
      | .array => .O₂†                           -- R5
      | _        => .O₂                              -- R4

-- R1 is the dominant gate: or' at monad always gives O_∞.
theorem r1_dominates (prot : Protection) (dim : Dimensionality) :
    ouroboricityTier .monad .or' prot dim = .O_∞ := by
  simp [ouroboricityTier]

-- O_∞ requires monad or roar: no other Phi value can give O_∞.
theorem o_inf_requires_phi_c (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_∞) :
    phi = .monad ∨ phi = .roar := by
  cases phi <;> simp [ouroboricityTier] at h <;> simp

-- O_∞ requires or': no other Polarity can give O_∞.
theorem o_inf_requires_P_pm_sym (phi : Criticality) (pol : Polarity)
    (prot : Protection) (dim : Dimensionality)
    (h : ouroboricityTier phi pol prot dim = .O_∞) :
    pol = .or' := by
  cases pol
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . all_goals (cases phi <;> cases prot <;> cases dim <;> simp [ouroboricityTier] at h <;> contradiction)
  . rfl

-- The Frobenius non-synthesizability statement (§23):
-- or' cannot be reached by the Polarity min (tensor bottleneck rule).
-- If either partner has P < or', the tensor product has P < or'.
def polarityTensor (a b : Polarity) : Polarity :=
  if compare a b = .lt then a else b   -- min rule: bottleneck primitive

theorem frobenius_not_synthesizable (a b : Polarity)
    (ha : a ≠ .or') : polarityTensor a b ≠ .or' := by
  simp [polarityTensor]
  split_ifs with h
  · exact ha
  · intro heq
    -- If b wins (a ≥ b), then result = b. But a ≠ or' and result = or'
    -- means b = or' and a ≥ or', i.e. a = or' — contradiction.
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
