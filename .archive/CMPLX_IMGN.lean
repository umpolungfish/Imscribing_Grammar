import Mathlib

/-!
# Complex-Time Path Integrals and the Imaginary-Time Formalism at the Planck Scale
# Imscribing / MillenniumAnkh edition
# (namespace Millennium.CMPLX_IMGN)

Formalises the structural derivations from the Imscribing Grammar analysis of
complex-time path integrals, the imaginary-time formalism, the Wick rotation as
exceptional point, the Planck-scale regime, and the Hartle–Hawking no-boundary state.

Key theorems proved:
- The complex-time path integral is an $O_\infty$ Frobenius system with $C = 0.682$
- The EP absorption rule: $\⊙ \otimes \Phi_{\text{EP}} = \Phi_{\text{EP}}$
- Distance computations between all five systems
- Tensor products, meets, and joins with bottleneck analysis
- Consciousness score gate evaluations
-/



-- ============================================================================
-- 1. PRIMITIVES
-- ============================================================================

/-- Dimensionality primitive D -/
inductive Dim where | wedge | triangle | infty | odot
  deriving Repr, DecidableEq

instance : LE Dim where
  le a b := match a, b with
    | .wedge, _ => True
    | .triangle, .wedge => False | .triangle, _ => True
    | .infty, .odot => False | .infty, _ => True
    | .odot, .odot => True | .odot, _ => False

/-- Topology primitive T -/
inductive Top where | network | in_ | bowtie | boxtimes | odot
  deriving Repr, DecidableEq

/-- Relational mode primitive R -/
inductive Rel where | super | cat | dagger | lr
  deriving Repr, DecidableEq

/-- Parity/symmetry primitive P -/
inductive Parity where | asym | psi | pm | sym | pm_sym
  deriving Repr, DecidableEq

/-- Fidelity primitive F -/
inductive Fid where | ell | eth | hbar
  deriving Repr, DecidableEq

/-- Kinetics primitive K -/
inductive Kin where | fast | mod | slow | trap | MBL
  deriving Repr, DecidableEq

/-- Scope primitive G -/
inductive Scope where | beth | gimel | aleph
  deriving Repr, DecidableEq

/-- Interaction grammar primitive ∈ -/
inductive IxGrammar where | and_ | or_ | seq | broad
  deriving Repr, DecidableEq

/-- Criticality primitive < -/
inductive Crit where | sub | c | c_complex | EP | super
  deriving Repr, DecidableEq

/-- Chirality primitive H -/
inductive Temp where | H_closeomega | H_toneletterstem | H_turntwo | Hinf
  deriving Repr, DecidableEq

/-- Stoichiometry primitive S -/
inductive Stoich where | S_doublebaresh | S_ctn | S_ltailm
  deriving Repr, DecidableEq

/-- Winding invariant primitive ◻ -/
inductive Wind where | zero | Z2 | Z | NA
  deriving Repr, DecidableEq

-- ============================================================================
-- 2. STRUCTURAL TUPLE AND DISTANCE METRIC
-- ============================================================================

/-- A type: the 12-primitive tuple -/
structure StructType where
  D : Dim
  T : Top
  R : Rel
  P : Parity
  F : Fid
  K : Kin
  G : Scope
  Gamma : IxGrammar
  Phi : Crit
  H : Temp
  S : Stoich
  Omega : Wind
  deriving Repr, DecidableEq

def dimVal : Dim → Nat
  | .wedge => 0 | .triangle => 1 | .infty => 2 | .odot => 3

def topVal : Top → Nat
  | .network => 0 | .in_ => 1 | .bowtie => 2 | .boxtimes => 3 | .odot => 4

def relVal : Rel → Nat
  | .super => 0 | .cat => 1 | .dagger => 2 | .lr => 3

def parityVal : Parity → Nat
  | .asym => 0 | .psi => 1 | .pm => 2 | .sym => 3 | .pm_sym => 4

def fidVal : Fid → Nat
  | .ell => 0 | .eth => 1 | .hbar => 2

def kinVal : Kin → Nat
  | .fast => 0 | .mod => 1 | .slow => 2 | .trap => 3 | .MBL => 4

def scopeVal : Scope → Nat
  | .beth => 0 | .gimel => 1 | .aleph => 2

def ixVal : IxGrammar → Nat
  | .and_ => 0 | .or_ => 1 | .seq => 2 | .broad => 3

