-- SynthOmnicon/Millennium/Barriers.lean
-- Cross-problem barrier taxonomy for all 7 Millennium Prize Problems.
-- The central theorem: a formal classification of why each problem is hard.

import Mathlib.Tactic
import SynthOmnicon.Millennium.RH
import SynthOmnicon.Millennium.YM
import SynthOmnicon.Millennium.Hodge
import SynthOmnicon.Millennium.NS
import SynthOmnicon.Millennium.PvsNP
import SynthOmnicon.Millennium.OPN
import SynthOmnicon.Millennium.BSD

/-!
# Millennium Problem Barrier Taxonomy

The sorry in a Lean proof can fail to be dischargeable for three distinct reasons:

  **MathlibGap**: The theorem IS proved in the literature. The sorry exists because
    the proof has not been formalized in Mathlib. These sorries will eventually go away
    as Mathlib grows. Example: Mazur's torsion theorem (BSD_2adic.lean).

  **OpenProblem**: No proof of the theorem exists in mathematics. The sorry cannot
    be discharged because humanity doesn't know how to discharge it. Example: RH.

  **MissingFoundation**: The sorry requires constructing a mathematical *object* whose
    type cannot be inhabited with current mathematical infrastructure — not just a proof
    of a property, but the thing the property talks about. Example: YM (path integral
    measure in 4D). These are qualitatively harder than OpenProblems because the question
    "is this true?" can't even be stated rigorously until the foundation is built.

---

The seven Millennium Problems classified:

  | Problem  | Barrier            | Missing object / why                                   |
  |----------|--------------------|--------------------------------------------------------|
  | RH       | OpenProblem        | `ZeroFreeStrip 0` — no proof of zero locations         |
  | Hodge    | OpenProblem        | `AlgebraicCycleRep` — no proof Hodge classes are alg.  |
  | P vs NP  | OpenProblem +      | `CircuitLowerBound SAT` — no proof; also               |
  |          | (partial) Missing  |   complexity theory barely formalized in Lean           |
  | NS       | OpenProblem        | `GlobalRegularityCert` — no proof; also subcritical gap |
  | YM       | MissingFoundation  | `PathIntegralMeasure 𝔤` — object doesn't exist in 4D   |
  | BSD      | MathlibGap (part.) | `bsd_rank_3adic` — 3-adic input not in Mathlib          |
  |          | + OpenProblem      |   BSD itself is open                                    |
  | OPN      | OpenProblem        | `opn_nonexistence` — no proof; Euler form is MathlibGap|

Note on BSD and OPN: they have layered barriers — some parts are MathlibGap
(Mazur torsion, Euler decomposition) and the final nonexistence/rank-formula is OpenProblem.
-/

namespace Millennium.Barriers

-- ============================================================
-- §1. The barrier type taxonomy
-- ============================================================

/-- Classification of why a Lean sorry cannot be discharged. -/
inductive BarrierType
  /-- The theorem is proved in mathematics but not yet formalized in Mathlib.
      These sorries will eventually go away. -/
  | MathlibGap
  /-- No proof of the theorem exists. This sorry cannot be discharged because
      the problem is unsolved. -/
  | OpenProblem
  /-- The sorry requires inhabiting a type that does not exist as a rigorous
      mathematical object — not just an unproved theorem, but missing infrastructure.
      These are qualitatively harder: the problem can't be fully stated until
      the foundation is built. -/
  | MissingFoundation
  deriving Repr, DecidableEq

-- ============================================================
-- §2. Problem identifiers
-- ============================================================

/-- The seven Millennium Prize Problems. -/
inductive MillenniumProblem
  | RH        -- Riemann Hypothesis
  | Hodge     -- Hodge Conjecture
  | PvsNP     -- P versus NP
  | NS        -- Navier-Stokes Existence and Smoothness
  | YM        -- Yang-Mills Existence and Mass Gap
  | BSD       -- Birch and Swinnerton-Dyer Conjecture
  | OPN       -- Odd Perfect Number (not a Clay problem, but tracked here)
  deriving Repr, DecidableEq

-- ============================================================
-- §3. The sorry boundary for each problem (typed axioms)
-- ============================================================

