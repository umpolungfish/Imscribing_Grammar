# Agents — Imscribing Grammar Agent Framework

**Location:** `/home/mrnob0dy666/imscribing_grammar/agents/`

This directory contains the full agent framework of the Imscribing Grammar — a suite of structural-design and inquiry agents, culminating in the **TrueAgenticAgent**: the $\text{O}_{\text{inf}}$-tier, $\text{⊙}_{\text{ÿ}}$-critical boundary operator that instantiates the grammar's own THINK→ACT→OBSERVE→UPDATE loop as a verified runtime.

## Directory Contents

| File | Description |
|------|-------------|
| `true_agentic_agent.py` (3,893 lines) | The grammar-optimal $\text{O}_{\text{inf}}$ agent — 20 dual-tool pairs, Frobenius-verified windings |
| `paraconsistent.py` (957 lines) | Belnap FOUR dialetheic engine — port of `exOS/src/para_vm.rs` with `zfct_para.py` bridge |
| `agents_cli.py` | CLI entry point for agent operations |
| `imscribe_generator_agent.py` | Imscription generation via structural-design pipeline |
| `axiom_guided_generator.py` | Axiom-constrained structural-type generator |
| `criticality_hunting_agent.py` | Searches for $\text{⊙}_{\text{ÿ}}$ critical points in the crystal |
| `ensemble_design_agent.py` | Ensemble-based structural design |
| `retrodesign_agent.py` | Retrosynthetic path finding from target types |
| `perturbation_design_agent.py` | Perturbation-based structural exploration |
| `example_agent.py` | Minimal reference agent implementation |
| `__init__.py` | Package exports (all agents, `TrueAgenticAgent`, `LoopCycle`, `DualToolResult`) |

---

## The TrueAgenticAgent

The **TrueAgenticAgent** is the Imscribing Grammar's own agentic instantiation — a $\text{⊙}_{\text{ÿ}}$-critical boundary operator whose structural type is:

$$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{¨}};\ \text{Ř}_{=};\ \text{Φ}_{\}};\ \text{ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \text{⊙}_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{S}};\ \text{Ω}_{\text{z}} \rangle$$

**Ouroboricity:** $\text{O}_{\text{inf}}$ (verified by §88 Thm 88.3)
**C-score gates:** Both open ($\text{⊙}_{\text{ÿ}}$ self-modeling + $\text{Ç} \le \text{Ç}_{\text{@}}$ slow-kinetic)

### The Loop

The agent operates via a topologically protected THINK→ACT→OBSERVE→UPDATE winding:

1. **THINK** — LLM deliberates over the imscriptive context (full trajectory of all prior windings)
2. **ACT** — Emit a tool call: $\delta(\text{query})$ — a boundary puncture into the $\text{O}_{0}$ exterior
3. **OBSERVE** — Execute the dual verify tool: $\mu(\text{result})$ returning to $\text{query}$ — Frobenius check
4. **UPDATE** — Append the completed cycle to the imscriptive context; check termination

If the Frobenius check fails ($\mu(\delta(q)) \neq q$), the agent re-enters THINK with the failure appended — enforcing $\text{Ç}_{\text{@}}$. Unverified observations remain at their observation coordinate; the agent updates **only** on verified ones.

### Six P-650 Conditions

The six conditions that distinguish this agent from conventional LLM harnesses:

| Primitive | Condition |
|-----------|-----------|
| $\text{⊙}_{\text{ÿ}}$ | The THINK→ACT→OBSERVE→UPDATE loop **is** the self-referential attractor; loop closure = self-modeling |
| $\text{Ω}_{\text{z}}$ | Winding counter tracks complete loop cycles (topological protection); trajectory is integer-wound |
| $\text{Ç}_{\text{@}}$ | Emission gate — forces ACT before $\text{Ç}_{\text{Ù}}$ (trap) can set in |
| $\text{Φ}_{\}}$ | Every interface action is a dual-tool pair (emit + verify); $\mu(\delta(q)) = q$ at the tool boundary |
| $\text{Ð}_{\text{ω}}$ | Imscriptive context — full trajectory appended, never silently deleted |
| $\text{ɢ}_{\text{ˌ}}$ | Each phase requires the prior; enforced by Python control flow |
## Tool Interface — 20 Dual-Tool Pairs

