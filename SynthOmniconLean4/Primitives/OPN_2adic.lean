-- SynthOmnicon/Classical/OPN_2adic.lean
-- Track 2, File 1: Classical number theory — 2-adic valuation for OPN.
-- This file is INDEPENDENT of the Synthonicon type system.
-- It uses Mathlib directly. Every sorry is an honest open problem marker.

import Mathlib.Tactic
import Mathlib.NumberTheory.ArithmeticFunction.Defs
import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.Data.Nat.Factorization.Basic
import Mathlib.Data.Nat.GCD.Basic
import Mathlib.RingTheory.Multiplicity
import Mathlib.Algebra.Ring.Parity           -- Nat.Even / Nat.Odd
import Mathlib.Algebra.Ring.GeomSum          -- geom_sum_mul, for σ(p^k) formula
import Mathlib.Data.Nat.Multiplicity         -- emultiplicity / v₂ lemmas

open Nat ArithmeticFunction

namespace SynthOmnicon.Classical.OPN

-- ============================================================
-- DEFINITIONS (must precede helper lemmas that reference them)
-- ============================================================

-- σ(n) is the sum-of-divisors function: ArithmeticFunction.sigma 1.
-- Perfect: σ(n) = 2n
def Perfect (n : ℕ) : Prop := sigma 1 n = 2 * n

-- 2-adic valuation: v₂(n) = exponent of 2 in the prime factorization of n.
noncomputable def v₂ (n : ℕ) : ℕ := (Nat.factorization n) 2

-- ============================================================
-- HELPER LEMMAS
-- ============================================================

-- Helper: (p-1) divides (p^n - 1) for any n, via geometric sum.
-- Uses geom_sum_mul: (∑ i < n, x^i) * (x - 1) = x^n - 1.
private lemma pred_dvd_pow_sub_one (p n : ℕ) (hp : 1 ≤ p) :
    (p - 1) ∣ (p ^ n - 1) := by
  use ∑ i ∈ Finset.range n, p ^ i
  zify [hp, Nat.one_le_pow n p (by omega)]
  -- geom_sum_mul gives (∑ i, p^i) * (p - 1) = p^n - 1
  -- We need p^n - 1 = (p - 1) * ∑ i, p^i (commutativity of multiplication)
  have h1 := geom_sum_mul (p : ℤ) n
  have h2 := mul_comm (∑ i ∈ Finset.range n, (p : ℤ) ^ i) ((p : ℤ) - 1)
  linarith

-- Helper: v₂(a / b) = v₂(a) - v₂(b) when b ∣ a.
private lemma v2_div_of_dvd {a b : ℕ} (h : b ∣ a) (hb : b ≠ 0) :
    v₂ (a / b) = v₂ a - v₂ b := by
  simp only [v₂]
  rw [Nat.factorization_div h]
  simp

-- Helper: If n % 4 = 2 then v₂(n) = 1.
-- 2^1 ∣ n (v₂ ≥ 1) and 2^2 ∤ n (v₂ < 2).
private lemma v2_eq_one_of_mod4_eq2 {n : ℕ} (hn : n % 4 = 2) : v₂ n = 1 := by
  have hpos : n ≠ 0 := by omega
  have h2prime : Nat.Prime 2 := by decide
  have h2dvd : 2^1 ∣ n := ⟨n / 2, by omega⟩
  have h4notdvd : ¬ (2^2 ∣ n) := by norm_num; intro ⟨k, hk⟩; omega
  simp only [v₂]
  apply Nat.le_antisymm
  · -- factorization 2 ≤ 1: if ≥ 2 then 2^2 ∣ n, contradiction
    by_contra hlt
    push_neg at hlt
    exact h4notdvd ((h2prime.pow_dvd_iff_le_factorization hpos (k := 2)).mpr (by omega))
  · -- 1 ≤ factorization 2: 2^1 ∣ n
    exact (h2prime.pow_dvd_iff_le_factorization hpos (k := 1)).mp h2dvd

-- Helper: q^i is odd whenever q is odd.
private lemma pow_odd_of_odd {q : ℕ} (hq : q % 2 = 1) (i : ℕ) : q ^ i % 2 = 1 := by
  induction i with
  | zero => simp
  | succ n ih => simp [pow_succ, Nat.mul_mod, hq, ih]