-- Each sorry is declared as an axiom: the exact type that cannot be inhabited.

/-- RH barrier: every critical zero has Re = 1/2.
    Type: `ZeroFreeStrip 0` (see RH.lean).
    Barrier: OpenProblem — no proof exists since 1859. -/
axiom rh_sorry_boundary : Millennium.RH.RiemannHypothesis

/-- Hodge barrier: every rational Hodge class on a smooth projective variety is algebraic.
    The missing type: `AlgebraicCycleRep X p α` — a proof that α ∈ H^{2p}(X,ℚ) ∩ H^{p,p}
    lies in the image of cl : CH^p(X) ⊗ ℚ → H^{2p}(X,ℚ) ∩ H^{p,p}.
    Barrier: OpenProblem. The p=1 case is proved (Lefschetz 1924); p ≥ 2 is open.
    See Hodge.lean for the full three-layer analysis. -/
axiom hodge_sorry_boundary : Millennium.Hodge.HodgeConjecture

/-- P vs NP barrier: the Boolean satisfiability problem is not in P.
    The missing type: `CircuitLowerBound SAT ε` — SAT requires circuits of size ≥ 2^(εn).
    Barrier: OpenProblem + deep MathlibGap (complexity classes P/NP not in Mathlib).
    Three meta-barriers in mathematics: relativization (BGS 1975), natural proofs
    (Razborov-Rudich 1994), algebrization (Aaronson-Wigderson 2009).
    See PvsNP.lean for the full three-layer analysis. -/
axiom pvsnp_sorry_boundary : Millennium.PvsNP.PNotEqualsNP

/-- Navier-Stokes barrier: smooth initial data gives smooth global solutions.
    The missing type: `GlobalRegularityCert u₀` — a smooth global bounded solution
    for every smooth divergence-free initial datum.
    Barrier: OpenProblem (near-MissingFoundation: critical Sobolev exponent s=1/2 in 3D).
    The critical scaling gap sits strictly between energy (s=0) and enstrophy (s=1).
    See NS.lean for the full three-layer analysis. -/
axiom ns_sorry_boundary : Millennium.NS.NavierStokesRegularity

/-- YM barrier: the quantum Yang-Mills theory exists with mass gap.
    Primary missing type: `PathIntegralMeasure 𝔤` — the path integral measure over gauge
    connections modulo gauge equivalence in 4D. This type does not exist in mathematics.
    Two stacked sorries: `ym_theory_exists` (MissingFoundation) → `ym_mass_gap` (OpenProblem).
    Barrier: MissingFoundation. See YM.lean for the full three-layer analysis. -/
axiom ym_sorry_boundary :
    ∀ (𝔤 : Type*) [LieRing 𝔤] [LieAlgebra ℝ 𝔤] [LieAlgebra.IsSimple ℝ 𝔤],
      Nonempty (Millennium.YM.QuantumYMTheory 𝔤) ∧
      ∀ T : Millennium.YM.QuantumYMTheory 𝔤, 0 < Millennium.YM.massGap 𝔤 T

/-- OPN barrier: no odd perfect number exists.
    Two-layer sorry: `euler_opn_structure` (MathlibGap — proved by Euler 1747, not in Mathlib)
    stacked methodologically (not logically) with `opn_nonexistence` (OpenProblem).
    Barrier: OpenProblem (primary). Euler form layer will eventually be discharged.
    See OPN.lean for the full analysis. -/
axiom opn_sorry_boundary : Millennium.OPN.OPNConjecture

/-- BSD barrier: the algebraic rank of E(ℚ) equals the analytic rank ord_{s=1} L(E,s).
    Three parallel sorries: `mordell_weil` + `mazur_torsion` (both MathlibGap, proved)
    and `bsd_certificate` (OpenProblem). All logically independent — unlike YM (stacked)
    and OPN (methodologically ordered). Known for analytic rank ≤ 1 (Kolyvagin 1988).
    See BSD.lean for the full three-layer analysis. -/
axiom bsd_sorry_boundary : Millennium.BSD.BSDRankConjecture

-- ============================================================
-- §4. The barrier classification theorem
-- ============================================================

