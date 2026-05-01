# Framework Methodology & Design Philosophy

This document explains the core methodology and design decisions behind the AjintK framework (v2.1.0) — a multi-provider AI agent framework.

## Core Design Principles

### 1. Separation of Concerns

The framework separates distinct responsibilities into isolated modules:

- **BaseAgent**: Agent logic and multi-LLM provider interaction
- **Orchestrator**: Multi-agent coordination and pipeline state
- **Enhanced LLM Provider System**: Multi-provider LLM integration with fallback routing
- **Tools**: External capabilities with a dynamic registry
- **Memory**: State persistence
- **Communication**: Inter-agent messaging
- **Config Loader**: YAML-based orchestration configuration

**Why**: This modularity enables agents to be developed independently while maintaining consistent interfaces for integration.

### 2. Inheritance-Based Extensibility

All agents inherit from `BaseAgent`, which provides:
- Multi-LLM provider client setup
- Lifecycle management (start → run → complete/fail)
- State tracking and artifact storage
- Response cleaning and JSON extraction
- Intelligent provider selection and routing

**Pattern**:
```python
class CustomAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(agent_id, name, description, capabilities, config)

    async def run(self, task, context):
        response = await self.call_llm(prompt=task)
        return {"status": "success", "findings": self.clean_response(response)}
```

**Why**: New agents get all base functionality for free. Developers only implement the unique `run()` logic.

### 3. Multi-Provider Architecture with Fallback Chain

Agents can utilize multiple LLM providers:
- Provider selection via configuration
- Intelligent routing based on task type, with a full ordered priority chain
- Automatic fallback: if the preferred provider is unavailable, the next in chain is tried
- Response caching for efficiency

**Pattern**:
```python
# Adaptive provider with real fallback — not just a static selection
provider, provider_name = await get_adaptive_provider(task_type="coding")
response = await provider.query(task)
```

**Why**: Flexibility to match provider capabilities to task requirements, optimize costs, and provide redundancy when a provider API is down or misconfigured.

### 4. Dynamic Tool Registry

Tools are no longer only defined statically on agent classes. A `ToolRegistry` allows runtime registration:

- `ToolDefinitions` provides a catalogue of standard schemas
- `ToolRegistry` / `global_registry` allow domain-specific tools to be registered once and used everywhere
- `ToolExecutor` checks the registry before falling back to its built-in handlers

**Pattern**:
```python
# Register once, globally
global_registry.register("parse_csv", handle_parse_csv, description, schema)

# Every ToolExecutor instance picks it up automatically
agent = MyAgent(...)  # agent.tool_executor already has parse_csv
```

**Why**: Eliminates the need to subclass `ToolExecutor` or repeat tool registration in every agent class. Downstream project teams can publish their tools to the global registry on import.

### 5. Full Context Accumulation in Pipelines (PipelineContext)

The original pipeline passed only `previous_stage` to the next agent, meaning a stage three agent could not see what stage one produced. `PipelineContext` fixes this:

- Every completed stage result is appended to `stage_results`
- Every artifact is collected into `artifacts`
- `to_context_dict()` exposes the full history at each step

**Pattern**:
```python
result = await orchestrator.run_pipeline(task, ["stage1", "stage2", "stage3"])

ctx = result["pipeline_context"]
# Stage 3 agent could access stage 1 output via ctx.stage_results[0]
```

**Why**: Multi-stage analysis workflows (research → triage → report) compound value only when later stages can see the full accumulated output, not just the immediately preceding one.

### 6. Pipeline Presets

Named sequences of agents can be registered once and invoked by name, following the preset pattern from specialized downstream tools:

**Pattern**:
```python
orchestrator.register_preset("full",    ["hunter", "triage", "reporter"])
orchestrator.register_preset("quick",   ["hunter", "reporter"])

# Later, invoke by name
result = await orchestrator.run_preset("full", task)
```

**Why**: Encourages reusable, named workflow definitions. Config-driven systems can specify a preset name rather than a list of agent IDs, making the orchestration intent explicit.

### 7. Response Post-Processing

LLM outputs frequently contain formatting noise — fenced code blocks, XML reasoning tags from chain-of-thought models, or `FINAL ANSWER:` prefixes. `BaseAgent` provides static utilities:

- **`clean_response(text)`**: Strips fenced code blocks, `<think>`/`<reasoning>` tags, `FINAL ANSWER:` prefix.
- **`extract_json_blocks(text)`**: Finds all JSON objects in a response using regex, not a fragile single-split.

**Why**: As reasoning models (DeepSeek-R1, Qwen-thinking) become common, their XML-tagged internal monologue must be stripped before the output is used. A centralized cleaner prevents every agent from implementing its own ad-hoc stripping logic.

### 8. YAML-Driven Configuration

Orchestration topology — providers, models, agent options, pipeline presets — can be declared in a single YAML file:

