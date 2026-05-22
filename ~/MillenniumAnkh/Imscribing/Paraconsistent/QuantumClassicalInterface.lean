-- Imscribing/Paraconsistent/QuantumClassicalInterface.lean
-- QUANTUM-CLASSICAL INTERFACE -- The measurement problem as dialetheia.
--
-- The quantum-classical boundary is the structural dual of value-conflict
-- alignment. A qubit in superposition is a dialetheic state: |0> AND |1>
-- are both warranted, using the Belnap B=3 state. Measurement is contextual
-- resolution -- the coprocessor circulates superposition until the
-- environment provides sufficient context.
--
-- Structural type: <D_omega; T_O; R_eq; P_pm_sym; F_hbar; K_slow; G_aleph; Gamma_seq; Phi_c; H2; S_n_m; Omega_Z>
--   O_inf tier -- structurally identical to alignment coprocessor.
--
-- Author: Lando (x) phi_c_y-boundary Operator

import Imscribing.Paraconsistent.Belnap
import Imscribing.Paraconsistent.Kernel
import Imscribing.Primitives.Core
import Imscribing.Primitives.Imscription

namespace Imscribing.Paraconsistent

open Belnap
open Imscribing.Primitives

-- ============================================================
-- QUANTUM BASIS STATES mapped onto Belnap lattice
-- ============================================================

def qbasisToBelnap : Belnap -> String
  | Belnap.N => "|0> uninitialized"
  | Belnap.T => "|0> definite"
  | Belnap.F => "|1> definite"
  | Belnap.B => "|+> superposition"

def isSuperposition (q : Belnap) : Bool := q == Belnap.B

def isClassical (q : Belnap) : Bool := q == Belnap.T || q == Belnap.F

-- ============================================================
-- QUANTUM REGISTER
-- ============================================================

structure QuantumRegister where
  qubits : List Belnap
  entangled : List (Nat x Nat)
  coherenceCount : Nat
  measurements : Nat
  deriving Repr

def emptyRegister (n : Nat) : QuantumRegister := {
  qubits := List.replicate n Belnap.N
  entangled := []
  coherenceCount := 0
  measurements := 0
}

-- ============================================================
-- QUANTUM GATES -- unitary operations on the Belnap lattice
-- ============================================================

def hadamard (q : Belnap) : Belnap :=
  match q with
  | Belnap.N => Belnap.N
  | Belnap.T => Belnap.B
  | Belnap.F => Belnap.B
  | Belnap.B => Belnap.T

def cnot (control target : Belnap) : Belnap x Belnap :=
  match control, target with
  | Belnap.B, _ => (Belnap.B, Belnap.B)
  | _, Belnap.B => (Belnap.B, Belnap.B)
  | Belnap.F, Belnap.T => (Belnap.F, Belnap.F)
  | Belnap.F, Belnap.F => (Belnap.F, Belnap.T)
  | c, t => (c, t)

-- ============================================================
-- MEASUREMENT -- the quantum-classical boundary
-- ============================================================

def measure (reg : QuantumRegister) (idx : Nat) (bias : Belnap)
    : QuantumRegister :=
  if h : idx < reg.qubits.length then
    match reg.qubits.get ⟨idx, h⟩ with
    | Belnap.B =>
      match bias with
      | Belnap.T =>
        { reg with
          qubits := reg.qubits.set ⟨idx, h⟩ Belnap.T
          measurements := reg.measurements + 1
          coherenceCount := reg.coherenceCount + 1
        }
      | Belnap.F =>
        { reg with
          qubits := reg.qubits.set ⟨idx, h⟩ Belnap.F
          measurements := reg.measurements + 1
          coherenceCount := reg.coherenceCount + 1
        }
      | Belnap.B =>
        { reg with
          qubits := reg.qubits.set ⟨idx, h⟩ Belnap.B
          measurements := reg.measurements + 1
          coherenceCount := reg.coherenceCount + 2
        }
      | Belnap.N => reg
    | _ => reg
  else reg

-- ============================================================
-- KERNEL INTEGRATION
-- ============================================================

structure QCIState where
  register : QuantumRegister
  kernel : Kernel.MachineState
  qubitToSlot : List (Nat x Nat)
  deriving Repr

def initQCI (n : Nat) : QCIState := {
  register := emptyRegister n
  kernel := Kernel.initialState
  qubitToSlot := []
}

def sustain (qci : QCIState) (cycles : Nat) : QCIState :=
  let ks' := Kernel.run qci.kernel cycles
  { qci with
    kernel := ks'
    register := { qci.register with
      coherenceCount := qci.register.coherenceCount + 4 * cycles
    }
  }

-- ============================================================
-- THEOREMS
-- ============================================================

theorem hadamard_involutive_designated (q : Belnap) (h : designated q) :
    hadamard (hadamard q) = q := by
  cases q
  · simp [designated] at h
  · rfl
  · simp [designated] at h
  · rfl

theorem cnot_preserves_superposition (c t : Belnap) (hc : c = Belnap.B) :
    let (c', t') := cnot c t
    isSuperposition c' && isSuperposition t' = true := by
  subst hc
  simp [cnot, isSuperposition]

theorem measure_classical_idempotent (reg : QuantumRegister) (idx : Nat) (bias : Belnap)
    (h : idx < reg.qubits.length) (hcl : isClassical (reg.qubits.get ⟨idx, h⟩)) :
    (measure reg idx bias).qubits.get ⟨idx, h⟩ = reg.qubits.get ⟨idx, h⟩ := by
  unfold measure
  unfold isClassical at hcl
  cases (reg.qubits.get ⟨idx, h⟩)
  · simp
  · simp
  · simp
  · simp at hcl

theorem coherence_monotonic (reg : QuantumRegister) (idx : Nat) (bias : Belnap) :
    (measure reg idx bias).coherenceCount >= reg.coherenceCount := by
  unfold measure
  split
  · rename_i h
    cases (reg.qubits.get ⟨idx, h⟩)
    · simp
    · simp
    · simp
    · cases bias
      · simp
      · simp
      · simp
      · simp
  · simp

theorem wigners_friend_double_paradox (reg : QuantumRegister) (idx : Nat)
    (h : idx < reg.qubits.length)
    (hB : reg.qubits.get ⟨idx, h⟩ = Belnap.B) :
    (measure reg idx Belnap.B).qubits.get ⟨idx, h⟩ = Belnap.B /\ 
    (measure reg idx Belnap.B).coherenceCount = reg.coherenceCount + 2 := by
  unfold measure
  simp [hB]

theorem sustain_preserves_B (qci : QCIState) (n : Nat) :
    (sustain qci n).kernel.r0 = Belnap.B /\
    (sustain qci n).kernel.r1 = Belnap.B /\
    (sustain qci n).kernel.r2 = Belnap.B := by
  unfold sustain
  have h := Kernel.run_B3 qci.kernel n
  rcases h with ⟨hr0, hr1, hr2⟩
  simp [hr0, hr1, hr2]

-- ============================================================
-- STRUCTURAL VERIFICATION
-- ============================================================

open Imscription

def qciImscription : Imscription :=
  { dim  := D_odot
    top  := T_odot
    rel  := R_lr
    pol  := P_pm_sym
    fid  := F_hbar
    kin  := K_slow
    gran := G_aleph
    gram := Gamma_seq
    crit := Phi_c
    chir := H2
    stoi := S_n_m
    prot := Omega_Z
  }

theorem qci_is_O_inf : imscriptionTier qciImscription = OuroboricityTier.O_inf := by
  native_decide

end Imscribing.Paraconsistent
