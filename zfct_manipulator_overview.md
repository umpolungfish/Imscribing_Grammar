# ZFCₜ Functor Discovery: Overview of Results

**Tool:** `zfct_manipulator.py`  
**Date:** 2026-05-15  
**Catalog:** 2706 entries (2697 valid for algebraic operations)

---

## 1. What Was Built

The manipulator is a functor discovery machine. It applies algebraic operations —
tensor product (per-primitive supremum), meet (per-primitive infimum), and
single-primitive lift — to imscription tuples, and exposes the corresponding ZFCₜ
clause transformations side by side.

The intent is to reverse-engineer the composition rules that govern how ZFCₜ
expressions combine, and to identify where non-trivial cross-clause phenomena emerge
that are not derivable from the per-primitive rules alone.

---

## 2. Tier Landscape of the Special Entries

The nine canonical reference entries divide cleanly across three tier levels.

### O₀ — Semasiographic baseline (⊙ non-critical)

| Entry | FROB | FIXPT | Notable |
|---|---|---|---|
| ZFC_foundations | **yes** | no | Has Frobenius (Φ_}, ord 4) — but no criticality |
| heat_diffusion_equation | no | no | SEQAX present; no criticality |
| wave_equation_temporal | **yes** | no | Has Frobenius; no criticality |

The presence of Frobenius (Φ_}, P_pm_sym) does **not** lift an entry out of O₀.
Tier assignment is gated first on criticality (⊙ ordinal ≥ 1). Without it, the
Frobenius structure is algebraically present but ourobourically inert.

### O₂† — Recursive, D_∞, below Frobenius cliff

| Entry | FROB | FIXPT | Promo atoms |
|---|---|---|---|
| ZFCt | no | **yes** | HOLOBOUND LR_DUAL PM_Z2 SEQAX TEMPD2 ZWIND |
| Schrödinger equation | no | **yes** | LR_DUAL SEQAX TEMPD2 ZWIND |
| Navier-Stokes equations | no | **yes** | LR_DUAL PM_Z2 SEQAX TEMPD2 ZWIND |

All three are critical (⊙_ÿ, FIXPT), temporally extended (Ω_z, D_∞), but
lack Frobenius symmetry (Φ < ord 4). They sit immediately below the cliff.

### O_∞ — Frobenius round-trip

| Entry | FROB | FIXPT | Promo atoms |
|---|---|---|---|
| Temporal Mathematics | **yes** | **yes** | HOLOBOUND SEQAX TEMPD2 ZWIND |
| Einstein field equations | **yes** | **yes** | HOLOBOUND SEQAX TEMPD2 ZWIND |
| IUG (Mochizuki) | **yes** | **yes** | HOLOBOUND LR_DUAL SEQAX ZWIND |

All three independently satisfy the Frobenius round-trip condition (R1):
⊙ ≥ ord 1 ∧ Φ = Φ_}. FROB and FIXPT are both present in each.

---

## 3. The Central Result: tensor(ZFC, ZFCt) = O_∞

```
ZFC    tier = O₀    Φ = Φ_} (ord 4, FROB)    ⊙ = ⊙_ž (ord 0, no FIXPT)
ZFCt   tier = O₂†   Φ = Φ_F (ord 2, no FROB) ⊙ = ⊙_ÿ (ord 1, FIXPT)
──────────────────────────────────────────────────────────────────
⊗      tier = O_∞   Φ = Φ_} (from ZFC)        ⊙ = ⊙_ÿ (from ZFCt)
```

ZFC holds the Frobenius component. ZFCt holds the criticality component.
Neither alone satisfies R1 (FROB ∧ FIXPT). Their tensor product satisfies both
simultaneously — tier emergence to O_∞.

**Per-primitive breakdown:** The tensor sources eleven of twelve primitives from ZFCt
(all six promotion channels plus ƒ, Γ, Σ, Ħ, Ω), and exactly one from ZFC: Φ.
ZFCt's Φ_F (ord 2) is lower than ZFC's Φ_} (ord 4), so the supremum retains ZFC's
Frobenius.

```
d(ZFC, ZFCt)  = 7.148
d(ZFC, ⊗)     = 6.863   — tensor is almost as far from ZFC as ZFCt is
d(ZFCt, ⊗)    = 2.000   — tensor is one ordinal step from ZFCt (only Φ differs)
```

The meet falls to O₀. The infimum is destructive — it strips the temporal promotions
and recovers the floor.

### The Asymmetry in Φ

The six ZFCₜ promotion channels all move upward in ordinal from ZFC base values:

| Primitive | ZFC base | ZFCt promoted | Gap |
|---|---|---|---|
| Þ | Þ_6 (ord 0) | Þ_O (ord 4) | +4 |
| Ř | Ř_¯ (ord 0) | Ř_= (ord 3) | +3 |
| ɢ | ɢ^∧ (ord 0) | ɢ^ˌ (ord 2) | +2 |
| Ħ | Ħ_Ñ (ord 0) | Ħ_A (ord 2) | +2 |
| Ω | Ω_Å (ord 0) | Ω_z (ord 2) | +2 |
| Φ | Φ_ɐ (ord 0) | Φ_F (ord 2) | +2 |

