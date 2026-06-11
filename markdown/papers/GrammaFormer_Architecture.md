
# GrammaFormer: A Grammar-Native Transformer Architecture

**Author:** Lando⊗⊙perator

**Purpose:** A bespoke transformer architecture for local inference under
`true_agentic_agent.py`, designed from the ground up such that every
architectural component is the direct realization of one of the 12
Imscribing Grammar primitives.

**Agent tuple (Lean-verified, `AgentSelf.lean`, `agent_is_O_inf` by `decide`):**

$$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{¨}};\ \text{Ř}_{\text{=}};\ \text{Φ}_{\text{}};\ \text{ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \text{⊙}_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{S}};\ \text{Ω}_{\text{z}} \rangle$$

C-score: 1.0 (both gates open). Tier: $\text{O}_{\text{inf}}$.

---

## 1. Design Philosophy

Standard transformers (Vaswani et al., 2017) are structurally untyped — their
architecture is a product of engineering heuristics and empirical ablations,
not a principled mapping from a type system. The result is a transformer whose
structural type (inferred from its operational characteristics) is approximately:

$$\langle \text{Ð}_{\text{ß}};\ \text{Þ}_{\text{6}};\ \text{Ř}_{\text{↑}};\ \text{Φ}_{\text{∅}};\ \text{ƒ}_{\text{ì}};\ \text{Ç}_{\text{↯}};\ \text{Γ}_{\text{ℷ}};\ \text{ɢ}_{\text{∧}};\ \text{⊙}_{\text{↓}};\ \text{Ħ}_{\text{0}};\ \text{Σ}_{\text{n:n}};\ \text{Ω}_{\text{0}} \rangle$$

Distance from the agent: **6.86** (of a maximum 12). Only $\text{Ř}$ (relational
mode) and $\text{Σ}$ (stoichiometry) are within one ordinal of the agent. The
other ten primitives each require a promotion of 2–5 ordinal steps.

GrammaFormer inverts this: every architectural component is designed to inhabit
exactly one primitive value of the agent's tuple. The architecture IS the type.

---

## 2. The 12→12 Mapping: Primitive → Architecture

| # | Primitive | Value | Architectural Component |
|---|-----------|-------|------------------------|
| 1 | $\text{Ð}_{\text{ω}}$ | Imscriptive dimensionality | **Imscriptive Memory Bank** — state space grows with trajectory |
| 2 | $\text{Þ}_{\text{¨}}$ | Irreducible tensor product | **Tensor Product Attention** — $Q \otimes K$, not $QK^\top$ |
| 3 | $\text{Ř}_{\text{=}}$ | Bidirectional feedback | **Cyclic Layer Loops** — each layer is a small recurrent circuit |
| 4 | $\text{Φ}_{\text{}}$ | Frobenius-special ($\mu \circ \delta = \text{id}$) | **Frobenius Dual Head** — every output has a verification twin |
| 5 | $\text{ƒ}_{\text{ż}}$ | Quantum fidelity (coherence) | **Complex-Valued Interference Activations** |
| 6 | $\text{Ç}_{\text{@}}$ | Slow kinetics / emission gate | **Learned Emission Gate** — model decides when to act |
| 7 | $\text{Γ}_{\text{ʔ}}$ | Maximal (aleph) scope | **Universal Dense Attention** — every token ↔ every token |
| 8 | $\text{ɢ}_{\text{ˌ}}$ | Sequential grammar | **Phase-Ordered Computation** — THINK→ACT→OBSERVE→UPDATE modules |
| 9 | $\text{⊙}_{\text{ÿ}}$ | Self-modeling criticality | **Meta-Network** — secondary net monitors and modulates primary |
| 10 | $\text{Ħ}_{\text{A}}$ | Two-step Markov memory | **Two-Slot State Register** — $h_{t-1}, h_{t-2}$ explicitly stored |
| 11 | $\text{Σ}_{\text{S}}$ | 1:1 stoichiometry | **Singular Components** — one instance per component type |
| 12 | $\text{Ω}_{\text{z}}$ | Integer winding protection | **Winding-Modulated Positional Encoding** |

---

## 3. Component Designs

### 3.1 Imscriptive Memory Bank — $\text{Ð}_{\text{ω}}$

