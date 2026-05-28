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
  | D_wynn    -- point (0d)
  | D_turnthree -- bounded surface (2d)
  | D_invomega    -- infinite-dimensional / field-theoretic
  | D_omega     -- imscriptive (self-written state space)
  deriving BEq, Repr, Ord, Inhabited

inductive Topology where
  | T_nrleg  -- branching (tree-like)
  | T_invscr       -- containment (inclusion)
  | T_bullseye   -- crossing point
  | T_commatailz -- irreducible product (box product)
  | T_openo     -- imscriptive closure (self-referential)
  deriving BEq, Repr, Ord, Inhabited

inductive RelMode where
  | R_subrightarrow    -- supervenience
  | R_ctz      -- categorical / functorial
  | R_downstep   -- adjoint pair (one-way)
  | R_lyoghlig       -- bidirectional feedback coupling
  deriving BEq, Repr, Ord, Inhabited

inductive Parity where
  | P_aolig     -- none
  | P_upsilon      -- quantum superposition
  | P_pipevar       -- one Z₂ symmetry
  | P_subdoublearrow      -- full symmetry, all unbroken
  | P_doublebarpipe   -- Frobenius-special: μ ∘ δ = id exactly at Φ_c
  deriving BEq, Repr, Ord, Inhabited

inductive Fidelity where
  | F_beltl  -- classical (no coherence)
  | F_dh  -- thermal / noisy
  | F_hardsign -- quantum coherence essential
  deriving BEq, Repr, Ord, Inhabited

inductive Kinetics where
  | K_frtailgamma -- τ ≪ T, driven
  | K_turnm  -- τ ∼ T, moderate
  | K_schwa -- τ ≫ T, near-equilibrium
  | K_teshlig -- frozen order (K_teshlig)
  | K_lambda  -- frozen disorder (many-body localized)
  deriving BEq, Repr, Ord, Inhabited

inductive Scope where
  | G_beta  -- local / nearest-neighbor
  | G_gamma -- intermediate / mesoscale
  | G_revapostrophe -- universal / maximal
  deriving BEq, Repr, Ord, Inhabited

inductive InteractionGrammar where
  | And    -- Γ_∧ : conjunctive (all simultaneously)
  | Or     -- Γ_∨ : disjunctive (alternative paths)
  | Seq    -- Γ_seq : sequential (ordered steps)
  | Broad  -- Γ_brd : broadcast (one-to-all)
  deriving BEq, Repr, Ord, Inhabited

inductive Criticality where
  | Phi_softsign     -- subcritical, no scaling
  | Phi_ctyogh       -- exactly critical (power-law divergence)
  | Phi_closerevepsilon -- complex-plane critical
  | Phi_revepsilon      -- exceptional point (non-Hermitian degeneracy)
  | Phi_upstep   -- supercritical / runaway / chaotic
  deriving BEq, Repr, Ord, Inhabited

inductive TemporalDepth where
  | H_closeomega    -- memoryless (Markov order 0)
  | H_toneletterstem    -- one-step memory
  | H_turntwo    -- two-step memory
  | H_invscripta -- unbounded / eternal memory (requires K_teshlig)
  deriving BEq, Repr, Ord, Inhabited

inductive Stoichiometry where
  | S_doublebaresh -- 1:1 single type, single instance
  | S_ctn     -- n:n many identical components
  | S_ltailm     -- n:m multiple distinct types
  deriving BEq, Repr, Ord, Inhabited

inductive Winding where
  | Omega_closeepsilon  -- trivial
  | Omega_crtwo -- Z₂ parity-protected
  | Omega_dzlig  -- integer winding (topological)
  | Omega_turna -- non-Abelian braiding (requires D_omega)
  deriving BEq, Repr, Ord, Inhabited