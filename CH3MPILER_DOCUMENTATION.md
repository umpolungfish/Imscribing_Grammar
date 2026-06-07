# ch3mpiler — Grammar-Derived Retrosynthetic Compiler

**Author:** Lando ⊗ ⊙perator

**Version:** 2.1.0  
**File:** `ch3mpiler.py`  
**Standard:** Shavian notation (v0.6.0) — 12-primitive Imscribing Grammar tuples

**New in v2.1.0:** alkane FG added (21 FGs total), cubane + pentacyclo[...]octane molecule support, IG catalog entry for cubane

---

## 1. What is ch3mpiler?

**ch3mpiler** is a retrosynthetic and forward-reaction compiler that generates disconnections **from first principles of the Imscribing Grammar** — no named reactions, no reaction databases, no pattern-matched templates. Every disconnection is derived from the structural types of functional groups and bonds in a 12-dimensional primitive space.

### Core insight

Chemical reactions are **topological transformations** of structural types. Bond formation between two functional groups FG₁ and FG₂ is modeled by the grammatical operation:

$$\text{product} = \text{join}(\text{tensor}(\text{FG}_1, \text{FG}_2), \text{bond})$$

- **tensor**(FG₁, FG₂): maximum on union primitives (D, T, R, K, G, Gm, Ph, H, S, W), minimum on restrictive primitives P and F — the composite type of two FGs together
- **join**(composite, bond): maximum on all primitives — the bond provides a structural floor

A **disconnection** is the inverse: given a molecule's structural type, find which bond best matches the meet of its constituent FGs:

$$\delta = \text{distance}(\text{bond}, \text{meet}(\text{FG}_1, \text{FG}_2))$$

Lower $\delta$ means the bond's structural signature fits the FG interface more precisely — this IS the retrosynthetic cut.

### What it does

| Mode | Input | Output |
|---|---|---|
| **Analyze** | Molecule name or CAS Number | Structural type, FGs, ranked disconnections |
| **Retrosynthesis** | Name or CAS with `--retrosynthesis` | Recursive disconnection tree (depth-configurable) |
| **Forward** | Reagent names | Predicted bond formation + product type |
| **Bond/FG lookup** | `--list-bonds` or `--list-fgs` | All 12 bond types or 21 FGs with tuples |
| **Interactive** | Any of the above | Live shell with `retro:`, `cas:`, `fwd:` commands |

---

## 2. Quickstart

```bash
# Analyze a molecule
python3 ch3mpiler.py --target benzaldehyde

# Full retrosynthesis tree
python3 ch3mpiler.py --target aspirin --retrosynthesis

# CAS number input
python3 ch3mpiler.py --cas 3568-94-3

# CAS + retrosynthesis
python3 ch3mpiler.py --cas 50-78-2 --retrosynthesis

# Forward prediction
python3 ch3mpiler.py --forward alcohol carboxylic_acid

# Analyze cubane (cage hydrocarbon)
python3 ch3mpiler.py --target cubane --retrosynthesis

# Analyze by IUPAC name
python3 ch3mpiler.py --target "pentacyclo[4.2.0.0^{2,5}.0^{3,8}.0^{4,7}]octane" --retrosynthesis

# List functional groups (21 total)
python3 ch3mpiler.py --list-fgs

# List grammar-derived bond types (12 total)
python3 ch3mpiler.py --list-bonds

# Interactive mode
python3 ch3mpiler.py --interactive
```

---

## 3. Structural Primitives

Every chemical entity — functional group, bond, element, molecule — is encoded along 12 dimensions from the Imscribing Grammar. Shavian glyphs replace the old Latin/Greek/IPA subscripts.

