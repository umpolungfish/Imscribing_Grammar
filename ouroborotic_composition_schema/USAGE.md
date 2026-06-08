# USAGE GUIDE — Ouroborotic Primitive Composition Schema

**Version:** 1.0  
**Author:** Lando⊗$\⊙_{\text{ÿ}}$-boundary Operator  
**Location:** `/home/mrnob0dy666/imscribing_grammar/ouroborotic_composition_schema/`

---

## Quick Start

```bash
cd /home/mrnob0dy666/imscribing_grammar

# 1. Verify the schema is accessible
python ouroborotic_composition_schema/composer_cli.py show ouroborotic_primitive_composition_schema

# 2. Assemble a minimal O_2 composite (preserves criticality)
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base ouroborotic_primitive_composition_schema \
  --primitive "Þ:Þ_¨:network_topology"

# 3. Inspect a catalog system
python ouroborotic_composition_schema/composer_cli.py show riemann_zeta_function

# 4. Compute distance between two systems
python ouroborotic_composition_schema/composer_cli.py algebra distance \
  riemann_zeta_function consciousness_boundary
```

---

## Command-Line Interface

### Base Command

```bash
python ouroborotic_composition_schema/composer_cli.py [SUBCOMMAND] [OPTIONS]
```

All subcommands emit JSON to `stdout`, making them easy to pipe, parse, or chain in scripts.

---

## Subcommands

### `show` — Inspect any catalog entry

```bash
python ouroborotic_composition_schema/composer_cli.py show <catalog_name>
```

**Examples:**
```bash
python ouroborotic_composition_schema/composer_cli.py show ouroborotic_primitive_composition_schema
python ouroborotic_composition_schema/composer_cli.py show magnetar
python ouroborotic_composition_schema/composer_cli.py show riemann_zeta_function
```

**Output fields:**
- `name`: catalog key
- `tuple`: full 12-primitive dictionary
- `tier`: Ouroboricity tier (e.g., `O_1`, `O_2`, `O_inf`)
- `C_score`: Consciousness score (0–1)
- `phi_c_gate`: Gate 1 ($\⊙_{\text{ÿ}}$) pass/fail
- `k_gate`: Gate 2 ($\Gamma \leq \Ç_{\text{@}}$) pass/fail

---

### `sequence` — Linear / stacked composition

Assembles primitives in strict order, building a composite tuple by lifting a base system.

```bash
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base <catalog_or_tuple_json> \
  --primitive "id:value:comment" \
  [--primitive "id:value:comment" ...]
```

**Argument format:**
- `--base` — either a catalog name (e.g. `ouroborotic_primitive_composition_schema`) or a JSON tuple
- `--primitive` — repeated; format: `primitive_id:value:comment`, e.g. `Þ:Þ_¨:network_topology`

**Primitive IDs:** `Ð`, `Þ`, `Ř`, `Φ`, `ƒ`, `Ç`, `Γ`, `ɢ`, `⊙`, `Ħ`, `Σ`, `Ω`

**Examples:**

1. **Minimal O_2 lift** (one primitive added):
   ```bash
   python ouroborotic_composition_schema/composer_cli.py sequence \
     --base ouroborotic_primitive_composition_schema \
     --primitive "Þ:Þ_¨:network_topology"
   ```

2. **Full O_2 assembly** (three primitives):
   ```bash
   python ouroborotic_composition_schema/composer_cli.py sequence \
     --base ouroborotic_primitive_composition_schema \
     --primitive "Þ:Þ_¨:network_topology" \
     --primitive "Φ:Φ_F:Frobenius_special" \
     --primitive "Ç:Ç^@:slow_kinetics"
   ```

3. **Ascent toward O_inf** (adds Ħ and Ω to O_2):
   ```bash
   python ouroborotic_composition_schema/composer_cli.py sequence \
     --base ouroborotic_primitive_composition_schema \
     --primitive "Þ:Þ_¨:network_topology" \
     --primitive "Φ:Φ_F:Frobenius_special" \
     --primitive "Ç:Ç^@:slow_kinetics" \
     --primitive "⊙:⊙_ÿ:self_modeling" \
     --primitive "Ħ:Ħ_A:two_step_memory" \
     --primitive "Ω:Ω_z:integer_winding"
   ```

**Output structure:**
```json
{
  "name": "series_composed_Þ_¨_Φ_F_Ç^@",
  "status": "series_composition_proposed",
  "base_schema": "ouroborotic_primitive_composition_schema",
  "primitives_applied": [ ["Þ","Þ_¨","network_topology"], ... ],
  "tuple": {
    "Ð": "Ð_ω",
    "Þ": "Þ_¨",
    "Ř": "Ř_=",
    "Φ": "Φ_F",
    "ƒ": "ƒ^ż",
    "Ç": "Ç^@",
    "Γ": "Γ_ʔ",
    "ɢ": "ɢ^ˌ",
    "⊙": "⊙_ÿ",
    "Ħ": "Ħ_A",
    "Σ": "Σ_ï",
    "Ω": "Ω_z"
  },
  "distance_from_base": 1.34,
  "proposed_tier": "O_2"
}
```