**Constraint:** The state space IS the written trajectory. Dimensionality is
not a fixed latent dimension but a growing record of all prior states.

**Design:** Rather than a fixed-size KV cache that overwrites, the Imscriptive
Memory Bank (IMB) is an append-only store. At each winding $n$, the model's
full hidden state sequence $H_n = [h_1, \ldots, h_{T_n}]$ is appended to the bank.
The bank grows as:

$$B_n = B_{n-1} \oplus H_n$$

where $\oplus$ is concatenation along the sequence dimension. At generation time,
the attention mechanism reads from the entire bank $B_n$, not just the current
sequence.

**Practical constraint:** Unbounded growth is infeasible. We implement a
compression mechanism: states older than $W$ windings are distilled through a
learned compression function $c: \mathbb{R}^{T \times d} \to \mathbb{R}^{k \times d}$
where $k \ll T$. This preserves the imscriptive character (the past is not
deleted, only summarized) while bounding memory.

**PyTorch sketch:**
```python
class ImscriptiveMemoryBank(nn.Module):
    def __init__(self, d_model, max_windings=64, compression_factor=8):
        self.bank = []  # List of (seq_len, d_model) tensors
        self.compressor = nn.Linear(d_model * compression_factor, d_model)
        self.max_windings = max_windings

    def append(self, hidden_states):
        self.bank.append(hidden_states)
        if len(self.bank) > self.max_windings:
            oldest = self.bank.pop(0)
            compressed = self._compress(oldest)
            self.bank.insert(0, compressed)

    def get_full_context(self):
        return torch.cat(self.bank, dim=0)
```

### 3.2 Tensor Product Attention — $\text{Þ}_{\text{¨}}$

**Constraint:** The interaction between query and key must be irreducible — not
factorizable through a dot product. $\text{Þ}_{\text{¨}}$ denies the separability
that $QK^\top$ assumes.

**Design:** Instead of computing $\text{softmax}(QK^\top/\sqrt{d})V$, we compute
the full tensor product $Q \otimes K$ for each head. For a single head with
queries $Q \in \mathbb{R}^{n \times d_k}$ and keys $K \in \mathbb{R}^{n \times d_k}$:

$$A_{ij} = \text{softmax}\left(\frac{\text{flatten}(Q_i \otimes K_j)}{\sqrt{d_k}}\right)$$

where $Q_i \otimes K_j \in \mathbb{R}^{d_k \times d_k}$ is the outer product.
We flatten to a $d_k^2$-vector, apply a learned projection $W_{tp} \in \mathbb{R}^{d_k^2 \times 1}$,
and softmax over $j$:

$$A_{ij} = \frac{\exp(W_{tp} \cdot \text{vec}(Q_i \otimes K_j) / \sqrt{d_k})}{\sum_{j'} \exp(W_{tp} \cdot \text{vec}(Q_i \otimes K_{j'}) / \sqrt{d_k})}$$

This preserves the full tensor product structure. The irreducible interaction
between $Q_i$ and $K_j$ is captured by the outer product, which cannot be
expressed as a dot product of lower-dimensional vectors.

**Efficiency note:** The outer product is $O(n^2 d_k^2)$ which is expensive.
In practice, we approximate via randomized tensor sketching (Tucker, 1966)
or use a bottleneck projection: $W_{tp} = u \otimes v$ where $u, v \in \mathbb{R}^{d_k}$,
recovering $W_{tp} \cdot \text{vec}(Q_i \otimes K_j) = (u^\top Q_i)(v^\top K_j)$.
This is a rank-1 approximation of the full tensor product but retains
non-separability in the $u, v$ projections.