-- Helper: p^i ≡ 1 (mod 4) whenever p ≡ 1 (mod 4).
private lemma pow_mod4_of_mod4 {p : ℕ} (hp : p % 4 = 1) (i : ℕ) : p ^ i % 4 = 1 := by
  induction i with
  | zero => simp
  | succ n ih => simp [pow_succ, Nat.mul_mod, hp, ih]

-- Helper: ∑_{i<n} q^i ≡ n (mod 2) whenever q is odd.
-- Corollary (n = 2e+1 odd): sum ≡ 1 (mod 2), i.e. sum is odd.
private lemma geom_sum_mod2 (q n : ℕ) (hq : q % 2 = 1) :
    (∑ i ∈ Finset.range n, q ^ i) % 2 = n % 2 := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, Nat.add_mod, pow_odd_of_odd hq k, ih]
    omega

-- Helper: Sum of (2e+1) odd terms is odd.
private lemma geom_sum_odd_mod2 (q e : ℕ) (hq : q % 2 = 1) :
    (∑ i ∈ Finset.range (2 * e + 1), q ^ i) % 2 = 1 := by
  have h := geom_sum_mod2 q (2 * e + 1) hq
  omega

-- Helper: ∑_{i<n} p^i ≡ n (mod 4) whenever p ≡ 1 (mod 4).
private lemma geom_sum_mod4 (p n : ℕ) (hp : p % 4 = 1) :
    (∑ i ∈ Finset.range n, p ^ i) % 4 = n % 4 := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, Nat.add_mod, pow_mod4_of_mod4 hp k, ih]
    omega

-- Corollary: n ≡ 2 (mod 4) ⟹ sum ≡ 2 (mod 4) ⟹ v₂(sum) = 1.
-- Core of Lemma 1 — NO LTE NEEDED.
private lemma geom_sum_mod4_eq2 (p n : ℕ) (hp : p % 4 = 1) (hn : n % 4 = 2) :
    (∑ i ∈ Finset.range n, p ^ i) % 4 = 2 := by
  have h := geom_sum_mod4 p n hp
  omega

-- ============================================================
-- σ MULTIPLICATIVITY AND THE PRODUCT FORMULA
-- ============================================================

-- σ is multiplicative: σ(ab) = σ(a)σ(b) for coprime a, b.
-- Direct from Mathlib's isMultiplicative_sigma.
lemma sigma_mul_of_coprime {a b : ℕ} (h : Nat.Coprime a b) :
    sigma 1 (a * b) = sigma 1 a * sigma 1 b :=
  isMultiplicative_sigma.map_mul_of_coprime h

-- The fundamental OPN product equation.
-- σ(pᵏ)·σ(m²) = 2·pᵏ·m²: perfect number condition factored over the Euler decomposition.
-- This is the load-bearing equation for all numerical OPN bounds.
theorem opn_product_constraint {p k m : ℕ}
    (hperf : Perfect (p ^ k * m ^ 2))
    (hcop : Nat.Coprime (p ^ k) (m ^ 2)) :
    sigma 1 (p ^ k) * sigma 1 (m ^ 2) = 2 * (p ^ k * m ^ 2) := by
  rw [← sigma_mul_of_coprime hcop]
  exact hperf

-- The sigma ratio identity (no division, pure ℕ):
--   σ(pᵏ)·(p−1) + 1 = p^(k+1)
-- Proof: geometric sum identity ∑_{i≤k} pⁱ · (p-1) = p^(k+1) - 1.
-- Interpretation: σ(pᵏ)/pᵏ < p/(p−1) — every factor is strictly below the "prime ceiling".
-- This ceiling product ∏ p/(p-1) over all prime factors must exceed 2 for σ(n)/n = 2,
-- which forces a minimum number of distinct prime factors.
lemma sigma_prime_pow_ratio (p k : ℕ) (hp : Nat.Prime p) :
    sigma 1 (p ^ k) * (p - 1) + 1 = p ^ (k + 1) := by
  have h_sum : sigma 1 (p ^ k) = ∑ i ∈ Finset.range (k + 1), p ^ i := by
    rw [sigma_apply, Nat.divisors_prime_pow hp, Finset.sum_map]; simp
  rw [h_sum]
  zify [hp.one_le, Nat.one_le_pow (k + 1) p hp.pos]
  linarith [geom_sum_mul (p : ℤ) (k + 1)]

