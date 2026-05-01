"""
Agent Orchestrator (Async)
Coordinates execution of single or multiple agents in parallel using asyncio.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import asyncio
import logging

from .base_agent import BaseAgent, AgentStatus


logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """
    Accumulated state that flows through a pipeline.

    Inspired by the BuildContext pattern from downstream adaptations — every stage
    can read outputs from ALL prior stages, not just the immediately preceding one.
    """
    task: str
    initial_context: Dict[str, Any] = field(default_factory=dict)
    stage_results: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_stage_result(self, agent_id: str, stage_num: int, result: Dict[str, Any]) -> None:
        self.stage_results.append({
            "stage": stage_num,
            "agent_id": agent_id,
            "result": result,
        })
        if isinstance(result.get("artifacts"), list):
            self.artifacts.extend(result["artifacts"])

    def to_context_dict(self) -> Dict[str, Any]:
        """
        Returns the full accumulated context dict passed to each agent's run().
        Includes all prior stage results as well as initial context keys.
        """
        ctx: Dict[str, Any] = dict(self.initial_context)
        ctx["pipeline_stages"] = self.stage_results
        ctx["all_artifacts"] = self.artifacts
        ctx["pipeline_metadata"] = self.metadata
        if self.stage_results:
            last = self.stage_results[-1]
            ctx["previous_stage"] = last["result"]
            ctx["previous_agent"] = last["agent_id"]
        return ctx


class AgentOrchestrator:
    """
    Orchestrates agent execution in single, swarm, or pipeline modes using asyncio.

    Additions over the base version:
    - PipelineContext: downstream agents see outputs from ALL prior stages.
    - Pipeline presets: named sequences of agents registered once, run by name.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.max_concurrent = self.config.get("max_concurrent_agents", 10)
        self._presets: Dict[str, List[str]] = {}

    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id} ({agent.name})")

    # ------------------------------------------------------------------
    # Pipeline preset management
    # ------------------------------------------------------------------

    def register_preset(self, name: str, agent_ids: List[str]) -> None:
        """
        Register a named pipeline preset — an ordered list of agent IDs.

        Example (from AtkSrfr-style presets):
            orchestrator.register_preset("full", ["hunter", "triage", "cwe_mapper"])
            orchestrator.register_preset("redteam", ["hunter", "exploit"])
        """
        self._presets[name] = agent_ids
        logger.info(f"Registered preset '{name}': {' -> '.join(agent_ids)}")

    def list_presets(self) -> Dict[str, List[str]]:
        """Return all registered presets."""
        return dict(self._presets)

    async def run_preset(
        self,
        preset_name: str,
        task: str,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run a named pipeline preset.
        Convenience wrapper around run_pipeline().
        """
        if preset_name not in self._presets:
            raise ValueError(
                f"Unknown preset '{preset_name}'. "
                f"Available: {list(self._presets.keys())}"
            )
        agent_ids = self._presets[preset_name]
        logger.info(f"Running preset '{preset_name}': {' -> '.join(agent_ids)}")
        return await self.run_pipeline(task, agent_ids, initial_context)

    # ------------------------------------------------------------------
    # Core execution methods
    # ------------------------------------------------------------------

    async def run_agent(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a single agent (Async)."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")

        agent = self.agents[agent_id]
        logger.info(f"Running agent: {agent_id}")

        try:
            agent.start()
            result = await agent.run(task, context)
            agent.complete(result)
            logger.info(f"Agent {agent_id} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Agent {agent_id} failed: {str(e)}")
            agent.fail(str(e))
            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id
            }

    async def run_swarm(
        self,
        task: str,
        agent_ids: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute multiple agents in parallel (Async)."""
        if agent_ids is None:
            agent_ids = list(self.agents.keys())

        logger.info(f"Running swarm with {len(agent_ids)} agents")

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def _run_with_semaphore(aid):
            async with semaphore:
                return await self.run_agent(aid, task, context)

        tasks = [_run_with_semaphore(aid) for aid in agent_ids]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        results = {}
        successful = 0
        failed = 0

        for agent_id, result in zip(agent_ids, results_list):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_id} raised an exception: {result}")
                results[agent_id] = {"status": "error", "error": str(result)}
                failed += 1
            else:
                results[agent_id] = result
                if result.get("status") == "success":
                    successful += 1
                else:
                    failed += 1

        logger.info(f"Swarm complete: {successful} successful, {failed} failed")

        return {
            "agents_run": len(agent_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    async def run_pipeline(
        self,
        task: str,
        agent_ids: List[str],
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially (Async).

        Each stage receives the full PipelineContext — outputs from every prior
        stage, not just the immediately preceding one.  The returned dict also
        includes the PipelineContext so callers can inspect the full history.
        """
        logger.info(f"Running pipeline with {len(agent_ids)} stages")

        pipeline_ctx = PipelineContext(
            task=task,
            initial_context=initial_context or {},
        )

        for i, agent_id in enumerate(agent_ids):
            stage_num = i + 1
            logger.info(f"Pipeline stage {stage_num}/{len(agent_ids)}: {agent_id}")

            context_dict = pipeline_ctx.to_context_dict()
            result = await self.run_agent(agent_id, task, context_dict)
            pipeline_ctx.add_stage_result(agent_id, stage_num, result)

            if result.get("status") != "success":
                logger.warning(f"Pipeline failed at stage {stage_num} ({agent_id})")
                return {
                    "status": "failed",
                    "failed_at_stage": stage_num,
                    "failed_agent": agent_id,
                    "pipeline_results": pipeline_ctx.stage_results,
                    "pipeline_context": pipeline_ctx,
                }

        logger.info("Pipeline completed successfully")

        return {
            "status": "success",
            "stages_completed": len(agent_ids),
            "pipeline_results": pipeline_ctx.stage_results,
            "final_context": pipeline_ctx.to_context_dict(),
            "pipeline_context": pipeline_ctx,
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get current status of an agent."""
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}")
        return self.agents[agent_id].status

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get info about all registered agents."""
        return {
            agent_id: {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "status": agent.status.value,
            }
            for agent_id, agent in self.agents.items()
        }
