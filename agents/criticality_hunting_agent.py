"""
Criticality Hunting Agent — Automated search for near-⊙ systems.

Combines Varma probe degeneracy scoring with perturbation pathfinding to:
1. Scan the entire catalog and score each imscription's ⊙ candidacy
2. Identify near-critical systems (score 0.40–0.70 — "approaching" range)
3. Run PerturbationEngine.find_path_to_target() toward a ⊙ ξ_CP threshold
4. Use an LLM to evaluate which proposed modifications are chemically realistic
5. Optionally generate new LLM-proposed upgraded imscription candidates

The agent focuses on "near-critical" systems rather than already-critical ones,
since those represent the highest-value targets for ⊙ assignment.

Usage::

    from agents.criticality_hunting_agent import CriticalityHuntingAgent
    from imscrbgrmr.provider_config import build_agent_config

    config = build_agent_config(provider="anthropic")
    agent = CriticalityHuntingAgent(config)
    report = await agent.hunt(
        delta_g=-12.0,
        target_xi_cp=6.5,
        top_n=10,
    )
    for c in report.candidates:
        print(c.imscription_name, c.current_score, c.upgrade_path)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from framework import BaseAgent, ToolDefinitions
from imscrbgrmr import global_catalog
from imscrbgrmr.varma_probe import degeneracy_strength
from imscrbgrmr.perturbation import PerturbationEngine
from imscrbgrmr.provider_config import build_agent_config


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class CriticalityCandidate:
    """A single near-⊙ candidate with upgrade path."""
    imscription_name: str
    current_score: float          # degeneracy_strength score
    current_tier: str             # "none" / "logarithmic" / "power-law" / "collapse"
    current_xi_CP: Optional[float]
    upgrade_path: Optional[Dict[str, Any]]   # from PerturbationEngine.find_path_to_target()
    llm_feasibility: str          # "HIGH" / "MEDIUM" / "LOW"
    llm_strategy: str             # LLM-proposed chemical modification
    flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "imscription": self.imscription_name,
            "current_score": round(self.current_score, 3),
            "current_tier": self.current_tier,
            "current_xi_CP_nats": round(self.current_xi_CP, 4) if self.current_xi_CP else None,
            "upgrade_path": self.upgrade_path,
            "llm_feasibility": self.llm_feasibility,
            "llm_strategy": self.llm_strategy,
            "flags": self.flags,
        }


@dataclass
class CriticalityHuntReport:
    """Full report from a criticality hunting run."""
    candidates: List[CriticalityCandidate]   # sorted by score descending
    already_critical: List[str]              # imscription names already at ⊙
    scan_stats: Dict[str, Any]
    llm_summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "already_critical": self.already_critical,
            "scan_stats": self.scan_stats,
            "llm_summary": self.llm_summary,
        }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class CriticalityHuntingAgent(BaseAgent):
    """
    Hunts for near-⊙ imscriptions in the catalog and proposes upgrade paths.

    Combines Varma probe degeneracy scoring (imscrbgrmr.varma_probe) with
    PerturbationEngine pathfinding and LLM chemical evaluation.

    Usage::

        config = build_agent_config(provider="anthropic")
        agent = CriticalityHuntingAgent(config)
        report = await agent.hunt(delta_g=-12.0, target_xi_cp=6.5, top_n=10)
    """

    # Score thresholds (from varma_probe tier definitions)
    PHI_C_THRESHOLD = 0.70       # already critical
    APPROACHING_LOW = 0.35       # lower bound for "approaching" window
    APPROACHING_HIGH = 0.70      # upper bound (exclusive)

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="criticality_hunting",
            name="Criticality Hunting Agent",
            description=(
                "Scans the catalog for near-⊙ systems and generates targeted "
                "upgrade paths using Varma probe scoring and perturbation pathfinding."
            ),
            capabilities=[
                "varma_probe_catalog_scan",
                "perturbation_pathfinding",
                "phi_c_upgrade_strategy",
                "llm_feasibility_assessment",
            ],
            config=config,
            persona=(
                "Expert in quantum criticality and self-organised chemical systems. "
                "You identify imscriptions approaching the critical point (⊙) and design "
                "targeted chemical modifications to push them into the critical regime. "
                "Your proposals are grounded in the Varma QXY universality class and "
                "scale-free degeneracy theory."
            ),
        )
        self.provider = self._setup_llm_provider_strict()
        self._perturb_engine = PerturbationEngine()

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

    async def hunt(
        self,
        delta_g: float = -12.0,
        target_xi_cp: float = 6.5,
        top_n: int = 10,
        optimize_primitives: Optional[List[str]] = None,
        include_already_critical: bool = False,
    ) -> CriticalityHuntReport:
        """
        Hunt for near-⊙ candidates in the global catalog.

        Args:
            delta_g: ΔG used for ξ_CP baseline computation (kJ/mol).
            target_xi_cp: Target ξ_CP (nats) for perturbation pathfinding.
                         Lower values correspond to more efficient, critical-like systems.
            top_n: Maximum number of candidates to analyse in depth.
            optimize_primitives: Primitives to vary in pathfinding (default: ["ƒ","Γ","Þ","Φ"]).
            include_already_critical: If True, include ⊙ entries in output.

        Returns:
            CriticalityHuntReport.
        """
        optimize_primitives = optimize_primitives or ["ƒ", "Γ", "Þ", "Φ"]

        # 1. Scan catalog
        approaching, already_critical, stats = self._scan_catalog(delta_g)

        # 2. Run pathfinding on top-N approaching candidates
        candidates = await self._build_candidates(
            approaching[:top_n], delta_g, target_xi_cp, optimize_primitives
        )

        # 3. LLM evaluation
        candidates, llm_summary = await self._llm_evaluate(candidates)

        # Sort by score descending
        candidates.sort(key=lambda c: c.current_score, reverse=True)

        return CriticalityHuntReport(
            candidates=candidates,
            already_critical=already_critical if include_already_critical else [],
            scan_stats={
                **stats,
                "top_n_analysed": len(candidates),
                "target_xi_cp_nats": target_xi_cp,
                "delta_g_kJ_mol": delta_g,
            },
            llm_summary=llm_summary,
            metadata={"provider": self.config.get("provider"), "model": self.config.get("model")},
        )

    # ------------------------------------------------------------------
    # Catalog scan
    # ------------------------------------------------------------------

    def _scan_catalog(
        self, delta_g: float
    ) -> Tuple[List[Tuple[float, str, str]], List[str], Dict[str, Any]]:
        """
        Score every imscription in the catalog.

        Returns:
            approaching: [(score, tier, name)] for near-critical imscriptions, sorted descending
            already_critical: names already at ⊙ (score ≥ 0.70)
            stats: scan statistics dict
        """
        approaching: List[Tuple[float, str, str]] = []
        already_critical: List[str] = []

        total = 0
        errors = 0
        for name, imscription in global_catalog._imscriptions.items():
            total += 1
            try:
                score, tier = degeneracy_strength(imscription)
                if score >= self.PHI_C_THRESHOLD:
                    already_critical.append(name)
                elif score >= self.APPROACHING_LOW:
                    approaching.append((score, tier, name))
            except Exception:
                errors += 1

        approaching.sort(reverse=True)

        stats = {
            "total_scanned": total,
            "already_critical": len(already_critical),
            "approaching_window": len(approaching),
            "scan_errors": errors,
        }
        return approaching, already_critical, stats

    # ------------------------------------------------------------------
    # Candidate building
    # ------------------------------------------------------------------

    async def _build_candidates(
        self,
        approaching: List[Tuple[float, str, str]],
        delta_g: float,
        target_xi_cp: float,
        optimize_primitives: List[str],
    ) -> List[CriticalityCandidate]:
        """Run perturbation pathfinding for each near-critical candidate."""
        candidates = []
        for score, tier, name in approaching:
            imscription = global_catalog.get(name)
            if imscription is None:
                continue

            # Baseline ξ_CP
            try:
                baseline = self._perturb_engine.compute_baseline(imscription, delta_g)
                xi_cp = baseline.xi_CP
            except Exception:
                xi_cp = None

            # Perturbation pathfinding
            path_result = None
            try:
                path_result = self._perturb_engine.find_path_to_target(
                    imscription, delta_g, target_xi_cp,
                    optimize_primitives=optimize_primitives,
                )
            except Exception:
                pass

            candidates.append(CriticalityCandidate(
                imscription_name=name,
                current_score=score,
                current_tier=tier,
                current_xi_CP=xi_cp,
                upgrade_path=path_result,
                llm_feasibility="MEDIUM",   # will be updated by LLM
                llm_strategy="",
                flags=[],
            ))

        return candidates

    # ------------------------------------------------------------------
    # LLM evaluation
    # ------------------------------------------------------------------

    async def _llm_evaluate(
        self, candidates: List[CriticalityCandidate]
    ) -> Tuple[List[CriticalityCandidate], str]:
        """Use LLM to assess chemical feasibility of upgrade paths."""
        if not candidates:
            return candidates, "No near-critical candidates found in the catalog."

        prompt = self._build_evaluation_prompt(candidates)
        try:
            raw = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.3,
                system=self._system_prompt(),
            )
            candidates, summary = self._parse_llm_response(raw, candidates)
        except Exception:
            summary = (
                f"Found {len(candidates)} near-critical candidates. "
                f"Top candidate: {candidates[0].imscription_name} "
                f"(score={candidates[0].current_score:.3f}, tier={candidates[0].current_tier})."
            )
        return candidates, summary

    def _build_evaluation_prompt(self, candidates: List[CriticalityCandidate]) -> str:
        candidate_lines = []
        for c in candidates[:8]:
            path_summary = "No path found"
            if c.upgrade_path:
                steps = c.upgrade_path.get("steps", [])
                reachable = c.upgrade_path.get("reachable", False)
                path_summary = f"Reachable={reachable}, steps={len(steps)}: {steps[:3]}"
            candidate_lines.append(
                f"- {c.imscription_name}: score={c.current_score:.3f}, tier={c.current_tier}, "
                f"ξ_CP={c.current_xi_CP:.3f if c.current_xi_CP else 'N/A'} nats | "
                f"Upgrade path: {path_summary}"
            )
        return f"""<task>