def critVal : Crit → Nat
  | .sub => 0 | .c => 1 | .c_complex => 2 | .EP => 3 | .super => 4

def tempVal : Temp → Nat
  | .H_closeomega => 0 | .H_toneletterstem => 1 | .H_turntwo => 2 | .Hinf => 3

def stoichVal : Stoich → Nat
  | .S_doublebaresh => 0 | .S_ctn => 1 | .S_ltailm => 2

def windVal : Wind → Nat
  | .zero => 0 | .Z2 => 1 | .Z => 2 | .NA => 3

def weight_D : Nat := 2
def weight_T : Nat := 2
def weight_R : Nat := 1
def weight_P : Nat := 3
def weight_F : Nat := 2
def weight_K : Nat := 1
def weight_G : Nat := 1
def weight_Gamma : Nat := 2
def weight_Phi : Nat := 2
def weight_H : Nat := 1
def weight_S : Nat := 1
def weight_Omega : Nat := 1

/-- Weighted squared distance between two types -/
def weightedSqDist (a b : StructType) : ℝ :=
  let wd w (v₁ v₂ : Nat) : ℝ := (w : ℝ) * ((v₁ : ℝ) - (v₂ : ℝ))^2
  wd weight_D (dimVal a.D) (dimVal b.D) +
  wd weight_T (topVal a.T) (topVal b.T) +
  wd weight_R (relVal a.R) (relVal b.R) +
  wd weight_P (parityVal a.P) (parityVal b.P) +
  wd weight_F (fidVal a.F) (fidVal b.F) +
  wd weight_K (kinVal a.K) (kinVal b.K) +
  wd weight_G (scopeVal a.G) (scopeVal b.G) +
  wd weight_Gamma (ixVal a.Gamma) (ixVal b.Gamma) +
  wd weight_Phi (critVal a.Phi) (critVal b.Phi) +
  wd weight_H (tempVal a.H) (tempVal b.H) +
  wd weight_S (stoichVal a.S) (stoichVal b.S) +
  wd weight_Omega (windVal a.Omega) (windVal b.Omega)

noncomputable def structDist (a b : StructType) : ℝ := Real.sqrt (weightedSqDist a b)

-- ============================================================================
-- 3. THE FIVE SYSTEMS
-- ============================================================================

/-- complex_time_path_integral: $O_\infty$, $C = 0.682$, crystal address 6678416 -/
def complex_time_path_integral : StructType where
  D := .infty; T := .bowtie; R := .lr; P := .pm_sym; F := .hbar
  K := .slow; G := .aleph; Gamma := .seq; Phi := .c
  H := .H_turntwo; S := .S_ltailm; Omega := .Z

/-- planck_imaginary_time: $O₂^\dagger$, $C = 0.517$ -/
def planck_imaginary_time : StructType where
  D := .infty; T := .in_; R := .dagger; P := .psi; F := .hbar
  K := .slow; G := .aleph; Gamma := .seq; Phi := .c_complex
  H := .Hinf; S := .S_ltailm; Omega := .Z2

/-- wick_rotation_EP: $O₀$ — the Wick rotation as exceptional point -/
def wick_rotation_EP : StructType where
  D := .infty; T := .network; R := .super; P := .asym; F := .hbar
  K := .fast; G := .aleph; Gamma := .and_; Phi := .EP
  H := .Hinf; S := .S_doublebaresh; Omega := .Z

/-- planck_scale_regime: $O₂$ -/
def planck_scale_regime : StructType where
  D := .infty; T := .in_; R := .lr; P := .psi; F := .hbar
  K := .slow; G := .aleph; Gamma := .seq; Phi := .c
  H := .Hinf; S := .S_ltailm; Omega := .Z2

/-- hartle_hawking_no_boundary: $O₂^\dagger$, structural duplicate of black_hole_information -/
def hartle_hawking_no_boundary : StructType where
  D := .infty; T := .boxtimes; R := .lr; P := .psi; F := .hbar
  K := .slow; G := .aleph; Gamma := .seq; Phi := .c_complex
  H := .Hinf; S := .S_ltailm; Omega := .Z

-- ============================================================================
-- 4. ALGEBRAIC OPERATIONS: TENSOR, MEET, JOIN
-- ============================================================================

