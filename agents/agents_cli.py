#!/usr/bin/env python3
"""
agents/agents_cli.py — Unified CLI launcher for all agents in this package.

Usage:
    python agents/agents_cli.py <agent_name> --task <task>
    
Agents:
    true_agentic_agent    - Grammar-optimal ⊙-critical agent (O_∞)
    research_agent        - Information gathering and synthesis
    analysis_agent        - Data analysis and pattern recognition
    aider_code_agent      - Git-native code operations (requires aider)
    perturbation_agent    - Primitive Jacobian interpretation
    ensemble_agent        - Goal-directed multi-imscription composition
    retrodesign_agent     - Retrosynthetic analysis
    criticality_agent     - ⊙ criticality hunting
    imscription_generator     - Imscription structure generation
    axiom_generator       - Axiom-guided generation
    autonomous_imscription    - Autonomous imscription discovery

Prefix syntax for --model (inherited from true_agentic_agent harness):
    ollama:llama3.2        → Ollama at localhost
    lm-studio:phi-4        → LM Studio at localhost:1234/v1
    vllm:mistral           → vLLM at localhost:8000/v1
    local:my-model         → LOCAL_BASE_URL env var
    deepseek:model-id      → DeepSeek API (DEEPSEEK_API_KEY)
    qwen:model-id          → Qwen/DashScope API (QWEN_API_KEY)
    groq:model-id          → Groq API (GROQ_API_KEY)

Example:
    python agents/agents_cli.py true_agentic_agent --task "Analyze Riemann zeta"
    python agents/agents_cli.py research_agent --file task.txt --model ollama:llama3.2
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ═══════════════════════════════════════════════════════════════════════════════
# Model resolution — imported from true_agentic_agent harness
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_ALIASES: Dict[str, str] = {
    "claude-opus-4":    "anthropic/claude-opus-4",
    "claude-sonnet-4":  "anthropic/claude-sonnet-4-5",
    "claude-haiku-4":   "anthropic/claude-haiku-4-5",
    "grok-4":           "x-ai/grok-4.3",
    "grok-4.3":         "x-ai/grok-4.3",
    "gpt-4o":           "openai/gpt-4o",
    "o3":               "openai/o3",
    "gemini-2-5-pro":   "google/gemini-2.5-pro-preview-05-06",
    "deepseek-r1":      "deepseek/deepseek-r1",
    "grammaformer":     "local:grammaformer",
}

LOCAL_BASE_URLS: Dict[str, str] = {
    "ollama":    os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/v1",
    "lm-studio": "http://localhost:1234/v1",
    "lmstudio":  "http://localhost:1234/v1",
    "vllm":      "http://localhost:8000/v1",
    "local":     os.environ.get("LOCAL_BASE_URL", "http://localhost:11434/v1"),
}

REMOTE_API_PROVIDERS: Dict[str, Tuple[str, str]] = {
    "deepseek": ("https://api.deepseek.com/v1",                          "DEEPSEEK_API_KEY"),
    "qwen":     ("https://dashscope.aliyuncs.com/compatible-mode/v1",    "QWEN_API_KEY"),
    "groq":     ("https://api.groq.com/openai/v1",                       "GROQ_API_KEY"),
}


def _provider_for(model_str: str, base_url: str = "") -> str:
    """Provider name for build_agent_config, resolved rather than assumed.

    Every runner in this file passed provider="anthropic" as a literal while
    separately resolving model/base_url/api_key from --model. The two disagreed
    whenever --model pointed anywhere else, and the run died with a billing
    error from a provider that was never asked for. Honour IG_PROVIDER, then
    infer from the endpoint, then fall back to openrouter.
    """
    env = os.environ.get("IG_PROVIDER") or os.environ.get("IG_DEFAULT_PROVIDER")
    if env:
        return env
    if ":" in (model_str or ""):
        prefix = model_str.split(":", 1)[0].lower()
        if prefix in ("ollama", "lm-studio", "lmstudio", "vllm", "local"):
            return "local"
        if prefix in ("deepseek", "qwen", "openrouter", "anthropic", "openai"):
            return prefix
    u = (base_url or "").lower()
    for name in ("openrouter", "deepseek", "dashscope", "anthropic", "openai"):
        if name in u:
            return "openrouter" if name == "openrouter" else name
    if u:
        return "local"
    return "openrouter"


def resolve_model(model_str: str) -> Tuple[str, str, str]:
    """Return (model_id, base_url, api_key).

    Prefix syntax:
        ollama:llama3.2        → Ollama at localhost:11434/v1
        lm-studio:phi-4        → LM Studio at localhost:1234/v1
        lmstudio:phi-4         → same
        vllm:mistral           → vLLM at localhost:8000/v1
        local:my-model         → LOCAL_BASE_URL env var (default: ollama)
        deepseek:model-id      → DeepSeek API (DEEPSEEK_API_KEY)
        qwen:model-id          → Qwen/DashScope API (QWEN_API_KEY)
    No prefix → check MODEL_ALIASES, then use OpenRouter.
    """
    if ":" in model_str:
        prefix, model_id = model_str.split(":", 1)
        prefix_lower = prefix.lower()
        if prefix_lower in LOCAL_BASE_URLS:
            base = LOCAL_BASE_URLS[prefix_lower]
            key = os.environ.get("LOCAL_API_KEY", "local")
            if prefix_lower == "local" and model_id == "grammaformer":
                return "grammaformer", "", ""
            return model_id, base, key
        if prefix_lower in REMOTE_API_PROVIDERS:
            base, key_env = REMOTE_API_PROVIDERS[prefix_lower]
            key = os.environ.get(key_env, "")
            if not key:
                sys.exit(f"{key_env} not set (required for provider '{prefix_lower}').")
            return model_id, base, key

    resolved = MODEL_ALIASES.get(model_str, model_str)
    return resolved, "", ""


def resolve_model_id(alias: str) -> str:
    model_id, _, _ = resolve_model(alias)
    return model_id


# ═══════════════════════════════════════════════════════════════════════════════
# Retry config — exponential backoff for LLM calls (from harness §RETRY)
# ═══════════════════════════════════════════════════════════════════════════════

RETRY_CONFIG = {
    "rate_limit": 5,     # 429
    "server_error": 3,   # 5xx
    "timeout": 2,        # connection timeout
    "other": 3,          # other transient errors
}


# ═══════════════════════════════════════════════════════════════════════════════
# Agent runner functions
# ═══════════════════════════════════════════════════════════════════════════════

def build_parser():
    parser = argparse.ArgumentParser(
        prog="agents_cli.py",
        description="Unified CLI launcher for all agents"
    )
    parser.add_argument(
        "agent",
        choices=[
            "true_agentic_agent",
            "research_agent",
            "analysis_agent",
            "aider_code_agent",
            "perturbation_agent",
            "ensemble_agent",
            "retrodesign_agent",
            "criticality_agent",
            "imscription_generator",
            "axiom_generator",
            "autonomous_imscription",
        ],
        help="Agent to run"
    )
    parser.add_argument(
        "--task", "-t",
        help="Task description (positional arg or file)"
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Read task from file"
    )
    parser.add_argument(
        "--model", "-m",
        default="grok-4",
        help="Model to use (default: grok-4). Supports prefix syntax: ollama:, lm-studio:, local:, deepseek:, qwen:, groq:"
    )
    parser.add_argument(
        "--max-windings", "-w",
        type=int,
        default=100,
        help="Max iterations (default: 100)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Max tokens per think phase (default: 4096)"
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--show-trajectory",
        action="store_true",
        help="Print full trajectory on completion"
    )
    parser.add_argument(
        "--config",
        metavar="JSON",
        help="Inline JSON config for agent-specific options"
    )
    return parser


def load_config(config_str: str | None) -> dict:
    """Load config from JSON string."""
    if not config_str:
        return {}
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing config: {e}", file=sys.stderr)
        sys.exit(1)


def run_true_agentic_agent(task: str, args):
    """Run TrueAgenticAgent."""
    from agents import TrueAgenticAgent
    
    # Resolve model with prefix syntax
    model_id, base_url, api_key = resolve_model(args.model)
    
    agent = TrueAgenticAgent(
        model=args.model,
        max_windings=args.max_windings,
        max_think_tokens=args.max_tokens,
        verbose=not args.quiet,
        base_url=base_url,
        api_key=api_key,
    )
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("RESULT:")
    print(result)
    
    if args.show_trajectory:
        print("\n\nTRAJECTORY:")
        agent.print_trajectory()
    
    return {
        "agent": "true_agentic_agent",
        "result": result,
        "structural_type": agent.structural_type,
        "windings": len(agent.trajectory),
        "frobenius_ratio": agent.frobenius_ratio,
    }


def run_research_agent(task: str, args):
    """Run ResearchAgent."""
    from agents import ResearchAgent
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = {
        "model": model_id,
        "max_tokens": args.max_tokens,
    }
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = ResearchAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("RESEARCH RESULTS:")
    print(result.get("findings", ""))
    
    return {
        "agent": "research_agent",
        "result": result,
    }


def run_analysis_agent(task: str, args):
    """Run AnalysisAgent."""
    from agents import AnalysisAgent
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = {
        "model": model_id,
        "max_tokens": args.max_tokens,
    }
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = AnalysisAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("ANALYSIS RESULTS:")
    print(result.get("findings", ""))
    
    return {
        "agent": "analysis_agent",
        "result": result,
    }


def run_aider_code_agent(task: str, args):
    """Run AiderCodeAgent."""
    from agents import AiderCodeAgent
    
    if AiderCodeAgent is None:
        print("Error: AiderCodeAgent requires 'aider-chat'. Install with: pip install aider-chat", file=sys.stderr)
        sys.exit(1)
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = {
        "model": model_id,
        "auto_commits": True,
        "show_diffs": True,
    }
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = AiderCodeAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("CODE RESULTS:")
    print(result.get("findings", ""))
    
    return {
        "agent": "aider_code_agent",
        "result": result,
    }


def run_perturbation_agent(task: str, args):
    """Run PerturbationDesignAgent."""
    from agents import PerturbationDesignAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = PerturbationDesignAgent(config)
    
    # Parse task for imscription_name and delta_g if provided
    # format: "imscription_name delta_g [target_xi_cp]"
    parts = task.split()
    imscription_name = parts[0] if parts else "carboxylic_acid_dimer"
    delta_g = float(parts[1]) if len(parts) > 1 else -12.0
    target_xi_cp = float(parts[2]) if len(parts) > 2 else None
    
    result = agent.run_sync(imscription_name, delta_g, target_xi_cp)
    
    print("\n" + "="*72)
    print("PERTURBATION DESIGN RESULTS:")
    for rec in result.recommendations:
        print(f"  {rec.primitive}: {rec.suggested_change}")
        print(f"    Strategy: {rec.strategy}")
    
    return {
        "agent": "perturbation_agent",
        "result": result.to_dict(),
    }


def run_ensemble_agent(task: str, args):
    """Run EnsembleDesignAgent."""
    from agents import EnsembleDesignAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = EnsembleDesignAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("ENSEMBLE DESIGN RESULTS:")
    print(f"  Selected: {', '.join(result.selected_components)}")
    print(f"  Rationale: {result.llm_rationale}")
    
    return {
        "agent": "ensemble_agent",
        "result": result.to_dict(),
    }


def run_retrodesign_agent(task: str, args):
    """Run RetrodesignAgent."""
    from agents import RetrodesignAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = RetrodesignAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("RETRODESIGN RESULTS:")
    for step in result.steps:
        print(f"  {step}")
    
    return {
        "agent": "retrodesign_agent",
        "result": result.to_dict(),
    }


def run_criticality_agent(task: str, args):
    """Run CriticalityHuntingAgent."""
    from agents import CriticalityHuntingAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = CriticalityHuntingAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("CRITICALITY HUNT RESULTS:")
    print(result.report)
    
    return {
        "agent": "criticality_agent",
        "result": result.to_dict(),
    }


def run_imscribe_generator_agent(task: str, args):
    """Run ImscriptionGeneratorAgent."""
    from agents import ImscriptionGeneratorAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = ImscriptionGeneratorAgent(config)

    # ImscriptionGeneratorAgent exposes `async def run(task)` returning a dict.
    # This called `agent.run_sync(task)` — which does not exist — and then read
    # `.imscriptions` and `.to_dict()` off the result, neither of which exists
    # either (the dataclass field is `imscription`, singular, and carries no
    # to_dict). Three attribute errors in four lines; the first one fired and
    # masked the other two.
    import asyncio as _asyncio
    try:
        result = _asyncio.run(agent.run(task))
    except RuntimeError:
        # already inside a loop (e.g. called from an async host)
        _loop = _asyncio.new_event_loop()
        try:
            result = _loop.run_until_complete(agent.run(task))
        finally:
            _loop.close()

    print("\n" + "=" * 72)
    print("IMSCRIPTION GENERATION RESULTS:")
    if result.get("status") == "success":
        print(result.get("findings", ""))
    else:
        print(f"FAILED: {result.get('error', 'unknown error')}")

    return {
        "agent": "imscription_generator",
        "result": result,
    }


def run_axiom_generator_agent(task: str, args):
    """Run AxiomGuidedGeneratorAgent."""
    from agents import AxiomGuidedGeneratorAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = AxiomGuidedGeneratorAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("AXIOM GENERATION RESULTS:")
    print(result.axioms)
    
    return {
        "agent": "axiom_generator",
        "result": result.to_dict(),
    }


def run_autonomous_imscribe_agent(task: str, args):
    """Run AutonomousImscriptionDiscoveryAgent."""
    from agents import AutonomousImscriptionDiscoveryAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    model_id, base_url, api_key = resolve_model(args.model)
    
    config = build_agent_config(provider=_provider_for(args.model, base_url), model=model_id)
    if base_url:
        config["base_url"] = base_url
    if api_key and api_key != "local":
        config["api_key"] = api_key
    if args.config:
        config.update(load_config(args.config))
    
    agent = AutonomousImscriptionDiscoveryAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("AUTONOMOUS IMSCRIPTION RESULTS:")
    print(result)
    
    return {
        "agent": "autonomous_imscription",
        "result": result,
    }


def main():
    parser = build_parser()
    args = parser.parse_args()
    
    # Load task
    if args.file:
        with open(args.file) as f:
            task = f.read().strip()
    elif args.task:
        task = args.task
    else:
        parser.print_help()
        print("\nError: Provide task via --task or --file", file=sys.stderr)
        sys.exit(1)
    
    # Dispatch to agent
    runners = {
        "true_agentic_agent": run_true_agentic_agent,
        "research_agent": run_research_agent,
        "analysis_agent": run_analysis_agent,
        "aider_code_agent": run_aider_code_agent,
        "perturbation_agent": run_perturbation_agent,
        "ensemble_agent": run_ensemble_agent,
        "retrodesign_agent": run_retrodesign_agent,
        "criticality_agent": run_criticality_agent,
        "imscription_generator": run_imscribe_generator_agent,
        "axiom_generator": run_axiom_generator_agent,
        "autonomous_imscription": run_autonomous_imscribe_agent,
    }
    
    runner = runners.get(args.agent)
    if not runner:
        print(f"Unknown agent: {args.agent}", file=sys.stderr)
        sys.exit(1)
    
    # Run agent
    result = runner(task, args)
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