-- Corollary: σ(pᵏ)·(p−1) < p^(k+1)  (strict: the ratio never hits the ceiling).
lemma sigma_prime_pow_lt (p k : ℕ) (hp : Nat.Prime p) :
    sigma 1 (p ^ k) * (p - 1) < p ^ (k + 1) := by
  have h := sigma_prime_pow_ratio p k hp; omega

-- Any OPN is ≡ 1 (mod 4).
-- Proof: p ≡ 1 (mod 4) → pᵏ ≡ 1 (mod 4); n odd → m odd → m² ≡ 1 (mod 4);
-- n = pᵏ·m² ≡ 1·1 ≡ 1 (mod 4).
lemma opn_mod4 (p k m : ℕ) (h_odd : ¬ 2 ∣ p ^ k * m ^ 2)
    (hp_mod : p % 4 = 1) :
    (p ^ k * m ^ 2) % 4 = 1 := by
  have hm_odd : m % 2 = 1 := by
    by_contra hm
    push_neg at hm
    have : 2 ∣ m := by omega
    exact h_odd (Dvd.dvd.mul_left (Dvd.dvd.pow this (by norm_num)) (p ^ k))
  have hpk_mod : p ^ k % 4 = 1 := pow_mod4_of_mod4 hp_mod k
  have hm2_mod : m ^ 2 % 4 = 1 := by
    have hm4 : m % 4 = 1 ∨ m % 4 = 3 := by omega
    rcases hm4 with h | h <;> simp [pow_succ, pow_zero, Nat.mul_mod, h]
  calc (p ^ k * m ^ 2) % 4
      = (p ^ k % 4 * (m ^ 2 % 4)) % 4 := by rw [Nat.mul_mod]
    _ = (1 * 1) % 4 := by rw [hpk_mod, hm2_mod]
    _ = 1 := by norm_num

-- ============================================================
-- EULER'S THEOREM (1747)
-- Every odd perfect number has the form n = p^k * m²
-- where p prime, p ≡ k ≡ 1 [MOD 4], gcd(p, m) = 1.
-- ============================================================

theorem euler_opn_form (n : ℕ) (h_odd : ¬ 2 ∣ n) (h_perf : Perfect n) :
    ∃ (p k m : ℕ),
      Nat.Prime p ∧
      n = p ^ k * m ^ 2 ∧
      p % 4 = 1 ∧
      k % 4 = 1 ∧
      ¬ p ∣ m := by
  sorry -- Euler 1747. Not yet in Mathlib as of 2025.

-- ============================================================
-- THE 2-ADIC VALUATION ARGUMENT
-- ============================================================

-- Lemma 1: For odd prime p ≡ k ≡ 1 (mod 4), v₂(σ(p^k)) = 1.
lemma v2_sigma_prime_power (p k : ℕ) (hp : Nat.Prime p) (hp_odd : ¬ 2 ∣ p)
    (hp_mod : p % 4 = 1) (hk_mod : k % 4 = 1) :
    v₂ (sigma 1 (p ^ k)) = 1 := by
  have h_sigma_sum : sigma 1 (p ^ k) = ∑ i ∈ Finset.range (k + 1), p ^ i := by
    rw [sigma_apply, Nat.divisors_prime_pow hp, Finset.sum_map]
    simp
  have h_sum_mod4 : (∑ i ∈ Finset.range (k + 1), p ^ i) % 4 = 2 :=
    geom_sum_mod4_eq2 p (k + 1) hp_mod (by omega)
  rw [h_sigma_sum]
  exact v2_eq_one_of_mod4_eq2 h_sum_mod4