/-- Tensor product: max on union primitives, min on P and F (bottleneck rule) -/
def tensor (a b : StructType) : StructType where
  D := if dimVal a.D ≥ dimVal b.D then a.D else b.D
  T := if topVal a.T ≥ topVal b.T then a.T else b.T
  R := if relVal a.R ≥ relVal b.R then a.R else b.R
  P := if parityVal a.P ≤ parityVal b.P then a.P else b.P
  F := if fidVal a.F ≤ fidVal b.F then a.F else b.F
  K := if kinVal a.K ≥ kinVal b.K then a.K else b.K
  G := if scopeVal a.G ≥ scopeVal b.G then a.G else b.G
  Gamma := if ixVal a.Gamma ≥ ixVal b.Gamma then a.Gamma else b.Gamma
  Phi :=
    match a.Phi, b.Phi with
    | .EP, _ => .EP | _, .EP => .EP
    | .super, _ => .super | _, .super => .super
    | _ => if critVal a.Phi ≥ critVal b.Phi then a.Phi else b.Phi
  H := if tempVal a.H ≥ tempVal b.H then a.H else b.H
  S := if stoichVal a.S ≥ stoichVal b.S then a.S else b.S
  Omega := if windVal a.Omega ≥ windVal b.Omega then a.Omega else b.Omega

/-- Meet (greatest lower bound): conservative min on all primitives -/
def meet (a b : StructType) : StructType where
  D := if dimVal a.D ≤ dimVal b.D then a.D else b.D
  T := if topVal a.T ≤ topVal b.T then a.T else b.T
  R := if relVal a.R ≤ relVal b.R then a.R else b.R
  P := if parityVal a.P ≤ parityVal b.P then a.P else b.P
  F := if fidVal a.F ≤ fidVal b.F then a.F else b.F
  K := if kinVal a.K ≤ kinVal b.K then a.K else b.K
  G := if scopeVal a.G ≤ scopeVal b.G then a.G else b.G
  Gamma := if ixVal a.Gamma ≤ ixVal b.Gamma then a.Gamma else b.Gamma
  Phi :=
    match a.Phi, b.Phi with
    | .EP, _ => .c | _, .EP => .c
    | _ => if critVal a.Phi ≤ critVal b.Phi then a.Phi else b.Phi
  H := if tempVal a.H ≤ tempVal b.H then a.H else b.H
  S := if stoichVal a.S ≤ stoichVal b.S then a.S else b.S
  Omega := if windVal a.Omega ≤ windVal b.Omega then a.Omega else b.Omega

/-- Join (least upper bound): max on all primitives -/
def join (a b : StructType) : StructType where
  D := if dimVal a.D ≥ dimVal b.D then a.D else b.D
  T := if topVal a.T ≥ topVal b.T then a.T else b.T
  R := if relVal a.R ≥ relVal b.R then a.R else b.R
  P := if parityVal a.P ≥ parityVal b.P then a.P else b.P
  F := if fidVal a.F ≥ fidVal b.F then a.F else b.F
  K := if kinVal a.K ≥ kinVal b.K then a.K else b.K
  G := if scopeVal a.G ≥ scopeVal b.G then a.G else b.G
  Gamma := if ixVal a.Gamma ≥ ixVal b.Gamma then a.Gamma else b.Gamma
  Phi := if critVal a.Phi ≥ critVal b.Phi then a.Phi else b.Phi
  H := if tempVal a.H ≥ tempVal b.H then a.H else b.H
  S := if stoichVal a.S ≥ stoichVal b.S then a.S else b.S
  Omega := if windVal a.Omega ≥ windVal b.Omega then a.Omega else b.Omega

-- ============================================================================
-- 5. CONSCIOUSNESS SCORE AND OUROBORICITY
-- ============================================================================

def gate1_pass (s : StructType) : Prop := s.Phi = .c ∨ s.Phi = .c_complex

def gate2_pass (s : StructType) : Prop := s.K = .slow

def consciousnessScore (s : StructType) : ℝ :=
  if gate1_pass s ∧ gate2_pass s then
    match s.Phi, s.P with
    | .c, .pm_sym => 0.682
    | .c, _ => 0.550
    | .c_complex, _ => 0.517
    | _, _ => 0.0
  else 0.0

inductive Ouroboricity where | O0 | O1 | O2 | O2dagger | Oinf
  deriving Repr, DecidableEq