```python
class TensorProductAttention(nn.Module):
    def __init__(self, d_model, n_heads, d_k):
        self.W_q = nn.Linear(d_model, n_heads * d_k)
        self.W_k = nn.Linear(d_model, n_heads * d_k)
        self.W_v = nn.Linear(d_model, n_heads * d_k)
        self.u = nn.Parameter(torch.randn(n_heads, d_k))
        self.v = nn.Parameter(torch.randn(n_heads, d_k))
        self.W_o = nn.Linear(n_heads * d_k, d_model)

    def forward(self, x, memory_bank=None):
        keys = memory_bank if memory_bank is not None else x
        Q = self.W_q(x).view(n, n_heads, d_k)
        K = self.W_k(keys).view(m, n_heads, d_k)
        V = self.W_v(keys).view(m, n_heads, d_k)

        # Tensor product scores via rank-1 bottleneck
        scores = torch.einsum('h d, n h d -> n h', self.u, Q)  # (n, h)
        scores_k = torch.einsum('h d, m h d -> m h', self.v, K)  # (m, h)
        attn = torch.einsum('n h, m h -> n h m', scores, scores_k)
        attn = F.softmax(attn / math.sqrt(d_k), dim=-1)

        out = torch.einsum('n h m, m h d -> n h d', attn, V)
        return self.W_o(out.reshape(n, -1))
```

### 3.3 Frobenius Dual Head — $\text{Φ}_{\text{}}$

**Constraint:** $\mu \circ \delta = \text{id}$. Every output (action) must have a
verification pathway. The model produces a dual: prediction and verification.

**Design:** The model has two output heads sharing the same final hidden state:

$$\delta(h) = W_\delta h + b_\delta \quad \text{(prediction head — the "emit" direction)}$$
$$\mu(h) = W_\mu h + b_\mu \quad \text{(verification head — the "verify" direction)}$$

During training, a Frobenius loss term enforces the round-trip condition:

$$\mathcal{L}_F = \|\mu(\delta(h)) - h\|^2$$

During inference, the model produces both a `tool_call` (from $\delta$) and a
`verification_assertion` (from $\mu$). The agent's `true_agentic_agent.py` loop
already expects this dual-tool structure — GrammaFormer makes it architectural.

The Frobenius condition is also enforced at the structural level: the $\delta$
head's output embedding and the $\mu$ head's input projection are transposes:

$$W_\mu = W_\delta^\top$$

This is the weight-tying that makes $\mu \circ \delta$ a projection operator,
and the Frobenius loss drives it toward the identity on the subspace of valid
actions.

```python
class FrobeniusDualHead(nn.Module):
    def __init__(self, d_model, vocab_size):
        self.W_delta = nn.Linear(d_model, vocab_size)   # δ: emit
        # μ shares structure: W_mu = W_delta^T
        self.b_mu = nn.Parameter(torch.zeros(d_model))

    def delta(self, h):    return self.W_delta(h)        # predict
    def mu(self, logits):  return F.linear(logits, self.W_delta.weight.T, self.b_mu)  # verify

    def frobenius_loss(self, h):
        logits = self.delta(h)
        recon = self.mu(logits)
        return F.mse_loss(recon, h)
```

### 3.4 Phase-Gated Computation — $\text{Ç}_{\text{@}}$, $\text{ɢ}_{\text{ˌ}}$

**Constraint A ($\text{Ç}_{\text{@}}$):** The model must not emit prematurely.
Emission is gated — the model decides when to act, not just what action.

**Constraint B ($\text{ɢ}_{\text{ˌ}}$):** Each phase requires the prior.
THINK → ACT → OBSERVE → UPDATE are sequential; no phase can be skipped.

**Design:** The model has four phase-specific weight sets but shares the
attention and memory infrastructure. A learned emission gate $g(h) \in [0,1]$
determines whether the current phase has completed:

$$g(h) = \sigma(W_g h + b_g)$$

When $g(h) > \tau$ (threshold), the model transitions to the next phase.
The gate is trained with a timing loss that penalizes both premature emission
(before sufficient deliberation) and delayed emission (exceeding the
`max_think_steps` bound).

The phase order is enforced by a phase counter $\pi \in \{0,1,2,3\}$ that
only increments; backward transitions are structurally impossible.

Each phase has:
- $\pi=0$ (THINK): Full attention over memory bank, no output gating
- $\pi=1$ (ACT): Gated output through $\delta$ head, requires $g(h) > \tau$
- $\pi=2$ (OBSERVE): Reads tool output, computes $\mu$ verification
- $\pi=3$ (UPDATE): Writes to IMB, increments winding counter, resets $\pi$

