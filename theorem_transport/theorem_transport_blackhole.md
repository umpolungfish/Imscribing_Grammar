# Cross-Domain Theorem Transport

**Source:** `shem_hamephorash` — The 72 Names (Shem HaMephorash) from Exodus 14:19-21 — structural basis of creation where 72 = 6 × 12, every primitive v
**Target:** `schwarzschild_black_hole` — A classical Schwarzschild black hole solution in general relativity: a spacetime region causally disconnected from infin
**Structural Distance:** 0.0

## Cotype Dictionary

| Source (Lean) | Kind | Target (schwarzschild_black_hole) |
|---|---|---|
| `FrobeniusType` | inductive | [def: FrobeniusType] |
| `trivial` | constructor | [constructor: trivial] |
| `algebraOnly` | constructor | [constructor: algebraOnly] |
| `full` | constructor | [constructor: full] |
| `special` | constructor | [constructor: special] |
| `FrobeniusType` | def | [def: FrobeniusType] |
| `frobeniusToOuroboricity` | def | [def: frobeniusToOuroboricity] |
| `frobeniusToOuroboricity_strictMono` | theorem | [theorem: frobeniusToOuroboricity_strictMono] |
| `no_tier_between_o1_and_o2` | theorem | [theorem: no_tier_between_o1_and_o2] |
| `IsSpecial` | def | [def: IsSpecial] |
| `c13_gap_is_one_frobenius_tier` | theorem | [theorem: c13_gap_is_one_frobenius_tier] |
| `full_not_special` | theorem | [theorem: full_not_special] |
| `special_is_top` | theorem | [theorem: special_is_top] |
| `leeYangFrobeniusType` | def | [def: leeYangFrobeniusType] |
| `rhFrobeniusType` | def | [def: rhFrobeniusType] |
| `leeYang_strictly_above_rh` | theorem | [theorem: leeYang_strictly_above_rh] |
| `leeYang_is_special` | theorem | [theorem: leeYang_is_special] |
| `rh_is_not_special` | theorem | [theorem: rh_is_not_special] |
| `c13_gap_leyang_rh_is_one` | theorem | [theorem: c13_gap_leyang_rh_is_one] |
| `ymFrobeniusType` | def | [def: ymFrobeniusType] |
| `nsFrobeniusType` | def | [def: nsFrobeniusType] |
| `rh_ym_ns_same_frobenius_type` | theorem | [theorem: rh_ym_ns_same_frobenius_type] |
| `schwingerFrobeniusType` | def | [def: schwingerFrobeniusType] |
| `lerayFrobeniusType` | def | [def: lerayFrobeniusType] |
| `proved_c12_templates_are_full` | theorem | [theorem: proved_c12_templates_are_full] |
| `IsSelfGrounding` | def | [def: IsSelfGrounding] |
| `algebraOnly_not_selfGrounding` | theorem | [theorem: algebraOnly_not_selfGrounding] |
| `full_selfGrounding` | theorem | [theorem: full_selfGrounding] |
| `special_selfGrounding` | theorem | [theorem: special_selfGrounding] |
| `o2_is_minimum_selfGrounding` | theorem | [theorem: o2_is_minimum_selfGrounding] |
| `selfGrounding_iff` | theorem | [theorem: selfGrounding_iff] |
| `exactly_two_selfGrounding_types` | theorem | [theorem: exactly_two_selfGrounding_types] |

## Transported Theorem: `exactly_two_selfGrounding_types`

### Source Statement (Lean)

```lean
theorem exactly_two_selfGrounding_types :
    (Finset.univ (α := FrobeniusType)).filter IsSelfGrounding =
    {FrobeniusType.full, FrobeniusType.special} := by
  ext t
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
             Finset.mem_insert, Finset.mem_singleton, selfGrounding_iff]
```

### Target Statement (schwarzschild_black_hole)

```
theorem exactly_two_selfGrounding_types :
    (Finset.univ (α := FrobeniusType)).filter IsSelfGrounding =
    {FrobeniusType.full, FrobeniusType.special} := by
  ext t
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
             Finset.mem_insert, Finset.mem_singleton, selfGrounding_iff]
```

## Unmapped Identifiers (32)

Run with `--register` to map these interactively:

- `FrobeniusType` (inductive): 
- `trivial` (constructor): /-- O₀ — unit η only; no fixed-point structure -/
- `algebraOnly` (constructor): /-- O₁ — (μ, η); can compose toward fixed points; basin not generated -/
- `full` (constructor): /-- O₂ — (μ, η, δ, ε) + Frobenius condition; self-grounding -/
- `special` (constructor): /-- O_∞ — full + μ ∘ δ = id; symmetry exactly characterises fixed point -/
- `FrobeniusType` (def): /-- Numerical rank for the linear order: trivial=0 < algebraOnly=1 < full=2 < special=3 -/
- `frobeniusToOuroboricity` (def): 
- `frobeniusToOuroboricity_strictMono` (theorem): /-- The ouroboricity map preserves strict ordering. -/
- `no_tier_between_o1_and_o2` (theorem): 
- `IsSpecial` (def): 
- `c13_gap_is_one_frobenius_tier` (theorem): 
- `full_not_special` (theorem): /-- Full Frobenius is not special. -/
- `special_is_top` (theorem): /-- Specialness is the strictly top tier. -/
- `leeYangFrobeniusType` (def): 
- `rhFrobeniusType` (def): 
- `leeYang_strictly_above_rh` (theorem): /-- Lee-Yang is strictly above RH in Frobenius completeness. -/
- `leeYang_is_special` (theorem): /-- Lee-Yang is special; RH is not. -/
- `rh_is_not_special` (theorem): 
- `c13_gap_leyang_rh_is_one` (theorem): 
- `ymFrobeniusType` (def): 
- `nsFrobeniusType` (def): 
- `rh_ym_ns_same_frobenius_type` (theorem): 
- `schwingerFrobeniusType` (def): 
- `lerayFrobeniusType` (def): 
- `proved_c12_templates_are_full` (theorem): 
- `IsSelfGrounding` (def): /-- A system is self-grounding iff its Frobenius type is at least full (O₂). -/
- `algebraOnly_not_selfGrounding` (theorem): /-- O₁ is not self-grounding: externally describable but cannot generate its basin. -/
- `full_selfGrounding` (theorem): /-- O₂ and O_∞ are self-grounding. -/
- `special_selfGrounding` (theorem): 
- `o2_is_minimum_selfGrounding` (theorem): 
- `selfGrounding_iff` (theorem): /-- Exactly full and special are self-grounding (the two highest tiers). -/
- `exactly_two_selfGrounding_types` (theorem): /-- Exactly two Frobenius types are self-grounding (full and special). -/


## Natural Language Rendering

**In the language of A classical Schwarzschild black hole solution in general relativity: a spacetime region causally disconnected from infinity by an event horizon. Exhibits thermodynamic properties (Bekenstein-Hawking entropy), information paradox, imscriptive encoding of interior degrees of freedom on the horizon:**

> Among the **FrobeniusType**, exactly **2** are **IsSelfGrounding**:
> - **FrobeniusType.full**
> - **FrobeniusType.special**

> The Lean proof (`cases t <;> decide`) becomes an examination of each frobeniustype. The proof tree is invariant; only the leaves are renamed.

> *Cotype of:*
> ```lean
> theorem exactly_two_selfGrounding_types :
>     (Finset.univ (α := FrobeniusType)).filter IsSelfGrounding =
>     {FrobeniusType.full, FrobeniusType.special} := by
>   ext t
> ```