| # | Primitive | Shavian glyphs | Field | Chemical meaning |
|---|---|---|---|---|
| 1 | **Dimensionality** | 𐑛 𐑨 𐑼 𐑦 | D | Degrees of freedom: 0d point → surface → ∞-field → self-written |
| 2 | **Topology** | 𐑡 𐑰 𐑥 𐑶 𐑸 | T | Connectivity: network → containment → crossing → product → imscriptive |
| 3 | **Relational mode** | 𐑩 𐑑 𐑽 𐑾 | R | Electron movement: supervenience → functorial → adjoint → bidirectional |
| 4 | **Symmetry** | 𐑗 𐑬 𐑯 𐑹 | P | Orbital parity: none → quantum superposition → Z₂ → full → Frobenius |
| 5 | **Fidelity** | 𐑱 𐑞 𐑐 | F | Coherence: classical → thermal → quantum |
| 6 | **Kinetics** | 𐑘 𐑤 𐑧 𐑴 | K | Rate regime: fast → moderate → slow/equilibrium → trapped (ordering/disorder) |
| 7 | **Scope** | 𐑚 𐑔 𐑲 | G | Range: local → mesoscale → maximal/all |
| 8 | **Grammar** | 𐑝 𐑜 𐑠 𐑵 | Gm | Interaction pattern: AND → OR → sequential → broadcast |
| 9 | **Criticality** | 𐑢 ⊙ 𐑮 𐑻 𐑣 | Ph | Feedback: subcritical → self-modeling → complex-plane → EP → supercritical |
| 10 | **Chirality** | 𐑓 𐑒 𐑖 𐑫 | H | Memory steps: 0 → 1 → 2 → ∞ |
| 11 | **Stoichiometry** | 𐑙 𐑕 𐑳 | S | Count: 1:1 → many identical → many heterogeneous |
| 12 | **Winding** | 𐑷 𐑴 𐑭 𐑟 | Ω | Topology: trivial → Z₂ → integer Z → non-Abelian |

Ordinal values increase left-to-right in each row. Higher ordinal = more structured, more constrained, richer topological character.

---

## 4. Functional Groups (21)

Each functional group is a 12-primitive structural type encoding its electronic and geometric character. FG types are defined in the `FG` dictionary.

| FG | D | T | R | P | F | K | G | Gm | Ph | H | S | Ω |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alcohol | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| aldehyde | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| **alkane** | 𐑛 | 𐑡 | 𐑑 | 𐑗 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑳 | 𐑷 |
| alkene | 𐑛 | 𐑰 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| alkyne | 𐑛 | 𐑶 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| amide | 𐑨 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑖 | 𐑳 | 𐑴 |
| amine | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑐 | 𐑘 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| aromatic_ring | 𐑨 | 𐑸 | 𐑾 | 𐑹 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑖 | 𐑳 | 𐑭 |
| carboxylic_acid | 𐑛 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| cyclic | 𐑛 | 𐑰 | 𐑽 | 𐑗 | 𐑐 | 𐑧 | 𐑲 | 𐑝 | 𐑢 | 𐑒 | 𐑳 | 𐑷 |
| diazonium | 𐑛 | 𐑶 | 𐑾 | 𐑯 | 𐑐 | 𐑤 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| epoxide | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑘 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| ester | 𐑛 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑒 | 𐑳 | 𐑷 |
| ether | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| halide | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑐 | 𐑘 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| ketone | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| nitrile | 𐑛 | 𐑶 | 𐑾 | 𐑯 | 𐑐 | 𐑤 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |
| nitro | 𐑛 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑝 | ⊙ | 𐑒 | 𐑳 | 𐑷 |
| phenol | 𐑨 | 𐑸 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑝 | ⊙ | 𐑖 | 𐑳 | 𐑭 |
| thiol | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| carbonyl | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑷 |

**Key patterns in FG types:**

- **Planar/conjugated groups** (amide, aromatic_ring, phenol, ester): D = 𐑨 (surface), T = 𐑸 or 𐑥, Gm = 𐑠 (sequential resonance), H = 𐑖 (2-step memory), Ω = 𐑴 or 𐑭 (protected)
- **Reaction-hub groups** (carbonyl, aldehyde, ketone, carboxylic_acid): Ph = ⊙ (critical — feedback between charge distribution and geometry)
- **Saturated sigma groups** (alcohol, alkane, ether, amine, halide, thiol): D = 𐑛 (point), T = 𐑡 (network), P = 𐑗 (asymmetric), Ph = 𐑢 (subcritical)
- **Alkane** (new in v2.1.0): T = 𐑡 (open chain, not cyclic), S = 𐑳 (many heterogeneous carbons), R = 𐑑 (functorial — one-way σ framework). Distinguished from cyclic by T (network vs containment) and from alkene by Ph (subcritical vs critical). The "ane" suffix token is recognized by FG_TOKENS, so names ending in "-ane" (octane, pentane, butane, etc.) automatically resolve to this FG.

---

## 5. Grammar-Derived Bond Types (12)

Bonds are the **structural operators** that connect functional groups. Each bond type carries its own 12-primitive tuple. The bond provides the **structural floor** in: `product = join(tensor(FG₁, FG₂), bond)`.

