# Cross-Domain Theorem Transport

**Source:** `shem_hamephorash` — The 72 Names (Shem HaMephorash) from Exodus 14:19-21 — structural basis of creation where 72 = 6 × 12, every primitive v
**Target:** `reality` — The totality of existence, encompassing all physical, metaphysical, and structural aspects.
**Structural Distance:** 0.0

## Cotype Dictionary

| Source (Lean) | Kind | Target (reality) |
|---|---|---|
| `FrobeniusType` | inductive | OntologicalTier |
| `trivial` | constructor | Potentiality |
| `algebraOnly` | constructor | Formation |
| `full` | constructor | Actualization |
| `special` | constructor | SelfAwareness |
| `FrobeniusType` | def | OntologicalTier |
| `frobeniusToOuroboricity` | def | tierToRank |
| `frobeniusToOuroboricity_strictMono` | theorem | tierToRank_strictMono |
| `no_tier_between_o1_and_o2` | theorem | no_tier_between_formation_and_actualization |
| `IsSpecial` | def | IsSelfKnowing |
| `c13_gap_is_one_frobenius_tier` | theorem | actualization_to_selfAwareness_gap_is_one |
| `full_not_special` | theorem | actualization_not_selfKnowing |
| `special_is_top` | theorem | selfAwareness_is_top |
| `leeYangFrobeniusType` | def | leeYangTier |
| `rhFrobeniusType` | def | riemannTier |
| `leeYang_strictly_above_rh` | theorem | leeYang_strictly_above_riemann |
| `leeYang_is_special` | theorem | leeYang_is_selfKnowing |
| `rh_is_not_special` | theorem | riemann_is_not_selfKnowing |
| `c13_gap_leyang_rh_is_one` | theorem | leeYang_riemann_gap_is_one |
| `ymFrobeniusType` | def | yangMillsTier |
| `nsFrobeniusType` | def | navierStokesTier |
| `rh_ym_ns_same_frobenius_type` | theorem | riemann_yangMills_navierStokes_same_tier |
| `schwingerFrobeniusType` | def | schwingerTier |
| `lerayFrobeniusType` | def | lerayTier |
| `proved_c12_templates_are_full` | theorem | proved_templates_are_actualized |
| `IsSelfGrounding` | def | IsSelfSubsisting |
| `algebraOnly_not_selfGrounding` | theorem | formation_not_selfSubsisting |
| `full_selfGrounding` | theorem | actualization_is_selfSubsisting |
| `special_selfGrounding` | theorem | selfAwareness_is_selfSubsisting |
| `o2_is_minimum_selfGrounding` | theorem | actualization_is_minimum_selfSubsisting |
| `selfGrounding_iff` | theorem | selfSubsisting_iff |
| `exactly_two_selfGrounding_types` | theorem | exactly_two_selfSubsisting_tiers |

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

### Target Statement (reality)

```
theorem exactly_two_selfSubsisting_tiers :
    (Finset.univ (α := OntologicalTier)).filter IsSelfSubsisting =
    {OntologicalTier.Actualization, OntologicalTier.SelfAwareness} := by
  ext t
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
             Finset.mem_insert, Finset.mem_singleton, selfSubsisting_iff]
```