```yaml
provider: anthropic
# model: omit to use provider-specific default, or specify explicitly
# model: claude-sonnet-4-5-20250929
max_tokens: 4000

presets:
  full:  [hunter, triage, reporter]
  quick: [hunter, reporter]
```

```python
cfg = load_config("config.yaml")
orchestrator = AgentOrchestrator(orchestrator_config_from(cfg))
register_presets_from_config(orchestrator, cfg)
```

**Why**: Separates "what the system does" (agent code) from "how it's configured" (YAML). Teams can ship different configs for different use-case profiles without touching Python.

### 9. Three Coordination Patterns

#### Pattern A: Single Agent
```python
result = await orchestrator.run_agent("researcher", task)
```
**Use**: Simple, focused tasks requiring single capability.

#### Pattern B: Parallel Swarm
```python
result = await orchestrator.run_swarm(task, ["agent1", "agent2", "agent3"])
```
**Use**: Multiple perspectives on the same problem, executed concurrently.

#### Pattern C: Sequential Pipeline
```python
result = await orchestrator.run_pipeline(task, ["research", "analyze", "synthesize"])
# Or by preset name:
result = await orchestrator.run_preset("full", task)
```
**Use**: Multi-stage workflows where later stages depend on (and can see) all earlier outputs.

### 10. State Machine Lifecycle

Every agent follows this lifecycle:

```
IDLE → start() → RUNNING → run() → complete()/fail() → COMPLETED/FAILED
```

**Why**: Consistent state management enables monitoring, debugging, and recovery.

---

## Key Architectural Decisions

### Decision 1: ToolRegistry Over Static Definitions Only

**Choice**: Add a dynamic `ToolRegistry` alongside the static `ToolDefinitions` catalogue.
**Alternative**: Keep all tools as static class methods on `ToolDefinitions`.
**Rationale**: Downstream projects must register domain-specific tools without forking the core. A shared `global_registry` lets teams publish tools on import, with zero changes to `BaseAgent`.

### Decision 2: PipelineContext Over Dict Mutation

**Choice**: Introduce `PipelineContext` dataclass to accumulate pipeline state.
**Alternative**: Continue mutating a plain dict with `context.update({"previous_stage": result})`.
**Rationale**: The mutation approach loses all but the last stage's output. `PipelineContext` preserves the full history structurally, exposes it cleanly, and is type-safe.

### Decision 3: Actual Fallback Chain in `get_adaptive_provider`

**Choice**: `get_adaptive_provider` iterates the full provider priority chain on failure.
**Alternative**: Select the first provider and raise immediately on misconfiguration.
**Rationale**: Real workloads run across multiple API keys/environments. Silently falling back to the next available provider is more robust than crashing on a missing env var.

### Decision 4: Static `clean_response` on BaseAgent

**Choice**: Put `clean_response` and `extract_json_blocks` as static methods on `BaseAgent`.
**Alternative**: Standalone functions in a `utils.py` module.
**Rationale**: Agents are the natural consumers of these utilities. Placing them on `BaseAgent` means every subclass inherits them without an import. They remain callable as statics (`BaseAgent.clean_response(text)`) for out-of-agent use.

### Decision 5: Named Personas

**Choice**: Optional `persona` field on `BaseAgent` (defaults to `name`).
**Alternative**: Always use agent `name` in system prompts.
**Rationale**: Some agent roles benefit from a distinct persona that differs from their technical name. Separating identity from identifier lets the same agent class play different roles in different pipeline configurations.

### Decision 6: JSON-Based Persistence

**Choice**: Store memory and messages as JSON files.
**Alternative**: Database (PostgreSQL, MongoDB).
**Rationale**: Zero external dependencies, human-readable for debugging, easy to version control. Sufficient for most use cases; can upgrade to DB later without changing agent interfaces.

### Decision 7: Result Dictionary Pattern

**Choice**: Agents return structured dicts:
```python
{
    "status": "success|error",
    "findings": "...",
    "artifacts": [...],
    "metadata": {"task": "...", "model": "...", "provider": "..."}
}
```
**Alternative**: Custom result classes.
**Rationale**: Simple, flexible, serializable, and extensible via metadata.

---

## Implementation Patterns

### Pattern: Standard Agent Run

```python
async def run(self, task: str, context=None) -> Dict[str, Any]:
    prompt = f"You are {self.persona}. Task: {task}"
    if context and context.get("previous_stage"):
        prompt += f"\n\nPrior findings:\n{context['previous_stage'].get('findings', '')}"

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
        "metadata": {"task": task, "provider": self.config.get("provider")}
    }
```

### Pattern: Accessing Full Pipeline History

```python
async def run(self, task: str, context=None) -> Dict[str, Any]:
    all_prior = ""
    for stage in (context or {}).get("pipeline_stages", []):
        agent_id = stage["agent_id"]
        findings = stage["result"].get("findings", "")
        all_prior += f"\n\n--- {agent_id} ---\n{findings}"

    prompt = f"Synthesize the following prior work:\n{all_prior}\n\nTask: {task}"
    response = self.clean_response(await self.call_llm(prompt))
    ...
```