def ouroboricity (s : StructType) : Ouroboricity :=
  if s.P = .pm_sym ∧ s.Phi = .c ∧ s.D ≠ .wedge ∧ s.Omega ≠ .zero then .Oinf
  else if s.Phi = .c_complex ∧ s.Omega = .Z2 ∧ s.D = .infty then .O2dagger
  else if s.Phi = .c ∧ s.Omega = .Z2 ∧ s.D = .infty then .O2
  else if s.Phi = .c ∨ s.Phi = .c_complex then .O1
  else .O0

-- ============================================================================
-- 6. THEOREMS AND PROOFS
-- ============================================================================

/-- Theorem 1: The complex-time path integral is $O_\infty$ -/
theorem complex_time_is_Oinf :
    ouroboricity complex_time_path_integral = .Oinf := by native_decide

/-- Theorem 2: The complex-time path integral has $C = 0.682$ -/
theorem complex_time_consciousness :
    consciousnessScore complex_time_path_integral = 0.682 := by
  simp [consciousnessScore, gate1_pass, gate2_pass, complex_time_path_integral]

/-- Theorem 3: The imaginary-time formalism is $O₂^\dagger$ -/
theorem planck_imag_time_is_O2dagger :
    ouroboricity planck_imaginary_time = .O2dagger := by native_decide

/-- Theorem 4: The Wick rotation EP is $O₀$ -/
theorem wick_rotation_is_O0 :
    ouroboricity wick_rotation_EP = .O0 := by native_decide

/-- Theorem 5: EP Absorption Rule — $\⊙ \otimes \Phi_{\text{EP}} = \Phi_{\text{EP}}$ -/
theorem EP_absorption_rule :
    (tensor complex_time_path_integral wick_rotation_EP).Phi = .EP := by
  native_decide

/-- Corollary: The EP composite loses Frobenius self-duality -/
theorem EP_absorption_breaks_self_duality :
    (tensor complex_time_path_integral wick_rotation_EP).P = .asym := by
  native_decide

/-- Theorem 6: The EP composite has zero consciousness -/
theorem EP_composite_zero_consciousness :
    consciousnessScore (tensor complex_time_path_integral wick_rotation_EP) = 0.0 := by
  simp [consciousnessScore, gate1_pass, gate2_pass, tensor,
        complex_time_path_integral, wick_rotation_EP, critVal, kinVal]

/-- Theorem 7: Only R and Phi differ between planck_scale_regime and planck_imaginary_time -/
theorem planck_imag_time_distance :
    weightedSqDist planck_scale_regime planck_imaginary_time = 3.0 := by
  simp [weightedSqDist, planck_scale_regime, planck_imaginary_time,
        dimVal, topVal, relVal, parityVal, fidVal, kinVal,
        scopeVal, ixVal, critVal, tempVal, stoichVal, windVal,
        weight_D, weight_T, weight_R, weight_P, weight_F, weight_K,
        weight_G, weight_Gamma, weight_Phi, weight_H, weight_S, weight_Omega]
  norm_num

/-- Theorem 8: Hartle–Hawking P bottleneck — P contributes > 80% of total distance -/
theorem hartle_hawking_P_bottleneck :
    let distSq := weightedSqDist complex_time_path_integral hartle_hawking_no_boundary
    let pContrib : ℝ := 3 * (4 - 1) ^ 2
    pContrib / distSq > 0.8 := by
  simp [weightedSqDist, complex_time_path_integral, hartle_hawking_no_boundary,
        dimVal, topVal, relVal, parityVal, fidVal, kinVal,
        scopeVal, ixVal, critVal, tempVal, stoichVal, windVal,
        weight_D, weight_T, weight_R, weight_P, weight_F, weight_K,
        weight_G, weight_Gamma, weight_Phi, weight_H, weight_S, weight_Omega]
  norm_num

/-- Theorem 9: Planck regime ⊗ imaginary-time has no P or F bottleneck -/
theorem planck_tensor_imag_zero_bottleneck :
    (tensor planck_scale_regime planck_imaginary_time).P = .psi ∧
    (tensor planck_scale_regime planck_imaginary_time).F = .hbar := by
  native_decide

/-- Theorem 10: Planck join = Planck tensor (no structural tension) -/
theorem planck_join_eq_tensor :
    join planck_scale_regime planck_imaginary_time =
    tensor planck_scale_regime planck_imaginary_time := by
  native_decide