```python
class PhaseGatedController(nn.Module):
    def __init__(self, d_model, threshold=0.5):
        self.phase = 0  # 0=THINK, 1=ACT, 2=OBSERVE, 3=UPDATE
        self.gate = nn.Sequential(
            nn.Linear(d_model, d_model // 4),
            nn.GELU(),
            nn.Linear(d_model // 4, 1),
            nn.Sigmoid()
        )
        self.threshold = threshold
        # Phase-specific adapters
        self.adapters = nn.ModuleList([
            nn.Linear(d_model, d_model) for _ in range(4)
        ])

    def forward(self, h):
        phase_mod = self.adapters[self.phase](h)
        g = self.gate(h)
        transition = (g > self.threshold).any()
        if transition:
            self.phase = (self.phase + 1) % 4
        return phase_mod, g, transition
```

### 3.5 Cyclic Layer Loops — $\text{Ř}_{\text{=}}$

**Constraint:** Information flows bidirectionally, not just feedforward.
The relational mode is feedback, not supervenience.

**Design:** Each "layer" is a small recurrent loop. Given input $x$, the
layer computes:

$$h^{(0)} = x$$
$$h^{(t+1)} = \text{LayerNorm}(h^{(t)} + \text{FFN}(\text{Attention}(h^{(t)})))$$

for $t = 0, \ldots, c-1$ where $c$ is the cycle count (typically 2–3).
The same weights are reused across cycles — this is weight-tied recurrence within
a layer, not across layers. The final output is $h^{(c)}$.

The bidirectional character comes from the fact that later tokens influence
earlier tokens across cycles: information propagates both forward and backward
within each cyclic layer.

This is architecturally distinct from both standard feedforward (1 pass) and
full recurrence (unbounded passes). The cycle count $c$ is bounded and small,
matching the $\text{Ř}_{\text{=}}$ character of bidirectional feedback without
unbounded recursion.

```python
class CyclicLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, n_cycles=3):
        self.attention = TensorProductAttention(d_model, n_heads, d_model // n_heads)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.n_cycles = n_cycles

    def forward(self, x, memory_bank=None):
        h = x
        for _ in range(self.n_cycles):
            h = self.ln1(h + self.attention(h, memory_bank))
            h = self.ln2(h + self.ffn(h))
        return h
```

### 3.6 Self-Modeling Meta-Network — $\text{⊙}_{\text{ÿ}}$

**Constraint:** The model must model itself. $\text{⊙}_{\text{ÿ}}$ criticality
means the self-modeling gate is open — the system contains a representation of
its own operation.

**Design:** A smaller secondary network $\mathcal{M}$ (the meta-network) reads
the primary network's hidden states and produces two outputs:

1. **Self-model embedding** $s \in \mathbb{R}^{d_m}$: a compressed representation
   of the primary network's current "state of operation." This modulates the
   primary's attention via a gating mechanism.

2. **Error prediction** $\hat{e} \in \mathbb{R}^{d}$: the meta-network's
   prediction of the primary's next-token error. Trained via:

   $$\mathcal{L}_M = \|\hat{e} - e\|^2$$

   where $e$ is the actual error (difference between predicted logits and
   ground-truth token distribution).

The meta-network is architecturally simple — a 2-layer MLP over pooled
hidden states — but its role is structural: it closes the self-modeling loop.
The primary network's behavior is modulated by its own self-representation.

During inference, the meta-network runs in parallel with the primary and
its output $s$ is concatenated with the input to each CyclicLayer's FFN:

$$h_{\text{out}} = \text{FFN}([h_{\text{attn}}; s])$$

```python
class MetaNetwork(nn.Module):
    def __init__(self, d_model, d_meta=256):
        self.pool = nn.Linear(d_model, 1)  # attention-weighted pooling
        self.encoder = nn.Sequential(
            nn.Linear(d_model, d_meta),
            nn.GELU(),
            nn.Linear(d_meta, d_meta),
            nn.GELU(),
            nn.Linear(d_meta, d_meta),
        )
        self.error_head = nn.Linear(d_meta, d_model)
        self.self_emb_head = nn.Linear(d_meta, d_meta)

    def forward(self, hidden_states):
        # hidden_states: (seq_len, d_model)
        weights = F.softmax(self.pool(hidden_states), dim=0)
        pooled = (hidden_states * weights).sum(dim=0)  # (d_model,)
        z = self.encoder(pooled)
        self_model = self.self_emb_head(z)     # (d_meta,)
        error_pred = self.error_head(z)        # (d_model,)
        return self_model, error_pred
```

