# Cross-Domain Theorem Transport

**Source:** `shem_hamephorash` — The 72 Names (Shem HaMephorash) from Exodus 14:19-21 — structural basis of creation where 72 = 6 × 12, every primitive v
**Target:** `reality` — The totality of existence, encompassing all physical, metaphysical, and structural aspects.
**Structural Distance:** 0.0

## Cotype Dictionary

| Source (Lean) | Kind | Target (reality) |
|---|---|---|
| `FrobeniusType` | inductive | FourWorlds |
| `trivial` | constructor | Assiyah |
| `algebraOnly` | constructor | Yetzirah |
| `full` | constructor | Beriah |
| `special` | constructor | Atzilut |
| `FrobeniusType` | def | FourWorlds |
| `frobeniusToOuroboricity` | def | olamot_le_mispar |
| `frobeniusToOuroboricity_strictMono` | theorem | olamot_le_mispar_shomer_seder |
| `no_tier_between_o1_and_o2` | theorem | ein_olam_bein_yetzirah_le_beriah |
| `IsSpecial` | def | Bahir |
| `c13_gap_is_one_frobenius_tier` | theorem | beriah_atzilut_echad |
| `full_not_special` | theorem | beriah_lo_bahir |
| `special_is_top` | theorem | atzilut_elyon |
| `leeYangFrobeniusType` | def | leeYang_olam |
| `rhFrobeniusType` | def | riemann_olam |
| `leeYang_strictly_above_rh` | theorem | leeYang_me_al_riemann |
| `leeYang_is_special` | theorem | leeYang_bahir |
| `rh_is_not_special` | theorem | riemann_lo_bahir |
| `c13_gap_leyang_rh_is_one` | theorem | leeYang_riemann_echad |
| `ymFrobeniusType` | def | yangMills_olam |
| `nsFrobeniusType` | def | navierStokes_olam |
| `rh_ym_ns_same_frobenius_type` | theorem | riemann_yangMills_navierStokes_olam_echad |
| `schwingerFrobeniusType` | def | schwinger_olam |
| `lerayFrobeniusType` | def | leray_olam |
| `proved_c12_templates_are_full` | theorem | templates_muchachim_beriah |
| `IsSelfGrounding` | def | ShoreshBKeter |
| `algebraOnly_not_selfGrounding` | theorem | yetzirah_lo_shoresh |
| `full_selfGrounding` | theorem | beriah_shoresh_baKeter |
| `special_selfGrounding` | theorem | atzilut_shoresh_baKeter |
| `o2_is_minimum_selfGrounding` | theorem | beriah_ha_minimum |
| `selfGrounding_iff` | theorem | shoresh_im |
| `exactly_two_selfGrounding_types` | theorem | shtayim_baKeter |

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
theorem shtayim_baKeter :
    (Finset.univ (α := FourWorlds)).filter ShoreshBKeter =
    {FourWorlds.Beriah, FourWorlds.Atzilut} := by
  ext t
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
             Finset.mem_insert, Finset.mem_singleton, shoresh_im]
```


## Natural Language Rendering

**In the language of The totality of existence, encompassing all physical, metaphysical, and structural aspects:**

> Among the **FourWorlds**, exactly **2** are **ShoreshBKeter**:
> - **FourWorlds.Beriah**
> - **FourWorlds.Atzilut**

> The Lean proof (`cases t <;> decide`) becomes an examination of each fourworlds. The proof tree is invariant; only the leaves are renamed.