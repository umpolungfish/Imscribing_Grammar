"""
Retrodesign Agent — LLM-enhanced retrosynthetic decomposition analysis.

Wraps RetrodesignEngine with an LLM layer that:
1. Interprets the decomposition tree in chemical terms
2. Ranks valid leaves by synthetic accessibility
3. Flags unusual retrosynthetic choices with explanations
4. Suggests catalog additions for missing sub-imscriptions
5. Identifies the most strategically useful retrosynthetic routes

Usage::

    from agents.retrodesign_agent import RetrodesignAgent
    from imscrbgrmr.provider_config import build_agent_config

    config = build_agent_config(provider="anthropic")
    agent = RetrodesignAgent(config)
    result = await agent.analyze(
        target="proline_aldol_cycle",
        max_depth=3,
        prune_axioms=[1, 2, 4, 6],
    )
    for route in result.ranked_routes:
        print(route.rank, route.leaf_name, route.accessibility)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from framework import BaseAgent, ToolDefinitions
from imscrbgrmr import global_catalog
from imscrbgrmr.retrodesign import RetrodesignEngine, DecompositionTree, DecompositionNode
from imscrbgrmr.provider_config import build_agent_config


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RetroRoute:
    """A single ranked retrosynthetic route (valid leaf)."""
    rank: int
    leaf_name: str
    notation: Optional[str]
    accessibility: str     # "HIGH" / "MEDIUM" / "LOW"
    reasoning: str         # LLM explanation
    catalog_gaps: List[str] = field(default_factory=list)  # suggested new catalog entries
    flags: List[str] = field(default_factory=list)


@dataclass
class RetrodesignAnalysisResult:
    """Full result of LLM-enhanced retrodesign analysis."""
    target: str
    tree: DecompositionTree
    ranked_routes: List[RetroRoute]
    pruned_count: int
    prune_axioms: List[int]
    llm_summary: str
    suggested_catalog_additions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "valid_leaves": len(self.ranked_routes),
            "pruned_count": self.pruned_count,
            "prune_axioms": self.prune_axioms,
            "ranked_routes": [
                {
                    "rank": r.rank,
                    "leaf": r.leaf_name,
                    "notation": r.notation,
                    "accessibility": r.accessibility,
                    "reasoning": r.reasoning,
                    "catalog_gaps": r.catalog_gaps,
                    "flags": r.flags,
                }
                for r in self.ranked_routes
            ],
            "suggested_catalog_additions": self.suggested_catalog_additions,
            "llm_summary": self.llm_summary,
        }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class RetrodesignAgent(BaseAgent):
    """
    LLM-enhanced retrosynthetic decomposition agent.

    Runs RetrodesignEngine to get the axiom-pruned decomposition tree, then
    uses an LLM to rank valid leaves by synthetic accessibility, explain
    pruning decisions, and suggest catalog additions.

    Usage::

        config = build_agent_config(provider="anthropic")
        agent = RetrodesignAgent(config)
        result = await agent.analyze("carboxylic_acid_dimer", max_depth=3)
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id="retrodesign",
            name="Retrodesign Agent",
            description=(
                "LLM-enhanced retrosynthetic decomposition: ranks valid leaves, "
                "explains pruning decisions, and suggests catalog additions."
            ),
            capabilities=[
                "retrosynthetic_decomposition",
                "route_ranking",
                "catalog_gap_identification",
                "pruning_explanation",
            ],
            config=config,
            persona=(
                "Expert retrosynthetic chemist specialising in the Unified Imscriptiveon framework. "
                "You interpret axiom-pruned decomposition trees, rank synthetic routes by "
                "accessibility, and identify which sub-imscription building blocks are missing "
                "from the catalog. Your analyses are mechanistically grounded."
            ),
        )
        self.provider = self._setup_llm_provider_strict()
        self._engine = RetrodesignEngine()

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
        target: str,
        max_depth: int = 3,
        prune_axioms: Optional[List[int]] = None,
        strict_grounding: bool = False,
        prune_ktrap: bool = True,
    ) -> RetrodesignAnalysisResult:
        """
        Run retrodesign analysis on a target imscription or notation string.

        Args:
            target:           Catalog imscription name or raw <...> notation string.
            max_depth:        Maximum decomposition depth.
            prune_axioms:     Axioms to enforce during pruning (default: [1,2,4,6]).
            strict_grounding: Block decomposition if D_∞ target lacks Axiom 6 grounding.
            prune_ktrap:      Prune Ç^Ù leaves without escape pathway (default True).

        Returns:
            RetrodesignAnalysisResult with ranked routes.
        """
        prune_axioms = prune_axioms or [1, 2, 4, 6]

        # 1. Run engine
        tree = self._engine.decompose(
            target,
            max_depth=max_depth,
            prune_axioms=prune_axioms,
            strict_grounding=strict_grounding,
            prune_ktrap=prune_ktrap,
        )

        # 2. LLM ranking and analysis
        ranked_routes, llm_summary, catalog_additions = await self._analyze_with_llm(target, tree)

        return RetrodesignAnalysisResult(
            target=target,
            tree=tree,
            ranked_routes=ranked_routes,
            pruned_count=tree.pruned_count,
            prune_axioms=prune_axioms,
            llm_summary=llm_summary,
            suggested_catalog_additions=catalog_additions,
            metadata={"provider": self.config.get("provider"), "model": self.config.get("model")},
        )

    # ------------------------------------------------------------------
    # LLM analysis
    # ------------------------------------------------------------------

    async def _analyze_with_llm(self, target: str, tree: DecompositionTree):
        prompt = self._build_analysis_prompt(target, tree)
        try:
            raw = await self.call_llm(
                prompt=prompt,
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=0.3,
                system=self._system_prompt(),
            )
            return self._parse_llm_response(raw, tree)
        except Exception:
            return self._fallback_ranking(tree)

    def _build_analysis_prompt(self, target: str, tree: DecompositionTree) -> str:
        from imscrbgrmr.registry import global_catalog
        target_imscription = global_catalog.get(target)
        target_domain = "unknown"
        target_r_mode = "unknown"
        if target_imscription:
            target_domain = str(target_imscription.dimensionality.domains)
            target_r_mode = target_imscription.recognition_mode.name

        valid_leaves = [
            {
                "name": leaf.imscription.name if leaf.imscription else leaf.notation,
                "notation": leaf.notation or (leaf.imscription.to_notation() if leaf.imscription else "?"),
                "in_catalog": leaf.imscription is not None,
                "domain": str(leaf.imscription.dimensionality.domains) if leaf.imscription else "?",
                "r_mode": leaf.imscription.recognition_mode.name if leaf.imscription else "?",
                "warnings": leaf.warnings,
            }
            for leaf in tree.valid_leaves
        ]
        pruned_summary = f"{tree.pruned_count} branches pruned by axioms {tree.prune_axioms}"
        return f"""<task>
Analyse this retrosynthetic decomposition tree for the target imscription.
Rank the valid leaves by CHEMICAL MECHANISM COMPATIBILITY first, then synthetic accessibility.
</task>

<target>
{target}
Notation: {tree.target_notation}
Target domain: {target_domain}
Target recognition mode: {target_r_mode}
</target>

<decomposition>
Valid leaves ({len(valid_leaves)}):
{json.dumps(valid_leaves, indent=2)}

{pruned_summary}
Tree warnings: {tree.warnings}
</decomposition>

<instructions>
The Unified Imscriptiveon framework defines compatibility through **primitive structure**,
not chemical identity. A leaf is a valid retrosynthetic sub-tuple if its primitive
profile is consistent with the target's decomposition — regardless of whether it
shares any domain-specific chemical relationship with the target. A photochromic
dye, a catalytic cycle, and an ecological network can all be valid Imscriptive analogs
if they share the relevant tuple structure.

RANKING RULES (apply in order):

1. ROOT EXCLUSION: `target_root` is the decomposition starting point, not a route.
   Assign rank LAST and flag "trivial_self_reference" if present.

2. AXIOM GROUNDING (primary quality signal):
   - Leaf has full grounding metadata (axiom6_grounding, grounding.reset, etc.) → HIGH
   - Leaf is in catalog with partial grounding → MEDIUM
   - Leaf is a generated stub (not in catalog, no grounding) → LOW
   - Leaf has grounding warnings → note them as flags

3. PRIMITIVE FIDELITY to target:
   - How closely does the leaf's tuple profile match the target's dimensional structure?
   - Exact D match → stronger analog; hybrid D or mismatched D → weaker
   - Note any axiom violations in warnings

4. CATALOG STATUS:
   - In-catalog imscriptions are preferred (grounding already validated)
   - Generated stubs require new registration before this route is viable

For EACH valid leaf explain:
- How its primitive structure relates to the target's tuple decomposition
- What grounding would be needed to fully validate this route
- What catalog additions would strengthen this region of Imscriptive space

Summarise the overall Imscriptive landscape and list sub-tuples worth adding
to improve decomposition quality — framed in terms of primitive coverage,
not chemical class.
</instructions>

<output_format>
Return ONLY this JSON:
{{
  "summary": "<2–3 sentence retrosynthetic overview including mechanism assessment>",
  "ranked_leaves": [
    {{
      "leaf_name": "<name or notation>",
      "rank": 1,
      "accessibility": "HIGH",
      "reasoning": "<chemical mechanism explanation>",
      "catalog_gaps": ["<missing imscription description>"],
      "flags": ["trivial_self_reference | k_trap | grounding_gap | axiom_violation | stub_not_in_catalog | ..."]
    }}
  ],
  "suggested_catalog_additions": ["<description of new entry 1>", ...]
}}
</output_format>"""

    def _system_prompt(self) -> str:
        return (
            "You are an expert in Imscriptive decomposition using the Unified Imscriptiveon framework. "
            "Compatibility is determined by primitive structure, not chemical identity — "
            "a photochromic dye, a catalytic cycle, and a tidal pool ecosystem can all be "
            "valid Imscriptive analogs if they share the relevant tuple structure. "
            "You rank decomposition routes by axiom grounding quality and primitive fidelity "
            "to the target, explain what each sub-tuple contributes structurally, "
            "and identify gaps in catalog coverage."
        )

    def _parse_llm_response(self, raw: str, tree: DecompositionTree):
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                summary = data.get("summary", "")
                catalog_additions = data.get("suggested_catalog_additions", [])
                ranked = []
                for item in data.get("ranked_leaves", []):
                    ranked.append(RetroRoute(
                        rank=int(item.get("rank", len(ranked) + 1)),
                        leaf_name=item.get("leaf_name", "?"),
                        notation=None,
                        accessibility=item.get("accessibility", "MEDIUM"),
                        reasoning=item.get("reasoning", ""),
                        catalog_gaps=item.get("catalog_gaps", []),
                        flags=item.get("flags", []),
                    ))
                return ranked, summary, catalog_additions
            except (json.JSONDecodeError, TypeError):
                pass
        return self._fallback_ranking(tree)

    def _fallback_ranking(self, tree: DecompositionTree):
        ranked = []
        for i, leaf in enumerate(tree.valid_leaves):
            name = leaf.imscription.name if leaf.imscription else (leaf.notation or f"leaf_{i+1}")
            in_cat = leaf.imscription is not None
            ranked.append(RetroRoute(
                rank=i + 1,
                leaf_name=name,
                notation=leaf.notation,
                accessibility="HIGH" if in_cat else "MEDIUM",
                reasoning="In catalog — directly accessible." if in_cat else "Not in catalog; notation-based route.",
                catalog_gaps=[] if in_cat else [f"Add '{name}' to catalog"],
                flags=leaf.warnings,
            ))
        summary = (
            f"Decomposition produced {len(tree.valid_leaves)} valid leaves, "
            f"{tree.pruned_count} branches pruned by axioms {tree.prune_axioms}."
        )
        return ranked, summary, []

    # ------------------------------------------------------------------
    # BaseAgent entry point
    # ------------------------------------------------------------------

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """BaseAgent interface. Task is the target imscription name or notation."""
        try:
            result = await self.analyze(task.strip())
            return {
                "status": "success",
                "findings": (
                    f"Retrodesign of '{result.target}': "
                    f"{len(result.ranked_routes)} valid routes, "
                    f"{result.pruned_count} pruned.\n"
                    f"{result.llm_summary}"
                ),
                "artifacts": self.artifacts,
                "metadata": result.to_dict(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

async def analyze_retrodesign(
    target: str,
    max_depth: int = 3,
    provider: str = "anthropic",
    model: Optional[str] = None,
) -> RetrodesignAnalysisResult:
    """Quick helper: run LLM-enhanced retrodesign analysis."""
    config = build_agent_config(provider=provider, model=model)
    agent = RetrodesignAgent(config)
    return await agent.analyze(target, max_depth=max_depth)