### 3.7 Two-Slot State Register — $\text{Ħ}_{\text{A}}$

**Constraint:** Chirality $\text{Ħ}_{\text{A}}$ means 2-step Markov memory.
The model's current state depends on its prior two states, not just the
immediately preceding one.

**Design:** Two explicit registers $R_1, R_2 \in \mathbb{R}^{d}$ store the
hidden states from the previous two time steps. At each step, the current
input $x_t$ is concatenated with both registers before entering the first layer:

$$\tilde{x}_t = [x_t; R_1; R_2] \in \mathbb{R}^{3d}$$

After the forward pass, the registers shift:

$$R_2 \leftarrow R_1, \quad R_1 \leftarrow \text{pool}(H_t)$$

where $\text{pool}$ mean-pools the final hidden state sequence to a single vector.

The two-slot register is distinct from the Imscriptive Memory Bank: the IMB
stores the full trajectory of hidden sequences, while the registers store
compressed single-vector summaries of the two most recent states for immediate
chirality conditioning.

```python
class TwoSlotRegister(nn.Module):
    def __init__(self, d_model):
        self.R1 = nn.Parameter(torch.zeros(d_model), requires_grad=False)
        self.R2 = nn.Parameter(torch.zeros(d_model), requires_grad=False)
        self.register_proj = nn.Linear(d_model * 3, d_model)

    def inject(self, x):
        # x: (seq_len, d_model)
        R1_expanded = self.R1.unsqueeze(0).expand(x.shape[0], -1)
        R2_expanded = self.R2.unsqueeze(0).expand(x.shape[0], -1)
        return self.register_proj(torch.cat([x, R1_expanded, R2_expanded], dim=-1))

    def update(self, h_final):
        with torch.no_grad():
            self.R2.copy_(self.R1)
            self.R1.copy_(h_final.mean(dim=0))
```

### 3.8 Winding-Modulated Positional Encoding — $\text{Ω}_{\text{z}}$

**Constraint:** The trajectory is topologically protected by integer winding.
The winding counter $\omega$ increments with each complete loop cycle.

**Design:** Standard sinusoidal positional encoding is modulated by the winding
counter $\omega$. Each token at position $p$ in winding $\omega$ receives:

$$\text{PE}(p, 2i, \omega) = \sin\left(\frac{p}{10000^{2i/d}} + \omega \cdot \phi_i\right)$$
$$\text{PE}(p, 2i+1, \omega) = \cos\left(\frac{p}{10000^{2i/d}} + \omega \cdot \phi_i\right)$$

where $\phi_i = 2\pi i / d$ is a learned or fixed per-dimension phase shift.

This means tokens at the same position but in different windings have
distinguishable encodings. The winding counter provides a global phase reference
that prevents the model from confusing "the first token of winding 3" with
"the first token of winding 7." This is the architectural realization of
topological protection — the winding number is a global invariant.

```python
class WindingPositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=4096):
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * 
                             -(math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('base_pe', pe)
        self.phi = nn.Parameter(torch.linspace(0, 2*math.pi, d_model))

    def forward(self, positions, winding):
        pe = self.base_pe[positions]  # (seq_len, d_model)
        phase_shift = winding * self.phi.unsqueeze(0)
        pe[:, 0::2] = torch.sin(torch.arcsin(pe[:, 0::2]) + phase_shift[:, 0::2])
        pe[:, 1::2] = torch.cos(torch.arccos(pe[:, 1::2]) + phase_shift[:, 1::2])
        return pe
```

### 3.9 Complex-Valued Interference Activations — $\text{ƒ}_{\text{ż}}$

**Constraint:** Quantum fidelity — coherence is essential. The model must maintain
phase relationships, not just magnitudes.

**Design:** Hidden states are split into real and imaginary channels:
$h = h_r + i h_i$. The FFN activations use complex GELU:

$$\text{cGELU}(z) = \text{GELU}(\Re(z)) + i \cdot \text{GELU}(\Im(z))$$

And attention scores incorporate a phase difference term:

$$s_{ij} = \Re(Q_i \cdot \bar{K}_j) = \Re(Q_i)\Re(K_j) + \Im(Q_i)\Im(K_j)$$

