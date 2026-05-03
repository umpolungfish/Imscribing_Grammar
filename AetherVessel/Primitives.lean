/- 
  AetherVessel: The Imscribing Grammar (IG) in Lean4
  Implements the 12-primitive structural type system, the crystal of 17.28M types,
  and the dual proof that G₂ is the perfect vessel for E₈.
-/

import Lean
import Std

-- ============================================================
-- PRIMITIVE TYPES (§8 of Aether_Vessel.md)
-- ============================================================

inductive Dimensionality where
  | D_wedge    -- point (0d)
  | D_triangle -- bounded surface (2d)
  | D_infty    -- infinite-dimensional / field-theoretic
  | D_odot     -- imscriptive (self-written state space)
  deriving BEq, Repr, Ord, Inhabited

inductive Topology where
  | T_network  -- branching (tree-like)
  | T_in       -- containment (inclusion)
  | T_bowtie   -- crossing point
  | T_boxtimes -- irreducible product (box product)
  | T_odot     -- imscriptive closure (self-referential)
  deriving BEq, Repr, Ord, Inhabited

inductive RelMode where
  | R_super    -- supervenience
  | R_cat      -- categorical / functorial
  | R_dagger   -- adjoint pair (one-way)
  | R_lr       -- bidirectional feedback coupling
  deriving BEq, Repr, Ord, Inhabited

inductive Parity where
  | P_asym     -- none
  | P_psi      -- quantum superposition
  | P_pm       -- one Z₂ symmetry
  | P_sym      -- full symmetry, all unbroken
  | P_pm_sym   -- Frobenius-special: μ ∘ δ = id exactly at Φ_c
  deriving BEq, Repr, Ord, Inhabited

inductive Fidelity where
  | F_ell  -- classical (no coherence)
  | F_eth  -- thermal / noisy
  | F_hbar -- quantum coherence essential
  deriving BEq, Repr, Ord, Inhabited

inductive Kinetics where
  | K_fast -- τ ≪ T, driven
  | K_mod  -- τ ∼ T, moderate
  | K_slow -- τ ≫ T, near-equilibrium
  | K_trap -- frozen order (K_trap)
  | K_MBL  -- frozen disorder (many-body localized)
  deriving BEq, Repr, Ord, Inhabited

inductive Scope where
  | G_beth  -- local / nearest-neighbor
  | G_gimel -- intermediate / mesoscale
  | G_aleph -- universal / maximal
  deriving BEq, Repr, Ord, Inhabited

inductive InteractionGrammar where
  | And    -- Γ_∧ : conjunctive (all simultaneously)
  | Or     -- Γ_∨ : disjunctive (alternative paths)
  | Seq    -- Γ_seq : sequential (ordered steps)
  | Broad  -- Γ_brd : broadcast (one-to-all)
  deriving BEq, Repr, Ord, Inhabited

inductive Criticality where
  | Phi_sub     -- subcritical, no scaling
  | Phi_c       -- exactly critical (power-law divergence)
  | Phi_c_complex -- complex-plane critical
  | Phi_EP      -- exceptional point (non-Hermitian degeneracy)
  | Phi_super   -- supercritical / runaway / chaotic
  deriving BEq, Repr, Ord, Inhabited

inductive TemporalDepth where
  | H0    -- memoryless (Markov order 0)
  | H1    -- one-step memory
  | H2    -- two-step memory
  | H_inf -- unbounded / eternal memory (requires K_trap)
  deriving BEq, Repr, Ord, Inhabited

inductive Stoichiometry where
  | one_one -- 1:1 single type, single instance
  | n_n     -- n:n many identical components
  | n_m     -- n:m multiple distinct types
  deriving BEq, Repr, Ord, Inhabited

inductive Winding where
  | Omega_0  -- trivial
  | Omega_Z2 -- Z₂ parity-protected
  | Omega_Z  -- integer winding (topological)
  | Omega_NA -- non-Abelian braiding (requires D_odot)
  deriving BEq, Repr, Ord, Inhabited