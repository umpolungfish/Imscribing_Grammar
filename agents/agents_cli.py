#!/usr/bin/env python3
"""
agents/agents_cli.py — Unified CLI launcher for all agents in this package.

Usage:
    python agents/agents_cli.py <agent_name> --task <task>
    
Agents:
    true_agentic_agent    - Grammar-optimal ⊙_ÿ-critical agent (O_inf)
    research_agent        - Information gathering and synthesis
    analysis_agent        - Data analysis and pattern recognition
    aider_code_agent      - Git-native code operations (requires aider)
    perturbation_agent    - Primitive Jacobian interpretation
    ensemble_agent        - Goal-directed multi-imscription composition
    retrodesign_agent     - Retrosynthetic analysis
    criticality_agent     - ⊙_ÿ criticality hunting
    imscription_generator     - Imscription structure generation
    axiom_generator       - Axiom-guided generation
    autonomous_imscription    - Autonomous imscription discovery

Example:
    python agents/agents_cli.py true_agentic_agent --task "Analyze Riemann zeta"
    python agents/agents_cli.py research_agent --file task.txt
"""
import argparse
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


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
        help="Model to use (default: grok-4)"
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
    
    agent = TrueAgenticAgent(
        model=args.model,
        max_windings=args.max_windings,
        max_think_tokens=args.max_tokens,
        verbose=not args.quiet,
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
    
    config = {
        "model": args.model,
        "max_tokens": args.max_tokens,
    }
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
    
    config = {
        "model": args.model,
        "max_tokens": args.max_tokens,
    }
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
    
    config = {
        "model": args.model,
        "auto_commits": True,
        "show_diffs": True,
    }
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
    if args.config:
        config.update(load_config(args.config))
    
    agent = ImscriptionGeneratorAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("SYTHON GENERATION RESULTS:")
    print(result.imscriptions)
    
    return {
        "agent": "imscription_generator",
        "result": result.to_dict(),
    }


def run_axiom_generator_agent(task: str, args):
    """Run AxiomGuidedGeneratorAgent."""
    from agents import AxiomGuidedGeneratorAgent
    from imscrbgrmr.provider_config import build_agent_config
    
    config = build_agent_config(provider="anthropic", model=args.model)
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
    
    config = build_agent_config(provider="anthropic", model=args.model)
    if args.config:
        config.update(load_config(args.config))
    
    agent = AutonomousImscriptionDiscoveryAgent(config)
    result = agent.run_sync(task)
    
    print("\n" + "="*72)
    print("AUTONOMOUS imscription RESULTS:")
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