-- Lemma 2: For odd prime q and even exponent 2e, v₂(σ(q^(2e))) = 0.
-- σ(q^(2e)) is a sum of 2e+1 odd terms → odd → v₂ = 0.
lemma v2_sigma_square_factor (q e : ℕ) (hq : Nat.Prime q) (hq_odd : ¬ 2 ∣ q) :
    v₂ (sigma 1 (q ^ (2 * e))) = 0 := by
  have hq_mod : q % 2 = 1 := by
    have : q % 2 ≠ 0 := fun h => hq_odd ⟨q / 2, by omega⟩
    omega
  have h_sigma_sum : sigma 1 (q ^ (2 * e)) = ∑ i ∈ Finset.range (2 * e + 1), q ^ i := by
    rw [sigma_apply, Nat.divisors_prime_pow hq, Finset.sum_map]
    simp
  have h_odd : (∑ i ∈ Finset.range (2 * e + 1), q ^ i) % 2 = 1 :=
    geom_sum_odd_mod2 q e hq_mod
  have h_not_dvd : ¬ 2 ∣ sigma 1 (q ^ (2 * e)) := by
    rw [h_sigma_sum, Nat.dvd_iff_mod_eq_zero]; omega
  simp only [v₂, Nat.factorization_eq_zero_iff]
  right; left; exact h_not_dvd

-- Lemma 3: The accumulation constraint.
-- v₂(σ(p^k)) = 1 and each v₂(σ(qᵢ^(2eᵢ))) = 0.
-- This is consistent with σ(n) = 2n — it constrains the square part, not a contradiction.
theorem v2_accumulation_constraint (n p k m : ℕ)
    (h_odd : ¬ 2 ∣ n) (h_perf : Perfect n)
    (h_euler : n = p ^ k * m ^ 2)
    (hp : Nat.Prime p) (hp_mod : p % 4 = 1) (hk_mod : k % 4 = 1)
    (hp_odd : ¬ 2 ∣ p)
    (hq_odd : ∀ q ∈ (Nat.factorization m).support, ¬ 2 ∣ q) :
    v₂ (sigma 1 (p ^ k)) = 1 ∧
    ∀ q ∈ (Nat.factorization m).support,
      ∃ e, v₂ (sigma 1 (q ^ (2 * e))) = 0 := by
  constructor
  · exact v2_sigma_prime_power p k hp hp_odd hp_mod hk_mod
  · intro q hq_supp
    use (Nat.factorization m) q
    have hm_pos : m ≠ 0 := by intro hm; simp [hm] at h_euler; omega
    have hq_prime : q.Prime := by
      have hmem : q ∈ m.primeFactors := by rwa [← Nat.support_factorization]
      exact (Nat.mem_primeFactors.mp hmem).1
    exact v2_sigma_square_factor q _ hq_prime (hq_odd q hq_supp)

-- ============================================================
-- 3-ADIC HELPERS FOR TOUCHARD
-- (Mirror structure of 2-adic Section 2, now mod 3)
-- ============================================================

-- q^(2e) ≡ 1 (mod 3) when q ≡ 2 (mod 3).
-- Proof: q² ≡ 4 ≡ 1 (mod 3), so (q²)^e ≡ 1 (mod 3).
private lemma pow_mod3_q2_even {q : ℕ} (hq : q % 3 = 2) (e : ℕ) :
    q ^ (2 * e) % 3 = 1 := by
  have hq2 : q ^ 2 % 3 = 1 := by
    have : q ^ 2 = q * q := by ring
    rw [this, Nat.mul_mod, hq]
  rw [pow_mul]
  induction e with
  | zero => simp
  | succ n ih => rw [pow_succ, Nat.mul_mod, hq2, ih]

-- q^(2e+1) ≡ 2 (mod 3) when q ≡ 2 (mod 3).
private lemma pow_mod3_q2_odd {q : ℕ} (hq : q % 3 = 2) (e : ℕ) :
    q ^ (2 * e + 1) % 3 = 2 := by
  rw [pow_succ, Nat.mul_mod, pow_mod3_q2_even hq e, hq]

-- ∑_{i<n} q^i ≡ n % 2  (in {0,1} ⊂ ℤ/3ℤ) when q ≡ 2 (mod 3).
-- Pairs (q^(2j), q^(2j+1)) ≡ (1, 2) ≡ 0 (mod 3) cancel in pairs.
-- Even n → sum ≡ 0 (mod 3). Odd n → sum ≡ 1 (mod 3).
private lemma geom_sum_mod3_q2 (q n : ℕ) (hq : q % 3 = 2) :
    (∑ i ∈ Finset.range n, q ^ i) % 3 = n % 2 := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, Nat.add_mod, ih]
    have hpow : q ^ k % 3 = if k % 2 = 0 then 1 else 2 := by
      by_cases h : k % 2 = 0
      · rw [if_pos h, show k = 2 * (k / 2) from by omega]
        exact pow_mod3_q2_even hq (k / 2)
      · rw [if_neg h, show k = 2 * (k / 2) + 1 from by omega]
        exact pow_mod3_q2_odd hq (k / 2)
    rw [hpow]; split_ifs with h <;> omega

