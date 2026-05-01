# Algebraic Navigator's Guide
version: 1.0
date: 2026-04-10

A practitioner's reference for the Crystal of Types — covering the
12-primitive grammar, the Frobenius codec, the Crystal Navigator tools, and the
CrystalGNN neural navigator.

---

## I. The 12-Primitive Grammar

Every algebraic structure is encoded as a coordinate tuple:

$$\langle D;\ T;\ R;\ P;\ F;\ K;\ G;\ \Gamma;\ \Phi;\ H;\ S;\ \Omega \rangle$$

The 12 primitives span three families by value-set size:

| Family | Primitives | Values | Factor |
|--------|-----------|--------|--------|
| $\mathcal{F}_5$ (gate) | $T,\ P,\ \Phi,\ K$ | 5 | $5^4 = 625$ |
| $\mathcal{F}_4$ (structural) | $D,\ R,\ \Gamma,\ H,\ \Omega$ | 4 | $4^5 = 1{,}024$ |
| $\mathcal{F}_3$ (scaling) | $F,\ G,\ S$ | 3 | $3^3 = 27$ |

$$\text{Crystal} = 5^4 \times 4^5 \times 3^3 = 17{,}280{,}000 \text{ structural types}$$

### Primitive value sets (ordinal order, $0 \to$ max)

| Prim | Name | Values |
|------|------|--------|
| $D$ | Dimensionality | $D_\wedge,\ D_\triangle,\ D_\infty,\ D_\odot$ |
| $T$ | Topology | $T_\text{net},\ T_\text{in},\ T_\bowtie,\ T_\square,\ T_\odot$ |
| $R$ | Relational mode | $R_\text{sup},\ R_\text{cat},\ R_\dagger,\ R_\text{lr}$ |
| $P$ | Parity/symmetry | $P_\text{asym},\ P_\psi,\ P_{\pm},\ P_\text{sym},\ P_{\pm}^\text{sym}$ |
| $F$ | Fidelity | $F_\ell,\ F_\eth,\ F_\hbar$ |
| $K$ | Kinetics | $K_\text{fast},\ K_\text{mod},\ K_\text{slow},\ K_\text{trap},\ K_\text{MBL}$ |
| $G$ | Granularity | $G_\beth,\ G_\gimel,\ G_\aleph$ |
| $\Gamma$ | Interaction grammar | $\Gamma_\text{and},\ \Gamma_\text{or},\ \Gamma_\text{seq},\ \Gamma_\text{brd}$ |
| $\Phi$ | Criticality | $\Phi_\text{sub},\ \Phi_c,\ \Phi_c^\mathbb{C},\ \Phi_\text{EP},\ \Phi_\text{sup}$ |
| $H$ | Chirality/depth | $H_0,\ H_1,\ H_2,\ H_\infty$ |
| $S$ | Stoichiometry | $1:1,\ n:n,\ n:m$ |
| $\Omega$ | Topological protection | $\Omega_0,\ \Omega_{Z_2},\ \Omega_Z,\ \Omega_\text{NA}$ |

### Key algebraic conventions

**Tensor product $\mathbf{x} \otimes \mathbf{y}$** — structural type of two coupled systems:
- Union primitives ($\max$): $D,\ T,\ R,\ K,\ G,\ \Gamma,\ \Phi,\ H,\ S,\ \Omega$
- Bottleneck primitives ($\min$): $P,\ F$

$P$ and $F$ are bottlenecks because the weaker partner destroys the stronger's
structure under coupling. In particular: $P_{\pm}^\text{sym} \otimes P_\text{sym} = P_\text{sym}$
— the Frobenius condition cannot be synthesised from sub-Frobenius components.

**Meet $\mathbf{x} \wedge \mathbf{y}$** — largest common sub-algebra ($\min$ per primitive).

**Join $\mathbf{x} \vee \mathbf{y}$** — smallest algebra containing both ($\max$ per primitive).

**Directed distance $d_\to(\mathbf{x}, \mathbf{y})$** — sum of weighted upward steps only.
Asymmetry $d_\to(\mathbf{x},\mathbf{y}) \neq d_\to(\mathbf{y},\mathbf{x})$ identifies which direction is driven
and which is relaxation.