### Pattern: Runtime Tool Registration

```python
from framework import global_registry

async def handle_my_tool(tool_input):
    return f"processed: {tool_input['value']}"

global_registry.register(
    name="my_tool",
    handler=handle_my_tool,
    description="Does something domain-specific",
    input_schema={
        "type": "object",
        "properties": {"value": {"type": "string"}},
        "required": ["value"]
    }
)
```

### Pattern: Preset-Driven Pipeline

```python
cfg = load_config("config.yaml")
orchestrator = AgentOrchestrator(orchestrator_config_from(cfg))
for agent_id, agent in build_agents(agent_config_from(cfg)).items():
    orchestrator.register_agent(agent_id, agent)
register_presets_from_config(orchestrator, cfg)

result = await orchestrator.run_preset("full", task="Audit authentication module")
```

### Pattern: Collaborative Messaging

```python
await comm.send_collaboration_request(
    from_agent="agent_a", to_agent="agent_b",
    task="Analyze this data", context={"data": results}
)

messages = await comm.receive_messages("agent_b")
for msg in messages:
    if msg["message_type"] == "collaboration_request":
        result = await process(msg["metadata"]["task"])
        await comm.send_response(
            from_agent="agent_b", to_agent="agent_a",
            original_message_id=msg["message_id"],
            response_content="Complete",
            response_data={"result": result}
        )
```

---

## Scalability Considerations

### Horizontal Scaling
- **Current**: `asyncio`-based concurrency on a single machine with semaphore-controlled parallelism.
- **Upgrade Path**: Replace orchestrator with a distributed task queue (Celery, RabbitMQ).
- **Agent Interface**: Unchanged — agents don't know about orchestration internals.

### Storage Scaling
- **Current**: JSON files stored locally.
- **Upgrade Path**: Replace with a database backend in `AgentMemory`.
- **Agent Interface**: Unchanged — agents use the same memory API.

### Provider Scaling
- **Current**: Individual API calls to each provider with caching and fallback.
- **Upgrade Path**: Add rate limiting and load balancing at the provider layer.
- **Agent Interface**: Unchanged.

---

## Performance Optimization

### Caching Strategy
Responses are cached to `.llm_cache.json` using a SHA-256 hash of prompt + model + temperature. Avoids redundant API calls across runs.

### Provider Selection
Use `task_type` in `get_adaptive_provider` to route to the most cost-effective capable provider. The fallback chain means production systems never fail on a single unavailable API key.

### Cost Optimization
```yaml
agents:
  researcher:
    model: "claude-sonnet-4-5-20250929"    # Complex reasoning
  formatter:
    model: "claude-haiku-4-5-20251001"  # Simple formatting
```

---

## Lessons Learned from Downstream Projects

### Lesson 1: Pipelines Need Full History
The original pattern of `context = {"previous_stage": last_result}` meant stage N could not see stage N-2. Every serious multi-step workflow needs all prior outputs. `PipelineContext` solves this structurally.

### Lesson 2: LLM Output Is Noisy
Reasoning models emit `<think>` blocks. Streaming responses include markdown fences. Every agent was writing its own stripping logic. A single `clean_response` utility on `BaseAgent` eliminates the duplication.

### Lesson 3: Tools Must Be Extensible at Runtime
Static `ToolDefinitions` class methods work for simple cases but break down when downstream projects need to publish domain-specific tools. `ToolRegistry` lets them register on import.

### Lesson 4: Named Workflows Lower the Barrier to Entry
Requiring users to know the ordered list of agent IDs for each workflow is friction. Named presets (`"full"`, `"quick"`, `"redteam"`) make the intent self-documenting and config-friendly.

### Lesson 5: Fallback Routing Must Actually Fall Back
A router that always returns index 0 of a priority list is not a router. `get_adaptive_provider` now genuinely iterates the chain, making multi-provider setups resilient to individual API outages.

### Lesson 6: Keep Agents Focused
Swiss-army-knife agents become hard to debug and expensive to run. Many specialized agents in a pipeline outperform one generalist agent given an enormous prompt.

---

## Framework Evolution

This framework evolves along several axes:

1. **Persistence**: JSON → Database
2. **Concurrency**: Single-machine async → Distributed queue
3. **Communication**: File-based inbox → Message broker
4. **Observability**: Logs → Metrics → Distributed tracing
5. **Orchestration**: Static pipelines → Conditional → Dynamic agent graphs

**Key Principle**: Evolution should be incremental and backward-compatible. Agent code remains stable while infrastructure scales.

---

**Remember**: The goal is productive agent development, not perfect abstraction. Use what you need, extend when necessary, keep agents simple.