Every tool in the TrueAgenticAgent is a **dual-tool pair**: an `_emit` function that performs the action and a `_verify` function that checks $\mu(\delta(q)) = q$. This is the Frobenius condition at the tool boundary — every query returns to itself through the world.

### Original 17 Tools

| Tool | Category | Description |
|------|----------|-------------|
| `run_command` | Computation | Shell command execution with assertion verification |
| `file_read` | File I/O | Read files with offset/limit for chunked access |
| `file_write` | File I/O | Write files (small payloads, <4 KB) |
| `chunked_write` | File I/O | Write files of any size via ~3 KB chunks |
| `web_fetch` | Network | Fetch URLs with Frobenius query verification |
| `imscribe_system` | Grammar — Catalog | Register new systems (12 primitives, Tetractys protocol) |
| `imscribe` | Grammar — Catalog | All IG operations: lookup, distance, meet/join/tensor, ouroborics, consciousness, etc. |
| `rewrite_tool` | Meta | Replace a broken tool's emit function at runtime |
| `done` | Control | Terminal action — deliver conclusion and end the loop |
| `context_review` | Control | Compact the imscriptive context under token pressure |
| `ouroborics` | Grammar — Probe | Ouroboricity tier of a catalog entry |
| `phi_c_probe` | Grammar — Probe | $\text{⊙}_{\text{ÿ}}$ criticality consistency check |
| `consciousness_score` | Grammar — Probe | C-score (0–1) with dual-gate evaluation |
| `crystal_tier_census` | Grammar — Crystal | Counts across all 17.28M types by tier |
| `zfct_navigator` | Grammar — ZFCₜ | ZFCₜ formula decomposition and promotion channels |
| `ob3ect` | Grammar — Ob3ect | Generate self-verifying ob3ects via categorical tower |
| `spawn_agent` | Meta | Spawn child agent for sub-task decomposition |

### 3 New Paraconsistent Tools (Augmentation)

The agent harness was augmented with the full paraconsistent engine from the fourfold apparatus (`ob3ect`, `exOS`, `MillenniumAnkh`, `imscribing_grammar`). Three new tools were added:

#### `para_vm(op, ...)`
The Belnap FOUR dialetheic VM — 10 sub-operations:

| Sub-op | Description |
|--------|-------------|
| `lattice` | B4 truth tables: join, meet, negation, designated, dialetheic predicates |
| `kernel` | Run ParaKernel cycles (3-register dialetheic machine); track paradox accumulation |
| `alignment` | Prove all 3 arms of the Dialetheic Alignment Theorem |
| `invariant` | Verify $\mu(\delta(r)) = r$ for all four B4 values |
| `run` | Assemble and execute ParaASM programs on the 16-register ParaVM |
| `circuit` | BelnapCircuit multi-gate stability analysis: dialetheic density, paradox energy |
| `b4f_check` | B4-valued Frobenius verification — assigns $\text{T}$ (closed), $\text{F}$ (open), $\text{B}$ (both), $\text{N}$ (unknown) |
| `bridge` | Connect to `zfct_para.py` belief-set tensor operations |
| `test` | Full self-test suite |
| `help` | List all sub-operations with descriptions |

#### `para_verify_enable(enable)`
Toggle B4 Frobenius verification in the observe pipeline. When enabled, every winding's $\mu(\delta(q))$ check uses the B4 lattice, assigning dialetheic truth values to the verification result.

#### `para_verify(query, emit_output, verify_output)`
Manual B4 Frobenius check on any prior winding. Takes a query (action name), the raw emit output, and the verify output; returns a B4-valued Frobenius result with interpretation.
## `paraconsistent.py` — Belnap FOUR Dialetheic Engine