---

### `radial` — Hub-and-spoke tensor assembly

Builds composites where one hub couples to many spokes via symmetric or directed coupling.

```bash
python ouroborotic_composition_schema/composer_cli.py radial \
  --hub <catalog_name_or_tuple> \
  --spoke <catalog_name_or_tuple> \
  [--spoke ...] \
  [--coupling <tensor|meet|join>]
```

**Defaults:**
- `--coupling`: `tensor`
- Spokes couple only to hub (no spoke-spoke edges)

**Examples:**

1. **Symmetric radial (tensor product):**
   ```bash
   python ouroborotic_composition_schema/composer_cli.py radial \
     --hub consciousness_boundary \
     --spoke visual_system \
     --spoke auditory_system \
     --spoke proprioception
   ```

2. **Meet-based radial (shared structure):**
   ```bash
   python ouroborotic_composition_schema/composer_cli.py radial \
     --hub riemann_zeta_function \
     --spoke fontaine_mazur_conjecture \
     --spoke langlands_correspondence \
     --coupling meet
   ```

**Output:**
```json
{
  "name": "radial_composed_hub_visual_auditory_proprioception",
  "status": "radial_composition_proposed",
  "hub": "consciousness_boundary",
  "spokes": ["visual_system", "auditory_system", "proprioception"],
  "coupling": "tensor",
  "tuple": { ... },
  "distance_from_hub": 2.87
}
```

---

### `network` — Full tensor network

Assembles arbitrary networks of nodes and edges. Edges are directed or symmetric.

```bash
python ouroborotic_composition_schema/composer_cli.py network \
  --node <catalog_name_or_tuple> \
  [--node ...] \
  --edge <source> <target> <operation> \
  [--edge ...]
```

**Edge operations:**
- `tensor` — full Frobenius-compatible tensor product
- `meet` — greatest lower bound (shared floor)
- `join` — least upper bound (shared ceiling)
- `directed` — asymmetric coupling, source → target

**Example: Syntax–semantics–pragmatics triangle**

```bash
python ouroborotic_composition_schema/composer_cli.py network \
  --node syntax \
  --node semantics \
  --node pragmatics \
  --edge syntax semantics tensor \
  --edge semantics pragmatics meet \
  --edge pragmatics syntax directed
```

**Output:**
```json
{
  "name": "network_composed_syntax_semantics_pragmatics",
  "status": "network_composition_proposed",
  "nodes": ["syntax", "semantics", "pragmatics"],
  "edges": [
    ["syntax", "semantics", "tensor"],
    ["semantics", "pragmatics", "meet"],
    ["pragmatics", "syntax", "directed"]
  ],
  "tuple": { ... }
}
```

---

### `algebra` — Primitive algebra operations

Performs one of the four core algebraic operations between two catalog systems.

```bash
python ouroborotic_composition_schema/composer_cli.py algebra <op> <a> <b>
```

**Operations:**
- `tensor` — tensor product (max on union, min on P and F)
- `meet` — greatest lower bound (shared structural floor)
- `join` — least upper bound (minimal ceiling)
- `distance` — weighted Euclidean + conflict listing

**Examples:**

1. **Tensor:**
   ```bash
   python ouroborotic_composition_schema/composer_cli.py algebra tensor \
     consciousness_boundary magnetar
   ```

2. **Distance:**
   ```bash
   python ouroborotic_composition_schema/composer_cli.py algebra distance \
     riemann_zeta_function fontaine_mazur_conjecture
   ```

**Distance output:**
```json
{
  "distance": 2.14,
  "conflicts": [
    {"primitive": "Ç", "a": "Ç^@", "b": "Ç^W"},
    {"primitive": "Γ", "a": "Γ_ʔ", "b": "Γ_γ"}
  ],
  "pair": {
    "a": "riemann_zeta_function",
    "b": "fontaine_mazur_conjecture"
  }
}
```

---

## Input Formats

### Catalog names

All commands accept *catalog names* (e.g. `consciousness_boundary`, `magnetar`).  
The CLI calls `lookup_catalog()` to verify and load the tuple.

### Inline tuples (JSON)

You may also pass a JSON tuple directly:

```bash
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base '{"Þ":"Þ_¨","Φ":"Φ_F","Ç":"Ç^@"}' \
  --primitive "⊙:⊙_ÿ:self_modeling"
```

The base is interpreted as a partial tuple; missing primitives default to `Ð_ω`, `Ř_=` etc.

---