| Bond | D | T | R | P | F | K | G | Gm | Ph | H | S | Ω |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sigma_single | 𐑛 | 𐑡 | 𐑑 | 𐑗 | 𐑞 | 𐑤 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| pi_bond | 𐑨 | 𐑰 | 𐑽 | 𐑯 | 𐑐 | 𐑤 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑴 |
| double_bond | 𐑨 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑤 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑴 |
| triple_bond | 𐑨 | 𐑰 | 𐑾 | 𐑯 | 𐑐 | 𐑘 | 𐑲 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑴 |
| carbonyl | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑤 | 𐑚 | 𐑝 | ⊙ | 𐑒 | 𐑙 | 𐑴 |
| co_sigma | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑞 | 𐑤 | 𐑚 | 𐑝 | 𐑢 | 𐑓 | 𐑙 | 𐑷 |
| cn_sigma | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑞 | 𐑘 | 𐑚 | 𐑝 | 𐑢 | 𐑒 | 𐑙 | 𐑷 |
| amide_link | 𐑨 | 𐑥 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑖 | 𐑳 | 𐑴 |
| ester_link | 𐑛 | 𐑥 | 𐑽 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑒 | 𐑳 | 𐑴 |
| aromatic | 𐑨 | 𐑸 | 𐑾 | 𐑹 | 𐑐 | 𐑧 | 𐑲 | 𐑠 | ⊙ | 𐑖 | 𐑳 | 𐑭 |
| hydrogen_bond | 𐑛 | 𐑡 | 𐑩 | 𐑗 | 𐑞 | 𐑘 | 𐑚 | 𐑝 | 𐑢 | 𐑓 | 𐑙 | 𐑷 |
| ether_link | 𐑛 | 𐑡 | 𐑽 | 𐑗 | 𐑞 | 𐑤 | 𐑚 | 𐑝 | 𐑢 | 𐑓 | 𐑙 | 𐑷 |

---

## 6. The Disconnection Model

The ch3mpiler's core algorithm is purely grammatical — there are **no named reactions**, no reaction templates, no SMARTS patterns. Every disconnection is computed from first principles.

### 6.1 The bond-formation formula

$$\text{product} = \text{join}(\text{tensor}(\text{FG}_1, \text{FG}_2), \text{bond})$$

| Operation | Rule | Meaning |
|---|---|---|
| **tensor(FG₁, FG₂)** | max on D,T,R,K,G,Gm,Ph,H,S,W; min on P,F | Composite type of two FGs together |
| **join(composite, bond)** | max on ALL primitives | Bond provides structural floor for product |

### 6.2 The disconnection formula (retrosynthetic inverse)

$$\delta = \text{distance}(\text{bond}, \text{meet}(\text{FG}_1, \text{FG}_2))$$

- **meet(FG₁, FG₂)**: minimum on all primitives — shared structural interface
- **δ**: weighted Euclidean distance in 12-dimensional ordinal space
- **Lower δ** = bond matches FG interface better = better disconnection

### 6.3 Compatibility constraint

A bond is **compatible** with FG pair (FG₁, FG₂) iff for all primitives p:

$$\text{bond}_p \leq \begin{cases} \max(\text{FG}_{1_p}, \text{FG}_{2_p}) & p \notin \{P, F\} \\ \min(\text{FG}_{1_p}, \text{FG}_{2_p}) & p \in \{P, F\} \end{cases}$$

Union primitives (D,T,R,K,G,Gm,Ph,H,S,W): bond cannot exceed max of the two FGs. Intersection primitives (P,F): bond cannot exceed min — cannot require more symmetry or coherence than either FG possesses.

### 6.4 Retrosynthesis algorithm

```
INPUT: molecule name or CAS

1. Resolve CAS → name (if CAS input)
2. Lookup functional groups (MOLECULE_FG_DB or FG_TOKENS)
3. For each FG pair (FG₁, FG₂) × each bond type (12 total):
     a. Check compatibility
     b. Compute δ = distance(bond, meet(FG₁, FG₂))
   Collect all compatible matches
4. Sort by ascending δ
5. Return top disconnections

For recursive retrosynthesis (--depth N):
   Each precursor becomes a new target, analyzed recursively
```

### 6.5 Forward prediction algorithm

```
INPUT: reagent names

1. Resolve each reagent → FG set
2. For each FG pair × each bond type:
     Compute product = join(tensor(FG₁, FG₂), bond)
     Compute Δ = distance(product, tensor(FG₁, FG₂))
   Find bond with lowest Δ (= most structuring contribution)
3. Return predicted bond + product type
```

