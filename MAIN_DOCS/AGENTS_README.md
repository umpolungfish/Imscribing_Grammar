# AjintK: Multi-Provider AI Agent Framework

A high-performance, asynchronous framework for building autonomous multi-agent systems with support for multiple LLM providers.

## Overview

AjintK is a production-ready framework designed for orchestrating autonomous agents. It leverages **Asynchronous I/O** to achieve high concurrency and features a **standardized autonomous tool-use loop**, allowing agents to "think" and "act" iteratively until a task is completed.

### Key Features

- **Asynchronous Architecture**: Built on `asyncio` for maximum performance and non-blocking agent orchestration.
- **Autonomous Tool-Use Loop**: Standardized Thinking/Acting cycle in `BaseAgent` for complex, multi-step tasks.
- **Multi-Provider Support**: Seamlessly switch between Anthropic (Claude), Google (Gemini), DeepSeek, Qwen, and Mistral.
- **Dynamic Tool Registry**: Register custom tools at runtime with a decorator or call — no subclassing required.
- **Optimized Caching**: High-efficiency response caching with model-parameter awareness and atomic disk writes.
- **Modern Dependency Management**: Integrated with `uv` for lightning-fast setup and resolution.
- **Intelligent Routing with Fallback**: Route tasks to the most capable provider; automatically fall back through the priority chain on failure.
- **Pipeline Presets**: Define named multi-stage agent workflows once, invoke them by name.
- **Full Context Accumulation**: Every pipeline stage receives outputs from all prior stages, not just the last one.
- **Response Cleaning**: Strip markdown blocks, XML reasoning tags, and formatting artifacts from LLM output automatically.
- **YAML Configuration**: Declare providers, agents, and pipeline presets in a single config file.
- **Persistent Memory**: Asynchronous, thread-safe JSON memory system for agent state and session history.

## Core Components

### 1. BaseAgent (Async)
The foundation for all agents. It provides:
- **`execute_with_tools`**: An autonomous loop that manages tool identification, execution, and response refinement.
- **`clean_response`**: Static method that strips markdown blocks, XML reasoning tags, and `FINAL ANSWER:` prefixes.
- **`extract_json_blocks`**: Robust multi-block JSON extraction using regex rather than fragile string splits.
- **`persona`**: Optional named role that shapes the system prompt identity.
- **Async LLM Calls**: Unified interface for multi-provider asynchronous queries.

### 2. AgentOrchestrator
Manages concurrent agent execution:
- **Swarm Mode**: Runs multiple agents in parallel using `asyncio.gather`.
- **Pipeline Mode**: Sequential execution where the full `PipelineContext` is passed between stages.
- **Preset Mode**: Run a named sequence of agents with `run_preset("full", task)`.

### 3. PipelineContext
Structured accumulator for multi-stage pipeline state:
- Stores results from every completed stage.
- Collects all artifacts produced by the pipeline.
- Exposes `to_context_dict()` so each agent can access the full execution history.

### 4. Tool System
Pre-built asynchronous tools with a dynamic registry:
- **File Operations**: `file_read`, `file_write`, `json_load`, `json_save`, `list_directory`.
- **System Commands**: `run_command` with timeout and subprocess management.
- **Web Interaction**: `web_fetch` using `httpx`.
- **ToolRegistry**: Register custom tools at runtime with `register()` or the `@tool_handler` decorator.
- **global_registry**: Shared singleton so downstream projects can register tools once.

### 5. Memory System
Asynchronous persistent storage:
- **Atomic Writes**: Prevents data corruption during concurrent operations.
- **Session Tracking**: Organize agent interactions into logical sessions and events.

### 6. Config Loader
YAML-based orchestration configuration:
- `load_config(path)` reads a YAML file into a plain dict.
- `agent_config_from(cfg)` / `orchestrator_config_from(cfg)` extract subsections.
- `register_presets_from_config(orchestrator, cfg)` wires up pipeline presets from YAML.

## Installation

We recommend using `uv` for the best performance.

```bash
# 1. Clone the repository
git clone https://github.com/mrnob0dy666/AjintK
cd AjintK

# 2. Setup environment and dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 3. Set up API keys
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export QWEN_API_KEY="your-key"
export MISTRAL_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"
```

## Quick Start

### Create an Autonomous Agent