-- p^k ≡ 1 (mod 3) when p ≡ 1 (mod 3).
private lemma pow_mod3_one {p : ℕ} (hp : p % 3 = 1) (k : ℕ) : p ^ k % 3 = 1 := by
  induction k with
  | zero => simp
  | succ n ih =>
    rw [pow_succ, Nat.mul_mod, hp, ih]

-- m² ≡ 1 (mod 3) whenever 3 ∤ m.
-- Proof: m ≡ 1 or 2 (mod 3), and 1² ≡ 1, 2² ≡ 4 ≡ 1 (mod 3).
private lemma sq_mod3_of_not_dvd {m : ℕ} (hm : ¬ 3 ∣ m) : m ^ 2 % 3 = 1 := by
  have hm3 : m % 3 = 1 ∨ m % 3 = 2 := by
    have : m % 3 ≠ 0 := fun h => hm ⟨m / 3, by omega⟩
    omega
  have : m ^ 2 = m * m := by ring
  rw [this, Nat.mul_mod]
  rcases hm3 with h | h <;> simp [h]

-- 3 ∣ σ(pᵏ) when p ≡ 2 (mod 3) and k is odd.
-- Key: k+1 is even, so ∑_{i≤k} pⁱ pairs up to ≡ 0 (mod 3).
private lemma sigma_dvd3_of_p2_kodd (p k : ℕ) (hp : Nat.Prime p)
    (hp3 : p % 3 = 2) (hk_odd : k % 2 = 1) :
    3 ∣ sigma 1 (p ^ k) := by
  have h_sum : sigma 1 (p ^ k) = ∑ i ∈ Finset.range (k + 1), p ^ i := by
    rw [sigma_apply, Nat.divisors_prime_pow hp, Finset.sum_map]; simp
  rw [Nat.dvd_iff_mod_eq_zero, h_sum, geom_sum_mod3_q2 p (k + 1) hp3]
  omega  -- (k+1) % 2 = 0 since k % 2 = 1

-- ============================================================
-- TOUCHARD'S CONGRUENCE (1953)
-- ============================================================