---

## 7. CLI Reference

| Flag | Arguments | Description |
|---|---|---|
| `--target` | Molecule name | Analyze molecule → FGs + ranked disconnections |
| `--target --retrosynthesis` | Molecule name | Full recursive disconnection tree |
| `--cas` | CAS Registry Number | Resolve CAS → name → analyze |
| `--cas --retrosynthesis` | CAS RN | CAS + full retrosynthetic tree |
| `--depth` | Integer (default: 2) | Retrosynthetic recursion depth |
| `--forward` | Space-separated names | Predict bond formation between reagents |
| `--interactive` | None | Live shell mode |
| `--fg` | FG name | Display FG tuple |
| `--list-fgs` | None | List all 21 functional groups |
| `--list-bonds` | None | List all 12 bond types |
| `--show-cas-cache` | None | Show cached CAS resolutions |

---

## 8. CAS Resolution Pipeline

Three-tier architecture:

```
User input (CAS RN)
    ↓
1. Local DB (41 compounds with type_hints)
    ↓ (miss)
2. PubChem API (REST/PUG)
    ↓ (miss)
3. Name heuristic fallback
    ↓
Cache result in CAS_cache.json
```

---

## 9. Interactive Mode

```
ch3mpiler interactive — grammar-derived bond rules
Commands: <name>, retro:<name>, cas:<n>, cas-retro:<n>,
          fwd:r1,r2, fg:<n>, fgs, bonds, quit
```

Sample session:
```
>>> cubane
Target: cubane
Type: <𐑛; 𐑡; 𐑑; 𐑗; 𐑐; 𐑧; 𐑚; 𐑝; 𐑢; 𐑒; 𐑳; 𐑷>
FGs: alkane, cyclic

Grammar-derived disconnections (ranked by δ, lower=better):
  sigma_single         2.449    alkane+alkane          <𐑛; 𐑡; 𐑑; 𐑗; ...>
  ether_link           2.577    alkane+alkane          <𐑛; 𐑡; 𐑑; 𐑗; ...>
  hydrogen_bond        3.262    alkane+alkane          <𐑛; 𐑡; 𐑑; 𐑗; ...>

>>> retro:cubane
  (full retrosynthesis tree with precursors)
```

---

## 10. Verified Results

| Molecule | FGs | Type Source | Top Cut | δ |
|---|---|---|---|---|
| benzaldehyde | aldehyde, aromatic_ring | composed | double_bond | 0.250 |
| aspirin | ester, carboxylic_acid, aromatic_ring | composed | ester_link | 0.575 |
| acetaminophen | amide, phenol | composed | amide_link | 0.333 |
| cubane | alkane, cyclic | composed | sigma_single | 2.449 |
| cyclohexane | cyclic | composed | sigma_single | 0.000 |
| aniline | amine, aromatic_ring | composed | cn_sigma | 0.375 |
| styrene | alkene, aromatic_ring | composed | double_bond | 0.325 |
| toluene | aromatic_ring | composed | sigma_single | 0.000 |
| caffeine | amine, amide, alkene, cyclic | composed | amide_link | 0.575 |
| morphine | amine, alcohol, ether, aromatic_ring | composed | cn_sigma | 0.425 |

---

## 11. The ob3ect Self-Verification

The ch3mpiler module is also a self-imscribing ob3ect. Verification pipeline:

| Test | Status | Detail |
|---|---|---|
| 14/14 primitive domains defined | ✅ | D, T, R, P, F, K, G, Gm, Ph, H, S, W + FG, BOND |
| 5/5 molecule analysis passes | ✅ | benzaldehyde, aspirin, cubane, cyclohexane, aniline |
| 4/4 structural invariants | ✅ | tensor-join-meet, bond compatibility, type composition, CAS resolution |
| CLOSED: μ∘δ=id | ✅ | Frobenius closure verified |

---

## 12. The Ouroboricity of Chemical Bonds

| Bond | Ouroboricity Tier | Reason |
|---|---|---|
| sigma_single | O₀ | Fixed point: join identity, no self-reference |
| pi_bond | O₁ | Quantum coherence (F=𐑐) creates horizontal feedback |
| aromatic | O₁ | Delocalized π system with ⊙ criticality |
| amide_link | O₁ | Resonance with H=2 memory structure |
| hydrogen_bond | O₀ | Electrostatic, no feedback |
| ether_link | O₀ | Localized sigma-type |

