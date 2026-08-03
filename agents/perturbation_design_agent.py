"""
Perturbation Design Agent — LLM-powered interpretation of Primitive Jacobian results.

Bridges the gap between the numerical Δξ_CP sensitivity output from
PerturbationEngine and actionable experimental chemistry recommendations.

The agent:
1. Runs PerturbationEngine.sweep_all() → full Primitive Jacobian
2. Runs fault_injection() → single points of failure
3. Optionally runs find_path_to_target() toward a target ξ_CP
4. Uses an LLM to translate numerical results into specific synthetic strategies
5. Returns a PerturbationDesignResult with ranked interventions

Usage::

    from agents.perturbation_design_agent import PerturbationDesignAgent
    from imscrbgrmr.provider_config import build_agent_config

    config = build_agent_config(provider="anthropic", model=None)
    agent = PerturbationDesignAgent(config)
    result = await agent.analyze(
        imscription_name="carboxylic_acid_dimer",
        delta_g=-12.0,
        target_xi_cp=5.0,   # optional — triggers pathfinding
    )
    print(result.recommendations[0])
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from framework import BaseAgent, ToolDefinitions
from imscrbgrmr import global_catalog
from imscrbgrmr.perturbation import PerturbationEngine, PrimitiveJacobian
from imscrbgrmr.provider_config import build_agent_config


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Intervention:
    """A single recommended experimental intervention."""
    primitive: str          # "⋈", "∈", "⊣", …
    primitive_name: str     # human-readable
    current_value: str
    suggested_change: str   # e.g. "upgrade ƒ^ð → ƒ^ż"
    expected_delta_xi: float   # nats (negative = improvement)
    strategy: str           # chemical strategy text from LLM
    feasibility: str        # "HIGH" / "MEDIUM" / "LOW"
    rationale: str


@dataclass
class PerturbationDesignResult:
    """Full result of a perturbation design analysis."""
    imscription_name: str
    delta_g: float
    baseline_xi_CP: float
    jacobian: PrimitiveJacobian
    fault_report: Dict[str, Any]
    path_to_target: Optional[Dict[str, Any]]   # None if no target given
    recommendations: List[Intervention]
    llm_summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "imscription": self.imscription_name,
            "delta_g_kJ_mol": self.delta_g,
            "baseline_xi_CP_nats": round(self.baseline_xi_CP, 4),
            "most_sensitive_primitive": (
                self.jacobian.most_sensitive.primitive
                if self.jacobian.most_sensitive else None
            ),
            "critical_primitives": [r.primitive for r in self.jacobian.critical_primitives],
            "fault_primitives": self.jacobian.fault_primitives,
            "system_robust": self.fault_report.get("system_robust", True),
            "path_to_target": self.path_to_target,
            "recommendations": [
                {
                    "primitive": iv.primitive,
                    "change": iv.suggested_change,
                    "expected_delta_xi_nats": round(iv.expected_delta_xi, 4),
                    "feasibility": iv.feasibility,
                    "strategy": iv.strategy,
                }
                for iv in self.recommendations
            ],
            "llm_summary": self.llm_summary,
        }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PerturbationDesignAgent(BaseAgent):
    """
    LLM agent that interprets Primitive Jacobian results as experimental interventions.

    For each sensitive primitive, the agent maps the numerical Δξ_CP to a concrete
    synthetic strategy: which bond to strengthen, which substituent to add, which
    solvent condition to change, etc.

    Usage::

        config = build_agent_config(provider="anthropic")
        agent = PerturbationDesignAgent(config)
        result = await agent.analyze("carboxylic_acid_dimer", delta_g=-12.0)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="perturbation_design",
            name="Perturbation Design Agent",
            description=(
                "Interprets Primitive Jacobian results and recommends experimental "
                "interventions to tune ξ_CP toward a target range."
            ),
            capabilities=[
                "primitive_jacobian_interpretation",
                "fault_injection_analysis",
                "perturbation_pathfinding",
                "experimental_strategy_recommendation",
            ],
            config=config,
            persona=(
                "Expert synthetic chemist and thermodynamic modeller specialising in "
                "the Unified Imscriptiveon framework. You translate numerical Δξ_CP "
                "sensitivity data into practical experimental strategies, citing "
                "specific functional-group changes, solvent conditions, substituent "
                "effects, and geometric modifications."
            ),
        )
        self.provider = self._setup_llm_provider_strict()
        self._engine = PerturbationEngine()

    def _setup_llm_provider_strict(self):
        """Setup LLM provider with MODEL_ALIASES resolution and base_url/api_key support.
        
        Supports prefix-syntax models resolved upstream by agents_cli.py.
        MODEL_ALIASES inherited from true_agentic_agent harness.
        """
        from framework.enhanced_llm_provider import get_llm_provider
        
        provider_name = self.config.get("provider", "anthropic")
        model = self.config.get("model", None)
        base_url = self.config.get("base_url", "")
        api_key = self.config.get("api_key", "")
        
        # Handle provider/model format like "deepseek/deepseek-chat"
        if "/" in provider_name:
            parts = provider_name.split("/", 1)
            provider_name = parts[0]
            model = parts[1] if len(parts) > 1 else model
        
        # Model alias resolution (from true_agentic_agent harness)
        MODEL_ALIASES = {
            "claude-opus-4":    "anthropic/claude-opus-4",
            "claude-sonnet-4":  "anthropic/claude-sonnet-4-5",
            "grok-4":           "x-ai/grok-4.3",
            "grok-4.3":         "x-ai/grok-4.3",
            "gpt-4o":           "openai/gpt-4o",
            "o3":               "openai/o3",
            "gemini-2-5-pro":   "google/gemini-2.5-pro-preview-05-06",
            "deepseek-r1":      "deepseek/deepseek-r1",
        }
        if model:
            model = MODEL_ALIASES.get(model, model)
        
        try:
            provider = get_llm_provider(provider_name, model=model)
            # Override base_url / api_key if provided in config (from agents_cli.py resolution)
            if base_url and hasattr(provider, 'base_url'):
                provider.base_url = base_url
            if api_key and hasattr(provider, 'api_key') and api_key != "local":
                provider.api_key = api_key
            return provider
        except ValueError as e:
            raise e

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            ToolDefinitions.file_read(),
            ToolDefinitions.file_write(),
            ToolDefinitions.json_load(),
            ToolDefinitions.json_save(),
            ToolDefinitions.run_command(),
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze(
        self,
        imscription_name: str,
        delta_g: float,
        target_xi_cp: Optional[float] = None,
        optimize_primitives: Optional[List[str]] = None,
        top_n: int = 5,
    ) -> PerturbationDesignResult:
        """
        Run full perturbation analysis and generate LLM-interpreted recommendations.

        Args:
            imscription_name: Name of imscription in the global catalog.
            delta_g: Assembly/reaction ΔG in kJ/mol.
            target_xi_cp: Optional target ξ_CP (nats). Triggers pathfinding.
            optimize_primitives: Primitives to vary in pathfinding (default: all).
            top_n: Number of top interventions to return.

        Returns:
            PerturbationDesignResult with recommendations.
        """
        imscription = global_catalog.get(imscription_name)
        if imscription is None:
            raise KeyError(f"Imscription '{imscription_name}' not found in global catalog.")

        # 1. Run Primitive Jacobian
        jacobian = self._engine.sweep_all(imscription, delta_g)

        # 2. Fault injection
        fault_report = self._engine.fault_injection(imscription, delta_g)

        # 3. Optional pathfinding
        path_result: Optional[Dict[str, Any]] = None
        if target_xi_cp is not None:
            path_result = self._engine.find_path_to_target(
                imscription, delta_g, target_xi_cp,
                optimize_primitives=optimize_primitives,
            )

        # 4. LLM interpretation
        llm_summary, recommendations = await self._interpret_with_llm(
            imscription, delta_g, jacobian, fault_report, path_result, top_n
        )

        return PerturbationDesignResult(
            imscription_name=imscription_name,
            delta_g=delta_g,
            baseline_xi_CP=jacobian.baseline_xi_CP,
            jacobian=jacobian,
            fault_report=fault_report,
            path_to_target=path_result,
            recommendations=recommendations,
            llm_summary=llm_summary,
            metadata={"provider": self.config.get("provider"), "model": self.config.get("model")},
        )

    # ------------------------------------------------------------------
    # LLM interpretation
    # ------------------------------------------------------------------

    async def _interpret_with_llm(
        self,
        imscription,
        delta_g: float,
        jacobian: PrimitiveJacobian,
        fault_report: Dict[str, Any],
        path_result: Optional[Dict[str, Any]],
        top_n: int,
    ):
        """Call LLM to translate Jacobian numbers into chemical strategies."""
        prompt = self._build_interpretation_prompt(imscription, delta_g, jacobian, fault_report, path_result, top_n)
        try:
            raw = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.3,
                system=self._system_prompt(),
            )
            return self._parse_llm_response(raw, jacobian)
        except Exception:
            return self._fallback_recommendations(jacobian, fault_report)

    def _build_interpretation_prompt(self, imscription, delta_g, jacobian, fault_report, path_result, top_n) -> str:
        jacobian_rows = "\n".join(
            f"  {r.primitive} ({r.primitive_name}): {r.old_value} → {r.new_value} "
            f"[Δξ_CP = {r.delta_xi_CP:+.3f} nats, {r.sensitivity}]"
            for r in jacobian.results[:8]
        )
        fault_lines = ""
        if fault_report.get("failure_points"):
            fault_lines = "SINGLE POINTS OF FAILURE:\n" + "\n".join(
                f"  {p}" for p in fault_report["failure_points"]
            )
        path_lines = ""
        if path_result and path_result.get("steps"):
            path_lines = "PATH TO TARGET:\n" + "\n".join(
                f"  Step {i+1}: {s}" for i, s in enumerate(path_result["steps"])
            )

        return f"""<task>
You are analysing perturbation sensitivity data for a chemical imscription.
Translate each numerical Δξ_CP sensitivity into a concrete experimental strategy.
</task>

<imscription>
Name: {imscription.name}
Description: {imscription.description or "N/A"}
Notation: {imscription.to_notation()}
ΔG: {delta_g} kJ/mol
Baseline ξ_CP: {jacobian.baseline_xi_CP:.3f} nats
</imscription>

<jacobian>
{jacobian_rows}
</jacobian>

{fault_lines}

{path_lines}

<instructions>
For each of the top-{top_n} most sensitive primitives, provide:
1. A specific synthetic/experimental strategy to exploit or protect that sensitivity
2. Feasibility assessment (HIGH/MEDIUM/LOW) with a one-line justification
3. Expected qualitative outcome on ξ_CP

Primitives that increase ξ_CP (positive Δξ_CP) represent DEGRADATION risks.
Primitives that decrease ξ_CP (negative Δξ_CP) represent IMPROVEMENT opportunities.

Focus on:
- For Fidelity (F): H-bond strength modifiers, fluorination, electron-withdrawing groups
- For Granularity (G): template effects, concentration, co-solvent control
- For Topology (T): ring closure strategies, macrocyclisation conditions
- For Recognition Mode (R): catalyst choice, reversibility conditions
- For Kinetics (K): temperature, catalyst loading, competing pathways
- For Polarity (P): protonation state, solvent dielectric, counterion effects
</instructions>

<output_format>
Return ONLY a JSON object:
{{
  "summary": "<2–3 sentence overview of what drives ξ_CP for this system>",
  "recommendations": [
    {{
      "primitive": "⋈",
      "primitive_name": "Fidelity",
      "current_value": "MEDIUM",
      "suggested_change": "upgrade ƒ^ð → ƒ^ż via electron-withdrawing substituents",
      "expected_delta_xi_nats": -1.2,
      "strategy": "<specific chemical modification>",
      "feasibility": "HIGH",
      "rationale": "<one sentence why>"
    }}
  ]
}}
</output_format>"""

    def _system_prompt(self) -> str:
        return (
            "You are an expert in Imscriptive system design using the Unified Imscriptiveon framework. "
            "You translate Δξ_CP Primitive Jacobian data into actionable intervention strategies. "
            "For primary-tier (molecular/supramolecular) systems your recommendations are "
            "chemically specific and experimentally grounded. For extended-tier (cross-domain) "
            "systems you apply domain-appropriate physical or engineering interventions. "
            "All recommendations are ranked by feasibility within their domain."
        )

    def _parse_llm_response(self, raw: str, jacobian: PrimitiveJacobian):
        import re
        # Extract JSON block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                summary = data.get("summary", "See recommendations below.")
                recs = []
                for r in data.get("recommendations", []):
                    recs.append(Intervention(
                        primitive=r.get("primitive", "?"),
                        primitive_name=r.get("primitive_name", "?"),
                        current_value=r.get("current_value", "?"),
                        suggested_change=r.get("suggested_change", ""),
                        expected_delta_xi=float(r.get("expected_delta_xi_nats", 0.0)),
                        strategy=r.get("strategy", ""),
                        feasibility=r.get("feasibility", "MEDIUM"),
                        rationale=r.get("rationale", ""),
                    ))
                return summary, recs
            except (json.JSONDecodeError, TypeError):
                pass
        return self._fallback_recommendations(jacobian, {})

    def _fallback_recommendations(self, jacobian: PrimitiveJacobian, fault_report: Dict):
        """Generate rule-based fallback when LLM is unavailable."""
        STRATEGIES = {
            "⋈": "Strengthen H-bond donors/acceptors; add electron-withdrawing substituents to raise fidelity.",
            "∈": "Use template-directed assembly or concentration effects to tune mesoscale ordering.",
            "⊣": "Explore macrocyclisation or ring-closing conditions to alter topology.",
            "⊤": "Adjust temperature or add competing kinetic pathways to modify barrier heights.",
            ">": "Switch between reversible (dynamic covalent) and non-covalent recognition modes.",
            "⊢": "Vary solvent system or co-crystal partner to shift domain character.",
            "<": "Modify protonation state or use directed H-bond arrays to adjust polarity.",
            "<": "Tune proximity to critical point via concentration or temperature ramp.",
        }
        recs = []
        for r in jacobian.results[:5]:
            recs.append(Intervention(
                primitive=r.primitive,
                primitive_name=r.primitive_name,
                current_value=r.old_value,
                suggested_change=f"{r.old_value} → {r.new_value}",
                expected_delta_xi=r.delta_xi_CP,
                strategy=STRATEGIES.get(r.primitive, "See Jacobian data."),
                feasibility="MEDIUM",
                rationale=f"Δξ_CP = {r.delta_xi_CP:+.3f} nats ({r.sensitivity} sensitivity).",
            ))
        summary = (
            f"Rule-based fallback: most sensitive primitive is "
            f"{jacobian.most_sensitive.primitive if jacobian.most_sensitive else 'N/A'} "
            f"with baseline ξ_CP = {jacobian.baseline_xi_CP:.3f} nats."
        )
        return summary, recs

    # ------------------------------------------------------------------
    # BaseAgent entry point
    # ------------------------------------------------------------------

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """BaseAgent interface. Task format: '<imscription_name> <delta_g> [target_xi_cp]'"""
        import re
        parts = task.strip().split()
        if len(parts) < 2:
            return {"status": "error", "error": "Usage: <imscription_name> <delta_g> [target_xi_cp]"}
        try:
            imscription_name = parts[0]
            delta_g = float(parts[1])
            target = float(parts[2]) if len(parts) > 2 else None
            result = await self.analyze(imscription_name, delta_g, target_xi_cp=target)
            return {
                "status": "success",
                "findings": result.llm_summary,
                "artifacts": self.artifacts,
                "metadata": result.to_dict(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

async def design_perturbation(
    imscription_name: str,
    delta_g: float,
    target_xi_cp: Optional[float] = None,
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> PerturbationDesignResult:
    """Quick helper: run perturbation design analysis."""
    config = build_agent_config(provider=provider, model=model)
    agent = PerturbationDesignAgent(config)
    return await agent.analyze(imscription_name, delta_g, target_xi_cp=target_xi_cp)