Evaluate the chemical feasibility of pushing near-critical imscriptions to ⊙.
</task>

<candidates>
{chr(10).join(candidate_lines)}
</candidates>

<background>
⊙ (criticality) requires G/D degeneracy: the system must exhibit scale-free
behavior where spatial correlation length is logarithmically determined by
temporal correlation length (Varma QXY universality class).

Key upgrade levers:
- F HIGH + T_⋈ → tighter cyclic constraint → lower ξ_CP → approach criticality
- G_ג (mesoscale) with cooperative induction → Axiom 3 G/D coupling
- ⊙ explicit assignment via upgrade from 𐑢
- 𐑡 topology enables scale-free propagation
</background>

<instructions>
For each candidate, provide:
1. Chemical feasibility of the proposed upgrade path (HIGH/MEDIUM/LOW)
2. One concrete synthetic strategy to push the system toward ⊙
3. Any flags (axiom conflicts, unrealistic modifications)

Write a 3-sentence summary of the most promising ⊙ upgrade opportunities.
</instructions>

<output_format>
Return ONLY this JSON:
{{
  "summary": "<3-sentence overview of best upgrade opportunities>",
  "evaluations": [
    {{
      "imscription_name": "<name>",
      "feasibility": "HIGH",
      "strategy": "<concrete chemical modification>",
      "flags": ["<any concerns>"]
    }}
  ]
}}
</output_format>"""

    def _system_prompt(self) -> str:
        return (
            "You are an expert in criticality and scale-free behaviour across Imscriptive systems. "
            "You evaluate whether proposed primitive-tier upgrades are physically realistic "
            "within their domain and propose specific modifications to push systems toward "
            "the Varma QXY critical point (⊙) in the Unified Imscriptiveon framework. "
            "For primary-tier systems this means concrete chemical modifications; "
            "for extended-tier systems this means domain-appropriate structural or parameter changes."
        )

    def _parse_llm_response(
        self, raw: str, candidates: List[CriticalityCandidate]
    ) -> Tuple[List[CriticalityCandidate], str]:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                summary = data.get("summary", "")
                evals = {e["imscription_name"]: e for e in data.get("evaluations", [])}
                for c in candidates:
                    ev = evals.get(c.imscription_name, {})
                    if ev:
                        c.llm_feasibility = ev.get("feasibility", "MEDIUM")
                        c.llm_strategy = ev.get("strategy", "")
                        c.flags = ev.get("flags", [])
                return candidates, summary
            except (json.JSONDecodeError, TypeError):
                pass
        summary = (
            f"Found {len(candidates)} near-critical candidates. "
            f"Top: {candidates[0].imscription_name} (score={candidates[0].current_score:.3f})."
        )
        return candidates, summary

    # ------------------------------------------------------------------
    # BaseAgent entry point
    # ------------------------------------------------------------------

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """BaseAgent interface. Task is ignored; uses default parameters."""
        try:
            report = await self.hunt()
            return {
                "status": "success",
                "findings": (
                    f"Criticality hunt: {len(report.candidates)} near-⊙ candidates found.\n"
                    f"{report.llm_summary}"
                ),
                "artifacts": self.artifacts,
                "metadata": report.to_dict(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

async def hunt_criticality(
    delta_g: float = -12.0,
    target_xi_cp: float = 6.5,
    top_n: int = 10,
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> CriticalityHuntReport:
    """Quick helper: run criticality hunt on the global catalog."""
    config = build_agent_config(provider=provider, model=model)
    agent = CriticalityHuntingAgent(config)
    return await agent.hunt(delta_g=delta_g, target_xi_cp=target_xi_cp, top_n=top_n)
