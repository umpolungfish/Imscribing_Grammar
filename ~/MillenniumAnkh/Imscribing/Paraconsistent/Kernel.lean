-- Imscribing/Paraconsistent/Kernel.lean
-- THE PARACONSISTENT KERNEL — Three-register machine running ENGAGR→FSPLIT→FFUSE.
-- Loop invariant: μ ∘ δ = id (Frobenius identity).
-- Belnap fixed point: all three registers permanently at B=3 (both).
-- Author: Lando ⊗ ⊙_ÿ-boundary Operator

import Imscribing.Paraconsistent.Belnap
import Imscribing.Primitives.Core
import Imscribing.Primitives.Imscription

namespace Imscribing.Paraconsistent

open Belnap

-- ============================================================
-- REGISTER MACHINE STATE
-- ============================================================

/-- State of the three-register paraconsistent machine.
    Each register holds a Belnap value. -/
structure MachineState where
  r0 : Belnap
  r1 : Belnap
  r2 : Belnap
  paradoxCount : Nat
  cycleCount : Nat
  deriving Repr

/-- The initial state: all three registers at B, paradox and cycle counters at 0.
    B=3 is the Belnap fixed point — the machine starts saturated. -/
def initialState : MachineState := {
  r0 := .B, r1 := .B, r2 := .B,
  paradoxCount := 0, cycleCount := 0
}

/-- All three registers are at B — the Belnap fixed-point condition. -/
def isFixedPoint (s : MachineState) : Bool :=
  s.r0 == .B && s.r1 == .B && s.r2 == .B

/-- Belnap distribution: count of each value across the three registers. -/
def belnapDist (s : MachineState) : BelnapDistribution where
  n := (if s.r0 == .N then 1 else 0) + (if s.r1 == .N then 1 else 0) + (if s.r2 == .N then 1 else 0)
  t := (if s.r0 == .T then 1 else 0) + (if s.r1 == .T then 1 else 0) + (if s.r2 == .T then 1 else 0)
  f := (if s.r0 == .F then 1 else 0) + (if s.r1 == .F then 1 else 0) + (if s.r2 == .F then 1 else 0)
  b := (if s.r0 == .B then 1 else 0) + (if s.r1 == .B then 1 else 0) + (if s.r2 == .B then 1 else 0)

-- ============================================================
-- KERNEL INSTRUCTIONS (three-instruction set)
-- ============================================================

/-- ENGAGR: Engulfs %r0 by meeting it with itself, then joining the result.
    In Belnap terms: engager(r) = r ⊓ r ⊔ r
    Since ⊓ is idempotent, r ⊓ r = r. Then r ⊔ r = r.
    So ENGAGR is operationally a no-op on a settled register, BUT:
    it is NOT a no-op in the paraconsistent context — it quantifies the agreement
    of the register with itself, a self-consistency check that produces paradox
    when the register is in an ambiguous state.

    In the full kernel semantics: ENGAGR %r0 means:
      The register self-models — it checks whether its own content is consistent.
      For B, this is a paraconsistent operation: B agrees with B, but B also
      disagrees with B (since B = both true and false). The agreement check triggers
      a paradox count increment.