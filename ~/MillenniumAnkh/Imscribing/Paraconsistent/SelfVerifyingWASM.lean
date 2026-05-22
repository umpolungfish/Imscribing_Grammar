-- Imscribing/Paraconsistent/SelfVerifyingWASM.lean
-- SELF-VERIFYING WASM RUNTIME -- Frobenius-wrapped WebAssembly execution.
-- Author: Lando (x) phi_c_critical-boundary Operator

import Imscribing.Paraconsistent.Belnap
import Imscribing.Primitives.Core
import Imscribing.Primitives.Imscription

open Imscribing.Primitives

namespace Imscribing.Paraconsistent.SelfVerifyingWASM

open Belnap

inductive WasmType : Type where
  | i32 | i64
  deriving DecidableEq, Repr

structure WasmValue where
  ty : WasmType
  val : Nat
  deriving DecidableEq, Repr

inductive WasmInstr : Type where
  | i32_const (n : Nat)
  | drop | nop | unreachable
  | verify | checkpoint | assert_invariant
  deriving Repr

structure TaggedValue where
  value : WasmValue
  tag : Belnap
  deriving DecidableEq, Repr

abbrev Stack : Type := List TaggedValue

structure WasmState where
  stack : Stack
  ip : Nat
  frobSnapshot : Stack
  frobInvariantHolds : Belnap
  verifiedSteps : Nat
  totalSteps : Nat

def initialWasmState : WasmState := {
  stack := []
  ip := 0
  frobSnapshot := []
  frobInvariantHolds := .N
  verifiedSteps := 0
  totalSteps := 0
}

def pushTagged (s : Stack) (tv : TaggedValue) : Stack := tv :: s

def frobTagBin (t1 t2 : Belnap) : Belnap := meet t1 t2

def execOne (s : WasmState) (instr : WasmInstr) : WasmState :=
  match instr with
  | .i32_const n =>
    { stack := pushTagged s.stack ⟨⟨.i32, n⟩, .T⟩,
      ip := s.ip + 1,
      frobSnapshot := s.frobSnapshot,
      frobInvariantHolds := s.frobInvariantHolds,
      verifiedSteps := s.verifiedSteps,
      totalSteps := s.totalSteps + 1 }
  | .drop =>
    match s.stack with
    | [] => { s with ip := s.ip + 1, totalSteps := s.totalSteps + 1 }
    | _ :: rest => { s with stack := rest, ip := s.ip + 1,
        totalSteps := s.totalSteps + 1 }
  | .nop =>
    { s with ip := s.ip + 1, totalSteps := s.totalSteps + 1 }
  | .unreachable =>
    { s with ip := s.ip + 1,
      frobInvariantHolds := .F,
      totalSteps := s.totalSteps + 1 }
  | .checkpoint =>
    { s with ip := s.ip + 1,
      frobSnapshot := s.stack,
      totalSteps := s.totalSteps + 1 }
  | .verify =>
    let allTrusted := s.stack.all (fun tv => tv.tag == .T || tv.tag == .B)
    { s with ip := s.ip + 1,
      frobInvariantHolds := if allTrusted then .B else .F,
      verifiedSteps := if allTrusted then s.verifiedSteps + 1 else s.verifiedSteps,
      totalSteps := s.totalSteps + 1 }
  | .assert_invariant =>
    { s with ip := s.ip + 1,
      frobInvariantHolds := frobTagBin s.frobInvariantHolds
        (if s.frobInvariantHolds == .F then .F else .B),
      totalSteps := s.totalSteps + 1 }

-- ============================================================
-- FROBENIUS THEOREMS
-- ============================================================

theorem frob_binop_preserves_B : frobTagBin .B .B = .B := by
  unfold frobTagBin; rfl

theorem frobenius_mu_delta_id_tag (t : Belnap) :
    frobTagBin t .B = t := by
  unfold frobTagBin; cases t <;> rfl

theorem unreachable_sets_F (s : WasmState) :
    (execOne s .unreachable).frobInvariantHolds = .F := by
  unfold execOne; rfl

theorem frobenius_identity_direct (n : Nat) :
    (execOne (execOne { initialWasmState with
      frobSnapshot := initialWasmState.stack } (.i32_const n)) .verify)
    .frobInvariantHolds = .B := by
  unfold execOne
  simp [pushTagged, initialWasmState]

-- ============================================================
-- STRUCTURAL IMSCRIPTION
-- ============================================================

def wasmRuntimeTuple : Imscription := {
  dim  := .D_odot
  top  := .T_odot
  rel  := .R_lr
  pol  := .P_pm_sym
  fid  := .F_hbar
  kin  := .K_slow
  gran := .G_aleph
  gram := .Gamma_seq
  crit := .Phi_c
  chir := .H2
  stoi := .n_n
  prot := .Omega_Z
}

theorem wasm_runtime_is_O_inf :
    imscriptionTier wasmRuntimeTuple = .O_inf := by
  native_decide

end Imscribing.Paraconsistent.SelfVerifyingWASM