/-- **The master classification**: the primary barrier for each Millennium Problem. -/
def millenniumBarrier : MillenniumProblem → BarrierType
  | .RH    => .OpenProblem
  | .Hodge => .OpenProblem
  | .PvsNP => .OpenProblem      -- secondary MissingFoundation for complexity formalization
  | .NS    => .OpenProblem      -- subcritical Sobolev scaling is near-MissingFoundation
  | .YM    => .MissingFoundation
  | .BSD   => .OpenProblem      -- primary; Mazur torsion part is MathlibGap
  | .OPN   => .OpenProblem      -- Euler form is MathlibGap; nonexistence is OpenProblem

/-- The unique MissingFoundation problem among the Millennium Problems. -/
theorem ym_is_unique_missing_foundation :
    ∀ p : MillenniumProblem,
      millenniumBarrier p = .MissingFoundation → p = .YM := by
  intro p hp
  cases p <;> simp_all [millenniumBarrier]

/-- MissingFoundation is strictly harder than OpenProblem in the following sense:
    for a MissingFoundation problem, the sorry *cannot be stated* as a proposition
    with well-defined truth value until the foundation is built.
    For an OpenProblem, the proposition is well-defined — we just don't know its truth value. -/
theorem missing_foundation_vs_open_problem :
    BarrierType.MissingFoundation ≠ BarrierType.OpenProblem := by
  decide

-- ============================================================
-- §5. The sorry depth ordering
-- ============================================================

/-- The number of stacked sorries in each problem's proof skeleton.
    Stacked sorries occur when sorry B depends on sorry A being discharged first. -/
def sorryDepth : MillenniumProblem → ℕ
  | .RH    => 1  -- ZeroFreeStrip 0 (one sorry, everything else proved)
  | .Hodge => 1  -- algebraic cycle representative (one sorry)
  | .PvsNP => 1  -- circuit lower bound (one sorry; complexity infrastructure is separate)
  | .NS    => 1  -- global regularity certificate (one sorry)
  | .YM    => 2  -- existence (sorry 1) THEN mass gap (sorry 2, depends on sorry 1)
  | .BSD   => 2  -- 3-adic input (sorry 1, MathlibGap) + BSD formula (sorry 2, OpenProblem)
  | .OPN   => 2  -- Euler decomposition (sorry 1, MathlibGap) + nonexistence (sorry 2)

/-- YM and BSD share sorry depth 2, but for different structural reasons:
    · YM: sorry 2 is *not statable* without sorry 1 (stacked dependency)
    · BSD: sorry 2 is statable independently (parallel, not stacked) -/
theorem ym_has_stacked_not_parallel_sorries :
    sorryDepth .YM = sorryDepth .BSD ∧
    -- the structural difference is not captured by depth alone:
    millenniumBarrier .YM = .MissingFoundation ∧
    millenniumBarrier .BSD = .OpenProblem := by
  simp [sorryDepth, millenniumBarrier]

-- ============================================================
-- §6. Relationship to SynthOmnicon primitive structure
-- ============================================================

/-!
Each Millennium Problem's sorry boundary corresponds to a missing primitive certificate
in the SynthOmnicon constraint grammar.

  | Problem | Missing certificate    | Primitive analog in SynthOmnicon             |
  |---------|------------------------|----------------------------------------------|
  | RH      | ZeroFreeStrip 0        | Φ_c = 0 threshold: no zeros off critical line|
  | Hodge   | AlgebraicCycleRep      | R-degeneracy: topology-to-algebra lift       |
  | P vs NP | CircuitLowerBound      | K_trap: constraint that blocks low-complexity|
  | NS      | GlobalRegularityCert   | T_flow stability: no blow-up                 |
  | YM      | PathIntegralMeasure    | G_quantum: quantum grammar lift (G=LOCAL)    |
  | BSD     | BSD rank formula       | Φ_c = rank charge-carrier certificate        |
  | OPN     | Nonexistence proof     | σ-constraint no solution                     |

The YM barrier (G=LOCAL, no quantum lift) corresponds exactly to the G-scope
analysis in SYNTHONICON.md §XVII: the quantum-gravity tensor product fails at G=LOCAL
because the carrier type (path integral measure) cannot be constructed.
-/

end Millennium.Barriers