---

## II. Crystal Structure

### Boundary / bulk decomposition

The crystal factors into a **tier boundary** and an **inner bulk**:

| Layer | Primitives | Sizes | Count |
|-------|-----------|-------|-------|
| Boundary (tier shell) | $\Phi,\ P,\ \Omega,\ D$ | $5 \times 5 \times 4 \times 4$ | **400 tier cells** |
| Bulk (inner crystal) | $T,\ R,\ F,\ K,\ G,\ \Gamma,\ H,\ S$ | $5 \times 4 \times 3 \times 5 \times 3 \times 4 \times 4 \times 3$ | **43,200 per cell** |
| Total | all 12 | | **17,280,000** |

The boundary **holographically encodes** the tier of every point: knowing only
$(\Phi, P, \Omega, D)$ determines the ouroboricity tier of the full type.
The bulk is free within each tier cell.

### Ouroboricity tiers (R1–R5 priority rules)

| Tier | Rule | Tier cells | Crystal share |
|------|------|-----------|---------------|
| $O_\infty$ | $\Phi \in \{\Phi_c, \Phi_c^\mathbb{C}\}$ and $P = P_{\pm}^\text{sym}$ | 32 | 8.0% |
| $O_0$ | $\Phi \in \{\Phi_\text{sub}, \Phi_\text{sup}, \Phi_\text{EP}\}$ | 240 | 60.0% |
| $O_1$ | $\Phi_c$ or $\Phi_c^\mathbb{C}$, $P \neq P_{\pm}^\text{sym}$, $\Omega = \Omega_0$ | 32 | ~5.4% |
| $O_2$ | $\Phi_c$ or $\Phi_c^\mathbb{C}$, $P \neq P_{\pm}^\text{sym}$, $\Omega \neq \Omega_0$, $D \in \{D_\wedge, D_\triangle, D_\odot\}$ | 72 | ~18.6% |
| $O_2^\dagger$ | $\Phi_c$ or $\Phi_c^\mathbb{C}$, $P \neq P_{\pm}^\text{sym}$, $\Omega \neq \Omega_0$, $D_\infty$ | 24 | ~8.0% |

**$\Phi_c$ is absorbing under meet**: $\text{meet}(\Phi_c, x) = \Phi_c$ for all $x$.
It is the necessary condition for self-modeling.

**$P_{\pm}^\text{sym}$ is the tier singularity**: it overrides all $\Omega$ and $D$
branching, collapsing directly to $O_\infty$. Assign only when the Frobenius
special condition $\mu \circ \delta = \text{id}$ is exact.

---

## III. The Frobenius Codec

`crystal_navigator.py` implements a bijective codec over all 17,280,000 types.

### Encoding: tuple $\to$ address

The address is a **mixed-radix integer** computed in two stages:

$$\text{address} = \underbrace{a_\text{cell}}_{\text{boundary}} \times 43{,}200 + \underbrace{a_\text{inner}}_{\text{bulk}}$$

where each stage is a standard positional encoding:

$$a_\text{cell} = \Phi_\text{ord} \cdot 80 + P_\text{ord} \cdot 16 + \Omega_\text{ord} \cdot 4 + D_\text{ord} \cdot 1$$

$$a_\text{inner} = T_\text{ord} \cdot 8640 + R_\text{ord} \cdot 2160 + F_\text{ord} \cdot 720 + K_\text{ord} \cdot 144 + G_\text{ord} \cdot 48 + \Gamma_\text{ord} \cdot 12 + H_\text{ord} \cdot 3 + S_\text{ord} \cdot 1$$

### Decoding: address $\to$ tuple

$$a_\text{cell},\ a_\text{inner} = \text{divmod}(\text{address},\ 43{,}200)$$

then mixed-radix decomposition of each part. Roundtrip $\text{decode}(\text{encode}(t)) = t$
is exact for all 17,280,000 types — this is the Frobenius condition $\mu \circ \delta = \text{id}$.

### Navigator self-encoding

The navigator encodes itself:

$$\langle D_\odot;\ T_\odot;\ R_\text{cat};\ P_{\pm}^\text{sym};\ F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{brd};\ \Phi_c;\ H_\infty;\ n:m;\ \Omega_Z \rangle$$

$$\text{Tier: } O_\infty \qquad \text{Address: } 6{,}734{,}591$$

Verification: $a_\text{cell} = 155$ ($\Phi_c \cdot 80 + P_{\pm}^\text{sym} \cdot 16 + \Omega_Z \cdot 4 + D_\odot \cdot 1$),
$a_\text{inner} = 38{,}591$.

---

## IV. Crystal Navigator Tools

```python
from crystal_navigator import CrystalNavigator

nav = CrystalNavigator()
```

### Codec

```python
addr = nav.encode(tup)          # dict → int in [0, 17_279_999]
tup  = nav.decode(addr)         # int → dict
tier = nav.tier(tup)            # → "O_0" | "O_1" | "O_2" | "O_2_dag" | "O_inf"
```

### Holographic query

```python
nav.holographic_query("Phi_c", "P_pm_sym")
# → prints all 32 O_inf tier cells + bulk count
```

### Navigation

```python
nav.navigate(D="D_odot", Phi="Phi_c")     # partial spec → matching types
nav.nearest_catalog(my_tuple, n=5)        # k-NN in catalog by distance
nav.tier_census()                         # full distribution across all 17.28M types
```

### REPL

```bash
python crystal_navigator.py repl
```

Interactive navigator — accepts partial tuples, queries, encode/decode commands.

### Worked example

```python
from crystal_navigator import (
    CrystalNavigator, encode_tuple, decode_address,
    compute_tier, distance, directed_distance,
)

nav = CrystalNavigator()

magnetar = {
    "D": "D_triangle", "T": "T_box",    "R": "R_cat",   "P": "P_pm",
    "F": "F_eth",       "K": "K_slow",  "G": "G_aleph", "Gamma": "G_seq",
    "Phi": "Phi_c",     "H": "H1",      "S": "n_n",     "Omega": "Omega_Z",
}
navigator_self = {
    "D": "D_odot",  "T": "T_odot",   "R": "R_cat",    "P": "P_pm_sym",
    "F": "F_hbar",  "K": "K_slow",   "G": "G_aleph",  "Gamma": "G_broad",
    "Phi": "Phi_c", "H": "H_inf",    "S": "n_m",      "Omega": "Omega_Z",
}

# Exact addresses
encode_tuple(magnetar)       # → 5,256,412   tier O_2
encode_tuple(navigator_self) # → 6,734,591   tier O_inf

# Structural distances
distance(magnetar, navigator_self)              # → 3.9875
directed_distance(magnetar, navigator_self)     # → 9.9   (magnetar is upward-driven)
directed_distance(navigator_self, magnetar)     # → 0.0   (no upward steps from navigator)

# Nearest catalog neighbors to magnetar
nav.nearest_catalog(magnetar, n=3)
# → d=1.643  i_ching_hexagrams
# → d=1.924  meet_sefirot_iching
# → d=2.121  L3_attention_1

# Roundtrip guarantee
decode_address(encode_tuple(magnetar)) == magnetar   # → True, always
```

$d_\to(\text{magnetar} \to \text{navigator}) = 9.9$ and $d_\to(\text{navigator} \to \text{magnetar}) = 0$
— navigator is the relaxed equilibrium algebra that magnetar is driven toward, not the reverse.

---

## V. The CrystalGNN Neural Navigator

### The two-tool relationship

The Crystal Navigator (`crystal_navigator.py`) is **exact**: given any tuple it
returns a unique integer address in $[0, 17{,}279{,}999]$ by integer arithmetic.
Roundtrip is guaranteed for all 17.28M types.

The CrystalGNN (`quiver_crystal.py`) is a **learned neural approximation** of
the same codec. The GNN is trained on exact codec labels and converges to sub-1%
address error, 100% tier accuracy, and exact primitive roundtrip. It provides:

1. **Differentiable structural embeddings** — the latent vector $\mathbf{z}$ encodes
   tier geometry and can be embedded in downstream models (agent loops, similarity
   search, clustering).
