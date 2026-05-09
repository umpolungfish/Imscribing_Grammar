---
header-includes:
  - |
    \usepackage{fontspec}
    \newfontfamily\hebrewfont[Script=Hebrew]{Noto Serif Hebrew}
    \newcommand{\heb}[1]{{\hebrewfont #1}}
    \newfontfamily\igfont[Ligatures=TeX]{Noto Serif}
    \newcommand{\igtext}[1]{{\igfont #1}}
---
# Agent Development Guide

This document covers conventions, patterns, and best practices for building agents with the AjintK framework (v2.1.0).

---

## Agent Anatomy

Every agent inherits from `BaseAgent` and must implement `run()`. All other methods are optional overrides.

```python
from framework import BaseAgent, ToolDefinitions
from typing import Dict, List, Any, Optional

class MyAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="my_agent",          # Unique identifier
            name="My Agent",              # Human-readable name
            description="Does X and Y",  # Shown in system prompts
            capabilities=["X", "Y"],      # List of capability strings
            config=config,
            persona="Senior X Specialist" # Optional: distinct role identity
        )

    def get_tools(self) -> List[Dict[str, Any]]:
        """Declare tools this agent may use (optional)."""
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.web_fetch(),
        ]

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent's task. Must return a status dict."""
        prompt = f"You are {self.persona}. Task: {task}"

        # Incorporate outputs from prior pipeline stages if available
        if context and context.get("previous_stage"):
            prior = context["previous_stage"].get("findings", "")
            prompt += f"\n\nPrior findings:\n{prior}"

        try:
            raw = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.7
            )
            response_text = self.clean_response(raw)
            self.save_artifact(response_text, "output")

            return {
                "status": "success",
                "findings": response_text,
                "artifacts": self.artifacts,
                "metadata": {
                    "task": task,
                    "model": self.config.get("model"),
                    "provider": self.config.get("provider", "anthropic")
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "findings": None,
                "artifacts": []
            }
```

---

## Return Value Contract

Every `run()` must return a dict with at minimum a `"status"` key:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `status` | `"success"` \| `"error"` | Yes | Pipeline uses this to detect failures |
| `findings` | `str` \| `None` | Recommended | Primary textual output |
| `artifacts` | `list` | Recommended | Use `self.artifacts` after `save_artifact()` calls |
| `metadata` | `dict` | Optional | Task, model, provider, any extra info |
| `error` | `str` | On error | Human-readable error description |

---

## Accessing Pipeline Context

When an agent runs inside a pipeline, `context` contains the full history of prior stages via `PipelineContext`:

```python
async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # Access only the immediately prior stage
    previous = (context or {}).get("previous_stage", {})
    prior_findings = previous.get("findings", "")

    # Access ALL prior stages (full pipeline history)
    all_stages = (context or {}).get("pipeline_stages", [])
    for stage in all_stages:
        stage_num   = stage["stage"]
        agent_id    = stage["agent_id"]
        result      = stage["result"]
        findings    = result.get("findings", "")
        print(f"Stage {stage_num} ({agent_id}): {findings[:100]}")

    # Access all accumulated artifacts
    all_artifacts = (context or {}).get("all_artifacts", [])
```

---

## Tool Use

### Declaring Tools

Override `get_tools()` to declare tools available in the autonomous loop:

```python
def get_tools(self) -> List[Dict[str, Any]]:
    return [
        ToolDefinitions.file_read(),
        ToolDefinitions.file_write(),
        ToolDefinitions.json_load(),
        ToolDefinitions.json_save(),
        ToolDefinitions.list_directory(),
        ToolDefinitions.run_command(),
        ToolDefinitions.web_fetch(),
    ]
```

### Autonomous Tool Loop

`execute_with_tools` runs the think/act cycle automatically:

```python
async def run(self, task: str, context=None) -> Dict[str, Any]:
    findings = await self.execute_with_tools(task, max_iterations=8)
    return {"status": "success", "findings": findings}
```

The loop:
1. Prompts the LLM with the task and available tools
2. Extracts JSON tool calls from the response
3. Executes each tool via `ToolExecutor`
4. Feeds the result back and repeats
5. Returns on `FINAL ANSWER:` or when `max_iterations` is reached

### Registering Custom Tools

Domain-specific tools can be registered globally once on import:

```python
from framework import global_registry

async def handle_entropy(tool_input):
    import math, collections
    data = tool_input["data"].encode()
    freq = collections.Counter(data)
    total = len(data)
    entropy = -sum((c/total) * math.log2(c/total) for c in freq.values())
    return f"Shannon entropy: {entropy:.4f} bits/byte"

global_registry.register(
    name="calc_entropy",
    handler=handle_entropy,
    description="Calculate Shannon entropy of a data string",
    input_schema={
        "type": "object",
        "properties": {
            "data": {"type": "string", "description": "Data to measure"}
        },
        "required": ["data"]
    }
)
```

Any agent's `ToolExecutor` will now resolve `calc_entropy` automatically.

---

## Response Cleaning

Always call `self.clean_response(raw)` on LLM output before using it. This is especially important when using reasoning models (DeepSeek-R1, Qwen-thinking) that emit `<think>` blocks:

```python
raw = await self.call_llm(prompt)
text = self.clean_response(raw)
# Strips: <think>...</think>, ```lang ... ```, FINAL ANSWER: prefix
```

To extract structured JSON from a response:

```python
blocks = self.extract_json_blocks(raw)
if blocks:
    data = blocks[0]  # First valid JSON object found
```

---

## Personas

The `persona` field sets the identity used in system prompts. It defaults to `name` but can be set independently:

```python
super().__init__(
    agent_id="vuln_agent",
    name="Vulnerability Analyst",
    description="...",
    capabilities=[...],
    config=config,
    persona="Senior Security Researcher specializing in memory safety"
)
```

This shapes the `execute_with_tools` system prompt and can be referenced directly in `run()` via `self.persona`.

---

## Orchestration

### Single Agent

```python
result = await orchestrator.run_agent("my_agent", task)
```

### Parallel Swarm

```python
orchestrator.register_agent("a", AgentA(config))
orchestrator.register_agent("b", AgentB(config))
orchestrator.register_agent("c", AgentC(config))

result = await orchestrator.run_swarm(
    task="Analyze target",
    agent_ids=["a", "b", "c"]
)
# result["results"]["a"], result["results"]["b"], etc.
```

### Sequential Pipeline

```python
result = await orchestrator.run_pipeline(
    task="Full audit",
    agent_ids=["hunter", "triage", "reporter"],
    initial_context={"scope": "auth module"}
)
# Every agent sees all prior outputs via PipelineContext
```

### Pipeline Presets

```python
orchestrator.register_preset("full",    ["hunter", "triage", "reporter"])
orchestrator.register_preset("quick",   ["hunter", "reporter"])
orchestrator.register_preset("redteam", ["hunter", "exploit"])

result = await orchestrator.run_preset("full", task)
```

---

## Multi-Provider Configuration

Set the `provider` and `model` keys in the agent config dict. Use `model=None` to use the provider-specific default from config:

```python
from imscrbgrmr.provider_config import build_agent_config

# Anthropic (uses claude-sonnet-4-5-20250929 if model=None)
config = build_agent_config(provider="anthropic", model=None)

# Google Gemini (uses gemini-2.0-flash-exp if model=None)
config = build_agent_config(provider="google", model=None)

# DeepSeek (uses deepseek-chat if model=None)
config = build_agent_config(provider="deepseek", model=None)

# Qwen (uses qwen3-max if model=None)
config = build_agent_config(provider="qwen", model=None)

# Mistral (uses codestral-2508 if model=None)
config = build_agent_config(provider="mistral", model=None)

# Or specify explicit model
config = build_agent_config(provider="anthropic", model="claude-3-opus-20240229")
```

### Adaptive Provider with Fallback

```python
from framework import get_adaptive_provider

# Automatically selects and falls back through the priority chain
provider, name = await get_adaptive_provider(task_type="coding")
response = await provider.query(task)
```

Task type options: `coding`, `reasoning`, `creative`, `analysis`, `general`.

### Cost-Optimized Per-Agent Models

```python
from imscrbgrmr.provider_config import build_agent_config

# Expensive model for complex reasoning
hunter_cfg = build_agent_config(provider="anthropic", model="claude-sonnet-4-5-20250929")

# Cheap model for simple formatting
format_cfg = build_agent_config(provider="anthropic", model="claude-haiku-4-5-20251001")
```

---

## YAML-Driven Agent Setup

`config.yaml`:
```yaml
provider: anthropic
# model: omit to use provider-specific default, or specify explicitly
# model: claude-sonnet-4-5-20250929
max_tokens: 4000
temperature: 0.7
max_concurrent_agents: 5

presets:
  full:  [researcher, analyst, reporter]
  quick: [researcher, reporter]
```

```python
from framework import (
    load_config, agent_config_from, orchestrator_config_from,
    register_presets_from_config, AgentOrchestrator
)

cfg      = load_config("config.yaml")
orch     = AgentOrchestrator(orchestrator_config_from(cfg))
agent_c  = agent_config_from(cfg)

orch.register_agent("researcher", ResearchAgent(agent_c))
orch.register_agent("analyst",    AnalysisAgent(agent_c))
orch.register_agent("reporter",   ReporterAgent(agent_c))
register_presets_from_config(orch, cfg)

result = await orch.run_preset("full", task="Audit authentication module")
```

---

## Communication Between Agents

```python
from framework import AgentCommunication, MessageType

comm = AgentCommunication()

# Agent A requests help from Agent B
await comm.send_collaboration_request(
    from_agent="agent_a",
    to_agent="agent_b",
    task="Triage this finding",
    context={"finding": data}
)

# Agent B reads and responds
messages = await comm.receive_messages("agent_b")
for msg in messages:
    if msg["message_type"] == MessageType.COLLABORATION.value:
        result = await do_triage(msg["metadata"]["task"])
        await comm.send_response(
            from_agent="agent_b",
            to_agent="agent_a",
            original_message_id=msg["message_id"],
            response_content="Triage complete",
            response_data={"result": result}
        )
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Class names | PascalCase | `ResearchAgent`, `TriageAgent` |
| Methods/functions | snake_case | `run_agent`, `get_tools` |
| Constants | UPPEŘ_SNAKE_CASE | `MAX_RETRIES`, `DEFAULÞ_TIMEOUT` |
| Private methods | `_` prefix | `_setup_llm_provider` |
| Instance variables | snake_case | `agent_id`, `max_concurrent` |

## Type Hints

```python
from typing import Dict, List, Optional, Any

async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ...
```

- Use `Optional[T]` for parameters that can be `None`
- Use `Union[T1, T2]` for multiple possible types
- Import from `typing` at the top of every file

---

## Framework Architecture Reference

| Module | Class | Purpose |
|--------|-------|---------|
| `base_agent.py` | `BaseAgent` | Abstract base with LLM calls, tool loop, response cleaning |
| `orchestrator.py` | `AgentOrchestrator` | Swarm, pipeline, preset coordination |
| `orchestrator.py` | `PipelineContext` | Full accumulated pipeline state |
| `tools.py` | `ToolDefinitions` | Catalogue of standard tool schemas |
| `tools.py` | `ToolExecutor` | Async tool dispatch |
| `tools.py` | `ToolRegistry` / `global_registry` | Runtime tool registration |
| `enhanced_llm_provider.py` | `ModelRouter` | Provider priority chains + fallback |
| `enhanced_llm_provider.py` | `get_adaptive_provider` | Auto-selects best available provider |
| `config_loader.py` | — | `load_config`, `agent_config_from`, `register_presets_from_config` |
| `memory.py` | `AgentMemory` | Async JSON-backed persistent state |
| `communication.py` | `AgentCommunication` | File-backed inter-agent messaging |