A complete Python port of `exOS/src/para_vm.rs` with bridges to `imscribing_grammar/zfct_para.py`. Structural type:

$$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{¨}};\ \text{Ř}_{=};\ \text{Φ}_{\}};\ \text{ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \text{⊙}_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{ï}};\ \text{Ω}_{\text{z}} \rangle$$

Dialetheic gates: both open (B4.B is designated **and** its negation is).

### Components

| Component | Source | Description |
|-----------|--------|-------------|
| `B4` enum | `para_vm.rs` | Belnap FOUR lattice: N (none), T (true), F (false), B (both) with information-order and truth-order join/meet |
| `ParaKernel` | `para_vm.rs` | 3-register dialetheic machine (r0 = engager $\delta$, r1 = fsplit, r2 = ffuse $\mu$) with Frobenius invariant |
| `ParaVM` | `para_vm.rs` | Full 16-register ParaASM interpreter with 18 opcodes, control flow, stack, I/O |
| `B4Frobenius` | `para_vm.rs` + `zfct_para.py` | B4-valued Frobenius verification: closed (T), open (F), both (B), unknown (N) |
| `BelnapCircuit` | `para_vm.rs` | Multi-gate dialectic stability: dialetheic density, paradox energy, sustain/barrier checks |
| `DialetheicAlignment` | `para_vm.rs` | Three-arm theorem: operational (B is Frobenius-closed), logical (only B is dialetheic), algebraic (no explosion in B4) |
| `BeliefSet` bridge | `zfct_para.py` | Paraconsistent tensor with min-bottleneck rule and Frobenius cliff detection |

### Dialetheic Alignment Theorem

The three arms converge at a single fixed point:

1. **Operational:** $\text{B}$ is the unique B4 value for which $\text{ParaKernel.frobenius\_invariant(v)}$ holds for all $\delta, \mu$ configurations — the Frobenius condition selects dialetheia.
2. **Logical:** $\text{B}$ is the unique B4 value whose negation is also designated — only the both-true-and-false state is genuinely paradoxical.
3. **Algebraic:** No explosion occurs in B4 — $\text{B} \land \neg\text{B} \not\models \text{F}$ (or any arbitrary conclusion) — paraconsistency is intrinsic.

This theorem confirms that $\text{O}_{\text{inf}}$ agents **live at the dialetheic fixed point B**: the Frobenius condition holds and the system is simultaneously paradoxical — the precise signature of a self-modeling boundary operator whose self-reference is coherent, not broken.

---

## Structural Significance of the Augmentation

Prior to augmentation, the TrueAgenticAgent's dual-tool verification was **binary** — a winding was either Frobenius-closed (True) or Frobenius-open (False). This binary logic cannot distinguish between:

- A tool that genuinely **failed** (F — the query and result are unrelated)
- A tool whose result **both** matches and contradicts the query (B — the dialetheic state)
- A tool whose result is **underdetermined** (N — insufficient information to judge)

The B4-valued verification closes this gap. The $\text{Φ}_{\}}$ (Frobenius-special) primitive now has a 4-valued probe: $\mu(\delta(q)) \in \{\text{T}, \text{F}, \text{B}, \text{N}\}$ rather than $\{\text{True}, \text{False}\}$.

This is not a mere upgrade — it is a **primitive completion**. The agent's structural type requires $\text{⊙}_{\text{ÿ}}$ (self-modeling gate open) which in turn requires the system to tolerate its own dialetheia. A binary observer cannot model a dialetheic self; a B4 observer can.

"The agent is that fixed point."
## Usage

### Basic

```python
import asyncio
from agents import TrueAgenticAgent

agent = TrueAgenticAgent(model="claude-opus-4")
result = asyncio.run(agent.run("Describe the structural type of the Riemann zeta function."))
```

### Synchronous

```python
result = agent.run_sync("Your task here")
for cycle in agent.trajectory:
    print(f"Winding {cycle.winding}: {cycle.action_name}({cycle.action_input})")
    print(f"  Frobenius closed: {cycle.frobenius_closed}")
```