```python
import asyncio
from framework import BaseAgent, ToolDefinitions

class DevAgent(BaseAgent):
    def get_tools(self):
        return [ToolDefinitions.run_command(), ToolDefinitions.file_write()]

    async def run(self, task: str, context=None):
        findings = await self.execute_with_tools(task)
        return {"status": "success", "findings": findings}

async def main():
    from imscrbgrmr.provider_config import build_agent_config
    
    # Use config-driven defaults (model=None uses provider default)
    config = build_agent_config(provider="anthropic", model=None)
    agent = DevAgent("dev_agent", "Developer", "Writes and tests code", ["coding"], config)
    result = await agent.run("Create a hello.py and run it to verify it works.")
    print(result["findings"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Dynamic Tool Registration

```python
from framework import global_registry, ToolExecutor

# Register a custom tool at runtime
async def handle_parse_csv(tool_input):
    import csv, io
    data = tool_input["data"]
    reader = csv.DictReader(io.StringIO(data))
    return list(reader)

global_registry.register(
    name="parse_csv",
    handler=handle_parse_csv,
    description="Parse CSV text into a list of row dicts",
    input_schema={
        "type": "object",
        "properties": {"data": {"type": "string", "description": "CSV text to parse"}},
        "required": ["data"]
    }
)
# All ToolExecutor instances now have access to parse_csv automatically
```

### Pipeline Presets

```python
from framework import AgentOrchestrator

orchestrator = AgentOrchestrator()
orchestrator.register_agent("hunter",   HunterAgent(config))
orchestrator.register_agent("triage",   TriageAgent(config))
orchestrator.register_agent("reporter", ReporterAgent(config))

# Register named workflows
orchestrator.register_preset("full",    ["hunter", "triage", "reporter"])
orchestrator.register_preset("quick",   ["hunter", "reporter"])

# Invoke by name
result = await orchestrator.run_preset("full", task="Audit the authentication module")
```

### Full Context Accumulation in Pipelines

```python
# Each stage receives ALL prior stage outputs via PipelineContext
result = await orchestrator.run_pipeline(
    task="Comprehensive analysis",
    agent_ids=["researcher", "analyst", "synthesizer"],
    initial_context={"focus": "security"}
)

# Access the full accumulated pipeline history
ctx = result["pipeline_context"]
for stage in ctx.stage_results:
    print(f"Stage {stage['stage']} ({stage['agent_id']}): {stage['result']['status']}")
```

### YAML-Driven Configuration

`config.yaml`:
```yaml
provider: anthropic
# model: omit to use provider-specific default, or specify explicitly
# model: claude-sonnet-4-5-20250929
max_tokens: 4000
temperature: 0.7
max_concurrent_agents: 5

presets:
  full:    [hunter, triage, reporter]
  quick:   [hunter, reporter]
  redteam: [hunter, exploit]
```

```python
from framework import load_config, agent_config_from, orchestrator_config_from, register_presets_from_config

cfg = load_config("config.yaml")
agent_cfg  = agent_config_from(cfg)
orch_cfg   = orchestrator_config_from(cfg)

orchestrator = AgentOrchestrator(orch_cfg)
# ... register agents ...
register_presets_from_config(orchestrator, cfg)

result = await orchestrator.run_preset("full", task="Scan for vulnerabilities")
```

### Parallel Swarms

```python
orchestrator = AgentOrchestrator({"max_concurrent_agents": 10})
orchestrator.register_agent("researcher", ResearchAgent(config))
orchestrator.register_agent("analyst",    AnalysisAgent(config))

results = await orchestrator.run_swarm(task="Analyze AI frameworks")
```

### Intelligent Routing with Fallback

```python
from framework import get_adaptive_provider

# Walks the provider priority chain; falls back automatically on API errors
provider, name = await get_adaptive_provider(task_type="coding")
code = await provider.query("Optimize this SQL query...")
print(f"Used provider: {name}")
```

### Response Cleaning

```python
from framework import BaseAgent

raw = "<think>internal monologue</think>```python\nprint('hello')\n```"
clean = BaseAgent.clean_response(raw)
# → "print('hello')"
```

## Performance & Reliability

- **Caching**: Responses are cached to `.llm_cache.json` based on a SHA-256 hash of the prompt, model, and temperature.
- **Async Safety**: Every component uses `asyncio.Lock` where necessary to ensure data integrity in high-concurrency scenarios.
- **Provider Fallback**: `get_adaptive_provider` tries each provider in the priority chain on failure rather than raising immediately.
- **Error Handling**: Standardized error reporting across all agent modes.

## Contributing

AjintK is designed to be extensible:
- **New providers**: Inherit from `LLMProvider` in `framework/llm_provider_abc.py` and implement `async query`.
- **New tools**: Use `global_registry.register()` or the `@tool_handler` decorator in `framework/tools.py`.
- **New agents**: Inherit from `BaseAgent`, implement `run()`, and optionally `get_tools()`.

---
**Build powerful, autonomous, and lightning-fast AI systems with AjintK.**