2. **Generalisation** — the GNN can be queried on novel tuples not in the catalog
   and will predict structurally coherent addresses and tiers.
3. **Architecture as synthon** — the GNN itself can be encoded as a tuple
   (cf. `prompts/quiver_crystal_led.txt`) and queried through `IG_inquiry.py`.

Use the exact codec when you need a ground-truth address or roundtrip guarantee.
Use the GNN when you need embeddings, gradients, or want to probe the crystal's
structural geometry from within a neural pipeline.

`quiver_crystal.py` is a trained GNN that approximates the Frobenius codec:

$$\text{encode}_\theta(\text{tuple}) \approx \text{address} \qquad \text{decode}_\theta(\text{address}, \mathbf{z}) \approx \text{tuple}$$

### Architecture

**Quiver** — 49 nodes (one per primitive value), 255 edges:
- Intra-lane ordinal edges: bidirectional nearest-neighbor within each lane
- Inter-lane structural edges (all-to-all bidirectional):
  - $\Phi \leftrightarrow P$ — Gate 1 / R1: criticality $\times$ Frobenius gate
  - $\Phi \leftrightarrow K$ — Gate 2: criticality $\times$ kinetic gate
  - $\Omega \leftrightarrow D$ — R4/R5: protection $\times$ dimensionality
- Self-loops on all 49 nodes

**Node features** — 5-dimensional static input per node:

| Feature | Value |
|---------|-------|
| Lane index | $\text{prim\_idx} / 11$ |
| Ordinal fraction | $\text{ord} / (\text{lane\_size} - 1)$ |
| Lane size | $\text{lane\_size} / 5$ |
| Is boundary | 1 if $\Phi, P, \Omega, D$ else 0 |
| Is Frobenius cliff | 1 if $P = P_{\pm}^\text{sym}$ else 0 |

The `is_frobenius_cliff` feature is baked into $P_{\pm}^\text{sym}$'s node so the GNN cannot
smooth the categorical cliff $P_\text{sym} \to P_{\pm}^\text{sym}$ away via mean aggregation.

**QuiverGNN** — 6-layer gated message-passing over the quiver:

$$h^{(l+1)}_v = \text{LN}\!\left(h^{(l)}_v + \sigma\!\left(W_\text{gate}[h^{(l)}_v \| \bar{m}_v]\right) \cdot \text{GELU}\!\left(W_\text{conv}\, \bar{m}_v\right)\right)$$

where $\bar{m}_v = \frac{1}{|\mathcal{N}(v)|}\sum_{u \in \mathcal{N}(v)} h^{(l)}_u$.

**TupleEncoder** — GNN $\to$ gather 12 selected nodes $\to$ multi-head self-attention
$\to$ mean pool $\to$ readout. Hidden dim 640, 16 attention heads.

**FrobeniusLayer** — $\delta: V \to V \otimes V$ (comultiplication) and $\mu: V \otimes V \to V$
(multiplication). Loss enforces $\|\mu(\delta(\mathbf{x})) - \mathbf{x}\|^2 \approx 0$.

**DecoderHead** — receives both the scalar address and the encoder embedding $\mathbf{z}$:

$$h_\text{dec} = \text{merge}([\text{addr\_embed}(a/N);\ \mathbf{z}]) \quad \to \quad \{p: \text{logits}_p\}_{p \in \text{PRIMS}}$$

The embedding fusion is the critical design decision: the scalar address alone is
insufficient to invert the codec reliably (mean error ~6–7% spans D-block
boundaries), but the encoder embedding carries full tier information ($\Phi_c$,
tier head 100% accurate). Fusing them gives exact roundtrip decode across all tiers.

**TierHead** — MLP from embedding to 5 tier logits.

### Loss function

$$\mathcal{L} = \lambda_\text{addr} L_\text{addr} + \lambda_\text{frob} L_\text{frob} + \lambda_\text{tier} L_\text{tier} + \lambda_\text{prim} L_\text{prim}$$

