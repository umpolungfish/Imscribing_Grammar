"""
Ensemble Design Agent — Goal-directed multi-imscription composition.

Given a desired emergent property (or a target system ξ_CP range), this agent:
1. Searches the catalog for imscription candidates matching the goal
2. Evaluates combinations with EnsembleCatalog.check_pairwise()
3. Uses an LLM to select the best combination and suggest modifications
4. Returns an EnsembleDesignResult with the recommended ensemble + EnsembleReport

Supported goal types:
  "emergent_criticality"         — maximize ensemble degeneracy score
  "granularity_amplification"    — trigger Axiom 3 G_ב → G_ג induction
  "fidelity_maximization"        — maximize ensemble consistency score
  "low_xi_cp"                    — minimize system thermodynamic inefficiency
  "custom:<description>"         — free-form description passed to LLM

Usage::

    from agents.ensemble_design_agent import EnsembleDesignAgent
    from imscrbgrmr.provider_config import build_agent_config

    config = build_agent_config(provider="anthropic")
    agent = EnsembleDesignAgent(config)
    result = await agent.design(
        goal="emergent_criticality",
        n_components=3,
        delta_g_assembly=-80.0,
    )
    print(result.report.is_consistent, result.llm_rationale)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from framework import BaseAgent, ToolDefinitions
from imscrbgrmr import Imscription, Dimensionality, global_catalog
from imscrbgrmr.ensembler import EnsembleCatalog, EnsembleReport
from imscrbgrmr.varma_probe import degeneracy_strength
from imscrbgrmr.provider_config import build_agent_config


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class EnsembleDesignResult:
    """Result of goal-directed ensemble design."""
    goal: str
    selected_components: List[str]       # imscription names
    report: EnsembleReport
    system_thermo: Optional[Dict[str, Any]]   # from compute_system_xi_CP
    llm_rationale: str
    alternatives: List[List[str]] = field(default_factory=list)  # other ranked combos
    suggestions: List[str] = field(default_factory=list)         # LLM modifications
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "selected_components": self.selected_components,
            "report": self.report.to_dict(),
            "system_thermo": self.system_thermo,
            "llm_rationale": self.llm_rationale,
            "alternatives": self.alternatives,
            "suggestions": self.suggestions,
        }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class EnsembleDesignAgent(BaseAgent):
    """
    Designs multi-imscription assemblies targeting a specified emergent property.

    Combines catalog search, pairwise compatibility checking, and LLM reasoning
    to propose and evaluate ensemble compositions.

    Usage::

        config = build_agent_config(provider="anthropic")
        agent = EnsembleDesignAgent(config)
        result = await agent.design("emergent_criticality", n_components=3)
    """

    # Goal → catalog search keywords
    GOAL_KEYWORDS: Dict[str, List[str]] = {
        "emergent_criticality": ["critical", "phi_c", "scale-free", "varma", "percolation"],
        "granularity_amplification": ["network", "framework", "global", "cooperative", "mof"],
        "fidelity_maximization": ["fidelity", "high", "hbar", "cyclic", "dimer", "base_pair"],
        "low_xi_cp": ["efficient", "eta", "thermodynamic", "low_xi", "optimal"],
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="ensemble_design",
            name="Ensemble Design Agent",
            description=(
                "Designs multi-imscription systems to achieve desired emergent properties "
                "by combining catalog search, pairwise analysis, and LLM selection."
            ),
            capabilities=[
                "goal_directed_ensemble_design",
                "catalog_search",
                "pairwise_compatibility_analysis",
                "emergent_property_optimization",
            ],
            config=config,
            persona=(
                "Expert in multi-component chemical assembly design. You select and combine "
                "imscriptions from the Unified Imscriptiveon catalog to achieve target emergent "
                "properties (criticality, granularity amplification, thermodynamic efficiency). "
                "You reason from axiom compatibility, emergent property scores, and chemical "
                "intuition to propose optimal ensembles."
            ),
        )
        self.provider = self._setup_llm_provider_strict()

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

    async def design(
        self,
        goal: str,
        n_components: int = 3,
        component_pool: Optional[List[str]] = None,
        delta_g_assembly: float = -80.0,
        interface_overhead_bits: float = 1.5,
        max_combinations: int = 20,
    ) -> EnsembleDesignResult:
        """
        Design a multi-imscription ensemble for the given goal.

        Args:
            goal: Desired property — one of GOAL_KEYWORDS keys or 'custom:<description>'.
            n_components: Number of components in the target ensemble.
            component_pool: Optional list of imscription names to consider (default: full catalog).
            delta_g_assembly: ΔG_assembly in kJ/mol for system ξ_CP computation.
            interface_overhead_bits: Interface overhead bits for Landauer term.
            max_combinations: Max combinations to evaluate before LLM selection.

        Returns:
            EnsembleDesignResult with recommended ensemble.
        """
        # 1. Build candidate pool
        pool = self._build_candidate_pool(goal, component_pool, n_components)

        if len(pool) < n_components:
            # Pad with any remaining catalog entries
            all_names = list(global_catalog._imscriptions.keys())
            for name in all_names:
                if name not in pool and len(pool) < max(n_components * 3, 10):
                    pool.append(name)

        # 2. Evaluate combinations
        combos = self._evaluate_combinations(pool, n_components, goal, max_combinations)

        # 3. LLM selects and annotates best combination
        best_combo, llm_rationale, suggestions, alternatives = await self._llm_select(
            goal, combos, n_components
        )

        # 4. Build full report for chosen combo
        ensemble = EnsembleCatalog()
        for name in best_combo:
            try:
                ensemble.add(name)
            except KeyError:
                pass

        report = ensemble.check_pairwise()

        system_thermo = None
        if ensemble.components():
            system_thermo = ensemble.compute_system_xi_CP(
                delta_g_assembly=delta_g_assembly,
                interface_overhead_bits=interface_overhead_bits,
            )

        return EnsembleDesignResult(
            goal=goal,
            selected_components=best_combo,
            report=report,
            system_thermo=system_thermo,
            llm_rationale=llm_rationale,
            alternatives=alternatives,
            suggestions=suggestions,
            metadata={"provider": self.config.get("provider"), "model": self.config.get("model")},
        )

    # ------------------------------------------------------------------
    # Candidate search
    # ------------------------------------------------------------------

    def _build_candidate_pool(self, goal: str, pool: Optional[List[str]], n_needed: int) -> List[str]:
        """Find catalog imscriptions relevant to the goal."""
        if pool:
            return list(pool)

        keywords = self.GOAL_KEYWORDS.get(goal, [])
        if goal.startswith("custom:"):
            desc = goal[7:].lower()
            keywords = desc.split()

        imscriptions = global_catalog._imscriptions
        scored: List[Tuple[float, str]] = []

        for name, s in imscriptions.items():
            score = 0.0
            text = f"{name} {s.description or ''}".lower()
            for kw in keywords:
                if kw in text:
                    score += 1.0

            # Score by goal-specific primitive signals
            if goal == "emergent_criticality":
                ds, _ = degeneracy_strength(s)
                score += ds * 2.0
            elif goal == "granularity_amplification":
                from imscrbgrmr.models import Granularity
                if s.granularity == Granularity.thigh:
                    score += 1.5
                elif s.granularity == Granularity.bib:
                    score += 0.8
            elif goal == "fidelity_maximization":
                from imscrbgrmr.models import Fidelity
                if s.fidelity == Fidelity.peep:
                    score += 1.5
            elif goal == "low_xi_cp":
                from imscrbgrmr.models import Fidelity
                if s.fidelity == Fidelity.peep:
                    score += 1.0  # high fidelity → lower ξ_CP typically

            scored.append((score, name))

        scored.sort(reverse=True)
        return [name for _, name in scored[:max(n_needed * 4, 20)]]

    # ------------------------------------------------------------------
    # Combination evaluation
    # ------------------------------------------------------------------

    def _evaluate_combinations(
        self,
        pool: List[str],
        n: int,
        goal: str,
        max_combos: int,
    ) -> List[Dict[str, Any]]:
        """Score top combinations without calling the LLM."""
        from itertools import combinations

        results = []
        for combo in list(combinations(pool, n))[:max_combos]:
            combo = list(combo)
            try:
                ensemble = EnsembleCatalog()
                for name in combo:
                    ensemble.add(name)
                report = ensemble.check_pairwise()

                # Quick goal score
                goal_score = self._score_combo(report, goal)

                results.append({
                    "components": combo,
                    "consistency_score": report.consistency_score,
                    "is_consistent": report.is_consistent,
                    "goal_score": goal_score,
                    "emergent_detected": any(ep.detected for ep in report.emergent_properties),
                    "emergent_names": [ep.property_name for ep in report.emergent_properties if ep.detected],
                })
            except Exception:
                continue

        results.sort(key=lambda x: (x["goal_score"], x["consistency_score"]), reverse=True)
        return results[:10]  # top 10 for LLM

    def _score_combo(self, report: EnsembleReport, goal: str) -> float:
        """Map EnsembleReport → goal-specific score."""
        score = report.consistency_score
        for ep in report.emergent_properties:
            if not ep.detected:
                continue
            if goal == "emergent_criticality" and "Criticality" in ep.property_name:
                score += (ep.score or 0.0) * 2.0
            elif goal == "granularity_amplification" and "Granularity" in ep.property_name:
                score += 1.5
            elif goal == "fidelity_maximization" and "Fidelity" not in ep.property_name:
                score -= 0.5  # penalise fidelity degradation
        return score

    # ------------------------------------------------------------------
    # LLM selection
    # ------------------------------------------------------------------

    async def _llm_select(
        self,
        goal: str,
        combos: List[Dict[str, Any]],
        n: int,
    ) -> Tuple[List[str], str, List[str], List[List[str]]]:
        """Use LLM to select and justify the best combination."""
        if not combos:
            return [], "No valid combinations found.", [], []

        prompt = self._build_selection_prompt(goal, combos, n)
        try:
            raw = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 3000),
                temperature=0.3,
                system=self._system_prompt(),
            )
            return self._parse_selection_response(raw, combos)
        except Exception:
            # Fallback: pick highest-scored combo
            best = combos[0]
            return (
                best["components"],
                f"Rule-based selection: highest goal score ({best['goal_score']:.3f}).",
                [],
                [c["components"] for c in combos[1:4]],
            )

    def _build_selection_prompt(self, goal: str, combos: List[Dict], n: int) -> str:
        combo_lines = "\n".join(
            f"  Option {i+1}: {c['components']} "
            f"[consistency={c['consistency_score']:.2f}, goal_score={c['goal_score']:.2f}, "
            f"emergent={c['emergent_names']}]"
            for i, c in enumerate(combos[:8])
        )
        return f"""<task>