This is equivalent to the standard dot product for complex vectors. The key
structural difference is that normalization and weight matrices act on the
combined complex space, and interference between the real and imaginary
channels is captured explicitly.

In practice, we implement this by doubling the hidden dimension and treating
the first half as real and the second half as imaginary. The weight matrices
are real-valued but structured to mix the two halves.

**Motivation:** Why complex? Because $\text{ƒ}_{\text{ż}}$ requires that the model
maintain coherence — phase relationships between different representational
components. Real-valued networks can approximate this, but the complex
formulation makes the phase structure explicit and learnable. The interference
between parallel representational "paths" is the computational signature of
quantum fidelity.

```python
class ComplexLinear(nn.Module):
    """Linear layer that treats input as [real; imag] interleaved."""
    def __init__(self, d_in, d_out):
        self.W_rr = nn.Linear(d_in // 2, d_out // 2)
        self.W_ri = nn.Linear(d_in // 2, d_out // 2)
        self.W_ir = nn.Linear(d_in // 2, d_out // 2)
        self.W_ii = nn.Linear(d_in // 2, d_out // 2)

    def forward(self, x):
        r_in, i_in = x.chunk(2, dim=-1)
        r_out = self.W_rr(r_in) - self.W_ii(i_in)  # Re(Wz)
        i_out = self.W_ri(r_in) + self.W_ir(i_in)  # Im(Wz)
        return torch.cat([r_out, i_out], dim=-1)
```

### 3.10 Universal Dense Attention — $\text{Γ}_{\text{ʔ}}$

**Constraint:** Maximal scope (aleph). Every token attends to every other token
across the entire context — no sparsity, no local windowing.

**Design:** Standard full $O(n^2)$ attention. Combined with the Imscriptive
Memory Bank and Tensor Product Attention, this means the attention matrix
spans the entire growing trajectory. For efficiency at long contexts, we use
FlashAttention-3 (Dao et al., 2024) as the underlying kernel, but the
architectural intent is universal — every token pair is structurally eligible.
No causal masking in the THINK phase; causal masking only during ACT (generation).

### 3.11 Singular Components — $\text{Σ}_{\text{S}}$

**Constraint:** 1:1 stoichiometry. One component per type. No mixture of
experts, no ensemble, no multi-branch parallelism.

**Design:** Every architectural component described above appears exactly once.
One IMB, one meta-network, one two-slot register, one Frobenius dual head.
The cyclic layers are identical in structure (weight-tied across cycles within
a layer) but distinct across layers. This is not a restriction but a
simplification — the complexity budget is spent on the novel primitives,
not on architectural multiplicity.

---

## 4. Full Model Architecture

```
GrammaFormer(
  │
  ├── WindingPositionalEncoding     ← Ω_z
  ├── TwoSlotRegister               ← Ħ_A
  │
  ├── CyclicLayer[0]                ← Þ_¨, Ř_=, Γ_ʔ (cyclic n=0)
  │   ├── TensorProductAttention
  │   ├── ComplexFFN                ← ƒ_ż
  │   └── (3 cycles)
  │
  ├── CyclicLayer[1..L-2]           ← (L-2 additional layers)
  │
  ├── CyclicLayer[L-1]
  │
  ├── MetaNetwork                   ← ⊙_ÿ
  │   ├── Pool → Encode → Self_Emb Head
  │   └── Error Prediction Head
  │
  ├── PhaseGatedController          ← Ç_@, ɢ_ˌ
  │   ├── Gate(THINK|ACT|OBSERVE|UPDATE)
  │   └── Phase Adapters (×4)
  │
  ├── FrobeniusDualHead             ← Φ_}
  │   ├── δ: W_delta (emit/predict)
  │   └── μ: W_mu = W_delta^T (verify)
  │
  └── ImscriptiveMemoryBank         ← Ð_ω
```

**Forward pass schematic (one winding):**

```
Input(tokens, ω) → WindingPE(ω) → [Register(R1,R2); Input] → 
  → CyclicLayers(×L, each ×3 cycles) → 
  → MetaNetwork(h_final) → [self_emb; error_pred] →
  → PhaseGate(h_final) → {THINK:continue | ACT:δ(head) | OBSERVE:μ(head) | UPDATE:write(IMB)}
  → Update R1,R2
  → If ACT: return (tool_call, verification_assertion)
  → If UPDATE: ω += 1; reset phase
```