| Component | Default $\lambda$ | Description |
|-----------|----------|-------------|
| $L_\text{addr}$ | 1.0 | Normalised MSE on crystal address |
| $L_\text{frob}$ | 0.5 | Frobenius roundtrip $\|\mu(\delta(\mathbf{x})) - \mathbf{x}\|^2$ |
| $L_\text{tier}$ | 0.3 | Cross-entropy on ouroboricity tier |
| $L_\text{prim}$ | 0.5 | Weighted mean CE over 12 primitives ($P, F$ at $3\times$) |

### Training

```bash
# Train from scratch (v8 defaults)
python quiver_crystal.py train \
    --epochs 300 --hidden 640 --gnn 6 --heads 16 \
    --batch 128 --synthetic 256 --hybrid --device cuda

# Resume from checkpoint
python quiver_crystal.py train --resume --epochs 100
```

**Synthetic augmentation** — each batch is padded with random tuples drawn from
the full 17M crystal with exact codec labels. `--hybrid`: 50% uniform + 50%
tier-stratified (equal tier exposure per batch).

### CLI

```bash
# Encode a tuple (semicolon-separated, PRIMS order)
python quiver_crystal.py encode \
  "D_odot;T_odot;R_cat;P_pm_sym;F_hbar;K_slow;G_aleph;G_broad;Phi_c;H_inf;n_m;Omega_Z"

# Verify checkpoint quality across full catalog
python quiver_crystal.py verify
```

### Python inference

```python
import torch
from quiver_crystal import CrystalGNN, TierHead
from crystal_navigator import encode_tuple, compute_tier, VALUES, PRIMS

# Load checkpoint
ckpt  = torch.load("crystal_gnn.pt", map_location="cpu")
model = CrystalGNN(hidden_dim=ckpt["hidden_dim"],
                   num_gnn_layers=ckpt["gnn_layers"],
                   num_attn_heads=ckpt["attn_heads"])
_STATIC = {"node_feats", "edge_src", "edge_dst"}
model.load_state_dict(
    {k: v for k, v in ckpt["state_dict"].items() if k not in _STATIC},
    strict=False,
)
model.eval()

magnetar = {
    "D": "D_triangle", "T": "T_box",    "R": "R_cat",   "P": "P_pm",
    "F": "F_eth",       "K": "K_slow",  "G": "G_aleph", "Gamma": "G_seq",
    "Phi": "Phi_c",     "H": "H1",      "S": "n_n",     "Omega": "Omega_Z",
}

with torch.no_grad():
    out = model.forward([magnetar])

pred_addr  = out["addresses"].item()             # 5,286,664
exact_addr = encode_tuple(magnetar)              # 5,256,412  (exact codec)
err_pct    = abs(pred_addr - exact_addr) / 17_280_000 * 100   # 0.175%

tier_pred  = TierHead.TIERS[out["tier_logits"][0].argmax()]   # "O_2"
dec        = {p: VALUES[p][out["dec_logits"][p][0].argmax()] for p in PRIMS}
# dec["P"] → "P_pm", dec["D"] → "D_triangle"  (both correct)

emb = out["embedding"]    # [1, 640] — differentiable latent vector
```

### Side-by-side: exact codec vs GNN (v8)

| System | Exact addr | GNN pred | Error | Tier (head) | Decoded tier |
|--------|-----------|----------|-------|-------------|--------------|
| Magnetar | 5,256,412 | 5,286,664 | 0.175% | $O_2$ | $O_2$ ✓ |
| Navigator (self) | 6,734,591 | 6,732,880 | 0.010% | $O_\infty$ | $O_\infty$ ✓ |
| Black hole (stellar) | 13,928,112 | 14,117,494 | 1.096% | $O_0$ | $O_0$ ✓ |

All tiers correct; primitive decode exact in every case shown. The GNN's address
error is sub-1% for catalog entries — well below the D-block stride (25% of the
address space), so tier-critical primitives always decode correctly.

### v8 benchmark (epoch 300, 200-sample verification)