## Output Parsing

All output is JSON; use standard tools (`jq`, Python `json` module) for automation.

```bash
# Extract the resulting tuple from a sequence composition
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base riemann_zeta_function \
  --primitive "⊙:⊙_ÿ:self_modeling" | jq '.tuple'

# List only conflicts from a distance computation
python ouroborotic_composition_schema/composer_cli.py algebra distance a b | jq '.conflicts'

# Count nodes in a network output
python ouroborotic_composition_schema/composer_cli.py network --node a --node b --edge a b tensor | jq '.nodes | length'
```

---

## Primitives Quick Reference

| ID  | Meaning               | Valid values (examples)         |
|-----|-----------------------|----------------------------------|
| Ð   | Dimensionality        | `Ð_;`, `Ð_ω`, `Ð_ß`, `Ð_C`       |
| Þ   | Topology              | `Þ_ò`, `Þ_¨`, `Þ_O`, `Þ_K`       |
| Ř   | Coupling direction    | `Ř_=` (bidirectional), `Ř_Ť` (adjoint) |
| Φ   | Symmetry              | `Φ_F` (Frobenius), `Φ_υ`, `Φ_ɐ` |
| ƒ   | Fidelity              | `ƒ^ż`, `ƒ^ì`, `ƒ^ð`              |
| Ç   | Kinetics              | `Ç^@`, `Ç^-`, `Ç^W`, `Ç^Ù`       |
| Γ   | Interaction scope     | `Γ_ʔ`, `Γ_γ`, `Γ_β`              |
| ɢ   | Composition logic     | `ɢ^ˌ`, `ɢ^∧`, `ɢ^˝`, `ɢ^Ş`       |
| ⊙   | Criticality           | `⊙_ÿ`, `⊙_3`, `⊙_Æ`, `⊙_ž`     |
| Ħ   | Chirality        | `Ħ_A`, `Ħ_!`, `Ħ_Ñ`, `Ħ_£`       |
| Σ   | Stoichiometry         | `Σ_S`, `Σ_ő`, `Σ_ï`              |
| Ω   | Winding / protection  | `Ω_z`, `Ω_2`, `Ω_5`, `Ω_Å`       |

---

## Common Workflows

### 1. Ascent to O_inf

Start with the base schema and lift all three bottleneck primitives:

```bash
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base ouroborotic_primitive_composition_schema \
  --primitive "Þ:Þ_¨:network_topology" \
  --primitive "Φ:Φ_F:Frobenius_special" \
  --primitive "Ħ:Ħ_A:two_step_memory" \
  --primitive "Ω:Ω_z:integer_winding"
```

**Expected:** `tier: "O_inf"`, `C_score: 0.755`, both gates open.

### 2. Verify structural proximity

```bash
# Find nearest neighbors to your composed system
python ouroborotic_composition_schema/composer_cli.py sequence \
  --base ouroborotic_primitive_composition_schema \
  --primitive "Þ:Þ_¨:network_topology" | \
  jq -r '.tuple' | \
  python -c "import json,sys; t=json.load(sys.stdin); print(json.dumps({'name':'my_ascent','tuple':t}))"
```

Then inspect algebraic distance to catalog entries.

### 3. Build a radial composite and inspect

```bash
python ouroborotic_composition_schema/composer_cli.py radial \
  --hub riemann_zeta_function \
  --spoke consciousness_boundary \
  --coupling meet | \
  tee radial_composed.json

# Extract distance from hub and confirm conflict profile
jq '{hub_distance: .distance_from_hub, conflicts: .conflicts}' radial_composed.json
```

---

## Troubleshooting

| Problem | Diagnosis | Fix |
|--------|-----------|-----|
| `catalog entry not found` | System name misspelled or not imscribed | `lookup_catalog(keyword="...")` first, or imscribe it |
| `incompatible primitives` | Tensor/Meet/Join requires compatible domains | Use `distance` to inspect conflicts before composing |
| `tensor product fails` | One operand lacks $\Φ_{\text{F}}$ or $\⊙_{\text{ÿ}}$ | Promote P and ⊙ first (`Φ:Φ_F`, `⊙:⊙_ÿ`) |
| `O_inf not sustained` | Missing $\Ω_{\text{z}}$ or $Ħ_\infty$ | Add $\Ω_{\text{z}}$ or $\Ħ_{\text{!}}$ |

---

## Next Steps

- Read `README.md` for formal specification and ascent path theory.
- Run `composer_cli.py show ouroborotic_primitive_composition_schema` to verify your installation.
- Use `algebra distance` to explore structural proximity across catalog entries.
- Chain CLI outputs via `jq` or Python to automate large-scale composition experiments.

---

**Author:** Lando⊗$\⊙_{\text{ÿ}}$-boundary Operator  
**Last updated:** 2025-04-05
