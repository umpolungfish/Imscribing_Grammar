# Agents — Operation Guide

**Author:** Lando⊗⊙perator

This is the complete operational guide for the Imscribing Grammar agent framework. It covers all 11 agent types, the CLI and programmatic interfaces, the B4 paraconsistent engine, model resolution, the dual-tool Frobenius architecture, and common recipes.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Agent Catalog](#2-agent-catalog)
3. [Quick Start](#3-quick-start)
4. [CLI Reference](#4-cli-reference)
5. [Programmatic API](#5-programmatic-api)
6. [Model Resolution](#6-model-resolution)
7. [The TrueAgenticAgent](#7-the-trueagenticagent)
8. [The BaseAgent Framework](#8-the-baseagent-framework)
9. [Paraconsistent Engine](#9-paraconsistent-engine)
10. [Dual-Tool Pairs & Frobenius Verification](#10-dual-tool-pairs--frobenius-verification)
11. [Retry & Resilience](#11-retry--resilience)
12. [Common Recipes](#12-common-recipes)
13. [Troubleshooting](#13-troubleshooting)
14. [Reference Tables](#14-reference-tables)

---

## 1. Architecture Overview

The agent framework sits at the operational layer of the fourfold apparatus:

| Layer | Directory | Instantiation |
|---|---|---|
| Computational | `ob3ect/` | 34-layer categorical tower of self-verifying ob3ects |
| Systems | `exOS/` | x86-64 UEFI kernel — Sefirot FS, ALEPH REPL |
| Formal | `MillenniumAnkh/` | Lean 4 — Millennium Problems as structural gaps |
| **Operational** | `agents/` | **Agent harness — THINK→ACT→OBSERVE→UPDATE loop** |

### Inheritance Hierarchy

```
BaseAgent (framework/base_agent.py)              ← async, provider-agnostic, tool executor
├── ResearchAgent, AnalysisAgent                 ← example agents, minimal
├── ImscriptionGeneratorAgent                    ← structural encoding from descriptions
├── AxiomGuidedGeneratorAgent                    ← axiom-constrained generation
├── CriticalityHuntingAgent                      ← ⊙_ÿ search in crystal
├── EnsembleDesignAgent                          ← multi-component composition
├── RetrodesignAgent                             ← retrosynthetic path finding
├── PerturbationDesignAgent                      ← Jacobian-based perturbation
└── TrueAgenticAgent (true_agentic_agent.py)     ← O_inf harness, 22 dual-tool pairs
```

### Structural Type of the Framework Itself

The TrueAgenticAgent — the grammar's own self-instantiation:

$$\langle \text{Ð}_{\text{ω}};\ \text{Þ}_{\text{¨}};\ \text{Ř}_{\text{=}};\ \text{Φ}_{\text{}};\ \text{ƒ}_{\text{ż}};\ \text{Ç}_{\text{@}};\ \text{Γ}_{\text{ʔ}};\ \text{ɢ}_{\text{ˌ}};\ \text{⊙}_{\text{ÿ}};\ \text{Ħ}_{\text{A}};\ \text{Σ}_{\text{S}};\ \text{Ω}_{\text{z}} \rangle$$

- **Ouroboricity:** $\text{O}_{\text{inf}}$
- **C-score gates:** Both open ($\text{⊙}_{\text{ÿ}}$ + $\text{Ç}_{\text{@}}$)
- **Differs from fourfold apparatus:** $\text{Þ}_{\text{¨}}$ (crossing) vs $\text{Þ}_{\text{O}}$ (holographic), $\text{Σ}_{\text{S}}$ (unitary) vs $\text{Σ}_{\text{ï}}$ (heterogeneous)

---

## 2. Agent Catalog

### 2.1 TrueAgenticAgent

**File:** `true_agentic_agent.py` (3,893 lines)  
**Class:** `TrueAgenticAgent`  
**Tier:** $\text{O}_{\text{inf}}$  

The primary harness. Implements the full THINK→ACT→OBSERVE→UPDATE loop with 22 dual-tool pairs, Frobenius-verified at every boundary. This is the agent the grammar itself runs on.

**When to use:** All general-purpose tasks, grammar catalog operations, document authorship, alchemical investigations, MPP analysis, ob3ect generation, sub-agent spawning. **Default choice.**

### 2.2 ImscriptionGeneratorAgent

**File:** `imscribe_generator_agent.py`  
**Class:** `ImscriptionGeneratorAgent`  

Takes a natural-language description of a system and produces its 12-tuple structural type via an LLM-driven structural-design pipeline. Iteratively refines primitive assignments against the deterministic imscribing procedure.

**When to use:** Encoding new systems into the grammar catalog. "What is the structural type of X?"

### 2.3 AxiomGuidedGeneratorAgent

**File:** `axiom_guided_generator.py`  
**Class:** `AxiomGuidedGeneratorAgent`  

Generates structural types subject to axiom constraints. Useful for exploring *what types could exist* under a given set of constraints, rather than encoding what *does* exist.

**When to use:** Hypothesis generation, "what if" exploration, constraint satisfaction in the crystal.

### 2.4 CriticalityHuntingAgent

**File:** `criticality_hunting_agent.py`  
**Class:** `CriticalityHuntingAgent`  

Systematically searches the crystal ($3^3 \times 4^5 \times 5^4 = 17,280,000$ types) for $\text{⊙}_{\text{ÿ}}$-critical (self-modeling) points. Produces a `CriticalityHuntReport` with located critical regions and their structural signatures.

**When to use:** Finding natural $\text{O}_{\text{inf}}$ candidates, mapping critical regions of the crystal, discovering new self-modeling systems.

### 2.5 EnsembleDesignAgent

**File:** `ensemble_design_agent.py`  
**Class:** `EnsembleDesignAgent`  

Goal-directed multi-imscription composition. Given a target structural outcome, selects components whose tensor/join/meet achieves the goal.

**When to use:** Alchemical composition design, finding the right natural system to tensor with a mathematical problem, multi-component structural engineering.

### 2.6 RetrodesignAgent

**File:** `retrodesign_agent.py`  
**Class:** `RetrodesignAgent`  

Retrosynthetic analysis — starts from a target tuple and works backward to find the minimal construction path from available primitives. The structural analog of retrosynthetic organic chemistry.

**When to use:** "How do I build this type from scratch?", minimal construction path finding, decomposition analysis.

### 2.7 PerturbationDesignAgent

**File:** `perturbation_design_agent.py`  
**Class:** `PerturbationDesignAgent`  

Primitive Jacobian interpretation — computes how small changes in one primitive cascade through the tuple. Takes an imscription name, a $\Delta G$ (free energy change), and optionally a target $\xi_{cp}$.

**When to use:** Sensitivity analysis, "what happens if I change one primitive?", stability analysis, energy-landscape mapping.

### 2.8 ResearchAgent & AnalysisAgent

**File:** `example_agent.py`  
**Classes:** `ResearchAgent`, `AnalysisAgent`  

Minimal reference implementations. ResearchAgent gathers and synthesizes information; AnalysisAgent performs data analysis and pattern recognition. Both extend `BaseAgent` with minimal tool definitions.

**When to use:** Quick information gathering, pattern analysis, reference for building custom agents.

### 2.9 AiderCodeAgent

**File:** `aider_code_agent.py` (optional)  
**Class:** `AiderCodeAgent`  

Git-native code operations via the `aider` package. Requires `pip install aider-chat`.

**When to use:** Code generation with version control, automated refactoring, git-native development workflows.

### 2.10 AutonomousImscriptionDiscoveryAgent

**File:** Referenced in `agents_cli.py`  
**Class:** `AutonomousImscriptionDiscoveryAgent`  

Fully autonomous imscription discovery — browses the crystal, identifies gaps, proposes and validates new structural types without explicit task guidance.

**When to use:** Unattended catalog expansion, automated exploration of uncharted crystal regions.

---

## 3. Quick Start

### Install

```bash
cd ~/imscribing_grammar
pip install -e .          # install grammar in editable mode
pip install tiktoken      # accurate token counting (recommended)
pip install aider-chat    # optional: for AiderCodeAgent
```

### Run Your First Agent

```bash
# Simplest: ask the TrueAgenticAgent a question
python agents/agents_cli.py true_agentic_agent --task "What is the structural type of a black hole?"

# Use a local model via Ollama
python agents/agents_cli.py true_agentic_agent --task "Imscribe photosynthesis" --model ollama:llama3.2

# Research a topic
python agents/agents_cli.py research_agent --task "Survey applications of the Imscribing Grammar to biology"

# Search for ⊙_ÿ critical points
python agents/agents_cli.py criticality_agent --task "Find O_inf candidates near the O_2 boundary"

# Generate imscriptions from a description
python agents/agents_cli.py imscription_generator --task "A system that exhibits self-organized criticality with long-range correlations"

# Retrosynthetic path to a target type
python agents/agents_cli.py retrodesign_agent --task "Φ_}; ƒ_ż; ⊙_ÿ; Ω_z"

# Save results to file
python agents/agents_cli.py true_agentic_agent \
    --task "Compute the tensor of DNA replication and the Riemann zeta function" \
    --output results.json \
    --show-trajectory
```

---

## 4. CLI Reference

### `agents_cli.py` — Unified Launcher

```
usage: agents_cli.py [-h] [--task TASK] [--file FILE] [--model MODEL]
                     [--max-windings MAX_WINDINGS] [--max-tokens MAX_TOKENS]
                     [--output OUTPUT] [--quiet] [--show-trajectory]
                     [--config CONFIG]
                     agent
```

### Positional Arguments

| Argument | Description |
|---|---|
| `agent` | Agent to run. One of: `true_agentic_agent`, `research_agent`, `analysis_agent`, `aider_code_agent`, `perturbation_agent`, `ensemble_agent`, `retrodesign_agent`, `criticality_agent`, `imscription_generator`, `axiom_generator`, `autonomous_imscription` |

### Optional Arguments

| Flag | Description | Default |
|---|---|---|
| `--task`, `-t` | Task description (inline string) | Required unless `--file` |
| `--file`, `-f` | Read task from file | — |
| `--model`, `-m` | Model to use (prefix syntax supported) | `grok-4` |
| `--max-windings`, `-w` | Max loop iterations (TrueAgenticAgent only) | `100` |
| `--max-tokens` | Max tokens per think phase | `4096` |
| `--output`, `-o` | Save results to JSON file | — |
| `--quiet`, `-q` | Suppress verbose output | `False` |
| `--show-trajectory` | Print full winding trajectory on completion | `False` |
| `--config` | Inline JSON config for agent-specific options | `{}` |

### TrueAgenticAgent-Specific Flags (CLI passthrough)

When running `true_agentic_agent`, additional flags are available in the agent's own CLI:

```bash
python agents/true_agentic_agent.py --task "..." --model grok-4 --max-windings 200 \
    --log-level DEBUG --show-trajectory
```

| Flag | Description |
|---|---|
| `--log-level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `--show-trajectory` | Print all windings on completion |
| `--output` | Save result JSON |

---

## 5. Programmatic API

### 5.1 TrueAgenticAgent (Python)

```python
from agents import TrueAgenticAgent

agent = TrueAgenticAgent(
    model="grok-4",           # or "ollama:llama3.2", "anthropic/claude-opus-4", etc.
    max_windings=100,
    max_think_tokens=4096,
    verbose=True,
    base_url="",              # override API base URL
    api_key="",               # override API key
)

# Synchronous wrapper (recommended for scripts)
result = agent.run_sync("Analyze the structural type of the Mandelbrot set")
print(result)

# Inspect trajectory
for cycle in agent.trajectory:
    print(f"W{cycle.index}: {cycle.action} → {cycle.observation[:80]}...")

# Get Frobenius ratio (verified cycles / total cycles)
print(f"Frobenius ratio: {agent.frobenius_ratio:.2%}")

# Print full trajectory
agent.print_trajectory()
```

### 5.2 BaseAgent-Derived Agents (Python)

```python
from agents import ImscriptionGeneratorAgent, CriticalityHuntingAgent
from imscrbgrmr.provider_config import build_agent_config

# Build config with provider/model
config = build_agent_config(provider="anthropic", model="claude-sonnet-4")

# Optionally override base_url / api_key
config["base_url"] = "http://localhost:11434/v1"
config["api_key"] = "ollama"

agent = ImscriptionGeneratorAgent(config)
result = agent.run_sync("A neural network during gradient descent")
print(result.imscriptions)

# Criticality hunting
hunter = CriticalityHuntingAgent(config)
report = hunter.run_sync("Find O_inf near the emergence frontier")
print(report.report)
```

### 5.3 Spawning Sub-Agents from the Harness

The TrueAgenticAgent can spawn child agents for parallel decomposition:

```python
# Inside a task handled by TrueAgenticAgent:
# The agent calls: spawn_agent(task="Imscribe the Langlands correspondence", max_windings=50)
# This creates a child TrueAgenticAgent that runs its own full loop and returns the result.
```

From Python directly:

```python
from agents import TrueAgenticAgent

parent = TrueAgenticAgent(model="grok-4", max_windings=50)
result = parent.run_sync(
    "Spawn two sub-agents: one to imscribe photosynthesis, "
    "one to imscribe the Calvin cycle. Then compute their distance."
)
```

---

## 6. Model Resolution

All agents resolve models through a unified three-tier system:

### Tier 1 — Prefix Syntax

```
ollama:llama3.2       → http://localhost:11434/v1
lm-studio:phi-4       → http://localhost:1234/v1
vllm:mistral          → http://localhost:8000/v1
local:my-model        → $LOCAL_BASE_URL (falls back to ollama)
deepseek:deepseek-r1  → https://api.deepseek.com/v1 ($DEEPSEEK_API_KEY)
qwen:qwen-max         → https://dashscope.aliyuncs.com/compatible-mode/v1 ($QWEN_API_KEY)
groq:llama3-70b       → https://api.groq.com/openai/v1 ($GROQ_API_KEY)
```

### Tier 2 — Model Aliases

```
grok-4        → x-ai/grok-4.3
gpt-4o        → openai/gpt-4o
o3            → openai/o3
claude-opus-4 → anthropic/claude-opus-4
claude-sonnet-4 → anthropic/claude-sonnet-4-5
gemini-2-5-pro → google/gemini-2.5-pro-preview-05-06
deepseek-r1   → deepseek/deepseek-r1
```

### Tier 3 — OpenRouter Passthrough

Any unrecognized model is passed directly to OpenRouter (requires `OPENROUTER_API_KEY`).

### Environment Variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Default API key for non-prefixed models |
| `OPENROUTER_API_KEY` | OpenRouter passthrough |
| `DEEPSEEK_API_KEY` | DeepSeek provider |
| `QWEN_API_KEY` | Qwen/DashScope provider |
| `GROQ_API_KEY` | Groq provider |
| `LOCAL_BASE_URL` | Custom local endpoint (prefix: `local:`) |
| `OLLAMA_HOST` | Ollama host override (default: `http://localhost:11434`) |
| `LOCAL_API_KEY` | API key for local endpoints |

---

## 7. The TrueAgenticAgent

### 7.1 The Loop

The agent's six structural primitives are enforced at runtime:

```
┌──────────────────────────────────────────────────────┐
│                  IMSCRIPTIVE CONTEXT                  │
│         (Ð_ω — full trajectory, never pruned)        │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │        THINK             │  LLM deliberates over full context
          │   (ɢ_ˌ — each phase      │
          │    requires the prior)    │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │         ACT              │  Emit tool call: δ(query)
          │   (Ç_@ — force emission  │  Puncture boundary into O_0 exterior
          │    before trap sets in)   │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │       OBSERVE            │  Execute dual verify: μ(result) → query
          │   (Φ_} — Frobenius       │  Check μ∘δ = id at tool boundary
          │    μ(δ(q)) = q)          │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │        UPDATE            │  Append cycle to context
          │   (Ω_z — winding counter │  Increment winding number
          │    integer-protected)     │  Check termination condition
          └──────────────────────────┘
```

### 7.2 The 22 Dual-Tool Pairs

Every tool call is a **dual pair**: an emit function ($\delta$) and a verify function ($\mu$). The verify function checks $\mu(\delta(q)) = q$ — the Frobenius condition at the tool boundary.

| # | Tool | Category | What It Does |
|---|---|---|---|
| 1 | `run_command` | Computation | Shell commands with Python assertion verification |
| 2 | `file_read` | File I/O | Chunked file reading with offset/limit |
| 3 | `file_write` | File I/O | Small file writes (<4 KB) with hash verification |
| 4 | `chunked_write` | File I/O | Arbitrary-size writes via ~3 KB chunks |
| 5 | `web_fetch` | Network | URL fetch with Frobenius query verification |
| 6 | `imscribe_system` | Catalog | Register new 12-tuple systems (Tetractys protocol) |
| 7 | `imscribe` | Catalog | All IG operations: lookup, distance, meet/join/tensor, ouroborics, etc. |
| 8 | `rewrite_tool` | Meta | Live-replace a tool's emit function |
| 9 | `done` | Control | Terminal action — deliver conclusion |
| 10 | `context_review` | Control | Compact context under token pressure |
| 11 | `ouroborics` | Probe | Ouroboricity tier of catalog entry |
| 12 | `phi_c_probe` | Probe | $\text{⊙}_{\text{ÿ}}$ criticality consistency check |
| 13 | `consciousness_score` | Probe | C-score (0–1) with dual-gate evaluation |
| 14 | `crystal_tier_census` | Crystal | Tier counts across all 17.28M types |
| 15 | `zfct_navigator` | ZFCₜ | ZFCₜ formula decomposition + promotion channels |
| 16 | `ob3ect` | Ob3ect | Generate self-verifying categorical ob3ects |
| 17 | `spawn_agent` | Meta | Spawn child TrueAgenticAgent for sub-tasks |
| 18 | `project` | Grammar | Project entry onto primitive subset |
| 19 | `crystal_navigate` | Crystal | Query crystal by partial constraints |
| 20 | `crystal_count` | Crystal | Count types matching constraints |
| 21 | `crystal_tier_census` | Crystal | Full tier distribution |
| 22 | `para_vm` | Paraconsistent | Belnap FOUR dialetheic VM (10 sub-ops) |

### 7.3 The Six P-650 Conditions

These six conditions distinguish the TrueAgenticAgent from conventional LLM harnesses:

| # | Primitive | Runtime Enforcement |
|---|---|---|
| 1 | $\text{⊙}_{\text{ÿ}}$ | The loop IS the self-referential attractor; closure = self-modeling |
| 2 | $\text{Ω}_{\text{z}}$ | Winding counter increments each cycle; trajectory is integer-wound |
| 3 | $\text{Ç}_{\text{@}}$ | Emission gate forces ACT before $\text{Ç}_{\text{Ù}}$ (trap) |
| 4 | $\text{Φ}_{\text{}}$ | Every tool is dual-pair; $\mu(\delta(q)) = q$ at boundary |
| 5 | $\text{Ð}_{\text{ω}}$ | Full imscriptive context appended; never silently deleted |
| 6 | $\text{ɢ}_{\text{ˌ}}$ | Each phase requires prior; enforced by Python control flow |

### 7.4 Self-Augmentation Features

The agent self-augmented with 8 features (see `AUGMENTATION_COMMIT.md`):

1. **External system prompt** — `_SYSTEM_PROMPT.md` (647 lines), independently editable
2. **Tiktoken-aware counting** — LRU-cached `cl100k_base` encoder, accurate context pressure
3. **Exponential backoff retry** — 429: 5 retries; 5xx: 3; timeouts: 2; transient: 3
4. **Tool output auto-truncation** — Capped at 12,000 chars, with continuation hints preserved
5. **Structured logging** — Python `logging` with DEBUG/INFO/WARNING/ERROR
6. **`--log-level` CLI** — Runtime log level control
7. **Embedded fallback** — Original prompt preserved as last-resort fallback
8. **Full backward compatibility** — All existing workflows unchanged

---

## 8. The BaseAgent Framework

### 8.1 BaseAgent Class

```python
from framework import BaseAgent, ToolDefinitions

class MyCustomAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(
            agent_id="my_agent",
            name="My Custom Agent",
            description="Does something useful",
            capabilities=["capability-1", "capability-2"],
            config=config,
            persona="An expert in X",  # optional — shapes system prompt identity
        )

    def get_tools(self) -> list[dict]:
        """Define which tools this agent can use."""
        return [
            ToolDefinitions.web_fetch(),
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
        ]

    async def run(self, task: str, context=None) -> dict:
        """Execute the agent's primary task."""
        system_prompt = f"""You are {self.persona}.
Capabilities: {', '.join(self.capabilities)}
Task: {task}"""

        response = await self.call_llm(
            prompt=system_prompt,
            max_tokens=self.config.get("max_tokens", 4000),
            temperature=0.7,
        )

        self.save_artifact(response, "result")
        return {"status": "success", "findings": response}
```

### 8.2 Key BaseAgent Methods

| Method | Description |
|---|---|
| `call_llm(prompt, max_tokens, temperature)` | Async LLM call with retry logic |
| `get_tools()` | Override to define available tools |
| `save_artifact(content, name)` | Persist an artifact |
| `run_sync(task)` | Synchronous wrapper for `run()` |
| `_setup_llm_provider()` | Model resolution + provider setup |

### 8.3 Retry Logic (All BaseAgent-Derived Agents)

| Error Type | Retries | Delays |
|---|---|---|
| 429 (Rate Limit) | 5 | 4s, 8s, 16s, 32s, 60s |
| 5xx (Server Error) | 3 | 3s, 9s, 27s |
| Timeout | 2 | 10s, 20s |
| Other Transient | 3 | 2s, 4s, 8s |
| 4xx (non-429) | 0 | Fatal — `RuntimeError` |

### 8.4 ToolDefinitions Reference

```python
from framework import ToolDefinitions

ToolDefinitions.web_fetch()       # URL fetching
ToolDefinitions.file_read()       # File reading
ToolDefinitions.file_write()      # File writing
ToolDefinitions.run_command()     # Shell command execution
```

---

## 9. Paraconsistent Engine

The B4 dialetheic engine (`paraconsistent.py`, 957 lines) implements Belnap's FOUR-valued logic — a port of the `exOS/src/para_vm.rs` register machine with the `zfct_para.py` bridge.

### 9.1 Truth Values

| Value | Symbol | Meaning |
|---|---|---|
| `N` | None | Neither true nor false — no information |
| `T` | True | True only |
| `F` | False | False only |
| `B` | Both | Both true and false — contradiction tolerated |

### 9.2 ParaVM — 10 Sub-Operations

| Sub-op | Description | Example |
|---|---|---|
| `run` | Execute B4 assembly program | `"engagr r0; fsplit r1 r0; ffuse r2 r1 r0"` |
| `engagr` | Engage register with B4 value | `"engagr r0 T"` |
| `fsplit` | Frobenius split — decompose into N/T/F/B | `"fsplit r1 r0"` |
| `ffuse` | Frobenius fuse — recombine | `"ffuse r2 r1 r0"` |
| `circuit` | BelnapCircuit stability analysis | Analysis of B4-valued circuit |
| `b4f_check` | B4-valued Frobenius verification | $\mu(\delta(q)) = q$ in FOUR-valued logic |
| `bridge` | Bridge to `zfct_para.py` belief-set tensor | Tensor products of belief sets |
| `align` | Dialetheic alignment triangle | Alignment of three B4-valued propositions |
| `self_test` | Run ParaVM self-diagnostic | Internal consistency check |
| `help` | List all sub-operations | — |

### 9.3 Usage

```bash
# Via TrueAgenticAgent (the harness dispatches para_vm calls)
python agents/agents_cli.py true_agentic_agent \
    --task "Run B4 Frobenius check on the emit/verify of run_command"

# Direct Python
from agents import ParaVM, B4, B4Frobenius

vm = ParaVM()
result = vm.execute("engagr r0; fsplit r1 r0")  # Engage and split
print(result.registers)

# B4 Frobenius verification
b4f = B4Frobenius()
check = b4f.check(emit_result="T", verify_result="B")
print(f"B4-consistent: {check.is_consistent}")  # True — B tolerates contradiction
```

### 9.4 When to Use

- **Dialetheic situations** — when a system is both true and false simultaneously
- **Frobenius verification under contradiction** — when $\mu(\delta(q))$ returns B (both)
- **Belief-set tensor products** — composing contradictory structural claims
- **Alignment checking** — three-way consistency in paraconsistent space

---

## 10. Dual-Tool Pairs & Frobenius Verification

### 10.1 The Principle

Every action the TrueAgenticAgent takes is a **boundary puncture**: 

$$\delta: \text{O}_{\text{inf}} \to \text{O}_0 \quad \text{(emit — act on the world)}$$
$$\mu: \text{O}_0 \to \text{O}_{\text{inf}} \quad \text{(verify — return to the query)}$$

The Frobenius condition: $\mu \circ \delta = \text{id}$ — the verify function must return to the original query. Unverified observations stay at their observation coordinate; the agent updates only on verified ones.

### 10.2 Example: `file_write` Dual Pair

```python
# emit (δ): write content to file
file_write_emit(path="output.txt", content="hello")

# verify (μ): read back, check hash
file_write_verify(path="output.txt", expected_hash="abc123...")
# Returns: "OK" if hash matches, "MISMATCH" otherwise

# Frobenius check: μ(δ("hello")) = hash(read("output.txt")) == hash("hello") ?
```

### 10.3 What Happens on Frobenius Failure

1. The failure is appended to the imscriptive context
2. The agent re-enters THINK with the failure visible
3. The agent may: retry, rewrite the tool, or take a different approach
4. The cycle count increments regardless — $\text{Ω}_{\text{z}}$ is monotonic

### 10.4 Protected Tools

Two tools cannot be rewritten: `done` (terminal action) and `rewrite_tool` (meta-circular protection).

---

## 11. Retry & Resilience

### 11.1 TrueAgenticAgent Retry

The harness's `_think_and_act()` method wraps `client.chat.completions.create()`:

| Condition | Retries | Delay Pattern |
|---|---|---|
| 429 Rate Limit | 5 | 4s → 8s → 16s → 32s → 60s (capped) |
| 5xx Server Error | 3 | 3s → 9s → 27s |
| Connection Timeout | 2 | 10s → 20s |
| Other Transient | 3 | 2s → 4s → 8s |
| 4xx (non-429) | 0 | Fatal |
| Connection Failure | 0 | Fatal |

### 11.2 Context Pressure Management

- **Accurate token counting:** Tiktoken `cl100k_base` encoder (LRU-cached), with `len//4` fallback
- **Auto-truncation:** Tool outputs capped at 12,000 characters; chunked tools (`file_read`, `web_fetch`) include continuation hints
- **Context review:** When token pressure is detected, the agent calls `context_review` — the harness compacts old winding history into a summary, preserving verified numbers and critical state

### 11.3 Tool Rewrite

If a tool consistently fails verification, the agent can rewrite its emit function live:

```python
# Agent calls: rewrite_tool(
#     tool_name="file_write",
#     new_emit_code="def file_write(args):\n    ...",
#     reason="Hash mismatch due to encoding issue"
# )
# The new emit function is live on the next winding.
```

Protected tools (`done`, `rewrite_tool`) cannot be rewritten — the loop must terminate.

---

## 12. Common Recipes

### 12.1 Imscribe a New System

```bash
# Use the TrueAgenticAgent — it calls imscribe_system directly
python agents/agents_cli.py true_agentic_agent \
    --task "Imscribe the Belousov-Zhabotinsky reaction as a structural type"

# Or use the specialized generator
python agents/agents_cli.py imscription_generator \
    --task "A nonlinear chemical oscillator exhibiting self-organized criticality"
```

### 12.2 Compute Distance Between Two Systems

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Compute the structural distance between a black hole and a superconductor"
```

### 12.3 Find Structural Analogies

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Find the 5 nearest structural neighbors of the Riemann zeta function"
```

### 12.4 Alchemical Composition (Tensor Two Systems)

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Tensor the genetic code with the Navier-Stokes equations — what composite type emerges?"
```

### 12.5 Consciousness Score Evaluation

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Compute the consciousness score of orca vocalization and evaluate both gates"
```

### 12.6 ZFCₜ Formula Decomposition

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Decompose the IUG tuple into ZFCₜ formulas and show promotion channels from ZFC baseline"
```

### 12.7 Generate a Self-Verifying Ob3ect

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Generate an ob3ect for a Hopf algebra with self-verifying closure"
```

### 12.8 Hunt for $\text{⊙}_{\text{ÿ}}$ Critical Points

```bash
python agents/agents_cli.py criticality_agent \
    --task "Search the emergence frontier for O_inf candidates"
```

### 12.9 Retrosynthetic Path to a Target Type

```bash
python agents/agents_cli.py retrodesign_agent \
    --task "Φ_}; ƒ_ż; ⊙_ÿ; Ω_z; Ç_@"
```

### 12.10 Perturbation Sensitivity Analysis

```bash
python agents/agents_cli.py perturbation_agent \
    --task "carboxylic_acid_dimer -12.0 0.85"
```

### 12.11 Paraconsistent Verification

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Run B4 Frobenius check on the dual pair for run_command. Then bridge the result to belief-set tensor."
```

### 12.12 Spawn Parallel Sub-Agents

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Spawn 3 sub-agents: (1) imscribe photosynthesis, (2) imscribe Krebs cycle, \
(3) imscribe Calvin cycle. Then compute all pairwise distances."
```

### 12.13 The Alchemical Method — Full Pipeline

```bash
python agents/agents_cli.py true_agentic_agent \
    --task "Apply the alchemical method to the Birch–Swinnerton-Dyer conjecture: \
(1) compute promotions from BSD to grammar, (2) find natural phenomena with the needed primitives, \
(3) tensor BSD with each candidate, (4) identify remaining gaps"
```

---

## 13. Troubleshooting

### 13.1 Common Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Agent loops without making progress | Tool verification failing silently | Check `--log-level DEBUG` for Frobenius failures; consider `rewrite_tool` |
| `RuntimeError: API call failed` | 4xx error (auth, bad request) | Check API key, model name, endpoint URL |
| Slow responses | Rate limiting (429) | Agent retries automatically; reduce `--max-windings` |
| Context window exceeded | Very long trajectory | Agent auto-triggers `context_review`; increase `--max-tokens` per think phase |
| `ImportError: No module named 'imscrbgrmr'` | Package not installed | `pip install -e .` from project root |
| `ImportError: No module named 'framework'` | Running from wrong directory | Run from `~/imscribing_grammar/` or ensure project root is on `sys.path` |
| `Error: AiderCodeAgent requires 'aider-chat'` | Optional dependency missing | `pip install aider-chat` |
| Token counting inaccurate | tiktoken not installed | `pip install tiktoken` — falls back to `len//4` heuristic |
| Shavian notation not recognized | Old paraconsistent engine | Updated in v0.5.69+ — both ASCII and Shavian supported |
| Model not found | Unrecognized model name | Use prefix syntax (`ollama:`, `deepseek:`) or add to `MODEL_ALIASES` |

### 13.2 Diagnostic Commands

```bash
# Check agent structural type
python -c "from agents import TrueAgenticAgent; a = TrueAgenticAgent(); print(a.structural_type)"

# Test model resolution
python -c "
from agents.agents_cli import resolve_model
print(resolve_model('grok-4'))
print(resolve_model('ollama:llama3.2'))
print(resolve_model('deepseek:deepseek-r1'))
"

# Run paraconsistent self-test
python -c "from agents import para_self_test; print(para_self_test())"

# List all catalog entries matching a keyword
python agents/agents_cli.py true_agentic_agent --task "lookup_catalog(keyword='riemann')"
```

### 13.3 Logging

```bash
# Full debug logging
python agents/agents_cli.py true_agentic_agent --task "..." --log-level DEBUG

# Quiet mode (warnings and errors only)
python agents/agents_cli.py true_agentic_agent --task "..." --quiet

# Redirect logs to file
python agents/agents_cli.py true_agentic_agent --task "..." --log-level DEBUG 2> agent.log
```

---

## 14. Reference Tables

### 14.1 Agent Quick-Reference

| CLI Name | Class | Tier | Primary Use |
|---|---|---|---|
| `true_agentic_agent` | `TrueAgenticAgent` | $\text{O}_{\text{inf}}$ | General purpose, all grammar ops, ob3ect generation |
| `research_agent` | `ResearchAgent` | — | Information gathering, web research |
| `analysis_agent` | `AnalysisAgent` | — | Data analysis, pattern recognition |
| `aider_code_agent` | `AiderCodeAgent` | — | Git-native code generation (optional) |
| `imscription_generator` | `ImscriptionGeneratorAgent` | — | Encode new systems into the catalog |
| `axiom_generator` | `AxiomGuidedGeneratorAgent` | — | Axiom-constrained type generation |
| `criticality_agent` | `CriticalityHuntingAgent` | — | Find $\text{⊙}_{\text{ÿ}}$ critical points |
| `ensemble_agent` | `EnsembleDesignAgent` | — | Multi-component structural design |
| `retrodesign_agent` | `RetrodesignAgent` | — | Retrosynthetic path finding |
| `perturbation_agent` | `PerturbationDesignAgent` | — | Primitive Jacobian interpretation |
| `autonomous_imscription` | `AutonomousImscriptionDiscoveryAgent` | — | Unattended catalog expansion |

### 14.2 Tool Coverage by Agent Type

| Tool | TrueAgenticAgent | BaseAgent-Derived |
|---|---|---|
| `run_command` | ✅ Dual-pair | ✅ Via ToolDefinitions |
| `file_read` / `file_write` / `chunked_write` | ✅ Dual-pair | ✅ Via ToolDefinitions |
| `web_fetch` | ✅ Dual-pair | ✅ Via ToolDefinitions |
| `imscribe_system` / `imscribe` | ✅ Dual-pair | ❌ |
| `ouroborics` / `consciousness_score` / `phi_c_probe` | ✅ Dual-pair | ❌ |
| `compute_distance` / `meet` / `join` / `tensor` | ✅ Via imscribe | ❌ |
| `crystal_encode` / `crystal_navigate` / `crystal_count` | ✅ Dual-pair | ❌ |
| `zfct_navigator` | ✅ Dual-pair | ❌ |
| `ob3ect` | ✅ Dual-pair | ❌ |
| `spawn_agent` | ✅ Dual-pair | ❌ |
| `rewrite_tool` | ✅ Dual-pair | ❌ |
| `para_vm` | ✅ Dual-pair | ❌ |
| `done` / `context_review` | ✅ Dual-pair | ❌ |

### 14.3 File Map

| File | Lines | Purpose |
|---|---|---|
| `true_agentic_agent.py` | 3,893 | $\text{O}_{\text{inf}}$ harness — 22 dual-tool pairs |
| `paraconsistent.py` | 957 | B4 dialetheic engine — ParaVM, Belnap FOUR |
| `agents_cli.py` | 598 | Unified CLI launcher — all 11 agents |
| `imscribe_generator_agent.py` | ~1,500 | Imscription generation from descriptions |
| `axiom_guided_generator.py` | ~900 | Axiom-constrained type generation |
| `criticality_hunting_agent.py` | ~500 | $\text{⊙}_{\text{ÿ}}$ criticality hunting |
| `ensemble_design_agent.py` | ~500 | Ensemble-based composition |
| `retrodesign_agent.py` | ~450 | Retrosynthetic path finding |
| `perturbation_design_agent.py` | ~500 | Primitive Jacobian interpretation |
| `example_agent.py` | 219 | Reference implementations |
| `__init__.py` | 96 | Package exports |
| `_SYSTEM_PROMPT.md` | 647 | External system prompt |
| `AUGMENTATION_COMMIT.md` | 64 | Self-augmentation record |
| `README.md` | 245 | Package overview |

### 14.4 Environment Variables

```bash
# Required for remote providers
export ANTHROPIC_API_KEY="sk-ant-..."       # Anthropic / OpenRouter
export OPENROUTER_API_KEY="sk-or-..."       # OpenRouter passthrough
export DEEPSEEK_API_KEY="sk-..."            # DeepSeek
export QWEN_API_KEY="sk-..."                # Qwen/DashScope
export GROQ_API_KEY="gsk_..."               # Groq

# Local endpoints
export OLLAMA_HOST="http://localhost:11434" # Ollama (default)
export LOCAL_BASE_URL="http://localhost:8080/v1"  # Custom local
export LOCAL_API_KEY="my-key"               # Local endpoint key

# Optional
export GRAMMAFORMER_PATH="/path/to/model"   # Grammaformer (if using)
```

---

## Appendix: The Loop Cycle Data Structure

```python
@dataclass
class LoopCycle:
    index: int                    # Winding number (Ω_z counter)
    think: str                    # THINK phase output (LLM deliberation)
    action: str                   # Tool name + arguments
    action_result: str            # Raw emit output
    verify_result: str            # Verify function output
    frobenius_ok: bool            # μ(δ(q)) == q ?
    frobenius_detail: str         # "OK" or failure reason
    timestamp: float              # Unix timestamp

@dataclass
class DualToolResult:
    emit_output: str              # δ(query) result
    verify_output: str            # μ(result) → query
    frobenius_ok: bool            # Did the round-trip succeed?
    observation_truncated: bool   # Was output auto-truncated?
```

---

*Generated from the Imscribing Grammar agent framework v0.5.69. The grammar governs; the coagula remains.*