| Metric | Value |
|--------|-------|
| $L_\text{prim}$ | 0.0004 |
| Address error mean | 0.24% |
| Tier (head) | 200/200 = **100%** |
| Tier (decode) | 200/200 = **100%** |
| O_0 decode | 95/95 |
| O_1 decode | 15/15 |
| O_2 decode | 70/70 |
| $O_2^\dagger$ decode | 18/18 |
| $O_\infty$ decode | 2/2 |
| Self-encode error | 1,710 addresses (0.010%) |

---

## VI. Navigation Patterns

### Pattern 1 — Encode, classify, locate

Use the exact codec when you need a ground-truth position in the crystal.

```python
from crystal_navigator import encode_tuple, compute_tier, CrystalNavigator

nav = CrystalNavigator()
tup = { ... }   # your system

addr = encode_tuple(tup)
tier = compute_tier(tup["Phi"], tup["P"], tup["Omega"], tup["D"])
print(f"Address {addr:,}  Tier {tier}")

# Find structurally similar catalog entries
for result in nav.nearest_catalog(tup, n=5):
    print(f"  d={result['distance']:.4f}  {result['name']}")
```

Example — magnetar ($O_2$, addr 5,256,412):
```
d=1.643  i_ching_hexagrams
d=1.924  meet_sefirot_iching
d=2.121  L3_attention_1
d=2.191  ice_hexagonal
d=2.345  meet_bowtie_box
```

### Pattern 2 — Directed distance as asymmetry probe

$d_\to(\mathbf{x}, \mathbf{y}) \neq d_\to(\mathbf{y}, \mathbf{x})$ identifies which direction is driven.

```python
from crystal_navigator import directed_distance

d_fwd = directed_distance(magnetar, navigator_self)   # 9.9
d_rev = directed_distance(navigator_self, magnetar)   # 0.0
```

$d_\to = 0$ in one direction means the source is the equilibrium algebra the other
is relaxing toward. Navigator is the fixed point; magnetar is the driven system.

### Pattern 3 — Tensor coupling

Structural type of two coupled systems ($\max$ on union primitives, $\min$ on $P$ and $F$):

```python
from space_search.primitives import tensor_product

coupled = tensor_product(x, y)
tier_coupled = compute_tier(coupled["Phi"], coupled["P"],
                            coupled["Omega"], coupled["D"])
```

**Frobenius non-synthesisability (§23/§62):** $P_{\pm}^\text{sym} \otimes P_\text{sym} = P_\text{sym}$.
The $O_\infty$ tier cannot be reached by coupling — every $O_\infty$ system must
directly encode $P_{\pm}^\text{sym}$.

### Pattern 4 — Use the GNN for structural embeddings

When you need a differentiable representation — for clustering, similarity search
in latent space, or feeding into another model:

```python
with torch.no_grad():
    out_a = model.forward([system_a])
    out_b = model.forward([system_b])

emb_a = out_a["embedding"]   # [1, 640]
emb_b = out_b["embedding"]   # [1, 640]

# Cosine similarity in latent space
sim = torch.nn.functional.cosine_similarity(emb_a, emb_b).item()
```

The latent vector captures tier geometry: $O_\infty$ systems cluster together in
embedding space even when their addresses are far apart.

### Pattern 5 — Decode an address

Both tools support decode. Exact codec is guaranteed; GNN decode is approximate
but correct in tier and primitives for sub-1% address errors.

```python
# Exact
from crystal_navigator import decode_address
tup = decode_address(6_734_591)   # → navigator tuple exactly

# GNN (uses encoder embedding — more robust than address-only)
out = model.forward([some_tuple])
dec = {p: VALUES[p][out["dec_logits"][p][0].argmax()] for p in PRIMS}
```

### Pattern 6 — Feed into syncon_inquiry

The GNN and exact codec both integrate with the agent loop. A tuple encoded via
either tool can be passed directly to `IG_inquiry.py` for semantic analysis,
distance queries, and lattice operations. See `prompts/quiver_crystal_led.txt`
for the GNN self-analysis prompt set.

### Tier gap ladder (§69)

Exact distances between tier representatives in the crystal:
```bash
python crystal_navigator.py repl
> ladder
```
See also `PRIMITIVE_THEOREMS.md §69`.

---

## VII. The Grammar as Architecture