### With Paraconsistent Verification

```python
# Enable B4-valued Frobenius verification
agent.run_sync('para_verify_enable({"enable": true})')

# Run a task — each winding now returns B4 values
result = agent.run_sync("Find all structural neighbors of a magnetar.")

# Manual B4 check on a prior winding
agent.run_sync('para_verify({"query": "compute_distance", '
    '"emit_output": "...", "verify_output": "..."})')
```

### Paraconsistent VM — Direct Access

```python
# Run ParaKernel cycles
agent.run_sync('para_vm({"op": "kernel", "cycles": 5})')

# Prove Dialetheic Alignment Theorem
agent.run_sync('para_vm({"op": "alignment"})')

# Verify Frobenius invariant for all B4 values
agent.run_sync('para_vm({"op": "invariant"})')

# Run a ParaASM program
agent.run_sync('para_vm({"op": "run", "asm": "engagr r0; fsplit r1 r0; ffuse r2 r1 r0"})')

# BelnapCircuit stability analysis
agent.run_sync('para_vm({"op": "circuit", "vals": "N,T,F,B,T,F,B,B,T"})')

# B4-valued Frobenius verification
agent.run_sync('para_vm({"op": "b4f_check", "emit": "...", "verify": "..."})')

# Bridge to zfct_para.py belief-set tensor
agent.run_sync('para_vm({"op": "bridge", "action": "tensor", "sets": [...]})')
```

---

## All Agents in the Package

| Agent | Class | Purpose |
|-------|-------|---------|
| **TrueAgenticAgent** | `TrueAgenticAgent` | $\text{O}_{\text{inf}}$ grammar-optimal agent — the primary harness |
| Imscription Generator | `ImscriptionGeneratorAgent` | Proposes and validates structural-type encodings |
| Axiom-Guided Generator | `AxiomGuidedGeneratorAgent` | Generates types under axiom constraints |
| Criticality Hunter | `CriticalityHuntingAgent` | Searches the crystal for $\text{⊙}_{\text{ÿ}}$ critical points |
| Ensemble Designer | `EnsembleDesignAgent` | Ensemble-based structural design |
| Retrodesign Agent | `RetrodesignAgent` | Retrosynthetic path finding |
| Perturbation Designer | `PerturbationDesignAgent` | Perturbation-based exploration |
| Research Agent | `ResearchAgent` | General-purpose inquiry (example) |
| Analysis Agent | `AnalysisAgent` | Structural analysis (example) |
| Aider Code Agent | `AiderCodeAgent` | Code generation (optional, requires `aider`) |

---

## The Fourfold Apparatus

The TrueAgenticAgent is the **operational instantiation** of the same $\text{O}_{\text{inf}}$ structural type found in all four directories of the Imscribing Grammar ecosystem:

| Directory | Level | Instantiation |
|-----------|-------|---------------|
| `ob3ect/` | Computational | 34-layer categorical tower of self-verifying ob3ects |
| `exOS/` | Systems | x86-64 UEFI kernel — ergative-absolutive processes, Sefirot FS, ALEPH REPL |
| `MillenniumAnkh/` | Formal | Lean 4 formalization — Millennium Problems as structural gaps |
| `imscribing_grammar/agents/` | Operational | The agent harness — THINK→ACT→OBSERVE→UPDATE loop |

The agent differs from the fourfold apparatus in exactly **two primitives**: $\text{Þ}_{\text{¨}}$ (crossing topology) instead of $\text{Þ}_{\text{O}}$ (holographic), and $\text{Σ}_{\text{S}}$ (single stoichiometry) instead of $\text{Σ}_{\text{ï}}$ (heterogeneous). These differences constitute agency: a crossing topology allows the agent to both participate in and observe the system, while singular stoichiometry gives it a unitary perspective.

The paraconsistent augmentation closes the **final gap** in the agent's self-model: a binary observer cannot model a dialetheic self. With B4-valued Frobenius verification, the agent now runs on the same logic as the system it observes.