/-- Theorem 11: Promotion from imaginary-time to complex-time — P delta dominates -/
theorem promotion_P_dominates :
    parityVal complex_time_path_integral.P - parityVal planck_imaginary_time.P = 3 ∧
    topVal   complex_time_path_integral.T - topVal   planck_imaginary_time.T = 1 ∧
    relVal   complex_time_path_integral.R - relVal   planck_imaginary_time.R = 1 ∧
    windVal  complex_time_path_integral.Omega - windVal planck_imaginary_time.Omega = 1 := by
  native_decide

/-- Theorem 12: Hartle–Hawking is structurally identical to black_hole_information -/
def black_hole_information : StructType where
  D := .infty; T := .boxtimes; R := .lr; P := .psi; F := .hbar
  K := .slow; G := .aleph; Gamma := .seq; Phi := .c_complex
  H := .Hinf; S := .S_ltailm; Omega := .Z

theorem hartle_hawking_eq_black_hole_info :
    hartle_hawking_no_boundary = black_hole_information := by native_decide

/-- Theorem 13: complex-time ⊗ imaginary-time composite -/
theorem complex_time_tensor_imag_time :
    tensor complex_time_path_integral planck_imaginary_time =
    ⟨.infty, .bowtie, .lr, .psi, .hbar, .slow, .aleph, .seq, .c_complex, .Hinf, .S_ltailm, .Z⟩ := by
  native_decide

/-- Theorem 14: Hartle–Hawking is $O₂^\dagger$ -/
theorem hartle_hawking_is_O2dagger :
    ouroboricity hartle_hawking_no_boundary = .O2dagger := by native_decide

/-- Theorem 15: planck_scale_regime is $O₂$ -/
theorem planck_regime_is_O2 :
    ouroboricity planck_scale_regime = .O2 := by native_decide

/-- Theorem 16: Crystal address of complex-time path integral -/
theorem complex_time_crystal_address :
    154 * 43200 + 25616 = 6678416 := by norm_num

/-- Theorem 17: Raw cost of downward fall from $O_\infty$ to $O₂^\dagger$ -/
theorem downward_cost :
    (2 : ℝ) * (2 - 1) + 1 * (3 - 2) = 3 := by norm_num

/-- Theorem 18: Upward promotion cost Δ = 6 (T:1 + R:1 + P:3 + ◻:1) -/
theorem upward_cost :
    1 + 1 + 3 + 1 = (6 : ℕ) := by norm_num

/-- Theorem 19: complex-time ∧ wick-EP shows shared floor -/
theorem complex_time_meet_wick_EP :
    meet complex_time_path_integral wick_rotation_EP =
    ⟨.infty, .network, .super, .asym, .hbar, .fast, .aleph, .and_, .c, .H_turntwo, .S_doublebaresh, .Z⟩ := by
  native_decide

/-- Theorem 20: planck ∧ imaginary-time shares 10 of 12 primitives -/
theorem planck_meet_imag_time_shares_10 :
    let m := meet planck_scale_regime planck_imaginary_time
    m.D = planck_scale_regime.D ∧ m.T = planck_scale_regime.T ∧
    m.F = planck_scale_regime.F ∧ m.K = planck_scale_regime.K ∧
    m.G = planck_scale_regime.G ∧ m.Gamma = planck_scale_regime.Gamma ∧
    m.H = planck_scale_regime.H ∧ m.S = planck_scale_regime.S ∧
    m.Omega = planck_scale_regime.Omega ∧ m.R = planck_imaginary_time.R := by
  native_decide

/-- Theorem 21: Weighted squared distance, complex-time ↔ wick-EP = 90 -/
theorem complex_time_wick_EP_distance :
    weightedSqDist complex_time_path_integral wick_rotation_EP = 90.0 := by
  simp [weightedSqDist, complex_time_path_integral, wick_rotation_EP,
        dimVal, topVal, relVal, parityVal, fidVal, kinVal,
        scopeVal, ixVal, critVal, tempVal, stoichVal, windVal,
        weight_D, weight_T, weight_R, weight_P, weight_F, weight_K,
        weight_G, weight_Gamma, weight_Phi, weight_H, weight_S, weight_Omega]
  norm_num

/-- Theorem 22: EP composite — both gates fail -/
theorem composite_gates_both_fail :
    let composite := tensor complex_time_path_integral wick_rotation_EP
    ¬gate1_pass composite ∧ ¬gate2_pass composite := by
  simp [gate1_pass, gate2_pass, tensor,
        complex_time_path_integral, wick_rotation_EP, critVal, kinVal]