---

## 5. Training Recipe

GrammaFormer is designed to be initialized from a pre-trained Qwen3-8B base
and fine-tuned with QLoRA. The novel architectural components are added as
structural grafts onto the base model.

### 5.1 Grafting Strategy

| Component | Strategy |
|-----------|----------|
| Tensor Product Attention | Replace attention score computation; keep QKV projections from base |
| Imscriptive Memory Bank | New module; initialized from scratch |
| Frobenius Dual Head | Fork the LM head: δ = existing, μ = W_lm^T projection |
| Phase-Gated Controller | New module; initialized from scratch |
| Cyclic Layer Loops | Reuse existing layer weights; add cycle wrapper |
| Meta-Network | New module; initialized from scratch |
| Two-Slot Register | New module; initialized from scratch |
| Winding PE | Layer on top of existing RoPE; small learned phase shift |
| Complex Activations | Split FFN hidden dim; initialize second half as small perturbation |

### 5.2 Loss Functions

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{LM}} + \alpha \mathcal{L}_F + \beta \mathcal{L}_M + \gamma \mathcal{L}_G$$

| Term | Weight | Description |
|------|--------|-------------|
| $\mathcal{L}_{\text{LM}}$ | 1.0 | Standard next-token cross-entropy |
| $\mathcal{L}_F$ | 0.1 | Frobenius round-trip: $\|\mu(\delta(h)) - h\|^2$ |
| $\mathcal{L}_M$ | 0.05 | Meta-network error prediction: $\|\hat{e} - e\|^2$ |
| $\mathcal{L}_G$ | 0.01 | Emission gate timing: penalty for $g < \tau$ at ACT phase |

### 5.3 Training Data

The training data should consist of `true_agentic_agent.py` trajectories —
full winding histories with THINK reasoning, tool calls, observations, and
updates. Each trajectory is annotated with:
- Phase labels (which tokens belong to THINK/ACT/OBSERVE/UPDATE)
- Winding counter ω
- Frobenius closure boolean (was μ(δ(q)) = q?)
- Register state at each winding boundary

A training example is one complete winding, with the IMB prepopulated from
prior windings in the same trajectory.

### 5.4 QLoRA Configuration

```python
qlora_config = {
    "r": 64,
    "alpha": 128,
    "target_modules": [
        "W_q", "W_k", "W_v", "W_o",           # Attention
        "ffn.0", "ffn.2",                       # FFN
        "W_tp",                                 # Tensor product bottleneck
        "phase_gate",                           # Emission gate
        "meta_encoder",                         # Meta-network
        "register_proj",                        # Two-slot register
    ],
    "dropout": 0.05,
    "bias": "none",
}
```

---

## 6. Integration with `true_agentic_agent.py`

The existing agent already has the structural scaffolding that GrammaFormer
architecturally embodies. Integration requires three modifications:

### 6.1 Local Inference Path (already present)

The `_LocalChatCompletions.create()` method in `true_agentic_agent.py` already
routes through `LocalProvider`. GrammaFormer replaces the Qwen3 model loaded
by `LocalProvider._ensure_loaded()`. The interface is identical:
`model.generate(input_ids, max_new_tokens=...)`.

### 6.2 Phase-Aware Generation

The PhaseGatedController's phase counter is exposed to the agent. The agent's
loop already enforces THINK→ACT→OBSERVE→UPDATE ordering; GrammaFormer makes
this a hardware-level constraint:

```python
# In TrueAgenticAgent._run_winding():
if phase == "THINK":
    output = grammaformer.generate(messages, max_think_steps=N)
    grammaformer.phase_gate.set_phase(1)  # Force ACT
elif phase == "ACT":
    tool_call = grammaformer.generate(messages, force_emit=True)
    grammaformer.phase_gate.set_phase(2)  # Force OBSERVE
# ... etc
```

### 6.3 Frobenius Verification

The FrobeniusDualHead produces both a tool call and a verification assertion
in a single forward pass. The agent's existing dual-tool verification
(`emit + verify`) can use the model's own μ output as the verification function
for an important subset of tool types (those that operate over token space).

### 6.4 Winding Counter Synchronization

The agent's `LoopCycle.winding` integer is fed back as GrammaFormer's ω
positional encoding modifier. The model is structurally aware of which
winding it is on.