Select the best {n}-component imscription ensemble for the goal: **{goal}**
</task>

<candidates>
{combo_lines}
</candidates>

<instructions>
1. Select the best option for the stated goal, explaining why.
2. Suggest 2–3 specific modifications that could further improve the ensemble.
3. List 2 runner-up alternatives.
</instructions>

<output_format>
Return ONLY this JSON:
{{
  "selected_option": <1-based integer>,
  "rationale": "<explanation of why this ensemble best achieves {goal}>",
  "suggestions": [
    "<modification 1>",
    "<modification 2>"
  ],
  "alternatives": [<option_number>, <option_number>]
}}
</output_format>"""

    def _system_prompt(self) -> str:
        return (
            "You are an expert in Imscriptive ensemble composition using the Unified Imscriptiveon "
            "framework. You evaluate ensemble compatibility, emergent properties, and "
            "thermodynamic efficiency to recommend optimal multi-imscription compositions. "
            "Primary-tier ensembles (molecular/supramolecular) are evaluated against "
            "experimental interaction energies. Extended-tier ensembles use analogue metrics."
        )

    def _parse_selection_response(
        self, raw: str, combos: List[Dict]
    ) -> Tuple[List[str], str, List[str], List[List[str]]]:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                idx = int(data.get("selected_option", 1)) - 1
                idx = max(0, min(idx, len(combos) - 1))
                best = combos[idx]["components"]
                rationale = data.get("rationale", "Selected by LLM.")
                suggestions = data.get("suggestions", [])
                alt_idxs = [int(i) - 1 for i in data.get("alternatives", [])]
                alternatives = [combos[i]["components"] for i in alt_idxs if 0 <= i < len(combos)]
                return best, rationale, suggestions, alternatives
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        best = combos[0]
        return best["components"], "Fallback: highest score.", [], [c["components"] for c in combos[1:3]]

    # ------------------------------------------------------------------
    # BaseAgent entry point
    # ------------------------------------------------------------------

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """BaseAgent interface. Task is the goal string."""
        try:
            result = await self.design(goal=task.strip())
            return {
                "status": "success",
                "findings": (
                    f"Ensemble for '{result.goal}': {result.selected_components}\n"
                    f"Consistent: {result.report.is_consistent}\n"
                    f"Rationale: {result.llm_rationale}"
                ),
                "artifacts": self.artifacts,
                "metadata": result.to_dict(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

async def design_ensemble(
    goal: str,
    n_components: int = 3,
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> EnsembleDesignResult:
    """Quick helper: design an ensemble for a given goal."""
    config = build_agent_config(provider=provider, model=model)
    agent = EnsembleDesignAgent(config)
    return await agent.design(goal, n_components=n_components)