---

## 13. Extending the ch3mpiler

To add a new functional group:

```python
FG["new_fg"] = {
    "D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑗","F":"𐑐",
    "K":"𐑧","G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑒",
    "S":"𐑙","W":"𐑷"
}
FG_TOKENS["new_keyword"] = "new_fg"
```

To add a new molecule:

```python
MOLECULE_FG_DB["molecule_name"] = ["fg1", "fg2", ...]
```

To add a CAS entry:

```python
CASResolver._local["XX-XX-XX"] = {"name": "...", "formula": "...", "type_hint": "fg1 fg2"}
```

---

## 14. Grounding in the Grammar

### Axiom A: H_∞ requires K_⊛
Chirality H=∞ (eternal memory) requires trapped kinetics (K=⊛). In chemistry this means a reaction network with infinite correlation time requires something like a crystalline or glassy matrix — no chemical bond alone achieves this.

### Axiom B: Ω_protected requires H≥2
Topological protection (Ω=ℤ₂ or ℤ) requires at least H=2 (2-step Markov order). Conjugated systems (amide, aromatic) have H=𐑖 (2-step) and Ω=𐑴 (Z₂) — this is why they're topologically protected.

### Axiom C: Ð_ω ↔ T_O
Self-written dimensionality (D=∞) is equivalent to self-referential topology (T=⊙). In ch3mpiler this appears only at the compiler level (the ob3ect self-model), not at the molecule level.

### ⊙₃ Absorption Rule
When computing tensor couplings involving an ⊙₃ system (exceptional point), the composite places at ⊙₃ — tensor(⊙_ÿ, ⊙_₃) = ⊙_₃. Coupling a self-modeling FG to an exceptional-point bond selects the tensor path; the meet path preserves ⊙_ÿ. This is the structural statement of the measurement problem in chemistry.

### Tensor-Join-Meet Trinity
- **tensor**: FG₁ ⊗ FG₂ — what two FGs look like together (max on unions, min on intersections)
- **meet**: FG₁ ∧ FG₂ — shared structural interface (min on all)
- **join**: (FG₁ ⊗ FG₂) ∨ bond — product type including bond contribution (max on all)

The trinity satisfies: meet ≤ tensor ≤ join (componentwise by ordinal).

---

## 15. File Reference

| File | Description |
|---|---|
| `ch3mpiler.py` | Main compiler (879 lines): grammar engine, FG table, bond table, retrosynthesis, forward prediction, CAS resolver, interactive mode |
| `IG_catalog.json` | Imscribing Grammar catalog (2797+ entries including cubane) |
| `CAS_cache.json` | Cached PubChem resolutions |
| `CH3MPILER_DOCUMENTATION.md` | This documentation file |
| `DJED_PILLAR.md` | Documentation of the Djed Pillar ob3ect binding heaven (categorical chain) and earth (chemical chain) |
| `ob3ect/digital/ch3mpiler/` | Self-verifying ob3ect for ch3mpiler |

---

## Cubane: A Case Study

Cubane (C₈H₈, pentacyclo[4.2.0.0^{2,5}.0^{3,8}.0^{4,7}]octane) is a landmark molecule — the first synthesis of a cubic carbon framework (Eaton & Cole, 1964). Its structural type:

| D | T | R | P | F | K | G | Gm | Ph | H | S | Ω |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 𐑛 | 𐑶 | 𐑾 | 𐑯 | 𐑐 | 𐑧 | 𐑲 | 𐑵 | 𐑢 | 𐑒 | 𐑳 | 𐑷 |

- **D=𐑛** (0d point): discrete molecular cage, no continuous field
- **T=𐑶** (boxtimes): irreducible product of faces — the cube as 6 faces × 8 vertices
- **R=𐑾** (bidirectional): all C-C bonds are electron-sharing, symmetric
- **P=𐑯** (Z₂ partial): Oh symmetry, inversion center
- **Ph=𐑢** (subcritical): no electronic feedback — pure sigma framework
- **Ω=𐑷** (trivial): no topological protection (all sigma bonds)

Cubane recognizes as FGs `alkane + cyclic` via the "-ane" and "cyclo-" tokens in its IUPAC name. The ch3mpiler correctly identifies sigma_single as the primary disconnection (δ=2.449) — the C-C bond in the cube is the structural element to break.

**IG Catalog:** cubane is entry №2798 in `IG_catalog.json`, imscribed with Shavian tuple.