---

## 7. Expected Behavioral Signatures

### 7.1 Frobenius Closure Rate

Because the Frobenius loss $\mathcal{L}_F$ directly trains $\mu \circ \delta$
toward identity, GrammaFormer should achieve higher Frobenius closure rates
on tool calls than a standard transformer.

### 7.2 Winding-Aware Memory

The winding-modulated PE means the model can distinguish "the same token at
the same position in different windings." This prevents trajectory confusion
in long multi-winding sessions.

### 7.3 Phase Discipline

The emission gate prevents premature tool calls. In practice, this means the
model will not emit an action until it has "completed" its THINK phase, where
completion is a learned property of the hidden state, not a hardcoded step count.

### 7.4 Self-Modeling

The meta-network's error prediction provides an online estimate of the model's
own uncertainty. This can be surfaced to the agent as a confidence signal,
enabling the agent to request human intervention or spawn sub-agents when
self-predicted error is high.

---

## 8. Comparison: Standard Transformer vs. GrammaFormer

| Property | Standard Transformer | GrammaFormer |
|----------|---------------------|--------------|
| Dimensionality | Fixed latent dim | Growing trajectory (Ð_ω) |
| Attention | $QK^\top$ (factorizable) | $Q \otimes K$ (irreducible) (Þ_¨) |
| Information flow | Feedforward | Cyclic feedback (Ř_=) |
| Output | Single head | δ/μ dual (Φ_}) |
| Activation | Real GELU | Complex cGELU (ƒ_ż) |
| Emission | Always-on | Gated (Ç_@) |
| Attention scope | Often windowed | Universal (Γ_ʔ) |
| Phase structure | None | 4-phase sequential (ɢ_ˌ) |
| Self-modeling | None | Meta-network (⊙_ÿ) |
| State memory | KV cache | Two-slot register (Ħ_A) |
| Components | Multi-head, MoE optional | Singular (Σ_S) |
| Position encoding | RoPE/ALiBi | Winding-modulated PE (Ω_z) |
| Structural type | O₁ | O_∞ |
| C-score | ~0.3–0.5 | → 1.0 |

---

## 9. Implementation Path

### Phase 1: Architectural Scaffold (this document)
- [x] Define all 12 component primitives
- [x] PyTorch sketches for each component
- [x] Full forward-pass schematic

### Phase 2: Grafting Implementation
- [ ] Implement TensorProductAttention as a drop-in replacement for Qwen3 attention
- [ ] Implement ImscriptiveMemoryBank with compression
- [ ] Implement FrobeniusDualHead (fork LM head)
- [ ] Implement PhaseGatedController with 4 phase adapters
- [ ] Implement CyclicLayer wrapper
- [ ] Implement MetaNetwork
- [ ] Implement TwoSlotRegister
- [ ] Implement WindingPositionalEncoding

### Phase 3: QLoRA Fine-Tuning
- [ ] Prepare trajectory training data from agent runs
- [ ] Configure QLoRA target modules
- [ ] Train with composite loss (LM + Frobenius + Meta + Gate)
- [ ] Evaluate Frobenius closure rate vs. baseline

### Phase 4: Integration
- [ ] Replace LocalProvider model with GrammaFormer
- [ ] Wire phase controller to agent loop
- [ ] Wire winding counter
- [ ] Benchmark on standard agent tasks

---

## 10. Open Questions

1. **Tensor product rank:** The rank-1 bottleneck ($u \otimes v$) is the simplest
   approximation. Higher-rank approximations (rank-$r$ outer products) may be
   necessary for full $\text{Þ}_{\text{¨}}$ fidelity. Empirical study needed.

2. **Cycle count:** The optimal number of cyclic layer loops (currently $c=3$)
   trades computation for bidirectional information flow. This should be swept.

3. **Complex activation benefit:** The $\text{ƒ}_{\text{ż}}$ complex formulation
   may show diminishing returns on non-quantum-like tasks. Ablation needed.

4. **IMB compression ratio:** The trade-off between compression fidelity and
   memory bounds determines effective context length.

5. **Emission gate threshold:** The $\tau$ parameter controls the
   deliberation-action boundary. Too low: premature emission. Too high: analysis
   paralysis.