-- Any OPN satisfies n ≡ 1 (mod 12) OR n ≡ 9 (mod 36).
-- Proof combines opn_mod4 (n ≡ 1 mod 4) with 3-adic case analysis.
theorem touchard_congruence (n p k m : ℕ)
    (h_odd : ¬ 2 ∣ n) (h_perf : Perfect n)
    (h_euler : n = p ^ k * m ^ 2)
    (hp : Nat.Prime p) (hp_mod : p % 4 = 1) (hk_mod : k % 4 = 1)
    (hcop : Nat.Coprime (p ^ k) (m ^ 2)) :
    n % 12 = 1 ∨ n % 36 = 9 := by
  -- Step 1: n ≡ 1 (mod 4)
  have hn4 : n % 4 = 1 := h_euler ▸ opn_mod4 p k m (h_euler ▸ h_odd) hp_mod
  -- Step 2: case split on 3 ∣ n
  by_cases h3 : 3 ∣ n
  · -- Case B: 3 ∣ n ─────────────────────────────────────────────────────
    right
    -- p ≡ 1 (mod 4) ≠ 3 ≡ 3 (mod 4), so p ≠ 3
    have hp3 : p ≠ 3 := by omega
    -- 3 is prime and p is prime and p ≠ 3, so 3 ∤ p
    have h3ndvdp : ¬ 3 ∣ p := fun h => by
      have := (hp.eq_one_or_self_of_dvd 3 h).resolve_left (by norm_num)
      omega
    -- 3 ∤ p → 3 ∤ pᵏ
    have h3ndvdpk : ¬ 3 ∣ p ^ k := fun h =>
      h3ndvdp ((by decide : Nat.Prime 3).dvd_of_dvd_pow h)
    -- 3 ∣ n = pᵏ·m², 3 ∤ pᵏ → 3 ∣ m²
    have h3m2 : 3 ∣ m ^ 2 := by
      have := h_euler ▸ h3
      rcases (by decide : Nat.Prime 3).dvd_mul.mp this with h | h
      · exact absurd h h3ndvdpk
      · exact h
    -- 3 ∣ m² → 3 ∣ m (3 prime)
    have h3m : 3 ∣ m := (by decide : Nat.Prime 3).dvd_of_dvd_pow h3m2
    -- 3 ∣ m → 9 ∣ m²
    obtain ⟨t, ht⟩ := h3m
    have h9m2 : 9 ∣ m ^ 2 := ⟨t ^ 2, by rw [ht]; ring⟩
    -- 9 ∣ n
    have h9n : 9 ∣ n := h_euler ▸ h9m2.mul_left (p ^ k)
    -- n ≡ 1 (mod 4) and 9 ∣ n → n ≡ 9 (mod 36)
    obtain ⟨s, hs⟩ := h9n
    rw [hs] at hn4; omega
  · -- Case A: 3 ∤ n ─────────────────────────────────────────────────────
    left
    -- 3 ∤ m (since n = pᵏ·m² and 3 ∤ n implies 3 ∤ m²  implies 3 ∤ m)
    have h3nm : ¬ 3 ∣ m := fun hm => h3 (h_euler ▸ dvd_mul_of_dvd_right (dvd_pow hm (by norm_num)) (p ^ k))
    -- m² ≡ 1 (mod 3)
    have hm2_3 : m ^ 2 % 3 = 1 := sq_mod3_of_not_dvd h3nm
    -- p ≡ 1 (mod 3): rule out p % 3 = 0 and p % 3 = 2
    have hp_3 : p % 3 = 1 := by
      have hp3_ne0 : p % 3 ≠ 0 := fun h => by
        have h3dvdp : 3 ∣ p := ⟨p / 3, by omega⟩
        have := hp.eq_one_or_self_of_dvd 3 h3dvdp
        -- 3 = 1 or 3 = p; 3 ≠ 1 so p = 3, but p % 4 = 1 ≠ 3 % 4 = 3
        omega
      have hp3_ne2 : p % 3 ≠ 2 := fun hp32 => by
        -- 3 ∣ σ(pᵏ) by sigma_dvd3_of_p2_kodd (k odd since k % 4 = 1)
        have hkodd : k % 2 = 1 := by omega
        have h3sig : 3 ∣ sigma 1 (p ^ k) :=
          sigma_dvd3_of_p2_kodd p k hp hp32 hkodd
        -- 3 ∣ σ(pᵏ) → 3 ∣ σ(pᵏ)·σ(m²) = 2n
        have hprod : sigma 1 (p ^ k) * sigma 1 (m ^ 2) = 2 * (p ^ k * m ^ 2) :=
          opn_product_constraint (h_euler ▸ h_perf) hcop
        have h3prod : 3 ∣ 2 * (p ^ k * m ^ 2) := hprod ▸ h3sig.mul_right _
        -- 3 ∤ 2n, contradiction
        have h3n2 : ¬ 3 ∣ 2 * n := fun h =>
          h3 ((by decide : Nat.Prime 3).dvd_mul.mp h |>.resolve_left (by norm_num))
        exact h3n2 (h_euler ▸ h3prod)
      omega
    -- pᵏ ≡ 1 (mod 3)
    have hpk_3 : p ^ k % 3 = 1 := pow_mod3_one hp_3 k
    -- n = pᵏ·m² ≡ 1·1 = 1 (mod 3)
    have hn3 : n % 3 = 1 := by
      rw [h_euler, Nat.mul_mod, hpk_3, hm2_3]
    -- CRT: n ≡ 1 (mod 4) and n ≡ 1 (mod 3) → n ≡ 1 (mod 12)
    omega

-- ============================================================
-- HONEST STATUS
-- ============================================================
-- The open problem is NOT that v₂ gives a contradiction.
-- It is showing that the full constraint system has no solution.
-- Current lower bound (Ochem-Rao 2012): OPN > 10^1500.

theorem opn_nonexistence : ∀ n : ℕ, ¬ (¬ 2 ∣ n ∧ Perfect n) := by
  sorry -- Open problem. Do not claim proven.

end SynthOmnicon.Classical.OPN