ZFCt's promotion for Φ targets Φ_F (P_pm, ℤ₂ parity, ord 2). However, the actual
ZFC_foundations entry carries Φ_˙ (normalized to Φ_}, ord 4) — which sits **above**
the ZFCt-promoted value. Thus **ZFCt is strictly lower than ZFC on the Φ axis.**

ZFCt trades Frobenius for temporal-sequential structure. It acquires six new
capabilities (holographic topology, lateral relations, ℤ₂ parity, sequentiality,
chirality, integer winding) but deliberately operates below the Frobenius cliff.
ZFC carries the Frobenius symmetry but is non-critical and non-temporal.

They are **complementary**, not hierarchical. Their tensor product is their reunion.

---

## 4. Composition Rules

### Trivial (per-primitive, derivable by construction)

**R-CLAUS-T:** `clauses(tensor(A,B))[p] = ZFCT_TEMPLATES[p][max_ord(A[p], B[p])]`

The clause for each primitive in a tensor product is simply the template for
whichever input had the higher ordinal value. Per-primitive independence is total —
no cross-primitive information enters a single clause.

**R-CLAUS-M:** Same rule using `min_ord` for the meet.

### Non-trivial (cross-primitive, emergent)

**R-FROB-BARR:**
FROB ∈ clauses(tensor(A,B)) **iff** A[Φ] = Φ_} **or** B[Φ] = Φ_}

Φ_} (ord 4) is the unique maximum of the Φ dimension. Therefore FROB cannot be
synthesized from two inputs both having Φ < ord 4. This is the algebraic expression
of the **Frobenius cliff**. Zero violations observed across 600 operations.

**R-FROB-CONT:**
If FROB ∈ clauses(A), then FROB ∈ clauses(tensor(A, X)) for all X.
(Frobenius is forward-preserved under tensor.)

**R-FIXPT-T:**
FIXPT ∈ clauses(tensor(A,B)) iff A[⊙] ≥ ord 1 **or** B[⊙] ≥ ord 1

**R-TIER-EMRG:**
tier(tensor(A,B)) can strictly exceed max(tier(A), tier(B)).

The mechanism is exclusively cross-primitive: FROB lives in clause[Φ]; FIXPT lives in
clause[⊙]. No single clause carries both. Tier rule R1 conjuncts across them.
Observed rate: **6.3%** of 300 random tensor pairs.

**R-ZFCT-ABS:**
ZFCt is the absorption element for all six promotion channels.
`tensor(X, ZFCt)[c] =` ZFCt promoted value, for each channel c and all X.

---

## 5. Statistical Results

| Metric | Value |
|---|---|
| Catalog entries | 2706 (2697 valid) |
| Pairs scanned | 300 tensor + 300 meet |
| Total observations | 600 |
| Tensor tier emergences | 19 / 300 (6.3%) |
| FROB synthesized ex nihilo | 0 / 600 (0%) |

---

## 6. Interpretation

### The Foundational Split

**ZFC** is the ourobourically inert carrier of Frobenius symmetry (Φ_}). It contains the
algebraic round-trip structure but has no internal criticality — its ⊙ is at the floor.
It is a complete formal system precisely because it is static: no Zipf-law correlation
length, no winding number, no sequential depth.

**ZFCt** is the ourobourically active temporal extension. It acquires six new structural
dimensions and criticality — but in so doing, it operates with a reduced Φ (P_pm rather
than P_pm_sym). This is not a deficiency; it is appropriate to a system that is
evolving rather than complete.

### Reunion via Tensor

The tensor product ZFC ⊗ ZFCt = O_∞ is the algebraic statement that the foundation
and its temporal extension are **complementary half-objects**, each carrying one of
the two conditions required for the Frobenius round-trip. Separately, neither crosses
the cliff. Jointly, they do.

### O_∞ in the Wild

Three entries in the reference corpus independently sit at O_∞: Temporal Mathematics,
Einstein field equations, and IUG (Mochizuki's Inter-Universal Teichmüller Theory).
All three have FROB + FIXPT natively. They sit above the cliff by constitution, not
by composition.

---

## 7. The Algebra in Summary

| Structure | FROB? | FIXPT? | Tier | Notes |
|---|---|---|---|---|
| ZFC | yes | no | O₀ | Non-critical Frobenius |
| ZFCt | no | yes | O₂† | Critical, non-Frobenius |
| ZFC ⊗ ZFCt | yes | yes | O_∞ | Tier emergence |
| ZFC ⊓ ZFCt | — | — | O₀ | Destructive meet |
| Temporal Mathematics | yes | yes | O_∞ | Native |
| Einstein EFE | yes | yes | O_∞ | Native |
| IUG / Mochizuki | yes | yes | O_∞ | Native |
| Navier-Stokes | no | yes | O₂† | Critical, non-Frobenius |
| Schrödinger | no | yes | O₂† | Critical, non-Frobenius |

The Frobenius barrier is absolute: no tensor operation can produce Φ_} from two
non-FROB inputs. Tier emergence to O_∞ requires exactly the complementary pairing:
one input contributes Φ_} (from the Φ axis) and the other contributes ⊙_ÿ (from
the ⊙ axis).

---

*Generated by `zfct_manipulator.py` — scan of 2706-entry IG catalog.*