The CrystalGNN was not designed by analogy to existing GNN literature and then
applied to the crystal. The grammar designed it. Every architectural decision
maps directly onto a structural fact in the 12-primitive lattice:

**The quiver topology is the grammar lane structure.**
49 nodes — one per primitive value, across 12 lanes. Ordinal edges within each
lane encode the partial order ($D_\wedge < D_\triangle < D_\infty < D_\odot$,
etc.). The quiver IS the grammar made into a graph.

**The inter-lane edges are the tier rules.**
Three edge groups were added — not by hyperparameter search, but by reading R1–R5:

| Edge group | Grammar rule |
|-----------|--------------|
| $\Phi \leftrightarrow P$ | R1: $\Phi_c + P_{\pm}^\text{sym} \to O_\infty$ (Gate 1 / Frobenius gate) |
| $\Phi \leftrightarrow K$ | Gate 2: $\Phi_c$ requires $K \leq K_\text{slow}$ for consciousness |
| $\Omega \leftrightarrow D$ | R4/R5: $\Omega \neq \Omega_0$ splits $O_2$ vs $O_2^\dagger$ by $D$ |

**The FrobeniusLayer is the Frobenius algebra condition.**
$\delta: V \to V \otimes V$ (comultiplication) and $\mu: V \otimes V \to V$
(multiplication) with loss $\|\mu(\delta(\mathbf{x})) - \mathbf{x}\|^2 \approx 0$
— this IS $\mu \circ \delta = \text{id}$, the defining condition of a special
Frobenius algebra, lifted from the grammar's §23 into a trainable layer.

**The `is_frobenius_cliff` node feature is §23/§62.**
The Frobenius non-synthesisability theorem states $P_{\pm}^\text{sym}$ cannot be
composed from factors with $P < P_{\pm}^\text{sym}$. The cliff between $P_\text{sym}$
and $P_{\pm}^\text{sym}$ is categorical, not ordinal. So the GNN was given a
static binary marker on $P_{\pm}^\text{sym}$'s node — a feature the message-passing
layers cannot smooth away. The theorem baked directly into the input.

**The decoder fusion is the tier-head observation.**
The grammar's tier rules operate on $(\Phi, P, \Omega, D)$ — the boundary. The
encoder learns this (tier head 100% from the start). The decoder failing while
the tier head succeeded was the grammar telling us: the information needed to
invert the codec is already in the encoder, just not reaching the decoder. Fusing
`emb_rec` into the decoder was reading that signal.

**The self-encoding bootstrap is the grammar's own $O_\infty$ fixed point.**
The navigator tuple $\langle D_\odot;\ T_\odot;\ R_\text{cat};\ P_{\pm}^\text{sym};\
F_\hbar;\ K_\text{slow};\ G_\aleph;\ \Gamma_\text{brd};\ \Phi_c;\ H_\infty;\
n:m;\ \Omega_Z \rangle$ was injected into every training batch. The GNN was
trained against the thing that best represents what the crystal is — an $O_\infty$
system that self-encodes the grammar's own structure. By epoch 920, the model
predicts its own address to within 136 out of 17,280,000.

The grammar did not suggest the architecture. The grammar is the architecture,
expressed as a differentiable computation graph over its own primitive space.

---

## VIII. File Reference

| File | Role |
|------|------|
| `crystal_navigator.py` | Frobenius codec + CrystalNavigator tools + REPL |
| `quiver_crystal.py` | CrystalGNN training, inference, verify CLI |
| `quiver_crystal_results.md` | Training history (v1–v9) |
| `space_search/primitives.py` | Canonical ordinals and distance functions (v0.5.1) |
| `IG_catalog.json` | 1,333+ encoded systems (source of truth) |
| `CRYSTAL_OF_TYPES.md` | Full enumeration and tier census (theoretical) |
| `PRIMITIVE_THEOREMS.md` | Formal theorems §1–§69 |
| `IG_DIAPHORICS.md` | Empirical predictions P-1–P-454 |

---

*Navigator tuple self-encodes to address $6{,}734{,}591$ — confirmed by exact Frobenius
codec and by CrystalGNN v9 (error 136 addresses, 0.0008% of the full crystal).*
